"""Tests for the two manual HEP Atlas tools: the link checker and the scaffold.

Neither test touches the network: `linkcheck.run` takes injectable `fetch`
and `sleep` callables precisely so this suite can drive the whole pipeline
offline and instantly.
"""

from __future__ import annotations

import datetime as dt
import json
import shutil
from pathlib import Path

import pytest

from hepgraph.atlas import linkcheck, scaffold, schema
from hepgraph.atlas.load import dump_json, load_atlas

FIXTURE = Path(__file__).parent / "fixtures" / "atlas_minimal"
TODAY = dt.date(2026, 9, 16)


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    root = tmp_path / "atlas"
    shutil.copytree(FIXTURE, root)
    return root


def _source(data_dir: Path, slug: str) -> dict:
    return json.loads((data_dir / "sources" / f"{slug}.json").read_text(encoding="utf-8"))


# --------------------------------------------------------------- linkcheck --

def test_selection_is_sorted_and_limited(data_dir: Path) -> None:
    atlas = load_atlas(data_dir)
    chosen = linkcheck.select_sources(atlas, today=TODAY)
    assert [source_id for source_id, _ in chosen] == sorted(atlas.by_type("source"))
    assert len(linkcheck.select_sources(atlas, limit=3, today=TODAY)) == 3
    assert linkcheck.select_sources(atlas, limit=0, today=TODAY) == []


def test_only_stale_skips_recently_checked_sources(data_dir: Path) -> None:
    path = data_dir / "sources" / "demo-tdr.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    record["link_check"]["last_checked"] = "2026-09-10"
    path.write_text(dump_json(record), encoding="utf-8")

    atlas = load_atlas(data_dir)
    stale = {source_id for source_id, _ in linkcheck.select_sources(atlas, only_stale=30, today=TODAY)}
    assert "src:demo-tdr" not in stale, "checked 6 days ago, so not stale at 30 days"
    assert "src:demo-experiment-site" in stale, "never checked, so always stale"

    fresh = {source_id for source_id, _ in linkcheck.select_sources(atlas, only_stale=5, today=TODAY)}
    assert "src:demo-tdr" in fresh, "checked 6 days ago, so stale at 5 days"


def test_results_are_written_back_into_the_source_files(data_dir: Path) -> None:
    def fetch(url: str) -> linkcheck.CheckResult:
        return linkcheck.CheckResult(url=url, http_status=200, redirect=None,
                                     content_hash="0123456789abcdef")

    report = linkcheck.run(data_dir, fetch=fetch, sleep=lambda _seconds: None, today=TODAY)
    # Counted from the fixture rather than typed: every source record is
    # checked and rewritten, and the fixture gains sources as the atlas does.
    source_count = len(list((data_dir / "sources").glob("*.json")))
    assert len(report.checked) == source_count
    assert report.failures == []
    assert len(report.written) == source_count

    record = _source(data_dir, "demo-tdr")
    assert record["link_check"] == {"last_checked": "2026-09-16", "http_status": 200,
                                    "redirect": None}
    assert record["content_hash"] == "0123456789abcdef"
    # A11: the rewritten file is still canonical JSON, so the diff stays reviewable.
    text = (data_dir / "sources" / "demo-tdr.json").read_text(encoding="utf-8")
    assert text == dump_json(json.loads(text))
    # The rewrite must not leak the loader's in-memory bookkeeping.
    assert not any(key.startswith("_") for key in record)


