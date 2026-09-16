"""A deliberately tiny, auditable overlay for sourced historical PhD relations.

This module is pure: it does not retrieve people, write a database, or infer an
identity from a name.  The caller must already have both INSPIRE author records
in a snapshot before an overlay relation can be attached.
"""
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


SOURCE_KIND = "institutional_historical_supplement"
ACCESSED = "2026-09-15"

# Each row has an institutionally published statement explicitly connecting the
# student, supervision, and doctorate.  Do not extend this list from an INSPIRE
# `other` adviser field, a coauthor list, or an academic-tree web site.
_HISTORICAL_PHD: tuple[dict[str, Any], ...] = (
    {
        "adviser": "1035527",
        "student": "1011729",
        "degree": "PhD",
        "year": 1926,
        "source_url": "https://www.damtp.cam.ac.uk/events/dirac/dirac/highlights.html",
        "source_record": "supplemental:cambridge-damtp-fowler-dirac",
        "source_kind": SOURCE_KIND,
        "accessed": ACCESSED,
        # The relation is explicit, but its provenance is external to the
        # selected INSPIRE author metadata and must remain visible to callers.
        "uncertainty": "external_institutional_historical_source",
    },
    {
        "adviser": "1049952",
        "student": "1010907",
        "degree": "PhD",
        "year": 1905,
        "source_url": "https://library.ethz.ch/en/collections-and-archives/platforms/einstein-online/ausserordentlicher-professor-an-der-universitaet-zuerich-profes.html",
        "source_record": "supplemental:eth-library-kleiner-einstein",
        "source_kind": SOURCE_KIND,
        "accessed": ACCESSED,
        "uncertainty": "external_institutional_historical_source",
    },
    {
        "adviser": "1011729",
        "student": "989544",
        "degree": "PhD",
        # The AIP catalogue and later biographies differ on 1952/1953. The
        # relationship is explicit; do not manufacture a precise award year.
        "year": None,
        "source_url": "https://history.aip.org/history/catalog/icos/33994.html",
        "source_record": "supplemental:aip-oral-history-dirac-sciama",
        "source_kind": SOURCE_KIND,
        "accessed": ACCESSED,
        "uncertainty": "external_institutional_historical_source",
    },
)

# These are not title rules.  They are only the four individual records reviewed
# in docs/HISTORICAL_SOURCES.md.  Their INSPIRE author arrays describe a session,
# correspondence, translation collection, or later editorial presentation rather
# than a research collaboration by the named historical author.
_EXCLUDED_WORKS: dict[str, dict[str, str]] = {
    "187326": {
        "reason": "special_session_participant_list_not_research_coauthorship",
        "source_url": "https://inspirehep.net/literature/187326",
    },
    "361713": {
        "reason": "posthumous_correspondence_publication_not_research_coauthorship",
        "source_url": "https://inspirehep.net/literature/361713",
    },
    "4676": {
        "reason": "translation_collection_not_research_coauthorship",
        "source_url": "https://inspirehep.net/literature/4676",
    },
    "48254": {
        "reason": "retrospective_editorial_attribution_not_research_coauthorship",
        "source_url": "https://inspirehep.net/literature/48254",
    },
}

# These are individually documented relation exceptions, rather than rules
# about adviser display names.  The overlay never replaces a conflicting name
# with another person ID or creates a person.
_EXCLUDED_PROFILE_RELATIONS: tuple[dict[str, str], ...] = (
    {
        "adviser": "1011729",
        "student": "1019944",
        "source_record": "1019944",
        "reason": "native_adviser_reference_conflicts_with_firsthand_phd_supervisor_account",
        "source_url": "https://www.the-scientist.com/gell-mann-opened-my-eyes-64150",
    },
    {
        "adviser": "1011729",
        "student": "1005469",
        "source_record": "1005469",
        "reason": "research_supervisor_without_doctorate_in_native_profile",
        "source_url": "https://www.hoyle.org.uk/A-Singular-Life/Years-of-Joy/",
    },
)

