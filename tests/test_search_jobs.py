"""Owner-thread continuation, cancellation, capacity and HTTP boundary checks."""
from copy import deepcopy
import json
import threading
import time

import pytest

from hepgraph.deep_search import DeepSearch
from hepgraph.graph import Filters
from hepgraph.search_jobs import JobError, SearchJobs
from test_acceptance_service import _LocalService, _snapshot
from test_live_service import Transport
from hepgraph.remote import RemoteClient


def eventually(predicate, timeout=2):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(.002)
    raise AssertionError('Worker did not reach the expected state.')


class Engine:
    def __init__(self, blocking=False):
        self.blocking = blocking
        self.sessions = []

    def start(self, source, target, filters, *, cancel, progress):
        session = Session(cancel, progress, self.blocking)
        self.sessions.append(session)
        return session


class Session:
    def __init__(self, cancel, progress, blocking):
        self.cancel, self.progress, self.blocking = cancel, progress, blocking
        self.owner = threading.get_ident()
        self.calls = []
        self.closed = threading.Event()
        self.entered = threading.Event()
        self.route = {'hops': 2, 'people': [{'id': '1'}, {'id': '2'}, {'id': '3'}], 'edges': []}

    def run(self, budget):
        assert threading.get_ident() == self.owner
        self.calls.append(budget)
        self.entered.set()
        self.progress({'people_explored': 7, 'works_retrieved': 12, 'elapsed_seconds': 1,
                       'stage': 'Searching', 'best_result': {'paths': [self.route], 'version': 'evidence-v1'}})
        if self.blocking:
            self.cancel.wait(2)
            self.progress({'stage': 'late progress must not overwrite cancellation'})
            return {'status': 'ok', 'can_continue': True, 'paths': [self.route]}
        return {'status': 'search_incomplete' if len(self.calls) == 1 else 'ok',
                'paths': [self.route], 'version': 'evidence-v1',
                'can_continue': len(self.calls) == 1}

    def close(self):
        assert threading.get_ident() == self.owner
        self.closed.set()


class ContinuableSuccessSession(Session):
    def run(self, budget):
        assert threading.get_ident() == self.owner
        self.calls.append(budget)
        self.entered.set()
        return {'status': 'ok', 'paths': [self.route], 'version': 'evidence-v1',
                'can_continue': True}


class ContinuableSuccessEngine(Engine):
    def start(self, source, target, filters, *, cancel, progress):
        session = ContinuableSuccessSession(cancel, progress, False)
        self.sessions.append(session)
        return session


class LargeFinalSession(Session):
    def run(self, budget):
        self.calls.append(budget)
        return {'status': 'ok', 'paths': [self.route], 'version': 'evidence-v1',
                'can_continue': False, 'padding': 'x' * 45_000}


class LargeFinalEngine(Engine):
    def start(self, source, target, filters, *, cancel, progress):
        session = LargeFinalSession(cancel, progress, False)
        self.sessions.append(session)
        return session


class OversizedFinalSession(Session):
    def run(self, budget):
        self.calls.append(budget)
        route = deepcopy(self.route)
        route['edges'] = [{
            'source': '1', 'target': '2', 'types': ['coauthor'],
            'shared_works': 1,
            'works': [{'id': 'huge', 'title': 'x' * 80_000,
                       'author_count': 2, 'authors': ['1', '2']}],
            'phd': [],
        }]
        return {'status': 'ok', 'paths': [route], 'version': 'evidence-v1',
                'can_continue': False}


class OversizedFinalEngine(Engine):
    def start(self, source, target, filters, *, cancel, progress):
        session = OversizedFinalSession(cancel, progress, False)
        self.sessions.append(session)
        return session


class OversizedProgressSession(Session):
    def run(self, budget):
        self.calls.append(budget)
        route = deepcopy(self.route)
        route['people'][1]['name'] = 'x' * 80_000
        self.progress({'stage': 'validating', 'best_result': {
            'paths': [route], 'version': 'evidence-v1'}})
        return {'status': 'ok', 'paths': [self.route], 'version': 'evidence-v1',
                'can_continue': False}


