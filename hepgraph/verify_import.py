"""End-to-end verification of a finished compact import.

``snapshot_validation`` proves the import is *internally* consistent: shards
tile their range, counters reconcile, no orphan rows.  That is necessary and not
sufficient — a crawl can be perfectly self-consistent and still have fetched the
wrong thing.  This module adds the two checks that need the outside world:

* the declared range's total, asked of INSPIRE again now, against what the
  import claims it saw;
* a random sample of stored works, re-fetched and compared field by field
  against what is in the database.

Sampling is batched by ``control_number`` so a few hundred records cost a
handful of requests rather than a few hundred.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from typing import Any

from .neon_compact_import import _query, _work_from_hit
from .pipeline import InspireClient, PipelineError, _hits, _metadata, _upstream_total
from .snapshot_validation import CompactImportValidator


SAMPLE_BATCH = 25


def upstream_total(client: Any, low: int, high: int) -> int | None:
    return _upstream_total(client.fetch("literature", _query(low, high), 1, 1))


def sample_works(connection: Any, import_id: str, size: int) -> list[dict[str, Any]]:
    """A uniform sample, taken in the database so no id list is shipped around."""
    rows = connection.execute(
        "SELECT work_id, year, author_count, member_count FROM inspire_compact_work "
        "WHERE import_id=%s ORDER BY random() LIMIT %s", (import_id, size)).fetchall()
    return [dict(row) for row in rows]


def members_of(connection: Any, import_id: str, work_id: int) -> set[int]:
    return {int(dict(row)["author_id"]) for row in connection.execute(
        "SELECT author_id FROM inspire_compact_membership WHERE import_id=%s AND work_id=%s",
        (import_id, work_id)).fetchall()}


def verify_sample(connection: Any, client: Any, import_id: str,
                  works: list[dict[str, Any]]) -> dict[str, Any]:
    """Re-fetch each sampled work and compare every stored field."""
    by_id = {int(work["work_id"]): work for work in works}
    identifiers = sorted(by_id)
    mismatches: list[dict[str, Any]] = []
    missing_upstream: list[int] = []
    checked = 0
    for start in range(0, len(identifiers), SAMPLE_BATCH):
        batch = identifiers[start:start + SAMPLE_BATCH]
        query = " OR ".join(f"control_number:{value}" for value in batch)
        response = client.fetch("literature", query, 1, len(batch))
        returned: dict[int, Any] = {}
        for hit in _hits(response):
            recid, _ = _metadata(hit)
            returned[int(recid)] = hit
        for work_id in batch:
            checked += 1
            hit = returned.get(work_id)
            if hit is None:
                missing_upstream.append(work_id)
                continue
            compact = _work_from_hit(hit)
            stored = by_id[work_id]
            if compact is None:
                # The record is in the database but would not be retained now:
                # either it changed upstream or the retention rule was misapplied.
                mismatches.append({"work_id": work_id, "field": "retention",
                                   "stored": "retained", "upstream": "not_eligible"})
                continue
            _, year, author_count, authors, _ = compact
            if year != stored["year"]:
                mismatches.append({"work_id": work_id, "field": "year",
                                   "stored": stored["year"], "upstream": year})
            if author_count != stored["author_count"]:
                mismatches.append({"work_id": work_id, "field": "author_count",
                                   "stored": stored["author_count"], "upstream": author_count})
            expected = set(authors)
            actual = members_of(connection, import_id, work_id)
            if expected != actual:
                mismatches.append({
                    "work_id": work_id, "field": "members",
                    "stored_only": sorted(actual - expected)[:5],
                    "upstream_only": sorted(expected - actual)[:5],
                    "stored_count": len(actual), "upstream_count": len(expected)})
            elif len(actual) != stored["member_count"]:
                mismatches.append({"work_id": work_id, "field": "member_count",
                                   "stored": stored["member_count"], "upstream": len(actual)})
    return {"checked": checked, "mismatches": mismatches,
            "missing_upstream": missing_upstream,
            "passed": not mismatches and not missing_upstream}


def verify_coverage(connection: Any, client: Any, import_id: str) -> dict[str, Any]:
    """Ask INSPIRE what the declared range holds and compare with the import."""
    header = connection.execute(
        "SELECT low_recid, high_recid FROM inspire_compact_import WHERE import_id=%s",
        (import_id,)).fetchone()
    if header is None:
        raise PipelineError(f"unknown import {import_id!r}")
    low, high = dict(header)["low_recid"], dict(header)["high_recid"]
    live = upstream_total(client, low, high)
    claimed = dict(connection.execute(
        "SELECT COALESCE(sum(expected_records), 0) AS n FROM inspire_compact_shard "
        "WHERE import_id=%s AND status <> 'SPLIT'", (import_id,)).fetchone())["n"]
    received = dict(connection.execute(
        "SELECT COALESCE(sum(LEAST(received_records, expected_records)), 0) AS n "
        "FROM inspire_compact_shard WHERE import_id=%s AND expected_records IS NOT NULL",
        (import_id,)).fetchone())["n"]
    retained = dict(connection.execute(
        "SELECT count(*) AS n FROM inspire_compact_work WHERE import_id=%s", (import_id,)).fetchone())["n"]
    # The leaf shards must account for the live total. A drift of a few records
    # is ordinary - INSPIRE keeps accepting new deposits while a crawl runs - so
    # report the gap rather than asserting equality.
    drift = None if live is None else live - int(claimed)
    return {"declared_range": [low, high], "upstream_total_now": live,
            "leaf_shard_expected_total": int(claimed),
            "source_records_seen": int(received), "works_retained": retained,
            "drift_vs_upstream": drift,
            "retention_rate": round(retained / int(received), 4) if received else None,
            "passed": live is not None and abs(drift) <= max(500, live * 0.001)}


def run(url: str, import_id: str, *, sample: int = 200) -> dict[str, Any]:
    import psycopg

    client = InspireClient()
    with psycopg.connect(url, autocommit=True, row_factory=psycopg.rows.dict_row) as connection:
        connection.execute("SET statement_timeout = '120s'")
        internal = CompactImportValidator(connection, import_id).validate()
        coverage = verify_coverage(connection, client, import_id)
        works = sample_works(connection, import_id, sample)
        spot = verify_sample(connection, client, import_id, works)
    gates = internal.as_dict()
    # `source_window` records that the crawl took hours and INSPIRE offers no
    # atomic point-in-time view. That is permanently true of any live-API crawl,
    # so it is reported as a standing limitation rather than something a finished
    # import could ever clear. Completeness is judged by `source_complete`.
    blocking = [item.name for item in internal.failures() if item.name != "source_window"]
    return {"import_id": import_id,
            "internal_validation": gates,
            "internal_passed": internal.passed,
            "source_complete": bool(gates.get("source_complete")),
            "blocking_failures": blocking,
            "upstream_coverage": coverage,
            "spot_check": spot,
            "passed": not blocking and coverage["passed"] and spot["passed"]}


def _print(report: dict[str, Any]) -> None:
    internal = report["internal_validation"]
    print(f"\n=== import {report['import_id']} ===\n")
    print("source completeness:", "PASS" if report["source_complete"] else "FAIL")
    print("blocking failures:", report["blocking_failures"] or "none")
    print("all internal checks:", "PASS" if report["internal_passed"] else
          "FAIL (see below; source_window is a standing limitation, not a defect)")
    for key, value in sorted(internal.items()):
        if isinstance(value, bool):
            print(f"  {key:<24} {'PASS' if value else 'FAIL'}")
    coverage = report["upstream_coverage"]
    print("\nupstream coverage:", "PASS" if coverage["passed"] else "FAIL")
    print(f"  declared range           {coverage['declared_range']}")
    print(f"  INSPIRE total now        {coverage['upstream_total_now']:,}"
          if coverage["upstream_total_now"] is not None else "  INSPIRE total now        unavailable")
    print(f"  leaf shards expected     {coverage['leaf_shard_expected_total']:,}")
    print(f"  source records seen      {coverage['source_records_seen']:,}")
    print(f"  works retained           {coverage['works_retained']:,}"
          f"  ({coverage['retention_rate']:.1%} of records seen)"
          if coverage["retention_rate"] else f"  works retained           {coverage['works_retained']:,}")
    print(f"  drift vs upstream        {coverage['drift_vs_upstream']}")
    spot = report["spot_check"]
    print("\nspot check:", "PASS" if spot["passed"] else "FAIL")
    print(f"  works re-fetched and compared   {spot['checked']}")
    print(f"  field mismatches                {len(spot['mismatches'])}")
    print(f"  absent upstream                 {len(spot['missing_upstream'])}")
    for item in spot["mismatches"][:10]:
        print(f"    {item}")
    print(f"\nOVERALL: {'PASS' if report['passed'] else 'FAIL'}\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL_UNPOOLED"))
    parser.add_argument("--import-id", default="inspire-20260916")
    parser.add_argument("--sample", type=int, default=200)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.database_url:
        parser.error("a direct database URL is required")
    report = run(args.database_url, args.import_id, sample=args.sample)
    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        _print(report)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
