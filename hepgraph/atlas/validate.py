"""HEP Atlas validator — ontology v0.2 (amendment block A1-A22 + §2, §3, §9).

The validator turns a loaded :class:`hepgraph.atlas.load.Atlas` into a flat,
deterministic list of :class:`Finding`s.  Every check is a small generator
function with a docstring naming the amendment (or ontology section) it
enforces; :func:`validate_atlas` is the only dispatcher and it is the only
place that knows the order in which checks run.

Two design points worth knowing before reading on:

* **The loader is forgiving on purpose.**  ``load_atlas`` migrates v0.1 files
  to v0.2 *in memory* (it fills in ``hep_graph``, recomputes a source's
  ``rank``, invents a ``membership_history``, drops registry ``validated``
  flags, …).  Rules that must judge *what an author wrote* therefore read the
  raw JSON from disk a second time (:class:`_RawIndex`) instead of the
  migrated record.  Everything else reads the migrated model, which is what
  the build will consume.

* **One defect, one rule.**  Where a generic rule and a specific rule would
  both fire on the same key (``result.date_kind`` is both "a required enum"
  and "A16 requires a date kind"), the generic rule skips the key and the
  specific rule owns it.  The skips are collected in :data:`_SKIP_REQUIRED`
  and :data:`_SKIP_ENUM` so they are easy to audit.

Vocabulary (units, enums, ranks, date parsing, the A3 timeline) comes from
:mod:`hepgraph.atlas.schema`; nothing is re-derived here.  Three small tables
that the contract states but ``schema.py`` does not yet expose are defined
locally and flagged in the module comments below.

Runtime dependencies: the standard library only.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator

from . import load, schema

__all__ = [
    'Finding', 'validate_atlas', 'errors', 'warnings', 'infos', 'group_findings',
    'format_report', 'main',
]

ERROR = 'error'
WARNING = 'warning'
#: A10: a coverage backlog row naming an experiment that is not researched
#: yet is not a defect (that is the backlog's purpose) — informational only,
#: never build-failing and never counted as a warning either.
INFO = 'info'

# ---------------------------------------------------------------------------
# Tables the contract states but schema.py does not expose yet.
# (Reported to the orchestrator; they belong in schema.py eventually.)
# ---------------------------------------------------------------------------

#: A6 — the identity-evidence methods a `person:inspire-*` record may claim.
IDENTITY_EVIDENCE_METHODS: frozenset[str] = frozenset({
    'orcid', 'collaboration_page_link', 'inspire_profile_affiliation_match',
    'institution_page_link',
})

#: A20 — external id keys with a known URL shape.  ``{key: (template, bare)}``
#: where ``template`` renders the substring a record-level source URL must
#: contain and ``bare`` strips a value that was written as a full URL.
EXTERNAL_ID_URL_PATTERNS: dict[str, str] = {
    'inspire_institution': 'inspirehep.net/institutions/{value}',
    'inspire_experiment': 'inspirehep.net/experiments/{value}',
    'ror': 'ror.org/{value}',
}

#: Keys whose value is a §2.2 Date (or a sourced Date wrapper around one).
DATE_KEYS: frozenset[str] = frozenset({
    'start', 'end', 'date', 'accessed', 'verified_at', 'as_of', 'known_since',
    'known_until', 'evidence_date', 'last_checked', 'formation', 'announced',
    'published',
})

#: A dict carrying any of these keys is treated as a provenance-bearing node
#: (a sourced value, a quantity, coordinates, an interval or a sourced row).
PROVENANCE_MARKERS: tuple[str, ...] = ('sources', 'confidence', 'verified_at')

#: Dates inside one provenance node that `verified_at` must not predate (A12).
VALUE_DATE_KEYS: tuple[str, ...] = (
    'value', 'date', 'start', 'end', 'known_since', 'known_until', 'evidence_date',
)

#: (entity type, field) pairs the generic required-field check leaves alone
#: because a specific rule owns them.
_SKIP_REQUIRED: frozenset[tuple[str, str]] = frozenset({
    ('source', 'accessed'),      # source-missing-accessed (A18)
    ('result', 'date_kind'),     # result-date-kind (A16)
})
#: (entity type, field) pairs the generic enum check leaves alone.
_SKIP_ENUM: frozenset[tuple[str, str]] = frozenset({
    ('result', 'date_kind'),
})

#: A9 fields that must be an SList (a list of sourced values), not one value.
_SLIST_FIELDS: dict[str, tuple[str, ...]] = {
    'experiment': ('physics_goals', 'unique_capabilities'),
}


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Finding:
    """One validator verdict.

    ``pointer`` is an RFC-6901 JSON pointer into the record the finding is
    about (``''`` for a record-level or file-level finding); ``path`` is the
    file, relative to the data root, an operator has to open to fix it.
    """

    level: str            # 'error' | 'warning' | 'info'
    rule: str             # stable kebab-case rule id, e.g. 'baseline-distance'
    path: str             # e.g. 'experiments/demo.json'
    entity_id: str | None
    pointer: str          # RFC-6901 pointer inside the record
    message: str

    @property
    def sort_key(self) -> tuple[str, str, str, str]:
        return (self.path, self.pointer, self.rule, self.message)

    def __str__(self) -> str:  # pragma: no cover - convenience
        location = f'{self.path}{self.pointer}' if self.pointer else self.path
        return f'{self.level}: {self.rule}: {location}: {self.message}'


def _pointer(*tokens: Any) -> str:
    """Build an RFC-6901 pointer from path tokens (``''`` for the record)."""
    if not tokens:
        return ''
    parts = []
    for token in tokens:
        text = str(token).replace('~', '~0').replace('/', '~1')
        parts.append(text)
    return '/' + '/'.join(parts)


_JSON_PATH_RE = re.compile(r'([^.\[\]]+)|\[(\d+)\]')


def _pointer_from_json_path(json_path: str) -> str:
    """Turn ``schema.iter_reference_fields``' ``a.b[0].id`` into a pointer."""
    tokens: list[str] = []
    for name, index in _JSON_PATH_RE.findall(json_path or ''):
        tokens.append(name or index)
    return _pointer(*tokens)


# ---------------------------------------------------------------------------
# Raw files (what the author actually wrote, before load.py's migrations)
# ---------------------------------------------------------------------------

@dataclass
class _RawIndex:
    """The JSON exactly as it sits on disk, indexed the same way as the Atlas.

    ``records`` keeps a *list* per id so :func:`check_duplicate_ids` can see an
    id written twice; the loader would have dropped the second copy.
    """

    records: dict[str, list[tuple[str, dict]]] = field(default_factory=dict)
    memberships: dict[str, tuple[str, dict]] = field(default_factory=dict)
    coverage: list[tuple[str, int, dict]] = field(default_factory=list)

    def record(self, entity_id: str) -> dict | None:
        rows = self.records.get(entity_id)
        return rows[0][1] if rows else None


def _read_raw(root: Path) -> _RawIndex:
    """Read every data file again, unmigrated.  Unreadable files are ignored
    (``load_atlas`` already reported them as problems)."""
    raw = _RawIndex()
    if not root.is_dir():
        return raw
    for path in load.iter_json_files(root):
        relative = path.relative_to(root)
        if len(relative.parts) != 2:
            continue
        directory = relative.parts[0]
        try:
            payload = load.read_json(path)
        except (OSError, ValueError):
            continue
        rel = relative.as_posix()
        if directory == 'memberships':
            if isinstance(payload, dict) and isinstance(payload.get('collaboration_id'), str):
                raw.memberships.setdefault(payload['collaboration_id'], (rel, payload))
        elif directory == 'coverage':
            rows = payload if isinstance(payload, list) else [payload]
            for index, row in enumerate(rows):
                if isinstance(row, dict):
                    raw.coverage.append((rel, index, row))
        elif directory in schema.DIR_TO_TYPE:
            rows = payload if isinstance(payload, list) else [payload]
            for row in rows:
                if isinstance(row, dict) and isinstance(row.get('id'), str):
                    raw.records.setdefault(schema.canonical_id(row['id']), []).append((rel, row))
    return raw


# ---------------------------------------------------------------------------
# Validation context
# ---------------------------------------------------------------------------

@dataclass
class _Context:
    """Everything a check function needs, computed once."""

    atlas: Any
    build_date: _dt.date
    raw: _RawIndex
    selection: str                                  # build month, 'YYYY-MM'
    segments: dict[str, list[list]] = field(default_factory=dict)

    # -- lookups -----------------------------------------------------------
    def path_of(self, entity_id: str | None) -> str:
        return self.atlas.files.get(entity_id, '') if entity_id else ''

    def resolve(self, entity_id: Any) -> dict | None:
        """A6: resolve a reference, following `superseded_by` at most 8 hops."""
        if not isinstance(entity_id, str):
            return None
        seen: set[str] = set()
        current = schema.canonical_id(entity_id)
        for _ in range(8):
            if current in seen:
                return None
            seen.add(current)
            record = self.atlas.get(current)
            if record is None:
                return None
            successor = record.get('superseded_by')
            if not isinstance(successor, str) or successor == current:
                return record
            current = schema.canonical_id(successor)
        return None

    def source(self, source_id: Any) -> dict | None:
        record = self.resolve(source_id)
        return record if record is not None and schema.id_type(record.get('id', '')) == 'source' else None

    def state_segments(self, entity_id: str, record: dict) -> list[list]:
        """A3 `state_segments`, memoised (it costs one `state_at` per month)."""
        if entity_id not in self.segments:
            self.segments[entity_id] = schema.state_segments(record, self.build_date)
        return self.segments[entity_id]

    def active_months(self, entity_id: str, record: dict) -> set[int]:
        months: set[int] = set()
        for first, last, status, _certainty in self.state_segments(entity_id, record):
            if status == 'active':
                months.update(range(first, last + 1))
        return months


# ---------------------------------------------------------------------------
# Generic tree walkers
# ---------------------------------------------------------------------------

def _iter_dicts(node: Any, tokens: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], dict]]:
    """Yield ``(tokens, dict)`` for every dict in a record, root included."""
    if isinstance(node, dict):
        yield tokens, node
        for key, value in node.items():
            yield from _iter_dicts(value, tokens + (str(key),))
    elif isinstance(node, list):
        for index, item in enumerate(node):
            yield from _iter_dicts(item, tokens + (str(index),))


def _iter_provenance(record: dict) -> Iterator[tuple[tuple[str, ...], dict]]:
    """Every sourced value / quantity / coordinate / interval / sourced row.

    The record root is excluded: its `sources` is the A22 record-level
    identity citation, which has its own rule.
    """
    for tokens, node in _iter_dicts(record):
        if not tokens:
            continue
        if any(marker in node for marker in PROVENANCE_MARKERS):
            yield tokens, node


def _iter_quantities(record: dict) -> Iterator[tuple[tuple[str, ...], dict]]:
    for tokens, node in _iter_dicts(record):
        if tokens and schema.is_quantity(node):
            yield tokens, node


