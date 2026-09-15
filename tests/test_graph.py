"""Deterministic and independent-reference tests for ``hepgraph.graph``."""

from __future__ import annotations

import random
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone

import pytest

from hepgraph.graph import Filters, Graph, GraphError


def person(person_id: str, name: str | None = None) -> dict:
    return {
        "id": person_id,
        "name": name or f"Person {person_id}",
        "aliases": [],
        "affiliations": [],
        "orcid": None,
        "profile_status": "profile",
        "source_url": f"https://inspirehep.net/authors/{person_id}",
    }


def work(work_id: str, authors: list[str], *, count: int | None = None, year: int | None = 2020,
         types: list[str] | None = None, unresolved: int = 0, title: str | None = None) -> dict:
    return {
        "id": work_id, "title": title if title is not None else f"Work {work_id}",
        "year": year,
        "date": None if year is None else f"{year}-01-01",
        "date_source": "preprint",
        "author_count": len(authors) + unresolved if count is None else count,
        "authors": authors,
        "unresolved_count": unresolved,
        "document_types": ["article"] if types is None else types,
        "doi": [],
        "arxiv": [],
        "source_url": f"https://inspirehep.net/literature/{work_id}",
        "source_ids": [],
        "retrieved_at": "2026-09-14T00:00:00Z",
    }


def phd(adviser: str, student: str, record: str, year: int = 2000) -> dict:
    return {
        "adviser": adviser, "student": student, "degree": "PhD", "year": year,
        "source_url": "https://inspirehep.net/literature/doctoral", "source_record": record,
        "uncertainty": None, "retrieved_at": "2026-09-14T00:00:00Z",
    }


@pytest.fixture
def snapshot() -> dict:
    return {
        "version": "fixture-v1", "created_at": "2026-09-14T00:00:00Z",
        "coverage": {"label": "fixture", "complete": False},
        "people": [person(item) for item in "ABCDEFGHI"],
        "works": [
            work("w1", ["A", "B"], year=2010),
            work("w2", ["A", "B"], year=2020),
            work("w3", ["B", "C"], year=2020),
            work("w4", ["C", "D"], year=2021),
            work("w5", ["A", "E"], count=11, year=2020),  # cap boundary fail at 10
            work("w6", ["E", "F"], count=10, year=2020),  # exact cap passes
            work("w7", ["F", "G"], year=None),
            work("w8", ["G", "H"], year=2020, types=["thesis", "article"]),
            work("w9", ["H", "I"], year=2020, types=["book"]),
            work("w10", ["A", "X"], year=2020),  # unresolved profile ID is not a node
            work("w2", ["A", "C"], year=2020),  # stable work duplicate cannot add A--C
        ],
        "phd": [phd("D", "E", "p1"), phd("E", "G", "p2"), phd("I", "E", "p3")],
    }


def ids(path_result: dict) -> list[list[str]]:
    return [[person_["id"] for person_ in path["people"]] for path in path_result["paths"]]


def test_metric_timestamp_is_computation_time_not_snapshot_time(snapshot: dict) -> None:
    snapshot["created_at"] = "2000-01-01T00:00:00Z"
    before = datetime.now(timezone.utc)
    result = Graph(snapshot, Filters()).centrality("degree")
    after = datetime.now(timezone.utc)
    computed = datetime.fromisoformat(result["computed_at"].replace("Z", "+00:00"))
    assert before <= computed <= after


def test_filters_validate_boundaries_roundtrip_and_invalid_values() -> None:
    assert Filters.from_dict({"max_authors": "all", "min_shared": 1000, "year_start": 1000, "year_end": 2100, "genealogy": "false"}).to_dict() == {
        "max_authors": None, "min_shared": 1000, "year_start": 1000, "year_end": 2100, "genealogy": False, "min_authors": 1,
    }
    for bad in (
        {"max_authors": 0}, {"max_authors": 100001}, {"min_shared": 0},
        {"min_shared": 1001}, {"year_start": 999}, {"year_end": 2101},
        {"year_start": 2021, "year_end": 2020}, {"genealogy": "sometimes"},
        {"max_authors": True}, {"unexpected": 1},
    ):
        with pytest.raises(GraphError) as error:
            Filters.from_dict(bad)
        assert error.value.code == "invalid_filter"


