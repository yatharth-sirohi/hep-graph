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
  facilityShape, statusAtMonth, statusInRange, statusColor, timelineAbsenceReason, DIMMED_STATUSES,
} from './model.js';
import * as filtersModule from './filters.js';
import { buildGlyph, cssToken, withAlpha } from './globeicons.js';

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
// on screen. Applied to the captions actually on screen by declutterLabels,
// after overlap removal; cluster badges (which *are* the count), the selected
// marker and the hovered one always count toward it.
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
// The range showView accepts: just above the surface to well clear of the globe.
const MIN_VIEW_ALTITUDE = 0.05;
const MAX_VIEW_ALTITUDE = 4;
// showView lowers a requested altitude on a stage too short to show the globe at least
// this big (radius, px).
const MIN_GLOBE_RADIUS_PX = 105;
// Throttles (ms). Camera moves fire per animation frame; rebuilding every DOM
// marker or re-measuring every label that often would cost more than the
// frame itself.
const REBUILD_THROTTLE_MS = 100;
const DECLUTTER_DELAY_MS = 120;
// A caption is dropped for a marker this close to the globe's edge (as a
// fraction of the angle to the horizon): foreshortened and sitting on the
// atmosphere glow, its name would only add noise. Beyond the horizon itself the
// marker is not drawn at all.
const LIMB_LABEL_FRACTION = 0.9;
// Scenery drawn after the first paint (see loadBorders, loadEarthTexture).
const BORDERS_URL = '/atlas/vendor/countries-borders-110m.json';
const BORDER_COLOR = 'rgba(176, 216, 204, 0.34)';
const COAST_COLOR = 'rgba(190, 228, 216, 0.62)';
// Just above the land polygons (polygonAltitude 0.006) so the lines never
// z-fight with the fill, and below every marker layer.
const BORDER_ALTITUDE = 0.0075;
// The shaded-relief Earth (static/atlas/vendor/README.md has its source and
// recipe). It replaces the flat land polygons once it has loaded; until then, or
// if it never does, the globe keeps its original look.
const EARTH_URL = '/atlas/vendor/earth-dark-4096.webp';
const BASE_LAND_COLOR = 'rgb(36,50,61)'; // atlas_earth_texture.py's land ramp, mid-way
const BASE_OCEAN_COLOR = '#0b1f2c'; // and its ocean ramp
const BASE_COAST_COLOR = 'rgba(150,188,184,0.42)';
const ATMOSPHERE_COLOR = '#2f9c96';
const ATMOSPHERE_ALTITUDE = 0.09;

// ---- facility glyph size -----------------------------------------------------
// A facility's marker grows with how many experiments it hosts (square root, so
// the area follows the count), clamped so CERN and Fermilab read as major
// without hiding a one-experiment site beside them.
const FACILITY_SIZE_MIN = 19;
const FACILITY_SIZE_MAX = 38;
const FACILITY_SIZE_BASE = 14.5;
const FACILITY_SIZE_SLOPE = 5.4;
export function facilityGlyphSize(experimentCount) {
  const n = Math.max(0, Number(experimentCount) || 0);
  return Math.round(clamp(FACILITY_SIZE_BASE + FACILITY_SIZE_SLOPE * Math.sqrt(n), FACILITY_SIZE_MIN, FACILITY_SIZE_MAX));
}

// ---- beams -------------------------------------------------------------------
// A long-baseline beam is drawn as an animated arc from its source to each far
// detector, labelled at mid-arc. A baseline shorter than this is a near-detector
// distance (BNB, NuMI's near hall): on the globe it would be a dot, so it is
// left to the to-scale local map.
export const BEAM_MIN_KM = 15;
const KM_PER_DEG = 111.195;
const BEAM_FLOW_MS = 2800;
const BEAM_COLOR = ['rgba(150,244,255,0.98)', 'rgba(70,180,255,0.88)'];
const BEAM_COLOR_SELECTED = ['rgba(255,255,255,1)', 'rgba(110,205,255,0.9)'];
// Beam arcs are drawn as tubes whose thickness is in degrees of arc on the globe,
// so a fixed value is a hair on the opening overview and a 20 px smear one zoom in.
// styleBeamArc turns these on-screen widths (px) into degrees for the camera
// altitude of the moment.
const BEAM_PX = 3;
const BEAM_PX_SELECTED = 4.6;
// A live beam also gets a wide, faint, solid arc underneath: a glow the tube
// geometry cannot give.
const BEAM_GLOW_PX = 9;
const BEAM_GLOW_PX_SELECTED = 13;
const BEAM_GLOW_COLOR = ['rgba(90,200,255,0.2)', 'rgba(60,150,255,0.1)'];
const BEAM_GLOW_COLOR_SELECTED = ['rgba(150,225,255,0.34)', 'rgba(90,180,255,0.2)'];
// A beam that is not running (under construction, shut down, completed): the same
// hue family, but fine static dashes instead of a flowing stream, and dimmer.
const BEAM_COLOR_QUIET = ['rgba(155,195,228,0.88)', 'rgba(135,175,212,0.74)'];
const BEAM_COLOR_QUIET_SELECTED = ['rgba(235,246,255,1)', 'rgba(160,200,232,0.9)'];
const BEAM_PX_QUIET = 2.4;
const BEAM_PX_QUIET_SELECTED = 3.2;
// A beam selection flies to show the whole baseline with room round it: about this
// many globe radii of altitude per degree of baseline, and never closer than the
// minimum. Closer than ~0.34 the 4096-px Earth image is magnified past 3.5x and its
// relief turns to mush; at 0.34 a 295 km beam is ~110 px long, which still carries
// its glow and labels.
const BEAM_FOCUS_ALTITUDE_PER_DEG = 0.062;
const BEAM_FOCUS_ALTITUDE_MIN = 0.34;
// An unselected beam's label needs its arc on screen to be at least as long as
// the label's shortest form (the distance alone, ~50 px) and never under this many
// pixels: a pill with no arc beside it is only noise. The full name needs the arc
// to be nearly as long as the name.
const BEAM_LABEL_MIN_PX = 26;

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

/** Great-circle angle in degrees (angularDistDeg below is a flat lat/lon
 * distance, good enough for clustering but wrong near the poles). */
function greatCircleDeg(aLat, aLon, bLat, bLon) {
  const rad = Math.PI / 180;
  const dLat = (bLat - aLat) * rad;
  const dLon = lonDelta(bLon, aLon) * rad;
  const h = Math.sin(dLat / 2) ** 2
    + Math.cos(aLat * rad) * Math.cos(bLat * rad) * Math.sin(dLon / 2) ** 2;
  return (2 * Math.asin(Math.min(1, Math.sqrt(h)))) / rad;
}

// ---- beam helpers --------------------------------------------------------------
// A baseline row is `{ from_site_id, to_site_id, distance: { value, unit, display,
// approx }, status? }`. The globe never invents a distance: the label formats the
// recorded value (the full `display`, with its uncertainty, is in the panel and the
// tooltip), and a row without a value is labelled with its endpoints alone.

/** The baseline's length in km, or null when no usable value is recorded. */
export function baselineKm(distance) {
  if (!distance || typeof distance.value !== 'number' || !Number.isFinite(distance.value)) return null;
  const unit = String(distance.unit || 'km').toLowerCase();
  if (unit === 'km') return distance.value;
  if (unit === 'm') return distance.value / 1000;
  if (unit === 'mi' || unit === 'mile' || unit === 'miles') return distance.value * 1.609344;
  return null;
}

/** "295 km", "1,285 km", "~810 km" for an approximate figure. */
export function formatBaselineKm(km, approx) {
  const rounded = km >= 100 ? Math.round(km) : Math.round(km * 10) / 10;
  return `${approx ? '~' : ''}${rounded.toLocaleString('en-US')} km`;
}

const ENDED_STATUSES = new Set(['completed', 'decommissioned', 'cancelled']);

// How a lifecycle status reads in a beam's label and tooltip. `active` is the only
// status drawn as a live, flowing beam; every other one is drawn quieter.
const BEAM_STATUS_PHRASE = {
  construction: 'under construction',
  commissioning: 'commissioning',
  approved: 'approved, not built',
  proposed: 'proposed',
  planned: 'planned',
  completed: 'completed',
  decommissioned: 'decommissioned',
  shutdown: 'shut down',
  upgrade: 'in upgrade shutdown',
  cancelled: 'cancelled',
};
export function beamStatusPhrase(status) {
  if (!status || status === 'active') return '';
  return BEAM_STATUS_PHRASE[status] || String(status).replace(/_/g, ' ');
}

function stripParen(text) {
  return String(text || '').replace(/\s*\([^)]*\)/g, '').trim();
}

