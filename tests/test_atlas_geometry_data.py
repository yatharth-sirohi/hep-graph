"""The real `data/atlas/` local maps must validate and measure up (A25).

Everything else in the atlas test suite runs against `tests/fixtures/`, which
is exactly what `docs/atlas-worklog/` records as having hidden real defects
behind a green suite before: a fixture proves the code works, not that the
data is true.  This module therefore runs against the committed tree itself.

It skips with a message while `data/atlas/maps/` is empty — which it is until
the research agents land the first campus — and starts enforcing the moment a
map appears.  A skip that says why is honest; a passing test over no data
would be a claim that the maps are correct when there are none.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hepgraph.atlas import geo, schema, validate as v
from hepgraph.atlas.load import DATA_DIR, load_atlas

MAPS_DIR = DATA_DIR / "maps"
GEOMETRY_DIR = DATA_DIR / "geometry"


def _map_files() -> list[Path]:
    return sorted(MAPS_DIR.glob("*.json")) if MAPS_DIR.is_dir() else []


def _geometry_files() -> list[Path]:
    return sorted(GEOMETRY_DIR.glob("*.json")) if GEOMETRY_DIR.is_dir() else []


requires_maps = pytest.mark.skipif(
    not _map_files(),
    reason="data/atlas/maps/ is empty: no campus has been researched yet "
           "(docs/HEP_ATLAS_GEOMETRY.md §5). These checks start enforcing with the first map.")


@pytest.fixture(scope="module")
def atlas():
    return load_atlas(DATA_DIR)


@pytest.fixture(scope="module")
def findings(atlas):
    return v.validate_atlas(atlas)


# ---------------------------------------------------------------------------
# The rule that holds whether or not any map exists yet
# ---------------------------------------------------------------------------

def test_the_real_tree_has_no_geometry_errors(findings) -> None:
    """A25 rules must report zero errors on the committed data, always.

    This one does not skip: an empty maps directory should produce no geometry
    findings at all, and a geometry record committed without its map is a
    defect the moment it lands.
    """
    geometry_rules = {finding.rule for finding in v.errors(findings)
                      if finding.rule.startswith(("geometry-", "map-", "ring-"))}
    offenders = [str(finding) for finding in v.errors(findings)
                 if finding.rule.startswith(("geometry-", "map-", "ring-"))]
    assert not geometry_rules, offenders


def test_a_geometry_record_never_ships_without_its_map(atlas) -> None:
    for entity_id, record in sorted(atlas.by_type("geometry").items()):
        map_id = record.get("map_id")
        assert atlas.get(map_id) is not None, \
            f"{entity_id} names {map_id!r}, which is not in data/atlas/maps/"


# ---------------------------------------------------------------------------
# Enforced from the first committed map onwards
# ---------------------------------------------------------------------------

@requires_maps
def test_every_map_validates_with_zero_errors(atlas, findings) -> None:
    map_ids = set(atlas.by_type("map"))
    geometry_ids = set(atlas.by_type("geometry"))
    offenders = [str(finding) for finding in v.errors(findings)
                 if finding.entity_id in map_ids | geometry_ids]
    assert offenders == [], offenders


@requires_maps
def test_every_geometry_check_passes(atlas) -> None:
    """Every authored cross-check is executed here, against the real shapes.

    A check that cannot be executed counts as a failure: a row the validator
    cannot answer is not evidence of anything, and the whole point of the
    layer is that a drawn shape agrees with an independently published figure.
    """
    by_id = atlas.by_type("geometry")
    failures: list[str] = []
    executed = 0
    for entity_id, record in sorted(by_id.items()):
        sourced = record.get("geometry") or {}
        value = sourced.get("value") if isinstance(sourced, dict) else None
        for index, row in enumerate(record.get("checks") or []):
            if not isinstance(row, dict):
                continue
            other = None
            if row.get("kind") == "distance":
                target = by_id.get(schema.canonical_id(row.get("to_geometry_id")) or "")
                other = (target or {}).get("geometry", {}).get("value") if target else None
            result = geo.evaluate_check(value, row, other)
            executed += 1
            if result["passed"] is not True:
                failures.append(f"{entity_id}/checks/{index}: "
                                f"{result['reason'] or geo.format_check(result)}")
    assert failures == [], failures
    assert executed, "maps exist but not one shape carries an executable cross-check"


@requires_maps
def test_every_map_record_is_canonical_json_and_matches_its_filename() -> None:
    from hepgraph.atlas.load import dump_json

    for path in _map_files() + _geometry_files():
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert path.read_text(encoding="utf-8") == dump_json(payload), \
            f"{path.name} is not canonical JSON (A11)"
        assert path.stem == schema.filename_for(payload["id"]), path


@requires_maps
def test_every_openstreetmap_shape_carries_its_odbl_attribution(atlas) -> None:
    """§7: OSM data may be used, and must be credited wherever it is drawn."""
    for entity_id, record in sorted(atlas.by_type("geometry").items()):
        osm = record.get("osm")
        if not isinstance(osm, dict) or not (osm.get("elements") or []):
            continue
        licence = record.get("license") or {}
        assert licence.get("name") == schema.ODBL_LICENSE_NAME, entity_id
        assert schema.OSM_ATTRIBUTION in str(licence.get("attribution") or ""), entity_id


@requires_maps
def test_the_geometry_licence_note_exists() -> None:
    """§7: the ODbL statement covering the OSM-derived records."""
    assert (GEOMETRY_DIR / "LICENSE.md").is_file()


@requires_maps
def test_every_map_builds_a_bundle_inside_the_size_budget() -> None:
    import datetime as dt
    import tempfile

    from hepgraph.atlas.build import build

    with tempfile.TemporaryDirectory() as out_dir:
        result = build(DATA_DIR, out_dir, build_date=dt.date.today(), check=True)
    assert result.errors == [], result.errors
    bundles = [path for path in result.files if path.startswith("geometry/")]
    assert len(bundles) == len(_map_files())
