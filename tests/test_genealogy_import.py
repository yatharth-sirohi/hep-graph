"""Adviser extraction and the genealogy overlay load.

The shapes below are taken from real INSPIRE author records, including the
common case of an adviser recorded only as a name with no record behind it.
"""

from __future__ import annotations

import os

import pytest

from hepgraph.genealogy_import import (GenealogyShardWorker, SCHEMA,
                                       advisers_from_hit, run)

psycopg = pytest.importorskip("psycopg")

URL = os.environ.get("HEPGRAPH_FAST_IMPORT_TEST_URL")


def hit(recid, advisors):
    return {"metadata": {"control_number": recid, "advisors": advisors}}


def ref(identifier):
    return {"$ref": f"https://inspirehep.net/api/authors/{identifier}"}


# ------------------------------------------------------------------ extraction

def test_linked_advisers_are_extracted_with_degree_and_curation():
    student, linked, unlinkable = advisers_from_hit(hit(1013263, [
        {"degree_type": "phd", "record": ref(1005901), "name": "Hirsch, Andrew S."},
        {"degree_type": "phd", "record": ref(1030132), "name": "Scharenberg, Rolf P.",
         "curated_relation": True},
    ]))
    assert student == 1013263
    assert unlinkable == 0
    assert [item["adviser_id"] for item in linked] == [1005901, 1030132]
    assert [item["degree"] for item in linked] == ["phd", "phd"]
    assert [item["curated"] for item in linked] == [False, True]


def test_an_adviser_without_a_record_is_counted_not_guessed():
    """A name with no INSPIRE record cannot become an edge; matching it by name
    is exactly the identity guess this project refuses to make."""
    student, linked, unlinkable = advisers_from_hit(hit(1013271, [
        {"degree_type": "phd", "name": "Hassinski, Jacques"},
        {"degree_type": "phd", "record": ref(1012045), "name": "Denegri, Daniel"},
    ]))
    assert unlinkable == 1
    assert [item["adviser_id"] for item in linked] == [1012045]


def test_hidden_advisers_are_dropped():
    _, linked, unlinkable = advisers_from_hit(hit(1, [
        {"degree_type": "phd", "record": ref(2), "hidden": True},
        {"degree_type": "phd", "record": ref(3)},
    ]))
    assert [item["adviser_id"] for item in linked] == [3]
    assert unlinkable == 0


def test_records_without_advisers_are_handled():
    assert advisers_from_hit(hit(5, None)) == (5, [], 0)
    assert advisers_from_hit({"metadata": {"control_number": 6}}) == (6, [], 0)


def test_the_range_query_targets_authors_that_can_yield_an_edge():
    worker = GenealogyShardWorker.__new__(GenealogyShardWorker)
    query = worker.range_query(1, 500)
    assert "control_number:[1 TO 500]" in query
    assert "advisors.record.$ref:*" in query
    assert GenealogyShardWorker.COLLECTION == "authors"


# ------------------------------------------------------------------ persistence

@pytest.mark.skipif(not URL, reason="HEPGRAPH_FAST_IMPORT_TEST_URL is not set")
def test_a_crawl_loads_only_doctoral_edges(monkeypatch):
    import hepgraph.fast_compact_import as module

    ADVISED = {
        100: [{"degree_type": "phd", "record": ref(900)}],
        101: [{"degree_type": "phd", "record": ref(900), "curated_relation": True},
              {"degree_type": "master", "record": ref(901)}],
        102: [{"degree_type": "master", "record": ref(902)}],
        103: [{"degree_type": "phd", "record": ref(103)}],  # self-reference
    }

    class Fake:
        def fetch(self, collection, query, page, size, sort=None):
            assert collection == "authors"
            body = query.split("control_number:[", 1)[1].rstrip("]")
            low, high = (int(part) for part in body.split(" TO "))
            window = [k for k in sorted(ADVISED) if low <= k <= high]
            if size == 1:
                return {"hits": {"total": len(window), "hits": []}}
            chunk = window[(page - 1) * size: page * size]
            return {"hits": {"total": len(window),
                             "hits": [hit(k, ADVISED[k]) for k in chunk]}}

    monkeypatch.setattr(module, "_PacedClient", lambda limiter: Fake())
    connection = psycopg.connect(URL, autocommit=True, row_factory=psycopg.rows.dict_row)
    for table in ("graph_genealogy_edge", "graph_genealogy_overlay",
                  "inspire_compact_membership", "inspire_compact_work",
                  "inspire_compact_shard", "inspire_compact_import"):
        connection.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
    connection.execute(module.SCHEMA)
    connection.execute(SCHEMA)

    run(URL, import_id="gen-test", overlay_id="gen-overlay", low=1, high=200,
        workers=2, rate=0, phd_only=True)

    rows = connection.execute(
        "SELECT adviser_id, student_id, degree, curated, source_record "
        "FROM graph_genealogy_edge ORDER BY student_id, adviser_id").fetchall()
    found = [(r["adviser_id"], r["student_id"], r["degree"], r["curated"]) for r in rows]
    # Only doctoral relations, and never the self-reference.
    assert found == [(900, 100, "phd", False), (900, 101, "phd", True)]
    assert rows[0]["source_record"] == "100"
    connection.close()
