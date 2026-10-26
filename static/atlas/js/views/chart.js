// chart.js — the small chart toolkit the Atlas views share: SVG axes on a linear or
// a log scale with proper tick labels (10⁻⁸, not 1e-8), labelled points that open
// their record, a legend, and an accessible data table built from the same rows.
//
//   const chart = createChart(container, {
//     id, title, description,                     the SVG's accessible name and description
//     x: { kind: 'linear', domain: [1000, 7000], label: 'Depth (m.w.e.)' },
//     y: { kind: 'log',    domain: [1e-10, 1e-6],  label: 'Muon flux (cm⁻² s⁻¹)' },
//     points: [{ id, x, y, yErr: [lo, hi]?, label, shape, tone, hollow, ring, group, href, aria, tip: [lines], priority }],
//     lines: [{ tone, ids: [pointId, ...] }],      thin lines joining points in order (a machine's track)
//     legend: [{ title?, items: [{ shape, tone, hollow, text }] }],
//     onOpen(point),                              a click, Enter or a click on the label
//   });
//   chart.setFaded(ids, note)     points drawn faint (and said so to a screen reader); a line fades with the point it
//                                 ends at, a label with its group (the points sharing `group`) once all of them fade
//   chart.destroy()
//
//   dataTable({ caption, columns, rows })         the same rows as an HTML table
//
// What is here and not in a view: the scales and their ticks (pure, so a unit check
// can run them under Node), label placement that keeps labels off each other and off
// the markers, and the rules every chart follows (a title and description on the SVG,
// a focus ring, a tooltip that never carries anything the table does not, no
// animation). A view supplies rows and words; the colours are the tokens in views.css
// (`tone` names one: it becomes the class `ch-tone-<tone>`).

const SVG_NS = 'http://www.w3.org/2000/svg';

// ---------------------------------------------------------------- small DOM helpers
export function h(tag, attrs = {}, children = []) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (key === 'class') el.className = value;
    else if (key === 'text') el.textContent = value;
    else if (value !== null && value !== undefined && value !== false) el.setAttribute(key, value === true ? '' : value);
  }
  for (const child of [].concat(children)) {
    if (child == null || child === false) continue;
    el.appendChild((typeof child === 'string' || typeof child === 'number') ? document.createTextNode(String(child)) : child);
  }
  return el;
}

export function s(tag, attrs = {}, children = []) {
  const el = document.createElementNS(SVG_NS, tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (key === 'class') el.setAttribute('class', value);
    else if (key === 'text') el.textContent = value;
    else if (value !== null && value !== undefined && value !== false) el.setAttribute(key, String(value));
  }
  for (const child of [].concat(children)) {
    if (child == null || child === false) continue;
    el.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
  }
  return el;
}

const f1 = (value) => (Math.round(value * 10) / 10).toString();

// ------------------------------------------------------------------------ numbers
const SUPERSCRIPTS = {
  0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹',
  '-': '⁻', '+': '⁺',
};

/** An integer as superscript characters: -8 -> "⁻⁸". */
export function superscript(value) {
  return String(value).replace(/[0-9+-]/g, (c) => SUPERSCRIPTS[c]);
}

/** 10 to an integer power as it is printed on a log axis: -8 -> "10⁻⁸", 1 -> "10", 0 -> "1". */
export function powerOfTen(exponent) {
  if (exponent === 0) return '1';
  if (exponent === 1) return '10';
  return `10${superscript(exponent)}`;
}

/** A number with thousands separators and no trailing zeros, for a linear axis. */
export function formatNumber(value) {
  return Number(value).toLocaleString('en-US', { maximumFractionDigits: 6 });
}

/** The decades of a log axis: `{ major: [{ value, exponent, label }], minor: [value] }`. Major ticks
 * sit on every power of ten inside [lo, hi]; minor ones on 2..9 times a power of ten. */
export function logTicks(lo, hi) {
  if (!(lo > 0) || !(hi > lo)) throw new RangeError('a log axis needs 0 < lo < hi');
  const eFirst = Math.ceil(Math.log10(lo) - 1e-9);
  const eLast = Math.floor(Math.log10(hi) + 1e-9);
  const major = [];
  for (let e = eFirst; e <= eLast; e += 1) major.push({ value: Number(`1e${e}`), exponent: e, label: powerOfTen(e) });
  const minor = [];
  for (let e = Math.floor(Math.log10(lo)); e <= Math.ceil(Math.log10(hi)); e += 1) {
    for (let m = 2; m <= 9; m += 1) {
      const value = Number(`${m}e${e}`);
      if (value > lo && value < hi) minor.push(value);
    }
  }
  return { major, minor };
}

