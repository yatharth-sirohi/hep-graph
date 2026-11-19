"""Behavioral regression for the teaching model, scoped URLs and evidence pilot.

Independent Python trigonometry catches unit/phase errors; real browser modules
run under Node, with only the browser location/history boundary supplied here.
"""
import json
import math
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which('node')
pytestmark = pytest.mark.skipif(not NODE, reason='Node is required for browser module checks')


def run_node(script):
    result = subprocess.run([NODE, '--input-type=module', '-e', script],
                            cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_two_flavor_probability_and_first_maximum_in_km_gev():
    out = run_node("""
      import {oscillationProbability as p, firstMaximumEnergy as e} from './static/atlas/js/views/oscillation-model.js';
      console.log(JSON.stringify({values: [[295.3352,.6],[1285,2.5],[735.3,1],[0,1]].map(([l,en])=>p(l,en)),
        maxima: [295.3352,1285].map(l=>[e(l),p(l,e(l)),p(l,e(l)*2)]),
        reduced: p(1285,e(1285),{thetaDeg:15})}));
    """)
    for actual, (baseline, energy) in zip(out['values'], [(295.3352,.6),(1285,2.5),(735.3,1),(0,1)]):
        assert actual == pytest.approx(math.sin(1.267 * .0025 * baseline / energy)**2, abs=1e-12)
        assert 0 <= actual <= 1
    for energy, probability, doubled in out['maxima']:
        assert probability == pytest.approx(1)
        assert doubled == pytest.approx(.5)
    assert out['maxima'][0][0] == pytest.approx(.5955414015, abs=1e-7)
    assert out['maxima'][1][0] == pytest.approx(2.5911936707, abs=1e-7)
    assert out['reduced'] == pytest.approx(.25)


def test_model_rejects_nonphysical_inputs_and_url_energy_stays_finite():
    out = run_node("""
      import {oscillationProbability as p, normaliseEnergy as n} from './static/atlas/js/views/oscillation-model.js';
      const invalid = [[1,0],[1,-1],[-1,1],[Infinity,1],[1,NaN]];
      console.log(JSON.stringify({rejected:invalid.map(args=>{try{p(...args);return false}catch{return true}}),
        energy: [null,'', 'banana','Infinity','-1','0.1','2.5','100'].map(n)}));
    """)
    assert all(out['rejected'])
    assert out['energy'] == [.6,.6,.6,.6,.2,.2,2.5,8]


def test_question_and_lab_urls_roundtrip_and_do_not_leak_into_results():
    out = run_node("""
      globalThis.window = {location: new URL('http://atlas.test/atlas?step=4&e=2.5#/tour/neutrino-beams-through-the-earth'),
        addEventListener(){}, history:{pushState(s,_,u){window.location=new URL(u,window.location)},
          replaceState(s,_,u){window.location=new URL(u,window.location)}}};
      const state = await import('./static/atlas/js/state.js');
      const initial=state.init();
      const link=state.patchFromLink('?step=6#/tour/higgs-hunt');
      state.navigate({entity:{type:'view',slug:'beam-section/lbnf'},energy:1.25});
      const beamURL=window.location.href;
      state.navigate({entity:{type:'result',slug:'atlas-higgs-observation-2012'}});
      console.log(JSON.stringify({initial,link,beamURL,resultURL:window.location.href,energy:state.get().energy}));
    """)
    assert out['initial']['energy'] == 2.5
    assert out['initial']['step'] == 4
    assert out['link']['step'] == 6
    assert '?e=1.25#/view/beam-section/lbnf' in out['beamURL']
    assert 'e=' not in out['resultURL']
    assert out['energy'] is None


def test_evidence_pilot_distinguishes_observed_expected_and_missing_records():
    out = run_node("""
      import {evidenceFor} from './static/atlas/js/result-evidence-data.js';
      console.log(JSON.stringify({atlas:evidenceFor('result:atlas-higgs-observation-2012'),
        cms:evidenceFor('result:cms-higgs-boson-observation-2012'), other:evidenceFor('result:other')}));
    """)
    assert out['other'] is None
    assert out['atlas']['significance']['observed'] == '5.9σ'
    assert out['atlas']['significance']['expected'] == '4.9σ'
    assert out['cms']['significance']['observed'] == '5.0σ'
    assert out['cms']['significance']['expected'] == '5.8σ'
    for experiment in ['atlas','cms']:
        entry = out[experiment]
        assert entry['significance']['scope'] == 'Local significance'
        assert all(item['locator'] and item['url'].startswith('https://arxiv.org/pdf/') and '#page=' in item['url']
                   for item in entry['evidence'])


def test_existing_tours_can_open_the_underground_and_higgs_visuals():
    import copy
    from hepgraph.atlas.load import DATA_DIR, load_atlas
    from hepgraph.atlas.tours import validate_tour, step_href
    atlas = load_atlas(DATA_DIR)
    for name, arg, expected in [('underground', '', '#/view/underground'),
                                ('results-story', 'higgs-physics', '#/view/results-story/higgs-physics')]:
        tour = copy.deepcopy(atlas.get('tour:higgs-hunt'))
        tour['steps'][5]['view'] = {'name': name, 'arg': arg}
        errors = [i for i in validate_tour(atlas, tour, '2026-11-19') if i.level == 'error']
        assert errors == [], [i.message for i in errors]
        assert step_href(tour['steps'][5]).endswith(expected)
