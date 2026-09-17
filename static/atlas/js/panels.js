// panels.js — detail panels with progressive disclosure (native <details>).
// Facility / experiment / collaboration / institution / topic / result /
// document. Long text (text.json) and citations (provenance.json) are
// fetched lazily, on first panel open, via loader.js (which itself caches).

import * as loader from './loader.js';
import { quantityText, fmtDate, titleCase } from './model.js';

let ATLAS = null;
let INDEX = null;
let CALLBACKS = {};
let lastCollaborationId = null;
let container = null;

export function init({ el, atlas, index, navigate, focusGlobe, viewOnGlobe }) {
  container = el;
  ATLAS = atlas;
  INDEX = index;
  CALLBACKS = { navigate, focusGlobe, viewOnGlobe };
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
    el.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
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

async function sourcesDisclosure(entityId) {
  const [provenance, sourcesBundle] = await Promise.all([loader.getProvenance(), loader.getSources()]);
  const entries = provenance[entityId];
  const items = [];
  if (entries) {
    for (const [pointer, record] of Object.entries(entries)) {
      const srcIds = record.sources || [];
      for (const srcId of srcIds) {
        const src = sourcesBundle.byId[srcId];
        if (!src) continue;
        const locatorOrQuote = record.quote ? `“${record.quote}”` : (record.locator || '');
        items.push(h('li', {}, [
          h('a', { href: src.url || '#', target: '_blank', rel: 'noopener' }, src.title || srcId),
          h('div', { class: 'source-meta' }, `${pointer}${locatorOrQuote ? ` — ${locatorOrQuote}` : ''}`),
          h('div', { class: 'source-access' }, src.accessed ? `Accessed ${src.accessed}` : ''),
        ]));
      }
    }
  }
  return section('Sources', items.length
    ? [h('ul', { class: 'source-list' }, items)]
    : [emptyNote('No sourced fields recorded for this entity yet.')], { open: false });
}

function experimentBadge(exp) {
  const div = h('div', { class: `status-badge status-${exp.status}` }, titleCase(exp.status));
  return div;
}

// ------------------------------------------------------------------ facility
async function renderFacility(id) {
  const facility = ATLAS.facilities[id];
  if (!facility) return emptyNote('Unknown facility.');
  const text = await loader.getText();
  const t = text[id] || {};

  const experiments = (facility.experiment_ids || []).map((eid) => ATLAS.experiments[eid]).filter(Boolean);
  const current = experiments.filter((e) => e.status === 'active' || e.status === 'commissioning');
  const historical = experiments.filter((e) => !current.includes(e));

  const { list: allResults } = await loader.getResults();
  const { list: allDocuments } = await loader.getDocuments();
  const results = allResults.filter((r) => (r.facility_ids || []).includes(id));
  const documents = allDocuments.filter((d) => (d.owner_ids || []).includes(id)
    || (facility.document_ids || []).includes(d.id));

  const frag = document.createDocumentFragment();
  frag.appendChild(h('h2', {}, facility.name));
  frag.appendChild(h('p', { class: 'panel-subtitle' }, titleCase(facility.kind)));
  frag.appendChild(experimentBadge(facility));

  frag.appendChild(section('Overview', [
    t.summary_plain ? h('p', {}, t.summary_plain) : emptyNote('No plain-language summary yet.'),
    keyValueList([
      ['Aliases', (facility.aliases || []).join(', ')],
      ['Operator', facility.operator],
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
    : [emptyNote('No historical experiments recorded.')], { open: false }));

  frag.appendChild(section('Results', results.length
    ? [h('ul', { class: 'entity-list' }, results.map((r) => h('li', {}, linkTo(idRoute(r.id), r.title))))]
    : [emptyNote('No results attributed directly to this facility.')], { open: false }));

  frag.appendChild(section('Documents', documents.length
    ? [h('ul', { class: 'entity-list' }, documents.map((d) => h('li', {},
      h('a', { href: d.reference && d.reference.url, target: '_blank', rel: 'noopener' }, d.title))))]
    : [emptyNote('No documents recorded.')], { open: false }));

  const links = Object.entries(facility.links || {}).filter(([, v]) => v);
  frag.appendChild(section('Official links', links.length
    ? [h('ul', { class: 'entity-list' }, links.map(([k, v]) => h('li', {}, h('a', { href: v, target: '_blank', rel: 'noopener' }, `${titleCase(k)}: ${v}`))))]
    : [emptyNote('No official links recorded.')], { open: false }));

  const related = (facility.related_facility_ids || []).map((rid) => ATLAS.facilities[rid]).filter(Boolean);
  frag.appendChild(section('Related facilities', related.length
    ? [h('ul', { class: 'entity-list' }, related.map((r) => h('li', {}, linkTo(idRoute(r.id), r.name))))]
    : [emptyNote('No related facilities recorded.')], { open: false }));

  frag.appendChild(await sourcesDisclosure(id));
  CALLBACKS.focusGlobe(id);
  return frag;
}

// ---------------------------------------------------------------- experiment
async function renderExperiment(id) {
  const exp = ATLAS.experiments[id];
  if (!exp) return emptyNote('Unknown experiment.');
  const text = await loader.getText();
  const t = text[id] || {};

  const frag = document.createDocumentFragment();
  frag.appendChild(h('h2', {}, exp.name));
  frag.appendChild(h('p', { class: 'panel-subtitle' }, titleCase(exp.kind)));
  frag.appendChild(experimentBadge(exp));

  const collabs = (exp.collaboration_ids || []).map((cid) => ATLAS.collaborations[cid]).filter(Boolean);
  if (collabs.length) {
    frag.appendChild(h('p', { class: 'collab-line' }, [
      'Collaboration: ',
      ...collabs.flatMap((c, i) => (i === 0 ? [linkTo(idRoute(c.id), c.name, 'collab-link')] : [document.createTextNode(', '), linkTo(idRoute(c.id), c.name, 'collab-link')])),
    ]));
  }

  frag.appendChild(section('What it studies', [
    t.summary_plain ? h('p', { class: 'plain-summary' }, t.summary_plain) : emptyNote('No plain-language summary yet.'),
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
  frag.appendChild(section('Beam and sites', [
    beamlines.length ? h('ul', { class: 'entity-list' }, beamlines.map((b) => h('li', {},
      `${b.name}: ${(b.baselines || []).map((base) => base.distance ? base.distance.display : '').join(', ')}`))) : emptyNote('No beamline.'),
    sites.length ? h('ul', { class: 'entity-list' }, sites.map((s) => h('li', {}, linkTo({ type: 'facility', slug: (s.facility_id || s.id).split(':')[1] }, `${s.name} (${s.setting})`)))) : null,
  ], { open: false }));

  const { byId: resultById } = await loader.getResults();
  const results = (exp.result_ids || []).map((rid) => resultById.get(rid)).filter(Boolean)
    .sort((a, b) => (a.month || 0) - (b.month || 0));
  frag.appendChild(section('Results timeline', results.length
    ? [h('ol', { class: 'entity-list timeline-list' }, results.map((r) => h('li', {}, [
      h('span', { class: 'result-date' }, r.date || String(r.year || '')),
      ' ',
      linkTo(idRoute(r.id), r.title),
    ])))]
    : [emptyNote('No results recorded yet.')], { open: false }));

  const { byId: docById } = await loader.getDocuments();
  const documents = (exp.document_ids || []).map((did) => docById.get(did)).filter(Boolean);
  frag.appendChild(section('Documents', documents.length
    ? [h('ul', { class: 'entity-list' }, documents.map((d) => h('li', {},
      h('a', { href: d.reference && d.reference.url, target: '_blank', rel: 'noopener' }, d.title))))]
    : [emptyNote('No documents recorded.')], { open: false }));

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

  frag.appendChild(await sourcesDisclosure(id));
  CALLBACKS.focusGlobe(id);
  return frag;
}

// ------------------------------------------------------------- collaboration
async function renderCollaboration(id) {
  const collab = ATLAS.collaborations[id];
  if (!collab) return emptyNote('Unknown collaboration.');
  const text = await loader.getText();
  const t = text[id] || {};
  const host = collab.host_facility_id && ATLAS.facilities[collab.host_facility_id];

  const frag = document.createDocumentFragment();
  frag.appendChild(h('h2', {}, collab.name));
  frag.appendChild(experimentBadge(collab));

  const summary = t.summary_plain
    || `Formed ${collab.formation || 'at an unrecorded date'}${host ? `, hosted at ${host.name}` : ''}.`;
  frag.appendChild(section('Summary', [h('p', {}, summary)]));

  frag.appendChild(section('Host facility', host
    ? [linkTo(idRoute(host.id), host.name)]
    : [emptyNote('No host facility recorded.')]));

  const viewBtn = h('button', { type: 'button', id: 'view-on-globe', class: 'primary-btn' }, 'View collaboration on globe');
  viewBtn.addEventListener('click', () => CALLBACKS.viewOnGlobe(id));
  frag.appendChild(h('div', { class: 'panel-actions' }, viewBtn));

  const countLabel = (collab.membership && collab.membership.count_label)
    || `${(collab.membership && collab.membership.confirmed_count) || 0} confirmed members`;
  frag.appendChild(section('Membership', [
    h('p', { class: 'membership-count' }, countLabel),
    keyValueList([
      ['Institutions', collab.membership && collab.membership.institution_count],
      ['Countries', collab.membership && collab.membership.country_count],
      ['As of', collab.membership && collab.membership.as_of],
    ]),
  ]));

  frag.appendChild(await sourcesDisclosure(id));
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
  const filterRow = h('div', { class: 'role-filter', role: 'group', 'aria-label': 'Filter by role' },
    ROLE_FILTERS.map((f) => h('button', { type: 'button', class: `role-btn${f.id === 'all' ? ' is-active' : ''}`, 'data-role': f.id }, f.label)));
  const peopleList = h('ul', { class: 'people-list', id: 'people-list' });
  peopleSection.append(filterRow, peopleList);

  let people = [];
  if (row && row.people_bundle) {
    const bundle = await loader.getPeople(row.people_bundle);
    people = bundle.people || [];
  }

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
        h('span', { class: 'person-role' }, ` — ${titleCase(person.role)}`),
        h('div', { class: 'person-evidence' }, person.evidence_label),
      ]);
      if (person.hep_graph && person.hep_graph.available && person.hep_graph.url) {
        li.appendChild(h('a', { href: person.hep_graph.url, target: '_blank', rel: 'noopener', class: 'hep-graph-link' }, 'Open in HEP Graph'));
      }
      peopleList.appendChild(li);
    }
  }
  filterRow.addEventListener('click', (event) => {
    const btn = event.target.closest('.role-btn');
    if (!btn) return;
    for (const b of filterRow.querySelectorAll('.role-btn')) b.classList.toggle('is-active', b === btn);
    renderPeople(btn.dataset.role);
  });
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

  const experiments = (topic.experiment_ids || []).map((eid) => ATLAS.experiments[eid]).filter(Boolean);
  const current = experiments.filter((e) => ['active', 'commissioning'].includes(e.status));
  const historical = experiments.filter((e) => ['completed', 'decommissioned', 'shutdown'].includes(e.status));
  const future = experiments.filter((e) => !current.includes(e) && !historical.includes(e));
  function expList(list) {
    return list.length ? h('ul', { class: 'entity-list' }, list.map((e) => h('li', {}, linkTo(idRoute(e.id), e.name)))) : emptyNote('None.');
  }
  frag.appendChild(section('Experiments', [
    h('h4', {}, 'Current'), expList(current),
    h('h4', {}, 'Historical'), expList(historical),
    h('h4', {}, 'Future / planned'), expList(future),
  ]));

  const { byId: resultById } = await loader.getResults();
  const results = (topic.result_ids || []).map((rid) => resultById.get(rid)).filter(Boolean);
  frag.appendChild(section('Related results', results.length
    ? [h('ul', { class: 'entity-list' }, results.map((r) => h('li', {}, linkTo(idRoute(r.id), r.title))))]
    : [emptyNote('No results recorded yet.')], { open: false }));

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
  frag.appendChild(keyValueList([
    ['Significance', result.significance],
    ['Key value', result.key_value_text],
    ['Announced', result.announced],
    ['Published', result.published],
  ]));
  const experiments = (result.experiment_ids || []).map((eid) => ATLAS.experiments[eid]).filter(Boolean);
  if (experiments.length) {
    frag.appendChild(section('Experiment', [h('ul', { class: 'entity-list' }, experiments.map((e) => h('li', {}, linkTo(idRoute(e.id), e.name))))]));
  }
  const pub = result.publication || {};
  const pubLinks = [];
  if (pub.doi) pubLinks.push(h('li', {}, h('a', { href: `https://doi.org/${pub.doi}`, target: '_blank', rel: 'noopener' }, `DOI ${pub.doi}`)));
  if (pub.arxiv) pubLinks.push(h('li', {}, h('a', { href: `https://arxiv.org/abs/${pub.arxiv}`, target: '_blank', rel: 'noopener' }, `arXiv ${pub.arxiv}`)));
  if (result.official_url) pubLinks.push(h('li', {}, h('a', { href: result.official_url, target: '_blank', rel: 'noopener' }, 'Official page')));
  frag.appendChild(section('Publication', pubLinks.length ? [h('ul', { class: 'entity-list' }, pubLinks)] : [emptyNote('No publication links recorded.')], { open: false }));

  frag.appendChild(await sourcesDisclosure(id));
  return frag;
}

// ----------------------------------------------------------------- document
async function renderDocument(id) {
  const { byId } = await loader.getDocuments();
  const document_ = byId.get(id);
  if (!document_) return emptyNote('Unknown document.');
  const frag = document.createDocumentFragment();
  frag.appendChild(h('h2', {}, document_.title));
  frag.appendChild(h('p', { class: 'panel-subtitle' }, `${titleCase(document_.doc_type)} · ${document_.year || ''}`));
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

const RENDERERS = {
  facility: renderFacility,
  experiment: renderExperiment,
  collaboration: renderCollaboration,
  institution: renderInstitution,
  topic: renderTopic,
  result: renderResult,
  document: renderDocument,
};

export async function render(route) {
  if (!route) {
    container.innerHTML = '';
    container.classList.add('hidden');
    return;
  }
  const id = `${route.type}:${route.slug}`;
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
    const frag = await renderer(id);
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
