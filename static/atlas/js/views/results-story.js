// results-story.js — "Results as a story": the Atlas's results on a timeline, in lanes,
// one lane per physics question.
//
//   #/view/results-story[/<topic-slug>]
//
// Every mark is a result of the Atlas at its date. Its form is the claim the record carries
// (an observation, evidence, a limit, or the neutral mark for anything else); the significance
// the record states is printed in the mark's card as written and never decides the form. A mark
// opens a card with two ways on: the result's own page in the Atlas and its paper. A lane
// header opens its topic. The timeline's year (?y=) draws a band for that year, and the marks
// after it are dimmed; on a phone the lanes stack (header above, strip below) and the strips
// scroll sideways together. Pure arithmetic is results-rows.js; this file only draws. Mounted
// by host.js through registry.js.

import { readableText } from '../tex.js';
import {
  FORMS, WORKING_TITLE, buildLanes, dateText, formCounts, lanesByResult, markForm, paperLink, parseArg,
  resultMoment, shortExperimentName,
} from './results-rows.js';

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
    else if (value !== null && value !== undefined) el.setAttribute(key, String(value));
  }
  for (const child of [].concat(children)) {
    if (child == null) continue;
    el.appendChild(child);
  }
  return el;
}

const words = (text) => String(text || '').replace(/_/g, ' ');
/** Greedy word wrap of a lane's name to `maxChars` characters a line. */
function wrapName(text, maxChars) {
  const lines = [];
  let line = '';
  for (const word of String(text).split(/\s+/)) {
    if (line && `${line} ${word}`.length > maxChars) { lines.push(line); line = word; } else { line = line ? `${line} ${word}` : word; }
  }
  if (line) lines.push(line);
  return lines;
}
const sentenceCase = (text) => { const t = words(text); return t.charAt(0).toUpperCase() + t.slice(1); };
const plural = (n, one, many) => `${n} ${n === 1 ? one : many}`;

/** The shape of a mark, in a 16 by 16 box: filled circle (observation), ring (evidence), down-pointing
 * triangle (limit), small dot (neutral). The shape alone says the form; colour only repeats it. */
function shape(form, size = 16) {
  const svg = s('svg', { class: `rs-shape rs-form-${form}`, width: size, height: size, viewBox: '0 0 16 16', 'aria-hidden': 'true', focusable: 'false' });
  if (form === 'observation') svg.append(s('circle', { class: 'rs-fill', cx: 8, cy: 8, r: 6.6 }));
  else if (form === 'evidence') svg.append(s('circle', { class: 'rs-ring', cx: 8, cy: 8, r: 5.6 }));
  else if (form === 'limit') svg.append(s('path', { class: 'rs-fill', d: 'M2.2,3.4L13.8,3.4L8,13.4Z' }));
  else svg.append(s('circle', { class: 'rs-dot', cx: 8, cy: 8, r: 3 }));
  return svg;
}

// ----------------------------------------------------------------- the strip's layout
const MARK = 24; // a mark's box
const ROW = 26; // a sub-row of a lane
const LABEL_SIZE = 11.5; // the short name beside a mark (views.css .rs-mark-label)

/** The width of a short label in the page's face, plus a few pixels of slack. A character count
 * is not enough: the experiment names are mostly capitals ("MicroBooNE"), wider than the average. */
function labelMeter() {
  const canvas = document.createElement('canvas').getContext('2d');
  canvas.font = `${LABEL_SIZE}px ${window.getComputedStyle(document.body).fontFamily}`;
  return (text) => canvas.measureText(text).width + 6;
}

/** Packs a lane's items (in date order) into sub-rows so no mark covers another, and says how
 * far each mark's row runs clear after it (`next`: the x of the next mark of its row). */
function packLane(items, xOf) {
  const rowEnds = [];
  const placed = items.map((it) => {
    const x = xOf(it.moment.t);
    let row = rowEnds.findIndex((end) => x - end >= MARK);
    if (row < 0) { row = rowEnds.length; rowEnds.push(-Infinity); }
    rowEnds[row] = x;
    return { it, x, row };
  });
  const lastByRow = new Map();
  placed.forEach((p, i) => {
    const prev = lastByRow.get(p.row);
    if (prev !== undefined) placed[prev].next = p.x;
    lastByRow.set(p.row, i);
  });
  return { placed, rowsN: Math.max(1, rowEnds.length) };
}

/** Whether the short label of the mark `p` fits beside it: clear of the next mark of its row, of the
 * strip's end, and of the edges of the timeline's band (a label that ran across a dashed edge would
 * be read through it). Returns the label's left edge, or null when it has no room. */
