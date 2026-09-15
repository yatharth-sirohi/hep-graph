"""Adversarial regression tests for the proposed deep-search engine patch.

Run these against a temporary copy that has ``engine-improvements.patch``
applied. They intentionally exercise search invariants through public evidence
fixtures rather than live INSPIRE calls.
"""
from __future__ import annotations

import time

import hepgraph.deep_search as deep_module
from hepgraph.deep_search import DeepSearch
from hepgraph.remote import RemoteError

# Reuse the production suite's fully offline INSPIRE-shaped records.  The test
# runner adds the application's tests directory to PYTHONPATH.
from test_deep_search import Client, budget, page, paper, profiles


def test_guarded_graph_is_reused_until_a_successful_fetch_changes_evidence(monkeypatch):
    """Repeated neighbour reads must retain one guarded Graph and its caches."""
    calls = 0
    original = deep_module.build_snapshot

    def counted(connection, manifest):
        nonlocal calls
        calls += 1
        return original(connection, manifest)

    monkeypatch.setattr(deep_module, "build_snapshot", counted)
    session = DeepSearch(Client(profiles(1, 2))).start(1, 2, {"genealogy": False})
    try:
        session._run_requests = 0
        session._run_deadline = time.monotonic() + 10
        session._fetch("authors", "control_number:1", 1, budget())
        first_snapshot, first_graph = session._snapshot(budget())
        assert session._eligible_neighbors("1", budget()) == ()
        second_snapshot, second_graph = session._snapshot(budget())
        assert calls == 1
        assert first_snapshot is second_snapshot
        assert first_graph is second_graph

        # Dynamic progress metadata still refreshes without rerunning the
        # identity guard or rebuilding the incidence graph.
        session._identity_confirmed.add("1")
        refreshed, refreshed_graph = session._snapshot(budget())
        assert refreshed_graph is first_graph
        assert refreshed["coverage"]["identity_validation"]["confirmed_profiles"] == 1
        assert calls == 1

        session._fetch("authors", "control_number:2", 1, budget())
        _, replacement_graph = session._snapshot(budget())
        assert calls == 2
        assert replacement_graph is not first_graph
    finally:
        session.close()


def test_repeated_work_bridge_between_closed_frontiers_is_detected_by_its_unrelated_cursor():
    """The Nth A--B work may arrive while expanding unrelated cursor C.

    The first A--B article is retrieved from the source side. The second is
    returned only while C is expanded, so C has just one shared paper with each
    endpoint and creates no eligible edge at ``min_shared=2``. The proposal
    must still notice that the two previously seen sides now connect via A--B.
    """
    responses = profiles(1, 2, 3, 4, 5)
    responses[("literature", "seed", 1)] = page(
        paper(10, [1, 2]), paper(11, [1, 2]), paper(12, [1, 3]), paper(13, [1, 3]),
        paper(20, [4, 5]), paper(21, [4, 5]), paper(22, [2, 4]),
    )
    # This works page belongs to C=3 and supplies the second 2--4 evidence,
    # but one C work alone cannot meet the selected threshold.
    responses[("literature", "authors.record.$ref:3 AND author_count:1->10", 1)] = page(
        paper(23, [2, 4, 3])
    )
    session = DeepSearch(Client(responses)).start(1, 5, {"genealogy": False, "min_shared": 2})
    try:
        session._run_requests = 0
        session._run_deadline = time.monotonic() + 10
        for person_id in (1, 2, 3, 4, 5):
            session._fetch("authors", f"control_number:{person_id}", 1, budget())
        session._fetch("literature", "seed", 1, budget())
        # These cursors deliberately simulate prior breadth work. A and B have
        # already been closed; C is the only live cursor and is not eligible to
        # either endpoint after its one new paper arrives.
        session.left.seen = {"1": 0, "2": 1, "3": 1}
        session.right.seen = {"5": 0, "4": 1}
        cursor = session._cursor("3", 1, profile_done=True)
        met = session._step_cursor(session.left, cursor, budget())
        snapshot, graph = session._snapshot(budget())
        found = graph.find_paths("1", "5", 1)
    finally:
        session.close()

    assert met is True
    assert found["status"] == "ok"
    assert [person["id"] for person in found["paths"][0]["people"]] == ["1", "2", "4", "5"]


def test_cross_frontier_diagonal_schedule_reaches_later_blocks_before_a_slice_is_spent():
    """A 3x3 bridge frontier should cover all left blocks in its first round."""
    session = DeepSearch(Client()).start(100, 200, {"genealogy": False})
    queries: list[str] = []
    try:
        session.left.seen = {str(item): 1 for item in range(100, 125)}
        session.right.seen = {str(item): 1 for item in range(200, 225)}
        session._run_requests = 0
        session._bridge_queries_this_run = 0
        session._run_deadline = time.monotonic() + 10

        def fetched(_collection, query, _page, _budget, **_kwargs):
            queries.append(query)
            return [], 0

        session._fetch = fetched
        assert session._cross_frontier(budget())
        assert session._cross_frontier(budget())
        assert session._cross_frontier(budget())
    finally:
        session.close()

    # First diagonal round: (left0,right0), (left1,right1), (left2,right2).
    assert all(f"authors.record.$ref:{item}" in queries[index] for index, item in enumerate((100, 110, 120)))
    assert all(f"authors.record.$ref:{item}" in queries[index] for index, item in enumerate((200, 210, 220)))
