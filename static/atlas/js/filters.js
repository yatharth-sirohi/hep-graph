// filters.js — the atlas-wide filter panel: experiment status (derived at the
// selected year, A3), research topic (hierarchical), facility kind,
// experiment kind, geographic region, and the coarse active/completed/
// planned group. Filters compose with each other (AND across facets, OR
// within a facet) and with the timeline. The same predicate functions here
// are used by globe.js (marker/cluster visibility), fallback.js (the
// no-WebGL accessible tables) and app.js (option counts, URL state), so all
// three surfaces agree on exactly the same visible set.
//
// This module owns no globe/DOM rendering of markers — only the filter
// *panel* UI (checkboxes, chips, clear-all) and the pure matching logic.

import { statusForTimeline, statusEra, titleCase, kindLabel } from './model.js';

// ---------------------------------------------------------------- regions
// Not exhaustive of all ISO-3166 alpha-2 codes, but covers every country
// that appears anywhere in the atlas's facility/site/institution records.
// A code this table does not know about falls into the visible "Unknown"
// bucket rather than being silently dropped from every regional filter.
const REGION_BY_COUNTRY = {
  // Europe
  AD: 'Europe', AL: 'Europe', AT: 'Europe', AX: 'Europe', BA: 'Europe', BE: 'Europe',
  BG: 'Europe', BY: 'Europe', CH: 'Europe', CY: 'Europe', CZ: 'Europe', DE: 'Europe',
  DK: 'Europe', EE: 'Europe', ES: 'Europe', FI: 'Europe', FO: 'Europe', FR: 'Europe',
  GB: 'Europe', GG: 'Europe', GI: 'Europe', GR: 'Europe', HR: 'Europe', HU: 'Europe',
  IE: 'Europe', IM: 'Europe', IS: 'Europe', IT: 'Europe', JE: 'Europe', LI: 'Europe',
  LT: 'Europe', LU: 'Europe', LV: 'Europe', MC: 'Europe', MD: 'Europe', ME: 'Europe',
  MK: 'Europe', MT: 'Europe', NL: 'Europe', NO: 'Europe', PL: 'Europe', PT: 'Europe',
  RO: 'Europe', RS: 'Europe', RU: 'Europe', SE: 'Europe', SI: 'Europe', SJ: 'Europe',
  SK: 'Europe', SM: 'Europe', UA: 'Europe', VA: 'Europe', XK: 'Europe',
  // North America (incl. Central America and the Caribbean)
  US: 'North America', CA: 'North America', MX: 'North America', GT: 'North America',
  BZ: 'North America', SV: 'North America', HN: 'North America', NI: 'North America',
  CR: 'North America', PA: 'North America', CU: 'North America', JM: 'North America',
  HT: 'North America', DO: 'North America', BS: 'North America', BB: 'North America',
  TT: 'North America', AG: 'North America', DM: 'North America', GD: 'North America',
  KN: 'North America', LC: 'North America', VC: 'North America', BM: 'North America',
  GL: 'North America', PR: 'North America', VI: 'North America',
  // South America
  AR: 'South America', BO: 'South America', BR: 'South America', CL: 'South America',
  CO: 'South America', EC: 'South America', GY: 'South America', PY: 'South America',
  PE: 'South America', SR: 'South America', UY: 'South America', VE: 'South America',
  FK: 'South America', GF: 'South America',
  // Asia (incl. the Middle East and the Caucasus)
  CN: 'Asia', JP: 'Asia', KR: 'Asia', KP: 'Asia', IN: 'Asia', PK: 'Asia', BD: 'Asia',
  LK: 'Asia', NP: 'Asia', BT: 'Asia', MM: 'Asia', TH: 'Asia', VN: 'Asia', LA: 'Asia',
  KH: 'Asia', MY: 'Asia', SG: 'Asia', ID: 'Asia', PH: 'Asia', TW: 'Asia', HK: 'Asia',
  MO: 'Asia', MN: 'Asia', KZ: 'Asia', KG: 'Asia', TJ: 'Asia', TM: 'Asia', UZ: 'Asia',
  AF: 'Asia', IR: 'Asia', IQ: 'Asia', SY: 'Asia', LB: 'Asia', JO: 'Asia', IL: 'Asia',
  PS: 'Asia', SA: 'Asia', YE: 'Asia', OM: 'Asia', AE: 'Asia', QA: 'Asia', BH: 'Asia',
  KW: 'Asia', GE: 'Asia', AM: 'Asia', AZ: 'Asia', TR: 'Asia',
  // Africa
  EG: 'Africa', LY: 'Africa', TN: 'Africa', DZ: 'Africa', MA: 'Africa', SD: 'Africa',
  SS: 'Africa', ET: 'Africa', ER: 'Africa', DJ: 'Africa', SO: 'Africa', KE: 'Africa',
  UG: 'Africa', TZ: 'Africa', RW: 'Africa', BI: 'Africa', CD: 'Africa', CG: 'Africa',
  GA: 'Africa', GQ: 'Africa', CM: 'Africa', CF: 'Africa', TD: 'Africa', NG: 'Africa',
  NE: 'Africa', BJ: 'Africa', TG: 'Africa', GH: 'Africa', CI: 'Africa', LR: 'Africa',
  SL: 'Africa', GN: 'Africa', GW: 'Africa', SN: 'Africa', GM: 'Africa', ML: 'Africa',
  BF: 'Africa', MR: 'Africa', NA: 'Africa', BW: 'Africa', ZA: 'Africa', LS: 'Africa',
  SZ: 'Africa', ZW: 'Africa', ZM: 'Africa', MW: 'Africa', MZ: 'Africa', MG: 'Africa',
  KM: 'Africa', SC: 'Africa', MU: 'Africa', ST: 'Africa', AO: 'Africa', CV: 'Africa',
  EH: 'Africa',
  // Oceania
  AU: 'Oceania', NZ: 'Oceania', PG: 'Oceania', FJ: 'Oceania', SB: 'Oceania',
  VU: 'Oceania', NC: 'Oceania', PF: 'Oceania', WS: 'Oceania', TO: 'Oceania',
  KI: 'Oceania', TV: 'Oceania', NR: 'Oceania', FM: 'Oceania', MH: 'Oceania',
  PW: 'Oceania', GU: 'Oceania', AS: 'Oceania', MP: 'Oceania',
  // Antarctica
  AQ: 'Antarctica', TF: 'Antarctica',
};

