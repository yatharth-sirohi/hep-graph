"""Local graph HTTP service. Run: python -m hepgraph.server --port 8765."""
from __future__ import annotations

import argparse
from collections import Counter, OrderedDict, deque
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
import os
from pathlib import Path
import re
import threading
import time
import unicodedata
import urllib.parse
import uuid

from .graph import Filters, Graph, GraphError
from .prefetch import PreparationError, PreparationJobs
from .remote import RemoteClient, RemoteError
from .search_jobs import JobError, SearchJobs

ROOT = Path(__file__).resolve().parent.parent
# Optional and gitignored: the application starts and searches without it.
CORE_NODE_FILE = ROOT / "data" / "cache" / "core-nodes.json"
FILTER_KEYS = {'max_authors', 'min_authors', 'min_shared', 'year_start', 'year_end', 'genealogy'}
SERVICE_VERSION = 'general-search-v3'
LOG = logging.getLogger('hepgraph')
# Forensics for a serverless deployment: which build is answering, and whether
# consecutive requests of one search reached the same process. Vercel exposes
# the build's commit and region as environment variables; the instance id is
# minted once per process at import. Nothing here is secret.
PROCESS_INSTANCE = uuid.uuid4().hex
PROCESS_STARTED = datetime.now(timezone.utc).isoformat(timespec='seconds')


def _git_commit():
    for name in ('VERCEL_GIT_COMMIT_SHA', 'GIT_COMMIT', 'SOURCE_VERSION'):
        value = os.environ.get(name)
        if value:
            return value[:40]
    head = ROOT / '.git' / 'HEAD'
    try:
        ref = head.read_text().strip()
        if ref.startswith('ref: '):
            return (ROOT / '.git' / ref[5:]).read_text().strip()[:40]
        return ref[:40]
    except OSError:
        return None


def runtime_info():
    return {
        'git_commit': _git_commit(),
        'deployment': os.environ.get('VERCEL_DEPLOYMENT_ID'),
        'region': os.environ.get('VERCEL_REGION'),
        'environment': os.environ.get('VERCEL_ENV'),
        'instance': PROCESS_INSTANCE,
        'process_started': PROCESS_STARTED,
        'pid': os.getpid(),
    }
_SERVERLESS_STATE = None
_SERVERLESS_STATE_LOCK = threading.Lock()


def _state_for_handler(server):
    """Attach one shared state when the hosting runtime owns the HTTP server."""
    state = getattr(server, 'state', None)
    if state is not None:
        return state
    global _SERVERLESS_STATE
    with _SERVERLESS_STATE_LOCK:
        if _SERVERLESS_STATE is None:
            _SERVERLESS_STATE = State(ROOT / 'data' / 'current.json', default_mode='live')
        state = _SERVERLESS_STATE
    server.state = state
    return state


