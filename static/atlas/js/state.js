// state.js — the single source of truth for "what is on screen": the hash
// route (#/facility/<slug> etc.), plus short query state (?y=, ?r=, ?t=, ?s=,
// ?m=, ?arcs=, a tour's ?step= and ?present=, and the Results list's own
// ?ry=/?rx=/?rf=/?rt=/?rk=/?rs=/?rb=).
// Back/forward and copy-pasted URLs both restore the view.

const TYPE_PREFIX = {
  facility: 'facility', experiment: 'experiment', collaboration: 'collaboration',
  institution: 'institution', topic: 'topic', result: 'result', document: 'document',
  site: 'site', detector: 'detector', accelerator: 'accelerator', beamline: 'beamline',
  // ---- local map view (docs/HEP_ATLAS_GEOMETRY.md §4) ----
  // `#/map/<facility-slug>` is a route like any other, so back/forward, the
  // search box and a pasted link all reach it through the same code path.
  map: 'map',
  // ---- views (js/views/registry.js) ----
  // `#/view/<name>/<arg>` (the beam section: `#/view/beam-section/lbnf~1`). The slug is
  // `<name>/<arg>`, so it keeps its own slash; the route is otherwise like any other.
  view: 'view',
  // ---- guided tours (js/tours.js) ----
  // `#/tour/<slug>` plays a tour; the step rides in `?step=<n>` (1-based) and
  // `?present=1` turns on presenter mode. `#/view/tour/<slug>` is accepted too and
  // is rewritten to this form by app.js. The step's own year, selection, map or
  // view are not in the address: the tour supplies them (docs A28, `href`).
  tour: 'tour',
};

// ---- Results list (modes.js) ------------------------------------------------
// The Results panel's year / experiment / facility / topic / type filters, its
// sort order and its grouping. They are part of the view, so they live in the
// URL while the panel is open: opening a result and pressing Back, or sending
// the link, brings back the same list. Only values that differ from the
// defaults are written, and only while `m=results` — leaving the panel must not
// strand them in the address of a view that cannot honour them.
const RESULTS_PARAMS = {
  year: 'ry', experiment: 'rx', facility: 'rf', topic: 'rt', type: 'rk', sort: 'rs', group: 'rb',
};
const RESULTS_SORTS = ['date', 'experiment', 'type'];
const RESULTS_GROUPS = ['none', 'year', 'experiment'];

export function defaultResultsView() {
  return { year: '', experiment: '', facility: '', topic: '', type: '', sort: 'date', group: 'none' };
}

function parseResultsView(params) {
  const view = defaultResultsView();
  for (const key of ['year', 'experiment', 'facility', 'topic', 'type']) {
    const value = params.get(RESULTS_PARAMS[key]);
    if (value) view[key] = value;
  }
  const sort = params.get(RESULTS_PARAMS.sort);
  if (RESULTS_SORTS.includes(sort)) view.sort = sort;
  const group = params.get(RESULTS_PARAMS.group);
  if (RESULTS_GROUPS.includes(group)) view.group = group;
  return view;
}

const subscribers = new Set();
let current = null;

