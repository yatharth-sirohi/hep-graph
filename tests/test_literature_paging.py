"""The literature page size is a correctness surface, not only a speed knob.

Page N means different records at a different size, so anything that changes
size mid-stream can skip or repeat works. These tests pin the rules that keep
a larger page safe.
"""
from __future__ import annotations

from pathlib import Path
import sys
import time

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from hepgraph.deep_search import (MAX_LITERATURE_PAGE, PROFILE_PAGE_SIZE, DeepBudget,
                                  DeepSearch, DeepSearchError)
from hepgraph.graph import Filters
from hepgraph.remote import MAX_SIZE, RemoteError
from test_deep_search import Client, literature_query, page, paper, person, profiles


def budget(**overrides):
    values = dict(max_seconds=30.0, max_requests=720, max_works=20000, max_people=20000,
                  page_size=MAX_LITERATURE_PAGE, max_pages_per_person=50)
    values.update(overrides)
    return DeepBudget(**values)


class Paging(Client):
    """Serve a fixed corpus with real pagination at whatever size is asked."""

    def __init__(self, works_by_person, profiles_map, *, total_override=None, cap_bytes=None):
        super().__init__(profiles_map)
        self.works_by_person = works_by_person
        self.total_override = total_override
        self.cap_bytes = cap_bytes
        self.sizes_seen = []
        self.pages_seen = []

    def search(self, collection, query, *, size=25, page=1, sort=None, deadline=None):
        if collection != "literature":
            return super().search(collection, query, size=size, page=page, sort=sort, deadline=deadline)
        self.sizes_seen.append(size)
        self.pages_seen.append((page, size))
        if self.cap_bytes is not None and size > self.cap_bytes:
            raise RemoteError("resource_limit", "INSPIRE response exceeded the 4 MiB limit")
        for person, works in self.works_by_person.items():
            if f"authors.record.$ref:{person} " in query + " ":
                window = works[(page - 1) * size:page * size]
                total = self.total_override if self.total_override is not None else len(works)
                return {"hits": {"total": total, "hits": list(window)}}
        return {"hits": {"total": 0, "hits": []}}


def corpus(count):
    """One source with `count` qualifying works, each with a distinct partner."""
    works = [paper(1000 + index, [1, 100 + index]) for index in range(count)]
    people = [1, 2] + [100 + index for index in range(count)]
    return works, profiles(*people)


def neighbours_of(client, source, **budget_overrides):
    session = DeepSearch(client).start(source, 2, Filters(genealogy=False))
    try:
        session._run_requests = 0
        session._run_deadline = time.monotonic() + 30
        session._budget = budget(**budget_overrides)
        session._begin_proof(session._budget)
        found = None
        for _ in range(400):
            found = session._oracle.neighborhood(str(source))
            if found.status == "complete":
                break
        return found, client.sizes_seen
    finally:
        session.close()


def test_the_api_page_ceiling_is_the_measured_one():
    assert MAX_LITERATURE_PAGE == 1000
    assert MAX_SIZE >= MAX_LITERATURE_PAGE
    assert PROFILE_PAGE_SIZE <= 100


@pytest.mark.parametrize("count", [1, 9, 10, 99, 100, 101, 250, 1000, 1001])
def test_a_neighbourhood_is_identical_at_every_page_size(count):
    """The whole point: size changes cost, never membership."""
    works, people = corpus(count)
    expected = {str(100 + index) for index in range(count)}
    seen = {}
    for size in (5, 100, 1000):
        client = Paging({"1": works}, dict(people))
        found, sizes = neighbours_of(client, 1, page_size=size)
        assert found.status == "complete", f"size {size} failed to certify {count} works"
        assert set(found.members) == expected, f"size {size} lost neighbours"
        seen[size] = len(sizes)
    # Bigger pages must cost strictly fewer requests once there is more than one.
    if count > 100:
        assert seen[1000] < seen[100] < seen[5]


def test_a_cursor_keeps_one_page_size_for_its_whole_pagination():
    works, people = corpus(250)
    client = Paging({"1": works}, dict(people))
    neighbours_of(client, 1, page_size=1000)
    literature_sizes = set(client.sizes_seen)
    assert len(literature_sizes) == 1, f"pagination changed size mid-stream: {literature_sizes}"


