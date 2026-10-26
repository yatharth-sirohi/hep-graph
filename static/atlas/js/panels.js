// panels.js — detail panels with progressive disclosure (native <details>).
// Facility / experiment / collaboration / institution / topic / result /
// document. Long text (text.json) and citations (provenance.json) are
// fetched lazily, on first panel open, via loader.js (which itself caches).

import * as loader from './loader.js';
import {
  quantityText, fmtDate, fmtInterval, titleCase, kindLabel, statusEra, statusForTimeline, timelineAbsenceReason,
} from './model.js';
import * as provenance from './provenance.js';
import { greatCircleM, initialBearing } from './localmap.js';
import {
  VIEW_NAME, WORKING_TITLE, rowGeometry, rowsForBeamline, rowsForExperiment,
} from './views/beam-rows.js';
import * as underground from './views/underground-rows.js';
import * as frontier from './views/frontier-rows.js';
import { quoteView, readableText, readableView } from './tex.js';

let ATLAS = null;
let INDEX = null;
let CALLBACKS = {};
let lastCollaborationId = null;
let container = null;
// §23 "focus returning to the trigger": whatever had keyboard focus the
// moment a *new* entity was opened (a search result, a globe marker, a link
// inside another panel) — not re-captured on a timeline-driven re-render of
// the same entity, so a slider drag while a panel is open doesn't overwrite
// it. Restored when the panel closes (render(null, ...)).
let openerElement = null;
let lastRenderedId = null;

export function init({ el, atlas, index, navigate, focusGlobe, viewOnGlobe }) {
  container = el;
  ATLAS = atlas;
  INDEX = index;
  CALLBACKS = { navigate, focusGlobe, viewOnGlobe };
  provenance.configure(index);
}

export function setCollaborationContext(id) {
  lastCollaborationId = id;
}

function h(tag, attrs = {}, children = []) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (k === 'class') el.className = v;
    else if (k === 'text') el.textContent = v;
    else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
    else if (v !== null && v !== undefined) el.setAttribute(k, v);
  }
  for (const child of [].concat(children)) {
    if (child == null) continue;
    el.appendChild((typeof child === 'string' || typeof child === 'number') ? document.createTextNode(String(child)) : child);
  }
  return el;
}

function linkTo(route, text, extraClass) {
  const a = h('a', { href: `#/${route.type}/${route.slug}`, class: `entity-link ${extraClass || ''}`.trim() }, text);
  a.addEventListener('click', (event) => {
    event.preventDefault();
    CALLBACKS.navigate({ entity: route });
  });
  return a;
}

function idRoute(id) {
  const [type, slug] = id.split(/:(.+)/);
  return { type, slug };
}

function section(titleText, contentNodes, { open = true } = {}) {
  const details = h('details', { class: 'panel-section', open: open ? '' : null });
  details.appendChild(h('summary', {}, titleText));
  const body = h('div', { class: 'panel-section-body' }, contentNodes);
  details.appendChild(body);
  return details;
}

// A figure and its unit never split across lines ("1285 km", "17.5 kt"): each
// pair is wrapped in a nowrap span. The text itself is unchanged, so copying a
// value still gives "1285 km", and a value too long for the line still wraps
// between pairs rather than overflowing the panel.
const FIGURE_WITH_UNIT = /(\d[\d.,]*(?:[-–]\d[\d.,]*)?)\s+([A-Za-zµΩ°%][\w.µΩ°%/^·²³⁻-]*)/g;
function keepFiguresWithUnits(value) {
  if (typeof value !== 'string') return value;
  const nodes = [];
  let last = 0;
  for (const match of value.matchAll(FIGURE_WITH_UNIT)) {
    if (match.index > last) nodes.push(value.slice(last, match.index));
    nodes.push(h('span', { class: 'nowrap' }, `${match[1]} ${match[2]}`));
    last = match.index + match[0].length;
  }
  if (!nodes.length) return value;
  if (last < value.length) nodes.push(value.slice(last));
  return nodes;
}

// Label/value facts. Returns null when no row has a value, so callers can hand
// it straight to a section that then does not appear.
function keyValueList(pairs) {
  const rows = pairs.filter(([, value]) => value != null && value !== '');
  if (!rows.length) return null;
  const dl = h('dl', { class: 'kv-list' });
  for (const [key, value] of rows) {
    dl.appendChild(h('div', { class: 'kv-row' }, [
      h('dt', {}, key),
      h('dd', {}, keepFiguresWithUnits(value)),
    ]));
  }
  return dl;
}

// A list of links to atlas records, or null when there are none.
function recordLinks(records) {
  return records.length
    ? h('ul', { class: 'entity-list' }, records.map((r) => h('li', {}, linkTo(idRoute(r.id), r.name))))
    : null;
}

function resultLinks(results) {
  return results.length
    ? h('ul', { class: 'entity-list' }, results.map((r) => h('li', {}, linkTo(idRoute(r.id), r.name || r.title))))
    : null;
}

function documentLinks(documents) {
  return documents.length
    ? h('ul', { class: 'entity-list' }, documents.map((d) => h('li', {},
      h('a', { href: d.reference && d.reference.url, target: '_blank', rel: 'noopener' }, d.name))))
    : null;
}

function emptyNote(text) {
  return h('p', { class: 'empty-note' }, text);
}

// A record panel is a stack of sections, and a section the Atlas has nothing for
// is not drawn: a heading that opens onto "none" is a click that tells a reader
// nothing. Each skipped section is remembered, and note() closes the panel with
// one line naming them all — worded as absence from the Atlas, never as absence
// in the world (the Atlas covers part of the field, and an empty list here is
// not evidence that none exist; that is also why this is a line and not silence).
//   add(title, content, { open, label, missing, quiet })
//       content: a node, an array, or null/[] to skip the section.
//       label:   what the closing line calls the section when it is skipped
//                (default: its title).
//       quiet:   skip it without naming it (a section most records have no
//                reason to carry, like a document's separate volumes).
//       missing: pieces absent from a section that is drawn anyway (the
//                plain-language summary of an otherwise filled Overview).
//   groups(title, [[heading, node, label?], ...], { open, optional })
//       sub-headed lists; only the filled ones show. `optional` headings are
//       not worth naming when empty.
function panelSections(frag) {
  const omitted = [];
  const nodesOf = (content) => [].concat(content).filter((node) => node != null && node !== false);
  return {
    add(titleText, content, { label, missing = [], quiet = false, ...options } = {}) {
      const nodes = nodesOf(content);
      if (!nodes.length) {
        if (!quiet) omitted.push(label || titleText);
        return null;
      }
      omitted.push(...missing.filter(Boolean));
      const el = section(titleText, nodes, options);
      frag.appendChild(el);
      return el;
    },
    groups(titleText, entries, { optional = [], ...options } = {}) {
      const filled = entries.filter(([, node]) => node != null);
      if (!filled.length) {
        omitted.push(titleText);
        return null;
      }
      for (const [heading, node, label] of entries) {
        if (node == null && !optional.includes(heading)) omitted.push(label || heading);
      }
      const nodes = filled.flatMap(([heading, node]) => [h('h4', {}, heading), node]);
      const el = section(titleText, nodes, options);
      frag.appendChild(el);
      return el;
    },
    note() {
      if (!omitted.length) return;
      frag.appendChild(h('p', { class: 'omitted-note' }, [
        `None recorded in the Atlas: ${omitted.join(', ')}. Coverage is partial, so this is not evidence that none exist (`,
        h('a', { href: '/atlas/about.html#coverage' }, 'coverage report'),
        ').',
      ]));
    },
  };
}

// The generated bundle puts an entity's plain-language summary right on its
// atlas.json record (`record.summary.plain`); the fixtures instead only put
// it in the lazily-loaded text bundle (`t.summary_plain`, no `summary` key
// on the record at all). Prefer the record's own field and fall back to the
// text bundle's, so both trees render a summary when one was written.
function plainSummaryOf(record, t) {
  return (record && record.summary && record.summary.plain) || (t && t.summary_plain) || null;
}

// A23 (docs/HEP_ATLAS_ONTOLOGY.md): a site's stripped `coordinates` carry
// `approximate: true` when the canonical confidence was `approximate` or
// `uncertain` — a campus-grade stand-in for a detector position no fetched
// source gives. The record must never be presented as if that point *were*
// the detector position, so this names the coordinate's own kind instead of
// echoing the site's `(setting)` label the way a real detector point would.
function siteLocationNote(site) {
  const coordinates = site && site.coordinates;
  if (!coordinates || !coordinates.approximate) return null;
  const kindLabel = (coordinates.kind || '').replace(/_/g, ' ');
  return h('div', { class: 'site-location-note' },
    `Approximate location${kindLabel ? ` (${kindLabel} point)` : ''} — not the detector position`);
}

// site/detector/accelerator/beamline panels (below): the generated bundle
// carries depth/depth_mwe/altitude as full Quantity objects (quantityText
// handles those already); the dev fixtures instead flatten them to plain
// numbers under `_m`-suffixed keys with no unit string at all (A23 predates
// these four record types getting fixture coverage). This covers both shapes
// without the caller needing to know which tree it's reading.
function siteQuantity(value, unit) {
  if (value == null) return null;
  if (typeof value === 'object') return quantityText(value);
  return `${value} ${unit}`;
}

// A detector's `subsystems` entries are inconsistent even within one bundle:
// most are `{name, description}` objects, a handful (e.g. detector:alice,
// detector:sphenix, detector:star in the generated tree) are bare strings,
// and `description` itself is sometimes a list of strings rather than one
// (e.g. detector:cdms-ii) rather than a single string. Render whatever shape
// shows up instead of assuming the common case.
function subsystemNode(sub) {
  if (sub == null) return null;
  if (typeof sub === 'string') return h('li', {}, sub);
  const description = Array.isArray(sub.description) ? sub.description.join(' ') : sub.description;
  return h('li', {}, sub.name
    ? [h('strong', {}, sub.name), description ? `: ${description}` : '']
    : (description || ''));
}

