// detector-scale.js — "Detector line-up": the detectors the Atlas has sourced sizes for,
// drawn side by side at ONE linear scale beside a 1.8 m person.
//
//   #/view/detector-scale
//
// What is drawn, and from what:
//   * each detector's width and height, read from its record's sourced `specs`
//     (scale-detectors.js says which key gives which dimension); a detector whose record
//     lacks a number is listed under "not drawn", never drawn from a guess;
//   * IceCube, whose instrumented ice is a kilometre deep, in a panel of its own at its
//     own stated scale (it cannot share the line-up's scale), with the line-up's
//     detectors drawn again beside it at that same scale. No log or broken axis is used
//     anywhere: both panels are linear;
//   * the numbers in a table, and — in "Inputs and method" — every dimension with its
//     verbatim quote and source.
//
// Mounted by host.js through registry.js.

import {
  ICECUBE, PERSON_HEIGHT_M, WORKING_TITLE, buildLineup, lengthSpec, packRows,
} from './scale-detectors.js';
import { EARTH_RADIUS_M, boundsCentre, vertices } from './scale-geometry.js';
import { statusForTimeline, timelineAbsenceReason } from '../model.js';

const SVG_NS = 'http://www.w3.org/2000/svg';

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
    if (key === 'text') el.textContent = value;
    else if (value !== null && value !== undefined) el.setAttribute(key, String(value));
  }
  for (const child of [].concat(children)) {
    if (child == null) continue;
    el.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
  }
  return el;
}

/** replaceChildren that leaves out a missing (null) child instead of writing the word "null". */
const put = (el, ...nodes) => el.replaceChildren(...nodes.filter((node) => node != null));

// ------------------------------------------------------------------- formatting
/** Metres as a person reads them: "39.3", "62", "4.2", "1,000". */
function num(value) {
  const digits = value >= 100 ? 0 : (value >= 10 ? 1 : 2);
  return Number(value.toFixed(digits)).toLocaleString('en-US');
}
const mText = (spec) => `${spec.approx ? '~' : ''}${num(spec.metres)} m`;
const dimsText = (entry) => `${entry.width.approx ? '~' : ''}${num(entry.width.metres)} × ${entry.height.approx ? '~' : ''}${num(entry.height.metres)} m`;

const STATUS_WORDS = {
  active: '', upgrade: '', construction: 'under construction', commissioning: 'commissioning',
  proposed: 'proposed', approved: 'approved', planned: 'planned', completed: 'completed',
  decommissioned: 'decommissioned', shutdown: 'shut down',
};
function statusWord(record, timelineState) {
  const segments = record.state_segments || [];
  const resolved = statusForTimeline(segments, timelineState || {});
  const status = resolved ? resolved.status : null;
  if (!status) {
    const reason = timelineAbsenceReason(segments, timelineState || { year: 2026 });
    if (reason === 'ended') return 'no longer operating';
    if (reason === 'not_yet') return 'not yet built';
    return 'no state recorded';
  }
  return Object.prototype.hasOwnProperty.call(STATUS_WORDS, status) ? STATUS_WORDS[status] : status;
}

const NICE_STEPS = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000];
function niceStep(minMetres) {
  return NICE_STEPS.find((step) => step >= minMetres) || NICE_STEPS[NICE_STEPS.length - 1];
}

// -------------------------------------------------------------------- the shapes
/** The outline of one detector as an SVG path, its box (x, y) top-left, w × h pixels. */
function outlinePath(shape, x, y, w, hgt) {
  if (shape === 'sphere') {
    const r = hgt / 2;
    return `M ${x + w / 2 - r} ${y + r} a ${r} ${r} 0 1 0 ${2 * r} 0 a ${r} ${r} 0 1 0 ${-2 * r} 0 Z`;
  }
  if (shape === 'cylinder-v') {
    const ry = Math.min(w * 0.12, hgt * 0.25);
    return `M ${x} ${y + ry} A ${w / 2} ${ry} 0 0 1 ${x + w} ${y + ry} L ${x + w} ${y + hgt - ry}`
      + ` A ${w / 2} ${ry} 0 0 1 ${x} ${y + hgt - ry} Z`;
  }
  if (shape === 'cylinder-h') {
    const rx = Math.min(hgt * 0.12, w * 0.25);
    return `M ${x + rx} ${y} L ${x + w - rx} ${y} A ${rx} ${hgt / 2} 0 0 1 ${x + w - rx} ${y + hgt}`
      + ` L ${x + rx} ${y + hgt} A ${rx} ${hgt / 2} 0 0 1 ${x + rx} ${y} Z`;
  }
  return `M ${x} ${y} h ${w} v ${hgt} h ${-w} Z`;
}

