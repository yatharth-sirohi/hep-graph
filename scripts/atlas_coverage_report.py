#!/usr/bin/env python3
"""Regenerate docs/HEP_ATLAS_COVERAGE.md from the coverage registry and data.

Coverage is a claim about the atlas, so it is computed, never typed.  The
report answers, per category: how many experiments are identified, how many are
researched, and what each researched record is still missing (collaboration
membership, historical intervals, major results, technical documents,
placeable geography).

    python scripts/atlas_coverage_report.py [--check]

`--check` exits non-zero when the committed document differs from what the data
implies, so the document cannot drift away from the registry.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from hepgraph.atlas import load  # noqa: E402

DOC = ROOT / 'docs' / 'HEP_ATLAS_COVERAGE.md'

CATEGORY_TITLES = {
    'collider': 'Colliders',
    'accelerator_neutrino': 'Accelerator neutrinos',
    'reactor_neutrino': 'Reactor and low-energy neutrinos',
    'solar_neutrino': 'Solar and radiochemical neutrinos',
    'atmospheric_neutrino': 'Atmospheric neutrinos',
    'astrophysical_neutrino': 'High-energy and astrophysical neutrinos',
    'neutrino_mass': 'Direct neutrino mass',
    'double_beta_decay': 'Neutrinoless double beta decay',
    'direct_dark_matter': 'Dark matter direct detection',
    'axion': 'Axions and ALPs',
    'muon_precision': 'Muon precision and rare processes',
    'fixed_target': 'Fixed target, rare kaons and long-lived particles',
    'cevns': 'Coherent elastic neutrino-nucleus scattering',
    'cosmic_ray': 'Cosmic rays, gamma rays and astroparticle',
    'gamma_ray': 'Gamma rays',
    'heavy_ion': 'Heavy ions',
    'other': 'Other',
}


def missing_fields(atlas, experiment_id: str) -> list[str]:
    """What a researched experiment still lacks, computed from the data."""
    record = atlas.get(experiment_id)
    if record is None:
        return ['record']
    gaps = []
    if not record.get('collaboration_ids'):
        gaps.append('collaboration')
    else:
        rosters = [c for c in record['collaboration_ids'] if c in atlas.memberships]
        if not rosters:
            gaps.append('institution membership')
    if len(record.get('intervals') or []) < 2:
        gaps.append('historical intervals')
    detectors = [d for d in atlas.by_type('detector').values()
                 if experiment_id in (d.get('experiment_ids') or [])]
    if not detectors:
        gaps.append('detector')
    else:
        placed = False
        for detector in detectors:
            for placement in detector.get('placements') or []:
                site = atlas.get(placement.get('site_id') or '')
                if site and (site.get('coordinates') or {}).get('lat') is not None:
                    placed = True
        if not placed:
            gaps.append('placeable geography')
    results = [r for r in atlas.by_type('result').values()
               if experiment_id in [x if isinstance(x, str) else x.get('id')
                                    for x in (r.get('experiment_ids') or [])]]
    if not results:
        gaps.append('major results')
    documents = [d for d in atlas.by_type('document').values()
                 if experiment_id in (d.get('owner_ids') or [])]
    if not documents:
        gaps.append('technical documents')
    if not (record.get('summary') or {}).get('plain'):
        gaps.append('plain-language summary')
    if not record.get('topic_ids'):
        gaps.append('research topics')
    return gaps


# Wave-1 and wave-2 workstreams were independently reviewed before the
# per-domain VERIFY_ reports existed; these are the reports that covered them.
EARLIER_REVIEWS: dict[str, str] = {
    'dark-matter': 'REVIEW_data_quality_wave1.md',
    'icecube': 'REVIEW_data_quality_wave1.md',
    'flavor': 'REVIEW_data_quality_wave1.md',
    'cern-cms': 'REVIEW_data_quality_wave1.md',
    'dune-atlas-completion': 'REVIEW_scientific.md',
    'fermilab-neutrino-other': 'REVIEW_scientific.md',
    'japan-neutrino': 'REVIEW_scientific.md',
    'historic-cern': 'REVIEW_scientific.md',
}


def render(atlas) -> str:
    rows = list(atlas.coverage)
    by_category: dict[str, list[dict]] = {}
    for row in rows:
        by_category.setdefault(row.get('category') or 'other', []).append(row)

    today = dt.date.today().isoformat()
    counts = {entity_type: len(table) for entity_type, table in atlas.entities.items()}
    member_rows = sum(len(roster.get('members', [])) for roster in atlas.memberships.values())

    out = [
        '# HEP Atlas coverage',
        '',
        f'Generated {today} by `scripts/atlas_coverage_report.py`. Every number here is',
        'computed from `data/atlas/`; none of it is asserted by hand. The atlas does not',
        'claim to contain every experiment in experimental high-energy physics, and the',
        'interface says only "coverage updated" with this date.',
        '',
        '## Entities in the atlas',
        '',
        '| Type | Count |',
        '| --- | ---: |',
    ]
    for entity_type in sorted(counts):
        out.append(f'| {entity_type} | {counts[entity_type]} |')
    out += [
        f'| membership rows | {member_rows} |',
        '',
        '## Coverage by tier',
        '',
        'Tier A experiments are flagships researched to full depth (results, technical',
        'documents, key specifications); tiers B–D are researched to the mandatory bar',
        '(identity, status, dated intervals, a located site, topics, summaries, an',
        'official site, at least one authoritative source, a collaboration where one',
        'exists) unless the row says otherwise. "Full" and "partial" are the',
        'researcher\'s own claim in the registry row; the per-experiment table below',
        'lists what each record still lacks regardless of that claim.',
        '',
        '| Tier | Rows | Researched: full | Researched: partial | Not researched |',
        '| --- | ---: | ---: | ---: | ---: |',
    ]
    tiers: dict[str, dict[str, int]] = {}
    for row in rows:
        bucket = tiers.setdefault(str(row.get('tier') or '?'), {'full': 0, 'partial': 0, 'none': 0})
        state = row.get('researched') or 'none'
        bucket[state if state in bucket else 'none'] += 1
    for tier in sorted(tiers):
        bucket = tiers[tier]
        out.append(f'| {tier} | {sum(bucket.values())} | {bucket["full"]} | {bucket["partial"]} | {bucket["none"]} |')
    out += [
        '',
        '## Independent verification by workstream',
        '',
        'A workstream is independently verified when a different agent re-fetched its',
        'cited sources and left a report at `docs/atlas-worklog/VERIFY_<owner>.md`.',
        'Rows without one were verified only by their researcher and the validator.',
        '',
        '| Workstream (owner) | Experiments | Independently verified |',
        '| --- | ---: | --- |',
    ]
    owners: dict[str, int] = {}
    for row in rows:
        owners[str(row.get('owner') or 'unassigned')] = owners.get(str(row.get('owner') or 'unassigned'), 0) + 1
    worklog_dir = Path(__file__).resolve().parents[1] / 'docs' / 'atlas-worklog'
    for owner in sorted(owners):
        report = None
        if (worklog_dir / f'VERIFY_{owner}.md').is_file():
            report = f'VERIFY_{owner}.md'
        elif owner in EARLIER_REVIEWS and (worklog_dir / EARLIER_REVIEWS[owner]).is_file():
            report = EARLIER_REVIEWS[owner]
        out.append(f'| {owner} | {owners[owner]} | {"yes — " + report if report else "no"} |')
    out += [
        '',
        '## Coverage by category',
        '',
        'Identified means the experiment is in the registry. Researched means a record',
        'exists with sourced content. Gaps are computed per record, not declared.',
        '',
        '| Category | Identified | Researched | Fully complete | Missing membership | Missing history | Missing results | Missing documents |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |',
    ]

    totals = dict(identified=0, researched=0, complete=0, membership=0, history=0, results=0, documents=0)
    detail_lines: list[str] = []
    for category in sorted(by_category, key=lambda c: CATEGORY_TITLES.get(c, c)):
        group = by_category[category]
        identified = len(group)
        researched = 0
        complete = 0
        gap_counts = dict(membership=0, history=0, results=0, documents=0)
        details = []
        for row in sorted(group, key=lambda r: r.get('name') or r.get('entity_id', '')):
            entity_id = row.get('entity_id') or row.get('experiment_id') or ''
            present = atlas.get(entity_id) is not None
            if not present:
                details.append((row.get('name') or entity_id, 'not researched', ['all']))
                continue
            researched += 1
            gaps = missing_fields(atlas, entity_id)
            if not gaps:
                complete += 1
            if 'institution membership' in gaps or 'collaboration' in gaps:
                gap_counts['membership'] += 1
            if 'historical intervals' in gaps:
                gap_counts['history'] += 1
            if 'major results' in gaps:
                gap_counts['results'] += 1
            if 'technical documents' in gaps:
                gap_counts['documents'] += 1
            details.append((row.get('name') or entity_id, 'researched', gaps or ['—']))
        out.append(
            f'| {CATEGORY_TITLES.get(category, category)} | {identified} | {researched} | '
            f'{complete} | {gap_counts["membership"]} | {gap_counts["history"]} | '
            f'{gap_counts["results"]} | {gap_counts["documents"]} |')
        totals['identified'] += identified
        totals['researched'] += researched
        totals['complete'] += complete
        for key in ('membership', 'history', 'results', 'documents'):
            totals[key] += gap_counts[key]

        detail_lines.append('')
        detail_lines.append(f'### {CATEGORY_TITLES.get(category, category)}')
        detail_lines.append('')
        detail_lines.append('| Experiment | State | Still missing |')
        detail_lines.append('| --- | --- | --- |')
        for name, state, gaps in details:
            detail_lines.append(f'| {name} | {state} | {", ".join(gaps)} |')

    out.append(
        f'| **All** | **{totals["identified"]}** | **{totals["researched"]}** | '
        f'**{totals["complete"]}** | **{totals["membership"]}** | **{totals["history"]}** | '
        f'**{totals["results"]}** | **{totals["documents"]}** |')
    out += ['', '## Per-experiment detail', '']
    out += detail_lines
    out += ['', '## What is deliberately out of scope', '',
            'See `docs/HEP_ATLAS_RESEARCH_METHOD.md` for the scope boundary and the',
            'reasons behind each inclusion and exclusion.', '']
    return '\n'.join(out) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true',
                        help='fail when the committed document is out of date')
    args = parser.parse_args()
    atlas = load.load_atlas()
    text = render(atlas)
    if args.check:
        current = DOC.read_text() if DOC.exists() else ''
        # The generation date changes daily; compare everything else.
        strip = lambda s: '\n'.join(line for line in s.splitlines() if not line.startswith('Generated '))
        if strip(current) != strip(text):
            print('docs/HEP_ATLAS_COVERAGE.md is out of date; run scripts/atlas_coverage_report.py')
            return 1
        print('coverage report is current')
        return 0
    DOC.write_text(text)
    print(f'wrote {DOC.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
