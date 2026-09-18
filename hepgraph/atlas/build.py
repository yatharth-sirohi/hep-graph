"""Turn `data/atlas/` into the browser bundles under `static/atlas/generated/`.

`docs/HEP_ATLAS_BUNDLES.md` is the contract this module implements; the
ontology amendments A1-A22 (`docs/HEP_ATLAS_ONTOLOGY.md`) govern the input.
Nothing here reads the network and nothing outside the standard library is
imported.

The build is **deterministic**: every dict is dumped with sorted keys through
`load.dump_json` (A11) and every list is sorted with an explicit key, so two
builds of the same data produce byte-identical files.  `manifest.version` is a
content hash of every generated file except the manifest itself, so it changes
exactly when the data changes.

Shape of the module: one small function per bundle, plus a shared
stripping/provenance walker (:class:`Stripper`) that splits every authored
record into

* the **stripped value** that goes into the hot-path bundles, and
* the **provenance entry** (`sources`, `verified_at`, `confidence`, `note`,
  `quote`, `locator`) that goes into the lazily loaded `provenance.json` (A14),

keyed by entity id and by an RFC 6901 JSON pointer into the *authored* record.

Usage::

    python -m hepgraph.atlas.build [--data DIR] [--out DIR]
                                   [--build-date YYYY-MM-DD] [--check]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from . import load, schema

# ---------------------------------------------------------------------------
# What goes where
# ---------------------------------------------------------------------------

#: Entity types that live in `atlas.json` (institutions, people, results,
#: documents and sources have their own bundles; §8 / A14).
ATLAS_TYPES: tuple[str, ...] = (
    'facility', 'site', 'accelerator', 'beamline', 'experiment', 'detector',
    'collaboration', 'topic',
)

#: Entity types that appear in `search.json`.  People are never in it (A14)
#: and sources are not user-facing search targets.
SEARCH_TYPES: tuple[str, ...] = ATLAS_TYPES + ('institution', 'result', 'document')

#: A1 inverse relations the build recomputes and writes, per entity type.
#: Everything listed here is emitted even when it is empty, so the frontend can
#: rely on the key existing.
DERIVED_LINKS: dict[str, tuple[str, ...]] = {
    'facility': ('site_ids', 'accelerator_ids', 'beamline_ids', 'institution_id',
                 'experiment_ids', 'document_ids'),
    'site': ('document_ids',),
    'accelerator': ('beamline_ids', 'serves_experiment_ids', 'fed_by_accelerator_ids',
                    'document_ids'),
    'beamline': ('experiment_ids', 'document_ids'),
    'experiment': ('facility_ids', 'site_ids', 'detector_ids', 'result_ids', 'document_ids'),
    'detector': ('document_ids',),
    'collaboration': ('experiment_ids', 'document_ids'),
    'institution': ('collaboration_ids',),
}
#: Derived link fields that hold a single id rather than a list.
SCALAR_DERIVED_LINKS: frozenset[str] = frozenset({'institution_id'})

#: Ontology §7 relation names, plus the four additions this build emits
#: (documented in docs/HEP_ATLAS_BUNDLES.md).
LINEAGE_EDGE_TYPES: dict[str, str] = {
    'predecessor': 'PRECEDED_BY',
    'successor': 'SUCCEEDED_BY',
    'upgrade_of': 'UPGRADE_OF',
    'upgraded_to': 'UPGRADED_TO',
    'same_program': 'SAME_PROGRAM',
    'complementary': 'COMPLEMENTARY',
}

#: A month index sorts before every real one when an edge has no known start.
_UNKNOWN_MONTH = -(1 << 30)


# ---------------------------------------------------------------------------
# Result of one build
# ---------------------------------------------------------------------------

@dataclass
class BuildResult:
    """Everything one build produced.

    `files` maps a bundle path relative to the output directory to its
    canonical JSON text, so a caller can inspect a build without touching the
    filesystem.  `drift` is filled in `--check` mode only.
    """

    files: dict[str, str] = field(default_factory=dict)
    manifest: dict = field(default_factory=dict)
    version: str = ''
    errors: list[str] = field(default_factory=list)
    drift: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    sizes: dict[str, int] = field(default_factory=dict)   # per-type bytes in atlas.json
    written: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    out_dir: Path | None = None
    build_date: str = ''

    @property
    def ok(self) -> bool:
        return not self.errors and not self.drift


# ---------------------------------------------------------------------------
# JSON pointers (RFC 6901)
# ---------------------------------------------------------------------------

def escape_token(token: Any) -> str:
    """Escape one RFC 6901 reference token (`~` -> `~0`, `/` -> `~1`)."""
    return str(token).replace('~', '~0').replace('/', '~1')


def pointer_of(parent: str, token: Any) -> str:
    return f'{parent}/{escape_token(token)}'


# ---------------------------------------------------------------------------
# The stripping / provenance walker (A14)
# ---------------------------------------------------------------------------

def _has_content(value: Any) -> bool:
    """True when a provenance value actually says something."""
    if value is None:
        return False
    if isinstance(value, (str, list, dict, tuple)):
        return len(value) > 0
    return True


class Stripper:
    """Splits authored records into stripped values plus provenance.

    One instance is shared by the whole build so that `provenance.json` and
    the `cited_by` map of `sources.json` are collected in a single walk.
    """

    def __init__(self) -> None:
        # entity id -> json pointer -> provenance record
        self.provenance: dict[str, dict[str, dict]] = {}
        # source id -> entity id -> set of json pointers citing it
        self.citations: dict[str, dict[str, set[str]]] = {}

    # -- provenance --------------------------------------------------------
    def _record(self, entity_id: str, pointer: str, node: dict) -> None:
        """Move the provenance keys of `node` into the provenance table."""
        if not any(key in node for key in schema.PROVENANCE_KEYS):
            return
        entry = {key: node.get(key) for key in schema.PROVENANCE_KEYS}
        if not any(_has_content(value) for value in entry.values()):
            return  # nothing but empty notes; not worth a lazy-loaded entry
        # The root of a record has an empty pointer; its `sources` are the A22
        # record-level identity claims, which the ontology addresses as `/sources`.
        pointer = pointer or '/sources'
        self.provenance.setdefault(entity_id, {})[pointer] = entry
        for source_id in entry.get('sources') or []:
            if isinstance(source_id, str):
                self.citations.setdefault(source_id, {}).setdefault(entity_id, set()).add(pointer)

    # -- stripping ---------------------------------------------------------
    def strip(self, value: Any, entity_id: str, pointer: str = '') -> Any:
        """Return `value` with every provenance key moved out (recursively)."""
        if isinstance(value, list):
            return [self.strip(item, entity_id, pointer_of(pointer, index))
                    for index, item in enumerate(value)]
        if not isinstance(value, dict):
            return value

        self._record(entity_id, pointer, value)
        rest = {key: item for key, item in value.items() if key not in schema.PROVENANCE_KEYS}

        if schema.is_quantity(value):
            return {key: rest[key] for key in schema.QUANTITY_KEYS if key in rest}
        if schema.is_coordinates(value):
            kept = {key: rest.get(key) for key in ('lat', 'lon', 'precision_m', 'kind')}
            # A23: the globe must be able to draw an admitted approximation
            # differently without fetching provenance.json, so the one bit of
            # confidence that changes the marker travels with the point.
            if value.get('confidence') in ('approximate', 'uncertain', 'derived'):
                kept['approximate'] = True
            return kept
        if schema.is_interval(value):
            kept = {key: rest[key] for key in ('label', 'status', 'kind') if key in rest}
            # `start`/`end` may themselves be date *objects* carrying a `note`
            # qualifier (§2.2): that note is provenance, not part of the
            # documented stripped Date-object shape (`date`/`approx`/
            # `planned`/`display`/…), so it must go through the same
            # recursive strip as everything else — not be copied verbatim —
            # or it leaks into atlas.json instead of provenance.json.
            for key in ('start', 'end'):
                if key in rest:
                    kept[key] = self.strip(rest[key], entity_id, pointer_of(pointer, key))
            if 'specs' in rest:
                kept['specs'] = self.strip(rest['specs'], entity_id, pointer_of(pointer, 'specs'))
            return kept
        if self._is_date_object(rest):
            return self._strip_date(rest)
        if 'value' in value and any(key in value for key in schema.PROVENANCE_KEYS):
            # A sourced value: `{"value": V, "sources": …}` collapses to V.
            return self.strip(value['value'], entity_id, pointer_of(pointer, 'value'))
        return {key: self.strip(item, entity_id, pointer_of(pointer, key))
                for key, item in rest.items()}

    @staticmethod
    def _is_date_object(node: dict) -> bool:
        return 'date' in node and set(node) <= schema.DATE_OBJECT_KEYS

    @staticmethod
    def _strip_date(node: dict) -> Any:
        """A date object keeps its qualifiers, a bare one collapses to the string."""
        qualifiers = {key: node[key] for key in ('approx', 'planned', 'display', 'earliest', 'latest')
                      if _has_content(node.get(key))}
        if not qualifiers:
            return node.get('date')
        return {'date': node.get('date'), **qualifiers}


# ---------------------------------------------------------------------------
# Derived inverse relations (A1)
# ---------------------------------------------------------------------------

class Links:
    """Every derived inverse relation of the dataset, computed once."""

    def __init__(self) -> None:
        self._sets: dict[str, dict[str, set[str]]] = {}

    def add(self, entity_id: Any, field_name: str, target: Any) -> None:
        if not isinstance(entity_id, str) or not isinstance(target, str):
            return
        self._sets.setdefault(entity_id, {}).setdefault(field_name, set()).add(target)

    def ids(self, entity_id: str, field_name: str) -> list[str]:
        return sorted(self._sets.get(entity_id, {}).get(field_name, ()))

    def one(self, entity_id: str, field_name: str) -> str | None:
        found = self.ids(entity_id, field_name)
        return found[0] if found else None


def derive_links(atlas: load.Atlas) -> Links:
    """Compute every A1 inverse list from the canonical directions."""
    links = Links()

    for site in _sorted_records(atlas, 'site'):
        links.add(site.get('facility_id'), 'site_ids', site['id'])

    for accelerator in _sorted_records(atlas, 'accelerator'):
        links.add(accelerator.get('facility_id'), 'accelerator_ids', accelerator['id'])
        for downstream in schema.ref_ids(accelerator.get('feeds_accelerator_ids')):
            links.add(downstream, 'fed_by_accelerator_ids', accelerator['id'])

    for beamline in _sorted_records(atlas, 'beamline'):
        links.add(beamline.get('facility_id'), 'beamline_ids', beamline['id'])
        links.add(beamline.get('accelerator_id'), 'beamline_ids', beamline['id'])

    for institution in _sorted_records(atlas, 'institution'):
        links.add(institution.get('facility_id'), 'institution_id', institution['id'])

    for experiment in _sorted_records(atlas, 'experiment'):
        for role in experiment.get('facility_roles') or []:
            if isinstance(role, dict):
                links.add(experiment['id'], 'facility_ids', role.get('facility_id'))
                links.add(role.get('facility_id'), 'experiment_ids', experiment['id'])
        for beamline_id in schema.ref_ids(experiment.get('beamline_ids')):
            links.add(beamline_id, 'experiment_ids', experiment['id'])
        for accelerator_id in schema.ref_ids(experiment.get('accelerator_ids')):
            links.add(accelerator_id, 'serves_experiment_ids', experiment['id'])
        for collaboration_id in schema.ref_ids(experiment.get('collaboration_ids')):
            links.add(collaboration_id, 'experiment_ids', experiment['id'])

    for detector in _sorted_records(atlas, 'detector'):
        for experiment_id in schema.ref_ids(detector.get('experiment_ids')):
            links.add(experiment_id, 'detector_ids', detector['id'])
            for placement in detector.get('placements') or []:
                if isinstance(placement, dict):
                    links.add(experiment_id, 'site_ids', placement.get('site_id'))

    for result in _sorted_records(atlas, 'result'):
        for experiment_id in schema.ref_ids(result.get('experiment_ids')):
            links.add(experiment_id, 'result_ids', result['id'])

    for document in _sorted_records(atlas, 'document'):
        for owner_id in schema.ref_ids(document.get('owner_ids')):
            links.add(owner_id, 'document_ids', document['id'])

    for collaboration_id in sorted(atlas.memberships):
        for row in atlas.memberships[collaboration_id].get('members') or []:
            if isinstance(row, dict):
                links.add(row.get('institution_id'), 'collaboration_ids', collaboration_id)

    return links


def derive_lineage(atlas: load.Atlas) -> dict[str, list[dict]]:
    """A1 inverse lineage rows, keyed by the experiment that receives them.

    `predecessor` / `upgrade_of` produce `successor` / `upgraded_to` on the
    other experiment; the symmetric relations (`same_program`,
    `complementary`), which are authored on the lexicographically smaller id,
    are mirrored onto the larger one.
    """
    inverse: dict[str, list[dict]] = {}
    for experiment in _sorted_records(atlas, 'experiment'):
        for row in experiment.get('lineage') or []:
            if not isinstance(row, dict):
                continue
            relation = row.get('relation')
            other_id = row.get('experiment_id')
            if relation not in schema.CANONICAL_LINEAGE_RELATIONS or not isinstance(other_id, str):
                continue  # `successor` / `upgraded_to` in a data file are ignored (A1)
            mirror = schema.LINEAGE_INVERSE[relation]
            inverse.setdefault(other_id, []).append({
                'experiment_id': experiment['id'],
                'relation': mirror,
                'derived': True,
            })
    for rows in inverse.values():
        rows.sort(key=lambda row: (row['relation'], row['experiment_id']))
    return inverse


def _sorted_records(atlas: load.Atlas, entity_type: str) -> list[dict]:
    table = atlas.by_type(entity_type)
    return [table[entity_id] for entity_id in sorted(table)]


# ---------------------------------------------------------------------------
# Timeline helpers
# ---------------------------------------------------------------------------

def _selection(build_day: _dt.date) -> str:
    """The `"YYYY-MM"` slider selection that represents the build date."""
    return f'{build_day.year:04d}-{build_day.month:02d}'


def _month_text(day: _dt.date) -> str:
    return f'{day.year:04d}-{day.month:02d}'


def _hull_bounds(record: dict, build_day: _dt.date) -> tuple[_dt.date, _dt.date | None] | None:
    """The A3 existence hull as `(start, end)`, `end` None while open.

    `schema.existence_hull` clamps an open hull at the build date; an edge that
    is still running should carry `end: null` instead, so the open case is
    detected from the absence of a terminal interval.
    """
    hull = schema.existence_hull(record, build_date=build_day)
    if hull is None:
        return None
    terminal = any(isinstance(row, dict) and row.get('status') in schema.TERMINAL_STATUSES
                   for row in record.get('intervals') or [])
    return hull[0], (hull[1] if terminal else None)


def hull_interval(first: dict | None, second: dict | None,
                  build_day: _dt.date) -> tuple[str | None, str | None]:
    """Intersection of two entities' existence hulls, as month strings.

    Returns `(None, None)` when either hull is unknown, so the edge is emitted
    with null bounds rather than a guess.
    """
    if not isinstance(first, dict) or not isinstance(second, dict):
        return None, None
    left = _hull_bounds(first, build_day)
    right = _hull_bounds(second, build_day)
    if left is None or right is None:
        return None, None
    start = max(left[0], right[0])
    ends = [end for end in (left[1], right[1]) if end is not None]
    end = min(ends) if ends else None
    if end is not None and end < start:
        return None, None
    return _month_text(start), (_month_text(end) if end is not None else None)


# ---------------------------------------------------------------------------
# Small presentation helpers
# ---------------------------------------------------------------------------

def humanise(value: Any) -> str:
    """`accelerator_neutrino` -> `Accelerator neutrino`."""
    text = str(value or '').replace('_', ' ').strip()
    return text[:1].upper() + text[1:] if text else ''


def _join(parts: Iterable[Any]) -> str:
    return ' · '.join(str(part) for part in parts if part)


def _year_of(value: Any) -> str:
    day = schema.lo(value)
    return f'{day.year:04d}' if day is not None else ''


# ---------------------------------------------------------------------------
# The build context: everything derived once, then read by each bundle
# ---------------------------------------------------------------------------

class _Context:
    """Shared state of one build (loaded data plus everything derived once)."""

    def __init__(self, atlas: load.Atlas, build_day: _dt.date) -> None:
        self.atlas = atlas
        self.build_day = build_day
        self.selection = _selection(build_day)
        self.build_date = build_day.isoformat()
        self.stripper = Stripper()
        self.links = derive_links(atlas)
        self.lineage = derive_lineage(atlas)
        self.warnings: list[str] = []
        # entity id -> stripped record (authored provenance removed)
        self.stripped: dict[str, dict] = {}
        # entity id -> {field: long text}
        self.text: dict[str, dict] = {}
        # entity id -> [[m0, m1, status, certainty], …]
        self.segments: dict[str, list[list]] = {}
        for entity_type, entity_id, record in atlas.iter_entities():
            self.stripped[entity_id] = self.stripper.strip(record, entity_id)
            long_text = self._extract_text(entity_type, entity_id, record)
            if long_text:
                self.text[entity_id] = long_text
            if record.get('intervals'):
                self.segments[entity_id] = schema.state_segments(record, build_day)
        self._derive_site_segments(atlas, build_day)
        for collaboration_id in sorted(atlas.memberships):
            self._strip_membership_file(collaboration_id)

    def _derive_site_segments(self, atlas: load.Atlas, build_day) -> None:
        """Give each site the timeline of what stands there.

        A site is a place and has no intervals of its own, but the globe has to
        answer "what was here in 1990". Without this every site marker shows in
        every year, so the ATLAS cavern appears a decade before it was dug and
        the timeline changes nothing. The answer is the union of the experiments
        whose detectors are placed at the site: a cavern is on the map when
        something is in it.
        """
        by_site: dict[str, list[dict]] = {}
        for detector in atlas.by_type('detector').values():
            experiments = [atlas.get(eid) for eid in schema.ref_ids(detector.get('experiment_ids'))]
            for placement in detector.get('placements') or []:
                site_id = placement.get('site_id') if isinstance(placement, dict) else None
                if not site_id:
                    continue
                # Prefer the experiments' own history; fall back to the
                # detector's when an experiment records none.
                sources = [e for e in experiments if e and e.get('intervals')] or [detector]
                by_site.setdefault(site_id, []).extend(s for s in sources if s.get('intervals'))

        for site_id, sources in by_site.items():
            if site_id in self.segments or not atlas.get(site_id):
                continue
            merged: dict[int, tuple[str, str]] = {}
            for source in sources:
                for m0, m1, status, certainty in schema.state_segments(source, build_day):
                    for month in range(m0, m1 + 1):
                        # An operating state beats a speculative one when two
                        # experiments share a hall.
                        previous = merged.get(month)
                        if previous is None or _state_rank(status) > _state_rank(previous[0]):
                            merged[month] = (status, certainty)
            if merged:
                self.segments[site_id] = _run_length(merged)

    # -- long text (§8) ----------------------------------------------------
    def _extract_text(self, entity_type: str, entity_id: str, record: dict) -> dict:
        """Pop the long-text fields out of the stripped record into text.json."""
        fields = schema.LONG_TEXT_FIELDS.get(entity_type, schema.LONG_TEXT_FIELDS['default'])
        stripped = self.stripped[entity_id]
        out: dict[str, Any] = {}
        for name in fields:
            if name == 'summary.technical':
                summary = stripped.get('summary')
                if isinstance(summary, dict) and 'technical' in summary:
                    out['summary_technical'] = summary.pop('technical')
            elif name == 'claim':
                # The claim's quote *is* the content (A16); only its `sources`
                # move to provenance.json.
                authored = record.get('claim')
                stripped.pop('claim', None)
                if isinstance(authored, dict):
                    out['claim'] = {key: authored[key] for key in ('quote', 'locator')
                                    if key in authored}
            elif name in stripped:
                out[name] = stripped.pop(name)
        return out

    # -- membership files --------------------------------------------------
    def _strip_membership_file(self, collaboration_id: str) -> None:
        """Collect the provenance of one roster file under the collaboration id.

        Pointers are into the authored membership file (`/members/3`,
        `/roster_sources`), which never collide with the collaboration
        entity's own pointers.
        """
        payload = self.atlas.memberships[collaboration_id]
        for index, row in enumerate(payload.get('members') or []):
            if isinstance(row, dict):
                self.stripper.strip(row, collaboration_id, f'/members/{index}')
        for index, snapshot in enumerate(payload.get('roster_snapshots') or []):
            if isinstance(snapshot, dict):
                self.stripper.strip(snapshot, collaboration_id, f'/roster_snapshots/{index}')
        roster_sources = payload.get('roster_sources') or []
        if roster_sources:
            self.stripper._record(collaboration_id, '/roster_sources',
                                  {'sources': list(roster_sources)})

    # -- convenience -------------------------------------------------------
    def name_of(self, entity_id: Any) -> str:
        record = self.atlas.get(entity_id) if isinstance(entity_id, str) else None
        return str((record or {}).get('name') or '')

    def status_at_build(self, record: dict) -> Any:
        """A3/A10 derived state at the build date, falling back to the file."""
        state = schema.state_at(record, self.selection, build_date=self.build_day)
        if state is None:
            return record.get('status')
        return state['status']


# ---------------------------------------------------------------------------
# Bundles
# ---------------------------------------------------------------------------

def build_atlas_bundle(ctx: _Context, coverage_flags: dict[str, dict]) -> tuple[dict, dict[str, int]]:
    """`atlas.json`: one key per entity type, each an object keyed by id."""
    bundle: dict[str, Any] = {
        'schema': schema.SCHEMA_TAG,
        'build_date': ctx.build_date,
    }
    sizes: dict[str, int] = {}
    for entity_type in ATLAS_TYPES:
        plural = schema.ENTITY_DIRS[entity_type]
        table: dict[str, dict] = {}
        for entity_id in sorted(ctx.atlas.by_type(entity_type)):
            table[entity_id] = _atlas_record(ctx, entity_type, entity_id, coverage_flags)
        bundle[plural] = table
        sizes[plural] = len(load.dump_json(table).encode('utf-8'))
    return bundle, sizes


def _atlas_record(ctx: _Context, entity_type: str, entity_id: str,
                  coverage_flags: dict[str, dict]) -> dict:
    """One stripped entity record with its derived fields filled in."""
    authored = ctx.atlas.by_type(entity_type)[entity_id]
    record = dict(ctx.stripped[entity_id])
    record.pop('schema', None)              # the bundle carries the schema tag

    # A1: never trust an authored derived field; recompute all of them.
    for name in schema.DERIVED_FIELDS.get(entity_type, ()):
        record.pop(name, None)
    for name in DERIVED_LINKS.get(entity_type, ()):
        record.pop(name, None)
        if name in SCALAR_DERIVED_LINKS:
            record[name] = ctx.links.one(entity_id, name)
        else:
            record[name] = ctx.links.ids(entity_id, name)

    if entity_type == 'experiment':
        lineage = list(record.get('lineage') or [])
        lineage.extend(ctx.lineage.get(entity_id, ()))
        lineage.sort(key=lambda row: (str(row.get('relation') or ''),
                                      str(row.get('experiment_id') or '')))
        record['lineage'] = lineage

    if authored.get('intervals'):
        record['state_segments'] = ctx.segments.get(entity_id, [])
        record['status'] = ctx.status_at_build(authored)
    elif entity_id in ctx.segments:
        # A site has no intervals of its own; its timeline is derived from what
        # stands there, so the globe can answer "what was here in 1990". Its
        # status follows from the same derivation rather than being authored.
        segments = ctx.segments[entity_id]
        record['state_segments'] = segments
        record['status'] = _status_from_segments(segments, ctx.build_day)

    flags = coverage_flags.get(entity_id)
    if flags:
        coverage = dict(record.get('coverage') or {})
        coverage.update(flags)
        record['coverage'] = coverage
    return record


def build_provenance_bundle(ctx: _Context) -> dict:
    """`provenance.json`: `{entity_id: {json_pointer: record}}` (A14)."""
    bundle: dict[str, Any] = {'schema': schema.SCHEMA_TAG}
    for entity_id in sorted(ctx.stripper.provenance):
        bundle[entity_id] = ctx.stripper.provenance[entity_id]
    return bundle


def build_text_bundle(ctx: _Context) -> dict:
    """`text.json`: the long-text fields of `schema.LONG_TEXT_FIELDS`."""
    bundle: dict[str, Any] = {'schema': schema.SCHEMA_TAG}
    for entity_id in sorted(ctx.text):
        bundle[entity_id] = ctx.text[entity_id]
    return bundle


def build_results_bundle(ctx: _Context) -> dict:
    """`results.json`: every result, plus its date as a month index."""
    bundle: dict[str, Any] = {'schema': schema.SCHEMA_TAG}
    for entity_id in sorted(ctx.atlas.by_type('result')):
        record = dict(ctx.stripped[entity_id])
        record.pop('schema', None)
        record['month'] = schema.month_index(schema.lo(record.get('date')))
        bundle[entity_id] = record
    return bundle


def build_documents_bundle(ctx: _Context) -> dict:
    """`documents.json`: every document, stripped."""
    bundle: dict[str, Any] = {'schema': schema.SCHEMA_TAG}
    for entity_id in sorted(ctx.atlas.by_type('document')):
        record = dict(ctx.stripped[entity_id])
        record.pop('schema', None)
        bundle[entity_id] = record
    return bundle


def build_sources_bundle(ctx: _Context) -> dict:
    """`sources.json`: every source with its derived `rank` and `cited_by`."""
    bundle: dict[str, Any] = {'schema': schema.SCHEMA_TAG}
    for entity_id in sorted(ctx.atlas.by_type('source')):
        authored = ctx.atlas.by_type('source')[entity_id]
        record = dict(ctx.stripped[entity_id])
        record.pop('schema', None)
        record['rank'] = schema.source_rank(authored.get('source_type'))  # A18, never authored
        citations = ctx.stripper.citations.get(entity_id, {})
        record['cited_by'] = {citing: sorted(pointers) for citing, pointers in sorted(citations.items())}
        bundle[entity_id] = record
    return bundle


def build_institutions_bundle(ctx: _Context) -> dict:
    """`institutions.json`: every institution plus its collaborations."""
    bundle: dict[str, Any] = {'schema': schema.SCHEMA_TAG}
    for entity_id in sorted(ctx.atlas.by_type('institution')):
        record = dict(ctx.stripped[entity_id])
        record.pop('schema', None)
        record['collaboration_ids'] = ctx.links.ids(entity_id, 'collaboration_ids')
        bundle[entity_id] = record
    return bundle


def build_membership_bundles(ctx: _Context) -> dict[str, dict]:
    """`memberships/<collaboration-slug>.json`, one per roster file (A5, A19)."""
    bundles: dict[str, dict] = {}
    for collaboration_id in sorted(ctx.atlas.memberships):
        payload = ctx.atlas.memberships[collaboration_id]
        collaboration = ctx.atlas.get(collaboration_id) or {}
        as_of = payload.get('as_of')
        history = payload.get('membership_history') or 'unknown'
        formation = _formation_of(collaboration)
        rows = [row for row in payload.get('members') or [] if isinstance(row, dict)]
        render_kwargs = dict(formation=formation, as_of=as_of, build_date=ctx.build_day,
                             membership_history=history)

        members = [_membership_row(ctx, row, collaboration, as_of, render_kwargs) for row in rows]
        members.sort(key=lambda row: (str(row.get('name') or ''), str(row.get('institution_id') or '')))

        snapshots = [ctx.stripper.strip(snapshot, collaboration_id, '')
                     for snapshot in payload.get('roster_snapshots') or []
                     if isinstance(snapshot, dict)]
        path = f'memberships/{schema.filename_for(collaboration_id)}.json'
        bundles[path] = {
            'schema': schema.SCHEMA_TAG,
            'collaboration_id': collaboration_id,
            'as_of': as_of,
            'membership_history': history,
            'roster_sources': sorted(payload.get('roster_sources') or []),
            'roster_snapshots': snapshots,
            'formation': formation,
            'counts': schema.membership_counts(rows, ctx.selection, **render_kwargs),
            'members': members,
        }
    return bundles


def _formation_of(collaboration: dict) -> Any:
    """The collaboration's formation date as a plain date value."""
    formation = collaboration.get('formation')
    if isinstance(formation, dict) and 'value' in formation:
        return formation.get('value')
    return formation


