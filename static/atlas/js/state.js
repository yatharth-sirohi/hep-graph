// state.js — the single source of truth for "what is on screen": the hash
// route (#/facility/<slug> etc.), plus short query state (?y=, ?r=, ?t=, ?s=,
// ?m=, ?arcs=). Back/forward and copy-pasted URLs both restore the view.

const TYPE_PREFIX = {
  facility: 'facility', experiment: 'experiment', collaboration: 'collaboration',
  institution: 'institution', topic: 'topic', result: 'result', document: 'document',
};

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
  return state;
}

function readLocation() {
  return {
    entity: parseHashEntity(window.location.hash),
    ...parseSearch(window.location.search),
    dataMode: new URLSearchParams(window.location.search).get('data'),
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
  const search = params.toString();
  const hash = state.entity ? `#/${state.entity.type}/${state.entity.slug}` : '';
  return `${window.location.pathname}${search ? `?${search}` : ''}${hash}`;
}

function notify() {
  for (const fn of subscribers) fn(current);
}

/** Merge `patch` into the current state and push a new history entry. */
export function navigate(patch, { replace = false } = {}) {
  current = { ...current, ...patch };
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
