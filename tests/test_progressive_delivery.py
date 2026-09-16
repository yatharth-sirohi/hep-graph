"""Progressive route delivery: publish the first verified route at once, keep
proving in the background, and version every published state.

The engine is faked; these tests are about what SearchJobs promises the browser:
a monotonic ``sequence_number``, a ``best_route`` that only the engine's own
verified routes can populate, honest ``route_status`` values, an event timeline
and timing metrics - and that Stop keeps the verified route.
"""
import json
import threading

import pytest

from hepgraph.graph import Filters
from hepgraph.search_jobs import ROUTE_STATUSES, SearchJobs
from test_search_jobs import eventually


def route(*ids):
    people = [{'id': str(i), 'name': f'Person {i}'} for i in ids]
    return {'hops': len(ids) - 1, 'people': people,
            'edges': [{'source': str(a), 'target': str(b), 'types': ['coauthor'], 'works': []}
                      for a, b in zip(ids, ids[1:])]}


LONG = route('A', 'X', 'Y', 'Z', 'B')          # 4 hops: the first thing found
LONG_TWIN = route('A', 'X', 'W', 'Z', 'B')     # 4 hops as well: not an improvement
SHORT = route('A', 'P', 'Q', 'B')              # 3 hops: hidden until later


class ImprovingEngine:
    """A scripted engine: no route, a 4-hop route, an equal 4-hop alternative,
    a 3-hop route, then the 3-hop proof."""

    def __init__(self, script=None):
        self.calls = 0
        self.closed = threading.Event()
        self.script = script or [
            {'status': 'search_incomplete', 'can_continue': True, 'paths': []},
            {'status': 'ok', 'can_continue': True, 'paths': [LONG]},
            {'status': 'ok', 'can_continue': True, 'paths': [LONG_TWIN, LONG]},
            {'status': 'ok', 'can_continue': True, 'paths': [SHORT]},
            {'status': 'ok', 'can_continue': False, 'paths': [SHORT], 'global_shortest_proven': True,
             'bounds': {'lower': 3, 'upper': 3, 'proven': True}},
        ]

    def start(self, source, target, filters, *, cancel, progress):
        self.cancel, self.progress = cancel, progress
        return self

    def run(self, budget):
        self.calls += 1
        step = self.script[min(self.calls, len(self.script)) - 1]
        return {'version': 'evidence-v1', 'message': 'scripted', 'coverage': {'failures': []},
                'progress': {'works_retrieved': 10 * self.calls, 'people_explored': self.calls,
                             'requests': self.calls, 'elapsed_seconds': self.calls},
                **step}

    def close(self):
        self.closed.set()


def polls_until(jobs, key, predicate, limit=20):
    """Poll the job, collecting every state, until the predicate holds."""
    states = []
    for _ in range(limit):
        states.append(jobs.get(key))
        if predicate(states[-1]):
            return states
    raise AssertionError('The job never reached the expected state.')


def test_first_route_is_published_then_improved_then_proven_without_a_browser_post():
    now = [0.0]

    def tick():
        now[0] += 1.0
        return now[0]

    engine = ImprovingEngine()
    jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=0, clock=tick)
    try:
        started = jobs.start('A', 'B', Filters())
        key = started['job_id']
        assert started['route_status'] == 'searching_no_path' and started['best_route'] is None
        assert started['search_policy']['prove_after_route'] is True

        states = polls_until(jobs, key, lambda s: s['route_status'] == 'exact_route_proven')
        # No poll ever needed a Continue: the job stayed 'searching' with a
        # verified route until the proof closed.
        assert [s['status'] for s in states[:-1]] == ['searching'] * (len(states) - 1)
        assert states[-1]['status'] == 'ok' and states[-1]['can_continue'] is False

        found = next(s for s in states if s['best_route'])
        assert found['route_status'] == 'verified_route_found'
        assert found['best_route']['hops'] == 4 and found['paths'][0]['hops'] == 4
        assert found['message'].startswith('A verified route is shown')
        assert found['progress']['stage'] == 'prove_shortest'

        improved = next(s for s in states if s['best_route'] and s['best_route']['hops'] == 3)
        assert improved['route_status'] == 'verified_route_found'
        assert improved['best_route']['route_id'] != found['best_route']['route_id']

        final = states[-1]
        assert final['best_route']['exact'] is True and final['best_route']['hops'] == 3
        assert final['best_route']['route_id'] == improved['best_route']['route_id']
        kinds = [event['type'] for event in final['events']]
        assert kinds == ['search_started', 'first_path_found', 'path_improved', 'exact_proven', 'search_finished']
        assert final['metrics']['improvements'] == 1
        assert final['metrics']['first_hops'] == 4 and final['metrics']['best_hops'] == 3
        first, best, exact = (final['metrics'][k] for k in
                              ('time_to_first_verified_path', 'time_to_best_route', 'time_to_exact_proof'))
        assert 0 < first < best < exact <= final['metrics']['elapsed_seconds']
        assert engine.closed.is_set()
    finally:
        jobs.shutdown()


