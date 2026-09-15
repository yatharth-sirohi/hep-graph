"""Live check that a larger literature page certifies the same neighbourhood.

Deliberately outside pytest collection: it performs real upstream requests.

    python tests/live_neighborhood_diff.py

Page size changes what page N means, so it is the one change in the exact
neighbourhood path that could silently skip or repeat records. This builds each
neighbourhood twice, at the old size and the new one, and requires the neighbour
set and the supporting work set to be identical.
"""
import re, sys, time
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hepgraph.remote import RemoteClient

PEOPLE = {"Hostert":"1621061","Pascoli":"1019647","Rodgers":"991505",
          "Witten":"983328","Visser":"2955074","Uppu":"1948928"}
MODES = {"small":"author_count:1->10", "large":"author_count:11+"}
REF = re.compile(r"/(\d+)$")

def neighborhood(client, pid, clause, size):
    """Page to exhaustion and return (neighbour ids, work ids, requests)."""
    neighbours, works, page, reqs = set(), set(), 1, 0
    q = f"authors.record.$ref:{pid} AND {clause}"
    while True:
        if page * size > 10_000:
            return None, None, reqs          # window: cannot certify
        r = client.search("literature", q, size=size, page=page, sort="mostrecent")
        reqs += 1
        hits = r["hits"]["hits"]
        total = r["hits"]["total"]
        total = total.get("value") if isinstance(total, dict) else total
        for h in hits:
            md = h.get("metadata", {})
            works.add(str(md.get("control_number")))
            for a in md.get("authors", []) or []:
                ref = (a.get("record") or {}).get("$ref", "")
                m = REF.search(ref)
                if m and m.group(1) != pid:
                    neighbours.add(m.group(1))
        if page * size >= total or not hits:
            return neighbours, works, reqs
        page += 1

bad = 0
print(f"{'person':9} {'mode':6} {'size100':>18} {'size1000':>18}  match")
for name, pid in PEOPLE.items():
    for mode, clause in MODES.items():
        size_small = 5 if mode == "large" else 100
        size_big = 5 if mode == "large" else 1000
        a_n, a_w, a_r = neighborhood(RemoteClient(), pid, clause, size_small)
        b_n, b_w, b_r = neighborhood(RemoteClient(), pid, clause, size_big)
        if a_n is None or b_n is None:
            print(f"{name:9} {mode:6} {'window-capped':>18} {'window-capped':>18}  skipped")
            continue
        ok = (a_n == b_n) and (a_w == b_w)
        bad += 0 if ok else 1
        print(f"{name:9} {mode:6} {f'{len(a_n)}n/{len(a_w)}w/{a_r}r':>18} "
              f"{f'{len(b_n)}n/{len(b_w)}w/{b_r}r':>18}  {'OK' if ok else 'MISMATCH'}")
        if not ok:
            print("   neighbours only in 100:", sorted(a_n - b_n)[:8])
            print("   neighbours only in 1000:", sorted(b_n - a_n)[:8])
print(f"\nmismatches={bad}")
sys.exit(1 if bad else 0)