def _membership_row(ctx: _Context, row: dict, collaboration: dict, as_of: Any,
                    render_kwargs: dict) -> dict:
    """One institution row of a roster, evaluated at the build date (A5, A19)."""
    institution_id = row.get('institution_id')
    institution = ctx.atlas.get(institution_id) if isinstance(institution_id, str) else None
    stripped_institution = ctx.stripped.get(institution_id or '', {}) if institution else {}
    verdict = schema.membership_render(row, ctx.selection, **render_kwargs)
    evidence_class = row.get('evidence_class')
    return {
        'institution_id': institution_id,
        'name': (institution or {}).get('name'),
        'country': (institution or {}).get('country'),
        'coordinates': stripped_institution.get('coordinates'),
        'start': _plain_date(row.get('start')),
        'end': _plain_date(row.get('end')),
        'known_since': _plain_date(row.get('known_since')),
        'known_until': _plain_date(row.get('known_until')),
        'known_since_month': schema.month_index(schema.lo(row.get('known_since'))),
        'known_until_month': schema.month_index(schema.hi(row.get('known_until'))),
        'evidence_class': evidence_class,
        'evidence_label': schema.evidence_label(
            evidence_class, as_of=as_of, collaboration=collaboration.get('name'),
            year=_year_of(row.get('evidence_date')) or None,
            checked=schema.date_text(row.get('evidence_date')) or schema.date_text(row.get('verified_at'))),
        'render': verdict['render'] if verdict else None,
        'counted': bool(verdict and verdict['counted']),
        # `note` is the only provenance key kept inline: the roster UI shows it
        # next to a hollow dot.  It is in provenance.json as well.
        'note': row.get('note') or '',
    }


