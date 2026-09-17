"""End-to-end database mode: API contract, and the two-stage retrieval rule.

The load-bearing test here is ``test_no_paper_fetch_during_traversal``: the
whole point of the migration is that exploring the graph costs no INSPIRE
requests, so a spy proves the frontier never touches the client.
"""

from __future__ import annotations

import os

import pytest

from hepgraph.graph import Filters
from hepgraph.graph_database_mode import DatabaseGraphService, DatabaseModeConfig
from hepgraph.graph_hydration import Hydrator
from hepgraph.hlbes import EXACT, SEARCH_INCOMPLETE, VERIFIED
from hepgraph.neon_compact_import import SCHEMA

psycopg = pytest.importorskip("psycopg")

URL = os.environ.get("HEPGRAPH_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not URL, reason="HEPGRAPH_TEST_DATABASE_URL is not set")

IMPORT_ID = "mode-test"
FILTERS = Filters(max_authors=10, genealogy=False)
WORKS = ((301, 2001, 2, (11, 12)), (302, 2002, 2, (12, 13)), (303, 2003, 2, (13, 14)))


class SpyClient:
    """Counts every INSPIRE call and records what was asked for."""

    def __init__(self):
        self.calls: list[tuple[str, str]] = []

    def fetch(self, collection, query, page=1, size=25, **kwargs):
        self.calls.append((collection, query))
        hits = []
        for token in query.replace("control_number:", "").replace(" OR ", " ").split():
            if not token.isdigit():
                continue
            if collection == "literature":
                hits.append({"metadata": {"control_number": int(token),
                                          "titles": [{"title": f"Paper {token}"}],
                                          "earliest_date": "2001-01-01",
                                          "author_count": 2, "document_type": ["article"]}})
            else:
                hits.append({"metadata": {"control_number": int(token),
                                          "name": {"value": f"Person {token}"}}})
        return {"hits": {"hits": hits, "total": len(hits)}}

    search = fetch


@pytest.fixture(scope="module")
def database():
    connection = psycopg.connect(URL, autocommit=True, row_factory=psycopg.rows.dict_row)
    connection.execute("DROP TABLE IF EXISTS graph_search_job")
    connection.execute("DROP TABLE IF EXISTS inspire_compact_membership")
    connection.execute("DROP TABLE IF EXISTS inspire_compact_work")
    connection.execute("DROP TABLE IF EXISTS inspire_compact_shard")
    connection.execute("DROP TABLE IF EXISTS inspire_compact_import")
    connection.execute(SCHEMA)
    connection.execute(
        "INSERT INTO inspire_compact_import(import_id,source_cutoff,low_recid,high_recid,status) "
        "VALUES (%s, now(), 300, 400, 'FETCHING')", (IMPORT_ID,))
    connection.execute(
        "INSERT INTO inspire_compact_shard(import_id,low_recid,high_recid,status,expected_records,"
        "received_records) VALUES (%s,300,400,'DONE',3,3)", (IMPORT_ID,))
    for work_id, year, count, members in WORKS:
        connection.execute(
            "INSERT INTO inspire_compact_work(import_id,work_id,year,author_count,member_count,"
            "retrieved_at) VALUES (%s,%s,%s,%s,%s,now())",
            (IMPORT_ID, work_id, year, count, len(members)))
        for author_id in members:
            connection.execute(
                "INSERT INTO inspire_compact_membership(import_id,work_id,author_id) "
                "VALUES (%s,%s,%s)", (IMPORT_ID, work_id, author_id))
    yield connection
    connection.close()


def service(database, spy, *, certified=True):
    config = DatabaseModeConfig(url="unused", import_id=IMPORT_ID, certified_complete=certified)
    return DatabaseGraphService(config, client=spy, connection=database,
                                hydrator=Hydrator(spy))


def settle(handle, record, limit=25):
    for _ in range(limit):
        if record["status"] != "searching":
            return record
        record = handle.job(record["job_id"])
    return record


# --------------------------------------------------------- two-stage retrieval

def test_no_paper_fetch_during_traversal(database):
    """Frontier expansion must cost zero INSPIRE requests."""
    spy = SpyClient()
    handle = service(database, spy)
    jobs = handle.jobs()
    record = jobs.start("11", "14", FILTERS)
    while record["status"] == "searching":
        record = jobs.get(record["job_id"])
    # The raw job engine never hydrates, so nothing has been fetched yet.
    assert spy.calls == []
    assert record["proof_status"] == EXACT
    # Only the delivered answer triggers retrieval.
    handle.hydrate(record)
    assert spy.calls


def test_hydration_covers_only_the_displayed_route(database):
    spy = SpyClient()
    handle = service(database, spy)
    record = settle(handle, handle.start_path("11", "14", FILTERS))
    people = [person["id"] for person in record["paths"][0]["people"]]
    assert people == ["11", "12", "13", "14"]
    assert [person["name"] for person in record["paths"][0]["people"]] == [
        "Person 11", "Person 12", "Person 13", "Person 14"]
    queried = " ".join(query for _, query in spy.calls)
    # Author 9 is not on this route and must never have been requested.
    assert "99" not in queried
    assert record["retrieval"]["people"] == 4


def test_edges_carry_hydrated_evidence_in_the_shape_the_ui_reads(database):
    spy = SpyClient()
    handle = service(database, spy)
    record = settle(handle, handle.start_path("11", "12", FILTERS))
    edge = record["paths"][0]["edges"][0]
    assert edge["types"] == ["coauthor"]
    assert edge["shared_works"] == 1
    assert edge["works"][0]["id"] == "301"
    assert edge["works"][0]["title"] == "Paper 301"
    assert edge["works"][0]["source_url"].endswith("/literature/301")


def test_upstream_failure_keeps_the_proven_edge_visible(database):
    class Broken(SpyClient):
        def fetch(self, *args, **kwargs):
            raise RuntimeError("upstream down")

        search = fetch

    handle = service(database, Broken())
    record = settle(handle, handle.start_path("11", "12", FILTERS))
    edge = record["paths"][0]["edges"][0]
    assert record["proof_status"] == EXACT
    assert edge["works"][0]["id"] == "301"
    assert edge["works"][0]["details_unavailable"] is True
    assert "title" not in edge["works"][0]
    assert record["retrieval"]["complete"] is False


# ------------------------------------------------------------------- contract

def test_dataset_reports_the_pin_and_refuses_to_claim_completeness(database):
    handle = service(database, SpyClient(), certified=False)
    dataset = handle.dataset()
    assert dataset["source_mode"] == "database"
    assert dataset["version"] == f"graph-db:{IMPORT_ID}"
    assert dataset["graph_snapshot"] == IMPORT_ID
    assert dataset["coverage"]["complete"] is False
    assert "not been certified" in dataset["coverage"]["description"]
    assert dataset["capabilities"]["global_centrality"] is False


def test_dataset_reports_coverage_when_certified(database):
    dataset = service(database, SpyClient(), certified=True).dataset()
    assert dataset["coverage"]["complete"] is True
    assert dataset["coverage"]["observed_record_range"] == [301, 303]


def test_uncertified_mode_never_returns_exact(database):
    handle = service(database, SpyClient(), certified=False)
    record = settle(handle, handle.start_path("11", "14", FILTERS))
    assert record["proof_status"] == VERIFIED
    assert record["global_shortest_proven"] is False


def test_profile_hydrates_on_demand_and_counts_from_the_graph(database):
    spy = SpyClient()
    profile = service(database, spy).person("12", FILTERS)
    assert profile["status"] == "ok"
    assert profile["person"]["name"] == "Person 12"
    assert profile["coauthor_count"] == 2
    assert {item["person"]["id"] for item in profile["collaborators"]} == {"11", "13"}
    assert profile["collaborators"][0]["shared_works"] == 1


def test_profile_of_an_unknown_person_is_not_found_not_absent(database):
    profile = service(database, SpyClient()).person("999999", FILTERS)
    assert profile["status"] == "not_found"
    assert "not evidence" in profile["message"]


def test_neighborhood_shape(database):
    found = service(database, SpyClient()).neighborhood("12", FILTERS)
    assert found["status"] == "ok"
    assert {person["id"] for person in found["people"]} == {"11", "12", "13"}
    assert all(edge["types"] == ["coauthor"] for edge in found["edges"])


def test_ancestry_is_unavailable_without_an_overlay(database):
    found = service(database, SpyClient()).ancestry("12", FILTERS)
    assert found["status"] == "unavailable"
    # Wording is the UI's to choose; what matters is that it says no, with a reason.
    assert "Adviser records" in found["message"]


def test_unknown_endpoint_is_reported_without_a_negative_claim(database):
    handle = service(database, SpyClient())
    record = settle(handle, handle.start_path("11", "999999", FILTERS))
    assert record["proof_status"] == SEARCH_INCOMPLETE
    assert record["reason"] == "author_not_in_graph"
    assert record["can_continue"] is False
    assert "not evidence" in record["message"]


def test_owns_job_distinguishes_database_jobs(database):
    handle = service(database, SpyClient())
    record = handle.start_path("11", "12", FILTERS)
    assert handle.owns_job(record["job_id"]) is True
    assert handle.owns_job("0" * 32) is False


def test_config_requires_an_explicit_completeness_certificate():
    env = {"HEPGRAPH_GRAPH_DATABASE_URL": "postgres://x", "HEPGRAPH_GRAPH_IMPORT_ID": "i"}
    config = DatabaseModeConfig.from_env(env)
    assert config.certified_complete is False
    assert DatabaseModeConfig.from_env({}) is None
    assert DatabaseModeConfig.from_env(env | {"HEPGRAPH_GRAPH_CERTIFIED_COMPLETE": "true"}
                                       ).certified_complete is True


# ----------------------------------------------------------- verification

class BylineClient(SpyClient):
    """Returns literature whose byline can be steered per work."""

    def __init__(self, bylines):
        super().__init__()
        self.bylines = bylines

    def fetch(self, collection, query, page=1, size=25, **kwargs):
        self.calls.append((collection, query))
        hits = []
        for token in query.replace("control_number:", "").replace(" OR ", " ").split():
            if not token.isdigit():
                continue
            if collection == "literature":
                authors = [{"record": {"$ref": f"https://inspirehep.net/api/authors/{a}"}}
                           for a in self.bylines.get(token, [])]
                hits.append({"metadata": {"control_number": int(token),
                                          "titles": [{"title": f"Paper {token}"}],
                                          "earliest_date": "2001-01-01", "author_count": 2,
                                          "document_type": ["article"], "authors": authors}})
            else:
                hits.append({"metadata": {"control_number": int(token),
                                          "name": {"value": f"Person {token}"}}})
        return {"hits": {"hits": hits, "total": len(hits)}}

    search = fetch


def test_edges_are_confirmed_against_the_inspire_byline(database):
    client = BylineClient({"301": ["11", "12"]})
    handle = service(database, client)
    handle._hydrator = Hydrator(client)
    record = settle(handle, handle.start_path("11", "12", FILTERS))
    edge = record["paths"][0]["edges"][0]
    assert edge["verification"] == "confirmed"
    assert edge["verified_works"] == ["301"]
    assert record["verification"]["edges_confirmed"] == 1
    assert record["verification"]["route_confirmed"] is True


def test_a_byline_that_omits_an_endpoint_withdraws_the_proof(database):
    """The graph claims the edge; INSPIRE does not. The claim must not stand."""
    client = BylineClient({"301": ["11", "999"]})
    handle = service(database, client)
    handle._hydrator = Hydrator(client)
    record = settle(handle, handle.start_path("11", "12", FILTERS))
    edge = record["paths"][0]["edges"][0]
    assert edge["verification"] == "contradicted"
    assert record["verification"]["edges_contradicted"] == 1
    assert record["proof_status"] == SEARCH_INCOMPLETE
    assert record["global_shortest_proven"] is False
    assert "drifted from the source" in record["message"]


def test_an_unlinked_byline_is_unverified_not_a_contradiction(database):
    """A record with no linked authors is missing evidence, not counter-evidence."""
    client = BylineClient({"301": []})
    handle = service(database, client)
    handle._hydrator = Hydrator(client)
    record = settle(handle, handle.start_path("11", "12", FILTERS))
    edge = record["paths"][0]["edges"][0]
    assert edge["verification"] == "unverified"
    assert record["verification"]["edges_contradicted"] == 0
    assert record["proof_status"] == EXACT


def test_each_delivery_gets_a_fresh_hydration_budget(database):
    """A cached hydrator fixes its deadline once and starves later results.

    An explicitly injected hydrator is still honoured, because a test that
    supplies one wants exactly that instance.
    """
    spy = SpyClient()
    config = DatabaseModeConfig(url="unused", import_id=IMPORT_ID, certified_complete=True)
    handle = DatabaseGraphService(config, client=spy, connection=database)
    first, second = handle.hydrator(), handle.hydrator()
    assert first is not second
    assert first._cache is second._cache

    injected = Hydrator(spy)
    pinned = DatabaseGraphService(config, client=spy, connection=database, hydrator=injected)
    assert pinned.hydrator() is injected