def test_an_oversized_page_shrinks_and_still_certifies_everything():
    """A 4 MiB rejection must not end a query or lose a neighbour."""
    works, people = corpus(300)
    client = Paging({"1": works}, dict(people), cap_bytes=200)
    found, sizes = neighbours_of(client, 1, page_size=1000)
    assert found.status == "complete"
    assert set(found.members) == {str(100 + index) for index in range(300)}
    assert max(sizes) > 200 and min(sizes) <= 200, "it should have tried big, then shrunk"


def test_shrinking_restarts_pagination_rather_than_resuming_at_the_wrong_offset():
    works, people = corpus(300)
    client = Paging({"1": works}, dict(people), cap_bytes=200)
    found, sizes = neighbours_of(client, 1, page_size=1000)
    assert found.status == "complete"
    # Nothing may be missing: a resumed page number at a new size would skip.
    assert len(found.members) == 300


def test_a_short_page_with_an_exact_total_still_ends_the_query():
    works, people = corpus(10)
    client = Paging({"1": works}, dict(people))
    found, _ = neighbours_of(client, 1, page_size=1000)
    assert found.status == "complete" and len(found.members) == 10


def test_a_page_beyond_the_result_window_cannot_certify():
    """page * size may not exceed 10,000, so a bigger set stays incomplete."""
    works, people = corpus(300)
    # Claim far more results than can ever be paged to.
    client = Paging({"1": works}, dict(people), total_override=50_000)
    found, _ = neighbours_of(client, 1, page_size=5)
    assert found.status != "complete"


def test_budget_rejects_a_page_size_above_the_api_maximum():
    with pytest.raises(DeepSearchError):
        budget(page_size=MAX_LITERATURE_PAGE + 1).validate()
    budget(page_size=MAX_LITERATURE_PAGE).validate()


# ------------------------------------------- what the independent review broke
def test_the_page_ceiling_follows_the_measured_payload_not_a_flat_threshold():
    """A 100-author page of 1000 records would be megabytes, not kilobytes."""
    from hepgraph.deep_search import DeepSession

    small = DeepSession.page_ceiling_for(Filters(max_authors=10))
    medium = DeepSession.page_ceiling_for(Filters(max_authors=100))
    broad = DeepSession.page_ceiling_for(Filters(max_authors=None))
    assert small > medium > broad, (small, medium, broad)
    assert broad >= 5 and small <= MAX_LITERATURE_PAGE
    for authors in (1, 5, 10, 11, 50, 100, 1000, None):
        ceiling = DeepSession.page_ceiling_for(Filters(max_authors=authors))
        per_record = 700 + 175 * (authors if authors is not None else 3000)
        assert ceiling * per_record <= 4 * 1024 * 1024, f"{authors} authors would overflow"


def test_wire_bytes_are_reported_separately_from_cache_residency():
    """The benchmark's byte column must measure traffic, not what is cached."""
    from hepgraph.remote import RemoteClient

    class Clock:
        now = 0.0
        def __call__(self): return self.now

    served = []
    def transport(url, timeout):
        body = b'{"hits": {"total": 1, "hits": [{"id": "1", "metadata": {"control_number": 1}}]}}'
        served.append(len(body))
        return body

    client = RemoteClient(transport=transport, clock=Clock(), sleep=lambda _: None)
    client.search("literature", "recid:1")
    layers = client.cache_info()["layers"]
    assert layers["literature"]["wire_bytes"] == sum(served)
    assert layers["literature"]["wire_bytes"] != layers["literature"]["bytes"]


# ------------------------------- what the final pre-merge review found broken
def test_a_floor_count_at_the_window_ceiling_reads_on_without_restarting(monkeypatch):
    """INSPIRE reports gte only when a set fills the result window.

    No page size can reach the empty page that would end such a query, and the
    first attempt at this looped for ever: every expansion reset the cursor to
    page one. It must page normally instead, read everything the window can
    serve, and stop there marked incomplete - stopping after one page would be
    honest about completeness but would find an order of magnitude fewer
    collaborators than the engine it replaced.
    """
    import hepgraph.deep_search as deep_search

    monkeypatch.setattr(deep_search, "MAX_RESULT_WINDOW", 300)
    monkeypatch.setattr(deep_search, "GTE_PAGE_SIZE", 50)
    works, people = corpus(400)
    client = Paging({"1": works}, dict(people),
                    total_override={"value": 300, "relation": "gte"})
    session = DeepSearch(client).start(1, 2, Filters(genealogy=False))
    try:
        session._run_requests = 0
        session._run_deadline = time.monotonic() + 30
        session._budget = budget(page_size=100)
        session._begin_proof(session._budget)
        for _ in range(40):
            found = session._oracle.neighborhood("1")
            if found.status == "complete":
                break
        cursor = session._oracle.cursors["1"]
    finally:
        session.close()
    assert found.status != "complete", "a set that fills the window is not exhausted"
    assert "literature_window" in cursor.incomplete
    assert client.pages_seen == sorted(set(client.pages_seen)), "no page re-read, no restart"
    assert len(found.members) >= 250, "it must read the window, not stop at one page"


