// modes.js — the three browsing modes that sit beside the default globe
// view: a research-topic tree, a filterable results list, and the document
// library. Each renders into the #mode-panel container.

import { titleCase, fmtDate, buildIndex } from './model.js';

let ctx = null; // { container, atlas, results, documents, navigate, highlightGlobe, setTimelineYear }
// Flat id->record index over atlas.json (same groups buildIndex covers:
// facilities/sites/accelerators/beamlines/experiments/detectors/
// collaborations/topics), built once per init() and reused to resolve a
// document's owner_ids to names — those ids point at experiment/detector/
// collaboration/beamline records, never at a separate "people" bundle.
let entityIndex = null;

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

/** A month index usable for sort ordering: the record's own `month` field
 * when present (results carry it; it's what drives "Move timeline here"),
 * else a coarse fallback derived from the year alone so year-only records
 * still sort sensibly relative to dated ones. */
function monthOf(record) {
  if (typeof record.month === 'number') return record.month;
  const year = yearOf(record);
  return year != null ? year * 12 : -Infinity;
}

function nameOf(id) {
  const record = entityIndex && entityIndex.get(id);
  return (record && record.name) || id;
}

export function init(context) {
  ctx = context;
  entityIndex = buildIndex(ctx.atlas);
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

// A group-header row inside a <ul> of <li>s — valid markup (a heading can
// sit inside a list item) that axe's list/listitem rules accept, unlike
// splicing a bare <h3> directly between <li> siblings.
function groupHeaderRow(label, count) {
  return h('li', { class: 'result-group-header' }, h('h3', {}, `${label} (${count})`));
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
    h('div', { class: 'mode-scroll' }, [tree]),
  ]);
}

// ------------------------------------------------------------- results mode
function uniqueSorted(values) {
  return [...new Set(values.filter(Boolean))].sort();
}

/** Orders a filtered result list per the sort control: newest first by
 * date (the default), else alphabetically by primary experiment or by
 * result type — always with newest-first as the tiebreaker so the order
 * stays stable and useful even when many rows share a sort key. */
function sortResults(list, sortBy, experimentNames) {
  const arr = list.slice();
  if (sortBy === 'experiment') {
    arr.sort((a, b) => {
      const an = experimentNames.get((a.experiment_ids || [])[0]) || '';
      const bn = experimentNames.get((b.experiment_ids || [])[0]) || '';
      return an.localeCompare(bn) || (monthOf(b) - monthOf(a));
    });
  } else if (sortBy === 'type') {
    arr.sort((a, b) => (
      (a.result_type || '').localeCompare(b.result_type || '') || (monthOf(b) - monthOf(a))
    ));
  } else {
    arr.sort((a, b) => monthOf(b) - monthOf(a));
  }
  return arr;
}

/** Buckets an already-sorted list into [label, items[]] groups per the
 * grouping toggle, ordering the groups themselves (newest year first;
 * experiments alphabetically) — 'none' returns everything as one ungrouped
 * bucket so the caller can share the same rendering loop either way. */
function groupResults(sortedList, groupBy, experimentNames) {
  if (groupBy === 'none') return [[null, sortedList]];
  const buckets = new Map();
  for (const r of sortedList) {
    const key = groupBy === 'year' ? (yearOf(r) ?? '__unknown') : ((r.experiment_ids || [])[0] || '__unknown');
    if (!buckets.has(key)) buckets.set(key, []);
    buckets.get(key).push(r);
  }
  const keys = [...buckets.keys()];
  if (groupBy === 'year') {
    keys.sort((a, b) => {
      if (a === '__unknown') return 1;
      if (b === '__unknown') return -1;
      return b - a;
    });
  } else {
    keys.sort((a, b) => {
      const an = a === '__unknown' ? '' : (experimentNames.get(a) || a);
      const bn = b === '__unknown' ? '' : (experimentNames.get(b) || b);
      return an.localeCompare(bn);
    });
  }
  return keys.map((key) => {
    const label = key === '__unknown'
      ? (groupBy === 'year' ? 'Unknown year' : 'Unknown experiment')
      : (groupBy === 'year' ? String(key) : (experimentNames.get(key) || key));
    return [label, buckets.get(key)];
  });
}

