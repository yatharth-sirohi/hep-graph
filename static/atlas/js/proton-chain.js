// proton-chain.js — the injector chain of a laboratory in a given year, from Atlas
// records only (no DOM, no fetch), so the player can use it and a unit check can
// run it under Node. Contract: ontology amendment A30 and
// docs/atlas-worklog/ACCELERATOR_CHAINS.md.
//
// What it does, and what it refuses to do:
//   * the ORDER of the stages is read from `accelerator.feeds_accelerator_ids`
//     (entries are id strings or {id, start, end, ...}; a link without dates holds
//     for hull(A) ∩ hull(B)) and from `beamline.accelerator_id`, filtered to the
//     year. Nothing is hard-coded: Linac2 vs Linac4 at CERN, the Recycler, the
//     Tevatron's years and the neutrino lines all fall out of the dates;
//   * a stage is in the chain only if the machine had a recorded state that year
//     that is not construction, planned or retired (`RUNNING`), and only if it
//     carries the same kind of particle as the chain (so the SPS → LEP electron
//     link is not followed by a proton);
//   * an energy is the machine's own: A30's rule, the specs of the latest-starting
//     covering interval that has the key, else the top-level value;
//   * a stage with no drawn geometry is still named, and says so;
//   * the geometry it hands back is only what the map bundle holds. It never
//     builds a path: no line is returned for a transfer, a building footprint or an
//     inferred direction.

import { statusForTimeline } from './model.js';

// The owner names features; this is the working title and the only place it is
// written (the control, the card and the sidebar section all read it here).
export const WORKING_TITLE = 'Follow the proton';
export function titleForSpecies(species) {
  return species === 'lepton' ? 'Follow the electrons and positrons' : WORKING_TITLE;
}

/** A machine in one of these states is part of the complex that year (a long
 * shutdown is still the complex; construction and retirement are not). */
export const RUNNING = new Set(['active', 'commissioning', 'upgrade', 'shutdown']);

// ------------------------------------------------------------------- dates
/** Month index (year * 12 + month - 1) of an A4 date (string or object), or null
 * when open. `edge` says which end of a coarse date a bare year means. */
export function monthOf(value, edge) {
  if (value == null) return null;
  const raw = typeof value === 'object' ? value.date : value;
  if (raw == null) return null;
  const m = /^(-?\d{1,4})(?:-(\d{2}))?(?:-(\d{2}))?/.exec(String(raw));
  if (!m) return null;
  const month = m[2] ? Number(m[2]) : (edge === 'start' ? 1 : 12);
  return Number(m[1]) * 12 + (month - 1);
}

/** The month a year is judged at: July, the convention of the timeline. */
function julyOf(year) {
  return year * 12 + 6;
}

function hullOf(record) {
  let start = Infinity;
  let end = -Infinity;
  let open = false;
  for (const interval of (record && record.intervals) || []) {
    const s = monthOf(interval.start, 'start');
    if (s != null) start = Math.min(start, s);
    const e = monthOf(interval.end, 'end');
    if (interval.end == null) open = true;
    else if (e != null) end = Math.max(end, e);
  }
  return {
    start: Number.isFinite(start) ? start : null,
    end: open || !Number.isFinite(end) ? null : end,
  };
}

// ------------------------------------------------------------------- links
/** Every `feeds_accelerator_ids` entry of a record as {from, to, start, end,
 * pointer, index, sourced}. `pointer` addresses the entry in provenance.json. */
export function feedLinks(record) {
  return ((record && record.feeds_accelerator_ids) || []).map((entry, index) => {
    const object = entry && typeof entry === 'object';
    return {
      from: record.id,
      to: object ? entry.id : entry,
      start: object ? entry.start : undefined,
      end: object ? entry.end : undefined,
      index,
      pointer: `/feeds_accelerator_ids/${index}`,
      kind: 'feeds',
    };
  }).filter((link) => typeof link.to === 'string');
}

/** The [start, end] months a link holds (null = unbounded), A30: explicit dates,
 * else the hull of the two machines. */
export function linkWindow(link, from, to) {
  const hf = hullOf(from);
  const ht = hullOf(to);
  let start = monthOf(link.start, 'start');
  let end = monthOf(link.end, 'end');
  if (link.start == null) {
    start = [hf.start, ht.start].filter((v) => v != null).reduce((a, b) => Math.max(a, b), -Infinity);
    if (start === -Infinity) start = null;
  }
  if (link.end == null) {
    end = [hf.end, ht.end].filter((v) => v != null).reduce((a, b) => Math.min(a, b), Infinity);
    if (end === Infinity) end = null;
  }
  return { start, end };
}