/** Round-number ticks for a linear axis: a step of 1, 2, 2.5 or 5 times a power of ten, about `target` of them. */
export function linearTicks(lo, hi, target = 6) {
  if (!(hi > lo)) throw new RangeError('a linear axis needs lo < hi');
  const raw = (hi - lo) / Math.max(1, target);
  const magnitude = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * magnitude).find((candidate) => candidate >= raw * 0.999) || 10 * magnitude;
  const ticks = [];
  const first = Math.ceil(lo / step - 1e-9);
  for (let i = first; i * step <= hi + step * 1e-9; i += 1) ticks.push(Number((i * step).toPrecision(12)));
  return { ticks, step };
}

/** A scale: `scale(value)` is the pixel, `scale.invert(pixel)` the value. */
export function createScale({ kind = 'linear', domain, range }) {
  const [d0, d1] = domain;
  const [r0, r1] = range;
  const log = kind === 'log';
  if (log && !(d0 > 0 && d1 > 0)) throw new RangeError('a log scale needs a positive domain');
  const t = log ? Math.log10 : (v) => v;
  const u = log ? (v) => 10 ** v : (v) => v;
  const scale = (value) => r0 + ((t(value) - t(d0)) / (t(d1) - t(d0))) * (r1 - r0);
  scale.invert = (pixel) => u(t(d0) + ((pixel - r0) / (r1 - r0)) * (t(d1) - t(d0)));
  scale.kind = kind;
  scale.domain = domain;
  scale.range = range;
  return scale;
}

// ---------------------------------------------------------------- label placement
function overlapArea(a, b) {
  const w = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
  const hgt = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
  return w > 0 && hgt > 0 ? w * hgt : 0;
}

function rectCircleOverlap(rect, circle) {
  const nx = Math.max(rect.x, Math.min(circle.x, rect.x + rect.w));
  const ny = Math.max(rect.y, Math.min(circle.y, rect.y + rect.h));
  const d = Math.hypot(circle.x - nx, circle.y - ny);
  return d < circle.r ? (circle.r - d) * 12 : 0;
}

/**
 * Where each point's label goes. `items`: `{ id, x, y, r, w, h, priority }` (the marker's centre and
 * radius, the label's size; higher priority is placed first and kept when room runs out), `bounds`:
 * `{ x0, y0, x1, y1 }`, the area labels may use (an item may ask for its label on the left: `side: 'left'`),
 * `options.segments`: lines `{ x1, y1, x2, y2 }` a label should stay off, `options.omit`: drop a label that cannot be placed
 * clear of the others instead of crowding it, `options.leaderMinPriority`: drop a label that would need
 * a leader line unless its priority is at least this. Returns `Map(id -> { x, y, w, h, leader })`, where
 * (x, y) is the label's top-left corner and `leader` says it sits away from its marker and wants a
 * line back to it.
 *
 * Markers that lie on top of one another (three halls with the same depth and a flux within a few
 * per cent) are labelled as a stack, in the order the markers sit, so the order of the labels still
 * says which marker is which.
 */
