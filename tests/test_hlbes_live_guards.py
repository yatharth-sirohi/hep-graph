"""Regressions for defects found reviewing the HLBES live adapter.

Each test here corresponds to a way the proof could be made to lie. They are
written against observable results, not internals, because that is the claim
that matters: the engine may say it cannot prove something, but it must never
prove something false.
"""
from __future__ import annotations

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from hepgraph.deep_search import DeepBudget, DeepSearch
from hepgraph.graph import Filters
from test_deep_search import (Client, DisappearingProfileClient, literature_query, page, paper,
                              person, profiles, ref)


def budget(**overrides):
    values = dict(max_seconds=30.0, max_requests=300, max_works=900, max_people=900,
                  page_size=2, max_pages_per_person=8)
    values.update(overrides)
    return DeepBudget(**values)


def run(client, source, target, filters=None, slices=6, **budget_overrides):
    session = DeepSearch(client).start(source, target, filters or Filters(genealogy=False))
    try:
        result = session.run(budget(**budget_overrides))
        for _ in range(slices):
            if not result.get("can_continue"):
                break
            result = session.run(budget(**budget_overrides))
        return result
    finally:
        session.close()


def lower_bound_page(hits, value):
    """INSPIRE's large-result form: the count is a floor, not a total."""
    return {"hits": {"total": {"value": value, "relation": "gte"}, "hits": list(hits)}}


# ------------------------------------------------- a floor is not a total
def _gte_fixture():
    responses = profiles(1, 2, 6, 7, 8, 9)
    responses[("literature", literature_query(1), 1)] = lower_bound_page([paper(106, [1, 6])], 1)
    responses[("literature", literature_query(2), 1)] = lower_bound_page([paper(182, [8, 2])], 1)
    responses[("literature", literature_query(6), 1)] = page(paper(106, [1, 6]), paper(167, [6, 7]), total=2)
    responses[("literature", literature_query(7), 1)] = page(paper(167, [6, 7]), paper(178, [7, 8]), total=2)
    responses[("literature", literature_query(8), 1)] = page(paper(178, [7, 8]), paper(182, [8, 2]), total=2)
    # The real two-hop route sits on page two of both endpoint queries.
    responses[("literature", literature_query(1), 2)] = page(paper(109, [1, 9]), total=2)
    responses[("literature", literature_query(2), 2)] = page(paper(209, [2, 9]), total=2)
    responses[("literature", literature_query(9), 1)] = page(paper(109, [1, 9]), paper(209, [2, 9]), total=2)
    return responses


def test_a_lower_bound_total_cannot_end_a_query_and_fake_a_proof():
    client = Client(_gte_fixture())
    result = run(client, 1, 2)
    assert ("literature", literature_query(1), 2) in client.calls
    assert [p["id"] for p in result["paths"][0]["people"]] == ["1", "9", "2"]
    assert result["paths"][0]["hops"] == 2
    assert result["global_shortest_proven"] is True


def test_a_lower_bound_total_cannot_fake_a_no_path():
    responses = profiles(1, 2, 3, 7, 8)
    responses[("literature", literature_query(1), 1)] = lower_bound_page([paper(170, [1, 7])], 1)
    responses[("literature", literature_query(2), 1)] = lower_bound_page([paper(280, [2, 8])], 1)
    responses[("literature", literature_query(7), 1)] = page(paper(170, [1, 7]), total=1)
    responses[("literature", literature_query(8), 1)] = page(paper(280, [2, 8]), total=1)
    # The only connection sits on page two of both endpoint queries.
    responses[("literature", literature_query(1), 2)] = page(paper(101, [1, 3]), total=1)
    responses[("literature", literature_query(2), 2)] = page(paper(201, [2, 3]), total=1)
    responses[("literature", literature_query(3), 1)] = page(paper(101, [1, 3]), paper(201, [2, 3]), total=2)
    result = run(Client(responses), 1, 2, page_size=1)
    assert result["status"] != "no_path"
    assert [p["id"] for p in result["paths"][0]["people"]] == ["1", "3", "2"]


# ------------------------------------------- genealogy has its own exhaustion
def test_a_doctoral_edge_does_not_permanently_block_every_proof():
    """Genealogy is on by default; a PhD edge must not stall every radius."""
    responses = profiles(1, 2, 3)
    responses[("authors", "control_number:1", 1)] = page(
        person(1, [{"record": ref(3), "degree_type": "phd", "curated_relation": True}]))
    for identifier in (1, 2, 3):
        responses[("literature", literature_query(identifier), 1)] = page(total=0)
    responses[("literature", literature_query(3), 1)] = page(paper(300, [3, 2]), total=1)
    for identifier in (1, 2, 3):
        responses[("authors", f"advisors.record.$ref:{identifier}", 1)] = page(total=0)
    result = run(Client(responses), 1, 2, Filters(genealogy=True))
    assert result["status"] == "ok"
    assert [p["id"] for p in result["paths"][0]["people"]] == ["1", "3", "2"]
    assert result["global_shortest_proven"] is True
    assert result["bounds"]["source_radius"] >= 1, "a doctoral edge must still close a layer"


