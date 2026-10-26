// localmap-compare.js — "Compare with…" on a local map: another facility's footprint
// laid over this map at true scale, centred on the map's view (or, when the reader
// asks, on their own location). Loaded by localmap.js the first time a map is opened,
// never on the globe.
//
// WHAT IT DRAWS   the rings, outlines and arrays of the other facility's geometry
//                 records (views/scale-geometry.js says which), each vertex moved by
//                 its distance and bearing from the footprint's centre — a translation
//                 on the sphere, so the shape keeps its true size. It is labelled an
//                 overlay, never styled like a feature of the host map, and it takes no
//                 clicks.
// THE URL         `?cmp=<facility-slug>` and `?cmpc=<lat>,<lon>` (the map point it is
//                 centred on, rounded to ~11 m). A link restores the overlay; it can
//                 never carry the reader's position: see below.
// LOCATION        Only a click on "Over my location" asks the browser for a position.
//                 It is held in this module's memory for the visit — not stored in the
//                 address, history, local storage or anywhere else, and sent nowhere. The
//                 OpenStreetMap basemap would tell its tile server roughly where the map
//                 is, so while the overlay sits over the reader the basemap is off unless
//                 the reader turns it on, and the panel says so.

import { placeFootprint } from './views/scale-geometry.js';

const h = (tag, attrs = {}, children = []) => {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (k === 'class') el.className = v;
    else if (k === 'text') el.textContent = v;
    else if (v !== null && v !== undefined) el.setAttribute(k, v);
  }
  for (const child of [].concat(children)) {
    if (child == null) continue;
    el.appendChild((typeof child === 'string' || typeof child === 'number') ? document.createTextNode(String(child)) : child);
  }
  return el;
};

const OVERLAY_DASH = '12 7';
const MAX_LISTED = 8;

function freshState() {
  return {
    mapId: null, // the host map this state belongs to
    slug: null, // the facility being compared
    key: null, // slug + anchor of the overlay that is drawn
    layer: null,
    placed: null,
    sourceMeta: null,
    anchor: null, // [lat, lon] the overlay is centred on (never persisted)
    anchorKind: null, // 'view' | 'record' | 'location'
    mode: 'view', // 'location' while the overlay sits over the reader
    location: null, // [lat, lon], this visit's memory only
    allowTiles: false, // the reader opted in to the basemap while over their location
    baseHidden: false, // whether the basemap was last applied as hidden
    loading: false,
    error: null,
    status: '', // a polite message ("asking your browser…")
    announce: '',
    focus: null,
    serial: 0,
  };
}

let api = null;
let st = freshState();

// -------------------------------------------------------------------- helpers
function metres(m) {
  if (m >= 10000) return `${(m / 1000).toFixed(0)} km`;
  if (m >= 1000) return `${(m / 1000).toFixed(m >= 100000 ? 0 : 2).replace(/\.?0+$/, '')} km`;
  return `${Math.round(m)} m`;
}

function squareMetres(m2) {
  if (m2 >= 1e6) return `${(m2 / 1e6).toFixed(m2 >= 1e8 ? 0 : 2)} km²`;
  return `${Math.round(m2).toLocaleString('en-US')} m²`;
}

const degreesText = (lat, lon) => `${Math.abs(lat).toFixed(4)}°${lat < 0 ? 'S' : 'N'}, ${Math.abs(lon).toFixed(4)}°${lon < 0 ? 'W' : 'E'}`;
const round4 = (x) => Math.round(x * 1e4) / 1e4;

function facilityOf(slug) {
  return (api && api.atlas.facilities || {})[`facility:${slug}`] || null;
}

function mapOf(facility) {
  return facility && facility.map_id ? (api.atlas.maps || {})[facility.map_id] || null : null;
}

/** The facilities a reader may compare with: every one with a local map, but this one. */
function candidates() {
  const own = api.mapMeta.facility_id;
  return Object.values(api.atlas.facilities || {})
    .filter((fac) => fac.id !== own && mapOf(fac))
    .sort((a, b) => a.name.localeCompare(b.name));
}

function removeLayer() {
  if (st.layer && api && api.map()) api.map().removeLayer(st.layer);
  st.layer = null;
  st.placed = null;
  st.key = null;
}

