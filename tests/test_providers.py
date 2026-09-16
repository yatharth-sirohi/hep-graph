"""Provider-boundary tests; the fixture is synthetic, not the partial pilot."""

from dataclasses import replace
from types import SimpleNamespace

import pytest

from hepgraph.graph import Filters
from hepgraph.hlbes import COMPLETE, EXACT, HLBES, NO_PATH, PARTIAL, SEARCH_INCOMPLETE, UNKNOWN, VERIFIED, Neighborhood, OracleStopped
from hepgraph.providers import (FixtureGraphProvider, GraphVersion, LiveInspireGraphProvider,
                                ProviderNeighborhood, ProviderOracle, filter_key,
                                search_pinned_snapshot)
from hepgraph.synthetic_store import SyntheticSQLiteProvider, build_synthetic_index


def fixture():
    return {
        "version": "synthetic-1", "source_cutoff": "2026-09-01T00:00:00Z",
        "people": [{"id": key, "name": key} for key in "abcd"],
        "works": [
            {"id": "w1", "title": "one", "document_types": ["article"], "year": 2020,
             "author_count": 2, "authors": ["a", "b"]},
            {"id": "w2", "title": "two", "document_types": ["article"], "year": 2021,
             "author_count": 2, "authors": ["a", "b"]},
            {"id": "w3", "title": "three", "document_types": ["article"], "year": 2020,
             "author_count": 11, "authors": ["b", "c"], "unresolved_count": 9},
            {"id": "w4", "title": "Erratum: one", "document_types": ["article"], "year": 2020,
             "author_count": 2, "authors": ["a", "d"]},
        ],
        "phd": [{"adviser": "c", "student": "d", "source_record": "phd-1"}],
    }


def test_synthetic_complete_modes_filters_batch_and_evidence():
    provider = FixtureGraphProvider(fixture(), complete=True)
    default = Filters(genealogy=False)
    assert provider.get_graph_version().source_cutoff == "2026-09-01T00:00:00Z"
    assert provider.resolve_author("a")["name"] == "a"
    assert provider.get_neighbors_batch(("a", "b", "missing"), default)["missing"].status == UNKNOWN
    assert provider.get_neighbors("a", default).members == {"b"}
    assert provider.get_neighbors("b", default).members == {"a"}
    assert provider.get_edge_evidence_refs("a", "b", default) == ("work:w1", "work:w2")
    assert provider.get_work_metadata("w3")["author_count"] == 11
    assert provider.get_neighbors("b", Filters(min_authors=11, max_authors=None, genealogy=False)).members == {"c"}
    assert provider.get_neighbors("b", Filters(max_authors=None, genealogy=False)).members == {"a", "c"}
    assert provider.get_neighbors("b", Filters(min_shared=2, year_start=2020, year_end=2020,
                                                genealogy=False)).members == set()
    assert provider.get_neighbors("c", Filters()).members == {"d"}
    assert provider.get_edge_evidence_refs("c", "d", Filters()) == ("phd:phd-1",)
    assert HLBES(ProviderOracle(provider, default)).search("a", "b").status == EXACT
    assert HLBES(ProviderOracle(provider, default)).search("a", "d").status == NO_PATH


def test_partial_fixture_cannot_prove_absence_or_long_route():
    provider = FixtureGraphProvider(fixture())
    assert provider.get_completeness(Filters()) is False
    assert provider.get_neighbors("a", Filters()).status == PARTIAL
    assert HLBES(ProviderOracle(provider, Filters(genealogy=False))).search("a", "d").status == SEARCH_INCOMPLETE


def test_mixed_version_and_filter_cannot_enter_hlbes_proof():
    provider = FixtureGraphProvider(fixture(), complete=True)
    adapter = ProviderOracle(provider, Filters())
    provider.version = GraphVersion("promoted-after-session-start", None, "fixture-v1")
    with pytest.raises(OracleStopped, match="graph_version_changed"):
        adapter.neighborhood("a")

    provider = FixtureGraphProvider(fixture(), complete=True)
    adapter = ProviderOracle(provider, Filters())
    original = provider.get_neighbors
    provider.get_neighbors = lambda node, filters: replace(original(node, filters), filter_key="wrong")
    with pytest.raises(OracleStopped, match="mixed graph semantics"):
        adapter.neighborhood("a")


