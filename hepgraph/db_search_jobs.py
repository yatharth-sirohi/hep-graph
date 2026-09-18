"""Durable, version-pinned shortest-path jobs over a compact graph import.

A serverless instance is frozen the moment it answers, so a multi-request proof
cannot live in a process-local object.  The live INSPIRE engine gets away with
it only because its session is inseparable from its paging cursors; a database
provider is deterministic, so the proof itself can be written down and picked up
by any instance.  That is what this module does: one row per search holding the
serialised HLBES state plus the version it was started against.

Version pinning is a mechanism here, not a policy.  The pinned import, overlay
and filter key are columns, and every slice re-checks them against the provider
it was handed.  A promotion or rollback mid-search therefore ends the job with
``graph_version_changed`` instead of quietly mixing two graphs, and a job
started after the pointer moved simply pins the new version.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import json
from typing import Any
from uuid import uuid4

from .graph import Filters
from .hlbes import (EXACT, NO_PATH, SEARCH_INCOMPLETE, VERIFIED, HLBES,
                    OracleStopped, Search, _Side)
from .neon_graph_provider import GraphDatabaseError
from .providers import ProviderOracle, filter_key


SCHEMA = """
CREATE TABLE IF NOT EXISTS graph_search_job (
    job_id TEXT PRIMARY KEY,
    import_id TEXT NOT NULL,
    overlay_id TEXT,
    schema_version TEXT NOT NULL,
    filter_key TEXT NOT NULL,
    filters JSONB NOT NULL,
    source TEXT NOT NULL,
    target TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('searching','settled','cancelled','failed')),
    state JSONB NOT NULL,
    outcome JSONB,
    sequence_number INTEGER NOT NULL DEFAULT 0,
    expansions INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS graph_search_job_expiry ON graph_search_job(expires_at);
