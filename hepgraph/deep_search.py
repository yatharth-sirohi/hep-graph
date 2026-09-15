"""Longer, bounded, RAM-only live path retrieval.

This is deliberately separate from :mod:`hepgraph.ondemand`.  A caller owns a
``DeepSession`` on one worker thread, runs it in bounded slices, and closes it
there.  No record, cursor, or graph is written to disk.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
import hashlib
import json
import re
import threading
import time
from typing import Any, Callable, Iterable

from .graph import Filters, Graph, GraphError
from .discovery import Navigator
from .identity_guard import apply_identity_guard
from .pipeline import PipelineError, build_snapshot, open_db, ref_id, store_record


class DeepSearchError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code, self.message = code, message


@dataclass(frozen=True)
class DeepBudget:
    """A per-run allowance plus session-wide evidence ceilings."""

    max_seconds: float
    max_requests: int
    max_works: int
    max_people: int
    page_size: int = 100
    max_pages_per_person: int = 4

    @classmethod
    def standard(cls) -> "DeepBudget":
        return cls(300.0, 240, 20_000, 30_000)

    @classmethod
    def extended(cls) -> "DeepBudget":
        # Graph's production index ceiling is 50,000 people.
        return cls(900.0, 720, 50_000, 50_000)

    def validate(self) -> None:
        if (not isinstance(self.max_seconds, (int, float)) or isinstance(self.max_seconds, bool)
                or not 1 <= float(self.max_seconds) <= 900):
            raise DeepSearchError("invalid_request", "max_seconds must be between 1 and 900.")
        for field, maximum in (("max_requests", 720), ("max_works", 50_000), ("max_people", 50_000),
                               ("page_size", 100), ("max_pages_per_person", 100)):
            value = getattr(self, field)
            if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
                raise DeepSearchError("invalid_request", f"{field} is outside the supported deep-search limit.")


@dataclass
class _Cursor:
    person_id: str
    depth: int
    profile_done: bool = False
    literature_page: int = 1
    reverse_page: int = 1
    literature_done: bool = False
    reverse_done: bool = False
    next_kind: str = "literature"
    pages: int = 0
    slice_pages: int = 0
    closed: bool = False
    deferred: bool = False
    historical_enqueued: bool = False
    incomplete: list[str] = field(default_factory=list)


@dataclass
class _Side:
    name: str
    root: str
    depth: int = 0
    current: deque[_Cursor] = field(default_factory=deque)
    following: deque[_Cursor] = field(default_factory=deque)
    deferred: deque[_Cursor] = field(default_factory=deque)
    seen: dict[str, int] = field(default_factory=dict)
    closed_depths: set[int] = field(default_factory=set)


@dataclass
class _PendingValidation:
    """A candidate route whose current public identities are not all checked."""

    signature: tuple[tuple[str, ...], ...]
    people: tuple[str, ...]
    index: int = 0


def _id(value: Any) -> str:
    result = str(value)
    if isinstance(value, bool) or not re.fullmatch(r"[1-9][0-9]{0,11}", result):
        raise DeepSearchError("invalid_request", "An INSPIRE numeric author record ID is required.")
    return result


class DeepSearch:
    """Factory for owner-thread, continuation-capable deep live searches."""

    def __init__(self, client: Any, guide_snapshot: dict[str, Any] | None = None,
                 suggestion_pairs: Iterable[tuple[Any, Any]] = ()) -> None:
        self.client = client
        self.guide_snapshot = guide_snapshot
        pairs: list[tuple[str, str]] = []
        for pair in suggestion_pairs:
            if not isinstance(pair, (tuple, list)) or len(pair) != 2:
                raise DeepSearchError("invalid_request", "Each navigation suggestion must be one pair of INSPIRE IDs.")
            left, right = _id(pair[0]), _id(pair[1])
            if left == right:
                raise DeepSearchError("invalid_request", "A navigation suggestion cannot join an ID to itself.")
            canonical = (left, right) if left < right else (right, left)
            if canonical not in pairs:
                pairs.append(canonical)
        if len(pairs) > 32:
            raise DeepSearchError("invalid_request", "At most 32 navigation suggestions are supported.")
        self.suggestion_pairs = tuple(pairs)

    def start(self, source: Any, target: Any, filters: Filters | dict[str, Any] | None = None, *,
              cancel: threading.Event | None = None,
              progress: Callable[[dict[str, Any]], None] | None = None) -> "DeepSession":
        active_filters = Filters() if filters is None else (filters if isinstance(filters, Filters) else Filters.from_dict(filters))
        return DeepSession(self.client, _id(source), _id(target), active_filters, self.guide_snapshot, self.suggestion_pairs,
                           cancel or threading.Event(), progress)


class DeepSession:
    """One in-memory search state. All methods must run on its creator thread."""

    def __init__(self, client: Any, source: str, target: str, filters: Filters,
                 guide_snapshot: dict[str, Any] | None, suggestion_pairs: tuple[tuple[str, str], ...], cancel: threading.Event,
                 progress: Callable[[dict[str, Any]], None] | None) -> None:
        self.client, self.source, self.target, self.filters = client, source, target, filters
        self.cancel, self.progress_callback = cancel, progress
        self.connection = open_db(":memory:")
        self.owner = threading.get_ident()
        self.started = time.monotonic()
        self.closed = False
        self.requests = 0
        self.works = 0
        self.failures: list[dict[str, str]] = []
        self.node_ledger: dict[str, dict[str, Any]] = {}
        self.left = _Side("source", source, seen={source: 0})
        self.right = _Side("target", target, seen={target: 0})
        self.bootstrap = deque(["source_profile", "target_profile", "direct_pair"])
        # A two-hop route is globally shortest only after every qualifying
        # endpoint-pair page has been checked. Retain this cursor across runs.
        self._direct_pair_page = 1
        self._direct_pair_last_page: int | None = None
        self._direct_pair_complete = source == target
        self._direct_pair_pages_checked = 0
        self._direct_pair_records_seen = 0
        self._direct_pair_total: int | None = 0 if source == target else None
        self._direct_pair_total_exact = True
        self.guide_graph = self._guide_graph(guide_snapshot)
        self.suggestion_neighbors: dict[str, set[str]] = {}
        for left, right in suggestion_pairs:
            self.suggestion_neighbors.setdefault(left, set()).add(right)
            self.suggestion_neighbors.setdefault(right, set()).add(left)
        self.guide_pairs = self._guide_pairs()
        self.guide_used = self.guide_graph is not None or bool(self.suggestion_neighbors)
        self.suggestion_pairs_configured = len(suggestion_pairs)
        self.guide_verified = 0
        self.guide_routes_attempted: set[tuple[str, ...]] = set()
        self.guide_pairs_requested: set[tuple[str, str]] = set()
        self.best: dict[str, Any] | None = None
        self.best_version: str | None = None
        self.last_status: str | None = None
        self._prefer_left = True
        self.frontier_started = False
        self._identity_confirmed: set[str] = set()
        self._unverified_people: dict[str, str] = {}
        self._pending_validation: _PendingValidation | None = None
        self._bridge_queries_seen: set[tuple[tuple[str, ...], tuple[str, ...]]] = set()
        self._bridge_failures: dict[tuple[tuple[str, ...], tuple[str, ...]], int] = {}
        self._bridge_failure_log: list[dict[str, Any]] = []
        self._bridge_disabled_this_run = False
        self._bridge_turn = False
        # The normalized/guarded graph is immutable until a successful fetch
        # adds fresh source state (or a current-profile validation excludes an
        # ID). Retaining it makes Graph's bounded pair and neighbour caches
        # useful across cursor pages without changing evidence semantics.
        self._materialized: tuple[dict[str, Any], Graph] | None = None
        # Cross-frontier queries are only an optional accelerator. Remember
        # where the prior successful block left off so an ID-sorted Cartesian
        # product cannot spend every 12-query allowance on its first blocks.
        self._bridge_block_offset = 0
        self.navigator = Navigator(source, target, base_neighbors=self._navigation_neighbors) if callable(getattr(client, 'coauthors', None)) else None
        self._navigation_disabled = False
        self._navigation_failures: list[str] = []
        self._navigation_since_expansion = 0
        self._navigation_route: list[str] | None = None
        self._navigation_pending_route: list[str] | None = None
        self._guide_pair_pages: dict[tuple[str, str], int] = {}

    def _check_owner(self) -> None:
        if threading.get_ident() != self.owner:
            raise RuntimeError("DeepSession must run and close on its owner thread.")
        if self.closed:
            raise RuntimeError("DeepSession is closed.")

    def _invalidate_materialized(self) -> None:
        """Discard only derived state after an evidence-affecting mutation."""
        self._materialized = None

    def _navigation_neighbors(self, person_id: str) -> tuple[str, ...]:
        neighbors = set(self.suggestion_neighbors.get(person_id, ()))
        if self.filters.genealogy:
            neighbors.update(self._historical_neighbors(person_id))
        if self.guide_graph is not None:
            try:
                neighbors.update(self.guide_graph._neighbors(person_id))
            except GraphError:
                pass
        return tuple(sorted(neighbors))

    def _navigation_step(self, budget: DeepBudget) -> bool:
        """Ask INSPIRE for compact navigation hints; never import them as edges."""
        if self.navigator is None or self._navigation_disabled:
            return False
        if self.cancel.is_set():
            raise DeepSearchError('cancelled', 'The deep search was cancelled.')
        if self._run_requests >= budget.max_requests or time.monotonic() >= self._run_deadline:
            raise DeepSearchError('resource_limit', 'This deep-search slice reached its request or time allowance.')
        if self._navigation_pending_route is not None:
            self._prepare_navigation_route(budget)
            return True
        # Confirmed structured doctoral records can also guide discovery. Their
        # source records, directions and identity checks remain in Graph.
        _, graph = self._snapshot(budget)
        if self.filters.genealogy:
            for relation in graph.phd:
                self.navigator.add_link(relation['adviser'], relation['student'])
        person_id = self.navigator.next_person()
        if person_id is None:
            return False
        self._run_requests += 1
        self.requests += 1
        try:
            response = self.client.coauthors(self.literature_query(person_id, self.filters), deadline=self._run_deadline)
        except Exception as error:
            # This endpoint is an accelerator. A failed/unsupported facet must
            # leave the bibliography search available and preserve its cursors.
            self._navigation_failures.append(getattr(error, 'message', str(error)))
            self._navigation_disabled = True
            return False
        self.navigator.accept(person_id, response['authors'], truncated=response['truncated'])
        self._navigation_since_expansion += 1
        route = self.navigator.route()
        if route and len(route) > 1:
            self._navigation_route = route
            self._navigation_pending_route = route
            self._prepare_navigation_route(budget)
        self._emit('discover_coauthors')
        return True

    def _prepare_navigation_route(self, budget: DeepBudget) -> None:
        route = self._navigation_pending_route
        confirmations = self._refresh_profiles(route, budget, force=False)
        for member, confirmed in confirmations.items():
            if not confirmed:
                self.navigator.reject_person(member)
        if all(confirmations.values()):
            # A newly discovered shorter corridor takes priority over an old
            # pilot route. Keep older work queued as a fallback if it fails.
            self.guide_pairs.extendleft(reversed(list(zip(route, route[1:]))))
        # A thrown time/request/upstream exception leaves the exact route
        # pending, including when the facet graph already marked it attempted.
        self._navigation_pending_route = None

    def _reject_unproved_navigation_edges(self, graph: Graph,
                                          candidates: Iterable[tuple[str, ...]]) -> None:
        """Discard only a validated candidate's guarded-away hint pairs.

        A facet route is an evolving discovery proposal.  It can contain edges
        that have not yet been fetched, so a failed identity check for an
        unrelated graph candidate must not blacklist that whole proposal.  The
        candidate signature records exactly which person paths entered current
        profile validation; only its pairs may be rejected when the fresh,
        guarded graph no longer contains them.
        """
        if self.navigator is None:
            return
        for route in candidates:
            for left, right in zip(route, route[1:]):
                if graph._edge(left, right) is None:
                    self.navigator.reject_edge(left, right)

    @staticmethod
    def _author_count_clause(filters: Filters) -> str:
        """Return INSPIRE's inclusive author-count range for every live query."""
        # INSPIRE documents ``authorcount:100+`` as the open-ended form. Keep
        # that semantics with the API field spelling rather than inventing an
        # upper ceiling that could silently omit a qualifying large-team work.
        if filters.max_authors is None:
            return f"author_count:{filters.min_authors}+"
        return f"author_count:{filters.min_authors}->{filters.max_authors}"

    @staticmethod
    def literature_query(person_id: str, filters: Filters) -> str:
        return f"authors.record.$ref:{person_id} AND {DeepSession._author_count_clause(filters)}"

    @staticmethod
    def pair_query(source: str, target: str, filters: Filters) -> str:
        return (f"authors.record.$ref:{source} AND authors.record.$ref:{target} "
                f"AND {DeepSession._author_count_clause(filters)}")

    @staticmethod
    def _cross_query(left: list[str], right: list[str], filters: Filters) -> str:
        def group(person_ids: list[str]) -> str:
            return "(" + " OR ".join(f"authors.record.$ref:{person_id}" for person_id in person_ids) + ")"
        return f"{group(left)} AND {group(right)} AND {DeepSession._author_count_clause(filters)}"

    def _guide_graph(self, guide: dict[str, Any] | None) -> Graph | None:
        if not isinstance(guide, dict):
            return None
        try:
            return Graph(guide, self.filters)
        except GraphError:
            return None

    def _guide_path(self, start: str, end: str) -> list[str] | None:
        if start == end or (self.guide_graph is None and not self.suggestion_neighbors):
            return None

        # The saved graph supplies filter-aware neighbours; ID-only hints add
        # discovery candidates only. Neither source becomes returned evidence.
        def neighbors(person_id: str) -> tuple[str, ...]:
            found = set(self.suggestion_neighbors.get(person_id, ()))
            if self.guide_graph is not None:
                try:
                    found.update(self.guide_graph._neighbors(person_id))
                except GraphError:
                    pass
            return tuple(sorted(found))

        previous = {start: None}
        queue = deque([start])
        while queue and len(previous) <= 2_000:
            current = queue.popleft()
            for person_id in neighbors(current):
                if person_id in previous:
                    continue
                previous[person_id] = current
                if person_id == end:
                    path = [end]
                    while previous[path[-1]] is not None:
                        path.append(previous[path[-1]])
                    return list(reversed(path))
                queue.append(person_id)
        return None

    def _guide_pairs(self) -> deque[tuple[str, str]]:
        path = self._guide_path(self.source, self.target)
        return deque(zip(path, path[1:])) if path else deque()

    def _queue_guide_bridge(self, side: _Side, person_id: str) -> None:
        """Turn a stale guide corridor into bounded fresh pair verifications.

        A candidate is useful only when it was *just discovered* by a live
        frontier from the other endpoint.  Guide records themselves never enter
        the temporary SQLite database or any returned evidence.
        """
        guide_root = self.source if side is self.right else self.target
        path = self._guide_path(guide_root, person_id)
        if not path:
            return
        signature = tuple(path)
        if signature in self.guide_routes_attempted or len(self.guide_routes_attempted) >= 8:
            return
        self.guide_routes_attempted.add(signature)
        for left, right in zip(path, path[1:]):
            pair = (left, right) if left < right else (right, left)
            if pair not in self.guide_pairs_requested:
                self.guide_pairs.append((left, right))

    def _emit(self, stage: str) -> None:
        if not self.progress_callback:
            return
        explored = set(self.node_ledger) | (self.navigator.queried if self.navigator else set())
        update = {"people_explored": len(explored), "works_retrieved": self.works,
                  "elapsed_seconds": round(time.monotonic() - self.started, 3), "stage": stage,
                  "requests": self.requests, "guide_used": self.guide_used,
                  "guide_candidates_verified": self.guide_verified}
        if self.best:
            update["best_result"] = self.best
        try:
            self.progress_callback(update)
        except Exception:
            # UI/reporting must never turn a bounded retrieval into an unsafe
            # unhandled job failure.
            pass

    def _total(self, response: dict[str, Any]) -> tuple[int, bool]:
        """Return the reported total and whether INSPIRE states it is exact."""
        hits = response.get("hits", {})
        total = hits.get("total") if isinstance(hits, dict) else None
        exact = isinstance(total, int) and not isinstance(total, bool)
        if isinstance(total, dict):
            relation = total.get("relation")
            total = total.get("value")
            # RemoteClient preserves ``eq``/``gte`` from INSPIRE. A legacy or
            # custom client lacking a relation remains usable for retrieval,
            # but cannot prove that a direct query has been exhausted.
            exact = relation == "eq"
        if isinstance(total, bool) or not isinstance(total, int) or total < 0:
            raise DeepSearchError("upstream_unavailable", "INSPIRE returned an invalid result total.")
        return total, exact

    def _fetch(self, collection: str, query: str, page: int, budget: DeepBudget, *,
               size: int | None = None) -> tuple[list[dict[str, Any]], int, bool]:
        if self.cancel.is_set():
            raise DeepSearchError("cancelled", "The deep search was cancelled.")
        if self._run_requests >= budget.max_requests:
            raise DeepSearchError("resource_limit", "This deep-search slice reached its request allowance.")
        if time.monotonic() >= self._run_deadline:
            raise DeepSearchError("resource_limit", "This deep-search slice reached its time allowance.")
        self._run_requests += 1
        self.requests += 1
        try:
            response = self.client.search(collection, query, size=size or budget.page_size, page=page,
                                          sort="mostrecent", deadline=self._run_deadline)
        except Exception as error:
            code = getattr(error, "code", "upstream_unavailable")
            message = getattr(error, "message", str(error) or "INSPIRE did not respond.")
            self.failures.append({"collection": collection, "query": query, "error": f"{code}: {message}"})
            raise DeepSearchError(code if self.requests == 1 else "search_incomplete", message) from error
        if not isinstance(response, dict) or not isinstance(response.get("hits"), dict):
            raise DeepSearchError("upstream_unavailable", "INSPIRE returned an invalid response.")
        hits = response["hits"].get("hits")
        if not isinstance(hits, list) or not all(isinstance(hit, dict) for hit in hits):
            raise DeepSearchError("upstream_unavailable", "INSPIRE returned invalid result records.")
        total, total_exact = self._total(response)
        for hit in hits:
            if self.cancel.is_set():
                raise DeepSearchError("cancelled", "The deep search was cancelled.")
            try:
                store_record(self.connection, collection, hit)
                # ``store_record`` can update an existing source row as well
                # as add a new one, so cached normalization must never survive
                # any successful write. This also covers a partial page if a
                # later malformed record makes the fetch raise.
                self._invalidate_materialized()
            except (PipelineError, TypeError, KeyError, ValueError) as error:
                self.failures.append({"collection": collection, "query": query, "error": f"malformed record: {error}"})
                raise DeepSearchError("search_incomplete", "A live record could not be safely interpreted.") from error
        self.works = self.connection.execute("select count(*) from source_records where collection='literature' and deleted=0").fetchone()[0]
        if self.works > budget.max_works:
            raise DeepSearchError("resource_limit", "The deep-search work ceiling was reached.")
        return hits, total, total_exact

    def _has_profile(self, person_id: str) -> bool:
        row = self.connection.execute(
            "select 1 from source_records where collection='authors' and recid=? and deleted=0", (person_id,)
        ).fetchone()
        return bool(row)

    def _profile(self, person_id: str, budget: DeepBudget, *, force: bool = False) -> bool:
        if self._has_profile(person_id) and not force:
            return True
        hits, _, _ = self._fetch("authors", f"control_number:{person_id}", 1, budget)
        # An old row in RAM cannot turn an unrelated or empty response into a
        # current identity confirmation.
        return person_id in self._profile_people(hits) and self._has_profile(person_id)

    @staticmethod
    def _profile_query(person_ids: list[str]) -> str:
        return " OR ".join(f"control_number:{person_id}" for person_id in person_ids)

    def _refresh_profiles(self, person_ids: list[str], budget: DeepBudget, *, force: bool) -> dict[str, bool]:
        """Fetch already discovered profiles in exact-ID batches of at most 25.

        A batch saves requests only. Each requested ID must still occur in the
        returned page and in a sanitized, non-deleted author record. A missing
        item falls back to its exact individual query, preventing a partial or
        broadened upstream result from becoming a false confirmation.
        """
        ordered = list(dict.fromkeys(person_id for person_id in person_ids if person_id))
        results: dict[str, bool] = {}
        needed = [person_id for person_id in ordered if force or not self._has_profile(person_id)]
        for person_id in ordered:
            if person_id not in needed:
                results[person_id] = True
        for start in range(0, len(needed), 25):
            chunk = needed[start:start + 25]
            if len(chunk) == 1:
                person_id = chunk[0]
                results[person_id] = self._profile(person_id, budget, force=force)
                continue
            hits, _, _ = self._fetch("authors", self._profile_query(chunk), 1, budget,
                                  size=max(25, len(chunk)))
            returned = set(self._profile_people(hits))
            for person_id in chunk:
                if person_id in returned and self._has_profile(person_id):
                    results[person_id] = True
                else:
                    results[person_id] = self._profile(person_id, budget, force=True)
        return results

    @staticmethod
    def _work_people(hits: list[dict[str, Any]]) -> list[str]:
        result: list[str] = []
        for hit in hits:
            metadata = hit.get("metadata") if isinstance(hit.get("metadata"), dict) else {}
            for author in metadata.get("authors", []) if isinstance(metadata.get("authors"), list) else []:
                if isinstance(author, dict):
                    person_id = ref_id(author.get("record"))
                    if person_id and person_id not in result:
                        result.append(person_id)
        return result

    @staticmethod
    def _profile_people(hits: list[dict[str, Any]]) -> list[str]:
        result: list[str] = []
        for hit in hits:
            metadata = hit.get("metadata") if isinstance(hit.get("metadata"), dict) else {}
            recid = hit.get("id") or metadata.get("control_number")
            if isinstance(recid, int):
                recid = str(recid)
            if isinstance(recid, str) and re.fullmatch(r"[1-9][0-9]{0,11}", recid) and recid not in result:
                result.append(recid)
        return result

    def _record_node(self, cursor: _Cursor) -> None:
        self.node_ledger[cursor.person_id] = {
            "depth": cursor.depth, "closed": cursor.closed, "pages": cursor.pages,
            "literature_next_page": cursor.literature_page, "reverse_next_page": cursor.reverse_page,
            "incomplete": list(cursor.incomplete),
            "deferred": cursor.deferred,
        }

    @staticmethod
    def _historical_neighbors(person_id: str) -> list[str]:
        # The overlay is an optional, separately audited module while it is
        # being assembled. Once present it is pure and never contacts a source.
        try:
            from .historical import historical_neighbors
        except ImportError:
            return []
        return historical_neighbors(person_id)

    @staticmethod
    def _advance(side: _Side) -> None:
        # Deferred pages are a fairness checkpoint, not a breadth barrier:
        # process already known next-layer candidates before returning to a
        # prolific person's later pages.
        if side.current or not side.following:
            return
        side.closed_depths.add(side.depth)
        side.depth += 1
        side.current, side.following = side.following, deque()

    @staticmethod
    def _restore_deferred(side: _Side) -> None:
        """Resume page cursors at their original breadth depth next slice."""
        while side.deferred:
            cursor = side.deferred.popleft()
            cursor.deferred = False
            cursor.slice_pages = 0
            side.current.append(cursor)

    def _enqueue(self, side: _Side, person_id: str, depth: int, budget: DeepBudget) -> bool:
        if person_id in side.seen:
            return person_id in (self.right.seen if side is self.left else self.left.seen)
        if len(set(self.left.seen) | set(self.right.seen)) >= budget.max_people:
            raise DeepSearchError("resource_limit", "The deep-search people ceiling was reached.")
        side.seen[person_id] = depth
        side.following.append(self._cursor(person_id, depth))
        self._queue_guide_bridge(side, person_id)
        return person_id in (self.right.seen if side is self.left else self.left.seen)

    def _cross_frontier(self, budget: DeepBudget) -> bool:
        """Fetch one bounded cross-frontier coauthor page, if a new set exists."""
        if self._bridge_disabled_this_run or self._bridge_queries_this_run >= 12:
            return False
        # Keep batches deterministic, including for the public query audit.
        # Diagonal scheduling below, rather than member order, prevents one
        # side's early blocks from consuming an entire bounded slice.
        left_ids = sorted(person_id for person_id in self.left.seen if person_id not in self._unverified_people)
        right_ids = sorted(person_id for person_id in self.right.seen if person_id not in self._unverified_people)
        # INSPIRE accepted profile OR batches but rejected live 25x25
        # literature combinations. Keep this optional probe deliberately small.
        left_blocks = [tuple(left_ids[start:start + 10]) for start in range(0, len(left_ids), 10)]
        right_blocks = [tuple(right_ids[start:start + 10]) for start in range(0, len(right_ids), 10)]
        # Diagonal rounds alternate both dimensions. A row-major product would
        # spend a 12-query slice on the oldest left block when the right side is
        # broad; a column-major product merely reverses that starvation.
        total_blocks = len(left_blocks) * len(right_blocks)
        if not total_blocks:
            return False
        start = self._bridge_block_offset % total_blocks
        # A frontier may contain thousands of blocks per side. Generate the
        # diagonal product lazily and bound skip work when old signatures no
        # longer match freshly extended batches.
        examined = 0
        for offset in range(min(total_blocks, 256)):
            index = (start + offset) % total_blocks
            round_index, left_index = divmod(index, len(left_blocks))
            signature = (left_blocks[left_index], right_blocks[(left_index + round_index) % len(right_blocks)])
            examined += 1
            if signature in self._bridge_queries_seen or self._bridge_failures.get(signature, 0) >= 2:
                continue
            query = self._cross_query(list(signature[0]), list(signature[1]), self.filters)
            if len(query) >= 4096:
                continue
            self._bridge_queries_this_run += 1
            try:
                self._fetch("literature", query, 1, budget, size=self._literature_size(budget))
            except DeepSearchError as error:
                # This is an optimization only. A transient/unsupported
                # upstream OR query must never abort ordinary BFS. Preserve
                # hard session boundaries so cancellation and resource
                # limits remain truthful and resumable.
                if error.code in {"cancelled", "resource_limit"}:
                    raise
                attempts = self._bridge_failures.get(signature, 0) + 1
                self._bridge_failures[signature] = attempts
                self._bridge_failure_log.append({
                    "left": list(signature[0]), "right": list(signature[1]),
                    "attempt": attempts, "code": error.code, "message": error.message,
                })
                # Keep the offset unchanged: a failed optional query must stay
                # retryable in the same retained session, as before.
                self._bridge_disabled_this_run = True
                return False
            # Advance only after success. The next invocation begins at the
            # next Cartesian block rather than continually favoring block 0.
            self._bridge_block_offset = index + 1
            self._bridge_queries_seen.add(signature)
            return True
        self._bridge_block_offset = start + examined
        return False

    def _cursor(self, person_id: str, depth: int, *, profile_done: bool = False) -> _Cursor:
        return _Cursor(person_id, depth, profile_done=profile_done, reverse_done=not self.filters.genealogy)

    def _literature_size(self, budget: DeepBudget) -> int:
        # Thousands of authors per record can make a 100-paper response exceed
        # the transport bound. Use small, consistently numbered pages for broad
        # team-size filters, retaining full author lists and exact counts.
        return min(5, budget.page_size) if self.filters.max_authors is None or self.filters.max_authors > 100 else budget.page_size

    def _page_done(self, cursor: _Cursor, total: int, page: int, budget: DeepBudget, kind: str,
                   page_size: int | None = None) -> None:
        if page * (page_size or budget.page_size) >= total:
            if kind == "literature": cursor.literature_done = True
            else: cursor.reverse_done = True
        # A per-run page allowance is a fairness checkpoint, never a claim
        # that page 5 and later do not exist. ``run`` restores this cursor in
        # the next slice with its exact page cursor and retained RAM evidence.
        elif cursor.slice_pages >= budget.max_pages_per_person:
            cursor.deferred = True

    def _hydrate_frontier_profiles(self, side: _Side, cursor: _Cursor, budget: DeepBudget) -> None:
        """Batch profile hydration for already discovered frontier members."""
        selected = [cursor]
        selected.extend(item for item in side.current if not item.profile_done and len(selected) < 25)
        requested = [item.person_id for item in selected if item.person_id not in self._unverified_people]
        confirmations = self._refresh_profiles(requested, budget, force=False) if requested else {}
        for item in selected:
            if item.person_id in self._unverified_people or not confirmations.get(item.person_id, False):
                if "profile_not_found" not in item.incomplete:
                    item.incomplete.append("profile_not_found")
                item.literature_done = item.reverse_done = True
            item.profile_done = True
            self._record_node(item)

    def _step_cursor(self, side: _Side, cursor: _Cursor, budget: DeepBudget) -> bool:
        """Do one bounded remote page; return whether it met the other side."""
        if not cursor.profile_done:
            self._hydrate_frontier_profiles(side, cursor, budget)
            side.current.append(cursor)
            return False
        met = False
        if self.filters.genealogy and not cursor.historical_enqueued:
            cursor.historical_enqueued = True
            # These are only exact, independently audited fixed neighbours.
            # The neighbour is still fetched as a live public profile before
            # an overlay edge can enter a graph snapshot.
            for person_id in self._historical_neighbors(cursor.person_id):
                if person_id != cursor.person_id:
                    met = self._enqueue(side, person_id, cursor.depth + 1, budget) or met
        kind = cursor.next_kind
        if kind == "literature" and cursor.literature_done:
            kind = "reverse"
        if kind == "reverse" and cursor.reverse_done:
            kind = "literature"
        if kind == "literature" and not cursor.literature_done:
            size = self._literature_size(budget)
            hits, total, _ = self._fetch("literature", self.literature_query(cursor.person_id, self.filters), cursor.literature_page, budget, size=size)
            # A work returned for cursor C can be the last required shared work
            # for already-closed A and B. When A and B sit on opposing
            # frontiers, checking only C's own filtered neighbours misses the
            # newly completed bridge at ``min_shared > 1``.
            hit_people = set(self._work_people(hits))
            met = met or bool(hit_people.intersection(self.left.seen) and hit_people.intersection(self.right.seen))
            cursor.pages += 1
            cursor.slice_pages += 1
            self._page_done(cursor, total, cursor.literature_page, budget, "literature", page_size=size)
            cursor.literature_page += 1
            cursor.next_kind = "reverse"
        elif kind == "reverse" and not cursor.reverse_done:
            hits, total, _ = self._fetch("authors", f"advisors.record.$ref:{cursor.person_id}", cursor.reverse_page, budget)
            cursor.pages += 1
            cursor.slice_pages += 1
            for person_id in self._eligible_neighbors(cursor.person_id, budget):
                if person_id != cursor.person_id:
                    met = self._enqueue(side, person_id, cursor.depth + 1, budget) or met
            self._page_done(cursor, total, cursor.reverse_page, budget, "reverse")
            cursor.reverse_page += 1
            cursor.next_kind = "literature"
        if kind == "literature":
            for person_id in self._eligible_neighbors(cursor.person_id, budget):
                if person_id != cursor.person_id:
                    met = self._enqueue(side, person_id, cursor.depth + 1, budget) or met
        if cursor.deferred:
            side.deferred.append(cursor)
        elif cursor.literature_done and cursor.reverse_done:
            cursor.closed = not cursor.incomplete
        else:
            side.current.append(cursor)
        self._record_node(cursor)
        return met

    def _snapshot(self, budget: DeepBudget) -> tuple[dict[str, Any], Graph]:
        if self._materialized is None:
            snapshot = build_snapshot(self.connection, {"label": "Deep live INSPIRE retrieval", "description": "RAM-only bounded deep search."})
            from .historical import apply_historical
            snapshot = apply_historical(snapshot)
            snapshot = apply_identity_guard(snapshot, self.connection)
            self._exclude_unverified_people(snapshot)
            if len(snapshot["people"]) > budget.max_people:
                raise DeepSearchError("resource_limit", "The deep-search people ceiling was reached.")
            self._materialized = (snapshot, Graph(snapshot, self.filters))
        snapshot, graph = self._materialized
        if len(snapshot["people"]) > budget.max_people:
            raise DeepSearchError("resource_limit", "The deep-search people ceiling was reached.")
        # Keep audited historical and identity corrections when replacing the
        # generic pipeline coverage with this session's live page ledger.
        overlay_coverage = snapshot.get("coverage", {})
        coverage = self._coverage(snapshot)
        if isinstance(overlay_coverage, dict):
            for key, value in overlay_coverage.items():
                # ``identity_validation`` is live progress, rebuilt by
                # ``_coverage``. All other identity keys are guard/exclusion
                # audit evidence created during the cached materialization.
                if key.startswith("historical_") or (key.startswith("identity_") and key != "identity_validation"):
                    coverage[key] = value
        snapshot["coverage"] = coverage
        # The overlay version preceded the live coverage replacement. Hash the
        # final evidence and policy view so this version names exactly what the
        # returned Graph received.
        content = {key: value for key, value in snapshot.items() if key not in {"version", "created_at"}}
        snapshot["version"] = "sha256:" + hashlib.sha256(
            json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        ).hexdigest()
        # Graph takes a reference to this snapshot but snapshots its version at
        # construction. Updating that metadata is safe: graph incidence and
        # all identity-filtered evidence remain unchanged until invalidation.
        graph.version = snapshot["version"]
        return snapshot, graph

    def _exclude_unverified_people(self, snapshot: dict[str, Any]) -> None:
        """Keep raw records, but prevent unverified IDs from forming derived ties."""
        if not self._unverified_people:
            return
        blocked = set(self._unverified_people)
        works = snapshot.get("works")
        removed: list[dict[str, str]] = []
        if isinstance(works, list):
            for work in works:
                if not isinstance(work, dict) or not isinstance(work.get("authors"), list):
                    continue
                original = [str(author) for author in work["authors"]]
                rejected = [author for author in original if author in blocked]
                if not rejected:
                    continue
                work["authors"] = [author for author in original if author not in blocked]
                raw_count = work.get("author_count")
                prior = work.get("unresolved_count", 0)
                prior_count = prior if isinstance(prior, int) and not isinstance(prior, bool) else 0
                if isinstance(raw_count, int) and not isinstance(raw_count, bool):
                    work["unresolved_count"] = max(prior_count + len(rejected), raw_count - len(work["authors"]))
                for person_id in rejected:
                    removed.append({"work_id": str(work.get("id")), "person": person_id,
                                    "reason": self._unverified_people[person_id]})
        people = snapshot.get("people")
        if isinstance(people, list):
            snapshot["people"] = [person for person in people if not isinstance(person, dict) or str(person.get("id")) not in blocked]
        coverage = snapshot.get("coverage")
        if not isinstance(coverage, dict):
            coverage = {}
            snapshot["coverage"] = coverage
        if removed:
            previous = coverage.get("identity_unverified_profile_exclusions")
            rows = [item for item in previous if isinstance(item, dict)] if isinstance(previous, list) else []
            known = {(str(item.get("work_id")), str(item.get("person"))) for item in rows}
            for item in removed:
                marker = (item["work_id"], item["person"])
                if marker not in known:
                    rows.append(item); known.add(marker)
            coverage["identity_unverified_profile_exclusions"] = sorted(rows, key=lambda item: (item["work_id"], item["person"]))

    @staticmethod
    def _path_signature(paths: list[dict[str, Any]]) -> tuple[tuple[str, ...], ...]:
        return tuple(
            tuple(str(person.get("id")) for person in path.get("people", []) if isinstance(person, dict))
            for path in paths if isinstance(path, dict)
        )

    def _validate_candidate_paths(self, snapshot: dict[str, Any], graph: Graph,
                                  budget: DeepBudget) -> dict[str, Any] | None:
        """Require a current profile for every person in every returned route.

        Validation is resumable. A budget/cancellation exception leaves the
        pending index unchanged, and `_result` deliberately never manufactures
        a path from an unvalidated graph snapshot.
        """
        found = graph.find_paths(self.source, self.target, 3)
        if found.get("status") != "ok" or not found.get("paths"):
            self._pending_validation = None
            return None
        paths = found["paths"]
        signature = self._path_signature(paths)
        if not signature:
            self._pending_validation = None
            return None
        if self._pending_validation is None or self._pending_validation.signature != signature:
            people = tuple(dict.fromkeys(person_id for route in signature for person_id in route))
            self._pending_validation = _PendingValidation(signature, people)
        pending = self._pending_validation
        outstanding = [person_id for person_id in pending.people[pending.index:]
                       if person_id not in self._identity_confirmed]
        if outstanding:
            # Each batch call has an exact authoritative ID check. The index
            # advances only after the batch and any exact fallbacks complete.
            confirmations = self._refresh_profiles(outstanding, budget, force=True)
            for person_id in outstanding:
                if confirmations.get(person_id):
                    self._identity_confirmed.add(person_id)
                else:
                    self._unverified_people[person_id] = "current_public_profile_not_found"
                    self._invalidate_materialized()
                pending.index += 1
                self._emit("validate_identity")
        fresh_snapshot, fresh_graph = self._snapshot(budget)
        fresh = fresh_graph.find_paths(self.source, self.target, 3)
        fresh_paths = fresh.get("paths") if fresh.get("status") == "ok" else []
        fresh_signature = self._path_signature(fresh_paths if isinstance(fresh_paths, list) else [])
        self._reject_unproved_navigation_edges(fresh_graph, pending.signature)
        if not fresh_signature:
            self._pending_validation = None
            return None
        if fresh_signature != pending.signature:
            # A confirmed alias may have made the guard remove a shorter
            # route. Queue the already loaded replacement immediately; no
            # later frontier meeting is needed to make it eligible for return.
            people = tuple(dict.fromkeys(person_id for route in fresh_signature for person_id in route))
            self._pending_validation = _PendingValidation(fresh_signature, people)
            return None
        if not set(person_id for route in fresh_signature for person_id in route) <= self._identity_confirmed:
            people = tuple(dict.fromkeys(person_id for route in fresh_signature for person_id in route))
            self._pending_validation = _PendingValidation(fresh_signature, people)
            return None
        self._pending_validation = None
        # The pending marker is part of coverage. Rebuild it once settled so
        # the saved result version names the exact coverage returned to callers.
        final_snapshot, final_graph = self._snapshot(budget)
        final = final_graph.find_paths(self.source, self.target, 3)
        if self._path_signature(final.get("paths", []) if final.get("status") == "ok" else []) != fresh_signature:
            return None
        prior_hops = self._best_hops()
        self._remember_best(final_snapshot, final)
        current_hops = self._best_hops()
        # On continuation, do not pause again on the already reported route.
        # Keep its verified evidence while retained frontiers seek a shorter one.
        if prior_hops is not None and current_hops is not None and current_hops >= prior_hops:
            return None
        return final

    def _eligible_neighbors(self, person_id: str, budget: DeepBudget) -> tuple[str, ...]:
        """Use cumulative, locally filtered graph semantics for expansion."""
        snapshot, graph = self._snapshot(budget)
        return graph._neighbors(person_id)  # Graph owns roles, dates, caps, min_shared, and PhD rules.

    def _coverage(self, snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
        profiles = self.connection.execute("select count(*) from source_records where collection='authors' and deleted=0").fetchone()[0]
        return {"label": "Deep live INSPIRE retrieval", "complete": False,
                "description": "Only retrieved pages and explicitly recorded evidence are represented.",
                "retrieved": {"profiles": profiles, "works": self.works,
                              "people": len(snapshot["people"]) if snapshot else None},
                "requests": self.requests, "nodes": dict(self.node_ledger), "failures": list(self.failures),
                "guide_used": self.guide_used, "guide_candidates_verified": self.guide_verified,
                "navigation_suggestion_pairs": self.suggestion_pairs_configured,
                "coauthor_discovery": {**(self.navigator.coverage() if self.navigator else {'enabled': False}),
                                       'failures': list(self._navigation_failures)},
                "cross_frontier": {"attempts": sum(self._bridge_failures.values()) + len(self._bridge_queries_seen),
                                   "failures": list(self._bridge_failure_log),
                                   "disabled_this_run": self._bridge_disabled_this_run},
                "direct_pair": {"pages_checked": self._direct_pair_pages_checked,
                                "last_page": self._direct_pair_last_page,
                                "records_seen": self._direct_pair_records_seen,
                                "reported_total": self._direct_pair_total,
                                "reported_total_exact": self._direct_pair_total_exact,
                                "complete": self._direct_pair_complete},
                "identity_validation": {"confirmed_profiles": len(self._identity_confirmed),
                                        "pending": self._pending_validation is not None,
                                        "unverified_people": dict(self._unverified_people)}}

    def _remember_best(self, snapshot: dict[str, Any], found: dict[str, Any]) -> None:
        self.best = {"paths": found.get("paths", []),
                     "exact_for_retrieved_graph": bool(found.get("exact")),
                     "alternatives_truncated": bool(found.get("alternatives_truncated"))}
        self.best_version = str(snapshot.get("version", "live-deep-incomplete"))

    def _best_hops(self) -> int | None:
        if not self.best or not isinstance(self.best.get("paths"), list) or not self.best["paths"]:
            return None
        first = self.best["paths"][0]
        hops = first.get("hops") if isinstance(first, dict) else None
        return hops if isinstance(hops, int) and not isinstance(hops, bool) else None

    def _found_result(self, budget: DeepBudget, message: str) -> dict[str, Any]:
        """Retain a non-shortest verified path for explicit exact continuation."""
        hops = self._best_hops()
        return self._result("ok", budget, message=message, can_continue=bool(hops and hops > 2))

    @staticmethod
    def _queryable_paths(paths: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """All returned route IDs came from fresh public profiles or records."""
        result: list[dict[str, Any]] = []
        for path in paths:
            if not isinstance(path, dict):
                continue
            item = dict(path)
            if isinstance(path.get("people"), list):
                item["people"] = [{**person, "queryable": True} if isinstance(person, dict) else person
                                  for person in path["people"]]
            result.append(item)
        return result

    def _result(self, status: str, budget: DeepBudget, *, message: str = "", can_continue: bool = False) -> dict[str, Any]:
        snapshot: dict[str, Any] | None = None
        paths: list[dict[str, Any]] = list(self.best.get("paths", [])) if self.best else []
        local_exact = bool(self.best and self.best.get("exact_for_retrieved_graph"))
        alternatives_truncated = bool(self.best and self.best.get("alternatives_truncated"))
        try:
            # Never discover a route here: budget interruption during final
            # identity validation must not return an unverified candidate.
            snapshot, _ = self._snapshot(budget)
        except (DeepSearchError, GraphError) as error:
            if status == "ok":
                status, message = error.code, error.message
        if status == "ok" and not self.best:
            status = "search_incomplete"
            if not message:
                message = "A route still needs current public-profile validation."
        coverage = snapshot.get("coverage") if isinstance(snapshot, dict) and isinstance(snapshot.get("coverage"), dict) else self._coverage(snapshot)
        direct = bool(paths and paths[0].get("hops") in {0, 1})
        two_hop_proven = bool(paths and paths[0].get("hops") == 2 and self._direct_pair_complete)
        return {"status": status, "message": message, "mode": "live", "filters": self.filters.to_dict(),
                "paths": self._queryable_paths(paths), "exact": False, "exact_for_retrieved_graph": local_exact,
                "global_shortest_proven": direct or two_hop_proven, "alternatives_truncated": alternatives_truncated,
                "can_continue": can_continue, "version": snapshot.get("version", self.best_version or "live-deep-incomplete") if snapshot else (self.best_version or "live-deep-incomplete"),
                "coverage": coverage, "progress": {"people_explored": len(set(self.node_ledger) | (self.navigator.queried if self.navigator else set())), "works_retrieved": self.works,
                                                        "elapsed_seconds": round(time.monotonic() - self.started, 3),
                                                        "requests": self.requests}}

    def run(self, budget: DeepBudget | None = None) -> dict[str, Any]:
        self._check_owner()
        budget = budget or DeepBudget.standard()
        budget.validate()
        self._run_requests = 0
        self._guide_pairs_this_run = 0
        self._bridge_queries_this_run = 0
        self._bridge_disabled_this_run = False
        self._navigation_disabled = False
        self._run_deadline = time.monotonic() + float(budget.max_seconds)
        self._restore_deferred(self.left)
        self._restore_deferred(self.right)
        try:
            while True:
                if self.cancel.is_set():
                    self.last_status = "cancelled"
                    return self._result("cancelled", budget, message="The deep search was cancelled.")
                if self._pending_validation is not None:
                    snapshot, graph = self._snapshot(budget)
                    validated = self._validate_candidate_paths(snapshot, graph, budget)
                    if validated is not None:
                        return self._found_result(budget, "A live route passed current-profile and source-name checks.")
                    # A guard correction may have removed the candidate. Keep
                    # the retained frontiers moving rather than treating that
                    # correction as a path result or terminal failure.
                    continue
                if self.bootstrap:
                    # Do not advance a resumable cursor until its remote work
                    # completed. A request-slice boundary may occur exactly at
                    # this call, and the next run must retry the same stage.
                    stage = self.bootstrap[0]
                    if stage == "source_profile" and not self._profile(self.source, budget):
                        return self._result("not_found", budget, message="The source profile was not found.")
                    if stage == "target_profile" and not self._profile(self.target, budget):
                        return self._result("not_found", budget, message="The target profile was not found.")
                    if stage == "direct_pair" and self.source != self.target:
                        pair_size = self._literature_size(budget)
                        hits, total, total_exact = self._fetch(
                            "literature", self.pair_query(self.source, self.target, self.filters),
                            self._direct_pair_page, budget, size=pair_size,
                        )
                        self._direct_pair_pages_checked += 1
                        self._direct_pair_last_page = self._direct_pair_page
                        self._direct_pair_records_seen += len(hits)
                        if not total_exact:
                            self._direct_pair_total_exact = False
                        elif self._direct_pair_total is None:
                            self._direct_pair_total = total
                        elif self._direct_pair_total != total:
                            self._direct_pair_total_exact = False
                        snapshot, graph = self._snapshot(budget)
                        direct = graph.find_paths(self.source, self.target, 1)
                        if direct.get("status") == "ok" and direct.get("paths") and direct["paths"][0]["hops"] <= 1:
                            self._direct_pair_complete = True
                            self.bootstrap.popleft()
                            validated = self._validate_candidate_paths(snapshot, graph, budget)
                            if validated is not None:
                                return self._found_result(budget, "Direct live evidence passed current-profile and source-name checks.")
                            continue
                        # Do not treat page arithmetic as proof: a short page
                        # with a claimed total can otherwise skip unseen rows.
                        # Exact exhaustion requires every reported hit to have
                        # actually arrived across the retained page cursor.
                        if self._direct_pair_total_exact and self._direct_pair_total is not None and self._direct_pair_records_seen < self._direct_pair_total:
                            self._direct_pair_page += 1
                            self._emit(stage)
                            continue
                        if not self._direct_pair_total_exact and len(hits) >= pair_size:
                            self._direct_pair_page += 1
                            self._emit(stage)
                            continue
                        self._direct_pair_complete = bool(
                            self._direct_pair_total_exact
                            and self._direct_pair_total is not None
                            and self._direct_pair_records_seen == self._direct_pair_total
                        )
                        self.bootstrap.popleft()
                        self._emit(stage)
                        continue
                    self.bootstrap.popleft()
                    self._emit(stage)
                    continue
                if self.source == self.target:
                    snapshot, graph = self._snapshot(budget)
                    validated = self._validate_candidate_paths(snapshot, graph, budget)
                    if validated is not None:
                        return self._found_result(budget, "The same current public profile was confirmed.")
                    continue
                # Both endpoint summaries are cheap and often expose a common
                # coauthor. Check them before following a longer saved route.
                if (self.navigator is not None and not self._navigation_disabled
                        and not {self.source, self.target} <= self.navigator.queried
                        and self._navigation_step(budget)):
                    continue
                if self.guide_pairs:
                    if self._guide_pairs_this_run >= 24:
                        # Do not allow a stale guide to consume a whole run;
                        # leave the remaining corridor for a later slice.
                        self._emit("guide_pair_cap")
                    else:
                        left, right = self.guide_pairs[0]
                        pair = (left, right) if left < right else (right, left)
                        self.guide_pairs_requested.add(pair)
                        # Literature pair evidence proves coauthorship. An
                        # overlay PhD hop additionally requires both current
                        # public profiles, never a stale guide-only assertion.
                        left_profile = self._profile(left, budget)
                        right_profile = self._profile(right, budget)
                        if not left_profile or not right_profile:
                            self.guide_pairs.popleft()
                            self._emit("guide_profile_missing")
                            continue
                        pair_page = self._guide_pair_pages.get(pair, 1)
                        pair_size = self._literature_size(budget)
                        _, total, _ = self._fetch("literature", self.pair_query(left, right, self.filters), pair_page, budget, size=pair_size)
                        self._guide_pairs_this_run += 1
                        self.guide_verified += 1
                        snapshot, graph = self._snapshot(budget)
                        if graph._edge(left, right) is None and pair_page * pair_size < total:
                            self._guide_pair_pages[pair] = pair_page + 1
                        else:
                            self.guide_pairs.popleft()
                            if self.navigator is not None and graph._edge(left, right) is None:
                                self.navigator.reject_edge(left, right)
                        found = graph.find_paths(self.source, self.target, 1)
                        if found.get("status") == "ok":
                            validated = self._validate_candidate_paths(snapshot, graph, budget)
                            if validated is not None:
                                return self._found_result(budget, "A suggested route passed current-profile and source-name checks.")
                        self._emit("guide_verify")
                        continue
                # Explore compact summaries from both ends while retaining a
                # regular bibliography/genealogy expansion at least every
                # eight facet requests. Top-100 hints can never exhaust BFS.
                if self._navigation_since_expansion < 8 and self._navigation_step(budget):
                    continue
                if (not self.frontier_started and not self.left.current and not self.left.following
                        and not self.right.current and not self.right.following):
                    self.left.current.append(self._cursor(self.source, 0, profile_done=True))
                    self.right.current.append(self._cursor(self.target, 0, profile_done=True))
                    self.frontier_started = True
                if self._bridge_turn:
                    self._bridge_turn = False
                    if self._cross_frontier(budget):
                        snapshot, graph = self._snapshot(budget)
                        found = graph.find_paths(self.source, self.target, 3)
                        if found.get("status") == "ok":
                            validated = self._validate_candidate_paths(snapshot, graph, budget)
                            if validated is not None:
                                return self._found_result(budget, "A route joining both search sides passed current-profile and source-name checks.")
                        self._emit("cross_frontier")
                        continue
                self._advance(self.left); self._advance(self.right)
                available = [side for side in (self.left, self.right) if side.current]
                if not available:
                    if self.left.deferred or self.right.deferred:
                        # No known frontier work remains, so resume the exact
                        # saved page cursors in this same allowance. Page five
                        # is never silently abandoned just because page four
                        # was a fair per-person checkpoint.
                        self._restore_deferred(self.left)
                        self._restore_deferred(self.right)
                        continue
                    # This is also a final safety net for a repeated-work edge
                    # that formed between two already closed cursors. Normal
                    # graph/identity ordering remains exactly the same.
                    snapshot, graph = self._snapshot(budget)
                    found = graph.find_paths(self.source, self.target, 3)
                    found_hops = (found.get("paths") or [{}])[0].get("hops") if isinstance(found.get("paths"), list) and found.get("paths") else None
                    if found.get("status") == "ok" and (self._best_hops() is None or (isinstance(found_hops, int) and found_hops < self._best_hops())):
                        validated = self._validate_candidate_paths(snapshot, graph, budget)
                        if validated is not None:
                            return self._found_result(budget, "A route in the retrieved evidence passed current-profile and source-name checks.")
                    if self.best:
                        return self._result(
                            "ok", budget,
                            message="The retained bounded frontiers are exhausted; the verified route remains scoped to retrieved evidence.",
                        )
                    return self._result("search_incomplete", budget, message="All bounded frontiers were exhausted; unqueried INSPIRE records may still connect these people.")
                smallest = min(len(item.current) for item in available)
                candidates = [item for item in available if len(item.current) == smallest]
                if len(candidates) == 1:
                    side = candidates[0]
                else:
                    side = self.left if self._prefer_left else self.right
                    if side not in candidates:
                        side = candidates[0]
                    self._prefer_left = not self._prefer_left
                cursor = side.current.popleft()
                self._navigation_since_expansion = 0
                try:
                    met = self._step_cursor(side, cursor, budget)
                except DeepSearchError:
                    # A budget boundary or transient upstream error must leave
                    # the exact page cursor on its original breadth frontier.
                    # A successful page has already advanced its cursor before
                    # any later failure, so repeating it is safe and idempotent.
                    side.current.appendleft(cursor)
                    raise
                self._emit(f"expand_{side.name}")
                self._bridge_turn = True
                if met:
                    snapshot, graph = self._snapshot(budget)
                    found = graph.find_paths(self.source, self.target, 3)
                    if found.get("status") == "ok":
                        validated = self._validate_candidate_paths(snapshot, graph, budget)
                        if validated is not None:
                            return self._found_result(budget, "A multi-hop live route passed current-profile and source-name checks.")
        except DeepSearchError as error:
            self.last_status = error.code
            continuable = error.code in {"resource_limit", "search_incomplete", "upstream_unavailable"} and not self.cancel.is_set()
            return self._result(error.code, budget, message=error.message, can_continue=continuable)

    def close(self) -> None:
        self._check_owner()
        self.connection.close()
        self.closed = True
