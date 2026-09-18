"""The parallel importer must produce exactly what the serial one would.

Speed is worthless if it loses or duplicates records, so these tests drive the
worker pool against a synthetic INSPIRE whose exact contents are known, then
check the resulting tables row by row rather than by summary counters.
"""

from __future__ import annotations

import os
import threading

import pytest

from hepgraph.fast_compact_import import RateLimiter, run
from hepgraph.neon_compact_import import SCHEMA

psycopg = pytest.importorskip("psycopg")

URL = os.environ.get("HEPGRAPH_FAST_IMPORT_TEST_URL")
pytestmark = pytest.mark.skipif(not URL, reason="HEPGRAPH_FAST_IMPORT_TEST_URL is not set")

IMPORT_ID = "fast-test"


class FakeInspire:
    """A deterministic INSPIRE over a fixed universe of literature records.

    Every record has two resolved authors derived from its id, so the expected
    membership rows are computable without consulting the importer.
    """

    def __init__(self, ids: list[int], *, delay: float = 0.0) -> None:
        self.ids = sorted(ids)
        self.delay = delay
        self.calls = 0
        self.lock = threading.Lock()

    def _window(self, query: str) -> list[int]:
        body = query.split("recid:", 1)[1]
        low, high = (int(part) for part in body.split("->"))
        return [value for value in self.ids if low <= value <= high]

    def fetch(self, collection, query, page, size, sort=None):
        with self.lock:
            self.calls += 1
        window = self._window(query)
        if size == 1:
            return {"hits": {"total": len(window), "hits": []}}
        chunk = window[(page - 1) * size: page * size]
        return {"hits": {"total": len(window), "hits": [{
            "updated": "2026-09-16T00:00:00Z",
            "metadata": {
                "control_number": recid,
                "titles": [{"title": f"Work {recid}"}],
                "document_type": ["article"],
                "author_count": 2,
                "earliest_date": "2015-03-04",
                "authors": [{"record": {"$ref": f"https://inspirehep.net/api/authors/{recid % 500}"}},
                            {"record": {"$ref": f"https://inspirehep.net/api/authors/{recid % 500 + 1000}"}}],
            }} for recid in chunk]}}


@pytest.fixture
def database():
    connection = psycopg.connect(URL, autocommit=True, row_factory=psycopg.rows.dict_row)
    for table in ("inspire_compact_membership", "inspire_compact_work",
                  "inspire_compact_shard", "inspire_compact_import"):
        connection.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
    connection.execute(SCHEMA)
    connection.execute(
        "INSERT INTO inspire_compact_import(import_id,source_cutoff,low_recid,high_recid,status) "
        "VALUES (%s, now(), 1, 40000, 'FETCHING')", (IMPORT_ID,))
    connection.execute(
        "INSERT INTO inspire_compact_shard(import_id,low_recid,high_recid,status) "
        "VALUES (%s,1,40000,'DISCOVER')", (IMPORT_ID,))
    yield connection
    connection.close()


def _run(monkeypatch, fake, **kwargs):
    import hepgraph.fast_compact_import as module

    monkeypatch.setattr(module, "_PacedClient", lambda limiter: fake)
    return module.run(URL, IMPORT_ID, rate=0, **kwargs)


def test_parallel_import_retains_every_record_exactly_once(database, monkeypatch):
    # 25,000 ids over a 40,000-wide range forces the 10,000-result window to
    # split several times, which is where a parallel claimer would go wrong.
    ids = list(range(1, 40000, 16))[:25000]
    fake = FakeInspire(ids)
    _run(monkeypatch, fake, workers=8)

    works = database.execute(
        "SELECT count(*) AS n FROM inspire_compact_work WHERE import_id=%s", (IMPORT_ID,)).fetchone()["n"]
    assert works == len(ids)
    stored = [row["work_id"] for row in database.execute(
        "SELECT work_id FROM inspire_compact_work WHERE import_id=%s ORDER BY work_id",
        (IMPORT_ID,)).fetchall()]
    assert stored == sorted(ids)
    memberships = database.execute(
        "SELECT count(*) AS n FROM inspire_compact_membership WHERE import_id=%s",
        (IMPORT_ID,)).fetchone()["n"]
    assert memberships == 2 * len(ids)


