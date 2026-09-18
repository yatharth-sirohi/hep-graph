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


# ---------------------------------------------------------------------------
# A25 — the local-map geometry layer (docs/HEP_ATLAS_GEOMETRY.md §3)
# ---------------------------------------------------------------------------

MAP_ID = "map:demo-lab"
GEOMETRY_BUNDLE = "geometry/demo-lab.json"


def test_atlas_json_carries_a_maps_table(built: BuildResult) -> None:
    table = _json(built, "atlas.json")["maps"]
    entry = table[MAP_ID]
    assert entry["facility_id"] == "facility:demo-lab"
    assert entry["site_ids"] == ["site:demo-lab-campus"]
    assert entry["center"] == {"lat": 41.8325, "lon": -88.2525}
    assert entry["extent_m"] == 3000
    assert entry["bundle"] == GEOMETRY_BUNDLE
    assert [level["id"] for level in entry["levels"]] == ["surface", "ring-tunnel"]


def test_the_maps_table_counts_features_to_scale_and_unlocated(built: BuildResult) -> None:
    entry = _json(built, "atlas.json")["maps"][MAP_ID]
    assert entry["feature_count"] == 4
    # Three shapes are to scale; the inferred direction line is not a structure.
    assert entry["to_scale_count"] == 3
    assert entry["unlocated_count"] == 1


def test_a_map_inherits_its_facilitys_timeline(built: BuildResult) -> None:
    """A map is a view of a facility and never claims a history of its own."""
    atlas = _json(built, "atlas.json")
    entry = atlas["maps"][MAP_ID]
    facility = atlas["facilities"]["facility:demo-lab"]
    assert entry["state_segments"] == facility["state_segments"]
    assert entry["status"] == facility["status"]


def test_the_maps_table_aggregates_licence_attributions(built: BuildResult) -> None:
    entry = _json(built, "atlas.json")["maps"][MAP_ID]
    assert entry["attribution"] == ["© OpenStreetMap contributors (ODbL-1.0)"]


def test_a_level_depth_strips_like_a_quantity(built: BuildResult) -> None:
    """`levels[].depth_m` keeps its numbers; its sources go to provenance.json."""
    levels = _json(built, "atlas.json")["maps"][MAP_ID]["levels"]
    depth = next(level for level in levels if level["id"] == "ring-tunnel")["depth_m"]
    assert depth == {"value": 9, "unit": "m", "dimension": "length",
                     "display": "9 m", "approx": False}
    assert "sources" not in depth


def test_a_map_centre_strips_like_coordinates(built: BuildResult) -> None:
    provenance = _json(built, "provenance.json")[MAP_ID]
    assert "/center" in provenance
    assert provenance["/center"]["sources"] == ["src:demo-lab-site"]


def test_facilities_and_sites_gain_a_derived_map_id(built: BuildResult) -> None:
    atlas = _json(built, "atlas.json")
    assert atlas["facilities"]["facility:demo-lab"]["map_id"] == MAP_ID
    assert atlas["sites"]["site:demo-lab-campus"]["map_id"] == MAP_ID
    # A site no map covers says so with null, not by omitting the key.
    assert atlas["sites"]["site:demo-far-cavern"]["map_id"] is None


def test_machines_gain_derived_geometry_map_ids_even_when_empty(built: BuildResult) -> None:
    atlas = _json(built, "atlas.json")
    assert atlas["accelerators"]["accelerator:demo-synchrotron"]["geometry_map_ids"] == [MAP_ID]
    assert atlas["beamlines"]["beamline:demo-beam"]["geometry_map_ids"] == [MAP_ID]
    # The far detector is on no map; the key still exists so the frontend can
    # ask without checking whether it was emitted.
    assert atlas["detectors"]["detector:demo-far-detector"]["geometry_map_ids"] == []


def test_an_authored_derived_map_field_is_recomputed(tmp_path: Path) -> None:
    """A1: whatever a file writes into a derived field, the build ignores."""
    import shutil

    root = tmp_path / "atlas"
    shutil.copytree(FIXTURE, root)
    path = root / "sites" / "demo-far-cavern.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    record["map_id"] = "map:invented"
    path.write_text(json.dumps(record), encoding="utf-8")
    result = build(root, tmp_path / "out", build_date=BUILD_DATE)
    assert json.loads(result.files["atlas.json"])["sites"]["site:demo-far-cavern"]["map_id"] is None


