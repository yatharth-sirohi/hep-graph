"""Bounded acceptance checks against the real, generated pilot snapshot.

These checks intentionally reconstruct a NetworkX reference from snapshot JSON
instead of using Graph internals.  They exercise the view a professor will see
without materialising a clique for any work above the selected author caps.
"""
from __future__ import annotations

from collections import defaultdict
from itertools import combinations
import json
from pathlib import Path
import random

import pytest

from hepgraph.graph import Filters, Graph


SNAPSHOT = Path(__file__).resolve().parents[1] / "data" / "current.json"


def _eligible(work: dict, filters: Filters) -> bool:
    """Independent copy of the documented snapshot eligibility policy."""
    types = {str(value).strip().lower() for value in work.get("document_types", [])}
    if not types.intersection({"article", "conference paper"}):
        return False
    if types.intersection({"thesis", "book", "book chapter", "proceedings"}):
        return False
    count = work.get("author_count")
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        return False
    if filters.max_authors is not None and count > filters.max_authors:
        return False
    year = work.get("year")
    if filters.year_start is not None or filters.year_end is not None:
        if not isinstance(year, int) or isinstance(year, bool):
            return False
        if filters.year_start is not None and year < filters.year_start:
            return False
        if filters.year_end is not None and year > filters.year_end:
            return False
    return True


def _reference(snapshot: dict, filters: Filters):
    nx = pytest.importorskip("networkx")
    people = {str(person["id"]) for person in snapshot["people"] if isinstance(person, dict) and person.get("id") is not None}
    coauthor = nx.Graph()
    coauthor.add_nodes_from(people)
    pair_works: dict[tuple[str, str], list[str]] = defaultdict(list)
    works: dict[str, dict] = {}
    for work in snapshot["works"]:
        if not isinstance(work, dict) or work.get("id") is None:
            continue
        work_id = str(work["id"])
        if work_id in works or not _eligible(work, filters):
            continue
        works[work_id] = work
        authors = sorted({str(author) for author in work.get("authors", []) if str(author) in people})
        # Every included production paper has at most the requested cap. This
        # makes the independent combinations bounded (10 default, 5 preset).
        for left, right in combinations(authors, 2):
            pair_works[(left, right)].append(work_id)
    for pair, record_ids in pair_works.items():
        if len(record_ids) >= filters.min_shared:
            coauthor.add_edge(*pair)

    combined = coauthor.copy()
    phd_by_pair: dict[tuple[str, str], list[dict]] = defaultdict(list)
    if filters.genealogy:
        seen: set[tuple[str, str, str]] = set()
        for record in snapshot.get("phd", []):
            if not isinstance(record, dict) or record.get("adviser") is None or record.get("student") is None:
                continue
            adviser, student = str(record["adviser"]), str(record["student"])
            key = (adviser, student, str(record.get("source_record", "")))
            if key in seen or adviser == student or adviser not in people or student not in people:
                continue
            seen.add(key)
            combined.add_edge(adviser, student)
            phd_by_pair[tuple(sorted((adviser, student)))].append(record)
    return coauthor, combined, pair_works, phd_by_pair


@pytest.fixture(scope="module")
def pilot() -> dict:
    if not SNAPSHOT.exists():
        pytest.skip("real pilot snapshot has not been built")
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


def _seeded_component_pairs(reference, count: int = 30) -> list[tuple[str, str]]:
    components = [sorted(component) for component in __import__("networkx").connected_components(reference) if len(component) > 1]
    assert components, "pilot must contain a connected demo component"
    largest = min((component for component in components if len(component) == max(map(len, components))), key=lambda component: component)
    pairs = list(combinations(largest, 2))
    return random.Random(20260914).sample(pairs, min(count, len(pairs)))


