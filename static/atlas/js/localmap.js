// localmap.js — the 2D, to-scale local-map view (docs/HEP_ATLAS_GEOMETRY.md §4).
//
// Route `#/map/<facility-slug>`, plus `lv` (visible levels), `bm` (basemap),
// `sel` (the entity or feature in the drawer) and the existing `y`/`r`
// timeline state. Everything round-trips through the URL.
//
// Three things this module refuses to do, because the map's value is that
// what it shows is true:
//   * it never draws a shape the build did not emit — an entity with no
//     geometry appears in the "Unlocated / geometry not verified" list with
//     its sourced reason, never as an invented circle;
//   * a failed bundle fetch renders an error, never an empty map (an empty
//     campus reads as "nothing is here", which is a claim we cannot make);
//   * every feature carries its representation class and positional accuracy
//     in its tooltip and its list row, so a derived shape is never mistaken
//     for a surveyed one.
//
// Leaflet is vendored (static/atlas/vendor/leaflet/) and loaded lazily: the
// globe's cold load must not pay for a map engine nobody has opened yet.

import {
  titleCase, kindLabel, quantityText, statusForTimeline, timelineAbsenceReason, monthToYear,
} from './model.js';
import * as mapstyle from './mapstyle.js';
import { plainReason, researchNotes } from './unlocated.js';

const LEAFLET_JS = '/atlas/vendor/leaflet/leaflet.js';
const LEAFLET_CSS = '/atlas/vendor/leaflet/leaflet.css';
const TILE_URL = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
const TILE_ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors';
const EARTH_R = 6371008.8;

let ATLAS = null;
let INDEX = null;
let NAVIGATE = null;
let PANELS = null;
let dom = null;
let leafletPromise = null;
let bundleCache = new Map();
let opened = false;
let currentMapId = null;
let mapMeta = null;
let bundle = null;
let mapInstance = null;
let tileLayer = null;
let featureGroup = null;
let layersByFeature = new Map();
let labelLayer = null;
let symbolLayer = null;
let labelRecords = new Map();
let labelTexts = new Map();
let labelFrame = 0;
let forcedLabelId = null;
let view = { levels: null, basemap: true, sel: null, timelineState: { year: null } };
let polarProjection = false;
let framed = false;
// The view is "pristine" until the reader pans or zooms it. A pristine view is
// re-framed to what the map draws whenever that changes (a level toggle, the
// timeline, "show features from all years"); a view the reader has moved is
// never taken back from them except by the reset-view button.
let userMoved = false;
let framing = false;
let frameKey = null;
let showOutside = false;
let depthOpen = false;
let selOpener = null;
let lastAnnouncedSel = null;

// ---------------------------------------------------------------- helpers

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
    el.appendChild((typeof child === 'string' || typeof child === 'number')
      ? document.createTextNode(String(child)) : child);
  }
  return el;
}

function toRad(d) { return (d * Math.PI) / 180; }
function toDeg(r) { return (r * 180) / Math.PI; }

/** Great-circle metres between two [lat, lon] pairs (schema.great_circle_m). */
export function greatCircleM(a, b) {
  const p1 = toRad(a[0]);
  const p2 = toRad(b[0]);
  const dp = p2 - p1;
  const dl = toRad(b[1] - a[1]);
  const x = Math.sin(dp / 2) ** 2 + Math.cos(p1) * Math.cos(p2) * Math.sin(dl / 2) ** 2;
  return 2 * EARTH_R * Math.asin(Math.min(1, Math.sqrt(x)));
}

/** Initial great-circle bearing in degrees from [lat, lon] a to b. */
export function initialBearing(a, b) {
  const p1 = toRad(a[0]);
  const p2 = toRad(b[0]);
  const dl = toRad(b[1] - a[1]);
  const y = Math.sin(dl) * Math.cos(p2);
  const x = Math.cos(p1) * Math.sin(p2) - Math.sin(p1) * Math.cos(p2) * Math.cos(dl);
  return (toDeg(Math.atan2(y, x)) + 360) % 360;
}

function destination(lat, lon, bearingDeg, distM) {
  const p1 = toRad(lat);
  const l1 = toRad(lon);
  const th = toRad(bearingDeg);
  const d = distM / EARTH_R;
  const p2 = Math.asin(Math.sin(p1) * Math.cos(d) + Math.cos(p1) * Math.sin(d) * Math.cos(th));
  const l2 = l1 + Math.atan2(Math.sin(th) * Math.sin(d) * Math.cos(p1),
    Math.cos(d) - Math.sin(p1) * Math.sin(p2));
  return [toDeg(p2), ((toDeg(l2) + 540) % 360) - 180];
}

function compassPoint(bearing) {
  const names = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
    'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
  return names[Math.round(bearing / 22.5) % 16];
}

function formatDistance(metres) {
  if (metres >= 10000) return `${Math.round(metres / 1000)} km`;
  if (metres >= 1000) return `${(metres / 1000).toFixed(1)} km`;
  return `${Math.round(metres)} m`;
}

function idRoute(id) {
  const [type, slug] = id.split(/:(.+)/);
  return { type, slug };
}

function checkUnit(kind) {
  if (kind === 'area') return 'm²';
  if (kind === 'azimuth') return '°';
  return 'm';
}

// ------------------------------------------------------------ lazy Leaflet

function loadLeaflet() {
  if (leafletPromise) return leafletPromise;
  leafletPromise = new Promise((resolve, reject) => {
    if (!document.querySelector(`link[href="${LEAFLET_CSS}"]`)) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = LEAFLET_CSS;
      document.head.appendChild(link);
    }
    if (window.L) { resolve(window.L); return; }
    const script = document.createElement('script');
    script.src = LEAFLET_JS;
    script.onload = () => (window.L ? resolve(window.L) : reject(new Error('Leaflet loaded but window.L is missing')));
    script.onerror = () => reject(new Error(`Failed to load the map engine (${LEAFLET_JS})`));
    document.head.appendChild(script);
  });
  return leafletPromise;
}

async function fetchBundle(base, relPath) {
  const key = `${base}${relPath}`;
  if (bundleCache.has(key)) return bundleCache.get(key);
  const promise = fetch(key).then((response) => {
    if (!response.ok) throw new Error(`failed to load ${relPath} (${response.status})`);
    return response.json();
  });
  bundleCache.set(key, promise);
  try {
    return await promise;
  } catch (error) {
    bundleCache.delete(key);
    throw error;
  }
}

// ------------------------------------------------------------------- DOM

function ensureDom() {
  if (dom) return dom;
  const host = document.getElementById('atlas-main');
  const root = h('section', { class: 'map-view', id: 'map-view' });

  const layers = h('aside', {
    class: 'map-layers', id: 'map-layers', 'aria-label': 'Map layers, places and legend',
  });
  const stage = h('div', { class: 'map-stage' });
  const canvas = h('div', {
    class: 'map-canvas',
    id: 'map-canvas',
    role: 'application',
    'aria-label': 'To-scale local map. This is a pan-and-zoom map surface: with it focused, '
      + 'the arrow keys pan, plus and minus zoom. Everything drawn on it is also listed as '
      + 'buttons under “Features on this map” in the panel to its left, which is the '
      + 'keyboard and screen-reader equivalent.',
  });
  const north = h('div', { class: 'map-north' }, [
    h('span', { class: 'map-north-arrow', 'aria-hidden': 'true' }, '↑'),
    h('span', { class: 'map-north-label' }, 'N'),
  ]);
  const tileNotice = h('p', { class: 'map-tile-notice hidden', id: 'map-tile-notice', role: 'status' });
  const depth = h('div', {
    class: 'map-depth hidden', id: 'map-depth', role: 'region',
    'aria-label': 'Depth and level diagram (vertical section)',
  });
  stage.append(canvas, north, tileNotice, depth);

  const drawer = h('aside', {
    class: 'map-drawer', id: 'map-drawer', 'aria-label': 'Selected feature',
  });
  const drawerHead = h('div', { class: 'map-drawer-head' });
  const drawerPanel = h('div', { class: 'map-drawer-panel', id: 'map-drawer-panel' });
  const drawerFacts = h('div', { class: 'map-drawer-facts', id: 'map-drawer-facts' });
  drawer.append(drawerHead, drawerPanel, drawerFacts);

  root.append(layers, stage, drawer);
  host.appendChild(root);
  dom = { root, layers, stage, canvas, tileNotice, depth, drawer, drawerHead, drawerPanel, drawerFacts };
  return dom;
}

/** The element panels.render() should draw the selected entity's normal
 *  detail panel into while the map route is open. */
export function drawerPanelEl() {
  return ensureDom().drawerPanel;
}

export function isOpen() {
  return opened;
}

// ------------------------------------------------------------- data views

function levelById(id) {
  return (mapMeta.levels || []).find((lv) => lv.id === id) || null;
}

function visibleLevelIds() {
  if (view.levels === null) return (mapMeta.levels || []).map((lv) => lv.id);
  return view.levels;
}

function featureStatus(feature) {
  if (!feature.state_segments) return { status: null, timeless: true };
  const resolved = statusForTimeline(feature.state_segments, view.timelineState);
  return { status: resolved ? resolved.status : null, timeless: false, resolved };
}

/** A feature is in-year when it is timeless (a context shape with no entity
 *  and no `valid`) or its state_segments cover the selected year/range. */
function inSelectedYear(feature) {
  const s = featureStatus(feature);
  return s.timeless || !!s.status;
}

/**
 * The selected entity is a special case. Opening
 * `sel=accelerator:fermilab-tevatron` at 2026 used to show the Tevatron's
 * panel beside a map with no Tevatron on it, and nothing said why — the
 * reader is left to guess whether the ring is missing from the data or
 * missing from the year. So a selected entity whose features are hidden
 * *only* by the timeline is drawn anyway, ghosted, and the drawer says what
 * happened and offers the years in which it existed.
 *
 * This overrides the timeline filter and nothing else: a level the reader
 * switched off stays off, and unselected features are unaffected.
 */
function isSelectionGhost(feature) {
  if (!view.sel) return false;
  if (view.sel !== feature.entity_id && view.sel !== feature.id) return false;
  return !inSelectedYear(feature);
}

function featureVisible(feature) {
  if (!visibleLevelIds().includes(feature.level_id)) return false;
  if (inSelectedYear(feature)) return true;
  return showOutside || isSelectionGhost(feature);
}

/** When the selection is only on screen because of the rule above, this
 *  describes the gap: which years its features do cover, and why now is not
 *  one of them. Returns null when the selection is genuinely in-year, has no
 *  features on this map, or is hidden by a level toggle instead. */
function selectionTimelineGap() {
  if (!view.sel || showOutside) return null;
  const features = selectedFeatures().filter((f) => visibleLevelIds().includes(f.level_id));
  if (!features.length || features.some((f) => inSelectedYear(f))) return null;
  let first = Infinity;
  let last = -Infinity;
  const reasons = new Set();
  for (const feature of features) {
    const segments = feature.state_segments;
    if (!segments || !segments.length) continue;
    first = Math.min(first, segments[0][0]);
    last = Math.max(last, segments[segments.length - 1][1]);
    reasons.add(timelineAbsenceReason(segments, view.timelineState || {}));
  }
  if (!Number.isFinite(first)) return { features, reason: 'no_history', from: null, to: null };
  return {
    features,
    reason: reasons.has('ended') ? 'ended' : (reasons.has('not_yet') ? 'not_yet' : 'gap'),
    from: monthToYear(first),
    to: monthToYear(last),
  };
}

function selectedFeatures() {
  if (!view.sel || !bundle) return [];
  const byEntity = (bundle.entity_index || {})[view.sel] || [];
  if (byEntity.length) return bundle.features.filter((f) => byEntity.includes(f.id));
  return bundle.features.filter((f) => f.id === view.sel);
}

function whenLabel() {
  const t = view.timelineState || {};
  if (t.range) return `${t.range[0]}–${t.range[1]}`;
  return String(t.year != null ? t.year : '');
}

// --------------------------------------------------------------- the map

function destroyMap() {
  if (mapInstance) {
    mapInstance.remove();
    mapInstance = null;
  }
  polarProjection = false;
  framed = false;
  userMoved = false;
  framing = false;
  frameKey = null;
  if (labelFrame) window.cancelAnimationFrame(labelFrame);
  labelFrame = 0;
  forcedLabelId = null;
  if (window.__hepAtlasLocalMap) delete window.__hepAtlasLocalMap;
  tileLayer = null;
  featureGroup = null;
  labelLayer = null;
  symbolLayer = null;
  labelRecords = new Map();
  layersByFeature = new Map();
}

// Web Mercator cannot draw a pole: Leaflet's EPSG3857 clamps latitude to
// ±85.0511, so a map centred at −89.998° would be framed 550 km away from
// the thing it depicts, and projecting the view corners produces NaN. Any
// map whose centre is inside either polar cap therefore gets a local
// azimuthal-equidistant projection in metres instead, with the 0° meridian
// as *grid* north (the convention used at Amundsen–Scott, and the axis
// convention of EPSG:3031 for the southern cap).
const POLAR_LAT = 85;

export function isPolar(centre) {
  return Math.abs(centre.lat) > POLAR_LAT;
}

