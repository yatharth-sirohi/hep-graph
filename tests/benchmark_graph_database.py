"""Measure the pinned graph provider on a candidate-shaped synthetic corpus.

Not a unit test: it builds a few million rows, so it is run deliberately.

    HEPGRAPH_TEST_DATABASE_URL=... python -m tests.benchmark_graph_database --build

The generated shape mirrors the observed Neon candidate (works, memberships and
a heavy tail of large collaborations) so the reported latencies and query plans
describe the real workload rather than a toy.
"""

from __future__ import annotations

import argparse
import os

import statistics
import time

import psycopg

from hepgraph.graph import Filters
from hepgraph.neon_compact_import import SCHEMA
from hepgraph.neon_graph_provider import CoverageClaim, NeonCompactGraphProvider

IMPORT_ID = "benchmark"
AUTHORS = 232_000          # distinct authors observed in the candidate
WORKS = 172_000            # works observed in the candidate
# Small teams dominate by count; a long tail of collaborations dominates rows.
TEAM_SIZES = ((2, 0.34), (3, 0.20), (4, 0.14), (6, 0.12), (10, 0.09),
              (30, 0.05), (120, 0.03), (600, 0.02), (2_932, 0.01))


def build(connection) -> None:
    connection.execute("DROP TABLE IF EXISTS inspire_compact_membership")
    connection.execute("DROP TABLE IF EXISTS inspire_compact_work")
    connection.execute("DROP TABLE IF EXISTS inspire_compact_shard")
    connection.execute("DROP TABLE IF EXISTS inspire_compact_import")
    connection.execute(SCHEMA)
    connection.execute(
        "INSERT INTO inspire_compact_import(import_id,source_cutoff,low_recid,high_recid,status) "
        "VALUES (%s, now(), 1, %s, 'FETCHING')", (IMPORT_ID, WORKS))
    started = time.perf_counter()
    # Generated server-side: moving millions of rows through the client is the
    # slowest possible way to build a fixture, and the sizes only need to be
    # reproducible, which setseed gives.
    buckets = " ".join(
        f"WHEN r < {sum(weight for _, weight in TEAM_SIZES[:index + 1]):.2f} THEN {size}"
        for index, (size, _) in enumerate(TEAM_SIZES))
    # The bucket draw must vary per work. A `LATERAL (SELECT random())` that
    # does not reference the row is uncorrelated, so the planner evaluates it
    # once and every work comes out the same size; derive it from the id instead,
    # which is also reproducible without setseed.
    connection.execute(f"""
        INSERT INTO inspire_compact_work(import_id,work_id,year,author_count,member_count,retrieved_at)
        SELECT %s, g, 1975 + (g %% 52), size, size, now()
        FROM (SELECT g, (CASE {buckets} ELSE 2 END) AS size
              FROM generate_series(1, %s) AS g,
                   LATERAL (SELECT ((g * 2654435761) %% 10000)::float / 10000.0 AS r) AS pick
             ) AS sized
    """, (IMPORT_ID, WORKS))
    # A collision simply yields a slightly smaller team, which is harmless here
    # and keeps the primary key doing the deduplication it does in production.
    connection.execute("""
        INSERT INTO inspire_compact_membership(import_id,work_id,author_id)
        SELECT w.import_id, w.work_id,
               1 + ((w.work_id * 7919 + slot * 104729) %% %s)
        FROM inspire_compact_work w,
             LATERAL generate_series(1, w.member_count) AS slot
        WHERE w.import_id = %s
        ON CONFLICT DO NOTHING
    """, (AUTHORS, IMPORT_ID))
    connection.execute("UPDATE inspire_compact_work w SET member_count = actual.rows "
                       "FROM (SELECT work_id, count(*) AS rows FROM inspire_compact_membership "
                       "WHERE import_id=%s GROUP BY work_id) actual "
                       "WHERE w.work_id = actual.work_id AND w.import_id=%s", (IMPORT_ID, IMPORT_ID))
    connection.execute("DELETE FROM inspire_compact_work WHERE import_id=%s AND member_count < 2",
                       (IMPORT_ID,))
    connection.execute("ANALYZE inspire_compact_work")
    connection.execute("ANALYZE inspire_compact_membership")
    works = connection.execute("SELECT count(*) FROM inspire_compact_work").fetchone()[0]
    rows = connection.execute("SELECT count(*) FROM inspire_compact_membership").fetchone()[0]
    print(f"built {works:,} works and {rows:,} memberships "
          f"in {time.perf_counter() - started:.1f}s")


