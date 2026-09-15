"""Independent fixtures for the conservative normalized-authorship identity guard."""
from __future__ import annotations

import copy
import json
import sqlite3

from hepgraph.identity_guard import (
    apply_identity_guard,
    full_given_name_conflict,
    hard_initial_conflict,
    partial_initial_ambiguity,
)


def _connection(profiles: dict[str, dict], occurrences: list[tuple[str, int, str | None, str, str]]) -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE source_records (recid TEXT, collection TEXT, payload TEXT, deleted INTEGER)")
    connection.execute(
        "CREATE TABLE authorship_occurrences (record_id TEXT, position INTEGER, person_id TEXT, full_name TEXT, affiliations TEXT, roles TEXT)"
    )
    for person_id, name in profiles.items():
        payload = {"name": name}
        connection.execute(
            "INSERT INTO source_records VALUES(?,?,?,0)", (person_id, "authors", json.dumps(payload))
        )
    connection.executemany("INSERT INTO authorship_occurrences VALUES(?,?,?,?,?,?)", occurrences)
    return connection


def _snapshot(people: list[dict], works: list[dict]) -> dict:
    return {
        "version": "sha256:before",
        "created_at": "2026-09-15T00:00:00Z",
        "coverage": {"complete": False},
        "people": people,
        "works": works,
        "phd": [],
    }


def _profile(person_id: str, name: str, aliases: list[str] | None = None, *, public: bool = True) -> dict:
    return {
        "id": person_id,
        "name": name,
        "aliases": aliases or [],
        "profile_status": "profile",
        "source_url": f"https://inspirehep.net/authors/{person_id}" if public else "https://example.test/profile",
    }


def _work(work_id: str, source_ids: list[str], authors: list[str], count: int | None = None) -> dict:
    return {
        "id": work_id,
        "source_ids": source_ids,
        "authors": authors,
        "author_count": len(authors) if count is None else count,
        "unresolved_count": 0,
    }


def test_initial_comparator_requires_all_profile_forms_to_be_explicitly_incompatible() -> None:
    assert hard_initial_conflict("Chiu, C.S.", ["Chiu, Charles B.", "Charles B. Chiu"])
    assert hard_initial_conflict("Kaufman, B.", ["Kaufman, S.B."])
    assert not hard_initial_conflict("Chiu, C.", ["Chiu, Charles B."])
    assert not hard_initial_conflict("Chiu, C.S.", ["Chiu, Charles B.", "Chiu, C.S."])
    assert not hard_initial_conflict("de la Cruz, J.", ["Juan de la Cruz"])  # multipart surname stays uncertain
    assert not hard_initial_conflict("García-López, M.", ["Garcia Lopez, M."])  # compatible diacritic/hyphen form
    assert not hard_initial_conflict("unparseable name", ["Chiu, Charles B."])
    assert not partial_initial_ambiguity("Chiu, Charles", ["Chiu, Charles B."], ["Chiu, C.S."])
    assert partial_initial_ambiguity("Chiu, C.", ["Chiu, Charles B."], ["Chiu, C.S."])


def test_name_parser_preserves_v_initial_and_keeps_diacritic_given_names_whole() -> None:
    # ``V`` is an author initial here, not a generational suffix.  Both the
    # surname-first and display forms must agree before a hard exclusion can be
    # considered, so this must remain resolved.
    assert not hard_initial_conflict(
        "Weisskopf, V.F.", ["Weisskopf, Victor Frederick", "Victor Frederick Weisskopf"]
    )
    # NFKD decomposes the acute marks in Gábor and István.  They are still one
    # token each, so the stated G.I. initials match the full public profile.
    assert not hard_initial_conflict("Nagy, G.I.", ["Nagy, Gábor István"])
    # Genuine terminal suffixes remain ignorable without treating an internal
    # or leading initial as a suffix.
    assert not hard_initial_conflict("Example, John Jr.", ["Example, John"])


