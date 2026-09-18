// modes.js — the three browsing modes that sit beside the default globe
// view: a research-topic tree, a filterable results list, and the document
// library. Each renders into the #mode-panel container.

import { titleCase, fmtDate } from './model.js';

let ctx = null; // { container, atlas, results, documents, navigate, highlightGlobe, setTimelineYear }

/** The human label of a record.
 *
 * Documents carry `name`; results carry both a `name` (the atlas's short
 * label) and a `title` (the publication's own wording). Reading only `title`
 * left every document in the library blank.
 */
function labelOf(record) {
  return record.name || record.title || record.id;
}

/** The year of a record, from its date; there is no `year` field. */
function yearOf(record) {
  const date = record.date && (record.date.date || record.date);
  const match = typeof date === 'string' ? /^(\d{4})/.exec(date) : null;
  return match ? Number(match[1]) : null;
}

export function init(context) {
  ctx = context;
}

function h(tag, attrs = {}, children = []) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (k === 'class') el.className = v;
    else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
    else if (v !== null && v !== undefined) el.setAttribute(k, v);
  }
  for (const child of [].concat(children)) {
    if (child == null) continue;
    el.appendChild((typeof child === 'string' || typeof child === 'number') ? document.createTextNode(String(child)) : child);
  }
  return el;
}

function goto(route) {
  ctx.navigate({ entity: route, mode: null });
}

// -------------------------------------------------------------- topic mode
function topicChildren(topics, parentId) {
  return Object.values(topics).filter((t) => t.parent_id === parentId);
}

function renderTopicNode(topics, topic) {
  const children = topicChildren(topics, topic.id);
  const li = h('li', {});
  const link = h('a', { href: `#/topic/${topic.id.split(':')[1]}`, class: 'topic-link' }, topic.name);
  link.addEventListener('click', (event) => {
    event.preventDefault();
    const matches = new Set([topic.id, ...(topic.experiment_ids || []), ...(topic.facility_ids || [])]);
    ctx.highlightGlobe(matches);
    goto({ type: 'topic', slug: topic.id.split(':')[1] });
  });
  li.appendChild(link);
  if (children.length) {
    li.appendChild(h('ul', { class: 'topic-tree-children' }, children.map((c) => renderTopicNode(topics, c))));
  }
  return li;
}

function renderTopicMode() {
  const topics = ctx.atlas.topics;
  const roots = topicChildren(topics, null).concat(topicChildren(topics, undefined));
  const tree = h('ul', { class: 'topic-tree' }, roots.map((r) => renderTopicNode(topics, r)));
  return h('div', { class: 'mode-body' }, [
    h('h2', {}, 'Research topics'),
    h('p', { class: 'mode-hint' }, 'Select a topic to highlight its experiments and facilities on the globe.'),
    tree,
  ]);
}

// ------------------------------------------------------------- results mode
function uniqueSorted(values) {
  return [...new Set(values.filter(Boolean))].sort();
}

