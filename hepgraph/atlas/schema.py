"""HEP Atlas data contract: entity field specs, enums, units, dates, intervals.

Everything here mirrors docs/HEP_ATLAS_ONTOLOGY.md (v0.1).  The validator,
the build step and the scaffold generator import their vocabulary from this
module so that a change to the contract happens in exactly one place.

Nothing in this module reads files or depends on anything outside the
standard library.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import datetime as _dt
import re
from typing import Any, Iterable

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
PERSON_INSPIRE_RE = re.compile(r'^person:inspire:[0-9]+$')
PERSON_UNRESOLVED_RE = re.compile(r'^person:unresolved:[a-z0-9]+(?:-[a-z0-9]+)*$')
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
    """Structural check: known prefix and a `-`-slug (people allow one extra `:`)."""
    if not isinstance(entity_id, str):
        return False
    kind = id_type(entity_id)
    if kind is None:
        return False
    if kind == 'person':
        return bool(PERSON_INSPIRE_RE.match(entity_id) or PERSON_UNRESOLVED_RE.match(entity_id))
    return bool(SLUG_RE.match(id_slug(entity_id)))


def filename_for(entity_id: str) -> str:
    """Basename (without .json) of the canonical file for an entity id.

    The slug is the id without its type prefix.  Person ids carry a second
    colon (`person:inspire:123`), which is not a portable filename character,
    so any remaining `:` becomes `-` (`inspire-123.json`).
    """
    return id_slug(entity_id).replace(':', '-')


def path_for(entity_id: str) -> str:
    """Relative path under data/atlas/ for an entity id, e.g. `experiments/dune.json`."""
    kind = id_type(entity_id)
    if kind is None:
        raise ValueError(f'unknown id prefix: {entity_id!r}')
    return f'{ENTITY_DIRS[kind]}/{filename_for(entity_id)}.json'


# ---------------------------------------------------------------------------
# Enumerations (§3–§6)
# ---------------------------------------------------------------------------

STATUSES: tuple[str, ...] = (
    'proposed', 'approved', 'construction', 'commissioning', 'active', 'shutdown',
    'upgrade', 'completed', 'decommissioned', 'cancelled', 'planned',
)
TERMINAL_STATUSES: frozenset[str] = frozenset({'completed', 'decommissioned', 'cancelled'})
# States that render dimmed and never as "operating" (§4).
DIMMED_STATUSES: frozenset[str] = frozenset({'proposed', 'planned'})

CONFIDENCES: tuple[str, ...] = ('verified', 'derived', 'approximate', 'uncertain')
COORDINATE_KINDS: tuple[str, ...] = ('detector', 'campus', 'underground_lab', 'headquarters', 'approximate_region')
# Kinds a globe marker for a detector/site may use (§2.5).
DETECTOR_COORDINATE_KINDS: frozenset[str] = frozenset({'detector', 'underground_lab'})
INSTITUTION_COORDINATE_KINDS: frozenset[str] = frozenset({'campus', 'headquarters'})

FACILITY_KINDS: tuple[str, ...] = (
    'accelerator_laboratory', 'underground_laboratory', 'neutrino_observatory',
    'astroparticle_observatory', 'reactor_site', 'spallation_source',
    'research_laboratory', 'polar_station', 'deep_sea_site',
)
SITE_SETTINGS: tuple[str, ...] = ('surface', 'underground', 'ice', 'sea', 'lake', 'balloon', 'mountain')
ACCELERATOR_KINDS: tuple[str, ...] = ('synchrotron', 'linac', 'storage_ring', 'collider', 'cyclotron', 'booster')
EXPERIMENT_KINDS: tuple[str, ...] = (
    'collider', 'fixed_target', 'accelerator_neutrino', 'reactor_neutrino', 'solar_neutrino',
    'atmospheric_neutrino', 'astrophysical_neutrino', 'direct_dark_matter', 'axion',
    'double_beta_decay', 'neutrino_mass', 'muon_precision', 'rare_kaon', 'long_lived_particle',
    'cosmic_ray', 'gamma_ray', 'heavy_ion', 'cevns', 'other',
)
LINEAGE_RELATIONS: tuple[str, ...] = (
    'predecessor', 'successor', 'upgrade_of', 'upgraded_to', 'same_program', 'complementary',
)
TECHNOLOGY_CLASSES: tuple[str, ...] = (
    'lar_tpc', 'water_cherenkov', 'liquid_scintillator', 'xenon_tpc', 'argon_tpc',
    'cryogenic_bolometer', 'germanium', 'scintillating_crystal', 'general_purpose_collider',
    'forward_spectrometer', 'ice_cherenkov', 'sea_cherenkov', 'radio', 'air_shower_array',
    'imaging_atmospheric_cherenkov', 'gaseous_tpc', 'emulsion', 'tracking_calorimeter',
    'haloscope', 'spectrometer', 'other',
)
INSTITUTION_KINDS: tuple[str, ...] = (
    'university', 'national_laboratory', 'research_institute', 'international_organization',
    'agency', 'company',
)
EVIDENCE_CLASSES: tuple[str, ...] = (
    'official_roster', 'official_institution_list', 'publication_affiliation_current',
    'publication_affiliation_historical', 'institutional_page', 'derived',
)
EVIDENCE_CLASS_LABELS: dict[str, str] = {
    'official_roster': 'Collaboration roster',
    'official_institution_list': 'Official institution list',
    'publication_affiliation_current': 'Recent collaboration author affiliation',
    'publication_affiliation_historical': 'Historical collaboration author affiliation',
    'institutional_page': 'Institution states participation',
    'derived': 'Derived; unverified',
}
PERSON_ROLES: tuple[str, ...] = (
    'faculty', 'staff_scientist', 'postdoc', 'graduate_student', 'other_researcher',
    'historical_member', 'unknown',
)
RESULT_TYPES: tuple[str, ...] = (
    'discovery', 'observation', 'evidence', 'measurement', 'precision_measurement', 'limit',
    'anomaly', 'first_detection', 'technology_milestone',
)
DOC_TYPES: tuple[str, ...] = (
    'conceptual_design_report', 'technical_design_report', 'technical_proposal',
    'letter_of_intent', 'detector_paper', 'performance_paper', 'physics_paper', 'run_plan',
    'beam_design', 'upgrade_report', 'public_note', 'hepdata_record', 'data_release',
    'software_documentation', 'review_article',
)
SOURCE_TYPES: tuple[str, ...] = (
    'official_experiment_site', 'official_facility_site', 'experiment_registry',
    'inspire_record', 'design_report', 'detector_paper', 'hepdata', 'pdg', 'institution_page',
    'result_page', 'journal_article', 'arxiv', 'secondary',
)
COVERAGE_TIERS: tuple[str, ...] = ('A', 'B', 'C', 'D', 'E')
RESEARCHED_LEVELS: tuple[str, ...] = ('none', 'partial', 'full')
# Owner types a document may describe (§3.13) and a source-of-truth for the
# `DESCRIBES` edge in §7.
DOCUMENT_OWNER_TYPES: frozenset[str] = frozenset({
    'experiment', 'facility', 'accelerator', 'beamline', 'detector', 'collaboration',
})
TOPIC_MAX_DEPTH = 3
SUMMARY_PLAIN_MAX_WORDS = 60
KEY_SPECS_MAX = 5
EXCERPT_MAX_CHARS = 300
EXTERNAL_REFERENCE_KEYS: tuple[str, ...] = ('doi', 'arxiv', 'inspire', 'url', 'report_number', 'hepdata')

# ---------------------------------------------------------------------------
# Units (§2.4)
# ---------------------------------------------------------------------------

UNITS: dict[str, tuple[str, ...]] = {
    'length': ('m', 'km', 'cm', 'mm'),
    'mass': ('kg', 't', 'kt'),
    'energy': ('eV', 'keV', 'MeV', 'GeV', 'TeV'),
    'power': ('W', 'kW', 'MW'),
    'luminosity': ('cm^-2 s^-1',),
    'integrated_luminosity': ('pb^-1', 'fb^-1', 'ab^-1'),
    'magnetic_field': ('T',),
    'depth_mwe': ('m.w.e.',),
    'volume': ('m^3', 'km^3'),
    'count': ('',),
    'time': ('s', 'ms', 'ns', 'd', 'yr'),
    'angle': ('deg', 'mrad'),
    'temperature': ('K', 'mK'),
    'pressure': ('bar', 'Pa'),
    'frequency': ('Hz', 'kHz', 'MHz', 'GHz'),
}
DIMENSIONS: tuple[str, ...] = tuple(UNITS)

# Multipliers to the first (base) unit of each dimension, for comparisons.
UNIT_SCALE: dict[str, dict[str, float]] = {
    'length': {'m': 1.0, 'km': 1e3, 'cm': 1e-2, 'mm': 1e-3},
    'mass': {'kg': 1.0, 't': 1e3, 'kt': 1e6},
    'energy': {'eV': 1.0, 'keV': 1e3, 'MeV': 1e6, 'GeV': 1e9, 'TeV': 1e12},
    'power': {'W': 1.0, 'kW': 1e3, 'MW': 1e6},
    'luminosity': {'cm^-2 s^-1': 1.0},
    'integrated_luminosity': {'pb^-1': 1.0, 'fb^-1': 1e3, 'ab^-1': 1e6},
    'magnetic_field': {'T': 1.0},
    'depth_mwe': {'m.w.e.': 1.0},
    'volume': {'m^3': 1.0, 'km^3': 1e9},
    'count': {'': 1.0},
    'time': {'s': 1.0, 'ms': 1e-3, 'ns': 1e-9, 'd': 86400.0, 'yr': 365.25 * 86400.0},
    'angle': {'deg': 1.0, 'mrad': 180.0 / (1000.0 * 3.141592653589793)},
    'temperature': {'K': 1.0, 'mK': 1e-3},
    'pressure': {'bar': 1.0, 'Pa': 1e-5},
    'frequency': {'Hz': 1.0, 'kHz': 1e3, 'MHz': 1e6, 'GHz': 1e9},
}


def unit_allowed(dimension: Any, unit: Any) -> bool:
    """True when `unit` is one of the recognised units of `dimension`.

    A `count` quantity uses the empty unit; `None` is accepted for it as well
    because JSON authors naturally write `"unit": null` for a bare count.
    """
    units = UNITS.get(dimension)
    if units is None:
        return False
    if dimension == 'count' and unit is None:
        return True
    return unit in units


def quantity_magnitude(quantity: dict) -> float | None:
    """Value (or range midpoint) of a quantity expressed in its dimension's base unit."""
    dimension, unit = quantity.get('dimension'), quantity.get('unit')
    if not unit_allowed(dimension, unit):
        return None
    scale = UNIT_SCALE[dimension][unit or '']
    if 'value' in quantity and isinstance(quantity['value'], (int, float)) and not isinstance(quantity['value'], bool):
        return float(quantity['value']) * scale
    low, high = quantity.get('min'), quantity.get('max')
    if isinstance(low, (int, float)) and isinstance(high, (int, float)):
        return (float(low) + float(high)) / 2.0 * scale
    return None


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


