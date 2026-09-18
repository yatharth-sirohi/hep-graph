#!/usr/bin/env python3
"""Compute the HEP Atlas validation counts from the repository itself.

`docs/HEP_ATLAS_VALIDATION.md` section 8 ("Final validation counts (addendum
section 41)") is the markdown this script prints, between the markers
`<!-- counts:begin -->` / `<!-- counts:end -->`. Nothing in that block is
hand-typed: every deterministic figure (entity counts, source link-check
coverage, the coverage registry, the validator's own findings, the P0/P1/P2
tally in `docs/atlas-worklog/INTEGRATION_ISSUES.md`) is recomputed here on
every run, from the same data the rest of the pipeline reads.

Two families of figures cannot be computed from a source tree alone:

* **Volatile, but machine-checkable** — pytest and browser-test results.
  These require a *run* of the suite, not just a read of the repository, so
  they are accepted as optional external input (`--pytest-log` /
  `--junit-xml`, `--browser-results`) rather than executed as a side effect
  of generating documentation. When not supplied, the report says so plainly
  instead of inventing a number.
* **Requiring a human** — accessibility audits, manual Safari/Firefox runs,
  a source-conflict count, subagent counts. These live in
  `docs/atlas-worklog/validation_counts_manual.json`, one record per field,
  each carrying its own `evidence` pointer. A field whose value is `null`
  renders as "not yet run" so the document never overstates what has
  actually been checked.

Usage:

    python scripts/atlas_validation_counts.py [--check]
        [--pytest-log FILE | --junit-xml FILE]
        [--browser-results DIR]

`--check` regenerates the block with the same inputs and compares it against
the committed copy inside the markers in `docs/HEP_ATLAS_VALIDATION.md`,
ignoring only the "Generated at" timestamp line. It exits 1 when they differ.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from hepgraph.atlas import load, schema, validate as validate_mod  # noqa: E402

DOC = ROOT / 'docs' / 'HEP_ATLAS_VALIDATION.md'
INTEGRATION_ISSUES = ROOT / 'docs' / 'atlas-worklog' / 'INTEGRATION_ISSUES.md'
MANUAL_JSON = ROOT / 'docs' / 'atlas-worklog' / 'validation_counts_manual.json'
BEGIN_MARKER = '<!-- counts:begin -->'
END_MARKER = '<!-- counts:end -->'

ENTITY_LABELS = {
    'facilities': 'Facilities', 'sites': 'Sites', 'accelerators': 'Accelerators',
    'beamlines': 'Beamlines', 'experiments': 'Experiments', 'detectors': 'Detectors',
    'collaborations': 'Collaborations', 'institutions': 'Institutions', 'people': 'People',
    'results': 'Results', 'documents': 'Documents', 'topics': 'Topics', 'sources': 'Sources',
    'memberships': 'Membership rosters', 'coverage': 'Coverage registry rows',
}


# --------------------------------------------------------------------- data

def entity_counts(atlas: load.Atlas) -> dict[str, int]:
    return atlas.counts()


def source_link_check_counts(atlas: load.Atlas) -> tuple[int, int]:
    """(total sources, sources with a recorded link-check status)."""
    sources = atlas.by_type('source')
    checked = 0
    for record in sources.values():
        link_check = record.get('link_check') or {}
        if link_check.get('last_checked') is not None or link_check.get('http_status') is not None:
            checked += 1
    return len(sources), checked


def coverage_tally(atlas: load.Atlas) -> Counter:
    return Counter((row.get('tier') or 'unknown', row.get('researched') or 'unknown')
                   for row in atlas.coverage)


def validator_counts(atlas: load.Atlas) -> Counter:
    findings = validate_mod.validate_atlas(atlas)
    return Counter(f.level for f in findings)


_ROW_RE = re.compile(r'^\|\s*(\d+)\s*\|')


def parse_integration_issues(path: Path) -> list[dict[str, Any]]:
    """Every `| # | Severity | Issue | [Raised by |] State |` row.

    Severity is always the second column and State always the last column
    across every table shape used in this file (checked against all six
    table variants present as of this writing), so the parser does not need
    to know each table's header.
    """
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding='utf-8').splitlines():
        stripped = line.strip()
        if not stripped.startswith('|') or not _ROW_RE.match(stripped):
            continue
        cells = [c.strip() for c in stripped.strip('|').split('|')]
        if len(cells) < 3:
            continue
        severity = cells[1]
        state_raw = cells[-1]
        # Every state in this file is either a bare word/phrase ("open",
        # "sent to pipeline") or "<word>: <explanation>" — splitting only on
        # the colon buckets those correctly without truncating an
        # explanation that happens to contain a comma or parenthesis.
        state = state_raw.split(':')[0].strip().lower()
        rows.append({'id': int(cells[0]), 'severity': severity, 'state': state, 'state_raw': state_raw})
    return rows


def integration_issue_tally(rows: list[dict[str, Any]]) -> Counter:
    return Counter((row['severity'], row['state']) for row in rows)


# ------------------------------------------------------------- volatile IO

def parse_pytest_log(text: str) -> dict[str, int]:
    result: dict[str, int] = {}
    for key, pattern in (
        ('passed', r'(\d+) passed'), ('failed', r'(\d+) failed'),
        ('skipped', r'(\d+) skipped'), ('errors', r'(\d+) error'),
        ('xfailed', r'(\d+) xfailed'),
    ):
        match = re.search(pattern, text)
        if match:
            result[key] = int(match.group(1))
    return result


def parse_junit_xml(path: Path) -> dict[str, int]:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == 'testsuite' else list(root.iter('testsuite'))
    totals = Counter()
    for suite in suites:
        attrs = suite.attrib
        tests = int(attrs.get('tests', 0))
        failures = int(attrs.get('failures', 0))
        errors = int(attrs.get('errors', 0))
        skipped = int(attrs.get('skipped', 0))
        totals['passed'] += tests - failures - errors - skipped
        totals['failed'] += failures
        totals['errors'] += errors
        totals['skipped'] += skipped
    return dict(totals)


def load_browser_results(directory: Path) -> list[dict[str, Any]]:
    if not directory.exists():
        return []
    # A relative --browser-results (as the default value and --help's own
    # usage both show) globs to relative Path objects; relative_to(ROOT)
    # below then raises ValueError unless the input is resolved first,
    # crashing every invocation that doesn't pass an absolute directory.
    directory = directory.resolve()
    reports = []
    for path in sorted(directory.rglob('*.json')):
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            continue
        checks = payload.get('checks') or []
        passed = sum(1 for c in checks if c.get('status') == 'passed')
        reports.append({
            'file': str(path.relative_to(ROOT)),
            'status': payload.get('status', 'unknown'),
            'checks_total': len(checks),
            'checks_passed': passed,
            'uncaught_errors': len(payload.get('uncaught_errors') or []),
            'checked_at': payload.get('checked_at'),
        })
    return reports


def load_manual(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding='utf-8'))


# --------------------------------------------------------------- rendering

def render(*, pytest_counts: dict[str, int] | None, pytest_source: str | None,
           browser_reports: list[dict[str, Any]], browser_dir: Path,
           manual: dict[str, Any], now: dt.datetime) -> str:
    atlas = load.load_atlas()
    counts = entity_counts(atlas)
    total_sources, checked_sources = source_link_check_counts(atlas)
    coverage = coverage_tally(atlas)
    validator = validator_counts(atlas)
    issue_rows = parse_integration_issues(INTEGRATION_ISSUES)
    issue_tally = integration_issue_tally(issue_rows)

    out: list[str] = [BEGIN_MARKER, '']
    out.append('## 8. Final validation counts (addendum §41)')
    out.append('')
    out.append(f'Generated at {now.strftime("%Y-%m-%d")} by `scripts/atlas_validation_counts.py`. '
                'Every figure below is computed directly from the repository at the '
                'moment this ran; nothing here is typed by hand. Run with `--check` to '
                'confirm this block still matches the current data.')
    out.append('')

    out.append('### 8.1 Entities')
    out.append('')
    out.append('| Type | Count |')
    out.append('| --- | ---: |')
    for key in ('facilities', 'sites', 'accelerators', 'beamlines', 'experiments', 'detectors',
                'collaborations', 'institutions', 'people', 'results', 'documents', 'topics',
                'sources', 'memberships', 'coverage'):
        out.append(f'| {ENTITY_LABELS.get(key, key)} | {counts.get(key, 0)} |')
    out.append('')
    pct = f'{checked_sources / total_sources:.0%}' if total_sources else 'n/a'
    out.append(f'Of {total_sources} sources, {checked_sources} ({pct}) carry a recorded '
                'link-check status (`link_check.last_checked` or `link_check.http_status` '
                'is not null); the rest have never been through '
                '`python -m hepgraph.atlas.linkcheck`.')
    out.append('')

    # Result types and link-check outcomes, so the doc's prose never has to
    # carry a typed number for either.
    result_types: dict[str, int] = {}
    for record in atlas.by_type('result').values():
        key = str(record.get('result_type') or 'unknown')
        result_types[key] = result_types.get(key, 0) + 1
    out.append('Results by the type their publication used: '
               + ', '.join(f'{n} {t.replace("_", " ")}' for t, n in sorted(result_types.items(), key=lambda kv: -kv[1]))
               + '.')
    out.append('')
    statuses: dict[str, int] = {}
    for record in atlas.by_type('source').values():
        check = record.get('link_check') or {}
        if check.get('last_checked'):
            code = check.get('http_status')
            statuses[str(code) if code is not None else 'no response'] = statuses.get(str(code) if code is not None else 'no response', 0) + 1
    if statuses:
        out.append('Link-check outcomes by HTTP status: '
                   + ', '.join(f'{n} × {code}' for code, n in sorted(statuses.items(), key=lambda kv: -kv[1])) + '.')
        out.append('')

    out.append('### 8.2 Coverage registry, by tier and researched state')
    out.append('')
    out.append('| Tier | Researched | Rows |')
    out.append('| --- | --- | ---: |')
    for (tier, researched), n in sorted(coverage.items()):
        out.append(f'| {tier} | {researched} | {n} |')
    if not coverage:
        out.append('| — | — | 0 |')
    out.append('')

    out.append('### 8.3 Validator findings (`python -m hepgraph.atlas.validate`)')
    out.append('')
    out.append('| Level | Count |')
    out.append('| --- | ---: |')
    for level in ('error', 'warning', 'info'):
        out.append(f'| {level} | {validator.get(level, 0)} |')
    out.append('')

    out.append('### 8.4 Integration issues (`docs/atlas-worklog/INTEGRATION_ISSUES.md`)')
    out.append('')
    out.append(f'{len(issue_rows)} rows parsed across every severity/state table in that file.')
    out.append('')
    out.append('| Severity | State | Rows |')
    out.append('| --- | --- | ---: |')
    for (severity, state), n in sorted(issue_tally.items()):
        out.append(f'| {severity} | {state} | {n} |')
    if not issue_tally:
        out.append('| — | — | 0 |')
    out.append('')

    out.append('### 8.5 Python test suite')
    out.append('')
    if pytest_counts:
        out.append(f'Source: {pytest_source}.')
        out.append('')
        out.append('| Outcome | Count |')
        out.append('| --- | ---: |')
        for key in ('passed', 'failed', 'errors', 'skipped', 'xfailed'):
            if key in pytest_counts:
                out.append(f'| {key} | {pytest_counts[key]} |')
    else:
        out.append('Not provided this run. Regenerate with `--pytest-log <(pytest -q)` '
                    'or `--junit-xml <path>` to include real counts instead of this notice.')
    out.append('')

    out.append('### 8.6 Browser test results')
    out.append('')
    if browser_reports:
        out.append(f'{len(browser_reports)} result file(s) found under '
                    f'`{browser_dir.relative_to(ROOT) if browser_dir.is_absolute() else browser_dir}`.')
        out.append('')
        out.append('| File | Status | Checks passed | Uncaught errors | Checked at |')
        out.append('| --- | --- | ---: | ---: | --- |')
        for report in browser_reports:
            out.append(f"| {report['file']} | {report['status']} | "
                        f"{report['checks_passed']}/{report['checks_total']} | "
                        f"{report['uncaught_errors']} | {report['checked_at'] or '—'} |")
    else:
        out.append(f'No `*.json` result files found under `{browser_dir}`. Run '
                    '`node tests/browser_atlas.cjs` (and again with `HEP_ATLAS_DATA=generated`) '
                    'first.')
    out.append('')

    out.append('### 8.7 Manual / human-verified fields')
    out.append('')
    out.append('From `docs/atlas-worklog/validation_counts_manual.json` — anything a script '
                'cannot check for itself.')
    out.append('')
    out.append('| Field | Value | Evidence |')
    out.append('| --- | --- | --- |')
    for key in sorted(manual):
        entry = manual[key] or {}
        value = entry.get('value')
        value_text = 'not yet run' if value is None else str(value)
        evidence = entry.get('evidence') or 'not yet run'
        out.append(f'| {key} | {value_text} | {evidence} |')
    if not manual:
        out.append('| — | — | `docs/atlas-worklog/validation_counts_manual.json` not found |')
    out.append('')
    out.append(END_MARKER)
    return '\n'.join(out) + '\n'


def _strip_volatile(text: str) -> str:
    return '\n'.join(line for line in text.splitlines() if not line.startswith('Generated at '))


def extract_committed_block(doc_text: str) -> str | None:
    start = doc_text.find(BEGIN_MARKER)
    end = doc_text.find(END_MARKER)
    if start == -1 or end == -1:
        return None
    return doc_text[start:end + len(END_MARKER)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true',
                        help='compare against the committed block in docs/HEP_ATLAS_VALIDATION.md')
    pytest_group = parser.add_mutually_exclusive_group()
    pytest_group.add_argument('--pytest-log', type=Path, help='a text file with `pytest -q` output')
    pytest_group.add_argument('--junit-xml', type=Path, help='a junit-xml pytest report')
    parser.add_argument('--browser-results', type=Path, default=ROOT / 'test-results' / 'atlas',
                        help='directory to scan for browser_atlas.cjs report.json files')
    args = parser.parse_args(argv)

    def _describe(path: Path, kind: str) -> str:
        try:
            return f'`{path.resolve().relative_to(ROOT)}` ({kind})'
        except ValueError:
            return f'a local {kind} (outside the repository tree, path not recorded)'

    pytest_counts: dict[str, int] | None = None
    pytest_source: str | None = None
    if args.pytest_log:
        pytest_counts = parse_pytest_log(args.pytest_log.read_text(encoding='utf-8'))
        pytest_source = _describe(args.pytest_log, '`pytest -q` log')
    elif args.junit_xml:
        pytest_counts = parse_junit_xml(args.junit_xml)
        pytest_source = _describe(args.junit_xml, 'junit-xml report')

    browser_reports = load_browser_results(args.browser_results)
    manual = load_manual(MANUAL_JSON)
    now = dt.datetime.now(dt.timezone.utc)

    text = render(pytest_counts=pytest_counts, pytest_source=pytest_source,
                  browser_reports=browser_reports, browser_dir=args.browser_results, manual=manual, now=now)

    if args.check:
        doc_text = DOC.read_text(encoding='utf-8') if DOC.exists() else ''
        committed = extract_committed_block(doc_text)
        if committed is None:
            print(f'{DOC.relative_to(ROOT)} has no {BEGIN_MARKER}/{END_MARKER} block')
            return 1
        if _strip_volatile(committed) != _strip_volatile(text):
            print(f'{DOC.relative_to(ROOT)} counts block is out of date; regenerate with '
                  'scripts/atlas_validation_counts.py')
            return 1
        print('validation counts block is current')
        return 0

    print(text)
    return 0


if __name__ == '__main__':  # pragma: no cover - CLI entry point
    raise SystemExit(main())
