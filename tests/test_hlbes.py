"""Adversarial and differential tests for the HLBES exact search engine."""
from __future__ import annotations

import random
import sys
from pathlib import Path

import networkx as nx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hepgraph.hlbes import (COMPLETE, EXACT, NO_PATH, PARTIAL, SEARCH_INCOMPLETE, UNKNOWN,
                            VERIFIED, HLBES, Neighborhood, OracleStopped, Search, cached_trial_path,
                            dict_oracle)


def graph_of(edges):
    adjacency: dict[str, set[str]] = {}
    for left, right in edges:
        adjacency.setdefault(left, set()).add(right)
        adjacency.setdefault(right, set()).add(left)
    return {node: sorted(members) for node, members in adjacency.items()}


def chain(*nodes):
    return list(zip(nodes, nodes[1:]))


def search(adjacency, source, target, **kwargs):
    trial = kwargs.pop("trial_path", None)
    return HLBES(dict_oracle(adjacency), **kwargs).search(source, target, trial_path=trial)


# --------------------------------------------------------------- basic shape
def test_same_endpoint_is_zero_and_exact():
    result = search(graph_of([("a", "b")]), "a", "a")
    assert (result.status, result.distance, result.path) == (EXACT, 0, ("a",))


def test_direct_edge_is_one_hop_exact():
    result = search(graph_of([("a", "b")]), "a", "b")
    assert (result.status, result.distance) == (EXACT, 1)
    assert result.lower_bound == result.upper_bound == 1


def test_two_hop_intersection_is_exact():
    result = search(graph_of(chain("a", "m", "b")), "a", "b")
    assert (result.status, result.distance, result.path) == (EXACT, 2, ("a", "m", "b"))


def test_long_chain_stays_exact():
    nodes = [f"n{index}" for index in range(41)]
    result = search(graph_of(chain(*nodes)), nodes[0], nodes[-1])
    assert (result.status, result.distance) == (EXACT, 40)
    assert result.path == tuple(nodes)


# ------------------------------------------------------- adversarial bounds
def test_misleading_upper_bound_is_corrected():
    """A verified six-hop trial route must not hide the true four-hop route."""
    edges = chain("s", "a", "b", "c", "d", "e", "t") + chain("s", "p", "q", "r", "t")
    result = search(graph_of(edges), "s", "t", trial_path=["s", "a", "b", "c", "d", "e", "t"])
    assert (result.status, result.distance) == (EXACT, 4)
    assert result.path == ("s", "p", "q", "r", "t")


def test_famous_hub_route_loses_to_obscure_short_route():
    edges = chain("s", "hub", "h2", "h3", "h4", "t") + chain("s", "x", "y", "t")
    fame = {"hub": 1e9, "h2": 1e9, "h3": 1e9, "h4": 1e9, "x": -1e9, "y": -1e9}
    result = search(graph_of(edges), "s", "t", routing_score=lambda node: fame.get(node, 0.0))
    assert (result.status, result.distance) == (EXACT, 3)


def test_absurd_routing_priority_cannot_change_distance():
    edges = chain("s", "a", "b", "t") + chain("s", "c", "t") + [("a", "c")]
    adjacency = graph_of(edges)
    baseline = search(adjacency, "s", "t").distance
    rng = random.Random(99)
    for _ in range(60):
        scores = {node: rng.uniform(-1e12, 1e12) for node in adjacency}
        costs = {node: rng.uniform(1e-6, 1e9) for node in adjacency}
        result = search(adjacency, "s", "t", routing_score=lambda n: scores[n],
                        cost_estimate=lambda n: costs[n])
        assert (result.status, result.distance) == (EXACT, baseline)