# ---------------------------------------------------------------------------
# Dates (§2.2)
# ---------------------------------------------------------------------------

DATE_RE = re.compile(r'^(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?$')
PRECISIONS: tuple[str, ...] = ('year', 'month', 'day')


class DateError(ValueError):
    """A date string or date object does not follow §2.2."""


@dataclass(frozen=True)
class ParsedDate:
    """A calendar date with the precision it was written at.

    `first_day()` / `last_day()` give the inclusive range of real days the
    written date denotes: "2008" is 2008-01-01 … 2008-12-31, "2008-09" is
    2008-09-01 … 2008-09-30, "2008-09-10" is one day.
    """

    text: str
    year: int
    month: int | None
    day: int | None
    approx: bool = False
    planned: bool = False
    note: str = ''

    @property
    def precision(self) -> str:
        if self.day is not None:
            return 'day'
        if self.month is not None:
            return 'month'
        return 'year'

    def first_day(self) -> _dt.date:
        return _dt.date(self.year, self.month or 1, self.day or 1)

    def last_day(self) -> _dt.date:
        if self.day is not None:
            return _dt.date(self.year, self.month, self.day)
        if self.month is not None:
            return _dt.date(self.year, self.month, _days_in_month(self.year, self.month))
        return _dt.date(self.year, 12, 31)

    def __str__(self) -> str:  # pragma: no cover - convenience
        return self.text


