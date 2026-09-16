"""Request-driven continuation, cancellation, capacity and HTTP boundary checks.

A search advances only inside start/poll/continue calls, one driver at a time.
The fakes below assert that invariant - no two calls on a session overlap -
rather than a particular owning thread, and use ``drive_in_background`` where a
test needs a slice to be in flight while it acts from the outside.
"""
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
        self.busy = threading.Lock()
        self.calls = []
        self.closed = threading.Event()
        self.entered = threading.Event()
        self.route = {'hops': 2, 'people': [{'id': '1'}, {'id': '2'}, {'id': '3'}], 'edges': []}

    def _enter(self):
        # The contract: calls never overlap, whichever thread makes them.
        assert self.busy.acquire(blocking=False), 'two requests drove one session at once'
        assert not self.closed.is_set(), 'a closed session was driven again'

    def run(self, budget):
        self._enter()
        try:
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
        finally:
            self.busy.release()

    def close(self):
        self._enter()
        self.closed.set()
        self.busy.release()


def drive_in_background(jobs, key):
    """Poll once on another thread, so a slice is in flight while the test acts."""
    thread = threading.Thread(target=lambda: jobs.get(key), daemon=True)
    thread.start()
    return thread


class ContinuableSuccessSession(Session):
    def run(self, budget):
        self._enter()
        try:
            self.calls.append(budget)
            self.entered.set()
            return {'status': 'ok', 'paths': [self.route], 'version': 'evidence-v1',
                    'can_continue': True}
        finally:
            self.busy.release()


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
        # Continuing runs a slice inside the request, so it may already be done.
        assert resumed['status'] in {'searching', 'ok'} and resumed['job_id'] == key
        eventually(lambda: jobs.get(key)['status'] == 'ok')
        assert len(engine.sessions) == 1
        assert len(engine.sessions[0].calls) == 2
        # The continued run carries the extended session ceilings, time-boxed
        # to one request's slice rather than the whole 900 s allowance.
        assert engine.sessions[0].calls[1].max_works == 50_000
        assert engine.sessions[0].calls[1].max_seconds <= jobs.poll_slice
        assert jobs.get(key)['filters']['max_authors'] == 5
        assert engine.sessions[0].closed.wait(1)
        with pytest.raises(JobError, match='cannot continue'):
            jobs.resume(key)
    finally:
        jobs.shutdown()


def test_cancel_is_immediate_preserves_evidence_and_ignores_late_updates():
    engine = Engine(blocking=True)
    jobs = SearchJobs(lambda: engine, start_slice=0)
    try:
        key = jobs.start('1', '3', Filters())['job_id']
        driver = drive_in_background(jobs, key)
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
        driver.join(3)
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
    jobs = SearchJobs(lambda: engine, start_slice=0)
    try:
        keys = [jobs.start('1', str(target), Filters())['job_id'] for target in (2, 3)]
        drivers = [drive_in_background(jobs, key) for key in keys]
        eventually(lambda: len(engine.sessions) == 2 and all(s.entered.is_set() for s in engine.sessions))
        with pytest.raises(JobError) as error:
            jobs.start('1', '4', Filters())
        assert error.value.http_status == 503
        for key in keys:
            jobs.cancel(key)
        assert all(session.closed.wait(1) for session in engine.sessions)
        for driver in drivers:
            driver.join(3)
    finally:
        jobs.shutdown()


def test_identical_directional_job_reuses_active_worker_and_filter_key_includes_min_authors():
    engine = Engine(blocking=True)
    jobs = SearchJobs(lambda: engine, max_active=2, start_slice=0)
    try:
        first = jobs.start('1', '3', Filters(max_authors=None, min_authors=11))
        driver = drive_in_background(jobs, first['job_id'])
        eventually(lambda: engine.sessions)
        assert engine.sessions[0].entered.wait(1)
        duplicate = jobs.start('1', '3', Filters(max_authors=None, min_authors=11))
        different = jobs.start('1', '3', Filters(max_authors=None, min_authors=12))
        # A job only acquires its engine session once something drives it.
        other = drive_in_background(jobs, different['job_id'])
        assert duplicate['job_id'] == first['job_id']
        assert duplicate['reused'] is True and duplicate['reuse_state'] == 'active'
        assert different['job_id'] != first['job_id']
        assert eventually(lambda: len(engine.sessions) == 2)
        info = jobs.info()
        assert info['directional_keys'] is True
        assert info['counters'] == {'started': 2, 'reused_active': 1, 'reused_completed': 0}
        jobs.cancel(first['job_id']); jobs.cancel(different['job_id'])
        driver.join(3); other.join(3)
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