// Shared by the four location/instrument panels below: a document's
// `owner_ids` lists every entity it documents, and the owning record's own
// `document_ids` (a build-derived inverse, per docs/HEP_ATLAS_BUNDLES.md) is
// read too so a document is found even if one side of that pair is thin.
async function documentsFor(id, record) {
  const { list } = await loader.getDocuments();
  return list.filter((d) => (d.owner_ids || []).includes(id) || (record.document_ids || []).includes(d.id));
}

function intervalLine(iv) {
  const label = iv.label ? `${titleCase(iv.label)}: ` : '';
  const status = titleCase(iv.status);
  return `${label}${status} (${fmtInterval(iv.start, iv.end) || '?–present'})`;
}

// Sources are ~2.2 MB combined (provenance.json + sources.json) and the
// disclosure they render into is collapsed by default — P1-2 in
// docs/atlas-worklog/REVIEW_performance.md found every panel open fetching
// both regardless, because this used to be `await`-ed unconditionally before
// the panel even rendered. Now nothing is fetched until the <details> is
// actually opened (a native `toggle` event fires whether that came from a
// click or the keyboard), the body shows a visible loading state while the
// request is in flight, and a failure renders a real message plus a retry
// button rather than leaving the disclosure silently empty.
// `record` is the entity's own already-loaded record (facility/experiment/
// collaboration/result/…, whatever the caller is rendering) — claimLabel()
// reads it to turn a pointer like `/key_specs/0/quantity` into "Baseline:
// ~1300 km" using the record's own content, instead of showing the pointer
// itself. For a collaboration, pass `membershipMembers` (the loaded roster,
// reordered to each row's authored `source_index`) so `/members/N` resolves
// to the right institution's name.
function sourcesDisclosure(entityId, record, { approximateSites = [], membershipMembers = null } = {}) {
  // data-state (idle → loading → loaded | error) says where the lazy load is,
  // so nothing has to guess from the placeholder text.
  const details = h('details', { class: 'panel-section', 'data-state': 'idle' });
  details.appendChild(h('summary', {}, 'Sources'));
  const body = h('div', { class: 'panel-section-body' }, [
    emptyNote('Opens to load this entity’s sources.'),
  ]);
  details.appendChild(body);

  let loaded = false;
  let inFlight = false;

  async function load() {
    if (loaded || inFlight) return;
    inFlight = true;
    details.dataset.state = 'loading';
    body.innerHTML = '';
    body.appendChild(h('p', { class: 'loading-note', role: 'status' }, 'Loading sources…'));
    try {
      const [provenanceBundle, sourcesBundle] = await Promise.all([loader.getProvenance(), loader.getSources()]);
      const entries = provenanceBundle[entityId];
      const labelRecord = membershipMembers ? { ...record, members: membershipMembers } : record;
      const items = provenance.renderClaimItems(entries, sourcesBundle, labelRecord);
      // A23: a linked site's admitted-approximate coordinate explains *why*
      // in its own provenance note (e.g. "campus point, real hall position
      // not yet sourced") — the visible location line only says *that* it
      // is approximate. provenance.json is keyed by entity id, so the
      // site's own entry is already sitting in the same object this
      // disclosure just fetched for its own entity; no extra request.
      for (const site of approximateSites) {
        const siteEntry = provenanceBundle[site.id] && provenanceBundle[site.id]['/coordinates'];
        if (siteEntry && siteEntry.note) {
          items.push(provenance.renderApproximateLocationNote(site, siteEntry.note));
        }
      }
      body.innerHTML = '';
      body.appendChild(items.length
        ? h('ul', { class: 'source-list' }, items)
        : emptyNote('No sourced fields recorded for this entity yet.'));
      loaded = true;
      details.dataset.state = 'loaded';
    } catch (error) {
      details.dataset.state = 'error';
      body.innerHTML = '';
      body.appendChild(h('p', { class: 'error-note', role: 'alert' },
        `Could not load sources: ${error.message}`));
      const retry = h('button', { type: 'button', class: 'text-btn' }, 'Retry');
      retry.addEventListener('click', load);
      body.appendChild(retry);
    } finally {
      inFlight = false;
    }
  }

  details.addEventListener('toggle', () => {
    if (details.open) load();
  });
  return details;
}

// ---- local map view hook (docs/HEP_ATLAS_GEOMETRY.md §4) -- begin -------
// How a local map depicts one entity, from the map's own geometry bundle:
//   drawn      a surveyed, georeferenced or derived feature stands for it
//   direction  only an inferred bearing points toward it (a line, not a place)
//   none       the map covers the entity's area but draws nothing for it
//   unknown    the bundle could not be read, so nothing is claimed
// `map_id` / `geometry_map_ids` only say that a map is *about* the entity; the
// wording a panel may use ("shown to scale") depends on this.
async function depictionOn(mapId, entityId) {
  const meta = ((ATLAS && ATLAS.maps) || {})[mapId];
  if (!meta || !meta.bundle) return 'unknown';
  try {
    const bundle = await loader.getGeometry(meta.bundle);
    const featureIds = new Set(((bundle.entity_index || {})[entityId]) || []);
    const features = (bundle.features || []).filter((f) => featureIds.has(f.id));
    if (!features.length) return 'none';
    return features.some((f) => f.representation !== 'inferred_direction' && f.feature_type !== 'direction_line')
      ? 'drawn' : 'direction';
  } catch (error) {
    return 'unknown';
  }
}

/**
 * The maps that concern a record, each with how it depicts it. `map_id` on a
 * facility or a site, `geometry_map_ids` on an accelerator, beamline or
 * detector (the maps that draw something for it). A detector that no map draws
 * itself, but whose own site is drawn to scale on one, also gets that map (kind
 * `site`): the site is where the detector is, and that is what the map shows.
 */
/**
 * Every local map of a facility, the one its record names first. A facility can
 * have several (JUNO has its campus and its reactor baselines; KM3NeT has ARCA
 * and ORCA), and `map_id` on the record only names one of them.
 */
function mapIdsOfFacility(facilityId) {
  const maps = (ATLAS && ATLAS.maps) || {};
  const facility = ATLAS && ATLAS.facilities && ATLAS.facilities[facilityId];
  const first = facility && facility.map_id;
  return Object.keys(maps)
    .filter((mapId) => maps[mapId].facility_id === facilityId || mapId === first)
    .sort((a, b) => (b === first) - (a === first));
}

// The facilities an experiment runs at: the ones it names, and those of its sites.
function facilityIdsOfExperiment(experiment) {
  const ids = new Set(experiment.facility_ids || []);
  for (const siteId of experiment.site_ids || []) {
    const site = ATLAS.sites && ATLAS.sites[siteId];
    if (site && site.facility_id) ids.add(site.facility_id);
  }
  return [...ids];
}

async function mapDepictions(record) {
  if (!record) return [];
  const maps = (ATLAS && ATLAS.maps) || {};
  const kind = record.id ? record.id.split(':')[0] : '';
  // A facility, or an experiment (which has no map of its own), is linked to
  // every map of its facility; anything else to the map(s) built for it.
  let ids;
  if (kind === 'facility') ids = mapIdsOfFacility(record.id);
  else if (kind === 'experiment') ids = [...new Set(facilityIdsOfExperiment(record).flatMap(mapIdsOfFacility))];
  else ids = record.map_id ? [record.map_id] : (record.geometry_map_ids || []);
  const rows = [];
  for (const mapId of ids.filter((id) => maps[id])) {
    // A facility is the map's host, not a feature on it.
    const how = kind === 'facility' || kind === 'experiment' ? 'host' : await depictionOn(mapId, record.id);
    rows.push({ mapId, meta: maps[mapId], how });
  }
  if (record.id && record.id.startsWith('detector:') && !rows.some((row) => row.how === 'drawn')) {
    for (const placement of record.placements || []) {
      const site = placement.site_id && ATLAS.sites[placement.site_id];
      if (!site || !site.map_id || !maps[site.map_id] || rows.some((row) => row.mapId === site.map_id && row.how === 'site')) continue;
      if (await depictionOn(site.map_id, site.id) === 'drawn') {
        rows.push({ mapId: site.map_id, meta: maps[site.map_id], how: 'site' });
      }
    }
  }
  // What is drawn to scale first, then what is only a direction or not drawn.
  const rank = { host: 0, drawn: 0, site: 1, none: 2, unknown: 3, direction: 4 };
  return rows.sort((a, b) => rank[a.how] - rank[b.how]);
}

/**
 * The "Open local map" affordance for any record the build has linked to a
 * local map. Returns null when the build linked none, so a caller can append it
 * unconditionally and nothing appears for a facility whose campus has not been
 * mapped yet — which means "not researched", not "has no layout". What each
 * row says about the map depends on how that map really depicts the record
 * (see mapDepictions): a direction line is never described as drawn to scale.
 */
export async function localMapLinks(record) {
  const rows = await mapDepictions(record);
  if (!rows.length) return null;
  const noun = record.id ? record.id.split(':')[0] : 'record';
  const items = rows.map(({ mapId, meta, how }) => {
    const drawn = `${meta.to_scale_count} feature${meta.to_scale_count === 1 ? '' : 's'} drawn to scale`;
    const unlocated = meta.unlocated_count
      ? ` \u00b7 ${meta.unlocated_count} not drawn (geometry not verified)` : '';
    const note = {
      direction: noun === 'beamline'
        ? 'Draws only an inferred beam direction \u2014 a bearing, not to scale'
        : `Draws only an inferred direction toward this ${noun} \u2014 a bearing, not to scale`,
      none: `This map covers its area, but nothing is drawn for this ${noun} (geometry not verified)`,
      site: 'Its site is drawn to scale on this map',
    }[how] || `${drawn}${unlocated}`;
    return h('li', { class: 'entity-link-with-meta' }, [
      linkTo(idRoute(mapId), `Open local map \u2014 ${meta.name}`, 'local-map-link'),
      h('div', { class: 'source-meta' }, note),
    ]);
  });
  return section('Local map', [h('ul', { class: 'entity-list' }, items)]);
}