def _days_in_month(year: int, month: int) -> int:
    if month == 12:
        return 31
    return (_dt.date(year, month + 1, 1) - _dt.timedelta(days=1)).day


def parse_date(value: Any) -> ParsedDate | None:
    """Parse a §2.2 date (string or object).  `None` stays `None`.

    Raises DateError for anything malformed: wrong shape, an impossible
    calendar date, an object without `date`, or qualifiers of the wrong type.
    """
    if value is None:
        return None
    approx = planned = False
    note = ''
    if isinstance(value, dict):
        if 'date' not in value:
            raise DateError('date object needs a "date" key')
        for key in ('approx', 'planned'):
            if key in value and not isinstance(value[key], bool):
                raise DateError(f'date qualifier {key!r} must be a boolean')
        if 'note' in value and value['note'] is not None and not isinstance(value['note'], str):
            raise DateError('date note must be a string')
        unknown = set(value) - {'date', 'approx', 'planned', 'note'}
        if unknown:
            raise DateError(f'unknown date keys: {sorted(unknown)}')
        approx = bool(value.get('approx', False))
        planned = bool(value.get('planned', False))
        note = value.get('note') or ''
        text = value['date']
        if text is None:
            return None
    else:
        text = value
    if not isinstance(text, str):
        raise DateError(f'date must be a string, got {type(text).__name__}')
    match = DATE_RE.match(text)
    if not match:
        raise DateError(f'date {text!r} is not YYYY, YYYY-MM or YYYY-MM-DD')
    year = int(match.group(1))
    month = int(match.group(2)) if match.group(2) else None
    day = int(match.group(3)) if match.group(3) else None
    try:
        _dt.date(year, month or 1, day or 1)
    except ValueError as exc:
        raise DateError(f'date {text!r} is not a real calendar date: {exc}') from None
    if year < 1000:
        raise DateError(f'date {text!r} has an implausible year')
    return ParsedDate(text, year, month, day, approx=approx, planned=planned, note=note)