# This correction is deliberately an authorship *occurrence* exclusion rather
# than a whole-work exclusion.  Literature record 44740 is a real Einstein–
# Bruria Kaufman paper, but INSPIRE points its ``Kaufman, B.`` author to the
# distinct S.B. Kaufman profile (2203900).  We must not map the display name to
# a different profile or discard the valid underlying publication.
_EXCLUDED_AUTHORSHIP_OCCURRENCES: tuple[dict[str, str], ...] = (
    {
        "source_record": "44740",
        "person": "2203900",
        "reason": "published_coauthor_name_conflicts_with_stable_author_profile",
        "source_url": "https://doi.org/10.2307/2007103",
    },
    {
        "source_record": "74757",
        "person": "1069266",
        "reason": "historical_initial_only_author_conflicts_with_modern_stable_profile",
        "source_url": "https://www.montecarlonet.org/opportunities_past_shorties/",
    },
    {
        "source_record": "41231",
        "person": "1005792",
        "reason": "published_banesh_hoffmann_conflicts_with_bernd_hoffmann_profile",
        "source_url": "https://doi.org/10.2307/1968714",
    },
    {
        "source_record": "42599",
        "person": "987542",
        "reason": "published_otto_stern_conflicts_with_mark_stern_profile",
        "source_url": "https://doi.org/10.1002/andp.2005517S148",
    },
    {
        "source_record": "44738",
        "person": "1024083",
        "reason": "published_ernst_straus_conflicts_with_emanuel_strauss_profile",
        "source_url": "https://doi.org/10.2307/1969231",
    },
)

_NEIGHBORS = {
    "1035527": ("1011729",),
    "1011729": ("1035527", "989544"),
    "989544": ("1011729",),
    "1049952": ("1010907",),
    "1010907": ("1049952",),
}


def historical_neighbors(person_id: str) -> list[str]:
    """Return only the fixed, reciprocal supplement neighbors for an ID.

    The result is an exact-ID lookup.  It deliberately performs no name search,
    historical inference, or network operation.
    """
    if isinstance(person_id, bool):
        return []
    return list(_NEIGHBORS.get(str(person_id), ()))