def test_full_given_name_conflict_requires_all_profile_forms_to_be_explicitly_incompatible() -> None:
    assert full_given_name_conflict("Born, Micheal", ["Born, Max", "Max Born"])
    # A known full alias, a prefix-compatible form, and a public initials-only
    # alias each leave room for an upstream spelling or attribution issue.
    assert not full_given_name_conflict("Born, Micheal", ["Born, Max", "Born, Micheal"])
    assert not full_given_name_conflict("Born, Micheal", ["Born, Max", "Born, Mich"])
    assert not full_given_name_conflict("Born, Micheal", ["Born, Max", "Born, M."])
    assert not full_given_name_conflict("Jones, Bob", ["Jones, Robert", "Jones, Bob"])
    assert not full_given_name_conflict("Born, M.", ["Born, Max"])


def test_full_given_name_conflict_is_suppressed_with_distinct_audit_reason() -> None:
    person = "1033321"
    profiles = {person: {"value": "Born, Max", "preferred_name": "Max Born", "name_variants": []}}
    source = _snapshot([_profile(person, "Max Born")], [_work("2961613", ["2961613"], [person])])
    guarded = apply_identity_guard(
        source,
        _connection(profiles, [("2961613", 0, person, "Born, Micheal", "[]", "[]")]),
    )

    assert guarded["works"] == [{**source["works"][0], "authors": [], "unresolved_count": 1}]
    assert guarded["coverage"]["identity_conflicts"] == []
    assert guarded["coverage"]["identity_full_name_conflicts"] == [{
        "work_id": "2961613", "source_id": "2961613", "person": person,
        "source_name": "Born, Micheal", "profile_names": ["Max Born", "Born, Max"],
        "reason": "all_public_profile_name_forms_have_incompatible_full_given_names",
    }]


def test_short_all_caps_compact_initials_remain_unresolved_and_retained() -> None:
    person = "shaevitz"
    profiles = {person: {"value": "Shaevitz, Michael H.", "preferred_name": "Michael H. Shaevitz", "name_variants": []}}
    source = _snapshot([_profile(person, "Michael H. Shaevitz")], [_work("1377197", ["1377197"], [person])])
    guarded = apply_identity_guard(
        source,
        _connection(profiles, [("1377197", 0, person, "Shaevitz, MH", "[]", "[]")]),
    )

    assert not hard_initial_conflict("Shaevitz, MH", ["Shaevitz, Michael H."])
    assert not full_given_name_conflict("Shaevitz, MH", ["Shaevitz, Michael H."])
    assert guarded["works"] == source["works"]
    assert "identity_full_name_conflicts" not in guarded["coverage"]
    # An all-caps short block can be a compact-initial byline or an ambiguous
    # display spelling.  It must never become a full-token contradiction.
    assert not hard_initial_conflict("Born, MAX", ["Born, Micheal"])
    assert not full_given_name_conflict("Born, MAX", ["Born, Micheal"])


def test_hard_chiu_conflict_is_suppressed_with_raw_count_and_audit_preserved() -> None:
    profiles = {"1013682": {"value": "Chiu, Charles B.", "preferred_name": "Charles B. Chiu", "name_variants": []}}
    occurrences = [("1112560", 0, "1013682", "Chiu, C.S.", "[]", "[]")]
    authors = ["1013682", "1013143", "1060897", "1050795", "1029197", "1073628", "1021216", "1079174"]
    source = _snapshot([_profile("1013682", "Charles B. Chiu")], [_work("1112560", ["1112560"], authors, count=8)])
    original = copy.deepcopy(source)

    guarded = apply_identity_guard(source, _connection(profiles, occurrences))

    assert source == original
    assert guarded["works"][0]["authors"] == authors[1:]
    assert guarded["works"][0]["author_count"] == 8
    assert guarded["works"][0]["source_ids"] == ["1112560"]
    assert guarded["works"][0]["unresolved_count"] == 1
    assert guarded["coverage"]["identity_conflicts"] == [{
        "work_id": "1112560", "source_id": "1112560", "person": "1013682",
        "source_name": "Chiu, C.S.",
        "profile_names": ["Charles B. Chiu", "Chiu, Charles B."],
        "reason": "all_public_profile_name_forms_have_incompatible_initials",
    }]
    assert guarded["version"].startswith("sha256:") and guarded["version"] != source["version"]
    assert apply_identity_guard(guarded, _connection(profiles, occurrences)) == guarded