def date_precision(value: Any) -> str | None:
    parsed = parse_date(value)
    return parsed.precision if parsed else None


def try_parse_date(value: Any) -> ParsedDate | None:
    """parse_date that swallows malformed input (returns None).  For build code
    running on data the validator has already accepted."""
    try:
        return parse_date(value)
    except DateError:
        return None


# ---------------------------------------------------------------------------
# Intervals and timeline semantics (§2.3, §4)
# ---------------------------------------------------------------------------

def year_bounds(year: int) -> tuple[_dt.date, _dt.date]:
    return _dt.date(year, 1, 1), _dt.date(year, 12, 31)


def interval_covers(interval: dict, year: int, *, as_of_year: int | None = None) -> bool | None:
    """Does this interval cover calendar year `year`?  True / False / None.

    Rule (§2.2, §2.3, §4):
    * A date covers every real day of its precision: start "2008" begins on
      2008-01-01 and start "2008-09" on 2008-09-01; an end date is inclusive
      of its precision, so end "2008" runs to 2008-12-31 and end "2008-09" to
      2008-09-30.  The interval covers `year` when its day range intersects
      1 Jan … 31 Dec of that year.
    * `end: null` with a non-terminal status means "ongoing": it covers every
      year from the start on.  `end: null` with a terminal status (which the
      validator only allows for `confidence: uncertain`) is treated as ending
      in an unknown year: it covers the start year and returns None (unknown)
      for later years.
    * `start: null` means "start unknown", **not** "since forever".  Such an
      interval definitely covers its end year (if an end is given) or the year
      of `verified_at` / `as_of_year` (if ongoing); for earlier years the
      answer is None (unknown), never True.
    * Malformed dates make the whole interval unknown (None).
    """
    try:
        start = parse_date(interval.get('start'))
        end = parse_date(interval.get('end'))
    except DateError:
        return None
    year_start, year_end = year_bounds(year)
    status = interval.get('status')
    terminal = status in TERMINAL_STATUSES
    if start is not None and start.first_day() > year_end:
        return False
    if end is not None and end.last_day() < year_start:
        return False
    if start is None:
        # Anchored only at the end (or at verified_at when ongoing).
        anchor = end.year if end is not None else _anchor_year(interval, as_of_year)
        if anchor is None:
            return None
        if year == anchor:
            return True
        if year > anchor and end is None and not terminal:
            return True
        return None
    if end is None and terminal:
        return True if year == start.year else None
    return True


