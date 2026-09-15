"""Regressions for defects an independent adversarial review confirmed.

Each of these was a runnable exploit before it was a test. They cover the ways
an unhelpful upstream can make the search certify something it has not seen:
a page that goes missing, a page that repeats, a count that moves, a byline
that belongs to somebody else, an erratum that displaces the paper it corrects,
and a record that cannot be read at all.

The corpus and harness below are the reviewer's, vendored so the evidence
outlives the scratchpad it was written in.
"""
from __future__ import annotations

import copy
import json
import re
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from hepgraph.deep_search import MAX_LITERATURE_PAGE, DeepBudget, DeepSearch, DeepSearchError
from hepgraph.graph import Filters, Graph
from hepgraph.identity_guard import apply_identity_guard
from hepgraph.pipeline import build_snapshot, open_db, store_record
from hepgraph.remote import OVERSIZE_MESSAGE, RemoteError
from test_deep_search import Client, literature_query, page, paper, person, profiles, ref


class Corpus(Client):
    """Serves a real coauthorship corpus. `faults` distorts specific responses."""

    def __init__(self, works, people_ids, *, shrink_after=None, drop_page=None,
                 dup_page=None, gte_for=None, oversize_above=None, fail_at=None,
                 garbage_at=None, on_call=None):
        super().__init__(profiles(*people_ids))
        self.works = {w["id"]: w for w in works}
        self.by_person = {}
        for w in works:
            for a in w["metadata"]["authors"]:
                pid = a["record"]["$ref"].rsplit("/", 1)[-1]
                self.by_person.setdefault(pid, []).append(w)
        self.shrink_after = shrink_after or {}   # pid -> (page, fake_total)
        self.drop_page = drop_page or {}         # pid -> page
        self.dup_page = dup_page or {}           # pid -> page
        self.gte_for = set(gte_for or ())        # pids whose total is a lower bound
        self.oversize_above = oversize_above     # int: raise if size > this
        self.fail_at = fail_at                   # (pid, page) -> raise 429
        self.garbage_at = garbage_at             # (pid, page) -> inject bad record
        self.on_call = on_call
        self.lit_calls = []

    def _pid_of(self, query):
        refs = re.findall(r"authors\.record\.\$ref:([0-9]+)", query)
        return refs if refs else None

    def search(self, collection, query, *, size=25, page=1, sort=None, deadline=None):
        if self.on_call:
            self.on_call(collection, query, page, size)
        if collection != "literature":
            return super().search(collection, query, size=size, page=page, sort=sort, deadline=deadline)
        refs = self._pid_of(query)
        if not refs:
            return {"hits": {"total": 0, "hits": []}}
        if len(refs) > 1:   # pair / cross query: intersection
            sets = [{w["id"] for w in self.by_person.get(r, [])} for r in refs]
            ids = set.intersection(*sets) if sets else set()
            hits = [self.works[i] for i in sorted(ids)]
            return {"hits": {"total": len(hits), "hits": copy.deepcopy(hits[(page-1)*size:page*size])}}
        pid = refs[0]
        self.lit_calls.append((pid, page, size))
        if self.oversize_above is not None and size > self.oversize_above:
            raise RemoteError("resource_limit", OVERSIZE_MESSAGE)
        if self.fail_at == (pid, page):
            raise RemoteError("resource_limit", "INSPIRE rate limited this client; retry after at least 5 seconds")
        works = self.by_person.get(pid, [])
        served_page = page
        if self.dup_page.get(pid) == page:
            served_page = page - 1
        window = works[(served_page-1)*size:served_page*size]
        if self.drop_page.get(pid) == page:
            window = []
        total = len(works)
        if pid in self.shrink_after:
            trigger, fake = self.shrink_after[pid]
            if page >= trigger:
                total = fake
        hits = copy.deepcopy(window)
        if self.garbage_at == (pid, page) and hits:
            hits[0] = {"id": "garbage", "metadata": {"control_number": "garbage", "authors": "not-a-list"}}
        if pid in self.gte_for:
            return {"hits": {"total": {"value": total, "relation": "gte"}, "hits": hits}}
        return {"hits": {"total": total, "hits": hits}}

