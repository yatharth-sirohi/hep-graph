"""Reading a layer's literature through one OR-union query changes cost only.

A work naming any union member is returned by the union, so exhausting the
union certifies every member at once.  What must not change is anything the
proof rests on: which records are evidence, which coauthors a person's own
query accounts for, and when a neighbourhood may be called COMPLETE.  These
tests drive the engine against a corpus that answers every query shape it
issues and compare union paging with individual paging record for record.
"""
from __future__ import annotations

import copy
from pathlib import Path
import random
import re
import sys
import time

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import hepgraph.deep_search as deep_search
from hepgraph.deep_search import BATCH_SIZE, DeepBudget, DeepSearch, DeepSession
from hepgraph.graph import Filters
from hepgraph.remote import OVERSIZE_MESSAGE, RemoteError
from test_deep_search import paper, person

REF = re.compile(r"authors\.record\.\$ref:([0-9]+)")
SMALL = Filters(genealogy=False)


def budget(**overrides):
    values = dict(max_seconds=30.0, max_requests=720, max_works=50_000, max_people=50_000,
                  page_size=1000, max_pages_per_person=100)
    values.update(overrides)
    return DeepBudget(**values)


class Corpus:
    """Serve a synthetic literature corpus for every query the engine issues.

    Single-author, endpoint-pair and OR-union literature queries are all
    answered from the same works, paged by (size, page) in most-recent order,
    with the 10,000-result window enforced as INSPIRE enforces it.  Profiles
    are served for exact IDs and OR batches of them.
    """

    def __init__(self, works, people, *, window=10_000, gte=False, short_unions=False,
                 cap_bytes=None, hidden=None):
        self.works = sorted(works, key=lambda work: -int(work["id"]))
        self.people = {str(item): person(item) for item in people}
        self.window, self.gte, self.short_unions, self.cap_bytes = window, gte, short_unions, cap_bytes
        # work id -> people whose own index term does not carry that work,
        # even though the record names them: INSPIRE is not always consistent.
        self.hidden = {str(key): {str(item) for item in value} for key, value in (hidden or {}).items()}
        self.calls: list[tuple[str, str, int, int]] = []

    # -- what was asked -------------------------------------------------
    def literature_calls(self):
        return [call for call in self.calls if call[0] == "literature"]

    def union_calls(self):
        return [call for call in self.literature_calls() if call[1].startswith("(")]

    def person_calls(self):
        return [call for call in self.literature_calls()
                if not call[1].startswith("(") and len(REF.findall(call[1])) == 1]

    # -- serving ---------------------------------------------------------
    def _indexed(self, work):
        named = {author["record"]["$ref"].rsplit("/", 1)[-1] for author in work["metadata"]["authors"]}
        return named - self.hidden.get(work["id"], set())

    def search(self, collection, query, *, size=25, page=1, sort=None, deadline=None):
        self.calls.append((collection, query, size, page))
        if page * size > self.window:
            raise RemoteError("resource_limit", f"page times size must not exceed the {self.window} result window")
        if collection == "authors":
            if query.startswith("advisors."):
                return {"hits": {"total": 0, "hits": []}}
            hits = [copy.deepcopy(self.people[item]) for item in re.findall(r"control_number:([0-9]+)", query)
                    if item in self.people]
            return {"hits": {"total": len(hits), "hits": hits}}
        if self.cap_bytes is not None and size > self.cap_bytes:
            raise RemoteError("resource_limit", OVERSIZE_MESSAGE)
        groups = re.findall(r"\(([^()]*)\)", query)
        terms = [set(REF.findall(group)) for group in groups] if groups else [{item} for item in REF.findall(query)]
        bounded = re.search(r"author_count:([0-9]+)->([0-9]+)", query)
        open_ended = re.search(r"author_count:([0-9]+)\+", query)
        low = int((bounded or open_ended).group(1))
        high = int(bounded.group(2)) if bounded else float("inf")
        selected = [work for work in self.works
                    if low <= work["metadata"]["author_count"] <= high
                    and all(self._indexed(work) & term for term in terms)]
        total = len(selected) + (1 if self.short_unions and groups else 0)
        if self.gte:
            total = {"value": total, "relation": "gte"}
        return {"hits": {"total": total, "hits": copy.deepcopy(selected[(page - 1) * size:page * size])}}


