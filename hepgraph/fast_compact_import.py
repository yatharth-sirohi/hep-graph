"""Parallel front-end for the compact INSPIRE import.

Measured on the live candidate: one 1,000-record page costs 9.6 s of INSPIRE
response time, 0.6 s of database writes and a 1.0 s self-imposed interval, so a
serial importer spends ~88% of its life waiting on one socket while INSPIRE's
published budget of 15 requests per 5 seconds sits unused.

This runs several shards at once against the *same* tables and checkpoints as
``neon_compact_import``, so the two are interchangeable and either can resume
the other's work.  Every retention and validation rule is reused from that
module rather than restated: a shard is still verified against the upstream
total, pages must still arrive complete, and every record must still fall inside
the shard that claimed it.

Ownership is arbitrated by PostgreSQL advisory locks, one per shard, so workers
never collide and a crashed worker's shard is released by the disconnect rather
than staying claimed.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterable
import os
import sys
import threading
import time
from typing import Any

from .neon_compact_import import (MAX_RESULTS_PER_QUERY, PAGE_SIZE, SCHEMA,
                                  _query, _utcnow, _work_from_hit)
from .pipeline import InspireClient, PipelineError, _hits, _metadata, _upstream_total


#: INSPIRE documents 15 requests per 5 seconds per IP. Stay meaningfully under
#: it: the point is to stop wasting the budget, not to spend all of it.
DEFAULT_RATE = 2.0
DEFAULT_WORKERS = 12

#: Only what ``_work_from_hit`` reads. Dropping author names and affiliations
#: keeps a 3,000-author record from shipping its byline twice over.
COMPACT_FIELDS = ("control_number,titles.title,document_type,author_count,"
                  "authors.record,authors.inspire_roles,earliest_date,deleted")


class RateLimiter:
    """Shared token bucket. Every worker's request passes through one of these."""

    def __init__(self, rate: float) -> None:
        self.interval = 1.0 / rate if rate > 0 else 0.0
        self.lock = threading.Lock()
        self.next_at = 0.0

    def take(self) -> None:
        with self.lock:
            now = time.monotonic()
            wait = max(0.0, self.next_at - now)
            self.next_at = max(now, self.next_at) + self.interval
        if wait > 0:
            time.sleep(wait)


class _PacedClient(InspireClient):
    """An INSPIRE client whose pacing is global instead of per-instance.

    ``InspireClient`` enforces its own one-second gap per object, which is
    exactly the serialisation this module exists to remove; the shared limiter
    replaces it.
    """

    def __init__(self, limiter: RateLimiter) -> None:
        super().__init__()
        self.limiter = limiter

    def fetch(self, collection: str, query: str, page: int, size: int,
              sort: str | None = None) -> dict[str, Any]:
        self.limiter.take()
        self._last_request = time.monotonic() - 10.0  # the shared limiter paces us
        return super().fetch(collection, query, page, size, sort)