/** The ring that shows a cylinder is round (the visible rim of its top, or its near end). */
function rimPath(shape, x, y, w, hgt) {
  if (shape === 'cylinder-v') {
    const ry = Math.min(w * 0.12, hgt * 0.25);
    return `M ${x} ${y + ry} A ${w / 2} ${ry} 0 0 0 ${x + w} ${y + ry}`;
  }
  if (shape === 'cylinder-h') {
    const rx = Math.min(hgt * 0.12, w * 0.25);
    return `M ${x + w - rx} ${y} A ${rx} ${hgt / 2} 0 0 0 ${x + w - rx} ${y + hgt}`;
  }
  return null;
}

/** A person, `hgt` pixels tall, standing with feet at (x, base). A line figure: its
 * proportions follow the 1.8 m height, its strokes stay legible at a few pixels. */
function person(x, base, hgt) {
  const u = hgt / PERSON_HEIGHT_M; // pixels per metre
  const head = Math.max(0.11 * u, 1.3);
  const top = base - hgt;
  return s('g', { class: 'ds-person', 'aria-hidden': 'true' }, [
    s('circle', { cx: x, cy: top + head, r: head }),
    s('path', {
      d: `M ${x} ${top + 2 * head} L ${x} ${base - 0.85 * u} M ${x - 0.28 * u} ${top + 0.35 * u} L ${x} ${top + 2.3 * head}`
        + ` L ${x + 0.28 * u} ${top + 0.35 * u} M ${x} ${base - 0.85 * u} L ${x - 0.17 * u} ${base} M ${x} ${base - 0.85 * u} L ${x + 0.17 * u} ${base}`,
    }),
  ]);
}

// ------------------------------------------------------------------------ the line-up
const GUTTER_PX = 48; // the ruler's column
const PERSON_SLOT_PX = 34;
const LABEL_LINE_PX = 15;
const ROW_PAD_TOP_PX = 18;
const ROW_GAP_PX = 22;
const MIN_SLOT_GAP_PX = 14;

function labelLines(entry, timelineState) {
  const status = statusWord(entry.record, timelineState);
  return [
    { text: entry.label, cls: 'ds-t-name' },
    entry.part ? { text: entry.part, cls: 'ds-t-part' } : null,
    { text: dimsText(entry), cls: 'ds-t-dims' },
    status ? { text: status, cls: 'ds-t-status' } : null,
  ].filter(Boolean);
}

/** Pixels wide the text of a label needs (an estimate: no font metrics at hand). */
function labelWidthPx(lines) {
  return Math.ceil(Math.max(...lines.map((line) => line.text.length * (line.cls === 'ds-t-name' ? 7.4 : 6.5)))) + 6;
}

