"""Bounded selected-author preparation and HTTP boundary regressions."""
from __future__ import annotations

import json
import re
import threading
import time

import pytest

from hepgraph.graph import Filters
from hepgraph.prefetch import PreparationError, PreparationJobs
from test_acceptance_service import _LocalService, _snapshot


def eventually(predicate, timeout: float = 2.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(.002)
    raise AssertionError("Preparation did not reach the expected state.")


class RecordingClient:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def search(self, collection, query, *, size=25, page=1, sort=None, deadline=None):
        self.calls.append(("search", collection, query, size, page, sort))
        if collection == "authors":
            match = re.fullmatch(r"control_number:([1-9][0-9]*)", query)
            if match:
                person = match.group(1)
                return {"hits": {"total": 1, "hits": [{
                    "id": person,
                    "metadata": {"control_number": person, "deleted": False},
                }]}}
        return {"hits": {"total": 0, "hits": []}}

    def coauthors(self, query, *, deadline=None):
        self.calls.append(("facets", query))
        return {"authors": [], "truncated": False, "total": 0}

    def cache_info(self):
        return {"bytes": 0, "limit": 8 * 1024 * 1024, "entries": 0,
                "ttl_seconds": 900.0, "storage": "memory", "persistent": False}


def test_prepare_warms_exact_deep_keys_once_and_reuses_ready_status() -> None:
    client = RecordingClient()
    jobs = PreparationJobs(client)
    filters = Filters(max_authors=None, genealogy=False, min_authors=11)
    try:
        first = jobs.start("42", filters)
        ready = eventually(lambda: value if (value := jobs.get(first["preparation_id"]))["status"] == "ready" else None)
        second = jobs.start("42", filters)
    finally:
        jobs.shutdown()

    query = "authors.record.$ref:42 AND author_count:11+"
    # No facet warm-up: with discovery hints off the search never calls it.
    assert client.calls == [
        ("search", "authors", "control_number:42", 25, 1, "mostrecent"),
        ("search", "literature", query, 5, 1, "mostrecent"),
    ]
    assert ready["warmed"] == ["identity", "literature"]
    assert second["preparation_id"] == first["preparation_id"] and second["reused"] is True
    assert jobs.info()["counters"] == {"ready": 1, "reused": 1, "started": 1}


class BlockingClient(RecordingClient):
    def __init__(self) -> None:
        super().__init__()
        self.entered = threading.Semaphore(0)
        self.release = threading.Event()

    def search(self, collection, query, **kwargs):
        self.calls.append(("search", collection, query))
        if collection == "authors":
            self.entered.release()
            assert self.release.wait(2)
            person = query.removeprefix("control_number:")
            return {"hits": {"total": 1, "hits": [{
                "id": person,
                "metadata": {"control_number": person, "deleted": False},
            }]}}
        return {"hits": {"total": 0, "hits": []}}


@pytest.mark.parametrize("author_hits", [
    [],
    [{"id": "41", "metadata": {"control_number": "41", "deleted": False}}],
    [{"id": "42", "metadata": {"control_number": "42", "deleted": True}}],
])
def test_prepare_requires_exact_current_identity_and_skips_downstream(author_hits) -> None:
    class MissingIdentityClient(RecordingClient):
        def search(self, collection, query, **kwargs):
            self.calls.append(("search", collection, query))
            return {"hits": {"total": len(author_hits), "hits": author_hits}}

    client = MissingIdentityClient()
    jobs = PreparationJobs(client)
    try:
        started = jobs.start("42", Filters())
        failed = eventually(lambda: value if (value := jobs.get(
            started["preparation_id"]))["status"] == "failed" else None)
    finally:
        jobs.shutdown()

    assert client.calls == [("search", "authors", "control_number:42")]
    assert failed["warmed"] == []
    assert failed["failures"] == [{
        "stage": "identity",
        "code": "not_found",
        "message": "INSPIRE did not return the requested current author profile.",
    }]


def test_prepare_pool_has_two_workers_and_one_explicit_pending_slot() -> None:
    client = BlockingClient()
    jobs = PreparationJobs(client, max_active=2, max_pending=1, max_retained=8)
    try:
        jobs.start("1", Filters())
        jobs.start("2", Filters())
        assert client.entered.acquire(timeout=1) and client.entered.acquire(timeout=1)
        queued = jobs.start("3", Filters())
        assert queued["status"] == "queued"
        assert jobs.info()["active"] == 2 and jobs.info()["pending"] == 1
        with pytest.raises(PreparationError) as full:
            jobs.start("4", Filters())
        assert full.value.http_status == 503
    finally:
        client.release.set()
        jobs.shutdown()


def test_prepare_http_is_post_only_same_origin_bodyless_and_parses_min_authors(tmp_path) -> None:
    path = tmp_path / "current.json"
    path.write_text(json.dumps(_snapshot()))
    service = _LocalService(path)
    client = RecordingClient()
    service.state._remote_client = client
    service.state._preparations = PreparationJobs(client)
    try:
        query = "/api/prepare?mode=live&person=42&min_authors=11&max_authors=all&genealogy=false"
        status, _, body = service.request(query, method="POST", extra_headers={"Origin": "http://localhost"})
        assert status == 202
        started = json.loads(body)
        assert started["person"] == "42"
        assert started["filters"]["min_authors"] == 11
        assert started["filters"]["max_authors"] is None
        terminal = eventually(lambda: value if (value := service.state._preparations.get(
            started["preparation_id"]))["status"] == "ready" else None)
        status, _, body = service.request(
            f"/api/preparations/{started['preparation_id']}?mode=live")
        assert status == 200 and json.loads(body)["status"] == terminal["status"]

        assert service.request(query)[0] == 405
        assert service.request(query, method="POST", extra_headers={"Origin": "https://attacker.invalid"})[0] == 403
        assert service.request(query, method="POST", extra_headers={"Content-Length": "2"}, body=b"{}") [0] == 400
        assert service.request("/api/prepare?mode=live&person=0", method="POST")[0] == 400
        cache_status = json.loads(service.request("/api/cache?mode=live")[2])
        assert cache_status["preparations"]["max_active"] == 2
    finally:
        service.state.shutdown()
