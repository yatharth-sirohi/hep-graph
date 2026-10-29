// export.js — "Take it to a slide" (docs/HEP_ATLAS_TEACHING_PLAN.md, workstream 3).
//
// Two things an instructor needs out of the Atlas and into a lecture:
//
//   1. The view on screen — the globe, a local map, or the figure of a view (the beam
//      section, the charts, the exclusion plot, the results timeline, the detector line-up) —
//      as a PNG with its title, the timeline year, a citation footer and, on a map, a metre
//      scale bar and a north arrow. Two sizes: a 1920 x 1080 slide, or twice what is on screen.
//   2. A one-page, print-ready sheet for a facility (A4 or Letter): what it is, where,
//      what it holds, who it hosts, a to-scale map, and where each fact comes from.
//
// How the picture is made (exportpaint.js has the painters): the globe's WebGL frame is
// drawn again at the export's pixel ratio (globe.js captureFrame) and the markers,
// captions and beam labels — HTML — are painted over it from the elements themselves.
// A map's tiles are drawn from the <img> elements Leaflet already loaded, its vector
// layer from the live SVG, and its labels and symbols from their own elements. Nothing
// is fetched for the export, no tile is requested twice, and nothing leaves the page.
//
// Map tiles come from tile.openstreetmap.org, which answers with
// `Access-Control-Allow-Origin: *`, and localmap.js asks for them with `crossOrigin`, so
// they can be drawn without tainting the canvas. That is checked every time rather than
// assumed: if the canvas does come out tainted, or the tiles had not all arrived, the
// image is made without them — to-scale shapes on a plain background — and the export
// dialog says so. It never half-covers a map and never proxies a tile.
//
// A view's figure is SVG, and the view host (views/host.js) hands it over: its shapes are drawn
// as the image the browser makes of the live SVG, its text from the page's own fonts, and the
// title band, the year and the citation are the same bands the globe and the map get. A view
// with no figure (a table) has no image to make, and the Export button says so.

import * as state from './state.js';
import * as loader from './loader.js';
import * as localmap from './localmap.js';
import { cssToken } from './globeicons.js';
import {
  kindLabel, statusForTimeline, timelineAbsenceReason, titleCase, quantityText,
} from './model.js';
import {
  makeTransform, canvasX, canvasY, intersects, isShown, effectiveOpacity, paintBox,
  paintStyledBox, paintText, paintGlyph, paintLeader, rasterizeSvgLayer, dropShadowHalos,
  roundedPath, paintSvgFigure,
} from './exportpaint.js';

export const SITE_ADDRESS = 'hep-graph.vercel.app/atlas';
const SLIDE = { width: 1920, height: 1080 };
const MAX_SIDE = 8192;
const TILE_WAIT_MS = 9000;
// A sheet is one page: a facility with more experiments or sources than these lists the
// rest as a count, and the facility's panel in the Atlas has the whole list.
const MAX_SHEET_EXPERIMENTS = 30;
const MAX_SHEET_SOURCES = 8;

let env = null; // { atlas, index, manifest, getGlobe, views }

const nextFrame = () => new Promise((resolve) => window.requestAnimationFrame(() => resolve()));
const sleep = (ms) => new Promise((resolve) => window.setTimeout(resolve, ms));

class ExportError extends Error {}

// ------------------------------------------------------------------ naming

function pad2(n) { return String(n).padStart(2, '0'); }

export function todayISO(now = new Date()) {
  return `${now.getFullYear()}-${pad2(now.getMonth() + 1)}-${pad2(now.getDate())}`;
}

export function slugify(text) {
  return String(text || '').toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60);
}

/** The timeline selection as words (for the picture) and as a file-name part. */
export function timelineText(current) {
  if (current.range) {
    return {
      label: 'Timeline range', value: `${current.range[0]}–${current.range[1]}`, file: `${current.range[0]}-${current.range[1]}`,
    };
  }
  const year = current.year != null ? current.year
    : ((env && env.manifest.timeline && env.manifest.timeline.default_year) || new Date().getFullYear());
  return { label: 'Timeline year', value: String(year), file: String(year) };
}

function dataVersion() {
  const { manifest } = env;
  const version = manifest.data_version || manifest.version || 'unknown';
  return manifest.fixture ? `${version} (development fixture data)` : String(version);
}

export function citationLine(date = todayISO()) {
  return `HEP Atlas — ${SITE_ADDRESS} — data version ${dataVersion()} — accessed ${date}`;
}

/** What the view host says about the view on screen (see views/host.js exportState). */
function viewExportState(slug) {
  if (!env || !env.views) return { ready: false, reason: 'Views cannot be exported yet.' };
  return env.views.exportState(slug);
}

function panelHeading() {
  const heading = document.querySelector('#detail-panel h2, #map-drawer-panel h2');
  return heading ? heading.textContent.trim() : '';
}

/** What the picture is of: its kind, title, a line under the title, the timeline words,
 * and the file name. */
function describeView() {
  const current = state.get();
  if (current.entity && current.entity.type === 'map' && !localmap.exportInfo()) {
    throw new ExportError('The local map has not finished opening, so there is nothing to export yet.');
  }
  const timeline = timelineText(current);
  const entity = current.entity;
  const filtered = ['topic', 'status', 'era', 'facilityKind', 'experimentKind', 'region'].some((key) => current[key]);
  const mapInfo = entity && entity.type === 'map' ? localmap.exportInfo() : null;
  const viewInfo = entity && entity.type === 'view' ? viewExportState(entity.slug) : null;
  if (viewInfo && !viewInfo.ready) throw new ExportError(viewInfo.reason);
  let kind = 'globe';
  let title = 'Globe overview';
  let subtitle = 'World view of the facilities in the HEP Atlas';
  let slug = 'globe';
  if (mapInfo) {
    kind = 'map';
    title = mapInfo.meta.name;
    subtitle = 'Local map, drawn to scale';
    slug = `${entity.slug}-map`;
    const selected = mapInfo.selected && env.index.get(mapInfo.selected);
    if (selected) subtitle += ` · selected: ${selected.name}`;
  } else if (viewInfo) {
    kind = 'figure';
    title = viewInfo.title || 'HEP Atlas view';
    subtitle = viewInfo.subtitle || 'A view of the HEP Atlas';
    slug = viewInfo.name || entity.slug;
  } else if (entity) {
    const record = env.index.get(`${entity.type}:${entity.slug}`);
    title = (record && record.name) || panelHeading() || entity.slug;
    subtitle = [titleCase(entity.type), record && record.kind ? kindLabel(record.kind) : '']
      .filter(Boolean).join(' · ');
    slug = entity.slug;
  }
  if (filtered) subtitle += ' · filtered view';
  return {
    kind,
    title,
    subtitle,
    timeline,
    filename: `hep-atlas_${slugify(slug) || 'view'}_${timeline.file}.png`,
    mapInfo,
  };
}

// ------------------------------------------------------------------ layout

function fontFamily() {
  return window.getComputedStyle(document.body).fontFamily;
}

async function ensureFonts() {
  const family = fontFamily();
  if (document.fonts && document.fonts.load) {
    try {
      await Promise.all([
        document.fonts.load(`700 20px ${family}`, 'HEP Atlas — © 0123456789'),
        document.fonts.load(`400 14px ${family}`, 'accessed → ν'),
        document.fonts.ready,
      ]);
    } catch (error) { /* a font that will not load falls back; the picture still draws */ }
  }
}

function wrapLines(ctx, text, maxWidth) {
  const words = text.split(' ');
  const lines = [];
  let line = '';
  for (const word of words) {
    const trial = line ? `${line} ${word}` : word;
    if (line && ctx.measureText(trial).width > maxWidth) {
      lines.push(line);
      line = word;
    } else {
      line = trial;
    }
  }
  if (line) lines.push(line);
  return lines;
}

function footerLinesFor(info, tiles, date) {
  const lines = [citationLine(date)];
  if (info.kind === 'figure') {
    const entity = state.get().entity;
    lines.push(`Figure: ${info.title} — ${SITE_ADDRESS}#/view/${entity ? entity.slug : ''}`);
    for (const note of info.notes || []) lines.push(note);
  }
  if (info.kind === 'map') {
    const credits = [];
    if (tiles && tiles.state === 'included') credits.push('Basemap © OpenStreetMap contributors');
    const attribution = info.mapInfo ? info.mapInfo.attribution : [];
    if (attribution.length) credits.push(`Geometry: ${attribution.join('; ')}`);
    if (credits.length) lines.push(credits.join(' · '));
  }
  return lines;
}

/** Sizes of the picture: for the slide preset exactly 1920 x 1080 with the view fitted
 * between the title band and the footer; for the double preset twice the stage with
 * the two bands added; for a sheet snapshot the stage itself at `scale`. */
