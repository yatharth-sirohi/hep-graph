"""Adversarial unit tests for the memory-only INSPIRE boundary."""
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import format_datetime
import json
import math
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse

import pytest

from hepgraph.pipeline import AUTHOR_FIELDS, LITERATURE_FIELDS
from hepgraph.remote import (MIN_REQUEST_INTERVAL_SECONDS, MAX_RESPONSE_BYTES,
                             REQUEST_INTERVAL_SECONDS, RemoteClient, RemoteError)


class Clock:
    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


def response(*, total: int | dict = 1, metadata: object | None = None) -> bytes:
    return json.dumps({"hits": {"total": total, "hits": [{"id": "1", "metadata": {"control_number": 1} if metadata is None else metadata}]}}).encode()


def test_identical_concurrent_requests_share_one_transport_and_return_isolated_values() -> None:
    entered, release = threading.Event(), threading.Event()
    calls = 0

    def transport(url: str, timeout: float) -> bytes:
        nonlocal calls
        calls += 1
        entered.set()
        assert release.wait(1)
        return response()

    client = RemoteClient(transport=transport, clock=lambda: time.monotonic(), sleep=time.sleep)
    values: list[dict] = []
    failures: list[Exception] = []

    def request() -> None:
        try:
            values.append(client.search("authors", "control_number:1", size=100, sort="mostrecent"))
        except Exception as exc:  # pragma: no cover - asserted below
            failures.append(exc)

    leader = threading.Thread(target=request)
    follower = threading.Thread(target=request)
    leader.start()
    assert entered.wait(1)
    follower.start()
    deadline = time.monotonic() + 1
    while client.cache_info()["coalesced"] < 1 and time.monotonic() < deadline:
        time.sleep(.002)
    release.set()
    leader.join(1); follower.join(1)

    assert failures == [] and calls == 1 and len(values) == 2
    values[0]["hits"]["hits"][0]["metadata"]["control_number"] = "changed"
    assert values[1]["hits"]["hits"][0]["metadata"]["control_number"] == "1"
    info = client.cache_info()
    assert info["coalesced"] == 1 and info["upstream_requests"] == 1
    assert info["layers"]["authors"]["coalesced"] == 1


def test_coalesced_waiter_deadline_does_not_cancel_the_leader() -> None:
    entered, release = threading.Event(), threading.Event()
    client = RemoteClient(
        transport=lambda url, timeout: (entered.set(), release.wait(1), response())[-1],
        clock=lambda: time.monotonic(), sleep=time.sleep,
    )
    leader_value: list[dict] = []
    leader = threading.Thread(target=lambda: leader_value.append(
        client.search("literature", "recid:1", deadline=time.monotonic() + 1)))
    leader.start()
    assert entered.wait(1)
    with pytest.raises(RemoteError, match="identical INSPIRE request") as expired:
        client.search("literature", "recid:1", deadline=time.monotonic() + .03)
    assert expired.value.code == "resource_limit"
    release.set(); leader.join(1)
    assert leader_value[0]["hits"]["total"] == 1
    assert client.cache_info()["wait_deadlines"] == 1


def test_coalesced_failure_wakes_followers_but_does_not_poison_a_retry() -> None:
    entered, release = threading.Event(), threading.Event()
    calls = 0

    def transport(url: str, timeout: float) -> bytes:
        nonlocal calls
        calls += 1
        if calls == 1:
            entered.set()
            assert release.wait(1)
            raise URLError("temporary")
        return response()

    clock = Clock()
    client = RemoteClient(transport=transport, clock=clock, sleep=clock.sleep)
    failures: list[RemoteError] = []

    def request() -> None:
        try:
            client.search("literature", "recid:1")
        except RemoteError as exc:
            failures.append(exc)

    leader = threading.Thread(target=request)
    follower = threading.Thread(target=request)
    leader.start(); assert entered.wait(1); follower.start()
    deadline = time.monotonic() + 1
    while client.cache_info()["coalesced"] < 1 and time.monotonic() < deadline:
        time.sleep(.002)
    release.set(); leader.join(1); follower.join(1)

    assert len(failures) == 2 and calls == 1 and client.cache_info()["entries"] == 0
    assert client.search("literature", "recid:1")["hits"]["total"] == 1
    assert calls == 2 and client.cache_info()["entries"] == 1