function polarCRS(L, centre) {
  const south = centre.lat < 0;
  const projection = {
    // Distance from the pole is the true great-circle distance, so a metre
    // on this map is a metre on the ground in every direction from the
    // pole — which is the whole point of an equidistant projection here.
    project(latLng) {
      const colatitude = toRad(south ? 90 + latLng.lat : 90 - latLng.lat);
      const rho = colatitude * EARTH_R;
      const lambda = toRad(latLng.lng);
      return new L.Point(rho * Math.sin(lambda),
        (south ? 1 : -1) * rho * Math.cos(lambda));
    },
    unproject(point) {
      const rho = Math.sqrt(point.x * point.x + point.y * point.y);
      const colatitude = toDeg(rho / EARTH_R);
      const lambda = Math.atan2(point.x, (south ? 1 : -1) * point.y);
      return new L.LatLng(south ? colatitude - 90 : 90 - colatitude, toDeg(lambda));
    },
    bounds: L.bounds([-Math.PI * EARTH_R, -Math.PI * EARTH_R],
      [Math.PI * EARTH_R, Math.PI * EARTH_R]),
  };
  return L.extend({}, L.CRS, {
    code: south ? 'HEP:SouthPolarAzimuthalEquidistant' : 'HEP:NorthPolarAzimuthalEquidistant',
    projection,
    // One projected unit is one metre, and scale(0) = 1 px per metre, so
    // zoom is a plain power of two on a metre grid (negative zooms are
    // normal here — see minZoom below).
    transformation: new L.Transformation(1, 0, -1, 0),
    scale: (zoom) => 2 ** zoom,
    zoom: (scale) => Math.log(scale) / Math.LN2,
    infinite: true,
    wrapLng: undefined,
    wrapLat: undefined,
    // The scale bar and every measurement must read true ground metres, the
    // same great-circle metres the geometry bundle's `measured` values use.
    distance: (a, b) => greatCircleM([a.lat, a.lng], [b.lat, b.lng]),
  });
}

/** The zoom at which the view's shorter side spans `2 × halfSpanM` metres,
 *  for whichever CRS is in use. */
function zoomForHalfSpan(halfSpanM, latitude) {
  const size = mapInstance.getSize();
  const shorter = Math.min(size.x, size.y);
  if (!shorter) return null;
  const metresPerPixel = (2 * halfSpanM) / shorter;
  if (polarProjection) return -Math.log2(metresPerPixel);
  // Web Mercator: 156543.03392 m/px at zoom 0 on the equator, scaled by
  // cos(latitude) — evaluated at the latitude the view is centred on.
  const atEquator = 156543.033928 * Math.cos(toRad(latitude));
  return Math.log2(atEquator / metresPerPixel);
}

/**
 * The fallback frame: the map record's own `center` and `extent_m`. Used when
 * nothing is drawn (a year or level selection that hides every feature), so
 * the empty map is still pointed at the facility rather than at the world.
 */
function frameToExtent() {
  const zoom = zoomForHalfSpan(mapMeta.extent_m || 3000, mapMeta.center.lat);
  if (zoom == null) return false;
  mapInstance.setView([mapMeta.center.lat, mapMeta.center.lon], zoom, { animate: false });
  return true;
}

/** Features that decide the frame. An inferred direction is a bearing, not a
 *  structure: T2K's runs 295 km to Kamioka and CNGS's 731 km to Gran Sasso, and
 *  fitting it would shrink the campus to nothing to make room for a line that
 *  is clipped at the map edge anyway. It is left out of the frame unless it is
 *  all that is drawn, in which case the record's own extent frames the view. */
function framingFeatures() {
  const drawn = bundle.features
    .filter(featureVisible)
    .filter((f) => f.representation !== 'inferred_direction' && f.feature_type !== 'direction_line');
  // A campus boundary is context: Fermilab's is 7 km across and framing it left
  // the rings a small knot in the middle. Frame the structures when there are any.
  const structures = drawn.filter((f) => f.feature_type !== 'boundary');
  return structures.length ? structures : drawn;
}

/**
 * Frame the view to the bounds of the features drawn for the current level and
 * year selection, with padding. Works in projected pixels at a reference zoom
 * rather than through L.latLngBounds, so it is the same arithmetic in Web
 * Mercator and in the polar metre grid (where a lat/lng box around the pole
 * spans every longitude). A Point is framed as the circle it is drawn as, its
 * positional accuracy, and the zoom is capped so a single small feature is
 * never blown up past what its accuracy supports.
 */
function frameToFeatures() {
  const L = window.L;
  const size = mapInstance.getSize();
  if (!size.x || !size.y) return false;
  const features = framingFeatures();
  if (!features.length) return false;
  const crs = mapInstance.options.crs;
  const z0 = 0;
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  let maxAccuracy = 0;
  const add = (lon, lat) => {
    const p = crs.latLngToPoint(L.latLng(lat, lon), z0);
    if (!Number.isFinite(p.x) || !Number.isFinite(p.y)) return;
    minX = Math.min(minX, p.x);
    maxX = Math.max(maxX, p.x);
    minY = Math.min(minY, p.y);
    maxY = Math.max(maxY, p.y);
  };
  for (const feature of features) {
    for (const part of lineParts(feature.geometry)) part.forEach(([lon, lat]) => add(lon, lat));
    for (const [lon, lat] of pointParts(feature.geometry)) {
      const radius = pointRadius(feature);
      for (const bearing of [0, 90, 180, 270]) {
        const [plat, plon] = destination(lat, lon, bearing, radius);
        add(plon, plat);
      }
    }
    if (feature.accuracy_m) maxAccuracy = Math.max(maxAccuracy, feature.accuracy_m);
  }
  if (!Number.isFinite(minX)) return false;
  const pad = Math.min(FRAME_PADDING_PX, Math.floor(Math.min(size.x, size.y) / 6));
  const availW = Math.max(40, size.x - 2 * pad);
  const availH = Math.max(40, size.y - 2 * pad);
  const widthPx = Math.max(maxX - minX, 1e-9);
  const heightPx = Math.max(maxY - minY, 1e-9);
  const centre = crs.pointToLatLng(L.point((minX + maxX) / 2, (minY + maxY) / 2), z0);
  let zoom = z0 + Math.log2(Math.min(availW / widthPx, availH / heightPx));
  const halfSpan = Math.max((mapMeta.extent_m || 3000) / FRAME_MIN_SPAN_DIVISOR,
    FRAME_ACCURACY_MULTIPLE * maxAccuracy, FRAME_MIN_HALF_SPAN_M);
  const cap = zoomForHalfSpan(halfSpan, centre.lat);
  if (cap != null) zoom = Math.min(zoom, cap);
  zoom = Math.max(mapInstance.getMinZoom(), Math.min(zoom, mapInstance.getMaxZoom()));
  if (!Number.isFinite(zoom)) return false;
  mapInstance.setView(centre, zoom, { animate: false });
  return true;
}

const FRAME_PADDING_PX = 56;
// A frame is never tighter than a sixth of the record's own extent, twice the
// largest positional accuracy it contains, or 150 m, whichever is widest: a
// lone Point or one small building is shown with the ground around it, not
// blown up to a scale its accuracy cannot support.
const FRAME_MIN_SPAN_DIVISOR = 6;
const FRAME_ACCURACY_MULTIPLE = 2;
const FRAME_MIN_HALF_SPAN_M = 150;

/** The drawn selection and the stage size: when either changes, a view the
 *  reader has not touched is framed again. */
function frameSignature() {
  const size = mapInstance.getSize();
  return `${framingFeatures().map((f) => f.id).join('|')}#${size.x}x${size.y}`;
}

/**
 * Frame the map to what it draws. `force` is the reset-view button; otherwise a
 * view the reader has already moved is left alone, and so is one that is
 * already framed to this same selection and stage size.
 */
function refreshFrame({ force = false } = {}) {
  if (!mapInstance) return false;
  const size = mapInstance.getSize();
  if (!size.x || !size.y) {
    framed = false;
    return false;
  }
  const key = frameSignature();
  if (!force && framed && (userMoved || key === frameKey)) return framed;
  framing = true;
  try {
    framed = frameToFeatures() || frameToExtent();
  } finally {
    framing = false;
  }
  frameKey = key;
  userMoved = false;
  return framed;
}

function createMap(L) {
  const { lat, lon } = mapMeta.center;
  polarProjection = isPolar(mapMeta.center);
  const options = {
    center: [lat, lon],
    zoom: 14,
    zoomControl: true,
    keyboard: true,
    attributionControl: true,
    preferCanvas: false,
    // Fractional zoom, so the opening view is exactly the extent the record
    // declares rather than the nearest whole power of two.
    zoomSnap: 0,
    zoomDelta: 0.5,
  };
  if (polarProjection) {
    options.crs = polarCRS(L, mapMeta.center);
    // A metre grid needs negative zooms: at zoom 0 one pixel is one metre,
    // so a 6 km-wide view of the pole sits near zoom −3.
    options.minZoom = -24;
    options.maxZoom = 14;
    options.zoom = 0;
  }
  mapInstance = L.map(dom.canvas, options);
  L.control.scale({ imperial: false, metric: true, position: 'bottomleft' }).addTo(mapInstance);
  resetViewControl(L).addTo(mapInstance);
  featureGroup = L.layerGroup().addTo(mapInstance);
  symbolLayer = L.layerGroup().addTo(mapInstance);
  labelLayer = L.layerGroup().addTo(mapInstance);
  // Anything that moves the view that this module did not do itself means the
  // reader has taken the camera (see refreshFrame).
  mapInstance.on('movestart zoomstart', () => { if (!framing) userMoved = true; });
  // Labels are laid out against the view, so they are re-laid out when it
  // changes; during a zoom animation they are hidden rather than left
  // sliding over the wrong shapes.
  mapInstance.on('zoomstart', () => mapInstance.getContainer().classList.add('map-labels-busy'));
  mapInstance.on('moveend resize', scheduleLabelLayout);
  // A stage that changes size (the drawer opening, a rotated phone) frames a
  // view the reader has not touched again.
  mapInstance.on('resize', () => { if (!framing) refreshFrame(); });
  // The container was display:none until the route's layout class landed on
  // #atlas-main, so it can still measure 0 × 0 here; framing then collapses
  // to zoom 0 (the whole world). Try now, and again from show() once the
  // browser has laid the stage out.
  refreshFrame();
  // A test/debug handle: the browser suite reads the scale control's label
  // and pixel width and checks it against map.distance() at the view centre.
  window.__hepAtlasLocalMap = mapInstance;
}

function applyBasemap(L) {
  if (polarProjection) {
    // OpenStreetMap ships no tiles in this projection — and Web Mercator
    // raster tiles do not exist for the pole at all — so the basemap is not
    // merely off here, it is unavailable, and the notice says which.
    dom.tileNotice.textContent = 'No basemap at the pole: the OpenStreetMap tile set is Web '
      + 'Mercator, which cannot represent latitude 90°. This map uses a local azimuthal '
      + 'projection in metres, so the atlas’s own to-scale features are drawn on a plain '
      + 'background. The scale bar and the grid-north indicator are unaffected.';
    dom.tileNotice.classList.remove('hidden');
    mapInstance.getContainer().classList.add('basemap-off');
    return;
  }
  if (view.basemap) {
    if (!tileLayer) {
      tileLayer = L.tileLayer(TILE_URL, {
        maxZoom: 19, attribution: TILE_ATTRIBUTION, crossOrigin: true,
      });
      let failures = 0;
      tileLayer.on('tileerror', () => {
        failures += 1;
        if (failures < 3) return;
        dom.tileNotice.textContent = 'The OpenStreetMap basemap is unavailable, so only the '
          + 'atlas’s own to-scale features are drawn, on a plain background. The shapes, '
          + 'the scale bar and the north indicator are unaffected.';
        dom.tileNotice.classList.remove('hidden');
      });
      tileLayer.on('load', () => {
        dom.tileNotice.classList.add('hidden');
        dom.tileNotice.textContent = '';
      });
    }
    if (!mapInstance.hasLayer(tileLayer)) tileLayer.addTo(mapInstance);
    mapInstance.getContainer().classList.remove('basemap-off');
  } else {
    if (tileLayer && mapInstance.hasLayer(tileLayer)) mapInstance.removeLayer(tileLayer);
    dom.tileNotice.classList.add('hidden');
    mapInstance.getContainer().classList.add('basemap-off');
  }
}

function tooltipFor(feature) {
  const t = mapstyle.typeStyle(feature.feature_type);
  const level = levelById(feature.level_id);
  const s = featureStatus(feature);
  const statusText = s.timeless
    ? 'drawn in every year (context feature)'
    : (s.status ? mapstyle.statusStyle(s.status).label : `not present in ${whenLabel()}`);
  const lines = [
    feature.entity_name || feature.name,
    `${t.label} · ${level ? level.name : feature.level_id}`,
    `${statusText} · ${mapstyle.accuracyText(feature)}`,
  ];
  if (feature.feature_type === 'direction_line' || feature.representation === 'inferred_direction') {
    lines.push('inferred direction — not a structure');
  }
  const clipped = clippedGeometry(feature);
  if (clipped) {
    lines.push(clipped.fullLength_m
      ? `drawn cut off at the edge of this map — the full bearing runs ${formatDistance(clipped.fullLength_m)}`
      : 'drawn cut off at the edge of this map');
  }
  if (feature.geometry.type === 'Point' || feature.geometry.type === 'MultiPoint') {
    lines.push(feature.accuracy_m != null
      ? `position only — the circle is its ±${feature.accuracy_m} m accuracy, not a footprint`
      : 'position only — no footprint is sourced for this feature');
  }
  return lines.join('\n');
}

