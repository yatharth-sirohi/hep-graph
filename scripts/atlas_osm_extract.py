#!/usr/bin/env python3
"""Draft geometry records for one campus from OpenStreetMap (A25).

This is a **maintainer helper**, not part of the pipeline: it fetches shapes
from Overpass, measures them, and writes *draft* `geometry` and `src:` records
a researcher then edits, checks against an official figure, and commits by
hand.  Nothing it writes is publishable as it stands — every draft is
`confidence: approximate` and carries a `TODO` telling the researcher what is
still missing.  The contract it drafts against is
`docs/HEP_ATLAS_GEOMETRY.md`; §5 of that document is the method this script
serves one step of.

    # every building and the ring tunnel inside a bounding box
    python scripts/atlas_osm_extract.py --map cern \
        --bbox 46.22,6.03,46.26,6.08 \
        --filter 'way["building"]' --filter 'relation["railway"="rail"]'

    # named elements, when you already know them
    python scripts/atlas_osm_extract.py --map cern --ids relation/9512017,way/123456

Output goes to a scratch directory (`--out`, default a temporary directory
that is printed), never to `data/atlas/` unless `--write-data` is passed and
the target files do not already exist.  Raw Overpass JSON is saved next to the
drafts so a reviewer can see exactly what came back.

Rules this script keeps, because the contract does:

* **One request.**  Overpass is a donated public service; the script issues a
  single query per run, with a 90-second timeout and an honest User-Agent, and
  it never retries in a loop.
* **The licence travels with the data.**  Every draft carries
  `license: ODbL-1.0` with the attribution string, `osm.elements` and the
  extract timestamp, and the source record is `source_type: openstreetmap`
  (rank 11) — which is why no draft it writes can be `verified`.
* **It measures, it does not judge.**  The length or perimeter of every shape
  is printed so the researcher can compare it with the official figure and
  write the `checks[]` row.  The script never invents that row.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from hepgraph.atlas import geo, load, schema  # noqa: E402

OVERPASS_URL = 'https://overpass-api.de/api/interpreter'
USER_AGENT = 'HEP-Atlas-research/1.0'
TIMEOUT_S = 90

#: What the browser and the validator both expect to see on OSM-derived data.
LICENSE = {
    'name': schema.ODBL_LICENSE_NAME,
    'attribution': schema.OSM_ATTRIBUTION,
    'url': 'https://www.openstreetmap.org/copyright',
}

#: A first guess at `feature_type` from OSM tags.  Deliberately shallow: the
#: researcher decides, and a wrong guess left in a draft is worse than `other`.
TAG_FEATURE_TYPES: tuple[tuple[str, str, str], ...] = (
    ('building', '*', 'building'),
    ('man_made', 'tunnel', 'tunnel'),
    ('tunnel', '*', 'tunnel'),
    ('railway', '*', 'other'),
    ('landuse', '*', 'boundary'),
    ('natural', 'water', 'water'),
    ('highway', '*', 'road'),
)

#: Accuracy floors from §1.2, by the kind of shape OSM gave us.  Honest and
#: rounded up: a researcher may raise these, never quietly lower them.
DEFAULT_ACCURACY_M: dict[str, int] = {
    'building': 10,
    'tunnel': 30,
    'road': 15,
    'water': 20,
    'boundary': 20,
    'other': 20,
}


# ---------------------------------------------------------------------------
# Overpass
# ---------------------------------------------------------------------------

def build_query(*, bbox: str | None, filters: list[str], ids: list[str]) -> str:
    """The single Overpass QL query this run will issue."""
    parts: list[str] = []
    if ids:
        for element in ids:
            kind, _, number = element.partition('/')
            parts.append(f'{kind}({number});')
    else:
        south, west, north, east = bbox.split(',')
        box = f'({south},{west},{north},{east})'
        for expression in filters:
            parts.append(f'{expression}{box};')
    body = '\n  '.join(parts)
    return f'[out:json][timeout:{TIMEOUT_S}];\n(\n  {body}\n);\nout body geom;'


def fetch(query: str, *, url: str = OVERPASS_URL) -> dict:
    """Issue the one Overpass request of this run."""
    request = urllib.request.Request(
        url,
        data=query.encode('utf-8'),
        headers={'User-Agent': USER_AGENT, 'Content-Type': 'text/plain; charset=utf-8'},
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
        return json.loads(response.read().decode('utf-8'))


# ---------------------------------------------------------------------------
# Overpass elements -> GeoJSON
# ---------------------------------------------------------------------------

def _ring(points: list[dict]) -> list[list[float]]:
    ring = [[round(float(p['lon']), 7), round(float(p['lat']), 7)] for p in points
            if isinstance(p, dict) and 'lat' in p and 'lon' in p]
    if len(ring) >= 3 and ring[0] != ring[-1]:
        ring.append(list(ring[0]))
    return ring


def element_geometry(element: dict) -> Any:
    """The GeoJSON geometry of one `out geom` element, or None.

    A closed way with an area-ish tag becomes a Polygon; any other closed or
    open way a LineString; a relation the MultiLineString of its members,
    since merging members into rings is a judgement the researcher makes with
    the campus in front of them, not something to guess here.
    """
    kind = element.get('type')
    if kind == 'node' and 'lat' in element and 'lon' in element:
        return {'type': 'Point',
                'coordinates': [round(float(element['lon']), 7), round(float(element['lat']), 7)]}
    if kind == 'way':
        points = element.get('geometry') or []
        line = [[round(float(p['lon']), 7), round(float(p['lat']), 7)] for p in points
                if isinstance(p, dict) and 'lat' in p and 'lon' in p]
        if len(line) < 2:
            return None
        tags = element.get('tags') or {}
        closed = line[0] == line[-1]
        areal = any(key in tags for key in ('building', 'landuse', 'area', 'amenity'))
        if closed and areal and len(line) >= 4:
            return {'type': 'Polygon', 'coordinates': [line]}
        return {'type': 'LineString', 'coordinates': line}
    if kind == 'relation':
        lines = []
        for member in element.get('members') or []:
            points = member.get('geometry') or []
            line = [[round(float(p['lon']), 7), round(float(p['lat']), 7)] for p in points
                    if isinstance(p, dict) and 'lat' in p and 'lon' in p]
            if len(line) >= 2:
                lines.append(line)
        if not lines:
            return None
        return {'type': 'MultiLineString', 'coordinates': lines}
    return None


def guess_feature_type(tags: dict) -> str:
    for key, wanted, feature_type in TAG_FEATURE_TYPES:
        value = tags.get(key)
        if value is not None and (wanted == '*' or value == wanted):
            return feature_type
    return 'other'


def slugify(text: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', str(text or '').lower()).strip('-')
    return slug or 'unnamed'


# ---------------------------------------------------------------------------
# Drafts
# ---------------------------------------------------------------------------

def source_id_for(map_slug: str, element: str) -> str:
    kind, _, number = element.partition('/')
    return f'src:osm-{map_slug}-{kind}-{number}'


def draft_source(map_slug: str, element: str, tags: dict, timestamp: str, today: str) -> dict:
    kind, _, number = element.partition('/')
    name = tags.get('name') or tags.get('ref') or element
    return {
        'id': source_id_for(map_slug, element),
        'type': 'src',
        'schema': schema.SCHEMA_TAG,
        'source_type': 'openstreetmap',
        'title': f'OpenStreetMap {kind} {number} — {name}',
        'publisher': 'OpenStreetMap contributors',
        'url': f'https://www.openstreetmap.org/{kind}/{number}',
        'accessed': today,
        'date': timestamp[:10] if timestamp else today,
        'retrieval': 'full_text',
        'excerpt': ', '.join(f'{key}={value}' for key, value in sorted(tags.items()))[:schema.EXCERPT_MAX_CHARS],
        'reference': {},
        'link_check': {'http_status': None, 'last_checked': None, 'redirect': None},
    }


def draft_geometry(map_slug: str, element: str, geometry: Any, tags: dict,
                   timestamp: str, today: str, level_id: str) -> dict:
    kind, _, number = element.partition('/')
    name = tags.get('name') or tags.get('ref') or f'{kind} {number}'
    feature_type = guess_feature_type(tags)
    slug = f'{map_slug}-{slugify(name)}-{kind}-{number}'
    tag_text = ', '.join(f'{key}={value}' for key, value in sorted(tags.items())) or 'no tags'
    return {
        'id': f'geometry:{slug}',
        'type': 'geometry',
        'schema': schema.SCHEMA_TAG,
        'name': str(name),
        'aliases': [],
        'map_id': f'map:{map_slug}',
        'entity_id': None,
        'site_id': None,
        'feature_type': feature_type,
        'level_id': level_id,
        'depth_m': None,
        'representation': 'georeferenced',
        'accuracy_m': DEFAULT_ACCURACY_M.get(feature_type, 20),
        'method': f'OpenStreetMap {kind} {number} ({tag_text}); nodes kept verbatim from an '
                  f'Overpass extract. TODO: say what was merged or simplified, if anything.',
        'geometry': {
            'value': geometry,
            'sources': [source_id_for(map_slug, element)],
            'verified_at': today,
            'confidence': 'approximate',
            'locator': f'OSM {kind}/{number} as of {timestamp or today}',
            'note': 'Traced by OpenStreetMap contributors; no official figure confirms it yet, '
                    'so it stays approximate (A25: OSM alone is rank 11).',
        },
        'checks': [],
        'valid': None,
        'license': dict(LICENSE),
        'osm': {'elements': [element], 'timestamp': timestamp or None},
        'summary': {'plain': f'TODO: one plain sentence about {name}.'},
        'sources': [source_id_for(map_slug, element)],
        'links': {'website': None},
        'notes': [
            'DRAFT from scripts/atlas_osm_extract.py. Before committing: set `entity_id` '
            '(or leave null for a context feature), set `level_id`, check `feature_type` and '
            '`accuracy_m`, add a `checks[]` row against an independent official figure, and '
            'write the summary. See docs/HEP_ATLAS_GEOMETRY.md.',
        ],
        'coverage': {'tier': 'C', 'researched': 'partial'},
    }


# ---------------------------------------------------------------------------
# Running
# ---------------------------------------------------------------------------

def measurements(geometry: Any) -> str:
    """The one line per shape a researcher compares with the official figure."""
    kind = (geometry or {}).get('type')
    length = geo.geometry_length_m(geometry)
    area = geo.geometry_area_m2(geometry)
    span = geo.geometry_span_m(geometry)
    parts = [f'{kind}', f'{len(geo.positions(geometry))} vertices']
    if length is not None:
        parts.append(f'{"perimeter" if area is not None else "length"} {length:,.1f} m')
    if area is not None:
        parts.append(f'area {area:,.0f} m²')
    if span is not None:
        parts.append(f'span {span:,.1f} m')
    return ' · '.join(parts)


def process(payload: dict, *, map_slug: str, level_id: str, today: str) -> tuple[list[dict], list[dict], list[str]]:
    """Turn an Overpass response into draft records plus the report lines."""
    timestamp = str(payload.get('osm3s', {}).get('timestamp_osm_base') or '')
    geometries: list[dict] = []
    sources: list[dict] = []
    lines: list[str] = []
    for element in payload.get('elements') or []:
        if not isinstance(element, dict):
            continue
        name = f"{element.get('type')}/{element.get('id')}"
        geometry = element_geometry(element)
        if geometry is None:
            lines.append(f'  skipped {name}: no usable geometry in the response')
            continue
        problems = geo.geojson_problems(geometry)
        if problems:
            lines.append(f'  skipped {name}: {problems[0]}')
            continue
        tags = element.get('tags') or {}
        geometries.append(draft_geometry(map_slug, name, geometry, tags, timestamp, today, level_id))
        sources.append(draft_source(map_slug, name, tags, timestamp, today))
        lines.append(f'  {name}: {measurements(geometry)}')
    return geometries, sources, lines


def write_drafts(out_dir: Path, geometries: list[dict], sources: list[dict], *,
                 overwrite: bool) -> list[str]:
    written: list[str] = []
    for record, directory in ((g, 'geometry') for g in geometries):
        target = out_dir / directory / f'{schema.filename_for(record["id"])}.json'
        if target.exists() and not overwrite:
            print(f'refusing to overwrite {target}', file=sys.stderr)
            continue
        load.write_json(target, record)
        written.append(str(target))
    for record in sources:
        target = out_dir / 'sources' / f'{schema.filename_for(record["id"])}.json'
        if target.exists() and not overwrite:
            print(f'refusing to overwrite {target}', file=sys.stderr)
            continue
        load.write_json(target, record)
        written.append(str(target))
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='python scripts/atlas_osm_extract.py',
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--map', required=True, metavar='SLUG',
                        help='the map slug the drafts belong to (map:<slug>)')
    parser.add_argument('--bbox', metavar='S,W,N,E',
                        help='bounding box, south,west,north,east in degrees')
    parser.add_argument('--filter', action='append', default=[], metavar='QL',
                        help='an Overpass QL element filter, e.g. \'way["building"]\' '
                             '(repeatable; combined into one query)')
    parser.add_argument('--ids', metavar='LIST',
                        help='comma-separated element ids instead of a bbox query, '
                             'e.g. way/123,relation/456')
    parser.add_argument('--level', default='surface', metavar='ID',
                        help='the map level the drafts name (default: %(default)s)')
    parser.add_argument('--out', metavar='DIR',
                        help='where to write the drafts (default: a scratch directory)')
    parser.add_argument('--write-data', action='store_true',
                        help='write into data/atlas/ instead of a scratch directory; '
                             'existing files are never overwritten')
    parser.add_argument('--overwrite', action='store_true',
                        help='allow replacing drafts already in the output directory')
    parser.add_argument('--query-only', action='store_true',
                        help='print the Overpass query and exit without fetching')
    parser.add_argument('--from-json', metavar='FILE',
                        help='process a saved Overpass response instead of fetching')
    arguments = parser.parse_args(argv)

    ids = [item.strip() for item in (arguments.ids or '').split(',') if item.strip()]
    if not ids and not (arguments.bbox and arguments.filter):
        parser.error('give either --ids, or --bbox together with at least one --filter')
    query = build_query(bbox=arguments.bbox, filters=arguments.filter, ids=ids)
    if arguments.query_only:
        print(query)
        return 0

    if arguments.from_json:
        payload = json.loads(Path(arguments.from_json).read_text(encoding='utf-8'))
    else:
        print(f'one Overpass request, {TIMEOUT_S} s timeout, User-Agent {USER_AGENT}')
        try:
            payload = fetch(query)
        except (urllib.error.URLError, OSError, ValueError) as exc:
            print(f'Overpass request failed: {exc}', file=sys.stderr)
            print('This is an error, not an empty result: nothing was written.', file=sys.stderr)
            return 1

    today = dt.date.today().isoformat()
    geometries, sources, lines = process(payload, map_slug=arguments.map,
                                         level_id=arguments.level, today=today)

    if arguments.write_data:
        out_dir = load.DATA_DIR
    elif arguments.out:
        out_dir = Path(arguments.out)
    else:
        out_dir = Path(tempfile.mkdtemp(prefix=f'atlas-osm-{arguments.map}-'))

    out_dir.mkdir(parents=True, exist_ok=True)
    load.write_json(out_dir / 'overpass-response.json', payload)

    print(f'\n{len(geometries)} draft feature(s) from {len(payload.get("elements") or [])} element(s):')
    for line in lines:
        print(line)

    written = write_drafts(out_dir, geometries, sources,
                           overwrite=arguments.overwrite and not arguments.write_data)
    print(f'\nwrote {len(written)} draft file(s) under {out_dir}')
    print('Every draft is `confidence: approximate` and carries a TODO note. Before committing:')
    print('  1. compare each measurement above with an official published figure and write')
    print('     the `checks[]` row that cites it (docs/HEP_ATLAS_GEOMETRY.md §1.2);')
    print('  2. set `entity_id`, `level_id`, `feature_type` and an honest `accuracy_m`;')
    print('  3. run `python -m hepgraph.atlas.validate` and fix every error.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
