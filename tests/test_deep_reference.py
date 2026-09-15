"""Independent remote-search reachability checks against a NetworkX oracle.

The oracle constructs eligible person edges directly from primitive fixtures;
it does not use production normalization, Graph, or the search frontiers.
"""
from collections import Counter
from copy import deepcopy
from itertools import combinations
import random
import re

import networkx as nx
import pytest

from hepgraph.deep_search import DeepBudget, DeepSearch
from hepgraph.graph import Filters


class RemoteFixture:
    def __init__(self, people, works, phd):
        self.works = works
        self.people = {str(pid): {'id': str(pid), 'metadata': {
            'control_number': pid, 'name': {'value': f'Researcher {pid}'},
            'advisors': [{'record': {'$ref': f'https://inspirehep.net/api/authors/{adviser}'},
                          'degree_type': 'phd', 'curated_relation': True}
                         for adviser, student in phd if student == pid]}} for pid in people}
        self.calls = 0

    def search(self, collection, query, *, size, page, **kwargs):
        self.calls += 1
        if collection == 'authors':
            if query.startswith('control_number:'):
                requested = set(re.findall(r'control_number:([0-9]+)', query))
                selected = [item for pid, item in self.people.items() if pid in requested]
            else:
                focus = query.split(':')[1]
                selected = [item for item in self.people.values() if any(
                    a['record']['$ref'].endswith('/' + focus) for a in item['metadata']['advisors'])]
        else:
            groups = re.findall(r'\(([^()]*)\)', query)
            if groups:
                required_groups = [set(re.findall(r'authors.record.\$ref:([0-9]+)', group)) for group in groups]
            else:
                required_groups = [{pid} for pid in re.findall(r'authors.record.\$ref:([0-9]+)', query)]
            cap = re.search(r'author_count:1->([0-9]+)', query)
            selected = [work for work in self.works if all(
                group & {author['record']['$ref'].rsplit('/', 1)[-1] for author in work['metadata']['authors']}
                for group in required_groups)
                and (cap is None or work['metadata']['author_count'] <= int(cap[1]))]
        return {'hits': {'total': len(selected), 'hits': deepcopy(selected[(page-1)*size:page*size])}}


@pytest.mark.parametrize('seed', range(24))
def test_remote_reachability_and_every_returned_hop_match_independent_oracle(seed):
    rng = random.Random(seed)
    people = list(range(700001, 700017))
    min_shared = 1 + seed % 3
    cap = (2, 5, 10)[seed % 3]
    year_start = 2010 if seed % 4 else None
    genealogy = bool(seed % 2)
    works, counts = [], Counter()
    for index in range(44):
        authors = rng.sample(people, rng.randrange(2, 5))
        year = rng.choice([None, 2005, 2015, 2022])
        kind = rng.choice(['article', 'article', 'conference paper', 'book', 'thesis'])
        editor = authors[-1] if index % 11 == 0 else None
        total = len(authors) + (20 if index % 9 == 0 else 0)
        record = {'id': str(900000 + index), 'metadata': {'control_number': 900000 + index,
            'titles': [{'title': f'Independent fixture {index}'}], 'document_type': [kind],
            'author_count': total, 'authors': [{'record': {'$ref': f'https://inspirehep.net/api/authors/{pid}'},
                'full_name': f'Researcher {pid}', 'inspire_roles': ['editor' if pid == editor else 'author']}
                for pid in authors]}}
        if year:
            record['metadata']['preprint_date'] = f'{year}-01-01'
        works.append(record)
        if kind in {'article', 'conference paper'} and total <= cap and (year_start is None or year is not None and year >= year_start):
            for pair in combinations(sorted(str(pid) for pid in authors if pid != editor), 2):
                counts[pair] += 1
    phd = [tuple(rng.sample(people, 2)) for _ in range(6)]
    expected = nx.Graph()
    expected.add_nodes_from(map(str, people))
    expected.add_edges_from(pair for pair, count in counts.items() if count >= min_shared)
    if genealogy:
        expected.add_edges_from((str(a), str(s)) for a, s in phd)
    client = RemoteFixture(people, works, phd)
    source, target = map(str, (people[0], people[-1]))
    session = DeepSearch(client).start(source, target, Filters(max_authors=cap, min_shared=min_shared,
                                                               year_start=year_start, genealogy=genealogy))
    try:
        result = session.run(DeepBudget(30, 720, 1000, 1000, page_size=2, max_pages_per_person=2))
    finally:
        session.close()
    assert bool(result['paths']) == nx.has_path(expected, source, target), (seed, result)
    assert result['status'] in {'ok', 'search_incomplete'}, (seed, result)
    for route in result['paths']:
        ids = [person['id'] for person in route['people']]
        assert len(ids) == len(set(ids))
        assert ids[0] == source and ids[-1] == target
        for left, right in zip(ids, ids[1:]):
            assert expected.has_edge(left, right), (seed, left, right)
        assert route['hops'] >= nx.shortest_path_length(expected, source, target)


@pytest.mark.parametrize('cap,expected_hops', [(10, 64), (None, 1)])
def test_long_remote_chain_and_large_collaboration_shortcut_follow_the_selected_scope(cap, expected_hops):
    people = list(range(810001, 810066))
    works = []
    for index, pair in enumerate(zip(people, people[1:])):
        works.append({'id': str(910000 + index), 'metadata': {
            'control_number': 910000 + index,
            'titles': [{'title': f'Long-route edge {index}'}],
            'document_type': ['article'], 'author_count': 2,
            'preprint_date': '1980-01-01',
            'authors': [{'record': {'$ref': f'https://inspirehep.net/api/authors/{pid}'},
                         'full_name': f'Researcher {pid}'} for pid in pair]}})
    # A real full-author-count ceiling must survive even when most authors
    # lack resolved profile IDs. A tempting direct shortcut is out of cap 10.
    works.append({'id': '920000', 'metadata': {'control_number': 920000,
        'titles': [{'title': 'Large collaboration shortcut'}], 'document_type': ['article'],
        'author_count': 1000, 'preprint_date': '2025-01-01',
        'authors': [{'record': {'$ref': f'https://inspirehep.net/api/authors/{pid}'},
                     'full_name': f'Researcher {pid}'} for pid in (people[0], people[-1])]}})
    client = RemoteFixture(people, works, [])
    session = DeepSearch(client).start(people[0], people[-1], Filters(max_authors=cap, genealogy=False))
    try:
        result = session.run(DeepBudget(30, 720, 1000, 1000, page_size=2, max_pages_per_person=2))
    finally:
        session.close()
    assert result['status'] == 'ok'
    assert result['paths'][0]['hops'] == expected_hops
    assert all(person['profile_status'] == 'profile' for person in result['paths'][0]['people'])
    assert result['global_shortest_proven'] is (expected_hops == 1)
    if cap == 10:
        assert [person['id'] for person in result['paths'][0]['people']] == list(map(str, people))
