"""Unit checks for the scale comparisons (static/atlas/js/views/scale-*.js), kept to the minimum.

  * "Compare with…" lays one facility's footprint over another place by moving every
    vertex by its (distance, bearing) from the footprint's centre. The check that matters
    is that this keeps true size: the LHC ring, moved over Iowa City, a Svalbard glacier
    and the South Pole, keeps its circumference to within 0.5 % (it is in fact exact to
    about 1e-8), measured here by the independent geometry code the validator uses.
  * The detector line-up reads every size from a sourced `specs` value. Each dimension the
    roster names must exist in its record as a length with a verbatim quote and a source.

Both run the browser modules under Node (skipped when Node is not installed).
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from hepgraph.atlas import geo

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "atlas"
VIEWS = ROOT / "static" / "atlas" / "js" / "views"
NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(NODE is None, reason="node is not installed")

# Where the LHC is laid in the check: a mid-latitude city, a high-latitude point and the pole
# (whose map is drawn in a polar projection, with its own grid north).
TARGETS = [
    ("Iowa City", 41.6611, -91.5302, False),
    ("Svalbard", 78.2, 15.6, False),
    ("South Pole", -89.9944, -62.6, True),
]

TRANSLATE = r"""
import fs from 'node:fs';
const dir = process.argv[1];
const { translator, boundsCentre, vertices } = await import(`${dir}/scale-geometry.js`);
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const centre = boundsCentre(vertices({ type: 'LineString', coordinates: input.coordinates }));
const out = {};
for (const [name, lat, lon, polar] of input.targets) {
  const move = translator({ lat: centre.lat, lon: centre.lon, polar: false }, { lat, lon, polar });
  out[name] = input.coordinates.map(move);
}
console.log(JSON.stringify(out));
"""

ROSTER = r"""
const { ROSTER, ICECUBE } = await import(`${process.argv[1]}/scale-detectors.js`);
console.log(JSON.stringify({ roster: ROSTER, icecube: ICECUBE }));
"""


def _node(script: str, *args: str, stdin: str = "") -> dict:
    result = subprocess.run(
        [NODE, "--no-warnings", "--input-type=module", "-e", script, *args],
        input=stdin, capture_output=True, text=True, check=True, timeout=60,
    )
    return json.loads(result.stdout)


def test_the_overlay_keeps_the_lhc_ring_its_true_size() -> None:
    record = json.loads((DATA / "geometry" / "lhc-tunnel-ring.json").read_text(encoding="utf-8"))
    coordinates = record["geometry"]["value"]["coordinates"]
    original = geo.line_length_m(coordinates)
    # The record's own circumference is the LHC's 26.7 km (the official 26 659 m, to its 2 % check).
    assert original == pytest.approx(26_659, rel=0.01)
    moved = _node(
        TRANSLATE, str(VIEWS),
        stdin=json.dumps({"coordinates": coordinates, "targets": [list(t) for t in TARGETS]}),
    )
    assert set(moved) == {name for name, *_ in TARGETS}
    for name, ring in moved.items():
        length = geo.line_length_m(ring)
        assert length == pytest.approx(original, rel=0.005), name


def test_every_lineup_dimension_is_a_sourced_length_in_its_record() -> None:
    table = _node(ROSTER, str(VIEWS))
    roster = table["roster"]
    assert len(roster) >= 12
    needs: list[tuple[str, str]] = []
    for entry in roster:
        needs += [(entry["id"], entry["width"]), (entry["id"], entry["height"])]
        if entry.get("inner"):
            needs += [(entry["id"], entry["inner"]["width"]), (entry["id"], entry["inner"]["height"])]
    ice = table["icecube"]
    needs += [(ice["id"], ice[key]) for key in ("depthMin", "depthMax", "volume", "spacing")]
    for detector_id, key in needs:
        record = json.loads((DATA / "detectors" / f"{detector_id.split(':')[1]}.json").read_text(encoding="utf-8"))
        spec = (record.get("specs") or {}).get(key)
        assert spec, f"{detector_id} has no specs.{key}"
        assert spec["dimension"] in ("length", "volume"), f"{detector_id} specs.{key}"
        assert spec["sources"] and spec["quote"], f"{detector_id} specs.{key} is not quoted from a source"