def test_filter_order_full_author_count_unknown_dates_and_distinct_work_dedup(snapshot: dict) -> None:
    graph = Graph(snapshot, Filters())
    # w5 fails because the original full count is 11, w6 passes at the 10 cap;
    # w2's duplicate record must not turn A--C into a collaboration.
    assert set(graph.works) == {"w1", "w2", "w3", "w4", "w6", "w7", "w10"}
    profile = graph.profile("A")
    assert profile["indexed_publications"] == 4
    assert profile["eligible_publications"] == 3
    assert [item["person"]["id"] for item in graph.profile("A")["collaborators"]] == ["B"]
    assert graph.find_paths("A", "E")["status"] == "ok"  # A-B-C-D => PhD => E
    bounded = Graph(snapshot, Filters(year_start=2019, year_end=2020))
    assert set(bounded.works) == {"w2", "w3", "w6", "w10"}
    # Date-less w7 is permitted without a date bound and excluded with one.
    assert "w7" not in bounded.works
    assert "w7" in Graph(snapshot, Filters(max_authors=None)).works


def test_min_shared_is_after_eligible_distinct_works_and_genealogy_is_independent(snapshot: dict) -> None:
    graph = Graph(snapshot, Filters(min_shared=2))
    assert graph.find_paths("A", "B")["status"] == "ok"
    assert graph.find_paths("B", "C")["status"] == "no_path"
    # The doctoral edge remains when paper filters remove every paper.
    doctoral = Graph(snapshot, Filters(max_authors=1, min_shared=1, year_start=2099, year_end=2100))
    assert doctoral.find_paths("D", "E")["status"] == "ok"
    assert doctoral.find_paths("D", "E")["paths"][0]["edges"][0]["types"] == ["phd"]
    no_genealogy = Graph(snapshot, Filters(genealogy=False))
    assert no_genealogy.find_paths("D", "E")["status"] == "no_path"
    # Turning genealogy off changes ordinary graph edges, not documented profile facts.
    profile = no_genealogy.profile("E")
    assert [record["source_record"] for record in profile["advisers"]] == ["p1", "p3"]
    assert profile["combined_degree"] == profile["coauthor_count"]


def test_standalone_correction_notice_cannot_inflate_min_shared_work_threshold() -> None:
    people = [person("A"), person("B")]
    original_and_correction = {
        "version": "correction-threshold", "people": people, "phd": [],
        "works": [
            work("original", ["A", "B"], title="A measurement with a detector"),
            work("erratum", ["A", "B"], title="  ErRaTuM: A measurement with a detector"),
        ],
    }
    rejected = Graph(original_and_correction, Filters(min_shared=2))
    assert "erratum" not in rejected.works
    assert rejected.find_paths("A", "B")["status"] == "no_path"

    two_research_works = deepcopy(original_and_correction)
    two_research_works["works"].append(
        work("followup", ["A", "B"], title="Independent detector calibration")
    )
    accepted = Graph(two_research_works, Filters(min_shared=2))
    edge = accepted.find_paths("A", "B")["paths"][0]["edges"][0]
    assert {item["id"] for item in edge["works"]} == {"original", "followup"}


@pytest.mark.parametrize("title", [
    "Erratum: title", " errata — title", "CORRIGENDUM (title)",
])
def test_only_leading_correction_labels_are_excluded(title: str) -> None:
    correction = Graph({
        "version": "correction-title", "people": [person("A"), person("B")], "phd": [],
        "works": [work("notice", ["A", "B"], title=title)],
    })
    assert correction.works == {}

    research = Graph({
        "version": "research-title", "people": [person("A"), person("B")], "phd": [],
        "works": [work("research", ["A", "B"], title="A study of an erratum in detector calibration")],
    })
    assert set(research.works) == {"research"}


def test_mixed_hops_dual_evidence_and_path_evidence_is_complete(snapshot: dict) -> None:
    extra = deepcopy(snapshot)
    extra["phd"].append(phd("A", "B", "p-dual"))
    graph = Graph(extra, Filters())
    result = graph.find_paths("A", "G")
    assert result["status"] == "ok"
    assert ids(result) == [["A", "B", "C", "D", "E", "G"]]
    dual = graph.find_paths("A", "B")["paths"][0]["edges"][0]
    assert dual["types"] == ["coauthor", "phd"]
    assert dual["shared_works"] == 2
    assert [item["id"] for item in dual["works"]] == ["w1", "w2"]
    assert [item["source_record"] for item in dual["phd"]] == ["p-dual"]


