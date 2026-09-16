"""Offline adversarial coverage for the owner-thread deep live search."""
from __future__ import annotations

import copy
import re
import threading
import time

import pytest

from hepgraph.deep_search import DeepBudget, DeepSearch, DeepSearchError
from hepgraph.graph import Filters
from hepgraph.remote import RemoteError


def ref(person_id: int | str) -> dict[str, str]:
    return {"$ref": f"https://inspirehep.net/api/authors/{person_id}"}


def person(person_id: int | str, advisers: list[dict] | None = None, *, name: str | None = None) -> dict:
    return {"id": str(person_id), "metadata": {"control_number": str(person_id),
        "name": {"value": name or f"Person {person_id}"}, "ids": [], "positions": [], "advisors": advisers or []}}


def paper(work_id: int | str, people: list[int | str], *, doi: str | None = None,
          author_count: int | None = None, roles: list[str] | None = None,
          names: dict[int | str, str] | None = None) -> dict:
    return {"id": str(work_id), "metadata": {"control_number": str(work_id),
        "titles": [{"title": f"Work {work_id}"}], "document_type": ["article"],
        "authors": [{"record": ref(item), "full_name": (names or {}).get(item, f"Person {item}"),
                     "inspire_roles": roles or ["author"], "affiliations": []} for item in people],
        "author_count": author_count if author_count is not None else len(people),
        "earliest_date": "2001-01-01", "preprint_date": "2001-01-01",
        "dois": [{"value": doi}] if doi else [], "arxiv_eprints": []}}


def page(*hits: dict, total: int | None = None) -> dict:
    return {"hits": {"total": len(hits) if total is None else total, "hits": list(hits)}}


class Client:
    def __init__(self, responses: dict[tuple[str, str, int], dict] | None = None) -> None:
        self.responses = responses or {}
        self.calls: list[tuple[str, str, int]] = []
        self.sizes: list[int] = []

    def search(self, collection: str, query: str, *, size: int = 25, page: int = 1,
               sort: str | None = None, deadline: float | None = None) -> dict:
        self.calls.append((collection, query, page))
        self.sizes.append(size)
        # Mirror the exact control-number OR behavior used by the deep profile
        # hydrator, while retaining fixture control over a missing ID.
        if collection == "authors" and " OR " in query:
            person_ids = re.findall(r"control_number:([1-9][0-9]*)", query)
            hits = []
            for person_id in person_ids:
                response = self.responses.get(("authors", f"control_number:{person_id}", 1))
                if response:
                    hits.extend(response["hits"]["hits"])
            return {"hits": {"total": len(hits), "hits": copy.deepcopy(hits)}}
        return copy.deepcopy(self.responses.get((collection, query, page), {"hits": {"total": 0, "hits": []}}))


class FlakyClient(Client):
    def __init__(self, responses, fail_once: tuple[str, str, int]) -> None:
        super().__init__(responses)
        self.fail_once = fail_once

    def search(self, collection, query, *, size=25, page=1, sort=None, deadline=None):
        self.calls.append((collection, query, page))
        key = (collection, query, page)
        if key == self.fail_once:
            self.fail_once = ("", "", -1)
            raise RemoteError("upstream_unavailable", "temporary fixture failure")
        return copy.deepcopy(self.responses.get(key, {"hits": {"total": 0, "hits": []}}))


class DisappearingProfileClient(Client):
    """Return an endpoint once, then prove it cannot be refreshed currently."""

    def __init__(self, responses, missing_id: str) -> None:
        super().__init__(responses)
        self.missing_id = missing_id
        self.exact_seen = 0

    def search(self, collection, query, *, size=25, page=1, sort=None, deadline=None):
        self.calls.append((collection, query, page)); self.sizes.append(size)
        if collection == "authors" and " OR " in query:
            # A noisy batch must not confirm the absent requested ID.
            ids = [item for item in re.findall(r"control_number:([1-9][0-9]*)", query) if item != self.missing_id]
            hits = []
            for person_id in ids:
                response = self.responses.get(("authors", f"control_number:{person_id}", 1))
                if response:
                    hits.extend(response["hits"]["hits"])
            hits.append(person(99, name="Noise, N."))
            return {"hits": {"total": len(hits), "hits": copy.deepcopy(hits)}}
        if collection == "authors" and query == f"control_number:{self.missing_id}":
            self.exact_seen += 1
            if self.exact_seen > 1:
                return {"hits": {"total": 0, "hits": []}}
        return copy.deepcopy(self.responses.get((collection, query, page), {"hits": {"total": 0, "hits": []}}))


