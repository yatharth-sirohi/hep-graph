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
from .graph_hydration import (PEOPLE, WORKS, Hydrator, HydrationBudget,
                              HydrationCache, placeholder)
from .db_search_jobs import DatabaseSearchJobs
from .neon_graph_provider import (CoverageClaim, GenealogyOverlay, GraphDatabaseError,
                                  NeonCompactGraphProvider, connect_read_only,
                                  observe_coverage)


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

    @classmethod
    def from_env(cls, environ: dict[str, str] | None = None) -> "DatabaseModeConfig | None":
        env = environ if environ is not None else os.environ
        url = env.get("HEPGRAPH_GRAPH_DATABASE_URL", "").strip()
        import_id = env.get("HEPGRAPH_GRAPH_IMPORT_ID", "").strip()
        if not url or not import_id:
            return None
        overlay = env.get("HEPGRAPH_GRAPH_OVERLAY_ID", "").strip() or None
        return cls(url=url, import_id=import_id, overlay_id=overlay,
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
                 connection: Any = None, hydrator: Hydrator | None = None) -> None:
        self.config = config
        self.lock = threading.RLock()
        self._connection = connection
        self._client = client
        self._hydrator = hydrator
        self._cache = HydrationCache()
        self._coverage: CoverageClaim | None = None

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

    def jobs(self) -> DatabaseSearchJobs:
        engine = DatabaseSearchJobs(
            self.connection(),
            provider_factory=lambda: self.provider(),
            provider_for=lambda pin: self.provider(pin.import_id))
        engine.ensure_schema()
        return engine

    def hydrator(self) -> Hydrator | None:
        with self.lock:
            if self._hydrator is None and self._client is not None:
                self._hydrator = Hydrator(self._client, cache=self._cache,
                                          budget=HydrationBudget())
            return self._hydrator

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
                "genealogy": ("Doctoral records come from a separately versioned overlay."
                              if self.config.overlay_id else
                              "Doctoral records are not part of this graph version."),
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

    def person(self, person_id: str, filters: Filters, *, limit: int = 40) -> dict[str, Any]:
        """A profile opened deliberately: counts from the graph, details fetched.

        Opening a profile is a user action, so hydrating it here is exactly the
        post-route rule, not a traversal cost.
        """
        provider = self.provider()
        coverage = self.coverage()
        if provider.resolve_author(str(person_id)) is None:
            return {"status": "not_found", "mode": "database",
                    "message": "This person is not in the pinned graph version, which is not "
                               "evidence that they are absent from INSPIRE.",
                    "person": {"id": str(person_id)}, "filters": filters.to_dict(),
                    "version": f"graph-db:{coverage.import_id}",
                    "coverage": self.dataset()["coverage"]}
        found = provider.get_neighbors(str(person_id), filters)
        neighbors = sorted(found.members, key=lambda value: (len(value), value))[:limit]
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
            "advisers": [], "students": [],
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

    def ancestry(self, person_id: str, filters: Filters) -> dict[str, Any]:
        coverage = self.coverage()
        if self.config.overlay_id is None:
            return {"status": "unavailable", "mode": "database",
                    "message": "Doctoral records are not part of this graph version.",
                    "person": {"id": str(person_id)}, "people": [], "edges": [],
                    "filters": filters.to_dict(),
                    "version": f"graph-db:{coverage.import_id}",
                    "coverage": self.dataset()["coverage"]}
        rows = self.connection().execute(
            "SELECT adviser_id, student_id, source_record FROM graph_genealogy_edge "
            "WHERE overlay_id=%s AND (adviser_id=%s OR student_id=%s) "
            "ORDER BY adviser_id, student_id LIMIT 100",
            (self.config.overlay_id, int(person_id), int(person_id))).fetchall()
        edges = [{"adviser": str(row[0]), "student": str(row[1]), "source_record": str(row[2])}
                 for row in rows]
        return {"status": "ok", "mode": "database", "person": {"id": str(person_id)},
                "people": [], "edges": edges, "truncated": len(edges) >= 100,
                "filters": filters.to_dict(), "version": f"graph-db:{coverage.import_id}",
                "coverage": self.dataset()["coverage"]}

    def owns_job(self, job_id: str) -> bool:
        row = self.connection().execute(
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
        for path in paths:
            path["people"] = [people.get(str(person["id"]),
                                         placeholder(PEOPLE, str(person["id"]), "not_requested"))
                              for person in path.get("people", ())]
            for edge in path.get("edges", ()):
                refs = edge.get("evidence_refs", ())
                edge["works"] = [works[ref.split(":", 1)[1]] for ref in refs
                                 if ref.startswith("work:") and ref.split(":", 1)[1] in works]
                edge["phd"] = [{"source_record": ref.split(":", 1)[1]} for ref in refs
                               if ref.startswith("phd:")]
                edge["types"] = ([  "coauthor"] if edge["works"] else []) + (
                    ["phd"] if edge["phd"] else [])
                edge["shared_works"] = len(edge["works"])
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
