"""Compare real plotted fluxes in common units; preserve scoped navigation."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which('node')
pytestmark = pytest.mark.skipif(not NODE, reason='Node is required for browser-module checks')


def node(script):
    result = subprocess.run([NODE, '--input-type=module', '-e', script], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


SETUP = """
import fs from 'node:fs';
import {undergroundRows} from './static/atlas/js/views/underground-rows.js';
import {normaliseFluxPair, compareFluxes, defaultFluxPair} from './static/atlas/js/views/underground-compare.js';
const atlas=JSON.parse(fs.readFileSync('static/atlas/generated/atlas.json','utf8'));
const rows=undergroundRows(atlas);
"""


def test_common_units_and_log_separation_use_the_actual_plotted_central_values():
    out = node(SETUP + """
const pair=defaultFluxPair(rows);const comparison=compareFluxes(rows,pair);
const reverse=compareFluxes(rows,[...pair].reverse());
const equalRows=[{...rows[0],id:'site:a',slug:'a',flux:2e-8},{...rows[1],id:'site:b',slug:'b',flux:2e-8}];
console.log(JSON.stringify({pair,comparison,reverse,equal:compareFluxes(equalRows,['a','b'])}));
""")
    assert out['pair'] == ['lngs-hall-c','snolab-underground-lab']
    c = out['comparison']
    assert c['a']['flux'] == pytest.approx(3.432e-8)
    assert c['b']['flux'] == pytest.approx(3.31e-10)
    assert c['ratio'] == pytest.approx(103.6858006042296)
    assert c['logRatio'] == pytest.approx(2.015719285400949)
    assert c['decades'] == pytest.approx(abs(c['logRatio']))
    assert out['reverse']['ratio'] == pytest.approx(1/c['ratio'])
    assert out['reverse']['logRatio'] == pytest.approx(-c['logRatio'])
    assert out['equal']['ratio'] == 1 and out['equal']['decades'] == 0


def test_invalid_missing_and_repeated_sites_cannot_produce_a_comparison():
    out = node(SETUP + """
const badRows=[{...rows[0],id:'site:a',slug:'a',flux:0},{...rows[1],id:'site:b',slug:'b',flux:Infinity}];
console.log(JSON.stringify({
 valid:[normaliseFluxPair('lngs-hall-c,snolab-underground-lab'),normaliseFluxPair(['a','b'])],
 invalid:['a','a,b,c','a/b,c','a,<script>',null,[],['a',{}]].map(normaliseFluxPair),
 rejected:[compareFluxes(rows,['missing','snolab-underground-lab']),compareFluxes(rows,['lngs-hall-c','lngs-hall-c']),compareFluxes(badRows,['a','b'])],
 fallback:defaultFluxPair(rows.slice(0,2)),tooFew:defaultFluxPair(rows.slice(0,1))}));
""")
    assert out['valid'] == [['lngs-hall-c','snolab-underground-lab'],['a','b']]
    assert out['invalid'] == [None]*7 and out['rejected'] == [None]*3
    assert len(set(out['fallback'])) == 2 and out['tooFew'] is None


def test_comparison_urls_roundtrip_in_the_view_and_tour_then_clear_for_results():
    out = node("""
globalThis.window={location:new URL('http://atlas.test/atlas?data=generated&theme=projector&uf=lngs-hall-c,snolab-underground-lab#/view/underground'),addEventListener(){},
 history:{replaceState(s,_,u){window.location=new URL(u,window.location)},pushState(s,_,u){window.location=new URL(u,window.location)}}};
const state=await import('./static/atlas/js/state.js');const initial=state.init();
state.navigate({undergroundPair:['lsm-frejus','snolab-underground-lab']});const changed=window.location.href;
state.navigate({entity:{type:'tour',slug:'going-underground-dark-matter'},step:6});const tour=window.location.href;
const patch=state.patchFromLink('?uf=snolab-underground-lab,lngs-hall-c&step=6#/tour/going-underground-dark-matter');
state.navigate({entity:{type:'result',slug:'atlas-higgs-observation-2012'}});const cleared=state.get();
console.log(JSON.stringify({initial:initial.undergroundPair,changed,tour,patch,cleared:cleared.undergroundPair,final:window.location.href}));
""")
    assert out['initial'] == ['lngs-hall-c','snolab-underground-lab']
    assert 'uf=lsm-frejus%2Csnolab-underground-lab' in out['changed']
    assert 'uf=lsm-frejus%2Csnolab-underground-lab' in out['tour'] and 'step=6' in out['tour']
    assert out['patch']['undergroundPair'] == ['snolab-underground-lab','lngs-hall-c']
    assert out['cleared'] is None and 'uf=' not in out['final']
    assert 'theme=projector' in out['final'] and 'data=generated' in out['final']
