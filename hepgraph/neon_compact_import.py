"""Resumable compact INSPIRE importer for an isolated Neon candidate branch.

The importer retains collaboration topology only: resolved INSPIRE author IDs,
literature IDs, true author counts, and years. It deliberately never writes
titles, abstracts, email addresses, affiliations, or author profiles to Neon.
It is a source-stage candidate and cannot be promoted or used for exact claims
until the separate compiler and independent validator pass.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterable
from datetime import UTC, datetime
import os
import re
import sys
from typing import Any

from .pipeline import (InspireClient, PipelineError, _hits, _metadata,
                       _upstream_total, ref_id)


MAX_RESULTS_PER_QUERY = 10_000
PAGE_SIZE = 1_000
_CORRECTION_TITLE = re.compile(r"^\s*(?:erratum|errata|corrigendum)(?=$|\W)", re.I)
_ALLOWED_TYPES = {"article", "conference paper"}
_EXCLUDED_TYPES = {"thesis", "book", "book chapter", "proceedings"}

SCHEMA = """
CREATE TABLE IF NOT EXISTS inspire_compact_import (
    import_id TEXT PRIMARY KEY,
    source_cutoff TIMESTAMPTZ NOT NULL,
    low_recid BIGINT NOT NULL,
    high_recid BIGINT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('FETCHING','PAUSED','FAILED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS inspire_compact_shard (
    import_id TEXT NOT NULL REFERENCES inspire_compact_import(import_id),
    low_recid BIGINT NOT NULL,
    high_recid BIGINT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('DISCOVER','PENDING','SPLIT','DONE','FAILED')),
    expected_records INTEGER,
    next_page INTEGER NOT NULL DEFAULT 1,
    received_records INTEGER NOT NULL DEFAULT 0,
    retained_works INTEGER NOT NULL DEFAULT 0,
    retained_memberships INTEGER NOT NULL DEFAULT 0,
    failure TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY(import_id, low_recid, high_recid)
);
CREATE INDEX IF NOT EXISTS inspire_compact_shard_pending
    ON inspire_compact_shard(import_id, status, high_recid DESC, low_recid DESC);
