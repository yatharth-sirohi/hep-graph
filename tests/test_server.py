"""HTTP and service-boundary tests for the graph-database service.

No test here contacts INSPIRE or a database: the graph service is stubbed, so
what is exercised is the request surface itself - parameter validation, the
static allowlist, method handling, and that an unconfigured deployment says so
instead of pretending to answer.
"""

from __future__ import annotations

import json
import socket
import threading

import pytest

from hepgraph import server as server_module
from hepgraph.graph import Filters


class StubDatabase:
    """Stands in for DatabaseGraphService with no database behind it."""

    def __init__(self):
        self.calls = []

    class _Coverage:
        import_id = "stub-import"

    def coverage(self, **kwargs):
        return self._Coverage()

    def provider(self, *args, **kwargs):
        return self

    def resolve_author(self, author_id):
        return {"id": str(author_id)}

    def dataset(self):
        return {"version": "graph-db:stub-import", "source_mode": "database",
                "created_at": None, "graph_snapshot": "stub-import",
                "counts": {"people": None, "works": 3, "phd": None},
                "coverage": {"label": "stub", "description": "stub", "complete": False,
                             "mode": "database", "queries": [], "failures": []},
                "capabilities": {"live_graph": False, "deep_search": True,
                                 "global_centrality": False},
                "policy": {}}

    def start_path(self, source, target, filters):
        self.calls.append(("start_path", source, target, filters.to_dict()))
        return {"job_id": "a" * 32, "status": "settled", "proof_status": "verified",
                "route_status": "verified_route_found", "paths": []}

    def person(self, person_id, filters, **kwargs):
        self.calls.append(("person", person_id))
        return {"status": "ok", "person": {"id": person_id}}

    def neighborhood(self, person_id, filters, **kwargs):
        self.calls.append(("neighborhood", person_id))
        return {"status": "ok", "people": [], "edges": []}

    def ancestry(self, person_id, filters):
        return {"status": "unavailable", "message": "no overlay"}

    def owns_job(self, job_id):
        return job_id == "a" * 32

    def job(self, job_id):
        return {"job_id": job_id, "status": "settled"}

    def resume(self, job_id):
        return {"job_id": job_id, "status": "searching", "resumed": True}

    def cancel(self, job_id):
        return {"job_id": job_id, "status": "cancelled"}


@pytest.fixture
def service(monkeypatch: pytest.MonkeyPatch):
    stub = StubDatabase()

    class LocalServer:
        def __init__(self):
            self.state = server_module.State()

        def request(self, path, *, method="GET", body=None, database=stub):
            monkeypatch.setattr(self.state, "graph_database", lambda: database)
            left, right = socket.socketpair()
            left.settimeout(5)
            try:
                headers = [f"{method} {path} HTTP/1.1", "Host: localhost", "Connection: close"]
                if body is not None:
                    headers.append(f"Content-Length: {len(body)}")
                payload = ("\r\n".join(headers) + "\r\n\r\n").encode() + (body or b"")
                left.sendall(payload)
                left.shutdown(socket.SHUT_WR)

                def serve_one():
                    try:
                        server_module.Handler(right, ("127.0.0.1", 12345), self)
                    finally:
                        right.close()

                thread = threading.Thread(target=serve_one, daemon=True)
                thread.start()
                chunks = []
                try:
                    while True:
                        chunk = left.recv(65536)
                        if not chunk:
                            break
                        chunks.append(chunk)
                except TimeoutError:
                    pass
                thread.join(timeout=2)
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
    yield local, local.state, stub


def _json(body: bytes) -> dict:
    return json.loads(body.decode("utf-8"))


# ------------------------------------------------------------------ surface

def test_health_and_dataset_describe_the_pinned_graph(service):
    base, _, _ = service
    status, headers, body = base.request("/api/health")
    assert status == 200
    payload = _json(body)
    assert payload["status"] == "ok"
    assert payload["runtime"]["instance"]
    assert headers.get("X-Content-Type-Options") == "nosniff"

    status, _, body = base.request("/api/dataset")
    payload = _json(body)
    assert status == 200
    assert payload["source_mode"] == "database"
    assert payload["version"] == "graph-db:stub-import"
    assert payload["capabilities"]["live_graph"] is False
    assert "examples" not in payload