function renderResultsMode() {
  const results = ctx.results.list;
  const experimentNames = new Map(Object.values(ctx.atlas.experiments).map((e) => [e.id, e.name]));
  const facilityNames = new Map(Object.values(ctx.atlas.facilities).map((f) => [f.id, f.name]));
  const topicNames = new Map(Object.values(ctx.atlas.topics).map((t) => [t.id, t.name]));

  const years = uniqueSorted(results.map((r) => yearOf(r)));
  const types = uniqueSorted(results.map((r) => r.result_type));
  // Every experiment in the atlas, not just ones a result already cites —
  // otherwise the dropdown could never offer an experiment with zero
  // curated results, and the distinct "No results curated yet for this
  // experiment" empty state (below) would be unreachable dead code.
  const experiments = uniqueSorted(Object.keys(ctx.atlas.experiments || {}));
  const facilities = uniqueSorted(results.flatMap((r) => r.facility_ids || []));
  const topics = uniqueSorted(results.flatMap((r) => r.topic_ids || []));

  const filters = { year: '', experiment: '', facility: '', topic: '', type: '' };
  let sortBy = 'date';
  let groupBy = 'none';

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

  const sortSel = h('select', { id: 'results-sort', 'aria-label': 'Sort by' }, [
    h('option', { value: 'date' }, 'Date (newest first)'),
    h('option', { value: 'experiment' }, 'Experiment (A–Z)'),
    h('option', { value: 'type' }, 'Result type (A–Z)'),
  ]);

  const groupYearBtn = h('button', {
    type: 'button', class: 'text-btn group-toggle', id: 'results-group-year', 'aria-pressed': 'false',
  }, 'Group by year');
  const groupExpBtn = h('button', {
    type: 'button', class: 'text-btn group-toggle', id: 'results-group-experiment', 'aria-pressed': 'false',
  }, 'Group by experiment');

  const countEl = h('p', { class: 'mode-count', role: 'status', id: 'results-count' }, '');
  const list = h('ul', { class: 'results-list', id: 'results-mode-list' });

  function buildResultRow(result) {
    const li = h('li', { class: 'result-row' });
    li.appendChild(h('span', { class: 'result-date' }, fmtDate(result.date) || String(yearOf(result) || '')));
    const main = h('div', { class: 'result-main' });
    const link = h('a', { href: `#/result/${result.id.split(':')[1]}`, class: 'result-title' }, labelOf(result));
    link.addEventListener('click', (event) => {
      event.preventDefault();
      const firstExp = (result.experiment_ids || [])[0];
      if (firstExp) ctx.highlightGlobe(new Set([firstExp]));
      goto({ type: 'result', slug: result.id.split(':')[1] });
    });
    main.appendChild(link);
    const metaParts = [];
    const expNames = (result.experiment_ids || []).map((id) => experimentNames.get(id) || id);
    if (expNames.length) metaParts.push(h('span', { class: 'result-tag' }, expNames.join(', ')));
    if (result.result_type) metaParts.push(h('span', { class: 'result-tag' }, titleCase(result.result_type)));
    if (result.significance) metaParts.push(h('span', { class: 'result-tag result-significance' }, result.significance));
    if (metaParts.length) main.appendChild(h('div', { class: 'result-meta' }, metaParts));
    li.appendChild(main);
    if (result.month != null) {
      const jump = h('button', { type: 'button', class: 'text-btn jump-year-btn' }, 'Move timeline here');
      jump.addEventListener('click', () => ctx.setTimelineYear(yearOf(result)));
      li.appendChild(jump);
    }
    return li;
  }

  // "No results match these filters" (any combination can cause zero rows)
  // vs. the more specific "No results curated yet for this experiment" —
  // the latter only when the *experiment* filter alone (ignoring every
  // other active filter) already has nothing, i.e. the atlas simply has no
  // curated results for that experiment at all, not just an unlucky filter
  // combination on top of results that do exist.
  function emptyMessage() {
    if (filters.experiment) {
      const anyForExperiment = results.some((r) => (r.experiment_ids || []).includes(filters.experiment));
      if (!anyForExperiment) return 'No results curated yet for this experiment.';
    }
    return 'No results match these filters.';
  }

  function apply() {
    filters.year = yearSel.value;
    filters.experiment = expSel.value;
    filters.facility = facSel.value;
    filters.topic = topicSel.value;
    filters.type = typeSel.value;
    sortBy = sortSel.value;
    const filtered = results.filter((r) => (
      (!filters.year || String(yearOf(r)) === filters.year)
      && (!filters.experiment || (r.experiment_ids || []).includes(filters.experiment))
      && (!filters.facility || (r.facility_ids || []).includes(filters.facility))
      && (!filters.topic || (r.topic_ids || []).includes(filters.topic))
      && (!filters.type || r.result_type === filters.type)
    ));
    countEl.textContent = `Showing ${filtered.length} of ${results.length} results`;
    list.innerHTML = '';
    if (!filtered.length) {
      list.appendChild(h('li', { class: 'empty-note' }, emptyMessage()));
      return;
    }
    const sorted = sortResults(filtered, sortBy, experimentNames);
    for (const [label, group] of groupResults(sorted, groupBy, experimentNames)) {
      if (label != null) list.appendChild(groupHeaderRow(label, group.length));
      for (const result of group) list.appendChild(buildResultRow(result));
    }
  }

  function setGroupBy(next) {
    groupBy = groupBy === next ? 'none' : next;
    groupYearBtn.setAttribute('aria-pressed', String(groupBy === 'year'));
    groupYearBtn.classList.toggle('is-active', groupBy === 'year');
    groupExpBtn.setAttribute('aria-pressed', String(groupBy === 'experiment'));
    groupExpBtn.classList.toggle('is-active', groupBy === 'experiment');
    apply();
  }
  groupYearBtn.addEventListener('click', () => setGroupBy('year'));
  groupExpBtn.addEventListener('click', () => setGroupBy('experiment'));

  for (const sel of [yearSel, expSel, facSel, topicSel, typeSel, sortSel]) sel.addEventListener('change', apply);
  apply();

  return h('div', { class: 'mode-body' }, [
    h('h2', {}, 'Results'),
    countEl,
    h('div', { class: 'results-filters' }, [yearSel, expSel, facSel, topicSel, typeSel]),
    h('div', { class: 'mode-toolbar' }, [
      sortSel,
      h('div', { class: 'group-toggle-row', role: 'group', 'aria-label': 'Group results by' }, [groupYearBtn, groupExpBtn]),
    ]),
    h('div', { class: 'mode-scroll' }, [list]),
  ]);
}