function renderResultsMode() {
  const results = ctx.results.list;
  const experimentNames = new Map(Object.values(ctx.atlas.experiments).map((e) => [e.id, e.name]));
  const facilityNames = new Map(Object.values(ctx.atlas.facilities).map((f) => [f.id, f.name]));
  const topicNames = new Map(Object.values(ctx.atlas.topics).map((t) => [t.id, t.name]));

  const years = uniqueSorted(results.map((r) => yearOf(r)));
  const types = uniqueSorted(results.map((r) => r.result_type));
  const experiments = uniqueSorted(results.flatMap((r) => r.experiment_ids || []));
  const facilities = uniqueSorted(results.flatMap((r) => r.facility_ids || []));
  const topics = uniqueSorted(results.flatMap((r) => r.topic_ids || []));

  const filters = { year: '', experiment: '', facility: '', topic: '', type: '' };

  function select(id, label, options, nameMap) {
    const sel = h('select', { id, 'aria-label': label });
    sel.appendChild(h('option', { value: '' }, `All ${label.toLowerCase()}`));
    for (const opt of options) sel.appendChild(h('option', { value: opt }, nameMap ? (nameMap.get(opt) || opt) : String(opt)));
    return sel;
  }

  const yearSel = select('results-filter-year', 'Year', years);
  const expSel = select('results-filter-experiment', 'Experiment', experiments, experimentNames);
  const facSel = select('results-filter-facility', 'Facility', facilities, facilityNames);
  const topicSel = select('results-filter-topic', 'Topic', topics, topicNames);
  const typeSel = select('results-filter-type', 'Result type', types, new Map(types.map((t) => [t, titleCase(t)])));

  const list = h('ul', { class: 'results-list', id: 'results-mode-list' });

  function apply() {
    filters.year = yearSel.value;
    filters.experiment = expSel.value;
    filters.facility = facSel.value;
    filters.topic = topicSel.value;
    filters.type = typeSel.value;
    const filtered = results.filter((r) => (
      (!filters.year || String(yearOf(r)) === filters.year)
      && (!filters.experiment || (r.experiment_ids || []).includes(filters.experiment))
      && (!filters.facility || (r.facility_ids || []).includes(filters.facility))
      && (!filters.topic || (r.topic_ids || []).includes(filters.topic))
      && (!filters.type || r.result_type === filters.type)
    ));
    list.innerHTML = '';
    if (!filtered.length) {
      list.appendChild(h('li', { class: 'empty-note' }, 'No results match these filters.'));
      return;
    }
    for (const result of filtered) {
      const li = h('li', { class: 'result-row' });
      li.appendChild(h('span', { class: 'result-date' }, fmtDate(result.date) || String(yearOf(result) || '')));
      const link = h('a', { href: `#/result/${result.id.split(':')[1]}` }, labelOf(result));
      link.addEventListener('click', (event) => {
        event.preventDefault();
        const firstExp = (result.experiment_ids || [])[0];
        if (firstExp) ctx.highlightGlobe(new Set([firstExp]));
        goto({ type: 'result', slug: result.id.split(':')[1] });
      });
      li.appendChild(link);
      if (result.month != null) {
        const jump = h('button', { type: 'button', class: 'text-btn jump-year-btn' }, 'Move timeline here');
        jump.addEventListener('click', () => ctx.setTimelineYear(yearOf(result)));
        li.appendChild(jump);
      }
      list.appendChild(li);
    }
  }
  for (const sel of [yearSel, expSel, facSel, topicSel, typeSel]) sel.addEventListener('change', apply);
  apply();

  return h('div', { class: 'mode-body' }, [
    h('h2', {}, 'Results'),
    h('div', { class: 'results-filters' }, [yearSel, expSel, facSel, topicSel, typeSel]),
    list,
  ]);
}

// --------------------------------------------------------- document library
function renderDocsMode() {
  const documents = ctx.documents.list.slice().sort((a, b) => (yearOf(b) || 0) - (yearOf(a) || 0));
  const list = h('ul', { class: 'entity-list document-library' }, documents.map((d) => h('li', {}, [
    h('a', {
      href: (d.reference && d.reference.url) || '#', target: '_blank', rel: 'noopener', class: 'document-title',
    }, labelOf(d)),
    h('span', { class: 'document-meta' }, ` — ${titleCase(d.doc_type)}${d.year ? `, ${d.year}` : ''}`),
  ])));
  return h('div', { class: 'mode-body' }, [
    h('h2', {}, 'Document library'),
    list.children.length ? list : h('p', { class: 'empty-note' }, 'No documents available.'),
  ]);
}

const MODE_RENDERERS = { topic: renderTopicMode, results: renderResultsMode, docs: renderDocsMode };

// §23 "focus returning to the trigger" — same contract as panels.js's
// openerElement: capture whatever was focused (the Topics/Results/Documents
// button) only on a real mode change, restore it when the mode panel closes
// (via the Globe button or the app-level Escape handler).
let modeOpener = null;
let lastMode = null;

export function show(mode) {
  const { container } = ctx;
  if (!mode || !MODE_RENDERERS[mode]) {
    container.innerHTML = '';
    container.classList.add('hidden');
    ctx.highlightGlobe(null);
    lastMode = null;
    if (modeOpener && document.body.contains(modeOpener)) {
      modeOpener.focus({ preventScroll: true });
    }
    modeOpener = null;
    return;
  }
  if (mode !== lastMode) {
    modeOpener = document.activeElement;
    lastMode = mode;
  }
  container.classList.remove('hidden');
  container.innerHTML = '';
  container.appendChild(MODE_RENDERERS[mode]());
}