function planLayout(options, stageW, stageH, footerLines) {
  const measure = document.createElement('canvas').getContext('2d');
  const family = fontFamily();
  const bandsFor = (width, u) => {
    const headerH = Math.round(84 * u);
    measure.font = `500 ${Math.round(19 * u)}px ${family}`;
    const count = footerLines.reduce((n, line) => n + wrapLines(measure, line, width - 56 * u).length, 0);
    const footerH = Math.round(count * 25 * u + 26 * u);
    return { headerH, footerH };
  };
  if (options.bands === false) {
    const s = options.scale || 2;
    return {
      W: Math.ceil(stageW * s), H: Math.ceil(stageH * s), s, u: Math.max(1, s), headerH: 0, footerH: 0, dx: 0, dy: 0,
    };
  }
  if (options.fitWidth && options.preset !== 'double') {
    // A figure much taller than a slide (the results timeline): 1920 px wide, as tall as it needs.
    const { headerH, footerH } = bandsFor(SLIDE.width, 1);
    let s = SLIDE.width / stageW;
    const tallest = MAX_SIDE - headerH - footerH;
    if (stageH * s > tallest) s = tallest / stageH;
    return {
      W: Math.ceil(stageW * s), H: Math.ceil(stageH * s) + headerH + footerH, s, u: 1, headerH, footerH, dx: 0, dy: headerH,
    };
  }
  if (options.preset === 'double') {
    let s = 2;
    for (let attempt = 0; attempt < 3; attempt += 1) {
      const W = Math.ceil(stageW * s);
      const u = Math.min(2, Math.max(0.8, W / 1920));
      const { headerH, footerH } = bandsFor(W, u);
      const H = Math.ceil(stageH * s) + headerH + footerH;
      if (Math.max(W, H) <= MAX_SIDE) {
        return {
          W, H, s, u, headerH, footerH, dx: 0, dy: headerH,
        };
      }
      s *= (MAX_SIDE / Math.max(W, H)) * 0.98;
    }
  }
  const W = SLIDE.width;
  const H = SLIDE.height;
  const { headerH, footerH } = bandsFor(W, 1);
  const free = H - headerH - footerH;
  const s = Math.min(W / stageW, free / stageH);
  return {
    W, H, s, u: 1, headerH, footerH, dx: (W - stageW * s) / 2, dy: headerH + (free - stageH * s) / 2,
  };
}

function newCanvas(W, H) {
  const canvas = document.createElement('canvas');
  canvas.width = W;
  canvas.height = H;
  const ctx = canvas.getContext('2d');
  ctx.imageSmoothingQuality = 'high';
  return { canvas, ctx };
}

function fitFont(ctx, text, weight, size, family, maxWidth, floor = 0.62) {
  let px = size;
  ctx.font = `${weight} ${px}px ${family}`;
  while (px > size * floor && ctx.measureText(text).width > maxWidth) {
    px -= 1;
    ctx.font = `${weight} ${px}px ${family}`;
  }
  let out = text;
  while (out.length > 4 && ctx.measureText(out).width > maxWidth) out = `${out.slice(0, -2).trimEnd()}…`;
  return out;
}

function paintHeader(ctx, layout, info) {
  const { W, headerH, u } = layout;
  const family = fontFamily();
  const navy = cssToken('--navy', '#10283f');
  const amber = cssToken('--amber', '#f2b441');
  const teal = cssToken('--teal', '#54c6ba');
  const white = cssToken('--white', '#f4f7f8');
  const muted = cssToken('--muted', '#a9b3b9');
  ctx.fillStyle = navy;
  ctx.fillRect(0, 0, W, headerH);
  ctx.fillStyle = teal;
  ctx.fillRect(0, headerH - Math.max(2, Math.round(3 * u)), W, Math.max(2, Math.round(3 * u)));
  const pad = 28 * u;
  // Right: the timeline year, large, so it reads from the back of the room.
  ctx.textAlign = 'right';
  ctx.textBaseline = 'alphabetic';
  ctx.fillStyle = amber;
  ctx.font = `700 ${Math.round(40 * u)}px ${family}`;
  ctx.fillText(info.timeline.value, W - pad, headerH * 0.6);
  const yearWidth = ctx.measureText(info.timeline.value).width;
  ctx.fillStyle = muted;
  ctx.font = `600 ${Math.round(14 * u)}px ${family}`;
  ctx.fillText(info.timeline.label.toUpperCase(), W - pad, headerH * 0.6 + 20 * u);
  // Left: what it is a picture of.
  ctx.textAlign = 'left';
  const room = W - 2 * pad - Math.max(yearWidth, 150 * u) - 24 * u;
  const title = fitFont(ctx, info.title, 700, Math.round(34 * u), family, room);
  ctx.fillStyle = white;
  ctx.fillText(title, pad, headerH * 0.5);
  ctx.fillStyle = muted;
  const subtitle = fitFont(ctx, info.subtitle, 500, Math.round(18 * u), family, room, 0.7);
  ctx.fillText(subtitle, pad, headerH * 0.5 + 25 * u);
}

function paintFooter(ctx, layout, lines) {
  const { W, H, footerH, u } = layout;
  const family = fontFamily();
  const navy = cssToken('--navy', '#10283f');
  const white = cssToken('--white', '#f4f7f8');
  const muted = cssToken('--muted', '#a9b3b9');
  const top = H - footerH;
  ctx.fillStyle = navy;
  ctx.fillRect(0, top, W, footerH);
  ctx.textAlign = 'left';
  ctx.textBaseline = 'alphabetic';
  ctx.font = `500 ${Math.round(19 * u)}px ${family}`;
  let y = top + 13 * u + 19 * u;
  lines.forEach((line, index) => {
    ctx.fillStyle = index === 0 ? white : muted;
    for (const part of wrapLines(ctx, line, W - 56 * u)) {
      ctx.fillText(part, 28 * u, y);
      y += 25 * u;
    }
  });
}

// ----------------------------------------------------------------- globe

/** Waits until the globe has finished laying itself out: no rebuild or caption pass
 * pending (globe.js isSettled), and the markers and captions standing still. A picture
 * taken before that would show captions where they were, not where they are going. */
async function settleGlobe(globe, container) {
  await ensureFonts();
  const sample = () => [...container.querySelectorAll('.atlas-marker, .atlas-marker-label, .bl-pill')].slice(0, 200).map((el) => {
    const rect = el.getBoundingClientRect();
    return rect.left * 3 + rect.top;
  });
  let previous = sample();
  let stable = 0;
  for (let frame = 0; frame < 150 && stable < 12; frame += 1) {
    await nextFrame();
    const now = sample();
    const same = now.length === previous.length && now.every((value, i) => Math.abs(value - previous[i]) < 0.5);
    stable = same && (typeof globe.isSettled !== 'function' || globe.isSettled()) ? stable + 1 : 0;
    previous = now;
  }
}

function paintGlobeBackground(ctx, layout) {
  const stage = document.getElementById('globe-stage');
  const image = stage ? window.getComputedStyle(stage).backgroundImage : '';
  const stops = (image.match(/rgba?\([^)]*\)/g) || []);
  const inner = stops[0] || '#0f2231';
  const outer = stops[1] || '#060d14';
  const x = 0;
  const y = layout.headerH;
  const w = layout.W;
  const h = layout.H - layout.headerH - layout.footerH;
  ctx.save();
  ctx.beginPath();
  ctx.rect(x, y, w, h);
  ctx.clip();
  // `ellipse at center`, farthest-corner: a circle stretched to the box's own shape.
  ctx.translate(x + w / 2, y + h / 2);
  ctx.scale(1, h / w);
  const gradient = ctx.createRadialGradient(0, 0, 0, 0, 0, (w / 2) * Math.SQRT2);
  gradient.addColorStop(0, inner);
  gradient.addColorStop(1, outer);
  ctx.fillStyle = gradient;
  ctx.fillRect(-w, -w, 2 * w, 2 * w);
  ctx.restore();
}

/** A hairline round the view when the slide preset has fitted it inside a wider frame, so
 * the bars at its sides read as a margin and not as part of the picture. */
function paintViewFrame(ctx, layout, stageRect) {
  if (!layout.headerH || layout.dx < 2) return;
  ctx.save();
  ctx.strokeStyle = 'rgba(111,132,145,0.55)';
  ctx.lineWidth = 1;
  ctx.strokeRect(layout.dx + 0.5, layout.dy + 0.5, stageRect.width * layout.s - 1, stageRect.height * layout.s - 1);
  ctx.restore();
}

