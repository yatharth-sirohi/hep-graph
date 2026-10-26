"""Guided tours (A28): the six launch tours are valid, and the validator can fail.

Like `test_atlas_geometry_data.py`, this runs against the committed tree: a
fixture would only prove the code works, not that the tours are true to the
records they cite.  The negative tests mutate a copy of a real tour, so each
one is a sentence an author could really write.
"""

from __future__ import annotations

import copy
import re
from pathlib import Path

import pytest

from hepgraph.atlas import tours as T, validate as v
from hepgraph.atlas.load import DATA_DIR, ROOT, load_atlas

LAUNCH = {
    'neutrino-oscillation-story', 'w-and-z-at-cern', 'higgs-hunt',
    'going-underground-dark-matter', 'neutrino-beams-through-the-earth',
    'how-a-collider-complex-works',
}
BUILD_DATE = '2026-10-26'


@pytest.fixture(scope='module')
def atlas():
    return load_atlas(DATA_DIR)


def _rules(issues, level='error'):
    return {issue.rule for issue in issues if issue.level == level}


def _tour(atlas, slug='neutrino-oscillation-story'):
    return copy.deepcopy(atlas.get(f'tour:{slug}'))


# -- the committed data ------------------------------------------------------

def test_the_six_launch_tours_exist_and_validate_clean(atlas) -> None:
    assert {tid.split(':', 1)[1] for tid in atlas.by_type('tour')} == LAUNCH
    findings = [f for f in v.validate_atlas(atlas, build_date=BUILD_DATE) if f.rule.startswith('tour-')]
    assert findings == [], '\n'.join(f'{f.level} {f.rule} {f.path}{f.pointer}: {f.message}' for f in findings)


def test_every_tour_has_steps_questions_and_a_view_where_promised(atlas) -> None:
    for tour_id, tour in atlas.by_type('tour').items():
        steps = tour['steps']
        assert T.STEP_MIN <= len(steps) <= T.STEP_MAX, tour_id
        assert T.QUESTION_MIN <= sum(1 for s in steps if s.get('question')) <= T.QUESTION_MAX, tour_id
        assert all(s['text'].strip() and s['claims'] for s in steps), tour_id
    beams = atlas.get('tour:neutrino-beams-through-the-earth')
    assert [s['view'] for s in beams['steps'] if s.get('view')] == [
        {'name': 'beam-section', 'arg': slug}
        for slug in ('kek-neutrino', 'cngs', 'numi', 'j-parc-neutrino', 'lbnf')]


def test_gargamelle_is_in_the_atlas_to_the_mandatory_bar(atlas) -> None:
    experiment = atlas.get('experiment:gargamelle')
    assert experiment['status'] == 'completed' and experiment['intervals'] and experiment['topic_ids']
    assert atlas.has('collaboration:gargamelle') and atlas.has('result:gargamelle-neutral-currents-1973')
    assert any(row['entity_id'] == 'experiment:gargamelle' for row in atlas.coverage)


def test_route_types_match_state_js() -> None:
    source = (ROOT / 'static' / 'atlas' / 'js' / 'state.js').read_text(encoding='utf-8')
    block = re.search(r'const TYPE_PREFIX = \{(.*?)\n\};', source, re.S).group(1)
    names = set(re.findall(r'\b([a-z]+):\s*\'[a-z]+\'', block))
    assert names == set(T.ROUTABLE_TYPES)


# -- the validator can fail -------------------------------------------------------

def test_a_valid_tour_has_no_findings(atlas) -> None:
    assert _rules(T.validate_tour(atlas, _tour(atlas), BUILD_DATE), 'error') == set()
    assert _rules(T.validate_tour(atlas, _tour(atlas), BUILD_DATE), 'warning') == set()


def test_unknown_entity_and_field_are_errors(atlas) -> None:
    tour = _tour(atlas)
    tour['steps'][0]['claims'][1] = {'covers': tour['steps'][0]['claims'][1]['covers'],
                                      'ref': 'experiment:no-such-experiment', 'field': 'key_specs.Baseline'}
    tour['steps'][1]['claims'][0]['field'] = 'key_specs.No such spec'
    assert {'tour-ref-unknown-entity', 'tour-ref-unknown-field'} <= _rules(T.validate_tour(atlas, tour, BUILD_DATE))


def test_empty_quote_and_missing_text_are_errors(atlas) -> None:
    tour = _tour(atlas)
    own = next(c for c in tour['steps'][0]['claims'] if 'quote' in c)
    own['quote'] = '  '
    tour['steps'][2]['text'] = ''
    assert {'tour-quote-empty', 'tour-step-text'} <= _rules(T.validate_tour(atlas, tour, BUILD_DATE))


