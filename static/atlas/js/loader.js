// loader.js — fetches HEP Atlas bundles lazily and normalizes the handful of
// shapes that differ between the shipped fixtures and the bundle contract in
// docs/HEP_ATLAS_BUNDLES.md (edges as [from,type,to] triples, results/documents
// wrapped in {order, results|documents}, sources split into {sources, cited_by}).
// `?data=fixtures` forces the fixtures/ tree. Otherwise generated/ is tried
// first. If generated/manifest.json is missing: on a dev host (localhost /
// 127.0.0.1) we fall back to fixtures/ with a visible notice, same as always;
// on any other host — a real deployment — falling back would silently show
// development fixture data in place of the real atlas, so resolveBase()
// instead reports an error and app.js shows the existing accessible error
// state (docs/atlas-worklog/REVIEW_performance.md P1-4) rather than a
// fixture banner. See `--browser-results`-driven test in browser_atlas.cjs
// ("A non-localhost host with no generated bundle...").

const cache = new Map();
let BASE = null;
let FALLBACK_NOTICE = null;
let LOAD_ERROR = null;

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
    // Not `no-store`: the server sends a strong ETag plus
    // `Cache-Control: public, max-age=0, must-revalidate` on every atlas
    // asset (see hepgraph/server.py's respond_atlas), so the default cache
    // mode already revalidates with the server on every request via
    // If-None-Match — manifest.json is never served stale, it just avoids
    // re-downloading identical bytes when nothing changed.
    const response = await fetch(`${base}manifest.json`);
    return response.ok;
  } catch (error) {
    return false;
  }
}

// A dev host is one where showing fixtures in place of missing real data is
// a convenience, not a misrepresentation: a developer running the server
// locally knows the generated tree may not exist yet. Anywhere else (a
// staging or production hostname), the same silent fallback would masquerade
// development data as the real atlas, so it is not offered there.
function isDevHost() {
  const host = window.location.hostname;
  return host === 'localhost' || host === '127.0.0.1' || host === '';
}

async function resolveBase() {
  const forced = paramsBase();
  if (forced) return { base: forced, notice: null, error: null };
  if (await probe(`${ROOT}generated/`)) return { base: `${ROOT}generated/`, notice: null, error: null };
  if (isDevHost()) {
    return {
      base: `${ROOT}fixtures/`,
      notice: 'generated/manifest.json is not available yet — showing development fixture data instead.',
      error: null,
    };
  }
  return {
    base: null,
    notice: null,
    error: 'The atlas data bundle is missing from this deployment.',
  };
}

