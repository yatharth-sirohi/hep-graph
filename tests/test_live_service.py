"""Exercise the compatibility quick HTTP → transport → normalization boundary.

INSPIRE is replaced only at the transport boundary. No internet is required.
"""
from __future__ import annotations

import hashlib
import json
from urllib.parse import parse_qs, urlsplit

import pytest

from hepgraph.remote import RemoteClient, URLError
from test_acceptance_service import _LocalService, _snapshot


class Transport:
    def __init__(self):
        self.calls = []
        self.offline = False
        self.connected = True
        self.now = 0.0

    def clock(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds

    def __call__(self, url, timeout):
        parsed = urlsplit(url)
        args = parse_qs(parsed.query)
        query = args['q'][0]
        self.calls.append((parsed.path, query, timeout))
        if self.offline:
            raise URLError('fixture unavailable')
        hits = []
        if parsed.path.endswith('/authors'):
            recid = {'control_number:101': '101', 'control_number:102': '102',
                     '(name.value:"New" OR name.name_variants:"New" OR name.preferred_name:"New") AND (name.value:"Researcher" OR name.name_variants:"Researcher" OR name.preferred_name:"Researcher")': '101'}.get(query)
            if recid:
                hits = [{'id': recid, 'metadata': {
                    'control_number': int(recid), 'name': {'value': f'New Researcher {recid}'},
                    'positions': [{'institution': 'Public university', 'current': True}],
                    'emails': ['must-not-be-retained@example.invalid'], 'private_notes': 'discard'}}]
        elif self.connected and query.startswith('authors.record.$ref:'):
            hits = [{'id': '500', 'metadata': {'control_number': 500,
                'titles': [{'title': 'A documented collaboration'}], 'document_type': ['article'],
                'preprint_date': '2020-01-01', 'author_count': 2,
                'authors': [{'record': {'$ref': f'https://inspirehep.net/api/authors/{pid}'},
                             'full_name': f'New Researcher {pid}'} for pid in ('101', '102')],
                'dois': [{'value': '10.1234/test'}]}}]
        return json.dumps({'hits': {'total': len(hits), 'hits': hits}}).encode()


@pytest.fixture
def live_service(tmp_path):
    path = tmp_path / 'current.json'
    path.write_text(json.dumps(_snapshot()))
    service = _LocalService(path)
    service.state.default_mode = 'live'
    transport = Transport()
    service.state._remote_client = RemoteClient(transport=transport,
        clock=transport.clock, sleep=transport.sleep)
    return service, transport, tmp_path


def fetch(service, path):
    if path.startswith('/api/path?'):
        path += '&search=quick'
    status, headers, body = service.request(path)
    return status, headers, json.loads(body)


def fingerprint(directory):
    return {str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in directory.rglob('*') if path.is_file()}


def test_full_live_flow_uses_remote_people_and_writes_no_data(live_service):
    service, transport, directory = live_service
    before = fingerprint(directory)
    status, _, dataset = fetch(service, '/api/dataset')
    assert status == 200 and dataset['source_mode'] == 'live'
    assert dataset['counts'] == {'people': None, 'works': None, 'phd': None}
    assert transport.calls == []  # Loading the application is not a harvest.
    status, _, search = fetch(service, '/api/search?q=New%20Researcher')
    assert status == 200 and search['results'][0]['id'] == '101'
    assert search['results'][0]['queryable'] is True
    status, headers, route = fetch(service, '/api/path?source=101&target=102&genealogy=false')
    assert status == 200 and route['status'] == 'ok'
    assert route['mode'] == 'live' and route['exact'] is False
    assert route['exact_for_retrieved_graph'] is True
    assert route['global_shortest_proven'] is True
    assert route['paths'][0]['hops'] == 1
    assert [p['id'] for p in route['paths'][0]['people']] == ['101', '102']
    assert route['paths'][0]['edges'][0]['works'][0]['source_url'] == 'https://inspirehep.net/literature/500'
    assert headers['Cache-Control'] == 'no-store'
    calls = len(transport.calls)
    assert fetch(service, '/api/path?source=101&target=102&genealogy=false')[2]['status'] == 'ok'
    assert len(transport.calls) == calls
    assert fingerprint(directory) == before
    cache = fetch(service, '/api/cache')[2]
    assert cache['persistent'] is False and cache['storage'] == 'memory'
    assert 0 < cache['bytes'] <= cache['limit']
    assert 'must-not-be-retained' not in repr(service.state._remote_client._cache)


def test_snapshot_mode_still_calculates_locally_without_upstream(live_service):
    service, transport, _ = live_service
    status, _, result = fetch(service, '/api/path?mode=snapshot&source=1&target=3')
    assert status == 200 and result['paths'][0]['hops'] == 2
    assert result['version'] == 'acceptance-v1'
    assert transport.calls == []


def test_legacy_versioned_query_keeps_saved_scope_but_explicit_live_wins(live_service):
    service, transport, _ = live_service
    status, _, result = fetch(service, '/api/path?source=1&target=3&version=acceptance-v1')
    assert status == 200 and result['paths'][0]['hops'] == 2
    assert result['version'] == 'acceptance-v1' and transport.calls == []
    status, _, result = fetch(service, '/api/path?mode=live&source=101&target=102&version=acceptance-v1')
    assert status == 200 and result['mode'] == 'live'
    assert result['paths'][0]['hops'] == 1 and transport.calls


def test_summary_looks_up_only_one_identity_without_loading_its_papers(live_service):
    service, transport, _ = live_service
    status, _, result = fetch(service, '/api/person/101?summary=1')
    assert status == 200 and result['person']['id'] == '101'
    assert result['indexed_publications'] is None
    assert [call[:2] for call in transport.calls] == [('/api/authors', 'control_number:101')]


@pytest.mark.parametrize('path', ['/api/search?q=New%20Researcher', '/api/person/101?summary=1',
                                '/api/path?source=101&target=102'])
def test_upstream_failure_is_never_recast_as_a_missing_person_or_route(live_service, path):
    service, transport, _ = live_service
    transport.offline = True
    status, _, result = fetch(service, path)
    assert status == 503 and result['status'] == 'upstream_unavailable'
    assert result['mode'] == 'live'
    assert result['version'] == 'live-inspire-v1' and result['coverage']['complete'] is False
    assert result['exact'] is False
    if not path.startswith('/api/search'):
        assert result['filters']['max_authors'] == 10


def test_missing_live_route_is_incomplete_and_global_analytics_do_not_fetch(live_service):
    service, transport, _ = live_service
    transport.connected = False
    status, _, result = fetch(service, '/api/path?source=101&target=102&genealogy=false')
    assert status == 200 and result['status'] == 'search_incomplete'
    assert result['exact'] is False and result['filters']['genealogy'] is False
    count = len(transport.calls)
    status, _, result = fetch(service, '/api/centrality?metric=harmonic')
    assert status == 200 and result['status'] == 'unavailable'
    assert len(transport.calls) == count


@pytest.mark.parametrize('path', ['/api/path?mode=global&source=101&target=102',
    '/api/person/101?summary=2', '/api/path?source=0&target=102',
    '/api/path?source=101&target=102&max_authors=0'])
def test_bad_live_inputs_do_not_contact_inspire(live_service, path):
    service, transport, _ = live_service
    status, _, result = fetch(service, path)
    assert status == 400 and result['status'] in {'invalid_input', 'invalid_request'}
    assert transport.calls == []


def test_busy_live_service_returns_a_resource_state_and_releases_slots(live_service):
    service, transport, _ = live_service
    gate = service.state.live_queries
    assert gate.acquire(blocking=False) and gate.acquire(blocking=False)
    try:
        status, _, result = fetch(service, '/api/path?source=101&target=102')
        assert status == 503 and result['status'] == 'resource_limit'
        assert result['version'] == 'live-inspire-v1' and result['coverage']['complete'] is False
        assert result['filters']['genealogy'] is True
        assert transport.calls == []
    finally:
        gate.release()
        gate.release()
    assert fetch(service, '/api/person/101?summary=1')[0] == 200
    assert gate.acquire(blocking=False) and gate.acquire(blocking=False)
    gate.release()
    gate.release()
