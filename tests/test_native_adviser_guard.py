"""Regression for native profile adviser names that contradict their linked IDs."""
from __future__ import annotations

import copy
import json
import sqlite3

from hepgraph.identity_guard import apply_identity_guard


YANG = "982820"
FERMI = "1020970"
TELLER = "1019685"


def _profile(name: str, advisers: list[dict] | None = None) -> dict:
    return {"name": {"value": name, "preferred_name": name, "name_variants": []}, "advisors": advisers or []}


def _connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE source_records (recid TEXT, collection TEXT, payload TEXT, deleted INTEGER)")
    connection.execute(
        "CREATE TABLE authorship_occurrences (record_id TEXT, position INTEGER, person_id TEXT, full_name TEXT, affiliations TEXT, roles TEXT)"
    )
    entries = {
        YANG: _profile("Yang, Chen Ning", [
            {"degree_type": "PhD", "record": FERMI, "name": "Teller, Edward", "hidden": False},
            {"degree_type": "PhD", "record": TELLER, "name": "Fermi, Enrico", "hidden": False},
        ]),
        FERMI: _profile("Fermi, Enrico"),
        TELLER: _profile("Teller, Edward"),
    }
    for recid, payload in entries.items():
        connection.execute("INSERT INTO source_records VALUES(?,?,?,0)", (recid, "authors", json.dumps(payload)))
    return connection


def _snapshot() -> dict:
    people = [
        {"id": person_id, "name": name, "aliases": [], "profile_status": "profile",
         "source_url": f"https://inspirehep.net/authors/{person_id}"}
        for person_id, name in ((YANG, "Yang, Chen Ning"), (FERMI, "Fermi, Enrico"), (TELLER, "Teller, Edward"))
    ]
    return {
        "version": "sha256:before", "created_at": "2026-09-15T00:00:00Z", "coverage": {"complete": False},
        "people": people, "works": [],
        "phd": [
            {"adviser": FERMI, "student": YANG, "degree": "PhD", "source_record": YANG,
             "source_url": f"https://inspirehep.net/authors/{YANG}"},
            {"adviser": TELLER, "student": YANG, "degree": "PhD", "source_record": YANG,
             "source_url": f"https://inspirehep.net/authors/{YANG}"},
        ],
    }


def test_native_adviser_name_id_collision_is_withheld_without_repairing_ids() -> None:
    source = _snapshot()
    original = copy.deepcopy(source)
    connection = _connection()

    guarded = apply_identity_guard(source, connection)

    assert source == original
    assert guarded["phd"] == []
    assert guarded["coverage"]["identity_phd_conflicts"] == [
        {"student": YANG, "adviser": TELLER, "source_record": YANG,
         "source_url": f"https://inspirehep.net/authors/{YANG}",
         "source_names": ["Fermi, Enrico"], "profile_names": ["Teller, Edward"],
         "reason": "native_adviser_name_conflicts_with_referenced_public_profile"},
        {"student": YANG, "adviser": FERMI, "source_record": YANG,
         "source_url": f"https://inspirehep.net/authors/{YANG}",
         "source_names": ["Teller, Edward"], "profile_names": ["Fermi, Enrico"],
         "reason": "native_adviser_name_conflicts_with_referenced_public_profile"},
    ]
    assert apply_identity_guard(guarded, connection) == guarded
