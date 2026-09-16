"""Conservative authorship identity checks for already retrieved INSPIRE data.

The guard is intentionally one-way: it can make a linked author occurrence
unresolved when that occurrence's published initials contradict every known
public profile-name form.  It never supplies a replacement person or performs a
name search.  It does no network I/O and writes no database state.
"""
from __future__ import annotations

import copy
import functools
import hashlib
import json
import re
import sqlite3
import unicodedata
from typing import Any, Iterable


# A lone ``V`` is also an ordinary author initial.  Treating it as a suffix
# would turn ``V.F.`` into ``F.`` and can create a false hard conflict.  The
# guard must leave that ambiguous rather than remove an authorship occurrence.
_SUFFIXES = {"jr", "sr", "ii", "iii", "iv"}
_MAX_COMPACT_INITIALS = 4


def _memo(function):
    """Cache a pure name helper.

    Every helper below is a function of its string arguments alone, and a live
    search rebuilds the guarded snapshot after every retrieved page: the same
    few thousand bylines and profile forms are compared again each time.  On a
    273-request search the uncached guard spent 220 s in these comparisons
    against 167 s waiting for INSPIRE.  Unhashable arguments (malformed source
    data) fall back to the plain call.
    """
    cached = functools.lru_cache(maxsize=1 << 18)(function)

    @functools.wraps(function)
    def wrapper(*args):
        try:
            return cached(*args)
        except TypeError:
            return function(*args)
    return wrapper


def _forms(names: Iterable[Any]) -> tuple[Any, ...]:
    """A hashable, order-preserving view of profile name forms."""
    return names if isinstance(names, tuple) else tuple(names)


@_memo
def _normal(value: str) -> str:
    """Case-fold a name component while treating diacritics and hyphens alike."""
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(char for char in decomposed.casefold() if char.isalpha())


@_memo
def _words(value: str) -> tuple[str, ...]:
    """Split a name only after removing NFKD combining marks.

    Regex word boundaries regard a combining mark as a separator.  Running the
    old expression directly over ``Ga\N{COMBINING ACUTE ACCENT}bor`` consequently
    produced ``Ga`` and ``bor`` as two apparent given names.  Removing marks
    first preserves one token while retaining the deliberately conservative
    treatment of punctuation and hyphens as separators.
    """
    decomposed = unicodedata.normalize("NFKD", value)
    without_marks = "".join(char for char in decomposed if not unicodedata.combining(char))
    return tuple(word for word in re.findall(r"[^\W\d_]+", without_marks, flags=re.UNICODE) if _normal(word))


@_memo
def _given_words(value: str) -> tuple[str, ...]:
    """Return given-name tokens, expanding short all-caps compact initials.

    INSPIRE bylines sometimes omit periods and spaces in initial sequences, for
    example ``MH`` for ``M.H.``.  A short all-caps token is not sufficiently
    explicit to serve as a full given name, so expand it character by character
    before comparison.  This deliberately also leaves an all-caps short name
    uncertain rather than treating it as a conflicting fully stated name.
    """
    words = _words(value)
    if len(words) >= 2 and _normal(words[-1]) in _SUFFIXES:
        words = words[:-1]
    expanded: list[str] = []
    for word in words:
        normalized = _normal(word)
        if 2 <= len(normalized) <= _MAX_COMPACT_INITIALS and word.isupper():
            expanded.extend(normalized)
        else:
            expanded.append(word)
    return tuple(expanded)


@_memo
def _given_initials(value: str) -> tuple[str, ...] | None:
    """Return stated initials/full-name initials, or ``None`` for unusable text."""
    words = _given_words(value)
    if not words:
        return None
    initials = tuple(_normal(word)[0] for word in words if _normal(word))
    return initials or None


@_memo
def _given_tokens(value: str) -> tuple[str, ...] | None:
    """Return normalized given-name tokens, retaining full-token information."""
    tokens = tuple(_normal(word) for word in _given_words(value))
    return tokens or None


