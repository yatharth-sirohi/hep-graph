// frontier-rows.js — which accelerators "The energy frontier" can draw, at what energy and from
// what year, and which it cannot (with the reason). Pure data and arithmetic over atlas.json (no
// DOM, no fetch), so panels.js and the search can use it without loading the view, and a unit
// check can run it under Node.
//
//   #/view/energy-frontier       energy (log) against the start of operation, one point per accelerator
//
// THE RULES (the view's "Inputs and method" states them again, in words):
//   * Energy field: a collider is drawn at √s (`specs.cms_energy`), every other machine (a fixed-target
//     accelerator, a synchrotron, an injector, a booster) at its beam energy (`specs.beam_energy`).
//     The two are different quantities, so a collider is a filled marker and the rest are hollow.
//   * A machine is a TRACK of points, one per era the record gives an energy for. An era is an interval
//     of status `active` (a `run`, a `phase`, or a plain interval) whose own `specs` carry the field
//     (A3, A30: "earlier eras live in intervals with their own specs"). Its point stands at the start
//     year of that interval. The points of a track are joined by a thin line in the machine's colour.
//   * Where no era carries an energy, the record's headline `specs` value is drawn once, at the year
//     the machine began operating, as an "as recorded today" point (a dashed ring): the Atlas dates no
//     energy to the start, and the chart says so rather than let a machine look as if it began at its
//     final energy. The same point is added in front of a track whose first era starts after the first
//     operation (RHIC: first collisions 2000, an energy recorded for 2021 only).
//   * Where eras exist and the headline value is not one of them (the LHC's 14 TeV design value, CEBAF's
//     12 GeV), the headline value is footnoted, not drawn: nothing dates it.
//   * No sourced energy, or no start of operation: not plotted, and listed with the reason.
//   * A machine's first operation is the start of its first interval of status `active`; a planned
//     date is not a start.

import { quantityText } from '../model.js';

export const VIEW_NAME = 'energy-frontier';
// The owner names features; this is the working title, and the only place it is written.
export const WORKING_TITLE = 'The energy frontier';

/**
 * Conversion of a recorded energy to eV, the base unit.
 *
 * COPIED from hepgraph/atlas/schema.py UNIT_SCALE['energy']: the bundle keeps each value in the unit
 * its source uses, and the chart draws in GeV. tests/test_atlas_charts.py fails if this table and the
 * schema drift.
 */
export const ENERGY_SCALE_EV = Object.freeze({
  eV: 1, meV: 1e-3, 'µeV': 1e-6, keV: 1e3, MeV: 1e6, GeV: 1e9, TeV: 1e12, PeV: 1e15, EeV: 1e18,
});

/** A recorded energy in GeV (a single number only: a range has no one value to plot), or null. */
export function energyGeV(quantity) {
  if (!quantity || typeof quantity.value !== 'number' || !Number.isFinite(quantity.value) || !(quantity.value > 0)) return null;
  const scale = ENERGY_SCALE_EV[quantity.unit];
  return scale === undefined ? null : (quantity.value * scale) / 1e9;
}

/** An energy in the units a physicist writes it: "450 GeV", "13.6 TeV", "400 MeV". */
export function energyText(gev) {
  if (gev >= 1000) return `${Number((gev / 1000).toPrecision(3))} TeV`;
  if (gev >= 1) return `${Number(gev.toPrecision(3))} GeV`;
  if (gev >= 1e-3) return `${Number((gev * 1000).toPrecision(3))} MeV`;
  return `${Number((gev * 1e6).toPrecision(3))} keV`;
}

// ---- dates ----------------------------------------------------------------------
/** `{ year, month, approx, planned }` from a date as recorded (a string, or `{ date, approx, planned, ... }`), or null. */
export function parseDate(date) {
  if (date == null) return null;
  const text = typeof date === 'string' ? date : date.date;
  const match = /^(\d{4})(?:-(\d{2}))?/.exec(String(text || ''));
  if (!match) return null;
  return {
    year: Number(match[1]),
    month: match[2] ? Number(match[2]) : 1,
    approx: typeof date === 'object' ? !!date.approx : false,
    planned: typeof date === 'object' ? !!date.planned : false,
  };
}

const dateKey = (d) => d.year * 12 + (d.month - 1);

// ---- particles -------------------------------------------------------------------
/** The family of one particle name, for the colour: electrons and positrons, protons (also antiprotons and
 * H⁻, which is stripped to protons), ions (also deuterons and alphas), or other. */
