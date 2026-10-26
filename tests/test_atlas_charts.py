"""Unit checks for the two Atlas charts, "Going underground" and "The energy frontier"
(static/atlas/js/views/).

Kept to the two things a browser cannot see: the unit conversions (the views copy the
schema's scale, and a copy that drifts would plot a wrong number without any error) and the
ticks of a logarithmic axis. Everything else is checked in tests/browser_atlas.cjs.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from hepgraph.atlas.schema import UNIT_SCALE

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "atlas"
VIEWS = ROOT / "static" / "atlas" / "js" / "views"
NODE = shutil.which("node")

NODE_SCRIPT = r"""
import fs from 'node:fs';
const dir = process.argv[1];
const atlas = JSON.parse(fs.readFileSync(0, 'utf8'));
const ug = await import(`${dir}/underground-rows.js`);
const fr = await import(`${dir}/frontier-rows.js`);
const chart = await import(`${dir}/chart.js`);
const out = {
  fluxScale: ug.MUON_FLUX_SCALE,
  energyScaleEv: fr.ENERGY_SCALE_EV,
  flux: Object.fromEntries(ug.undergroundRows(atlas).map((r) => [r.id, r.flux])),
  depthOnly: ug.depthOnlyRows(atlas).map((r) => r.id),
  energyGeV: Object.fromEntries(fr.frontierRows(atlas).map((r) => [r.id, r.energy.gev])),
  ticks: chart.logTicks(1e-10, 1e-6).major.map((t) => [t.value, t.label]),
  ticksOffDecade: chart.logTicks(3e-10, 5e-7).major.map((t) => t.label),
  minor: chart.logTicks(1e-3, 1e-1).minor.length,
  superscript: chart.superscript(-10),
};
console.log(JSON.stringify(out));
"""


@pytest.fixture(scope="module")
def result() -> dict:
    """The browser modules run under Node on atlas.json as built from data/atlas (nothing is written)."""
    if NODE is None:
        pytest.skip("node is not installed")
    from hepgraph.atlas.build import build

    built = build(DATA, ROOT / "static" / "atlas" / "generated", check=True)
    atlas = built.files["atlas.json"]
    run = subprocess.run(
        [NODE, "--input-type=module", "-e", NODE_SCRIPT, str(VIEWS)],
        input=atlas if isinstance(atlas, str) else atlas.decode("utf-8"),
        capture_output=True, text=True, check=True, timeout=60,
    )
    return json.loads(run.stdout)


def _sites() -> dict[str, dict]:
    return {rec["id"]: rec for rec in (json.loads(p.read_text(encoding="utf-8")) for p in (DATA / "sites").glob("*.json"))}


def test_the_copied_unit_scales_equal_the_schema(result: dict) -> None:
    """The views copy UNIT_SCALE (they cannot import Python); the copy must not drift."""
    for unit, factor in UNIT_SCALE["muon_flux"].items():
        assert result["fluxScale"][unit] == pytest.approx(factor, rel=1e-12), unit
    assert set(result["fluxScale"]) == set(UNIT_SCALE["muon_flux"])
    assert set(result["energyScaleEv"]) == set(UNIT_SCALE["energy"])
    for unit, factor in UNIT_SCALE["energy"].items():
        assert result["energyScaleEv"][unit] == pytest.approx(factor, rel=1e-12), unit


def test_every_flux_is_converted_to_cm2_per_s_with_the_a27_scale(result: dict) -> None:
    sites = _sites()
    expected = {
        sid: s["muon_flux"]["value"] * UNIT_SCALE["muon_flux"][s["muon_flux"]["unit"]]
        for sid, s in sites.items() if s.get("muon_flux") and s.get("depth_mwe")
    }
    assert sorted(result["flux"]) == sorted(expected) and len(expected) == 15
    for sid, value in expected.items():
        assert result["flux"][sid] == pytest.approx(value, rel=1e-12), sid
    # Three units are in use: LSM's 5.4 per m^2 per day is 6.25e-9 per cm^2 per s, LNGS Hall C's 3.432e-4 per m^2 per s is 3.432e-8.
    assert result["flux"]["site:lsm-frejus"] == pytest.approx(6.25e-9, rel=1e-3)
    assert result["flux"]["site:lngs-hall-c"] == pytest.approx(3.432e-8, rel=1e-9)
    # A site with a depth in m.w.e. and no flux is listed as "depth known, flux not recorded", not plotted.
    assert "site:surf-4850-level-dune-far-detector" in result["depthOnly"]
    assert "site:lngs-hall-c" not in result["depthOnly"]


def test_energies_are_converted_to_gev(result: dict) -> None:
    gev = result["energyGeV"]
    assert gev["accelerator:fermilab-linac"] == pytest.approx(0.4)  # 400 MeV
    assert gev["accelerator:sps"] == pytest.approx(450)
    assert gev["accelerator:lhc"] == pytest.approx(13600)  # Run 3, 13.6 TeV, not the 14 TeV design value


def test_log_axis_ticks_are_decades_with_superscripts(result: dict) -> None:
    assert result["ticks"] == [
        [1e-10, "10⁻¹⁰"], [1e-9, "10⁻⁹"], [1e-8, "10⁻⁸"], [1e-7, "10⁻⁷"], [1e-6, "10⁻⁶"],
    ]
    assert result["ticksOffDecade"] == ["10⁻⁹", "10⁻⁸", "10⁻⁷"]  # only decades inside the domain
    assert result["minor"] == 8 * 2  # 2..9 times 10^-3 and 10^-2
    assert result["superscript"] == "⁻¹⁰"


def test_the_views_are_registered_and_loaded_only_when_asked() -> None:
    registry = (VIEWS / "registry.js").read_text(encoding="utf-8")
    assert "load: () => import('./underground.js')" in registry
    assert "load: () => import('./energy-frontier.js')" in registry
    for path in (ROOT / "static/atlas/js").rglob("*.js"):
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"^import .* from '[^']*(chart|underground|energy-frontier)\.js'", text, re.M) or path.parent == VIEWS, path.name