/**
 * The same affordance as one compact line for a panel's subtitle area, so a
 * reader looking at a site, accelerator, beamline or detector sees how it
 * appears on a local map before scrolling. "Shown to scale" is said only when a
 * surveyed, georeferenced or derived feature depicts the record; an inferred
 * direction line, a covered-but-undrawn area and an unreadable bundle each have
 * their own wording. Returns null when the build linked none.
 */
export async function localMapChip(record) {
  const rows = await mapDepictions(record);
  if (!rows.length) return null;
  const noun = record.id ? record.id.split(':')[0] : 'record';
  // One row, one chip per line: the sentences are long, and two of them run
  // together with a dot between read as one.
  const wrap = h('p', { class: 'panel-subtitle local-map-chip-row' });
  rows.forEach(({ mapId, meta, how }, i) => {
    if (i) wrap.appendChild(h('br'));
    const text = {
      drawn: `\u25ce Shown to scale on the ${meta.name} local map`,
      site: `\u25ce Its site is shown to scale on the ${meta.name} local map`,
      direction: noun === 'beamline'
        ? `\u25ce Beam direction drawn on the ${meta.name} map (an inferred bearing, not to scale)`
        : `\u25ce Direction toward this ${noun} drawn on the ${meta.name} map (an inferred bearing, not to scale)`,
      none: `\u25ce Within the ${meta.name} local map \u2014 not drawn there`,
    }[how] || `\u25ce On the ${meta.name} local map`;
    wrap.appendChild(linkTo(idRoute(mapId), text, 'local-map-chip'));
  });
  return wrap;
}
// ---- local map view hook -- end ----------------------------------------

// Renders the status pill from the entity's per-year `state_segments` at the
// currently selected timeline position, never from its static build-time
// `status` — the globe's own markers already do this (model.js's
// statusAtMonth/statusInRange), and the panel must agree with them instead
// of showing a frozen, potentially anachronistic label (e.g. an experiment
// reading "Active" at a year decades before it existed).
function experimentBadge(record, timelineState) {
  const segments = record.state_segments;
  const resolved = statusForTimeline(segments, timelineState);
  const when = timelineState && timelineState.range
    ? `${timelineState.range[0]}–${timelineState.range[1]}`
    : String((timelineState && timelineState.year) || '');
  if (resolved) {
    const label = titleCase(resolved.status) + (resolved.certainty === 'possible' ? ' (uncertain)' : '');
    return h('div', { class: `status-badge status-${resolved.status}` }, label);
  }
  const reason = timelineAbsenceReason(segments, timelineState || {});
  const text = {
    not_yet: `Not yet proposed in ${when}`,
    ended: `No longer active in ${when}`,
    gap: `No recorded status in ${when}`,
    no_history: 'No timeline data recorded for this entity',
  }[reason] || 'No timeline data recorded for this entity';
  return h('div', { class: 'status-badge is-outside-timeline' }, text);
}

// ------------------------------------------------------------------ facility
async function renderFacility(id, timelineState) {
  const facility = ATLAS.facilities[id];
  if (!facility) return emptyNote('Unknown facility.');
  const text = await loader.getText();
  const t = text[id] || {};

  const experiments = (facility.experiment_ids || []).map((eid) => ATLAS.experiments[eid]).filter(Boolean);
  const current = experiments.filter((e) => statusEra(e.status) === 'current');
  const historical = experiments.filter((e) => statusEra(e.status) === 'historical');
  const future = experiments.filter((e) => statusEra(e.status) === 'future');

  const { list: allResults } = await loader.getResults();
  const { list: allDocuments } = await loader.getDocuments();
  const results = allResults.filter((r) => (r.facility_ids || []).includes(id));
  const documents = allDocuments.filter((d) => (d.owner_ids || []).includes(id)
    || (facility.document_ids || []).includes(d.id));

  const frag = document.createDocumentFragment();
  const sections = panelSections(frag);
  frag.appendChild(h('h2', {}, facility.name));
  frag.appendChild(h('p', { class: 'panel-subtitle' }, kindLabel(facility.kind)));
  frag.appendChild(experimentBadge(facility, timelineState));
  if (facility.kind === 'underground_laboratory') {
    const chartLink = undergroundCta(facility);
    if (chartLink) frag.appendChild(chartLink);
  }

  const facilitySummary = plainSummaryOf(facility, t);
  sections.add('Overview', [
    facilitySummary ? h('p', {}, facilitySummary) : null,
    keyValueList([
      ['Aliases', (facility.aliases || []).join(', ')],
      // Generated bundle: `operator_text` (no `operator` field at all).
      // Fixtures: `operator` (no `operator_text`). Read whichever exists.
      ['Operator', facility.operator_text || facility.operator],
      ['Country', (facility.country || []).join(', ')],
    ]),
  ], { missing: [!facilitySummary && 'Plain-language summary'] });

  const specRows = Object.entries(facility.specs || {}).map(([k, v]) => [titleCase(k), quantityText(v)]);
  sections.add('Technical information', keyValueList(specRows), { open: false });

  sections.add('Current experiments', recordLinks(current));
  sections.add('Historical experiments', recordLinks(historical), { open: false });
  sections.add('Future / planned experiments', recordLinks(future), { open: false });
  sections.add('Results', resultLinks(results), { open: false });
  sections.add('Documents', documentLinks(documents), { open: false });

  const links = Object.entries(facility.links || {}).filter(([, v]) => v);
  sections.add('Official links', links.length
    ? h('ul', { class: 'entity-list' }, links.map(([k, v]) => h('li', {}, h('a', { href: v, target: '_blank', rel: 'noopener' }, `${titleCase(k)}: ${v}`))))
    : null, { open: false });

  const related = (facility.related_facility_ids || []).map((rid) => ATLAS.facilities[rid]).filter(Boolean);
  sections.add('Related facilities', recordLinks(related), { open: false });

  // ---- local map view hook (§4): only the facility renderer calls it for
  // now; the site/accelerator/beamline/detector renderers can append the
  // same element when they land.
  const mapSection = await localMapLinks(facility);
  if (mapSection) frag.appendChild(mapSection);

  sections.note();
  frag.appendChild(sourcesDisclosure(id, facility));
  CALLBACKS.focusGlobe(id);
  return frag;
}

// ---- "Beam through the Earth" (js/views/beam-section.js) ---------------------
// A baseline row is a drawable cross-section of the Earth, so every beamline panel,
// and every experiment panel whose far detector a baseline reaches, links to it, one
// link per row. The numbers in the hint are the view's own (views/beam-rows.js and
// beam-geometry.js), computed from the two recorded coordinates; the view shows
// their formulas, inputs and uncertainty. Pure arithmetic: nothing is fetched here.
function beamSectionHint(row) {
  const { geometry } = rowGeometry(row);
  const distance = row.baseline.distance ? row.baseline.distance.display : '';
  return [distance, `dips ${geometry.dipDeg.toFixed(1)}\u00b0 below the horizon`,
    `${geometry.sagittaKm.toFixed(1)} km deep at mid-path`]
    .filter(Boolean).join(' \u00b7 ');
}

function beamSectionRoute(row) {
  return { type: 'view', slug: `${VIEW_NAME}/${row.arg}` };
}

// The beamline panel's call to action: a card, one prominent link per baseline row.
function beamSectionCta(rows) {
  const route = (row) => beamSectionRoute(row);
  return h('div', { class: 'beam-section-cta' }, [
    h('p', { class: 'beam-section-cta-kicker' }, 'See the physics'),
    ...rows.map((row) => {
      const a = h('a', {
        class: 'beam-section-link',
        href: `#/${route(row).type}/${route(row).slug}`,
      }, [
        h('span', { class: 'beam-section-link-title' }, rows.length > 1 ? `${WORKING_TITLE}: ${row.label}` : WORKING_TITLE),
        h('span', { class: 'beam-section-link-hint' }, `${row.label} \u00b7 ${beamSectionHint(row)}`),
      ]);
      a.addEventListener('click', (event) => {
        if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        CALLBACKS.navigate({ entity: route(row) });
      });
      return a;
    }),
  ]);
}

// The experiment panel's quieter line: the same links, in running text.
function beamSectionLinkLine(rows) {
  return h('p', { class: 'beam-section-links' }, [
    'See the physics: ',
    ...rows.flatMap((row, i) => [
      i ? document.createTextNode(' \u00b7 ') : null,
      linkTo(beamSectionRoute(row), `${WORKING_TITLE}: ${row.label}`),
    ]),
  ]);
}

// ---- "Going underground" and "The energy frontier" (js/views/underground.js, energy-frontier.js) ----
// A card like the beam section's, in the chart's tone: the facility panel of an underground laboratory
// links to the chart of depth against muon flux, an accelerator panel to the chart of energy against
// year. The hints are the views' own numbers (views/underground-rows.js, frontier-rows.js), read from
// atlas.json with nothing fetched; a record the chart cannot place says so instead of linking blindly.
function chartCta(route, title, hint) {
  const a = h('a', { class: 'chart-link', href: `#/${route.type}/${route.slug}` }, [
    h('span', { class: 'chart-link-title' }, title),
    hint ? h('span', { class: 'chart-link-hint' }, hint) : null,
  ]);
  a.addEventListener('click', (event) => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    CALLBACKS.navigate({ entity: route });
  });
  return h('div', { class: 'chart-cta' }, [h('p', { class: 'chart-cta-kicker' }, 'See the physics'), a]);
}

function undergroundCta(facility) {
  const rows = underground.rowsForFacility(ATLAS, facility.id);
  const depthOnly = underground.depthOnlyRows(ATLAS).filter((row) => row.site.facility_id === facility.id);
  if (!rows.length && !depthOnly.length) return null;
  let hint;
  if (rows.length === 1) hint = `${rows[0].depthQuantity.display} \u00b7 muon flux ${underground.fluxText(rows[0].flux)}`;
  else if (rows.length > 1) hint = `${rows.length} sites on the chart: ${rows.map((row) => row.label).sort().join(', ')}`;
  else hint = `Depth recorded (${depthOnly[0].depthQuantity.display}); no muon flux, so no marker`;
  return chartCta({ type: 'view', slug: underground.VIEW_NAME }, underground.WORKING_TITLE, hint);
}

