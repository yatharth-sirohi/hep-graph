"""Historical state assertions over the *built* atlas bundle (A13, §60).

A13 is explicit that history tests assert the **derived state**, not mere
presence:

    state_at(id, "1990") -> None | {"status", "certainty"}

and that the slider, range mode, playback and these tests all read the same
precomputed `state_segments` from `atlas.json` — never the raw interval
lists.  So this module builds the bundle and reads it back exactly as the
browser would, which is what makes it a regression test of the pipeline and
not of `schema.state_at`.

`PILOT_CASES` below is the **placeholder for the pilot assertions**.  It is
empty until the pilot experiments (ATLAS, Belle, ALEPH, DUNE, …) are
researched into `data/atlas/`; the A13 examples are written out in
`A13_EXAMPLES` as the shape those rows will take.  Filling `PILOT_CASES` in
is the only edit this file needs when the pilot data lands.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import pytest

from hepgraph.atlas import schema
from hepgraph.atlas.build import build
from hepgraph.atlas.load import DATA_DIR

FIXTURE = Path(__file__).parent / "fixtures" / "atlas_minimal"
BUILD_DATE = dt.date(2026, 9, 16)

# Every top-level key of atlas.json that holds timeline-bearing entities.
TIMELINE_COLLECTIONS = ("facilities", "sites", "accelerators", "beamlines",
                        "experiments", "detectors", "collaborations")


# ---------------------------------------------------------------------------
# Reading the built bundle the way the globe does
# ---------------------------------------------------------------------------

def load_bundle(data_dir: Path, out_dir: Path, *, build_date: dt.date = BUILD_DATE) -> dict:
    """Build `data_dir` into `out_dir` and return the parsed `atlas.json`."""
    result = build(data_dir, out_dir, build_date=build_date)
    assert not result.errors, result.errors
    return json.loads((out_dir / "atlas.json").read_text(encoding="utf-8"))


def find_record(bundle: dict, entity_id: str) -> dict | None:
    """The record for `entity_id` in a parsed `atlas.json`, or None."""
    for collection in TIMELINE_COLLECTIONS + ("topics",):
        table = bundle.get(collection)
        if isinstance(table, dict) and entity_id in table:
            return table[entity_id]
    return None


def state_at(bundle: dict, entity_id: str, selection: str) -> dict | None:
    """A13: the derived state of `entity_id` at `"YYYY"` or `"YYYY-MM"`.

    Reads only `state_segments` from the bundle, so it exercises exactly what
    the frontend will.  Returns None when the entity is absent in that window,
    otherwise `{"status", "certainty", "secondary"}` — a superset of the A13
    contract, which names `status` and `certainty`.
    """
    record = find_record(bundle, entity_id)
    if record is None:
        return None
    segments = record.get("state_segments") or []
    low, high = schema.selection_bounds(selection)
    verdict = schema.range_state(segments, schema.month_index(low), schema.month_index(high))
    if verdict is None:
        return None
    return {"status": verdict["status"], "certainty": verdict["certainty"],
            "secondary": verdict["secondary"]}


@pytest.fixture(scope="module")
def fixture_bundle(tmp_path_factory) -> dict:
    return load_bundle(FIXTURE, tmp_path_factory.mktemp("atlas-history"))


# ---------------------------------------------------------------------------
# The contract itself, exercised on the fixture dataset
# ---------------------------------------------------------------------------

def test_state_at_returns_none_before_an_entity_exists(fixture_bundle) -> None:
    assert state_at(fixture_bundle, "experiment:demo", "2004") is None
    assert state_at(fixture_bundle, "experiment:demo", "1990") is None


def test_state_at_returns_a_status_and_a_certainty(fixture_bundle) -> None:
    for year, expected in [("2006", "proposed"), ("2009", "construction"),
                           ("2012", "active"), ("2016", "shutdown"), ("2020", "active")]:
        state = state_at(fixture_bundle, "experiment:demo", year)
        assert state is not None, year
        assert state["status"] == expected, year
        assert state["certainty"] in schema.CERTAINTIES


def test_state_at_never_reports_active_after_the_build_date(fixture_bundle) -> None:
    """A3: an open interval is "assumed ongoing" past the build date, not active."""
    assert state_at(fixture_bundle, "experiment:demo", "2026") is not None
    assert state_at(fixture_bundle, "experiment:demo", "2027") is None
    assert state_at(fixture_bundle, "experiment:demo", "2030") is None


def test_month_resolution_agrees_with_year_resolution(fixture_bundle) -> None:
    assert state_at(fixture_bundle, "experiment:demo", "2016-06")["status"] == "shutdown"
    assert state_at(fixture_bundle, "experiment:demo", "2009-03")["status"] == "construction"


def test_state_segments_drive_the_answer_not_the_interval_list(fixture_bundle) -> None:
    """A13: the tests must read the same precomputed segments as the slider."""
    record = find_record(fixture_bundle, "experiment:demo")
    assert record is not None
    assert record["state_segments"], "atlas.json must precompute state_segments"
    stripped = dict(record)
    stripped.pop("intervals", None)
    assert stripped["state_segments"] == record["state_segments"]
    # Months are indices from the manifest epoch, not years.
    for segment in record["state_segments"]:
        assert isinstance(segment[0], int) and isinstance(segment[1], int)
        assert segment[0] <= segment[1]
        assert segment[2] in schema.STATUSES or segment[2] == schema.UNRECORDED
        assert segment[3] in schema.CERTAINTIES


def test_every_timeline_entity_in_the_bundle_carries_segments(fixture_bundle) -> None:
    seen = 0
    for collection in TIMELINE_COLLECTIONS:
        for entity_id, record in (fixture_bundle.get(collection) or {}).items():
            if not record.get("intervals"):
                continue
            seen += 1
            assert record.get("state_segments"), f"{entity_id} has intervals but no segments"
            state = state_at(fixture_bundle, entity_id, "2026-09")
            assert state is not None and state["status"] == record["status"], entity_id
    assert seen >= 6, "the fixture should exercise several entity types"


def test_derived_status_matches_the_build_date_state(fixture_bundle) -> None:
    """A10: the authored `status` equals the derived state at the build date."""
    selection = f"{BUILD_DATE.year:04d}-{BUILD_DATE.month:02d}"
    for collection in TIMELINE_COLLECTIONS:
        for entity_id, record in (fixture_bundle.get(collection) or {}).items():
            if not record.get("state_segments"):
                continue
            state = state_at(fixture_bundle, entity_id, selection)
            assert state is not None and state["status"] == record["status"], entity_id


# ---------------------------------------------------------------------------
# Pilot assertions (A13) -- PLACEHOLDER
# ---------------------------------------------------------------------------

# The worked examples from A13, kept verbatim so the shape of a pilot row is
# unambiguous.  `expected` is either None, an exact status string, a set of
# acceptable statuses, or a ("not", {statuses}) pair for a negative assertion.
A13_EXAMPLES: tuple[tuple[str, str, object], ...] = (
    ("experiment:atlas", "1990", None),
    ("experiment:atlas", "1994", {"proposed", "approved"}),
    ("experiment:belle", "1997", ("not", {"active", "commissioning"})),
    ("experiment:aleph", "2001", None),
    ("experiment:dune", "2026", "construction"),
)

# PLACEHOLDER: empty until the pilot experiments are researched into
# data/atlas/.  Copy rows out of A13_EXAMPLES as each one lands.
PILOT_CASES: tuple[tuple[str, str, object], ...] = ()


def assert_pilot_state(bundle: dict, entity_id: str, selection: str, expected: object) -> None:
    """Assert one A13 row against the built bundle."""
    state = state_at(bundle, entity_id, selection)
    if expected is None:
        assert state is None, f"{entity_id} at {selection}: expected absent, got {state}"
        return
    assert state is not None, f"{entity_id} at {selection}: expected a state, got None"
    status = state["status"]
    if isinstance(expected, tuple) and expected and expected[0] == "not":
        assert status not in expected[1], f"{entity_id} at {selection}: {status} is excluded"
    elif isinstance(expected, (set, frozenset)):
        assert status in expected, f"{entity_id} at {selection}: {status} not in {sorted(expected)}"
    else:
        assert status == expected, f"{entity_id} at {selection}: {status} != {expected}"


@pytest.mark.skipif(not PILOT_CASES,
                    reason="A13 pilot history assertions are pending: the pilot experiments "
                           "are not in data/atlas/ yet. Fill PILOT_CASES from A13_EXAMPLES.")
def test_pilot_history(tmp_path_factory) -> None:
    bundle = load_bundle(DATA_DIR, tmp_path_factory.mktemp("atlas-pilot"))
    for entity_id, selection, expected in PILOT_CASES:
        assert_pilot_state(bundle, entity_id, selection, expected)


def test_pilot_case_shape_is_understood_by_the_asserter(fixture_bundle) -> None:
    """The placeholder machinery works, so filling PILOT_CASES in is safe."""
    assert_pilot_state(fixture_bundle, "experiment:demo", "1990", None)
    assert_pilot_state(fixture_bundle, "experiment:demo", "2006", {"proposed", "approved"})
    assert_pilot_state(fixture_bundle, "experiment:demo", "1997", None)
    assert_pilot_state(fixture_bundle, "experiment:demo", "2009",
                       ("not", {"active", "commissioning"}))
    assert_pilot_state(fixture_bundle, "experiment:demo", "2012", "active")
    for entity_id, selection, expected in A13_EXAMPLES:
        assert isinstance(entity_id, str) and schema.id_type(entity_id) == "experiment"
        assert schema.selection_bounds(selection)
        assert expected is None or isinstance(expected, (str, set, frozenset, tuple))
