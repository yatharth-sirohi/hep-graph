"""Bounded, memory-only access to the public INSPIRE search endpoints.

This module is deliberately a small transport boundary.  It never accepts an
upstream URL, never writes a cache to disk, and has no background work.  Callers
must share one client instance for process-wide request pacing in the normal
application configuration.
"""
from __future__ import annotations

import copy
from collections import Counter, OrderedDict
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
import json
import math
import os
import re
import threading
import time
from typing import Any, Callable
import weakref
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .pipeline import (
    API_ROOT, AUTHOR_FIELDS, LITERATURE_FIELDS, PipelineError, _cached_hit,
    sanitize_author, sanitize_literature,
)


# A single literature page can now be megabytes, so an 8 MiB budget would let
# two of them evict every warmed author record. Keep the cache bounded, but
# large enough that one page is a small fraction of it.
MAX_CACHE_BYTES = 64 * 1024 * 1024
# No single response may occupy more than this share of the budget.
MAX_ENTRY_FRACTION = 0.1
MAX_CACHE_ENTRIES = 256
CACHE_TTL_SECONDS = 15 * 60
MAX_RESPONSE_BYTES = 4 * 1024 * 1024
# Raised verbatim so a caller can tell "this page was too big" from every other
# resource limit and retry smaller instead of giving up on the query.
OVERSIZE_MESSAGE = "INSPIRE response exceeded the 4 MiB limit"
NETWORK_TIMEOUT_SECONDS = 8.0
# INSPIRE documents 15 requests per 5 s per IP (rest-api-doc, checked
# 2026-09-15).  That ceiling is 3.0 req/s; HEP Graph paces at 2.0 req/s so the
# worst case in any 5 s window is 10 of the allowed 15, leaving headroom for
# retries and for a second process sharing the address.  Override with
# HEPGRAPH_REQUEST_INTERVAL (seconds) to pace even more slowly.
INSPIRE_DOCUMENTED_REQUESTS = 15
INSPIRE_DOCUMENTED_WINDOW_SECONDS = 5.0
REQUEST_INTERVAL_SECONDS = 0.5
MIN_REQUEST_INTERVAL_SECONDS = (
    INSPIRE_DOCUMENTED_WINDOW_SECONDS / INSPIRE_DOCUMENTED_REQUESTS)
MAX_QUERY_LENGTH = 4096
MAX_PAGE = 10_000
# INSPIRE accepts up to 1000 results per page and rejects 2000 with a 400
# (measured; see docs/INSPIRE_NEIGHBORHOOD_API_AUDIT.md). Large pages are the
# single biggest saving available on neighbourhood certification: 1,127
# qualifying works cost two requests at 1000 and twelve at 100.
MAX_SIZE = 1000
MAX_FACET_BUCKETS = 100
MAX_INFLIGHT = 8
MIN_RETRY_AFTER_SECONDS = 5.0
MAX_JSON_DEPTH = 64
AUTHOR_ID_PATTERN = r"[1-9][0-9]{0,11}"


class RemoteError(RuntimeError):
    """A safe remote-access failure suitable for an API response."""

    def __init__(self, code: str, message: str) -> None:
        if code not in {"upstream_unavailable", "resource_limit"}:
            raise ValueError("unsupported remote error code")
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass
class _CacheEntry:
    expires_at: float
    value: dict[str, Any]
    size: int


@dataclass
class _PaceState:
    lock: threading.Lock
    next_allowed: float = 0.0
    cooldown_until: float = 0.0


@dataclass
class _PendingRequest:
    """One leader request shared by callers with independent wait deadlines."""

    event: threading.Event
    value: dict[str, Any] | None = None
    error: tuple[str, str] | None = None


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req: Request, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


def _default_transport(url: str, timeout: float) -> bytes:
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "hep-graph/1"})
    with build_opener(_NoRedirect()).open(request, timeout=timeout) as response:
        body = response.read(MAX_RESPONSE_BYTES + 1)
    return body