function drawLineup(lineup, width, ppm, timelineState, navigate) {
  const entries = lineup.map((entry) => ({ ...entry, lines: labelLines(entry, timelineState) }));
  const usable = Math.max(240, width - GUTTER_PX - PERSON_SLOT_PX - 12);
  const slotM = (entry) => Math.max(entry.width.metres, labelWidthPx(entry.lines) / ppm);
  const widest = Math.max(...entries.map(slotM));
  const rowWidthM = Math.max(usable / ppm, widest);
  const rows = packRows(entries, rowWidthM, MIN_SLOT_GAP_PX / ppm, slotM);
  const rowPx = rows.map((row) => ({
    row,
    height: ROW_PAD_TOP_PX + row.heightM * ppm + 8 + 4 * LABEL_LINE_PX,
  }));
  const contentWidth = GUTTER_PX + PERSON_SLOT_PX + rowWidthM * ppm + 12;
  const svgWidth = Math.max(width, Math.ceil(contentWidth));
  const totalHeight = rowPx.reduce((sum, r) => sum + r.height + ROW_GAP_PX, 0) + 6;
  const step = niceStep(34 / ppm);

  const svg = s('svg', {
    class: 'ds-svg', width: svgWidth, height: totalHeight, viewBox: `0 0 ${svgWidth} ${totalHeight}`,
    role: 'group', 'aria-labelledby': 'ds-line-title ds-line-desc',
  });
  svg.append(
    s('title', { id: 'ds-line-title', text: 'Detectors at one true scale' }),
    s('desc', {
      id: 'ds-line-desc',
      text: `${entries.length} detectors drawn at the same linear scale, ${ppm.toFixed(1)} pixels to the metre, `
        + 'each beside a 1.8 metre person. Each detector is a link to its record; the same sizes are in the table below.',
    }),
  );

  let y = 0;
  rowPx.forEach(({ row, height }, rowIndex) => {
    const base = y + ROW_PAD_TOP_PX + row.heightM * ppm; // the row's ground line
    const x0 = GUTTER_PX + PERSON_SLOT_PX;
    const group = s('g', { class: 'ds-row' });
    // ruler and faint gridlines every `step` metres
    group.append(s('line', { class: 'ds-ruler', x1: GUTTER_PX - 8, x2: GUTTER_PX - 8, y1: base, y2: base - row.heightM * ppm }));
    for (let m = 0; m <= row.heightM + 1e-9; m += step) {
      const ty = base - m * ppm;
      group.append(
        s('line', { class: 'ds-tick', x1: GUTTER_PX - 14, x2: GUTTER_PX - 8, y1: ty, y2: ty }),
        s('text', { class: 'ds-t-axis', x: GUTTER_PX - 18, y: ty + 4, 'text-anchor': 'end', text: `${m} m` }),
      );
      if (m > 0) group.append(s('line', { class: 'ds-grid', x1: GUTTER_PX - 8, x2: svgWidth - 6, y1: ty, y2: ty }));
    }
    group.append(s('line', { class: 'ds-ground', x1: GUTTER_PX - 8, x2: svgWidth - 6, y1: base, y2: base }));
    group.append(person(GUTTER_PX + 14, base, PERSON_HEIGHT_M * ppm));
    if (rowIndex === 0) {
      group.append(s('text', { class: 'ds-t-person', x: GUTTER_PX + 14, y: base + 14, 'text-anchor': 'middle', text: 'person' }),
        s('text', { class: 'ds-t-person', x: GUTTER_PX + 14, y: base + 27, 'text-anchor': 'middle', text: '1.8 m' }));
    }
    for (const { entry, x } of row.items) {
      const slot = slotM(entry);
      const slotPx = slot * ppm;
      const wPx = entry.width.metres * ppm;
      const hPx = entry.height.metres * ppm;
      const left = x0 + x * ppm + (slotPx - wPx) / 2;
      const top = base - hPx;
      const slug = entry.id.split(':')[1];
      const link = s('a', {
        class: 'ds-link', href: `#/detector/${slug}`, tabindex: '0', role: 'link', 'data-detector': entry.id,
        'aria-label': `${entry.label}${entry.part ? `, ${entry.part}` : ''}: ${dimsText(entry)}. Open its record.`,
      });
      const open = (event) => {
        if (event.type === 'click' && (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey)) return;
        event.preventDefault();
        navigate({ entity: { type: 'detector', slug } });
      };
      link.addEventListener('click', open);
      link.addEventListener('keydown', (event) => { if (event.key === 'Enter') open(event); });
      link.append(s('title', { text: `${entry.label}${entry.part ? ` (${entry.part})` : ''}: ${dimsText(entry)}` }));
      // a transparent box over the label and the shape, so the whole slot is the target
      link.append(s('rect', { class: 'ds-hit', x: left - 4, y: top - 3, width: Math.max(wPx, labelWidthPx(entry.lines)) + 8, height: hPx + 8 + entry.lines.length * LABEL_LINE_PX }));
      link.append(s('path', { class: 'ds-shape', d: outlinePath(entry.shape, left, top, wPx, hPx) }));
      const rim = rimPath(entry.shape, left, top, wPx, hPx);
      if (rim) link.append(s('path', { class: 'ds-rim', d: rim }));
      if (entry.inner) {
        const iw = entry.inner.width.metres * ppm;
        const ih = entry.inner.height.metres * ppm;
        link.append(s('path', {
          class: 'ds-inner', d: outlinePath(entry.shape, left + (wPx - iw) / 2, top + (hPx - ih) / 2, iw, ih),
        }));
      }
      const cx = left + wPx / 2;
      entry.lines.forEach((line, i) => {
        link.append(s('text', { class: line.cls, x: cx, y: base + 16 + i * LABEL_LINE_PX, 'text-anchor': 'middle', text: line.text }));
      });
      group.append(link);
    }
    svg.append(group);
    y += height + ROW_GAP_PX;
  });
  return { svg, rows, step };
}

// --------------------------------------------------------------- IceCube's own scale
/** What the IceCube panel needs from the record and the South Pole map's geometry. */
async function loadIceCube(atlas, loader) {
  const record = (atlas.detectors || {})[ICECUBE.id];
  if (!record) return { error: 'The IceCube record is not in this data build.' };
  const depthMin = lengthSpec(record, ICECUBE.depthMin);
  const depthMax = lengthSpec(record, ICECUBE.depthMax);
  if (!depthMin || !depthMax) return { error: 'The IceCube record has no sourced depth range, so its panel is not drawn.' };
  const spacing = lengthSpec(record, ICECUBE.spacing);
  const volume = record.specs && record.specs[ICECUBE.volume];
  const meta = (atlas.maps || {})[ICECUBE.footprintMap];
  let footprint = null;
  let note = '';
  if (meta) {
    try {
      const bundle = await loader.getGeometry(meta.bundle);
      const hull = bundle.features.find((f) => f.id === ICECUBE.footprintGeometry);
      const strings = bundle.features.find((f) => f.id === 'geometry:icecube-strings-1-78');
      if (hull) {
        const centre = boundsCentre(vertices(hull.geometry), true);
        footprint = {
          widthM: centre.widthM, heightM: centre.heightM,
          areaM2: hull.measured ? hull.measured.area_m2 : null,
          accuracyM: hull.accuracy_m, method: hull.method, feature: hull,
          strings: [],
        };
        if (strings && strings.geometry.type === 'MultiPolygon') {
          // Each string's east-west position, in metres from the footprint's centre, in the
          // plane the map draws (south polar, grid east to the right): the side view draws
          // every string where the record puts it.
          const eastM = (lat, lon) => ((90 - Math.abs(lat)) * Math.PI / 180) * EARTH_RADIUS_M * Math.sin((lon * Math.PI) / 180);
          const x0 = eastM(centre.lat, centre.lon);
          for (const polygon of strings.geometry.coordinates) {
            const middle = boundsCentre(vertices({ type: 'Polygon', coordinates: polygon }), true);
            footprint.strings.push(eastM(middle.lat, middle.lon) - x0);
          }
        }
      }
    } catch (error) {
      note = `The South Pole map could not be loaded (${error.message}), so IceCube's footprint is not drawn; its sourced depth range still is.`;
    }
  }
  return { record, depthMin, depthMax, spacing, volume, footprint, note };
}

