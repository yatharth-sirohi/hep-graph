"""HEP Atlas data contract: entity field specs, enums, units, dates, timeline.

Everything here mirrors docs/HEP_ATLAS_ONTOLOGY.md **v0.2** (the amendment
block A1-A22 at the top of that document overrides its body).  The validator,
the build step, the link checker and the scaffold generator import their
vocabulary from this module so that a change to the contract happens in
exactly one place.

Nothing in this module reads files or depends on anything outside the
standard library.

Timeline model (A3) in one paragraph: an imprecise date denotes a closed
range of real days, ``lo(d) .. hi(d)``.  The slider selects a closed range
``[Y_lo, Y_hi]``.  An interval *covers* the selection iff
``lo(start) <= Y_hi`` and (``end`` is null or ``hi(end) >= Y_lo``); coverage
is *certain* if additionally ``hi(start) <= Y_lo`` and (``end`` null or
``lo(end) >= Y_hi``), otherwise *possible*.  Open intervals extend to the
build date, never to ``verified_at``.  Presence uses the existence hull;
state is chosen among covering intervals by the precedence rules in
:func:`state_at`.
"""
from __future__ import annotations

from dataclasses import dataclass
import datetime as _dt
import math
import re
from typing import Any, Iterable, Sequence

SCHEMA_TAG = 'hep-atlas/0.2'

# ---------------------------------------------------------------------------
# Identifiers and entity types
# ---------------------------------------------------------------------------

# type -> plural directory under data/atlas/ (rule 2 of RESEARCH_AGENT_RULES).
ENTITY_DIRS: dict[str, str] = {
    'facility': 'facilities',
    'site': 'sites',
    'accelerator': 'accelerators',
    'beamline': 'beamlines',
    'experiment': 'experiments',
    'detector': 'detectors',
    'collaboration': 'collaborations',
    'institution': 'institutions',
    'person': 'people',
    'result': 'results',
    'document': 'documents',
    'topic': 'topics',
    'source': 'sources',
    # A25 (2026-09-18): the local-map geometry layer.  Appended last so that
    # `iter_entities` keeps the order every existing bundle and report was
    # built in, and so a map may reference anything that loads before it.
    'map': 'maps',
    'geometry': 'geometry',
    # A28 (2026-10-26): guided tours.  Appended last for the same reason; a
    # tour references anything, nothing references a tour.
    'tour': 'tours',
}
DIR_TO_TYPE: dict[str, str] = {v: k for k, v in ENTITY_DIRS.items()}
ENTITY_TYPES: tuple[str, ...] = tuple(ENTITY_DIRS)
# Directories that hold non-entity files (keyed by collaboration / workstream).
AUXILIARY_DIRS: tuple[str, ...] = ('memberships', 'coverage')

# Every id is `<type>:<slug>`; `src:` is the prefix of the `source` type.
ID_PREFIX_TO_TYPE: dict[str, str] = {t: t for t in ENTITY_TYPES if t != 'source'}
ID_PREFIX_TO_TYPE['src'] = 'source'
TYPE_TO_ID_PREFIX: dict[str, str] = {v: k for k, v in ID_PREFIX_TO_TYPE.items()}

SLUG_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
# A6: `person:inspire-<recid>` and `person:unresolved-<collab>-<institution>-<name>`.
PERSON_INSPIRE_RE = re.compile(r'^person:inspire-([0-9]+)$')
PERSON_UNRESOLVED_RE = re.compile(r'^person:unresolved-[a-z0-9]+(?:-[a-z0-9]+)*$')
# v0.1 wrote a second colon; accepted on load and migrated (see load.py).
LEGACY_PERSON_INSPIRE_RE = re.compile(r'^person:inspire:([0-9]+)$')
LEGACY_PERSON_UNRESOLVED_RE = re.compile(r'^person:unresolved:[a-z0-9]+(?:-[a-z0-9]+)*$')
ID_RE = re.compile(r'^([a-z]+):(.+)$')


def id_prefix(entity_id: str) -> str | None:
    match = ID_RE.match(entity_id or '')
    return match.group(1) if match else None


def id_type(entity_id: str) -> str | None:
    """Return the entity type an id refers to, or None for an unknown prefix."""
    prefix = id_prefix(entity_id)
    return ID_PREFIX_TO_TYPE.get(prefix) if prefix else None


def id_slug(entity_id: str) -> str:
    match = ID_RE.match(entity_id or '')
    return match.group(2) if match else ''


def is_valid_id(entity_id: Any) -> bool:
    """Structural check: known prefix and a `-`-slug (A6 shapes for people)."""
    if not isinstance(entity_id, str):
        return False
    kind = id_type(entity_id)
    if kind is None:
        return False
    if kind == 'person':
        return bool(PERSON_INSPIRE_RE.match(entity_id) or PERSON_UNRESOLVED_RE.match(entity_id))
    return bool(SLUG_RE.match(id_slug(entity_id)))


def canonical_id(entity_id: Any) -> Any:
    """v0.1 -> v0.2 id migration: `person:inspire:1` -> `person:inspire-1`.

    Every other id is returned unchanged, including non-strings, so callers
    can pass raw JSON values.
    """
    if not isinstance(entity_id, str):
        return entity_id
    if LEGACY_PERSON_INSPIRE_RE.match(entity_id) or LEGACY_PERSON_UNRESOLVED_RE.match(entity_id):
        head, _, tail = entity_id.partition(':')
        return f'{head}:{tail.replace(":", "-", 1)}'
    return entity_id


def filename_for(entity_id: str) -> str:
    """Basename (without .json) of the canonical file for an entity id."""
    return id_slug(canonical_id(entity_id)).replace(':', '-')


def path_for(entity_id: str) -> str:
    """Relative path under data/atlas/ for an entity id, e.g. `experiments/dune.json`."""
    kind = id_type(entity_id)
    if kind is None:
        raise ValueError(f'unknown id prefix: {entity_id!r}')
    return f'{ENTITY_DIRS[kind]}/{filename_for(entity_id)}.json'


def inspire_recid(person_id: Any) -> int | None:
    """INSPIRE author recid of a resolved person id, else None."""
    match = PERSON_INSPIRE_RE.match(canonical_id(person_id) or '') if isinstance(person_id, str) else None
    return int(match.group(1)) if match else None


def hep_graph_url(person_id: str) -> str | None:
    """`/?source=<recid>&mode=live` for `person:inspire-*` ids only (A6, §3.9)."""
    recid = inspire_recid(person_id)
    return f'/?source={recid}&mode=live' if recid is not None else None


def normalise_name(text: Any) -> str:
    """A20 name normalisation: lower-case, drop a leading "the", strip
    every non-alphanumeric character."""
    value = str(text or '').strip().lower()
    if value.startswith('the '):
        value = value[4:]
    return re.sub(r'[^a-z0-9]+', '', value)


# ---------------------------------------------------------------------------
# Enumerations (§3-§6, A2, A19)
# ---------------------------------------------------------------------------

STATUSES: tuple[str, ...] = (
    'proposed', 'approved', 'construction', 'commissioning', 'active', 'shutdown',
    'upgrade', 'completed', 'decommissioned', 'cancelled', 'planned',
)
TERMINAL_STATUSES: frozenset[str] = frozenset({'completed', 'decommissioned', 'cancelled'})
# A3 rule (1): these beat {proposed, approved, planned} outright.
REALISED_STATUSES: frozenset[str] = frozenset({
    'construction', 'commissioning', 'active', 'shutdown', 'upgrade',
})
SPECULATIVE_STATUSES: frozenset[str] = frozenset({'proposed', 'approved', 'planned'})
# States that render dimmed and never as "operating".
DIMMED_STATUSES: frozenset[str] = frozenset({'proposed', 'planned'})
# A3 rule (3), highest first.
STATE_PRECEDENCE: tuple[str, ...] = (
    'decommissioned', 'cancelled', 'completed', 'shutdown', 'upgrade', 'active',
    'commissioning', 'construction', 'approved', 'proposed', 'planned',
)
STATE_RANK: dict[str, int] = {status: len(STATE_PRECEDENCE) - i for i, status in enumerate(STATE_PRECEDENCE)}
# A3: the hull covers the selection but no interval does.
UNRECORDED = 'unrecorded'

INTERVAL_KINDS: tuple[str, ...] = ('lifecycle', 'run', 'phase')  # A3
CERTAINTIES: tuple[str, ...] = ('certain', 'possible')

CONFIDENCES: tuple[str, ...] = ('verified', 'derived', 'approximate', 'uncertain')
COORDINATE_KINDS: tuple[str, ...] = ('detector', 'campus', 'underground_lab', 'headquarters', 'approximate_region')
# Kinds a globe marker for a detector/site may use (§2.5).
DETECTOR_COORDINATE_KINDS: frozenset[str] = frozenset({'detector', 'underground_lab'})
INSTITUTION_COORDINATE_KINDS: frozenset[str] = frozenset({'campus', 'headquarters'})
# A17: coordinates of these kinds may not rest on a geocoder / rank >= 8 source.
STRICT_COORDINATE_KINDS: frozenset[str] = frozenset({'detector', 'underground_lab'})
GEOCODER_COORDINATE_KINDS: frozenset[str] = frozenset({'campus', 'headquarters'})

FACILITY_KINDS: tuple[str, ...] = (
    'accelerator_laboratory', 'underground_laboratory', 'neutrino_observatory',
    'astroparticle_observatory', 'reactor_site', 'spallation_source',
    'research_laboratory', 'polar_station', 'deep_sea_site',
    'astronomical_observatory',  # A26
)
SITE_SETTINGS: tuple[str, ...] = ('surface', 'underground', 'ice', 'sea', 'lake', 'balloon', 'mountain')
ACCELERATOR_KINDS: tuple[str, ...] = ('synchrotron', 'linac', 'storage_ring', 'collider', 'cyclotron', 'booster')
EXPERIMENT_KINDS: tuple[str, ...] = (
    'collider', 'fixed_target', 'accelerator_neutrino', 'reactor_neutrino', 'solar_neutrino',
    'atmospheric_neutrino', 'astrophysical_neutrino', 'direct_dark_matter', 'axion',
    'double_beta_decay', 'neutrino_mass', 'muon_precision', 'rare_kaon', 'long_lived_particle',
    'cosmic_ray', 'gamma_ray', 'heavy_ion', 'cevns', 'other',
    # A26: the coverage wave (all of HEP, ground-based).
    'cmb', 'dark_energy_survey', 'nucleon_decay', 'hadron_structure',
    'electroweak_precision', 'antimatter', 'neutron_precision',
)
# A21: kinds for which a far site is expected and the 50 km warning is muted.
LONG_BASELINE_KINDS: frozenset[str] = frozenset({
    'accelerator_neutrino', 'astrophysical_neutrino', 'cosmic_ray',
})
# A1: only these four relations are authored; the build derives the inverses.
LINEAGE_RELATIONS: tuple[str, ...] = (
    'predecessor', 'successor', 'upgrade_of', 'upgraded_to', 'same_program', 'complementary',
)
CANONICAL_LINEAGE_RELATIONS: tuple[str, ...] = ('predecessor', 'upgrade_of', 'same_program', 'complementary')
DERIVED_LINEAGE_RELATIONS: tuple[str, ...] = ('successor', 'upgraded_to')
LINEAGE_INVERSE: dict[str, str] = {
    'predecessor': 'successor',
    'successor': 'predecessor',
    'upgrade_of': 'upgraded_to',
    'upgraded_to': 'upgrade_of',
    'same_program': 'same_program',
    'complementary': 'complementary',
}
# A1: `same_program` / `complementary` live on the lexicographically smaller id.
SYMMETRIC_LINEAGE_RELATIONS: frozenset[str] = frozenset({'same_program', 'complementary'})