def test_bfs_returns_deterministic_shortest_useful_alternatives() -> None:
    data = {
        "version": "diamond", "people": [person(item) for item in "ABCDEFG"],
        "works": [
            work("ab", ["A", "B"]), work("bd", ["B", "D"]),
            work("ac", ["A", "C"]), work("cd", ["C", "D"]),
            work("ae", ["A", "E"]), work("ed", ["E", "D"]),
            work("af", ["A", "F"]), work("fg", ["F", "G"]), work("gd", ["G", "D"]),
        ], "phd": [],
    }
    graph = Graph(data, Filters())
    result = graph.find_paths("A", "D", alternatives=3)
    assert ids(result) == [["A", "B", "D"], ["A", "C", "D"], ["A", "E", "D"]]
    assert all(path["hops"] == 2 for path in result["paths"])
    with pytest.raises(GraphError):
        graph.find_paths("A", "D", alternatives=4)


def test_path_distance_remains_exact_when_alternative_parent_storage_is_bounded() -> None:
    middle = [f"M{number:02}" for number in range(13)]
    data = {
        "version": "many-shortest", "people": [person(item) for item in ["A", "Z", *middle]],
        "works": [work(f"a{item}", ["A", item]) for item in middle] + [work(f"z{item}", [item, "Z"]) for item in middle],
        "phd": [],
    }
    result = Graph(data, Filters()).find_paths("A", "Z", alternatives=3)
    assert result["exact"] is True
    assert result["alternatives_truncated"] is True
    assert result["paths"][0]["hops"] == 2


def test_long_shortest_path_is_reconstructed_iteratively() -> None:
    names = [f"P{number}" for number in range(1_050)]
    data = {"version": "long", "people": [person(item) for item in names], "works": [work(f"w{number}", [names[number], names[number + 1]]) for number in range(len(names) - 1)], "phd": []}
    result = Graph(data, Filters()).find_paths(names[0], names[-1])
    assert result["status"] == "ok" and result["paths"][0]["hops"] == len(names) - 1


def test_not_indexed_no_path_isolation_and_multiadviser_ancestry(snapshot: dict) -> None:
    graph = Graph(snapshot, Filters())
    assert graph.find_paths("A", "MISSING")["status"] == "not_indexed"
    assert graph.find_paths("A", "H")["status"] == "no_path"
    assert graph.profile("I")["coauthor_count"] == 0
    assert graph.profile("E")["advisers"] == [phd("D", "E", "p1"), phd("I", "E", "p3")]
    # E has D and I as advisers; both appear in the directed ancestor result.
    tree = graph.ancestry("E", "ancestors")
    assert {item["id"] for item in tree["people"]} == {"D", "E", "I"}
    assert {(edge["source"], edge["target"]) for edge in tree["edges"]} == {("D", "E"), ("I", "E")}
    with pytest.raises(GraphError, match="not indexed"):
        graph.neighborhood("missing")


def test_neighborhood_limit_and_large_incidence_without_clique_materialization() -> None:
    names = [str(number) for number in range(120)]
    data = {"version": "large", "people": [person(item) for item in names], "works": [work("big", names, count=120)], "phd": []}
    graph = Graph(data, Filters(max_authors=120))
    result = graph.find_paths("0", "119")
    assert result["status"] == "ok"
    assert ids(result) == [["0", "119"]]
    neighborhood = graph.neighborhood("0", limit=5)
    assert len(neighborhood["people"]) == 5
    assert neighborhood["truncated"] is True
    # No global pair-clique attribute is produced; pair evidence is cached only on demand.
    assert len(graph._pair_cache) < len(names) * (len(names) - 1) // 2


def test_resource_limits_are_explicit_and_not_reported_as_no_path(snapshot: dict, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Graph, "MAX_QUERY_OPERATIONS", 1)
    graph = Graph(snapshot, Filters())
    result = graph.find_paths("A", "D")
    assert result["status"] == "resource_limit"
    assert result["exact"] is False
    monkeypatch.setattr(Graph, "MAX_INDEXED_WORKS", 1)
    with pytest.raises(GraphError) as error:
        Graph(snapshot, Filters())
    assert error.value.code == "resource_limit"


