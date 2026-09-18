"""Pilot acceptance test for HEP Atlas.

The product specification fixes a gate before the atlas may be expanded beyond
its pilot: DUNE, ATLAS and T2K must each answer a fixed list of questions from
the canonical data alone.  These tests read `data/atlas/` through the ordinary
loader — not the generated bundles — so a failure points at the research data,
not at the build.

Each test is skipped while its experiment is absent, so the file is useful from
the first day of research and becomes a real gate as records land.  Nothing
here asserts a physics value; the scientific reviewers do that.  These
assertions are about *structure being answerable*: is the near detector
somewhere, is the beamline attached, does the baseline exist as a quantity, are
there institutions, documents, intervals.
"""
from __future__ import annotations

import pytest

from hepgraph.atlas import load, schema


@pytest.fixture(scope='module')
def atlas():
    return load.load_atlas()


def experiment(atlas, experiment_id):
    record = atlas.get(experiment_id)
    if record is None:
        pytest.skip(f'{experiment_id} has not been researched yet')
    return record


def sites_of(atlas, experiment_id):
    """Every site a detector of this experiment has been placed at."""
    found = []
    for detector in atlas.by_type('detector').values():
        if experiment_id not in detector.get('experiment_ids', []):
            continue
        for placement in detector.get('placements', []) or []:
            site_id = placement.get('site_id')
            if site_id:
                found.append((detector['id'], placement.get('role'), site_id))
    return found


def documents_of(atlas, entity_id):
    return [doc for doc in atlas.by_type('document').values()
            if entity_id in doc.get('owner_ids', [])]


def results_of(atlas, experiment_id):
    return [row for row in atlas.by_type('result').values()
            if experiment_id in [r if isinstance(r, str) else r.get('id')
                                 for r in row.get('experiment_ids', [])]]


def has_coordinates(atlas, site_id):
    site = atlas.get(site_id)
    return bool(site and isinstance(site.get('coordinates'), dict)
                and site['coordinates'].get('lat') is not None)


# --- DUNE -----------------------------------------------------------------

def test_dune_has_near_and_far_detectors_at_located_sites(atlas):
    experiment(atlas, 'experiment:dune')
    placements = sites_of(atlas, 'experiment:dune')
    roles = {role for _, role, _ in placements}
    assert 'near' in roles, 'DUNE has no detector placed with role "near"'
    assert 'far' in roles, 'DUNE has no detector placed with role "far"'
    for detector_id, _role, site_id in placements:
        assert has_coordinates(atlas, site_id), (
            f'{detector_id} is placed at {site_id}, which has no coordinates')


def test_dune_far_site_is_underground_and_distinct_from_fermilab(atlas):
    experiment(atlas, 'experiment:dune')
    far = [site_id for _, role, site_id in sites_of(atlas, 'experiment:dune') if role == 'far']
    near = [site_id for _, role, site_id in sites_of(atlas, 'experiment:dune') if role == 'near']
    assert far and near
    assert set(far).isdisjoint(near), 'DUNE near and far detectors share a site'
    for site_id in far:
        site = atlas.get(site_id)
        assert site.get('setting') == 'underground', f'{site_id} is not underground'


def test_dune_beamline_connects_the_two_sites_with_a_sourced_baseline(atlas):
    record = experiment(atlas, 'experiment:dune')
    beamline_ids = [b if isinstance(b, str) else b.get('id')
                    for b in record.get('beamline_ids', [])]
    assert beamline_ids, 'DUNE lists no beamline'
    baselines = []
    for beamline_id in beamline_ids:
        beamline = atlas.get(beamline_id)
        assert beamline is not None, f'{beamline_id} is referenced but missing'
        baselines.extend(beamline.get('baselines', []) or [])
    assert baselines, 'no baseline recorded on any DUNE beamline'
    for baseline in baselines:
        distance = baseline.get('distance') or {}
        assert distance.get('dimension') == 'length'
        assert distance.get('sources'), 'the DUNE baseline carries no source'


def test_dune_detector_technology_and_mass_are_recorded(atlas):
    experiment(atlas, 'experiment:dune')
    far_detectors = [atlas.get(detector_id)
                     for detector_id, role, _ in sites_of(atlas, 'experiment:dune')
                     if role == 'far']
    assert far_detectors
    for detector in far_detectors:
        assert detector.get('technology'), f"{detector['id']} has no technology"
        specs = detector.get('specs') or {}
        assert any(key in specs for key in ('total_mass', 'active_mass', 'fiducial_mass')), (
            f"{detector['id']} records no mass")


def test_dune_has_collaboration_documents_intervals_and_goals(atlas):
    record = experiment(atlas, 'experiment:dune')
    assert record.get('collaboration_ids'), 'DUNE has no collaboration'
    assert len(record.get('intervals', [])) >= 2, 'DUNE history is a single interval'
    assert record.get('physics_goals'), 'DUNE records no physics goals'
    assert documents_of(atlas, 'experiment:dune'), 'DUNE has no technical documents'


def test_dune_collaboration_has_member_institutions_with_coordinates(atlas):
    experiment(atlas, 'experiment:dune')
    roster = atlas.memberships.get('collaboration:dune')
    if roster is None:
        pytest.skip('the DUNE roster has not been ingested yet')
    members = roster.get('members', [])
    assert len(members) >= 20, f'only {len(members)} DUNE member institutions'
    placed = 0
    for row in members:
        institution = atlas.get(row.get('institution_id', ''))
        if institution and (institution.get('coordinates') or {}).get('lat') is not None:
            placed += 1
    assert placed >= len(members) * 0.8, (
        f'only {placed} of {len(members)} DUNE institutions can be placed on the globe')