def test_sequence_numbers_are_strictly_monotonic_and_route_ids_stable():
    engine = ImprovingEngine()
    jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=0)
    try:
        key = jobs.start('A', 'B', Filters())['job_id']
        states = polls_until(jobs, key, lambda s: s['status'] != 'searching')
        sequences = [s['sequence_number'] for s in states]
        assert sequences == sorted(sequences) and len(set(sequences)) == len(sequences)
        assert all(s['route_status'] in ROUTE_STATUSES for s in states)
        # The same route keeps the same identity wherever it appears, and a
        # path's own route_id matches the best_route that names it.
        ids = {}
        for s in states:
            for path in s['paths']:
                key_ = tuple(p['id'] for p in path['people'])
                assert ids.setdefault(key_, path['route_id']) == path['route_id']
            if s['best_route']:
                assert s['best_route']['route_id'] == s['paths'][0]['route_id']
        # A poll that changes nothing does not mint a new version.
        again = jobs.get(key)
        assert again['sequence_number'] == states[-1]['sequence_number']
    finally:
        jobs.shutdown()


def test_an_equal_length_route_is_not_an_improvement():
    engine = ImprovingEngine()
    jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=0)
    try:
        key = jobs.start('A', 'B', Filters())['job_id']
        states = polls_until(jobs, key, lambda s: s['status'] != 'searching')
        twin = next(s for s in states if s['paths'] and s['paths'][0]['people'][2]['id'] == 'W')
        assert twin['best_route']['hops'] == 4 and twin['best_route']['alternatives'] == 1
        assert [e['type'] for e in twin['events']].count('path_improved') == 0
        assert twin['metrics']['improvements'] == 0
        # Its identity moved to the new primary route, its hop count did not.
        assert twin['best_route']['route_id'] == twin['paths'][0]['route_id']
    finally:
        jobs.shutdown()


def test_stop_preserves_the_verified_route_and_names_the_state():
    engine = ImprovingEngine()
    jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=0)
    try:
        key = jobs.start('A', 'B', Filters())['job_id']
        found = polls_until(jobs, key, lambda s: s['best_route'] is not None)[-1]
        stopped = jobs.cancel(key)
        assert stopped['status'] == 'cancelled' and stopped['can_continue'] is False
        assert stopped['paths'] == found['paths']
        assert stopped['best_route']['route_id'] == found['best_route']['route_id']
        assert stopped['best_route']['exact'] is False
        assert stopped['route_status'] == 'verified_search_stopped'
        assert stopped['events'][-1]['type'] == 'search_stopped'
        assert stopped['sequence_number'] > found['sequence_number']
        assert stopped['metrics']['time_to_exact_proof'] is None
        # Nothing later may revive it or relabel the route.
        assert jobs.get(key)['route_status'] == 'verified_search_stopped'
        assert engine.closed.wait(1)
    finally:
        jobs.shutdown()


