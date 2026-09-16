from datetime import datetime, timedelta, timezone
import sqlite3

import pytest

from hepgraph.snapshot_registry import SnapshotRegistry, SnapshotStateError


PASSING = {
    "source_complete": True, "checksums_match": True,
    "identity_passed": True, "work_semantics_passed": True,
    "graph_passed": True, "search_passed": True,
    "benchmark_passed": True, "preview_passed": True,
}


def registry():
    return SnapshotRegistry(sqlite3.connect(":memory:"))


def candidate(store):
    return store.create_candidate(
        schema_version="test-v1", build_code_commit="abc123",
        source_cutoff=(datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
        source_description="complete synthetic test universe")


def ready(store):
    snapshot_id = candidate(store)
    store.advance(snapshot_id, "FETCHING")
    store.advance(snapshot_id, "BUILDING")
    store.advance(snapshot_id, "VALIDATING")
    store.mark_ready(snapshot_id, checksum="a" * 64, validation_report=PASSING)
    return snapshot_id


def test_incomplete_candidate_cannot_affect_active():
    store = registry()
    first = ready(store)
    store.promote(first)
    second = candidate(store)
    store.advance(second, "FETCHING")
    store.advance(second, "FAILED")
    with pytest.raises(SnapshotStateError, match="READY"):
        store.promote(second)
    assert store.pin_active()[0] == first
    assert store.state(first) == "ACTIVE" and store.state(second) == "FAILED"
    store.advance(second, "FETCHING")  # resume same candidate
    assert store.state(second) == "FETCHING"


def test_validation_all_gates_required_and_promotion_is_distinct():
    store = registry()
    snapshot_id = candidate(store)
    store.advance(snapshot_id, "FETCHING")
    store.advance(snapshot_id, "BUILDING")
    store.advance(snapshot_id, "VALIDATING")
    with pytest.raises(SnapshotStateError, match="all independent"):
        store.mark_ready(snapshot_id, checksum="a" * 64,
                         validation_report={**PASSING, "source_complete": False})
    with pytest.raises(SnapshotStateError, match="SHA-256"):
        store.mark_ready(snapshot_id, checksum="bad", validation_report=PASSING)
    assert store.pin_active() == (None, 0)
    store.mark_ready(snapshot_id, checksum="b" * 64, validation_report=PASSING)
    assert store.pin_active() == (None, 0)  # READY is not ACTIVE
    store.promote(snapshot_id)
    assert store.pin_active() == (snapshot_id, 1)


def test_atomic_pointer_pinning_and_rollback():
    store = registry()
    first = ready(store)
    store.promote(first)
    pinned = store.pin_active()
    second = ready(store)
    store.promote(second)
    assert pinned == (first, 1)  # existing request retains A
    assert store.pin_active() == (second, 2)
    assert store.state(first) == "SUPERSEDED"
    assert store.status()["previous_snapshot"] == first
    assert store.status()["age_days"] >= 2
    restored = store.rollback()
    assert restored == first
    assert store.pin_active() == (first, 3)
    assert store.state(second) == "SUPERSEDED"
    with pytest.raises(SnapshotStateError, match="no previous"):
        store.rollback()


def test_active_snapshot_cannot_reenter_build_states():
    store = registry()
    snapshot_id = ready(store)
    store.promote(snapshot_id)
    for status in ("FETCHING", "BUILDING", "FAILED", "READY"):
        with pytest.raises(SnapshotStateError):
            store.advance(snapshot_id, status)
    assert store.pin_active()[0] == snapshot_id


def test_future_or_naive_cutoff_rejected():
    store = registry()
    with pytest.raises(ValueError, match="timezone-aware"):
        store.create_candidate(schema_version="v1", build_code_commit="abc",
                               source_cutoff="2026-09-16", source_description="test")
