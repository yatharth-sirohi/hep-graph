"""Tests for the HEP Atlas builder (hepgraph/atlas/build.py).

`docs/HEP_ATLAS_BUNDLES.md` is the contract this module implements; these
tests build the fixture dataset (`tests/fixtures/atlas_minimal/`) into a
temporary directory and check the bundles against that contract: byte-for-byte
determinism, the provenance split (A14), that people never leak into
`search.json`, that they are sharded per (collaboration, institution), that
`hep_graph.url` is derived only for `person:inspire-*` ids, and that graph
edges carry intervals (§7 / A9).
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import pytest

from hepgraph.atlas import schema
from hepgraph.atlas.build import BuildResult, build

FIXTURE = Path(__file__).parent / "fixtures" / "atlas_minimal"
BUILD_DATE = dt.date(2026, 9, 16)


@pytest.fixture(scope="module")
def built(tmp_path_factory) -> BuildResult:
    out_dir = tmp_path_factory.mktemp("atlas-build")
    result = build(FIXTURE, out_dir, build_date=BUILD_DATE)
    assert result.errors == [], result.errors
    return result


def _json(result: BuildResult, path: str) -> dict:
    return json.loads(result.files[path])


# ---------------------------------------------------------------------------
# Determinism (A11 / the bundles contract)
# ---------------------------------------------------------------------------

def test_build_reports_no_errors_on_the_fixture(built: BuildResult) -> None:
    assert built.errors == []
    assert built.drift == []


def test_two_builds_of_the_same_data_are_byte_identical(tmp_path: Path) -> None:
    first = build(FIXTURE, tmp_path / "out1", build_date=BUILD_DATE)
    second = build(FIXTURE, tmp_path / "out2", build_date=BUILD_DATE)
    assert first.errors == [] and second.errors == []
    assert set(first.files) == set(second.files)
    for path in first.files:
        assert first.files[path] == second.files[path], f"{path} is not deterministic"
    assert first.version == second.version


def test_build_check_mode_reports_no_drift_against_its_own_output(tmp_path: Path) -> None:
    out_dir = tmp_path / "atlas-out"
    build(FIXTURE, out_dir, build_date=BUILD_DATE)
    checked = build(FIXTURE, out_dir, build_date=BUILD_DATE, check=True)
    assert checked.drift == []
    # --check must not write anything.
    assert checked.written == [] and checked.removed == []


def test_every_bundle_is_canonical_json(built: BuildResult) -> None:
    from hepgraph.atlas.load import dump_json

    for path, text in built.files.items():
        payload = json.loads(text)
        assert text == dump_json(payload), f"{path} is not canonical JSON (A11)"


def test_manifest_lists_every_bundle_with_a_hash(built: BuildResult) -> None:
    manifest = _json(built, "manifest.json")
    assert manifest["version"] == built.version
    assert manifest["build_date"] == BUILD_DATE.isoformat()
    for path, text in built.files.items():
        if path == "manifest.json":
            continue
        entry = manifest["bundles"][path]
        assert entry["bytes"] == len(text.encode("utf-8"))
    assert manifest["counts"]["experiments"] == 1
    assert manifest["counts"]["people"] == 2


def test_written_files_on_disk_match_the_in_memory_bundles(tmp_path: Path) -> None:
    out_dir = tmp_path / "atlas-out"
    result = build(FIXTURE, out_dir, build_date=BUILD_DATE)
    for path, text in result.files.items():
        assert (out_dir / path).read_text(encoding="utf-8") == text


# ---------------------------------------------------------------------------
# The provenance split (A14)
# ---------------------------------------------------------------------------

def test_atlas_json_carries_no_provenance_keys(built: BuildResult) -> None:
    """`sources`, `verified_at`, `confidence`, `note`, `quote`, `locator` all
    move to `provenance.json`; `atlas.json` keeps only stripped values."""
    atlas_bundle = _json(built, "atlas.json")

    def walk(node) -> None:
        if isinstance(node, dict):
            for key in schema.PROVENANCE_KEYS:
                assert key not in node, f"atlas.json leaks provenance key {key!r}: {node}"
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    for entity_type in ("facilities", "sites", "accelerators", "beamlines", "experiments",
                        "detectors", "collaborations", "topics"):
        walk(atlas_bundle[entity_type])


def test_provenance_json_holds_sourced_fields_by_pointer(built: BuildResult) -> None:
    provenance = _json(built, "provenance.json")
    experiment = provenance["experiment:demo"]
    # A record-level `sources` is addressed at the `/sources` pointer (A14/A22).
    assert "/sources" in experiment
    assert experiment["/sources"]["sources"], "record-level sources must be preserved"
    # A nested sourced value (a key_specs quantity) keeps its own pointer.
    baseline = experiment["/key_specs/0/quantity"]
    assert baseline["sources"] == ["src:demo-tdr"]
    assert baseline["confidence"] == "verified"
    # Every provenance record carries the full A14/A15 key set.
    for entry in experiment.values():
        assert set(entry) == {"sources", "verified_at", "confidence", "note", "quote", "locator"}


def test_provenance_json_covers_membership_rows_under_the_collaboration_id(built: BuildResult) -> None:
    provenance = _json(built, "provenance.json")
    roster_provenance = provenance["collaboration:demo"]
    assert any(pointer.startswith("/members/") for pointer in roster_provenance)


def test_stripped_interval_keeps_only_display_fields(built: BuildResult) -> None:
    experiment = _json(built, "atlas.json")["experiments"]["experiment:demo"]
    for interval in experiment["intervals"]:
        assert set(interval) <= {"label", "status", "start", "end", "kind", "specs"}
        assert "sources" not in interval and "verified_at" not in interval


# ---------------------------------------------------------------------------
# People: never in search, sharded per (collaboration, institution)
# ---------------------------------------------------------------------------

def test_search_json_contains_no_people(built: BuildResult) -> None:
    search = _json(built, "search.json")
    types = {entry[0] for entry in search["entries"]}
    assert "person" not in types
    # Every non-person entity type in the fixture is still searchable.
    assert {"experiment", "facility", "site", "accelerator", "beamline", "detector",
            "collaboration", "topic", "institution", "result", "document"} <= types


def test_search_json_is_sorted_by_type_then_id(built: BuildResult) -> None:
    search = _json(built, "search.json")
    ids = [(entry[0], entry[1]) for entry in search["entries"]]
    assert ids == sorted(ids)


def test_people_are_sharded_per_collaboration_and_institution(built: BuildResult) -> None:
    # The fixture has one person at institution:university-of-iowa and one
    # (unresolved) at institution:demo-lab, both in collaboration:demo.
    iowa_bundle = _json(built, "people/demo/university-of-iowa.json")
    assert iowa_bundle["collaboration_id"] == "collaboration:demo"
    assert iowa_bundle["institution_id"] == "institution:university-of-iowa"
    assert [person["id"] for person in iowa_bundle["people"]] == ["person:inspire-1019647"]

    lab_bundle = _json(built, "people/demo/demo-lab.json")
    assert lab_bundle["institution_id"] == "institution:demo-lab"
    assert [person["id"] for person in lab_bundle["people"]] == [
        "person:unresolved-demo-demo-lab-demo-student"]

    # No cross-contamination: neither bundle repeats the other's person.
    assert iowa_bundle["people"][0]["id"] not in [p["id"] for p in lab_bundle["people"]]


def test_a_membership_row_naming_no_institution_goes_to_the_unknown_shard(tmp_path: Path) -> None:
    import shutil

    root = tmp_path / "atlas"
    shutil.copytree(FIXTURE, root)
    person_path = root / "people" / "inspire-1019647.json"
    person = json.loads(person_path.read_text(encoding="utf-8"))
    person["memberships"][0]["institution_id"] = None
    person_path.write_text(json.dumps(person), encoding="utf-8")

    result = build(root, tmp_path / "out", build_date=BUILD_DATE)
    assert result.errors == []
    unknown = json.loads(result.files["people/demo/_unknown.json"])
    assert [row["id"] for row in unknown["people"]] == ["person:inspire-1019647"]


def test_hep_graph_url_is_derived_only_for_inspire_people(built: BuildResult) -> None:
    iowa_bundle = _json(built, "people/demo/university-of-iowa.json")
    resolved = iowa_bundle["people"][0]
    assert resolved["id"] == "person:inspire-1019647"
    assert resolved["hep_graph"]["available"] is True
    assert resolved["hep_graph"]["url"] == "/?source=1019647&mode=live"

    lab_bundle = _json(built, "people/demo/demo-lab.json")
    unresolved = lab_bundle["people"][0]
    assert unresolved["id"].startswith("person:unresolved-")
    assert unresolved["hep_graph"] == {"available": False}
    assert "url" not in unresolved["hep_graph"]


# ---------------------------------------------------------------------------
# graph.json: edges carry intervals (§7 / A9)
# ---------------------------------------------------------------------------

def test_graph_edges_carry_intervals(built: BuildResult) -> None:
    graph = _json(built, "graph.json")
    edges = {(edge["type"], edge["from"], edge["to"]): edge for edge in graph["edges"]}

    # An explicit A9 object entry (`experiment.accelerator_ids[0]` carries its
    # own start/end) is used verbatim, not the hull intersection.
    uses_accelerator = edges[("USES_ACCELERATOR", "experiment:demo", "accelerator:demo-synchrotron")]
    assert uses_accelerator["start"] == "2010-03"
    assert uses_accelerator["end"] is None
    assert uses_accelerator["start_month"] == schema.month_index(dt.date(2010, 3, 1))
    assert uses_accelerator["end_month"] is None

    # MEMBER_OF for a person carries the membership row's own interval.
    member_of = edges[("MEMBER_OF", "person:inspire-1019647", "collaboration:demo")]
    assert member_of["start"] == "2012"
    assert member_of["start_month"] == schema.month_index(dt.date(2012, 1, 1))


def test_graph_edges_fall_back_to_the_hull_intersection_when_untimed(built: BuildResult) -> None:
    graph = _json(built, "graph.json")
    edges = {(edge["type"], edge["from"], edge["to"]): edge for edge in graph["edges"]}
    # `detector.experiment_ids` carries no per-entry interval, so the USES edge
    # falls back to the intersection of the two entities' existence hulls.
    uses = edges[("USES", "experiment:demo", "detector:demo-far-detector")]
    assert uses["start"] is not None, "the hull intersection must fill in a start"
    assert uses["start_month"] is not None


def test_graph_json_is_sorted_and_deduplicated(built: BuildResult) -> None:
    graph = _json(built, "graph.json")
    keys = [(edge["type"], edge["from"], edge["to"]) for edge in graph["edges"]]
    assert keys == sorted(keys)
    assert len(keys) == len(set(keys)), "one edge per (type, from, to) triple"


# ---------------------------------------------------------------------------
# The globe's contract: every site's coordinates are readable as lat/lon.
#
# docs/HEP_ATLAS_BUNDLES.md's stripping-rules table is explicit about this
# shape: "Coordinates | {"lat", "lon", "precision_m", "kind"}" — a *nested*
# object, matching the canonical data files (§2.5) exactly, not the
# flattened `site.lat` / `site.lon` a since-fixed frontend bug assumed.
# That nested shape is the one this test enforces: it is what the doc
# already specifies, what `build.py` already emits, and the shape
# `static/atlas/fixtures/build_fixture.py` should be regenerated to match
# rather than the other way around (see the final report for detail).
# ---------------------------------------------------------------------------

def test_every_site_with_authored_coordinates_has_readable_lat_lon(built: BuildResult) -> None:
    sites = _json(built, "atlas.json")["sites"]
    from hepgraph.atlas.load import load_atlas

    authored = load_atlas(FIXTURE)
    checked = 0
    for site_id, site in sites.items():
        authored_coordinates = authored.get(site_id).get("coordinates")
        if not isinstance(authored_coordinates, dict):
            continue  # A17: a site legitimately may not have coordinates yet.
        checked += 1
        coordinates = site.get("coordinates")
        assert coordinates is not None, (
            f"{site_id} has authored coordinates but the built bundle's are null — "
            f"exactly the shape that left the globe with a NaN bounding sphere")
        assert isinstance(coordinates, dict), f"{site_id}.coordinates must be an object, not flattened"
        assert set(coordinates) == {"lat", "lon", "precision_m", "kind"}, (
            f"{site_id}.coordinates must match the BUNDLES.md contract exactly, got "
            f"{sorted(coordinates)}")
        assert isinstance(coordinates["lat"], (int, float)) and not isinstance(coordinates["lat"], bool)
        assert isinstance(coordinates["lon"], (int, float)) and not isinstance(coordinates["lon"], bool)
        assert -90.0 <= coordinates["lat"] <= 90.0
        assert -180.0 <= coordinates["lon"] <= 180.0
    assert checked >= 2, "the fixture should exercise more than one site with coordinates"


def test_site_coordinates_are_never_flattened_onto_the_record(built: BuildResult) -> None:
    """The bug this guards against: `site.lat` / `site.lon` alongside (or
    instead of) `site.coordinates` — the shape a since-fixed frontend
    build assumed and the canonical data never provided."""
    sites = _json(built, "atlas.json")["sites"]
    for site_id, site in sites.items():
        assert "lat" not in site and "lon" not in site, (
            f"{site_id} carries top-level lat/lon; coordinates belong under "
            f"the nested `coordinates` object per BUNDLES.md")


def test_institution_coordinates_use_the_same_nested_contract(built: BuildResult) -> None:
    """`institutions.json` carries `coordinates` too (§8); the shape must be
    the same nested one, not a second, different convention."""
    institutions = _json(built, "institutions.json")
    checked = 0
    for institution_id, institution in institutions.items():
        if not isinstance(institution, dict):
            continue  # the bundle-level "schema" tag, not an institution
        coordinates = institution.get("coordinates")
        if coordinates is None:
            continue
        checked += 1
        assert set(coordinates) == {"lat", "lon", "precision_m", "kind"}
        assert isinstance(coordinates["lat"], (int, float))
        assert isinstance(coordinates["lon"], (int, float))
    assert checked >= 1


# ---------------------------------------------------------------------------
# A14: a `note` qualifier on an interval's `start`/`end` date object is
# provenance and must not leak into atlas.json alongside the display keys
# the BUNDLES.md contract actually names for a Date object.
# ---------------------------------------------------------------------------

def test_no_provenance_keys_leak_through_an_intervals_start_or_end(tmp_path: Path) -> None:
    import shutil

    root = tmp_path / "atlas"
    shutil.copytree(FIXTURE, root)
    experiment_path = root / "experiments" / "demo.json"
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    experiment["intervals"][-1]["end"] = None
    experiment["intervals"][-1]["start"] = {
        "date": "2017", "approx": True,
        "note": "a note on the date qualifier itself, not the interval — must not leak",
    }
    experiment_path.write_text(json.dumps(experiment), encoding="utf-8")

    result = build(root, tmp_path / "out", build_date=BUILD_DATE)
    assert result.errors == []
    built_experiment = json.loads(result.files["atlas.json"])["experiments"]["experiment:demo"]
    mutated_interval = built_experiment["intervals"][-1]
    assert set(mutated_interval["start"]) == {"date", "approx"}, (
        "the stripped Date object must match BUNDLES.md's documented shape "
        "(date/approx/planned/display/…), not carry a bare `note`")
    provenance = json.loads(result.files["provenance.json"])
    pointer = f"/intervals/{len(experiment['intervals']) - 1}/start"
    assert provenance["experiment:demo"][pointer]["note"] == (
        "a note on the date qualifier itself, not the interval — must not leak")


# ---------------------------------------------------------------------------
# Sanity checks on the remaining bundles the fixture must exercise.
# ---------------------------------------------------------------------------

def test_institutions_bundle_carries_derived_collaboration_ids(built: BuildResult) -> None:
    institutions = _json(built, "institutions.json")
    iowa = institutions["institution:university-of-iowa"]
    assert iowa["collaboration_ids"] == ["collaboration:demo"]


def test_sources_bundle_has_a_derived_rank_and_cited_by(built: BuildResult) -> None:
    sources = _json(built, "sources.json")
    tdr = sources["src:demo-tdr"]
    assert tdr["rank"] == schema.source_rank("design_report")
    assert "experiment:demo" in tdr["cited_by"]


def test_results_bundle_has_a_month_index(built: BuildResult) -> None:
    results = _json(built, "results.json")
    result = results["result:demo-oscillation-observation-2020"]
    assert result["month"] == schema.month_index(dt.date(2020, 3, 15))


def test_membership_bundle_reports_confirmed_and_undated_counts(built: BuildResult) -> None:
    roster = _json(built, "memberships/demo.json")
    assert roster["collaboration_id"] == "collaboration:demo"
    assert "counts" in roster and "confirmed" in roster["counts"]
