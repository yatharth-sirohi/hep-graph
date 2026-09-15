"""The seed list is a routing convenience and must never become a graph fact."""
from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from hepgraph import core_nodes
from hepgraph.deep_search import DeepSearch
from hepgraph.graph import Filters
from test_deep_search import Client, budget, literature_query, page, paper, profiles


def query_for(name):
    return f'name:"{name}"'


def author(identifier, name):
    return {"id": str(identifier), "metadata": {"control_number": str(identifier),
                                                "name": {"value": name}}}


class Authors:
    def __init__(self, answers):
        self.answers, self.calls = answers, []

    def search(self, collection, query, *, size=5, page=1, **kwargs):
        self.calls.append(query)
        answer = self.answers.get(query, [])
        if isinstance(answer, Exception):
            raise answer
        return {"hits": {"total": len(answer), "hits": answer}}


def test_seed_list_is_deduplicated_and_bounded():
    assert len(core_nodes.SEEDS) == len(set(core_nodes.SEEDS))
    assert 400 <= len(core_nodes.SEEDS) <= core_nodes.MAX_SEEDS
    assert all(isinstance(name, str) and name.strip() for name in core_nodes.SEEDS)


def test_only_an_unambiguous_profile_is_resolved():
    client = Authors({
        query_for("Solo One"): [author(11, "One, Solo")],
        query_for("Two Ways"): [author(12, "Ways, Two"), author(13, "Ways, T.")],
        query_for("Nobody Home"): [],
        query_for("Broken Call"): RuntimeError("upstream down"),
    })
    outcome = core_nodes.resolve(client, ["Solo One", "Two Ways", "Nobody Home", "Broken Call"],
                                 query_for=query_for)
    assert outcome["resolved"] == {"Solo One": "11"}
    assert list(outcome["ambiguous"]) == ["Two Ways"]
    assert outcome["missing"] == ["Nobody Home"]
    assert "Broken Call" in outcome["failed"]


def test_a_record_that_does_not_answer_for_itself_is_not_resolved():
    """A hit whose control number disagrees with its ID is not an identity."""
    mismatched = {"id": "20", "metadata": {"control_number": "21", "name": {"value": "X"}}}
    client = Authors({query_for("Mismatch"): [mismatched]})
    assert core_nodes.resolve(client, ["Mismatch"], query_for=query_for)["resolved"] == {}


def test_loading_seeds_never_fails_the_application(tmp_path):
    assert core_nodes.load(tmp_path / "absent.json") == frozenset()
    broken = tmp_path / "broken.json"
    broken.write_text("{not json")
    assert core_nodes.load(broken) == frozenset()
    wrong = tmp_path / "wrong.json"
    wrong.write_text(json.dumps({"resolved": ["not", "a", "mapping"]}))
    assert core_nodes.load(wrong) == frozenset()
    good = tmp_path / "good.json"
    good.write_text(json.dumps({"resolved": {"A": "11", "B": "12", "C": "not-an-id"}}))
    assert core_nodes.load(good) == frozenset({"11", "12"})


def _run(core):
    """Two routes of different lengths; the seed sits on the longer one."""
    responses = profiles(1, 2, 3, 4, 5)
    responses[("literature", literature_query(1), 1)] = page(paper(700, [1, 2]),
                                                             paper(701, [1, 3]), total=2)
    responses[("literature", literature_query(2), 1)] = page(paper(702, [2, 5]))
    responses[("literature", literature_query(3), 1)] = page(paper(703, [3, 4]))
    responses[("literature", literature_query(4), 1)] = page(paper(704, [4, 5]))
    session = DeepSearch(Client(responses), core_nodes=core).start(1, 5, Filters(genealogy=False))
    try:
        for _ in range(6):
            result = session.run(budget(max_requests=200))
            if not result["can_continue"]:
                break
        return result
    finally:
        session.close()


@pytest.mark.parametrize("core", [(), ("2",), ("3", "4"), ("1", "2", "3", "4", "5")])
def test_seeds_reorder_work_but_never_change_the_distance(core):
    result = _run(core)
    assert result["status"] == "ok"
    assert result["paths"][0]["hops"] == 2
    assert [person["id"] for person in result["paths"][0]["people"]] == ["1", "2", "5"]


def test_seeds_are_not_edges_and_are_not_reported_as_evidence():
    result = _run(("3", "4"))
    for edge in result["paths"][0]["edges"]:
        assert edge["types"] == ["coauthor"]
        assert edge["works"], "every displayed hop still needs real paper evidence"


def test_server_starts_without_a_seed_file(tmp_path, monkeypatch):
    """Portability: a clean clone has no cache directory at all."""
    from hepgraph import server

    monkeypatch.setattr(server, "CORE_NODE_FILE", tmp_path / "missing" / "core-nodes.json")
    state = server.State.__new__(server.State)
    state._core_nodes = None
    assert state.core_nodes() == frozenset()