def _plain_date(value: Any) -> Any:
    """A date value as the plain `"YYYY[-MM[-DD]]"` string when it is one."""
    if isinstance(value, dict):
        text = schema.date_text(value)
        return text if set(value) <= schema.DATE_OBJECT_KEYS else value
    return value


def _status_from_segments(segments: list[list], build_day: _dt.date) -> str | None:
    """The derived status a site has at the build date, from its own segments."""
    month = (build_day.year - 1950) * 12 + (build_day.month - 1)
    for m0, m1, status, _certainty in segments:
        if m0 <= month <= m1:
            return status
    return segments[-1][2] if segments else None


def _state_rank(status: str) -> int:
    """How strongly a status claims a site; unknown statuses rank lowest."""
    return schema.STATE_RANK.get(status, -1)


def _run_length(months: dict[int, tuple[str, str]]) -> list[list]:
    """Collapse a month -> (status, certainty) map into `state_segments`."""
    out: list[list] = []
    for month in sorted(months):
        status, certainty = months[month]
        if out and out[-1][1] == month - 1 and out[-1][2] == status and out[-1][3] == certainty:
            out[-1][1] = month
        else:
            out.append([month, month, status, certainty])
    return out


def _link_people_bundles(files: dict[str, dict], people_bundles: dict[str, dict]) -> None:
    """Point each membership row at its people bundle, where one exists.

    People load lazily, one institution at a time, so a roster row has to carry
    the path of its own bundle: without it the interface has no way to reach
    the people at an institution and the collaboration view stops at the dots.
    Rows with no people keep no pointer, which is how the panel knows to say so.
    """
    by_pair = {(bundle['collaboration_id'], bundle['institution_id']): path
               for path, bundle in people_bundles.items()}
    for path, bundle in files.items():
        if not path.startswith('memberships/'):
            continue
        collaboration_id = bundle.get('collaboration_id')
        for row in bundle.get('members') or []:
            people_path = by_pair.get((collaboration_id, row.get('institution_id')))
            if people_path:
                row['people_bundle'] = people_path
                row['people_count'] = len(people_bundles[people_path]['people'])