function arrowheadCoords(coords) {
  const p1 = coords[coords.length - 1];
  const p0 = coords[coords.length - 2];
  if (!p0 || !p1) return null;
  const tip = [p1[1], p1[0]];
  const back = initialBearing(tip, [p0[1], p0[0]]);
  const len = Math.max(20, greatCircleM([p0[1], p0[0]], tip) * 0.12);
  const a = destination(tip[0], tip[1], (back - 22 + 360) % 360, len);
  const b = destination(tip[0], tip[1], (back + 22) % 360, len);
  return [a, tip, b];
}

/**
 * §4 draws an inferred direction "clipped to the map extent". Some records
 * carry the full baseline instead — T2K's line runs 295 km to Kamioka,
 * CNGS's 731 km to Gran Sasso — so the arrowhead would be computed hundreds
 * of kilometres off screen and its legs would streak across the view. This
 * trims the line where it leaves a generous multiple of the map's own
 * extent, which is also where the reader stops being able to see it.
 *
 * It changes nothing about the claim: the bearing is the bearing, the facts
 * panel still gives the method and the full length, and the drawer says the
 * line is cut off rather than pretending it ends here.
 */
const DIRECTION_CLIP_FACTOR = 1.4;

function clipToExtent(coords) {
  const limit = DIRECTION_CLIP_FACTOR * (mapMeta.extent_m || 3000);
  const centre = [mapMeta.center.lat, mapMeta.center.lon];
  const inside = (pt) => greatCircleM(centre, [pt[1], pt[0]]) <= limit;
  // Bisect the crossing segment: 24 halvings puts the cut well under a metre
  // at any campus scale, with no projection maths. `from` is the end inside.
  const boundary = (from, to) => {
    let lo = 0;
    let hi = 1;
    for (let k = 0; k < 24; k += 1) {
      const mid = (lo + hi) / 2;
      const at = [from[0] + (to[0] - from[0]) * mid, from[1] + (to[1] - from[1]) * mid];
      if (inside(at)) lo = mid; else hi = mid;
    }
    return [from[0] + (to[0] - from[0]) * lo, from[1] + (to[1] - from[1]) * lo];
  };
  // A direction line may start at the far site and end on this campus
  // (T2K's runs J-PARC -> Kamioka), so both ends have to be considered.
  // A line that leaves and re-enters would need multi-part output; no
  // direction line does, since it is a single great-circle segment.
  const out = [];
  let clipped = false;
  for (let i = 0; i < coords.length; i += 1) {
    const cur = coords[i];
    const curIn = inside(cur);
    if (i > 0) {
      const prev = coords[i - 1];
      const prevIn = inside(prev);
      if (prevIn !== curIn) {
        out.push(prevIn ? boundary(prev, cur) : boundary(cur, prev));
        clipped = true;
      }
    }
    if (curIn) out.push(cur); else clipped = true;
  }
  // Nothing of it reaches this map: draw the record's own shape rather than
  // silently dropping a feature the list still names.
  if (out.length < 2) return { coords, clipped: false };
  return { coords: out, clipped };
}

/** True when this feature's shape runs beyond the map's own extent and is
 *  drawn cut off. Only inferred directions are trimmed. */
function clippedGeometry(feature) {
  if (feature.representation !== 'inferred_direction') return null;
  const line = lineCoords(feature.geometry);
  if (!line || line.length < 2) return null;
  const result = clipToExtent(line);
  if (!result.clipped) return null;
  return {
    geometry: { type: 'LineString', coordinates: result.coords },
    fullLength_m: feature.measured && feature.measured.length_m,
  };
}

function lineCoords(geometry) {
  if (geometry.type === 'LineString') return geometry.coordinates;
  if (geometry.type === 'MultiLineString') return geometry.coordinates[geometry.coordinates.length - 1];
  return null;
}

/** The radius a Point is drawn with: its positional accuracy, or 25 m when
 *  the record gives none. */
function pointRadius(feature) {
  return feature.accuracy_m != null && feature.accuracy_m > 0 ? feature.accuracy_m : 25;
}

/** [lon, lat] vertex arrays of a line or of a polygon's outer ring(s). */
function lineParts(geometry) {
  switch (geometry.type) {
    case 'LineString': return [geometry.coordinates];
    case 'MultiLineString': return geometry.coordinates;
    case 'Polygon': return geometry.coordinates.slice(0, 1);
    case 'MultiPolygon': return geometry.coordinates.map((polygon) => polygon[0]);
    default: return [];
  }
}

/** [lon, lat] positions of a Point or MultiPoint. */
function pointParts(geometry) {
  if (geometry.type === 'Point') return [geometry.coordinates];
  if (geometry.type === 'MultiPoint') return geometry.coordinates;
  return [];
}

/** Leaflet's default for a GeoJSON Point is a pin marker, which is exactly
 *  what §4 rules out: a pin asserts a position and says nothing about what
 *  is known. A quarter of the real features are Points — a cavern, an
 *  instrument, an array whose footprint no source gives — and what *is*
 *  known about each is a position plus a positional accuracy. So each is
 *  drawn to scale as a circle of radius `accuracy_m` (the uncertainty
 *  itself, as a real ground distance) with a small screen-sized centre
 *  mark so it stays findable when zoomed out. Both are SVG paths, both
 *  carry the same four encodings as every other feature. */
function pointLayers(L, feature, options) {
  const radius = pointRadius(feature);
  return {
    pointToLayer: (_geoJsonPoint, latlng) => L.circle(latlng, {
      ...options, radius, fill: true, fillColor: options.color, fillOpacity: options.fillOpacity || 0.12,
    }),
  };
}

function drawFeatures(L) {
  featureGroup.clearLayers();
  layersByFeature = new Map();
  // Leaflet fades a removed tooltip out over 200 ms before dropping its node;
  // drop the old labels now so the DOM never holds two sets of names.
  const stale = [];
  labelLayer.eachLayer((tooltip) => stale.push(tooltip.getElement()));
  labelLayer.clearLayers();
  symbolLayer.clearLayers();
  stale.forEach((el) => { if (el) el.remove(); });
  labelRecords = new Map();
  const seriesOfFeature = collapseSeries(bundle.features.filter(featureVisible));
  for (const feature of bundle.features) {
    if (!featureVisible(feature)) continue;
    const level = levelById(feature.level_id);
    const s = featureStatus(feature);
    const ghost = !s.timeless && !s.status;
    const options = mapstyle.pathOptions(feature, { level, status: s.status, ghost });
    const isPoint = feature.geometry.type === 'Point' || feature.geometry.type === 'MultiPoint';
    const clip = clippedGeometry(feature);
    const shape = clip ? clip.geometry : feature.geometry;
    const parts = [];
    if (mapstyle.levelIsSubsurface(level) && !isPoint) {
      parts.push(L.geoJSON(shape, { style: () => mapstyle.casingOptions(feature, { ghost }) }));
    }
    const main = L.geoJSON(shape, {
      style: () => options,
      ...(isPoint ? pointLayers(L, feature, options) : {}),
    });
    parts.push(main);
    if (isPoint) {
      parts.push(L.geoJSON(feature.geometry, {
        pointToLayer: (_p, latlng) => L.circleMarker(latlng, {
          ...options, radius: 4, fill: true, fillColor: options.color, fillOpacity: 0.9,
          dashArray: null, weight: 1.5,
        }),
      }));
    }
    const t = mapstyle.typeStyle(feature.feature_type);
    const coords = t.arrow ? lineCoords(shape) : null;
    if (coords && coords.length >= 2) {
      const head = arrowheadCoords(coords);
      if (head) parts.push(L.polyline(head, { ...options, fill: false, fillOpacity: 0, dashArray: null }));
    }
    const group = L.featureGroup(parts);
    const tooltip = tooltipFor(feature);
    group.bindTooltip(tooltip, { sticky: true, className: 'map-tooltip' });
    group.on('click', () => selectFrom(feature, null));
    group.addTo(featureGroup);
    const el = main.getLayers()[0] && main.getLayers()[0].getElement && main.getLayers()[0].getElement();
    if (el) {
      el.setAttribute('data-geometry-id', feature.id);
      el.setAttribute('data-representation', feature.representation);
      if (ghost) el.classList.add('is-ghosted');
    }
    layersByFeature.set(feature.id, group);
    addLabel(L, feature, shape, { options, ghost, series: seriesOfFeature.get(feature.id) });
    if (isPoint) addUncertaintyLabel(L, feature, { options, ghost });
  }
  scheduleLabelLayout();
}


// ---------------------------------------------------------- reset-view button

/** "Reset view": frames the map to what it draws, again. A real <button>, so
 *  Enter and Space both work (Leaflet's own zoom buttons are links). */
function resetViewControl(L) {
  const ResetView = L.Control.extend({
    options: { position: 'topleft' },
    onAdd() {
      const bar = L.DomUtil.create('div', 'leaflet-bar leaflet-control map-reset-control');
      const btn = h('button', {
        type: 'button',
        class: 'map-reset-btn',
        id: 'map-reset-view',
        title: 'Reset view',
        'aria-label': 'Reset the view to the features this map draws',
      });
      btn.innerHTML = '<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true" focusable="false">'
        + '<path d="M2 6V2h4M10 2h4v4M14 10v4h-4M6 14H2v-4" fill="none" stroke="currentColor" '
        + 'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
      btn.addEventListener('click', () => refreshFrame({ force: true }));
      L.DomEvent.disableClickPropagation(bar);
      bar.appendChild(btn);
      return bar;
    },
  });
  return new ResetView();
}

// ----------------------------------------------------------------- labels
//
// Every drawn feature carries a permanent label, because a shape that names
// itself only in a hover tooltip leaves a reader unable to tell the LHC from
// the SPS without hovering each one. Labels are Leaflet tooltips, not map
// features: they take no clicks (the shape under them does), they are hidden
// from assistive technology (the feature list is the equivalent, and carries
// the same names), and which of them show is decided per view by
// layoutLabels(): in priority order, each label takes the first position that
// fits on screen without covering a more important label.

const LABEL_GAP_PX = 10;
const POINT_LABEL_GAPS_PX = [LABEL_GAP_PX, 40, 80];
const LABEL_PAD_PX = 3;
const LABEL_EDGE_PX = 4;
const OUTLINE_SAMPLES = 48;
// An open line is sampled this many times along its length; the label tries
// the middle of whatever part of the line is on screen first, then fans out.
const LINE_SAMPLES = 41;
// Their interior is context for the features inside them, so a label sits on
// the outline instead of on top of what is inside.
const OUTLINE_LABEL_TYPES = new Set(['boundary', 'level_outline']);

function coordBox(coords) {
  let w = Infinity;
  let s = Infinity;
  let e = -Infinity;
  let n = -Infinity;
  for (const [lon, lat] of coords) {
    w = Math.min(w, lon);
    e = Math.max(e, lon);
    s = Math.min(s, lat);
    n = Math.max(n, lat);
  }
  return { w, s, e, n };
}

function planarLength(coords) {
  const k = Math.cos(toRad(coords[0][1]));
  let total = 0;
  for (let i = 1; i < coords.length; i += 1) {
    total += Math.hypot((coords[i][0] - coords[i - 1][0]) * k, coords[i][1] - coords[i - 1][1]);
  }
  return total;
}

function isClosedLine(coords) {
  const a = coords[0];
  const b = coords[coords.length - 1];
  return coords.length > 3 && a[0] === b[0] && a[1] === b[1];
}

/** The [lon, lat] a given fraction of the way along a polyline. */
function pointAlong(coords, fraction) {
  const k = Math.cos(toRad(coords[0][1]));
  const lengths = [];
  let total = 0;
  for (let i = 1; i < coords.length; i += 1) {
    const d = Math.hypot((coords[i][0] - coords[i - 1][0]) * k, coords[i][1] - coords[i - 1][1]);
    lengths.push(d);
    total += d;
  }
  let remaining = total * fraction;
  for (let i = 0; i < lengths.length; i += 1) {
    if (remaining <= lengths[i] || i === lengths.length - 1) {
      const u = lengths[i] ? Math.min(1, remaining / lengths[i]) : 0;
      return [
        coords[i][0] + (coords[i + 1][0] - coords[i][0]) * u,
        coords[i][1] + (coords[i + 1][1] - coords[i][1]) * u,
      ];
    }
    remaining -= lengths[i];
  }
  return coords[0];
}