def test_genealogy_off_still_proves_the_same_distance():
    responses = profiles(1, 2, 3)
    for identifier in (1, 2, 3):
        responses[("literature", literature_query(identifier), 1)] = page(total=0)
    responses[("literature", literature_query(1), 1)] = page(paper(101, [1, 3]), total=1)
    responses[("literature", literature_query(2), 1)] = page(paper(201, [2, 3]), total=1)
    responses[("literature", literature_query(3), 1)] = page(paper(101, [1, 3]), paper(201, [2, 3]), total=2)
    result = run(Client(responses), 1, 2)
    assert result["paths"][0]["hops"] == 2 and result["global_shortest_proven"] is True


# ------------------------------------------------- an exhausted set is frozen
def test_a_pair_crossing_min_shared_later_withdraws_the_exhaustion_claim():
    """The second shared work can arrive on a third person's page."""
    responses = profiles(1, 2, 3, 4)
    responses[("literature", literature_query(1), 1)] = page(paper(401, [1, 2]), paper(402, [1, 2]), total=2)
    responses[("literature", literature_query(2), 1)] = page(paper(401, [1, 2]), paper(402, [1, 2]),
                                                             paper(403, [2, 4]), total=3)
    responses[("literature", literature_query(4), 1)] = page(paper(403, [2, 4]), paper(404, [2, 4, 3]), total=2)
    responses[("literature", literature_query(3), 1)] = page(paper(404, [2, 4, 3]), total=1)
    result = run(Client(responses), 1, 4, Filters(genealogy=False, min_shared=2), page_size=8)
    assert result["status"] == "ok"
    assert [p["id"] for p in result["paths"][0]["people"]] == ["1", "2", "4"]


# ------------------------------------------------------ nothing escapes run()
@pytest.mark.parametrize("vanishing", ["1", "2", "3"])
def test_a_profile_that_stops_answering_never_escapes_as_an_exception(vanishing):
    """Identity validation can retire the proof mid-result; run() must cope.

    Whatever the outcome, it arrives as a structured result and every person
    on a returned route has been confirmed against a current public profile.
    """
    responses = profiles(1, 2, 3)
    responses[("literature", literature_query(1), 1)] = page(paper(101, [1, 3]), total=1)
    responses[("literature", literature_query(2), 1)] = page(paper(201, [2, 3]), total=1)
    responses[("literature", literature_query(3), 1)] = page(paper(101, [1, 3]), paper(201, [2, 3]), total=2)
    session = DeepSearch(DisappearingProfileClient(responses, vanishing)).start(
        1, 2, Filters(genealogy=False))
    try:
        result = session.run(budget())
        for _ in range(6):
            if not result.get("can_continue"):
                break
            result = session.run(budget())
        confirmed = set(session._identity_confirmed)
        unverified = set(session._unverified_people)
    finally:
        session.close()
    assert result["status"] in {"ok", "search_incomplete", "not_found", "no_path"}
    for route in result["paths"]:
        people = [item["id"] for item in route["people"]]
        assert set(people) <= confirmed
        assert not set(people) & unverified


# --------------------------------------------- an unproven route cannot seed U
def test_the_upper_bound_is_never_seeded_from_an_unvalidated_route():
    """A hop the live profile check would retract must not become a bound."""
    responses = profiles(1, 2, 3, 4, 5)
    responses[("literature", literature_query(1), 1)] = page(paper(101, [1, 3]), paper(104, [1, 4]), total=2)
    responses[("literature", literature_query(2), 1)] = page(paper(201, [2, 3]), paper(205, [2, 5]), total=2)
    responses[("literature", literature_query(3), 1)] = page(paper(101, [1, 3]), paper(201, [2, 3]), total=2)
    responses[("literature", literature_query(4), 1)] = page(paper(104, [1, 4]), paper(145, [4, 5]), total=2)
    responses[("literature", literature_query(5), 1)] = page(paper(205, [2, 5]), paper(145, [4, 5]), total=2)
    result = run(Client(responses), 1, 2)
    assert result["paths"][0]["hops"] == 2
    assert result["global_shortest_proven"] is True
    assert result["bounds"]["lower"] == result["bounds"]["upper"] == 2


# ------------------------------------------------------------- loop is bounded
def test_local_work_between_requests_cannot_outrun_the_time_allowance():
    responses = profiles(1, 2)
    for identifier in (1, 2):
        responses[("literature", literature_query(identifier), 1)] = page(total=0)
    result = run(Client(responses), 1, 2, slices=0, max_seconds=1.0)
    assert result["status"] in {"no_path", "search_incomplete", "resource_limit", "ok"}
