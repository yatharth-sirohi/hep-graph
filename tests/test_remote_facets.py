"""Adversarial tests for bounded INSPIRE coauthor-facet discovery."""
from __future__ import annotations

import json
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse

import pytest

from hepgraph.remote import (MAX_FACET_BUCKETS, MAX_RESPONSE_BYTES,
                             REQUEST_INTERVAL_SECONDS, RemoteClient, RemoteError)


@pytest.fixture(autouse=True)
def isolate_injected_clock_domains() -> None:
    """Prevent stale synthetic-clock IDs from leaking between unit tests."""
    RemoteClient._pace_states.clear()
    yield
    RemoteClient._pace_states.clear()


class Clock:
    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


def facets_response(
    *,
    total: object = 4,
    buckets: object = None,
    omitted: object = 0,
    error: object = 0,
) -> bytes:
    if buckets is None:
        buckets = [
            {"key": "983328_Edward Witten", "doc_count": 4},
            {"key": "989440_Nathan Seiberg", "doc_count": 2},
        ]
    return json.dumps(
        {
            "hits": {"total": total, "hits": []},
            "aggregations": {
                "author": {
                    "buckets": buckets,
                    "sum_other_doc_count": omitted,
                    "doc_count_error_upper_bound": error,
                    "meta": {"private_display_configuration": "must be discarded"},
                },
                "unrequested_private_aggregation": {"value": "must be discarded"},
            },
        }
    ).encode()


def test_fixed_facets_endpoint_encoded_query_sanitization_and_memory_cache() -> None:
    clock = Clock()
    calls: list[tuple[str, float]] = []

    def transport(url: str, timeout: float) -> bytes:
        calls.append((url, timeout))
        return facets_response(total={"value": 4, "relation": "eq"})

    client = RemoteClient(transport=transport, clock=clock, sleep=clock.sleep)
    query = "authors.record.$ref:983328 AND author_count:1->10"
    first = client.coauthors(query)
    assert first == {
        "authors": [{"id": "983328", "count": 4}, {"id": "989440", "count": 2}],
        "truncated": False,
        "total": 4,
    }
    assert "Witten" not in json.dumps(first)
    first["authors"][0]["count"] = 999
    assert client.coauthors(query)["authors"][0]["count"] == 4
    assert len(calls) == 1
    parsed = urlparse(calls[0][0])
    assert parsed.scheme == "https"
    assert parsed.netloc == "inspirehep.net"
    assert parsed.path == "/api/literature/facets"
    assert parse_qs(parsed.query) == {"q": [query]}
    assert calls[0][1] == 8.0
    assert client.cache_info()["entries"] == 1
    assert client.cache_info()["storage"] == "memory"


def test_facets_share_global_pacing_and_bounded_lru_with_search_requests() -> None:
    clock = Clock()
    calls: list[tuple[str, float]] = []

    def transport(url: str, timeout: float) -> bytes:
        calls.append((url, clock.now))
        if urlparse(url).path.endswith("/facets"):
            return facets_response()
        return json.dumps(
            {"hits": {"total": 1, "hits": [{"id": "1", "metadata": {"control_number": 1}}]}}
        ).encode()

    left = RemoteClient(transport=transport, clock=clock, sleep=clock.sleep, cache_entries=2)
    right = RemoteClient(transport=transport, clock=clock, sleep=clock.sleep, cache_entries=2)
    left.coauthors("authors.record.$ref:1")
    right.search("authors", "recid:2")
    assert [called_at for _, called_at in calls] == [0.0, REQUEST_INTERVAL_SECONDS]
    assert clock.sleeps == [REQUEST_INTERVAL_SECONDS]

    # Cache reads do not consume pacing, and facet entries use the same LRU.
    left.coauthors("authors.record.$ref:1")
    assert len(calls) == 2
    left.coauthors("authors.record.$ref:3")
    left.coauthors("authors.record.$ref:4")
    assert left.cache_info()["entries"] == 2
    left.coauthors("authors.record.$ref:1")
    assert len(calls) == 5  # query 1 was the least-recently-used entry and was fetched again


def test_facets_429_sets_shared_cooldown_and_honors_deadline_and_inflight_limits() -> None:
    clock = Clock()
    attempts: list[str] = []

    def transport(url: str, timeout: float) -> bytes:
        attempts.append(url)
        if len(attempts) == 1:
            raise HTTPError(url, 429, "slow down", hdrs={"Retry-After": "7"}, fp=None)
        return facets_response()

    first = RemoteClient(transport=transport, clock=clock, sleep=clock.sleep)
    second = RemoteClient(transport=transport, clock=clock, sleep=clock.sleep)
    with pytest.raises(RemoteError) as limited:
        first.coauthors("authors.record.$ref:1")
    assert limited.value.code == "resource_limit"
    assert "7 seconds" in limited.value.message
    with pytest.raises(RemoteError) as deadline:
        second.coauthors("authors.record.$ref:2", deadline=6.0)
    assert deadline.value.code == "resource_limit"
    assert "cooldown" in deadline.value.message
    assert len(attempts) == 1
    assert second.coauthors("authors.record.$ref:2", deadline=9.0)["total"] == 4
    assert len(attempts) == 2 and clock.sleeps == [7.0]

    acquired = [second._inflight.acquire(blocking=False) for _ in range(8)]
    try:
        assert all(acquired)
        with pytest.raises(RemoteError) as queue_error:
            second.coauthors("authors.record.$ref:3")
        assert queue_error.value.code == "resource_limit"
    finally:
        for _ in acquired:
            second._inflight.release()