def test_redirects_and_errors_are_recorded_but_never_fatal(data_dir: Path) -> None:
    def fetch(url: str) -> linkcheck.CheckResult:
        if "institutions" in url:
            return linkcheck.CheckResult(url=url, http_status=301,
                                         redirect=url + "/current")
        if "demo-result" in url:
            return linkcheck.CheckResult(url=url, http_status=503, error="HTTP 503 Service Unavailable")
        if "demo-tdr" in url:
            return linkcheck.CheckResult(url=url, http_status=404, error="HTTP 404 Not Found")
        if "inspirehep" in url:
            return linkcheck.CheckResult(url=url, error="URLError: timed out")
        return linkcheck.CheckResult(url=url, http_status=200)

    report = linkcheck.run(data_dir, fetch=fetch, sleep=lambda _seconds: None, today=TODAY)
    statuses = {source_id: result.http_status for source_id, result in report.checked}
    assert statuses["src:demo-institution-list"] == 301
    assert statuses["src:demo-result-paper"] == 503
    assert statuses["src:demo-inspire-experiment"] is None

    # A22: only 404/410 land on the "review required" list; a 5xx does not.
    review = {source_id for source_id, _ in report.review_required}
    assert review == {"src:demo-tdr"}
    assert {source_id for source_id, _ in report.failures} == {
        "src:demo-result-paper", "src:demo-tdr", "src:demo-inspire-experiment"}

    redirected = _source(data_dir, "demo-institution-list")
    assert redirected["link_check"]["redirect"].endswith("/current")
    timed_out = _source(data_dir, "demo-inspire-experiment")
    assert timed_out["link_check"]["error"] == "URLError: timed out"
    assert "content_hash" not in timed_out

    report_text = linkcheck.format_report(report)
    assert "review required" in report_text
    assert "never fatal" in report_text


def test_a18_a_failed_retrieval_is_skipped_not_checked(data_dir: Path) -> None:
    path = data_dir / "sources" / "demo-tdr.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    record["retrieval"] = "failed"
    path.write_text(dump_json(record), encoding="utf-8")

    calls: list[str] = []

    def fetch(url: str) -> linkcheck.CheckResult:
        calls.append(url)
        return linkcheck.CheckResult(url=url, http_status=200)

    report = linkcheck.run(data_dir, fetch=fetch, sleep=lambda _s: None, today=TODAY)
    assert [source_id for source_id, _ in report.skipped] == ["src:demo-tdr"]
    assert not any("demo-tdr" in url for url in calls)


def test_dry_run_writes_nothing_and_the_delay_is_never_below_one_second(data_dir: Path) -> None:
    before = {path: path.read_bytes() for path in sorted(data_dir.rglob("*.json"))}
    slept: list[float] = []
    report = linkcheck.run(data_dir, fetch=lambda url: linkcheck.CheckResult(url=url, http_status=200),
                           sleep=slept.append, delay=0.0, dry_run=True, today=TODAY)
    assert report.written == []
    assert {path: path.read_bytes() for path in sorted(data_dir.rglob("*.json"))} == before
    # One sleep between each pair of requests, never faster than a second.
    assert len(slept) == len(report.checked) - 1
    assert slept and min(slept) >= linkcheck.MIN_DELAY_SECONDS