TECHNOLOGY_CLASSES: tuple[str, ...] = (
    'lar_tpc', 'water_cherenkov', 'liquid_scintillator', 'xenon_tpc', 'argon_tpc',
    'noble_liquid_tpc', 'cryogenic_bolometer', 'germanium', 'scintillating_crystal',
    'general_purpose_collider', 'forward_spectrometer', 'ice_cherenkov', 'sea_cherenkov',
    'radio', 'air_shower_array', 'imaging_atmospheric_cherenkov', 'gaseous_tpc', 'emulsion',
    'tracking_calorimeter', 'haloscope', 'spectrometer',
    # A24 (2026-09-17): classes the wave-3 axion, cryogenic dark-matter and
    # CEvNS records needed and had to file under `other`.
    'helioscope', 'light_shining_through_wall', 'lumped_element_resonator',
    'cryogenic_phonon_detector', 'skipper_ccd', 'spherical_proportional_counter',
    'radiochemical', 'magnetic_spectrometer', 'other',
)
# A9: `noble_liquid_tpc` is preferred; these stay accepted aliases.
TECHNOLOGY_CLASS_ALIASES: dict[str, str] = {
    'lar_tpc': 'noble_liquid_tpc',
    'xenon_tpc': 'noble_liquid_tpc',
    'argon_tpc': 'noble_liquid_tpc',
}

# A2.
PLACEMENT_ROLES: tuple[str, ...] = ('main', 'near', 'far', 'prototype', 'storage')
FACILITY_ROLES: tuple[str, ...] = ('host', 'beam_source', 'detector_host', 'prototype_host')

INSTITUTION_KINDS: tuple[str, ...] = (
    'university', 'national_laboratory', 'research_institute', 'international_organization',
    'agency', 'company',
)

# A19: the two new classes come last in the tuple but have their own precedence.
EVIDENCE_CLASSES: tuple[str, ...] = (
    'official_roster', 'official_institution_list', 'inspire_author_profile',
    'publication_affiliation_current', 'institutional_page', 'self_reported',
    'publication_affiliation_historical', 'derived',
)
# A19 precedence when several apply, strongest first.
EVIDENCE_PRECEDENCE: tuple[str, ...] = EVIDENCE_CLASSES
EVIDENCE_RANK: dict[str, int] = {name: index for index, name in enumerate(EVIDENCE_PRECEDENCE)}
# A19: classes counted under a "member institutions" label.
COUNTED_EVIDENCE_CLASSES: frozenset[str] = frozenset({
    'official_roster', 'official_institution_list', 'inspire_author_profile',
    'publication_affiliation_current', 'institutional_page',
})
# A19: forbidden on person rows (institution rows only, always hollow).
PERSON_FORBIDDEN_EVIDENCE_CLASSES: frozenset[str] = frozenset({'derived'})
# A19: classes that require `evidence_date`.
EVIDENCE_DATE_REQUIRED: frozenset[str] = frozenset({
    'publication_affiliation_current', 'publication_affiliation_historical',
})
# A15: rows whose source must be an official one need a quote or a locator.
OFFICIAL_EVIDENCE_CLASSES: frozenset[str] = frozenset({'official_roster', 'official_institution_list'})
# A19: publication_affiliation_current fails when as_of - evidence_date > 3 years.
PUBLICATION_CURRENT_MAX_YEARS = 3

# A19 exact UI wording.  `{as_of}`, `{collab}`, `{year}`, `{checked}` are filled in.
EVIDENCE_CLASS_TEMPLATES: dict[str, str] = {
    'official_roster': "On the collaboration's own member list (as of {as_of})",
    'official_institution_list': 'On the official institution list (as of {as_of})',
    'inspire_author_profile': 'INSPIRE author profile lists this collaboration',
    'publication_affiliation_current':
        'Listed with this affiliation on a {collab} paper ({year}); current membership not confirmed',
    'publication_affiliation_historical':
        'Listed on a {collab} paper in {year}; may no longer be a member',
    'institutional_page': "The institution's own page states participation (checked {checked})",
    'self_reported': 'Self-reported',
    'derived': 'Inferred, not verified',
}


def evidence_label(evidence_class: str, *, as_of: Any = None, collaboration: Any = None,
                   year: Any = None, checked: Any = None) -> str:
    """A19 UI wording for one evidence class, with its placeholders filled."""
    template = EVIDENCE_CLASS_TEMPLATES.get(evidence_class)
    if template is None:
        return str(evidence_class)
    return template.format(
        as_of=as_of if as_of is not None else 'unknown',
        collab=collaboration if collaboration is not None else 'collaboration',
        year=year if year is not None else 'unknown',
        checked=checked if checked is not None else 'unknown',
    )


PERSON_ROLES: tuple[str, ...] = (
    'faculty', 'staff_scientist', 'postdoc', 'graduate_student', 'other_researcher',
    'historical_member', 'unknown',
)
# A6: collaboration-level roles.
LEADERSHIP_ROLES: tuple[str, ...] = (
    'spokesperson', 'deputy_spokesperson', 'physics_coordinator', 'technical_coordinator',
    'ib_chair', 'other',
)
RESULT_TYPES: tuple[str, ...] = (
    'discovery', 'observation', 'evidence', 'measurement', 'precision_measurement', 'limit',
    'anomaly', 'first_detection', 'technology_milestone',
)
# A16 mechanical keyword check: result_type -> substring required (case-folded)
# in `claim.quote` or in the title of one cited source.
RESULT_CLAIM_KEYWORDS: dict[str, str] = {
    'discovery': 'discover',
    'observation': 'observ',
    'evidence': 'evidence',
    # A16 (extended 2026-09-17): a "first detection" must say so in the paper.
    'first_detection': 'detect',
}
RESULT_DATE_KINDS: tuple[str, ...] = ('announcement', 'preprint', 'publication')  # A16
# A12: results that are allowed to predate their experiment's operation.
MILESTONE_RESULT_TYPES: frozenset[str] = frozenset({'technology_milestone'})

DOC_TYPES: tuple[str, ...] = (
    'conceptual_design_report', 'technical_design_report', 'technical_proposal',
    'letter_of_intent', 'detector_paper', 'performance_paper', 'physics_paper', 'run_plan',
    'beam_design', 'upgrade_report', 'public_note', 'hepdata_record', 'data_release',
    'software_documentation', 'review_article',
)

# A7/A18.  `inspire_record` is retired in favour of the two explicit types but
# stays readable (load.py migrates it to `inspire_literature_record`).
SOURCE_TYPES: tuple[str, ...] = (
    'official_experiment_site', 'official_facility_site', 'experiment_registry',
    'inspire_experiment_record', 'design_report', 'detector_paper', 'hepdata', 'pdg',
    'institution_page', 'geocoder', 'result_page', 'press_release', 'project_document',
    'journal_article', 'arxiv', 'inspire_literature_record', 'wikipedia', 'wikidata',
    'secondary',
    # A25: OpenStreetMap, rank 11 — below `journal_article` (10), so a shape
    # traced by OSM contributors can never on its own make a value `verified`
    # (A17 needs rank <= VERIFIED_MAX_RANK = 10).  That is the whole point of
    # the rank: OSM is excellent geodata and is nobody's official record.
    'openstreetmap',
)
LEGACY_SOURCE_TYPES: dict[str, str] = {'inspire_record': 'inspire_literature_record'}
# A18 derived rank mapping.  Never authored; the build and the validator
# recompute it from `source_type`.
SOURCE_RANKS: dict[str, int] = {
    'official_experiment_site': 1,
    'official_facility_site': 2,
    'experiment_registry': 3,
    'inspire_experiment_record': 3,
    'design_report': 4,
    'detector_paper': 5,
    'hepdata': 6,
    'pdg': 7,
    'institution_page': 8,
    'geocoder': 8,
    'result_page': 9,
    'press_release': 9,
    'project_document': 9,
    'journal_article': 10,
    'arxiv': 10,
    'inspire_literature_record': 10,
    'openstreetmap': 11,     # A25
    'wikipedia': 12,
    'wikidata': 12,
    'secondary': 12,
}
# A17: a `verified` value must cite at least one source of rank <= this.
VERIFIED_MAX_RANK = 10
RETRIEVALS: tuple[str, ...] = ('full_text', 'partial', 'summary', 'failed')  # A18
UNCITABLE_RETRIEVALS: frozenset[str] = frozenset({'failed'})
NO_QUOTE_RETRIEVALS: frozenset[str] = frozenset({'summary'})

# A19 evidence class -> the source types that may back it.
EVIDENCE_SOURCE_TYPES: dict[str, frozenset[str]] = {
    'official_roster': frozenset({'official_experiment_site', 'official_facility_site', 'experiment_registry'}),
    'official_institution_list': frozenset({'official_experiment_site', 'official_facility_site', 'experiment_registry'}),
    'publication_affiliation_current': frozenset({
        'journal_article', 'arxiv', 'inspire_literature_record', 'detector_paper', 'design_report'}),
    'publication_affiliation_historical': frozenset({
        'journal_article', 'arxiv', 'inspire_literature_record', 'detector_paper', 'design_report'}),
    'institutional_page': frozenset({'institution_page'}),
}


def source_rank(source_type: Any) -> int | None:
    """A18: derived rank of a source type, or None when the type is unknown."""
    if not isinstance(source_type, str):
        return None
    return SOURCE_RANKS.get(LEGACY_SOURCE_TYPES.get(source_type, source_type))


# ---------------------------------------------------------------------------
# Local-map geometry vocabulary (A25)
# ---------------------------------------------------------------------------

#: Contract §1.2.  Rings and tunnels are lines, halls and buildings polygons,
#: strings and shafts may be points; `other` is the honest escape hatch.
FEATURE_TYPES: tuple[str, ...] = (
    'ring', 'linac', 'transfer_line', 'beamline', 'tunnel', 'shaft', 'cavern',
    'hall', 'experimental_area', 'target_station', 'building', 'boundary',
    'array', 'string', 'direction_line', 'level_outline', 'road', 'water', 'other',
)
#: Feature types that depict a named atlas entity and may not be context-only.
FEATURE_TYPES_REQUIRING_ENTITY: frozenset[str] = frozenset({
    'ring', 'linac', 'beamline', 'transfer_line', 'cavern', 'hall',
    'target_station', 'array', 'string', 'direction_line',
})
#: Entity types a geometry feature may depict (contract §1.2).
GEOMETRY_ENTITY_TYPES: tuple[str, ...] = (
    'accelerator', 'beamline', 'detector', 'site', 'experiment', 'facility',
)

#: What kind of evidence a shape is.  There is deliberately no `schematic`:
#: a tracing of an unscaled diagram is a `map.schematics` link, not geometry.
REPRESENTATIONS: tuple[str, ...] = ('surveyed', 'georeferenced', 'derived', 'inferred_direction')
#: The one representation that is not a physical structure and needs no accuracy.
DIRECTION_REPRESENTATION = 'inferred_direction'
#: Representations counted as "to scale" in the build's `to_scale_count`.
TO_SCALE_REPRESENTATIONS: frozenset[str] = frozenset({'surveyed', 'georeferenced', 'derived'})

#: A map level's physical plane (contract §1.1).
LEVEL_KINDS: tuple[str, ...] = ('surface', 'underground', 'sea', 'lake', 'ice', 'mountain')

#: Independent cross-checks the validator executes against a shape (§1.2).
CHECK_KINDS: tuple[str, ...] = ('length', 'area', 'distance', 'azimuth', 'span')
#: Default fractional tolerance of a `checks[]` row when it states none.
CHECK_TOLERANCE_DEFAULT = 0.03
#: `azimuth` is compared in degrees, not as a fraction: 1 degree, per A25.
AZIMUTH_TOLERANCE_DEG = 1.0

#: `extent_m` bounds (contract §1.1): a half-width smaller than 500 m is a
#: building plan, larger than 60 km is a region, and neither is a campus map.
MIN_EXTENT_M, MAX_EXTENT_M = 500.0, 60_000.0
#: Hard limit on how far any position may sit from the map centre (§2).
MAX_FEATURE_DISTANCE_M = 60_000.0
#: A map centre further than this from the facility's primary site warns (§2).
MAX_MAP_CENTER_DISTANCE_M = 30_000.0
#: §1.2: a feature's centroid must sit within `max(3 x precision_m, this)` of
#: a precise site point, and a site point coarser than this never checks anything.
SITE_MATCH_MAX_PRECISION_M = 100.0
SITE_MATCH_FLOOR_M = 150.0
#: §3: the build fails when one map's geometry bundle exceeds this.
GEOMETRY_BUNDLE_MAX_BYTES = 2_000_000

