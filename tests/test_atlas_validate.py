"""Tests for the HEP Atlas v0.2 validator (hepgraph/atlas/validate.py).

The fixture dataset (`tests/fixtures/atlas_minimal/`) is the ground truth: it
must validate with zero errors and zero warnings on its own.  Every other test
here copies that fixture into a temporary directory, mutates exactly one file
to introduce one specific defect, and asserts that the validator catches it
under the expected rule and severity — the same "one defect, one rule"
discipline `validate.py`'s module docstring describes.

Two defects the orchestrator asked to be re-checked against the ontology
(A1/A10, coverage backlog rows) get their own focused section rather than a
mutation, since the real `data/atlas/coverage/backlog.json` already exercises
them at scale.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Callable

import pytest

from hepgraph.atlas import validate as v
from hepgraph.atlas.load import dump_json, load_atlas

FIXTURE = Path(__file__).parent / "fixtures" / "atlas_minimal"
BUILD_DATE = "2026-09-16"


# ---------------------------------------------------------------------------
# Fixture plumbing
# ---------------------------------------------------------------------------

@pytest.fixture
def root(tmp_path: Path) -> Path:
    """A private copy of the fixture tree this test may mutate freely."""
    target = tmp_path / "atlas"
    shutil.copytree(FIXTURE, target)
    return target


def _read(root: Path, relative: str) -> dict:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def _write(root: Path, relative: str, record: dict) -> None:
    (root / relative).write_text(json.dumps(record), encoding="utf-8")


def _mutate(root: Path, relative: str, edit: Callable[[dict], None]) -> None:
    """Read `relative`, apply `edit` in place, and write it back."""
    record = _read(root, relative)
    edit(record)
    _write(root, relative, record)


def _validate(root: Path) -> list[v.Finding]:
    atlas = load_atlas(root)
    assert atlas.problems == [], [str(problem) for problem in atlas.problems]
    return v.validate_atlas(atlas, build_date=BUILD_DATE)


def _findings(findings: list[v.Finding], rule: str) -> list[v.Finding]:
    return [finding for finding in findings if finding.rule == rule]


# ---------------------------------------------------------------------------
# The fixture itself
# ---------------------------------------------------------------------------

def test_fixture_validates_cleanly() -> None:
    """The ground-truth dataset must have no errors and no warnings at all."""
    findings = _validate(FIXTURE)
    assert v.errors(findings) == [], [str(f) for f in v.errors(findings)]
    assert v.warnings(findings) == [], [str(f) for f in v.warnings(findings)]
    assert v.infos(findings) == [], [str(f) for f in v.infos(findings)]


def test_cli_exits_zero_on_the_clean_fixture() -> None:
    assert v.main(["--data", str(FIXTURE)]) == 0


# ---------------------------------------------------------------------------
# One mutation per rule (task 2 of the review)
# ---------------------------------------------------------------------------

def _missing_sources(root: Path) -> None:
    _mutate(root, "experiments/demo.json",
            lambda r: r["energy_regime"].__setitem__("sources", []))


def _confidence_without_note(root: Path) -> None:
    def edit(r: dict) -> None:
        r["energy_regime"]["confidence"] = "uncertain"
        r["energy_regime"]["note"] = ""
    _mutate(root, "experiments/demo.json", edit)


def _dangling_reference(root: Path) -> None:
    _mutate(root, "experiments/demo.json",
            lambda r: r["topic_ids"].append("topic:does-not-exist"))


def _interval_end_before_start(root: Path) -> None:
    def edit(r: dict) -> None:
        # intervals[2] is "Run 1", start 2010-03: give it an end before that.
        assert r["intervals"][2]["label"] == "Run 1"
        r["intervals"][2]["end"] = "2005-01-01"
    _mutate(root, "experiments/demo.json", edit)


def _non_terminal_after_terminal(root: Path) -> None:
    def edit(r: dict) -> None:
        # A terminal interval starting in 2003, before the (non-terminal)
        # "proposal" interval that starts in 2005: A3 forbids exactly this.
        r["intervals"].append({
            "label": "cancelled-branch", "status": "cancelled", "kind": "lifecycle",
            "start": "2003", "end": "2003", "sources": ["src:demo-experiment-site"],
            "verified_at": "2026-09-16", "confidence": "verified", "note": "",
        })
    _mutate(root, "experiments/demo.json", edit)


def _detector_at_headquarters_coordinates(root: Path) -> None:
    _mutate(root, "sites/demo-far-cavern.json",
            lambda r: r["coordinates"].__setitem__("kind", "headquarters"))


def _baseline_disagrees_with_great_circle(root: Path) -> None:
    def edit(r: dict) -> None:
        r["baselines"][0]["distance"]["value"] = 1
        r["baselines"][0]["distance"]["display"] = "~1 km"
    _mutate(root, "beamlines/demo-beam.json", edit)


def _display_ten_times_the_value(root: Path) -> None:
    def edit(r: dict) -> None:
        # value is 120 GeV; 1300 GeV is a factor ~10.8, over the A21 factor-10 cap.
        r["specs"]["beam_energy"]["display"] = "1300 GeV"
    _mutate(root, "accelerators/demo-synchrotron.json", edit)


def _duplicate_alias(root: Path) -> None:
    _mutate(root, "experiments/demo.json", lambda r: r["aliases"].append("DEMO"))


def _duplicate_external_id(root: Path) -> None:
    _mutate(root, "institutions/university-of-iowa.json",
            lambda r: r["external"].__setitem__("ror", "https://ror.org/020hgte69"))


def _result_before_experiment_began(root: Path) -> None:
    # The experiment's earliest active/commissioning start is Run 1, 2010-03.
    _mutate(root, "results/demo-oscillation-observation-2020.json",
            lambda r: r["date"].__setitem__("value", "2009-01-01"))


def _future_date_without_planned(root: Path) -> None:
    _mutate(root, "collaborations/demo.json",
            lambda r: r["formation"].__setitem__("value", "2030"))


MUTATION_CASES: tuple[tuple[str, Callable[[Path], None], str, str], ...] = (
    ("missing sources", _missing_sources, "sourced-value-without-sources", v.ERROR),
    ("confidence without a note", _confidence_without_note, "confidence-note-required", v.ERROR),
    ("dangling reference", _dangling_reference, "dangling-reference", v.ERROR),
    ("end before start", _interval_end_before_start, "interval-end-before-start", v.ERROR),
    ("terminal without a later non-terminal", _non_terminal_after_terminal,
     "non-terminal-after-terminal", v.ERROR),
    ("detector at headquarters coordinates", _detector_at_headquarters_coordinates,
     "coordinate-kind", v.ERROR),
    ("baseline disagrees with the great-circle distance", _baseline_disagrees_with_great_circle,
     "baseline-distance", v.ERROR),
    ("display string ten times its value", _display_ten_times_the_value,
     "display-value-mismatch", v.ERROR),
    ("duplicate alias", _duplicate_alias, "duplicate-alias", v.ERROR),
    ("duplicate external id", _duplicate_external_id, "duplicate-external-id", v.ERROR),
    ("result dated before its experiment began", _result_before_experiment_began,
     "result-before-experiment", v.ERROR),
    ("future date without planned", _future_date_without_planned,
     "future-date-not-planned", v.ERROR),
)


@pytest.mark.parametrize("name, mutate, rule, level", MUTATION_CASES, ids=[case[0] for case in MUTATION_CASES])
def test_one_mutation_is_caught_under_its_rule(root: Path, name: str,
                                               mutate: Callable[[Path], None],
                                               rule: str, level: str) -> None:
    mutate(root)
    findings = _validate(root)
    matches = _findings(findings, rule)
    assert matches, f'{name!r}: expected rule {rule!r} to fire; got {[str(f) for f in findings]}'
    assert all(finding.level == level for finding in matches), \
        f'{name!r}: expected every {rule!r} finding at level {level!r}, got {[f.level for f in matches]}'


def test_mutations_are_independent_of_each_other(root: Path) -> None:
    """Sanity check on the harness: an untouched copy is still clean."""
    findings = _validate(root)
    assert v.errors(findings) == []


# ---------------------------------------------------------------------------
# Validator defect (a): the coverage backlog is not a wall of dangling refs.
# ---------------------------------------------------------------------------

def _add_coverage_row(root: Path, *, researched: str, entity_id: str = "experiment:not-yet-researched") -> None:
    (root / "coverage" / "backlog.json").write_text(json.dumps([{
        "name": "Not Yet Researched", "entity_id": entity_id, "experiment_id": entity_id,
        "category": "other", "facility": "", "tier": "C", "priority": 9,
        "researched": researched, "missing_fields": ["all"], "owner": None, "notes": "",
    }]), encoding="utf-8")


def test_a10_an_unresearched_backlog_row_naming_a_missing_entity_is_informational(root: Path) -> None:
    _add_coverage_row(root, researched="none")
    findings = _validate(root)
    assert v.errors(findings) == [], [str(f) for f in v.errors(findings)]
    info = _findings(findings, "coverage-not-yet-researched")
    assert len(info) >= 1
    assert all(finding.level == v.INFO for finding in info)
    assert not _findings(findings, "dangling-reference")


@pytest.mark.parametrize("researched", ["partial", "full"])
def test_a10_a_row_claiming_research_for_a_missing_entity_is_still_an_error(root: Path, researched: str) -> None:
    _add_coverage_row(root, researched=researched)
    findings = _validate(root)
    dangling = _findings(findings, "dangling-reference")
    assert dangling, f'researched={researched!r} naming a missing entity must still error'
    assert all(finding.level == v.ERROR for finding in dangling)
    assert not _findings(findings, "coverage-not-yet-researched")


def test_a10_a_backlog_row_naming_an_existing_entity_never_gets_an_info_note(root: Path) -> None:
    """Once an entity exists, its backlog row is ordinary — no info noise."""
    _mutate(root, "coverage/fixture.json", lambda rows: rows[0].__setitem__("researched", "none"))
    findings = _validate(root)
    assert not _findings(findings, "coverage-not-yet-researched")
    assert not _findings(findings, "dangling-reference")


# ---------------------------------------------------------------------------
# Validator defect (b): a derived field is reported once, under its own rule.
# ---------------------------------------------------------------------------

def test_a1_an_authored_derived_field_is_not_also_a_dangling_reference(root: Path) -> None:
    """`detector.document_ids` is derived (A1): authoring it warns once, and
    a target that does not exist must not *also* surface as a dangling
    reference — the build ignores the field's contents entirely."""
    _mutate(root, "detectors/demo-far-detector.json",
            lambda r: r.__setitem__("document_ids", ["document:does-not-exist"]))
    findings = _validate(root)
    derived = _findings(findings, "derived-field")
    assert any(f.entity_id == "detector:demo-far-detector" and "document_ids" in f.pointer
              for f in derived)
    assert not any("document:does-not-exist" in f.message for f in findings
                  if f.rule == "dangling-reference")


