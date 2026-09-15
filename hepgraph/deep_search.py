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
from .remote import MAX_RESPONSE_BYTES, OVERSIZE_MESSAGE
from .hlbes import (COMPLETE, EXACT, HLBES, NO_PATH, PARTIAL, UNKNOWN, Neighborhood,
                    OracleStopped, Search)
from .discovery import Navigator
from .identity_guard import apply_identity_guard
from .pipeline import PipelineError, build_snapshot, open_db, ref_id, store_record


# INSPIRE serves at most this many results per query, so a set larger than the
# window can be read from but never read to the end.
MAX_RESULT_WINDOW = 10_000

# INSPIRE's maximum accepted page size, measured against the live API.
MAX_LITERATURE_PAGE = 1_000
# Measured in docs/INSPIRE_NEIGHBORHOOD_API_AUDIT.md: a literature record costs
# roughly 700 bytes plus 175 per listed author. A page has to fit the 4 MiB
# transport bound with room to spare, so the safe page size falls out of the
# mode's author ceiling rather than from a flat threshold.
# A floor count must be read to an empty page, which has to land inside the
# result window; 100 keeps that reachable for every set the window can hold.
GTE_PAGE_SIZE = 100
# A page whose records cannot be interpreted will not become interpretable by
# being asked for again. Retry it a couple of times, then step past it with the
# neighbourhood honestly marked incomplete.
UNREADABLE_PAGE_MESSAGE = "A live record could not be safely interpreted."
MAX_PAGE_ATTEMPTS = 2
RECORD_BASE_BYTES = 700
RECORD_AUTHOR_BYTES = 175
PAGE_BUDGET_FRACTION = 0.5
# What an unbounded team size has to be assumed to cost.
ASSUMED_BROAD_AUTHORS = 3_000
# An exact-ID author lookup returns at most one record per requested ID, and
# profile batches are capped at 25, so a literature-sized page would only make
# the request (and its cache key) larger for nothing.
PROFILE_PAGE_SIZE = 25


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
    page_size: int = 1000
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
                               ("page_size", 1000), ("max_pages_per_person", 100)):
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
    # Fixed once paging starts: page N means different records at a different
    # size, so a mid-stream change would silently skip or repeat works.
    page_size: int = 0
    # Page arithmetic alone cannot prove a query was read to the end: an empty
    # or repeated page satisfies it while records are missing. Count the
    # distinct records that actually arrived, and stop trusting the reported
    # count if it ever moves.
    literature_seen: set[str] = field(default_factory=set)
    reverse_seen: set[str] = field(default_factory=set)
    literature_total: int | None = None
    reverse_total: int | None = None
    literature_stable: bool = True
    reverse_stable: bool = True
    literature_stable_total: bool = True
    # A transport retry is progress. Without this the oracle would see an
    # unchanged token twice and park the person for the rest of the search.
    shrinks: int = 0
    page_failures: int = 0

    literature_done: bool = False
    reverse_done: bool = False
    next_kind: str = "literature"
    pages: int = 0
    slice_pages: int = 0
    closed: bool = False
    deferred: bool = False
    historical_enqueued: bool = False
    incomplete: list[str] = field(default_factory=list)

    def literature_stable_window(self, window: int) -> bool:
        """False when this size cannot reach the empty page a floor count needs."""
        if self.literature_total is None or self.literature_stable_total:
            return True
        size = self.page_size or 1
        return (self.literature_total // size + 1) * size <= window



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
                 suggestion_pairs: Iterable[tuple[Any, Any]] = (),
                 core_nodes: Iterable[str] = (),
                 discovery_hints: bool = False) -> None:
        self.client = client
        self.guide_snapshot = guide_snapshot
        # Seed identities reorder equal-depth work and nothing else.
        self.core_nodes = frozenset(str(item) for item in core_nodes)
        # Facet discovery and cross-frontier bridging were written for the
        # previous engine, which had no systematic way to notice that its two
        # frontiers had met. HLBES rescans every node both sides know after
        # every expansion, so measured against it these two only spend
        # requests: on Witten -> Visser they were 55 of 94, and removing them
        # reached the same proven four-hop answer in 41 s instead of 85 s.
        # They are kept, and off, because a future oracle change could make
        # cheap hints worth having again.
        self.discovery_hints = bool(discovery_hints)
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
        return DeepSession(self.client, _id(source), _id(target), active_filters, self.guide_snapshot,
                           self.suggestion_pairs, cancel or threading.Event(), progress,
                           core_nodes=self.core_nodes, discovery_hints=self.discovery_hints)


class _EvidenceWithdrawn(Exception):
    """A retrieved page contradicted an exhaustion claim the proof rested on."""


