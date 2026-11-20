"""Reviewed SNO evidence keeps channel fluxes and fitted flavor components distinct."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which('node')
pytestmark = pytest.mark.skipif(not NODE, reason='Node is required for browser data checks')


def run_node(script):
    result = subprocess.run([NODE, '--input-type=module', '-e', script], cwd=ROOT,
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


@pytest.fixture(scope='module')
def evidence():
    return run_node("""
      import {evidenceFor} from './static/atlas/js/result-evidence-data.js';
      console.log(JSON.stringify(evidenceFor('result:sno-nc-evidence-2002')));
    """)


def test_sno_reader_uses_the_reported_shape_constrained_channel_fluxes(evidence):
    assert evidence is not None, 'SNO needs a reviewed measured-evidence trail'
    reader = evidence['channelReader']
    assert '⁸B' in reader['assumption'] and 'standard' in reader['assumption'].lower()
    assert reader['units'] == '10⁶ cm⁻² s⁻¹'
    cc,nc = reader['channels']
    assert [cc['id'],nc['id']] == ['cc','nc']
    assert cc['flux'] == {'value':'1.76','stat':'+0.06 / −0.05','syst':'±0.09'}
    assert nc['flux'] == {'value':'5.09','stat':'+0.44 / −0.43','syst':'+0.46 / −0.43'}
    assert cc['probes'] == ['electron']
    assert set(nc['probes']) == {'electron','muon','tau'}
    assert reader['reactionSource']['url'] == 'https://arxiv.org/pdf/nucl-ex/0204008v2#page=2'
    assert reader['fluxSource']['url'] == 'https://arxiv.org/pdf/nucl-ex/0204008v2#page=4'
    source = json.loads((ROOT/'data/atlas/sources/sno-2002-nc-evidence.json').read_text())
    assert 'nucl-ex/0204008v2' in source['url']
    result = json.loads((ROOT/'data/atlas/results/sno-nc-evidence-2002.json').read_text())
    assert 'src:sno-2002-nc-evidence' in result['sources']


def test_reported_significance_belongs_to_the_fitted_non_electron_component(evidence):
    assert evidence is not None
    assert evidence['significance']['observed'] == '5.3σ above zero'
    assert not evidence['significance'].get('expected')
    assert '3.41' in evidence['significance']['at'] and 'ES' in evidence['significance']['at']
    assert 'ratio' in evidence['significance']['note']
    assert 'single-energy' in evidence['conclusion']
    assert evidence['evidence'][0]['url'] == 'https://arxiv.org/pdf/nucl-ex/0204008v2#page=5'
    assert 'Figure 3' in evidence['evidence'][0]['locator']


def test_the_pilot_reuses_the_existing_sno_question_and_leaves_other_records_uncurated(evidence):
    assert evidence is not None
    assert evidence['nextQuestion']['tour'] == 'neutrino-oscillation-story'
    assert evidence['nextQuestion']['step'] == 3
    out = run_node("""
      import {evidenceFor} from './static/atlas/js/result-evidence-data.js';
      console.log(JSON.stringify({other:evidenceFor('result:atlas-nature-higgs-2022'),
       atlas:evidenceFor('result:atlas-higgs-observation-2012').significance,
       cms:evidenceFor('result:cms-higgs-boson-observation-2012').significance}));
    """)
    assert out['other'] is None
    assert (out['atlas']['observed'],out['atlas']['expected']) == ('5.9σ','4.9σ')
    assert (out['cms']['observed'],out['cms']['expected']) == ('5.0σ','5.8σ')


def test_native_evidence_result_link_retains_only_visit_context():
    href = run_node("""
      import {resultEvidenceHref} from './static/atlas/js/tour-link.js';
      console.log(JSON.stringify(resultEvidenceHref('sno-nc-evidence-2002',
       '?data=generated&embed=1&theme=projector&e=1.2&th=15&le=1&present=1&step=5&r=2002,2026')));
    """)
    from urllib.parse import urlsplit,parse_qs
    url = urlsplit(href)
    assert url.fragment == '/result/sno-nc-evidence-2002'
    assert parse_qs(url.query) == {'data':['generated'],'embed':['1'],'theme':['projector']}


def test_native_evidence_link_clears_a_source_query_with_no_visit_context():
    out = run_node("""
      import {resultEvidenceHref} from './static/atlas/js/tour-link.js';
      const source='http://atlas.test/atlas?e=1.2&th=15&le=1&step=5&present=1#/tour/neutrino-beams-through-the-earth';
      const target=new URL(resultEvidenceHref('sno-nc-evidence-2002',new URL(source).search),source);
      console.log(JSON.stringify({params:[...target.searchParams],hash:target.hash}));
    """)
    assert out['params'] == [], 'native links must not inherit the source lesson query'
    assert out['hash'] == '#/result/sno-nc-evidence-2002'