def test_a1_a_derived_field_naming_a_real_entity_is_still_only_a_warning(root: Path) -> None:
    """Even when the named entity *does* exist, the field stays derived-only:
    no dangling-reference, no reference-type-mismatch noise from it either."""
    _mutate(root, "detectors/demo-far-detector.json",
            lambda r: r.__setitem__("document_ids", ["document:demo-tdr"]))
    findings = _validate(root)
    assert v.errors(findings) == [], [str(f) for f in v.errors(findings)]
    assert _findings(findings, "derived-field")


# ---------------------------------------------------------------------------
# Validator defect (c): legitimate Appendix A spec keys on accelerators.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("key, dimension, value, display", [
    ("integrated_luminosity", "integrated_luminosity", 1000, "1000 fb^-1"),
    ("design_luminosity", "luminosity", 6e35, "6e35 cm^-2 s^-1"),
])
def test_a21_appendix_a_luminosity_keys_are_recognised(root: Path, key: str, dimension: str,
                                                       value: float, display: str) -> None:
    def edit(r: dict) -> None:
        r["specs"][key] = {
            "value": value, "unit": "fb^-1" if dimension == "integrated_luminosity" else "cm^-2 s^-1",
            "dimension": dimension, "display": display, "sources": ["src:demo-lab-site"],
            "verified_at": "2026-09-16", "confidence": "verified", "note": "",
        }
    _mutate(root, "accelerators/demo-synchrotron.json", edit)
    findings = _validate(root)
    assert not _findings(findings, "unknown-spec-key")