export const REGION_LIST = [
  'Europe', 'North America', 'South America', 'Asia', 'Africa', 'Oceania', 'Antarctica', 'Unknown',
];

export function regionOfCountry(code) {
  if (!code) return 'Unknown';
  return REGION_BY_COUNTRY[String(code).toUpperCase()] || 'Unknown';
}

/** A record's country data may be `country` (string or list) and/or
 * `countries` (list, A9 — multi-country baselines/sites). Union both into
 * the set of regions the record touches. */
export function regionsOf(record) {
  if (!record) return [];
  const codes = []
    .concat(record.country || [])
    .concat(record.countries || []);
  return [...new Set(codes.map(regionOfCountry))];
}

// ---------------------------------------------------------- coarse eras
// The ontology's model.js already ranks a status into current/historical/
// future (statusEra); the filter UI and the spec's own wording use
// active/completed/planned instead, so this is purely a relabelling, not a
// different rule — the two must never disagree about which bucket a status
// falls into.
const ERA_LABEL = { current: 'active', historical: 'completed', future: 'planned' };
export const ERA_LIST = ['active', 'completed', 'planned'];

export function eraOfStatus(status) {
  return ERA_LABEL[statusEra(status)] || 'planned';
}

// -------------------------------------------------------------- topics
/** Map every topic id to itself plus every descendant id, so selecting a
 * parent topic ("Neutrino physics") also matches records tagged only with a
 * child ("Leptonic CP violation"). */
export function buildTopicIndex(topics) {
  const byParent = new Map();
  for (const topic of Object.values(topics || {})) {
    const list = byParent.get(topic.parent_id || null) || [];
    list.push(topic.id);
    byParent.set(topic.parent_id || null, list);
  }
  const descendants = new Map();
  function collect(id) {
    if (descendants.has(id)) return descendants.get(id);
    const set = new Set([id]);
    for (const childId of byParent.get(id) || []) {
      for (const d of collect(childId)) set.add(d);
    }
    descendants.set(id, set);
    return set;
  }
  for (const topic of Object.values(topics || {})) collect(topic.id);
  return {
    /** Every id that a selection of `topicId` should also match. */
    selfAndDescendants(topicId) {
      return descendants.get(topicId) || new Set([topicId]);
    },
  };
}

