"""Smoke test for scripts/atlas_validation_counts.py.

`--check` is deliberately not exercised here: it compares against the browser
test result files under `test-results/atlas/` (gitignored, produced by
`node tests/browser_atlas.cjs`), so its outcome depends on whether those
files happen to exist locally — exactly the kind of order-dependent,
environment-dependent test this suite avoids. `--check` is exercised
manually / in CI as documented in docs/HEP_ATLAS_VALIDATION.md's
"Reproducing this" section, the same way scripts/atlas_coverage_report.py's
`--check` is not part of this suite either. This test only asserts the
generator itself runs cleanly against the real data tree and produces the
markdown section it promises.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / 'scripts' / 'atlas_validation_counts.py'


def test_generates_a_report_and_exits_zero():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True, text=True, cwd=ROOT, timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert '## 8. Final validation counts (addendum §41)' in result.stdout
    assert '<!-- counts:begin -->' in result.stdout
    assert '<!-- counts:end -->' in result.stdout
    assert '### 8.1 Entities' in result.stdout
    assert '### 8.7 Manual / human-verified fields' in result.stdout