def build_people_bundles(ctx: _Context) -> dict[str, dict]:
    """`people/<collab>/<institution>.json`, split lazily per (collab, institution)."""
    groups: dict[tuple[str, str | None], list[dict]] = {}
    for person_id in sorted(ctx.atlas.by_type('person')):
        person = ctx.atlas.by_type('person')[person_id]
        for row in person.get('memberships') or []:
            if not isinstance(row, dict):
                continue
            collaboration_id = row.get('collaboration_id')
            if not isinstance(collaboration_id, str):
                continue
            institution_id = row.get('institution_id')
            key = (collaboration_id, institution_id if isinstance(institution_id, str) else None)
            groups.setdefault(key, []).append(_person_row(ctx, person_id, person, row, collaboration_id))

    bundles: dict[str, dict] = {}
    for (collaboration_id, institution_id), people in sorted(
            groups.items(), key=lambda item: (item[0][0], item[0][1] or '')):
        people.sort(key=lambda row: (str(row.get('name') or ''), str(row.get('id') or '')))
        slug = schema.filename_for(institution_id) if institution_id else '_unknown'
        path = f'people/{schema.filename_for(collaboration_id)}/{slug}.json'
        bundles[path] = {
            'schema': schema.SCHEMA_TAG,
            'collaboration_id': collaboration_id,
            'institution_id': institution_id,
            'people': people,
        }
    return bundles


