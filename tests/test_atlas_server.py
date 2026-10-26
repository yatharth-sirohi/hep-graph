"""HTTP tests for the additive HEP Atlas static routes under /atlas.

The fixture mirrors tests/test_server.py: a socketpair drives the production
BaseHTTPRequestHandler without binding a port. No network is used.
"""

from __future__ import annotations

import json
from pathlib import Path
import socket
import threading

import pytest

from hepgraph import server as server_module


def _person(person_id: str) -> dict:
    return {
        "id": person_id,
        "name": f"Person {person_id}",
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
def service():
    class LocalServer:
        def __init__(self):
            self.state = server_module.State()

        def request(self, path: str, *, method: str = "GET", body: bytes | None = None):
            left, right = socket.socketpair()
            try:
                body = body or b""
                headers = [f"{method} {path} HTTP/1.0", "Host: localhost", "Connection: close"]
                if body:
                    headers.append(f"Content-Length: {len(body)}")
                left.sendall(("\r\n".join(headers) + "\r\n\r\n").encode() + body)
                left.shutdown(socket.SHUT_WR)

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


def _request(base, path: str, *, method: str = "GET") -> tuple[int, dict[str, str], bytes]:
    return base.request(path, method=method)


def _json(body: bytes) -> dict:
    return json.loads(body.decode("utf-8"))


MANIFEST_BYTES = b'{"version":"abc123",  "files": {"atlas.json": "atlas.json"}}\n'
NOT_FOUND = b'{"status": "not_found"}'


@pytest.fixture
def atlas_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "atlas-static"
    (root / "generated").mkdir(parents=True)
    (root / "assets").mkdir()
    (root / "subdir").mkdir()
    (root / "index.html").write_text("<!doctype html><title>HEP Atlas</title><h1>HEP Atlas</h1>", encoding="utf-8")
    (root / "atlas.js").write_text("console.log('atlas');\n", encoding="utf-8")
    (root / "atlas.css").write_text("body { margin: 0 }\n", encoding="utf-8")
    (root / "generated" / "manifest.json").write_bytes(MANIFEST_BYTES)
    (root / "generated" / "atlas.json").write_text(json.dumps({"nodes": []}), encoding="utf-8")
    (root / "assets" / "logo.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8")
    # Local-map view (docs/HEP_ATLAS_GEOMETRY.md §4): the vendored Leaflet
    # bundle and the lazily-fetched per-map geometry bundle.
    (root / "vendor" / "leaflet" / "images").mkdir(parents=True)
    (root / "vendor" / "leaflet" / "leaflet.js").write_text("/* leaflet */\n", encoding="utf-8")
    (root / "vendor" / "leaflet" / "leaflet.css").write_text(".leaflet-container{}\n", encoding="utf-8")
    (root / "vendor" / "leaflet" / "images" / "layers.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (root / "generated" / "geometry").mkdir()
    (root / "generated" / "geometry" / "cern.json").write_text(
        json.dumps({"features": []}), encoding="utf-8")
    (root / "notes.txt").write_text("private notes", encoding="utf-8")
    monkeypatch.setattr(server_module, "ATLAS_STATIC", root)
    return root


def _assert_security_headers(headers: dict[str, str]) -> None:
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert "Content-Security-Policy" in headers
    assert "X-HEP-Instance" in headers


ATLAS_CACHE_CONTROL = "public, max-age=0, must-revalidate"


def test_atlas_index_is_served_with_and_without_trailing_slash(service, atlas_dir) -> None:
    base, _ = service
    for path in ("/atlas", "/atlas/"):
        status, headers, body = _request(base, path)
        assert status == 200, path
        assert headers["Content-Type"] == "text/html; charset=utf-8"
        assert headers["Cache-Control"] == ATLAS_CACHE_CONTROL
        assert "ETag" in headers
        assert b"HEP Atlas" in body
        _assert_security_headers(headers)


def test_atlas_scripts_styles_and_images_have_their_content_types(service, atlas_dir) -> None:
    base, _ = service
    status, headers, body = _request(base, "/atlas/atlas.js")
    assert status == 200
    assert headers["Content-Type"] == "text/javascript; charset=utf-8"
    assert headers["Cache-Control"] == ATLAS_CACHE_CONTROL
    assert "ETag" in headers
    assert body == (atlas_dir / "atlas.js").read_bytes()
    _assert_security_headers(headers)

    status, headers, body = _request(base, "/atlas/atlas.css")
    assert status == 200
    assert headers["Content-Type"] == "text/css; charset=utf-8"
    assert headers["Cache-Control"] == ATLAS_CACHE_CONTROL
    assert "ETag" in headers
    assert body == (atlas_dir / "atlas.css").read_bytes()

    status, headers, body = _request(base, "/atlas/assets/logo.svg")
    assert status == 200
    assert headers["Content-Type"] == "image/svg+xml"
    assert headers["Cache-Control"] == ATLAS_CACHE_CONTROL
    assert "ETag" in headers
    assert body == (atlas_dir / "assets" / "logo.svg").read_bytes()
    _assert_security_headers(headers)


def test_atlas_serves_html_under_subpaths(service, atlas_dir) -> None:
    """respond_atlas serves any .html file under /atlas/, not just the index —
    the route in hepgraph/server.py is generic over path/extension rather than
    special-casing index.html, which is what lets static/atlas/about.html be
    served at /atlas/about.html with no server change (see the sibling test
    below, which checks the real file at that real path)."""
    base, _ = service
    (atlas_dir / "about.html").write_text("<!doctype html><title>About</title><h1>About</h1>", encoding="utf-8")
    nested = atlas_dir / "docs"
    nested.mkdir()
    (nested / "guide.html").write_text("<!doctype html><title>Guide</title><h1>Guide</h1>", encoding="utf-8")

    status, headers, body = _request(base, "/atlas/about.html")
    assert status == 200
    assert headers["Content-Type"] == "text/html; charset=utf-8"
    assert headers["Cache-Control"] == ATLAS_CACHE_CONTROL
    assert "ETag" in headers
    assert b"About" in body
    _assert_security_headers(headers)

    status, headers, body = _request(base, "/atlas/docs/guide.html")
    assert status == 200
    assert headers["Content-Type"] == "text/html; charset=utf-8"
    assert b"Guide" in body


def test_about_page_is_served_at_its_real_path(service) -> None:
    """Integration check against the real static/atlas tree (ATLAS_STATIC is
    not monkeypatched here): the methodology page this branch adds is
    reachable at /atlas/about.html exactly as the footer links to it."""
    base, _ = service
    status, headers, body = _request(base, "/atlas/about.html")
    assert status == 200
    assert headers["Content-Type"] == "text/html; charset=utf-8"
    assert headers["Cache-Control"] == ATLAS_CACHE_CONTROL
    assert "ETag" in headers
    assert b"About" in body and b"HEP Atlas" in body
    assert b'id="coverage"' in body
    _assert_security_headers(headers)


def test_local_map_assets_are_served_with_their_content_types(service, atlas_dir) -> None:
    """The §4 local-map view needs three things served from /atlas: the
    vendored Leaflet script and stylesheet, Leaflet's own PNG sprites, and
    the per-map geometry bundle under generated/geometry/. A missing
    content type here is a 404, so the map silently never opens."""
    base, _ = service
    expected = {
        "/atlas/vendor/leaflet/leaflet.js": "text/javascript; charset=utf-8",
        "/atlas/vendor/leaflet/leaflet.css": "text/css; charset=utf-8",
        "/atlas/vendor/leaflet/images/layers.png": "image/png",
        "/atlas/generated/geometry/cern.json": "application/json; charset=utf-8",
    }
    for path, content_type in expected.items():
        status, headers, body = _request(base, path)
        assert status == 200, path
        assert headers["Content-Type"] == content_type, path
        assert headers["Cache-Control"] == ATLAS_CACHE_CONTROL, path
        assert "ETag" in headers, path
        assert body == (atlas_dir / path[len("/atlas/"):]).read_bytes(), path
        _assert_security_headers(headers)


def test_csp_allows_openstreetmap_tiles_as_images_only(service, atlas_dir) -> None:
    """The local map draws over OSM standard tiles, which are plain <img>
    requests to a third-party origin. img-src must name those hosts, and
    nothing else may be relaxed to reach them."""
    base, _ = service
    _status, headers, _body = _request(base, "/atlas/")
    policy = headers["Content-Security-Policy"]
    img_src = next(d.strip() for d in policy.split(";") if d.strip().startswith("img-src"))
    assert "https://tile.openstreetmap.org" in img_src
    assert "https://*.tile.openstreetmap.org" in img_src
    for directive in ("default-src 'self'", "script-src 'self'", "connect-src 'self'",
                      "object-src 'none'", "frame-ancestors 'none'"):
        assert directive in policy, directive
    assert "openstreetmap" not in policy.replace(img_src, "")


def test_geolocation_is_allowed_to_the_atlas_pages_only(service, atlas_dir) -> None:
    """"Over my location" on a local map needs the Geolocation API, which the site-wide policy
    switched off. Only the Atlas may use it, only for its own origin; camera and microphone
    stay off, and every other route keeps geolocation off."""
    base, _ = service
    _status, atlas_headers, _body = _request(base, "/atlas/")
    assert atlas_headers["Permissions-Policy"] == "camera=(), microphone=(), geolocation=(self)"
    _status, home_headers, _body = _request(base, "/")
    assert home_headers["Permissions-Policy"] == "camera=(), microphone=(), geolocation=()"


def test_generated_files_are_cacheable_and_sent_byte_for_byte(service, atlas_dir) -> None:
    base, _ = service
    status, headers, body = _request(base, "/atlas/generated/manifest.json")
    assert status == 200
    assert headers["Content-Type"] == "application/json; charset=utf-8"
    assert headers["Cache-Control"] == ATLAS_CACHE_CONTROL
    assert headers["Content-Length"] == str(len(MANIFEST_BYTES))
    assert "ETag" in headers
    # Raw bytes, not a json.dumps re-encoding of the parsed document.
    assert body == MANIFEST_BYTES
    _assert_security_headers(headers)

    status, headers, body = _request(base, "/atlas/generated/atlas.json")
    assert status == 200
    assert headers["Cache-Control"] == ATLAS_CACHE_CONTROL
    assert "ETag" in headers
    assert body == (atlas_dir / "generated" / "atlas.json").read_bytes()


def test_generated_json_and_vendor_js_revalidate_with_etag(service, atlas_dir) -> None:
    """ETag present on every response; a matching If-None-Match gets a
    304 with no body; a stale one gets a full 200 with the real bytes."""
    base, _ = service
    (atlas_dir / "vendor").mkdir(exist_ok=True)
    vendor_bytes = b"window.Globe = function Globe() {};\n"
    (atlas_dir / "vendor" / "globe.gl.min.js").write_bytes(vendor_bytes)

    for path, expected_body in (
        ("/atlas/generated/manifest.json", MANIFEST_BYTES),
        ("/atlas/generated/atlas.json", (atlas_dir / "generated" / "atlas.json").read_bytes()),
        ("/atlas/vendor/globe.gl.min.js", vendor_bytes),
    ):
        status, headers, body = _request(base, path)
        assert status == 200, path
        etag = headers["ETag"]
        assert etag, path
        assert body == expected_body, path

        status2, headers2, body2 = base.request(path, method="GET")
        assert status2 == 200
        assert headers2["ETag"] == etag, "the same unchanged file must hash to the same ETag"

        # A matching If-None-Match: a 304 with no body.
        status3, headers3, body3 = _conditional_request(base, path, if_none_match=etag)
        assert status3 == 304, path
        assert body3 == b""
        assert headers3.get("ETag") == etag
        assert headers3["Cache-Control"] == ATLAS_CACHE_CONTROL
        assert "Content-Type" not in headers3

        # A stale/unknown ETag: a full 200 with the real bytes again.
        status4, headers4, body4 = _conditional_request(base, path, if_none_match='"stale-etag-value"')
        assert status4 == 200, path
        assert body4 == expected_body, path
        assert headers4["ETag"] == etag


def _conditional_request(base, path: str, *, if_none_match: str):
    left, right = socket.socketpair()
    try:
        headers = [
            f"GET {path} HTTP/1.0", "Host: localhost", "Connection: close",
            f"If-None-Match: {if_none_match}",
        ]
        left.sendall(("\r\n".join(headers) + "\r\n\r\n").encode())
        left.shutdown(socket.SHUT_WR)

        def serve_one():
            try:
                server_module.Handler(right, ("127.0.0.1", 12345), base)
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


def test_disallowed_extensions_directories_and_missing_files_are_not_found(service, atlas_dir) -> None:
    base, _ = service
    for path in ("/atlas/notes.txt", "/atlas/generated", "/atlas/generated/", "/atlas/subdir", "/atlas/missing.json", "/atlas/assets"):
        status, headers, body = _request(base, path)
        assert status == 404, path
        assert headers["Content-Type"] == "application/json; charset=utf-8"
        assert _json(body) == {"status": "not_found"}
        assert b"private notes" not in body
        _assert_security_headers(headers)


def test_traversal_attempts_are_not_found_and_expose_nothing(service, atlas_dir) -> None:
    base, _ = service
    pyproject = (server_module.ROOT / "pyproject.toml").read_bytes()
    assert pyproject, "the traversal target must exist for the test to be meaningful"
    attempts = (
        "/atlas/../index.html",
        "/atlas/%2e%2e/%2e%2e/pyproject.toml",
        "/atlas/generated/..%2f..%2fpyproject.toml",
        "/atlas//index.html",
        "/atlas/..%5cindex.html",
        "/atlas/generated/../../../pyproject.toml",
        "/atlas/generated//manifest.json",
        "/atlas/%00.html",
        "/atlas/generated%2f..%2f..%2fpyproject.toml",
    )
    for path in attempts:
        status, headers, body = _request(base, path)
        assert status == 404, path
        assert _json(body) == {"status": "not_found"}
        assert body != pyproject
        assert b"[project]" not in body and b"HEP Atlas" not in body and b"HEP Graph" not in body
        _assert_security_headers(headers)


def test_head_returns_headers_without_body(service, atlas_dir) -> None:
    base, _ = service
    status, headers, body = _request(base, "/atlas/generated/manifest.json", method="HEAD")
    assert status == 200
    assert headers["Content-Type"] == "application/json; charset=utf-8"
    assert headers["Content-Length"] == str(len(MANIFEST_BYTES))
    assert headers["Cache-Control"] == ATLAS_CACHE_CONTROL
    assert "ETag" in headers
    assert body == b""
    _assert_security_headers(headers)

    status, headers, body = _request(base, "/atlas", method="HEAD")
    assert status == 200
    assert headers["Content-Length"] == str(len((atlas_dir / "index.html").read_bytes()))
    assert body == b""


def test_missing_index_yields_not_found_json(service, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    base, _ = service
    empty = tmp_path / "empty-atlas"
    empty.mkdir()
    monkeypatch.setattr(server_module, "ATLAS_STATIC", empty)
    for path in ("/atlas", "/atlas/"):
        status, headers, body = _request(base, path)
        assert status == 404, path
        assert headers["Content-Type"] == "application/json; charset=utf-8"
        assert headers["Cache-Control"] == "no-store"
        assert _json(body) == {"status": "not_found"}


def test_hep_graph_routes_are_unchanged(service, atlas_dir) -> None:
    base, _ = service
    status, headers, body = _request(base, "/")
    assert status == 200
    assert headers["Content-Type"] == "text/html; charset=utf-8"
    # The shell is cacheable by a shared cache and revalidated by ETag; what
    # this test guards is that serving the atlas did not change these routes.
    assert headers["Cache-Control"] == server_module.Handler.SHELL_CACHE_CONTROL
    assert b"HEP Graph" in body
    _assert_security_headers(headers)

    expected = {
        "/app.js": "text/javascript; charset=utf-8",
        "/styles.css": "text/css; charset=utf-8",
        "/favicon.svg": "image/svg+xml; charset=utf-8",
        "/index.html": "text/html; charset=utf-8",
    }
    for path, content_type in expected.items():
        status, headers, body = _request(base, path)
        assert status == 200, path
        assert headers["Content-Type"] == content_type
        assert headers["Cache-Control"] == (
            server_module.Handler.SHELL_CACHE_CONTROL if path.endswith(".html")
            else server_module.Handler.ASSET_CACHE_CONTROL)
        assert body

    status, headers, body = _request(base, "/api/health")
    assert status == 200
    assert headers["Content-Type"] == "application/json; charset=utf-8"
    assert headers["Cache-Control"] == "no-store"
    assert _json(body)["status"] == "ok"

    for path in ("/data/current.json", "/static/app.js", "/atlasx", "/atlas-foo", "/atlas.html"):
        status, headers, body = _request(base, path)
        assert status == 404, path
        assert headers["Content-Type"] == "application/json; charset=utf-8"
        assert headers["Cache-Control"] == "no-store"
        assert body == NOT_FOUND
