"""A scripted stand-in for ``http.client.HTTPSConnection``.

``hepgraph.remote._KeepAliveTransport`` looks the class up as the module
attribute ``hepgraph.remote.HTTPSConnection`` at connect time, so a test can
``monkeypatch.setattr(remote_module, "HTTPSConnection", make_connection_class(...))``
and observe connects, requests, timeouts and connection sharing without a
network.  Responses mimic the parts of ``http.client.HTTPResponse`` the
transport relies on: ``read(amt)`` clips to the body and marks the response
closed once drained, ``will_close`` follows ``Connection: close``, and a
``will_close`` response detaches the connection's socket as ``getresponse``
does.
"""
from __future__ import annotations

from collections import deque
from http.client import HTTPMessage
import json
import threading
import time
from typing import Any, Callable


def json_body(payload: Any) -> bytes:
    return json.dumps(payload).encode()


class ScriptedResponse:
    def __init__(self, body: bytes = b"{}", *, status: int = 200, reason: str = "OK",
                 headers: dict[str, str] | None = None, close: bool = False,
                 read_error: BaseException | None = None) -> None:
        self.status = status
        self.reason = reason
        self.headers = HTTPMessage()
        for name, value in (headers or {}).items():
            self.headers[name] = value
        self.will_close = close or self.headers.get("Connection", "").lower() == "close"
        self._remaining = body
        self._closed = False
        self._read_error = read_error
        self._owner: FakeConnectionBase | None = None

    def read(self, amt: int | None = None) -> bytes:
        if self._read_error is not None:
            error, self._read_error = self._read_error, None
            raise error
        if self._closed:
            return b""
        if amt is None or amt >= len(self._remaining):
            chunk, self._remaining = self._remaining, b""
            self._finish()
        else:
            chunk, self._remaining = self._remaining[:amt], self._remaining[amt:]
        return chunk

    def isclosed(self) -> bool:
        return self._closed

    def close(self) -> None:
        self._finish()

    def _finish(self) -> None:
        self._closed = True
        if self._owner is not None:
            self._owner._release()


class FakeSocket:
    def __init__(self) -> None:
        self.settimeouts: list[float] = []

    def settimeout(self, timeout: float) -> None:
        self.settimeouts.append(timeout)


class FakeConnectionBase:
    """Class-level state is per generated class, so each test gets a clean slate."""

    lock: threading.Lock
    instances: list[FakeConnectionBase]
    script: deque[Any]
    default: Any
    connect_error: BaseException | None
    latency: float
    connects: int
    concurrent_violations: int
    active: int
    max_concurrent: int

    def __init__(self, host: str, port: int | None = None, *, timeout: float | None = None,
                 context: Any = None) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.context = context
        self.sock: FakeSocket | None = None
        self.closed = False
        self.requests: list[tuple[str, str, dict[str, str]]] = []
        self._busy = False

    def connect(self) -> None:
        cls = type(self)
        with cls.lock:
            if cls.connect_error is not None:
                raise cls.connect_error
            cls.connects += 1
            cls.instances.append(self)
        self.sock = FakeSocket()

    def request(self, method: str, path: str, body: Any = None, headers: dict[str, str] | None = None) -> None:
        cls = type(self)
        if self.sock is None:
            raise RuntimeError("request on a connection without a socket")
        with cls.lock:
            if self._busy:
                cls.concurrent_violations += 1
            self._busy = True
            cls.active += 1
            cls.max_concurrent = max(cls.max_concurrent, cls.active)
        self.requests.append((method, path, dict(headers or {})))

    def getresponse(self) -> ScriptedResponse:
        cls = type(self)
        with cls.lock:
            action = cls.script.popleft() if cls.script else cls.default
        if cls.latency:
            time.sleep(cls.latency)
        if isinstance(action, type) and issubclass(action, BaseException):
            action = action()
        if isinstance(action, BaseException):
            self._release()
            self.sock = None
            raise action
        if callable(action) and not isinstance(action, ScriptedResponse):
            action = action()
        response = action if isinstance(action, ScriptedResponse) else ScriptedResponse(action)
        response._owner = self
        if response.will_close:
            # http.client hands the socket to the response and closes itself.
            self.sock = None
            self.closed = True
        return response

    def close(self) -> None:
        self.sock = None
        self.closed = True
        self._release()

    def _release(self) -> None:
        cls = type(self)
        with cls.lock:
            if self._busy:
                self._busy = False
                cls.active -= 1


def make_connection_class(script: tuple[Any, ...] | list[Any] = (), *, default: Any = b"{}",
                          connect_error: BaseException | None = None,
                          latency: float = 0.0) -> type[FakeConnectionBase]:
    """Build a fresh fake class.

    ``script`` entries are consumed one per ``getresponse`` across all
    connections: ``bytes`` become a 200 JSON response, a ``ScriptedResponse``
    is returned as is, an exception (instance or class) is raised, and a
    callable is invoked for the response.  ``default`` serves every request
    once the script is exhausted.
    """
    namespace = {
        "lock": threading.Lock(), "instances": [], "script": deque(script), "default": default,
        "connect_error": connect_error, "latency": latency, "connects": 0,
        "concurrent_violations": 0, "active": 0, "max_concurrent": 0,
    }
    return type("FakeHTTPSConnection", (FakeConnectionBase,), namespace)
