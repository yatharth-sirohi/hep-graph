// compare-rows.js — what "Compare experiments" puts in its table, and its CSV. Pure
// data and arithmetic over atlas.json, the results bundle and (once loaded)
// provenance.json and sources.json: no DOM, no fetch, so the view and the unit check
// both run it. The route and the search entry are compare-route.js.
//
// A TABLE is rows x experiments. Every cell is a list of LINES, and a line is one
// sourced statement: its label (the key specification's own label, so "Detector mass"
// is never read as a target mass), its text, the claims in provenance.json that back it
// (so each carries a source marker), and, where it was converted to the row's common
// unit, the wording the record used. Nothing is computed from other numbers and nothing
// is filled in: a cell with no line reads "not recorded".

import {
  fmtDate, idSlug, kindLabel, quantityText, statusForTimeline, timelineAbsenceReason, titleCase,
} from '../model.js';
import { buildCsv } from '../research/files.js';
import { rowsForExperiment, shortPlaceName } from './beam-rows.js';
import {
  chooseUnit, composeText, convert, formatNumber, isConvertible, parseSimpleDisplay,
} from './compare-units.js';

export const NOT_RECORDED = 'not recorded';
/** A row that does not apply to an experiment's kind: a dark-matter detector has no baseline. Unlike
 * "not recorded" (the Atlas holds no value), this says there is nothing to record. */
export const NOT_APPLICABLE = 'not applicable';

/** The kinds of experiment a baseline (the distance from a beam's source, or from a reactor, to the
 * detector) is a quantity of. Any other kind with no baseline recorded reads "not applicable"; one of
 * these with none reads "not recorded". A baseline that a record does carry is always shown. */
export const BASELINE_KINDS = new Set(['accelerator_neutrino', 'reactor_neutrino']);