def _iter_dates(node: Any, tokens: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], Any]]:
    """Yield ``(tokens, date_value)`` for every §2.2 Date in a record.

    A key in :data:`DATE_KEYS` whose value is a *sourced date wrapper*
    (``{"value": "2005-06", "sources": [...]}``) yields the wrapped date at
    ``.../value`` and keeps walking the wrapper's own dates (``verified_at``).
    A Date *object* (``{"date": "2030", "planned": true}``) is yielded whole
    and not descended into, so its qualifiers are checked exactly once.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            child = tokens + (str(key),)
            if key in DATE_KEYS:
                if isinstance(value, dict) and 'date' not in value:
                    if value.get('value') is not None:
                        yield child + ('value',), value['value']
                    rest = {k: v for k, v in value.items() if k != 'value'}
                    yield from _iter_dates(rest, child)
                    continue
                if value is None:
                    continue
                yield child, value
                continue
            yield from _iter_dates(value, child)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            yield from _iter_dates(item, tokens + (str(index),))


def _intervals(record: Any) -> list[dict]:
    rows = (record or {}).get('intervals') if isinstance(record, dict) else None
    return [row for row in rows or [] if isinstance(row, dict)]


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ''


def _has_claim_evidence(node: Any) -> bool:
    """A15: a value carries claim-level evidence when it has a quote or a locator."""
    if not isinstance(node, dict):
        return False
    return bool(_text(node.get('quote')) or _text(node.get('locator')))


#: A20: a query parameter whose *name* starts with this is tracking noise
#: ("utm_source", "utm_campaign", …), never part of what a URL identifies.
_UTM_PARAM_RE = re.compile(r'(?i)^utm_[^=]*(=|$)')


def _normalise_url(url: Any) -> str:
    """A20/A7 URL normalisation: lower-case the scheme and host (never the
    path or query — those can be meaningfully case-sensitive and, much more
    importantly, are where two genuinely different sources are told apart:
    an INSPIRE API search and a geocoder lookup are identified by their
    query string, not merely their host), no `www.`, drop the fragment and
    any `utm_*` tracking parameters, keep the rest of the query string, no
    trailing `/` on a query-less path.

    A validator that folded the query string away would propose merging
    every INSPIRE literature search into one record and every geocoder
    lookup into one record — a P0-shaped data-corruption risk, not a
    cosmetic false positive, so this is deliberately conservative about
    what it throws away.
    """
    text = str(url or '').strip()
    text = text.split('#', 1)[0]                                  # drop the fragment
    match = re.match(r'^[a-zA-Z][a-zA-Z0-9+.\-]*://([^/?]*)(.*)$', text)
    if match:
        host, rest = match.group(1).lower(), match.group(2)
    else:
        host, rest = '', text
    if host.startswith('www.'):
        host = host[4:]
    path, _sep, query = rest.partition('?')
    path = path.rstrip('/')
    if query:
        kept = [param for param in query.split('&') if param and not _UTM_PARAM_RE.match(param)]
        rest = path + ('?' + '&'.join(kept) if kept else '')
    else:
        rest = path
    return host + rest


def _normalise_doi(doi: Any) -> str:
    # DOIs are case-insensitive by the DOI Handbook and never carry a
    # meaningful query string, so (unlike a general URL) the whole thing is
    # safely lower-cased for comparison.
    text = _normalise_url(doi).lower()
    for prefix in ('doi.org/', 'dx.doi.org/'):
        if text.startswith(prefix):
            text = text[len(prefix):]
    return text


def _normalise_spec_label(label: Any) -> str:
    """A21: `"Far detector mass"` -> `far_detector_mass` for range lookups."""
    text = re.sub(r'[^a-z0-9]+', '_', str(label or '').strip().lower())
    return text.strip('_')


def _bare_external_id(key: str, value: Any) -> str:
    """A20: the id itself, even when the author wrote the full URL."""
    text = str(value).strip()
    if key == 'ror':
        text = _normalise_url(text).lower()
        return text.rsplit('/', 1)[-1] if '/' in text else text
    return text


def _months_or_none(earlier: Any, later: Any) -> int | None:
    return schema.months_between(earlier, later)


# ===========================================================================
# §9 — structure
# ===========================================================================

def check_load_problems(ctx: _Context) -> Iterator[Finding]:
    """File-level defects the loader collected (§9): unreadable JSON, an id in
    the wrong directory, a filename that does not match its id, …"""
    for problem in ctx.atlas.problems:
        yield Finding(ERROR, 'load', problem.path, None, '', problem.message)


def check_duplicate_ids(ctx: _Context) -> Iterator[Finding]:
    """§9: one id may be written in exactly one place (read from disk, because
    the loader keeps only the first copy)."""
    for entity_id, rows in sorted(ctx.raw.records.items()):
        if len(rows) < 2:
            continue
        files = sorted({rel for rel, _ in rows})
        for rel, _record in rows:
            yield Finding(ERROR, 'duplicate-id', rel, entity_id, _pointer('id'),
                          f'id {entity_id!r} is written {len(rows)} times ({", ".join(files)})')


def _reference_rows(ctx: _Context) -> Iterator[tuple[str, str | None, dict]]:
    """(file path, entity id, record) for every record that may hold references.

    A1: a build-derived field (``detector.document_ids`` and the like) is
    stripped from the record before it is walked for references.  Authoring
    one is already reported once by :func:`check_derived_fields`; the build
    ignores whatever it names, so its contents must not also be checked as
    dangling references (that would be reporting the same defect twice, and
    under the wrong rule).  Coverage registry rows are handled separately by
    :func:`check_coverage_references`, since a backlog row naming an
    unresearched experiment is not a dangling reference at all.
    """
    for entity_type, entity_id, record in ctx.atlas.iter_entities():
        derived = schema.DERIVED_FIELDS.get(entity_type, ())
        if derived and any(name in record for name in derived):
            record = {key: value for key, value in record.items() if key not in derived}
        yield ctx.path_of(entity_id), entity_id, record
    for collaboration_id, payload in sorted(ctx.atlas.memberships.items()):
        yield ctx.atlas.membership_files.get(collaboration_id, ''), collaboration_id, payload


def check_references(ctx: _Context) -> Iterator[Finding]:
    """§9 / A6: every id under `*_id` / `*_ids` / `sources` / `roster_sources` /
    `distinct_from` must have a known prefix, a legal slug and a record —
    resolving through `superseded_by`."""
    for path, entity_id, record in _reference_rows(ctx):
        for json_path, reference in schema.iter_reference_fields(record):
            pointer = _pointer_from_json_path(json_path)
            canonical = schema.canonical_id(reference)
            if schema.id_type(canonical) is None:
                yield Finding(ERROR, 'unknown-id-prefix', path, entity_id, pointer,
                              f'{reference!r} has no known id prefix')
                continue
            if not schema.is_valid_id(canonical):
                yield Finding(ERROR, 'malformed-id', path, entity_id, pointer,
                              f'{reference!r} is not a lower-case `-` slug with a typed prefix')
                continue
            if ctx.resolve(canonical) is None:
                yield Finding(ERROR, 'dangling-reference', path, entity_id, pointer,
                              f'{reference!r} does not exist in the atlas')


def check_coverage_references(ctx: _Context) -> Iterator[Finding]:
    """§3.15 / A10: a coverage registry row names an experiment via `entity_id`
    (and its legacy twin `experiment_id`).

    The backlog's entire purpose is to name experiments nobody has researched
    yet, so a row whose `researched` is `"none"` naming an entity that does
    not exist is not a defect — it is an informational note that the entity
    is still queued.  A row that *claims* research happened (`"partial"` or
    `"full"`) for a missing entity is still a dangling reference and stays an
    error.
    """
    for row in ctx.atlas.coverage:
        path = row.get('_file', '')
        label = row.get('entity_id')
        researched = row.get('researched')
        for key in ('entity_id', 'experiment_id'):
            reference = row.get(key)
            if not isinstance(reference, str):
                continue
            pointer = _pointer(key)
            canonical = schema.canonical_id(reference)
            if schema.id_type(canonical) is None:
                yield Finding(ERROR, 'unknown-id-prefix', path, label, pointer,
                              f'{reference!r} has no known id prefix')
                continue
            if not schema.is_valid_id(canonical):
                yield Finding(ERROR, 'malformed-id', path, label, pointer,
                              f'{reference!r} is not a lower-case `-` slug with a typed prefix')
                continue
            if ctx.resolve(canonical) is None:
                if researched == 'none':
                    yield Finding(INFO, 'coverage-not-yet-researched', path, label, pointer,
                                  f'{reference!r} is not in the atlas yet; backlog entry '
                                  f'awaiting research')
                else:
                    yield Finding(ERROR, 'dangling-reference', path, label, pointer,
                                  f'{reference!r} does not exist in the atlas, but this row '
                                  f'claims researched={researched!r}')


def check_reference_types(ctx: _Context) -> Iterator[Finding]:
    """§9: a typed reference field must point at the right kind of entity
    (a `facility_id` may not hold a `site:` id)."""
    for entity_type, entity_id, record in ctx.atlas.iter_entities():
        path = ctx.path_of(entity_id)
        for name, spec in schema.ENTITY_FIELDS[entity_type].items():
            if spec.kind not in {'id', 'ids'} or spec.ref_type is None or name not in record:
                continue
            expected = (spec.ref_type,) if isinstance(spec.ref_type, str) else tuple(spec.ref_type)
            values = [record[name]] if spec.kind == 'id' else schema.ref_ids(record[name])
            for index, value in enumerate(values):
                if not isinstance(value, str):
                    continue
                target = ctx.resolve(value)
                if target is None:
                    continue  # dangling; reported by check_references
                actual = schema.id_type(target.get('id', ''))
                if actual not in expected:
                    pointer = _pointer(name) if spec.kind == 'id' else _pointer(name, index)
                    yield Finding(ERROR, 'reference-type-mismatch', path, entity_id, pointer,
                                  f'{name} expects {"/".join(expected)}, got {value!r} '
                                  f'which is a {actual}')


def _required_check(fields: dict[str, schema.FieldSpec], record: dict, path: str,
                    entity_id: str | None, prefix: tuple[str, ...],
                    skip: Iterable[str] = ()) -> Iterator[Finding]:
    skip = set(skip)
    for name, spec in fields.items():
        if not spec.required or name in skip:
            continue
        if name not in record:
            yield Finding(ERROR, 'missing-required-field', path, entity_id,
                          _pointer(*prefix, name), f'required field {name!r} is missing')
        elif record[name] is None and not spec.nullable:
            yield Finding(ERROR, 'null-required-field', path, entity_id,
                          _pointer(*prefix, name), f'required field {name!r} may not be null')


def check_required_fields(ctx: _Context) -> Iterator[Finding]:
    """§3: every `FieldSpec.required` field is present; a `nullable=False` one
    is not null.  `sources` is left to the A22 rule."""
    for entity_type, entity_id, record in ctx.atlas.iter_entities():
        skip = {'sources'} | {name for etype, name in _SKIP_REQUIRED if etype == entity_type}
        yield from _required_check(schema.ENTITY_FIELDS[entity_type], record,
                                   ctx.path_of(entity_id), entity_id, (), skip)
    for collaboration_id, payload in sorted(ctx.atlas.memberships.items()):
        path = ctx.atlas.membership_files.get(collaboration_id, '')
        yield from _required_check(schema.MEMBERSHIP_FILE_FIELDS, payload, path,
                                   collaboration_id, (), {'membership_history'})
        for index, row in enumerate(payload.get('members') or []):
            if isinstance(row, dict):
                yield from _required_check(schema.MEMBERSHIP_ROW_FIELDS, row, path,
                                           collaboration_id, ('members', index),
                                           {'evidence_class', 'sources'})
    for row in ctx.atlas.coverage:
        clean = {k: v for k, v in row.items() if k != '_file'}
        yield from _required_check(schema.COVERAGE_ROW_FIELDS, clean, row.get('_file', ''),
                                   row.get('entity_id'), ())


def _enum_finding(path: str, entity_id: str | None, tokens: tuple[Any, ...], value: Any,
                  allowed: Iterable[str], what: str) -> Finding | None:
    if value is None or value in set(allowed):
        return None
    return Finding(ERROR, 'unknown-enum-value', path, entity_id, _pointer(*tokens),
                   f'{what} {value!r} is not one of {sorted(set(allowed))}')


def check_enums(ctx: _Context) -> Iterator[Finding]:
    """§3-§6: every `enum` / `enums` field, plus the enums nested inside
    intervals, coordinates, placements, roles and evidence rows."""
    nested: dict[str, tuple[str, ...]] = {
        'status': schema.STATUSES,
        'confidence': schema.CONFIDENCES,
        'evidence_class': schema.EVIDENCE_CLASSES,
        'relation': schema.LINEAGE_RELATIONS,
    }
    for entity_type, entity_id, record in ctx.atlas.iter_entities():
        path = ctx.path_of(entity_id)
        for name, spec in schema.ENTITY_FIELDS[entity_type].items():
            if (entity_type, name) in _SKIP_ENUM or spec.enum is None or name not in record:
                continue
            if spec.kind == 'enum':
                finding = _enum_finding(path, entity_id, (name,), record[name], spec.enum, name)
                if finding is not None:
                    yield finding
            elif spec.kind == 'enums' and isinstance(record[name], list):
                for index, item in enumerate(record[name]):
                    finding = _enum_finding(path, entity_id, (name, index), item, spec.enum, name)
                    if finding is not None:
                        yield finding
        # Nested enums, wherever they appear in the record tree.
        for tokens, node in _iter_dicts(record):
            for key, allowed in nested.items():
                if key in node and not (len(tokens) == 0 and key in schema.ENTITY_FIELDS[entity_type]):
                    finding = _enum_finding(path, entity_id, tokens + (key,), node[key], allowed, key)
                    if finding is not None:
                        yield finding
            if 'kind' in node and tokens and tokens[-1] == 'coordinates':
                finding = _enum_finding(path, entity_id, tokens + ('kind',), node['kind'],
                                        schema.COORDINATE_KINDS, 'coordinate kind')
                if finding is not None:
                    yield finding
            if 'kind' in node and schema.is_interval(node):
                finding = _enum_finding(path, entity_id, tokens + ('kind',), node['kind'],
                                        schema.INTERVAL_KINDS, 'interval kind')
                if finding is not None:
                    yield finding
        for index, row in enumerate(record.get('placements') or []):
            if isinstance(row, dict):
                finding = _enum_finding(path, entity_id, ('placements', index, 'role'),
                                        row.get('role'), schema.PLACEMENT_ROLES, 'placement role')
                if finding is not None:
                    yield finding
        for index, row in enumerate(record.get('facility_roles') or []):
            if isinstance(row, dict):
                finding = _enum_finding(path, entity_id, ('facility_roles', index, 'role'),
                                        row.get('role'), schema.FACILITY_ROLES, 'facility role')
                if finding is not None:
                    yield finding
        for index, row in enumerate(record.get('leadership') or []):
            if isinstance(row, dict):
                finding = _enum_finding(path, entity_id, ('leadership', index, 'role'),
                                        row.get('role'), schema.LEADERSHIP_ROLES, 'leadership role')
                if finding is not None:
                    yield finding
        coverage = record.get('coverage')
        if isinstance(coverage, dict):
            for key, allowed in (('tier', schema.COVERAGE_TIERS), ('researched', schema.RESEARCHED_LEVELS)):
                finding = _enum_finding(path, entity_id, ('coverage', key), coverage.get(key),
                                        allowed, f'coverage {key}')
                if finding is not None:
                    yield finding
    for collaboration_id, payload in sorted(ctx.atlas.memberships.items()):
        path = ctx.atlas.membership_files.get(collaboration_id, '')
        for index, row in enumerate(payload.get('members') or []):
            if not isinstance(row, dict):
                continue
            for key, allowed in (('evidence_class', schema.EVIDENCE_CLASSES),
                                 ('confidence', schema.CONFIDENCES)):
                finding = _enum_finding(path, collaboration_id, ('members', index, key),
                                        row.get(key), allowed, key)
                if finding is not None:
                    yield finding
    for row in ctx.atlas.coverage:
        for name, spec in schema.COVERAGE_ROW_FIELDS.items():
            if spec.enum is None or name not in row:
                continue
            finding = _enum_finding(row.get('_file', ''), row.get('entity_id'), (name,),
                                    row[name], spec.enum, name)
            if finding is not None:
                yield finding


def check_coordinates(ctx: _Context) -> Iterator[Finding]:
    """§2.5 / §9: a site needs coordinates; latitude and longitude stay in
    range; a `headquarters` point may only mark an institution and a site that
    holds a detector must be a `detector` or `underground_lab` point."""
    detector_sites: set[str] = set()
    for _id, detector in sorted(ctx.atlas.by_type('detector').items()):
        for row in detector.get('placements') or []:
            if isinstance(row, dict) and isinstance(row.get('site_id'), str):
                detector_sites.add(schema.canonical_id(row['site_id']))

    for entity_type in ('site', 'institution'):
        for entity_id, record in sorted(ctx.atlas.by_type(entity_type).items()):
            path = ctx.path_of(entity_id)
            coordinates = record.get('coordinates')
            if not isinstance(coordinates, dict):
                if entity_type == 'site':
                    yield Finding(ERROR, 'site-missing-coordinates', path, entity_id,
                                  _pointer('coordinates'), 'a site must carry coordinates (§3.2)')
                continue
            latitude, longitude = coordinates.get('lat'), coordinates.get('lon')
            if not schema.is_number(latitude) or not -90 <= float(latitude) <= 90:
                yield Finding(ERROR, 'coordinates-out-of-range', path, entity_id,
                              _pointer('coordinates', 'lat'),
                              f'latitude {latitude!r} is not a number in [-90, 90]')
            if not schema.is_number(longitude) or not -180 <= float(longitude) <= 180:
                yield Finding(ERROR, 'coordinates-out-of-range', path, entity_id,
                              _pointer('coordinates', 'lon'),
                              f'longitude {longitude!r} is not a number in [-180, 180]')
            kind = coordinates.get('kind')
            pointer = _pointer('coordinates', 'kind')
            if entity_type == 'institution':
                if kind is not None and kind not in schema.INSTITUTION_COORDINATE_KINDS:
                    yield Finding(ERROR, 'coordinate-kind', path, entity_id, pointer,
                                  f'an institution point must be one of '
                                  f'{sorted(schema.INSTITUTION_COORDINATE_KINDS)}, got {kind!r}')
            else:
                if kind == 'headquarters':
                    yield Finding(ERROR, 'coordinate-kind', path, entity_id, pointer,
                                  'a `headquarters` point may only be used for institutions (§2.5)')
                if entity_id in detector_sites and kind not in schema.DETECTOR_COORDINATE_KINDS:
                    # A23: a campus-grade point may stand in for a detector
                    # hall only when the record says so — `confidence`
                    # approximate/uncertain and a note. Then the globe draws
                    # an approximate marker and the panel says "approximate
                    # location"; the alternative (relabelling a campus point
                    # `detector`) is the dishonest one.
                    admitted = (kind == 'campus'
                                and coordinates.get('confidence') in ('approximate', 'uncertain')
                                and _text(coordinates.get('note')))
                    if admitted:
                        yield Finding(WARNING, 'coordinate-kind-approximate', path, entity_id, pointer,
                                      'A23: a site holding a detector is placed at a campus-grade '
                                      'point; shown as approximate until a hall position is sourced')
                    else:
                        yield Finding(ERROR, 'coordinate-kind', path, entity_id, pointer,
                                      f'a site holding a detector needs a globe marker of kind '
                                      f'{sorted(schema.DETECTOR_COORDINATE_KINDS)}, got {kind!r} '
                                      f'(A23: `campus` is allowed only with `confidence` '
                                      f'approximate/uncertain and a `note`)')


def check_intervals(ctx: _Context) -> Iterator[Finding]:
    """§2.3 / A3 / A12: `hi(end) < lo(start)` (which also covers a terminal
    interval's `end`, when given — A3 supersedes §4's "a terminal status
    needs an `end`": terminal statuses are events, `end` is optional, and the
    only requirement is that it not be earlier than `start`), two same-label
    intervals that overlap, a non-terminal interval that starts after a
    terminal one, and the "start unknown" warning."""
    for _type, entity_id, record in ctx.atlas.iter_entities():
        path = ctx.path_of(entity_id)
        rows = _intervals(record)
        for index, row in enumerate(rows):
            pointer = _pointer('intervals', index)
            start, end = schema.lo(row.get('start')), schema.hi(row.get('end'))
            if start is not None and end is not None and end < start:
                yield Finding(ERROR, 'interval-end-before-start', path, entity_id, pointer,
                              f'interval ends {end.isoformat()} before it starts {start.isoformat()}')
            if 'start' in row and row.get('start') is None:
                yield Finding(WARNING, 'interval-start-unknown', path, entity_id,
                              _pointer('intervals', index, 'start'),
                              'start unknown; the UI will say so (§2.3)')
        # A3 says a terminal status is an event. One terminal row that also
        # carries an `end` is a whole lifetime folded into its final state:
        # the entity derives `completed` for every year it was running (PHENIX
        # read completed in 2005). Split it into the operating interval and
        # the terminal event.
        if len(rows) == 1 and rows[0].get('status') in schema.TERMINAL_STATUSES \
                and rows[0].get('end') is not None and rows[0].get('start') is not None \
                and schema.lo(rows[0].get('start')) != schema.lo(rows[0].get('end')):
            yield Finding(WARNING, 'collapsed-history', path, entity_id, _pointer('intervals', 0),
                          'A3: the only interval is terminal but spans a lifetime; the entity '
                          'derives its terminal state for every year it was operating — split '
                          'into an operating interval and the terminal event')
        for first in range(len(rows)):
            for second in range(first + 1, len(rows)):
                a, b = rows[first], rows[second]
                if a.get('label') != b.get('label'):
                    continue
                if schema.intervals_overlap(a, b):
                    yield Finding(ERROR, 'overlapping-intervals', path, entity_id,
                                  _pointer('intervals', second),
                                  f'intervals {first} and {second} share the label '
                                  f'{a.get("label")!r} and overlap (§2.3)')
        terminal_starts = [schema.lo(row.get('start')) for row in rows
                           if row.get('status') in schema.TERMINAL_STATUSES]
        terminal_starts = [day for day in terminal_starts if day is not None]
        if terminal_starts:
            earliest_terminal = min(terminal_starts)
            for index, row in enumerate(rows):
                if row.get('status') in schema.TERMINAL_STATUSES:
                    continue
                start = schema.lo(row.get('start'))
                if start is not None and start > earliest_terminal:
                    yield Finding(ERROR, 'non-terminal-after-terminal', path, entity_id,
                                  _pointer('intervals', index),
                                  f'a non-terminal interval starts {start.isoformat()}, after the '
                                  f'terminal interval that starts {earliest_terminal.isoformat()} '
                                  f'(A3: a revived programme is a new experiment id)')


def check_results(ctx: _Context) -> Iterator[Finding]:
    """§3.12 / §9 / A16: a result needs sources, a publication or an official
    url, a claim with evidence and a date kind; a `discovery` needs a
    significance and the claim keyword its `result_type` implies."""
    for entity_id, record in sorted(ctx.atlas.by_type('result').items()):
        path = ctx.path_of(entity_id)
        if not record.get('sources'):
            yield Finding(ERROR, 'result-missing-sources', path, entity_id, _pointer('sources'),
                          'a result must cite at least one source (§9)')
        if not record.get('publication') and not record.get('official_url'):
            yield Finding(ERROR, 'result-missing-publication', path, entity_id, '',
                          'a result needs either `publication` or `official_url` (§9)')
        result_type = record.get('result_type')
        if result_type == 'discovery':
            significance = record.get('significance')
            if not isinstance(significance, dict) or not _text(significance.get('value')):
                yield Finding(ERROR, 'discovery-without-significance', path, entity_id,
                              _pointer('significance'),
                              'a `discovery` must report the significance exactly as published (§9)')
        date_kind = record.get('date_kind')
        if date_kind is None:
            yield Finding(ERROR, 'result-date-kind', path, entity_id, _pointer('date_kind'),
                          'A16 requires `date_kind` (announcement | preprint | publication)')
        elif date_kind not in schema.RESULT_DATE_KINDS:
            yield Finding(ERROR, 'result-date-kind', path, entity_id, _pointer('date_kind'),
                          f'`date_kind` {date_kind!r} is not one of {list(schema.RESULT_DATE_KINDS)}')
        claim = record.get('claim')
        if not isinstance(claim, dict):
            yield Finding(ERROR, 'result-claim-missing', path, entity_id, _pointer('claim'),
                          'A16 requires a `claim` quoted from the publication or the '
                          "collaboration's own result page")
            continue
        if not _text(claim.get('quote')) and not _text(claim.get('locator')):
            yield Finding(ERROR, 'result-claim-evidence', path, entity_id, _pointer('claim'),
                          'A16: the claim needs a `quote` or a `locator`')
        if not claim.get('sources'):
            yield Finding(ERROR, 'result-claim-sources', path, entity_id, _pointer('claim', 'sources'),
                          'A16: the claim must cite the source it was read from')
        keyword = schema.RESULT_CLAIM_KEYWORDS.get(result_type)
        if keyword:
            haystacks = [_text(claim.get('quote')).lower()]
            cited = list(claim.get('sources') or []) + list(record.get('sources') or [])
            for source_id in cited:
                source = ctx.source(source_id)
                if source is not None:
                    haystacks.append(_text(source.get('title')).lower())
            if not any(keyword in text for text in haystacks):
                yield Finding(ERROR, 'result-claim-keyword', path, entity_id, _pointer('claim'),
                              f'A16: `result_type: {result_type}` requires {keyword!r} in the '
                              f'claim quote or in a cited source title')


def check_quantities(ctx: _Context) -> Iterator[Finding]:
    """§2.4 / A8 / A21: a quantity's `dimension` must be known, its `unit` must
    belong to that dimension, and `display` must agree with `value`."""
    for _type, entity_id, record in ctx.atlas.iter_entities():
        path = ctx.path_of(entity_id)
        for tokens, quantity in _iter_quantities(record):
            dimension = quantity.get('dimension')
            if dimension not in schema.UNITS:
                yield Finding(ERROR, 'quantity-dimension', path, entity_id,
                              _pointer(*tokens, 'dimension'),
                              f'unknown dimension {dimension!r} (§2.4)')
                continue
            if not schema.unit_allowed(dimension, quantity.get('unit')):
                yield Finding(ERROR, 'quantity-unit', path, entity_id, _pointer(*tokens, 'unit'),
                              f'unit {quantity.get("unit")!r} is not a {dimension} unit '
                              f'{list(schema.UNITS[dimension])}')
                continue
            value = schema.quantity_magnitude(quantity)
            shown = schema.display_magnitude(quantity)
            if value is None or shown is None or value == 0 or shown == 0:
                continue
            ratio = max(abs(shown / value), abs(value / shown))
            pointer = _pointer(*tokens, 'display')
            if ratio > schema.DISPLAY_FACTOR_ERROR:
                yield Finding(ERROR, 'display-value-mismatch', path, entity_id, pointer,
                              f'`display` {quantity.get("display")!r} and `value` differ by a '
                              f'factor {ratio:.3g} (> {schema.DISPLAY_FACTOR_ERROR:g}) (A21)')
            elif ratio > schema.DISPLAY_FACTOR_WARN:
                yield Finding(WARNING, 'display-value-drift', path, entity_id, pointer,
                              f'`display` {quantity.get("display")!r} and `value` differ by '
                              f'{(ratio - 1) * 100:.1f} % (A21 warns above 5 %)')


def check_sourced_values(ctx: _Context) -> Iterator[Finding]:
    """§2.1 / A17: every sourced value cites at least one source, explains a
    `confidence` other than `verified`, and backs a `verified` value with a
    source of derived rank <= 10."""
    for entity_type, entity_id, record in ctx.atlas.iter_entities():
        path = ctx.path_of(entity_id)
        for tokens, node in _iter_provenance(record):
            if entity_type == 'result' and tokens == ('claim',):
                continue  # owned by result-claim-sources
            yield from _provenance_findings(ctx, path, entity_id, tokens, node)
    for collaboration_id, payload in sorted(ctx.atlas.memberships.items()):
        path = ctx.atlas.membership_files.get(collaboration_id, '')
        for index, row in enumerate(payload.get('members') or []):
            if isinstance(row, dict):
                yield from _provenance_findings(ctx, path, collaboration_id, ('members', index), row)


def _provenance_findings(ctx: _Context, path: str, entity_id: str | None,
                         tokens: tuple[Any, ...], node: dict) -> Iterator[Finding]:
    """The §2.1 / A17 / A18 checks for one provenance-bearing node."""
    sources = node.get('sources')
    if not sources:
        yield Finding(ERROR, 'sourced-value-without-sources', path, entity_id,
                      _pointer(*tokens, 'sources'),
                      'a sourced value must cite at least one source (§2.1)')
    confidence = node.get('confidence')
    if confidence is not None and confidence != 'verified' and not _text(node.get('note')):
        yield Finding(ERROR, 'confidence-note-required', path, entity_id, _pointer(*tokens, 'note'),
                      f'`confidence: {confidence}` requires a `note` (§2.1)')
    resolved = [ctx.source(source_id) for source_id in sources or []]
    resolved = [source for source in resolved if source is not None]
    if confidence == 'verified' and resolved:
        ranks = [schema.source_rank(source.get('source_type')) for source in resolved]
        ranks = [rank for rank in ranks if rank is not None]
        if ranks and min(ranks) > schema.VERIFIED_MAX_RANK:
            yield Finding(ERROR, 'verified-source-rank', path, entity_id, _pointer(*tokens, 'sources'),
                          f'A17: a `verified` value needs a source of rank <= '
                          f'{schema.VERIFIED_MAX_RANK}; the best cited rank is {min(ranks)}')
    quote = _text(node.get('quote'))
    if quote and len(quote) > schema.QUOTE_MAX_CHARS:
        yield Finding(ERROR, 'quote-too-long', path, entity_id, _pointer(*tokens, 'quote'),
                      f'A15: a quote is at most {schema.QUOTE_MAX_CHARS} characters, this one '
                      f'is {len(quote)}')
    if quote and resolved and all(source.get('retrieval') in schema.NO_QUOTE_RETRIEVALS
                                  for source in resolved):
        yield Finding(ERROR, 'quote-on-summary-source', path, entity_id, _pointer(*tokens, 'quote'),
                      'A18: a quote may not rest on a `summary` retrieval alone')


def check_topics(ctx: _Context) -> Iterator[Finding]:
    """§3.10: the topic tree is at most three deep and has no cycles."""
    topics = ctx.atlas.by_type('topic')
    for topic_id, record in sorted(topics.items()):
        path = ctx.path_of(topic_id)
        parent = record.get('parent_id')
        depth = schema.topic_depth(topic_id, topics)
        if depth is None:
            if isinstance(parent, str) and parent in topics:
                yield Finding(ERROR, 'topic-cycle', path, topic_id, _pointer('parent_id'),
                              f'{topic_id} is part of a `parent_id` cycle (§3.10)')
            continue
        if depth > schema.TOPIC_MAX_DEPTH:
            yield Finding(ERROR, 'topic-depth', path, topic_id, _pointer('parent_id'),
                          f'topic depth {depth} exceeds the maximum of {schema.TOPIC_MAX_DEPTH} (§3.10)')


def check_documents(ctx: _Context) -> Iterator[Finding]:
    """§3.13: a document's `reference.url` is required."""
    for entity_id, record in sorted(ctx.atlas.by_type('document').items()):
        reference = record.get('reference')
        url = reference.get('url') if isinstance(reference, dict) else None
        if not _text(url):
            yield Finding(ERROR, 'document-missing-url', ctx.path_of(entity_id), entity_id,
                          _pointer('reference', 'url'), 'a document needs `reference.url` (§3.13)')