def _snapshot_version(snapshot: dict[str, Any]) -> str:
    """Hash all stable snapshot content, excluding volatile publication fields."""
    content = {key: value for key, value in snapshot.items() if key not in {"version", "created_at"}}
    digest = hashlib.sha256(
        json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()
    return f"sha256:{digest}"


def _people_ids(snapshot: dict[str, Any]) -> set[str]:
    raw_people = snapshot.get("people", [])
    if not isinstance(raw_people, list):
        return set()
    return {
        str(person["id"])
        for person in raw_people
        if (
            isinstance(person, dict)
            and person.get("id") is not None
            # Literature-only placeholders and ambiguous adviser references
            # are useful raw evidence, but are not fresh identity verification
            # for an external historical edge.
            and person.get("profile_status") == "profile"
        )
    }


def _overlay_exclusions(snapshot: dict[str, Any]) -> None:
    """Remove only fully reviewed non-research source groups and audit them.

    A normalized work can combine exact DOI/arXiv versions.  If its source IDs
    include an individually reviewed historical attribution *and* an unreviewed
    source, deleting the whole group could discard a genuine separate work.
    Retain that group and make the ambiguity explicit instead.
    """
    works = snapshot.get("works")
    if not isinstance(works, list):
        return
    retained: list[Any] = []
    applied: list[dict[str, str]] = []
    conflicts: list[dict[str, Any]] = []
    for work in works:
        if not isinstance(work, dict):
            retained.append(work)
            continue
        work_id = str(work.get("id")) if work.get("id") is not None else None
        raw_source_ids = work.get("source_ids")
        source_ids = {
            str(value)
            for value in raw_source_ids
            if value is not None and not isinstance(value, bool)
        } if isinstance(raw_source_ids, list) else set()
        if not source_ids and work_id is not None:
            source_ids = {work_id}
        excluded_ids = sorted(source_ids.intersection(_EXCLUDED_WORKS))
        if not excluded_ids:
            retained.append(work)
            continue
        unreviewed_ids = sorted(source_ids.difference(_EXCLUDED_WORKS))
        if unreviewed_ids:
            retained.append(work)
            conflicts.append(
                {
                    "work_id": work_id,
                    "source_ids": sorted(source_ids),
                    "excluded_source_ids": excluded_ids,
                    "unreviewed_source_ids": unreviewed_ids,
                    "reason": "merged_source_ids_include_unreviewed_record",
                }
            )
            continue
        for source_id in excluded_ids:
            applied.append({"work_id": work_id, "source_id": source_id, **_EXCLUDED_WORKS[source_id]})
    if not applied and not conflicts:
        return
    snapshot["works"] = retained
    coverage = snapshot.get("coverage")
    if not isinstance(coverage, dict):
        coverage = {}
        snapshot["coverage"] = coverage
    _merge_coverage_items(coverage, "historical_coauthorship_exclusions", applied, ("work_id", "source_id"))
    _merge_coverage_items(coverage, "historical_coauthorship_exclusion_conflicts", conflicts, ("work_id", "excluded_source_ids"))


def _merge_coverage_items(
    coverage: dict[str, Any], key: str, additions: list[dict[str, Any]], identity: tuple[str, ...]
) -> None:
    """Append audit rows once, using stable fields rather than list position."""
    previous = coverage.get(key, [])
    merged = [item for item in previous if isinstance(item, dict)] if isinstance(previous, list) else []
    existing = {tuple(json.dumps(item.get(part), sort_keys=True) for part in identity) for item in merged}
    for item in additions:
        marker = tuple(json.dumps(item.get(part), sort_keys=True) for part in identity)
        if marker not in existing:
            merged.append(item)
            existing.add(marker)
    coverage[key] = sorted(
        merged,
        key=lambda item: tuple(json.dumps(item.get(part), sort_keys=True) for part in identity),
    )


def _exclude_profile_relations(snapshot: dict[str, Any], records: list[Any]) -> list[Any]:
    """Drop one exact reviewed native relation and retain all other evidence."""
    exclusions = {
        (item["adviser"], item["student"], item["source_record"]): item
        for item in _EXCLUDED_PROFILE_RELATIONS
    }
    retained: list[Any] = []
    applied: list[dict[str, str]] = []
    for record in records:
        if not isinstance(record, dict):
            retained.append(record)
            continue
        relation = (
            str(record.get("adviser")),
            str(record.get("student")),
            str(record.get("source_record", "")),
        )
        exclusion = exclusions.get(relation)
        if exclusion is None:
            retained.append(record)
            continue
        applied.append({**exclusion})
    if applied:
        coverage = snapshot.get("coverage")
        if not isinstance(coverage, dict):
            coverage = {}
            snapshot["coverage"] = coverage
        _merge_coverage_items(
            coverage,
            "historical_profile_relation_exclusions",
            applied,
            ("adviser", "student", "source_record"),
        )
    return retained


def _overlay_authorship_occurrences(snapshot: dict[str, Any]) -> None:
    """Remove only an exact bad author occurrence, never infer a replacement.

    The work remains available as a publication.  If exact identifier grouping
    mixes the reviewed source with any other source, leave the group untouched
    and record a conflict rather than applying a source-specific correction to
    evidence that may belong to the other source.
    """
    works = snapshot.get("works")
    if not isinstance(works, list):
        return
    exclusions = {(item["source_record"], item["person"]): item for item in _EXCLUDED_AUTHORSHIP_OCCURRENCES}
    applied: list[dict[str, str]] = []
    conflicts: list[dict[str, Any]] = []
    for work in works:
        if not isinstance(work, dict):
            continue
        work_id = str(work.get("id")) if work.get("id") is not None else None
        raw_source_ids = work.get("source_ids")
        source_ids = {
            str(value)
            for value in raw_source_ids
            if value is not None and not isinstance(value, bool)
        } if isinstance(raw_source_ids, list) else set()
        if not source_ids and work_id is not None:
            source_ids = {work_id}
        authors = work.get("authors")
        if not isinstance(authors, list):
            continue
        for source_id, person in sorted(exclusions):
            exclusion = exclusions[(source_id, person)]
            if source_id not in source_ids or person not in authors:
                continue
            unreviewed_ids = sorted(source_ids - {source_id})
            if unreviewed_ids:
                conflicts.append(
                    {
                        "work_id": work_id,
                        "source_ids": sorted(source_ids),
                        "source_record": source_id,
                        "person": person,
                        "unreviewed_source_ids": unreviewed_ids,
                        "reason": "merged_source_ids_prevent_source_specific_authorship_correction",
                    }
                )
                continue
            work["authors"] = [author for author in authors if author != person]
            authors = work["authors"]
            count = work.get("author_count")
            if isinstance(count, int) and not isinstance(count, bool):
                prior_unresolved = work.get("unresolved_count", 0)
                prior = prior_unresolved if isinstance(prior_unresolved, int) and not isinstance(prior_unresolved, bool) else 0
                work["unresolved_count"] = max(prior, count - len(authors))
            applied.append({"work_id": work_id, **exclusion})
    if not applied and not conflicts:
        return
    coverage = snapshot.get("coverage")
    if not isinstance(coverage, dict):
        coverage = {}
        snapshot["coverage"] = coverage
    _merge_coverage_items(
        coverage,
        "historical_authorship_exclusions",
        applied,
        ("work_id", "source_record", "person"),
    )
    _merge_coverage_items(
        coverage,
        "historical_authorship_occurrence_conflicts",
        conflicts,
        ("work_id", "source_record", "person"),
    )


def _overlay_phd(snapshot: dict[str, Any]) -> None:
    people = _people_ids(snapshot)
    records = snapshot.get("phd")
    if not isinstance(records, list):
        records = []
    records = _exclude_profile_relations(snapshot, records)
    snapshot["phd"] = records
    known = {
        (str(record.get("adviser")), str(record.get("student")), str(record.get("source_record", "")))
        for record in records
        if isinstance(record, dict)
    }
    for relation in _HISTORICAL_PHD:
        key = (relation["adviser"], relation["student"], relation["source_record"])
        # A supplement never manufactures a person just to make a path.
        if relation["adviser"] == relation["student"] or not {relation["adviser"], relation["student"]} <= people or key in known:
            continue
        records.append(copy.deepcopy(relation))
        known.add(key)
    records.sort(key=lambda record: (
        str(record.get("student", "")) if isinstance(record, dict) else "",
        str(record.get("adviser", "")) if isinstance(record, dict) else "",
        str(record.get("source_record", "")) if isinstance(record, dict) else "",
    ))


def apply_historical(snapshot: dict[str, Any], *, copy_input: bool = True, version: bool = True) -> dict[str, Any]:
    """Return a new snapshot with the narrow historical overlay applied.

    Existing people are never modified or added.  Exact record exclusions are
    removed from the derived coauthor-work view while their reason and source
    remain in ``coverage.historical_coauthorship_exclusions``.  The function is
    idempotent and leaves the input object untouched - unless the caller owns a
    fresh object and passes ``copy_input=False``; a live search rebuilds this
    after every page, and the copy and the version hash it would recompute
    anyway are most of that cost.
    """
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be an object")
    result = copy.deepcopy(snapshot) if copy_input else snapshot
    _overlay_exclusions(result)
    _overlay_authorship_occurrences(result)
    _overlay_phd(result)
    if version:
        result["version"] = _snapshot_version(result)
    return result
