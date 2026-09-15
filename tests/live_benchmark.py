"""Cold-cache live INSPIRE benchmarks for the path engine.

Deliberately outside pytest collection: it performs real upstream requests.

    python tests/live_benchmark.py --out results.json [--case hostert_pascoli]

Each case runs with a fresh :class:`RemoteClient`, so caches start cold; the
process-wide request pacer is shared, which is what production sees too.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import threading
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hepgraph.deep_search import DeepBudget, DeepSearch
from hepgraph.graph import Filters
from hepgraph.remote import RemoteClient

# Resolved once through INSPIRE's author collection; see the overnight report.
PEOPLE = {
    "hostert": "1621061", "pascoli": "1019647", "einstein": "1010907",
    "dirac": "1011729", "feynman": "1010044", "wheeler": "983692",
    "witten": "983328", "ellis": "1010819", "visser": "2955074",
    "uppu": "1948928", "rodgers": "991505", "massey": "1054235",
    "aad": "1066085", "abbott": "1019091",
}

SMALL = {"max_authors": 10, "min_authors": 1, "genealogy": False}
LARGE = {"max_authors": None, "min_authors": 11, "genealogy": False}
ALL = {"max_authors": None, "min_authors": 1, "genealogy": False}

CASES = [
    ("hostert_pascoli", "hostert", "pascoli", SMALL),
    ("hostert_dirac", "hostert", "dirac", SMALL),
    ("hostert_ellis", "hostert", "ellis", SMALL),
    ("hostert_feynman", "hostert", "feynman", SMALL),
    ("hostert_einstein", "hostert", "einstein", SMALL),
    ("hostert_witten", "hostert", "witten", SMALL),
    ("feynman_wheeler", "feynman", "wheeler", SMALL),
    ("witten_visser", "witten", "visser", SMALL),
    ("visser_uppu", "visser", "uppu", SMALL),
    ("visser_rodgers", "visser", "rodgers", SMALL),
    ("visser_massey", "visser", "massey", SMALL),
    ("aad_abbott_large", "aad", "abbott", LARGE),
    # Fresh cross-field pairs, not used during development.
    ("pascoli_wheeler", "pascoli", "wheeler", SMALL),
    ("uppu_ellis", "uppu", "ellis", SMALL),
    ("rodgers_dirac", "rodgers", "dirac", SMALL),
    ("ellis_massey_all", "ellis", "massey", ALL),
]


def run_case(name, source, target, filters, cap_seconds, slice_seconds):
    client = RemoteClient()
    session = DeepSearch(client).start(PEOPLE[source], PEOPLE[target], Filters.from_dict(filters))
    started = time.monotonic()
    first_path_at = None
    result = None
    slices = 0
    try:
        while True:
            remaining = cap_seconds - (time.monotonic() - started)
            if remaining <= 1:
                break
            budget = DeepBudget(max_seconds=min(slice_seconds, remaining), max_requests=240,
                                max_works=20_000, max_people=30_000)
            result = session.run(budget)
            slices += 1
            if first_path_at is None and result.get("paths"):
                first_path_at = round(time.monotonic() - started, 2)
            if not result.get("can_continue"):
                break
    finally:
        elapsed = round(time.monotonic() - started, 2)
        info = client.cache_info()
        session.close()

    result = result or {}
    paths = result.get("paths") or []
    progress = result.get("progress") or {}
    return {
        "case": name, "source": source, "target": target, "filters": filters,
        "status": result.get("status"),
        "proven_shortest": bool(result.get("global_shortest_proven")),
        "hops": paths[0].get("hops") if paths else None,
        "elapsed_seconds": elapsed,
        "first_path_seconds": first_path_at,
        "hit_cap": elapsed >= cap_seconds - 1,
        "slices": slices,
        "api_calls": progress.get("requests"),
        "literature_pages": progress.get("literature_pages"),
        "literature_hits": progress.get("literature_hits"),
        # wire_bytes is traffic; layers[*]["bytes"] is live cache residency,
        # which is a different and much smaller number.
        "bytes": sum(layer.get("wire_bytes", 0) for layer in (info.get("layers") or {}).values()),
        "layers": {name: {"req": layer.get("upstream_requests", 0),
                          "hits": layer.get("hits", 0),
                          "mb": round(layer.get("wire_bytes", 0) / 1048576, 2)}
                   for name, layer in (info.get("layers") or {}).items()},
        "works_fetched": progress.get("works_retrieved"),
        "people_explored": progress.get("people_explored"),
        "upstream_requests": info.get("upstream_requests"),
        "cache_hits": info.get("hits"),
        "coalesced": info.get("coalesced"),
        "lower_bound": result.get("lower_bound"),
        "upper_bound": result.get("upper_bound"),
        "message": (result.get("message") or "")[:160],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--cap", type=float, default=180.0)
    parser.add_argument("--slice", type=float, default=60.0)
    parser.add_argument("--label", default="")
    args = parser.parse_args()

    selected = [case for case in CASES if not args.case or case[0] in args.case]
    rows = []
    for name, source, target, filters in selected:
        try:
            row = run_case(name, source, target, filters, args.cap, args.slice)
        except Exception as error:  # a live benchmark must report, never abort
            row = {"case": name, "status": "harness_error", "message": f"{type(error).__name__}: {error}"}
        rows.append(row)
        print(json.dumps(row), flush=True)
    Path(args.out).write_text(json.dumps({"label": args.label, "rows": rows}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