function frontierCta(accelerator) {
  if (!frontier.frontierRows(ATLAS).length) return null;
  const entry = frontier.frontierFor(ATLAS, accelerator.id);
  if (!entry) return null;
  let hint;
  if (entry.plotted) {
    const row = entry.plotted;
    const quantity = row.collider ? '\u221as' : 'beam energy';
    const steps = row.points.filter((point) => point.kind === 'era');
    hint = steps.length > 1
      ? `${quantity}: ${steps.map((point) => `${frontier.energyText(point.gev)} (${point.year})`).join(' \u2192 ')}`
      : `${frontier.energyText(row.points[0].gev)} ${quantity}${row.points[0].kind === 'today' ? ', as recorded today' : ` from ${row.points[0].year}`} \u00b7 began operating ${row.first.year}`;
  } else {
    hint = `Not plotted: ${entry.skipped.reason}`;
  }
  return chartCta({ type: 'view', slug: frontier.VIEW_NAME }, frontier.WORKING_TITLE, hint);
}

// ---- distance between an experiment's sites ------------------------------
// formatDistance/compassPoint mirror the local map view's own "off-campus
// destination" rows (which compute the same great-circle figures with the same
// two exported helpers), so a distance read here and on the map agree.
function formatDistance(metres) {
  if (metres >= 10000) return `${Math.round(metres / 1000)} km`;
  if (metres >= 1000) return `${(metres / 1000).toFixed(1)} km`;
  return `${Math.round(metres)} m`;
}

function compassPoint(bearing) {
  const names = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
    'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
  return names[Math.round(bearing / 22.5) % 16];
}

/**
 * Where two sites of one experiment lie from each other: great-circle distance
 * and the initial bearing, with links to the local maps of both ends (DUNE:
 * Fermilab to the SURF 4850 Level, 1285 km away, to the west-north-west). Shown
 * for every pair of the experiment's sites that have coordinates; an
 * experiment has at most three, so this is at most three short lines. The pair
 * is oriented along the beam when a beamline names one site as near and the
 * other as far (or as a baseline), otherwise in the order the record lists the
 * sites. Returns null with fewer than two located sites.
 */
function siteDistances(sites, beamlines) {
  const located = sites.filter((s) => s.lat != null && s.lon != null);
  if (located.length < 2) return null;
  const along = (from, to) => beamlines.some((b) => (
    ((b.near_detector_site_ids || []).includes(from.id) && (b.far_detector_site_ids || []).includes(to.id))
    || (b.baselines || []).some((base) => base.from_site_id === from.id && base.to_site_id === to.id)));
  const pairs = [];
  for (let i = 0; i < located.length; i += 1) {
    for (let j = i + 1; j < located.length; j += 1) {
      let [from, to] = [located[i], located[j]];
      if (along(to, from) && !along(from, to)) [from, to] = [to, from];
      const a = [from.lat, from.lon];
      const b = [to.lat, to.lon];
      pairs.push({ from, to, metres: greatCircleM(a, b), bearing: initialBearing(a, b) });
    }
  }
  pairs.sort((x, y) => x.metres - y.metres);
  const maps = (ATLAS && ATLAS.maps) || {};
  const placeName = (site, other) => {
    const facility = site.facility_id && ATLAS.facilities[site.facility_id];
    const otherFacility = other.facility_id && ATLAS.facilities[other.facility_id];
    return facility && facility !== otherFacility ? facility.name : site.name;
  };
  const items = pairs.map(({ from, to, metres, bearing }) => {
    const approximate = [from, to].some((s) => s.coordinates && s.coordinates.approximate);
    const mapIds = [...new Set([from, to].map((s) => s.map_id).filter((id) => id && maps[id]))];
    // A campus-grade coordinate is good to a few kilometres, so a figure
    // between two such points is not quoted to the metre (1288 km would sit
    // beside the beamline's own 1285 km as a disagreement it is not).
    const shown = approximate && metres >= 100000 ? Math.round(metres / 10000) * 10000 : metres;
    return h('li', { class: 'entity-link-with-meta' }, [
      `${placeName(from, to)} \u2192 ${placeName(to, from)}: ${approximate ? '\u2248 ' : ''}${formatDistance(shown)}, `
        + `bearing ${bearing.toFixed(0)}\u00b0 (${compassPoint(bearing)})`,
      mapIds.length ? h('div', { class: 'source-meta' }, [
        mapIds.length === 1 ? 'Local map: ' : 'Local maps: ',
        ...mapIds.flatMap((mapId, i) => [
          i ? document.createTextNode(' \u00b7 ') : null,
          linkTo(idRoute(mapId), maps[mapId].name, 'local-map-link'),
        ]),
      ]) : null,
    ]);
  });
  return h('div', { class: 'site-distances' }, [
    h('h4', {}, 'Distance between sites'),
    h('ul', { class: 'entity-list' }, items),
    h('p', { class: 'source-meta' }, [
      'Great-circle distance and initial bearing between the recorded site coordinates',
      pairs.some((p) => [p.from, p.to].some((s) => s.coordinates && s.coordinates.approximate))
        ? '; \u2248 marks a campus-grade (approximate) coordinate, so that distance is rounded to 10 km.' : '.',
    ]),
  ]);
}

// ---------------------------------------------------------------- experiment
async function renderExperiment(id, timelineState) {
  const exp = ATLAS.experiments[id];
  if (!exp) return emptyNote('Unknown experiment.');
  const text = await loader.getText();
  const t = text[id] || {};

  const frag = document.createDocumentFragment();
  const sections = panelSections(frag);
  frag.appendChild(h('h2', {}, exp.name));
  frag.appendChild(h('p', { class: 'panel-subtitle' }, kindLabel(exp.kind)));
  frag.appendChild(experimentBadge(exp, timelineState));

  const collabs = (exp.collaboration_ids || []).map((cid) => ATLAS.collaborations[cid]).filter(Boolean);
  if (collabs.length) {
    frag.appendChild(h('p', { class: 'collab-line' }, [
      'Collaboration: ',
      ...collabs.flatMap((c, i) => (i === 0 ? [linkTo(idRoute(c.id), c.name, 'collab-link')] : [document.createTextNode(', '), linkTo(idRoute(c.id), c.name, 'collab-link')])),
    ]));
  }

  const experimentBeamRows = rowsForExperiment(ATLAS, exp);
  if (experimentBeamRows.length) frag.appendChild(beamSectionLinkLine(experimentBeamRows));

  const expPlainSummary = plainSummaryOf(exp, t);
  sections.add('What it studies', [
    expPlainSummary ? h('p', { class: 'plain-summary' }, expPlainSummary) : null,
    exp.topic_ids && exp.topic_ids.length
      ? h('p', {}, ['Research topics: ', ...exp.topic_ids.flatMap((tid, i) => {
        const topic = ATLAS.topics[tid];
        const link = topic ? linkTo(idRoute(tid), topic.name) : document.createTextNode(tid);
        return i === 0 ? [link] : [document.createTextNode(', '), link];
      })])
      : null,
  ], { missing: [!expPlainSummary && 'Plain-language summary'] });

  const keySpecRows = (exp.key_specs || []).map((s) => [s.label, quantityText(s.quantity)]);
  sections.add('Key specifications', keyValueList(keySpecRows));

  sections.add('Full technical section', [
    t.summary_technical ? h('p', {}, t.summary_technical) : null,
    keyValueList([
      ['Energy regime', exp.energy_regime],
      ['External IDs', exp.external ? Object.entries(exp.external).filter(([, v]) => v).map(([k, v]) => `${k}: ${v}`).join(' · ') : ''],
    ]),
  ], { open: false, missing: [!t.summary_technical && 'Technical summary'] });

  const detectors = (exp.detector_ids || []).map((did) => ATLAS.detectors[did]).filter(Boolean);
  sections.add('Detectors', recordLinks(detectors));

  const beamlines = (exp.beamline_ids || []).map((bid) => ATLAS.beamlines[bid]).filter(Boolean);
  const sites = (exp.site_ids || []).map((sid) => ATLAS.sites[sid]).filter(Boolean);
  // A23: an admitted-approximate site coordinate (a campus point standing
  // in for a real hall position no fetched source gives) must say so
  // wherever it's shown, and must never read as the detector's own
  // position — so the location line names the coordinate's kind instead of
  // silently reusing the same "(setting)" phrasing a real detector point gets.
  const approximateSites = sites.filter((s) => s.coordinates && s.coordinates.approximate);
  sections.add('Beam and sites', [
    beamlines.length ? h('ul', { class: 'entity-list' }, beamlines.map((b) => {
      const distances = (b.baselines || []).map((base) => (base.distance ? base.distance.display : '')).filter(Boolean);
      return h('li', {}, distances.length ? `${b.name}: ${distances.join(', ')}` : b.name);
    })) : null,
    sites.length ? h('ul', { class: 'entity-list' }, sites.map((s) => h('li', {}, [
      linkTo({ type: 'facility', slug: (s.facility_id || s.id).split(':')[1] }, `${s.name} (${s.setting})`),
      siteLocationNote(s),
    ]))) : null,
    siteDistances(sites, beamlines),
  ], { open: false });

  const { byId: resultById } = await loader.getResults();
  const results = (exp.result_ids || []).map((rid) => resultById.get(rid)).filter(Boolean)
    .sort((a, b) => (a.month || 0) - (b.month || 0));
  // Task A5: an experiment that hasn't started operating yet has no results
  // *because there is nothing to report yet* — a scientifically meaningful
  // absence, not a curation gap — so the closing note names it as such
  // instead of leaving it among the sections the Atlas simply has not filled.
  const notYetOperating = statusEra(exp.status) === 'future';
  sections.add('Results timeline', results.length
    ? h('ol', { class: 'entity-list timeline-list' }, results.map((r) => h('li', {}, [
      h('span', { class: 'result-date' }, r.date || String(r.year || '')),
      ' ',
      linkTo(idRoute(r.id), r.name || r.title),
    ])))
    : null, { open: false, label: notYetOperating ? 'Results (not yet operating, none expected)' : 'Results' });

  const { byId: docById } = await loader.getDocuments();
  const documents = (exp.document_ids || []).map((did) => docById.get(did)).filter(Boolean);
  sections.add('Documents', documentLinks(documents), { open: false });

  const predecessors = (exp.lineage || []).filter((l) => ['predecessor', 'upgrade_of'].includes(l.relation));
  const successors = (exp.lineage || []).filter((l) => ['successor', 'upgraded_to'].includes(l.relation));
  const others = (exp.lineage || []).filter((l) => !predecessors.includes(l) && !successors.includes(l));
  function lineageList(rows) {
    return rows.length
      ? h('ul', { class: 'entity-list' }, rows.map((l) => {
        const other = ATLAS.experiments[l.experiment_id];
        return h('li', {}, [other ? linkTo(idRoute(l.experiment_id), other.name) : document.createTextNode(l.experiment_id), ` (${l.relation.replace(/_/g, ' ')})`]);
      }))
      : null;
  }
  sections.groups('Predecessors and successors', [
    ['Predecessors', lineageList(predecessors)],
    ['Successors', lineageList(successors)],
    ['Related programs', lineageList(others)],
  ], { open: false, optional: ['Related programs'] });

  // The local maps of the facility it runs at (every one of them).
  const mapSection = await localMapLinks(exp);
  if (mapSection) frag.appendChild(mapSection);

  sections.note();
  frag.appendChild(sourcesDisclosure(id, exp, { approximateSites }));
  CALLBACKS.focusGlobe(id);
  return frag;
}

