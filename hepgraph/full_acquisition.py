"""Manual, resumable INSPIRE source acquisition for an isolated build worker.

This module does *not* produce a production-ready graph.  It proves source
partition accounting and stores only the fields allowlisted by pipeline.py.
Compilation, independent validation, and explicit promotion remain separate.
Never run a full build on a developer laptop or commit its SQLite spool.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from .pipeline import InspireClient, PipelineError, _hits, _upstream_total, sanitize_author, sanitize_literature, utc_now


COLLECTIONS = ("literature", "authors")
MAX_PAGE_SIZE = 1000
SCHEMA = """
CREATE TABLE IF NOT EXISTS acquisition_meta (
    collection TEXT PRIMARY KEY, root_total INTEGER NOT NULL, range_total INTEGER NOT NULL,
    max_recid INTEGER NOT NULL, started_at TEXT NOT NULL, completed_at TEXT
);
CREATE TABLE IF NOT EXISTS acquisition_partition (
    collection TEXT NOT NULL, low_id INTEGER NOT NULL, high_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('DISCOVER', 'SPLIT', 'READY', 'DONE')),
    expected INTEGER, received INTEGER, sha256 TEXT, completed_at TEXT,
    PRIMARY KEY(collection, low_id, high_id)
);
CREATE INDEX IF NOT EXISTS acquisition_pending ON acquisition_partition(collection,status,low_id);
CREATE TABLE IF NOT EXISTS acquisition_record (
    collection TEXT NOT NULL, recid TEXT NOT NULL, partition_low INTEGER NOT NULL,
    payload TEXT NOT NULL, PRIMARY KEY(collection,recid)
);
CREATE INDEX IF NOT EXISTS acquisition_record_partition ON acquisition_record(collection,partition_low);
CREATE TABLE IF NOT EXISTS acquisition_report (
    singleton INTEGER PRIMARY KEY CHECK(singleton=1), payload TEXT NOT NULL
);
"""


def open_acquisition(path: str | Path) -> sqlite3.Connection:
    path = Path(path)
    if path.exists() and not path.is_file():
        raise PipelineError("acquisition destination is not a file")
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    return connection


def _query(collection: str, low: int, high: int) -> str:
    if collection == "literature":
        return f"recid:{low}->{high}"
    return f"control_number:[{low} TO {high}]"


class FullAcquisition:
    """One-page, ID-range shards avoid INSPIRE's 10k result-window cap.

    A partition is committed only after its count, IDs, sanitized payloads,
    and content digest have been checked.  The primary key prevents duplicate
    records across disjoint shards.  A changed upstream count stops the build;
    it never turns a partial crawl into a completeness certificate.
    """

    def __init__(self, connection: sqlite3.Connection, client: InspireClient | Any,
                 *, max_recid: int = 10_000_000, shard_size: int = MAX_PAGE_SIZE) -> None:
        if max_recid < 1 or not 1 <= shard_size <= MAX_PAGE_SIZE:
            raise ValueError("invalid acquisition bounds")
        self.db, self.client = connection, client
        self.max_recid, self.shard_size = max_recid, shard_size

    def _count(self, collection: str, query: str) -> int:
        total = _upstream_total(self.client.fetch(collection, query, 1, 1))
        if total is None:
            raise PipelineError("INSPIRE did not provide an exact hit count")
        return total

    def plan(self) -> dict[str, Any]:
        """Discover all shards, checkpointing each recursive split."""
        for collection in COLLECTIONS:
            existing = self.db.execute(
                "SELECT * FROM acquisition_meta WHERE collection=?", (collection,)).fetchone()
            if existing is None:
                root_total = self._count(collection, "")
                range_total = self._count(collection, _query(collection, 1, self.max_recid))
                if root_total != range_total:
                    raise PipelineError(f"{collection} ID range omits records: {range_total}/{root_total}")
                with self.db:
                    self.db.execute("INSERT INTO acquisition_meta VALUES (?,?,?,?,?,NULL)",
                                    (collection, root_total, range_total, self.max_recid, utc_now()))
                    self.db.execute("INSERT INTO acquisition_partition(collection,low_id,high_id,status) "
                                    "VALUES (?,?,?,'DISCOVER')", (collection, 1, self.max_recid))
            elif existing["max_recid"] != self.max_recid:
                raise PipelineError("cannot change the ID horizon while resuming a build")
            while True:
                row = self.db.execute(
                    "SELECT low_id,high_id FROM acquisition_partition "
                    "WHERE collection=? AND status='DISCOVER' ORDER BY low_id LIMIT 1",
                    (collection,)).fetchone()
                if row is None:
                    break
                low, high = row["low_id"], row["high_id"]
                count = self._count(collection, _query(collection, low, high))
                if count <= self.shard_size:
                    with self.db:
                        self.db.execute("UPDATE acquisition_partition SET status='READY',expected=? "
                                        "WHERE collection=? AND low_id=? AND high_id=?",
                                        (count, collection, low, high))
                    continue
                if low == high:
                    raise PipelineError("single INSPIRE ID returned more than one record")
                middle = (low + high) // 2
                with self.db:
                    self.db.execute("UPDATE acquisition_partition SET status='SPLIT',expected=? "
                                    "WHERE collection=? AND low_id=? AND high_id=?",
                                    (count, collection, low, high))
                    self.db.executemany(
                        "INSERT OR IGNORE INTO acquisition_partition(collection,low_id,high_id,status) "
                        "VALUES (?,?,?,'DISCOVER')",
                        ((collection, low, middle), (collection, middle + 1, high)))
        return self.status()

    def fetch(self, *, max_partitions: int | None = None) -> dict[str, Any]:
        """Fetch ready shards; ``max_partitions`` supports bounded dry runs."""
        if max_partitions is not None and max_partitions < 1:
            raise ValueError("max_partitions must be positive")
        completed = 0
        while max_partitions is None or completed < max_partitions:
            row = self.db.execute(
                "SELECT collection,low_id,high_id,expected FROM acquisition_partition "
                "WHERE status='READY' ORDER BY CASE collection WHEN 'literature' THEN 0 ELSE 1 END,"
                "low_id LIMIT 1").fetchone()
            if row is None:
                break
            collection, low, high, expected = (row[key] for key in
                                               ("collection", "low_id", "high_id", "expected"))
            response = self.client.fetch(collection, _query(collection, low, high), 1,
                                         max(1, expected))
            rows = _hits(response)
            if _upstream_total(response) != expected or len(rows) != expected:
                raise PipelineError(f"{collection} shard {low}-{high} changed during acquisition")
            sanitize = sanitize_literature if collection == "literature" else sanitize_author
            records: list[tuple[str, str, int, str]] = []
            for hit in rows:
                recid, payload = sanitize(hit)
                if not low <= int(recid) <= high:
                    raise PipelineError(f"{collection} returned an ID outside shard {low}-{high}")
                records.append((collection, recid, low, json.dumps(payload, ensure_ascii=False,
                                                                    sort_keys=True, separators=(",", ":"))))
            if len({item[1] for item in records}) != expected:
                raise PipelineError(f"{collection} shard {low}-{high} contains duplicate IDs")
            digest = hashlib.sha256()
            for _, recid, _, payload in sorted(records, key=lambda item: int(item[1])):
                digest.update(f"{recid}\t{payload}\n".encode("utf-8"))
            with self.db:
                self.db.executemany("INSERT INTO acquisition_record VALUES (?,?,?,?)", records)
                self.db.execute("UPDATE acquisition_partition SET status='DONE',received=?,sha256=?,"
                                "completed_at=? WHERE collection=? AND low_id=? AND high_id=?",
                                (len(records), digest.hexdigest(), utc_now(), collection, low, high))
            completed += 1
        return self.status()

    def status(self) -> dict[str, Any]:
        collections: dict[str, Any] = {}
        for collection in COLLECTIONS:
            meta = self.db.execute("SELECT * FROM acquisition_meta WHERE collection=?",
                                   (collection,)).fetchone()
            if meta is None:
                collections[collection] = {"state": "UNPLANNED"}
                continue
            counts = {row[0]: row[1] for row in self.db.execute(
                "SELECT status,COUNT(*) FROM acquisition_partition WHERE collection=? GROUP BY status",
                (collection,))}
            received = self.db.execute(
                "SELECT COUNT(*) FROM acquisition_record WHERE collection=?", (collection,)).fetchone()[0]
            collections[collection] = {"root_total": meta["root_total"], "max_recid": meta["max_recid"],
                                       "partitions": counts, "received": received}
        return collections

    def verify(self) -> dict[str, Any]:
        """Independent re-hash and accounting; never certifies graph semantics."""
        report: dict[str, Any] = {"source_complete": False, "collections": {}}
        for collection in COLLECTIONS:
            meta = self.db.execute("SELECT * FROM acquisition_meta WHERE collection=?",
                                   (collection,)).fetchone()
            if meta is None:
                raise PipelineError(f"{collection} has not been planned")
            pending = self.db.execute("SELECT COUNT(*) FROM acquisition_partition "
                                      "WHERE collection=? AND status IN ('DISCOVER','READY')",
                                      (collection,)).fetchone()[0]
            if pending:
                raise PipelineError(f"{collection} has {pending} incomplete partitions")
            leaves = self.db.execute("SELECT * FROM acquisition_partition WHERE collection=? "
                                     "AND status='DONE' ORDER BY low_id", (collection,)).fetchall()
            if not leaves or leaves[0]["low_id"] != 1 or leaves[-1]["high_id"] != self.max_recid:
                raise PipelineError(f"{collection} partition coverage has gaps")
            for before, after in zip(leaves, leaves[1:]):
                if before["high_id"] + 1 != after["low_id"]:
                    raise PipelineError(f"{collection} partition coverage has gaps or overlaps")
            if sum(row["expected"] for row in leaves) != meta["root_total"]:
                raise PipelineError(f"{collection} partition totals differ from root count")
            for shard in leaves:
                rows = self.db.execute("SELECT recid,payload FROM acquisition_record "
                                       "WHERE collection=? AND partition_low=? ORDER BY CAST(recid AS INTEGER)",
                                       (collection, shard["low_id"])).fetchall()
                digest = hashlib.sha256()
                for row in rows:
                    digest.update(f"{row['recid']}\t{row['payload']}\n".encode("utf-8"))
                if len(rows) != shard["expected"] or digest.hexdigest() != shard["sha256"]:
                    raise PipelineError(f"{collection} shard {shard['low_id']} checksum/count failed")
            actual = self.db.execute("SELECT COUNT(*) FROM acquisition_record WHERE collection=?",
                                     (collection,)).fetchone()[0]
            if actual != meta["root_total"]:
                raise PipelineError(f"{collection} unique ID count differs from root count")
            current_total = self._count(collection, "")
            current_range = self._count(collection, _query(collection, 1, self.max_recid))
            if current_total != meta["root_total"] or current_range != current_total:
                raise PipelineError(f"{collection} upstream count drifted; no cutoff can be certified")
            report["collections"][collection] = {"records": actual, "shards": len(leaves),
                                                  "started_at": meta["started_at"]}
        report["source_complete"] = True
        report["verified_at"] = utc_now()
        with self.db:
            self.db.execute("INSERT INTO acquisition_report(singleton,payload) VALUES (1,?) "
                            "ON CONFLICT(singleton) DO UPDATE SET payload=excluded.payload",
                            (json.dumps(report, sort_keys=True),))
        return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manual INSPIRE source acquisition (isolated worker only)")
    parser.add_argument("command", choices=("build", "plan", "fetch", "status", "verify"))
    parser.add_argument("--spool", required=True, type=Path,
                        help="private SQLite file on ephemeral build storage; never commit")
    parser.add_argument("--max-recid", type=int, default=10_000_000)
    parser.add_argument("--shard-size", type=int, default=MAX_PAGE_SIZE)
    parser.add_argument("--max-partitions", type=int)
    parser.add_argument("--ephemeral-worker", action="store_true",
                        help="acknowledge that this is not a developer laptop")
    args = parser.parse_args(argv)
    if args.command in {"build", "plan", "fetch"} and not args.ephemeral_worker:
        parser.error("full acquisition requires --ephemeral-worker")
    db = open_acquisition(args.spool)
    try:
        runner = FullAcquisition(db, InspireClient(), max_recid=args.max_recid,
                                 shard_size=args.shard_size)
        if args.command in {"build", "plan"}:
            runner.plan()
        if args.command in {"build", "fetch"}:
            runner.fetch(max_partitions=args.max_partitions)
        result = (runner.verify() if args.command == "verify" or
                  (args.command == "build" and args.max_partitions is None) else runner.status())
        print(json.dumps(result, indent=2, sort_keys=True))
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