def test_real_pilot_paths_filters_and_evidence_match_independent_networkx(pilot: dict) -> None:
    nx = pytest.importorskip("networkx")
    presets = [
        Filters(),
        Filters(max_authors=5, min_shared=2, year_start=2020, year_end=2020, genealogy=False),
    ]
    for filters in presets:
        graph = Graph(pilot, filters)
        coauthor, reference, pair_works, phd_by_pair = _reference(pilot, filters)
        assert set(graph.works) == {str(work_id) for work_id in {work["id"] for work in pilot["works"] if _eligible(work, filters)}}
        selected = _seeded_component_pairs(reference)
        for source, target in selected:
            actual = graph.find_paths(source, target)
            assert actual["status"] == "ok"
            assert actual["paths"][0]["hops"] == nx.shortest_path_length(reference, source, target)
            for edge in actual["paths"][0]["edges"]:
                pair = tuple(sorted((edge["source"], edge["target"])))
                expected_work_ids = pair_works.get(pair, [])
                expected_work_ids = expected_work_ids if len(expected_work_ids) >= filters.min_shared else []
                expected_phd = phd_by_pair.get(pair, []) if filters.genealogy else []
                assert edge["shared_works"] == len(expected_work_ids)
                assert {str(work["id"]) for work in edge["works"]} == set(expected_work_ids)
                assert {str(record["source_record"]) for record in edge["phd"]} == {str(record["source_record"]) for record in expected_phd}
                assert set(edge["types"]) == ({"coauthor"} if expected_work_ids else set()) | ({"phd"} if expected_phd else set())
        # The preset intentionally removes doctoral edges from ordinary paths.
        assert graph.centrality("degree", limit=5)["scope"].endswith("eligible coauthorship only")
        assert all(coauthor.has_node(person) for person in graph.people)


def test_real_pilot_degree_harmonic_component_scope_and_sampled_betweenness(pilot: dict) -> None:
    nx = pytest.importorskip("networkx")
    filters = Filters()
    graph = Graph(pilot, filters)
    coauthor, combined, _, _ = _reference(pilot, filters)
    population = len(pilot["people"])

    degree = graph.centrality("degree", limit=100)
    assert degree["status"] == "ok" and degree["exact"] is True
    for row in degree["rows"]:
        assert row["value"] == float(coauthor.degree(str(row["person"]["id"])))

    harmonic = graph.centrality("harmonic", limit=50)
    assert harmonic["status"] == "ok" and harmonic["population"] == population
    for row in harmonic["rows"][:30]:
        person_id = str(row["person"]["id"])
        expected = sum(1 / distance for distance in nx.single_source_shortest_path_length(combined, person_id).values() if distance) / (population - 1)
        assert row["value"] == pytest.approx(expected)

    components = [sorted(component) for component in nx.connected_components(combined) if len(component) > 1]
    largest = min((component for component in components if len(component) == max(map(len, components))), key=lambda component: component)
    eccentricity = graph.centrality("eccentricity", limit=500)
    assert eccentricity["status"] == "ok"
    assert f"component of {len(largest)} people" in eccentricity["scope"]
    expected_eccentricity = nx.eccentricity(combined.subgraph(largest))
    assert {str(row["person"]["id"]) for row in eccentricity["rows"]} == set(largest)
    for row in eccentricity["rows"]:
        assert row["value"] == float(expected_eccentricity[str(row["person"]["id"])])

    betweenness = graph.centrality("betweenness", limit=100)
    active = sorted(node for node in combined if combined.degree(node))
    assert betweenness["status"] == "ok" and betweenness["exact"] is False
    assert betweenness["approximation"]["active_population"] == len(active)
    sources = random.Random(Graph.BETWENNESS_SAMPLE_SEED).sample(active, Graph.BETWENNESS_SAMPLE_SOURCES)
    subset = nx.betweenness_centrality_subset(combined, sources=sources, targets=active, normalized=False)
    factor = 2 * len(active) / len(sources) / ((population - 1) * (population - 2))
    for row in betweenness["rows"][:30]:
        assert row["value"] == pytest.approx(subset[str(row["person"]["id"])] * factor)


def test_real_pilot_directed_ancestry_and_evidence_counts(pilot: dict) -> None:
    nx = pytest.importorskip("networkx")
    graph = Graph(pilot, Filters())
    directed = nx.DiGraph()
    directed.add_nodes_from(graph.people)
    records: dict[tuple[str, str], list[dict]] = defaultdict(list)
    seen: set[tuple[str, str, str]] = set()
    for record in pilot["phd"]:
        adviser, student = str(record["adviser"]), str(record["student"])
        key = (adviser, student, str(record.get("source_record", "")))
        if key not in seen and adviser in graph.people and student in graph.people and adviser != student:
            seen.add(key)
            directed.add_edge(adviser, student)
            records[(adviser, student)].append(record)
    candidate = min(node for node in directed if directed.in_degree(node) and directed.out_degree(node))
    result = graph.ancestry(candidate, "ancestors", limit=100)
    expected_nodes = set(nx.ancestors(directed, candidate)) | {candidate}
    assert {str(person["id"]) for person in result["people"]} == expected_nodes
    expected_edges = {(left, right) for left, right in directed.edges if left in expected_nodes and right in expected_nodes}
    assert {(edge["source"], edge["target"]) for edge in result["edges"]} == expected_edges
    for edge in result["edges"]:
        assert len(edge["phd"]) == len(records[(edge["source"], edge["target"])])