def test_a21_collision_scheme_is_a_recognised_sourced_string(root: Path) -> None:
    def edit(r: dict) -> None:
        r["specs"]["collision_scheme"] = {
            "value": "nano-beam scheme", "sources": ["src:demo-lab-site"],
            "verified_at": "2026-09-16", "confidence": "verified", "note": "",
        }
    _mutate(root, "accelerators/demo-synchrotron.json", edit)
    findings = _validate(root)
    assert not _findings(findings, "unknown-spec-key")
    assert not _findings(findings, "spec-key-dimension")


# ---------------------------------------------------------------------------
# Validator defect (d): every citation path feeds the A22 "uncited" check.
# ---------------------------------------------------------------------------

_EXTRA_SOURCE_ID = "src:demo-extra-citation-target"


def _add_uncited_source(root: Path) -> None:
    """A brand-new source nothing in the fixture cites yet."""
    (root / "sources" / "demo-extra-citation-target.json").write_text(json.dumps({
        "id": _EXTRA_SOURCE_ID, "type": "src", "source_type": "secondary",
        "rank": 12, "title": "An extra source used only to test citation paths",
        "publisher": "", "url": "https://example.org/demo-extra", "accessed": "2026-09-16",
        "date": "2026", "excerpt": "", "retrieval": "partial",
        "link_check": {"last_checked": None, "http_status": None, "redirect": None},
    }), encoding="utf-8")


