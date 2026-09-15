"""Tests for the closed, source-audited historical overlay."""
from __future__ import annotations

import copy
import json

import pytest

from hepgraph.historical import apply_historical, historical_neighbors


FOWLER = "1035527"
DIRAC = "1011729"
SCIAMA = "989544"
KLEINER = "1049952"
EINSTEIN = "1010907"
POLKINGHORNE = "1019944"
HOYLE = "1005469"
SB_KAUFMAN = "2203900"
HOLGER_SCHULZ = "1069266"
BERND_HOFFMANN = "1005792"
MARK_STERN = "987542"
EMANUEL_STRAUSS = "1024083"


def _snapshot(
    *people: str,
    works: list[dict] | None = None,
    phd: list[dict] | None = None,
    profile_status: str = "profile",
) -> dict:
    return {
        "version": "sha256:input",
        "created_at": "2026-09-15T00:00:00Z",
        "coverage": {"complete": False, "queries": [], "failures": []},
        "people": [
            {"id": person, "name": f"Person {person}", "profile_status": profile_status}
            for person in people
        ],
        "works": works or [],
        "phd": phd or [],
        "examples": [],
    }


def test_historical_neighbors_are_closed_exact_id_pairs() -> None:
    assert historical_neighbors(FOWLER) == [DIRAC]
    assert historical_neighbors(DIRAC) == [FOWLER, SCIAMA]
    assert historical_neighbors(SCIAMA) == [DIRAC]
    assert historical_neighbors(KLEINER) == [EINSTEIN]
    assert historical_neighbors(EINSTEIN) == [KLEINER]
    assert historical_neighbors("993651") == []  # Petcov has no supported continuation.
    assert historical_neighbors(True) == []


def test_overlay_adds_only_resolved_distinct_documented_pairs_and_is_idempotent() -> None:
    source = _snapshot(FOWLER, DIRAC, KLEINER, EINSTEIN, "ordinary")
    original = copy.deepcopy(source)
    overlaid = apply_historical(source)

    assert source == original  # no mutation of caller or stored INSPIRE data
    assert {person["id"] for person in overlaid["people"]} == {FOWLER, DIRAC, KLEINER, EINSTEIN, "ordinary"}
    assert {(edge["adviser"], edge["student"]) for edge in overlaid["phd"]} == {(FOWLER, DIRAC), (KLEINER, EINSTEIN)}
    for edge in overlaid["phd"]:
        assert edge["degree"] == "PhD"
        assert edge["source_record"].startswith("supplemental:")
        assert edge["source_kind"] == "institutional_historical_supplement"
        assert edge["accessed"] == "2026-09-15"
        assert edge["uncertainty"] == "external_institutional_historical_source"
        assert edge["source_url"].startswith("https://")
        assert isinstance(edge["year"], int)
    assert overlaid["version"].startswith("sha256:") and overlaid["version"] != source["version"]
    assert apply_historical(overlaid) == overlaid


def test_archival_sciama_doctoral_relation_has_provenance_without_guessed_year():
    source = _snapshot(DIRAC, SCIAMA)
    overlaid = apply_historical(source)
    relation, = overlaid['phd']
    assert (relation['adviser'], relation['student'], relation['degree']) == (DIRAC, SCIAMA, 'PhD')
    assert relation['year'] is None
    assert relation['source_url'] == 'https://history.aip.org/history/catalog/icos/33994.html'
    assert relation['source_record'] == 'supplemental:aip-oral-history-dirac-sciama'
    assert apply_historical(overlaid) == overlaid


@pytest.mark.parametrize("people", [(FOWLER,), (DIRAC,), (KLEINER,), (EINSTEIN,), (FOWLER, KLEINER)])
def test_overlay_never_creates_missing_people_or_half_edges(people: tuple[str, ...]) -> None:
    overlaid = apply_historical(_snapshot(*people))
    assert [person["id"] for person in overlaid["people"]] == list(people)
    assert overlaid["phd"] == []


@pytest.mark.parametrize("profile_status", ["literature_only", "unresolved", None, ""])
def test_overlay_requires_fresh_profile_identity_for_both_endpoints(profile_status: str | None) -> None:
    overlaid = apply_historical(_snapshot(FOWLER, DIRAC, profile_status=profile_status))
    assert overlaid["phd"] == []


