"""Live check that one OR-union query certifies the same neighbourhoods as
paging each person alone.

Deliberately outside pytest collection: it performs real upstream requests.

    python tests/live_batched_diff.py

A work naming any union member is returned by the union, so for every member
the set of union records naming them must equal the records their own query
returns. This reads five small-team authors both ways with RemoteClient, which
paces itself, and requires the per-author work-id sets to be identical.
"""
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hepgraph.deep_search import DeepSession
from hepgraph.graph import Filters
from hepgraph.remote import RemoteClient

PEOPLE = {"hostert": "1621061", "pascoli": "1019647", "visser": "2955074",
          "rodgers": "991505", "massey": "1054235"}
FILTERS = Filters(max_authors=10, min_authors=1, genealogy=False)
SIZE = 1000


def read_all(client, query, size):
    """Page a query to exhaustion. Returns {work id: {author ids}}, pages, exact."""
    works, page, exact = {}, 1, True
    while True:
        if page * size > 10_000:
            return works, page - 1, False
        response = client.search("literature", query, size=size, page=page, sort="mostrecent")
        hits = response["hits"]["hits"]
        total = response["hits"]["total"]
        if isinstance(total, dict):
            exact = exact and total.get("relation") == "eq"
            total = total["value"]
        for hit in hits:
            metadata = hit.get("metadata", {})
            works[str(metadata.get("control_number"))] = {
                (author.get("record") or {}).get("$ref", "").rsplit("/", 1)[-1]
                for author in metadata.get("authors", []) or []}
        if page * size >= total or not hits:
            return works, page, exact
        page += 1


def main() -> int:
    client = RemoteClient()
    started = time.monotonic()
    individual, individual_pages = {}, 0
    for name, pid in PEOPLE.items():
        works, pages, exact = read_all(client, DeepSession.literature_query(pid, FILTERS), SIZE)
        individual[pid] = set(works)
        individual_pages += pages
        print(f"{name:9} alone: {len(works):5} works in {pages} page(s){'' if exact else '  (floor count)'}")

    union_works, union_pages, exact = read_all(client, DeepSession.batch_query(PEOPLE.values(), FILTERS), SIZE)
    print(f"\nunion: {len(union_works)} distinct works in {union_pages} page(s){'' if exact else '  (floor count)'}")
    print(f"sum of individual totals: {sum(len(items) for items in individual.values())}")

    mismatches = 0
    for name, pid in PEOPLE.items():
        from_union = {work for work, authors in union_works.items() if pid in authors}
        ok = from_union == individual[pid]
        mismatches += 0 if ok else 1
        print(f"{name:9} union-owned {len(from_union):5}  alone {len(individual[pid]):5}  {'OK' if ok else 'MISMATCH'}")
        if not ok:
            print("   only alone:", sorted(individual[pid] - from_union)[:8])
            print("   only union:", sorted(from_union - individual[pid])[:8])
    print(f"\npages: {individual_pages} individually vs {union_pages} as one union; "
          f"{time.monotonic() - started:.1f}s; mismatches={mismatches}")
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