export function placeLabels(items, bounds, options = {}) {
  const gap = 4;
  const placed = new Map();
  const taken = [];
  const circles = items.map((it) => ({ x: it.x, y: it.y, r: it.r }));
  const inside = (rect) => rect.x >= bounds.x0 && rect.y >= bounds.y0 && rect.x + rect.w <= bounds.x1 && rect.y + rect.h <= bounds.y1;

  const cost = (rect, self) => {
    let total = 0;
    if (!inside(rect)) total += 1e5;
    for (const other of taken) total += overlapArea(rect, other) * 40;
    // A label stays off the thin lines of the tracks too (about two pixels of cost for each pixel of line it covers).
    for (const seg of options.segments || []) {
      const length = Math.hypot(seg.x2 - seg.x1, seg.y2 - seg.y1);
      const steps = Math.max(1, Math.ceil(length / 3));
      for (let i = 0; i <= steps; i += 1) {
        const px = seg.x1 + ((seg.x2 - seg.x1) * i) / steps;
        const py = seg.y1 + ((seg.y2 - seg.y1) * i) / steps;
        if (px >= rect.x && px <= rect.x + rect.w && py >= rect.y && py <= rect.y + rect.h) total += 6;
      }
    }
    circles.forEach((circle, i) => { if (items[i] !== self) total += rectCircleOverlap(rect, circle) * 6; });
    // The label's own marker too: a label never covers the mark it names.
    total += rectCircleOverlap(rect, { x: self.x, y: self.y, r: self.r + 1 }) * 6;
    return total;
  };

  const near = (it, rect) => {
    const cx = Math.max(rect.x, Math.min(it.x, rect.x + rect.w));
    const cy = Math.max(rect.y, Math.min(it.y, rect.y + rect.h));
    return Math.hypot(it.x - cx, it.y - cy);
  };

  const candidates = (it) => {
    const { x, y, r, w, h: hgt } = it;
    const near0 = r + gap;
    const list = [
      { x: x + near0, y: y - hgt / 2, leader: false },
      { x: x - near0 - w, y: y - hgt / 2, leader: false },
      { x: x - w / 2, y: y - r - gap - hgt, leader: false },
      { x: x - w / 2, y: y + r + gap, leader: false },
      { x: x + near0 * 0.8, y: y - r - hgt, leader: false },
      { x: x + near0 * 0.8, y: y + r * 0.6, leader: false },
      { x: x - near0 * 0.8 - w, y: y - r - hgt, leader: false },
      { x: x - near0 * 0.8 - w, y: y + r * 0.6, leader: false },
    ];
    for (const distance of [18, 30, 46, 66, 90]) {
      for (let k = 0; k < 12; k += 1) {
        const angle = (k * Math.PI) / 6;
        const cx = x + Math.cos(angle) * (distance + w / 2 * Math.abs(Math.cos(angle)));
        const cy = y + Math.sin(angle) * distance;
        list.push({ x: cx - w / 2, y: cy - hgt / 2, leader: true });
      }
    }
    // A marker that is the start of a line (a machine's track runs to the right) prefers its label on the left.
    if (it.side === 'left') {
      [list[0], list[1]] = [list[1], list[0]];
      [list[4], list[6]] = [list[6], list[4]];
      [list[5], list[7]] = [list[7], list[5]];
    }
    return list.map((c) => ({ ...c, w, h: hgt }));
  };

  // Markers within a few pixels of one another are one cluster.
  const clusters = [];
  const seen = new Set();
  for (const it of items) {
    if (seen.has(it.id)) continue;
    const group = items.filter((o) => !seen.has(o.id) && Math.hypot(o.x - it.x, o.y - it.y) <= Math.max(it.r, o.r) * 1.1);
    group.forEach((o) => seen.add(o.id));
    clusters.push(group);
  }

  const order = clusters
    .map((group) => ({ group, priority: Math.max(...group.map((it) => it.priority || 0)), crowd: group.length }))
    .sort((a, b) => (b.priority - a.priority) || (b.crowd - a.crowd) || (a.group[0].y - b.group[0].y));

  for (const { group } of order) {
    if (group.length === 1) {
      const it = group[0];
      let best = null;
      for (const candidate of candidates(it)) {
        const rect = { x: candidate.x, y: candidate.y, w: candidate.w, h: candidate.h };
        const c = cost(rect, it) + (candidate.leader ? 30 + near(it, rect) : 0);
        if (!best || c < best.c) best = { c, rect, leader: candidate.leader };
        if (c === 0) break;
      }
      if (options.omit && best.c >= 1000) continue;
      // A label that has to stand away from its marker is kept only for a marker important enough to need one.
      if (best.leader && (it.priority || 0) < (options.leaderMinPriority || 0)) continue;
      taken.push(best.rect);
      placed.set(it.id, { ...best.rect, leader: best.leader });
      continue;
    }
    // A stack: the labels in the order of the markers (top to bottom), to one side of the cluster.
    const stack = group.slice().sort((a, b) => a.y - b.y);
    const cx = stack.reduce((sum, it) => sum + it.x, 0) / stack.length;
    const cy = stack.reduce((sum, it) => sum + it.y, 0) / stack.length;
    const rowH = Math.max(...stack.map((it) => it.h)) + 2;
    const reach = Math.max(...stack.map((it) => it.r)) + 14;
    let best = null;
    for (const side of [1, -1]) {
      for (const dy of [0, -rowH, rowH, -2 * rowH, 2 * rowH]) {
        const rects = stack.map((it, i) => ({
          x: side === 1 ? cx + reach : cx - reach - it.w,
          y: cy + dy - (stack.length * rowH) / 2 + i * rowH,
          w: it.w, h: it.h,
        }));
        let c = 0;
        rects.forEach((rect, i) => { c += cost(rect, stack[i]); });
        if (!best || c < best.c) best = { c, rects, side };
        if (c === 0) break;
      }
      if (best && best.c === 0) break;
    }
    stack.forEach((it, i) => {
      taken.push(best.rects[i]);
      placed.set(it.id, { ...best.rects[i], leader: true });
    });
  }
  return placed;
}