# --- ATLAS ----------------------------------------------------------------

def test_atlas_is_at_cern_and_linked_to_the_lhc(atlas):
    record = experiment(atlas, 'experiment:atlas')
    facilities = [row if isinstance(row, str) else row.get('facility_id')
                  for row in record.get('facility_roles', [])]
    assert 'facility:cern' in facilities, 'ATLAS is not hosted at CERN'
    accelerators = [a if isinstance(a, str) else a.get('id')
                    for a in record.get('accelerator_ids', [])]
    assert 'accelerator:lhc' in accelerators, 'ATLAS is not linked to the LHC'


def test_atlas_detector_is_placed_and_described(atlas):
    experiment(atlas, 'experiment:atlas')
    placements = sites_of(atlas, 'experiment:atlas')
    assert placements, 'no ATLAS detector placement'
    for detector_id, _role, site_id in placements:
        assert has_coordinates(atlas, site_id), f'{detector_id} sits at an unlocated site'
        detector = atlas.get(detector_id)
        assert (detector.get('specs') or {}), f'{detector_id} has no specifications'


def test_atlas_timeline_spans_construction_to_running(atlas):
    record = experiment(atlas, 'experiment:atlas')
    statuses = {interval.get('status') for interval in record.get('intervals', [])}
    assert {'construction'} & statuses, 'ATLAS has no construction interval'
    assert {'active'} & statuses, 'ATLAS has no operating interval'
    assert len(record.get('intervals', [])) >= 4, 'ATLAS history is too coarse'


def test_atlas_was_not_operating_in_1990(atlas):
    record = experiment(atlas, 'experiment:atlas')
    state = schema.state_at(record, '1990') if hasattr(schema, 'state_at') else None
    if state is None:
        return
    assert state.get('status') not in {'active', 'commissioning', 'shutdown'}, (
        f"ATLAS is shown as {state.get('status')} in 1990")


def test_atlas_has_curated_results_with_sources(atlas):
    experiment(atlas, 'experiment:atlas')
    results = results_of(atlas, 'experiment:atlas')
    assert results, 'ATLAS has no major results'
    for result in results:
        assert result.get('sources'), f"{result['id']} has no sources"
        assert result.get('result_type') in schema.RESULT_TYPES
        assert (result.get('publication') or result.get('publication_source_id')
                or (result.get('official_url') or {}).get('value')), (
            f"{result['id']} cannot be opened by a reader")


def test_atlas_collaboration_is_geographically_distributed(atlas):
    experiment(atlas, 'experiment:atlas')
    roster = atlas.memberships.get('collaboration:atlas')
    if roster is None:
        pytest.skip('the ATLAS roster has not been ingested yet')
    countries = set()
    for row in roster.get('members', []):
        institution = atlas.get(row.get('institution_id', ''))
        if institution:
            countries.update(institution.get('countries') or [])
    assert len(countries) >= 10, f'ATLAS spans only {len(countries)} countries in the data'


# --- T2K ------------------------------------------------------------------

def test_t2k_runs_from_jparc_to_kamioka(atlas):
    record = experiment(atlas, 'experiment:t2k')
    facilities = [row if isinstance(row, str) else row.get('facility_id')
                  for row in record.get('facility_roles', [])]
    assert any('j-parc' in f for f in facilities), 'T2K has no J-PARC role'
    site_ids = {site_id for _, _, site_id in sites_of(atlas, 'experiment:t2k')}
    assert any('kamioka' in site_id for site_id in site_ids), (
        'T2K has no detector placed at Kamioka')


def test_t2k_baseline_is_recorded_with_a_source(atlas):
    record = experiment(atlas, 'experiment:t2k')
    beamline_ids = [b if isinstance(b, str) else b.get('id')
                    for b in record.get('beamline_ids', [])]
    assert beamline_ids, 'T2K lists no beamline'
    baselines = []
    for beamline_id in beamline_ids:
        beamline = atlas.get(beamline_id)
        assert beamline is not None
        baselines.extend(beamline.get('baselines', []) or [])
    assert baselines, 'the T2K beamline records no baseline'
    assert all((baseline.get('distance') or {}).get('sources') for baseline in baselines)


def test_t2k_has_timeline_results_and_documents(atlas):
    record = experiment(atlas, 'experiment:t2k')
    assert len(record.get('intervals', [])) >= 2
    assert results_of(atlas, 'experiment:t2k'), 'T2K has no major results'
    assert documents_of(atlas, 'experiment:t2k'), 'T2K has no technical documents'


# --- cross-cutting pilot guarantees ---------------------------------------

def test_every_pilot_experiment_can_be_summarised_for_a_newcomer(atlas):
    for experiment_id in ('experiment:dune', 'experiment:atlas', 'experiment:t2k'):
        record = atlas.get(experiment_id)
        if record is None:
            continue
        summary = record.get('summary') or {}
        assert summary.get('plain'), f'{experiment_id} has no plain-language summary'
        assert len(summary['plain'].split()) <= 60, (
            f'{experiment_id} plain summary is longer than 60 words')


def test_resolved_people_carry_inspire_identifiers(atlas):
    people = atlas.by_type('person')
    if not people:
        pytest.skip('no people have been ingested yet')
    for person_id, person in people.items():
        if person_id.startswith('person:inspire-'):
            recid = person_id.rsplit('-', 1)[-1]
            assert recid.isdigit(), f'{person_id} has a non-numeric INSPIRE id'
            assert str((person.get('external') or {}).get('inspire_author')) == recid
            assert person.get('identity_evidence'), (
                f'{person_id} claims an INSPIRE identity with no evidence')