function drawIceCube(ice, lineup, width, timelineState) {
  const { depthMin, depthMax, footprint } = ice;
  const axisDepth = Math.ceil((depthMax.metres + 150) / 500) * 500; // the axis runs a little past the array
  const compact = width < 560;
  const topPad = 56;
  const kpm = Math.min(0.2, (compact ? 330 : 430) / axisDepth); // px per metre of THIS panel
  const heightPx = topPad + axisDepth * kpm + 56;
  const xAxis = 62;
  const blockW = (footprint ? footprint.widthM : 1000) * kpm;
  const xBlock = xAxis + 36;
  const svg = s('svg', {
    class: 'ds-svg ds-ice-svg', width, height: heightPx, viewBox: `0 0 ${width} ${heightPx}`,
    role: 'group', 'aria-labelledby': 'ds-ice-title ds-ice-desc',
  });
  svg.append(
    s('title', { id: 'ds-ice-title', text: 'IceCube at its own scale' }),
    s('desc', {
      id: 'ds-ice-desc',
      text: `A vertical section of the ice at ${(1 / kpm).toFixed(1)} metres to the pixel: IceCube's instrumented volume lies `
        + `between ${depthMin.metres} and ${depthMax.metres} metres below the surface. The detectors of the line-up above are drawn again at this scale.`,
    }),
  );
  const y0 = topPad;
  const yAt = (depth) => y0 + depth * kpm;
  // the ice, and the surface
  svg.append(s('rect', { class: 'ds-ice', x: xAxis, y: y0, width: Math.max(0, width - xAxis - 8), height: axisDepth * kpm }));
  svg.append(s('line', { class: 'ds-surface', x1: xAxis, x2: width - 8, y1: y0, y2: y0 }));
  svg.append(s('text', { class: 'ds-t-part', x: width - 10, y: y0 - 6, 'text-anchor': 'end', text: 'ice surface' }));
  // the depth axis, every 500 m
  svg.append(s('line', { class: 'ds-ruler', x1: xAxis, x2: xAxis, y1: y0, y2: yAt(axisDepth) }));
  for (let d = 0; d <= axisDepth; d += 500) {
    svg.append(
      s('line', { class: 'ds-tick', x1: xAxis - 6, x2: xAxis, y1: yAt(d), y2: yAt(d) }),
      s('text', { class: 'ds-t-axis', x: xAxis - 9, y: yAt(d) + 4, 'text-anchor': 'end', text: `${d.toLocaleString('en-US')} m` }),
    );
  }
  svg.append(s('text', { class: 'ds-t-part', x: 12, y: y0 - 24, text: 'depth below the surface' }));
  // the instrumented block and its strings
  svg.append(s('rect', {
    class: 'ds-ice-block', x: xBlock, y: yAt(depthMin.metres), width: blockW, height: (depthMax.metres - depthMin.metres) * kpm,
  }));
  if (footprint && footprint.strings.length) {
    const mid = xBlock + blockW / 2;
    for (const x of footprint.strings) {
      svg.append(s('line', {
        class: 'ds-ice-string', x1: mid + x * kpm, x2: mid + x * kpm, y1: yAt(depthMin.metres), y2: yAt(depthMax.metres),
      }));
    }
  }
  const textX = xBlock + blockW + 14;
  const dTop = yAt(depthMin.metres);
  const dBot = yAt(depthMax.metres);
  svg.append(
    s('line', { class: 'ds-dim', x1: xBlock - 10, x2: xBlock - 10, y1: dTop, y2: dBot }),
    s('text', { class: 'ds-t-name', x: textX, y: (dTop + dBot) / 2 - 14, text: 'IceCube' }),
    s('text', { class: 'ds-t-dims', x: textX, y: (dTop + dBot) / 2 + 3, text: `${depthMin.metres.toLocaleString('en-US')}–${depthMax.metres.toLocaleString('en-US')} m deep` }),
    s('text', { class: 'ds-t-part', x: textX, y: (dTop + dBot) / 2 + 19, text: footprint
      ? `${num(footprint.widthM)} m across, ${num(footprint.heightM)} m north–south` : 'footprint not drawn' }),
  );
  // a scale bar of 1 km, vertical, in this panel's own scale
  const barX = width - 22;
  const barTop = yAt(axisDepth) - 1000 * kpm;
  svg.append(
    s('line', { class: 'ds-bar', x1: barX, x2: barX, y1: barTop, y2: yAt(axisDepth) }),
    s('line', { class: 'ds-bar', x1: barX - 5, x2: barX + 5, y1: barTop, y2: barTop }),
    s('line', { class: 'ds-bar', x1: barX - 5, x2: barX + 5, y1: yAt(axisDepth), y2: yAt(axisDepth) }),
    s('text', { class: 'ds-t-dims', x: barX - 9, y: (barTop + yAt(axisDepth)) / 2 + 4, 'text-anchor': 'end', text: '1 km' }),
  );
  // the line-up, at this panel's scale, standing on the surface line
  const others = lineup.slice().sort((a, b) => b.height.metres - a.height.metres);
  let x = Math.max(xBlock + blockW + 190, xBlock + blockW + 14);
  const room = width - x - 46;
  const strip = s('g', { class: 'ds-strip' });
  let used = 0;
  for (const entry of others) {
    const w = entry.width.metres * kpm;
    const hgt = entry.height.metres * kpm;
    if (used + w > room) break;
    strip.append(s('path', { class: 'ds-shape ds-shape-small', d: outlinePath(entry.shape, x + used, y0 - hgt, w, hgt) }));
    used += w + 3;
  }
  if (used > 0) {
    svg.append(strip);
    svg.append(s('text', {
      class: 'ds-t-part', x: x + used / 2, y: y0 + 18, 'text-anchor': 'middle', text: 'the line-up above, at this scale',
    }), s('text', {
      class: 'ds-t-part', x: x + used / 2, y: y0 + 33, 'text-anchor': 'middle',
      text: `(the tallest, ${num(others[0].height.metres)} m, is ${num(others[0].height.metres * kpm)} px)`,
    }));
  }
  return svg;
}

