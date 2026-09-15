"""Small, bounded cache warm-ups for explicitly selected live authors.

Preparation never builds a graph or writes records.  It performs exactly the
three requests that the beginning of a deep search can reuse: the selected
profile, its author facet, and the first filtered literature page.
"""
from __future__ import annotations

from collections import Counter, OrderedDict
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import dataclass, field
import json
import re
import threading
import time
import uuid
from typing import Any

from .deep_search import PROFILE_PAGE_SIZE, DeepBudget, DeepSession
from .graph import Filters


class PreparationError(ValueError):
    def __init__(self, code: str, message: str, http_status: int = 400) -> None:
        super().__init__(message)
        self.code, self.message, self.http_status = code, message, http_status


@dataclass
class _Preparation:
    id: str
    person: str
    filters: Filters
    key: tuple[str, str]
    queued_at: float
    status: str = "queued"
    started_at: float | None = None
    finished_at: float | None = None
    warmed: list[str] = field(default_factory=list)
    failures: list[dict[str, str]] = field(default_factory=list)


class PreparationJobs:
    """A fixed worker pool with a small explicit queue and retained statuses."""

    def __init__(
        self,
        client: Any,
        *,
        max_active: int = 2,
        max_pending: int = 8,
        max_retained: int = 32,
        ttl: float = 10 * 60,
        clock=time.monotonic,
    ) -> None:
        if (isinstance(max_active, bool) or not isinstance(max_active, int) or not 1 <= max_active <= 2
                or isinstance(max_pending, bool) or not isinstance(max_pending, int) or not 1 <= max_pending <= 32
                or isinstance(max_retained, bool) or not isinstance(max_retained, int) or not max_active <= max_retained <= 128
                or isinstance(ttl, bool) or not isinstance(ttl, (int, float)) or not 1 <= ttl <= 3600):
            raise ValueError("Invalid preparation limits.")
        self.client = client
        self.max_active = max_active
        self.max_pending = max_pending
        self.max_retained = max_retained
        self.ttl = float(ttl)
        self.clock = clock
        self.lock = threading.RLock()
        self.jobs: OrderedDict[str, _Preparation] = OrderedDict()
        self.executor = ThreadPoolExecutor(max_workers=max_active, thread_name_prefix="hep-prepare")
        self.closed = False
        self.stop = threading.Event()
        self.counters: Counter[str] = Counter()

    @staticmethod
    def _key(person: str, filters: Filters) -> tuple[str, str]:
        # Direction is irrelevant for one selected profile.  A canonical JSON
        # filter key naturally includes new filter fields such as min_authors.
        return person, json.dumps(filters.to_dict(), sort_keys=True, separators=(",", ":"))

    @staticmethod
    def _literature_size(filters: Filters) -> int:
        page_size = DeepBudget.standard().page_size
        return min(5, page_size) if filters.max_authors is None or filters.max_authors > 100 else page_size

    @staticmethod
    def _has_exact_current_identity(response: Any, person: str) -> bool:
        """Require the exact requested, non-deleted numeric profile record."""
        container = response.get("hits") if isinstance(response, dict) else None
        hits = container.get("hits") if isinstance(container, dict) else None
        if not isinstance(hits, list):
            return False
        for hit in hits:
            metadata = hit.get("metadata") if isinstance(hit, dict) else None
            if not isinstance(metadata, dict):
                continue
            if (hit.get("id") == person and metadata.get("control_number") == person
                    and metadata.get("deleted") is not True):
                return True
        return False

    def _prune(self, *, make_room: bool = False) -> None:
        now = self.clock()
        for job_id, job in list(self.jobs.items()):
            if job.finished_at is not None and now - job.finished_at >= self.ttl:
                del self.jobs[job_id]
                self.counters["expired"] += 1
        while len(self.jobs) > self.max_retained or (make_room and len(self.jobs) >= self.max_retained):
            removable = next((job_id for job_id, job in self.jobs.items() if job.finished_at is not None), None)
            if removable is None:
                break
            del self.jobs[removable]
            self.counters["evicted"] += 1

    def _public(self, job: _Preparation, *, reused: bool = False) -> dict[str, Any]:
        return {
            "preparation_id": job.id,
            "status": job.status,
            "mode": "live",
            "person": job.person,
            "filters": job.filters.to_dict(),
            "warmed": list(job.warmed),
            "failures": deepcopy(job.failures),
            "reused": reused,
            "storage": "temporary_memory",
            "ttl_seconds": self.ttl,
        }

    def start(self, person: str, filters: Filters) -> dict[str, Any]:
        if not isinstance(person, str) or not re.fullmatch(r"[1-9][0-9]{0,11}", person):
            raise PreparationError("invalid_request", "A numeric INSPIRE author record ID is required.")
        if not isinstance(filters, Filters):
            raise PreparationError("invalid_request", "Preparation filters are invalid.")
        key = self._key(person, filters)
        with self.lock:
            self._prune(make_room=True)
            if self.closed:
                raise PreparationError("resource_limit", "Preparation is stopping.", 503)
            existing = next((job for job in reversed(self.jobs.values())
                             if job.key == key and job.status in {"queued", "running", "ready"}), None)
            if existing is not None:
                self.jobs.move_to_end(existing.id)
                self.counters["reused"] += 1
                return self._public(existing, reused=True)
            active = sum(job.status == "running" for job in self.jobs.values())
            pending = sum(job.status == "queued" for job in self.jobs.values())
            if active + pending >= self.max_active + self.max_pending:
                self.counters["rejected"] += 1
                raise PreparationError("resource_limit", "The small preparation queue is full. Retry shortly.", 503)
            if len(self.jobs) >= self.max_retained:
                self.counters["rejected"] += 1
                raise PreparationError("resource_limit", "The temporary preparation workspace is full.", 503)
            job = _Preparation(uuid.uuid4().hex, person, filters, key, self.clock())
            # Reserve one of the two worker slots before submitting. This makes
            # queue accounting deterministic even if the executor has not yet
            # scheduled the new callable.
            if active < self.max_active:
                job.status = "running"
            self.jobs[job.id] = job
            self.counters["started"] += 1
            try:
                self.executor.submit(self._work, job)
            except RuntimeError as exc:
                del self.jobs[job.id]
                raise PreparationError("resource_limit", "Preparation is stopping.", 503) from exc
            return self._public(job)

    def _work(self, job: _Preparation) -> None:
        with self.lock:
            if self.closed:
                job.status = "cancelled"
                job.finished_at = self.clock()
                return
            job.status = "running"
            job.started_at = self.clock()

        query = DeepSession.literature_query(job.person, job.filters)
        identity_request = lambda: self.client.search(
            "authors", f"control_number:{job.person}", size=PROFILE_PAGE_SIZE,
            page=1, sort="mostrecent")
        downstream_requests = (
            ("facets", lambda: self.client.coauthors(query)),
            ("literature", lambda: self.client.search(
                "literature", query, size=self._literature_size(job.filters),
                page=1, sort="mostrecent")),
        )
        warmed: list[str] = []
        failures: list[dict[str, str]] = []
        identity_absent = False
        if not self.stop.is_set():
            try:
                identity_response = identity_request()
                if self._has_exact_current_identity(identity_response, job.person):
                    warmed.append("identity")
                else:
                    identity_absent = True
                    failures.append({
                        "stage": "identity",
                        "code": "not_found",
                        "message": "INSPIRE did not return the requested current author profile.",
                    })
            except Exception as exc:
                code = str(getattr(exc, "code", "upstream_unavailable"))
                message = (str(getattr(exc, "message"))
                           if hasattr(exc, "code") and hasattr(exc, "message")
                           else "This preparation request failed.")
                failures.append({"stage": "identity", "code": code, "message": message})

        # An exact-ID search which succeeds but omits the requested current
        # profile proves that this selection cannot be prepared. Do not spend
        # two more upstream requests warming evidence for a different identity.
        for stage, request in (() if identity_absent else downstream_requests):
            if self.stop.is_set():
                break
            try:
                request()
                warmed.append(stage)
            except Exception as exc:
                code = str(getattr(exc, "code", "upstream_unavailable"))
                message = (str(getattr(exc, "message"))
                           if hasattr(exc, "code") and hasattr(exc, "message")
                           else "This preparation request failed.")
                failures.append({
                    "stage": stage,
                    "code": code,
                    "message": message,
                })

        with self.lock:
            job.warmed = warmed
            job.failures = failures
            job.status = ("cancelled" if self.stop.is_set()
                          else ("ready" if not failures else ("partial" if warmed else "failed")))
            job.finished_at = self.clock()
            self.counters[job.status] += 1

    def get(self, preparation_id: str) -> dict[str, Any]:
        with self.lock:
            self._prune()
            job = self.jobs.get(preparation_id)
            if job is None:
                raise PreparationError("not_found", "This preparation has expired or was not found.", 404)
            return self._public(job)

    def info(self) -> dict[str, Any]:
        with self.lock:
            self._prune()
            statuses = Counter(job.status for job in self.jobs.values())
            return {
                "active": statuses["running"],
                "pending": statuses["queued"],
                "retained": len(self.jobs),
                "max_active": self.max_active,
                "max_pending": self.max_pending,
                "max_retained": self.max_retained,
                "ttl_seconds": self.ttl,
                "storage": "memory",
                "persistent": False,
                "counters": {key: int(value) for key, value in sorted(self.counters.items())},
            }

    def shutdown(self) -> None:
        with self.lock:
            self.closed = True
            self.stop.set()
            for job in self.jobs.values():
                if job.status == "queued":
                    job.status = "cancelled"
                    job.finished_at = self.clock()
        self.executor.shutdown(wait=False, cancel_futures=True)
