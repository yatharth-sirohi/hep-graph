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

from .graph import Filters, GraphError
from .neon_graph_provider import GraphDatabaseError
from .identity_search import search as resolve_identity
from .remote import RemoteClient, RemoteError

ROOT = Path(__file__).resolve().parent.parent
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
            _SERVERLESS_STATE = State()
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
    def __init__(self):
        self.default_mode = 'database'
        self._remote_client = None
        self._graph_database = None
        self.lock = threading.RLock()
        self.workers = threading.BoundedSemaphore(8)
        self.rates = OrderedDict()

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

    def remote_client(self):
        with self.lock:
            if self._remote_client is None:
                self._remote_client = RemoteClient()
            return self._remote_client

    def graph_database(self):
        """The pinned-graph serving mode, or None when it is not configured.

        Built lazily so an unconfigured deployment never opens a connection,
        and cached per process like every other client here.
        """
        from .graph_database_mode import service_from_env
        with self.lock:
            if self._graph_database is None:
                self._graph_database = service_from_env(self.remote_client()) or False
            return self._graph_database or None

    def cache_info(self):
        result = self.remote_client().cache_info()
        database = self.graph_database()
        result['graph_database'] = ({'configured': True,
                                     'graph_snapshot': database.coverage().import_id}
                                    if database is not None else {'configured': False})
        return result

    def shutdown(self):
        return None

    def dataset(self, mode='database'):
        """Describe the pinned graph the routes will be traced through."""
        database = self.graph_database()
        if database is None:
            return {'version': None, 'source_mode': 'database', 'default_mode': self.default_mode,
                    'created_at': None, 'counts': {'people': None, 'works': None, 'phd': None},
                    'coverage': {'label': 'Research data unavailable',
                                 'description': 'This deployment has no published research data, so '
                                                'routes cannot be traced.',
                                 'complete': False, 'mode': 'database',
                                 'queries': [], 'failures': []},
                    'cache': self.cache_info(),
                    'capabilities': {'live_graph': False, 'deep_search': False,
                                     'global_centrality': False},
                    'policy': {}}
        return database.dataset() | {'default_mode': self.default_mode,
                                     'cache': self.cache_info()}


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

    def do_HEAD(self):
        if urllib.parse.urlsplit(self.path).path in {'/api/path', '/api/prepare'}:
            return self.respond({'status': 'invalid_request', 'message': 'This operation requires its documented request method.'}, 405)
        self.do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlsplit(self.path)
        if not re.fullmatch(r'/api/search-jobs/[0-9a-f]{32}/(?:continue|cancel)', parsed.path):
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
        except GraphDatabaseError as exc:
            # The store could not answer. That is an error, never an empty
            # neighborhood, which HLBES would read as proof of no connection.
            self.respond({'status': 'unavailable', 'mode': 'database', 'exact': False,
                          'message': 'The research data could not be reached.',
                          'reason': exc.reason}, 503)
        except RemoteError as exc:
            self.respond({'status': exc.code, 'message': exc.message, 'mode': 'database',
                          'exact': False}, 422 if exc.code == 'resource_limit' else 503)
        except GraphError as exc:
            code = getattr(exc, 'code', 'resource_limit')
            status = 422 if code == 'resource_limit' else (404 if code == 'not_indexed' else 400)
            self.respond({'status': code, 'message': str(exc)}, status)
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
                      '/app.js': ('app.js', 'text/javascript'), '/styles.css': ('styles.css', 'text/css'),
                      '/favicon.svg': ('favicon.svg', 'image/svg+xml')}
            if path not in assets:
                return self.respond({'status': 'not_found'}, 404)
            filename, mime = assets[path]
            return self.respond((ROOT / 'static' / filename).read_bytes(),
                                content_type=mime + '; charset=utf-8')
        pairs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True, max_num_fields=20)
        if any(len(v) != 1 for v in pairs.values()):
            raise ValueError('Duplicate query parameters are not allowed.')
        args = {k: v[0] for k, v in pairs.items() if v[0] != ''}
        allowed = FILTER_KEYS | {'source', 'target', 'person', 'alternatives', 'q', 'limit',
                                 'metric', 'direction', 'version', 'mode', 'summary'}
        if set(args) - allowed:
            raise ValueError('Unknown query parameter.')
        if args.get('mode', 'database') != 'database':
            raise ValueError('The requested search source is unavailable.')
        if args.get('summary', '0') not in {'0', '1'}:
            raise ValueError('Profile summary must be 0 or 1.')
        if path == '/api/health':
            return self.respond({'status': 'ok', 'service_version': SERVICE_VERSION,
                                 'runtime': runtime_info()})
        if path == '/api/dataset':
            return self.respond(state.dataset())
        if path == '/api/cache':
            return self.respond(state.cache_info())

        database = state.graph_database()
        if database is None:
            return self.respond({
                'status': 'unavailable', 'mode': 'database',
                'message': 'This deployment has no published research data available, so routes '
                           'cannot be traced.'}, 503)

        if path.startswith('/api/search-jobs/'):
            match = re.fullmatch(r'/api/search-jobs/([0-9a-f]{32})(?:/(continue|cancel))?', path)
            if not match:
                return self.respond({'status': 'not_found', 'message': 'Search job not found.'}, 404)
            job_id, action = match.groups()
            if action and self.command != 'POST':
                return self.respond({'status': 'invalid_request',
                                     'message': 'Use POST for search controls.'}, 405)
            if not database.owns_job(job_id):
                return self.respond({'status': 'not_found', 'message': 'Search job not found.'}, 404)
            return self.respond(database.resume(job_id) if action == 'continue' else
                                database.cancel(job_id) if action else database.job(job_id))
        if path == '/api/search':
            # Identity resolution is a name lookup, not traversal: the compact
            # graph stores no names, so this is the one pre-route INSPIRE call.
            return self.respond(resolve_identity(state.remote_client(), args.get('q', '').strip(),
                                                 provider=database.provider()))

        filter_values = {k: v for k, v in args.items() if k in FILTER_KEYS}
        for key in ('max_authors', 'min_authors', 'min_shared', 'year_start', 'year_end'):
            if key in filter_values and not (key == 'max_authors' and filter_values[key] == 'all'):
                filter_values[key] = integer(filter_values[key], None, 1, 100000)
        filters = Filters.from_dict(filter_values)

        if path == '/api/path':
            source, target = person_id(args.get('source')), person_id(args.get('target'))
            integer(args.get('alternatives'), 3, 1, 3)
            return self.respond(database.start_path(source, target, filters))
        if path.startswith('/api/person/'):
            return self.respond(database.person(person_id(path.removeprefix('/api/person/')), filters))
        if path.startswith('/api/neighborhood/'):
            return self.respond(database.neighborhood(
                person_id(path.removeprefix('/api/neighborhood/')), filters,
                limit=integer(args.get('limit'), 40, 1, 80)))
        if path.startswith('/api/ancestry/'):
            direction = args.get('direction', 'ancestors')
            if direction not in {'ancestors', 'descendants'}:
                raise ValueError('Direction must be ancestors or descendants.')
            return self.respond(database.ancestry(
                person_id(path.removeprefix('/api/ancestry/')), filters))
        if path == '/api/centrality':
            # A whole-graph metric needs the whole graph resident, which a
            # function instance must never hold for a corpus this size.
            return self.respond({
                'status': 'unavailable', 'mode': 'database', 'exact': False,
                'message': 'Global centrality is not available in this release.',
                'filters': filters.to_dict(),
                'version': f"graph-db:{database.coverage().import_id}"})
        return self.respond({'status': 'not_found'}, 404)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.daemon_threads = True
    server.state = State()
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