function holdsAt(window, year) {
  const t = julyOf(year);
  return (window.start == null || window.start <= t) && (window.end == null || t <= window.end);
}

function stateAt(record, year) {
  return record ? statusForTimeline(record.state_segments, { year }) : null;
}

function statusAt(record, year) {
  const resolved = stateAt(record, year);
  return resolved ? resolved.status : null;
}

// ----------------------------------------------------------------- species
/** What a machine carries: {family: Set('proton'|'antiproton'|'lepton'), hminus}. */
export function speciesOf(record) {
  const family = new Set();
  let hminus = false;
  for (const particle of (record && record.particles) || []) {
    const text = String(particle).toLowerCase();
    if (/^h[-−]/.test(text)) { hminus = true; family.add('proton'); } else if (text.includes('antiproton')) family.add('antiproton');
    else if (text.includes('proton')) family.add('proton');
    else if (text.includes('electron') || text.includes('positron')) family.add('lepton');
  }
  return { family, hminus };
}

function chainSpecies(record) {
  const { family } = speciesOf(record);
  if (family.has('proton')) return 'proton';
  if (family.has('lepton')) return 'lepton';
  return [...family][0] || null;
}

const SPECIES_WORD = { proton: 'protons', lepton: 'electrons and positrons', antiproton: 'antiprotons' };
export function speciesWord(species) {
  return SPECIES_WORD[species] || 'the beam';
}

// ---------------------------------------------------------------- energies
const GEV = { eV: 1e-9, keV: 1e-6, MeV: 1e-3, GeV: 1, TeV: 1e3, PeV: 1e6 };

/** A quantity as {lo, hi} in GeV: a plain value gives lo = hi; a range ({min, max}, in
 * `value` or beside it) gives its two ends, which the ladder draws as a bar. */
export function rangeGeV(quantity) {
  if (!quantity || typeof quantity !== 'object') return null;
  const factor = GEV[quantity.unit];
  if (factor == null) return null;
  let lo = quantity.value;
  let hi = quantity.value;
  if (lo && typeof lo === 'object') { hi = lo.max; lo = lo.min; }
  if (typeof lo !== 'number' && quantity.min != null && quantity.max != null) { lo = quantity.min; hi = quantity.max; }
  if (typeof lo !== 'number' || typeof hi !== 'number' || !Number.isFinite(lo) || !Number.isFinite(hi)) return null;
  return { lo: lo * factor, hi: hi * factor };
}

/** The upper end of a quantity in GeV (its value, or the top of its range), or null. */
export function toGeV(quantity) {
  const range = rangeGeV(quantity);
  return range ? range.hi : null;
}

/** A30: the specs of the latest-starting interval covering the year that has `key`,
 * else the top-level value. Returns {quantity, pointer, origin, label} or null. */
export function specAt(record, key, year) {
  if (!record) return null;
  const t = julyOf(year);
  let best = null;
  (record.intervals || []).forEach((interval, index) => {
    if (!interval.specs || !interval.specs[key]) return;
    const s = monthOf(interval.start, 'start');
    const e = monthOf(interval.end, 'end');
    if ((s != null && s > t) || (interval.end != null && e != null && e < t)) return;
    if (!best || (s != null ? s : -Infinity) >= best.start) best = { start: s != null ? s : -Infinity, index, interval };
  });
  if (best) {
    return {
      quantity: best.interval.specs[key],
      pointer: `/intervals/${best.index}/specs/${key}`,
      origin: 'interval',
      label: best.interval.label || 'era',
    };
  }
  const top = record.specs && record.specs[key];
  if (!top) return null;
  // The record also holds per-run values (the LHC's), none of which covers this year
  // (a long shutdown): the top-level one is then the design or current value, and the
  // card says so.
  const hasEras = (record.intervals || []).some((interval) => interval.kind === 'run' && interval.specs && interval.specs[key]);
  return { quantity: top, pointer: `/specs/${key}`, origin: 'record', label: null, eraGap: hasEras };
}

/** Energy in and out of a stage in a year. A beamline has one number, the energy of
 * the protons on target. */
export function stageEnergies(record, year) {
  if (record.type === 'beamline') {
    return { energyIn: null, energyOut: specAt(record, 'proton_energy', year), onTarget: true };
  }
  return {
    energyIn: specAt(record, 'injection_energy', year),
    energyOut: specAt(record, 'beam_energy', year),
    onTarget: false,
  };
}

