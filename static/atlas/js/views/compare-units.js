// compare-units.js — reading values across experiments in one unit.
//
// Pure (no DOM, no fetch), so the Compare view and its unit check can both run it.
//
// A row of the comparison table that shares a unit dimension (the baselines, the
// masses, the depths, the energies) is shown in ONE unit, so the eye can read across
// it: 1285 km, 295 km and 52.5 km, not "1285 km", "295,000 m" and "52.5 km". The
// rules are deliberately narrow, because a conversion must never change what a source
// said:
//
//   * only metric prefixes of the same dimension are converted (m, km; g, kg, t, kt;
//     eV ... TeV), by exact powers of ten;
//   * only a value whose recorded wording is ONE figure and ONE unit ("17.5 kt",
//     "at least 10 kt", "~295 km") is converted. "260 kt total, 188 kt fiducial" or
//     "700 m granite overburden" has more in it than the number, so it is shown
//     exactly as recorded and says so;
//   * the recorded wording always survives: the reader sees it in a tooltip, and the
//     CSV carries it beside the converted figure.

/** Unit ladders, smallest to largest: [unit, size of one unit in the dimension's base unit]. */
export const LADDERS = {
  length: [['cm', 0.01], ['m', 1], ['km', 1000]],
  mass: [['g', 0.001], ['kg', 1], ['t', 1000], ['kt', 1e6]],
  energy: [['eV', 1], ['keV', 1e3], ['MeV', 1e6], ['GeV', 1e9], ['TeV', 1e12]],
};

function ladderFor(dimension) {
  return LADDERS[dimension] || null;
}

function sizeOf(dimension, unit) {
  const ladder = ladderFor(dimension);
  if (!ladder) return null;
  const rung = ladder.find(([name]) => name === unit);
  return rung ? rung[1] : null;
}

/** Whether a value in `unit` of `dimension` can be converted at all. */
export function isConvertible(dimension, unit) {
  return sizeOf(dimension, unit) != null;
}

/** `value` of `from` expressed in `to`, both units of `dimension`; null if either is unknown. */
export function convert(value, dimension, from, to) {
  const a = sizeOf(dimension, from);
  const b = sizeOf(dimension, to);
  if (a == null || b == null || typeof value !== 'number' || !Number.isFinite(value)) return null;
  // Round away the binary noise a power-of-ten factor leaves (7 t in kt is 0.007, not 0.007000000000000001).
  return Number((value * (a / b)).toPrecision(12));
}

/** A number as a person reads it: separators, no more than six significant figures. */
export function formatNumber(value) {
  if (typeof value !== 'number' || !Number.isFinite(value)) return String(value);
  const rounded = Number(value.toPrecision(6));
  return rounded.toLocaleString('en-US', { maximumFractionDigits: 8 });
}

/**
 * The unit a set of values is shown in: the largest rung on the ladder at which no
 * value reads below 1 (so 1285, 295 and 52.5 km stay in km, 650 m beside 1.5 km goes to
 * m, and 300 g beside 3.7 t reads in g). `cap` names the largest unit the row may use: depths are
 * read in metres, not 0.65 km. `values` are [{ value, unit }] of one dimension; null when the
 * dimension has no ladder or nothing is convertible.
 */
export function chooseUnit(dimension, values, cap = null) {
  const full = ladderFor(dimension);
  const capped = full && cap ? full.findIndex(([name]) => name === cap) : -1;
  const ladder = capped >= 0 ? full.slice(0, capped + 1) : full;
  const usable = values.filter((v) => sizeOf(dimension, v.unit) != null && v.value !== 0);
  if (!ladder || !usable.length) return null;
  const smallest = Math.min(...usable.map((v) => Math.abs(v.value) * sizeOf(dimension, v.unit)));
  let chosen = ladder[0][0];
  for (const [name, size] of ladder) {
    if (smallest / size >= 1) chosen = name;
  }
  return chosen;
}

const PREFIXES = '(?:(?:at least|about|around|approximately|up to|over|under|roughly|more than|less than)\\s+|[~≈<>≤≥]\\s*)';
const SIMPLE = new RegExp(`^(${PREFIXES})?(\\d[\\d,]*(?:\\.\\d+)?)\\s*([^\\s\\d,;()]+)$`, 'i');

/**
 * `{ prefix, number, unit }` when the record's own wording of a quantity is exactly one
 * figure and one unit (optionally led by "~", "at least", ...) and agrees with the
 * record's numeric `value` and `unit`; otherwise null. The check against `value` and
 * `unit` is what makes it safe: a display that says something else is never "converted".
 */
export function parseSimpleDisplay(quantity) {
  if (!quantity || typeof quantity.display !== 'string') return null;
  const match = SIMPLE.exec(quantity.display.trim());
  if (!match) return null;
  const number = Number(match[2].replace(/,/g, ''));
  if (!Number.isFinite(number) || number !== quantity.value || match[3] !== quantity.unit) return null;
  return { prefix: (match[1] || '').trim(), number, unit: match[3] };
}

/** "at least 10 kt", "~295 km", "17,500 t": the prefix, the figure, the unit. */
export function composeText(prefix, number, unit) {
  const lead = prefix ? (/^[~≈<>≤≥]$/.test(prefix) ? prefix : `${prefix} `) : '';
  return `${lead}${formatNumber(number)} ${unit}`;
}
