// compare.js — "Compare experiments": two to four experiments side by side.
//
//   #/view/compare/<slug>,<slug>[,<slug>…]
//
// Rows: status and dates, host facility and site, depth or overburden, baseline, target
// or fiducial mass, energy, technology, key results with dates, collaboration size.
// Every value is one sourced line (compare-rows.js) followed by a marker that links to
// its source; a row that shares a unit dimension is shown in one unit, the record's own
// wording a tooltip away; what the Atlas does not hold reads "not recorded". "Download
// CSV" exports exactly this table, with a citations column.
//
// This file only draws. The rows are compare-rows.js, the route compare-route.js, the
// tray that collects experiments is research/compare-tray.js. Mounted by host.js
// through registry.js; loaded only when the route is opened.

import { WORKING_TITLE, EXAMPLES, MAX_EXPERIMENTS, MIN_EXPERIMENTS, compareRoute, resolveArg } from './compare-route.js';
import {
  NOT_RECORDED, attachSources, buildComparison, comparisonCsv, shortExperimentName,
} from './compare-rows.js';
import * as tray from '../research/compare-tray.js';
import { accessDate, downloadFile, fileName } from '../research/files.js';
import { sourceTypeWord } from '../provenance.js';

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

// A line whose `kind` is a lifecycle status is drawn with the Atlas's own status badge (a dot and the word).
const STATUS_KINDS = new Set(['active', 'upgrade', 'commissioning', 'construction', 'approved', 'proposed', 'planned',
  'completed', 'decommissioned', 'shutdown']);

const plainClick = (event) => event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey;