class _LiveOracle:
    """DeepSession's paged retrieval, presented as an HLBES neighbourhood oracle.

    COMPLETE means every qualifying literature page (and, with genealogy on,
    every reverse-adviser page) for that person under the active mode has been
    retrieved, *and* that those pages account for every neighbour the
    cumulative evidence attributes to them.  A neighbour discovered only
    through somebody else's page means the person's own exhausted query
    disagrees with the index, so the neighbourhood stays PARTIAL and can never
    close a search layer.
    """

    def __init__(self, session: "DeepSession") -> None:
        self.session = session
        self.cursors: dict[str, _Cursor] = {}
        # Kept apart on purpose: only a person's own literature pages can
        # settle who their coauthors are. Reverse-adviser results name
        # students, and letting them answer the coauthor question would
        # silently retire the index-disagreement check.
        self.attested: dict[str, set[str]] = {}
        self.students: dict[str, set[str]] = {}
        self.complete: set[str] = set()
        self.reported: dict[str, frozenset[str]] = {}
        self.contradicted: set[str] = set()
        self.bridged_page = False
        self.genealogy_done: set[str] = set()

    def cursor_for(self, person_id: str, *, profile_done: bool = False) -> _Cursor:
        cursor = self.cursors.get(person_id)
        if cursor is None:
            cursor = self.cursors[person_id] = self.session._cursor(person_id, 0, profile_done=profile_done)
        return cursor

    def _companions(self, person_id: str) -> list[_Cursor]:
        """Hydrate the rest of the pending layer in the same batched request."""
        proof = self.session._proof
        if proof is None:
            return []
        pending = (proof.left.open_pending() | proof.right.open_pending()) - {person_id}
        return [self.cursor_for(other) for other in sorted(pending)[:24]]

    def _members(self, person_id: str) -> tuple[frozenset[str], frozenset[str]]:
        """This person's coauthor neighbours and their genealogy-only ones."""
        session = self.session
        _, graph = session._snapshot(session._budget)
        coauthors = frozenset(other for other in graph._coauthor_neighbors(person_id)
                              if other != person_id)
        everyone = frozenset(other for other in graph._neighbors(person_id)
                             if other != person_id)
        return coauthors, everyone - coauthors

    def _accounted(self, person_id: str) -> bool:
        """Every neighbour must be explained by a source this person exhausted.

        Coauthorship is settled by their own literature query.  A doctoral edge
        is settled by their public record's advisers plus the reverse student
        query, so it needs those two to be finished rather than a literature
        page that could never have carried it.
        """
        coauthors, genealogy = self._members(person_id)
        if not coauthors <= self.attested.get(person_id, set()):
            return False
        cursor = self.cursors.get(person_id)
        if genealogy and not (cursor is not None and cursor.profile_done and cursor.reverse_done):
            return False
        return True

    def _audit(self, touched: Iterable[str]) -> None:
        """A retrieved page can contradict an exhaustion claim made earlier.

        INSPIRE's index is not always self-consistent, so a neighbour that only
        ever appeared on somebody else's page withdraws the claim rather than
        quietly leaving a proof resting on it.
        """
        for person_id in touched:
            if person_id not in self.complete:
                continue
            coauthors, genealogy = self._members(person_id)
            # An exhausted neighbourhood must not move in either direction: a
            # pair can also cross ``min_shared`` on a work retrieved elsewhere.
            if coauthors | genealogy != self.reported.get(person_id) or not self._accounted(person_id):
                self.complete.discard(person_id)
                self.contradicted.add(person_id)

    def complete_still_holds(self) -> bool:
        return all(self._accounted(person_id) for person_id in sorted(self.complete))

    def withdrawn(self) -> bool:
        """True once the identity guard has removed adjacency already reported.

        A name or lifetime conflict is only detectable after the neighbour's
        public profile arrives, which can be several expansions later.  Bounds
        derived from the retracted edge describe a graph that no longer exists.
        """
        session = self.session
        for person_id, reported in self.reported.items():
            members = {other for other in session._eligible_neighbors(person_id, session._budget)
                       if other != person_id}
            if not reported <= members:
                return True
        return False

    def neighborhood(self, person_id: str) -> Neighborhood:
        session = self.session
        budget = session._budget
        cursor = self.cursor_for(person_id)
        try:
            if session.filters.genealogy and person_id not in self.genealogy_done:
                # An audited overlay edge still needs the neighbour's live
                # public profile before it can enter a graph snapshot. Mark
                # this done only once every one of them has arrived: a slice
                # boundary here would otherwise drop the overlay for good and
                # leave a neighbourhood that looks exhausted but is not.
                for other in session._historical_neighbors(person_id):
                    if other != person_id:
                        session._profile(other, budget)
                self.genealogy_done.add(person_id)
            attested = self.attested.setdefault(person_id, set())
            page_people, kind = session._page_person(cursor, budget, self._companions(person_id))
            if kind == "reverse":
                self.students.setdefault(person_id, set()).update(page_people)
            else:
                attested |= page_people
            self._audit(page_people - {person_id})
            proof = session._proof
            if proof is not None and page_people & set(proof.left.dist) and page_people & set(proof.right.dist):
                # This page may have completed an edge between two frontier
                # members that neither side has expanded, which no vertex
                # meeting can see. Ask the session to look for a route.
                self.bridged_page = True
            if self.contradicted:
                # Raise before any of this page reaches the proof: the bounds
                # were derived from a claim that no longer holds, so the whole
                # proof is rebuilt from the retained evidence instead.
                raise _EvidenceWithdrawn()
        except DeepSearchError as error:
            raise OracleStopped(error.code, error.message) from error
        if cursor.deferred:
            # A per-run page allowance is a fairness checkpoint for the old
            # round-robin frontier. HLBES already balances the two sides, and
            # a layer cannot close until this person is read to the end.
            cursor.deferred, cursor.slice_pages = False, 0
        members = frozenset(other for other in session._eligible_neighbors(person_id, budget)
                            if other != person_id)
        # Retrieval progress, not the member set: a page may legitimately add
        # no new qualifying neighbour and must not look like a dead end.
        token = (cursor.profile_done, cursor.pages, cursor.literature_page,
                 cursor.reverse_page, cursor.shrinks)
        self.reported[person_id] = members
        paged_out = cursor.literature_done and cursor.reverse_done and not cursor.incomplete
        if paged_out and self._accounted(person_id):
            self.complete.add(person_id)
            return Neighborhood(members, COMPLETE, token)
        self.complete.discard(person_id)
        return Neighborhood(members, PARTIAL if cursor.pages or members else UNKNOWN, token)


