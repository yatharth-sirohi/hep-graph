// limits.js — "WIMP exclusion plot": the published limits on the spin-independent
// WIMP–nucleon cross section, against WIMP mass, on logarithmic axes.
//
//   #/view/limits/<plot-slug>        today: wimp-si
//
// What is drawn is data, never computed here: every curve is a table fetched from
// HEPData (CC0) and stored in data/atlas/limits/<slug>.json (A29), served as
// limits/<plot>.json. A curve is the points of the table's limit column joined by
// straight segments; nothing is smoothed, fitted or interpolated. A paper with no
// HEPData table is drawn as the single minimum its abstract publishes, as a hollow
// diamond that says so. Every curve is cited under the figure (record, table, DOI,
// arXiv id, confidence level, the exact columns and units), and the figure's numbers
// are in tables. Mounted by host.js through registry.js.

import { readableText } from '../tex.js';
import { PLOTS, WORKING_TITLE, plotFor } from './limits-rows.js';

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

const SUPERSCRIPT = { 0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹', '-': '⁻' };
const sup = (n) => String(n).replace('−', '-').split('').map((c) => SUPERSCRIPT[c] || c).join('');

/** 2.18 × 10⁻⁴⁸ (three significant figures by default), the way a physicist writes it. */
function sci(value, digits = 3) {
  const [mantissa, exponent] = Number(value).toExponential(digits - 1).split('e');
  return `${mantissa} × 10${sup(Number(exponent))}`;
}

/** A mass in GeV/c²: "40", "1 000", "10 000" (a thin space between thousands). */
function massText(value) {
  const rounded = Number(value) >= 100 ? Math.round(value) : Number(Number(value).toPrecision(3));
  return String(rounded).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
}

const UNIT_TEXT = { 'GeV/c^2': 'GeV/c²', 'cm^2': 'cm²' };
const unitText = (unit) => UNIT_TEXT[unit] || unit;

let uid = 0;

// ------------------------------------------------------------------- the model
/** The bundle's rows as the figure draws them: a series per curve or marker, in the bundle's order. */
function buildModel(bundle) {
  const series = bundle.curves.map((row, index) => {
    const isMarker = row.type === 'limit_marker';
    const points = isMarker ? [[row.point.x, row.point.y]] : row.points;
    let lowest = points[0];
    for (const point of points) if (point[1] < lowest[1]) lowest = point;
    return {
      row, index, isMarker, points, lowest, slug: row.slug, label: row.label,
      short: row.short_label || row.label, className: `lm-s${index % 6}`,
    };
  });
  const xs = series.flatMap((one) => one.points.map((p) => p[0]));
  const ys = series.flatMap((one) => one.points.map((p) => p[1]));
  // Quarter-decade bounds in mass that hold every point with room at both ends; whole decades in cross section.
  const x0 = 10 ** (Math.floor((Math.log10(Math.min(...xs)) - 0.02) * 4) / 4);
  const x1 = 10 ** (Math.ceil((Math.log10(Math.max(...xs)) + 0.05) * 4) / 4);
  const y0 = 10 ** Math.floor(Math.log10(Math.min(...ys)));
  const y1 = 10 ** Math.ceil(Math.log10(Math.max(...ys)));
  return { series, domain: { x0, x1, y0, y1 } };
}

// ------------------------------------------------------------------- the figure
function drawPlot(model, bundle, width) {
  const { domain } = model;
  const id = `lm${++uid}`;
  const compact = width < 560;
  const margin = { left: compact ? 56 : 74, right: compact ? 10 : 18, top: 14, bottom: compact ? 48 : 54 };
  const W = width;
  const H = compact ? 400 : 500;
  const pw = W - margin.left - margin.right;
  const ph = H - margin.top - margin.bottom;
  const lx = (v) => margin.left + ((Math.log10(v) - Math.log10(domain.x0)) / (Math.log10(domain.x1) - Math.log10(domain.x0))) * pw;
  const ly = (v) => margin.top + ph - ((Math.log10(v) - Math.log10(domain.y0)) / (Math.log10(domain.y1) - Math.log10(domain.y0))) * ph;
  const xUnit = unitText(bundle.x.unit);
  const yUnit = unitText(bundle.y.unit);
  const fx = (v) => v.toFixed(1);

  const svg = s('svg', {
    class: 'lm-svg', viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: 'img',
    'aria-labelledby': `${id}-t ${id}-d`, focusable: 'false',
  });
  const curveNames = model.series.filter((one) => !one.isMarker).map((one) => one.label).join('; ');
  const markerNames = model.series.filter((one) => one.isMarker).map((one) => one.label).join('; ');
  svg.append(
    s('title', { id: `${id}-t` }, bundle.title),
    s('desc', { id: `${id}-d` },
      `A log–log plot. The horizontal axis is ${bundle.x.label.toLowerCase()} in ${xUnit}, from ${massText(domain.x0)} to ${massText(domain.x1)}; `
      + `the vertical axis is the ${bundle.y.label.toLowerCase()} in ${yUnit}, from ${sci(domain.y0, 1)} to ${sci(domain.y1, 1)}. `
      + `Each line is the 90% confidence-level upper limit published for one result (${curveNames}); the region above a line is excluded. `
      + (markerNames ? `Hollow diamonds mark the one published minimum of a result whose curve is not in HEPData (${markerNames}). ` : '')
      + 'The same numbers are in the tables under the figure.'),
  );
  const clipId = `${id}-clip`;
  svg.append(s('defs', {}, s('clipPath', { id: clipId }, s('rect', { x: margin.left, y: margin.top, width: pw, height: ph }))));

  // ---- grid and axes
  const grid = s('g', { class: 'lm-grid' });
  const axes = s('g', { class: 'lm-axes' });
  for (let e = Math.ceil(Math.log10(domain.x0)); e <= Math.floor(Math.log10(domain.x1)); e += 1) {
    const x = lx(10 ** e);
    grid.append(s('line', { class: 'lm-gridline', x1: fx(x), x2: fx(x), y1: margin.top, y2: margin.top + ph }));
    axes.append(s('text', { class: 'lm-tick', x: fx(x), y: margin.top + ph + 18, 'text-anchor': 'middle', text: e === 0 ? '1' : e === 1 ? '10' : `10${sup(e)}` }));
  }
  for (let e = Math.floor(Math.log10(domain.x0)); e <= Math.floor(Math.log10(domain.x1)); e += 1) {
    for (let m = 2; m <= 9; m += 1) {
      const v = m * 10 ** e;
      if (v > domain.x0 && v < domain.x1) {
        const xm = lx(v);
        grid.append(s('line', { class: 'lm-minor', x1: fx(xm), x2: fx(xm), y1: margin.top + ph, y2: margin.top + ph - 5 }));
      }
    }
  }
  const lowY = Math.round(Math.log10(domain.y0));
  const highY = Math.round(Math.log10(domain.y1));
  const yStep = highY - lowY > 7 ? 2 : 1;
  for (let e = lowY; e <= highY; e += 1) {
    const y = ly(10 ** e);
    grid.append(s('line', { class: 'lm-gridline', x1: margin.left, x2: margin.left + pw, y1: fx(y), y2: fx(y) }));
    if ((e - lowY) % yStep === 0) axes.append(s('text', { class: 'lm-tick', x: margin.left - 8, y: fx(y + 4), 'text-anchor': 'end', text: `10${sup(e)}` }));
  }
  axes.append(
    s('rect', { class: 'lm-frame', x: margin.left, y: margin.top, width: pw, height: ph }),
    s('text', { class: 'lm-axis-title', x: fx(margin.left + pw / 2), y: H - 10, 'text-anchor': 'middle', text: `${bundle.x.label} (${xUnit})` }),
    s('text', {
      class: 'lm-axis-title', transform: `translate(14 ${fx(margin.top + ph / 2)}) rotate(-90)`, 'text-anchor': 'middle',
      text: compact ? `SI cross section (${yUnit})` : `${bundle.y.label} (${yUnit})`,
    }),
  );
  svg.append(grid, axes);

  // ---- the series
  const layer = s('g', { class: 'lm-layer', 'clip-path': `url(#${clipId})` });
  const labels = s('g', { class: 'lm-labels' });
  const hit = []; // every drawn point in pixels, for the read-out
  for (const one of model.series) {
    const g = s('g', { class: `lm-series ${one.className}${one.isMarker ? ' is-marker' : ''}`, 'data-slug': one.slug });
    const px = one.points.map(([x, y]) => [lx(x), ly(y)]);
    if (!one.isMarker) {
      const line = px.map(([x, y], i) => `${i ? 'L' : 'M'}${fx(x)},${fx(y)}`).join('');
      // The region above the line is what the result excludes.
      g.append(
        s('path', { class: 'lm-excluded', d: `${line}L${fx(px[px.length - 1][0])},${margin.top}L${fx(px[0][0])},${margin.top}Z` }),
        s('path', { class: 'lm-line', d: line }),
      );
      for (const [x, y] of px) g.append(s('circle', { class: 'lm-dot', cx: fx(x), cy: fx(y), r: compact ? 2.4 : 3 }));
      g.append(s('circle', { class: 'lm-min-ring', cx: fx(lx(one.lowest[0])), cy: fx(ly(one.lowest[1])), r: 8 }));
    } else {
      const [x, y] = px[0];
      const r = compact ? 6 : 7;
      g.append(s('path', { class: 'lm-diamond', d: `M${fx(x)},${fx(y - r)}L${fx(x + r)},${fx(y)}L${fx(x)},${fx(y + r)}L${fx(x - r)},${fx(y)}Z` }));
    }
    layer.append(g);
    one.points.forEach((point, i) => hit.push({ one, point, px: px[i][0], py: px[i][1] }));
  }
  svg.append(layer);

  // ---- direct labels: at the line end for a curve, beside the diamond for a marker
  for (const one of model.series) {
    const text = one.short;
    if (one.isMarker) {
      const [x, y] = [lx(one.points[0][0]), ly(one.points[0][1])];
      labels.append(s('text', { class: `lm-label ${one.className}`, x: fx(x + 12), y: fx(y + 4), 'text-anchor': 'start', 'data-slug': one.slug, text }));
    } else {
      const last = one.points[one.points.length - 1];
      labels.append(s('text', { class: `lm-label ${one.className}`, x: fx(margin.left + pw - 6), y: fx(ly(last[1]) - 11), 'text-anchor': 'end', 'data-slug': one.slug, text }));
    }
  }
  svg.append(labels);
  svg.append(s('text', { class: 'lm-region-note', x: margin.left + 10, y: margin.top + 20, text: 'Excluded at 90% CL: the region above each line' }));

  // ---- the read-out target
  const cross = s('g', { class: 'lm-cross', visibility: 'hidden' }, s('circle', { class: 'lm-cross-ring', r: 10, cx: 0, cy: 0 }));
  svg.append(cross);
  const overlay = s('rect', { class: 'lm-overlay', x: margin.left, y: margin.top, width: pw, height: ph, fill: 'transparent' });
  svg.append(overlay);
  return { svg, hit, cross, overlay, width, height: H };
}

// ---------------------------------------------------------------------- mount
export async function mount(ctx) {
  const { host, loader } = ctx;
  const plot = plotFor(ctx.arg);
  if (!plot) {
    host.fail(`The Atlas has no exclusion plot called “${ctx.arg}”. The plot it has is “${PLOTS['wimp-si'].slug}”.`);
    return null;
  }
  let bundle;
  try {
    bundle = await loader.getLimits(plot.slug);
  } catch (error) {
    // A missing or failed bundle is an error, never an empty plot: nothing drawn must read as "no limits".
    host.fail(`The limits could not be loaded: ${error.message}. Check your connection and retry.`, {
      retry: () => window.location.reload(),
    });
    return null;
  }
  if (!bundle || !Array.isArray(bundle.curves) || !bundle.curves.length) {
    host.fail('This plot has no curves in the Atlas data, so there is nothing to draw.');
    return null;
  }
  // Every point must be a finite number in the plot's units, or the figure would lie.
  for (const row of bundle.curves) {
    const points = row.type === 'limit_marker' ? [[row.point.x, row.point.y]] : row.points;
    const unitsOk = row.columns && row.columns.x.unit === bundle.x.unit && row.columns.y.unit === bundle.y.unit;
    if (!unitsOk || points.some((p) => !(Number.isFinite(p[0]) && Number.isFinite(p[1]) && p[0] > 0 && p[1] > 0))) {
      host.fail(`The data of “${row.label}” is not made of finite positive numbers in ${unitText(bundle.x.unit)} and ${unitText(bundle.y.unit)}, so the plot is not drawn.`);
      return null;
    }
  }

  const model = buildModel(bundle);
  const link = (route, text) => {
    const a = h('a', { class: 'entity-link', href: `#/${route.type}/${route.slug}` }, text);
    a.addEventListener('click', (event) => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      ctx.navigate({ entity: route });
    });
    return a;
  };
  const external = (href, text) => h('a', { href, target: '_blank', rel: 'noopener' }, text);
  const recordRoute = (id) => ({ type: id.split(':')[0], slug: id.split(':')[1] });
  // Results live in their own (already fetched) bundle, not in atlas.json: a name that cannot be
  // found is shown as its id, never as a blank.
  let resultsById = new Map();
  try {
    resultsById = (await loader.getResults()).byId;
  } catch (error) {
    window.console.error(error);
  }
  const nameOf = (id) => {
    const record = ctx.index.get(id) || resultsById.get(id);
    return record ? readableText(record.name || record.title || id) : id;
  };
  const swatchOf = (one, width = 30) => s('svg', {
    class: `lm-swatch ${one.className}`, width, height: 14, viewBox: '0 0 30 14', 'aria-hidden': 'true', focusable: 'false',
  }, one.isMarker
    ? s('path', { class: 'lm-diamond', d: 'M15,1L22,7L15,13L8,7Z' })
    : [s('path', { class: 'lm-line', d: 'M1,7L29,7' }), s('circle', { class: 'lm-dot', cx: 15, cy: 7, r: 3 })]);

  host.setSubtitle(bundle.title);

  // ---- the lede
  const lede = h('p', { class: 'lm-lede' }, [
    'A dark-matter detector that sees nothing rules out some WIMPs: at each WIMP mass, a particle whose cross section on a nucleon is ',
    h('strong', {}, 'above'), ' the line would have left more events than the detector recorded, so it is excluded (at 90% confidence). ',
    'Lower is more sensitive. The lines are the numbers the collaborations published; nothing here is fitted or smoothed.',
  ]);

  // ---- the legend (also the way to pick one series out of the others)
  const legend = h('div', { class: 'lm-legend', role: 'group', 'aria-label': 'Curves: press one to pick it out' },
    model.series.map((one) => h('button', { type: 'button', class: 'lm-chip', 'aria-pressed': 'false', 'data-slug': one.slug }, [
      swatchOf(one), h('span', { class: 'lm-chip-label' }, one.label),
    ])));
  const plotWrap = h('div', { class: 'lm-plot' });
  const readout = h('p', { class: 'lm-readout' }, 'Move over the plot, or tap it, to read the nearest point.');
  const figure = h('figure', { class: 'lm-figure' }, [
    legend, plotWrap, readout,
    h('figcaption', { class: 'lm-caption' }, [
      h('strong', {}, 'How to read it. '),
      'Both axes are logarithmic. The region above a line is excluded at 90% confidence by that result; a lower curve excludes more. ',
      'Hollow diamonds are not curves: each marks the one minimum a paper states in its abstract, for papers whose limit curve is not on HEPData.',
    ]),
  ]);

  // ---- the lowest point of each series
  const stats = h('dl', { class: 'lm-stats' }, model.series.map((one) => h('div', { class: `lm-stat ${one.className}` }, [
    h('dt', {}, one.isMarker ? one.label : `${one.label}: lowest point`),
    h('dd', {}, [
      h('span', { class: 'lm-stat-value' }, `${sci(one.lowest[1])} ${unitText(bundle.y.unit)}`),
      h('span', { class: 'lm-stat-note' }, `at ${massText(one.lowest[0])} ${unitText(bundle.x.unit)}${one.isMarker ? ' · the number its abstract states' : ` · of ${one.points.length} published points`}`),
    ]),
  ])));

  // ---- the citations
  const citation = (one) => {
    const row = one.row;
    const rows = [];
    rows.push(['Experiment', link(recordRoute(row.experiment_id), nameOf(row.experiment_id))]);
    if (row.result_id) rows.push(['Result in the Atlas', link(recordRoute(row.result_id), nameOf(row.result_id))]);
    const paper = row.paper || {};
    const paperLinks = [];
    if (paper.arxiv) paperLinks.push(external(`https://arxiv.org/abs/${paper.arxiv}`, `arXiv:${paper.arxiv}`));
    if (paper.doi) paperLinks.push(external(`https://doi.org/${paper.doi}`, `DOI ${paper.doi}`));
    rows.push(['Paper', [paper.title ? `${paper.title}. ` : '', paper.journal ? `${paper.journal}. ` : '', ...paperLinks.flatMap((a, i) => (i ? [' · ', a] : [a]))]]);
    rows.push(['Confidence level', row.confidence_level.display]);
    if (one.isMarker) {
      rows.push(['Why a diamond', row.hepdata_note]);
      rows.push(['What the abstract says', h('blockquote', { class: 'lm-quote' }, `“${row.quote}”`)]);
      rows.push(['Where', `${row.locator}. Taken from the Atlas record named above; not re-fetched for this page.`]);
      rows.push(['The point', `${massText(row.point.x)} ${unitText(row.columns.x.unit)}, ${sci(row.point.y)} ${unitText(row.columns.y.unit)}`]);
    } else {
      const hd = row.hepdata;
      rows.push(['HEPData record', [external(hd.record_url, hd.record_url.replace('https://www.', '')), ` · version ${hd.version} · ${hd.license}`]]);
      rows.push(['Table', [`“${hd.table}” · `, external(`https://doi.org/${hd.table_doi}`, `DOI ${hd.table_doi}`)]]);
      rows.push(['Columns used', `${row.columns.x.name} → ${unitText(row.columns.x.unit)} (x); ${row.columns.y.name} → ${unitText(row.columns.y.unit)} (y)`]);
      rows.push(['Points', `${row.points.length} of the table’s ${hd.rows} rows${row.thinned ? ', thinned' : ', not thinned'}`]);
    }
    return h('article', { class: `lm-cite ${one.className}` }, [
      h('h4', {}, [swatchOf(one, 24), ` ${one.label}`]),
      h('dl', { class: 'lm-cite-list' }, rows.flatMap(([key, value]) => [h('dt', {}, key), h('dd', {}, value)])),
    ]);
  };
  const cites = h('section', { class: 'lm-cites', 'aria-labelledby': 'lm-cites-h' }, [
    h('h3', { id: 'lm-cites-h' }, 'Where each line comes from'),
    ...model.series.map(citation),
  ]);

  // ---- the numbers, per series
  const numbers = h('section', { class: 'lm-numbers', 'aria-labelledby': 'lm-numbers-h' }, [
    h('h3', { id: 'lm-numbers-h' }, 'The numbers'),
    h('p', { class: 'lm-numbers-note' }, `Every plotted point, in ${unitText(bundle.x.unit)} and ${unitText(bundle.y.unit)}, exactly as stored.`),
    ...model.series.map((one) => h('details', { class: 'lm-data' }, [
      h('summary', {}, `${one.label} · ${one.points.length} point${one.points.length === 1 ? '' : 's'}`),
      h('div', { class: 'lm-table-scroll' }, h('table', { class: 'lm-table' }, [
        h('caption', {}, `${one.label}: ${one.row.quantity}`),
        h('thead', {}, h('tr', {}, [
          h('th', { scope: 'col' }, `${bundle.x.label} (${unitText(bundle.x.unit)})`),
          h('th', { scope: 'col' }, `${one.isMarker ? 'Published minimum' : one.row.columns.y.name} (${unitText(bundle.y.unit)})`),
        ])),
        h('tbody', {}, one.points.map(([x, y]) => h('tr', {}, [h('td', { class: 'lm-num' }, String(x)), h('td', { class: 'lm-num' }, String(y))]))),
      ])),
    ])),
  ]);

  host.body.append(lede, figure, stats, cites, numbers);
  fillMethod(host.method, { bundle, model });

  // ---- draw, and keep drawing as the stage resizes
  let focused = null;
  let lastEntry = null;
  let frame = 0;
  const describe = (entry) => {
    const { one, point } = entry;
    return `${one.label}: ${massText(point[0])} ${unitText(bundle.x.unit)}, ${sci(point[1])} ${unitText(bundle.y.unit)} (${one.isMarker ? 'published minimum' : '90% CL upper limit'}).`;
  };
  const applyFocus = () => {
    figure.dataset.focus = focused || '';
    for (const chip of legend.querySelectorAll('.lm-chip')) chip.setAttribute('aria-pressed', chip.dataset.slug === focused ? 'true' : 'false');
    // Picking one series out dims the others (the legend's chips, the lines and the labels).
    for (const el of figure.querySelectorAll('.lm-series, .lm-label')) {
      el.classList.toggle('is-dim', !!focused && el.dataset.slug !== focused);
    }
  };
  function draw() {
    const width = Math.floor(plotWrap.clientWidth || 0);
    if (width < 280) return;
    const drawn = drawPlot(model, bundle, width);
    plotWrap.replaceChildren(drawn.svg);
    const { hit, cross, overlay } = drawn;
    const nearest = (event) => {
      const box = drawn.svg.getBoundingClientRect();
      const x = ((event.clientX - box.left) / box.width) * drawn.width;
      const y = ((event.clientY - box.top) / box.height) * drawn.height;
      let best = null;
      let bestD = Infinity;
      for (const entry of hit) {
        if (focused && entry.one.slug !== focused) continue;
        const d = (entry.px - x) ** 2 + (entry.py - y) ** 2;
        if (d < bestD) { bestD = d; best = entry; }
      }
      return best;
    };
    const show = (entry) => {
      lastEntry = { one: entry.one, point: entry.point };
      cross.setAttribute('visibility', 'visible');
      cross.setAttribute('transform', `translate(${entry.px.toFixed(1)} ${entry.py.toFixed(1)})`);
      cross.setAttribute('class', `lm-cross ${entry.one.className}`);
      readout.textContent = describe(entry);
    };
    overlay.addEventListener('pointermove', (event) => { const entry = nearest(event); if (entry) show(entry); });
    overlay.addEventListener('pointerdown', (event) => {
      const entry = nearest(event);
      if (!entry) return;
      show(entry);
      host.announce(describe(entry));
    });
    overlay.addEventListener('pointerleave', (event) => {
      if (event.pointerType === 'mouse') cross.setAttribute('visibility', 'hidden');
    });
    applyFocus();
    // A resize redraws the figure; the point the reader was reading stays on screen.
    if (lastEntry) {
      const again = hit.find((entry) => entry.one.slug === lastEntry.one.slug && entry.point === lastEntry.point);
      if (again) show(again);
    }
  }
  const redraw = () => {
    window.cancelAnimationFrame(frame);
    frame = window.requestAnimationFrame(draw);
  };
  legend.addEventListener('click', (event) => {
    const chip = event.target.closest('.lm-chip');
    if (!chip) return;
    focused = focused === chip.dataset.slug ? null : chip.dataset.slug;
    applyFocus();
  });
  let observer = null;
  if (typeof ResizeObserver !== 'undefined') {
    observer = new ResizeObserver(redraw);
    observer.observe(plotWrap);
  }
  draw();
  window.requestAnimationFrame(draw);

  host.announce(`${WORKING_TITLE}: ${bundle.title}. ${model.series.length} results are drawn, ${model.series.filter((one) => !one.isMarker).length} as curves.`);

  return {
    update() { /* the plot does not depend on the timeline year */ },
    destroy() {
      window.cancelAnimationFrame(frame);
      if (observer) observer.disconnect();
    },
  };
}

