"""Independent, adversarial validation of a compact INSPIRE candidate import.

The product claim is that a reported route is *mathematically shortest*, or
that *no path exists*. Both claims are statements about a complete universe,
so they may only be made when the underlying import is provably complete for
the queried range. This module exists to decide that question without
trusting the importer: the importer's own status columns describe what it
believes it did, and a belief is not evidence.

Everything here is therefore derived from persisted rows, and every check
fails closed. A gate is set to True only when the database itself proves the
property; anything the schema cannot decide is reported as False with a
reason and recorded in ``ValidationReport.limitations`` so a reader can never
mistake "not checked" for "checked and fine". All SQL is read-only,
parameterized, and bounded by a session statement timeout.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .neon_compact_import import PAGE_SIZE
from .postgres_registry import _REQUIRED_GATES


MIN_PLAUSIBLE_YEAR = 1500
EXAMPLE_LIMIT = 5
DEFAULT_STATEMENT_TIMEOUT_MS = 30_000

# Shard states that are leaves of the discovery tree. SPLIT nodes are interior
# and are covered only by their children, so a SPLIT node whose children were
# never inserted shows up as a gap rather than as coverage.
_LEAF_STATES = frozenset({"DISCOVER", "PENDING", "DONE", "FAILED"})
_INTERIOR_STATE = "SPLIT"
_UNFINISHED_STATES = ("DISCOVER", "PENDING", "FAILED")

# Gates this module can decide from the candidate database alone. Every other
# required gate defaults to False with the reason below.
_UNPROVABLE_GATES = {
    "checksums_match":
        "no checksum of the imported rows is stored in this schema",
    "identity_passed":
        "only resolved INSPIRE author IDs are stored; merged or split author "
        "records cannot be detected from them",
    "graph_passed":
        "graph construction and reachability are not exercised by reading the "
        "import tables",
    "search_passed":
        "search exactness must be demonstrated by running the engine",
    "benchmark_passed":
        "benchmark routes must be executed against a built snapshot",
    "preview_passed":
        "preview requires a served snapshot and human review",
}

LIMITATIONS: tuple[str, ...] = (
    "Ingest-time eligibility rules (allowed document types, erratum and "
    "corrigendum exclusion, author_count >= 2, resolved-author roles) were "
    "applied by the importer and cannot be re-derived: no titles, document "
    "types, or author roles are persisted.",
    "Preprint/journal duplicate reconciliation is NOT verifiable from this "
    "schema: no DOI or arXiv identifiers are stored, so two rows describing "
    "the same paper under different literature IDs are indistinguishable "
    "from two distinct papers.",
    "INSPIRE exposes no verifiable atomic snapshot, so source_cutoff is a "
    "start marker, not proof of a point-in-time view of the source.",
    "expected_records is reported by the source itself; records the source "
    "never returned, or deleted upstream before discovery, are invisible "
    "here.",
    "Records rejected at ingest are not recorded, so the difference between a "
    "shard's received_records and its retained_works cannot be attributed.",
    "Author identity disambiguation is out of scope: identity_passed must be "
    "established by the identity guard, not by this validator.",
    "Graph, search, benchmark, preview, and checksum gates require running "
    "the engine over a built snapshot and are never granted here.",
)


@dataclass(frozen=True, slots=True)
class Finding:
    """One check's verdict plus the evidence that produced it."""

    name: str
    passed: bool
    details: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "passed": self.passed, "details": self.details}


@dataclass(frozen=True, slots=True)
class CoverageClaim:
    """What range this import may honestly claim to cover."""

    complete: bool
    reason: str
    declared_range: tuple[int, int]
    covered_ranges: tuple[tuple[int, int], ...]
    gaps: tuple[tuple[int, int], ...]
    observed_work_span: tuple[int, int] | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "complete": self.complete, "reason": self.reason,
            "declared_range": list(self.declared_range),
            "covered_ranges": [list(item) for item in self.covered_ranges],
            "gaps": [list(item) for item in self.gaps],
            "observed_work_span": (None if self.observed_work_span is None
                                   else list(self.observed_work_span)),
        }


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """Aggregate verdict, shaped to feed ``PostgresSnapshotRegistry.mark_ready``."""

    import_id: str
    passed: bool
    findings: tuple[Finding, ...]
    gates: dict[str, bool]
    gate_reasons: dict[str, str]
    coverage: CoverageClaim
    limitations: tuple[str, ...] = LIMITATIONS

    def finding(self, name: str) -> Finding:
        for item in self.findings:
            if item.name == name:
                return item
        raise KeyError(name)

    def failures(self) -> tuple[Finding, ...]:
        return tuple(item for item in self.findings if not item.passed)

    def as_dict(self) -> dict[str, Any]:
        """A JSON-serializable report with gate booleans at the top level."""
        report: dict[str, Any] = dict(self.gates)
        report.update({
            "import_id": self.import_id, "passed": self.passed,
            "findings": [item.as_dict() for item in self.findings],
            "gate_reasons": dict(self.gate_reasons),
            "coverage": self.coverage.as_dict(),
            "limitations": list(self.limitations),
        })
        return report