def test_fixed_endpoint_allowlisted_fields_encoded_params_and_memory_cache() -> None:
    clock = Clock()
    calls: list[tuple[str, float]] = []

    def transport(url: str, timeout: float) -> bytes:
        calls.append((url, timeout))
        return response()

    client = RemoteClient(transport=transport, clock=clock, sleep=clock.sleep, cache_entries=2)
    first = client.search("authors", 'name.value:"Ada Lovelace"', size=25, page=2, sort="mostrecent")
    first["hits"]["hits"][0]["metadata"]["control_number"] = "mutated"
    second = client.search("authors", 'name.value:"Ada Lovelace"', size=25, page=2, sort="mostrecent")
    assert len(calls) == 1
    assert second["hits"]["hits"][0]["metadata"]["control_number"] == "1"
    parsed = urlparse(calls[0][0])
    assert parsed.scheme == "https" and parsed.netloc == "inspirehep.net" and parsed.path == "/api/authors"
    parameters = parse_qs(parsed.query)
    assert parameters == {"q": ['name.value:"Ada Lovelace"'], "size": ["25"], "page": ["2"], "sort": ["mostrecent"], "fields": [AUTHOR_FIELDS]}
    info = client.cache_info()
    assert {key: info[key] for key in ("bytes", "limit", "entries", "ttl_seconds", "storage", "persistent")} == {
        "bytes": info["bytes"], "limit": 8 * 1024 * 1024, "entries": 2,
        "ttl_seconds": 900.0, "storage": "memory", "persistent": False,
    }
    assert info["layers"]["authors"]["entries"] == 2
    assert info["layers"]["authors"]["record_entries"] == 1
    client.clear_cache()
    assert client.cache_info()["entries"] == 0 and client.cache_info()["storage"] == "memory"


def test_author_record_cache_reuses_normalized_sanitized_hit_across_query_shapes() -> None:
    clock = Clock()
    calls: list[str] = []
    raw = {
        "hits": {"total": 1, "hits": [{
            "id": 7,
            "metadata": {
                "control_number": 7,
                "name": {"value": "Curie, Marie", "name_variants": ["Marie Curie"]},
                "ids": [{"schema": "ORCID", "value": "0000-0000-0000-0007"}],
                "emails": ["private@example.test"],
                "private_notes": ["secret"],
            },
        }]},
    }

    def transport(url: str, timeout: float) -> bytes:
        calls.append(url)
        return json.dumps(raw).encode()

    client = RemoteClient(transport=transport, clock=clock, sleep=clock.sleep)
    client.search("authors", 'name.value:"Curie"', size=25, page=2, sort="bestmatch")
    exact = client.search("authors", "control_number:7", size=1, page=1, sort="mostrecent")

    assert len(calls) == 1
    assert exact["hits"]["total"] == 1
    assert exact["hits"]["hits"][0]["id"] == "7"
    assert exact["hits"]["hits"][0]["metadata"]["control_number"] == "7"
    assert "private@example" not in json.dumps(exact) and "private_notes" not in json.dumps(exact)
    info = client.cache_info()
    assert info["layers"]["authors"]["record_entries"] == 1
    assert info["layers"]["authors"]["record_hits"] == 1


