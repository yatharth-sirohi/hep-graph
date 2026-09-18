"""Reproducible local graph benchmarks and real-data evidence checks.

This script performs no network requests unless ``--url`` is explicitly
provided. It writes measured JSON under ignored ``test-results/`` by default.
"""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import gzip
import json
import os
from pathlib import Path
import platform
import random
import resource
import sqlite3
import statistics
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE = ROOT / "data" / "hepgraph.sqlite"
DEFAULT_OUTPUT = ROOT / "test-results" / "benchmarks.json"
RANDOM_SEED = 1729

# Make ``python tests/benchmark.py`` work from the source root as documented.
sys.path.insert(0, str(ROOT))
from hepgraph.graph import Filters, Graph


def now() -> float:
    return time.perf_counter()


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # macOS reports bytes; Linux and the BSDs traditionally report KiB.
    return int(value if sys.platform == "darwin" else value * 1024)


def hardware() -> dict:
    result = {"system": platform.system(), "release": platform.release(), "machine": platform.machine(),
              "processor": platform.processor() or None, "python": platform.python_version(),
              "rss_unit": "bytes (macOS ru_maxrss)" if sys.platform == "darwin" else "bytes (Linux/BSD KiB ru_maxrss converted)"}
    for key in ("hw.model", "hw.ncpu"):
        try:
            completed = subprocess.run(["sysctl", "-n", key], check=True, capture_output=True, text=True, timeout=2)
            result[key] = completed.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            result[key] = None
    return result


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(round((p / 100) * (len(ordered) - 1))))]


def timings(rows: list[dict]) -> dict:
    durations = [row["duration_s"] for row in rows]
    return {"count": len(rows), "total_s": sum(durations), "mean_s": statistics.mean(durations) if durations else None,
            "median_s": statistics.median(durations) if durations else None, "p95_s": percentile(durations, 95),
            "statuses": dict(Counter(row["status"] for row in rows)), "runs": rows}


def load_snapshot(path: Path) -> tuple[dict, dict]:
    started = now()
    raw = path.read_bytes()
    read_s = now() - started
    started = now()
    snapshot = json.loads(raw)
    parse_s = now() - started
    return snapshot, {"path": str(path), "bytes": path.stat().st_size, "read_s": read_s, "parse_s": parse_s}


def build_graph(snapshot: dict, filters: Filters) -> tuple[Graph, dict]:
    import tracemalloc

    rss_before = rss_bytes()
    tracemalloc.start()
    started = now()
    graph = Graph(snapshot, filters)
    elapsed = now() - started
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return graph, {"filters": filters.to_dict(), "elapsed_s": elapsed, "tracemalloc_current_bytes": current,
                   "tracemalloc_peak_bytes": peak, "rss_before_bytes": rss_before, "rss_after_bytes": rss_bytes(),
                   "people": len(graph.people), "eligible_works": len(graph.works), "phd_edges": len(graph.phd),
                   "pair_cache_length": len(graph._pair_cache), "neighbor_cache_length": len(graph._neighbor_cache)}


def path_record(graph: Graph, source: str, target: str) -> dict:
    started = now()
    result = graph.find_paths(source, target)
    elapsed = now() - started
    first = result.get("paths", [{}])[0] if result.get("paths") else {}
    return {"source": source, "target": target, "status": result.get("status"), "exact": result.get("exact"),
            "hops": first.get("hops"), "path_count": len(result.get("paths", [])), "duration_s": elapsed}


def representative_pairs(snapshot: dict) -> list[tuple[str, str]]:
    pairs = [(str(item["source"]), str(item["target"])) for item in snapshot.get("examples", [])]
    ids = sorted(str(person["id"]) for person in snapshot.get("people", []))
    rng = random.Random(RANDOM_SEED)
    seen = set(pairs)
    while len(pairs) < 20:
        source, target = rng.sample(ids, 2)
        if (source, target) not in seen:
            pairs.append((source, target)); seen.add((source, target))
    return pairs


def path_benchmark(snapshot: dict) -> dict:
    graph, build = build_graph(snapshot, Filters())
    pairs = representative_pairs(snapshot)
    cold, warm = [], []
    for source, target in pairs:
        graph._pair_cache.clear(); graph._neighbor_cache.clear()
        cold.append(path_record(graph, source, target))
        warm.append(path_record(graph, source, target))
    return {"pair_seed": RANDOM_SEED, "pairs": [{"source": a, "target": b} for a, b in pairs],
            "graph_build": build, "cold": timings(cold), "warm": timings(warm)}