class ShardWorker:
    """Claims one shard at a time and drives it to DONE or SPLIT.

    Everything here is corpus-independent: claiming, splitting a range that
    exceeds the 10,000-result window, paging with the completeness and drift
    checks, and checkpointing. A different corpus overrides ``COLLECTION``,
    ``range_query`` and ``persist``.
    """

    COLLECTION = "literature"

    def range_query(self, low: int, high: int) -> str:
        return _query(low, high)

    def __init__(self, connection: Any, client: Any, import_id: str, *,
                 stop: threading.Event, report: Any) -> None:
        self.connection, self.client, self.import_id = connection, client, import_id
        self.stop, self.report = stop, report
        self.pages = 0
        self.records = 0

    # ------------------------------------------------------------------ claim
    def _key(self, low: int, high: int) -> str:
        return f"hepgraph:shard:{self.import_id}:{low}:{high}"

    def _claim(self) -> dict[str, Any] | None:
        """Take the newest unclaimed shard. The lock, not a column, marks it."""
        rows = self.connection.execute(
            "SELECT low_recid,high_recid,status,expected_records,next_page,received_records "
            "FROM inspire_compact_shard WHERE import_id=%s AND status IN ('DISCOVER','PENDING') "
            "ORDER BY high_recid DESC LIMIT 64", (self.import_id,)).fetchall()
        for row in rows:
            row = dict(row)
            taken = self.connection.execute(
                "SELECT pg_try_advisory_lock(hashtext(%s)) AS ok",
                (self._key(row["low_recid"], row["high_recid"]),)).fetchone()
            if not dict(taken)["ok"]:
                continue
            # Re-read under the lock: another worker may have finished it
            # between the list above and the lock being granted.
            fresh = self.connection.execute(
                "SELECT low_recid,high_recid,status,expected_records,next_page,received_records "
                "FROM inspire_compact_shard WHERE import_id=%s AND low_recid=%s AND high_recid=%s",
                (self.import_id, row["low_recid"], row["high_recid"])).fetchone()
            fresh = dict(fresh) if fresh else None
            if fresh and fresh["status"] in {"DISCOVER", "PENDING"}:
                return fresh
            self._release(row["low_recid"], row["high_recid"])
        return None

    def _release(self, low: int, high: int) -> None:
        self.connection.execute("SELECT pg_advisory_unlock(hashtext(%s))", (self._key(low, high),))

    def _executemany(self, query: str, values: Iterable[tuple[Any, ...]]) -> None:
        with self.connection.cursor() as cursor:
            cursor.executemany(query, values)

    # --------------------------------------------------------------- the work
    def _discover(self, shard: dict[str, Any]) -> None:
        low, high = shard["low_recid"], shard["high_recid"]
        count = _upstream_total(self.client.fetch(self.COLLECTION, self.range_query(low, high), 1, 1))
        if count is None:
            raise PipelineError("INSPIRE did not provide an exact shard count")
        with self.connection.transaction():
            if count <= MAX_RESULTS_PER_QUERY:
                self.connection.execute(
                    "UPDATE inspire_compact_shard SET status=%s,expected_records=%s,updated_at=now() "
                    "WHERE import_id=%s AND low_recid=%s AND high_recid=%s",
                    ("DONE" if count == 0 else "PENDING", count, self.import_id, low, high))
            else:
                if low == high:
                    raise PipelineError("single literature ID returned more than one record")
                mid = (low + high) // 2
                self.connection.execute(
                    "UPDATE inspire_compact_shard SET status='SPLIT',expected_records=%s,updated_at=now() "
                    "WHERE import_id=%s AND low_recid=%s AND high_recid=%s",
                    (count, self.import_id, low, high))
                self._executemany(
                    "INSERT INTO inspire_compact_shard(import_id,low_recid,high_recid,status) "
                    "VALUES (%s,%s,%s,'DISCOVER') ON CONFLICT DO NOTHING",
                    ((self.import_id, low, mid), (self.import_id, mid + 1, high)))

    def _load_page(self, shard: dict[str, Any]) -> bool:
        low, high = shard["low_recid"], shard["high_recid"]
        page, expected = shard["next_page"], shard["expected_records"]
        response = self.client.fetch(self.COLLECTION, self.range_query(low, high), page, PAGE_SIZE)
        total, hits = _upstream_total(response), _hits(response)
        if total != expected:
            raise PipelineError(f"INSPIRE shard {low}-{high} changed during import")
        remaining = expected - (page - 1) * PAGE_SIZE
        if len(hits) != min(PAGE_SIZE, remaining):
            raise PipelineError(f"INSPIRE shard {low}-{high} page {page} is incomplete")
        seen: set[int] = set()
        for hit in hits:
            recid, _ = _metadata(hit)
            if not low <= int(recid) <= high or int(recid) in seen:
                raise PipelineError(f"INSPIRE shard {low}-{high} contains an invalid or duplicate ID")
            seen.add(int(recid))
        done = page * PAGE_SIZE >= expected
        with self.connection.transaction():
            primary, secondary = self.persist(hits)
            self.connection.execute(
                "UPDATE inspire_compact_shard SET status=%s,next_page=%s,"
                "received_records=received_records+%s,retained_works=retained_works+%s,"
                "retained_memberships=retained_memberships+%s,updated_at=now() "
                "WHERE import_id=%s AND low_recid=%s AND high_recid=%s",
                ("DONE" if done else "PENDING", page + 1, len(hits), primary,
                 secondary, self.import_id, low, high))
        self.pages += 1
        self.records += len(hits)
        self.report(len(hits))
        shard["next_page"], shard["received_records"] = page + 1, shard["received_records"] + len(hits)
        return done

    def persist(self, hits: list[Any]) -> tuple[int, int]:
        """Store one page. Returns the two counters the shard row tracks."""
        works: list[tuple[Any, ...]] = []
        memberships: list[tuple[Any, ...]] = []
        for hit in hits:
            compact = _work_from_hit(hit)
            if compact is None:
                continue
            work_id, year, author_count, authors, updated = compact
            works.append((self.import_id, work_id, year, author_count, len(authors), updated, _utcnow()))
            memberships.extend((self.import_id, work_id, author_id) for author_id in authors)
        if works:
            self._executemany(
                "INSERT INTO inspire_compact_work(import_id,work_id,year,author_count,"
                "member_count,source_updated_at,retrieved_at) VALUES (%s,%s,%s,%s,%s,%s,%s) "
                "ON CONFLICT (import_id,work_id) DO NOTHING", works)
        if memberships:
            self._executemany(
                "INSERT INTO inspire_compact_membership(import_id,work_id,author_id) "
                "VALUES (%s,%s,%s) ON CONFLICT DO NOTHING", memberships)
        return len(works), len(memberships)

    def run(self) -> None:
        while not self.stop.is_set():
            shard = self._claim()
            if shard is None:
                time.sleep(2.0)
                continue
            low, high = shard["low_recid"], shard["high_recid"]
            try:
                if shard["status"] == "DISCOVER":
                    self._discover(shard)
                else:
                    while not self.stop.is_set() and not self._load_page(shard):
                        pass
            except Exception as exc:
                # One shard's failure is recorded and skipped; the other workers
                # keep going, and `--retry-failed` on either importer resumes it.
                self.connection.execute(
                    "UPDATE inspire_compact_shard SET status='FAILED',failure=%s,updated_at=now() "
                    "WHERE import_id=%s AND low_recid=%s AND high_recid=%s",
                    (str(exc)[:500], self.import_id, low, high))
                print(f"shard {low}-{high} failed: {exc}", file=sys.stderr, flush=True)
            finally:
                self._release(low, high)