def check_people(ctx: _Context) -> Iterator[Finding]:
    """A6: person ids are `person:inspire-<digits>` or
    `person:unresolved-<slug>`; a resolved person's `external.inspire_author`
    matches the id and carries `identity_evidence`."""
    for entity_id, record in sorted(ctx.atlas.by_type('person').items()):
        path = ctx.path_of(entity_id)
        recid = schema.inspire_recid(entity_id)
        unresolved = bool(schema.PERSON_UNRESOLVED_RE.match(entity_id))
        if recid is None and not unresolved:
            yield Finding(ERROR, 'person-id-shape', path, entity_id, _pointer('id'),
                          'A6: a person id is `person:inspire-<recid>` or '
                          '`person:unresolved-<collab>-<institution>-<name>`')
            continue
        if recid is None:
            continue
        external = record.get('external') if isinstance(record.get('external'), dict) else {}
        author = external.get('inspire_author')
        if not isinstance(author, int) or isinstance(author, bool) or author != recid:
            yield Finding(ERROR, 'person-inspire-mismatch', path, entity_id,
                          _pointer('external', 'inspire_author'),
                          f'A6: `external.inspire_author` must be the numeric recid {recid}, '
                          f'got {author!r}')
        evidence = record.get('identity_evidence')
        pointer = _pointer('identity_evidence')
        if not isinstance(evidence, dict):
            yield Finding(ERROR, 'person-identity-evidence', path, entity_id, pointer,
                          'A6: every `person:inspire-*` carries `identity_evidence`')
            continue
        if evidence.get('method') not in IDENTITY_EVIDENCE_METHODS:
            yield Finding(ERROR, 'person-identity-evidence', path, entity_id,
                          _pointer('identity_evidence', 'method'),
                          f'A6: `identity_evidence.method` must be one of '
                          f'{sorted(IDENTITY_EVIDENCE_METHODS)}, got {evidence.get("method")!r}')
        if not evidence.get('sources'):
            yield Finding(ERROR, 'person-identity-evidence', path, entity_id,
                          _pointer('identity_evidence', 'sources'),
                          'A6: `identity_evidence` must cite the evidence it rests on')


