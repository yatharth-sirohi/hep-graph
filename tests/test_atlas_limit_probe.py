"""Exact published-row comparisons: an allowed point is not a detection."""
import copy
import json
import shutil
import subprocess
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which('node')
pytestmark = pytest.mark.skipif(not NODE, reason='Node is required for real module checks')
ROW = json.loads((ROOT/'data/atlas/limits/lz-2024-si-wimp-nucleon.json').read_text())


def run_node(script):
    result = subprocess.run([NODE, '--input-type=module', '-e', script], cwd=ROOT,
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


@pytest.mark.parametrize('factor,relation,want', [
    (.1, 'below', 2.1816833824484828e-49),
    (1, 'boundary', 2.1816833824484827e-48),
    (10, 'above', 2.1816833824484828e-47),
])
def test_model_point_compares_to_the_exact_observed_column(factor, relation, want):
    # Catch substituting expected sensitivity, reversing exclusions, or rounding before comparison.
    out = run_node(f"""
      import {{limitComparison}} from './static/atlas/js/views/limit-probe-model.js';
      console.log(JSON.stringify(limitComparison({json.dumps(ROW)},40,{factor})));
    """)
    assert out == {'massGeV': 40, 'limitCm2': 2.1816833824484827e-48,
                   'modelCm2': pytest.approx(want,rel=1e-14,abs=0), 'factor': factor, 'relation': relation}


def test_comparison_refuses_missing_masses_invalid_factors_units_and_overflow():
    wrong_units = copy.deepcopy(ROW)
    wrong_units['columns']['y']['unit'] = 'pb'
    overflowing = copy.deepcopy(ROW)
    overflowing['points'] = [[40, 1e308]]
    out = run_node(f"""
      import {{limitComparison as c}} from './static/atlas/js/views/limit-probe-model.js';
      const row={json.dumps(ROW)};
      const invalid=[[39,10],[40,0],[40,.2],[40,100],[40,NaN],[40,Infinity],['40',10],[40,'10']];
      console.log(JSON.stringify([...invalid.map(p=>c(row,...p)),c({json.dumps(wrong_units)},40,10),c({json.dumps(overflowing)},40,10)]));
    """)
    assert out == [None]*10, 'No interpolation, unit mixing or invalid hypothetical points'


def test_query_normalization_rejects_unrepresentable_or_unsupported_setups():
    out = run_node("""
      import {normaliseLimitProbe as n} from './static/atlas/js/views/limit-probe-model.js';
      console.log(JSON.stringify(['40,10','4e1,1e-1','40,1',null,'','40','0,10','-40,10','Infinity,10','40,NaN','40,2','40,10,1',true].map(n)));
    """)
    assert out == ['40,10','40,0.1','40,1']+[None]*10


def test_overlay_domain_keeps_every_published_point_and_trial_symbol_inside():
    out = run_node(f"""
      import {{limitComparison,comparisonDomain}} from './static/atlas/js/views/limit-probe-model.js';
      const row={json.dumps(ROW)},domain={{x0:5,x1:1e6,y0:1e-48,y1:1e-42}};
      const comparisons=row.points.flatMap(([mass])=>[.1,1,10].map(f=>limitComparison(row,mass,f)));
      console.log(JSON.stringify({{original:domain,closed:comparisonDomain(domain,null),runs:comparisons.map(c=>({{c,d:comparisonDomain(domain,c)}}))}}));
    """)
    assert out['original'] == out['closed'] == {'x0':5,'x1':1e6,'y0':1e-48,'y1':1e-42}
    assert len(out['runs']) == 78
    for run in out['runs']:
        c, d = run['c'], run['d']
        assert d['x0'] == 5 and d['x1'] == 1e6
        assert d['y0'] < min(c['limitCm2'], c['modelCm2'])
        assert d['y1'] > max(c['limitCm2'], c['modelCm2'])
        assert d['y0'] <= 1e-48 and d['y1'] >= 1e-42


def test_probe_roundtrips_only_on_the_registered_limit_plot():
    out = run_node("""
      const listeners={};globalThis.window={location:new URL('http://atlas.test/atlas?data=generated&wp=4e1,1e-1#/view/limits/wimp-si'),
       addEventListener(k,fn){listeners[k]=fn},history:{pushState(s,_,u){window.location=new URL(u,window.location)},replaceState(s,_,u){window.location=new URL(u,window.location)}}};
      const state=await import('./static/atlas/js/state.js');const initial=state.init();
      state.patchQuietly({wimpProbe:'40,10'});const edited=window.location.href;
      const patch=state.patchFromLink('?wp=40,1#/view/limits/wimp-si');state.navigate(patch);const linked=window.location.href;
      const excluded=['limits/wimp-si/nested','limits/other','energy-frontier'].map(slug=>{state.navigate({entity:{type:'view',slug},wimpProbe:'40,10'});return {url:window.location.href,value:state.get().wimpProbe}});
      window.location=new URL(edited);listeners.popstate();
      console.log(JSON.stringify({initial,edited,patch,linked,excluded,restored:state.get()}));
    """)
    assert out['initial'].get('wimpProbe') == '40,0.1'
    assert parse_qs(urlsplit(out['edited']).query)['wp'] == ['40,10']
    assert out['patch']['wimpProbe'] == '40,1'
    assert parse_qs(urlsplit(out['linked']).query)['wp'] == ['40,1']
    assert all(r['value'] is None and 'wp=' not in r['url'] for r in out['excluded'])
    assert out['restored']['wimpProbe'] == '40,10'


def test_overlay_domain_reserves_room_for_the_whole_symbol_at_interior_masses():
    # Catch a center inside the domain whose 7px triangle + stroke crosses an axis.
    out = run_node(f"""
      import {{limitComparison,comparisonDomain}} from './static/atlas/js/views/limit-probe-model.js';
      const row={json.dumps(ROW)},d={{x0:5,x1:1e6,y0:1e-48,y1:1e-44}};
      console.log(JSON.stringify(row.points.flatMap(([m])=>[.1,1,10].map(f=>{{const c=limitComparison(row,m,f);return {{c,d:comparisonDomain(d,c)}}}}))));
    """)
    import math
    for run in out:
        c, d = run['c'], run['d']
        span = math.log10(d['y1'])-math.log10(d['y0'])
        for value in [c['limitCm2'],c['modelCm2']]:
            above = 338*(math.log10(value)-math.log10(d['y0']))/span
            below = 338*(math.log10(d['y1'])-math.log10(value))/span
            assert min(above,below)>13, (c,above,below)


@pytest.mark.parametrize('hash', ['#/result/lz-ws2024-wimp-search-2024', '#/view/limits/other', '#/view/limits/wimp-si/nested'])
def test_unrelated_pasted_setup_cannot_open_a_later_limit_exercise(hash):
    out = run_node(f"""
      const listeners={{}};globalThis.window={{location:new URL('http://atlas.test/atlas?wp=40,10{hash}'),addEventListener(k,f){{listeners[k]=f}},
       history:{{pushState(s,_,u){{window.location=new URL(u,window.location)}},replaceState(s,_,u){{window.location=new URL(u,window.location)}}}}}};
      const state=await import('./static/atlas/js/state.js');const initial=state.init().wimpProbe;
      state.navigate({{entity:{{type:'view',slug:'limits/wimp-si'}}}});const entered={{value:state.get().wimpProbe,url:window.location.href}};
      window.location=new URL('http://atlas.test/atlas?wp=40,10{hash}');listeners.popstate();const restored=state.get().wimpProbe;
      console.log(JSON.stringify({{initial,entered,restored}}));
    """)
    assert out['initial'] is None and out['restored'] is None
    assert out['entered']['value'] is None and 'wp=' not in out['entered']['url']
