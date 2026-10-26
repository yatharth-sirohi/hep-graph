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
//   * Operating energy beats the headline value. A record's `specs` hold its headline energy (often
//     the design value); `intervals[].specs` hold what a run actually delivered (A3: "values that change
//     per run"). Where an active interval carries its own value of the field, the latest such interval
//     gives the plotted energy and the headline value is footnoted if it differs.
//   * Year: the start of the first interval whose status is `active` (the machine began operating),
//     read from the date as recorded: a planned date is not a start.
//   * No sourced energy, or no start of operation: not plotted, and listed with the reason.

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
  return `${Number((gev * 1000).toPrecision(3))} MeV`;
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

/** What one accelerator is drawn as, or why it is not: `{ plotted: row }` or `{ skipped: { id, accelerator, reason } }`. */
export function frontierEntry(accelerator) {
  const field = FIELD_OF(accelerator);
  const intervals = accelerator.intervals || [];
  const reasons = [];

  // ---- the energy
  const headline = (accelerator.specs || {})[field] || null;
  const headlineGeV = energyGeV(headline);
  const own = intervals
    .map((interval, index) => ({ interval, index, quantity: (interval.specs || {})[field] || null }))
    .filter(({ interval, quantity }) => interval.status === 'active' && energyGeV(quantity) != null);
  const start = (entry) => {
    const date = parseDate(entry.interval.start);
    return date ? dateKey(date) : -Infinity;
  };
  own.sort((a, b) => (start(a) - start(b)) || (a.index - b.index));
  const operating = own.length ? own[own.length - 1] : null;
  let energy = null;
  if (operating) {
    energy = {
      quantity: operating.quantity, gev: energyGeV(operating.quantity), kind: 'interval', index: operating.index,
      pointer: `/intervals/${operating.index}/specs/${field}`, label: operating.interval.label || 'operating interval',
    };
  } else if (headlineGeV != null) {
    energy = { quantity: headline, gev: headlineGeV, kind: 'specs', index: null, pointer: `/specs/${field}`, label: 'the record’s stated value' };
  } else if (accelerator.is_collider) {
    const beam = (accelerator.specs || {}).beam_energy;
    reasons.push(beam
      ? `A collider with no sourced centre-of-mass energy (√s). It records a beam energy (${quantityText(beam)}), but the chart draws a collider at √s and does not derive one.`
      : 'A collider with no sourced centre-of-mass energy (√s) and no beam energy.');
  } else {
    reasons.push('No sourced beam energy.');
  }

  // ---- the start of operation
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

  if (reasons.length) return { skipped: { id: accelerator.id, accelerator, reason: reasons.join(' ') } };

  // ---- the footnote: the headline value, when the operating one replaced a different one
  let other = null;
  if (operating && headline && headlineGeV != null && Math.abs(headlineGeV - energy.gev) > 1e-9 * energy.gev) {
    other = { quantity: headline, gev: headlineGeV, pointer: `/specs/${field}` };
  }
  // ---- the energies the record gives for its own runs, in order
  const history = own.map(({ interval, index, quantity }) => ({
    label: interval.label || 'run', year: (parseDate(interval.start) || {}).year || null, quantity, gev: energyGeV(quantity), index,
  }));

  const families = (accelerator.particles || []).map(particleFamily);
  const family = families[0] || 'other';
  return {
    plotted: {
      id: accelerator.id,
      slug: accelerator.id.split(':')[1],
      accelerator,
      name: accelerator.name,
      label: shortName(accelerator),
      collider: !!accelerator.is_collider,
      field,
      energy,
      other,
      history,
      start: {
        year: first.date.year, month: first.date.month, approx: first.date.approx, index: first.index,
        label: first.interval.label || '', pointer: `/intervals/${first.index}`,
      },
      family,
      particles: accelerator.particles || [],
    },
  };
}

/** `{ rows, skipped }`: every accelerator, either plotted (in order of start, then energy) or listed with the reason. */
export function frontierData(atlas) {
  const rows = [];
  const skipped = [];
  for (const accelerator of Object.values(atlas.accelerators || {})) {
    const entry = frontierEntry(accelerator);
    if (entry.plotted) rows.push(entry.plotted);
    else skipped.push(entry.skipped);
  }
  rows.sort((a, b) => (a.start.year - b.start.year) || (a.energy.gev - b.energy.gev) || (a.id < b.id ? -1 : 1));
  skipped.sort((a, b) => (a.id < b.id ? -1 : 1));
  return { rows, skipped };
}

export function frontierRows(atlas) {
  return frontierData(atlas).rows;
}

/** The row, or the reason, for one accelerator id (the panel's link). */
export function frontierFor(atlas, acceleratorId) {
  const accelerator = (atlas.accelerators || {})[acceleratorId];
  return accelerator ? frontierEntry(accelerator) : null;
}

/** True when the machine had started operating by the selected timeline position: a year, or a range (its last year). */
export function startedBy(row, timelineState) {
  if (!timelineState) return true;
  if (timelineState.range) return row.start.year <= timelineState.range[1];
  if (timelineState.year != null) return row.start.year <= timelineState.year;
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
