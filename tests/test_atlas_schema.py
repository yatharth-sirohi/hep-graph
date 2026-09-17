"""Unit tests for the HEP Atlas v0.2 data contract (hepgraph/atlas/schema.py).

The cases come straight from the ontology's amendment block: A3 (dates,
coverage, presence, state precedence, state_segments, range mode), A4 (date
qualifiers and seasons), A5 (membership render) and A6/A18 (ids, ranks).
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import pytest

from hepgraph.atlas import schema
from hepgraph.atlas.load import load_atlas

FIXTURE = Path(__file__).parent / "fixtures" / "atlas_minimal"
BUILD_DATE = dt.date(2026, 9, 16)


@pytest.fixture(scope="module")
def atlas():
    return load_atlas(FIXTURE)


# ---------------------------------------------------------------- dates ----

def test_date_precision_and_day_range() -> None:
    year = schema.parse_date("2008")
    assert year.precision == "year"
    assert (year.lo(), year.hi()) == (dt.date(2008, 1, 1), dt.date(2008, 12, 31))

    month = schema.parse_date("2008-09")
    assert month.precision == "month"
    assert (month.lo(), month.hi()) == (dt.date(2008, 9, 1), dt.date(2008, 9, 30))

    day = schema.parse_date("2008-09-10")
    assert day.precision == "day"
    assert day.lo() == day.hi() == dt.date(2008, 9, 10)


def test_february_and_leap_years() -> None:
    assert schema.parse_date("2024-02").hi() == dt.date(2024, 2, 29)
    assert schema.parse_date("2023-02").hi() == dt.date(2023, 2, 28)
    assert schema.parse_date("2024-02-29").lo() == dt.date(2024, 2, 29)
    with pytest.raises(schema.DateError):
        schema.parse_date("2023-02-29")


@pytest.mark.parametrize(
    "value",
    [
        "20081",          # wrong shape
        "2008-13",        # impossible month
        "2008-09-31",     # impossible day
        "1899",           # A12: year < 1900
        "2101",           # A12: year > 2100
        {"approx": True},  # object without "date"
        {"date": "2008", "bogus": 1},
        {"date": "2008", "approx": "yes"},
    ],
)
def test_malformed_dates_raise(value) -> None:
    with pytest.raises(schema.DateError):
        schema.parse_date(value)


def test_a4_earliest_latest_widen_the_range() -> None:
    parsed = schema.parse_date(
        {"date": "2008-04", "earliest": "2008-03", "latest": "2008-05", "display": "Spring 2008"}
    )
    assert parsed.lo() == dt.date(2008, 3, 1)
    assert parsed.hi() == dt.date(2008, 5, 31)
    assert parsed.display == "Spring 2008"


def test_a4_inconsistent_earliest_or_latest_is_an_error() -> None:
    with pytest.raises(schema.DateError):
        schema.parse_date({"date": "2008-04", "earliest": "2008-06"})
    with pytest.raises(schema.DateError):
        schema.parse_date({"date": "2008-04", "latest": "2008-02"})


def test_a4_seasons_map_to_month_ranges() -> None:
    assert schema.season_range("Spring", 2008) == ("2008-04", "2008-03", "2008-05")
    assert schema.season_range("summer", 2008) == ("2008-07", "2008-06", "2008-08")
    assert schema.season_range("autumn", 2008) == ("2008-10", "2008-09", "2008-11")
    # Winter wraps: its earliest month is December of the previous year.
    assert schema.season_range("winter", 2008) == ("2008-01", "2007-12", "2008-02")
    assert schema.season_range("harvest", 2008) is None


def test_planned_flag_survives_parsing() -> None:
    assert schema.is_planned({"date": "2030", "planned": True, "approx": True}) is True
    assert schema.is_planned("2030") is False


# ------------------------------------------------------- A3 coverage -------

def _interval(status="active", start="2010", end=None):
    return {"status": status, "start": start, "end": end}


@pytest.mark.parametrize(
    "interval, selection, expected",
    [
        # Year-precision bounds: the selection sits strictly inside.
        (_interval(start="2008", end="2015"), "2010", "certain"),
        # The selection equals the start year, whose hi() is 2008-12-31 > y_lo.
        (_interval(start="2008", end="2015"), "2008", "possible"),
        (_interval(start="2008", end="2015"), "2015", "possible"),
        (_interval(start="2008", end="2015"), "2007", None),
        (_interval(start="2008", end="2015"), "2016", None),
        # Day precision removes the ambiguity at the edges.
        (_interval(start="2008-01-01", end="2015-12-31"), "2008", "certain"),
        # Month resolution inside a year-precision start.
        (_interval(start="2008", end="2015"), "2008-01", "possible"),
        (_interval(start="2008-01-01", end="2015-12-31"), "2008-01", "certain"),
    ],
)
def test_a3_interval_coverage(interval, selection, expected) -> None:
    y_lo, y_hi = schema.selection_bounds(selection)
    assert schema.interval_coverage(interval, y_lo, y_hi, build_date=BUILD_DATE) == expected


def test_a3_open_interval_extends_to_the_build_date_only() -> None:
    row = _interval(start="2017", end=None)
    assert schema.interval_covers(row, "2026", build_date=BUILD_DATE) == "certain"
    # A3: years after the build date are "assumed ongoing", not active.
    assert schema.interval_covers(row, "2027", build_date=BUILD_DATE) is None
    assert schema.interval_covers(row, "2030", build_date=BUILD_DATE) is None


def test_a3_null_start_covers_only_the_end_range() -> None:
    row = {"status": "active", "start": None, "end": "2015"}
    assert schema.interval_covers(row, "2015", build_date=BUILD_DATE) == "possible"
    assert schema.interval_covers(row, "2014", build_date=BUILD_DATE) is None
    assert schema.interval_covers(row, "2016", build_date=BUILD_DATE) is None
    # Null start with a null end says nothing at all.
    unknown = {"status": "active", "start": None, "end": None}
    assert schema.interval_covers(unknown, "2015", build_date=BUILD_DATE) is None


# ------------------------------------------------ A3 presence and state ----

def test_a3_existence_hull_runs_to_the_build_date_when_open() -> None:
    entity = {"intervals": [_interval(start="2005", end="2008", status="proposed"),
                            _interval(start="2010", end=None)]}
    assert schema.existence_hull(entity, build_date=BUILD_DATE) == (dt.date(2005, 1, 1), BUILD_DATE)


def test_a3_existence_hull_stops_at_the_earliest_terminal_start() -> None:
    entity = {"intervals": [_interval(start="1989", end="2000"),
                            _interval(start="2000", end="2000", status="completed")]}
    assert schema.existence_hull(entity, build_date=BUILD_DATE) == (dt.date(1989, 1, 1),
                                                                    dt.date(2000, 12, 31))


def test_a3_presence_uses_the_hull_not_the_intervals() -> None:
    entity = {"intervals": [_interval(start="1990", end="1995"),
                            _interval(start="2005", end="2010")]}
    # 2000 falls in the hull's gap: present, but with no recorded state.
    assert schema.present_at(entity, "2000", build_date=BUILD_DATE) is True
    assert schema.state_at(entity, "2000", build_date=BUILD_DATE) == {
        "status": schema.UNRECORDED, "certainty": "possible", "secondary": []}
    assert schema.present_at(entity, "1989", build_date=BUILD_DATE) is False
    assert schema.state_at(entity, "1989", build_date=BUILD_DATE) is None


def test_a3_precedence_rule_1_realised_beats_speculative() -> None:
    entity = {"intervals": [
        _interval(status="proposed", start="2005", end="2012"),
        _interval(status="construction", start="2008", end="2012"),
    ]}
    state = schema.state_at(entity, "2010", build_date=BUILD_DATE)
    assert state["status"] == "construction"
    # The dropped candidate does not reappear as a secondary state.
    assert state["secondary"] == []


def test_a3_precedence_rule_1_terminal_beats_speculative() -> None:
    entity = {"intervals": [
        _interval(status="planned", start="2005", end="2015"),
        _interval(status="cancelled", start="2009", end="2009"),
    ]}
    assert schema.state_at(entity, "2009", build_date=BUILD_DATE)["status"] == "cancelled"


def test_a3_precedence_rule_2_latest_start_wins() -> None:
    entity = {"intervals": [
        _interval(status="construction", start="2008", end="2012"),
        _interval(status="commissioning", start="2011", end="2012"),
    ]}
    state = schema.state_at(entity, "2012", build_date=BUILD_DATE)
    assert state["status"] == "commissioning"
    assert state["secondary"] == ["construction"]


def test_a3_precedence_rule_3_ties_break_by_rank() -> None:
    # Identical starts: `shutdown` outranks `active` in STATE_PRECEDENCE.
    entity = {"intervals": [
        _interval(status="active", start="2016", end="2016"),
        _interval(status="shutdown", start="2016", end="2016"),
    ]}
    assert schema.state_at(entity, "2016", build_date=BUILD_DATE)["status"] == "shutdown"
    assert schema.STATE_RANK["decommissioned"] > schema.STATE_RANK["cancelled"]
    assert schema.STATE_RANK["cancelled"] > schema.STATE_RANK["completed"]
    assert schema.STATE_RANK["completed"] > schema.STATE_RANK["shutdown"]
    assert schema.STATE_RANK["construction"] > schema.STATE_RANK["approved"]
    assert schema.STATE_RANK["proposed"] > schema.STATE_RANK["planned"]


def test_a3_secondary_states_are_reported() -> None:
    entity = {"intervals": [
        _interval(status="construction", start="2008", end="2011"),
        _interval(status="commissioning", start="2010", end="2011"),
        _interval(status="active", start="2010", end="2015"),
    ]}
    state = schema.state_at(entity, "2011", build_date=BUILD_DATE)
    assert state["status"] in {"active", "commissioning"}
    assert "construction" in state["secondary"]


# --------------------------------------------------- A3 state_segments -----

def test_month_index_epoch_is_1950_01() -> None:
    assert schema.month_index(dt.date(1950, 1, 1)) == 0
    assert schema.month_index(dt.date(1950, 2, 1)) == 1
    assert schema.month_index(dt.date(1951, 1, 1)) == 12
    assert schema.month_index(dt.date(2026, 9, 16)) == (2026 - 1950) * 12 + 8
    # Dates before the epoch are honestly negative, not clamped.
    assert schema.month_index(dt.date(1949, 12, 1)) == -1
    assert schema.month_to_date(920) == dt.date(2026, 9, 1)


def test_state_segments_are_contiguous_and_cover_the_hull(atlas) -> None:
    experiment = atlas.get("experiment:demo")
    segments = schema.state_segments(experiment, BUILD_DATE)
    assert segments, "the fixture experiment must have segments"
    for previous, current in zip(segments, segments[1:]):
        assert current[0] == previous[1] + 1, "segments must be contiguous"
        assert (current[2], current[3]) != (previous[2], previous[3]), "runs must be merged"
    hull = schema.existence_hull(experiment, build_date=BUILD_DATE)
    assert segments[0][0] == schema.month_index(hull[0])
    assert segments[-1][1] == schema.month_index(hull[1])
    for _m0, _m1, status, certainty in segments:
        assert status in schema.STATUSES or status == schema.UNRECORDED
        assert certainty in schema.CERTAINTIES


def test_state_segments_agree_with_state_at(atlas) -> None:
    experiment = atlas.get("experiment:demo")
    segments = schema.state_segments(experiment, BUILD_DATE)
    for m0, m1, status, certainty in segments:
        for index in (m0, (m0 + m1) // 2, m1):
            bounds = schema.month_bounds(index)
            state = schema.state_at(experiment, bounds, build_date=BUILD_DATE)
            assert state == {"status": status, "certainty": certainty,
                             "secondary": state["secondary"]}


def test_state_segments_of_the_fixture_experiment_tell_its_story(atlas) -> None:
    experiment = atlas.get("experiment:demo")
    segments = schema.state_segments(experiment, BUILD_DATE)
    statuses = [segment[2] for segment in segments]
    assert statuses[0] == "proposed"
    assert "construction" in statuses
    assert "shutdown" in statuses
    assert statuses[-1] == "active"
    # The 2016 long shutdown occupies exactly the twelve months of 2016.
    shutdown = [segment for segment in segments if segment[2] == "shutdown"]
    assert len(shutdown) == 1
    assert schema.month_to_date(shutdown[0][0]) == dt.date(2016, 1, 1)
    assert schema.month_to_date(shutdown[0][1]) == dt.date(2016, 12, 1)


def test_range_mode_picks_the_longest_clipped_duration(atlas) -> None:
    experiment = atlas.get("experiment:demo")
    segments = schema.state_segments(experiment, BUILD_DATE)
    verdict = schema.range_state(segments,
                                 schema.month_index(dt.date(2010, 1, 1)),
                                 schema.month_index(dt.date(2016, 12, 1)))
    assert verdict["status"] == "active"
    assert "shutdown" in verdict["secondary"]
    assert verdict["months"] > 12
    assert schema.range_state(segments, -100, -50) is None


def test_hull_gaps_report_unrecorded_stretches() -> None:
    entity = {"intervals": [_interval(start="1990-01", end="1994-12"),
                            _interval(start="2000-01", end="2004-12")]}
    gaps = schema.hull_gaps(entity, build_date=BUILD_DATE)
    # The interior gap, plus the trailing one: with no terminal interval the
    # hull runs to the build date (A3), so 2005 onwards is unrecorded too.
    assert len(gaps) == 2
    assert schema.month_to_date(gaps[0][0]) == dt.date(1995, 1, 1)
    assert schema.month_to_date(gaps[0][1]) == dt.date(1999, 12, 1)
    assert gaps[0][1] - gaps[0][0] + 1 >= schema.MAX_HULL_GAP_MONTHS
    assert schema.month_to_date(gaps[1][0]) == dt.date(2005, 1, 1)
    # A terminal interval closes the hull, leaving only the interior gap.
    entity["intervals"].append({"status": "completed", "start": "2004-12", "end": "2004-12"})
    assert len(schema.hull_gaps(entity, build_date=BUILD_DATE)) == 1


# ----------------------------------------------- A5 membership rendering ---

def _member(**kwargs):
    row = {"institution_id": "institution:x", "start": None, "end": None,
           "known_since": None, "known_until": None}
    row.update(kwargs)
    return row


def test_a5_dated_membership_is_solid_and_counted() -> None:
    row = _member(start="2005-06", end=None)
    verdict = schema.membership_render(row, "2010", formation="2005-06", as_of="2026-09",
                                       build_date=BUILD_DATE, membership_history="partial")
    assert verdict == {"render": "solid", "counted": True, "reason": "confirmed"}


def test_a5_evidence_window_makes_a_row_solid() -> None:
    row = _member(start=None, known_since="2012", known_until="2026-09")
    verdict = schema.membership_render(row, "2015", formation="2005-06", as_of="2026-09",
                                       build_date=BUILD_DATE, membership_history="partial")
    assert verdict["render"] == "solid" and verdict["counted"] is True


def test_a5_undated_years_are_hollow_and_uncounted() -> None:
    row = _member(start=None, known_since="2012", known_until="2026-09")
    verdict = schema.membership_render(row, "2008", formation="2005-06", as_of="2026-09",
                                       build_date=BUILD_DATE, membership_history="partial")
    assert verdict == {"render": "hollow", "counted": False, "reason": "undated"}
    # A5: a `complete` history means the undated years really are membership years.
    complete = schema.membership_render(row, "2008", formation="2005-06", as_of="2026-09",
                                        build_date=BUILD_DATE, membership_history="complete")
    assert complete == {"render": "hollow", "counted": True, "reason": "undated"}


def test_a5_before_formation_the_row_does_not_apply() -> None:
    row = _member(start=None, known_since="2012", known_until="2026-09")
    assert schema.membership_render(row, "2001", formation="2005-06", as_of="2026-09",
                                    build_date=BUILD_DATE) is None


def test_a5_after_as_of_the_row_is_hollow_not_re_verified() -> None:
    row = _member(start="2005-06", end=None)
    verdict = schema.membership_render(row, "2026-12", formation="2005-06", as_of="2026-09",
                                       build_date=dt.date(2027, 6, 1))
    assert verdict == {"render": "hollow", "counted": False, "reason": "not_re_verified"}


def test_a5_counts_wording_inputs(atlas) -> None:
    roster = atlas.memberships["collaboration:demo"]
    counts = schema.membership_counts(
        roster["members"], "2026",
        formation="2005-06", as_of=roster["as_of"], build_date=BUILD_DATE,
        membership_history=roster["membership_history"])
    assert counts == {"confirmed": 2, "undated": 0}
    early = schema.membership_counts(
        roster["members"], "2008",
        formation="2005-06", as_of=roster["as_of"], build_date=BUILD_DATE,
        membership_history=roster["membership_history"])
    assert early == {"confirmed": 1, "undated": 1}


def test_a19_evidence_precedence_and_wording() -> None:
    assert schema.strongest_evidence_class(
        ["derived", "publication_affiliation_current", "official_roster"]) == "official_roster"
    assert schema.strongest_evidence_class(
        ["self_reported", "publication_affiliation_historical"]) == "self_reported"
    assert schema.strongest_evidence_class([]) is None
    assert schema.evidence_label("official_roster", as_of="2026-09") == (
        "On the collaboration's own member list (as of 2026-09)")
    assert schema.evidence_label("publication_affiliation_historical",
                                 collaboration="DUNE", year=2011) == (
        "Listed on a DUNE paper in 2011; may no longer be a member")
    assert schema.evidence_label("derived") == "Inferred, not verified"


# ------------------------------------------------------ A6 / A18 tables ----

def test_a6_person_ids_use_a_hyphen() -> None:
    assert schema.is_valid_id("person:inspire-1019647")
    assert not schema.is_valid_id("person:inspire:1019647")
    assert schema.canonical_id("person:inspire:1019647") == "person:inspire-1019647"
    assert schema.canonical_id("person:unresolved:demo-student") == "person:unresolved-demo-student"
    assert schema.canonical_id("experiment:dune") == "experiment:dune"
    assert schema.inspire_recid("person:inspire-1019647") == 1019647
    assert schema.inspire_recid("person:unresolved-demo-student") is None
    assert schema.hep_graph_url("person:inspire-1019647") == "/?source=1019647&mode=live"
    assert schema.hep_graph_url("person:unresolved-demo-student") is None
    assert schema.filename_for("person:inspire-1019647") == "inspire-1019647"


def test_a18_source_ranks_are_derived_from_the_type() -> None:
    assert schema.source_rank("official_experiment_site") == 1
    assert schema.source_rank("official_facility_site") == 2
    assert schema.source_rank("experiment_registry") == 3
    assert schema.source_rank("inspire_experiment_record") == 3
    assert schema.source_rank("journal_article") == 10
    assert schema.source_rank("wikipedia") == 12
    # The retired `inspire_record` still resolves, to the literature rank.
    assert schema.source_rank("inspire_record") == 10
    assert schema.source_rank("not_a_type") is None


def test_a8_unit_table_additions() -> None:
    for dimension, unit in [("energy", "PeV"), ("energy", "µeV"), ("mass", "mg"),
                            ("time", "h"), ("magnetic_field", "G"), ("area", "km^2"),
                            ("electric_field", "kV/cm"), ("exposure", "t yr"),
                            ("fraction", "%"), ("volume", "L"), ("current", "mA"),
                            ("cross_section", "fb"), ("rate", "kHz"),
                            ("mass_energy", "GeV/c^2"), ("luminosity", "Hz/nb"),
                            ("angle", "arcsec"), ("power", "GW"), ("mass", "Mt")]:
        assert schema.unit_allowed(dimension, unit), f"{unit} missing from {dimension}"
    assert not schema.unit_allowed("length", "furlong")
    assert schema.unit_allowed("count", None)
    # Every declared unit has a scale factor.
    for dimension, units in schema.UNITS.items():
        for unit in units:
            assert unit in schema.UNIT_SCALE[dimension], f"{dimension}/{unit} has no scale"


def test_quantity_and_display_magnitudes() -> None:
    quantity = {"value": 1285, "unit": "km", "dimension": "length", "display": "~1,300 km"}
    assert schema.quantity_magnitude(quantity) == 1_285_000.0
    assert schema.display_magnitude(quantity) == 1_300_000.0
    assert schema.display_magnitude({"value": 1, "unit": "km", "dimension": "length",
                                     "display": "a few"}) is None
    span = {"min": 0.6, "max": 10, "unit": "GeV", "dimension": "energy"}
    assert schema.quantity_magnitude(span) == pytest.approx(5.3e9)


def test_a21_plausibility_table_and_great_circle() -> None:
    low, high = schema.PLAUSIBILITY_RANGES["baseline"]["length"]
    assert low == 100.0 and high == 2.0e7
    # Fermilab-like campus to a SURF-like cavern: the fixture's 1285 km baseline.
    metres = schema.great_circle_m(41.832, -88.252, 44.352, -103.751)
    assert abs(metres / 1000.0 - 1285) / 1285 < schema.BASELINE_TOLERANCE
    assert schema.great_circle_m(0.0, 0.0, 0.0, 0.0) == 0.0


# ------------------------------------------------------------- A9 shapes ---

def test_a9_reference_entries_may_be_objects_with_intervals(atlas) -> None:
    experiment = atlas.get("experiment:demo")
    entry = experiment["accelerator_ids"][0]
    entity_id, interval = schema.ref_entry(entry)
    assert entity_id == "accelerator:demo-synchrotron"
    assert interval["start"] == "2010-03" and interval["end"] is None
    assert schema.ref_ids(experiment["accelerator_ids"]) == ["accelerator:demo-synchrotron"]
    assert schema.ref_ids(experiment["beamline_ids"]) == ["beamline:demo-beam"]
    assert schema.ref_entry("beamline:demo-beam") == ("beamline:demo-beam", None)


def test_a9_slist_accepts_both_shapes(atlas) -> None:
    experiment = atlas.get("experiment:demo")
    rows = schema.slist(experiment["physics_goals"])
    assert [row["value"] for row in rows] == ["Measure delta_CP",
                                              "Determine the neutrino mass ordering"]
    assert schema.slist_is_legacy(experiment["physics_goals"]) is False
    legacy = {"value": ["a", "b"], "sources": ["src:x"], "confidence": "verified"}
    assert [row["value"] for row in schema.slist(legacy)] == ["a", "b"]
    assert all(row["sources"] == ["src:x"] for row in schema.slist(legacy))
    assert schema.slist_is_legacy(legacy) is True


def test_reference_walker_finds_nested_and_object_entries(atlas) -> None:
    experiment = atlas.get("experiment:demo")
    found = dict(schema.iter_reference_fields(experiment))
    assert found["accelerator_ids[0].id"] == "accelerator:demo-synchrotron"
    assert found["facility_roles[0].facility_id"] == "facility:demo-lab"
    assert found["sources[0]"].startswith("src:")
    assert found["key_specs[0].quantity.sources[0]"] == "src:demo-tdr"


def test_normalised_names_ignore_case_punctuation_and_a_leading_the() -> None:
    assert schema.normalise_name("The Super-Kamiokande") == "superkamiokande"
    assert schema.normalise_name("SuperK") == "superk"
    assert schema.normalise_name("Super-K") == schema.normalise_name("SUPER K")


# ----------------------------------------------------------- A10 / A11 ----

def test_a10_fixture_status_equals_the_derived_state_at_the_build_date(atlas) -> None:
    selection = f"{BUILD_DATE.year:04d}-{BUILD_DATE.month:02d}"
    for entity_type, entity_id, record in atlas.iter_entities():
        if not record.get("intervals"):
            continue
        state = schema.state_at(record, selection, build_date=BUILD_DATE)
        assert state is not None, f"{entity_id} has intervals but no state at the build date"
        assert record.get("status") == state["status"], entity_id


def test_a11_every_fixture_file_carries_the_schema_tag_and_canonical_json() -> None:
    from hepgraph.atlas.load import dump_json

    for path in sorted(FIXTURE.rglob("*.json")):
        text = path.read_text(encoding="utf-8")
        payload = json.loads(text)
        assert text == dump_json(payload), f"{path} is not canonical JSON (A11)"
        records = payload if isinstance(payload, list) else [payload]
        for record in records:
            if isinstance(record, dict) and "coverage" not in path.parts:
                assert record.get("schema") == schema.SCHEMA_TAG, path


def test_a1_fixture_authors_no_derived_fields() -> None:
    """A1/A22: derived fields are build outputs and never appear in a data file.

    This reads the files on disk, not the loaded model: load.py legitimately
    fills in derived fields such as `hep_graph` in memory.
    """
    for path in sorted(FIXTURE.rglob("*.json")):
        if path.parts[-2] in {"coverage", "memberships"}:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for record in (payload if isinstance(payload, list) else [payload]):
            if not isinstance(record, dict):
                continue
            entity_type = schema.id_type(record.get("id") or "")
            for field in schema.DERIVED_FIELDS.get(entity_type, ()):
                assert field not in record, f"{path} authors the derived field {field!r}"


def test_a2_placements_and_facility_roles_replace_the_scalars(atlas) -> None:
    detector = atlas.get("detector:demo-far-detector")
    assert "site_id" not in detector and "facility_id" not in detector
    assert detector["placements"][0]["site_id"] == "site:demo-far-cavern"
    assert detector["placements"][0]["role"] in schema.PLACEMENT_ROLES
    experiment = atlas.get("experiment:demo")
    assert "facility_ids" not in experiment
    assert experiment["facility_roles"][0]["role"] in schema.FACILITY_ROLES


# ------------------------------------------- legacy migration on load ------

def test_legacy_v01_records_are_migrated_on_load(tmp_path: Path) -> None:
    """A2/A5/A6/A7/A9: a v0.1 tree loads, with one warning per migration."""
    import shutil

    root = tmp_path / "atlas"
    shutil.copytree(FIXTURE, root)

    detector_path = root / "detectors" / "demo-far-detector.json"
    detector = json.loads(detector_path.read_text(encoding="utf-8"))
    detector.pop("placements")
    detector.pop("technology_classes")
    detector.pop("schema")
    detector["site_id"] = "site:demo-far-cavern"
    detector["facility_id"] = "facility:demo-lab"
    detector_path.write_text(json.dumps(detector), encoding="utf-8")

    experiment_path = root / "experiments" / "demo.json"
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    experiment.pop("facility_roles")
    experiment["facility_ids"] = ["facility:demo-lab"]
    experiment_path.write_text(json.dumps(experiment), encoding="utf-8")

    source_path = root / "sources" / "demo-result-paper.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    source["type"] = "source"
    source["source_type"] = "inspire_record"
    source["rank"] = 11
    source_path.write_text(json.dumps(source), encoding="utf-8")

    membership_path = root / "memberships" / "demo.json"
    membership = json.loads(membership_path.read_text(encoding="utf-8"))
    membership.pop("membership_history")
    membership["default_evidence_class"] = "official_institution_list"
    for row in membership["members"]:
        row.pop("evidence_class")
    membership_path.write_text(json.dumps(membership), encoding="utf-8")

    person_path = root / "people" / "inspire-1019647.json"
    person = json.loads(person_path.read_text(encoding="utf-8"))
    person["id"] = "person:inspire:1019647"
    person_path.write_text(json.dumps(person), encoding="utf-8")
    (root / "people" / "inspire-1019647.json").rename(root / "people" / "inspire-1019647.json")

    collaboration_path = root / "collaborations" / "demo.json"
    collaboration = json.loads(collaboration_path.read_text(encoding="utf-8"))
    collaboration["leadership"][0]["person_id"] = "person:inspire:1019647"
    collaboration_path.write_text(json.dumps(collaboration), encoding="utf-8")

    coverage_path = root / "coverage" / "fixture.json"
    coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
    coverage[0].pop("entity_id")
    coverage[0]["validated"] = True
    coverage[0]["globe_ready"] = True
    coverage_path.write_text(json.dumps(coverage), encoding="utf-8")

    migrated = load_atlas(root)
    assert migrated.problems == [], [str(problem) for problem in migrated.problems]
    messages = " | ".join(str(warning) for warning in migrated.warnings)

    detector = migrated.get("detector:demo-far-detector")
    assert detector["placements"] == [{
        "site_id": "site:demo-far-cavern", "role": "main", "start": None, "end": None,
        "sources": ["src:demo-tdr"], "verified_at": None, "confidence": "derived",
        "note": "migrated from the v0.1 scalar `site_id`",
    }]
    assert "facility_id" not in detector
    assert detector["technology_classes"] == ["lar_tpc"]
    assert detector["schema"] == schema.SCHEMA_TAG
    assert "A2" in messages and "A9" in messages

    experiment = migrated.get("experiment:demo")
    assert experiment["facility_roles"] == [{
        "facility_id": "facility:demo-lab", "role": "host", "start": None, "end": None,
        "sources": experiment["sources"],
    }]
    assert "facility_ids" not in experiment

    source = migrated.get("src:demo-result-paper")
    assert source["type"] == "src"
    assert source["source_type"] == "inspire_literature_record"
    assert source["rank"] == 10

    roster = migrated.memberships["collaboration:demo"]
    assert roster["membership_history"] == "unknown"
    assert "default_evidence_class" not in roster
    assert all(row["evidence_class"] == "official_institution_list" for row in roster["members"])

    assert migrated.get("person:inspire-1019647") is not None
    assert migrated.get("person:inspire:1019647") is not None  # resolved through canonical_id
    assert migrated.get("person:inspire-1019647")["hep_graph"] == {
        "available": True, "url": "/?source=1019647&mode=live"}
    assert migrated.get("collaboration:demo")["leadership"][0]["person_id"] == "person:inspire-1019647"

    row = migrated.coverage[0]
    assert row["entity_id"] == "experiment:demo"
    assert "validated" not in row and "globe_ready" not in row


def test_unresolved_person_gets_no_hep_graph_url(atlas) -> None:
    person = atlas.get("person:unresolved-demo-demo-lab-demo-student")
    assert person["hep_graph"] == {"available": False}


def test_load_reports_problems_instead_of_raising(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    (root / "experiments").mkdir(parents=True)
    (root / "experiments" / "broken.json").write_text("{not json", encoding="utf-8")
    (root / "experiments" / "wrong-name.json").write_text(
        json.dumps({"id": "experiment:other", "type": "experiment"}), encoding="utf-8")
    broken = load_atlas(root)
    messages = " ".join(str(problem) for problem in broken.problems)
    assert "unreadable JSON" in messages
    assert "filename must be" in messages
