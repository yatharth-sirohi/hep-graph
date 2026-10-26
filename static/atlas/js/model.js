// model.js — small shared helpers used by globe/timeline/panels/modes/search
// so each of those files can stay focused on its own concern.

export const EPOCH_YEAR = 1950;

export function monthIndex(year, month = 7) {
  return (year - EPOCH_YEAR) * 12 + (month - 1);
}

export function monthToYear(month) {
  return EPOCH_YEAR + Math.floor(month / 12);
}

// Rough priority for collapsing several overlapping segments (range mode)
// into one representative status: "most alive" wins.
export const STATUS_PRIORITY = [
  'active', 'upgrade', 'commissioning', 'construction', 'approved',
  'proposed', 'completed', 'decommissioned', 'shutdown', 'unrecorded',
];

export const DIMMED_STATUSES = new Set(['proposed', 'approved', 'planned']);

export const STATUS_COLOR = {
  active: '#4fd1a5', upgrade: '#7fd1e6', commissioning: '#e6c25c',
  construction: '#e6a25c', approved: '#8a8fd6', proposed: '#8a8fd6',
  completed: '#7d8b96', decommissioned: '#5a636b', shutdown: '#5a636b',
  unrecorded: '#3d444a',
};

export function statusColor(status) {
  return STATUS_COLOR[status] || '#9aa7b0';
}

// Which of three coarse eras a lifecycle status belongs to, used to group
// an entity's related experiments into "current" / "historical" / "future"
// lists (facility and topic panels). Under construction, commissioning,
// upgrade and shutdown all count as *current* (the thing is happening now,
// even if it isn't taking data this second); only a genuinely finished
// program is historical; proposed/approved/planned things haven't started.
export const STATUS_ERA = {
  active: 'current', construction: 'current', commissioning: 'current', upgrade: 'current', shutdown: 'current',
  completed: 'historical', decommissioned: 'historical', cancelled: 'historical',
  proposed: 'future', approved: 'future', planned: 'future',
};

export function statusEra(status) {
  return STATUS_ERA[status] || 'future';
}

/** Resolves the status (+certainty) an entity's `state_segments` show at the
 * currently selected timeline position — a single year, or an inclusive
 * [lo, hi] range — instead of its static build-time `status`. Mirrors what
 * globe.js already does per marker (statusAtMonth / statusInRange), so the
 * detail panel's badge and the globe's dimming agree at every year. Returns
 * `null` when the entity has no recorded state at that selection (it hadn't
 * started yet, or it had already ended, or it carries no state_segments). */
export function statusForTimeline(segments, timelineState) {
  if (!segments || !timelineState) return null;
  if (timelineState.range) {
    const [lo, hi] = timelineState.range;
    return statusInRange(segments, monthIndex(lo, 1), monthIndex(hi, 12));
  }
  if (timelineState.year != null) {
    return statusAtMonth(segments, monthIndex(timelineState.year, 7));
  }
  return null;
}

/** When statusForTimeline() returns null, explains *why* in one of:
 * "no_history" (no state_segments at all), "not_yet" (selection is entirely
 * before the entity's first recorded segment), "ended" (entirely after its
 * last), or "gap" (falls between two segments, which the model doesn't
 * currently produce but is handled rather than mis-explained). */
export function timelineAbsenceReason(segments, timelineState) {
  if (!segments || !segments.length) return 'no_history';
  const first = segments[0][0];
  const last = segments[segments.length - 1][1];
  let lo;
  let hi;
  if (timelineState.range) {
    [lo, hi] = timelineState.range;
    lo = monthIndex(lo, 1);
    hi = monthIndex(hi, 12);
  } else {
    lo = monthIndex(timelineState.year, 7);
    hi = lo;
  }
  if (hi < first) return 'not_yet';
  if (lo > last) return 'ended';
  return 'gap';
}