def profiles(*ids: int) -> dict[tuple[str, str, int], dict]:
    return {("authors", f"control_number:{item}", 1): page(person(item)) for item in ids}


def literature_query(person_id: int) -> str:
    return f"authors.record.$ref:{person_id} AND author_count:1->10"


def pair_query(left: int, right: int) -> str:
    return f"authors.record.$ref:{left} AND authors.record.$ref:{right} AND author_count:1->10"


def seed_frontiers(session: "DeepSession", left, right) -> None:
    """Place people on both HLBES frontiers without doing remote discovery."""
    session._run_requests = 0
    session._run_deadline = time.monotonic() + 10
    session._budget = budget()
    session._begin_proof(budget())
    for person_id in left:
        session._proof.left.add(str(person_id), 1, None)
    for person_id in right:
        session._proof.right.add(str(person_id), 1, None)


def budget(**overrides: int | float) -> DeepBudget:
    values = dict(max_seconds=30.0, max_requests=120, max_works=500, max_people=500,
                  page_size=1, max_pages_per_person=3)
    values.update(overrides)
    return DeepBudget(**values)


def test_multilevel_bidirectional_search_reaches_eight_hops_and_old_second_page() -> None:
    """The first useful source work appears only on page two, beyond six hops."""
    responses = profiles(*range(1, 10))
    # The exact endpoint pair has no direct work. Source page one is a recent
    # distraction; its historical route starts on page two.
    responses[("literature", literature_query(1), 1)] = page(paper(100, [1, 90]), total=2)
    responses[("literature", literature_query(1), 2)] = page(paper(101, [1, 2]), total=2)
    for left in range(2, 9):
        responses[("literature", literature_query(left), 1)] = page(paper(100 + left, [left, left + 1]))
    client = Client(responses)
    updates: list[dict] = []
    session = DeepSearch(client).start(1, 9, Filters(genealogy=False), progress=updates.append)
    try:
        result = session.run(budget())
    finally:
        session.close()

    assert result["status"] == "ok"
    assert result["paths"][0]["hops"] == 8
    assert [item["id"] for item in result["paths"][0]["people"]] == [str(item) for item in range(1, 10)]
    assert all(item["queryable"] is True for item in result["paths"][0]["people"])
    assert result["exact"] is False and result["exact_for_retrieved_graph"] is True
    assert result["global_shortest_proven"] is False
    assert any(call == ("literature", literature_query(1), 2) for call in client.calls)
    assert updates and {"people_explored", "works_retrieved", "elapsed_seconds", "stage"} <= set(updates[-1])


def test_pair_evidence_uses_local_dedup_and_min_shared_not_upstream_claims() -> None:
    responses = profiles(1, 2)
    responses[("literature", pair_query(1, 2), 1)] = page(
        paper(10, [1, 2], doi="10.example/version", author_count=8),
        paper(11, [1, 2], doi="10.example/version", author_count=3),
        paper(12, [1, 2], doi="10.example/distinct"),
    )
    session = DeepSearch(Client(responses)).start(1, 2, {"min_shared": 2})
    try:
        result = session.run(budget(page_size=10))
    finally:
        session.close()

    edge = result["paths"][0]["edges"][0]
    assert result["status"] == "ok" and edge["shared_works"] == 2
    assert edge["works"][0]["author_count"] == 8
    assert result["global_shortest_proven"] is True