def random_paths(snapshot: dict, count: int = 100) -> dict:
    graph, build = build_graph(snapshot, Filters())
    ids = sorted(graph.people)
    rng = random.Random(RANDOM_SEED)
    rows = []
    for _ in range(count):
        source, target = rng.sample(ids, 2)
        rows.append(path_record(graph, source, target))
    return {"seed": RANDOM_SEED, "requested": count, "graph_build": build, **timings(rows)}


def giant_direct(snapshot: dict) -> dict:
    work = next((item for item in snapshot.get("works", []) if str(item.get("id")) == "1124337"), None)
    if work is None:
        return {"status": "not_available", "work_id": "1124337"}
    authors = [str(item) for item in work.get("authors", [])]
    result = {"work_id": str(work["id"]), "title": work.get("title"), "full_author_count": work.get("author_count"),
              "resolved_author_count": len(authors), "first_author": authors[0] if authors else None,
              "last_author": authors[-1] if authors else None}
    if len(authors) < 2:
        result["status"] = "not_available"
        return result
    source, target = authors[0], authors[-1]
    for label, filters in (("all_authors", Filters(max_authors=None)), ("cap_10", Filters()), ("min_shared_2", Filters(max_authors=None, min_shared=2))):
        graph, build = build_graph(snapshot, filters)
        measured = path_record(graph, source, target)
        result[label] = {"filters": filters.to_dict(), "graph_build": build, **measured,
                         "pair_cache_length_after": len(graph._pair_cache), "neighbor_cache_length_after": len(graph._neighbor_cache)}
    return result


def centralities(snapshot: dict) -> dict:
    graph, build = build_graph(snapshot, Filters())
    result = {"graph_build": build, "metrics": {}}
    for metric in ("degree", "combined_degree", "harmonic", "betweenness", "eccentricity"):
        started = now()
        response = graph.centrality(metric, limit=25)
        result["metrics"][metric] = {"duration_s": now() - started, "status": response.get("status"),
                                     "exact": response.get("exact"), "method": response.get("method"),
                                     "population": response.get("population"), "row_count": len(response.get("rows", [])),
                                     "message": response.get("message"), "scope": response.get("scope")}
    return result


def evidence_database(database: Path, provenance: Path | None) -> tuple[sqlite3.Connection, str]:
    """Open explicitly supplied build state or source evidence."""
    if database.exists():
        return sqlite3.connect(database), "local_build_database"
    if provenance is None:
        raise ValueError("pass --database or --provenance for raw evidence checks")
    fixture = json.loads(gzip.decompress(provenance.read_bytes()))
    connection = sqlite3.connect(":memory:")
    for table, data in fixture["tables"].items():
        connection.execute(f"CREATE TABLE {table} ({data['schema']})")
        if data["rows"]:
            slots = ",".join("?" for _ in data["rows"][0])
            connection.executemany(f"INSERT INTO {table} VALUES ({slots})", data["rows"])
    return connection, "frozen_public_fixture"


def raw_edge_checks(database: Path, provenance: Path | None, graph: Graph, pair: tuple[str, str]) -> dict:
    result = graph.find_paths(*pair)
    checked_edges = []
    connection, evidence_source = evidence_database(database, provenance)
    try:
        for path in result.get("paths", [])[:1]:
            for edge in path.get("edges", []):
                item = {"source": edge["source"], "target": edge["target"], "types": edge.get("types", []), "works": [], "phd": []}
                endpoint_identifiers = {}
                for endpoint in (edge["source"], edge["target"]):
                    row = connection.execute("SELECT payload FROM source_records WHERE collection='authors' AND recid=?", (str(endpoint),)).fetchone()
                    if row:
                        payload = json.loads(row[0])
                        endpoint_identifiers[str(endpoint)] = payload.get("ids", [])
                item["endpoint_profile_identifiers"] = endpoint_identifiers
                for work in edge.get("works", []):
                    source_ids = [str(value) for value in work.get("source_ids", [work.get("id")])]
                    raw_matches = []
                    for source_id in source_ids:
                        row = connection.execute("SELECT payload FROM source_records WHERE collection='literature' AND recid=?", (source_id,)).fetchone()
                        if not row:
                            continue
                        payload = json.loads(row[0])
                        authors = [{"record": str(author.get("record")), "roles": author.get("inspire_roles", []), "name": author.get("full_name")} for author in payload.get("authors", []) if author.get("record")]
                        members = {author["record"] for author in authors}
                        if edge["source"] in members and edge["target"] in members:
                            raw_matches.extend(authors)
                    item["works"].append({"id": str(work.get("id")), "source_ids": source_ids, "raw_author_records": raw_matches,
                                          "raw_pair_evidence": bool(raw_matches)})
                for phd in edge.get("phd", []):
                    source_id = str(phd.get("source_record"))
                    row = connection.execute("SELECT payload FROM source_records WHERE collection='authors' AND recid=?", (source_id,)).fetchone()
                    profile_evidence = False
                    advisers = []
                    if row:
                        payload = json.loads(row[0])
                        advisers = payload.get("advisors", [])
                        profile_evidence = any(str(adviser.get("record")) == str(phd.get("adviser")) and
                                               str(adviser.get("degree_type", "")).lower() == "phd" and
                                               adviser.get("hidden") is not True for adviser in advisers)
                    item["phd"].append({"source_record": source_id, "profile_record_found": row is not None,
                                        "explicit_phd_degree": profile_evidence, "adviser_rows": len(advisers)})
                checked_edges.append(item)
    finally:
        connection.close()
    return {"source": pair[0], "target": pair[1], "status": result.get("status"), "hops": result.get("paths", [{}])[0].get("hops") if result.get("paths") else None,
            "path_count": len(result.get("paths", [])), "edges": checked_edges,
            "evidence_source": evidence_source,
            "all_displayed_edges_have_raw_evidence": all(all(work.get("raw_pair_evidence") for work in edge["works"]) for edge in checked_edges if edge["works"]),
            "profile_phd_edges_explicit": all(item["explicit_phd_degree"] for edge in checked_edges for item in edge["phd"]) if any(edge["phd"] for edge in checked_edges) else None}


