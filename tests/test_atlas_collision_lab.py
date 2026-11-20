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


@pytest.mark.parametrize('slug',['energy-frontier/collision','energy-frontier/collision/'])
def test_question_entry_keeps_selected_energy_in_the_existing_view_grammar(slug):
    out=run_node(f"""
      globalThis.window={{location:new URL('http://atlas.test/atlas?data=generated&ce=1200#/view/{slug}'),addEventListener(){{}},
        history:{{pushState(s,_,u){{window.location=new URL(u,window.location)}},replaceState(s,_,u){{window.location=new URL(u,window.location)}}}}}};
      const state=await import('./static/atlas/js/state.js');const initial=state.init();state.navigate({{year:2012}});
      const atYear=window.location.href;state.patchQuietly({{collisionEnergy:800}});const edited=window.location.href;
      state.navigate({{entity:{{type:'view',slug:'energy-frontier/collision/extra'}},collisionEnergy:800}});
      console.log(JSON.stringify({{initial,atYear,edited,excluded:window.location.href,energy:state.get().collisionEnergy}}));
    """)
    assert out['initial']['entity']=={'type':'view','slug':'energy-frontier/collision'}
    assert 'ce=1200'in out['atYear'] and out['atYear'].endswith('#/view/energy-frontier/collision')
    assert 'ce=800'in out['edited']
    assert 'ce='not in out['excluded'] and out['energy']is None


def test_start_here_adds_the_collision_question_and_preserves_the_original_three():
    from html.parser import HTMLParser
    from urllib.parse import parse_qs,urlsplit
    class Links(HTMLParser):
        def __init__(self):super().__init__();self.links=[];self.current=None
        def handle_starttag(self,tag,attrs):
            attrs=dict(attrs)
            if tag=='a'and 'data-start-link'in attrs:self.current={'href':attrs['href'],'text':''}
        def handle_data(self,data):
            if self.current is not None:self.current['text']+=data
        def handle_endtag(self,tag):
            if tag=='a'and self.current is not None:self.links.append(self.current);self.current=None
    parser=Links();parser.feed((ROOT/'static/atlas/index.html').read_text())
    expected={'Why do neutrino beams go through the Earth?':'/tour/neutrino-beams-through-the-earth',
      'How did ATLAS and CMS establish the Higgs discovery?':'/tour/higgs-hunt',
      'Why are some detectors underground?':'/tour/going-underground-dark-matter',
      'Why do colliders reach higher collision energies?':'/view/energy-frontier/collision'}
    for title,fragment in expected.items():
        link=next((row for row in parser.links if title in row['text']),None)
        assert link is not None,f'Start here needs the question: {title}'
        assert urlsplit(link['href']).fragment==fragment
        if 'colliders' in title:
            assert parse_qs(urlsplit(link['href']).query)=={'ce':['450']}
            assert 'predict' in link['text'].lower()and 'head-on'in link['text']


def test_native_start_links_reuse_visit_context_without_inheriting_other_lesson_inputs():
    out=run_node("""
      import {visitHref} from './static/atlas/js/tour-link.js';
      const context='?data=generated&embed=1&theme=projector&e=1.2&th=15&ce=1000&le=1&step=4&present=1&m=results';
      console.log(JSON.stringify({collision:visitHref('?ce=450#/view/energy-frontier/collision',context),
       beam:visitHref('?step=5&e=2.5#/tour/neutrino-beams-through-the-earth',context),
       cleared:visitHref('?ce=450&data=fixture&embed=1&theme=standard#/view/energy-frontier/collision',''),
       empty:visitHref('#/view/energy-frontier/collision','?e=1.2&th=15')}));
    """)
    from urllib.parse import parse_qs,urlsplit
    assert parse_qs(urlsplit(out['collision']).query)=={'ce':['450'],'data':['generated'],'embed':['1'],'theme':['projector']}
    assert parse_qs(urlsplit(out['beam']).query)=={'step':['5'],'e':['2.5'],'data':['generated'],'embed':['1'],'theme':['projector']}
    assert out['cleared']=='?ce=450#/view/energy-frontier/collision'
    assert out['empty']=='?#/view/energy-frontier/collision'


def test_start_destinations_replace_prior_lesson_state_and_keep_only_visit_context():
    out=run_node("""
      globalThis.window={location:new URL('http://atlas.test/atlas'),addEventListener(){},history:{pushState(s,_,u){window.location=new URL(u,window.location)},replaceState(s,_,u){window.location=new URL(u,window.location)}}};
      const state=await import('./static/atlas/js/state.js');const {visitHref}=await import('./static/atlas/js/tour-link.js');
      const source='http://atlas.test/atlas?data=generated&embed=1&theme=projector&y=2012&m=results&rt=higgs-physics&ry=2012&e=1.2&th=15&le=1&step=5&present=1#/tour/neutrino-beams-through-the-earth';
      const links=['?ce=450#/view/energy-frontier/collision','?step=6#/tour/higgs-hunt','?step=5&e=2.5#/tour/neutrino-beams-through-the-earth','?m=tours'];
      console.log(JSON.stringify(links.map(href=>{window.location=new URL(source);state.init();const target=visitHref(href,window.location.search);state.navigate(state.destinationFromLink(target,{defaultYear:2026}));return {url:window.location.href,state:state.get()}})));
    """)
    from urllib.parse import parse_qs,urlsplit
    for index,row in enumerate(out):
        params=parse_qs(urlsplit(row['url']).query)
        assert all(params[key]==[value]for key,value in [('data','generated'),('embed','1'),('theme','projector')])
        assert not {'rt','ry','th','le','present'}&params.keys()
        assert params['y']==['2026']
        assert row['state']['results']['topic']=='' and row['state']['results']['year']==''
        if index==0:
            assert params['ce']==['450'] and 'm'not in params and 'e'not in params
        elif index==1:
            assert params['step']==['6'] and 'e'not in params and 'm'not in params
        elif index==2:
            assert params['e']==['2.5'] and params['step']==['5'] and 'm'not in params
        else:
            assert params['m']==['tours'] and row['state']['entity']is None
            assert 'ce'not in params and 'step'not in params


def test_full_start_destination_uses_startup_year_without_overriding_authored_dates():
    out=run_node("""
      globalThis.window={location:new URL('http://atlas.test/atlas?r=1990-1995&m=results'),addEventListener(){}};
      const {destinationFromLink}=await import('./static/atlas/js/state.js');
      console.log(JSON.stringify(['?ce=450#/view/energy-frontier/collision','?ce=450&y=1984#/view/energy-frontier/collision','?ce=450&r=1990-1995#/view/energy-frontier/collision'].map(href=>{
       const d=destinationFromLink(href,{defaultYear:2026});return {year:d.year,range:d.range};
      })));
    """)
    assert out==[{'year':2026,'range':None},{'year':1984,'range':None},{'year':None,'range':[1990,1995]}]