def test_cli_returns_zero_even_when_every_url_fails(data_dir: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(linkcheck, "check_url",
                        lambda url, **kwargs: linkcheck.CheckResult(url=url, http_status=500))
    assert linkcheck.main(["--data", str(data_dir), "--limit", "2"]) == 0
    assert "2 source(s)" in capsys.readouterr().out
    assert linkcheck.main(["--data", str(data_dir / "missing")]) == 1


# ---------------------------------------------------------------- scaffold --

def test_scaffold_writes_v02_skeletons(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    written = scaffold.scaffold_experiment(
        root, "demo2", facility="demo-lab-2", collaboration="demo2", site="demo-cavern-2",
        owner="neutrino-lead", today=TODAY)

    assert set(written) == {
        "sources/demo2-official-site.json",
        "experiments/demo2.json",
        "collaborations/demo2.json",
        "memberships/demo2.json",
        "facilities/demo-lab-2.json",
        "sites/demo-cavern-2.json",
        "coverage/neutrino-lead.json",
    }
    for relative, text in written.items():
        assert (root / relative).read_text(encoding="utf-8") == text
        assert text == dump_json(json.loads(text)), f"{relative} is not canonical JSON (A11)"

    experiment = json.loads((root / "experiments" / "demo2.json").read_text(encoding="utf-8"))
    assert experiment["schema"] == schema.SCHEMA_TAG
    assert experiment["id"] == "experiment:demo2"
    # A2: the v0.2 canonical relation, not the retired `facility_ids`.
    assert "facility_ids" not in experiment
    assert experiment["facility_roles"][0] == {
        "facility_id": "facility:demo-lab-2", "role": "host", "start": None, "end": None,
        "sources": ["src:demo2-official-site"], "verified_at": None,
        "confidence": "uncertain", "note": scaffold.TODO_NOTE}
    # A1: no derived field is authored.
    for field in schema.DERIVED_FIELDS["experiment"]:
        assert field not in experiment
    # A17: nothing is invented.
    assert experiment["status"] is None and experiment["intervals"] == []

    site = json.loads((root / "sites" / "demo-cavern-2.json").read_text(encoding="utf-8"))
    assert site["coordinates"] is None, "the scaffold must not invent coordinates"

    roster = json.loads((root / "memberships" / "demo2.json").read_text(encoding="utf-8"))
    assert roster["membership_history"] == "unknown"      # A5
    assert "default_evidence_class" not in roster          # A19
    assert roster["members"] == []

    stub = json.loads((root / "sources" / "demo2-official-site.json").read_text(encoding="utf-8"))
    assert stub["type"] == schema.SOURCE_TYPE_FIELD_VALUE   # A7: "src"
    assert scaffold.PLACEHOLDER_HOST in stub["url"]
    assert stub["accessed"] == TODAY.isoformat()            # A18

    rows = json.loads((root / "coverage" / "neutrino-lead.json").read_text(encoding="utf-8"))
    assert rows[0]["entity_id"] == "experiment:demo2"
    assert rows[0]["researched"] == "none"
    # A10: these are build outputs, not registry fields.
    assert "validated" not in rows[0] and "globe_ready" not in rows[0]


def test_scaffold_loads_without_file_level_problems(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    scaffold.scaffold_experiment(root, "demo2", facility="demo-lab-2",
                                 collaboration="demo2", today=TODAY)
    atlas = load_atlas(root)
    assert atlas.problems == [], [str(problem) for problem in atlas.problems]
    assert atlas.get("experiment:demo2") is not None
    assert atlas.coverage[0]["entity_id"] == "experiment:demo2"


def test_scaffold_never_clobbers_existing_files_without_force(data_dir: Path) -> None:
    before = (data_dir / "experiments" / "demo.json").read_bytes()
    written = scaffold.scaffold_experiment(data_dir, "demo", facility="demo-lab",
                                           collaboration="demo", today=TODAY)
    assert "experiments/demo.json" not in written
    assert (data_dir / "experiments" / "demo.json").read_bytes() == before

    forced = scaffold.scaffold_experiment(data_dir, "demo", facility="demo-lab",
                                          collaboration="demo", force=True, today=TODAY)
    assert "experiments/demo.json" in forced
    assert (data_dir / "experiments" / "demo.json").read_bytes() != before


def test_scaffold_appends_to_an_existing_coverage_file_without_duplicating(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    scaffold.scaffold_experiment(root, "alpha", facility="lab", collaboration="alpha",
                                 owner="team", priority=2, today=TODAY)
    scaffold.scaffold_experiment(root, "beta", facility="lab", collaboration="beta",
                                 owner="team", priority=1, today=TODAY)
    rows = json.loads((root / "coverage" / "team.json").read_text(encoding="utf-8"))
    assert [row["entity_id"] for row in rows] == ["experiment:beta", "experiment:alpha"]

    scaffold.scaffold_experiment(root, "alpha", facility="lab", collaboration="alpha",
                                 owner="team", priority=2, today=TODAY)
    rows = json.loads((root / "coverage" / "team.json").read_text(encoding="utf-8"))
    assert len(rows) == 2, "re-scaffolding must not duplicate the registry row"


def test_scaffold_cli(tmp_path: Path, capsys) -> None:
    root = tmp_path / "atlas"
    assert scaffold.main(["--data", str(root), "experiment", "demo2",
                          "--facility", "demo-lab-2", "--collaboration", "demo2",
                          "--dry-run"]) == 0
    assert not root.exists(), "--dry-run must not touch the filesystem"
    assert "would write" in capsys.readouterr().out

    assert scaffold.main(["--data", str(root), "experiment", "demo2",
                          "--facility", "demo-lab-2", "--collaboration", "demo2"]) == 0
    assert (root / "experiments" / "demo2.json").is_file()

    assert scaffold.main(["--data", str(root), "experiment", "Not A Slug",
                          "--facility", "f", "--collaboration", "c"]) == 2