def real_data_checks(snapshot: dict, database: Path, provenance: Path | None) -> dict:
    if not database.exists() and provenance is None:
        return {"status": "skipped", "reason": "pass --database or --provenance for raw evidence checks"}
    graph, build = build_graph(snapshot, Filters())
    pairs = [("1621061", "1019647", "Hostert to Pascoli"), ("1010044", "983692", "Feynman to Wheeler"),
             ("983328", "1007454", "Witten to Gross"), ("1621061", "1013775", "Hostert to Cheung/Kingman")]
    checks = []
    for source, target, label in pairs:
        checked = raw_edge_checks(database, provenance, graph, (source, target))
        checked["label"] = label
        if label == "Hostert to Cheung/Kingman":
            checked["expected_hops_if_connected"] = 5
            checked["matches_expected_if_connected"] = checked["status"] != "ok" or checked["hops"] == 5
        checks.append(checked)
    return {"filters": Filters().to_dict(), "graph_build": build, "checks": checks}


def http_workload(base_url: str) -> dict:
    base_url = base_url.rstrip("/")
    paths = ["/api/health", "/api/dataset", "/api/search?" + urlencode({"q": "Witten", "live": "0"})]
    def one(path: str) -> dict:
        started = now()
        try:
            with urlopen(Request(base_url + path), timeout=15) as response:
                body = response.read()
                return {"path": path, "status": response.status, "bytes": len(body), "duration_s": now() - started}
        except (HTTPError, URLError, TimeoutError) as exc:
            return {"path": path, "status": getattr(exc, "code", "error"), "error": type(exc).__name__, "duration_s": now() - started}
    with ThreadPoolExecutor(max_workers=len(paths)) as executor:
        rows = list(executor.map(one, paths))
    return {"status": "executed", "base_url": base_url, "concurrency": len(paths), "requests": rows}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True,
                        help="explicit local graph export to benchmark; no example dataset is bundled")
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--provenance", type=Path,
                        help="optional source evidence export for independent checks")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--url", help="optional already-running local HTTP service URL")
    args = parser.parse_args(argv)
    snapshot, load = load_snapshot(args.snapshot)
    payload = {"generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "hardware": hardware(),
               "inputs": {"snapshot": load | {"version": snapshot.get("version"), "created_at": snapshot.get("created_at"),
                                                "people": len(snapshot.get("people", [])), "works": len(snapshot.get("works", [])), "phd": len(snapshot.get("phd", []))},
                          "database": {"path": str(args.database), "bytes": args.database.stat().st_size if args.database.exists() else None}},
               "load": load, "paths": path_benchmark(snapshot), "random_paths": random_paths(snapshot),
               "giant_direct": giant_direct(snapshot), "centrality": centralities(snapshot),
               "real_data_checks": real_data_checks(snapshot, args.database, args.provenance),
               "http": http_workload(args.url) if args.url else {"status": "skipped", "reason": "--url not supplied"}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "snapshot_version": snapshot.get("version"), "people": len(snapshot.get("people", [])), "works": len(snapshot.get("works", []))}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