class OversizedProgressEngine(Engine):
    def start(self, source, target, filters, *, cancel, progress):
        session = OversizedProgressSession(cancel, progress, False)
        self.sessions.append(session)
        return session


def test_continue_uses_same_worker_session_and_frozen_filters():
    engine = Engine()
    jobs = SearchJobs(lambda: engine)
    try:
        first = jobs.start('1', '3', Filters(max_authors=5))
        key = first['job_id']
        ended = eventually(lambda: value if (value := jobs.get(key))['status'] != 'searching' else None)
        assert ended['status'] == 'search_incomplete' and ended['can_continue']
        assert ended['paths'][0]['hops'] == 2
        ended['paths'].clear()
        assert jobs.get(key)['paths']  # Browser/client cannot mutate RAM evidence.
        resumed = jobs.resume(key)
        assert resumed['status'] == 'searching' and resumed['job_id'] == key
        eventually(lambda: jobs.get(key)['status'] == 'ok')
        assert len(engine.sessions) == 1
        assert len(engine.sessions[0].calls) == 2
        assert engine.sessions[0].calls[1].max_seconds == 900
        assert jobs.get(key)['filters']['max_authors'] == 5
        assert engine.sessions[0].closed.wait(1)
        with pytest.raises(JobError, match='cannot continue'):
            jobs.resume(key)
    finally:
        jobs.shutdown()


def test_cancel_is_immediate_preserves_evidence_and_ignores_late_updates():
    engine = Engine(blocking=True)
    jobs = SearchJobs(lambda: engine)
    try:
        key = jobs.start('1', '3', Filters())['job_id']
        eventually(lambda: engine.sessions)
        assert engine.sessions[0].entered.wait(1)
        eventually(lambda: jobs.get(key).get('paths'))
        assert jobs.cancel(key)['status'] == 'cancelled'
        assert engine.sessions[0].closed.wait(1)
        value = jobs.get(key)
        assert value['status'] == 'cancelled' and value['can_continue'] is False
        assert value['paths'][0]['hops'] == 2
        assert value['progress']['stage'] == 'Searching'
        with pytest.raises(JobError):
            jobs.resume(key)
    finally:
        jobs.shutdown()


def test_active_and_paused_capacity_are_bounded_and_expiry_releases_owner():
    clock = [0.0]
    engine = Engine()
    jobs = SearchJobs(lambda: engine, max_active=1, max_retained=1,
                      clock=lambda: clock[0], ttl=.05)
    try:
        key = jobs.start('1', '3', Filters())['job_id']
        eventually(lambda: jobs.get(key)['status'] != 'searching')
        with pytest.raises(JobError, match='workspace is full'):
            jobs.start('2', '4', Filters())
        clock[0] = 10.0
        with pytest.raises(JobError) as error:
            jobs.get(key)
        assert error.value.http_status == 404
        assert engine.sessions[0].closed.wait(1)
        next_key = jobs.start('2', '4', Filters())['job_id']
        assert next_key != key
    finally:
        jobs.shutdown()


def test_two_running_workers_reject_third_without_starting_it():
    engine = Engine(blocking=True)
    jobs = SearchJobs(lambda: engine)
    try:
        keys = [jobs.start('1', str(target), Filters())['job_id'] for target in (2, 3)]
        with pytest.raises(JobError) as error:
            jobs.start('1', '4', Filters())
        assert error.value.http_status == 503
        eventually(lambda: len(engine.sessions) == 2)
        for key in keys:
            jobs.cancel(key)
        assert all(session.closed.wait(1) for session in engine.sessions)
    finally:
        jobs.shutdown()


def test_identical_directional_job_reuses_active_worker_and_filter_key_includes_min_authors():
    engine = Engine(blocking=True)
    jobs = SearchJobs(lambda: engine, max_active=2)
    try:
        first = jobs.start('1', '3', Filters(max_authors=None, min_authors=11))
        eventually(lambda: engine.sessions)
        assert engine.sessions[0].entered.wait(1)
        duplicate = jobs.start('1', '3', Filters(max_authors=None, min_authors=11))
        different = jobs.start('1', '3', Filters(max_authors=None, min_authors=12))
        assert duplicate['job_id'] == first['job_id']
        assert duplicate['reused'] is True and duplicate['reuse_state'] == 'active'
        assert different['job_id'] != first['job_id']
        assert eventually(lambda: len(engine.sessions) == 2)
        info = jobs.info()
        assert info['directional_keys'] is True
        assert info['counters'] == {'started': 2, 'reused_active': 1, 'reused_completed': 0}
        jobs.cancel(first['job_id']); jobs.cancel(different['job_id'])
    finally:
        jobs.shutdown()


