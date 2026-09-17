"""Read-only graph provider over one pinned compact PostgreSQL import.

Adjacency is computed from the work-author incidence tables, never from a
materialised pair table: one 2,932-author collaboration would be 4.3M pairs on
its own.  Every query is parameterised, bounded and ordered deterministically.

The three honesty rules this module exists to enforce:

* An infrastructure failure raises :class:`GraphDatabaseError`.  It is never a
  neighborhood, and above all never an *empty complete* one, because HLBES
  treats a COMPLETE neighborhood as proof and would turn a dropped connection
  into a false ``no_path``.
* An author the import has never seen is UNKNOWN, not absent.  A partial import
  says nothing about INSPIRE.
* COMPLETE requires an external certificate (:class:`CoverageClaim`), not the
  importer's own opinion that it finished.  Traversal filters only ever select a
  subset of a certified universe, so they preserve a completeness claim; a
  missing *edge class* such as genealogy destroys it, because the neighborhood
  would be missing edges rather than merely filtered ones.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .graph import Filters
from .hlbes import COMPLETE, PARTIAL, UNKNOWN
from .providers import GraphVersion, ProviderNeighborhood, filter_key


SCHEMA_VERSION = "neon-compact-incidence-v1"

#: Resolved author slots read while building one batch of neighborhoods.  A
#: neighborhood over this bound is reported PARTIAL rather than streamed into
#: the function instance, so one hub author cannot exhaust serverless memory.
DEFAULT_MEMBER_VISIT_BUDGET = 2_000_000
DEFAULT_STATEMENT_TIMEOUT_MS = 15_000


class GraphDatabaseError(RuntimeError):
    """The graph store could not answer. Never convertible to an empty result."""

    def __init__(self, reason: str, message: str = "") -> None:
        super().__init__(message or reason)
        self.reason, self.message = reason, message or reason


@dataclass(frozen=True)
class GenealogyOverlay:
    """A separately sourced, separately versioned doctoral edge set.

    Doctoral records are not collaboration topology and are not carried by the
    compact import, so they arrive as an overlay with its own certificate.
    """

    overlay_id: str
    certified_complete: bool = False


@dataclass(frozen=True)
class CoverageClaim:
    """What one import may claim, decided outside the importer.

    ``certified_complete`` is only ever set from an independent validation
    report.  ``shards_outstanding`` and the observed span are recorded so the
    API can describe coverage instead of implying a whole-INSPIRE view.
    """

    import_id: str
    source_cutoff: str | None = None
    declared_low: int | None = None
    declared_high: int | None = None
    observed_low: int | None = None
    observed_high: int | None = None
    shards_outstanding: int | None = None
    works: int | None = None
    certified_complete: bool = False
    reason: str = "not_certified"

    def to_dict(self) -> dict[str, Any]:
        return {
            "import_id": self.import_id, "source_cutoff": self.source_cutoff,
            "declared_recid_range": [self.declared_low, self.declared_high],
            "observed_recid_range": [self.observed_low, self.observed_high],
            "shards_outstanding": self.shards_outstanding, "works": self.works,
            "certified_complete": self.certified_complete, "reason": self.reason,
        }


def observe_coverage(connection: Any, import_id: str) -> CoverageClaim:
    """Read-only description of an import. It certifies nothing by itself."""
    try:
        header = connection.execute(
            "SELECT source_cutoff, low_recid, high_recid FROM inspire_compact_import "
            "WHERE import_id=%s", (import_id,)).fetchone()
        if header is None:
            raise GraphDatabaseError("unknown_import", f"no compact import {import_id!r}")
        outstanding = connection.execute(
            "SELECT count(*) FROM inspire_compact_shard WHERE import_id=%s "
            "AND status <> 'DONE' AND status <> 'SPLIT'", (import_id,)).fetchone()
        span = connection.execute(
            "SELECT min(work_id), max(work_id), count(*) FROM inspire_compact_work "
            "WHERE import_id=%s", (import_id,)).fetchone()
    except GraphDatabaseError:
        raise
    except Exception as exc:  # psycopg errors must not look like empty coverage
        raise GraphDatabaseError("database_unavailable", str(exc)) from exc
    cutoff, low, high = _row(header, ("source_cutoff", "low_recid", "high_recid"))
    return CoverageClaim(
        import_id=import_id,
        source_cutoff=cutoff.isoformat() if hasattr(cutoff, "isoformat") else (
            str(cutoff) if cutoff is not None else None),
        declared_low=low, declared_high=high,
        observed_low=_at(span, 0), observed_high=_at(span, 1), works=_at(span, 2),
        shards_outstanding=_at(outstanding, 0),
        certified_complete=False, reason="not_certified")


def _row(row: Any, keys: tuple[str, ...]) -> tuple[Any, ...]:
    """Accept both dict_row and tuple cursors so callers can pick either."""
    if isinstance(row, dict):
        return tuple(row[key] for key in keys)
    return tuple(row[index] for index in range(len(keys)))


def _at(row: Any, index: int) -> Any:
    if row is None:
        return None
    if isinstance(row, dict):
        return list(row.values())[index]
    return row[index]


def connect_read_only(url: str, *, statement_timeout_ms: int = DEFAULT_STATEMENT_TIMEOUT_MS) -> Any:
    """Open a serving connection that cannot write and cannot hang forever.

    Read-only is set on the session as defence in depth; the deployed serving
    credential should also be read-only at the database level.
    """
    import psycopg

    # dict rows: the job engine reads its record by column name.
    connection = psycopg.connect(url, autocommit=True, row_factory=psycopg.rows.dict_row)
    connection.execute("SET default_transaction_read_only = on")
    # SET takes no bound parameters, so the value goes through set_config rather
    # than being interpolated into the statement.
    connection.execute("SELECT set_config('statement_timeout', %s, false)",
                       (str(int(statement_timeout_ms)),))
    connection.execute("SELECT set_config('idle_in_transaction_session_timeout', %s, false)",
                       (str(int(statement_timeout_ms)),))
    return connection


class NeonCompactGraphProvider:
    """One pinned import, served read-only. Satisfies ``GraphProvider``.

    The instance never re-reads the active pointer: the caller resolves it once
    when a search is created and keeps this object for that search's whole life,
    so a promotion cannot change the graph under a running proof.
    """

    def __init__(self, connection: Any, *, coverage: CoverageClaim,
                 genealogy_overlay: GenealogyOverlay | None = None,
                 member_visit_budget: int = DEFAULT_MEMBER_VISIT_BUDGET,
                 max_batch: int = 64) -> None:
        if not coverage.import_id:
            raise ValueError("a pinned import_id is required")
        self.connection = connection
        self.coverage = coverage
        self.import_id = coverage.import_id
        self.overlay = genealogy_overlay
        self.member_visit_budget = member_visit_budget
        self.max_batch = max(1, max_batch)
        self.version = GraphVersion(coverage.import_id, coverage.source_cutoff, SCHEMA_VERSION)
        self.queries = 0

    # ------------------------------------------------------------------ plumbing
    def _execute(self, sql: str, params: dict[str, Any]) -> list[Any]:
        try:
            self.queries += 1
            return self.connection.execute(sql, params).fetchall()
        except GraphDatabaseError:
            raise
        except Exception as exc:
            raise GraphDatabaseError("database_unavailable", str(exc)) from exc

    def _filter_params(self, filters: Filters) -> dict[str, Any]:
        return {"import_id": self.import_id,
                "min_authors": filters.min_authors, "max_authors": filters.max_authors,
                "year_start": filters.year_start, "year_end": filters.year_end,
                "min_shared": filters.min_shared}

    #: Eligibility already applied at import time (document type, erratum
    #: titles, author_count >= 2) cannot be re-derived here, so it is pinned by
    #: schema version rather than re-checked per query.
    _QUALIFYING = """
        SELECT a.anchor, m.work_id, w.member_count
        FROM anchors a
        JOIN inspire_compact_membership m
          ON m.import_id = %(import_id)s AND m.author_id = a.anchor
        JOIN inspire_compact_work w
          ON w.import_id = %(import_id)s AND w.work_id = m.work_id
        WHERE w.author_count >= %(min_authors)s
          AND (%(max_authors)s::int IS NULL OR w.author_count <= %(max_authors)s::int)
          AND (%(year_start)s::int IS NULL
               OR (w.year IS NOT NULL AND w.year >= %(year_start)s::int))
          AND (%(year_end)s::int IS NULL
               OR (w.year IS NOT NULL AND w.year <= %(year_end)s::int))
    """

    # ------------------------------------------------------------------ contract
    def get_graph_version(self) -> GraphVersion:
        return self.version

    def get_completeness(self, filters: Filters) -> bool:
        """Filters subset a certified universe; a missing edge class does not."""
        if not self.coverage.certified_complete:
            return False
        if filters.genealogy:
            return self.overlay is not None and self.overlay.certified_complete
        return True

    def incompleteness_reason(self, filters: Filters) -> str:
        if not self.coverage.certified_complete:
            return self.coverage.reason or "import_not_certified"
        if filters.genealogy and (self.overlay is None or not self.overlay.certified_complete):
            return "genealogy_overlay_uncertified"
        return ""

    def resolve_author(self, author_id: str) -> dict[str, Any] | None:
        """Presence in this import only. Absence is never absence from INSPIRE."""
        try:
            anchor = int(str(author_id))
        except (TypeError, ValueError):
            return None
        rows = self._execute(
            "SELECT 1 FROM inspire_compact_membership "
            "WHERE import_id=%(import_id)s AND author_id=%(author_id)s LIMIT 1",
            {"import_id": self.import_id, "author_id": anchor})
        if rows:
            return {"id": str(anchor), "source": "compact_import",
                    "source_url": f"https://inspirehep.net/authors/{anchor}"}
        if self.overlay is not None:
            rows = self._execute(
                "SELECT 1 FROM graph_genealogy_edge WHERE overlay_id=%(overlay_id)s "
                "AND (adviser_id=%(author_id)s OR student_id=%(author_id)s) LIMIT 1",
                {"overlay_id": self.overlay.overlay_id, "author_id": anchor})
            if rows:
                return {"id": str(anchor), "source": "genealogy_overlay",
                        "source_url": f"https://inspirehep.net/authors/{anchor}"}
        return None

    def get_neighbors(self, author_id: str, filters: Filters) -> ProviderNeighborhood:
        return self.get_neighbors_batch((str(author_id),), filters)[str(author_id)]

    def get_neighbors_batch(self, author_ids: tuple[str, ...],
                            filters: Filters) -> dict[str, ProviderNeighborhood]:
        """Two round trips per batch; a hub author degrades to PARTIAL, not OOM."""
        key = filter_key(filters)
        wanted = [str(author_id) for author_id in author_ids]
        anchors: list[int] = []
        results: dict[str, ProviderNeighborhood] = {}
        for author_id in wanted:
            try:
                anchors.append(int(author_id))
            except (TypeError, ValueError):
                results[author_id] = self._unknown(key, "invalid_author_id")
        for start in range(0, len(anchors), self.max_batch):
            self._batch(anchors[start:start + self.max_batch], filters, key, results)
        return {author_id: results.get(author_id, self._unknown(key, "author_not_in_import"))
                for author_id in wanted}

    def _batch(self, anchors: list[int], filters: Filters, key: str,
               results: dict[str, ProviderNeighborhood]) -> None:
        if not anchors:
            return
        params = self._filter_params(filters) | {"anchors": anchors}
        # Presence and cost in one trip. Presence must be asked separately from
        # the qualifying join: an author whose every work is filtered out still
        # exists, and must not be reported as unknown to the import.  Cost is
        # counted before the neighbor join runs, so an oversized neighborhood is
        # declined rather than materialised and then discarded.
        probe = self._execute(
            f"WITH anchors AS (SELECT unnest(%(anchors)s::bigint[]) AS anchor), "
            f"qualifying AS ({self._QUALIFYING}) "
            "SELECT a.anchor, "
            "  EXISTS (SELECT 1 FROM inspire_compact_membership p "
            "          WHERE p.import_id=%(import_id)s AND p.author_id=a.anchor) AS present, "
            "  COALESCE(sum(q.member_count),0) AS visits "
            "FROM anchors a LEFT JOIN qualifying q ON q.anchor = a.anchor "
            "GROUP BY a.anchor ORDER BY a.anchor", params)
        present, cost = set(), {}
        for row in probe:
            name = str(_at(row, 0))
            if _at(row, 1):
                present.add(name)
            cost[name] = int(_at(row, 2) or 0)
        affordable = [anchor for anchor in anchors
                      if str(anchor) in present
                      and cost.get(str(anchor), 0) <= self.member_visit_budget]
        overspent = {str(anchor) for anchor in anchors} - {str(anchor) for anchor in affordable}
        for anchor in anchors:
            name = str(anchor)
            if name not in present:
                results[name] = self._unknown(key, "author_not_in_import")
            elif name in overspent:
                # Deterministic token: a repeated call returns the same key, so
                # HLBES parks the node instead of spinning on it forever.
                results[name] = ProviderNeighborhood(
                    self.version, key, frozenset(), PARTIAL,
                    "member_visit_budget_exceeded", cursor="budget")
        if not affordable:
            return
        params = params | {"anchors": affordable}
        rows = self._execute(
            f"WITH anchors AS (SELECT unnest(%(anchors)s::bigint[]) AS anchor), "
            f"qualifying AS ({self._QUALIFYING}) "
            "SELECT q.anchor, m.author_id, count(*) AS shared "
            "FROM qualifying q "
            "JOIN inspire_compact_membership m "
            "  ON m.import_id = %(import_id)s AND m.work_id = q.work_id "
            "WHERE m.author_id <> q.anchor "
            "GROUP BY q.anchor, m.author_id "
            "HAVING count(*) >= %(min_shared)s "
            "ORDER BY q.anchor, m.author_id", params)
        found: dict[str, set[str]] = {str(anchor): set() for anchor in affordable}
        for row in rows:
            # The membership primary key makes one row per (work, author), so
            # this count is already a count of *distinct* shared works.
            found[str(_at(row, 0))].add(str(_at(row, 1)))
        if filters.genealogy and self.overlay is not None:
            for anchor, other in self._genealogy(affordable):
                found.setdefault(anchor, set()).add(other)
        reason = self.incompleteness_reason(filters)
        complete = self.get_completeness(filters)
        for anchor, members in found.items():
            results[anchor] = ProviderNeighborhood(
                self.version, key, frozenset(members),
                COMPLETE if complete else PARTIAL, "" if complete else reason,
                cursor="complete" if complete else reason)

    def _genealogy(self, anchors: list[int]) -> list[tuple[str, str]]:
        if self.overlay is None:
            return []
        rows = self._execute(
            "SELECT adviser_id, student_id FROM graph_genealogy_edge "
            "WHERE overlay_id=%(overlay_id)s AND (adviser_id = ANY(%(anchors)s) "
            "OR student_id = ANY(%(anchors)s)) ORDER BY adviser_id, student_id",
            {"overlay_id": self.overlay.overlay_id, "anchors": anchors})
        wanted = {str(anchor) for anchor in anchors}
        edges: list[tuple[str, str]] = []
        for row in rows:
            adviser, student = str(_at(row, 0)), str(_at(row, 1))
            if adviser in wanted:
                edges.append((adviser, student))
            if student in wanted:
                edges.append((student, adviser))
        return edges

    def _unknown(self, key: str, reason: str) -> ProviderNeighborhood:
        return ProviderNeighborhood(self.version, key, frozenset(), UNKNOWN, reason,
                                    cursor=reason)

    def get_edge_evidence_refs(self, source: str, target: str,
                               filters: Filters) -> tuple[str, ...]:
        """Stable, ordered refs. Display metadata is hydrated separately."""
        try:
            anchor, other = int(str(source)), int(str(target))
        except (TypeError, ValueError):
            return ()
        params = self._filter_params(filters) | {"anchors": [anchor], "other": other}
        rows = self._execute(
            f"WITH anchors AS (SELECT unnest(%(anchors)s::bigint[]) AS anchor), "
            f"qualifying AS ({self._QUALIFYING}) "
            "SELECT q.work_id FROM qualifying q "
            "JOIN inspire_compact_membership m "
            "  ON m.import_id = %(import_id)s AND m.work_id = q.work_id "
            "     AND m.author_id = %(other)s "
            "ORDER BY q.work_id", params)
        works = [str(_at(row, 0)) for row in rows]
        refs = [f"work:{work_id}" for work_id in works] if len(works) >= filters.min_shared else []
        if filters.genealogy and self.overlay is not None:
            refs.extend(f"phd:{_at(row, 0)}" for row in self._execute(
                "SELECT source_record FROM graph_genealogy_edge WHERE overlay_id=%(overlay_id)s "
                "AND ((adviser_id=%(a)s AND student_id=%(b)s) "
                "  OR (adviser_id=%(b)s AND student_id=%(a)s)) ORDER BY source_record",
                {"overlay_id": self.overlay.overlay_id, "a": anchor, "b": other}))
        return tuple(refs)

    def get_work_metadata(self, work_id: str) -> dict[str, Any] | None:
        """Structure only. Titles and dates come from post-route hydration."""
        try:
            identifier = int(str(work_id))
        except (TypeError, ValueError):
            return None
        rows = self._execute(
            "SELECT work_id, year, author_count, member_count FROM inspire_compact_work "
            "WHERE import_id=%(import_id)s AND work_id=%(work_id)s",
            {"import_id": self.import_id, "work_id": identifier})
        if not rows:
            return None
        work, year, author_count, member_count = (_at(rows[0], index) for index in range(4))
        return {"id": str(work), "year": year, "author_count": author_count,
                "resolved_author_count": member_count,
                "source_url": f"https://inspirehep.net/literature/{work}",
                "details_available": False}
