"""Hermetic tests for the independent compact-import validator.

No network and no database server: a SQLite-backed stand-in mimics the
psycopg 3 connection surface the validator uses (``execute`` returning a
cursor, ``%s`` placeholders, ``set_config`` for the statement timeout).
"""

from __future__ import annotations

import sqlite3
from typing import Any

import pytest

from hepgraph.postgres_registry import _REQUIRED_GATES
from hepgraph.snapshot_validation import (CompactImportValidator, Finding,
                                          ValidationError)


IMPORT_ID = "test-import"
CUTOFF = "2026-09-16T12:00:00+00:00"
BEFORE_CUTOFF = "2026-09-16T09:00:00+00:00"
AFTER_CUTOFF = "2026-09-16T18:00:00+00:00"

# Mirrors hepgraph.neon_compact_import.SCHEMA in SQLite dialect. Foreign keys
# are declared but left unenforced (SQLite default) so orphan rows can be
# planted deliberately.
_SQLITE_SCHEMA = """
CREATE TABLE inspire_compact_import (
    import_id TEXT PRIMARY KEY,
    source_cutoff TEXT NOT NULL,
    low_recid INTEGER NOT NULL,
    high_recid INTEGER NOT NULL,
    status TEXT NOT NULL
);
CREATE TABLE inspire_compact_shard (
    import_id TEXT NOT NULL,
    low_recid INTEGER NOT NULL,
    high_recid INTEGER NOT NULL,
    status TEXT NOT NULL,
    expected_records INTEGER,
    next_page INTEGER NOT NULL DEFAULT 1,
    received_records INTEGER NOT NULL DEFAULT 0,
    retained_works INTEGER NOT NULL DEFAULT 0,
    retained_memberships INTEGER NOT NULL DEFAULT 0,
    failure TEXT,
    PRIMARY KEY(import_id, low_recid, high_recid)
);
CREATE TABLE inspire_compact_work (
    import_id TEXT NOT NULL,
    work_id INTEGER NOT NULL,
    year INTEGER,
    author_count INTEGER NOT NULL,
    member_count INTEGER NOT NULL,
    source_updated_at TEXT,
    retrieved_at TEXT NOT NULL,
    PRIMARY KEY(import_id, work_id)
);
CREATE TABLE inspire_compact_membership (
    import_id TEXT NOT NULL,
    work_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    PRIMARY KEY(import_id, work_id, author_id),
    FOREIGN KEY(import_id, work_id)
        REFERENCES inspire_compact_work(import_id, work_id)
);
"""


class _Cursor:
    def __init__(self, rows: list[Any]) -> None:
        self._rows = rows

    def fetchall(self) -> list[Any]:
        return list(self._rows)

    def fetchone(self) -> Any:
        return self._rows[0] if self._rows else None


class FakeConnection:
    """SQLite stand-in for an autocommit psycopg 3 connection."""

    def __init__(self, *, dict_rows: bool = False) -> None:
        self._db = sqlite3.connect(":memory:")
        self._db.row_factory = sqlite3.Row
        self._db.executescript(_SQLITE_SCHEMA)
        self.dict_rows = dict_rows
        self.statements: list[str] = []
        self.statement_timeout: str | None = None

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> _Cursor:
        self.statements.append(query)
        if "set_config" in query:
            self.statement_timeout = params[0]
            return _Cursor([])
        rows = self._db.execute(query.replace("%s", "?"), params).fetchall()
        return _Cursor([dict(row) for row in rows] if self.dict_rows else rows)

    def seed(self, table: str, rows: list[tuple[Any, ...]], columns: str) -> None:
        marks = ",".join("?" * len(columns.split(",")))
        self._db.executemany(f"INSERT INTO {table}({columns}) VALUES ({marks})", rows)
        self._db.commit()


