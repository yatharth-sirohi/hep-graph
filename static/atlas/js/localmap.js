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
  titleCase, quantityText, statusForTimeline, timelineAbsenceReason,
} from './model.js';
import * as mapstyle from './mapstyle.js';

const LEAFLET_JS = '/atlas/vendor/leaflet/leaflet.js';
const LEAFLET_CSS = '/atlas/vendor/leaflet/leaflet.css';
const TILE_URL = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
const TILE_ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors';
const EARTH_R = 6371008.8;

let ATLAS = null;
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
let view = { levels: null, basemap: true, sel: null, timelineState: { year: null } };
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
  const north = h('div', { class: 'map-north', 'aria-hidden': 'true' }, [
    h('span', { class: 'map-north-arrow' }, '↑'),
    h('span', { class: 'map-north-label' }, 'N'),
  ]);
  const tileNotice = h('p', { class: 'map-tile-notice hidden', id: 'map-tile-notice', role: 'status' });
  const stageControls = h('div', { class: 'map-stage-controls' });
  const depth = h('div', {
    class: 'map-depth hidden', id: 'map-depth', role: 'region',
    'aria-label': 'Depth and level diagram (vertical section)',
  });
  const status = h('div', { class: 'map-status', id: 'map-status', role: 'status' });
  stage.append(canvas, north, tileNotice, stageControls, depth, status);

  const drawer = h('aside', {
    class: 'map-drawer', id: 'map-drawer', 'aria-label': 'Selected feature',
  });
  const drawerHead = h('div', { class: 'map-drawer-head' });
  const drawerPanel = h('div', { class: 'map-drawer-panel', id: 'map-drawer-panel' });
  const drawerFacts = h('div', { class: 'map-drawer-facts', id: 'map-drawer-facts' });
  drawer.append(drawerHead, drawerPanel, drawerFacts);

  root.append(layers, stage, drawer);
  host.appendChild(root);
  dom = { root, layers, stage, canvas, tileNotice, stageControls, depth, drawer, drawerHead, drawerPanel, drawerFacts, status };
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

function featureVisible(feature) {
  if (!visibleLevelIds().includes(feature.level_id)) return false;
  if (inSelectedYear(feature)) return true;
  return showOutside;
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
  if (window.__hepAtlasLocalMap) delete window.__hepAtlasLocalMap;
  tileLayer = null;
  featureGroup = null;
  layersByFeature = new Map();
}

function createMap(L) {
  const { lat, lon } = mapMeta.center;
  mapInstance = L.map(dom.canvas, {
    center: [lat, lon],
    zoom: 14,
    zoomControl: true,
    keyboard: true,
    attributionControl: true,
    preferCanvas: false,
  });
  L.control.scale({ imperial: false, metric: true, position: 'bottomleft' }).addTo(mapInstance);
  // Fit the map to the extent the map record declares, so what opens is the
  // campus the record describes rather than an arbitrary zoom.
  const half = mapMeta.extent_m || 3000;
  const sw = destination(lat, lon, 225, half * Math.SQRT2);
  const ne = destination(lat, lon, 45, half * Math.SQRT2);
  mapInstance.fitBounds([sw, ne]);
  featureGroup = L.layerGroup().addTo(mapInstance);
  // A test/debug handle: the browser suite reads the scale control's label
  // and pixel width and checks it against map.distance() at the view centre.
  window.__hepAtlasLocalMap = mapInstance;
}

function applyBasemap(L) {
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

function lineCoords(geometry) {
  if (geometry.type === 'LineString') return geometry.coordinates;
  if (geometry.type === 'MultiLineString') return geometry.coordinates[geometry.coordinates.length - 1];
  return null;
}

function drawFeatures(L) {
  featureGroup.clearLayers();
  layersByFeature = new Map();
  for (const feature of bundle.features) {
    if (!featureVisible(feature)) continue;
    const level = levelById(feature.level_id);
    const s = featureStatus(feature);
    const ghost = !s.timeless && !s.status;
    const options = mapstyle.pathOptions(feature, { level, status: s.status, ghost });
    const parts = [];
    if (mapstyle.levelIsSubsurface(level)) {
      parts.push(L.geoJSON(feature.geometry, { style: () => mapstyle.casingOptions(feature, { ghost }) }));
    }
    const main = L.geoJSON(feature.geometry, { style: () => options });
    parts.push(main);
    const t = mapstyle.typeStyle(feature.feature_type);
    const coords = t.arrow ? lineCoords(feature.geometry) : null;
    if (coords && coords.length >= 2) {
      const head = arrowheadCoords(coords);
      if (head) parts.push(L.polyline(head, { ...options, fill: false, fillOpacity: 0, dashArray: null }));
    }
    const group = L.featureGroup(parts);
    const tooltip = tooltipFor(feature);
    group.bindTooltip(tooltip, { sticky: true, className: 'map-tooltip' });
    if (ghost) group.getLayers().forEach((l) => l.getElement && l.getElement());
    group.on('click', () => selectFrom(feature, null));
    group.addTo(featureGroup);
    const el = main.getLayers()[0] && main.getLayers()[0].getElement && main.getLayers()[0].getElement();
    if (el) {
      el.setAttribute('data-geometry-id', feature.id);
      el.setAttribute('data-representation', feature.representation);
      if (ghost) el.classList.add('is-ghosted');
    }
    layersByFeature.set(feature.id, group);
  }
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
  const btn = h('button', {
    type: 'button',
    class: `map-toggle ${extraClass || ''}`.trim(),
    'aria-pressed': pressed ? 'true' : 'false',
  }, label);
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
  ]);
  btn.addEventListener('click', () => selectFrom(feature, btn));
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

