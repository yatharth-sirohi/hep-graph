// loader.js — fetches HEP Atlas bundles lazily and normalizes the handful of
// shapes that differ between the shipped fixtures and the bundle contract in
// docs/HEP_ATLAS_BUNDLES.md (edges as [from,type,to] triples, results/documents
// wrapped in {order, results|documents}, sources split into {sources, cited_by}).
// `?data=fixtures` forces the fixtures/ tree; otherwise generated/ is tried
// first and we fall back to fixtures/ with a visible notice if generated/
// manifest.json is missing.

const cache = new Map();
let BASE = null;
let FALLBACK_NOTICE = null;

// Absolute (not page-relative) so this works whether the page was reached
// as /atlas or /atlas/ — the handler serves both, but relative URLs would
// resolve differently for each.
const ROOT = '/atlas/';

function paramsBase() {
  const params = new URLSearchParams(window.location.search);
  return params.get('data') === 'fixtures' ? `${ROOT}fixtures/` : null;
}

async function probe(base) {
  try {
    const response = await fetch(`${base}manifest.json`, { cache: 'no-store' });
    return response.ok;
  } catch (error) {
    return false;
  }
}

async function resolveBase() {
  const forced = paramsBase();
  if (forced) return { base: forced, notice: null };
  if (await probe(`${ROOT}generated/`)) return { base: `${ROOT}generated/`, notice: null };
  return {
    base: `${ROOT}fixtures/`,
    notice: 'generated/manifest.json is not available yet — showing development fixture data instead.',
  };
}

async function fetchJSON(relativePath) {
  const key = `${BASE}${relativePath}`;
  if (cache.has(key)) return cache.get(key);
  const promise = fetch(key, { cache: 'no-store' }).then((response) => {
    if (!response.ok) {
      throw new Error(`HEP Atlas: failed to load ${key} (${response.status})`);
    }
    return response.json();
  });
  cache.set(key, promise);
  try {
    return await promise;
  } catch (error) {
    cache.delete(key);
    throw error;
  }
}

/** Initialize the loader: pick the base path. Must run before any get*(). */
export async function init() {
  const resolved = await resolveBase();
  BASE = resolved.base;
  FALLBACK_NOTICE = resolved.notice;
  return { base: BASE, notice: FALLBACK_NOTICE };
}

export function base() {
  return BASE;
}

export function fallbackNotice() {
  return FALLBACK_NOTICE;
}

export async function getManifest() {
  return fetchJSON('manifest.json');
}

/** Lift a site's coordinates to the top level.
 *
 * The generated bundle keeps them in a `coordinates` object, as the canonical
 * data files do; the fixtures flatten them. The globe wants one shape, and a
 * site whose latitude reads as undefined silently becomes a NaN position that
 * draws no marker at all, so this normalisation is load-bearing.
 */
function flattenSiteCoordinates(atlas) {
  for (const site of Object.values(atlas.sites || {})) {
    const coordinates = site.coordinates;
    if (site.lat == null && coordinates && coordinates.lat != null) {
      site.lat = coordinates.lat;
      site.lon = coordinates.lon;
      site.coord_kind = site.coord_kind || coordinates.kind;
      site.precision_m = site.precision_m ?? coordinates.precision_m;
    }
  }
  return atlas;
}

export async function getAtlas() {
  return flattenSiteCoordinates(await fetchJSON('atlas.json'));
}

export async function getInstitutions() {
  const raw = await fetchJSON('institutions.json');
  return raw.institutions || raw;
}

export async function getText() {
  return fetchJSON('text.json');
}

export async function getProvenance() {
  return fetchJSON('provenance.json');
}

/** Returns { list: [record,...] (in canonical order), byId: Map }. */
function orderedBundle(raw, key) {
  const table = raw[key] || {};
  const order = Array.isArray(raw.order) ? raw.order : Object.keys(table).sort();
  const list = order.filter((id) => table[id]).map((id) => table[id]);
  const byId = new Map(list.map((record) => [record.id, record]));
  return { list, byId };
}

let resultsCache = null;
export async function getResults() {
  if (resultsCache) return resultsCache;
  const raw = await fetchJSON('results.json');
  resultsCache = orderedBundle(raw, 'results');
  return resultsCache;
}

let documentsCache = null;
export async function getDocuments() {
  if (documentsCache) return documentsCache;
  const raw = await fetchJSON('documents.json');
  documentsCache = orderedBundle(raw, 'documents');
  return documentsCache;
}

let sourcesCache = null;
export async function getSources() {
  if (sourcesCache) return sourcesCache;
  const raw = await fetchJSON('sources.json');
  const sources = raw.sources || raw;
  const citedBy = raw.cited_by || {};
  sourcesCache = { byId: sources, citedBy };
  return sourcesCache;
}

export async function getSearchEntries() {
  const raw = await fetchJSON('search.json');
  const entries = Array.isArray(raw) ? raw : (raw.entries || []);
  return entries.map(([type, id, name, aliases, subtitle]) => ({
    type, id, name, aliases: aliases || [], subtitle: subtitle || '',
  }));
}

let graphCache = null;
export async function getGraph() {
  if (graphCache) return graphCache;
  const raw = await fetchJSON('graph.json');
  graphCache = (raw.edges || []).map((edge) => (
    Array.isArray(edge)
      ? { from: edge[0], type: edge[1], to: edge[2] }
      : edge
  ));
  return graphCache;
}

export async function getCoverage() {
  return fetchJSON('coverage.json');
}

export async function getMembership(collaborationId) {
  const slug = collaborationId.split(':')[1];
  const roster = await fetchJSON(`memberships/${slug}.json`);
  // Same nested-versus-flat coordinate split as the site records: an
  // institution whose latitude reads as undefined silently draws no dot, so
  // collaboration mode would come up empty against the generated bundles.
  for (const member of roster.members || []) {
    const coordinates = member.coordinates;
    if (member.lat == null && coordinates && coordinates.lat != null) {
      member.lat = coordinates.lat;
      member.lon = coordinates.lon;
    }
  }
  return roster;
}

/** relPath is the exact value of a membership row's `people_bundle` field. */
export async function getPeople(relPath) {
  return fetchJSON(relPath);
}

export async function getLandOutline() {
  const key = '/atlas/vendor/land-110m.json';
  if (cache.has(key)) return cache.get(key);
  const promise = fetch(key, { cache: 'force-cache' }).then((r) => r.json());
  cache.set(key, promise);
  return promise;
}