def test_exact_reviewed_work_exclusions_are_audited_without_heuristics() -> None:
    reviewed = ["187326", "361713", "4676", "48254"]
    ordinary = {"id": "ordinary", "authors": [FOWLER, DIRAC], "document_types": ["article"], "author_count": 2}
    works = [ordinary, *({"id": work_id, "authors": [FOWLER, DIRAC], "document_types": ["article"], "author_count": 2} for work_id in reviewed)]
    source = _snapshot(FOWLER, DIRAC, works=works)
    overlaid = apply_historical(source)

    assert [work["id"] for work in overlaid["works"]] == ["ordinary"]
    assert [item["work_id"] for item in overlaid["coverage"]["historical_coauthorship_exclusions"]] == sorted(reviewed)
    assert all(item["reason"].endswith("not_research_coauthorship") for item in overlaid["coverage"]["historical_coauthorship_exclusions"])
    assert [work["id"] for work in source["works"]] == ["ordinary", *reviewed]


def test_source_id_aliases_are_checked_and_mixed_groups_are_retained_for_review() -> None:
    source = _snapshot(
        FOWLER,
        DIRAC,
        works=[
            {"id": "canonical", "source_ids": ["187326"], "authors": [FOWLER, DIRAC]},
            {"id": "merged", "source_ids": ["48254", "independent-version"], "authors": [EINSTEIN]},
        ],
    )
    overlaid = apply_historical(source)

    assert [work["id"] for work in overlaid["works"]] == ["merged"]
    assert overlaid["coverage"]["historical_coauthorship_exclusions"] == [
        {
            "work_id": "canonical",
            "source_id": "187326",
            "reason": "special_session_participant_list_not_research_coauthorship",
            "source_url": "https://inspirehep.net/literature/187326",
        }
    ]
    assert overlaid["coverage"]["historical_coauthorship_exclusion_conflicts"] == [
        {
            "work_id": "merged",
            "source_ids": ["48254", "independent-version"],
            "excluded_source_ids": ["48254"],
            "unreviewed_source_ids": ["independent-version"],
            "reason": "merged_source_ids_include_unreviewed_record",
        }
    ]


def test_exact_native_dirac_polkinghorne_relation_is_excluded_without_name_repair() -> None:
    malformed = {
        "adviser": DIRAC,
        "student": POLKINGHORNE,
        "degree": "PhD",
        "source_record": POLKINGHORNE,
    }
    separately_sourced = {**malformed, "source_record": "supplemental:separate-evidence"}
    overlaid = apply_historical(_snapshot(DIRAC, POLKINGHORNE, phd=[malformed, separately_sourced]))

    assert overlaid["phd"] == [separately_sourced]
    assert "990582" not in {person["id"] for person in overlaid["people"]}
    assert overlaid["coverage"]["historical_profile_relation_exclusions"] == [
        {
            "adviser": DIRAC,
            "student": POLKINGHORNE,
            "source_record": POLKINGHORNE,
            "reason": "native_adviser_reference_conflicts_with_firsthand_phd_supervisor_account",
            "source_url": "https://www.the-scientist.com/gell-mann-opened-my-eyes-64150",
        }
    ]


def test_exact_hoyle_research_supervision_is_not_promoted_to_a_phd() -> None:
    false_phd = {
        "adviser": DIRAC,
        "student": HOYLE,
        "degree": "PhD",
        "source_record": HOYLE,
    }
    retained_other_evidence = {**false_phd, "source_record": "supplemental:separate-evidence"}
    overlaid = apply_historical(_snapshot(DIRAC, HOYLE, phd=[false_phd, retained_other_evidence]))

    assert overlaid["phd"] == [retained_other_evidence]
    assert overlaid["coverage"]["historical_profile_relation_exclusions"] == [
        {
            "adviser": DIRAC,
            "student": HOYLE,
            "source_record": HOYLE,
            "reason": "research_supervisor_without_doctorate_in_native_profile",
            "source_url": "https://www.hoyle.org.uk/A-Singular-Life/Years-of-Joy/",
        }
    ]