/** A short name for a facility or site: its own name when it fits, else the first
 * alias that does ("Fermi National Accelerator Laboratory" -> "Fermilab"). */
export function shortPlaceName(record, max = 20) {
  if (!record) return '';
  const name = stripParen(record.name);
  if (name && name.length <= max) return name;
  for (const alias of record.aliases || []) {
    const short = stripParen(alias);
    if (short.length >= 3 && short.length <= max) return short;
  }
  return name.length > max ? `${name.slice(0, max - 1).trimEnd()}…` : name;
}

/** A detector's short name: "Super-Kamiokande detector" -> "Super-K" through its
 * aliases, "MINOS far detector" -> "MINOS". */
export function shortDetectorName(record) {
  const clean = (text) => stripParen(text).replace(/\s+((far|near)\s+)?detector$/i, '').trim();
  const candidates = [record.name, ...(record.aliases || [])].map(clean).filter((t) => t.length >= 4);
  candidates.sort((a, b) => a.length - b.length);
  return candidates[0] || stripParen(record.name);
}

function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]));
}

// ---- fitting the camera to a set of places ---------------------------------
// Opening a topic mutes every marker but the ones it is about; the camera should
// go where they are. `fitView` answers where: the centre of the set and an
// altitude that shows all of it. A set that spans most of the globe cannot be
// shown whole at any altitude the overview uses, and flying in on part of it
// would hide the rest, so the view then only turns to its densest region (the
// most points within FIT_DENSE_RADIUS_DEG) and stays at overview height.
const FIT_MAX_ALTITUDE = 2.4; // the opening overview
const FIT_MIN_ALTITUDE = FOCUS_ALTITUDE;
const FIT_OVERVIEW_ALTITUDE = 2;
const FIT_DENSE_RADIUS_DEG = 25;

function unitVector(lat, lon) {
  const rad = Math.PI / 180;
  return [Math.cos(lat * rad) * Math.cos(lon * rad), Math.cos(lat * rad) * Math.sin(lon * rad), Math.sin(lat * rad)];
}

function centreOf(points) {
  const sum = [0, 0, 0];
  for (const p of points) {
    const v = unitVector(p.lat, p.lon);
    sum[0] += v[0];
    sum[1] += v[1];
    sum[2] += v[2];
  }
  const norm = Math.hypot(...sum);
  if (norm < 1e-9) return { lat: points[0].lat, lon: points[0].lon };
  const deg = 180 / Math.PI;
  return { lat: Math.asin(sum[2] / norm) * deg, lon: Math.atan2(sum[1], sum[0]) * deg };
}

// The camera altitude whose visible cap (half-angle acos(1 / (1 + altitude)))
// covers `spreadDeg` around the centre with a margin.
function altitudeForSpread(spreadDeg) {
  const half = clamp(spreadDeg * 1.3 + 6, 10, 85) * (Math.PI / 180);
  return clamp(1 / Math.cos(half) - 1, FIT_MIN_ALTITUDE, FIT_MAX_ALTITUDE);
}

/** `{ lat, lon, altitude, whole }` for a set of `{lat, lon}` places: the view
 * that shows all of them, or, when they span most of the globe (`whole` false),
 * the overview turned to their densest region. null for an empty set. */
