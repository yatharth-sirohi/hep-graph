"""Load every JSON file under data/atlas/ into one typed in-memory model.

Loading is deliberately forgiving: structural problems that make a file
unusable (unparsable JSON, an id that does not match the filename, an
unknown directory) are *recorded* on the returned `Atlas` instead of raised,
so the validator can list all of them in one report.  Records with a usable
`id` are still indexed so that cross-reference checks can run.

Loading also performs the **v0.1 -> v0.2 migrations** of A2/A5/A6/A7/A9/A11.
Every migration appends a warning to `Atlas.warnings`; nothing is silently
rewritten.  The migrations are applied to the in-memory records only: the
files on disk are untouched until someone runs the scaffold or the build.

Layout (RESEARCH_AGENT_RULES rule 2; ontology §3):

    data/atlas/<type-plural>/<slug>.json     one entity per file
    data/atlas/topics/*.json                 each a LIST of topic records (§3.10)
    data/atlas/memberships/<collab>.json      one collaboration's roster (§3.11)
    data/atlas/coverage/<workstream>.json     LIST of registry rows (§3.15, A10)
"""
from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Iterator

from . import schema

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / 'data' / 'atlas'
GENERATED_DIR = ROOT / 'static' / 'atlas' / 'generated'


@dataclass(frozen=True)
class LoadProblem:
    """A file-level defect (an error) or a migration notice (a warning)."""

    path: str        # relative to the atlas root, posix form
    message: str

    def __str__(self) -> str:
        return f'{self.path}: {self.message}'


@dataclass
class Atlas:
    """Typed in-memory model of data/atlas/.

    `entities[type][id]` holds every entity record (sources included, under
    type `source`); `memberships[collaboration_id]` the roster files;
    `coverage` the merged registry rows (each row annotated with `_file`);
    `files[id]` the relative path an id was loaded from; `problems` the
    file-level defects found during loading; `warnings` the v0.1 -> v0.2
    migrations that were applied.
    """

    root: Path
    entities: dict[str, dict[str, dict]] = field(default_factory=lambda: {t: {} for t in schema.ENTITY_TYPES})
    memberships: dict[str, dict] = field(default_factory=dict)
    coverage: list[dict] = field(default_factory=list)
    limits: dict[str, dict] = field(default_factory=dict)   # A29: curve slug -> file
    files: dict[str, str] = field(default_factory=dict)
    membership_files: dict[str, str] = field(default_factory=dict)
    problems: list[LoadProblem] = field(default_factory=list)
    warnings: list[LoadProblem] = field(default_factory=list)

    # -- lookups -----------------------------------------------------------
    def get(self, entity_id: str) -> dict | None:
        entity_id = schema.canonical_id(entity_id)
        kind = schema.id_type(entity_id)
        if kind is None:
            return None
        return self.entities[kind].get(entity_id)

    def has(self, entity_id: str) -> bool:
        return self.get(entity_id) is not None

    def by_type(self, entity_type: str) -> dict[str, dict]:
        return self.entities.get(entity_type, {})

    def all_ids(self) -> set[str]:
        return {entity_id for table in self.entities.values() for entity_id in table}

    def iter_entities(self) -> Iterator[tuple[str, str, dict]]:
        """Yield (type, id, record) in deterministic (type, id) order."""
        for entity_type in schema.ENTITY_TYPES:
            for entity_id in sorted(self.entities[entity_type]):
                yield entity_type, entity_id, self.entities[entity_type][entity_id]

    def counts(self) -> dict[str, int]:
        counts = {schema.ENTITY_DIRS[t]: len(self.entities[t]) for t in schema.ENTITY_TYPES}
        counts['memberships'] = len(self.memberships)
        counts['coverage'] = len(self.coverage)
        return counts

    def relative(self, path: Path) -> str:
        try:
            return path.relative_to(self.root).as_posix()
        except ValueError:
            return path.as_posix()

    def problem(self, path: Path | str, message: str) -> None:
        rel = self.relative(path) if isinstance(path, Path) else path
        self.problems.append(LoadProblem(rel, message))

    def warn(self, path: Path | str, message: str) -> None:
        rel = self.relative(path) if isinstance(path, Path) else path
        self.warnings.append(LoadProblem(rel, message))


def read_json(path: Path) -> Any:
    with path.open('r', encoding='utf-8') as handle:
        return json.load(handle)


def dump_json(value: Any, *, indent: int | None = 2) -> str:
    """A11 canonical JSON text: sorted keys, UTF-8, trailing newline."""
    return json.dumps(value, ensure_ascii=False, allow_nan=False, indent=indent, sort_keys=True) + '\n'


