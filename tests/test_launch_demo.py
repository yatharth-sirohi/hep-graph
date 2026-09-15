"""Unit checks for the dependency-free local professor-demo launcher."""

from __future__ import annotations

import json
from pathlib import Path
import stat

import launch_demo


class _Response:
    status = 200
    headers = {"Content-Type": "application/json; charset=utf-8"}

    def __init__(self, payload: object):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit: int = -1) -> bytes:
        return self.payload[:limit] if limit >= 0 else self.payload


class _FakeChild:
    returncode = None

    def __init__(self, command):
        self.command = command
        self.terminated = False

    def poll(self):
        return 0 if self.terminated else None

    def wait(self, timeout=None):
        self.terminated = True
        self.returncode = 0
        return 0

    def terminate(self):
        self.terminated = True
        self.returncode = 0

    def kill(self):
        self.terminated = True
        self.returncode = -9


def test_check_reuses_matching_service_without_browser_or_child(monkeypatch):
    expected = launch_demo.snapshot_version()
    monkeypatch.setattr(
        launch_demo.urllib.request,
        "urlopen",
        lambda request, timeout: _Response({"status": "ok", "version": expected, "service_version": "general-search-v3"}),
    )
    monkeypatch.setattr(launch_demo.webbrowser, "open", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("browser opened")))
    monkeypatch.setattr(launch_demo.subprocess, "Popen", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("child started")))

    assert launch_demo.run(check_only=True) == 0


def test_mismatched_existing_service_is_left_running(monkeypatch, capsys):
    monkeypatch.setattr(
        launch_demo.urllib.request,
        "urlopen",
        lambda request, timeout: _Response({"status": "ok", "version": "old-snapshot", "service_version": "general-search-v3"}),
    )
    monkeypatch.setattr(launch_demo.subprocess, "Popen", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("existing service replaced")))

    assert launch_demo.run(check_only=True) == 2
    assert "will not stop it" in capsys.readouterr().err


def test_new_child_is_bounded_then_opens_fixed_demo_route(monkeypatch):
    expected = launch_demo.snapshot_version()
    probes = iter([
        launch_demo.Probe("unavailable", detail="nothing is listening"),
        launch_demo.Probe("ready", version=expected),
    ])
    monkeypatch.setattr(launch_demo, "probe_service", lambda: next(probes))
    children = []

    def fake_popen(command, **kwargs):
        child = _FakeChild(command)
        children.append((child, kwargs))
        return child

    opened = []
    monkeypatch.setattr(launch_demo.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(launch_demo.webbrowser, "open", lambda url, new: opened.append((url, new)) or True)

    assert launch_demo.run() == 0
    assert len(children) == 1
    child, kwargs = children[0]
    assert child.command[:3] == [launch_demo.sys.executable, "-m", "hepgraph.server"]
    assert "--host" in child.command and launch_demo.HOST in child.command
    assert "--port" in child.command and str(launch_demo.PORT) in child.command
    assert kwargs["cwd"] == launch_demo.ROOT
    assert opened == [(launch_demo.DEMO_URL, 2)]


def test_old_service_with_same_snapshot_cannot_silently_replace_live_mode(monkeypatch, capsys):
    monkeypatch.setattr(launch_demo.urllib.request, "urlopen",
        lambda request, timeout: _Response({'status': 'ok', 'version': launch_demo.snapshot_version()}))
    monkeypatch.setattr(launch_demo.subprocess, "Popen",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError('old service replaced')))
    assert launch_demo.run(check_only=True) == 2
    assert 'older HEP Graph service' in capsys.readouterr().err


def test_mac_launcher_is_executable_and_uses_portable_python_candidates():
    launcher = launch_demo.ROOT / "Start HEP Graph.command"
    assert launcher.stat().st_mode & stat.S_IXUSR
    text = launcher.read_text(encoding="utf-8")
    assert ".venv/bin/python" in text
    assert "/opt/homebrew/bin/python3" in text
    assert "/usr/local/bin/python3" in text
    assert "command -v python3" in text