// ------------------------------------------------------------------------- the tables
function dimensionRows(lineup) {
  const rows = [];
  for (const entry of lineup) {
    const label = entry.label;
    const add = (spec, what) => rows.push({ entry, label, what, spec, detectorId: entry.id });
    add(entry.width, entry.shape === 'sphere' ? 'diameter' : (entry.shape === 'cylinder-v' ? 'diameter (width)' : 'width (length)'));
    if (entry.height !== entry.width && entry.height.key !== entry.width.key) {
      add(entry.height, entry.shape === 'cylinder-h' ? 'height (diameter)' : 'height');
    }
    if (entry.inner) {
      add(entry.inner.width, `${entry.inner.part}: diameter`);
      add(entry.inner.height, `${entry.inner.part}: height`);
    }
  }
  return rows;
}

function summaryTable(lineup, link) {
  return h('div', { class: 'bs-table-scroll' }, h('table', { class: 'bs-table' }, [
    h('caption', {}, 'The sizes drawn above, from each detector’s record'),
    h('thead', {}, h('tr', {}, ['Detector', 'What is measured', 'Width', 'Height', 'Inside it']
      .map((label) => h('th', { scope: 'col' }, label)))),
    h('tbody', {}, lineup.slice().sort((a, b) => b.height.metres - a.height.metres).map((entry) => h('tr', {}, [
      h('th', { scope: 'row' }, link(entry)),
      h('td', { 'data-label': 'What is measured' }, entry.part || 'the detector'),
      h('td', { class: 'bs-num', 'data-label': 'Width' }, mText(entry.width)),
      h('td', { class: 'bs-num', 'data-label': 'Height' }, mText(entry.height)),
      h('td', { 'data-label': 'Inside it' }, entry.inner
        ? `${entry.inner.part}: ${num(entry.inner.width.metres)} × ${num(entry.inner.height.metres)} m (dashed outline)` : '—'),
    ]))),
  ]));
}