def truth(works):
    """Coauthor adjacency the corpus implies under the small-team filter."""
    adjacency: dict[str, set[str]] = {}
    for work in works:
        if not 1 <= work["metadata"]["author_count"] <= 10:
            continue
        named = [author["record"]["$ref"].rsplit("/", 1)[-1] for author in work["metadata"]["authors"]]
        for item in named:
            adjacency.setdefault(item, set()).update(other for other in named if other != item)
    return adjacency


def random_corpus(seed, *, people=30, works=200):
    """Six communities on a chain, so a route needs several closed layers.

    Every work draws one to six authors from one community, occasionally
    reaching into the next one, which is what makes the search read whole
    layers of several people rather than meet after one expansion each.
    """
    rng = random.Random(seed)
    ids = [str(1000 + index) for index in range(people)]
    communities = [ids[index::6] for index in range(6)]
    corpus = []
    for index in range(works):
        home = rng.randrange(6)
        pool = list(communities[home])
        if home < 5 and rng.random() < 0.25:
            pool.append(rng.choice(communities[home + 1]))
        authors = rng.sample(pool, min(len(pool), rng.randint(1, 6)))
        corpus.append(paper(5000 + index, authors))
    return corpus, ids, communities[0][0], communities[5][-1]


class Run:
    """Everything a finished search leaves behind that the tests compare."""

    def __init__(self, session, result, client):
        oracle = session._oracle
        self.result, self.client = result, client
        self.complete = set(oracle.complete) if oracle else set()
        self.reported = {key: set(value) for key, value in oracle.reported.items()} if oracle else {}
        self.cursors = dict(oracle.cursors) if oracle else {}


def search(client, source, target, *, filters=SMALL, batch_size=BATCH_SIZE, runs=1, **overrides):
    session = DeepSearch(client, batch_size=batch_size).start(source, target, filters)
    try:
        result = None
        for _ in range(runs):
            result = session.run(budget(**overrides))
            if not result["can_continue"]:
                break
        return Run(session, result, client)
    finally:
        session.close()


def seeded(client, left, right, *, batch_size=BATCH_SIZE, **overrides):
    """A session whose proof already has `left`/`right` as its pending layers."""
    session = DeepSearch(client, batch_size=batch_size).start(left[0], right[0], SMALL)
    session._run_requests = 0
    session._run_deadline = time.monotonic() + 30
    session._budget = budget(**overrides)
    session._begin_proof(session._budget)
    session._proof.left.complete.add(left[0])
    session._proof.right.complete.add(right[0])
    for person_id in left[1:]:
        session._proof.left.add(person_id, 1, left[0])
    for person_id in right[1:]:
        session._proof.right.add(person_id, 1, right[0])
    session._proof.left.radius = session._proof.right.radius = 1
    return session


def certify(session, person_id, limit=60):
    """Call the oracle until it certifies this person, or give up."""
    found = None
    for _ in range(limit):
        found = session._oracle.neighborhood(person_id)
        if found.status == "complete":
            break
    return found


def hops(run):
    paths = run.result.get("paths") or []
    return paths[0]["hops"] if paths else None