def test_the_manifest_counts_maps_and_geometry(built: BuildResult) -> None:
    counts = _json(built, "manifest.json")["counts"]
    assert counts["maps"] == 1
    assert counts["geometry"] == 4


def test_search_json_offers_the_map(built: BuildResult) -> None:
    entries = [entry for entry in _json(built, "search.json")["entries"] if entry[0] == "map"]
    assert entries == [["map", MAP_ID, "Demo Laboratory — main campus", [],
                        "Local map · Demo Laboratory"]]


# -- the per-map bundle ------------------------------------------------------

def test_the_build_emits_one_geometry_bundle_per_map(built: BuildResult) -> None:
    assert GEOMETRY_BUNDLE in built.files


def test_the_geometry_bundle_has_the_shape_the_contract_specifies(built: BuildResult) -> None:
    bundle = _json(built, GEOMETRY_BUNDLE)
    assert set(bundle) == {"schema", "version", "build_date", "map", "bbox", "attribution",
                           "features", "source_titles", "entity_index"}
    assert bundle["version"] == built.version
    assert bundle["build_date"] == BUILD_DATE.isoformat()
    assert bundle["attribution"] == ["© OpenStreetMap contributors (ODbL-1.0)"]
    minlon, minlat, maxlon, maxlat = bundle["bbox"]
    assert minlon < maxlon and minlat < maxlat


def test_features_are_sorted_by_id(built: BuildResult) -> None:
    ids = [feature["id"] for feature in _json(built, GEOMETRY_BUNDLE)["features"]]
    assert ids == sorted(ids)
    assert ids == ["geometry:demo-beam-axis", "geometry:demo-beam-direction",
                   "geometry:demo-synchrotron-ring", "geometry:demo-target-hall"]


def test_a_feature_carries_its_measurements_and_provenance(built: BuildResult) -> None:
    feature = next(f for f in _json(built, GEOMETRY_BUNDLE)["features"]
                   if f["id"] == "geometry:demo-synchrotron-ring")
    assert feature["entity_id"] == "accelerator:demo-synchrotron"
    assert feature["entity_type"] == "accelerator"
    assert feature["entity_name"] == "Demo Synchrotron"
    assert feature["representation"] == "derived"
    assert feature["accuracy_m"] == 120
    assert feature["measured"]["length_m"] == pytest.approx(3300, rel=1e-3)
    assert feature["measured"]["area_m2"] is None
    assert feature["measured"]["centroid"] is not None
    assert feature["provenance"]["confidence"] == "derived"
    assert feature["provenance"]["sources"] == ["src:demo-lab-site"]
    assert feature["provenance"]["locator"]


def test_a_feature_reports_its_checks_with_the_arithmetic(built: BuildResult) -> None:
    feature = next(f for f in _json(built, GEOMETRY_BUNDLE)["features"]
                   if f["id"] == "geometry:demo-synchrotron-ring")
    check = feature["checks"][0]
    assert check["kind"] == "length"
    assert check["passed"] is True
    assert check["expected_m"] == pytest.approx(3300)
    assert check["measured_m"] == pytest.approx(3300, rel=1e-3)
    assert check["tolerance"] == 0.02
    assert check["sources"] == ["src:demo-lab-site"]


def test_the_geometry_value_strips_to_a_bare_geojson_object(built: BuildResult) -> None:
    """No `sources`/`confidence` inside the shape: they are in `provenance`."""
    for feature in _json(built, GEOMETRY_BUNDLE)["features"]:
        assert set(feature["geometry"]) == {"type", "coordinates"}
        assert feature["geometry"]["type"] in (
            "Point", "LineString", "MultiLineString", "Polygon", "MultiPolygon")


