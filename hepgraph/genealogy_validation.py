"""Independent checks before a genealogy overlay may be certified.

Certifying an overlay is not a formality. A neighborhood that includes doctoral
edges can only be COMPLETE if the overlay holds *every* such edge INSPIRE
publishes; otherwise HLBES would advance a completed radius through a graph
that is missing edges, and prove a shortest route that is not one.

So completeness here means one specific, checkable thing: every INSPIRE author
record carrying an adviser with a record reference was fetched and reconciled.
It deliberately does **not** mean INSPIRE knows everyone's adviser - it does not,
and that gap is reported rather than certified away.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .neon_graph_provider import _at


#: Bounded so a broken overlay reports examples instead of dumping the table.
EXAMPLE_LIMIT = 5


@dataclass(frozen=True)
class Finding:
    name: str
    passed: bool
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OverlayReport:
    overlay_id: str
    passed: bool
    findings: tuple[Finding, ...]
    limitations: tuple[str, ...]

    def failures(self) -> tuple[Finding, ...]:
        return tuple(item for item in self.findings if not item.passed)

    def as_dict(self) -> dict[str, Any]:
        return {"overlay_id": self.overlay_id, "passed": self.passed,
                "findings": [{"name": f.name, "passed": f.passed, "details": f.details}
                             for f in self.findings],
                "limitations": list(self.limitations)}


class GenealogyOverlayValidator:
    """Read-only auditor. It never writes and never certifies by itself."""

    LIMITATIONS = (
        "INSPIRE records an adviser for only a small fraction of its authors; a "
        "person with no edge here may simply have no adviser recorded upstream.",
        "An adviser given only as a name, with no INSPIRE record, cannot become an "
        "edge and is excluded rather than matched by name.",
        "Only relations INSPIRE typed as doctoral are traversable; relations it left "
        "untyped are stored but are not doctoral evidence.",
        "Adviser relations carry no date in this schema, so a lineage cannot be "
        "checked against a plausible chronology.",
    )

    def __init__(self, connection: Any, overlay_id: str, *, import_id: str,
                 thesis_import_id: str | None = None) -> None:
        self.connection = connection
        self.overlay_id = overlay_id
        self.import_id = import_id
        #: Supervisors read from thesis records are a second crawl feeding the
        #: same overlay; when present it must reconcile too.
        self.thesis_import_id = thesis_import_id

    def _one(self, sql: str, params: tuple[Any, ...] = ()) -> Any:
        row = self.connection.execute(sql, params).fetchone()
        if row is None:
            return None
        return row[0] if not isinstance(row, dict) else list(row.values())[0]

    def check_registered(self) -> Finding:
        row = self.connection.execute(
            "SELECT source_description, certified_complete FROM graph_genealogy_overlay "
            "WHERE overlay_id=%s", (self.overlay_id,)).fetchone()
        return Finding("overlay_registered", row is not None,
                       {"overlay_id": self.overlay_id, "present": row is not None})

    def check_crawl_reconciled(self) -> Finding:
        """Every crawl feeding the overlay must be finished and add up."""
        details: dict[str, Any] = {}
        passed = True
        for import_id in filter(None, (self.import_id, self.thesis_import_id)):
            outstanding = self._one(
                "SELECT count(*) FROM inspire_compact_shard WHERE import_id=%s "
                "AND status NOT IN ('DONE','SPLIT')", (import_id,))
            shards = self._one(
                "SELECT count(*) FROM inspire_compact_shard WHERE import_id=%s", (import_id,))
            mismatched = self.connection.execute(
                "SELECT low_recid, high_recid, expected_records, received_records "
                "FROM inspire_compact_shard WHERE import_id=%s AND status='DONE' "
                "AND received_records <> expected_records LIMIT %s",
                (import_id, EXAMPLE_LIMIT)).fetchall()
            expected = self._one(
                "SELECT COALESCE(sum(expected_records),0) FROM inspire_compact_shard "
                "WHERE import_id=%s AND status='DONE'", (import_id,))
            passed = passed and bool(shards) and outstanding == 0 and not mismatched
            details[import_id] = {"outstanding_shards": outstanding,
                                  "records_expected": int(expected or 0),
                                  "mismatched_shards": [[_at(row, i) for i in range(4)]
                                                        for row in mismatched]}
        return Finding("crawl_reconciled", passed, details)

    def check_no_self_relations(self) -> Finding:
        count = self._one(
            "SELECT count(*) FROM graph_genealogy_edge WHERE overlay_id=%s "
            "AND adviser_id = student_id", (self.overlay_id,))
        return Finding("no_self_relations", count == 0, {"self_relations": count})

    def check_edges_present(self) -> Finding:
        edges = self._one("SELECT count(*) FROM graph_genealogy_edge WHERE overlay_id=%s",
                          (self.overlay_id,))
        doctoral = self._one(
            "SELECT count(*) FROM graph_genealogy_edge WHERE overlay_id=%s AND degree='phd'",
            (self.overlay_id,))
        return Finding("edges_present", bool(edges) and bool(doctoral),
                       {"edges": edges, "doctoral_edges": doctoral})

    def check_degrees_known(self) -> Finding:
        """Every stored degree should be a value the traversal rule can reason about."""
        rows = self.connection.execute(
            "SELECT COALESCE(degree,'(untyped)') AS degree, count(*) AS n "
            "FROM graph_genealogy_edge WHERE overlay_id=%s GROUP BY 1 ORDER BY n DESC",
            (self.overlay_id,)).fetchall()
        spread = {str(_at(row, 0)): int(_at(row, 1)) for row in rows}
        return Finding("degrees_known", bool(spread), {"degree_spread": spread})

    def check_lineage_acyclic(self) -> Finding:
        """A doctoral chain that returns to its start would loop a lineage walk.

        Checked exactly over the whole relation rather than by a bounded walk,
        because a loop longer than any walk bound would otherwise pass.
        """
        from .genealogy_import import find_cycle

        pairs = [(int(_at(row, 0)), int(_at(row, 1))) for row in self.connection.execute(
            "SELECT DISTINCT adviser_id, student_id FROM graph_genealogy_edge "
            "WHERE overlay_id=%s AND degree='phd'", (self.overlay_id,)).fetchall()]
        loop = find_cycle(pairs)
        return Finding("lineage_acyclic", loop is None,
                       {"example_loop": loop[:EXAMPLE_LIMIT * 2] if loop else []})

    def validate(self) -> OverlayReport:
        findings = (self.check_registered(), self.check_crawl_reconciled(),
                    self.check_edges_present(), self.check_no_self_relations(),
                    self.check_degrees_known(), self.check_lineage_acyclic())
        return OverlayReport(self.overlay_id, all(item.passed for item in findings),
                             findings, self.LIMITATIONS)
