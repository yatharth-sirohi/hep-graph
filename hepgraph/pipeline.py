"""Restartable, privacy-minimising importer for a small INSPIRE graph.

The database is deliberately the durable representation.  ``current.json`` is
only a reproducible, atomically-published view of that database.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener


API_ROOT = "https://inspirehep.net/api"
PAGE_SIZE = 1000
MAX_QUERY_RESULTS = 10_000
REQUEST_INTERVAL = 1.0
LITERATURE_FIELDS = (
    "control_number,titles.title,document_type,authors.full_name,authors.record,"
    "authors.inspire_roles,authors.affiliations.value,author_count,earliest_date,"
    "arxiv_eprints.value,dois.value,deleted,new_record,deleted_records,"
    "preprint_date,imprints.date,publication_info.year,collaborations.value,"
    "thesis_info.degree_type,thesis_info.date"
)
AUTHOR_FIELDS = (
    "control_number,name.value,name.preferred_name,name.name_variants,ids.schema,"
    "ids.value,positions.institution,positions.current,advisors.degree_type,"
    "advisors.record,advisors.name,advisors.curated_relation,advisors.hidden,"
    "death_date,"
    "deleted,new_record,deleted_records"
)


class PipelineError(ValueError):
    """A malformed manifest or source payload."""


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ref_id(value: Any) -> str | None:
    """Extract a numerical INSPIRE record ID from the accepted $ref forms."""
    if isinstance(value, dict):
        value = value.get("$ref") or value.get("recid")
    if isinstance(value, int):
        return str(value)
    if not isinstance(value, str):
        return None
    match = re.search(r"(?:authors|literature)/(\d+)(?:/?$|[?#])", value)
    if match:
        return match.group(1)
    return value if value.isdigit() else None


def source_url(collection: str, recid: str) -> str:
    return f"https://inspirehep.net/{collection}/{recid}"


def _string(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _metadata(hit: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if not isinstance(hit, dict):
        raise PipelineError("source record must be an object")
    data = hit.get("metadata") if isinstance(hit.get("metadata"), dict) else hit
    recid = hit.get("id") or data.get("control_number")
    if isinstance(recid, int):
        recid = str(recid)
    if not isinstance(recid, str) or not recid.isdigit():
        raise PipelineError("source record has no numeric id/control_number")
    return recid, data


def _ref_list(value: Any) -> list[str]:
    values = value if isinstance(value, list) else [value]
    return [item for item in (ref_id(v) for v in values) if item]


def sanitize_literature(hit: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Keep exactly the requested fields before anything reaches disk."""
    recid, data = _metadata(hit)
    authors: list[dict[str, Any]] = []
    raw_authors = data.get("authors", [])
    if raw_authors is not None and not isinstance(raw_authors, list):
        raise PipelineError("literature.authors must be an array")
    for item in _list(raw_authors):
        if not isinstance(item, dict):
            raise PipelineError("literature author must be an object")
        affiliations = []
        raw_affiliations = item.get("affiliations", [])
        if raw_affiliations is not None and not isinstance(raw_affiliations, list):
            raise PipelineError("author affiliations must be an array")
        for affiliation in _list(raw_affiliations):
            if isinstance(affiliation, dict) and _string(affiliation.get("value")):
                affiliations.append(affiliation["value"].strip())
        record = ref_id(item.get("record"))
        authors.append({
            "full_name": _string(item.get("full_name")),
            "record": record,
            "inspire_roles": _strings(item.get("inspire_roles")),
            "affiliations": affiliations,
        })
    titles: list[str] = []
    raw_titles = data.get("titles", [])
    if raw_titles is not None and not isinstance(raw_titles, list):
        raise PipelineError("literature.titles must be an array")
    for title in _list(raw_titles):
        if isinstance(title, dict) and _string(title.get("title")):
            titles.append(title["title"].strip())
    document_types = _strings(data.get("document_type"))
    for field in ("dois", "arxiv_eprints", "imprints", "publication_info", "collaborations"):
        if data.get(field) is not None and not isinstance(data.get(field), list):
            raise PipelineError(f"literature.{field} must be an array")
    dois = [x["value"].strip() for x in _list(data.get("dois"))
            if isinstance(x, dict) and _string(x.get("value"))]
    arxiv = [x["value"].strip() for x in _list(data.get("arxiv_eprints"))
             if isinstance(x, dict) and _string(x.get("value"))]
    count = data.get("author_count", 0)
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        raise PipelineError("literature.author_count must be a non-negative integer")
    thesis = data.get("thesis_info", {})
    if thesis is not None and not isinstance(thesis, dict):
        raise PipelineError("literature.thesis_info must be an object")
    return recid, {
        "control_number": recid,
        "titles": titles,
        "document_type": document_types,
        "authors": authors,
        "author_count": count,
        "earliest_date": _string(data.get("earliest_date")),
        "preprint_date": _string(data.get("preprint_date")),
        "imprints": [item["date"].strip() for item in _list(data.get("imprints")) if isinstance(item, dict) and _string(item.get("date"))],
        "publication_years": [str(item["year"]) for item in _list(data.get("publication_info")) if isinstance(item, dict) and isinstance(item.get("year"), int) and 1000 <= item["year"] <= 2100],
        "collaborations": [item["value"].strip() for item in _list(data.get("collaborations")) if isinstance(item, dict) and _string(item.get("value"))],
        "arxiv_eprints": arxiv,
        "dois": dois,
        "deleted": data.get("deleted") is True,
        "new_record": _ref_list(data.get("new_record")),
        "deleted_records": _ref_list(data.get("deleted_records")),
        "thesis_info": {"degree_type": _string(thesis.get("degree_type")), "date": _string(thesis.get("date"))},
        "source_updated_at": _string(hit.get("updated")) or _string(data.get("updated")),
    }


