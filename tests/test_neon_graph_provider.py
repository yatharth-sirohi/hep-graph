"""Integration tests for the pinned compact graph provider.

These run against a real PostgreSQL because the provider's whole job is SQL
semantics: array parameters, the qualifying-work join and NULL-year handling
cannot be proven against a mock.  Point ``HEPGRAPH_TEST_DATABASE_URL`` at a
throwaway database; the suite skips when none is configured so the rest of the
project still runs without a server.
"""

from __future__ import annotations

import os

import pytest

from hepgraph.graph import Filters
from hepgraph.hlbes import COMPLETE, PARTIAL, UNKNOWN
from hepgraph.neon_compact_import import SCHEMA
from hepgraph.neon_graph_provider import (CoverageClaim, GenealogyOverlay,
                                          GraphDatabaseError,
                                          NeonCompactGraphProvider, observe_coverage)

psycopg = pytest.importorskip("psycopg")

URL = os.environ.get("HEPGRAPH_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not URL, reason="HEPGRAPH_TEST_DATABASE_URL is not set")

IMPORT_ID = "test-import"
OVERLAY_ID = "test-overlay"

# (work_id, year, author_count, members)
WORKS = (
    # A small-team chain: 1-2 share two works, 2-3 share one.
    (101, 2001, 3, (1, 2, 9)),
    (102, 2005, 2, (1, 2)),
    (103, 2010, 4, (2, 3, 8, 9)),
    # 3-4 share one work with an unknown year.
    (104, None, 2, (3, 4)),
    # A large collaboration: excluded from small-team mode by author_count.
    (105, 2015, 500, (4, 5, 6)),
    # An author whose only work is large-team, so small-team mode must still
    # report them as present with an empty neighborhood, not unknown.
    (106, 2016, 800, (6, 7)),
)


def _connect():
    connection = psycopg.connect(URL, autocommit=True)
    connection.execute("SET statement_timeout = '15s'")
    return connection


@pytest.fixture(scope="module")
def database():
    connection = _connect()
    connection.execute("DROP TABLE IF EXISTS graph_genealogy_edge")
    connection.execute("DROP TABLE IF EXISTS graph_genealogy_overlay")
    connection.execute("DROP TABLE IF EXISTS inspire_compact_membership")
    connection.execute("DROP TABLE IF EXISTS inspire_compact_work")
    connection.execute("DROP TABLE IF EXISTS inspire_compact_shard")
    connection.execute("DROP TABLE IF EXISTS inspire_compact_import")
    connection.execute(SCHEMA)
    from pathlib import Path

    import hepgraph

    connection.execute((Path(hepgraph.__path__[0]) / "sql" / "genealogy_overlay.sql").read_text())
    connection.execute(
        "INSERT INTO inspire_compact_import(import_id,source_cutoff,low_recid,high_recid,status) "
        "VALUES (%s, now(), 100, 200, 'FETCHING')", (IMPORT_ID,))
    connection.execute(
        "INSERT INTO inspire_compact_shard(import_id,low_recid,high_recid,status,expected_records,"
        "received_records) VALUES (%s,100,200,'DONE',6,6)", (IMPORT_ID,))
    for work_id, year, author_count, members in WORKS:
        connection.execute(
            "INSERT INTO inspire_compact_work(import_id,work_id,year,author_count,member_count,"
            "retrieved_at) VALUES (%s,%s,%s,%s,%s, now())",
            (IMPORT_ID, work_id, year, author_count, len(members)))
        for author_id in members:
            connection.execute(
                "INSERT INTO inspire_compact_membership(import_id,work_id,author_id) "
                "VALUES (%s,%s,%s)", (IMPORT_ID, work_id, author_id))
    connection.execute(
        "INSERT INTO graph_genealogy_overlay(overlay_id,source_description,source_cutoff,"
        "certified_complete) VALUES (%s,'test','2026-01-01T00:00:00+00:00', TRUE)", (OVERLAY_ID,))
    connection.execute(
        "INSERT INTO graph_genealogy_edge(overlay_id,adviser_id,student_id,source_record) "
        "VALUES (%s,1,7,'rec-17')", (OVERLAY_ID,))
    yield connection
    connection.close()


def provider(database, *, certified=False, overlay=None, budget=2_000_000):
    claim = CoverageClaim(import_id=IMPORT_ID, source_cutoff="2026-09-16T00:00:00+00:00",
                          declared_low=100, declared_high=200,
                          certified_complete=certified,
                          reason="" if certified else "import_not_certified")
    return NeonCompactGraphProvider(database, coverage=claim, genealogy_overlay=overlay,
                                    member_visit_budget=budget)


def members(neighborhood):
    return set(neighborhood.members)


# ---------------------------------------------------------------- adjacency

def test_small_team_neighbors_exclude_large_collaborations(database):
    graph = provider(database)
    assert members(graph.get_neighbors("1", Filters(max_authors=10))) == {"2", "9"}
    # 4's only small-team work is 104 with author 3; work 105 has 500 authors.
    assert members(graph.get_neighbors("4", Filters(max_authors=10))) == {"3"}


def test_large_team_mode_selects_the_complementary_works(database):
    graph = provider(database)
    large = Filters(max_authors=None, min_authors=11)
    assert members(graph.get_neighbors("4", large)) == {"5", "6"}
    assert members(graph.get_neighbors("1", large)) == set()


def test_all_mode_unions_both_regimes(database):
    graph = provider(database)
    every = Filters(max_authors=None)
    assert members(graph.get_neighbors("4", every)) == {"3", "5", "6"}


def test_min_shared_counts_distinct_qualifying_works(database):
    graph = provider(database)
    # 1-2 share works 101 and 102; 1-9 share only 101.
    assert members(graph.get_neighbors("1", Filters(max_authors=10, min_shared=2))) == {"2"}
    assert members(graph.get_neighbors("1", Filters(max_authors=10, min_shared=3))) == set()


def test_year_bounds_are_inclusive_and_exclude_unknown_years(database):
    graph = provider(database)
    bounded = Filters(max_authors=10, year_start=2001, year_end=2001)
    assert members(graph.get_neighbors("1", bounded)) == {"2", "9"}
    # Work 104 has no year: excluded whenever a bound is active, kept otherwise.
    assert members(graph.get_neighbors("3", Filters(max_authors=10))) == {"2", "8", "9", "4"}
    assert members(graph.get_neighbors("3", Filters(max_authors=10, year_start=1900))) == {"2", "8", "9"}
    assert members(graph.get_neighbors("3", Filters(max_authors=10, year_end=2100))) == {"2", "8", "9"}


def test_repeated_membership_rows_cannot_double_count(database):
    """The membership primary key is what makes ``count(*)`` a distinct count."""
    with pytest.raises(Exception):
        database.execute(
            "INSERT INTO inspire_compact_membership(import_id,work_id,author_id) VALUES (%s,101,1)",
            (IMPORT_ID,))
    graph = provider(database)
    assert members(graph.get_neighbors("1", Filters(max_authors=10, min_shared=2))) == {"2"}


# ------------------------------------------------------------ proof honesty

def test_absent_author_is_unknown_never_an_empty_complete(database):
    graph = provider(database, certified=True)
    found = graph.get_neighbors("424242", Filters())
    assert found.status == UNKNOWN
    assert found.reason == "author_not_in_import"
    assert not found.members


def test_present_author_with_no_qualifying_work_is_not_unknown(database):
    """Filtered to nothing is an empty neighborhood, not an absent person."""
    graph = provider(database, certified=True)
    found = graph.get_neighbors("7", Filters(max_authors=10, genealogy=False))
    assert found.status == COMPLETE
    assert not found.members


def test_uncertified_import_can_never_report_complete(database):
    graph = provider(database, certified=False)
    found = graph.get_neighbors("1", Filters(max_authors=10, genealogy=False))
    assert found.status == PARTIAL
    assert found.reason == "import_not_certified"
    assert not graph.get_completeness(Filters(genealogy=False))


def test_certified_import_reports_complete_without_genealogy(database):
    graph = provider(database, certified=True)
    assert graph.get_completeness(Filters(genealogy=False))
    assert graph.get_neighbors("1", Filters(max_authors=10, genealogy=False)).status == COMPLETE


def test_genealogy_without_an_overlay_is_partial_not_silently_dropped(database):
    graph = provider(database, certified=True)
    found = graph.get_neighbors("1", Filters(max_authors=10, genealogy=True))
    assert found.status == PARTIAL
    assert found.reason == "genealogy_overlay_uncertified"
    assert not graph.get_completeness(Filters(genealogy=True))


def test_certified_overlay_adds_doctoral_edges_and_restores_completeness(database):
    graph = provider(database, certified=True,
                     overlay=GenealogyOverlay(OVERLAY_ID, certified_complete=True))
    found = graph.get_neighbors("1", Filters(max_authors=10, genealogy=True))
    assert found.status == COMPLETE
    assert members(found) == {"2", "9", "7"}
    # The doctoral edge is traversable in both directions.
    assert "1" in members(graph.get_neighbors("7", Filters(max_authors=10, genealogy=True)))
    # Genealogy off keeps it out of the graph entirely.
    assert "7" not in members(graph.get_neighbors("1", Filters(max_authors=10, genealogy=False)))


def test_budget_exhaustion_degrades_to_partial_and_converges(database):
    graph = provider(database, certified=True, budget=1)
    first = graph.get_neighbors("1", Filters(max_authors=10, genealogy=False))
    second = graph.get_neighbors("1", Filters(max_authors=10, genealogy=False))
    assert first.status == PARTIAL and first.reason == "member_visit_budget_exceeded"
    assert not first.members
    # A repeated call must return the same key so HLBES parks the node.
    assert (first.members, first.status, first.cursor) == (second.members, second.status, second.cursor)


def test_database_failure_raises_and_is_never_an_empty_neighborhood(database):
    class Broken:
        def execute(self, *args, **kwargs):
            raise RuntimeError("connection reset")

    claim = CoverageClaim(import_id=IMPORT_ID, certified_complete=True, reason="")
    graph = NeonCompactGraphProvider(Broken(), coverage=claim)
    with pytest.raises(GraphDatabaseError) as error:
        graph.get_neighbors("1", Filters())
    assert error.value.reason == "database_unavailable"


# ------------------------------------------------------------------ batching

def test_batch_is_two_round_trips_and_matches_single_lookups(database):
    graph = provider(database, certified=True)
    filters = Filters(max_authors=10, genealogy=False)
    before = graph.queries
    batch = graph.get_neighbors_batch(("1", "2", "3", "424242"), filters)
    assert graph.queries - before == 2
    assert batch["424242"].status == UNKNOWN
    single = provider(database, certified=True)
    for author_id in ("1", "2", "3"):
        assert members(batch[author_id]) == members(single.get_neighbors(author_id, filters))


def test_batch_pins_one_version_and_filter_key(database):
    graph = provider(database, certified=True)
    filters = Filters(max_authors=10)
    batch = graph.get_neighbors_batch(("1", "2"), filters)
    assert {found.version for found in batch.values()} == {graph.get_graph_version()}
    assert {found.filter_key for found in batch.values()} == {batch["1"].filter_key}


def test_invalid_author_id_is_unknown_not_an_error(database):
    graph = provider(database, certified=True)
    assert graph.get_neighbors("not-a-number", Filters()).status == UNKNOWN


# ------------------------------------------------------------------ evidence

def test_edge_evidence_is_ordered_stable_and_respects_min_shared(database):
    graph = provider(database, certified=True)
    filters = Filters(max_authors=10, genealogy=False)
    assert graph.get_edge_evidence_refs("1", "2", filters) == ("work:101", "work:102")
    assert graph.get_edge_evidence_refs("2", "1", filters) == ("work:101", "work:102")
    strict = Filters(max_authors=10, min_shared=2, genealogy=False)
    assert graph.get_edge_evidence_refs("1", "9", strict) == ()


def test_edge_evidence_includes_doctoral_records_only_with_genealogy(database):
    graph = provider(database, certified=True,
                     overlay=GenealogyOverlay(OVERLAY_ID, certified_complete=True))
    assert graph.get_edge_evidence_refs("1", "7", Filters(max_authors=10)) == ("phd:rec-17",)
    assert graph.get_edge_evidence_refs("1", "7", Filters(max_authors=10, genealogy=False)) == ()


def test_work_metadata_is_structure_only(database):
    graph = provider(database, certified=True)
    work = graph.get_work_metadata("101")
    assert work == {"id": "101", "year": 2001, "author_count": 3, "resolved_author_count": 3,
                    "source_url": "https://inspirehep.net/literature/101",
                    "details_available": False}
    assert "title" not in work
    assert graph.get_work_metadata("999999") is None


def test_resolve_author_reports_import_membership_only(database):
    graph = provider(database, certified=True)
    assert graph.resolve_author("1")["id"] == "1"
    assert graph.resolve_author("424242") is None


# ------------------------------------------------------------------ coverage

def test_observe_coverage_never_certifies_by_itself(database):
    claim = observe_coverage(database, IMPORT_ID)
    assert claim.import_id == IMPORT_ID
    assert claim.certified_complete is False
    assert claim.reason == "not_certified"
    assert (claim.declared_low, claim.declared_high) == (100, 200)
    assert (claim.observed_low, claim.observed_high) == (101, 106)
    assert claim.works == len(WORKS)


def test_observe_coverage_rejects_an_unknown_import(database):
    with pytest.raises(GraphDatabaseError) as error:
        observe_coverage(database, "no-such-import")
    assert error.value.reason == "unknown_import"