function parseHashEntity(hash) {
  const clean = (hash || '').replace(/^#\/?/, '');
  if (!clean) return null;
  const [type, ...rest] = clean.split('/');
  const slug = rest.join('/');
  if (!TYPE_PREFIX[type] || !slug) return null;
  return { type, slug };
}

function parseSearch(search) {
  const params = new URLSearchParams(search);
  const state = {
    year: null, range: null, topic: null, status: null, mode: null, arcs: false, collab: null,
    era: null, facilityKind: null, experimentKind: null, region: null,
    // ---- local map view (§4): `lv` visible levels, `bm` basemap, `sel`
    // the entity (or context feature) in the drawer. `levels: null` means
    // "all levels", which is not the same as "no levels" (`[]`).
    levels: null, basemap: true, sel: null,
    // ---- guided tours: the 1-based step, and presenter mode ----
    step: null, present: false,
    results: parseResultsView(params),
  };
  if (params.has('y')) {
    const y = parseInt(params.get('y'), 10);
    if (!Number.isNaN(y)) state.year = y;
  }
  if (params.has('r')) {
    const m = /^(\d{3,4})-(\d{3,4})$/.exec(params.get('r'));
    if (m) state.range = [parseInt(m[1], 10), parseInt(m[2], 10)];
  }
  // Filter facets (docs/HEP_ATLAS_ARCHITECTURE.md "Filters and clustering"):
  // `t`/`s` predate the filter panel and are kept for URL compatibility;
  // both now carry comma-separated OR-lists rather than a single value.
  if (params.has('t')) state.topic = params.get('t');
  if (params.has('s')) state.status = params.get('s');
  if (params.has('er')) state.era = params.get('er');
  if (params.has('fk')) state.facilityKind = params.get('fk');
  if (params.has('ek')) state.experimentKind = params.get('ek');
  if (params.has('rg')) state.region = params.get('rg');
  if (params.has('m')) state.mode = params.get('m');
  if (params.has('c')) state.collab = params.get('c');
  state.arcs = params.get('arcs') === '1';
  // ---- local map view (§4) ----
  if (params.has('lv')) {
    const raw = params.get('lv');
    state.levels = raw === '' ? [] : raw.split(',').filter(Boolean);
  }
  if (params.get('bm') === '0') state.basemap = false;
  if (params.has('sel')) state.sel = params.get('sel');
  if (params.has('step')) {
    const step = parseInt(params.get('step'), 10);
    if (Number.isFinite(step) && step >= 1) state.step = step;
  }
  state.present = params.get('present') === '1';
  return state;
}

// A query written inside the hash (`#/tour/higgs-hunt?step=3`, the way a tour link is
// often typed or pasted) is read as if it stood before the `#`; a parameter in both
// places keeps the real query's value. The address is rewritten in the usual form the
// next time anything navigates.
function locationParts() {
  const { hash, search } = window.location;
  const at = hash.indexOf('?');
  if (at < 0) return { hash, search };
  const merged = new URLSearchParams(search);
  for (const [key, value] of new URLSearchParams(hash.slice(at + 1))) if (!merged.has(key)) merged.set(key, value);
  return { hash: hash.slice(0, at), search: `?${merged.toString()}` };
}

function readLocation() {
  const { hash, search } = locationParts();
  return {
    entity: parseHashEntity(hash),
    ...parseSearch(search),
    dataMode: new URLSearchParams(search).get('data'),
  };
}

function buildURL(state) {
  const params = new URLSearchParams();
  if (state.dataMode) params.set('data', state.dataMode);
  if (state.year != null) params.set('y', String(state.year));
  if (state.range) params.set('r', `${state.range[0]}-${state.range[1]}`);
  if (state.topic) params.set('t', state.topic);
  if (state.status) params.set('s', state.status);
  if (state.era) params.set('er', state.era);
  if (state.facilityKind) params.set('fk', state.facilityKind);
  if (state.experimentKind) params.set('ek', state.experimentKind);
  if (state.region) params.set('rg', state.region);
  if (state.mode) params.set('m', state.mode);
  if (state.collab) params.set('c', state.collab);
  if (state.arcs) params.set('arcs', '1');
  // ---- local map view (§4) ----
  // These three only mean anything on a map route, so they are written only
  // there: leaving a map must not leave `lv`/`bm`/`sel` stranded in the URL
  // of a globe view that cannot honour them.
  if (state.entity && state.entity.type === 'map') {
    if (state.levels) params.set('lv', state.levels.join(','));
    if (state.basemap === false) params.set('bm', '0');
    if (state.sel) params.set('sel', state.sel);
  }
  // The tour's step and presenter flag only mean something on a tour route, so they
  // are written only there (the same rule as `sel` above).
  // (`#/view/tour/<slug>` is the same route by another name until app.js rewrites it.)
  const onTour = state.entity && (state.entity.type === 'tour'
    || (state.entity.type === 'view' && String(state.entity.slug).startsWith('tour/')));
  if (onTour) {
    if (state.step != null) params.set('step', String(state.step));
    if (state.present) params.set('present', '1');
  }
  if (state.mode === 'results' && state.results) {
    const defaults = defaultResultsView();
    for (const [key, param] of Object.entries(RESULTS_PARAMS)) {
      if (state.results[key] && state.results[key] !== defaults[key]) params.set(param, state.results[key]);
    }
  }
  const search = params.toString();
  const hash = state.entity ? `#/${state.entity.type}/${state.entity.slug}` : '';
  return `${window.location.pathname}${search ? `?${search}` : ''}${hash}`;
}

function notify() {
  for (const fn of subscribers) fn(current);
}

/** Merge `patch` into the current state and push a new history entry. */
export function navigate(patch, { replace = false } = {}) {
  const previousMode = current ? current.mode : null;
  const previousEntity = current ? current.entity : null;
  current = { ...current, ...patch };
  // A tour's step and presenter flag belong to one tour: leaving it forgets both, and
  // opening another tour (from search, a topic, the Tours list) starts at its first step
  // unless the patch names one.
  if ('entity' in patch) {
    const into = patch.entity && patch.entity.type === 'tour';
    const same = into && previousEntity && previousEntity.type === 'tour' && previousEntity.slug === patch.entity.slug;
    if (!('step' in patch) && !same) current.step = null;
    if (!into && !('present' in patch)) current.present = false;
  }
  // The Results filters belong to one visit of the panel: opening it again from
  // the toolbar starts from the full list, as it always has. (Back/forward
  // restores them from the address instead, through readLocation().)
  if ('mode' in patch && (patch.mode || null) !== (previousMode || null) && !('results' in patch)) {
    current.results = defaultResultsView();
  }
  const url = buildURL(current);
  if (replace) {
    window.history.replaceState(current, '', url);
  } else {
    window.history.pushState(current, '', url);
  }
  notify();
}

export function get() {
  return current;
}

export function subscribe(fn) {
  subscribers.add(fn);
  return () => subscribers.delete(fn);
}

/** Wire popstate and read the initial URL. Call once at startup. */
export function init() {
  current = readLocation();
  window.addEventListener('popstate', () => {
    current = readLocation();
    notify();
  });
  return current;
}

/**
 * The state patch a deep link names, e.g. "#/experiment/dune" or "?fk=underground_laboratory":
 * only what the link says, so navigate(patch) opens that route or filter on top of the
 * current view. A link the Start-here card shows is a real href (middle-click, copy
 * link and a crawler all work); its click handler turns it into this patch.
 */
export function patchFromLink(href) {
  const url = new URL(href, window.location.href);
  const parsed = parseSearch(url.search);
  const params = new URLSearchParams(url.search);
  const patch = {};
  const entity = parseHashEntity(url.hash);
  if (entity) patch.entity = entity;
  const named = [['y', 'year'], ['t', 'topic'], ['s', 'status'], ['er', 'era'], ['fk', 'facilityKind'],
    ['ek', 'experimentKind'], ['rg', 'region'], ['m', 'mode']];
  for (const [param, key] of named) if (params.has(param)) patch[key] = parsed[key];
  return patch;
}

export function entityHash(type, slug) {
  return `#/${type}/${slug}`;
}

export function idToRoute(id) {
  const [type, slug] = id.split(/:(.+)/);
  if (!TYPE_PREFIX[type] || slug === undefined) return null;
  return { type, slug };
}

export function routeToId(route) {
  return `${route.type}:${route.slug}`;
}
