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
], ids=["interval", "quantity", "coordinates", "placement", "leadership", "membership-row", "claim"])
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
