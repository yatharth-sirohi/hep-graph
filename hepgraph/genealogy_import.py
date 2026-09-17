"""Harvest INSPIRE doctoral relations into the genealogy overlay.

Advisers are not collaboration topology: they come from the ``authors``
collection, on the student's own record, and they carry their own provenance.
So they load into a separately versioned overlay rather than into the compact
graph, and a neighborhood that needs them cannot claim completeness from a
literature import alone.

The crawl reuses ``fast_compact_import``'s shard protocol unchanged - recursive
splitting around the 10,000-result window, advisory-lock ownership, page
completeness and drift checks, per-page checkpoints - and only replaces the
collection, the range query and what a page stores.

Two properties of the source shape the result:

* ``recid:`` ranges do not work on ``authors``; ``control_number:[a TO b]``
  does, so that is what the shards are cut on.
* Only about 29,000 of 805,000 author records carry an adviser with a record
  reference, so the crawl asks for exactly those. An adviser given only as a
  name, with no INSPIRE record behind it, cannot become an edge and is counted
  rather than guessed at.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

from .fast_compact_import import DEFAULT_RATE, DEFAULT_WORKERS, ShardWorker, run as run_shards
from .neon_graph_provider import ADVISER_DEGREES, _at
from .pipeline import PipelineError, _metadata, ref_id


#: Only records that can actually yield an edge.
HAS_LINKED_ADVISER = "advisors.record.$ref:*"

#: INSPIRE author records are numerous but the advised subset is small, so one
#: page of 1,000 covers a large slice of a shard.
AUTHOR_FIELDS = ("control_number,advisors.record,advisors.degree_type,"
                 "advisors.curated_relation,advisors.hidden,advisors.name")

SCHEMA = (
    "CREATE TABLE IF NOT EXISTS graph_genealogy_overlay ("
    " overlay_id TEXT PRIMARY KEY,"
    " source_description TEXT NOT NULL,"
    " source_cutoff TIMESTAMPTZ NOT NULL,"
    " created_at TIMESTAMPTZ NOT NULL DEFAULT now(),"
    " certified_complete BOOLEAN NOT NULL DEFAULT FALSE);"
    "CREATE TABLE IF NOT EXISTS graph_genealogy_edge ("
    " overlay_id TEXT NOT NULL REFERENCES graph_genealogy_overlay(overlay_id),"
    " adviser_id BIGINT NOT NULL,"
    " student_id BIGINT NOT NULL,"
    " source_record TEXT NOT NULL,"
    " degree TEXT,"
    " year SMALLINT,"
    " curated BOOLEAN NOT NULL DEFAULT FALSE,"
    " source_kind TEXT NOT NULL DEFAULT 'author_profile',"
    " PRIMARY KEY (overlay_id, adviser_id, student_id, source_record),"
    " CHECK (adviser_id <> student_id));"
    "ALTER TABLE graph_genealogy_edge ADD COLUMN IF NOT EXISTS"
    " source_kind TEXT NOT NULL DEFAULT 'author_profile';"
    "CREATE INDEX IF NOT EXISTS graph_genealogy_edge_student"
    " ON graph_genealogy_edge (overlay_id, student_id, adviser_id);"
    "CREATE INDEX IF NOT EXISTS graph_genealogy_edge_adviser"
    " ON graph_genealogy_edge (overlay_id, adviser_id, student_id);"
    "CREATE TABLE IF NOT EXISTS graph_genealogy_quarantine ("
    " overlay_id TEXT NOT NULL,"
    " adviser_id BIGINT NOT NULL,"
    " student_id BIGINT NOT NULL,"
    " source_record TEXT NOT NULL,"
    " degree TEXT,"
    " source_kind TEXT NOT NULL,"
    " reason TEXT NOT NULL,"
    " quarantined_at TIMESTAMPTZ NOT NULL DEFAULT now(),"
    " PRIMARY KEY (overlay_id, adviser_id, student_id, source_record));"
)


def advisers_from_hit(hit: dict[str, Any]) -> tuple[int, list[dict[str, Any]], int]:
    """Return (student_id, linked advisers, count of unlinkable advisers).

    An adviser INSPIRE records only as a name is real but unusable: there is no
    record to point an edge at, and matching it by name is exactly the identity
    guess this project refuses to make. It is counted so the gap is visible.
    """
    recid, metadata = _metadata(hit)
    advisers = metadata.get("advisors")
    if not isinstance(advisers, list):
        return int(recid), [], 0
    linked: list[dict[str, Any]] = []
    unlinkable = 0
    for adviser in advisers:
        if not isinstance(adviser, dict):
            continue
        if adviser.get("hidden") is True:
            continue
        identifier = ref_id(adviser.get("record"))
        if identifier is None:
            unlinkable += 1
            continue
        degree = adviser.get("degree_type")
        linked.append({
            "adviser_id": int(identifier),
            "degree": str(degree).lower() if isinstance(degree, str) else None,
            "curated": adviser.get("curated_relation") is True,
        })
    return int(recid), linked, unlinkable


class GenealogyShardWorker(ShardWorker):
    """The shard protocol, pointed at author records and adviser edges.

    Every linked adviser is stored with the degree INSPIRE recorded, including
    the 1,500-odd relations it leaves untyped. Filtering to doctoral at crawl
    time would discard real relationships that simply have no degree recorded,
    and re-deciding later would mean crawling again; the query layer filters.
    """

    COLLECTION = "authors"
    overlay_id = "inspire-genealogy"
    degrees: tuple[str, ...] | None = None

    def range_query(self, low: int, high: int) -> str:
        return f"{HAS_LINKED_ADVISER} AND control_number:[{low} TO {high}]"

    def persist(self, hits: list[Any]) -> tuple[int, int]:
        rows: list[tuple[Any, ...]] = []
        students = 0
        for hit in hits:
            student, advisers, _ = advisers_from_hit(hit)
            kept = [item for item in advisers
                    if self.degrees is None or item["degree"] in self.degrees]
            # A record listing itself as its own adviser is a source error, not
            # a relation; the table's CHECK would reject it anyway.
            kept = [item for item in kept if item["adviser_id"] != student]
            if kept:
                students += 1
            for item in kept:
                rows.append((self.overlay_id, item["adviser_id"], student,
                             str(student), item["degree"], None, item["curated"]))
        if rows:
            self._executemany(
                "INSERT INTO graph_genealogy_edge(overlay_id,adviser_id,student_id,"
                "source_record,degree,year,curated) VALUES (%s,%s,%s,%s,%s,%s,%s) "
                "ON CONFLICT DO NOTHING", rows)
        return students, len(rows)


#: A thesis record names its own supervisors, which the author collection's
#: adviser field often omits: ~27,000 theses carry a linked supervisor, 93% of
#: them doctoral, and none of that was read by the profile crawl.
THESIS_QUERY = "document_type:thesis AND supervisors.record.$ref:*"
THESIS_FIELDS = ("control_number,authors.record,authors.inspire_roles,"
                 "supervisors.record,supervisors.inspire_roles,thesis_info.degree_type")


def supervisors_from_thesis(hit: dict[str, Any]) -> tuple[int, list[int], list[int], str | None]:
    """Return (thesis_recid, student ids, supervisor ids, degree) for one thesis."""
    recid, metadata = _metadata(hit)
    info = metadata.get("thesis_info") if isinstance(metadata.get("thesis_info"), dict) else {}
    degree = info.get("degree_type")
    degree = str(degree).lower() if isinstance(degree, str) else None

    def roles(person: dict[str, Any]) -> list[Any]:
        value = person.get("inspire_roles")
        return value if isinstance(value, list) else []

    students: list[int] = []
    supervisors: list[int] = []
    # INSPIRE lists supervisors twice: in ``supervisors`` and again inside
    # ``authors`` with inspire_roles ["supervisor"]. Some records also repeat a
    # supervisor as a plain author, so anyone named supervisor anywhere on the
    # thesis is a supervisor of it and never its student.
    for key in ("supervisors", "authors"):
        people = metadata.get(key)
        for person in people if isinstance(people, list) else ():
            if not isinstance(person, dict):
                continue
            identifier = ref_id(person.get("record"))
            if identifier is None:
                continue
            if key == "supervisors" or "supervisor" in roles(person):
                if int(identifier) not in supervisors:
                    supervisors.append(int(identifier))
    for person in metadata.get("authors") if isinstance(metadata.get("authors"), list) else ():
        if not isinstance(person, dict) or "supervisor" in roles(person):
            continue
        identifier = ref_id(person.get("record"))
        if identifier is not None and int(identifier) not in supervisors \
                and int(identifier) not in students:
            students.append(int(identifier))
    return int(recid), students, supervisors, degree


class ThesisSupervisorShardWorker(GenealogyShardWorker):
    """The same shard protocol over thesis records instead of author profiles."""

    COLLECTION = "literature"

    def range_query(self, low: int, high: int) -> str:
        return f"{THESIS_QUERY} AND recid:{low}->{high}"

    def persist(self, hits: list[Any]) -> tuple[int, int]:
        rows: list[tuple[Any, ...]] = []
        theses = 0
        for hit in hits:
            thesis, students, supervisors, degree = supervisors_from_thesis(hit)
            if self.degrees is not None and degree not in self.degrees:
                continue
            kept = [(adviser, student) for student in students for adviser in supervisors
                    if adviser != student]
            if kept:
                theses += 1
            rows.extend((self.overlay_id, adviser, student, str(thesis), degree, None,
                         False, "thesis") for adviser, student in kept)
        if rows:
            self._executemany(
                "INSERT INTO graph_genealogy_edge(overlay_id,adviser_id,student_id,"
                "source_record,degree,year,curated,source_kind) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", rows)
        return theses, len(rows)


def find_cycle(pairs: list[tuple[int, int]]) -> list[tuple[int, int]] | None:
    """Return the edges of one doctoral loop, or None if the relation is a forest of DAGs."""
    from collections import defaultdict

    children: dict[int, list[int]] = defaultdict(list)
    parents: dict[int, list[int]] = defaultdict(list)
    indegree: dict[int, int] = defaultdict(int)
    nodes: set[int] = set()
    for adviser, student in pairs:
        children[adviser].append(student)
        parents[student].append(adviser)
        indegree[student] += 1
        nodes.update((adviser, student))
    ready = [node for node in nodes if indegree[node] == 0]
    while ready:
        node = ready.pop()
        for child in children[node]:
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)
    residual = {node for node in nodes if indegree[node] > 0}
    if not residual:
        return None
    # Every residual node still has an adviser inside the residue, so walking
    # advisers must revisit a node; the revisited stretch is a loop.
    order: list[int] = []
    seen: dict[int, int] = {}
    node = min(residual)
    while node not in seen:
        seen[node] = len(order)
        order.append(node)
        node = next(parent for parent in parents[node] if parent in residual)
    loop = order[seen[node]:] + [node]
    return [(loop[i + 1], loop[i]) for i in range(len(loop) - 1)]


def quarantine_cycles(connection: Any, overlay_id: str = "inspire-genealogy") -> list[dict[str, Any]]:
    """Move the evidence behind impossible doctoral loops out of the overlay.

    INSPIRE is taken at its word, but a person cannot be their own academic
    ancestor, and a loop would make "generation" meaningless. Such a loop is a
    record error - typically a thesis whose author link points at the wrong
    person. One relation per loop is withdrawn, chosen without any judgement
    about who is right: the pair with the least supporting evidence, a thesis
    before an author profile, then the most recently created record. Withdrawn
    rows are kept, with the reason, rather than deleted.
    """
    withdrawn: list[dict[str, Any]] = []
    while True:
        pairs = [(int(_at(r, 0)), int(_at(r, 1))) for r in connection.execute(
            "SELECT DISTINCT adviser_id, student_id FROM graph_genealogy_edge "
            "WHERE overlay_id=%s AND COALESCE(degree,'other') = ANY(%s)",
            (overlay_id, list(ADVISER_DEGREES))).fetchall()]
        loop = find_cycle(pairs)
        if loop is None:
            return withdrawn

        def weight(pair: tuple[int, int]) -> tuple[int, int, int]:
            rows = connection.execute(
                "SELECT source_kind, source_record FROM graph_genealogy_edge WHERE overlay_id=%s "
                "AND COALESCE(degree,'other') = ANY(%s) AND adviser_id=%s AND student_id=%s",
                (overlay_id, list(ADVISER_DEGREES), *pair)).fetchall()
            profile = any(_at(r, 0) != "thesis" for r in rows)
            newest = max(int(_at(r, 1)) for r in rows)
            return (len(rows), int(profile), -newest)

        adviser, student = min(loop, key=weight)
        reason = "doctoral loop: " + " -> ".join(str(a) for a, _ in loop) + f" -> {loop[-1][1]}"
        moved = connection.execute(
            "DELETE FROM graph_genealogy_edge WHERE overlay_id=%s "
            "AND COALESCE(degree,'other') = ANY(%s) AND adviser_id=%s AND student_id=%s "
            "RETURNING overlay_id, adviser_id, student_id, source_record, degree, source_kind",
            (overlay_id, list(ADVISER_DEGREES), adviser, student)).fetchall()
        for row in moved:
            connection.execute(
                "INSERT INTO graph_genealogy_quarantine(overlay_id,adviser_id,student_id,"
                "source_record,degree,source_kind,reason) VALUES (%s,%s,%s,%s,%s,%s,%s) "
                "ON CONFLICT DO NOTHING", (*[_at(row, i) for i in range(6)], reason))
            withdrawn.append({"adviser": adviser, "student": student,
                              "source_record": _at(row, 3), "reason": reason})


def run_theses(url: str, *, import_id: str = "genealogy-theses-20260917",
               overlay_id: str = "inspire-genealogy", low: int = 1, high: int = 4_000_000,
               workers: int = 8, rate: float = DEFAULT_RATE) -> dict[str, Any]:
    worker = type("_ThesisWorker", (ThesisSupervisorShardWorker,),
                  {"overlay_id": overlay_id, "degrees": None})

    def setup(control: Any) -> None:
        control.execute(SCHEMA)
        control.execute(
            "INSERT INTO inspire_compact_import(import_id,source_cutoff,low_recid,high_recid,status) "
            "VALUES (%s, now(), %s, %s, 'FETCHING') ON CONFLICT DO NOTHING", (import_id, low, high))
        control.execute(
            "INSERT INTO inspire_compact_shard(import_id,low_recid,high_recid,status) "
            "VALUES (%s,%s,%s,'DISCOVER') ON CONFLICT DO NOTHING", (import_id, low, high))

    import hepgraph.pipeline as pipeline

    previous = pipeline.LITERATURE_FIELDS
    pipeline.LITERATURE_FIELDS = THESIS_FIELDS
    try:
        return run_shards(url, import_id, workers=workers, rate=rate, minimal_fields=False,
                          worker_class=worker, setup=setup)
    finally:
        pipeline.LITERATURE_FIELDS = previous


def run(url: str, *, import_id: str = "genealogy-20260917",
        overlay_id: str = "inspire-genealogy", low: int = 1, high: int = 4_000_000,
        workers: int = 8, rate: float = DEFAULT_RATE, phd_only: bool = False,
        duration: float | None = None) -> dict[str, Any]:
    import psycopg

    worker = type("_Worker", (GenealogyShardWorker,),
                  {"overlay_id": overlay_id,
                   "degrees": ("phd",) if phd_only else None})

    def setup(control: Any) -> None:
        control.execute(SCHEMA)
        control.execute(
            "INSERT INTO graph_genealogy_overlay(overlay_id,source_description,source_cutoff) "
            "VALUES (%s,%s, now()) ON CONFLICT DO NOTHING",
            (overlay_id, "INSPIRE author records: advisers carrying a record reference"))
        control.execute(
            "INSERT INTO inspire_compact_import(import_id,source_cutoff,low_recid,high_recid,status) "
            "VALUES (%s, now(), %s, %s, 'FETCHING') ON CONFLICT DO NOTHING",
            (import_id, low, high))
        control.execute(
            "INSERT INTO inspire_compact_shard(import_id,low_recid,high_recid,status) "
            "VALUES (%s,%s,%s,'DISCOVER') ON CONFLICT DO NOTHING", (import_id, low, high))

    # The author field projection replaces the literature one for this crawl.
    import hepgraph.pipeline as pipeline

    previous = pipeline.AUTHOR_FIELDS
    pipeline.AUTHOR_FIELDS = AUTHOR_FIELDS
    try:
        return run_shards(url, import_id, workers=workers, rate=rate,
                          minimal_fields=False, duration=duration,
                          worker_class=worker, setup=setup)
    finally:
        pipeline.AUTHOR_FIELDS = previous


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL_UNPOOLED"))
    parser.add_argument("--import-id", default="genealogy-20260917")
    parser.add_argument("--overlay-id", default="inspire-genealogy")
    parser.add_argument("--low", type=int, default=1)
    parser.add_argument("--high", type=int, default=4_000_000)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--rate", type=float, default=DEFAULT_RATE)
    parser.add_argument("--theses", action="store_true",
                        help="harvest supervisors named on thesis records instead of author profiles")
    parser.add_argument("--quarantine", action="store_true",
                        help="withdraw the evidence behind impossible doctoral loops")
    parser.add_argument("--phd-only", action="store_true",
                        help="store only advisers INSPIRE explicitly typed as doctoral")
    parser.add_argument("--duration", type=float, default=None)
    args = parser.parse_args(argv)
    if not args.database_url:
        parser.error("a direct database URL is required")
    try:
        if args.theses:
            run_theses(args.database_url, overlay_id=args.overlay_id,
                       workers=args.workers, rate=args.rate)
        if args.theses or args.quarantine:
            import psycopg

            with psycopg.connect(args.database_url, autocommit=True) as connection:
                connection.execute(SCHEMA)
                for item in quarantine_cycles(connection, args.overlay_id):
                    print(f"withdrew {item['adviser']}->{item['student']} "
                          f"(record {item['source_record']}): {item['reason']}", flush=True)
            return 0
        run(args.database_url, import_id=args.import_id, overlay_id=args.overlay_id,
            low=args.low, high=args.high, workers=args.workers, rate=args.rate,
            phd_only=args.phd_only, duration=args.duration)
    except (PipelineError, ValueError) as exc:
        print(f"genealogy import stopped: {exc}", file=sys.stderr, flush=True)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
