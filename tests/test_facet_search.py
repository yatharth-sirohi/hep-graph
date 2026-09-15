"""Offline integration checks for compact facet-guided deep retrieval.

Facet rows are deliberately only navigation hints in these fixtures. Every
returned hop still has to be fetched as an exact pair query and pass Graph's
normal document, filter, and identity rules.
"""
from __future__ import annotations

import copy
import re

import pytest

from hepgraph.deep_search import DeepSearch
from hepgraph.remote import RemoteError
from test_deep_search import Client, budget, page, pair_query, paper, profiles


class FacetClient(Client):
    def __init__(self, responses, facets=None, *, unsupported=False):
        super().__init__(responses)
        self.facets = facets or {}
        self.unsupported = unsupported
        self.facet_calls: list[str] = []

    def coauthors(self, query, *, deadline=None):
        self.facet_calls.append(query)
        if self.unsupported:
            raise RemoteError("upstream_unavailable", "facet endpoint unavailable in fixture")
        person_id = re.search(r"authors\.record\.\$ref:([1-9][0-9]*)", query).group(1)
        value = self.facets.get(person_id, {"authors": [], "truncated": False, "total": 0})
        return copy.deepcopy(value)


def facet(*ids, truncated=False):
    return {"authors": [{"id": str(item), "count": 1} for item in ids],
            "truncated": truncated, "total": len(ids)}


def run(client, source=1, target=2, filters=None, **limits):
    session = DeepSearch(client).start(source, target, filters or {"genealogy": False})
    try:
        return session.run(budget(max_requests=80, **limits))
    finally:
        session.close()


def test_arbitrary_facet_endpoints_join_through_a_backbone_with_exact_evidence():
    """Neither endpoint belongs to a saved pilot component or hard-coded hint."""
    responses = profiles(1, 2, 10, 11, 20)
    for work_id, left, right in ((101, 1, 10), (102, 10, 11), (103, 11, 20), (104, 20, 2)):
        responses[("literature", pair_query(left, right), 1)] = page(paper(work_id, [left, right]))
    client = FacetClient(responses, {
        "1": facet(10), "2": facet(20), "10": facet(11), "20": facet(11),
    })

    result = run(client)

    assert result["status"] == "ok"
    assert [person["id"] for person in result["paths"][0]["people"]] == ["1", "10", "11", "20", "2"]
    displayed = {work["id"] for edge in result["paths"][0]["edges"] for work in edge["works"]}
    assert displayed == {"101", "102", "103", "104"}
    assert result["coverage"]["coauthor_discovery"]["purpose"].startswith("navigation_only")
    assert client.facet_calls


@pytest.mark.parametrize("case", ["min_shared", "date", "roles", "correction"])
def test_facet_link_never_bypasses_normal_paper_filters(case):
    responses = profiles(1, 2, 3)
    first, second = paper(201, [1, 3]), paper(202, [3, 2])
    filters = {"genealogy": False}
    if case == "min_shared":
        filters["min_shared"] = 2
    elif case == "date":
        filters.update(year_start=2000, year_end=2000)
    elif case == "roles":
        first = paper(201, [1, 3], roles=["editor"])
    else:
        first["metadata"]["titles"][0]["title"] = "Erratum: a fixture correction"
    responses[("literature", pair_query(1, 3), 1)] = page(first)
    responses[("literature", pair_query(3, 2), 1)] = page(second)
    client = FacetClient(responses, {"1": facet(3), "2": facet(3)})

    result = run(client, filters=filters)

    assert result["status"] == "search_incomplete"
    assert result["paths"] == []
    # The pair was fetched as ordinary literature. The compact count was never
    # converted into a graph edge or substituted for the rejected evidence.
    assert ("literature", pair_query(1, 3), 1) in client.calls


def test_missing_facet_profile_rejects_that_candidate_and_uses_an_alternate():
    responses = profiles(1, 2, 4)
    for work_id, left, right in ((301, 1, 4), (302, 4, 2)):
        responses[("literature", pair_query(left, right), 1)] = page(paper(work_id, [left, right]))
    client = FacetClient(responses, {"1": facet(3, 4), "2": facet(3, 4)})

    result = run(client)

    assert result["status"] == "ok"
    assert [person["id"] for person in result["paths"][0]["people"]] == ["1", "4", "2"]
    assert result["coverage"]["coauthor_discovery"]["rejected_links"] >= 0
    assert any("control_number:3" in query for kind, query, _ in client.calls if kind == "authors")