class ValidationError(RuntimeError):
    """The candidate cannot be validated at all (e.g. the import is unknown)."""


def _row_values(row: Any, columns: Sequence[str]) -> tuple[Any, ...]:
    """Accept dict_row, tuple rows, or psycopg named rows identically."""
    if isinstance(row, Mapping):
        return tuple(row[name] for name in columns)
    return tuple(row)


def _as_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def _iso(value: Any) -> str | None:
    moment = _as_datetime(value)
    return moment.isoformat() if moment is not None else (
        value if isinstance(value, str) and value else None)


def _int(value: Any) -> int:
    return 0 if value is None else int(value)


class CompactImportValidator:
    """Read-only auditor for one ``inspire_compact_*`` candidate import.

    Constructed with a psycopg-style connection whose ``execute`` returns a
    cursor. The validator never writes, never creates schema, and never asks
    the importer whether it finished.
    """

    def __init__(self, connection: Any, import_id: str, *,
                 statement_timeout_ms: int = DEFAULT_STATEMENT_TIMEOUT_MS,
                 current_year: int | None = None) -> None:
        if not isinstance(import_id, str) or not import_id.strip():
            raise ValueError("import_id must be a non-empty string")
        if statement_timeout_ms < 1:
            raise ValueError("statement_timeout_ms must be positive")
        self.connection = connection
        self.import_id = import_id
        self.statement_timeout_ms = statement_timeout_ms
        self.current_year = current_year or datetime.now().year
        self._timeout_applied = False
        self._identity: tuple[int, int, Any, str] | None = None

    # ---- bounded read-only access -------------------------------------

    def _fetch(self, query: str, params: tuple[Any, ...],
               columns: Sequence[str]) -> list[tuple[Any, ...]]:
        if not query.lstrip().upper().startswith("SELECT"):
            raise ValueError("the validator may only issue SELECT statements")
        self._ensure_timeout()
        rows = self.connection.execute(query, params).fetchall()
        return [_row_values(row, columns) for row in rows]

    def _fetch_one(self, query: str, params: tuple[Any, ...],
                   columns: Sequence[str]) -> tuple[Any, ...] | None:
        rows = self._fetch(query, params, columns)
        return rows[0] if rows else None

    def _ensure_timeout(self) -> None:
        # set_config is a SELECT, so the read-only rule holds; is_local=false
        # is required because the caller's connection is autocommit and a
        # transaction-local setting would silently do nothing.
        if self._timeout_applied:
            return
        self._timeout_applied = True
        self.connection.execute(
            "SELECT set_config('statement_timeout', %s, false)",
            (str(self.statement_timeout_ms),))

    # ---- import identity ----------------------------------------------

    def import_row(self) -> tuple[int, int, Any, str]:
        """Declared identity, read once so every check audits the same claim."""
        if self._identity is None:
            row = self._fetch_one(
                "SELECT low_recid, high_recid, source_cutoff, status "
                "FROM inspire_compact_import WHERE import_id = %s",
                (self.import_id,), ("low_recid", "high_recid", "source_cutoff", "status"))
            if row is None:
                raise ValidationError(f"no compact import named {self.import_id!r}")
            self._identity = (int(row[0]), int(row[1]), row[2], str(row[3]))
        return self._identity

    def _shards(self) -> list[tuple[int, int, str, int | None, int, int, int, int]]:
        columns = ("low_recid", "high_recid", "status", "expected_records",
                   "received_records", "retained_works", "retained_memberships",
                   "next_page")
        return [(int(low), int(high), str(status),
                 None if expected is None else int(expected),
                 _int(received), _int(works), _int(memberships), _int(page))
                for low, high, status, expected, received, works, memberships, page
                in self._fetch(
                    "SELECT low_recid, high_recid, status, expected_records, "
                    "received_records, retained_works, retained_memberships, next_page "
                    "FROM inspire_compact_shard WHERE import_id = %s "
                    "ORDER BY low_recid, high_recid", (self.import_id,), columns)]

    # ---- checks --------------------------------------------------------

    def check_shard_coverage(self) -> Finding:
        """Leaf shards must tile the declared range with no gap and no overlap."""
        low, high, _, _ = self.import_row()
        shards = self._shards()
        unknown = sorted({status for _, _, status, _, _, _, _, _ in shards
                          if status not in _LEAF_STATES and status != _INTERIOR_STATE})
        leaves = sorted((shard_low, shard_high)
                        for shard_low, shard_high, status, _, _, _, _, _ in shards
                        if status in _LEAF_STATES)
        inverted = [[a, b] for a, b in leaves if a > b]
        outside = [[a, b] for a, b in leaves if a < low or b > high]

        covered: list[list[int]] = []
        overlaps: list[list[int]] = []
        gaps: list[list[int]] = []
        cursor = low
        for shard_low, shard_high in leaves:
            if shard_low > cursor:
                gaps.append([cursor, shard_low - 1])
            elif shard_low < cursor:
                overlaps.append([shard_low, min(shard_high, cursor - 1)])
            if covered and shard_low <= covered[-1][1] + 1:
                covered[-1][1] = max(covered[-1][1], shard_high)
            else:
                covered.append([shard_low, shard_high])
            cursor = max(cursor, shard_high + 1)
        if cursor <= high:
            gaps.append([cursor, high])

        exact = covered == [[low, high]]
        passed = (not gaps and not overlaps and not inverted
                  and not outside and not unknown and exact)
        return Finding("shard_coverage", passed, {
            "declared_range": [low, high],
            "leaf_shards": len(leaves),
            "interior_shards": sum(1 for _, _, status, _, _, _, _, _ in shards
                                   if status == _INTERIOR_STATE),
            "covered_ranges": covered,
            "gaps": gaps,
            "overlaps": overlaps,
            "inverted_ranges": inverted,
            "ranges_outside_declared": outside,
            "unknown_statuses": unknown,
            "covered_equals_declared": exact,
        })

    def check_shard_completion(self) -> Finding:
        """Any shard not DONE means ingestion has not finished."""
        _, _, _, import_status = self.import_row()
        shards = self._shards()
        counts: dict[str, int] = {}
        for _, _, status, _, _, _, _, _ in shards:
            counts[status] = counts.get(status, 0) + 1
        outstanding = {state: counts[state] for state in _UNFINISHED_STATES
                       if counts.get(state)}
        examples = [[low, high, status] for low, high, status, _, _, _, _, _ in shards
                    if status in _UNFINISHED_STATES][:EXAMPLE_LIMIT]
        return Finding("shard_completion", bool(shards) and not outstanding, {
            "shard_status_counts": counts,
            "outstanding": outstanding,
            "outstanding_examples": examples,
            # The importer has no terminal success state: FETCHING/PAUSED/FAILED
            # are the only values it writes, so this is context, not evidence.
            "import_status": import_status,
            "shards_present": len(shards),
        })

    def check_record_reconciliation(self) -> Finding:
        """Per leaf shard, received_records must equal the upstream total."""
        shards = self._shards()
        undiscovered: list[list[int]] = []
        under: list[dict[str, int]] = []
        over: list[dict[str, int]] = []
        replayed: list[dict[str, int]] = []
        expected_total = received_total = retained_works_total = 0
        for low, high, status, expected, received, works, _, next_page in shards:
            if status not in _LEAF_STATES:
                continue
            retained_works_total += works
            if expected is None:
                undiscovered.append([low, high])
                continue
            expected_total += expected
            received_total += received
            if received < expected:
                under.append({"low_recid": low, "high_recid": high,
                              "expected_records": expected, "received_records": received})
            elif received > expected:
                # The counter records page *attempts*, so a replayed page inflates
                # it while the primary key discards the duplicate rows. What
                # actually proves the shard was covered is the page cursor: every
                # page up to ceil(expected / PAGE_SIZE) has been committed. Treat
                # a surplus with a complete cursor as a replay, and keep failing
                # the ones where pagination really did stop short.
                entry = {"low_recid": low, "high_recid": high,
                         "expected_records": expected, "received_records": received,
                         "next_page": next_page}
                if (next_page - 1) * PAGE_SIZE >= expected:
                    replayed.append(entry)
                else:
                    over.append(entry)
        work_rows = self._work_count()
        impossible = work_rows > retained_works_total
        passed = not undiscovered and not under and not over and not impossible
        return Finding("record_reconciliation", passed, {
            "expected_records_total": expected_total,
            "received_records_total": received_total,
            "undiscovered_shards": undiscovered[:EXAMPLE_LIMIT],
            "undiscovered_shard_count": len(undiscovered),
            "under_receipt": under[:EXAMPLE_LIMIT],
            "under_receipt_count": len(under),
            "over_receipt": over[:EXAMPLE_LIMIT],
            "over_receipt_count": len(over),
            "replayed_pages": replayed[:EXAMPLE_LIMIT],
            "replayed_page_shard_count": len(replayed),
            "retained_works_counter": retained_works_total,
            "work_rows": work_rows,
            # Retry attempts can inflate the counter above the deduplicated row
            # count; the reverse is impossible and means rows arrived untracked.
            "work_rows_exceed_retained_counter": impossible,
        })

    def check_referential_integrity(self) -> Finding:
        """Every membership must point at a work row of the same import."""
        row = self._fetch_one(
            "SELECT COUNT(*) AS orphans FROM inspire_compact_membership m "
            "WHERE m.import_id = %s AND NOT EXISTS ("
            "SELECT 1 FROM inspire_compact_work w "
            "WHERE w.import_id = m.import_id AND w.work_id = m.work_id)",
            (self.import_id,), ("orphans",))
        orphans = _int(row[0]) if row else 0
        examples = [int(value) for (value,) in self._fetch(
            "SELECT DISTINCT m.work_id FROM inspire_compact_membership m "
            "WHERE m.import_id = %s AND NOT EXISTS ("
            "SELECT 1 FROM inspire_compact_work w "
            "WHERE w.import_id = m.import_id AND w.work_id = m.work_id) "
            "ORDER BY m.work_id LIMIT %s",
            (self.import_id, EXAMPLE_LIMIT), ("work_id",))] if orphans else []
        membership_row = self._fetch_one(
            "SELECT COUNT(*) AS memberships FROM inspire_compact_membership "
            "WHERE import_id = %s", (self.import_id,), ("memberships",))
        return Finding("referential_integrity", orphans == 0, {
            "orphan_memberships": orphans,
            "orphan_work_id_examples": examples,
            "membership_rows": _int(membership_row[0]) if membership_row else 0,
        })

    def check_work_semantics(self) -> Finding:
        """member_count must equal the stored membership degree, and 2 <= it <= author_count."""
        summary = self._fetch_one(
            "SELECT "
            "COALESCE(SUM(CASE WHEN actual <> member_count THEN 1 ELSE 0 END),0) AS mismatched,"
            "COALESCE(SUM(CASE WHEN member_count < 2 THEN 1 ELSE 0 END),0) AS below_minimum,"
            "COALESCE(SUM(CASE WHEN member_count > author_count THEN 1 ELSE 0 END),0) AS exceeds_authors,"
            "COUNT(*) AS works FROM (" + self._semantics_subquery() + ") AS s",
            (self.import_id,),
            ("mismatched", "below_minimum", "exceeds_authors", "works"))
        mismatched, below, exceeds, works = (
            (_int(summary[0]), _int(summary[1]), _int(summary[2]), _int(summary[3]))
            if summary else (0, 0, 0, 0))
        examples = [{"work_id": int(work_id), "member_count": _int(member_count),
                     "author_count": _int(author_count), "membership_rows": _int(actual)}
                    for work_id, member_count, author_count, actual in self._fetch(
                        "SELECT work_id, member_count, author_count, actual FROM ("
                        + self._semantics_subquery() + ") AS s "
                        "WHERE actual <> member_count OR member_count < 2 "
                        "OR member_count > author_count ORDER BY work_id LIMIT %s",
                        (self.import_id, EXAMPLE_LIMIT),
                        ("work_id", "member_count", "author_count", "actual"))
                    ] if (mismatched or below or exceeds) else []
        return Finding("work_semantics", not (mismatched or below or exceeds), {
            "works": works,
            "member_count_mismatches": mismatched,
            "member_count_below_two": below,
            "member_count_exceeds_author_count": exceeds,
            "examples": examples,
        })

    @staticmethod
    def _semantics_subquery() -> str:
        return ("SELECT w.work_id AS work_id, w.member_count AS member_count, "
                "w.author_count AS author_count, COUNT(m.author_id) AS actual "
                "FROM inspire_compact_work w LEFT JOIN inspire_compact_membership m "
                "ON m.import_id = w.import_id AND m.work_id = w.work_id "
                "WHERE w.import_id = %s "
                "GROUP BY w.work_id, w.member_count, w.author_count")

    def check_duplicate_works(self) -> Finding:
        """Exact duplicates are impossible by primary key; near-duplicates are invisible."""
        row = self._fetch_one(
            "SELECT COUNT(*) AS rows_present, COUNT(DISTINCT work_id) AS distinct_work_ids "
            "FROM inspire_compact_work WHERE import_id = %s",
            (self.import_id,), ("rows_present", "distinct_work_ids"))
        present, distinct = (_int(row[0]), _int(row[1])) if row else (0, 0)
        return Finding("duplicate_works", present == distinct, {
            "work_rows": present,
            "distinct_work_ids": distinct,
            "duplicate_work_ids": present - distinct,
            "primary_key_prevents_exact_duplicates": True,
            "note": "(import_id, work_id) is the primary key, so exact duplicate "
                    "rows cannot exist; this check only confirms the constraint "
                    "still holds in the table being read.",
            "unverifiable": "Preprint/journal duplicate reconciliation by DOI or "
                            "arXiv identifier is NOT verifiable from this schema: "
                            "no external identifiers are stored.",
        })

    def check_year_sanity(self) -> Finding:
        """Years are optional, but a stored year must be plausible."""
        upper = self.current_year + 1
        row = self._fetch_one(
            "SELECT COALESCE(SUM(CASE WHEN year IS NULL THEN 1 ELSE 0 END),0) AS missing,"
            "COALESCE(SUM(CASE WHEN year IS NOT NULL AND (year < %s OR year > %s) "
            "THEN 1 ELSE 0 END),0) AS out_of_range,"
            "MIN(year) AS earliest, MAX(year) AS latest "
            "FROM inspire_compact_work WHERE import_id = %s",
            (MIN_PLAUSIBLE_YEAR, upper, self.import_id),
            ("missing", "out_of_range", "earliest", "latest"))
        missing, out_of_range, earliest, latest = (
            (_int(row[0]), _int(row[1]), row[2], row[3]) if row else (0, 0, None, None))
        return Finding("year_sanity", out_of_range == 0, {
            "plausible_range": [MIN_PLAUSIBLE_YEAR, upper],
            "missing_year": missing,
            "out_of_range": out_of_range,
            "earliest_year": None if earliest is None else int(earliest),
            "latest_year": None if latest is None else int(latest),
        })

    def check_source_window(self) -> Finding:
        """Rows retrieved after the cutoff prove the cutoff is not a snapshot."""
        _, _, cutoff, _ = self.import_row()
        row = self._fetch_one(
            "SELECT MIN(retrieved_at) AS earliest, MAX(retrieved_at) AS latest,"
            "COALESCE(SUM(CASE WHEN retrieved_at > %s THEN 1 ELSE 0 END),0) AS after_cutoff,"
            "COUNT(*) AS works FROM inspire_compact_work WHERE import_id = %s",
            (cutoff, self.import_id), ("earliest", "latest", "after_cutoff", "works"))
        earliest, latest, after, works = (
            (row[0], row[1], _int(row[2]), _int(row[3])) if row else (None, None, 0, 0))
        first, last = _as_datetime(earliest), _as_datetime(latest)
        span = (last - first).total_seconds() if first and last else None
        return Finding("source_window", after == 0, {
            "source_cutoff": _iso(cutoff),
            "earliest_retrieved_at": _iso(earliest),
            "latest_retrieved_at": _iso(latest),
            "retrieval_span_seconds": span,
            "rows_retrieved_after_cutoff": after,
            "works": works,
            "note": "INSPIRE offers no verifiable atomic snapshot. source_cutoff "
                    "is a start marker; rows retrieved after it were read from a "
                    "source that may have changed mid-import.",
        })

    def check_coverage_claim(self, prerequisites: Sequence[Finding]) -> Finding:
        """Derive the claim this import supports from the checks already run."""
        low, high, _, _ = self.import_row()
        span, works = self._observed_work_span()
        return self._coverage_finding(
            self._coverage_claim(prerequisites, (low, high), span), works)

    def _observed_work_span(self) -> tuple[tuple[int, int] | None, int]:
        row = self._fetch_one(
            "SELECT MIN(work_id) AS lowest, MAX(work_id) AS highest, "
            "COUNT(*) AS works FROM inspire_compact_work WHERE import_id = %s",
            (self.import_id,), ("lowest", "highest", "works"))
        lowest, highest, works = ((row[0], row[1], _int(row[2])) if row
                                  else (None, None, 0))
        span = (None if lowest is None or highest is None
                else (int(lowest), int(highest)))
        return span, works

    @staticmethod
    def _coverage_finding(claim: CoverageClaim, works: int) -> Finding:
        details = claim.as_dict()
        details.update({
            "work_rows": works,
            # The observed span is always a subset of the declared range: most
            # literature IDs never qualify, so it is context, not coverage.
            "observed_span_is_not_coverage": True,
        })
        return Finding("coverage_claim", claim.complete, details)

    # ---- aggregation ---------------------------------------------------

    def _coverage_claim(self, findings: Sequence[Finding],
                        declared: tuple[int, int],
                        observed: tuple[int, int] | None) -> CoverageClaim:
        by_name = {item.name: item for item in findings}
        coverage = by_name.get("shard_coverage")
        completion = by_name.get("shard_completion")
        reconciliation = by_name.get("record_reconciliation")
        covered = tuple(tuple(item) for item in  # type: ignore[misc]
                        (coverage.details.get("covered_ranges", []) if coverage else []))
        gaps = tuple(tuple(item) for item in  # type: ignore[misc]
                     (coverage.details.get("gaps", []) if coverage else []))
        exact = bool(coverage and coverage.details.get("covered_equals_declared"))
        if coverage is None or completion is None or reconciliation is None:
            reason = "incomplete_validation"
        elif not coverage.passed:
            reason = "shard_ranges_do_not_tile_declared_range"
        elif not exact:
            reason = "covered_range_differs_from_declared_range"
        elif not completion.passed:
            reason = "shards_still_outstanding"
        elif not reconciliation.passed:
            reason = "shard_record_counts_do_not_reconcile"
        else:
            reason = "declared_range_fully_discovered_and_reconciled"
        complete = reason == "declared_range_fully_discovered_and_reconciled"
        return CoverageClaim(complete, reason, declared, covered, gaps, observed)

    def _work_count(self) -> int:
        row = self._fetch_one(
            "SELECT COUNT(*) AS works FROM inspire_compact_work WHERE import_id = %s",
            (self.import_id,), ("works",))
        return _int(row[0]) if row else 0

    def validate(self) -> ValidationReport:
        low, high, _, _ = self.import_row()  # fails fast on an unknown candidate
        findings = [
            self.check_shard_coverage(),
            self.check_shard_completion(),
            self.check_record_reconciliation(),
            self.check_referential_integrity(),
            self.check_work_semantics(),
            self.check_duplicate_works(),
            self.check_year_sanity(),
            self.check_source_window(),
        ]
        span, works = self._observed_work_span()
        claim = self._coverage_claim(findings, (low, high), span)
        findings.append(self._coverage_finding(claim, works))
        by_name = {item.name: item for item in findings}

        source_complete = bool(
            claim.complete
            and by_name["shard_coverage"].passed
            and by_name["shard_completion"].passed
            and by_name["record_reconciliation"].passed)
        work_semantics = bool(
            by_name["work_semantics"].passed
            and by_name["referential_integrity"].passed
            and by_name["duplicate_works"].passed
            and by_name["year_sanity"].passed)
        gates = {gate: False for gate in _REQUIRED_GATES}
        gates["source_complete"] = source_complete
        gates["work_semantics_passed"] = work_semantics
        reasons = dict(_UNPROVABLE_GATES)
        if not source_complete:
            reasons["source_complete"] = claim.reason
        if not work_semantics:
            reasons["work_semantics_passed"] = "stored work rows contradict the schema's invariants"
        return ValidationReport(
            import_id=self.import_id,
            passed=all(item.passed for item in findings),
            findings=tuple(findings),
            gates=gates,
            gate_reasons=reasons,
            coverage=claim,
        )