def test_idle_expiry_frees_capacity_and_marks_the_job_cancelled():
    clock = [0.0]
    engine = Engine()
    jobs = SearchJobs(lambda: engine, max_active=1, clock=lambda: clock[0],
                      start_slice=0, auto_continue=True, retry_delay=0, idle_seconds=30)
    try:
        key = jobs.start('1', '3', Filters())['job_id']
        # Nothing polls; the job is still nominally active and searching.
        assert jobs.jobs[key].active and jobs.jobs[key].data['status'] == 'searching'
        with pytest.raises(JobError, match='already running'):
            jobs.start('2', '4', Filters())
        clock[0] = 31.0
        stopped = jobs.get(key)
        assert stopped['status'] == 'cancelled' and stopped['can_continue'] is False
        assert 'nothing asked about it' in stopped['message']
        assert jobs.info()['active'] == 0
        # The slot is free again.
        assert jobs.start('2', '4', Filters())['job_id'] != key
        assert engine.sessions == [] or all(s.closed.is_set() for s in engine.sessions)
    finally:
        jobs.shutdown()


class SlowFinishSession(Session):
    """Blocks inside run() until told to finish, then returns a continuable result."""

    def __init__(self, cancel, progress, blocking):
        super().__init__(cancel, progress, blocking)
        self.release = threading.Event()

    def run(self, budget):
        self._enter()
        try:
            self.calls.append(budget)
            self.entered.set()
            self.release.wait(3)
            return {'status': 'search_incomplete', 'can_continue': True, 'paths': [],
                    'coverage': {'failures': []},
                    'progress': {'works_retrieved': len(self.calls), 'people_explored': 1, 'requests': len(self.calls)}}
        finally:
            self.busy.release()


class SlowFinishEngine(Engine):
    def start(self, source, target, filters, *, cancel, progress):
        session = SlowFinishSession(cancel, progress, False)
        self.sessions.append(session)
        return session


def test_a_cancel_during_a_slice_is_never_overwritten_by_that_slice():
    """The slice's continuation decision re-checks cancel under the lock it writes with."""
    engine = SlowFinishEngine()
    jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=0, start_slice=0)
    try:
        key = jobs.start('1', '3', Filters())['job_id']
        driver = drive_in_background(jobs, key)
        assert eventually(lambda: engine.sessions and engine.sessions[0].entered.is_set())
        assert jobs.cancel(key)['status'] == 'cancelled'
        engine.sessions[0].release.set()
        driver.join(3)
        job = jobs.jobs[key]
        assert job.data['status'] == 'cancelled' and job.worker_done and not job.active
        assert engine.sessions[0].closed.is_set()
        assert jobs.info()['active'] == 0
    finally:
        jobs.shutdown()


def test_continuing_after_a_long_read_is_not_reaped_as_abandoned():
    clock = [0.0]
    engine = ContinuableSuccessEngine()
    jobs = SearchJobs(lambda: engine, clock=lambda: clock[0], idle_seconds=30, start_slice=0)
    try:
        key = jobs.start('1', '3', Filters())['job_id']
        paused = jobs.get(key)
        assert paused['status'] == 'ok' and paused['can_continue'] is True
        clock[0] = 600.0  # the user reads the result for ten minutes
        resumed = jobs.resume(key)
        assert resumed['status'] in {'ok', 'searching'}
        assert jobs.get(key)['status'] != 'cancelled'
        assert 'nothing asked about it' not in (jobs.get(key).get('message') or '')
    finally:
        jobs.shutdown()


def test_a_slice_in_flight_is_not_reaped_at_the_idle_boundary():
    clock = [0.0]
    engine = SlowFinishEngine()
    jobs = SearchJobs(lambda: engine, clock=lambda: clock[0], idle_seconds=30,
                      start_slice=0, auto_continue=True, retry_delay=0)
    try:
        key = jobs.start('1', '3', Filters())['job_id']
        clock[0] = 29.0
        driver = drive_in_background(jobs, key)
        assert eventually(lambda: engine.sessions and engine.sessions[0].entered.is_set())
        clock[0] = 31.0
        jobs.info()  # runs _prune while the slice is in flight
        assert jobs.jobs[key].data['status'] == 'searching', 'a running slice is not abandonment'
        engine.sessions[0].release.set()
        driver.join(3)
    finally:
        jobs.shutdown()