/** Area centroid of a ring; falls back to the box centre for a degenerate one. */
function ringCentroid(ring) {
  const k = Math.cos(toRad(ring[0][1]));
  let area = 0;
  let cx = 0;
  let cy = 0;
  for (let i = 0; i < ring.length - 1; i += 1) {
    const x0 = ring[i][0] * k;
    const y0 = ring[i][1];
    const x1 = ring[i + 1][0] * k;
    const y1 = ring[i + 1][1];
    const cross = x0 * y1 - x1 * y0;
    area += cross;
    cx += (x0 + x1) * cross;
    cy += (y0 + y1) * cross;
  }
  if (Math.abs(area) < 1e-18) {
    const box = coordBox(ring);
    return [(box.w + box.e) / 2, (box.s + box.n) / 2];
  }
  return [cx / (3 * area) / k, cy / (3 * area)];
}

/** The part of a multi-part shape a label is attached to: the biggest by
 *  bounding box (for areas) or the longest (for lines). */
function principalPart(parts, byArea) {
  let best = parts[0];
  let bestScore = -1;
  for (const part of parts) {
    const box = coordBox(part);
    const score = byArea ? (box.e - box.w) * (box.n - box.s) : planarLength(part);
    if (score > bestScore) {
      best = part;
      bestScore = score;
    }
  }
  return best;
}

/** Candidate anchors for a feature's label, as lat/lng with the placements to
 *  try at each. `kind` says how layoutLabels() should order them. */
function labelPlan(L, feature, shape) {
  const ll = ([lon, lat]) => L.latLng(lat, lon);
  const points = pointParts(shape);
  if (points.length) {
    return {
      kind: 'point',
      // A position can sit inside a building whose own label is centred on it,
      // so the label may stand a little further off, on any side.
      anchors: [{
        ll: ll(points[0]), places: ['above', 'right', 'left', 'below'], gap: LABEL_GAP_PX, gaps: POINT_LABEL_GAPS_PX,
      }],
    };
  }
  const parts = lineParts(shape);
  if (!parts.length) return null;
  const isArea = shape.type === 'Polygon' || shape.type === 'MultiPolygon';
  const part = principalPart(parts, isArea);
  const outline = () => ({
    kind: 'outline',
    anchors: Array.from({ length: OUTLINE_SAMPLES }, (_, i) => ({
      ll: ll(pointAlong(part, i / OUTLINE_SAMPLES)), places: ['center'], gap: 0,
    })),
  });
  if (isArea) {
    if (OUTLINE_LABEL_TYPES.has(feature.feature_type)) return outline();
    const box = coordBox(part);
    const midLon = (box.w + box.e) / 2;
    const midLat = (box.s + box.n) / 2;
    return {
      kind: 'area',
      box,
      anchors: [
        { id: 'centre', ll: ll(ringCentroid(part)), places: ['center'], gap: 0 },
        { id: 'above', ll: ll([midLon, box.n]), places: ['above'], gap: LABEL_PAD_PX + 1 },
        { id: 'below', ll: ll([midLon, box.s]), places: ['below'], gap: LABEL_PAD_PX + 1 },
        { id: 'right', ll: ll([box.e, midLat]), places: ['right'], gap: LABEL_PAD_PX + 1 },
        { id: 'left', ll: ll([box.w, midLat]), places: ['left'], gap: LABEL_PAD_PX + 1 },
      ],
    };
  }
  if (isClosedLine(part)) return outline();
  return {
    kind: 'line',
    anchors: Array.from({ length: LINE_SAMPLES }, (_, i) => ({
      ll: ll(pointAlong(part, i / (LINE_SAMPLES - 1))), places: ['center'], gap: LABEL_GAP_PX,
    })),
  };
}

/** Rough size of a feature in metres (its bounding-box diagonal, or the
 *  accuracy circle of a point): the tie-break after feature type. */
function featureSizeM(feature) {
  const points = pointParts(feature.geometry);
  if (points.length) return 2 * pointRadius(feature);
  const parts = lineParts(feature.geometry);
  if (!parts.length) return 0;
  let w = Infinity;
  let s = Infinity;
  let e = -Infinity;
  let n = -Infinity;
  for (const part of parts) {
    const box = coordBox(part);
    w = Math.min(w, box.w);
    e = Math.max(e, box.e);
    s = Math.min(s, box.s);
    n = Math.max(n, box.n);
  }
  return greatCircleM([s, w], [n, e]);
}

// A footprint or line that is drawn smaller than this on screen is
// effectively invisible (JUNO's reactor buildings are ~50 m each and 52 km
// from the detector: at the scale that frames both, each is under a pixel),
// so it also gets a point symbol, which goes away once the shape is big enough.
const SYMBOL_BELOW_PX = 8;
const SYMBOL_SIZE_PX = 14;
const SYMBOL_LABEL_GAPS_PX = [SYMBOL_SIZE_PX / 2 + 5, 40, 80];
const LINE_TYPES = new Set(['ring', 'tunnel', 'linac', 'beamline', 'transfer_line', 'direction_line', 'road']);
const FOOTPRINT_TYPES = new Set(['hall', 'cavern', 'building', 'experimental_area', 'target_station',
  'shaft', 'array', 'string']);

/** The symbol's shape follows the feature type, the way the stroke does: a
 *  diamond for a line-like structure, a square for a footprint, a circle
 *  for anything else. */
function symbolShape(featureType) {
  if (LINE_TYPES.has(featureType)) return 'diamond';
  if (FOOTPRINT_TYPES.has(featureType)) return 'square';
  return 'circle';
}

function unionBox(parts) {
  const box = { w: Infinity, s: Infinity, e: -Infinity, n: -Infinity };
  for (const part of parts) {
    const b = coordBox(part);
    box.w = Math.min(box.w, b.w);
    box.e = Math.max(box.e, b.e);
    box.s = Math.min(box.s, b.s);
    box.n = Math.max(box.n, b.n);
  }
  return box;
}

/** The point symbol for a polygon or line feature (not for a Point, which
 *  already draws a centre mark): same colour, hover tooltip and click as the
 *  shape it stands for. Added to the map only while the shape is tiny. */
function symbolFor(L, feature, shape, { options, ghost, series }) {
  const parts = lineParts(shape);
  if (!parts.length) return null;
  const isArea = shape.type === 'Polygon' || shape.type === 'MultiPolygon';
  const part = principalPart(parts, isArea);
  const [lon, lat] = isArea ? ringCentroid(part) : pointAlong(part, 0.5);
  const icon = L.divIcon({
    className: 'map-symbol-icon',
    html: `<span class="map-symbol map-symbol-${symbolShape(feature.feature_type)}"></span>`,
    iconSize: [SYMBOL_SIZE_PX, SYMBOL_SIZE_PX],
    iconAnchor: [SYMBOL_SIZE_PX / 2, SYMBOL_SIZE_PX / 2],
  });
  const marker = L.marker([lat, lon], { icon, keyboard: false, riseOnHover: false });
  marker.bindTooltip(series
    ? `${series.text}\n${series.count} records drawn, each listed under "Features on this map"`
    : tooltipFor(feature), { sticky: true, className: 'map-tooltip' });
  // A series' symbol stands for many records, so it opens none of them.
  if (!series) marker.on('click', () => selectFrom(feature, null));
  marker.on('add', () => {
    const el = marker.getElement();
    if (!el) return;
    // Decoration: the feature list is the screen-reader equivalent.
    el.setAttribute('aria-hidden', 'true');
    el.setAttribute('data-symbol-for', feature.id);
    el.style.setProperty('--symbol-color', options.color);
    el.classList.toggle('is-ghosted', ghost);
    el.classList.toggle('is-selected', !!view.sel && (view.sel === feature.entity_id || view.sel === feature.id));
  });
  return { marker, centre: L.latLng(lat, lon), extent: unionBox(parts) };
}

/** Show a feature's point symbol while its shape is drawn smaller than
 *  SYMBOL_BELOW_PX across, and take it off again once the shape is bigger. */
function updateSymbols() {
  if (!mapInstance || !symbolLayer) return;
  for (const rec of labelRecords.values()) {
    if (!rec.symbol) continue;
    const a = mapInstance.latLngToContainerPoint([rec.symbol.extent.s, rec.symbol.extent.w]);
    const b = mapInstance.latLngToContainerPoint([rec.symbol.extent.n, rec.symbol.extent.e]);
    const tiny = Math.max(Math.abs(a.x - b.x), Math.abs(a.y - b.y)) < SYMBOL_BELOW_PX;
    if (tiny && !rec.symbolShown) symbolLayer.addLayer(rec.symbol.marker);
    else if (!tiny && rec.symbolShown) symbolLayer.removeLayer(rec.symbol.marker);
    rec.symbolShown = tiny;
  }
}

/**
 * Group the drawn features into series (see mapstyle.seriesOf): three or more
 * numbered records of one thing share a single label at the middle of the
 * whole run, which counts as selected when any member is (the selection is
 * usually the array's entity, shared by all of them). Returns a map from
 * feature id to `{ leader: true, ... }` for the member that carries the label,
 * or `{ leader: false }` for the rest.
 */
function collapseSeries(features) {
  const groups = new Map();
  for (const feature of features) {
    if (pointParts(feature.geometry).length || !lineParts(feature.geometry).length) continue;
    const info = mapstyle.seriesOf(feature);
    if (!info) continue;
    if (!groups.has(info.key)) groups.set(info.key, { info, members: [] });
    groups.get(info.key).members.push(feature);
  }
  const out = new Map();
  for (const { info, members } of groups.values()) {
    if (members.length < mapstyle.SERIES_MIN_MEMBERS) continue;
    const box = unionBox(members.flatMap((m) => lineParts(m.geometry)));
    const [leader, ...rest] = members;
    out.set(leader.id, {
      leader: true,
      text: mapstyle.seriesLabel(info, members.length),
      count: members.length,
      memberIds: new Set(members.map((m) => m.id)),
      selected: members.some((m) => !!view.sel && (view.sel === m.entity_id || view.sel === m.id)),
      // The rectangle the whole run covers, so the label sits at its middle.
      shape: {
        type: 'Polygon',
        coordinates: [[[box.w, box.s], [box.e, box.s], [box.e, box.n], [box.w, box.n], [box.w, box.s]]],
      },
    });
    for (const member of rest) out.set(member.id, { leader: false });
  }
  return out;
}

function addLabel(L, feature, shape, { options, ghost, series }) {
  if (series && !series.leader) return;
  const labelShape = series ? series.shape : shape;
  const plan = labelPlan(L, feature, labelShape);
  if (!plan) return;
  const spec = series
    ? { text: series.text, sub: '' }
    : (labelTexts.get(feature.id) || { text: feature.entity_name || feature.name, sub: '' });
  const rank = mapstyle.labelRank(feature.feature_type, { experimentSite: isExperimentSite(feature) });
  const selected = series ? series.selected : !!view.sel && (view.sel === feature.entity_id || view.sel === feature.id);
  const content = h('span', { class: 'map-label-text' }, [
    h('span', { class: 'map-label-name' }, spec.text),
    spec.sub ? h('span', { class: 'map-label-sub' }, spec.sub) : null,
  ]);
  const classes = ['map-label', 'is-hidden'];
  if (ghost) classes.push('is-ghosted');
  if (selected) classes.push('is-selected');
  if (rank <= 1) classes.push('is-principal');
  const tooltip = L.tooltip({
    permanent: true, direction: 'center', opacity: 1, interactive: false, className: classes.join(' '),
  }).setLatLng(plan.anchors[0].ll).setContent(content);
  labelLayer.addLayer(tooltip);
  const el = tooltip.getElement();
  if (el) {
    // The feature list carries every name; the map's copy is decoration for a
    // screen reader, and would otherwise read as a stray "tooltip".
    el.removeAttribute('role');
    el.setAttribute('aria-hidden', 'true');
    el.setAttribute('data-label-for', feature.id);
    el.style.setProperty('--label-accent', options.color);
  }
  labelRecords.set(feature.id, {
    id: feature.id,
    tooltip,
    plan,
    rank,
    selected,
    sizeM: series ? featureSizeM({ ...feature, geometry: series.shape }) : featureSizeM(feature),
    memberIds: series ? series.memberIds : null,
    box: { w: 0, h: 0 },
    lastKey: null,
    symbol: symbolFor(L, feature, labelShape, { options, ghost, series }),
    symbolShown: false,
  });
}

/** Sites that hold a detector placement, by site id (built once per atlas). */
let detectorSiteIds = null;

function hostsDetector(siteId) {
  if (!detectorSiteIds) {
    detectorSiteIds = new Set();
    for (const detector of Object.values((ATLAS && ATLAS.detectors) || {})) {
      for (const placement of detector.placements || []) detectorSiteIds.add(placement.site_id);
    }
  }
  return detectorSiteIds.has(siteId);
}

/** True for a feature that stands for the place an experiment's detector sits
 *  but is drawn as a surface-site outline — an LHC point's boundary polygon: a
 *  site underground (a cavern) that has a detector placed in it. A cavern or hall
 *  drawn as such already ranks with the caverns; it is the outline that was
 *  ranked with the campus fences. */
function isExperimentSite(feature) {
  if (feature.entity_type !== 'site' || feature.feature_type !== 'boundary') return false;
  const site = INDEX ? INDEX.get(feature.entity_id) : null;
  return !!site && site.setting === 'underground' && hostsDetector(site.id);
}