function paintSelectedRing(ctx, marker, xf) {
  const ring = window.getComputedStyle(marker, '::before');
  const size = parseFloat(ring.width);
  if (!size) return;
  const rect = marker.querySelector(':scope > svg').getBoundingClientRect();
  const centreX = rect.left + rect.width / 2;
  const centreY = rect.top + rect.height / 2;
  const box = {
    x: canvasX(xf, centreX - size / 2), y: canvasY(xf, centreY - size / 2), w: size * xf.s, h: size * xf.s,
  };
  paintStyledBox(ctx, ring, box, xf.s, { alpha: 1 });
}

async function paintMarker(ctx, marker, container, xf, stageRect) {
  const alpha = effectiveOpacity(marker, container);
  if (alpha <= 0.01) return;
  const svg = marker.querySelector(':scope > svg');
  const label = marker.querySelector('.atlas-marker-label');
  const leader = marker.querySelector('.atlas-marker-leader');
  const glyphRect = svg ? svg.getBoundingClientRect() : null;
  const labelShown = label && isShown(label) && window.getComputedStyle(label).display !== 'none';
  const labelRect = labelShown ? label.getBoundingClientRect() : null;
  const near = [glyphRect, labelRect].filter(Boolean);
  if (!near.some((rect) => intersects(rect, stageRect))) return;
  if (glyphRect) {
    if (marker.classList.contains('is-selected')) paintSelectedRing(ctx, marker, xf);
    const halos = [
      ...dropShadowHalos(window.getComputedStyle(marker).filter),
      ...dropShadowHalos(window.getComputedStyle(svg).filter),
    ];
    await paintGlyph(ctx, svg, xf, { alpha, halos });
  }
  if (leader && glyphRect) {
    paintLeader(ctx, leader, {
      x: glyphRect.left + glyphRect.width / 2, y: glyphRect.top + glyphRect.height / 2,
    }, xf, { alpha });
  }
  if (labelShown) {
    paintBox(ctx, label, xf, { alpha });
    paintText(ctx, label, xf, { alpha });
  }
}

function paintBeamLabel(ctx, outer, container, xf, stageRect) {
  const pill = outer.querySelector('.bl-pill');
  if (!pill || !isShown(pill)) return;
  const alpha = effectiveOpacity(outer, container);
  const rect = pill.getBoundingClientRect();
  if (!intersects(rect, stageRect)) return;
  const origin = outer.getBoundingClientRect();
  const leader = outer.querySelector('.bl-leader');
  if (leader) paintLeader(ctx, leader, { x: origin.left, y: origin.top }, xf, { alpha });
  paintBox(ctx, pill, xf, { alpha });
  paintText(ctx, pill, xf, { alpha });
}

async function paintGlobeOverlays(ctx, container, xf, stageRect) {
  const items = [...container.querySelectorAll('.atlas-marker, .atlas-beam-label')].map((el, order) => ({
    el, order, z: parseInt(window.getComputedStyle(el).zIndex, 10) || 0,
  })).sort((a, b) => (a.z - b.z) || (a.order - b.order));
  for (const { el } of items) {
    if (el.classList.contains('atlas-marker')) {
      if (el.classList.contains('is-absent') || !isShown(el)) continue;
      // eslint-disable-next-line no-await-in-loop
      await paintMarker(ctx, el, container, xf, stageRect);
    } else {
      paintBeamLabel(ctx, el, container, xf, stageRect);
    }
  }
}

async function composeGlobe(info, options) {
  const globe = env.getGlobe();
  if (!globe) {
    throw new ExportError('The globe needs WebGL, which this browser is not offering, so there is no globe to export. '
      + 'The list view cannot be exported as an image.');
  }
  const container = document.getElementById('globe-container');
  await settleGlobe(globe, container);
  const stageRect = container.getBoundingClientRect();
  if (!stageRect.width || !stageRect.height) throw new ExportError('The globe is not on screen, so there is nothing to export.');
  const date = todayISO();
  const footerLines = footerLinesFor(info, null, date);
  const layout = planLayout(options, stageRect.width, stageRect.height, footerLines);
  const { canvas, ctx } = newCanvas(layout.W, layout.H);
  if (layout.headerH) paintGlobeBackground(ctx, layout);
  else {
    ctx.fillStyle = cssToken('--paper', '#0b1620');
    ctx.fillRect(0, 0, layout.W, layout.H);
  }
  const frame = globe.captureFrame(layout.s);
  ctx.drawImage(frame, layout.dx, layout.dy, stageRect.width * layout.s, stageRect.height * layout.s);
  const xf = makeTransform(stageRect, layout.s, layout.dx, layout.dy);
  ctx.save();
  ctx.beginPath();
  ctx.rect(layout.dx, layout.dy, stageRect.width * layout.s, stageRect.height * layout.s);
  ctx.clip();
  await paintGlobeOverlays(ctx, container, xf, stageRect);
  ctx.restore();
  paintViewFrame(ctx, layout, stageRect);
  if (layout.headerH) {
    paintHeader(ctx, layout, info);
    paintFooter(ctx, layout, footerLines);
  }
  return {
    canvas, layout, info, footerLines, date, tiles: null, scaleBar: null,
  };
}

// ------------------------------------------------------------------- map

function currentTileLevel(container) {
  const levels = [...container.querySelectorAll('.leaflet-tile-pane .leaflet-tile-container')];
  let best = null;
  let bestZ = -Infinity;
  for (const level of levels) {
    const z = parseInt(level.style.zIndex, 10) || 0;
    if (z >= bestZ) { best = level; bestZ = z; }
  }
  return best;
}

/** Tiles the current view needs, as `{ total, pending, failed }`. A tile outside the view (Leaflet
 * keeps a margin loaded) is not waited for. */
function tileCounts(container) {
  const level = currentTileLevel(container);
  if (!level) return { total: 0, pending: 0 };
  const view = container.getBoundingClientRect();
  let total = 0;
  let pending = 0;
  let failed = 0;
  for (const tile of level.querySelectorAll('img.leaflet-tile')) {
    if (!intersects(tile.getBoundingClientRect(), view)) continue;
    total += 1;
    if (!(tile.complete && tile.naturalWidth > 0 && tile.classList.contains('leaflet-tile-loaded'))) {
      pending += 1;
      // Finished loading and still no picture: the request failed, so waiting longer is no use.
      if (tile.complete && tile.getAttribute('src') && tile.naturalWidth === 0) failed += 1;
    }
  }
  return { total, pending, failed };
}

async function settleMap(map, container) {
  await ensureFonts();
  const deadline = performance.now() + TILE_WAIT_MS;
  let lastView = '';
  let stable = 0;
  while (performance.now() < deadline && stable < 4) {
    await nextFrame();
    const center = map.getCenter();
    const key = `${center.lat.toFixed(6)},${center.lng.toFixed(6)},${map.getZoom()}`;
    const busy = map._animatingZoom || container.classList.contains('map-labels-busy')
      || container.classList.contains('leaflet-zoom-anim');
    stable = key === lastView && !busy ? stable + 1 : 0;
    lastView = key;
  }
}

/** Waits for the basemap tiles of the view to be in, up to TILE_WAIT_MS. */
async function waitForTiles(container) {
  const deadline = performance.now() + TILE_WAIT_MS;
  let quiet = 0;
  while (performance.now() < deadline) {
    const { total, pending, failed } = tileCounts(container);
    quiet = total > 0 && pending === 0 ? quiet + 1 : 0;
    if (quiet >= 3) return true;
    if (failed > 0 && failed === pending) return false;
    // eslint-disable-next-line no-await-in-loop
    await sleep(80);
  }
  const { total, pending } = tileCounts(container);
  return total > 0 && pending === 0;
}

const TILE_MESSAGES = {
  included: 'Basemap tiles are included. OpenStreetMap allows its tiles to be drawn into an image, and the credit is in the footer.',
  off: 'The basemap is switched off on the map, so the image has no tiles: the to-scale shapes are on a plain background.',
  polar: 'There is no basemap at the pole (OpenStreetMap’s tiles cannot represent it), so the image has none: the to-scale shapes are on a plain background.',
  incomplete: 'The basemap tiles had not all loaded (or the tile server would not let them be drawn into an image), so the image is made without them rather than half-covered: the to-scale shapes are on a plain background. If the map was still drawing, try again.',
  blocked: 'The browser would not let the tiles be drawn into an image (the tile server did not allow it), so the image has none: the to-scale shapes are on a plain background.',
};

function paintTiles(ctx, container, xf, stageRect) {
  const images = [...container.querySelectorAll('.leaflet-tile-pane img.leaflet-tile')]
    .filter((img) => img.complete && img.naturalWidth > 0 && img.classList.contains('leaflet-tile-loaded'));
  const levelOf = (img) => (img.parentElement ? parseInt(img.parentElement.style.zIndex, 10) || 0 : 0);
  images.sort((a, b) => levelOf(a) - levelOf(b));
  let drawn = 0;
  for (const img of images) {
    const rect = img.getBoundingClientRect();
    if (!intersects(rect, stageRect)) continue;
    // Whole device pixels, edge to edge: a tile on a fractional zoom lands between pixels.
    const x0 = Math.floor(canvasX(xf, rect.left));
    const y0 = Math.floor(canvasY(xf, rect.top));
    const x1 = Math.ceil(canvasX(xf, rect.right));
    const y1 = Math.ceil(canvasY(xf, rect.bottom));
    ctx.drawImage(img, x0, y0, x1 - x0, y1 - y0);
    drawn += 1;
  }
  return drawn;
}