def test_stop_before_any_route_is_an_incomplete_search_not_a_no_path():
    engine = ImprovingEngine(script=[{'status': 'search_incomplete', 'can_continue': True, 'paths': []}])
    jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=0)
    try:
        key = jobs.start('A', 'B', Filters())['job_id']
        stopped = jobs.cancel(key)
        assert stopped['status'] == 'cancelled' and stopped['best_route'] is None
        assert stopped['route_status'] == 'search_incomplete'
        assert stopped['metrics']['time_to_first_verified_path'] is None
    finally:
        jobs.shutdown()


def test_legacy_policy_still_pauses_on_a_verified_route():
    engine = ImprovingEngine()
    jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=0, prove_after_route=False)
    try:
        started = jobs.start('A', 'B', Filters())
        assert started['search_policy']['prove_after_route'] is False
        key = started['job_id']
        paused = polls_until(jobs, key, lambda s: s['status'] != 'searching')[-1]
        assert paused['status'] == 'ok' and paused['can_continue'] is True
        assert paused['best_route']['hops'] == 4
        # A verified route whose shortestness is open is an incomplete search.
        assert paused['route_status'] == 'search_incomplete'
        assert paused['events'][-1]['type'] == 'search_paused'
        resumed = jobs.resume(key)
        assert resumed['events'] and any(e['type'] == 'search_resumed' for e in resumed['events'])
    finally:
        jobs.shutdown()


def test_a_withdrawn_route_is_reported_not_kept():
    """If the engine's identity guard retracts its best route, the server
    must stop calling it the best route rather than keep publishing it."""
    engine = ImprovingEngine(script=[
        {'status': 'ok', 'can_continue': True, 'paths': [LONG]},
        {'status': 'search_incomplete', 'can_continue': True, 'paths': []},
        {'status': 'ok', 'can_continue': False, 'paths': [SHORT], 'global_shortest_proven': True},
    ])
    jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=0)
    try:
        key = jobs.start('A', 'B', Filters())['job_id']
        states = polls_until(jobs, key, lambda s: s['status'] != 'searching')
        withdrawn = next(s for s in states if s['best_route'] is None)
        assert withdrawn['route_status'] == 'searching_no_path'
        assert withdrawn['events'][-1]['type'] == 'route_withdrawn'
        assert withdrawn['events'][-1]['previous_hops'] == 4
        final = states[-1]
        assert final['route_status'] == 'exact_route_proven' and final['best_route']['hops'] == 3
        assert final['metrics']['improvements'] == 0  # A new first route, not an improvement.
        assert [e['type'] for e in final['events']].count('first_path_found') == 2
    finally:
        jobs.shutdown()


def test_early_progress_route_is_versioned_like_any_other_state():
    """A route published through the engine's progress callback, mid-slice,
    goes through the same versioning as a slice result."""
    class ProgressEngine(ImprovingEngine):
        def run(self, budget):
            self.calls += 1
            if self.calls == 1:
                self.progress({'stage': 'check_candidate', 'works_retrieved': 3, 'people_explored': 2,
                               'best_result': {'paths': [LONG], 'version': 'evidence-v1'}})
                return {'status': 'search_incomplete', 'can_continue': True, 'paths': [LONG],
                        'coverage': {'failures': []}, 'version': 'evidence-v1',
                        'progress': {'works_retrieved': 3, 'people_explored': 2, 'requests': 1}}
            return {'status': 'ok', 'can_continue': False, 'paths': [SHORT], 'global_shortest_proven': True,
                    'coverage': {'failures': []}, 'version': 'evidence-v1',
                    'progress': {'works_retrieved': 9, 'people_explored': 5, 'requests': 2}}

    seen = []
    engine = ProgressEngine()
    jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=0)
    try:
        started = jobs.start('A', 'B', Filters())
        seen.append(started)
        assert started['best_route']['hops'] == 4 and started['route_status'] == 'verified_route_found'
        assert started['events'][1]['type'] == 'first_path_found'
        final = polls_until(jobs, started['job_id'], lambda s: s['status'] != 'searching')[-1]
        assert final['sequence_number'] > started['sequence_number']
        assert [e['type'] for e in final['events']] == [
            'search_started', 'first_path_found', 'path_improved', 'exact_proven', 'search_finished']
    finally:
        jobs.shutdown()