def write_json(path: Path, value: Any, *, indent: int | None = 2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_json(value, indent=indent), encoding='utf-8')


def iter_json_files(root: Path) -> Iterator[Path]:
    """Every *.json under root, sorted for deterministic loading."""
    if not root.is_dir():
        return iter(())
    return iter(sorted(p for p in root.rglob('*.json') if p.is_file()))


def load_atlas(root: Path | str = DATA_DIR) -> Atlas:
    """Load data/atlas/ (or another root of the same layout), migrating to v0.2."""
    root = Path(root)
    atlas = Atlas(root=root)
    if not root.is_dir():
        atlas.problem(root.as_posix(), 'atlas data directory does not exist')
        return atlas
    for path in iter_json_files(root):
        rel = path.relative_to(root)
        if len(rel.parts) != 2:
            atlas.problem(path, 'files must sit directly in one type directory (data/atlas/<type-plural>/<slug>.json)')
            continue
        directory = rel.parts[0]
        try:
            payload = read_json(path)
        except (OSError, ValueError) as exc:
            atlas.problem(path, f'unreadable JSON: {exc}')
            continue
        if directory == 'memberships':
            _load_membership(atlas, path, payload)
        elif directory == 'coverage':
            _load_coverage(atlas, path, payload)
        elif directory == 'limits':
            _load_limit(atlas, path, payload)
        elif directory == 'topics':
            _load_topics(atlas, path, payload)
        elif directory in schema.DIR_TO_TYPE:
            _load_entity(atlas, path, payload, schema.DIR_TO_TYPE[directory])
        else:
            atlas.problem(path, f'unknown directory {directory!r}; expected one of '
                                f'{sorted(schema.DIR_TO_TYPE) + list(schema.AUXILIARY_DIRS)}')
    return atlas


# ---------------------------------------------------------------------------
# v0.1 -> v0.2 migration (A2, A5, A6, A7, A9, A11)
# ---------------------------------------------------------------------------

def migrate_person_references(node: Any) -> int:
    """Rewrite `person:inspire:<n>` -> `person:inspire-<n>` in id positions.

    Only values under `id`, `*_id` and `*_ids` keys are touched, so free text
    keeps whatever it says.  Returns the number of rewrites.
    """
    changed = 0
    if isinstance(node, dict):
        for key, value in list(node.items()):
            if (key == 'id' or key.endswith('_id')) and isinstance(value, str):
                canonical = schema.canonical_id(value)
                if canonical != value:
                    node[key] = canonical
                    changed += 1
            elif key.endswith('_ids') and isinstance(value, list):
                for index, item in enumerate(value):
                    if isinstance(item, str):
                        canonical = schema.canonical_id(item)
                        if canonical != item:
                            value[index] = canonical
                            changed += 1
                    else:
                        changed += migrate_person_references(item)
            else:
                changed += migrate_person_references(value)
    elif isinstance(node, list):
        for item in node:
            changed += migrate_person_references(item)
    return changed


def _sourced_row(source: dict, keys: tuple[str, ...]) -> dict:
    return {key: source[key] for key in keys if key in source}