function isTainted(ctx) {
  try {
    ctx.getImageData(0, 0, 1, 1);
    return false;
  } catch (error) {
    return true;
  }
}

/** 1, 2 or 5 times a power of ten, at most `metres`. */
export function niceLength(metres) {
  if (!(metres > 0)) return 0;
  const power = 10 ** Math.floor(Math.log10(metres));
  const digit = metres / power;
  return power * (digit >= 5 ? 5 : digit >= 2 ? 2 : 1);
}

export function lengthLabel(metres, unitOf = metres) {
  const km = unitOf >= 1000;
  const value = km ? metres / 1000 : metres;
  const text = Number.isInteger(value) ? String(value) : String(Math.round(value * 100) / 100);
  return `${text}${km ? ' km' : ' m'}`;
}

/** The metre scale bar, measured the way Leaflet's own scale control measures: with
 * the map's `distance()` between two points of one row of the view. */
function scaleBarFor(map) {
  const size = map.getSize();
  const y = Math.max(1, size.y - 34);
  const x0 = 24;
  const metresPerPixel = map.distance(
    map.containerPointToLatLng([x0, y]),
    map.containerPointToLatLng([x0 + 100, y]),
  ) / 100;
  if (!(metresPerPixel > 0) || !Number.isFinite(metresPerPixel)) return null;
  const metres = niceLength(metresPerPixel * Math.min(260, size.x * 0.3));
  if (!metres) return null;
  return { metres, cssPixels: metres / metresPerPixel, metresPerPixel };
}

function paintScaleBar(ctx, bar, xf, k) {
  const family = fontFamily();
  const white = cssToken('--white', '#f4f7f8');
  const ink = cssToken('--paper', '#0b1620');
  const length = bar.cssPixels * xf.s;
  const thick = 7 * k;
  const fontPx = Math.round(14 * k);
  const padding = 10 * k;
  const left = xf.dx + 14 * xf.s;
  const baseline = xf.dy + canvasHeightOfStage(xf) - 14 * xf.s;
  ctx.font = `600 ${fontPx}px ${family}`;
  const endLabelW = ctx.measureText(lengthLabel(bar.metres)).width;
  const boxW = length + 2 * padding + 4 * k + endLabelW + 6 * k;
  const boxH = thick + fontPx + 3.4 * padding;
  const boxX = left;
  const boxY = baseline - boxH;
  ctx.save();
  ctx.fillStyle = 'rgba(11,22,32,0.88)';
  roundedPath(ctx, boxX, boxY, boxW, boxH, [5 * k, 5 * k, 5 * k, 5 * k]);
  ctx.fill();
  ctx.strokeStyle = 'rgba(111,132,145,0.9)';
  ctx.lineWidth = Math.max(1, k);
  ctx.stroke();
  const x0 = boxX + padding + 4 * k;
  const barY = boxY + boxH - padding - thick;
  // Two alternating segments, so the half-way point is readable without a ruler.
  ctx.fillStyle = white;
  ctx.fillRect(x0, barY, length / 2, thick);
  ctx.fillStyle = ink;
  ctx.fillRect(x0 + length / 2, barY, length / 2, thick);
  ctx.strokeStyle = white;
  ctx.lineWidth = Math.max(1.5, 1.6 * k);
  ctx.strokeRect(x0, barY, length, thick);
  ctx.fillStyle = white;
  ctx.font = `600 ${fontPx}px ${family}`;
  ctx.textBaseline = 'alphabetic';
  const labelY = barY - 6 * k;
  ctx.textAlign = 'left';
  ctx.fillText('0', x0 - 2 * k, labelY);
  ctx.textAlign = 'center';
  ctx.fillText(lengthLabel(bar.metres / 2, bar.metres), x0 + length / 2, labelY);
  ctx.textAlign = 'left';
  ctx.fillText(lengthLabel(bar.metres), x0 + length + 3 * k, labelY);
  ctx.restore();
  return { x: x0, y: barY, width: length, thickness: thick };
}

function canvasHeightOfStage(xf) {
  return xf.stageHeight * xf.s;
}

function paintNorthArrow(ctx, xf, polar, k) {
  const family = fontFamily();
  const white = cssToken('--white', '#f4f7f8');
  const amber = cssToken('--amber', '#f2b441');
  const stageW = xf.stageWidth * xf.s;
  const label = polar ? 'grid north (0° meridian)' : 'N';
  const fontPx = Math.round((polar ? 12 : 17) * k);
  ctx.save();
  ctx.font = `700 ${fontPx}px ${family}`;
  const textW = ctx.measureText(label).width;
  const boxW = Math.max(46 * k, textW + 20 * k);
  const boxH = (polar ? 76 : 70) * k;
  const x = xf.dx + stageW - 14 * xf.s - boxW;
  const y = xf.dy + 14 * xf.s;
  ctx.fillStyle = 'rgba(11,22,32,0.88)';
  roundedPath(ctx, x, y, boxW, boxH, [6 * k, 6 * k, 6 * k, 6 * k]);
  ctx.fill();
  ctx.strokeStyle = polar ? amber : 'rgba(111,132,145,0.9)';
  ctx.lineWidth = Math.max(1, k);
  ctx.stroke();
  const cx = x + boxW / 2;
  ctx.fillStyle = white;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'alphabetic';
  ctx.fillText(label, cx, y + 10 * k + fontPx * 0.8);
  // The arrow itself: a head and a stem pointing up the page.
  const tipY = y + 10 * k + fontPx + 6 * k;
  const baseY = y + boxH - 9 * k;
  ctx.beginPath();
  ctx.moveTo(cx, tipY);
  ctx.lineTo(cx + 8 * k, tipY + 14 * k);
  ctx.lineTo(cx + 2.4 * k, tipY + 11 * k);
  ctx.lineTo(cx + 2.4 * k, baseY);
  ctx.lineTo(cx - 2.4 * k, baseY);
  ctx.lineTo(cx - 2.4 * k, tipY + 11 * k);
  ctx.lineTo(cx - 8 * k, tipY + 14 * k);
  ctx.closePath();
  ctx.fillStyle = white;
  ctx.fill();
  ctx.restore();
}

function paintAttributionChip(ctx, lines, xf, k) {
  const family = fontFamily();
  ctx.save();
  const fontPx = Math.round(12 * k);
  ctx.font = `500 ${fontPx}px ${family}`;
  const width = Math.max(...lines.map((line) => ctx.measureText(line).width)) + 14 * k;
  const height = lines.length * fontPx * 1.35 + 8 * k;
  const x = xf.dx + xf.stageWidth * xf.s - 10 * xf.s - width;
  const y = xf.dy + xf.stageHeight * xf.s - 10 * xf.s - height;
  ctx.fillStyle = 'rgba(11,22,32,0.88)';
  roundedPath(ctx, x, y, width, height, [4 * k, 4 * k, 4 * k, 4 * k]);
  ctx.fill();
  ctx.fillStyle = cssToken('--white', '#f4f7f8');
  ctx.textAlign = 'left';
  ctx.textBaseline = 'alphabetic';
  lines.forEach((line, i) => ctx.fillText(line, x + 7 * k, y + 4 * k + fontPx * (1.05 + i * 1.35)));
  ctx.restore();
}

async function paintMapLayers(ctx, container, xf, stageRect, withTiles) {
  const result = { tiles: 0 };
  if (withTiles) result.tiles = paintTiles(ctx, container, xf, stageRect);
  // The vector layer: the features the atlas drew, as the live SVG.
  const svg = container.querySelector('.leaflet-overlay-pane > svg');
  if (svg) {
    const layer = await rasterizeSvgLayer(svg, xf.s);
    ctx.drawImage(layer.image, canvasX(xf, layer.rect.left), canvasY(xf, layer.rect.top),
      layer.rect.width * xf.s, layer.rect.height * xf.s);
  }
  // Symbols (the small marks for features too small to see), then labels.
  const symbols = [...container.querySelectorAll('.leaflet-marker-pane .map-symbol')];
  for (const symbol of symbols) {
    if (!isShown(symbol)) continue;
    const alpha = effectiveOpacity(symbol, container);
    paintBox(ctx, symbol, xf, { alpha });
  }
  const labels = [...container.querySelectorAll('.leaflet-tooltip-pane .map-label')]
    .map((el, order) => ({ el, order, z: parseInt(window.getComputedStyle(el).zIndex, 10) || 0 }))
    .sort((a, b) => (a.z - b.z) || (a.order - b.order));
  for (const { el } of labels) {
    if (!isShown(el) || !intersects(el.getBoundingClientRect(), stageRect)) continue;
    const alpha = effectiveOpacity(el, container);
    paintBox(ctx, el, xf, { alpha });
    paintText(ctx, el, xf, { alpha });
  }
  return result;
}