/** True if `topicIds` (a record's own topic_ids) intersects the expanded
 * set of any selected topic (including descendants). */
function matchesTopics(topicIds, selectedTopics, topicIndex) {
  if (!selectedTopics || !selectedTopics.length) return true;
  if (!topicIds || !topicIds.length) return false;
  const expanded = new Set();
  for (const sel of selectedTopics) {
    for (const id of topicIndex.selfAndDescendants(sel)) expanded.add(id);
  }
  return topicIds.some((id) => expanded.has(id));
}

// ----------------------------------------------------- site -> experiments
/** A site itself carries no `kind`/`topic_ids` of its own — those live on
 * the experiments that use it. Filtering sites by experiment kind or topic
 * means asking "does at least one experiment at this site match?" */
export function buildSiteExperimentIndex(atlas) {
  const bySite = new Map();
  for (const experiment of Object.values(atlas.experiments || {})) {
    for (const siteId of experiment.site_ids || []) {
      const list = bySite.get(siteId) || [];
      list.push(experiment);
      bySite.set(siteId, list);
    }
  }
  return bySite;
}

// --------------------------------------------------------------- state
export function emptyFilterState() {
  return {
    status: [], era: [], topic: [], facilityKind: [], experimentKind: [], region: [],
  };
}

function splitParam(value) {
  return value ? value.split(',').filter(Boolean) : [];
}

export function filtersFromState(state) {
  return {
    status: splitParam(state && state.status),
    era: splitParam(state && state.era),
    topic: splitParam(state && state.topic),
    facilityKind: splitParam(state && state.facilityKind),
    experimentKind: splitParam(state && state.experimentKind),
    region: splitParam(state && state.region),
  };
}

export function filtersToPatch(filters) {
  const join = (list) => (list && list.length ? list.join(',') : null);
  return {
    status: join(filters.status),
    era: join(filters.era),
    topic: join(filters.topic),
    facilityKind: join(filters.facilityKind),
    experimentKind: join(filters.experimentKind),
    region: join(filters.region),
  };
}

export function isEmptyFilterState(filters) {
  return ['status', 'era', 'topic', 'facilityKind', 'experimentKind', 'region']
    .every((key) => !filters[key] || filters[key].length === 0);
}

// ----------------------------------------------------------- predicates
function statusPasses(segments, filters, timelineState) {
  if ((!filters.status || !filters.status.length) && (!filters.era || !filters.era.length)) return true;
  const resolved = statusForTimeline(segments, timelineState);
  if (!resolved) return false; // filtered out: it does not exist at this year at all
  if (filters.status && filters.status.length && !filters.status.includes(resolved.status)) return false;
  if (filters.era && filters.era.length && !filters.era.includes(eraOfStatus(resolved.status))) return false;
  return true;
}

export function facilityMatches(facility, filters, timelineState) {
  if (filters.facilityKind && filters.facilityKind.length && !filters.facilityKind.includes(facility.kind)) return false;
  if (filters.region && filters.region.length) {
    const regions = regionsOf(facility);
    if (!regions.some((r) => filters.region.includes(r))) return false;
  }
  if (filters.topic && filters.topic.length) {
    // Handled by caller via topicIndex (needs the index); default true here.
  }
  return statusPasses(facility.state_segments, filters, timelineState);
}

export function facilityMatchesWithTopics(facility, filters, timelineState, topicIndex) {
  if (!facilityMatches(facility, filters, timelineState)) return false;
  return matchesTopics(facility.topic_ids, filters.topic, topicIndex);
}

export function experimentMatches(experiment, filters, timelineState, topicIndex) {
  if (filters.experimentKind && filters.experimentKind.length) {
    const kinds = [experiment.kind, ...(experiment.secondary_kinds || [])];
    if (!kinds.some((k) => filters.experimentKind.includes(k))) return false;
  }
  if (!matchesTopics(experiment.topic_ids, filters.topic, topicIndex)) return false;
  return statusPasses(experiment.state_segments, filters, timelineState);
}

/** A site is visible if its own region/status pass, AND — only when an
 * experiment-kind or topic filter is active — at least one experiment
 * hosted there matches that filter too. */