// ---- names -------------------------------------------------------------------------
/** A heading for a column: the name, or its shortest alias when the name is long. */
export function shortExperimentName(record) {
  const name = record.name || record.id;
  if (name.length <= 24) return name;
  const aliases = (record.aliases || []).filter((a) => a.length >= 3 && a.length < name.length && !/[/(]/.test(a));
  aliases.sort((a, b) => a.length - b.length);
  return aliases[0] || name;
}

// ---- lines -------------------------------------------------------------------------
function makeLine(text, extra = {}) {
  return {
    label: null, text, suffix: '', original: null, note: null, route: null, indent: 0, kind: null,
    claims: [], fallback: [], sourceIds: [], firstOnly: false, derived: false,
    ...extra,
  };
}

const claim = (id, pointer) => ({ id, pointer });

function usableQuantity(quantity) {
  return !!quantity && typeof quantity === 'object' && typeof quantity.display === 'string';
}

/** "Status in 2026" or "Status in 2015–2020", from the selected timeline position. */
export function whenText(timelineState) {
  if (timelineState && timelineState.range) return `${timelineState.range[0]}–${timelineState.range[1]}`;
  return timelineState && timelineState.year != null ? String(timelineState.year) : '';
}

function statusLines(exp, ctx) {
  const resolved = statusForTimeline(exp.state_segments, ctx.timelineState);
  if (resolved) {
    const text = titleCase(resolved.status) + (resolved.certainty === 'possible' ? ' (uncertain)' : '');
    // The status is read from dated intervals, so the sources are those of the intervals in that state.
    const claims = (exp.intervals || [])
      .map((interval, index) => (interval.status === resolved.status ? claim(exp.id, `/intervals/${index}`) : null))
      .filter(Boolean);
    return [makeLine(text, {
      claims, fallback: [claim(exp.id, '/sources')], kind: resolved.status,
      note: 'Read from the dated intervals under “Dates” at the selected position on the timeline.',
    })];
  }
  const when = whenText(ctx.timelineState);
  const reason = timelineAbsenceReason(exp.state_segments, ctx.timelineState || {});
  const text = {
    not_yet: `Not yet proposed in ${when}`,
    ended: `No longer active in ${when}`,
    gap: `No recorded status in ${when}`,
  }[reason];
  return text ? [makeLine(text, { derived: true })] : [];
}

/** "2017-07-21 – 2024-02", "from 2015-04", "planned: 2028 (between 2027 and 2028)". */
export function intervalRange(start, end) {
  const from = fmtDate(start);
  const to = fmtDate(end);
  if (from && to) return `${from} – ${to}`;
  if (from) return start && typeof start === 'object' && start.planned ? `planned: ${from}` : `from ${from}`;
  return to ? `until ${to}` : '';
}

function dateLines(exp) {
  return (exp.intervals || []).map((interval, index) => {
    const range = intervalRange(interval.start, interval.end);
    const status = titleCase(interval.status);
    const label = interval.label && interval.label.toLowerCase() !== String(interval.status).toLowerCase()
      ? ` — ${interval.label}` : '';
    return makeLine(`${range ? `${range} · ` : ''}${status}${label}`, {
      claims: [claim(exp.id, `/intervals/${index}`)], fallback: [claim(exp.id, '/sources')],
    });
  });
}

const ROLE_WORDS = { beam_source: 'beam source', detector_host: 'detector host', prototype_host: 'prototype host' };
const roleWord = (role) => ROLE_WORDS[role] || String(role || '').replace(/_/g, ' ');

function hostLines(exp, ctx) {
  const { atlas } = ctx;
  const lines = [];
  const facilities = [];
  const roles = exp.facility_roles || [];
  roles.forEach((entry, index) => {
    let item = facilities.find((f) => f.id === entry.facility_id);
    if (!item) {
      item = { id: entry.facility_id, roles: [], pointers: [] };
      facilities.push(item);
    }
    item.roles.push(roleWord(entry.role));
    item.pointers.push(`/facility_roles/${index}`);
  });
  if (!facilities.length) {
    for (const id of exp.facility_ids || []) facilities.push({ id, roles: [], pointers: [] });
  }
  const sites = (exp.site_ids || []).map((id) => (atlas.sites || {})[id]).filter(Boolean);
  const placed = new Set();
  const siteLine = (site) => makeLine(site.name, {
    route: { type: 'site', slug: idSlug(site.id) }, indent: 1, kind: 'site',
    claims: [claim(site.id, '/coordinates')], fallback: [claim(site.id, '/sources')],
  });
  for (const item of facilities) {
    const facility = (atlas.facilities || {})[item.id];
    const name = facility ? facility.name : item.id;
    lines.push(makeLine(name, {
      suffix: item.roles.length ? ` · ${[...new Set(item.roles)].join(', ')}` : '',
      route: facility ? { type: 'facility', slug: idSlug(item.id) } : null, kind: 'facility',
      claims: item.pointers.map((pointer) => claim(exp.id, pointer)), fallback: [claim(exp.id, '/sources')],
    }));
    for (const site of sites) {
      if (site.facility_id === item.id) {
        lines.push(siteLine(site));
        placed.add(site.id);
      }
    }
  }
  for (const site of sites) if (!placed.has(site.id)) lines.push(siteLine(site));
  return lines;
}

// ---- rows that carry a quantity ----------------------------------------------------
// Each experiment contributes "candidates" (a label, the recorded quantity and its
// claims); the row then picks one unit per dimension and turns them into lines.

const DEPTH_LABEL = /\b(depth|overburden)\b/i;
const BASELINE_LABEL = /baseline|distance from|far-hall|near-hall/i;
const MASS_EXCLUDED = /magnet|solenoid|dipole|equipment/i;
const ENERGY_EXCLUDED = /resolution|threshold|q-value|mass range|axion/i;
const SIZE_LABEL = /collaboration size|participating institut/i;

function specCandidates(exp, test) {
  const out = [];
  (exp.key_specs || []).forEach((spec, index) => {
    if (!usableQuantity(spec.quantity) || !test(spec, spec.quantity)) return;
    out.push({
      label: spec.label, quantity: spec.quantity,
      claims: [claim(exp.id, `/key_specs/${index}/quantity`)], fallback: [claim(exp.id, '/sources')],
    });
  });
  return out;
}

function depthCandidates(exp, ctx) {
  const out = specCandidates(exp, (spec, q) => DEPTH_LABEL.test(spec.label || '') && ['length', 'depth_mwe'].includes(q.dimension));
  const sites = (exp.site_ids || []).map((id) => (ctx.atlas.sites || {})[id]).filter(Boolean);
  const withDepth = sites.filter((site) => usableQuantity(site.depth) || usableQuantity(site.depth_mwe));
  const named = withDepth.length > 1;
  const hasLength = out.some((c) => c.quantity.dimension === 'length');
  const hasMwe = out.some((c) => c.quantity.dimension === 'depth_mwe');
  for (const site of withDepth) {
    const where = named ? ` at ${shortPlaceName(site, 40)}` : '';
    if (usableQuantity(site.depth) && !hasLength) {
      out.push({
        label: `Depth${where}`, quantity: site.depth,
        claims: [claim(site.id, '/depth')], fallback: [claim(site.id, '/sources')],
      });
    }
    if (usableQuantity(site.depth_mwe) && !hasMwe) {
      out.push({
        label: `Water-equivalent depth${where}`, quantity: site.depth_mwe,
        claims: [claim(site.id, '/depth_mwe')], fallback: [claim(site.id, '/sources')],
      });
    }
  }
  return out;
}

function baselineCandidates(exp, ctx) {
  const out = specCandidates(exp, (spec, q) => BASELINE_LABEL.test(spec.label || '') && q.dimension === 'length');
  if (out.length) return out;
  // No baseline among the key specifications: the sourced baseline of the beamline it sits on.
  for (const row of rowsForExperiment(ctx.atlas, exp)) {
    if (!usableQuantity(row.baseline.distance)) continue;
    out.push({
      label: row.label, quantity: row.baseline.distance,
      claims: [claim(row.beamline.id, `/baselines/${row.index}/distance`)], fallback: [claim(row.beamline.id, '/sources')],
    });
  }
  return out;
}

function massCandidates(exp) {
  return specCandidates(exp, (spec, q) => q.dimension === 'mass' && !MASS_EXCLUDED.test(spec.label || ''));
}

function energyCandidates(exp) {
  const out = specCandidates(exp, (spec, q) => q.dimension === 'energy' && !ENERGY_EXCLUDED.test(spec.label || ''));
  if (exp.energy_regime) {
    out.unshift({
      label: 'Energy regime', quantity: null, text: exp.energy_regime,
      claims: [claim(exp.id, '/energy_regime')], fallback: [claim(exp.id, '/sources')],
    });
  }
  return out;
}

/**
 * The lines of a quantity row: one common unit per dimension, the recorded wording kept.
 *
 * A value whose wording is more than one figure and one unit cannot be converted, so it
 * stays in the unit it was recorded in. Those values decide the common unit (the unit
 * most of them share), so a converted value is never set beside an unconverted one in
 * another unit. With none of them, the unit is chosen by magnitude (chooseUnit).
 */
function quantityLines(perExperiment, caps = {}) {
  const byDimension = new Map();
  for (const candidates of perExperiment) {
    for (const c of candidates) {
      if (!c.quantity || !isConvertible(c.quantity.dimension, c.quantity.unit)) continue;
      if (!byDimension.has(c.quantity.dimension)) byDimension.set(c.quantity.dimension, { all: [], fixed: [] });
      const entry = byDimension.get(c.quantity.dimension);
      entry.all.push({ value: c.quantity.value, unit: c.quantity.unit });
      if (!parseSimpleDisplay(c.quantity)) entry.fixed.push(c.quantity.unit);
    }
  }
  const units = new Map();
  for (const [dimension, { all, fixed }] of byDimension) {
    if (fixed.length) {
      const counts = new Map();
      fixed.forEach((unit) => counts.set(unit, (counts.get(unit) || 0) + 1));
      units.set(dimension, [...counts].sort((a, b) => b[1] - a[1])[0][0]);
    } else {
      units.set(dimension, chooseUnit(dimension, all, caps[dimension]));
    }
  }
  return perExperiment.map((candidates) => candidates.map((c) => {
    const base = { label: c.label, claims: c.claims, fallback: c.fallback };
    if (!c.quantity) return makeLine(c.text, base);
    const q = c.quantity;
    const unit = units.get(q.dimension);
    if (!unit || q.unit === unit || !isConvertible(q.dimension, q.unit)) return makeLine(quantityText(q), base);
    const simple = parseSimpleDisplay(q);
    if (!simple) {
      return makeLine(quantityText(q), {
        ...base, note: 'Shown as recorded: its wording has more than one figure, so it is not converted.',
      });
    }
    return makeLine(composeText(simple.prefix, convert(simple.number, q.dimension, simple.unit, unit), unit), {
      ...base, original: q.display,
    });
  }));
}

// ---- the other rows ----------------------------------------------------------------
function technologyLines(exp, ctx) {
  const groups = new Map();
  for (const id of exp.detector_ids || []) {
    const detector = (ctx.atlas.detectors || {})[id];
    if (!detector || !detector.technology_class) continue;
    if (!groups.has(detector.technology_class)) groups.set(detector.technology_class, []);
    groups.get(detector.technology_class).push(detector);
  }
  return [...groups].map(([technologyClass, detectors]) => makeLine(kindLabel(technologyClass), {
    // One detector's claim is enough to cite a class shared by several.
    firstOnly: true,
    claims: detectors.map((d) => claim(d.id, '/technology')),
    fallback: detectors.map((d) => claim(d.id, '/sources')),
    note: `Detector${detectors.length === 1 ? '' : 's'} recorded: ${detectors.map((d) => d.name).join('; ')}`,
  }));
}

/** An ISO-like date as a string that sorts in time order ("2024-08" before "2024-08-26"). */
const dateSortKey = (result) => {
  const date = result.date && typeof result.date === 'object' ? result.date.date : result.date;
  return typeof date === 'string' ? date : '';
};

function resultLines(exp, ctx) {
  const results = (exp.result_ids || []).map((id) => ctx.results.get(id)).filter(Boolean)
    .sort((a, b) => dateSortKey(a).localeCompare(dateSortKey(b)) || (a.name || '').localeCompare(b.name || ''));
  return results.map((result) => {
    const date = fmtDate(result.date) || (result.year ? String(result.year) : '');
    return makeLine(`${date ? `${date} · ` : ''}${result.name || result.title}`, {
      route: { type: 'result', slug: idSlug(result.id) }, kind: 'result',
      claims: [claim(result.id, '/date')], fallback: [claim(result.id, '/claim'), claim(result.id, '/sources')],
    });
  });
}

function collaborationLines(exp, ctx) {
  const lines = [];
  const collaborations = (exp.collaboration_ids || []).map((id) => (ctx.atlas.collaborations || {})[id]).filter(Boolean);
  for (const collaboration of collaborations) {
    const membership = collaboration.membership;
    if (!membership) continue;
    const prefix = collaborations.length > 1 ? `${collaboration.name}: ` : '';
    const asOf = membership.as_of ? ` (as of ${membership.as_of})` : '';
    const sources = { sourceIds: membership.roster_source_ids || [] };
    if (typeof membership.member_count === 'number') {
      lines.push(makeLine(`${prefix}${formatNumber(membership.member_count)} members${asOf}`, {
        claims: [claim(collaboration.id, '/membership/member_count')], ...sources,
      }));
    }
    if (typeof membership.institution_count === 'number') {
      const countries = typeof membership.country_count === 'number' ? ` in ${formatNumber(membership.country_count)} countries` : '';
      lines.push(makeLine(`${prefix}${formatNumber(membership.institution_count)} institutions${countries}${typeof membership.member_count === 'number' ? '' : asOf}`, {
        claims: [claim(collaboration.id, '/membership/institution_count')], ...sources,
      }));
    }
  }
  for (const candidate of specCandidates(exp, (spec) => SIZE_LABEL.test(spec.label || ''))) {
    lines.push(makeLine(quantityText(candidate.quantity), {
      label: candidate.label, claims: candidate.claims, fallback: candidate.fallback,
    }));
  }
  return lines;
}

// ---- the model ---------------------------------------------------------------------
/**
 * The comparison of `experiments` (records of atlas.json): `{ experiments, rows, when }`,
 * each row `{ key, label, cells }` with one cell `{ lines }` per experiment, in order.
 * `ctx` is `{ atlas, results (Map of id -> record), timelineState }`.
 */
export function buildComparison(ctx, experiments) {
  const rows = [];
  const perExperiment = (fn) => experiments.map((exp) => fn(exp, ctx));
  const plain = (key, label, fn) => rows.push({ key, label, cells: perExperiment(fn).map((lines) => ({ lines })) });
  const quantity = (key, label, fn, caps) => rows.push({
    key, label, cells: quantityLines(perExperiment(fn), caps).map((lines) => ({ lines })),
  });
  const when = whenText(ctx.timelineState);
  plain('status', when ? `Status in ${when}` : 'Status', statusLines);
  plain('dates', 'Dates', dateLines);
  plain('host', 'Host facility and site', hostLines);
  // A depth is read in metres (not 0.65 km), the way the sources give it.
  quantity('depth', 'Depth or overburden', depthCandidates, { length: 'm' });
  quantity('baseline', 'Baseline', baselineCandidates);
  rows[rows.length - 1].cells.forEach((cell, index) => {
    if (!cell.lines.length && !BASELINE_KINDS.has(experiments[index].kind)) cell.notApplicable = true;
  });
  quantity('mass', 'Target or fiducial mass', massCandidates);
  quantity('energy', 'Energy', energyCandidates);
  plain('technology', 'Technology', technologyLines);
  plain('results', 'Key results, with dates', resultLines);
  plain('collaboration', 'Collaboration size', collaborationLines);
  return {
    experiments: experiments.map((record) => ({
      id: record.id,
      slug: idSlug(record.id),
      name: record.name,
      short: shortExperimentName(record),
      kind: kindLabel(record.kind),
    })),
    rows,
    when,
  };
}

// ---- sources -----------------------------------------------------------------------
/** The source ids a line cites: its claims in provenance.json, else its fallbacks, else its own ids. */
export function lineSourceIds(line, provenance) {
  const ids = [];
  const add = (id) => { if (!ids.includes(id)) ids.push(id); };
  const take = (claims) => {
    let found = false;
    for (const { id, pointer } of claims) {
      const entry = provenance[id] && provenance[id][pointer];
      const sources = entry && entry.sources ? entry.sources : [];
      if (sources.length) found = true;
      sources.forEach(add);
      if (found && line.firstOnly) break;
    }
    return found;
  };
  if (!take(line.claims)) take(line.fallback);
  if (!ids.length) line.sourceIds.forEach(add);
  return ids;
}

/**
 * Gives every line its sources and numbers the sources in the order a reader meets them
 * (row by row, column by column): `line.sources` is the list of ids and `line.markers`
 * the numbers. Returns the numbered list `[{ n, id, url, title, type, accessed }]`.
 * A source id that sources.json does not know is dropped, not shown as a dead marker.
 */
export function attachSources(model, provenance, sourcesById) {
  const numbers = new Map();
  const list = [];
  for (const row of model.rows) {
    for (const cell of row.cells) {
      for (const line of cell.lines) {
        line.sources = lineSourceIds(line, provenance).filter((id) => sourcesById[id] && sourcesById[id].url);
        line.markers = line.sources.map((id) => {
          if (!numbers.has(id)) {
            const source = sourcesById[id];
            numbers.set(id, list.length + 1);
            list.push({
              n: list.length + 1, id, url: source.url, title: source.title || id,
              type: source.source_type || null, accessed: source.accessed || null,
            });
          }
          return numbers.get(id);
        });
      }
    }
  }
  model.sourceList = list;
  return list;
}

// ---- CSV ---------------------------------------------------------------------------
/** A line as text: "Label: value (recorded: original)". */
export function lineText(line) {
  return `${line.label ? `${line.label}: ` : ''}${line.text}${line.suffix}${line.original ? ` (recorded: ${line.original})` : ''}`;
}

export function cellText(cell) {
  if (cell.lines.length) return cell.lines.map(lineText).join(' | ');
  return cell.notApplicable ? NOT_APPLICABLE : NOT_RECORDED;
}

/**
 * The comparison as CSV text, exactly the table: one column per experiment, one row per
 * row, and a last column of source URLs. `sources` is the list attachSources() returned
 * (or null before the sources have loaded: that is an error to the caller, never an
 * export without citations). The metadata lines at the top start with "#".
 */
export function comparisonCsv(model, { dataVersion, accessed, link }) {
  if (!model.sourceList) throw new Error('the sources have not been attached to this comparison');
  const urls = (cells, index) => {
    const found = [];
    for (const line of cells[index].lines) {
      for (const id of line.sources) {
        const source = model.sourceList.find((s) => s.id === id);
        if (source && !found.includes(source.url)) found.push(source.url);
      }
    }
    return found;
  };
  const heads = model.experiments.map((e) => e.short);
  const preamble = [
    'HEP Atlas: comparison of experiments',
    `Atlas data version: ${dataVersion}`,
    `Accessed: ${accessed}`,
    `Experiments: ${model.experiments.map((e) => `${e.short} = ${e.id}`).join('; ')}`,
    link ? `Link: ${link}` : null,
    'Values that share a dimension are in one unit; "(recorded: ...)" gives the record\'s own wording. "not recorded" means the Atlas holds no sourced value, not that none exists.',
  ].filter(Boolean);
  const rows = model.rows.map((row) => {
    const citations = heads
      .map((head, index) => {
        const found = urls(row.cells, index);
        return found.length ? `${head}: ${found.join(' ')}` : null;
      })
      .filter(Boolean);
    return [row.label, ...row.cells.map(cellText), citations.length ? citations.join(' | ') : NOT_RECORDED];
  });
  return buildCsv({ preamble, header: ['Quantity', ...heads, 'Citations'], rows });
}
