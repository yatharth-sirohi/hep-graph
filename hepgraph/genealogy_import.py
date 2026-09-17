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
    " PRIMARY KEY (overlay_id, adviser_id, student_id, source_record),"
    " CHECK (adviser_id <> student_id));"
    "CREATE INDEX IF NOT EXISTS graph_genealogy_edge_student"
    " ON graph_genealogy_edge (overlay_id, student_id, adviser_id);"
    "CREATE INDEX IF NOT EXISTS graph_genealogy_edge_adviser"
    " ON graph_genealogy_edge (overlay_id, adviser_id, student_id);"
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
    parser.add_argument("--phd-only", action="store_true",
                        help="store only advisers INSPIRE explicitly typed as doctoral")
    parser.add_argument("--duration", type=float, default=None)
    args = parser.parse_args(argv)
    if not args.database_url:
        parser.error("a direct database URL is required")
    try:
        run(args.database_url, import_id=args.import_id, overlay_id=args.overlay_id,
            low=args.low, high=args.high, workers=args.workers, rate=args.rate,
            phd_only=args.phd_only, duration=args.duration)
    except (PipelineError, ValueError) as exc:
        print(f"genealogy import stopped: {exc}", file=sys.stderr, flush=True)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
