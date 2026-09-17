"""Manual, versioned snapshot state and atomic active-pointer operations.

This registry deliberately contains no scheduler, source fetcher or cloud
credentials. A real candidate must be built in private storage and checked by
an independent validator before its report may be submitted here.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import re
import sqlite3
from typing import Any
from uuid import uuid4


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_REQUIRED_GATES = (
    "source_complete", "checksums_match", "identity_passed",
    "work_semantics_passed", "graph_passed", "search_passed",
    "benchmark_passed", "preview_passed",
)
_BUILD_STATES = {"CREATED", "FETCHING", "BUILDING", "VALIDATING"}
_TRANSITIONS = {
    "CREATED": {"FETCHING", "FAILED"},
    "FETCHING": {"BUILDING", "FAILED"},
    "BUILDING": {"VALIDATING", "FAILED"},
    "VALIDATING": {"FAILED"},
    "FAILED": {"FETCHING"},  # resume keeps the same candidate identity
}


class SnapshotStateError(ValueError):
    """An unsafe state change was rejected without changing the active graph."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SnapshotRegistry:
    """Local SQLite control-plane prototype, not the Neon production registry.

    Every search should call ``pin_active`` once, then pass that snapshot ID
    to every graph and evidence query. The pointer is never queried again
    inside a running search, so promotion cannot mix two snapshots.
    """

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS graph_snapshot (
                snapshot_id TEXT PRIMARY KEY,
                schema_version TEXT NOT NULL,
                build_code_commit TEXT NOT NULL,
                created_at TEXT NOT NULL,
                source_cutoff TEXT NOT NULL,
                source_description TEXT NOT NULL,
                status TEXT NOT NULL,
                checksum TEXT,
                validation_report TEXT
            );
            CREATE TABLE IF NOT EXISTS graph_pointer (
                singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                current_snapshot TEXT REFERENCES graph_snapshot(snapshot_id),
                previous_snapshot TEXT REFERENCES graph_snapshot(snapshot_id),
                generation INTEGER NOT NULL DEFAULT 0
            );
            INSERT OR IGNORE INTO graph_pointer(singleton, generation) VALUES (1, 0);
        """)
        self.connection.commit()

    def create_candidate(self, *, schema_version: str, build_code_commit: str,
                         source_cutoff: str, source_description: str) -> str:
        if not all(isinstance(value, str) and value.strip() for value in
                   (schema_version, build_code_commit, source_cutoff, source_description)):
            raise ValueError("snapshot provenance fields must be non-empty")
        cutoff = datetime.fromisoformat(source_cutoff.replace("Z", "+00:00"))
        if cutoff.tzinfo is None or cutoff.astimezone(timezone.utc) > datetime.now(timezone.utc):
            raise ValueError("source_cutoff must be timezone-aware and not in the future")
        snapshot_id = uuid4().hex
        with self.connection:
            self.connection.execute(
                "INSERT INTO graph_snapshot(snapshot_id,schema_version,build_code_commit,created_at,"
                "source_cutoff,source_description,status) VALUES (?,?,?,?,?,?,?)",
                (snapshot_id, schema_version, build_code_commit, _now(),
                 source_cutoff, source_description, "CREATED"))
        return snapshot_id

    def _row(self, snapshot_id: str) -> sqlite3.Row:
        self.connection.row_factory = sqlite3.Row
        row = self.connection.execute("SELECT * FROM graph_snapshot WHERE snapshot_id=?",
                                      (snapshot_id,)).fetchone()
        if row is None:
            raise SnapshotStateError("unknown snapshot")
        return row

    def state(self, snapshot_id: str) -> str:
        return str(self._row(snapshot_id)["status"])

    def advance(self, snapshot_id: str, status: str) -> None:
        if status not in {"FETCHING", "BUILDING", "VALIDATING", "FAILED"}:
            raise SnapshotStateError("state requires a dedicated lifecycle operation")
        with self.connection:
            old = self.state(snapshot_id)
            if status not in _TRANSITIONS.get(old, set()):
                raise SnapshotStateError(f"cannot change {old} to {status}")
            self.connection.execute("UPDATE graph_snapshot SET status=? WHERE snapshot_id=?",
                                    (status, snapshot_id))

    def mark_ready(self, snapshot_id: str, *, checksum: str,
                   validation_report: dict[str, Any]) -> None:
        """Accept only a complete external validator report; never auto-promote."""
        if not isinstance(checksum, str) or _SHA256.fullmatch(checksum) is None:
            raise SnapshotStateError("a SHA-256 checksum is required")
        if not isinstance(validation_report, dict) or any(
                validation_report.get(gate) is not True for gate in _REQUIRED_GATES):
            raise SnapshotStateError("all independent validation gates must pass")
        with self.connection:
            if self.state(snapshot_id) != "VALIDATING":
                raise SnapshotStateError("only a validating candidate may become ready")
            self.connection.execute(
                "UPDATE graph_snapshot SET status='READY', checksum=?, validation_report=? "
                "WHERE snapshot_id=?",
                (checksum, json.dumps(validation_report, sort_keys=True), snapshot_id))

    def pin_active(self) -> tuple[str | None, int]:
        row = self.connection.execute(
            "SELECT current_snapshot,generation FROM graph_pointer WHERE singleton=1").fetchone()
        return (row[0], row[1])

    def promote(self, snapshot_id: str) -> None:
        """One transaction switches A→B; A remains the rollback target."""
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            if self.state(snapshot_id) != "READY":
                raise SnapshotStateError("only a validated READY snapshot may be promoted")
            current, _ = self.pin_active()
            if current is not None:
                self.connection.execute(
                    "UPDATE graph_snapshot SET status='SUPERSEDED' WHERE snapshot_id=? AND status='ACTIVE'",
                    (current,))
            self.connection.execute("UPDATE graph_snapshot SET status='ACTIVE' WHERE snapshot_id=?",
                                    (snapshot_id,))
            self.connection.execute(
                "UPDATE graph_pointer SET current_snapshot=?,previous_snapshot=?,generation=generation+1 "
                "WHERE singleton=1", (snapshot_id, current))

    def rollback(self) -> str:
        """Restore the prior known-good version in one transaction, no rebuild."""
        with self.connection:
            self.connection.execute("BEGIN IMMEDIATE")
            row = self.connection.execute(
                "SELECT current_snapshot,previous_snapshot FROM graph_pointer WHERE singleton=1").fetchone()
            current, previous = row[0], row[1]
            if current is None or previous is None or self.state(previous) != "SUPERSEDED":
                raise SnapshotStateError("no previous known-good snapshot is available")
            self.connection.execute("UPDATE graph_snapshot SET status='SUPERSEDED' WHERE snapshot_id=?",
                                    (current,))
            self.connection.execute("UPDATE graph_snapshot SET status='ACTIVE' WHERE snapshot_id=?",
                                    (previous,))
            self.connection.execute(
                "UPDATE graph_pointer SET current_snapshot=?,previous_snapshot=NULL,generation=generation+1 "
                "WHERE singleton=1", (previous,))
            return previous

    def status(self) -> dict[str, Any]:
        current, generation = self.pin_active()
        pointer = self.connection.execute(
            "SELECT previous_snapshot FROM graph_pointer WHERE singleton=1").fetchone()
        if current is None:
            return {"graph_status": "unavailable", "snapshot": None, "generation": generation}
        row = self._row(current)
        cutoff = datetime.fromisoformat(row["source_cutoff"].replace("Z", "+00:00"))
        return {
            "graph_status": "ok", "snapshot": current,
            "source_cutoff": row["source_cutoff"], "built_at": row["created_at"],
            "age_days": max(0, (datetime.now(timezone.utc) - cutoff.astimezone(timezone.utc)).days),
            "schema_version": row["schema_version"], "validation_status": row["status"],
            "previous_snapshot": pointer[0], "generation": generation,
        }