@pytest.mark.parametrize("relative, edit", [
    ("experiments/demo.json",
     lambda r: r["intervals"][0].__setitem__("sources", [_EXTRA_SOURCE_ID])),
    ("experiments/demo.json",
     lambda r: r["key_specs"][0]["quantity"].__setitem__("sources", [_EXTRA_SOURCE_ID])),
    ("institutions/demo-lab.json",
     lambda r: r["coordinates"].__setitem__("sources", [_EXTRA_SOURCE_ID])),
    ("detectors/demo-far-detector.json",
     lambda r: r["placements"][0].__setitem__("sources", [_EXTRA_SOURCE_ID])),
    ("collaborations/demo.json",
     lambda r: r["leadership"][0].__setitem__("sources", [_EXTRA_SOURCE_ID])),
    ("memberships/demo.json",
     lambda r: r["members"][0].__setitem__("sources", [_EXTRA_SOURCE_ID])),
    ("results/demo-oscillation-observation-2020.json",
     lambda r: r["claim"].__setitem__("sources", [_EXTRA_SOURCE_ID])),
    ("experiments/demo.json",
     lambda r: r["facility_roles"][0].__setitem__("sources", [_EXTRA_SOURCE_ID])),
    ("beamlines/demo-beam.json",
     lambda r: r["baselines"][0].__setitem__("sources", [_EXTRA_SOURCE_ID])),
    ("experiments/demo.json",
     lambda r: r["lineage"].append({"experiment_id": "experiment:demo", "relation": "same_program",
                                    "sources": [_EXTRA_SOURCE_ID]})),
], ids=["interval", "quantity", "coordinates", "placement", "leadership", "membership-row", "claim",
        "facility-role", "baseline", "lineage-row"])
def test_a22_every_citation_path_marks_a_source_as_cited(root: Path, relative: str,
                                                         edit: Callable[[dict], None]) -> None:
    """A brand-new, otherwise-uncited source is cited through each provenance
    shape in turn; each one must silence `uncited-source` for it, proving the
    A22 traversal reaches every one of these shapes without a special case."""
    _add_uncited_source(root)
    baseline = _findings(_validate(root), "uncited-source")
    assert any(f.entity_id == _EXTRA_SOURCE_ID for f in baseline), \
        f"{_EXTRA_SOURCE_ID} must start out uncited for this test to mean anything"
    _mutate(root, relative, edit)
    findings = _findings(_validate(root), "uncited-source")
    assert not any(f.entity_id == _EXTRA_SOURCE_ID for f in findings)


