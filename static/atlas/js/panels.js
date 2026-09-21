// panels.js — detail panels with progressive disclosure (native <details>).
// Facility / experiment / collaboration / institution / topic / result /
// document. Long text (text.json) and citations (provenance.json) are
// fetched lazily, on first panel open, via loader.js (which itself caches).

import * as loader from './loader.js';
import {
  quantityText, fmtDate, titleCase, statusEra, statusForTimeline, timelineAbsenceReason,
} from './model.js';
import * as provenance from './provenance.js';

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

function keyValueList(pairs) {
  const dl = h('dl', { class: 'kv-list' });
  for (const [key, value] of pairs) {
    if (value == null || value === '') continue;
    dl.appendChild(h('dt', {}, key));
    dl.appendChild(h('dd', {}, value));
  }
  return dl;
}

function emptyNote(text) {
  return h('p', { class: 'empty-note' }, text);
}

// Task A4/A5: an empty "Results" section must say whether that is because
// curation hasn't reached this entity yet or the atlas is simply small —
// never read as if the atlas had checked and found none (CLAUDE.md: "an
// empty 'complete' neighborhood reads as proof a person has no
// collaborators" is exactly the failure mode this avoids). The counts come
// from the results bundle the caller already loaded, never hardcoded, so
// they can't drift from what the atlas actually holds.
function noResultsCurated(list, scopeLabel) {
  const experimentIds = new Set();
  for (const r of list) for (const eid of r.experiment_ids || []) experimentIds.add(eid);
  return emptyNote(
    `No results curated for this ${scopeLabel} yet (the atlas records ${list.length} results `
    + `across ${experimentIds.size} experiments; see coverage)`);
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
  const start = fmtDate(iv.start) || '?';
  const end = fmtDate(iv.end) || 'present';
  return `${label}${status} (${start}–${end})`;
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
  const details = h('details', { class: 'panel-section' });
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
    } catch (error) {
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
/**
 * The "Open local map" affordance for any record the build has linked to a
 * to-scale local map: `map_id` on a facility or a site, `geometry_map_ids`
 * on an accelerator, beamline or detector (the maps that draw it). Returns
 * null when the build linked none, so a caller can append it unconditionally
 * and nothing appears for a facility whose campus has not been mapped yet —
 * which means "not researched", not "has no layout".
 */
export function localMapLinks(record) {
  if (!record) return null;
  const ids = record.map_id ? [record.map_id] : (record.geometry_map_ids || []);
  const maps = (ATLAS && ATLAS.maps) || {};
  const known = ids.filter((mapId) => maps[mapId]);
  if (!known.length) return null;
  const items = known.map((mapId) => {
    const meta = maps[mapId];
    const drawn = `${meta.to_scale_count} feature${meta.to_scale_count === 1 ? '' : 's'} drawn to scale`;
    const unlocated = meta.unlocated_count
      ? ` \u00b7 ${meta.unlocated_count} not drawn (geometry not verified)` : '';
    return h('li', {}, [
      linkTo(idRoute(mapId), `Open local map \u2014 ${meta.name}`, 'local-map-link'),
      h('div', { class: 'source-meta' }, `${drawn}${unlocated}`),
    ]);
  });
  return section('Local map', [h('ul', { class: 'entity-list' }, items)]);
}

/**
 * The same affordance as one compact line for a panel's subtitle area, so a
 * reader looking at a site, accelerator, beamline or detector sees "shown on
 * a local map" before scrolling. Returns null when the build linked none.
 */
export function localMapChip(record) {
  if (!record) return null;
  const ids = record.map_id ? [record.map_id] : (record.geometry_map_ids || []);
  const maps = (ATLAS && ATLAS.maps) || {};
  const known = ids.filter((mapId) => maps[mapId]);
  if (!known.length) return null;
  const wrap = h('p', { class: 'panel-subtitle local-map-chip-row' });
  known.forEach((mapId, i) => {
    if (i) wrap.appendChild(document.createTextNode(' \u00b7 '));
    wrap.appendChild(linkTo(idRoute(mapId), `\u25ce Shown to scale on the ${maps[mapId].name} local map`,
      'local-map-chip'));
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
  frag.appendChild(h('h2', {}, facility.name));
  frag.appendChild(h('p', { class: 'panel-subtitle' }, titleCase(facility.kind)));
  frag.appendChild(experimentBadge(facility, timelineState));

  const facilitySummary = plainSummaryOf(facility, t);
  frag.appendChild(section('Overview', [
    facilitySummary ? h('p', {}, facilitySummary) : emptyNote('No plain-language summary yet.'),
    keyValueList([
      ['Aliases', (facility.aliases || []).join(', ')],
      // Generated bundle: `operator_text` (no `operator` field at all).
      // Fixtures: `operator` (no `operator_text`). Read whichever exists.
      ['Operator', facility.operator_text || facility.operator],
      ['Country', (facility.country || []).join(', ')],
    ]),
  ]));

  const specRows = Object.entries(facility.specs || {}).map(([k, v]) => [titleCase(k), quantityText(v)]);
  frag.appendChild(section('Technical information', [
    specRows.length ? keyValueList(specRows) : emptyNote('No technical specifications recorded.'),
  ], { open: false }));

  frag.appendChild(section('Current experiments', current.length
    ? [h('ul', { class: 'entity-list' }, current.map((e) => h('li', {}, linkTo(idRoute(e.id), e.name))))]
    : [emptyNote('No experiments currently active here.')]));
  frag.appendChild(section('Historical experiments', historical.length
    ? [h('ul', { class: 'entity-list' }, historical.map((e) => h('li', {}, linkTo(idRoute(e.id), e.name))))]
    : [emptyNote('No historical experiments recorded in the atlas (coverage is partial).')], { open: false }));
  frag.appendChild(section('Future / planned experiments', future.length
    ? [h('ul', { class: 'entity-list' }, future.map((e) => h('li', {}, linkTo(idRoute(e.id), e.name))))]
    : [emptyNote('No future or planned experiments recorded in the atlas (coverage is partial).')], { open: false }));

  frag.appendChild(section('Results', results.length
    ? [h('ul', { class: 'entity-list' }, results.map((r) => h('li', {}, linkTo(idRoute(r.id), r.title))))]
    : [noResultsCurated(allResults, 'facility')], { open: false }));

  frag.appendChild(section('Documents', documents.length
    ? [h('ul', { class: 'entity-list' }, documents.map((d) => h('li', {},
      h('a', { href: d.reference && d.reference.url, target: '_blank', rel: 'noopener' }, d.name))))]
    : [emptyNote('No documents curated yet.')], { open: false }));

  const links = Object.entries(facility.links || {}).filter(([, v]) => v);
  frag.appendChild(section('Official links', links.length
    ? [h('ul', { class: 'entity-list' }, links.map(([k, v]) => h('li', {}, h('a', { href: v, target: '_blank', rel: 'noopener' }, `${titleCase(k)}: ${v}`))))]
    : [emptyNote('No official links recorded.')], { open: false }));

  const related = (facility.related_facility_ids || []).map((rid) => ATLAS.facilities[rid]).filter(Boolean);
  frag.appendChild(section('Related facilities', related.length
    ? [h('ul', { class: 'entity-list' }, related.map((r) => h('li', {}, linkTo(idRoute(r.id), r.name))))]
    : [emptyNote('No related facilities recorded.')], { open: false }));

  // ---- local map view hook (§4): only the facility renderer calls it for
  // now; the site/accelerator/beamline/detector renderers can append the
  // same element when they land.
  const mapSection = localMapLinks(facility);
  if (mapSection) frag.appendChild(mapSection);

  frag.appendChild(sourcesDisclosure(id, facility));
  CALLBACKS.focusGlobe(id);
  return frag;
}

// ---------------------------------------------------------------- experiment
async function renderExperiment(id, timelineState) {
  const exp = ATLAS.experiments[id];
  if (!exp) return emptyNote('Unknown experiment.');
  const text = await loader.getText();
  const t = text[id] || {};

  const frag = document.createDocumentFragment();
  frag.appendChild(h('h2', {}, exp.name));
  frag.appendChild(h('p', { class: 'panel-subtitle' }, titleCase(exp.kind)));
  frag.appendChild(experimentBadge(exp, timelineState));

  const collabs = (exp.collaboration_ids || []).map((cid) => ATLAS.collaborations[cid]).filter(Boolean);
  if (collabs.length) {
    frag.appendChild(h('p', { class: 'collab-line' }, [
      'Collaboration: ',
      ...collabs.flatMap((c, i) => (i === 0 ? [linkTo(idRoute(c.id), c.name, 'collab-link')] : [document.createTextNode(', '), linkTo(idRoute(c.id), c.name, 'collab-link')])),
    ]));
  }

  const expPlainSummary = plainSummaryOf(exp, t);
  frag.appendChild(section('What it studies', [
    expPlainSummary ? h('p', { class: 'plain-summary' }, expPlainSummary) : emptyNote('No plain-language summary yet.'),
    exp.topic_ids && exp.topic_ids.length
      ? h('p', {}, ['Research topics: ', ...exp.topic_ids.flatMap((tid, i) => {
        const topic = ATLAS.topics[tid];
        const link = topic ? linkTo(idRoute(tid), topic.name) : document.createTextNode(tid);
        return i === 0 ? [link] : [document.createTextNode(', '), link];
      })])
      : null,
  ]));

  const keySpecRows = (exp.key_specs || []).map((s) => [s.label, quantityText(s.quantity)]);
  frag.appendChild(section('Key specifications', [
    keySpecRows.length ? keyValueList(keySpecRows) : emptyNote('No key specifications recorded.'),
  ]));

  frag.appendChild(section('Full technical section', [
    t.summary_technical ? h('p', {}, t.summary_technical) : emptyNote('No technical summary yet.'),
    keyValueList([
      ['Energy regime', exp.energy_regime],
      ['External IDs', exp.external ? Object.entries(exp.external).filter(([, v]) => v).map(([k, v]) => `${k}: ${v}`).join(' · ') : ''],
    ]),
  ], { open: false }));

  const beamlines = (exp.beamline_ids || []).map((bid) => ATLAS.beamlines[bid]).filter(Boolean);
  const sites = (exp.site_ids || []).map((sid) => ATLAS.sites[sid]).filter(Boolean);
  // A23: an admitted-approximate site coordinate (a campus point standing
  // in for a real hall position no fetched source gives) must say so
  // wherever it's shown, and must never read as the detector's own
  // position — so the location line names the coordinate's kind instead of
  // silently reusing the same "(setting)" phrasing a real detector point gets.
  const approximateSites = sites.filter((s) => s.coordinates && s.coordinates.approximate);
  frag.appendChild(section('Beam and sites', [
    beamlines.length ? h('ul', { class: 'entity-list' }, beamlines.map((b) => h('li', {},
      `${b.name}: ${(b.baselines || []).map((base) => base.distance ? base.distance.display : '').join(', ')}`))) : emptyNote('No beamline.'),
    sites.length ? h('ul', { class: 'entity-list' }, sites.map((s) => h('li', {}, [
      linkTo({ type: 'facility', slug: (s.facility_id || s.id).split(':')[1] }, `${s.name} (${s.setting})`),
      siteLocationNote(s),
    ]))) : null,
  ], { open: false }));

  const { byId: resultById, list: allResults } = await loader.getResults();
  const results = (exp.result_ids || []).map((rid) => resultById.get(rid)).filter(Boolean)
    .sort((a, b) => (a.month || 0) - (b.month || 0));
  // Task A5: an experiment that hasn't started operating yet has no results
  // *because there is nothing to report yet* — a scientifically meaningful
  // absence, not a curation gap — so it gets its own wording instead of the
  // "not yet curated" note every other empty Results section uses.
  const notYetOperating = statusEra(exp.status) === 'future';
  frag.appendChild(section('Results timeline', results.length
    ? [h('ol', { class: 'entity-list timeline-list' }, results.map((r) => h('li', {}, [
      h('span', { class: 'result-date' }, r.date || String(r.year || '')),
      ' ',
      linkTo(idRoute(r.id), r.title),
    ])))]
    : [notYetOperating
      ? emptyNote('Not yet operating — no results expected.')
      : noResultsCurated(allResults, 'experiment')], { open: false }));

  const { byId: docById } = await loader.getDocuments();
  const documents = (exp.document_ids || []).map((did) => docById.get(did)).filter(Boolean);
  frag.appendChild(section('Documents', documents.length
    ? [h('ul', { class: 'entity-list' }, documents.map((d) => h('li', {},
      h('a', { href: d.reference && d.reference.url, target: '_blank', rel: 'noopener' }, d.name))))]
    : [emptyNote('No documents curated yet.')], { open: false }));

  const predecessors = (exp.lineage || []).filter((l) => ['predecessor', 'upgrade_of'].includes(l.relation));
  const successors = (exp.lineage || []).filter((l) => ['successor', 'upgraded_to'].includes(l.relation));
  const others = (exp.lineage || []).filter((l) => !predecessors.includes(l) && !successors.includes(l));
  function lineageList(rows) {
    return rows.length
      ? h('ul', { class: 'entity-list' }, rows.map((l) => {
        const other = ATLAS.experiments[l.experiment_id];
        return h('li', {}, [other ? linkTo(idRoute(l.experiment_id), other.name) : document.createTextNode(l.experiment_id), ` (${l.relation.replace(/_/g, ' ')})`]);
      }))
      : emptyNote('None recorded.');
  }
  frag.appendChild(section('Predecessors and successors', [
    h('h4', {}, 'Predecessors'), lineageList(predecessors),
    h('h4', {}, 'Successors'), lineageList(successors),
    others.length ? h('div', {}, [h('h4', {}, 'Related programs'), lineageList(others)]) : null,
  ], { open: false }));

  frag.appendChild(sourcesDisclosure(id, exp, { approximateSites }));
  CALLBACKS.focusGlobe(id);
  return frag;
}

// ------------------------------------------------------------- collaboration
async function renderCollaboration(id, timelineState) {
  const collab = ATLAS.collaborations[id];
  if (!collab) return emptyNote('Unknown collaboration.');
  const text = await loader.getText();
  const t = text[id] || {};
  const host = collab.host_facility_id && ATLAS.facilities[collab.host_facility_id];

  const frag = document.createDocumentFragment();
  frag.appendChild(h('h2', {}, collab.name));
  frag.appendChild(experimentBadge(collab, timelineState));

  const summary = plainSummaryOf(collab, t)
    || `Formed ${collab.formation || 'at an unrecorded date'}${host ? `, hosted at ${host.name}` : ''}.`;
  frag.appendChild(section('Summary', [h('p', {}, summary)]));

  frag.appendChild(section('Host facility', host
    ? [linkTo(idRoute(host.id), host.name)]
    : [emptyNote('No host facility recorded.')]));

  // The collaboration record's own `membership` block does not carry a
  // confirmed-member count (only institution_count / country_count / as_of
  // headline stats) — the actual roster counts, split into confirmed and
  // undated per ontology amendment A5, live in the membership bundle itself.
  // A missing bundle (no roster curated at all) is not the same absence as
  // one that exists but is only partially researched — §TASK3 keeps those
  // two honest instead of collapsing both into "0 members" or a stale count.
  let membership = null;
  try {
    membership = await loader.getMembership(id);
  } catch (error) {
    membership = null;
  }

  const viewBtn = h('button', { type: 'button', id: 'view-on-globe', class: 'primary-btn' }, 'View collaboration on globe');
  if (membership && (membership.members || []).length) {
    viewBtn.addEventListener('click', () => CALLBACKS.viewOnGlobe(id));
  } else {
    viewBtn.disabled = true;
    viewBtn.setAttribute('aria-disabled', 'true');
    viewBtn.title = 'No institution roster curated yet for this collaboration.';
  }
  frag.appendChild(h('div', { class: 'panel-actions' }, viewBtn));

  let membershipBody;
  let membershipMembers = null;
  if (!membership) {
    membershipBody = [emptyNote('Institution roster not yet curated for this collaboration.')];
  } else {
    const counts = membership.counts || {};
    const confirmed = counts.confirmed || 0;
    const undated = counts.undated || 0;
    const asOf = membership.as_of ? ` as of ${membership.as_of}` : '';
    const history = membership.membership_history;
    const countLabel = (history === 'partial' || history === 'unknown')
      ? `Partial roster: ${confirmed} confirmed institutions (+${undated} undated)${asOf}; the full membership is larger`
      : `${confirmed} confirmed institutions (+${undated} undated)${asOf}`;
    membershipBody = [
      h('p', { class: 'membership-count' }, countLabel),
      keyValueList([
        ['Institutions', collab.membership && collab.membership.institution_count],
        ['Countries', collab.membership && collab.membership.country_count],
        ['As of', collab.membership && collab.membership.as_of],
      ]),
    ];
    // `/members/N` provenance pointers index the roster's *authored* file
    // order (`source_index`), not this display-sorted `members` array — see
    // build.py's `_membership_row` and docs/HEP_ATLAS_BUNDLES.md.
    membershipMembers = [];
    for (const row of membership.members || []) {
      if (typeof row.source_index === 'number') membershipMembers[row.source_index] = row;
    }
  }
  frag.appendChild(section('Membership', membershipBody));

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
  frag.appendChild(h('h2', {}, institution.name));
  frag.appendChild(h('p', { class: 'panel-subtitle' }, [
    titleCase(institution.kind), institution.place ? ` · ${institution.place.city}, ${institution.place.country}` : '',
  ].join('')));

  const collabId = (institution.collaboration_ids || []).includes(lastCollaborationId)
    ? lastCollaborationId
    : (institution.collaboration_ids || [])[0];

  if (!collabId) {
    frag.appendChild(emptyNote('No collaboration membership recorded for this institution.'));
    return frag;
  }

  const membership = await loader.getMembership(collabId);
  const row = (membership.members || []).find((m) => m.institution_id === id);
  const collab = ATLAS.collaborations[collabId];

  frag.appendChild(section(`Membership in ${collab ? collab.name : collabId}`, [
    row ? h('p', { class: 'evidence-label' }, row.evidence_label) : emptyNote('No membership evidence recorded.'),
    row && row.note ? h('p', { class: 'membership-note' }, row.note) : null,
  ]));

  const peopleSection = h('div', { class: 'people-section' });
  const peopleList = h('ul', { class: 'people-list', id: 'people-list' });

  let people = [];
  if (row && row.people_bundle) {
    const bundle = await loader.getPeople(row.people_bundle);
    people = bundle.people || [];
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
      peopleList.appendChild(h('li', { class: 'empty-note' }, 'No people recorded for this filter.'));
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

  frag.appendChild(section(`People (${people.length})`, people.length ? [peopleSection] : [emptyNote(
    (row && row.people_count) ? `${row.people_count} people recorded, not yet resolved to named records.` : 'No people recorded for this institution.',
  )]));

  return frag;
}

// -------------------------------------------------------------------- topic
async function renderTopic(id) {
  const topic = ATLAS.topics[id];
  if (!topic) return emptyNote('Unknown topic.');
  const text = await loader.getText();
  const t = text[id] || {};

  const frag = document.createDocumentFragment();
  frag.appendChild(h('h2', {}, topic.name));
  frag.appendChild(h('p', { class: 'plain-question' }, topic.question || ''));
  if (t.overview) frag.appendChild(h('p', {}, t.overview));

  if (topic.observables && topic.observables.length) {
    frag.appendChild(section('Observables', [h('ul', { class: 'entity-list' }, topic.observables.map((o) => h('li', {}, o)))]));
  }

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
  function expList(list) {
    // "None." here means none *of this era specifically* — only meaningful
    // once the section as a whole has at least one tagged experiment; the
    // all-eras-empty case below gets its own honest wording instead.
    return list.length ? h('ul', { class: 'entity-list' }, list.map((e) => h('li', {}, linkTo(idRoute(e.id), e.name)))) : emptyNote('None.');
  }
  frag.appendChild(section('Experiments', experiments.length
    ? [
      h('h4', {}, 'Current'), expList(current),
      h('h4', {}, 'Historical'), expList(historical),
      h('h4', {}, 'Future / planned'), expList(future),
    ]
    : [emptyNote('No experiments in the atlas tagged with this topic yet.')]));

  const { list: allResults } = await loader.getResults();
  const results = allResults.filter((r) => (r.topic_ids || []).includes(id));
  frag.appendChild(section('Related results', results.length
    ? [h('ul', { class: 'entity-list' }, results.map((r) => h('li', {}, linkTo(idRoute(r.id), r.title))))]
    : [noResultsCurated(allResults, 'topic')], { open: false }));

  return frag;
}

// ------------------------------------------------------------------- result
async function renderResult(id) {
  const { byId } = await loader.getResults();
  const result = byId.get(id);
  if (!result) return emptyNote('Unknown result.');
  const text = await loader.getText();
  const t = text[id] || {};

  const frag = document.createDocumentFragment();
  frag.appendChild(h('h2', {}, result.title));
  frag.appendChild(h('p', { class: 'panel-subtitle' }, `${titleCase(result.result_type)} · ${fmtDate(result.date)}`));
  frag.appendChild(h('p', {}, (t.claim && t.claim.quote) || (result.claim && result.claim.quote) || result.summary && result.summary.plain || ''));
  // The bundle carries one `date` plus a `date_kind` ("announcement" |
  // "preprint" | "publication"), not separate `announced` / `published`
  // fields — those never exist on a real result record, so this used to
  // silently drop both rows every time.
  frag.appendChild(keyValueList([
    ['Significance', result.significance],
    ['Key value', result.key_value_text],
    [titleCase(result.date_kind) || 'Date', fmtDate(result.date)],
  ]));
  const experiments = (result.experiment_ids || []).map((eid) => ATLAS.experiments[eid]).filter(Boolean);
  if (experiments.length) {
    frag.appendChild(section('Experiment', [h('ul', { class: 'entity-list' }, experiments.map((e) => h('li', {}, linkTo(idRoute(e.id), e.name))))]));
  }
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
  frag.appendChild(section('Publication', pubLinks.length ? [h('ul', { class: 'entity-list' }, pubLinks)] : [emptyNote('No publication links recorded.')], { open: false }));

  frag.appendChild(sourcesDisclosure(id, result));
  return frag;
}

// ----------------------------------------------------------------- document
async function renderDocument(id) {
  const { byId } = await loader.getDocuments();
  const document_ = byId.get(id);
  if (!document_) return emptyNote('Unknown document.');
  const frag = document.createDocumentFragment();
  // The bundle's document records carry `name` and `date`, not `title` and
  // `year` — reading the latter left every document panel's heading blank
  // and its subtitle a dangling "Technical Design Report · " with nothing
  // after the separator, for all ~56 documents in the atlas.
  frag.appendChild(h('h2', {}, document_.name));
  frag.appendChild(h('p', { class: 'panel-subtitle' }, `${titleCase(document_.doc_type)} · ${fmtDate(document_.date)}`));
  frag.appendChild(h('p', {}, h('a', { href: document_.reference && document_.reference.url, target: '_blank', rel: 'noopener' }, 'Open document (new tab)')));
  if (document_.volumes && document_.volumes.length) {
    frag.appendChild(section('Volumes', [h('ul', { class: 'entity-list' }, document_.volumes.map((v) => h('li', {}, h('a', { href: v.url, target: '_blank', rel: 'noopener' }, v.title))))]));
  }
  const owners = (document_.owner_ids || []).map((oid) => ({ id: oid, route: idRoute(oid), record: INDEX.get(oid) })).filter((o) => o.record);
  frag.appendChild(section('Owners', owners.length
    ? [h('ul', { class: 'entity-list' }, owners.map((o) => h('li', {}, linkTo(o.route, o.record.name))))]
    : [emptyNote('No owners recorded.')], { open: false }));
  return frag;
}

// ---------------------------------------------------------------------- site
async function renderSite(id, timelineState) {
  const site = ATLAS.sites[id];
  if (!site) return emptyNote('Unknown site.');
  const text = await loader.getText();
  const t = text[id] || {};

  const frag = document.createDocumentFragment();
  frag.appendChild(h('h2', {}, site.name));
  const place = site.place ? [site.place.city, site.place.country].filter(Boolean).join(', ') : '';
  frag.appendChild(h('p', { class: 'panel-subtitle' }, [titleCase(site.setting), place].filter(Boolean).join(' · ')));
  frag.appendChild(experimentBadge(site, timelineState));
  // ---- local map view hook (§4): the compact subtitle-area affordance
  const mapChip = localMapChip(site);
  if (mapChip) frag.appendChild(mapChip);

  // A23: coordinates.approximate only exists on the generated tree's nested
  // shape; the fixtures' flat lat/lon predate the amendment and are never
  // approximate, so siteLocationNote() silently returns null there.
  const locationNote = siteLocationNote(site);
  const coordText = (site.lat != null && site.lon != null)
    ? `${site.lat.toFixed(4)}, ${site.lon.toFixed(4)}${site.precision_m != null ? ` (±${site.precision_m} m${site.coord_kind ? `, ${titleCase(site.coord_kind)}` : ''})` : ''}`
    : '';
  const siteSummary = plainSummaryOf(site, t);
  frag.appendChild(section('Overview', [
    siteSummary ? h('p', {}, siteSummary) : emptyNote('No plain-language summary yet.'),
    keyValueList([
      ['Aliases', (site.aliases || []).join(', ')],
      ['Country', (site.countries && site.countries.length ? site.countries.join(', ') : site.country) || ''],
      ['Coordinates', coordText],
    ]),
    locationNote,
  ]));

  const quantRows = [
    ['Depth', siteQuantity(site.depth != null ? site.depth : site.depth_m, 'm')],
    ['Depth (water equivalent)', siteQuantity(site.depth_mwe, 'm.w.e.')],
    ['Altitude', siteQuantity(site.altitude != null ? site.altitude : site.altitude_m, 'm')],
  ].filter(([, v]) => v);
  frag.appendChild(section('Depth and altitude', quantRows.length
    ? [keyValueList(quantRows)]
    : [emptyNote('No depth or altitude recorded.')], { open: false }));

  const facility = site.facility_id && ATLAS.facilities[site.facility_id];
  frag.appendChild(section('Facility', facility
    ? [linkTo(idRoute(facility.id), facility.name)]
    : [emptyNote('No facility recorded for this site.')]));

  // Sites carry no derived `detector_ids` inverse list in the generated
  // bundle (docs/HEP_ATLAS_BUNDLES.md's inverse-list table stops at `site:
  // document_ids`) — derive "placed here" by scanning every detector's own
  // `placements` for this site id, which both trees carry.
  const detectorsHere = Object.values(ATLAS.detectors || {})
    .map((detector) => ({ detector, placement: (detector.placements || []).find((p) => p.site_id === id) }))
    .filter((row) => row.placement);
  frag.appendChild(section('Detectors placed here', detectorsHere.length
    ? [h('ul', { class: 'entity-list' }, detectorsHere.map(({ detector, placement }) => h('li', { class: 'entity-link-with-meta' }, [
      linkTo(idRoute(detector.id), detector.name),
      placement.role ? ` — ${titleCase(placement.role)}` : '',
      (placement.start || placement.end) ? ` (${placement.start || '?'}–${placement.end || 'present'})` : '',
    ])))]
    : [emptyNote('No detectors recorded at this site.')]));

  const experimentIds = new Set();
  for (const { detector } of detectorsHere) {
    for (const eid of detector.experiment_ids || []) experimentIds.add(eid);
  }
  const experimentsHosted = [...experimentIds].map((eid) => ATLAS.experiments[eid]).filter(Boolean);
  frag.appendChild(section('Experiments hosted', experimentsHosted.length
    ? [h('ul', { class: 'entity-list' }, experimentsHosted.map((e) => h('li', {}, linkTo(idRoute(e.id), e.name))))]
    : [emptyNote('No experiments recorded at this site.')]));

  const acceleratorsHere = Object.values(ATLAS.accelerators || {}).filter((a) => a.site_id === id);
  frag.appendChild(section('Accelerators sited here', acceleratorsHere.length
    ? [h('ul', { class: 'entity-list' }, acceleratorsHere.map((a) => h('li', {}, linkTo(idRoute(a.id), a.name))))]
    : [emptyNote('No accelerators recorded at this site.')], { open: false }));

  const beamlinesHere = Object.values(ATLAS.beamlines || {}).filter((b) => (b.near_detector_site_ids || []).includes(id)
    || (b.far_detector_site_ids || []).includes(id));
  frag.appendChild(section('Beamlines', beamlinesHere.length
    ? [h('ul', { class: 'entity-list' }, beamlinesHere.map((b) => h('li', {}, linkTo(idRoute(b.id), b.name))))]
    : [emptyNote('No beamlines recorded at this site.')], { open: false }));

  const documents = await documentsFor(id, site);
  frag.appendChild(section('Documents', documents.length
    ? [h('ul', { class: 'entity-list' }, documents.map((d) => h('li', {},
      h('a', { href: d.reference && d.reference.url, target: '_blank', rel: 'noopener' }, d.name))))]
    : [emptyNote('No documents recorded.')], { open: false }));

  // ---- local map view hook (§4)
  const mapSection = localMapLinks(site);
  if (mapSection) frag.appendChild(mapSection);

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
  frag.appendChild(h('h2', {}, detector.name));
  const techLabel = [detector.technology, (detector.technology_classes || []).map(titleCase).join(', ')]
    .filter(Boolean).join(' · ');
  if (techLabel) frag.appendChild(h('p', { class: 'panel-subtitle' }, techLabel));
  frag.appendChild(experimentBadge(detector, timelineState));
  // ---- local map view hook (§4): the compact subtitle-area affordance
  const mapChip = localMapChip(detector);
  if (mapChip) frag.appendChild(mapChip);

  const detectorSummary = plainSummaryOf(detector, t);
  frag.appendChild(section('Overview', [
    detectorSummary ? h('p', {}, detectorSummary) : emptyNote('No plain-language summary yet.'),
    keyValueList([['Aliases', (detector.aliases || []).join(', ')]]),
  ]));

  const specRows = Object.entries(detector.specs || {}).map(([k, v]) => [titleCase(k), quantityText(v)]);
  frag.appendChild(section('Specifications', specRows.length
    ? [keyValueList(specRows)]
    : [emptyNote('No technical specifications recorded.')], { open: false }));

  const placements = detector.placements || [];
  frag.appendChild(section('Placements', placements.length
    ? [h('ul', { class: 'entity-list' }, placements.map((p) => {
      const site = ATLAS.sites[p.site_id];
      return h('li', { class: 'entity-link-with-meta' }, [
        site ? linkTo(idRoute(site.id), site.name) : document.createTextNode(p.site_id),
        p.role ? ` — ${titleCase(p.role)}` : '',
        (p.start || p.end) ? ` (${p.start || '?'}–${p.end || 'present'})` : '',
      ]);
    }))]
    : [emptyNote('No placement recorded.')]));

  const experimentsHere = (detector.experiment_ids || []).map((eid) => ATLAS.experiments[eid]).filter(Boolean);
  frag.appendChild(section('Experiments', experimentsHere.length
    ? [h('ul', { class: 'entity-list' }, experimentsHere.map((e) => h('li', {}, linkTo(idRoute(e.id), e.name))))]
    : [emptyNote('No experiments recorded.')]));

  const parent = detector.parent_detector_id && ATLAS.detectors[detector.parent_detector_id];
  const children = Object.values(ATLAS.detectors || {}).filter((d) => d.parent_detector_id === id);
  frag.appendChild(section('Parent and child detectors', [
    h('h4', {}, 'Parent'),
    parent ? h('p', {}, linkTo(idRoute(parent.id), parent.name)) : emptyNote('No parent detector recorded.'),
    h('h4', {}, 'Child detectors'),
    children.length
      ? h('ul', { class: 'entity-list' }, children.map((c) => h('li', {}, linkTo(idRoute(c.id), c.name))))
      : emptyNote('No child detectors recorded.'),
  ], { open: false }));

  const subsystems = (detector.subsystems || []).map(subsystemNode).filter(Boolean);
  frag.appendChild(section('Subsystems', subsystems.length
    ? [h('ul', { class: 'entity-list' }, subsystems)]
    : [emptyNote('No subsystems recorded.')], { open: false }));

  const documents = await documentsFor(id, detector);
  frag.appendChild(section('Documents', documents.length
    ? [h('ul', { class: 'entity-list' }, documents.map((d) => h('li', {},
      h('a', { href: d.reference && d.reference.url, target: '_blank', rel: 'noopener' }, d.name))))]
    : [emptyNote('No documents recorded.')], { open: false }));

  // ---- local map view hook (§4)
  const mapSection = localMapLinks(detector);
  if (mapSection) frag.appendChild(mapSection);

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
  frag.appendChild(h('h2', {}, accelerator.name));
  frag.appendChild(h('p', { class: 'panel-subtitle' }, titleCase(accelerator.kind)));
  frag.appendChild(experimentBadge(accelerator, timelineState));
  // ---- local map view hook (§4): the compact subtitle-area affordance
  const mapChip = localMapChip(accelerator);
  if (mapChip) frag.appendChild(mapChip);

  const acceleratorSummary = plainSummaryOf(accelerator, t);
  frag.appendChild(section('Overview', [
    acceleratorSummary ? h('p', {}, acceleratorSummary) : emptyNote('No plain-language summary yet.'),
    keyValueList([
      ['Aliases', (accelerator.aliases || []).join(', ')],
      ['Collider', accelerator.is_collider ? 'Yes' : 'No'],
      ['Particles', (accelerator.particles || []).join(', ')],
    ]),
  ]));

  const specRows = Object.entries(accelerator.specs || {}).map(([k, v]) => [titleCase(k), quantityText(v)]);
  frag.appendChild(section('Specifications', specRows.length
    ? [keyValueList(specRows)]
    : [emptyNote('No technical specifications recorded.')], { open: false }));

  const facility = accelerator.facility_id && ATLAS.facilities[accelerator.facility_id];
  const site = accelerator.site_id && ATLAS.sites[accelerator.site_id];
  frag.appendChild(section('Facility and site', [
    facility ? h('p', { class: 'entity-link-with-meta' }, ['Facility: ', linkTo(idRoute(facility.id), facility.name)]) : emptyNote('No facility recorded.'),
    site ? h('p', { class: 'entity-link-with-meta' }, ['Site: ', linkTo(idRoute(site.id), site.name)]) : emptyNote('No site recorded.'),
  ]));

  const feeds = (accelerator.feeds_accelerator_ids || []).map((aid) => ATLAS.accelerators[aid]).filter(Boolean);
  // `fed_by_accelerator_ids` is a generated-tree-only derived field (never
  // present, not even empty, on the fixtures' accelerator records).
  const fedBy = (accelerator.fed_by_accelerator_ids || []).map((aid) => ATLAS.accelerators[aid]).filter(Boolean);
  frag.appendChild(section('Accelerator chain', [
    h('h4', {}, 'Feeds'),
    feeds.length ? h('ul', { class: 'entity-list' }, feeds.map((a) => h('li', {}, linkTo(idRoute(a.id), a.name)))) : emptyNote('None recorded.'),
    h('h4', {}, 'Fed by'),
    fedBy.length ? h('ul', { class: 'entity-list' }, fedBy.map((a) => h('li', {}, linkTo(idRoute(a.id), a.name)))) : emptyNote('None recorded.'),
  ], { open: false }));

  const beamlinesHere = (accelerator.beamline_ids || []).map((bid) => ATLAS.beamlines[bid]).filter(Boolean);
  frag.appendChild(section('Beamlines', beamlinesHere.length
    ? [h('ul', { class: 'entity-list' }, beamlinesHere.map((b) => h('li', {}, linkTo(idRoute(b.id), b.name))))]
    : [emptyNote('No beamlines recorded.')]));

  const servedExperiments = (accelerator.serves_experiment_ids || []).map((eid) => ATLAS.experiments[eid]).filter(Boolean);
  frag.appendChild(section('Experiments served', servedExperiments.length
    ? [h('ul', { class: 'entity-list' }, servedExperiments.map((e) => h('li', {}, linkTo(idRoute(e.id), e.name))))]
    : [emptyNote('No experiments recorded.')]));

  // `intervals` is absent on the fixtures' accelerator/beamline records (only
  // the generated tree's build derives it) — state_segments still drives the
  // status badge above either way, so this only ever loses the fixtures'
  // human-readable timeline, not their status.
  const intervals = accelerator.intervals || [];
  frag.appendChild(section('Timeline', intervals.length
    ? [h('ul', { class: 'entity-list' }, intervals.map((iv) => h('li', {}, intervalLine(iv))))]
    : [emptyNote('No interval history recorded.')], { open: false }));

  const documents = await documentsFor(id, accelerator);
  frag.appendChild(section('Documents', documents.length
    ? [h('ul', { class: 'entity-list' }, documents.map((d) => h('li', {},
      h('a', { href: d.reference && d.reference.url, target: '_blank', rel: 'noopener' }, d.name))))]
    : [emptyNote('No documents recorded.')], { open: false }));

  // ---- local map view hook (§4)
  const mapSection = localMapLinks(accelerator);
  if (mapSection) frag.appendChild(mapSection);

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
  frag.appendChild(h('h2', {}, beamline.name));
  frag.appendChild(experimentBadge(beamline, timelineState));
  // ---- local map view hook (§4): the compact subtitle-area affordance
  const mapChip = localMapChip(beamline);
  if (mapChip) frag.appendChild(mapChip);

  const beamlineSummary = plainSummaryOf(beamline, t);
  const primaryBeam = beamline.primary_beam || {};
  const primaryBeamText = [primaryBeam.particle, primaryBeam.energy ? quantityText(primaryBeam.energy) : null]
    .filter(Boolean).join(' · ');
  frag.appendChild(section('Overview', [
    beamlineSummary ? h('p', {}, beamlineSummary) : emptyNote('No plain-language summary yet.'),
    keyValueList([
      ['Aliases', (beamline.aliases || []).join(', ')],
      ['Primary beam', primaryBeamText],
      ['Secondary beam', beamline.secondary_beam],
      ['Target', beamline.target],
      ['Direction', beamline.direction],
    ]),
  ]));

  const specRows = Object.entries(beamline.specs || {}).map(([k, v]) => [titleCase(k), quantityText(v)]);
  frag.appendChild(section('Specifications', specRows.length
    ? [keyValueList(specRows)]
    : [emptyNote('No technical specifications recorded.')], { open: false }));

  const facility = beamline.facility_id && ATLAS.facilities[beamline.facility_id];
  const accelerator = beamline.accelerator_id && ATLAS.accelerators[beamline.accelerator_id];
  frag.appendChild(section('Facility and accelerator', [
    facility ? h('p', { class: 'entity-link-with-meta' }, ['Facility: ', linkTo(idRoute(facility.id), facility.name)]) : emptyNote('No facility recorded.'),
    accelerator ? h('p', { class: 'entity-link-with-meta' }, ['Accelerator: ', linkTo(idRoute(accelerator.id), accelerator.name)]) : emptyNote('No accelerator recorded.'),
  ]));

  function siteLi(sid) {
    const site = ATLAS.sites[sid];
    return h('li', {}, site ? linkTo(idRoute(site.id), site.name) : document.createTextNode(sid));
  }
  const nearSites = beamline.near_detector_site_ids || [];
  const farSites = beamline.far_detector_site_ids || [];
  const baselines = beamline.baselines || [];
  frag.appendChild(section('Near and far detector sites', [
    h('h4', {}, 'Near'),
    nearSites.length ? h('ul', { class: 'entity-list' }, nearSites.map(siteLi)) : emptyNote('None recorded.'),
    h('h4', {}, 'Far'),
    farSites.length ? h('ul', { class: 'entity-list' }, farSites.map(siteLi)) : emptyNote('None recorded.'),
    baselines.length ? h('div', {}, [
      h('h4', {}, 'Baselines'),
      h('ul', { class: 'entity-list' }, baselines.map((b) => {
        const from = ATLAS.sites[b.from_site_id];
        const to = ATLAS.sites[b.to_site_id];
        const distance = b.distance ? quantityText(b.distance) : '';
        return h('li', {}, `${from ? from.name : b.from_site_id} → ${to ? to.name : b.to_site_id}${distance ? `: ${distance}` : ''}`);
      })),
    ]) : null,
  ]));

  const beamlineExperiments = (beamline.experiment_ids || []).map((eid) => ATLAS.experiments[eid]).filter(Boolean);
  frag.appendChild(section('Experiments', beamlineExperiments.length
    ? [h('ul', { class: 'entity-list' }, beamlineExperiments.map((e) => h('li', {}, linkTo(idRoute(e.id), e.name))))]
    : [emptyNote('No experiments recorded.')]));

  const intervals = beamline.intervals || [];
  frag.appendChild(section('Timeline', intervals.length
    ? [h('ul', { class: 'entity-list' }, intervals.map((iv) => h('li', {}, intervalLine(iv))))]
    : [emptyNote('No interval history recorded.')], { open: false }));

  const documents = await documentsFor(id, beamline);
  frag.appendChild(section('Documents', documents.length
    ? [h('ul', { class: 'entity-list' }, documents.map((d) => h('li', {},
      h('a', { href: d.reference && d.reference.url, target: '_blank', rel: 'noopener' }, d.name))))]
    : [emptyNote('No documents recorded.')], { open: false }));

  // ---- local map view hook (§4)
  const mapSection = localMapLinks(beamline);
  if (mapSection) frag.appendChild(mapSection);

  frag.appendChild(sourcesDisclosure(id, beamline));
  const focusSite = nearSites[0] || farSites[0];
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
