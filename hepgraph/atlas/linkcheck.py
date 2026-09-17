"""Manual link checker for `data/atlas/sources/*.json` (A18, A22).

This module is **never** run by the build or by the test suite against the
network: it makes outbound HTTP requests, so a human runs it deliberately.

    python -m hepgraph.atlas.linkcheck --only-stale 30 --limit 50

What it does, per source file:

* fetches `url` with a HEAD (falling back to GET when HEAD is refused),
* writes `link_check.last_checked`, `link_check.http_status` and
  `link_check.redirect` back into the file,
* writes a top-level `content_hash` (A18) — the SHA-256 of the fetched body,
  truncated to 16 hex characters — when a body was actually read,
* rewrites the file in the A11 canonical form so the diff stays reviewable.

What it never does (A22): **fail**.  A 5xx, a timeout or a DNS failure is
recorded and reported; the exit status stays 0.  Only a genuine local problem
(no data directory, unwritable file) is an error.  A 404/410 on the sole
source of a `verified` value is printed under "review required" for a human
to act on; the build is not blocked.

Politeness: at least one second between requests, always.  `--delay` may
raise that but never lower it.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Sequence

from . import schema
from .load import DATA_DIR, dump_json, load_atlas

USER_AGENT = 'HEP-Atlas-linkcheck/0.2 (+https://github.com/; contact: atlas maintainers)'
MIN_DELAY_SECONDS = 1.0
DEFAULT_TIMEOUT_SECONDS = 20.0
# A22: these statuses put a source on the "review required" list.
GONE_STATUSES: frozenset[int] = frozenset({404, 410})
CONTENT_HASH_CHARS = 16
MAX_BODY_BYTES = 2_000_000


@dataclass(frozen=True)
class CheckResult:
    """What one fetch found.  `http_status` is None when nothing answered."""

    url: str
    http_status: int | None = None
    redirect: str | None = None
    content_hash: str | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.http_status is not None and 200 <= self.http_status < 400

    @property
    def gone(self) -> bool:
        return self.http_status in GONE_STATUSES


@dataclass
class Report:
    """Everything one run learned, for the printed summary and for tests."""

    checked: list[tuple[str, CheckResult]] = field(default_factory=list)
    skipped: list[tuple[str, str]] = field(default_factory=list)
    written: list[str] = field(default_factory=list)

    @property
    def review_required(self) -> list[tuple[str, CheckResult]]:
        """A22: sources whose URL is gone and therefore need a human."""
        return [(source_id, result) for source_id, result in self.checked if result.gone]

    @property
    def failures(self) -> list[tuple[str, CheckResult]]:
        """Everything that did not answer with a success/redirect status."""
        return [(source_id, result) for source_id, result in self.checked if not result.ok]


# ---------------------------------------------------------------------------
# Selecting what to check
# ---------------------------------------------------------------------------

def last_checked(record: dict) -> _dt.date | None:
    """The `link_check.last_checked` date of a source record, if any."""
    link_check = record.get('link_check')
    if not isinstance(link_check, dict):
        return None
    return schema.as_date(link_check.get('last_checked'))


def is_stale(record: dict, *, days: int, today: _dt.date) -> bool:
    """True when this source has never been checked, or not for `days` days."""
    checked = last_checked(record)
    return checked is None or (today - checked).days >= days


def select_sources(atlas: Any, *, only_stale: int | None = None, limit: int | None = None,
                   today: _dt.date | None = None) -> list[tuple[str, dict]]:
    """The (source id, record) pairs to check, in deterministic id order.

    `only_stale=N` keeps sources never checked or last checked N or more days
    ago; `limit` caps the list so a run stays short and polite.
    """
    today = today or _dt.date.today()
    chosen: list[tuple[str, dict]] = []
    for source_id in sorted(atlas.by_type('source')):
        record = atlas.by_type('source')[source_id]
        if not isinstance(record.get('url'), str) or not record['url'].strip():
            continue
        if only_stale is not None and not is_stale(record, days=only_stale, today=today):
            continue
        chosen.append((source_id, record))
    if limit is not None:
        chosen = chosen[:max(0, limit)]
    return chosen


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------

def check_url(url: str, *, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> CheckResult:
    """Fetch one URL and describe what came back.  Never raises."""
    for method in ('HEAD', 'GET'):
        request = urllib.request.Request(url, method=method, headers={'User-Agent': USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                final_url = response.geturl()
                body = response.read(MAX_BODY_BYTES) if method == 'GET' else b''
                return CheckResult(
                    url=url,
                    http_status=getattr(response, 'status', None) or response.getcode(),
                    redirect=final_url if final_url and final_url != url else None,
                    content_hash=_content_hash(body) if body else None,
                )
        except urllib.error.HTTPError as exc:
            # 405/501 mean "HEAD is not allowed here"; retry once with GET.
            if method == 'HEAD' and exc.code in {405, 501}:
                continue
            return CheckResult(url=url, http_status=exc.code, error=f'HTTP {exc.code} {exc.reason}')
        except (urllib.error.URLError, OSError, ValueError) as exc:
            if method == 'HEAD':
                continue
            return CheckResult(url=url, error=f'{type(exc).__name__}: {exc}')
    return CheckResult(url=url, error='no response')


def _content_hash(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()[:CONTENT_HASH_CHARS]


# ---------------------------------------------------------------------------
# Writing results back
# ---------------------------------------------------------------------------

def apply_result(record: dict, result: CheckResult, *, today: _dt.date) -> bool:
    """Write one CheckResult into a source record.  True when it changed."""
    before = json.dumps(record, sort_keys=True, ensure_ascii=False)
    link_check = dict(record.get('link_check') or {})
    link_check['last_checked'] = today.isoformat()
    link_check['http_status'] = result.http_status
    link_check['redirect'] = result.redirect
    if result.error:
        link_check['error'] = result.error
    else:
        link_check.pop('error', None)
    record['link_check'] = link_check
    if result.content_hash:
        record['content_hash'] = result.content_hash
    return json.dumps(record, sort_keys=True, ensure_ascii=False) != before


def run(data_dir: Path | str = DATA_DIR, *, only_stale: int | None = None,
        limit: int | None = None, delay: float = MIN_DELAY_SECONDS,
        dry_run: bool = False, fetch: Callable[[str], CheckResult] = check_url,
        sleep: Callable[[float], None] = time.sleep,
        today: _dt.date | None = None) -> Report:
    """Check the selected sources and write the results back.

    `fetch` and `sleep` are injectable so the tests can exercise the whole
    pipeline without touching the network or waiting a second per source.
    """
    data_dir = Path(data_dir)
    today = today or _dt.date.today()
    delay = max(MIN_DELAY_SECONDS, float(delay))
    atlas = load_atlas(data_dir)
    report = Report()
    targets = select_sources(atlas, only_stale=only_stale, limit=limit, today=today)
    for index, (source_id, record) in enumerate(targets):
        if record.get('retrieval') in schema.UNCITABLE_RETRIEVALS:
            report.skipped.append((source_id, 'retrieval is "failed"; nothing may cite it'))
            continue
        if index:
            sleep(delay)
        result = fetch(record['url'])
        report.checked.append((source_id, result))
        if dry_run:
            continue
        if apply_result(record, result, today=today):
            path = data_dir / atlas.files[source_id]
            path.write_text(dump_json(_without_private(record)), encoding='utf-8')
            report.written.append(atlas.files[source_id])
    return report


def _without_private(record: dict) -> dict:
    """Drop keys the loader added in memory before writing a file back."""
    return {key: value for key, value in record.items() if not key.startswith('_')}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def format_report(report: Report) -> str:
    lines: list[str] = []
    ok = [pair for pair in report.checked if pair[1].ok]
    lines.append(f'checked {len(report.checked)} source(s): {len(ok)} ok, '
                 f'{len(report.failures)} not ok, {len(report.skipped)} skipped')
    redirects = [(sid, res) for sid, res in report.checked if res.redirect]
    if redirects:
        lines.append('')
        lines.append('redirects:')
        for source_id, result in redirects:
            lines.append(f'  {source_id}: {result.url} -> {result.redirect}')
    if report.failures:
        lines.append('')
        lines.append('failures (never fatal, A22):')
        for source_id, result in report.failures:
            detail = result.error or f'HTTP {result.http_status}'
            lines.append(f'  {source_id}: {detail}')
    if report.review_required:
        lines.append('')
        lines.append('review required (404/410):')
        for source_id, result in report.review_required:
            lines.append(f'  {source_id}: HTTP {result.http_status} {result.url}')
    if report.skipped:
        lines.append('')
        lines.append('skipped:')
        for source_id, reason in report.skipped:
            lines.append(f'  {source_id}: {reason}')
    if report.written:
        lines.append('')
        lines.append(f'updated {len(report.written)} file(s):')
        for path in report.written:
            lines.append(f'  {path}')
    return '\n'.join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='python -m hepgraph.atlas.linkcheck',
        description='Check every source URL and record the result (manual; makes network requests).')
    parser.add_argument('--data', default=str(DATA_DIR), help='atlas data directory')
    parser.add_argument('--limit', type=int, default=None, help='check at most N sources')
    parser.add_argument('--only-stale', type=int, default=None, metavar='DAYS',
                        help='only sources never checked or last checked DAYS or more days ago')
    parser.add_argument('--delay', type=float, default=MIN_DELAY_SECONDS,
                        help=f'seconds between requests (minimum {MIN_DELAY_SECONDS})')
    parser.add_argument('--dry-run', action='store_true', help='fetch but do not write files')
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    data_dir = Path(args.data)
    if not data_dir.is_dir():
        print(f'no such atlas data directory: {data_dir}', file=sys.stderr)
        return 1
    report = run(data_dir, only_stale=args.only_stale, limit=args.limit,
                 delay=args.delay, dry_run=args.dry_run)
    print(format_report(report))
    # A22: link-check failures never fail the run.
    return 0


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
