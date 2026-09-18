"""Serving mode that answers routes from a pinned graph database.

This is the join between the three halves of the migration: the active pointer
decides *which* graph a new search may use, the durable job engine proves the
route against exactly that graph, and hydration fetches display metadata only
for the people and evidence that survived into the answer.

The mode is configuration-gated and off unless a database URL and import are
supplied, so an unconfigured deployment keeps behaving exactly as before.  The
completeness certificate is a separate, explicit setting: pointing at an import
never by itself licenses an ``exact`` or ``no_path`` claim.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
import threading
from typing import Any

from .graph import Filters
from .kinship import best_meeting_point, describe, describe_link
from .hlbes import SEARCH_INCOMPLETE
from .graph_hydration import (PEOPLE, WORKS, Hydrator, HydrationBudget,
                              HydrationCache, placeholder)
from .db_search_jobs import DatabaseSearchJobs
from .graph import GraphError
from .neon_graph_provider import (ADVISER_DEGREES, CoverageClaim, GenealogyOverlay, GraphDatabaseError, _at,
                                  NeonCompactGraphProvider, connect_read_only,
                                  observe_coverage)


def evidence_url(source_kind: Any, source_record: str) -> str:
    """Where a reader can check this relation for themselves.

    A thesis names its supervisors on a literature record, an adviser field
    lives on the student's author profile, and a Wikidata relation lives on the
    item that states it. Each links to what actually carries the claim - and a
    relation taken from a published page carries that page's own address.
    """
    if str(source_record).startswith(("http://", "https://")):
        return str(source_record)
    if source_kind == "wikidata":
        return f"https://www.wikidata.org/wiki/{source_record}"
    collection = "literature" if source_kind == "thesis" else "authors"
    return f"https://inspirehep.net/{collection}/{source_record}"


@dataclass(frozen=True)
class DatabaseModeConfig:
    url: str
    import_id: str
    overlay_id: str | None = None
    #: Only an operator who has run the independent validator may set this.
    #: It is read from its own variable so that pointing at a candidate can
    #: never be mistaken for certifying it.
    certified_complete: bool = False
    overlay_certified: bool = False
    statement_timeout_ms: int = 15_000
    #: Job state is the one thing serving writes. It is a separate URL so the
    #: graph itself can be served by a credential with no write rights at all;
    #: it defaults to the graph URL for a single-credential deployment.
    job_store_url: str | None = None

    @classmethod
    def from_env(cls, environ: dict[str, str] | None = None) -> "DatabaseModeConfig | None":
        env = environ if environ is not None else os.environ
        url = env.get("HEPGRAPH_GRAPH_DATABASE_URL", "").strip()
        import_id = env.get("HEPGRAPH_GRAPH_IMPORT_ID", "").strip()
        if not url or not import_id:
            return None
        overlay = env.get("HEPGRAPH_GRAPH_OVERLAY_ID", "").strip() or None
        return cls(url=url, import_id=import_id, overlay_id=overlay,
                   job_store_url=env.get("HEPGRAPH_GRAPH_JOB_STORE_URL", "").strip() or None,
                   certified_complete=_flag(env.get("HEPGRAPH_GRAPH_CERTIFIED_COMPLETE")),
                   overlay_certified=_flag(env.get("HEPGRAPH_GRAPH_OVERLAY_CERTIFIED")),
                   statement_timeout_ms=int(env.get("HEPGRAPH_GRAPH_STATEMENT_TIMEOUT_MS", "15000")))


def _flag(value: str | None) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


class DatabaseGraphService:
    """One process-local handle: connection, pointer, jobs and hydration.

    The connection is revalidated per request rather than trusted from cold
    start, because a frozen serverless instance can be resumed long after the
    database has closed its side.
    """

    def __init__(self, config: DatabaseModeConfig, *, client: Any = None,
                 connection: Any = None, job_connection: Any = None,
                 hydrator: Hydrator | None = None) -> None:
        self.config = config
        self.lock = threading.RLock()
        self._connection = connection
        self._client = client
        self._hydrator = hydrator
        self._cache = HydrationCache()
        self._coverage: CoverageClaim | None = None
        # An injected connection serves both roles: a caller supplying one
        # already owns its read/write policy, so no second dial is made.
        self._job_connection = job_connection if job_connection is not None else connection

    # ------------------------------------------------------------- connection
    def connection(self) -> Any:
        with self.lock:
            if self._connection is not None and not self._closed(self._connection):
                return self._connection
            self._connection = connect_read_only(
                self.config.url, statement_timeout_ms=self.config.statement_timeout_ms)
            return self._connection

    @staticmethod
    def _closed(connection: Any) -> bool:
        try:
            if getattr(connection, "closed", False):
                return True
            connection.execute("SELECT 1")
            return False
        except Exception:
            return True

    def coverage(self, *, refresh: bool = False) -> CoverageClaim:
        """Observed coverage plus the operator's separate certificate."""
        with self.lock:
            if self._coverage is None or refresh:
                observed = observe_coverage(self.connection(), self.config.import_id)
                certified = self.config.certified_complete
                self._coverage = CoverageClaim(
                    import_id=observed.import_id, source_cutoff=observed.source_cutoff,
                    declared_low=observed.declared_low, declared_high=observed.declared_high,
                    observed_low=observed.observed_low, observed_high=observed.observed_high,
                    shards_outstanding=observed.shards_outstanding, works=observed.works,
                    certified_complete=certified,
                    reason="" if certified else "import_not_certified")
            return self._coverage

    def overlay(self) -> GenealogyOverlay | None:
        if self.config.overlay_id is None:
            return None
        return GenealogyOverlay(self.config.overlay_id, self.config.overlay_certified)

    # --------------------------------------------------------------- provider
    def provider(self, import_id: str | None = None) -> NeonCompactGraphProvider:
        """Resolve the pointer once. Callers hold the result for one search."""
        coverage = self.coverage()
        if import_id is not None and import_id != coverage.import_id:
            # A resumed job asks for its own pinned import; serve that exact one
            # and let the job engine decide whether the pin still matches.
            coverage = CoverageClaim(import_id=import_id, source_cutoff=coverage.source_cutoff,
                                     certified_complete=self.config.certified_complete,
                                     reason="" if self.config.certified_complete
                                     else "import_not_certified")
        return NeonCompactGraphProvider(self.connection(), coverage=coverage,
                                        genealogy_overlay=self.overlay())

    def job_connection(self) -> Any:
        """The writable connection, used only for search-job rows."""
        import psycopg

        with self.lock:
            if self._job_connection is not None and not self._closed(self._job_connection):
                return self._job_connection
            self._job_connection = psycopg.connect(
                self.config.job_store_url or self.config.url,
                autocommit=True, row_factory=psycopg.rows.dict_row)
            self._job_connection.execute(
                "SELECT set_config('statement_timeout', %s, false)",
                (str(int(self.config.statement_timeout_ms)),))
            return self._job_connection

    def jobs(self) -> DatabaseSearchJobs:
        engine = DatabaseSearchJobs(
            self.job_connection(),
            provider_factory=lambda: self.provider(),
            provider_for=lambda pin: self.provider(pin.import_id))
        engine.ensure_schema()
        return engine

    def hydrator(self) -> Hydrator | None:
        """A fresh hydrator per delivery, sharing the process-wide cache.

        A hydrator fixes its deadline when it is built, so reusing one across
        requests would silently exhaust every later result's budget while the
        cache it holds is exactly the part worth keeping.
        """
        if self._hydrator is not None:
            return self._hydrator
        if self._client is None:
            return None
        return Hydrator(self._client, cache=self._cache, budget=HydrationBudget())

    # ------------------------------------------------------------------- API
    def dataset(self) -> dict[str, Any]:
        coverage = self.coverage(refresh=True)
        certified = coverage.certified_complete
        return {
            "version": f"graph-db:{coverage.import_id}", "source_mode": "database",
            "created_at": coverage.source_cutoff,
            "graph_snapshot": coverage.import_id,
            "source_cutoff": coverage.source_cutoff,
            "counts": {"people": None, "works": coverage.works, "phd": None},
            "coverage": {
                "label": ("Pinned graph version" if certified
                          else "Pinned graph version — coverage not certified"),
                "description": (
                    "Routes are traced through one fixed version of the collaboration "
                    "graph with a recorded source cutoff, not a live reading of INSPIRE. "
                    "Paper titles and researcher details are retrieved afterwards, only "
                    "for the results shown."
                    + ("" if certified else
                       " This version has not been certified as covering the whole source, "
                       "so a route that is found is evidenced, while the absence of a route "
                       "is not evidence that none exists.")),
                "complete": certified, "mode": "database",
                "graph_snapshot": coverage.import_id,
                "observed_record_range": [coverage.observed_low, coverage.observed_high],
                "declared_record_range": [coverage.declared_low, coverage.declared_high],
                "shards_outstanding": coverage.shards_outstanding,
                "queries": [], "failures": [],
            },
            "capabilities": {
                "live_graph": False, "deep_search": True,
                # Centrality needs the whole graph in memory, which a function
                # instance must never hold; it stays a saved-snapshot feature.
                "global_centrality": False,
                "genealogy": self.config.overlay_id is not None,
            },
            "policy": {
                "papers": "Articles and individual conference papers; correction notices and "
                          "theses, books and proceedings were excluded when the graph was built.",
                "identity": "Stable INSPIRE author record IDs; names never establish identity.",
                "genealogy": ("Adviser records come from a separately versioned overlay."
                              if self.config.overlay_id else
                              "Adviser records are not part of this graph version."),
                "storage": "The graph stores identifiers, author counts and years only. "
                           "Titles, names and affiliations are fetched per result and kept in memory.",
                "distance": "One person-to-person tie is one hop. A route is shortest only "
                            "within this graph version, and only when its coverage is certified.",
            },
        }

    def start_path(self, source: str, target: str, filters: Filters) -> dict[str, Any]:
        return self.hydrate(self.jobs().start(str(source), str(target), filters))

    def job(self, job_id: str) -> dict[str, Any]:
        return self.hydrate(self.jobs().get(job_id))

    def resume(self, job_id: str) -> dict[str, Any]:
        return self.hydrate(self.jobs().resume(job_id))

    def cancel(self, job_id: str) -> dict[str, Any]:
        return self.hydrate(self.jobs().cancel(job_id))

    def person(self, person_id: str, filters: Filters, *, limit: int = 40,
               summary: bool = False) -> dict[str, Any]:
        """A profile opened deliberately: counts from the graph, details fetched.

        Opening a profile is a user action, so hydrating it here is exactly the
        post-route rule, not a traversal cost. ``summary`` is for callers that
        only need to know who an id is - restoring a shared route, labelling a
        node - and skips the neighbourhood, which is most of the cost.
        """
        provider = self.provider()
        coverage = self.coverage()
        if provider.resolve_author(str(person_id)) is None:
            return {"status": "not_found", "mode": "database",
                    "message": "This person is not included in this release, which is not "
                               "evidence that they are absent from INSPIRE.",
                    "person": {"id": str(person_id)}, "filters": filters.to_dict(),
                    "version": f"graph-db:{coverage.import_id}",
                    "coverage": self.dataset()["coverage"]}
        if summary:
            hydrator = self.hydrator()
            people = (hydrator.hydrate_people((str(person_id),)) if hydrator is not None
                      else {str(person_id): placeholder(PEOPLE, str(person_id),
                                                        "hydration_unavailable")})
            return {"status": "ok", "mode": "database", "summary": True,
                    "person": people.get(str(person_id),
                                         placeholder(PEOPLE, str(person_id), "not_found")),
                    "indexed": True, "queryable": True, "filters": filters.to_dict(),
                    "version": f"graph-db:{coverage.import_id}"}
        found = provider.get_neighbors(str(person_id), filters)
        neighbors = sorted(found.members, key=lambda value: (len(value), value))[:limit]
        relations = self._direct_relations(str(person_id))
        hydrator = self.hydrator()
        wanted = (str(person_id), *neighbors)
        people = (hydrator.hydrate_people(wanted) if hydrator is not None
                  else {identifier: placeholder(PEOPLE, identifier, "hydration_unavailable")
                        for identifier in wanted})
        return {
            "status": "ok", "mode": "database",
            "person": people.get(str(person_id), placeholder(PEOPLE, str(person_id), "not_found")),
            "indexed": True, "queryable": True,
            "coauthor_count": len(found.members),
            "combined_degree": len(found.members),
            "collaborators": [{"person": people.get(identifier,
                                                    placeholder(PEOPLE, identifier, "not_found")),
                               "shared_works": len([
                                   ref for ref in provider.get_edge_evidence_refs(
                                       str(person_id), identifier, filters)
                                   if ref.startswith("work:")])}
                              for identifier in neighbors],
            "advisers": relations["advisers"], "students": relations["students"],
            "indexed_publications": None, "eligible_publications": None,
            "truncated": len(found.members) > len(neighbors),
            "neighborhood_status": found.status, "neighborhood_reason": found.reason,
            "reachability": {"status": "unavailable" if not coverage.certified_complete else "ok",
                             "message": "Component sizes need certified coverage."
                             if not coverage.certified_complete else ""},
            "filters": filters.to_dict(), "version": f"graph-db:{coverage.import_id}",
            "coverage": self.dataset()["coverage"],
        }

    def neighborhood(self, person_id: str, filters: Filters, *, limit: int = 40) -> dict[str, Any]:
        profile = self.person(person_id, filters, limit=limit)
        if profile["status"] != "ok":
            return profile
        people = [profile["person"]] + [item["person"] for item in profile["collaborators"]]
        return {"status": "ok", "mode": "database", "people": people,
                "edges": [{"source": str(person_id), "target": item["person"]["id"],
                           "types": ["coauthor"], "shared_works": item["shared_works"]}
                          for item in profile["collaborators"]],
                "truncated": profile["truncated"], "filters": filters.to_dict(),
                "version": profile["version"], "coverage": profile["coverage"]}

    def _direct_relations(self, person_id: str) -> dict[str, list[dict[str, Any]]]:
        """One generation either side, for the profile panel."""
        empty: dict[str, list[dict[str, Any]]] = {"advisers": [], "students": []}
        if self.config.overlay_id is None:
            return empty
        rows = self.connection().execute(
            "SELECT adviser_id, student_id, source_record, degree, curated, source_kind "
            "FROM graph_genealogy_edge WHERE overlay_id=%s AND COALESCE(degree,'other') = ANY(%s) "
            "AND (adviser_id=%s OR student_id=%s) ORDER BY adviser_id, student_id LIMIT 200",
            (self.config.overlay_id, list(ADVISER_DEGREES),
             int(person_id), int(person_id))).fetchall()
        for row in rows:
            adviser, student = str(_at(row, 0)), str(_at(row, 1))
            source_record, source_kind = str(_at(row, 2)), _at(row, 5)
            record = {"adviser": adviser, "student": student,
                      "source_record": source_record, "degree": _at(row, 3),
                      "curated": bool(_at(row, 4)), "source_kind": source_kind,
                      "source_url": evidence_url(source_kind, source_record)}
            empty["advisers" if student == str(person_id) else "students"].append(record)
        return empty

    MAX_LINEAGE_DEPTH = 6
    MAX_LINEAGE_EDGES = 400

    def ancestry(self, person_id: str, filters: Filters, *,
                 direction: str = "ancestors", depth: int = 4) -> dict[str, Any]:
        """Walk doctoral lineage up or down, several generations at a time.

        Supervision is a directed acyclic graph, not a tree: a person may have
        more than one adviser, and two lines can rejoin. The walk therefore
        carries the visited path and refuses to re-enter it, so a cycle in the
        source data cannot spin here, and it reports the generation each
        relation was found at so the caller can group by distance.
        """
        coverage = self.coverage()
        base = {"mode": "database", "person": {"id": str(person_id)},
                "direction": direction, "people": [], "edges": [],
                "filters": filters.to_dict(),
                "version": f"graph-db:{coverage.import_id}",
                "coverage": self.dataset()["coverage"]}
        if self.config.overlay_id is None:
            return base | {"status": "unavailable",
                           "message": "Adviser records are not part of this release."}
        if direction not in {"ancestors", "descendants"}:
            raise GraphError("invalid_input", "Direction must be ancestors or descendants.")
        depth = max(1, min(int(depth), self.MAX_LINEAGE_DEPTH))
        provider = self.provider()
        if provider.resolve_author(str(person_id)) is None:
            return base | {"status": "not_found",
                           "message": "This person has no doctoral record in the pinned graph, "
                                      "which is not evidence that none exists."}
        # Climbing means following adviser_id from a student; descending is the
        # same edge read the other way, so only the two column roles swap.
        step_from, step_to = (("student_id", "adviser_id") if direction == "ancestors"
                              else ("adviser_id", "student_id"))
        rows = self.connection().execute(
            f"""WITH RECURSIVE walk(origin, reached, generation, path) AS (
                    SELECT e.{step_from}, e.{step_to}, 1,
                           ARRAY[e.{step_from}, e.{step_to}]
                      FROM graph_genealogy_edge e
                     WHERE e.overlay_id = %s AND COALESCE(e.degree,'other') = ANY(%s)
                       AND e.{step_from} = %s
                    UNION ALL
                    SELECT w.reached, e.{step_to}, w.generation + 1,
                           w.path || e.{step_to}
                      FROM walk w
                      JOIN graph_genealogy_edge e
                        ON e.overlay_id = %s AND COALESCE(e.degree,'other') = ANY(%s)
                       AND e.{step_from} = w.reached
                     WHERE w.generation < %s AND NOT e.{step_to} = ANY(w.path))
                SELECT DISTINCT w.origin, w.reached, w.generation,
                       e.source_record, e.degree, e.curated, e.source_kind
                  FROM walk w
                  JOIN graph_genealogy_edge e
                    ON e.overlay_id = %s AND COALESCE(e.degree,'other') = ANY(%s)
                   AND e.{step_from} = w.origin AND e.{step_to} = w.reached
                 ORDER BY w.generation, w.origin, w.reached
                 LIMIT %s""",
            (self.config.overlay_id, list(ADVISER_DEGREES), int(person_id),
             self.config.overlay_id, list(ADVISER_DEGREES), depth,
             self.config.overlay_id, list(ADVISER_DEGREES),
             self.MAX_LINEAGE_EDGES + 1)).fetchall()
        truncated = len(rows) > self.MAX_LINEAGE_EDGES
        rows = rows[:self.MAX_LINEAGE_EDGES]
        edges, generation_of = [], {}
        for row in rows:
            origin, reached, generation = str(_at(row, 0)), str(_at(row, 1)), int(_at(row, 2))
            adviser, student = ((reached, origin) if direction == "ancestors"
                                else (origin, reached))
            edges.append({"adviser": adviser, "student": student,
                          "source_record": str(_at(row, 3)), "degree": _at(row, 4),
                          "curated": bool(_at(row, 5)), "source_kind": _at(row, 6),
                          "generation": generation})
            generation_of[reached] = min(generation_of.get(reached, generation), generation)
        people = self._lineage_people(str(person_id), generation_of)
        return base | {"status": "ok", "depth": depth, "truncated": truncated,
                       "person": people.get(str(person_id), {"id": str(person_id)}),
                       "people": [people[identifier] | {"generation": generation}
                                  for identifier, generation in sorted(
                                      generation_of.items(), key=lambda item: (item[1], item[0]))
                                  if identifier in people],
                       "edges": edges}

    #: A relationship is only interesting while it is a relationship. Beyond
    #: this the two lines are so far apart that the answer is really "both are
    #: physicists", and the walk would cost more than it says.
    MAX_KINSHIP_DEPTH = 12

    def _ancestors(self, person_id: int, depth: int) -> dict[int, list[int]]:
        """Every ancestor of one person, with the shortest line reaching them.

        The person themselves is included at distance zero, which is what makes
        a direct line of descent fall out of the same comparison as a cousinhood.
        """
        rows = self.connection().execute(
            """WITH RECURSIVE climb(person, depth, line) AS (
                   SELECT %s::bigint, 0, ARRAY[%s::bigint]
                   UNION ALL
                   SELECT e.adviser_id, c.depth + 1, c.line || e.adviser_id
                     FROM climb c
                     JOIN graph_genealogy_edge e
                       ON e.overlay_id = %s AND COALESCE(e.degree,'other') = ANY(%s)
                      AND e.student_id = c.person
                    WHERE c.depth < %s AND NOT e.adviser_id = ANY(c.line))
               SELECT DISTINCT ON (person) person, line
                 FROM climb ORDER BY person, depth, line""",
            (int(person_id), int(person_id), self.config.overlay_id,
             list(ADVISER_DEGREES), int(depth))).fetchall()
        return {int(_at(row, 0)): [int(item) for item in _at(row, 1)] for row in rows}

    #: How far each side may wander when the two share no ancestor. Four and
    #: four meets in the middle of any eight-link route, which is already
    #: further than a relationship worth naming.
    MAX_LINK_DEPTH = 4

    def _within_reach(self, person_id: int, depth: int) -> dict[int, list[int]]:
        """Everyone reachable by following supervision in *either* direction.

        Descent answers "are they related"; this answers "are they connected at
        all", which for this data is the much more common case.
        """
        rows = self.connection().execute(
            """WITH RECURSIVE reach(person, depth, line) AS (
                   SELECT %s::bigint, 0, ARRAY[%s::bigint]
                   UNION ALL
                   SELECT step.other, r.depth + 1, r.line || step.other
                     FROM reach r
                     JOIN (SELECT student_id AS person, adviser_id AS other
                             FROM graph_genealogy_edge
                            WHERE overlay_id = %s AND COALESCE(degree,'other') = ANY(%s)
                           UNION ALL
                           SELECT adviser_id, student_id
                             FROM graph_genealogy_edge
                            WHERE overlay_id = %s AND COALESCE(degree,'other') = ANY(%s)) step
                       ON step.person = r.person
                    WHERE r.depth < %s AND NOT step.other = ANY(r.line))
               SELECT DISTINCT ON (person) person, line
                 FROM reach ORDER BY person, depth, line""",
            (int(person_id), int(person_id), self.config.overlay_id, list(ADVISER_DEGREES),
             self.config.overlay_id, list(ADVISER_DEGREES), int(depth))).fetchall()
        return {int(_at(row, 0)): [int(item) for item in _at(row, 1)] for row in rows}

    def _steps_along(self, line: list[int]) -> list[dict[str, Any]]:
        """The relation behind each step of a path, in whichever direction it runs."""
        steps: list[dict[str, Any]] = []
        for here, there in zip(line, line[1:]):
            for student, adviser, direction in ((here, there, "up"), (there, here, "down")):
                row = self.connection().execute(
                    "SELECT source_record, degree, curated, source_kind "
                    "FROM graph_genealogy_edge WHERE overlay_id=%s AND student_id=%s "
                    "AND adviser_id=%s AND COALESCE(degree,'other') = ANY(%s) "
                    "ORDER BY CASE WHEN degree='phd' THEN 0 ELSE 1 END LIMIT 1",
                    (self.config.overlay_id, student, adviser, list(ADVISER_DEGREES))).fetchone()
                if row is not None:
                    source_record = str(_at(row, 0))
                    steps.append({"adviser": str(adviser), "student": str(student),
                                  "direction": direction, "source_record": source_record,
                                  "degree": _at(row, 1), "curated": bool(_at(row, 2)),
                                  "source_kind": _at(row, 3),
                                  "source_url": evidence_url(_at(row, 3), source_record)})
                    break
        return steps

    def _relations_along(self, line: list[int]) -> list[dict[str, Any]]:
        """The stored relation behind each step of a line, for its evidence."""
        steps: list[dict[str, Any]] = []
        for student, adviser in zip(line, line[1:]):
            row = self.connection().execute(
                "SELECT source_record, degree, curated, source_kind "
                "FROM graph_genealogy_edge WHERE overlay_id=%s AND student_id=%s "
                "AND adviser_id=%s AND COALESCE(degree,'other') = ANY(%s) "
                "ORDER BY CASE WHEN degree='phd' THEN 0 ELSE 1 END LIMIT 1",
                (self.config.overlay_id, student, adviser, list(ADVISER_DEGREES))).fetchone()
            if row is None:
                continue
            source_record = str(_at(row, 0))
            steps.append({"adviser": str(adviser), "student": str(student),
                          "source_record": source_record, "degree": _at(row, 1),
                          "curated": bool(_at(row, 2)), "source_kind": _at(row, 3),
                          "source_url": evidence_url(_at(row, 3), source_record)})
        return steps

    def relationship(self, first_id: str, second_id: str, filters: Filters, *,
                     depth: int = MAX_KINSHIP_DEPTH) -> dict[str, Any]:
        """How two people are related in the adviser forest, in kinship terms.

        Silence here is a claim about the records, never about the people: two
        researchers with no line between them are reported as having none
        *recorded*, which is what the overlay can actually support.
        """
        coverage = self.coverage()
        base = {"mode": "database", "filters": filters.to_dict(),
                "version": f"graph-db:{coverage.import_id}",
                "coverage": self.dataset()["coverage"],
                "people": {}, "chain": []}
        if self.config.overlay_id is None:
            return base | {"status": "unavailable",
                           "message": "Adviser records are not part of this release."}
        depth = max(1, min(int(depth), self.MAX_KINSHIP_DEPTH))
        provider = self.provider()
        for identifier in (first_id, second_id):
            if provider.resolve_author(str(identifier)) is None:
                return base | {"status": "not_found", "person": {"id": str(identifier)},
                               "message": "This person has no adviser record in the pinned "
                                          "graph, which is not evidence that none exists."}
        if str(first_id) == str(second_id):
            named = self._lineage_people(str(first_id), {})
            return base | {"status": "ok", "people": named,
                           "meeting_point": str(first_id), "distances": [0, 0],
                           "chain": [], **describe(0, 0)}

        first, second = int(first_id), int(second_id)
        up, down = self._ancestors(first, depth), self._ancestors(second, depth)
        meeting = best_meeting_point({person: len(line) - 1 for person, line in up.items()},
                                     {person: len(line) - 1 for person, line in down.items()})
        if meeting is None:
            return self._connection_without_descent(first, second, base, depth)
        ancestor, up_steps, down_steps = meeting
        # The two climbs meet head to head, so the second is walked back down.
        # Every step says which way it runs, so a reader - or a drawing - can
        # follow the chain from the first person to the second without
        # inferring direction from who advised whom.
        chain = [step | {"direction": "up"} for step in self._relations_along(up[ancestor])]
        chain += [step | {"direction": "down"}
                  for step in reversed(self._relations_along(down[ancestor]))]
        on_show = {str(person): 0 for line in (up[ancestor], down[ancestor])
                   for person in line}
        named = self._lineage_people(str(first), on_show)
        return base | {"status": "ok", "people": named, "chain": chain,
                       "meeting_point": str(ancestor), "distances": [up_steps, down_steps],
                       "line_up": [str(person) for person in up[ancestor]],
                       "line_down": [str(person) for person in down[ancestor]],
                       **describe(up_steps, down_steps)}

    def _connection_without_descent(self, first: int, second: int, base: dict[str, Any],
                                    depth: int) -> dict[str, Any]:
        """No shared ancestor: look for any route through supervision at all."""
        reach = min(self.MAX_LINK_DEPTH, depth)
        outward, inward = self._within_reach(first, reach), self._within_reach(second, reach)
        shared = set(outward) & set(inward)
        if not shared:
            named = self._lineage_people(str(first), {str(second): 0})
            return base | {"status": "no_relation", "people": named,
                           "label": "no recorded relation",
                           "explanation": "No chain of supervision recorded in this release "
                                          "connects them, within " f"{reach * 2} links. That "
                                          "describes the records, not the researchers: INSPIRE "
                                          "names an adviser for only a small share of physicists.",
                           "searched_generations": reach * 2}
        middle = min(shared, key=lambda person: (len(outward[person]) + len(inward[person]),
                                                 person))
        line = outward[middle] + list(reversed(inward[middle]))[1:]
        steps = self._steps_along(line)
        on_show = {str(person): index for index, person in enumerate(line)}
        named = self._lineage_people(str(first), on_show)
        return base | {"status": "connected", "people": named, "chain": steps,
                       "line": [str(person) for person in line],
                       **describe_link([step["direction"] for step in steps])}

    def _lineage_people(self, root: str, generation_of: dict[str, int]) -> dict[str, Any]:
        """Names for the people on show. A failure keeps the ID, never invents one."""
        wanted = (root, *sorted(generation_of, key=lambda item: (generation_of[item], item)))
        hydrator = self.hydrator()
        if hydrator is None:
            return {identifier: placeholder(PEOPLE, identifier, "hydration_unavailable")
                    for identifier in wanted}
        return hydrator.hydrate_people(wanted)

    def lineage_map(self) -> dict[str, Any]:
        """The whole doctoral forest, laid out once and read back whole.

        This is the one payload the application sends in bulk. It is a derived
        drawing of relations already public on INSPIRE, and it is precomputed
        rather than assembled per request.
        """
        if self.config.overlay_id is None:
            return {"status": "unavailable",
                    "message": "Adviser records are not part of this release."}
        from .lineage_map import read_map

        coverage = self.coverage()
        return read_map(self.connection(), self.config.overlay_id,
                        f"graph-db:{coverage.import_id}")

    def owns_job(self, job_id: str) -> bool:
        row = self.job_connection().execute(
            "SELECT 1 FROM graph_search_job WHERE job_id=%s", (job_id,)).fetchone()
        return row is not None

    # -------------------------------------------------------------- hydration
    def hydrate(self, record: dict[str, Any]) -> dict[str, Any]:
        """Fill in display metadata for what the answer actually shows.

        This runs once per delivered record, never inside traversal.  A failure
        here leaves the proven structure and its evidence identifiers in place:
        an edge is never dropped because its paper could not be fetched.
        """
        paths = record.get("paths") or []
        if not paths:
            return record
        people_ids = tuple(dict.fromkeys(
            str(person["id"]) for path in paths for person in path.get("people", ())))
        work_ids = tuple(dict.fromkeys(
            ref.split(":", 1)[1] for path in paths for edge in path.get("edges", ())
            for ref in edge.get("evidence_refs", ()) if ref.startswith("work:")))
        hydrator = self.hydrator()
        if hydrator is None:
            people = {identifier: placeholder(PEOPLE, identifier, "hydration_unavailable")
                      for identifier in people_ids}
            works = {identifier: placeholder(WORKS, identifier, "hydration_unavailable")
                     for identifier in work_ids}
            result = None
        else:
            result = hydrator.hydrate_route(people_ids=people_ids, work_ids=work_ids)
            people, works = result.people, result.works
        members = getattr(hydrator, "work_members", {}) if hydrator is not None else {}
        verified_edges = contradicted = unverified = 0
        for path in paths:
            path["people"] = [people.get(str(person["id"]),
                                         placeholder(PEOPLE, str(person["id"]), "not_requested"))
                              for person in path.get("people", ())]
            for edge in path.get("edges", ()):
                refs = edge.get("evidence_refs", ())
                work_ids = [ref.split(":", 1)[1] for ref in refs if ref.startswith("work:")]
                edge["works"] = [works[work_id] for work_id in work_ids if work_id in works]
                edge["phd"] = [{"source_record": ref.split(":", 1)[1]} for ref in refs
                               if ref.startswith("phd:")]
                edge["types"] = (["coauthor"] if edge["works"] else []) + (
                    ["phd"] if edge["phd"] else [])
                edge["shared_works"] = len(edge["works"])
                # The graph said these two share this paper; INSPIRE is asked to
                # confirm it from the byline of the very record being displayed.
                # A contradiction means the pinned graph has drifted from the
                # source, which the reader must be told rather than shown a
                # clean-looking edge.
                # Only a record that actually carries linked authors can
                # confirm or contradict anything. An unlinked byline is missing
                # evidence, not evidence of absence.
                checked = [work_id for work_id in work_ids if members.get(work_id)]
                confirmed = [work_id for work_id in checked
                             if {str(edge["source"]), str(edge["target"])} <= members[work_id]]
                edge["verified_works"] = confirmed
                if confirmed:
                    edge["verification"] = "confirmed"
                    verified_edges += 1
                elif checked:
                    edge["verification"] = "contradicted"
                    contradicted += 1
                else:
                    edge["verification"] = "unverified"
                    unverified += 1
            path["verified"] = all(edge.get("verification") == "confirmed"
                                   for edge in path.get("edges", ())) if path.get("edges") else True
        record["verification"] = {
            "edges_confirmed": verified_edges, "edges_contradicted": contradicted,
            "edges_unverified": unverified,
            "route_confirmed": contradicted == 0 and unverified == 0,
        }
        if contradicted:
            # Never present a contradicted route as proven: the evidence the
            # proof rests on is not what the source says.
            record["proof_status"] = SEARCH_INCOMPLETE
            record["route_status"] = "search_incomplete"
            record["global_shortest_proven"] = False
            record["exact"] = False
            record["reason"] = "evidence_contradicted_by_source"
            record["message"] = ("INSPIRE does not list both researchers on a paper this route "
                                 "relies on, so the pinned graph has drifted from the source.")
        record["retrieval"] = {
            "people": len(people_ids), "works": len(work_ids),
            "requests": getattr(result, "requests_made", 0),
            "cache_hits": getattr(result, "cache_hits", 0),
            "failures": getattr(result, "failures", len(people_ids) + len(work_ids)
                                if result is None else 0),
            "complete": getattr(result, "complete", False),
            "reason": getattr(result, "reason", "hydration_unavailable" if result is None else ""),
        }
        return record


def service_from_env(client: Any = None,
                     environ: dict[str, str] | None = None) -> DatabaseGraphService | None:
    config = DatabaseModeConfig.from_env(environ)
    return None if config is None else DatabaseGraphService(config, client=client)


__all__ = ["DatabaseGraphService", "DatabaseModeConfig", "GraphDatabaseError",
           "service_from_env"]