def test_coordinates_are_rounded_to_seven_decimals(built: BuildResult) -> None:
    from hepgraph.atlas import geo

    for feature in _json(built, GEOMETRY_BUNDLE)["features"]:
        for lon, lat in geo.positions(feature["geometry"]):
            assert round(lon, 7) == lon and round(lat, 7) == lat


def test_a_shape_with_its_own_valid_window_uses_it(built: BuildResult) -> None:
    """The ODbL building is valid from 1999; the feature's timeline says so."""
    from hepgraph.atlas import schema

    feature = next(f for f in _json(built, GEOMETRY_BUNDLE)["features"]
                   if f["id"] == "geometry:demo-target-hall")
    assert feature["state_segments"] == [[schema.month_index("1999-01"),
                                          schema.month_index(BUILD_DATE.isoformat()),
                                          "active", "certain"]]


def test_a_shape_without_valid_inherits_its_entitys_timeline(built: BuildResult) -> None:
    atlas = _json(built, "atlas.json")
    feature = next(f for f in _json(built, GEOMETRY_BUNDLE)["features"]
                   if f["id"] == "geometry:demo-beam-axis")
    assert feature["state_segments"] == atlas["beamlines"]["beamline:demo-beam"]["state_segments"]


def test_the_bundle_map_section_names_every_unlocated_entity(built: BuildResult) -> None:
    unlocated = _json(built, GEOMETRY_BUNDLE)["map"]["unlocated"]
    assert len(unlocated) == 1
    row = unlocated[0]
    assert row["entity_id"] == "experiment:demo"
    assert row["entity_name"] == "Demo Experiment"
    assert row["entity_type"] == "experiment"
    # An unlocated entry is worth nothing without a reason and a way forward.
    assert row["reason"] and row["backlog"] and row["sources"]


def test_schematics_are_links_only(built: BuildResult) -> None:
    schematics = _json(built, GEOMETRY_BUNDLE)["map"]["schematics"]
    assert len(schematics) == 1
    assert set(schematics[0]) == {"title", "url", "source_id", "note"}
    assert "not to scale" in schematics[0]["title"]


def test_the_bundle_indexes_features_by_the_entity_they_depict(built: BuildResult) -> None:
    index = _json(built, GEOMETRY_BUNDLE)["entity_index"]
    assert index["accelerator:demo-synchrotron"] == ["geometry:demo-synchrotron-ring"]
    assert index["beamline:demo-beam"] == ["geometry:demo-beam-axis",
                                           "geometry:demo-beam-direction"]
    # A context feature depicts nothing and is not in the index.
    assert all("geometry:demo-target-hall" not in rows for rows in index.values())


def test_the_bundle_titles_every_source_it_cites(built: BuildResult) -> None:
    bundle = _json(built, GEOMETRY_BUNDLE)
    titles = bundle["source_titles"]
    assert "src:demo-osm-extract" in titles
    assert titles["src:demo-osm-extract"]["source_type"] == "openstreetmap"
    cited = {source for feature in bundle["features"]
             for source in feature["provenance"]["sources"]}
    assert cited <= set(titles)


# -- coverage, determinism and the size guard --------------------------------

def test_coverage_json_gains_a_maps_section(built: BuildResult) -> None:
    coverage = _json(built, "coverage.json")
    row = coverage["maps"][0]
    assert row["map_id"] == MAP_ID
    assert row["feature_count"] == 4
    assert row["representations"] == {"surveyed": 1, "georeferenced": 1,
                                      "derived": 1, "inferred_direction": 1}
    assert row["unlocated_count"] == 1
    assert row["checks_passed"] == 1 and row["checks_failed"] == 0


def test_coverage_json_lists_facilities_without_a_map(tmp_path: Path) -> None:
    """A facility nobody has drawn is named, not silently absent."""
    import shutil

    root = tmp_path / "atlas"
    shutil.copytree(FIXTURE, root)
    (root / "maps" / "demo-lab.json").unlink()
    for path in (root / "geometry").glob("*.json"):
        path.unlink()
    result = build(root, tmp_path / "out", build_date=BUILD_DATE)
    coverage = json.loads(result.files["coverage.json"])
    assert coverage["maps"] == []
    assert coverage["facilities_without_a_map"] == [
        {"facility_id": "facility:demo-lab", "name": "Demo Laboratory"}]