CREATE TABLE IF NOT EXISTS inspire_compact_work (
    import_id TEXT NOT NULL REFERENCES inspire_compact_import(import_id),
    work_id BIGINT NOT NULL,
    year SMALLINT,
    author_count INTEGER NOT NULL CHECK (author_count >= 0),
    member_count INTEGER NOT NULL CHECK (member_count >= 2),
    source_updated_at TEXT,
    retrieved_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY(import_id, work_id)
);
CREATE TABLE IF NOT EXISTS inspire_compact_membership (
    import_id TEXT NOT NULL,
    work_id BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    PRIMARY KEY(import_id, work_id, author_id),
    FOREIGN KEY(import_id, work_id)
        REFERENCES inspire_compact_work(import_id, work_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS inspire_compact_author_work
    ON inspire_compact_membership(import_id, author_id, work_id);
"""


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _query(low: int, high: int) -> str:
    return f"recid:{low}->{high}"


def _work_from_hit(hit: dict[str, Any]) -> tuple[int, int | None, int, tuple[int, ...], str | None] | None:
    """Return only fields required for graph topology, or no qualifying work."""
    recid, metadata = _metadata(hit)
    if metadata.get("deleted") is True:
        return None
    titles = metadata.get("titles", [])
    if not isinstance(titles, list):
        return None
    if any(isinstance(title, dict) and isinstance(title.get("title"), str)
           and _CORRECTION_TITLE.match(title["title"]) for title in titles):
        return None
    types = metadata.get("document_type", [])
    if not isinstance(types, list):
        return None
    type_set = {str(item).strip().lower() for item in types}
    if not type_set.intersection(_ALLOWED_TYPES) or type_set.intersection(_EXCLUDED_TYPES):
        return None
    author_count = metadata.get("author_count")
    if isinstance(author_count, bool) or not isinstance(author_count, int) or author_count < 2:
        return None
    authors = metadata.get("authors", [])
    if not isinstance(authors, list):
        return None
    members: set[int] = set()
    for author in authors:
        if not isinstance(author, dict):
            continue
        roles = author.get("inspire_roles", [])
        if isinstance(roles, list) and roles and "author" not in {str(role).lower() for role in roles}:
            continue
        author_id = ref_id(author.get("record"))
        if author_id is not None:
            members.add(int(author_id))
    if len(members) < 2:
        return None
    earliest = metadata.get("earliest_date")
    year = int(earliest[:4]) if isinstance(earliest, str) and re.fullmatch(r"\d{4}(?:-\d{2}(?:-\d{2})?)?", earliest) else None
    updated = hit.get("updated") if isinstance(hit.get("updated"), str) else None
    return int(recid), year, author_count, tuple(sorted(members)), updated


class NeonCompactImporter:
    """A page-at-a-time direct loader that fails closed on source drift.

    Range discovery is persisted in the candidate database. Queries wider than
    INSPIRE's 10k window are split recursively; valid leaf ranges are paged.
    Work and membership rows commit atomically with their page checkpoint.
    """

    def __init__(self, connection: Any, client: InspireClient | Any, *, import_id: str,
                 low_recid: int = 1, high_recid: int = 3_000_000) -> None:
        if not import_id or low_recid < 1 or high_recid < low_recid:
            raise ValueError("invalid import identity or range")
        self.connection, self.client = connection, client
        self.import_id, self.low_recid, self.high_recid = import_id, low_recid, high_recid

    def ensure_schema(self) -> None:
        with self.connection.transaction():
            self.connection.execute(SCHEMA)
            row = self.connection.execute(
                "SELECT low_recid,high_recid FROM inspire_compact_import WHERE import_id=%s",
                (self.import_id,)).fetchone()
            if row is None:
                self.connection.execute(
                    "INSERT INTO inspire_compact_import(import_id,source_cutoff,low_recid,high_recid,status) "
                    "VALUES (%s,%s,%s,%s,'FETCHING')",
                    (self.import_id, _utcnow(), self.low_recid, self.high_recid))
                self.connection.execute(
                    "INSERT INTO inspire_compact_shard(import_id,low_recid,high_recid,status) "
                    "VALUES (%s,%s,%s,'DISCOVER')", (self.import_id, self.low_recid, self.high_recid))
            elif (row["low_recid"], row["high_recid"]) != (self.low_recid, self.high_recid):
                raise PipelineError("cannot change the range for an existing compact import")
            else:
                self.connection.execute("UPDATE inspire_compact_import SET status='FETCHING',updated_at=now() "
                                        "WHERE import_id=%s", (self.import_id,))

    def _executemany(self, query: str, values: Iterable[tuple[Any, ...]]) -> None:
        """Psycopg 3 exposes batch writes from a cursor, not Connection."""
        with self.connection.cursor() as cursor:
            cursor.executemany(query, values)

    def _next_shard(self) -> Any | None:
        return self.connection.execute(
            "SELECT * FROM inspire_compact_shard WHERE import_id=%s "
            "AND status IN ('DISCOVER','PENDING') "
            "ORDER BY high_recid DESC,low_recid DESC LIMIT 1", (self.import_id,)).fetchone()

    def retry_failed_checkpoints(self) -> int:
        """Resume failed source pages without deleting already committed rows."""
        with self.connection.transaction():
            rows = self.connection.execute(
                "SELECT * FROM inspire_compact_shard WHERE import_id=%s AND status='FAILED' "
                "FOR UPDATE", (self.import_id,)).fetchall()
            for row in rows:
                # A failure before discovery has no expected count. A failure
                # while paging resumes at next_page; completed source rows are
                # never removed or refetched as a condition of retrying.
                state = ("DISCOVER" if row["expected_records"] is None else
                         "DONE" if row["received_records"] >= row["expected_records"] else "PENDING")
                self.connection.execute(
                    "UPDATE inspire_compact_shard SET status=%s,failure=NULL,updated_at=now() "
                    "WHERE import_id=%s AND low_recid=%s AND high_recid=%s",
                    (state, self.import_id, row["low_recid"], row["high_recid"]))
            if rows:
                self.connection.execute("UPDATE inspire_compact_import SET status='FETCHING',updated_at=now() "
                                        "WHERE import_id=%s", (self.import_id,))
        return len(rows)

    def _discover(self, shard: Any) -> None:
        low, high = shard["low_recid"], shard["high_recid"]
        response = self.client.fetch("literature", _query(low, high), 1, 1)
        count = _upstream_total(response)
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

    def _load_page(self, shard: Any) -> None:
        low, high, page, expected = (shard[key] for key in
                                     ("low_recid", "high_recid", "next_page", "expected_records"))
        response = self.client.fetch("literature", _query(low, high), page, PAGE_SIZE)
        total, hits = _upstream_total(response), _hits(response)
        if total != expected:
            raise PipelineError(f"INSPIRE shard {low}-{high} changed during import")
        remaining = expected - (page - 1) * PAGE_SIZE
        expected_page = min(PAGE_SIZE, remaining)
        if len(hits) != expected_page:
            raise PipelineError(f"INSPIRE shard {low}-{high} page {page} is incomplete")
        works: list[tuple[Any, ...]] = []
        memberships: list[tuple[Any, ...]] = []
        seen_ids: set[int] = set()
        for hit in hits:
            compact = _work_from_hit(hit)
            # Every source record must stay inside its claimed shard, even
            # skipped records. This closes a bad pagination/mixed-query hole.
            recid, _ = _metadata(hit)
            if not low <= int(recid) <= high or int(recid) in seen_ids:
                raise PipelineError(f"INSPIRE shard {low}-{high} contains an invalid or duplicate ID")
            seen_ids.add(int(recid))
            if compact is None:
                continue
            work_id, year, author_count, authors, updated = compact
            works.append((self.import_id, work_id, year, author_count, len(authors), updated, _utcnow()))
            memberships.extend((self.import_id, work_id, author_id) for author_id in authors)
        done = page * PAGE_SIZE >= expected
        with self.connection.transaction():
            if works:
                self._executemany(
                    "INSERT INTO inspire_compact_work(import_id,work_id,year,author_count,member_count,source_updated_at,retrieved_at) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (import_id,work_id) DO NOTHING", works)
            if memberships:
                self._executemany(
                    "INSERT INTO inspire_compact_membership(import_id,work_id,author_id) VALUES (%s,%s,%s) "
                    "ON CONFLICT DO NOTHING", memberships)
            self.connection.execute(
                "UPDATE inspire_compact_shard SET status=%s,next_page=%s,received_records=received_records+%s,"
                "retained_works=retained_works+%s,retained_memberships=retained_memberships+%s,updated_at=now() "
                "WHERE import_id=%s AND low_recid=%s AND high_recid=%s",
                ("DONE" if done else "PENDING", page + 1, len(hits), len(works), len(memberships),
                 self.import_id, low, high))

    def run(self, *, max_requests: int, retry_failed: bool = False) -> dict[str, Any]:
        if max_requests < 1:
            raise ValueError("max_requests must be positive")
        lock = self.connection.execute(
            "SELECT pg_try_advisory_lock(hashtext(%s)) AS acquired",
            (f"hepgraph:inspire-compact:{self.import_id}",)).fetchone()
        if not lock["acquired"]:
            raise PipelineError("another compact importer already owns this candidate")
        try:
            self.ensure_schema()
            if retry_failed:
                self.retry_failed_checkpoints()
            requests = 0
            while requests < max_requests:
                shard = self._next_shard()
                if shard is None:
                    break
                if shard["status"] == "DISCOVER":
                    self._discover(shard)
                else:
                    self._load_page(shard)
                requests += 1
        except Exception as exc:
            # Preserve the current PENDING/DISCOVER page for an explicit
            # resume. Disk quota and upstream failures must not erase the
            # only useful checkpoint by incorrectly calling it complete.
            with self.connection.transaction():
                self.connection.execute("UPDATE inspire_compact_import SET status='PAUSED',updated_at=now() "
                                        "WHERE import_id=%s", (self.import_id,))
            raise
        finally:
            # This is a session lock; closing the direct connection also
            # releases it, but explicit unlock makes a normal completion clear.
            self.connection.execute("SELECT pg_advisory_unlock(hashtext(%s))",
                                    (f"hepgraph:inspire-compact:{self.import_id}",))
        return self.status(requests=requests)

    def status(self, *, requests: int = 0) -> dict[str, Any]:
        rows = self.connection.execute(
            "SELECT status,COUNT(*) AS count FROM inspire_compact_shard WHERE import_id=%s GROUP BY status",
            (self.import_id,)).fetchall()
        counts = {row["status"]: row["count"] for row in rows}
        # Shard counters are checkpoints, not the source of truth for graph
        # cardinality. A stopped process can be retried after a successful
        # page commit, so primary-key deduplication may make the table row
        # count smaller than the historical "retained" attempt counter.
        # Clamp source progress to a shard's known upstream total and report
        # persisted graph rows directly so the operator never mistakes retry
        # attempts for imported topology.
        source = self.connection.execute(
            "SELECT COALESCE(SUM(CASE WHEN expected_records IS NULL THEN 0 "
            "ELSE LEAST(received_records, expected_records) END),0) AS source_records_seen "
            "FROM inspire_compact_shard WHERE import_id=%s",
            (self.import_id,)).fetchone()
        stored = self.connection.execute(
            "SELECT "
            "(SELECT COUNT(*) FROM inspire_compact_work WHERE import_id=%s) AS works_retained,"
            "(SELECT COUNT(*) FROM inspire_compact_membership WHERE import_id=%s) AS memberships_retained",
            (self.import_id, self.import_id)).fetchone()
        return {"import_id": self.import_id, "requests_this_run": requests,
                "shards": counts, "source_records_seen": source["source_records_seen"],
                "works_retained": stored["works_retained"],
                "memberships_retained": stored["memberships_retained"]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL_UNPOOLED"),
                        help="direct Neon URL; defaults to DATABASE_URL_UNPOOLED")
    parser.add_argument("--import-id", default="inspire-20260916")
    parser.add_argument("--low-recid", type=int, default=1)
    parser.add_argument("--high-recid", type=int, default=3_000_000)
    parser.add_argument("--max-requests", type=int, default=100)
    parser.add_argument("--retry-failed", action="store_true",
                        help="resume failed checkpoints without deleting committed graph rows")
    parser.add_argument("--status", action="store_true",
                        help="read candidate import counters without fetching or writing")
    args = parser.parse_args(argv)
    if not args.database_url:
        parser.error("a direct Neon database URL is required")
    import psycopg
    connection = psycopg.connect(args.database_url, autocommit=True, row_factory=psycopg.rows.dict_row)
    try:
        importer = NeonCompactImporter(connection, InspireClient(), import_id=args.import_id,
                                       low_recid=args.low_recid, high_recid=args.high_recid)
        result = importer.status() if args.status else importer.run(
            max_requests=args.max_requests, retry_failed=args.retry_failed)
        print(result, flush=True)
    except (PipelineError, ValueError) as exc:
        print(f"compact import stopped: {exc}", file=sys.stderr, flush=True)
        return 2
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