# ---------------------------------------------------------------------------
# Validator defect (e): the CLI exit code.
# ---------------------------------------------------------------------------

def test_cli_exits_non_zero_when_there_are_errors(root: Path) -> None:
    _dangling_reference(root)
    assert v.main(["--data", str(root)]) == 1


def test_cli_strict_mode_fails_on_warnings_alone(root: Path) -> None:
    _mutate(root, "experiments/demo.json",
            lambda r: r["intervals"].append({
                "label": "gap-warning", "status": "active", "kind": "lifecycle",
                "start": None, "end": None, "sources": ["src:demo-experiment-site"],
                "verified_at": "2026-09-16", "confidence": "verified", "note": "",
            }))
    assert v.main(["--data", str(root)]) == 0
    assert v.main(["--data", str(root), "--strict"]) == 1


# ---------------------------------------------------------------------------
# Second review wave, against the live research data (four more defects).
# ---------------------------------------------------------------------------

# --- (1) A10's amended reading: status vs. a terminal interval already
#     reached, not the raw (and by then necessarily absent) derived state. ---

def _add_terminal_interval(r: dict, *, start: str = "2020", end: str | None = "2020",
                           confidence: str = "verified", note: str = "") -> None:
    r["intervals"].append({
        "label": "decommissioned", "status": "decommissioned", "kind": "lifecycle",
        "start": start, "end": end, "sources": ["src:demo-experiment-site"],
        "verified_at": "2026-09-16", "confidence": confidence, "note": note,
    })


def test_a10_status_matches_a_terminal_interval_already_reached(root: Path) -> None:
    """A3: the existence hull ends at the terminal interval's start, so
    `state_at` at the build date legitimately answers "absent" (None) for a
    decommissioned entity.  A10 must compare `status` against the terminal
    interval's own status in that case, not against that `None`."""
    def edit(r: dict) -> None:
        _add_terminal_interval(r)
        r["status"] = "decommissioned"
    _mutate(root, "experiments/demo.json", edit)
    findings = _validate(root)
    assert not _findings(findings, "status-not-derived-state")


def test_a10_status_still_errors_when_it_disagrees_with_the_reached_terminal_status(root: Path) -> None:
    def edit(r: dict) -> None:
        _add_terminal_interval(r)
        # `status` left at "active": wrong once the terminal event has passed.
    _mutate(root, "experiments/demo.json", edit)
    findings = _validate(root)
    matches = _findings(findings, "status-not-derived-state")
    assert matches and all(finding.level == v.ERROR for finding in matches)
    assert any("decommissioned" in finding.message for finding in matches)


def test_a10_a_future_terminal_interval_does_not_yet_override_the_derived_state(root: Path) -> None:
    """A terminal interval whose start has not happened yet (relative to the
    build date) must not pre-empt A10's comparison — `status` is still
    checked against the ordinary current derived state."""
    def edit(r: dict) -> None:
        _add_terminal_interval(r, start="2030", end=None, confidence="uncertain",
                               note="future decommissioning; exact date not yet fixed")
        r["status"] = "decommissioned"
    _mutate(root, "experiments/demo.json", edit)
    findings = _validate(root)
    matches = _findings(findings, "status-not-derived-state")
    assert matches, ("a not-yet-reached terminal interval must not excuse `status` from matching "
                     "the ordinary derived state")


# --- (2) display_magnitude's parsing bugs, at the validator level (the unit
#     tests for the function itself live in test_atlas_schema.py). ---

def test_a21_display_parsing_fix_stops_flagging_correct_data(root: Path) -> None:
    def edit(r: dict) -> None:
        r["specs"]["circumference"]["value"] = 3300
        r["specs"]["circumference"]["unit"] = "m"
        r["specs"]["circumference"]["display"] = "3 300 m"       # space-grouped thousands
    _mutate(root, "accelerators/demo-synchrotron.json", edit)
    findings = _validate(root)
    assert not _findings(findings, "display-value-mismatch")
    assert not _findings(findings, "display-value-drift")


