"""Frozen real INSPIRE errors, independently identified in September 2026."""
import copy
import json
from pathlib import Path

import pytest

from hepgraph.identity_guard import apply_identity_guard
from hepgraph.pipeline import build_snapshot, open_db, store_record
from hepgraph.ondemand import OnDemand


FIXTURE = Path(__file__).parent / "fixtures" / "identity_collisions.json"


@pytest.mark.parametrize("work_id", ["2150122", "2627214", "2623742", "2606257", "1665003"])
def test_each_real_bergmann_misattribution_is_withheld_without_changing_raw_count(work_id):
    fixture = json.loads(FIXTURE.read_text())
    raw = next(w for w in fixture["bergmann_works"] if str(w["id"]) == work_id)
    db = open_db(":memory:")
    store_record(db, "authors", fixture["bergmann_profile"])
    store_record(db, "literature", raw)
    before = build_snapshot(db, {"label": "Real identity regression"})
    assert "1016635" in before["works"][0]["authors"]
    result = apply_identity_guard(before, db)
    work = result["works"][0]
    assert "1016635" not in work["authors"]
    assert work["author_count"] == raw["metadata"]["author_count"]
    assert work["unresolved_count"] >= 1
    assert len(json.loads(db.execute("SELECT payload FROM source_records WHERE collection='literature'").fetchone()[0])["authors"]) == len(raw["metadata"]["authors"])
    audit_key = "identity_full_name_conflicts" if work_id in {"2606257", "1665003"} else "identity_lifetime_review"
    assert any(row["work_id"] == work_id and row["person"] == "1016635" for row in result["coverage"][audit_key])
    assert apply_identity_guard(result, db) == result
    db.close()


def _phd_fixture(advisers):
    db = open_db(":memory:")
    for pid, name in [("982820", "Yang, Chen-Ning"), ("1020970", "Fermi, Enrico"), ("1019685", "Teller, Edward")]:
        store_record(db, "authors", {"id": pid, "metadata": {"control_number": int(pid),
                     "name": {"value": name}, "advisors": advisers if pid == "982820" else []}})
    return db, build_snapshot(db, {"label": "Native adviser identity regression"})


def test_real_yang_fermi_teller_transposed_references_are_not_swapped_or_used():
    fixture = json.loads(FIXTURE.read_text())
    advisers = fixture["yang_advisers"]
    db, before = _phd_fixture(advisers)
    assert len(before["phd"]) == 2
    after = apply_identity_guard(before, db)
    assert after["phd"] == []
    assert len(after["coverage"]["identity_phd_conflicts"]) == 2
    raw = json.loads(db.execute("SELECT payload FROM source_records WHERE collection='authors' AND recid='982820'").fetchone()[0])
    assert raw["advisors"][0]["name"] == "Teller, Edward"
    assert raw["advisors"][0]["record"] == "1020970"
    assert apply_identity_guard(after, db) == after
    db.close()


@pytest.mark.parametrize("name", ["Teller, Edward", "Teller, E.", None])
def test_matching_or_uncertain_native_adviser_name_is_retained(name):
    advisers = [{"degree_type": "phd", "record": {"$ref": "https://inspirehep.net/api/authors/1019685"}, "name": name}]
    db, before = _phd_fixture(advisers)
    after = apply_identity_guard(before, db)
    assert after["phd"] == before["phd"]
    assert not after["coverage"].get("identity_phd_conflicts")
    db.close()


def test_lookup_uses_documented_aliases_without_becoming_raw_query_language():
    query = OnDemand._author_search_query("Gerard ’t Hooft")
    assert '(name.value:"Gerard" OR name.name_variants:"Gerard" OR name.preferred_name:"Gerard")' in query
    assert '(name.value:"Hooft" OR name.name_variants:"Hooft" OR name.preferred_name:"Hooft")' in query
    assert query.count(") AND (") == 2
    attack = OnDemand._author_search_query("* OR control_number:1019113")
    assert "control_number:" not in attack and "*" not in attack
    assert 'name.value:"OR"' in attack
    assert OnDemand._author_search_query("1019113") == "control_number:1019113"


def test_composed_and_decomposed_diacritics_have_the_same_lookup_key():
    assert OnDemand._author_search_query("Franc\u0327ois Englert") == OnDemand._author_search_query("François Englert")
