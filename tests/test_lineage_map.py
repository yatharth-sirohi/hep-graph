"""Layout of the whole doctoral forest.

The layout is what the map draws, so the properties that matter are the ones a
reader would notice: generations read downward, a person never sits above
someone they descend from, separate families do not overlap, and nobody is
dropped.
"""

from __future__ import annotations

import pytest

from hepgraph.lineage_map import COLUMN, ROW, build_layout
from hepgraph.pipeline import PipelineError


def by_id(nodes):
    return {node["id"]: node for node in nodes}


def test_generation_is_the_longest_path_not_the_shortest():
    """4 descends from 1 two ways; it must sit below the deeper line."""
    nodes, _ = build_layout([(1, 2), (2, 4), (1, 4)])
    found = by_id(nodes)
    assert found[1]["generation"] == 0
    assert found[2]["generation"] == 1
    # Shortest path from 1 is one step, longest is two; two is what reads right.
    assert found[4]["generation"] == 2


def test_every_person_in_an_edge_is_placed():
    edges = [(1, 2), (3, 4), (5, 6), (6, 7)]
    nodes, _ = build_layout(edges)
    assert {node["id"] for node in nodes} == {1, 2, 3, 4, 5, 6, 7}


def test_separate_families_get_separate_components_and_do_not_overlap():
    nodes, _ = build_layout([(1, 2), (10, 11), (20, 21)])
    found = by_id(nodes)
    assert len({found[1]["component"], found[10]["component"], found[20]["component"]}) == 3
    # Roots of different families sit at different columns on the same row.
    roots = [found[1], found[10], found[20]]
    assert len({node["x"] for node in roots}) == 3
    assert len({node["y"] for node in roots}) == 1


def test_component_size_counts_the_whole_family():
    nodes, _ = build_layout([(1, 2), (2, 3), (9, 8)])
    found = by_id(nodes)
    assert found[1]["component_size"] == 3
    assert found[9]["component_size"] == 2


def test_a_parent_is_centred_over_its_children():
    nodes, _ = build_layout([(1, 2), (1, 3), (1, 4)])
    found = by_id(nodes)
    children = sorted(found[child]["x"] for child in (2, 3, 4))
    assert found[1]["x"] == pytest.approx((children[0] + children[-1]) / 2, abs=COLUMN)


def test_generations_are_rows_a_fixed_distance_apart():
    nodes, _ = build_layout([(1, 2), (2, 3)])
    found = by_id(nodes)
    assert found[2]["y"] - found[1]["y"] == ROW
    assert found[3]["y"] - found[2]["y"] == ROW


def test_bounds_cover_every_node():
    edges = [(i, i + 1000) for i in range(1, 60)] + [(1, 2), (2, 3)]
    nodes, bounds = build_layout(edges)
    assert bounds["width"] >= max(node["x"] for node in nodes)
    assert bounds["height"] >= max(node["y"] for node in nodes)


def test_a_cycle_is_refused_rather_than_silently_dropping_people():
    """The overlay validator rules this out; the layout must not paper over it."""
    with pytest.raises(PipelineError, match="cycle"):
        build_layout([(1, 2), (2, 3), (3, 1)])


def test_multiple_advisers_keep_one_position_each():
    """A person with two advisers is one node, not one per line of descent."""
    nodes, _ = build_layout([(1, 3), (2, 3)])
    assert sum(1 for node in nodes if node["id"] == 3) == 1
    found = by_id(nodes)
    assert found[3]["generation"] == 1
    assert found[1]["component"] == found[2]["component"] == found[3]["component"]