// The label on a position's accuracy circle (mapstyle.uncertaintyLabel). It is
// shown only while the circle is big enough on screen to read as a shape, and it
// takes the topmost spot on the ring that is free.
const UNCERTAINTY_MIN_RADIUS_PX = 24;
const UNCERTAINTY_RING_SAMPLES = 24;
const UNCERTAINTY_LABEL_RANK = 4;

function addUncertaintyLabel(L, feature, { options, ghost }) {
  const parts = mapstyle.uncertaintyParts(feature);
  const [centre] = pointParts(feature.geometry);
  if (!parts || !centre) return;
  const [lon, lat] = centre;
  const radiusM = pointRadius(feature);
  // A sample on the ring, with the side of it the label stands on: above the top
  // of the circle, to the right of its right edge, and so on, so the label never
  // covers the ring it explains.
  const anchors = Array.from({ length: UNCERTAINTY_RING_SAMPLES }, (_, i) => {
    const bearing = (i * 360) / UNCERTAINTY_RING_SAMPLES;
    const [plat, plon] = destination(lat, lon, bearing, radiusM);
    const side = bearing >= 315 || bearing < 45 ? 'above' : (bearing < 135 ? 'right' : (bearing < 225 ? 'below' : 'left'));
    return { ll: L.latLng(plat, plon), places: [side], gap: LABEL_PAD_PX + 2 };
  });
  const classes = ['map-label', 'map-label-uncertainty', 'is-hidden'];
  if (ghost) classes.push('is-ghosted');
  const tooltip = L.tooltip({
    permanent: true, direction: 'center', opacity: 1, interactive: false, className: classes.join(' '),
  }).setLatLng(anchors[0].ll).setContent(h('span', { class: 'map-label-text' }, [
    h('span', { class: 'map-label-name' }, [
      `${parts.lead} `, h('span', { class: 'map-label-keep' }, parts.figure), ' ',
      h('span', { class: 'map-label-keep' }, parts.tail),
    ]),
  ]));
  labelLayer.addLayer(tooltip);
  const el = tooltip.getElement();
  if (el) {
    el.removeAttribute('role');
    el.setAttribute('aria-hidden', 'true');
    el.setAttribute('data-label-for', `${feature.id}#uncertainty`);
    el.style.setProperty('--label-accent', options.color);
  }
  const id = `${feature.id}#uncertainty`;
  labelRecords.set(id, {
    id,
    tooltip,
    plan: { kind: 'outline', anchors },
    rank: UNCERTAINTY_LABEL_RANK,
    selected: false,
    sizeM: 0,
    // Hovering the feature's list row asks for this label with it.
    memberIds: new Set([feature.id]),
    box: { w: 0, h: 0 },
    lastKey: null,
    symbol: null,
    symbolShown: false,
    circle: { centre: L.latLng(lat, lon), north: anchors[0].ll, text: mapstyle.uncertaintyLabel(feature) },
  });
}

/** Whether a record's accuracy circle is drawn big enough, on screen, for its label. */
function circleReadable(rec) {
  if (!rec.circle) return true;
  const a = mapInstance.latLngToContainerPoint(rec.circle.centre);
  const b = mapInstance.latLngToContainerPoint(rec.circle.north);
  return Math.hypot(a.x - b.x, a.y - b.y) >= UNCERTAINTY_MIN_RADIUS_PX;
}

function scheduleLabelLayout() {
  if (labelFrame || !mapInstance) return;
  labelFrame = window.requestAnimationFrame(() => {
    labelFrame = 0;
    layoutLabels();
  });
}

/** Show a feature's label whatever the declutter says: its list row is being
 *  hovered or focused, so the reader is asking which shape it is. */
function revealLabel(featureId) {
  if (forcedLabelId === featureId) return;
  forcedLabelId = featureId;
  scheduleLabelLayout();
}

/** A hovered or focused list row asks for its own label — or, if the row is
 *  one member of a series, for the series' single label. */
function isForced(rec) {
  return !!forcedLabelId && (rec.id === forcedLabelId || (!!rec.memberIds && rec.memberIds.has(forcedLabelId)));
}

function labelPriority(a, b) {
  const forced = (rec) => (isForced(rec) ? 0 : 1);
  if (forced(a) !== forced(b)) return forced(a) - forced(b);
  if (a.selected !== b.selected) return a.selected ? -1 : 1;
  if (a.rank !== b.rank) return a.rank - b.rank;
  if (a.sizeM !== b.sizeM) return b.sizeM - a.sizeM;
  return a.id < b.id ? -1 : 1;
}

/** Screen boxes the labels must keep clear of: the map's own controls and the
 *  notices laid over it, which sit above the tooltip pane. */
function obstacleBoxes() {
  const container = mapInstance.getContainer();
  const origin = container.getBoundingClientRect();
  const nodes = [...container.querySelectorAll('.leaflet-control')];
  nodes.push(...dom.stage.querySelectorAll(
    '.map-north, .map-tile-notice:not(.hidden), .map-empty-notice, .map-gap-notice.on-stage, .map-depth:not(.hidden)',
  ));
  const boxes = [];
  for (const node of nodes) {
    const r = node.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    boxes.push({
      x: r.left - origin.left - LABEL_PAD_PX,
      y: r.top - origin.top - LABEL_PAD_PX,
      w: r.width + 2 * LABEL_PAD_PX,
      h: r.height + 2 * LABEL_PAD_PX,
    });
  }
  return boxes;
}

function boxesOverlap(a, b) {
  return a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;
}

function labelBox(candidate, size) {
  const { x, y } = candidate.point;
  const { w, h } = size;
  switch (candidate.place) {
    case 'above': return { x: x - w / 2, y: y - candidate.gap - h, w, h };
    case 'below': return { x: x - w / 2, y: y + candidate.gap, w, h };
    case 'right': return { x: x + candidate.gap, y: y - h / 2, w, h };
    case 'left': return { x: x - candidate.gap - w, y: y - h / 2, w, h };
    default: return { x: x - w / 2, y: y - h / 2, w, h };
  }
}

/** The positions a label may take in the current view, best first. */
function labelCandidates(rec) {
  if (rec.symbolShown) {
    // The shape is a few pixels across and stands as a point symbol: its label
    // goes beside the symbol, as a Point's does, not on top of it.
    const point = mapInstance.latLngToContainerPoint(rec.symbol.centre);
    const out = [];
    for (const gap of SYMBOL_LABEL_GAPS_PX) {
      for (const place of ['above', 'right', 'left', 'below']) {
        out.push({ key: `s:${place}:${gap}`, point, place, gap });
      }
    }
    const kept = out.findIndex((c) => c.key === rec.lastKey);
    if (kept > 0) out.unshift(out.splice(kept, 1)[0]);
    return out;
  }
  const { plan } = rec;
  const project = (anchor) => mapInstance.latLngToContainerPoint(anchor.ll);
  let anchors = plan.anchors.map((anchor, index) => ({ anchor, index, point: project(anchor) }));
  if (plan.kind === 'outline') {
    // On a ring or an outline the label sits on the line, topmost first: the
    // 12 o'clock of a ring reads as its name plate and rarely covers another.
    anchors = anchors.slice().sort((a, b) => a.point.y - b.point.y || a.index - b.index);
  } else if (plan.kind === 'line') {
    // At a line's midpoint — or, when the view shows only part of it, the
    // midpoint of the part that is shown — then outwards from there.
    const size = mapInstance.getSize();
    const visible = anchors.filter(({ point }) => point.x >= 0 && point.y >= 0
      && point.x <= size.x && point.y <= size.y);
    if (visible.length) {
      const middle = visible[Math.floor(visible.length / 2)].index;
      anchors = visible.slice().sort((a, b) => Math.abs(a.index - middle) - Math.abs(b.index - middle)
        || a.index - b.index);
      // The first few also try just above and below, so a label can sit beside
      // a line that a more important label is crossing.
      anchors = anchors.map((entry, i) => (i < 3
        ? { ...entry, anchor: { ...entry.anchor, places: ['center', 'above', 'below'] } } : entry));
    } else {
      anchors = [];
    }
  } else if (plan.kind === 'area') {
    // A footprint smaller than its own label would be hidden by it, so the
    // label goes beside it instead.
    const sw = mapInstance.latLngToContainerPoint([plan.box.s, plan.box.w]);
    const ne = mapInstance.latLngToContainerPoint([plan.box.n, plan.box.e]);
    const small = Math.abs(ne.x - sw.x) < rec.box.w || Math.abs(sw.y - ne.y) < rec.box.h;
    if (small) anchors = anchors.slice(1).concat(anchors[0]);
  }
  const out = [];
  for (const { anchor, index, point } of anchors) {
    for (const gap of anchor.gaps || [anchor.gap]) {
      for (const place of anchor.places) {
        out.push({ key: `${index}:${place}:${gap}`, point, place, gap });
      }
    }
  }
  // A label that has a working position keeps it, so panning does not make
  // names skate around their ring.
  const kept = out.findIndex((c) => c.key === rec.lastKey);
  if (kept > 0) out.unshift(out.splice(kept, 1)[0]);
  return out;
}

/**
 * Decide which labels show, and where, for the current view. Highest priority
 * first (the selected feature, then by feature type, then by size); each
 * takes the first candidate position that is on screen and clear of every
 * label already placed and of the map's controls. A label with no such
 * position is hidden — its name is still in the hover tooltip and the list.
 */
function layoutLabels() {
  if (!mapInstance) return;
  const container = mapInstance.getContainer();
  const mapSize = mapInstance.getSize();
  if (!mapSize.x || !mapSize.y || !labelRecords.size) {
    container.classList.remove('map-labels-busy');
    return;
  }
  updateSymbols();
  const blocked = obstacleBoxes();
  const placed = [];
  const ringTextsShown = new Set();
  const inView = (box) => box.x >= LABEL_EDGE_PX && box.y >= LABEL_EDGE_PX
    && box.x + box.w <= mapSize.x - LABEL_EDGE_PX && box.y + box.h <= mapSize.y - LABEL_EDGE_PX;
  const order = [...labelRecords.values()].sort(labelPriority);
  for (const rec of order) {
    const el = rec.tooltip.getElement();
    if (!el) continue;
    if (!rec.box.w || !rec.box.h) rec.box = { w: el.offsetWidth, h: el.offsetHeight };
    if (!rec.box.w || !rec.box.h) continue;
    const forced = isForced(rec);
    // Four telescopes with the same ±15 m would carry four identical chips: say
    // it once (the legend and every tooltip say it for the rest), unless the
    // reader is asking about that one.
    if (!circleReadable(rec) || (rec.circle && !forced && ringTextsShown.has(rec.circle.text))) {
      el.classList.add('is-hidden');
      continue;
    }
    let chosen = null;
    let fallback = null;
    for (const candidate of labelCandidates(rec)) {
      const box = labelBox(candidate, rec.box);
      if (!inView(box)) continue;
      if (!fallback) fallback = { candidate, box };
      const clear = !placed.some((other) => boxesOverlap(box, other))
        && !blocked.some((other) => boxesOverlap(box, other));
      if (clear) {
        chosen = { candidate, box };
        break;
      }
    }
    if (!chosen && forced) chosen = fallback;
    el.classList.toggle('is-forced', forced);
    if (!chosen) {
      el.classList.add('is-hidden');
      continue;
    }
    placed.push({
      x: chosen.box.x - LABEL_PAD_PX,
      y: chosen.box.y - LABEL_PAD_PX,
      w: chosen.box.w + 2 * LABEL_PAD_PX,
      h: chosen.box.h + 2 * LABEL_PAD_PX,
    });
    rec.lastKey = chosen.candidate.key;
    if (rec.circle) ringTextsShown.add(rec.circle.text);
    rec.tooltip.setLatLng(mapInstance.containerPointToLatLng([
      chosen.box.x + chosen.box.w / 2, chosen.box.y + chosen.box.h / 2,
    ]));
    el.classList.remove('is-hidden');
  }
  container.classList.remove('map-labels-busy');
}

// ------------------------------------------------------------- selection

function selectFrom(feature, trigger) {
  selOpener = trigger || document.activeElement;
  const target = feature.entity_id || feature.id;
  NAVIGATE({ sel: target });
}

function clearSelection() {
  const opener = selOpener;
  selOpener = null;
  NAVIGATE({ sel: null });
  if (opener && document.body.contains(opener)) opener.focus({ preventScroll: true });
}

// ------------------------------------------------------------ left column

function toggleButton(label, pressed, onClick, extraClass) {
  // A plain-text label is wrapped so the pressed/unpressed state can be
  // shown as a leading check or cross as well as a colour — no toggle in
  // this view is distinguishable by colour alone.
  const body = typeof label === 'string' ? h('span', { class: 'map-toggle-name' }, label) : label;
  const btn = h('button', {
    type: 'button',
    class: `map-toggle ${extraClass || ''}`.trim(),
    'aria-pressed': pressed ? 'true' : 'false',
  }, body);
  btn.addEventListener('click', onClick);
  return btn;
}

function panelSection(titleText, nodes, { open = true, className = '' } = {}) {
  const details = h('details', { class: `map-section ${className}`.trim(), open: open ? '' : null });
  details.appendChild(h('summary', {}, titleText));
  details.appendChild(h('div', { class: 'map-section-body' }, nodes));
  return details;
}

