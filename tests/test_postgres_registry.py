"""Opt-in integration checks against an isolated disposable PostgreSQL DB.

Set HEPGRAPH_TEST_POSTGRES_DSN to a dedicated empty test database. The suite
never connects to production, creates a provider account, or uses Neon by
default. The test owns and removes only its uniquely prefixed schema.
"""

from datetime import datetime, timedelta, timezone
import os
from uuid import uuid4

import pytest

from hepgraph.postgres_registry import PostgresSnapshotRegistry
from hepgraph.snapshot_registry import SnapshotStateError


PASSING = {
    "source_complete": True, "checksums_match": True,
    "identity_passed": True, "work_semantics_passed": True,
    "graph_passed": True, "search_passed": True,
    "benchmark_passed": True, "preview_passed": True,
}


@pytest.fixture
def registry():
    dsn = os.environ.get("HEPGRAPH_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("set HEPGRAPH_TEST_POSTGRES_DSN for isolated PostgreSQL integration tests")
    psycopg = pytest.importorskip("psycopg")
    schema = "hepgraph_test_" + uuid4().hex
    with psycopg.connect(dsn, autocommit=True) as connection:
        connection.execute(f'CREATE SCHEMA "{schema}"')
        try:
            connection.execute(f'SET search_path TO "{schema}"')
            store = PostgresSnapshotRegistry(connection)
            store.ensure_schema()
            yield store
        finally:
            connection.execute("SET search_path TO public")
            connection.execute(f'DROP SCHEMA "{schema}" CASCADE')


def _candidate(store):
    return store.create_candidate(
        schema_version="test-v1", build_code_commit="abc123",
        source_cutoff=(datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
        source_description="complete synthetic test universe")


def _ready(store):
    snapshot_id = _candidate(store)
    store.advance(snapshot_id, "FETCHING")
    store.advance(snapshot_id, "BUILDING")
    store.advance(snapshot_id, "VALIDATING")
    store.mark_ready(snapshot_id, checksum="a" * 64, validation_report=PASSING)
    return snapshot_id


def test_postgres_promotion_and_rollback_are_atomic(registry):
    first = _ready(registry)
    assert registry.pin_active() == (None, 0)
    registry.promote(first)
    pinned = registry.pin_active()
    second = _ready(registry)
    registry.promote(second)
    assert pinned == (first, 1)
    assert registry.pin_active() == (second, 2)
    assert registry.state(first) == "SUPERSEDED"
    assert registry.status()["previous_snapshot"] == first
    assert registry.rollback() == first
    assert registry.pin_active() == (first, 3)
    with pytest.raises(SnapshotStateError, match="no previous"):
        registry.rollback()


def test_postgres_incomplete_candidate_cannot_promote(registry):
    first = _ready(registry)
    registry.promote(first)
    second = _candidate(registry)
    registry.advance(second, "FETCHING")
    registry.advance(second, "FAILED")
    with pytest.raises(SnapshotStateError, match="READY"):
        registry.promote(second)
    assert registry.pin_active()[0] == first
    registry.advance(second, "FETCHING")
    assert registry.state(second) == "FETCHING"


def test_postgres_validation_gates_and_autocommit(registry):
    candidate = _candidate(registry)
    registry.advance(candidate, "FETCHING")
    registry.advance(candidate, "BUILDING")
    registry.advance(candidate, "VALIDATING")
    with pytest.raises(SnapshotStateError, match="all independent"):
        registry.mark_ready(candidate, checksum="a" * 64,
                            validation_report={**PASSING, "graph_passed": False})
    with pytest.raises(SnapshotStateError, match="SHA-256"):
        registry.mark_ready(candidate, checksum="bad", validation_report=PASSING)
    assert registry.state(candidate) == "VALIDATING"
    registry.mark_ready(candidate, checksum="b" * 64, validation_report=PASSING)
    assert registry.pin_active() == (None, 0)