def test_editor_occurrence_does_not_create_a_false_live_bridge_and_page_cap_is_ledgered() -> None:
    responses = profiles(1, 3)
    responses[("literature", literature_query(1), 1)] = page(paper(30, [1, 2], roles=["editor"]), total=2)
    responses[("literature", literature_query(1), 2)] = page(paper(31, [1, 2], roles=["editor"]), total=2)
    responses[("literature", literature_query(3), 1)] = page(paper(32, [2, 3], roles=["editor"]), total=2)
    responses[("literature", literature_query(3), 2)] = page(paper(33, [2, 3], roles=["editor"]), total=2)
    session = DeepSearch(Client(responses)).start(1, 3, {"genealogy": False})
    try:
        result = session.run(budget(max_pages_per_person=1))
        continued = session.run(budget(max_pages_per_person=1))
    finally:
        session.close()

    assert result["status"] == "search_incomplete" and result["paths"] == []
    assert any(item["literature_next_page"] >= 2 for item in continued["coverage"]["nodes"].values())


def test_cycles_do_not_repeat_nodes_and_sliced_continuation_keeps_ram_evidence() -> None:
    responses = profiles(1, 2, 3, 4)
    for node, neighbors in {1: [1, 2], 2: [2, 3], 3: [3, 1], 4: [3, 4]}.items():
        responses[("literature", literature_query(node), 1)] = page(paper(50 + node, neighbors))
    client = Client(responses)
    session = DeepSearch(client).start(1, 4, {"genealogy": False})
    try:
        # Split immediately after the first endpoint profile: bootstrap and
        # frontier cursors must remain retryable in this same RAM session.
        first = session.run(budget(max_requests=1))
        second = session.run(budget(max_requests=80))
    finally:
        session.close()

    assert first["status"] == "resource_limit" and first["can_continue"] is True
    assert second["status"] == "ok" and second["paths"][0]["hops"] == 3
    assert len({(kind, query, number) for kind, query, number in client.calls}) == len(client.calls)


def test_cancellation_does_not_contact_upstream_and_session_is_owner_thread_only() -> None:
    client = Client(profiles(1, 2))
    cancelled = threading.Event(); cancelled.set()
    session = DeepSearch(client).start(1, 2, cancel=cancelled)
    try:
        result = session.run(budget())
        assert result["status"] == "cancelled" and result["can_continue"] is False
        assert client.calls == []
    finally:
        session.close()


def test_frontier_page_error_restores_the_same_cursor_for_a_later_run() -> None:
    responses = profiles(1, 2, 3)
    responses[("literature", literature_query(1), 1)] = page(paper(401, [1, 2]))
    responses[("literature", literature_query(2), 1)] = page(paper(402, [2, 3]))
    flaky = FlakyClient(responses, ("literature", literature_query(1), 1))
    session = DeepSearch(flaky).start(1, 3, {"genealogy": False})
    try:
        first = session.run(budget())
        second = session.run(budget())
    finally:
        session.close()

    assert first["status"] == "search_incomplete" and first["can_continue"] is True
    assert second["status"] == "ok" and second["paths"][0]["hops"] == 2
    assert flaky.calls.count(("literature", literature_query(1), 1)) == 2


def test_audited_historical_overlay_requires_live_profiles_and_respects_genealogy() -> None:
    # Fowler -> Dirac is injected only by the independent historical overlay
    # after both exact public profiles have been fetched into this RAM session.
    responses = profiles(1035527, 1011729)
    session = DeepSearch(Client(responses)).start(1035527, 1011729, {"genealogy": True})
    try:
        result = session.run(budget())
    finally:
        session.close()

    assert result["status"] == "ok" and result["paths"][0]["hops"] == 1
    assert result["paths"][0]["edges"][0]["types"] == ["phd"]
    assert result["global_shortest_proven"] is True