def migrate_record(record: dict, entity_type: str) -> list[str]:
    """Apply every v0.1 -> v0.2 migration to one record in place.

    Returns a list of human-readable notices (one per migration applied).
    """
    notices: list[str] = []
    if migrate_person_references(record):
        notices.append('rewrote legacy `person:inspire:<recid>` ids to `person:inspire-<recid>` (A6)')
    if not record.get('schema'):
        record['schema'] = schema.SCHEMA_TAG

    if entity_type == 'detector':
        placements = record.get('placements')
        if not isinstance(placements, list) or not placements:
            site_id = record.get('site_id')
            if isinstance(site_id, str):
                record['placements'] = [{
                    'site_id': site_id, 'role': 'main', 'start': None, 'end': None,
                    'sources': list(record.get('sources') or []),
                    'verified_at': None, 'confidence': 'derived',
                    'note': 'migrated from the v0.1 scalar `site_id`',
                }]
                notices.append('migrated `site_id` to one `main` placement (A2)')
            elif placements is None:
                record['placements'] = []
        if record.get('facility_id') is not None:
            notices.append('dropped `facility_id`; a detector is placed at a site, not a facility (A2)')
            record.pop('facility_id', None)
        classes = record.get('technology_classes')
        scalar = record.get('technology_class')
        if not isinstance(classes, list) or not classes:
            record['technology_classes'] = [scalar] if isinstance(scalar, str) else []
            if isinstance(scalar, str):
                notices.append('derived `technology_classes` from the legacy scalar `technology_class` (A9)')

    elif entity_type == 'experiment':
        roles = record.get('facility_roles')
        if not isinstance(roles, list) or not roles:
            legacy = record.get('facility_ids')
            if isinstance(legacy, list) and legacy:
                record['facility_roles'] = [
                    {'facility_id': entry, 'role': 'host', 'start': None, 'end': None,
                     'sources': list(record.get('sources') or [])}
                    for entry in schema.ref_ids(legacy)
                ]
                notices.append('migrated `facility_ids` to `facility_roles` with role `host` (A2)')
            elif roles is None:
                record['facility_roles'] = []
        record.pop('facility_ids', None)

    elif entity_type == 'facility':
        if record.get('operator') is not None and record.get('operator_text') is None:
            record['operator_text'] = record['operator']
            notices.append('copied `operator` to `operator_text` (A1)')
        if 'operator_ids' not in record:
            record['operator_ids'] = []

    elif entity_type == 'source':
        if record.get('type') == schema.SOURCE_TYPE_FIELD_LEGACY:
            record['type'] = schema.SOURCE_TYPE_FIELD_VALUE
            notices.append('source `type` is "src" in v0.2 (A7)')
        legacy_type = record.get('source_type')
        if legacy_type in schema.LEGACY_SOURCE_TYPES:
            record['source_type'] = schema.LEGACY_SOURCE_TYPES[legacy_type]
            notices.append(f'`source_type: {legacy_type}` is retired; using '
                           f'{record["source_type"]!r} (A18)')
        derived_rank = schema.source_rank(record.get('source_type'))
        if derived_rank is not None and record.get('rank') != derived_rank:
            if record.get('rank') is not None:
                notices.append(f'`rank` is derived from `source_type` (A7/A18): '
                               f'{record.get("rank")!r} -> {derived_rank}')
            record['rank'] = derived_rank

    elif entity_type == 'person':
        recid = schema.inspire_recid(record.get('id'))
        hep_graph = {'available': recid is not None}
        url = schema.hep_graph_url(record.get('id'))
        if url is not None:
            hep_graph['url'] = url
        if record.get('hep_graph') != hep_graph:
            record['hep_graph'] = hep_graph

    return notices


def migrate_membership_file(payload: dict) -> list[str]:
    """A5/A19 migration of one memberships/<collab>.json in place."""
    notices: list[str] = []
    migrate_person_references(payload)
    if not payload.get('schema'):
        payload['schema'] = schema.SCHEMA_TAG
    if payload.get('membership_history') not in schema.MEMBERSHIP_HISTORY_LEVELS:
        payload['membership_history'] = 'unknown'
        notices.append('`membership_history` is required in v0.2; assuming "unknown" (A5)')
    default_class = payload.pop('default_evidence_class', None)
    filled = 0
    for row in payload.get('members') or []:
        if not isinstance(row, dict):
            continue
        if row.get('evidence_class') is None and isinstance(default_class, str):
            row['evidence_class'] = default_class
            filled += 1
    if default_class is not None:
        notices.append(f'`default_evidence_class` is removed in v0.2; copied onto {filled} row(s) (A19)')
    return notices


def migrate_coverage_row(row: dict) -> list[str]:
    """A10 migration of one registry row in place."""
    notices: list[str] = []
    if row.get('entity_id') is None and isinstance(row.get('experiment_id'), str):
        row['entity_id'] = row['experiment_id']
    elif row.get('experiment_id') is None and isinstance(row.get('entity_id'), str):
        row['experiment_id'] = row['entity_id']
    for key in schema.COVERAGE_DERIVED_FIELDS:
        if key in row:
            row.pop(key)
            notices.append(f'`{key}` is a build output, not a registry field; dropped (A10)')
    return notices


# ---------------------------------------------------------------------------
# Per-file loaders
# ---------------------------------------------------------------------------

