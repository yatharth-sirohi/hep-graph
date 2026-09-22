"""Tests for the manual HEP Atlas tools: the link checker, the scaffold and
the OpenStreetMap extractor.

No test here touches the network: `linkcheck.run` takes injectable `fetch`
and `sleep` callables precisely so this suite can drive the whole pipeline
offline and instantly, and `atlas_osm_extract` is driven from a saved
Overpass response.
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


# ---------------------------------------------------------------------------
# scripts/atlas_osm_extract.py — the A25 maintainer helper
#
# Driven from a saved Overpass response: the script issues exactly one network
# request in real use and none at all here.
# ---------------------------------------------------------------------------

import importlib.util
import sys as _sys

_SPEC = importlib.util.spec_from_file_location(
    "atlas_osm_extract",
    Path(__file__).resolve().parents[1] / "scripts" / "atlas_osm_extract.py")
osm_extract = importlib.util.module_from_spec(_SPEC)
_sys.modules["atlas_osm_extract"] = osm_extract
_SPEC.loader.exec_module(osm_extract)


OVERPASS_RESPONSE = {
    "version": 0.6,
    "generator": "Overpass API",
    "osm3s": {"timestamp_osm_base": "2026-09-18T12:00:00Z"},
    "elements": [
        {"type": "way", "id": 123456789,
         "tags": {"building": "industrial", "name": "Target Hall"},
         "geometry": [{"lat": 41.8310, "lon": -88.2530}, {"lat": 41.8310, "lon": -88.2523},
                      {"lat": 41.8314, "lon": -88.2523}, {"lat": 41.8314, "lon": -88.2530},
                      {"lat": 41.8310, "lon": -88.2530}]},
        {"type": "way", "id": 987654321, "tags": {"highway": "service", "name": "Ring Road"},
         "geometry": [{"lat": 41.8300, "lon": -88.2540}, {"lat": 41.8340, "lon": -88.2500}]},
        {"type": "way", "id": 7, "tags": {}, "geometry": [{"lat": 41.8, "lon": -88.2}]},
    ],
}


def _drafts(tmp_path: Path) -> tuple[list[dict], list[dict], list[str]]:
    return osm_extract.process(OVERPASS_RESPONSE, map_slug="demo-lab",
                               level_id="surface", today="2026-09-18")


def test_the_query_is_one_request_with_a_timeout() -> None:
    query = osm_extract.build_query(bbox="41.82,-88.27,41.85,-88.23",
                                    filters=['way["building"]'], ids=[])
    assert query.count("out ") == 1
    assert f"timeout:{osm_extract.TIMEOUT_S}" in query
    assert 'way["building"](41.82,-88.27,41.85,-88.23);' in query


def test_explicit_ids_replace_the_bounding_box() -> None:
    query = osm_extract.build_query(bbox=None, filters=[],
                                    ids=["relation/9512017", "way/123"])
    assert "relation(9512017);" in query and "way(123);" in query


def test_the_user_agent_identifies_the_project() -> None:
    assert osm_extract.USER_AGENT == "HEP-Atlas-research/1.0"


def test_a_closed_building_way_becomes_a_polygon(tmp_path: Path) -> None:
    geometries, _sources, _lines = _drafts(tmp_path)
    hall = next(record for record in geometries if "123456789" in record["id"])
    assert hall["geometry"]["value"]["type"] == "Polygon"
    assert hall["feature_type"] == "building"


def test_an_open_way_becomes_a_line(tmp_path: Path) -> None:
    geometries, _sources, _lines = _drafts(tmp_path)
    road = next(record for record in geometries if "987654321" in record["id"])
    assert road["geometry"]["value"]["type"] == "LineString"
    assert road["feature_type"] == "road"


def test_an_element_without_usable_geometry_is_skipped_not_invented(tmp_path: Path) -> None:
    geometries, _sources, lines = _drafts(tmp_path)
    assert not any("way/7" in record["id"] for record in geometries)
    assert any("skipped way/7" in line for line in lines)


def test_every_draft_carries_the_odbl_licence_and_its_elements(tmp_path: Path) -> None:
    geometries, _sources, _lines = _drafts(tmp_path)
    for record in geometries:
        assert record["license"]["name"] == schema.ODBL_LICENSE_NAME
        assert record["license"]["attribution"] == schema.OSM_ATTRIBUTION
        assert record["osm"]["elements"]
        assert record["osm"]["timestamp"] == "2026-09-18T12:00:00Z"
        assert record["geometry"]["locator"].startswith("OSM ")


def test_no_draft_can_claim_to_be_verified(tmp_path: Path) -> None:
    """OpenStreetMap is rank 11; a draft that said `verified` would be a lie."""
    geometries, sources, _lines = _drafts(tmp_path)
    for record in geometries:
        assert record["geometry"]["confidence"] == "approximate"
        assert record["checks"] == []
    for source in sources:
        assert source["source_type"] == "openstreetmap"
        assert schema.source_rank(source["source_type"]) > schema.VERIFIED_MAX_RANK


def test_every_draft_says_what_is_still_missing(tmp_path: Path) -> None:
    geometries, _sources, _lines = _drafts(tmp_path)
    for record in geometries:
        assert any("DRAFT" in note for note in record["notes"])
        assert "TODO" in record["summary"]["plain"] or "TODO" in record["method"]


def test_the_report_prints_a_measurement_per_shape(tmp_path: Path) -> None:
    """The researcher compares these with the official figure; the script never
    writes the `checks[]` row itself."""
    _geometries, _sources, lines = _drafts(tmp_path)
    hall = next(line for line in lines if "way/123456789" in line)
    assert "perimeter" in hall and "area" in hall
    road = next(line for line in lines if "way/987654321" in line)
    assert "length" in road


def test_the_drafts_are_valid_records_the_validator_can_read(tmp_path: Path) -> None:
    """A draft is incomplete, not malformed: it loads and validates as written."""
    from hepgraph.atlas import validate as v

    root = tmp_path / "atlas"
    shutil.copytree(FIXTURE, root)
    geometries, sources, _lines = _drafts(tmp_path)
    # The fixture already cites OSM way/123456789; a second source record for
    # the same URL is a real A20 duplicate, so that one draft source is dropped
    # and its feature is pointed at the source the fixture already has.
    duplicate = "src:osm-demo-lab-way-123456789"
    for record in geometries:
        if duplicate in record["sources"]:
            record["sources"] = ["src:demo-osm-extract"]
            record["geometry"]["sources"] = ["src:demo-osm-extract"]
        (root / "geometry" / f'{schema.filename_for(record["id"])}.json').write_text(
            dump_json(record), encoding="utf-8")
    for record in sources:
        if record["id"] == duplicate:
            continue
        (root / "sources" / f'{schema.filename_for(record["id"])}.json').write_text(
            dump_json(record), encoding="utf-8")

    atlas = load_atlas(root)
    assert atlas.problems == [], [str(problem) for problem in atlas.problems]
    errors = v.errors(v.validate_atlas(atlas, build_date="2026-09-18"))
    assert errors == [], [str(error) for error in errors]


def test_the_script_never_writes_into_data_atlas_by_default(tmp_path: Path) -> None:
    """`--write-data` is opt-in; a run with no destination uses a scratch dir."""
    response = tmp_path / "overpass.json"
    response.write_text(json.dumps(OVERPASS_RESPONSE), encoding="utf-8")
    out_dir = tmp_path / "scratch"
    assert osm_extract.main(["--map", "demo-lab", "--ids", "way/1",
                             "--from-json", str(response), "--out", str(out_dir)]) == 0
    assert sorted(path.name for path in (out_dir / "geometry").glob("*.json"))
    # The raw response is kept next to the drafts so a reviewer sees the input.
    assert (out_dir / "overpass-response.json").is_file()