def test_verified_route_is_retained_if_a_later_snapshot_attempt_hits_a_limit(monkeypatch) -> None:
    responses = profiles(1, 2)
    responses[("literature", pair_query(1, 2), 1)] = page(paper(501, [1, 2]))
    session = DeepSearch(Client(responses)).start(1, 2)
    try:
        found = session.run(budget())
        original_version = found["version"]
        monkeypatch.setattr(session, "_snapshot", lambda _: (_ for _ in ()).throw(DeepSearchError("resource_limit", "fixture limit")))
        retained = session._result("resource_limit", budget(), message="A later limit occurred.")
    finally:
        session.close()

    assert found["status"] == "ok" and retained["status"] == "resource_limit"
    assert retained["paths"] == found["paths"]
    assert retained["version"] == original_version


def test_historical_overlay_audit_survives_deep_live_coverage_replacement() -> None:
    responses = profiles(1, 2)
    responses[("literature", pair_query(1, 2), 1)] = page(paper(187326, [1, 2]))
    session = DeepSearch(Client(responses)).start(1, 2, {"genealogy": False})
    try:
        result = session.run(budget())
    finally:
        session.close()

    exclusions = result["coverage"]["historical_coauthorship_exclusions"]
    assert result["status"] == "search_incomplete" and result["paths"] == []
    assert len(exclusions) == 1
    assert {key: exclusions[0][key] for key in ("work_id", "source_id", "reason", "source_url")} == {
        "work_id": "187326", "source_id": "187326",
        "reason": "special_session_participant_list_not_research_coauthorship",
        "source_url": "https://inspirehep.net/literature/187326",
    }
    assert result["version"].startswith("sha256:")


def test_page_five_is_visited_within_one_generous_run_and_genealogy_off_skips_reverse_queries() -> None:
    responses = profiles(1, 2)
    for number in range(1, 5):
        responses[("literature", literature_query(1), number)] = page(paper(600 + number, [1, 90 + number]), total=5)
    responses[("literature", literature_query(1), 5)] = page(paper(605, [1, 2]), total=5)
    client = Client(responses)
    session = DeepSearch(client).start(1, 2, {"genealogy": False})
    try:
        result = session.run(budget(max_pages_per_person=4, max_requests=80))
    finally:
        session.close()

    assert result["status"] == "ok" and result["paths"][0]["hops"] == 1
    assert ("literature", literature_query(1), 5) in client.calls
    assert not any(kind == "authors" and query.startswith("advisors.record.$ref:") for kind, query, _ in client.calls)


def test_live_frontier_stitches_a_guide_component_without_copying_stale_guide_evidence() -> None:
    """Target 9 is absent from the guide; its live neighbour reaches bridge 3."""
    guide = {
        "version": "saved-guide", "coverage": {}, "phd": [],
        "people": [{"id": str(item), "name": f"Guide {item}"} for item in (1, 2, 3)],
        "works": [
            {"id": "guide-12", "authors": ["1", "2"], "author_count": 2, "year": 2000,
             "document_types": ["article"]},
            {"id": "guide-23", "authors": ["2", "3"], "author_count": 2, "year": 2000,
             "document_types": ["article"]},
        ],
    }
    responses = profiles(1, 2, 3, 9)
    responses[("literature", literature_query(9), 1)] = page(paper(900, [9, 3]))
    responses[("literature", pair_query(1, 2), 1)] = page(paper(801, [1, 2]))
    responses[("literature", pair_query(2, 3), 1)] = page(paper(802, [2, 3]))
    client = Client(responses)
    session = DeepSearch(client, guide).start(1, 9, {"genealogy": False})
    try:
        result = session.run(budget())
    finally:
        session.close()

    assert result["status"] == "ok"
    assert [item["id"] for item in result["paths"][0]["people"]] == ["1", "2", "3", "9"]
    assert result["coverage"]["guide_used"] is True
    assert result["coverage"]["guide_candidates_verified"] == 2
    displayed_work_ids = {work["id"] for edge in result["paths"][0]["edges"] for work in edge["works"]}
    assert displayed_work_ids == {"801", "802", "900"}
    assert ("literature", pair_query(1, 2), 1) in client.calls
    assert ("literature", pair_query(2, 3), 1) in client.calls