def test_a_count_that_over_reports_stops_paging_without_certifying():
    """A recid served twice, or a record the projection drops, must not strand."""
    works, people = corpus(100)
    client = Paging({"1": works[:99]}, dict(people), total_override=100)
    session = DeepSearch(client).start(1, 2, Filters(genealogy=False))
    try:
        session._run_requests = 0
        session._run_deadline = time.monotonic() + 30
        session._budget = budget(page_size=10)
        session._begin_proof(session._budget)
        for _ in range(60):
            found = session._oracle.neighborhood("1")
            if found.status == "complete":
                break
        cursor = session._oracle.cursors["1"]
    finally:
        session.close()
    assert found.status != "complete", "99 of a promised 100 is not exhaustion"
    assert "literature_short" in cursor.incomplete
    assert cursor.literature_page <= 12, "it must stop, not walk to the window"


def test_the_prefetch_page_size_matches_what_the_search_will_request():
    """A different size is a different cache key, so the warm-up is wasted."""
    from hepgraph.prefetch import PreparationJobs

    class Idle:
        def search(self, *a, **k): return {"hits": {"total": 0, "hits": []}}
        def coauthors(self, *a, **k): return {"authors": [], "truncated": False, "total": 0}

    jobs = PreparationJobs(Idle())
    for authors in (1, 5, 10, 11, 50, 100, 101, 1000, None):
        filters = Filters(max_authors=authors)
        session = DeepSearch(Idle()).start(1, 2, filters)
        try:
            session._budget = DeepBudget.standard()
            assert jobs._literature_size(filters) == session._literature_size(session._budget), \
                f"prefetch and search disagree at max_authors={authors}"
        finally:
            session.close()
    jobs.shutdown()


def test_the_reverse_query_pages_through_all_advisees():
    """Mutation guard: without page_size=REVERSE_PAGE_SIZE this stops at 100.

    The reverse page is pinned to 100 records while budget.page_size is 1000,
    so measuring the page against the budget makes the short-page rule fire on
    page one and truncates genealogy to a person's first hundred advisees.
    """
    from hepgraph.deep_search import REVERSE_PAGE_SIZE

    advisees = [str(500 + index) for index in range(250)]
    people = profiles(*([1, 2] + [int(item) for item in advisees]))
    responses = dict(people)
    responses[("literature", literature_query(1), 1)] = page(total=0)
    responses[("literature", literature_query(2), 1)] = page(total=0)

    class Reverse(Client):
        def __init__(self, responses):
            super().__init__(responses)
            self.reverse = []

        def search(self, collection, query, *, size=25, page=1, sort=None, deadline=None):
            if collection == "authors" and query.startswith("advisors.record.$ref:1"):
                self.reverse.append((page, size))
                window = advisees[(page - 1) * size:page * size]
                return {"hits": {"total": len(advisees),
                                 "hits": [person(item) for item in window]}}
            if collection == "authors" and query.startswith("advisors.record.$ref:"):
                return {"hits": {"total": 0, "hits": []}}
            return super().search(collection, query, size=size, page=page, sort=sort, deadline=deadline)

    client = Reverse(responses)
    session = DeepSearch(client).start(1, 2, Filters(genealogy=True))
    try:
        session._run_requests = 0
        session._run_deadline = time.monotonic() + 30
        session._budget = budget()
        session._begin_proof(session._budget)
        cursor = session._oracle.cursor_for("1", profile_done=True)
        for _ in range(12):
            session._page_person(cursor, session._budget)
            if cursor.reverse_done:
                break
    finally:
        session.close()
    assert [size for _, size in client.reverse] == [REVERSE_PAGE_SIZE] * 3
    assert len(cursor.reverse_seen) == 250, "every advisee must be paged through"
    assert "reverse_short" not in cursor.incomplete
