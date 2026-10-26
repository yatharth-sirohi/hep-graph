// beam-section.js — "Beam through the Earth": the cross-section of the Earth along
// one long-baseline neutrino beam, from the two sites' recorded coordinates.
//
//   #/view/beam-section/<beamline-slug>[~<row-index>]
//
// A baseline row of atlas.json (source site -> far-detector site) becomes:
//   * a zoomed section with the vertical stretched ("vertical x 20", stated in the
//     figure): the surface arc, the straight chord the neutrinos travel, both sites
//     named, and each site's recorded depth;
//   * the whole Earth at true scale, and the dip angle at its true size;
//   * the numbers — dip, deepest point, chord, surface distance, light travel time —
//     in a table with their formulas, inputs and uncertainty;
//   * the sourced baseline beside the computed distance, with its source;
//   * where a record carries a sourced off-axis angle, a schematic marked not to scale.
//
// The arithmetic is beam-geometry.js (shared with the unit check), the row logic is
// beam-rows.js. This file only draws. Mounted by host.js through registry.js.

import {
  EARTH_RADIUS_KM, EARTH_RADIUS_POLAR_KM, EARTH_RADIUS_EQUATORIAL_KM, LIGHT_SPEED_KM_S,
  agreesWithin, chooseExaggeration, niceLength, surfaceProfile,
} from './beam-geometry.js';
import {
  WORKING_TITLE, beamStatusAt, offAxisFor, resolveRow, rowGeometry, rowsForBeamline,
} from './beam-rows.js';
import { quantityText, titleCase } from '../model.js';
import * as provenance from '../provenance.js';

const SVG_NS = 'http://www.w3.org/2000/svg';

// ---------------------------------------------------------------- small helpers
function h(tag, attrs = {}, children = []) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (key === 'class') el.className = value;
    else if (key === 'text') el.textContent = value;
    else if (value !== null && value !== undefined) el.setAttribute(key, value);
  }
  for (const child of [].concat(children)) {
    if (child == null) continue;
    el.appendChild((typeof child === 'string' || typeof child === 'number') ? document.createTextNode(String(child)) : child);
  }
  return el;
}

function s(tag, attrs = {}, children = []) {
  const el = document.createElementNS(SVG_NS, tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (key === 'class') el.setAttribute('class', value);
    else if (key === 'text') el.textContent = value;
    else if (value !== null && value !== undefined) el.setAttribute(key, String(value));
  }
  for (const child of [].concat(children)) {
    if (child == null) continue;
    el.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
  }
  return el;
}

const f = (value, digits) => Number(value).toFixed(digits);
/** The gap before a unit: none before a degree sign. */
const sp = (unit) => (unit === '°' ? '' : ' ');
const rad = (degrees) => (degrees * Math.PI) / 180;
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

/** Two significant figures, for an uncertainty ("0.014", "3.1", "12"). */
function sig2(value) {
  if (!(value > 0)) return '0';
  const digits = Math.max(0, 1 - Math.floor(Math.log10(value)));
  return value.toFixed(Math.min(digits, 6));
}

function km(value, digits = 1) {
  return `${f(value, digits)} km`;
}

/** A recorded depth as a person reads it: whole metres, "~" when the record says approximate. */
function depthText(depth) {
  const metres = Math.round(depth.km * 1000);
  return `${depth.approx ? '~' : ''}${metres} m`;
}

/** Greedy word wrap to `maxChars` characters per line (an estimate: no font metrics at hand). */
function wrap(text, maxChars) {
  const lines = [];
  let line = '';
  for (const word of String(text).split(/\s+/)) {
    if (line && `${line} ${word}`.length > maxChars) {
      lines.push(line);
      line = word;
    } else {
      line = line ? `${line} ${word}` : word;
    }
  }
  if (line) lines.push(line);
  return lines;
}

const charWidth = (size) => size * 0.56;

let uid = 0;

// ------------------------------------------------------------------- the model
function buildModel(atlas, row) {
  const { geometry, precisionKm, uncertainty } = rowGeometry(row);
  const deepest = Math.max(0, ...[row.from, row.to].map((site) => (site.depth ? site.depth.km : 0)));
  const exaggeration = chooseExaggeration(geometry.chordKm, geometry.sagittaKm, deepest);
  return {
    row, g: geometry, precisionKm, u: uncertainty, V: exaggeration,
    from: row.from, to: row.to,
  };
}

/** Worst-case ± of a quantity: the larger Earth-radius deviation plus the coordinate effect. */
function worstCase(model, key) {
  const radius = model.u.radius[key];
  const nominal = model.g[key];
  const byRadius = Math.max(nominal - radius.min, radius.max - nominal);
  const byCoordinates = model.u.coordinates ? model.u.coordinates[key] : null;
  return { byRadius, byCoordinates, total: byRadius + (byCoordinates || 0) };
}