def test_identity_guard_rejects_shorter_bad_initial_route_then_finds_longer_verified_route() -> None:
    """A hard initial mismatch removes the early route without inventing a substitute."""
    names = {1: "Start, A.", 2: "Kaufman, B.", 3: "Middle, C.", 4: "End, D.", 5: "Later, E."}
    responses = {
        ("authors", f"control_number:{person_id}", 1): page(person(person_id, name=(
            "Kaufman, S. B." if person_id == 2 else names[person_id]
        )))
        for person_id in names
    }
    responses[("literature", literature_query(1), 1)] = page(paper(100, [1, 2], names=names), total=2)
    responses[("literature", literature_query(1), 2)] = page(paper(101, [1, 3], names=names), total=2)
    responses[("literature", literature_query(4), 1)] = page(paper(102, [2, 4], names=names), total=2)
    responses[("literature", literature_query(4), 2)] = page(paper(103, [5, 4], names=names), total=2)
    responses[("literature", literature_query(3), 1)] = page(paper(104, [3, 5], names=names))
    responses[("literature", literature_query(5), 1)] = page(paper(105, [5, 4], names=names))
    client = Client(responses)
    session = DeepSearch(client).start(1, 4, {"genealogy": False})
    try:
        result = session.run(budget(max_requests=100))
    finally:
        session.close()

    assert result["status"] == "ok"
    assert [person["id"] for person in result["paths"][0]["people"]] == ["1", "3", "5", "4"]
    assert all(person["queryable"] is True for person in result["paths"][0]["people"])
    conflicts = result["coverage"]["identity_conflicts"]
    assert {(row["person"], row["source_name"]) for row in conflicts} == {
        ("2", "Kaufman, B."),
    }
    assert any(" OR " in query for kind, query, _ in client.calls if kind == "authors")
    assert all(size <= 100 for size in client.sizes)


def test_validation_budget_resume_never_returns_unvalidated_direct_path() -> None:
    responses = profiles(1, 2)
    responses[("literature", pair_query(1, 2), 1)] = page(paper(200, [1, 2]))
    session = DeepSearch(Client(responses)).start(1, 2, {"genealogy": False})
    try:
        paused = session.run(budget(max_requests=3))
        resumed = session.run(budget(max_requests=20))
    finally:
        session.close()

    assert paused["status"] == "resource_limit" and paused["can_continue"] is True
    assert paused["paths"] == []
    assert paused["coverage"]["identity_validation"]["pending"] is True
    assert resumed["status"] == "ok" and resumed["paths"][0]["hops"] == 1
    assert all(person["queryable"] is True for person in resumed["paths"][0]["people"])


def test_missing_current_profile_rejects_direct_connection_and_false_batch_hit() -> None:
    responses = profiles(1, 2)
    responses[("literature", pair_query(1, 2), 1)] = page(paper(300, [1, 2]))
    client = DisappearingProfileClient(responses, "2")
    session = DeepSearch(client).start(1, 2, {"genealogy": False})
    try:
        result = session.run(budget(max_requests=40))
    finally:
        session.close()

    assert result["status"] == "search_incomplete" and result["paths"] == []
    assert result["global_shortest_proven"] is False
    assert result["coverage"]["identity_unverified_profile_exclusions"] == [{
        "work_id": "300", "person": "2", "reason": "current_public_profile_not_found",
    }]
    assert any(" OR " in query for kind, query, _ in client.calls if kind == "authors")
    assert 25 in client.sizes


def test_cross_frontier_query_connects_discovered_groups_before_individual_crawls() -> None:
    responses = profiles(1, 2, 3, 4)
    responses[("literature", literature_query(1), 1)] = page(paper(401, [1, 2]))
    responses[("literature", literature_query(4), 1)] = page(paper(402, [3, 4]))
    query = (
        "(authors.record.$ref:1 OR authors.record.$ref:2) AND "
        "(authors.record.$ref:3 OR authors.record.$ref:4) AND author_count:1->10"
    )
    responses[("literature", query, 1)] = page(paper(403, [2, 3]))
    client = Client(responses)
    session = DeepSearch(client, discovery_hints=True).start(1, 4, {"genealogy": False})
    try:
        result = session.run(budget(max_requests=40))
    finally:
        session.close()

    assert result["status"] == "ok"
    assert [person["id"] for person in result["paths"][0]["people"]] == ["1", "2", "3", "4"]
    assert ("literature", query, 1) in client.calls
    assert client.calls.count(("literature", query, 1)) == 1


