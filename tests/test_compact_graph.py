import sqlite3

import pytest

from hepgraph.compact_graph import (CompactSQLiteProvider, build_compact_fixture,
                                    pack_ids, unpack_ids)
from hepgraph.graph import Filters, GraphError
from hepgraph.hlbes import COMPLETE, PARTIAL, UNKNOWN
from hepgraph.providers import FixtureGraphProvider


def fixture():
    return {
        "version": "compact-fixture", "source_cutoff": "2026-09-01T00:00:00Z",
        "people": [{"id": str(i), "name": f"Person {i}"} for i in range(1, 7)],
        "works": [
            {"id": "100", "title": "Paper A", "document_types": ["article"],
             "year": 2020, "author_count": 2, "authors": ["1", "2"]},
            {"id": "101", "title": "Paper B", "document_types": ["article"],
             "year": 2021, "author_count": 2, "authors": ["1", "2"]},
            {"id": "102", "title": "Large team", "document_types": ["article"],
             "year": 2021, "author_count": 11, "authors": ["2", "3"], "unresolved_count": 9},
            {"id": "103", "title": "Erratum: Paper A", "document_types": ["article"],
             "year": 2020, "author_count": 2, "authors": ["1", "4"]},
            {"id": "104", "title": "Solo", "document_types": ["article"],
             "year": 2020, "author_count": 1, "authors": ["5"]},
        ],
        "phd": [{"adviser": "3", "student": "4", "source_record": "200"}],
    }


def test_delta_varint_roundtrip_and_invalid_stream():
    ids = ["1", "3", "128", "129", "1000000", "128", "987654321"]
    blob = pack_ids(ids)
    assert unpack_ids(blob) == ("1", "3", "128", "129", "1000000", "987654321")
    assert len(blob) < len(",".join(ids))
    with pytest.raises(ValueError, match="truncated"):
        unpack_ids(bytes([0x80]))
    with pytest.raises(ValueError, match="positive"):
        pack_ids([0])


def test_compact_incidence_preserves_filter_and_evidence_semantics(tmp_path):
    path = tmp_path / "compact.sqlite"
    snapshot = fixture()
    build_compact_fixture(snapshot, path)
    with pytest.raises(FileExistsError):
        build_compact_fixture(snapshot, path)
    reference = FixtureGraphProvider(snapshot, complete=True)
    provider = CompactSQLiteProvider(path, complete_for_test=True)
    try:
        assert provider.resolve_author("5") == {"id": "5"}  # isolated author retained
        assert provider.resolve_author("999") is None
        for filters in (Filters(), Filters(genealogy=False),
                        Filters(min_shared=2, genealogy=False),
                        Filters(max_authors=None, genealogy=False),
                        Filters(min_authors=11, max_authors=None, genealogy=False),
                        Filters(year_start=2021, year_end=2021),
                        Filters(max_authors=None, year_end=2020)):
            for author_id in ("1", "2", "3", "4", "5", "6", "999"):
                actual = provider.get_neighbors(author_id, filters)
                expected = reference.get_neighbors(author_id, filters)
                assert (actual.members, actual.status) == (expected.members, expected.status)
            for source, target in (("1", "2"), ("2", "3"), ("3", "4"), ("1", "4")):
                assert provider.get_edge_evidence_refs(source, target, filters) == \
                    reference.get_edge_evidence_refs(source, target, filters)
        assert provider.get_work_metadata("100") == {
            "id": "100", "year": 2020, "author_count": 2,
            "source_url": "https://inspirehep.net/literature/100",
        }
        assert provider.get_work_metadata("999") is None
        # The private index contains neither titles nor complete profiles.
        with sqlite3.connect(path) as db:
            assert "Paper A" not in "".join(db.iterdump())
    finally:
        provider.close()


def test_compact_provider_is_uncertified_by_default(tmp_path):
    path = tmp_path / "candidate.sqlite"
    build_compact_fixture(fixture(), path)
    provider = CompactSQLiteProvider(path)
    try:
        assert provider.get_neighbors("1", Filters()).status == PARTIAL
        assert provider.get_neighbors("999", Filters()).status == UNKNOWN
        assert provider.get_neighbors_batch(("1", "999"), Filters())["1"].status == PARTIAL
    finally:
        provider.close()


def test_missing_work_is_an_error_not_an_empty_complete_neighborhood(tmp_path):
    path = tmp_path / "broken.sqlite"
    build_compact_fixture(fixture(), path)
    with sqlite3.connect(path) as db:
        db.execute("DELETE FROM work WHERE id='100'")
    provider = CompactSQLiteProvider(path, complete_for_test=True)
    try:
        with pytest.raises(GraphError, match="missing work"):
            provider.get_neighbors("1", Filters())
    finally:
        provider.close()
