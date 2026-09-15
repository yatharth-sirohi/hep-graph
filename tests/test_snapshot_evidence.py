"""Independent whole-snapshot provenance checks for the local pilot dataset.

These tests read the published JSON and an independently frozen source-table fixture.
They do not import ingestion or normalization helpers, so they catch a divergence
between the source evidence and the delivered graph snapshot.
"""

from __future__ import annotations

import json
import gzip
import re
import sqlite3
from pathlib import Path
from typing import Any

import pytest


PROJECT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = PROJECT / "data" / "current.json"
EVIDENCE_PATH = PROJECT / "tests" / "fixtures" / "saved-provenance.json.gz"


@pytest.fixture(scope="module")
def evidence() -> tuple[dict[str, Any], sqlite3.Connection]:
    snapshot = json.loads(SNAPSHOT_PATH.read_text())
    # A compact fixed public fixture keeps clean clones independent of a local
    # runtime database. No production ingestion/normalization function is used.
    fixture = json.loads(gzip.decompress(EVIDENCE_PATH.read_bytes()))
    assert fixture["snapshot_version"] == snapshot["version"]
    database = sqlite3.connect(":memory:")
    allowed = {"source_records", "authorship_occurrences", "works", "people", "replacements"}
    assert set(fixture["tables"]) == allowed
    for table, data in fixture["tables"].items():
        database.execute(f"CREATE TABLE {table} ({data['schema']})")
        if data["rows"]:
            slots = ",".join("?" for _ in data["rows"][0])
            database.executemany(f"INSERT INTO {table} VALUES ({slots})", data["rows"])
    yield snapshot, database
    database.close()


def _loads(value: str) -> Any:
    return json.loads(value)


def _is_editor(roles: list[Any]) -> bool:
    return any(str(role).strip().lower() == "editor" for role in roles)


_DATE = re.compile(r"^(?P<year>\d{4})(?:-(?P<month>\d{2})(?:-(?P<day>\d{2}))?)?$")


def _authoritative_earliest_date(raw: dict[str, Any]) -> str:
    """Validate the sanctioned INSPIRE earliest-record date without re-ranking it.

    ``earliest_date`` already encodes INSPIRE's chronological judgment. A later,
    more precise imprint must not displace it merely because it has a day value.
    """
    value = raw.get("earliest_date")
    assert isinstance(value, str) and _DATE.fullmatch(value)
    return value