def _provider(connection):
    return NeonCompactGraphProvider(
        connection, coverage=CoverageClaim(import_id=IMPORT_ID, certified_complete=True, reason=""))


def _time(label, call, repeats=5):
    samples = []
    for _ in range(repeats):
        started = time.perf_counter()
        call()
        samples.append((time.perf_counter() - started) * 1000)
    print(f"{label:<52} median {statistics.median(samples):8.1f} ms   "
          f"min {min(samples):7.1f}   max {max(samples):7.1f}")


def measure(connection) -> None:
    provider = _provider(connection)
    filters = Filters(max_authors=10, genealogy=False)
    every = Filters(max_authors=None, genealogy=False)
    degrees = connection.execute(
        "SELECT author_id, count(*) AS works FROM inspire_compact_membership "
        "WHERE import_id=%s GROUP BY author_id ORDER BY works DESC LIMIT 1", (IMPORT_ID,)).fetchone()
    hub = str(degrees[0])
    # The median-degree author, whatever the corpus density turns out to be.
    typical = connection.execute(
        "SELECT author_id, works FROM (SELECT author_id, count(*) AS works, "
        "  row_number() OVER (ORDER BY count(*)) AS position, count(*) OVER () AS total "
        "  FROM inspire_compact_membership WHERE import_id=%s GROUP BY author_id) ranked "
        "WHERE position = total / 2", (IMPORT_ID,)).fetchone()
    ordinary = str(typical[0])
    print(f"\nhub author {hub}: {degrees[1]} works; "
          f"median author {ordinary}: {typical[1]} works\n")
    _time("neighbors, ordinary author, small-team", lambda: provider.get_neighbors(ordinary, filters))
    _time("neighbors, ordinary author, all modes", lambda: provider.get_neighbors(ordinary, every))
    _time("neighbors, hub author, small-team", lambda: provider.get_neighbors(hub, filters))
    _time("neighbors, hub author, all modes", lambda: provider.get_neighbors(hub, every))
    batch = tuple(str(value) for value in range(1, 33))
    _time("neighbors batch of 32, small-team", lambda: provider.get_neighbors_batch(batch, filters))
    _time("evidence refs for one edge", lambda: provider.get_edge_evidence_refs(ordinary, "1", filters))
    _time("author existence check", lambda: provider.resolve_author(ordinary))
    print(f"\nqueries issued: {provider.queries}")


def explain(connection) -> None:
    """Plain EXPLAIN only: it plans the statement without running it."""
    filters = Filters(max_authors=10, genealogy=False)
    provider = _provider(connection)
    params = provider._filter_params(filters) | {"anchors": [1, 2, 3]}
    sql = (f"WITH anchors AS (SELECT unnest(%(anchors)s::bigint[]) AS anchor), "
           f"qualifying AS ({provider._QUALIFYING}) "
           "SELECT q.anchor, m.author_id, count(*) AS shared FROM qualifying q "
           "JOIN inspire_compact_membership m ON m.import_id = %(import_id)s "
           "AND m.work_id = q.work_id WHERE m.author_id <> q.anchor "
           "GROUP BY q.anchor, m.author_id HAVING count(*) >= %(min_shared)s "
           "ORDER BY q.anchor, m.author_id")
    print("\n--- EXPLAIN: batched neighborhood ---")
    for row in connection.execute("EXPLAIN " + sql, params).fetchall():
        print(row[0])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true", help="regenerate the synthetic corpus")
    parser.add_argument("--explain", action="store_true")
    args = parser.parse_args()
    url = os.environ.get("HEPGRAPH_TEST_DATABASE_URL")
    if not url:
        parser.error("set HEPGRAPH_TEST_DATABASE_URL")
    with psycopg.connect(url, autocommit=True) as connection:
        connection.execute("SET statement_timeout = '120s'")
        if args.build:
            build(connection)
        measure(connection)
        if args.explain:
            explain(connection)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