export function siteMatches(site, filters, timelineState, siteExperimentIndex, topicIndex) {
  if (filters.region && filters.region.length) {
    const regions = regionsOf(site);
    if (!regions.some((r) => filters.region.includes(r))) return false;
  }
  if (!statusPasses(site.state_segments, filters, timelineState)) return false;
  const needsExperimentCheck = (filters.experimentKind && filters.experimentKind.length)
    || (filters.topic && filters.topic.length);
  if (!needsExperimentCheck) return true;
  const experiments = siteExperimentIndex.get(site.id) || [];
  if (!experiments.length) return false;
  return experiments.some((exp) => experimentMatches(exp, filters, timelineState, topicIndex));
}

/** A collaboration's own record carries `state_segments` (status/era) and a
 * `host_facility_id` (region, via the host's country); topic/experiment-kind
 * match through its experiment(s), same as a site. */
export function collaborationMatches(collaboration, filters, timelineState, atlas, topicIndex) {
  if (filters.region && filters.region.length) {
    const host = atlas.facilities && atlas.facilities[collaboration.host_facility_id];
    const regions = host ? regionsOf(host) : [];
    if (!regions.some((r) => filters.region.includes(r))) return false;
  }
  if (!statusPasses(collaboration.state_segments, filters, timelineState)) return false;
  const needsExperimentCheck = (filters.experimentKind && filters.experimentKind.length)
    || (filters.topic && filters.topic.length);
  if (!needsExperimentCheck) return true;
  const experiments = (collaboration.experiment_ids || [])
    .map((id) => atlas.experiments && atlas.experiments[id]).filter(Boolean);
  if (!experiments.length) return false;
  return experiments.some((exp) => experimentMatches(exp, filters, timelineState, topicIndex));
}

/** Institution membership rows carry no lifecycle status of their own, so
 * status/era facets do not apply to them; region always does, and
 * experiment-kind/topic apply via the collaboration's own experiment(s)
 * when supplied. */
export function institutionMatches(member, filters, collaborationExperiments, topicIndex) {
  if (filters.region && filters.region.length) {
    const region = regionOfCountry(member.country);
    if (!filters.region.includes(region)) return false;
  }
  const needsExperimentCheck = (filters.experimentKind && filters.experimentKind.length)
    || (filters.topic && filters.topic.length);
  if (!needsExperimentCheck) return true;
  const experiments = collaborationExperiments || [];
  if (!experiments.length) return false;
  return experiments.some((exp) => (
    (!filters.experimentKind || !filters.experimentKind.length
      || [exp.kind, ...(exp.secondary_kinds || [])].some((k) => filters.experimentKind.includes(k)))
    && matchesTopics(exp.topic_ids, filters.topic, topicIndex)
  ));
}

// ------------------------------------------------------------ option counts
/** Independent per-option counts ("if only this one option were selected in
 * its own facet, how many facilities/experiments match, at the current
 * year?"). Deliberately not combined with the *other* currently-active
 * facets — that would need a combinatorial re-scan on every toggle — but it
 * does reflect the selected year/range (A3), per the spec's "counts per
 * option that reflect the current year". */
export function computeOptionCounts(atlas, timelineState) {
  const counts = {
    status: {}, era: {}, topic: {}, facilityKind: {}, experimentKind: {}, region: {},
  };
  const bump = (facet, key) => { counts[facet][key] = (counts[facet][key] || 0) + 1; };
  for (const f of Object.values(atlas.facilities || {})) {
    bump('facilityKind', f.kind);
    for (const r of regionsOf(f)) bump('region', r);
    const resolved = statusForTimeline(f.state_segments, timelineState);
    if (resolved) {
      bump('status', resolved.status);
      bump('era', eraOfStatus(resolved.status));
    }
  }
  for (const e of Object.values(atlas.experiments || {})) {
    for (const kind of [e.kind, ...(e.secondary_kinds || [])]) bump('experimentKind', kind);
    for (const t of e.topic_ids || []) bump('topic', t);
    const resolved = statusForTimeline(e.state_segments, timelineState);
    if (resolved) {
      bump('status', resolved.status);
      bump('era', eraOfStatus(resolved.status));
    }
  }
  return counts;
}

// -------------------------------------------------------------------- UI
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

// Plain names: the simple status first ("running, finished or planned"); the twelve
// lifecycle stages behind it are the "Detailed status".
const FACET_LABELS = {
  status: 'Detailed status', era: 'Running, finished or planned', topic: 'Physics topic',
  facilityKind: 'Kind of place', experimentKind: 'Kind of experiment', region: 'Region',
};

