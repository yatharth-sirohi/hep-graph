"""Keep-alive transport: connection reuse, staleness, bounds, and thread safety.

Most tests script ``http.client.HTTPSConnection`` through
``fake_https_connection``.  The ``real TLS`` tests at the end run the genuine
``http.client`` against a local TLS server when an ``openssl`` binary can mint
a certificate, and are skipped otherwise.
"""
from __future__ import annotations

from http.client import BadStatusLine, RemoteDisconnected
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import shutil
import socketserver
import ssl
import subprocess
import threading
import time
from urllib.error import HTTPError
from urllib.parse import urlsplit

import pytest

from fake_https_connection import ScriptedResponse, json_body, make_connection_class
from hepgraph import remote as remote_module
from hepgraph.remote import (MAX_IDLE_CONNECTIONS, MAX_IDLE_SECONDS, MAX_RESPONSE_BYTES, OVERSIZE_MESSAGE,
                             RemoteClient, RemoteError, _KeepAliveTransport)

URL = "https://inspirehep.net/api/literature?q=a&size=25"
TARGET = "/api/literature?q=a&size=25"
PAYLOAD = json_body({"hits": {"total": 1, "hits": [{"id": "1", "metadata": {"control_number": 1}}]}})
HEADERS = {"Accept": "application/json", "User-Agent": "hep-graph/1", "Connection": "keep-alive"}


class Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


def fake_connections(monkeypatch, script=(), **kwargs):
    connections = make_connection_class(script, **kwargs)
    monkeypatch.setattr(remote_module, "HTTPSConnection", connections)
    return connections


def stats(transport: _KeepAliveTransport, **expected: int) -> None:
    baseline = {"connections_opened": 0, "requests": 0, "reused_requests": 0,
                "stale_retries": 0, "idle_expired": 0, "idle_connections": 0}
    assert transport.stats() == baseline | expected


# (a) reuse ------------------------------------------------------------------

def test_sequential_requests_share_one_connection(monkeypatch) -> None:
    connections = fake_connections(monkeypatch, default=PAYLOAD)
    transport = _KeepAliveTransport()
    for _ in range(5):
        assert transport(URL, 4.0) == PAYLOAD
    assert connections.connects == 1
    (connection,) = connections.instances
    assert connection.requests == [("GET", TARGET, HEADERS)] * 5
    assert isinstance(connection.context, ssl.SSLContext)
    stats(transport, connections_opened=1, requests=5, reused_requests=4, idle_connections=1)


def test_pool_is_keyed_per_host(monkeypatch) -> None:
    connections = fake_connections(monkeypatch, default=PAYLOAD)
    transport = _KeepAliveTransport()
    transport("https://inspirehep.net/api/a", 4.0)
    transport("https://labs.inspirehep.net:8443/api/a", 4.0)
    transport("https://inspirehep.net/api/b", 4.0)
    assert [(c.host, c.port) for c in connections.instances] == [("inspirehep.net", 443), ("labs.inspirehep.net", 8443)]
    stats(transport, connections_opened=2, requests=3, reused_requests=1, idle_connections=2)


