"""Doctoral lineage as it is served: degree rule, direction, depth, provenance.

The load-bearing test is ``test_only_doctoral_relations_are_traversable``. The
overlay stores every supervision relation INSPIRE records, so a missing degree
filter would quietly route physicists to each other through a master's project
while the interface says the tie is doctoral.
"""

from __future__ import annotations

import os

import pytest

from hepgraph.genealogy_validation import GenealogyOverlayValidator
from hepgraph.graph import Filters
from hepgraph.graph_database_mode import DatabaseGraphService, DatabaseModeConfig
from hepgraph.graph_hydration import Hydrator
from hepgraph.neon_compact_import import SCHEMA as COMPACT_SCHEMA
from hepgraph.genealogy_import import SCHEMA as OVERLAY_SCHEMA
from hepgraph.neon_graph_provider import (CoverageClaim, GenealogyOverlay,
                                          NeonCompactGraphProvider)

psycopg = pytest.importorskip("psycopg")

URL = os.environ.get("HEPGRAPH_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not URL, reason="HEPGRAPH_TEST_DATABASE_URL is not set")

IMPORT_ID = "lineage-test"
OVERLAY_ID = "lineage-overlay"

# A four-generation doctoral line, one master's relation that must never be
# traversed, and a second adviser so the shape is a graph, not a tree.
#            40
#           /  \
#         30    31        (30 and 31 both advised 20)
#           \  /
#            20
#            |
#            10
EDGES = [
    (30, 20, "phd"), (31, 20, "phd"), (40, 30, "phd"), (20, 10, "phd"),
    (99, 10, "master"),
]


class Names:
    def fetch(self, collection, query, page=1, size=25, **kwargs):
        ids = [t for t in query.replace("control_number:", "").replace(" OR ", " ").split()
               if t.isdigit()]
        return {"hits": {"hits": [{"metadata": {"control_number": int(i),
                                                "name": {"value": f"Person {i}"}}} for i in ids],
                         "total": len(ids)}}

    search = fetch


@pytest.fixture(scope="module")
def database():
    connection = psycopg.connect(URL, autocommit=True, row_factory=psycopg.rows.dict_row)
    for table in ("graph_search_job", "graph_genealogy_edge", "graph_genealogy_overlay",
                  "graph_genealogy_quarantine",
                  "inspire_compact_membership", "inspire_compact_work",
                  "inspire_compact_shard", "inspire_compact_import"):
        connection.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
    connection.execute(COMPACT_SCHEMA)
    connection.execute(OVERLAY_SCHEMA)
    connection.execute(
        "INSERT INTO inspire_compact_import(import_id,source_cutoff,low_recid,high_recid,status) "
        "VALUES (%s, now(), 1, 100, 'FETCHING')", (IMPORT_ID,))
    connection.execute(
        "INSERT INTO inspire_compact_shard(import_id,low_recid,high_recid,status,"
        "expected_records,received_records) VALUES (%s,1,100,'DONE',5,5)", (IMPORT_ID,))
    connection.execute(
        "INSERT INTO graph_genealogy_overlay(overlay_id,source_description,source_cutoff) "
        "VALUES (%s,'test', now())", (OVERLAY_ID,))
    for adviser, student, degree in EDGES:
        connection.execute(
            "INSERT INTO graph_genealogy_edge(overlay_id,adviser_id,student_id,source_record,"
            "degree,curated) VALUES (%s,%s,%s,%s,%s,%s)",
            (OVERLAY_ID, adviser, student, str(student), degree, degree == "phd"))
    yield connection
    connection.close()


def service(database, *, overlay=True):
    config = DatabaseModeConfig(url="unused", import_id=IMPORT_ID,
                                overlay_id=OVERLAY_ID if overlay else None,
                                certified_complete=True, overlay_certified=True)
    client = Names()
    return DatabaseGraphService(config, client=client, connection=database,
                                hydrator=Hydrator(client))


def provider(database):
    return NeonCompactGraphProvider(
        database, coverage=CoverageClaim(import_id=IMPORT_ID, certified_complete=True, reason=""),
        genealogy_overlay=GenealogyOverlay(OVERLAY_ID, certified_complete=True))


# --------------------------------------------------------------- the degree rule

def test_only_doctoral_relations_are_traversable(database):
    """A master's relation must not become a route hop."""
    found = provider(database).get_neighbors("10", Filters(max_authors=10, genealogy=True))
    assert "20" in found.members       # doctoral adviser
    assert "99" not in found.members   # master's supervisor


def test_evidence_refs_exclude_non_doctoral_relations(database):
    graph = provider(database)
    filters = Filters(max_authors=10, genealogy=True)
    assert graph.get_edge_evidence_refs("10", "20", filters) == ("phd:10",)
    assert graph.get_edge_evidence_refs("10", "99", filters) == ()


def test_a_person_known_only_by_a_masters_relation_is_not_in_the_graph(database):
    graph = provider(database)
    assert graph.resolve_author("40") is not None   # doctoral adviser
    assert graph.resolve_author("99") is None       # master's only


# ------------------------------------------------------------------- lineage

def test_ancestors_walk_several_generations(database):
    found = service(database).ancestry("10", Filters(), direction="ancestors", depth=4)
    assert found["status"] == "ok"
    by_generation = {p["id"]: p["generation"] for p in found["people"]}
    assert by_generation["20"] == 1
    assert by_generation["30"] == 2 and by_generation["31"] == 2
    assert by_generation["40"] == 3
    assert "99" not in by_generation


def test_multiple_advisers_are_both_returned(database):
    """Supervision is a graph: one person can have two advisers."""
    found = service(database).ancestry("20", Filters(), direction="ancestors", depth=1)
    assert sorted(p["id"] for p in found["people"]) == ["30", "31"]
    assert all(edge["student"] == "20" for edge in found["edges"])


def test_descendants_walk_the_other_way(database):
    found = service(database).ancestry("40", Filters(), direction="descendants", depth=3)
    by_generation = {p["id"]: p["generation"] for p in found["people"]}
    assert by_generation == {"30": 1, "20": 2, "10": 3}
    assert all(edge["adviser"] != edge["student"] for edge in found["edges"])


def test_depth_bounds_the_walk(database):
    shallow = service(database).ancestry("10", Filters(), direction="ancestors", depth=1)
    assert [p["id"] for p in shallow["people"]] == ["20"]
    assert shallow["depth"] == 1
    # Beyond the ceiling the request is clamped, not honoured or refused.
    deep = service(database).ancestry("10", Filters(), direction="ancestors", depth=99)
    assert deep["depth"] == DatabaseGraphService.MAX_LINEAGE_DEPTH


def test_lineage_people_are_named_and_edges_carry_provenance(database):
    found = service(database).ancestry("10", Filters(), direction="ancestors", depth=2)
    assert found["person"]["name"] == "Person 10"
    assert {p["name"] for p in found["people"]} == {"Person 20", "Person 30", "Person 31"}
    edge = found["edges"][0]
    assert edge["degree"] == "phd" and edge["curated"] is True
    assert edge["source_record"]


def test_an_unknown_person_is_not_found_without_a_negative_claim(database):
    found = service(database).ancestry("424242", Filters())
    assert found["status"] == "not_found"
    assert "not evidence" in found["message"]


def test_lineage_is_unavailable_without_an_overlay(database):
    found = service(database, overlay=False).ancestry("10", Filters())
    assert found["status"] == "unavailable"
    assert found["people"] == [] and found["edges"] == []


def test_profile_lists_direct_advisers_and_students(database):
    profile = service(database).person("20", Filters(max_authors=10, genealogy=True))
    assert sorted(item["adviser"] for item in profile["advisers"]) == ["30", "31"]
    assert [item["student"] for item in profile["students"]] == ["10"]


# ----------------------------------------------------------------- validation

def test_the_overlay_validator_passes_on_a_sound_overlay(database):
    report = GenealogyOverlayValidator(database, OVERLAY_ID, import_id=IMPORT_ID).validate()
    assert report.passed is True, report.as_dict()
    assert report.limitations


def test_the_validator_reports_an_unfinished_crawl(database):
    database.execute(
        "INSERT INTO inspire_compact_shard(import_id,low_recid,high_recid,status) "
        "VALUES (%s,101,200,'PENDING') ON CONFLICT DO NOTHING", (IMPORT_ID,))
    try:
        report = GenealogyOverlayValidator(database, OVERLAY_ID, import_id=IMPORT_ID).validate()
        assert report.passed is False
        assert "crawl_reconciled" in [item.name for item in report.failures()]
    finally:
        database.execute("DELETE FROM inspire_compact_shard WHERE import_id=%s AND low_recid=101",
                         (IMPORT_ID,))


def test_a_contradictory_thesis_loop_fails_validation_and_is_quarantined(database):
    """Two theses naming each other as supervisor: the newer record is withdrawn, not deleted."""
    from hepgraph.genealogy_import import quarantine_cycles

    rows = [(10, 40, "2830917"), (40, 10, "2897779")]  # 10 already descends from 40
    for adviser, student, record in rows:
        database.execute(
            "INSERT INTO graph_genealogy_edge(overlay_id,adviser_id,student_id,source_record,"
            "degree,source_kind) VALUES (%s,%s,%s,%s,'phd','thesis')",
            (OVERLAY_ID, adviser, student, record))
    try:
        report = GenealogyOverlayValidator(database, OVERLAY_ID, import_id=IMPORT_ID).validate()
        assert "lineage_acyclic" in [item.name for item in report.failures()]

        withdrawn = quarantine_cycles(database, OVERLAY_ID)
        assert len(withdrawn) >= 1
        assert GenealogyOverlayValidator(database, OVERLAY_ID, import_id=IMPORT_ID) \
            .check_lineage_acyclic().passed
        kept = database.execute(
            "SELECT count(*) AS n FROM graph_genealogy_quarantine WHERE overlay_id=%s",
            (OVERLAY_ID,)).fetchone()["n"]
        assert kept == len(withdrawn)
        # The sound, single-source author-profile lineage is never what gets withdrawn.
        assert all(item["source_record"] in {"2830917", "2897779"} for item in withdrawn)
    finally:
        database.execute("DELETE FROM graph_genealogy_edge WHERE overlay_id=%s "
                         "AND source_kind='thesis'", (OVERLAY_ID,))
        database.execute("DELETE FROM graph_genealogy_quarantine WHERE overlay_id=%s", (OVERLAY_ID,))


def test_a_thesis_relation_links_to_the_thesis_not_an_author_profile(database):
    """Evidence must point at the record that actually states the supervision."""
    database.execute(
        "INSERT INTO graph_genealogy_edge(overlay_id,adviser_id,student_id,source_record,"
        "degree,source_kind) VALUES (%s,41,10,'2830917','phd','thesis')", (OVERLAY_ID,))
    try:
        profile = service(database).person("10", Filters(max_authors=10, genealogy=True))
        thesis = next(item for item in profile["advisers"] if item["adviser"] == "41")
        assert thesis["source_kind"] == "thesis"
        assert thesis["source_url"] == "https://inspirehep.net/literature/2830917"
        profile_sourced = next(item for item in profile["advisers"] if item["adviser"] == "20")
        assert profile_sourced["source_url"] == "https://inspirehep.net/authors/10"
        walk = service(database).ancestry("10", Filters(), direction="ancestors", depth=1)
        kinds = {edge["adviser"]: edge["source_kind"] for edge in walk["edges"]}
        assert kinds["41"] == "thesis" and kinds["20"] == "author_profile"
    finally:
        database.execute("DELETE FROM graph_genealogy_edge WHERE overlay_id=%s AND adviser_id=41",
                         (OVERLAY_ID,))


def test_an_adviser_inspire_left_untyped_is_still_an_adviser(database):
    """INSPIRE writes 'other' when it did not record the degree, not 'not a doctorate'.

    Treating that as no relation hid an adviser from 12,518 people, so 'other'
    and untyped are traversable; a master's relation still is not.
    """
    database.execute(
        "INSERT INTO graph_genealogy_edge(overlay_id,adviser_id,student_id,source_record,degree)"
        " VALUES (%s,42,10,'10','other'), (%s,43,10,'10',NULL)", (OVERLAY_ID, OVERLAY_ID))
    try:
        profile = service(database).person("10", Filters(max_authors=10, genealogy=True))
        advisers = {item["adviser"] for item in profile["advisers"]}
        assert {"42", "43"} <= advisers
        assert "99" not in advisers  # the master's relation stays out
        walk = service(database).ancestry("10", Filters(), direction="ancestors", depth=1)
        assert {edge["adviser"] for edge in walk["edges"]} >= {"42", "43"}
    finally:
        database.execute("DELETE FROM graph_genealogy_edge WHERE overlay_id=%s "
                         "AND adviser_id IN (42,43)", (OVERLAY_ID,))


def test_a_loop_withdraws_the_weaker_claim_not_the_explicit_doctorate(database):
    """INSPIRE typed one direction 'phd' and the reverse not at all; keep the doctorate."""
    from hepgraph.genealogy_import import quarantine_cycles

    database.execute(
        "INSERT INTO graph_genealogy_edge(overlay_id,adviser_id,student_id,source_record,degree)"
        " VALUES (%s,51,52,'52','phd'), (%s,52,51,'51','other')", (OVERLAY_ID, OVERLAY_ID))
    try:
        withdrawn = quarantine_cycles(database, OVERLAY_ID)
        assert [(item["adviser"], item["student"]) for item in withdrawn] == [(52, 51)]
        kept = database.execute(
            "SELECT degree FROM graph_genealogy_edge WHERE overlay_id=%s AND adviser_id=51 "
            "AND student_id=52", (OVERLAY_ID,)).fetchone()
        assert kept["degree"] == "phd"
    finally:
        database.execute("DELETE FROM graph_genealogy_edge WHERE overlay_id=%s "
                         "AND adviser_id IN (51,52)", (OVERLAY_ID,))
        database.execute("DELETE FROM graph_genealogy_quarantine WHERE overlay_id=%s", (OVERLAY_ID,))


def test_a_faculty_is_not_an_adviser_but_a_mislabelled_person_still_is(database):
    """INSPIRE author records built from thesis metadata include non-people."""
    from hepgraph.genealogy_import import quarantine_non_people

    database.execute(
        "INSERT INTO graph_genealogy_person(overlay_id,person_id,name) VALUES "
        "(%s,61,'Fizyki, Wydział'), (%s,62,'Quadt, Betreuer: Arnulf'), (%s,63,'Advisor(s)') "
        "ON CONFLICT DO NOTHING", (OVERLAY_ID, OVERLAY_ID, OVERLAY_ID))
    database.execute(
        "INSERT INTO graph_genealogy_edge(overlay_id,adviser_id,student_id,source_record,degree)"
        " VALUES (%s,61,10,'t1','phd'), (%s,62,10,'t2','phd'), (%s,63,10,'t3','phd')",
        (OVERLAY_ID, OVERLAY_ID, OVERLAY_ID))
    try:
        summary = quarantine_non_people(database, OVERLAY_ID)
        assert summary["relations_withdrawn"] == 2 and summary["names_cleaned"] == 1

        advisers = {item["adviser"] for item in
                    service(database).person("10", Filters(max_authors=10, genealogy=True))["advisers"]}
        assert "62" in advisers                      # Arnulf Quadt keeps his student
        assert {"61", "63"}.isdisjoint(advisers)     # a faculty and a form heading do not
        assert database.execute(
            "SELECT name FROM graph_genealogy_person WHERE overlay_id=%s AND person_id=62",
            (OVERLAY_ID,)).fetchone()["name"] == "Quadt, Arnulf"
        assert database.execute(
            "SELECT count(*) AS n FROM graph_genealogy_quarantine WHERE overlay_id=%s",
            (OVERLAY_ID,)).fetchone()["n"] == 2
    finally:
        database.execute("DELETE FROM graph_genealogy_edge WHERE overlay_id=%s "
                         "AND adviser_id IN (61,62,63)", (OVERLAY_ID,))
        database.execute("DELETE FROM graph_genealogy_person WHERE overlay_id=%s "
                         "AND person_id IN (61,62,63)", (OVERLAY_ID,))
        database.execute("DELETE FROM graph_genealogy_quarantine WHERE overlay_id=%s", (OVERLAY_ID,))


# --------------------------------------------------------------- relationships

def test_two_students_of_one_adviser_are_academic_siblings(database):
    """40 advised 30; give it a second student and the two become siblings."""
    database.execute(
        "INSERT INTO graph_genealogy_edge(overlay_id,adviser_id,student_id,source_record,degree)"
        " VALUES (%s,40,31,'31','phd')", (OVERLAY_ID,))
    try:
        found = service(database).relationship("30", "31", Filters())
        assert found["status"] == "ok"
        assert found["label"] == "academic siblings"
        assert found["meeting_point"] == "40"
        assert found["distances"] == [1, 1]
    finally:
        database.execute("DELETE FROM graph_genealogy_edge WHERE overlay_id=%s "
                         "AND adviser_id=40 AND student_id=31", (OVERLAY_ID,))


def test_a_direct_line_is_named_by_generation(database):
    found = service(database).relationship("10", "40", Filters())
    assert found["status"] == "ok"
    # 10 is three supervisions below 40, and the name is read from 10's side.
    assert found["label"] == "academic great-grandstudent"
    assert found["distances"] == [3, 0]
    assert [step["adviser"] for step in found["chain"]] == ["20", "30", "40"]

    back = service(database).relationship("40", "10", Filters())
    assert back["label"] == "academic great-grandadviser"


def test_cousins_meet_at_their_nearest_shared_ancestor(database):
    """30 and 31 both descend from 40; their students are first cousins."""
    database.execute(
        "INSERT INTO graph_genealogy_edge(overlay_id,adviser_id,student_id,source_record,degree)"
        " VALUES (%s,40,31,'31','phd'), (%s,31,70,'70','phd'), (%s,30,71,'71','phd')",
        (OVERLAY_ID, OVERLAY_ID, OVERLAY_ID))
    try:
        found = service(database).relationship("70", "71", Filters())
        assert found["status"] == "ok"
        assert found["label"] == "academic first cousins"
        assert found["meeting_point"] == "40"
        assert {step["student"] for step in found["chain"]} == {"70", "71", "30", "31"}
    finally:
        database.execute("DELETE FROM graph_genealogy_edge WHERE overlay_id=%s "
                         "AND student_id IN (70,71) OR overlay_id=%s AND student_id=31",
                         (OVERLAY_ID, OVERLAY_ID))


def test_unrelated_people_are_told_the_records_are_silent_not_that_they_are_strangers(database):
    database.execute(
        "INSERT INTO graph_genealogy_edge(overlay_id,adviser_id,student_id,source_record,degree)"
        " VALUES (%s,80,81,'81','phd')", (OVERLAY_ID,))
    try:
        found = service(database).relationship("10", "81", Filters())
        assert found["status"] == "no_relation"
        assert found["label"] == "no recorded relation"
        assert "describes the records" in found["explanation"]
        assert found["chain"] == []
    finally:
        database.execute("DELETE FROM graph_genealogy_edge WHERE overlay_id=%s AND adviser_id=80",
                         (OVERLAY_ID,))


def test_a_person_with_no_adviser_record_is_unknown_not_unrelated(database):
    found = service(database).relationship("10", "424242", Filters())
    assert found["status"] == "not_found"
    assert "not evidence that none exists" in found["message"]


def test_the_chain_carries_the_evidence_for_every_step(database):
    found = service(database).relationship("10", "40", Filters())
    for step in found["chain"]:
        assert step["source_url"].startswith("http")
        assert step["source_kind"]



def test_a_named_relationship_is_walked_from_the_first_person_to_the_second(database):
    """Direction on every step: an ancestor reads downward, a student upward."""
    down = service(database).relationship("40", "10", Filters())
    assert [step["direction"] for step in down["chain"]] == ["down", "down", "down"]
    assert [step["adviser"] for step in down["chain"]] == ["40", "30", "20"]

    up = service(database).relationship("10", "40", Filters())
    assert [step["direction"] for step in up["chain"]] == ["up", "up", "up"]
    assert [step["student"] for step in up["chain"]] == ["10", "20", "30"]