sys.path.insert(0, "/Users/yatharthsirohi/Desktop/HEP-Graph")
sys.path.insert(0, "/Users/yatharthsirohi/Desktop/HEP-Graph/tests")


def budget(**o):
    v = dict(max_seconds=30.0, max_requests=720, max_works=20000, max_people=20000,
             page_size=MAX_LITERATURE_PAGE, max_pages_per_person=50)
    v.update(o)
    return DeepBudget(**v)

def neighbourhood_of(client, source, target=2, iters=400, **bo):
    """Drive the oracle on `source` until COMPLETE or iterations run out."""
    session = DeepSearch(client).start(source, target, Filters(genealogy=False))
    try:
        session._run_requests = 0
        session._run_deadline = time.monotonic() + 30
        session._budget = budget(**bo)
        session._begin_proof(session._budget)
        found = None
        for _ in range(iters):
            found = session._oracle.neighborhood(str(source))
            if found.status == "complete":
                break
        return found, session
    except Exception as e:
        return e, session

def report(name, expected, actual, verdict):
    print(f"\n{'='*70}\n{name}\n{'-'*70}")
    print(f"EXPECTED: {expected}")
    print(f"ACTUAL:   {actual}")
    print(f"VERDICT:  {verdict}")



sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

N = 700
def big_corpus():
    works = [paper(1000 + i, [1, 100 + i]) for i in range(N)]
    return works, [1, 2] + [100 + i for i in range(N)]

def certify(**faults):
    works, ids = big_corpus()
    c = Corpus(works, ids, **faults)
    found, s = neighbourhood_of(c, 1, iters=3000, page_size=100)
    st, mem = getattr(found, "status", None), set(getattr(found, "members", ()) or ())
    s.close()
    return st, mem

# --- D1/D2/D3: COMPLETE is claimed for a pagination that lost records -------
def test_D1_a_missing_middle_page_must_not_certify_complete():
    st, mem = certify(drop_page={"1": 3})
    assert not (st == "complete" and len(mem) < N), f"COMPLETE with {N-len(mem)} works never retrieved"

def test_D2_a_duplicated_page_must_not_certify_complete():
    st, mem = certify(dup_page={"1": 4})
    assert not (st == "complete" and len(mem) < N), f"COMPLETE with {N-len(mem)} works never retrieved"

def test_D3_a_total_that_shrinks_mid_pagination_must_not_certify_complete():
    st, mem = certify(shrink_after={"1": (2, 150)})
    assert not (st == "complete" and len(mem) < N), f"COMPLETE with {N-len(mem)} works never retrieved"

# --- D4: `no_path` returned while a 2-hop route exists ----------------------
def test_D4_no_path_is_returned_although_a_two_hop_route_exists():
    works = [paper(1000 + i, [1, 10 + i]) for i in range(4)] + [paper(1500, [1, 20]), paper(1600, [1, 14])]
    works += [paper(2500, [20, 2])]
    works += [paper(2000 + i, [2, 30 + i]) for i in range(3)] + [paper(2600, [2, 34])]
    works = ([paper(1000 + i, [1, 10 + i]) for i in range(4)] + [paper(1500, [1, 20]), paper(1600, [1, 14])]
             + [paper(2000 + i, [2, 30 + i]) for i in range(4)] + [paper(2500, [2, 20]), paper(2600, [2, 34])])
    ids = [1, 2, 20] + list(range(10, 15)) + list(range(30, 35))
    c = Corpus(works, ids, shrink_after={"1": (2, 4), "2": (2, 4)})
    s = DeepSearch(c).start(1, 2, Filters(genealogy=False))
    r = s.run(budget(page_size=2, max_pages_per_person=50)); s.close()
    assert r["status"] != "no_path", "no_path although 1--20--2 exists on an unread page"

