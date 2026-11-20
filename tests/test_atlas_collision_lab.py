"""Independent invariants for the energy-frontier teaching comparison and its URL scope."""
import json
import math
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
NODE=shutil.which('node')
pytestmark=pytest.mark.skipif(not NODE,reason='Node is required for real browser module checks')


def run_node(script):
    result=subprocess.run([NODE,'--input-type=module','-e',script],cwd=ROOT,capture_output=True,text=True,timeout=30)
    assert result.returncode==0,result.stderr
    return json.loads(result.stdout)


@pytest.mark.parametrize('energy',[0.938272,1,450,7000,10000])
def test_collision_energy_matches_the_independent_four_vector_invariant(energy):
    out=run_node(f"""
      import {{COLLISION_MODEL as model,collisionEnergies}} from './static/atlas/js/views/collision-model.js';
      console.log(JSON.stringify({{model,energies:collisionEnergies({energy})}}));
    """)
    mass_energy=0.938272
    momentum=math.sqrt(energy**2-mass_energy**2)
    expected=math.sqrt((energy+mass_energy)**2-momentum**2)
    result=out['energies']
    assert result['beamEnergyGeV']==energy
    assert result['fixedTargetGeV']==pytest.approx(expected,rel=1e-10)
    assert result['headOnGeV']==pytest.approx(math.sqrt((2*energy)**2-(momentum-momentum)**2))
    assert out['model']['restEnergyGeV']==pytest.approx(0.93827208816,rel=1e-6)
    assert out['model']['kinematicsURL']=='https://pdg.lbl.gov/2024/reviews/rpp2024-rev-kinematics.pdf#page=1'
    assert out['model']['restEnergyURL']=='https://pdg.lbl.gov/2024/reviews/rpp2024-rev-phys-constants.pdf#page=1'


def test_nonphysical_and_overflowing_inputs_never_produce_a_figure():
    out=run_node("""
      import {collisionEnergies as calc} from './static/atlas/js/views/collision-model.js';
      console.log(JSON.stringify([0,-1,.5,NaN,Infinity,null,'450',1e308].map(e=>{try{calc(e);return false}catch(error){return error instanceof RangeError}})));
    """)
    assert all(out)


def test_query_normalization_is_finite_bounded_and_explicitly_rounded():
    out=run_node("""
      import {COLLISION_ENERGY as bounds,normaliseCollisionEnergy as n} from './static/atlas/js/views/collision-model.js';
      console.log(JSON.stringify({bounds,values:[null,'','banana','Infinity',true,-1,.938272,1,1.26,450.15,1e9].map(n)}));
    """)
    assert out['bounds']=={'min':1,'max':10000,'default':450,'step':.1}
    assert out['values']==[450,450,450,450,450,1,1,1,1.3,450.2,10000]


def test_quadrupling_uses_the_exact_rest_term_and_refuses_range_overflow():
    out=run_node("""
      import {quadrupleExperiment as q} from './static/atlas/js/views/collision-model.js';
      console.log(JSON.stringify({runs:[1,450,2500].map(q),refused:[0,.938272,2500.01,10000,NaN,Infinity].map(q)}));
    """)
    for energy,result in zip([1,450,2500],out['runs']):
        assert result['start']['beamEnergyGeV']==energy and result['end']['beamEnergyGeV']==4*energy
        assert result['fixedFactor']==pytest.approx(math.sqrt((.938272+4*energy)/(.938272+energy)))
        assert result['headOnFactor']==4
    assert 1.5<out['runs'][0]['fixedFactor']<1.7
    assert out['runs'][1]['fixedFactor']<2
    assert out['refused']==[None]*6


def test_collision_input_roundtrips_and_clears_outside_the_energy_view():
    out=run_node("""
      globalThis.window={location:new URL('http://atlas.test/atlas?data=generated&theme=projector&y=2012&ce=450.15#/view/energy-frontier'),
       addEventListener(){},history:{pushState(s,_,url){window.location=new URL(url,window.location)},replaceState(s,_,url){window.location=new URL(url,window.location)}}};
      const state=await import('./static/atlas/js/state.js');const initial=state.init();
      const patch=state.patchFromLink('?ce=1800#/view/energy-frontier');state.navigate(patch);const updated=window.location.href;
      state.navigate({entity:{type:'result',slug:'atlas-higgs-observation-2012'}});const result={url:window.location.href,energy:state.get().collisionEnergy};
      state.navigate({entity:{type:'view',slug:'beam-section/lbnf'},energy:2.5});
      console.log(JSON.stringify({initial,patch,updated,result,beam:window.location.href}));
    """)
    from urllib.parse import parse_qs,urlsplit
    assert out['initial'].get('collisionEnergy')==450.2
    assert out['patch']['collisionEnergy']==1800
    assert parse_qs(urlsplit(out['updated']).query)=={'data':['generated'],'theme':['projector'],'y':['2012'],'ce':['1800']}
    assert out['result']['energy'] is None and 'ce='not in out['result']['url']
    assert 'ce='not in out['beam'] and 'e=2.5'in out['beam']


def test_empty_argument_energy_route_is_canonical_but_arbitrary_views_are_excluded():
    out=run_node("""
      globalThis.window={location:new URL('http://atlas.test/atlas?ce=1200#/view/energy-frontier/'),addEventListener(){},
        history:{pushState(s,_,u){window.location=new URL(u,window.location)},replaceState(s,_,u){window.location=new URL(u,window.location)}}};
      const state=await import('./static/atlas/js/state.js');const initial=state.init();state.navigate({year:2012});
      const start=window.location.href;state.patchQuietly({collisionEnergy:800});const edited=window.location.href;
      const excluded=['energy-frontier/other','energy-frontier/nested/path','other-energy-frontier'].map(slug=>{
       state.navigate({entity:{type:'view',slug},collisionEnergy:800});return {url:window.location.href,value:state.get().collisionEnergy};
      });
      console.log(JSON.stringify({initial,start,edited,excluded}));
    """)
    assert out['initial']['entity']=={'type':'view','slug':'energy-frontier'}
    assert 'ce=1200' in out['start'] and out['start'].endswith('#/view/energy-frontier')
    assert 'ce=800' in out['edited'] and out['edited'].endswith('#/view/energy-frontier')
    assert all(row['value'] is None and 'ce='not in row['url']for row in out['excluded'])