export function particleFamily(particle) {
  const text = String(particle || '').toLowerCase();
  if (/electron|positron/.test(text)) return 'lepton';
  if (/^h[-−⁻]/.test(text) || /proton/.test(text)) return 'hadron';
  if (/\bion\b|deuteron|alpha|nucleus|nuclei/.test(text)) return 'ion';
  return 'other';
}

/** The chart's marker for a family: the tone (a colour token, views.css) and a shape, so colour is never the only cue. */
export const FAMILIES = Object.freeze({
  hadron: { label: 'Protons and antiprotons', tone: 'hadron', shape: 'circle' },
  lepton: { label: 'Electrons and positrons', tone: 'lepton', shape: 'diamond' },
  ion: { label: 'Heavy ions', tone: 'ion', shape: 'square' },
  other: { label: 'Other', tone: 'other', shape: 'triangle' },
});

// ---- names ------------------------------------------------------------------------
function stripParen(text) {
  return String(text || '').replace(/\s*\([^)]*\)/g, '').trim();
}

/** The shortest of a record's name and aliases that is at least three characters ("LHC", "Tevatron", "FNAL Booster"). */
export function shortName(record) {
  const all = [record.name, ...(record.aliases || [])].map(stripParen).filter((t) => t.length >= 3);
  all.sort((a, b) => a.length - b.length);
  return all[0] || stripParen(record.name);
}

// ---- rows -------------------------------------------------------------------------
const FIELD_OF = (accelerator) => (accelerator.is_collider ? 'cms_energy' : 'beam_energy');

const STATUS_WORD = {
  construction: 'construction', commissioning: 'commissioning', approved: 'approved', proposed: 'proposed',
  planned: 'planned', shutdown: 'shutdown', upgrade: 'upgrade', completed: 'completed', decommissioned: 'decommissioned',
};

function statusSummary(intervals) {
  const seen = [];
  for (const interval of intervals) {
    const word = STATUS_WORD[interval.status] || interval.status;
    if (word && !seen.includes(word)) seen.push(word);
  }
  return seen.join(', ');
}

/** The footnote on a point whose energy no era dates: the Atlas holds the machine's energy today, not the one it started with. */
export const AS_RECORDED_TODAY = 'Energy as recorded today; the starting energy is not in the Atlas.';

/** What one accelerator is drawn as, or why it is not: `{ plotted: machine }` or `{ skipped: { id, accelerator, reason } }`. A
 * machine is `{ id, slug, accelerator, name, label, collider, field, family, particles, first, points, other }`; a point is
 * `{ id, index, year, month, approx, gev, quantity, kind: 'era' | 'today', label, pointer }`. */