def _anchor_year(interval: dict, as_of_year: int | None) -> int | None:
    if as_of_year is not None:
        return as_of_year
    verified = try_parse_date(interval.get('verified_at'))
    return verified.year if verified else None


def _entity_intervals(entity: dict | list) -> list[dict]:
    intervals = entity if isinstance(entity, list) else entity.get('intervals') or []
    return [row for row in intervals if isinstance(row, dict)]


def present_at(entity: dict | list, year: int, *, as_of_year: int | None = None) -> bool | None:
    """Is the entity present in `year` (§4)?

    True when some interval covers the year, False when every interval
    excludes it, None when the answer depends on an unknown start or end.
    An entity with no intervals is never present (None: nothing is known).
    `entity` may be the record or its `intervals` list.
    """
    rows = _entity_intervals(entity)
    if not rows:
        return None
    verdicts = [interval_covers(row, year, as_of_year=as_of_year) for row in rows]
    if any(v is True for v in verdicts):
        return True
    if any(v is None for v in verdicts):
        return None
    return False


def state_at(entity: dict | list, year: int, *, as_of_year: int | None = None) -> str | None:
    """Status of the entity in `year`, or None when absent/unknown (§4).

    When several intervals with different labels cover the same year (for
    example `construction` overlapping `commissioning`), the one with the
    latest known start wins, because the later phase describes the newer
    state; ties keep file order (the later row wins).  Intervals with an
    unknown start rank before every dated one.
    """
    best: tuple[tuple[int, int], str] | None = None
    for index, row in enumerate(_entity_intervals(entity)):
        if interval_covers(row, year, as_of_year=as_of_year) is not True:
            continue
        start = try_parse_date(row.get('start'))
        rank = (start.first_day().toordinal() if start else -1, index)
        if best is None or rank >= best[0]:
            best = (rank, row.get('status'))
    return best[1] if best else None


def covering_intervals(entity: dict | list, year: int, *, as_of_year: int | None = None) -> list[dict]:
    """All intervals that definitely cover `year`, in file order."""
    return [row for row in _entity_intervals(entity) if interval_covers(row, year, as_of_year=as_of_year) is True]


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
    a_lo, b_lo = a_start.first_day(), b_start.first_day()
    a_hi = a_end.last_day() if a_end else _dt.date.max
    b_hi = b_end.last_day() if b_end else _dt.date.max
    return a_lo <= b_hi and b_lo <= a_hi


def interval_years(intervals: Iterable[dict]) -> tuple[int | None, int | None]:
    """(earliest start year, latest end year) over intervals; an open end
    yields None for the upper bound.  Unknown starts are ignored."""
    lo: int | None = None
    hi: int | None = None
    open_end = False
    for row in intervals:
        if not isinstance(row, dict):
            continue
        start, end = try_parse_date(row.get('start')), try_parse_date(row.get('end'))
        if start is not None and (lo is None or start.year < lo):
            lo = start.year
        if end is None:
            if start is not None or 'end' in row:
                open_end = True
        elif hi is None or end.year > hi:
            hi = end.year
    return lo, (None if open_end else hi)


def membership_present_at(member: dict, year: int, *, formation_year: int | None, as_of: Any) -> bool | None:
    """§3.11 rule for a membership row.

    With a known `start`, the row behaves like an interval.  With
    `start: null` the member is present only for years >= the collaboration's
    formation year and <= the roster's `as_of` year (the UI labels this
    "membership history unknown"); outside that window the answer is None
    (unknown) rather than False, because the join date was not published.
    """
    if member.get('start') is not None:
        row = {'start': member.get('start'), 'end': member.get('end'), 'status': 'active'}
        return interval_covers(row, year)
    as_of_date = try_parse_date(as_of)
    upper = as_of_date.year if as_of_date else None
    end = try_parse_date(member.get('end'))
    if end is not None:
        upper = end.year if upper is None else min(upper, end.year)
    if formation_year is None or upper is None:
        return None
    if formation_year <= year <= upper:
        return True
    if year < formation_year:
        return False
    return None