def test_exact_wrong_einstein_authorship_occurrence_is_removed_without_name_replacement() -> None:
    work = {
        "id": "44740",
        "source_ids": ["44740"],
        "authors": [EINSTEIN, SB_KAUFMAN],
        "author_count": 2,
        "unresolved_count": 0,
    }
    overlaid = apply_historical(_snapshot(EINSTEIN, SB_KAUFMAN, works=[work]))

    assert overlaid["works"] == [{**work, "authors": [EINSTEIN], "unresolved_count": 1}]
    assert overlaid["coverage"]["historical_authorship_exclusions"] == [
        {
            "work_id": "44740",
            "source_record": "44740",
            "person": SB_KAUFMAN,
            "reason": "published_coauthor_name_conflicts_with_stable_author_profile",
            "source_url": "https://doi.org/10.2307/2007103",
        }
    ]
    assert "Bruria Kaufman" not in json.dumps(overlaid)


def test_authorship_correction_does_not_cross_a_mixed_source_group() -> None:
    work = {
        "id": "canonical",
        "source_ids": ["44740", "unreviewed-version"],
        "authors": [EINSTEIN, SB_KAUFMAN],
        "author_count": 2,
        "unresolved_count": 0,
    }
    overlaid = apply_historical(_snapshot(EINSTEIN, SB_KAUFMAN, works=[work]))

    assert overlaid["works"] == [work]
    assert overlaid["coverage"]["historical_authorship_occurrence_conflicts"] == [
        {
            "work_id": "canonical",
            "source_ids": ["44740", "unreviewed-version"],
            "source_record": "44740",
            "person": SB_KAUFMAN,
            "unreviewed_source_ids": ["unreviewed-version"],
            "reason": "merged_source_ids_prevent_source_specific_authorship_correction",
        }
    ]


def test_exact_historical_initial_only_author_is_not_merged_into_modern_holger_schulz() -> None:
    work = {
        "id": "74757",
        "source_ids": ["74757"],
        "authors": ["1009613", "1010724", "996398", "2267145", "982466", "2267154", "1008661", HOLGER_SCHULZ],
        "author_count": 8,
        "unresolved_count": 0,
    }
    overlaid = apply_historical(_snapshot("1009613", HOLGER_SCHULZ, works=[work]))

    assert overlaid["works"] == [{**work, "authors": work["authors"][:-1], "unresolved_count": 1}]
    assert overlaid["coverage"]["historical_authorship_exclusions"] == [
        {
            "work_id": "74757",
            "source_record": "74757",
            "person": HOLGER_SCHULZ,
            "reason": "historical_initial_only_author_conflicts_with_modern_stable_profile",
            "source_url": "https://www.montecarlonet.org/opportunities_past_shorties/",
        }
    ]


@pytest.mark.parametrize(
    ("work_id", "person", "reason", "source_url"),
    [
        ("41231", BERND_HOFFMANN, "published_banesh_hoffmann_conflicts_with_bernd_hoffmann_profile", "https://doi.org/10.2307/1968714"),
        ("42599", MARK_STERN, "published_otto_stern_conflicts_with_mark_stern_profile", "https://doi.org/10.1002/andp.2005517S148"),
        ("44738", EMANUEL_STRAUSS, "published_ernst_straus_conflicts_with_emanuel_strauss_profile", "https://doi.org/10.2307/1969231"),
    ],
)
def test_exact_einstein_historical_profile_mismatches_leave_the_paper_intact(
    work_id: str, person: str, reason: str, source_url: str
) -> None:
    work = {
        "id": work_id,
        "source_ids": [work_id],
        "authors": [EINSTEIN, person],
        "author_count": 2,
        "unresolved_count": 0,
    }
    overlaid = apply_historical(_snapshot(EINSTEIN, person, works=[work]))

    assert overlaid["works"] == [{**work, "authors": [EINSTEIN], "unresolved_count": 1}]
    assert overlaid["coverage"]["historical_authorship_exclusions"] == [{
        "work_id": work_id,
        "source_record": work_id,
        "person": person,
        "reason": reason,
        "source_url": source_url,
    }]


def test_existing_native_evidence_is_preserved_while_distinct_supplement_is_added() -> None:
    native = {"adviser": FOWLER, "student": DIRAC, "degree": "PhD", "year": None,
              "source_record": DIRAC, "source_url": f"https://inspirehep.net/authors/{DIRAC}", "uncertainty": "curated_relation_not_true"}
    overlaid = apply_historical(_snapshot(FOWLER, DIRAC, phd=[native]))
    assert len(overlaid["phd"]) == 2
    assert native in overlaid["phd"]
    assert {edge["source_record"] for edge in overlaid["phd"]} == {DIRAC, "supplemental:cambridge-damtp-fowler-dirac"}
