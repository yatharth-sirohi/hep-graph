"""The HEP Atlas glossary (data/atlas/glossary/, `glossary.json`, js/glossary.js).

Every definition is a sourced claim: a plain definition, the verbatim quote it rests on,
a locator and a source record. These tests check the data (shape, sources, no
encyclopaedia), the validator rules, the bundle, and the matcher that decides which words
in a panel become buttons - in the browser's own regular-expression engine (node), against
the real summaries, so a pattern that would mark the wrong sense of a word fails here.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from hepgraph.atlas import load, schema, validate
from hepgraph.atlas.build import build

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = Path(__file__).parent / "fixtures" / "atlas_minimal"
GLOSSARY_JS = ROOT / "static" / "atlas" / "js" / "glossary.js"
ENCYCLOPAEDIAS = {"wikipedia", "wikidata", "secondary"}


@pytest.fixture(scope="module")
def atlas():
    return load.load_atlas()


def test_the_glossary_loads_without_problems(atlas) -> None:
    assert atlas.problems == []
    assert 20 <= len(atlas.glossary) <= 35, "the brief asks for about 20-30 terms"
    ids = [term["id"] for term in atlas.glossary]
    assert ids == sorted(ids) and len(set(ids)) == len(ids)


def test_every_term_is_a_sourced_definition(atlas) -> None:
    for term in atlas.glossary:
        where = term["id"]
        assert 1 <= len(term["definition"].split()) <= schema.GLOSSARY_DEFINITION_MAX_WORDS, where
        assert 0 < len(term["quote"]) <= schema.GLOSSARY_QUOTE_MAX_CHARS, where
        assert term["locator"].strip(), where
        assert term["confidence"] in schema.CONFIDENCES, where
        assert term["verified_at"] == "2026-10-26", where
        assert term["sources"], where
        for source_id in term["sources"]:
            source = atlas.get(source_id)
            assert source is not None, f"{where}: {source_id} is not a source record"
            assert source["source_type"] not in ENCYCLOPAEDIAS, f"{where} cites an encyclopaedia"
            assert schema.source_rank(source["source_type"]) <= schema.VERIFIED_MAX_RANK, where
            assert "wikipedia.org" not in source["url"], where


def test_the_validator_accepts_the_real_glossary(atlas) -> None:
    findings = validate.validate_atlas(atlas, build_date="2026-10-26")
    mine = [f for f in findings if f.rule.startswith("glossary")]
    assert mine == []
    glossary_sources = {s for term in atlas.glossary for s in term["sources"]}
    uncited = [f for f in findings if f.rule == "uncited-source" and f.entity_id in glossary_sources]
    assert uncited == [], "a glossary term's source counts as cited"


def _atlas_with(terms: list[dict]) -> load.Atlas:
    atlas = load.Atlas(root=Path("/nonexistent-atlas-root"))
    atlas.entities["source"]["src:ok"] = {
        "id": "src:ok", "type": "src", "source_type": "pdg", "retrieval": "full_text",
        "title": "A review", "url": "https://pdg.lbl.gov/x.pdf", "accessed": "2026-10-26",
    }
    atlas.entities["source"]["src:failed"] = {
        "id": "src:failed", "type": "src", "source_type": "pdg", "retrieval": "failed",
        "title": "Gone", "url": "https://pdg.lbl.gov/y.pdf", "accessed": "2026-10-26",
    }
    atlas.glossary = [{**term, "_file": "glossary/t.json"} for term in terms]
    return atlas


GOOD = {
    "id": "term-a", "term": "term a", "title": "Term A", "definition": "A plain definition.",
    "quote": "The page's own words.", "locator": "section 1", "sources": ["src:ok"],
    "confidence": "verified", "verified_at": "2026-10-26", "match": ["term a"],
}


def _rules(term: dict) -> set[str]:
    findings = validate.validate_atlas(_atlas_with([term]), build_date="2026-10-26")
    return {f.rule for f in findings if f.rule.startswith("glossary")}


def test_the_validator_flags_each_way_a_term_can_be_unsourced_or_unusable() -> None:
    assert _rules(GOOD) == set()
    assert "glossary-missing-field" in _rules({**GOOD, "quote": ""})
    assert "glossary-missing-field" in _rules({k: v for k, v in GOOD.items() if k != "locator"})
    assert "glossary-sources" in _rules({**GOOD, "sources": []})
    assert "glossary-sources" in _rules({**GOOD, "sources": ["src:missing"]})
    assert "glossary-sources" in _rules({**GOOD, "sources": ["src:failed"]})
    assert "glossary-definition-length" in _rules({**GOOD, "definition": "word " * 46})
    assert "glossary-quote-length" in _rules({**GOOD, "quote": "q" * 301})
    assert "glossary-confidence" in _rules({**GOOD, "confidence": "certain"})
    assert "glossary-match" in _rules({**GOOD, "match": []})
    assert "glossary-match" in _rules({**GOOD, "match": ["(unclosed"]})
    assert "glossary-match" in _rules({**GOOD, "match": ["(?<=\\d)x"]}), "look-behind is not portable"
    assert "glossary-id" in _rules({**GOOD, "id": "Not Kebab"})


def test_the_loader_reports_a_duplicate_or_malformed_term(tmp_path: Path) -> None:
    shutil.copytree(FIXTURE, tmp_path / "atlas")
    (tmp_path / "atlas" / "glossary").mkdir()
    (tmp_path / "atlas" / "glossary" / "a.json").write_text(json.dumps([GOOD, GOOD, "not an object"]))
    atlas = load.load_atlas(tmp_path / "atlas")
    messages = " ".join(str(problem) for problem in atlas.problems)
    assert "duplicate glossary term" in messages and "not an object" in messages
    assert len(atlas.glossary) == 1


def test_the_bundle_carries_each_term_with_its_source_and_is_left_out_when_empty(tmp_path: Path) -> None:
    plain = build(FIXTURE, tmp_path / "plain", build_date="2026-09-16")
    assert "glossary.json" not in plain.files and plain.errors == []

    shutil.copytree(FIXTURE, tmp_path / "data")
    source_id = next(iter(load.load_atlas(FIXTURE).entities["source"]))
    (tmp_path / "data" / "glossary").mkdir()
    (tmp_path / "data" / "glossary" / "terms.json").write_text(
        json.dumps([{**GOOD, "sources": [source_id]}]))
    result = build(tmp_path / "data", tmp_path / "out", build_date="2026-09-16")
    assert result.errors == []
    bundle = json.loads(result.files["glossary.json"])
    assert [term["id"] for term in bundle["terms"]] == ["term-a"]
    term = bundle["terms"][0]
    assert term["definition"] == GOOD["definition"] and term["quote"] == GOOD["quote"]
    assert term["source"]["id"] == source_id and term["source"]["url"]
    assert "_file" not in term
    assert "glossary.json" in json.loads(result.files["manifest.json"])["bundles"]


# --------------------------------------------------------------- the matcher
# Run in node, with the browser's regular-expression engine and the app's own
# matcher (static/atlas/js/glossary.js), on the real bundle's terms.
NODE = shutil.which("node")

HARNESS = """
import { compile, firstMatch } from %(module)r;
import fs from 'node:fs';
const terms = compile(JSON.parse(fs.readFileSync(%(terms)r, 'utf8')));
const texts = JSON.parse(fs.readFileSync(%(texts)r, 'utf8'));
const byId = Object.fromEntries(terms.map((t) => [t.id, t]));
const out = { compiled: terms.length, hits: {}, probes: [] };
for (const t of terms) out.hits[t.id] = 0;
for (const text of texts.corpus) for (const t of terms) if (firstMatch(t, text)) out.hits[t.id] += 1;
for (const [id, text] of texts.probes) {
  const m = byId[id] && firstMatch(byId[id], text);
  out.probes.push(m ? text.slice(m.index, m.index + m.length) : null);
}
console.log(JSON.stringify(out));
"""

# (term id, text, what a reader sees marked or None). Each is a sense of a word that
# the glossary does and does not define.
PROBES = [
    ("significance-sigma", "a signal significance above 5σ.", "5σ"),
    ("significance-sigma", "rejecting the hypothesis at 3.9σ, and more", "3.9σ"),
    ("significance-sigma", "the cross section σ_SI is limited", None),
    ("confidence-level", "set a limit at 90% C.L. for WIMPs", "90% C.L."),
    ("confidence-level", "an upper limit (95% CL).", "95% CL"),
    ("confidence-level", "the CL of the lighter circuit", None),
    ("metres-water-equivalent", "a depth of 6000 m.w.e. at SNOLAB", "m.w.e."),
    ("metres-water-equivalent", "about 2700 metres water equivalent", "metres water equivalent"),
    ("fiducial-volume", "a fiducial mass of 5.5 tonnes", "fiducial mass"),
    ("fiducial-volume", "a fiducial cross section of 78 pb", None),
    ("energy-threshold", "a low-energy-threshold run", "energy-threshold"),
    ("energy-threshold", "close to the D0 D*0 threshold", None),
    ("synchrotron", "Super Proton Synchrotron ring", "Synchrotron"),
    ("synchrotron", "a synchrotron radiation source", None),
    ("cherenkov-light", "a water-Cherenkov detector", "Cherenkov"),
    ("cherenkov-light", "the Cherenkov Telescope Array", None),
    ("baseline", "long-baseline neutrino oscillation", "baseline"),
    ("baseline", "baselines of 470 m and 576 m", "baselines"),
    ("neutrino-oscillation", "a fourth neutrino oscillations search", "oscillations"),
    ("time-projection-chamber", "a dual-phase TPC and a liquid xenon TPCs", "TPC"),
    ("wimp", "heavy WIMPs, not wimps", "WIMPs"),
    ("cevns", "CEvNS and CEνNS are the same", "CEvNS"),
    ("neutrinoless-double-beta-decay", "0νββ searches", "0νββ"),
    ("calorimeter", "a hadronic calorimeter and calorimetry", "calorimeter"),
    ("sterile-neutrino", "light sterile neutrinos", "sterile neutrinos"),
    ("centre-of-mass-energy", "collisions at √s = 13 TeV", "√s"),
    ("luminosity", "an integrated luminosity of 140 fb-1", "integrated luminosity"),
    ("off-axis-angle", "the off-axis angle is 2.5°", "off-axis angle"),
    ("nuclear-recoil", "nuclear recoils from neutrons", "nuclear recoils"),
]


def _corpus(atlas) -> list[str]:
    texts: list[str] = []
    for _type, _id, record in atlas.iter_entities():
        summary = record.get("summary")
        if isinstance(summary, dict):
            texts.extend(value for value in (summary.get("plain"), summary.get("technical")) if isinstance(value, str))
    return texts


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_the_matcher_marks_each_term_in_real_text_and_not_its_other_senses(atlas, tmp_path: Path) -> None:
    terms = [{"id": t["id"], "match": t["match"]} for t in atlas.glossary]
    (tmp_path / "terms.json").write_text(json.dumps(terms))
    (tmp_path / "texts.json").write_text(json.dumps({
        "corpus": _corpus(atlas), "probes": [[term_id, text] for term_id, text, _ in PROBES]}))
    script = tmp_path / "check.mjs"
    script.write_text(HARNESS % {
        "module": GLOSSARY_JS.as_uri(), "terms": str(tmp_path / "terms.json"), "texts": str(tmp_path / "texts.json")})
    run = subprocess.run([NODE, str(script)], capture_output=True, text=True, timeout=60)
    assert run.returncode == 0, run.stderr
    result = json.loads(run.stdout)
    assert result["compiled"] == len(terms), "every term compiles in the browser's engine"
    dead = [term_id for term_id, count in result["hits"].items() if count == 0]
    assert dead == [], f"terms no summary in the Atlas uses (a dead glossary entry): {dead}"
    for (term_id, text, expected), actual in zip(PROBES, result["probes"]):
        assert actual == expected, f"{term_id!r} in {text!r}: marked {actual!r}, expected {expected!r}"