async function composeMap(info, options) {
  const mapInfo = localmap.exportInfo();
  if (!mapInfo) throw new ExportError('The map is not drawn yet, so there is nothing to export.');
  const { map } = mapInfo;
  const container = map.getContainer();
  await settleMap(map, container);
  const stageRect = container.getBoundingClientRect();
  if (!stageRect.width || !stageRect.height) throw new ExportError('The map is not on screen, so there is nothing to export.');
  let tilesState = 'included';
  if (mapInfo.polar) tilesState = 'polar';
  else if (!mapInfo.basemap) tilesState = 'off';
  else if (options.tiles === false) tilesState = 'blocked';
  else if (!(await waitForTiles(container))) tilesState = 'incomplete';
  const date = todayISO();

  const build = async (state0) => {
    const tiles = { state: state0, message: TILE_MESSAGES[state0] };
    const footerLines = footerLinesFor({ ...info, mapInfo }, tiles, date);
    const layout = planLayout(options, stageRect.width, stageRect.height, footerLines);
    const { canvas, ctx } = newCanvas(layout.W, layout.H);
    ctx.fillStyle = layout.headerH ? cssToken('--paper', '#0b1620') : '#0b1620';
    ctx.fillRect(0, 0, layout.W, layout.H);
    const xf = makeTransform(stageRect, layout.s, layout.dx, layout.dy);
    xf.stageWidth = stageRect.width;
    xf.stageHeight = stageRect.height;
    const k = Math.max(1.15, layout.s);
    ctx.save();
    ctx.beginPath();
    ctx.rect(layout.dx, layout.dy, stageRect.width * layout.s, stageRect.height * layout.s);
    ctx.clip();
    // The plain background the to-scale shapes sit on when there are no tiles.
    ctx.fillStyle = '#0b1620';
    ctx.fillRect(layout.dx, layout.dy, stageRect.width * layout.s, stageRect.height * layout.s);
    const drawn = await paintMapLayers(ctx, container, xf, stageRect, state0 === 'included');
    const bar = scaleBarFor(map);
    const scaleBar = bar ? { ...bar, ...paintScaleBar(ctx, bar, xf, k), canvasPixels: bar.cssPixels * layout.s } : null;
    paintNorthArrow(ctx, xf, mapInfo.polar, k);
    if (!layout.headerH) {
      const credits = [];
      if (state0 === 'included') credits.push('© OpenStreetMap contributors');
      if (mapInfo.attribution.length) credits.push(`Geometry: ${mapInfo.attribution.join('; ')}`);
      if (credits.length) paintAttributionChip(ctx, credits, xf, k);
    }
    ctx.restore();
    paintViewFrame(ctx, layout, stageRect);
    if (layout.headerH) {
      paintHeader(ctx, layout, info);
      paintFooter(ctx, layout, footerLines);
    }
    return {
      canvas, ctx, layout, info, footerLines, date, tiles: { ...tiles, drawn: drawn.tiles }, scaleBar,
    };
  };

  let out = await build(tilesState);
  if (tilesState === 'included' && isTainted(out.ctx)) out = await build('blocked');
  return out;
}

// ---------------------------------------------------------------- a view's figure

const FIGURE_PAD = 18;
const FIGURE_GAP = 16;
// Below this scale a figure on a 1920 x 1080 slide would be drawn too small to read.
const TALL_FIGURE_SCALE = 0.7;

/** The figure of the view on screen. The view host hands over its SVG(s) (views/host.js): the
 * shapes are drawn as the image the browser makes of each live SVG and the text from the page's
 * own fonts, on a panel in the page's own colours, under the same title band and above the same
 * citation footer as a globe or a map. Several SVGs (the beam section and the whole Earth) stand
 * side by side ("row") or one above the other ("column"). */
async function composeFigure(info, options) {
  if (!env.views) throw new ExportError('Views cannot be exported yet.');
  let exported = null;
  try {
    exported = await env.views.exportFigure();
  } catch (error) {
    throw new ExportError(error.message);
  }
  try {
    await ensureFonts();
    const sizes = exported.figures.map((svg) => svg.getBoundingClientRect());
    if (sizes.some((rect) => !rect.width || !rect.height)) {
      throw new ExportError('The figure is not on screen yet, so there is nothing to export. Try again in a moment.');
    }
    const row = exported.layout === 'row';
    const innerW = row
      ? sizes.reduce((sum, rect) => sum + rect.width, 0) + FIGURE_GAP * (sizes.length - 1)
      : Math.max(...sizes.map((rect) => rect.width));
    const innerH = row
      ? Math.max(...sizes.map((rect) => rect.height))
      : sizes.reduce((sum, rect) => sum + rect.height, 0) + FIGURE_GAP * (sizes.length - 1);
    const stage = { width: innerW + 2 * FIGURE_PAD, height: innerH + 2 * FIGURE_PAD };
    const date = todayISO();
    let footerLines = footerLinesFor({ ...info, notes: exported.notes }, null, date);
    let layout = planLayout(options, stage.width, stage.height, footerLines);
    if (options.preset !== 'double' && layout.s < TALL_FIGURE_SCALE) {
      // On a slide this figure would be drawn too small to read: it keeps a readable size and the
      // picture is taller than a slide, with a line in the footer that says so.
      const tallLines = [...footerLines, 'This figure is taller than a slide, so the picture is 1920 px wide and as tall as it needs to be.'];
      const taller = planLayout({ ...options, fitWidth: true }, stage.width, stage.height, tallLines);
      if (taller.s > layout.s) {
        layout = taller;
        footerLines = tallLines;
      }
    }
    const { canvas, ctx } = newCanvas(layout.W, layout.H);
    // The page's own ground, then the panel the figure sits on (the stage is the figures and their margin).
    ctx.fillStyle = cssToken('--paper', '#0b1620');
    ctx.fillRect(0, 0, layout.W, layout.H);
    ctx.fillStyle = cssToken('--panel', '#10283f');
    ctx.fillRect(layout.dx, layout.dy, stage.width * layout.s, stage.height * layout.s);
    let cursor = FIGURE_PAD;
    for (let i = 0; i < exported.figures.length; i += 1) {
      const rect = sizes[i];
      const offsetX = row ? cursor : FIGURE_PAD + (innerW - rect.width) / 2;
      const offsetY = row ? FIGURE_PAD : cursor;
      const xf = makeTransform(rect, layout.s, layout.dx + offsetX * layout.s, layout.dy + offsetY * layout.s);
      // eslint-disable-next-line no-await-in-loop
      await paintSvgFigure(ctx, exported.figures[i], xf);
      cursor += (row ? rect.width : rect.height) + FIGURE_GAP;
    }
    paintViewFrame(ctx, layout, { width: stage.width, height: stage.height });
    if (layout.headerH) {
      paintHeader(ctx, layout, info);
      paintFooter(ctx, layout, footerLines);
    }
    return {
      canvas, layout, info, footerLines, date, tiles: null, scaleBar: null,
    };
  } finally {
    exported.release();
  }
}

// ----------------------------------------------------------------- public

/**
 * Draws the view on screen. Options: `preset` ('slide' | 'double'), `bands: false` for a
 * bare snapshot of the stage (the facility sheet's map), `scale` for that snapshot,
 * `tiles: false` to leave the basemap out. Resolves to
 * `{ canvas, filename, kind, tiles, scaleBar, footerLines, width, height }`.
 */
export async function composeView(options = {}) {
  if (!env) throw new ExportError('Export is not ready yet.');
  const info = describeView();
  const compose = { map: composeMap, figure: composeFigure, globe: composeGlobe }[info.kind];
  const result = await compose(info, options);
  const summary = {
    kind: info.kind,
    filename: info.filename,
    title: info.title,
    subtitle: info.subtitle,
    timeline: info.timeline.value,
    width: result.canvas.width,
    height: result.canvas.height,
    footerLines: result.footerLines,
    tiles: result.tiles,
    scaleBar: result.scaleBar,
    preset: options.preset || 'slide',
  };
  window.__hepAtlasExport = { ...(window.__hepAtlasExport || {}), last: summary };
  return { ...summary, canvas: result.canvas };
}

export function downloadCanvas(canvas, filename) {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (!blob) {
        reject(new ExportError('The browser could not encode the image.'));
        return;
      }
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      link.rel = 'noopener';
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 30000);
      resolve(blob.size);
    }, 'image/png');
  });
}