function featureRow(feature) {
  const t = mapstyle.typeStyle(feature.feature_type);
  const level = levelById(feature.level_id);
  const s = featureStatus(feature);
  const ghost = !s.timeless && !s.status;
  const selected = view.sel && (view.sel === feature.entity_id || view.sel === feature.id);
  const statusText = s.timeless
    ? 'every year (context feature)'
    : (s.status ? mapstyle.statusStyle(s.status).label
      : `${{
        not_yet: 'not yet built', ended: 'no longer present', gap: 'no recorded status',
        no_history: 'no recorded history',
      }[timelineAbsenceReason(feature.state_segments, view.timelineState || {})] || 'not present'} in ${whenLabel()}`);
  const isPoint = feature.geometry.type === 'Point' || feature.geometry.type === 'MultiPoint';
  const btn = h('button', {
    type: 'button',
    class: `map-feature-row${ghost ? ' is-ghosted' : ''}${selected ? ' is-selected' : ''}`,
    'aria-pressed': selected ? 'true' : 'false',
    'data-feature-row': feature.id,
  }, [
    h('span', { class: 'map-feature-name' }, feature.entity_name || feature.name),
    h('span', { class: 'map-feature-meta' },
      `${t.label} · ${level ? level.name : feature.level_id}`),
    h('span', { class: 'map-feature-meta' },
      `${statusText} · ${mapstyle.accuracyText(feature)}`),
    isPoint ? h('span', { class: 'map-feature-meta' }, 'position only — no sourced footprint') : null,
  ]);
  btn.addEventListener('click', () => selectFrom(feature, btn));
  // Hovering or focusing a row shows that feature's map label even if the
  // declutter has hidden it, so the list and the map can be read together.
  btn.addEventListener('mouseenter', () => revealLabel(feature.id));
  btn.addEventListener('focus', () => revealLabel(feature.id));
  btn.addEventListener('mouseleave', () => revealLabel(null));
  btn.addEventListener('blur', () => revealLabel(null));
  return btn;
}

function renderLevels() {
  const rows = [];
  for (const level of mapMeta.levels || []) {
    const on = visibleLevelIds().includes(level.id);
    const depthText = level.depth_m ? quantityText(level.depth_m) : null;
    const kindText = mapstyle.LEVEL_KIND_LABEL[level.kind] || titleCase(level.kind);
    const count = bundle.features.filter((f) => f.level_id === level.id).length;
    const btn = toggleButton([
      h('span', { class: 'map-toggle-name' }, level.name),
      h('span', { class: 'map-toggle-meta' },
        `${kindText}${depthText ? ` · ${depthText} below surface` : ''} · ${count} feature${count === 1 ? '' : 's'}`),
    ], on, () => {
      const next = new Set(visibleLevelIds());
      if (next.has(level.id)) next.delete(level.id); else next.add(level.id);
      NAVIGATE({ levels: (mapMeta.levels || []).map((lv) => lv.id).filter((id) => next.has(id)) });
    }, 'map-level-toggle');
    btn.setAttribute('data-level-id', level.id);
    rows.push(btn);
  }
  return rows;
}

/** The name a record id stands for on this map, or null when the bundles do not
 *  say. Used to turn the ids in a recorded reason into words a reader can use. */