class DeepSession:
    """One in-memory search state. All methods must run on its creator thread."""

    def __init__(self, client: Any, source: str, target: str, filters: Filters,
                 guide_snapshot: dict[str, Any] | None, suggestion_pairs: tuple[tuple[str, str], ...], cancel: threading.Event,
                 progress: Callable[[dict[str, Any]], None] | None,
                 core_nodes: frozenset[str] = frozenset(),
                 discovery_hints: bool = False) -> None:
        self.client, self.source, self.target, self.filters = client, source, target, filters
        self.cancel, self.progress_callback = cancel, progress
        self.core_nodes = core_nodes
        self.discovery_hints = discovery_hints
        self.connection = open_db(":memory:")
        self.owner = threading.get_ident()
        self.started = time.monotonic()
        self.closed = False
        self.requests = 0
        self.works = 0
        # "Work records fetched" conflates a projected hit with a hydrated
        # record. Count the distinct things separately so a change that trades
        # one for the other is visible instead of hidden in one number.
        self.literature_pages = 0
        self.literature_hits = 0
        self.failures: list[dict[str, str]] = []
        self.node_ledger: dict[str, dict[str, Any]] = {}
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
        self._direct_pair_size = 0
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
        # HLBES owns traversal and the exactness proof; this session owns
        # retrieval, evidence, and identity. The proof state survives every
        # slice boundary so a continuation resumes rather than restarts.
        self._bridged: set[tuple[str, bool]] = set()
        self._rebuilds = 0
        # Starts from what this mode can afford and is only ever lowered, when
        # a real response turns out bigger than the estimate allowed for.
        self._page_ceiling = self.page_ceiling_for(filters)
        self._proof: Search | None = None
        self._engine: HLBES | None = None
        self._oracle: _LiveOracle | None = None
        self._budget: DeepBudget = DeepBudget.standard()
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

    def _queue_guide_bridge(self, person_id: str, *, discovered_from_source: bool) -> None:
        """Turn a stale guide corridor into bounded fresh pair verifications.

        A candidate is useful only when it was *just discovered* by a live
        frontier from the other endpoint.  Guide records themselves never enter
        the temporary SQLite database or any returned evidence.
        """
        guide_root = self.target if discovered_from_source else self.source
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
                                                        "literature_pages": self.literature_pages,
                                                        "literature_hits": self.literature_hits,
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
                raise DeepSearchError("search_incomplete", UNREADABLE_PAGE_MESSAGE) from error
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
        hits, _, _ = self._fetch("authors", f"control_number:{person_id}", 1, budget,
                                 size=PROFILE_PAGE_SIZE)
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
                                  size=max(PROFILE_PAGE_SIZE, len(chunk)))
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

    def _cross_frontier(self, budget: DeepBudget) -> bool:
        """Fetch one bounded cross-frontier coauthor page, if a new set exists."""
        if self._bridge_disabled_this_run or self._bridge_queries_this_run >= 12:
            return False
        # Keep batches deterministic, including for the public query audit.
        # Diagonal scheduling below, rather than member order, prevents one
        # side's early blocks from consuming an entire bounded slice.
        left_ids, right_ids = self._bridge_groups()
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
                self._fetch_literature(query, 1, budget, self._literature_size(budget))
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

    def _bridge_groups(self) -> tuple[list[str], list[str]]:
        """Both discovered sides, taken from whichever frontier is in charge."""
        left, right = ((self._proof.left.dist, self._proof.right.dist) if self._proof is not None
                       else ({self.source: 0}, {self.target: 0}))
        return (sorted(person_id for person_id in left if person_id not in self._unverified_people),
                sorted(person_id for person_id in right if person_id not in self._unverified_people))

    def _cursor(self, person_id: str, depth: int, *, profile_done: bool = False) -> _Cursor:
        return _Cursor(person_id, depth, profile_done=profile_done, reverse_done=not self.filters.genealogy)

    @staticmethod
    def page_ceiling_for(filters: Filters) -> int:
        """Largest page this mode can ask for and still fit the transport.

        A small-team record is about 1.8 KB and a large-team one about 414 KB,
        so the affordable page size is a function of the mode's author ceiling.
        Deriving it keeps the 11..100 band honest: it is neither "small" (a
        100-author page of 1000 would be 1.7 MiB per 100 records) nor as
        expensive as an unbounded collaboration.
        """
        authors = filters.max_authors if filters.max_authors is not None else ASSUMED_BROAD_AUTHORS
        per_record = RECORD_BASE_BYTES + RECORD_AUTHOR_BYTES * authors
        affordable = int(PAGE_BUDGET_FRACTION * MAX_RESPONSE_BYTES / max(per_record, 1))
        return max(5, min(MAX_LITERATURE_PAGE, affordable))

    def _literature_size(self, budget: DeepBudget) -> int:
        """Records per literature page, never above what this session survived."""
        return max(1, min(budget.page_size, self._page_ceiling))

    def _lower_page_ceiling(self) -> bool:
        """Drop the session's page size after a response the transport refused."""
        if self._page_ceiling <= 5:
            return False
        self._page_ceiling = max(5, self._page_ceiling // 4)
        self._emit("literature_page_shrink")
        return True

    def _fetch_literature(self, query: str, page: int, budget: DeepBudget,
                          size: int) -> tuple[list[dict[str, Any]], int, bool, int]:
        """Fetch one literature page, retrying smaller if it was too large.

        Every literature call needs this, not only per-person pagination: the
        endpoint-pair probe is the cheapest and most important query the
        product makes, and without a retry an oversized first page turns a
        one-hop answer into a permanent search_incomplete.
        """
        while True:
            try:
                hits, total, exact = self._fetch("literature", query, page, budget, size=size)
                return hits, total, exact, size
            except DeepSearchError as error:
                if error.message != OVERSIZE_MESSAGE or not self._lower_page_ceiling():
                    raise
                smaller = self._literature_size(budget)
                if smaller >= size:
                    raise
                # Page numbers only mean something against a fixed size, so a
                # caller that had advanced has to be told to start over.
                page, size = 1, smaller

    def _shrink_pages(self, cursor: _Cursor) -> bool:
        """Halve the page size after an oversized response and start over.

        Page numbers are only meaningful against a fixed size, so a cursor
        that changes size has to re-read from page one.  Every page it already
        read is still in the session cache, so this costs little.
        """
        if not self._lower_page_ceiling():
            return False
        cursor.shrinks += 1
        cursor.literature_page, cursor.page_size = 1, 0
        cursor.literature_done = False
        cursor.literature_seen, cursor.literature_total = set(), None
        cursor.literature_stable = True
        return True

    def _page_done(self, cursor: _Cursor, total: int, page: int, budget: DeepBudget, kind: str,
                   page_size: int | None = None, *, total_exact: bool = True,
                   returned: int = 0, arrived: Iterable[str] = ()) -> None:
        """Decide whether this query has been read to the end.

        Page arithmetic is not proof.  A page that comes back empty, or that
        repeats the one before it, satisfies ``page * size >= total`` while the
        records it should have carried are missing, and the neighbourhood built
        from it would then be certified COMPLETE with collaborators silently
        absent.  So exhaustion needs the distinct records to have actually
        arrived, and a reported count that moves mid-pagination is no longer
        something to do arithmetic against at all.

        This is the rule the endpoint-pair cursor has always used; the
        per-person cursor simply never had it.
        """
        size = page_size or budget.page_size
        literature = kind == "literature"
        seen = cursor.literature_seen if literature else cursor.reverse_seen
        seen.update(str(item) for item in arrived)
        if literature:
            cursor.literature_stable_total = total_exact
        known = cursor.literature_total if literature else cursor.reverse_total
        if known is None:
            if literature: cursor.literature_total = total
            else: cursor.reverse_total = total
        elif known != total:
            # The result set moved underneath the cursor.
            if literature: cursor.literature_stable = False
            else: cursor.reverse_stable = False
        stable = cursor.literature_stable if literature else cursor.reverse_stable

        if total_exact and stable:
            # Every reported record must have actually arrived, counted once.
            finished = len(seen) >= total and page * size >= total
        else:
            # INSPIRE reports ``{"value": n, "relation": "gte"}`` for large
            # result sets, and an unstable count is no better. Read on until a
            # page comes back empty: one extra request is a fair price for the
            # exhaustion claim the whole proof rests on.
            finished = returned == 0

        # INSPIRE serves at most MAX_RESULT_WINDOW results per query, so a set
        # larger than the window can be read from but never read to the end.
        exhausted_window = not finished and (page + 1) * size > MAX_RESULT_WINDOW
        if exhausted_window and f"{kind}_window" not in cursor.incomplete:
            cursor.incomplete.append(f"{kind}_window")
        if finished or exhausted_window:
            if literature: cursor.literature_done = True
            else: cursor.reverse_done = True
        # A per-run page allowance is a fairness checkpoint, never a claim
        # that page 5 and later do not exist. ``run`` restores this cursor in
        # the next slice with its exact page cursor and retained RAM evidence.
        elif cursor.slice_pages >= budget.max_pages_per_person:
            cursor.deferred = True

    def _hydrate_profiles(self, cursor: _Cursor, companions: Iterable[_Cursor],
                          budget: DeepBudget) -> None:
        """Batch profile hydration for already discovered frontier members."""
        selected = [cursor]
        selected.extend(item for item in companions if not item.profile_done and len(selected) < 25)
        requested = [item.person_id for item in selected if item.person_id not in self._unverified_people]
        confirmations = self._refresh_profiles(requested, budget, force=False) if requested else {}
        for item in selected:
            if item.person_id in self._unverified_people or not confirmations.get(item.person_id, False):
                if "profile_not_found" not in item.incomplete:
                    item.incomplete.append("profile_not_found")
                item.literature_done = item.reverse_done = True
            item.profile_done = True
            self._record_node(item)

    def _page_person(self, cursor: _Cursor, budget: DeepBudget,
                     companions: Iterable[_Cursor] = ()) -> tuple[set[str], str]:
        """One bounded remote page for one person, with no frontier bookkeeping.

        Returns the people named on the page and which query produced them, so
        a caller can tell coauthorship evidence from genealogy evidence.
        """
        if not cursor.profile_done:
            self._hydrate_profiles(cursor, companions, budget)
            return set(), "profile"
        kind = cursor.next_kind
        if kind == "literature" and cursor.literature_done:
            kind = "reverse"
        if kind == "reverse" and cursor.reverse_done:
            kind = "literature"
        people: set[str] = set()
        if kind == "literature" and not cursor.literature_done:
            if not cursor.page_size:
                cursor.page_size = self._literature_size(budget)
            if not cursor.literature_stable_window(MAX_RESULT_WINDOW):
                # A floor count is only exhausted by an empty page, and that
                # page has to fit inside the result window. A large page can
                # step straight over it, so fall back to one that cannot.
                cursor.page_size, cursor.literature_page = GTE_PAGE_SIZE, 1
                cursor.literature_seen, cursor.literature_total = set(), None
                cursor.literature_stable = True
                cursor.shrinks += 1
            size = cursor.page_size
            try:
                hits, total, total_exact = self._fetch(
                    "literature", self.literature_query(cursor.person_id, self.filters),
                    cursor.literature_page, budget, size=size)
            except DeepSearchError as error:
                # An oversized page is a transport limit, not an answer. The
                # code is rewritten to search_incomplete after the first
                # request of a run, so match the condition, not the code.
                if error.message == OVERSIZE_MESSAGE and self._shrink_pages(cursor):
                    return set(), "literature"
                if error.message == UNREADABLE_PAGE_MESSAGE:
                    cursor.page_failures += 1
                    if cursor.page_failures >= MAX_PAGE_ATTEMPTS:
                        # Step over it rather than spend every future slice on
                        # the same page. The person can never be COMPLETE now,
                        # so nothing downstream can mistake this for exhaustion.
                        if "literature_unreadable" not in cursor.incomplete:
                            cursor.incomplete.append("literature_unreadable")
                        cursor.literature_page += 1
                        cursor.page_failures = 0
                        cursor.shrinks += 1
                        self._emit("literature_page_skipped")
                raise
            people = set(self._work_people(hits))
            self.literature_pages += 1
            self.literature_hits += len(hits)
            cursor.pages += 1
            cursor.slice_pages += 1
            self._page_done(cursor, total, cursor.literature_page, budget, "literature", page_size=size,
                            total_exact=total_exact, returned=len(hits),
                            arrived=(hit.get("id") for hit in hits))
            cursor.literature_page += 1
            cursor.next_kind = "reverse"
        elif kind == "reverse" and not cursor.reverse_done:
            hits, total, total_exact = self._fetch(
                "authors", f"advisors.record.$ref:{cursor.person_id}", cursor.reverse_page, budget)
            people = set(self._profile_people(hits))
            cursor.pages += 1
            cursor.slice_pages += 1
            self._page_done(cursor, total, cursor.reverse_page, budget, "reverse",
                            total_exact=total_exact, returned=len(hits),
                            arrived=(hit.get("id") for hit in hits))
            cursor.reverse_page += 1
            cursor.next_kind = "literature"
        self._record_node(cursor)
        return people, kind

    def _routing_score(self, person_id: str) -> float:
        """Order equal-depth work only. This can never change a distance."""
        cursor = self._oracle.cursors.get(person_id) if self._oracle else None
        cached = 1.0 if cursor is not None and cursor.pages else 0.0
        hinted = 1.0 if person_id in self.suggestion_neighbors else 0.0
        seeded = 0.5 if person_id in self.core_nodes else 0.0
        facets = len(self.navigator.adjacency.get(person_id, ())) if self.navigator is not None else 0
        return cached + hinted + seeded + min(float(facets), 500.0) / 500.0

    def _pages_fetched(self, person_id: str) -> int:
        cursor = self._oracle.cursors.get(person_id) if self._oracle else None
        return cursor.pages if cursor is not None else 0

    def _retrieval_cost(self, person_id: str) -> float:
        """Estimated remaining upstream pages for this person."""
        cursor = self._oracle.cursors.get(person_id) if self._oracle else None
        if cursor is None:
            return 4.0
        remaining = 0.0 if cursor.literature_done else 2.0
        remaining += 0.0 if cursor.reverse_done else 1.0
        return remaining if cursor.profile_done else remaining + 1.0

    def _cached_trial_path(self, graph: Graph) -> list[str] | None:
        """A route in already-retrieved evidence: an upper bound, never a proof."""
        found = graph.find_paths(self.source, self.target, 1)
        if found.get("status") != "ok" or not found.get("paths"):
            return None
        return [str(person["id"]) for person in found["paths"][0].get("people", [])]

    def _retained_route(self) -> list[str] | None:
        paths = (self.best or {}).get("paths") or []
        people = paths[0].get("people") if paths and isinstance(paths[0], dict) else None
        if not isinstance(people, list) or len(people) < 2:
            return None
        return [str(person["id"]) for person in people]

    def _drop_retracted_best(self, graph: Graph) -> None:
        """Forget a retained route whose evidence the guard has since removed.

        ``best`` was validated when it was remembered, and a rebuild happens
        precisely because the evidence moved underneath it.  A route whose hops
        are no longer in the guarded graph must not be re-seeded as a bound,
        and must not be returned citing records the snapshot now excludes.
        """
        route = self._retained_route()
        if route is None:
            return
        if any(graph._edge(left, right) is None for left, right in zip(route, route[1:])):
            self.best, self.best_version = None, None
            self._emit("retained_route_retracted")

    def _validated_route(self, graph: Graph) -> list[str] | None:
        """The retained route, if identity validation and evidence both hold.

        A bound is only as trustworthy as the evidence under it, so a proof is
        never seeded from a graph route that identity validation has not yet
        seen, nor from one whose hops have since been withdrawn.
        """
        self._drop_retracted_best(graph)
        return self._retained_route()

    def _offer_cached_route(self, budget: DeepBudget) -> None:
        """Hand the proof any route the retrieved evidence already supports."""
        _, graph = self._snapshot(budget)
        route = self._cached_trial_path(graph)
        if route is not None and self._proof is not None and self._engine is not None:
            self._engine.offer(self._proof, route)

    MAX_REBUILDS = 32

    def _rebuild_proof(self, reason: str) -> bool:
        """Discard a proof built on evidence that changed. Bounded on purpose.

        Each rebuild is triggered by new evidence, so they cannot continue
        indefinitely in practice; the ceiling is there so that a pathological
        upstream cannot turn a search into a rebuild loop.
        """
        self._proof = None
        self._rebuilds += 1
        self._emit(reason)
        return self._rebuilds <= self.MAX_REBUILDS

    def _begin_proof(self, budget: DeepBudget) -> None:
        self._budget = budget
        _, graph = self._snapshot(budget)
        # A rebuilt proof keeps the existing oracle: every page cursor and
        # attested neighbour survives, so a restart repeats no request.
        if self._oracle is None:
            self._oracle = _LiveOracle(self)
            # Bootstrap already confirmed both endpoint profiles.
            self._oracle.cursor_for(self.source, profile_done=True)
            self._oracle.cursor_for(self.target, profile_done=True)
        self._engine = HLBES(self._oracle, routing_score=self._routing_score,
                             cost_estimate=self._retrieval_cost,
                             pages_fetched=self._pages_fetched)
        self._proof = self._engine.begin(self.source, self.target,
                                         trial_path=self._validated_route(graph))
        self._emit("hlbes_begin")

    def _harvest(self, budget: DeepBudget, message: str) -> dict[str, Any] | None:
        """Turn retrieved evidence into a validated, returnable route."""
        snapshot, graph = self._snapshot(budget)
        found = graph.find_paths(self.source, self.target, 3)
        if found.get("status") != "ok":
            return None
        hops = (found.get("paths") or [{}])[0].get("hops")
        best = self._best_hops()
        if best is not None and isinstance(hops, int) and hops >= best and not self._proven():
            return None
        if self._validate_candidate_paths(snapshot, graph, budget) is None:
            return None
        return self._found_result(budget, message)

    def _register_discoveries(self, budget: DeepBudget) -> None:
        """Apply the people ceiling and the guide corridor to new discoveries."""
        if self._proof is None:
            return
        left, right = self._proof.left.dist, self._proof.right.dist
        if len(set(left) | set(right)) > budget.max_people:
            raise DeepSearchError("resource_limit", "The deep-search people ceiling was reached.")
        for known, from_source in ((left, True), (right, False)):
            for person_id in sorted(known):
                if (person_id, from_source) in self._bridged:
                    continue
                self._bridged.add((person_id, from_source))
                self._queue_guide_bridge(person_id, discovered_from_source=from_source)

    def _retire_proof(self, person_id: str) -> None:
        """Rebuild the proof when the identity guard removes one of its nodes.

        Distances and bounds recorded against a graph that contained this
        person no longer describe the graph without them.  Retained evidence
        and page cursors survive, so the rebuild costs no upstream requests
        beyond the pages that were still outstanding anyway.
        """
        if self._proof is None or self._engine is None:
            return
        if person_id not in self._proof.left.dist and person_id not in self._proof.right.dist:
            return
        if self._oracle is not None:
            self._oracle.cursors.pop(person_id, None)
            self._oracle.attested.pop(person_id, None)
            self._oracle.complete.discard(person_id)
            self._oracle.reported.pop(person_id, None)
        self._rebuild_proof("hlbes_retire")

    def _traversed_a_component(self) -> bool:
        """Exhausting a component we never saw any evidence for proves nothing."""
        if self._proof is None or not self.works or self._oracle is None:
            return False
        if not any(len(side.dist) > 1 and side.complete
                   for side in (self._proof.left, self._proof.right)):
            return False
        return self._oracle.complete_still_holds()

    def _hunting(self) -> bool:
        """True while no route is known at all.

        The facet navigator and the cross-frontier bridge exist to stumble onto
        a first route.  HLBES scans every node both sides know after every
        expansion, so once an upper bound exists those two find nothing the
        search would not find anyway, and each one costs a request that could
        have gone into closing the bound.  Measured on Witten -> Visser: the
        same proven four-hop answer in 36 s and 39 requests instead of 85 s and
        94, with both running on their old fixed cadence.
        """
        return self._proof is None or self._proof.upper == float("inf")

    def _proven(self) -> bool:
        return self._proof is not None and self._proof.done == EXACT

    def _bounds(self) -> dict[str, Any]:
        if self._proof is None:
            return {"lower": None, "upper": None, "proven": False}
        upper = self._proof.upper
        return {"lower": self._proof.lower,
                "upper": None if upper == float("inf") else int(upper),
                "proven": self._proof.done == EXACT,
                "source_radius": self._proof.left.radius,
                "target_radius": self._proof.right.radius,
                "complete_neighborhoods": len(self._proof.left.complete) + len(self._proof.right.complete),
                "expansions": self._proof.expansions}

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
                    self._retire_proof(person_id)
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
                              "literature_pages": self.literature_pages,
                              "literature_hits": self.literature_hits,
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
                "exact_proof": self._bounds(),
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
        if self._proof is not None:
            # Offer continuation exactly while shortestness is still open.
            return self._result("ok", budget, message=message,
                                can_continue=self._proof.done is None)
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
            snapshot, graph = self._snapshot(budget)
            self._drop_retracted_best(graph)
            paths = list(self.best.get("paths", [])) if self.best else []
            local_exact = bool(self.best and self.best.get("exact_for_retrieved_graph"))
            alternatives_truncated = bool(self.best and self.best.get("alternatives_truncated"))
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
        bounds = self._bounds()
        return {"status": status, "message": message, "mode": "live", "filters": self.filters.to_dict(),
                "paths": self._queryable_paths(paths), "exact": False, "exact_for_retrieved_graph": local_exact,
                "global_shortest_proven": direct or two_hop_proven or (
                    # Only call a route proven when the route being returned is
                    # the one the bounds closed on.
                    bounds["proven"] and bool(paths) and paths[0].get("hops") == bounds["upper"]),
                "bounds": bounds, "alternatives_truncated": alternatives_truncated,
                "can_continue": can_continue, "version": snapshot.get("version", self.best_version or "live-deep-incomplete") if snapshot else (self.best_version or "live-deep-incomplete"),
                "coverage": coverage, "progress": {"people_explored": len(set(self.node_ledger) | (self.navigator.queried if self.navigator else set())), "works_retrieved": self.works,
                                                        "literature_pages": self.literature_pages,
                                                        "literature_hits": self.literature_hits,
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
        self._budget = budget
        try:
            while True:
                if self.cancel.is_set():
                    self.last_status = "cancelled"
                    return self._result("cancelled", budget, message="The deep search was cancelled.")
                if time.monotonic() >= self._run_deadline:
                    # Requests are individually bounded, but local work between
                    # them is not. Bound the loop itself so no combination of
                    # rebuilds and cached expansions can outrun the allowance.
                    raise DeepSearchError("resource_limit", "This deep-search slice reached its time allowance.")
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
                        if self._direct_pair_size and self._direct_pair_size != pair_size:
                            # Page N means different records at a different
                            # size, so the accumulated ledger no longer
                            # describes this pagination.
                            self._direct_pair_page, self._direct_pair_records_seen = 1, 0
                            self._direct_pair_total, self._direct_pair_total_exact = None, True
                        hits, total, total_exact, pair_size = self._fetch_literature(
                            self.pair_query(self.source, self.target, self.filters),
                            self._direct_pair_page, budget, pair_size)
                        if self._direct_pair_size and self._direct_pair_size != pair_size:
                            self._direct_pair_page, self._direct_pair_records_seen = 1, 0
                            self._direct_pair_total, self._direct_pair_total_exact = None, True
                        self._direct_pair_size = pair_size
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
                if (self.discovery_hints and self.navigator is not None and not self._navigation_disabled
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
                        _, total, _, pair_size = self._fetch_literature(
                            self.pair_query(left, right, self.filters), pair_page, budget, pair_size)
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
                if (self.discovery_hints and self._hunting()
                        and self._navigation_since_expansion < 8
                        and self._navigation_step(budget)):
                    continue
                if self._proof is None:
                    self._begin_proof(budget)
                    continue
                if self._bridge_turn:
                    self._bridge_turn = False
                    if self._cross_frontier(budget):
                        result = self._harvest(budget, "A route joining both search sides passed current-profile and source-name checks.")
                        if result is not None:
                            return result
                        self._emit("cross_frontier")
                        continue
                before = self._proof.upper
                try:
                    running = self._engine.advance(self._proof)
                except _EvidenceWithdrawn:
                    # Every retrieved page and page cursor survives, so the
                    # rebuild repeats no upstream request.
                    self._oracle.contradicted.clear()
                    if not self._rebuild_proof("hlbes_restart"):
                        raise DeepSearchError("search_incomplete",
                                              "Live records kept changing under this proof.")
                    continue
                if not running and self._proof.done is None:
                    # The proof paused rather than finished: report it through
                    # the session's own resumable error plumbing.
                    raise DeepSearchError(self._proof.reason or "search_incomplete",
                                          self._proof.stop_message or "The deep search paused before proving shortestness.")
                if self._oracle.bridged_page:
                    self._oracle.bridged_page = False
                    self._offer_cached_route(budget)
                if self._proof.conflict:
                    if not self._rebuild_proof("hlbes_restart"):
                        raise DeepSearchError("search_incomplete",
                                              "Live records kept changing under this proof.")
                    continue
                self._register_discoveries(budget)
                self._emit("hlbes_expand")
                self._bridge_turn = self.discovery_hints and self._hunting()
                if self._proof.upper < before or self._proof.done is not None:
                    if self._oracle.withdrawn():
                        self._oracle.reported.clear()
                        self._oracle.complete.clear()
                        if not self._rebuild_proof("hlbes_restart"):
                            raise DeepSearchError("search_incomplete",
                                                  "Live records kept changing under this proof.")
                        continue
                    result = self._harvest(budget, "A live route passed current-profile and source-name checks.")
                    if result is not None:
                        return result
                    if self._proof is None:
                        # Identity validation retired the proof while building
                        # the result. Rebuild it rather than read a dead one.
                        continue
                if running:
                    continue
                if self._proof.done == NO_PATH and self._traversed_a_component():
                    return self._result("no_path", budget, message=(
                        "Every reachable collaborator of one endpoint was retrieved in full and "
                        "none of them reaches the other person under these filters."))
                if self.best:
                    return self._result(
                        "ok", budget,
                        message="The retained bounded frontiers are exhausted; the verified route remains scoped to retrieved evidence.")
                return self._result("search_incomplete", budget,
                                    message="All bounded frontiers were exhausted; unqueried INSPIRE records may still connect these people.")
        except DeepSearchError as error:
            self.last_status = error.code
            continuable = error.code in {"resource_limit", "search_incomplete", "upstream_unavailable"} and not self.cancel.is_set()
            return self._result(error.code, budget, message=error.message, can_continue=continuable)

    def close(self) -> None:
        self._check_owner()
        self.connection.close()
        self.closed = True