def test_bounds_are_monotone_and_bracket_the_truth():
    nodes = [f"n{index}" for index in range(15)]
    edges = chain(*nodes) + [("n0", "n7")]
    result = search(graph_of(edges), "n0", "n14")
    lows = [low for low, _ in result.stats["bounds"]]
    ups = [up for _, up in result.stats["bounds"]]
    assert lows == sorted(lows)
    assert ups == sorted(ups, reverse=True)
    assert all(low <= result.distance <= up for low, up in result.stats["bounds"])


def test_multiple_shortest_paths_agree_on_distance():
    edges = [("s", f"m{i}") for i in range(12)] + [(f"m{i}", "t") for i in range(12)]
    rng = random.Random(5)
    for _ in range(25):
        scores = {f"m{i}": rng.random() for i in range(12)}
        result = search(graph_of(edges), "s", "t", routing_score=lambda n: scores.get(n, 0.0))
        assert (result.status, result.distance) == (EXACT, 2)
        assert result.path[0] == "s" and result.path[-1] == "t" and len(result.path) == 3


def test_dense_hub_stress_stays_exact():
    edges = [(f"h{i}", f"h{j}") for i in range(30) for j in range(i + 1, 30)]
    edges += [("s", "h0"), ("h29", "t")]
    result = search(graph_of(edges), "s", "t")
    assert (result.status, result.distance) == (EXACT, 3)


# ------------------------------------------------------------ status rules
def test_disconnected_graph_returns_no_path_only_after_exhaustion():
    edges = chain("s", "a", "b") + chain("t", "c", "d")
    result = search(graph_of(edges), "s", "t")
    assert result.status == NO_PATH
    assert result.path is None and result.distance is None


def test_partial_adjacency_never_certifies_exactness():
    """A route is found, but the withheld short route keeps it unproven."""
    edges = chain("s", "p", "q", "t") + chain("s", "x", "w", "y", "t")
    adjacency = graph_of(edges)
    withheld = {("p", "q"), ("q", "p")}

    class Oracle:
        def neighborhood(self, node):
            members = frozenset(adjacency.get(node, ()))
            hidden = {other for other in members if (node, other) in withheld}
            if hidden:
                return Neighborhood(members - hidden, PARTIAL)
            return Neighborhood(members, COMPLETE)

    result = HLBES(Oracle()).search("s", "t")
    assert result.status == VERIFIED
    assert result.distance is None                      # never claims a distance
    assert result.upper_bound == 4                      # the route it could see
    assert result.lower_bound < result.upper_bound      # shortestness unproven
    assert nx.shortest_path_length(nx.Graph(edges), "s", "t") == 3


def test_partial_adjacency_still_allows_proof_it_cannot_affect():
    """Partiality only blocks a layer it is actually needed for."""
    adjacency = graph_of(chain("s", "a", "b", "t"))

    class Oracle:
        def neighborhood(self, node):
            members = frozenset(adjacency.get(node, ()))
            if node == "a":  # never needed: both radii close without it
                return Neighborhood(members - {"b"}, PARTIAL)
            return Neighborhood(members, COMPLETE)

    result = HLBES(Oracle()).search("s", "t")
    assert (result.status, result.distance) == (EXACT, 3)


def test_partial_adjacency_on_both_endpoints_keeps_searching_but_never_proves():
    """Discovery continues past a stalled radius; the proof does not."""
    adjacency = graph_of(chain("s", "a", "t") + chain("s", "b", "c", "d", "t"))

    class Oracle:
        def neighborhood(self, node):
            members = frozenset(adjacency.get(node, ()))
            if node in {"s", "t"}:
                return Neighborhood(members - {"a"}, PARTIAL)
            return Neighborhood(members, COMPLETE)

    result = HLBES(Oracle()).search("s", "t")
    assert result.status == VERIFIED          # the long route was still found
    assert result.upper_bound == 4
    assert result.distance is None            # but 4 is never claimed as shortest
    assert result.lower_bound < result.upper_bound
    assert result.stats["stalled"] is True