def test_a_finalized_job_never_acquires_a_fresh_engine_session():
    """cancel() between a poll's decision and its slice must not open a session for nobody."""
    engine = Engine()
    jobs = SearchJobs(lambda: engine, start_slice=0)
    try:
        key = jobs.start('1', '3', Filters())['job_id']
        job = jobs.jobs[key]
        assert job.session is None
        jobs.cancel(key)
        jobs.get(key)
        assert job.session is None and engine.sessions == []
    finally:
        jobs.shutdown()


def test_a_dead_upstream_still_backs_off_and_eventually_pauses():
    from test_automatic_search import FailingEngine

    now = [0.0]
    engine = FailingEngine(clock=now)
    jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=5, max_stalled_runs=3,
                      clock=lambda: now[0], start_slice=0)
    try:
        key = jobs.start('1', '3', Filters())['job_id']
        job = jobs.jobs[key]
        delays = []
        for _ in range(6):
            now[0] = max(now[0], job.next_attempt_at)
            before = engine.calls
            jobs.get(key)
            if engine.calls > before:
                delays.append(job.next_attempt_at - now[0])
            if job.data['status'] != 'searching':
                break
        # Failed requests are not progress: the delay grows and the job pauses.
        assert job.data['status'] != 'searching' and job.data['can_continue'] is True
        assert engine.calls <= 4
    finally:
        jobs.shutdown()


def test_an_upstream_cooldown_waits_instead_of_pausing_as_exhausted():
    """A 429 cooldown refuses every slice instantly. That is not exhaustion and
    not stalling: the job stays searching, says why, and retries after the wait."""
    class CooldownSession(Session):
        def run(self, budget):
            self._enter()
            try:
                self.calls.append(budget)
                return {'status': 'resource_limit', 'can_continue': True, 'paths': [],
                        'message': "Waiting 42s for INSPIRE's rate limit before continuing.",
                        'retry_after': 42.0, 'coverage': {'failures': []},
                        'progress': {'works_retrieved': 0, 'people_explored': 0, 'requests': 0}}
            finally:
                self.busy.release()

    class CooldownEngine(Engine):
        def start(self, source, target, filters, *, cancel, progress):
            session = CooldownSession(cancel, progress, False)
            self.sessions.append(session)
            return session

    clock = [0.0]
    engine = CooldownEngine()
    jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=5, max_stalled_runs=3,
                      clock=lambda: clock[0])
    try:
        key = jobs.start('1', '3', Filters())['job_id']
        job = jobs.jobs[key]
        assert job.data['status'] == 'searching'
        assert job.data['progress']['stage'] == 'rate_limit_wait'
        assert 'rate limit' in job.data['message']
        assert job.next_attempt_at == 42.0 and job.stalled_runs == 0
        for _ in range(10):
            jobs.get(key)          # nothing is due yet: no slice, no stall count
        assert len(engine.sessions[0].calls) == 1 and job.data['status'] == 'searching'
        clock[0] = 42.0
        jobs.get(key)
        assert len(engine.sessions[0].calls) == 2 and job.stalled_runs == 0
    finally:
        jobs.shutdown()


def test_polling_a_paused_job_never_blocks_its_retirement():
    """A poll on a paused job must not touch its drive lock, or start() retiring
    it as a victim would fail spuriously and destroy its continuation."""
    engine = ContinuableSuccessEngine()
    jobs = SearchJobs(lambda: engine, max_active=1, max_sessions=1, start_slice=0)
    try:
        key = jobs.start('1', '3', Filters())['job_id']
        assert jobs.get(key)['status'] == 'ok'              # paused, can_continue
        stop = threading.Event()
        pollers = [threading.Thread(target=lambda: [jobs.get(key) for _ in iter(lambda: stop.is_set(), True)],
                                    daemon=True) for _ in range(3)]
        for thread in pollers:
            thread.start()
        try:
            for _ in range(20):
                jobs.start('2', '4', Filters(min_shared=2))   # must never see 'still releasing'
        finally:
            stop.set()
            for thread in pollers:
                thread.join(3)
    finally:
        jobs.shutdown()