/** Status (+certainty) covering a single month, or null if absent there. */
export function statusAtMonth(segments, month) {
  if (!segments) return null;
  for (const [m0, m1, status, certainty] of segments) {
    if (month >= m0 && month <= m1) return { status, certainty };
  }
  return null;
}

/** Status (+certainty) representative of a [m0, m1] range, or null if the
 * entity has no segment overlapping the range at all. */
export function statusInRange(segments, lo, hi) {
  if (!segments) return null;
  let best = null;
  let bestRank = Infinity;
  let anyPossible = false;
  for (const [m0, m1, status, certainty] of segments) {
    if (m1 < lo || m0 > hi) continue;
    if (certainty === 'possible') anyPossible = true;
    const rank = STATUS_PRIORITY.indexOf(status);
    const effectiveRank = rank === -1 ? STATUS_PRIORITY.length : rank;
    if (effectiveRank < bestRank) {
      bestRank = effectiveRank;
      best = status;
    }
  }
  if (best === null) return null;
  return { status: best, certainty: anyPossible ? 'possible' : 'certain' };
}

// facility "kind" -> a shape id (rendered as inline SVG in globe.js) and a
// colour independent of status, so shape encodes kind and colour encodes
// kind too (status modulates opacity/dimming, not hue, for facilities).
export const FACILITY_KIND_SHAPE = {
  accelerator_laboratory: { shape: 'ring', color: '#54c6ba', label: 'Accelerator laboratory' },
  underground_laboratory: { shape: 'triangle-down', color: '#c98bd6', label: 'Underground laboratory' },
  neutrino_observatory: { shape: 'hexagon', color: '#6fa8dc', label: 'Neutrino observatory' },
  astroparticle_observatory: { shape: 'diamond', color: '#d68b6f', label: 'Astroparticle observatory' },
  polar_station: { shape: 'snowflake', color: '#bfe6f2', label: 'Polar station' },
  reactor_site: { shape: 'square', color: '#e0c25c', label: 'Reactor site' },
  research_laboratory: { shape: 'flask', color: '#d98bb2', label: 'Research laboratory' },
  spallation_source: { shape: 'starburst', color: '#ffa65c', label: 'Spallation source' },
};

export function facilityShape(kind) {
  return FACILITY_KIND_SHAPE[kind] || { shape: 'circle', color: '#9aa7b0', label: kind || 'Facility' };
}

export function idKind(id) {
  return id.split(':')[0];
}

export function idSlug(id) {
  return id.split(/:(.+)/)[1];
}

