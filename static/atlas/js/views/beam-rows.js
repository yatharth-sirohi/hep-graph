// beam-rows.js — which beams the "Beam through the Earth" view can draw, and how
// a link, a search entry or a panel names them. Pure data and arithmetic over
// atlas.json (no DOM, no fetch), so panels.js and the search can use it without
// loading the view itself, and the unit check can run it under Node.
//
// A *row* is one entry of a beamline's `baselines[]`: a source site, a far-detector
// site and the sourced distance between them. The view's route names a row as
// `<beamline-slug>` (the first row) or `<beamline-slug>~<row-index>`:
//
//   #/view/beam-section/lbnf           LBNF: Fermilab -> SURF (DUNE)
//   #/view/beam-section/numi~1         NuMI's second row: Fermilab -> Ash River (NOvA)

import { statusForTimeline, timelineAbsenceReason } from '../model.js';
import { sectionGeometry, uncertainty } from './beam-geometry.js';

export const VIEW_NAME = 'beam-section';
// The owner names features; this is the working title, and the only place it is
// written (the heading, the link text and the search entry all read it here).
export const WORKING_TITLE = 'Beam through the Earth';

/** Below this chord a "section of the Earth" is a dot: such a row is not offered. */
const MIN_CHORD_KM = 1;

// ---- names ------------------------------------------------------------------------
function stripParen(text) {
  return String(text || '').replace(/\s*\([^)]*\)/g, '').trim();
}

/** A short name for a facility or site: its own name when it fits, else the first
 * alias that does ("Fermi National Accelerator Laboratory" -> "Fermilab"). The same
 * rule the globe's beam labels use. */
export function shortPlaceName(record, max = 20) {
  if (!record) return '';
  const name = stripParen(record.name);
  if (name && name.length <= max) return name;
  for (const alias of record.aliases || []) {
    const short = stripParen(alias);
    if (short.length >= 3 && short.length <= max) return short;
  }
  return name.length > max ? `${name.slice(0, max - 1).trimEnd()}…` : name;
}

function shortDetectorName(record) {
  const clean = (text) => stripParen(text).replace(/\s+((far|near)\s+)?detector$/i, '').trim();
  const candidates = [record.name, ...(record.aliases || [])].map(clean).filter((t) => t.length >= 4);
  candidates.sort((a, b) => a.length - b.length);
  return candidates[0] || stripParen(record.name);
}

// ---- sites --------------------------------------------------------------------------
/** [lat, lon] and the recorded precision of a site, whichever shape the bundle gave it
 * (the loader lifts `coordinates` to the top level; a raw atlas.json keeps it nested). */
export function siteLatLon(site) {
  if (!site) return null;
  const c = site.coordinates || {};
  const lat = site.lat != null ? site.lat : c.lat;
  const lon = site.lon != null ? site.lon : c.lon;
  if (typeof lat !== 'number' || typeof lon !== 'number') return null;
  const precision = site.precision_m != null ? site.precision_m : c.precision_m;
  return {
    lat,
    lon,
    precisionM: typeof precision === 'number' ? precision : null,
    approximate: !!c.approximate,
    kind: site.coord_kind || c.kind || null,
  };
}

/** A recorded length in km, or null (the site's `depth`, in m or km). */
export function lengthKm(quantity) {
  if (!quantity || typeof quantity.value !== 'number' || !Number.isFinite(quantity.value)) return null;
  const unit = String(quantity.unit || 'km').toLowerCase();
  if (unit === 'km') return quantity.value;
  if (unit === 'm') return quantity.value / 1000;
  if (unit === 'mi' || unit === 'mile' || unit === 'miles') return quantity.value * 1.609344;
  return null;
}

function detectorsAt(atlas, siteId) {
  const out = [];
  for (const detector of Object.values(atlas.detectors || {})) {
    for (const placement of detector.placements || []) {
      if (placement.site_id === siteId) out.push({ record: detector, role: placement.role });
    }
  }
  return out;
}

/** The far end named as the globe names it: the detector there when the site holds
 * one far (else main) detector, else the facility. */
function farEndName(atlas, site) {
  const placed = detectorsAt(atlas, site.id);
  let pool = placed.filter((p) => p.role === 'far');
  if (!pool.length) pool = placed.filter((p) => p.role === 'main');
  if (pool.length === 1) return shortDetectorName(pool[0].record);
  const facility = site.facility_id && atlas.facilities && atlas.facilities[site.facility_id];
  return shortPlaceName(facility) || shortPlaceName(site);
}

function siteView(atlas, siteId, beamline, role) {
  const record = (atlas.sites || {})[siteId];
  if (!record) return { id: siteId, record: null, located: false, name: siteId, short: siteId };
  const position = siteLatLon(record);
  const facility = (record.facility_id && atlas.facilities && atlas.facilities[record.facility_id])
    || (beamline.facility_id && atlas.facilities && atlas.facilities[beamline.facility_id]) || null;
  const short = role === 'far'
    ? farEndName(atlas, record)
    : (shortPlaceName(facility) || shortPlaceName(record));
  const depthKm = lengthKm(record.depth);
  return {
    id: siteId,
    record,
    located: !!position,
    ...(position || {}),
    name: record.name,
    short,
    setting: record.setting || null,
    depth: depthKm == null ? null : {
      km: depthKm,
      approx: !!(record.depth && record.depth.approx),
      display: record.depth.display || `${record.depth.value} ${record.depth.unit}`,
    },
  };
}