def _seed_import(connection: FakeConnection, *, low: int = 1, high: int = 100,
                 cutoff: str = CUTOFF, status: str = "FETCHING") -> None:
    connection.seed("inspire_compact_import", [(IMPORT_ID, cutoff, low, high, status)],
                    "import_id,source_cutoff,low_recid,high_recid,status")


def _seed_shards(connection: FakeConnection, rows: list[tuple[Any, ...]]) -> None:
    connection.seed(
        "inspire_compact_shard",
        [(IMPORT_ID, *row) for row in rows],
        "import_id,low_recid,high_recid,status,expected_records,received_records,retained_works")


def _seed_works(connection: FakeConnection, rows: list[tuple[Any, ...]]) -> None:
    connection.seed("inspire_compact_work", [(IMPORT_ID, *row) for row in rows],
                    "import_id,work_id,year,author_count,member_count,retrieved_at")


def _seed_memberships(connection: FakeConnection, rows: list[tuple[int, int]]) -> None:
    connection.seed("inspire_compact_membership", [(IMPORT_ID, *row) for row in rows],
                    "import_id,work_id,author_id")


def complete_import(*, dict_rows: bool = False,
                    late_retrieval: bool = False) -> FakeConnection:
    """A synthetic import that is genuinely complete for recids 1..100.

    The cutoff deliberately sits after the retrievals: a real importer stamps
    source_cutoff before it fetches, which is exactly why the source-window
    check exists.
    """
    connection = FakeConnection(dict_rows=dict_rows)
    _seed_import(connection)
    _seed_shards(connection, [
        (1, 50, "SPLIT", 3, 0, 0),
        (1, 25, "DONE", 2, 2, 2),
        (26, 50, "DONE", 1, 1, 1),
        (51, 100, "DONE", 0, 0, 0),
    ])
    _seed_works(connection, [
        (10, 2021, 3, 2, BEFORE_CUTOFF),
        (20, 2019, 2, 2, BEFORE_CUTOFF),
        (30, None, 5, 3, AFTER_CUTOFF if late_retrieval else BEFORE_CUTOFF),
    ])
    _seed_memberships(connection, [
        (10, 901), (10, 902),
        (20, 902), (20, 903),
        (30, 901), (30, 903), (30, 904),
    ])
    return connection


def validator(connection: FakeConnection) -> CompactImportValidator:
    return CompactImportValidator(connection, IMPORT_ID, current_year=2026)


def _finding(report: Any, name: str) -> Finding:
    return report.finding(name)


def test_complete_import_passes_every_check_and_proves_source_completeness():
    report = validator(complete_import()).validate()
    assert [item.name for item in report.failures()] == []
    assert report.passed is True
    assert report.gates["source_complete"] is True
    assert report.gates["work_semantics_passed"] is True
    assert report.coverage.complete is True
    assert report.coverage.reason == "declared_range_fully_discovered_and_reconciled"
    assert report.coverage.covered_ranges == ((1, 100),)
    assert report.coverage.gaps == ()
    assert report.coverage.observed_work_span == (10, 30)


def test_dict_row_connections_produce_the_same_verdict():
    tuple_report = validator(complete_import()).validate()
    dict_report = validator(complete_import(dict_rows=True)).validate()
    assert dict_report.as_dict() == tuple_report.as_dict()


def test_every_statement_is_a_select_and_the_statement_timeout_is_set():
    connection = complete_import()
    validator(connection).validate()
    assert connection.statement_timeout == "30000"
    assert all(statement.lstrip().upper().startswith("SELECT")
               for statement in connection.statements)
    assert sum("set_config" in statement for statement in connection.statements) == 1


def test_validator_refuses_to_issue_a_write():
    audit = validator(complete_import())
    with pytest.raises(ValueError):
        audit._fetch("DELETE FROM inspire_compact_work", (), ())


def test_unknown_import_cannot_be_validated():
    connection = FakeConnection()
    with pytest.raises(ValidationError):
        CompactImportValidator(connection, "absent").validate()


