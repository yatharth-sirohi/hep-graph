"""Version-pinned graph-provider boundary.

One provider instance serves one search for its whole life, so a promotion
cannot change the graph under a running proof.  ``ProviderOracle`` is the seam
HLBES sees: it refuses a response whose version or filters differ from the ones
the search was pinned to, rather than letting two graphs be mixed silently.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Protocol

from .graph import Filters
from .hlbes import COMPLETE, PARTIAL, UNKNOWN, Neighborhood, OracleStopped


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