// ------------------------------------------------------------------------------- mount
export async function mount(ctx) {
  const { atlas, loader, host, navigate } = ctx;
  let timelineState = ctx.timelineState;
  const lineup0 = buildLineup(atlas);
  if (!lineup0.drawn.length) {
    host.fail('No detector in this data build has the sourced dimensions the line-up needs, so nothing is drawn.');
    return null;
  }
  const lineup = lineup0.drawn;
  const skipped = lineup0.skipped;
  const { body } = host;

  host.setSubtitle(`${lineup.length} detectors at one linear scale, each beside a ${PERSON_HEIGHT_M} m person — and IceCube, a kilometre deep, at its own.`);
  const link = (entry) => {
    const slug = entry.id.split(':')[1];
    const a = h('a', { class: 'entity-link', href: `#/detector/${slug}` }, entry.label);
    a.addEventListener('click', (event) => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      navigate({ entity: { type: 'detector', slug } });
    });
    return a;
  };

  // ---- the controls: the scale is the reader's to change, the proportions never change
  let manual = null; // px per metre chosen with the buttons; null = fit to the stage
  const figureWrap = h('div', { class: 'ds-figure-scroll' });
  const scaleNote = h('p', { class: 'ds-scale-note', id: 'ds-scale-note' });
  const zoomIn = h('button', { type: 'button', class: 'text-btn', id: 'ds-zoom-in' }, 'Larger');
  const zoomOut = h('button', { type: 'button', class: 'text-btn', id: 'ds-zoom-out' }, 'Smaller');
  const zoomFit = h('button', { type: 'button', class: 'text-btn', id: 'ds-zoom-fit' }, 'Fit to the page');
  const controls = h('div', { class: 'ds-controls', role: 'group', 'aria-label': 'Scale of the line-up' }, [
    h('span', { class: 'ds-controls-label' }, 'Zoom the line-up:'), zoomOut, zoomIn, zoomFit,
  ]);
  const iceWrap = h('div', { class: 'ds-ice-wrap' });
  const iceCaption = h('p', { class: 'ds-caption', id: 'ds-ice-caption' });

  const lede = h('p', { class: 'ds-lede' }, [
    'How big is a detector? Each shape below is drawn from sizes recorded in the Atlas, ',
    'on one linear scale, so a width on the page is a width in the world. A detector’s outline is its overall size as its source gives it, ',
    'simplified to a cylinder, a sphere or a box seen from the side. Select one to open its record.',
  ]);
  const figure = h('figure', { class: 'ds-figure' }, [
    controls, figureWrap, scaleNote,
  ]);
  const iceFigure = h('figure', { class: 'ds-figure ds-ice-figure' }, [
    h('h3', { class: 'ds-h3', id: 'ds-ice-h' }, 'IceCube, at its own scale'),
    h('div', { class: 'ds-ice-body' }, [iceWrap, iceCaption]),
  ]);
  const skippedNote = skipped.length ? h('p', { class: 'ds-skipped' }, [
    h('strong', {}, 'Not drawn: '),
    skipped.map((row) => `${row.name} (${row.reason})`).join('; '),
    '. A detector appears here only when its record carries the sourced numbers.',
  ]) : null;
  body.replaceChildren(...[lede, figure, iceFigure, summaryTable(lineup, link), skippedNote].filter(Boolean));

  // ---- drawing
  let lastWidth = 0;
  function autoScale(width) {
    // about 200 m of row on a wide stage; never smaller than 3 px to the metre
    return Math.min(8, Math.max(3.2, (width - GUTTER_PX - PERSON_SLOT_PX) / 200));
  }
  let scale = 4;
  let ice = null;
  function drawAll() {
    const width = Math.floor(figureWrap.clientWidth || body.clientWidth || 360);
    if (width < 240) return;
    lastWidth = width;
    scale = manual == null ? autoScale(width) : manual;
    const { svg, step } = drawLineup(lineup, width, scale, timelineState, navigate);
    figureWrap.replaceChildren(svg);
    scaleNote.replaceChildren(
      h('strong', {}, `Scale: ${scale >= 10 ? scale.toFixed(0) : scale.toFixed(1)} pixels to the metre, the same horizontally and vertically. `),
      `The grey ruler marks every ${step} m. No log scale, no broken axis: one linear scale for every shape here. `,
      'IceCube’s kilometre does not fit on it, so it has its own panel below, with its own scale bar. ',
      `The status under a name (“under construction”, “no longer operating”) is the record’s, for ${timelineState && timelineState.range ? `${timelineState.range[0]}–${timelineState.range[1]}` : (timelineState && timelineState.year != null ? timelineState.year : 'the selected year')} on the timeline.`,
    );
    zoomOut.disabled = scale <= 1.01;
    zoomIn.disabled = scale >= 40;
    if (ice && ice.record) {
      const w = Math.floor(iceWrap.clientWidth || width);
      iceWrap.replaceChildren(drawIceCube(ice, lineup, Math.max(w, 280), timelineState));
    }
  }
  zoomIn.addEventListener('click', () => { manual = Math.min(40, scale * 1.5); drawAll(); host.announce(`Scale ${manual.toFixed(1)} pixels to the metre.`); });
  zoomOut.addEventListener('click', () => { manual = Math.max(1, scale / 1.5); drawAll(); host.announce(`Scale ${manual.toFixed(1)} pixels to the metre.`); });
  zoomFit.addEventListener('click', () => { manual = null; drawAll(); host.announce('Scale fitted to the page.'); });

  let frame = 0;
  const redraw = () => {
    window.cancelAnimationFrame(frame);
    frame = window.requestAnimationFrame(() => {
      const width = Math.floor(figureWrap.clientWidth || 0);
      if (width && Math.abs(width - lastWidth) > 4) drawAll();
    });
  };
  let observer = null;
  if (typeof ResizeObserver !== 'undefined') {
    observer = new ResizeObserver(redraw);
    observer.observe(figureWrap);
  }
  drawAll();
  window.requestAnimationFrame(drawAll);

  // ---- IceCube's panel needs the South Pole map's geometry: fetched now, after the first paint
  let destroyed = false;
  loadIceCube(atlas, loader).then((result) => {
    if (destroyed) return;
    ice = result;
    if (result.error) {
      iceWrap.replaceChildren(h('p', { class: 'error-note', role: 'alert' }, result.error));
      return;
    }
    const f = result.footprint;
    iceCaption.replaceChildren(
      h('strong', {}, 'A different scale. '),
      `The bar at the right is 1 km. The instrumented ice lies ${result.depthMin.metres.toLocaleString('en-US')}–${result.depthMax.metres.toLocaleString('en-US')} m below the surface`,
      result.volume ? `, holding ${result.volume.display}` : '',
      result.spacing ? `, on strings ${mText(result.spacing)} apart` : '',
      '. ',
      f ? `The footprint (${num(f.widthM)} × ${num(f.heightM)} m${f.areaM2 ? `, ${(f.areaM2 / 1e6).toFixed(2)} km² for the 78 standard strings` : ''}) and every string are drawn from the Atlas’s own South Pole geometry records. ` : '',
      'The detectors of the line-up above stand on the surface line at this same scale, to show how small they are beside it (they are not at IceCube’s depth).',
      result.note ? ` ${result.note}` : '',
    );
    drawAll();
    fillIceMethod(host.method, result);
  }).catch((error) => {
    if (destroyed) return;
    iceWrap.replaceChildren(h('p', { class: 'error-note', role: 'alert' }, `IceCube's panel could not be drawn: ${error.message}.`));
  });
  // the method is useful before IceCube's geometry arrives; its IceCube part fills in after
  fillMethod(host.method, { lineup, skipped, link, loader, getDestroyed: () => destroyed });

  host.announce(`${WORKING_TITLE}: ${lineup.length} detectors drawn at one scale beside a ${PERSON_HEIGHT_M} metre person.`);

  return {
    update(next) {
      timelineState = next.timelineState;
      drawAll();
    },
    destroy() {
      destroyed = true;
      window.cancelAnimationFrame(frame);
      if (observer) observer.disconnect();
    },
  };
}