export function titleCase(s) {
  return (s || '').replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

// Display labels for the schema's `kind` / `technology_class` enums
// (hepgraph/atlas/schema.py FACILITY_KINDS, EXPERIMENT_KINDS, ACCELERATOR_KINDS,
// TECHNOLOGY_CLASSES). The ids stay the slugs the data uses — this is only
// what a person reads. titleCase() turns "cevns" into "Cevns" and "lar_tpc"
// into "Lar Tpc", so any slug whose natural spelling is not plain Title Case
// is listed here; the rest fall through to titleCase().
export const KIND_LABELS = {
  // experiment kinds
  cevns: 'CEvNS',
  long_lived_particle: 'Long-Lived Particle (LLP)',
  gamma_ray: 'Gamma-Ray',
  // technology classes
  lar_tpc: 'Liquid-Argon TPC',
  xenon_tpc: 'Liquid-Xenon TPC',
  argon_tpc: 'Liquid-Argon TPC',
  noble_liquid_tpc: 'Noble-Liquid TPC',
  gaseous_tpc: 'Gaseous TPC',
  imaging_atmospheric_cherenkov: 'Imaging Atmospheric Cherenkov (IACT)',
  skipper_ccd: 'Skipper CCD',
  light_shining_through_wall: 'Light-Shining-Through-Wall',
  lumped_element_resonator: 'Lumped-Element Resonator',
};

/** Human label for a facility/experiment/accelerator kind or a detector
 * technology class: the explicit KIND_LABELS entry if there is one, else
 * titleCase(). */
export function kindLabel(value) {
  if (value == null || value === '') return '';
  return KIND_LABELS[value] || titleCase(value);
}

/** The globe markers that stand for a research topic: the facilities and sites
 * of the experiments that carry it in `topic_ids` — exactly the experiments the
 * topic panel lists. (A topic record carries no experiment list of its own; the
 * link is stored on the experiment.) Returns an empty set for a topic nothing
 * in the Atlas is tagged with, which callers must treat as "nothing to
 * highlight" rather than "mute the whole globe". */
export function topicMarkerIds(atlas, topicId) {
  const ids = new Set();
  const facilities = atlas.facilities || {};
  const sites = atlas.sites || {};
  for (const experiment of Object.values(atlas.experiments || {})) {
    if (!(experiment.topic_ids || []).includes(topicId)) continue;
    for (const facilityId of experiment.facility_ids || []) {
      if (facilities[facilityId]) ids.add(facilityId);
    }
    for (const siteId of experiment.site_ids || []) {
      const site = sites[siteId];
      if (!site) continue;
      ids.add(siteId);
      if (site.facility_id && facilities[site.facility_id]) ids.add(site.facility_id);
    }
  }
  return ids;
}

/** A flat entity index over atlas.json, so any id can be resolved to its
 * record and coarse "kind" in O(1). */
export function buildIndex(atlas) {
  const index = new Map();
  for (const group of ['facilities', 'sites', 'accelerators', 'beamlines',
    'experiments', 'detectors', 'collaborations', 'topics']) {
    for (const [id, record] of Object.entries(atlas[group] || {})) {
      index.set(id, record);
    }
  }
  return index;
}

// A date is a plain string ("2012-07-04") or a structured value
// `{date, approx, planned, earliest, latest, display}` (an interval end that is
// only known roughly). A structured value reads as its own `display` wording
// when the record has one ("end of 2014"); otherwise as the date, with "c."
// for an approximate one and the bounds it carries ("2028 (between 2027 and
// 2028)"). An object is never printed as "[object Object]".
export function fmtDate(d) {
  if (!d) return '';
  if (typeof d === 'string') return d;
  if (typeof d === 'object') {
    if (d.display) return String(d.display);
    if (!d.date) return '';
    const base = `${d.approx ? 'c. ' : ''}${d.date}`;
    const { earliest, latest } = d;
    if (earliest && latest && earliest !== latest) return `${base} (between ${earliest} and ${latest})`;
    if (earliest && earliest !== d.date) return `${base} (no earlier than ${earliest})`;
    if (latest && latest !== d.date) return `${base} (no later than ${latest})`;
    return base;
  }
  return String(d);
}

// "2009–present" for an interval whose ends are strings or structured dates. An
// open end reads "present", except after a planned start (a detector not yet
// built is not "present"), which reads "planned from <start>". An end the record
// words itself ("end of 2014", "summer of 2022") is a phrase, not a year, so a
// range reads "since end of 2014" / "from X to Y" instead of a dash between
// phrases. Empty when neither end is recorded.
export function fmtInterval(start, end) {
  const from = fmtDate(start);
  const to = fmtDate(end);
  if (!from && !to) return '';
  const phrased = (d) => !!d && typeof d === 'object' && !!d.display;
  if (from && !to) {
    if (start && typeof start === 'object' && start.planned) return `planned from ${from}`;
    return phrased(start) ? `since ${from}` : `${from}\u2013present`;
  }
  if (!from) return phrased(end) ? `until ${to}` : `?\u2013${to}`;
  return phrased(start) || phrased(end) ? `from ${from} to ${to}` : `${from}\u2013${to}`;
}

export function quantityText(q) {
  if (q == null) return '';
  if (typeof q === 'object') {
    if (q.display) return q.display;
    if (q.min != null || q.max != null) return `${q.min ?? '?'}–${q.max ?? '?'} ${q.unit || ''}`.trim();
    return `${q.value ?? ''} ${q.unit || ''}`.trim();
  }
  return String(q);
}