def sanitize_author(hit: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    recid, data = _metadata(hit)
    name = data.get("name", {})
    if name is not None and not isinstance(name, dict):
        raise PipelineError("author.name must be an object")
    if isinstance(name, dict) and name.get("name_variants") is not None and not isinstance(name.get("name_variants"), list):
        raise PipelineError("author.name.name_variants must be an array")
    variants = _strings(name.get("name_variants") if isinstance(name, dict) else [])
    ids: list[dict[str, str]] = []
    raw_ids = data.get("ids", [])
    if raw_ids is not None and not isinstance(raw_ids, list):
        raise PipelineError("author.ids must be an array")
    for identifier in _list(raw_ids):
        if not isinstance(identifier, dict):
            raise PipelineError("author identifier must be an object")
        schema, value = _string(identifier.get("schema")), _string(identifier.get("value"))
        if schema and value and schema.lower() in {"orcid", "inspire bai", "inspire id"}:
            ids.append({"schema": schema, "value": value})
    positions: list[dict[str, Any]] = []
    raw_positions = data.get("positions", [])
    if raw_positions is not None and not isinstance(raw_positions, list):
        raise PipelineError("author.positions must be an array")
    for position in _list(raw_positions):
        if isinstance(position, dict) and _string(position.get("institution")):
            positions.append({"institution": position["institution"].strip(), "current": position.get("current") is True})
    advisers: list[dict[str, Any]] = []
    raw_advisers = data.get("advisors", [])
    if raw_advisers is not None and not isinstance(raw_advisers, list):
        raise PipelineError("author.advisors must be an array")
    for adviser in _list(raw_advisers):
        if not isinstance(adviser, dict):
            raise PipelineError("author advisor must be an object")
        advisers.append({
            "degree_type": _string(adviser.get("degree_type")),
            "record": ref_id(adviser.get("record")),
            "name": _string(adviser.get("name")),
            "curated_relation": adviser.get("curated_relation") is True,
            "hidden": adviser.get("hidden") is True,
        })
    result = {
        "control_number": recid,
        "name": {
            "value": _string(name.get("value") if isinstance(name, dict) else None),
            "preferred_name": _string(name.get("preferred_name") if isinstance(name, dict) else None),
            "name_variants": variants,
        },
        "ids": ids,
        "positions": positions,
        "advisors": advisers,
        "deleted": data.get("deleted") is True,
        "new_record": _ref_list(data.get("new_record")),
        "deleted_records": _ref_list(data.get("deleted_records")),
        "source_updated_at": _string(hit.get("updated")) or _string(data.get("updated")),
    }
    # This is public profile metadata used only as a conservative review signal.
    # Omit it altogether when the profile does not supply it so old snapshots
    # and fixtures retain their existing shape.
    death_date = _string(data.get("death_date"))
    if death_date:
        result["death_date"] = death_date
    return recid, result


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS source_records (
 collection TEXT NOT NULL, recid TEXT NOT NULL, payload TEXT NOT NULL,
 retrieved_at TEXT NOT NULL, updated_at TEXT, deleted INTEGER NOT NULL DEFAULT 0,
 PRIMARY KEY(collection, recid));
CREATE TABLE IF NOT EXISTS replacements (
 collection TEXT NOT NULL, old_id TEXT NOT NULL, new_id TEXT NOT NULL,
 source_id TEXT NOT NULL, PRIMARY KEY(collection, old_id, new_id));
CREATE TABLE IF NOT EXISTS query_checkpoints (
 query_key TEXT PRIMARY KEY, collection TEXT NOT NULL, query TEXT NOT NULL,
 requested_limit INTEGER NOT NULL, sort TEXT, next_page INTEGER NOT NULL DEFAULT 1,
 complete INTEGER NOT NULL DEFAULT 0, error TEXT, updated_at TEXT NOT NULL,
 upstream_total INTEGER, received_count INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS ingestion_state (
 name TEXT PRIMARY KEY, complete INTEGER NOT NULL, error TEXT, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS ingestion_manifest (
 name TEXT PRIMARY KEY, payload TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS authorship_occurrences (
 record_id TEXT NOT NULL, position INTEGER NOT NULL, person_id TEXT,
 full_name TEXT, affiliations TEXT NOT NULL, roles TEXT NOT NULL,
 PRIMARY KEY(record_id, position));
CREATE TABLE IF NOT EXISTS works (
 work_id TEXT PRIMARY KEY, payload TEXT NOT NULL, source_ids TEXT NOT NULL,
 built_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS people (
 person_id TEXT PRIMARY KEY, payload TEXT NOT NULL, built_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS doctoral_audit (
 evidence_kind TEXT NOT NULL, source_record TEXT NOT NULL, subject_id TEXT,
 adviser_id TEXT, reason TEXT NOT NULL, payload TEXT NOT NULL,
 created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS dedup_conflicts (
 identifier TEXT NOT NULL, record_ids TEXT NOT NULL, reason TEXT NOT NULL,
 created_at TEXT NOT NULL, PRIMARY KEY(identifier, record_ids));
CREATE TABLE IF NOT EXISTS redirect_conflicts (
 collection TEXT NOT NULL, record_ids TEXT NOT NULL, reason TEXT NOT NULL,
 created_at TEXT NOT NULL, PRIMARY KEY(collection, record_ids, reason));
CREATE TABLE IF NOT EXISTS identifier_aliases (
 kind TEXT NOT NULL, identifier TEXT NOT NULL, record_id TEXT NOT NULL,
 PRIMARY KEY(kind, identifier, record_id));
"""


def open_db(path: str | Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    # Existing pilot databases may predate the resumability counters.
    known = {row[1] for row in connection.execute("PRAGMA table_info(query_checkpoints)")}
    if "upstream_total" not in known:
        connection.execute("ALTER TABLE query_checkpoints ADD COLUMN upstream_total INTEGER")
    if "received_count" not in known:
        connection.execute("ALTER TABLE query_checkpoints ADD COLUMN received_count INTEGER NOT NULL DEFAULT 0")
    return connection


def _replace_refs(connection: sqlite3.Connection, collection: str, recid: str, payload: dict[str, Any]) -> None:
    # A deleted source record points forward via new_record; a replacement record
    # points backward through deleted_records.
    connection.execute("DELETE FROM replacements WHERE collection=? AND source_id=?", (collection, recid))
    for target in payload.get("new_record", []):
        connection.execute("INSERT OR REPLACE INTO replacements VALUES(?,?,?,?)", (collection, recid, target, recid))
    for old in payload.get("deleted_records", []):
        connection.execute("INSERT OR REPLACE INTO replacements VALUES(?,?,?,?)", (collection, old, recid, recid))


def store_record(connection: sqlite3.Connection, collection: str, hit: dict[str, Any], *, retrieved_at: str | None = None) -> str:
    if collection == "literature":
        recid, payload = sanitize_literature(hit)
    elif collection == "authors":
        recid, payload = sanitize_author(hit)
    else:
        raise PipelineError(f"unsupported collection {collection!r}")
    return _store_sanitized(connection, collection, recid, payload, retrieved_at=retrieved_at)


def _store_sanitized(connection: sqlite3.Connection, collection: str, recid: str, payload: dict[str, Any], *,
                     retrieved_at: str | None = None) -> str:
    """Persist a payload which has already passed the collection sanitizer."""
    now = retrieved_at or utc_now()
    with connection:
        connection.execute(
            "INSERT INTO source_records(collection,recid,payload,retrieved_at,updated_at,deleted) VALUES(?,?,?,?,?,?) "
            "ON CONFLICT(collection,recid) DO UPDATE SET payload=excluded.payload,retrieved_at=excluded.retrieved_at,updated_at=excluded.updated_at,deleted=excluded.deleted",
            (collection, recid, json.dumps(payload, sort_keys=True), now, payload.get("source_updated_at") or now, int(payload["deleted"])),
        )
        _replace_refs(connection, collection, recid, payload)
        if collection == "literature":
            connection.execute("DELETE FROM authorship_occurrences WHERE record_id=?", (recid,))
            for position, author in enumerate(payload["authors"]):
                connection.execute("INSERT INTO authorship_occurrences VALUES(?,?,?,?,?,?)", (
                    recid, position, author["record"], author["full_name"],
                    json.dumps(author["affiliations"]), json.dumps(author["inspire_roles"]),
                ))
            connection.execute("DELETE FROM identifier_aliases WHERE record_id=?", (recid,))
            for doi in payload["dois"]:
                connection.execute("INSERT OR IGNORE INTO identifier_aliases VALUES(?,?,?)", ("doi", normalise_doi(doi), recid))
            for arxiv in payload["arxiv_eprints"]:
                connection.execute("INSERT OR IGNORE INTO identifier_aliases VALUES(?,?,?)", ("arxiv", normalise_arxiv(arxiv), recid))
    return recid


def normalise_doi(value: str) -> str:
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value.strip().lower()).rstrip(".")


def normalise_arxiv(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"^(?:arxiv:)?", "", value)
    return re.sub(r"v\d+$", "", value)


def load_manifest(path: str | Path) -> dict[str, Any]:
    try:
        manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PipelineError(f"cannot read manifest: {exc}") from exc
    if not isinstance(manifest, dict) or not _string(manifest.get("label")):
        raise PipelineError("manifest.label must be a non-empty string")
    if "description" in manifest and not isinstance(manifest["description"], str):
        raise PipelineError("manifest.description must be a string")
    for collection in ("literature", "authors"):
        entries = manifest.get(collection, [])
        if not isinstance(entries, list):
            raise PipelineError(f"manifest.{collection} must be an array")
        for entry in entries:
            if not isinstance(entry, dict) or not _string(entry.get("query")):
                raise PipelineError(f"every manifest.{collection} entry needs query")
            limit = entry.get("limit")
            if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= MAX_QUERY_RESULTS:
                raise PipelineError(f"manifest.{collection}.limit must be 1..{MAX_QUERY_RESULTS}")
            if collection == "literature" and "sort" in entry and not isinstance(entry["sort"], str):
                raise PipelineError("manifest.literature.sort must be a string")
    examples = manifest.get("examples", [])
    if not isinstance(examples, list):
        raise PipelineError("manifest.examples must be an array")
    return manifest


def query_key(collection: str, query: str, limit: int, sort: str | None) -> str:
    text = json.dumps([collection, query, limit, sort], separators=(",", ":"))
    return hashlib.sha256(text.encode()).hexdigest()


class InspireClient:
    """Small sequential client.  Callers may replace ``fetch`` in tests."""
    def __init__(self) -> None:
        self._last_request = 0.0

    def fetch(self, collection: str, query: str, page: int, size: int, sort: str | None = None) -> dict[str, Any]:
        params = {"q": query, "page": page, "size": size,
                  "fields": LITERATURE_FIELDS if collection == "literature" else AUTHOR_FIELDS}
        if sort:
            params["sort"] = sort
        url = f"{API_ROOT}/{collection}?{urlencode(params)}"
        attempt = 0
        while True:
            wait = REQUEST_INTERVAL - (time.monotonic() - self._last_request)
            if wait > 0:
                time.sleep(wait)
            try:
                request = Request(url, headers={"Accept": "application/json", "User-Agent": "hep-graph/1"})
                # Redirects are not followed: the collection endpoint above is
                # part of the data boundary and a redirect could widen it.
                class NoRedirect(HTTPRedirectHandler):
                    def redirect_request(self, req: Request, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
                        return None
                with build_opener(NoRedirect()).open(request, timeout=30) as response:  # fixed HTTPS host above
                    self._last_request = time.monotonic()
                    return json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                self._last_request = time.monotonic()
                if exc.code != 429 and not 500 <= exc.code <= 599:
                    raise PipelineError(f"INSPIRE HTTP {exc.code}") from exc
                attempt += 1
                if attempt >= 5:
                    raise PipelineError(f"INSPIRE HTTP {exc.code} after {attempt} attempts") from exc
                retry = exc.headers.get("Retry-After")
                try:
                    delay = min(60.0, max(5.0, float(retry))) if retry else min(60.0, 5.0 * (2 ** (attempt - 1)))
                except ValueError:
                    delay = min(60.0, 5.0 * (2 ** (attempt - 1)))
                time.sleep(delay)
            except URLError as exc:
                self._last_request = time.monotonic()
                attempt += 1
                if attempt >= 5:
                    raise PipelineError(f"INSPIRE request failed after {attempt} attempts: {exc}") from exc
                time.sleep(min(60.0, 5.0 * (2 ** (attempt - 1))))
            except json.JSONDecodeError as exc:
                raise PipelineError(f"INSPIRE response was not JSON: {exc}") from exc


def _hits(response: dict[str, Any]) -> list[dict[str, Any]]:
    hits = response.get("hits", {}) if isinstance(response, dict) else {}
    rows = hits.get("hits", []) if isinstance(hits, dict) else []
    if not isinstance(rows, list) or not all(isinstance(item, dict) for item in rows):
        raise PipelineError("INSPIRE response lacks hits.hits array")
    return rows


def _upstream_total(response: dict[str, Any]) -> int | None:
    hits = response.get("hits", {}) if isinstance(response, dict) else {}
    total = hits.get("total") if isinstance(hits, dict) else None
    if isinstance(total, int) and total >= 0:
        return total
    if isinstance(total, dict) and isinstance(total.get("value"), int) and total["value"] >= 0:
        return total["value"]
    return None


def _cached_hit(collection: str, recid: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Return a re-validatable API-shaped object containing allowlisted data only."""
    if collection == "literature":
        metadata = {
            "control_number": recid, "titles": [{"title": title} for title in payload["titles"]],
            "document_type": payload["document_type"],
            "authors": [{"full_name": author["full_name"], "record": {"$ref": f"https://inspirehep.net/api/authors/{author['record']}"} if author["record"] else None,
                         "inspire_roles": author["inspire_roles"], "affiliations": [{"value": x} for x in author["affiliations"]]} for author in payload["authors"]],
            "author_count": payload["author_count"], "earliest_date": payload["earliest_date"], "preprint_date": payload["preprint_date"],
            "imprints": [{"date": x} for x in payload["imprints"]], "publication_info": [{"year": int(x)} for x in payload["publication_years"]],
            "collaborations": [{"value": x} for x in payload["collaborations"]], "arxiv_eprints": [{"value": x} for x in payload["arxiv_eprints"]],
            "dois": [{"value": x} for x in payload["dois"]], "deleted": payload["deleted"], "new_record": payload["new_record"], "deleted_records": payload["deleted_records"],
            "thesis_info": payload["thesis_info"],
        }
    else:
        metadata = {"control_number": recid, "name": payload["name"], "ids": payload["ids"], "positions": payload["positions"],
                    "advisors": [{**item, "record": {"$ref": f"https://inspirehep.net/api/authors/{item['record']}"} if item["record"] else None} for item in payload["advisors"]],
                    "deleted": payload["deleted"], "new_record": payload["new_record"], "deleted_records": payload["deleted_records"]}
        if payload.get("death_date"):
            metadata["death_date"] = payload["death_date"]
    hit: dict[str, Any] = {"id": recid, "metadata": metadata}
    if payload.get("source_updated_at"): hit["updated"] = payload["source_updated_at"]
    return hit


def _read_cache_page(path: Path, collection: str) -> tuple[str, list[tuple[str, dict[str, Any]]]] | None:
    try:
        cached = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(cached, dict) or not isinstance(cached.get("retrieved_at"), str) or not isinstance(cached.get("records"), list):
            return None
        rows = cached["records"]
        sanitised = [sanitize_literature(row) if collection == "literature" else sanitize_author(row) for row in rows]
        return cached["retrieved_at"], sanitised
    except (OSError, json.JSONDecodeError, PipelineError):
        return None


def ingest_manifest(connection: sqlite3.Connection, manifest: dict[str, Any], *, cache: str | Path,
                    refresh: bool = False, client: InspireClient | None = None) -> dict[str, Any]:
    """Ingest a manifest, committing every page and cache file independently."""
    cache_path = Path(cache)
    cache_path.mkdir(parents=True, exist_ok=True)
    client = client or InspireClient()
    result = {"queries": 0, "records": 0, "failures": []}
    with connection:
        connection.execute("INSERT INTO ingestion_manifest VALUES('active',?,?) ON CONFLICT(name) DO UPDATE SET payload=excluded.payload,updated_at=excluded.updated_at",
                           (json.dumps(manifest, sort_keys=True), utc_now()))
    for collection in ("literature", "authors"):
        for entry in manifest.get(collection, []):
            query, limit = entry["query"], entry["limit"]
            sort = entry.get("sort") if collection == "literature" else None
            key = query_key(collection, query, limit, sort)
            checkpoint = connection.execute("SELECT * FROM query_checkpoints WHERE query_key=?", (key,)).fetchone()
            if checkpoint and checkpoint["complete"] and not refresh:
                continue
            page = 1 if refresh else (checkpoint["next_page"] if checkpoint else 1)
            page_size = min(PAGE_SIZE, limit)
            with connection:
                connection.execute(
                    "INSERT INTO query_checkpoints(query_key,collection,query,requested_limit,sort,next_page,complete,error,updated_at,upstream_total,received_count) VALUES(?,?,?,?,?,?,0,NULL,?,NULL,0) "
                    "ON CONFLICT(query_key) DO UPDATE SET next_page=excluded.next_page,complete=0,error=NULL,updated_at=excluded.updated_at,received_count=CASE WHEN ? THEN 0 ELSE received_count END,upstream_total=CASE WHEN ? THEN NULL ELSE upstream_total END",
                    (key, collection, query, limit, sort, page, utc_now(), int(refresh), int(refresh)),
                )
            result["queries"] += 1
            remaining = limit - (page - 1) * page_size
            try:
                while remaining > 0:
                    cache_file = cache_path / f"{key}-{page}.json"
                    cached = None if refresh else _read_cache_page(cache_file, collection)
                    upstream_total = None
                    if cached:
                        retrieved_at, sanitized = cached
                        rows_count = len(sanitized)
                    else:
                        response = client.fetch(collection, query, page, page_size, sort)
                        upstream_total = _upstream_total(response)
                        response_rows = _hits(response)
                        # A final page deliberately retains the same server page
                        # size, then slices locally. Changing size changes offset.
                        response_rows = response_rows[:remaining]
                        sanitized = [sanitize_literature(row) if collection == "literature" else sanitize_author(row) for row in response_rows]
                        retrieved_at = utc_now()
                        rows_count = len(response_rows)
                        # The cache is API-shaped but contains only the fields
                        # that have already survived sanitisation.
                        cache_value = {"retrieved_at": retrieved_at, "records": [_cached_hit(collection, recid, payload) for recid, payload in sanitized]}
                        temp = cache_file.with_suffix(".tmp")
                        temp.write_text(json.dumps(cache_value, sort_keys=True), encoding="utf-8")
                        os.replace(temp, cache_file)
                    for recid, payload in sanitized:
                        _store_sanitized(connection, collection, recid, payload, retrieved_at=retrieved_at)
                    with connection:
                        connection.execute("UPDATE query_checkpoints SET next_page=?,updated_at=?,upstream_total=COALESCE(?,upstream_total),received_count=received_count+? WHERE query_key=?", (page + 1, utc_now(), upstream_total, rows_count, key))
                    result["records"] += rows_count
                    if rows_count < page_size:
                        break
                    page += 1
                    remaining -= rows_count
                with connection:
                    connection.execute("UPDATE query_checkpoints SET complete=1,error=NULL,updated_at=? WHERE query_key=?", (utc_now(), key))
            # A test or a future transport adapter can raise a normal runtime
            # exception too.  Persist it as a resumable query failure rather
            # than losing the checkpoint after a successful earlier page.
            except (Exception,) as exc:
                with connection:
                    connection.execute("UPDATE query_checkpoints SET complete=0,error=?,updated_at=? WHERE query_key=?", (str(exc), utc_now(), key))
                result["failures"].append({"collection": collection, "query": query, "error": str(exc)})
    with connection:
        connection.execute("INSERT INTO ingestion_state VALUES('manifest',?,?,?) ON CONFLICT(name) DO UPDATE SET complete=excluded.complete,error=excluded.error,updated_at=excluded.updated_at",
                           (int(not result["failures"]), json.dumps(result["failures"]) if result["failures"] else None, utc_now()))
    return result


def import_jsonl(connection: sqlite3.Connection, path: str | Path) -> dict[str, Any]:
    imported, failures = 0, []
    with Path(path).open(encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
                if not isinstance(item, dict):
                    raise PipelineError("JSONL line must be an object")
                collection = item.get("collection") or item.get("kind") or item.get("type")
                if collection not in {"literature", "authors"}:
                    raise PipelineError("JSONL collection must be literature or authors")
                record = item.get("record", item.get("payload", item))
                if not isinstance(record, dict):
                    raise PipelineError("JSONL record must be an object")
                store_record(connection, collection, record)
                imported += 1
            except (json.JSONDecodeError, PipelineError, OSError, sqlite3.Error) as exc:
                failures.append({"line": line_no, "error": str(exc)})
    with connection:
        connection.execute("INSERT INTO ingestion_state VALUES('jsonl',?,?,?) ON CONFLICT(name) DO UPDATE SET complete=excluded.complete,error=excluded.error,updated_at=excluded.updated_at",
                           (int(not failures), json.dumps(failures) if failures else None, utc_now()))
    return {"records": imported, "failures": failures}


def _redirects(connection: sqlite3.Connection, collection: str) -> dict[str, str]:
    rows = connection.execute("SELECT old_id,new_id FROM replacements WHERE collection=?", (collection,)).fetchall()
    targets: dict[str, set[str]] = defaultdict(set)
    for row in rows: targets[row["old_id"]].add(row["new_id"])
    direct: dict[str, str] = {}
    for old, choices in targets.items():
        if len(choices) == 1:
            direct[old] = next(iter(choices))
        else:
            with connection:
                connection.execute("INSERT OR IGNORE INTO redirect_conflicts VALUES(?,?,?,?)", (collection, json.dumps(sorted([old, *choices])), "multiple replacement targets", utc_now()))
    resolved: dict[str, str] = {}
    for start in direct:
        seen, current = set(), start
        while current in direct and current not in seen:
            seen.add(current); current = direct[current]
        if current in seen:
            with connection:
                connection.execute("INSERT OR IGNORE INTO redirect_conflicts VALUES(?,?,?,?)", (collection, json.dumps(sorted(seen)), "replacement cycle", utc_now()))
            continue
        resolved[start] = current
    return resolved


def _tombstones(connection: sqlite3.Connection, collection: str, redirects: dict[str, str]) -> set[str]:
    rows = connection.execute("SELECT recid FROM source_records WHERE collection=? AND deleted=1", (collection,)).fetchall()
    return {row["recid"] for row in rows if row["recid"] not in redirects}


def _coauthor(author: dict[str, Any]) -> bool:
    roles = {role.lower() for role in author.get("inspire_roles", [])}
    return not roles or "author" in roles


def _author_members(payload: dict[str, Any], person_redirects: dict[str, str], tombstones: set[str] = frozenset()) -> tuple[list[dict[str, Any]], set[str]]:
    selected = [author for author in payload["authors"] if _coauthor(author)]
    members = {person_redirects.get(author["record"], author["record"]) for author in selected if author["record"] and author["record"] not in tombstones}
    return selected, members


def _work_groups(connection: sqlite3.Connection, rows: list[sqlite3.Row], person_redirects: dict[str, str], tombstones: set[str]) -> list[list[tuple[sqlite3.Row, dict[str, Any]]]]:
    """Merge identifier-equal records only when observed memberships agree.

    We intentionally leave a contradictory DOI/arXiv pair separate.  Combining
    their author lists would manufacture collaborations which neither source
    record establishes.
    """
    records = [(row, json.loads(row["payload"])) for row in rows]
    by_identifier: dict[str, list[int]] = defaultdict(list)
    for index, (_, payload) in enumerate(records):
        for identifier in {f"doi:{normalise_doi(v)}" for v in payload["dois"]} | {f"arxiv:{normalise_arxiv(v)}" for v in payload["arxiv_eprints"]}:
            by_identifier[identifier].append(index)
    parent = list(range(len(records)))
    component_members = [_author_members(payload, person_redirects, tombstones)[1] for _, payload in records]
    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]; value = parent[value]
        return value
    def union(a: int, b: int) -> None:
        a, b = find(a), find(b)
        if a != b:
            parent[b] = a
            component_members[a] = component_members[a] or component_members[b]
    for identifier, indices in by_identifier.items():
        roots = {find(index) for index in indices}
        known_memberships = {frozenset(component_members[root]) for root in roots if component_members[root]}
        if len(known_memberships) <= 1:
            # Empty identity sets cannot prove a conflict, but do not bridge two
            # contradictory non-empty components (the branch below handles that).
            roots = list(roots)
            for root in roots[1:]:
                union(roots[0], root)
        else:
            ids = json.dumps(sorted(records[index][0]["recid"] for index in indices))
            with connection:
                connection.execute("INSERT OR IGNORE INTO dedup_conflicts VALUES(?,?,?,?)", (identifier, ids, "conflicting resolved author memberships", utc_now()))
            # The exact identifier still says these are versions of one work.
            # Select one authoritative complete record below; never union the
            # different author lists into a fabricated collaboration list.
            roots = list(roots)
            for root in roots[1:]:
                union(roots[0], root)
    groups: dict[int, list[tuple[sqlite3.Row, dict[str, Any]]]] = defaultdict(list)
    for index, record in enumerate(records): groups[find(index)].append(record)
    return list(groups.values())


_CORRECTION_TITLE = re.compile(r"^\s*(?:erratum|errata|corrigendum)(?=$|\W)", re.IGNORECASE)


def _is_correction(payload: dict[str, Any]) -> bool:
    return any(_CORRECTION_TITLE.match(title) for title in payload.get("titles", [])
               if isinstance(title, str))


def _best_record(group: list[tuple[sqlite3.Row, dict[str, Any]]], person_redirects: dict[str, str], tombstones: set[str]) -> tuple[sqlite3.Row, dict[str, Any], list[dict[str, Any]]]:
    def score(record: tuple[sqlite3.Row, dict[str, Any]]) -> tuple[int, int, int, int, str]:
        row, payload = record
        authors, _ = _author_members(payload, person_redirects, tombstones)
        # An erratum shares its original's DOI, so it lands in the same group.
        # With identical author lists the tie-break used to fall through to
        # recid order, and a correction that sorted higher became the group's
        # representative - which the graph then rejects as a standalone
        # correction, erasing the real paper and the collaboration with it.
        return (0 if _is_correction(payload) else 1,
                max(len(authors), payload["author_count"]), len(authors),
                len(payload["titles"]), row["recid"])
    row, payload = max(group, key=score)
    authors, _ = _author_members(payload, person_redirects, tombstones)
    return row, payload, authors


def _documented_date(payloads: Iterable[dict[str, Any]]) -> tuple[str | None, str]:
    """Choose the earliest documented date without throwing away precision.

    The public ``earliest_date`` field needs special handling.  INSPIRE's
    server-side property falls back to the record's ``created`` timestamp when
    it cannot derive a scholarly date.  We do not request or publish that
    database timestamp.  Therefore an ``earliest_date`` is usable only when a
    selected scholarly field on the same source record corroborates its known
    precision: preprint, imprint, thesis, or publication year.  For example,
    ``2020-02`` is corroborated by an imprint on ``2020-02-03``; a publication
    year alone corroborates only an ``earliest_date`` of ``2020``.

    INSPIRE's ``publication_info.year`` is often a bare year while a supported
    ``earliest_date`` contains a month or day in that same year.  A year can
    still establish that publication evidence is genuinely earlier than a
    later preprint year.  Within the earliest year, a supported
    ``earliest_date`` preserves its reported precision: a later journal issue
    must not replace an earlier arXiv month just because it has a day.  If
    there is no supported earliest date, use the earliest selected scholarly
    date and leave the value unknown if none exists.
    """
    source_order = {"earliest_date": 0, "preprint_date": 1, "imprints.date": 2, "thesis_info.date": 3, "publication_info.year": 4}

    def parse(date: Any, source: str) -> tuple[int, int, int, int, int, str, str] | None:
        if not isinstance(date, str):
            return None
        match = re.fullmatch(r"(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?", date)
        if not match:
            return None
        year, month, day = int(match.group(1)), match.group(2), match.group(3)
        month_value = int(month) if month else 1
        day_value = int(day) if day else 1
        precision = 2 if day else (1 if month else 0)
        try:
            datetime(year, month_value, day_value)
        except ValueError:
            return None
        return year, month_value, day_value, precision, source_order[source], date, source

    def corroborates(earliest: tuple[int, int, int, int, int, str, str],
                     scholarly: Iterable[tuple[int, int, int, int, int, str, str]]) -> bool:
        """Return whether evidence covers every part reported by earliest.

        A coarser source cannot establish an invented day or month.  Conversely
        a more precise real source can corroborate an INSPIRE earliest date at
        its reported precision.
        """
        for evidence in scholarly:
            if evidence[3] < earliest[3] or evidence[0] != earliest[0]:
                continue
            if earliest[3] >= 1 and evidence[1] != earliest[1]:
                continue
            if earliest[3] >= 2 and evidence[2] != earliest[2]:
                continue
            return True
        return False

    candidates: list[tuple[int, int, int, int, int, str, str]] = []
    for payload in payloads:
        thesis = payload.get("thesis_info")
        thesis_date = thesis.get("date") if isinstance(thesis, dict) else None
        imprints = payload.get("imprints")
        publication_years = payload.get("publication_years")
        if not isinstance(imprints, list):
            imprints = []
        if not isinstance(publication_years, list):
            publication_years = []
        scholarly = [
            item for item in (
                parse(payload.get("preprint_date"), "preprint_date"),
                *(parse(date, "imprints.date") for date in imprints),
                parse(thesis_date, "thesis_info.date"),
                *(parse(date, "publication_info.year") for date in publication_years),
            ) if item is not None
        ]
        candidates.extend(scholarly)
        earliest = parse(payload.get("earliest_date"), "earliest_date")
        if earliest is not None and corroborates(earliest, scholarly):
            candidates.append(earliest)
    if not candidates:
        return None, "unknown"
    earliest_year = min(item[0] for item in candidates)
    in_year = [item for item in candidates if item[0] == earliest_year]
    primary = [item for item in in_year if item[6] == "earliest_date"]
    if primary:
        # Documented API semantics define this as the record's earliest date.
        # Preserve its precision rather than replacing (say) 2012-07 with the
        # later, more precise journal issue 2012-09-17.
        in_year = primary
    else:
        non_publication = [item for item in in_year if item[6] != "publication_info.year" and item[3] > 0]
        if non_publication:
            in_year = non_publication
    _, _, _, _, _, date, source = min(in_year, key=lambda item: (item[1], item[2], -item[3], item[4]))
    return date, source


def _person_from_profile(recid: str, payload: dict[str, Any], retrieved_at: str) -> dict[str, Any]:
    name = payload["name"]
    preferred = name["preferred_name"] or name["value"] or (name["name_variants"][0] if name["name_variants"] else f"INSPIRE author {recid}")
    aliases = list(dict.fromkeys([x for x in [name["value"], *name["name_variants"]] if x and x != preferred]))
    affiliations = list(dict.fromkeys([p["institution"] for p in payload["positions"] if p["current"]]))
    if not affiliations:
        affiliations = list(dict.fromkeys([p["institution"] for p in payload["positions"]]))
    orcid = next((item["value"] for item in payload["ids"] if item["schema"].lower() == "orcid"), None)
    person = {"id": recid, "name": preferred, "aliases": aliases, "affiliations": affiliations, "orcid": orcid,
              "profile_status": "profile", "source_url": source_url("authors", recid), "_retrieved_at": retrieved_at}
    if payload.get("death_date"):
        person["death_date"] = payload["death_date"]
    return person


def _ensure_person(people: dict[str, dict[str, Any]], recid: str, *, name: str | None = None,
                   affiliations: Iterable[str] = ()) -> None:
    if recid in people:
        person = people[recid]
        if person["profile_status"] == "literature_only":
            person["aliases"] = list(dict.fromkeys([*person["aliases"], *([name] if name and name != person["name"] else [])]))
            person["affiliations"] = list(dict.fromkeys([*person["affiliations"], *affiliations]))
        return
    people[recid] = {"id": recid, "name": name or f"INSPIRE author {recid}", "aliases": [],
                     "affiliations": list(dict.fromkeys(affiliations)), "orcid": None,
                     "profile_status": "literature_only", "source_url": source_url("authors", recid)}


def build_snapshot(connection: sqlite3.Connection, manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    if manifest is None:
        saved_manifest = connection.execute("SELECT payload FROM ingestion_manifest WHERE name='active'").fetchone()
        manifest = json.loads(saved_manifest["payload"]) if saved_manifest else {}
    person_redirects = _redirects(connection, "authors")
    work_redirects = _redirects(connection, "literature")
    person_tombstones = _tombstones(connection, "authors", person_redirects)
    people: dict[str, dict[str, Any]] = {}
    profiles = connection.execute("SELECT recid,payload,retrieved_at FROM source_records WHERE collection='authors' AND deleted=0").fetchall()
    for row in profiles:
        recid = person_redirects.get(row["recid"], row["recid"])
        if recid != row["recid"]: continue
        people[recid] = _person_from_profile(recid, json.loads(row["payload"]), row["retrieved_at"])
    literature_rows = connection.execute("SELECT * FROM source_records WHERE collection='literature' AND deleted=0").fetchall()
    current_rows = [row for row in literature_rows if work_redirects.get(row["recid"], row["recid"]) == row["recid"]]
    groups = _work_groups(connection, current_rows, person_redirects, person_tombstones)
    works: list[dict[str, Any]] = []
    phd: list[dict[str, Any]] = []
    for group in groups:
        row, payload, author_entries = _best_record(group, person_redirects, person_tombstones)
        resolved: list[str] = []
        for author in author_entries:
            if author["record"] and author["record"] not in person_tombstones:
                recid = person_redirects.get(author["record"], author["record"])
                _ensure_person(people, recid, name=author["full_name"], affiliations=author["affiliations"])
                if recid not in resolved: resolved.append(recid)
        date, date_source = _documented_date(record[1] for record in group)
        year = int(date[:4]) if date and re.fullmatch(r"\d{4}(?:-\d{2}(?:-\d{2})?)?", date) else None
        source_ids = sorted(record[0]["recid"] for record in group)
        full_count = max([len(author_entries), *(record[1]["author_count"] for record in group)])
        merged_dois = sorted({doi for _, candidate in group for doi in candidate["dois"]})
        merged_arxiv = sorted({identifier for _, candidate in group for identifier in candidate["arxiv_eprints"]})
        work = {"id": row["recid"], "title": payload["titles"][0] if payload["titles"] else "Untitled INSPIRE record",
                "year": year, "date": date, "date_source": date_source,
                "author_count": full_count, "authors": resolved,
                "unresolved_count": sum(1 for author in author_entries if not author["record"] or author["record"] in person_tombstones),
                "document_types": payload["document_type"], "doi": merged_dois, "arxiv": merged_arxiv,
                "source_url": source_url("literature", row["recid"]), "source_ids": source_ids,
                "retrieved_at": max(record[0]["retrieved_at"] for record in group)}
        works.append(work)
        types = {kind.lower() for kind in payload["document_type"]}
        if "thesis" in types and (payload["thesis_info"]["degree_type"] or "").lower() == "phd":
            # HEP schema roles distinguish supervisor/editor; it does not
            # require a student role.  A thesis with exactly one ordinary
            # author gives unambiguous student evidence.
            candidates = [person_redirects.get(a["record"], a["record"]) for a in payload["authors"] if a["record"] and a["record"] not in person_tombstones and _coauthor(a)]
            students = candidates if len(candidates) == 1 else []
            supervisors = [person_redirects.get(a["record"], a["record"]) for a in payload["authors"] if a["record"] and a["record"] not in person_tombstones and "supervisor" in {x.lower() for x in a["inspire_roles"]}]
            if candidates and not students:
                with connection:
                    connection.execute("INSERT INTO doctoral_audit VALUES(?,?,?,?,?,?,?)", ("literature_thesis", row["recid"], None, None, "ambiguous_thesis_students", json.dumps(payload["authors"], sort_keys=True), utc_now()))
            for student in students:
                for supervisor in supervisors:
                    _ensure_person(people, student); _ensure_person(people, supervisor)
                    phd.append({"adviser": supervisor, "student": student, "degree": "PhD", "year": year,
                                "source_url": work["source_url"], "source_record": row["recid"], "uncertainty": None,
                                "retrieved_at": work["retrieved_at"]})
    # Profile adviser assertions are separate evidence and retain whether curated.
    for row in profiles:
        student = person_redirects.get(row["recid"], row["recid"])
        if student != row["recid"]: continue
        payload = json.loads(row["payload"])
        for adviser in payload["advisors"]:
            adviser_id = person_redirects.get(adviser["record"], adviser["record"]) if adviser["record"] and adviser["record"] not in person_tombstones else None
            reason = None
            if (adviser["degree_type"] or "").lower() != "phd": reason = "degree_type_not_phd"
            elif adviser["hidden"]: reason = "hidden"
            elif not adviser_id: reason = "missing_record"
            if reason:
                with connection:
                    connection.execute("INSERT INTO doctoral_audit VALUES(?,?,?,?,?,?,?)", ("profile_advisor", row["recid"], student, adviser_id, reason, json.dumps(adviser, sort_keys=True), utc_now()))
                continue
            _ensure_person(people, student); _ensure_person(people, adviser_id, name=adviser["name"])
            phd.append({"adviser": adviser_id, "student": student, "degree": "PhD", "year": None,
                        "source_url": source_url("authors", row["recid"]), "source_record": row["recid"],
                        "uncertainty": None if adviser["curated_relation"] else "curated_relation_not_true",
                        "retrieved_at": row["retrieved_at"]})
    # Deduplicate same evidence safely; two different source records remain evidence.
    unique_phd = {(item["adviser"], item["student"], item["source_record"]): item for item in phd}
    for person in people.values(): person.pop("_retrieved_at", None)
    examples = []
    for item in manifest.get("examples", []):
        if isinstance(item, dict) and all(isinstance(item.get(key), str) for key in ("label", "source", "target")):
            examples.append({key: item[key] for key in ("label", "source", "target")})
    failure_rows = connection.execute("SELECT collection,query,error FROM query_checkpoints WHERE complete=0 AND error IS NOT NULL").fetchall()
    redirect_rows = connection.execute("SELECT collection,record_ids,reason FROM redirect_conflicts ORDER BY collection,record_ids").fetchall()
    checkpoints = connection.execute("SELECT collection,query,requested_limit,sort,complete,error,upstream_total,received_count FROM query_checkpoints ORDER BY collection,query").fetchall()
    coverage_queries = [{"collection": row["collection"], "query": row["query"], "limit": row["requested_limit"], "sort": row["sort"], "complete": bool(row["complete"]),
                         "upstream_total": row["upstream_total"], "received_count": row["received_count"],
                         "limited": row["upstream_total"] is not None and row["upstream_total"] > row["requested_limit"],
                         "truncated": row["upstream_total"] is not None and row["received_count"] < row["upstream_total"]} for row in checkpoints]
    created_at = utc_now()
    with connection:
        connection.execute("DELETE FROM works")
        connection.execute("DELETE FROM people")
        for work in works:
            connection.execute("INSERT INTO works VALUES(?,?,?,?)", (work["id"], json.dumps(work, sort_keys=True), json.dumps(work["source_ids"]), created_at))
        for person in people.values():
            connection.execute("INSERT INTO people VALUES(?,?,?)", (person["id"], json.dumps(person, sort_keys=True), created_at))
    coverage_failures = ([{"collection": row["collection"], "query": row["query"], "error": row["error"]} for row in failure_rows] +
                         [{"collection": row["collection"], "records": json.loads(row["record_ids"]), "error": row["reason"]} for row in redirect_rows])
    snapshot_content = {"coverage": {"label": manifest.get("label", "INSPIRE subset"), "description": manifest.get("description", ""), "complete": False,
                                     "queries": coverage_queries, "failures": coverage_failures},
                        "people": sorted(people.values(), key=lambda item: (item["name"].casefold(), item["id"])),
                        "works": sorted(works, key=lambda item: item["id"]), "phd": sorted(unique_phd.values(), key=lambda item: (item["student"], item["adviser"], item["source_record"])), "examples": examples}
    content_hash = hashlib.sha256(json.dumps(snapshot_content, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return {"version": f"sha256:{content_hash}", "created_at": created_at,
            "coverage": {"label": manifest.get("label", "INSPIRE subset"), "description": manifest.get("description", ""), "complete": False,
                         "queries": coverage_queries, "failures": coverage_failures},
            "people": sorted(people.values(), key=lambda item: (item["name"].casefold(), item["id"])),
            "works": sorted(works, key=lambda item: item["id"]), "phd": sorted(unique_phd.values(), key=lambda item: (item["student"], item["adviser"], item["source_record"])), "examples": examples}


def publish_snapshot(snapshot: dict[str, Any], output: str | Path) -> None:
    path = Path(output); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    ingest = commands.add_parser("ingest", help="fetch allowlisted manifest data")
    ingest.add_argument("--manifest", required=True); ingest.add_argument("--db", required=True); ingest.add_argument("--cache", required=True); ingest.add_argument("--refresh", action="store_true")
    build = commands.add_parser("build", help="atomically publish a graph snapshot")
    build.add_argument("--db", required=True); build.add_argument("--output", required=True); build.add_argument("--manifest")
    bulk = commands.add_parser("import-jsonl", help="import supported external metadata records")
    bulk.add_argument("--input", required=True); bulk.add_argument("--db", required=True)
    # JSONL rows are always upserts.  Accepting the flag keeps scripted update
    # invocations uniform with network ingestion without changing that meaning.
    bulk.add_argument("--refresh", action="store_true")
    args = parser.parse_args(argv)
    connection = open_db(args.db)
    try:
        if args.command == "ingest":
            result = ingest_manifest(connection, load_manifest(args.manifest), cache=args.cache, refresh=args.refresh)
        elif args.command == "import-jsonl":
            result = import_jsonl(connection, args.input)
        else:
            manifest = load_manifest(args.manifest) if args.manifest else None
            snapshot = build_snapshot(connection, manifest)
            publish_snapshot(snapshot, args.output)
            result = {"output": str(args.output), "people": len(snapshot["people"]), "works": len(snapshot["works"])}
        print(json.dumps(result, sort_keys=True))
        return 1 if result.get("failures") else 0
    except PipelineError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