export function fitView(points) {
  if (!points || !points.length) return null;
  const centre = centreOf(points);
  const spread = Math.max(...points.map((p) => greatCircleDeg(centre.lat, centre.lon, p.lat, p.lon)));
  const half = clamp(spread * 1.3 + 6, 10, 85);
  const needed = 1 / Math.cos(half * (Math.PI / 180)) - 1;
  if (needed <= FIT_MAX_ALTITUDE) return { ...centre, altitude: altitudeForSpread(spread), whole: true };
  let best = null;
  for (const anchor of points) {
    const near = points.filter((p) => greatCircleDeg(anchor.lat, anchor.lon, p.lat, p.lon) <= FIT_DENSE_RADIUS_DEG);
    if (!best || near.length > best.length) best = near;
  }
  return { ...centreOf(best), altitude: FIT_OVERVIEW_ALTITUDE, whole: false };
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
  // `animateIn` scales and spins the globe into place over ~1 s at start-up
  // (markers glide ~100 px with the camera standing still): skip it for a
  // reader who asked for reduced motion.
  const globe = Globe({ animateIn: !reducedMotion() })(container)
    .backgroundColor('rgba(0,0,0,0)')
    .showAtmosphere(true)
    .atmosphereColor(ATMOSPHERE_COLOR)
    .atmosphereAltitude(ATMOSPHERE_ALTITUDE)
    // The first paint, before the Earth image arrives (and the look if it never
    // does): the same dark slate land on navy ocean as the image's own ramps, so
    // the swap to the relief reads as detail arriving, not as a change of colour.
    .polygonCapColor(() => BASE_LAND_COLOR)
    .polygonSideColor(() => 'rgba(0,0,0,0)')
    .polygonStrokeColor(() => BASE_COAST_COLOR)
    .polygonAltitude(0.006)
    .htmlAltitude((d) => d.altitude)
    .htmlElement((d) => d.el)
    // three-globe tweens a marker to its new position over 1 s whenever the
    // layer is rebuilt (a cluster re-forming moved ~130 px on load): motion a
    // reader who asked for reduced motion must not get.
    .htmlTransitionDuration(reducedMotion() ? 0 : 1000)
    .arcsData([])
    .arcStartLat((d) => d.startLat)
    .arcStartLng((d) => d.startLng)
    .arcEndLat((d) => d.endLat)
    .arcEndLng((d) => d.endLng)
    .arcColor((d) => (d.selected ? d.colorSelected : d.color))
    .arcStroke((d) => (d.selected ? d.strokeSelected : d.stroke))
    .arcAltitude((d) => (d.altitude == null ? null : d.altitude))
    .arcLabel((d) => d.label)
    .arcAltitudeAutoScale(0.35)
    // Dash motion re-animates an arc's material on every rendered frame
    // regardless of user interaction; with a couple hundred institution arcs
    // this was a standing, avoidable cost (REVIEW_performance.md P1-3), so only
    // the handful of beam arcs flow — and not at all for a reader who asked for
    // reduced motion, who gets the same dashes standing still. An institution
    // arc's static dash still reads as directional without the redraw.
    .arcDashLength((d) => (d.beamline ? d.dashLength : 0.4))
    .arcDashGap((d) => (d.beamline ? d.dashGap : 0.18))
    .arcDashAnimateTime((d) => (d.beamline && d.flow && !reducedMotion() ? BEAM_FLOW_MS : 0))
    .onArcClick((d) => {
      // A beam arc opens its beamline, like its label does.
      if (d && d.beamline && onSelect) onSelect({ type: 'beamline', slug: d.beamline.id.split(':')[1] });
    })
    .arcsTransitionDuration(0)
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
      mat.color.setStyle(BASE_OCEAN_COLOR);
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
    motionQuery.addEventListener('change', () => {
      if (reducedMotion()) stopAutoRotate();
      globe.htmlTransitionDuration(reducedMotion() ? 0 : 1000);
      rebuildVisibleLayer(); // re-reads each beam arc's flow
    });
  }

  fetch('/atlas/vendor/land-110m.json').then((r) => r.json()).then((land) => {
    globe.polygonsData(land.features || []);
  }).catch(() => {});

  // ---- scenery: the shaded-relief Earth and the country lines ------------------
  // Both are fetched only after the globe has painted, so neither delays the
  // first frame, and either failing leaves the globe as it was: the flat land
  // polygons stay until the Earth image is in place, and keep their own coast
  // stroke until the line work is.
  let earthApplied = false;
  let bordersApplied = false;
  function syncScenery() {
    if (earthApplied) {
      // The picture is the land now: no flat fill over it. Its coasts come from
      // the line layer, or, if that never arrives, from the polygons' outline.
      globe.polygonCapColor(() => 'rgba(0,0,0,0)');
      if (bordersApplied) globe.polygonsData([]);
      else globe.polygonStrokeColor(() => COAST_COLOR);
    } else if (bordersApplied) {
      // The coastline now comes from the path layer; drop the land polygons' own
      // (dark, doubled) outline.
      globe.polygonStrokeColor(() => null);
    }
  }

  let earthRequested = false;
  function loadEarthTexture() {
    if (earthRequested) return;
    earthRequested = true;
    fetch(EARTH_URL)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.blob();
      })
      .then((blob) => new Promise((resolve, reject) => {
        // Decode it here first: a corrupt or truncated file is found out before
        // the globe is told to use it. The blob URL (an object of this page, so
        // inside the CSP's img-src) also spares three.js a second request.
        const url = URL.createObjectURL(blob);
        const image = new Image();
        image.onload = () => resolve(url);
        image.onerror = () => { URL.revokeObjectURL(url); reject(new Error('earth image did not decode')); };
        image.src = url;
      }))
      .then((url) => {
        globe.globeImageUrl(url);
        // three-globe attaches the texture when its own loader finishes (a frame
        // or two later); swap the scenery when it has, not before, so the globe
        // never shows a bare sphere.
        let tries = 0;
        const wait = () => {
          let ready = false;
          try { ready = !!globe.globeMaterial().map; } catch (error) { ready = false; }
          if (ready) {
            earthApplied = true;
            syncScenery();
            URL.revokeObjectURL(url);
          } else if ((tries += 1) < 120) {
            window.requestAnimationFrame(wait);
          }
        };
        window.requestAnimationFrame(wait);
      })
      .catch(() => {});
  }

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
        bordersApplied = true;
        syncScenery();
      })
      .catch(() => {});
  }

  // --- marker model -------------------------------------------------
  const markerEls = new Map(); // id -> element
  const markerMeta = new Map(); // id -> { segments, tier, route }
  const beamEls = new Map(); // arc id -> { outer, pill, leader, arc, text, shortText }
  let arcsEnabled = false;
  let arcsForcedOff = false; // true once a collaboration exceeds INSTITUTION_ARC_THRESHOLD
  let beamArcs = [];
  let highlightSet = null;
  let currentAltitude = 2.4;
  // What the open panel is about: the entity id, the globe markers that stand
  // for it (highlighted, kept out of clusters, always captioned) and, for an
  // institution, its id (its markers are ids of the form `<collab>::<id>`).
  let selection = {
    id: null, markerIds: new Set(), beamlineIds: new Set(), institutionId: null, anchor: null, altitude: FOCUS_ALTITUDE,
  };
  let filterState = filtersModule.emptyFilterState();
  const topicIndex = filtersModule.buildTopicIndex(atlas.topics || {});
  const siteExperimentIndex = filtersModule.buildSiteExperimentIndex(atlas);

  function makeInteractiveElement({
    id, name, ariaLabel, size, shape, kind, color, hollow, hatched, approximate, tier, extraClass, onActivate,
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
      shape, kind, color, size, hollow, hatched, approximate,
    }));
    const label = document.createElement('span');
    label.className = 'atlas-marker-label';
    label.textContent = name;
    el.appendChild(label);
    // A selected caption that had to move off its marker (see declutterLabels) is
    // tied back to it by this line.
    const leader = document.createElement('span');
    leader.className = 'atlas-marker-leader';
    leader.setAttribute('aria-hidden', 'true');
    el.appendChild(leader);
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
    id, name, route, size, shape, kind, color, hollow, hatched, approximate, tier,
  }) {
    return makeInteractiveElement({
      id,
      name,
      size,
      shape,
      kind,
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
      color: cssToken('--amber', '#f2b441'),
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

  // ---- beams: one arc per baseline row ------------------------------------------
  // The far end of a beam is named for the detector there when the site holds a
  // single far (else main) detector — "Super-K", "MINOS" — and for the facility
  // when it holds several (LNGS Hall C, the DUNE caverns): never a guess.
  const detectorsBySite = new Map();
  for (const detector of Object.values(atlas.detectors || {})) {
    for (const placement of detector.placements || []) {
      if (!placement.site_id) continue;
      const list = detectorsBySite.get(placement.site_id) || [];
      list.push({ record: detector, role: placement.role });
      detectorsBySite.set(placement.site_id, list);
    }
  }
  function siteFacility(siteId, fallbackFacilityId) {
    const site = atlas.sites && atlas.sites[siteId];
    const facilityId = (site && site.facility_id) || fallbackFacilityId;
    return (atlas.facilities && atlas.facilities[facilityId]) || null;
  }
  function farEndName(siteId, beamlineFacilityId) {
    const placed = detectorsBySite.get(siteId) || [];
    let pool = placed.filter((p) => p.role === 'far');
    if (!pool.length) pool = placed.filter((p) => p.role === 'main');
    if (pool.length === 1) return shortDetectorName(pool[0].record);
    return shortPlaceName(siteFacility(siteId, beamlineFacilityId)) || shortPlaceName(atlas.sites && atlas.sites[siteId]);
  }

  function buildBeamArcs() {
    const out = [];
    for (const beamline of Object.values(atlas.beamlines || {})) {
      (beamline.baselines || []).forEach((baseline, row) => {
        const from = siteCoords(baseline.from_site_id);
        const to = siteCoords(baseline.to_site_id);
        if (!from || !to) return;
        const spanDeg = greatCircleDeg(from.lat, from.lon, to.lat, to.lon);
        const recordedKm = baselineKm(baseline.distance);
        // Under BEAM_MIN_KM (BNB's 110 m, NuMI's near hall) the arc would be a dot
        // on top of its own marker: those baselines belong on the local map.
        // Coordinates that fall on the same point cannot be drawn at all.
        if ((recordedKm != null && recordedKm < BEAM_MIN_KM) || spanDeg * KM_PER_DEG < BEAM_MIN_KM / 3) return;
        const approx = !!(baseline.distance && baseline.distance.approx);
        const km = recordedKm;
        const sites = atlas.sites || {};
        const fromName = (sites[baseline.from_site_id] || {}).name || baseline.from_site_id;
        const toName = (sites[baseline.to_site_id] || {}).name || baseline.to_site_id;
        const source = shortPlaceName(siteFacility(baseline.from_site_id, beamline.facility_id))
          || shortPlaceName(sites[baseline.from_site_id]);
        const far = farEndName(baseline.to_site_id, beamline.facility_id);
        const distanceText = km == null ? '' : formatBaselineKm(km, approx);
        const mid = centreOf([{ lat: from.lat, lon: from.lon }, { lat: to.lat, lon: to.lon }]);
        out.push({
          id: `${beamline.id}:${baseline.from_site_id}:${baseline.to_site_id}:${row}`,
          kind: 'beam',
          beamline,
          baselineStatus: baseline.status || null,
          startLat: from.lat,
          startLng: from.lon,
          endLat: to.lat,
          endLng: to.lon,
          spanDeg,
          mid: { lat: mid.lat, lng: mid.lon },
          rank: 0,
          fromName,
          toName,
          distanceDisplay: baseline.distance ? baseline.distance.display || distanceText : '',
          nameText: `${source} → ${far}`,
          distanceText,
        });
      });
    }
    // Baselines that begin and end at (nearly) the same places — T2K's Super-K and
    // T2HK's Hyper-K arcs leave J-PARC together and land 8 km apart — would be drawn
    // on top of each other. Each further arc in such a bundle rides higher.
    const SAME_PLACE_DEG = 0.3;
    out.sort((a, b) => (a.id < b.id ? -1 : 1));
    for (let i = 0; i < out.length; i += 1) {
      for (let j = 0; j < i; j += 1) {
        const a = out[j];
        const b = out[i];
        if (greatCircleDeg(a.startLat, a.startLng, b.startLat, b.startLng) <= SAME_PLACE_DEG
          && greatCircleDeg(a.endLat, a.endLng, b.endLat, b.endLng) <= SAME_PLACE_DEG) {
          b.rank = Math.max(b.rank, a.rank + 1);
        }
      }
    }
    for (const arc of out) {
      // three-globe's arc rises to 1.125 x its `altitude` at mid-span.
      arc.altitude = clamp(0.42 * (arc.spanDeg * Math.PI) / 180, 0.012, 0.3) * (1 + 0.6 * arc.rank);
      arc.apex = 1.125 * arc.altitude;
    }
    return out;
  }

  /** The beam arc's state for the current timeline selection: null when its
   * beamline had not yet begun then (the arc is not drawn), else the status it is
   * drawn in. A beam that has ended stays on the globe as a completed one — CNGS
   * and K2K are history, not absent — while a baseline row's own status wins over
   * its beamline's: the Hyper-K arm is under construction while the beamline it
   * hangs from is running. */
  function beamStatus(arc) {
    const { beamline } = arc;
    let status = beamline.status || 'active';
    if (timelineMode && beamline.state_segments && beamline.state_segments.length) {
      const present = segmentsPresence(beamline.state_segments);
      if (present) {
        status = present.status;
      } else if (timelineAbsenceReason(beamline.state_segments, filterTimelineState()) === 'ended') {
        status = ENDED_STATUSES.has(beamline.status) ? beamline.status : 'completed';
      } else {
        // Not yet built in the selected year: drawn only for the beam a panel is
        // open on, which the panel itself explains.
        return selection.beamlineIds.has(beamline.id) ? 'absent' : null;
      }
    }
    if (arc.baselineStatus) status = arc.baselineStatus;
    return status;
  }

  /** The tube diameter, in degrees of arc, that shows `px` pixels at the current
   * camera altitude (the vertical field of view is 50 degrees). */
  function beamStrokeDeg(px) {
    const height = Math.max(200, container.clientHeight || 700);
    return Math.max(0.004, (px * 2 * Math.tan((25 * Math.PI) / 180) * Math.max(currentAltitude, 0.05) * (180 / Math.PI)) / height);
  }

  /** Styles one arc for its status and selection, in place (three-globe reads
   * these back through the accessors set up with the globe). Returns the arc. */
  function styleBeamArc(arc, status) {
    const quiet = status !== 'active';
    const phrase = status === 'absent' ? 'not yet built in the selected year' : beamStatusPhrase(status);
    arc.status = status;
    arc.quiet = quiet;
    arc.statusPhrase = phrase;
    arc.selected = selection.beamlineIds.has(arc.beamline.id);
    arc.flow = !quiet;
    arc.dashLength = quiet ? 0.03 : 0.1;
    arc.dashGap = quiet ? 0.05 : 0.07;
    arc.color = quiet ? BEAM_COLOR_QUIET : BEAM_COLOR;
    arc.colorSelected = quiet ? BEAM_COLOR_QUIET_SELECTED : BEAM_COLOR_SELECTED;
    arc.stroke = beamStrokeDeg(quiet ? BEAM_PX_QUIET : BEAM_PX);
    arc.strokeSelected = beamStrokeDeg(quiet ? BEAM_PX_QUIET_SELECTED : BEAM_PX_SELECTED);
    // The glow under a live beam shares its geometry, tooltip and click.
    if (!quiet) {
      const glow = arc.glow || (arc.glow = {
        kind: 'beam-glow', beamline: arc.beamline, dashLength: 1, dashGap: 0, flow: false,
      });
      Object.assign(glow, {
        startLat: arc.startLat,
        startLng: arc.startLng,
        endLat: arc.endLat,
        endLng: arc.endLng,
        altitude: arc.altitude,
        selected: arc.selected,
        color: BEAM_GLOW_COLOR,
        colorSelected: BEAM_GLOW_COLOR_SELECTED,
        stroke: beamStrokeDeg(BEAM_GLOW_PX),
        strokeSelected: beamStrokeDeg(BEAM_GLOW_PX_SELECTED),
      });
    }
    const lines = [`${escapeHtml(arc.beamline.name)}`, `${escapeHtml(arc.fromName)} → ${escapeHtml(arc.toName)}`];
    if (arc.distanceDisplay) lines.push(`${escapeHtml(arc.distanceDisplay)} baseline`);
    if (phrase) lines.push(`<em>${escapeHtml(phrase)}</em>`);
    arc.label = lines.join('<br>');
    if (arc.glow) arc.glow.label = arc.label;
    return arc;
  }

  function makeBeamLabelElement(arc) {
    const outer = document.createElement('div');
    outer.className = 'atlas-beam-label';
    const pill = document.createElement('div');
    pill.className = 'bl-pill';
    pill.setAttribute('role', 'button');
    pill.setAttribute('tabindex', '0');
    const phrase = arc.statusPhrase ? `, ${arc.statusPhrase}` : '';
    const text = `${arc.nameText}${arc.distanceText ? ` · ${arc.distanceText}` : ''}${arc.statusPhrase ? ` · ${arc.statusPhrase}` : ''}`;
    const aria = `${arc.beamline.name}: ${arc.fromName} to ${arc.toName}`
      + `${arc.distanceDisplay ? `, ${arc.distanceDisplay} baseline` : ''}${phrase}. Press Enter to open the beamline.`;
    pill.setAttribute('aria-label', aria);
    pill.title = aria.replace(/\. Press Enter.*$/, '');
    const long = document.createElement('span');
    long.className = 'bl-long';
    long.textContent = text;
    const short = document.createElement('span');
    short.className = 'bl-short';
    short.textContent = arc.distanceText || arc.nameText;
    pill.appendChild(long);
    pill.appendChild(short);
    const leader = document.createElement('span');
    leader.className = 'bl-leader';
    leader.setAttribute('aria-hidden', 'true');
    outer.appendChild(leader);
    outer.appendChild(pill);
    const open = () => {
      if (onSelect) onSelect({ type: 'beamline', slug: arc.beamline.id.split(':')[1] });
    };
    pill.addEventListener('click', open);
    pill.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        open();
      }
    });
    return {
      outer, pill, leader, arc, text, shortText: short.textContent,
    };
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
    lastRebuildAt = performance.now();
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
    //
    // A facility that does not exist in the selected year or range is hidden
    // (is-absent), so it must not be counted in, or named by, a cluster either:
    // only the members present in the selection are clustered; the absent ones
    // stay as (hidden) single markers, which is what they are on their own.
    const absentInSelection = (f) => !!timelineMode
      && !!(f.record.state_segments && f.record.state_segments.length)
      && !segmentsPresence(f.record.state_segments);
    const presentFacilities = clusterableFacilities.filter((f) => !absentInSelection(f));
    const absentFacilities = clusterableFacilities.filter(absentInSelection);
    const facilityClustered = (currentAltitude >= FACILITY_CLUSTER_ALTITUDE && currentAltitude > MIN_CLUSTER_ALTITUDE)
      ? clusterByRadius(presentFacilities, facilityClusterRadiusDeg(currentAltitude))
      : presentFacilities.map((f) => ({ kind: 'single', lat: f.lat, lon: f.lon, item: f }));
    for (const f of absentFacilities) {
      facilityClustered.push({ kind: 'single', lat: f.lat, lon: f.lon, item: f });
    }
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
          // Sized by how many experiments the facility hosts, so the major
          // laboratories read first.
          size: facilityGlyphSize((record.experiment_ids || []).length),
          shape: info.shape,
          kind: record.kind,
          color: info.color,
          hollow: false,
          hatched: uncertain,
          approximate: entry.item.approximate,
          tier: 'facility',
        });
        markerEls.set(record.id, el);
        // `weight` ranks captions in declutterLabels: a facility that hosts more
        // experiments keeps its name when two would collide.
        markerMeta.set(record.id, {
          segments: record.state_segments, tier: 'facility', weight: (record.experiment_ids || []).length,
        });
        applyTimelineClasses(el, record.state_segments);
        htmlLayer.push({
          id: record.id, lat: entry.lat, lng: entry.lon, altitude: 0.02, el,
        });
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
        markerMeta.set(id, { segments: null, tier: 'facility', cluster: true, weight: entry.items.length });
        htmlLayer.push(marker);
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
      markerMeta.set(site.id, {
        segments: site.record.state_segments, tier: 'site', weight: (siteExperimentIndex.get(site.id) || []).length,
      });
      applyTimelineClasses(el, site.record.state_segments);
      htmlLayer.push({
        id: site.id, lat: site.lat, lng: site.lon, altitude: 0.012, el,
      });
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
          color: cssToken('--amber', '#f2b441'),
          hollow,
          tier: 'institution',
        });
        el.dataset.collaboration = institutionCollaborationId;
        markerEls.set(id, el);
        markerMeta.set(id, { segments: null, tier: 'institution', weight: 0 });
        htmlLayer.push({
          id, lat: entry.lat, lng: entry.lon, altitude: 0.015, el,
        });
        if (hostCoords) {
          instArcs.push({
            id: `conn:${id}`,
            startLat: hostCoords.lat,
            startLng: hostCoords.lon,
            endLat: entry.lat,
            endLng: entry.lon,
            color: [withAlpha(cssToken('--amber', '#f2b441'), 0.55), withAlpha(cssToken('--amber', '#f2b441'), 0.05)],
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
        markerMeta.set(id, { segments: null, tier: 'institution', cluster: true, weight: entry.items.length });
        htmlLayer.push(marker);
        if (hostCoords) {
          instArcs.push({
            id: `conn:${id}`,
            startLat: hostCoords.lat,
            startLng: hostCoords.lon,
            endLat: entry.lat,
            endLng: entry.lon,
            color: [withAlpha(cssToken('--amber', '#f2b441'), 0.55), withAlpha(cssToken('--amber', '#f2b441'), 0.05)],
            stroke: 0.25,
            label: `${entry.items.length} institutions ↔ collaboration host`,
          });
        }
      }
    }

    // ---- captions carry over a rebuild ------------------------------------
    // A rebuild replaces every marker element. Starting the new ones with the
    // caption decisions of the last declutter pass (and unknown facilities
    // hidden until the next pass reveals them) means captions do not flash
    // cluttered for a frame and then disappear. Clusters keep their count.
    for (const [id, el] of markerEls) {
      const meta = markerMeta.get(id);
      if (meta.cluster || meta.tier !== 'facility' || isSelectedMarker(id)) continue;
      const hidden = labelHidden.has(id) ? labelHidden.get(id) : true;
      if (hidden) el.classList.add('is-label-hidden');
    }

    // ---- highlight (topic mode) carries over the rebuild --------------
    if (highlightSet) {
      for (const [id, el] of markerEls) {
        const lit = isHighlighted(id);
        el.classList.toggle('is-highlighted', lit);
        el.classList.toggle('is-muted', !lit);
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

    for (const d of htmlLayer) markerMeta.get(d.id).pos = { lat: d.lat, lng: d.lng };

    // ---- beams: an arc per baseline row, its label riding at mid-arc ------------
    const arcs = [];
    beamEls.clear();
    const beamLayer = [];
    for (const arc of beamArcs) {
      const status = beamStatus(arc);
      if (status == null) continue; // the beamline did not exist in the selected year
      styleBeamArc(arc, status);
      if (!arc.quiet) arcs.push(arc.glow); // under the beam itself
      arcs.push(arc);
      const parts = makeBeamLabelElement(arc);
      if (arc.selected) parts.outer.classList.add('is-selected');
      if (arc.quiet) parts.outer.classList.add('is-quiet');
      const wasHidden = labelHidden.get(`beam:${arc.id}`);
      if (!arc.selected && wasHidden !== false) parts.outer.classList.add('is-label-hidden');
      beamEls.set(arc.id, parts);
      beamLayer.push({
        id: `beam:${arc.id}`, lat: arc.mid.lat, lng: arc.mid.lng, altitude: arc.apex, el: parts.outer,
      });
    }

    globe.htmlElementsData(htmlLayer.concat(beamLayer));
    // Marker boxes only get their screen positions on the next rendered frame,
    // so caption decluttering waits for it.
    scheduleDeclutter(DECLUTTER_DELAY_MS);

    // ---- arcs: capped to what's actually drawn (never the full roster —
    // only the currently visible/clustered institution markers get an arc).
    // The >INSTITUTION_ARC_THRESHOLD *default*-off behaviour is enforced by
    // app.js resetting the `arcs` URL/UI state when a large collaboration is
    // first entered (isArcsForcedOff()); the toggle itself always reflects
    // and controls what's actually drawn here, so it never lies to the user.
    if (arcsEnabled) arcs.push(...instArcs);
    globe.arcsData(arcs);
  }

  function reapplyTimeline() {
    rebuildVisibleLayer();
  }

  // ---- camera-driven work, throttled -----------------------------------
  // `onZoom` fires for every camera movement — a drag, a damped coast, a
  // programmatic flight — once per animation frame. Re-clustering (a full DOM
  // rebuild) and re-measuring labels at that rate is wasted work, so both run
  // at most every ~100 ms with a trailing call, which always fires after the
  // last movement and so always sees the camera's final position.
  let lastRebuildAt = 0;
  let rebuildTimer = null;
  function scheduleRebuild() {
    if (rebuildTimer) return;
    const wait = Math.max(0, REBUILD_THROTTLE_MS - (performance.now() - lastRebuildAt));
    rebuildTimer = window.setTimeout(() => {
      rebuildTimer = null;
      rebuildVisibleLayer();
    }, wait);
  }

  globe.onZoom(({ altitude }) => {
    if (Math.abs(altitude - currentAltitude) >= 0.01) {
      currentAltitude = altitude;
      scheduleRebuild();
    }
    scheduleDeclutter(DECLUTTER_DELAY_MS);
  });

  // ---- caption decluttering ---------------------------------------------
  // Facility names are drawn under their glyph. In dense regions (Europe, the
  // US west, Japan) the captions collide with each other and with other
  // markers, so after each camera change we measure what is actually on screen
  // and hide the caption of any marker whose box would overlap one that
  // matters more. Priority: selected > hovered/focused > cluster badge >
  // facilities hosting more experiments > everything else. A hidden caption is
  // `visibility: hidden` (class `is-label-hidden`), never removed: the marker
  // keeps its glyph and its click/focus target, and the caption returns on
  // hover or keyboard focus (atlas.css). Markers on the far side of the globe
  // are display:none (CSS2DRenderer), have no box, and so never take part.
  let declutterTimer = null;
  // marker id -> last decision (true = caption hidden); read by the next rebuild.
  const labelHidden = new Map();
  function scheduleDeclutter(delay) {
    if (declutterTimer) return;
    declutterTimer = window.setTimeout(() => {
      // CSS2DRenderer attaches and positions a marker on a rendered frame, so
      // measure two animation frames from now: by then the globe's own loop has
      // drawn at least once since whatever scheduled this (a rebuild's fresh
      // markers have no screen position until it has).
      window.requestAnimationFrame(() => window.requestAnimationFrame(() => {
        declutterTimer = null;
        declutterLabels();
      }));
    }, delay);
  }

  const LABEL_PAD = 1; // px of breathing room between captions (each side)
  function padded(r) {
    return {
      left: r.left - LABEL_PAD, top: r.top - LABEL_PAD, right: r.right + LABEL_PAD, bottom: r.bottom + LABEL_PAD,
    };
  }
  function overlaps(a, b) {
    return a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;
  }
  function boxAt(cx, cy, w, h) {
    return padded({
      left: cx - w / 2, top: cy - h / 2, right: cx + w / 2, bottom: cy + h / 2,
    });
  }
  /** A rectangle against a circle (a selection ring). */
  function hitsCircle(rect, cx, cy, radius) {
    const nx = Math.min(Math.max(cx, rect.left), rect.right);
    const ny = Math.min(Math.max(cy, rect.top), rect.bottom);
    return (nx - cx) ** 2 + (ny - cy) ** 2 < radius * radius;
  }

  // The selection halo reaches this far past the glyph's edge (atlas.css).
  const RING_REACH = 12;

  /** Centres, relative to an anchor, at which a `w` x `h` caption can sit clear of
   * a circle of radius `r` around it: the usual place first, then the other sides,
   * the corners, and finally columns stacked further out. */
  function captionOffsets(r, w, h, preferAbove) {
    const gap = 2;
    const step = h + 3;
    const down = r + gap + h / 2;
    const up = -down;
    const side = r + gap + w / 2;
    const diagX = r * 0.72 + w / 2;
    const diagY = r * 0.72 + h / 2;
    const list = preferAbove
      ? [[0, up], [0, down], [side, 0], [-side, 0], [diagX, -diagY], [-diagX, -diagY], [diagX, diagY], [-diagX, diagY]]
      : [[0, down], [0, up], [side, 0], [-side, 0], [diagX, diagY], [-diagX, diagY], [diagX, -diagY], [-diagX, -diagY]];
    for (let k = 1; k <= 6; k += 1) {
      const lift = k * step;
      const above = [[0, up - lift], [side, -lift], [-side, -lift]];
      const below = [[0, down + lift], [side, lift], [-side, lift]];
      list.push(...(preferAbove ? [...above, ...below] : [...below, ...above]));
    }
    return list;
  }

  /** Where the caption of a selected marker or beam goes: the first of the
   * candidate places that is on the stage and clear of every caption already
   * placed and every selection ring; a first pass also keeps clear of the other
   * facilities' glyphs, a second gives that up before giving up the caption. */
  function placeCaption({
    cx, cy, radius, w, h, preferAbove, stage, placed, rings, glyphs,
  }) {
    const inStage = (r) => r.left >= stage.left + 2 && r.right <= stage.right - 2
      && r.top >= stage.top + 2 && r.bottom <= stage.bottom - 2;
    const offsets = captionOffsets(radius, w, h, preferAbove);
    for (const clearOfGlyphs of [true, false]) {
      for (let i = 0; i < offsets.length; i += 1) {
        let [dx, dy] = offsets[i];
        let box = boxAt(cx + dx, cy + dy, w, h);
        // A caption wider than the room beside its marker (a phone) slides along
        // the row until it is on the stage; its leader line ties it back.
        let slid = false;
        if (box.left < stage.left + 2 && w <= stage.width - 4) {
          dx += stage.left + 2 - box.left;
          slid = true;
        } else if (box.right > stage.right - 2 && w <= stage.width - 4) {
          dx -= box.right - (stage.right - 2);
          slid = true;
        }
        if (slid) box = boxAt(cx + dx, cy + dy, w, h);
        if (!inStage(box)) continue;
        if (placed.some((r) => overlaps(box, r))) continue;
        if (rings.some((ring) => hitsCircle(box, ring.cx, ring.cy, ring.r))) continue;
        if (clearOfGlyphs && glyphs.some((g) => overlaps(box, g))) continue;
        return {
          dx, dy, index: i, moved: i > 0 || slid, box,
        };
      }
    }
    return null;
  }

  // Width of a beam label's text, to choose between its two forms without
  // touching the DOM. The font is read once, from the first label built.
  let beamFont = null;
  let measureContext = null;
  const widthCache = new Map();
  function beamTextWidth(text, pill) {
    if (!beamFont) {
      const css = window.getComputedStyle(pill);
      beamFont = `${css.fontWeight} ${css.fontSize} ${css.fontFamily}`;
    }
    const key = `${beamFont}|${text}`;
    if (widthCache.has(key)) return widthCache.get(key);
    if (!measureContext) measureContext = document.createElement('canvas').getContext('2d');
    let width = text.length * 6.4;
    if (measureContext) {
      measureContext.font = beamFont;
      width = measureContext.measureText(text).width;
    }
    widthCache.set(key, width);
    return width;
  }
  const BEAM_PILL_PAD = 20; // horizontal padding + border of .bl-pill (globe.css)
  const BEAM_PILL_HEIGHT = 24;

  function declutterLabels() {
    if (!markerEls.size && !beamEls.size) return;
    const stage = container.getBoundingClientRect();
    if (!stage.width || !stage.height) return;
    const items = [];
    const pov = globe.pointOfView();
    const limbDeg = LIMB_LABEL_FRACTION * (Math.acos(1 / (1 + pov.altitude)) * 180) / Math.PI;
    // ---- reads only (no style writes until every box is measured) ----------
    for (const [id, el] of markerEls) {
      const meta = markerMeta.get(id) || {};
      // A marker on the far side of the globe is never attached (or is
      // display:none): no box, so it takes no part.
      if (!el.isConnected || !el.style.transform) continue;
      const glyph = el.getBoundingClientRect();
      if (!glyph.width && !glyph.height) continue;
      if (glyph.right < stage.left || glyph.left > stage.right
        || glyph.bottom < stage.top || glyph.top > stage.bottom) continue; // off screen
      const selected = el.classList.contains('is-selected');
      const hovered = el.matches(':hover') || el === document.activeElement;
      const cluster = !!meta.cluster;
      const labelled = selected || hovered || cluster || meta.tier === 'facility';
      const label = labelled ? el.querySelector('.atlas-marker-label') : null;
      const nearLimb = !!meta.pos
        && greatCircleDeg(pov.lat, pov.lng, meta.pos.lat, meta.pos.lng) > limbDeg;
      items.push({
        type: 'marker',
        nearLimb,
        el, selected, hovered, cluster, meta, glyph: padded(glyph),
        cx: glyph.left + glyph.width / 2,
        cy: glyph.top + glyph.height / 2,
        half: glyph.width / 2,
        // A hidden caption keeps its box (visibility), so it can be re-measured.
        label: label ? padded(label.getBoundingClientRect()) : null,
        // Natural size, unaffected by where the caption currently sits.
        labelSize: label ? { w: label.offsetWidth, h: label.offsetHeight } : null,
        leader: selected ? el.querySelector('.atlas-marker-leader') : null,
        name: el.dataset.id,
      });
    }
    for (const [id, parts] of beamEls) {
      if (!parts.pill.getClientRects().length) continue; // far side of the globe
      const anchor = parts.outer.getBoundingClientRect();
      const { arc } = parts;
      const a = globe.getScreenCoords(arc.startLat, arc.startLng, 0);
      const b = globe.getScreenCoords(arc.endLat, arc.endLng, 0);
      const lengthPx = Math.hypot(a.x - b.x, a.y - b.y);
      const hovered = parts.pill.matches(':hover') || parts.pill === document.activeElement;
      const longW = beamTextWidth(parts.text, parts.pill) + BEAM_PILL_PAD;
      const shortW = beamTextWidth(parts.shortText, parts.pill) + BEAM_PILL_PAD;
      items.push({
        type: 'beam',
        name: `beam:${id}`,
        parts,
        selected: arc.selected,
        hovered,
        cluster: false,
        meta: { weight: 1e6 - arc.rank },
        cx: anchor.left,
        cy: anchor.top,
        lengthPx,
        longW,
        shortW,
        label: null,
        glyph: null,
      });
    }
    // ---- decide ------------------------------------------------------------
    const rank = (it) => {
      if (it.type === 'beam') return it.selected ? -1 : it.hovered ? 1 : 2.5;
      return it.selected ? (it.meta.tier === 'facility' ? 0 : 0.5) : it.hovered ? 1 : it.cluster ? 2 : 3;
    };
    const order = items.slice().sort((a, b) => (
      rank(a) - rank(b)
      || (b.meta.weight || 0) - (a.meta.weight || 0)
      || (a.name < b.name ? -1 : 1)
    ));
    // A caption also keeps clear of the glyph of any facility or cluster that
    // outranks its own marker (a lesser facility's pin may sit under it; the
    // caption never covers a more important one).
    const markerItems = items.filter((it) => it.type === 'marker');
    const obstacles = markerItems.filter((it) => it.cluster || it.meta.tier === 'facility' || it.selected);
    const glyphBoxes = obstacles.map((o) => o.glyph);
    const rings = markerItems.filter((it) => it.selected).map((it) => ({
      cx: it.cx, cy: it.cy, r: it.half + RING_REACH,
    }));
    const orderIndex = new Map(order.map((it, i) => [it, i]));
    const placed = [];
    const hide = new Map(); // element -> true/false (marker) or { hidden, ... } (beam)
    const moves = new Map(); // element -> placement of a selected caption
    // LABEL_BUDGET (spec §70) caps how many captions are on screen at once;
    // clusters, the selection and the hovered marker are always inside it.
    let budgetLeft = LABEL_BUDGET;
    const beamDecisions = [];
    const beamIsSubject = items.some((it) => it.type === 'beam' && it.selected);
    for (const it of order) {
      if (it.type === 'beam') {
        const decision = { it, hidden: true, short: true };
        beamDecisions.push(decision);
        const idle = !it.selected && !it.hovered;
        // While a beam is the subject, the other beams' labels stay out of its way
        // (hover or focus still brings one up).
        if (idle && (it.lengthPx < Math.max(BEAM_LABEL_MIN_PX, it.shortW * 0.9) || budgetLeft <= 0 || beamIsSubject)) continue;
        // The full name when the arc is long enough to carry it (or the beam is the
        // one a panel is open for), else the distance alone: a short label is tried
        // before a long one is given up.
        const forms = [];
        if (it.selected || it.lengthPx >= it.longW * 0.85) forms.push({ short: false, w: it.longW });
        forms.push({ short: true, w: it.shortW });
        for (const form of forms) {
          const spot = placeCaption({
            cx: it.cx,
            cy: it.cy,
            radius: 5,
            w: form.w,
            h: BEAM_PILL_HEIGHT,
            preferAbove: true,
            stage,
            placed,
            // The halo of a selected marker is decoration: a beam label may lie over
            // it, but never over a glyph.
            rings: [],
            glyphs: glyphBoxes,
          });
          // An unselected label keeps to its own place (above, below or beside its arc) or is
          // dropped; only a selected one is moved about to find room.
          if (!spot || (idle && spot.index > 3)) continue;
          decision.hidden = false;
          decision.short = form.short;
          decision.spot = spot;
          placed.push(spot.box);
          budgetLeft -= 1;
          break;
        }
        continue;
      }
      if (!it.label) continue;
      if (it.selected) {
        // Selected captions (an experiment selects every site and facility it
        // uses) never overlap: each takes the first free place around its ring,
        // joined to it by a leader line when it is not the usual one below.
        const spot = placeCaption({
          cx: it.cx,
          cy: it.cy,
          radius: it.half + RING_REACH,
          w: it.labelSize.w,
          h: it.labelSize.h,
          preferAbove: false,
          stage,
          placed,
          rings,
          glyphs: glyphBoxes.filter((g) => g !== it.glyph),
        });
        if (!spot) { hide.set(it.el, true); continue; }
        placed.push(spot.box);
        moves.set(it.el, { it, spot });
        hide.set(it.el, false);
        budgetLeft -= 1;
        continue;
      }
      if (it.hovered || it.cluster) {
        // The hovered marker and cluster badges are never hidden.
        placed.push(it.label);
        hide.set(it.el, false);
        budgetLeft -= 1;
        continue;
      }
      if (budgetLeft <= 0 || it.nearLimb) { hide.set(it.el, true); continue; }
      // A caption running past the stage edge would be cut off mid-word.
      const clipped = it.label.left < stage.left || it.label.right > stage.right
        || it.label.top < stage.top || it.label.bottom > stage.bottom;
      const blocked = clipped
        || placed.some((r) => overlaps(it.label, r))
        || obstacles.some((o) => orderIndex.get(o) < orderIndex.get(it) && overlaps(it.label, o.glyph));
      hide.set(it.el, blocked);
      if (!blocked) { placed.push(it.label); budgetLeft -= 1; }
    }

    // ---- writes ------------------------------------------------------------
    for (const [el, hidden] of hide) {
      labelHidden.set(el.dataset.id, hidden);
      if (el.classList.contains('is-label-hidden') !== hidden) el.classList.toggle('is-label-hidden', hidden);
    }
    for (const [el, { it, spot }] of moves) {
      el.style.setProperty('--label-x', `${spot.dx.toFixed(1)}px`);
      el.style.setProperty('--label-y', `${spot.dy.toFixed(1)}px`);
      applyLeader(el, it.leader, spot, it.half + RING_REACH - 3, it.cx, it.cy);
    }
    for (const { it, hidden, short, spot } of beamDecisions) {
      const { outer, pill, leader } = it.parts;
      labelHidden.set(it.name, hidden);
      if (outer.classList.contains('is-label-hidden') !== hidden) outer.classList.toggle('is-label-hidden', hidden);
      if (outer.classList.contains('is-short') !== short) outer.classList.toggle('is-short', short);
      if (spot) {
        pill.style.setProperty('--bx', `${spot.dx.toFixed(1)}px`);
        pill.style.setProperty('--by', `${spot.dy.toFixed(1)}px`);
        applyLeader(outer, leader, spot, 4, it.cx, it.cy);
      }
    }
  }

  /** Draws (or clears) the leader line from an anchor out to the caption placed at
   * `spot`, starting `start` px out from the anchor along the way. */
  function applyLeader(host, leader, spot, start, cx, cy) {
    if (!leader) return;
    const nx = Math.min(Math.max(cx, spot.box.left + LABEL_PAD), spot.box.right - LABEL_PAD);
    const ny = Math.min(Math.max(cy, spot.box.top + LABEL_PAD), spot.box.bottom - LABEL_PAD);
    const dx = nx - cx;
    const dy = ny - cy;
    const distance = Math.hypot(dx, dy);
    const length = distance - start;
    // The caption sits in its usual place (or touches the ring): no line needed.
    if (!spot.moved || length < 5) {
      host.classList.remove('has-label-offset');
      return;
    }
    const angle = Math.atan2(dy, dx);
    leader.style.width = `${length.toFixed(1)}px`;
    leader.style.transform = `translate(${(Math.cos(angle) * start).toFixed(1)}px, ${(Math.sin(angle) * start).toFixed(1)}px) rotate(${angle.toFixed(4)}rad)`;
    host.classList.add('has-label-offset');
  }

  // ---- selection: which markers an open panel stands for, and where to look
  const facilitiesBySite = new Map();
  for (const facility of Object.values(atlas.facilities || {})) {
    if (!facility.primary_site_id) continue;
    const list = facilitiesBySite.get(facility.primary_site_id) || [];
    list.push(facility.id);
    facilitiesBySite.set(facility.primary_site_id, list);
  }

  /** Whether the highlight set (a topic's facilities and sites) covers a marker.
   * A cluster stands for several markers — its id lists them, `cluster:<tier>:
   * <id>+<id>…` — so it is lit when any of them is, rather than muted over the
   * very facility being pointed at. */
  function isHighlighted(id) {
    if (!highlightSet) return false;
    if (highlightSet.has(id)) return true;
    if (!id.startsWith('cluster:')) return false;
    return id.replace(/^cluster:[^:]+:/, '').split('+').some((member) => highlightSet.has(member));
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
      id, markerIds: new Set(), beamlineIds: new Set(), institutionId: null, anchor: null, altitude: FOCUS_ALTITUDE,
    };
    if (!id) return out;
    const record = index.get(id);
    // The beams a panel is about: a beamline's own, or those an experiment uses
    // (the link is stored on both records, so either one counts).
    if (id.startsWith('beamline:') && atlas.beamlines && atlas.beamlines[id]) out.beamlineIds.add(id);
    if (id.startsWith('experiment:')) {
      for (const beamline of Object.values(atlas.beamlines || {})) {
        if ((beamline.experiment_ids || []).includes(id) || (record && (record.beamline_ids || []).includes(beamline.id))) {
          out.beamlineIds.add(beamline.id);
        }
      }
    }
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
    // A beam selection frames the whole baseline, centred between its ends.
    if (out.beamlineIds.size) {
      const ends = [];
      for (const beamlineId of out.beamlineIds) {
        for (const baseline of atlas.beamlines[beamlineId].baselines || []) {
          const from = siteCoords(baseline.from_site_id);
          const to = siteCoords(baseline.to_site_id);
          const km = baselineKm(baseline.distance);
          if (!from || !to || (km != null && km < BEAM_MIN_KM)) continue;
          ends.push({ lat: from.lat, lon: from.lon }, { lat: to.lat, lon: to.lon });
        }
      }
      if (ends.length) {
        const middle = centreOf(ends);
        let span = 0;
        for (const a of ends) for (const b of ends) span = Math.max(span, greatCircleDeg(a.lat, a.lon, b.lat, b.lon));
        out.anchor = { lat: middle.lat, lon: middle.lon };
        out.altitude = clamp(span * BEAM_FOCUS_ALTITUDE_PER_DEG, BEAM_FOCUS_ALTITUDE_MIN, FOCUS_ALTITUDE_WIDE);
        return out;
      }
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
    endViewRequest(true); // the subject changed: ease back to the centre of the view
    globe.pointOfView(
      { lat: anchor.lat, lng: anchor.lon, altitude },
      reducedMotion() ? 0 : FOCUS_FLIGHT_MS,
    );
  }

  /** Flies the camera to the places the current highlight (a topic's
   * facilities and sites) is about: all of them in view, or the densest region
   * when they span most of the globe (see fitView). Instant under
   * prefers-reduced-motion. */
  function fitHighlight() {
    if (!highlightSet || !highlightSet.size) return;
    const points = [];
    for (const id of highlightSet) {
      const at = atlas.sites && atlas.sites[id] ? siteCoords(id) : facilityAnchor(id);
      if (at) points.push({ lat: at.lat, lon: at.lon });
    }
    const view = fitView(points);
    if (!view) return;
    stopAutoRotate();
    endViewRequest(true);
    globe.pointOfView(
      { lat: view.lat, lng: view.lon, altitude: view.altitude },
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
  // Where showView's caller wants its subject, as a pixel shift of the view centre
  // (positive x: to the right; positive y: down), on top of the bottom-sheet inset.
  let framing = { x: 0, y: 0 };
  let framingTween = 0;
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
    const inset = Math.round(coveredBottom());
    // globe.gl's own `globeOffset` moves the picture by this many pixels (right, down)
    // and keeps doing so through resizes and the library's own start-up digest, which
    // clear a view window set on the camera directly. A bottom sheet moves the picture
    // up by half of what it covers, so its subject sits mid-way in what is left.
    const shiftX = Math.round(framing.x);
    const shiftY = Math.round(framing.y - inset / 2);
    const key = `${width}x${height}:${shiftX},${shiftY}`;
    if (key === insetKey) return;
    insetKey = key;
    globe.globeOffset([shiftX, shiftY]);
    scheduleDeclutter(DECLUTTER_DELAY_MS);
  }

  /** Eases the framing shift to `target` over `ms` (at once when 0, or under
   * prefers-reduced-motion). */
  function moveFraming(target, ms) {
    window.cancelAnimationFrame(framingTween);
    framingTween = 0;
    const from = { ...framing };
    if (!ms || reducedMotion() || (Math.abs(target.x - from.x) < 0.5 && Math.abs(target.y - from.y) < 0.5)) {
      framing = { ...target };
      applyViewInset(globe.width(), globe.height());
      return;
    }
    const start = performance.now();
    const step = (now) => {
      const p = Math.min(1, (now - start) / ms);
      const e = p < 0.5 ? 2 * p * p : 1 - ((-2 * p + 2) ** 2) / 2;
      framing = { x: from.x + (target.x - from.x) * e, y: from.y + (target.y - from.y) * e };
      applyViewInset(globe.width(), globe.height());
      framingTween = p < 1 ? window.requestAnimationFrame(step) : 0;
    };
    framingTween = window.requestAnimationFrame(step);
  }

  /** The pixel shift that puts the middle of the stage's free part at the centre
   * of the view, for an element laid over the stage (the Start-here card): a sheet
   * spanning the stage's width frees the other end; a panel spanning its height
   * frees the other side; a card floating at one side is judged by the nearest
   * edge it hangs from. An element that does not overlap the stage (a phone sheet
   * that shrinks the stage instead of covering it) shifts nothing. */
  function clearanceShift(element) {
    if (!element || element.getClientRects().length === 0) return { x: 0, y: 0 };
    const stage = container.getBoundingClientRect();
    const box = element.getBoundingClientRect();
    const ox = Math.min(box.right, stage.right) - Math.max(box.left, stage.left);
    const oy = Math.min(box.bottom, stage.bottom) - Math.max(box.top, stage.top);
    if (!(ox > 0 && oy > 0) || !stage.width || !stage.height) return { x: 0, y: 0 };
    const limit = (v, size) => clamp(v, -0.35 * size, 0.35 * size);
    const above = box.top + box.height / 2 < stage.top + stage.height / 2;
    const leftOf = box.left + box.width / 2 < stage.left + stage.width / 2;
    if (ox >= 0.9 * stage.width) {
      return { x: 0, y: limit(above ? (box.bottom - stage.top) / 2 : -(stage.bottom - box.top) / 2, stage.height) };
    }
    if (oy >= 0.9 * stage.height) {
      return { x: limit(leftOf ? (box.right - stage.left) / 2 : -(stage.right - box.left) / 2, stage.width), y: 0 };
    }
    const gaps = [
      ['left', box.left - stage.left], ['right', stage.right - box.right],
      ['top', box.top - stage.top], ['bottom', stage.bottom - box.bottom],
    ].sort((a, b) => a[1] - b[1]);
    switch (gaps[0][0]) {
      case 'left': return { x: limit((box.right - stage.left) / 2, stage.width), y: 0 };
      case 'right': return { x: limit(-(stage.right - box.left) / 2, stage.width), y: 0 };
      case 'top': return { x: 0, y: limit((box.bottom - stage.top) / 2, stage.height) };
      default: return { x: 0, y: limit(-(stage.bottom - box.top) / 2, stage.height) };
    }
  }

  /** The highest camera altitude at which the globe still shows at least
   * MIN_GLOBE_RADIUS_PX across its radius in what is left of the stage: a view
   * written for a full-height stage (2.6 for the opening look) would be a 40 px
   * marble in the 120 px strip a phone's sheet leaves. */
  function altitudeCeiling() {
    const visible = Math.max(80, container.clientHeight - coveredBottom());
    const u = (MIN_GLOBE_RADIUS_PX * Math.tan((25 * Math.PI) / 180)) / (visible / 2);
    return 1 / (u / Math.sqrt(1 + u * u)) - 1;
  }

  // What showView was last asked for. While it stands, a change in the stage's size
  // (a sheet opening, a rotation) or in the element it clears is answered by framing
  // the same view again; any other camera command ends it, and a person taking the
  // camera ends the re-aiming (`held`) but not the shift. A shift ends by easing
  // back to the centre.
  let viewRequest = null;
  function endViewRequest(animate) {
    viewRequest = null;
    if (framing.x || framing.y) moveFraming({ x: 0, y: 0 }, animate ? FOCUS_FLIGHT_MS : 0);
  }
  function reframe(animate) {
    if (!viewRequest) return;
    const { view, offset, clearOf } = viewRequest;
    const shift = clearanceShift(clearOf);
    moveFraming({ x: shift.x + offset.x, y: shift.y + offset.y }, animate ? 450 : 0);
    if (viewRequest.held) {
      const altitude = clamp(Math.min(view.altitude, altitudeCeiling()), MIN_VIEW_ALTITUDE, MAX_VIEW_ALTITUDE);
      if (Math.abs(altitude - viewRequest.altitude) > 0.01) {
        viewRequest.altitude = altitude;
        // A flight begun by showView may still be running, and the library never
        // cancels one: a new flight of the same length starts later, so it ends last
        // and wins.
        globe.pointOfView({ lat: view.lat, lng: view.lng, altitude }, reducedMotion() ? 0 : FOCUS_FLIGHT_MS);
        if (reducedMotion()) {
          currentAltitude = altitude;
          rebuildVisibleLayer();
        }
      }
    }
  }
  controls.addEventListener('start', () => { if (viewRequest) viewRequest.held = false; });

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
      // After the first frame has painted, bring in the Earth and the country lines.
      window.requestAnimationFrame(() => window.setTimeout(() => {
        loadEarthTexture();
        loadBorders();
      }, 0));
    },
    /** Points the camera at `{ lat, lng, altitude }` (altitude in globe radii; 2.4
     * is the opening overview, 0.5 a country). Animated by default, instant when
     * `animate` is false or under prefers-reduced-motion. Ends auto-rotation, like
     * any other deliberate camera move, so the framed view stays framed.
     *
     * Options for a view that is meant to sit beside something laid over the stage:
     *   offset   `{ x, y }` px — where the subject goes relative to the stage's centre
     *            (x > 0: right of it, y > 0: below it)
     *   clearOf  an element over the stage (the Start-here card): the subject goes to the
     *            middle of what that element leaves free, and follows it as it moves,
     *            resizes, or is dismissed (the view eases back to the centre)
     * The altitude asked for is lowered on a stage too short to show a globe of a
     * useful size (the strip a phone's sheet leaves). The shift ends, easing back,
     * when anything else moves the camera (a selection, a topic, a collaboration). */
    showView(view, { animate = true, offset = null, clearOf = null } = {}) {
      const lat = Number(view && view.lat);
      const lng = Number(view && view.lng);
      const altitude = Number(view && view.altitude);
      if (!Number.isFinite(lat) || !Number.isFinite(lng) || !Number.isFinite(altitude)) return;
      stopAutoRotate();
      const instant = !animate || reducedMotion();
      const wanted = {
        lat: clamp(lat, -90, 90),
        lng: ((((lng + 180) % 360) + 360) % 360) - 180,
        altitude,
      };
      const dx = Number(offset && offset.x);
      const dy = Number(offset && offset.y);
      const extra = { x: Number.isFinite(dx) ? dx : 0, y: Number.isFinite(dy) ? dy : 0 };
      if (viewRequest && viewRequest.clearOf && viewRequest.clearOf !== clearOf && resizeObserver) {
        resizeObserver.unobserve(viewRequest.clearOf);
      }
      viewRequest = {
        view: wanted, offset: extra, clearOf: clearOf || null, held: true, altitude: null,
      };
      if (clearOf && resizeObserver) resizeObserver.observe(clearOf);
      const shift = clearanceShift(clearOf);
      moveFraming({ x: shift.x + extra.x, y: shift.y + extra.y }, instant ? 0 : FOCUS_FLIGHT_MS);
      const target = {
        lat: wanted.lat,
        lng: wanted.lng,
        altitude: clamp(Math.min(altitude, altitudeCeiling()), MIN_VIEW_ALTITUDE, MAX_VIEW_ALTITUDE),
      };
      viewRequest.altitude = target.altitude;
      if (instant) currentAltitude = target.altitude;
      globe.pointOfView(target, instant ? 0 : FOCUS_FLIGHT_MS);
      if (instant) rebuildVisibleLayer(); // markers cluster for the new altitude at once
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
        const lit = isHighlighted(id);
        el.classList.toggle('is-highlighted', lit);
        el.classList.toggle('is-muted', !!highlightSet && !lit);
      }
    },
    fitHighlight,
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
        endViewRequest(true);
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
      const resized = globe.width() !== width || globe.height() !== height;
      if (resized) globe.width(width).height(height);
      applyViewInset(width, height);
      if (resized && viewRequest) reframe(false); // a stage of another size: the same view, re-aimed
      scheduleDeclutter(DECLUTTER_DELAY_MS);
    },
    /** True when no marker rebuild and no caption declutter is waiting to run, so what is
     * on screen is the final layout for the camera where it is (export.js waits for this
     * before it takes a picture, and never takes one in the middle of a layout). */
    isSettled() {
      return !rebuildTimer && !declutterTimer;
    },
    /** The globe as a picture, for export.js: the frame on screen, drawn again at
     * `pixelRatio` device pixels per CSS pixel and copied to a new canvas that is the
     * stage's size times that. The WebGL canvas is not kept once it has been shown
     * (preserveDrawingBuffer would cost every frame), so the frame is rendered and
     * copied in the same task, before the browser presents it; the renderer then goes
     * back to its own ratio and draws the frame it had. The markers, captions and beam
     * labels are DOM elements, not part of this canvas (export.js draws them from the
     * elements themselves). */
    captureFrame(pixelRatio) {
      const renderer = globe.renderer();
      const original = renderer.getPixelRatio();
      try {
        renderer.setPixelRatio(pixelRatio);
        renderer.render(globe.scene(), globe.camera());
        const source = renderer.domElement;
        const copy = document.createElement('canvas');
        copy.width = source.width;
        copy.height = source.height;
        copy.getContext('2d').drawImage(source, 0, 0);
        return copy;
      } finally {
        renderer.setPixelRatio(original);
        renderer.render(globe.scene(), globe.camera());
      }
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
        // The element a view clears moved, resized or went away: follow it.
        if (viewRequest) reframe(true);
      });
    });
    resizeObserver.observe(container);
    // A bottom sheet appearing or changing height does not resize the stage,
    // but it does change what is visible of it.
    for (const el of coverElements) if (el) resizeObserver.observe(el);
  }
  return api;
}