// ---------------------------------------------------------------- dialog

function h(tag, attrs = {}, children = []) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (key === 'class') el.className = value;
    else if (key === 'text') el.textContent = value;
    else if (value !== null && value !== undefined && value !== false) el.setAttribute(key, value === true ? '' : value);
  }
  for (const child of [].concat(children)) {
    if (child == null) continue;
    el.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
  }
  return el;
}

// Set by createDialog: re-reads whether the Export button can be used on the view on screen.
let refreshExportButton = () => {};

function createDialog() {
  const button = document.getElementById('export-btn');
  const popover = document.getElementById('export-popover');
  if (!button || !popover) return;

  const title = h('h2', { class: 'export-title', id: 'export-title' }, 'Save this view as an image');
  const closeX = h('button', { type: 'button', class: 'export-close', 'aria-label': 'Close export' }, '×');
  const lede = h('p', { class: 'export-lede', id: 'export-lede' });
  const sizes = h('fieldset', { class: 'export-sizes' }, [h('legend', {}, 'Size')]);
  const radios = {};
  const dims = {};
  for (const [value, label] of [['slide', 'Slide'], ['double', 'Twice the size on screen']]) {
    const input = h('input', { type: 'radio', name: 'export-size', value });
    const dim = h('span', { class: 'export-dim' });
    radios[value] = input;
    dims[value] = dim;
    sizes.appendChild(h('label', { class: 'export-size' }, [input, h('span', {}, [`${label} `, dim])]));
  }
  radios.slide.checked = true;
  const preview = h('div', { class: 'export-preview' });
  const notes = h('div', { class: 'export-notes' });
  const status = h('p', { class: 'export-status', role: 'status', 'aria-live': 'polite' });
  const download = h('button', { type: 'button', class: 'primary-btn export-download', disabled: true }, 'Download PNG');
  const dismiss = h('button', { type: 'button', class: 'text-btn' }, 'Close');
  popover.append(title, closeX, lede, sizes, preview, notes, status, h('div', { class: 'export-actions' }, [download, dismiss]));
  popover.setAttribute('aria-labelledby', 'export-title');

  let open = false;
  let token = 0;
  let current = null;
  let refreshTimer = 0;

  // On a view the button is offered only while there is a figure to make the picture from. Where
  // there is none (a table, an error, a view still loading) it is disabled and says why, in its
  // tooltip and for a screen reader: it never opens a dialog that cannot do anything.
  const reasonEl = h('span', { class: 'visually-hidden', id: 'export-reason' });
  button.after(reasonEl);
  function refreshButton() {
    const entity = state.get().entity;
    let reason = '';
    if (entity && entity.type === 'view') {
      const info = viewExportState(entity.slug);
      if (!info.ready) reason = info.reason || 'This view has no figure to export.';
    }
    button.disabled = !!reason;
    button.title = reason ? `Save image: unavailable. ${reason}`
      : 'Save image: download what is on screen as a picture for a slide, with its title, year and citation';
    reasonEl.textContent = reason ? `Export is unavailable. ${reason}` : '';
    if (reason) button.setAttribute('aria-describedby', 'export-reason');
    else button.removeAttribute('aria-describedby');
    if (reason && open) setOpen(false, { restoreFocus: false });
  }

  const presetValue = () => (radios.double.checked ? 'double' : 'slide');

  function say(text) { status.textContent = text; }

  function showNotes(result) {
    notes.replaceChildren();
    if (!result) return;
    const contents = result.kind === 'map'
      ? 'In the image: the map, its title, the timeline year, a metre scale bar, a north arrow and the citation.'
      : (result.kind === 'figure'
        ? 'In the image: the figure of this view as it is drawn on screen, its title, the timeline year, the address of the view and the citation.'
        : 'In the image: the globe with its markers, captions and beams, the title, the timeline year and the citation.');
    notes.appendChild(h('p', { class: 'export-contents' }, contents));
    if (result.tiles) {
      notes.appendChild(h('p', {
        class: `export-tiles is-${result.tiles.state}`, role: result.tiles.state === 'included' ? null : 'note',
      }, result.tiles.message));
    }
    notes.appendChild(h('p', { class: 'export-file' }, [h('span', {}, 'File: '), h('code', {}, result.filename)]));
  }

  const routeType = () => { const e = state.get().entity; return e ? e.type : null; };

  function whatIs() {
    if (routeType() === 'view') {
      const info = viewExportState(state.get().entity.slug);
      return info.ready ? `The figure on screen: ${info.title}.` : 'The figure of this view.';
    }
    const mapOpen = routeType() === 'map' && localmap.exportInfo();
    return mapOpen ? 'The local map on screen.' : 'The globe on screen.';
  }

  function updateDims() {
    const stage = routeType() === 'view' ? null
      : document.getElementById(routeType() === 'map' ? 'map-canvas' : 'globe-container');
    const rect = stage ? stage.getBoundingClientRect() : null;
    dims.slide.textContent = `${SLIDE.width} × ${SLIDE.height} px`;
    dims.double.textContent = rect && rect.width ? `about ${Math.round(rect.width * 2)} × ${Math.round(rect.height * 2)} px` : '';
  }

  async function render() {
    const mine = ++token;
    download.disabled = true;
    current = null;
    lede.textContent = whatIs();
    updateDims();
    say('Preparing the image…');
    preview.classList.add('is-busy');
    try {
      const result = await composeView({ preset: presetValue() });
      if (mine !== token) return;
      current = result;
      result.canvas.className = 'export-canvas';
      result.canvas.setAttribute('role', 'img');
      result.canvas.setAttribute('aria-label', `Preview of the image: ${result.title}, ${result.timeline}.`);
      preview.replaceChildren(result.canvas);
      dims[presetValue()].textContent = `${result.width} × ${result.height} px`;
      showNotes(result);
      download.disabled = false;
      say(`Ready: ${result.width} by ${result.height} pixels.`);
    } catch (error) {
      if (mine !== token) return;
      preview.replaceChildren(h('p', { class: 'export-error', role: 'alert' }, error instanceof ExportError
        ? error.message : `The image could not be made: ${error.message}`));
      notes.replaceChildren();
      say('');
      window.console.error(error);
    } finally {
      if (mine === token) preview.classList.remove('is-busy');
    }
  }

  function setOpen(next, { restoreFocus = true } = {}) {
    if (next === open) return;
    open = next;
    popover.hidden = !next;
    button.setAttribute('aria-expanded', String(next));
    if (next) {
      popover.focus({ preventScroll: true });
      render();
    } else {
      token += 1;
      window.clearTimeout(refreshTimer);
      preview.replaceChildren();
      current = null;
      if (restoreFocus) button.focus({ preventScroll: true });
    }
  }

  button.addEventListener('click', () => setOpen(!open));
  closeX.addEventListener('click', () => setOpen(false));
  dismiss.addEventListener('click', () => setOpen(false));
  for (const input of Object.values(radios)) input.addEventListener('change', () => render());
  // The button stays enabled while it saves (a disabled button drops the focus it holds).
  let saving = false;
  download.addEventListener('click', async () => {
    if (!current || saving) return;
    saving = true;
    try {
      const bytes = await downloadCanvas(current.canvas, current.filename);
      say(`Saved ${current.filename} (${Math.round(bytes / 1024)} KB).`);
    } catch (error) {
      say(error.message);
    } finally {
      saving = false;
    }
  });

  // The picture follows the view while the dialog is open (a year, a selection), so the
  // preview is always the file that would be saved.
  state.subscribe(() => {
    refreshButton();
    if (!open) return;
    window.clearTimeout(refreshTimer);
    refreshTimer = window.setTimeout(() => { if (open) render(); }, 450);
  });
  refreshExportButton = refreshButton;
  refreshButton();

  document.addEventListener('pointerdown', (event) => {
    if (!open || popover.contains(event.target) || button.contains(event.target)) return;
    setOpen(false, { restoreFocus: false });
  });
  // Capture phase, like the Key popover: Escape closes this before it closes the panel.
  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape' || !open) return;
    event.stopPropagation();
    setOpen(false);
  }, true);
}

// ------------------------------------------------------- facility sheet

function regionName(code) {
  try {
    return new Intl.DisplayNames(['en'], { type: 'region' }).of(code) || code;
  } catch (error) {
    return code;
  }
}

function degrees(value, positive, negative) {
  return `${Math.abs(value).toFixed(4)}° ${value >= 0 ? positive : negative}`;
}

/** Years an experiment ran: from the start of its first `active` interval to the end of
 * its last, or "present" while it has not ended. An experiment that never ran says where
 * it stands instead (proposed, approved, under construction). */