function nameForId(id) {
  const type = String(id).split(':')[0];
  if (type === 'src') {
    const row = (bundle.source_titles || {})[id];
    // A source's title can carry its own brackets and a talk's date; the part
    // before them is what it is called.
    return row && row.title ? row.title.replace(/\s+\(.*$/, '').trim() : null;
  }
  if (type === 'geometry') {
    const feature = (bundle.features || []).find((f) => f.id === id);
    return feature ? (feature.entity_name || feature.name) : null;
  }
  const record = INDEX ? INDEX.get(id) : null;
  return record && record.name ? record.name : null;
}

/** One entry of "Unlocated / geometry not verified": what is not drawn, the one
 *  plain reason, the sources it rests on, and — collapsed — the research notes
 *  (the full recorded reason, what would settle it, and the record ids). */
function unlocatedRow(row) {
  const name = row.entity_name || row.entity_id || 'Unnamed';
  const notes = researchNotes(row, nameForId);
  const sources = (row.sources || []).map((sid) => nameForId(sid)).filter(Boolean);
  const reason = plainReason(row.reason, { resolve: nameForId, name });
  const noteNodes = [];
  // Only worth repeating when the reader's sentence is not already all of it.
  if (notes.reason && notes.reason.replace(/\s+/g, ' ') !== reason) {
    noteNodes.push(h('p', { class: 'map-research-label' }, 'Full reason as recorded'),
      h('p', { class: 'map-research-text' }, notes.reason));
  }
  if (notes.backlog) {
    noteNodes.push(h('p', { class: 'map-research-label' }, 'What would let us draw it'),
      h('p', { class: 'map-research-text' }, notes.backlog));
  }
  const ids = [...new Set([row.entity_id, ...(row.sources || []), ...notes.ids].filter(Boolean))];
  if (ids.length) {
    noteNodes.push(h('p', { class: 'map-research-label' }, 'Record ids'),
      h('p', { class: 'map-research-ids' }, ids.join(' · ')));
  }
  return h('li', { class: 'map-unlocated-row' }, [
    h('div', { class: 'map-unlocated-name entity-link-with-meta' },
      row.entity_id ? [
        h('a', {
          href: `#/${idRoute(row.entity_id).type}/${idRoute(row.entity_id).slug}`,
          class: 'entity-link',
          onclick: (event) => { event.preventDefault(); NAVIGATE({ entity: idRoute(row.entity_id) }); },
        }, row.entity_name || row.entity_id),
        row.entity_type ? h('span', { class: 'map-feature-meta' }, ` · ${titleCase(row.entity_type)}`) : null,
      ] : name),
    h('p', { class: 'map-unlocated-reason' }, reason),
    h('p', { class: 'source-meta' }, sources.length ? `Sources: ${sources.join('; ')}` : 'No source recorded.'),
    noteNodes.length
      ? h('details', { class: 'map-research-notes' }, [h('summary', {}, 'Research notes'), ...noteNodes])
      : null,
  ]);
}

function renderUnlocated() {
  const rows = (bundle.map.unlocated || []).map(unlocatedRow);
  if (!rows.length) {
    return [h('p', { class: 'empty-note' },
      'Every accelerator, beamline and detector-hosting site this map accounts for is drawn.')];
  }
  return [
    h('p', { class: 'map-note' },
      'These belong to this facility but are deliberately not drawn: no fetched public source '
      + 'supports a shape for them. They are missing evidence, not missing from the laboratory.'),
    h('ul', { class: 'map-unlocated-list' }, rows),
  ];
}

function linkedDestinations() {
  const rows = [];
  const center = [mapMeta.center.lat, mapMeta.center.lon];
  const onThisMap = new Set(mapMeta.site_ids || []);
  for (const mid of mapMeta.linked_map_ids || []) {
    const other = (ATLAS.maps || {})[mid];
    if (!other) continue;
    const to = [other.center.lat, other.center.lon];
    rows.push({
      kind: 'map', id: mid, name: other.name, route: idRoute(mid),
      metres: greatCircleM(center, to), bearing: initialBearing(center, to),
    });
  }
  const beamlines = Object.values(ATLAS.beamlines || {})
    .filter((b) => b.facility_id === mapMeta.facility_id);
  for (const beamline of beamlines) {
    for (const sid of beamline.far_detector_site_ids || []) {
      if (onThisMap.has(sid) || rows.some((r) => r.id === sid)) continue;
      const site = (ATLAS.sites || {})[sid];
      if (!site || site.lat == null) continue;
      const to = [site.lat, site.lon];
      rows.push({
        kind: 'site', id: sid, name: site.name, route: idRoute(sid), via: beamline.name,
        mapId: site.map_id || null,
        metres: greatCircleM(center, to), bearing: initialBearing(center, to),
      });
    }
  }
  rows.sort((a, b) => a.metres - b.metres);
  return rows;
}

function renderLinked() {
  const rows = linkedDestinations();
  if (!rows.length) {
    return [h('p', { class: 'empty-note' }, 'No off-campus destination is recorded for this facility.')];
  }
  return [
    h('p', { class: 'map-note' },
      'Off-campus destinations are never drawn inside this campus. Their distance and bearing '
      + 'from the map centre are given instead.'),
    h('ul', { class: 'map-linked-list' }, rows.map((row) => {
      const target = row.mapId ? idRoute(row.mapId) : row.route;
      const link = h('a', {
        href: `#/${target.type}/${target.slug}`,
        class: 'entity-link',
        onclick: (event) => { event.preventDefault(); NAVIGATE({ entity: target, sel: null, levels: null }); },
      }, row.mapId ? `${row.name} — open its local map` : row.name);
      return h('li', { class: 'entity-link-with-meta' }, [
        link,
        h('div', { class: 'map-feature-meta' },
          `${formatDistance(row.metres)} · bearing ${row.bearing.toFixed(0)}° (${compassPoint(row.bearing)})`
          + (row.via ? ` · via ${row.via}` : '')),
      ]);
    })),
  ];
}

function renderSchematics() {
  const items = bundle.map.schematics || [];
  if (!items.length) return [h('p', { class: 'empty-note' }, 'No official schematic is recorded for this facility.')];
  return [
    h('p', { class: 'map-note' },
      'Schematics are offered as links only. They are not to scale and are never drawn on this map.'),
    h('ul', { class: 'map-schematic-list' }, items.map((s) => h('li', { class: 'entity-link-with-meta' }, [
      h('a', { href: s.url || '#', target: '_blank', rel: 'noopener' }, s.title),
      h('div', { class: 'map-feature-meta' }, 'not to scale'),
      s.note ? h('div', { class: 'source-meta' }, s.note) : null,
    ]))),
  ];
}

function renderLegend() {
  const groups = mapstyle.legendGroups(mapMeta.levels || []);
  return groups.map((group) => h('div', { class: 'map-legend-group' }, [
    h('h4', {}, group.title),
    h('p', { class: 'map-note' }, group.note),
    h('dl', { class: 'map-legend-list' }, group.rows.flatMap(([cls, term, hint]) => [
      h('dt', {}, [h('i', { class: `map-swatch ${cls}`, 'aria-hidden': 'true' }), term]),
      h('dd', {}, hint),
    ])),
  ]));
}

function sourceTitle(sid) {
  const row = (bundle.source_titles || {})[sid];
  if (!row) return sid;
  return row.title || sid;
}

function renderSidebar() {
  const { layers } = dom;
  layers.innerHTML = '';
  // The rows are rebuilt, so a hovered or focused one is gone without a blur.
  if (forcedLabelId) revealLabel(null);

  const back = h('button', { type: 'button', class: 'map-back-btn', id: 'map-back' }, '← Back to globe');
  back.addEventListener('click', () => NAVIGATE({ entity: null, sel: null, levels: null, basemap: true }));
  layers.appendChild(back);

  layers.appendChild(h('h2', { class: 'map-title', id: 'map-title', tabindex: '-1' }, mapMeta.name));
  const facility = (ATLAS.facilities || {})[mapMeta.facility_id];
  layers.appendChild(h('p', { class: 'map-subtitle' }, [
    `${mapMeta.to_scale_count} feature${mapMeta.to_scale_count === 1 ? '' : 's'} drawn to scale`,
    mapMeta.unlocated_count
      ? ` · ${mapMeta.unlocated_count} entit${mapMeta.unlocated_count === 1 ? 'y' : 'ies'} not drawn (geometry not verified)`
      : '',
  ]));
  if (facility) {
    const facLink = h('a', {
      href: `#/facility/${facility.id.split(':')[1]}`, class: 'entity-link',
      onclick: (event) => { event.preventDefault(); NAVIGATE({ entity: idRoute(facility.id), sel: null, levels: null }); },
    }, `Open the ${facility.name} record`);
    layers.appendChild(h('p', { class: 'map-subtitle entity-link-with-meta' }, facLink));
  }
  for (const note of (bundle.map.notes || [])) {
    layers.appendChild(h('p', { class: 'map-data-note', role: 'note' }, note));
  }

  layers.appendChild(h('p', { class: 'visually-hidden', id: 'map-selection-live', role: 'status', 'aria-live': 'polite' },
    lastAnnouncedSel || ''));

  // ---- view controls
  const basemapBtn = toggleButton('OpenStreetMap basemap', view.basemap && !polarProjection, () => {
    if (polarProjection) return;
    NAVIGATE({ basemap: !view.basemap });
  }, 'map-basemap-toggle');
  basemapBtn.id = 'map-basemap-toggle';
  if (polarProjection) {
    basemapBtn.disabled = true;
    basemapBtn.setAttribute('aria-disabled', 'true');
    basemapBtn.setAttribute('aria-describedby', 'map-basemap-unavailable');
  }
  const outsideBtn = toggleButton('Show features outside the selected year', showOutside, () => {
    showOutside = !showOutside;
    redraw();
  }, 'map-outside-toggle');
  outsideBtn.id = 'map-outside-toggle';
  const depthBtn = h('button', {
    type: 'button', class: 'map-toggle map-depth-toggle', id: 'map-depth-toggle',
    'aria-expanded': depthOpen ? 'true' : 'false', 'aria-controls': 'map-depth',
  }, 'Depth view — vertical section diagram');
  depthBtn.addEventListener('click', () => { depthOpen = !depthOpen; renderDepth(); renderSidebar(); });
  layers.appendChild(panelSection('View', [
    basemapBtn,
    polarProjection
      ? h('p', { class: 'map-note', id: 'map-basemap-unavailable' },
        'No basemap at the pole: OpenStreetMap\u2019s tiles are Web Mercator, which cannot '
        + 'represent latitude 90\u00b0. This map uses a local azimuthal projection in metres '
        + 'instead, so there is no basemap to turn on.')
      : null,
    outsideBtn,
    depthBtn,
  ]));

  layers.appendChild(panelSection('Levels', [
    h('p', { class: 'map-note' },
      'Each feature belongs to exactly one level. Turn a level off to take its features off the map.'),
    ...renderLevels(),
  ]));

  // ---- features, grouped by level
  const featureNodes = [];
  for (const level of mapMeta.levels || []) {
    const rows = bundle.features
      .filter((f) => f.level_id === level.id)
      .filter((f) => visibleLevelIds().includes(f.level_id))
      // Same predicate as the map, so the list and the map never disagree
      // about what is on screen (a browser test asserts set equality).
      .filter((f) => showOutside || inSelectedYear(f) || isSelectionGhost(f));
    if (!rows.length) continue;
    featureNodes.push(h('h4', { class: 'map-feature-group' }, level.name));
    featureNodes.push(h('div', { class: 'map-feature-rows' }, rows.map(featureRow)));
  }
  if (!featureNodes.length) {
    featureNodes.push(h('p', { class: 'empty-note' },
      `No feature of this map is both on a visible level and present in ${whenLabel()}. `
      + 'That is a filter, not a statement about the laboratory — turn a level back on, '
      + 'move the timeline, or switch on “show features outside the selected year”.'));
  }
  layers.appendChild(panelSection('Features on this map', featureNodes));

  layers.appendChild(panelSection('Unlocated / geometry not verified', renderUnlocated()));
  layers.appendChild(panelSection('Linked maps and far sites', renderLinked(), { open: false }));
  layers.appendChild(panelSection('Schematics (not to scale)', renderSchematics(), { open: false }));
  // A map whose only drawn things are positions (and stand-in shapes) is read
  // through its legend — it says what the circles are — so it starts open there.
  layers.appendChild(panelSection('Legend', renderLegend(), { open: mapstyle.isPositionOnlyMap(bundle.features) }));

  if ((bundle.attribution || []).length) {
    layers.appendChild(h('p', { class: 'map-attribution' },
      `Geometry: ${bundle.attribution.join('; ')}`));
  }
}

// --------------------------------------------------------------- drawer

function checkRow(check) {
  const unit = checkUnit(check.kind);
  const expected = check.expected_m != null ? `${check.expected_m} ${unit}` : '—';
  const measured = check.measured_m != null ? `${check.measured_m} ${unit}` : '—';
  return h('li', { class: `map-check ${check.passed ? 'is-passed' : 'is-failed'}` }, [
    h('span', { class: 'map-check-verdict' }, check.passed ? 'Passed' : 'FAILED'),
    h('span', {}, `${titleCase(check.kind)} — expected ${expected}, measured ${measured}`
      + (check.tolerance != null ? ` (tolerance ${(check.tolerance * 100).toFixed(1)} %)` : '')),
    check.locator ? h('div', { class: 'source-meta' }, check.locator) : null,
    h('div', { class: 'source-meta' }, (check.sources || []).map(sourceTitle).join('; ')),
  ]);
}

function factsFor(feature) {
  const t = mapstyle.typeStyle(feature.feature_type);
  const level = levelById(feature.level_id);
  const r = mapstyle.representationStyle(feature.representation);
  const s = featureStatus(feature);
  const rows = [
    ['Feature', feature.name],
    ['Type', `${t.label} (${titleCase(feature.feature_type)})`],
    ['Level', level ? `${level.name} — ${mapstyle.LEVEL_KIND_LABEL[level.kind] || level.kind}` : feature.level_id],
    ['Depth', feature.depth_m ? quantityText(feature.depth_m)
      : (level && level.depth_m ? `${quantityText(level.depth_m)} (level)` : 'At the surface')],
    ['Representation', `${r.label} — ${r.hint}`],
    ['Positional accuracy', feature.accuracy_m != null ? `± ${feature.accuracy_m} m`
      : 'not applicable — an inferred bearing, not a structure'],
    ['Status in ' + whenLabel(), s.timeless ? 'Context feature — drawn in every year'
      : (s.status ? mapstyle.statusStyle(s.status).label : 'Not present in this year')],
    ['Method', feature.method],
    ['Measured', [
      feature.measured && feature.measured.length_m != null ? `length/perimeter ${feature.measured.length_m} m` : null,
      feature.measured && feature.measured.area_m2 != null ? `area ${feature.measured.area_m2} m²` : null,
    ].filter(Boolean).join(' · ')],
  ];
  const dl = h('dl', { class: 'kv-list' });
  for (const [k, v] of rows) {
    if (v == null || v === '') continue;
    dl.append(h('dt', {}, k), h('dd', {}, v));
  }

  const nodes = [h('h3', {}, 'Shape facts'), dl];
  if (feature.representation === 'inferred_direction') {
    const clipped = clippedGeometry(feature);
    nodes.push(h('p', { class: 'map-inferred-warning' },
      'This line is an inferred direction — not a structure. Nothing is built along it; '
      + 'it is the great-circle bearing towards the far site.'
      + (clipped
        ? ` It is drawn cut off at the edge of this map: the bearing continues for ${
          clipped.fullLength_m ? formatDistance(clipped.fullLength_m) : 'the full baseline'
        }, which no campus map can show at this scale.`
        : ' It is clipped to the map extent.')));
  }
  nodes.push(h('h3', {}, 'Cross-checks'));
  nodes.push((feature.checks || []).length
    ? h('ul', { class: 'map-check-list' }, feature.checks.map(checkRow))
    : h('p', { class: 'empty-note' },
      'No independent cross-check was possible for this shape, so its confidence is not raised by one.'));

  nodes.push(h('h3', {}, 'Sources'));
  const prov = feature.provenance || {};
  const sourceItems = (prov.sources || []).map((sid) => {
    const row = (bundle.source_titles || {})[sid] || {};
    return h('li', {}, [
      row.url
        ? h('a', { href: row.url, target: '_blank', rel: 'noopener' }, row.title || sid)
        : h('span', {}, row.title || sid),
      row.source_type ? h('div', { class: 'source-meta' }, titleCase(row.source_type)) : null,
    ]);
  });
  nodes.push(sourceItems.length
    ? h('ul', { class: 'source-list' }, sourceItems)
    : h('p', { class: 'empty-note' }, 'No source recorded for this shape.'));
  const provMeta = [
    prov.confidence ? `Confidence: ${titleCase(prov.confidence)}` : null,
    prov.verified_at ? `Verified ${prov.verified_at}` : null,
    prov.locator ? `Locator: ${prov.locator}` : null,
    prov.quote ? `“${prov.quote}”` : null,
    prov.note || null,
  ].filter(Boolean);
  if (provMeta.length) nodes.push(h('p', { class: 'source-meta' }, provMeta.join(' · ')));

  nodes.push(h('h3', {}, 'Licence'));
  nodes.push(feature.license
    ? h('p', { class: 'source-meta' }, [
      `${feature.license.name} — ${feature.license.attribution}`,
      feature.license.url ? ' ' : null,
      feature.license.url ? h('a', { href: feature.license.url, target: '_blank', rel: 'noopener' }, 'licence terms') : null,
    ])
    : h('p', { class: 'source-meta' },
      'No third-party licence: this shape is the atlas’s own derivation from published numbers.'));
  return h('section', { class: 'map-facts' }, nodes);
}

/** The notice §4's honesty rule needs: the shape is on screen only because
 *  it is selected, it is not what the map shows for this year, and here are
 *  the years in which it was. `variant` only changes the class. */
function timelineGapNotice(gap, variant) {
  const name = gap.features[0] ? (gap.features[0].entity_name || gap.features[0].name) : view.sel;
  const when = whenLabel();
  const span = gap.from != null && gap.to != null
    ? (gap.from === gap.to ? `${gap.from}` : `${gap.from}\u2013${gap.to}`)
    : null;
  const lead = {
    ended: span ? `${name} was there in ${span}, not in ${when}.` : `${name} is no longer there in ${when}.`,
    not_yet: span ? `${name} is recorded for ${span}, not yet in ${when}.` : `${name} does not exist yet in ${when}.`,
    gap: span ? `${name} has no recorded state in ${when}; its shapes cover ${span}.` : `${name} has no recorded state in ${when}.`,
    no_history: `${name} carries no recorded history, so no year can place it.`,
  }[gap.reason] || `${name} is not present in ${when}.`;
  const box = h('div', { class: `map-gap-notice ${variant || ''}`.trim(), role: 'status' }, [
    h('p', {}, `${lead} It is drawn ghosted because you selected it \u2014 it is not what this map `
      + `shows for ${when}.`),
  ]);
  if (span && gap.from != null) {
    const btn = h('button', { type: 'button', class: 'text-btn map-gap-btn' },
      gap.from === gap.to ? `Show ${gap.from}` : `Show ${gap.from}\u2013${gap.to}`);
    btn.addEventListener('click', () => {
      if (gap.from === gap.to) NAVIGATE({ year: gap.from, range: null });
      else NAVIGATE({ year: null, range: [gap.from, gap.to] });
    });
    box.appendChild(btn);
  }
  return box;
}

function renderSelectionNotice() {
  const existing = dom.stage.querySelector('.map-gap-notice');
  if (existing) existing.remove();
  const gap = selectionTimelineGap();
  if (!gap) return;
  dom.stage.appendChild(timelineGapNotice(gap, 'on-stage'));
}

/**
 * When nothing at all is drawn, say so on the map itself, with the one click
 * that fixes it. A blank dark map with the explanation in the sidebar reads as
 * "there is nothing here" — a claim the atlas cannot make: the map is empty
 * because of the timeline or the level toggles, not because the laboratory is.
 */
function renderEmptyNotice() {
  const existing = dom.stage.querySelector('.map-empty-notice');
  if (existing) existing.remove();
  if (!bundle || !bundle.features.length || layersByFeature.size) return;
  const onVisibleLevels = bundle.features.filter((f) => visibleLevelIds().includes(f.level_id));
  const nodes = [];
  let action;
  if (!onVisibleLevels.length) {
    nodes.push(
      h('p', { class: 'map-empty-title' }, 'Every level is switched off, so nothing is drawn.'),
      h('p', {}, `This map has ${bundle.features.length} feature${bundle.features.length === 1 ? '' : 's'}; `
        + 'switching levels off only hides them.'),
    );
    action = h('button', { type: 'button', class: 'map-empty-btn' }, 'Show all levels');
    action.addEventListener('click', () => NAVIGATE({ levels: null }));
  } else {
    let first = Infinity;
    let last = -Infinity;
    for (const feature of onVisibleLevels) {
      const segments = feature.state_segments;
      if (!segments || !segments.length) continue;
      first = Math.min(first, segments[0][0]);
      last = Math.max(last, segments[segments.length - 1][1]);
    }
    const span = Number.isFinite(first)
      ? (monthToYear(first) === monthToYear(last)
        ? `${monthToYear(first)}` : `${monthToYear(first)}\u2013${monthToYear(last)}`)
      : null;
    const n = onVisibleLevels.length;
    nodes.push(
      h('p', { class: 'map-empty-title' }, `Nothing on this map is present in ${whenLabel()}.`),
      h('p', {}, `${n === 1 ? 'Its one feature belongs' : `Its ${n} features belong`} to other years`
        + `${span ? ` (${span})` : ''}. The timeline is hiding ${n === 1 ? 'it' : 'them'}: `
        + 'that is a filter, not a statement about the laboratory.'),
    );
    action = h('button', { type: 'button', class: 'map-empty-btn', id: 'map-empty-all-years' },
      'Show features from all years');
    action.addEventListener('click', () => {
      showOutside = true;
      redraw();
      const toggle = document.getElementById('map-outside-toggle');
      if (toggle) toggle.focus({ preventScroll: true });
    });
  }
  nodes.push(action);
  dom.stage.appendChild(h('div', { class: 'map-empty-notice', role: 'status' }, nodes));
}

function renderDrawer() {
  const { drawer, drawerHead, drawerFacts, root } = dom;
  const features = selectedFeatures();
  const open = !!view.sel;
  root.classList.toggle('drawer-open', open);
  drawer.classList.toggle('hidden', !open);
  drawerHead.innerHTML = '';
  drawerFacts.innerHTML = '';
  if (!open) {
    lastAnnouncedSel = null;
    return;
  }
  const primary = features[0] || null;
  const name = (primary && (primary.entity_name || primary.name)) || view.sel;
  const closeBtn = h('button', {
    type: 'button', class: 'close-btn', id: 'map-drawer-close', 'aria-label': 'Close the selection drawer',
  }, '×');
  closeBtn.addEventListener('click', clearSelection);
  drawerHead.append(closeBtn, h('h2', { class: 'map-drawer-title', id: 'map-drawer-title', tabindex: '-1' }, name));
  // Directly under the title, not below the entity's panel: "why is this not
  // on the map" has to be answered before the reader starts scrolling.
  const gap = selectionTimelineGap();
  if (gap) drawerHead.appendChild(timelineGapNotice(gap, 'in-drawer'));
  if (primary && primary.entity_type) {
    const record = INDEX ? INDEX.get(view.sel) : null;
    const resolved = record && record.state_segments
      ? statusForTimeline(record.state_segments, view.timelineState) : null;
    drawerHead.appendChild(h('p', { class: 'map-subtitle' }, [
      titleCase(primary.entity_type),
      record && record.kind ? ` · ${kindLabel(record.kind)}` : '',
      resolved ? ` · ${mapstyle.statusStyle(resolved.status).label} in ${whenLabel()}` : '',
    ].join('')));
  }
  if (!primary) {
    drawerFacts.appendChild(h('p', { class: 'empty-note' },
      `Nothing on this map depicts ${view.sel}.`));
  } else {
    for (const feature of features) drawerFacts.appendChild(factsFor(feature));
  }
  const live = document.getElementById('map-selection-live');
  lastAnnouncedSel = `Selected ${name}.`;
  if (live) live.textContent = lastAnnouncedSel;
}

// ---------------------------------------------------------- depth diagram

function renderDepth() {
  const { depth } = dom;
  depth.innerHTML = '';
  depth.classList.toggle('hidden', !depthOpen);
  if (!depthOpen) return;
  const bars = [];
  for (const level of mapMeta.levels || []) {
    const d = level.depth_m;
    const value = d ? (d.value != null ? d.value : ((d.min || 0) + (d.max || 0)) / 2) : 0;
    bars.push({ label: level.name, depth: value, kind: 'level', display: d ? quantityText(d) : 'surface (0 m)' });
  }
  for (const feature of bundle.features) {
    if (!feature.depth_m) continue;
    const d = feature.depth_m;
    const value = d.value != null ? d.value : ((d.min || 0) + (d.max || 0)) / 2;
    bars.push({ label: feature.name, depth: value, kind: 'feature', display: quantityText(d) });
  }
  const maxDepth = Math.max(10, ...bars.map((b) => b.depth)) * 1.15;
  const W = 300;
  const H = 240;
  const top = 26;
  const left = 54;
  const plotH = H - top - 26;
  const svgNS = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(svgNS, 'svg');
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  svg.setAttribute('class', 'map-depth-svg');
  svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label',
    `Vertical section: depth below the surface in metres, ${bars.length} bars, deepest ${Math.round(Math.max(0, ...bars.map((b) => b.depth)))} metres.`);
  const mk = (tag, attrs, text) => {
    const node = document.createElementNS(svgNS, tag);
    for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
    if (text != null) node.textContent = text;
    return node;
  };
  svg.appendChild(mk('text', { x: 4, y: 14, class: 'map-depth-axis-label' }, 'Depth below surface (m)'));
  // vertical metres axis
  svg.appendChild(mk('line', { x1: left, y1: top, x2: left, y2: top + plotH, class: 'map-depth-axis' }));
  const ticks = 4;
  for (let i = 0; i <= ticks; i += 1) {
    const value = (maxDepth * i) / ticks;
    const y = top + (plotH * i) / ticks;
    svg.appendChild(mk('line', { x1: left - 4, y1: y, x2: left, y2: y, class: 'map-depth-axis' }));
    svg.appendChild(mk('text', { x: left - 7, y: y + 4, 'text-anchor': 'end', class: 'map-depth-tick' },
      `${Math.round(value)}`));
  }
  const slot = bars.length ? (W - left - 12) / bars.length : 0;
  bars.forEach((bar, i) => {
    const x = left + 4 + i * slot;
    const y = top + (plotH * bar.depth) / maxDepth;
    svg.appendChild(mk('rect', {
      x, y: top, width: Math.max(6, slot - 8), height: Math.max(1, y - top),
      class: `map-depth-bar is-${bar.kind}`,
    }));
    svg.appendChild(mk('line', {
      x1: x, y1: y, x2: x + Math.max(6, slot - 8), y2: y, class: 'map-depth-floor',
    }));
  });
  depth.append(
    h('h3', {}, 'Depth and level diagram — vertical section, not a plan view'),
    h('p', { class: 'map-note' },
      'This diagram shows how far below the surface each level and each feature sits. '
      + 'It is a section through the campus; distances across the page carry no meaning.'),
    svg,
    h('ul', { class: 'map-depth-key' }, bars.map((bar) => h('li', {},
      `${bar.label} — ${bar.display}`))),
  );
  const close = h('button', { type: 'button', class: 'text-btn' }, 'Close the depth diagram');
  close.addEventListener('click', () => {
    depthOpen = false;
    renderDepth();
    renderSidebar();
    const btn = document.getElementById('map-depth-toggle');
    if (btn) btn.focus({ preventScroll: true });
  });
  depth.appendChild(close);
}