// ------------------------------------------------------------------- the layer
function buildLayer(L, placed, facility, anchor) {
  const group = L.layerGroup();
  for (const feature of placed.features) {
    const area = /Polygon/.test(feature.geometry.type);
    const options = {
      className: `map-cmp-shape ${area ? 'map-cmp-area' : 'map-cmp-line'}`,
      interactive: false,
      fill: area,
      fillOpacity: area ? 0.06 : 0,
      weight: area ? 2 : 3.5,
      dashArray: OVERLAY_DASH,
      lineCap: 'butt',
    };
    L.geoJSON(feature.geometry, { ...options, style: () => options }).addTo(group);
  }
  // The label sits at the top of the footprint, in a pane above the map's own labels.
  const map = api.map();
  if (!map.getPane('map-cmp-pane')) {
    const pane = map.createPane('map-cmp-pane');
    pane.style.zIndex = 660;
    pane.style.pointerEvents = 'none';
  }
  let top = null;
  for (const feature of placed.features) {
    const walk = (c) => {
      if (typeof c[0] === 'number') {
        const projected = map.project(L.latLng(c[1], c[0]), 0);
        if (Number.isFinite(projected.y) && (top === null || projected.y < top.y)) top = { y: projected.y, at: [c[1], c[0]] };
      } else {
        c.forEach(walk);
      }
    };
    walk(feature.geometry.coordinates);
  }
  const text = st.mode === 'location'
    ? `${facility.name}: overlay over your location`
    : `${facility.name}: overlay at true scale`;
  const escaped = text.replace(/[&<>"]/g, (c) => `&#${c.charCodeAt(0)};`);
  L.marker(anchor, {
    interactive: false,
    keyboard: false,
    pane: 'map-cmp-pane',
    icon: L.divIcon({
      className: 'map-cmp-anchor',
      html: '<span class="map-cmp-cross" aria-hidden="true"></span>',
      iconSize: [0, 0],
    }),
  }).addTo(group);
  L.marker(top ? top.at : anchor, {
    interactive: false,
    keyboard: false,
    pane: 'map-cmp-pane',
    icon: L.divIcon({
      className: 'map-cmp-anchor',
      html: `<span class="map-cmp-label" aria-hidden="true">${escaped}</span>`,
      iconSize: [0, 0],
    }),
  }).addTo(group);
  return group;
}

// --------------------------------------------------------------------- syncing
/**
 * Make the drawn overlay match the address (`cmp`, `cmpc`). Called by localmap.js on
 * every show(); it does nothing when the overlay is already the one the address names.
 * `context`: { L, map(), atlas, mapId, mapMeta, polarHost, view, isPolar(centre),
 *              fetchBundle(path), navigate(patch), rerender(), reframe(), applyBasemap() }
 */
export async function sync(context) {
  try {
    await run(context);
  } finally {
    // The basemap follows the overlay's mode (see hidesBasemap): apply it when it changed.
    if (api && api.map() && st.baseHidden !== hidesBasemap()) {
      st.baseHidden = hidesBasemap();
      api.applyBasemap();
    }
  }
}

async function run(context) {
  api = context;
  const mapChanged = st.mapId !== api.mapId;
  if (mapChanged) {
    removeLayer();
    st = { ...freshState(), mapId: api.mapId, serial: st.serial };
  }
  const ticket = ++st.serial;
  const slug = api.view.cmp || null;

  if (!slug) {
    removeLayer();
    st.slug = null;
    st.error = null;
    st.loading = false;
    st.mode = 'view';
    st.location = null;
    st.allowTiles = false;
    st.status = '';
    return;
  }

  const facility = facilityOf(slug);
  const meta = mapOf(facility);
  st.slug = slug;
  if (!facility || !meta || facility.id === api.mapMeta.facility_id) {
    removeLayer();
    st.loading = false;
    st.error = !facility
      ? `The address names a facility “${slug}” that this data build does not have, so nothing is overlaid.`
      : (!meta
        ? `${facility.name} has no local map yet, so it has no footprint to overlay.`
        : 'A map cannot be compared with itself.');
    return;
  }
  // The overlay's anchor: the reader's location while that mode lasts, else the map
  // point the address names, else the host map's recorded centre.
  let anchor;
  let kind;
  if (st.mode === 'location' && st.location) {
    anchor = st.location;
    kind = 'location';
  } else {
    st.mode = 'view';
    st.location = null;
    anchor = api.view.cmpc || [api.mapMeta.center.lat, api.mapMeta.center.lon];
    kind = api.view.cmpc ? 'view' : 'record';
  }
  const key = `${slug}|${anchor[0].toFixed(5)},${anchor[1].toFixed(5)}`;
  if (key === st.key && st.layer) {
    st.anchorKind = kind;
    return;
  }
  st.loading = true;
  st.error = null;
  st.anchor = anchor;
  st.anchorKind = kind;
  let bundle;
  try {
    bundle = await api.fetchBundle(meta.bundle);
  } catch (error) {
    if (ticket !== st.serial) return;
    removeLayer();
    st.loading = false;
    st.error = `The footprint of ${facility.name} could not be loaded: ${error.message}. Nothing is overlaid, because a missing footprint must not look like a facility with no structures.`;
    api.rerender();
    return;
  }
  if (ticket !== st.serial || !api.map()) return;
  const placed = placeFootprint(
    bundle,
    { lat: anchor[0], lon: anchor[1], polar: api.polarHost },
    api.isPolar(meta.center),
  );
  removeLayer();
  st.loading = false;
  if (!placed) {
    st.error = `${facility.name}’s local map draws no ring, outline, array, hall or cavern with an extent (its structures are positions only), so there is no true-scale footprint to overlay.`;
    api.rerender();
    return;
  }
  st.sourceMeta = meta;
  st.placed = placed;
  st.key = key;
  st.layer = buildLayer(api.L, placed, facility, anchor).addTo(api.map());
  st.announce = `${facility.name}'s footprint is overlaid at true scale, ${metres(placed.centre.widthM)} by ${metres(placed.centre.heightM)}.`;
  api.reframe();
  api.rerender();
}

/** Remove the overlay from the address and the map. */
function remove() {
  st.focus = 'map-compare-select';
  api.navigate({ cmp: null, cmpc: null });
}

function choose(slug) {
  st.focus = 'map-compare-select';
  if (!slug) { remove(); return; }
  st.mode = 'view';
  st.location = null;
  st.allowTiles = false;
  const centre = api.map().getCenter();
  api.navigate({ cmp: slug, cmpc: [round4(centre.lat), round4(centre.lng)] });
}

function centreOnView() {
  st.focus = 'map-compare-centre';
  st.mode = 'view';
  st.location = null;
  st.allowTiles = false;
  const centre = api.map().getCenter();
  api.navigate({ cmp: api.view.cmp, cmpc: [round4(centre.lat), round4(centre.lng)] });
}

function overMyLocation() {
  st.focus = 'map-compare-locate';
  if (!api.view.cmp) {
    st.status = 'Choose a facility to compare first.';
    api.rerender();
    return;
  }
  if (!('geolocation' in navigator)) {
    st.status = 'This browser has no location service, so the overlay cannot be placed over you.';
    api.rerender();
    return;
  }
  st.status = 'Waiting for your browser to share your location…';
  api.rerender();
  navigator.geolocation.getCurrentPosition((position) => {
    if (!api || !api.map() || !api.view.cmp) return;
    // Held in memory only: not in the address (cmpc is cleared), not in storage, not sent.
    st.location = [position.coords.latitude, position.coords.longitude];
    st.mode = 'location';
    st.allowTiles = false;
    st.status = '';
    api.navigate({ cmp: api.view.cmp, cmpc: null });
  }, (error) => {
    st.status = error && error.code === 1
      ? 'Your browser did not share your location (permission was denied), so the overlay stays where it was.'
      : 'Your location could not be found, so the overlay stays where it was.';
    api.rerender();
  }, { enableHighAccuracy: false, maximumAge: 0, timeout: 20000 });
}

// -------------------------------------------------------- what localmap.js asks
/** [lon, lat] vertices the frame should include, and whether they replace the host's. */
export function framePoints() {
  if (!st.placed) return null;
  const points = st.placed.features.flatMap((f) => {
    const out = [];
    const walk = (c) => { if (typeof c[0] === 'number') out.push(c); else c.forEach(walk); };
    walk(f.geometry.coordinates);
    return out;
  });
  return { points, exclusive: st.mode === 'location' };
}

/** Changes when the overlay does, so an unmoved view is framed again. */
export function signature() {
  return st.key || '';
}

/** True while the overlay sits over the reader and they have not opted in to tiles. */
export function hidesBasemap() {
  return st.mode === 'location' && !st.allowTiles;
}

export function basemapNotice() {
  return 'Basemap off over your location, so no map tile request tells OpenStreetMap where you are. '
    + 'Turn it on under “Compare with…”.';
}

export function destroy() {
  if (st.layer && api && api.map()) api.map().removeLayer(st.layer);
  st = freshState();
  if (typeof window !== 'undefined' && window.__hepAtlasCompare) delete window.__hepAtlasCompare;
}

// ------------------------------------------------------------------- the panel
function featureRows(placed) {
  const rows = placed.features.slice().sort((a, b) => (b.lengthM || 0) - (a.lengthM || 0));
  const shown = rows.slice(0, MAX_LISTED).map((feature) => {
    const pieces = [];
    if (/Polygon/.test(feature.geometry.type)) {
      if (feature.areaM2) pieces.push(`${squareMetres(feature.areaM2)} enclosed`);
    } else if (feature.lengthM) {
      pieces.push(`${metres(feature.lengthM)} long`);
    }
    if (feature.officialLengthM) pieces.push(`official figure ${metres(feature.officialLengthM)}`);
    if (feature.accuracyM) pieces.push(`±${feature.accuracyM} m`);
    return h('li', {}, [h('strong', {}, feature.name), ` — ${feature.featureType.replace(/_/g, ' ')}${pieces.length ? `, ${pieces.join(', ')}` : ''}`]);
  });
  if (rows.length > MAX_LISTED) shown.push(h('li', {}, `and ${rows.length - MAX_LISTED} more shape${rows.length - MAX_LISTED === 1 ? '' : 's'} of its map`));
  return shown;
}

function methodBlock(facility, placed) {
  const src = placed.centre;
  const centreText = st.anchorKind === 'location'
    ? 'the reader’s location (not shown, not stored)'
    : degreesText(st.anchor[0], st.anchor[1]);
  return h('details', { class: 'map-cmp-method' }, [
    h('summary', {}, 'How the overlay is placed'),
    h('p', {}, [
      `Each vertex of ${facility.name}’s drawn shapes is described by its great-circle distance and initial bearing from the middle of the footprint's bounding box (${degreesText(src.lat, src.lon)}). `,
      `The overlay puts it at that same distance and bearing from ${centreText}. `,
    ]),
    h('p', {}, [
      'That is a translation on the sphere (R = 6371.0088 km), not a shift of latitude and longitude, which would squeeze a ring moved toward a pole. ',
      'Distances from the centre are kept exactly, and distances between two points change by less than 0.01 % for a footprint this size. ',
      'Bearings are from true north; on a map drawn in a polar projection, from the map’s grid north, so the overlay stands upright there.',
    ]),
    h('p', {}, [
      'The shapes are the geometry records of that facility’s own map, with the positional accuracy listed above; the footprint is not redrawn or simplified. ',
      'It ignores the timeline: a ring is shown whether or not it was operating in the selected year.',
    ]),
  ]);
}

function activeBlock() {
  const facility = facilityOf(api.view.cmp);
  const placed = st.placed;
  const meta = st.sourceMeta;
  const where = st.anchorKind === 'location'
    ? 'your location. Your position stays in this page: it is not stored, not sent anywhere and not in the link.'
    : (st.anchorKind === 'view'
      ? `the map point ${degreesText(st.anchor[0], st.anchor[1])}, where the view was centred when it was placed.`
      : 'this map’s recorded centre (the address names no other point).');
  const own = placed.centre;
  const children = [
    h('p', { class: 'map-cmp-title' }, [h('i', { class: 'map-swatch map-cmp-swatch', 'aria-hidden': 'true' }), `Overlay: ${facility.name}`]),
    h('p', { class: 'map-note' }, [
      'This is an overlay, not part of this map. ',
      `${facility.name}’s footprint is drawn at true scale, so any distance on it reads the same against this map’s scale bar.`,
    ]),
    h('p', { class: 'map-note' }, ['Centred on ', where]),
    h('p', { class: 'map-note' }, [
      h('strong', {}, 'Its own scale: '),
      `it spans ${metres(own.widthM)} east–west by ${metres(own.heightM)} north–south`,
      meta && meta.extent_m ? `; its own map opens about ±${metres(meta.extent_m)} wide, drawn at the same scale.` : '.',
    ]),
  ];
  if (placed.tier === 'secondary') {
    children.push(h('p', { class: 'map-note' }, 'This facility’s map has no ring, outline or array, so its halls, caverns and buildings are drawn instead.'));
  }
  children.push(
    h('ul', { class: 'map-cmp-features' }, featureRows(placed)),
    methodBlock(facility, placed),
  );
  const actions = h('div', { class: 'map-cmp-actions' });
  const zoom = h('button', { type: 'button', class: 'text-btn', id: 'map-compare-fit' }, 'Zoom to the overlay');
  zoom.addEventListener('click', () => { st.focus = 'map-compare-fit'; api.reframe(); });
  const remove_ = h('button', { type: 'button', class: 'text-btn', id: 'map-compare-remove' }, 'Remove the overlay');
  remove_.addEventListener('click', remove);
  actions.append(zoom, remove_);
  children.push(actions);
  return h('div', { class: 'map-cmp-active' }, children);
}

/** Render the section's body into `el` (localmap.js rebuilds it with the sidebar). */
export function renderPanel(el) {
  if (!api) return;
  const nodes = [];
  nodes.push(h('p', { class: 'map-note' },
    'Lay another facility’s footprint — its rings, outlines and arrays — over this map at true scale, '
    + 'to see how big it really is.'));

  const select = h('select', { id: 'map-compare-select', class: 'map-cmp-select' }, [
    h('option', { value: '' }, 'No overlay'),
    ...candidates().map((fac) => h('option', { value: fac.id.split(':')[1] }, fac.name)),
  ]);
  select.value = api.view.cmp && facilityOf(api.view.cmp) ? api.view.cmp : '';
  select.addEventListener('change', () => choose(select.value));
  nodes.push(h('label', { class: 'map-cmp-label-row', for: 'map-compare-select' }, 'Compare with…'), select);

  const chosen = !!api.view.cmp && !!facilityOf(api.view.cmp);
  const centreBtn = h('button', { type: 'button', class: 'text-btn', id: 'map-compare-centre' }, 'Centre on this view');
  centreBtn.addEventListener('click', () => { if (chosen) centreOnView(); });
  const locateBtn = h('button', {
    type: 'button', class: 'text-btn', id: 'map-compare-locate', 'aria-describedby': 'map-compare-privacy',
  }, 'Over my location');
  if (api.polarHost) {
    locateBtn.disabled = true;
    locateBtn.setAttribute('aria-describedby', 'map-compare-polar');
  } else {
    locateBtn.addEventListener('click', overMyLocation);
  }
  if (!chosen) {
    centreBtn.disabled = true;
    locateBtn.disabled = true;
  }
  nodes.push(h('div', { class: 'map-cmp-actions' }, [centreBtn, locateBtn]));
  if (!chosen) nodes.push(h('p', { class: 'map-note' }, 'Choose a facility to place it.'));
  if (api.polarHost) {
    nodes.push(h('p', { class: 'map-note', id: 'map-compare-polar' },
      'Over my location is not offered here: this map uses a projection that is accurate only near the pole.'));
  }
  nodes.push(h('p', { class: 'map-note map-cmp-privacy', id: 'map-compare-privacy' }, [
    h('strong', {}, 'Your location. '),
    'The location button asks your browser for your position only when you click it. The position is used in this page '
    + 'alone: it is not stored, not sent anywhere, and not written into the link. A shared link carries only the facility '
    + 'being compared and the map point it sits on.',
  ]));
  nodes.push(h('p', { class: 'visually-hidden', role: 'status', 'aria-live': 'polite', id: 'map-compare-status' },
    st.status || st.announce || ''));
  if (st.status) nodes.push(h('p', { class: 'map-note map-cmp-status' }, st.status));

  if (st.error) {
    nodes.push(h('p', { class: 'error-note', role: 'alert' }, st.error));
  } else if (st.loading) {
    nodes.push(h('p', { class: 'loading-note', role: 'status' }, 'Loading the footprint…'));
  } else if (st.placed && chosen) {
    nodes.push(activeBlock());
    if (st.mode === 'location') {
      const tiles = h('button', {
        type: 'button', class: 'map-toggle', id: 'map-compare-tiles', 'aria-pressed': st.allowTiles ? 'true' : 'false',
      }, [
        h('span', { class: 'map-toggle-name' }, 'OpenStreetMap basemap around you'),
        h('span', { class: 'map-toggle-meta' }, st.allowTiles
          ? 'On: your browser is asking OpenStreetMap for tiles around you, which tells it roughly where you are.'
          : 'Off, so that no tile request says where you are. Turn on to see streets and places.'),
      ]);
      tiles.addEventListener('click', () => {
        st.allowTiles = !st.allowTiles;
        st.focus = 'map-compare-tiles';
        api.applyBasemap();
        api.rerender();
      });
      nodes.push(tiles);
    }
  }
  el.replaceChildren(...nodes);
  if (st.focus) {
    const target = el.querySelector(`#${st.focus}`);
    if (target && !target.disabled) target.focus({ preventScroll: true });
    st.focus = null;
  }
  // A test and debugging handle: nothing about the reader's position is in it.
  window.__hepAtlasCompare = () => ({
    slug: st.slug,
    mode: st.mode,
    shapes: st.placed ? st.placed.features.map((f) => ({ id: f.id, type: f.featureType, lengthM: f.lengthM })) : [],
    widthM: st.placed ? st.placed.centre.widthM : null,
    heightM: st.placed ? st.placed.centre.heightM : null,
  });
}
