"""Regression coverage for the three public author-count modes and continuation."""
from __future__ import annotations

import copy
import re

import pytest

from hepgraph.deep_search import DeepBudget, DeepSearch, DeepSession
from hepgraph.graph import Filters, Graph, GraphError


def _person(person_id: int) -> dict:
    return {"id": str(person_id), "metadata": {
        "control_number": str(person_id), "name": {"value": f"Person {person_id}"},
        "ids": [], "positions": [], "advisors": [],
    }}


def _paper(work_id: int, people: list[int], count: int) -> dict:
    return {"id": str(work_id), "metadata": {
        "control_number": str(work_id), "titles": [{"title": f"Work {work_id}"}],
        "document_type": ["article"],
        "authors": [{"record": {"$ref": f"https://inspirehep.net/api/authors/{person_id}"},
                     "full_name": f"Person {person_id}", "inspire_roles": ["author"], "affiliations": []}
                    for person_id in people],
        "author_count": count, "earliest_date": "2022-01-01", "preprint_date": "2022-01-01",
        "dois": [], "arxiv_eprints": [],
    }}


def _page(*hits: dict, total: int | None = None) -> dict:
    return {"hits": {"total": len(hits) if total is None else total, "hits": list(hits)}}


def _snapshot() -> dict:
    return {
        "version": "author-mode-fixture",
        "people": [{"id": str(person_id), "name": f"Person {person_id}"} for person_id in range(1, 103)],
        "works": [
            {"id": "ten", "authors": ["1", "2"], "author_count": 10, "year": 2022, "document_types": ["article"]},
            {"id": "eleven", "authors": ["1", "3"], "author_count": 11, "year": 2022, "document_types": ["article"]},
            {"id": "large", "authors": ["1", "4"], "author_count": 102, "year": 2022, "document_types": ["article"]},
        ],
        "phd": [],
    }


def test_author_count_modes_are_inclusive_and_filter_keys_include_the_lower_bound() -> None:
    small = Filters.from_dict({"max_authors": 10})
    large = Filters.from_dict({"min_authors": 11, "max_authors": None})
    all_authors = Filters.from_dict({"max_authors": None})

    assert small.to_dict()["min_authors"] == 1
    assert large.to_dict() == {
        "max_authors": None, "min_shared": 1, "year_start": None,
        "year_end": None, "genealogy": True, "min_authors": 11,
    }
    assert set(Graph(_snapshot(), small).works) == {"ten"}
    assert set(Graph(_snapshot(), large).works) == {"eleven", "large"}
    assert set(Graph(_snapshot(), all_authors).works) == {"ten", "eleven", "large"}

    for values in ({"min_authors": 0}, {"min_authors": 100_001}, {"min_authors": 11, "max_authors": 10}):
        with pytest.raises(GraphError):
            Filters.from_dict(values)
    with pytest.raises(GraphError):
        Filters(max_authors=10, min_authors=11)


def test_large_team_upstream_queries_are_open_ended_and_use_small_pages() -> None:
    large = Filters(min_authors=11, max_authors=None, genealogy=False)
    assert DeepSession.literature_query("1", large).endswith("author_count:11+")
    assert DeepSession.pair_query("1", "2", large).endswith("author_count:11+")
    assert DeepSession._cross_query(["1"], ["2"], large).endswith("author_count:11+")