def test_idle_pool_is_capped(monkeypatch) -> None:
    barrier = threading.Barrier(3)

    def held() -> ScriptedResponse:
        barrier.wait(timeout=5)
        return ScriptedResponse(PAYLOAD)

    connections = fake_connections(monkeypatch, default=held)
    transport = _KeepAliveTransport(max_idle=2)
    threads = [threading.Thread(target=transport, args=(URL, 4.0)) for _ in range(3)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(5)
    assert connections.connects == 3 and connections.concurrent_violations == 0
    assert sum(connection.closed for connection in connections.instances) == 1
    stats(transport, connections_opened=3, requests=3, idle_connections=2)


# (b) Connection: close --------------------------------------------------------

def test_connection_close_response_drops_the_connection(monkeypatch) -> None:
    connections = fake_connections(
        monkeypatch, [PAYLOAD, ScriptedResponse(PAYLOAD, headers={"Connection": "close"})], default=PAYLOAD)
    transport = _KeepAliveTransport()
    transport(URL, 4.0)
    assert transport(URL, 4.0) == PAYLOAD
    assert connections.connects == 1 and connections.instances[0].closed
    stats(transport, connections_opened=1, requests=2, reused_requests=1)
    assert transport(URL, 4.0) == PAYLOAD
    assert connections.connects == 2 and not connections.instances[1].closed
    stats(transport, connections_opened=2, requests=3, reused_requests=1, idle_connections=1)


# (c)/(d) stale connections ----------------------------------------------------

@pytest.mark.parametrize("error", [
    RemoteDisconnected("Remote end closed connection without response"),
    BadStatusLine(""),
    ConnectionResetError(54, "Connection reset by peer"),
    BrokenPipeError(32, "Broken pipe"),
    ssl.SSLError(1, "[SSL: UNEXPECTED_EOF_WHILE_READING]"),
])
def test_stale_pooled_connection_is_retried_once_on_a_fresh_connection(monkeypatch, error) -> None:
    connections = fake_connections(monkeypatch, [PAYLOAD, error], default=PAYLOAD)
    transport = _KeepAliveTransport()
    transport(URL, 4.0)
    assert transport(URL, 4.0) == PAYLOAD
    assert connections.connects == 2
    first, second = connections.instances
    assert first.closed and not second.closed
    assert first.requests == [("GET", TARGET, HEADERS)] * 2 and second.requests == [("GET", TARGET, HEADERS)]
    stats(transport, connections_opened=2, requests=2, stale_retries=1, idle_connections=1)


def test_stale_failure_twice_in_a_row_propagates(monkeypatch) -> None:
    connections = fake_connections(monkeypatch, [PAYLOAD, RemoteDisconnected(), RemoteDisconnected()], default=PAYLOAD)
    clock = Clock()
    client = RemoteClient(clock=clock, sleep=clock.sleep)
    client.search("literature", "first")
    with pytest.raises(RemoteError) as info:
        client.search("literature", "second")
    assert (info.value.code, info.value.message, info.value.deadline) == ("upstream_unavailable", "INSPIRE is unavailable", False)
    assert connections.connects == 2 and all(connection.closed for connection in connections.instances)
    transport = client.cache_info()["transport"]
    assert transport["stale_retries"] == 1 and transport["idle_connections"] == 0
    # The pool recovers: the next request opens a new connection.
    client.search("literature", "third")
    assert connections.connects == 3 and client.cache_info()["transport"]["idle_connections"] == 1


def test_failures_that_are_not_a_stale_pooled_connection_are_not_retried(monkeypatch) -> None:
    # A fresh connection failing the same way is a real fault.
    connections = fake_connections(monkeypatch, [RemoteDisconnected()], default=PAYLOAD)
    transport = _KeepAliveTransport()
    with pytest.raises(RemoteDisconnected):
        transport(URL, 4.0)
    assert connections.connects == 1
    stats(transport, connections_opened=1, requests=1)

    # A timeout on a reused connection surfaces at once for the deadline logic.
    connections = fake_connections(monkeypatch, [PAYLOAD, TimeoutError("timed out")], default=PAYLOAD)
    transport = _KeepAliveTransport()
    transport(URL, 4.0)
    with pytest.raises(TimeoutError):
        transport(URL, 4.0)
    assert connections.connects == 1 and connections.instances[0].closed
    stats(transport, connections_opened=1, requests=2)

    # A failure after the status line was read is not retried either.
    connections = fake_connections(
        monkeypatch, [PAYLOAD, ScriptedResponse(PAYLOAD, read_error=ConnectionResetError())], default=PAYLOAD)
    transport = _KeepAliveTransport()
    transport(URL, 4.0)
    with pytest.raises(ConnectionResetError):
        transport(URL, 4.0)
    assert connections.connects == 1 and connections.instances[0].closed
    stats(transport, connections_opened=1, requests=2)

    # An HTTP error is never retried.
    connections = fake_connections(monkeypatch, [PAYLOAD, ScriptedResponse(b"{}", status=503, reason="Unavailable")], default=PAYLOAD)
    transport = _KeepAliveTransport()
    transport(URL, 4.0)
    with pytest.raises(HTTPError):
        transport(URL, 4.0)
    assert connections.connects == 1 and connections.instances[0].requests == [("GET", TARGET, HEADERS)] * 2


# (e) response cap -----------------------------------------------------------------

def test_oversize_body_is_truncated_and_its_connection_is_not_reused(monkeypatch) -> None:
    big = b"x" * (MAX_RESPONSE_BYTES + 2)
    connections = fake_connections(monkeypatch, [big], default=PAYLOAD)
    transport = _KeepAliveTransport()
    body = transport(URL, 4.0)
    assert len(body) == MAX_RESPONSE_BYTES + 1 and connections.instances[0].closed
    stats(transport, connections_opened=1, requests=1)
    assert transport(URL, 4.0) == PAYLOAD
    assert connections.connects == 2

    connections = fake_connections(monkeypatch, [big], default=PAYLOAD)
    clock = Clock()
    client = RemoteClient(clock=clock, sleep=clock.sleep)
    with pytest.raises(RemoteError) as info:
        client.search("literature", "huge")
    assert (info.value.code, info.value.message) == ("resource_limit", OVERSIZE_MESSAGE)
    cache = client.cache_info()
    assert cache["layers"]["literature"]["wire_bytes"] == MAX_RESPONSE_BYTES + 1
    assert cache["transport"]["connections_opened"] == 1 and cache["transport"]["idle_connections"] == 0


# (f) status handling --------------------------------------------------------------

def limited() -> ScriptedResponse:
    return ScriptedResponse(b'{"message":"slow down"}', status=429, reason="Too Many Requests", headers={"Retry-After": "9"})


def moved() -> ScriptedResponse:
    return ScriptedResponse(b"", status=302, reason="Found", headers={"Location": "https://inspirehep.net/api/elsewhere"})


def test_rate_limit_and_redirect_statuses_surface_as_http_errors(monkeypatch) -> None:
    connections = fake_connections(monkeypatch, [limited(), moved()], default=PAYLOAD)
    transport = _KeepAliveTransport()
    with pytest.raises(HTTPError) as limited_info:
        transport(URL, 4.0)
    error = limited_info.value
    assert (error.code, error.headers["Retry-After"], error.read()) == (429, "9", b'{"message":"slow down"}')
    assert RemoteClient._retry_after(error) == 9.0
    with pytest.raises(HTTPError) as moved_info:
        transport(URL, 4.0)
    assert moved_info.value.code == 302
    # The redirect was not followed, and both drained error responses left the
    # connection reusable.
    (connection,) = connections.instances
    assert connection.requests == [("GET", TARGET, HEADERS)] * 2
    stats(transport, connections_opened=1, requests=2, reused_requests=1, idle_connections=1)


def test_client_maps_rate_limit_to_cooldown_and_redirect_to_unavailable(monkeypatch) -> None:
    fake_connections(monkeypatch, [limited(), moved()], default=PAYLOAD)
    clock = Clock()
    client = RemoteClient(clock=clock, sleep=clock.sleep)
    with pytest.raises(RemoteError) as limited_info:
        client.search("literature", "first")
    assert limited_info.value.code == "resource_limit" and "retry after at least 9" in limited_info.value.message
    assert client.pacing_wait() == pytest.approx(9.0)
    clock.now += 10
    with pytest.raises(RemoteError) as moved_info:
        client.search("literature", "second")
    assert (moved_info.value.code, moved_info.value.message) == ("upstream_unavailable", "INSPIRE HTTP 302")


# (g) per-request timeout -----------------------------------------------------------

def test_timeout_is_applied_per_request_on_a_reused_connection(monkeypatch) -> None:
    connections = fake_connections(monkeypatch, default=PAYLOAD)
    transport = _KeepAliveTransport()
    transport(URL, 3.5)
    (connection,) = connections.instances
    assert connection.timeout == 3.5 and connection.sock.settimeouts == []
    transport(URL, 2.25)
    assert connection.timeout == 2.25 and connection.sock.settimeouts == [2.25]

    connections = fake_connections(monkeypatch, default=PAYLOAD)
    clock = Clock()
    client = RemoteClient(clock=clock, sleep=clock.sleep)
    client.search("literature", "first", deadline=clock.now + 3.0)
    # Pacing sleeps 0.5 s before the second request, leaving 2.0 s of its deadline.
    client.search("literature", "second", deadline=clock.now + 2.5)
    (connection,) = connections.instances
    assert connection.timeout == pytest.approx(2.0) and connection.sock.settimeouts == [pytest.approx(2.0)]


# (h) thread safety ----------------------------------------------------------------

def test_concurrent_requests_through_one_client_never_share_a_connection(monkeypatch) -> None:
    connections = fake_connections(monkeypatch, default=PAYLOAD, latency=0.002)
    # Real clock with a no-op sleep: pacing is exercised but takes no time.
    client = RemoteClient(clock=time.monotonic, sleep=lambda _: None)
    errors: list[BaseException] = []
    completed: list[int] = []

    def worker(index: int) -> None:
        for step in range(20):
            try:
                result = client.search("literature", f"thread:{index} step:{step}")
                assert result["hits"]["total"] == 1
                completed.append(1)
            except BaseException as exc:  # noqa: BLE001 - collected for the assertion
                errors.append(exc)

    threads = [threading.Thread(target=worker, args=(index,)) for index in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(30)
    assert errors == [] and len(completed) == 160
    assert connections.concurrent_violations == 0
    assert connections.max_concurrent > 1, "the threads never overlapped, so the assertion proved nothing"
    assert 1 <= connections.connects <= 8
    transport = client.cache_info()["transport"]
    assert transport["requests"] == 160 and transport["connections_opened"] == connections.connects
    assert transport["reused_requests"] == 160 - connections.connects
    assert transport["idle_connections"] <= MAX_IDLE_CONNECTIONS
    assert client.cache_info()["upstream_requests"] == 160


# (i) idle age -----------------------------------------------------------------------

def test_idle_connections_expire_on_borrow(monkeypatch) -> None:
    connections = fake_connections(monkeypatch, default=PAYLOAD)
    clock = Clock()
    transport = _KeepAliveTransport(clock=clock)
    transport(URL, 4.0)
    clock.now = 30.0
    transport(URL, 4.0)
    assert connections.connects == 1
    clock.now = 30.0 + MAX_IDLE_SECONDS + 0.001
    transport(URL, 4.0)
    assert connections.connects == 2 and connections.instances[0].closed
    stats(transport, connections_opened=2, requests=3, reused_requests=1, idle_expired=1, idle_connections=1)


# (j) scheme ----------------------------------------------------------------------------

def test_non_https_urls_are_refused_before_any_connection(monkeypatch) -> None:
    connections = fake_connections(monkeypatch, default=PAYLOAD)
    transport = _KeepAliveTransport()
    for url in ("http://inspirehep.net/api/literature", "ftp://inspirehep.net/x", "https:///path", "inspirehep.net/api"):
        with pytest.raises(ValueError):
            transport(url, 4.0)
    assert connections.connects == 0
    stats(transport)
    clock = Clock()
    client = RemoteClient(transport=transport, clock=clock, sleep=clock.sleep)
    with pytest.raises(RemoteError) as info:
        client._fetch_json("http://inspirehep.net/api/literature", clock.now + 5, "literature")
    assert info.value.code == "upstream_unavailable" and connections.connects == 0


# counters and close ------------------------------------------------------------------------

def test_cache_info_exposes_transport_counters_and_close_drops_the_pool(monkeypatch) -> None:
    connections = fake_connections(monkeypatch, default=PAYLOAD)
    clock = Clock()
    client = RemoteClient(clock=clock, sleep=clock.sleep)
    client.search("literature", "one")
    client.search("literature", "two")
    assert client.cache_info()["transport"] == {
        "connections_opened": 1, "requests": 2, "reused_requests": 1,
        "stale_retries": 0, "idle_expired": 0, "idle_connections": 1,
    }
    client.clear_cache()
    assert client.cache_info()["transport"]["idle_connections"] == 1
    client.close()
    assert connections.instances[0].closed and client.cache_info()["transport"]["idle_connections"] == 0
    # A closed pool still serves requests, without retaining connections.
    client.search("literature", "three")
    assert connections.connects == 2 and client.cache_info()["transport"]["idle_connections"] == 0
    client.close()
    # Injected callables carry no counters.
    assert RemoteClient(transport=lambda url, timeout: PAYLOAD).cache_info()["transport"] == {}


# real TLS -------------------------------------------------------------------------------------

OPENSSL = shutil.which("openssl")


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args) -> None:
        pass

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        self.server.paths.append(path)
        if path == "/ok":
            self._reply(200, PAYLOAD)
        elif path == "/close":
            self._reply(200, PAYLOAD, {"Connection": "close"})
        elif path == "/drop":
            # Answer as if keeping the connection, then close it anyway: what a
            # pooled connection looks like after the server's idle timeout.
            self._reply(200, PAYLOAD)
            self.close_connection = True
        elif path == "/big":
            self._reply(200, b"x" * (MAX_RESPONSE_BYTES + 100))
        elif path == "/limited":
            self._reply(429, b'{"message":"slow down"}', {"Retry-After": "9"})
        elif path == "/moved":
            self._reply(302, b"", {"Location": f"https://localhost:{self.server.server_port}/ok"})
        else:
            self._reply(404, b"{}")

    def _reply(self, status: int, body: bytes, headers: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)


class _Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, context: ssl.SSLContext) -> None:
        super().__init__(("127.0.0.1", 0), _Handler)
        self.socket = context.wrap_socket(self.socket, server_side=True)
        self.accepted = 0
        self.paths: list[str] = []
        self.counter_lock = threading.Lock()

    def server_bind(self) -> None:
        # Skip HTTPServer's reverse lookup of the bind address.
        socketserver.TCPServer.server_bind(self)
        self.server_name = "localhost"
        self.server_port = self.socket.getsockname()[1]

    def get_request(self):
        request, address = super().get_request()
        with self.counter_lock:
            self.accepted += 1
        return request, address

    def handle_error(self, request, client_address) -> None:
        pass