def test_author_record_cache_satisfies_complete_batches_but_not_missing_or_unpageable_sets() -> None:
    clock = Clock()
    calls: list[str] = []

    def author_page(ids: list[str], total: int | None = None) -> bytes:
        return json.dumps({"hits": {"total": len(ids) if total is None else total, "hits": [
            {"id": person_id, "metadata": {"control_number": person_id, "name": {"value": f"Person {person_id}"}}}
            for person_id in ids
        ]}}).encode()

    def transport(url: str, timeout: float) -> bytes:
        calls.append(url)
        query = parse_qs(urlparse(url).query)["q"][0]
        if query == 'name.value:"seed"':
            return author_page(["1", "2"])
        if query == "control_number:1 OR control_number:3":
            return author_page(["1", "3"])
        if query == "control_number:1 OR control_number:2" and "size=1" in url:
            return author_page(["1"], total=2)
        if query == "control_number:1 OR control_number:2" and "page=2" in url:
            return author_page([], total=2)
        raise AssertionError(f"unexpected transport request: {url}")

    client = RemoteClient(transport=transport, clock=clock, sleep=clock.sleep)
    client.search("authors", 'name.value:"seed"', size=25)
    cached_batch = client.search(
        "authors", "control_number:2 OR control_number:1", size=2, sort="mostrecent")
    assert [hit["id"] for hit in cached_batch["hits"]["hits"]] == ["2", "1"]
    assert len(calls) == 1

    # One missing ID sends the whole exact batch upstream. It is not inferred
    # absent from the cached subset, and the returned profile becomes reusable.
    client.search("authors", "control_number:1 OR control_number:3", size=25)
    assert len(calls) == 2
    assert client.search("authors", "control_number:3", size=1)["hits"]["hits"][0]["id"] == "3"
    assert len(calls) == 2

    # A batch larger than the requested page and a later page need upstream
    # ordering, even when every involved record is cached.
    client.search("authors", "control_number:1 OR control_number:2", size=1)
    client.search("authors", "control_number:1 OR control_number:2", size=2, page=2)
    assert len(calls) == 4


def test_author_record_cache_does_not_poison_errors_and_expires_with_shared_ttl() -> None:
    clock = Clock()
    calls = 0

    def transport(url: str, timeout: float) -> bytes:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise URLError("temporary")
        return response()

    client = RemoteClient(
        transport=transport, clock=clock, sleep=clock.sleep, ttl_seconds=2)
    with pytest.raises(RemoteError):
        client.search("authors", "control_number:1", size=100, sort="mostrecent")
    assert client.cache_info()["layers"]["authors"]["record_entries"] == 0

    assert client.search("authors", "control_number:1", size=1)["hits"]["hits"][0]["id"] == "1"
    assert client.search("authors", "control_number:1", size=100, sort="bestmatch")["hits"]["total"] == 1
    assert calls == 2
    clock.now += 2.1
    client.search("authors", "control_number:1", size=1)
    assert calls == 3


def test_new_author_hit_replaces_record_cache_without_merging_alias_queries() -> None:
    clock = Clock()
    calls: list[str] = []

    def transport(url: str, timeout: float) -> bytes:
        query = parse_qs(urlparse(url).query)["q"][0]
        calls.append(query)
        display = "Old Name" if query == 'name.value:"old"' else "Current Name"
        return json.dumps({"hits": {"total": 1, "hits": [{
            "id": "8", "metadata": {"control_number": "8", "name": {"value": display}},
        }]}}).encode()

    client = RemoteClient(transport=transport, clock=clock, sleep=clock.sleep)
    client.search("authors", 'name.value:"old"')
    client.search("authors", 'name.name_variants:"new"')
    exact = client.search("authors", "control_number:8", size=1)

    assert calls == ['name.value:"old"', 'name.name_variants:"new"']
    assert exact["hits"]["hits"][0]["metadata"]["name"]["value"] == "Current Name"
    # Each alias response remains a distinct transport-cache entry; the shared
    # record key only serves explicit numeric-ID queries.
    assert client.search("authors", 'name.value:"old"')["hits"]["hits"][0]["metadata"]["name"]["value"] == "Old Name"
    assert len(calls) == 2