def test_recent_success_is_reused_but_cancelled_job_is_not():
    engine = Engine()
    jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=0)
    try:
        first = jobs.start('1', '3', Filters())
        finished = eventually(lambda: value if (value := jobs.get(first['job_id']))['status'] == 'ok' else None)
        duplicate = jobs.start('1', '3', Filters())
        assert duplicate['job_id'] == finished['job_id']
        assert duplicate['reused'] is True and duplicate['reuse_state'] == 'retained'
        assert len(engine.sessions) == 1

        blocking = Engine(blocking=True)
        cancelled_jobs = SearchJobs(lambda: blocking)
        try:
            cancelled = cancelled_jobs.start('4', '5', Filters())
            eventually(lambda: blocking.sessions)
            cancelled_jobs.cancel(cancelled['job_id'])
            assert blocking.sessions[0].closed.wait(1)
            replacement = cancelled_jobs.start('4', '5', Filters())
            assert replacement['job_id'] != cancelled['job_id'] and replacement['reused'] is False
            cancelled_jobs.cancel(replacement['job_id'])
        finally:
            cancelled_jobs.shutdown()
    finally:
        jobs.shutdown()


def test_fifth_verified_continuable_search_retires_oldest_session_but_keeps_result():
    engine = ContinuableSuccessEngine()
    jobs = SearchJobs(lambda: engine, max_active=2, max_sessions=4, max_retained=8)
    try:
        started = []
        for target in ('2', '3', '4', '5'):
            row = jobs.start('1', target, Filters())
            started.append(row['job_id'])
            eventually(lambda job_id=row['job_id']: jobs.get(job_id)['status'] == 'ok')
        assert jobs.info()['resumable_sessions'] == 4

        fifth = jobs.start('1', '6', Filters())
        eventually(lambda: jobs.get(fifth['job_id'])['status'] == 'ok')
        retained = jobs.get(started[0])
        assert retained['status'] == 'ok' and retained['paths']
        assert retained['can_continue'] is False and retained['session_retired'] is True
        assert engine.sessions[0].closed.is_set()
        info = jobs.info()
        assert info['retained'] == 5 and info['resumable_sessions'] == 4
        assert info['result_bytes'] <= info['result_bytes_limit']
    finally:
        jobs.shutdown()


def test_compact_result_lru_enforces_aggregate_byte_ceiling() -> None:
    engine = LargeFinalEngine()
    jobs = SearchJobs(lambda: engine, max_retained=8, max_result_bytes=64 * 1024)
    try:
        first = jobs.start('1', '2', Filters())['job_id']
        eventually(lambda: engine.sessions and engine.sessions[0].closed.is_set())
        second = jobs.start('1', '3', Filters())['job_id']
        eventually(lambda: len(engine.sessions) == 2 and engine.sessions[1].closed.is_set())
        with pytest.raises(JobError) as expired:
            jobs.get(first)
        assert expired.value.http_status == 404
        assert jobs.get(second)['status'] == 'ok'
        info = jobs.info()
        assert info['retained'] == 1
        assert info['result_bytes'] <= info['result_bytes_limit'] == 64 * 1024
    finally:
        jobs.shutdown()