def _person_row(ctx: _Context, person_id: str, person: dict, row: dict,
                collaboration_id: str) -> dict:
    """One person inside a `people/<collab>/<institution>.json` bundle."""
    roster = ctx.atlas.memberships.get(collaboration_id) or {}
    collaboration = ctx.atlas.get(collaboration_id) or {}
    evidence_class = row.get('evidence_class')
    evidence_date = schema.date_text(row.get('evidence_date'))
    hep_graph: dict[str, Any] = {'available': schema.inspire_recid(person_id) is not None}
    url = schema.hep_graph_url(person_id)          # A6: `person:inspire-*` only
    if url is not None:
        hep_graph['url'] = url
    return {
        'id': person_id,
        'name': person.get('name'),
        'start': _plain_date(row.get('start')),
        'end': _plain_date(row.get('end')),
        'evidence_class': evidence_class,
        'evidence_label': schema.evidence_label(
            evidence_class, as_of=roster.get('as_of'), collaboration=collaboration.get('name'),
            year=_year_of(row.get('evidence_date')) or None, checked=evidence_date),
        'evidence_date': evidence_date,
        'hep_graph': hep_graph,
    }


def build_search_bundle(ctx: _Context) -> dict:
    """`search.json`: `[type, id, name, aliases, subtitle]`, never people (A14)."""
    entries: list[list] = []
    for entity_type in SEARCH_TYPES:
        for entity_id in sorted(ctx.atlas.by_type(entity_type)):
            record = ctx.atlas.by_type(entity_type)[entity_id]
            stripped = ctx.stripped[entity_id]
            aliases = [alias for alias in stripped.get('aliases') or [] if isinstance(alias, str)]
            entries.append([entity_type, entity_id, record.get('name'), sorted(aliases),
                            _subtitle(ctx, entity_type, record, stripped)])
    entries.sort(key=lambda entry: (entry[0], entry[1]))
    return {'schema': schema.SCHEMA_TAG, 'entries': entries}


#: Which facility best answers "where is this experiment", most telling first.
_FACILITY_ROLE_ORDER = ('host', 'beam_source', 'detector_host', 'prototype_host')