#: Licence names the geometry layer expects to see (free text is still allowed;
#: this is what the ODbL attribution rule keys on).
ODBL_LICENSE_NAME = 'ODbL-1.0'
OSM_ATTRIBUTION = '\u00a9 OpenStreetMap contributors'


COVERAGE_TIERS: tuple[str, ...] = ('A', 'B', 'C', 'D', 'E')
RESEARCHED_LEVELS: tuple[str, ...] = ('none', 'partial', 'full')
# A20: these tiers need an INSPIRE experiment id or an explicit note.
INSPIRE_REQUIRED_TIERS: frozenset[str] = frozenset({'A', 'B'})
# Owner types a document may describe (§3.13).
DOCUMENT_OWNER_TYPES: frozenset[str] = frozenset({
    'experiment', 'facility', 'accelerator', 'beamline', 'detector', 'collaboration',
})
TOPIC_MAX_DEPTH = 3
SUMMARY_PLAIN_MAX_WORDS = 60
KEY_SPECS_MAX = 5
EXCERPT_MAX_CHARS = 300
QUOTE_MAX_CHARS = 300  # A15
EXTERNAL_REFERENCE_KEYS: tuple[str, ...] = ('doi', 'arxiv', 'inspire', 'url', 'report_number', 'hepdata')
# A5.
MEMBERSHIP_HISTORY_LEVELS: tuple[str, ...] = ('unknown', 'partial', 'complete')
# A12 warning thresholds.
MAX_VERIFIED_AGE_MONTHS = 18
MAX_HULL_GAP_MONTHS = 12
# A20: two sites of one facility closer than this warn as a likely duplicate.
MIN_SITE_SEPARATION_M = 100.0
# A21: a detector site this far from the facility's primary site warns.
MAX_DETECTOR_SITE_DISTANCE_KM = 50.0
# A21: `baselines[].distance` must agree with the great-circle distance to 2 %.
BASELINE_TOLERANCE = 0.02
# A21: display vs value after unit conversion.
DISPLAY_FACTOR_ERROR = 10.0
DISPLAY_FACTOR_WARN = 1.05
# A12: years outside this range are a calendar error.
MIN_YEAR, MAX_YEAR = 1900, 2100
# §8: the build fails above this (uncompressed atlas.json).
ATLAS_JSON_MAX_BYTES = 1_500_000
ATLAS_JSON_BUDGET_BYTES = 400_000  # pilot budget; over it the build prints a note

# A3: state_segments are expressed in months since this epoch.
EPOCH_YEAR = 1950
EPOCH_MONTH = 1

# ---------------------------------------------------------------------------
# Units (§2.4 + A8 + A21)
# ---------------------------------------------------------------------------

UNITS: dict[str, tuple[str, ...]] = {
    'length': ('m', 'km', 'cm', 'mm'),
    'area': ('m^2', 'km^2', 'cm^2'),
    'mass': ('kg', 't', 'kt', 'Mt', 'g', 'mg'),
    'energy': ('eV', 'meV', 'µeV', 'keV', 'MeV', 'GeV', 'TeV', 'PeV', 'EeV'),
    'mass_energy': ('eV/c^2', 'keV/c^2', 'MeV/c^2', 'GeV/c^2', 'TeV/c^2'),
    'power': ('W', 'kW', 'MW', 'GW'),
    'luminosity': ('cm^-2 s^-1', 'nb^-1 s^-1', 'Hz/nb'),
    'integrated_luminosity': ('pb^-1', 'fb^-1', 'ab^-1'),
    'cross_section': ('cm^2', 'b', 'mb', 'µb', 'nb', 'pb', 'fb', 'zb'),
    'magnetic_field': ('T', 'mT', 'G'),
    'electric_field': ('V/cm', 'kV/cm', 'kV/m'),
    'depth_mwe': ('m.w.e.',),
    'volume': ('m^3', 'km^3', 'L'),
    'exposure': ('kg d', 'kg yr', 't yr', 'kt yr'),
    'fraction': ('%', ''),
    'count': ('',),
    'current': ('A', 'mA'),
    'time': ('s', 'ms', 'ns', 'min', 'h', 'd', 'yr'),
    'rate': ('Hz', 'kHz', 'MHz', '/yr'),
    'angle': ('deg', 'mrad', 'rad', 'µrad', 'arcmin', 'arcsec'),
    'temperature': ('K', 'mK'),
    'pressure': ('bar', 'Pa'),
    'frequency': ('Hz', 'kHz', 'MHz', 'GHz'),
}
DIMENSIONS: tuple[str, ...] = tuple(UNITS)

_YEAR_SECONDS = 365.25 * 86400.0
_PI = 3.141592653589793

# Multipliers to the first (base) unit of each dimension, for comparisons.
UNIT_SCALE: dict[str, dict[str, float]] = {
    'length': {'m': 1.0, 'km': 1e3, 'cm': 1e-2, 'mm': 1e-3},
    'area': {'m^2': 1.0, 'km^2': 1e6, 'cm^2': 1e-4},
    'mass': {'kg': 1.0, 't': 1e3, 'kt': 1e6, 'Mt': 1e9, 'g': 1e-3, 'mg': 1e-6},
    'energy': {'eV': 1.0, 'meV': 1e-3, 'µeV': 1e-6, 'keV': 1e3, 'MeV': 1e6,
               'GeV': 1e9, 'TeV': 1e12, 'PeV': 1e15, 'EeV': 1e18},
    'mass_energy': {'eV/c^2': 1.0, 'keV/c^2': 1e3, 'MeV/c^2': 1e6, 'GeV/c^2': 1e9, 'TeV/c^2': 1e12},
    'power': {'W': 1.0, 'kW': 1e3, 'MW': 1e6, 'GW': 1e9},
    # Base cm^-2 s^-1; 1 nb^-1 s^-1 = 1e33 cm^-2 s^-1 (1 nb = 1e-33 cm^2).
    'luminosity': {'cm^-2 s^-1': 1.0, 'nb^-1 s^-1': 1e33, 'Hz/nb': 1e33},
    'integrated_luminosity': {'pb^-1': 1.0, 'fb^-1': 1e3, 'ab^-1': 1e6},
    'cross_section': {'cm^2': 1.0, 'b': 1e-24, 'mb': 1e-27, 'µb': 1e-30,
                      'nb': 1e-33, 'pb': 1e-36, 'fb': 1e-39, 'zb': 1e-45},
    'magnetic_field': {'T': 1.0, 'mT': 1e-3, 'G': 1e-4},
    'electric_field': {'V/cm': 1.0, 'kV/cm': 1e3, 'kV/m': 10.0},
    'depth_mwe': {'m.w.e.': 1.0},
    'volume': {'m^3': 1.0, 'km^3': 1e9, 'L': 1e-3},
    # Base kg d.
    'exposure': {'kg d': 1.0, 'kg yr': 365.25, 't yr': 365.25e3, 'kt yr': 365.25e6},
    'fraction': {'%': 0.01, '': 1.0},
    'count': {'': 1.0},
    'current': {'A': 1.0, 'mA': 1e-3},
    'time': {'s': 1.0, 'ms': 1e-3, 'ns': 1e-9, 'min': 60.0, 'h': 3600.0,
             'd': 86400.0, 'yr': _YEAR_SECONDS},
    'rate': {'Hz': 1.0, 'kHz': 1e3, 'MHz': 1e6, '/yr': 1.0 / _YEAR_SECONDS},
    'angle': {'deg': 1.0, 'mrad': 180.0 / (1000.0 * _PI), 'rad': 180.0 / _PI,
              'µrad': 180.0 / (1e6 * _PI), 'arcmin': 1.0 / 60.0, 'arcsec': 1.0 / 3600.0},
    'temperature': {'K': 1.0, 'mK': 1e-3},
    'pressure': {'bar': 1.0, 'Pa': 1e-5},
    'frequency': {'Hz': 1.0, 'kHz': 1e3, 'MHz': 1e6, 'GHz': 1e9},
}


def unit_allowed(dimension: Any, unit: Any) -> bool:
    """True when `unit` is one of the recognised units of `dimension`.

    `count` and `fraction` use the empty unit; `None` is accepted for `count`
    because JSON authors naturally write `"unit": null` for a bare count.
    """
    units = UNITS.get(dimension)
    if units is None:
        return False
    if dimension == 'count' and unit is None:
        return True
    return unit in units


def unit_scale(dimension: Any, unit: Any) -> float | None:
    if not unit_allowed(dimension, unit):
        return None
    return UNIT_SCALE[dimension][unit or '']


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def quantity_magnitude(quantity: dict) -> float | None:
    """Value (or range midpoint) of a quantity in its dimension's base unit."""
    scale = unit_scale(quantity.get('dimension'), quantity.get('unit'))
    if scale is None:
        return None
    if is_number(quantity.get('value')):
        return float(quantity['value']) * scale
    low, high = quantity.get('min'), quantity.get('max')
    if is_number(low) and is_number(high):
        return (float(low) + float(high)) / 2.0 * scale
    return None


# A21: characters a source uses to group digits in a written-out number —
# a plain space, a no-break space, a narrow no-break space (the thousands
# separator French- and SI-styled sources favour, e.g. "26 659 m"), or a
# comma.  Included in the number only when it sits between two digits, so a
# trailing unit ("659 m") is never swallowed into the match.
_GROUP_CHARS = '   ,'
_NUMBER_RE = re.compile(
    r'[-+]?\d(?:\d|[' + _GROUP_CHARS + r'](?=\d))*(?:\.\d+)?(?:[eE][-+]?\d+)?')
# A21: "mantissa (x|×) 10^exponent", once `_normalise_exponents` has turned a
# unicode superscript exponent ("10³⁴") into a caret ("10^34").
_SCI_NOTATION_RE = re.compile(
    r'(?P<mantissa>[-+]?\d(?:\d|[' + _GROUP_CHARS + r'](?=\d))*(?:\.\d+)?)'
    r'\s*[x×]\s*10\^(?P<exponent>-?\d+)')
# A21: superscript digits/sign a source uses for "10³⁴" or a unit exponent
# ("cm⁻²"); only the ones following "10" are turned into an ASCII exponent
# (`_normalise_exponents`) — the rest are left alone, since unit detection
# below only needs to recognise the ASCII unit spellings in Appendix A.
_SUPERSCRIPT_TRANSLATION = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺', '0123456789-+')
_TEN_TO_SUPERSCRIPT_RE = re.compile(r'10([⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺]+)')


def _normalise_exponents(text: str) -> str:
    """"10³⁴" -> "10^34"; leaves ordinary text and other superscripts alone."""
    return _TEN_TO_SUPERSCRIPT_RE.sub(
        lambda match: '10^' + match.group(1).translate(_SUPERSCRIPT_TRANSLATION), text)


def _clean_number(text: str) -> str:
    """Strip A21 grouping characters, leaving a string `float()` accepts."""
    return re.sub('[' + _GROUP_CHARS + ']', '', text)


def _detect_display_unit(text: str, dimension: Any) -> str | None:
    """The longest Appendix A unit of `dimension` that appears in `text` as
    its own token (not, say, the "m" inside "MeV").  `display` sometimes
    states its number in a different unit than the quantity's own `unit`
    ("800 MeV" on a quantity stored in GeV, "26 659 m" on one stored in km);
    when that happens the display's own unit is what its number must be
    scaled by, not the quantity's."""
    units = UNITS.get(dimension)
    if not units:
        return None
    for unit in sorted((u for u in units if u), key=len, reverse=True):
        pattern = r'(?<![A-Za-zµ])' + re.escape(unit) + r'(?![A-Za-zµ])'
        if re.search(pattern, text):
            return unit
    return None