def _index(atlas: Atlas, path: Path, record: dict, expected_type: str, *, check_filename: bool) -> None:
    entity_id = record.get('id')
    if not isinstance(entity_id, str) or not entity_id:
        atlas.problem(path, 'record has no string "id"')
        return
    prefix_type = schema.id_type(entity_id)
    if prefix_type is None:
        atlas.problem(path, f'id {entity_id!r} has an unknown prefix')
        return
    if prefix_type != expected_type:
        atlas.problem(path, f'id {entity_id!r} belongs in {schema.ENTITY_DIRS[prefix_type]}/, '
                            f'not {schema.ENTITY_DIRS[expected_type]}/')
        return
    if not schema.is_valid_id(entity_id):
        atlas.problem(path, f'id {entity_id!r} is not a lower-case `-` slug with a typed prefix')
    declared = record.get('type')
    expected_declared = (schema.SOURCE_TYPE_FIELD_VALUE if expected_type == 'source' else expected_type)
    if declared != expected_declared:
        atlas.problem(path, f'"type" is {declared!r}; the id prefix says {expected_declared!r}')
    if check_filename and path.stem != schema.filename_for(entity_id):
        atlas.problem(path, f'filename must be {schema.filename_for(entity_id)}.json to match id {entity_id!r}')
    table = atlas.entities[expected_type]
    if entity_id in table:
        atlas.problem(path, f'duplicate id {entity_id!r} (also in {atlas.files.get(entity_id)})')
        return
    table[entity_id] = record
    atlas.files[entity_id] = atlas.relative(path)


def _load_entity(atlas: Atlas, path: Path, payload: Any, entity_type: str) -> None:
    if not isinstance(payload, dict):
        atlas.problem(path, 'entity file must contain one JSON object')
        return
    for notice in migrate_record(payload, entity_type):
        atlas.warn(path, notice)
    _index(atlas, path, payload, entity_type, check_filename=True)


def _load_topics(atlas: Atlas, path: Path, payload: Any) -> None:
    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list):
        atlas.problem(path, 'topics file must contain a JSON list of topic records')
        return
    for index, record in enumerate(payload):
        if not isinstance(record, dict):
            atlas.problem(path, f'topics[{index}] is not an object')
            continue
        record.setdefault('type', 'topic')
        for notice in migrate_record(record, 'topic'):
            atlas.warn(path, f'topics[{index}]: {notice}')
        _index(atlas, path, record, 'topic', check_filename=False)


def _load_membership(atlas: Atlas, path: Path, payload: Any) -> None:
    if not isinstance(payload, dict):
        atlas.problem(path, 'membership file must contain one JSON object')
        return
    for notice in migrate_membership_file(payload):
        atlas.warn(path, notice)
    collaboration_id = payload.get('collaboration_id')
    if not isinstance(collaboration_id, str) or schema.id_type(collaboration_id) != 'collaboration':
        atlas.problem(path, f'"collaboration_id" must be a collaboration: id, got {collaboration_id!r}')
        return
    if path.stem != schema.filename_for(collaboration_id):
        atlas.problem(path, f'filename must be {schema.filename_for(collaboration_id)}.json to match {collaboration_id!r}')
    if collaboration_id in atlas.memberships:
        atlas.problem(path, f'duplicate membership file for {collaboration_id!r} (also {atlas.membership_files[collaboration_id]})')
        return
    if not isinstance(payload.get('members'), list):
        atlas.problem(path, '"members" must be a list')
        payload = {**payload, 'members': []}
    atlas.memberships[collaboration_id] = payload
    atlas.membership_files[collaboration_id] = atlas.relative(path)


def _load_limit(atlas: Atlas, path: Path, payload: Any) -> None:
    """A29: one file per published limit curve (or published minimum), keyed by slug."""
    if not isinstance(payload, dict):
        atlas.problem(path, 'limit file must contain one JSON object')
        return
    slug = payload.get('slug')
    if not isinstance(slug, str) or path.stem != slug:
        atlas.problem(path, f'"slug" must equal the file name ({path.stem!r}), got {slug!r}')
        return
    if slug in atlas.limits:
        atlas.problem(path, f'duplicate limit slug {slug!r}')
        return
    atlas.limits[slug] = payload


def _load_coverage(atlas: Atlas, path: Path, payload: Any) -> None:
    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list):
        atlas.problem(path, 'coverage file must contain a JSON list of registry rows')
        return
    seen = {row.get('entity_id') for row in atlas.coverage}
    for index, row in enumerate(payload):
        if not isinstance(row, dict):
            atlas.problem(path, f'coverage[{index}] is not an object')
            continue
        for notice in migrate_coverage_row(row):
            atlas.warn(path, f'coverage[{index}]: {notice}')
        entity_id = row.get('entity_id')
        if not isinstance(entity_id, str):
            atlas.problem(path, f'coverage[{index}] has no "entity_id" (or legacy "experiment_id")')
            continue
        if entity_id in seen:
            atlas.problem(path, f'duplicate coverage row for {entity_id!r}')
            continue
        seen.add(entity_id)
        atlas.coverage.append({**row, '_file': atlas.relative(path)})
    atlas.coverage.sort(key=lambda row: (row.get('priority') if isinstance(row.get('priority'), int) else 1 << 30,
                                         row['entity_id']))