def check_experiments(ctx: _Context) -> Iterator[Finding]:
    """§9: an experiment has a collaboration (or a note saying why not) and is
    somewhere — a `facility_roles` entry or a site."""
    detector_sites: dict[str, set[str]] = {}
    for _id, detector in sorted(ctx.atlas.by_type('detector').items()):
        for row in detector.get('placements') or []:
            if not isinstance(row, dict) or not isinstance(row.get('site_id'), str):
                continue
            for experiment_id in schema.ref_ids(detector.get('experiment_ids')):
                detector_sites.setdefault(schema.canonical_id(experiment_id), set()).add(row['site_id'])

    for entity_id, record in sorted(ctx.atlas.by_type('experiment').items()):
        path = ctx.path_of(entity_id)
        if not schema.ref_ids(record.get('collaboration_ids')):
            if not [note for note in record.get('notes') or [] if _text(note)]:
                yield Finding(ERROR, 'experiment-without-collaboration', path, entity_id,
                              _pointer('collaboration_ids'),
                              'an experiment needs a collaboration or a `notes` entry '
                              'explaining why it has none (§9)')
        has_facility = bool([row for row in record.get('facility_roles') or []
                             if isinstance(row, dict) and row.get('facility_id')])
        has_site = bool(schema.ref_ids(record.get('site_ids')) or detector_sites.get(entity_id))
        if not has_facility and not has_site:
            yield Finding(ERROR, 'experiment-without-facility-or-site', path, entity_id,
                          _pointer('facility_roles'),
                          'an experiment needs a `facility_roles` entry or a site (§9)')


# ===========================================================================
# A12 — dates and timeline
# ===========================================================================

def _date_rows(ctx: _Context) -> Iterator[tuple[str, str | None, dict]]:
    for _type, entity_id, record in ctx.atlas.iter_entities():
        yield ctx.path_of(entity_id), entity_id, record
    for collaboration_id, payload in sorted(ctx.atlas.memberships.items()):
        yield ctx.atlas.membership_files.get(collaboration_id, ''), collaboration_id, payload
    for row in ctx.atlas.coverage:
        yield row.get('_file', ''), row.get('entity_id'), {k: v for k, v in row.items() if k != '_file'}


def check_dates(ctx: _Context) -> Iterator[Finding]:
    """A12: date regex, calendar validity and year range; a future date needs
    `planned: true`; `approx` on a day-precision date warns."""
    for path, entity_id, record in _date_rows(ctx):
        for tokens, value in _iter_dates(record):
            pointer = _pointer(*tokens)
            try:
                parsed = schema.parse_date(value)
            except schema.DateError as exc:
                yield Finding(ERROR, 'date-invalid', path, entity_id, pointer, str(exc))
                continue
            if parsed is None:
                continue
            if parsed.lo() > ctx.build_date and not parsed.planned:
                yield Finding(ERROR, 'future-date-not-planned', path, entity_id, pointer,
                              f'A4/A12: {parsed.text} is after the build date '
                              f'{ctx.build_date.isoformat()} and is not marked `planned: true`')
            if parsed.approx and parsed.precision == 'day':
                yield Finding(WARNING, 'approx-day-precision', path, entity_id, pointer,
                              f'A12: `approx: true` on the day-precision date {parsed.text} is '
                              f'contradictory; widen the precision instead')


def check_verified_at_order(ctx: _Context) -> Iterator[Finding]:
    """A12: `verified_at` may not predate a non-planned date in the same value
    — an agent cannot have read a source before the event it reports."""
    for path, entity_id, record in _date_rows(ctx):
        nodes: list[tuple[tuple[str, ...], dict]] = list(_iter_provenance(record))
        for index, row in enumerate(record.get('members') or []):
            if isinstance(row, dict):
                nodes.append((('members', str(index)), row))
        for tokens, node in nodes:
            verified = schema.hi(node.get('verified_at'))
            if verified is None:
                continue
            for key in VALUE_DATE_KEYS:
                if key not in node or node[key] is None:
                    continue
                try:
                    parsed = schema.parse_date(node[key])
                except schema.DateError:
                    continue
                if parsed is None or parsed.planned:
                    continue
                if parsed.lo() > verified:
                    yield Finding(ERROR, 'verified-at-before-date', path, entity_id,
                                  _pointer(*tokens, 'verified_at'),
                                  f'A12: `verified_at` {node["verified_at"]!r} is before '
                                  f'{key} {parsed.text!r}, which is not marked `planned`')


def check_result_dates(ctx: _Context) -> Iterator[Finding]:
    """A12: a result may not be dated after the build date, and a non-milestone
    result may not predate every listed experiment's operation."""
    for entity_id, record in sorted(ctx.atlas.by_type('result').items()):
        path = ctx.path_of(entity_id)
        date_node = record.get('date')
        value = date_node.get('value') if isinstance(date_node, dict) else date_node
        try:
            parsed = schema.parse_date(value)
        except schema.DateError:
            continue
        if parsed is None:
            continue
        if parsed.lo() > ctx.build_date:
            yield Finding(ERROR, 'result-after-build-date', path, entity_id,
                          _pointer('date', 'value'),
                          f'A12: the result is dated {parsed.text}, after the build date '
                          f'{ctx.build_date.isoformat()}')
        if record.get('result_type') in schema.MILESTONE_RESULT_TYPES:
            continue
        operating: list[_dt.date] = []
        for experiment_id in schema.ref_ids(record.get('experiment_ids')):
            experiment = ctx.resolve(experiment_id)
            if experiment is None:
                continue
            starts = [schema.lo(row.get('start')) for row in _intervals(experiment)
                      if row.get('status') in {'commissioning', 'active'}]
            starts = [day for day in starts if day is not None]
            if starts:
                operating.append(min(starts))
        if operating and parsed.hi() < min(operating):
            yield Finding(ERROR, 'result-before-experiment', path, entity_id,
                          _pointer('date', 'value'),
                          f'A12: the result is dated {parsed.text}, before every listed '
                          f'experiment started operating ({min(operating).isoformat()})')


