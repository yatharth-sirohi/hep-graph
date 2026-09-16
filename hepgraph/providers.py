"""Version-pinned graph-provider boundary for the snapshot migration.

The fixture adapter is deliberately in-memory and test-only.  It is not a
production snapshot loader: a complete production claim needs an independently
validated, private source acquisition and storage pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Protocol

from .graph import Filters, Graph
from .hlbes import (COMPLETE, EXACT, NO_PATH, PARTIAL, SEARCH_INCOMPLETE, UNKNOWN,
                    VERIFIED, HLBES, Neighborhood, OracleStopped, SearchResult)


def filter_key(filters: Filters) -> str:
    """A stable key covering every edge-affecting filter."""
    return json.dumps(filters.to_dict(), sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class GraphVersion:
    snapshot_id: str
    source_cutoff: str | None
    schema_version: str


@dataclass(frozen=True)
class ProviderNeighborhood:
    version: GraphVersion
    filter_key: str
    members: frozenset[str]
    status: str
    reason: str = ""
    cursor: Any = None

    def __post_init__(self) -> None:
        if self.status not in {UNKNOWN, PARTIAL, COMPLETE}:
            raise ValueError("invalid neighborhood status")


class GraphProvider(Protocol):
    """One pinned provider instance per search; no active-pointer rereads."""

    def get_graph_version(self) -> GraphVersion: ...

    def get_completeness(self, filters: Filters) -> bool: ...

    def resolve_author(self, author_id: str) -> dict[str, Any] | None: ...

    def get_neighbors(self, author_id: str, filters: Filters) -> ProviderNeighborhood: ...

    def get_neighbors_batch(self, author_ids: tuple[str, ...], filters: Filters) -> dict[str, ProviderNeighborhood]: ...

    def get_edge_evidence_refs(self, source: str, target: str, filters: Filters) -> tuple[str, ...]: ...

    def get_work_metadata(self, work_id: str) -> dict[str, Any] | None: ...


class FixtureGraphProvider:
    """Small trusted fixture, never a certificate for a sampled INSPIRE pilot.

    ``complete=True`` is an assertion supplied by the test that its entire
    synthetic universe is present.  The default deliberately cannot prove a
    negative result or a multi-hop shortest path.
    """

    def __init__(self, snapshot: dict[str, Any], *, complete: bool = False) -> None:
        self.snapshot = snapshot
        self.complete = complete
        self.version = GraphVersion(str(snapshot.get("version", "fixture")),
                                    snapshot.get("source_cutoff"), "fixture-v1")
        self._graphs: dict[str, Graph] = {}

    def get_graph_version(self) -> GraphVersion:
        return self.version

    def get_completeness(self, filters: Filters) -> bool:
        return self.complete

    def _graph(self, filters: Filters) -> Graph:
        key = filter_key(filters)
        if key not in self._graphs:
            self._graphs[key] = Graph(self.snapshot, filters)
        return self._graphs[key]

    def resolve_author(self, author_id: str) -> dict[str, Any] | None:
        return self._graph(Filters()).people.get(str(author_id))

    def get_neighbors(self, author_id: str, filters: Filters) -> ProviderNeighborhood:
        graph = self._graph(filters)
        author_id = str(author_id)
        if author_id not in graph.people:
            return ProviderNeighborhood(self.version, filter_key(filters), frozenset(), UNKNOWN,
                                        "author_not_in_snapshot")
        members = frozenset(graph._neighbors(author_id))
        return ProviderNeighborhood(self.version, filter_key(filters), members,
                                    COMPLETE if self.complete else PARTIAL,
                                    "" if self.complete else "fixture_coverage_incomplete")

    def get_neighbors_batch(self, author_ids: tuple[str, ...], filters: Filters) -> dict[str, ProviderNeighborhood]:
        return {str(author_id): self.get_neighbors(str(author_id), filters) for author_id in author_ids}

    def get_edge_evidence_refs(self, source: str, target: str, filters: Filters) -> tuple[str, ...]:
        edge = self._graph(filters)._edge(str(source), str(target))
        if edge is None:
            return ()
        refs = [f"work:{work['id']}" for work in edge["works"]]
        refs.extend(f"phd:{record.get('source_record')}" for record in edge["phd"]
                    if record.get("source_record") is not None)
        return tuple(refs)

    def get_work_metadata(self, work_id: str) -> dict[str, Any] | None:
        # Unfiltered evidence hydration is intentionally distinct from whether
        # the work qualifies for any particular traversal mode.
        for work in self.snapshot.get("works", ()):
            if isinstance(work, dict) and str(work.get("id")) == str(work_id):
                return work
        return None


class LiveInspireGraphProvider:
    """Adapter around a single existing DeepSession's audited, paged oracle.

    The caller still drives and serializes DeepSession and owns its budget.
    This does not turn live retrieval into a frozen, globally complete graph.
    Evidence/profile methods expose only records already in session memory.
    """

    def __init__(self, session: Any, oracle: Any) -> None:
        self.session, self.oracle = session, oracle
        self.version = GraphVersion(f"live-session:{id(session)}", None, "live")

    def get_graph_version(self) -> GraphVersion:
        return self.version

    def get_completeness(self, filters: Filters) -> bool:
        return False  # per-author proof is reported by the audited oracle

    def _graph(self) -> Graph:
        return self.session._snapshot(self.session._budget)[1]

    def resolve_author(self, author_id: str) -> dict[str, Any] | None:
        return self._graph().people.get(str(author_id))

    def get_neighbors(self, author_id: str, filters: Filters) -> ProviderNeighborhood:
        if filters != self.session.filters:
            raise ValueError("live session filters changed")
        result = self.oracle.neighborhood(str(author_id))
        return ProviderNeighborhood(self.version, filter_key(filters), result.members,
                                    result.status, cursor=result.token)

    def get_neighbors_batch(self, author_ids: tuple[str, ...], filters: Filters) -> dict[str, ProviderNeighborhood]:
        # The live oracle may internally coalesce pages. Never infer that one
        # person's completion certifies another's neighborhood.
        return {str(author_id): self.get_neighbors(str(author_id), filters) for author_id in author_ids}

    def get_edge_evidence_refs(self, source: str, target: str, filters: Filters) -> tuple[str, ...]:
        if filters != self.session.filters:
            raise ValueError("live session filters changed")
        edge = self._graph()._edge(str(source), str(target))
        if edge is None:
            return ()
        refs = [f"work:{work['id']}" for work in edge["works"]]
        refs.extend(f"phd:{record.get('source_record')}" for record in edge["phd"]
                    if record.get("source_record") is not None)
        return tuple(refs)

    def get_work_metadata(self, work_id: str) -> dict[str, Any] | None:
        return self._graph().works.get(str(work_id))


class ProviderOracle:
    """HLBES adapter that rejects version/filter mixing before proof updates."""

    def __init__(self, provider: GraphProvider, filters: Filters) -> None:
        self.provider, self.filters = provider, filters
        self.version = provider.get_graph_version()
        self.key = filter_key(filters)

    def neighborhood(self, node: str) -> Neighborhood:
        if self.provider.get_graph_version() != self.version:
            raise OracleStopped("graph_version_changed")
        result = self.provider.get_neighbors(node, self.filters)
        if result.version != self.version or result.filter_key != self.key:
            raise OracleStopped("graph_version_changed", "provider returned mixed graph semantics")
        return Neighborhood(result.members, result.status, result.cursor)


@dataclass(frozen=True)
class PinnedSearchOutcome:
    """Proof status explicitly scoped to the chosen version and filters."""

    status: str
    graph_snapshot: str
    source_cutoff: str | None
    graph_mode: str
    filters: dict[str, Any]
    global_shortest_proven: bool
    result: SearchResult | None = None
    reason: str = ""


def search_pinned_snapshot(provider: GraphProvider, source: str, target: str,
                           filters: Filters) -> PinnedSearchOutcome:
    """Bounded test-path entry point; never turn a missing author into NO_PATH.

    A production integration still needs independently certified coverage,
    private versioned evidence and server-job version pinning. This function
    makes the status/metadata contract executable on synthetic providers.
    """
    version = provider.get_graph_version()
    mode = "large" if filters.min_authors > 10 else ("all" if filters.max_authors is None else "small")

    def outcome(status: str, *, result: SearchResult | None = None,
                reason: str = "") -> PinnedSearchOutcome:
        return PinnedSearchOutcome(status, version.snapshot_id, version.source_cutoff,
                                   mode, filters.to_dict(), status == EXACT, result, reason)

    if provider.resolve_author(source) is None or provider.resolve_author(target) is None:
        return outcome("author_not_in_snapshot")
    if provider.get_graph_version() != version:
        return outcome(SEARCH_INCOMPLETE, reason="graph_version_changed")
    complete = provider.get_completeness(filters)
    result = HLBES(ProviderOracle(provider, filters)).search(str(source), str(target))
    if provider.get_graph_version() != version:
        return outcome(SEARCH_INCOMPLETE, reason="graph_version_changed")
    if not complete and result.status == EXACT:
        # A one-hop witness or same-node path is valid but the unvalidated
        # source universe cannot receive a global snapshot certificate.
        return outcome(VERIFIED, result=result, reason="snapshot_not_validated")
    if not complete and result.status == NO_PATH:
        return outcome(SEARCH_INCOMPLETE, result=result, reason="snapshot_not_validated")
    return outcome(result.status, result=result, reason=result.reason)