def test_ttl_lru_and_global_pacing_across_clients_sharing_a_clock() -> None:
    clock = Clock()
    calls: list[tuple[str, float]] = []

    def transport(url: str, timeout: float) -> bytes:
        calls.append((url, clock.now))
        return response()

    left = RemoteClient(transport=transport, clock=clock, sleep=clock.sleep, cache_entries=2, ttl_seconds=2)
    right = RemoteClient(transport=transport, clock=clock, sleep=clock.sleep, cache_entries=2, ttl_seconds=2)
    left.search("literature", "recid:1")
    right.search("literature", "recid:2")
    assert [time for _, time in calls] == [0.0, REQUEST_INTERVAL_SECONDS]
    assert clock.sleeps == [REQUEST_INTERVAL_SECONDS]
    # Cache reads do not consume the global upstream request budget.
    left.search("literature", "recid:1")
    assert len(calls) == 2
    clock.now += 2.1
    left.search("literature", "recid:1")
    assert len(calls) == 3
    # The same bounded LRU policy applies regardless of collection.
    left.search("literature", "recid:3")
    left.search("literature", "recid:4")
    assert left.cache_info()["entries"] == 2


def test_deadline_and_inflight_bounds_prevent_unbounded_waiting() -> None:
    clock = Clock()
    called = 0

    def transport(url: str, timeout: float) -> bytes:
        nonlocal called
        called += 1
        return response()

    client = RemoteClient(transport=transport, clock=clock, sleep=clock.sleep)
    client.search("literature", "recid:1")
    with pytest.raises(RemoteError) as pacing_error:
        client.search("literature", "recid:2", deadline=0.5)
    assert pacing_error.value.code == "resource_limit" and called == 1
    acquired = [client._inflight.acquire(blocking=False) for _ in range(8)]
    try:
        assert all(acquired)
        with pytest.raises(RemoteError) as queue_error:
            client.search("literature", "recid:3")
        assert queue_error.value.code == "resource_limit"
    finally:
        for _ in acquired:
            client._inflight.release()


def test_429_establishes_shared_cooldown_and_honors_deadlines() -> None:
    clock = Clock()
    attempts: list[str] = []

    def transport(url: str, timeout: float) -> bytes:
        attempts.append(url)
        if len(attempts) == 1:
            raise HTTPError(url, 429, "slow down", hdrs={"Retry-After": "7"}, fp=None)
        return response()

    first = RemoteClient(transport=transport, clock=clock, sleep=clock.sleep)
    second = RemoteClient(transport=transport, clock=clock, sleep=clock.sleep)
    with pytest.raises(RemoteError) as limited:
        first.search("literature", "recid:1")
    assert limited.value.code == "resource_limit" and "7 seconds" in limited.value.message
    with pytest.raises(RemoteError) as deadline:
        second.search("literature", "recid:2", deadline=6.0)
    assert deadline.value.code == "resource_limit" and "cooldown" in deadline.value.message
    assert len(attempts) == 1
    result = second.search("literature", "recid:2", deadline=9.0)
    assert result["hits"]["total"] == 1
    assert len(attempts) == 2 and clock.sleeps == [7.0]


def test_429_preserves_a_long_numeric_retry_after_without_a_premature_request() -> None:
    clock = Clock()
    attempts: list[str] = []

    def transport(url: str, timeout: float) -> bytes:
        attempts.append(url)
        if len(attempts) == 1:
            raise HTTPError(url, 429, "slow down", hdrs={"Retry-After": "600"}, fp=None)
        return response()

    client = RemoteClient(transport=transport, clock=clock, sleep=clock.sleep)
    with pytest.raises(RemoteError) as limited:
        client.search("literature", "recid:1")
    assert limited.value.code == "resource_limit" and "600 seconds" in limited.value.message
    with pytest.raises(RemoteError) as deadline:
        client.search("literature", "recid:2", deadline=20.0)
    assert deadline.value.code == "resource_limit" and "cooldown" in deadline.value.message
    assert len(attempts) == 1 and clock.sleeps == []
    clock.now = 600.0
    assert client.search("literature", "recid:2", deadline=608.0)["hits"]["total"] == 1
    assert len(attempts) == 2