def test_every_published_state_serializes_and_round_trips():
    engine = ImprovingEngine()
    jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=0)
    try:
        key = jobs.start('A', 'B', Filters())['job_id']
        for state in polls_until(jobs, key, lambda s: s['status'] != 'searching'):
            wire = json.dumps(state, allow_nan=False)
            back = json.loads(wire)
            assert back == state
            assert isinstance(back['sequence_number'], int) and back['sequence_number'] >= 1
            assert set(back['metrics']) == {'elapsed_seconds', 'time_to_first_verified_path',
                                            'time_to_best_route', 'time_to_exact_proof',
                                            'improvements', 'first_hops', 'best_hops'}
            if back['best_route'] is not None:
                assert set(back['best_route']) == {'route_id', 'hops', 'alternatives', 'exact',
                                                   'found_at_seconds', 'version'}
    finally:
        jobs.shutdown()


def test_a_refused_oversized_state_does_not_advance_the_sequence_or_timeline():
    class Oversized(ImprovingEngine):
        def run(self, budget):
            self.calls += 1
            if self.calls == 1:
                return {'status': 'ok', 'can_continue': True, 'paths': [LONG], 'version': 'evidence-v1',
                        'coverage': {'failures': []}, 'progress': {'works_retrieved': 1, 'people_explored': 1, 'requests': 1}}
            return {'status': 'ok', 'can_continue': False, 'paths': [SHORT], 'version': 'evidence-v1',
                    'global_shortest_proven': True, 'coverage': {'failures': []},
                    'padding': 'x' * 70_000,
                    'progress': {'works_retrieved': 2, 'people_explored': 2, 'requests': 2}}

    engine = Oversized()
    jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=0, max_result_bytes=64 * 1024)
    try:
        found = jobs.start('A', 'B', Filters())
        assert found['best_route']['hops'] == 4 and found['status'] == 'searching'
        limited = polls_until(jobs, found['job_id'], lambda s: s['status'] != 'searching')[-1]
        assert limited['status'] == 'resource_limit'
        # The oversized 3-hop state was never installed: the retained route is
        # still the 4-hop one, with the honest status, and no version or
        # event ever described the refused improvement.
        assert limited['paths'] == found['paths'] and limited['best_route']['hops'] == 4
        assert limited['route_status'] == 'search_incomplete'
        assert limited['sequence_number'] > found['sequence_number']
        assert [e['type'] for e in limited['events']].count('path_improved') == 0
        assert all(e.get('hops') != 3 for e in limited['events'])
        assert limited['metrics']['best_hops'] == 4 and limited['metrics']['time_to_exact_proof'] is None
    finally:
        jobs.shutdown()


def test_http_responses_carry_the_delivery_fields(tmp_path):
    from test_acceptance_service import _LocalService, _snapshot
    from test_search_jobs import get_json
    path = tmp_path / 'current.json'
    path.write_text(json.dumps(_snapshot()))
    local = _LocalService(path)
    local.state.default_mode = 'live'
    engine = ImprovingEngine()
    local.state._jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=0)
    try:
        status, started = get_json(local, '/api/path?source=101&target=102')
        assert status == 200 and started['route_status'] == 'searching_no_path'
        assert started['sequence_number'] >= 1 and started['events'][0]['type'] == 'search_started'
        key = started['job_id']
        seen = [started]
        for _ in range(10):
            code, value = get_json(local, f'/api/search-jobs/{key}?mode=live')
            assert code == 200
            seen.append(value)
            if value['status'] != 'searching':
                break
        assert seen[-1]['route_status'] == 'exact_route_proven'
        assert [s['sequence_number'] for s in seen] == sorted(set(s['sequence_number'] for s in seen))
        assert any(s['route_status'] == 'verified_route_found' and s['status'] == 'searching' for s in seen)
        assert seen[-1]['paths'][0]['route_id'] == seen[-1]['best_route']['route_id']
    finally:
        local.state.shutdown()