def test_duplicate_ids_are_deduplicated_without_inflating_counts_and_truncation_is_conservative() -> None:
    buckets = [
        {"key": "42_First Display Name", "doc_count": 3},
        {"key": "7_Another Author", "doc_count": 2},
        {"key": "42_Second Display Name", "doc_count": 5},
        {"key": "42_Third Display Name", "doc_count": 4},
    ]
    client = RemoteClient(
        transport=lambda *_: facets_response(
            total={"value": 9, "relation": "eq"}, buckets=buckets, omitted=0, error=1
        ),
        clock=Clock(),
        sleep=lambda _: None,
    )
    result = client.coauthors("authors.record.$ref:42")
    assert result == {
        "authors": [{"id": "42", "count": 5}, {"id": "7", "count": 2}],
        "truncated": True,
        "total": 9,
    }
    assert "Display Name" not in json.dumps(result)

    omitted_client = RemoteClient(
        transport=lambda *_: facets_response(omitted=6, error=0), clock=Clock(), sleep=lambda _: None
    )
    assert omitted_client.coauthors("authors.record.$ref:9")["truncated"] is True


def test_unresolvable_name_only_buckets_are_skipped_and_mark_coverage_incomplete() -> None:
    buckets = [
        {"key": "NOREC_A. Researcher", "doc_count": 3},
        {"key": "Name Only", "doc_count": 2},
        {"key": "01_Invalid Numeric Prefix", "doc_count": 2},
        {"key": "7_Resolved Author", "doc_count": 1},
    ]
    client = RemoteClient(
        transport=lambda *_: facets_response(buckets=buckets), clock=Clock(), sleep=lambda _: None
    )
    assert client.coauthors("authors.record.$ref:7") == {
        "authors": [{"id": "7", "count": 1}],
        "truncated": True,
        "total": 4,
    }


def test_lower_bound_total_marks_truncation_and_bucket_count_is_bounded() -> None:
    lower_bound = RemoteClient(
        transport=lambda *_: facets_response(total={"value": 4, "relation": "gte"}),
        clock=Clock(),
        sleep=lambda _: None,
    )
    result = lower_bound.coauthors("authors.record.$ref:1")
    assert result["total"] == 4 and result["truncated"] is True

    maximum = [{"key": f"{index + 1}_Author {index + 1}", "doc_count": 1} for index in range(MAX_FACET_BUCKETS)]
    bounded = RemoteClient(
        transport=lambda *_: facets_response(total=MAX_FACET_BUCKETS, buckets=maximum),
        clock=Clock(),
        sleep=lambda _: None,
    )
    assert len(bounded.coauthors("authors.record.$ref:2")["authors"]) == MAX_FACET_BUCKETS


@pytest.mark.parametrize(
    "body",
    [
        b"not json",
        json.dumps([]).encode(),
        json.dumps({"aggregations": {"author": {"buckets": [], "sum_other_doc_count": 0, "doc_count_error_upper_bound": 0}}}).encode(),
        facets_response(total=True),
        facets_response(total=-1),
        facets_response(total={"relation": "eq"}),
        facets_response(total={"value": 1}),
        json.dumps({"hits": {"total": 1}, "aggregations": {}}).encode(),
        json.dumps({"hits": {"total": 1}, "aggregations": {"author": []}}).encode(),
        facets_response(buckets={}),
        facets_response(omitted=None),
        facets_response(omitted=-1),
        facets_response(error=True),
        facets_response(error=-1),
        facets_response(buckets=["not-a-bucket"]),
        facets_response(buckets=[{"key": 1, "doc_count": 1}]),
        facets_response(buckets=[{"key": "1_Name", "doc_count": True}]),
        facets_response(buckets=[{"key": "1_Name", "doc_count": 0}]),
        facets_response(buckets=[{"key": "1_Name", "doc_count": -1}]),
        facets_response(buckets=[{"key": "1_Name", "doc_count": "1"}]),
        facets_response(total=0, buckets=[{"key": "1_Name", "doc_count": 1}]),
        facets_response(total=1, buckets=[{"key": "1_Name", "doc_count": 2}]),
        facets_response(
            total=MAX_FACET_BUCKETS + 1,
            buckets=[
                {"key": f"{index + 1}_Author {index + 1}", "doc_count": 1}
                for index in range(MAX_FACET_BUCKETS + 1)
            ],
        ),
    ],
)
def test_malformed_facets_responses_fail_closed_without_cache(body: bytes) -> None:
    client = RemoteClient(transport=lambda *_: body, clock=Clock(), sleep=lambda _: None)
    with pytest.raises(RemoteError) as failure:
        client.coauthors("authors.record.$ref:1")
    assert failure.value.code == "upstream_unavailable"
    assert client.cache_info()["entries"] == 0


def test_oversize_facets_response_uses_shared_four_mib_limit() -> None:
    client = RemoteClient(
        transport=lambda *_: b"x" * (MAX_RESPONSE_BYTES + 1), clock=Clock(), sleep=lambda _: None
    )
    with pytest.raises(RemoteError) as failure:
        client.coauthors("authors.record.$ref:1")
    assert failure.value.code == "resource_limit"
    assert client.cache_info()["entries"] == 0


@pytest.mark.parametrize("query", ["", "x" * 4097, "one\ntwo", "bad\x7fquery"])
def test_invalid_facet_query_never_reaches_transport(query: str) -> None:
    client = RemoteClient(
        transport=lambda *_: pytest.fail("transport must not run"), clock=Clock(), sleep=lambda _: None
    )
    with pytest.raises(RemoteError) as failure:
        client.coauthors(query)
    assert failure.value.code == "resource_limit"
