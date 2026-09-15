"""Bounded RAM-only INSPIRE graph retrieval.

This module deliberately has no persistent cache or database path.  Every public
operation opens SQLite ``:memory:``, stores only the records retrieved for that
operation through the normal sanitizers, builds one ephemeral snapshot, and then
closes the database.  A route found here is therefore exact only in that
retrieved graph, never an assertion about the whole INSPIRE corpus.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
import time
import unicodedata
from typing import Any

from .graph import Filters, Graph, GraphError
from .pipeline import PipelineError, build_snapshot, open_db, store_record
from .historical import apply_historical, historical_neighbors
from .identity_guard import apply_identity_guard


class OnDemandError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass
class _Session:
    engine: "OnDemand"
    connection: Any = field(init=False)
    started: float = field(default_factory=time.monotonic)
    requests: int = 0
    partial: bool = False
    failures: list[str] = field(default_factory=list)
    fetched_profiles: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        self.connection = open_db(":memory:")

    def close(self) -> None:
        self.connection.close()

    @property
    def deadline(self) -> float:
        return self.started + self.engine.MAX_SECONDS

    def _remaining(self) -> float:
        return self.deadline - time.monotonic()

    def fetch(self, collection: str, query: str, *, size: int, page: int = 1, sort: str | None = None) -> list[dict[str, Any]]:
        if self.requests >= self.engine.MAX_REQUESTS:
            raise OnDemandError("resource_limit", "The live retrieval request limit was reached.")
        if self._remaining() <= 0:
            raise OnDemandError("resource_limit", "The live retrieval deadline was reached.")
        self.requests += 1
        try:
            response = self.engine.client.search(collection, query, size=size, page=page, sort=sort, deadline=self.deadline)
        except Exception as error:  # RemoteError is intentionally duck-typed during client replacement.
            code = getattr(error, "code", "upstream_unavailable")
            message = getattr(error, "message", str(error) or "The live source did not respond.")
            self.failures.append(f"{code}: {message}")
            evidence = self.connection.execute("select count(*) from source_records").fetchone()[0]
            # Before any public record is safely retained this is an upstream
            # failure (or a transport resource limit), not a graph conclusion.
            # Once there is a partial graph, explain that it is incomplete.
            status = code if evidence == 0 and code in {"upstream_unavailable", "resource_limit"} else "search_incomplete"
            raise OnDemandError(status, f"Live retrieval failed: {message}") from error
        if not isinstance(response, dict):
            raise OnDemandError("search_incomplete", "Live retrieval returned an invalid response.")
        hits_container = response.get("hits")
        hits = hits_container.get("hits") if isinstance(hits_container, dict) else None
        if not isinstance(hits, list) or not all(isinstance(hit, dict) for hit in hits):
            raise OnDemandError("search_incomplete", "Live retrieval returned invalid result records.")
        total = hits_container.get("total") if isinstance(hits_container, dict) else None
        if isinstance(total, dict):
            total = total.get("value")
        # ``RemoteClient`` validates ``total``.  Do not infer truncation merely
        # because a page is full: a one-result exact profile query has
        # ``len(hits) == size == total`` and is complete.
        if (isinstance(total, int) and total > len(hits)) or (total is None and len(hits) >= size):
            self.partial = True
        for hit in hits:
            try:
                store_record(self.connection, collection, hit)
            except (PipelineError, KeyError, TypeError, ValueError) as error:
                self.failures.append(f"malformed {collection} record: {error}")
                raise OnDemandError("search_incomplete", "A live record could not be safely interpreted.") from error
        if collection == "literature":
            count = self.connection.execute("select count(*) from source_records where collection='literature'").fetchone()[0]
            if count > self.engine.MAX_WORKS:
                raise OnDemandError("resource_limit", "The retrieved work limit was reached.")
        return hits

    def profile(self, person_id: str) -> bool:
        if person_id in self.fetched_profiles:
            return True
        hits = self.fetch("authors", f"control_number:{person_id}", size=1)
        found = self.connection.execute(
            "select 1 from source_records where collection='authors' and recid=? and deleted=0", (person_id,)
        ).fetchone()
        if found is None:
            # A nonmatching hit never creates a person from a query string.
            return False
        self.fetched_profiles.add(person_id)
        return bool(hits)

    def literature(self, person_id: str, filters: Filters) -> None:
        self.fetch("literature", self.engine.literature_query(person_id, filters), size=self.engine.literature_page_size(filters), sort="mostrecent")

    def reverse_students(self, adviser_id: str) -> None:
        # The documented field is an INSPIRE reference. No name search is used
        # to infer a student relationship.
        self.fetch("authors", f"advisors.record.$ref:{adviser_id}", size=self.engine.REVERSE_STUDENT_PAGE_SIZE)

    def snapshot(self) -> dict[str, Any]:
        snapshot = build_snapshot(
            self.connection,
            {
                "label": "Live retrieved INSPIRE subgraph",
                "description": "RAM-only bounded retrieval; counts cover retrieved records only.",
                "examples": [],
                "literature": [],
                "authors": [],
            },
        )
        if len(snapshot["people"]) > self.engine.MAX_PEOPLE:
            raise OnDemandError("resource_limit", "The retrieved people limit was reached.")
        snapshot["coverage"] = self.coverage(snapshot)
        return apply_identity_guard(apply_historical(snapshot), self.connection)

    def coverage(self, snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
        people = self.connection.execute("select count(*) from source_records where collection='authors' and deleted=0").fetchone()[0]
        works = self.connection.execute("select count(*) from source_records where collection='literature' and deleted=0").fetchone()[0]
        return {
            **{key: value for key, value in (snapshot or {}).get('coverage', {}).items() if key.startswith(('historical_', 'identity_'))},
            "label": "Live retrieved INSPIRE subgraph",
            "description": "RAM-only, bounded live retrieval. Counts are retrieved records, not INSPIRE totals.",
            "complete": False,
            "queries": [],
            "failures": list(self.failures),
            "retrieved": {"profiles": people, "works": works, "people": len(snapshot["people"]) if snapshot else None},
            "requests": self.requests,
            "partial": self.partial,
        }


class OnDemand:
    """A no-disk, bounded live connection engine.

    ``seed_snapshot`` is accepted for forward compatibility but deliberately is
    not merged in this first mode: default and current behavior remain a pure,
    predictable live-retrieval scope rather than silently mixing two corpora.
    """

    MAX_REQUESTS = 12
    MAX_SECONDS = 20.0
    MAX_WORKS = 400
    MAX_PEOPLE = 5_000
    MAX_PROFILE_EXPANSIONS = 6
    LITERATURE_PAGE_SIZE = 25
    REVERSE_STUDENT_PAGE_SIZE = 25

    def __init__(self, client: Any, seed_snapshot: dict[str, Any] | None = None) -> None:
        self.client = client
        self.seed_snapshot = seed_snapshot

    @classmethod
    def literature_page_size(cls, filters: Filters) -> int:
        # A handful of complete ATLAS/CMS records fits the transport body cap.
        return min(5, cls.LITERATURE_PAGE_SIZE) if filters.max_authors is None or filters.max_authors > 100 else cls.LITERATURE_PAGE_SIZE

    @staticmethod
    def literature_query(person_id: str, filters: Filters) -> str:
        # Use the documented INSPIRE reference field, never the display-name
        # shorthand (and never ``a <numeric-id>``, which does not mean the
        # same thing upstream).  The request is still sent only through
        # RemoteClient, which owns host, response, timeout, and pacing bounds.
        query = f"authors.record.$ref:{person_id}"
        if filters.max_authors is not None:
            query += f" AND author_count:{filters.min_authors}->{filters.max_authors}"
        elif filters.min_authors > 1:
            query += f" AND author_count:{filters.min_authors}+"
        return query

    @staticmethod
    def pair_literature_query(source: str, target: str, filters: Filters) -> str:
        """A direct pair lookup before either endpoint's recent-work page."""
        query = f"authors.record.$ref:{source} AND authors.record.$ref:{target}"
        if filters.max_authors is not None:
            query += f" AND author_count:{filters.min_authors}->{filters.max_authors}"
        elif filters.min_authors > 1:
            query += f" AND author_count:{filters.min_authors}+"
        return query

    @staticmethod
    def _person_id(value: Any) -> str:
        if isinstance(value, bool):
            raise OnDemandError("invalid_request", "An INSPIRE numeric author record ID is required.")
        result = str(value)
        # ``str.isdigit`` accepts many non-ASCII digits. INSPIRE record IDs are
        # decimal ASCII positive integers, and record zero is not a person ID.
        if not re.fullmatch(r"[1-9][0-9]{0,11}", result):
            raise OnDemandError("invalid_request", "An INSPIRE numeric author record ID is required.")
        return result

    @staticmethod
    def _filters(value: Filters | dict[str, Any] | None) -> Filters:
        if value is None:
            return Filters()
        return value if isinstance(value, Filters) else Filters.from_dict(value)

    @staticmethod
    def _author_search_query(value: str) -> str:
        """Turn an identity input into one conservative upstream query.

        This does not accept raw INSPIRE query language from the UI.  Numeric
        records and conventional ORCIDs use field queries; name lookup permits
        only literal human-name tokens across documented name and alias fields.
        """
        query = unicodedata.normalize("NFC", value.strip())
        if re.fullmatch(r"[0-9]+", query):
            if not re.fullmatch(r"[1-9][0-9]{0,11}", query):
                raise OnDemandError("invalid_request", "An INSPIRE numeric author record ID must be positive.")
            return f"control_number:{query}"
        if re.fullmatch(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]", query, re.IGNORECASE):
            return f'ids.value:"{query.upper()}"'
        if any(ord(character) < 32 or ord(character) == 127 for character in query):
            raise OnDemandError("invalid_request", "Search must be a numeric INSPIRE ID, ORCID, or a plain name.")
        # Search individual Unicode letter/number tokens.  This supports name
        # order differences in INSPIRE ("Hostert, Matheus" vs the input
        # "Matheus Hostert") and does not admit query-language punctuation.
        tokens = re.findall(r"[^\W_]+", query, re.UNICODE)
        if not tokens:
            raise OnDemandError("invalid_request", "Search must be a numeric INSPIRE ID, ORCID, or a plain name.")
        fields = ("name.value", "name.name_variants", "name.preferred_name")
        return " AND ".join(
            "(" + " OR ".join(f'{field}:"{token}"' for field in fields) + ")"
            for token in tokens
        )

    def _run(self) -> _Session:
        return _Session(self)

    @staticmethod
    def _base(session: _Session, snapshot: dict[str, Any]) -> dict[str, Any]:
        return {
            "version": snapshot["version"],
            "coverage": session.coverage(snapshot),
            "counts_scope": "retrieved",
            "mode": "live",
            "global_shortest_proven": False,
        }

    @staticmethod
    def _queryable_people(result: dict[str, Any]) -> dict[str, Any]:
        """Mark only public, retrieved people as selectable live identities."""
        if isinstance(result.get("person"), dict):
            result["person"] = {**result["person"], "queryable": True}
        if isinstance(result.get("results"), list):
            result["results"] = [{**person, "queryable": True} if isinstance(person, dict) else person for person in result["results"]]
        if isinstance(result.get("people"), list):
            result["people"] = [{**person, "queryable": True} if isinstance(person, dict) else person for person in result["people"]]
        if isinstance(result.get("collaborators"), list):
            result["collaborators"] = [
                {**item, "person": {**item["person"], "queryable": True}}
                if isinstance(item, dict) and isinstance(item.get("person"), dict) else item
                for item in result["collaborators"]
            ]
        for path in result.get("paths", []) if isinstance(result.get("paths"), list) else []:
            if isinstance(path, dict) and isinstance(path.get("people"), list):
                path["people"] = [{**person, "queryable": True} if isinstance(person, dict) else person for person in path["people"]]
        return result

    @staticmethod
    def _error(error: OnDemandError | GraphError, **extra: Any) -> dict[str, Any]:
        return {"status": error.code, "message": error.message, "counts_scope": "retrieved", "mode": "live",
                "global_shortest_proven": False, **extra}

    @staticmethod
    def _matched_people(snapshot: dict[str, Any], hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Return only public author records in this response, in hit order.

        Building a snapshot can create a literature-only adviser placeholder
        from an otherwise matched student's PhD entry. That placeholder is
        valid graph evidence but is not an author-search result.
        """
        people = {str(person.get("id")): person for person in snapshot.get("people", []) if isinstance(person, dict)}
        ordered: list[dict[str, Any]] = []
        seen: set[str] = set()
        for hit in hits:
            metadata = hit.get("metadata") if isinstance(hit.get("metadata"), dict) else hit
            recid = hit.get("id") or (metadata.get("control_number") if isinstance(metadata, dict) else None)
            recid = str(recid) if isinstance(recid, (str, int)) and not isinstance(recid, bool) else ""
            if recid in seen or recid not in people:
                continue
            seen.add(recid)
            ordered.append(people[recid])
        return ordered

    def search(self, query: str) -> dict[str, Any]:
        if not isinstance(query, str) or not 1 <= len(query.strip()) <= 120:
            raise OnDemandError("invalid_request", "Search must contain 1–120 characters.")
        session = self._run()
        try:
            hits = session.fetch("authors", self._author_search_query(query), size=25)
            snapshot = session.snapshot()
            results = self._matched_people(snapshot, hits)
            status = "ambiguous" if len(results) > 1 or session.partial else ("ok" if results else "not_found")
            return self._queryable_people({"status": status, "results": results, "source": "live", "message": "Results are a bounded live page." if session.partial else "", **self._base(session, snapshot)})
        except OnDemandError as error:
            return self._error(error, results=[], source="live")
        finally:
            session.close()

    def _retrieve_person(self, session: _Session, person_id: str, filters: Filters, *, literature: bool, reverse: bool) -> bool:
        if not session.profile(person_id):
            return False
        if literature:
            session.literature(person_id, filters)
        if reverse:
            session.reverse_students(person_id)
            for neighbor in historical_neighbors(person_id):
                session.profile(neighbor)
        return True

    def _retrieve_pair(self, session: _Session, source: str, target: str, filters: Filters) -> None:
        session.fetch("literature", self.pair_literature_query(source, target, filters),
                      size=self.literature_page_size(filters), sort="mostrecent")

    @staticmethod
    def _frontier(snapshot: dict[str, Any], source: str, target: str, excluded: set[str]) -> list[str]:
        sides: list[list[str]] = []
        for focus in (source, target):
            candidates: list[str] = []
            for work in snapshot["works"]:
                if focus in work.get("authors", []):
                    for person_id in work.get("authors", []):
                        person_id = str(person_id)
                        if person_id not in {source, target} and person_id not in excluded and person_id not in candidates:
                            candidates.append(person_id)
            sides.append(candidates)
        # Fetch one candidate from each side before taking a second candidate
        # from either.  That makes the bounded expansion genuinely guided from
        # both endpoints instead of spending its two live lookups on one side.
        ordered: list[str] = []
        for index in range(max((len(side) for side in sides), default=0)):
            for candidates in sides:
                if index < len(candidates) and candidates[index] not in ordered:
                    ordered.append(candidates[index])
        return ordered

    def _graph_result(self, session: _Session, filters: Filters) -> tuple[dict[str, Any], Graph]:
        snapshot = session.snapshot()
        return snapshot, Graph(snapshot, filters)

    def profile(self, person_id: Any, filters: Filters | dict[str, Any] | None = None) -> dict[str, Any]:
        person_id, graph_filters = self._person_id(person_id), self._filters(filters)
        session = self._run()
        try:
            if not self._retrieve_person(session, person_id, graph_filters, literature=True, reverse=graph_filters.genealogy):
                return {"status": "not_found", "message": "No public INSPIRE profile was retrieved for this ID.", "counts_scope": "retrieved", "mode": "live", "global_shortest_proven": False}
            snapshot, graph = self._graph_result(session, graph_filters)
            result = graph.profile(person_id)
            result["status"] = "ok"
            result["retrieved_publications"] = result["indexed_publications"]
            return self._queryable_people(result | self._base(session, snapshot))
        except OnDemandError as error:
            return self._error(error)
        except GraphError as error:
            return self._error(error)
        finally:
            session.close()

    def neighborhood(self, person_id: Any, filters: Filters | dict[str, Any] | None = None, limit: int = 40) -> dict[str, Any]:
        person_id, graph_filters = self._person_id(person_id), self._filters(filters)
        session = self._run()
        try:
            if not self._retrieve_person(session, person_id, graph_filters, literature=True, reverse=graph_filters.genealogy):
                return {"status": "not_found", "message": "No public INSPIRE profile was retrieved for this ID.", "counts_scope": "retrieved", "mode": "live", "global_shortest_proven": False}
            snapshot, graph = self._graph_result(session, graph_filters)
            return self._queryable_people(graph.neighborhood(person_id, limit) | {"status": "ok", **self._base(session, snapshot)})
        except (OnDemandError, GraphError) as error:
            return self._error(error)
        finally:
            session.close()

    def find_paths(self, source: Any, target: Any, filters: Filters | dict[str, Any] | None = None, alternatives: int = 3) -> dict[str, Any]:
        source, target, graph_filters = self._person_id(source), self._person_id(target), self._filters(filters)
        session = self._run()
        try:
            if source == target:
                if not self._retrieve_person(session, source, graph_filters, literature=False, reverse=False):
                    return {"status": "not_found", "paths": [], "message": "No public INSPIRE profile was retrieved for this ID.", "counts_scope": "retrieved", "mode": "live", "global_shortest_proven": False}
                snapshot, graph = self._graph_result(session, graph_filters)
                result = graph.find_paths(source, target, alternatives)
                result["exact_for_retrieved_graph"] = bool(result.get("exact"))
                result["exact"] = False
                return self._queryable_people(result | self._base(session, snapshot) | {"global_shortest_proven": True})
            # Confirm both profiles first. Then a precise pair query reaches
            # older shared papers that a recent-25 endpoint page can miss. A
            # direct graph edge is already a globally shortest route, so this
            # lets us return without retrieving either full ego neighborhood.
            if not self._retrieve_person(session, source, graph_filters, literature=False, reverse=False):
                return {"status": "not_found", "paths": [], "message": "No public INSPIRE profile was retrieved for the source ID.", "counts_scope": "retrieved", "mode": "live", "global_shortest_proven": False}
            if not self._retrieve_person(session, target, graph_filters, literature=False, reverse=False):
                return {"status": "not_found", "paths": [], "message": "No public INSPIRE profile was retrieved for the target ID.", "counts_scope": "retrieved", "mode": "live", "global_shortest_proven": False}
            self._retrieve_pair(session, source, target, graph_filters)
            snapshot, graph = self._graph_result(session, graph_filters)
            result = graph.find_paths(source, target, alternatives)
            if result["status"] == "ok" and result["paths"] and result["paths"][0]["hops"] <= 1:
                result["exact_for_retrieved_graph"] = bool(result.get("exact"))
                result["exact"] = False
                return self._queryable_people(result | self._base(session, snapshot) | {
                    "global_shortest_proven": True,
                    "scope": "Shortest path is exact only within the retrieved live graph.",
                })

            if not self._retrieve_person(session, source, graph_filters, literature=True, reverse=graph_filters.genealogy):
                # The profile was already checked above. This branch only keeps
                # the response honest if a future session implementation drops
                # an already retrieved record.
                return {"status": "search_incomplete", "paths": [], "exact": False, "alternatives_truncated": False,
                        "exact_for_retrieved_graph": False, "filters": graph_filters.to_dict(),
                        "message": "The bounded retrieval did not retain the source profile.", **self._base(session, snapshot)}
            if not self._retrieve_person(session, target, graph_filters, literature=True, reverse=graph_filters.genealogy):
                return {"status": "search_incomplete", "paths": [], "exact": False, "alternatives_truncated": False,
                        "exact_for_retrieved_graph": False, "filters": graph_filters.to_dict(),
                        "message": "The bounded retrieval did not retain the target profile.", **self._base(session, snapshot)}
            snapshot, graph = self._graph_result(session, graph_filters)
            result = graph.find_paths(source, target, alternatives)
            if result["status"] == "no_path":
                for candidate in self._frontier(snapshot, source, target, session.fetched_profiles)[:2]:
                    if len(session.fetched_profiles) >= self.MAX_PROFILE_EXPANSIONS + 2:
                        break
                    self._retrieve_person(session, candidate, graph_filters, literature=True, reverse=False)
                snapshot, graph = self._graph_result(session, graph_filters)
                result = graph.find_paths(source, target, alternatives)
            if result["status"] == "no_path":
                return {"status": "search_incomplete", "paths": [], "exact": False, "alternatives_truncated": False,
                        "exact_for_retrieved_graph": False, "filters": graph_filters.to_dict(),
                        "message": "No route was found in the bounded retrieved graph; this is not evidence that no INSPIRE route exists.",
                        **self._base(session, snapshot)}
            if result["status"] == "not_indexed":
                return {"status": "search_incomplete", "paths": [], "exact": False, "alternatives_truncated": False,
                        "exact_for_retrieved_graph": False, "filters": graph_filters.to_dict(),
                        "message": "The bounded retrieval did not retain both requested people.", **self._base(session, snapshot)}
            global_proven = result["status"] == "ok" and bool(result["paths"]) and result["paths"][0]["hops"] <= 1
            result["exact_for_retrieved_graph"] = bool(result.get("exact"))
            result["exact"] = False
            return self._queryable_people(result | self._base(session, snapshot) | {"global_shortest_proven": global_proven,
                                                                                        "scope": "Shortest path is exact only within the retrieved live graph."})
        except (OnDemandError, GraphError) as error:
            return self._error(error, paths=[], exact=False, alternatives_truncated=False)
        finally:
            session.close()

    def ancestry(self, person_id: Any, filters: Filters | dict[str, Any] | None = None, direction: str = "ancestors", limit: int = 100) -> dict[str, Any]:
        del person_id, filters, direction, limit
        return {"status": "unavailable", "message": "Ancestry is unavailable in bounded on-demand mode; retrieved reverse adviser pages are incomplete.", "counts_scope": "retrieved", "mode": "live", "global_shortest_proven": False}

    def centrality(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        del args, kwargs
        return {"status": "unavailable", "message": "Global centrality is unavailable in on-demand mode.", "counts_scope": "retrieved", "mode": "live", "global_shortest_proven": False}