function labelSpot(p, label, { trackW, padR, band: bandPx, measure }) {
  if (!label) return null;
  const left = p.x + MARK / 2 - 1; // a clear 3 px beyond the mark's own edge
  let right = Math.min(p.next === undefined ? Infinity : p.next - MARK / 2 - 4, trackW + padR - 2);
  if (bandPx) {
    // From a mark left of the band the label must stop before the band; from inside it, before the
    // band's far edge.
    if (p.x < bandPx.left) right = Math.min(right, bandPx.left - 3);
    else if (p.x <= bandPx.right) right = Math.min(right, bandPx.right - 3);
  }
  return right - left >= measure(label) ? left : null;
}

// ------------------------------------------------------------------------ mount
export async function mount(ctx) {
  const { host, atlas, index, loader, navigate } = ctx;
  const scope = parseArg(atlas, ctx.arg);
  if (scope.error) {
    host.fail(scope.error);
    return null;
  }
  let results;
  try {
    results = (await loader.getResults()).list;
  } catch (error) {
    // A failed load is an error, never an empty timeline: a blank lane would read as "nothing happened".
    host.fail(`The results could not be loaded: ${error.message}. Check your connection and retry.`, { retry: () => window.location.reload() });
    return null;
  }
  const model = buildLanes(atlas, results, scope);
  if (!model.lanes.length) {
    host.fail(`No result of the Atlas is filed under “${atlas.topics[scope.topicId].name}”, so there is nothing to draw. That says nothing about the physics: only that the Atlas has recorded no result there.`);
    return null;
  }

  const scopeTopic = scope.kind === 'topic' ? atlas.topics[scope.topicId] : null;
  if (scopeTopic) host.setTitle(`${WORKING_TITLE}: ${scopeTopic.name}`);
  const byResult = lanesByResult(model.lanes);
  const counts = formCounts(model.results);

  // ---- the marks of each lane
  const experimentOf = (r) => {
    const id = (r.experiment_ids || [])[0];
    const record = id && (index.get(id) || (atlas.experiments || {})[id]);
    return record ? shortExperimentName(record) : '';
  };
  const itemsOf = (lane) => lane.results.map((r) => ({
    r,
    id: r.id,
    moment: resultMoment(r),
    form: markForm(r),
    name: readableText(r.name || r.title || r.id),
    experiment: experimentOf(r),
  })).sort((a, b) => (a.moment.t - b.moment.t) || (a.id < b.id ? -1 : 1));
  const laneItems = new Map(model.lanes.map((lane) => [lane.id, itemsOf(lane)]));
  const allItems = [...laneItems.values()].flat();
  const minT = Math.min(...allItems.map((it) => it.moment.t));
  const maxT = Math.max(...allItems.map((it) => it.moment.t));
  const d0 = Math.floor(minT) - 0.5;
  const d1 = Math.ceil(maxT) + 0.25;

  host.setSubtitle(`${plural(model.total, 'result', 'results')} in ${plural(model.lanes.length, 'lane', 'lanes')} · ${Math.floor(minT)}–${Math.floor(maxT)}`);

  const link = (route, text, className = 'entity-link') => {
    const a = h('a', { class: className, href: `#/${route.type}/${route.slug}` }, text);
    a.addEventListener('click', (event) => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      navigate({ entity: route });
    });
    return a;
  };
  const resultRoute = (r) => ({ type: 'result', slug: r.id.split(':')[1] });
  const topicRoute = (topicId) => ({ type: 'topic', slug: topicId.split(':')[1] });

  // ---- the lede and the key
  const lede = h('p', { class: 'rs-lede' }, [
    scopeTopic
      ? `The Atlas’s results filed under ${scopeTopic.name}, by date, one lane to a physics question. `
      : 'The Atlas’s results by date, one lane to a physics question. ',
    'Press a mark for its result and its paper; press a lane’s name for its topic.',
  ]);
  const keyItems = Object.values(FORMS).map((form) => h('li', { class: 'rs-key-item', 'data-form': form.key }, [
    shape(form.key, 20),
    h('span', { class: 'rs-key-text' }, [
      h('strong', {}, `${form.label} (${counts[form.key]})`), h('span', { class: 'rs-key-meaning' }, form.meaning),
    ]),
  ]));
  const example = results.find((r) => r.id === 'result:icecube-galactic-plane-neutrinos-2023');
  const key = h('div', { class: 'rs-key-wrap' }, [
    h('ul', { class: 'rs-key', 'aria-label': 'What the marks mean' }, keyItems),
    h('details', { class: 'rs-key-more' }, [
      h('summary', {}, 'Shape is the claim, not a number'),
      h('p', { class: 'rs-key-note' }, [
        'In particle physics “evidence” conventionally means about 3σ and “observation” about 5σ. The shape here is the claim the paper makes, as the Atlas records it; the significance the paper states is printed in each mark’s card exactly as reported, and it does not choose the shape',
        example && example.significance ? ` (the Galactic-plane “observation” by IceCube is ${readableText(example.significance).replace(/ \(.*$/, '')}).` : '.',
        ' Where a record has no significance the card says so.',
      ]),
    ]),
  ]);

  // ---- where in the list of questions to jump
  const jump = h('details', { class: 'rs-jump' }, [
    h('summary', {}, model.lanes.length > 1 ? 'Jump to a question' : 'The question'),
    h('ul', { class: 'rs-jump-list' }, model.lanes.map((lane) => h('li', {}, h('button', {
      type: 'button', class: 'rs-jump-btn', 'data-lane': lane.id,
    }, `${lane.name} (${lane.results.length})`)))),
  ]);
  const scopeLine = scopeTopic ? h('p', { class: 'rs-scope' }, [
    `Showing ${plural(model.lanes.length, 'lane', 'lanes')} under ${scopeTopic.name}. `,
    link({ type: 'view', slug: 'results-story/all' }, 'Show every question'),
    ' · ', link(topicRoute(scopeTopic.id), `Open the topic ${scopeTopic.name}`),
  ]) : null;

  // ---- the stage
  const scroller = h('div', { class: 'rs-scroll', tabindex: '-1' });
  const canvas = h('div', { class: 'rs-canvas' });
  scroller.append(canvas);
  const card = h('div', { class: 'rs-card', role: 'dialog', 'aria-label': 'Result', hidden: '', tabindex: '-1' });
  const stage = h('div', { class: 'rs-stage' }, [scroller, card]);
  const nowNote = h('p', { class: 'rs-now-note' }, '');
  const status = h('p', { class: 'visually-hidden', role: 'status', 'aria-live': 'polite' }, '');

  // ---- the same marks as a table
  const tableRows = model.results.slice().sort((a, b) => resultMoment(a).t - resultMoment(b).t || (a.id < b.id ? -1 : 1)).map((r) => {
    const lanes = byResult.get(r.id) || [];
    return h('tr', {}, [
      h('td', { class: 'rs-num' }, dateText(r)),
      h('th', { scope: 'row' }, link(resultRoute(r), readableText(r.name || r.title || r.id))),
      h('td', {}, sentenceCase(r.result_type)),
      h('td', {}, r.significance ? readableText(r.significance) : 'not recorded in the Atlas'),
      h('td', {}, lanes.map((lane) => lane.name).join('; ')),
    ]);
  });
  const table = h('details', { class: 'rs-table-details' }, [
    h('summary', {}, `All ${model.total} results as a table`),
    h('div', { class: 'rs-table-scroll' }, h('table', { class: 'rs-table' }, [
      h('caption', {}, 'Every result drawn above, by date, with its type, its significance as the record states it, and its lane'),
      h('thead', {}, h('tr', {}, ['Date', 'Result', 'Type', 'Significance (as reported)', 'Lane'].map((t) => h('th', { scope: 'col' }, t)))),
      h('tbody', {}, tableRows),
    ])),
  ]);

  host.body.append(...[lede, scopeLine, key, jump, nowNote, status, stage, table].filter(Boolean));
  fillMethod(host.method, { model, counts, byResult, atlas, scope });

  // ------------------------------------------------------------ drawing
  let timelineState = ctx.timelineState;
  let selectedId = null;
  let pinned = false;
  let hoverTimer = 0;
  let leaveTimer = 0;
  let frame = 0;
  let lastScroll = 0;
  let didInitialScroll = false;
  let marksById = new Map(); // result id -> [button, ...]
  let laneMarks = new Map(); // lane id -> [button, ...] in date order

  const band = () => {
    const state = timelineState || {};
    if (state.range) return { lo: state.range[0], hi: state.range[1] + 1, label: `${state.range[0]}–${state.range[1]}` };
    if (state.year != null) return { lo: state.year, hi: state.year + 1, label: String(state.year) };
    return null;
  };

  function ariaLabel(it) {
    const sig = it.r.significance ? `, significance as reported: ${readableText(it.r.significance)}` : ', no significance recorded';
    return `${it.name}. ${it.form.key === 'neutral' ? sentenceCase(it.r.result_type) : it.form.label}, ${dateText(it.r)}${sig}. Opens a card with the result and its paper.`;
  }

  function draw() {
    const width = Math.floor(scroller.clientWidth || 0);
    if (width < 240) return;
    const stacked = width < 760;
    const canvasW = stacked ? 940 : width;
    const headW = stacked ? 0 : 210;
    const padL = stacked ? 14 : 8;
    const padR = 22;
    const trackW = canvasW - headW - padL - padR;
    const xOf = (t) => ((t - d0) / (d1 - d0)) * trackW;
    canvas.style.width = `${canvasW}px`;
    canvas.classList.toggle('is-stacked', stacked);
    canvas.style.setProperty('--rs-head-w', `${headW}px`);
    canvas.style.setProperty('--rs-view-w', `${width}px`);
    const b = band();
    const tickEvery = stacked ? 10 : (trackW < 700 ? 10 : 5);
    const ticks = [];
    for (let year = Math.ceil(d0 / tickEvery) * tickEvery; year <= d1; year += tickEvery) ticks.push(year);

    const bandPx = b ? { left: Math.max(0, xOf(b.lo)), right: Math.min(trackW, xOf(b.hi)) } : null;
    const measure = labelMeter();

    const nodes = [];
    marksById = new Map();
    laneMarks = new Map();
    let lastGroup = null;
    for (const lane of model.lanes) {
      if (lane.group !== lastGroup && model.lanes.length > 1) {
        lastGroup = lane.group;
        nodes.push(h('div', { class: 'rs-group', role: 'presentation' }, [
          h('span', { class: 'rs-group-name' }, lane.group),
          h('span', { class: 'rs-axis', 'aria-hidden': 'true', style: `left:${headW + padL}px;width:${trackW}px` }, ticks.map((year) => h('span', {
            class: 'rs-axis-tick', style: `left:${xOf(year).toFixed(1)}px`,
          }, String(year)))),
        ]));
      }
      const items = laneItems.get(lane.id);
      // Pack the marks into sub-rows so none covers another.
      const { placed, rowsN } = packLane(items, xOf);
      const trackH = rowsN * ROW + 12;
      const track = h('div', { class: 'rs-track', style: `height:${trackH}px;width:${trackW}px`, role: 'group', 'aria-label': `${lane.name}: ${plural(items.length, 'result', 'results')}` });
      for (const year of ticks) track.append(h('span', { class: 'rs-grid', 'aria-hidden': 'true', style: `left:${xOf(year).toFixed(1)}px` }));
      if (b) {
        const left = Math.max(0, xOf(b.lo));
        const right = Math.min(trackW, xOf(b.hi));
        if (right > left) track.append(h('span', { class: 'rs-now', 'aria-hidden': 'true', style: `left:${left.toFixed(1)}px;width:${Math.max(2, right - left).toFixed(1)}px` }));
      }
      const buttons = [];
      placed.forEach((p, i) => {
        const { it } = p;
        const later = b && it.moment.t >= b.hi;
        const earlier = b && b.lo > d0 && it.moment.t < b.lo && !!(timelineState && timelineState.range);
        const button = h('button', {
          type: 'button',
          class: `rs-mark rs-form-${it.form.key}${later || earlier ? ' is-later' : ''}${it.moment.precision === 'year' ? ' is-year' : ''}`,
          'data-id': it.id,
          'data-lane': lane.id,
          'aria-label': ariaLabel(it),
          'aria-expanded': 'false',
          tabindex: i === 0 ? '0' : '-1',
          style: `left:${(p.x - MARK / 2).toFixed(1)}px;top:${6 + p.row * ROW - 1}px`,
        }, shape(it.form.key));
        buttons.push(button);
        track.append(button);
        const labelLeft = labelSpot(p, it.experiment, { trackW, padR, band: bandPx, measure });
        if (labelLeft !== null) {
          track.append(h('span', {
            class: `rs-mark-label${later || earlier ? ' is-later' : ''}`, 'aria-hidden': 'true',
            style: `left:${labelLeft.toFixed(1)}px;top:${6 + p.row * ROW + 3}px`,
          }, it.experiment));
        }
        if (!marksById.has(it.id)) marksById.set(it.id, []);
        marksById.get(it.id).push(button);
      });
      laneMarks.set(lane.id, buttons);

      const head = h('h3', { class: 'rs-lane-head' }, [
        lane.topicId && lane.id !== 'lane:other' ? link(topicRoute(lane.topicId), lane.name, 'rs-lane-link') : h('span', { class: 'rs-lane-link' }, lane.name),
        h('span', { class: 'rs-lane-count' }, plural(items.length, 'result', 'results')),
      ]);
      nodes.push(h('section', { class: 'rs-lane', 'data-lane': lane.id, 'aria-label': lane.name }, [head, track]));
    }
    canvas.replaceChildren(...nodes);
    nowNote.textContent = `${stacked ? 'Drag the strips sideways to move through the years. ' : ''}${b
      ? `The shaded band is ${timelineState && timelineState.range ? 'the timeline’s range' : 'the timeline’s year'}, ${b.label}; results after it are dimmed. Change it with the timeline below.`
      : ''}`;
    if (stacked && !didInitialScroll) {
      // The strips open on the stretch where most results are, not on the empty years before them.
      didInitialScroll = true;
      const times = allItems.map((it) => it.moment.t).sort((a, c) => a - c);
      const median = times[Math.floor(times.length / 2)];
      scroller.scrollLeft = Math.max(0, headW + padL + xOf(median) - width * 0.6);
      lastScroll = scroller.scrollLeft;
    }
    if (selectedId && marksById.has(selectedId)) {
      const mark = marksById.get(selectedId)[0];
      setSelected(selectedId, mark, { keepOpen: !card.hidden });
    }
  }

  // ---- "Export image": the lanes as one SVG made for the picture (the page's own timeline is HTML)
  function exportFigure() {
    const W = 1500;
    const headW = 224;
    const padL = 8;
    const padR = 22;
    const x0 = headW + padL;
    const trackW = W - x0 - padR;
    const xOf = (t) => ((t - d0) / (d1 - d0)) * trackW;
    const b = band();
    const bandPx = b ? { left: Math.max(0, xOf(b.lo)), right: Math.min(trackW, xOf(b.hi)) } : null;
    const measure = labelMeter();
    const ticks = [];
    for (let year = Math.ceil(d0 / 5) * 5; year <= d1; year += 5) ticks.push(year);
    const svg = s('svg', { class: 'rs-fig', width: W, role: 'img', 'aria-hidden': 'true', focusable: 'false' });
    const rule = (yy, strong) => s('line', { class: `rs-fig-rule${strong ? ' is-strong' : ''}`, x1: 0, x2: W, y1: yy, y2: yy });
    const text = (cls, x, y, value, anchor) => {
      const node = s('text', { class: cls, x: x.toFixed(1), y: y.toFixed(1), 'text-anchor': anchor || null });
      node.textContent = value;
      return node;
    };
    const put = (node) => { svg.append(node); return node; };

    // The key: the four shapes and what each says.
    let y = 8;
    let kx = 12;
    for (const form of Object.values(FORMS)) {
      const mark = shape(form.key, 18);
      mark.setAttribute('x', String(kx));
      mark.setAttribute('y', String(y));
      put(mark);
      const label = `${form.label} (${counts[form.key]})`;
      put(text('rs-fig-key', kx + 26, y + 14, label));
      kx += 26 + labelMeter()(label) * 1.12 + 26;
    }
    y += 34;

    let lastGroup = null;
    for (const lane of model.lanes) {
      if (lane.group !== lastGroup && model.lanes.length > 1) {
        lastGroup = lane.group;
        put(rule(y, true));
        put(text('rs-fig-group', 12, y + 20, lane.group.toUpperCase()));
        // The year labels start after the group's name (a long name runs under the first of them).
        const nameEnd = 12 + lane.group.length * 9.2 + 16;
        for (const year of ticks) if (x0 + xOf(year) - 14 > nameEnd) put(text('rs-fig-tick', x0 + xOf(year), y + 20, String(year), 'middle'));
        y += 30;
      }
      const { placed, rowsN } = packLane(laneItems.get(lane.id), xOf);
      const nameLines = wrapName(lane.name, 27);
      const headH = 14 + nameLines.length * 16 + 22;
      const trackH = rowsN * ROW + 12;
      const laneH = Math.max(headH, trackH);
      const top = y + (laneH - trackH) / 2;
      put(rule(y));
      nameLines.forEach((line, i) => put(text('rs-fig-lane', 12, y + 22 + i * 16, line)));
      put(text('rs-fig-count', 12, y + 22 + nameLines.length * 16, plural(placed.length, 'result', 'results')));
      for (const year of ticks) put(s('line', { class: 'rs-fig-grid', x1: (x0 + xOf(year)).toFixed(1), x2: (x0 + xOf(year)).toFixed(1), y1: y, y2: y + laneH }));
      if (bandPx && bandPx.right > bandPx.left) {
        put(s('rect', { class: 'rs-fig-now', x: (x0 + bandPx.left).toFixed(1), y, width: Math.max(2, bandPx.right - bandPx.left).toFixed(1), height: laneH }));
      }
      for (const p of placed) {
        const dim = b && (p.it.moment.t >= b.hi || (b.lo > d0 && p.it.moment.t < b.lo && !!(timelineState && timelineState.range)));
        const mark = shape(p.it.form.key, 16);
        mark.setAttribute('x', (x0 + p.x - 8).toFixed(1));
        mark.setAttribute('y', (top + 9 + p.row * ROW).toFixed(1));
        if (dim) mark.setAttribute('class', `${mark.getAttribute('class')} rs-fig-later`);
        put(mark);
        const labelLeft = labelSpot(p, p.it.experiment, { trackW, padR, band: bandPx, measure });
        if (labelLeft !== null) {
          put(text(`rs-fig-label${dim ? ' rs-fig-later' : ''}`, x0 + labelLeft, top + 6 + p.row * ROW + 16.5, p.it.experiment));
        }
      }
      y += laneH;
    }
    put(rule(y));
    y += 8;
    svg.setAttribute('height', String(Math.ceil(y)));
    svg.setAttribute('viewBox', `0 0 ${W} ${Math.ceil(y)}`);
    const holder = h('div', { class: 'export-holder', 'aria-hidden': 'true' }, svg);
    document.body.append(holder);
    const notes = [];
    if (b) notes.push(`The shaded band is the timeline’s ${timelineState && timelineState.range ? 'range' : 'year'}, ${b.label}; results after it are dimmed.`);
    notes.push('A mark’s shape is the claim its paper makes, not a measured significance; a gap in a lane is a gap in what the Atlas has sourced.');
    return { figures: [svg], layout: 'column', notes, release: () => holder.remove() };
  }
  host.setExporter(exportFigure);

  // ------------------------------------------------------------ the card
  const itemOf = (id) => allItems.find((it) => it.id === id);

  function fillCard(it) {
    const r = it.r;
    const paper = paperLink(r);
    const lanes = byResult.get(r.id) || [];
    const kind = r.date_kind ? ` (${words(r.date_kind)} date)` : '';
    const precision = it.moment.precision === 'year' ? ' The record gives the year only; the mark sits at mid-year.' : (it.moment.precision === 'month' ? ' The record gives the month only; the mark sits mid-month.' : '');
    const experiments = (r.experiment_ids || []).map((id) => {
      const record = index.get(id) || (atlas.experiments || {})[id];
      return record ? link({ type: 'experiment', slug: id.split(':')[1] }, record.name) : null;
    }).filter(Boolean);
    const closeBtn = h('button', { type: 'button', class: 'rs-card-close', 'aria-label': 'Close' }, '×');
    closeBtn.addEventListener('click', () => closeCard(true));
    const resultLink = link(resultRoute(r), 'Open the result', 'rs-btn rs-btn-primary');
    const actions = h('div', { class: 'rs-card-actions' }, [
      resultLink,
      paper
        ? h('a', { class: 'rs-btn', href: paper.href, target: '_blank', rel: 'noopener' }, `Open the paper · ${paper.label}`)
        : h('span', { class: 'rs-card-nopaper' }, 'No paper link is recorded for this result.'),
    ]);
    card.replaceChildren(...[
      closeBtn,
      h('p', { class: 'rs-card-kicker' }, [
        shape(it.form.key, 18),
        ` ${it.form.key === 'neutral' ? sentenceCase(r.result_type) : it.form.label} · ${dateText(r)}${kind}`,
      ]),
      h('h4', { class: 'rs-card-title' }, it.name),
      h('p', { class: 'rs-card-sig' }, r.significance
        ? [h('strong', {}, 'Significance, as reported: '), readableText(r.significance)]
        : [h('strong', {}, 'Significance: '), 'no significance is recorded in the Atlas for this result.']),
      experiments.length ? h('p', { class: 'rs-card-meta' }, ['Experiment: ', ...experiments.flatMap((a, i) => (i ? [', ', a] : [a]))]) : null,
      lanes.length > 1 ? h('p', { class: 'rs-card-meta' }, `Also in: ${lanes.map((lane) => lane.name).join('; ')}.`) : null,
      precision ? h('p', { class: 'rs-card-meta' }, precision.trim()) : null,
      actions,
    ].filter(Boolean));
    card.setAttribute('aria-label', `${it.name}: result card`);
  }

  function placeCard(mark) {
    const box = stage.getBoundingClientRect();
    const m = mark.getBoundingClientRect();
    card.hidden = false;
    const cw = Math.min(340, box.width - 16);
    card.style.width = `${cw}px`;
    let left = m.left - box.left + m.width / 2 - cw / 2;
    left = Math.max(8, Math.min(box.width - cw - 8, left));
    card.style.left = `${left}px`;
    const ch = card.offsetHeight;
    let top = m.bottom - box.top + 8;
    // Above the mark when the card would run past the foot of the screen (the bars below the page take ~110 px).
    if (m.bottom + 8 + ch > window.innerHeight - 110 && m.top - 8 - ch > 60) top = m.top - box.top - ch - 8;
    card.style.top = `${top}px`;
  }

  function setSelected(id, mark, { keepOpen = false } = {}) {
    for (const buttons of marksById.values()) {
      for (const button of buttons) {
        button.classList.toggle('is-selected', button.dataset.id === id && button === mark);
        button.classList.toggle('is-twin', button.dataset.id === id && button !== mark);
        button.setAttribute('aria-expanded', button === mark && keepOpen ? 'true' : 'false');
      }
    }
    selectedId = id;
  }

  function openCard(mark, { focus = false, pin = false } = {}) {
    const it = itemOf(mark.dataset.id);
    if (!it) return;
    window.clearTimeout(hoverTimer);
    window.clearTimeout(leaveTimer);
    fillCard(it);
    pinned = pinned || pin;
    card.dataset.mark = `${mark.dataset.lane}|${mark.dataset.id}`;
    setSelected(it.id, mark, { keepOpen: true });
    card.hidden = false;
    placeCard(mark);
    status.textContent = `${it.name}. ${it.form.label}, ${dateText(it.r)}.`;
    if (focus) {
      const first = card.querySelector('.rs-btn');
      if (first) first.focus({ preventScroll: true });
    }
  }

  function closeCard(returnFocus = false) {
    window.clearTimeout(hoverTimer);
    window.clearTimeout(leaveTimer);
    const open = card.dataset.mark;
    card.hidden = true;
    pinned = false;
    card.dataset.mark = '';
    for (const buttons of marksById.values()) for (const button of buttons) button.setAttribute('aria-expanded', 'false');
    if (returnFocus && open) {
      const [laneId, id] = open.split('|');
      const mark = (laneMarks.get(laneId) || []).find((button) => button.dataset.id === id);
      if (mark) mark.focus({ preventScroll: true });
    }
  }

  const markOf = (event) => event.target.closest && event.target.closest('.rs-mark');

  canvas.addEventListener('click', (event) => {
    const mark = markOf(event);
    if (!mark) return;
    // detail 0 is a keyboard activation: the reader goes on into the card; a pointer stays where it is.
    const same = !card.hidden && card.dataset.mark === `${mark.dataset.lane}|${mark.dataset.id}` && pinned;
    if (same) { closeCard(true); return; }
    openCard(mark, { focus: event.detail === 0, pin: true });
  });
  canvas.addEventListener('pointerover', (event) => {
    const mark = markOf(event);
    if (!mark || event.pointerType !== 'mouse' || pinned) return;
    window.clearTimeout(leaveTimer);
    window.clearTimeout(hoverTimer);
    hoverTimer = window.setTimeout(() => openCard(mark), 110);
  });
  canvas.addEventListener('pointerout', (event) => {
    if (event.pointerType !== 'mouse' || pinned) return;
    if (!markOf(event)) return;
    window.clearTimeout(hoverTimer);
    leaveTimer = window.setTimeout(() => { if (!pinned && !card.matches(':hover')) closeCard(); }, 260);
  });
  card.addEventListener('pointerleave', (event) => {
    if (event.pointerType !== 'mouse' || pinned) return;
    leaveTimer = window.setTimeout(() => { if (!pinned) closeCard(); }, 260);
  });
  // Arrow keys walk along a lane (one tab stop per lane), Home and End jump to its ends.
  canvas.addEventListener('keydown', (event) => {
    const mark = markOf(event);
    if (!mark) return;
    if (event.key === 'Escape' && !card.hidden) {
      event.stopPropagation();
      closeCard(true);
      return;
    }
    const buttons = laneMarks.get(mark.dataset.lane) || [];
    const at = buttons.indexOf(mark);
    const target = {
      ArrowRight: buttons[at + 1], ArrowDown: buttons[at + 1], ArrowLeft: buttons[at - 1], ArrowUp: buttons[at - 1],
      Home: buttons[0], End: buttons[buttons.length - 1],
    }[event.key];
    if (!target) return;
    event.preventDefault();
    for (const button of buttons) button.tabIndex = button === target ? 0 : -1;
    target.focus();
  });
  card.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    event.stopPropagation();
    closeCard(true);
  });
  const onDocumentPointerDown = (event) => {
    if (card.hidden || card.contains(event.target) || markOf(event)) return;
    closeCard();
  };
  document.addEventListener('pointerdown', onDocumentPointerDown);

  jump.addEventListener('click', (event) => {
    const button = event.target.closest('.rs-jump-btn');
    if (!button) return;
    const lane = canvas.querySelector(`.rs-lane[data-lane="${CSS.escape(button.dataset.lane)}"]`);
    if (lane) {
      lane.scrollIntoView({ block: 'start', behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
      const first = (laneMarks.get(button.dataset.lane) || [])[0];
      if (first) first.focus({ preventScroll: true });
    }
  });

  // The card belongs to a mark's place on the stage: when the strips scroll sideways, it closes.
  scroller.addEventListener('scroll', () => { if (!card.hidden && scroller.scrollLeft !== lastScroll) closeCard(); lastScroll = scroller.scrollLeft; });
  const redraw = () => {
    window.cancelAnimationFrame(frame);
    frame = window.requestAnimationFrame(draw);
  };
  let observer = null;
  if (typeof ResizeObserver !== 'undefined') {
    observer = new ResizeObserver(redraw);
    observer.observe(scroller);
  }
  draw();
  window.requestAnimationFrame(draw);

  host.announce(`${WORKING_TITLE}: ${plural(model.total, 'result', 'results')} in ${plural(model.lanes.length, 'lane', 'lanes')}.`);

  return {
    update(next) {
      // Only the timeline's year or range moved: redraw the band and dim what comes after it.
      timelineState = next.timelineState;
      draw();
    },
    destroy() {
      window.cancelAnimationFrame(frame);
      window.clearTimeout(hoverTimer);
      window.clearTimeout(leaveTimer);
      document.removeEventListener('pointerdown', onDocumentPointerDown);
      if (observer) observer.disconnect();
    },
  };
}

// ----------------------------------------------------------- the method disclosure
function fillMethod(el, { model, counts, byResult, atlas, scope }) {
  const laneRows = model.lanes.map((lane) => h('tr', {}, [
    h('th', { scope: 'row' }, lane.name),
    h('td', {}, lane.topicId && lane.id !== 'lane:other' ? lane.topicId : 'results under none of the lanes above'),
    h('td', { class: 'rs-num' }, String(lane.results.length)),
  ]));
  const inMore = [...byResult.values()].filter((lanes) => lanes.length > 1).length;
  const claimed = model.results.filter((r) => ['observation', 'evidence'].includes(markForm(r).key));
  const claimedNoSig = claimed.filter((r) => !r.significance).length;
  const withSig = model.results.filter((r) => r.significance).length;
  el.replaceChildren(
    h('p', { class: 'bs-method-intro' }, [
      'Nothing on this page is computed from the physics. It draws the Atlas’s own result records (their date, type, significance, paper and topics) and groups them by topic. ',
      'A gap in a lane is a gap in what the Atlas has sourced, not evidence that nothing happened there.',
    ]),
    h('h3', {}, 'Inputs'),
    h('p', {}, `${model.total} results of the Atlas${scope.kind === 'topic' ? ` filed under ${atlas.topics[scope.topicId].name}` : ''}, each from its record in the results bundle: date, date kind, result type, significance, publication and topics.`),
    h('h3', {}, 'Lanes'),
    h('ul', { class: 'bs-method-list' }, [
      h('li', {}, 'A lane is an Atlas topic, a physics question. The list of lanes is an editorial choice, fixed in the code (views/results-rows.js); which results stand in a lane is not: a result stands in a lane when its record is filed under that topic or under a topic below it.'),
      h('li', {}, `${inMore} of the ${model.total} results answer more than one question and stand in more than one lane; the card of such a mark says so, and selecting it rings its copies.`),
      h('li', {}, 'Results filed under no lane topic are drawn in the last lane, so none is dropped.'),
    ]),
    h('div', { class: 'rs-table-scroll' }, h('table', { class: 'rs-table' }, [
      h('caption', {}, 'The lanes drawn'),
      h('thead', {}, h('tr', {}, ['Lane', 'Topic', 'Results'].map((t) => h('th', { scope: 'col' }, t)))),
      h('tbody', {}, laneRows),
    ])),
    h('h3', {}, 'Dates'),
    h('p', {}, 'Each mark sits at the record’s date. That date is the date of a preprint, an announcement or a publication (its card says which), so two marks on the same day may not be the same kind of date. A date given to the year or to the month is drawn at mid-year or mid-month, and its card says so.'),
    h('h3', {}, 'Marks'),
    h('ul', { class: 'bs-method-list' }, [
      h('li', {}, `The form is the result’s type: an observation (including a discovery or a first detection), evidence, a limit, or the neutral mark for everything else. This is the claim the record carries, and for observation and evidence the Atlas’s validator checks the type against the wording of the paper’s own claim. Here: ${counts.observation} observation, ${counts.evidence} evidence, ${counts.limit} limit, ${counts.neutral} neutral.`),
      h('li', {}, `The significance is a sourced string kept exactly as the paper reports it. It is printed in the card and is never parsed, converted or used to pick a shape. ${withSig} of the ${model.total} results here carry one; ${claimedNoSig} of the ${claimed.length} marked observation or evidence do not, and say “no significance is recorded in the Atlas”, which is not a statement that the paper gives none.`),
      h('li', {}, 'The conventions of about 3σ for evidence and about 5σ for observation are shown to explain the words. They are not applied: a paper’s own wording decides the shape, so a mark can disagree with the convention and the card shows both.'),
    ]),
    h('h3', {}, 'The “now” band'),
    h('p', {}, 'The timeline’s year (or range) at the foot of the page is drawn as a band, and results after it are dimmed. Change the year with the timeline and the band moves; nothing else on the page changes.'),
  );
}
