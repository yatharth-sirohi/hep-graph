"""Optional predictions extend the existing tour question, with validated content."""
import copy
import json
from pathlib import Path

import pytest

from hepgraph.atlas import tours as T
from hepgraph.atlas.load import DATA_DIR, load_atlas

DATE = '2026-11-20'
CHOICES = [{'id':'background','label':'Background-only tail at a tested mass'},
           {'id':'model','label':'Probability of the model itself'},
           {'id':'scan','label':'Probability over the whole mass scan'}]


@pytest.fixture(scope='module')
def atlas():
    return load_atlas(DATA_DIR)


def errors(atlas, tour):
    return [f for f in T.validate_tour(atlas,tour,DATE) if f.level=='error']


def pilot(atlas):
    tour=copy.deepcopy(atlas.get('tour:higgs-hunt'))
    return tour,tour['steps'][5]['question']


def test_the_real_pilot_preserves_working_and_carries_one_supported_interpretation(atlas):
    tour,q=pilot(atlas)
    assert len(q.get('choices',[]))==3, 'Higgs needs a prediction before its answer is revealed'
    assert q['correct_choice']=='local-background'
    assert q['correct_choice'] in {c['id'] for c in q['choices']}
    assert q['calculation'][-1]['value']==590
    assert all(phrase in q['answer'] for phrase in ['background-only','at least','fixed tested mass','on average'])
    assert 'later ATLAS paper' in tour['steps'][5]['text']
    assert not errors(atlas,tour)
    built,_=T.build_bundle(atlas,DATE)
    out=built['tours'][tour['id']]['steps'][5]['question']
    assert out['choices']==q['choices'] and out['correct_choice']==q['correct_choice']
    assert out['calculation'][-1]['value']==590
    source=json.loads((Path(DATA_DIR)/'sources/tours-atlas-higgs-observation-arxiv-1207-7214-pdf.json').read_text())
    assert source['url']=='https://arxiv.org/pdf/1207.7214v1'


def test_choices_are_optional_and_resolved_without_changing_a_legacy_question(atlas):
    tour,q=pilot(atlas)
    q.pop('choices',None);q.pop('correct_choice',None)
    assert not errors(atlas,tour)
    legacy=T._resolved_question(atlas,q)
    assert 'choices' not in legacy and 'correct_choice' not in legacy
    q.update(choices=CHOICES,correct_choice='background')
    assert not errors(atlas,tour)
    resolved=T._resolved_question(atlas,q)
    assert resolved['choices']==CHOICES and resolved['correct_choice']=='background'


@pytest.mark.parametrize('patch',[
    {'choices':CHOICES[:1],'correct_choice':'background'},
    {'choices':CHOICES*2,'correct_choice':'background'},
    {'choices':'background','correct_choice':'background'},
    {'choices':CHOICES,'correct_choice':'missing'},
    {'choices':CHOICES},
    {'choices':[CHOICES[0],{**CHOICES[1],'id':'background'}],'correct_choice':'background'},
    {'choices':[CHOICES[0],{**CHOICES[1],'label':CHOICES[0]['label']}],'correct_choice':'background'},
    {'choices':[CHOICES[0],{**CHOICES[1],'label':''}],'correct_choice':'background'},
    {'choices':[CHOICES[0],{**CHOICES[1],'feedback':'Unsourced extra content'}],'correct_choice':'background'},
    {'correct_choice':'background'},
])
def test_malformed_choice_metadata_is_reported_before_building(atlas,patch):
    tour,q=pilot(atlas)
    q.pop('choices',None);q.pop('correct_choice',None);q.update(copy.deepcopy(patch))
    assert 'tour-choice-shape' in {f.rule for f in errors(atlas,tour)}


def test_worked_examples_do_not_create_another_prediction_checkpoint(atlas):
    tour=copy.deepcopy(atlas.get('tour:going-underground-dark-matter'))
    example=tour['steps'][5]['question']['worked_example']
    example.update(choices=CHOICES,correct_choice='background')
    assert 'tour-choice-shape' in {f.rule for f in errors(atlas,tour)}


def test_sno_prediction_distinguishes_inferred_flux_from_raw_counts(atlas):
    tour=atlas.get('tour:neutrino-oscillation-story')
    step=tour['steps'][2];q=step['question']
    assert len(q.get('choices',[]))==3, 'SNO needs an interpretation before revealing its flux working'
    choices={c['id']:c['label'] for c in q['choices']}
    assert set(choices)=={'equal-inferred-flux','nc-must-be-larger','equal-raw-counts'}
    assert q['correct_choice']=='equal-inferred-flux'
    assert 'inferred' in choices['equal-inferred-flux'] and 'agree' in choices['equal-inferred-flux']
    assert 'raw' in choices['equal-raw-counts']
    assert 'more flavors' in choices['nc-must-be-larger']
    for phrase in ['reaction responses','does not require equal raw','no propagated uncertainty','single-energy','not this division']:
        assert phrase in q['answer']
    assert [q['calculation'][i]['value'] for i in [0,1,-1]]==[1.76,5.09,35]
    assert any('reaction responses' in c.get('covers','') and 'PDF page 2' in c.get('locator','') for c in q['claims'])
    assert step['select']=='experiment:sno' and step['year']==2002
    assert not errors(atlas,tour)
    built,issues=T.build_bundle(atlas,DATE)
    assert not issues
    resolved=built['tours'][tour['id']]['steps'][2]['question']
    assert resolved['choices']==q['choices'] and resolved['correct_choice']==q['correct_choice']
    assert resolved['calculation'][-1]['value']==35
