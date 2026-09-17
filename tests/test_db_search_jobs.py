"""Durable job tests: resumption across processes and version pinning.

The proof must survive being written to a row and picked up by a different
engine instance, and it must fail closed rather than mix two graph versions.
"""

from __future__ import annotations

import os

import pytest

from hepgraph.db_search_jobs import (DatabaseSearchJobs, JobPin, classify,
                                     deserialise, serialise)
from hepgraph.graph import Filters
from hepgraph.hlbes import EXACT, NO_PATH, SEARCH_INCOMPLETE, VERIFIED, HLBES
from hepgraph.neon_compact_import import SCHEMA
from hepgraph.neon_graph_provider import (CoverageClaim, GraphDatabaseError,
                                          NeonCompactGraphProvider)
from hepgraph.providers import ProviderOracle

psycopg = pytest.importorskip("psycopg")

URL = os.environ.get("HEPGRAPH_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not URL, reason="HEPGRAPH_TEST_DATABASE_URL is not set")

FILTERS = Filters(max_authors=10, genealogy=False)

# A 1-2-3-4 chain plus an isolated pair 8-9, so a disconnected query is real.
WORKS = ((201, 2001, 2, (1, 2)), (202, 2002, 2, (2, 3)), (203, 2003, 2, (3, 4)),
         (204, 2004, 2, (8, 9)))


def _connect():
    connection = psycopg.connect(URL, autocommit=True, row_factory=psycopg.rows.dict_row)
    connection.execute("SET statement_timeout = '15s'")
    return connection


def _load(connection, import_id):
    connection.execute(
        "INSERT INTO inspire_compact_import(import_id,source_cutoff,low_recid,high_recid,status) "
        "VALUES (%s, now(), 200, 300, 'FETCHING') ON CONFLICT DO NOTHING", (import_id,))
    for work_id, year, count, members in WORKS:
        connection.execute(
            "INSERT INTO inspire_compact_work(import_id,work_id,year,author_count,member_count,"
            "retrieved_at) VALUES (%s,%s,%s,%s,%s,now()) ON CONFLICT DO NOTHING",
            (import_id, work_id, year, count, len(members)))
        for author_id in members:
            connection.execute(
                "INSERT INTO inspire_compact_membership(import_id,work_id,author_id) "
                "VALUES (%s,%s,%s) ON CONFLICT DO NOTHING", (import_id, work_id, author_id))


@pytest.fixture(scope="module")
def database():
    connection = _connect()
    connection.execute("DROP TABLE IF EXISTS graph_search_job")
    connection.execute("DROP TABLE IF EXISTS inspire_compact_membership")
    connection.execute("DROP TABLE IF EXISTS inspire_compact_work")
    connection.execute("DROP TABLE IF EXISTS inspire_compact_shard")
    connection.execute("DROP TABLE IF EXISTS inspire_compact_import")
    connection.execute(SCHEMA)
    _load(connection, "v1")
    _load(connection, "v2")
    yield connection
    connection.close()


def make_provider(connection, import_id, *, certified):
    claim = CoverageClaim(import_id=import_id, source_cutoff="2026-09-16T00:00:00+00:00",
                          certified_complete=certified,
                          reason="" if certified else "import_not_certified")
    return NeonCompactGraphProvider(connection, coverage=claim)


def jobs(connection, import_id="v1", *, certified=True, **kwargs):
    engine = DatabaseSearchJobs(
        connection, provider_factory=lambda: make_provider(connection, import_id, certified=certified),
        provider_for=lambda pin: make_provider(connection, pin.import_id, certified=certified),
        **kwargs)
    engine.ensure_schema()
    return engine


def run(engine, record, limit=20):
    """Poll like a client would until the job stops moving."""
    for _ in range(limit):
        if record["status"] != "searching":
            return record
        record = engine.get(record["job_id"])
    return record


# ------------------------------------------------------------------- routing

def test_zero_hop_is_immediately_exact(database):
    engine = jobs(database)
    record = engine.start("1", "1", FILTERS)
    assert record["proof_status"] == EXACT
    assert record["route_status"] == "exact_route_proven"
    assert record["global_shortest_proven"] is True
    assert record["paths"][0]["hops"] == 0


def test_direct_edge_is_proven_shortest_on_a_certified_import(database):
    record = run(engine := jobs(database), engine.start("1", "2", FILTERS))
    assert record["proof_status"] == EXACT
    assert record["paths"][0]["hops"] == 1
    assert record["paths"][0]["edges"][0]["evidence_refs"] == ["work:201"]


def test_multi_hop_route_is_found_and_proven(database):
    record = run(engine := jobs(database), engine.start("1", "4", FILTERS))
    assert record["proof_status"] == EXACT
    assert record["paths"][0]["hops"] == 3
    assert [person["id"] for person in record["paths"][0]["people"]] == ["1", "2", "3", "4"]


def test_disconnected_pair_is_no_path_only_when_certified(database):
    record = run(engine := jobs(database), engine.start("1", "8", FILTERS))
    assert record["proof_status"] == NO_PATH
    assert record["route_status"] == "no_path"


def test_disconnected_pair_is_incomplete_when_the_import_is_not_certified(database):
    """A partial import may never turn silence into a negative claim."""
    engine = jobs(database, certified=False)
    record = run(engine, engine.start("1", "8", FILTERS))
    assert record["proof_status"] == SEARCH_INCOMPLETE
    assert record["route_status"] == "search_incomplete"
    assert record["global_shortest_proven"] is False


def test_uncertified_import_downgrades_exact_to_verified(database):
    engine = jobs(database, certified=False)
    record = run(engine, engine.start("1", "2", FILTERS))
    assert record["proof_status"] == VERIFIED
    assert record["global_shortest_proven"] is False
    assert record["paths"][0]["hops"] == 1
    assert record["completeness_reason"] == "import_not_certified"


def test_unknown_endpoint_never_becomes_no_path(database):
    engine = jobs(database)
    record = run(engine, engine.start("1", "999999", FILTERS))
    assert record["proof_status"] == SEARCH_INCOMPLETE
    assert record["proof_status"] != NO_PATH
    assert not record.get("paths")


# ---------------------------------------------------------------- durability

def test_state_round_trips_through_serialisation(database):
    provider = make_provider(database, "v1", certified=True)
    engine = HLBES(ProviderOracle(provider, FILTERS), max_expansions=2)
    state = engine.begin("1", "4")
    while engine.advance(state):
        pass
    restored = deserialise(serialise(state))
    assert restored.upper == state.upper
    assert restored.lower == state.lower
    assert restored.left.dist == state.left.dist
    assert restored.left.radius == state.left.radius
    assert restored.left.complete == state.left.complete
    assert restored.right.blocked == state.right.blocked
    # levels are rebuilt from dist rather than stored, so they must still match.
    assert restored.left.levels == state.left.levels


def test_a_fresh_engine_resumes_a_job_another_instance_started(database):
    starter = jobs(database, slice_expansions=1)
    record = starter.start("1", "4", FILTERS)
    assert record["status"] == "searching"
    # A different object with its own provider, as a second serverless instance
    # would have: the proof continues from the row, not from memory.
    for _ in range(20):
        record = jobs(database, slice_expansions=1).get(record["job_id"])
        if record["status"] != "searching":
            break
    assert record["proof_status"] == EXACT
    assert record["paths"][0]["hops"] == 3


def test_progressive_result_is_labelled_provisional_until_settled(database):
    engine = jobs(database, slice_expansions=1)
    record = engine.start("1", "4", FILTERS)
    seen_provisional = record.get("provisional", False)
    for _ in range(20):
        if record["status"] != "searching":
            break
        record = engine.get(record["job_id"])
        seen_provisional = seen_provisional or record.get("provisional", False)
    assert seen_provisional
    assert record["provisional"] is False


def test_expansion_budget_stops_the_search_without_a_false_negative(database):
    engine = jobs(database, slice_expansions=1, max_expansions=1)
    record = run(engine, engine.start("1", "4", FILTERS))
    assert record["proof_status"] in {SEARCH_INCOMPLETE, VERIFIED}
    assert record["proof_status"] != NO_PATH
    assert record["can_continue"] is True


# -------------------------------------------------------------- version pins

def test_promotion_mid_search_fails_the_job_closed(database):
    """The pinned job must not be answered from a different import."""
    engine = DatabaseSearchJobs(
        database, provider_factory=lambda: make_provider(database, "v1", certified=True),
        # The pointer has moved: every later slice would serve v2.
        provider_for=lambda pin: make_provider(database, "v2", certified=True),
        slice_expansions=1)
    engine.ensure_schema()
    record = engine.start("1", "4", FILTERS)
    for _ in range(20):
        if record["status"] != "searching":
            break
        record = engine.get(record["job_id"])
    assert record["status"] == "failed"
    assert record["reason"] == "graph_version_changed"
    assert not record.get("paths")


def test_a_running_job_keeps_its_pin_while_a_new_search_takes_the_new_version(database):
    """The rollback drill: old jobs stay on their version, new ones move."""
    pointer = {"active": "v1"}
    engine = DatabaseSearchJobs(
        database, provider_factory=lambda: make_provider(database, pointer["active"], certified=True),
        provider_for=lambda pin: make_provider(database, pin.import_id, certified=True),
        slice_expansions=1)
    engine.ensure_schema()
    running = engine.start("1", "4", FILTERS)
    assert running["graph_snapshot"] == "v1"
    pointer["active"] = "v2"  # promotion, or a rollback to a restored version
    fresh = engine.start("1", "2", FILTERS)
    assert fresh["graph_snapshot"] == "v2"
    for _ in range(20):
        if running["status"] != "searching":
            break
        running = engine.get(running["job_id"])
    assert running["graph_snapshot"] == "v1"
    assert running["proof_status"] == EXACT


def test_filters_are_part_of_the_pin(database):
    engine = jobs(database)
    record = engine.start("1", "4", FILTERS)
    pin = JobPin("v1", None, "neon-compact-incidence-v1", "x")
    assert pin.filter_key != record["filters"]


# ------------------------------------------------------------------ failures

def test_database_failure_marks_the_job_failed_not_empty(database):
    class Broken:
        coverage = CoverageClaim(import_id="v1", certified_complete=True, reason="")

        def get_graph_version(self):
            return make_provider(database, "v1", certified=True).get_graph_version()

        def get_completeness(self, filters):
            return True

        def get_neighbors(self, author_id, filters):
            raise GraphDatabaseError("database_unavailable", "connection reset")

    engine = DatabaseSearchJobs(
        database, provider_factory=lambda: make_provider(database, "v1", certified=True),
        provider_for=lambda pin: Broken(), slice_expansions=1)
    engine.ensure_schema()
    record = engine.start("1", "4", FILTERS)
    record = engine.get(record["job_id"])
    assert record["status"] == "failed"
    assert record["reason"] == "database_unavailable"
    assert record["proof_status"] != NO_PATH


def test_cancel_does_not_relabel_a_proven_result(database):
    engine = jobs(database)
    record = run(engine, engine.start("1", "2", FILTERS))
    assert record["proof_status"] == EXACT
    cancelled = engine.cancel(record["job_id"])
    assert cancelled["proof_status"] == EXACT
    assert cancelled["global_shortest_proven"] is True


def test_cancel_stops_an_unfinished_search(database):
    engine = jobs(database, slice_expansions=1)
    record = engine.start("1", "4", FILTERS)
    cancelled = engine.cancel(record["job_id"])
    assert cancelled["status"] == "cancelled"
    assert cancelled["can_continue"] is False


# ------------------------------------------------------------ classification

@pytest.mark.parametrize("status,complete,settled,expected", [
    (EXACT, True, True, (EXACT, "exact_route_proven", True)),
    (EXACT, False, True, (VERIFIED, "verified_route_found", False)),
    (NO_PATH, True, True, (NO_PATH, "no_path", False)),
    (NO_PATH, False, True, (SEARCH_INCOMPLETE, "search_incomplete", False)),
    (VERIFIED, False, True, (VERIFIED, "verified_search_stopped", False)),
    (VERIFIED, False, False, (VERIFIED, "verified_route_found", False)),
    (SEARCH_INCOMPLETE, True, True, (SEARCH_INCOMPLETE, "search_incomplete", False)),
])
def test_classification_never_invents_a_global_claim(status, complete, settled, expected):
    assert classify(status, complete=complete, settled=settled) == expected