def test_partial_import_reports_gaps_and_refuses_source_completeness():
    connection = FakeConnection()
    _seed_import(connection)
    # 51..100 was never discovered at all, and 26..50 is still being paged.
    _seed_shards(connection, [
        (1, 50, "SPLIT", 3, 0, 0),
        (1, 25, "DONE", 2, 2, 1),
        (26, 50, "PENDING", 4, 1, 0),
    ])
    _seed_works(connection, [(10, 2021, 3, 2, BEFORE_CUTOFF)])
    _seed_memberships(connection, [(10, 901), (10, 902)])
    report = validator(connection).validate()

    coverage = _finding(report, "shard_coverage")
    assert coverage.passed is False
    assert coverage.details["gaps"] == [[51, 100]]
    assert coverage.details["covered_ranges"] == [[1, 50]]
    assert coverage.details["covered_equals_declared"] is False
    completion = _finding(report, "shard_completion")
    assert completion.passed is False
    assert completion.details["outstanding"] == {"PENDING": 1}
    assert report.passed is False
    assert report.gates["source_complete"] is False
    assert report.coverage.complete is False
    assert report.coverage.reason == "shard_ranges_do_not_tile_declared_range"
    assert report.gate_reasons["source_complete"] == report.coverage.reason


def test_split_shard_without_children_is_a_gap_and_overlaps_are_reported():
    connection = FakeConnection()
    _seed_import(connection)
    _seed_shards(connection, [
        (1, 60, "SPLIT", 20000, 0, 0),   # children were never inserted
        (40, 100, "DONE", 1, 1, 1),      # and this leaf overlaps the lost half
    ])
    _seed_works(connection, [(50, 2020, 2, 2, BEFORE_CUTOFF)])
    _seed_memberships(connection, [(50, 901), (50, 902)])
    coverage = validator(connection).check_shard_coverage()
    assert coverage.passed is False
    assert coverage.details["gaps"] == [[1, 39]]
    assert coverage.details["interior_shards"] == 1
    assert coverage.details["leaf_shards"] == 1


def test_under_received_shard_fails_reconciliation():
    connection = complete_import()
    connection.seed("inspire_compact_shard",
                    [(IMPORT_ID, 101, 150, "DONE", 9, 4, 0)],
                    "import_id,low_recid,high_recid,status,expected_records,"
                    "received_records,retained_works")
    finding = validator(connection).check_record_reconciliation()
    assert finding.passed is False
    assert finding.details["under_receipt_count"] == 1
    assert finding.details["under_receipt"][0] == {
        "low_recid": 101, "high_recid": 150,
        "expected_records": 9, "received_records": 4}


def test_undiscovered_shard_has_no_upstream_total_and_fails_reconciliation():
    connection = FakeConnection()
    _seed_import(connection)
    _seed_shards(connection, [(1, 100, "PENDING", None, 0, 0)])
    finding = validator(connection).check_record_reconciliation()
    assert finding.passed is False
    assert finding.details["undiscovered_shards"] == [[1, 100]]


def test_orphan_memberships_are_detected():
    connection = complete_import()
    _seed_memberships(connection, [(777, 901), (777, 902)])
    finding = validator(connection).check_referential_integrity()
    assert finding.passed is False
    assert finding.details["orphan_memberships"] == 2
    assert finding.details["orphan_work_id_examples"] == [777]


def test_member_count_must_match_the_stored_membership_degree():
    connection = complete_import()
    _seed_works(connection, [(40, 2022, 9, 4, BEFORE_CUTOFF)])
    _seed_memberships(connection, [(40, 901), (40, 902)])
    finding = validator(connection).check_work_semantics()
    assert finding.passed is False
    assert finding.details["member_count_mismatches"] == 1
    assert finding.details["member_count_exceeds_author_count"] == 0
    assert finding.details["examples"][0] == {
        "work_id": 40, "member_count": 4, "author_count": 9, "membership_rows": 2}