@_memo
def _comma_name(name: Any) -> tuple[str, tuple[str, ...]] | None:
    """Parse the unambiguous ``surname, given`` source form only."""
    if not isinstance(name, str) or name.count(",") != 1:
        return None
    surname, given = (part.strip() for part in name.split(",", 1))
    surname_key = _normal(surname)
    initials = _given_initials(given)
    if not surname_key or initials is None:
        return None
    return surname_key, initials


@_memo
def _profile_initials(name: Any, expected_surname: str) -> tuple[str, ...] | None:
    """Parse one profile name only when its surname is explicit and compatible.

    A comma form has an unambiguous surname.  For a normal display form we use
    only a single-word final surname; multipart particles therefore remain
    unparsed rather than risking a false conflict.
    """
    if not isinstance(name, str) or not name.strip():
        return None
    if name.count(",") == 1:
        surname, given = (part.strip() for part in name.split(",", 1))
        if _normal(surname) != expected_surname:
            return None
        return _given_initials(given)
    if "," in name:
        return None
    words = _words(name)
    if len(words) < 2 or _normal(words[-1]) != expected_surname:
        return None
    return _given_initials(" ".join(words[:-1]))


@_memo
def _profile_given_tokens(name: Any, expected_surname: str) -> tuple[str, ...] | None:
    """Parse profile given-name tokens under the same conservative surname rule."""
    if not isinstance(name, str) or not name.strip():
        return None
    if name.count(",") == 1:
        surname, given = (part.strip() for part in name.split(",", 1))
        if _normal(surname) != expected_surname:
            return None
        return _given_tokens(given)
    if "," in name:
        return None
    words = _words(name)
    if len(words) < 2 or _normal(words[-1]) != expected_surname:
        return None
    return _given_tokens(" ".join(words[:-1]))


def _full_token_compatible(left: str, right: str) -> bool:
    """Accept spelling prefixes only when both sides are stated full tokens."""
    return len(left) > 1 and len(right) > 1 and (left.startswith(right) or right.startswith(left))


def hard_initial_conflict(source_name: Any, profile_names: Iterable[Any]) -> bool:
    return _hard_initial_conflict(source_name, _forms(profile_names))


@_memo
def _hard_initial_conflict(source_name: Any, profile_names: tuple[Any, ...]) -> bool:
    """Whether a source's explicit initial sequence contradicts every profile form.

    A source initial sequence may be a prefix of a profile's known given names:
    ``C. Chiu`` is compatible with Charles B. Chiu.  In contrast, ``C.S. Chiu``
    conflicts with Charles B. Chiu at a stated second initial, and ``B. Kaufman``
    conflicts with S.B. Kaufman at a stated first initial.  Any missing,
    unparsable, surname-incompatible, or matching profile form makes the answer
    false.  This deliberately favors false negatives over false identity splits.
    """
    parsed = _comma_name(source_name)
    if parsed is None:
        return False
    surname, source_initials = parsed
    profile_forms = list(profile_names)
    if not profile_forms:
        return False
    incompatible = False
    for name in profile_forms:
        initials = _profile_initials(name, surname)
        if initials is None:
            return False
        if len(initials) < len(source_initials):
            return False
        if initials[: len(source_initials)] == source_initials:
            return False
        incompatible = True
    return incompatible


def full_given_name_conflict(source_name: Any, profile_names: Iterable[Any]) -> bool:
    return _full_given_name_conflict(source_name, _forms(profile_names))


