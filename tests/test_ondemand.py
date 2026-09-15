"""Independent, offline tests for the bounded live graph adapter."""

from __future__ import annotations

import copy

import pytest

import hepgraph.ondemand as ondemand_module
from hepgraph.ondemand import OnDemand
from hepgraph.remote import RemoteError


def ref(recid: int | str) -> dict[str, str]:
    return {"$ref": f"https://inspirehep.net/api/authors/{recid}"}


def author(recid: int | str, *, name: str | None = None, advisers: list[dict] | None = None) -> dict:
    return {
        "id": str(recid),
        "metadata": {
            "control_number": str(recid),
            "name": {"value": name or f"Person {recid}"},
            "ids": [],
            "positions": [],
            "advisors": advisers or [],
        },
    }


def work(recid: int | str, author_ids: list[int | str], *, roles: list[str] | None = None,
         author_count: int | None = None, doi: str | None = None, earliest_date: str = "2020-01-01") -> dict:
    return {
        "id": str(recid),
        "metadata": {
            "control_number": str(recid),
            "titles": [{"title": f"Work {recid}"}],
            "document_type": ["article"],
            "authors": [
                {"full_name": f"Person {person_id}", "record": ref(person_id),
                 "inspire_roles": roles or ["author"], "affiliations": []}
                for person_id in author_ids
            ],
            "author_count": author_count if author_count is not None else len(author_ids),
            "earliest_date": earliest_date,
            "preprint_date": earliest_date,
            "dois": [{"value": doi}] if doi else [],
            "arxiv_eprints": [],
        },
    }


def page(*hits: dict, total: int | None = None) -> dict:
    return {"hits": {"total": len(hits) if total is None else total, "hits": list(hits)}}


class FakeClient:
    """A response map that implements RemoteClient's public call shape."""

    def __init__(self, responses: dict[tuple[str, str], dict | Exception] | None = None) -> None:
        self.responses = responses or {}
        self.calls: list[tuple[str, str, int, int, str | None, float | None]] = []

    def search(self, collection: str, query: str, *, size: int = 25, page: int = 1,
               sort: str | None = None, deadline: float | None = None) -> dict:
        self.calls.append((collection, query, size, page, sort, deadline))
        response = self.responses.get((collection, query), {"hits": {"total": 0, "hits": []}})
        if isinstance(response, Exception):
            raise response
        return copy.deepcopy(response)


def person_queries(*profiles: dict) -> dict[tuple[str, str], dict]:
    return {("authors", f"control_number:{item['id']}"): page(item) for item in profiles}


def test_search_is_memory_only_and_returns_sanitized_profile(monkeypatch: pytest.MonkeyPatch) -> None:
    calls_to_open: list[str] = []
    original_open = ondemand_module.open_db

    def tracking_open(path: str):
        calls_to_open.append(str(path))
        return original_open(path)

    monkeypatch.setattr(ondemand_module, "open_db", tracking_open)
    client = FakeClient({("authors", '(name.value:"Grace" OR name.name_variants:"Grace" OR name.preferred_name:"Grace") AND (name.value:"Hopper" OR name.name_variants:"Hopper" OR name.preferred_name:"Hopper")'): page(author(7, name="Grace Hopper"))})
    result = OnDemand(client).search("Grace Hopper")

    assert calls_to_open == [":memory:"]
    assert result["status"] == "ok"
    assert len(result["results"]) == 1
    assert result["results"][0] | {"queryable": True} == result["results"][0]
    assert {key: result["results"][0][key] for key in ("id", "name", "orcid", "affiliations")} == {
        "id": "7", "name": "Grace Hopper", "orcid": None, "affiliations": []
    }
    assert result["counts_scope"] == "retrieved"
    assert result["coverage"]["retrieved"] == {"profiles": 1, "works": 0, "people": 1}
    assert client.calls[0][0:5] == ("authors", '(name.value:"Grace" OR name.name_variants:"Grace" OR name.preferred_name:"Grace") AND (name.value:"Hopper" OR name.name_variants:"Hopper" OR name.preferred_name:"Hopper")', 25, 1, None)
    assert isinstance(client.calls[0][5], float)


def test_paths_are_exact_only_in_retrieved_graph_and_use_numeric_reference_clause() -> None:
    responses = person_queries(author(1), author(3))
    responses.update({
        ("literature", "authors.record.$ref:1 AND author_count:1->10"): page(work(11, [1, 2])),
        ("literature", "authors.record.$ref:3 AND author_count:1->10"): page(work(23, [2, 3])),
    })
    result = OnDemand(FakeClient(responses)).find_paths("1", "3")

    assert result["status"] == "ok"
    assert result["exact"] is False
    assert result["exact_for_retrieved_graph"] is True
    assert result["global_shortest_proven"] is False
    assert result["scope"] == "Shortest path is exact only within the retrieved live graph."
    assert result["paths"][0]["hops"] == 2
    assert [person["id"] for person in result["paths"][0]["people"]] == ["1", "2", "3"]
    assert result["coverage"]["partial"] is False