def display_magnitude(quantity: dict) -> float | None:
    """A21: the number in `display`, scaled to the quantity's base unit so it
    can be compared with `value`.  None when `display` holds no recognisable
    number or no usable unit.

    Two source conventions this must not misparse: a thousands separator
    written as a plain or narrow no-break space ("26 659 m"), and scientific
    notation written either ASCII-style ("2 x 10^34") or with a unicode
    multiplication sign and superscript exponent ("2.11 × 10³⁴").  And one
    thing it must not assume: that `display`'s number is in the quantity's
    own `unit` — a source may state the same fact in a different, equally
    valid unit ("~800 MeV mean" on a quantity stored in GeV), so a unit
    named in `display` itself takes precedence over the quantity's `unit`.
    """
    display = quantity.get('display')
    if not isinstance(display, str):
        return None
    dimension = quantity.get('dimension')
    scale = unit_scale(dimension, quantity.get('unit'))
    if scale is None:
        return None
    normalised = _normalise_exponents(display)
    sci = _SCI_NOTATION_RE.search(normalised)
    try:
        if sci is not None:
            magnitude = float(_clean_number(sci.group('mantissa'))) * (10.0 ** int(sci.group('exponent')))
        else:
            match = _NUMBER_RE.search(normalised)
            if match is None:
                return None
            magnitude = float(_clean_number(match.group(0)))
    except ValueError:  # pragma: no cover - the regexes only match numbers
        return None
    display_unit = _detect_display_unit(normalised, dimension)
    if display_unit is not None:
        display_scale = unit_scale(dimension, display_unit)
        if display_scale is not None:
            scale = display_scale
    return magnitude * scale


# A21 per-key plausibility ranges, expressed in each dimension's base unit.
PLAUSIBILITY_RANGES: dict[str, dict[str, tuple[float, float]]] = {
    'baseline':    {'length': (100.0, 2.0e7)},                 # 0.1 km .. 20 000 km
    'overburden':  {'length': (0.0, 12_000.0), 'depth_mwe': (0.0, 15_000.0)},
    'altitude':    {'length': (-500.0, 6_000.0)},
    'cms_energy':  {'energy': (1.0e8, 1.0e15)},                # 100 MeV .. 1000 TeV
    'beam_power':  {'power': (1.0e3, 1.0e7)},                  # 1 kW .. 10 MW
    'total_mass':  {'mass': (1.0, 1.0e12)},                    # 1 kg .. 1e9 t
}

# Appendix A + §3.1/3.3/3.4: spec key -> allowed dimensions.  An empty tuple
# marks a key that is a sourced string (S), not a quantity.
SPEC_KEY_DIMENSIONS: dict[str, tuple[str, ...]] = {
    # facility / accelerator / beamline
    'depth': ('length', 'depth_mwe'),
    'overburden': ('length', 'depth_mwe'),
    'altitude': ('length',),
    'beam_power': ('power',),
    'beam_energy': ('energy',),
    'cms_energy': ('energy',),
    'circumference': ('length',),
    'length': ('length',),
    'diameter': ('length',),
    'peak_luminosity': ('luminosity',),
    'protons_per_year': ('count',),
    'proton_energy': ('energy',),
    'peak_neutrino_energy': ('energy',),
    'off_axis_angle': ('angle',),
    'baseline': ('length',),
    'integrated_luminosity': ('integrated_luminosity',),
    'design_luminosity': ('luminosity',),
    'collision_scheme': (),
    # lar_tpc / noble_liquid_tpc
    'total_mass': ('mass',),
    'active_mass': ('mass',),
    'fiducial_mass': ('mass',),
    'target_mass': ('mass',),
    'drift_length': ('length',),
    'readout': (),
    'cryostat_count': ('count',),
    'drift_field': ('electric_field',),
    'module_count': ('count',),
    'target_medium': (),
    'phase': (),
    # water_cherenkov / liquid_scintillator
    'pmt_count': ('count',),
    'tank_height': ('length',),
    'tank_diameter': ('length',),
    'photocoverage': ('fraction',),
    'energy_resolution': (),
    # xenon / argon tpc
    'threshold': ('energy',),
    'shielding': (),
    'exposure': ('exposure',),
    # general_purpose_collider
    'solenoid_field': ('magnetic_field',),
    'toroid_field': ('magnetic_field',),
    'tracker': (),
    'calorimeters': (),
    'muon_system': (),
    'pseudorapidity_coverage': (),
    'trigger_rate': ('rate', 'frequency'),
    # ice / sea cherenkov
    'instrumented_volume': ('volume',),
    'sensor_count': ('count',),
    'string_count': ('count',),
    'depth_min': ('length',),
    'depth_max': ('length',),
    'energy_range': (),
    # haloscope
    'cavity_volume': ('volume',),
    'magnetic_field': ('magnetic_field',),
    'frequency_range': ('frequency',),
    'temperature': ('temperature',),
    # air shower / IACT
    'area': ('area',),
    'station_count': ('count',),
    'telescope_count': ('count',),
    'mirror_area': ('area',),
    # bolometer / germanium
    'isotope': (),
    'isotope_mass': ('mass',),
    'enrichment': (),
}

# Appendix A recommended keys per technology class (scaffolding + reviews).
RECOMMENDED_SPEC_KEYS: dict[str, tuple[str, ...]] = {
    'lar_tpc': ('total_mass', 'active_mass', 'fiducial_mass', 'drift_length', 'readout',
                'cryostat_count', 'drift_field', 'module_count'),
    'noble_liquid_tpc': ('total_mass', 'active_mass', 'fiducial_mass', 'drift_length', 'readout',
                         'cryostat_count', 'drift_field', 'module_count', 'target_medium', 'phase'),
    'water_cherenkov': ('total_mass', 'fiducial_mass', 'pmt_count', 'tank_height', 'tank_diameter',
                        'photocoverage'),
    'liquid_scintillator': ('target_mass', 'fiducial_mass', 'pmt_count', 'energy_resolution'),
    'xenon_tpc': ('target_mass', 'active_mass', 'fiducial_mass', 'threshold', 'depth', 'shielding', 'exposure'),
    'argon_tpc': ('target_mass', 'active_mass', 'fiducial_mass', 'threshold', 'depth', 'shielding', 'exposure'),
    'general_purpose_collider': ('length', 'diameter', 'total_mass', 'solenoid_field', 'toroid_field',
                                 'tracker', 'calorimeters', 'muon_system', 'pseudorapidity_coverage',
                                 'trigger_rate'),
    'ice_cherenkov': ('instrumented_volume', 'sensor_count', 'string_count', 'depth_min', 'depth_max',
                      'energy_range'),
    'sea_cherenkov': ('instrumented_volume', 'sensor_count', 'string_count', 'depth_min', 'depth_max',
                      'energy_range'),
    'haloscope': ('cavity_volume', 'magnetic_field', 'frequency_range', 'temperature'),
    'air_shower_array': ('area', 'station_count', 'altitude', 'energy_range'),
    'imaging_atmospheric_cherenkov': ('telescope_count', 'mirror_area', 'energy_range', 'altitude'),
    'cryogenic_bolometer': ('isotope', 'isotope_mass', 'enrichment', 'temperature', 'depth'),
    'germanium': ('isotope', 'isotope_mass', 'enrichment', 'temperature', 'depth'),
}

# ---------------------------------------------------------------------------
# Dates (§2.2 + A4)
# ---------------------------------------------------------------------------

DATE_RE = re.compile(r'^(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?$')
PRECISIONS: tuple[str, ...] = ('year', 'month', 'day')
DATE_OBJECT_KEYS: frozenset[str] = frozenset({
    'date', 'approx', 'planned', 'note', 'earliest', 'latest', 'display',
})
# A4 seasons: (date month, earliest month, latest month).  Winter wraps, so its
# earliest month belongs to the previous year (December).
SEASON_MONTHS: dict[str, tuple[int, int, int]] = {
    'spring': (4, 3, 5),
    'summer': (7, 6, 8),
    'autumn': (10, 9, 11),
    'fall': (10, 9, 11),
    'winter': (1, 12, 2),
}


class DateError(ValueError):
    """A date string or date object does not follow §2.2 / A4."""


@dataclass(frozen=True)
class ParsedDate:
    """A calendar date with the precision it was written at (A4).

    `lo()` / `hi()` give the inclusive range of real days the written date can
    denote: "2008" is 2008-01-01 .. 2008-12-31, "2008-09" is 2008-09-01 ..
    2008-09-30, "2008-09-10" is one day.  An explicit `earliest` / `latest`
    widens that range.
    """

    text: str
    year: int
    month: int | None
    day: int | None
    approx: bool = False
    planned: bool = False
    note: str = ''
    display: str = ''
    earliest: _dt.date | None = None
    latest: _dt.date | None = None

    @property
    def precision(self) -> str:
        if self.day is not None:
            return 'day'
        if self.month is not None:
            return 'month'
        return 'year'

    def first_day(self) -> _dt.date:
        """First day of the written date's own precision (ignores `earliest`)."""
        return _dt.date(self.year, self.month or 1, self.day or 1)

    def last_day(self) -> _dt.date:
        """Last day of the written date's own precision (ignores `latest`)."""
        if self.day is not None:
            return _dt.date(self.year, self.month, self.day)
        if self.month is not None:
            return _dt.date(self.year, self.month, _days_in_month(self.year, self.month))
        return _dt.date(self.year, 12, 31)

    def lo(self) -> _dt.date:
        """A3 `lo(d)`: the first real day this date can denote."""
        own = self.first_day()
        return min(own, self.earliest) if self.earliest is not None else own

    def hi(self) -> _dt.date:
        """A3 `hi(d)`: the last real day this date can denote."""
        own = self.last_day()
        return max(own, self.latest) if self.latest is not None else own

    def __str__(self) -> str:  # pragma: no cover - convenience
        return self.text


def _days_in_month(year: int, month: int) -> int:
    if month == 12:
        return 31
    return (_dt.date(year, month + 1, 1) - _dt.timedelta(days=1)).day


def _parse_plain_date(text: Any, *, field: str = 'date') -> tuple[int, int | None, int | None]:
    if not isinstance(text, str):
        raise DateError(f'{field} must be a string, got {type(text).__name__}')
    match = DATE_RE.match(text)
    if not match:
        raise DateError(f'{field} {text!r} is not YYYY, YYYY-MM or YYYY-MM-DD')
    year = int(match.group(1))
    month = int(match.group(2)) if match.group(2) else None
    day = int(match.group(3)) if match.group(3) else None
    try:
        _dt.date(year, month or 1, day or 1)
    except ValueError as exc:
        raise DateError(f'{field} {text!r} is not a real calendar date: {exc}') from None
    if day is not None and day > _days_in_month(year, month):
        raise DateError(f'{field} {text!r} is not a real calendar date')
    if not MIN_YEAR <= year <= MAX_YEAR:
        raise DateError(f'{field} {text!r} has a year outside [{MIN_YEAR}, {MAX_YEAR}]')
    return year, month, day