// ------------------------------------------------------------------- marker shapes
/** The SVG element of one marker, centred on (0, 0). */
export function markerShape(shape, r) {
  switch (shape) {
    case 'square': return s('rect', { x: -r * 0.9, y: -r * 0.9, width: r * 1.8, height: r * 1.8, rx: 1 });
    case 'diamond': return s('path', { d: `M0 ${-r * 1.25}L${r * 1.25} 0L0 ${r * 1.25}L${-r * 1.25} 0Z` });
    case 'triangle': return s('path', { d: `M0 ${-r * 1.2}L${r * 1.15} ${r * 0.85}L${-r * 1.15} ${r * 0.85}Z` });
    default: return s('circle', { r });
  }
}

function legendSwatch({ shape, tone, hollow, ring, line }) {
  const svg = s('svg', { class: 'ch-swatch', width: line ? 34 : 22, height: 22, viewBox: line ? '-17 -11 34 22' : '-11 -11 22 22', 'aria-hidden': 'true', focusable: 'false' });
  if (line) svg.appendChild(s('line', { class: `ch-track ch-tone-${tone || 'plain'}`, x1: -15, x2: 15, y1: 0, y2: 0 }));
  if (ring) svg.appendChild(s('circle', { class: `ch-ring ch-tone-${tone || 'plain'}`, r: 9 }));
  if (!line || shape) {
    const mark = markerShape(shape || 'circle', 5.5);
    mark.setAttribute('class', `ch-mark ch-tone-${tone || 'plain'}${hollow ? ' is-hollow' : ''}`);
    svg.appendChild(mark);
  }
  return svg;
}

/** The legend: groups of (swatch, words), as HTML so they wrap on a phone. */
export function buildLegend(groups) {
  return h('div', { class: 'ch-legend' }, groups.map((group) => h('div', { class: 'ch-legend-group' }, [
    group.title ? h('p', { class: 'ch-legend-title' }, group.title) : null,
    h('ul', { class: 'ch-legend-list' }, group.items.map((item) => h('li', { class: 'ch-legend-item' }, [
      legendSwatch(item),
      h('span', {}, item.text),
    ]))),
  ])));
}

// ------------------------------------------------------------------------ the chart
let chartCounter = 0;

/** Estimated width of a label before it is measured (about 0.58 em a character). */
const estimateWidth = (text, size) => text.length * size * 0.58;