@_memo
def _full_given_name_conflict(source_name: Any, profile_names: tuple[Any, ...]) -> bool:
    """Whether fully stated source names contradict every public profile form.

    Initials cannot settle a ``Micheal`` versus ``Max`` collision, because both
    reduce to ``M``.  A full-name conflict is safe only when every usable public
    profile form has a full, position-aligned token for every full source token,
    and each form disagrees at least once.  An initial-only profile alias,
    omitted component, matching token, or prefix-compatible spelling leaves
    the existing source link unchanged because the comparison is inconclusive.
    """
    parsed = _comma_name(source_name)
    if parsed is None:
        return False
    surname, _ = parsed
    _, given = (part.strip() for part in source_name.split(",", 1))
    source_tokens = _given_tokens(given)
    full_positions = [(index, token) for index, token in enumerate(source_tokens or ()) if len(token) > 1]
    if not full_positions:
        return False
    forms = list(profile_names)
    if not forms:
        return False
    for name in forms:
        profile_tokens = _profile_given_tokens(name, surname)
        if profile_tokens is None:
            return False
        # A profile which leaves any full source component abbreviated or
        # unstated does not explicitly contradict it.
        if any(index >= len(profile_tokens) or len(profile_tokens[index]) <= 1 for index, _ in full_positions):
            return False
        if all(_full_token_compatible(token, profile_tokens[index]) for index, token in full_positions):
            return False
    return True


def partial_initial_ambiguity(source_name: Any, profile_names: Iterable[Any], conflicting_names: Iterable[Any]) -> bool:
    return _partial_initial_ambiguity(source_name, _forms(profile_names), _forms(conflicting_names))


@_memo
def _partial_initial_ambiguity(source_name: Any, profile_names: tuple[Any, ...], conflicting_names: tuple[Any, ...]) -> bool:
    """Whether a short compatible form is ambiguous within this retrieved corpus.

    This is deliberately weaker than a hard conflict.  It applies only after a
    different occurrence already has a hard conflict for the same exact public
    profile in this snapshot.  A source ``C. Chiu`` is then ambiguous between
    Charles B. Chiu and observed ``C.S. Chiu``; an explicit ``C.B. Chiu`` is
    not a prefix of the conflicting C.S. form and stays resolved.
    """
    parsed = _comma_name(source_name)
    if parsed is None:
        return False
    surname, source_initials = parsed
    _, source_given = (part.strip() for part in source_name.split(",", 1))
    source_tokens = _given_tokens(source_given)
    if source_tokens is None:
        return False
    profile_initials = [_profile_initials(name, surname) for name in profile_names]
    if not profile_initials or any(initials is None for initials in profile_initials):
        return False
    if any(len(initials) <= len(source_initials) or initials[: len(source_initials)] != source_initials for initials in profile_initials):
        return False
    full_positions = [(index, token) for index, token in enumerate(source_tokens) if len(token) > 1]
    profile_tokens = [_profile_given_tokens(name, surname) for name in profile_names]
    if full_positions and (any(tokens is None for tokens in profile_tokens) or any(
        len(tokens) <= index or not _full_token_compatible(token, tokens[index])
        for index, token in full_positions for tokens in profile_tokens if tokens is not None
    )):
        return False
    for name in conflicting_names:
        conflict = _comma_name(name)
        if conflict is None:
            continue
        conflict_surname, conflict_initials = conflict
        if conflict_surname != surname or len(conflict_initials) <= len(source_initials) or conflict_initials[: len(source_initials)] != source_initials:
            continue
        _, conflict_given = (part.strip() for part in name.split(",", 1))
        conflict_tokens = _given_tokens(conflict_given)
        if conflict_tokens is None:
            continue
        if any(len(conflict_tokens) <= index or not _full_token_compatible(token, conflict_tokens[index]) for index, token in full_positions):
            continue
        if conflict_surname == surname:
            return True
    return False


