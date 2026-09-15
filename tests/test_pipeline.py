import json
import sqlite3

from hepgraph.pipeline import (
    InspireClient,
    _documented_date,
    build_snapshot,
    ingest_manifest,
    open_db,
    store_record,
)


def literature(recid, authors, **extra):
    metadata = {
        "control_number": recid,
        "titles": [{"title": f"Work {recid}"}],
        "document_type": ["article"],
        "authors": authors,
        "author_count": 0,
        "dois": [],
        "arxiv_eprints": [],
    }
    metadata.update(extra)
    return {"id": str(recid), "metadata": metadata}


def author(recid, **extra):
    metadata = {"control_number": recid, "name": {"value": f"Person {recid}"}, "ids": [], "positions": [], "advisors": []}
    metadata.update(extra)
    return {"id": str(recid), "metadata": metadata}


def ref(recid):
    return {"$ref": f"https://inspirehep.net/api/authors/{recid}"}


def test_roles_count_unresolved_and_profile_enrichment(tmp_path):
    db = open_db(tmp_path / "graph.sqlite")
    store_record(db, "authors", author(1, name={"value": "A", "preferred_name": "Ada", "name_variants": ["A. A"]}, ids=[{"schema": "ORCID", "value": "0000"}], positions=[{"institution": "CERN", "current": True}]))
    store_record(db, "literature", literature(10, [
        {"full_name": "Ada", "record": ref(1), "inspire_roles": ["author"], "affiliations": [{"value": "CERN"}]},
        {"full_name": "Supervisor", "record": ref(2), "inspire_roles": ["supervisor"]},
        {"full_name": "Unknown", "inspire_roles": []},
        {"full_name": "Editor", "record": ref(3), "inspire_roles": ["editor"]},
    ], author_count=6, earliest_date="2020-02-03", preprint_date="2020-02-03"))
    snapshot = build_snapshot(db, {"label": "pilot"})
    work = snapshot["works"][0]
    assert work["authors"] == ["1"]
    assert work["unresolved_count"] == 1
    assert work["author_count"] == 6  # never recomputed from resolved profiles
    assert work["year"] == 2020 and work["date_source"] == "earliest_date"
    person = next(item for item in snapshot["people"] if item["id"] == "1")
    assert person["name"] == "Ada" and person["orcid"] == "0000" and person["affiliations"] == ["CERN"]


def test_thesis_and_profile_advisers_keep_only_phd_and_audit(tmp_path):
    db = open_db(tmp_path / "graph.sqlite")
    store_record(db, "authors", author(7, advisors=[
        {"degree_type": "PhD", "record": ref(8), "name": "Advisor", "curated_relation": False},
        {"degree_type": "master", "record": ref(9), "name": "Nope"},
        {"degree_type": "PhD", "record": ref(10), "hidden": True},
    ]))
    store_record(db, "literature", literature(20, [
        {"record": ref(7), "inspire_roles": ["author"]},
        {"record": ref(8), "inspire_roles": ["supervisor"]},
    ], document_type=["thesis"], thesis_info={"degree_type": "PhD", "date": "2019"}, earliest_date="2019"))
    snapshot = build_snapshot(db, {"label": "pilot"})
    pairs = {(edge["adviser"], edge["student"], edge["source_record"]): edge for edge in snapshot["phd"]}
    assert ("8", "7", "20") in pairs
    assert pairs[("8", "7", "7")]["uncertainty"] == "curated_relation_not_true"
    assert db.execute("SELECT COUNT(*) FROM doctoral_audit").fetchone()[0] == 2