@pytest.mark.parametrize('engine_class', [OversizedFinalEngine, OversizedProgressEngine])
def test_single_oversized_result_is_retained_as_explicit_bounded_terminal_state(engine_class) -> None:
    engine = engine_class()
    jobs = SearchJobs(lambda: engine, max_retained=8, max_result_bytes=64 * 1024)
    try:
        job_id = jobs.start('1', '2', Filters())['job_id']
        terminal = eventually(lambda: value if (value := jobs.get(job_id))['status'] != 'searching' else None)
        assert terminal['status'] == 'resource_limit'
        assert terminal['can_continue'] is False
        assert terminal['global_shortest_proven'] is False
        assert terminal['paths'] == []
        assert 'not retained' in terminal['message'] or 'being presented' in terminal['message']
        assert terminal['coverage']['result_retention']['limit_bytes'] == 64 * 1024
        assert engine.sessions[0].closed.wait(1)
        info = jobs.info()
        assert info['retained'] == 1
        assert info['result_bytes'] <= info['result_bytes_limit'] == 64 * 1024
        # The terminal state remains queryable rather than silently evicting
        # the job that just completed.
        assert jobs.get(job_id)['status'] == 'resource_limit'
    finally:
        jobs.shutdown()


@pytest.fixture
def service(tmp_path):
    path = tmp_path / 'current.json'
    path.write_text(json.dumps(_snapshot()))
    local = _LocalService(path)
    local.state.default_mode = 'live'
    transport = Transport()
    local.state._remote_client = RemoteClient(transport=transport, clock=transport.clock, sleep=transport.sleep)
    yield local, transport, tmp_path
    local.state.shutdown()


def get_json(service, path, **kwargs):
    status, headers, body = service.request(path, **kwargs)
    return status, json.loads(body) if body else None


def test_default_deep_http_flow_normalizes_real_transport_and_keeps_disk_unchanged(service):
    local, transport, directory = service
    before = {str(p): p.read_bytes() for p in directory.rglob('*') if p.is_file()}
    status, started = get_json(local, '/api/path?source=101&target=102&genealogy=false')
    assert status == 200 and started['job_id']
    key = started['job_id']
    def terminal():
        code, value = get_json(local, f'/api/search-jobs/{key}?mode=live')
        assert code == 200
        return value if value['status'] != 'searching' else None
    result = eventually(terminal)
    assert result['status'] == 'ok' and result['paths'][0]['hops'] == 1
    assert result['global_shortest_proven'] is True
    assert result['paths'][0]['edges'][0]['works'][0]['source_url'].endswith('/500')
    assert result['filters']['genealogy'] is False
    assert before == {str(p): p.read_bytes() for p in directory.rglob('*') if p.is_file()}


def test_http_cancel_continue_and_frozen_filter_configuration(service):
    local, _, _ = service
    engine = Engine()
    local.state._jobs = SearchJobs(lambda: engine)
    _, value = get_json(local, '/api/path?source=101&target=102&max_authors=5')
    key = value['job_id']
    eventually(lambda: local.state._jobs.get(key)['can_continue'])
    path = f'/api/search-jobs/{key}/continue?mode=live&max_authors=10'
    assert get_json(local, path)[0] == 405
    status, value = get_json(local, path, method='POST', extra_headers={'Origin': 'http://localhost'})
    assert status == 200 and value['filters']['max_authors'] == 5
    assert get_json(local, f'/api/search-jobs/{key}/cancel?mode=live', method='POST')[1]['status'] == 'cancelled'


@pytest.mark.parametrize('extra_headers', [
    {'Origin': 'https://attacker.invalid'}, {'Origin': 'null'},
    {'Content-Length': '2'}, {'Transfer-Encoding': 'chunked'},
])
def test_control_requests_reject_cross_origin_and_bodies_without_starting_work(service, extra_headers):
    local, transport, _ = service
    status, result = get_json(local, '/api/search-jobs/' + 'a' * 32 + '/cancel?mode=live',
                              method='POST', extra_headers=extra_headers)
    assert status in {400, 403} and result['status'] == 'invalid_request'
    assert transport.calls == [] and local.state._jobs is None


def test_head_and_invalid_parameters_never_start_a_search(service):
    local, transport, _ = service
    assert get_json(local, '/api/path?source=101&target=102', method='HEAD')[0] == 405
    for query in ('source=0&target=102', 'source=101&target=102&max_authors=0',
                  'source=101&target=102&search=anything', 'source=101&source=102&target=103'):
        assert get_json(local, '/api/path?' + query)[0] == 400
    assert transport.calls == [] and local.state._jobs is None