def test_partial_initial_and_matching_alias_remain_resolved() -> None:
    profiles = {"1": {"value": "Kaufman, S.B.", "preferred_name": None, "name_variants": ["Kaufman, B."]}}
    occurrences = [
        ("partial", 0, "1", "Chiu, C.", "[]", "[]"),
        ("alias", 0, "1", "Kaufman, B.", "[]", "[]"),
    ]
    # The first fixture uses a distinct profile with a compatible C-prefix.
    profiles["2"] = {"value": "Chiu, Charles B.", "preferred_name": None, "name_variants": []}
    source = _snapshot(
        [_profile("1", "Kaufman, S.B.", ["Kaufman, B."]), _profile("2", "Chiu, Charles B.")],
        [_work("partial", ["partial"], ["2"]), _work("alias", ["alias"], ["1"])],
    )
    guarded = apply_identity_guard(source, _connection(profiles, occurrences))
    assert [work["authors"] for work in guarded["works"]] == [["2"], ["1"]]
    assert "identity_conflicts" not in guarded["coverage"]


def test_hard_conflict_in_this_corpus_makes_only_shared_partial_initial_ambiguous() -> None:
    profiles = {"1013682": {"value": "Chiu, Charles B.", "preferred_name": "Charles B. Chiu", "name_variants": []}}
    occurrences = [
        ("1112560", 0, "1013682", "Chiu, C.S.", "[]", "[]"),
        ("1190670", 0, "1013682", "Chiu, C.", "[]", "[]"),
        ("1969", 0, "1013682", "Chiu, C.B.", "[]", "[]"),
        ("full", 0, "1013682", "Chiu, Charles", "[]", "[]"),
        ("full-two", 0, "1013682", "Chiu, Charles B.", "[]", "[]"),
    ]
    source = _snapshot(
        [_profile("1013682", "Charles B. Chiu")],
        [
            _work("1112560", ["1112560"], ["1013682"]),
            _work("1190670", ["1190670"], ["1013682"]),
            _work("1969", ["1969"], ["1013682"]),
            _work("full", ["full"], ["1013682"]),
            _work("full-two", ["full-two"], ["1013682"]),
        ],
    )
    guarded = apply_identity_guard(source, _connection(profiles, occurrences))

    assert [work["authors"] for work in guarded["works"]] == [[], [], ["1013682"], ["1013682"], ["1013682"]]
    assert guarded["coverage"]["identity_ambiguities"] == [{
        "work_id": "1190670", "source_id": "1190670", "person": "1013682",
        "source_name": "Chiu, C.", "profile_names": ["Charles B. Chiu", "Chiu, Charles B."],
        "conflicting_source_names": ["Chiu, C.S."],
        "reason": "partial_initial_matches_profile_and_observed_conflicting_occurrence",
    }]


def test_unconfirmed_or_unknown_profiles_and_editor_occurrences_are_not_assumed_wrong() -> None:
    profiles = {"profile": {"value": "Chiu, Charles B.", "preferred_name": None, "name_variants": []}}
    occurrences = [
        ("unknown", 0, "unknown", "Chiu, C.S.", "[]", "[]"),
        ("nonpublic", 0, "nonpublic", "Chiu, C.S.", "[]", "[]"),
        ("editor", 1, "profile", "Chiu, C.S.", "[]", '["editor"]'),
    ]
    source = _snapshot(
        [
            {"id": "unknown", "name": "Chiu, Charles B.", "aliases": [], "profile_status": "literature_only"},
            _profile("nonpublic", "Chiu, Charles B.", public=False),
            _profile("profile", "Chiu, Charles B."),
        ],
        [
            _work("unknown", ["unknown"], ["unknown"]),
            _work("nonpublic", ["nonpublic"], ["nonpublic"]),
            # The editor is not a coauthor in the normalized work list.
            _work("editor", ["editor"], ["someone-else"]),
        ],
    )
    guarded = apply_identity_guard(source, _connection(profiles, occurrences))
    assert [work["authors"] for work in guarded["works"]] == [["unknown"], ["nonpublic"], ["someone-else"]]
    assert "identity_conflicts" not in guarded["coverage"]