// The sidebar holds ~90 checkboxes. The two long groups start collapsed so the
// short ones (and the groups below them) are reachable without scrolling past
// 60 rows; a collapsed group still says how many of its options are active.
// The simple status and the regions are open; the rest are one click away, each
// heading saying how many choices it holds.
const COLLAPSED_BY_DEFAULT = new Set(['status', 'topic', 'facilityKind', 'experimentKind']);
const LONG_FACETS = new Set(['topic', 'experimentKind']);
const CLEAR_ALL_ID = 'filter-clear-all';

function optionLabel(facet, value) {
  // Kind slugs go through the explicit label map (model.js KIND_LABELS), not
  // titleCase(), which spells "cevns" as "Cevns" and "long_lived_particle" as
  // "Long Lived Particle".
  if (facet === 'facilityKind' || facet === 'experimentKind') return kindLabel(value);
  return facet === 'region' || facet === 'era' ? titleCase(value).replace(/^./, (c) => c.toUpperCase())
    : titleCase(value);
}

/**
 * Renders the filter controls into `container` and keeps them in sync with
 * `getFilters()`/`getCounts()`. `onChange(nextFilters)` fires whenever a
 * checkbox is toggled or a chip is cleared. Every control is a native
 * checkbox with an associated <label> (keyboard-operable, visibly focused by
 * the app's existing :focus-visible rule) plus a text count — never colour
 * alone.
 */