export function frontierEntry(accelerator) {
  const field = FIELD_OF(accelerator);
  const intervals = accelerator.intervals || [];
  const reasons = [];

  // ---- the first operation
  const active = intervals
    .map((interval, index) => ({ interval, index, date: parseDate(interval.start) }))
    .filter(({ interval, date }) => interval.status === 'active' && date && !date.planned);
  active.sort((a, b) => (dateKey(a.date) - dateKey(b.date)) || (a.index - b.index));
  const first = active[0] || null;
  if (!first) {
    const hasActive = intervals.some((interval) => interval.status === 'active');
    reasons.push(hasActive
      ? 'No dated start of operation: its operating interval has no start date, or only a planned one.'
      : `Not yet operating: its recorded intervals are ${statusSummary(intervals) || 'absent'}, none of them active, so it has no start of operation.`);
  }

  // ---- the eras that carry an energy of their own, in order
  const headline = (accelerator.specs || {})[field] || null;
  const headlineGeV = energyGeV(headline);
  const eras = active
    .map(({ interval, index, date }) => ({ interval, index, date, quantity: (interval.specs || {})[field] || null }))
    .filter(({ quantity }) => energyGeV(quantity) != null);

  const points = eras.map(({ interval, index, date, quantity }, n) => ({
    index: n, year: date.year, month: date.month, approx: date.approx, gev: energyGeV(quantity), quantity, kind: 'era',
    label: interval.label || 'era', pointer: `/intervals/${index}/specs/${field}`, startPointer: `/intervals/${index}`,
  }));

  if (!points.length && headlineGeV == null) {
    if (accelerator.is_collider) {
      const beam = (accelerator.specs || {}).beam_energy;
      reasons.push(beam
        ? `A collider with no sourced centre-of-mass energy (\u221as). It records a beam energy (${quantityText(beam)}), but the chart draws a collider at \u221as and does not derive one.`
        : 'A collider with no sourced centre-of-mass energy (\u221as) and no beam energy.');
    } else {
      reasons.push('No sourced beam energy.');
    }
  }
  if (reasons.length) return { skipped: { id: accelerator.id, accelerator, reason: reasons.join(' ') } };

  // ---- the point for the first operation, when no era dates an energy to it
  let other = null;
  if (headlineGeV != null && (!points.length || points[0].year > first.date.year)) {
    points.unshift({
      index: 0, year: first.date.year, month: first.date.month, approx: first.date.approx, gev: headlineGeV, quantity: headline,
      kind: 'today', label: first.interval.label || 'first operation', pointer: `/specs/${field}`, startPointer: `/intervals/${first.index}`,
    });
    points.forEach((point, n) => { point.index = n; });
  } else if (headlineGeV != null && !points.some((point) => Math.abs(point.gev - headlineGeV) <= 1e-9 * headlineGeV)) {
    other = { quantity: headline, gev: headlineGeV, pointer: `/specs/${field}` };
  }
  for (const point of points) point.id = `${accelerator.id}#${point.index}`;

  const families = (accelerator.particles || []).map(particleFamily);
  return {
    plotted: {
      id: accelerator.id,
      slug: accelerator.id.split(':')[1],
      accelerator,
      name: accelerator.name,
      label: shortName(accelerator),
      collider: !!accelerator.is_collider,
      field,
      points,
      other,
      first: {
        year: first.date.year, month: first.date.month, approx: first.date.approx, index: first.index,
        label: first.interval.label || '', pointer: `/intervals/${first.index}`,
      },
      family: families[0] || 'other',
      particles: accelerator.particles || [],
    },
  };
}

/** `{ rows, skipped, points }`: every accelerator, either plotted (a machine with its points, in order of first operation) or listed with the reason. */
export function frontierData(atlas) {
  const rows = [];
  const skipped = [];
  for (const accelerator of Object.values(atlas.accelerators || {})) {
    const entry = frontierEntry(accelerator);
    if (entry.plotted) rows.push(entry.plotted);
    else skipped.push(entry.skipped);
  }
  rows.sort((a, b) => (a.first.year - b.first.year) || (a.points[0].gev - b.points[0].gev) || (a.id < b.id ? -1 : 1));
  skipped.sort((a, b) => (a.id < b.id ? -1 : 1));
  return { rows, skipped, points: rows.flatMap((row) => row.points.map((point) => ({ ...point, machine: row }))) };
}

export function frontierRows(atlas) {
  return frontierData(atlas).rows;
}

/** The row, or the reason, for one accelerator id (the panel's link). */
export function frontierFor(atlas, acceleratorId) {
  const accelerator = (atlas.accelerators || {})[acceleratorId];
  return accelerator ? frontierEntry(accelerator) : null;
}

/** True when a point's year is not after the selected timeline position: a year, or a range (its last year). A machine's
 * first point is the year it began operating, so this is also whether the machine had started. */
export function startedBy(point, timelineState) {
  if (!timelineState) return true;
  if (timelineState.range) return point.year <= timelineState.range[1];
  if (timelineState.year != null) return point.year <= timelineState.year;
  return true;
}

export function viewHash() {
  return `#/view/${VIEW_NAME}`;
}

// ---- search -------------------------------------------------------------------------
/** Search entries for the Atlas search box. Nothing when no accelerator can be drawn. */
export function frontierSearchEntries(atlas) {
  const rows = frontierRows(atlas);
  if (!rows.length) return [];
  return [{
    type: 'view',
    id: `view:${VIEW_NAME}`,
    name: WORKING_TITLE,
    aliases: [
      // The title without its article, so "energy frontier" matches exactly (and, with `view` first in the
      // search's type order, leads here and not to the topic of the same name).
      'energy frontier',
      'Livingston chart',
      'Livingston plot',
      'accelerator energy against year',
      'collider energy over time',
      'centre-of-mass energy',
      'beam energy',
      'accelerator energy history',
    ],
    subtitle: `Chart · energy against year, ${rows.length} accelerators`,
  }];
}