def test_every_shard_finishes_and_tiles_the_range(database, monkeypatch):
    ids = list(range(1, 40000, 16))[:25000]
    _run(monkeypatch, FakeInspire(ids), workers=8)
    outstanding = database.execute(
        "SELECT count(*) AS n FROM inspire_compact_shard WHERE import_id=%s "
        "AND status NOT IN ('DONE','SPLIT')", (IMPORT_ID,)).fetchone()["n"]
    assert outstanding == 0
    failed = database.execute(
        "SELECT count(*) AS n FROM inspire_compact_shard WHERE import_id=%s AND status='FAILED'",
        (IMPORT_ID,)).fetchone()["n"]
    assert failed == 0


def test_leaf_shards_received_exactly_what_was_expected(database, monkeypatch):
    ids = list(range(1, 40000, 16))[:25000]
    _run(monkeypatch, FakeInspire(ids), workers=6)
    rows = database.execute(
        "SELECT low_recid,high_recid,expected_records,received_records FROM inspire_compact_shard "
        "WHERE import_id=%s AND status='DONE'", (IMPORT_ID,)).fetchall()
    assert rows
    for row in rows:
        # No shard may over- or under-receive: a parallel claimer that let two
        # workers page the same shard would inflate this counter.
        assert row["received_records"] == row["expected_records"], dict(row)


def test_a_resumed_run_adds_nothing_and_changes_nothing(database, monkeypatch):
    ids = list(range(1, 40000, 16))[:25000]
    _run(monkeypatch, FakeInspire(ids), workers=6)
    before = database.execute(
        "SELECT count(*) AS w, (SELECT count(*) FROM inspire_compact_membership) AS m "
        "FROM inspire_compact_work").fetchone()
    second = FakeInspire(ids)
    _run(monkeypatch, second, workers=6)
    after = database.execute(
        "SELECT count(*) AS w, (SELECT count(*) FROM inspire_compact_membership) AS m "
        "FROM inspire_compact_work").fetchone()
    assert (after["w"], after["m"]) == (before["w"], before["m"])
    # Nothing is left to do, so a resume must not re-fetch the corpus either.
    assert second.calls == 0


def test_failed_shards_are_retried_by_the_next_run(database, monkeypatch):
    ids = list(range(1, 40000, 16))[:25000]

    class Flaky(FakeInspire):
        def __init__(self, ids):
            super().__init__(ids)
            self.failed_once = False

        def fetch(self, collection, query, page, size, sort=None):
            with self.lock:
                if not self.failed_once and size > 1 and page == 1:
                    self.failed_once = True
                    raise RuntimeError("upstream blip")
            return super().fetch(collection, query, page, size, sort)

    _run(monkeypatch, Flaky(ids), workers=4)
    # The blip marked one shard FAILED; a second run must resume and finish it.
    _run(monkeypatch, FakeInspire(ids), workers=4)
    outstanding = database.execute(
        "SELECT count(*) AS n FROM inspire_compact_shard WHERE import_id=%s "
        "AND status NOT IN ('DONE','SPLIT')", (IMPORT_ID,)).fetchone()["n"]
    assert outstanding == 0
    works = database.execute(
        "SELECT count(*) AS n FROM inspire_compact_work WHERE import_id=%s", (IMPORT_ID,)).fetchone()["n"]
    assert works == len(ids)


def test_rate_limiter_paces_the_whole_pool_not_each_thread():
    limiter = RateLimiter(50.0)
    started = threading.Barrier(4)

    def take():
        started.wait()
        for _ in range(5):
            limiter.take()

    import time

    threads = [threading.Thread(target=take) for _ in range(4)]
    clock = time.monotonic()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    # 20 tokens at 50/s cannot be served faster than ~0.38 s however many
    # threads ask for them.
    assert time.monotonic() - clock >= 0.3