def test_429_honors_an_http_date_retry_after_without_a_premature_request(monkeypatch: pytest.MonkeyPatch) -> None:
    clock = Clock()
    attempts: list[str] = []
    monkeypatch.setattr("hepgraph.remote.time.time", lambda: 1_000.0)
    retry_after = format_datetime(datetime.fromtimestamp(1_600, tz=timezone.utc), usegmt=True)

    def transport(url: str, timeout: float) -> bytes:
        attempts.append(url)
        raise HTTPError(url, 429, "slow down", hdrs={"Retry-After": retry_after}, fp=None)

    client = RemoteClient(transport=transport, clock=clock, sleep=clock.sleep)
    with pytest.raises(RemoteError) as limited:
        client.search("authors", "recid:1")
    assert limited.value.code == "resource_limit" and "600 seconds" in limited.value.message
    with pytest.raises(RemoteError) as deadline:
        client.search("authors", "recid:2", deadline=20.0)
    assert deadline.value.code == "resource_limit" and "cooldown" in deadline.value.message
    assert len(attempts) == 1 and clock.sleeps == []


def test_429_malformed_retry_after_uses_the_five_second_minimum() -> None:
    clock = Clock()
    attempts = 0

    def transport(url: str, timeout: float) -> bytes:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise HTTPError(url, 429, "slow down", hdrs={"Retry-After": "not-a-delay"}, fp=None)
        return response()

    client = RemoteClient(transport=transport, clock=clock, sleep=clock.sleep)
    with pytest.raises(RemoteError) as limited:
        client.search("literature", "recid:1")
    assert limited.value.code == "resource_limit" and "5 seconds" in limited.value.message
    with pytest.raises(RemoteError) as deadline:
        client.search("literature", "recid:2", deadline=4.0)
    assert deadline.value.code == "resource_limit" and attempts == 1
    assert client.search("literature", "recid:2", deadline=6.0)["hits"]["total"] == 1
    assert attempts == 2 and clock.sleeps == [5.0]


def test_remote_strips_unexpected_private_fields_before_return_and_cache() -> None:
    clock = Clock()
    raw = {
        "hits": {"total": {"value": 1}, "hits": [{
            "id": "9", "created": "2020-01-01T00:00:00Z", "updated": "2020-01-02T00:00:00Z",
            "metadata": {
                "control_number": 9, "titles": [{"title": "Safe title"}], "document_type": ["article"],
                "authors": [{"full_name": "Researcher, A", "record": {"$ref": "https://inspirehep.net/api/authors/1"},
                             "affiliations": [{"value": "Institute"}], "emails": ["private@example.test"], "phone": "555"}],
                "author_count": 1, "abstracts": [{"value": "private abstract"}], "keywords": [{"value": "private keyword"}],
                "documents": [{"url": "https://private.example"}], "private_notes": ["private note"], "emails": ["also-private@example.test"],
            },
        }]}}
    calls = 0
    def transport(url: str, timeout: float) -> bytes:
        nonlocal calls
        calls += 1
        return json.dumps(raw).encode()
    client = RemoteClient(transport=transport, clock=clock, sleep=clock.sleep)
    returned = client.search("literature", "recid:9")
    returned_text = json.dumps(returned)
    for forbidden in ("private@example", "555", "abstract", "keyword", "documents", "private_notes", "emails"):
        assert forbidden not in returned_text
    assert returned["hits"]["hits"][0]["created"] == "2020-01-01T00:00:00Z"
    assert returned["hits"]["hits"][0]["updated"] == "2020-01-02T00:00:00Z"
    # A cache hit has the same already-sanitised surface, with no second fetch.
    assert client.search("literature", "recid:9") == returned and calls == 1
    assert "private@example" not in json.dumps(next(iter(client._cache.values())).value)


