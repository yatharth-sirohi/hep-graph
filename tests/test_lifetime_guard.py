"""Conservative review of late initials-only links to deceased profiles."""
from __future__ import annotations

import json
import sqlite3

import pytest

from hepgraph.identity_guard import apply_identity_guard
from hepgraph.pipeline import _cached_hit, build_snapshot, open_db, sanitize_author, store_record


PERSON = "1016635"
PROFILE_LINK = f"https://inspirehep.net/authors/{PERSON}"


def _connection(death_date: str | None) -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE source_records (recid TEXT, collection TEXT, payload TEXT, deleted INTEGER)")
    connection.execute(
        "CREATE TABLE authorship_occurrences (record_id TEXT, position INTEGER, person_id TEXT, full_name TEXT, affiliations TEXT, roles TEXT)"
    )
    profile = {
        "name": {
            "value": "Bergmann, Peter G.",
            "preferred_name": "Peter G. Bergmann",
            "name_variants": [],
        },
    }
    if death_date is not None:
        profile["death_date"] = death_date
    connection.execute("INSERT INTO source_records VALUES(?,?,?,0)", (PERSON, "authors", json.dumps(profile)))
    return connection


def _snapshot(work_id: str, year: int, raw_name: str) -> dict:
    return {
        "version": "sha256:before",
        "created_at": "2026-09-15T00:00:00Z",
        "coverage": {"complete": False},
        "people": [{
            "id": PERSON,
            "name": "Peter G. Bergmann",
            "aliases": ["Bergmann, Peter G."],
            "profile_status": "profile",
            "source_url": PROFILE_LINK,
        }],
        "works": [{
            "id": work_id,
            "source_ids": [work_id],
            "year": year,
            "author_count": 2,
            "authors": [PERSON, "coauthor"],
            "unresolved_count": 0,
        }],
        "phd": [],
        "raw_name": raw_name,
    }


def _guarded(work_id: str, year: int, raw_name: str, death_date: str | None) -> tuple[dict, dict]:
    source = _snapshot(work_id, year, raw_name)
    connection = _connection(death_date)
    connection.execute(
        "INSERT INTO authorship_occurrences VALUES(?,?,?,?,?,?)",
        (work_id, 0, PERSON, raw_name, "[]", "[]"),
    )
    return source, apply_identity_guard(source, connection)


def test_late_matching_initial_only_byline_is_quarantined_with_a_lifetime_review() -> None:
    source, guarded = _guarded("modern", 2022, "P. Bergmann", "2002-10")

    assert source["works"][0]["authors"] == [PERSON, "coauthor"]  # caller is never mutated
    assert guarded["works"][0]["authors"] == ["coauthor"]
    assert guarded["works"][0]["author_count"] == 2
    assert guarded["works"][0]["unresolved_count"] == 1
    assert guarded["coverage"]["identity_lifetime_review"] == [{
        "work_id": "modern",
        "person": PERSON,
        "work_year": 2022,
        "death_date": "2002-10",
        "source_profile_link": PROFILE_LINK,
        "source_id": "modern",
        "source_name": "P. Bergmann",
        "reason": "initial_only_authorship_more_than_two_years_after_profile_death_year",
    }]
    connection = _connection("2002-10")
    connection.execute(
        "INSERT INTO authorship_occurrences VALUES(?,?,?,?,?,?)",
        ("modern", 0, PERSON, "P. Bergmann", "[]", "[]"),
    )
    assert apply_identity_guard(guarded, connection) == guarded


@pytest.mark.parametrize(
    ("year", "raw_name", "death_date"),
    [
        (1980, "P. Bergmann", "2002-10"),  # documented before death
        (2004, "P. Bergmann", "2002-10"),  # two-year grace period
        (2022, "Peter G. Bergmann", "2002-10"),  # fully stated byline
        (2022, "P. Bergmann", None),
        (2022, "P. Bergmann", "not-a-date"),
        (2022, "P. Bergmann", "2002-02-31"),
    ],
)
def test_only_late_initial_only_links_with_a_valid_profile_death_date_are_reviewed(
    year: int, raw_name: str, death_date: str | None,
) -> None:
    _, guarded = _guarded(f"retained-{year}-{raw_name[:1]}-{death_date}", year, raw_name, death_date)

    assert guarded["works"][0]["authors"] == [PERSON, "coauthor"]
    assert guarded["works"][0]["author_count"] == 2
    assert guarded["works"][0]["unresolved_count"] == 0
    assert "identity_lifetime_review" not in guarded["coverage"]


def test_death_date_is_allowlisted_cached_and_exposed_only_when_a_profile_supplies_it(tmp_path) -> None:
    def author(recid: str, death_date: str | None = None) -> dict:
        metadata = {
            "control_number": recid,
            "name": {"value": "Bergmann, Peter G.", "preferred_name": "Peter G. Bergmann", "name_variants": []},
            "ids": [], "positions": [], "advisors": [],
        }
        if death_date is not None:
            metadata["death_date"] = death_date
        return {"id": recid, "metadata": metadata}

    recid, with_death = sanitize_author(author(PERSON, "2002-10"))
    _, without_death = sanitize_author(author("999"))
    assert with_death["death_date"] == "2002-10"
    assert "death_date" not in without_death
    assert _cached_hit("authors", recid, with_death)["metadata"]["death_date"] == "2002-10"
    assert "death_date" not in _cached_hit("authors", "999", without_death)["metadata"]

    db = open_db(tmp_path / "lifetime.sqlite")
    store_record(db, "authors", author(PERSON, "2002-10"))
    store_record(db, "authors", author("999"))
    people = {person["id"]: person for person in build_snapshot(db, {"label": "lifetime"})["people"]}
    assert people[PERSON]["death_date"] == "2002-10"
    assert "death_date" not in people["999"]