def run(url: str, import_id: str, *, workers: int = DEFAULT_WORKERS,
        rate: float = DEFAULT_RATE, minimal_fields: bool = True,
        duration: float | None = None, worker_class: type = None,
        setup: Any = None) -> dict[str, Any]:
    import psycopg

    control = psycopg.connect(url, autocommit=True, row_factory=psycopg.rows.dict_row)
    lock = control.execute("SELECT pg_try_advisory_lock(hashtext(%s)) AS ok",
                           (f"hepgraph:inspire-compact:{import_id}",)).fetchone()
    if not lock["ok"]:
        control.close()
        raise PipelineError("another compact importer already owns this candidate")
    control.execute(SCHEMA)
    if setup is not None:
        setup(control)
    control.execute("UPDATE inspire_compact_import SET status='FETCHING',updated_at=now() "
                    "WHERE import_id=%s", (import_id,))
    # Resume anything a previous run left FAILED, exactly as the serial importer
    # does: committed rows are never discarded to retry a shard.
    control.execute(
        "UPDATE inspire_compact_shard SET status=CASE WHEN expected_records IS NULL THEN 'DISCOVER' "
        "WHEN received_records >= expected_records THEN 'DONE' ELSE 'PENDING' END, "
        "failure=NULL, updated_at=now() WHERE import_id=%s AND status='FAILED'", (import_id,))

    import hepgraph.pipeline as pipeline

    previous_fields = pipeline.LITERATURE_FIELDS
    if minimal_fields:
        pipeline.LITERATURE_FIELDS = COMPACT_FIELDS

    limiter = RateLimiter(rate)
    stop = threading.Event()
    started, counter, counter_lock = time.monotonic(), [0], threading.Lock()

    def report(records: int) -> None:
        with counter_lock:
            counter[0] += records
            total, elapsed = counter[0], time.monotonic() - started
            if total // 10_000 != (total - records) // 10_000:
                print(f"{total:,} records in {elapsed/60:.1f} min "
                      f"({total/max(elapsed,1):.0f}/s)", flush=True)

    connections = []
    threads = []
    try:
        for _ in range(workers):
            connection = psycopg.connect(url, autocommit=True, row_factory=psycopg.rows.dict_row)
            connections.append(connection)
            worker = (worker_class or ShardWorker)(connection, _PacedClient(limiter),
                                                   import_id, stop=stop, report=report)
            thread = threading.Thread(target=worker.run, daemon=True)
            threads.append(thread)
            thread.start()
        while any(thread.is_alive() for thread in threads):
            remaining = control.execute(
                "SELECT count(*) AS n FROM inspire_compact_shard WHERE import_id=%s "
                "AND status IN ('DISCOVER','PENDING')", (import_id,)).fetchone()["n"]
            if remaining == 0:
                break
            if duration is not None and time.monotonic() - started > duration:
                break
            time.sleep(3.0)
    finally:
        stop.set()
        for thread in threads:
            thread.join(timeout=30)
        for connection in connections:
            connection.close()
        elapsed = time.monotonic() - started
        print(f"stopped after {counter[0]:,} records in {elapsed/60:.1f} min "
              f"({counter[0]/max(elapsed,1):.0f}/s)", flush=True)
        pipeline.LITERATURE_FIELDS = previous_fields
        control.execute("SELECT pg_advisory_unlock(hashtext(%s))",
                        (f"hepgraph:inspire-compact:{import_id}",))
        control.close()
    return {"records": counter[0], "seconds": elapsed}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL_UNPOOLED"))
    parser.add_argument("--import-id", default="inspire-20260916")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--rate", type=float, default=DEFAULT_RATE,
                        help="requests per second across all workers")
    parser.add_argument("--duration", type=float, default=None, help="stop after N seconds")
    parser.add_argument("--full-fields", action="store_true",
                        help="request every field the serial importer does")
    args = parser.parse_args(argv)
    if not args.database_url:
        parser.error("a direct Neon database URL is required")
    try:
        run(args.database_url, args.import_id, workers=args.workers, rate=args.rate,
            minimal_fields=not args.full_fields, duration=args.duration)
    except (PipelineError, ValueError) as exc:
        print(f"fast compact import stopped: {exc}", file=sys.stderr, flush=True)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