def folded(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', str(value)).casefold() if not unicodedata.combining(c))


def integer(value, default, low, high):
    if value is None:
        return default
    if not re.fullmatch(r'[0-9]{1,10}', str(value)) or not low <= int(value) <= high:
        raise ValueError(f'Expected an integer from {low} to {high}.')
    return int(value)


def person_id(value):
    if not re.fullmatch(r'[1-9][0-9]{0,11}', str(value or '')):
        raise ValueError('Choose an INSPIRE researcher identity with a numeric record ID.')
    return str(value)


class State:
    def __init__(self, snapshot_path, default_mode='snapshot'):
        if default_mode not in {'live', 'snapshot'}:
            raise ValueError('Choose live or snapshot mode.')
        self.default_mode = default_mode
        self._remote_client = None
        self._jobs = None
        self._preparations = None
        self._core_nodes = None
        self.live_queries = threading.BoundedSemaphore(2)
        self.path = Path(snapshot_path)
        self.lock = threading.RLock()
        self.graphs = OrderedDict()
        self.analytics = threading.BoundedSemaphore(1)
        self.workers = threading.BoundedSemaphore(8)
        self.rates = OrderedDict()
        self.stamp = None
        self.reload()

    def reload(self):
        with self.lock:
            stat = self.path.stat()
            stamp = (stat.st_mtime_ns, stat.st_size)
            if stamp == self.stamp:
                return
            data = json.loads(self.path.read_text())
            if not all(k in data for k in ('version', 'people', 'works', 'phd', 'coverage')):
                raise ValueError('Published snapshot has an invalid schema.')
            people = {str(p['id']): p for p in data['people']}
            counts, representative = Counter(), {}
            for work in data['works']:
                for pid in set(work['authors']):
                    counts[pid] += 1
                    if pid not in representative or (work.get('year') or 0) > (representative[pid].get('year') or 0):
                        representative[pid] = {k: work.get(k) for k in ('id', 'title', 'year', 'source_url')}
            self.snapshot, self.people = data, people
            self.counts, self.representative = counts, representative
            self.search_text = {pid: folded(' '.join([p['name'], *p.get('aliases', []), pid, p.get('orcid') or ''])) for pid, p in people.items()}
            self.graphs.clear()
            self.stamp = stamp
            LOG.info('Loaded snapshot %s: %d people, %d works', data['version'], len(people), len(data['works']))

    def rate_ok(self, ip):
        now = time.monotonic()
        with self.lock:
            q = self.rates.setdefault(ip, deque())
            while q and q[0] < now - 60:
                q.popleft()
            if len(q) >= 180:
                return False
            q.append(now)
            self.rates.move_to_end(ip)
            while len(self.rates) > 4096:
                self.rates.popitem(last=False)
            return True

    def graph(self, filters):
        with self.lock:
            key = (self.snapshot['version'], json.dumps(filters.to_dict(), sort_keys=True))
            if key not in self.graphs:
                self.graphs[key] = (Graph(self.snapshot, filters), threading.RLock())
            self.graphs.move_to_end(key)
            while len(self.graphs) > 4:
                self.graphs.popitem(last=False)
            return self.graphs[key]

    def remote_client(self):
        with self.lock:
            if self._remote_client is None:
                self._remote_client = RemoteClient()
            return self._remote_client

    def on_demand(self):
        from .ondemand import OnDemand
        return OnDemand(self.remote_client())

    def core_nodes(self):
        """Optional seed identities. Absent is normal and changes no result."""
        from .core_nodes import load
        if self._core_nodes is None:
            self._core_nodes = load(CORE_NODE_FILE)
        return self._core_nodes

    def search_jobs(self):
        from .deep_search import DeepSearch
        from .navigation_hints import HISTORICAL_NAVIGATION_PAIRS
        with self.lock:
            if self._jobs is None:
                self._jobs = SearchJobs(
                    lambda: DeepSearch(self.remote_client(), guide_snapshot=self.snapshot,
                                       suggestion_pairs=HISTORICAL_NAVIGATION_PAIRS,
                                       core_nodes=self.core_nodes()),
                    coverage=self.dataset('live')['coverage'], auto_continue=True)
            return self._jobs

    def preparation_jobs(self):
        with self.lock:
            if self._preparations is None:
                self._preparations = PreparationJobs(self.remote_client())
            return self._preparations

    def cache_info(self):
        result = self.remote_client().cache_info()
        result['preparations'] = (self._preparations.info() if self._preparations is not None else {
            'active': 0, 'pending': 0, 'retained': 0, 'max_active': 2,
            'max_pending': 8, 'max_retained': 32, 'ttl_seconds': 600.0,
            'storage': 'memory', 'persistent': False, 'counters': {},
        })
        result['search_jobs'] = (self._jobs.info() if self._jobs is not None else {
            'active': 0, 'retained': 0, 'max_active': 2, 'max_retained': 32,
            'resumable_sessions': 0, 'max_resumable_sessions': 4,
            'result_bytes': 0, 'result_bytes_limit': 8 * 1024 * 1024,
            'ttl_seconds': 1200.0, 'directional_keys': True,
            'storage': 'memory', 'persistent': False,
            'counters': {'started': 0, 'reused_active': 0, 'reused_completed': 0},
        })
        return result

    def shutdown(self):
        if self._jobs is not None:
            self._jobs.shutdown()
        if self._preparations is not None:
            self._preparations.shutdown()

    def dataset(self, mode='snapshot'):
        if mode == 'live':
            return {
                'version': 'live-inspire-v1', 'source_mode': 'live',
                'default_mode': self.default_mode, 'created_at': None,
                'counts': {'people': None, 'works': None, 'phd': None},
                'coverage': {
                    'label': 'Live INSPIRE — retrieved for your search',
                    'description': 'Names, papers, and doctoral records are requested when you search. The search continues automatically through time checkpoints, retaining its progress for up to two hours while you can stop it at any time. Memory limits and persistent source failures are reported explicitly. A found route is evidenced; an unfinished search cannot prove that no route exists or that a multi-hop route is globally shortest. Retrieved records and progress stay in temporary memory.',
                    'complete': False, 'mode': 'live', 'queries': [], 'failures': [],
                },
                'examples': self.snapshot.get('examples', []),
                'cache': self.cache_info(),
                'capabilities': {'live_graph': True, 'deep_search': True, 'global_centrality': False},
                'policy': {
                    'papers': 'Articles and individual conference papers, excluding standalone correction notices. The full author count controls eligibility.',
                    'identity': 'Stable INSPIRE author record IDs; names never establish an identity match.',
                    'genealogy': 'Explicit PhD adviser to student records, including a small separately sourced institutional historical supplement; source uncertainty is retained.',
                    'storage': 'Newly retrieved metadata stays in memory; no downloaded database, disk cache, or background harvest.',
                    'distance': 'One person-to-person tie is one hop. Multi-hop paths are shortest only in the retrieved graph.',
                },
            }
        s = self.snapshot
        return {k: s.get(k) for k in ('version', 'created_at', 'coverage', 'examples')} | {
            'source_mode': 'snapshot', 'default_mode': self.default_mode,
            'counts': {'people': len(s['people']), 'works': len(s['works']), 'phd': len(s['phd']),
                       'unresolved_occurrences': sum(w.get('unresolved_count', 0) for w in s['works'])},
            'policy': {'papers': 'Articles and individual conference papers; excludes theses, books, book chapters, proceedings volumes, and standalone correction notices.',
                       'dates': 'Earliest documented preprint/publication date. Unknown dates are included only for all-years queries.',
                       'genealogy': 'Only explicitly doctoral supervision. Paper filters affect coauthorship only.',
                       'distance': 'One eligible person-to-person connection is one hop. A path is shortest within this snapshot, with no claim of global shortestness.',
                       'identity': 'INSPIRE author record IDs; names are searchable labels, never identity keys.',
                       'affiliations': 'Profile affiliations where available; otherwise affiliations on indexed works, which may be historical.'}}

    def local_search(self, query):
        tokens = folded(query).split()
        matched = [pid for pid, text in self.search_text.items() if all(t in text for t in tokens)]
        matched.sort(key=lambda pid: (folded(self.people[pid]['name']) != folded(query), -self.counts[pid], self.people[pid]['name']))
        results = [self.people[pid] | {'indexed': True, 'indexed_publications': self.counts[pid], 'representative_work': self.representative.get(pid)} for pid in matched[:20]]
        return {'status': 'ambiguous' if len(matched) > 1 else ('ok' if matched else 'not_found'), 'results': results,
                'source': 'local', 'total': len(matched), 'version': self.snapshot['version'],
                'message': 'Select the intended researcher using identifiers and affiliations.' if len(matched) > 1 else ('No matching indexed researcher. Try live INSPIRE search.' if not matched else '')}

    def live_search(self, query):
        """Legacy saved-demo discovery uses the same bounded RAM transport."""
        result = self.on_demand().search(query)
        people = []
        for person in result.get('results', []):
            pid = person['id']
            saved = self.people.get(pid, person)
            people.append(saved | {'indexed': pid in self.people,
                'queryable': pid in self.people,
                'indexed_publications': self.counts[pid],
                'representative_work': self.representative.get(pid)})
        return result | {'results': people,
            'message': result.get('message') or 'Live discovery does not add a researcher to the saved demo.'}


class Handler(BaseHTTPRequestHandler):
    server_version = 'HEPGraph/0.1'
    sys_version = ''

    def setup(self):
        self.request.settimeout(15)
        super().setup()

    def log_message(self, fmt, *args):
        LOG.info('%s %s', self.address_string(), fmt % args)

    def respond(self, value, status=200, content_type='application/json; charset=utf-8'):
        body = json.dumps(value, ensure_ascii=False, allow_nan=False).encode() if content_type.startswith('application/json') else value
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store' if content_type.startswith('application/json') else 'no-cache')
        self.send_header('X-Content-Type-Options', 'nosniff')
        # Which process answered. Lets a client tell whether the polls of one
        # search all reached the same instance; carries nothing sensitive.
        self.send_header('X-HEP-Instance', PROCESS_INSTANCE)
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.send_header('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
        self.end_headers()
        if self.command != 'HEAD':
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass

    def live_result(self, result, filters=None, status=None):
        # Even a failed retrieval has an explicit source and policy version.
        # Successful operations supply their own content version and counts.
        result = {'mode': 'live', 'version': 'live-inspire-v1', 'exact': False,
                  'coverage': self.server.state.dataset('live')['coverage'], **result}
        if filters is not None:
            result.setdefault('filters', filters.to_dict())
        if status is None:
            status = {'resource_limit': 422, 'upstream_unavailable': 503,
                      'invalid_request': 400, 'invalid_input': 400}.get(result.get('status'), 200)
        return self.respond(result, status)

    def do_HEAD(self):
        if urllib.parse.urlsplit(self.path).path in {'/api/path', '/api/prepare'}:
            return self.respond({'status': 'invalid_request', 'message': 'This operation requires its documented request method.'}, 405)
        self.do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlsplit(self.path)
        if (parsed.path != '/api/prepare'
                and not re.fullmatch(r'/api/search-jobs/[0-9a-f]{32}/(?:continue|cancel)', parsed.path)):
            return self.send_error(501, "Unsupported method ('POST') for this route.")
        origin = self.headers.get('Origin')
        if origin:
            source = urllib.parse.urlsplit(origin)
            if source.scheme not in {'http', 'https'} or source.netloc != self.headers.get('Host') or source.path:
                return self.respond({'status': 'invalid_request', 'message': 'Search controls require the same origin.'}, 403)
        if self.headers.get('Transfer-Encoding') or self.headers.get('Content-Length', '0') != '0':
            return self.respond({'status': 'invalid_request', 'message': 'Search controls do not accept a request body.'}, 400)
        self.do_GET()

    def do_GET(self):
        state = _state_for_handler(self.server)
        if len(self.path) > 4096:
            return self.respond({'status': 'invalid_input', 'message': 'Request URL is too long.'}, 414)
        if not state.rate_ok(self.client_address[0]):
            return self.respond({'status': 'resource_limit', 'message': 'Request rate limit reached; retry after one minute.'}, 429)
        if not state.workers.acquire(blocking=False):
            return self.respond({'status': 'resource_limit', 'message': 'The query service is busy. Retry shortly.'}, 503)
        try:
            self.route(state)
        except JobError as exc:
            self.live_result({'status': exc.code, 'message': exc.message}, status=exc.http_status)
        except PreparationError as exc:
            self.live_result({'status': exc.code, 'message': exc.message}, status=exc.http_status)
        except RemoteError as exc:
            self.respond({'status': exc.code, 'message': exc.message, 'mode': 'live',
                          'coverage': state.dataset('live')['coverage'], 'exact': False},
                         422 if exc.code == 'resource_limit' else 503)
        except GraphError as exc:
            code = getattr(exc, 'code', 'resource_limit')
            status = 422 if code == 'resource_limit' else (404 if code == 'not_indexed' else 400)
            self.respond({'status': code, 'message': str(exc), 'version': state.snapshot['version'], 'coverage': state.snapshot['coverage']}, status)
        except (ValueError, TypeError) as exc:
            self.respond({'status': 'invalid_input', 'message': str(exc)}, 400)
        except Exception:
            LOG.exception('Unhandled request error')
            self.respond({'status': 'error', 'message': 'The request failed. Please retry or inspect the local service log.'}, 500)
        finally:
            state.workers.release()

    def route(self, state):
        parsed = urllib.parse.urlsplit(self.path)
        if parsed.scheme or parsed.netloc:
            raise ValueError('Absolute request URLs are not supported.')
        path = parsed.path
        if not path.startswith('/api/'):
            assets = {'/': ('index.html', 'text/html'), '/index.html': ('index.html', 'text/html'),
                      '/app.js': ('app.js', 'text/javascript'), '/styles.css': ('styles.css', 'text/css'), '/favicon.svg': ('favicon.svg', 'image/svg+xml')}
            if path not in assets:
                return self.respond({'status': 'not_found'}, 404)
            filename, mime = assets[path]
            return self.respond((ROOT / 'static' / filename).read_bytes(), content_type=mime + '; charset=utf-8')
        pairs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True, max_num_fields=20)
        if any(len(v) != 1 for v in pairs.values()):
            raise ValueError('Duplicate query parameters are not allowed.')
        args = {k: v[0] for k, v in pairs.items() if v[0] != ''}
        allowed = FILTER_KEYS | {'source', 'target', 'person', 'alternatives', 'q', 'live', 'limit', 'metric', 'direction', 'version', 'mode', 'summary', 'search'}
        if set(args) - allowed:
            raise ValueError('Unknown query parameter.')
        # Links from the saved-only release carry a snapshot version but no
        # source mode. Preserve their meaning after the default becomes live.
        mode = args.get('mode', 'snapshot' if args.get('version') else state.default_mode)
        if mode not in {'live', 'snapshot'}:
            raise ValueError('Choose live or snapshot mode.')
        if args.get('summary', '0') not in {'0', '1'}:
            raise ValueError('Profile summary must be 0 or 1.')
        if args.get('search', 'deep') not in {'deep', 'quick'}:
            raise ValueError('Choose deep or quick search.')
        state.reload()
        if path == '/api/health':
            return self.respond({'status': 'ok', 'version': state.snapshot['version'],
                                 'service_version': SERVICE_VERSION, 'runtime': runtime_info()})
        if path == '/api/dataset':
            return self.respond(state.dataset(mode))
        if path == '/api/cache':
            return self.respond(state.cache_info())
        if path.startswith('/api/preparations/'):
            match = re.fullmatch(r'/api/preparations/([0-9a-f]{32})', path)
            if not match or mode != 'live':
                return self.respond({'status': 'not_found', 'message': 'Preparation not found.'}, 404)
            return self.respond(state.preparation_jobs().get(match.group(1)))
        if path.startswith('/api/search-jobs/'):
            match = re.fullmatch(r'/api/search-jobs/([0-9a-f]{32})(?:/(continue|cancel))?', path)
            if not match or mode != 'live':
                return self.respond({'status': 'not_found', 'message': 'Search job not found.'}, 404)
            job_id, action = match.groups()
            if action:
                if self.command != 'POST':
                    return self.respond({'status': 'invalid_request', 'message': 'Use POST for search controls.'}, 405)
                result = state.search_jobs().resume(job_id) if action == 'continue' else state.search_jobs().cancel(job_id)
            else:
                result = state.search_jobs().get(job_id)
            return self.respond(result)
        if path == '/api/search':
            q = args.get('q', '').strip()
            if not 2 <= len(q) <= 120:
                raise ValueError('Search must contain 2–120 characters.')
            if args.get('live', '0') not in {'0', '1'}:
                raise ValueError('Live search must be 0 or 1.')
            if mode == 'live':
                return self.live_result(state.on_demand().search(q))
            return self.respond(state.live_search(q) if args.get('live') == '1' else state.local_search(q))
        filter_values = {k: v for k, v in args.items() if k in FILTER_KEYS}
        for key in ('max_authors', 'min_authors', 'min_shared', 'year_start', 'year_end'):
            if key in filter_values and not (key == 'max_authors' and filter_values[key] == 'all'):
                filter_values[key] = integer(filter_values[key], None, 1, 100000)
        filters = Filters.from_dict(filter_values)
        if path == '/api/prepare':
            if self.command != 'POST':
                return self.respond({'status': 'invalid_request', 'message': 'Use POST to prepare a selected author.'}, 405)
            if mode != 'live':
                return self.respond({'status': 'invalid_request', 'message': 'Preparation is available only in live mode.'}, 400)
            prepared = state.preparation_jobs().start(person_id(args.get('person')), filters)
            # The warm-up runs inside this request, so it has usually finished
            # by now; only a still-running one is "accepted".
            return self.respond(prepared, 202 if prepared.get('status') in {'queued', 'running'} else 200)
        if mode == 'live':
            if path == '/api/path' and args.get('search', 'deep') == 'deep':
                source, target = person_id(args.get('source')), person_id(args.get('target'))
                integer(args.get('alternatives'), 3, 1, 3)
                return self.respond(state.search_jobs().start(source, target, filters))
            if path == '/api/centrality':
                if args.get('metric', 'degree') not in {'degree', 'combined_degree', 'harmonic', 'betweenness', 'eccentricity'}:
                    raise ValueError('Unknown centrality measure.')
                return self.respond({'status': 'unavailable', 'mode': 'live', 'exact': False,
                    'message': 'Global centrality requires a graph index. Live searches retrieve only a small part of the network. Choose Saved demo to inspect its explicitly scoped metrics.',
                    'filters': filters.to_dict(), 'version': 'live-inspire-v1',
                    'coverage': state.dataset('live')['coverage']})
            if not state.live_queries.acquire(blocking=False):
                return self.live_result({'status': 'resource_limit',
                    'message': 'Two live connection queries are already running. Retry shortly.'}, filters, 503)
            try:
                engine = state.on_demand()
                if path == '/api/path':
                    result = engine.find_paths(person_id(args.get('source')), person_id(args.get('target')), filters,
                                               integer(args.get('alternatives'), 3, 1, 3))
                elif path.startswith('/api/person/'):
                    pid = person_id(path.removeprefix('/api/person/'))
                    if args.get('summary') == '1':
                        found = engine.search(pid)
                        if found.get('status') not in {'ok', 'ambiguous', 'not_found'}:
                            return self.live_result(found, filters)
                        person = next((p for p in found.get('results', []) if str(p.get('id')) == pid), None)
                        if person is None:
                            return self.live_result({'status': 'not_found',
                                'message': 'This INSPIRE author record was not found.'}, filters, 404)
                        result = {'status': 'ok', 'mode': 'live', 'person': person, 'queryable': True,
                                  'indexed_publications': None, 'eligible_publications': None,
                                  'coauthor_count': None, 'combined_degree': None,
                                  'filters': filters.to_dict(), 'version': 'live-inspire-v1',
                                  'coverage': state.dataset('live')['coverage']}
                    else:
                        result = engine.profile(pid, filters)
                elif path.startswith('/api/neighborhood/'):
                    result = engine.neighborhood(person_id(path.removeprefix('/api/neighborhood/')), filters,
                                                 integer(args.get('limit'), 40, 1, 80))
                elif path.startswith('/api/ancestry/'):
                    direction = args.get('direction', 'ancestors')
                    if direction not in {'ancestors', 'descendants'}:
                        raise ValueError('Direction must be ancestors or descendants.')
                    result = engine.ancestry(person_id(path.removeprefix('/api/ancestry/')), filters,
                                             direction, integer(args.get('limit'), 100, 1, 100))
                else:
                    return self.respond({'status': 'not_found'}, 404)
                return self.live_result(result, filters)
            finally:
                state.live_queries.release()
        graph, graph_lock = state.graph(filters)
        with graph_lock:
            if path == '/api/path':
                result = graph.find_paths(person_id(args.get('source')), person_id(args.get('target')), integer(args.get('alternatives'), 3, 1, 3))
            elif path.startswith('/api/person/'):
                result = graph.profile(person_id(path.removeprefix('/api/person/')))
            elif path.startswith('/api/neighborhood/'):
                result = graph.neighborhood(person_id(path.removeprefix('/api/neighborhood/')), integer(args.get('limit'), 40, 1, 80))
            elif path.startswith('/api/ancestry/'):
                direction = args.get('direction', 'ancestors')
                if direction not in {'ancestors', 'descendants'}:
                    raise ValueError('Direction must be ancestors or descendants.')
                result = graph.ancestry(person_id(path.removeprefix('/api/ancestry/')), direction, integer(args.get('limit'), 100, 1, 100))
            elif path == '/api/centrality':
                if not state.analytics.acquire(blocking=False):
                    return self.respond({'status': 'resource_limit', 'message': 'Another analysis is running. Retry shortly.'}, 503)
                try:
                    result = graph.centrality(args.get('metric', 'degree'), integer(args.get('limit'), 25, 1, 100))
                finally:
                    state.analytics.release()
            else:
                return self.respond({'status': 'not_found'}, 404)
        requested_version = args.get('version')
        if requested_version and requested_version != graph.version:
            result = result | {'version_mismatch': True, 'requested_version': requested_version,
                               'version_warning': 'The shared snapshot is not the current snapshot. This result was recalculated against the displayed current version.'}
        self.respond(result, 422 if result.get('status') == 'resource_limit' else 200)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--snapshot', default=str(ROOT / 'data' / 'current.json'))
    parser.add_argument('--default-mode', choices=('live', 'snapshot'), default='live',
                        help='live retrieves records on demand in memory; snapshot uses the saved demo')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.daemon_threads = True
    server.state = State(args.snapshot, default_mode=args.default_mode)
    LOG.info('HEP Graph running at http://%s:%s', args.host, args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.state.shutdown()
        server.server_close()


if __name__ == '__main__':
    main()