def test_direct_and_self_paths_are_the_only_global_proofs() -> None:
    responses = person_queries(author(1), author(2))
    responses[("literature", "authors.record.$ref:1 AND author_count:1->10")] = page(work(12, [1, 2]))
    responses[("literature", "authors.record.$ref:2 AND author_count:1->10")] = page(work(12, [1, 2]))
    engine = OnDemand(FakeClient(responses))

    direct = engine.find_paths(1, 2)
    self_path = engine.find_paths(1, 1)

    assert direct["paths"][0]["hops"] == 1 and direct["global_shortest_proven"] is True
    assert direct["exact"] is False and direct["exact_for_retrieved_graph"] is True
    assert self_path["paths"][0]["hops"] == 0 and self_path["global_shortest_proven"] is True
    assert self_path["exact"] is False and self_path["exact_for_retrieved_graph"] is True


def test_missing_route_is_search_incomplete_not_a_claim_of_global_absence() -> None:
    responses = person_queries(author(1), author(3))
    responses.update({
        ("literature", "authors.record.$ref:1 AND author_count:1->10"): page(work(11, [1, 2])),
        ("literature", "authors.record.$ref:3 AND author_count:1->10"): page(work(34, [3, 4])),
    })
    result = OnDemand(FakeClient(responses)).find_paths(1, 3)

    assert result["status"] == "search_incomplete"
    assert result["paths"] == []
    assert result["exact"] is False
    assert "not evidence" in result["message"]
    assert result["global_shortest_proven"] is False


def test_profile_and_neighborhood_keep_full_counts_apply_roles_filters_and_deduplicate() -> None:
    responses = person_queries(author(1))
    # The two source records are identifier versions of one work.  An editor
    # reference must not become a collaboration edge, while author_count stays
    # the full author list count rather than the resolved ordinary-author count.
    responses[("literature", "authors.record.$ref:1 AND author_count:1->10")] = page(
        work(100, [1, 2], author_count=9, doi="10.example/same", earliest_date="2020-02"),
        work(101, [1, 2], author_count=3, doi="10.example/same", earliest_date="2020-02-03"),
        work(102, [1, 3], roles=["editor"], author_count=2),
    )
    engine = OnDemand(FakeClient(responses))
    profile = engine.profile(1)
    neighborhood = engine.neighborhood(1, {"year_start": 2020, "year_end": 2020})

    assert profile["status"] == "ok"
    assert profile["indexed_publications"] == profile["eligible_publications"] == profile["retrieved_publications"] == 1
    assert len(profile["collaborators"]) == 1
    assert profile["collaborators"][0]["shared_works"] == 1
    assert profile["collaborators"][0]["person"]["id"] == "2"
    assert profile["collaborators"][0]["person"]["queryable"] is True
    assert ("authors", "advisors.record.$ref:1") in {(item[0], item[1]) for item in engine.client.calls}
    assert neighborhood["status"] == "ok"
    assert [person["id"] for person in neighborhood["people"]] == ["1", "2"]
    edge_work = neighborhood["edges"][0]["works"][0]
    assert edge_work["author_count"] == 9
    assert edge_work["date"] == "2020-02"  # earliest INSPIRE date keeps its documented precision.


def test_min_shared_and_phd_ties_use_only_explicit_same_entry_evidence() -> None:
    advisor = author(1)
    student = author(2, advisers=[
        {"degree_type": "PhD", "record": ref(1), "curated_relation": True},
        # This is deliberately not a PhD relation and must not add a second edge.
        {"degree_type": "master", "record": ref(9), "curated_relation": True},
    ])
    responses = person_queries(advisor, student)
    responses.update({
        ("literature", "authors.record.$ref:1 AND author_count:1->10"): page(work(10, [1, 2]), work(11, [1, 2])),
        ("literature", "authors.record.$ref:2 AND author_count:1->10"): page(work(10, [1, 2]), work(11, [1, 2])),
        ("authors", "advisors.record.$ref:1"): page(student),
    })
    client = FakeClient(responses)
    coauthor = OnDemand(client).find_paths(1, 2, {"min_shared": 2, "genealogy": False})
    phd = OnDemand(client).find_paths(1, 2, {"max_authors": 1})

    assert coauthor["status"] == "ok"
    assert coauthor["paths"][0]["edges"][0]["shared_works"] == 2
    assert phd["status"] == "ok"
    assert phd["paths"][0]["edges"][0]["types"] == ["phd"]
    assert ("authors", "advisors.record.$ref:1") not in {(item[0], item[1]) for item in client.calls}