def _profile_people(snapshot: dict[str, Any], connection: sqlite3.Connection) -> dict[str, list[str]]:
    """Return names only for public, fetched author profiles in this snapshot."""
    people = snapshot.get("people")
    if not isinstance(people, list):
        return {}
    requested: dict[str, list[str]] = {}
    for person in people:
        if not isinstance(person, dict) or person.get("profile_status") != "profile":
            continue
        person_id = person.get("id")
        if person_id is None or isinstance(person_id, bool):
            continue
        person_id = str(person_id)
        if person.get("source_url") != f"https://inspirehep.net/authors/{person_id}":
            continue
        names = [person.get("name"), *(person.get("aliases") if isinstance(person.get("aliases"), list) else [])]
        requested[person_id] = [name for name in names if isinstance(name, str) and name.strip()]
    if not requested:
        return {}
    try:
        rows = connection.execute(
            "SELECT recid,payload FROM source_records WHERE collection='authors' AND deleted=0"
        ).fetchall()
    except (sqlite3.DatabaseError, AttributeError, TypeError):
        return {}
    profiles: dict[str, list[str]] = {}
    for recid, payload in rows:
        person_id = str(recid)
        if person_id not in requested:
            continue
        try:
            data = json.loads(payload)
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
        name = data.get("name") if isinstance(data, dict) else None
        if not isinstance(name, dict):
            continue
        source_names = [name.get("value"), name.get("preferred_name")]
        variants = name.get("name_variants")
        if isinstance(variants, list):
            source_names.extend(variants)
        merged = [*requested[person_id], *(item for item in source_names if isinstance(item, str) and item.strip())]
        # The profile row makes this a fetched public INSPIRE profile, rather
        # than a literature-created placeholder bearing a similar display name.
        profiles[person_id] = list(dict.fromkeys(merged))
    return profiles


def _death_year(value: Any) -> int | None:
    """Return only a syntactically documented profile death year.

    This guard does not infer dates.  A malformed or partial non-calendar value
    is harmless metadata and must not alter an authorship link.
    """
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"(1\d{3}|20\d{2})(?:-(0[1-9]|1[0-2])(?:-(0[1-9]|[12]\d|3[01]))?)?", value)
    if not match:
        return None
    if match.group(3):
        from datetime import date
        try:
            date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            return None
    return int(match.group(1))