def check_membership_dates(ctx: _Context) -> Iterator[Finding]:
    """A5/A12: a membership row may not be dated past the file's `as_of`, and
    `known_since <= known_until <= as_of` must hold."""
    for collaboration_id, payload in sorted(ctx.atlas.memberships.items()):
        path = ctx.atlas.membership_files.get(collaboration_id, '')
        as_of = schema.hi(payload.get('as_of'))
        for index, row in enumerate(payload.get('members') or []):
            if not isinstance(row, dict):
                continue
            if as_of is not None:
                for key in ('start', 'end', 'known_until'):
                    day = schema.lo(row.get(key))
                    if day is not None and day > as_of:
                        yield Finding(ERROR, 'membership-date-after-as-of', path, collaboration_id,
                                      _pointer('members', index, key),
                                      f'A12: {key} {row[key]!r} is later than the roster '
                                      f'`as_of` {payload.get("as_of")!r}')
            since, until = schema.lo(row.get('known_since')), schema.hi(row.get('known_until'))
            if since is not None and until is not None and since > until:
                yield Finding(ERROR, 'membership-known-window', path, collaboration_id,
                              _pointer('members', index, 'known_since'),
                              f'A5: `known_since` {row["known_since"]!r} is after `known_until` '
                              f'{row["known_until"]!r}')


def _has_multiple_locations(entity_type: str, record: dict) -> bool:
    """True when the entity can legitimately have operated at more than one
    place — currently only a `detector` with more than one A2 `placements`
    row, the ontology's own model for a detector that relocates: it operates
    at its first site, is rebuilt (a fresh `construction` interval) at a
    second, and operates again."""
    if entity_type == 'detector':
        return len(record.get('placements') or []) > 1
    return False


def check_timeline_warnings(ctx: _Context) -> Iterator[Finding]:
    """A12 warnings: hull gaps, `active` before `construction`, an experiment
    that predates its host facility, an experiment operating with no beam, a
    stale `verified_at` and a `planned` date that has quietly passed."""
    for entity_type, entity_id, record in ctx.atlas.iter_entities():
        path = ctx.path_of(entity_id)
        rows = _intervals(record)
        if rows:
            for first, last in schema.hull_gaps(record, build_date=ctx.build_date):
                months = last - first + 1
                if months >= schema.MAX_HULL_GAP_MONTHS:
                    start = schema.month_to_date(first)
                    end = schema.month_to_date(last)
                    yield Finding(WARNING, 'hull-gap', path, entity_id, _pointer('intervals'),
                                  f'A12: {months} months with no interval '
                                  f'({start:%Y-%m} .. {end:%Y-%m}) inside the entity\'s lifetime')
            construction = [schema.lo(row.get('start')) for row in rows
                            if row.get('status') == 'construction']
            construction = [day for day in construction if day is not None]
            active = [schema.lo(row.get('start')) for row in rows if row.get('status') == 'active']
            active = [day for day in active if day is not None]
            # A12 (refined): only a genuine "shown running before it was built"
            # mistake — every `active` start earlier than every `construction`
            # start — and only when the entity has nowhere else it could have
            # been operating before this construction (a detector relocated
            # across more than one `placements` row is expected to look
            # exactly like this: active at the first site, a fresh
            # `construction` interval for the rebuild at the second, active
            # again — and must not be flagged).
            if (construction and active and max(active) < min(construction)
                    and not _has_multiple_locations(entity_type, record)):
                yield Finding(WARNING, 'active-before-construction', path, entity_id,
                              _pointer('intervals'),
                              f'A12: every `active` interval starts before the first '
                              f'`construction` interval ({min(construction).isoformat()}), '
                              f'latest {max(active).isoformat()}; a relocated or rebuilt '
                              f'detector (more than one A2 `placements` row) is expected to '
                              f'look like this and is exempted — otherwise check whether '
                              f'`active` and `construction` are in the right order')
        yield from _check_stale_verification(ctx, path, entity_id, record)
        yield from _check_planned_dates_passed(ctx, path, entity_id, record)
    yield from _check_experiment_timeline(ctx)


def _check_stale_verification(ctx: _Context, path: str, entity_id: str,
                              record: dict) -> Iterator[Finding]:
    """A12: build date - `verified_at` > 18 months warns (the value is stale)."""
    for tokens, node in _iter_provenance(record):
        age = _months_or_none(node.get('verified_at'), ctx.build_date)
        if age is not None and age > schema.MAX_VERIFIED_AGE_MONTHS:
            yield Finding(WARNING, 'stale-verified-at', path, entity_id,
                          _pointer(*tokens, 'verified_at'),
                          f'A12: last verified {age} months ago (> '
                          f'{schema.MAX_VERIFIED_AGE_MONTHS}); re-check the source')


def _check_planned_dates_passed(ctx: _Context, path: str, entity_id: str,
                                record: dict) -> Iterator[Finding]:
    """A12: a `planned` date that has passed with no non-planned interval
    covering it — the schedule was never confirmed against reality."""
    rows = _intervals(record)
    confirmed = [row for row in rows if not schema.is_planned(row.get('start'))]
    for tokens, value in _iter_dates(record):
        try:
            parsed = schema.parse_date(value)
        except schema.DateError:
            continue
        if parsed is None or not parsed.planned or parsed.hi() >= ctx.build_date:
            continue
        month = f'{parsed.hi().year:04d}-{parsed.hi().month:02d}'
        covered = any(schema.interval_covers(row, month, build_date=ctx.build_date)
                      for row in confirmed)
        if not covered:
            yield Finding(WARNING, 'planned-date-passed', path, entity_id, _pointer(*tokens),
                          f'A12: the planned date {parsed.text} has passed and no confirmed '
                          f'interval covers it')


def _check_experiment_timeline(ctx: _Context) -> Iterator[Finding]:
    """A12: an experiment older than its host facility, or `active` in a month
    when none of its accelerators or beamlines is."""
    for entity_id, record in sorted(ctx.atlas.by_type('experiment').items()):
        path = ctx.path_of(entity_id)
        starts = [schema.lo(row.get('start')) for row in _intervals(record)]
        starts = [day for day in starts if day is not None]
        if starts:
            for role in record.get('facility_roles') or []:
                if not isinstance(role, dict) or role.get('role') != 'host':
                    continue
                facility = ctx.resolve(role.get('facility_id'))
                if facility is None:
                    continue
                founded = [schema.lo(row.get('start')) for row in _intervals(facility)]
                founded = [day for day in founded if day is not None]
                if founded and min(starts) < min(founded):
                    yield Finding(WARNING, 'experiment-before-facility', path, entity_id,
                                  _pointer('intervals'),
                                  f'A12: the experiment starts {min(starts).isoformat()}, before '
                                  f'its host facility {facility.get("id")} '
                                  f'({min(founded).isoformat()})')
        beams: set[int] = set()
        for field_name in ('accelerator_ids', 'beamline_ids'):
            for reference in schema.ref_ids(record.get(field_name)):
                beam = ctx.resolve(reference)
                if beam is not None:
                    beams |= ctx.active_months(beam.get('id', reference), beam)
        uncovered = sorted(ctx.active_months(entity_id, record) - beams)
        if uncovered:
            first = schema.month_to_date(uncovered[0])
            yield Finding(WARNING, 'experiment-without-active-beam', path, entity_id,
                          _pointer('intervals'),
                          f'A12: the experiment is `active` in {first:%Y-%m} but no listed '
                          f'accelerator or beamline is')


# ===========================================================================
# A10 / A11 / A15 / A18 / A19 / A22
# ===========================================================================

def _terminal_status_already_reached(record: dict, build_date: _dt.date) -> str | None:
    """A10 (amended reading): the status of the earliest terminal interval
    whose `start` is at or before the build date, or None if there is none.

    A3's existence hull ends at `lo(earliest terminal start)`, so once the
    build date is past that point `state_at` legitimately answers "absent"
    (`None`) — the entity's presence really has ended.  The authored
    `status` for a terminal entity is correctly the terminal status itself
    (e.g. `decommissioned`), not the hull's "absent" answer, so that is what
    A10 must compare it against.  Picking the *earliest* qualifying terminal
    interval matches the interval `existence_hull` itself uses as the hull
    boundary, so the two stay consistent with each other.
    """
    candidates: list[tuple[_dt.date, str]] = []
    for row in _intervals(record):
        row_status = row.get('status')
        if row_status not in schema.TERMINAL_STATUSES:
            continue
        start = schema.lo(row.get('start'))
        if start is not None and start <= build_date:
            candidates.append((start, row_status))
    if not candidates:
        return None
    candidates.sort(key=lambda pair: pair[0])
    return candidates[0][1]


def check_status_matches_state(ctx: _Context) -> Iterator[Finding]:
    """A10 (amended): an entity's `status` must equal the status of a
    terminal interval already reached by the build date (§4: terminal
    statuses are events, and A3's existence hull ends exactly there, so
    `state_at` answering "absent" past it does not mean `status` is wrong);
    failing that, it must equal the ordinary A3 state derived from its
    intervals at the build date's month."""
    for entity_type, entity_id, record in ctx.atlas.iter_entities():
        if 'status' not in schema.ENTITY_FIELDS[entity_type]:
            continue
        status = record.get('status')
        terminal = _terminal_status_already_reached(record, ctx.build_date)
        if terminal is not None:
            derived = terminal
        else:
            state = schema.state_at(record, ctx.selection, build_date=ctx.build_date)
            derived = state['status'] if state else None
        if status is None and derived is None:
            continue
        if status == derived:
            continue
        yield Finding(ERROR, 'status-not-derived-state', ctx.path_of(entity_id), entity_id,
                      _pointer('status'),
                      f'A10: `status` is {status!r} but the state derived from the intervals at '
                      f'{ctx.selection} is {derived!r}')


def check_schema_tag(ctx: _Context) -> Iterator[Finding]:
    """A11: a `schema` key, when present, must read `hep-atlas/0.2`."""
    for entity_id, rows in sorted(ctx.raw.records.items()):
        for path, record in rows:
            tag = record.get('schema')
            if tag is not None and tag != schema.SCHEMA_TAG:
                yield Finding(ERROR, 'schema-tag', path, entity_id, _pointer('schema'),
                              f'A11: `schema` must be {schema.SCHEMA_TAG!r}, got {tag!r}')
    for _collaboration_id, (path, payload) in sorted(ctx.raw.memberships.items()):
        tag = payload.get('schema')
        if tag is not None and tag != schema.SCHEMA_TAG:
            yield Finding(ERROR, 'schema-tag', path, None, _pointer('schema'),
                          f'A11: `schema` must be {schema.SCHEMA_TAG!r}, got {tag!r}')


def check_claim_evidence(ctx: _Context) -> Iterator[Finding]:
    """A15: coordinates, `key_specs` quantities, baselines, a result's `date`
    and `significance`, official membership rows, a collaboration's
    `formation` and month/day-precision interval bounds each need a `quote`
    or a `locator`."""
    def demand(path: str, entity_id: str | None, tokens: tuple[Any, ...], node: Any,
               what: str) -> Iterator[Finding]:
        if isinstance(node, dict) and not _has_claim_evidence(node):
            yield Finding(ERROR, 'claim-evidence-required', path, entity_id, _pointer(*tokens),
                          f'A15: {what} needs a `quote` or a `locator`')

    for entity_type, entity_id, record in ctx.atlas.iter_entities():
        path = ctx.path_of(entity_id)
        if entity_type in {'site', 'institution'}:
            yield from demand(path, entity_id, ('coordinates',), record.get('coordinates'),
                              'coordinates')
        if entity_type == 'experiment':
            for index, row in enumerate(record.get('key_specs') or []):
                if isinstance(row, dict):
                    yield from demand(path, entity_id, ('key_specs', index, 'quantity'),
                                      row.get('quantity'), 'a key spec quantity')
        if entity_type == 'beamline':
            for index, row in enumerate(record.get('baselines') or []):
                if isinstance(row, dict):
                    yield from demand(path, entity_id, ('baselines', index, 'distance'),
                                      row.get('distance'), 'a baseline distance')
        if entity_type == 'result':
            yield from demand(path, entity_id, ('date',), record.get('date'), "a result's date")
            yield from demand(path, entity_id, ('significance',), record.get('significance'),
                              "a result's significance")
        if entity_type == 'collaboration':
            yield from demand(path, entity_id, ('formation',), record.get('formation'),
                              "a collaboration's formation date")
        for index, row in enumerate(_intervals(record)):
            precise = False
            for key in ('start', 'end'):
                try:
                    parsed = schema.parse_date(row.get(key))
                except schema.DateError:
                    continue
                if parsed is not None and parsed.precision in {'month', 'day'}:
                    precise = True
            if precise:
                yield from demand(path, entity_id, ('intervals', index), row,
                                  'an interval with month or day precision')
    for collaboration_id, payload in sorted(ctx.atlas.memberships.items()):
        path = ctx.atlas.membership_files.get(collaboration_id, '')
        for index, row in enumerate(payload.get('members') or []):
            if isinstance(row, dict) and row.get('evidence_class') in schema.OFFICIAL_EVIDENCE_CLASSES:
                yield from demand(path, collaboration_id, ('members', index), row,
                                  f'a membership row with evidence class {row["evidence_class"]}')