def test_a21_display_parsing_still_catches_a_real_mismatch(root: Path) -> None:
    """The fix must not turn the check into a no-op: a display that genuinely
    disagrees with `value`, once correctly parsed, still errors."""
    def edit(r: dict) -> None:
        r["specs"]["circumference"]["value"] = 3300
        r["specs"]["circumference"]["unit"] = "m"
        r["specs"]["circumference"]["display"] = "330 000 m"     # a real factor-100 disagreement
    _mutate(root, "accelerators/demo-synchrotron.json", edit)
    findings = _validate(root)
    matches = _findings(findings, "display-value-mismatch")
    assert matches and all(finding.level == v.ERROR for finding in matches)


# --- (3) `part_of` excuses a chapter/volume from sharing its container's DOI. ---

def test_a20_duplicate_source_url_still_errors_without_part_of(root: Path) -> None:
    _mutate(root, "sources/demo-result-paper.json",
            lambda r: r["reference"].__setitem__("doi", "10.0000/demo-tdr"))
    findings = _validate(root)
    matches = _findings(findings, "duplicate-source-url")
    assert matches and all(finding.level == v.ERROR for finding in matches)


def test_a20_part_of_excuses_a_shared_doi_from_its_container(root: Path) -> None:
    def edit(r: dict) -> None:
        r["reference"]["doi"] = "10.0000/demo-tdr"
        r["part_of"] = "src:demo-tdr"
    _mutate(root, "sources/demo-result-paper.json", edit)
    findings = _validate(root)
    assert not _findings(findings, "duplicate-source-url")


def test_a20_part_of_pointing_nowhere_is_still_a_dangling_reference(root: Path) -> None:
    _mutate(root, "sources/demo-result-paper.json",
            lambda r: r.__setitem__("part_of", "src:does-not-exist"))
    findings = _validate(root)
    assert _findings(findings, "dangling-reference")


# --- (4) alias-equals-name says what to do about it. ---

def test_alias_equals_name_message_tells_the_author_what_to_do(root: Path) -> None:
    _mutate(root, "experiments/demo.json", lambda r: r["aliases"].append("Demo Experiment"))
    findings = _validate(root)
    matches = _findings(findings, "alias-equals-name")
    assert matches
    assert all("remove this alias" in finding.message
               and "case or punctuation" in finding.message for finding in matches)


# ---------------------------------------------------------------------------
# Third review wave, against real research-data volume (two more defects).
# ---------------------------------------------------------------------------

# --- (1) A3 supersedes §4: a terminal interval's `end` is optional; only an
#     `end` earlier than `start` is an error. ---

def test_a3_a_terminal_interval_with_no_end_is_not_an_error(root: Path) -> None:
    """The LEP detectors' `completed` event in November 2000 has no `end`,
    and A3 says that is fine: "Terminal statuses are events: `end` is
    optional." The withdrawn §4 sentence required one; it must not fire."""
    def edit(r: dict) -> None:
        r["intervals"].append({
            "label": "completed", "status": "completed", "kind": "lifecycle",
            "start": "2020", "end": None, "sources": ["src:demo-experiment-site"],
            "verified_at": "2026-09-16", "confidence": "verified", "note": "",
        })
    _mutate(root, "experiments/demo.json", edit)
    findings = _validate(root)
    assert not _findings(findings, "terminal-interval-without-end")
    assert "terminal-interval-without-end" not in {finding.rule for finding in findings}


def test_a3_a_terminal_intervals_end_before_its_start_is_still_an_error(root: Path) -> None:
    """A3's actual requirement — `end`, when given, must not precede
    `start` — must still be enforced, just under the general rule that
    already exists for every interval."""
    def edit(r: dict) -> None:
        r["intervals"].append({
            "label": "completed", "status": "completed", "kind": "lifecycle",
            "start": "2020", "end": "2015", "sources": ["src:demo-experiment-site"],
            "verified_at": "2026-09-16", "confidence": "verified", "note": "",
        })
    _mutate(root, "experiments/demo.json", edit)
    findings = _validate(root)
    matches = _findings(findings, "interval-end-before-start")
    assert matches and all(finding.level == v.ERROR for finding in matches)