// --------------------------------------------------------- document library
function renderDocsMode() {
  const documents = ctx.documents.list;
  const countEl = h('p', { class: 'mode-count', role: 'status', id: 'docs-count' }, '');
  const filterInput = h('input', {
    type: 'search',
    id: 'docs-text-filter',
    'aria-label': 'Filter documents by title or owner',
    placeholder: 'Filter by title or owner…',
  });
  const list = h('ul', { class: 'entity-list document-library', id: 'docs-mode-list' });

  function matchesText(doc, needle) {
    if (!needle) return true;
    const owners = (doc.owner_ids || []).map(nameOf);
    const haystack = [labelOf(doc), ...owners].join(' ').toLowerCase();
    return haystack.includes(needle);
  }

  function buildDocRow(doc) {
    const owners = (doc.owner_ids || []).map(nameOf);
    const year = yearOf(doc);
    const metaBits = [titleCase(doc.doc_type)];
    if (year) metaBits.push(String(year));
    const li = h('li', { class: 'document-row' }, [
      h('a', {
        href: (doc.reference && doc.reference.url) || '#', target: '_blank', rel: 'noopener', class: 'document-title',
      }, labelOf(doc)),
      h('span', { class: 'document-meta' }, ` — ${metaBits.join(', ')}`),
    ]);
    if (owners.length) {
      li.appendChild(h('div', { class: 'document-owners' }, `Owners: ${owners.join(', ')}`));
    }
    return li;
  }

  function apply() {
    const needle = filterInput.value.trim().toLowerCase();
    const filtered = documents.filter((d) => matchesText(d, needle));
    countEl.textContent = `Showing ${filtered.length} of ${documents.length} documents`;
    list.innerHTML = '';
    if (!filtered.length) {
      list.appendChild(h('li', { class: 'empty-note' }, (
        documents.length ? 'No documents match this filter.' : 'No documents available.'
      )));
      return;
    }
    // Group by document type, each group sorted newest first.
    const buckets = new Map();
    for (const doc of filtered) {
      const key = doc.doc_type || 'other';
      if (!buckets.has(key)) buckets.set(key, []);
      buckets.get(key).push(doc);
    }
    const keys = [...buckets.keys()].sort((a, b) => titleCase(a).localeCompare(titleCase(b)));
    for (const key of keys) {
      const group = buckets.get(key).slice().sort((a, b) => monthOf(b) - monthOf(a));
      list.appendChild(groupHeaderRow(titleCase(key), group.length));
      for (const doc of group) list.appendChild(buildDocRow(doc));
    }
  }

  filterInput.addEventListener('input', apply);
  apply();

  return h('div', { class: 'mode-body' }, [
    h('h2', {}, 'Document library'),
    countEl,
    h('div', { class: 'results-filters' }, [filterInput]),
    h('div', { class: 'mode-scroll' }, [list]),
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