"""

DEFAULT_SLICE_EXPANSIONS = 40
DEFAULT_MAX_EXPANSIONS = 4_000
DEFAULT_TTL_SECONDS = 1_200


class JobVersionChanged(RuntimeError):
    """The pinned graph moved under a running proof; the job fails closed."""


def serialise(state: Search) -> dict[str, Any]:
    """Everything needed to resume, and nothing whose meaning is process-local.

    ``seen_key`` is deliberately dropped: it holds ``hash()`` values that differ
    between interpreters.  Rebuilding it empty costs at most one extra expansion
    per parked node after a resume, while ``blocked`` - the decision that key
    produced - is persisted, so no node can silently unpark itself.
    """
    def side(value: _Side) -> dict[str, Any]:
        return {"root": value.root, "dist": value.dist, "parent": value.parent,
                "radius": value.radius, "complete": sorted(value.complete),
                "blocked": sorted(value.blocked), "expansions": value.expansions}

    # JSON has no infinity: an open upper bound is stored as null on the way
    # out and restored on the way back in, never as a number.
    return {"source": state.source, "target": state.target,
            "upper": _finite(state.upper),
            "lower": state.lower, "best": list(state.best) if state.best else None,
            "done": state.done, "reason": state.reason, "stalled": state.stalled,
            "conflict": state.conflict, "meetings": state.meetings,
            "expansions": state.expansions,
            "bounds": [[low, _finite(high)] for low, high in state.bounds[-32:]],
            "left": side(state.left), "right": side(state.right)}


def _finite(value: float) -> int | None:
    return None if value == float("inf") else int(value)


def _dump(payload: Any) -> str:
    """JSONB rejects Infinity and NaN, which HLBES stats legitimately carry.

    An open bound becomes null rather than a sentinel number, so nothing can
    later read it back as a real distance.
    """
    def clean(value: Any) -> Any:
        if isinstance(value, float):
            return None if value in (float("inf"), float("-inf")) or value != value else value
        if isinstance(value, dict):
            return {key: clean(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [clean(item) for item in value]
        return value

    return json.dumps(clean(payload), allow_nan=False)


def deserialise(payload: dict[str, Any]) -> Search:
    state = Search(payload["source"], payload["target"])
    state.upper = float("inf") if payload["upper"] is None else float(payload["upper"])
    state.lower = int(payload["lower"])
    state.best = tuple(payload["best"]) if payload["best"] else None
    state.done, state.reason = payload["done"], payload["reason"]
    state.stalled, state.conflict = bool(payload["stalled"]), bool(payload["conflict"])
    state.meetings, state.expansions = int(payload["meetings"]), int(payload["expansions"])
    state.bounds = [(int(low), float("inf") if high is None else float(high))
                    for low, high in payload["bounds"]]
    for side, stored in ((state.left, payload["left"]), (state.right, payload["right"])):
        side.dist = {key: int(value) for key, value in stored["dist"].items()}
        side.parent = dict(stored["parent"])
        side.levels = {}
        for node, distance in side.dist.items():
            side.levels.setdefault(distance, set()).add(node)
        side.radius = int(stored["radius"])
        side.complete = set(stored["complete"])
        side.blocked = set(stored["blocked"])
        side.expansions = int(stored["expansions"])
    return state


def classify(status: str, *, complete: bool, settled: bool) -> tuple[str, str, bool]:
    """Map a proof to (api_status, route_status, global_shortest_proven).

    An uncertified source may still witness a route, but it can never certify a
    *shortest* route or a *missing* one, so EXACT is reported as merely verified
    and NO_PATH becomes an incomplete search.
    """
    if status == EXACT and complete:
        return EXACT, "exact_route_proven", True
    if status == EXACT:
        return VERIFIED, "verified_route_found", False
    if status == VERIFIED:
        return VERIFIED, "verified_search_stopped" if settled else "verified_route_found", False
    if status == NO_PATH and complete:
        return NO_PATH, "no_path", False
    if status == NO_PATH:
        return SEARCH_INCOMPLETE, "search_incomplete", False
    return SEARCH_INCOMPLETE, "search_incomplete", False


@dataclass(frozen=True)
class JobPin:
    import_id: str
    overlay_id: str | None
    schema_version: str
    filter_key: str


class DatabaseSearchJobs:
    """Start, poll, continue and cancel proofs that outlive one request.

    ``provider_factory`` resolves the active pointer and returns a provider
    pinned to it.  It is called once per *new* search; a resumed search is
    served by ``provider_for`` for its own recorded pin, never the current one.
    """

    def __init__(self, connection: Any, *, provider_factory: Any,
                 provider_for: Any | None = None,
                 slice_expansions: int = DEFAULT_SLICE_EXPANSIONS,
                 max_expansions: int = DEFAULT_MAX_EXPANSIONS,
                 ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
        self.connection = connection
        self.provider_factory = provider_factory
        self.provider_for = provider_for or (lambda pin: provider_factory())
        self.slice_expansions = slice_expansions
        self.max_expansions = max_expansions
        self.ttl_seconds = ttl_seconds

    def ensure_schema(self) -> None:
        self.connection.execute(SCHEMA)

    # ------------------------------------------------------------------ public
    def start(self, source: str, target: str, filters: Filters) -> dict[str, Any]:
        provider = self.provider_factory()
        version = provider.get_graph_version()
        pin = JobPin(version.snapshot_id, self._overlay_id(provider),
                     version.schema_version, filter_key(filters))
        job_id = uuid4().hex
        state = HLBES(ProviderOracle(provider, filters)).begin(str(source), str(target))
        # An endpoint the graph has never heard of would otherwise let the
        # opposite side exhaust its component and settle NO_PATH, which would
        # read as "these two are unconnected" rather than "we do not know this
        # person". Decide it here instead, before any expansion.
        missing = [str(node) for node in (source, target)
                   if provider.resolve_author(str(node)) is None]
        self.connection.execute(
            "INSERT INTO graph_search_job(job_id,import_id,overlay_id,schema_version,filter_key,"
            "filters,source,target,status,state,outcome,expires_at) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (job_id, pin.import_id, pin.overlay_id, pin.schema_version, pin.filter_key,
             _dump(filters.to_dict()), str(source), str(target),
             "settled" if missing else "searching",
             _dump(serialise(state)),
             _dump(self._unresolved(provider, filters, missing)) if missing else None,
             datetime.now(UTC) + timedelta(seconds=self.ttl_seconds)))
        if missing:
            return self._record(self._row(job_id))
        return self._advance(job_id, provider)

    def _unresolved(self, provider: Any, filters: Filters,
                    missing: list[str]) -> dict[str, Any]:
        version = provider.get_graph_version()
        return {"proof_status": SEARCH_INCOMPLETE, "route_status": "search_incomplete",
                "global_shortest_proven": False, "exact": False, "provisional": False,
                "paths": [], "reason": "author_not_in_graph",
                "unresolved_endpoints": missing,
                "message": "This person is not in the pinned graph version, which is not "
                           "evidence that they are absent from INSPIRE.",
                "graph_snapshot": version.snapshot_id,
                "source_cutoff": version.source_cutoff,
                "schema_version": version.schema_version,
                "coverage": provider.coverage.to_dict() if hasattr(provider, "coverage") else {}}

    def get(self, job_id: str) -> dict[str, Any]:
        return self._advance(job_id, None)

    def resume(self, job_id: str) -> dict[str, Any]:
        row = self._row(job_id)
        if row is None:
            raise KeyError(job_id)
        if row["status"] == "settled" and (row["outcome"] or {}).get("global_shortest_proven"):
            return self._record(row)
        if row["status"] in {"cancelled", "failed"}:
            return self._record(row)
        self.connection.execute(
            "UPDATE graph_search_job SET status='searching',updated_at=now(),expires_at=%s "
            "WHERE job_id=%s AND status<>'cancelled'",
            (datetime.now(UTC) + timedelta(seconds=self.ttl_seconds), job_id))
        return self._advance(job_id, None)

    def cancel(self, job_id: str) -> dict[str, Any]:
        row = self._row(job_id)
        if row is None:
            raise KeyError(job_id)
        # A proven result is never relabelled by a cancel that arrives late.
        if row["status"] != "settled":
            self.connection.execute(
                "UPDATE graph_search_job SET status='cancelled',updated_at=now() WHERE job_id=%s",
                (job_id,))
        return self._record(self._row(job_id))

    def prune(self) -> int:
        rows = self.connection.execute(
            "DELETE FROM graph_search_job WHERE expires_at < now() RETURNING job_id").fetchall()
        return len(rows)

    # --------------------------------------------------------------- mechanics
    @staticmethod
    def _overlay_id(provider: Any) -> str | None:
        overlay = getattr(provider, "overlay", None)
        return overlay.overlay_id if overlay is not None else None

    def _row(self, job_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            "SELECT * FROM graph_search_job WHERE job_id=%s", (job_id,)).fetchone()
        return dict(row) if row is not None else None

    def _advance(self, job_id: str, provider: Any | None) -> dict[str, Any]:
        row = self._row(job_id)
        if row is None:
            raise KeyError(job_id)
        if row["status"] in {"cancelled", "failed", "settled"}:
            return self._record(row)
        pin = JobPin(row["import_id"], row["overlay_id"], row["schema_version"], row["filter_key"])
        filters = Filters.from_dict(dict(row["filters"]))
        if provider is None:
            provider = self.provider_for(pin)
        try:
            self._check_pin(provider, pin, filters)
        except JobVersionChanged as changed:
            return self._fail(row, "graph_version_changed", str(changed))
        state = deserialise(dict(row["state"]))
        engine = HLBES(ProviderOracle(provider, filters),
                       max_expansions=min(state.expansions + self.slice_expansions,
                                          self.max_expansions))
        try:
            while engine.advance(state):
                pass
        except OracleStopped as stop:
            state.reason = stop.reason
        except GraphDatabaseError as error:
            # An unreachable store is reported, never mistaken for an answer.
            return self._fail(row, "database_unavailable", error.message)
        complete = provider.get_completeness(filters)
        settled = state.done is not None or state.expansions >= self.max_expansions
        if state.conflict:
            return self._fail(row, "graph_conflict",
                              "the proof rests on adjacency that has since changed")
        result = HLBES.result(state)
        outcome = self._outcome(provider, filters, result, complete=complete, settled=settled)
        self.connection.execute(
            "UPDATE graph_search_job SET state=%s,outcome=%s,status=%s,"
            "sequence_number=sequence_number+1,expansions=%s,updated_at=now() WHERE job_id=%s",
            (_dump(serialise(state)), _dump(outcome),
             "settled" if settled else "searching", state.expansions, job_id))
        return self._record(self._row(job_id))

    def _check_pin(self, provider: Any, pin: JobPin, filters: Filters) -> None:
        version = provider.get_graph_version()
        current = JobPin(version.snapshot_id, self._overlay_id(provider),
                         version.schema_version, filter_key(filters))
        if current != pin:
            raise JobVersionChanged(
                f"job pinned {pin.import_id}/{pin.overlay_id}/{pin.schema_version} "
                f"but the provider serves {current.import_id}/{current.overlay_id}/"
                f"{current.schema_version}")

    def _outcome(self, provider: Any, filters: Filters, result: Any, *,
                 complete: bool, settled: bool) -> dict[str, Any]:
        status, route_status, proven = classify(result.status, complete=complete, settled=settled)
        if not settled and result.path is None:
            status, route_status = SEARCH_INCOMPLETE, "searching_no_path"
        coverage = provider.coverage.to_dict() if hasattr(provider, "coverage") else {}
        version = provider.get_graph_version()
        paths: list[dict[str, Any]] = []
        if result.path:
            paths.append({
                "hops": len(result.path) - 1,
                "people": [{"id": node} for node in result.path],
                "edges": [{"source": a, "target": b,
                           "evidence_refs": list(provider.get_edge_evidence_refs(a, b, filters))}
                          for a, b in zip(result.path, result.path[1:])],
                "provisional": not settled,
            })
        return {
            "proof_status": status, "route_status": route_status,
            "global_shortest_proven": proven,
            "exact": proven,
            "provisional": not settled,
            "paths": paths,
            "distance": result.distance,
            "bounds": {"lower": result.lower_bound,
                       "upper": None if result.upper_bound == float("inf") else int(result.upper_bound)},
            "reason": result.reason,
            "graph_snapshot": version.snapshot_id,
            "source_cutoff": version.source_cutoff,
            "schema_version": version.schema_version,
            "coverage": coverage,
            "completeness_reason": provider.incompleteness_reason(filters)
            if hasattr(provider, "incompleteness_reason") else "",
            "stats": result.stats,
        }

    def _fail(self, row: dict[str, Any], reason: str, message: str) -> dict[str, Any]:
        self.connection.execute(
            "UPDATE graph_search_job SET status='failed',outcome=%s,"
            "sequence_number=sequence_number+1,updated_at=now() WHERE job_id=%s",
            (_dump({"proof_status": SEARCH_INCOMPLETE, "route_status": "search_incomplete",
                         "global_shortest_proven": False, "exact": False, "paths": [],
                         "reason": reason, "message": message}), row["job_id"]))
        return self._record(self._row(row["job_id"]))

    def _record(self, row: dict[str, Any]) -> dict[str, Any]:
        """``status`` is the job's lifecycle; ``proof_status`` is what was proved.

        Keeping them apart is what stops a late cancel from relabelling a proven
        route, or an incomplete proof from looking like a dead job.
        """
        outcome = dict(row["outcome"] or {})
        running = row["status"] == "searching"
        # Continuing cannot help a search whose endpoint is not in the graph or
        # whose version moved; only an unfinished proof is worth resuming.
        resumable = outcome.get("reason") not in {"author_not_in_graph",
                                                  "graph_version_changed",
                                                  "graph_conflict"}
        record = {
            "job_id": row["job_id"], "mode": "database",
            "version": f"graph-db:{row['import_id']}",
            "graph_snapshot": row["import_id"], "overlay_id": row["overlay_id"],
            "schema_version": row["schema_version"],
            "filters": dict(row["filters"]),
            "source": row["source"], "target": row["target"],
            "status": "searching" if running else row["status"],
            "sequence_number": row["sequence_number"],
            "can_continue": resumable and (running or (
                row["status"] == "settled"
                and not outcome.get("global_shortest_proven", False))),
            "progress": {"expansions": row["expansions"],
                         "stage": "continue_search" if running else "finished"},
        }
        record.update(outcome)
        if record.get("paths"):
            best = record["paths"][0]
            record["best_route"] = {"hops": best["hops"], "provisional": best.get("provisional", False)}
        return record