// ------------------------------------------------------------------ the method disclosure
let methodToken = 0;

function fillMethod(el, { lineup, skipped, link, loader, getDestroyed }) {
  const token = ++methodToken;
  const rows = dimensionRows(lineup);
  const sourceTable = h('div', { class: 'bs-table-scroll' }, h('table', { class: 'bs-table ds-source-table' }, [
    h('caption', {}, 'Every dimension: its value, source and the words the source uses'),
    h('thead', {}, h('tr', {}, ['Detector', 'Dimension', 'Value', 'Source and locator', 'Quoted from the source']
      .map((label) => h('th', { scope: 'col' }, label)))),
    h('tbody', {}, rows.map((row) => h('tr', { 'data-detector': row.detectorId, 'data-spec': row.spec.key }, [
      h('th', { scope: 'row' }, link(row.entry)),
      h('td', { 'data-label': 'Dimension' }, [row.what, h('div', { class: 'ds-spec-key' }, `specs.${row.spec.key}`)]),
      h('td', { class: 'bs-num', 'data-label': 'Value' }, mText(row.spec)),
      h('td', { class: 'ds-cite', 'data-cite': `${row.detectorId}|${row.spec.key}`, 'data-label': 'Source and locator' }, 'Loading the source…'),
      h('td', { class: 'ds-quote', 'data-quote': `${row.detectorId}|${row.spec.key}`, 'data-label': 'Quoted from the source' }, ''),
    ]))),
  ]));
  put(el,
    h('p', { class: 'ds-method-intro' }, [
      'Every size on this page is a number in a detector record’s sourced `specs`; the code only chooses a shape and which numbers are its width and height. ',
      'The table gives each number beside the sentence its source uses, so it can be checked against the source.',
    ]),
    h('h3', {}, 'How it is drawn'),
    h('ul', { class: 'ds-method-list' }, [
      h('li', {}, 'Scale: one pixel-per-metre factor for the whole line-up, the same on both axes. The ruler and the grid lines mark whole metres; the person is 1.8 m, a drawing convention and not a record.'),
      h('li', {}, 'Shapes: a vertical cylinder (Super-Kamiokande, Hyper-Kamiokande, LZ’s water shield) is drawn as its side view, with its diameter as width and its height as height; a horizontal cylinder (ATLAS, CMS, KATRIN’s main spectrometer, the STAR TPC) with its length as width and its diameter as height; a sphere (JUNO, SNO, MiniBooNE) by its diameter; a box (DUNE’s cryostat, the NOvA far detector, ALICE, LHCb) by its length and height. The real instruments are not these simple solids.'),
      h('li', {}, 'Super-Kamiokande’s dashed inner outline is its inner detector, drawn centred in the tank; the detector paper says about 2.5 m of water remain on every side of it.'),
      h('li', {}, 'Rows are filled tallest first at one scale; where the page is narrow they wrap. “Larger” and “Smaller” change the scale for every shape together.'),
      h('li', {}, 'IceCube is a kilometre of instrumented ice, which cannot share the line-up’s scale without shrinking every other detector to nothing. It is in its own panel at its own stated scale (the 1 km bar), a linear scale too, with the line-up’s detectors drawn again beside it at that scale. Nothing on the page uses a logarithmic or a broken scale.'),
      h('li', {}, 'Sizes are overall dimensions as each source states them: some are internal (the DUNE cryostat), some outer (the SK tank), and for a part of a larger instrument (KATRIN’s main spectrometer, the STAR TPC, LZ’s water shield) the part is named. Detectors are not drawn at their depths.'),
    ]),
    h('h3', {}, 'Every dimension and its source'),
    sourceTable,
    h('div', { class: 'ds-method-ice', id: 'ds-method-ice' }),
    skipped.length ? h('h3', {}, 'Not drawn') : null,
    skipped.length ? h('ul', { class: 'ds-method-list' }, skipped.map((row) => h('li', {}, `${row.name}: ${row.reason}.`))) : null,
  );
  loadCitations(el, rows, loader, token, getDestroyed);
}

