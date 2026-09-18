"""Write empty v0.2 skeleton records so a research agent starts from a shape.

    python -m hepgraph.atlas.scaffold experiment dune \\
        --facility fermilab --collaboration dune --site surf-4850-level

Creates, under `data/atlas/` (never overwriting an existing file unless
`--force`):

* `experiments/<slug>.json`      the experiment skeleton
* `collaborations/<collab>.json` its collaboration
* `memberships/<collab>.json`    an empty roster with `membership_history: unknown`
* `facilities/<facility>.json`   its host facility
* `sites/<site>.json`            one site, when `--site` is given
* `sources/<slug>-official-site.json`  a source stub to replace with the real one
* a row in `coverage/<owner>.json` with `researched: "none"`

A skeleton is **deliberately incomplete**: every critical value is `null`
with a note, per ground rule 3 ("unknown is a value") and A17 ("no
from-memory values").  Running the validator on a fresh scaffold therefore
lists exactly the research that has to happen — that is the point.  The one
placeholder that is not null is the source stub's URL, which uses the
reserved `.invalid` TLD so nobody mistakes it for a real citation.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import sys
from pathlib import Path
from typing import Any, Sequence

from . import schema
from .load import DATA_DIR, dump_json

TODO_NOTE = 'TODO: scaffold placeholder; replace with a sourced value or leave null with a note'
PLACEHOLDER_HOST = 'example.invalid'


def _title(slug: str) -> str:
    """A first-guess display name from a slug; the agent corrects it."""
    return ' '.join(part.capitalize() for part in slug.split('-'))


def _common(entity_id: str, entity_type: str, name: str, source_id: str) -> dict:
    return {
        'schema': schema.SCHEMA_TAG,
        'id': entity_id,
        'type': entity_type,
        'name': name,
        'aliases': [],
        'summary': {'plain': '', 'technical': ''},
        'sources': [source_id],
        'links': {'website': None},
        'notes': [TODO_NOTE],
        'coverage': {'tier': 'C', 'researched': 'none'},
    }


def source_stub(slug: str, name: str, *, today: str) -> dict:
    """A placeholder source the agent replaces with the page it actually read."""
    return {
        'schema': schema.SCHEMA_TAG,
        'id': f'src:{slug}-official-site',
        'type': schema.SOURCE_TYPE_FIELD_VALUE,
        'source_type': 'official_experiment_site',
        'title': f'{name} — official site (scaffold placeholder)',
        'publisher': '',
        'url': f'https://{PLACEHOLDER_HOST}/{slug}',
        'reference': {},
        'accessed': today,
        'date': None,
        'excerpt': '',
        'retrieval': None,
        'link_check': {'last_checked': None, 'http_status': None, 'redirect': None},
    }


def experiment_skeleton(slug: str, *, name: str, source_id: str, collaboration: str,
                        facility: str) -> dict:
    record = _common(f'experiment:{slug}', 'experiment', name, source_id)
    record.update({
        'kind': 'other',
        'secondary_kinds': [],
        'collaboration_ids': [f'collaboration:{collaboration}'],
        'facility_roles': [{
            'facility_id': f'facility:{facility}', 'role': 'host',
            'start': None, 'end': None, 'sources': [source_id],
            'verified_at': None, 'confidence': 'uncertain', 'note': TODO_NOTE,
        }],
        'beamline_ids': [],
        'accelerator_ids': [],
        'topic_ids': [],
        'intervals': [],
        'status': None,
        'physics_goals': [],
        'unique_capabilities': [],
        'energy_regime': None,
        'key_specs': [],
        'lineage': [],
        'external': {'inspire_experiment': None, 'greybook': None, 'wikidata': None},
    })
    return record


def collaboration_skeleton(slug: str, *, name: str, source_id: str, facility: str) -> dict:
    record = _common(f'collaboration:{slug}', 'collaboration', f'{name} Collaboration', source_id)
    record.update({
        'formation': None,
        'intervals': [],
        'status': None,
        'membership': {
            'as_of': None,
            'evidence_class': None,
            'institution_count': None,
            'country_count': None,
            'member_count': None,
            'roster_source_ids': [],
        },
        'leadership': [],
        'host_facility_id': f'facility:{facility}',
        'host_site_id': None,
    })
    return record


def facility_skeleton(slug: str, *, source_id: str, primary_site_id: str | None) -> dict:
    record = _common(f'facility:{slug}', 'facility', _title(slug), source_id)
    record.update({
        'kind': 'research_laboratory',
        'operator_text': None,
        'operator_ids': [],
        'country': [],
        'countries': [],
        'primary_site_id': primary_site_id,
        'intervals': [],
        'status': None,
        'specs': {},
        'topic_ids': [],
        'related_facility_ids': [],
    })
    return record


def site_skeleton(slug: str, *, source_id: str, facility: str) -> dict:
    record = _common(f'site:{slug}', 'site', _title(slug), source_id)
    record.update({
        'facility_id': f'facility:{facility}',
        # A21/§9 require real coordinates; the scaffold refuses to invent them.
        'coordinates': None,
        'setting': 'surface',
        'depth': None,
        'depth_rock': None,
        'depth_mwe': None,
        'altitude': None,
        'country': None,
        'countries': [],
        'place': {'city': None, 'region': None, 'country': None},
    })
    return record


def membership_skeleton(collaboration: str, *, source_id: str) -> dict:
    return {
        'schema': schema.SCHEMA_TAG,
        'collaboration_id': f'collaboration:{collaboration}',
        'as_of': None,
        'membership_history': 'unknown',
        'roster_snapshots': [],
        'roster_sources': [source_id],
        'members': [],
    }


def coverage_row(slug: str, *, name: str, facility: str, tier: str, priority: int,
                 owner: str) -> dict:
    """A10: planning fields only — `validated` / `globe_ready` are build outputs."""
    return {
        'name': name,
        'entity_id': f'experiment:{slug}',
        'experiment_id': f'experiment:{slug}',
        'category': 'other',
        'facility': _title(facility),
        'status': None,
        'tier': tier,
        'priority': priority,
        'researched': 'none',
        'missing_fields': [],
        'owner': owner,
        'notes': 'scaffolded; not researched yet',
    }


def scaffold_experiment(data_dir: Path | str, slug: str, *, facility: str, collaboration: str,
                        site: str | None = None, name: str | None = None, tier: str = 'C',
                        priority: int = 50, owner: str = 'unassigned',
                        coverage_file: str | None = None, force: bool = False,
                        dry_run: bool = False, today: _dt.date | None = None) -> dict[str, str]:
    """Write the skeletons and return `{relative path: canonical JSON text}`.

    Existing files are left alone unless `force`; nothing is written when
    `dry_run`.  The returned mapping always describes what *would* be written.
    """
    data_dir = Path(data_dir)
    today_text = (today or _dt.date.today()).isoformat()
    name = name or _title(slug)
    source_id = f'src:{slug}-official-site'
    primary_site_id = f'site:{site}' if site else None

    planned: dict[str, Any] = {
        f'sources/{slug}-official-site.json': source_stub(slug, name, today=today_text),
        f'experiments/{slug}.json': experiment_skeleton(
            slug, name=name, source_id=source_id, collaboration=collaboration, facility=facility),
        f'collaborations/{collaboration}.json': collaboration_skeleton(
            collaboration, name=name, source_id=source_id, facility=facility),
        f'memberships/{collaboration}.json': membership_skeleton(collaboration, source_id=source_id),
        f'facilities/{facility}.json': facility_skeleton(
            facility, source_id=source_id, primary_site_id=primary_site_id),
    }
    if site:
        planned[f'sites/{site}.json'] = site_skeleton(site, source_id=source_id, facility=facility)

    coverage_rel = f'coverage/{coverage_file or owner}.json'
    existing_rows: list[dict] = []
    coverage_path = data_dir / coverage_rel
    if coverage_path.is_file():
        import json
        try:
            loaded = json.loads(coverage_path.read_text(encoding='utf-8'))
            existing_rows = loaded if isinstance(loaded, list) else [loaded]
        except ValueError:
            existing_rows = []
    row = coverage_row(slug, name=name, facility=facility, tier=tier, priority=priority, owner=owner)
    if not any(item.get('entity_id') == row['entity_id'] for item in existing_rows if isinstance(item, dict)):
        existing_rows.append(row)
    existing_rows.sort(key=lambda item: (item.get('priority') if isinstance(item.get('priority'), int)
                                         else 1 << 30, item.get('entity_id') or ''))
    planned[coverage_rel] = existing_rows

    written: dict[str, str] = {}
    for relative, payload in sorted(planned.items()):
        text = dump_json(payload)
        path = data_dir / relative
        is_coverage = relative == coverage_rel
        if path.exists() and not force and not is_coverage:
            continue
        written[relative] = text
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')
    return written


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='python -m hepgraph.atlas.scaffold',
        description='Write empty HEP Atlas v0.2 skeleton records for a new experiment.')
    parser.add_argument('--data', default=str(DATA_DIR), help='atlas data directory')
    subparsers = parser.add_subparsers(dest='command', required=True)

    experiment = subparsers.add_parser('experiment', help='scaffold one experiment and its neighbours')
    experiment.add_argument('slug', help='experiment slug, e.g. dune (no `experiment:` prefix)')
    experiment.add_argument('--facility', required=True, help='host facility slug')
    experiment.add_argument('--collaboration', required=True, help='collaboration slug')
    experiment.add_argument('--site', default=None, help='optional primary site slug')
    experiment.add_argument('--name', default=None, help='display name (default: from the slug)')
    experiment.add_argument('--tier', default='C', choices=list(schema.COVERAGE_TIERS))
    experiment.add_argument('--priority', type=int, default=50)
    experiment.add_argument('--owner', default='unassigned', help='workstream that owns the row')
    experiment.add_argument('--coverage-file', default=None,
                            help='basename under coverage/ (default: the owner)')
    experiment.add_argument('--force', action='store_true', help='overwrite existing files')
    experiment.add_argument('--dry-run', action='store_true', help='print what would be written')
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    data_dir = Path(args.data)
    for slug in (args.slug, args.facility, args.collaboration) + ((args.site,) if args.site else ()):
        if not schema.SLUG_RE.match(slug or ''):
            print(f'not a valid slug: {slug!r} (lower-case, digits and `-` only)', file=sys.stderr)
            return 2
    written = scaffold_experiment(
        data_dir, args.slug, facility=args.facility, collaboration=args.collaboration,
        site=args.site, name=args.name, tier=args.tier, priority=args.priority,
        owner=args.owner, coverage_file=args.coverage_file, force=args.force,
        dry_run=args.dry_run)
    if not written:
        print('nothing to do: every file already exists (use --force to overwrite)')
        return 0
    verb = 'would write' if args.dry_run else 'wrote'
    print(f'{verb} {len(written)} file(s) under {data_dir}:')
    for relative in sorted(written):
        print(f'  {relative}')
    print('\nEvery critical value is null on purpose (A17). Run the validator to see '
          'exactly what still needs research:\n'
          f'  python -m hepgraph.atlas.validate --data {data_dir}')
    return 0


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