def test_member_count_may_never_exceed_the_true_author_count():
    connection = complete_import()
    _seed_works(connection, [(40, 2022, 3, 4, BEFORE_CUTOFF)])
    _seed_memberships(connection, [(40, 901), (40, 902), (40, 903), (40, 904)])
    finding = validator(connection).check_work_semantics()
    assert finding.passed is False
    assert finding.details["member_count_exceeds_author_count"] == 1
    assert finding.details["member_count_mismatches"] == 0


def test_member_count_below_two_is_rejected():
    connection = complete_import()
    _seed_works(connection, [(40, 2022, 5, 1, BEFORE_CUTOFF)])
    _seed_memberships(connection, [(40, 901)])
    finding = validator(connection).check_work_semantics()
    assert finding.passed is False
    assert finding.details["member_count_below_two"] == 1


def test_duplicate_check_states_what_the_schema_cannot_decide():
    finding = validator(complete_import()).check_duplicate_works()
    assert finding.passed is True
    assert finding.details["duplicate_work_ids"] == 0
    assert "NOT verifiable" in finding.details["unverifiable"]
    assert "DOI" in finding.details["unverifiable"]


def test_implausible_years_are_reported_and_null_years_are_allowed():
    connection = complete_import()
    _seed_works(connection, [(40, 3999, 2, 2, BEFORE_CUTOFF)])
    _seed_memberships(connection, [(40, 901), (40, 902)])
    finding = validator(connection).check_year_sanity()
    assert finding.passed is False
    assert finding.details["out_of_range"] == 1
    assert finding.details["missing_year"] == 1
    assert finding.details["plausible_range"] == [1500, 2027]


def test_work_rows_may_never_exceed_the_shard_retention_counters():
    connection = complete_import()
    _seed_works(connection, [(40, 2024, 2, 2, BEFORE_CUTOFF)])
    _seed_memberships(connection, [(40, 901), (40, 902)])
    finding = validator(connection).check_record_reconciliation()
    assert finding.passed is False
    assert finding.details["work_rows_exceed_retained_counter"] is True
    assert (finding.details["work_rows"], finding.details["retained_works_counter"]) == (4, 3)


def test_rows_retrieved_after_the_cutoff_break_the_source_window():
    connection = complete_import(late_retrieval=True)
    finding = validator(connection).check_source_window()
    assert finding.passed is False
    assert finding.details["rows_retrieved_after_cutoff"] == 1
    assert finding.details["source_cutoff"] == CUTOFF
    assert finding.details["latest_retrieved_at"] == AFTER_CUTOFF
    assert finding.details["retrieval_span_seconds"] == 9 * 3600
    assert "start marker" in finding.details["note"]


def test_source_window_failure_does_not_by_itself_deny_source_completeness():
    report = validator(complete_import(late_retrieval=True)).validate()
    assert report.passed is False
    assert [item.name for item in report.failures()] == ["source_window"]
    assert report.gates["source_complete"] is True


def test_gates_never_claim_what_the_database_cannot_prove():
    report = validator(complete_import()).validate()
    assert set(report.gates) == set(_REQUIRED_GATES)
    provable = {"source_complete", "work_semantics_passed"}
    for gate in _REQUIRED_GATES:
        if gate not in provable:
            assert report.gates[gate] is False
            assert report.gate_reasons[gate]
    # A perfect import still cannot satisfy mark_ready() on its own.
    assert any(report.gates[gate] is not True for gate in _REQUIRED_GATES)


def test_report_dict_is_shaped_for_mark_ready_and_names_its_limitations():
    payload = validator(complete_import()).validate().as_dict()
    assert payload["source_complete"] is True
    assert payload["import_id"] == IMPORT_ID
    assert len(payload["findings"]) == 9
    assert any("DOI" in item for item in payload["limitations"])
    assert any("atomic snapshot" in item for item in payload["limitations"])
    assert any("cannot be re-derived" in item for item in payload["limitations"])