def test_no_route_behind_partial_adjacency_is_incomplete_not_no_path():
    adjacency = graph_of(chain("s", "a", "b", "t"))

    class Oracle:
        def neighborhood(self, node):
            if node in {"s", "t"}:  # neither end can be read past
                return Neighborhood(frozenset(), PARTIAL)
            return Neighborhood(frozenset(adjacency.get(node, ())), COMPLETE)

    result = HLBES(Oracle()).search("s", "t")
    assert result.status == SEARCH_INCOMPLETE
    assert result.status != NO_PATH
    assert result.path is None


def test_unknown_adjacency_is_incomplete_not_no_path():
    class Oracle:
        def neighborhood(self, node):
            return Neighborhood(frozenset(), UNKNOWN)

    assert HLBES(Oracle()).search("s", "t").status == SEARCH_INCOMPLETE


def test_oracle_stop_yields_incomplete_or_verified_never_exact():
    adjacency = graph_of(chain("s", "a", "b", "c", "t"))

    class Oracle:
        def __init__(self):
            self.calls = 0

        def neighborhood(self, node):
            self.calls += 1
            if self.calls > 2:
                raise OracleStopped("rate_limited")
            return Neighborhood(frozenset(adjacency.get(node, ())), COMPLETE)

    result = HLBES(Oracle()).search("s", "t")
    assert result.status == SEARCH_INCOMPLETE and result.reason == "rate_limited"


def test_expansion_limit_reports_verified_rather_than_exact():
    nodes = [f"n{index}" for index in range(30)]
    engine = HLBES(dict_oracle(graph_of(chain(*nodes))), max_expansions=4)
    result = engine.search(nodes[0], nodes[-1])
    assert result.status == SEARCH_INCOMPLETE and result.reason == "expansion_limit"


def test_trial_path_alone_is_verified_when_proof_cannot_finish():
    adjacency = graph_of(chain("s", "a", "b", "t"))
    engine = HLBES(dict_oracle(adjacency), max_expansions=1)
    result = engine.search("s", "t", trial_path=["s", "a", "b", "t"])
    assert result.status == VERIFIED and result.upper_bound == 3 and result.distance is None


def test_invalid_trial_paths_are_ignored():
    adjacency = graph_of(chain("s", "a", "t"))
    for trial in ([], ["s"], ["s", "a", "s", "t"]):
        result = search(adjacency, "s", "t", trial_path=trial)
        assert (result.status, result.distance) == (EXACT, 2)


def test_neighborhood_rejects_unknown_status():
    with pytest.raises(ValueError):
        Neighborhood(frozenset(), "nearly")


# ------------------------------------------------------------ trial helper
def test_cached_trial_path_finds_a_route_or_none():
    adjacency = graph_of(chain("s", "a", "b", "t"))
    assert cached_trial_path(adjacency, "s", "t") == ("s", "a", "b", "t")
    assert cached_trial_path(adjacency, "s", "s") == ("s",)
    assert cached_trial_path(adjacency, "s", "missing") is None
    assert cached_trial_path(adjacency, "s", "t", limit=1) is None


