"""Historical beam dependencies drive one checkpoint in the existing map player."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which('node')
pytestmark = pytest.mark.skipif(not NODE, reason='Node is required for the real browser modules')


def node(script):
    result = subprocess.run([NODE, '--input-type=module', '-e', script], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


SETUP = """
import fs from 'node:fs';
import {chainAt} from './static/atlas/js/proton-chain.js';
import {beamDependencyExercise, beamDependencyAvailable, DEPENDENCY_ENTRY} from './static/atlas/js/proton-dependency.js';
const atlas=JSON.parse(fs.readFileSync('static/atlas/generated/atlas.json','utf8'));
const geometry=JSON.parse(fs.readFileSync('static/atlas/generated/geometry/fermilab.json','utf8'));
const chain=chainAt(atlas,'facility:fermilab',2016,geometry);
"""


def test_reviewed_feeders_and_native_trace_steps_come_from_the_actual_chain():
    data = node(SETUP + """
const exercise=beamDependencyExercise(chain);
console.log(JSON.stringify({exercise,entry:DEPENDENCY_ENTRY,available:beamDependencyAvailable(atlas),
 entryStage:chain.steps[DEPENDENCY_ENTRY.proton-1].stage.id,
 targets:exercise.branches.map(b=>{const s=chain.steps[b.traceStep-1];return [s.kind,s.from.id,s.to.id]})}));
""")
    assert data['available']
    assert data['entry'] == {'map': 'fermilab', 'year': 2016, 'proton': 7}
    assert data['entryStage'] == 'accelerator:fermilab-main-injector'
    exercise = data['exercise']
    assert exercise['answerId'] == 'beamline:numi'
    assert [b['sourceId'] for b in exercise['branches']] == ['accelerator:fermilab-main-injector','accelerator:fermilab-booster']
    assert [b['traceStep'] for b in exercise['branches']] == [8,10]
    assert data['targets'] == [['transfer','accelerator:fermilab-main-injector','beamline:numi'],
                               ['transfer','accelerator:fermilab-booster','beamline:bnb']]
    canonical = json.loads((ROOT/'static/atlas/generated/atlas.json').read_text())
    for branch, paper, page in zip(exercise['branches'], ['1507.06690v2','0806.1449v2'], [6,2]):
        assert branch['sourceId'] == canonical['beamlines'][branch['id']]['accelerator_id']
        evidence = branch['evidence']
        assert evidence['url'] == f'https://arxiv.org/pdf/{paper}#page={page}'
        assert f'PDF page {page}' in evidence['locator']
        authored = json.loads((ROOT/'data/atlas/beamlines'/f"{branch['id'].split(':')[1]}.json").read_text())
        assert evidence['sourceId'] in authored['sources']


def test_missing_or_changed_source_geometry_cannot_leave_a_stale_question():
    data = node(SETUP + """
const clone=()=>structuredClone(chain);
const missing=clone();missing.stages=missing.stages.filter(s=>s.id!=='beamline:bnb');
const changed=clone();changed.stages.find(s=>s.id==='beamline:bnb').record.accelerator_id='accelerator:fermilab-main-injector';
const undrawn=clone();undrawn.stages.find(s=>s.id==='beamline:bnb').drawn=false;
const noTransfer=clone();noTransfer.steps=noTransfer.steps.filter(s=>s.kind!=='transfer');
const later=chainAt(atlas,'facility:fermilab',2023,geometry);
console.log(JSON.stringify({rejected:[missing,changed,undrawn,noTransfer,{...chain,facilityId:'facility:cern'},{...chain,species:'electron'}].map(beamDependencyExercise),
 changedKey:beamDependencyExercise(chain).key!==beamDependencyExercise(later).key,
 noMap:beamDependencyAvailable({...atlas,maps:{}})}));
""")
    assert data['rejected'] == [None]*6
    assert data['changedKey'] is True
    assert data['noMap'] is False


def test_map_question_deep_link_keeps_visit_options_and_scopes_its_own_year_step():
    data = node("""
import {mapStepHref} from './static/atlas/js/tour-link.js';
globalThis.window={location:new URL('http://atlas.test/atlas?y=2026&e=1.2&le=1#/experiment/nova'),addEventListener(){},
 history:{replaceState(s,_,u){window.location=new URL(u,window.location)},pushState(s,_,u){window.location=new URL(u,window.location)}}};
const state=await import('./static/atlas/js/state.js');state.init();
const href=mapStepHref('fermilab',2016,7,'?data=generated&embed=1&theme=projector&y=2026&proton=99&step=5&e=1.2&le=1&from=2025&to=2026');
window.location=new URL(href,window.location);
console.log(JSON.stringify({href,target:state.init()}));
""")
    assert data['href'] == '?data=generated&embed=1&theme=projector&y=2016&proton=7#/map/fermilab'
    assert data['target']['entity'] == {'type':'map','slug':'fermilab'}
    assert data['target']['year'] == 2016 and data['target']['proton'] == 7
    assert data['target']['range'] is None and data['target']['energy'] is None