def test_a_sentence_or_number_no_claim_covers_is_an_error(atlas) -> None:
    tour = _tour(atlas)
    tour['steps'][3]['text'] += ' It was also the biggest of its kind, 99 metres wide.'
    rules = _rules(T.validate_tour(atlas, tour, BUILD_DATE))
    assert 'tour-number-uncovered' in rules or 'tour-sentence-uncovered' in rules or 'tour-text-length' in rules


def test_a_number_that_disagrees_with_its_evidence_is_an_error(atlas) -> None:
    tour = _tour(atlas)
    step = tour['steps'][4]
    step['text'] = step['text'].replace('295 km', '395 km')
    for claim in step['claims']:
        claim['covers'] = claim['covers'].replace('295 km', '395 km')
    assert 'tour-claim-number-mismatch' in _rules(T.validate_tour(atlas, tour, BUILD_DATE))


def test_wrong_arithmetic_is_an_error(atlas) -> None:
    tour = _tour(atlas)
    calc = tour['steps'][4]['question']['calculation']
    next(line for line in calc if line.get('name') == 't_ms')['value'] = 9.8
    assert 'tour-calc-result' in _rules(T.validate_tour(atlas, tour, BUILD_DATE))


def test_view_year_camera_and_select_are_checked(atlas) -> None:
    tour = _tour(atlas, 'neutrino-beams-through-the-earth')
    tour['steps'][0]['view'] = {'name': 'no-such-view', 'arg': 'x'}
    tour['steps'][1]['year'] = 1950          # CNGS did not exist
    tour['steps'][2]['camera'] = {'lat': 95, 'lng': 0, 'altitude': 1}
    tour['steps'][3]['select'] = 'source:src-nothing'
    rules = _rules(T.validate_tour(atlas, tour, BUILD_DATE))
    assert {'tour-view', 'tour-select-absent-at-year', 'tour-camera', 'tour-select'} <= rules


def test_step_and_question_counts_are_enforced(atlas) -> None:
    tour = _tour(atlas)
    tour['steps'] = tour['steps'][:3]
    assert {'tour-step-count', 'tour-question-count'} <= _rules(T.validate_tour(atlas, tour, BUILD_DATE))


def test_a_claim_may_not_lean_on_an_encyclopaedia_only_field(atlas) -> None:
    # Homestake's continuous-operation interval cites Wikipedia alone (rank 12).
    resolved = T.resolve(atlas, 'experiment:homestake', 'intervals.continuous operation')
    assert resolved.sources == ['src:homestake-wikipedia']
    tour = _tour(atlas)
    tour['steps'][0]['claims'][1] = {'covers': tour['steps'][0]['claims'][1]['covers'],
                                      'ref': 'experiment:homestake', 'field': 'intervals.continuous operation'}
    assert 'tour-ref-weak-source' in _rules(T.validate_tour(atlas, tour, BUILD_DATE))


# -- the bundle and the links ----------------------------------------------------------

def test_the_bundle_resolves_every_reference_and_links_every_step(atlas) -> None:
    bundle, errors = T.build_bundle(atlas, BUILD_DATE)
    assert errors == []
    assert [tid.split(':', 1)[1] for tid in bundle['order']] == [
        'neutrino-oscillation-story', 'w-and-z-at-cern', 'higgs-hunt',
        'going-underground-dark-matter', 'neutrino-beams-through-the-earth', 'how-a-collider-complex-works']
    for tour in bundle['tours'].values():
        assert tour['sources'] and tour['estimated_minutes']
        for step in tour['steps']:
            assert step['href'].startswith(('?y=', '#/'))
            for claim in step['claims']:
                assert claim['sources'], (tour['id'], step['id'])
                assert 'ref' not in claim or claim['value']


def test_step_links_use_the_routes_state_js_reads() -> None:
    assert T.step_href({'year': 1998, 'select': 'experiment:super-kamiokande'}) == '?y=1998#/experiment/super-kamiokande'
    assert T.step_href({'year': 2024, 'map': 'cern', 'select': 'accelerator:psb'}) == '?y=2024&sel=accelerator%3Apsb#/map/cern'
    assert T.step_href({'year': 2010, 'view': {'name': 'beam-section', 'arg': 'numi'}}) == '?y=2010#/view/beam-section/numi'
    assert T.step_href({}) == ''


def test_number_matching_reads_a_rounded_figure() -> None:
    assert T.number_matches('1.5', [1.478])         # "1.5 km" against 1,478 m
    assert T.number_matches('1500', [1478.0])       # two trailing zeros: read as rounded
    assert not T.number_matches('1480', [1478.0])   # one: exact only
    assert not T.number_matches('295', [395.0])
    assert [t for t, _s, _e in T.number_tokens('T2K at DEAP-3600 in Run 3: 2.5 km')] == ['2.5']