def check_coordinate_sources(ctx: _Context) -> Iterator[Finding]:
    """A17: `detector` / `underground_lab` coordinates may not rest on a
    geocoder or on rank >= 8 sources alone, and a geocoder may only back a
    `campus` or `headquarters` point."""
    for entity_type in ('site', 'institution'):
        for entity_id, record in sorted(ctx.atlas.by_type(entity_type).items()):
            coordinates = record.get('coordinates')
            if not isinstance(coordinates, dict):
                continue
            path = ctx.path_of(entity_id)
            pointer = _pointer('coordinates', 'sources')
            kind = coordinates.get('kind')
            resolved = [ctx.source(source_id) for source_id in coordinates.get('sources') or []]
            resolved = [source for source in resolved if source is not None]
            if not resolved:
                continue
            if kind in schema.STRICT_COORDINATE_KINDS:
                strong = [source for source in resolved
                          if source.get('source_type') != 'geocoder'
                          and (schema.source_rank(source.get('source_type')) or 99) < 8]
                if not strong:
                    yield Finding(ERROR, 'coordinate-source-quality', path, entity_id, pointer,
                                  f'A17: {kind} coordinates may not rely solely on a geocoder or '
                                  f'on rank >= 8 sources')
            for source in resolved:
                if source.get('source_type') == 'geocoder' and kind not in schema.GEOCODER_COORDINATE_KINDS:
                    yield Finding(ERROR, 'geocoder-coordinate-kind', path, entity_id, pointer,
                                  f'A17: a geocoder may only back '
                                  f'{sorted(schema.GEOCODER_COORDINATE_KINDS)} coordinates, '
                                  f'not {kind!r} ({source.get("id")})')


def check_sources(ctx: _Context) -> Iterator[Finding]:
    """A18/A22: `accessed` is required, a `failed` retrieval may not be cited,
    a source nobody cites warns, and an authored `rank` that disagrees with the
    derived one warns."""
    cited: set[str] = set()
    for _path, _entity_id, record in _reference_rows(ctx):
        for _json_path, reference in schema.iter_reference_fields(record):
            canonical = schema.canonical_id(reference)
            if schema.id_type(canonical) == 'source':
                cited.add(canonical)

    for entity_id, record in sorted(ctx.atlas.by_type('source').items()):
        path = ctx.path_of(entity_id)
        if not _text(record.get('accessed')):
            yield Finding(ERROR, 'source-missing-accessed', path, entity_id, _pointer('accessed'),
                          'A18: `accessed` (the day an agent read the source) is required')
        if record.get('retrieval') in schema.UNCITABLE_RETRIEVALS and entity_id in cited:
            yield Finding(ERROR, 'failed-source-cited', path, entity_id, _pointer('retrieval'),
                          'A18: a source whose retrieval `failed` may not be cited')
        if entity_id not in cited:
            yield Finding(WARNING, 'uncited-source', path, entity_id, '',
                          'A22: this source is cited by nothing; drop it or cite it')
        raw = ctx.raw.record(entity_id)
        derived = schema.source_rank(record.get('source_type'))
        if raw is not None and 'rank' in raw and derived is not None and raw['rank'] != derived:
            yield Finding(WARNING, 'source-rank-mismatch', path, entity_id, _pointer('rank'),
                          f'A7/A18: `rank` is derived from `source_type`; the file says '
                          f'{raw["rank"]!r}, the table says {derived}')


def _evidence_rows(ctx: _Context) -> Iterator[tuple[str, str | None, tuple[Any, ...], dict, bool]]:
    """Every row that carries an evidence class: membership file rows and the
    `memberships` / `affiliations` rows of a person (A19)."""
    for collaboration_id, payload in sorted(ctx.atlas.memberships.items()):
        path = ctx.atlas.membership_files.get(collaboration_id, '')
        for index, row in enumerate(payload.get('members') or []):
            if isinstance(row, dict):
                yield path, collaboration_id, ('members', index), row, False
    for entity_id, record in sorted(ctx.atlas.by_type('person').items()):
        path = ctx.path_of(entity_id)
        for name in ('memberships', 'affiliations'):
            for index, row in enumerate(record.get(name) or []):
                if isinstance(row, dict):
                    yield path, entity_id, (name, index), row, True


def check_evidence_classes(ctx: _Context) -> Iterator[Finding]:
    """A19: evidence class <-> source type consistency, a required
    `evidence_class`, `derived` forbidden on people, and the
    `publication_affiliation_*` date rules."""
    as_of_by_collaboration = {
        collaboration_id: payload.get('as_of')
        for collaboration_id, payload in ctx.atlas.memberships.items()
    }
    for path, entity_id, tokens, row, is_person in _evidence_rows(ctx):
        evidence_class = row.get('evidence_class')
        if evidence_class is None:
            yield Finding(ERROR, 'evidence-class-missing', path, entity_id,
                          _pointer(*tokens, 'evidence_class'),
                          'A19: every membership / affiliation row states its `evidence_class`')
            continue
        if is_person and evidence_class in schema.PERSON_FORBIDDEN_EVIDENCE_CLASSES:
            yield Finding(ERROR, 'person-derived-evidence', path, entity_id,
                          _pointer(*tokens, 'evidence_class'),
                          f'A19: `{evidence_class}` is forbidden on a person row '
                          f'(institution rows only)')
        allowed = schema.EVIDENCE_SOURCE_TYPES.get(evidence_class)
        if allowed:
            types = []
            for source_id in row.get('sources') or []:
                source = ctx.source(source_id)
                if source is not None:
                    types.append(source.get('source_type'))
            if types and not any(source_type in allowed for source_type in types):
                yield Finding(ERROR, 'evidence-source-type', path, entity_id,
                              _pointer(*tokens, 'sources'),
                              f'A19: `{evidence_class}` must be backed by one of '
                              f'{sorted(allowed)}; the row cites {sorted(set(types))}')
        if evidence_class in schema.EVIDENCE_DATE_REQUIRED and not row.get('evidence_date'):
            yield Finding(ERROR, 'evidence-date-required', path, entity_id,
                          _pointer(*tokens, 'evidence_date'),
                          f'A19: `{evidence_class}` requires an `evidence_date`')
        if evidence_class == 'publication_affiliation_current' and row.get('evidence_date'):
            as_of = as_of_by_collaboration.get(entity_id) if not is_person else None
            horizon = schema.hi(as_of) if as_of else ctx.build_date
            months = _months_or_none(row.get('evidence_date'), horizon)
            limit = schema.PUBLICATION_CURRENT_MAX_YEARS * 12
            if months is not None and months > limit:
                yield Finding(ERROR, 'publication-affiliation-stale', path, entity_id,
                              _pointer(*tokens, 'evidence_date'),
                              f'A19: `publication_affiliation_current` is {months} months old '
                              f'(limit {limit}); use `publication_affiliation_historical`')
        if evidence_class == 'publication_affiliation_historical':
            if row.get('end') is None and row.get('known_until') is None:
                yield Finding(ERROR, 'publication-affiliation-historical-open', path, entity_id,
                              _pointer(*tokens),
                              'A19: `publication_affiliation_historical` requires an `end` or a '
                              '`known_until`')


def check_membership_files(ctx: _Context) -> Iterator[Finding]:
    """A5/A12: `membership_history` is required (read from disk, because the
    loader defaults it), and an open-ended row on a finished collaboration
    warns."""
    for collaboration_id, payload in sorted(ctx.atlas.memberships.items()):
        path = ctx.atlas.membership_files.get(collaboration_id, '')
        raw = ctx.raw.memberships.get(collaboration_id)
        authored = raw[1].get('membership_history') if raw else payload.get('membership_history')
        if authored not in schema.MEMBERSHIP_HISTORY_LEVELS:
            yield Finding(ERROR, 'membership-history', path, collaboration_id,
                          _pointer('membership_history'),
                          f'A5: `membership_history` must be one of '
                          f'{list(schema.MEMBERSHIP_HISTORY_LEVELS)}, got {authored!r}')
        collaboration = ctx.resolve(collaboration_id)
        terminal = _is_terminal(ctx, collaboration) if collaboration else False
        for index, row in enumerate(payload.get('members') or []):
            if not isinstance(row, dict):
                continue
            if terminal and row.get('end') is None:
                yield Finding(WARNING, 'membership-open-end-terminal-collaboration', path,
                              collaboration_id, _pointer('members', index, 'end'),
                              'A12: the collaboration has finished; an open-ended membership is '
                              'clamped at the build date')
            institution = ctx.resolve(row.get('institution_id'))
            if institution is not None and schema.coordinates_of(institution) is None:
                yield Finding(WARNING, 'membership-institution-without-coordinates', path,
                              collaboration_id, _pointer('members', index, 'institution_id'),
                              f'A12: {row.get("institution_id")} has no coordinates; its dot is '
                              f'not drawn (not a failure)')


def _is_terminal(ctx: _Context, record: dict | None) -> bool:
    """True when an entity has finished: its derived state at the build date is
    terminal, or it has left the timeline having ended in a terminal status."""
    if not isinstance(record, dict):
        return False
    state = schema.state_at(record, ctx.selection, build_date=ctx.build_date)
    if state is not None:
        return state['status'] in schema.TERMINAL_STATUSES
    return any(row.get('status') in schema.TERMINAL_STATUSES for row in _intervals(record))


def check_record_sources(ctx: _Context) -> Iterator[Finding]:
    """A22: record-level `sources` is required non-empty on every entity type
    that has the field (a `src:` record cites itself; a result has its own rule)."""
    for entity_type, entity_id, record in ctx.atlas.iter_entities():
        if entity_type in {'source', 'result'}:
            continue
        if 'sources' not in schema.ENTITY_FIELDS[entity_type]:
            continue
        if not record.get('sources'):
            yield Finding(ERROR, 'record-sources-required', ctx.path_of(entity_id), entity_id,
                          _pointer('sources'),
                          'A22: record-level `sources` is required and non-empty')


def check_derived_fields(ctx: _Context) -> Iterator[Finding]:
    """A1/A10: a build-derived field authored in a data file (read from disk;
    the loader fills several of them in itself)."""
    for entity_id, rows in sorted(ctx.raw.records.items()):
        entity_type = schema.id_type(entity_id)
        if entity_type is None:
            continue
        for path, record in rows:
            for name in schema.DERIVED_FIELDS.get(entity_type, ()):  # A1
                if name in record:
                    yield Finding(WARNING, 'derived-field', path, entity_id, _pointer(name),
                                  f'A1: `{name}` is derived at build time; the build ignores '
                                  f'whatever is written here')
            coverage = record.get('coverage')
            if isinstance(coverage, dict):
                for name in schema.COVERAGE_DERIVED_FIELDS:
                    if name in coverage:
                        yield Finding(WARNING, 'coverage-derived-field', path, entity_id,
                                      _pointer('coverage', name),
                                      f'A10: `coverage.{name}` is a build output, not an '
                                      f'authored field')
    for path, index, row in ctx.raw.coverage:
        for name in schema.COVERAGE_DERIVED_FIELDS:
            if name in row:
                yield Finding(WARNING, 'coverage-derived-field', path, row.get('entity_id'),
                              _pointer(index, name),
                              f'A10: `{name}` is a build output; the registry keeps planning '
                              f'fields only')


