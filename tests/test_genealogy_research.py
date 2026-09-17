"""Web-researched leads: what may be stored, and what a lead must carry.

These leads come from weaker models reading the open web, so the tests are
about refusing what cannot be checked rather than about happy paths.
"""

from __future__ import annotations

import json
import os

import pytest

from hepgraph.genealogy_research import (Lead, SCHEMA, record, record_miss, targets)
from hepgraph.genealogy_import import SCHEMA as OVERLAY_SCHEMA
from hepgraph.lineage_map import SCHEMA as LAYOUT_SCHEMA

psycopg = pytest.importorskip("psycopg")

URL = os.environ.get("HEPGRAPH_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not URL, reason="HEPGRAPH_TEST_DATABASE_URL is not set")

OVERLAY = "research-overlay"
GOOD = dict(evidence_url="https://example.edu/thesis/1",
            evidence_quote="Thesis submitted under the supervision of A. Adviser, 1998.",
            corroboration="Same institution and years as INSPIRE record 30; adviser's INSPIRE "
                          "profile lists the department.",
            confidence="high")


@pytest.fixture()
def database():
    connection = psycopg.connect(URL, autocommit=True, row_factory=psycopg.rows.dict_row)
    for table in ("graph_genealogy_research", "graph_genealogy_research_miss",
                  "graph_lineage_layout", "graph_genealogy_person"):
        connection.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
    connection.execute(OVERLAY_SCHEMA)
    connection.execute(LAYOUT_SCHEMA)
    connection.execute(SCHEMA)
    connection.execute("INSERT INTO graph_genealogy_overlay(overlay_id,source_description,"
                       "source_cutoff) VALUES (%s,'test',now()) ON CONFLICT DO NOTHING", (OVERLAY,))
    connection.execute("DELETE FROM graph_genealogy_edge WHERE overlay_id=%s", (OVERLAY,))
    connection.execute(
        "INSERT INTO graph_genealogy_edge(overlay_id,adviser_id,student_id,source_record,degree)"
        " VALUES (%s,30,20,'20','phd')", (OVERLAY,))
    connection.execute(
        "INSERT INTO graph_genealogy_edge(overlay_id,adviser_id,student_id,source_record,degree)"
        " VALUES (%s,40,50,'50','phd')", (OVERLAY,))
    for identifier, size, generation in ((20, 2, 1), (30, 2, 0), (40, 1, 0)):
        connection.execute(
            "INSERT INTO graph_lineage_layout(overlay_id,person_id,x,y,generation,component,"
            "component_size) VALUES (%s,%s,0,0,%s,1,%s)",
            (OVERLAY, identifier, generation, size))
    yield connection
    connection.close()


def test_a_lead_needs_a_url_a_quote_and_corroboration():
    assert Lead(20, 30, **GOOD).problems() == []
    bare = Lead(20, 30, evidence_url="probably a paper", evidence_quote="advisor",
                corroboration="same name", confidence="certain")
    assert len(bare.problems()) == 4


def test_a_person_may_not_be_their_own_adviser():
    assert "a person cannot be their own adviser" in Lead(20, 20, **GOOD).problems()


def test_a_refused_lead_is_not_written(database):
    result = record(database, Lead(20, 20, **GOOD), researcher="haiku", overlay_id=OVERLAY)
    assert result["stored"] is False and result["problems"]
    assert database.execute("SELECT count(*) AS n FROM graph_genealogy_research").fetchone()["n"] == 0


def test_a_relation_inspire_already_records_is_not_re_researched(database):
    result = record(database, Lead(20, 30, **GOOD), researcher="haiku", overlay_id=OVERLAY)
    assert result["problems"] == ["INSPIRE already records this relation"]


def test_a_sound_lead_is_stored_pending_and_never_becomes_an_inspire_edge(database):
    assert record(database, Lead(40, 30, **GOOD), researcher="haiku", overlay_id=OVERLAY)["stored"]
    row = database.execute("SELECT status, researcher FROM graph_genealogy_research").fetchone()
    assert row["status"] == "pending" and row["researcher"] == "haiku"
    assert database.execute(
        "SELECT count(*) AS n FROM graph_genealogy_edge WHERE overlay_id=%s", (OVERLAY,)
    ).fetchone()["n"] == 2


def test_targets_are_people_without_a_doctoral_adviser_busiest_first(database):
    found = targets(database, OVERLAY, limit=10)
    # 20 and 50 already have advisers; 30 outranks 40 on the size of its family.
    assert [item["student_id"] for item in found] == [30, 40]
    assert found[0]["descendants"] == 1


def test_a_person_already_researched_is_not_handed_out_again(database):
    record(database, Lead(40, 30, **GOOD), researcher="haiku", overlay_id=OVERLAY)
    record_miss(database, 30, researcher="haiku", note="no source names an adviser",
                overlay_id=OVERLAY)
    assert targets(database, OVERLAY, limit=10) == []


def test_ingest_counts_what_it_refused_rather_than_dropping_it(database):
    from hepgraph.genealogy_research import ingest
    lines = [
        json.dumps({"student_id": 40, "adviser_id": 30, **GOOD}),
        json.dumps({"student_id": 30, "not_found": True, "note": "no source names an adviser"}),
        json.dumps({"student_id": 20, "adviser_id": 30, **GOOD}),          # INSPIRE knows it
        json.dumps({"student_id": 41, "adviser_id": 42, "evidence_url": "hearsay",
                    "evidence_quote": "x", "corroboration": "y", "confidence": "sure"}),
        "{not json at all",
    ]
    summary = ingest(database, lines, researcher="haiku", overlay_id=OVERLAY)
    assert summary["stored"] == 1 and summary["missed"] == 1
    assert len(summary["refused"]) == 3
    assert database.execute(
        "SELECT count(*) AS n FROM graph_genealogy_research").fetchone()["n"] == 1