def test_total_relation_is_preserved_and_unknown_relation_is_rejected() -> None:
    clock = Clock()
    client = RemoteClient(
        transport=lambda url, timeout: response(total={"value": 10_000, "relation": "gte"}),
        clock=clock, sleep=clock.sleep,
    )
    assert client.search("authors", "control_number:1")["hits"]["total"] == {
        "value": 10_000, "relation": "gte",
    }
    malformed = RemoteClient(
        transport=lambda url, timeout: response(total={"value": 1, "relation": "approximately"}),
        clock=Clock(), sleep=lambda _: None,
    )
    with pytest.raises(RemoteError, match="total relation"):
        malformed.search("authors", "control_number:1")


def test_cache_reports_bounded_usage_for_each_request_layer() -> None:
    clock = Clock()

    def transport(url: str, timeout: float) -> bytes:
        if "/facets?" in url:
            return json.dumps({
                "hits": {"total": 0},
                "aggregations": {"author": {"buckets": [], "sum_other_doc_count": 0,
                                                "doc_count_error_upper_bound": 0}},
            }).encode()
        return json.dumps({"hits": {"total": 0, "hits": []}}).encode()

    client = RemoteClient(transport=transport, clock=clock, sleep=clock.sleep)
    client.search("authors", "control_number:1")
    client.search("literature", "authors.record.$ref:1")
    client.search("literature", "authors.record.$ref:1 AND authors.record.$ref:2")
    client.coauthors("authors.record.$ref:1")
    info = client.cache_info()
    # An empty exact-author response is deliberately not a negative cache
    # entry. The three reusable literature/facet responses remain bounded.
    assert info["entries"] == 3 and info["bytes"] <= info["limit"]
    assert {layer: row["upstream_requests"] for layer, row in info["layers"].items()} == {
        "authors": 1, "literature": 1, "facets": 1, "shared_papers": 1,
    }


@pytest.mark.parametrize("collection,query,size,page,sort", [
    ("unknown", "recid:1", 25, 1, None),
    ("authors", "", 25, 1, None),
    ("authors", "x" * 4097, 25, 1, None),
    ("authors", "one\ntwo", 25, 1, None),
    ("authors", "recid:1", 0, 1, None),
    ("authors", "recid:1", 101, 1, None),
    ("authors", "recid:1", 25, 0, None),
    ("authors", "recid:1", 25, 10_001, None),
    ("authors", "recid:1", 100, 101, None),
    ("authors", "recid:1", 25, 1, "bad\x00sort"),
])
def test_invalid_input_never_reaches_transport(collection, query, size, page, sort) -> None:
    client = RemoteClient(transport=lambda *_: pytest.fail("transport must not run"), clock=Clock(), sleep=lambda _: None)
    with pytest.raises(RemoteError) as error:
        client.search(collection, query, size=size, page=page, sort=sort)
    assert error.value.code == "resource_limit"


@pytest.mark.parametrize("body,code", [
    (b"not json", "upstream_unavailable"),
    (json.dumps({"hits": []}).encode(), "upstream_unavailable"),
    (json.dumps({"hits": {"total": True, "hits": []}}).encode(), "upstream_unavailable"),
    (response(metadata=[]), "upstream_unavailable"),
    (b"x" * (MAX_RESPONSE_BYTES + 1), "resource_limit"),
])
def test_malformed_or_oversize_upstream_responses_are_explicit(body: bytes, code: str) -> None:
    client = RemoteClient(transport=lambda *_: body, clock=Clock(), sleep=lambda _: None)
    with pytest.raises(RemoteError) as error:
        client.search("literature", "recid:1")
    assert error.value.code == code


@pytest.mark.parametrize("number", ["NaN", "Infinity", "-Infinity", "1e10000"])
def test_non_finite_json_numbers_are_rejected_before_normalization(number: str) -> None:
    body = (b'{"hits":{"total":1,"hits":[{"id":"1","metadata":{"control_number":1}}],"untrusted":'
            + number.encode() + b"}}")
    client = RemoteClient(transport=lambda *_: body, clock=Clock(), sleep=lambda _: None)
    with pytest.raises(RemoteError) as error:
        client.search("literature", "recid:1")
    assert error.value.code == "upstream_unavailable"