# ---------------------------------------------------------------------------
# Field specifications (§3)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FieldSpec:
    """How one field of an entity is shaped.

    kind is one of:
      str, int, bool, list, dict, id, ids, enum, enums (list of enum),
      sourced (S), sourced_date, sourced_list, quantity (Q),
      quantity_map (dict name -> Q), intervals (I), coordinates (C),
      date, place, summary, links, coverage, external, external_reference,
      lineage, key_specs, membership_summary, leadership, affiliations,
      memberships, hep_graph, link_check, baselines, subsystems, volumes,
      country_list
    """

    kind: str
    required: bool = False
    enum: tuple[str, ...] | None = None
    ref_type: str | tuple[str, ...] | None = None   # for id/ids: which entity type(s)
    dimension: str | tuple[str, ...] | None = None  # for quantity: allowed dimension(s)
    nullable: bool = True
    note: str = ''


def _f(kind: str, required: bool = False, **kw: Any) -> FieldSpec:
    return FieldSpec(kind, required, **kw)


# Fields every "full" entity carries (§3 preamble).  Person, topic and source
# records have their own reduced shapes.
COMMON_FIELDS: dict[str, FieldSpec] = {
    'id': _f('str', True, nullable=False),
    'type': _f('str', True, nullable=False),
    'name': _f('str', True, nullable=False),
    'aliases': _f('list', True),
    'summary': _f('summary', True),
    'sources': _f('ids', True, ref_type='source'),
    'links': _f('links', True),
    'notes': _f('list', True),
    'coverage': _f('coverage', True),
}