// ---------------------------------------------------------------- geometry
const LINE_TYPES = new Set(['ring', 'linac', 'beamline', 'tunnel', 'transfer_line']);
const EARTH_R = 6371008.8;

function lineParts(geometry) {
  if (!geometry) return [];
  if (geometry.type === 'LineString') return [geometry.coordinates];
  if (geometry.type === 'MultiLineString') return geometry.coordinates;
  return [];
}

function metres(a, b) {
  const k = Math.PI / 180;
  const dy = (b[1] - a[1]) * k * EARTH_R;
  const dx = (b[0] - a[0]) * k * EARTH_R * Math.cos(((a[1] + b[1]) / 2) * k);
  return Math.hypot(dx, dy);
}

function partLength(coords) {
  let total = 0;
  for (let i = 1; i < coords.length; i += 1) total += metres(coords[i - 1], coords[i]);
  return total;
}

function featureCentre(feature) {
  const g = feature.geometry;
  if (g.type === 'Point') return g.coordinates;
  const c = feature.measured && feature.measured.centroid;
  return Array.isArray(c) ? c : null;
}

/** The part of a [lon, lat] line that lies before the point nearest to `target`
 * (null when that is less than `minM` of it: the line then starts at the target
 * or beyond it and is not a path the protons take). */
function upstreamOf(coords, target, minM) {
  let bestIndex = -1;
  let bestDistance = Infinity;
  for (let i = 0; i < coords.length; i += 1) {
    const d = metres(coords[i], target);
    if (d < bestDistance) { bestDistance = d; bestIndex = i; }
  }
  if (bestIndex < 0) return null;
  const cut = coords.slice(0, bestIndex + 1);
  return partLength(cut) >= minM ? { coords: cut, gapM: bestDistance } : null;
}

/**
 * What one stage looks like on this map, from the bundle alone.
 *   features    the stage's drawn structures (an inferred direction is not one)
 *   path        the line a dot may run along, as parts of [lat, lon]; null when the
 *               bundle holds no such line (a building footprint, a point, nothing)
 *   pathFeature the feature the path comes from
 *   pathNote    why there is no path, in words, or how the path was taken
 *   drawn       true when anything is drawn
 */
export function stageGeometry(bundle, entityId) {
  const index = (bundle && bundle.entity_index) || {};
  const ids = new Set(index[entityId] || []);
  const all = ((bundle && bundle.features) || []).filter((f) => ids.has(f.id));
  const features = all.filter((f) => f.representation !== 'inferred_direction' && f.feature_type !== 'direction_line');
  const out = { features, path: null, pathFeature: null, pathNote: null, drawn: features.length > 0, inferredOnly: !features.length && all.length > 0 };
  if (!features.length) return out;

  const isBeamline = entityId.startsWith('beamline:');
  const lines = features.filter((f) => lineParts(f.geometry).length);
  const toPath = (feature, parts) => ({ pathFeature: feature, path: parts.map((part) => part.map(([lon, lat]) => [lat, lon])) });

  if (isBeamline) {
    // The protons travel the primary line to the target; a line that starts at the
    // target is the neutrino axis, and is not their path.
    const transfer = lines.find((f) => f.feature_type === 'transfer_line');
    if (transfer) return { ...out, ...toPath(transfer, lineParts(transfer.geometry)), pathNote: 'the primary proton line, from its first pretarget magnet to the target' };
    const target = features.find((f) => f.feature_type === 'target_station');
    const centre = target ? featureCentre(target) : null;
    if (centre) {
      for (const feature of lines.filter((f) => LINE_TYPES.has(f.feature_type))) {
        const parts = lineParts(feature.geometry);
        const found = parts.length === 1 ? upstreamOf(parts[0], centre, 30) : null;
        const reach = Math.max(60, 3 * Math.max(feature.accuracy_m || 0, (target && target.accuracy_m) || 0));
        if (found && found.gapM <= reach) {
          return { ...out, ...toPath(feature, [found.coords]), pathNote: 'the part of the line before the target station, where the primary beamline ends' };
        }
      }
    }
    return { ...out, pathNote: 'the line the protons follow to the target is not drawn on this map; only the target is' };
  }

  // An accelerator's path is its ring or its linac line. Any other line drawn for it (a ring
  // road traced as a stand-in, a tunnel stub) is lit but is not the path of the beam.
  const preferred = lines.find((f) => f.feature_type === 'ring') || lines.find((f) => f.feature_type === 'linac');
  if (preferred) return { ...out, ...toPath(preferred, lineParts(preferred.geometry)) };
  if (lines.length) return { ...out, pathNote: 'the line drawn is a stand-in for the structure, not the path of the beam' };
  return { ...out, pathNote: 'only its footprint or position is drawn, not the line the beam follows' };
}

