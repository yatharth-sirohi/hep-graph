"""Bounded, cancellable live searches; all retrieved state stays in RAM.

A search advances only inside HTTP requests.  Starting a job runs a short first
slice before the response is written, and every poll runs another bounded slice
before answering, so the engine's frontier, page cursors and proof state live in
one process but never depend on a thread being scheduled between requests.

That is the shape a serverless runtime actually offers.  The previous design ran
each search on a daemon thread and let the browser poll; on Vercel the process is
frozen whenever no request is in flight, so that thread only ran during the
~130 ms a poll took every 1.5 s.  Measured on a one-hop pair: 19 s at a 1.5 s
poll interval, 2.6 s at 0.25 s, 1.4 s locally - the same work, paced entirely
by how often a request happened to be open.  Worse, an 8 s upstream deadline
would elapse while the thread was frozen mid-request, which the engine then
treated as an upstream failure and backed off from.

Exactly one request drives a given job at a time; a poll that arrives while
another is driving just reads the current state.
"""
from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
import dataclasses
import json
import logging
import threading
import time
import uuid

from .deep_search import DeepBudget

LOG = logging.getLogger(__name__)
MAX_RETAINED_RESULT_BYTES = 8 * 1024 * 1024


class JobError(ValueError):
    def __init__(self, code, message, http_status=400):
        super().__init__(message)
        self.code, self.message, self.http_status = code, message, http_status


class _Job:
    def __init__(self, source, target, filters, coverage, now):
        self.id = uuid.uuid4().hex
        self.source, self.target, self.filters = source, target, filters
        # Keep this directional: all current progress and displayed people are
        # oriented from source to target, so reverse reuse would require a full
        # result/progress transformation rather than only swapping the key.
        self.key = (source, target, json.dumps(filters.to_dict(), sort_keys=True,
                                                separators=(',', ':')))
        self.cancel = threading.Event()
        self.retire = threading.Event()
        self.closed = threading.Event()
        # One request advances this job at a time. The engine session is not
        # thread-bound; it is bound to whoever holds this lock.
        self.drive = threading.Lock()
        self.session = None
        self.budget = None
        self.auto_started = now
        self.stalled_runs = 0
        self.last_progress = None
        # A transient upstream failure schedules the next attempt instead of
        # sleeping: a request cannot sleep for the caller.
        self.next_attempt_at = 0.0
        self.failures_seen = 0
        self.last_driven_at = now
        self.active = True
        self.worker_done = False
        self.expired = False
        self.paused_at = None
        self.finished_at = None
        self.generation = 0
        self.data = {
            'job_id': self.id, 'status': 'searching', 'mode': 'live',
            'version': 'live-deep-v1', 'filters': filters.to_dict(),
            'coverage': deepcopy(coverage), 'source': source, 'target': target,
            'exact': False, 'can_continue': False, 'paths': [],
            'progress': {'people_explored': 0, 'works_retrieved': 0,
                         'elapsed_seconds': 0, 'stage': 'Starting the search'},
            'message': 'Searching INSPIRE for a documented connection.',
        }


