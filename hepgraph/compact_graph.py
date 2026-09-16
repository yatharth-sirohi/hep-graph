"""Compact incidence representation: no stored paper titles or full profiles.

This SQLite compiler is a bounded semantic/size prototype.  The production
compiler must stream a complete validated source into versioned cloud storage;
never treat this small in-memory fixture path as a full INSPIRE build.
"""

from __future__ import annotations

from collections import defaultdict
import sqlite3
from pathlib import Path
from typing import Any, Iterable

from .graph import Filters, Graph, GraphError
from .hlbes import COMPLETE, PARTIAL, UNKNOWN
from .providers import GraphVersion, ProviderNeighborhood, filter_key


def pack_ids(values: Iterable[int | str]) -> bytes:
    """Sorted, unique positive IDs encoded as delta unsigned varints."""
    ids = sorted({int(value) for value in values})
    if any(value < 1 for value in ids):
        raise ValueError("INSPIRE IDs must be positive")
    output = bytearray()
    previous = 0
    for value in ids:
        delta = value - previous
        while delta >= 128:
            output.append((delta & 0x7f) | 0x80)
            delta >>= 7
        output.append(delta)
        previous = value
    return bytes(output)


def unpack_ids(blob: bytes) -> tuple[str, ...]:
    values: list[str] = []
    previous = 0
    delta = 0
    shift = 0
    for byte in blob:
        delta |= (byte & 0x7f) << shift
        if byte & 0x80:
            shift += 7
            if shift > 63:
                raise ValueError("invalid compact ID stream")
        else:
            if delta < 1:
                raise ValueError("IDs must be strictly increasing")
            previous += delta
            values.append(str(previous))
            delta = shift = 0
    if shift:
        raise ValueError("truncated compact ID stream")
    return tuple(values)


SCHEMA = """
CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE author(id TEXT PRIMARY KEY, works BLOB NOT NULL);
CREATE TABLE work(id TEXT PRIMARY KEY, year INTEGER, author_count INTEGER NOT NULL,
                  members BLOB NOT NULL);
CREATE TABLE phd(adviser TEXT NOT NULL, student TEXT NOT NULL, source TEXT NOT NULL,
                 PRIMARY KEY(adviser,student,source));
CREATE INDEX phd_student ON phd(student,adviser);
"""


def build_compact_fixture(snapshot: dict[str, Any], destination: Path) -> None:
    """Build only a synthetic fixture; Graph's in-memory caps still apply."""
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError(destination)
    graph = Graph(snapshot, Filters(max_authors=None))
    postings: dict[str, set[str]] = defaultdict(set)
    connection = sqlite3.connect(destination)
    try:
        connection.executescript(SCHEMA)
        connection.executemany("INSERT INTO metadata VALUES (?,?)", (
            ("snapshot_id", str(snapshot.get("version", "compact-fixture"))),
            ("source_cutoff", str(snapshot.get("source_cutoff", ""))),
            ("schema_version", "compact-incidence-v1"),
        ))
        for work in graph.works.values():
            members = graph._resolved_authors(work)
            if len(members) < 2:
                continue  # no collaboration edge; author still exists below
            count = work.get("author_count")
            if not isinstance(count, int) or isinstance(count, bool):
                count = len(work.get("authors", ())) + max(0, work.get("unresolved_count", 0))
            year = work.get("year")
            if not isinstance(year, int) or isinstance(year, bool):
                year = None
            work_id = str(work["id"])
            connection.execute("INSERT INTO work VALUES (?,?,?,?)",
                               (work_id, year, count, pack_ids(members)))
            for member in members:
                postings[member].add(work_id)
        for person_id in graph.people:
            connection.execute("INSERT INTO author VALUES (?,?)",
                               (person_id, pack_ids(postings[person_id])))
        connection.executemany("INSERT INTO phd VALUES (?,?,?)", (
            (str(item["adviser"]), str(item["student"]), str(item.get("source_record", "")))
            for item in graph.phd))
        connection.commit()
    except BaseException:
        connection.rollback()
        connection.close()
        raise
    else:
        connection.close()