// ----------------------------------------------------------- the method disclosure
function fillMethod(el, { bundle, model }) {
  const curves = model.series.filter((one) => !one.isMarker);
  const markers = model.series.filter((one) => one.isMarker);
  const maxPoints = Math.max(...curves.map((one) => one.points.length));
  const fileRows = model.series.map((one) => {
    const row = one.row;
    return h('tr', {}, [
      h('th', { scope: 'row' }, one.label),
      h('td', {}, one.isMarker ? 'a published minimum (no HEPData table)' : `HEPData ins${row.hepdata.inspire_id}, “${row.hepdata.table}”`),
      h('td', {}, one.isMarker ? 'the quoted value' : `${row.columns.x.name}, ${row.columns.y.name}`),
      h('td', { class: 'lm-num' }, one.isMarker ? '1' : `${row.points.length} of ${row.hepdata.rows}`),
      h('td', {}, one.isMarker ? 'not applicable' : `${row.hepdata.retrieved}; sha-256 ${row.hepdata.table_sha256.slice(0, 12)}…`),
      h('td', {}, `data/atlas/limits/${row.slug}.json`),
    ]);
  });
  el.replaceChildren(
    h('p', { class: 'bs-method-intro' }, [
      'Nothing on this page is computed from a model. Each curve is a table copied from HEPData, the open repository of published numbers, where it is licensed CC0; ',
      'the Atlas stores the points in a small file of its own, with the record, the table, the DOIs, the confidence level, the exact columns and the units, ',
      'and its validator refuses a file whose points are not finite positive numbers in the plot’s units.',
    ]),
    h('h3', {}, 'Inputs'),
    h('div', { class: 'lm-table-scroll' }, h('table', { class: 'lm-table' }, [
      h('caption', {}, 'The data files behind the figure'),
      h('thead', {}, h('tr', {}, ['Series', 'Source', 'Columns used', 'Points kept', 'Fetched', 'File'].map((t) => h('th', { scope: 'col' }, t)))),
      h('tbody', {}, fileRows),
    ])),
    h('h3', {}, 'What is drawn'),
    h('ul', { class: 'bs-method-list' }, [
      h('li', {}, `Axes: ${bundle.x.label.toLowerCase()} in ${unitText(bundle.x.unit)} against the ${bundle.y.label.toLowerCase()} in ${unitText(bundle.y.unit)}, both logarithmic (base 10). A point is drawn at (log₁₀ x, log₁₀ y); the figure applies no other transformation.`),
      h('li', {}, 'A curve is its published points joined by straight segments on the logarithmic axes. Between two points the table does not say what the limit is; the segment is a guide to the eye, not a measurement.'),
      h('li', {}, 'The tinted region above a line is what that result excludes at the stated confidence level. Regions of different results overlap, so the most excluded area is the darkest.'),
      h('li', {}, 'Each limit rests on its own paper’s assumptions (the dark-matter halo, the nuclear physics of spin-independent scattering, the statistical method). They are not restated here: read them in the paper cited under the figure.'),
    ]),
    h('h3', {}, 'Units'),
    h('p', {}, [
      'HEPData’s column headers carry names but no units. The units are fixed by a check on every curve: the number its abstract quotes, with its unit (cm² at a stated mass in GeV/c²), equals the table’s lowest value in the plotted column at that mass. ',
      ...curves.map((one) => `${one.label}: the abstract’s ${sci(one.row.units_check.value, 2)} cm² at ${massText(one.row.units_check.mass)} GeV/c² is the table’s ${sci(one.lowest[1], 4)} at ${massText(one.lowest[0])}. `),
    ]),
    h('h3', {}, 'Thinning'),
    h('p', {}, `No curve is thinned: the longest has ${maxPoints} points, under the 300 the Atlas keeps. A longer table would be thinned, its data file would say so (thinned: true, with the table’s own row count), and this section would state it.`),
    h('h3', {}, 'What is not drawn, and why'),
    h('ul', { class: 'bs-method-list' }, [
      h('li', {}, markers.length
        ? `${markers.map((one) => one.short.replace(/ \(min\.\)$/, '')).join(' and ')}: no limit curve is drawn because none is in HEPData (searched on 2026-10-26 by arXiv number, title, DOI and collaboration). The diamonds are the one number each abstract states, taken from the Atlas’s own records. They are not curves, and they do not say that nothing better was published.`
        : 'Every result with a published curve is drawn.'),
      h('li', {}, 'The neutrino “fog” (the floor where solar, atmospheric and supernova neutrinos begin to mimic a WIMP) is not drawn. It would be drawn only from a published curve obtained the same way, from a HEPData table with its record and DOI; no such table is in HEPData, so the Atlas leaves it out rather than redraw it from a figure.'),
      h('li', {}, 'Other limits (spin-dependent, other detectors, other runs of the same experiments) are not on this plot: it shows what the Atlas has sourced, which is a part of the field and not all of it.'),
    ]),
    h('h3', {}, 'Licence'),
    h('p', {}, 'The HEPData tables are CC0 (public domain). The papers’ own text appears only where a quotation is marked.'),
  );
}