// ---------------------------------------------------------------- the zoomed section
function drawSection(model, status, width, minHeight = 0) {
  const { g, V, from, to } = model;
  const id = `bs${++uid}`;
  const compact = width < 560;
  const W = width;
  const mx = compact ? 16 : 30;
  const plotW = W - 2 * mx;
  const kx = plotW / g.chordKm; // px per km along the chord
  const ky = kx * V; // px per km, vertical: stretched
  const sagPx = g.sagittaKm * ky;
  const headH = 50;
  const yApex = headH + 16;
  const yChord = yApex + sagPx;
  const x0 = mx;
  const x1 = W - mx;
  const xm = W / 2;

  // Below the chord: the detector depths and the two sites' names.
  const labelW = Math.min(250, plotW * (compact ? 0.48 : 0.42));
  const chars = Math.floor(labelW / charWidth(12.5));
  const ends = [
    { site: from, x: x0, side: 1, role: 'Beam source' },
    { site: to, x: x1, side: -1, role: 'Far detector site' },
  ].map((end) => {
    const depthPx = end.site.depth ? end.site.depth.km * ky : 0;
    // The depth line of text sits at least 30 px under the chord, clear of the pills on it.
    const depthTextY = Math.max(yChord + depthPx + 4, yChord + 30);
    const blockTop = depthTextY + 18;
    const lines = wrap(end.site.name, chars);
    return { ...end, depthPx, depthTextY, blockTop, lines, bottom: blockTop + 20 + 20 + lines.length * 16 };
  });
  // `minHeight`: with the whole-Earth panel beside it, the section is at least as tall as that
  // panel, and the rock simply goes on down to the bottom edge.
  const yBottom = Math.max(Math.max(...ends.map((e) => e.bottom)) + 8, minHeight - 8);
  const H = Math.ceil(yBottom + 8);

  const svg = s('svg', {
    class: 'bs-svg', viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: 'img', 'aria-labelledby': `${id}-t ${id}-d`,
    focusable: 'false',
  });
  const depthSentences = ends
    .filter((e) => e.site.depth)
    .map((e) => `${e.site.short} is ${e.site.depth.display} below the local surface`);
  svg.append(
    s('title', { id: `${id}-t` }, `Cross-section of the Earth along the neutrino beam from ${from.short} to ${to.short}`),
    s('desc', { id: `${id}-d` },
      `The Earth's surface is an arc ${km(g.surfaceKm)} long between ${from.name} and ${to.name}. The neutrinos travel the straight `
      + `chord beneath it, ${km(g.chordKm)} long: they leave ${f(g.dipDeg, 2)} degrees below the horizontal and reach ${km(g.sagittaKm)} below the `
      + `surface at the midpoint. The drawing stretches vertical distances by a factor of ${V}; horizontal distances are to scale.`
      + `${depthSentences.length ? ` ${depthSentences.join('; ')}.` : ''}${status.dashed ? ` The beam is ${status.phrase}.` : ''}`),
  );

  // Gradients and the rock.
  svg.append(s('defs', {}, [
    s('linearGradient', { id: `${id}-rock`, x1: 0, y1: 0, x2: 0, y2: 1 }, [
      s('stop', { offset: '0%', class: 'bs-rock-top' }),
      s('stop', { offset: '100%', class: 'bs-rock-bottom' }),
    ]),
  ]));

  const profile = surfaceProfile(g.centralAngleRad, g.R, 120).map((p) => [xm + p.x * kx, yChord - p.y * ky]);
  const surfacePath = profile.map(([x, y], i) => `${i ? 'L' : 'M'}${f(x, 2)} ${f(y, 2)}`).join(' ');
  svg.append(
    s('path', { class: 'bs-rock', d: `${surfacePath} L${f(x1, 2)} ${f(yBottom, 2)} L${f(x0, 2)} ${f(yBottom, 2)} Z`, fill: `url(#${id}-rock)` }),
    s('path', { class: 'bs-surface', d: surfacePath, fill: 'none' }),
  );

  // Heading inside the figure, so a screenshot of it still says what it shows.
  svg.append(
    s('text', { class: 'bs-t bs-t-strong bs-t-head', x: x0, y: 22 }, `Zoomed section · vertical ×${V}`),
    s('text', { class: 'bs-t bs-t-muted', x: x0, y: 41 },
      compact ? 'Vertical stretched; horizontal to scale' : 'Distances along the beam are to scale; heights and depths are stretched'),
  );

  // Scale bars, in the open sky at the top left.
  const hBarKm = niceLength(g.chordKm * 0.2);
  const vBarKm = niceLength(Math.max(g.sagittaKm * 0.3, 0.2));
  const bx = x0;
  const by = yApex + 4;
  svg.append(
    s('g', { class: 'bs-scale' }, [
      s('path', { class: 'bs-scale-line', d: `M${bx} ${by} h${f(hBarKm * kx, 1)} M${bx} ${by - 4} v8 M${f(bx + hBarKm * kx, 1)} ${by - 4} v8` }),
      s('text', { class: 'bs-t', x: bx, y: by + 20 }, compact ? `${hBarKm} km` : `${hBarKm} km along the beam`),
      // On a phone the open sky is too narrow for a second bar and its label (they would run into
      // the surface); the stretch is in the heading and every depth is written beside its mark.
      compact ? null : s('path', { class: 'bs-scale-line', d: `M${bx} ${by + 34} v${f(vBarKm * ky, 1)} M${bx - 4} ${by + 34} h8 M${bx - 4} ${f(by + 34 + vBarKm * ky, 1)} h8` }),
      compact ? null : s('text', { class: 'bs-t', x: bx + 9, y: by + 34 + Math.max(14, (vBarKm * ky) / 2 + 4) }, `${vBarKm < 1 ? `${vBarKm * 1000} m` : `${vBarKm} km`} (×${V})`),
    ]),
  );

  // The deepest point: a dimension line from the surface down to the chord at mid-chord.
  const dimLabelX = xm + 10;
  svg.append(s('g', { class: 'bs-dim' }, [
    s('path', { class: 'bs-dim-line', d: `M${xm} ${f(yApex, 1)} V${f(yChord, 1)} M${xm - 5} ${f(yApex, 1)} h10 M${xm - 5} ${f(yChord, 1)} h10` }),
    s('text', { class: 'bs-t bs-t-strong bs-t-num', x: dimLabelX, y: f(yApex + sagPx / 2 - 2, 1) }, km(g.sagittaKm)),
    s('text', { class: 'bs-t bs-t-muted', x: dimLabelX, y: f(yApex + sagPx / 2 + 15, 1) }, compact ? 'deepest point' : 'below the surface, mid-chord'),
  ]));

  // The beam: the chord, drawn dashed while it is not running, with a flowing overlay
  // while it is (CSS turns the flow off under prefers-reduced-motion).
  const beamClass = ['bs-beam', status.dashed ? 'is-dashed' : '', status.flowing ? '' : 'is-quiet'].filter(Boolean).join(' ');
  svg.append(s('g', { class: 'bs-beam-group' }, [
    s('line', { class: 'bs-beam-glow', x1: x0, y1: yChord, x2: x1, y2: yChord }),
    s('line', { class: beamClass, x1: x0, y1: yChord, x2: x1, y2: yChord }),
    status.flowing ? s('line', { class: 'bs-flow', x1: x0, y1: yChord, x2: x1, y2: yChord }) : null,
    s('path', { class: 'bs-arrowhead', d: `M${x1 - 3} ${yChord} l-13 -6 v12 Z` }),
  ]));
  const pill = (cx, cy, text, cls) => {
    const w = text.length * charWidth(12.5) + 16;
    return s('g', { class: `bs-pill ${cls || ''}` }, [
      s('rect', { x: f(cx - w / 2, 1), y: f(cy - 11, 1), width: f(w, 1), height: 22, rx: 11 }),
      s('text', { class: 'bs-t', x: f(cx, 1), y: f(cy + 4, 1), 'text-anchor': 'middle' }, text),
    ]);
  };
  svg.append(pill(xm + plotW * 0.26, yChord, compact ? `chord ${f(g.chordKm, 0)} km` : `straight chord · ${km(g.chordKm)}`, 'bs-pill-beam'));
  if (status.phrase) svg.append(pill(xm - plotW * 0.26, yChord, status.phrase, 'bs-pill-status'));

  // The two sites: a dot on the surface, the recorded depth below it, the name.
  for (const end of ends) {
    const { site, x, side } = end;
    const anchor = side > 0 ? 'start' : 'end';
    const tx = x + side * 12;
    const g2 = s('g', { class: 'bs-end' });
    if (site.depth) {
      g2.append(
        s('path', { class: 'bs-depth-line', d: `M${x} ${yChord} V${f(yChord + end.depthPx, 1)}` }),
        s('rect', { class: 'bs-detector', x: x - 7, y: f(yChord + end.depthPx - 2.5, 1), width: 14, height: 5, rx: 1.5 }),
        s('text', { class: 'bs-t', x: tx, y: f(end.depthTextY - 4, 1), 'text-anchor': anchor },
          `${depthText(site.depth)} below the surface`),
      );
    } else {
      g2.append(s('text', { class: 'bs-t bs-t-muted', x: tx, y: f(end.depthTextY - 4, 1), 'text-anchor': anchor }, 'depth not recorded'));
    }
    g2.append(s('circle', { class: 'bs-site', cx: x, cy: yChord, r: 5.5 }));
    // Plain text, not links: an image that holds links is an interactive control inside an
    // image (axe nested-interactive). Each site's record is linked under "Open the records".
    const label = s('g', { class: 'bs-site-label', 'data-site': site.id });
    label.append(
      s('text', { class: 'bs-t bs-t-role', x, y: end.blockTop + 4, 'text-anchor': anchor }, end.role.toUpperCase()),
      s('text', { class: 'bs-t bs-t-strong bs-t-name', x, y: end.blockTop + 24, 'text-anchor': anchor }, site.short),
      ...end.lines.map((line, i) => s('text', { class: 'bs-t bs-t-muted', x, y: end.blockTop + 42 + i * 16, 'text-anchor': anchor }, line)),
    );
    g2.append(label);
    svg.append(g2);
  }
  return svg;
}