# --- D5: global_shortest_proven on a 3-hop route when 2 hops exists ---------
@pytest.mark.parametrize("faults", [
    dict(shrink_after={"1": (2, 4), "2": (2, 4)}),
    dict(drop_page={"1": 3, "2": 3}),
    dict(dup_page={"1": 3, "2": 3}),
])
def test_D5_global_shortest_proven_on_a_longer_route(faults):
    works = ([paper(1000 + i, [1, 10 + i]) for i in range(4)] + [paper(1500, [1, 20]), paper(1600, [1, 14])]
             + [paper(2000, [2, 40])] + [paper(2001 + i, [2, 31 + i]) for i in range(3)]
             + [paper(2500, [2, 20]), paper(2600, [2, 34])] + [paper(3001, [10, 40])])
    ids = [1, 2, 10, 11, 12, 13, 14, 20, 31, 32, 33, 34, 40]
    c = Corpus(works, ids, **faults)
    s = DeepSearch(c).start(1, 2, Filters(genealogy=False))
    b = budget(page_size=2, max_pages_per_person=50)
    for _ in range(12):
        r = s.run(b)
        if not r.get("can_continue"): break
    hops = r["paths"][0]["hops"] if r["paths"] else None
    s.close()
    assert not (r["global_shortest_proven"] and hops and hops > 2), \
        f"global_shortest_proven=True on {hops} hops while 1--20--2 exists"

# --- D6: coauthor identity guard has no surname test -----------------------
FIX = json.loads(Path("/Users/yatharthsirohi/Desktop/HEP-Graph/tests/fixtures/identity_collisions.json").read_text())
BERG, BID = FIX["bergmann_profile"], "1016635"

def test_D6_a_different_surname_byline_must_not_resolve_to_that_profile():
    w = paper(9001, [7001, BID, 7002], names={BID: "Schmidt, Anna"})
    w["metadata"]["earliest_date"] = w["metadata"]["preprint_date"] = "2023-05-01"
    db = open_db(":memory:")
    store_record(db, "authors", BERG); store_record(db, "literature", w)
    after = apply_identity_guard(build_snapshot(db, {"label": "t"}), db)
    db.close()
    assert BID not in after["works"][0]["authors"], \
        "a 2023 'Schmidt, Anna' byline resolved to the 'Bergmann, Peter Gabriel' profile (died 2002)"

# --- D7: an erratum sharing the original's DOI erases the original ---------
def test_D7_an_erratum_must_not_erase_the_original_work():
    base = paper(5001, [1, 2], doi="10.1/abc")
    err = paper(5002, [1, 2], doi="10.1/abc")
    err["metadata"]["titles"] = [{"title": "Erratum: Work 5001"}]
    db = open_db(":memory:")
    store_record(db, "literature", base); store_record(db, "literature", err)
    snap = build_snapshot(db, {"label": "t"})
    g = Graph(snap, Filters(genealogy=False)); db.close()
    assert g._edge("1", "2") is not None, \
        f"the erratum became the group's representative and the edge vanished ({[w['title'] for w in snap['works']]})"

# --- D8: one poison record permanently blocks a provable alternative route --
def test_D8_a_poison_record_must_not_permanently_block_a_provable_route():
    works = ([paper(1000 + i, [1, 100 + i]) for i in range(6)] + [paper(1500, [1, 20]), paper(2500, [20, 2])]
             + [paper(2000 + i, [2, 300 + i]) for i in range(6)])
    ids = [1, 2, 20] + [100 + i for i in range(6)] + [300 + i for i in range(6)]
    c = Corpus(works, ids, garbage_at=("1", 3))
    s = DeepSearch(c).start(1, 2, Filters(genealogy=False))
    b = budget(page_size=2, max_pages_per_person=50)
    for _ in range(8):
        r = s.run(b)
        if not r.get("can_continue"): break
    s.close()
    assert r["paths"], "eight slices returned no route, all spent re-requesting the same failing page"