// ---- rows ---------------------------------------------------------------------------
/** The route argument of a row: `lbnf`, or `numi~1` for a later row. */
export function rowArg(beamlineId, index) {
  const slug = String(beamlineId).split(':')[1];
  return index === 0 ? slug : `${slug}~${index}`;
}

export function viewHash(arg) {
  return `#/view/${VIEW_NAME}/${arg}`;
}

/** `{ slug, index }` from a route argument, or null when it is not one. */
export function parseArg(arg) {
  const match = /^([a-z0-9][a-z0-9-]*)(?:~(\d+))?$/.exec(String(arg || ''));
  if (!match) return null;
  return { slug: match[1], index: match[2] === undefined ? 0 : Number(match[2]) };
}

function baselineKm(distance) {
  return lengthKm(distance);
}

function makeRow(atlas, beamline, baseline, index) {
  const from = siteView(atlas, baseline.from_site_id, beamline, 'near');
  const to = siteView(atlas, baseline.to_site_id, beamline, 'far');
  const arg = rowArg(beamline.id, index);
  return {
    arg,
    hash: viewHash(arg),
    beamline,
    index,
    baseline,
    from,
    to,
    located: from.located && to.located,
    sourcedKm: baselineKm(baseline.distance),
    label: `${from.short} → ${to.short}`,
  };
}

/** Every baseline row of every beamline, located or not, in id order. */
export function allBeamRows(atlas) {
  const out = [];
  for (const beamline of Object.values(atlas.beamlines || {}).sort((a, b) => (a.id < b.id ? -1 : 1))) {
    (beamline.baselines || []).forEach((baseline, index) => out.push(makeRow(atlas, beamline, baseline, index)));
  }
  return out;
}

/** The rows the view can draw: both ends have coordinates and a chord of at least a kilometre. */
export function beamRows(atlas) {
  return allBeamRows(atlas).filter((row) => {
    if (!row.located) return false;
    return rowGeometry(row).geometry.chordKm >= MIN_CHORD_KM;
  });
}

/** The row a route argument names: `{ row }`, or `{ error }` in words a reader can act on. */
export function resolveRow(atlas, arg) {
  const parsed = parseArg(arg);
  if (!parsed) return { error: `“${arg}” is not a beamline.` };
  const beamline = (atlas.beamlines || {})[`beamline:${parsed.slug}`];
  if (!beamline) return { error: `The Atlas has no beamline called “${parsed.slug}”.` };
  const baselines = beamline.baselines || [];
  if (!baselines.length) {
    return {
      error: `${beamline.name} has no recorded baseline between two sites, so there is no section to draw. `
        + 'That says nothing about whether it has detectors: only that this Atlas records no source-to-detector distance for it.',
      beamline,
    };
  }
  if (parsed.index >= baselines.length) {
    return { error: `${beamline.name} has ${baselines.length} recorded baseline${baselines.length === 1 ? '' : 's'}, numbered from 0; there is no number ${parsed.index}.`, beamline };
  }
  const row = makeRow(atlas, beamline, baselines[parsed.index], parsed.index);
  if (!row.located) {
    const missing = [row.from, row.to].filter((s) => !s.located).map((s) => s.name).join(' and ');
    return { error: `The Atlas records no coordinates for ${missing}, so the section cannot be computed.`, beamline, row };
  }
  if (rowGeometry(row).geometry.chordKm < MIN_CHORD_KM) {
    return { error: `The two sites of this baseline are closer than ${MIN_CHORD_KM} km on the recorded coordinates, so there is no section to draw.`, beamline, row };
  }
  return { row, beamline };
}

/** The computed section of a row: geometry, the sites' summed precision and the uncertainty. */
export function rowGeometry(row) {
  const geometry = sectionGeometry([row.from.lat, row.from.lon], [row.to.lat, row.to.lon]);
  const precisionKm = row.from.precisionM != null && row.to.precisionM != null
    ? (row.from.precisionM + row.to.precisionM) / 1000 : null;
  return { geometry, precisionKm, uncertainty: uncertainty(geometry.centralAngleRad, precisionKm) };
}

/** The rows an experiment's far detectors sit on: its beamlines' rows whose far end is one of its sites. */
export function rowsForExperiment(atlas, experiment) {
  const sites = new Set(experiment.site_ids || []);
  const beamlineIds = new Set(experiment.beamline_ids || []);
  return beamRows(atlas).filter((row) => beamlineIds.has(row.beamline.id) && sites.has(row.to.id));
}