def test_identifier_versions_merge_only_with_consistent_membership_and_keep_provenance(tmp_path):
    db = open_db(tmp_path / "graph.sqlite")
    common = [{"record": ref(1), "inspire_roles": ["author"]}]
    store_record(db, "literature", literature(30, common, dois=[{"value": "10.1/X"}], arxiv_eprints=[{"value": "arXiv:1234.5678v1"}], author_count=4))
    store_record(db, "literature", literature(31, common, dois=[{"value": "https://doi.org/10.1/x"}], arxiv_eprints=[{"value": "1234.5678v2"}], author_count=1))
    snapshot = build_snapshot(db, {"label": "pilot"})
    assert len(snapshot["works"]) == 1
    assert snapshot["works"][0]["source_ids"] == ["30", "31"]
    assert snapshot["works"][0]["author_count"] == 4
    store_record(db, "literature", literature(32, [{"record": ref(2), "inspire_roles": ["author"]}], dois=[{"value": "10.1/x"}]))
    snapshot = build_snapshot(db, {"label": "pilot"})
    assert len(snapshot["works"]) == 1
    assert snapshot["works"][0]["authors"] == ["1"]  # never union conflicting membership
    assert db.execute("SELECT COUNT(*) FROM dedup_conflicts").fetchone()[0] >= 1


def test_an_unresolved_version_cannot_bridge_conflicting_identifier_groups(tmp_path):
    db = open_db(tmp_path / "graph.sqlite")
    store_record(db, "literature", literature(60, [{"record": ref(1), "inspire_roles": ["author"]}], dois=[{"value": "10.bridge/a"}]))
    store_record(db, "literature", literature(61, [], dois=[{"value": "10.bridge/a"}], arxiv_eprints=[{"value": "1111.2222v1"}]))
    store_record(db, "literature", literature(62, [{"record": ref(2), "inspire_roles": ["author"]}], arxiv_eprints=[{"value": "1111.2222v2"}]))
    works = build_snapshot(db, {"label": "pilot"})["works"]
    # It is permissible to retain extra uncertain versions; it is not
    # permissible for their shared identifier to create a 1--2 work membership.
    assert all(not ({"1", "2"} <= set(work["authors"])) for work in works)


def test_replacements_tombstones_and_atomic_resume(tmp_path):
    db = open_db(tmp_path / "graph.sqlite")
    store_record(db, "literature", literature(40, [], deleted=True, new_record={"$ref": "https://inspirehep.net/api/literature/41"}))
    store_record(db, "literature", literature(41, []))
    store_record(db, "literature", literature(42, [], deleted=True))
    assert [work["id"] for work in build_snapshot(db, {"label": "pilot"})["works"]] == ["41"]

    class FakeClient(InspireClient):
        def __init__(self): self.calls = 0
        def fetch(self, collection, query, page, size, sort=None):
            self.calls += 1
            if self.calls == 1:
                return {"hits": {"hits": [literature(50, [])]}}
            raise AssertionError("completed checkpoint should skip fetching")

    client = FakeClient()
    manifest = {"label": "pilot", "literature": [{"query": "x", "limit": 2}], "authors": []}
    result = ingest_manifest(db, manifest, cache=tmp_path / "cache", client=client)
    assert result["records"] == 1 and client.calls == 1
    assert ingest_manifest(db, manifest, cache=tmp_path / "cache", client=client)["queries"] == 0
    cached = next((tmp_path / "cache").glob("*.json"))
    cached_payload = json.loads(cached.read_text())
    assert "abstracts" not in json.dumps(cached_payload) and "emails" not in json.dumps(cached_payload)


def test_manifest_refresh_retries_failed_checkpoint(tmp_path):
    db = open_db(tmp_path / "graph.sqlite")
    class Failing(InspireClient):
        def fetch(self, *args): raise ValueError("offline")
    manifest = {"label": "pilot", "literature": [{"query": "x", "limit": 1}], "authors": []}
    result = ingest_manifest(db, manifest, cache=tmp_path / "cache", client=Failing())
    assert result["failures"]
    class Good(InspireClient):
        def fetch(self, *args): return {"hits": {"hits": []}}
    assert ingest_manifest(db, manifest, cache=tmp_path / "cache", client=Good(), refresh=True)["failures"] == []