// ------------------------------------------------------------- collaboration
// What the roster's rows are, by `evidence_class`, for a roster none of whose
// rows is individually dated: an official list of member institutions, or the
// affiliations printed on a paper. Any other class is named by its own label.
const ROSTER_ROW_WORDS = {
  official_institution_list: (n, asOf) => `${n} institutions on the official list${asOf}, not individually dated`,
  publication_affiliation_current: (n, asOf) => `${n} institutions listed on a collaboration paper${asOf}; `
    + 'current membership not confirmed, not individually dated. The full membership is larger',
};

// The headline over a roster. A roster whose rows carry dates is counted as
// confirmed and undated members. One whose rows carry none (`counts` all zero)
// is not "0 confirmed institutions": it has a list, and the sentence says what
// kind of list it is and that nothing on it is dated.
function rosterCountLabel(membership) {
  const counts = membership.counts || {};
  const confirmed = counts.confirmed || 0;
  const undated = counts.undated || 0;
  const asOf = membership.as_of ? ` as of ${membership.as_of}` : '';
  const history = membership.membership_history;
  const rows = membership.members || [];
  if (confirmed + undated === 0) {
    if (!rows.length) return 'No institutions are listed in the Atlas roster for this collaboration yet';
    const byClass = new Map();
    for (const row of rows) {
      const key = row.evidence_class || row.evidence_label || 'unspecified';
      byClass.set(key, [...(byClass.get(key) || []), row]);
    }
    return [...byClass].map(([key, group]) => {
      const words = ROSTER_ROW_WORDS[key];
      return words ? words(group.length, asOf)
        : `${group.length} institutions on the roster${asOf} (${group[0].evidence_label || key}), not individually dated`;
    }).join('; ');
  }
  return (history === 'partial' || history === 'unknown')
    ? `Partial roster: ${confirmed} confirmed institutions (+${undated} undated)${asOf}; the full membership is larger`
    : `${confirmed} confirmed institutions (+${undated} undated)${asOf}`;
}

async function renderCollaboration(id, timelineState) {
  const collab = ATLAS.collaborations[id];
  if (!collab) return emptyNote('Unknown collaboration.');
  const text = await loader.getText();
  const t = text[id] || {};
  const host = collab.host_facility_id && ATLAS.facilities[collab.host_facility_id];

  const frag = document.createDocumentFragment();
  const sections = panelSections(frag);
  frag.appendChild(h('h2', {}, collab.name));
  frag.appendChild(experimentBadge(collab, timelineState));

  const summary = plainSummaryOf(collab, t)
    || `Formed ${collab.formation || 'at an unrecorded date'}${host ? `, hosted at ${host.name}` : ''}.`;
  sections.add('Summary', h('p', {}, summary));

  sections.add('Host facility', host ? linkTo(idRoute(host.id), host.name) : null);

  // The collaboration record's own `membership` block does not carry a
  // confirmed-member count (only institution_count / country_count / as_of
  // headline stats) — the actual roster counts, split into confirmed and
  // undated per ontology amendment A5, live in the membership bundle itself.
  // The loader answers `null` for a collaboration the build wrote no roster
  // for (manifest.json does not list it — 119 of 122 today): that is not the
  // same absence as a roster that exists but is only partially researched, so
  // the two stay distinct instead of collapsing both into "0 members" or a
  // stale count. A listed roster that fails to load is an error, and renders
  // as one (render()'s catch), never as an empty roster.
  const membership = await loader.getMembership(id);

  const viewBtn = h('button', { type: 'button', id: 'view-on-globe', class: 'primary-btn' }, 'View collaboration on globe');
  if (membership && (membership.members || []).length) {
    viewBtn.addEventListener('click', () => CALLBACKS.viewOnGlobe(id));
  } else {
    viewBtn.disabled = true;
    viewBtn.setAttribute('aria-disabled', 'true');
    viewBtn.title = 'No institution roster curated yet for this collaboration.';
  }
  frag.appendChild(h('div', { class: 'panel-actions' }, viewBtn));

  let membershipMembers = null;
  if (!membership) {
    // The reason the button above is disabled, in text a reader can see (a
    // title attribute is invisible on a phone and to most keyboard users).
    frag.appendChild(emptyNote('Institution roster not yet curated for this collaboration.'));
  } else {
    sections.add('Membership', [
      h('p', { class: 'membership-count' }, rosterCountLabel(membership)),
      keyValueList([
        ['Institutions (collaboration’s own count)', collab.membership && collab.membership.institution_count],
        ['Countries (collaboration’s own count)', collab.membership && collab.membership.country_count],
        ['As of', collab.membership && collab.membership.as_of],
      ]),
    ]);
    // `/members/N` provenance pointers index the roster's *authored* file
    // order (`source_index`), not this display-sorted `members` array — see
    // build.py's `_membership_row` and docs/HEP_ATLAS_BUNDLES.md.
    membershipMembers = [];
    for (const row of membership.members || []) {
      if (typeof row.source_index === 'number') membershipMembers[row.source_index] = row;
    }
  }

  sections.note();
  frag.appendChild(sourcesDisclosure(id, collab, { membershipMembers }));
  return frag;
}

// -------------------------------------------------------------- institution
const ROLE_FILTERS = [
  { id: 'all', label: 'All' },
  { id: 'faculty_permanent', label: 'Faculty and permanent staff' },
  { id: 'postdocs', label: 'Postdocs' },
  { id: 'students', label: 'Students' },
  { id: 'unknown', label: 'Unknown' },
];

async function renderInstitution(id) {
  const institutions = await loader.getInstitutions();
  const institution = institutions[id];
  if (!institution) return emptyNote('Unknown institution.');

  const frag = document.createDocumentFragment();
  const sections = panelSections(frag);
  frag.appendChild(h('h2', {}, institution.name));
  frag.appendChild(h('p', { class: 'panel-subtitle' }, [
    titleCase(institution.kind), institution.place ? ` · ${institution.place.city}, ${institution.place.country}` : '',
  ].join('')));

  const collabId = (institution.collaboration_ids || []).includes(lastCollaborationId)
    ? lastCollaborationId
    : (institution.collaboration_ids || [])[0];

  if (!collabId) {
    frag.appendChild(emptyNote('No collaboration membership recorded in the Atlas for this institution.'));
    return frag;
  }

  const membership = await loader.getMembership(collabId);
  const row = membership ? (membership.members || []).find((m) => m.institution_id === id) : null;
  const collab = ATLAS.collaborations[collabId];

  sections.add(`Membership in ${collab ? collab.name : collabId}`, [
    row ? h('p', { class: 'evidence-label' }, row.evidence_label) : null,
    row && row.note ? h('p', { class: 'membership-note' }, row.note) : null,
  ]);

  const peopleSection = h('div', { class: 'people-section' });
  const peopleList = h('ul', { class: 'people-list', id: 'people-list' });

  let people = [];
  if (row && row.people_bundle) {
    // `null` when the manifest does not list the bundle the row points at.
    const bundle = await loader.getPeople(row.people_bundle);
    people = (bundle && bundle.people) || [];
  }

  // The role-filter buttons only mean anything when the people bundle
  // actually carries a `role_group` per person — the generated bundle
  // currently never does (only the dev fixtures do), so showing four
  // buttons that all silently return "no people" except "All" would be its
  // own false statement. Only wire the filter row up when it can work.
  const hasRoleData = people.some((p) => p.role_group);
  const filterRow = hasRoleData
    ? h('div', { class: 'role-filter', role: 'group', 'aria-label': 'Filter by role' },
      ROLE_FILTERS.map((f) => h('button', { type: 'button', class: `role-btn${f.id === 'all' ? ' is-active' : ''}`, 'data-role': f.id }, f.label)))
    : null;
  peopleSection.append(...(filterRow ? [filterRow, peopleList] : [peopleList]));

  function renderPeople(filter) {
    peopleList.innerHTML = '';
    const filtered = filter === 'all' ? people : people.filter((p) => p.role_group === filter);
    if (!filtered.length) {
      peopleList.appendChild(h('li', { class: 'empty-note' }, 'No people recorded in the Atlas for this filter.'));
      return;
    }
    for (const person of filtered) {
      const li = h('li', {}, [
        h('span', { class: 'person-name' }, person.name),
        // `role` isn't part of the real bundle's person records at all (see
        // above) — only show it when a value actually exists, rather than a
        // dangling " — " with nothing after the separator.
        person.role ? h('span', { class: 'person-role' }, ` — ${titleCase(person.role)}`) : null,
        h('div', { class: 'person-evidence' }, person.evidence_label),
      ]);
      if (person.hep_graph && person.hep_graph.available && person.hep_graph.url) {
        li.appendChild(h('a', { href: person.hep_graph.url, target: '_blank', rel: 'noopener', class: 'hep-graph-link' }, 'Open in HEP Graph'));
      }
      peopleList.appendChild(li);
    }
  }
  if (filterRow) {
    filterRow.addEventListener('click', (event) => {
      const btn = event.target.closest('.role-btn');
      if (!btn) return;
      for (const b of filterRow.querySelectorAll('.role-btn')) b.classList.toggle('is-active', b === btn);
      renderPeople(btn.dataset.role);
    });
  }
  renderPeople('all');

  sections.add(`People (${people.length})`, people.length ? peopleSection : null, {
    label: (row && row.people_count)
      ? `People (${row.people_count} recorded, not yet resolved to named records)` : 'People',
  });

  sections.note();
  return frag;
}