def test_an_atlas_with_no_maps_still_emits_the_table(tmp_path: Path) -> None:
    """The real tree has no maps yet; the browser must still find the key."""
    import shutil

    root = tmp_path / "atlas"
    shutil.copytree(FIXTURE, root)
    (root / "maps" / "demo-lab.json").unlink()
    for path in (root / "geometry").glob("*.json"):
        path.unlink()
    result = build(root, tmp_path / "out", build_date=BUILD_DATE)
    assert result.errors == []
    assert json.loads(result.files["atlas.json"])["maps"] == {}
    assert not [path for path in result.files if path.startswith("geometry/")]


def test_the_geometry_bundle_is_byte_deterministic(tmp_path: Path) -> None:
    first = build(FIXTURE, tmp_path / "out1", build_date=BUILD_DATE)
    second = build(FIXTURE, tmp_path / "out2", build_date=BUILD_DATE)
    assert first.files[GEOMETRY_BUNDLE] == second.files[GEOMETRY_BUNDLE]


def test_check_mode_sees_no_drift_once_the_geometry_bundle_is_written(tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    build(FIXTURE, out_dir, build_date=BUILD_DATE)
    assert (out_dir / GEOMETRY_BUNDLE).is_file()
    assert build(FIXTURE, out_dir, build_date=BUILD_DATE, check=True).drift == []


def test_a_geometry_bundle_over_two_megabytes_fails_the_build(tmp_path: Path,
                                                              monkeypatch) -> None:
    """The 2 MB guard is what stops a campus shipping a million OSM nodes."""
    import shutil

    from hepgraph.atlas import schema

    root = tmp_path / "atlas"
    shutil.copytree(FIXTURE, root)
    monkeypatch.setattr(schema, "GEOMETRY_BUNDLE_MAX_BYTES", 4096)
    result = build(root, tmp_path / "out", build_date=BUILD_DATE)
    assert any("over the 4096 byte limit" in error for error in result.errors), result.errors
    assert any(GEOMETRY_BUNDLE in error for error in result.errors)


def test_linked_maps_agree_between_the_table_and_the_bundle(tmp_path: Path) -> None:
    """A facility with two campus maps must not get two different answers.

    `linked_map_ids` is derived twice — once for `atlas.json.maps` and once
    for the per-map bundle — and a facility with more than one map is exactly
    where a first-wins and a last-wins index would disagree.
    """
    import shutil

    root = tmp_path / "atlas"
    shutil.copytree(FIXTURE, root)

    # A second map of the same facility, covering no site of its own, and a
    # far-site map so there is something real to link to.
    annex = json.loads((root / "maps" / "demo-lab.json").read_text(encoding="utf-8"))
    annex["id"] = "map:demo-lab-annex"
    annex["name"] = "Demo Laboratory — annex campus"
    annex["site_ids"] = []
    annex["unlocated"] = []
    (root / "maps" / "demo-lab-annex.json").write_text(json.dumps(annex), encoding="utf-8")

    far = json.loads((root / "maps" / "demo-lab.json").read_text(encoding="utf-8"))
    far["id"] = "map:demo-far"
    far["name"] = "Demo far detector campus"
    far["facility_id"] = "facility:demo-lab"
    far["site_ids"] = ["site:demo-far-cavern"]
    far["unlocated"] = []
    far["center"] = dict(far["center"], lat=44.352, lon=-103.751)
    (root / "maps" / "demo-far.json").write_text(json.dumps(far), encoding="utf-8")

    result = build(root, tmp_path / "out", build_date=BUILD_DATE)
    table = json.loads(result.files["atlas.json"])["maps"]
    for map_id, entry in table.items():
        bundle = json.loads(result.files[entry["bundle"]])
        assert bundle["map"]["linked_map_ids"] == entry["linked_map_ids"], map_id

    # The beamline's far site is on map:demo-far, so the campus map links to it.
    assert "map:demo-far" in table["map:demo-lab"]["linked_map_ids"]
    # A map never links to itself.
    for map_id, entry in table.items():
        assert map_id not in entry["linked_map_ids"]