def test_an_unconfigured_deployment_refuses_instead_of_pretending(service):
    """No database means no routes; saying so is the only honest answer."""
    base, _, _ = service
    status, _, body = base.request("/api/path?source=101&target=102", database=None)
    assert status == 503
    payload = _json(body)
    assert payload["status"] == "unavailable"
    assert "no published research data" in payload["message"]


def test_route_search_reaches_the_database_with_parsed_filters(service):
    base, _, stub = service
    status, _, body = base.request("/api/path?source=101&target=102&max_authors=all&min_shared=2")
    assert status == 200
    assert _json(body)["route_status"] == "verified_route_found"
    call = [item for item in stub.calls if item[0] == "start_path"][0]
    assert call[1:3] == ("101", "102")
    assert call[3]["max_authors"] is None and call[3]["min_shared"] == 2


def test_person_and_neighborhood_are_served_from_the_database(service):
    base, _, stub = service
    assert base.request("/api/person/101")[0] == 200
    assert base.request("/api/neighborhood/101?limit=10")[0] == 200
    assert base.request("/api/ancestry/101")[0] == 200
    assert ("person", "101") in stub.calls


def test_centrality_reports_unavailable_rather_than_sampling(service):
    base, _, _ = service
    status, _, body = base.request("/api/centrality")
    payload = _json(body)
    assert status == 200
    assert payload["status"] == "unavailable"
    assert payload["exact"] is False


def test_search_jobs_are_polled_continued_and_cancelled(service):
    base, _, _ = service
    job = "a" * 32
    assert _json(base.request(f"/api/search-jobs/{job}")[1 + 1])["status"] == "settled"
    assert _json(base.request(f"/api/search-jobs/{job}/continue", method="POST")[2])["resumed"] is True
    assert _json(base.request(f"/api/search-jobs/{job}/cancel", method="POST")[2])["status"] == "cancelled"
    # A control action must not be reachable by GET.
    assert base.request(f"/api/search-jobs/{job}/continue")[0] == 405
    assert base.request(f"/api/search-jobs/{'b' * 32}")[0] == 404


# ------------------------------------------------------------------ hardening

@pytest.mark.parametrize("path", [
    "/api/path?source=1&source=2&target=3",
    "/api/path?source=1&target=3&unknown=1",
    "/api/path?source=1&target=3&max_authors=0",
    "/api/path?source=0&target=2",
    "/api/path?mode=live&source=1&target=2",
    "/api/person/not-an-inspire-id",
    "/api/search?q=x",
    "/api/neighborhood/101?limit=999",
    "/api/ancestry/101?direction=sideways",
])
def test_malformed_duplicate_unknown_and_invalid_parameters_are_400(service, path):
    base, _, _ = service
    status, _, body = base.request(path)
    assert status == 400
    assert _json(body)["status"] == "invalid_input"


def test_the_removed_live_mode_is_rejected_not_silently_ignored(service):
    base, _, _ = service
    status, _, body = base.request("/api/path?mode=live&source=101&target=102")
    assert status == 400
    assert "search source is unavailable" in _json(body)["message"]


def test_excessive_parameters_and_url_length_are_rejected(service):
    base, _, _ = service
    many = "&".join(f"p{index}=1" for index in range(40))
    assert base.request(f"/api/dataset?{many}")[0] == 400
    # Over the 4096 limit, but small enough that the socketpair buffer
    # still accepts it after the handler has closed its side.
    assert base.request("/api/path?source=1&target=" + "9" * 4200)[0] == 414


def test_static_routes_are_allowlisted_and_traversal_cannot_expose_files(service):
    base, _, _ = service
    assert base.request("/")[0] == 200
    assert base.request("/app.js")[0] == 200
    for path in ("/../hepgraph/server.py", "/static/../pyproject.toml", "/%2e%2e/pyproject.toml",
                 "/data/current.json", "/.env.local"):
        status, _, body = base.request(path)
        assert status == 404, path
        assert b"DATABASE_URL" not in body


def test_head_has_no_body_and_post_is_limited_to_search_controls(service):
    base, _, _ = service
    status, headers, body = base.request("/api/health", method="HEAD")
    assert status == 200 and body == b""
    assert base.request("/api/dataset", method="POST", body=b"")[0] == 501