// ---------------------------------------------------------------- the whole Earth
function drawEarth(model, width) {
  const { g, from, to } = model;
  const id = `bs${++uid}`;
  const W = Math.min(width, 340);
  const r = clamp((W - 120) / 2, 70, 120);
  const cx = W / 2;
  const top = 92;
  const cy = top + r;
  const h2 = g.dipRad; // half the central angle
  const P = { x: cx - r * Math.sin(h2), y: cy - r * Math.cos(h2) };
  const Q = { x: cx + r * Math.sin(h2), y: cy - r * Math.cos(h2) };

  // Below the Earth: the dip at its true size.
  const dipTop = cy + r + 56;
  const armLen = Math.min(W - 60, 200);
  const O = { x: 34, y: dipTop + 30 };
  const dipRadius = Math.min(armLen * 0.55, 96);
  const dipEnd = { x: O.x + armLen * Math.cos(g.dipRad), y: O.y + armLen * Math.sin(g.dipRad) };
  const H = Math.ceil(dipEnd.y + 40);

  const svg = s('svg', {
    class: 'bs-svg', viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: 'img', 'aria-labelledby': `${id}-t ${id}-d`, focusable: 'false',
  });
  svg.append(
    s('title', { id: `${id}-t` }, 'The whole Earth at true scale, with the beam as a chord near its surface'),
    s('desc', { id: `${id}-d` },
      `A circle for the Earth, radius ${f(g.R, 1)} km, drawn at true scale. ${from.short} and ${to.short} are two points on its rim, a central `
      + `angle of ${f(g.centralAngleDeg, 2)} degrees apart. The beam is the straight chord between them; the surface arc is ${km(g.surfaceKm)} long. `
      + `At the source the chord leaves ${f(g.dipDeg, 2)} degrees below the local horizontal, drawn below at its true size.`),
    s('defs', {}, [
      s('radialGradient', { id: `${id}-earth`, cx: '50%', cy: '35%', r: '75%' }, [
        s('stop', { offset: '0%', class: 'bs-rock-top' }),
        s('stop', { offset: '100%', class: 'bs-rock-bottom' }),
      ]),
    ]),
    s('text', { class: 'bs-t bs-t-strong bs-t-head', x: 8, y: 22 }, 'The whole Earth, true scale'),
    s('text', { class: 'bs-t bs-t-muted', x: 8, y: 41 }, `radius ${f(g.R, 1)} km; no stretching here`),
  );

  svg.append(s('circle', { class: 'bs-earth', cx, cy, r, fill: `url(#${id}-earth)` }));
  // The radii that bound the central angle, and the centre.
  svg.append(
    s('path', { class: 'bs-radius', d: `M${f(P.x, 2)} ${f(P.y, 2)} L${cx} ${cy} L${f(Q.x, 2)} ${f(Q.y, 2)}` }),
    s('circle', { class: 'bs-centre', cx, cy, r: 3 }),
    s('text', { class: 'bs-t bs-t-muted', x: cx, y: cy + 20, 'text-anchor': 'middle' }, 'centre of the Earth'),
    s('text', { class: 'bs-t', x: cx, y: cy + 38, 'text-anchor': 'middle' }, `Δσ = ${f(g.centralAngleDeg, 2)}°`),
  );
  // The surface arc and the chord.
  const arcFlag = g.centralAngleRad > Math.PI ? 1 : 0;
  svg.append(
    s('path', { class: 'bs-earth-arc', d: `M${f(P.x, 2)} ${f(P.y, 2)} A${r} ${r} 0 ${arcFlag} 1 ${f(Q.x, 2)} ${f(Q.y, 2)}`, fill: 'none' }),
    s('line', { class: 'bs-earth-chord', x1: P.x, y1: P.y, x2: Q.x, y2: Q.y }),
    s('circle', { class: 'bs-site', cx: P.x, cy: P.y, r: 3.5 }),
    s('circle', { class: 'bs-site', cx: Q.x, cy: Q.y, r: 3.5 }),
  );
  // Names, above the rim, away from each other.
  svg.append(
    s('text', { class: 'bs-t bs-t-strong', x: f(P.x - 8, 1), y: f(P.y - 16, 1), 'text-anchor': 'end' }, from.short),
    s('text', { class: 'bs-t bs-t-strong', x: f(Q.x + 8, 1), y: f(Q.y - 16, 1), 'text-anchor': 'start' }, to.short),
    s('path', { class: 'bs-leader', d: `M${f(P.x - 4, 1)} ${f(P.y - 12, 1)} L${f(P.x, 1)} ${f(P.y - 4, 1)} M${f(Q.x + 4, 1)} ${f(Q.y - 12, 1)} L${f(Q.x, 1)} ${f(Q.y - 4, 1)}` }),
    s('text', { class: 'bs-t bs-t-muted', x: cx, y: f(cy + r + 20, 1), 'text-anchor': 'middle' },
      `surface arc: ${f((g.surfaceKm / (2 * Math.PI * g.R)) * 100, 1)} % of the way round`),
  );

  // The dip, true size: the local horizontal and the chord from one point.
  svg.append(
    s('text', { class: 'bs-t bs-t-strong bs-t-head', x: 8, y: f(dipTop - 6, 1) }, 'The dip at the source, true size'),
    s('line', { class: 'bs-horizon', x1: O.x - 8, y1: O.y, x2: f(O.x + armLen + 8, 1), y2: O.y }),
    s('line', { class: 'bs-earth-chord', x1: O.x, y1: O.y, x2: f(dipEnd.x, 2), y2: f(dipEnd.y, 2) }),
    s('path', { class: 'bs-dip-arc', d: `M${f(O.x + dipRadius, 2)} ${O.y} A${f(dipRadius, 1)} ${f(dipRadius, 1)} 0 0 1 ${f(O.x + dipRadius * Math.cos(g.dipRad), 2)} ${f(O.y + dipRadius * Math.sin(g.dipRad), 2)}`, fill: 'none' }),
    s('circle', { class: 'bs-site', cx: O.x, cy: O.y, r: 3.5 }),
    s('text', { class: 'bs-t bs-t-strong bs-t-num', x: O.x, y: f(dipEnd.y + 26, 1) }, `${f(g.dipDeg, 2)}° below the horizontal`),
    s('text', { class: 'bs-t bs-t-muted', x: f(O.x + armLen + 6, 1), y: f(O.y - 8, 1), 'text-anchor': 'end' }, 'local horizontal'),
  );
  return svg;
}