# ------------------------------------------------------------- differential
@pytest.mark.parametrize("seed", range(6))
def test_union_paging_changes_cost_and_nothing_else(seed):
    works, people, source, target = random_corpus(seed)
    page_size = (10, 25, 1000)[seed % 3]
    batched = search(Corpus(works, people), source, target, page_size=page_size, runs=50)
    single = search(Corpus(works, people), source, target, page_size=page_size, batch_size=1, runs=50)

    assert batched.result["status"] == single.result["status"]
    assert hops(batched) == hops(single)
    assert batched.result["global_shortest_proven"] == single.result["global_shortest_proven"]
    expected = truth(works)
    for run in (batched, single):
        for person_id in run.complete:
            assert run.reported[person_id] == expected.get(person_id, set()), person_id
    for person_id in batched.complete & single.complete:
        assert batched.reported[person_id] == single.reported[person_id]
    assert batched.client.union_calls(), "this corpus is built to make the search read whole layers"
    assert not single.client.union_calls()
    assert len(batched.client.literature_calls()) < len(single.client.literature_calls())


# ---------------------------------------------------------------- one union
def layer_corpus(members, per_member):
    """Each member has `per_member` works, each shared with a distinct partner."""
    works, partners, next_partner = [], {}, 100
    for member in members:
        partners[member] = set()
        for _ in range(per_member):
            partner = str(next_partner)
            next_partner += 1
            works.append(paper(5000 + len(works), [member, partner]))
            partners[member].add(partner)
    people = ["1", "2", *members, *(partner for group in partners.values() for partner in group)]
    return works, partners, people


MEMBERS = ("11", "12", "13")


def test_an_exhausted_union_certifies_every_member_without_another_request():
    works, partners, people = layer_corpus(MEMBERS, 4)
    client = Corpus(works, people)
    session = seeded(client, ["1", *MEMBERS], ["2"], page_size=5)
    try:
        found = certify(session, "11")
        assert found.status == "complete" and set(found.members) == partners["11"]
        union = session._oracle.cursors["11"].union
        assert union is not None and union.members == MEMBERS and union.literature_done
        # Twelve records at size five: three pages, each read exactly once.
        assert [call[3] for call in client.union_calls()] == [1, 2, 3]
        assert {call[1] for call in client.union_calls()} == {DeepSession.batch_query(MEMBERS, SMALL)}
        requests = len(client.calls)
        for member in ("12", "13"):
            found = session._oracle.neighborhood(member)
            assert found.status == "complete" and set(found.members) == partners[member]
            assert session._oracle._accounted(member)
        assert len(client.calls) == requests, "the union already read them"
        assert not client.person_calls()
        for member in MEMBERS:
            cursor = session._oracle.cursors[member]
            assert cursor.literature_done and not cursor.incomplete
            assert cursor.literature_total == 4 and len(cursor.literature_seen) == 4
            assert cursor.pages == 3, "every union page is progress for every member"
            # A member owns the records that name them and nothing else.
            assert session._oracle.attested[member] == partners[member] | {member}
    finally:
        session.close()


def test_a_union_the_window_cannot_hold_certifies_nobody_and_members_page_alone(monkeypatch):
    monkeypatch.setattr(deep_search, "MAX_RESULT_WINDOW", 30)
    works, partners, people = layer_corpus(MEMBERS, 12)  # union total 36 > 30
    client = Corpus(works, people, window=30)
    session = seeded(client, ["1", *MEMBERS], ["2"], page_size=10)
    try:
        session._oracle.neighborhood("11")  # profiles
        found = session._oracle.neighborhood("11")  # union page one, then detach
        assert found.status == "partial"
        assert client.union_calls() == [("literature", DeepSession.batch_query(MEMBERS, SMALL), 10, 1)]
        for member in MEMBERS:
            cursor = session._oracle.cursors[member]
            assert cursor.union is None and cursor.solo
            assert cursor.literature_page == 1 and not cursor.literature_done and cursor.pages == 1
        assert session.works == 10, "the page already read stays as evidence"
        for member in MEMBERS:
            found = certify(session, member)
            assert found.status == "complete" and set(found.members) == partners[member]
        assert len(client.union_calls()) == 1, "an unreadable union must not form again"
        for member in MEMBERS:
            pages = [call[3] for call in client.person_calls() if REF.findall(call[1]) == [member]]
            assert pages == [1, 2]
    finally:
        session.close()