// -------------------------------------------------------------------- topic
async function renderTopic(id) {
  const topic = ATLAS.topics[id];
  if (!topic) return emptyNote('Unknown topic.');
  const text = await loader.getText();
  const t = text[id] || {};

  const frag = document.createDocumentFragment();
  const sections = panelSections(frag);
  frag.appendChild(h('h2', {}, topic.name));
  frag.appendChild(h('p', { class: 'plain-question' }, topic.question || ''));
  if (t.overview) frag.appendChild(h('p', {}, t.overview));

  sections.add('Observables', topic.observables && topic.observables.length
    ? h('ul', { class: 'entity-list' }, topic.observables.map((o) => h('li', {}, o)))
    : null);

  // `topic.experiment_ids` / `topic.result_ids` are not derived fields in
  // the generated bundle (unlike facility/experiment/collaboration, topics
  // get no inverse relation at build time — see docs/HEP_ATLAS_BUNDLES.md's
  // list of derived inverse lists, which does not include topic). The link
  // does exist the other way round (`experiment.topic_ids`, `result.topic_ids`),
  // so resolve it here instead of reading a field that is always undefined.
  const experiments = Object.values(ATLAS.experiments || {}).filter((e) => (e.topic_ids || []).includes(id));
  const current = experiments.filter((e) => statusEra(e.status) === 'current');
  const historical = experiments.filter((e) => statusEra(e.status) === 'historical');
  const future = experiments.filter((e) => statusEra(e.status) === 'future');
  sections.groups('Experiments', [
    ['Current', recordLinks(current), 'Current experiments'],
    ['Historical', recordLinks(historical), 'Historical experiments'],
    ['Future / planned', recordLinks(future), 'Future / planned experiments'],
  ]);

  const { list: allResults } = await loader.getResults();
  const results = allResults.filter((r) => (r.topic_ids || []).includes(id));
  // Physics results first. A technology milestone (a cavern excavated, a
  // prototype's performance, a luminosity record) belongs to the topic's
  // instruments, not to what the topic has found, so it follows under its own
  // heading instead of sitting among the findings.
  const milestones = results.filter((r) => r.result_type === 'technology_milestone');
  const physics = results.filter((r) => r.result_type !== 'technology_milestone');
  sections.add('Related results', [
    resultLinks(physics),
    milestones.length ? h('h4', {}, 'Technology milestones') : null,
    resultLinks(milestones),
  ], { open: false, label: 'Related results' });

  sections.note();
  return frag;
}

// ------------------------------------------------------------------- result
// Lower-case letters and digits only, so a quote and a title compare equal
// despite TeX, typesetting, hyphens or case.
function plainKey(text) {
  return readableText(text).normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]+/gu, '');
}

// What the verbatim claim is called ("From the abstract"), from the claim's
// `locator` (where in the source it was read). null when the quote should not
// be shown under the lede: it is the paper's title, which the page already
// carries. `always` keeps it even then (no plain-language summary to lead with).
function claimExcerptLabel(result, quote, locator, always) {
  const where = String(locator || '').toLowerCase();
  const titleOnly = /\btitle\b/.test(where) && !/\babstract\b/.test(where);
  const key = plainKey(quote);
  const isTitle = titleOnly || [result.title, result.name].some((title) => title && plainKey(title) === key);
  if (isTitle && !always) return null;
  if (isTitle) return 'From the paper\u2019s title';
  return /\babstract\b/.test(where) ? 'From the abstract' : 'From the paper';
}

async function renderResult(id) {
  const { byId } = await loader.getResults();
  const result = byId.get(id);
  if (!result) return emptyNote('Unknown result.');
  const text = await loader.getText();
  const t = text[id] || {};

  const frag = document.createDocumentFragment();
  const sections = panelSections(frag);
  // The heading is the Atlas's own name (typeset notation); the paper's title
  // is kept verbatim underneath when it differs, as it was published.
  frag.appendChild(h('h2', {}, result.name || result.title));
  frag.appendChild(h('p', { class: 'panel-subtitle' }, `${titleCase(result.result_type)} · ${fmtDate(result.date)}`));
  if (result.title && result.name && result.title !== result.name) {
    frag.appendChild(h('p', { class: 'source-meta' }, ['Paper title: ', readableView(result.title)]));
  }
  // The lede is the Atlas's own plain-language summary. The paper's wording of
  // the claim follows under a label that says where it was taken from, so it
  // reads as an excerpt and not as the Atlas speaking; a quote that is only the
  // paper's title is not repeated (the title is already on the page).
  const lede = plainSummaryOf(result, t);
  if (lede) frag.appendChild(h('p', { class: 'plain-summary result-lede' }, lede));
  const claim = (t.claim && t.claim.quote) || (result.claim && result.claim.quote) || '';
  const locator = (t.claim && t.claim.locator) || (result.claim && result.claim.locator) || '';
  const excerpt = claim && claimExcerptLabel(result, claim, locator, !lede);
  if (excerpt) {
    frag.appendChild(h('p', { class: 'result-excerpt' }, [
      h('span', { class: 'excerpt-label' }, `${excerpt}: `),
      quoteView(claim),
    ]));
  }
  // The bundle carries one `date` plus a `date_kind` ("announcement" |
  // "preprint" | "publication"), not separate `announced` / `published`
  // fields — those never exist on a real result record, so this used to
  // silently drop both rows every time.
  const facts = keyValueList([
    ['Significance', result.significance],
    ['Key value', result.key_value_text],
    [titleCase(result.date_kind) || 'Date', fmtDate(result.date)],
  ]);
  if (facts) frag.appendChild(facts);
  // Where it was done: the facility records the result names, each with its
  // local map when the Atlas has drawn one (an absent link means not mapped yet).
  const facilities = (result.facility_ids || []).map((fid) => ATLAS.facilities[fid]).filter(Boolean);
  if (facilities.length) {
    const maps = (ATLAS && ATLAS.maps) || {};
    frag.appendChild(h('p', { class: 'result-where' }, [
      h('strong', {}, 'Where: '),
      ...facilities.flatMap((facility, i) => [
        i ? document.createTextNode(', ') : null,
        linkTo(idRoute(facility.id), facility.name),
        // One map reads "local map"; a facility with several names each.
        (() => {
          const mapIds = mapIdsOfFacility(facility.id).filter((mapId) => maps[mapId]);
          return mapIds.length
            ? h('span', { class: 'result-where-map' }, [
              ' (',
              ...mapIds.flatMap((mapId, k) => [
                k ? document.createTextNode(', ') : null,
                linkTo(idRoute(mapId), mapIds.length === 1 ? 'local map' : maps[mapId].name, 'local-map-link'),
              ]),
              ')',
            ])
            : null;
        })(),
      ]),
    ]));
  }
  const experiments = (result.experiment_ids || []).map((eid) => ATLAS.experiments[eid]).filter(Boolean);
  sections.add('Experiment', recordLinks(experiments));
  const pub = result.publication || {};
  const pubLinks = [];
  if (pub.doi) pubLinks.push(h('li', {}, h('a', { href: `https://doi.org/${pub.doi}`, target: '_blank', rel: 'noopener' }, `DOI ${pub.doi} (journal)`)));
  if (pub.arxiv) pubLinks.push(h('li', {}, h('a', { href: `https://arxiv.org/abs/${pub.arxiv}`, target: '_blank', rel: 'noopener' }, `arXiv ${pub.arxiv} (preprint)`)));
  // A4: `official_url_kind` (build-derived) says whether `official_url`
  // just restates the arXiv/DOI link already shown above under another
  // name — in that case it is not a second link, so showing a redundant
  // "Official page" pointed at the same target is never correct. Only a
  // `kind` the build could not match to either (`"official"`, or the field
  // absent from a bundle the build hasn't run against — never silently
  // dropped) gets its own row.
  if (result.official_url && result.official_url_kind !== 'arxiv' && result.official_url_kind !== 'doi') {
    pubLinks.push(h('li', {}, h('a', { href: result.official_url, target: '_blank', rel: 'noopener' }, 'Collaboration result page')));
  }
  sections.add('Publication', pubLinks.length ? h('ul', { class: 'entity-list' }, pubLinks) : null, { open: false });

  sections.note();
  frag.appendChild(sourcesDisclosure(id, result));
  return frag;
}