function renderUnlocated() {
  const rows = (bundle.map.unlocated || []).map((row) => h('li', { class: 'map-unlocated-row' }, [
    h('div', { class: 'map-unlocated-name' },
      row.entity_id ? [
        h('a', {
          href: `#/${idRoute(row.entity_id).type}/${idRoute(row.entity_id).slug}`,
          class: 'entity-link',
          onclick: (event) => { event.preventDefault(); NAVIGATE({ entity: idRoute(row.entity_id) }); },
        }, row.entity_name || row.entity_id),
        row.entity_type ? h('span', { class: 'map-feature-meta' }, ` · ${titleCase(row.entity_type)}`) : null,
      ] : (row.entity_name || 'Unnamed')),
    h('p', { class: 'map-unlocated-reason' }, row.reason),
    row.backlog ? h('p', { class: 'map-unlocated-backlog' }, `To do: ${row.backlog}`) : null,
    h('p', { class: 'source-meta' },
      (row.sources || []).map((sid) => sourceTitle(sid)).join('; ') || 'No source recorded.'),
  ]));
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
      return h('li', {}, [
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
    h('ul', { class: 'map-schematic-list' }, items.map((s) => h('li', {}, [
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

  const back = h('button', { type: 'button', class: 'map-back-btn', id: 'map-back' }, '← Back to globe');
  back.addEventListener('click', () => NAVIGATE({ entity: null, sel: null, levels: null, basemap: true }));
  layers.appendChild(back);

  layers.appendChild(h('h2', { class: 'map-title', id: 'map-title', tabindex: '-1' }, mapMeta.name));
  const facility = (ATLAS.facilities || {})[mapMeta.facility_id];
  layers.appendChild(h('p', { class: 'map-subtitle' }, [
    `${mapMeta.to_scale_count} feature${mapMeta.to_scale_count === 1 ? '' : 's'} drawn to scale`,
    mapMeta.unlocated_count
      ? ` · ${mapMeta.unlocated_count} not verified`
      : '',
    facility ? ' · ' : '',
  ]));
  if (facility) {
    const facLink = h('a', {
      href: `#/facility/${facility.id.split(':')[1]}`, class: 'entity-link',
      onclick: (event) => { event.preventDefault(); NAVIGATE({ entity: idRoute(facility.id), sel: null, levels: null }); },
    }, `Open the ${facility.name} record`);
    layers.appendChild(h('p', { class: 'map-subtitle' }, facLink));
  }
  for (const note of (bundle.map.notes || [])) {
    layers.appendChild(h('p', { class: 'map-data-note', role: 'note' }, note));
  }

  layers.appendChild(h('p', { class: 'visually-hidden', id: 'map-selection-live', role: 'status', 'aria-live': 'polite' },
    lastAnnouncedSel || ''));

  // ---- view controls
  const basemapBtn = toggleButton('OpenStreetMap basemap', view.basemap, () => {
    NAVIGATE({ basemap: !view.basemap });
  }, 'map-basemap-toggle');
  basemapBtn.id = 'map-basemap-toggle';
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
  layers.appendChild(panelSection('View', [basemapBtn, outsideBtn, depthBtn]));

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
      .filter((f) => showOutside || inSelectedYear(f));
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
  layers.appendChild(panelSection('Legend', renderLegend(), { open: false }));

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
    nodes.push(h('p', { class: 'map-inferred-warning' },
      'This line is an inferred direction — not a structure. Nothing is built along it; '
      + 'it is the great-circle bearing towards the far site, clipped to the map extent.'));
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

function renderStageControls() {
  dom.stageControls.innerHTML = '';
  const back = h('button', { type: 'button', class: 'map-stage-btn', id: 'map-back-stage' }, '← Back to globe');
  back.addEventListener('click', () => NAVIGATE({ entity: null, sel: null, levels: null, basemap: true }));
  dom.stageControls.appendChild(back);
}

function redraw() {
  const L = window.L;
  drawFeatures(L);
  renderSidebar();
  renderDepth();
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
  ATLAS = ctx.atlas;
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
      return;
    }
    createMap(L);
    renderStageControls();
  }

  mapMeta = meta;
  const L = window.L;
  applyBasemap(L);
  drawFeatures(L);
  renderSidebar();
  renderDepth();
  renderDrawer();

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
  // the map route's layout class landed on #atlas-main.
  if (mapInstance) window.requestAnimationFrame(() => mapInstance.invalidateSize());
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