# --------------------------------------------- differential against NetworkX
def _random_graph(rng):
    size = rng.randint(2, 60)
    seed = rng.randrange(10 ** 6)
    kind = rng.choice(["gnp", "ba", "ws", "tree", "grid", "lollipop", "barbell", "split"])
    if kind == "gnp":
        return nx.gnp_random_graph(size, rng.choice([0.02, 0.05, 0.15, 0.4]), seed=seed)
    if kind == "ba":
        return nx.barabasi_albert_graph(max(size, 5), rng.randint(1, 3), seed=seed)
    if kind == "ws":
        return nx.watts_strogatz_graph(max(size, 6), 4, rng.choice([0.0, 0.2, 0.6]), seed=seed)
    if kind == "tree":
        return nx.random_labeled_tree(max(size, 2), seed=seed)
    if kind == "grid":
        return nx.convert_node_labels_to_integers(nx.grid_2d_graph(rng.randint(2, 7), rng.randint(2, 7)))
    if kind == "lollipop":
        return nx.lollipop_graph(rng.randint(2, 7), rng.randint(1, 12))
    if kind == "barbell":
        return nx.barbell_graph(rng.randint(2, 7), rng.randint(0, 12))
    return nx.disjoint_union(nx.gnp_random_graph(size // 2 + 1, 0.3, seed=seed),
                             nx.gnp_random_graph(size // 2 + 1, 0.3, seed=seed + 1))


@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5, 6, 7, 8])
def test_matches_networkx_on_random_graphs(seed):
    """With a COMPLETE oracle there must be zero distance mismatches."""
    rng = random.Random(seed)
    for _ in range(90):
        graph = nx.relabel_nodes(_random_graph(rng), lambda node: f"n{node}")
        adjacency = {node: sorted(graph.neighbors(node)) for node in graph}
        nodes = sorted(graph)
        scores = {node: rng.uniform(-1e6, 1e6) for node in nodes}
        costs = {node: rng.uniform(1e-3, 1e6) for node in nodes}
        for _ in range(3):
            source, target = rng.choice(nodes), rng.choice(nodes)
            result = HLBES(dict_oracle(adjacency), routing_score=lambda n: scores[n],
                           cost_estimate=lambda n: costs[n]).search(source, target)
            try:
                truth = nx.shortest_path_length(graph, source, target)
            except nx.NetworkXNoPath:
                assert result.status == NO_PATH
                continue
            assert result.status == EXACT
            assert result.distance == truth
            assert result.path[0] == source and result.path[-1] == target
            assert len(result.path) - 1 == truth
            assert all(result.path[i + 1] in adjacency[result.path[i]]
                       for i in range(len(result.path) - 1))
            lows = [low for low, _ in result.stats["bounds"]]
            assert lows == sorted(lows)
            assert all(low <= truth <= up for low, up in result.stats["bounds"])


@pytest.mark.parametrize("seed", [11, 12, 13])
def test_random_trial_paths_never_change_the_distance(seed):
    rng = random.Random(seed)
    for _ in range(60):
        graph = nx.relabel_nodes(_random_graph(rng), lambda node: f"n{node}")
        adjacency = {node: sorted(graph.neighbors(node)) for node in graph}
        nodes = sorted(graph)
        source, target = rng.choice(nodes), rng.choice(nodes)
        try:
            truth = nx.shortest_path_length(graph, source, target)
        except nx.NetworkXNoPath:
            continue
        trial = None
        for candidate in nx.all_simple_paths(graph, source, target, cutoff=min(truth + 5, 11)):
            trial = candidate if trial is None or len(candidate) > len(trial) else trial
            if len(trial) > truth + 3:
                break
        result = HLBES(dict_oracle(adjacency)).search(source, target, trial_path=trial)
        assert (result.status, result.distance) == (EXACT, truth)


# ------------------------------------------------------------- resumability
def test_a_paused_search_resumes_without_losing_the_proof():
    """A transient stop is not an answer: the same state must continue."""
    adjacency = graph_of(chain("n0", "n1", "n2", "n3", "n4", "n5"))

    class Flaky:
        def __init__(self):
            self.allowed = 2
            self.calls = 0

        def neighborhood(self, node):
            if self.allowed <= 0:
                raise OracleStopped("rate_limited", "slice exhausted")
            self.allowed -= 1
            self.calls += 1
            return Neighborhood(frozenset(adjacency.get(node, ())), COMPLETE)

    oracle = Flaky()
    engine = HLBES(oracle)
    state = engine.begin("n0", "n5")
    while engine.advance(state):
        pass
    assert state.done is None                     # paused, not finished
    assert HLBES.result(state).status in {VERIFIED, SEARCH_INCOMPLETE}
    first_calls = oracle.calls

    oracle.allowed = 50                           # the slice budget returns
    while engine.advance(state):
        pass
    result = HLBES.result(state)
    assert (result.status, result.distance) == (EXACT, 5)
    assert oracle.calls > first_calls
    lows = [low for low, _ in result.stats["bounds"]]
    assert lows == sorted(lows)                   # the bound never went backwards


def test_stopping_rule_uses_the_full_radius_sum_plus_one():
    """U == Rs + Rt + 1 is provably exact and must not cost another layer."""
    nodes = [f"n{index}" for index in range(7)]
    counted = []

    class Counting:
        def neighborhood(self, node):
            counted.append(node)
            return Neighborhood(frozenset(graph_of(chain(*nodes)).get(node, ())), COMPLETE)

    result = HLBES(Counting()).search(nodes[0], nodes[-1])
    assert (result.status, result.distance) == (EXACT, 6)
    # Six hops across seven nodes: proving it must not expand every node twice.
    assert len(counted) <= len(nodes)


def test_side_is_ranked_by_the_cost_of_the_layer_it_would_actually_read():
    """The side rank and the node it expands use the same estimates: a side
    cannot win on a one-page person and then read a ten-page one."""
    costs = {"a": 1.0, "b": 10.0, "c": 2.0, "d": 2.0}
    engine = HLBES(dict_oracle({}), cost_estimate=lambda n: costs[n],
                   routing_score=lambda n: {"b": 5.0}.get(n, 0.0))
    state = Search("s", "t")
    state.left.complete.add("s"); state.right.complete.add("t")
    for node in ("a", "b"):
        state.left.add(node, 1, "s")
    for node in ("c", "d"):
        state.right.add(node, 1, "t")
    state.left.radius = state.right.radius = 1
    side, _, node = engine._choose(state)
    # Source layer costs 11 in total, target layer 4: the target side wins even
    # though the source has the single cheapest person and the highest score.
    assert side.name == "target" and node == "c"
    # Within a layer the cheapest person goes first; routing utility only
    # breaks ties between equal costs.
    costs["c"] = 3.0
    side, _, node = engine._choose(state)
    assert side.name == "target" and node == "d"
    state.left.radius = 0  # Nothing pending on the source at its radius.
    side, _, node = engine._choose(state)
    assert side.name == "target"


def test_within_a_layer_the_cheapest_person_is_read_first():
    costs = {"a": 3.0, "b": 1.0, "c": 2.0}
    engine = HLBES(dict_oracle({}), cost_estimate=lambda n: costs.get(n, 1.0),
                   routing_score=lambda n: {"a": 9.0}.get(n, 0.0))
    state = Search("s", "t")
    state.left.complete.add("s"); state.right.complete.add("t")
    for node in costs:
        state.left.add(node, 1, "s")
    state.left.radius = 1
    assert engine._choose(state)[2] == "b"
    state.left.complete.add("b")
    assert engine._choose(state)[2] == "c"
    costs["c"] = costs["a"]
    assert engine._choose(state)[2] == "a"  # Equal cost: the higher score wins.


def test_breadth_ranks_a_side_by_its_next_layer_not_everyone_it_has_heard_of():
    """A side that glimpsed many deep names is not thereby the expensive side."""
    # The target root's own page names thirty people; the source root's names one.
    edges = [("s", "a"), ("a", "m"), ("m", "t")] + [("t", f"d{i}") for i in range(30)]
    expanded = []

    class Recording:
        def __init__(self, inner): self.inner = inner
        def neighborhood(self, node):
            expanded.append(node)
            return self.inner.neighborhood(node)

    result = HLBES(Recording(dict_oracle(graph_of(edges)))).search("s", "t")
    assert result.status == EXACT and result.distance == 3
    # The thirty-person layer was glimpsed, never read: the small frontier
    # was grown until the sides met, and the proof closed on the roots.
    assert not any(node.startswith("d") for node in expanded)
    assert expanded.count("t") == 1
