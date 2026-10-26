"""Unit checks for "Beam through the Earth" (static/atlas/js/views/).

The view computes a cross-section of the Earth along each sourced baseline: the
dip below the horizontal at the source, the deepest point of the chord, the
chord, the surface distance and the light travel time, on a spherical Earth of
R = 6371.0 km. Three things are checked here, none of which needs a browser:

  * an independent Python implementation of the formulas gives the values the
    brief states (DUNE 5.8 deg and ~32 km; NuMI to Soudan 3.3 deg and 10.6 km;
    T2K 1.33 deg and 1.7 km) from the canonical records in data/atlas;
  * the browser modules, run under Node on the same records, agree with it to
    six figures (skipped when Node is not installed);
  * the route, the registry and the stylesheet are wired once, and the view's
    module is only ever imported dynamically (nothing loads until asked).
"""
from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "atlas"
VIEWS = ROOT / "static" / "atlas" / "js" / "views"

R_KM = 6371.0
C0_KM_S = 299_792.458


def reference(a: tuple[float, float], b: tuple[float, float]) -> dict[str, float]:
    """The five numbers, written out from the formulas in the brief."""
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    d_lat, d_lon = p2 - p1, math.radians(b[1] - a[1])
    h = math.sin(d_lat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(d_lon / 2) ** 2
    sigma = 2 * math.asin(math.sqrt(h))
    chord = 2 * R_KM * math.sin(sigma / 2)
    return {
        "surface_km": R_KM * sigma,
        "chord_km": chord,
        "dip_deg": math.degrees(sigma / 2),
        "sagitta_km": R_KM * (1 - math.cos(sigma / 2)),
        "light_ms": chord / C0_KM_S * 1000,
    }


def _records(folder: str) -> dict[str, dict]:
    out = {}
    for path in sorted((DATA / folder).glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        out[record["id"]] = record
    return out


def _rows() -> list[dict]:
    sites = _records("sites")
    rows = []
    for beamline in _records("beamlines").values():
        for index, baseline in enumerate(beamline.get("baselines") or []):
            a, b = sites[baseline["from_site_id"]], sites[baseline["to_site_id"]]
            rows.append({
                "beamline": beamline["id"],
                "index": index,
                "arg": beamline["id"].split(":")[1] + (f"~{index}" if index else ""),
                "sourced_km": baseline["distance"]["value"],
                "numbers": reference(
                    (a["coordinates"]["lat"], a["coordinates"]["lon"]),
                    (b["coordinates"]["lat"], b["coordinates"]["lon"]),
                ),
            })
    return rows


def _by_arg() -> dict[str, dict]:
    return {row["arg"]: row["numbers"] for row in _rows()}


def test_there_are_seven_baselines() -> None:
    assert sorted(row["arg"] for row in _rows()) == [
        "cngs", "j-parc-neutrino", "j-parc-neutrino~1", "kek-neutrino", "lbnf", "numi", "numi~1",
    ]


def test_the_briefs_check_values_hold() -> None:
    rows = _by_arg()
    dune = rows["lbnf"]
    assert dune["dip_deg"] == pytest.approx(5.8, abs=0.05)
    assert dune["sagitta_km"] == pytest.approx(32, abs=0.7)
    numi = rows["numi"]
    assert numi["dip_deg"] == pytest.approx(3.3, abs=0.05)
    assert numi["sagitta_km"] == pytest.approx(10.6, abs=0.1)
    t2k = rows["j-parc-neutrino"]
    assert t2k["dip_deg"] == pytest.approx(1.33, abs=0.02)
    assert t2k["sagitta_km"] == pytest.approx(1.7, abs=0.1)


def test_the_computed_chord_agrees_with_every_sourced_baseline() -> None:
    """A baseline is a straight-line distance, so it is the chord that must agree (within 0.5 %)."""
    for row in _rows():
        assert row["numbers"]["chord_km"] == pytest.approx(row["sourced_km"], rel=0.005), row["arg"]


def test_the_formulas_are_self_consistent() -> None:
    for arg, n in _by_arg().items():
        # s = R * 2 * dip and c = 2R sin(dip) tie the five numbers together.
        assert n["surface_km"] == pytest.approx(R_KM * math.radians(2 * n["dip_deg"]), rel=1e-12), arg
        assert n["chord_km"] == pytest.approx(2 * R_KM * math.sin(math.radians(n["dip_deg"])), rel=1e-12), arg
        assert n["chord_km"] < n["surface_km"], arg


NODE = shutil.which("node")

NODE_SCRIPT = r"""
import fs from 'node:fs';
const dir = process.argv[1];
const atlas = JSON.parse(fs.readFileSync(0, 'utf8'));
const rows = await import(`${dir}/beam-rows.js`);
const geometry = await import(`${dir}/beam-geometry.js`);
const out = { rows: {}, entries: rows.beamSearchEntries(atlas).map((e) => [e.id, e.name, e.aliases]) };
for (const row of rows.beamRows(atlas)) {
  const { geometry: g } = rows.rowGeometry(row);
  out.rows[row.arg] = {
    surface_km: g.surfaceKm, chord_km: g.chordKm, dip_deg: g.dipDeg, sagitta_km: g.sagittaKm, light_ms: g.lightMs,
    exaggeration: geometry.chooseExaggeration(g.chordKm, g.sagittaKm, Math.max(0, ...[row.from, row.to].map((s) => (s.depth ? s.depth.km : 0)))),
    status: rows.beamStatusAt(row, { year: 2026 }).status,
    offAxis: rows.offAxisFor(atlas, row).map((c) => `${c.experiment.id}:${c.quantity.display}`),
  };
}
out.parse = [rows.parseArg('numi~1'), rows.parseArg('lbnf'), rows.parseArg('x~y'), rows.parseArg('')];
console.log(JSON.stringify(out));
"""


@pytest.fixture(scope="module")
def built_atlas() -> dict:
    """atlas.json as the browser receives it, built in memory from data/atlas (nothing is written)."""
    from hepgraph.atlas.build import build

    result = build(DATA, ROOT / "static" / "atlas" / "generated", check=True)
    return json.loads(result.files["atlas.json"])


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_the_browser_modules_agree_with_the_python_reference(built_atlas: dict) -> None:
    atlas = built_atlas
    result = subprocess.run(
        [NODE, "--input-type=module", "-e", NODE_SCRIPT, str(VIEWS)],
        input=json.dumps(atlas), capture_output=True, text=True, check=True, timeout=60,
    )
    out = json.loads(result.stdout)
    expected = _by_arg()
    assert sorted(out["rows"]) == sorted(expected)
    for arg, numbers in expected.items():
        for key, value in numbers.items():
            assert out["rows"][arg][key] == pytest.approx(value, rel=1e-9), (arg, key)
    # The stretch the figure states, the status it is drawn in, the sourced off-axis angles.
    assert {arg: row["exaggeration"] for arg, row in out["rows"].items()}["lbnf"] == 20
    assert out["rows"]["j-parc-neutrino~1"]["status"] == "construction"
    assert out["rows"]["lbnf"]["status"] == "construction"
    assert out["rows"]["j-parc-neutrino"]["status"] == "active"
    assert out["rows"]["numi~1"]["offAxis"] == ["experiment:nova:14.6 mrad"]
    assert out["rows"]["numi"]["offAxis"] == []  # MINOS sits on axis: no angle is drawn for it
    assert out["rows"]["j-parc-neutrino~1"]["offAxis"] == ["experiment:hyper-kamiokande:2.5°"]
    # Search: "beam through the earth" and "DUNE beam" can reach the view.
    by_id = {entry[0]: entry for entry in out["entries"]}
    assert len(by_id) == 7
    lbnf = by_id["view:beam-section/lbnf"]
    assert lbnf[1].startswith("Beam through the Earth")
    assert "DUNE beam" in lbnf[2]
    # The route argument: a slug, optionally ~<row>.
    assert out["parse"] == [{"slug": "numi", "index": 1}, {"slug": "lbnf", "index": 0}, None, None]


# ---------------------------------------------------------------------------
# Wiring
# ---------------------------------------------------------------------------
def test_the_view_route_and_registry_are_wired() -> None:
    state = (ROOT / "static/atlas/js/state.js").read_text(encoding="utf-8")
    assert re.search(r"\bview:\s*'view'", state)
    registry = (VIEWS / "registry.js").read_text(encoding="utf-8")
    assert "load: () => import('./beam-section.js')" in registry
    # Nothing loads until asked: no module imports the view statically.
    for path in (ROOT / "static/atlas/js").rglob("*.js"):
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"^import .* from '[^']*beam-section\.js'", text, re.M), path.name


def test_views_css_is_linked_once() -> None:
    html = (ROOT / "static/atlas/index.html").read_text(encoding="utf-8")
    assert html.count('href="/atlas/views.css"') == 1
    assert html.index("/atlas/globe.css") < html.index("/atlas/views.css") < html.index("/atlas/phone.css")