async function fetchJSON(relativePath) {
  const key = `${BASE}${relativePath}`;
  if (cache.has(key)) return cache.get(key);
  // Default cache mode, not `no-store`: every bundle is served with a
  // strong ETag and `max-age=0, must-revalidate`, so the browser always
  // asks the server whether its cached copy is still good and only pays
  // for the bytes again when the content actually changed (a 304 otherwise).
  const promise = fetch(key).then((response) => {
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

/** Initialize the loader: pick the base path. Must run before any get*().
 *
 * When `error` is set, `base` is null and no get*() call should be made —
 * the caller must show the error state instead (see app.js's main()).
 */
export async function init() {
  const resolved = await resolveBase();
  BASE = resolved.base;
  FALLBACK_NOTICE = resolved.notice;
  LOAD_ERROR = resolved.error;
  return { base: BASE, notice: FALLBACK_NOTICE, error: LOAD_ERROR };
}

export function base() {
  return BASE;
}

export function fallbackNotice() {
  return FALLBACK_NOTICE;
}

export function loadError() {
  return LOAD_ERROR;
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

/** Returns { list: [record,...] (in canonical order), byId: Map }.
 *
 * The generated bundles are a flat map of id to record; the fixtures wrap the
 * same map under a named key alongside an explicit order. Reading only the
 * wrapped form left results and documents silently empty against real data.
 */
function orderedBundle(raw, key) {
  const table = raw[key]
    || Object.fromEntries(Object.entries(raw).filter(([id]) => id.includes(':')));
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

/** One local map's geometry bundle (`maps[id].bundle` in atlas.json, e.g.
 * `geometry/fermilab.json`). Panels read only its `entity_index` and each
 * feature's `representation` — to say truthfully how a map depicts an entity —
 * so this is the same cached request the map view itself makes later. */
export async function getGeometry(bundlePath) {
  return fetchJSON(bundlePath);
}

/** One exclusion plot's bundle (`limits/<plot>.json`, A29): its axes and every curve and
 * published minimum drawn on it. A plot the build did not write is an error with a message
 * a reader can act on, never an empty plot: a missing curve must not read as "no limits". */
export async function getLimits(plot) {
  const bundlePath = `limits/${plot}.json`;
  if (!(await isBundleListed(bundlePath))) {
    throw new Error(`the Atlas data has no exclusion plot called \u201c${plot}\u201d`);
  }
  return fetchJSON(bundlePath);
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

/** Returns `{ rows: [{entity_id, tier, researched}, ...] }`, one row per
 * experiment in the coverage registry (docs/HEP_ATLAS_COVERAGE.md).
 *
 * The generated bundle's `coverage.json` already carries exactly this: a
 * flat `rows` array scoped to the registry (one row per experiment,
 * `scripts/atlas_coverage_report.py`'s source of truth). The fixture bundle
 * predates that shape and instead carries an `entities` map keyed by id,
 * covering every entity type (facilities, sites, accelerators, ...) with
 * `tier`/`researched` attached to all of them, not just the registry —
 * this is a known fixture/generated drift (see the "Integration defects"
 * section of docs/HEP_ATLAS_VALIDATION.md). Filtering to `experiment:` keys
 * recovers the same registry rows from the fixture tree, so a page like
 * about.html that renders live coverage numbers reads one shape regardless
 * of which tree is loaded.
 */
export async function getCoverage() {
  const raw = await fetchJSON('coverage.json');
  if (Array.isArray(raw.rows)) return { rows: raw.rows };
  const entities = raw.entities || {};
  const rows = Object.entries(entities)
    .filter(([id]) => id.startsWith('experiment:'))
    .map(([entity_id, row]) => ({ entity_id, tier: row.tier, researched: row.researched }));
  return { rows };
}

/** Whether the build wrote the bundle at `relativePath`.
 *
 * manifest.json lists every bundle in the data tree, and 119 of the 122
 * collaborations have no membership roster, so asking the server for
 * `memberships/<slug>.json` unconditionally is a 404 (and a console error) for
 * almost every collaboration panel. The manifest is already loaded and cached;
 * a path it does not list does not exist. A manifest with no `bundles` table
 * cannot answer, and then the only honest move is to try the request.
 */
export async function isBundleListed(relativePath) {
  const manifest = await getManifest();
  const bundles = manifest && manifest.bundles;
  if (Array.isArray(bundles)) return bundles.includes(relativePath);
  if (bundles && typeof bundles === 'object') return Object.hasOwn(bundles, relativePath);
  return true;
}

/** The membership roster of a collaboration, or `null` when the build has none
 * for it (no roster curated yet). A listed roster that fails to load throws:
 * that is an error, not "no members". */
export async function getMembership(collaborationId) {
  const slug = collaborationId.split(':')[1];
  const bundlePath = `memberships/${slug}.json`;
  if (!(await isBundleListed(bundlePath))) return null;
  const roster = await fetchJSON(bundlePath);
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

/** relPath is the exact value of a membership row's `people_bundle` field.
 * `null` when the manifest does not list it (the row says people exist, the
 * build has not written their names). */
export async function getPeople(relPath) {
  if (!(await isBundleListed(relPath))) return null;
  return fetchJSON(relPath);
}

export async function getLandOutline() {
  const key = '/atlas/vendor/land-110m.json';
  if (cache.has(key)) return cache.get(key);
  const promise = fetch(key, { cache: 'force-cache' }).then((r) => r.json());
  cache.set(key, promise);
  return promise;
}