def check_slist_shapes(ctx: _Context) -> Iterator[Finding]:
    """A9: `physics_goals`, `unique_capabilities` and `subsystems[].description`
    are SLists (a list of sourced values), not one sourced value."""
    for entity_type, entity_id, record in ctx.atlas.iter_entities():
        path = ctx.path_of(entity_id)
        for name in _SLIST_FIELDS.get(entity_type, ()):
            value = record.get(name)
            if isinstance(value, dict):
                yield Finding(WARNING, 'sourced-list-shape', path, entity_id, _pointer(name),
                              f'A9: `{name}` is an SList (a list of sourced values); accepted '
                              f'as one value, but please split it')
        if entity_type == 'detector':
            for index, row in enumerate(record.get('subsystems') or []):
                if isinstance(row, dict) and isinstance(row.get('description'), dict):
                    yield Finding(WARNING, 'sourced-list-shape', path, entity_id,
                                  _pointer('subsystems', index, 'description'),
                                  'A9: `subsystems[].description` is an SList (a list of '
                                  'sourced values)')


# ===========================================================================
# A20 — duplicates
# ===========================================================================

def _external_pairs(record: dict) -> list[tuple[str, str]]:
    """(bucket, normalised value) for every external identifier on a record."""
    pairs: list[tuple[str, str]] = []
    external = record.get('external')
    if isinstance(external, dict):
        for key, value in external.items():
            if value in (None, '', [], {}):
                continue
            pairs.append((f'external.{key}', str(value).strip().lower()))
    for container in ('publication', 'reference'):
        block = record.get(container)
        if not isinstance(block, dict):
            continue
        for key in ('doi', 'arxiv', 'inspire'):
            value = block.get(key)
            if value in (None, '', [], {}):
                continue
            normalised = _normalise_doi(value) if key == 'doi' else str(value).strip().lower()
            pairs.append((key, normalised))
    return pairs


def check_duplicate_externals(ctx: _Context) -> Iterator[Finding]:
    """A20/§9: two entities of one type may not share an `external.*` value, a
    DOI, an arXiv id, an INSPIRE recid or an ORCID."""
    for entity_type in schema.ENTITY_TYPES:
        index: dict[tuple[str, str], list[str]] = {}
        for entity_id, record in sorted(ctx.atlas.by_type(entity_type).items()):
            for pair in _external_pairs(record):
                index.setdefault(pair, []).append(entity_id)
        for (bucket, value), ids in sorted(index.items()):
            if len(ids) < 2:
                continue
            for entity_id in ids:
                others = [other for other in ids if other != entity_id]
                yield Finding(ERROR, 'duplicate-external-id', ctx.path_of(entity_id), entity_id, '',
                              f'A20: {bucket} {value!r} is also on {", ".join(sorted(others))}')


#: A20 (amended): a normalised alias shorter than this is an initialism
#: routinely reused by unrelated institutions ("CU", "ISU", "NU", "IFT") and
#: is ignored entirely for the cross-record collision check below; it can
#: still fail the per-record checks (an alias equal to the record's own
#: name, or repeated within one record).
MIN_ALIAS_COLLISION_LENGTH = 5


def _mutually_distinct(table: dict[str, dict], entity_id: str, others: Iterable[str]) -> bool:
    """A20: true when `entity_id` and every one of `others` name each other
    in `distinct_from` — the escape hatch for a deliberate name collision."""
    distinct = {schema.canonical_id(other) for other in table[entity_id].get('distinct_from') or []}
    return all(
        other in distinct
        and entity_id in {schema.canonical_id(x) for x in table[other].get('distinct_from') or []}
        for other in others)


def check_duplicate_names(ctx: _Context) -> Iterator[Finding]:
    """A20 (amended): a normalised **name**-vs-name collision, or a name
    colliding with another record's long alias, is build-failing, unless
    both records name each other in `distinct_from`; plus an alias equal to
    the record's own name, and a repeated alias (both per-record, so length
    does not excuse them).

    Two records merely sharing a long alias — neither's own name — is
    reported as informational only.  A short alias (under
    :data:`MIN_ALIAS_COLLISION_LENGTH` normalised characters) is ignored for
    all of the cross-record comparisons: "CU", "ISU", "NU" and "IFT" are
    routinely reused by unrelated institutions, and asking every ROR-derived
    record to cross-list every homonym in `distinct_from` is not a real fix.
    A long alias still catches the case that matters, "Super-K" duplicating
    "Super-Kamiokande".
    """
    for entity_type in schema.ENTITY_TYPES:
        table = ctx.atlas.by_type(entity_type)
        names: dict[str, list[str]] = {}
        long_aliases: dict[str, list[str]] = {}
        for entity_id, record in sorted(table.items()):
            path = ctx.path_of(entity_id)
            own = schema.normalise_name(record.get('name'))
            seen: set[str] = set()
            for position, alias in enumerate(record.get('aliases') or []):
                normalised = schema.normalise_name(alias)
                if not normalised:
                    continue
                if normalised == own:
                    yield Finding(ERROR, 'alias-equals-name', path, entity_id,
                                  _pointer('aliases', position),
                                  f'A20: alias {alias!r} repeats the record\'s own name; remove '
                                  f'this alias; it differs from the name only in case or '
                                  f'punctuation')
                if normalised in seen:
                    yield Finding(ERROR, 'duplicate-alias', path, entity_id,
                                  _pointer('aliases', position),
                                  f'A20: alias {alias!r} is listed twice')
                seen.add(normalised)
            if own:
                names.setdefault(own, []).append(entity_id)
            for alias_name in seen:
                if len(alias_name) >= MIN_ALIAS_COLLISION_LENGTH:
                    long_aliases.setdefault(alias_name, []).append(entity_id)

        # name vs. name.
        for name, ids in sorted(names.items()):
            unique = sorted(set(ids))
            if len(unique) < 2:
                continue
            for entity_id in unique:
                others = [other for other in unique if other != entity_id]
                if _mutually_distinct(table, entity_id, others):
                    continue
                yield Finding(ERROR, 'duplicate-name', ctx.path_of(entity_id), entity_id,
                              _pointer('name'),
                              f'A20: the normalised name {name!r} collides with '
                              f'{", ".join(others)}; list them in `distinct_from` if they '
                              f'really are different things')

        # name vs. another record's long alias.
        for name, alias_ids in sorted(long_aliases.items()):
            name_ids = names.get(name) or []
            if not name_ids:
                continue
            for alias_entity_id in sorted(set(alias_ids)):
                others = sorted({other for other in name_ids if other != alias_entity_id})
                if not others or _mutually_distinct(table, alias_entity_id, others):
                    continue
                yield Finding(ERROR, 'duplicate-name', ctx.path_of(alias_entity_id), alias_entity_id,
                              _pointer('aliases'),
                              f'A20: the normalised alias {name!r} collides with the name of '
                              f'{", ".join(others)}; list them in `distinct_from` if they '
                              f'really are different things')

        # long alias vs. long alias only (neither is anyone's own name):
        # informational — likely just two records independently using the
        # same shorthand, not evidence of one canonical entity written twice.
        for name, alias_ids in sorted(long_aliases.items()):
            if name in names:
                continue  # already reported (as an error) above
            unique = sorted(set(alias_ids))
            if len(unique) < 2:
                continue
            for entity_id in unique:
                others = [other for other in unique if other != entity_id]
                if _mutually_distinct(table, entity_id, others):
                    continue
                yield Finding(INFO, 'duplicate-alias-across-records', ctx.path_of(entity_id),
                              entity_id, _pointer('aliases'),
                              f'A20: the normalised alias {name!r} is also used by '
                              f'{", ".join(others)}; informational only — not necessarily the '
                              f'same thing')


def _part_of_chain(ctx: _Context, entity_id: str, limit: int = 8) -> set[str]:
    """`entity_id` and every source it (transitively) names as `part_of`."""
    chain = {entity_id}
    current = entity_id
    for _ in range(limit):
        record = ctx.atlas.get(current)
        parent = record.get('part_of') if record is not None else None
        if not isinstance(parent, str):
            break
        current = schema.canonical_id(parent)
        if current in chain:
            break
        chain.add(current)
    return chain


def _sources_share_a_container(ctx: _Context, a: str, b: str) -> bool:
    """A20: true when `a` is `b`'s container (or vice versa) via `part_of` —
    a chapter or volume of a larger work legitimately shares its DOI/URL."""
    return b in _part_of_chain(ctx, a) or a in _part_of_chain(ctx, b)


def check_duplicate_source_urls(ctx: _Context) -> Iterator[Finding]:
    """A20/A7: two `src:` records with the same normalised URL or DOI —
    unless one names the other as its `part_of` container (a chapter or
    volume of a larger work legitimately shares that work's DOI/URL)."""
    index: dict[tuple[str, str], list[str]] = {}
    for entity_id, record in sorted(ctx.atlas.by_type('source').items()):
        url = _normalise_url(record.get('url'))
        if url:
            index.setdefault(('url', url), []).append(entity_id)
        reference = record.get('reference')
        doi = _normalise_doi(reference.get('doi')) if isinstance(reference, dict) else ''
        if doi:
            index.setdefault(('doi', doi), []).append(entity_id)
    for (bucket, value), ids in sorted(index.items()):
        if len(ids) < 2:
            continue
        for entity_id in ids:
            others = [other for other in ids if other != entity_id
                      and not _sources_share_a_container(ctx, entity_id, other)]
            if not others:
                continue
            yield Finding(ERROR, 'duplicate-source-url', ctx.path_of(entity_id), entity_id,
                          _pointer(bucket if bucket == 'url' else 'reference'),
                          f'A20: the normalised {bucket} {value!r} is also on '
                          f'{", ".join(sorted(others))}')


def check_external_id_sources(ctx: _Context) -> Iterator[Finding]:
    """A20: an `external.*` id with a known URL shape needs a record-level
    source whose URL contains it."""
    for _type, entity_id, record in ctx.atlas.iter_entities():
        external = record.get('external')
        if not isinstance(external, dict):
            continue
        urls = []
        for source_id in record.get('sources') or []:
            source = ctx.source(source_id)
            if source is not None:
                urls.append(_normalise_url(source.get('url')).lower())
        for key, template in EXTERNAL_ID_URL_PATTERNS.items():
            value = external.get(key)
            if value in (None, '', [], {}):
                continue
            expected = template.format(value=_bare_external_id(key, value)).lower()
            if not any(expected in url for url in urls):
                yield Finding(ERROR, 'external-id-source', ctx.path_of(entity_id), entity_id,
                              _pointer('external', key),
                              f'A20: no record-level source URL contains {expected!r}')


def check_experiment_inspire_id(ctx: _Context) -> Iterator[Finding]:
    """A20: a tier A or B experiment needs `external.inspire_experiment`, or a
    `notes` entry saying why it has none."""
    registry_tiers = {row.get('entity_id'): row.get('tier') for row in ctx.atlas.coverage}
    for entity_id, record in sorted(ctx.atlas.by_type('experiment').items()):
        coverage = record.get('coverage') if isinstance(record.get('coverage'), dict) else {}
        tier = coverage.get('tier') or registry_tiers.get(entity_id)
        if tier not in schema.INSPIRE_REQUIRED_TIERS:
            continue
        external = record.get('external') if isinstance(record.get('external'), dict) else {}
        if external.get('inspire_experiment'):
            continue
        if [note for note in record.get('notes') or [] if _text(note)]:
            continue
        yield Finding(ERROR, 'experiment-inspire-id', ctx.path_of(entity_id), entity_id,
                      _pointer('external', 'inspire_experiment'),
                      f'A20: a tier {tier} experiment needs `external.inspire_experiment` or a '
                      f'`notes` entry explaining its absence')


def check_close_sites(ctx: _Context) -> Iterator[Finding]:
    """A20: two sites of one facility less than 100 m apart are probably one
    site written twice."""
    by_facility: dict[str, list[tuple[str, tuple[float, float]]]] = {}
    for entity_id, record in sorted(ctx.atlas.by_type('site').items()):
        facility_id = record.get('facility_id')
        coordinates = schema.coordinates_of(record)
        if isinstance(facility_id, str) and coordinates is not None:
            by_facility.setdefault(schema.canonical_id(facility_id), []).append((entity_id, coordinates))
    for facility_id, sites in sorted(by_facility.items()):
        for first in range(len(sites)):
            for second in range(first + 1, len(sites)):
                (a_id, a), (b_id, b) = sites[first], sites[second]
                metres = schema.great_circle_m(a[0], a[1], b[0], b[1])
                if metres < schema.MIN_SITE_SEPARATION_M:
                    yield Finding(WARNING, 'sites-too-close', ctx.path_of(b_id), b_id,
                                  _pointer('coordinates'),
                                  f'A20: {b_id} is {metres:.0f} m from {a_id}; both belong to '
                                  f'{facility_id} and may be the same site')


