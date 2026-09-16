"""Focused service acceptance regressions for a local professor demo.

These checks use an in-process socketpair and deterministic fake upstream
responses. They do not bind a port or contact INSPIRE.
"""

from __future__ import annotations

import json
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time

import pytest

from hepgraph import server as server_module
from fake_https_connection import json_body, make_connection_class
from hepgraph import remote as remote_module


def _person(person_id: str) -> dict:
    return {"id": person_id, "name": f"Person {person_id}", "aliases": [], "affiliations": [],
            "orcid": None, "profile_status": "profile", "source_url": f"https://inspirehep.net/authors/{person_id}"}


def _work(work_id: str, authors: list[str], year: int) -> dict:
    return {"id": work_id, "title": f"Work {work_id}", "year": year, "date": f"{year}-01-01",
            "date_source": "preprint", "author_count": len(authors), "authors": authors,
            "unresolved_count": 0, "document_types": ["article"], "doi": [], "arxiv": [],
            "source_url": f"https://inspirehep.net/literature/{work_id}", "source_ids": [],
            "retrieved_at": "2026-09-14T00:00:00Z"}


def _snapshot(version: str = "acceptance-v1") -> dict:
    return {"version": version, "created_at": "2026-09-14T00:00:00Z",
            "coverage": {"label": "acceptance fixture", "description": "local", "complete": False, "queries": [], "failures": []},
            "people": [_person(item) for item in ("1", "2", "3")],
            "works": [_work("w1", ["1", "2"], 2019), _work("w2", ["2", "3"], 2020)],
            "phd": [], "examples": []}


@pytest.fixture
def snapshot_path(tmp_path: Path) -> Path:
    path = tmp_path / "current.json"
    path.write_text(json.dumps(_snapshot()), encoding="utf-8")
    return path


class _LocalService:
    def __init__(self, snapshot_path: Path):
        self.state = server_module.State(snapshot_path)

    def request(self, path: str, *, method: str = "GET", extra_headers: dict | None = None, body: bytes = b'') -> tuple[int, dict[str, str], bytes]:
        left, right = socket.socketpair()
        try:
            headers = ''.join(f'{key}: {value}\r\n' for key, value in (extra_headers or {}).items())
            left.sendall(f"{method} {path} HTTP/1.0\r\nHost: localhost\r\nConnection: close\r\n{headers}\r\n".encode() + body)
            left.shutdown(socket.SHUT_WR)

            def serve() -> None:
                try:
                    server_module.Handler(right, ("127.0.0.1", 12345), self)
                finally:
                    right.close()

            worker = threading.Thread(target=serve, daemon=True)
            worker.start()
            chunks = []
            while True:
                chunk = left.recv(65536)
                if not chunk:
                    break
                chunks.append(chunk)
            worker.join(timeout=2)
            raw = b"".join(chunks)
        finally:
            left.close()
            right.close()
        header, _, body = raw.partition(b"\r\n\r\n")
        lines = header.decode("iso-8859-1").split("\r\n")
        status = int(lines[0].split()[1])
        headers = {}
        for line in lines[1:]:
            key, _, value = line.partition(":")
            headers[key] = value.strip()
        return status, headers, body


@pytest.fixture
def service(snapshot_path: Path) -> _LocalService:
    return _LocalService(snapshot_path)


def _json(body: bytes) -> dict:
    return json.loads(body.decode("utf-8"))


def test_source_tree_startup_commands_and_declared_python_floor() -> None:
    assert sys.version_info >= (3, 11)
    metadata = server_module.ROOT / "pyproject.toml"
    assert metadata.exists()
    import tomllib
    project = tomllib.loads(metadata.read_text())["project"]
    assert project["requires-python"] == ">=3.11"
    for module in ("hepgraph.server", "hepgraph.pipeline"):
        result = subprocess.run([sys.executable, "-m", module, "--help"], cwd=server_module.ROOT,
                                capture_output=True, text=True, timeout=10)
        assert result.returncode == 0, result.stderr
        assert "usage:" in result.stdout


def test_custom_filters_and_version_are_echoed_without_dropping_values(service: _LocalService) -> None:
    status, _, body = service.request("/api/path?source=1&target=3&max_authors=all&min_shared=1&year_start=2019&year_end=2020&genealogy=false&version=stale")
    assert status == 200
    result = _json(body)
    assert result["status"] == "ok"
    assert result["filters"] == {"max_authors": None, "min_shared": 1, "year_start": 2019, "year_end": 2020, "genealogy": False, "min_authors": 1}
    assert result["version"] == "acceptance-v1"
    assert result["version_mismatch"] is True
    assert result["requested_version"] == "stale"


def test_unknown_route_and_invalid_custom_metric_keep_json_error_surface(service: _LocalService) -> None:
    status, _, body = service.request("/api/does-not-exist")
    assert status == 404
    assert _json(body)["status"] == "not_found"

    status, _, body = service.request("/api/centrality?metric=made_up")
    assert status == 400
    assert _json(body)["status"] == "invalid_request"


def test_malformed_snapshot_does_not_replace_last_loaded_state(snapshot_path: Path) -> None:
    state = server_module.State(snapshot_path)
    assert state.snapshot["version"] == "acceptance-v1"
    snapshot_path.write_text("{\"version\": \"broken\"}", encoding="utf-8")
    snapshot_path.touch()
    with pytest.raises(ValueError, match="invalid schema"):
        state.reload()
    assert state.snapshot["version"] == "acceptance-v1"

    snapshot_path.write_text(json.dumps(_snapshot("acceptance-v2")), encoding="utf-8")
    time.sleep(0.001)
    state.reload()
    assert state.snapshot["version"] == "acceptance-v2"


@pytest.mark.parametrize("payload", [
    {"hits": []},
    {"hits": {"hits": 17}},
    {"hits": {"hits": [17]}},
    {"hits": {"hits": [{"metadata": []}]}},
    {"hits": {"hits": [{"metadata": {"control_number": 77, "name": []}}]}},
    {"hits": {"hits": [{"metadata": {"control_number": 77, "name": {}, "positions": [17]}}]}},
    {"hits": {"hits": [{"metadata": {"control_number": 77, "name": {}, "ids": [17]}}]}},
])
def test_malformed_live_upstream_payload_becomes_explicit_unavailable(monkeypatch: pytest.MonkeyPatch, snapshot_path: Path, payload: dict) -> None:
    # A proxy or upstream regression can return a non-object hit. The service
    # contract exposes this as upstream_unavailable rather than a traceback.
    monkeypatch.setattr(remote_module, "HTTPSConnection", make_connection_class(default=json_body(payload)))
    state = server_module.State(snapshot_path)
    result = state.live_search("Malformed payload")
    assert result["status"] == "upstream_unavailable"
    assert result["results"] == []