@pytest.mark.parametrize('policy', [{'prove_after_route': 1}, {'prove_after_route': None}])
def test_invalid_delivery_policy_is_rejected(policy):
    with pytest.raises(ValueError):
        SearchJobs(lambda: None, **policy)


def test_a_route_the_engine_already_calls_shortest_is_terminal_even_if_the_bound_is_open():
    """A direct pair or an exhausted two-hop check proves shortestness while
    the HLBES bound is formally open, so the engine may say can_continue. There
    is nothing left to look for: the job must not keep spending requests."""
    engine = ImprovingEngine(script=[
        {'status': 'ok', 'can_continue': True, 'paths': [route('A', 'M', 'B')], 'global_shortest_proven': True},
        {'status': 'search_incomplete', 'can_continue': True, 'paths': [route('A', 'M', 'B')], 'global_shortest_proven': True},
    ])
    jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=0)
    try:
        started = jobs.start('A', 'B', Filters())
        assert started['status'] == 'ok' and started['can_continue'] is False
        assert started['route_status'] == 'exact_route_proven' and started['best_route']['exact'] is True
        assert engine.calls == 1 and engine.closed.wait(1)
        # Stopping a proven result changes nothing: it is not a stopped search.
        assert jobs.cancel(started['job_id'])['route_status'] == 'exact_route_proven'
        assert jobs.get(started['job_id'])['status'] == 'ok'
    finally:
        jobs.shutdown()


def test_delivery_tolerates_contract_violations_without_contradicting_itself():
    """Malformed or self-contradictory engine output must degrade honestly:
    no crash, no route without paths, no no_path beside a route, no
    negative hop count, and a withdrawn proof does not survive its route."""
    engine = ImprovingEngine(script=[
        {'status': 'search_incomplete', 'can_continue': True, 'paths': 7},
        {'status': 'no_path', 'can_continue': True, 'paths': [LONG]},
        {'status': 'ok', 'can_continue': True, 'paths': [{**SHORT, 'hops': -1}]},
        {'status': 'ok', 'can_continue': True, 'paths': [route('A', 'M', 'B')], 'global_shortest_proven': True},
    ])
    jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=0)
    try:
        started = jobs.start('A', 'B', Filters())
        assert started['paths'] == [] and started['best_route'] is None
        states = polls_until(jobs, started['job_id'], lambda s: s['status'] != 'searching')
        contradiction = states[0]  # 'no_path' beside a route: the route wins, and the search goes on.
        assert contradiction['route_status'] == 'verified_route_found' and contradiction['best_route']['hops'] == 4
        assert all(s['route_status'] != 'no_path' for s in states)
        negative = states[1]
        assert negative['best_route'] is None and negative['metrics']['best_hops'] is None
        assert negative['events'][-1]['type'] == 'route_withdrawn'
        final = states[-1]
        assert final['route_status'] == 'exact_route_proven' and final['best_route']['hops'] == 2
        assert final['metrics']['time_to_exact_proof'] >= final['metrics']['time_to_best_route']
    finally:
        jobs.shutdown()


def test_withdrawing_a_proven_route_withdraws_its_proof():
    engine = ImprovingEngine(script=[
        {'status': 'ok', 'can_continue': True, 'paths': [SHORT]},
        {'status': 'search_incomplete', 'can_continue': True, 'paths': []},
        {'status': 'ok', 'can_continue': False, 'paths': [LONG], 'global_shortest_proven': True},
    ])
    jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=0)
    try:
        key = jobs.start('A', 'B', Filters())['job_id']
        final = polls_until(jobs, key, lambda s: s['status'] != 'searching')[-1]
        metrics = final['metrics']
        assert final['best_route']['hops'] == 4 and final['best_route']['exact'] is True
        assert metrics['time_to_best_route'] <= metrics['time_to_exact_proof']
        assert [e['type'] for e in final['events']].count('exact_proven') == 1
    finally:
        jobs.shutdown()