def test_terminal_interval_without_end_rule_no_longer_exists() -> None:
    """The rule itself is gone, not merely silenced by an excuse clause."""
    source = Path(v.__file__).read_text(encoding="utf-8")
    assert "terminal-interval-without-end" not in source


# --- (2) duplicate-name: name-vs-name real, alias-vs-alias only
#     informational, short aliases (initialisms) ignored entirely. ---

def _write_institution(root: Path, slug: str, name: str, aliases: list[str]) -> None:
    template = _read(root, "institutions/demo-lab.json")
    template.update(id=f"institution:{slug}", name=name, aliases=aliases,
                    external={}, facility_id=None)
    _write(root, f"institutions/{slug}.json", template)


def test_a20_short_acronym_aliases_are_ignored_entirely(root: Path) -> None:
    """"CU" is shared by Chulalongkorn, Columbia and Cornell in the real
    data; none of that is a real duplicate, and it must not even be an
    informational finding."""
    _write_institution(root, "columbia-test", "Columbia Test University", ["CU"])
    _write_institution(root, "cornell-test", "Cornell Test University", ["CU"])
    _write_institution(root, "chulalongkorn-test", "Chulalongkorn Test University", ["CU"])
    findings = _validate(root)
    assert not _findings(findings, "duplicate-name")
    assert not _findings(findings, "duplicate-alias-across-records")


def test_a20_name_vs_name_collision_is_still_an_error(root: Path) -> None:
    _write_institution(root, "iowa-state-a", "Duplicate State University", [])
    _write_institution(root, "iowa-state-b", "Duplicate State University", [])
    findings = _validate(root)
    matches = _findings(findings, "duplicate-name")
    assert matches and all(finding.level == v.ERROR for finding in matches)


def test_a20_name_vs_long_alias_collision_is_still_an_error(root: Path) -> None:
    """"Super-K" duplicating "Super-Kamiokande": a long alias that is
    literally another record's name is exactly the kind of collision A20
    means to keep catching."""
    _write_institution(root, "superk-real", "Super-Kamiokande Test Institute", [])
    _write_institution(root, "superk-impostor", "An Unrelated Institute",
                        ["Super-Kamiokande Test Institute"])
    findings = _validate(root)
    matches = _findings(findings, "duplicate-name")
    assert matches and all(finding.level == v.ERROR for finding in matches)
    assert any(finding.entity_id == "institution:superk-impostor" for finding in matches)


def test_a20_long_alias_vs_long_alias_only_is_informational(root: Path) -> None:
    """Two records that merely share a long shorthand — neither's own
    name — is not build-failing; it is a note for a human to check."""
    _write_institution(root, "alias-holder-a", "Alias Holder Institute A", ["Shorthandalias"])
    _write_institution(root, "alias-holder-b", "Alias Holder Institute B", ["Shorthandalias"])
    findings = _validate(root)
    assert not _findings(findings, "duplicate-name")
    matches = _findings(findings, "duplicate-alias-across-records")
    assert matches and all(finding.level == v.INFO for finding in matches)


def test_a20_distinct_from_excuses_a_genuine_name_collision(root: Path) -> None:
    def edit(a: dict) -> None:
        a["distinct_from"] = ["institution:iowa-state-b"]

    def edit_b(b: dict) -> None:
        b["distinct_from"] = ["institution:iowa-state-a"]

    _write_institution(root, "iowa-state-a", "Distinct State University", [])
    _write_institution(root, "iowa-state-b", "Distinct State University", [])
    _mutate(root, "institutions/iowa-state-a.json", edit)
    _mutate(root, "institutions/iowa-state-b.json", edit_b)
    findings = _validate(root)
    assert not _findings(findings, "duplicate-name")