def test_fixed_pages_cache_resume_date_fallback_coverage_and_stable_version(tmp_path):
    db = open_db(tmp_path / "graph.sqlite")
    calls = []
    class Pages(InspireClient):
        def fetch(self, collection, query, page, size, sort=None):
            calls.append((page, size))
            start = 0 if page == 1 else 1000
            return {"hits": {"total": 2200, "hits": [literature(start + i + 1, [], preprint_date="2021-03-02") for i in range(size)]}}
    manifest = {"label": "pilot", "literature": [{"query": "x", "limit": 1500}], "authors": []}
    result = ingest_manifest(db, manifest, cache=tmp_path / "cache", client=Pages())
    assert result["records"] == 1500 and calls == [(1, 1000), (2, 1000)]
    snapshot = build_snapshot(db)
    assert snapshot["coverage"]["queries"][0] | {"upstream_total": 2200, "received_count": 1500, "limited": True, "truncated": True}
    assert snapshot["works"][0]["date"] == "2021-03-02" and snapshot["works"][0]["date_source"] == "preprint_date"
    assert snapshot["version"] == build_snapshot(db)["version"]

    # Simulate interruption after a cache write but before checkpoint commit.
    db.execute("UPDATE query_checkpoints SET complete=0,next_page=1,received_count=0")
    class Offline(InspireClient):
        def fetch(self, *args): raise AssertionError("cache should satisfy resumed page")
    resumed = ingest_manifest(db, manifest, cache=tmp_path / "cache", client=Offline())
    assert resumed["records"] == 1500


def test_source_updated_time_and_ambiguous_thesis_are_recorded(tmp_path):
    db = open_db(tmp_path / "graph.sqlite")
    record = literature(90, [{"record": ref(1), "inspire_roles": ["author"]}, {"record": ref(2), "inspire_roles": ["author"]}, {"record": ref(3), "inspire_roles": ["supervisor"]}],
                        document_type=["thesis"], thesis_info={"degree_type": "PhD"})
    record["updated"] = "2026-01-01T12:00:00Z"
    store_record(db, "literature", record)
    assert db.execute("SELECT updated_at FROM source_records WHERE recid='90'").fetchone()[0] == "2026-01-01T12:00:00Z"
    assert build_snapshot(db, {"label": "pilot"})["phd"] == []
    assert db.execute("SELECT reason FROM doctoral_audit WHERE source_record='90'").fetchone()[0] == "ambiguous_thesis_students"


def test_documented_date_keeps_same_year_precision_but_honors_a_truly_earlier_year():
    # Regression for real pilot record 10245: lexical sorting chose the bare
    # publication year 1981 over the documented earliest/preprint month 1981-01.
    same_year = {
        "earliest_date": "1981-01", "preprint_date": "1981-01", "imprints": [],
        "publication_years": ["1981"], "thesis_info": {"date": None},
    }
    assert _documented_date([same_year]) == ("1981-01", "earliest_date")

    # A bare publication year is still meaningful when it establishes an
    # earlier calendar year than all more-precise documented candidates.
    earlier_publication = {**same_year, "earliest_date": "1981-03-04", "preprint_date": "1981-03-04", "publication_years": ["1980"]}
    assert _documented_date([earlier_publication]) == ("1980", "publication_info.year")

    # A later, more precise journal issue cannot replace INSPIRE's explicitly
    # earliest month. This is the real 1124337 July-vs-September failure mode.
    precise = {"earliest_date": "2020-02", "preprint_date": None, "imprints": ["2020-02-03", "2020-99"], "publication_years": ["2020"], "thesis_info": {"date": None}}
    assert _documented_date([precise]) == ("2020-02", "earliest_date")
    july_vs_september = {"earliest_date": "2012-07", "preprint_date": "2012-07", "imprints": ["2012-09-17"], "publication_years": ["2012"], "thesis_info": {"date": None}}
    assert _documented_date([july_vs_september]) == ("2012-07", "earliest_date")

    # Without earliest_date, a full other documented date retains its precision
    # instead of being truncated to the same-year publication field.
    fallback = {"earliest_date": None, "preprint_date": None, "imprints": ["2020-02-03"], "publication_years": ["2020"], "thesis_info": {"date": None}}
    assert _documented_date([fallback]) == ("2020-02-03", "imprints.date")