class _LaterPageClient:
    """Mock a real-world large-team direct work that appears after page one."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, int, int]] = []
        self.profiles = {str(person_id): _page(_person(person_id)) for person_id in (1, 2)}
        self.direct = "authors.record.$ref:1 AND authors.record.$ref:2 AND author_count:11+"

    def search(self, collection: str, query: str, *, size: int = 25, page: int = 1, **_: object) -> dict:
        self.calls.append((collection, query, page, size))
        if collection == "authors":
            match = re.fullmatch(r"control_number:(\d+)", query)
            return copy.deepcopy(self.profiles.get(match.group(1) if match else "", _page()))
        if collection == "literature" and query == self.direct and page == 1:
            # Five earlier small-team records occupy the first large-mode page.
            return _page(*[_paper(100 + number, [1, 2, *range(3, 11)], 10) for number in range(5)], total=6)
        if collection == "literature" and query == self.direct and page == 2:
            # 102 is intentionally above the old >10 query cap and must not
            # be lost simply because it appears after the first page.
            return _page(_paper(2150122, list(range(1, 103)), 102), total=6)
        return _page()


def test_large_team_direct_evidence_on_a_later_page_is_retrieved_and_verified() -> None:
    client = _LaterPageClient()
    session = DeepSearch(client).start(1, 2, Filters(min_authors=11, max_authors=None, genealogy=False))
    budget = DeepBudget(max_seconds=30, max_requests=40, max_works=500, max_people=500, page_size=25, max_pages_per_person=4)
    try:
        result = session.run(budget)
    finally:
        session.close()

    assert result["status"] == "ok"
    assert result["paths"][0]["hops"] == 1
    assert result["paths"][0]["edges"][0]["works"][0]["author_count"] == 102
    assert result["coverage"]["direct_pair"] == {
        "pages_checked": 2, "last_page": 2, "records_seen": 6,
        "reported_total": 6, "reported_total_exact": True, "complete": True,
    }
    direct_calls = [call for call in client.calls if call[0] == "literature" and call[1] == client.direct]
    assert [(page, size) for _, _, page, size in direct_calls] == [(1, 5), (2, 5)]


class _ContinuationClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, int]] = []
        self.responses = {
            **{("authors", f"control_number:{person_id}", 1): _page(_person(person_id)) for person_id in range(1, 5)},
            ("literature", "authors.record.$ref:1 AND authors.record.$ref:4 AND author_count:1->10", 1): _page(),
            ("literature", "authors.record.$ref:1 AND author_count:1->10", 1): _page(_paper(1, [1, 2], 2)),
            ("literature", "authors.record.$ref:2 AND author_count:1->10", 1): _page(_paper(2, [2, 3], 2)),
            ("literature", "authors.record.$ref:3 AND author_count:1->10", 1): _page(),
            ("literature", "authors.record.$ref:4 AND author_count:1->10", 1): _page(_paper(3, [3, 4], 2)),
        }

    def search(self, collection: str, query: str, *, page: int = 1, **_: object) -> dict:
        self.calls.append((collection, query, page))
        return copy.deepcopy(self.responses.get((collection, query, page), _page()))


def test_verified_three_hop_route_can_continue_without_replaying_it() -> None:
    client = _ContinuationClient()
    session = DeepSearch(client).start(1, 4, Filters(genealogy=False))
    budget = DeepBudget(max_seconds=30, max_requests=60, max_works=500, max_people=500, page_size=10, max_pages_per_person=4)
    try:
        first = session.run(budget)
        second = session.run(budget)
    finally:
        session.close()

    assert first["status"] == "ok" and first["paths"][0]["hops"] == 3
    assert first["can_continue"] is True
    assert first["global_shortest_proven"] is False
    assert second["status"] == "ok" and second["paths"] == first["paths"]
    assert second["can_continue"] is False
    direct = "authors.record.$ref:1 AND authors.record.$ref:4 AND author_count:1->10"
    assert client.calls.count(("literature", direct, 1)) == 1


def test_genealogy_off_keeps_phd_as_coauthor_context_without_creating_a_phd_edge() -> None:
    relation = {"adviser": "1", "student": "2", "degree": "PhD", "source_record": "profile-2"}
    coauthor_snapshot = {
        "version": "context", "people": [{"id": "1"}, {"id": "2"}],
        "works": [{"id": "work", "authors": ["1", "2"], "author_count": 2,
                   "year": 2022, "document_types": ["article"]}],
        "phd": [relation],
    }
    edge = Graph(coauthor_snapshot, Filters(genealogy=False))._edge("1", "2")
    assert edge is not None
    assert edge["types"] == ["coauthor"]
    assert edge["phd"] == [relation]

    phd_only = {**coauthor_snapshot, "works": []}
    assert Graph(phd_only, Filters(genealogy=False))._edge("1", "2") is None


class _LowerBoundTotalClient:
    """A `gte` direct-pair total supports retrieval, never absence proof."""

    def __init__(self) -> None:
        self.responses = {
            **{("authors", f"control_number:{person_id}", 1): _page(_person(person_id)) for person_id in (1, 2, 3)},
            ("literature", "authors.record.$ref:1 AND authors.record.$ref:3 AND author_count:1->10", 1): {
                "hits": {"total": {"value": 10_000, "relation": "gte"}, "hits": []},
            },
            ("literature", "authors.record.$ref:1 AND author_count:1->10", 1): _page(_paper(11, [1, 2], 2)),
            ("literature", "authors.record.$ref:3 AND author_count:1->10", 1): _page(_paper(12, [2, 3], 2)),
            ("literature", "authors.record.$ref:2 AND author_count:1->10", 1): _page(),
        }

    def search(self, collection: str, query: str, *, page: int = 1, **_: object) -> dict:
        return copy.deepcopy(self.responses.get((collection, query, page), _page()))


def test_lower_bound_direct_total_cannot_prove_a_verified_two_hop_route_is_global() -> None:
    session = DeepSearch(_LowerBoundTotalClient()).start(1, 3, Filters(genealogy=False))
    budget = DeepBudget(max_seconds=30, max_requests=50, max_works=500, max_people=500, page_size=10, max_pages_per_person=4)
    try:
        result = session.run(budget)
    finally:
        session.close()

    assert result["status"] == "ok" and result["paths"][0]["hops"] == 2
    assert result["global_shortest_proven"] is False
    assert result["coverage"]["direct_pair"]["reported_total"] is None
    assert result["coverage"]["direct_pair"]["reported_total_exact"] is False
    assert result["coverage"]["direct_pair"]["complete"] is False


class _ShortExactPageClient:
    def __init__(self) -> None:
        self.responses = {
            **{("authors", f"control_number:{person_id}", 1): _page(_person(person_id)) for person_id in (1, 3)},
            # The claimed exact total is two, but page one is short and page
            # two is empty. A caller must not use nominal page arithmetic to
            # turn that inconsistent response into a proof of no direct work.
            ("literature", "authors.record.$ref:1 AND authors.record.$ref:3 AND author_count:1->10", 1): _page(_paper(21, [1, 2], 2), total=2),
            ("literature", "authors.record.$ref:1 AND authors.record.$ref:3 AND author_count:1->10", 2): _page(total=2),
        }

    def search(self, collection: str, query: str, *, page: int = 1, **_: object) -> dict:
        return copy.deepcopy(self.responses.get((collection, query, page), _page()))


def test_short_exact_direct_pages_never_complete_the_direct_absence_proof() -> None:
    session = DeepSearch(_ShortExactPageClient()).start(1, 3, Filters(genealogy=False))
    budget = DeepBudget(max_seconds=30, max_requests=4, max_works=500, max_people=500, page_size=10, max_pages_per_person=4)
    try:
        result = session.run(budget)
    finally:
        session.close()

    assert result["status"] == "resource_limit"
    assert result["global_shortest_proven"] is False
    assert result["coverage"]["direct_pair"] == {
        "pages_checked": 2, "last_page": 2, "records_seen": 1,
        "reported_total": 2, "reported_total_exact": True, "complete": False,
    }