def _principal_facility(ctx: _Context, record: dict) -> str | None:
    """The facility an experiment should be named after.

    An experiment can touch several facilities in different roles, and the
    order they happen to appear in is meaningless. A prototype host is the
    least representative of them, so it is chosen last.
    """
    roles = record.get('facility_roles')
    if isinstance(roles, list) and roles:
        def rank(row: dict) -> tuple[int, int]:
            role = row.get('role')
            # A role the record itself calls historic is the least useful
            # answer: ICARUS ran at Gran Sasso, but it is at Fermilab now.
            historic = 1 if 'historic' in str(row.get('note') or '').lower() else 0
            position = (_FACILITY_ROLE_ORDER.index(role) if role in _FACILITY_ROLE_ORDER
                        else len(_FACILITY_ROLE_ORDER))
            return (historic, position)

        ranked = sorted((row for row in roles
                         if isinstance(row, dict) and row.get('facility_id')), key=rank)
        if ranked:
            return ranked[0]['facility_id']
    facilities = ctx.links.ids(record['id'], 'facility_ids')
    return facilities[0] if facilities else None


def _subtitle(ctx: _Context, entity_type: str, record: dict, stripped: dict) -> str:
    """One short line of context per search hit."""
    if entity_type == 'facility':
        countries = stripped.get('country') or stripped.get('countries') or []
        country = countries[0] if isinstance(countries, list) and countries else countries
        return _join([humanise(record.get('kind')), country if isinstance(country, str) else ''])
    if entity_type == 'site':
        place = stripped.get('place') or {}
        return _join([humanise(record.get('setting')),
                      ctx.name_of(record.get('facility_id')) or place.get('city')])
    if entity_type == 'accelerator':
        return _join([humanise(record.get('kind')), ctx.name_of(record.get('facility_id'))])
    if entity_type == 'beamline':
        return _join(['Beamline', ctx.name_of(record.get('facility_id'))])
    if entity_type == 'experiment':
        # Name the facility that *hosts* the experiment, not whichever id sorts
        # first: DUNE's prototypes live at CERN, and labelling DUNE "CERN" in
        # search results is simply wrong.
        return _join([humanise(record.get('kind')),
                      ctx.name_of(_principal_facility(ctx, record)) or ''])
    if entity_type == 'detector':
        classes = record.get('technology_classes') or []
        experiments = schema.ref_ids(record.get('experiment_ids'))
        return _join([humanise(classes[0] if classes else record.get('technology_class')),
                      ctx.name_of(experiments[0]) if experiments else ''])
    if entity_type == 'collaboration':
        experiments = ctx.links.ids(record['id'], 'experiment_ids')
        return _join(['Collaboration', ctx.name_of(experiments[0]) if experiments else ''])
    if entity_type == 'topic':
        return _join(['Topic', ctx.name_of(record.get('parent_id'))])
    if entity_type == 'institution':
        return _join([humanise(record.get('kind')), record.get('country')])
    if entity_type == 'result':
        return _join([humanise(record.get('result_type')), _year_of(stripped.get('date'))])
    if entity_type == 'document':
        return _join([humanise(record.get('doc_type')), _year_of(stripped.get('date'))])
    return ''


def build_graph_bundle(ctx: _Context) -> dict:
    """`graph.json`: the ontology §7 edge list with intervals (A9)."""
    edges: list[dict] = []

    def emit(edge_type: str, source_id: Any, target_id: Any, *,
             interval: Any = None, hull_from: dict | None = None,
             hull_to: dict | None = None) -> None:
        """Add one edge, taking an explicit interval when the data gave one."""
        if not isinstance(source_id, str) or not isinstance(target_id, str):
            return
        start = end = None
        if isinstance(interval, dict) and (interval.get('start') is not None
                                           or interval.get('end') is not None):
            start, end = interval.get('start'), interval.get('end')
        else:
            start, end = hull_interval(hull_from, hull_to, ctx.build_day)
        edges.append({
            'type': edge_type,
            'from': source_id,
            'to': target_id,
            'start': _plain_date(start),
            'end': _plain_date(end),
            'start_month': schema.month_index(schema.lo(start)),
            'end_month': schema.month_index(schema.hi(end)),
        })

    get = ctx.atlas.get

    # INSTITUTION --MEMBER_OF--> COLLABORATION (roster rows; A5 evidence dates
    # stand in for a missing join date).
    for collaboration_id in sorted(ctx.atlas.memberships):
        collaboration = get(collaboration_id)
        for row in ctx.atlas.memberships[collaboration_id].get('members') or []:
            if not isinstance(row, dict):
                continue
            emit('MEMBER_OF', row.get('institution_id'), collaboration_id,
                 interval={'start': row.get('start') or row.get('known_since'),
                           'end': row.get('end')},
                 hull_from=get(row.get('institution_id')), hull_to=collaboration)

    # PERSON --MEMBER_OF--> COLLABORATION and --AFFILIATED_WITH--> INSTITUTION.
    for person_id in sorted(ctx.atlas.by_type('person')):
        person = ctx.atlas.by_type('person')[person_id]
        for row in person.get('memberships') or []:
            if isinstance(row, dict):
                emit('MEMBER_OF', person_id, row.get('collaboration_id'), interval=row)
        for row in person.get('affiliations') or []:
            if isinstance(row, dict):
                emit('AFFILIATED_WITH', person_id, row.get('institution_id'), interval=row)

    # EXPERIMENT edges.
    for experiment in _sorted_records(ctx.atlas, 'experiment'):
        experiment_id = experiment['id']
        for collaboration_id in schema.ref_ids(experiment.get('collaboration_ids')):
            emit('OPERATES', collaboration_id, experiment_id,
                 hull_from=get(collaboration_id), hull_to=experiment)
        for role in experiment.get('facility_roles') or []:
            if isinstance(role, dict):
                emit('LOCATED_AT', experiment_id, role.get('facility_id'), interval=role,
                     hull_from=experiment, hull_to=get(role.get('facility_id')))
        for site_id in ctx.links.ids(experiment_id, 'site_ids'):
            emit('LOCATED_AT', experiment_id, site_id, hull_from=experiment, hull_to=get(site_id))
        for detector_id in ctx.links.ids(experiment_id, 'detector_ids'):
            emit('USES', experiment_id, detector_id, hull_from=experiment, hull_to=get(detector_id))
        for entry in experiment.get('beamline_ids') or []:
            beamline_id, interval = schema.ref_entry(entry)
            emit('USES_BEAMLINE', experiment_id, beamline_id, interval=interval,
                 hull_from=experiment, hull_to=get(beamline_id))
        for entry in experiment.get('accelerator_ids') or []:
            accelerator_id, interval = schema.ref_entry(entry)
            emit('USES_ACCELERATOR', experiment_id, accelerator_id, interval=interval,
                 hull_from=experiment, hull_to=get(accelerator_id))
        for topic_id in schema.ref_ids(experiment.get('topic_ids')):
            emit('STUDIES', experiment_id, topic_id)
        lineage = list(experiment.get('lineage') or []) + list(ctx.lineage.get(experiment_id, ()))
        for row in lineage:
            if not isinstance(row, dict):
                continue
            edge_type = LINEAGE_EDGE_TYPES.get(row.get('relation'))
            if edge_type:
                emit(edge_type, experiment_id, row.get('experiment_id'),
                     hull_from=experiment, hull_to=get(row.get('experiment_id')))

    # DETECTOR --LOCATED_AT--> SITE (placements carry their own interval, A2).
    for detector in _sorted_records(ctx.atlas, 'detector'):
        for placement in detector.get('placements') or []:
            if isinstance(placement, dict):
                emit('LOCATED_AT', detector['id'], placement.get('site_id'), interval=placement,
                     hull_from=detector, hull_to=get(placement.get('site_id')))

    # Containment inside a facility, and the accelerator chain.
    for site in _sorted_records(ctx.atlas, 'site'):
        emit('LOCATED_AT', site['id'], site.get('facility_id'),
             hull_from=site, hull_to=get(site.get('facility_id')))
    for accelerator in _sorted_records(ctx.atlas, 'accelerator'):
        emit('LOCATED_AT', accelerator['id'], accelerator.get('facility_id'),
             hull_from=accelerator, hull_to=get(accelerator.get('facility_id')))
        for entry in accelerator.get('feeds_accelerator_ids') or []:
            downstream, interval = schema.ref_entry(entry)
            emit('FED_BY', downstream, accelerator['id'], interval=interval,
                 hull_from=get(downstream), hull_to=accelerator)
    for beamline in _sorted_records(ctx.atlas, 'beamline'):
        emit('LOCATED_AT', beamline['id'], beamline.get('facility_id'),
             hull_from=beamline, hull_to=get(beamline.get('facility_id')))
        emit('FED_BY', beamline['id'], beamline.get('accelerator_id'),
             hull_from=beamline, hull_to=get(beamline.get('accelerator_id')))

    # RESULT and DOCUMENT edges (a result is an event: no interval).
    for result in _sorted_records(ctx.atlas, 'result'):
        for experiment_id in schema.ref_ids(result.get('experiment_ids')):
            emit('PRODUCED_BY', result['id'], experiment_id)
        for topic_id in schema.ref_ids(result.get('topic_ids')):
            emit('MEASURES', result['id'], topic_id)
    for document in _sorted_records(ctx.atlas, 'document'):
        for owner_id in schema.ref_ids(document.get('owner_ids')):
            emit('DESCRIBES', document['id'], owner_id)

    edges.sort(key=lambda edge: (
        edge['type'], edge['from'], edge['to'],
        edge['start_month'] if edge['start_month'] is not None else _UNKNOWN_MONTH,
        edge['end_month'] if edge['end_month'] is not None else -_UNKNOWN_MONTH,
    ))
    unique: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    for edge in edges:
        key = (edge['type'], edge['from'], edge['to'])
        if key not in seen:          # the earliest-starting edge of a triple wins
            seen.add(key)
            unique.append(edge)
    return {'schema': schema.SCHEMA_TAG, 'edges': unique}