export function operatingYears(experiment) {
  const year = (value) => {
    const text = value && typeof value === 'object' ? (value.date || '') : String(value || '');
    const match = /^(\d{4})/.exec(text);
    return match ? Number(match[1]) : null;
  };
  const intervals = experiment.intervals || [];
  const active = intervals.filter((iv) => iv.status === 'active' && year(iv.start) != null);
  const ended = ['completed', 'decommissioned', 'cancelled'].includes(experiment.status);
  if (active.length) {
    const start = Math.min(...active.map((iv) => year(iv.start)));
    if (!ended) return { text: `${start}–present`, from: start };
    const ends = active.map((iv) => year(iv.end)).filter((v) => v != null);
    const done = intervals.find((iv) => iv.status === 'completed' && year(iv.start) != null);
    const end = ends.length ? Math.max(...ends) : (done ? year(done.start) : null);
    return { text: end && end !== start ? `${start}–${end}` : String(start), from: start };
  }
  if (ended) {
    const spans = intervals.filter((iv) => iv.status === 'completed' && year(iv.start) != null && year(iv.end) != null);
    if (spans.length) {
      const from = year(spans[0].start);
      return { text: `${from}–${year(spans[0].end)}`, from };
    }
  }
  const words = {
    proposed: 'proposed', approved: 'approved', planned: 'planned', construction: 'building', commissioning: 'commissioning',
  };
  const first = intervals.find((iv) => iv.status === experiment.status && year(iv.start) != null);
  const from = first ? year(first.start) : 9999;
  return { text: `${words[experiment.status] || titleCase(experiment.status).toLowerCase()}${first ? ` ${from}` : ''}`, from };
}

const SPEC_WORDS = { cms_energy: 'centre-of-mass energy', peak_luminosity: 'peak luminosity' };
// A machine that is not built yet. Its numbers are design values, and a sheet that listed them with
// the machines that run (CERN: FCC-ee's circumference and depth, CLIC's energy) would read as
// specifications of the laboratory. They are listed apart, each with its status.
const NOT_BUILT = { proposed: 'proposed', planned: 'planned', approved: 'approved, not built' };
const STATUS_NOTE = { construction: 'under construction', commissioning: 'commissioning' };

function specRows(facility) {
  const own = Object.entries(facility.specs || {}).map(([key, value]) => [titleCase(key), quantityText(value)]);
  if (own.length) return { rows: own, proposed: [], note: '' };
  // An accelerator laboratory records its numbers on its accelerators.
  const accelerators = (facility.accelerator_ids || []).map((id) => env.atlas.accelerators[id]).filter(Boolean)
    .filter((a) => !['decommissioned', 'completed', 'cancelled'].includes(a.status));
  const label = (key) => SPEC_WORDS[key] || titleCase(key).toLowerCase();
  const specText = (a) => Object.entries(a.specs || {}).slice(0, 3).map(([key, value]) => `${label(key)} ${quantityText(value)}`).join('; ');
  const rows = accelerators.filter((a) => !NOT_BUILT[a.status])
    .map((a) => [STATUS_NOTE[a.status] ? `${a.name} (${STATUS_NOTE[a.status]})` : a.name, specText(a)])
    .filter(([, text]) => text).slice(0, 7);
  const proposed = accelerators.filter((a) => NOT_BUILT[a.status])
    .map((a) => [`${a.name} (${NOT_BUILT[a.status]})`, specText(a)])
    .filter(([, text]) => text).slice(0, 4);
  return { rows, proposed, note: rows.length || proposed.length ? 'Recorded on the facility’s accelerators.' : '' };
}

function statusLine(facility, current) {
  const timelineState = current.range ? { range: current.range } : { year: current.year };
  const when = current.range ? `${current.range[0]}–${current.range[1]}` : String(timelineText(current).value);
  const resolved = statusForTimeline(facility.state_segments, timelineState);
  if (resolved) {
    return `${titleCase(resolved.status)}${resolved.certainty === 'possible' ? ' (uncertain)' : ''} in ${when}`;
  }
  const reason = timelineAbsenceReason(facility.state_segments, timelineState);
  return ({
    not_yet: `Not yet proposed in ${when}`,
    ended: `No longer active in ${when}`,
    gap: `No recorded status in ${when}`,
    no_history: 'No timeline data recorded',
  })[reason] || 'No timeline data recorded';
}

function shortSource(source) {
  const title = source.title || source.id;
  let where = '';
  try {
    const url = new URL(source.url);
    const arxiv = /arxiv\.org\/abs\/(.+)$/.exec(source.url);
    where = arxiv ? `arXiv:${arxiv[1]}` : `${url.hostname.replace(/^www\./, '')}${url.pathname.length > 1 ? url.pathname : ''}`;
    if (where.length > 52) where = `${where.slice(0, 51)}…`;
  } catch (error) { /* no usable address */ }
  const who = source.publisher && !title.includes(source.publisher) ? source.publisher : '';
  return { title, who, where, accessed: source.accessed || '' };
}

function pointerSources(entries) {
  const found = [];
  const walk = (value) => {
    if (!value) return;
    if (Array.isArray(value)) { value.forEach(walk); return; }
    if (Array.isArray(value.sources)) for (const id of value.sources) if (!found.includes(id)) found.push(id);
  };
  Object.values(entries || {}).forEach(walk);
  return found;
}

async function sheetData(facilityId) {
  const { atlas } = env;
  const facility = atlas.facilities[facilityId];
  const current = state.get();
  const [text, provenance, sources] = await Promise.all([
    loader.getText().catch(() => ({})), loader.getProvenance().catch(() => ({})), loader.getSources().catch(() => ({ byId: {} })),
  ]);
  const site = atlas.sites[facility.primary_site_id];
  const place = site && site.place ? [site.place.city, site.place.region].filter(Boolean).join(', ') : '';
  const countries = (facility.country || []).map(regionName).join(' and ');
  const coordinates = site && site.coordinates;
  let where = '';
  if (coordinates && coordinates.lat != null) {
    where = `${degrees(coordinates.lat, 'N', 'S')}, ${degrees(coordinates.lon, 'E', 'W')}`;
    if (coordinates.approximate) {
      where += ` (${coordinates.kind ? `${String(coordinates.kind).replace(/_/g, ' ')} point` : 'campus point'}`
        + `${coordinates.precision_m ? `, to about ${coordinates.precision_m} m` : ''})`;
    }
  }
  const experiments = (facility.experiment_ids || []).map((id) => atlas.experiments[id]).filter(Boolean)
    .map((experiment) => ({ name: experiment.name, ...operatingYears(experiment) }))
    .sort((a, b) => (a.from - b.from) || a.name.localeCompare(b.name));
  const cited = pointerSources(provenance[facilityId]);
  const byId = sources.byId || {};
  const list = cited.map((id) => byId[id]).filter(Boolean).map(shortSource);
  return {
    facility,
    summary: (facility.summary && facility.summary.plain) || (text[facilityId] && text[facilityId].summary_plain) || '',
    kind: kindLabel(facility.kind),
    status: statusLine(facility, current),
    location: [place, countries].filter(Boolean).join(' — '),
    coordinates: where,
    specs: specRows(facility),
    experiments,
    sources: list,
    sourceCount: cited.length,
  };
}

