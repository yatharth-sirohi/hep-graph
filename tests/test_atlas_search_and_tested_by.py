"""Unit checks for the search ranking and for "Tested by", on the real records (no browser).

  * a typed word matches at the start of a word, never from the middle of one ("libra" is
    DAMA/LIBRA, not "calibration"), and a typed phrase matches a name with simple plurals
    folded ("neutrino oscillation" is the topic "Neutrino oscillations", which comes first);
  * a result that states a claim (DAMA/LIBRA's 11.8 and 13.7 sigma) lists the results of the
    experiments recorded as complementary to its own, and of the experiments whose text names it,
    and never its own experiment's or collaboration's, nor a technology milestone.

The browser modules run under Node (skipped when Node is not installed). Nothing is fetched or written.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static" / "atlas"
JS = STATIC / "js"
DATA = ROOT / "data" / "atlas"
NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(NODE is None, reason="node is not installed")

NODE_SCRIPT = r"""
import fs from 'node:fs';
const js = process.argv[1];
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const rank = await import(`${js}/searchrank.js`);
const tested = await import(`${js}/tested-by.js`);

const entries = input.search.entries.map(([type, id, name, aliases, subtitle]) => ({ type, id, name, aliases, subtitle }));
const resultList = Object.values(input.results).filter((r) => r && typeof r === 'object' && r.id);
const search = rank.createMatcher(entries, rank.buildRelatedTopics(input.atlas, resultList));
const names = (query, limit = 40) => search(query, limit).map((r) => r.entry.name);

const out = {};
out.libra = names('libra');
out.calibration = names('calibration');
out.singular = names('neutrino oscillation', 5);
out.plural = names('neutrino oscillations', 3);
out.across = names('superkam', 3);
out.atlas = names('atlas', 3);
out.nothing = names('zzzzqq');

const resultById = new Map(resultList.map((r) => [r.id, r]));
const by = (id) => tested.testedBy(resultById.get(id), { atlas: input.atlas, resultList, text: input.text });
const summary = (t) => t && {
  total: t.items.length,
  ids: t.items.map((i) => i.result.id),
  citing: t.items.filter((i) => i.cites).map((i) => i.result.id),
  experiments: t.experiments,
};
out.dama2021 = summary(by('result:dama-libra-phase2-further-results-2021'));
out.damaNai = summary(by('result:dama-nai-seven-annual-cycles-2003'));
out.higgs = summary(by('result:atlas-higgs-observation-2012'));
out.limit = summary(by('result:cosine-100-dama-constraints-2021'));
out.names = tested.citationNames(input.atlas.experiments['experiment:dama-libra']);
out.statesClaim = [
  tested.statesClaim({ result_type: 'limit', significance: null }),
  tested.statesClaim({ result_type: 'measurement', significance: '6.3 sigma' }),
  tested.statesClaim({ result_type: 'evidence' }),
];
console.log(JSON.stringify(out));
"""


@pytest.fixture(scope="module")
def out() -> dict:
    from hepgraph.atlas.build import build

    built = build(DATA, STATIC / "generated", check=True)
    payload = {
        "atlas": json.loads(built.files["atlas.json"]),
        "results": json.loads(built.files["results.json"]),
        "search": json.loads(built.files["search.json"]),
        "text": json.loads(built.files["text.json"]),
    }
    result = subprocess.run(
        [NODE, "--input-type=module", "-e", NODE_SCRIPT, str(JS)],
        input=json.dumps(payload), capture_output=True, text=True, check=True, timeout=120,
    )
    return json.loads(result.stdout)


def test_a_word_matches_at_the_start_of_a_word_not_from_its_middle(out: dict) -> None:
    assert out["libra"][0] == "DAMA/LIBRA"
    assert not any("alibration" in name for name in out["libra"]), "libra is not calibration"
    assert all("libra" in name.lower() or "DAMA" in name for name in out["libra"][:5])
    # Hyphens and spaces typed away still find the name.
    assert out["across"][0] == "Super-Kamiokande"
    assert out["atlas"][0] == "ATLAS"
    assert out["nothing"] == []


def test_a_typed_phrase_matches_a_name_with_simple_plurals_folded(out: dict) -> None:
    assert out["singular"][0] == "Neutrino oscillations"
    assert out["plural"][0] == "Neutrino oscillations"


def test_dama_libra_is_listed_with_the_results_that_test_it(out: dict) -> None:
    t = out["dama2021"]
    assert t is not None and t["total"] >= 10
    experiments = set(t["experiments"])
    # The experiments of the complementary lineage rows the brief names.
    assert {"experiment:anais-112", "experiment:cosine-100", "experiment:cdex-1"} <= experiments
    # Never its own experiment, its predecessor DAMA/NaI (same collaboration), or a technology milestone.
    assert not experiments & {"experiment:dama-libra", "experiment:dama-nai"}
    assert "result:cosinus-facility-dama-challenge-2025" not in t["ids"], "a plan for a first run tests nothing yet"
    assert "result:cosine-100-dama-constraints-2021" in t["ids"] and "result:cosine-100-dama-constraints-2021" in t["citing"]
    # Results whose own text names DAMA/LIBRA come before the others.
    first_other = next((i for i, rid in enumerate(t["ids"]) if rid not in t["citing"]), len(t["ids"]))
    assert all(rid in t["citing"] for rid in t["ids"][:first_other]) and set(t["ids"][first_other:]).isdisjoint(t["citing"])


def test_tested_by_is_only_for_a_claim_whose_experiment_has_complementary_rows(out: dict) -> None:
    assert out["limit"] is None, "an upper limit states no claim for others to test"
    assert out["higgs"] is None, "ATLAS records no complementary experiment, so nothing is listed"
    assert out["statesClaim"] == [False, True, True]
    assert "DAMA/LIBRA" in out["names"] and "DAMA" in out["names"] and "LIBRA" in out["names"]