def _source_works(database: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    return {
        str(recid): _loads(payload)
        for recid, payload in database.execute(
            "select recid, payload from source_records where collection=? and deleted=0", ("literature",)
        )
    }


def _occurrences(database: sqlite3.Connection, work_id: str) -> list[tuple[int, str | None, str, list[Any], list[Any]]]:
    return [
        (position, person_id, full_name, _loads(affiliations), _loads(roles))
        for position, person_id, full_name, affiliations, roles in database.execute(
            """select position, person_id, full_name, affiliations, roles
               from authorship_occurrences where record_id=? order by position""",
            (work_id,),
        )
    ]


def test_published_works_are_a_complete_non_deleted_stable_id_projection(evidence: tuple[dict[str, Any], sqlite3.Connection]) -> None:
    snapshot, database = evidence
    source_works = _source_works(database)
    published = {str(work["id"]): work for work in snapshot["works"]}
    normalized = {
        str(work_id): _loads(payload)
        for work_id, payload in database.execute("select work_id, payload from works")
    }
    normalized_people = {
        str(person_id): _loads(payload)
        for person_id, payload in database.execute("select person_id, payload from people")
    }
    published_people = {str(person["id"]): person for person in snapshot["people"]}

    assert len(published) == len(snapshot["works"])
    assert set(published) == set(normalized) == set(source_works)
    assert published_people == normalized_people

    # A source-record replacement must retire its old stable ID.  It is not a
    # name-based work merge, and every delivered work retains one source ID.
    retired_ids = {
        str(old_id)
        for collection, old_id in database.execute("select collection, old_id from replacements")
        if collection == "literature"
    }
    assert not retired_ids.intersection(published)
    for work_id, work in published.items():
        assert work == normalized[work_id]
        assert work["source_ids"] == [work_id]
        assert source_works[work_id]["deleted"] is False
        assert str(source_works[work_id]["control_number"]) == work_id


def test_every_published_work_preserves_full_counts_roles_and_stable_author_ids(evidence: tuple[dict[str, Any], sqlite3.Connection]) -> None:
    snapshot, database = evidence
    source_works = _source_works(database)
    published = {str(work["id"]): work for work in snapshot["works"]}
    people = {str(person["id"]) for person in snapshot["people"]}
    default_eligible: set[str] = set()

    for work_id, raw in source_works.items():
        work = published[work_id]
        raw_authors = raw["authors"]
        occurrences = _occurrences(database, work_id)
        assert [row[0] for row in occurrences] == list(range(len(raw_authors)))
        assert len(raw_authors) == raw["author_count"] == work["author_count"]

        expected_authors: list[str] = []
        unresolved = 0
        for raw_author, (_, person_id, full_name, affiliations, roles) in zip(raw_authors, occurrences):
            raw_roles = raw_author.get("inspire_roles", [])
            assert person_id == raw_author.get("record")
            assert full_name == raw_author.get("full_name")
            assert affiliations == raw_author.get("affiliations", [])
            assert roles == raw_roles
            if _is_editor(raw_roles):
                continue
            if person_id is None:
                unresolved += 1
            elif person_id not in expected_authors:
                # Retain the first source occurrence of an exact stable profile
                # ID. Different names attached to one source ID do not create an
                # inferred identity merge.
                expected_authors.append(person_id)

        assert work["authors"] == expected_authors
        assert work["unresolved_count"] == unresolved
        assert set(work["authors"]).issubset(people)

        document_types = {str(value).strip().lower() for value in work["document_types"]}
        if (
            document_types.intersection({"article", "conference paper"})
            and not document_types.intersection({"thesis", "book", "book chapter", "proceedings"})
            and work["author_count"] <= 10
        ):
            default_eligible.add(work_id)

    # This independently reconstructs the default paper population used by the
    # demo graph, including the full original author-count cap.
    assert len(default_eligible) == 1_153


def test_dates_preserve_authoritative_inspire_earliest_date(evidence: tuple[dict[str, Any], sqlite3.Connection]) -> None:
    snapshot, database = evidence
    source_works = _source_works(database)

    for work in snapshot["works"]:
        raw = source_works[str(work["id"])]
        expected_date = _authoritative_earliest_date(raw)
        assert work["date"] == expected_date
        assert work["date_source"] == "earliest_date"
        assert work["year"] == int(expected_date[:4])


def test_atlas_1124337_keeps_earlier_july_record_date_over_september_imprint(evidence: tuple[dict[str, Any], sqlite3.Connection]) -> None:
    snapshot, database = evidence
    source_works = _source_works(database)
    # ATLAS 1124337 establishes that a later, more precise September imprint
    # cannot replace INSPIRE's earlier July record date.
    atlas = source_works["1124337"]
    assert atlas["earliest_date"] == "2012-07"
    assert "2012-09-17" in atlas["imprints"]
    published_atlas = next(work for work in snapshot["works"] if work["id"] == "1124337")
    assert published_atlas["date"] == "2012-07"
    assert published_atlas["date_source"] == "earliest_date"


def test_every_phd_edge_has_an_explicit_profile_phd_record_with_stable_ids(evidence: tuple[dict[str, Any], sqlite3.Connection]) -> None:
    snapshot, database = evidence
    people = {str(person["id"]) for person in snapshot["people"]}
    seen: set[tuple[str, str, str]] = set()

    for relation in snapshot["phd"]:
        assert relation["degree"] == "PhD"
        key = (str(relation["adviser"]), str(relation["student"]), str(relation["source_record"]))
        assert key not in seen
        seen.add(key)
        assert relation["adviser"] in people and relation["student"] in people
        assert relation["student"] == relation["source_record"]
        assert relation["source_url"] == f"https://inspirehep.net/authors/{relation['source_record']}"
        row = database.execute(
            "select payload, deleted from source_records where collection=? and recid=?",
            ("authors", relation["source_record"]),
        ).fetchone()
        assert row is not None and row[1] == 0
        profile = _loads(row[0])
        assert str(profile["control_number"]) == str(relation["student"])
        matches = [advisor for advisor in profile.get("advisors", []) if str(advisor.get("record")) == str(relation["adviser"])]
        assert matches
        assert any(str(advisor.get("degree_type", "")).lower() == "phd" for advisor in matches)
        # IDs come directly from the profile relation; names are evidence only.
        assert all(advisor.get("record") is not None for advisor in matches)
        assert relation["year"] is None
        if any(advisor.get("curated_relation") is True for advisor in matches if str(advisor.get("degree_type", "")).lower() == "phd"):
            assert relation["uncertainty"] is None
        else:
            assert relation["uncertainty"] == "curated_relation_not_true"

    assert len(snapshot["phd"]) == 43