def test_unsupported_facets_fall_back_to_ordinary_bidirectional_retrieval():
    responses = profiles(1, 2, 3)
    responses[("literature", "authors.record.$ref:1 AND author_count:1->10", 1)] = page(paper(401, [1, 3]))
    responses[("literature", "authors.record.$ref:2 AND author_count:1->10", 1)] = page(paper(402, [3, 2]))
    client = FacetClient(responses, unsupported=True)

    result = run(client)

    assert result["status"] == "ok"
    assert [person["id"] for person in result["paths"][0]["people"]] == ["1", "3", "2"]
    assert result["coverage"]["coauthor_discovery"]["failures"]


def test_truncated_facets_never_produce_a_no_connection_claim():
    responses = profiles(1, 2, 3)
    client = FacetClient(responses, {"1": facet(3, truncated=True), "2": facet(3, truncated=True)})

    result = run(client)

    assert result["status"] == "search_incomplete"
    assert result["paths"] == []
    discovery = result["coverage"]["coauthor_discovery"]
    assert discovery["truncated_profiles"] >= 1
    assert discovery["complete"] is False


def test_route_profile_hydration_resumes_after_a_slice_boundary():
    """A retained route must not vanish when profile batching hits the limit."""
    responses = profiles(1, 2, 3)
    responses[("literature", pair_query(1, 3), 1)] = page(paper(501, [1, 3]))
    responses[("literature", pair_query(3, 2), 1)] = page(paper(502, [3, 2]))
    client = FacetClient(responses, {"1": facet(3), "2": facet(3)})
    session = DeepSearch(client).start(1, 2, {"genealogy": False})
    try:
        paused = session.run(budget(max_requests=6))
        resumed = session.run(budget(max_requests=40))
    finally:
        session.close()

    assert paused["status"] == "resource_limit" and paused["can_continue"] is True
    assert resumed["status"] == "ok"
    assert [person["id"] for person in resumed["paths"][0]["people"]] == ["1", "3", "2"]


def test_identity_rejection_does_not_blacklist_an_unfetched_current_facet_route():
    """Only the path being validated may lose its guarded-away pairs."""
    session = DeepSearch(FacetClient({})).start(1, 2, {"genealogy": False})

    class NoEdges:
        @staticmethod
        def _edge(_left, _right):
            return None

    try:
        # The navigator has moved on to this prospective route, but the
        # identity guard is processing a different candidate from the retrieved
        # graph. None of 1--8 or 8--2 has been fetched yet.
        session.navigator.add_link("1", "8")
        session.navigator.add_link("8", "2")
        session._navigation_route = ["1", "8", "2"]
        session._reject_unproved_navigation_edges(NoEdges(), (("1", "3", "2"),))

        assert session.navigator.pair("1", "3") in session.navigator.blocked_edges
        assert session.navigator.pair("3", "2") in session.navigator.blocked_edges
        assert session.navigator.pair("1", "8") not in session.navigator.blocked_edges
        assert session.navigator.pair("8", "2") not in session.navigator.blocked_edges
        assert session.navigator.route() == ["1", "8", "2"]
    finally:
        session.close()


def test_two_endpoint_facets_beat_an_older_longer_navigation_corridor():
    """A saved guide must not consume the run before both live roots are sampled."""
    responses = profiles(1, 2, 3, 4, 5)
    for work_id, left, right in (
        (601, 1, 3), (602, 3, 4), (603, 4, 2),  # old 3-hop guide
        (604, 1, 5), (605, 5, 2),                # live 2-hop facet route
    ):
        responses[("literature", pair_query(left, right), 1)] = page(paper(work_id, [left, right]))
    client = FacetClient(responses, {"1": facet(5), "2": facet(5)})
    session = DeepSearch(client, suggestion_pairs=((1, 3), (3, 4), (4, 2))).start(
        1, 2, {"genealogy": False}
    )
    try:
        result = session.run(budget(max_requests=80))
    finally:
        session.close()

    assert result["status"] == "ok"
    assert [person["id"] for person in result["paths"][0]["people"]] == ["1", "5", "2"]
    pair_calls = [query for kind, query, _ in client.calls if kind == "literature" and " AND " in query]
    assert pair_calls[1:3] == [pair_query(1, 5), pair_query(5, 2)]