def test_profile_survives_component_limit_and_caches_are_bounded(snapshot: dict, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Graph, "MAX_QUERY_OPERATIONS", 1)
    profile = Graph(snapshot, Filters()).profile("A")
    assert profile["person"]["id"] == "A"
    assert profile["collaborators"][0]["person"]["id"] == "B"
    assert profile["reachability"]["status"] == "resource_limit"
    assert profile["reachability"]["coauthor_component_size"] is None

    monkeypatch.setattr(Graph, "MAX_PAIR_CACHE", 3)
    monkeypatch.setattr(Graph, "MAX_NEIGHBOR_CACHE", 2)
    graph = Graph(snapshot, Filters())
    for item in "ABCDEFG":
        graph.profile(item)
    assert len(graph._pair_cache) <= 3
    assert len(graph._neighbor_cache) <= 2
    # Direct pair lookup avoids an otherwise unnecessary neighbour expansion.
    monkeypatch.setattr(Graph, "MAX_QUERY_OPERATIONS", 0)
    assert graph.find_paths("A", "B")["status"] == "ok"


def _reference_graph(data: dict, filters: Filters):
    nx = pytest.importorskip("networkx")
    graph = Graph(data, filters)
    reference = nx.Graph()
    reference.add_nodes_from(graph.people)
    pair_counts: dict[tuple[str, str], int] = defaultdict(int)
    for work_item in graph.works.values():
        authors = sorted({str(author) for author in work_item.get("authors", []) if str(author) in graph.people})
        for position, left in enumerate(authors):
            for right in authors[position + 1:]:
                pair_counts[(left, right)] += 1
    for (left, right), count in pair_counts.items():
        if count >= filters.min_shared:
            reference.add_edge(left, right)
    if filters.genealogy:
        for record in graph.phd:
            reference.add_edge(str(record["adviser"]), str(record["student"]))
    return graph, reference


def test_random_paths_components_and_centralities_match_networkx_reference() -> None:
    rng = random.Random(1729)
    names = [str(item) for item in range(18)]
    works = []
    for number in range(36):
        authors = rng.sample(names, rng.randint(2, 5))
        works.append(work(f"r{number}", authors, year=rng.choice([2018, 2019, 2020, 2021])))
    records = [phd("0", "1", "d1"), phd("4", "9", "d2"), phd("10", "14", "d3")]
    data = {"version": "random", "created_at": "2026-09-14T00:00:00Z", "people": [person(item) for item in names], "works": works, "phd": records}
    filters = Filters(max_authors=5, min_shared=2)
    graph, reference = _reference_graph(data, filters)
    nx = pytest.importorskip("networkx")

    for source in names:
        for target in names:
            ours = graph.find_paths(source, target)
            if nx.has_path(reference, source, target):
                assert ours["status"] == "ok"
                assert ours["paths"][0]["hops"] == nx.shortest_path_length(reference, source, target)
            else:
                assert ours["status"] == "no_path"

    components = {item: len(next(component for component in nx.connected_components(reference) if item in component)) for item in names}
    for item in names:
        profile = graph.profile(item)
        assert profile["reachability"]["combined_component_size"] == components[item]

    degree = graph.centrality("degree", limit=50)
    degree_values = {row["person"]["id"]: row["value"] for row in degree["rows"]}
    coauthor = _reference_graph(data, Filters(max_authors=5, min_shared=2, genealogy=False))[1]
    assert degree_values == {item: float(coauthor.degree(item)) for item in names}

    harmonic = graph.centrality("harmonic", limit=50)
    harmonic_values = {row["person"]["id"]: row["value"] for row in harmonic["rows"]}
    expected_harmonic = nx.harmonic_centrality(reference, distance=None)
    for item in names:
        assert harmonic_values[item] == pytest.approx(expected_harmonic[item] / (len(names) - 1))

    betweenness = graph.centrality("betweenness", limit=50)
    betweenness_values = {row["person"]["id"]: row["value"] for row in betweenness["rows"]}
    expected_betweenness = nx.betweenness_centrality(reference, normalized=True)
    for item in names:
        assert betweenness_values[item] == pytest.approx(expected_betweenness[item])


def test_degree_is_exact_above_global_active_distance_budget() -> None:
    pairs = [(f"A{number}", f"B{number}") for number in range(Graph.MAX_CENTRALITY_NODES + 1)]
    names = [item for pair in pairs for item in pair]
    data = {"version": "many-pairs", "people": [person(item) for item in names], "works": [work(f"w{number}", list(pair)) for number, pair in enumerate(pairs)], "phd": []}
    result = Graph(data, Filters()).centrality("degree", limit=3)
    assert result["status"] == "ok" and result["exact"] is True
    assert all(row["value"] == 1.0 for row in result["rows"])