/** The rows of a beamline the view can draw. */
export function rowsForBeamline(atlas, beamline) {
  return beamRows(atlas).filter((row) => row.beamline.id === beamline.id);
}

// ---- off-axis angle ----------------------------------------------------------------
/**
 * The sourced off-axis angles that belong to a row: the "Off-axis angle" key
 * specification of the experiments housed at the row's far end (T2K at Super-K, NOvA
 * at Ash River, Hyper-K at Tochibora). When one of them is housed at this far site
 * alone and another also at a different far site of the same beamline (T2K lists
 * Super-K and Tochibora), only the former is taken, so the T2HK row carries Hyper-K's
 * angle and not T2K's.
 */
export function offAxisFor(atlas, row) {
  const farSites = new Set((row.beamline.baselines || []).map((b) => b.to_site_id));
  const candidates = [];
  for (const experimentId of row.beamline.experiment_ids || []) {
    const experiment = (atlas.experiments || {})[experimentId];
    if (!experiment || !(experiment.site_ids || []).includes(row.to.id)) continue;
    (experiment.key_specs || []).forEach((spec, specIndex) => {
      if (!/off[- ]?axis/i.test(spec.label || '') || !spec.quantity) return;
      const sharesAnotherFarSite = (experiment.site_ids || []).some((id) => id !== row.to.id && farSites.has(id));
      candidates.push({
        experiment,
        label: spec.label,
        quantity: spec.quantity,
        pointer: `/key_specs/${specIndex}/quantity`,
        exclusive: !sharesAnotherFarSite,
      });
    });
  }
  const exclusive = candidates.filter((c) => c.exclusive);
  return exclusive.length ? exclusive : candidates;
}

// ---- status ---------------------------------------------------------------------------
const STATUS_PHRASE = {
  construction: 'under construction',
  commissioning: 'commissioning',
  approved: 'approved, not built',
  proposed: 'proposed',
  planned: 'planned',
  completed: 'completed',
  decommissioned: 'decommissioned',
  shutdown: 'shut down',
  upgrade: 'in upgrade shutdown',
  cancelled: 'cancelled',
};
const ENDED = new Set(['completed', 'decommissioned', 'cancelled']);

export function statusPhrase(status) {
  if (!status || status === 'active') return '';
  if (status === 'absent') return 'not yet built';
  return STATUS_PHRASE[status] || String(status).replace(/_/g, ' ');
}

/**
 * The state the beam is drawn in for the selected year (or range): the same rule the
 * globe's arcs and the beamline panel's badge follow. The row's own status wins over
 * its beamline's (the Hyper-K arm is under construction while the beamline runs).
 * `flowing` is true only for a beam that is running, which is the only one animated;
 * a construction or not-yet-built beam is drawn dashed.
 */
export function beamStatusAt(row, timelineState) {
  const { beamline, baseline } = row;
  let status = beamline.status || 'active';
  const segments = beamline.state_segments;
  // No year and no range (a state that has not been read yet): the record's own status.
  const dated = !!timelineState && (!!timelineState.range || timelineState.year != null);
  if (dated && segments && segments.length) {
    const present = statusForTimeline(segments, timelineState);
    if (present) {
      status = present.status;
    } else if (timelineAbsenceReason(segments, timelineState) === 'ended') {
      status = ENDED.has(beamline.status) ? beamline.status : 'completed';
    } else {
      status = 'absent';
    }
  }
  if (baseline.status && status !== 'absent') status = baseline.status;
  return {
    status,
    phrase: statusPhrase(status),
    flowing: status === 'active',
    dashed: status === 'construction' || status === 'commissioning' || status === 'absent'
      || status === 'approved' || status === 'proposed' || status === 'planned',
  };
}

// ---- search ---------------------------------------------------------------------------
/** Search entries for the Atlas search box: "beam through the earth" reaches every row,
 * and "DUNE beam" or "T2K beam" the row whose far detector the experiment is. Entries
 * are `{ type: 'view', id, name, aliases, subtitle }`, the shape search.json rows take. */
export function beamSearchEntries(atlas) {
  return beamRows(atlas).map((row) => {
    const names = [];
    for (const experimentId of row.beamline.experiment_ids || []) {
      const experiment = (atlas.experiments || {})[experimentId];
      if (!experiment || !(experiment.site_ids || []).includes(row.to.id)) continue;
      names.push(stripParen(experiment.name), ...(experiment.aliases || []).map(stripParen));
    }
    const aliases = [
      WORKING_TITLE,
      'neutrino beam through the Earth',
      'beam cross-section',
      'beam section',
      ...[...new Set(names.filter(Boolean))].map((name) => `${name} beam`),
      `${row.beamline.name} section`,
    ];
    return {
      type: 'view',
      id: `view:${VIEW_NAME}/${row.arg}`,
      name: `${WORKING_TITLE}: ${row.label}`,
      aliases,
      subtitle: `Section view · ${row.baseline.distance ? row.baseline.distance.display : 'recorded baseline'}`,
    };
  });
}
