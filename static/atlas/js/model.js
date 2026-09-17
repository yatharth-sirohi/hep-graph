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

export function fmtDate(d) {
  if (!d) return '';
  if (typeof d === 'string') return d;
  if (typeof d === 'object') return d.display || d.date || '';
  return String(d);
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