def test_degree_has_one_aggregate_expansion_budget_for_a_giant_eligible_work() -> None:
    names = [f"G{number}" for number in range(600)]
    data = {
        "version": "giant-degree", "people": [person(item) for item in names],
        "works": [work("giant", names, count=len(names))], "phd": [],
    }
    result = Graph(data, Filters(max_authors=len(names))).centrality("degree")
    assert result["status"] == "resource_limit"
    assert result["exact"] is False
    assert "expansion limit" in result["message"]


def test_sampled_betweenness_is_deterministic_and_matches_networkx_subset_estimator(monkeypatch: pytest.MonkeyPatch) -> None:
    nx = pytest.importorskip("networkx")
    names = [f"P{number:03}" for number in range(501)]
    data = {"version": "sampled", "people": [person(item) for item in names], "works": [work(f"w{number}", [names[number], names[number + 1]]) for number in range(len(names) - 1)], "phd": []}
    graph = Graph(data, Filters())
    first = graph.centrality("betweenness", limit=500)
    second = graph.centrality("betweenness", limit=500)
    assert first["status"] == "ok" and first["exact"] is False
    assert first["method"] == "deterministic sampled Brandes estimator"
    assert first["approximation"]["source_count"] == 64
    assert first["ranking_note"].startswith("Ranks are deterministic estimates")
    assert first["rows"] == second["rows"]

    reference = nx.path_graph(names)
    sample = random.Random(42).sample(sorted(names), 64)
    subset = nx.betweenness_centrality_subset(reference, sources=sample, targets=names, normalized=False)
    # NetworkX's directed-subset convention contributes half an undirected
    # source dependency total. Scale it independently to this estimator.
    factor = 2 * len(names) / len(sample) / ((len(names) - 1) * (len(names) - 2))
    observed = {row["person"]["id"]: row["value"] for row in first["rows"]}
    for item, value in observed.items():
        assert value == pytest.approx(subset[item] * factor)
    monkeypatch.setattr(Graph, "MAX_CENTRALITY_WORK", 1)
    limited = graph.centrality("betweenness")
    assert limited["status"] == "resource_limit" and "estimated" in limited["message"]


def test_dense_component_work_preflight_bounds_all_source_centralities(monkeypatch: pytest.MonkeyPatch) -> None:
    names = [f"D{number}" for number in range(100)]
    # Doctoral records make a dense person graph without constructing work-paper
    # cliques. The analytic estimate is 100 * (100 + 100 * 99) = 1,000,000.
    data = {
        "version": "dense", "people": [person(item) for item in names], "works": [],
        "phd": [phd(left, right, f"{left}-{right}") for position, left in enumerate(names) for right in names[position + 1:]],
    }
    monkeypatch.setattr(Graph, "MAX_CENTRALITY_WORK", 999_999)
    graph = Graph(data, Filters())
    for metric in ("harmonic", "betweenness", "eccentricity"):
        result = graph.centrality(metric)
        assert result["status"] == "resource_limit"
        assert "estimated" in result["message"]


def test_eccentricity_uses_largest_non_isolated_component_and_honest_scope() -> None:
    data = {
        "version": "ecc", "people": [person(item) for item in "ABCDEFG"],
        "works": [work("ab", ["A", "B"]), work("bc", ["B", "C"]), work("de", ["D", "E"])], "phd": [],
    }
    result = Graph(data, Filters()).centrality("eccentricity", limit=10)
    assert result["population"] == 7
    assert result["radius"] == 1.0
    assert [item["id"] for item in result["centers"]] == ["B"]
    assert {row["person"]["id"] for row in result["rows"]} == {"A", "B", "C"}
    all_isolated = Graph({"version": "empty", "people": [person("A")], "works": [], "phd": []}, Filters()).centrality("eccentricity")
    assert all_isolated["rows"] == [] and all_isolated["radius"] is None


def test_centrality_keeps_large_isolated_population_but_computes_active_graph() -> None:
    isolated = [f"z{number}" for number in range(2_100)]
    data = {
        "version": "population", "people": [person(item) for item in ["A", "B", "C", *isolated]],
        "works": [work("ab", ["A", "B"]), work("bc", ["B", "C"])], "phd": [],
    }
    graph = Graph(data, Filters())
    harmonic = graph.centrality("harmonic", limit=10)
    values = {row["person"]["id"]: row["value"] for row in harmonic["rows"]}
    assert harmonic["status"] == "ok" and harmonic["population"] == len(data["people"])
    assert values["B"] == pytest.approx(2 / (len(data["people"]) - 1))
    assert graph.centrality("betweenness", limit=10)["status"] == "ok"
