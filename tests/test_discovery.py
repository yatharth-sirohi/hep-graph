"""Independent graph checks for compact, explicitly unverified navigation."""
from collections import deque
import random

import networkx as nx
import pytest

from hepgraph.discovery import Navigator


def test_arbitrary_endpoints_can_join_through_an_existing_backbone():
    base = {'10': ['11'], '11': ['10', '12'], '12': ['11']}
    nav = Navigator('101', '202', base_neighbors=lambda p: base.get(p, []))
    assert nav.next_person() == '101'
    nav.accept('101', [{'id': '10', 'count': 1}])
    assert nav.next_person() == '202'
    nav.accept('202', [{'id': '12', 'count': 1}], truncated=True)
    assert nav.route() == ['101', '10', '11', '12', '202']
    assert nav.coverage()['complete'] is False
    assert nav.coverage()['truncated_profiles'] == 1


def test_pending_cursor_survives_an_upstream_failure():
    nav = Navigator('1', '9')
    assert nav.next_person() == '1'
    assert nav.next_person() == '1'
    with pytest.raises(ValueError):
        nav.accept('9', [])
    nav.accept('1', [])
    assert nav.next_person() == '9'


def test_rejected_edge_exposes_another_route_and_profile_rejection_removes_it():
    nav = Navigator('1', '9')
    for a, b in [('1', '2'), ('2', '9'), ('1', '3'), ('3', '4'), ('4', '9')]:
        nav.add_link(a, b)
    assert nav.route() == ['1', '2', '9']
    nav.reject_edge('2', '9')
    assert nav.route() == ['1', '3', '4', '9']
    nav.reject_person('4')
    assert nav.route() is None


def test_fanout_cannot_starve_the_other_search_side():
    nav = Navigator('1', '900')
    visited = []
    for _ in range(10):
        person = nav.next_person()
        visited.append(person)
        if person == '1':
            nav.accept(person, [{'id': str(n), 'count': 1} for n in range(2, 102)])
        else:
            nav.accept(person, [{'id': str(int(person) + 1), 'count': 1}])
    assert visited[:2] == ['1', '900']
    assert any(int(person) < 900 for person in visited[2:])


def test_large_paper_hints_remain_compact_and_bounded():
    nav = Navigator('1', '999', max_nodes=50, max_links=30)
    person = nav.next_person()
    nav.accept(person, [{'id': str(n), 'count': 1} for n in range(2, 102)], truncated=True)
    assert nav.links <= 30 and len(nav.adjacency) <= 50
    assert len(nav.known) <= 50 and nav.capped
    assert nav.coverage()['complete'] is False


@pytest.mark.parametrize('seed', range(16))
def test_navigation_distances_match_independent_networkx(seed):
    graph = nx.gnp_random_graph(80, .06, seed=seed)
    nav = Navigator('0', '79')
    for a, b in graph.edges:
        nav.add_link(str(a), str(b))
    route = nav.route()
    if nx.has_path(graph, 0, 79):
        assert len(route) - 1 == nx.shortest_path_length(graph, 0, 79)
        assert all(graph.has_edge(int(a), int(b)) for a, b in zip(route, route[1:]))
    else:
        assert route is None