class SearchJobs:
    def __init__(self, engine_factory, *, coverage=None, standard_budget=None,
                 extended_budget=None, ttl=1200.0, max_active=2,
                 max_retained=32, max_sessions=4,
                 max_result_bytes=MAX_RETAINED_RESULT_BYTES,
                 clock=time.monotonic, auto_continue=False,
                 max_auto_seconds=7200.0, retry_delay=5.0, max_stalled_runs=12,
                 start_slice=3.0, poll_slice=5.0, idle_seconds=120.0):
        self.engine_factory = engine_factory
        self.coverage = coverage or {'complete': False, 'mode': 'live',
                                    'label': 'Live INSPIRE — search in progress'}
        self.standard_budget = standard_budget or DeepBudget.standard()
        self.extended_budget = extended_budget or DeepBudget.extended()
        self.ttl = ttl
        if isinstance(max_sessions, int) and not isinstance(max_sessions, bool) and max_sessions > max_retained:
            max_sessions = max_retained
        if (isinstance(max_active, bool) or not isinstance(max_active, int) or not 1 <= max_active <= 8
                or isinstance(max_sessions, bool) or not isinstance(max_sessions, int)
                or not max_active <= max_sessions <= 16
                or isinstance(max_retained, bool) or not isinstance(max_retained, int)
                or not max_sessions <= max_retained <= 128
                or isinstance(max_result_bytes, bool) or not isinstance(max_result_bytes, int)
                or not 64 * 1024 <= max_result_bytes <= MAX_RETAINED_RESULT_BYTES):
            raise ValueError('Invalid search retention limits.')
        self.max_active, self.max_retained = max_active, max_retained
        self.max_sessions = max_sessions
        self.max_result_bytes = max_result_bytes
        self.clock = clock
        if (not isinstance(auto_continue, bool) or isinstance(max_auto_seconds, bool)
                or not isinstance(max_auto_seconds, (int, float))
                or not 1 <= max_auto_seconds <= 86400
                or isinstance(retry_delay, bool) or not isinstance(retry_delay, (int, float))
                or not 0 <= retry_delay <= 60
                or isinstance(max_stalled_runs, bool) or not isinstance(max_stalled_runs, int)
                or not 1 <= max_stalled_runs <= 100):
            raise ValueError('Invalid automatic continuation policy.')
        for name, value in (('start_slice', start_slice), ('poll_slice', poll_slice)):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 60:
                raise ValueError(f'{name} must be between 0 and 60 seconds.')
        if isinstance(idle_seconds, bool) or not isinstance(idle_seconds, (int, float)) or not 1 <= idle_seconds <= 3600:
            raise ValueError('idle_seconds must be between 1 and 3600 seconds.')
        # A searching job only advances when somebody polls it. One that nobody
        # has polled for this long has been abandoned - a closed tab - and must
        # not keep an active slot for ever.
        self.idle_seconds = float(idle_seconds)
        self.auto_continue = auto_continue
        self.max_auto_seconds = max_auto_seconds
        self.retry_delay = retry_delay
        self.max_stalled_runs = max_stalled_runs
        # Seconds of engine work a request may perform before answering.
        self.start_slice, self.poll_slice = float(start_slice), float(poll_slice)
        self.lock = threading.RLock()
        self.jobs = OrderedDict()
        self.closed = False
        self.reuse_counters = {'started': 0, 'reused_active': 0, 'reused_completed': 0}

    def _active_count(self):
        return sum(job.active for job in self.jobs.values())

    def _session_count(self):
        return sum(not job.worker_done for job in self.jobs.values())

    @staticmethod
    def _job_bytes(job):
        return len(json.dumps(job.data, ensure_ascii=False, separators=(',', ':'),
                              allow_nan=False).encode('utf-8'))

    def _retained_bytes(self):
        return sum(self._job_bytes(job) for job in self.jobs.values())

    def _replace_job_data(self, job, candidate):
        """Install one result only when the aggregate retained-data cap holds.

        Every caller holds ``self.lock``.  Closed compact results may be
        evicted to make room, but an active or resumable session is never
        discarded.  Checking before assignment keeps the advertised byte
        ceiling true even while a worker is finalizing a large response.
        """
        candidate_bytes = len(json.dumps(candidate, ensure_ascii=False,
                                         separators=(',', ':'),
                                         allow_nan=False).encode('utf-8'))
        while True:
            other_bytes = sum(self._job_bytes(item) for item in self.jobs.values()
                              if item is not job)
            if other_bytes + candidate_bytes <= self.max_result_bytes:
                job.data = candidate
                return True
            removable = next((job_id for job_id, item in self.jobs.items()
                              if item is not job and item.worker_done and not item.active), None)
            if removable is None:
                return False
            del self.jobs[removable]

    def _update_job_data(self, job, **changes):
        candidate = deepcopy(job.data)
        candidate.update(deepcopy(changes))
        return self._replace_job_data(job, candidate)

    def _retention_limit_result(self, job):
        """Return a small, explicit terminal result after an oversized update.

        If an earlier verified route already fit in the cache, retain it.  A
        route first seen only inside the oversized update is not partially
        serialized or relabeled as evidence; callers receive an honest
        resource-limit state instead.
        """
        prior_paths = deepcopy(job.data.get('paths', []))
        result = {
            'job_id': job.id, 'status': 'resource_limit', 'mode': 'live',
            'version': job.data.get('version', 'live-deep-incomplete'),
            'filters': job.filters.to_dict(), 'source': job.source,
            'target': job.target, 'exact': False, 'can_continue': False,
            'paths': prior_paths,
            'exact_for_retrieved_graph': bool(
                prior_paths and job.data.get('exact_for_retrieved_graph')),
            'global_shortest_proven': bool(
                prior_paths and job.data.get('global_shortest_proven')),
            'alternatives_truncated': bool(
                prior_paths and job.data.get('alternatives_truncated')),
            'progress': deepcopy(job.data.get('progress', {})),
            'coverage': {
                'complete': False,
                'mode': 'live',
                'label': 'Live INSPIRE — result retention limit reached',
                'result_retention': {
                    'status': 'resource_limit',
                    'limit_bytes': self.max_result_bytes,
                    'storage': 'temporary_memory',
                },
            },
            'message': (
                'The previously verified route remains available, but the exact search '
                'produced more response data than the bounded temporary result cache can retain.'
                if prior_paths else
                'The search produced more response data than the bounded temporary result cache '
                'can retain, so no route from that oversized response is being presented.'
            ),
        }
        if self._replace_job_data(job, result):
            return
        # This variant is guaranteed to be smaller than a newly admitted job.
        # Drop prior route evidence only if concurrent in-use results leave no
        # room for the evidence-preserving terminal form.
        result['paths'] = []
        result['exact_for_retrieved_graph'] = False
        result['global_shortest_proven'] = False
        result['alternatives_truncated'] = False
        result['message'] = ('The search exceeded the bounded temporary result cache, and its '
                             'oversized response was not retained.')
        if not self._replace_job_data(job, result):
            raise RuntimeError('The bounded result cache could not retain a terminal job state.')

    def _make_result_room(self, incoming=0, *, reserve_slot=False):
        """Evict only closed compact results; never discard a live session."""
        while ((len(self.jobs) >= self.max_retained if reserve_slot else len(self.jobs) > self.max_retained)
               or self._retained_bytes() + incoming > self.max_result_bytes):
            removable = next((job_id for job_id, job in self.jobs.items()
                              if job.worker_done and not job.active), None)
            if removable is None:
                break
            del self.jobs[removable]

    def _prune(self):
        now = self.clock()
        for job_id, job in list(self.jobs.items()):
            if (job.active and not job.worker_done and not job.cancel.is_set()
                    and now - job.last_driven_at >= self.idle_seconds):
                # Abandoned mid-search. Stop it honestly and release its slot;
                # the retained result, if any, stays until the ordinary TTL.
                job.cancel.set()
                if self._update_job_data(
                        job, status='cancelled', can_continue=False,
                        message='This search stopped because nothing asked about it for a while. Start it again to continue.'):
                    pass
                else:
                    self._retention_limit_result(job)
                job.finished_at = now
                self._finalize(job)
                continue
            since = job.paused_at if job.paused_at is not None else job.finished_at
            if since is not None and now - since >= self.ttl:
                job.expired = True
                job.cancel.set()
                self._finalize(job)
                if job.worker_done and not job.active:
                    del self.jobs[job_id]

    def _lookup(self, job_id):
        self._prune()
        job = self.jobs.get(job_id)
        if job is None or job.expired:
            raise JobError('not_found', 'This search has expired or was not found. Start a new search.', 404)
        return job

    def start(self, source, target, filters):
        key = (source, target, json.dumps(filters.to_dict(), sort_keys=True,
                                           separators=(',', ':')))
        with self.lock:
            self._prune()
            if self.closed:
                raise JobError('resource_limit', 'The search service is stopping.', 503)
            reusable = next((job for job in reversed(self.jobs.values())
                             if job.key == key and not job.expired and job.data.get('status') != 'cancelled'
                             and (job.data.get('status') in {'searching', 'ok'}
                                  or job.data.get('can_continue') is True)), None)
            if reusable is not None:
                self.jobs.move_to_end(reusable.id)
                active = reusable.data.get('status') == 'searching'
                self.reuse_counters['reused_active' if active else 'reused_completed'] += 1
                job, reused = reusable, {'reused': True, 'reuse_state': 'active' if active else 'retained'}
            else:
                if self._active_count() >= self.max_active:
                    raise JobError('resource_limit', 'Two deep searches are already running. Stop one or retry shortly.', 503)
                if self._session_count() >= self.max_sessions:
                    victim = next((old for old in self.jobs.values()
                                   if not old.active and not old.worker_done
                                   and old.data.get('status') == 'ok'
                                   and old.data.get('can_continue') is True), None)
                    if victim is None:
                        raise JobError('resource_limit', 'The temporary search workspace is full of resumable searches. Continue, stop, or let one expire.', 503)
                    victim.retire.set()
                    if not self._update_job_data(
                            victim, can_continue=False, session_retired=True,
                            message='The verified result remains available; its older continuation state was released to admit a new search.'):
                        self._retention_limit_result(victim)
                    self.reuse_counters.setdefault('sessions_retired', 0)
                    self.reuse_counters['sessions_retired'] += 1
                    # A paused session has no driver, so its state is released
                    # here rather than by a worker that no longer exists.
                    if not self._finalize(victim):
                        raise JobError('resource_limit', 'An older verified search is still releasing its temporary state. Retry shortly.', 503)
                job = _Job(source, target, filters, self.coverage, self.clock())
                job.budget = self.standard_budget
                job.data['automatic_continuations'] = 0
                job.data['search_policy'] = {
                    'automatic_continuation': self.auto_continue,
                    'max_automatic_seconds': self.max_auto_seconds,
                    'storage': 'temporary_memory',
                    'driver': 'request',
                }
                incoming = self._job_bytes(job)
                self._make_result_room(incoming, reserve_slot=True)
                if (len(self.jobs) >= self.max_retained
                        or self._retained_bytes() + incoming > self.max_result_bytes):
                    raise JobError('resource_limit', 'The bounded result cache is full of searches that are still in use.', 503)
                self.jobs[job.id] = job
                self.reuse_counters['started'] += 1
                reused = {'reused': False}
        # The first slice runs inside the starting request, so a direct
        # connection is usually answered before the browser ever polls.
        self._advance(job, self.start_slice)
        with self.lock:
            return deepcopy(job.data) | reused

    def info(self):
        with self.lock:
            self._prune()
            return {
                'active': self._active_count(),
                'retained': len(self.jobs),
                'max_active': self.max_active,
                'max_retained': self.max_retained,
                'resumable_sessions': self._session_count(),
                'max_resumable_sessions': self.max_sessions,
                'result_bytes': self._retained_bytes(),
                'result_bytes_limit': self.max_result_bytes,
                'ttl_seconds': self.ttl,
                'directional_keys': True,
                'storage': 'memory',
                'persistent': False,
                'driver': 'request',
                'start_slice_seconds': self.start_slice,
                'poll_slice_seconds': self.poll_slice,
                'idle_seconds': self.idle_seconds,
                'counters': dict(self.reuse_counters),
            }

    def get(self, job_id):
        with self.lock:
            job = self._lookup(job_id)
        # A poll is the only moment this process is guaranteed to be running,
        # so it does a bounded slice of the search before it answers.
        self._advance(job, self.poll_slice)
        with self.lock:
            return deepcopy(job.data)

    def cancel(self, job_id):
        with self.lock:
            job = self._lookup(job_id)
            job.cancel.set()
            if not self._update_job_data(
                    job, status='cancelled', can_continue=False,
                    message='Search stopped. Any displayed route retains its supporting evidence.'):
                self._retention_limit_result(job)
            job.finished_at = self.clock()
            job.paused_at = None
            # If a slice is running right now it will notice the flag and
            # release the session itself when it returns.
            self._finalize(job)
            return deepcopy(job.data)

    def resume(self, job_id):
        with self.lock:
            job = self._lookup(job_id)
            if self.closed:
                raise JobError('resource_limit', 'The search service is stopping.', 503)
            if job.data['status'] == 'searching':
                return deepcopy(job.data)
            if job.cancel.is_set() or not job.data.get('can_continue') or job.worker_done:
                raise JobError('invalid_request', 'This search cannot continue. Start a new search instead.', 409)
            if self._active_count() >= self.max_active:
                raise JobError('resource_limit', 'Two deep searches are already running. Stop one or retry shortly.', 503)
            job.active = True
            job.paused_at = None
            job.finished_at = None
            job.generation += 1
            job.budget = self.extended_budget
            job.auto_started = self.clock()
            job.stalled_runs = 0
            job.next_attempt_at = 0.0
            if not self._update_job_data(
                    job, status='searching', can_continue=False,
                    message='Continuing from the records and search progress already retrieved.'):
                job.active = False
                self._retention_limit_result(job)
                raise JobError('resource_limit', 'The bounded result cache cannot retain this continued search.', 503)
        self._advance(job, self.poll_slice)
        with self.lock:
            return deepcopy(job.data)

    def _publish(self, job, update):
        with self.lock:
            if job.cancel.is_set() or job.data['status'] != 'searching':
                return
            candidate = deepcopy(job.data)
            progress = deepcopy(update)
            best = progress.pop('best_result', None)
            candidate['progress'] = progress
            if best and best.get('paths'):
                candidate['best_result'] = deepcopy(best)
                for key in ('paths', 'version', 'coverage', 'distance', 'exact_for_retrieved_graph', 'global_shortest_proven'):
                    if key in best:
                        candidate[key] = deepcopy(best[key])
            if not self._replace_job_data(job, candidate):
                self._retention_limit_result(job)
                job.retire.set()

    @staticmethod
    def _slice(budget, seconds):
        """The run allowance for one request: the job's budget, time-boxed."""
        return dataclasses.replace(budget, max_seconds=max(1.0, min(float(seconds), float(budget.max_seconds))))

    def _advance(self, job, seconds):
        """Run one bounded slice of a job inside the calling request, if it is due."""
        if seconds <= 0:
            return
        with self.lock:
            due = (job.active and not job.worker_done and not job.cancel.is_set()
                   and not job.retire.is_set() and self.clock() >= job.next_attempt_at)
        if not due or not job.drive.acquire(blocking=False):
            return
        try:
            self._run_slice(job, seconds)
        finally:
            with self.lock:
                job.last_driven_at = self.clock()
            job.drive.release()

    def _run_slice(self, job, seconds):
        """Caller holds ``job.drive``. One engine run, then the continuation decision."""
        try:
            if job.session is None:
                job.session = self.engine_factory().start(
                    job.source, job.target, job.filters, cancel=job.cancel,
                    progress=lambda update: self._publish(job, update))
            result = job.session.run(self._slice(job.budget, seconds))
        except Exception as exc:
            LOG.exception('Deep search failed')
            with self.lock:
                if not job.cancel.is_set():
                    code = getattr(exc, 'code', 'upstream_unavailable')
                    if code not in {'resource_limit', 'upstream_unavailable', 'invalid_request', 'not_found'}:
                        code = 'upstream_unavailable'
                    if not self._update_job_data(
                            job, status=code, can_continue=False,
                            message=getattr(exc, 'message', 'The live search could not finish. Please retry.')):
                        self._retention_limit_result(job)
            self._finalize(job, held=True)
            return
        if job.retire.is_set() or job.cancel.is_set():
            self._finalize(job, held=True)
            return
        progress = result.get('progress') or {}
        # Any upstream request is progress: a slice spent hydrating profiles
        # retrieves no new work and explores nobody new, yet it is not stuck.
        marker = (progress.get('works_retrieved'), progress.get('people_explored'), progress.get('requests'))
        job.stalled_runs = job.stalled_runs + 1 if marker == job.last_progress else 0
        job.last_progress = marker
        # A time/request checkpoint is resumable; a session-wide memory ceiling
        # cannot be fixed by immediately trying again.
        ceiling = ('ceiling' in result.get('message', '').lower()
                   and job.budget.max_works >= self.extended_budget.max_works
                   and job.budget.max_people >= self.extended_budget.max_people)
        automatic = (self.auto_continue and result.get('can_continue', False)
                     and result.get('status') != 'ok' and not ceiling
                     and self.clock() - job.auto_started < self.max_auto_seconds
                     and job.stalled_runs < self.max_stalled_runs)
        # A short slice routinely ends mid-validation, which the engine reports
        # as search_incomplete. That is a checkpoint, not an upstream failure,
        # and must not be backed off from: the only sign of a real failure is
        # a new entry in the coverage failure log during this slice.
        failures = (result.get('coverage') or {}).get('failures')
        failure_count = len(failures) if isinstance(failures, list) else job.failures_seen
        failed_upstream = failure_count > job.failures_seen
        job.failures_seen = failure_count
        with self.lock:
            candidate = deepcopy(job.data)
            candidate.update(deepcopy(result))
            candidate.update(job_id=job.id, mode='live', source=job.source,
                             target=job.target, filters=job.filters.to_dict())
            if automatic:
                transient = failed_upstream and result.get('status') in {'search_incomplete', 'upstream_unavailable'}
                candidate['automatic_continuations'] += 1
                candidate.update(status='searching', can_continue=False,
                                 message='Continuing automatically from the evidence already retrieved.')
                candidate['progress'] = {**progress, 'stage': 'retry_upstream' if transient else 'continue_search'}
            if not self._replace_job_data(job, candidate):
                self._retention_limit_result(job)
                job.retire.set()
                terminal = True
            else:
                terminal = not result.get('can_continue', False)
            if job.retire.is_set():
                pass
            elif automatic:
                job.finished_at = job.paused_at = None
                # Back off from a transient upstream failure without sleeping
                # inside somebody's request: the next poll simply waits its turn.
                delay = min(60, self.retry_delay * (2 ** min(job.stalled_runs, 4))) if transient else 0
                job.next_attempt_at = self.clock() + delay
                job.budget = self.extended_budget
                return
            else:
                job.active = False
                job.finished_at = self.clock()
                if not terminal:
                    job.paused_at = self.clock()
                    return
        self._finalize(job, held=True)

    def _finalize(self, job, *, held=False):
        """Release a job's engine session and mark it closed.

        Returns False when a slice is running on another request; that slice
        sees the cancel or retire flag when it returns and finalizes itself.
        """
        if job.worker_done:
            return True
        if not held and not job.drive.acquire(blocking=False):
            return False
        try:
            if job.session is not None:
                try:
                    job.session.close()
                except Exception:
                    LOG.exception('Could not release temporary search state')
                job.session = None
            with self.lock:
                job.active = False
                job.worker_done = True
                job.finished_at = job.finished_at or self.clock()
                if job.cancel.is_set():
                    if not self._update_job_data(job, status='cancelled', can_continue=False):
                        self._retention_limit_result(job)
                elif job.retire.is_set():
                    if not self._update_job_data(job, can_continue=False):
                        self._retention_limit_result(job)
                job.closed.set()
                # Every mutation above was admitted before assignment.  This
                # final pass only enforces the retained-count LRU bound.
                self._make_result_room()
            return True
        finally:
            if not held:
                job.drive.release()

    def shutdown(self):
        with self.lock:
            self.closed = True
            jobs = list(self.jobs.values())
            for job in jobs:
                job.cancel.set()
        deadline = time.monotonic() + 2
        for job in jobs:
            if job.drive.acquire(timeout=max(0.0, deadline - time.monotonic())):
                try:
                    self._finalize(job, held=True)
                finally:
                    job.drive.release()
