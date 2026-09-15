"""Optional running-service checks and a modest measured HTTP workload.

Run from the source directory: python tests/http_acceptance.py [--live]
--live makes two public INSPIRE author searches through the local service.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import time
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8765')
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--output', default='docs/http-acceptance.json')
    args = parser.parse_args()

    def request(path):
        start = time.perf_counter()
        try:
            response = urlopen(args.url + path, timeout=30)
        except HTTPError as error:
            response = error
        with response:
            data = json.loads(response.read())
            row = {'path': path, 'http_status': response.status,
                   'status': data.get('status'), 'seconds': time.perf_counter() - start}
        return data, row

    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'base': args.url,
              'purpose': 'Local bounded-pilot acceptance, not a full-INSPIRE capacity estimate.'}
    dataset, _ = request('/api/dataset')
    report['snapshot_version'] = dataset['version']
    checks = []
    connected = '/api/path?source=1621061&target=1013775'
    data, row = request(connected)
    assert data['status'] == 'ok' and data['paths'][0]['hops'] == 5
    assert all(len(p['edges']) == p['hops'] for p in data['paths'])
    assert len({tuple(person['id'] for person in p['people']) for p in data['paths']}) == len(data['paths'])
    checks.append(row | {'assertion': 'Real five-hop route and distinct person alternatives', 'hops': 5,
                         'path_count': len(data['paths'])})

    for path, expected in [
        ('/api/path?source=1621061&target=983328', 'no_path'),
        ('/api/path?source=1621061&target=1621061', 'ok'),
        ('/api/path?source=2955074&target=1621061', 'not_indexed'),
        ('/api/search?q=Witten', 'ambiguous'),
        ('/api/search?q=Unlisted%20Example%20Researcher', 'not_found'),
        ('/api/path?source=1066085&target=1071895&max_authors=all', 'ok'),
        ('/api/path?source=1066085&target=1071895&max_authors=10', 'no_path'),
        ('/api/centrality?metric=degree&max_authors=all', 'resource_limit'),
    ]:
        data, row = request(path)
        assert data['status'] == expected, (path, data)
        if 'centrality' in path:
            assert row['http_status'] == 422 and data['exact'] is False
        if 'max_authors=all' in path and '/path' in path:
            assert data['paths'][0]['hops'] == 1
            assert data['paths'][0]['edges'][0]['works'][0]['author_count'] == 2932
        checks.append(row | {'expected': expected})

    data, row = request('/api/centrality?metric=harmonic')
    assert data['status'] == 'ok' and data['exact'] is True
    computed = datetime.fromisoformat(data['computed_at'].replace('Z', '+00:00'))
    assert abs((datetime.now(timezone.utc) - computed).total_seconds()) < 30
    checks.append(row | {'assertion': 'Actual centrality computation timestamp', 'computed_at': data['computed_at']})

    if args.live:
        live = []
        for name, expected in [('Unlisted Example Researcher', 'not_found'), ('Erin Visser', 'ok')]:
            data, row = request('/api/search?' + urlencode({'q': name, 'live': 1}))
            assert data['status'] == expected, (name, data)
            assert not any(p.get('indexed') for p in data['results'])
            live.append(row | {'query': name, 'expected_at_test_time': expected,
                               'results': [{'id': p['id'], 'name': p['name'], 'indexed': p['indexed']}
                                           for p in data['results']]})
            time.sleep(1.05)
        report['live_discovery'] = live
    else:
        report['live_discovery'] = {'status': 'skipped', 'reason': '--live was not supplied'}

    paths = [connected, '/api/path?source=1621061&target=1019647',
             '/api/path?source=1621061&target=983328',
             '/api/path?source=1066085&target=1071895&max_authors=all'] * 8
    begin = time.perf_counter()
    with ThreadPoolExecutor(max_workers=4) as pool:
        requests = [result[1] for result in pool.map(request, paths)]
    total = time.perf_counter() - begin
    assert all(r['http_status'] == 200 for r in requests)
    times = sorted(r['seconds'] for r in requests)
    report['http_workload'] = {'concurrency': 4, 'request_count': len(requests),
        'mix': 'Eight each: five-hop route, direct route, disconnected pair, 2932-author direct route.',
        'cache_state': 'Repeated filters and pairs; warm application caches, includes HTTP and JSON overhead.',
        'wall_seconds': total, 'mean_seconds': statistics.mean(times),
        'median_seconds': statistics.median(times), 'p95_seconds': times[round(.95 * (len(times)-1))],
        'max_seconds': max(times), 'statuses': dict(Counter(r['status'] for r in requests)),
        'requests': requests}
    report['checks'] = checks
    report['status'] = 'passed'
    Path(args.output).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('checks', 'http_workload')}, indent=2))
    print(json.dumps({k: v for k, v in report['http_workload'].items() if k != 'requests'}, indent=2))


if __name__ == '__main__':
    main()