// ---------------------------------------------------------------- off-axis schematic
function drawOffAxis(width) {
  const id = `bs${++uid}`;
  const W = Math.min(width, 340);
  const H = 132;
  const O = { x: 22, y: 50 };
  const L = W - 70;
  const theta = rad(20); // drawn size; the real angle is in the text, and this says so
  const svg = s('svg', {
    class: 'bs-svg', viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: 'img', 'aria-labelledby': `${id}-t ${id}-d`, focusable: 'false',
  });
  svg.append(
    s('title', { id: `${id}-t` }, 'Schematic of the off-axis angle, not to scale'),
    s('desc', { id: `${id}-d` }, 'Two lines leave the beam source: the beam axis, and the line to the detector, which lies off to one side of it by the off-axis angle. The angle drawn is much larger than the real one.'),
    s('line', { class: 'bs-earth-chord', x1: O.x, y1: O.y, x2: O.x + L, y2: O.y }),
    s('line', { class: 'bs-detector-line', x1: O.x, y1: O.y, x2: f(O.x + L * Math.cos(theta), 1), y2: f(O.y + L * Math.sin(theta), 1) }),
    s('path', { class: 'bs-dip-arc', d: `M${O.x + 62} ${O.y} A62 62 0 0 1 ${f(O.x + 62 * Math.cos(theta), 1)} ${f(O.y + 62 * Math.sin(theta), 1)}`, fill: 'none' }),
    s('circle', { class: 'bs-site', cx: O.x, cy: O.y, r: 3.5 }),
    s('rect', { class: 'bs-detector', x: f(O.x + L * Math.cos(theta) - 7, 1), y: f(O.y + L * Math.sin(theta) - 7, 1), width: 14, height: 14, rx: 2 }),
    s('text', { class: 'bs-t bs-t-muted', x: O.x + L, y: O.y - 8, 'text-anchor': 'end' }, 'beam axis'),
    s('text', { class: 'bs-t', x: f(O.x + L * Math.cos(theta) - 12, 1), y: f(O.y + L * Math.sin(theta) + 22, 1), 'text-anchor': 'end' }, 'line to the detector'),
    s('text', { class: 'bs-t bs-t-strong', x: O.x + 70, y: O.y + 14 }, 'θ'),
    s('text', { class: 'bs-t bs-t-strong bs-not-to-scale', x: 8, y: 20 }, 'NOT TO SCALE'),
  );
  return svg;
}

