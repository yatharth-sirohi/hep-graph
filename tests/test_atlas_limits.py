"""Unit check for the published limit curves (A29): the loader and the validator.

Each file under data/atlas/limits/ is a HEPData table (or a labelled published minimum). The
validator is the guard that a plotted point is a finite positive number in the units the plot
declares; these checks keep to that bare minimum, plus the one table the browser modules use to
decide which panel links to the plot, which must agree with the data.
"""
from __future__ import annotations

import copy
import datetime as dt
import re
from pathlib import Path

import pytest

from hepgraph.atlas import load, validate

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "atlas"


@pytest.fixture(scope="module")
def atlas():
    loaded = load.load_atlas(DATA)
    assert not loaded.problems
    return loaded


def _findings(atlas, mutate=None, slug="lz-2024-si-wimp-nucleon"):
    original = atlas.limits[slug]
    try:
        if mutate is not None:
            atlas.limits[slug] = copy.deepcopy(original)
            mutate(atlas.limits[slug])
        ctx = validate._Context(atlas=atlas, build_date=dt.date(2026, 10, 26), raw=validate._RawIndex(), selection="2026-10")
        return [f for f in validate.check_limits(ctx)]
    finally:
        atlas.limits[slug] = original


def test_the_shipped_curves_load_and_validate(atlas):
    assert sorted(atlas.limits) == [
        "lz-2022-si-wimp-nucleon", "lz-2024-si-wimp-nucleon", "pandax-4t-2021-si-minimum", "xenonnt-2023-si-minimum",
    ]
    assert _findings(atlas) == []
    for slug in ("lz-2022-si-wimp-nucleon", "lz-2024-si-wimp-nucleon", "xenonnt-2023-si-minimum", "pandax-4t-2021-si-minimum"):
        assert _findings(atlas, None, slug) == []


@pytest.mark.parametrize("name,mutate,rule", [
    ("a NaN", lambda c: c["points"].__setitem__(3, [float("nan"), 1e-47]), "limit-points"),
    ("a zero (log axis)", lambda c: c["points"].__setitem__(3, [c["points"][3][0], 0]), "limit-points"),
    ("a string", lambda c: c["points"].__setitem__(3, ["46", 1e-47]), "limit-points"),
    ("the wrong y unit", lambda c: c["columns"]["y"].__setitem__("unit", "pb"), "limit-units"),
    ("the wrong x unit", lambda c: c["columns"]["x"].__setitem__("unit", "TeV/c^2"), "limit-units"),
    ("an unsorted curve", lambda c: c["points"].reverse(), "limit-points-order"),
    ("a units check that no longer matches", lambda c: c["units_check"].__setitem__("value", 9.9e-48), "limit-units-check"),
    ("a missing HEPData record", lambda c: c.__setitem__("hepdata", None), "limit-hepdata"),
    ("a row count that disagrees without thinning", lambda c: c["hepdata"].__setitem__("rows", 999), "limit-thinned"),
])
def test_the_validator_refuses_a_bad_curve(atlas, name, mutate, rule):
    rules = {f.rule for f in _findings(atlas, mutate)}
    assert rule in rules, f"{name}: expected {rule}, got {sorted(rules)}"


def test_the_validator_refuses_a_marker_whose_quote_lacks_its_value(atlas):
    rules = {f.rule for f in _findings(atlas, lambda c: c.__setitem__("value_as_written", "9.9e-99 cm^2"), "pandax-4t-2021-si-minimum")}
    assert "limit-marker-quote" in rules


def test_the_panel_link_table_agrees_with_the_data(atlas):
    """limits-rows.js says which records link to the plot without loading it; it must match the files."""
    source = (ROOT / "static" / "atlas" / "js" / "views" / "limits-rows.js").read_text(encoding="utf-8")
    listed = {
        key: set(re.findall(r"'((?:experiment|result|topic):[a-z0-9-]+)'", re.search(rf"{key}: \[(.*?)\]", source, re.S).group(1)))
        for key in ("topics", "experiments", "results")
    }
    experiments = {c["experiment_id"] for c in atlas.limits.values()}
    results = {c["result_id"] for c in atlas.limits.values() if c["result_id"]}
    assert listed["experiments"] == experiments
    assert listed["results"] == results
    assert all(atlas.get(topic) for topic in listed["topics"])