// ------------------------------------------------------------------ chains
/**
 * The chain of `facilityId` in `year`.
 *
 *   atlas   atlas.json
 *   bundle  the map's geometry bundle (decides which stages are drawn); without it
 *           every stage counts as drawn
 *
 * Returns { year, facilityId, species, stages: [stage], steps: [step] } where a
 * stage is {id, type, record, role: 'trunk'|'branch', feederId, link, status,
 * drawn, geometry, energies, alsoFeeds, alsoFedBy} and the steps alternate stages
 * with `transfer` steps between two drawn stages. `stages` is empty when the year
 * has no chain of at least two stages.
 */
export function chainAt(atlas, facilityId, year, bundle = null) {
  const accelerators = Object.values((atlas && atlas.accelerators) || {}).filter((a) => a.facility_id === facilityId);
  const beamlines = Object.values((atlas && atlas.beamlines) || {}).filter((b) => b.facility_id === facilityId);
  const geometryOf = (record) => (bundle ? stageGeometry(bundle, record.id) : { features: [], path: null, drawn: true, pathNote: null });
  const byId = new Map([...accelerators, ...beamlines].map((r) => [r.id, r]));
  const running = (record) => RUNNING.has(statusAt(record, year));

  // Nodes: machines in a state that year; beamlines only when drawn (this view
  // follows the proton as far as the map can show it).
  const nodeAcc = accelerators.filter(running);
  const nodeIds = new Set(nodeAcc.map((a) => a.id));
  const nodeBeam = beamlines.filter((b) => running(b) && nodeIds.has(b.accelerator_id) && geometryOf(b).drawn);
  for (const b of nodeBeam) nodeIds.add(b.id);

  // Every link valid that year, with the particle test applied afterwards.
  const links = [];
  for (const a of nodeAcc) {
    for (const link of feedLinks(a)) {
      const to = byId.get(link.to);
      if (!to || !nodeIds.has(to.id) || to.type !== 'accelerator') continue;
      if (holdsAt(linkWindow(link, a, to), year)) links.push(link);
    }
  }
  for (const b of nodeBeam) {
    links.push({ from: b.accelerator_id, to: b.id, kind: 'beamline', pointer: null, index: null });
  }

  const out = new Map();
  for (const link of links) {
    if (!out.has(link.from)) out.set(link.from, []);
    out.get(link.from).push(link);
  }
  const carries = (id, species) => {
    const record = byId.get(id);
    if (record.type === 'beamline') {
      const particle = String((record.primary_beam && record.primary_beam.particle) || '').toLowerCase();
      return species === 'proton' ? particle.includes('proton') && !particle.includes('anti') : true;
    }
    return speciesOf(record).family.has(species);
  };

  // The trunk: the longest chain of valid links (ties: the higher final energy).
  const outGeV = (id) => {
    const energies = stageEnergies(byId.get(id), year);
    return toGeV(energies.energyOut && energies.energyOut.quantity) || 0;
  };
  let best = null;
  const walk = (path, species, links0) => {
    const last = path[path.length - 1];
    let extended = false;
    for (const link of out.get(last) || []) {
      if (path.includes(link.to) || !carries(link.to, species)) continue;
      extended = true;
      walk([...path, link.to], species, [...links0, link]);
    }
    if (!extended) {
      const score = [path.length, outGeV(last)];
      if (!best || score[0] > best.score[0] || (score[0] === best.score[0] && score[1] > best.score[1])) {
        best = { path, links: links0, score, species };
      }
    }
  };
  for (const a of nodeAcc) {
    const species = chainSpecies(a);
    if (species) walk([a.id], species, []);
  }
  if (!best || best.path.length < 2) return { year, facilityId, species: best ? best.species : null, stages: [], steps: [] };
  const species = best.species;

  // Stages: the trunk, then everything downstream of it that the same beam reaches.
  const sequence = best.path.map((id, i) => ({ id, role: 'trunk', feederId: i ? best.path[i - 1] : null, link: i ? best.links[i - 1] : null }));
  const seen = new Set(best.path);
  for (let i = 0; i < best.path.length; i += 1) {
    const queue = [best.path[i]];
    while (queue.length) {
      const from = queue.shift();
      const next = (out.get(from) || []).filter((l) => !seen.has(l.to) && carries(l.to, species));
      next.sort((x, y) => outGeV(x.to) - outGeV(y.to));
      for (const link of next) {
        seen.add(link.to);
        sequence.push({ id: link.to, role: 'branch', feederId: from, link });
        queue.push(link.to);
      }
    }
  }

  const inSequence = new Set(sequence.map((s) => s.id));
  const stages = sequence.map((entry) => {
    const record = byId.get(entry.id);
    const geometry = geometryOf(record);
    const fedHere = new Set(sequence.filter((s) => s.feederId === entry.id).map((s) => s.id));
    const alsoFeeds = [];
    for (const link of out.get(entry.id) || []) {
      if (fedHere.has(link.to)) continue;
      const target = byId.get(link.to);
      alsoFeeds.push({
        id: target.id,
        name: target.name,
        why: carries(target.id, species)
          ? (inSequence.has(target.id) ? 'also directly' : 'directly')
          : `carries ${speciesWord(chainSpecies(target))}, not ${speciesWord(species)}`,
        link,
      });
    }
    for (const b of beamlines) {
      if (b.accelerator_id === entry.id && running(b) && !geometryOf(b).drawn) {
        alsoFeeds.push({ id: b.id, name: b.name, why: 'not drawn on this map', link: null });
      }
    }
    const alsoFedBy = [];
    for (const a of nodeAcc) {
      for (const link of feedLinks(a)) {
        if (link.to === entry.id && !inSequence.has(a.id) && holdsAt(linkWindow(link, a, record), year)) {
          alsoFedBy.push({ id: a.id, name: a.name, link });
        }
      }
    }
    return {
      id: entry.id,
      type: record.type,
      record,
      role: entry.role,
      feederId: entry.feederId,
      link: entry.link,
      status: statusAt(record, year),
      certainty: (stateAt(record, year) || {}).certainty || null,
      drawn: geometry.drawn,
      geometry,
      energies: stageEnergies(record, year),
      alsoFeeds,
      alsoFedBy,
    };
  });

  // Steps: each stage, and a transfer before it when it and its feeder are both drawn.
  const steps = [];
  const stageById = new Map(stages.map((s) => [s.id, s]));
  let stageNumber = 0;
  for (const stage of stages) {
    const feeder = stage.feederId ? stageById.get(stage.feederId) : null;
    if (feeder && feeder.drawn && stage.drawn) {
      steps.push({ kind: 'transfer', from: feeder, to: stage, link: stage.link });
    }
    stageNumber += 1;
    steps.push({ kind: 'stage', stage, stageNumber });
  }
  steps.forEach((step, i) => { step.index = i + 1; });
  return { year, facilityId, species, stages, steps };
}