def test_pair_lookup_finds_old_direct_works_before_recent_endpoint_pages() -> None:
    """A pair search supplies historical shared evidence in three requests."""
    responses = person_queries(author(1), author(2))
    pair_query = "authors.record.$ref:1 AND authors.record.$ref:2 AND author_count:1->10"
    responses[("literature", pair_query)] = page(
        # Two distinct old works establish min_shared=2. The DOI version must
        # collapse into the first work rather than inflate the shared count.
        work(10, [1, 2], author_count=9, doi="10.example/old", earliest_date="1999-01"),
        work(11, [1, 2], author_count=3, doi="10.example/old", earliest_date="1999-01-02"),
        work(12, [1, 2], doi="10.example/older", earliest_date="1998"),
    )
    client = FakeClient(responses)
    result = OnDemand(client).find_paths(1, 2, {"min_shared": 2})

    assert result["status"] == "ok"
    assert result["paths"][0]["hops"] == 1
    assert result["paths"][0]["edges"][0]["shared_works"] == 2
    assert result["paths"][0]["edges"][0]["works"][0]["author_count"] == 9
    assert result["global_shortest_proven"] is True
    assert len(client.calls) == 3
    assert [(call[0], call[1]) for call in client.calls] == [
        ("authors", "control_number:1"),
        ("authors", "control_number:2"),
        ("literature", pair_query),
    ]


def test_partial_malformed_and_upstream_failures_are_truthful_and_bounded() -> None:
    partial = OnDemand(FakeClient({("authors", '(name.value:"Ada" OR name.name_variants:"Ada" OR name.preferred_name:"Ada")'): page(author(1), total=26)})).search("Ada")
    malformed = OnDemand(FakeClient({("authors", '(name.value:"Ada" OR name.name_variants:"Ada" OR name.preferred_name:"Ada")'): {"hits": {"total": 1, "hits": [{"id": "x", "metadata": {}}]}}})).search("Ada")
    offline = OnDemand(FakeClient({("authors", '(name.value:"Ada" OR name.name_variants:"Ada" OR name.preferred_name:"Ada")'): RemoteError("upstream_unavailable", "offline")})).search("Ada")

    assert partial["status"] == "ambiguous" and partial["coverage"]["partial"] is True
    assert malformed["status"] == "search_incomplete" and malformed["results"] == []
    assert offline["status"] == "upstream_unavailable" and "offline" in offline["message"]


def test_request_and_work_caps_prevent_unbounded_live_expansion() -> None:
    responses = person_queries(author(1))
    responses[("literature", "authors.record.$ref:1 AND author_count:1->10")] = page(work(1, [1]), work(2, [1]))
    engine = OnDemand(FakeClient(responses))
    engine.MAX_WORKS = 1
    result = engine.profile(1)

    assert result["status"] == "resource_limit"
    assert "work limit" in result["message"]


def test_unavailable_global_features_and_invalid_numeric_ids_are_explicit() -> None:
    engine = OnDemand(FakeClient())
    assert engine.ancestry(1)["status"] == "unavailable"
    assert engine.centrality("degree")["status"] == "unavailable"
    with pytest.raises(ValueError, match="numeric author record ID"):
        engine.profile("Ada Lovelace")
    with pytest.raises(ValueError, match="numeric author record ID"):
        engine.profile("١")
    with pytest.raises(ValueError, match="numeric author record ID"):
        engine.profile(0)


def test_search_returns_only_direct_public_hits_and_supports_numeric_exact_ids() -> None:
    student = author(2, name="Matheus Hostert", advisers=[
        {"degree_type": "PhD", "record": ref(1), "curated_relation": True},
    ])
    adviser = author(1, name="Adviser Placeholder")
    client = FakeClient({
        ("authors", '(name.value:"Matheus" OR name.name_variants:"Matheus" OR name.preferred_name:"Matheus") AND (name.value:"Hostert" OR name.name_variants:"Hostert" OR name.preferred_name:"Hostert")'): page(student),
        ("authors", "control_number:2"): page(student),
        # This is not reached by search, but makes the regression robust if a
        # future implementation mistakenly follows advisor entries.
        ("authors", "control_number:1"): page(adviser),
    })
    engine = OnDemand(client)
    name_result = engine.search("Matheus Hostert")
    id_result = engine.search("2")

    assert [person["id"] for person in name_result["results"]] == ["2"]
    assert [person["id"] for person in id_result["results"]] == ["2"]
    assert all(person["id"] != "1" for person in name_result["results"])