function sheetNode(data, snapshot, date) {
  const { facility } = data;
  const slug = facility.id.split(':')[1];
  const section = (heading, ...nodes) => h('section', { class: 'ps-section' }, [h('h2', {}, heading), ...nodes.flat()]);
  const sheet = h('div', { class: 'print-sheet', id: 'print-sheet' });
  sheet.append(
    h('header', { class: 'ps-head' }, [
      h('p', { class: 'ps-brand' }, 'HEP Atlas · Facility sheet'),
      h('h1', { class: 'ps-title' }, facility.name),
      h('p', { class: 'ps-kind' }, [data.kind, ' · ', data.status]),
      h('p', { class: 'ps-where' }, [data.location, data.coordinates ? ` · ${data.coordinates}` : '']),
    ]),
    data.summary ? section('What it is', h('p', { class: 'ps-summary' }, data.summary)) : null,
  );
  const columns = h('div', { class: 'ps-columns' });
  const specList = (rows) => h('dl', { class: 'ps-specs' }, rows.flatMap(([key, value]) => [h('dt', {}, key), h('dd', {}, value)]));
  const specs = data.specs.rows.length
    ? specList(data.specs.rows)
    : (data.specs.proposed.length ? null : h('p', { class: 'ps-none' }, 'None recorded in the Atlas for this facility.'));
  columns.append(
    section('Key specifications', specs,
      // Machines not built yet: apart from the ones that run, each with its status.
      data.specs.proposed.length ? [
        h('p', { class: 'ps-note ps-proposed-head' }, 'Proposed or planned machines, not built (design values):'),
        specList(data.specs.proposed),
      ] : null,
      data.specs.note ? h('p', { class: 'ps-note' }, data.specs.note) : null),
    section('Experiments hosted', data.experiments.length
      ? [
        h('ul', { class: `ps-experiments${data.experiments.length > 8 ? ' is-long' : ''}` }, data.experiments.slice(0, MAX_SHEET_EXPERIMENTS).map((e) => h('li', {}, [
          h('span', { class: 'ps-exp-name' }, e.name), h('span', { class: 'ps-exp-years' }, e.text),
        ]))),
        data.experiments.length > MAX_SHEET_EXPERIMENTS
          ? h('p', { class: 'ps-note' }, `and ${data.experiments.length - MAX_SHEET_EXPERIMENTS} more, listed in the facility\u2019s panel in the Atlas.`) : null,
      ]
      : h('p', { class: 'ps-none' }, 'None recorded in the Atlas.')),
  );
  sheet.append(columns);
  const figure = h('figure', { class: 'ps-map' });
  if (snapshot && snapshot.url) {
    figure.append(
      h('img', { src: snapshot.url, alt: `Local map of ${facility.name}, drawn to scale, with a scale bar and a north arrow.` }),
      h('figcaption', {}, snapshot.caption),
    );
  } else {
    figure.append(h('p', { class: 'ps-none' }, snapshot && snapshot.error
      ? `The local map could not be drawn for this sheet: ${snapshot.error}`
      : 'No local map has been published for this facility yet.'));
  }
  sheet.append(figure);
  const shown = data.sources.slice(0, MAX_SHEET_SOURCES);
  sheet.append(section('Sources',
    shown.length
      ? h('ol', { class: 'ps-sources' }, shown.map((s) => h('li', {}, [
        h('span', { class: 'ps-src-title' }, s.title),
        s.who ? h('span', { class: 'ps-src-who' }, ` — ${s.who}`) : null,
        s.where ? h('span', { class: 'ps-src-where' }, ` (${s.where})`) : null,
      ])))
      : h('p', { class: 'ps-none' }, 'No sourced fields are recorded for this facility yet.'),
    data.sources.length > shown.length
      ? h('p', { class: 'ps-note' }, `and ${data.sources.length - shown.length} more, listed in the facility’s panel in the Atlas.`) : null));
  sheet.append(h('footer', { class: 'ps-foot' }, [
    h('p', {}, citationLine(date)),
    h('p', {}, `Record: ${SITE_ADDRESS}#/facility/${slug}`),
  ]));
  return sheet;
}

function waitFor(predicate, ms) {
  const deadline = performance.now() + ms;
  return new Promise((resolve) => {
    const tick = () => {
      if (predicate()) resolve(true);
      else if (performance.now() > deadline) resolve(false);
      else window.requestAnimationFrame(tick);
    };
    tick();
  });
}

/** A to-scale snapshot of a facility's local map: opens the map route, draws it, and puts
 * the reader back where they were. If the map for this facility is already open, that is
 * the snapshot. */
async function snapshotMap(slug, mapName) {
  const before = state.get();
  const onIt = before.entity && before.entity.type === 'map' && before.entity.slug === slug && !!localmap.exportInfo();
  try {
    if (!onIt) {
      state.navigate({
        entity: { type: 'map', slug }, sel: null, levels: null, basemap: true,
      }, { replace: true });
      const ready = await waitFor(() => {
        const info = localmap.exportInfo();
        const el = info && info.map.getContainer();
        return info && info.meta.id === `map:${slug}` && el && el.getBoundingClientRect().width > 0;
      }, 15000);
      if (!ready) throw new Error('the map did not open');
    }
    const result = await composeView({ bands: false, scale: 2 });
    const blob = await new Promise((resolve) => { result.canvas.toBlob(resolve, 'image/png'); });
    if (!blob) throw new Error('the image could not be encoded');
    const credits = [];
    if (result.tiles && result.tiles.state === 'included') credits.push('Basemap © OpenStreetMap contributors.');
    const attribution = (localmap.exportInfo() || {}).attribution || [];
    if (attribution.length) credits.push(`Geometry: ${attribution.join('; ')}.`);
    return {
      url: URL.createObjectURL(blob),
      caption: `${mapName}. Drawn to scale; the bar is a true ground distance. ${credits.join(' ')}`.trim(),
      tiles: result.tiles,
    };
  } catch (error) {
    return { url: null, error: error.message };
  } finally {
    if (!onIt) {
      state.navigate({
        entity: before.entity, sel: before.sel, levels: before.levels, basemap: before.basemap, mode: before.mode,
      }, { replace: true });
    }
  }
}

let sheetUrl = null;

function clearSheet() {
  const old = document.getElementById('print-sheet');
  if (old) old.remove();
  if (sheetUrl) { URL.revokeObjectURL(sheetUrl); sheetUrl = null; }
  document.body.classList.remove('is-printing-sheet');
}

/**
 * Builds the one-page sheet for `facilityId` and puts it in the page, ready to print:
 * no interactive chrome prints (export.css). Resolves to the sheet's element. `print`
 * false builds it without opening the print dialog (the browser check uses that).
 */
export async function buildFacilitySheet(facilityId, { map = true } = {}) {
  const facility = env.atlas.facilities[facilityId];
  if (!facility) throw new ExportError('Unknown facility.');
  clearSheet();
  const mapMeta = facility.map_id && env.atlas.maps[facility.map_id];
  const [data, snapshot] = await Promise.all([
    sheetData(facilityId),
    map && mapMeta ? snapshotMap(facility.map_id.split(':')[1], mapMeta.name) : Promise.resolve(null),
  ]);
  if (snapshot && snapshot.url) sheetUrl = snapshot.url;
  const sheet = sheetNode(data, snapshot, todayISO());
  document.body.appendChild(sheet);
  const image = sheet.querySelector('img');
  if (image) { try { await image.decode(); } catch (error) { /* it will still paint */ } }
  await ensureFonts();
  fitSheet(sheet);
  return sheet;
}

// Letter's printable height is 257 mm (A4's 273); the sheet is fitted to 252 so it is one
// page on either. Measured off screen at A4's narrower width (export.css .is-measuring).
const SHEET_BUDGET_MM = 252;
const MM = 96 / 25.4;

/** Lowers the map's height, and if it must the type size, until the sheet is one page. */
export function fitSheet(sheet) {
  const figure = sheet.querySelector('.ps-map img');
  sheet.classList.add('is-measuring');
  const heightMm = () => sheet.getBoundingClientRect().height / MM;
  let mapMm = 72;
  for (let size = 9.4; size >= 8.2; size -= 0.6) {
    sheet.style.fontSize = `${size}pt`;
    for (let pass = 0; pass < 8 && heightMm() > SHEET_BUDGET_MM && figure && mapMm > 40; pass += 1) {
      mapMm = Math.max(40, mapMm - (heightMm() - SHEET_BUDGET_MM) - 0.5);
      figure.style.maxHeight = `${mapMm.toFixed(1)}mm`;
    }
    if (heightMm() <= SHEET_BUDGET_MM) break;
  }
  const result = heightMm();
  sheet.classList.remove('is-measuring');
  sheet.dataset.heightMm = result.toFixed(1);
  return result;
}

export async function printFacilitySheet(facilityId) {
  const sheet = await buildFacilitySheet(facilityId);
  document.body.classList.add('is-printing-sheet');
  window.addEventListener('afterprint', clearSheet, { once: true });
  window.print();
  return sheet;
}

/** The "Print facility sheet" action for a facility panel (panels.js): a button and the
 * line that says what is happening, or what went wrong. */
export function facilityPrintAction(facilityId) {
  const button = h('button', { type: 'button', class: 'text-btn print-sheet-btn' }, 'Print facility sheet');
  const note = h('span', { class: 'print-sheet-note', role: 'status', 'aria-live': 'polite' });
  button.addEventListener('click', async () => {
    const label = button.textContent;
    button.disabled = true;
    button.textContent = 'Preparing the sheet\u2026';
    note.textContent = '';
    try {
      await printFacilitySheet(facilityId);
    } catch (error) {
      window.console.error(error);
      note.textContent = `The sheet could not be made: ${error.message}`;
    } finally {
      button.disabled = false;
      button.textContent = label;
    }
  });
  return h('p', { class: 'panel-actions' }, [button, note]);
}

// ------------------------------------------------------------------- init

export function init({
  atlas, index, manifest, getGlobe,
}) {
  env = {
    atlas, index, manifest, getGlobe, views: null,
  };
  window.__hepAtlasExport = window.__hepAtlasExport || {};
  createDialog();
}

/** The view host is made after this module is initialised (app.js): it is handed over here, and
 * the Export button follows it from then on. */
export function attachViews(views) {
  if (!env) return;
  env.views = views;
  views.onExportChange(() => refreshExportButton());
  refreshExportButton();
}