def check_unresolved_person_names(ctx: _Context) -> Iterator[Finding]:
    """A20: an unresolved person whose normalised name equals a resolved one's
    is probably the same human, twice."""
    resolved: dict[str, str] = {}
    unresolved: list[tuple[str, str]] = []
    for entity_id, record in sorted(ctx.atlas.by_type('person').items()):
        name = schema.normalise_name(record.get('name'))
        if not name:
            continue
        if schema.inspire_recid(entity_id) is not None:
            resolved.setdefault(name, entity_id)
        else:
            unresolved.append((entity_id, name))
    for entity_id, name in unresolved:
        twin = resolved.get(name)
        if twin:
            yield Finding(WARNING, 'unresolved-person-name-collision', ctx.path_of(entity_id),
                          entity_id, _pointer('name'),
                          f'A20: the same normalised name as the resolved person {twin}')


# ===========================================================================
# A21 — geometry and plausibility
# ===========================================================================

def check_baselines(ctx: _Context) -> Iterator[Finding]:
    """A21: `beamline.baselines[].distance` must agree with the great-circle
    distance between the two sites to within 2 %."""
    for entity_id, record in sorted(ctx.atlas.by_type('beamline').items()):
        path = ctx.path_of(entity_id)
        for index, row in enumerate(record.get('baselines') or []):
            if not isinstance(row, dict):
                continue
            quantity = row.get('distance')
            if not isinstance(quantity, dict):
                continue
            first = schema.coordinates_of(ctx.resolve(row.get('from_site_id')))
            second = schema.coordinates_of(ctx.resolve(row.get('to_site_id')))
            if first is None or second is None:
                continue  # A21: skip when a site has no coordinates
            stated = schema.quantity_magnitude(quantity)
            if stated is None or stated == 0:
                continue
            actual = schema.great_circle_m(first[0], first[1], second[0], second[1])
            relative = abs(stated - actual) / actual if actual else 1.0
            if relative > schema.BASELINE_TOLERANCE:
                yield Finding(ERROR, 'baseline-distance', path, entity_id,
                              _pointer('baselines', index, 'distance'),
                              f'A21: the stated baseline is {stated / 1000:.1f} km but the '
                              f'great-circle distance is {actual / 1000:.1f} km '
                              f'({relative * 100:.1f} % > '
                              f'{schema.BASELINE_TOLERANCE * 100:g} %)')


def _plausibility_finding(path: str, entity_id: str | None, tokens: tuple[Any, ...],
                          key: str, quantity: dict) -> Finding | None:
    """A21 per-key plausibility range, in the dimension's base unit."""
    ranges = schema.PLAUSIBILITY_RANGES.get(key)
    if not ranges:
        return None
    bounds = ranges.get(quantity.get('dimension'))
    if bounds is None:
        return None
    magnitude = schema.quantity_magnitude(quantity)
    if magnitude is None:
        return None
    low, high = bounds
    if low <= magnitude <= high:
        return None
    return Finding(ERROR, 'plausibility-range', path, entity_id, _pointer(*tokens),
                   f'A21: {key} = {magnitude:g} (base unit) is outside the plausible range '
                   f'[{low:g}, {high:g}]')


def check_specs(ctx: _Context) -> Iterator[Finding]:
    """A21 / Appendix A: spec keys keep to their dimension whitelist and their
    plausibility range; an unrecognised spec key warns."""
    for _type, entity_id, record in ctx.atlas.iter_entities():
        path = ctx.path_of(entity_id)
        specs = record.get('specs')
        if isinstance(specs, dict):
            for key in sorted(specs):
                value = specs[key]
                if value is None:
                    continue
                tokens = ('specs', key)
                if key not in schema.SPEC_KEY_DIMENSIONS:
                    yield Finding(WARNING, 'unknown-spec-key', path, entity_id, _pointer(*tokens),
                                  f'A21: `{key}` is not an Appendix A spec key')
                    continue
                allowed = schema.SPEC_KEY_DIMENSIONS[key]
                quantity = schema.is_quantity(value)
                if not allowed:
                    if quantity:
                        yield Finding(ERROR, 'spec-key-dimension', path, entity_id,
                                      _pointer(*tokens),
                                      f'A21: `{key}` is a sourced string, not a quantity')
                    continue
                if not quantity:
                    yield Finding(ERROR, 'spec-key-dimension', path, entity_id, _pointer(*tokens),
                                  f'A21: `{key}` must be a quantity of dimension '
                                  f'{list(allowed)}')
                    continue
                if value.get('dimension') not in allowed:
                    yield Finding(ERROR, 'spec-key-dimension', path, entity_id,
                                  _pointer(*tokens, 'dimension'),
                                  f'A21: `{key}` takes dimension {list(allowed)}, got '
                                  f'{value.get("dimension")!r}')
                    continue
                finding = _plausibility_finding(path, entity_id, tokens, key, value)
                if finding is not None:
                    yield finding
        for index, row in enumerate(record.get('key_specs') or []):
            if not isinstance(row, dict) or not schema.is_quantity(row.get('quantity')):
                continue
            key = _normalise_spec_label(row.get('label'))
            finding = _plausibility_finding(path, entity_id, ('key_specs', index, 'quantity'),
                                            key, row['quantity'])
            if finding is not None:
                yield finding
        for index, row in enumerate(record.get('baselines') or []):
            if not isinstance(row, dict) or not schema.is_quantity(row.get('distance')):
                continue
            finding = _plausibility_finding(path, entity_id, ('baselines', index, 'distance'),
                                            'baseline', row['distance'])
            if finding is not None:
                yield finding


def check_planned_starts(ctx: _Context) -> Iterator[Finding]:
    """A21: an interval whose `start.planned` is true cannot already be
    active, commissioning, completed or decommissioned."""
    forbidden = {'active', 'commissioning', 'completed', 'decommissioned'}
    for _type, entity_id, record in ctx.atlas.iter_entities():
        for index, row in enumerate(_intervals(record)):
            if schema.is_planned(row.get('start')) and row.get('status') in forbidden:
                yield Finding(ERROR, 'planned-start-with-realised-status', ctx.path_of(entity_id),
                              entity_id, _pointer('intervals', index, 'start'),
                              f'A21: a `planned` start cannot carry status '
                              f'{row.get("status")!r}')


def check_detector_site_distance(ctx: _Context) -> Iterator[Finding]:
    """A21: a detector site more than 50 km from its facility's primary site
    warns, unless the experiment is a long-baseline kind."""
    limit_m = schema.MAX_DETECTOR_SITE_DISTANCE_KM * 1000.0
    for entity_id, detector in sorted(ctx.atlas.by_type('detector').items()):
        path = ctx.path_of(entity_id)
        experiments = [ctx.resolve(reference)
                       for reference in schema.ref_ids(detector.get('experiment_ids'))]
        experiments = [record for record in experiments if record is not None]
        if any(record.get('kind') in schema.LONG_BASELINE_KINDS for record in experiments):
            continue
        facilities: list[dict] = []
        for experiment in experiments:
            for role in experiment.get('facility_roles') or []:
                if isinstance(role, dict):
                    facility = ctx.resolve(role.get('facility_id'))
                    if facility is not None:
                        facilities.append(facility)
        for index, placement in enumerate(detector.get('placements') or []):
            if not isinstance(placement, dict):
                continue
            site = ctx.resolve(placement.get('site_id'))
            here = schema.coordinates_of(site)
            if here is None:
                continue
            candidates = list(facilities)
            own_facility = ctx.resolve((site or {}).get('facility_id'))
            if own_facility is not None:
                candidates.append(own_facility)
            distances: list[float] = []
            for facility in candidates:
                primary = schema.coordinates_of(ctx.resolve(facility.get('primary_site_id')))
                if primary is not None:
                    distances.append(schema.great_circle_m(here[0], here[1], primary[0], primary[1]))
            if distances and min(distances) > limit_m:
                yield Finding(WARNING, 'detector-site-distance', path, entity_id,
                              _pointer('placements', index, 'site_id'),
                              f'A21: {placement.get("site_id")} is {min(distances) / 1000:.0f} km '
                              f'from the facility\'s primary site (> '
                              f'{schema.MAX_DETECTOR_SITE_DISTANCE_KM:g} km)')


# ===========================================================================
# Dispatcher and reporting
# ===========================================================================

#: Every check, in the order they run.  The result is sorted afterwards, so
#: this order only affects which defect a reader meets first while debugging.
CHECKS = (
    check_load_problems,
    check_duplicate_ids,
    check_references,
    check_coverage_references,
    check_reference_types,
    check_required_fields,
    check_enums,
    check_coordinates,
    check_intervals,
    check_results,
    check_quantities,
    check_sourced_values,
    check_topics,
    check_documents,
    check_people,
    check_experiments,
    check_dates,
    check_verified_at_order,
    check_result_dates,
    check_membership_dates,
    check_timeline_warnings,
    check_status_matches_state,
    check_schema_tag,
    check_claim_evidence,
    check_coordinate_sources,
    check_sources,
    check_evidence_classes,
    check_membership_files,
    check_record_sources,
    check_derived_fields,
    check_slist_shapes,
    check_duplicate_externals,
    check_duplicate_names,
    check_duplicate_source_urls,
    check_external_id_sources,
    check_experiment_inspire_id,
    check_close_sites,
    check_unresolved_person_names,
    check_baselines,
    check_specs,
    check_planned_starts,
    check_detector_site_distance,
)


def validate_atlas(atlas: Any, *, build_date: Any = None) -> list[Finding]:
    """Run every rule against a loaded atlas and return the findings.

    `build_date` may be a `datetime.date`, a `"YYYY-MM-DD"` string or None
    (today).  The order is deterministic: `(path, pointer, rule, message)`.
    """
    day = schema.as_date(build_date) or _dt.date.today()
    context = _Context(
        atlas=atlas,
        build_date=day,
        raw=_read_raw(Path(atlas.root)),
        selection=f'{day.year:04d}-{day.month:02d}',
    )
    findings: list[Finding] = []
    for check in CHECKS:
        findings.extend(check(context))
    findings.sort(key=lambda finding: finding.sort_key)
    return findings


def errors(findings: Iterable[Finding]) -> list[Finding]:
    """Only the build-failing findings."""
    return [finding for finding in findings if finding.level == ERROR]


def warnings(findings: Iterable[Finding]) -> list[Finding]:
    """Only the advisory findings."""
    return [finding for finding in findings if finding.level == WARNING]


def infos(findings: Iterable[Finding]) -> list[Finding]:
    """Only the informational findings (never build-failing, never a warning)."""
    return [finding for finding in findings if finding.level == INFO]


def group_findings(findings: Iterable[Finding]) -> dict[str, list[Finding]]:
    """Rule id -> its findings, rules in alphabetical order."""
    grouped: dict[str, list[Finding]] = {}
    for finding in findings:
        grouped.setdefault(finding.rule, []).append(finding)
    return {rule: grouped[rule] for rule in sorted(grouped)}


def format_report(findings: Iterable[Finding], *, strict: bool = False) -> str:
    """A human-readable report grouped by rule, ending in a count line."""
    findings = list(findings)
    grouped = group_findings(findings)
    lines: list[str] = []
    for rule, rows in grouped.items():
        if any(row.level == ERROR for row in rows):
            level = ERROR
        elif any(row.level == WARNING for row in rows):
            level = WARNING
        else:
            level = INFO
        lines.append(f'{rule} [{level}] — {len(rows)} finding(s)')
        for row in rows:
            location = f'{row.path}{row.pointer}' if row.pointer else row.path
            entity = f' ({row.entity_id})' if row.entity_id else ''
            lines.append(f'  - {location}{entity}: {row.message}')
        lines.append('')
    error_count, warning_count, info_count = (
        len(errors(findings)), len(warnings(findings)), len(infos(findings)))
    if not findings:
        lines.append('no findings')
    lines.append(f'{error_count} errors, {warning_count} warnings, {info_count} informational')
    if strict and warning_count and not error_count:
        lines.append('--strict: warnings are treated as errors')
    return '\n'.join(lines)


def main(argv: list[str] | None = None) -> int:
    """`python -m hepgraph.atlas.validate [--data DIR] [--strict]`."""
    parser = argparse.ArgumentParser(
        prog='python -m hepgraph.atlas.validate',
        description='Validate data/atlas/ against the HEP Atlas ontology v0.2.')
    parser.add_argument('--data', default=str(load.DATA_DIR),
                        help='the atlas data directory (default: %(default)s)')
    parser.add_argument('--strict', action='store_true',
                        help='exit non-zero when there are warnings as well as errors')
    parser.add_argument('--build-date', default=None,
                        help='the build date to derive states at (default: today)')
    arguments = parser.parse_args(argv)
    atlas = load.load_atlas(Path(arguments.data))
    findings = validate_atlas(atlas, build_date=arguments.build_date)
    print(format_report(findings, strict=arguments.strict))
    if errors(findings):
        return 1
    if arguments.strict and warnings(findings):
        return 1
    return 0


if __name__ == '__main__':  # pragma: no cover - CLI entry point
    raise SystemExit(main())