ENTITY_FIELDS: dict[str, dict[str, FieldSpec]] = {
    'facility': {
        **COMMON_FIELDS,
        'kind': _f('enum', True, enum=FACILITY_KINDS),
        'operator': _f('sourced'),
        'country': _f('country_list', True),
        'primary_site_id': _f('id', True, ref_type='site'),
        'site_ids': _f('ids', True, ref_type='site'),
        'accelerator_ids': _f('ids', ref_type='accelerator'),
        'beamline_ids': _f('ids', ref_type='beamline'),
        'intervals': _f('intervals', True),
        'status': _f('enum', True, enum=STATUSES),
        'specs': _f('quantity_map'),
        'topic_ids': _f('ids', ref_type='topic'),
        'related_facility_ids': _f('ids', ref_type='facility'),
        'institution_id': _f('id', ref_type='institution'),
    },
    'site': {
        **COMMON_FIELDS,
        'facility_id': _f('id', True, ref_type='facility'),
        'coordinates': _f('coordinates', True, nullable=False),
        'setting': _f('enum', True, enum=SITE_SETTINGS),
        'depth': _f('quantity', dimension=('length', 'depth_mwe')),
        'altitude': _f('quantity', dimension='length'),
        'country': _f('str', True),
        'place': _f('place', True),
    },
    'accelerator': {
        **COMMON_FIELDS,
        'kind': _f('enum', True, enum=ACCELERATOR_KINDS),
        'facility_id': _f('id', True, ref_type='facility'),
        'site_id': _f('id', True, ref_type='site'),
        'particles': _f('list', True),
        'specs': _f('quantity_map'),
        'intervals': _f('intervals', True),
        'status': _f('enum', True, enum=STATUSES),
        'feeds_accelerator_ids': _f('ids', ref_type='accelerator'),
        'serves_experiment_ids': _f('ids', ref_type='experiment'),
        'beamline_ids': _f('ids', ref_type='beamline'),
        'document_ids': _f('ids', ref_type='document'),
    },
    'beamline': {
        **COMMON_FIELDS,
        'facility_id': _f('id', True, ref_type='facility'),
        'accelerator_id': _f('id', True, ref_type='accelerator'),
        'primary_beam': _f('sourced'),
        'target': _f('sourced'),
        'secondary_beam': _f('sourced'),
        'specs': _f('quantity_map'),
        'direction': _f('sourced'),
        'near_detector_site_ids': _f('ids', ref_type='site'),
        'far_detector_site_ids': _f('ids', ref_type='site'),
        'baselines': _f('baselines'),
        'intervals': _f('intervals', True),
        'status': _f('enum', True, enum=STATUSES),
        'document_ids': _f('ids', ref_type='document'),
    },
    'experiment': {
        **COMMON_FIELDS,
        'kind': _f('enum', True, enum=EXPERIMENT_KINDS),
        'secondary_kinds': _f('enums', enum=EXPERIMENT_KINDS),
        'collaboration_ids': _f('ids', True, ref_type='collaboration'),
        'facility_ids': _f('ids', True, ref_type='facility'),
        'site_ids': _f('ids', True, ref_type='site'),
        'detector_ids': _f('ids', True, ref_type='detector'),
        'beamline_ids': _f('ids', ref_type='beamline'),
        'accelerator_ids': _f('ids', ref_type='accelerator'),
        'topic_ids': _f('ids', True, ref_type='topic'),
        'intervals': _f('intervals', True),
        'status': _f('enum', True, enum=STATUSES),
        'physics_goals': _f('sourced_list'),
        'unique_capabilities': _f('sourced_list'),
        'energy_regime': _f('sourced'),
        'key_specs': _f('key_specs'),
        'lineage': _f('lineage'),
        'external': _f('external'),
        'document_ids': _f('ids', ref_type='document'),
        'result_ids': _f('ids', ref_type='result'),
    },
    'detector': {
        **COMMON_FIELDS,
        'experiment_ids': _f('ids', True, ref_type='experiment'),
        'facility_id': _f('id', True, ref_type='facility'),
        'site_id': _f('id', True, ref_type='site'),
        'technology': _f('sourced'),
        'technology_class': _f('enum', True, enum=TECHNOLOGY_CLASSES),
        'intervals': _f('intervals', True),
        'status': _f('enum', True, enum=STATUSES),
        'specs': _f('quantity_map'),
        'subsystems': _f('subsystems'),
        'document_ids': _f('ids', ref_type='document'),
    },
    'collaboration': {
        **COMMON_FIELDS,
        'experiment_ids': _f('ids', True, ref_type='experiment'),
        'formation': _f('sourced_date'),
        'intervals': _f('intervals', True),
        'status': _f('enum', True, enum=STATUSES),
        'membership': _f('membership_summary'),
        'leadership': _f('leadership'),
        'host_facility_id': _f('id', ref_type='facility'),
        'host_site_id': _f('id', ref_type='site'),
    },
    'institution': {
        **COMMON_FIELDS,
        'kind': _f('enum', True, enum=INSTITUTION_KINDS),
        'coordinates': _f('coordinates', True),
        'place': _f('place', True),
        'country': _f('str', True),
        'external': _f('external'),
        'facility_id': _f('id', ref_type='facility'),
    },
    'person': {
        'id': _f('str', True, nullable=False),
        'type': _f('str', True, nullable=False),
        'name': _f('str', True, nullable=False),
        'aliases': _f('list'),
        'external': _f('external', True),
        'affiliations': _f('affiliations', True),
        'memberships': _f('memberships', True),
        'topic_ids': _f('ids', ref_type='topic'),
        'hep_graph': _f('hep_graph'),
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
        'topic_ids': _f('ids', True, ref_type='topic'),
        'result_type': _f('enum', True, enum=RESULT_TYPES),
        'title': _f('str', True),
        'why_it_matters': _f('str'),
        'key_value': _f('quantity_or_sourced'),
        'significance': _f('sourced'),
        'publication': _f('external_reference'),
        'official_url': _f('sourced'),
        'hepdata': _f('str'),
    },
    'document': {
        **COMMON_FIELDS,
        'doc_type': _f('enum', True, enum=DOC_TYPES),
        'date': _f('date', True),
        'owner_ids': _f('ids', True, ref_type=tuple(sorted(DOCUMENT_OWNER_TYPES))),
        'reference': _f('external_reference', True),
        'volumes': _f('volumes'),
    },
    'topic': {
        'id': _f('str', True, nullable=False),
        'type': _f('str'),
        'name': _f('str', True, nullable=False),
        'aliases': _f('list'),
        'parent_id': _f('id', True, ref_type='topic'),
        'question': _f('str', True),
        'overview': _f('str', True),
        'observables': _f('list', True),
        'sources': _f('ids', True, ref_type='source'),
    },
    'source': {
        'id': _f('str', True, nullable=False),
        'type': _f('str', True, nullable=False),
        'source_type': _f('enum', True, enum=SOURCE_TYPES),
        'rank': _f('int', True),
        'title': _f('str', True),
        'publisher': _f('str'),
        'url': _f('str', True),
        'reference': _f('external_reference'),
        'accessed': _f('date', True),
        'date': _f('date'),
        'excerpt': _f('str'),
        'link_check': _f('link_check'),
    },
}