def test_a_floor_count_union_certifies_nobody_and_members_page_alone():
    works, partners, people = layer_corpus(MEMBERS, 12)
    client = Corpus(works, people, gte=True)
    session = seeded(client, ["1", *MEMBERS], ["2"], page_size=10)
    try:
        session._oracle.neighborhood("11")
        found = session._oracle.neighborhood("11")
        assert found.status == "partial"
        assert all(session._oracle.cursors[member].union is None for member in MEMBERS)
        for member in MEMBERS:
            found = certify(session, member)
            assert found.status == "complete" and set(found.members) == partners[member]
        assert len(client.union_calls()) == 1
        for member in MEMBERS:
            # A floor count is read to its empty page, one person at a time.
            pages = [call[3] for call in client.person_calls() if REF.findall(call[1]) == [member]]
            assert pages == [1, 2, 3]
    finally:
        session.close()


def test_a_short_union_marks_every_member_incomplete_and_certifies_none():
    works, partners, people = layer_corpus(MEMBERS, 4)
    client = Corpus(works, people, short_unions=True)  # promises 13, serves 12
    session = seeded(client, ["1", *MEMBERS], ["2"])
    try:
        for member in MEMBERS:
            found = certify(session, member, limit=6)
            assert found.status == "partial" and set(found.members) == partners[member]
            cursor = session._oracle.cursors[member]
            assert cursor.literature_done and "literature_short" in cursor.incomplete
        assert len(client.union_calls()) == 1 and not client.person_calls()
        assert not session._oracle.complete
    finally:
        session.close()


def test_an_oversized_union_page_shrinks_restarts_and_still_certifies_everyone():
    works, partners, people = layer_corpus(MEMBERS, 4)
    client = Corpus(works, people, cap_bytes=10)
    session = seeded(client, ["1", *MEMBERS], ["2"])
    try:
        for member in MEMBERS:
            found = certify(session, member)
            assert found.status == "complete" and set(found.members) == partners[member]
        sizes = [call[2] for call in client.union_calls()]
        assert sizes[0] > 10 and sizes[-1] <= 10, "it tried big, then shrank"
        final = [call[3] for call in client.union_calls() if call[2] == sizes[-1]]
        assert final == [1, 2, 3], "a new size restarts at page one and reads each page once"
        assert all(session._oracle.cursors[member].shrinks == len(set(sizes)) - 1 for member in MEMBERS)
    finally:
        session.close()


def test_a_member_the_guard_retired_does_not_stall_the_union():
    works, partners, people = layer_corpus(MEMBERS, 4)
    client = Corpus(works, people)
    session = seeded(client, ["1", *MEMBERS], ["2"], page_size=5)
    try:
        session._oracle.neighborhood("11")
        session._oracle.neighborhood("11")  # union page one
        session._oracle.cursors.pop("12")  # what _retire_proof does
        session._oracle.attested.pop("12", None)
        for member in ("11", "13"):
            found = certify(session, member)
            assert found.status == "complete" and set(found.members) == partners[member]
    finally:
        session.close()


def test_a_members_cost_is_their_share_of_the_unions_remaining_pages():
    works, partners, people = layer_corpus(MEMBERS, 4)
    client = Corpus(works, people)
    session = seeded(client, ["1", *MEMBERS], ["2"], page_size=5)
    try:
        session._oracle.neighborhood("11")
        session._oracle.neighborhood("11")  # 5 of 12 read: two pages remain
        costs = [session._retrieval_cost(member) for member in MEMBERS]
        assert costs == pytest.approx([2 / 3] * 3)
        assert sum(costs) == pytest.approx(2.0), "the layer costs what the union costs"
    finally:
        session.close()