def test_guarded_shortcut_immediately_validates_an_already_loaded_longer_route() -> None:
    names = {1: "Start, A.", 2: "Kaufman, B.", 3: "Middle, C.", 4: "End, D."}
    responses = {
        ("authors", f"control_number:{person_id}", 1): page(person(person_id, name=(
            "Kaufman, S. B." if person_id == 2 else names[person_id]
        )))
        for person_id in names
    }
    # Both the bad two-hop shortcut and the valid three-hop replacement are
    # already in the first pages when the guard sees the incompatible profile.
    responses[("literature", literature_query(1), 1)] = page(
        paper(501, [1, 2], names=names), paper(502, [1, 3], names=names), total=1)
    responses[("literature", literature_query(4), 1)] = page(
        paper(503, [2, 4], names=names), paper(504, [3, 4], names=names), total=1)
    client = Client(responses)
    session = DeepSearch(client).start(1, 4, {"genealogy": False})
    try:
        result = session.run(budget(max_requests=30))
    finally:
        session.close()

    assert result["status"] == "ok"
    assert [person["id"] for person in result["paths"][0]["people"]] == ["1", "3", "4"]
    assert not any(query == literature_query(2) for kind, query, _ in client.calls if kind == "literature")


def test_failed_cross_frontier_request_is_retryable_in_the_same_session() -> None:
    query = (
        "(authors.record.$ref:1 OR authors.record.$ref:2) AND "
        "(authors.record.$ref:3 OR authors.record.$ref:4) AND author_count:1->10"
    )
    responses = {("literature", query, 1): page(paper(601, [2, 3]))}
    client = FlakyClient(responses, ("literature", query, 1))
    session = DeepSearch(client).start(1, 4, {"genealogy": False})
    try:
        seed_frontiers(session, ("1", "2"), ("3", "4"))
        session._run_requests = 0; session._bridge_queries_this_run = 0
        session._run_deadline = time.monotonic() + 10
        assert session._cross_frontier(budget()) is False
        assert (("1", "2"), ("3", "4")) not in session._bridge_queries_seen
        assert session._bridge_disabled_this_run is True
        session._run_requests = 0; session._bridge_queries_this_run = 0; session._bridge_disabled_this_run = False
        assert session._cross_frontier(budget()) is True
    finally:
        session.close()

    assert client.calls.count(("literature", query, 1)) == 2


def test_optional_cross_frontier_failure_falls_back_to_regular_bfs() -> None:
    responses = profiles(1, 2, 3)
    responses[("literature", literature_query(1), 1)] = page(paper(701, [1, 2]))
    responses[("literature", literature_query(3), 1)] = page(paper(702, [2, 3]))
    cross = (
        "(authors.record.$ref:1 OR authors.record.$ref:2) AND "
        "(authors.record.$ref:3) AND author_count:1->10"
    )
    client = FlakyClient(responses, ("literature", cross, 1))
    session = DeepSearch(client, discovery_hints=True).start(1, 3, {"genealogy": False})
    try:
        result = session.run(budget(max_requests=40))
    finally:
        session.close()

    assert result["status"] == "ok"
    assert [person["id"] for person in result["paths"][0]["people"]] == ["1", "2", "3"]
    assert result["coverage"]["cross_frontier"]["failures"][0]["code"] in {"upstream_unavailable", "search_incomplete"}
    assert ("literature", literature_query(3), 1) in client.calls


