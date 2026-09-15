"""HLBES - Hub-guided Lazy Bidirectional Exact Search.

One authoritative, transport-free shortest-path engine.  It knows nothing
about INSPIRE: every remote fact arrives through a :class:`NeighborhoodOracle`,
so the exactness proof can be tested against NetworkX on synthetic graphs and
reused unchanged by the live adapter.

Exactness rests on one invariant.  For each side let ``R`` be its *completed
radius*: every node whose true distance from that root is at most ``R`` is
known, with its exact distance.  ``R`` advances from ``r`` to ``r + 1`` only
once every node at recorded distance ``r`` has been expanded through a
COMPLETE neighborhood, so a PARTIAL neighborhood can lower ``U`` but can never
raise ``L``.

Let ``U`` be the length of the shortest verified route seen so far.  Any s-t
path of length ``k <= Rs + Rt`` contains a vertex ``v`` at distance at most
``Rs`` from the source and at most ``Rt`` from the target; both sides
therefore know ``v`` with exact distances, and the meeting scan has already
recorded ``U <= k``.  Contrapositively, ``U > Rs + Rt`` proves no such path
exists, so ``d(s, t) >= Rs + Rt + 1``.  Together with ``d(s, t) <= U`` that
gives the rigorous lower bound

    L = min(U, Rs + Rt + 1)

and exactness follows in both of the ways ``L`` can meet ``U``:

    U <= Rs + Rt      =>  U <= d <= U           (a shorter path would have met)
    U == Rs + Rt + 1  =>  L <= d <= U == L      (nothing shorter can exist)

so the stopping rule is ``L == U``, that is ``U <= Rs + Rt + 1``.  Stopping at
``U <= Rs + Rt`` instead would be sound but would pay for one whole extra
layer of remote expansion.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Protocol

UNKNOWN, PARTIAL, COMPLETE = "unknown", "partial", "complete"
_STATUSES = (UNKNOWN, PARTIAL, COMPLETE)

EXACT, VERIFIED, NO_PATH, SEARCH_INCOMPLETE = "exact", "verified", "no_path", "search_incomplete"


class OracleStopped(Exception):
    """The oracle cannot continue: timeout, rate limit, cancellation, budget."""

    def __init__(self, reason: str = "search_incomplete", message: str = "") -> None:
        super().__init__(message or reason)
        self.reason, self.message = reason, message or reason


@dataclass(frozen=True)
class Neighborhood:
    """Adjacency known for one node, plus how much of it is proven."""

    members: frozenset[str]
    status: str = UNKNOWN
    #: Opaque progress marker. Two consecutive calls returning the same token
    #: tell the engine that no further discovery is available for this node.
    #: A paging oracle should advance it on every retrieved page, because a
    #: page can legitimately add no new qualifying neighbour.
    token: Any = None

    def __post_init__(self) -> None:
        if self.status not in _STATUSES:
            raise ValueError(f"neighborhood status must be one of {_STATUSES}")

    @property
    def key(self) -> tuple[Any, ...]:
        return self.status, len(self.members), hash(self.members), self.token


class NeighborhoodOracle(Protocol):
    def neighborhood(self, node: str) -> Neighborhood:
        """Do the next available unit of discovery for ``node`` and return it.

        Repeated calls must converge: returning the same members and status
        twice tells the engine no further progress is available for that node.
        Raise :class:`OracleStopped` when no work of any kind can continue.
        """


@dataclass(frozen=True)
class SearchResult:
    status: str
    distance: int | None
    path: tuple[str, ...] | None
    lower_bound: int
    upper_bound: float
    reason: str = ""
    stats: dict[str, Any] = field(default_factory=dict)

    @property
    def proven_shortest(self) -> bool:
        return self.status == EXACT


@dataclass
class _Side:
    name: str
    root: str
    dist: dict[str, int] = field(default_factory=dict)
    parent: dict[str, str | None] = field(default_factory=dict)
    levels: dict[int, set[str]] = field(default_factory=dict)
    radius: int = 0
    complete: set[str] = field(default_factory=set)
    blocked: set[str] = field(default_factory=set)
    seen_key: dict[str, tuple[str, int, int]] = field(default_factory=dict)
    expansions: int = 0

    def add(self, node: str, distance: int, parent: str | None) -> bool:
        known = self.dist.get(node)
        if known is not None and known <= distance:
            return False
        if known is not None:
            self.levels.get(known, set()).discard(node)
        self.dist[node], self.parent[node] = distance, parent
        self.levels.setdefault(distance, set()).add(node)
        return True

    def pending(self) -> set[str]:
        """Nodes at the completed radius still owing a COMPLETE expansion."""
        return {node for node in self.levels.get(self.radius, ()) if node not in self.complete}

    def open_pending(self) -> set[str]:
        return self.pending() - self.blocked

    def trace(self, node: str) -> list[str]:
        route, guard = [], 0
        while node is not None and guard <= len(self.dist) + 1:
            route.append(node)
            node, guard = self.parent.get(node), guard + 1
        return route


class Search:
    """One resumable HLBES proof. Drive it with :meth:`HLBES.advance`."""

    def __init__(self, source: str, target: str) -> None:
        self.source, self.target = source, target
        self.left, self.right = _Side("source", source), _Side("target", target)
        self.left.add(source, 0, None)
        self.right.add(target, 0, None)
        self.upper: float = float("inf")
        self.lower = 0
        self.best: tuple[str, ...] | None = None
        self.bounds: list[tuple[int, float]] = []
        self.meetings = 0
        self.done: str | None = None
        self.reason = ""
        #: True once no completed radius can advance: U may still fall, L cannot.
        self.stalled = False
        self.stop_message = ""
        #: Set when an offered route is shorter than the proven lower bound,
        #: which means this state was built on evidence that no longer holds.
        self.conflict = False
        self.expansions = 0

    @property
    def radius_sum(self) -> int:
        return self.left.radius + self.right.radius


class HLBES:
    """Exact unweighted shortest distance over a lazily revealed graph."""

    def __init__(self, oracle: NeighborhoodOracle, *,
                 routing_score: Callable[[str], float] | None = None,
                 cost_estimate: Callable[[str], float] | None = None,
                 max_expansions: int | None = None,
                 observer: Callable[[dict[str, Any]], None] | None = None) -> None:
        self.oracle = oracle
        self.routing_score = routing_score or (lambda node: 0.0)
        self.cost_estimate = cost_estimate or (lambda node: 1.0)
        self.max_expansions = max_expansions
        self.observer = observer

    # ---------------------------------------------------------------- driving
    def begin(self, source: str, target: str, *,
              trial_path: Iterable[str] | None = None) -> Search:
        state = Search(source, target)
        if source == target:
            state.upper, state.best, state.lower = 0, (source,), 0
            state.done = EXACT
        else:
            self._seed(state, trial_path)
        self._record(state)
        return state

    def advance(self, state: Search) -> bool:
        """Do one unit of work. Returns False once the search is finished."""
        if state.done is not None:
            return False
        if state.upper <= state.radius_sum + 1:
            return self._settle(state, EXACT)
        side, other, node = self._choose(state)
        if side is None:
            # The completed radius cannot move, so the proof is finished; keep
            # discovering past it, which can only lower U and never raise L.
            side, other, node = self._discover(state)
            state.stalled = True
        if side is None:
            if self._exhausted(state.left) or self._exhausted(state.right):
                return self._settle(state, EXACT if state.best is not None else NO_PATH)
            return self._settle(state, VERIFIED if state.best else SEARCH_INCOMPLETE,
                                state.reason or "adjacency_incomplete")
        if self.max_expansions is not None and state.expansions >= self.max_expansions:
            return self._pause(state, "expansion_limit")
        try:
            self._expand(state, side, other, node)
        except OracleStopped as stop:
            # A timeout, rate limit or slice boundary is not an answer. Leave
            # the proof resumable so a continuation picks it up unchanged.
            return self._pause(state, stop.reason, stop.message)
        self._record(state)
        return True

    def offer(self, state: Search, route: Iterable[str]) -> bool:
        """Accept an externally verified route as an upper bound only.

        A caller that can see an edge the oracle has not yet attributed to
        either endpoint - a crossing edge between two unexpanded frontier
        members, or a cheap shortcut across a known route - may hand it over
        here.  It can only lower U; it never advances a completed radius.
        """
        path = tuple(str(node) for node in route)
        if len(path) < 2 or len(set(path)) != len(path):
            return False
        if path[0] != state.source or path[-1] != state.target:
            return False
        if len(path) - 1 >= state.upper:
            return False
        if len(path) - 1 < state.lower:
            # A verified route shorter than the proven minimum means the proof
            # rests on adjacency that has since changed. Refuse it and say so.
            state.conflict = True
            return False
        state.upper, state.best = len(path) - 1, path
        self._record(state)
        return True

    def search(self, source: str, target: str, *,
               trial_path: Iterable[str] | None = None) -> SearchResult:
        state = self.begin(source, target, trial_path=trial_path)
        while self.advance(state):
            pass
        return self.result(state)

    # ------------------------------------------------------------- mechanics
    @staticmethod
    def _seed(state: Search, trial_path: Iterable[str] | None) -> None:
        """Adopt a caller-verified route purely as an upper bound."""
        if trial_path is None:
            return
        route = tuple(str(node) for node in trial_path)
        if len(route) < 2 or len(set(route)) != len(route):
            return
        if len(route) - 1 < state.upper:
            state.upper, state.best = len(route) - 1, route

    def _choose(self, state: Search) -> tuple[_Side | None, _Side | None, str | None]:
        """Pick the cheaper side that can legally advance its completed radius."""
        options = []
        for side, other in ((state.left, state.right), (state.right, state.left)):
            work = side.open_pending()
            if work:
                # Distance is primary: every candidate here already sits at the
                # same completed radius, so routing utility only breaks that tie.
                node = max(sorted(work), key=self.routing_score)
                options.append((min(self.cost_estimate(item) for item in work), side.name, side, other, node))
        if not options:
            return None, None, None
        best = min(options)
        return best[2], best[3], best[4]

    def _discover(self, state: Search) -> tuple[_Side | None, _Side | None, str | None]:
        """Expand past a stalled radius, shallowest first. This only lowers U."""
        best = None
        for side, other in ((state.left, state.right), (state.right, state.left)):
            for node in sorted(side.dist):
                if node in side.complete or node in side.blocked:
                    continue
                key = (side.dist[node], self.cost_estimate(node), -self.routing_score(node),
                       side.name, node)
                if best is None or key < best[0]:
                    best = (key, side, other, node)
        return (best[1], best[2], best[3]) if best else (None, None, None)

    def _expand(self, state: Search, side: _Side, other: _Side, node: str) -> None:
        found = self.oracle.neighborhood(node)
        side.expansions += 1
        state.expansions += 1
        previous, side.seen_key[node] = side.seen_key.get(node), found.key
        depth = side.dist[node]
        for neighbor in found.members:
            if neighbor != node:
                side.add(neighbor, depth + 1, node)
        if found.status == COMPLETE:
            side.complete.add(node)
            side.blocked.discard(node)
        elif previous == found.key:
            # No further progress is available for this node, so it can never
            # certify a completed layer. Park it instead of spinning.
            side.blocked.add(node)
        self._scan(state, side, other)
        if not side.pending():
            side.radius += 1

    def _scan(self, state: Search, side: _Side, other: _Side) -> None:
        """Every node both sides know is a candidate meeting."""
        near, far = ((side.dist, other.dist) if len(side.dist) <= len(other.dist)
                     else (other.dist, side.dist))
        for node, distance in near.items():
            opposite = far.get(node)
            if opposite is None:
                continue
            state.meetings += 1
            total = distance + opposite
            if total < state.upper:
                state.upper, state.best = total, self._join(node, side, other)

    @staticmethod
    def _join(node: str, side: _Side, other: _Side) -> tuple[str, ...]:
        left, right = (side, other) if side.name == "source" else (other, side)
        head, tail = left.trace(node), right.trace(node)
        route = tuple(reversed(head)) + tuple(tail[1:])
        return route if len(set(route)) == len(route) else HLBES._simplify(route)

    @staticmethod
    def _simplify(route: tuple[str, ...]) -> tuple[str, ...]:
        """A walk proves at most its own length; shortcutting only shortens it."""
        seen: dict[str, int] = {}
        out: list[str] = []
        for node in route:
            if node in seen:
                del out[seen[node] + 1:]
                seen = {name: index for index, name in enumerate(out)}
                continue
            seen[node] = len(out)
            out.append(node)
        return tuple(out)

    @staticmethod
    def _exhausted(side: _Side) -> bool:
        """The whole reachable component is known through COMPLETE adjacency."""
        return not side.blocked and all(node in side.complete for node in side.dist)

    def _record(self, state: Search) -> None:
        lower = min(state.upper, state.radius_sum + 1)
        lower = int(lower) if lower != float("inf") else state.lower
        if lower < state.lower:  # pragma: no cover - guarded by invariant tests
            raise AssertionError(f"lower bound regressed from {state.lower} to {lower}")
        state.lower = lower
        state.bounds.append((state.lower, state.upper))
        if self.observer is not None:
            self.observer({"lower": state.lower, "upper": state.upper,
                           "source_radius": state.left.radius,
                           "target_radius": state.right.radius,
                           "expansions": state.expansions})

    @staticmethod
    def _pause(state: Search, reason: str, message: str = "") -> bool:
        """Stop this slice without deciding the search."""
        state.reason, state.stop_message = reason, message or reason
        return False

    def _settle(self, state: Search, status: str, reason: str = "") -> bool:
        state.done, state.reason = status, reason
        if status == EXACT:
            state.lower = int(state.upper)
        state.bounds.append((state.lower, state.upper))
        return False

    # ----------------------------------------------------------------- output
    @staticmethod
    def result(state: Search) -> SearchResult:
        status = state.done or (VERIFIED if state.best else SEARCH_INCOMPLETE)
        left, right = state.left, state.right
        stats = {"expansions": state.expansions,
                 "source_expansions": left.expansions, "target_expansions": right.expansions,
                 "source_radius": left.radius, "target_radius": right.radius,
                 "source_known": len(left.dist), "target_known": len(right.dist),
                 "complete_neighborhoods": len(left.complete) + len(right.complete),
                 "blocked_neighborhoods": len(left.blocked) + len(right.blocked),
                 "meeting_checks": state.meetings, "stalled": state.stalled,
                 "bounds": list(state.bounds)}
        return SearchResult(status=status,
                            distance=int(state.upper) if status == EXACT else None,
                            path=state.best if status in {EXACT, VERIFIED} else None,
                            lower_bound=state.lower, upper_bound=state.upper,
                            reason=state.reason if status not in {EXACT, NO_PATH} else "",
                            stats=stats)


def dict_oracle(adjacency: dict[str, Iterable[str]], *, status: str = COMPLETE,
                missing: str = COMPLETE) -> NeighborhoodOracle:
    """A synthetic oracle over an in-memory graph, for tests and cached trials."""

    class _Dict:
        def neighborhood(self, node: str) -> Neighborhood:
            if node not in adjacency:
                return Neighborhood(frozenset(), missing)
            return Neighborhood(frozenset(adjacency[node]), status)

    return _Dict()


def cached_trial_path(adjacency: dict[str, Iterable[str]], source: str, target: str,
                      limit: int = 12) -> tuple[str, ...] | None:
    """Plain BFS over already-validated cached edges: an upper bound only."""
    if source == target:
        return (source,)
    parent: dict[str, str | None] = {source: None}
    queue = deque([(source, 0)])
    while queue:
        node, depth = queue.popleft()
        if depth >= limit:
            continue
        for neighbor in adjacency.get(node, ()):  # type: ignore[union-attr]
            if neighbor in parent:
                continue
            parent[neighbor] = node
            if neighbor == target:
                route, cursor = [], neighbor
                while cursor is not None:
                    route.append(cursor)
                    cursor = parent[cursor]
                return tuple(reversed(route))
            queue.append((neighbor, depth + 1))
    return None