// ------------------------------------------------------------------------- the view
export function mount(ctx) {
  const { atlas, arg, host, loader } = ctx;
  const resolved = resolveRow(atlas, arg);
  if (resolved.error) {
    host.setTitle(WORKING_TITLE);
    host.fail(resolved.error);
    return null;
  }
  const { row, beamline } = resolved;
  const model = buildModel(atlas, row);
  const { g, u, V } = model;
  let timelineState = ctx.timelineState;
  let status = beamStatusAt(row, timelineState);

  host.setTitle(WORKING_TITLE);
  host.setBack({ label: `Back to ${beamline.name}`, route: { type: 'beamline', slug: beamline.id.split(':')[1] } });

  const subtitleStatus = h('span', { class: 'status-badge', id: 'bs-status' });
  function paintStatus() {
    status = beamStatusAt(row, timelineState);
    const year = timelineState && timelineState.year != null ? timelineState.year
      : (timelineState && timelineState.range ? `${timelineState.range[0]}–${timelineState.range[1]}` : '');
    subtitleStatus.className = 'status-badge';
    if (status.status === 'absent') {
      subtitleStatus.classList.add('is-outside-timeline');
      subtitleStatus.textContent = `Not yet built in ${year}`;
    } else {
      subtitleStatus.classList.add(`status-${status.status}`);
      subtitleStatus.textContent = status.phrase ? `${status.phrase.charAt(0).toUpperCase()}${status.phrase.slice(1)}` : 'Active';
    }
  }
  paintStatus();
  host.setSubtitle(h('span', {}, [
    `${row.from.short} → ${row.to.short} · ${beamline.name} `,
    subtitleStatus,
  ]));

  const body = host.body;
  body.replaceChildren();

  // ---- the sentence a newcomer can read
  const lede = h('p', { class: 'bs-lede' }, [
    'Neutrinos pass through rock almost untouched, so the beam goes straight through the Earth: it leaves ',
    h('strong', {}, row.from.short),
    ` pointing ${f(g.dipDeg, 1)}° below the horizon, runs in a straight line for ${f(g.chordKm, 0)} km, and surfaces at `,
    h('strong', {}, row.to.short),
    `. Halfway, it is ${f(g.sagittaKm, 1)} km under the ground. Everything below is computed from the two recorded coordinates.`,
  ]);

  // ---- four numbers
  const tile = (label, value, note) => h('div', { class: 'bs-stat' }, [
    h('dt', {}, label),
    h('dd', {}, [h('span', { class: 'bs-stat-value' }, value), note ? h('span', { class: 'bs-stat-note' }, note) : null]),
  ]);
  const wc = (key, unit) => `±${sig2(worstCase(model, key).total)}${sp(unit)}${unit} worst case`;
  const stats = h('dl', { class: 'bs-stats', 'aria-label': 'The computed numbers' }, [
    tile('Dip below the horizontal at the source', `${f(g.dipDeg, 2)}°`, wc('dipDeg', '°')),
    tile('Deepest point, at mid-chord', km(g.sagittaKm), wc('sagittaKm', 'km')),
    tile('Straight-line path (the chord)', km(g.chordKm), wc('chordKm', 'km')),
    tile('Light travel time along the chord', `${f(g.lightMs, 2)} ms`, wc('lightMs', 'ms')),
  ]);

  // ---- the figure
  const sectionWrap = h('div', { class: 'bs-fig-a' });
  const earthWrap = h('div', { class: 'bs-fig-b' });
  const offAxisCards = offAxisFor(atlas, row);
  const offAxisWrap = offAxisCards.length ? h('div', { class: 'bs-offaxis' }) : null;
  const grid = h('div', { class: 'bs-fig-grid' }, [sectionWrap, h('div', { class: 'bs-fig-side' }, [earthWrap])]);
  const caption = h('figcaption', { class: 'bs-caption' }, [
    h('strong', {}, `Vertical ×${V}. `),
    `In the left panel, distances along the beam are to scale and everything vertical (the curve of the surface, the depths) is stretched ${V} times, so the chord's depth can be seen. `,
    'The right panel is the same beam on the whole Earth, unstretched: the chord is a hair below the surface. ',
    `The beam is the straight chord between the two surface points; the Earth is a sphere of radius ${f(g.R, 1)} km.`,
  ]);
  const figure = h('figure', { class: 'bs-figure' }, [grid, caption]);

  function drawFigures() {
    const wA = Math.floor(sectionWrap.clientWidth || 0);
    const wB = Math.floor(earthWrap.clientWidth || 0);
    if (wB >= 200) earthWrap.replaceChildren(drawEarth(model, wB));
    // Beside the Earth panel (a wide stage) the section matches its height; stacked (a phone) it does not.
    // (Its own drawn height, not the stretched panel's: that would chase itself.)
    const earthSvg = earthWrap.querySelector('svg');
    const beside = earthWrap.getBoundingClientRect().left >= sectionWrap.getBoundingClientRect().right - 1;
    const earthHeight = earthSvg ? Number(earthSvg.getAttribute('height')) : 0;
    if (wA >= 240) sectionWrap.replaceChildren(drawSection(model, status, wA, beside ? earthHeight : 0));
    if (offAxisWrap) {
      const wC = Math.floor(offAxisWrap.clientWidth || 0);
      const holder = offAxisWrap.querySelector('.bs-offaxis-fig');
      if (wC >= 200 && holder) holder.replaceChildren(drawOffAxis(wC));
    }
  }

  // ---- the table of numbers, with formulas and inputs
  const rad5 = f(g.centralAngleRad, 6);
  const row2 = (name, formula, inputs, value, uncertainty) => h('tr', {}, [
    h('th', { scope: 'row' }, name),
    h('td', { class: 'bs-formula', 'data-label': 'Formula and inputs' }, [h('span', { class: 'bs-math' }, formula), h('span', { class: 'bs-inputs' }, inputs)]),
    h('td', { class: 'bs-num', 'data-label': 'Value' }, value),
    h('td', { class: 'bs-uncertainty', 'data-label': 'Uncertainty (worst case)' }, uncertainty),
  ]);
  const uncertaintyCell = (key, digits, unit) => {
    const w = worstCase(model, key);
    const parts = [];
    if (key === 'dipDeg' || key === 'centralAngleDeg') {
      parts.push(h('span', {}, 'Earth radius: does not enter'));
    } else {
      const r = u.radius[key];
      parts.push(h('span', {}, `Earth radius 6357–6378 km: ${f(r.min, digits)} to ${f(r.max, digits)}${sp(unit)}${unit}`));
    }
    parts.push(h('span', {}, w.byCoordinates == null ? 'Site coordinates: a precision is not recorded' : `Site coordinates: ±${sig2(w.byCoordinates)}${sp(unit)}${unit}`));
    return h('div', { class: 'bs-uncertainty-parts' }, parts);
  };
  const table = h('table', { class: 'bs-table' }, [
    h('caption', {}, 'The computed numbers, with their formulas and inputs'),
    h('thead', {}, h('tr', {}, [
      h('th', { scope: 'col' }, 'Quantity'),
      h('th', { scope: 'col' }, 'Formula and inputs'),
      h('th', { scope: 'col' }, 'Value'),
      h('th', { scope: 'col' }, 'Uncertainty (worst case)'),
    ])),
    h('tbody', {}, [
      row2('Central angle Δσ', 'haversine of the two (latitude, longitude) pairs', `= ${rad5} rad`, `${f(g.centralAngleDeg, 3)}°`, uncertaintyCell('centralAngleDeg', 3, '°')),
      row2('Surface distance s', 's = R · Δσ', `= ${f(g.R, 1)} km × ${rad5}`, km(g.surfaceKm), uncertaintyCell('surfaceKm', 1, 'km')),
      row2('Chord c (the neutrino path)', 'c = 2R · sin(Δσ / 2)', `= 2 × ${f(g.R, 1)} km × sin(${f(g.dipRad, 6)})`, km(g.chordKm), uncertaintyCell('chordKm', 1, 'km')),
      row2('Dip below the local horizontal at the source', 'dip = Δσ / 2', `= ${rad5} / 2 rad`, `${f(g.dipDeg, 2)}°`, uncertaintyCell('dipDeg', 2, '°')),
      row2('Deepest point, at mid-chord', 'depth = R · (1 − cos(Δσ / 2))', `= ${f(g.R, 1)} km × (1 − cos ${f(g.dipRad, 6)})`, km(g.sagittaKm), uncertaintyCell('sagittaKm', 2, 'km')),
      row2('Light travel time along the chord', 't = c / c₀', `= ${f(g.chordKm, 1)} km / ${LIGHT_SPEED_KM_S.toLocaleString('en-US')} km/s`, `${f(g.lightMs, 3)} ms`, uncertaintyCell('lightMs', 3, 'ms')),
    ]),
  ]);

  // ---- the sourced baseline beside the computed distances
  const sourced = row.sourcedKm;
  const rChord = u.radius.chordKm;
  const coordKm = u.coordinates ? u.coordinates.chordKm : null;
  const agrees = sourced == null ? null : agreesWithin(sourced, g.chordKm, rChord, coordKm);
  const diff = sourced == null ? null : g.chordKm - sourced;
  const compareBody = h('div', { class: 'bs-compare-body' }, [
    h('dl', { class: 'bs-compare-list' }, [
      h('div', {}, [h('dt', {}, 'Recorded baseline (sourced)'), h('dd', {}, row.baseline.distance ? row.baseline.distance.display : 'none recorded')]),
      h('div', {}, [h('dt', {}, 'Computed surface distance'), h('dd', {}, km(g.surfaceKm))]),
      h('div', {}, [h('dt', {}, 'Computed chord'), h('dd', {}, km(g.chordKm))]),
    ]),
    sourced == null
      ? h('p', { class: 'bs-compare-note' }, 'The record carries no baseline value to compare with.')
      : h('p', { class: 'bs-compare-note' }, [
        `A baseline is the straight-line distance from the target to the detector, so the like-for-like comparison is with the chord: `,
        h('strong', {}, `${diff >= 0 ? '+' : '−'}${f(Math.abs(diff), 1)} km (${diff >= 0 ? '+' : '−'}${f((Math.abs(diff) / sourced) * 100, 2)} %)`),
        agrees
          ? ' — within the Earth-radius spread and the sites’ recorded coordinate precision.'
          : ' — more than the Earth-radius spread and the sites’ recorded coordinate precision allow. The sourced value is the one to trust; the coordinates need a closer look.',
      ]),
    h('div', { class: 'bs-cite', id: 'bs-cite-baseline' }, h('p', { class: 'loading-note' }, 'Loading the source of the baseline…')),
  ]);
  const compare = h('section', { class: 'bs-compare', 'aria-labelledby': 'bs-compare-h' }, [
    h('h3', { id: 'bs-compare-h' }, 'Sourced baseline and computed distance'),
    compareBody,
  ]);

  // ---- records this beam is made of, and its sister rows
  const recordLinks = [];
  const link = (route, text) => {
    const a = h('a', { class: 'entity-link', href: `#/${route.type}/${route.slug}` }, text);
    a.addEventListener('click', (event) => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      ctx.navigate({ entity: route });
    });
    return a;
  };
  recordLinks.push(h('li', {}, ['Beamline: ', link({ type: 'beamline', slug: beamline.id.split(':')[1] }, beamline.name)]));
  for (const experimentId of beamline.experiment_ids || []) {
    const experiment = (atlas.experiments || {})[experimentId];
    if (experiment && (experiment.site_ids || []).includes(row.to.id)) {
      recordLinks.push(h('li', {}, ['Experiment: ', link({ type: 'experiment', slug: experimentId.split(':')[1] }, experiment.name)]));
    }
  }
  for (const site of [row.from, row.to]) {
    recordLinks.push(h('li', {}, [`${site === row.from ? 'Source' : 'Far'} site: `, link({ type: 'site', slug: site.id.split(':')[1] }, site.name)]));
  }
  const siblings = rowsForBeamline(atlas, beamline).filter((other) => other.arg !== row.arg);
  const records = h('section', { class: 'bs-records', 'aria-labelledby': 'bs-records-h' }, [
    h('h3', { id: 'bs-records-h' }, 'Open the records'),
    h('ul', { class: 'entity-list' }, recordLinks),
    siblings.length ? h('h3', { class: 'bs-records-sub' }, 'Other baselines of this beamline') : null,
    siblings.length ? h('ul', { class: 'entity-list' }, siblings.map((other) => h('li', {}, [
      link({ type: 'view', slug: `beam-section/${other.arg}` }, `${WORKING_TITLE}: ${other.label}`),
      other.baseline.distance ? ` (${other.baseline.distance.display})` : '',
    ]))) : null,
  ]);

  // The sourced baseline and (where one exists) the off-axis angle sit side by side.
  const lower = h('div', { class: offAxisWrap ? 'bs-lower has-offaxis' : 'bs-lower' }, [compare, offAxisWrap]);
  body.append(lede, stats, figure, table, lower, records);

  // ---- the off-axis card (only where a record carries a sourced angle)
  if (offAxisWrap) {
    const lines = offAxisCards.map((card) => {
      const quantity = card.quantity;
      const converted = quantity.unit === 'mrad' && typeof quantity.value === 'number'
        ? ` (= ${f((quantity.value * 180) / (1000 * Math.PI), 2)}°)` : '';
      return h('p', { class: 'bs-offaxis-line' }, [
        h('strong', {}, `${card.experiment.name.replace(/\s*\(.*\)/, '')}: ${quantityText(quantity)}${converted}`),
        ' off-axis. ',
        h('span', { class: 'bs-cite', 'data-offaxis': card.experiment.id }, 'Loading the source…'),
      ]);
    });
    offAxisWrap.append(
      h('h3', {}, 'Off-axis angle'),
      h('div', { class: 'bs-offaxis-fig' }),
      h('p', { class: 'bs-offaxis-warning' }, 'Schematic, not to scale: the real angle is far smaller than the one drawn.'),
      ...lines,
    );
  }

  // ---- inputs and method (the host's disclosure)
  fillMethod(host.method, { model, row, offAxisCards, link });

  // ---- draw, and keep drawing as the stage resizes
  let frame = 0;
  const redraw = () => {
    window.cancelAnimationFrame(frame);
    frame = window.requestAnimationFrame(drawFigures);
  };
  let observer = null;
  if (typeof ResizeObserver !== 'undefined') {
    observer = new ResizeObserver(redraw);
    observer.observe(sectionWrap);
    observer.observe(earthWrap);
  }
  drawFigures();
  window.requestAnimationFrame(drawFigures);

  // ---- the citations, after the first paint (provenance.json is large and is not
  //      fetched until a view that cites it is asked for)
  let destroyed = false;
  async function loadCitations() {
    const holders = [...document.querySelectorAll('#view-host .bs-cite, #view-host .bs-sources')];
    try {
      const [prov, sources] = await Promise.all([loader.getProvenance(), loader.getSources()]);
      if (destroyed) return;
      const claims = (entityId, pointers, record) => {
        const all = prov[entityId] || {};
        const picked = {};
        for (const pointer of pointers) if (all[pointer]) picked[pointer] = all[pointer];
        return provenance.renderClaimItems(picked, sources, record);
      };
      const wrapList = (items, empty) => (items.length
        ? h('ul', { class: 'source-list' }, items)
        : h('p', { class: 'empty-note' }, empty));
      const baselinePointer = `/baselines/${row.index}/distance`;
      const baselineCite = document.getElementById('bs-cite-baseline');
      if (baselineCite) {
        baselineCite.replaceChildren(wrapList(claims(beamline.id, [baselinePointer], beamline), 'No source is recorded for this baseline value.'));
      }
      for (const card of offAxisCards) {
        const cite = document.querySelector(`#view-host [data-offaxis="${card.experiment.id}"]`);
        if (cite) cite.replaceChildren(wrapList(claims(card.experiment.id, [card.pointer], card.experiment), 'No source is recorded for this angle.'));
      }
      const sourcesHost = document.getElementById('bs-method-sources');
      if (sourcesHost) {
        const blocks = [];
        for (const site of [row.from, row.to]) {
          const items = claims(site.id, ['/coordinates', '/depth'], site.record);
          blocks.push(h('div', { class: 'bs-source-block' }, [
            h('h4', {}, site.name),
            wrapList(items, 'No sourced coordinate or depth is recorded for this site.'),
          ]));
        }
        sourcesHost.replaceChildren(...blocks);
      }
    } catch (error) {
      if (destroyed) return;
      for (const holder of holders) {
        const retry = h('button', { type: 'button', class: 'text-btn' }, 'Retry');
        retry.addEventListener('click', () => { loadCitations(); });
        holder.replaceChildren(h('p', { class: 'error-note', role: 'alert' }, `Could not load the sources: ${error.message}. `), retry);
      }
    }
  }
  window.setTimeout(loadCitations, 0);

  host.announce(`${WORKING_TITLE}: ${row.label}. The beam leaves ${f(g.dipDeg, 2)} degrees below the horizontal and is ${f(g.sagittaKm, 1)} kilometres deep at its midpoint.`);

  return {
    update(next) {
      timelineState = next.timelineState;
      paintStatus();
      drawFigures();
    },
    destroy() {
      destroyed = true;
      window.cancelAnimationFrame(frame);
      if (observer) observer.disconnect();
    },
  };
}