def test_id_only_navigation_hints_propose_but_do_not_supply_an_arbitrary_route() -> None:
    responses = profiles(10, 20, 30)
    responses[("literature", pair_query(10, 20), 1)] = page(paper(810, [10, 20]))
    responses[("literature", pair_query(20, 30), 1)] = page(paper(820, [20, 30]))
    session = DeepSearch(Client(responses), suggestion_pairs=[("10", "20"), ("20", "30")]).start(
        10, 30, {"genealogy": False}
    )
    try:
        # Configuring an ID-only corridor does not insert people, works, or
        # edges into this query's in-memory evidence database.
        assert session.connection.execute("select count(*) from source_records").fetchone()[0] == 0
        result = session.run(budget(max_requests=40))
    finally:
        session.close()

    assert result["status"] == "ok"
    assert [person["id"] for person in result["paths"][0]["people"]] == ["10", "20", "30"]
    assert result["coverage"]["navigation_suggestion_pairs"] == 2
    works = {work["id"] for edge in result["paths"][0]["edges"] for work in edge["works"]}
    assert works == {"810", "820"}


def test_stale_or_filtered_navigation_hint_never_creates_path_evidence() -> None:
    responses = profiles(1, 2)
    # The hint suggests the pair, but this work violates the selected cap.
    responses[("literature", pair_query(1, 2), 1)] = page(paper(901, [1, 2], author_count=11))
    session = DeepSearch(Client(responses), suggestion_pairs=(("1", "2"),)).start(
        1, 2, {"genealogy": False, "max_authors": 10}
    )
    try:
        result = session.run(budget(max_requests=40))
    finally:
        session.close()

    assert result["status"] == "search_incomplete" and result["paths"] == []
    assert result["global_shortest_proven"] is False


def test_nonexistent_navigation_hint_person_is_not_invented_as_evidence() -> None:
    responses = profiles(1, 2)
    # Neither suggested edge has current live evidence, and the intermediate
    # record does not exist.  A navigation ID is never allowed into the graph
    # simply because a caller supplied it as a useful historical direction.
    session = DeepSearch(
        Client(responses), suggestion_pairs=(("1", "999"), ("999", "2"))
    ).start(1, 2, {"genealogy": False})
    try:
        result = session.run(budget(max_requests=40))
        raw_ids = {
            row[0]
            for row in session.connection.execute(
                "select recid from source_records where collection='authors'"
            )
        }
    finally:
        session.close()

    assert result["status"] == "search_incomplete" and result["paths"] == []
    assert "999" not in raw_ids


def test_a_short_slice_never_truncates_a_request_below_the_network_timeout() -> None:
    """The slice allowance decides whether to start work, not how long a
    started request may take. A 1 s slice must not hand the client a 1 s
    deadline and then log the resulting abort as an upstream failure."""
    from hepgraph.remote import NETWORK_TIMEOUT_SECONDS

    seen: list[float] = []

    class DeadlineClient(Client):
        def search(self, collection, query, *, size=25, page=1, sort=None, deadline=None):
            seen.append(deadline - time.monotonic())
            return super().search(collection, query, size=size, page=page, sort=sort, deadline=deadline)

    session = DeepSearch(DeadlineClient(profiles(1, 2))).start(1, 2, {"genealogy": False})
    try:
        session.run(budget(max_seconds=1))
    finally:
        session.close()
    assert seen and all(remaining >= NETWORK_TIMEOUT_SECONDS - 0.5 for remaining in seen), seen


def test_a_deadline_refusal_is_a_checkpoint_not_a_logged_failure() -> None:
    class Refusing(Client):
        def search(self, collection, query, *, size=25, page=1, sort=None, deadline=None):
            if collection == "literature":
                raise RemoteError("resource_limit", "request deadline would be exceeded by global rate pacing",
                                  deadline=True)
            return super().search(collection, query, size=size, page=page, sort=sort, deadline=deadline)

    session = DeepSearch(Refusing(profiles(1, 2))).start(1, 2, {"genealogy": False})
    try:
        result = session.run(budget())
        assert result["status"] == "resource_limit" and result["can_continue"] is True
        assert result["coverage"]["failures"] == [], "our own clock is not an upstream failure"
    finally:
        session.close()
