"""Local graph HTTP service. Run: python -m hepgraph.server --port 8765."""
from __future__ import annotations

import argparse
import hashlib
from collections import Counter, OrderedDict, deque
from datetime import datetime, timezone
import gzip
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
# HEP Atlas is served additively under /atlas from its own directory. Bound as a
# module constant so tests can point it at a temporary tree.
ATLAS_STATIC = ROOT / 'static' / 'atlas'
ATLAS_CONTENT_TYPES = {
    '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
    '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8',
    '.svg': 'image/svg+xml', '.png': 'image/png', '.webp': 'image/webp',
    '.woff2': 'font/woff2', '.glb': 'model/gltf-binary',
}
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

    def rate_ok(self, ip, limit=180, bucket='api'):
        """Per-address request budget for the last minute.

        The API budget protects the query service, whose requests reach INSPIRE
        and occupy a worker. Static files cost neither, and one HEP Atlas page
        legitimately fetches dozens of small bundles, so assets get their own
        larger budget in a separate bucket: browsing the atlas must never spend
        the allowance a search needs (see `do_GET`).
        """
        now = time.monotonic()
        with self.lock:
            q = self.rates.setdefault((ip, bucket), deque())
            while q and q[0] < now - 60:
                q.popleft()
            if len(q) >= limit:
                return False
            q.append(now)
            self.rates.move_to_end((ip, bucket))
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

    #: Compressing below this costs more than it saves.
    COMPRESS_MIN_BYTES = 1024

    def _compressible(self, content_type, body):
        """Whether to gzip this response for this client.

        The atlas ships large JSON bundles and a megabyte-and-a-half of vendored
        JavaScript; uncompressed they dominate its first load. Images and fonts
        are already compressed, so they are left alone.
        """
        if len(body) < self.COMPRESS_MIN_BYTES:
            return False
        if 'gzip' not in (self.headers.get('Accept-Encoding') or ''):
            return False
        return content_type.split(';')[0] in {
            'application/json', 'text/html', 'text/css', 'text/javascript',
            'image/svg+xml', 'model/gltf-binary',
        }

    def respond(self, value, status=200, content_type='application/json; charset=utf-8', *, cache_control=None, etag=None, raw=False):
        body = json.dumps(value, ensure_ascii=False, allow_nan=False).encode() if content_type.startswith('application/json') and not raw else value
        encoding = None

        if self.command != 'HEAD' and self._compressible(content_type, body):
            compressed = gzip.compress(body, 6)
            if len(compressed) < len(body):
                body, encoding = compressed, 'gzip'
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        if encoding:
            self.send_header('Content-Encoding', encoding)
            self.send_header('Vary', 'Accept-Encoding')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', cache_control or ('no-store' if content_type.startswith('application/json') else 'no-cache'))
        if etag:
            self.send_header('ETag', etag)
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
        # A static asset is a file read: it neither reaches INSPIRE nor needs a
        # worker. One HEP Atlas page pulls dozens of bundles, so serving them
        # under the query budget would throttle ordinary browsing.
        asset = not urllib.parse.urlsplit(self.path).path.startswith('/api/')
        if not state.rate_ok(self.client_address[0], 2000 if asset else 180,
                             'asset' if asset else 'api'):
            return self.respond({'status': 'resource_limit', 'message': 'Request rate limit reached; retry after one minute.'}, 429)
        if not asset and not state.workers.acquire(blocking=False):
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
            if not asset:
                state.workers.release()

    def respond_atlas(self, path):
        """Serve one file of the HEP Atlas tree; anything doubtful is not_found."""
        not_found = {'status': 'not_found'}
        root = ATLAS_STATIC.resolve()
        relative = 'index.html' if path in {'/atlas', '/atlas/'} else path[len('/atlas/'):]
        decoded = urllib.parse.unquote(relative)
        for candidate in (relative, decoded):
            if ('..' in candidate or '\\' in candidate or '\x00' in candidate
                    or '//' in candidate or candidate.startswith('/') or candidate.endswith('/')):
                return self.respond(not_found, 404)
        content_type = ATLAS_CONTENT_TYPES.get(Path(decoded).suffix.lower())
        if content_type is None:
            return self.respond(not_found, 404)
        target = (root / decoded).resolve()
        if not target.is_relative_to(root) or not target.is_file():
            return self.respond(not_found, 404)
        try:
            body = target.read_bytes()
        except OSError:
            return self.respond(not_found, 404)
        cache = 'public, max-age=300' if decoded.startswith('generated/') else 'no-cache'
        return self.respond(body, content_type=content_type, cache_control=cache, raw=True)

    def route(self, state):
        parsed = urllib.parse.urlsplit(self.path)
        if parsed.scheme or parsed.netloc:
            raise ValueError('Absolute request URLs are not supported.')
        path = parsed.path
        if not path.startswith('/api/'):
            if path == '/atlas' or path.startswith('/atlas/'):
                return self.respond_atlas(path)
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
                                 'metric', 'direction', 'depth', 'version', 'mode', 'summary',
                                 'a', 'b'}
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
            return self.respond(database.person(
                person_id(path.removeprefix('/api/person/')), filters,
                summary=args.get('summary') == '1'))
        if path.startswith('/api/neighborhood/'):
            return self.respond(database.neighborhood(
                person_id(path.removeprefix('/api/neighborhood/')), filters,
                limit=integer(args.get('limit'), 40, 1, 80)))
        if path == '/api/lineage-map':
            # 1.5 MB that changes only when the layout is rebuilt. A fixed
            # max-age would keep showing the old map after a rebuild, so the
            # browser revalidates every time and an unchanged map costs a 304.
            payload = database.lineage_map()
            # The platform caps a response at 4.5 MB. Compressed this map is
            # about 1.2 MB, but a client that cannot take gzip would be sent
            # the whole 5 MB and get an error instead of a map. Names are the
            # compressible bulk and the only part the map can draw without, so
            # they are what gives way - the map still renders, with ids.
            if 'gzip' not in (self.headers.get('Accept-Encoding') or ''):
                payload = payload | {'names': [], 'names_omitted': True}
            body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode()
            etag = 'W/"' + hashlib.sha256(body).hexdigest()[:32] + '"'
            if self.headers.get('If-None-Match') == etag:
                self.send_response(304)
                self.send_header('ETag', etag)
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                return None
            return self.respond(body, content_type='application/json; charset=utf-8',
                                cache_control='no-cache', etag=etag, raw=True)
        if path == '/api/relationship':
            # Both people are required and both are validated the same way, so
            # a malformed id is refused before any query runs.
            return self.respond(database.relationship(
                person_id(args.get('a', '')), person_id(args.get('b', '')), filters,
                depth=integer(args.get('depth'), 12, 1, 12)))
        if path.startswith('/api/ancestry/'):
            direction = args.get('direction', 'ancestors')
            if direction not in {'ancestors', 'descendants'}:
                raise ValueError('Direction must be ancestors or descendants.')
            return self.respond(database.ancestry(
                person_id(path.removeprefix('/api/ancestry/')), filters,
                direction=direction, depth=integer(args.get('depth'), 4, 1, 6)))
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