// ----------------------------------------------------------------- document
async function renderDocument(id) {
  const { byId } = await loader.getDocuments();
  const document_ = byId.get(id);
  if (!document_) return emptyNote('Unknown document.');
  const frag = document.createDocumentFragment();
  const sections = panelSections(frag);
  // The bundle's document records carry `name` and `date`, not `title` and
  // `year` — reading the latter left every document panel's heading blank
  // and its subtitle a dangling "Technical Design Report · " with nothing
  // after the separator, for all ~56 documents in the atlas.
  frag.appendChild(h('h2', {}, document_.name));
  frag.appendChild(h('p', { class: 'panel-subtitle' }, `${titleCase(document_.doc_type)} · ${fmtDate(document_.date)}`));
  frag.appendChild(h('p', {}, h('a', { href: document_.reference && document_.reference.url, target: '_blank', rel: 'noopener' }, 'Open document (new tab)')));
  sections.add('Volumes', document_.volumes && document_.volumes.length
    ? h('ul', { class: 'entity-list' }, document_.volumes.map((v) => h('li', {}, h('a', { href: v.url, target: '_blank', rel: 'noopener' }, v.title))))
    : null, { quiet: true });
  const owners = (document_.owner_ids || []).map((oid) => ({ id: oid, route: idRoute(oid), record: INDEX.get(oid) })).filter((o) => o.record);
  sections.add('Owners', owners.length
    ? h('ul', { class: 'entity-list' }, owners.map((o) => h('li', {}, linkTo(o.route, o.record.name))))
    : null, { open: false });
  sections.note();
  return frag;
}

// ---------------------------------------------------------------------- site
async function renderSite(id, timelineState) {
  const site = ATLAS.sites[id];
  if (!site) return emptyNote('Unknown site.');
  const text = await loader.getText();
  const t = text[id] || {};

  const frag = document.createDocumentFragment();
  const sections = panelSections(frag);
  frag.appendChild(h('h2', {}, site.name));
  const place = site.place ? [site.place.city, site.place.country].filter(Boolean).join(', ') : '';
  frag.appendChild(h('p', { class: 'panel-subtitle' }, [titleCase(site.setting), place].filter(Boolean).join(' · ')));
  frag.appendChild(experimentBadge(site, timelineState));
  // ---- local map view hook (§4): the compact subtitle-area affordance
  const mapChip = await localMapChip(site);
  if (mapChip) frag.appendChild(mapChip);

  // A23: coordinates.approximate only exists on the generated tree's nested
  // shape; the fixtures' flat lat/lon predate the amendment and are never
  // approximate, so siteLocationNote() silently returns null there.
  const locationNote = siteLocationNote(site);
  const coordText = (site.lat != null && site.lon != null)
    ? `${site.lat.toFixed(4)}, ${site.lon.toFixed(4)}${site.precision_m != null ? ` (±${site.precision_m} m${site.coord_kind ? `, ${titleCase(site.coord_kind)}` : ''})` : ''}`
    : '';
  const siteSummary = plainSummaryOf(site, t);
  sections.add('Overview', [
    siteSummary ? h('p', {}, siteSummary) : null,
    keyValueList([
      ['Aliases', (site.aliases || []).join(', ')],
      ['Country', (site.countries && site.countries.length ? site.countries.join(', ') : site.country) || ''],
      ['Coordinates', coordText],
    ]),
    locationNote,
  ], { missing: [!siteSummary && 'Plain-language summary'] });

  const quantRows = [
    ['Depth', siteQuantity(site.depth != null ? site.depth : site.depth_m, 'm')],
    ['Depth (water equivalent)', siteQuantity(site.depth_mwe, 'm.w.e.')],
    // A27: the cosmic-ray muon flux, in the unit its source uses (the chart converts).
    ['Cosmic-ray muon flux', siteQuantity(site.muon_flux, 'cm^-2 s^-1')],
    ['Altitude', siteQuantity(site.altitude != null ? site.altitude : site.altitude_m, 'm')],
  ].filter(([, v]) => v);
  sections.add('Depth and altitude', keyValueList(quantRows), { open: false });

  const facility = site.facility_id && ATLAS.facilities[site.facility_id];
  sections.add('Facility', facility ? linkTo(idRoute(facility.id), facility.name) : null);

  // Sites carry no derived `detector_ids` inverse list in the generated
  // bundle (docs/HEP_ATLAS_BUNDLES.md's inverse-list table stops at `site:
  // document_ids`) — derive "placed here" by scanning every detector's own
  // `placements` for this site id, which both trees carry.
  const detectorsHere = Object.values(ATLAS.detectors || {})
    .map((detector) => ({ detector, placement: (detector.placements || []).find((p) => p.site_id === id) }))
    .filter((row) => row.placement);
  sections.add('Detectors placed here', detectorsHere.length
    ? h('ul', { class: 'entity-list' }, detectorsHere.map(({ detector, placement }) => h('li', { class: 'entity-link-with-meta' }, [
      linkTo(idRoute(detector.id), detector.name),
      placement.role ? ` — ${titleCase(placement.role)}` : '',
      (placement.start || placement.end) ? ` (${fmtInterval(placement.start, placement.end)})` : '',
    ])))
    : null);

  const experimentIds = new Set();
  for (const { detector } of detectorsHere) {
    for (const eid of detector.experiment_ids || []) experimentIds.add(eid);
  }
  const experimentsHosted = [...experimentIds].map((eid) => ATLAS.experiments[eid]).filter(Boolean);
  sections.add('Experiments hosted', recordLinks(experimentsHosted));

  const acceleratorsHere = Object.values(ATLAS.accelerators || {}).filter((a) => a.site_id === id);
  sections.add('Accelerators sited here', recordLinks(acceleratorsHere), { open: false });

  const beamlinesHere = Object.values(ATLAS.beamlines || {}).filter((b) => (b.near_detector_site_ids || []).includes(id)
    || (b.far_detector_site_ids || []).includes(id));
  sections.add('Beamlines', recordLinks(beamlinesHere), { open: false });

  const documents = await documentsFor(id, site);
  sections.add('Documents', documentLinks(documents), { open: false });

  // ---- local map view hook (§4)
  const mapSection = await localMapLinks(site);
  if (mapSection) frag.appendChild(mapSection);

  sections.note();
  const approximateSites = (site.coordinates && site.coordinates.approximate) ? [site] : [];
  frag.appendChild(sourcesDisclosure(id, site, { approximateSites }));
  CALLBACKS.focusGlobe(id);
  return frag;
}

// ------------------------------------------------------------------ detector
async function renderDetector(id, timelineState) {
  const detector = ATLAS.detectors[id];
  if (!detector) return emptyNote('Unknown detector.');
  const text = await loader.getText();
  const t = text[id] || {};

  const frag = document.createDocumentFragment();
  const sections = panelSections(frag);
  frag.appendChild(h('h2', {}, detector.name));
  const techLabel = [detector.technology, (detector.technology_classes || []).map(kindLabel).join(', ')]
    .filter(Boolean).join(' · ');
  if (techLabel) frag.appendChild(h('p', { class: 'panel-subtitle' }, techLabel));
  frag.appendChild(experimentBadge(detector, timelineState));
  // ---- local map view hook (§4): the compact subtitle-area affordance
  const mapChip = await localMapChip(detector);
  if (mapChip) frag.appendChild(mapChip);

  const detectorSummary = plainSummaryOf(detector, t);
  sections.add('Overview', [
    detectorSummary ? h('p', {}, detectorSummary) : null,
    keyValueList([['Aliases', (detector.aliases || []).join(', ')]]),
  ], { missing: [!detectorSummary && 'Plain-language summary'] });

  const specRows = Object.entries(detector.specs || {}).map(([k, v]) => [titleCase(k), quantityText(v)]);
  sections.add('Specifications', keyValueList(specRows), { open: false });

  const placements = detector.placements || [];
  sections.add('Placements', placements.length
    ? h('ul', { class: 'entity-list' }, placements.map((p) => {
      const site = ATLAS.sites[p.site_id];
      return h('li', { class: 'entity-link-with-meta' }, [
        site ? linkTo(idRoute(site.id), site.name) : document.createTextNode(p.site_id),
        p.role ? ` — ${titleCase(p.role)}` : '',
        (p.start || p.end) ? ` (${fmtInterval(p.start, p.end)})` : '',
      ]);
    }))
    : null);

  const experimentsHere = (detector.experiment_ids || []).map((eid) => ATLAS.experiments[eid]).filter(Boolean);
  sections.add('Experiments', recordLinks(experimentsHere));

  const parent = detector.parent_detector_id && ATLAS.detectors[detector.parent_detector_id];
  const children = Object.values(ATLAS.detectors || {}).filter((d) => d.parent_detector_id === id);
  sections.groups('Parent and child detectors', [
    ['Parent', parent ? h('p', {}, linkTo(idRoute(parent.id), parent.name)) : null, 'Parent detector'],
    ['Child detectors', recordLinks(children)],
  ], { open: false });

  const subsystems = (detector.subsystems || []).map(subsystemNode).filter(Boolean);
  sections.add('Subsystems', subsystems.length ? h('ul', { class: 'entity-list' }, subsystems) : null, { open: false });

  const documents = await documentsFor(id, detector);
  sections.add('Documents', documentLinks(documents), { open: false });

  // ---- local map view hook (§4)
  const mapSection = await localMapLinks(detector);
  if (mapSection) frag.appendChild(mapSection);

  sections.note();
  frag.appendChild(sourcesDisclosure(id, detector));
  const focusSite = placements.map((p) => p.site_id).find(Boolean);
  if (focusSite) CALLBACKS.focusGlobe(focusSite);
  return frag;
}

