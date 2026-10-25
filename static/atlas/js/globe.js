// globe.js — Globe.gl wrapper. Facility/site/institution markers are real
// focusable DOM elements (htmlElementsData) holding inline SVG, per
// docs/HEP_ATLAS_GLOBE_LIBRARY.md's own recommendation: this keeps markers
// accessible and clickable without needing access to the bundled three.js
// classes (which globe.gl does not expose on window). Beam and institution
// arcs use the built-in arcsData canvas layer.
//
// Clustering and semantic zoom (docs/HEP_ATLAS_ARCHITECTURE.md "Clustering
// and filters"): the raw entity lists are rebuilt into DOM markers only on
// meaningful events (initial load, a zoom change, a timeline/filter change,
// entering or leaving collaboration mode) — never per animation frame — and
// nearby markers merge into a single focusable cluster marker whose size
// depends on the camera altitude, so a drag never has to reposition more
// DOM nodes than are actually going to be visible.

import {
  facilityShape, statusAtMonth, statusInRange, statusColor, DIMMED_STATUSES,
} from './model.js';
import * as filtersModule from './filters.js';

const SVG_NS = 'http://www.w3.org/2000/svg';

function reducedMotion() {
  return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

export function supportsWebGL2() {
  try {
    const canvas = document.createElement('canvas');
    return !!(window.WebGLRenderingContext && canvas.getContext('webgl2'));
  } catch (error) {
    return false;
  }
}

// ---- clustering / LOD constants (docs/atlas-worklog/REVIEW_performance.md
// "Closure of P1-3") -------------------------------------------------------
// Arcs to a collaboration's institutions default OFF above this many
// *rendered* (post-filter, post-timeline) members — dragging with hundreds
// of always-on arcs was the reviewed worst case (P1-3). The existing
// "Show institution connections" toggle can still turn them back on.
export const INSTITUTION_ARC_THRESHOLD = 150;
// "do not show 5,000 labels simultaneously" (spec §70) — a hard ceiling on
// simultaneously visible marker labels, independent of how many markers are
// on screen. Cluster badges (which *are* the count) always count toward it.
export const LABEL_BUDGET = 40;
// Below this altitude the camera is close enough that individual facility
// pins are unambiguous; at or above it, nearby facilities merge into one
// cluster marker (§17, §70 "far zoom: major facilities").
const FACILITY_CLUSTER_ALTITUDE = 0.6;
// Below this altitude, site/experiment-tier pins are shown at all (§70
// "medium zoom: experiments/sites"); at or above it only facility-tier
// markers (individual or clustered) are drawn.
const SITE_VISIBLE_ALTITUDE = 1.3;
// At or below this altitude, clustering is disabled outright — every
// facility/institution renders as its own marker, however close together.
// This is what makes cluster expansion *terminate*: whatever altitude an
// expansion's geometry math targets, it is clamped to no less than this, so
// repeated activation always converges here instead of asymptoting forever
// against a cluster radius floor no altitude can shrink below (see
// `facilityClusterRadiusDeg`'s own floor of 1°/`institutionClusterRadiusDeg`'s
// 0.4° — two points closer together than that in raw degrees can never be
// separated by the radius formula alone, only by disabling it).
const MIN_CLUSTER_ALTITUDE = 0.12;
// Camera altitude (globe radii) a selection flies to: roughly 30 degrees of
// latitude top to bottom — a country or a US state group is readable, and the
// site tier (below SITE_VISIBLE_ALTITUDE) is on. Selections whose markers are
// far apart (a long-baseline beam, a collaboration's hosts) get the wider one.
const FOCUS_ALTITUDE = 0.5;
const FOCUS_ALTITUDE_WIDE = 1.1;
const FOCUS_WIDE_SPREAD_DEG = 18;
const FOCUS_FLIGHT_MS = 1000;
// Scenery drawn after the first paint (see loadBorders).
const BORDERS_URL = '/atlas/vendor/countries-borders-110m.json';
const BORDER_COLOR = 'rgba(176, 216, 204, 0.42)';
const COAST_COLOR = 'rgba(190, 228, 216, 0.7)';
// Just above the land polygons (polygonAltitude 0.006) so the lines never
// z-fight with the fill, and below every marker layer.
const BORDER_ALTITUDE = 0.0075;

function clamp(v, lo, hi) {
  return Math.min(hi, Math.max(lo, v));
}

/** Shortest signed angular distance between two longitudes, so clustering
 * near the antimeridian (e.g. the IceCube site at lon 0 near the pole, or
 * any future Pacific facility) doesn't see a false 350°+ gap. */
function lonDelta(a, b) {
  let d = a - b;
  d = ((d + 180) % 360 + 360) % 360 - 180;
  return d;
}

function angularDistDeg(aLat, aLon, bLat, bLon) {
  const dLat = aLat - bLat;
  const dLon = lonDelta(aLon, bLon);
  return Math.sqrt(dLat * dLat + dLon * dLon);
}

// Cluster radius (degrees) as a function of camera altitude: clamp(altitude
// * SCALE, FLOOR_DEG, CEIL_DEG). Tuned so that facilities roughly a country
// apart (e.g. CERN and LNGS, ~730 km / ~8.4°) merge at the default overview
// altitude, while different continents never accidentally merge.
function facilityClusterRadiusDeg(altitude) {
  return clamp(altitude * 3.8, 1, 30);
}
// Institution dots are far denser (a single collaboration can have hundreds
// in a small region), so their cluster radius grows faster with altitude.
function institutionClusterRadiusDeg(altitude) {
  return clamp(altitude * 6, 0.4, 45);
}

/**
 * The camera altitude to fly to when a cluster marker is activated.
 *
 * A first version derived this from just the clicked cluster's own members'
 * pairwise spread (zoom in exactly enough to separate *those* points). That
 * broke down in a real, densely-populated region: the wave-3 tree has a
 * chain of ~14 European facilities each within a few hundred km of a
 * neighbour (CERN-LNGS ~8.4°, CERN-Brokdorf ~8.3°, CERN-Leibstadt ~2.5°,
 * Leibstadt-Karlsruhe ~1.5°, and so on). Zooming in "just enough" to split
 * the two clicked members apart routinely lands the camera at an altitude
 * where the clicked pair separates — into two *different* clusters, each
 * freshly re-merged with other nearby facilities the click never
 * mentioned — so a single activation on "CERN, Brokdorf" could still never
 * produce a lone `facility:cern` marker.
 *
 * The fix is not to chase this cluster's specific neighbours; it's to
 * guarantee that one activation disables clustering for the *entire tier*,
 * unconditionally, by targeting an altitude below whichever fixed gate
 * governs that tier: `FACILITY_CLUSTER_ALTITUDE` for facilities (below it,
 * `rebuildVisibleLayer` never clusters facilities at all, dense region or
 * not), and `MIN_CLUSTER_ALTITUDE` for institutions (which have no
 * intermediate gate — they cluster "at every zoom" by design, so this
 * floor is the only altitude at which they don't). This also guarantees
 * termination in the general case: every activation strictly decreases the
 * altitude (`currentAltitude * 0.6` bounds it above), so repeated clicks
 * converge to MIN_CLUSTER_ALTITUDE — where clustering is off for
 * everything, everywhere — in a bounded number of steps regardless of
 * local density.
 */
function expandTargetAltitude(currentAltitude, disableClusteringBelow) {
  const belowGate = disableClusteringBelow * 0.75;
  const upperBound = Math.max(MIN_CLUSTER_ALTITUDE, currentAltitude * 0.6);
  return clamp(Math.min(belowGate, upperBound), MIN_CLUSTER_ALTITUDE, upperBound);
}

/** Greedy single-pass clustering: each item joins the first existing
 * cluster within `radiusDeg` of that cluster's running centroid, else it
 * starts a new one. Deterministic for a stable input order and cheap enough
 * to re-run on every zoom/filter change (never per animation frame). */
function clusterByRadius(items, radiusDeg) {
  const clusters = [];
  for (const item of items) {
    let target = null;
    for (const c of clusters) {
      if (angularDistDeg(c.lat, c.lon, item.lat, item.lon) <= radiusDeg) { target = c; break; }
    }
    if (target) {
      target.items.push(item);
      target.lat = target.items.reduce((s, p) => s + p.lat, 0) / target.items.length;
      target.lon = target.items.reduce((s, p) => s + p.lon, 0) / target.items.length;
    } else {
      clusters.push({ lat: item.lat, lon: item.lon, items: [item] });
    }
  }
  return clusters.map((c) => (
    c.items.length === 1
      ? { kind: 'single', lat: c.items[0].lat, lon: c.items[0].lon, item: c.items[0] }
      : { kind: 'cluster', lat: c.lat, lon: c.lon, items: c.items }
  ));
}

/** Coordinates may be flat (`{lat, lon}`, the dev fixtures) or nested under
 * `coordinates` (`{coordinates: {lat, lon}}`, the real build — see
 * docs/HEP_ATLAS_BUNDLES.md's "Coordinates" stripping rule). Reading only
 * the flat shape silently collapsed every site/institution in the real
 * bundle onto the same undefined point. */
function coordsOf(record) {
  if (!record) return null;
  const c = record.coordinates;
  const lat = c ? c.lat : record.lat;
  const lon = c ? c.lon : record.lon;
  if (lat == null || lon == null) return null;
  // A23: a site's stripped `coordinates` may carry `approximate: true` — a
  // campus-grade point standing in for a detector hall that hasn't been
  // pinned precisely yet. Only the nested (real-bundle) shape carries this;
  // the flat dev-fixture shape predates A23 and is never approximate.
  return { lat, lon, approximate: !!(c && c.approximate) };
}

let hatchCounter = 0;

function svgEl(name, attrs) {
  const el = document.createElementNS(SVG_NS, name);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  return el;
}

/** Builds a small inline-SVG glyph for a marker. `shape` selects the outline,
 * `hollow` draws a stroke-only shape, `hatched` fills with a diagonal hatch
 * pattern (certainty === "possible"), `approximate` draws a dashed outline
 * (A23 — the coordinate itself is a campus-grade stand-in, not a pin on the
 * actual hall/cavern) in the same colour family as the precise marker. */
function buildGlyph({
  shape, color, size, hollow, hatched, approximate,
}) {
  const svg = svgEl('svg', {
    viewBox: '0 0 24 24', width: size, height: size, 'aria-hidden': 'true',
  });
  let fill = (hollow || approximate) ? 'none' : color;
  const stroke = color;
  if (hatched && !hollow && !approximate) {
    hatchCounter += 1;
    const patternId = `atlas-hatch-${hatchCounter}`;
    const defs = svgEl('defs', {});
    const pattern = svgEl('pattern', {
      id: patternId, width: '4', height: '4', patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(45)',
    });
    pattern.appendChild(svgEl('rect', { width: '4', height: '4', fill: 'rgba(0,0,0,0.35)' }));
    pattern.appendChild(svgEl('line', {
      x1: '0', y1: '0', x2: '0', y2: '4', stroke: color, 'stroke-width': '2',
    }));
    defs.appendChild(pattern);
    svg.appendChild(defs);
    fill = `url(#${patternId})`;
  }
  const strokeWidth = (hollow || approximate) ? 2.4 : hatched ? 1.5 : 1;
  const dash = approximate ? '2,2' : (hatched && hollow ? '3,2' : null);
  const common = { fill, stroke, 'stroke-width': strokeWidth };
  if (dash) common['stroke-dasharray'] = dash;
  switch (shape) {
    case 'ring':
      svg.appendChild(svgEl('circle', {
        cx: 12, cy: 12, r: 8, fill: 'none', stroke, 'stroke-width': 3, ...(dash ? { 'stroke-dasharray': dash } : {}),
      }));
      if (!hollow && !approximate) svg.appendChild(svgEl('circle', { cx: 12, cy: 12, r: 8, fill, opacity: 0.25 }));
      break;
    case 'triangle-down':
      svg.appendChild(svgEl('polygon', { points: '3,4 21,4 12,21', ...common }));
      break;
    case 'hexagon':
      svg.appendChild(svgEl('polygon', { points: '12,2 21,7 21,17 12,22 3,17 3,7', ...common }));
      break;
    case 'diamond':
      svg.appendChild(svgEl('polygon', { points: '12,2 22,12 12,22 2,12', ...common }));
      break;
    case 'snowflake':
      for (const angle of [0, 60, 120]) {
        svg.appendChild(svgEl('line', {
          x1: 12, y1: 3, x2: 12, y2: 21, stroke, 'stroke-width': 2,
          transform: `rotate(${angle} 12 12)`,
        }));
      }
      break;
    case 'square':
      svg.appendChild(svgEl('rect', {
        x: 3, y: 3, width: 18, height: 18, ...common,
      }));
      break;
    case 'cluster':
      svg.appendChild(svgEl('circle', { cx: 12, cy: 12, r: 10, fill: 'rgba(15,34,49,0.92)', stroke, 'stroke-width': 2 }));
      break;
    default:
      svg.appendChild(svgEl('circle', { cx: 12, cy: 12, r: 9, ...common }));
  }
  return svg;
}

/**
 * Creates the globe inside `container`.
 * `atlas` is the parsed atlas.json. `index` maps any id -> its record.
 * `onSelect(route)` fires when a marker is activated (click or Enter).
 * `coverElements` are panels that may be laid over the bottom of the stage
 * (the phone layout's bottom sheets); the view is centred on what they leave
 * visible, so a selected marker is not parked underneath one.
 */
export function createGlobe(container, {
  atlas, index, onSelect, coverElements = [],
}) {
  const Globe = window.Globe;
  const globe = Globe()(container)
    .backgroundColor('rgba(0,0,0,0)')
    .showAtmosphere(true)
    .atmosphereColor('#6fa8dc')
    .atmosphereAltitude(0.18)
    .polygonCapColor(() => 'rgba(70,120,100,0.55)')
    .polygonSideColor(() => 'rgba(0,0,0,0)')
    .polygonStrokeColor(() => 'rgba(40,80,66,0.9)')
    .polygonAltitude(0.006)
    .htmlAltitude((d) => d.altitude)
    .htmlElement((d) => d.el)
    .arcsData([])
    .arcStartLat((d) => d.startLat)
    .arcStartLng((d) => d.startLng)
    .arcEndLat((d) => d.endLat)
    .arcEndLng((d) => d.endLng)
    .arcColor((d) => d.color)
    .arcStroke((d) => d.stroke)
    .arcLabel((d) => d.label)
    .arcAltitudeAutoScale(0.35)
    // Dash motion re-animates every arc's material on every rendered frame
    // regardless of user interaction; with a couple hundred institution arcs
    // this was a standing, avoidable cost (REVIEW_performance.md P1-3). A
    // static dash still reads as directional without the continuous redraw.
    .arcDashLength(0.4)
    .arcDashGap(0.18)
    .arcDashAnimateTime(0)
    // Country borders and coastlines (static/atlas/vendor/countries-borders-
    // 110m.json): 1px lines, low contrast, loaded after the first paint.
    .pathsData([])
    .pathPoints('points')
    .pathPointLat((p) => p[1])
    .pathPointLng((p) => p[0])
    .pathPointAlt(BORDER_ALTITUDE)
    .pathColor((d) => (d.kind === 'coastline' ? COAST_COLOR : BORDER_COLOR))
    .pathStroke(null)
    .pathTransitionDuration(0)
    .pathLabel(() => '');

  try {
    const mat = globe.globeMaterial();
    if (mat && mat.color && typeof mat.color.setStyle === 'function') {
      mat.color.setStyle('#0b1f2b');
      if ('shininess' in mat) mat.shininess = 2;
    }
  } catch (error) {
    // Cosmetic only — the sphere still renders with the library default.
  }

  // Evaluated at the moment of use, not once at start-up: a person can switch
  // "reduce motion" on while the page is open.
  const controls = globe.controls();
  controls.autoRotate = !reducedMotion();
  controls.autoRotateSpeed = 0.28;
  controls.enableDamping = true;

  // Auto-rotation is an idle attract mode, and it ends for good the first time
  // the person does anything: drag, wheel/pinch zoom, select something, or move
  // keyboard focus onto a marker. It never resumes — a globe that starts turning
  // again after a pause carries the facility someone is reading about out of
  // view (and is moving content with no way to stop it, WCAG 2.2.2).
  function stopAutoRotate() {
    if (!controls.autoRotate) return;
    controls.autoRotate = false;
    // With damping on, OrbitControls keeps the last rotation steps as momentum
    // and keeps applying them for a second or so after auto-rotation is off —
    // enough to nudge the camera off a facility it has just flown to (more so
    // on a slow frame rate, where each step is bigger). Turning damping off for
    // two frames applies that momentum in one go and clears it.
    const damping = controls.enableDamping;
    controls.enableDamping = false;
    window.requestAnimationFrame(() => window.requestAnimationFrame(() => {
      controls.enableDamping = damping;
    }));
  }
  controls.addEventListener('start', stopAutoRotate); // OrbitControls: pointer down, wheel, touch
  container.addEventListener('focusin', stopAutoRotate);
  const motionQuery = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');
  if (motionQuery && typeof motionQuery.addEventListener === 'function') {
    motionQuery.addEventListener('change', () => { if (reducedMotion()) stopAutoRotate(); });
  }

  fetch('/atlas/vendor/land-110m.json').then((r) => r.json()).then((land) => {
    globe.polygonsData(land.features || []);
  }).catch(() => {});

  // Country borders + coastlines. Fetched only after the globe has painted, so
  // they never delay the first frame; any failure leaves the globe exactly as
  // it was (the land fill keeps its own coast stroke).
  let bordersRequested = false;
  function loadBorders() {
    if (bordersRequested) return;
    bordersRequested = true;
    fetch(BORDERS_URL)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((collection) => {
        const paths = [];
        for (const feature of collection.features || []) {
          const kind = feature.properties && feature.properties.kind;
          const lines = (feature.geometry && feature.geometry.coordinates) || [];
          for (const points of lines) {
            if (points.length > 1) paths.push({ kind, points });
          }
        }
        if (!paths.length) return;
        globe.pathsData(paths);
        // The coastline now comes from the path layer; drop the land polygons'
        // own (dark, doubled) outline.
        globe.polygonStrokeColor(() => null);
      })
      .catch(() => {});
  }

  // --- marker model -------------------------------------------------
  const markerEls = new Map(); // id -> element
  const markerMeta = new Map(); // id -> { segments, tier, route }
  let arcsEnabled = false;
  let arcsForcedOff = false; // true once a collaboration exceeds INSTITUTION_ARC_THRESHOLD
  let beamArcs = [];
  let highlightSet = null;
  let currentAltitude = 2.4;
  // What the open panel is about: the entity id, the globe markers that stand
  // for it (highlighted, kept out of clusters, always captioned) and, for an
  // institution, its id (its markers are ids of the form `<collab>::<id>`).
  let selection = { id: null, markerIds: new Set(), institutionId: null, anchor: null, altitude: FOCUS_ALTITUDE };
  let filterState = filtersModule.emptyFilterState();
  const topicIndex = filtersModule.buildTopicIndex(atlas.topics || {});
  const siteExperimentIndex = filtersModule.buildSiteExperimentIndex(atlas);

  function makeInteractiveElement({
    id, name, ariaLabel, size, shape, color, hollow, hatched, approximate, tier, extraClass, onActivate,
  }) {
    const el = document.createElement('div');
    el.className = `atlas-marker tier-${tier}${extraClass ? ` ${extraClass}` : ''}`;
    if (approximate) el.classList.add('is-approximate-location');
    el.setAttribute('role', 'button');
    el.setAttribute('tabindex', '0');
    // A23 + §23 (non-colour-only encoding): an approximate coordinate (a
    // campus-grade stand-in, not a pin on the actual hall) and an "uncertain"
    // certainty (docs/HEP_ATLAS_ARCHITECTURE.md's "the globe hatches" possible
    // segments) each say so in the accessible name, not only by shape/pattern
    // — a dashed outline or a diagonal hatch is invisible to a screen reader.
    const label0 = ariaLabel || name;
    const suffixes = [];
    if (hatched) suffixes.push('uncertain');
    if (approximate) suffixes.push('approximate location');
    const fullLabel = suffixes.length ? `${label0} (${suffixes.join(', ')})` : label0;
    el.setAttribute('aria-label', fullLabel);
    el.title = fullLabel;
    el.dataset.id = id;
    // Read by the selected-marker halo in atlas.css so the ring clears the glyph.
    el.style.setProperty('--marker-size', `${size}px`);
    el.appendChild(buildGlyph({
      shape, color, size, hollow, hatched, approximate,
    }));
    const label = document.createElement('span');
    label.className = 'atlas-marker-label';
    label.textContent = name;
    el.appendChild(label);
    el.addEventListener('click', onActivate);
    el.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        onActivate();
      }
    });
    return el;
  }

  function makeMarkerElement({
    id, name, route, size, shape, color, hollow, hatched, approximate, tier,
  }) {
    return makeInteractiveElement({
      id,
      name,
      size,
      shape,
      color,
      hollow,
      hatched,
      approximate,
      tier,
      onActivate: () => {
        // Clicking the marker whose panel is already open puts the camera back
        // on it (the navigation itself is a no-op for an unchanged route).
        if (selection.markerIds.has(id)) flyToSelection();
        if (onSelect) onSelect(route);
      },
    });
  }

  function makeClusterElement({
    id, lat, lng, tier, count, names, expand,
  }) {
    const size = clamp(18 + Math.log2(count + 1) * 4, 18, 34);
    const label = `${count} ${tier === 'facility' ? 'facilities' : tier === 'site' ? 'sites' : 'institutions'}`;
    const namesPreview = names.slice(0, 4).join(', ') + (names.length > 4 ? ', …' : '');
    const el = makeInteractiveElement({
      id,
      name: String(count),
      ariaLabel: `${label} near here — ${namesPreview}. Press Enter to zoom in and expand.`,
      size,
      shape: 'cluster',
      color: '#f2b441',
      hollow: false,
      tier,
      extraClass: 'tier-cluster',
      onActivate: () => expand(lat, lng),
    });
    el.classList.add('is-cluster');
    return { id, lat, lng, altitude: tier === 'institution' ? 0.02 : 0.03, el, size, count };
  }

  function siteCoords(siteId) {
    return coordsOf(index.get(siteId));
  }

  /** Zooms to `lat`/`lng` at an altitude below `disableClusteringBelow`
   * (see `expandTargetAltitude`), so activating a cluster disables
   * clustering for its whole tier rather than just nudging its own two
   * members apart. */
  function expandAt(lat, lng, disableClusteringBelow) {
    const nextAltitude = expandTargetAltitude(currentAltitude, disableClusteringBelow);
    currentAltitude = nextAltitude;
    globe.pointOfView({ lat, lng, altitude: nextAltitude }, reducedMotion() ? 0 : 700);
    rebuildVisibleLayer();
  }

  // --- raw entity lists (built once; re-clustered on demand, not rebuilt
  // from atlas every time) -------------------------------------------------
  let facilityEntities = [];
  let siteEntities = [];
  let institutionEntities = [];
  let institutionCollaborationId = null;
  let institutionCollaborationExperiments = [];
  let hostCoords = null;
  let rawInstitutionCount = 0;

  function buildFacilityEntities() {
    const out = [];
    for (const facility of Object.values(atlas.facilities || {})) {
      const coords = siteCoords(facility.primary_site_id);
      if (!coords) continue;
      out.push({
        id: facility.id,
        name: facility.name,
        lat: coords.lat,
        lon: coords.lon,
        approximate: coords.approximate,
        record: facility,
      });
    }
    return out;
  }

  function buildSiteEntities() {
    const out = [];
    for (const site of Object.values(atlas.sites || {})) {
      const coords = coordsOf(site);
      if (!coords) continue;
      out.push({
        id: site.id,
        name: site.name,
        lat: coords.lat,
        lon: coords.lon,
        approximate: coords.approximate,
        record: site,
      });
    }
    return out;
  }

  function buildBeamArcs() {
    const out = [];
    for (const beamline of Object.values(atlas.beamlines || {})) {
      for (const baseline of beamline.baselines || []) {
        const from = siteCoords(baseline.from_site_id);
        const to = siteCoords(baseline.to_site_id);
        if (!from || !to) continue;
        out.push({
          id: `${beamline.id}:${baseline.from_site_id}:${baseline.to_site_id}`,
          startLat: from.lat,
          startLng: from.lon,
          endLat: to.lat,
          endLng: to.lon,
          color: ['rgba(84,198,186,0.85)', 'rgba(84,198,186,0.15)'],
          stroke: 0.5,
          label: `${beamline.name}: ${baseline.distance ? baseline.distance.display : ''} baseline`,
          kind: 'beam',
        });
      }
    }
    return out;
  }

  // --- timeline filtering ---------------------------------------------
  let timelineMode = null; // { kind: 'year', year, month } | { kind: 'range', lo, hi } | null
  // The same selection, shaped for filters.js's statusForTimeline (A3).
  function filterTimelineState() {
    if (!timelineMode) return null;
    return timelineMode.kind === 'year'
      ? { year: timelineMode.year }
      : { range: [Math.floor(timelineMode.lo / 12) + 1950, Math.floor(timelineMode.hi / 12) + 1950] };
  }

  function segmentsPresence(segments) {
    if (!segments || segments.length === 0 || !timelineMode) return null;
    return timelineMode.kind === 'year'
      ? statusAtMonth(segments, timelineMode.month)
      : statusInRange(segments, timelineMode.lo, timelineMode.hi);
  }

  function applyTimelineClasses(el, segments) {
    if (!segments || segments.length === 0 || !timelineMode) {
      el.classList.remove('is-dimmed', 'is-possible', 'is-absent');
      return;
    }
    const result = segmentsPresence(segments);
    if (!result) {
      el.classList.add('is-absent');
      el.classList.remove('is-dimmed', 'is-possible');
      return;
    }
    el.classList.remove('is-absent');
    el.classList.toggle('is-dimmed', DIMMED_STATUSES.has(result.status));
    el.classList.toggle('is-possible', result.certainty === 'possible');
  }

  // --- the actual render pipeline --------------------------------------
  // Runs only on real state changes (never per animation frame): initial
  // load, a camera zoom, a timeline move, a filter change, or entering/
  // leaving a collaboration. Each run fully replaces htmlElementsData and
  // arcsData with a freshly clustered set sized for the current altitude.
  function rebuildVisibleLayer() {
    markerEls.clear();
    markerMeta.clear();
    const tls = filterTimelineState();

    // ---- facilities: always shown, clustered when zoomed out ----------
    // The selected facility is shown whatever the filters say (its panel is
    // open, so it must be findable) and is never merged into a cluster.
    const passingFacilities = facilityEntities.filter(
      (f) => selection.markerIds.has(f.id)
        || filtersModule.facilityMatchesWithTopics(f.record, filterState, tls, topicIndex),
    );
    const selectedFacilities = passingFacilities.filter((f) => selection.markerIds.has(f.id));
    const clusterableFacilities = selectedFacilities.length
      ? passingFacilities.filter((f) => !selection.markerIds.has(f.id)) : passingFacilities;
    // Facilities also disable clustering outright below FACILITY_CLUSTER_ALTITUDE
    // (see `expandTargetAltitude`, which always zooms cluster-expansion below
    // it) — the `> MIN_CLUSTER_ALTITUDE` guard is redundant here in practice
    // but keeps this condition correct if that gate is ever lowered.
    const facilityClustered = (currentAltitude >= FACILITY_CLUSTER_ALTITUDE && currentAltitude > MIN_CLUSTER_ALTITUDE)
      ? clusterByRadius(clusterableFacilities, facilityClusterRadiusDeg(currentAltitude))
      : clusterableFacilities.map((f) => ({ kind: 'single', lat: f.lat, lon: f.lon, item: f }));
    for (const f of selectedFacilities) {
      facilityClustered.push({ kind: 'single', lat: f.lat, lon: f.lon, item: f });
    }

    // ---- sites: only at medium/close zoom; not clustered (kept
    // individually addressable — see docs/HEP_ATLAS_ARCHITECTURE.md) -----
    const sitesVisibleTier = currentAltitude < SITE_VISIBLE_ALTITUDE;
    // A selected site is drawn at any zoom (it is what the panel is about).
    const passingSites = siteEntities.filter((s) => (
      selection.markerIds.has(s.id)
      || (sitesVisibleTier
        && filtersModule.siteMatches(s.record, filterState, tls, siteExperimentIndex, topicIndex))
    ));

    // ---- institutions: clustered at every zoom (collaboration mode) ---
    const passingInstitutions = institutionEntities.filter(
      (m) => filtersModule.institutionMatches(
        m.record, filterState, institutionCollaborationExperiments, topicIndex,
      ),
    );
    const isSelectedInstitution = (m) => !!selection.institutionId
      && m.record.institution_id === selection.institutionId;
    const clusterableInstitutions = selection.institutionId
      ? passingInstitutions.filter((m) => !isSelectedInstitution(m)) : passingInstitutions;
    const institutionClustered = currentAltitude > MIN_CLUSTER_ALTITUDE
      ? clusterByRadius(clusterableInstitutions, institutionClusterRadiusDeg(currentAltitude))
      : clusterableInstitutions.map((m) => ({ kind: 'single', lat: m.lat, lon: m.lon, item: m }));
    for (const m of passingInstitutions.filter(isSelectedInstitution)) {
      institutionClustered.push({ kind: 'single', lat: m.lat, lon: m.lon, item: m });
    }

    const htmlLayer = [];
    const labelCandidates = []; // { el, priority } — trimmed to LABEL_BUDGET after building

    for (const entry of facilityClustered) {
      if (entry.kind === 'single') {
        const { record } = entry.item;
        const info = facilityShape(record.kind);
        // §23 / docs/HEP_ATLAS_ARCHITECTURE.md "certainty ... which the globe
        // hatches": must be known before the glyph is built, since the hatch
        // pattern is baked into the marker's own SVG, not toggled after the
        // fact by a CSS class the way dimming is.
        const presence = segmentsPresence(record.state_segments);
        const uncertain = !!(presence && presence.certainty === 'possible');
        const el = makeMarkerElement({
          id: record.id,
          name: record.name,
          route: { type: 'facility', slug: record.id.split(':')[1] },
          size: 26,
          shape: info.shape,
          color: info.color,
          hollow: false,
          hatched: uncertain,
          approximate: entry.item.approximate,
          tier: 'facility',
        });
        markerEls.set(record.id, el);
        markerMeta.set(record.id, { segments: record.state_segments, tier: 'facility' });
        applyTimelineClasses(el, record.state_segments);
        htmlLayer.push({
          id: record.id, lat: entry.lat, lng: entry.lon, altitude: 0.02, el,
        });
        labelCandidates.push({ el, priority: 0 });
      } else {
        const id = `cluster:facility:${entry.items.map((i) => i.id).sort().join('+')}`;
        const marker = makeClusterElement({
          id,
          lat: entry.lat,
          lng: entry.lon,
          tier: 'facility',
          count: entry.items.length,
          names: entry.items.map((i) => i.name),
          expand: (lat, lng) => expandAt(lat, lng, FACILITY_CLUSTER_ALTITUDE),
        });
        markerEls.set(id, marker.el);
        markerMeta.set(id, { segments: null, tier: 'facility' });
        htmlLayer.push(marker);
        labelCandidates.push({ el: marker.el, priority: -1 }); // clusters always keep their label
      }
    }

    for (const site of passingSites) {
      const sitePresence = segmentsPresence(site.record.state_segments);
      const siteUncertain = !!(sitePresence && sitePresence.certainty === 'possible');
      const el = makeMarkerElement({
        id: site.id,
        name: site.record.name,
        // Sites have their own detail panel (routes added with the local-map
        // release), so a site marker opens the site, not its parent facility.
        route: { type: 'site', slug: site.id.split(':')[1] },
        size: 12,
        shape: 'circle',
        color: statusColor(site.record.status),
        hollow: false,
        hatched: siteUncertain,
        approximate: site.approximate,
        tier: 'site',
      });
      el.classList.add('is-site-tier');
      markerEls.set(site.id, el);
      markerMeta.set(site.id, { segments: site.record.state_segments, tier: 'site' });
      applyTimelineClasses(el, site.record.state_segments);
      htmlLayer.push({
        id: site.id, lat: site.lat, lng: site.lon, altitude: 0.012, el,
      });
      labelCandidates.push({ el, priority: 1 });
    }

    const instArcs = [];
    for (const entry of institutionClustered) {
      if (entry.kind === 'single') {
        const member = entry.item.record;
        const id = `${institutionCollaborationId}::${member.institution_id}`;
        const hollow = member.render === 'hollow';
        const el = makeMarkerElement({
          id,
          name: member.name,
          route: { type: 'institution', slug: member.institution_id.split(':')[1] },
          size: 9,
          shape: 'circle',
          color: '#f2b441',
          hollow,
          tier: 'institution',
        });
        el.dataset.collaboration = institutionCollaborationId;
        markerEls.set(id, el);
        markerMeta.set(id, { segments: null, tier: 'institution' });
        htmlLayer.push({
          id, lat: entry.lat, lng: entry.lon, altitude: 0.015, el,
        });
        labelCandidates.push({ el, priority: 2 });
        if (hostCoords) {
          instArcs.push({
            id: `conn:${id}`,
            startLat: hostCoords.lat,
            startLng: hostCoords.lon,
            endLat: entry.lat,
            endLng: entry.lon,
            color: ['rgba(242,180,65,0.55)', 'rgba(242,180,65,0.05)'],
            stroke: 0.25,
            label: `${member.name} ↔ collaboration host`,
          });
        }
      } else {
        const id = `cluster:institution:${institutionCollaborationId}:${entry.items.map((i) => i.record.institution_id).sort().join('+')}`;
        const marker = makeClusterElement({
          id,
          lat: entry.lat,
          lng: entry.lon,
          tier: 'institution',
          count: entry.items.length,
          names: entry.items.map((i) => i.record.name),
          expand: (lat, lng) => expandAt(lat, lng, MIN_CLUSTER_ALTITUDE),
        });
        markerEls.set(id, marker.el);
        markerMeta.set(id, { segments: null, tier: 'institution' });
        htmlLayer.push(marker);
        labelCandidates.push({ el: marker.el, priority: -1 });
        if (hostCoords) {
          instArcs.push({
            id: `conn:${id}`,
            startLat: hostCoords.lat,
            startLng: hostCoords.lon,
            endLat: entry.lat,
            endLng: entry.lon,
            color: ['rgba(242,180,65,0.55)', 'rgba(242,180,65,0.05)'],
            stroke: 0.25,
            label: `${entry.items.length} institutions ↔ collaboration host`,
          });
        }
      }
    }

    // ---- label budget: clusters (priority -1) always keep their label;
    // individual markers are shown in tier order (facility, site,
    // institution) until the budget is spent. ----------------------------
    labelCandidates.sort((a, b) => a.priority - b.priority);
    let shown = 0;
    for (const { el, priority } of labelCandidates) {
      const keep = priority < 0 || shown < LABEL_BUDGET;
      el.classList.toggle('no-label', !keep);
      if (keep) shown += 1;
    }

    // ---- highlight (topic mode) carries over the rebuild --------------
    if (highlightSet) {
      for (const [id, el] of markerEls) {
        el.classList.toggle('is-highlighted', highlightSet.has(id));
        el.classList.toggle('is-muted', !highlightSet.has(id));
      }
    }

    // ---- the selected entity's markers (halo + caption, atlas.css) ----------
    // A site that sits under a selected facility's glyph (a facility marker is
    // drawn on its primary site) gets no halo of its own: one ring, not two
    // nested ones, and one caption.
    const selectedFacilityPoints = htmlLayer.filter(
      (d) => markerMeta.get(d.id).tier === 'facility' && !markerMeta.get(d.id).cluster && isSelectedMarker(d.id),
    );
    // Within ~5 km: closer than a facility glyph is wide at the zoom a selection
    // flies to.
    const isUnderSelectedFacility = (d) => selectedFacilityPoints.some(
      (f) => Math.abs(f.lat - d.lat) < 0.05 && Math.abs(lonDelta(f.lng, d.lng)) < 0.05,
    );
    for (const d of htmlLayer) {
      if (!isSelectedMarker(d.id)) continue;
      const el = d.el;
      el.setAttribute('aria-current', 'true');
      const under = markerMeta.get(d.id).tier === 'site' && isUnderSelectedFacility(d);
      if (!under) el.classList.add('is-selected');
      // Timeline: an entity that did not exist in the selected year is hidden
      // (is-absent), but one whose panel is open must stay findable. The panel
      // says why it is not operating; the marker is drawn dimmed.
      if (el.classList.contains('is-absent')) {
        el.classList.remove('is-absent');
        el.classList.add('is-dimmed');
      }
    }

    globe.htmlElementsData(htmlLayer);

    // ---- arcs: capped to what's actually drawn (never the full roster —
    // only the currently visible/clustered institution markers get an arc).
    // The >INSTITUTION_ARC_THRESHOLD *default*-off behaviour is enforced by
    // app.js resetting the `arcs` URL/UI state when a large collaboration is
    // first entered (isArcsForcedOff()); the toggle itself always reflects
    // and controls what's actually drawn here, so it never lies to the user.
    const arcs = [...beamArcs];
    if (arcsEnabled) arcs.push(...instArcs);
    globe.arcsData(arcs);
  }

  function reapplyTimeline() {
    rebuildVisibleLayer();
  }

  globe.onZoom(({ altitude }) => {
    if (Math.abs(altitude - currentAltitude) < 0.01) return;
    currentAltitude = altitude;
    rebuildVisibleLayer();
  });

  // ---- selection: which markers an open panel stands for, and where to look
  const facilitiesBySite = new Map();
  for (const facility of Object.values(atlas.facilities || {})) {
    if (!facility.primary_site_id) continue;
    const list = facilitiesBySite.get(facility.primary_site_id) || [];
    list.push(facility.id);
    facilitiesBySite.set(facility.primary_site_id, list);
  }

  function isSelectedMarker(id) {
    return selection.markerIds.has(id)
      || (!!selection.institutionId && id.endsWith(`::${selection.institutionId}`));
  }

  function facilityAnchor(facilityId) {
    const facility = atlas.facilities && atlas.facilities[facilityId];
    return facility ? siteCoords(facility.primary_site_id) : null;
  }

  /** The markers and camera target for an entity id (`facility:fermilab`,
   * `experiment:dune`, ...). An entity with no place on the globe — a person,
   * a result, a topic — resolves to an empty selection: nothing highlighted
   * and nowhere to fly. A facility's marker sits on its primary site, so a
   * site that hosts a facility highlights that facility's marker too: it is
   * the glyph a person can actually see there. */
  function resolveSelection(id) {
    const out = {
      id, markerIds: new Set(), institutionId: null, anchor: null, altitude: FOCUS_ALTITUDE,
    };
    if (!id) return out;
    const record = index.get(id);
    const addSite = (siteId) => {
      if (!siteId || !atlas.sites || !atlas.sites[siteId]) return;
      out.markerIds.add(siteId);
      for (const facilityId of facilitiesBySite.get(siteId) || []) out.markerIds.add(facilityId);
    };
    const addFacility = (facilityId) => {
      if (facilityId && atlas.facilities && atlas.facilities[facilityId]) out.markerIds.add(facilityId);
    };
    switch (id.split(':')[0]) {
      case 'facility':
        addFacility(id);
        out.anchor = facilityAnchor(id);
        break;
      case 'site':
        addSite(id);
        out.anchor = siteCoords(id);
        break;
      case 'experiment': {
        if (!record) break;
        const host = (record.facility_roles || []).find((r) => r.role === 'host');
        (record.site_ids || []).forEach(addSite);
        (record.facility_ids || []).forEach(addFacility);
        out.anchor = (host && facilityAnchor(host.facility_id))
          || (record.site_ids || []).map(siteCoords).find(Boolean)
          || (record.facility_ids || []).map(facilityAnchor).find(Boolean) || null;
        break;
      }
      case 'detector': {
        if (!record) break;
        const siteIds = (record.placements || []).map((p) => p.site_id).filter(Boolean);
        siteIds.forEach(addSite);
        out.anchor = siteIds.map(siteCoords).find(Boolean) || null;
        break;
      }
      case 'accelerator':
        if (!record) break;
        addSite(record.site_id);
        addFacility(record.facility_id);
        out.anchor = siteCoords(record.site_id) || facilityAnchor(record.facility_id);
        break;
      case 'beamline': {
        if (!record) break;
        const siteIds = [...(record.near_detector_site_ids || []), ...(record.far_detector_site_ids || [])];
        addFacility(record.facility_id);
        siteIds.forEach(addSite);
        out.anchor = siteIds.map(siteCoords).find(Boolean) || facilityAnchor(record.facility_id);
        break;
      }
      case 'collaboration':
        if (!record) break;
        addSite(record.host_site_id);
        addFacility(record.host_facility_id);
        out.anchor = siteCoords(record.host_site_id) || facilityAnchor(record.host_facility_id);
        break;
      case 'institution': {
        out.institutionId = id;
        const member = institutionEntities.find((m) => m.record.institution_id === id);
        out.anchor = member ? { lat: member.lat, lon: member.lon } : null;
        break;
      }
      default:
        break;
    }
    if (out.anchor) {
      let spread = 0;
      for (const markerId of out.markerIds) {
        const at = atlas.sites && atlas.sites[markerId] ? siteCoords(markerId) : facilityAnchor(markerId);
        if (at) spread = Math.max(spread, angularDistDeg(out.anchor.lat, out.anchor.lon, at.lat, at.lon));
      }
      out.altitude = spread > FOCUS_WIDE_SPREAD_DEG ? FOCUS_ALTITUDE_WIDE : FOCUS_ALTITUDE;
    }
    return out;
  }

  /** Flies the camera to the selection (~1 s, or an instant jump under
   * prefers-reduced-motion). Auto-rotation is switched off first: left on, it
   * keeps turning the globe under the flight and the facility drifts away. */
  function flyToSelection() {
    const { anchor, altitude } = selection;
    if (!anchor) return;
    stopAutoRotate();
    globe.pointOfView(
      { lat: anchor.lat, lng: anchor.lon, altitude },
      reducedMotion() ? 0 : FOCUS_FLIGHT_MS,
    );
  }

  // ---- a panel laid over the bottom of the stage ---------------------------
  // On a phone the detail panel is a fixed bottom sheet over the globe. The
  // camera looks at the middle of the *canvas*, so a selected marker lands
  // right under the sheet. A projection offset moves the centre of the view up
  // by half of what the sheet covers, so the camera target sits in the middle
  // of the part that is still visible. Desktop panels are grid columns (the
  // canvas itself shrinks) or sit inside the stage, so nothing is covered.
  let insetKey = '';
  function coveredBottom() {
    const stage = container.getBoundingClientRect();
    let covered = 0;
    for (const el of coverElements) {
      if (!el || el.getClientRects().length === 0) continue; // display:none
      if (window.getComputedStyle(el).position !== 'fixed') continue;
      const top = el.getBoundingClientRect().top;
      if (top < stage.bottom) covered = Math.max(covered, stage.bottom - Math.max(top, stage.top));
    }
    // Never push the view centre past the point where little globe would be
    // left on screen.
    return Math.min(covered, stage.height * 0.7);
  }
  function applyViewInset(width, height) {
    const camera = typeof globe.camera === 'function' ? globe.camera() : null;
    if (!camera || typeof camera.setViewOffset !== 'function') return;
    const inset = Math.round(coveredBottom());
    // The library refreshes the projection when the canvas size changes but
    // keeps the old view window, so the size is part of what must be unchanged.
    const key = `${width}x${height}:${inset}`;
    if (key === insetKey) return;
    insetKey = key;
    if (inset > 0) camera.setViewOffset(width, height, 0, Math.round(inset / 2), width, height);
    else if (camera.view && camera.view.enabled) camera.clearViewOffset();
  }

  // --- public API -------------------------------------------------------
  const api = {
    ready() {
      // No fly-in intro: an animated initial camera move is exactly the kind
      // of motion prefers-reduced-motion asks us to skip, and it also left
      // marker screen positions a moving target for a second or two after
      // load. Frame a stable default view instantly instead.
      currentAltitude = 2.4;
      globe.pointOfView({ lat: 20, lng: 10, altitude: currentAltitude }, 0);
      facilityEntities = buildFacilityEntities();
      siteEntities = buildSiteEntities();
      beamArcs = buildBeamArcs();
      rebuildVisibleLayer();
      // After the first frame has painted, bring in the country borders.
      window.requestAnimationFrame(() => window.setTimeout(loadBorders, 0));
    },
    setYear(year) {
      timelineMode = { kind: 'year', year, month: Math.round((year - 1950) * 12 + 6) };
      reapplyTimeline();
    },
    setRange(lo, hi) {
      timelineMode = {
        kind: 'range', lo: Math.round((lo - 1950) * 12), hi: Math.round((hi - 1950) * 12 + 11),
      };
      reapplyTimeline();
    },
    clearTimeline() {
      timelineMode = null;
      reapplyTimeline();
    },
    setFilters(nextFilters) {
      const next = nextFilters || filtersModule.emptyFilterState();
      // app.js pushes the filters on every route change; rebuilding every DOM
      // marker for an unchanged set is wasted work and drops hover state.
      if (JSON.stringify(next) === JSON.stringify(filterState)) return;
      filterState = next;
      rebuildVisibleLayer();
    },
    setArcsEnabled(enabled) {
      if (enabled === arcsEnabled) return;
      arcsEnabled = enabled;
      rebuildVisibleLayer();
    },
    /** True once a collaboration's raw member count exceeded
     * INSTITUTION_ARC_THRESHOLD and arcs were defaulted off for it — lets
     * app.js keep the toggle's checked state honest. */
    isArcsForcedOff() {
      return arcsForcedOff;
    },
    setHighlight(idSet) {
      highlightSet = idSet;
      for (const [id, el] of markerEls) {
        el.classList.toggle('is-highlighted', !!highlightSet && highlightSet.has(id));
        el.classList.toggle('is-muted', !!highlightSet && !highlightSet.has(id));
      }
    },
    async setCollaboration(collaborationId, membership) {
      institutionCollaborationId = collaborationId;
      const collaboration = index.get(collaborationId);
      institutionCollaborationExperiments = ((collaboration && collaboration.experiment_ids) || [])
        .map((id) => atlas.experiments[id]).filter(Boolean);
      hostCoords = collaboration && siteCoords(collaboration.host_site_id);
      const rows = (membership && membership.members) || [];
      institutionEntities = [];
      for (const member of rows) {
        if (!member.institution_id) continue;
        const coords = coordsOf(member);
        if (!coords) continue;
        institutionEntities.push({ lat: coords.lat, lon: coords.lon, record: member });
      }
      rawInstitutionCount = institutionEntities.length;
      arcsForcedOff = rawInstitutionCount > INSTITUTION_ARC_THRESHOLD;
      rebuildVisibleLayer();
      if (hostCoords) {
        currentAltitude = 1.6;
        globe.pointOfView({ lat: hostCoords.lat, lng: hostCoords.lon, altitude: currentAltitude }, reducedMotion() ? 0 : 900);
        rebuildVisibleLayer();
      }
    },
    clearCollaboration() {
      institutionCollaborationId = null;
      institutionCollaborationExperiments = [];
      institutionEntities = [];
      hostCoords = null;
      arcsForcedOff = false;
      rebuildVisibleLayer();
    },
    /** The open panel's entity (or null when the panel closes). Highlights its
     * markers, keeps them out of clusters, and — unless `fly` is false, as in
     * collaboration mode where setCollaboration() owns the camera — flies there.
     * Selecting what is already selected does nothing, so re-rendering the panel
     * (a filter or a timeline move) never yanks the camera back. */
    select(id, { fly = true } = {}) {
      const next = id || null;
      if (next === selection.id) return;
      selection = resolveSelection(next);
      if (next) stopAutoRotate();
      rebuildVisibleLayer();
      if (next && fly) flyToSelection();
    },
    resize() {
      const width = container.clientWidth;
      const height = container.clientHeight;
      // A hidden stage (no-WebGL fallback showing, or a 0-sized container) has
      // no size to fit; keep the last good one.
      if (!width || !height) return;
      if (globe.width() !== width || globe.height() !== height) globe.width(width).height(height);
      applyViewInset(width, height);
    },
    destroy() {
      if (resizeObserver) resizeObserver.disconnect();
      if (typeof globe._destructor === 'function') globe._destructor();
    },
  };
  api.resize();

  // Keep the canvas sized to its container whatever changes it: the window, a
  // detail panel opening or closing (the grid gives the globe a different
  // width), or the timeline bar finishing its own layout after the globe was
  // created — the canvas was sized once at start-up, before the timeline
  // existed, and stayed taller than the stage it sits in.
  let resizeObserver = null;
  if (typeof ResizeObserver === 'function') {
    let frame = 0;
    resizeObserver = new ResizeObserver(() => {
      if (frame) return;
      frame = window.requestAnimationFrame(() => {
        frame = 0;
        api.resize();
      });
    });
    resizeObserver.observe(container);
    // A bottom sheet appearing or changing height does not resize the stage,
    // but it does change what is visible of it.
    for (const el of coverElements) if (el) resizeObserver.observe(el);
  }
  return api;
}
