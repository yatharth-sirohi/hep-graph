"""Historical false-shortcut regressions through ingestion and deep retrieval."""
import pytest

from hepgraph.deep_search import DeepSearch
from hepgraph.ondemand import OnDemand
from test_deep_search import Client, budget, literature_query, page, paper, person, profiles, ref


@pytest.mark.parametrize('work_id,source,target', [
    ('44740',1010907,2203900), ('74757',1069266,1009613),
    ('41231',1010907,1005792), ('42599',1010907,987542), ('44738',1010907,1024083),
])
def test_mislinked_author_occurrence_cannot_become_a_live_direct_path(work_id, source, target):
    responses = profiles(source, target)
    bad_work = paper(work_id, [source, target])
    for query in (f'authors.record.$ref:{source} AND authors.record.$ref:{target} AND author_count:1->10',
                  literature_query(source), literature_query(target)):
        responses[('literature', query, 1)] = page(bad_work)
    session = DeepSearch(Client(responses)).start(source, target, {'genealogy': False})
    try:
        result = session.run(budget(page_size=100))
    finally:
        session.close()
    assert result['status'] == 'search_incomplete' and result['paths'] == []
    assert result['coverage']['historical_authorship_exclusions']
    assert result['coverage']['retrieved']['works'] == 1  # A real publication was retained.


@pytest.mark.parametrize('student', [1005469,1019944])
def test_reviewed_non_doctoral_native_assertion_is_not_a_live_phd_shortcut(student):
    responses = profiles(1011729, student)
    hit = person(student, [{'record': ref(1011729), 'degree_type': 'phd', 'curated_relation': False}])
    responses[('authors', f'control_number:{student}', 1)] = page(hit)
    responses[('authors', 'advisors.record.$ref:1011729', 1)] = page(hit)
    session = DeepSearch(Client(responses)).start(1011729, student)
    try:
        result = session.run(budget(page_size=100))
    finally:
        session.close()
    assert result['status'] == 'search_incomplete' and result['paths'] == []
    assert result['coverage']['historical_profile_relation_exclusions'][0]['student'] == str(student)


def test_institutional_source_is_available_in_quick_live_profile_and_deep_path():
    responses = profiles(1011729,1035527)
    client = Client(responses)
    quick = OnDemand(client).profile(1011729)
    assert quick['status'] == 'ok'
    assert any(item['adviser'] == '1035527' and item['source_url'].startswith('https://www.damtp.cam.ac.uk/')
               for item in quick['advisers'])
    session = DeepSearch(client).start(1035527,1011729)
    try:
        deep = session.run(budget(page_size=100))
    finally:
        session.close()
    assert deep['status'] == 'ok' and deep['paths'][0]['hops'] == 1
    assert deep['paths'][0]['edges'][0]['phd'][0]['source_kind'] == 'institutional_historical_supplement'


def test_quick_live_path_uses_the_same_profile_initial_identity_guard():
    responses = profiles(1013143,1013682)
    responses[('authors', 'control_number:1013143', 1)] = page(person(1013143, name='Conrad, Janet M.'))
    responses[('authors', 'control_number:1013682', 1)] = page(person(1013682, name='Chiu, Charles B.'))
    work = paper(1112560, [1013143,1013682], names={1013143: 'Conrad, J.M.', 1013682: 'Chiu, C.S.'})
    for query in ('authors.record.$ref:1013143 AND authors.record.$ref:1013682 AND author_count:1->10',
                  literature_query(1013143), literature_query(1013682)):
        responses[('literature', query, 1)] = page(work)
    result = OnDemand(Client(responses)).find_paths(1013143,1013682, {'genealogy': False})
    assert result['status'] == 'search_incomplete' and result['paths'] == []
    assert result['coverage']['identity_conflicts'][0]['person'] == '1013682'