def parse_date(value: Any) -> ParsedDate | None:
    """Parse a §2.2 / A4 date (string or object).  `None` stays `None`.

    Raises DateError for anything malformed: wrong shape, an impossible
    calendar date, a year outside [1900, 2100], an object without `date`,
    qualifiers of the wrong type, or `earliest > date > latest`.
    """
    if value is None:
        return None
    approx = planned = False
    note = display = ''
    earliest = latest = None
    if isinstance(value, dict):
        if 'date' not in value:
            raise DateError('date object needs a "date" key')
        for key in ('approx', 'planned'):
            if key in value and value[key] is not None and not isinstance(value[key], bool):
                raise DateError(f'date qualifier {key!r} must be a boolean')
        for key in ('note', 'display'):
            if key in value and value[key] is not None and not isinstance(value[key], str):
                raise DateError(f'date {key} must be a string')
        unknown = set(value) - DATE_OBJECT_KEYS
        if unknown:
            raise DateError(f'unknown date keys: {sorted(unknown)}')
        approx = bool(value.get('approx') or False)
        planned = bool(value.get('planned') or False)
        note = value.get('note') or ''
        display = value.get('display') or ''
        text = value['date']
        if text is None:
            return None
        if value.get('earliest') is not None:
            e_year, e_month, e_day = _parse_plain_date(value['earliest'], field='earliest')
            earliest = _dt.date(e_year, e_month or 1, e_day or 1)
        if value.get('latest') is not None:
            l_year, l_month, l_day = _parse_plain_date(value['latest'], field='latest')
            if l_day is not None:
                latest = _dt.date(l_year, l_month, l_day)
            elif l_month is not None:
                latest = _dt.date(l_year, l_month, _days_in_month(l_year, l_month))
            else:
                latest = _dt.date(l_year, 12, 31)
    else:
        text = value
    year, month, day = _parse_plain_date(text)
    parsed = ParsedDate(text, year, month, day, approx=approx, planned=planned, note=note,
                        display=display, earliest=earliest, latest=latest)
    if earliest is not None and earliest > parsed.first_day():
        raise DateError(f'earliest {earliest.isoformat()} is after date {text!r}')
    if latest is not None and latest < parsed.last_day():
        raise DateError(f'latest {latest.isoformat()} is before date {text!r}')
    if earliest is not None and latest is not None and earliest > latest:
        raise DateError('earliest is after latest')
    return parsed


def try_parse_date(value: Any) -> ParsedDate | None:
    """parse_date that swallows malformed input (returns None).  For build code
    running on data the validator has already accepted."""
    try:
        return parse_date(value)
    except DateError:
        return None


def date_precision(value: Any) -> str | None:
    parsed = parse_date(value)
    return parsed.precision if parsed else None


def date_text(value: Any) -> str | None:
    """The bare `YYYY[-MM[-DD]]` string of a Date, string or object."""
    if isinstance(value, dict):
        value = value.get('date')
    return value if isinstance(value, str) else None


def lo(value: Any) -> _dt.date | None:
    """A3 `lo(d)` for any Date value (string, object or already-parsed)."""
    parsed = value if isinstance(value, ParsedDate) else try_parse_date(value)
    return parsed.lo() if parsed else None


def hi(value: Any) -> _dt.date | None:
    """A3 `hi(d)` for any Date value (string, object or already-parsed)."""
    parsed = value if isinstance(value, ParsedDate) else try_parse_date(value)
    return parsed.hi() if parsed else None


def is_planned(value: Any) -> bool:
    parsed = try_parse_date(value)
    return bool(parsed and parsed.planned)


def as_date(value: Any) -> _dt.date | None:
    """Coerce a build date / `datetime.date` / date string to a `date`."""
    if value is None:
        return None
    if isinstance(value, _dt.datetime):
        return value.date()
    if isinstance(value, _dt.date):
        return value
    if isinstance(value, ParsedDate):
        return value.hi()
    return hi(value)


def season_range(season: Any, year: int) -> tuple[str, str, str] | None:
    """A4: (date, earliest, latest) month strings for a named season.

    Winter's earliest month is December of the previous year.
    """
    months = SEASON_MONTHS.get(str(season or '').strip().lower())
    if months is None:
        return None
    middle, first, last = months
    first_year = year - 1 if first > last else year
    return f'{year:04d}-{middle:02d}', f'{first_year:04d}-{first:02d}', f'{year:04d}-{last:02d}'


# ---------------------------------------------------------------------------
# Months since the epoch (A3 state_segments)
# ---------------------------------------------------------------------------

def month_index(value: Any) -> int | None:
    """Months since 1950-01 for a date (may be negative for earlier dates)."""
    day = as_date(value) if not isinstance(value, _dt.date) else value
    if day is None:
        return None
    return (day.year - EPOCH_YEAR) * 12 + (day.month - EPOCH_MONTH)