def test_merged_source_group_removes_disputed_person_and_keeps_raw_group_for_review() -> None:
    profiles = {"1013682": {"value": "Chiu, Charles B.", "preferred_name": None, "name_variants": []}}
    occurrences = [("1112560", 0, "1013682", "Chiu, C.S.", "[]", "[]")]
    work = _work("canonical", ["1112560", "another-source"], ["1013682"])
    guarded = apply_identity_guard(_snapshot([_profile("1013682", "Chiu, Charles B.")], [work]), _connection(profiles, occurrences))
    assert guarded["works"] == [{**work, "authors": [], "unresolved_count": 1}]
    assert guarded["coverage"]["identity_conflict_review"] == [{
        "work_id": "canonical", "source_id": "1112560,another-source",
        "source_ids": ["1112560", "another-source"], "person": "1013682",
        "reason": "source_group_contains_disputed_identity_pending_review",
    }]


def test_initial_only_profile_with_two_incompatible_full_names_is_quarantined_corpus_wide() -> None:
    person = "2411810"
    profiles = {person: {"value": "Lee, K.K.", "preferred_name": None, "name_variants": []}}
    occurrences = [
        ("883174", 0, person, "Lee, Kuen", "[]", "[]"),
        ("2886055", 0, person, "Lee, Kyeongwon", "[]", "[]"),
        ("65073", 0, person, "Lee, K.K.", "[]", "[]"),
    ]
    works = [
        _work("883174", ["883174"], [person]),
        _work("2886055", ["2886055"], [person]),
        _work("65073", ["65073"], [person]),
    ]
    guarded = apply_identity_guard(_snapshot([_profile(person, "Lee, K.K.")], works), _connection(profiles, occurrences))

    assert [work["authors"] for work in guarded["works"]] == [[], [], []]
    assert all(work["author_count"] == 1 and work["unresolved_count"] == 1 for work in guarded["works"])
    assert guarded["coverage"]["identity_ambiguous_profiles"] == [{
        "person": person,
        "profile_names": ["Lee, K.K."],
        "observed_full_name_forms": ["Lee, Kuen", "Lee, Kyeongwon"],
        "reason": "initial_only_profile_has_incompatible_full_names_in_retrieved_corpus",
    }]


def test_initial_only_profile_is_not_quarantined_without_conflict_or_with_known_full_alias() -> None:
    person = "1"
    one_full = {person: {"value": "Lee, K.K.", "preferred_name": None, "name_variants": []}}
    one_source = [("one", 0, person, "Lee, Kuen", "[]", "[]")]
    source = _snapshot([_profile(person, "Lee, K.K.")], [_work("one", ["one"], [person])])
    assert apply_identity_guard(source, _connection(one_full, one_source))["works"][0]["authors"] == [person]

    known_alias = {person: {"value": "Lee, K.K.", "preferred_name": None, "name_variants": ["Lee, Kuen"]}}
    two_sources = [
        ("first", 0, person, "Lee, Kuen", "[]", "[]"),
        ("second", 0, person, "Lee, Kyeongwon", "[]", "[]"),
    ]
    source = _snapshot(
        [_profile(person, "Lee, K.K.", ["Lee, Kuen"])],
        [_work("first", ["first"], [person]), _work("second", ["second"], [person])],
    )
    guarded = apply_identity_guard(source, _connection(known_alias, two_sources))
    assert [work["authors"] for work in guarded["works"]] == [[person], [person]]
    assert "identity_ambiguous_profiles" not in guarded["coverage"]
