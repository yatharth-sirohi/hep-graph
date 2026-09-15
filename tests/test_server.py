"""HTTP and service-boundary tests for the read-only HEP Graph service.

The fixture is deliberately small and local.  No test in this module contacts
INSPIRE; live-search tests replace the opener with a deterministic fake.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import threading
import time

import pytest

from hepgraph import server as server_module
from hepgraph import remote as remote_module
from hepgraph.graph import Filters, Graph


def _person(person_id: str, name: str | None = None) -> dict:
    return {
        "id": person_id,
        "name": name or f"Person {person_id}",
        "aliases": [],
        "affiliations": [],
        "orcid": None,
        "profile_status": "profile",
        "source_url": f"https://inspirehep.net/authors/{person_id}",
    }


def _work(work_id: str, authors: list[str], year: int) -> dict:
    return {
        "id": work_id,
        "title": f"Work {work_id}",
        "year": year,
        "date": f"{year}-01-01",
        "date_source": "preprint",
        "author_count": len(authors),
        "authors": authors,
        "unresolved_count": 0,
        "document_types": ["article"],
        "doi": [],
        "arxiv": [],
        "source_url": f"https://inspirehep.net/literature/{work_id}",
        "source_ids": [],
        "retrieved_at": "2026-09-14T00:00:00Z",
    }


def _snapshot(version: str = "fixture-v1") -> dict:
    return {
        "version": version,
        "created_at": "2026-09-14T00:00:00Z",
        "coverage": {"label": "local fixture", "description": "test data", "complete": False, "queries": [], "failures": []},
        "people": [_person(item) for item in ("1", "2", "3", "4")],
        "works": [_work("w1", ["1", "2"], 2010), _work("w2", ["2", "3"], 2020), _work("w3", ["3", "4"], 2021)],
        "phd": [{
            "adviser": "1", "student": "4", "degree": "PhD", "year": 2000,
            "source_url": "https://inspirehep.net/literature/doctoral",
            "source_record": "p1", "uncertainty": None,
            "retrieved_at": "2026-09-14T00:00:00Z",
        }],
        "examples": [],
    }


@pytest.fixture
def snapshot_path(tmp_path: Path) -> Path:
    path = tmp_path / "current.json"
    path.write_text(json.dumps(_snapshot()), encoding="utf-8")
    return path


@pytest.fixture
def service(snapshot_path: Path):
    # The managed test sandbox does not allow binding TCP ports. A socketpair
    # still runs the production BaseHTTPRequestHandler request/response code,
    # including HTTP parsing, without a listening socket or live network.
    class LocalServer:
        def __init__(self):
            self.state = server_module.State(snapshot_path)

        def request(self, path: str, *, method: str = "GET", body: bytes | None = None):
            left, right = socket.socketpair()
            try:
                body = body or b""
                headers = [f"{method} {path} HTTP/1.0", "Host: localhost", "Connection: close"]
                if body:
                    headers.append(f"Content-Length: {len(body)}")
                left.sendall(("\r\n".join(headers) + "\r\n\r\n").encode() + body)
                left.shutdown(socket.SHUT_WR)
                # Invoke the handler concurrently so a static response larger
                # than the socket buffer cannot deadlock while the peer reads.
                def serve_one():
                    try:
                        server_module.Handler(right, ("127.0.0.1", 12345), self)
                    finally:
                        right.close()

                handler_thread = threading.Thread(target=serve_one, daemon=True)
                handler_thread.start()
                chunks = []
                while True:
                    chunk = left.recv(65536)
                    if not chunk:
                        break
                    chunks.append(chunk)
                handler_thread.join(timeout=2)
                raw = b"".join(chunks)
            finally:
                left.close()
                right.close()
            head, _, response_body = raw.partition(b"\r\n\r\n")
            lines = head.decode("iso-8859-1").split("\r\n")
            status = int(lines[0].split()[1])
            response_headers = {}
            for line in lines[1:]:
                key, _, value = line.partition(":")
                response_headers[key] = value.strip()
            return status, response_headers, response_body

    local = LocalServer()
    yield local, local.state


def _request(base, path: str, *, method: str = "GET", body: bytes | None = None) -> tuple[int, dict[str, str], bytes]:
    return base.request(path, method=method, body=body)


def _json(body: bytes) -> dict:
    return json.loads(body.decode("utf-8"))


def test_handler_state_is_created_once_when_runtime_owns_server(monkeypatch: pytest.MonkeyPatch) -> None:
    created = []
    sentinel = object()

    def make_state(path, default_mode):
        created.append((path, default_mode))
        return sentinel

    monkeypatch.setattr(server_module, "State", make_state)
    monkeypatch.setattr(server_module, "_SERVERLESS_STATE", None)
    first_server = type("RuntimeServer", (), {})()
    second_server = type("RuntimeServer", (), {})()

    assert server_module._state_for_handler(first_server) is sentinel
    assert server_module._state_for_handler(first_server) is sentinel
    assert server_module._state_for_handler(second_server) is sentinel
    assert first_server.state is sentinel
    assert second_server.state is sentinel
    assert created == [(server_module.ROOT / "data" / "current.json", "live")]


def test_health_dataset_headers_and_exact_snapshot_version(service) -> None:
    base, state = service
    status, headers, body = _request(base, "/api/health")
    assert status == 200
    assert _json(body) == {"status": "ok", "version": "fixture-v1", "service_version": "general-search-v3"}
    assert headers["Content-Type"].startswith("application/json")
    assert headers["Cache-Control"] == "no-store"
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["Content-Security-Policy"].startswith("default-src 'self'")

    status, _, body = _request(base, "/api/path?source=1&target=3&version=fixture-v1")
    assert status == 200
    result = _json(body)
    assert result["version"] == "fixture-v1"
    assert "version_mismatch" not in result

    status, _, body = _request(base, "/api/path?source=1&target=3&version=stale-v0")
    assert status == 200
    result = _json(body)
    assert result["version"] == "fixture-v1"
    assert result["version_mismatch"] is True
    assert result["requested_version"] == "stale-v0"
    assert "current version" in result["version_warning"]

    # State.reload is driven by the published file stamp, so a newly published
    # snapshot becomes the exact version used by subsequent graph responses.
    state.path.write_text(json.dumps(_snapshot("fixture-v2")), encoding="utf-8")
    os.utime(state.path, ns=(time.time_ns(), time.time_ns() + 1_000_000))
    status, _, body = _request(base, "/api/health")
    assert status == 200
    assert _json(body)["version"] == "fixture-v2"


def test_filters_change_graph_and_identity_states_are_explicit(service) -> None:
    base, _ = service
    status, _, body = _request(base, "/api/path?source=1&target=3&genealogy=false")
    assert status == 200
    assert _json(body)["status"] == "ok"

    # Only the 2020 paper remains; that leaves person 1 disconnected from 3.
    status, _, body = _request(base, "/api/path?source=1&target=3&year_start=2020&year_end=2020&genealogy=false")
    assert status == 200
    filtered = _json(body)
    assert filtered["status"] == "no_path"
    assert filtered["paths"] == []
    assert filtered["filters"]["year_start"] == 2020

    status, _, body = _request(base, "/api/path?source=2&target=2")
    assert status == 200
    same = _json(body)
    assert same["status"] == "ok"
    assert same["paths"][0]["hops"] == 0
    assert same["paths"][0]["edges"] == []

    status, _, body = _request(base, "/api/path?source=1&target=999")
    assert status == 200
    assert _json(body)["status"] == "not_indexed"

    # Profile/neighborhood use GraphError for the same identity state.  It must
    # retain its typed status instead of being swallowed as generic bad input.
    status, _, body = _request(base, "/api/person/999")
    assert status in {404, 422}
    assert _json(body)["status"] == "not_indexed"

    status, _, body = _request(base, "/api/path?source=1&target=4&year_start=2020&year_end=2020&genealogy=false")
    assert status == 200
    assert _json(body)["status"] == "no_path"


@pytest.mark.parametrize(
    "path",
    [
        "/api/path?source=1&source=2&target=3",
        "/api/path?source=1&target=3&unknown=1",
        "/api/path?source=1&target=3&max_authors=0",
        "/api/search?q=x",
        "/api/search?q=Alice&live=2",
        "/api/person/not-an-inspire-id",
    ],
)
def test_malformed_duplicate_unknown_and_invalid_parameters_are_400(service, path: str) -> None:
    status, _, body = _request(service[0], path)
    assert status == 400
    assert _json(body)["status"] == "invalid_input"


def test_excessive_parameters_and_url_length_are_rejected(service) -> None:
    base, _ = service
    fields = "&".join(f"x{index}=1" for index in range(21))
    status, _, body = _request(base, "/api/health?" + fields)
    assert status == 400
    assert _json(body)["status"] == "invalid_input"

    status, _, body = _request(base, "/api/health?x=" + ("a" * 4100))
    assert status == 414
    assert _json(body)["status"] == "invalid_input"


def test_static_routes_are_allowlisted_and_traversal_cannot_expose_files(service) -> None:
    base, _ = service
    status, headers, body = _request(base, "/")
    assert status == 200
    assert headers["Content-Type"].startswith("text/html")
    assert b"HEP Graph" in body

    for path in ("/data/current.json", "/%2e%2e/%2e%2e/CONTRACT.md", "/api/../CONTRACT.md", "/static/app.js"):
        status, _, body = _request(base, path)
        assert status == 404
        assert b"HEP implementation contract" not in body


def test_get_only_surface_has_head_without_body_and_rejects_post(service) -> None:
    base, _ = service
    status, headers, body = _request(base, "/api/health", method="HEAD")
    assert status == 200
    assert headers["Content-Length"].isdigit()
    assert body == b""

    status, _, body = _request(base, "/api/health", method="POST", body=b"status=bad")
    assert status == 501
    assert b"Unsupported method" in body


def test_resource_limit_is_not_returned_as_success_or_no_path(service, monkeypatch: pytest.MonkeyPatch) -> None:
    base, _ = service
    monkeypatch.setattr(Graph, "MAX_PATH_NODES", 0)
    status, _, body = _request(base, "/api/path?source=1&target=3")
    result = _json(body)
    assert status in {422, 503}
    assert result["status"] == "resource_limit"
    assert result["status"] != "no_path"


class _FakeResponse:
    def __init__(self, payload: bytes):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit: int = -1) -> bytes:
        return self.payload if limit < 0 else self.payload[:limit]


class _FakeOpener:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.requests = []

    def open(self, request, timeout):
        self.requests.append((request, timeout))
        if self.error:
            raise self.error
        return self.response


def _live_payload(name: str = "<script>alert(1)</script>") -> bytes:
    return json.dumps({"hits": {"total": 1, "hits": [{
        "id": "77",
        "metadata": {
            "control_number": 77,
            "name": {"preferred_name": name, "name_variants": []},
            "ids": [],
            "positions": [],
            "untrusted_field": "must not be copied",
        },
    }]}}).encode()


def test_live_search_constructs_only_fixed_upstream_urls_and_bounds_query(monkeypatch, snapshot_path: Path) -> None:
    opener = _FakeOpener(_FakeResponse(_live_payload()))
    monkeypatch.setattr(remote_module, "build_opener", lambda _: opener)
    state = server_module.State(snapshot_path)
    result = state.live_search("x/y? OR attacker")
    assert result["status"] == "ok"
    assert result["results"][0]["id"] == "77"
    assert result["results"][0]["name"] == "<script>alert(1)</script>"
    assert "untrusted_field" not in result["results"][0]
    request, timeout = opener.requests[0]
    parsed = server_module.urllib.parse.urlsplit(request.full_url)
    assert parsed.scheme == "https"
    assert parsed.netloc == "inspirehep.net"
    assert parsed.path == "/api/authors"
    assert "attacker" in server_module.urllib.parse.parse_qs(parsed.query)["q"][0]
    assert 0 < timeout <= 8


def test_live_upstream_failure_is_explicit_and_cached_results_are_isolated(monkeypatch, snapshot_path: Path) -> None:
    failing = _FakeOpener(error=remote_module.URLError("offline"))
    monkeypatch.setattr(remote_module, "build_opener", lambda _: failing)
    state = server_module.State(snapshot_path)
    unavailable = state.live_search("Offline researcher")
    assert unavailable["status"] == "upstream_unavailable"
    assert unavailable["results"] == []

    opener = _FakeOpener(_FakeResponse(_live_payload("Cached name")))
    monkeypatch.setattr(remote_module, "build_opener", lambda _: opener)
    state = server_module.State(snapshot_path)
    first = state.live_search("Cached researcher")
    first["results"][0]["name"] = "mutated by caller"
    second = state.live_search("Cached researcher")
    assert second["results"][0]["name"] == "Cached name"
    assert len(opener.requests) == 1