// --------------------------------------------------------------- accelerator
async function renderAccelerator(id, timelineState) {
  const accelerator = ATLAS.accelerators[id];
  if (!accelerator) return emptyNote('Unknown accelerator.');
  const text = await loader.getText();
  const t = text[id] || {};

  const frag = document.createDocumentFragment();
  const sections = panelSections(frag);
  frag.appendChild(h('h2', {}, accelerator.name));
  frag.appendChild(h('p', { class: 'panel-subtitle' }, kindLabel(accelerator.kind)));
  frag.appendChild(experimentBadge(accelerator, timelineState));
  // ---- local map view hook (§4): the compact subtitle-area affordance
  const mapChip = await localMapChip(accelerator);
  if (mapChip) frag.appendChild(mapChip);
  const frontierLink = frontierCta(accelerator);
  if (frontierLink) frag.appendChild(frontierLink);

  const acceleratorSummary = plainSummaryOf(accelerator, t);
  sections.add('Overview', [
    acceleratorSummary ? h('p', {}, acceleratorSummary) : null,
    keyValueList([
      ['Aliases', (accelerator.aliases || []).join(', ')],
      ['Collider', accelerator.is_collider ? 'Yes' : 'No'],
      ['Particles', (accelerator.particles || []).join(', ')],
    ]),
  ], { missing: [!acceleratorSummary && 'Plain-language summary'] });

  const specRows = Object.entries(accelerator.specs || {}).map(([k, v]) => [titleCase(k), quantityText(v)]);
  sections.add('Specifications', keyValueList(specRows), { open: false });

  const facility = accelerator.facility_id && ATLAS.facilities[accelerator.facility_id];
  const site = accelerator.site_id && ATLAS.sites[accelerator.site_id];
  sections.add('Facility and site', [
    facility ? h('p', { class: 'entity-link-with-meta' }, ['Facility: ', linkTo(idRoute(facility.id), facility.name)]) : null,
    site ? h('p', { class: 'entity-link-with-meta' }, ['Site: ', linkTo(idRoute(site.id), site.name)]) : null,
  ], { missing: [!facility && 'Facility', !site && 'Site'] });

  const feeds = (accelerator.feeds_accelerator_ids || []).map((aid) => ATLAS.accelerators[aid]).filter(Boolean);
  // `fed_by_accelerator_ids` is a generated-tree-only derived field (never
  // present, not even empty, on the fixtures' accelerator records).
  const fedBy = (accelerator.fed_by_accelerator_ids || []).map((aid) => ATLAS.accelerators[aid]).filter(Boolean);
  sections.groups('Accelerator chain', [
    ['Feeds', recordLinks(feeds), 'Accelerators it feeds'],
    ['Fed by', recordLinks(fedBy), 'Accelerators feeding it'],
  ], { open: false });

  const beamlinesHere = (accelerator.beamline_ids || []).map((bid) => ATLAS.beamlines[bid]).filter(Boolean);
  sections.add('Beamlines', recordLinks(beamlinesHere));

  const servedExperiments = (accelerator.serves_experiment_ids || []).map((eid) => ATLAS.experiments[eid]).filter(Boolean);
  sections.add('Experiments served', recordLinks(servedExperiments));

  // `intervals` is absent on the fixtures' accelerator/beamline records (only
  // the generated tree's build derives it) — state_segments still drives the
  // status badge above either way, so this only ever loses the fixtures'
  // human-readable timeline, not their status.
  const intervals = accelerator.intervals || [];
  sections.add('Timeline', intervals.length
    ? h('ul', { class: 'entity-list' }, intervals.map((iv) => h('li', {}, intervalLine(iv))))
    : null, { open: false });

  const documents = await documentsFor(id, accelerator);
  sections.add('Documents', documentLinks(documents), { open: false });

  // ---- local map view hook (§4)
  const mapSection = await localMapLinks(accelerator);
  if (mapSection) frag.appendChild(mapSection);

  sections.note();
  frag.appendChild(sourcesDisclosure(id, accelerator));
  if (accelerator.site_id) CALLBACKS.focusGlobe(accelerator.site_id);
  return frag;
}

// ------------------------------------------------------------------ beamline
async function renderBeamline(id, timelineState) {
  const beamline = ATLAS.beamlines[id];
  if (!beamline) return emptyNote('Unknown beamline.');
  const text = await loader.getText();
  const t = text[id] || {};

  const frag = document.createDocumentFragment();
  const sections = panelSections(frag);
  frag.appendChild(h('h2', {}, beamline.name));
  frag.appendChild(experimentBadge(beamline, timelineState));
  // ---- local map view hook (§4): the compact subtitle-area affordance
  const mapChip = await localMapChip(beamline);
  if (mapChip) frag.appendChild(mapChip);
  const beamlineRows = rowsForBeamline(ATLAS, beamline);
  if (beamlineRows.length) frag.appendChild(beamSectionCta(beamlineRows));

  const beamlineSummary = plainSummaryOf(beamline, t);
  const primaryBeam = beamline.primary_beam || {};
  const primaryBeamText = [primaryBeam.particle, primaryBeam.energy ? quantityText(primaryBeam.energy) : null]
    .filter(Boolean).join(' · ');
  sections.add('Overview', [
    beamlineSummary ? h('p', {}, beamlineSummary) : null,
    keyValueList([
      ['Aliases', (beamline.aliases || []).join(', ')],
      ['Primary beam', primaryBeamText],
      ['Secondary beam', beamline.secondary_beam],
      ['Target', beamline.target],
      ['Direction', beamline.direction],
    ]),
  ], { missing: [!beamlineSummary && 'Plain-language summary'] });

  const specRows = Object.entries(beamline.specs || {}).map(([k, v]) => [titleCase(k), quantityText(v)]);
  sections.add('Specifications', keyValueList(specRows), { open: false });

  const facility = beamline.facility_id && ATLAS.facilities[beamline.facility_id];
  const accelerator = beamline.accelerator_id && ATLAS.accelerators[beamline.accelerator_id];
  sections.add('Facility and accelerator', [
    facility ? h('p', { class: 'entity-link-with-meta' }, ['Facility: ', linkTo(idRoute(facility.id), facility.name)]) : null,
    accelerator ? h('p', { class: 'entity-link-with-meta' }, ['Accelerator: ', linkTo(idRoute(accelerator.id), accelerator.name)]) : null,
  ], { missing: [!facility && 'Facility', !accelerator && 'Accelerator'] });

  function siteItems(siteIds) {
    return siteIds.length ? h('ul', { class: 'entity-list' }, siteIds.map((sid) => {
      const site = ATLAS.sites[sid];
      return h('li', {}, site ? linkTo(idRoute(site.id), site.name) : document.createTextNode(sid));
    })) : null;
  }
  const baselines = beamline.baselines || [];
  sections.groups('Near and far detector sites', [
    ['Near', siteItems(beamline.near_detector_site_ids || []), 'Near detector sites'],
    ['Far', siteItems(beamline.far_detector_site_ids || []), 'Far detector sites'],
    ['Baselines', baselines.length ? h('ul', { class: 'entity-list' }, baselines.map((b) => {
      const from = ATLAS.sites[b.from_site_id];
      const to = ATLAS.sites[b.to_site_id];
      const distance = b.distance ? quantityText(b.distance) : '';
      return h('li', {}, `${from ? from.name : b.from_site_id} → ${to ? to.name : b.to_site_id}${distance ? `: ${distance}` : ''}`);
    })) : null],
  ], { optional: ['Baselines'] });

  const beamlineExperiments = (beamline.experiment_ids || []).map((eid) => ATLAS.experiments[eid]).filter(Boolean);
  sections.add('Experiments', recordLinks(beamlineExperiments));

  const intervals = beamline.intervals || [];
  sections.add('Timeline', intervals.length
    ? h('ul', { class: 'entity-list' }, intervals.map((iv) => h('li', {}, intervalLine(iv))))
    : null, { open: false });

  const documents = await documentsFor(id, beamline);
  sections.add('Documents', documentLinks(documents), { open: false });

  // ---- local map view hook (§4)
  const mapSection = await localMapLinks(beamline);
  if (mapSection) frag.appendChild(mapSection);

  sections.note();
  frag.appendChild(sourcesDisclosure(id, beamline));
  const focusSite = (beamline.near_detector_site_ids || [])[0] || (beamline.far_detector_site_ids || [])[0];
  if (focusSite) CALLBACKS.focusGlobe(focusSite);
  return frag;
}

const RENDERERS = {
  facility: renderFacility,
  experiment: renderExperiment,
  collaboration: renderCollaboration,
  institution: renderInstitution,
  topic: renderTopic,
  result: renderResult,
  document: renderDocument,
  site: renderSite,
  detector: renderDetector,
  accelerator: renderAccelerator,
  beamline: renderBeamline,
};

// `timelineState` is `{ year }` or `{ range: [lo, hi] }`, the same shape
// app.js already tracks from the URL/slider — passed through so the
// facility/experiment/collaboration badges (the only ones with a lifecycle)
// can read the entity's state *at that selection* instead of its frozen
// build-time status. app.js re-invokes render() on every timeline change
// (it is itself a state.navigate() subscriber), so this also re-renders the
// whole panel whenever the year or range moves.
export async function render(route, timelineState = { year: new Date().getFullYear() }) {
  if (!route) {
    container.innerHTML = '';
    container.classList.add('hidden');
    lastRenderedId = null;
    // Return keyboard focus to whatever opened this panel — otherwise
    // closing it (the close button or Escape) drops focus to <body> and a
    // keyboard user loses their place entirely.
    if (openerElement && document.body.contains(openerElement)) {
      openerElement.focus({ preventScroll: true });
    }
    openerElement = null;
    return;
  }
  const id = `${route.type}:${route.slug}`;
  if (id !== lastRenderedId) {
    openerElement = document.activeElement;
    lastRenderedId = id;
  }
  const renderer = RENDERERS[route.type];
  container.classList.remove('hidden');
  container.setAttribute('aria-busy', 'true');
  container.innerHTML = '<p class="loading-note">Loading…</p>';
  if (!renderer) {
    container.innerHTML = '';
    container.appendChild(emptyNote(`Unknown entity type: ${route.type}`));
    container.removeAttribute('aria-busy');
    return;
  }
  try {
    const frag = await renderer(id, timelineState);
    container.innerHTML = '';
    const closeBtn = h('button', {
      type: 'button', class: 'close-btn', id: 'close-detail', 'aria-label': 'Close panel',
    }, '×');
    closeBtn.addEventListener('click', () => CALLBACKS.navigate({ entity: null }));
    container.appendChild(closeBtn);
    container.appendChild(frag);
    const heading = container.querySelector('h2');
    if (heading) {
      heading.setAttribute('tabindex', '-1');
      heading.focus({ preventScroll: true });
    }
    if (route.type === 'collaboration') setCollaborationContext(id);
  } catch (error) {
    container.innerHTML = '';
    container.appendChild(emptyNote(`Could not load this entity: ${error.message}`));
  }
  container.removeAttribute('aria-busy');
}
