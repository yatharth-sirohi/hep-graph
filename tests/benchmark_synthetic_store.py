"""Run a bounded, local-only synthetic graph-index comparison.

Usage: python tests/benchmark_synthetic_store.py
No INSPIRE calls, production data, cloud deployment or cost estimate.
"""

from __future__ import annotations

import json
from pathlib import Path
import random
import statistics
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hepgraph.graph import Filters
from hepgraph.providers import FixtureGraphProvider
from hepgraph.synthetic_store import SyntheticSQLiteProvider, build_synthetic_index


def corpus() -> dict:
    rng = random.Random(20260916)
    people = [{"id": str(i), "name": f"Synthetic {i}"} for i in range(3000)]
    works = []
    for i in range(1500):
        authors = rng.sample(range(500), rng.randrange(2, 11))
        works.append({"id": f"small-{i}", "document_types": ["article"],
                      "author_count": len(authors), "authors": [str(a) for a in authors],
                      "year": 2000 + i % 26})
    works.append({"id": "mega", "document_types": ["article"],
                  "author_count": 2932, "authors": [str(i) for i in range(2932)], "year": 2020})
    return {"version": "synthetic-benchmark", "people": people, "works": works, "phd": []}


def median_ms(call, repetitions: int = 30) -> float:
    values = []
    for _ in range(repetitions):
        start = time.perf_counter()
        call()
        values.append((time.perf_counter() - start) * 1000)
    return round(statistics.median(values), 3)


def main() -> None:
    sample = corpus()
    fixture = FixtureGraphProvider(sample, complete=True)
    with tempfile.TemporaryDirectory(prefix="hepgraph-synthetic-") as temporary:
        path = Path(temporary) / "candidate.sqlite"
        start = time.perf_counter()
        build_synthetic_index(sample, path)
        build_s = round(time.perf_counter() - start, 3)
        provider = SyntheticSQLiteProvider(path, complete_for_test=True)
        try:
            rows = []
            for label, filters in (("small", Filters(genealogy=False)),
                                   ("large", Filters(min_authors=11, max_authors=None, genealogy=False)),
                                   ("all", Filters(max_authors=None, genealogy=False))):
                for author in ("0", "500", "2900"):
                    expected = fixture.get_neighbors(author, filters).members
                    actual = provider.get_neighbors(author, filters).members
                    if actual != expected:
                        raise AssertionError(f"index mismatch: {label} {author}")
                    rows.append({"mode": label, "author": author, "neighbors": len(actual),
                                 "fixture_ms": median_ms(lambda: fixture.get_neighbors(author, filters)),
                                 "sqlite_ms": median_ms(lambda: provider.get_neighbors(author, filters))})
            print(json.dumps({"synthetic_only": True, "works": len(sample["works"]),
                              "people": len(sample["people"]), "index_bytes": path.stat().st_size,
                              "build_seconds": build_s, "queries": rows}, indent=2))
        finally:
            provider.close()


if __name__ == "__main__":
    main()
