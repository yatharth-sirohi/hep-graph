"""Private, small synthetic SQLite index prototype; NOT a production loader.

The compiler deliberately starts from an already normalized in-memory test
snapshot. It does not acquire INSPIRE, prove source completeness, checkpoint a
full build, or permit production promotion. Those are separate v0.3 gates.
"""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any

from .graph import Filters, Graph
from .hlbes import COMPLETE, PARTIAL, UNKNOWN
from .providers import GraphVersion, ProviderNeighborhood, filter_key


def build_synthetic_index(snapshot: dict[str, Any], destination: Path) -> None:
    """Build an isolated test index at a *new* path; never overwrite a version."""
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError(destination)
    # Graph applies the same correction/type/identity-filtered work semantics
    # as the saved demo. This is only practical for bounded synthetic fixtures.
    graph = Graph(snapshot, Filters(max_authors=None))
    connection = sqlite3.connect(destination)
    try:
        connection.executescript("""
            CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE person(id TEXT PRIMARY KEY, data TEXT NOT NULL);
            CREATE TABLE work(id TEXT PRIMARY KEY, author_count INTEGER NOT NULL,
                              year INTEGER, data TEXT NOT NULL);
            CREATE TABLE incidence(author TEXT NOT NULL, work TEXT NOT NULL,
                                   PRIMARY KEY(author, work));
            CREATE INDEX incidence_work ON incidence(work, author);
            CREATE TABLE small_edge(author TEXT NOT NULL, neighbor TEXT NOT NULL,
                                    work TEXT NOT NULL, PRIMARY KEY(author, neighbor, work));
            CREATE INDEX small_edge_author ON small_edge(author, neighbor);
            CREATE TABLE phd(adviser TEXT NOT NULL, student TEXT NOT NULL,
                             source TEXT NOT NULL, data TEXT NOT NULL,
                             PRIMARY KEY(adviser, student, source));
        """)
        connection.executemany("INSERT INTO metadata VALUES (?, ?)", (
            ("snapshot_id", str(snapshot.get("version", "synthetic"))),
            ("source_cutoff", str(snapshot.get("source_cutoff", ""))),
            ("schema_version", "synthetic-sqlite-v1"),
        ))
        for person_id, person in graph.people.items():
            connection.execute("INSERT INTO person VALUES (?, ?)", (person_id, json.dumps(person)))
        for work_id, work in graph.works.items():
            count = work.get("author_count")
            if not isinstance(count, int) or isinstance(count, bool):
                count = len(work.get("authors", ())) + max(0, work.get("unresolved_count", 0))
            year = work.get("year")
            if not isinstance(year, int) or isinstance(year, bool):
                year = None
            connection.execute("INSERT INTO work VALUES (?, ?, ?, ?)",
                               (work_id, count, year, json.dumps(work)))
            authors = graph._resolved_authors(work)
            connection.executemany("INSERT INTO incidence VALUES (?, ?)",
                                   ((author, work_id) for author in authors))
            if count <= 10:
                connection.executemany("INSERT INTO small_edge VALUES (?, ?, ?)",
                                       ((author, neighbor, work_id) for author in authors
                                        for neighbor in authors if author != neighbor))
        for record in graph.phd:
            connection.execute("INSERT INTO phd VALUES (?, ?, ?, ?)",
                               (str(record["adviser"]), str(record["student"]),
                                str(record.get("source_record", "")), json.dumps(record)))
        connection.commit()
    except BaseException:
        connection.rollback()
        connection.close()
        # A failed prototype is not a candidate. The caller owns disposal;
        # do not delete any path that might be mistaken for an active version.
        raise
    else:
        connection.close()


class SyntheticSQLiteProvider:
    """Read-only hybrid-index prototype, complete only in a declared test world."""

    def __init__(self, path: Path, *, complete_for_test: bool = False) -> None:
        self.connection = sqlite3.connect(f"file:{Path(path).resolve()}?mode=ro", uri=True)
        self.connection.row_factory = sqlite3.Row
        meta = dict(self.connection.execute("SELECT key, value FROM metadata"))
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
        row = self.connection.execute("SELECT data FROM person WHERE id=?", (str(author_id),)).fetchone()
        return json.loads(row[0]) if row else None

    @staticmethod
    def _where(filters: Filters) -> tuple[str, list[int]]:
        clauses = ["w.author_count >= ?"]
        args = [filters.min_authors]
        if filters.max_authors is not None:
            clauses.append("w.author_count <= ?")
            args.append(filters.max_authors)
        if filters.year_start is not None:
            clauses.append("w.year >= ?")
            args.append(filters.year_start)
        if filters.year_end is not None:
            clauses.append("w.year <= ?")
            args.append(filters.year_end)
        return " AND ".join(clauses), args

    def get_neighbors(self, author_id: str, filters: Filters) -> ProviderNeighborhood:
        author_id = str(author_id)
        if self.resolve_author(author_id) is None:
            return ProviderNeighborhood(self.version, filter_key(filters), frozenset(), UNKNOWN,
                                        "author_not_in_snapshot")
        where, args = self._where(filters)
        if filters.max_authors is not None and filters.max_authors <= 10:
            sql = ("SELECT e.neighbor FROM small_edge e JOIN work w ON w.id=e.work "
                   f"WHERE e.author=? AND {where} GROUP BY e.neighbor "
                   "HAVING COUNT(DISTINCT e.work)>=?")
        else:
            sql = ("SELECT peer.author AS neighbor FROM incidence own "
                   "JOIN incidence peer ON peer.work=own.work AND peer.author<>own.author "
                   "JOIN work w ON w.id=own.work "
                   f"WHERE own.author=? AND {where} GROUP BY peer.author "
                   "HAVING COUNT(DISTINCT own.work)>=?")
        members = {row[0] for row in self.connection.execute(sql, [author_id, *args, filters.min_shared])}
        if filters.genealogy:
            members.update(row[0] for row in self.connection.execute(
                "SELECT student FROM phd WHERE adviser=? UNION SELECT adviser FROM phd WHERE student=?",
                (author_id, author_id)))
        return ProviderNeighborhood(self.version, filter_key(filters), frozenset(members),
                                    COMPLETE if self.complete else PARTIAL,
                                    "" if self.complete else "synthetic_coverage_incomplete")

    def get_neighbors_batch(self, author_ids: tuple[str, ...], filters: Filters) -> dict[str, ProviderNeighborhood]:
        return {str(author_id): self.get_neighbors(author_id, filters) for author_id in author_ids}

    def get_edge_evidence_refs(self, source: str, target: str, filters: Filters) -> tuple[str, ...]:
        source, target = str(source), str(target)
        where, args = self._where(filters)
        rows = self.connection.execute(
            "SELECT w.id FROM incidence a JOIN incidence b ON a.work=b.work "
            "JOIN work w ON w.id=a.work "
            f"WHERE a.author=? AND b.author=? AND {where} ORDER BY w.id",
            [source, target, *args]).fetchall()
        refs = [f"work:{row[0]}" for row in rows] if len(rows) >= filters.min_shared else []
        if refs or filters.genealogy:
            refs.extend(f"phd:{row[0]}" for row in self.connection.execute(
                "SELECT source FROM phd WHERE (adviser=? AND student=?) OR (adviser=? AND student=?) ORDER BY source",
                (source, target, target, source)))
        return tuple(refs)

    def get_work_metadata(self, work_id: str) -> dict[str, Any] | None:
        row = self.connection.execute("SELECT data FROM work WHERE id=?", (str(work_id),)).fetchone()
        return json.loads(row[0]) if row else None