// ------------------------------------------------------------ stage chrome

/** At a pole every direction is north, so the arrow cannot mean true north.
 *  It means grid north: the 0° meridian, which is the convention used at
 *  Amundsen–Scott and the +Y axis of this map's projection. */
function renderNorthIndicator() {
  const arrow = dom.stage.querySelector('.map-north-arrow');
  const label = dom.stage.querySelector('.map-north-label');
  const box = dom.stage.querySelector('.map-north');
  if (!arrow || !label || !box) return;
  if (polarProjection) {
    label.textContent = 'grid north (0° meridian)';
    box.classList.add('is-grid-north');
    box.setAttribute('role', 'note');
    box.setAttribute('aria-label',
      'Up on this map is grid north: the 0° meridian. True north is not a direction here — '
      + 'every direction from the pole is north.');
  } else {
    label.textContent = 'N';
    box.classList.remove('is-grid-north');
    box.setAttribute('role', 'note');
    box.setAttribute('aria-label', 'Up on this map is true north.');
  }
}

function redraw() {
  const L = window.L;
  drawFeatures(L);
  refreshFrame();
  layoutLabels();
  renderSidebar();
  renderDepth();
  renderSelectionNotice();
  renderEmptyNotice();
}

// ------------------------------------------------------------------ show

function renderMessage(nodes) {
  ensureDom();
  dom.layers.innerHTML = '';
  const back = h('button', { type: 'button', class: 'map-back-btn', id: 'map-back' }, '← Back to globe');
  back.addEventListener('click', () => NAVIGATE({ entity: null, sel: null, levels: null, basemap: true }));
  dom.layers.append(back, ...nodes);
  dom.drawer.classList.add('hidden');
  dom.root.classList.remove('drawer-open');
}

/**
 * Render the map route. `ctx` carries what app.js already owns: the atlas
 * tables, the navigate function, the panels module (whose container app.js
 * has already pointed at this view's drawer), the current timeline selection
 * and the loader's resolved base path.
 */
export async function show(current, ctx) {
  if (ATLAS !== ctx.atlas) detectorSiteIds = null;
  ATLAS = ctx.atlas;
  INDEX = ctx.index;
  NAVIGATE = ctx.navigate;
  PANELS = ctx.panels;
  ensureDom();
  opened = true;
  dom.root.classList.remove('hidden');

  const mapId = `map:${current.entity.slug}`;
  const meta = (ATLAS.maps || {})[mapId];
  if (!meta) {
    destroyMap();
    currentMapId = null;
    renderMessage([
      h('h2', { class: 'map-title', tabindex: '-1' }, 'No such local map'),
      h('p', { class: 'error-note', role: 'alert' },
        `This data build has no map ${mapId}. That means no local map has been researched and `
        + 'published for it yet — not that the facility has no layout.'),
    ]);
    return;
  }

  view = {
    levels: current.levels === undefined ? null : current.levels,
    basemap: current.basemap !== false,
    sel: current.sel || null,
    timelineState: ctx.timelineState,
  };

  if (mapId !== currentMapId) {
    destroyMap();
    currentMapId = mapId;
    mapMeta = meta;
    bundle = null;
    renderMessage([
      h('h2', { class: 'map-title', tabindex: '-1' }, meta.name),
      h('p', { class: 'loading-note', role: 'status' }, 'Loading the local map…'),
    ]);
    let L;
    try {
      [L, bundle] = await Promise.all([loadLeaflet(), fetchBundle(ctx.loaderBase, meta.bundle)]);
      labelTexts = mapstyle.labelsFor(bundle.features, { isExperimentSite });
      createMap(L);
    } catch (error) {
      currentMapId = null;
      // §"Correctness rules": an upstream failure is an error, never an
      // empty map. An empty campus would read as "there is nothing here".
      renderMessage([
        h('h2', { class: 'map-title', tabindex: '-1' }, meta.name),
        h('p', { class: 'error-note', role: 'alert' },
          `The local map for ${meta.name} could not be loaded: ${error.message}. `
          + 'Nothing is drawn, because a blank map would look like a laboratory with no '
          + 'structures rather than a failed request.'),
        (() => {
          const retry = h('button', { type: 'button', class: 'text-btn' }, 'Retry');
          retry.addEventListener('click', () => { currentMapId = null; show(current, ctx); });
          return retry;
        })(),
      ]);
      destroyMap();
      currentMapId = null;
      renderMessage([
        h('h2', { class: 'map-title', tabindex: '-1' }, meta.name),
        h('p', { class: 'error-note', role: 'alert' },
          `The local map for ${meta.name} could not be opened: ${error.message}. `
          + 'Nothing is drawn, because a blank map would look like a laboratory with no '
          + 'structures rather than a failed request.'),
        (() => {
          const retry = h('button', { type: 'button', class: 'text-btn' }, 'Retry');
          retry.addEventListener('click', () => { currentMapId = null; show(current, ctx); });
          return retry;
        })(),
      ]);
      return;
    }
  }

  mapMeta = meta;
  const L = window.L;
  try {
    drawFeatures(L);
    // Frame before the basemap is added, so tiles are requested once, for the
    // view the reader will see, and not for a first guess at it.
    refreshFrame();
    applyBasemap(L);
    layoutLabels();
  } catch (error) {
    window.console.error('HEP Atlas local map: could not draw', error);
    renderMessage([
      h('h2', { class: 'map-title', tabindex: '-1' }, meta.name),
      h('p', { class: 'error-note', role: 'alert' },
        `The local map for ${meta.name} could not be drawn: ${error.message}.`),
    ]);
    return;
  }
  renderSidebar();
  renderNorthIndicator();
  renderDepth();
  renderDrawer();
  renderSelectionNotice();
  renderEmptyNotice();

  // The selected entity's normal detail panel, rendered by panels.js into
  // the drawer (app.js has already pointed panels at drawerPanelEl()).
  if (view.sel) {
    const route = idRoute(view.sel);
    if (route.type === 'geometry') {
      dom.drawerPanel.innerHTML = '';
      dom.drawerPanel.appendChild(h('p', { class: 'empty-note' },
        'This is a context feature: it depicts no atlas entity, so it has no record of its own.'));
    } else {
      await PANELS.render(route, view.timelineState);
    }
    const title = document.getElementById('map-drawer-title');
    if (title && !dom.drawer.contains(document.activeElement)) title.focus({ preventScroll: true });
  } else {
    dom.drawerPanel.innerHTML = '';
  }

  // Leaflet sizes itself from the container, which was display:none until
  // the map route's layout class landed on #atlas-main — so the map was very
  // likely built against a 0 × 0 box, where framing collapses to zoom 0 (the
  // whole world). Measure again on the next frame and, if the opening view
  // was never framed, frame it now.
  if (mapInstance) {
    window.requestAnimationFrame(() => {
      if (!mapInstance) return;
      mapInstance.invalidateSize({ animate: false });
      refreshFrame();
      layoutLabels();
    });
  }
}

export function hide() {
  if (!dom) { opened = false; return; }
  opened = false;
  depthOpen = false;
  destroyMap();
  currentMapId = null;
  bundle = null;
  dom.root.classList.add('hidden');
  dom.layers.innerHTML = '';
  dom.drawerHead.innerHTML = '';
  dom.drawerFacts.innerHTML = '';
  dom.drawerPanel.innerHTML = '';
}

// ------------------------------------------------------------ Escape (§23)
// Capture phase on `document`, so this runs before app.js's own Escape
// handler and can stop the event reaching it when the map view owns the key.
// "Closest overlay first": the depth diagram, then the drawer, and only then
// does app.js get to close the map route itself and return to the globe.
document.addEventListener('keydown', (event) => {
  if (event.key !== 'Escape' || !opened) return;
  if (depthOpen) {
    event.stopPropagation();
    depthOpen = false;
    renderDepth();
    renderSidebar();
    const btn = document.getElementById('map-depth-toggle');
    if (btn) btn.focus({ preventScroll: true });
    return;
  }
  if (view.sel) {
    event.stopPropagation();
    clearSelection();
  }
}, true);