/** The years (inclusive) in which a facility has a chain of at least two drawn
 * stages, as a sorted array. Empty means the map offers no "follow the beam". */
export function yearsWithChain(atlas, facilityId, bundle, minYear = 1931, maxYear = 2026) {
  const years = [];
  for (let year = minYear; year <= maxYear; year += 1) {
    const chain = chainAt(atlas, facilityId, year, bundle);
    if (chain.stages.filter((s) => s.drawn).length >= 2) years.push(year);
  }
  return years;
}

// ------------------------------------------------------------------ ladder
/** The log-scale rows of the energy ladder: one per stage, with the energy range
 * the stage covers in GeV, and the decade limits of the axis. */
export function ladderRows(chain) {
  const rows = chain.steps.filter((s) => s.kind === 'stage').map((step) => {
    const e = step.stage.energies;
    const out = rangeGeV(e.energyOut && e.energyOut.quantity);
    const inn = rangeGeV(e.energyIn && e.energyIn.quantity);
    return { step, inGeV: inn ? inn.hi : null, outGeV: out ? out.hi : null, inLo: inn ? inn.lo : null, outLo: out ? out.lo : null };
  });
  const values = rows.flatMap((r) => [r.inGeV, r.outGeV, r.inLo, r.outLo]).filter((v) => v != null && v > 0);
  if (!values.length) return { rows, lo: -3, hi: 0 };
  const lo = Math.floor(Math.log10(Math.min(...values)));
  let hi = Math.ceil(Math.log10(Math.max(...values)));
  if (hi <= lo) hi = lo + 1;
  return { rows, lo, hi };
}

/** An axis tick as a person writes it: 100 MeV, 1 GeV, 10 TeV. */
export function tickLabel(exponentOfGeV) {
  const value = 10 ** exponentOfGeV;
  if (value < 1e-3) return `${Math.round(value * 1e6)} keV`;
  if (value < 1) return `${Math.round(value * 1e3)} MeV`;
  if (value < 1e3) return `${Math.round(value)} GeV`;
  return `${Math.round(value / 1e3)} TeV`;
}