def build_coverage_bundle(ctx: _Context) -> tuple[dict, dict[str, dict]]:
    """`coverage.json`: the merged registry plus the derived A10 flags.

    Returns the bundle and a `{entity_id: {"validated", "globe_ready"}}` map so
    `atlas.json` can carry the same two flags on the entity's `coverage`.
    """
    validated = _validated_entities(ctx)
    rows: list[dict] = []
    flags: dict[str, dict] = {}
    for row in ctx.atlas.coverage:
        entity_id = row.get('entity_id')
        clean = {key: value for key, value in row.items()
                 if key not in ('_file', 'experiment_id')}
        is_validated = bool(entity_id in validated)
        clean['validated'] = is_validated
        clean['globe_ready'] = is_validated and _is_globe_ready(ctx, entity_id)
        rows.append(clean)
        if isinstance(entity_id, str):
            flags[entity_id] = {'validated': clean['validated'],
                                'globe_ready': clean['globe_ready']}
    rows.sort(key=lambda row: (row.get('priority') if isinstance(row.get('priority'), int) else 1 << 30,
                               str(row.get('entity_id') or '')))
    return {'schema': schema.SCHEMA_TAG, 'rows': rows}, flags


def _validated_entities(ctx: _Context) -> set[str]:
    """Entity ids the validator reports no *error* for (A10).

    `hepgraph.atlas.validate` is optional: when it is not importable the build
    falls back to "the entity exists and has been researched".
    """
    researched = {
        row.get('entity_id') for row in ctx.atlas.coverage
        if isinstance(row.get('entity_id'), str)
        and ctx.atlas.has(row['entity_id'])
        and row.get('researched') != 'none'
    }
    try:
        from . import validate as validate_module
    except ImportError:
        return {entity_id for entity_id in researched if isinstance(entity_id, str)}
    validate_atlas = getattr(validate_module, 'validate_atlas', None)
    if validate_atlas is None:
        ctx.warnings.append('hepgraph.atlas.validate has no validate_atlas(); '
                            'coverage.validated falls back to `researched != "none"`')
        return {entity_id for entity_id in researched if isinstance(entity_id, str)}
    try:
        findings = validate_atlas(ctx.atlas, build_date=ctx.build_day)
    except Exception as exc:                       # pragma: no cover - defensive
        ctx.warnings.append(f'validator raised {exc!r}; coverage.validated falls back '
                            f'to `researched != "none"`')
        return {entity_id for entity_id in researched if isinstance(entity_id, str)}
    failed = {getattr(finding, 'entity_id', None) for finding in findings
              if getattr(finding, 'level', None) == 'error'}
    return {entity_id for entity_id in researched
            if isinstance(entity_id, str) and entity_id not in failed}


def _is_globe_ready(ctx: _Context, entity_id: Any) -> bool:
    """A10: the experiment can be drawn — a detector site and a known start."""
    record = ctx.atlas.get(entity_id) if isinstance(entity_id, str) else None
    if record is None:
        return False
    has_site = False
    for site_id in ctx.links.ids(entity_id, 'site_ids'):
        site = ctx.atlas.get(site_id) or {}
        coordinates = site.get('coordinates')
        if isinstance(coordinates, dict) and schema.coordinates_of(site) is not None \
                and (coordinates.get('kind') in schema.DETECTOR_COORDINATE_KINDS
                     or (coordinates.get('kind') == 'campus'
                         and coordinates.get('confidence') in ('approximate', 'uncertain'))):
            # A23: an admitted campus-grade placement is drawable, as approximate.
            has_site = True
            break
    has_start = any(isinstance(row, dict) and schema.try_parse_date(row.get('start')) is not None
                    for row in record.get('intervals') or [])
    return has_site and has_start


def build_manifest(ctx: _Context, files: dict[str, str], sizes: dict[str, int]) -> dict:
    """`manifest.json`: version, counts, timeline bounds and bundle sizes."""
    bundles: dict[str, dict] = {}
    for path in sorted(files):
        raw = files[path].encode('utf-8')
        bundles[path] = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
    months = [month for segments in ctx.segments.values() for segment in segments
              for month in (segment[0], segment[1])]
    timeline = {
        'min_month': min(months) if months else None,
        'max_month': max(months) if months else None,
        'min_year': schema.month_to_date(min(months)).year if months else None,
        'max_year': schema.month_to_date(max(months)).year if months else None,
    }
    return {
        'schema': schema.SCHEMA_TAG,
        'version': content_version(files),
        'build_date': ctx.build_date,
        'epoch': {'year': schema.EPOCH_YEAR, 'month': schema.EPOCH_MONTH},
        'counts': ctx.atlas.counts(),
        'timeline': timeline,
        'bundles': bundles,
        'atlas_bytes': sizes,
    }