/** IceCube's part of the method, once its geometry records have loaded. */
function fillIceMethod(el, ice) {
  const holder = el.querySelector('#ds-method-ice');
  if (!holder || !ice || !ice.record) return;
  const spec = (value) => (value ? `${num(value.metres)} m` : null);
  const key = (text) => h('span', { class: 'ds-spec-key' }, text);
  holder.replaceChildren(
    h('h3', {}, 'IceCube’s panel'),
    h('ul', { class: 'ds-method-list' }, [
      h('li', {}, [h('strong', {}, 'Depth range: '), `${spec(ice.depthMin)} to ${spec(ice.depthMax)} (`, key('specs.depth_min, specs.depth_max'), ').']),
      ice.volume ? h('li', {}, [h('strong', {}, 'Instrumented volume: '), ice.volume.display, ' (', key('specs.instrumented_volume'), ').']) : null,
      ice.spacing ? h('li', {}, [h('strong', {}, 'String spacing: '), spec(ice.spacing), ' (', key('specs.string_spacing'), ').']) : null,
      ice.footprint ? h('li', {}, [
        h('strong', {}, 'Footprint and strings: '),
        'from the geometry records geometry:icecube-array-footprint (the convex hull of the 78 standard strings, '
        + `${num(ice.footprint.widthM)} m wide and ${num(ice.footprint.heightM)} m tall in the map’s grid${ice.footprint.areaM2 ? `, ${(ice.footprint.areaM2 / 1e6).toFixed(2)} km²` : ''}; `
        + `its absolute position is good to ±${ice.footprint.accuracyM} m, the strings’ layout relative to each other to far less) and geometry:icecube-strings-1-78 (each string’s plan position). `
        + 'The hull is a computed outline, not a published boundary of the ice: it is about 13 % under the nominal 1 km² because it leaves out the corner sites of the full hexagon.',
      ]) : null,
    ]),
  );
}

async function loadCitations(el, rows, loader, token, getDestroyed) {
  const holders = [...el.querySelectorAll('.ds-cite')];
  try {
    const [prov, sources] = await Promise.all([loader.getProvenance(), loader.getSources()]);
    if (getDestroyed() || token !== methodToken) return;
    for (const row of rows) {
      const claim = ((prov[row.detectorId] || {})[`/specs/${row.spec.key}`]) || null;
      const cite = el.querySelector(`[data-cite="${row.detectorId}|${row.spec.key}"]`);
      const quote = el.querySelector(`[data-quote="${row.detectorId}|${row.spec.key}"]`);
      if (!cite || !quote) continue;
      if (!claim || !(claim.sources || []).length) {
        cite.replaceChildren(h('span', { class: 'error-note' }, 'No source is recorded for this value.'));
        continue;
      }
      const items = claim.sources.map((id) => {
        const src = sources.byId[id];
        return src && src.url
          ? h('a', { href: src.url, target: '_blank', rel: 'noopener' }, src.title || id)
          : h('span', {}, src && src.title ? src.title : id);
      });
      put(cite,
        ...items.flatMap((item, i) => (i ? [h('br'), item] : [item])),
        claim.locator ? h('div', { class: 'ds-locator' }, claim.locator) : null,
        h('div', { class: 'ds-locator' }, `${claim.confidence || 'confidence not recorded'}${claim.verified_at ? `, checked ${claim.verified_at}` : ''}`),
      );
      quote.replaceChildren(claim.quote ? h('q', {}, claim.quote) : '—');
    }
  } catch (error) {
    if (getDestroyed() || token !== methodToken) return;
    for (const holder of holders) {
      const retry = h('button', { type: 'button', class: 'text-btn' }, 'Retry');
      retry.addEventListener('click', () => loadCitations(el, rows, loader, token, getDestroyed));
      holder.replaceChildren(h('span', { class: 'error-note', role: 'alert' }, `Could not load the sources: ${error.message}. `), retry);
    }
  }
}
