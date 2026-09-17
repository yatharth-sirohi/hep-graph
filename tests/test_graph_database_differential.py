"""The provider must agree with ``Graph`` on every edge-affecting filter.

``Graph`` is the shipped definition of an eligible tie, so parity with it - not
a restatement of the rules in SQL - is what shows the migration preserves
meaning.  The corpus is randomised but seeded, and the comparison sweeps the
whole filter matrix over every person, so a disagreement on any one rule shows
up as a concrete pair rather than a vague count.
"""

from __future__ import annotations

import os
import random

import pytest

from hepgraph.graph import Filters, Graph
from hepgraph.neon_compact_import import SCHEMA
from hepgraph.neon_graph_provider import (CoverageClaim, GenealogyOverlay,
                                          NeonCompactGraphProvider)

psycopg = pytest.importorskip("psycopg")

URL = os.environ.get("HEPGRAPH_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not URL, reason="HEPGRAPH_TEST_DATABASE_URL is not set")

IMPORT_ID = "differential"
OVERLAY_ID = "differential-overlay"
PEOPLE = [str(1000 + index) for index in range(24)]

# The importer's own ingest-time eligibility rules, which the compact tables
# cannot express and therefore cannot be re-checked by the provider.
ALLOWED = {"article", "conference paper"}
EXCLUDED = {"thesis", "book", "book chapter", "proceedings"}


def _person(person_id: str) -> dict:
    return {"id": person_id, "name": f"Person {person_id}", "aliases": [], "affiliations": [],
            "orcid": None, "profile_status": "profile",
            "source_url": f"https://inspirehep.net/authors/{person_id}"}


def _corpus() -> dict:
    """A seeded corpus with the awkward cases deliberately represented."""
    rng = random.Random(20260916)
    works = []
    for index in range(120):
        work_id = str(5000 + index)
        size = rng.choice([2, 2, 3, 3, 4, 6, 12, 40, 900])
        authors = sorted(rng.sample(PEOPLE, min(size, len(PEOPLE))))
        # A large collaboration keeps its true author count even though only a
        # few of its authors are resolved: the count, not the resolved list, is
        # what the author-count filters read.
        count = size if size <= len(PEOPLE) else size
        year = rng.choice([None, 1998, 2004, 2010, 2015, 2020, 2024])
        kind = rng.choices(["article", "conference paper", "thesis", "proceedings"],
                           weights=[70, 15, 8, 7])[0]
        title = "Erratum: something" if rng.random() < 0.08 else f"Work {work_id}"
        works.append({
            "id": work_id, "title": title, "year": year,
            "date": None if year is None else f"{year}-01-01", "date_source": "preprint",
            "author_count": count, "authors": authors, "unresolved_count": max(0, count - len(authors)),
            "document_types": [kind], "doi": [], "arxiv": [],
            "source_url": f"https://inspirehep.net/literature/{work_id}",
            "source_ids": [], "retrieved_at": "2026-09-16T00:00:00Z"})
    phd = [{"adviser": PEOPLE[index], "student": PEOPLE[index + 1], "degree": "PhD",
            "year": 2000 + index, "source_url": "https://inspirehep.net/literature/doctoral",
            "source_record": f"rec-{index}", "uncertainty": None,
            "retrieved_at": "2026-09-16T00:00:00Z"}
           for index in range(0, 10, 2)]
    return {"version": "differential-v1", "created_at": "2026-09-16T00:00:00Z",
            "coverage": {"label": "fixture", "complete": True},
            "people": [_person(item) for item in PEOPLE], "works": works, "phd": phd}


def _ingestible(work: dict) -> bool:
    """Exactly the importer's retention rule, applied once at load time."""
    if str(work["title"]).lower().startswith(("erratum", "errata", "corrigendum")):
        return False
    types = {str(item).strip().lower() for item in work["document_types"]}
    if not types & ALLOWED or types & EXCLUDED:
        return False
    return work["author_count"] >= 2 and len(set(work["authors"])) >= 2


@pytest.fixture(scope="module")
def pair():
    corpus = _corpus()
    connection = psycopg.connect(URL, autocommit=True)
    connection.execute("SET statement_timeout='30s'")
    connection.execute("DROP TABLE IF EXISTS graph_genealogy_edge")
    connection.execute("DROP TABLE IF EXISTS graph_genealogy_overlay")
    connection.execute("DROP TABLE IF EXISTS inspire_compact_membership")
    connection.execute("DROP TABLE IF EXISTS inspire_compact_work")
    connection.execute("DROP TABLE IF EXISTS inspire_compact_shard")
    connection.execute("DROP TABLE IF EXISTS inspire_compact_import")
    connection.execute(SCHEMA)
    from pathlib import Path

    import hepgraph

    connection.execute((Path(hepgraph.__path__[0]) / "sql" / "genealogy_overlay.sql").read_text())
    connection.execute(
        "INSERT INTO inspire_compact_import(import_id,source_cutoff,low_recid,high_recid,status) "
        "VALUES (%s, now(), 5000, 5200, 'FETCHING')", (IMPORT_ID,))
    for work in corpus["works"]:
        if not _ingestible(work):
            continue
        members = sorted({int(author) for author in work["authors"]})
        connection.execute(
            "INSERT INTO inspire_compact_work(import_id,work_id,year,author_count,member_count,"
            "retrieved_at) VALUES (%s,%s,%s,%s,%s,now())",
            (IMPORT_ID, int(work["id"]), work["year"], work["author_count"], len(members)))
        for author_id in members:
            connection.execute(
                "INSERT INTO inspire_compact_membership(import_id,work_id,author_id) "
                "VALUES (%s,%s,%s)", (IMPORT_ID, int(work["id"]), author_id))
    connection.execute(
        "INSERT INTO graph_genealogy_overlay(overlay_id,source_description,source_cutoff,"
        "certified_complete) VALUES (%s,'differential','2026-01-01T00:00:00+00:00',TRUE)",
        (OVERLAY_ID,))
    for record in corpus["phd"]:
        connection.execute(
            "INSERT INTO graph_genealogy_edge(overlay_id,adviser_id,student_id,source_record,"
            "degree,year) VALUES (%s,%s,%s,%s,%s,%s)",
            (OVERLAY_ID, int(record["adviser"]), int(record["student"]),
             record["source_record"], record["degree"], record["year"]))
    provider = NeonCompactGraphProvider(
        connection,
        coverage=CoverageClaim(import_id=IMPORT_ID, certified_complete=True, reason=""),
        genealogy_overlay=GenealogyOverlay(OVERLAY_ID, certified_complete=True))
    yield corpus, provider
    connection.close()


MATRIX = [
    Filters(max_authors=10, min_shared=1, genealogy=False),
    Filters(max_authors=10, min_shared=2, genealogy=False),
    Filters(max_authors=10, min_shared=3, genealogy=False),
    Filters(max_authors=None, min_authors=11, min_shared=1, genealogy=False),
    Filters(max_authors=None, min_shared=1, genealogy=False),
    Filters(max_authors=None, min_shared=2, genealogy=False),
    Filters(max_authors=10, min_shared=1, year_start=2010, genealogy=False),
    Filters(max_authors=10, min_shared=1, year_end=2009, genealogy=False),
    Filters(max_authors=10, min_shared=1, year_start=2004, year_end=2015, genealogy=False),
    Filters(max_authors=None, min_shared=1, year_start=2015, year_end=2015, genealogy=False),
    Filters(max_authors=10, min_shared=1, genealogy=True),
    Filters(max_authors=None, min_shared=1, genealogy=True),
    Filters(max_authors=10, min_shared=2, year_start=2000, genealogy=True),
]


@pytest.mark.parametrize("filters", MATRIX, ids=lambda item: (
    f"max{item.max_authors}-min{item.min_authors}-shared{item.min_shared}"
    f"-y{item.year_start}_{item.year_end}-g{int(item.genealogy)}"))
def test_neighbors_match_the_in_memory_graph(pair, filters):
    corpus, provider = pair
    graph = Graph(corpus, filters)
    for person_id in PEOPLE:
        expected = set(graph._neighbors(person_id))
        found = provider.get_neighbors(person_id, filters)
        assert set(found.members) == expected, (
            f"{person_id} disagrees under {filters.to_dict()}: "
            f"only in Graph {expected - set(found.members)}, "
            f"only in provider {set(found.members) - expected}")


@pytest.mark.parametrize("filters", MATRIX[:10], ids=lambda item: (
    f"max{item.max_authors}-shared{item.min_shared}-y{item.year_start}_{item.year_end}"))
def test_edge_evidence_matches_the_in_memory_graph(pair, filters):
    corpus, provider = pair
    graph = Graph(corpus, filters)
    for index, source in enumerate(PEOPLE):
        for target in PEOPLE[index + 1:]:
            edge = graph._edge(source, target)
            expected = ([f"work:{work['id']}" for work in edge["works"]] if edge else [])
            found = [ref for ref in provider.get_edge_evidence_refs(source, target, filters)
                     if ref.startswith("work:")]
            assert found == expected, f"{source}-{target} under {filters.to_dict()}"


def test_batch_agrees_with_single_lookups_across_the_matrix(pair):
    _, provider = pair
    for filters in MATRIX:
        batch = provider.get_neighbors_batch(tuple(PEOPLE), filters)
        for person_id in PEOPLE:
            single = provider.get_neighbors(person_id, filters)
            assert batch[person_id].members == single.members
            assert batch[person_id].status == single.status
