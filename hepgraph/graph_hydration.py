"""Bounded, post-route hydration of display metadata from INSPIRE.

The compact graph stores topology only, so the route is proven against the
database first and only the handful of records that will actually be shown are
fetched afterwards.  Two properties make that safe.

Bounded: hydration runs inside one serverless request, so every dimension a
slow upstream could expand -- requests, entries, wall clock, request rate --
is capped up front, and exhausting any of them ends the work cleanly.

Honest: a record that cannot be fetched becomes a placeholder that keeps its
ID and says why.  The edge it supports was already proven, so dropping the
entry would silently shorten a real route, and inventing a title or a name
would attribute work to the wrong person.
"""
from __future__ import annotations

import copy
import json
import re
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Protocol

from .pipeline import (PipelineError, _documented_date, _hits, _person_from_profile,
                       ref_id, sanitize_author, sanitize_literature, source_url, utc_now)
from .remote import RemoteError


WORK_KEYS = ("id", "title", "source_url", "date", "year", "date_source",
             "author_count", "doi", "arxiv", "retrieved_at")
PERSON_KEYS = ("id", "name", "orcid", "affiliations", "source_url", "profile_status")

RECORD_ID = re.compile(r"[1-9][0-9]{0,11}")
# INSPIRE accepts exact-ID OR batches on both collections; deep_search measured
# 25 as a safe width, and remote.RemoteClient recognises exactly this form for
# its per-record author cache.
BATCH_SIZE = 25

CACHE_TTL_SECONDS = 15 * 60
MAX_CACHE_ENTRIES = 512
MAX_CACHE_BYTES = 4 * 1024 * 1024

PEOPLE, WORKS = "people", "works"
_COLLECTION = {PEOPLE: "authors", WORKS: "literature"}
#: Cache namespace for a work's byline, stored beside the work itself so a
#: cached paper can still be checked against the source.  It is never fetched
#: or hydrated on its own, so it is not a hydration kind.
MEMBERS = "work-members"


class InspireLike(Protocol):
    """Either pipeline.InspireClient (``fetch``) or remote.RemoteClient (``search``)."""

    def fetch(self, collection: str, query: str, page: int, size: int,
              sort: str | None = None) -> dict[str, Any]: ...