def _request_interval(override: float | None) -> float:
    """Never pace faster than INSPIRE's published ceiling allows."""
    if override is None:
        raw = os.environ.get("HEPGRAPH_REQUEST_INTERVAL")
        try:
            override = float(raw) if raw else REQUEST_INTERVAL_SECONDS
        except (TypeError, ValueError):
            override = REQUEST_INTERVAL_SECONDS
        if not math.isfinite(override):
            override = REQUEST_INTERVAL_SECONDS
    if isinstance(override, bool) or not isinstance(override, (int, float)) or not math.isfinite(float(override)):
        raise ValueError("request_interval must be a finite number of seconds")
    return max(float(override), MIN_REQUEST_INTERVAL_SECONDS)


class RemoteClient:
    """A synchronously bounded public-search client.

    ``deadline`` is an absolute value in the injected monotonic ``clock``
    domain.  If omitted, each call receives an eight-second budget including
    pacing and transport.  Tests may inject ``transport(url, timeout)``,
    ``clock()``, and ``sleep(seconds)`` without creating network traffic.
    """

    _pace_states: weakref.WeakKeyDictionary[Any, _PaceState] = weakref.WeakKeyDictionary()
    _pace_states_lock = threading.Lock()
    _default_pace_state = _PaceState(threading.Lock())

    def __init__(
        self,
        *,
        transport: Callable[[str, float], bytes] | None = None,
        clock: Callable[[], float] | None = None,
        sleep: Callable[[float], None] | None = None,
        cache_bytes: int = MAX_CACHE_BYTES,
        cache_entries: int = MAX_CACHE_ENTRIES,
        ttl_seconds: float = CACHE_TTL_SECONDS,
        request_interval: float | None = None,
    ) -> None:
        if isinstance(cache_bytes, bool) or not isinstance(cache_bytes, int) or not 1 <= cache_bytes <= MAX_CACHE_BYTES:
            raise ValueError(f"cache_bytes must be 1..{MAX_CACHE_BYTES}")
        if isinstance(cache_entries, bool) or not isinstance(cache_entries, int) or not 1 <= cache_entries <= MAX_CACHE_ENTRIES:
            raise ValueError(f"cache_entries must be 1..{MAX_CACHE_ENTRIES}")
        if (isinstance(ttl_seconds, bool) or not isinstance(ttl_seconds, (int, float))
                or not math.isfinite(float(ttl_seconds)) or ttl_seconds <= 0):
            raise ValueError("ttl_seconds must be a finite positive number")
        self._request_interval = _request_interval(request_interval)
        self._transport = transport or _default_transport
        self._clock = time.monotonic if clock is None else clock
        self._sleep = time.sleep if sleep is None else sleep
        self._cache_limit = cache_bytes
        self._entry_limit = cache_entries
        self._ttl_seconds = float(ttl_seconds)
        # Query responses and reusable public author records share one LRU, one
        # entry ceiling, and the same 8 MiB byte ceiling.  Record keys let an
        # exact ID batch reuse profiles obtained through a different query,
        # while keeping arbitrary name/alias queries as distinct query keys.
        self._cache: OrderedDict[tuple[Any, ...], _CacheEntry] = OrderedDict()
        self._cache_bytes = 0
        self._cache_lock = threading.RLock()
        self._inflight = threading.BoundedSemaphore(MAX_INFLIGHT)
        self._pending_lock = threading.Lock()
        self._pending: dict[tuple[str, str, int, int, str | None], _PendingRequest] = {}
        self._stats_lock = threading.Lock()
        self._stats: dict[str, Counter[str]] = {
            layer: Counter() for layer in ("authors", "literature", "facets", "shared_papers")
        }
        # Clients which use the same clock share pacing.  The application uses
        # the default monotonic clock, making this process-wide without mixing
        # unrelated deterministic test clock domains.
        if clock is None:
            self._pace_state = self._default_pace_state
        else:
            with self._pace_states_lock:
                try:
                    self._pace_state = self._pace_states.setdefault(self._clock, _PaceState(threading.Lock()))
                except TypeError:
                    # Some injected callables cannot be weak-keyed. Keep those
                    # clients isolated rather than retaining an unbounded
                    # process-wide registry or risking object-id reuse.
                    self._pace_state = _PaceState(threading.Lock())

    @staticmethod
    def _validate_query(query: str) -> None:
        if not isinstance(query, str) or not query or len(query) > MAX_QUERY_LENGTH or any(ord(char) < 32 or ord(char) == 127 for char in query):
            raise RemoteError("resource_limit", "query is empty, too long, or contains control characters")

    @classmethod
    def _validate_request(cls, collection: str, query: str, size: int, page: int, sort: str | None) -> None:
        if collection not in {"authors", "literature"}:
            raise RemoteError("resource_limit", "unsupported INSPIRE collection")
        cls._validate_query(query)
        if isinstance(size, bool) or not isinstance(size, int) or not 1 <= size <= MAX_SIZE:
            raise RemoteError("resource_limit", f"size must be between 1 and {MAX_SIZE}")
        if isinstance(page, bool) or not isinstance(page, int) or not 1 <= page <= MAX_PAGE:
            raise RemoteError("resource_limit", f"page must be between 1 and {MAX_PAGE}")
        if page * size > MAX_PAGE:
            raise RemoteError("resource_limit", f"page times size must not exceed the {MAX_PAGE} result window")
        if sort is not None and (not isinstance(sort, str) or not sort or len(sort) > 128 or any(ord(char) < 32 or ord(char) == 127 for char in sort)):
            raise RemoteError("resource_limit", "sort is invalid")

    def _deadline(self, deadline: float | None) -> float:
        now = self._clock()
        if deadline is None:
            return now + NETWORK_TIMEOUT_SECONDS
        if isinstance(deadline, bool) or not isinstance(deadline, (int, float)) or not math.isfinite(float(deadline)):
            raise RemoteError("resource_limit", "deadline must be a monotonic timestamp")
        if deadline <= now:
            raise RemoteError("resource_limit", "request deadline has already elapsed")
        return float(deadline)

    def _evict_expired(self, now: float) -> None:
        for key in list(self._cache):
            entry = self._cache[key]
            if entry.expires_at > now:
                continue
            self._cache_bytes -= entry.size
            del self._cache[key]

    def _cached(self, key: tuple[Any, ...], now: float) -> dict[str, Any] | None:
        with self._cache_lock:
            self._evict_expired(now)
            entry = self._cache.pop(key, None)
            if entry is None:
                return None
            self._cache[key] = entry
            return copy.deepcopy(entry.value)

    def _cache_result(self, key: tuple[Any, ...], value: dict[str, Any], now: float) -> None:
        try:
            encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise RemoteError("upstream_unavailable", "INSPIRE returned a non-JSON-safe search result") from exc
        size = len(encoded)
        # One large literature page must never be able to evict the warmed
        # author records the next request depends on, so an entry that would
        # dominate the budget is simply not kept.
        if size > self._cache_limit * MAX_ENTRY_FRACTION:
            return
        with self._cache_lock:
            self._evict_expired(now)
            old = self._cache.pop(key, None)
            if old is not None:
                self._cache_bytes -= old.size
            while self._cache and (len(self._cache) >= self._entry_limit or self._cache_bytes + size > self._cache_limit):
                _, removed = self._cache.popitem(last=False)
                self._cache_bytes -= removed.size
            self._cache[key] = _CacheEntry(now + self._ttl_seconds, copy.deepcopy(value), size)
            self._cache_bytes += size

    @staticmethod
    def _cache_layer(key: tuple[Any, ...]) -> str:
        if len(key) == 2 and key[0] == "author_record":
            return "authors"
        collection, query, _, _, _ = key
        if collection == "authors":
            return "authors"
        if collection == "facets":
            return "facets"
        if len(re.findall(r"authors\.record\.\$ref:", query)) >= 2:
            return "shared_papers"
        return "literature"

    def _count(self, layer: str, field: str, amount: int = 1) -> None:
        with self._stats_lock:
            self._stats[layer][field] += amount

    @staticmethod
    def _exact_author_ids(query: str) -> list[str] | None:
        """Recognise only exact numeric profile queries generated by this app."""
        parts = query.split(" OR ")
        if not parts:
            return None
        ids: list[str] = []
        for part in parts:
            match = re.fullmatch(rf"control_number:({AUTHOR_ID_PATTERN})", part)
            if match is None or match.group(1) in ids:
                return None
            ids.append(match.group(1))
        return ids

    def _cached_author_ids(self, ids: list[str], *, size: int, page: int, now: float) -> dict[str, Any] | None:
        """Build a first page only when every exact requested ID is fresh.

        We cannot synthesize later pages or a size-truncated batch because the
        upstream sort order would be unknown.  A missing record is never cached
        as an absence and sends the whole request to INSPIRE.
        """
        if page != 1 or len(ids) > size:
            return None
        with self._cache_lock:
            self._evict_expired(now)
            entries = [self._cache.get(("author_record", person_id)) for person_id in ids]
            if any(entry is None for entry in entries):
                return None
            for person_id in ids:
                self._cache.move_to_end(("author_record", person_id))
            return {
                "hits": {
                    "total": len(ids),
                    "hits": [copy.deepcopy(entry.value) for entry in entries if entry is not None],
                }
            }

    def _index_author_records(self, response: dict[str, Any], now: float) -> None:
        """Index only sanitized, internally consistent public author hits."""
        hits = response.get("hits", {}).get("hits", [])
        indexed = 0
        for hit in hits:
            metadata = hit.get("metadata") if isinstance(hit, dict) else None
            person_id = hit.get("id") if isinstance(hit, dict) else None
            control_number = metadata.get("control_number") if isinstance(metadata, dict) else None
            if (not isinstance(person_id, str) or not re.fullmatch(AUTHOR_ID_PATTERN, person_id)
                    or control_number != person_id):
                continue
            self._cache_result(("author_record", person_id), hit, now)
            indexed += 1
        if indexed:
            self._count("authors", "records_indexed", indexed)

    def _request(
        self,
        key: tuple[str, str, int, int, str | None],
        deadline: float,
        loader: Callable[[], dict[str, Any]],
        *,
        cache_response: bool = True,
    ) -> dict[str, Any]:
        """Return a cached value or coalesce one identical live request.

        The leader's deadline belongs only to the leader. Followers wait on the
        same result for at most their own remaining time and never cancel the
        shared transport. Errors wake current followers but are neither cached
        nor retained in the pending map for later callers.
        """

        layer = self._cache_layer(key)
        cached = self._cached(key, self._clock())
        if cached is not None:
            self._count(layer, "hits")
            return cached

        with self._pending_lock:
            # Close the race with a leader that finished between the first
            # cache lookup and pending-map acquisition.
            cached = self._cached(key, self._clock())
            if cached is not None:
                self._count(layer, "hits")
                return cached
            pending = self._pending.get(key)
            leader = pending is None
            if leader:
                if not self._inflight.acquire(blocking=False):
                    self._count(layer, "rejected")
                    raise RemoteError("resource_limit", "too many live INSPIRE requests are already in progress")
                pending = _PendingRequest(threading.Event())
                self._pending[key] = pending
                self._count(layer, "misses")
            else:
                self._count(layer, "coalesced")

        assert pending is not None
        if not leader:
            remaining = deadline - self._clock()
            if remaining <= 0 or not pending.event.wait(remaining):
                self._count(layer, "wait_deadlines")
                raise RemoteError("resource_limit", "request deadline elapsed while waiting for an identical INSPIRE request")
            if self._clock() > deadline:
                self._count(layer, "wait_deadlines")
                raise RemoteError("resource_limit", "request deadline elapsed while waiting for an identical INSPIRE request")
            if pending.error is not None:
                code, message = pending.error
                # A short-deadline leader must not impose its private time
                # budget on a longer-lived follower. After the failed leader
                # leaves the pending map, current followers race once more and
                # still coalesce behind a single replacement leader.
                if code == "resource_limit" and "deadline" in message and self._clock() < deadline:
                    return self._request(key, deadline, loader)
                raise RemoteError(code, message)
            if pending.value is None:
                raise RemoteError("upstream_unavailable", "the shared INSPIRE request did not produce a result")
            return copy.deepcopy(pending.value)

        try:
            self._count(layer, "upstream_requests")
            value = loader()
            if cache_response:
                self._cache_result(key, value, self._clock())
            pending.value = copy.deepcopy(value)
            return copy.deepcopy(value)
        except RemoteError as exc:
            pending.error = (exc.code, exc.message)
            self._count(layer, "errors")
            raise
        except Exception as exc:
            pending.error = ("upstream_unavailable", "the shared INSPIRE request failed")
            self._count(layer, "errors")
            raise
        finally:
            with self._pending_lock:
                self._pending.pop(key, None)
                pending.event.set()
            self._inflight.release()

    @staticmethod
    def _validate_json_value(value: Any) -> None:
        """Reject decoder edge cases before schema sanitisation can discard them."""
        pending: list[tuple[Any, int]] = [(value, 0)]
        while pending:
            item, depth = pending.pop()
            if depth > MAX_JSON_DEPTH:
                raise RemoteError("upstream_unavailable", "INSPIRE response exceeds the JSON nesting limit")
            if isinstance(item, float):
                if not math.isfinite(item):
                    raise RemoteError("upstream_unavailable", "INSPIRE response contains a non-finite JSON number")
            elif isinstance(item, dict):
                # json.loads creates string keys, but retain this check if a
                # decoder implementation ever changes.
                if not all(isinstance(key, str) for key in item):
                    raise RemoteError("upstream_unavailable", "INSPIRE response contains invalid JSON object keys")
                pending.extend((nested, depth + 1) for nested in item.values())
            elif isinstance(item, list):
                pending.extend((nested, depth + 1) for nested in item)
            elif item is not None and not isinstance(item, (str, int, bool)):
                raise RemoteError("upstream_unavailable", "INSPIRE response contains an invalid JSON value")

    @staticmethod
    def _validate_response(value: Any, requested_size: int) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise RemoteError("upstream_unavailable", "INSPIRE returned a malformed search response")
        hits = value.get("hits")
        if not isinstance(hits, dict) or not isinstance(hits.get("hits"), list):
            raise RemoteError("upstream_unavailable", "INSPIRE response lacks a valid hits container")
        if len(hits["hits"]) > requested_size:
            raise RemoteError("upstream_unavailable", "INSPIRE response returned more hits than requested")
        total = hits.get("total")
        if isinstance(total, bool):
            raise RemoteError("upstream_unavailable", "INSPIRE response has an invalid total")
        if isinstance(total, dict):
            relation = total.get("relation")
            if relation is not None and relation not in {"eq", "gte"}:
                raise RemoteError("upstream_unavailable", "INSPIRE response has an invalid total relation")
            total = total.get("value")
        if not isinstance(total, int) or isinstance(total, bool) or total < 0:
            raise RemoteError("upstream_unavailable", "INSPIRE response has an invalid total")
        for hit in hits["hits"]:
            if not isinstance(hit, dict) or not isinstance(hit.get("metadata"), dict):
                raise RemoteError("upstream_unavailable", "INSPIRE response has malformed hit metadata")
        return value

    @staticmethod
    def _sanitized_response(collection: str, value: dict[str, Any]) -> dict[str, Any]:
        """Return only requested public metadata before any caller/cache sees it."""
        hits = value["hits"]
        raw_total = hits["total"]
        total: int | dict[str, Any]
        if isinstance(raw_total, dict):
            total = {"value": raw_total["value"]}
            if "relation" in raw_total:
                total["relation"] = raw_total["relation"]
        else:
            total = raw_total
        clean_hits: list[dict[str, Any]] = []
        try:
            for raw_hit in hits["hits"]:
                if collection == "literature":
                    recid, payload = sanitize_literature(raw_hit)
                else:
                    recid, payload = sanitize_author(raw_hit)
                clean = _cached_hit(collection, recid, payload)
                # These are source lifecycle values, not personal metadata.
                created = raw_hit.get("created")
                if isinstance(created, str) and created.strip():
                    clean["created"] = created.strip()
                clean_hits.append(clean)
        except PipelineError as exc:
            raise RemoteError("upstream_unavailable", "INSPIRE response does not match the requested metadata schema") from exc
        return {"hits": {"total": total, "hits": clean_hits}}

    @staticmethod
    def _retry_after(error: HTTPError) -> float:
        headers = error.headers
        value = headers.get("Retry-After") if headers is not None else None
        try:
            delay = float(value)
        except (TypeError, ValueError):
            delay = None
        if delay is not None and math.isfinite(delay) and delay >= 0:
            return max(MIN_RETRY_AFTER_SECONDS, delay)
        if isinstance(value, str):
            try:
                retry_at = parsedate_to_datetime(value)
                if retry_at.tzinfo is not None:
                    delay = retry_at.timestamp() - time.time()
                    if math.isfinite(delay) and delay >= 0:
                        return max(MIN_RETRY_AFTER_SECONDS, delay)
            except (IndexError, OverflowError, TypeError, ValueError):
                pass
        return MIN_RETRY_AFTER_SECONDS

    def _set_cooldown(self, seconds: float) -> None:
        with self._pace_state.lock:
            until = self._clock() + seconds
            self._pace_state.cooldown_until = max(self._pace_state.cooldown_until, until)
            self._pace_state.next_allowed = max(self._pace_state.next_allowed, self._pace_state.cooldown_until)

    def _reserve_request(self, deadline: float) -> None:
        with self._pace_state.lock:
            now = self._clock()
            earliest = max(self._pace_state.next_allowed, self._pace_state.cooldown_until)
            delay = earliest - now
            if delay > 0:
                if now + delay >= deadline:
                    if self._pace_state.cooldown_until > now:
                        raise RemoteError("resource_limit", "INSPIRE rate-limit cooldown would exceed this request deadline")
                    raise RemoteError("resource_limit", "request deadline would be exceeded by global rate pacing")
                self._sleep(delay)
                now = self._clock()
            if now >= deadline:
                raise RemoteError("resource_limit", "request deadline elapsed while waiting for global pacing")
            self._pace_state.next_allowed = now + self._request_interval

    def _fetch_json(self, url: str, deadline: float, layer: str) -> Any:
        """Fetch and validate JSON under the shared transport constraints."""
        timeout = min(NETWORK_TIMEOUT_SECONDS, deadline - self._clock())
        if timeout <= 0:
            raise RemoteError("resource_limit", "request deadline elapsed before transport")
        try:
            body = self._transport(url, timeout)
        except HTTPError as exc:
            if exc.code == 429:
                retry_after = self._retry_after(exc)
                self._set_cooldown(retry_after)
                raise RemoteError("resource_limit", f"INSPIRE rate limited this client; retry after at least {retry_after:g} seconds") from exc
            raise RemoteError("upstream_unavailable", f"INSPIRE HTTP {exc.code}") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise RemoteError("upstream_unavailable", "INSPIRE is unavailable") from exc
        except Exception as exc:
            raise RemoteError("upstream_unavailable", "INSPIRE transport failed") from exc
        if not isinstance(body, bytes):
            raise RemoteError("upstream_unavailable", "INSPIRE transport returned invalid data")
        # Traffic, counted at the one place the transport actually runs, and
        # before the size check so a refused page still shows what it cost.
        # Deliberately not the cache-residency figure in layers[*]["bytes"].
        self._count(layer, "wire_bytes", len(body))
        if len(body) > MAX_RESPONSE_BYTES:
            raise RemoteError("resource_limit", OVERSIZE_MESSAGE)
        try:
            value = json.loads(body.decode("utf-8"), parse_constant=lambda _: (_ for _ in ()).throw(ValueError("non-finite JSON number")))
        except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError) as exc:
            raise RemoteError("upstream_unavailable", "INSPIRE returned invalid JSON") from exc
        self._validate_json_value(value)
        if self._clock() > deadline:
            raise RemoteError("resource_limit", "request deadline elapsed during transport")
        return value

    @staticmethod
    def _sanitized_coauthors_response(value: Any) -> dict[str, Any]:
        """Reduce a facets response to weighted author-ID discovery hints."""
        if not isinstance(value, dict):
            raise RemoteError("upstream_unavailable", "INSPIRE returned a malformed facets response")
        hits = value.get("hits")
        if not isinstance(hits, dict):
            raise RemoteError("upstream_unavailable", "INSPIRE facets response lacks a valid hits container")
        total = hits.get("total")
        total_is_lower_bound = False
        if isinstance(total, dict):
            relation = total.get("relation")
            total = total.get("value")
            if relation not in {"eq", "gte"}:
                raise RemoteError("upstream_unavailable", "INSPIRE facets response has an invalid total")
            total_is_lower_bound = relation == "gte"
        if isinstance(total, bool) or not isinstance(total, int) or total < 0:
            raise RemoteError("upstream_unavailable", "INSPIRE facets response has an invalid total")

        aggregations = value.get("aggregations")
        author = aggregations.get("author") if isinstance(aggregations, dict) else None
        if not isinstance(author, dict) or not isinstance(author.get("buckets"), list):
            raise RemoteError("upstream_unavailable", "INSPIRE facets response lacks an author aggregation")
        if len(author["buckets"]) > MAX_FACET_BUCKETS:
            raise RemoteError("upstream_unavailable", "INSPIRE author aggregation exceeds the bucket limit")
        omitted = author.get("sum_other_doc_count")
        error = author.get("doc_count_error_upper_bound")
        for count in (omitted, error):
            if isinstance(count, bool) or not isinstance(count, int) or count < 0:
                raise RemoteError("upstream_unavailable", "INSPIRE author aggregation has invalid completeness metadata")

        counts_by_id: OrderedDict[str, int] = OrderedDict()
        unresolved_bucket = False
        for bucket in author["buckets"]:
            if not isinstance(bucket, dict):
                raise RemoteError("upstream_unavailable", "INSPIRE author aggregation contains a malformed bucket")
            key = bucket.get("key")
            count = bucket.get("doc_count")
            if (not isinstance(key, str) or isinstance(count, bool) or not isinstance(count, int)
                    or count <= 0 or count > total):
                raise RemoteError("upstream_unavailable", "INSPIRE author aggregation contains a malformed bucket")
            match = re.fullmatch(r"([1-9][0-9]{0,11})_(.+)", key)
            if match is None:
                # Older or unresolved author terms can be name-only or carry a
                # non-record prefix. They are unusable without a forbidden
                # name join, so omit them and report incomplete coverage.
                unresolved_bucket = True
                continue
            author_id = match.group(1)
            # The terms key includes a display name, so one stable author ID can
            # theoretically occur in more than one bucket. Taking the maximum
            # avoids inventing a larger edge weight by summing overlapping works.
            counts_by_id[author_id] = max(count, counts_by_id.get(author_id, 0))

        return {
            "authors": [{"id": author_id, "count": count} for author_id, count in counts_by_id.items()],
            "truncated": total_is_lower_bound or omitted > 0 or error > 0 or unresolved_bucket,
            "total": total,
        }

    def search(self, collection: str, query: str, *, size: int = 25, page: int = 1,
               sort: str | None = None, deadline: float | None = None) -> dict[str, Any]:
        """Fetch a bounded public search response, or raise ``RemoteError``."""
        self._validate_request(collection, query, size, page, sort)
        end = self._deadline(deadline)
        key = (collection, query, size, page, sort)
        author_ids = self._exact_author_ids(query) if collection == "authors" else None
        reusable_author_ids = author_ids is not None and page == 1 and len(author_ids) <= size
        if reusable_author_ids:
            cached_authors = self._cached_author_ids(author_ids, size=size, page=page, now=self._clock())
            if cached_authors is not None:
                self._count("authors", "hits")
                self._count("authors", "record_hits")
                return cached_authors
            self._count("authors", "record_misses")

        def load() -> dict[str, Any]:
            self._reserve_request(end)
            params = {
                "q": query, "size": size, "page": page,
                "fields": LITERATURE_FIELDS if collection == "literature" else AUTHOR_FIELDS,
            }
            if sort is not None:
                params["sort"] = sort
            url = f"{API_ROOT}/{collection}?{urlencode(params)}"
            value = self._fetch_json(url, end, self._cache_layer(key))
            response = self._sanitized_response(collection, self._validate_response(value, size))
            if collection == "authors":
                self._index_author_records(response, self._clock())
            return response

        # Exact ID requests are represented by their individual record entries.
        # Avoid storing a duplicate query response; incomplete/empty exact-ID
        # responses therefore cannot become negative-cache evidence either.
        return self._request(key, end, load, cache_response=not reusable_author_ids)

    def coauthors(self, query: str, *, deadline: float | None = None) -> dict[str, Any]:
        """Return bounded server-side coauthor discovery hints from INSPIRE."""
        self._validate_query(query)
        end = self._deadline(deadline)
        key = ("facets", query, 0, 0, None)

        def load() -> dict[str, Any]:
            self._reserve_request(end)
            url = f"{API_ROOT}/literature/facets?{urlencode({'q': query})}"
            value = self._fetch_json(url, end, "facets")
            return self._sanitized_coauthors_response(value)

        return self._request(key, end, load)

    def cache_info(self) -> dict[str, Any]:
        with self._cache_lock:
            self._evict_expired(self._clock())
            cache_bytes = self._cache_bytes
            cache_entries = len(self._cache)
            usage = {layer: {"bytes": 0, "entries": 0} for layer in self._stats}
            author_record_entries = 0
            for key, entry in self._cache.items():
                layer = self._cache_layer(key)
                usage[layer]["bytes"] += entry.size
                usage[layer]["entries"] += 1
                if len(key) == 2 and key[0] == "author_record":
                    author_record_entries += 1
            with self._stats_lock:
                layers = {
                    layer: usage[layer] | {
                        field: int(self._stats[layer].get(field, 0))
                        for field in ("hits", "misses", "coalesced", "upstream_requests",
                                      "errors", "rejected", "wait_deadlines", "wire_bytes")
                    }
                    for layer in self._stats
                }
                layers["authors"]["record_entries"] = author_record_entries
                for field in ("record_hits", "record_misses", "records_indexed"):
                    layers["authors"][field] = int(self._stats["authors"].get(field, 0))
        with self._pending_lock:
            pending = len(self._pending)
        totals = {
            field: sum(row[field] for row in layers.values())
            for field in ("hits", "misses", "coalesced", "upstream_requests",
                          "errors", "rejected", "wait_deadlines", "wire_bytes")
        }
        return {"bytes": cache_bytes, "limit": self._cache_limit, "entries": cache_entries,
                "ttl_seconds": self._ttl_seconds, "storage": "memory", "persistent": False,
                "inflight": pending, "inflight_limit": MAX_INFLIGHT, "layers": layers, **totals}

    def clear_cache(self) -> None:
        with self._cache_lock:
            self._cache.clear()
            self._cache_bytes = 0