def month_to_date(index: int) -> _dt.date:
    """First day of the month `index` months after 1950-01."""
    total = EPOCH_YEAR * 12 + (EPOCH_MONTH - 1) + int(index)
    return _dt.date(total // 12, total % 12 + 1, 1)


def month_bounds(index: int) -> tuple[_dt.date, _dt.date]:
    start = month_to_date(index)
    end = month_to_date(index + 1) - _dt.timedelta(days=1)
    return start, end


# ---------------------------------------------------------------------------
# Intervals and timeline semantics (A3)
# ---------------------------------------------------------------------------

SELECTION_RE = re.compile(r'^(\d{4})(?:-(\d{2}))?$')


def selection_bounds(selection: Any) -> tuple[_dt.date, _dt.date]:
    """Closed day range of a slider selection: `"YYYY"` or `"YYYY-MM"`.

    A `(date, date)` pair, an `int` year or a `datetime.date` are accepted too
    so callers can drive the timeline from whatever they already hold.
    """
    if isinstance(selection, tuple) and len(selection) == 2:
        first, second = as_date(selection[0]), as_date(selection[1])
        if first is None or second is None:
            raise DateError(f'selection {selection!r} is not a pair of dates')
        return (first, second) if first <= second else (second, first)
    if isinstance(selection, _dt.date):
        return selection, selection
    if isinstance(selection, int) and not isinstance(selection, bool):
        return _dt.date(selection, 1, 1), _dt.date(selection, 12, 31)
    if not isinstance(selection, str):
        raise DateError(f'selection must be "YYYY" or "YYYY-MM", got {type(selection).__name__}')
    match = SELECTION_RE.match(selection)
    if not match:
        raise DateError(f'selection {selection!r} is not "YYYY" or "YYYY-MM"')
    year = int(match.group(1))
    if match.group(2) is None:
        return _dt.date(year, 1, 1), _dt.date(year, 12, 31)
    month = int(match.group(2))
    if not 1 <= month <= 12:
        raise DateError(f'selection {selection!r} has an impossible month')
    return _dt.date(year, month, 1), _dt.date(year, month, _days_in_month(year, month))


def _entity_intervals(entity: Any, *, lifecycle_only: bool = False) -> list[dict]:
    """The `intervals` list of an entity; `entity` may be the list itself.

    With `lifecycle_only`, `run` and `phase` rows are dropped. A3 gives only
    lifecycle intervals the power to set the timeline state: a run or a phase
    annotates a state rather than being one. Without the distinction an
    open-ended milestone such as "first accelerator groundbreaking" outranks
    the operating interval that follows it, and the entity reads as under
    construction for ever after.
    """
    intervals = entity if isinstance(entity, list) else (entity or {}).get('intervals') or []
    rows = [row for row in intervals if isinstance(row, dict)]
    if not lifecycle_only:
        return rows
    lifecycle = [row for row in rows if (row.get('kind') or 'lifecycle') == 'lifecycle']
    # An entity annotated only with runs or phases must still exist somewhere.
    return lifecycle or rows


def interval_coverage(interval: dict, y_lo: _dt.date, y_hi: _dt.date, *,
                      build_date: _dt.date | None = None) -> str | None:
    """A3 coverage of `[y_lo, y_hi]` by one interval.

    Returns `"certain"`, `"possible"` or None (does not cover).

    * covers iff `lo(start) <= y_hi` and (`end` null or `hi(end) >= y_lo`);
    * certain iff additionally `hi(start) <= y_lo` and (`end` null or
      `lo(end) >= y_hi`);
    * `start: null` covers only `[lo(end), hi(end)]`, always "possible";
    * an open `end` extends to `build_date`, never past it.
    """
    start = try_parse_date(interval.get('start'))
    end = try_parse_date(interval.get('end'))
    open_end = interval.get('end') is None

    if open_end:
        # "Assumed ongoing" beyond the build date is not coverage (A3).
        if build_date is not None and y_lo > build_date:
            return None
    if start is None:
        if open_end or end is None:
            return None
        # A3: `start: null` covers exactly [lo(end), hi(end)].
        return 'possible' if end.lo() <= y_hi and end.hi() >= y_lo else None
    if start.lo() > y_hi:
        return None
    if not open_end:
        if end is None:
            return None
        if end.hi() < y_lo:
            return None
    certain = start.hi() <= y_lo and (open_end or end.lo() >= y_hi)
    return 'certain' if certain else 'possible'


def interval_covers(interval: dict, selection: Any, *, build_date: Any = None,
                    as_of_year: int | None = None) -> str | None:
    """`interval_coverage` driven by a `"YYYY"`/`"YYYY-MM"`/int selection."""
    if as_of_year is not None and build_date is None:  # pragma: no cover - v0.1 callers
        build_date = _dt.date(as_of_year, 12, 31)
    y_lo, y_hi = selection_bounds(selection)
    return interval_coverage(interval, y_lo, y_hi, build_date=as_date(build_date))


def covering_intervals(entity: Any, selection: Any, *, build_date: Any = None,
                       as_of_year: int | None = None) -> list[dict]:
    """Intervals that cover `selection` (certain or possible), in file order."""
    if as_of_year is not None and build_date is None:  # pragma: no cover - v0.1 callers
        build_date = _dt.date(as_of_year, 12, 31)
    y_lo, y_hi = selection_bounds(selection)
    day = as_date(build_date)
    return [row for row in _entity_intervals(entity)
            if interval_coverage(row, y_lo, y_hi, build_date=day) is not None]


def existence_hull(entity: Any, *, build_date: Any = None) -> tuple[_dt.date, _dt.date] | None:
    """A3 existence hull `[lo(earliest start), lo(earliest terminal start) or build date]`.

    None when no interval carries a usable start (nothing is known about when
    the entity existed).  An entity whose only terminal start precedes its
    earliest start (a data defect the validator rejects) yields a degenerate
    hull of one day rather than an inverted range.
    """
    rows = _entity_intervals(entity)
    starts: list[_dt.date] = []
    terminal_starts: list[_dt.date] = []
    terminal_ends: list[_dt.date] = []
    for row in rows:
        start = try_parse_date(row.get('start'))
        if start is not None:
            starts.append(start.lo())
        if row.get('status') in TERMINAL_STATUSES:
            if start is not None:
                terminal_starts.append(start.lo())
            end = try_parse_date(row.get('end'))
            if end is not None:
                terminal_ends.append(end.hi())
    if not starts:
        return None
    first = min(starts)
    build = as_date(build_date) or _dt.date.today()
    if terminal_starts:
        last = min(terminal_starts)
        # A terminal *event* with an end (e.g. a decommissioning campaign)
        # still belongs inside the hull.
        if terminal_ends:
            last = max(last, min(terminal_ends))
    else:
        last = build
    return first, max(first, last)


def present_at(entity: Any, selection: Any, *, build_date: Any = None) -> bool:
    """A3 presence: does the entity's existence hull touch the selection?"""
    hull = existence_hull(entity, build_date=build_date)
    if hull is None:
        return False
    y_lo, y_hi = selection_bounds(selection)
    return hull[0] <= y_hi and hull[1] >= y_lo


def _state_sort_key(row: dict, coverage: str, index: int) -> tuple:
    start = try_parse_date(row.get('start'))
    start_ordinal = start.lo().toordinal() if start is not None else -(1 << 30)
    status = row.get('status')
    return (start_ordinal, STATE_RANK.get(status, 0), 1 if coverage == 'certain' else 0, index)


def state_at(entity: Any, selection: Any, *, build_date: Any = None) -> dict | None:
    """A3 derived state at a slider selection.

    Returns None when the entity is absent, otherwise
    `{"status", "certainty", "secondary"}`:

    * `status` is the winning interval's status, or `"unrecorded"` when the
      existence hull covers the selection but no interval does;
    * `certainty` is `"certain"` or `"possible"` (A3; `"unrecorded"` is always
      possible);
    * `secondary` lists the other covering statuses for the tooltip.

    Selection rules, in order: (1) a realised or terminal covering interval
    knocks out every proposed/approved/planned candidate; (2) the latest
    `lo(start)` wins; (3) ties break by `STATE_PRECEDENCE`.
    """
    build = as_date(build_date)
    if not present_at(entity, selection, build_date=build):
        return None
    y_lo, y_hi = selection_bounds(selection)
    candidates: list[tuple[tuple, dict, str]] = []
    annotations: list[tuple[tuple, dict, str]] = []
    for index, row in enumerate(_entity_intervals(entity)):
        coverage = interval_coverage(row, y_lo, y_hi, build_date=build)
        if coverage is None:
            continue
        item = (_state_sort_key(row, coverage, index), row, coverage)
        if (row.get('kind') or 'lifecycle') == 'lifecycle':
            candidates.append(item)
        else:
            annotations.append(item)
    # A3: a run or a phase annotates a state rather than being one, so it only
    # decides the answer where no lifecycle interval covers the selection. A run
    # is how an experiment's operating years are usually recorded, but an
    # open-ended milestone such as a groundbreaking must never outrank the
    # operating interval that follows it.
    if not candidates:
        candidates = annotations
    if not candidates:
        return {'status': UNRECORDED, 'certainty': 'possible', 'secondary': []}
    strong = [item for item in candidates
              if item[1].get('status') in REALISED_STATUSES or item[1].get('status') in TERMINAL_STATUSES]
    if strong:
        candidates = [item for item in candidates if item[1].get('status') not in SPECULATIVE_STATUSES]
    candidates.sort(key=lambda item: item[0])
    _, winner, coverage = candidates[-1]
    secondary: list[str] = []
    for _, row, _cov in reversed(candidates[:-1]):
        status = row.get('status')
        if isinstance(status, str) and status != winner.get('status') and status not in secondary:
            secondary.append(status)
    return {'status': winner.get('status'), 'certainty': coverage, 'secondary': secondary}


def state_segments(entity: Any, build_date: Any = None) -> list[list]:
    """A3 precomputed timeline: `[[m0, m1, status, certainty], ...]`.

    Months are counted from 1950-01 (:data:`EPOCH_YEAR`); `m0` and `m1` are
    both inclusive.  Segments are contiguous runs of equal
    `(status, certainty)` over the entity's existence hull, so the slider,
    range mode, playback and the history tests never re-derive state.
    Months before the epoch produce negative indices rather than being
    silently clamped.
    """
    build = as_date(build_date) or _dt.date.today()
    hull = existence_hull(entity, build_date=build)
    if hull is None:
        return []
    first = month_index(hull[0])
    last = month_index(hull[1])
    if first is None or last is None or last < first:
        return []
    segments: list[list] = []
    for index in range(first, last + 1):
        m_lo, m_hi = month_bounds(index)
        state = state_at(entity, (m_lo, m_hi), build_date=build)
        if state is None:
            continue
        status, certainty = state['status'], state['certainty']
        if segments and segments[-1][2] == status and segments[-1][3] == certainty \
                and segments[-1][1] == index - 1:
            segments[-1][1] = index
        else:
            segments.append([index, index, status, certainty])
    return segments


def range_state(segments: Sequence[Sequence], m0: int, m1: int) -> dict | None:
    """A3 range mode: the state with the longest clipped duration in
    `[m0, m1]`, plus every status the range touches.

    `segments` is an entity's `state_segments`.  Returns None when the range
    touches nothing.
    """
    if m1 < m0:
        m0, m1 = m1, m0
    durations: dict[tuple[str, str], int] = {}
    order: list[tuple[str, str]] = []
    for segment in segments:
        start, end, status, certainty = segment[0], segment[1], segment[2], segment[3]
        overlap = min(end, m1) - max(start, m0) + 1
        if overlap <= 0:
            continue
        key = (status, certainty)
        if key not in durations:
            durations[key] = 0
            order.append(key)
        durations[key] += overlap
    if not durations:
        return None
    best = max(order, key=lambda key: (durations[key], STATE_RANK.get(key[0], 0), key[1] == 'certain'))
    statuses: list[str] = []
    for status, _certainty in order:
        if status not in statuses:
            statuses.append(status)
    return {
        'status': best[0],
        'certainty': best[1],
        'months': durations[best],
        'secondary': [status for status in statuses if status != best[0]],
    }


def intervals_overlap(a: dict, b: dict) -> bool | None:
    """Do two intervals share at least one day?  None when a date is malformed
    or an open bound makes the answer undecidable."""
    try:
        a_start, a_end = parse_date(a.get('start')), parse_date(a.get('end'))
        b_start, b_end = parse_date(b.get('start')), parse_date(b.get('end'))
    except DateError:
        return None
    if a_start is None or b_start is None:
        return None
    a_lo, b_lo = a_start.lo(), b_start.lo()
    a_hi = a_end.hi() if a_end else _dt.date.max
    b_hi = b_end.hi() if b_end else _dt.date.max
    return a_lo <= b_hi and b_lo <= a_hi


def interval_years(intervals: Iterable[dict]) -> tuple[int | None, int | None]:
    """(earliest start year, latest end year) over intervals; an open end
    yields None for the upper bound.  Unknown starts are ignored."""
    low: int | None = None
    high: int | None = None
    open_end = False
    for row in intervals:
        if not isinstance(row, dict):
            continue
        start, end = try_parse_date(row.get('start')), try_parse_date(row.get('end'))
        if start is not None and (low is None or start.lo().year < low):
            low = start.lo().year
        if end is None:
            if start is not None or 'end' in row:
                open_end = True
        elif high is None or end.hi().year > high:
            high = end.hi().year
    return low, (None if open_end else high)


def hull_gaps(entity: Any, *, build_date: Any = None) -> list[tuple[int, int]]:
    """A12 warning input: month ranges inside the hull that no interval covers.

    Each gap is `(first_month, last_month)` in months since the epoch.
    """
    segments = state_segments(entity, build_date)
    hull = existence_hull(entity, build_date=build_date)
    if hull is None:
        return []
    first, last = month_index(hull[0]), month_index(hull[1])
    if first is None or last is None:
        return []
    covered = {index for segment in segments for index in range(segment[0], segment[1] + 1)
               if segment[2] != UNRECORDED}
    gaps: list[tuple[int, int]] = []
    run: int | None = None
    for index in range(first, last + 1):
        if index in covered:
            if run is not None:
                gaps.append((run, index - 1))
                run = None
        elif run is None:
            run = index
    if run is not None:
        gaps.append((run, last))
    return gaps


# ---------------------------------------------------------------------------
# Memberships (A5, A19)
# ---------------------------------------------------------------------------

def membership_render(row: dict, selection: Any, *, formation: Any = None, as_of: Any = None,
                      build_date: Any = None, membership_history: str = 'unknown') -> dict | None:
    """A5 render decision for one membership row at a slider selection.

    Returns None when the row does not apply at all, otherwise
    `{"render": "solid"|"hollow", "counted": bool, "reason": str}`.

    * solid and counted when `[start, end]` or `[known_since, known_until]`
      covers the selection;
    * hollow "undated member" between the collaboration's formation and
      `known_since` (counted only when `membership_history == "complete"`);
    * hollow "not re-verified" between `as_of` and the build date.
    """
    y_lo, y_hi = selection_bounds(selection)
    build = as_date(build_date) or _dt.date.today()
    as_of_hi = hi(as_of)
    horizon = as_of_hi or build

    windows = [
        (row.get('start'), row.get('end')),
        (row.get('known_since'), row.get('known_until')),
    ]
    for start_value, end_value in windows:
        start, end = try_parse_date(start_value), try_parse_date(end_value)
        if start is None and end is None:
            continue
        low = start.lo() if start is not None else None
        high = end.hi() if end is not None else horizon
        if low is None:
            low = high  # a row known only by its last evidence date
        if low <= y_hi and high >= y_lo:
            return {'render': 'solid', 'counted': True, 'reason': 'confirmed'}

    known_since = try_parse_date(row.get('known_since'))
    start = try_parse_date(row.get('start'))
    earliest_evidence = min([d.lo() for d in (known_since, start) if d is not None], default=None)
    formation_lo = lo(formation)
    if formation_lo is not None and earliest_evidence is not None \
            and y_lo < earliest_evidence and y_hi >= formation_lo:
        return {
            'render': 'hollow',
            'counted': membership_history == 'complete',
            'reason': 'undated',
        }
    if as_of_hi is not None and y_lo > as_of_hi and y_lo <= build:
        # Still listed, but nobody re-checked the roster since `as_of`.
        end = try_parse_date(row.get('end'))
        if end is None or end.hi() >= y_lo:
            return {'render': 'hollow', 'counted': False, 'reason': 'not_re_verified'}
    if formation_lo is not None and earliest_evidence is None and y_hi >= formation_lo \
            and y_lo <= horizon:
        return {'render': 'hollow', 'counted': membership_history == 'complete', 'reason': 'undated'}
    return None


def membership_counts(rows: Iterable[dict], selection: Any, **kwargs: Any) -> dict[str, int]:
    """A5 "N confirmed members (+M undated)" counts for one roster."""
    confirmed = undated = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        verdict = membership_render(row, selection, **kwargs)
        if verdict is None:
            continue
        if verdict['render'] == 'solid':
            confirmed += 1
        elif verdict['reason'] == 'undated':
            undated += 1
    return {'confirmed': confirmed, 'undated': undated}


def strongest_evidence_class(classes: Iterable[Any]) -> str | None:
    """A19 precedence: the strongest of several evidence classes."""
    ranked = [c for c in classes if isinstance(c, str) and c in EVIDENCE_RANK]
    return min(ranked, key=lambda c: EVIDENCE_RANK[c]) if ranked else None


# ---------------------------------------------------------------------------
# Geometry (A21)
# ---------------------------------------------------------------------------

EARTH_RADIUS_M = 6_371_008.8


def great_circle_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in metres on a sphere of mean Earth radius."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    d_phi = p2 - p1
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(d_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(min(1.0, math.sqrt(a)))


def coordinates_of(record: Any) -> tuple[float, float] | None:
    coords = (record or {}).get('coordinates') if isinstance(record, dict) else None
    if not isinstance(coords, dict):
        return None
    lat, lon = coords.get('lat'), coords.get('lon')
    if is_number(lat) and is_number(lon):
        return float(lat), float(lon)
    return None


# ---------------------------------------------------------------------------
# Field specifications (§3 + A2, A9, A15, A16, A18)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FieldSpec:
    """How one field of an entity is shaped.

    kind is one of:
      str, int, bool, list, dict, id, ids, enum, enums (list of enum),
      sourced (S), sourced_date, sourced_list (SList), quantity (Q),
      quantity_map (dict name -> Q), intervals (I), coordinates (C),
      date, place, summary, links, coverage, external, external_reference,
      lineage, key_specs, membership_summary, leadership, affiliations,
      memberships, hep_graph, link_check, baselines, subsystems, volumes,
      country_list, placements, facility_roles, claim, identity_evidence,
      quantity_or_sourced, primary_beam,
      levels, unlocated, schematics, checks, validity, license, osm (A25)
    """

    kind: str
    required: bool = False
    enum: tuple[str, ...] | None = None
    ref_type: str | tuple[str, ...] | None = None   # for id/ids: which entity type(s)
    dimension: str | tuple[str, ...] | None = None  # for quantity: allowed dimension(s)
    nullable: bool = True
    derived: bool = False   # A1: never authored; the build fills it in
    note: str = ''


def _f(kind: str, required: bool = False, **kw: Any) -> FieldSpec:
    return FieldSpec(kind, required, **kw)


# Fields every "full" entity carries (§3 preamble).  Person, topic and source
# records have their own reduced shapes.
COMMON_FIELDS: dict[str, FieldSpec] = {
    'id': _f('str', True, nullable=False),
    'type': _f('str', True, nullable=False),
    'schema': _f('str'),                     # A11
    'name': _f('str', True, nullable=False),
    'aliases': _f('list', True),
    'distinct_from': _f('ids'),              # A20 escape hatch
    'superseded_by': _f('id'),               # A6
    'summary': _f('summary', True),
    'sources': _f('ids', True, ref_type='source'),   # A22 record-level identity claims
    'links': _f('links', True),
    'notes': _f('list', True),
    'coverage': _f('coverage', True),
}

ENTITY_FIELDS: dict[str, dict[str, FieldSpec]] = {
    'facility': {
        **COMMON_FIELDS,
        'kind': _f('enum', True, enum=FACILITY_KINDS),
        'operator': _f('sourced'),
        'operator_text': _f('sourced'),                      # A1
        'operator_ids': _f('ids', ref_type='institution'),   # A1 canonical
        'country': _f('country_list', True),
        'countries': _f('country_list'),                     # A9
        'primary_site_id': _f('id', True, ref_type='site'),
        'site_ids': _f('ids', ref_type='site', derived=True),
        'accelerator_ids': _f('ids', ref_type='accelerator', derived=True),
        'beamline_ids': _f('ids', ref_type='beamline', derived=True),
        'intervals': _f('intervals', True),
        'status': _f('enum', True, enum=STATUSES),
        'specs': _f('quantity_map'),
        'topic_ids': _f('ids', ref_type='topic'),
        'related_facility_ids': _f('ids', ref_type='facility'),
        'institution_id': _f('id', ref_type='institution', derived=True),
        'document_ids': _f('ids', ref_type='document', derived=True),
        'experiment_ids': _f('ids', ref_type='experiment', derived=True),
        'map_id': _f('id', ref_type='map', derived=True),               # A25
    },
    'site': {
        **COMMON_FIELDS,
        'facility_id': _f('id', True, ref_type='facility'),
        'coordinates': _f('coordinates', True, nullable=False),
        'setting': _f('enum', True, enum=SITE_SETTINGS),
        'depth': _f('quantity', dimension=('length', 'depth_mwe')),
        'depth_rock': _f('quantity', dimension='length'),      # A9
        'depth_mwe': _f('quantity', dimension='depth_mwe'),    # A9
        'altitude': _f('quantity', dimension='length'),
        'country': _f('str', True),
        'countries': _f('country_list'),
        'place': _f('place', True),
        'document_ids': _f('ids', ref_type='document', derived=True),
        'map_id': _f('id', ref_type='map', derived=True),               # A25
    },
    'accelerator': {
        **COMMON_FIELDS,
        'kind': _f('enum', True, enum=ACCELERATOR_KINDS),
        'is_collider': _f('bool'),                             # A9
        'facility_id': _f('id', True, ref_type='facility'),
        'site_id': _f('id', True, ref_type='site'),
        'particles': _f('list', True),
        'specs': _f('quantity_map'),
        'intervals': _f('intervals', True),
        'status': _f('enum', True, enum=STATUSES),
        'feeds_accelerator_ids': _f('ids', ref_type='accelerator'),
        'fed_by_accelerator_ids': _f('ids', ref_type='accelerator', derived=True),
        'serves_experiment_ids': _f('ids', ref_type='experiment', derived=True),
        'beamline_ids': _f('ids', ref_type='beamline', derived=True),
        'document_ids': _f('ids', ref_type='document', derived=True),
        'geometry_map_ids': _f('ids', ref_type='map', derived=True),    # A25
    },
    'beamline': {
        **COMMON_FIELDS,
        'facility_id': _f('id', True, ref_type='facility'),
        'accelerator_id': _f('id', True, ref_type='accelerator'),
        'primary_beam': _f('primary_beam'),                    # A9
        'target': _f('sourced'),
        'secondary_beam': _f('sourced'),
        'specs': _f('quantity_map'),
        'direction': _f('sourced'),
        'near_detector_site_ids': _f('ids', ref_type='site'),
        'far_detector_site_ids': _f('ids', ref_type='site'),
        'baselines': _f('baselines'),
        'intervals': _f('intervals', True),
        'status': _f('enum', True, enum=STATUSES),
        'experiment_ids': _f('ids', ref_type='experiment', derived=True),
        'document_ids': _f('ids', ref_type='document', derived=True),
        'geometry_map_ids': _f('ids', ref_type='map', derived=True),    # A25
    },
    'experiment': {
        **COMMON_FIELDS,
        'kind': _f('enum', True, enum=EXPERIMENT_KINDS),
        'secondary_kinds': _f('enums', enum=EXPERIMENT_KINDS),
        'collaboration_ids': _f('ids', True, ref_type='collaboration'),
        'facility_roles': _f('facility_roles', True),          # A2 canonical
        'site_ids': _f('ids', ref_type='site', derived=True),
        'detector_ids': _f('ids', ref_type='detector', derived=True),
        'beamline_ids': _f('ids', ref_type='beamline'),
        'accelerator_ids': _f('ids', ref_type='accelerator'),
        'topic_ids': _f('ids', True, ref_type='topic'),
        'intervals': _f('intervals', True),
        'status': _f('enum', True, enum=STATUSES),
        'physics_goals': _f('sourced_list'),                   # A9 SList
        'unique_capabilities': _f('sourced_list'),
        'energy_regime': _f('sourced'),
        'key_specs': _f('key_specs'),
        'lineage': _f('lineage'),
        'external': _f('external'),
        'document_ids': _f('ids', ref_type='document', derived=True),
        'result_ids': _f('ids', ref_type='result', derived=True),
    },
    'detector': {
        **COMMON_FIELDS,
        'experiment_ids': _f('ids', True, ref_type='experiment'),
        'placements': _f('placements', True),                  # A2 canonical
        'parent_detector_id': _f('id', ref_type='detector'),   # A2
        'technology': _f('sourced'),
        'technology_class': _f('enum', enum=TECHNOLOGY_CLASSES),
        'technology_classes': _f('enums', enum=TECHNOLOGY_CLASSES),  # A9, primary first
        'intervals': _f('intervals', True),
        'status': _f('enum', True, enum=STATUSES),
        'specs': _f('quantity_map'),
        'subsystems': _f('subsystems'),
        'document_ids': _f('ids', ref_type='document', derived=True),
        'geometry_map_ids': _f('ids', ref_type='map', derived=True),    # A25
    },
    'collaboration': {
        **COMMON_FIELDS,
        'experiment_ids': _f('ids', ref_type='experiment', derived=True),
        'formation': _f('sourced_date'),
        'intervals': _f('intervals', True),
        'status': _f('enum', True, enum=STATUSES),
        'membership': _f('membership_summary'),
        'leadership': _f('leadership'),
        'host_facility_id': _f('id', ref_type='facility'),
        'host_site_id': _f('id', ref_type='site'),
        'document_ids': _f('ids', ref_type='document', derived=True),
    },
    'institution': {
        **COMMON_FIELDS,
        'kind': _f('enum', True, enum=INSTITUTION_KINDS),
        'coordinates': _f('coordinates', True),
        'place': _f('place', True),
        'country': _f('str', True),
        'countries': _f('country_list'),
        'external': _f('external'),
        'facility_id': _f('id', ref_type='facility'),
        'parent_institution_id': _f('id', ref_type='institution'),   # A1
    },
    'person': {
        'id': _f('str', True, nullable=False),
        'type': _f('str', True, nullable=False),
        'schema': _f('str'),
        'name': _f('str', True, nullable=False),
        'aliases': _f('list'),
        'distinct_from': _f('ids'),
        'superseded_by': _f('id'),
        'external': _f('external', True),
        'identity_evidence': _f('identity_evidence'),           # A6
        'affiliations': _f('affiliations', True),
        'memberships': _f('memberships', True),
        'topic_ids': _f('ids', ref_type='topic'),
        'hep_graph': _f('hep_graph', derived=True),             # A6/A22
        'sources': _f('ids', True, ref_type='source'),
        'notes': _f('list'),
    },
    'result': {
        **COMMON_FIELDS,
        'experiment_ids': _f('ids', True, ref_type='experiment'),
        'collaboration_ids': _f('ids', ref_type='collaboration'),
        'facility_ids': _f('ids', ref_type='facility'),
        'detector_ids': _f('ids', ref_type='detector'),
        'date': _f('sourced_date', True),
        'date_kind': _f('enum', True, enum=RESULT_DATE_KINDS),  # A16
        'announced': _f('sourced_date'),                        # A9
        'published': _f('sourced_date'),                        # A9
        'claim': _f('claim', True),                             # A16
        'topic_ids': _f('ids', True, ref_type='topic'),
        'result_type': _f('enum', True, enum=RESULT_TYPES),
        'title': _f('str', True),
        'why_it_matters': _f('str'),
        'key_value': _f('quantity'),                            # A9
        'key_value_text': _f('sourced'),                        # A9
        'significance': _f('sourced'),
        'publication': _f('external_reference'),
        'publication_source_id': _f('id', ref_type='source'),   # A7
        'official_url': _f('sourced'),
        'hepdata': _f('str'),
    },
    'document': {
        **COMMON_FIELDS,
        'doc_type': _f('enum', True, enum=DOC_TYPES),
        'date': _f('date', True),
        'owner_ids': _f('ids', True, ref_type=tuple(sorted(DOCUMENT_OWNER_TYPES))),
        'reference': _f('external_reference', True),
        'source_id': _f('id', ref_type='source'),               # A7
        'volumes': _f('volumes'),
    },
    'topic': {
        'id': _f('str', True, nullable=False),
        'type': _f('str'),
        'schema': _f('str'),
        'name': _f('str', True, nullable=False),
        'aliases': _f('list'),
        'parent_id': _f('id', True, ref_type='topic'),
        'question': _f('str', True),
        'overview': _f('str', True),
        'observables': _f('list', True),
        'sources': _f('ids', True, ref_type='source'),
    },
    # A25 — the local-map geometry layer (docs/HEP_ATLAS_GEOMETRY.md §1).
    'map': {
        **COMMON_FIELDS,
        'facility_id': _f('id', True, ref_type='facility', nullable=False),
        'site_ids': _f('ids', ref_type='site'),
        'center': _f('coordinates', True, nullable=False),
        'extent_m': _f('int', True, nullable=False),     # half-width, 500-60 000 m
        'levels': _f('levels', True),
        'unlocated': _f('unlocated', True),
        'schematics': _f('schematics'),
        'linked_map_ids': _f('ids', ref_type='map'),     # authored; the build adds derived ones
    },
    'geometry': {
        **COMMON_FIELDS,
        'map_id': _f('id', True, ref_type='map', nullable=False),
        'entity_id': _f('id', True, ref_type=GEOMETRY_ENTITY_TYPES),   # null for context features
        'site_id': _f('id', ref_type='site'),
        'feature_type': _f('enum', True, enum=FEATURE_TYPES, nullable=False),
        'level_id': _f('str', True, nullable=False),     # one of the map's levels[].id
        'depth_m': _f('quantity', dimension='length'),
        'representation': _f('enum', True, enum=REPRESENTATIONS, nullable=False),
        'accuracy_m': _f('int'),                         # required except inferred_direction
        'method': _f('str'),
        'geometry': _f('sourced', True, nullable=False),  # value is a GeoJSON geometry object
        'checks': _f('checks'),
        'valid': _f('validity'),
        'license': _f('license'),
        'osm': _f('osm'),
    },
    # A28 — guided tours (docs/HEP_ATLAS_ONTOLOGY.md A28; rules in tours.py).
    # A tour is not a `COMMON_FIELDS` entity: it has no coverage tier, links or
    # aliases.  Its steps are validated by `hepgraph.atlas.tours`, not by the
    # generic field table, so the table only names the top-level shape.
    'tour': {
        'id': _f('str', True, nullable=False),
        'type': _f('str', True, nullable=False),
        'schema': _f('str'),
        'name': _f('str', True, nullable=False),                # a working title
        'order': _f('int'),                                     # position in the tour list
        'summary': _f('str', True, nullable=False),             # what the tour is, not a fact
        'audience': _f('str', True, nullable=False),
        'estimated_minutes': _f('int', True, nullable=False),
        'sources': _f('ids', True, ref_type='source'),          # every source its claims rest on
        'steps': _f('list', True, nullable=False),
        'notes': _f('list'),
        'superseded_by': _f('id'),
    },
    'source': {
        'id': _f('str', True, nullable=False),
        'type': _f('str', True, nullable=False),                # A7: "src"
        'schema': _f('str'),
        'source_type': _f('enum', True, enum=SOURCE_TYPES),
        'rank': _f('int', derived=True),                        # A7/A18 derived
        'title': _f('str', True),
        'publisher': _f('str'),
        'publisher_id': _f('id', ref_type=('collaboration', 'facility', 'institution')),
        'part_of': _f('id', ref_type='source'),                 # A20: a chapter/volume's container
        'url': _f('str', True),
        'archive_url': _f('str'),                               # A18
        'content_hash': _f('str'),                              # A18, link checker
        'retrieval': _f('enum', enum=RETRIEVALS),               # A18
        'reference': _f('external_reference'),
        'accessed': _f('date', True),                           # A18 required
        'date': _f('date'),
        'excerpt': _f('str'),
        'cited_by': _f('dict', derived=True),                   # A22/§8 derived
        'link_check': _f('link_check'),
    },
}

# A7: the `type` field a source file carries.
SOURCE_TYPE_FIELD_VALUE = 'src'
SOURCE_TYPE_FIELD_LEGACY = 'source'

# A1: fields the build derives.  Authoring them is a validator warning and the
# build ignores whatever was written.
DERIVED_FIELDS: dict[str, tuple[str, ...]] = {
    entity_type: tuple(sorted(name for name, spec in fields.items() if spec.derived))
    for entity_type, fields in ENTITY_FIELDS.items()
}

# A1: legacy field -> the v0.2 field that replaces it (load.py migrates).
LEGACY_FIELDS: dict[str, dict[str, str]] = {
    'detector': {'site_id': 'placements', 'facility_id': 'placements',
                 'technology_class': 'technology_classes'},
    'experiment': {'facility_ids': 'facility_roles'},
    'facility': {'operator': 'operator_text'},
}

# Non-entity file shapes.
MEMBERSHIP_FILE_FIELDS: dict[str, FieldSpec] = {
    'schema': _f('str'),
    'collaboration_id': _f('id', True, ref_type='collaboration', nullable=False),
    'as_of': _f('date', True),
    'membership_history': _f('enum', True, enum=MEMBERSHIP_HISTORY_LEVELS),  # A5 required
    'roster_snapshots': _f('list'),                                          # A5
    'roster_sources': _f('ids', True, ref_type='source'),                    # A19 documentation
    'members': _f('list', True),
}
MEMBERSHIP_ROW_FIELDS: dict[str, FieldSpec] = {
    'institution_id': _f('id', True, ref_type='institution', nullable=False),
    'start': _f('date', True),
    'end': _f('date', True),
    'known_since': _f('date'),        # A5 earliest evidence date
    'known_until': _f('date'),        # A5 latest evidence date
    'evidence_class': _f('enum', True, enum=EVIDENCE_CLASSES),   # A19 per-row required
    'evidence_date': _f('date'),                                 # A19
    'sources': _f('ids', True, ref_type='source'),
    'verified_at': _f('date', True),
    'confidence': _f('enum', True, enum=CONFIDENCES),
    'quote': _f('str'),               # A15
    'locator': _f('str'),             # A15
    'note': _f('str'),
}
# A10: the registry keeps planning fields only; `validated`/`globe_ready` are
# build outputs and are dropped from authored rows with a warning.
COVERAGE_ROW_FIELDS: dict[str, FieldSpec] = {
    'name': _f('str', True),
    'entity_id': _f('id', ref_type='experiment', nullable=False),
    'experiment_id': _f('id', ref_type='experiment', nullable=False),
    'category': _f('enum', enum=EXPERIMENT_KINDS),
    'facility': _f('str'),
    'status': _f('enum', enum=STATUSES),
    'tier': _f('enum', True, enum=COVERAGE_TIERS),
    'priority': _f('int', True),
    'researched': _f('enum', True, enum=RESEARCHED_LEVELS),
    'validated': _f('bool', derived=True),
    'globe_ready': _f('bool', derived=True),
    'missing_fields': _f('list', True),
    'owner': _f('str', True),
    'notes': _f('str'),
}
COVERAGE_DERIVED_FIELDS: tuple[str, ...] = ('validated', 'globe_ready')

SOURCED_VALUE_KEYS: tuple[str, ...] = ('value', 'sources', 'verified_at', 'confidence', 'note',
                                       'quote', 'locator')
INTERVAL_KEYS: tuple[str, ...] = ('label', 'status', 'start', 'end', 'kind', 'specs', 'sources',
                                  'verified_at', 'confidence', 'note', 'quote', 'locator')
COORDINATE_KEYS: tuple[str, ...] = ('lat', 'lon', 'precision_m', 'kind', 'sources', 'verified_at',
                                    'confidence', 'note', 'quote', 'locator')
QUANTITY_KEYS: tuple[str, ...] = ('value', 'min', 'max', 'unit', 'dimension', 'approx', 'display',
                                  'sources', 'verified_at', 'confidence', 'note', 'quote', 'locator')
PLACEMENT_KEYS: tuple[str, ...] = ('site_id', 'role', 'start', 'end', 'sources', 'verified_at',
                                   'confidence', 'note', 'quote', 'locator')
FACILITY_ROLE_KEYS: tuple[str, ...] = ('facility_id', 'role', 'start', 'end', 'sources',
                                       'verified_at', 'confidence', 'note', 'quote', 'locator')
CLAIM_KEYS: tuple[str, ...] = ('quote', 'locator', 'sources')

# A15: values that must carry a `quote` or a `locator`.
CLAIM_EVIDENCE_REQUIRED_PATHS: tuple[str, ...] = (
    'coordinates', 'key_specs', 'baselines', 'formation',
)

# Provenance keys that move out of atlas.json into provenance.json (A14).
PROVENANCE_KEYS: tuple[str, ...] = ('sources', 'verified_at', 'confidence', 'note', 'quote', 'locator')
# Keys a stripped value keeps in atlas.json (A14).
STRIPPED_VALUE_KEYS: tuple[str, ...] = ('value', 'unit', 'dimension', 'display', 'min', 'max',
                                        'approx', 'status', 'start', 'end', 'label', 'kind')

# Fields that hold long text and move to text.json at build time (§8).
LONG_TEXT_FIELDS: dict[str, tuple[str, ...]] = {
    'default': ('summary.technical', 'notes'),
    'experiment': ('summary.technical', 'notes', 'physics_goals', 'unique_capabilities'),
    'result': ('summary.technical', 'notes', 'why_it_matters', 'claim'),
    'topic': ('overview',),
}


def required_fields(entity_type: str) -> list[str]:
    return [name for name, spec in ENTITY_FIELDS[entity_type].items() if spec.required]


def reference_fields(entity_type: str) -> dict[str, FieldSpec]:
    """Fields of kind id/ids for an entity type (dangling-reference checks)."""
    return {name: spec for name, spec in ENTITY_FIELDS[entity_type].items() if spec.kind in {'id', 'ids'}}


def is_sourced_value(value: Any) -> bool:
    """Loose shape test: a dict with `value` and `sources` keys."""
    return isinstance(value, dict) and 'value' in value and 'sources' in value


def is_quantity(value: Any) -> bool:
    return isinstance(value, dict) and 'dimension' in value and ('value' in value or ('min' in value and 'max' in value))


def is_coordinates(value: Any) -> bool:
    return isinstance(value, dict) and 'lat' in value and 'lon' in value


def is_interval(value: Any) -> bool:
    return isinstance(value, dict) and 'status' in value and 'start' in value and 'end' in value


def ref_entry(entry: Any) -> tuple[str | None, dict | None]:
    """A9: an `*_ids` entry is either an id string or `{"id", "start", "end", "sources"}`.

    Returns `(id, interval_or_None)`.
    """
    if isinstance(entry, str):
        return entry, None
    if isinstance(entry, dict) and isinstance(entry.get('id'), str):
        if entry.get('start') is not None or entry.get('end') is not None:
            return entry['id'], {'start': entry.get('start'), 'end': entry.get('end'),
                                 'status': 'active', 'sources': entry.get('sources') or []}
        return entry['id'], None
    return None, None


def ref_ids(value: Any) -> list[str]:
    """Every id in an `*_ids` list, accepting both A9 entry shapes."""
    if isinstance(value, str):
        return [value]
    if not isinstance(value, list):
        return []
    out = []
    for entry in value:
        entity_id, _ = ref_entry(entry)
        if entity_id is not None:
            out.append(entity_id)
    return out


def slist(value: Any) -> list[dict]:
    """A9 `SList<T>` = `[Sourced<T>]`, tolerating the v0.1 single-sourced form.

    `physics_goals`, `unique_capabilities` and `subsystems[].description` are
    lists of sourced values in v0.2.  A v0.1 file wrote one sourced value whose
    `value` was a list; this expands that into the v0.2 shape so build code has
    a single case to handle.  (The validator still warns about the old form.)
    """
    if isinstance(value, list):
        return [row for row in value if isinstance(row, dict)]
    if is_sourced_value(value):
        inner = value.get('value')
        provenance = {k: v for k, v in value.items() if k != 'value'}
        if isinstance(inner, list):
            return [{'value': item, **provenance} for item in inner]
        return [dict(value)]
    return []


def slist_is_legacy(value: Any) -> bool:
    """True when an SList field was written in the v0.1 single-sourced form."""
    return not isinstance(value, list) and is_sourced_value(value)


#: Keys that end in `_id` but name something *inside* a record rather than an
#: entity in the atlas.  A25's `geometry.level_id` names one of its own map's
#: `levels[].id`, which is a local label like `"surface"`, not `type:slug`;
#: without this the dangling-reference rule would read every level name as a
#: broken entity id.  `geometry-unknown-level` is what checks it instead.
NON_REFERENCE_ID_KEYS: frozenset[str] = frozenset({'level_id'})


def iter_reference_fields(record: Any, path: str = '') -> Iterable[tuple[str, str]]:
    """Yield (json_path, id) for every value under a key named `*_id` /
    `*_ids` (and `sources`, `roster_sources`, `roster_source_ids`,
    `distinct_from`, `part_of`), recursively, skipping
    :data:`NON_REFERENCE_ID_KEYS`.

    Used by the validator for the §9 / A12 "dangling references" rule,
    independent of the per-type field tables.  A9 object entries are
    reported at `path[i].id`.
    """
    if isinstance(record, dict):
        for key, value in record.items():
            here = f'{path}.{key}' if path else key
            if key in NON_REFERENCE_ID_KEYS:
                continue
            if (key.endswith('_id') or key == 'part_of') and isinstance(value, str):
                yield here, value
            elif key.endswith('_ids') or key in {'sources', 'roster_sources', 'distinct_from'}:
                if isinstance(value, list):
                    for index, item in enumerate(value):
                        if isinstance(item, str):
                            yield f'{here}[{index}]', item
                        elif isinstance(item, dict):
                            if isinstance(item.get('id'), str):
                                yield f'{here}[{index}].id', item['id']
                            yield from iter_reference_fields(
                                {k: v for k, v in item.items() if k != 'id'}, f'{here}[{index}]')
            else:
                yield from iter_reference_fields(value, here)
    elif isinstance(record, list):
        for index, item in enumerate(record):
            yield from iter_reference_fields(item, f'{path}[{index}]')


def topic_depth(topic_id: str, topics: dict[str, dict]) -> int | None:
    """1 for a root topic, 2 for its child, ...; None on a cycle or dangling parent."""
    depth = 0
    seen: set[str] = set()
    current: str | None = topic_id
    while current is not None:
        if current in seen or current not in topics:
            return None
        seen.add(current)
        depth += 1
        current = topics[current].get('parent_id')
    return depth


def word_count(text: Any) -> int:
    return len(str(text or '').split())


def months_between(earlier: Any, later: Any) -> int | None:
    """Whole months from `earlier` to `later` (negative when reversed)."""
    a, b = month_index(earlier), month_index(later)
    return None if a is None or b is None else b - a
