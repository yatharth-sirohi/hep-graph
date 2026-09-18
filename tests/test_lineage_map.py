"""Layout of the whole doctoral forest.

The layout is what the map draws, so the properties that matter are the ones a
reader would notice: generations read downward, a person never sits above
someone they descend from, separate families do not overlap, and nobody is
dropped.
"""

from __future__ import annotations

import os

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


# ------------------------------------------------------- the served payload

URL = os.environ.get("HEPGRAPH_TEST_DATABASE_URL")


@pytest.mark.skipif(not URL, reason="HEPGRAPH_TEST_DATABASE_URL is not set")
def test_names_ride_alongside_the_nodes_in_the_same_order():
    """65,843 repeated id keys cost ~600 kB against a hard response ceiling."""
    psycopg = pytest.importorskip("psycopg")
    from hepgraph.genealogy_import import SCHEMA as OVERLAY_SCHEMA
    from hepgraph.lineage_map import SCHEMA, read_map, store_layout

    overlay = "map-payload-test"
    connection = psycopg.connect(URL, autocommit=True, row_factory=psycopg.rows.dict_row)
    connection.execute(OVERLAY_SCHEMA)
    connection.execute(SCHEMA)
    connection.execute("INSERT INTO graph_genealogy_overlay(overlay_id,source_description,"
                       "source_cutoff) VALUES (%s,'test',now()) ON CONFLICT DO NOTHING", (overlay,))
    connection.execute("DELETE FROM graph_genealogy_edge WHERE overlay_id=%s", (overlay,))
    connection.execute("DELETE FROM graph_lineage_layout WHERE overlay_id=%s", (overlay,))
    connection.execute("DELETE FROM graph_genealogy_person WHERE overlay_id=%s", (overlay,))
    connection.execute(
        "INSERT INTO graph_genealogy_edge(overlay_id,adviser_id,student_id,source_record,degree)"
        " VALUES (%s,7,8,'8','phd'), (%s,7,9,'9','other')", (overlay, overlay))
    connection.execute("INSERT INTO graph_genealogy_person(overlay_id,person_id,name) "
                       "VALUES (%s,7,'Adviser Seven')", (overlay,))
    nodes, _ = build_layout([(7, 8), (7, 9)])
    store_layout(connection, overlay, nodes)
    try:
        payload = read_map(connection, overlay, "v-test")
        assert isinstance(payload["names"], list)
        assert len(payload["names"]) == len(payload["nodes"]) == 3
        by_id = {node[0]: payload["names"][i] for i, node in enumerate(payload["nodes"])}
        assert by_id[7] == "Adviser Seven"
        assert by_id[8] == "" and by_id[9] == ""   # unnamed, but still placed
        assert payload["counts"]["named"] == 1
        # An 'other' relation is a relation: both students are on the map.
        assert payload["counts"]["relations"] == 2
    finally:
        connection.close()



@pytest.mark.skipif(not URL, reason="HEPGRAPH_TEST_DATABASE_URL is not set")
def test_a_pair_stated_twice_is_drawn_once_with_its_earliest_thesis_year():
    """A profile and a thesis naming the same adviser are one relation."""
    psycopg = pytest.importorskip("psycopg")
    from hepgraph.genealogy_import import SCHEMA as OVERLAY_SCHEMA
    from hepgraph.lineage_map import SCHEMA, read_map, store_layout

    overlay = "map-years-test"
    connection = psycopg.connect(URL, autocommit=True, row_factory=psycopg.rows.dict_row)
    connection.execute(OVERLAY_SCHEMA)
    connection.execute(SCHEMA)
    connection.execute("INSERT INTO graph_genealogy_overlay(overlay_id,source_description,"
                       "source_cutoff) VALUES (%s,'test',now()) ON CONFLICT DO NOTHING", (overlay,))
    for table in ("graph_genealogy_edge", "graph_lineage_layout"):
        connection.execute(f"DELETE FROM {table} WHERE overlay_id=%s", (overlay,))
    connection.execute(
        "INSERT INTO graph_genealogy_edge(overlay_id,adviser_id,student_id,source_record,"
        "degree,year,source_kind) VALUES "
        "(%s,7,8,'8','phd',NULL,'author_profile'), (%s,7,8,'t1','phd',1994,'thesis'), "
        "(%s,7,9,'9','other',NULL,'author_profile')", (overlay, overlay, overlay))
    nodes, _ = build_layout([(7, 8), (7, 9)])
    store_layout(connection, overlay, nodes)
    try:
        payload = read_map(connection, overlay, "v-test")
        assert payload["counts"]["relations"] == 2          # not three
        assert len(payload["years"]) == len(payload["edges"])
        ids = [node[0] for node in payload["nodes"]]
        dated = {(ids[a], ids[b]): year for (a, b), year in zip(payload["edges"], payload["years"])}
        assert dated == {(7, 8): 1994, (7, 9): None}
        assert payload["counts"]["dated"] == 1
    finally:
        connection.close()
