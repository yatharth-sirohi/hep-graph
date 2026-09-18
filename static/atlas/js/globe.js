// globe.js — Globe.gl wrapper. Facility/site/institution markers are real
// focusable DOM elements (htmlElementsData) holding inline SVG, per
// docs/HEP_ATLAS_GLOBE_LIBRARY.md's own recommendation: this keeps markers
// accessible and clickable without needing access to the bundled three.js
// classes (which globe.gl does not expose on window). Beam and institution
// arcs use the built-in arcsData canvas layer.

import { facilityShape, statusAtMonth, statusInRange, statusColor, DIMMED_STATUSES } from './model.js';

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

let hatchCounter = 0;

function svgEl(name, attrs) {
  const el = document.createElementNS(SVG_NS, name);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  return el;
}

/** Builds a small inline-SVG glyph for a marker. `shape` selects the outline,
 * `hollow` draws a stroke-only shape, `hatched` fills with a diagonal hatch
 * pattern (certainty === "possible"). */
function buildGlyph({ shape, color, size, hollow, hatched }) {
  const svg = svgEl('svg', { viewBox: '0 0 24 24', width: size, height: size, 'aria-hidden': 'true' });
  let fill = hollow ? 'none' : color;
  const stroke = color;
  if (hatched && !hollow) {
    hatchCounter += 1;
    const patternId = `atlas-hatch-${hatchCounter}`;
    const defs = svgEl('defs', {});
    const pattern = svgEl('pattern', {
      id: patternId, width: '4', height: '4', patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(45)',
    });
    pattern.appendChild(svgEl('rect', { width: '4', height: '4', fill: 'rgba(0,0,0,0.35)' }));
    pattern.appendChild(svgEl('line', { x1: '0', y1: '0', x2: '0', y2: '4', stroke: color, 'stroke-width': '2' }));
    defs.appendChild(pattern);
    svg.appendChild(defs);
    fill = `url(#${patternId})`;
  }
  const strokeWidth = hollow ? 2.4 : hatched ? 1.5 : 1;
  const dash = hatched && hollow ? '3,2' : null;
  const common = { fill, stroke, 'stroke-width': strokeWidth };
  if (dash) common['stroke-dasharray'] = dash;
  switch (shape) {
    case 'ring':
      svg.appendChild(svgEl('circle', { cx: 12, cy: 12, r: 8, fill: 'none', stroke, 'stroke-width': 3 }));
      if (!hollow) svg.appendChild(svgEl('circle', { cx: 12, cy: 12, r: 8, fill, opacity: 0.25 }));
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
      svg.appendChild(svgEl('rect', { x: 3, y: 3, width: 18, height: 18, ...common }));
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
 */
export function createGlobe(container, { atlas, index, onSelect, onArcHover }) {
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
    .arcAltitudeAutoScale(0.35);

  try {
    const mat = globe.globeMaterial();
    if (mat && mat.color && typeof mat.color.setStyle === 'function') {
      mat.color.setStyle('#0b1f2b');
      if ('shininess' in mat) mat.shininess = 2;
    }
  } catch (error) {
    // Cosmetic only — the sphere still renders with the library default.
  }

  const reduced = reducedMotion();
  globe.arcDashLength(reduced ? 1 : 0.4);
  globe.arcDashGap(reduced ? 0 : 0.18);
  globe.arcDashAnimateTime(reduced ? 0 : 2600);
  const controls = globe.controls();
  controls.autoRotate = !reduced;
  controls.autoRotateSpeed = 0.28;
  controls.enableDamping = true;

  fetch('/atlas/vendor/land-110m.json').then((r) => r.json()).then((land) => {
    globe.polygonsData(land.features || []);
  }).catch(() => {});

  // --- marker model -------------------------------------------------
  const markerEls = new Map(); // id -> element
  const markerMeta = new Map(); // id -> { segments, baseShape info, route }
  let arcsEnabled = false;
  let institutionConnectionArcs = [];
  let beamArcs = [];
  let highlightSet = null;

  function makeMarkerElement({ id, name, route, size, shape, color, hollow, tier }) {
    const el = document.createElement('div');
    el.className = `atlas-marker tier-${tier}`;
    el.setAttribute('role', 'button');
    el.setAttribute('tabindex', '0');
    el.setAttribute('aria-label', name);
    el.dataset.id = id;
    el.appendChild(buildGlyph({ shape, color, size, hollow, hatched: false }));
    const label = document.createElement('span');
    label.className = 'atlas-marker-label';
    label.textContent = name;
    el.appendChild(label);
    const activate = () => onSelect && onSelect(route);
    el.addEventListener('click', activate);
    el.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        activate();
      }
    });
    return el;
  }

  function siteCoords(siteId) {
    const site = index.get(siteId);
    return site ? { lat: site.lat, lon: site.lon } : null;
  }

  function buildFacilityMarkers() {
    const out = [];
    for (const facility of Object.values(atlas.facilities || {})) {
      const coords = siteCoords(facility.primary_site_id);
      if (!coords) continue;
      const info = facilityShape(facility.kind);
      const id = facility.id;
      const el = makeMarkerElement({
        id, name: facility.name, route: { type: 'facility', slug: id.split(':')[1] },
        size: 26, shape: info.shape, color: info.color, hollow: false, tier: 'facility',
      });
      markerEls.set(id, el);
      markerMeta.set(id, { segments: facility.state_segments, tier: 'facility' });
      out.push({
        id, lat: coords.lat, lng: coords.lon, altitude: 0.02, el,
      });
    }
    return out;
  }

  function buildSiteMarkers() {
    const out = [];
    for (const site of Object.values(atlas.sites || {})) {
      const id = site.id;
      const el = makeMarkerElement({
        id, name: site.name, route: { type: 'facility', slug: (site.facility_id || id).split(':')[1] },
        size: 12, shape: 'circle', color: statusColor(site.status), hollow: false, tier: 'site',
      });
      el.classList.add('is-site-tier');
      markerEls.set(id, el);
      markerMeta.set(id, { segments: site.state_segments, tier: 'site' });
      out.push({ id, lat: site.lat, lng: site.lon, altitude: 0.012, el });
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
          startLat: from.lat, startLng: from.lon, endLat: to.lat, endLng: to.lon,
          color: ['rgba(84,198,186,0.85)', 'rgba(84,198,186,0.15)'],
          stroke: 0.5,
          label: `${beamline.name}: ${baseline.distance ? baseline.distance.display : ''} baseline`,
          kind: 'beam',
        });
      }
    }
    return out;
  }

  function refreshArcs() {
    const arcs = [...beamArcs];
    if (arcsEnabled) arcs.push(...institutionConnectionArcs);
    globe.arcsData(arcs);
  }

  let facilityMarkers = [];
  let siteMarkers = [];
  let institutionMarkerData = [];

  function rebuildBaseLayers() {
    facilityMarkers = buildFacilityMarkers();
    siteMarkers = buildSiteMarkers();
    beamArcs = buildBeamArcs();
    applyHtmlLayer();
    refreshArcs();
  }

  function applyHtmlLayer() {
    globe.htmlElementsData([...facilityMarkers, ...siteMarkers, ...institutionMarkerData]);
  }

  // --- semantic zoom: sites fade in only once zoomed close enough ----
  const ZOOM_THRESHOLD = 1.3;
  function updateZoomTier(altitude) {
    const zoomedIn = altitude < ZOOM_THRESHOLD;
    for (const [id, el] of markerEls) {
      const meta = markerMeta.get(id);
      if (meta && meta.tier === 'site') {
        el.style.display = zoomedIn ? '' : 'none';
      }
    }
  }
  globe.onZoom(({ altitude }) => updateZoomTier(altitude));

  // --- timeline filtering ---------------------------------------------
  let timelineMode = null; // { kind: 'year', year } | { kind: 'range', lo, hi } | null

  function applyTimelineToElement(id, segments) {
    const el = markerEls.get(id);
    if (!el) return;
    if (!segments || segments.length === 0 || !timelineMode) {
      el.classList.remove('is-dimmed', 'is-possible', 'is-absent');
      return;
    }
    const result = timelineMode.kind === 'year'
      ? statusAtMonth(segments, timelineMode.month)
      : statusInRange(segments, timelineMode.lo, timelineMode.hi);
    if (!result) {
      el.classList.add('is-absent');
      el.classList.remove('is-dimmed', 'is-possible');
      return;
    }
    el.classList.remove('is-absent');
    el.classList.toggle('is-dimmed', DIMMED_STATUSES.has(result.status));
    el.classList.toggle('is-possible', result.certainty === 'possible');
  }

  function reapplyTimeline() {
    for (const [id, meta] of markerMeta) applyTimelineToElement(id, meta.segments);
  }

  // --- public API -------------------------------------------------------
  const api = {
    ready() {
      // No fly-in intro: an animated initial camera move is exactly the kind
      // of motion prefers-reduced-motion asks us to skip, and it also left
      // marker screen positions a moving target for a second or two after
      // load. Frame a stable default view instantly instead.
      globe.pointOfView({ lat: 20, lng: 10, altitude: 2.4 }, 0);
      rebuildBaseLayers();
    },
    setYear(year) {
      timelineMode = { kind: 'year', year, month: Math.round((year - 1950) * 12 + 6) };
      reapplyTimeline();
    },
    setRange(lo, hi) {
      timelineMode = {
        kind: 'range',
        lo: Math.round((lo - 1950) * 12), hi: Math.round((hi - 1950) * 12 + 11),
      };
      reapplyTimeline();
    },
    clearTimeline() {
      timelineMode = null;
      reapplyTimeline();
    },
    setArcsEnabled(enabled) {
      arcsEnabled = enabled;
      refreshArcs();
    },
    setHighlight(idSet) {
      highlightSet = idSet;
      for (const [id, el] of markerEls) {
        el.classList.toggle('is-highlighted', !!highlightSet && highlightSet.has(id));
        el.classList.toggle('is-muted', !!highlightSet && !highlightSet.has(id));
      }
    },
    async setCollaboration(collaborationId, membership) {
      institutionMarkerData = [];
      institutionConnectionArcs = [];
      const collaboration = index.get(collaborationId);
      const hostCoords = collaboration && siteCoords(collaboration.host_site_id);
      for (const member of (membership && membership.members) || []) {
        if (!member.institution_id || member.lat == null || member.lon == null) continue;
        const id = `${collaborationId}::${member.institution_id}`;
        const hollow = member.render === 'hollow';
        const el = makeMarkerElement({
          id, name: member.name, route: { type: 'institution', slug: member.institution_id.split(':')[1] },
          size: 9, shape: 'circle', color: '#f2b441', hollow, tier: 'institution',
        });
        el.dataset.collaboration = collaborationId;
        markerEls.set(id, el);
        markerMeta.set(id, { segments: null, tier: 'institution' });
        institutionMarkerData.push({ id, lat: member.lat, lng: member.lon, altitude: 0.015, el });
        if (hostCoords) {
          institutionConnectionArcs.push({
            id: `conn:${id}`,
            startLat: hostCoords.lat, startLng: hostCoords.lon,
            endLat: member.lat, endLng: member.lon,
            color: ['rgba(242,180,65,0.55)', 'rgba(242,180,65,0.05)'],
            stroke: 0.25,
            label: `${member.name} ↔ collaboration host`,
          });
        }
      }
      applyHtmlLayer();
      refreshArcs();
      if (hostCoords) globe.pointOfView({ lat: hostCoords.lat, lng: hostCoords.lon, altitude: 1.6 }, reduced ? 0 : 900);
    },
    clearCollaboration() {
      for (const marker of institutionMarkerData) {
        markerEls.delete(marker.id);
        markerMeta.delete(marker.id);
      }
      institutionMarkerData = [];
      institutionConnectionArcs = [];
      applyHtmlLayer();
      refreshArcs();
    },
    focus(id) {
      const site = index.get(id) && index.get(id).primary_site_id ? index.get(index.get(id).primary_site_id) : index.get(id);
      const coords = site && site.lat != null ? { lat: site.lat, lon: site.lon } : null;
      if (coords) globe.pointOfView({ lat: coords.lat, lng: coords.lon, altitude: 1.0 }, reduced ? 0 : 900);
    },
    pauseAutoRotate() { controls.autoRotate = false; },
    resumeAutoRotate() { if (!reduced) controls.autoRotate = true; },
    resize() {
      globe.width(container.clientWidth).height(container.clientHeight);
    },
    destroy() {
      if (typeof globe._destructor === 'function') globe._destructor();
    },
  };
  api.resize();
  return api;
}
