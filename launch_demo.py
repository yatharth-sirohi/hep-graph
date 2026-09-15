"""Start or verify the local HEP Graph professor demo.

This helper deliberately binds only to loopback and never stops a process that
it did not start.  It is dependency-free and can be run from any directory.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser


ROOT = Path(__file__).resolve().parent
SNAPSHOT = ROOT / "data" / "current.json"
HOST = "127.0.0.1"
PORT = 8765
BASE_URL = f"http://{HOST}:{PORT}"
HEALTH_URL = f"{BASE_URL}/api/health"
DEMO_URL = f"{BASE_URL}/?mode=live"
READY_TIMEOUT = 10.0
SERVICE_VERSION = "general-search-v3"


@dataclass(frozen=True)
class Probe:
    """The result of probing the fixed local health endpoint."""

    state: str  # ready, unavailable, occupied
    version: str | None = None
    detail: str = ""


def snapshot_version(path: Path = SNAPSHOT) -> str:
    """Read the version of the snapshot the demo is about to display."""

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Cannot read the published snapshot at {path}: {exc}") from exc
    version = data.get("version") if isinstance(data, dict) else None
    if not isinstance(version, str) or not version:
        raise RuntimeError(f"The published snapshot at {path} has no usable version.")
    return version


def probe_service(timeout: float = 0.8) -> Probe:
    """Probe only the fixed loopback health URL and classify the port safely."""

    request = urllib.request.Request(HEALTH_URL, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                return Probe("occupied", detail=f"health endpoint returned HTTP {response.status}")
            content_type = response.headers.get("Content-Type", "")
            if "application/json" not in content_type:
                return Probe("occupied", detail="health endpoint did not return JSON")
            raw = response.read(64 * 1024)
        payload = json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return Probe("occupied", detail=f"health endpoint returned HTTP {exc.code}")
    except urllib.error.URLError as exc:
        reason = exc.reason
        if isinstance(reason, (ConnectionRefusedError, ConnectionResetError, socket.timeout, TimeoutError)):
            return Probe("unavailable", detail="nothing is listening on the demo port")
        return Probe("occupied", detail=f"the demo port could not be inspected: {reason}")
    except (ConnectionRefusedError, ConnectionResetError, socket.timeout, TimeoutError):
        return Probe("unavailable", detail="nothing is listening on the demo port")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return Probe("occupied", detail=f"the demo port returned an unreadable response: {exc}")

    if not isinstance(payload, dict) or payload.get("status") != "ok" or not isinstance(payload.get("version"), str):
        return Probe("occupied", detail="the demo port is occupied by an unexpected service")
    if payload.get("service_version") != SERVICE_VERSION:
        return Probe("occupied", detail="an older HEP Graph service is running; stop its own Terminal window and start this release")
    return Probe("ready", version=payload["version"])


def wait_until_ready(expected_version: str, process: subprocess.Popen[bytes | str]) -> Probe:
    """Wait at most ten seconds for our child server to expose the expected version."""

    deadline = time.monotonic() + READY_TIMEOUT
    last = Probe("unavailable", detail="waiting for the server")
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"HEP Graph exited before becoming ready (status {process.returncode}).")
        last = probe_service()
        if last.state == "ready" and last.version == expected_version:
            return last
        if last.state == "ready" and last.version != expected_version:
            raise RuntimeError(
                "Port 8765 is serving a different HEP Graph snapshot "
                f"({last.version}); refusing to stop or replace it."
            )
        if last.state == "occupied":
            raise RuntimeError(f"Port 8765 became occupied by another service: {last.detail}; no process was stopped.")
        time.sleep(0.2)
    raise RuntimeError(f"HEP Graph did not become ready within {READY_TIMEOUT:.0f} seconds: {last.detail}.")


def stop_child(process: subprocess.Popen[bytes | str] | None) -> None:
    """Stop only a child created by this invocation."""

    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=3)


def run(*, check_only: bool = False, no_browser: bool = False) -> int:
    """Verify or launch the demo; return a shell-friendly status code."""

    expected = snapshot_version()
    existing = probe_service()
    child: subprocess.Popen[bytes | str] | None = None

    if existing.state == "ready":
        if existing.version != expected:
            message = (
                "Port 8765 already serves HEP Graph snapshot "
                f"{existing.version}, while current.json is {expected}. "
                "Close or update that service yourself; this launcher will not stop it."
            )
            print(message, file=sys.stderr)
            return 2
        print(f"HEP Graph is already ready at {BASE_URL} (snapshot {expected}).")
    elif existing.state == "occupied":
        print(f"Cannot start HEP Graph: {existing.detail}. Port 8765 was left untouched.", file=sys.stderr)
        return 2
    elif check_only:
        print(f"No HEP Graph service is ready at {HEALTH_URL}; --check did not start one.", file=sys.stderr)
        return 2
    else:
        command = [
            sys.executable,
            "-m",
            "hepgraph.server",
            "--host",
            HOST,
            "--port",
            str(PORT),
            "--snapshot",
            str(SNAPSHOT),
        ]
        print(f"Starting local HEP Graph on {BASE_URL} with snapshot {expected}.")
        child = subprocess.Popen(command, cwd=ROOT)
        try:
            wait_until_ready(expected, child)
        except Exception:
            stop_child(child)
            raise
        print("HEP Graph is ready. Keep this Terminal window open; press Control-C to stop the server.")

    if check_only:
        print(f"Verified HEP Graph snapshot {expected} at {HEALTH_URL}.")
        return 0
    if not no_browser:
        if not webbrowser.open(DEMO_URL, new=2):
            print(f"Open this demo URL in a browser: {DEMO_URL}")
        else:
            print(f"Opened the five-hop demo route: {DEMO_URL}")
    else:
        print(f"Browser opening skipped (--no-browser). Demo URL: {DEMO_URL}")

    if child is None:
        return 0
    try:
        child.wait()
    except KeyboardInterrupt:
        print("Stopping the HEP Graph child server.")
    finally:
        stop_child(child)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify an existing matching service without starting or opening a browser")
    parser.add_argument("--no-browser", action="store_true", help="start or reuse the service without opening a browser")
    args = parser.parse_args(argv)
    try:
        return run(check_only=args.check, no_browser=args.no_browser)
    except (RuntimeError, OSError) as exc:
        print(f"HEP Graph demo launcher: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