def _profile_lifetimes(snapshot: dict[str, Any], connection: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    """Return documented death dates for fetched public INSPIRE profiles only."""
    people = snapshot.get("people")
    if not isinstance(people, list):
        return {}
    requested: dict[str, str] = {}
    for person in people:
        if not isinstance(person, dict) or person.get("profile_status") != "profile":
            continue
        person_id = person.get("id")
        if person_id is None or isinstance(person_id, bool):
            continue
        person_id = str(person_id)
        source_link = f"https://inspirehep.net/authors/{person_id}"
        if person.get("source_url") == source_link:
            requested[person_id] = source_link
    if not requested:
        return {}
    try:
        rows = connection.execute(
            "SELECT recid,payload FROM source_records WHERE collection='authors' AND deleted=0"
        ).fetchall()
    except (sqlite3.DatabaseError, AttributeError, TypeError):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for recid, payload in rows:
        person_id = str(recid)
        if person_id not in requested:
            continue
        try:
            data = json.loads(payload)
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
        death_date = data.get("death_date") if isinstance(data, dict) else None
        death_year = _death_year(death_date)
        if death_year is not None:
            result[person_id] = {
                "death_date": death_date,
                "death_year": death_year,
                "source_profile_link": requested[person_id],
            }
    return result


def _initial_only_compatible_with_full_profile(source_name: Any, profile_names: Iterable[Any]) -> bool:
    """Whether a byline is a matching-surname initial-only form of a full profile.

    Both comma and simple display forms are accepted only where their final
    surname is structurally clear.  Multipart names and any fully written raw
    given name remain uncertain and are therefore retained.
    """
    if not isinstance(source_name, str) or not source_name.strip():
        return False
    if source_name.count(",") == 1:
        surname, given = (part.strip() for part in source_name.split(",", 1))
        surname_key = _normal(surname)
        source_tokens = _given_tokens(given)
    elif "," not in source_name:
        words = _words(source_name)
        if len(words) < 2:
            return False
        surname_key = _normal(words[-1])
        source_tokens = _given_tokens(" ".join(words[:-1]))
    else:
        return False
    if not surname_key or source_tokens is None or not all(len(token) == 1 for token in source_tokens):
        return False
    source_initials = tuple(token[0] for token in source_tokens)
    for profile_name in profile_names:
        profile_tokens = _profile_given_tokens(profile_name, surname_key)
        if (profile_tokens is None or not any(len(token) > 1 for token in profile_tokens)
                or len(profile_tokens) < len(source_initials)):
            continue
        if tuple(token[0] for token in profile_tokens[:len(source_initials)]) == source_initials:
            return True
    return False


def _source_ids(work: dict[str, Any]) -> set[str]:
    raw = work.get("source_ids")
    result = {str(item) for item in raw if item is not None and not isinstance(item, bool)} if isinstance(raw, list) else set()
    if not result and work.get("id") is not None and not isinstance(work.get("id"), bool):
        result.add(str(work["id"]))
    return result


def _occurrence_index(connection: sqlite3.Connection) -> dict[str, list[tuple[str, str]]]:
    """Every ``(person_id, source_name)`` occurrence, keyed by source record.

    Read once per guard run: a per-work query was one SQLite round trip per
    work per rebuild, which a long live search repeats hundreds of times.
    """
    try:
        rows = connection.execute("SELECT record_id,person_id,full_name FROM authorship_occurrences").fetchall()
    except (sqlite3.DatabaseError, AttributeError, TypeError):
        return {}
    index: dict[str, list[tuple[str, str]]] = {}
    for record_id, person_id, full_name in rows:
        if person_id is None or not isinstance(full_name, str):
            continue
        index.setdefault(str(record_id), []).append((str(person_id), full_name))
    return index


def _occurrences(index: dict[str, list[tuple[str, str]]], source_ids: set[str]) -> dict[str, list[tuple[str, str]]]:
    """Map resolved person IDs to exact ``(source_id, source_name)`` rows."""
    result: dict[str, list[tuple[str, str]]] = {}
    for source_id in sorted(source_ids):
        for person_id, full_name in index.get(source_id, ()):
            result.setdefault(person_id, []).append((source_id, full_name))
    return result


def _merge_coverage(coverage: dict[str, Any], additions: list[dict[str, Any]], key: str) -> None:
    old = coverage.get(key)
    merged = [item for item in old if isinstance(item, dict)] if isinstance(old, list) else []
    present = {(str(item.get("work_id")), str(item.get("source_id")), str(item.get("person"))) for item in merged}
    for item in additions:
        marker = (str(item["work_id"]), str(item["source_id"]), str(item["person"]))
        if marker not in present:
            merged.append(item)
            present.add(marker)
    coverage[key] = sorted(merged, key=lambda item: (str(item["work_id"]), str(item["source_id"]), str(item["person"])))


def _merge_profile_coverage(coverage: dict[str, Any], additions: list[dict[str, Any]]) -> None:
    """Merge one audit row per ambiguous profile, independent of work grouping."""
    old = coverage.get("identity_ambiguous_profiles")
    merged = [item for item in old if isinstance(item, dict)] if isinstance(old, list) else []
    present = {str(item.get("person")) for item in merged}
    for item in additions:
        if item["person"] not in present:
            merged.append(item)
            present.add(item["person"])
    coverage["identity_ambiguous_profiles"] = sorted(merged, key=lambda item: item["person"])


def _profile_forms_are_initial_only(profile_names: Iterable[Any], surname: str) -> bool:
    return _profile_forms_initial_only(_forms(profile_names), surname)


@_memo
def _profile_forms_initial_only(profile_names: tuple[Any, ...], surname: str) -> bool:
    """Require every public profile form to parse and contain initials only."""
    forms = list(profile_names)
    if not forms:
        return False
    parsed = [_profile_given_tokens(name, surname) for name in forms]
    return bool(parsed) and all(tokens is not None and all(len(token) == 1 for token in tokens) for tokens in parsed)


@_memo
def _incompatible_full_given_forms(left: str, right: str) -> bool:
    """Whether two source names state conflicting full given-name tokens."""
    left_parsed = _comma_name(left)
    right_parsed = _comma_name(right)
    if left_parsed is None or right_parsed is None or left_parsed[0] != right_parsed[0]:
        return False
    _, left_given = (part.strip() for part in left.split(",", 1))
    _, right_given = (part.strip() for part in right.split(",", 1))
    left_tokens, right_tokens = _given_tokens(left_given), _given_tokens(right_given)
    if left_tokens is None or right_tokens is None:
        return False
    for left_token, right_token in zip(left_tokens, right_tokens):
        if len(left_token) > 1 and len(right_token) > 1 and not _full_token_compatible(left_token, right_token):
            return True
    return False


def _ambiguous_initial_only_profiles(
    profiles: dict[str, list[str]],
    inspected: Iterable[tuple[dict[str, Any], set[str], dict[str, list[tuple[str, str]]]]],
) -> dict[str, list[str]]:
    """Find initial-only public profiles linked to incompatible full source names.

    This is corpus-local evidence, not a claim that a short name is universally
    wrong.  A known full profile alias prevents this profile-wide quarantine.
    """
    observed: dict[str, list[str]] = {}
    for work, _, occurrences in inspected:
        authors = work.get("authors") if isinstance(work, dict) else None
        if not isinstance(authors, list):
            continue
        for person in authors:
            person_id = str(person)
            profile_names = profiles.get(person_id)
            if not profile_names:
                continue
            for _, source_name in occurrences.get(person_id, []):
                parsed = _comma_name(source_name)
                if parsed is None:
                    continue
                surname, _ = parsed
                if not _profile_forms_are_initial_only(profile_names, surname):
                    continue
                _, given = (part.strip() for part in source_name.split(",", 1))
                tokens = _given_tokens(given)
                if tokens is not None and any(len(token) > 1 for token in tokens):
                    observed.setdefault(person_id, []).append(source_name)
    ambiguous: dict[str, list[str]] = {}
    for person_id, names in observed.items():
        unique = sorted(set(names))
        if any(_incompatible_full_given_forms(left, right) for index, left in enumerate(unique) for right in unique[index + 1:]):
            ambiguous[person_id] = unique
    return ambiguous


def _version(snapshot: dict[str, Any]) -> str:
    content = {key: value for key, value in snapshot.items() if key not in {"version", "created_at"}}
    data = json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def _remove_author_occurrence(work: dict[str, Any], person_id: str) -> None:
    """Make one disputed resolved member unavailable while retaining raw count."""
    authors = work.get("authors")
    if not isinstance(authors, list):
        return
    work["authors"] = [author for author in authors if str(author) != person_id]
    raw_count = work.get("author_count")
    prior = work.get("unresolved_count", 0)
    prior_count = prior if isinstance(prior, int) and not isinstance(prior, bool) else 0
    if isinstance(raw_count, int) and not isinstance(raw_count, bool):
        work["unresolved_count"] = max(prior_count + 1, raw_count - len(work["authors"]))


@_memo
def _explicit_profile_surname(name: Any) -> str | None:
    """Parse only an explicit comma form or an ordinary two-word full name."""
    parsed = _comma_name(name)
    if parsed is not None:
        return parsed[0]
    if not isinstance(name, str) or "," in name:
        return None
    words = _words(name)
    # Multiword surnames, suffixes and native-name order remain uncertain.
    if len(words) != 2 or len(_normal(words[0])) < 2:
        return None
    return _normal(words[-1])


def _adviser_name_conflict(name: Any, forms: list[str]) -> bool:
    source = _comma_name(name)
    if source is None or not forms:
        return False
    surnames = [_explicit_profile_surname(form) for form in forms]
    different_surname = all(surname is not None and surname != source[0] for surname in surnames)
    return different_surname or hard_initial_conflict(name, forms) or full_given_name_conflict(name, forms)


def _guard_phd_references(result: dict[str, Any], connection: sqlite3.Connection,
                          profiles: dict[str, list[str]]) -> None:
    """Withhold a native adviser link whose own stated name contradicts its ID.

    This never swaps or repairs upstream identifiers. An independently sourced
    institutional relation, thesis edge, or coauthorship survives independently.
    """
    relations = result.get("phd")
    if not isinstance(relations, list):
        return
    retained, additions = [], []
    for relation in relations:
        if not isinstance(relation, dict):
            retained.append(relation)
            continue
        student, adviser = str(relation.get("student")), str(relation.get("adviser"))
        if str(relation.get("source_record")) != student or relation.get("source_url") != f"https://inspirehep.net/authors/{student}" or adviser not in profiles:
            retained.append(relation)
            continue
        try:
            row = connection.execute("SELECT payload FROM source_records WHERE collection='authors' AND recid=? AND deleted=0", (student,)).fetchone()
            payload = json.loads(row[0]) if row else {}
            matches = [item for item in payload.get("advisors", []) if isinstance(item, dict)
                       and str(item.get("record")) == adviser and str(item.get("degree_type", "")).lower() == "phd"
                       and not item.get("hidden")]
        except (sqlite3.DatabaseError, ValueError, TypeError, AttributeError):
            matches = []
        if matches and all(_adviser_name_conflict(item.get("name"), profiles[adviser]) for item in matches):
            additions.append({"student": student, "adviser": adviser,
                "source_record": student, "source_url": relation["source_url"],
                "source_names": sorted({item["name"] for item in matches}),
                "profile_names": profiles[adviser],
                "reason": "native_adviser_name_conflicts_with_referenced_public_profile"})
        else:
            retained.append(relation)
    if additions:
        result["phd"] = retained
        coverage = result.setdefault("coverage", {})
        old = coverage.get("identity_phd_conflicts", [])
        merged = {(str(item.get("student")), str(item.get("adviser")), str(item.get("source_record"))): item
                  for item in old if isinstance(item, dict)} if isinstance(old, list) else {}
        merged.update({(item["student"], item["adviser"], item["source_record"]): item for item in additions})
        coverage["identity_phd_conflicts"] = [merged[key] for key in sorted(merged)]


def apply_identity_guard(snapshot: dict[str, Any], connection: sqlite3.Connection) -> dict[str, Any]:
    """Return a copy with explicit identity conflicts and local ambiguity removed.

    The first pass observes hard conflicts across every relevant normalized work.
    The second pass can then make a shorter otherwise-compatible initial form
    unresolved only when it is ambiguous with one of those observed conflicts.
    """
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be an object")
    result = copy.deepcopy(snapshot)
    works = result.get("works")
    if not isinstance(works, list):
        result["version"] = _version(result)
        return result
    profiles = _profile_people(result, connection)
    lifetimes = _profile_lifetimes(result, connection)
    _guard_phd_references(result, connection, profiles)
    inspected: list[tuple[dict[str, Any], set[str], dict[str, list[tuple[str, str]]]]] = []
    hard_by_person: dict[str, list[str]] = {}
    index = _occurrence_index(connection)
    for work in works:
        if not isinstance(work, dict) or not isinstance(work.get("authors"), list):
            continue
        source_ids = _source_ids(work)
        occurrences = _occurrences(index, source_ids)
        inspected.append((work, source_ids, occurrences))
        for person in work["authors"]:
            person_id = str(person)
            profile_names = profiles.get(person_id)
            if not profile_names:
                continue
            for _, source_name in occurrences.get(person_id, []):
                if (full_given_name_conflict(source_name, profile_names)
                        or hard_initial_conflict(source_name, profile_names)):
                    hard_by_person.setdefault(person_id, []).append(source_name)
    ambiguous_profiles = _ambiguous_initial_only_profiles(profiles, inspected)
    hard_additions: list[dict[str, Any]] = []
    full_name_additions: list[dict[str, Any]] = []
    ambiguity_additions: list[dict[str, Any]] = []
    reviews: list[dict[str, Any]] = []
    lifetime_reviews: list[dict[str, Any]] = []
    for work, source_ids, occurrences in inspected:
        for person in list(work.get("authors", [])):
            person_id = str(person)
            profile_names = profiles.get(person_id)
            if not profile_names:
                continue
            rows = occurrences.get(person_id, [])
            lifetime = lifetimes.get(person_id)
            work_year = work.get("year")
            lifetime_rows = []
            if (lifetime and isinstance(work_year, int) and not isinstance(work_year, bool)
                    and work_year > lifetime["death_year"] + 2):
                lifetime_rows = [
                    (source_id, source_name) for source_id, source_name in rows
                    if _initial_only_compatible_with_full_profile(source_name, profile_names)
                ]
            if lifetime_rows:
                _remove_author_occurrence(work, person_id)
                lifetime_reviews.extend({
                    "work_id": str(work.get("id")), "person": person_id,
                    "work_year": work_year, "death_date": lifetime["death_date"],
                    "source_profile_link": lifetime["source_profile_link"],
                    "source_id": source_id, "source_name": source_name,
                    "reason": "initial_only_authorship_more_than_two_years_after_profile_death_year",
                } for source_id, source_name in lifetime_rows)
                continue
            if person_id in ambiguous_profiles:
                _remove_author_occurrence(work, person_id)
                continue
            # Fully stated names take audit precedence over their initial
            # sequence, so ``Micheal`` versus ``Max`` is never reported as an
            # initial-only conflict.
            full_name_rows = [
                (source_id, source_name) for source_id, source_name in rows
                if full_given_name_conflict(source_name, profile_names)
            ]
            hard_rows = [] if full_name_rows else [
                (source_id, source_name) for source_id, source_name in rows
                if hard_initial_conflict(source_name, profile_names)
            ]
            ambiguity_rows = [] if full_name_rows or hard_rows else [
                (source_id, source_name)
                for source_id, source_name in rows
                if partial_initial_ambiguity(source_name, profile_names, hard_by_person.get(person_id, []))
            ]
            applied_rows = full_name_rows or hard_rows or ambiguity_rows
            if not applied_rows:
                continue
            # Even when exact identifier deduplication groups another source,
            # a disputed person is not eligible as a coauthor until review. The
            # raw grouped evidence remains in source_ids and coverage.
            _remove_author_occurrence(work, person_id)
            target = full_name_additions if full_name_rows else hard_additions if hard_rows else ambiguity_additions
            reason = (
                "all_public_profile_name_forms_have_incompatible_full_given_names"
                if full_name_rows else "all_public_profile_name_forms_have_incompatible_initials"
                if hard_rows else "partial_initial_matches_profile_and_observed_conflicting_occurrence"
            )
            for source_id, source_name in applied_rows:
                item: dict[str, Any] = {
                    "work_id": str(work.get("id")), "source_id": source_id, "person": person_id,
                    "source_name": source_name, "profile_names": profile_names, "reason": reason,
                }
                if ambiguity_rows:
                    item["conflicting_source_names"] = sorted(set(hard_by_person.get(person_id, [])))
                target.append(item)
            if len(source_ids) != 1 or len(rows) != 1:
                reviews.append({
                    "work_id": str(work.get("id")), "source_id": ",".join(sorted(source_ids)),
                    "source_ids": sorted(source_ids), "person": person_id,
                    "reason": "source_group_contains_disputed_identity_pending_review",
                })
    profile_additions = [
        {
            "person": person_id,
            "profile_names": profiles[person_id],
            "observed_full_name_forms": names,
            "reason": "initial_only_profile_has_incompatible_full_names_in_retrieved_corpus",
        }
        for person_id, names in sorted(ambiguous_profiles.items())
    ]
    if hard_additions or full_name_additions or ambiguity_additions or reviews or profile_additions or lifetime_reviews:
        coverage = result.get("coverage")
        if not isinstance(coverage, dict):
            coverage = {}
            result["coverage"] = coverage
        _merge_coverage(coverage, hard_additions, "identity_conflicts")
        _merge_coverage(coverage, full_name_additions, "identity_full_name_conflicts")
        _merge_coverage(coverage, ambiguity_additions, "identity_ambiguities")
        _merge_coverage(coverage, reviews, "identity_conflict_review")
        _merge_coverage(coverage, lifetime_reviews, "identity_lifetime_review")
        _merge_profile_coverage(coverage, profile_additions)
    result["version"] = _version(result)
    return result
