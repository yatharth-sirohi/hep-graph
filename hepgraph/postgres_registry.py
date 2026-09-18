"""Neon-compatible manual snapshot control plane.

This module owns only candidate state and the active pointer. It does not
claim source completeness, write graph rows, or create cloud resources.
The caller supplies an autocommit Psycopg 3 connection; each mutation uses
one explicit transaction and row locks to serialize competing publishers.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any
from uuid import uuid4

from .snapshot_registry import SnapshotStateError


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_REQUIRED_GATES = (
    "source_complete", "checksums_match", "identity_passed",
    "work_semantics_passed", "graph_passed", "search_passed",
    "benchmark_passed", "preview_passed",
)
_TRANSITIONS = {
    "CREATED": {"FETCHING", "FAILED"},
    "FETCHING": {"BUILDING", "FAILED"},
    "BUILDING": {"VALIDATING", "FAILED"},
    "VALIDATING": {"FAILED"},
    "FAILED": {"FETCHING"},
}
_SCHEMA = (Path(__file__).parent / "sql" / "snapshot_registry.sql").read_text()


class PostgresSnapshotRegistry:
    """Atomic version metadata and promotion for a Psycopg 3 connection.

    Use a *writer* credential for mutations and a separate read-only
    credential for serving. Searches should pin one snapshot ID at start
    and carry it through graph and evidence queries.
    """

    def __init__(self, connection: Any) -> None:
        if not connection.autocommit:
            raise ValueError("registry requires an autocommit connection")
        self.connection = connection

    def ensure_schema(self) -> None:
        """Idempotent explicit setup, called by a maintainer, never on reads."""
        with self.connection.transaction():
            self.connection.execute(_SCHEMA)

    def create_candidate(self, *, schema_version: str, build_code_commit: str,
                         source_cutoff: str, source_description: str) -> str:
        if not all(isinstance(value, str) and value.strip() for value in
                   (schema_version, build_code_commit, source_cutoff, source_description)):
            raise ValueError("snapshot provenance fields must be non-empty")
        cutoff = datetime.fromisoformat(source_cutoff.replace("Z", "+00:00"))
        if cutoff.tzinfo is None or cutoff.astimezone(timezone.utc) > datetime.now(timezone.utc):
            raise ValueError("source_cutoff must be timezone-aware and not in the future")
        snapshot_id = uuid4().hex
        with self.connection.transaction():
            self.connection.execute(
                "INSERT INTO graph_snapshot(snapshot_id,schema_version,build_code_commit,"
                "source_cutoff,source_description,status) VALUES (%s,%s,%s,%s,%s,'CREATED')",
                (snapshot_id, schema_version, build_code_commit, cutoff, source_description))
        return snapshot_id

    def state(self, snapshot_id: str) -> str:
        row = self.connection.execute(
            "SELECT status FROM graph_snapshot WHERE snapshot_id=%s", (snapshot_id,)).fetchone()
        if row is None:
            raise SnapshotStateError("unknown snapshot")
        return str(row[0])

    def advance(self, snapshot_id: str, status: str) -> None:
        if status not in {"FETCHING", "BUILDING", "VALIDATING", "FAILED"}:
            raise SnapshotStateError("state requires a dedicated lifecycle operation")
        with self.connection.transaction():
            row = self.connection.execute(
                "SELECT status FROM graph_snapshot WHERE snapshot_id=%s FOR UPDATE",
                (snapshot_id,)).fetchone()
            if row is None:
                raise SnapshotStateError("unknown snapshot")
            if status not in _TRANSITIONS.get(row[0], set()):
                raise SnapshotStateError(f"cannot change {row[0]} to {status}")
            self.connection.execute(
                "UPDATE graph_snapshot SET status=%s WHERE snapshot_id=%s", (status, snapshot_id))

    def mark_ready(self, snapshot_id: str, *, checksum: str,
                   validation_report: dict[str, Any]) -> None:
        """Only accept a complete external validator report; never promote."""
        if not isinstance(checksum, str) or _SHA256.fullmatch(checksum) is None:
            raise SnapshotStateError("a SHA-256 checksum is required")
        if not isinstance(validation_report, dict) or any(
                validation_report.get(gate) is not True for gate in _REQUIRED_GATES):
            raise SnapshotStateError("all independent validation gates must pass")
        from psycopg.types.json import Jsonb

        with self.connection.transaction():
            row = self.connection.execute(
                "SELECT status FROM graph_snapshot WHERE snapshot_id=%s FOR UPDATE",
                (snapshot_id,)).fetchone()
            if row is None:
                raise SnapshotStateError("unknown snapshot")
            if row[0] != "VALIDATING":
                raise SnapshotStateError("only a validating candidate may become ready")
            self.connection.execute(
                "UPDATE graph_snapshot SET status='READY',checksum=%s,validation_report=%s "
                "WHERE snapshot_id=%s", (checksum, Jsonb(validation_report), snapshot_id))

    def pin_active(self) -> tuple[str | None, int]:
        row = self.connection.execute(
            "SELECT current_snapshot,generation FROM graph_pointer WHERE singleton=TRUE"
        ).fetchone()
        if row is None:
            raise RuntimeError("graph_pointer has not been initialized")
        return row[0], row[1]

    def promote(self, snapshot_id: str) -> None:
        """Atomically switch A→B; A remains the rollback target."""
        with self.connection.transaction():
            pointer = self.connection.execute(
                "SELECT current_snapshot FROM graph_pointer WHERE singleton=TRUE FOR UPDATE"
            ).fetchone()
            if pointer is None:
                raise RuntimeError("graph_pointer has not been initialized")
            row = self.connection.execute(
                "SELECT status FROM graph_snapshot WHERE snapshot_id=%s FOR UPDATE",
                (snapshot_id,)).fetchone()
            if row is None or row[0] != "READY":
                raise SnapshotStateError("only a validated READY snapshot may be promoted")
            previous = pointer[0]
            if previous is not None:
                self.connection.execute(
                    "UPDATE graph_snapshot SET status='SUPERSEDED' "
                    "WHERE snapshot_id=%s AND status='ACTIVE'", (previous,))
            self.connection.execute(
                "UPDATE graph_snapshot SET status='ACTIVE' WHERE snapshot_id=%s", (snapshot_id,))
            self.connection.execute(
                "UPDATE graph_pointer SET current_snapshot=%s,previous_snapshot=%s,"
                "generation=generation+1 WHERE singleton=TRUE", (snapshot_id, previous))

    def rollback(self) -> str:
        """Restore the previous known-good version without rebuilding."""
        with self.connection.transaction():
            row = self.connection.execute(
                "SELECT current_snapshot,previous_snapshot FROM graph_pointer "
                "WHERE singleton=TRUE FOR UPDATE").fetchone()
            if row is None:
                raise RuntimeError("graph_pointer has not been initialized")
            current, previous = row
            if current is None or previous is None:
                raise SnapshotStateError("no previous known-good snapshot is available")
            old = self.connection.execute(
                "SELECT status FROM graph_snapshot WHERE snapshot_id=%s FOR UPDATE",
                (previous,)).fetchone()
            if old is None or old[0] != "SUPERSEDED":
                raise SnapshotStateError("no previous known-good snapshot is available")
            self.connection.execute(
                "UPDATE graph_snapshot SET status='SUPERSEDED' WHERE snapshot_id=%s", (current,))
            self.connection.execute(
                "UPDATE graph_snapshot SET status='ACTIVE' WHERE snapshot_id=%s", (previous,))
            self.connection.execute(
                "UPDATE graph_pointer SET current_snapshot=%s,previous_snapshot=NULL,"
                "generation=generation+1 WHERE singleton=TRUE", (previous,))
            return previous

    def status(self) -> dict[str, Any]:
        row = self.connection.execute(
            "SELECT p.current_snapshot,p.previous_snapshot,p.generation,"
            "s.source_cutoff,s.created_at,s.schema_version,s.status "
            "FROM graph_pointer p LEFT JOIN graph_snapshot s "
            "ON s.snapshot_id=p.current_snapshot WHERE p.singleton=TRUE").fetchone()
        if row is None:
            raise RuntimeError("graph_pointer has not been initialized")
        current, previous, generation, cutoff, built_at, schema, state = row
        if current is None:
            return {"graph_status": "unavailable", "snapshot": None,
                    "generation": generation}
        return {
            "graph_status": "ok", "snapshot": current,
            "source_cutoff": cutoff.isoformat(), "built_at": built_at.isoformat(),
            "age_days": max(0, (datetime.now(timezone.utc) - cutoff).days),
            "schema_version": schema, "validation_status": state,
            "previous_snapshot": previous, "generation": generation,
        }
