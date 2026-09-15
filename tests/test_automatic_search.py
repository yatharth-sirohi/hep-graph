"""Automatic continuation owns one session, backs off and remains cancellable."""
import threading

import pytest

from hepgraph.graph import Filters
from hepgraph.search_jobs import SearchJobs
from test_search_jobs import Engine, eventually


def test_automatic_checkpoint_continues_same_session_without_a_browser_post():
    engine = Engine()
    jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=0)
    try:
        key = jobs.start('1', '3', Filters(max_authors=5))['job_id']
        value = eventually(lambda: value if (value := jobs.get(key))['status'] == 'ok' else None)
        assert value['automatic_continuations'] == 1
        assert value['filters']['max_authors'] == 5
        assert len(engine.sessions) == 1 and len(engine.sessions[0].calls) == 2
        assert engine.sessions[0].closed.wait(1)
    finally:
        jobs.shutdown()


class FailingEngine:
    def __init__(self, *, message='INSPIRE is unavailable.', clock=None):
        self.message, self.clock = message, clock
        self.calls = 0
        self.closed = threading.Event()

    def start(self, source, target, filters, *, cancel, progress):
        self.owner = threading.get_ident()
        return self

    def run(self, budget):
        assert threading.get_ident() == self.owner
        self.calls += 1
        if self.clock is not None:
            self.clock[0] += 2
        return {'status': 'search_incomplete', 'can_continue': True,
                'message': self.message, 'paths': [],
                'progress': {'works_retrieved': 0, 'people_explored': 0}}

    def close(self):
        assert threading.get_ident() == self.owner
        self.closed.set()


def test_stop_interrupts_automatic_retry_wait_and_keeps_capacity_until_closed():
    engine = FailingEngine()
    jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=60)
    try:
        key = jobs.start('1', '3', Filters())['job_id']
        eventually(lambda: jobs.get(key)['automatic_continuations'] == 1)
        assert jobs.get(key)['status'] == 'searching'
        assert jobs.cancel(key)['status'] == 'cancelled'
        assert engine.closed.wait(1)
        assert engine.calls == 1
    finally:
        jobs.shutdown()


def test_persistent_failure_pauses_without_busy_loop_or_claiming_no_path():
    engine = FailingEngine()
    jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=0, max_stalled_runs=2)
    try:
        key = jobs.start('1', '3', Filters())['job_id']
        value = eventually(lambda: value if (value := jobs.get(key))['status'] != 'searching' else None)
        assert value['status'] == 'search_incomplete' and value['can_continue']
        assert value['paths'] == [] and engine.calls == 3
    finally:
        jobs.shutdown()


def test_session_memory_ceiling_is_not_retried_forever():
    engine = FailingEngine(message='The deep-search work ceiling was reached.')
    jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=0)
    try:
        key = jobs.start('1', '3', Filters())['job_id']
        value = eventually(lambda: value if (value := jobs.get(key))['status'] != 'searching' else None)
        assert engine.calls == 2  # Standard allowance can grow once to extended.
        assert value['can_continue']
    finally:
        jobs.shutdown()


def test_automatic_wall_time_guard_can_be_explicitly_continued():
    now = [0.0]
    engine = FailingEngine(clock=now)
    jobs = SearchJobs(lambda: engine, auto_continue=True, retry_delay=0,
                      max_auto_seconds=3, clock=lambda: now[0])
    try:
        key = jobs.start('1', '3', Filters())['job_id']
        eventually(lambda: jobs.get(key)['status'] != 'searching')
        assert engine.calls == 2
        jobs.resume(key)
        eventually(lambda: engine.calls == 4 and jobs.get(key)['status'] != 'searching')
    finally:
        jobs.shutdown()


@pytest.mark.parametrize('policy', [{'max_auto_seconds': float('nan')},
                                    {'retry_delay': -1}, {'max_stalled_runs': True}])
def test_invalid_automatic_policy_is_rejected(policy):
    with pytest.raises(ValueError):
        SearchJobs(lambda: None, **policy)