@pytest.fixture(scope="module")
def tls_server(tmp_path_factory):
    if OPENSSL is None:
        pytest.skip("no openssl binary to mint a test certificate")
    directory = tmp_path_factory.mktemp("tls")
    key, cert = directory / "key.pem", directory / "cert.pem"
    try:
        subprocess.run(
            [OPENSSL, "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", str(key), "-out", str(cert),
             "-days", "1", "-subj", "/CN=localhost", "-addext", "subjectAltName=DNS:localhost,IP:127.0.0.1"],
            check=True, capture_output=True, timeout=60)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        pytest.skip(f"openssl could not mint a test certificate: {exc}")
    server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_context.load_cert_chain(str(cert), str(key))
    server = _Server(server_context)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
    thread.start()
    client_context = ssl.create_default_context(cafile=str(cert))
    try:
        yield server, client_context
    finally:
        server.shutdown()
        server.server_close()


def test_real_tls_sequential_requests_reuse_one_connection(tls_server) -> None:
    server, context = tls_server
    transport = _KeepAliveTransport(ssl_context=context)
    accepted = server.accepted
    for _ in range(5):
        assert transport(f"https://localhost:{server.server_port}/ok", 5.0) == PAYLOAD
    assert server.accepted - accepted == 1
    stats(transport, connections_opened=1, requests=5, reused_requests=4, idle_connections=1)