# Non-entity file shapes.
MEMBERSHIP_FILE_FIELDS: dict[str, FieldSpec] = {
    'collaboration_id': _f('id', True, ref_type='collaboration', nullable=False),
    'as_of': _f('date', True),
    'roster_sources': _f('ids', True, ref_type='source'),
    'default_evidence_class': _f('enum', True, enum=EVIDENCE_CLASSES),
    'members': _f('list', True),
}
MEMBERSHIP_ROW_FIELDS: dict[str, FieldSpec] = {
    'institution_id': _f('id', True, ref_type='institution', nullable=False),
    'start': _f('date', True),
    'end': _f('date', True),
    'evidence_class': _f('enum', True, enum=EVIDENCE_CLASSES),
    'sources': _f('ids', True, ref_type='source'),
    'verified_at': _f('date', True),
    'confidence': _f('enum', True, enum=CONFIDENCES),
    'note': _f('str'),
}
COVERAGE_ROW_FIELDS: dict[str, FieldSpec] = {
    'name': _f('str', True),
    'experiment_id': _f('id', True, ref_type='experiment', nullable=False),
    'category': _f('enum', True, enum=EXPERIMENT_KINDS),
    'facility': _f('str', True),
    'status': _f('enum', True, enum=STATUSES),
    'tier': _f('enum', True, enum=COVERAGE_TIERS),
    'priority': _f('int', True),
    'researched': _f('enum', True, enum=RESEARCHED_LEVELS),
    'validated': _f('bool', True),
    'globe_ready': _f('bool', True),
    'missing_fields': _f('list', True),
    'owner': _f('str', True),
    'notes': _f('str'),
}
SOURCED_VALUE_KEYS: tuple[str, ...] = ('value', 'sources', 'verified_at', 'confidence', 'note')
INTERVAL_KEYS: tuple[str, ...] = ('label', 'status', 'start', 'end', 'sources', 'verified_at', 'confidence', 'note')
COORDINATE_KEYS: tuple[str, ...] = ('lat', 'lon', 'precision_m', 'kind', 'sources', 'verified_at', 'confidence', 'note')
QUANTITY_KEYS: tuple[str, ...] = ('value', 'min', 'max', 'unit', 'dimension', 'approx', 'display',
                                  'sources', 'verified_at', 'confidence', 'note')

# Fields that hold long text and move to text.json at build time (§8).
LONG_TEXT_FIELDS: dict[str, tuple[str, ...]] = {
    'default': ('summary.technical', 'notes'),
    'experiment': ('summary.technical', 'notes', 'physics_goals', 'unique_capabilities'),
    'result': ('summary.technical', 'notes', 'why_it_matters'),
    'topic': ('overview',),
}


def required_fields(entity_type: str) -> list[str]:
    return [name for name, spec in ENTITY_FIELDS[entity_type].items() if spec.required]


def reference_fields(entity_type: str) -> dict[str, FieldSpec]:
    """Fields of kind id/ids for an entity type (used for dangling-reference checks)."""
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


def iter_reference_fields(record: Any, path: str = '') -> Iterable[tuple[str, str]]:
    """Yield (json_path, id) for every value under a key named `*_id` /
    `*_ids` (and `sources`, `roster_sources`, `roster_source_ids`), recursively.

    Used by the validator for the §9 "dangling references (any *_id/*_ids)"
    rule, independent of the per-type field tables.
    """
    if isinstance(record, dict):
        for key, value in record.items():
            here = f'{path}.{key}' if path else key
            if key.endswith('_id') and isinstance(value, str):
                yield here, value
            elif key.endswith('_ids') or key in {'sources', 'roster_sources'}:
                if isinstance(value, list):
                    for index, item in enumerate(value):
                        if isinstance(item, str):
                            yield f'{here}[{index}]', item
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


def hep_graph_url(person_id: str) -> str | None:
    """`/?source=<recid>&mode=live` for `person:inspire:` ids only (§3.9)."""
    if isinstance(person_id, str) and PERSON_INSPIRE_RE.match(person_id):
        return f'/?source={person_id.rsplit(":", 1)[1]}&mode=live'
    return None