// ----------------------------------------------------------- the method disclosure
function fillMethod(el, { model, row, offAxisCards, link }) {
  const { g, precisionKm } = model;
  const wcDip = worstCase(model, 'dipDeg');
  const wcSag = worstCase(model, 'sagittaKm');
  const wcChord = worstCase(model, 'chordKm');

  // Inputs: the two sites.
  const siteRow = (site, role) => h('tr', {}, [
    h('th', { scope: 'row' }, role),
    h('td', {}, link({ type: 'site', slug: site.id.split(':')[1] }, site.name)),
    h('td', { class: 'bs-num' }, `${f(site.lat, 5)}°`),
    h('td', { class: 'bs-num' }, `${f(site.lon, 5)}°`),
    h('td', { class: 'bs-num' }, site.precisionM == null ? 'not recorded' : `±${site.precisionM >= 1000 ? `${f(site.precisionM / 1000, 1)} km` : `${site.precisionM} m`}`),
    h('td', {}, site.kind ? `${titleCase(site.kind)}${site.approximate ? ' (approximate)' : ''}` : ''),
    h('td', {}, site.depth ? site.depth.display : 'not recorded'),
  ]);
  const inputs = h('div', { class: 'bs-table-scroll' }, h('table', { class: 'bs-table bs-inputs-table' }, [
    h('caption', {}, 'Inputs: the two sites as the Atlas records them'),
    h('thead', {}, h('tr', {}, ['End', 'Site', 'Latitude', 'Longitude', 'Coordinate precision', 'Kind of point', 'Depth below the surface']
      .map((label) => h('th', { scope: 'col' }, label)))),
    h('tbody', {}, [siteRow(row.from, 'Source'), siteRow(row.to, 'Far end')]),
  ]));

  const radiusPct = ((EARTH_RADIUS_EQUATORIAL_KM - EARTH_RADIUS_POLAR_KM) / EARTH_RADIUS_KM) * 100;
  const depthTerms = [row.from, row.to].filter((site) => site.depth);
  const altitudeNotes = depthTerms
    .filter((site) => site.record && site.record.altitude && site.record.altitude.display)
    .map((site) => ` ${site.short} lies under ${site.depth.display} yet at an altitude of ${site.record.altitude.display}, because the mountain stands above the surface drawn here.`);
  const depthNote = (() => {
    const far = row.to.depth;
    if (!far) return null;
    const extraDeg = (far.km / g.chordKm) * (180 / Math.PI);
    return `Aiming at a detector ${depthText(far)} down, rather than at the surface above it, would steepen the beam by about d / c = ${f(extraDeg, 2)}° (${far.km.toFixed(3)} km / ${f(g.chordKm, 1)} km). That correction is not in the numbers above, which are for the two surface points.`;
  })();

  el.replaceChildren(
    h('p', { class: 'bs-method-intro' }, [
      'Everything on this page is computed from the two recorded site coordinates by the formulas below; nothing is measured from the drawing. ',
      'The sourced baseline is shown beside the result so the two can be compared, not mixed.',
    ]),
    h('h3', {}, 'Inputs'),
    inputs,
    h('ul', { class: 'bs-method-list' }, [
      h('li', {}, [h('strong', {}, 'Earth radius R'), ` = ${f(EARTH_RADIUS_KM, 1)} km, the mean radius of a spherical Earth (the real radius runs from ${EARTH_RADIUS_POLAR_KM} km at the poles to ${EARTH_RADIUS_EQUATORIAL_KM} km at the equator).`]),
      h('li', {}, [h('strong', {}, 'Speed of light c₀'), ` = ${LIGHT_SPEED_KM_S.toLocaleString('en-US')} km/s (exact, by definition of the metre).`]),
      h('li', {}, [h('strong', {}, 'Recorded baseline'), ` = ${row.baseline.distance ? row.baseline.distance.display : 'none'}, from the source cited under “Sourced baseline and computed distance”.`]),
    ]),
    h('h3', {}, 'Formulas'),
    h('ol', { class: 'bs-method-list bs-formulas' }, [
      h('li', {}, ['Central angle, from the haversine: ', h('span', { class: 'bs-math' }, 'a = sin²(Δφ/2) + cosφ₁ · cosφ₂ · sin²(Δλ/2),  Δσ = 2 · asin(√a)'), ' with φ the latitudes and λ the longitudes.']),
      h('li', {}, ['Surface distance: ', h('span', { class: 'bs-math' }, 's = R · Δσ'), '.']),
      h('li', {}, ['Chord, the straight path through the Earth: ', h('span', { class: 'bs-math' }, 'c = 2R · sin(Δσ/2)'), '.']),
      h('li', {}, ['Dip below the local horizontal at the source: ', h('span', { class: 'bs-math' }, 'Δσ/2'), '. The angle between a tangent and a chord is half the arc the chord cuts off, and the local horizontal is the tangent to the surface at the source.']),
      h('li', {}, ['Deepest point, at mid-chord (the sagitta): ', h('span', { class: 'bs-math' }, 'R · (1 − cos(Δσ/2))'), ', the gap between the chord and the surface above its midpoint.']),
      h('li', {}, ['Light travel time: ', h('span', { class: 'bs-math' }, 't = c / c₀'), ', the time light takes for the chord. A neutrino of these energies travels at essentially the same speed.']),
    ]),
    h('h3', {}, 'Uncertainty'),
    h('p', {}, [
      `The Earth is not a sphere: its radius varies by about ${f(radiusPct, 1)} % (${EARTH_RADIUS_POLAR_KM}–${EARTH_RADIUS_EQUATORIAL_KM} km). Using the polar or the equatorial radius instead of ${f(EARTH_RADIUS_KM, 1)} km moves the surface distance, the chord, the depth and the time by that much `,
      `(here the chord by up to ${sig2(wcChord.byRadius)} km, the depth by up to ${sig2(wcSag.byRadius)} km). The central angle and the dip do not contain R; for them the sphere is itself the approximation, at the same ${f(radiusPct, 1)} % level (the latitudes are geodetic, the model spherical), which this page does not try to remove.`,
    ]),
    h('p', {}, precisionKm == null
      ? 'At least one of the two sites records no coordinate precision, so the effect of the coordinates cannot be stated.'
      : [
        `Each site's coordinate is good only to the precision recorded with it: ±${sig2(row.from.precisionM / 1000)} km at ${row.from.short} and ±${sig2(row.to.precisionM / 1000)} km at ${row.to.short}. `,
        `Taking both displaced along the line that joins them, the worst case adds them: ±${sig2(precisionKm)} km on the distance, which is ±${sig2(wcDip.byCoordinates)}° on the dip and ±${sig2(wcSag.byCoordinates)} km on the deepest point. `,
        'The “worst case” in the tiles and the table is the larger of the Earth-radius deviations plus this coordinate term.',
      ]),
    h('h3', {}, 'What is modelled, and what is not'),
    h('ul', { class: 'bs-method-list' }, [
      h('li', {}, 'The two sites are points on a smooth sphere. Mountains, the altitude of a site, and the shape of the geoid are not modelled.'),
      h('li', {}, depthTerms.length
        ? 'The chord joins the two surface points. A detector’s depth is drawn below its site, stretched like everything vertical in the left panel, but it is not part of the computed chord.'
        : 'The chord joins the two surface points.'),
      depthNote ? h('li', {}, depthNote) : null,
      depthTerms.length ? h('li', {}, [
        'A depth is the rock overburden recorded for the site (the vertical distance down from the ground above the detector), not a depth below sea level.',
        ...altitudeNotes,
      ]) : null,
      h('li', {}, 'The neutrinos are taken to travel in a straight line, which is what neutrinos of these energies do; the beam’s own spread is not drawn.'),
      row.from.approximate || row.to.approximate
        ? h('li', {}, `At least one site is a campus-grade (approximate) point, not a surveyed beam position: ${[row.from, row.to].filter((site) => site.approximate).map((site) => site.short).join(' and ')}.`)
        : null,
    ]),
    offAxisCards.length ? h('p', {}, 'The off-axis angle is the sourced value from the experiment’s record, drawn as a schematic; it is not part of the computation.') : null,
    h('h3', {}, 'Sources of the inputs'),
    h('div', { class: 'bs-sources', id: 'bs-method-sources' }, h('p', { class: 'loading-note' }, 'Loading the sources…')),
  );
}