def test_an_audit_contradiction_withdraws_a_member_the_union_certified():
    """A neighbour that only ever appears on somebody else's page is a
    contradiction, whichever query certified the person."""
    works = [paper(5001, ["11", "101"]), paper(5002, ["12", "102"]), paper(5003, ["11", "13"])]
    # 5003 names 11 but 11's own index term (hence any union containing 11)
    # does not carry it; 13's does.
    client = Corpus(works, ["1", "2", "11", "12", "13", "101", "102"], hidden={5003: ["11"]})
    session = seeded(client, ["1", "11", "12"], ["2", "13"])
    try:
        found = certify(session, "11")
        assert found.status == "complete" and set(found.members) == {"101"}
        assert client.union_calls() and "11" in session._oracle.complete
        with pytest.raises(deep_search._EvidenceWithdrawn):
            for _ in range(3):
                session._oracle.neighborhood("13")  # its page names 11
        assert "11" not in session._oracle.complete and "11" in session._oracle.contradicted
        assert "13" not in session._oracle.attested["11"], "someone else's page never attests for a member"
    finally:
        session.close()


# ------------------------------------------------------------ whole searches
def test_a_union_resumes_across_slice_boundaries():
    works, people, source, target = random_corpus(3)
    sliced = search(Corpus(works, people), source, target, page_size=5, max_requests=1, runs=600)
    whole = search(Corpus(works, people), source, target, page_size=5, runs=50)
    assert not sliced.result["can_continue"] and not whole.result["can_continue"]
    assert hops(sliced) == hops(whole) and sliced.result["global_shortest_proven"]
    by_query: dict[str, list[int]] = {}
    for call in sliced.client.union_calls():
        by_query.setdefault(call[1], []).append(call[3])
    assert by_query and any(len(pages) > 1 for pages in by_query.values()), "unions spanned slices"
    for pages in by_query.values():
        assert pages == list(range(1, len(pages) + 1)), "resume exactly where it left off"
    assert len(sliced.client.calls) == len(whole.client.calls)


def test_large_team_mode_never_forms_a_union():
    works, people, source, target = random_corpus(1)
    broad = Filters(max_authors=None, min_authors=1, genealogy=False)
    run = search(Corpus(works, people), source, target, filters=broad, runs=50)
    assert run.result["status"] == "ok" and not run.client.union_calls()
    medium = Filters(max_authors=100, genealogy=False)
    run = search(Corpus(works, people), source, target, filters=medium, runs=50)
    assert run.client.union_calls(), "a 100-author page still holds over a hundred records"


def test_union_pages_are_counted_as_requests_and_literature_pages():
    works, people, source, target = random_corpus(2)
    run = search(Corpus(works, people), source, target, page_size=10, runs=50)
    progress = run.result["progress"]
    assert run.client.union_calls()
    assert progress["requests"] == len(run.client.calls)
    assert progress["literature_pages"] == len(run.client.person_calls()) + len(run.client.union_calls())


def test_endpoints_alone_in_their_layer_still_read_their_own_warm_query():
    """The prefetch warms the per-person page-one key; a union must not miss it."""
    works, people, source, target = random_corpus(0)
    run = search(Corpus(works, people), source, target, runs=50)
    warm = min(DeepBudget.standard().page_size, DeepSession.page_ceiling_for(SMALL))
    for endpoint in (source, target):
        assert ("literature", DeepSession.literature_query(endpoint, SMALL), warm, 1) in run.client.calls
        assert not any(endpoint in REF.findall(call[1]) for call in run.client.union_calls())


def test_batch_query_is_sorted_for_a_stable_cache_key():
    assert DeepSession.batch_query(["7", "12", "3"], SMALL) == DeepSession.batch_query(["3", "7", "12"], SMALL)
    assert DeepSession.batch_query(["7", "3"], SMALL) == \
        "(authors.record.$ref:3 OR authors.record.$ref:7) AND author_count:1->10"
    assert BATCH_SIZE == 8