@dataclass(frozen=True)
class HydrationBudget:
    """Conservative per-request allowance; a serverless handler owns one."""

    max_requests: int = 6
    max_people: int = 32
    max_works: int = 32
    deadline_seconds: float = 6.0
    min_interval_seconds: float = 0.5

    def validate(self) -> None:
        for field, maximum in (("max_requests", 64), ("max_people", 512), ("max_works", 512)):
            value = getattr(self, field)
            if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
                raise ValueError(f"{field} is outside the supported hydration limit")
        for field, maximum in (("deadline_seconds", 60.0), ("min_interval_seconds", 10.0)):
            value = getattr(self, field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= float(value) <= maximum:
                raise ValueError(f"{field} is outside the supported hydration limit")
        if self.deadline_seconds <= 0:
            raise ValueError("deadline_seconds must be positive")


@dataclass
class _Entry:
    expires_at: float
    value: dict[str, Any]
    size: int


class HydrationCache:
    """Process-local LRU of hydrated entries, bounded by count, bytes and TTL.

    Only successful entries are stored: caching a placeholder would turn one
    transient upstream failure into a TTL-long lie about the same record.
    """

    def __init__(self, *, ttl_seconds: float = CACHE_TTL_SECONDS,
                 max_entries: int = MAX_CACHE_ENTRIES, max_bytes: int = MAX_CACHE_BYTES,
                 clock: Callable[[], float] = time.monotonic) -> None:
        if ttl_seconds <= 0 or max_entries < 1 or max_bytes < 1:
            raise ValueError("hydration cache bounds must be positive")
        self._ttl, self._max_entries, self._max_bytes = float(ttl_seconds), max_entries, max_bytes
        self._clock = clock
        self._lock = threading.Lock()
        self._entries: OrderedDict[tuple[str, str], _Entry] = OrderedDict()
        self._bytes = 0

    def _evict_expired(self, now: float) -> None:
        for key in [key for key, entry in self._entries.items() if entry.expires_at <= now]:
            self._bytes -= self._entries.pop(key).size

    def get(self, kind: str, ident: str) -> dict[str, Any] | None:
        with self._lock:
            now = self._clock()
            self._evict_expired(now)
            entry = self._entries.pop((kind, ident), None)
            if entry is None:
                return None
            self._entries[(kind, ident)] = entry
            return copy.deepcopy(entry.value)

    def put(self, kind: str, ident: str, value: dict[str, Any]) -> None:
        try:
            size = len(json.dumps(value, ensure_ascii=False, separators=(",", ":"),
                                  allow_nan=False).encode("utf-8"))
        except (TypeError, ValueError):
            return
        if size > self._max_bytes:
            return
        with self._lock:
            now = self._clock()
            self._evict_expired(now)
            old = self._entries.pop((kind, ident), None)
            if old is not None:
                self._bytes -= old.size
            while self._entries and (len(self._entries) >= self._max_entries
                                     or self._bytes + size > self._max_bytes):
                self._bytes -= self._entries.popitem(last=False)[1].size
            self._entries[(kind, ident)] = _Entry(now + self._ttl, copy.deepcopy(value), size)
            self._bytes += size

    def info(self) -> dict[str, int]:
        with self._lock:
            self._evict_expired(self._clock())
            return {"entries": len(self._entries), "bytes": self._bytes}

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()
            self._bytes = 0


@dataclass(frozen=True)
class HydrationResult:
    people: dict[str, dict[str, Any]]
    works: dict[str, dict[str, Any]]
    requests_made: int
    cache_hits: int
    failures: int
    complete: bool
    reason: str | None


def placeholder(kind: str, ident: str, reason: str) -> dict[str, Any]:
    """An entry that keeps the proven ID and admits it carries no detail."""
    known = RECORD_ID.fullmatch(ident) is not None
    return {"id": ident, "details_unavailable": True, "reason": reason,
            "source_url": source_url(_COLLECTION[kind], ident) if known else None}


def _dedupe(ids: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(str(ident) for ident in ids if isinstance(ident, str) and ident))


def _member_ids(hit: Any) -> frozenset[str]:
    """Resolved INSPIRE author record IDs on one literature hit."""
    metadata = hit.get("metadata") if isinstance(hit, dict) else None
    authors = metadata.get("authors") if isinstance(metadata, dict) else None
    if not isinstance(authors, list):
        return frozenset()
    found = set()
    for author in authors:
        if not isinstance(author, dict):
            continue
        identifier = ref_id(author.get("record"))
        if identifier is not None:
            found.add(str(identifier))
    return frozenset(found)


def _work_entry(recid: str, payload: dict[str, Any]) -> dict[str, Any]:
    date, date_source = _documented_date([payload])
    year = int(date[:4]) if date and re.fullmatch(r"\d{4}(?:-\d{2}(?:-\d{2})?)?", date) else None
    return {
        "id": recid,
        "title": payload["titles"][0] if payload["titles"] else "Untitled INSPIRE record",
        "source_url": source_url("literature", recid),
        "date": date, "year": year, "date_source": date_source,
        "author_count": payload["author_count"],
        "doi": sorted(set(payload["dois"])), "arxiv": sorted(set(payload["arxiv_eprints"])),
        "retrieved_at": utc_now(),
    }


def _person_entry(recid: str, payload: dict[str, Any]) -> dict[str, Any]:
    person = _person_from_profile(recid, payload, utc_now())
    return {key: person[key] for key in PERSON_KEYS}


class Hydrator:
    """Fetches display metadata for an already-proven route, within a budget."""

    def __init__(self, client: InspireLike, *, cache: HydrationCache | None = None,
                 budget: HydrationBudget | None = None,
                 clock: Callable[[], float] = time.monotonic,
                 sleep: Callable[[float], None] = time.sleep) -> None:
        self.budget = budget or HydrationBudget()
        self.budget.validate()
        self._client = client
        self._cache = cache if cache is not None else HydrationCache(clock=clock)
        self._clock, self._sleep = clock, sleep
        self._deadline = clock() + float(self.budget.deadline_seconds)
        self._next_request_at = 0.0
        self._used = {PEOPLE: 0, WORKS: 0}
        self.requests_made = self.cache_hits = self.failures = 0
        #: Resolved author IDs per fetched work, kept from the same response
        #: that supplied the metadata so verifying a route's edges against the
        #: source costs no additional requests.
        self.work_members: dict[str, frozenset[str]] = {}

    def hydrate_people(self, ids: tuple[str, ...]) -> dict[str, dict[str, Any]]:
        return self._hydrate(PEOPLE, ids)

    def hydrate_works(self, ids: tuple[str, ...]) -> dict[str, dict[str, Any]]:
        return self._hydrate(WORKS, ids)

    def hydrate_route(self, *, people_ids: tuple[str, ...],
                      work_ids: tuple[str, ...]) -> HydrationResult:
        before = (self.requests_made, self.cache_hits, self.failures)
        people = self._hydrate(PEOPLE, people_ids)
        works = self._hydrate(WORKS, work_ids)
        missing = [entry for entry in (*people.values(), *works.values())
                   if entry.get("details_unavailable")]
        reason: str | None = None
        if missing:
            reasons = {entry["reason"] for entry in missing}
            reason = "budget_exhausted" if "budget_exhausted" in reasons else missing[0]["reason"]
        return HydrationResult(
            people=people, works=works,
            requests_made=self.requests_made - before[0],
            cache_hits=self.cache_hits - before[1],
            failures=self.failures - before[2],
            complete=not missing, reason=reason,
        )

    def _limit(self, kind: str) -> int:
        return self.budget.max_people if kind == PEOPLE else self.budget.max_works

    def _fail(self, results: dict[str, dict[str, Any]], kind: str, ident: str, reason: str) -> None:
        results[ident] = placeholder(kind, ident, reason)
        self.failures += 1

    def _hydrate(self, kind: str, ids: tuple[str, ...]) -> dict[str, dict[str, Any]]:
        results: dict[str, dict[str, Any]] = {}
        pending: list[str] = []
        for ident in _dedupe(ids):
            if RECORD_ID.fullmatch(ident) is None:
                self._fail(results, kind, ident, "invalid_id")
                continue
            if self._used[kind] >= self._limit(kind):
                self._fail(results, kind, ident, "budget_exhausted")
                continue
            self._used[kind] += 1
            cached = self._cache.get(kind, ident)
            if cached is not None:
                self.cache_hits += 1
                results[ident] = cached
                # A cached paper must still be able to confirm or contradict the
                # edge that cites it.  Without its byline the route would be
                # reported unverified purely because the paper was fetched
                # recently, which reads as missing evidence rather than what it
                # is: evidence already in hand.
                if kind == WORKS:
                    members = self._cache.get(MEMBERS, ident)
                    if members is not None:
                        self.work_members[ident] = frozenset(members["ids"])
                continue
            pending.append(ident)
        for start in range(0, len(pending), BATCH_SIZE):
            chunk = pending[start:start + BATCH_SIZE]
            records, reasons, failure = self._fetch(kind, chunk)
            for ident in chunk:
                payload = records.get(ident)
                if payload is not None:
                    entry = (_person_entry if kind == PEOPLE else _work_entry)(ident, payload)
                    self._cache.put(kind, ident, entry)
                    # Kept for exactly as long as the entry it belongs to.  An
                    # unlinked byline is stored as nothing, which is how the
                    # edge check already reads a record that can confirm
                    # nothing.
                    members = self.work_members.get(ident)
                    if kind == WORKS and members:
                        self._cache.put(MEMBERS, ident, {"ids": sorted(members)})
                    results[ident] = entry
                else:
                    self._fail(results, kind, ident, failure or reasons.get(ident, "not_found"))
        return results

    def _fetch(self, kind: str, chunk: list[str]) -> tuple[dict[str, dict[str, Any]], dict[str, str], str | None]:
        """Return sanitized payloads by ID, per-ID reasons, and any whole-batch failure."""
        if self.requests_made >= self.budget.max_requests:
            return {}, {}, "budget_exhausted"
        wait = max(0.0, self._next_request_at - self._clock())
        if self._clock() + wait >= self._deadline:
            return {}, {}, "budget_exhausted"
        if wait > 0:
            self._sleep(wait)
        collection = _COLLECTION[kind]
        query = " OR ".join(f"control_number:{ident}" for ident in chunk)
        self.requests_made += 1
        try:
            response = self._call(collection, query, max(len(chunk), 1))
        except (RemoteError, PipelineError, TimeoutError, OSError) as error:
            self._next_request_at = self._clock() + self.budget.min_interval_seconds
            return {}, {}, _failure_reason(error)
        except Exception:
            # Hydration is decoration on an answer that is already proven.  No
            # client fault may destroy the route and evidence the search earned,
            # so an unexpected error degrades this batch instead of raising.
            self._next_request_at = self._clock() + self.budget.min_interval_seconds
            return {}, {}, "upstream_unavailable"
        self._next_request_at = self._clock() + self.budget.min_interval_seconds
        sanitize = sanitize_author if kind == PEOPLE else sanitize_literature
        requested: set[str] = set(chunk)
        records: dict[str, dict[str, Any]] = {}
        reasons: dict[str, str] = {}
        try:
            hits = _hits(response)
        except PipelineError:
            return {}, {}, "malformed_response"
        for hit in hits:
            ident = _hit_id(hit)
            try:
                recid, payload = sanitize(hit)
            except PipelineError:
                if ident in requested:
                    reasons[ident] = "malformed_record"
                continue
            # A broadened or substituted upstream result must never stand in for
            # the record the route actually cited.
            if recid not in requested:
                continue
            if payload["deleted"]:
                reasons[recid] = "record_deleted"
                continue
            records[recid] = payload
            if kind == WORKS:
                # The byline is not display metadata, so it is not part of the
                # work entry; it is kept aside so a route's edges can be checked
                # against the source without fetching the record twice.
                self.work_members[recid] = _member_ids(hit)
            reasons.pop(recid, None)
        return records, reasons, None

    def _call(self, collection: str, query: str, size: int) -> dict[str, Any]:
        search = getattr(self._client, "search", None)
        if callable(search):
            return search(collection, query, size=size, page=1)
        return self._client.fetch(collection, query, 1, size)


def _hit_id(hit: Any) -> str | None:
    if not isinstance(hit, dict):
        return None
    metadata = hit.get("metadata") if isinstance(hit.get("metadata"), dict) else {}
    recid = hit.get("id") or metadata.get("control_number")
    return str(recid) if isinstance(recid, (str, int)) and not isinstance(recid, bool) else None


def _failure_reason(error: Exception) -> str:
    if isinstance(error, RemoteError):
        if getattr(error, "deadline", False) or error.code == "resource_limit":
            return "upstream_timeout"
        return "upstream_unavailable"
    if isinstance(error, TimeoutError):
        return "upstream_timeout"
    return "upstream_unavailable"