export function createChart(container, spec) {
  const uid = `ch${++chartCounter}`;
  const figure = h('figure', { class: 'ch-figure' });
  const stage = h('div', { class: 'ch-stage' });
  const tip = h('div', { class: 'ch-tip', role: 'presentation' });
  tip.hidden = true;
  stage.appendChild(tip);
  figure.append(stage, buildLegend(spec.legend || []));
  container.appendChild(figure);

  let width = 0;
  let svg = null;
  let fade = { ids: new Set(), note: '' };
  let parts = new Map(); // id -> { link, label, leader, point }
  let tracks = new Map(); // id of the point a line ends at -> the line
  let groups = new Map(); // group -> ids of its points
  let geometry = null; // { xs, plot } of the last drawing, for the year marker
  let xMarker = null; // { value, text }
  let markerLayer = null;
  let destroyed = false;
  let frame = 0;

  function hideTip() {
    tip.hidden = true;
  }

  function showTip(point, cx, cy) {
    const lines = [].concat(point.tip || []);
    if (fade.ids.has(point.id) && fade.note) lines.push(fade.note);
    if (!lines.length) return;
    tip.replaceChildren(...lines.map((line, i) => h('span', { class: i === 0 ? 'ch-tip-head' : 'ch-tip-line' }, line)));
    tip.hidden = false;
    const stageWidth = stage.clientWidth;
    const w = tip.offsetWidth;
    const hgt = tip.offsetHeight;
    let left = cx + 14;
    if (left + w > stageWidth - 4) left = cx - 14 - w;
    left = Math.max(4, Math.min(left, stageWidth - w - 4));
    let top = cy - hgt - 12;
    if (top < 4) top = cy + 14;
    tip.style.left = `${Math.round(left)}px`;
    tip.style.top = `${Math.round(top)}px`;
  }

  function activate(point, event) {
    if (event && (event.button > 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey)) return;
    if (event) event.preventDefault();
    if (spec.onOpen) spec.onOpen(point);
  }

  function paintFade() {
    for (const [id, part] of parts) {
      const faded = fade.ids.has(id);
      part.link.classList.toggle('is-faded', faded);
      // A label belongs to a machine, not to one of its points: it fades when all of them have.
      const group = groups.get(part.point.group || part.point.id) || [id];
      const labelFaded = group.every((member) => fade.ids.has(member));
      if (part.label) part.label.classList.toggle('is-faded', labelFaded);
      if (part.leader) part.leader.classList.toggle('is-faded', labelFaded);
      const base = part.point.aria || part.point.label;
      part.link.setAttribute('aria-label', faded && fade.note ? `${base}. ${fade.note}` : base);
    }
    for (const [id, line] of tracks) line.classList.toggle('is-faded', fade.ids.has(id));
  }

  function paintMarker() {
    if (!markerLayer || !geometry) return;
    markerLayer.replaceChildren();
    if (!xMarker) return;
    const { xs, plot } = geometry;
    const [d0, d1] = spec.x.domain;
    if (xMarker.value < d0 || xMarker.value > d1) return;
    const x = f1(xs(xMarker.value));
    const flip = Number(x) > plot.x1 - 56;
    markerLayer.append(
      s('line', { class: 'ch-xmarker', x1: x, x2: x, y1: plot.y0, y2: plot.y1 }),
      s('text', { class: 'ch-xmarker-label', x: Number(x) + (flip ? -5 : 5), y: plot.y0 + 14, 'text-anchor': flip ? 'end' : 'start' }, xMarker.text),
    );
  }

  function draw() {
    const W = width;
    const compact = W < 560;
    const wide = W >= 1000;
    const labelSize = wide ? 15 : 13;
    const tickSize = wide ? 14 : 12;
    const xTicks = spec.x.ticks || (spec.x.kind === 'log' ? logTicks(...spec.x.domain).major.map((t) => t.value) : linearTicks(...spec.x.domain, compact ? 5 : 8).ticks);
    const yLog = spec.y.kind === 'log' ? logTicks(...spec.y.domain) : null;
    const yTicks = yLog ? yLog.major.map((t) => t.value) : (spec.y.ticks || linearTicks(...spec.y.domain, 6).ticks);
    const xText = (v) => (spec.x.tickLabel ? spec.x.tickLabel(v) : formatNumber(v));
    const yText = (v) => {
      if (spec.y.tickLabel) return spec.y.tickLabel(v);
      if (yLog) return powerOfTen(Math.round(Math.log10(v)));
      return formatNumber(v);
    };
    const yLabelWidth = Math.max(...yTicks.map((v) => estimateWidth(yText(v), tickSize)));
    const margin = {
      top: 14,
      right: compact ? 14 : 26,
      bottom: compact ? 54 : 60,
      left: Math.ceil(yLabelWidth) + (compact ? 34 : 42),
    };
    const H = spec.height ? spec.height(W) : Math.round(Math.min(compact ? 520 : 600, Math.max(compact ? 380 : 400, W * (compact ? 1.12 : (wide ? 0.46 : 0.55)))));
    const plot = { x0: margin.left, x1: W - margin.right, y0: margin.top, y1: H - margin.bottom };
    const xs = createScale({ kind: spec.x.kind || 'linear', domain: spec.x.domain, range: [plot.x0, plot.x1] });
    const ys = createScale({ kind: spec.y.kind || 'linear', domain: spec.y.domain, range: [plot.y1, plot.y0] });

    const node = s('svg', {
      class: `ch-svg${compact ? ' is-compact' : ''}${wide ? ' is-wide' : ''}`,
      viewBox: `0 0 ${W} ${H}`, width: W, height: H,
      role: 'group', 'aria-labelledby': `${uid}-t`, 'aria-describedby': `${uid}-d`, focusable: 'false',
    });
    node.append(
      s('title', { id: `${uid}-t` }, spec.title),
      s('desc', { id: `${uid}-d` }, typeof spec.description === 'function' ? spec.description() : spec.description),
    );

    // ---- grid and axes
    const grid = s('g', { class: 'ch-grid', 'aria-hidden': 'true' });
    const axes = s('g', { class: 'ch-axes', 'aria-hidden': 'true' });
    if (yLog) {
      for (const v of yLog.minor) grid.appendChild(s('line', { class: 'ch-grid-minor', x1: plot.x0, x2: plot.x1, y1: f1(ys(v)), y2: f1(ys(v)) }));
    }
    for (const v of yTicks) {
      const y = f1(ys(v));
      grid.appendChild(s('line', { class: 'ch-grid-major', x1: plot.x0, x2: plot.x1, y1: y, y2: y }));
      axes.append(
        s('line', { class: 'ch-tick', x1: plot.x0 - 5, x2: plot.x0, y1: y, y2: y }),
        s('text', { class: 'ch-tick-label', x: plot.x0 - 9, y: Number(y) + tickSize * 0.35, 'text-anchor': 'end' }, yText(v)),
      );
    }
    for (const v of xTicks) {
      const x = f1(xs(v));
      grid.appendChild(s('line', { class: 'ch-grid-major', x1: x, x2: x, y1: plot.y0, y2: plot.y1 }));
      axes.append(
        s('line', { class: 'ch-tick', x1: x, x2: x, y1: plot.y1, y2: plot.y1 + 5 }),
        s('text', { class: 'ch-tick-label', x, y: plot.y1 + 8 + tickSize, 'text-anchor': 'middle' }, xText(v)),
      );
    }
    axes.append(
      s('line', { class: 'ch-axis-line', x1: plot.x0, x2: plot.x1, y1: plot.y1, y2: plot.y1 }),
      s('line', { class: 'ch-axis-line', x1: plot.x0, x2: plot.x0, y1: plot.y0, y2: plot.y1 }),
      s('text', { class: 'ch-axis-title', x: (plot.x0 + plot.x1) / 2, y: H - 8, 'text-anchor': 'middle' }, spec.x.label),
      s('text', { class: 'ch-axis-title', transform: `translate(${14} ${(plot.y0 + plot.y1) / 2}) rotate(-90)`, 'text-anchor': 'middle' }, spec.y.label),
    );
    node.append(grid, axes);
    markerLayer = s('g', { class: 'ch-xmarker-layer', 'aria-hidden': 'true' });
    node.appendChild(markerLayer);
    geometry = { xs, plot };

    // ---- points
    const markR = compact ? 5.5 : 6.5;
    const trackLayer = s('g', { class: 'ch-tracks', 'aria-hidden': 'true' });
    const bars = s('g', { class: 'ch-bars', 'aria-hidden': 'true' });
    const leaders = s('g', { class: 'ch-leaders', 'aria-hidden': 'true' });
    const marks = s('g', { class: 'ch-points' });
    const labels = s('g', { class: 'ch-labels', 'aria-hidden': 'true' });
    node.append(trackLayer, bars, leaders, marks, labels);
    const next = new Map();
    const labelNodes = [];
    for (const point of spec.points) {
      const cx = xs(point.x);
      const cy = ys(point.y);
      const err = point.yErr && Number.isFinite(point.yErr[0]) && Number.isFinite(point.yErr[1]) ? point.yErr : null;
      let bar = null;
      if (err) {
        const y0 = ys(err[0]);
        const y1 = ys(err[1]);
        bar = s('path', { class: 'ch-errbar', d: `M${f1(cx)} ${f1(y0)}V${f1(y1)}M${f1(cx - 4)} ${f1(y0)}h8M${f1(cx - 4)} ${f1(y1)}h8` });
        bars.appendChild(bar);
      }
      const link = s('a', {
        class: 'ch-point', href: point.href || null, tabindex: 0, role: 'link',
        'aria-label': point.aria || point.label, 'data-id': point.id,
      });
      const g = s('g', { transform: `translate(${f1(cx)} ${f1(cy)})` });
      const mark = markerShape(point.shape || 'circle', markR);
      mark.setAttribute('class', `ch-mark ch-tone-${point.tone || 'plain'}${point.hollow ? ' is-hollow' : ''}`);
      g.append(...[
        s('circle', { class: 'ch-hit', r: compact ? 12 : 11 }),
        s('circle', { class: 'ch-focus', r: markR + 6 }),
        point.ring ? s('circle', { class: `ch-ring ch-tone-${point.tone || 'plain'}`, r: markR + 3.5 }) : null,
        mark,
      ].filter(Boolean));
      link.appendChild(g);
      link.addEventListener('click', (event) => activate(point, event));
      link.addEventListener('keydown', (event) => { if (event.key === 'Enter') activate(point, event); });
      link.addEventListener('pointerenter', () => showTip(point, cx, cy));
      link.addEventListener('pointerleave', hideTip);
      link.addEventListener('focus', () => showTip(point, cx, cy));
      link.addEventListener('blur', hideTip);
      marks.appendChild(link);
      next.set(point.id, { link, label: null, leader: null, point, cx, cy, bar });
      if (point.label) labelNodes.push(point);
    }

    // ---- the lines that join a machine's points, drawn under the markers
    const nextTracks = new Map();
    for (const line of spec.lines || []) {
      for (let i = 1; i < line.ids.length; i += 1) {
        const from = next.get(line.ids[i - 1]);
        const to = next.get(line.ids[i]);
        if (!from || !to) continue;
        const el = s('line', { class: `ch-track ch-tone-${line.tone || 'plain'}`, x1: f1(from.cx), y1: f1(from.cy), x2: f1(to.cx), y2: f1(to.cy) });
        trackLayer.appendChild(el);
        nextTracks.set(line.ids[i], el);
      }
    }
    tracks = nextTracks;
    groups = new Map();
    for (const point of spec.points) {
      const key = point.group || point.id;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(point.id);
    }

    // ---- labels (measured in place, then moved off each other and off the markers)
    container.querySelector('.ch-svg')?.remove();
    stage.insertBefore(node, tip);
    const items = [];
    const textFor = new Map();
    for (const point of labelNodes) {
      const t = s('text', { class: 'ch-label', 'data-for': point.id }, point.label);
      labels.appendChild(t);
      textFor.set(point.id, t);
      let box = null;
      try { box = t.getBBox(); } catch (error) { box = null; }
      const w = box && box.width > 0 ? box.width + 2 : estimateWidth(point.label, labelSize);
      const hgt = box && box.height > 0 ? box.height : labelSize * 1.25;
      const part = next.get(point.id);
      items.push({ id: point.id, x: part.cx, y: part.cy, r: markR + 1, w, h: hgt, priority: point.priority || 0, side: point.labelSide || null });
    }
    const segments = [];
    for (const line of spec.lines || []) {
      for (let i = 1; i < line.ids.length; i += 1) {
        const from = next.get(line.ids[i - 1]);
        const to = next.get(line.ids[i]);
        if (from && to) segments.push({ x1: from.cx, y1: from.cy, x2: to.cx, y2: to.cy });
      }
    }
    const placement = placeLabels(items, { x0: plot.x0 + 2, y0: plot.y0 - 2, x1: plot.x1 + margin.right - 4, y1: plot.y1 - 2 }, { segments, omit: !!spec.omitCrowdedLabels, leaderMinPriority: compact ? (spec.compactLeaderMinPriority || 0) : 0 });
    for (const point of labelNodes) {
      const t = textFor.get(point.id);
      const spot = placement.get(point.id);
      const part = next.get(point.id);
      if (!spot) { t.remove(); continue; }
      const baseline = spot.y + spot.h * 0.76;
      t.setAttribute('x', f1(spot.x + 1));
      t.setAttribute('y', f1(baseline));
      if (spot.leader) {
        // From the marker's rim to the nearest edge of the label.
        const lx = part.cx < spot.x ? spot.x : (part.cx > spot.x + spot.w ? spot.x + spot.w : part.cx);
        const ly = part.cy < spot.y ? spot.y : (part.cy > spot.y + spot.h ? spot.y + spot.h : spot.y + spot.h / 2);
        const dx = lx - part.cx;
        const dy = ly - part.cy;
        const len = Math.hypot(dx, dy) || 1;
        const line = s('line', { class: 'ch-leader', x1: f1(part.cx + (dx / len) * markR), y1: f1(part.cy + (dy / len) * markR), x2: f1(lx), y2: f1(ly) });
        leaders.appendChild(line);
        part.leader = line;
      }
      t.addEventListener('click', (event) => activate(point, event));
      t.addEventListener('pointerenter', () => showTip(point, part.cx, part.cy));
      t.addEventListener('pointerleave', hideTip);
      part.label = t;
    }

    parts = next;
    svg = node;
    paintFade();
    paintMarker();
    if (spec.onDraw) spec.onDraw({ width: W, labelled: placement.size, total: labelNodes.length });
  }

  function measure() {
    if (destroyed) return;
    const w = Math.floor(stage.clientWidth || 0);
    if (w < 200 || w === width) return;
    width = w;
    const active = document.activeElement && document.activeElement.getAttribute ? document.activeElement.getAttribute('data-id') : null;
    const hadFocus = active && stage.contains(document.activeElement);
    draw();
    if (hadFocus && parts.has(active)) parts.get(active).link.focus({ preventScroll: true });
  }

  let observer = null;
  if (typeof ResizeObserver !== 'undefined') {
    observer = new ResizeObserver(() => {
      window.cancelAnimationFrame(frame);
      frame = window.requestAnimationFrame(measure);
    });
    observer.observe(stage);
  }
  measure();
  frame = window.requestAnimationFrame(measure);
  // Labels are measured in the face the page uses: when the fonts arrive after the first drawing, draw again.
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(() => {
      if (destroyed || !width) return;
      width = 0;
      measure();
    });
  }
  stage.addEventListener('keydown', (event) => { if (event.key === 'Escape' && !tip.hidden) { hideTip(); event.stopPropagation(); } });

  return {
    element: figure,
    /** Points drawn faint: `ids` (a Set), and `note`, the words that go with them for a screen reader. */
    setFaded(ids, note = '') {
      fade = { ids: new Set(ids), note };
      paintFade();
    },
    /** A thin vertical line across the plot at `value` (a year, say), with `text` beside it; null removes it. */
    setXMarker(value, text = '') {
      xMarker = value == null ? null : { value, text };
      paintMarker();
    },
    /** Which points are on the page (for a check), as ids. */
    pointIds() {
      return [...parts.keys()];
    },
    svg: () => svg,
    destroy() {
      destroyed = true;
      window.cancelAnimationFrame(frame);
      if (observer) observer.disconnect();
    },
  };
}

// ------------------------------------------------------------------------- the table
/**
 * The same rows as a table. `columns`: `{ key?, label, cell(row) -> string | Node, numeric?, header? }`; the
 * column marked `header` becomes the row header. Each cell carries its label in `data-label`, so a phone
 * (views.css) can stack a row as a card with every value still named.
 */
export function dataTable({ caption, columns, rows, rowId, className = '' }) {
  const body = h('tbody', {}, rows.map((row) => {
    const tr = h('tr', { 'data-id': rowId ? rowId(row) : null });
    for (const column of columns) {
      const value = column.cell ? column.cell(row) : row[column.key];
      const attrs = { 'data-label': column.label, class: column.numeric ? 'ch-num' : null };
      tr.appendChild(column.header
        ? h('th', { scope: 'row', ...attrs }, value)
        : h('td', attrs, value));
    }
    return tr;
  }));
  const table = h('table', { class: `ch-table ${className}`.trim() }, [
    h('caption', {}, caption),
    h('thead', {}, h('tr', {}, columns.map((column) => h('th', { scope: 'col' }, column.label)))),
    body,
  ]);
  return h('div', { class: 'ch-table-scroll' }, table);
}
