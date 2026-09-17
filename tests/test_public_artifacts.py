"""Fail CI if a private snapshot or unusually large artifact is tracked."""

from pathlib import Path
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_PREFIXES = ("data/production/", "data/snapshots/", "data/candidates/")
PRIVATE_SUFFIXES = (".sqlite", ".db", ".dump", ".sql.gz", ".pem", ".key", ".p12")
MAX_TRACKED_BYTES = 10 * 1024 * 1024


def test_no_private_or_oversized_artifacts_are_tracked():
    listed = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=False)
    if listed.returncode:
        pytest.skip("git checkout unavailable in packaged source")
    tracked = [Path(path.decode()) for path in listed.stdout.split(b"\0") if path]
    forbidden = [str(path) for path in tracked if str(path).startswith(PRIVATE_PREFIXES)
                 or str(path).lower().endswith(PRIVATE_SUFFIXES)
                 or path.name == ".env" or path.name.startswith(".env.") and path.name != ".env.example"]
    oversized = [str(path) for path in tracked if (ROOT / path).exists()
                 and (ROOT / path).stat().st_size > MAX_TRACKED_BYTES]
    assert not forbidden, f"private artifacts tracked: {forbidden}"
    assert not oversized, f"oversized artifacts tracked: {oversized}"