def test_excessively_nested_or_oversize_hit_page_is_rejected_before_cache() -> None:
    nested: object = "leaf"
    for _ in range(65):
        nested = {"next": nested}
    recursive_body = json.dumps({"hits": {"total": 1, "hits": [{"id": "1", "metadata": {"control_number": 1, "untrusted": nested}}]}}).encode()
    recursive_client = RemoteClient(transport=lambda *_: recursive_body, clock=Clock(), sleep=lambda _: None)
    with pytest.raises(RemoteError) as recursion_error:
        recursive_client.search("literature", "recid:1")
    assert recursion_error.value.code == "upstream_unavailable"

    hit = {"id": "1", "metadata": {"control_number": 1}}
    overfull_body = json.dumps({"hits": {"total": 2, "hits": [hit, hit]}}).encode()
    overfull_client = RemoteClient(transport=lambda *_: overfull_body, clock=Clock(), sleep=lambda _: None)
    with pytest.raises(RemoteError) as overfull_error:
        overfull_client.search("literature", "recid:1", size=1)
    assert overfull_error.value.code == "upstream_unavailable"
    assert overfull_client.cache_info()["entries"] == 0


def test_transport_http_failures_and_literature_field_allowlist() -> None:
    clock = Clock()

    def rate_limited(url: str, timeout: float) -> bytes:
        raise HTTPError(url, 429, "slow down", hdrs=None, fp=None)

    client = RemoteClient(transport=rate_limited, clock=clock, sleep=clock.sleep)
    with pytest.raises(RemoteError) as error:
        client.search("literature", "recid:1")
    assert error.value.code == "resource_limit"

    urls: list[str] = []
    client = RemoteClient(transport=lambda url, timeout: urls.append(url) or response(total={"value": 1}), clock=Clock(), sleep=lambda _: None)
    assert client.search("literature", "recid:1")["hits"]["total"] == {"value": 1}
    assert parse_qs(urlparse(urls[0]).query)["fields"] == [LITERATURE_FIELDS]


def test_non_finite_time_configuration_and_deadlines_are_rejected() -> None:
    for ttl in (math.inf, -math.inf, math.nan):
        with pytest.raises(ValueError):
            RemoteClient(ttl_seconds=ttl)
    client = RemoteClient(transport=lambda *_: pytest.fail("transport must not run"), clock=Clock(), sleep=lambda _: None)
    for deadline in (math.inf, -math.inf, math.nan):
        with pytest.raises(RemoteError) as error:
            client.search("authors", "recid:1", deadline=deadline)
        assert error.value.code == "resource_limit"


def test_pacing_stays_below_the_documented_inspire_ceiling() -> None:
    """INSPIRE publishes 15 requests per 5 s; never pace at or above that."""
    assert REQUEST_INTERVAL_SECONDS > MIN_REQUEST_INTERVAL_SECONDS
    window = 5.0 / REQUEST_INTERVAL_SECONDS
    assert window <= 12, "a 5 s window must stay comfortably under 15 requests"


def test_request_interval_can_be_slowed_but_never_sped_past_the_ceiling() -> None:
    clock = Clock()
    calls: list[float] = []

    def transport(url: str, timeout: float) -> bytes:
        calls.append(clock.now)
        return response()

    slow = RemoteClient(transport=transport, clock=clock, sleep=clock.sleep, request_interval=3.0)
    slow.search("literature", "recid:1")
    slow.search("literature", "recid:2")
    assert calls == [0.0, 3.0]

    faster = Clock()
    calls.clear()
    reckless = RemoteClient(transport=lambda url, timeout: (calls.append(faster.now), response())[1],
                            clock=faster, sleep=faster.sleep, request_interval=0.0)
    reckless.search("literature", "recid:1")
    reckless.search("literature", "recid:2")
    assert calls == [0.0, MIN_REQUEST_INTERVAL_SECONDS]