def content_version(files: dict[str, str]) -> str:
    """First 16 hex characters of the SHA-256 over every non-manifest file."""
    digest = hashlib.sha256()
    for path in sorted(files):
        if path == 'manifest.json':
            continue
        digest.update(path.encode('utf-8'))
        digest.update(b'\0')
        digest.update(files[path].encode('utf-8'))
    return digest.hexdigest()[:16]


# ---------------------------------------------------------------------------
# The build itself
# ---------------------------------------------------------------------------

def build(data_dir: Path | str | None = None, out_dir: Path | str | None = None, *,
          build_date: Any = None, check: bool = False) -> BuildResult:
    """Build every bundle from `data_dir`.

    With `check=False` the bundles are written to `out_dir` and files that the
    build no longer produces are removed; with `check=True` nothing is written
    and `BuildResult.drift` lists every path that differs, is missing or is
    left over on disk.
    """
    data_path = Path(data_dir) if data_dir is not None else load.DATA_DIR
    out_path = Path(out_dir) if out_dir is not None else load.GENERATED_DIR
    build_day = schema.as_date(build_date) or _dt.date.today()

    atlas = load.load_atlas(data_path)
    result = BuildResult(out_dir=out_path, build_date=build_day.isoformat())
    # A file-level defect (unreadable JSON, a duplicate id, a duplicate
    # coverage row) makes the bundles untrustworthy: report every one.
    result.errors.extend(str(problem) for problem in atlas.problems)

    ctx = _Context(atlas, build_day)
    coverage_bundle, coverage_flags = build_coverage_bundle(ctx)
    atlas_bundle, sizes = build_atlas_bundle(ctx, coverage_flags)
    atlas_bundle['version'] = ''        # filled in below, once the version is known

    files: dict[str, Any] = {
        'atlas.json': atlas_bundle,
        'provenance.json': build_provenance_bundle(ctx),
        'text.json': build_text_bundle(ctx),
        'results.json': build_results_bundle(ctx),
        'documents.json': build_documents_bundle(ctx),
        'sources.json': build_sources_bundle(ctx),
        'institutions.json': build_institutions_bundle(ctx),
        'search.json': build_search_bundle(ctx),
        'graph.json': build_graph_bundle(ctx),
        'coverage.json': coverage_bundle,
    }
    files.update(build_membership_bundles(ctx))
    people_bundles = build_people_bundles(ctx)
    files.update(people_bundles)
    _link_people_bundles(files, people_bundles)

    # `atlas.json` repeats the data version, so the version must be computed
    # from the bundle text with the field blanked, then written back.
    texts = {path: load.dump_json(value) for path, value in files.items()}
    version = content_version(texts)
    atlas_bundle['version'] = version
    texts['atlas.json'] = load.dump_json(atlas_bundle)

    manifest = build_manifest(ctx, texts, sizes)
    manifest['version'] = version
    texts['manifest.json'] = load.dump_json(manifest)

    result.files = texts
    result.manifest = manifest
    result.version = version
    result.sizes = sizes
    result.warnings.extend(ctx.warnings)

    atlas_bytes = len(texts['atlas.json'].encode('utf-8'))
    if atlas_bytes > schema.ATLAS_JSON_MAX_BYTES:
        result.errors.append(
            f'atlas.json is {atlas_bytes} bytes, over the {schema.ATLAS_JSON_MAX_BYTES} byte limit')
    first_load = atlas_bytes + len(texts['manifest.json'].encode('utf-8'))
    if first_load > schema.ATLAS_JSON_BUDGET_BYTES:
        result.warnings.append(
            f'atlas.json + manifest.json is {first_load} bytes, over the pilot budget '
            f'of {schema.ATLAS_JSON_BUDGET_BYTES} bytes')

    if check:
        result.drift = compare(texts, out_path)
    else:
        result.written, result.removed = write_bundles(texts, out_path)
    return result


def compare(files: dict[str, str], out_dir: Path) -> list[str]:
    """Every difference between the freshly built bundles and `out_dir`."""
    drift: list[str] = []
    for path in sorted(files):
        target = out_dir / path
        if not target.is_file():
            drift.append(f'missing: {path}')
            continue
        if target.read_text(encoding='utf-8') != files[path]:
            drift.append(f'differs: {path}')
    for existing in sorted(_existing_files(out_dir)):
        if existing not in files:
            drift.append(f'extra: {existing}')
    return drift


def write_bundles(files: dict[str, str], out_dir: Path) -> tuple[list[str], list[str]]:
    """Write every bundle and delete the generated files we no longer produce."""
    written: list[str] = []
    for path in sorted(files):
        target = out_dir / path
        target.parent.mkdir(parents=True, exist_ok=True)
        text = files[path]
        if not target.is_file() or target.read_text(encoding='utf-8') != text:
            target.write_text(text, encoding='utf-8')
        written.append(path)
    removed: list[str] = []
    for existing in sorted(_existing_files(out_dir)):
        if existing not in files:
            (out_dir / existing).unlink()
            removed.append(existing)
    _prune_empty_dirs(out_dir)
    return written, removed


def _existing_files(out_dir: Path) -> list[str]:
    if not out_dir.is_dir():
        return []
    return [path.relative_to(out_dir).as_posix()
            for path in out_dir.rglob('*') if path.is_file()]


def _prune_empty_dirs(out_dir: Path) -> None:
    if not out_dir.is_dir():
        return
    for path in sorted(out_dir.rglob('*'), key=lambda p: len(p.parts), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------

def size_table(result: BuildResult) -> str:
    """The per-type byte table printed by every build."""
    lines = ['type                     bytes']
    for name in sorted(result.sizes):
        lines.append(f'{name:<24} {result.sizes[name]:>9}')
    for path in ('atlas.json', 'manifest.json'):
        if path in result.files:
            lines.append(f'{path:<24} {len(result.files[path].encode("utf-8")):>9}')
    total = sum(len(text.encode('utf-8')) for text in result.files.values())
    lines.append(f'{"all bundles":<24} {total:>9}')
    return '\n'.join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='python -m hepgraph.atlas.build',
        description='Build the HEP Atlas browser bundles from data/atlas/.')
    parser.add_argument('--data', default=None, help='atlas data directory (default: data/atlas)')
    parser.add_argument('--out', default=None,
                        help='output directory (default: static/atlas/generated)')
    parser.add_argument('--build-date', default=None, metavar='YYYY-MM-DD',
                        help='build date used for open intervals (default: today)')
    parser.add_argument('--check', action='store_true',
                        help='compare with the files on disk and fail on any drift')
    args = parser.parse_args(argv)

    build_date = args.build_date
    if build_date is not None and schema.as_date(build_date) is None:
        parser.error(f'--build-date {build_date!r} is not YYYY-MM-DD')

    result = build(args.data, args.out, build_date=build_date, check=args.check)

    print(size_table(result))
    for warning in result.warnings:
        print(f'warning: {warning}')
    for error in result.errors:
        print(f'error: {error}')

    if args.check:
        for line in result.drift:
            print(f'drift: {line}')
        if result.drift:
            print(f'{len(result.drift)} generated file(s) differ from {result.out_dir}')
        else:
            print(f'{len(result.files)} generated file(s) are up to date')
    else:
        print(f'wrote {len(result.written)} file(s) to {result.out_dir} '
              f'(version {result.version}, removed {len(result.removed)} stale file(s))')

    return 1 if (result.errors or result.drift) else 0


if __name__ == '__main__':
    raise SystemExit(main())