def test_real_tls_connection_close_reconnects(tls_server) -> None:
    server, context = tls_server
    transport = _KeepAliveTransport(ssl_context=context)
    base = f"https://localhost:{server.server_port}"
    accepted = server.accepted
    assert transport(f"{base}/close", 5.0) == PAYLOAD
    assert transport.stats()["idle_connections"] == 0
    assert transport(f"{base}/ok", 5.0) == PAYLOAD
    assert server.accepted - accepted == 2
    stats(transport, connections_opened=2, requests=2, idle_connections=1)


def test_real_tls_connection_dropped_by_the_server_is_retried_once(tls_server) -> None:
    server, context = tls_server
    transport = _KeepAliveTransport(ssl_context=context)
    base = f"https://localhost:{server.server_port}"
    accepted = server.accepted
    assert transport(f"{base}/drop", 5.0) == PAYLOAD
    assert transport.stats()["idle_connections"] == 1
    assert transport(f"{base}/ok", 5.0) == PAYLOAD
    assert server.accepted - accepted == 2
    stats(transport, connections_opened=2, requests=2, stale_retries=1, idle_connections=1)


def test_real_tls_oversize_body_is_truncated_and_its_connection_discarded(tls_server) -> None:
    server, context = tls_server
    transport = _KeepAliveTransport(ssl_context=context)
    base = f"https://localhost:{server.server_port}"
    accepted = server.accepted
    assert len(transport(f"{base}/big", 5.0)) == MAX_RESPONSE_BYTES + 1
    assert transport.stats()["idle_connections"] == 0
    assert transport(f"{base}/ok", 5.0) == PAYLOAD
    assert server.accepted - accepted == 2


def test_real_tls_error_statuses_are_http_errors_and_redirects_are_not_followed(tls_server) -> None:
    server, context = tls_server
    transport = _KeepAliveTransport(ssl_context=context)
    base = f"https://localhost:{server.server_port}"
    accepted, seen = server.accepted, len(server.paths)
    with pytest.raises(HTTPError) as limited_info:
        transport(f"{base}/limited", 5.0)
    assert limited_info.value.code == 429 and RemoteClient._retry_after(limited_info.value) == 9.0
    with pytest.raises(HTTPError) as moved_info:
        transport(f"{base}/moved", 5.0)
    assert moved_info.value.code == 302
    assert server.paths[seen:] == ["/limited", "/moved"]
    assert server.accepted - accepted == 1
    stats(transport, connections_opened=1, requests=2, reused_requests=1, idle_connections=1)
