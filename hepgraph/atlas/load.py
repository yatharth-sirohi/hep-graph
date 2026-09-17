"""Load every JSON file under data/atlas/ into one typed in-memory model.

Loading is deliberately forgiving: structural problems that make a file
unusable (unparsable JSON, an id that does not match the filename, an
unknown directory) are *recorded* on the returned `Atlas` instead of raised,
so the validator can list all of them in one report.  Records with a usable
`id` are still indexed so that cross-reference checks can run.

Layout (RESEARCH_AGENT_RULES rule 2; ontology §3):

    data/atlas/<type-plural>/<slug>.json     one entity per file
    data/atlas/topics/*.json                 each a LIST of topic records (§3.10)
    data/atlas/memberships/<collab>.json      one collaboration's roster (§3.11)
    data/atlas/coverage/<workstream>.json     LIST of registry rows (§3.15)
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
    """A file-level defect found while loading (always an error)."""

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
    file-level defects found during loading.
    """

    root: Path
    entities: dict[str, dict[str, dict]] = field(default_factory=lambda: {t: {} for t in schema.ENTITY_TYPES})
    memberships: dict[str, dict] = field(default_factory=dict)
    coverage: list[dict] = field(default_factory=list)
    files: dict[str, str] = field(default_factory=dict)
    membership_files: dict[str, str] = field(default_factory=dict)
    problems: list[LoadProblem] = field(default_factory=list)

    # -- lookups -----------------------------------------------------------
    def get(self, entity_id: str) -> dict | None:
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


def read_json(path: Path) -> Any:
    with path.open('r', encoding='utf-8') as handle:
        return json.load(handle)


def dump_json(value: Any, *, indent: int | None = 2) -> str:
    """Canonical JSON text: sorted keys, UTF-8, trailing newline."""
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
    """Load data/atlas/ (or another root of the same layout)."""
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
        elif directory == 'topics':
            _load_topics(atlas, path, payload)
        elif directory in schema.DIR_TO_TYPE:
            _load_entity(atlas, path, payload, schema.DIR_TO_TYPE[directory])
        else:
            atlas.problem(path, f'unknown directory {directory!r}; expected one of '
                                f'{sorted(schema.DIR_TO_TYPE) + list(schema.AUXILIARY_DIRS)}')
    return atlas


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
    if declared != expected_type:
        atlas.problem(path, f'"type" is {declared!r}; the id prefix says {expected_type!r}')
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
        _index(atlas, path, record, 'topic', check_filename=False)


def _load_membership(atlas: Atlas, path: Path, payload: Any) -> None:
    if not isinstance(payload, dict):
        atlas.problem(path, 'membership file must contain one JSON object')
        return
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


def _load_coverage(atlas: Atlas, path: Path, payload: Any) -> None:
    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list):
        atlas.problem(path, 'coverage file must contain a JSON list of registry rows')
        return
    seen = {row.get('experiment_id') for row in atlas.coverage}
    for index, row in enumerate(payload):
        if not isinstance(row, dict):
            atlas.problem(path, f'coverage[{index}] is not an object')
            continue
        experiment_id = row.get('experiment_id')
        if not isinstance(experiment_id, str):
            atlas.problem(path, f'coverage[{index}] has no "experiment_id"')
            continue
        if experiment_id in seen:
            atlas.problem(path, f'duplicate coverage row for {experiment_id!r}')
            continue
        seen.add(experiment_id)
        atlas.coverage.append({**row, '_file': atlas.relative(path)})
    atlas.coverage.sort(key=lambda row: (row.get('priority') if isinstance(row.get('priority'), int) else 1 << 30,
                                         row['experiment_id']))