def test_live_adapter_preserves_each_author_status_and_rejects_filter_change():
    class Oracle:
        def neighborhood(self, node):
            return Neighborhood(frozenset({"b"}), COMPLETE if node == "a" else PARTIAL, node)

    filters = Filters()
    session = SimpleNamespace(filters=filters)
    provider = LiveInspireGraphProvider(session, Oracle())
    result = provider.get_neighbors_batch(("a", "c"), filters)
    assert result["a"].status == COMPLETE and result["c"].status == PARTIAL
    assert result["a"].cursor == "a" and result["c"].cursor == "c"
    assert provider.get_completeness(filters) is False
    with pytest.raises(ValueError, match="filters changed"):
        provider.get_neighbors("a", Filters(max_authors=None))


def test_provider_error_is_not_reclassified_as_empty_complete():
    provider = FixtureGraphProvider(fixture(), complete=True)
    adapter = ProviderOracle(provider, Filters())
    provider.get_neighbors = lambda *_: (_ for _ in ()).throw(OracleStopped("graph_provider_error"))
    with pytest.raises(OracleStopped, match="graph_provider_error"):
        adapter.neighborhood("a")
    assert filter_key(Filters()) == filter_key(Filters.from_dict({}))


def test_private_synthetic_sqlite_hybrid_matches_fixture_across_filters(tmp_path):
    path = tmp_path / "candidate.sqlite"
    snapshot = fixture()
    build_synthetic_index(snapshot, path)
    with pytest.raises(FileExistsError):
        build_synthetic_index(snapshot, path)
    provider = SyntheticSQLiteProvider(path, complete_for_test=True)
    reference = FixtureGraphProvider(snapshot, complete=True)
    try:
        assert provider.get_graph_version().source_cutoff == reference.get_graph_version().source_cutoff
        assert provider.resolve_author("a") == reference.resolve_author("a")
        for filters in (Filters(), Filters(genealogy=False),
                        Filters(min_authors=11, max_authors=None, genealogy=False),
                        Filters(max_authors=None, genealogy=False),
                        Filters(min_shared=2, year_start=2020, year_end=2020, genealogy=False),
                        Filters(max_authors=None, year_start=2021, genealogy=True)):
            for author in ("a", "b", "c", "d", "missing"):
                actual = provider.get_neighbors(author, filters)
                expected = reference.get_neighbors(author, filters)
                assert (actual.members, actual.status) == (expected.members, expected.status)
            for pair in (("a", "b"), ("b", "c"), ("c", "d"), ("a", "d")):
                assert provider.get_edge_evidence_refs(*pair, filters) == reference.get_edge_evidence_refs(*pair, filters)
        assert provider.get_work_metadata("w3") == reference.get_work_metadata("w3")
        assert HLBES(ProviderOracle(provider, Filters(max_authors=None))).search("a", "d").status == EXACT
    finally:
        provider.close()


def test_uncertified_synthetic_index_never_reports_complete(tmp_path):
    path = tmp_path / "uncertified.sqlite"
    build_synthetic_index(fixture(), path)
    provider = SyntheticSQLiteProvider(path)
    try:
        assert provider.get_neighbors("a", Filters()).status == PARTIAL
        assert HLBES(ProviderOracle(provider, Filters(genealogy=False))).search("a", "d").status == SEARCH_INCOMPLETE
    finally:
        provider.close()


def test_search_entry_distinguishes_absent_author_and_scopes_exactness():
    filters = Filters(max_authors=None)
    complete = FixtureGraphProvider(fixture(), complete=True)
    absent = search_pinned_snapshot(complete, "a", "new-live-author", filters)
    assert absent.status == "author_not_in_snapshot" and not absent.global_shortest_proven
    exact = search_pinned_snapshot(complete, "a", "d", filters)
    assert exact.status == EXACT and exact.global_shortest_proven
    assert exact.graph_snapshot == "synthetic-1" and exact.source_cutoff == "2026-09-01T00:00:00Z"
    assert exact.graph_mode == "all" and exact.filters == filters.to_dict()

    incomplete = FixtureGraphProvider(fixture())
    verified = search_pinned_snapshot(incomplete, "a", "b", filters)
    assert verified.status == VERIFIED and not verified.global_shortest_proven
    assert search_pinned_snapshot(incomplete, "a", "d", Filters(genealogy=False)).status == SEARCH_INCOMPLETE