export function createFilterPanel(container, { atlas, topicIndex, onChange }) {
  let filters = emptyFilterState();
  let counts = {};

  const facilityKinds = [...new Set(Object.values(atlas.facilities || {}).map((f) => f.kind))].sort();
  const experimentKinds = [...new Set(Object.values(atlas.experiments || {})
    .flatMap((e) => [e.kind, ...(e.secondary_kinds || [])]))].sort();
  const statuses = [...new Set(Object.values(atlas.experiments || {})
    .flatMap((e) => (e.state_segments || []).map((seg) => seg[2])))].sort();
  const topics = Object.values(atlas.topics || {})
    .slice()
    .sort((a, b) => a.name.localeCompare(b.name));

  const clearRow = h('div', { class: 'filter-clear-row' });
  const chipsRow = h('div', { class: 'filter-chips', role: 'status', 'aria-live': 'polite' });
  const body = h('div', { class: 'filter-facets' });
  container.innerHTML = '';
  container.append(clearRow, chipsRow, body);

  // Every render rebuilds the groups, so whether each one is open lives here,
  // not in the DOM — otherwise ticking a box would snap a group back to its
  // default. Updated by the native `toggle` event (a click or the keyboard).
  const openState = new Map();
  const isOpenGroup = (facet) => (openState.has(facet) ? openState.get(facet) : !COLLAPSED_BY_DEFAULT.has(facet));

  // The outer "Filters" disclosure (index.html) can be collapsed too, so its
  // own summary carries the active count: a hidden filter never goes unnoticed.
  const outerSummary = container.closest('details')
    ? container.closest('details').querySelector(':scope > summary') : null;
  const outerLabel = outerSummary ? outerSummary.textContent.trim() : '';

  function countFor(facet, value) {
    return counts[facet] && counts[facet][value] != null ? counts[facet][value] : null;
  }

  function toggle(facet, value, checked) {
    const set = new Set(filters[facet]);
    if (checked) set.add(value); else set.delete(value);
    filters = { ...filters, [facet]: [...set] };
    onChange(filters);
  }

  function checkboxRow(facet, value, label) {
    const id = `filter-${facet}-${String(value).replace(/[^a-z0-9]+/gi, '-')}`;
    const input = h('input', {
      type: 'checkbox', id, checked: filters[facet].includes(value) ? '' : null,
      onchange: (e) => toggle(facet, value, e.target.checked),
    });
    const count = countFor(facet, value);
    return h('div', { class: 'filter-option' }, [
      input,
      h('label', { for: id }, `${label}${count != null ? ` (${count})` : ''}`),
    ]);
  }

  // A group's header: its name, plus "N selected" whenever any of its options
  // is active — the only cue a collapsed group has that it is filtering.
  function groupSummary(facet, size) {
    const selected = filters[facet].length;
    return h('summary', {}, [
      FACET_LABELS[facet],
      size ? h('span', { class: 'filter-group-size' }, ` ${size}`) : null,
      // The space is real text, so the accessible name reads "Research topic 3 selected".
      selected ? ' ' : null,
      selected ? h('span', { class: 'filter-group-count' }, `${selected} selected`) : null,
    ]);
  }

  function groupDetails(facet, rows) {
    const details = h('details', {
      class: 'filter-group', 'data-facet': facet, open: isOpenGroup(facet) ? '' : null,
    }, [
      groupSummary(facet, rows.length),
      h('div', { class: `filter-options${LONG_FACETS.has(facet) ? ' is-long' : ''}` }, rows),
    ]);
    details.addEventListener('toggle', () => openState.set(facet, details.open));
    return details;
  }

  function facetGroup(facet, options, labelFn) {
    return groupDetails(facet, options.map((value) => (
      checkboxRow(facet, value, labelFn ? labelFn(value) : optionLabel(facet, value)))));
  }

  function topicRows(list, depth) {
    return list.map((topic) => {
      const row = checkboxRow('topic', topic.id, topic.name);
      row.style.paddingLeft = `${depth * 12}px`;
      const children = topics.filter((t) => t.parent_id === topic.id);
      return children.length ? [row, ...topicRows(children, depth + 1)] : [row];
    }).flat();
  }

  function renderChips() {
    chipsRow.innerHTML = '';
    clearRow.innerHTML = '';
    const active = [];
    for (const facet of Object.keys(filters)) {
      for (const value of filters[facet]) active.push({ facet, value });
    }
    if (outerSummary) {
      outerSummary.textContent = active.length ? `${outerLabel} (${active.length} active)` : outerLabel;
    }
    if (!active.length) return;
    clearRow.appendChild(h('button', {
      type: 'button', id: CLEAR_ALL_ID, class: 'filter-clear-all',
      onclick: () => { filters = emptyFilterState(); onChange(filters); },
    }, 'Clear all filters'));
    for (const { facet, value } of active) {
      const label = facet === 'topic'
        ? (atlas.topics[value] && atlas.topics[value].name) || value
        : optionLabel(facet, value);
      chipsRow.appendChild(h('button', {
        type: 'button', class: 'filter-chip',
        'aria-label': `Remove filter: ${FACET_LABELS[facet]}: ${label}`,
        onclick: () => toggle(facet, value, false),
      }, `${label} ×`));
    }
  }

  function render() {
    // Re-rendering rebuilds every control, which would otherwise drop
    // keyboard focus after every single toggle. Facet/option checkbox ids
    // are stable across renders, so re-find and refocus the same one.
    const focusedId = document.activeElement && document.activeElement.id;
    // The `toggle` event is dispatched asynchronously, so a group closed just
    // before this render may not have reported it yet: read the DOM too.
    for (const group of body.querySelectorAll('.filter-group')) openState.set(group.dataset.facet, group.open);
    body.innerHTML = '';
    body.append(
      facetGroup('era', ERA_LIST),
      facetGroup('status', statuses),
      groupDetails('topic', topicRows(topics.filter((t) => !t.parent_id), 0)),
      facetGroup('facilityKind', facilityKinds),
      facetGroup('experimentKind', experimentKinds),
      facetGroup('region', REGION_LIST),
    );
    renderChips();
    if (focusedId) {
      const toRefocus = document.getElementById(focusedId);
      if (toRefocus) toRefocus.focus();
      else if (focusedId === CLEAR_ALL_ID) {
        // The button removes itself once nothing is active; keep the keyboard
        // user's place at the top of the filter list instead of on <body>.
        const first = body.querySelector('summary');
        if (first) first.focus();
      }
    }
  }

  render();

  return {
    getFilters() { return filters; },
    /** Set filters from outside (e.g. restoring from the URL) without
     * re-firing onChange — mirrors timeline.js's syncFromState contract. */
    setFilters(next) {
      filters = { ...emptyFilterState(), ...next };
      render();
    },
    setCounts(next) {
      counts = next || {};
      render();
    },
    /** Recompute per-option counts for the given timeline selection (A3) and
     * re-render. Called whenever the year/range changes. */
    updateForTimeline(timelineState) {
      counts = computeOptionCounts(atlas, timelineState);
      render();
    },
  };
}
