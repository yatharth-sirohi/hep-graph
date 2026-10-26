"""Unit check for "Follow the proton" (static/atlas/js/proton-chain.js).

The order of the stages is read from `feeds_accelerator_ids` filtered to the year (A30), never
written down. Run under Node on the atlas as the browser receives it (built in memory from
data/atlas; nothing is written): CERN's chain starts at Linac2 in 2015 and at Linac4 in 2021,
and has neither between them (Linac2 stopped in November 2018, Linac4 joined the PS Booster in
2020). Skipped when Node is not installed.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
JS = ROOT / "static" / "atlas" / "js"
NODE = shutil.which("node")

NODE_SCRIPT = r"""
import fs from 'node:fs';
const dir = process.argv[1];
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const chain = await import(`${dir}/proton-chain.js`);
const out = {};
for (const year of [1960, 2015, 2019, 2021]) {
  const result = chain.chainAt(input.atlas, 'facility:cern', year, input.bundle);
  out[year] = result.stages.map((stage) => `${stage.id.split(':')[1]}${stage.drawn ? '' : '*'}`);
}
console.log(JSON.stringify(out));
"""


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_cern_chain_follows_the_dated_feed_links() -> None:
    from hepgraph.atlas.build import build

    result = build(ROOT / "data" / "atlas", ROOT / "static" / "atlas" / "generated", check=True)
    payload = {
        "atlas": json.loads(result.files["atlas.json"]),
        "bundle": json.loads(result.files["geometry/cern.json"]),
    }
    run = subprocess.run(
        [NODE, "--input-type=module", "-e", NODE_SCRIPT, str(JS)],
        input=json.dumps(payload), capture_output=True, text=True, check=True, timeout=60,
    )
    out = json.loads(run.stdout)
    # `*` marks a stage the CERN map does not draw (Linac2 is listed as unlocated).
    assert out["2015"] == ["linac2*", "psb", "ps", "sps", "lhc"]
    assert out["2021"] == ["linac4", "psb", "ps", "sps", "lhc"]
    assert out["2019"] == ["psb", "ps", "sps", "lhc"]
    assert out["1960"] == []  # the PS alone is not a chain


def test_the_player_is_only_imported_when_a_map_opens() -> None:
    # Nothing loads until asked: localmap.js imports it dynamically, nothing statically.
    for path in JS.rglob("*.js"):
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"^import .* from '[^']*proton\.js'", text, re.M), path.name
    assert "import('./proton.js')" in (JS / "localmap.js").read_text(encoding="utf-8")
