"""Explicit, bounded real-INSPIRE regression checks against a running HEP Graph.

Run from a clone with Python 3.11+: python tests/live_regression.py --group demo
This script is intentionally outside pytest collection; live checks require an
explicit invocation. It imports no production graph or normalization helpers.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

PROJECT = Path(__file__).resolve().parents[1]


def request(base, path, post=False):
    try:
        with urlopen(Request(base + path, method="POST" if post else "GET"), timeout=25) as response:
            return json.load(response)
    except HTTPError as exc:
        try:
            return json.load(exc)
        except (ValueError, OSError):
            raise RuntimeError(f"HTTP {exc.code} on {path}") from exc


def validate(case, result):
    """Check independent path/edge/filter invariants, not global connectivity."""
    errors = []
    source, target = str(case["source"]), str(case["target"])
    f = {"max_authors": 10, "min_authors": 1, "min_shared": 1,
         "genealogy": False, "year_start": None, "year_end": None, **case.get("filters", {})}
    paths = result.get("paths", [])
    if case.get("must_find", True) and not paths:
        errors.append("No evidenced route returned within the test allowance.")
    for route in paths:
        people = [str(p["id"]) for p in route["people"]]
        if not people or people[0] != source or people[-1] != target:
            errors.append("Returned endpoints do not match the selected exact identities.")
        if len(people) != len(set(people)) or route["hops"] != len(people)-1 or len(route["edges"]) != route["hops"]:
            errors.append("Path is cyclic or its hop count is inconsistent.")
        if case.get("max_hops") is not None and route["hops"] > case["max_hops"]:
            errors.append("A separately evidenced shorter route is known for this pair.")
        if case.get("forbid_direct") and route["hops"] == 1:
            errors.append("A forbidden direct connection passed the selected paper mode.")
        for a, b, edge in zip(people, people[1:], route["edges"]):
            pair = {a, b}
            if pair != {str(edge["source"]), str(edge["target"])}:
                errors.append("Evidence is attached to the wrong path hop.")
            works = edge.get("works", [])
            distinct = {w["id"] for w in works}
            if len(distinct) != len(works):
                errors.append("Duplicate work IDs inflated an edge.")
            if "coauthor" in edge.get("types", []):
                if edge.get("shared_works", 0) < f["min_shared"] or len(works) < f["min_shared"]:
                    errors.append("Coauthorship lacks the required distinct work evidence.")
            elif not f["genealogy"] or not edge.get("phd"):
                errors.append("A hop has neither permitted coauthorship nor sourced doctoral evidence.")
            if not f["genealogy"] and "phd" in edge.get("types", []):
                errors.append("Genealogy was used while disabled.")
            for w in works:
                if not pair <= set(map(str, w.get("authors", []))):
                    errors.append("Both stable author IDs are not present in supporting work.")
                count = w.get("author_count")
                if not isinstance(count, int) or isinstance(count, bool) or count < f["min_authors"] or (f["max_authors"] is not None and count > f["max_authors"]):
                    errors.append("Full author count violates the selected graph definition.")
                types = set(w.get("document_types", []))
                if not types & {"article", "conference paper"} or types & {"thesis", "book", "book chapter", "proceedings"}:
                    errors.append("An ineligible document type passed the graph filter.")
                if re.match(r"^\s*(?:erratum|errata|corrigendum)(?:$|\W)", w.get("title", ""), re.I):
                    errors.append("A standalone correction notice counted as a collaboration.")
                for key, relation in (("year_start", lambda y, bound: y >= bound), ("year_end", lambda y, bound: y <= bound)):
                    if f[key] is not None and (not isinstance(w.get("year"), int) or not relation(w["year"], f[key])):
                        errors.append("Work date violates the selected date range.")
                if w.get("source_url") != f"https://inspirehep.net/literature/{w['id']}":
                    errors.append("Work evidence lacks its canonical INSPIRE link.")
                if str(w["id"]) in {"2150122", "2627214", "2623742", "2606257", "1665003"} and "1016635" in pair:
                    errors.append("Known Peter/Philip Bergmann identity collision escaped quarantine.")
            for phd in edge.get("phd", []):
                if phd.get("degree") != "PhD" or {str(phd.get("adviser")), str(phd.get("student"))} != pair or urlsplit(phd.get("source_url", "")).scheme != "https":
                    errors.append("Doctoral evidence lacks an explicit degree, direction or HTTPS source.")
    if not paths and result.get("status") == "no_path":
        errors.append("A bounded live search was presented as no path.")
    if result.get("global_shortest_proven") and paths and paths[0]["hops"] > 2:
        # Update this deliberate contract guard only alongside a reviewed proof
        # for deeper live searches; ordinary local BFS exactness is insufficient.
        errors.append("A deeper live route unexpectedly claims global shortestness.")
    return sorted(set(errors))


def run_case(base, case, seconds, output, repeat):
    f = {"max_authors": 10, "min_authors": 1, "min_shared": 1,
         "genealogy": False, **case.get("filters", {})}
    params = {"mode": "live", "search": "deep", "source": str(case["source"]), "target": str(case["target"])}
    params.update({k: ("all" if v is None and k == "max_authors" else str(v).lower() if isinstance(v, bool) else v)
                   for k, v in f.items() if v is not None or k == "max_authors"})
    path = "/api/path?" + urlencode(params)
    before = request(base, "/api/cache")
    start = time.monotonic()
    result = request(base, path)
    last_notice = start
    timed_out = False
    while result.get("status") == "searching":
        now = time.monotonic()
        if now - start >= seconds:
            timed_out = True
            result = request(base, f"/api/search-jobs/{result['job_id']}/cancel?mode=live", True)
            break
        if now - last_notice >= 45:
            print(json.dumps({"case": case["id"], "progress": result.get("progress"), "verified_hops": [r["hops"] for r in result.get("paths", [])]}), flush=True)
            last_notice = now
        time.sleep(1.0)
        result = request(base, f"/api/search-jobs/{result['job_id']}?mode=live")
    elapsed = round(time.monotonic() - start, 3)
    errors = validate(case, result)
    repeated = None
    if repeat and result.get("status") == "ok":
        again = time.monotonic()
        cached = request(base, path)
        repeated = {"seconds": round(time.monotonic()-again, 4), "job_id": cached.get("job_id"),
                    "same_job": cached.get("job_id") == result.get("job_id"), "status": cached.get("status")}
        if cached.get("status") != "ok" or not repeated["same_job"]:
            errors.append("A completed recent identical search was restarted instead of reused.")
    report = {"case": case["id"], "label": case["label"], "parameters": params,
              "checked_at": datetime.now(timezone.utc).isoformat(), "wall_seconds": elapsed,
              "test_allowance_seconds": seconds, "stopped_at_test_allowance": timed_out,
              "problems": errors, "validation": "failed" if errors else ("passed" if result.get("paths") else "honest_incomplete"),
              "repeat": repeated, "cache_before": before, "cache_after": request(base, "/api/cache"), "result": result}
    output.mkdir(parents=True, exist_ok=True)
    (output/(case["id"]+".json")).write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps({"case": case["id"], "validation": report["validation"], "seconds": elapsed,
                      "repeat": repeated, "errors": errors, "routes": [[p["name"] for p in r["people"]] for r in result.get("paths", [])],
                      "hops": [r["hops"] for r in result.get("paths", [])], "global_shortest_proven": result.get("global_shortest_proven")}), flush=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8765")
    parser.add_argument("--manifest", type=Path, default=PROJECT/"tests/fixtures/live_pairs.json")
    parser.add_argument("--group", default="demo")
    parser.add_argument("--cases", nargs="+")
    parser.add_argument("--seconds", type=int, default=180)
    parser.add_argument("--workers", type=int, choices=[1, 2], default=1)
    parser.add_argument("--repeat", action="store_true")
    parser.add_argument("--output", type=Path, default=PROJECT/"test-results/live")
    args = parser.parse_args()
    if not 1 <= args.seconds <= 1800:
        parser.error("--seconds must be 1..1800 per case")
    cases = json.loads(args.manifest.read_text())["cases"]
    selected = [c for c in cases if (c["id"] in args.cases if args.cases else args.group == "all" or args.group in c["groups"])]
    if not selected:
        parser.error("No matching cases")
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_case, args.url.rstrip("/"), c, args.seconds, args.output, args.repeat) for c in selected]
        reports = [f.result() for f in futures]
    summary = {"cases": len(reports), "passed": sum(r["validation"] == "passed" for r in reports),
               "honest_incomplete": sum(r["validation"] == "honest_incomplete" for r in reports),
               "failed": sum(bool(r["problems"]) for r in reports), "source": args.url,
               "concurrency": args.workers, "max_seconds_per_case": args.seconds}
    (args.output/"summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary), flush=True)
    return int(bool(summary["failed"]))


if __name__ == "__main__":
    raise SystemExit(main())