export async function mount(ctx) {
  const { atlas, loader, host, navigate } = ctx;
  const body = host.body;

  // The page opened with nothing named (the search box, a bare link): the tray's list is
  // what the reader was collecting, so open that.
  if (!ctx.arg && tray.list().length) {
    navigate({ entity: compareRoute(tray.list()) }, { replace: true });
    return { destroy() {} };
  }

  const { experiments, unknown, extra } = resolveArg(atlas, ctx.arg);
  const slugs = experiments.map((e) => e.id.split(':')[1]);
  // What the address shows is what the tray holds from here on.
  tray.set(slugs);
  const { byId: results } = await loader.getResults();

  let timelineState = ctx.timelineState;
  let model = null;
  let provenance = null;
  let sourcesById = null;
  let sourcesState = 'idle'; // idle | loading | loaded | error
  let destroyed = false;

  const tableHolder = h('div', { class: 'cmp-table-holder' });
  const sourcesHolder = h('section', { class: 'cmp-sources', 'aria-labelledby': 'cmp-sources-h' });
  const csvStatus = h('p', { class: 'cmp-status', id: 'cmp-status', role: 'status', 'aria-live': 'polite' });

  function rebuild() {
    model = buildComparison({ atlas, results, timelineState }, experiments);
    if (provenance && sourcesById) attachSources(model, provenance, sourcesById);
  }

  // ---- the editor: who is being compared, and how to change it
  function go(next) {
    tray.set(next);
    navigate({ entity: compareRoute(next) });
  }

  const chips = h('ul', { class: 'cmp-chips', 'aria-label': 'Experiments in this comparison' }, experiments.map((record) => {
    const slug = record.id.split(':')[1];
    const remove = h('button', {
      type: 'button', class: 'cmp-chip-remove', 'aria-label': `Remove ${record.name} from the comparison`,
    }, '×');
    remove.addEventListener('click', () => go(slugs.filter((s) => s !== slug)));
    const link = h('a', { class: 'cmp-chip-name', href: `#/experiment/${slug}` }, shortExperimentName(record));
    link.addEventListener('click', (event) => {
      if (!plainClick(event)) return;
      event.preventDefault();
      navigate({ entity: { type: 'experiment', slug } });
    });
    return h('li', { class: 'cmp-chip' }, [link, remove]);
  }));

  const full = experiments.length >= MAX_EXPERIMENTS;
  const select = h('select', { id: 'cmp-add', class: 'cmp-add', 'aria-label': 'Add an experiment to the comparison' });
  select.appendChild(h('option', { value: '' }, full ? `The table holds ${MAX_EXPERIMENTS}; remove one to add another` : 'Add an experiment…'));
  const choices = Object.values(atlas.experiments || {})
    .filter((record) => !slugs.includes(record.id.split(':')[1]))
    .sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: 'base', numeric: true }));
  for (const record of choices) select.appendChild(h('option', { value: record.id.split(':')[1] }, record.name));
  select.disabled = full;
  select.addEventListener('change', () => {
    if (select.value) go([...slugs, select.value]);
  });

  const csvButton = h('button', { type: 'button', class: 'primary-btn cmp-csv', id: 'cmp-csv' }, 'Download CSV');
  csvButton.disabled = experiments.length < MIN_EXPERIMENTS;
  csvButton.addEventListener('click', () => { downloadCsv(); });

  const editor = h('div', { class: 'cmp-editor' }, [
    h('div', { class: 'cmp-editor-row' }, [
      h('span', { class: 'cmp-editor-label', id: 'cmp-chips-label' }, `Comparing (${experiments.length} of ${MAX_EXPERIMENTS})`),
      chips,
    ]),
    h('div', { class: 'cmp-editor-row' }, [
      h('label', { class: 'visually-hidden', for: 'cmp-add' }, 'Add an experiment to the comparison'),
      select,
      csvButton,
    ]),
    csvStatus,
  ]);

  const notices = [];
  if (unknown.length) {
    notices.push(h('p', { class: 'cmp-notice', role: 'alert' }, [
      `The Atlas has no experiment called ${unknown.map((s) => `“${s}”`).join(', ')}, so ${unknown.length === 1 ? 'it is' : 'they are'} not in the table. `,
      'Absence from the Atlas is not absence from the field: it covers part of it.',
    ]));
  }
  if (extra.length) {
    notices.push(h('p', { class: 'cmp-notice', role: 'status' },
      `The table holds ${MAX_EXPERIMENTS} experiments at most. Not shown: ${extra.map((e) => e.name).join(', ')}.`));
  }

  // ---- the lede, and the examples when there is nothing to compare yet
  const lede = h('p', { class: 'cmp-lede' },
    experiments.length >= MIN_EXPERIMENTS
      ? 'Each value comes from the Atlas record and carries a marker that opens its source. A value the Atlas does not hold reads “not recorded”: that says what is in the Atlas, not what exists.'
      : `Choose two to ${MAX_EXPERIMENTS} experiments to see them side by side, or add one from its panel with “Add to compare”.`);

  const examples = experiments.length >= MIN_EXPERIMENTS ? null : h('div', { class: 'cmp-examples' }, [
    h('h3', {}, 'Try one'),
    h('ul', { class: 'entity-list' }, EXAMPLES
      .filter((example) => example.slugs.every((slug) => (atlas.experiments || {})[`experiment:${slug}`]))
      .map((example) => {
        const a = h('a', { href: `#/view/compare/${example.slugs.join(',')}`, class: 'entity-link cmp-example' },
          `${example.label}: ${example.slugs.map((slug) => shortExperimentName(atlas.experiments[`experiment:${slug}`])).join(', ')}`);
        a.addEventListener('click', (event) => {
          if (!plainClick(event)) return;
          event.preventDefault();
          go(example.slugs);
        });
        return h('li', {}, a);
      })),
  ]);

  // ---- the table
  function markerLink(source) {
    const a = h('a', {
      class: 'cmp-src', href: source.url, target: '_blank', rel: 'noopener',
      'aria-label': `Source ${source.n}: ${source.title} (opens in a new tab)`, title: source.title,
    }, String(source.n));
    return a;
  }

  function renderLine(line) {
    const parts = [];
    if (line.label) parts.push(h('span', { class: 'cmp-label' }, `${line.label}: `));
    let text;
    if (line.route) {
      text = h('a', { class: 'entity-link cmp-text', href: `#/${line.route.type}/${line.route.slug}` }, line.text);
      text.addEventListener('click', (event) => {
        if (!plainClick(event)) return;
        event.preventDefault();
        navigate({ entity: line.route });
      });
    } else if (line.original) {
      // The converted value; the record's own wording is a hover or a focus away.
      text = h('abbr', {
        class: 'cmp-text cmp-converted', tabindex: '0', title: `Recorded as: ${line.original}`,
        'data-original': `Recorded as: ${line.original}`,
      }, line.text);
    } else if (STATUS_KINDS.has(line.kind)) {
      text = h('span', { class: `status-badge status-${line.kind} cmp-status-badge`, title: line.note }, line.text);
    } else {
      text = h('span', { class: 'cmp-text', title: line.note }, line.text);
    }
    parts.push(text);
    if (line.suffix) parts.push(h('span', { class: 'cmp-suffix' }, line.suffix));
    const marks = h('span', { class: 'cmp-marks' });
    if (model.sourceList) {
      for (const n of line.markers || []) marks.append(' ', markerLink(model.sourceList[n - 1]));
      if (!(line.markers || []).length && !line.derived && (line.claims.length || line.sourceIds.length)) {
        marks.append(' ', h('span', { class: 'cmp-nosrc' }, 'no source recorded'));
      }
    }
    parts.push(marks);
    return h('li', { class: `cmp-line${line.indent ? ' is-sub' : ''}${line.kind ? ` kind-${line.kind}` : ''}` }, parts);
  }

  function renderCell(cell, label) {
    return h('td', { 'data-label': label }, cell.lines.length
      ? h('ul', { class: 'cmp-lines' }, cell.lines.map(renderLine))
      : h('p', { class: 'cmp-missing' }, NOT_RECORDED));
  }

  function renderTable() {
    const heads = model.experiments.map((exp) => {
      const link = h('a', { class: 'entity-link', href: `#/experiment/${exp.slug}` }, exp.short);
      link.addEventListener('click', (event) => {
        if (!plainClick(event)) return;
        event.preventDefault();
        navigate({ entity: { type: 'experiment', slug: exp.slug } });
      });
      return h('th', { scope: 'col' }, [link, h('span', { class: 'cmp-kind' }, exp.kind)]);
    });
    const table = h('table', { class: 'cmp-table', style: `--cols:${model.experiments.length}` }, [
      h('caption', {}, 'The experiments side by side. Values that share a dimension are in one unit; hover or focus a converted value to see how the record words it.'),
      h('thead', {}, h('tr', {}, [h('th', { scope: 'col' }, 'Quantity'), ...heads])),
      h('tbody', {}, model.rows.map((row) => h('tr', { 'data-row': row.key }, [
        h('th', { scope: 'row' }, row.label),
        ...row.cells.map((cell, index) => renderCell(cell, model.experiments[index].short)),
      ]))),
    ]);
    return h('div', {
      class: 'cmp-scroll', role: 'region', 'aria-label': 'Comparison table', tabindex: '0',
    }, table);
  }

  function renderSources() {
    const retry = () => { loadSources().catch((error) => window.console.warn(error)); };
    if (sourcesState === 'error') {
      const button = h('button', { type: 'button', class: 'text-btn' }, 'Retry');
      button.addEventListener('click', retry);
      return [h('h3', { id: 'cmp-sources-h' }, 'Sources'), h('p', { class: 'error-note', role: 'alert' }, 'Could not load the sources, so the table has no source markers yet. '), button];
    }
    if (sourcesState !== 'loaded') {
      return [h('h3', { id: 'cmp-sources-h' }, 'Sources'), h('p', { class: 'loading-note', role: 'status' }, 'Loading the sources…')];
    }
    const list = model.sourceList;
    return [
      h('h3', { id: 'cmp-sources-h' }, `Sources cited (${list.length})`),
      list.length
        ? h('ol', { class: 'cmp-source-list' }, list.map((source) => h('li', { value: source.n }, [
          h('a', { href: source.url, target: '_blank', rel: 'noopener' }, source.title),
          ' ',
          h('span', { class: 'source-type' }, sourceTypeWord(source.type)),
          source.accessed ? h('span', { class: 'source-access' }, ` · accessed ${source.accessed}`) : null,
        ])))
        : h('p', { class: 'empty-note' }, 'No source is recorded for any value in this table.'),
    ];
  }

  function draw() {
    tableHolder.replaceChildren(renderTable());
    sourcesHolder.replaceChildren(...renderSources());
  }

  // ---- sources: provenance.json and sources.json are large, so they follow the first paint
  let sourcesPromise = null;
  function loadSources() {
    if (sourcesPromise) return sourcesPromise;
    sourcesState = 'loading';
    sourcesPromise = (async () => {
      try {
        const [prov, sources] = await Promise.all([loader.getProvenance(), loader.getSources()]);
        provenance = prov;
        sourcesById = sources.byId;
        sourcesState = 'loaded';
        if (!destroyed) { rebuild(); draw(); }
      } catch (error) {
        sourcesState = 'error';
        sourcesPromise = null;
        if (!destroyed) draw();
        throw error;
      }
    })();
    return sourcesPromise;
  }

  async function downloadCsv() {
    csvStatus.classList.remove('is-error');
    csvStatus.textContent = 'Preparing the citations…';
    try {
      await loadSources();
      const manifest = await loader.getManifest();
      const dataVersion = manifest.data_version || manifest.version || 'unknown';
      const accessed = accessDate();
      const text = comparisonCsv(model, { dataVersion, accessed, link: window.location.href });
      const name = fileName(['hep-atlas-compare', ...model.experiments.map((e) => e.slug), accessed], 'csv');
      downloadFile(name, text, 'text/csv');
      csvStatus.textContent = `Downloaded ${name}: ${model.rows.length} rows, with a citations column.`;
    } catch (error) {
      csvStatus.classList.add('is-error');
      csvStatus.textContent = `The CSV could not be prepared: ${error.message}. Try again.`;
    }
  }

  // ---- inputs and method (the host's disclosure)
  host.method.replaceChildren(
    h('p', {}, 'Nothing in the table is computed from other numbers. Each row is read from the Atlas record as follows, and a row that has no such value for an experiment reads “not recorded”.'),
    h('ul', { class: 'cmp-method-list' }, [
      h('li', {}, [h('strong', {}, 'Status and dates. '), 'The status at the year or range selected on the timeline, read from the experiment’s dated intervals; the dates are those intervals, each with its own sources.']),
      h('li', {}, [h('strong', {}, 'Host facility and site. '), 'The experiment’s facility roles and sites, each with the sources of that role or of the site’s location.']),
      h('li', {}, [h('strong', {}, 'Depth or overburden. '), 'Key specifications labelled as a depth or an overburden, and the depth and water-equivalent depth of the experiment’s sites. Metres of rock and metres water equivalent are different quantities and are never converted into each other.']),
      h('li', {}, [h('strong', {}, 'Baseline. '), 'Key specifications labelled as a baseline or a distance from the source; for a beam experiment with none, the sourced baseline of its beamline.']),
      h('li', {}, [h('strong', {}, 'Target or fiducial mass. '), 'Every mass among the key specifications except magnets and equipment. The label stays beside each value, because a “detector mass” is not a target mass.']),
      h('li', {}, [h('strong', {}, 'Energy. '), 'The recorded energy regime, and beam or collision energies; resolutions, thresholds and Q-values are not energies of the experiment and are left out.']),
      h('li', {}, [h('strong', {}, 'Technology. '), 'The technology class of the experiment’s detectors.']),
      h('li', {}, [h('strong', {}, 'Key results. '), 'The results the Atlas records for the experiment, oldest first, with their dates.']),
      h('li', {}, [h('strong', {}, 'Collaboration size. '), 'The membership recorded for the collaboration, with the date it was counted, and any collaboration-size specification.']),
    ]),
    h('h3', {}, 'Units'),
    h('p', {}, 'Rows that share a dimension (lengths, masses, energies) are shown in one unit, chosen so no value reads below 1. Only exact powers of ten between metric units are used, and only for a value the record words as one figure and one unit (“17.5 kt”, “~295 km”). A value with more in it (“260 kt total, 188 kt fiducial”) is shown exactly as recorded and is not converted. The record’s own wording is the tooltip of every converted value, and the CSV carries it beside the converted figure as “(recorded: …)”.'),
    h('h3', {}, 'Sources and the CSV'),
    h('p', {}, 'A marker is the number of a source in the list under the table and links to it. “No source recorded” means the record carries the value but provenance.json lists no source for it. The CSV has one column per experiment and a last column of the source URLs for each row; its first lines, starting with “#”, give the Atlas data version, the access date and the link to this comparison.'),
  );

  // ---- assemble, draw, then fetch the sources
  rebuild();
  host.setSubtitle(experiments.length ? experiments.map((e) => shortExperimentName(e)).join(' · ') : '');
  const page = h('div', { class: 'cmp-page' }, [lede, editor, ...notices]);
  if (examples) page.append(examples);
  if (experiments.length >= MIN_EXPERIMENTS) page.append(tableHolder, sourcesHolder);
  body.append(page);
  if (experiments.length >= MIN_EXPERIMENTS) {
    draw();
    window.setTimeout(() => { loadSources().catch((error) => window.console.warn(error)); }, 0);
    host.announce(`${WORKING_TITLE}: ${experiments.map((e) => shortExperimentName(e)).join(', ')}.`);
  } else {
    host.method.parentElement.hidden = true;
  }

  return {
    update(next) {
      timelineState = next.timelineState;
      if (experiments.length < MIN_EXPERIMENTS) return;
      rebuild();
      draw();
    },
    destroy() {
      destroyed = true;
    },
  };
}