class CompactSQLiteProvider:
    """Read-only proof-of-concept for the final work-ID/member-ID shape."""

    MAX_MEMBER_VISITS = 3_000_000

    def __init__(self, path: Path, *, complete_for_test: bool = False) -> None:
        self.connection = sqlite3.connect(f"file:{Path(path).resolve()}?mode=ro", uri=True)
        self.connection.row_factory = sqlite3.Row
        meta = dict(self.connection.execute("SELECT key,value FROM metadata"))
        self.version = GraphVersion(meta["snapshot_id"], meta["source_cutoff"] or None,
                                    meta["schema_version"])
        self.complete = complete_for_test

    def close(self) -> None:
        self.connection.close()

    def get_graph_version(self) -> GraphVersion:
        return self.version

    def get_completeness(self, filters: Filters) -> bool:
        return self.complete

    def resolve_author(self, author_id: str) -> dict[str, Any] | None:
        row = self.connection.execute("SELECT 1 FROM author WHERE id=?", (str(author_id),)).fetchone()
        return {"id": str(author_id)} if row else None

    def _qualifying(self, author_id: str, filters: Filters) -> dict[str, list[str]] | None:
        row = self.connection.execute("SELECT works FROM author WHERE id=?", (str(author_id),)).fetchone()
        if row is None:
            return None
        neighbors: dict[str, list[str]] = defaultdict(list)
        visits = 0
        work_ids = unpack_ids(row[0])
        # Bounded batches avoid oversized SQL parameter lists. Only one
        # author's posting list and one batch of work/member blobs are live.
        for offset in range(0, len(work_ids), 500):
            batch = work_ids[offset:offset + 500]
            if not batch:
                continue
            placeholders = ",".join("?" for _ in batch)
            found = 0
            for work in self.connection.execute(
                    f"SELECT id,year,author_count,members FROM work WHERE id IN ({placeholders})", batch):
                found += 1
                count, year = work["author_count"], work["year"]
                if count < filters.min_authors or (filters.max_authors is not None and count > filters.max_authors):
                    continue
                if filters.year_start is not None and (year is None or year < filters.year_start):
                    continue
                if filters.year_end is not None and (year is None or year > filters.year_end):
                    continue
                members = unpack_ids(work["members"])
                if str(author_id) not in members:
                    raise GraphError("invalid_snapshot", "author posting and work membership disagree")
                visits += len(members)
                if visits > self.MAX_MEMBER_VISITS:
                    raise GraphError("resource_limit", "compact neighborhood exceeds member-visit budget")
                for member in members:
                    if member != str(author_id):
                        neighbors[member].append(work["id"])
            if found != len(batch):
                raise GraphError("invalid_snapshot", "author posting references a missing work")
        return neighbors

    def get_neighbors(self, author_id: str, filters: Filters) -> ProviderNeighborhood:
        author_id = str(author_id)
        neighbors = self._qualifying(author_id, filters)
        if neighbors is None:
            return ProviderNeighborhood(self.version, filter_key(filters), frozenset(), UNKNOWN,
                                        "author_not_in_snapshot")
        members = {member for member, works in neighbors.items()
                   if len(works) >= filters.min_shared}
        if filters.genealogy:
            members.update(row[0] for row in self.connection.execute(
                "SELECT student FROM phd WHERE adviser=? UNION SELECT adviser FROM phd WHERE student=?",
                (author_id, author_id)))
        return ProviderNeighborhood(self.version, filter_key(filters), frozenset(members),
                                    COMPLETE if self.complete else PARTIAL,
                                    "" if self.complete else "uncertified_compact_fixture")

    def get_neighbors_batch(self, author_ids: tuple[str, ...], filters: Filters) -> dict[str, ProviderNeighborhood]:
        return {str(author_id): self.get_neighbors(str(author_id), filters) for author_id in author_ids}

    def get_edge_evidence_refs(self, source: str, target: str, filters: Filters) -> tuple[str, ...]:
        source, target = str(source), str(target)
        neighbors = self._qualifying(source, filters)
        work_ids = sorted(neighbors.get(target, ()), key=int) if neighbors else []
        refs = [f"work:{work_id}" for work_id in work_ids] if len(work_ids) >= filters.min_shared else []
        if filters.genealogy:
            refs.extend(f"phd:{row[0]}" for row in self.connection.execute(
                "SELECT source FROM phd WHERE (adviser=? AND student=?) OR "
                "(adviser=? AND student=?) ORDER BY source", (source, target, target, source)))
        return tuple(refs)

    def get_work_metadata(self, work_id: str) -> dict[str, Any] | None:
        row = self.connection.execute("SELECT id,year,author_count FROM work WHERE id=?",
                                      (str(work_id),)).fetchone()
        if row is None:
            return None
        return {"id": row["id"], "year": row["year"], "author_count": row["author_count"],
                "source_url": f"https://inspirehep.net/literature/{row['id']}"}
