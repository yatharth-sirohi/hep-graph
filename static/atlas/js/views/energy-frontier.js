// energy-frontier.js — "The energy frontier": a Livingston-style chart of every accelerator in the
// Atlas, its energy (logarithmic) against the year it began operating.
//
//   #/view/energy-frontier
//
// The chart toolkit is chart.js; which accelerators qualify, which field gives each its energy and
// which interval its year are frontier-rows.js (pure, shared with the panels and the search). This
// file puts them on the page, with the same rows as a table, the machines that cannot be plotted and
// why, and the "Inputs and method" disclosure. Mounted by host.js through registry.js.

import { createChart, dataTable, h } from './chart.js';
import { claimItem, lazyInputs } from './chart-inputs.js';
import {
  ENERGY_SCALE_EV, FAMILIES, WORKING_TITLE, energyText, frontierData, startedBy,
} from './frontier-rows.js';
import { quantityText } from '../model.js';

/** A tick of the energy axis in the units a physicist reads: 10 MeV, 1 GeV, 100 GeV, 10 TeV. */
function energyTick(gev) {
  if (gev < 1) return `${Math.round(gev * 1000)} MeV`;
  if (gev < 1000) return `${Math.round(gev)} GeV`;
  return `${Math.round(gev / 1000)} TeV`;
}

const quantityName = (row) => (row.collider ? '√s, the centre-of-mass energy' : 'beam energy');
const fieldName = (row) => (row.collider ? 'cms_energy' : 'beam_energy');
const startText = (row) => `${row.start.approx ? 'c. ' : ''}${row.start.year}`;

export function mount(ctx) {
  const { atlas, host, loader } = ctx;
  host.setTitle(WORKING_TITLE);
  const { rows, skipped } = frontierData(atlas);
  if (!rows.length) {
    host.fail('No accelerator in the data loaded here has both a sourced energy and a start of operation, so there is nothing to plot. '
      + 'That says nothing about the machines themselves: only that this Atlas build holds no values for them.');
    return null;
  }

  let timelineState = ctx.timelineState;
  const link = (route, text) => {
    const a = h('a', { class: 'entity-link', href: `#/${route.type}/${route.slug}` }, text);
    a.addEventListener('click', (event) => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      ctx.navigate({ entity: route });
    });
    return a;
  };
  const accLink = (row) => link({ type: 'accelerator', slug: row.slug }, row.name);

  host.setSubtitle(`${rows.length} accelerators plotted · energy against the year each began operating`);

  // ---- the sentence a newcomer can read
  const colliders = rows.filter((row) => row.collider);
  const firstCollider = colliders[0];
  const topCollider = colliders.reduce((best, row) => (row.energy.gev > best.energy.gev ? row : best), colliders[0]);
  const lede = h('p', { class: 'ch-lede' }, [
    'Each marker is one accelerator: the year it began operating across, its energy up, on a logarithmic axis. ',
    'A filled marker is a collider, drawn at √s, the energy available in a collision; a hollow one is any other machine, drawn at its beam energy. ',
    colliders.length > 1
      ? `Among the colliders, √s grows from ${energyText(firstCollider.energy.gev)} (${firstCollider.label}, ${firstCollider.start.year}) to ${energyText(topCollider.energy.gev)} (${topCollider.label}, ${topCollider.start.year}).`
      : '',
  ]);

  // ---- the chart
  const years = rows.map((row) => row.start.year);
  const gevs = rows.map((row) => row.energy.gev);
  const xLo = Math.floor((Math.min(...years) - 4) / 5) * 5;
  const xHi = Math.max(2030, Math.ceil((Math.max(...years) + 4) / 5) * 5);
  const yLo = 10 ** Math.floor(Math.log10(Math.min(...gevs) * 0.9));
  const yHi = 10 ** Math.ceil(Math.log10(Math.max(...gevs) * 1.1));
  const families = [...new Set(rows.map((row) => row.family))];
  const chartHost = h('div', { class: 'ch-chart', id: 'ef-chart' });
  const points = rows.map((row) => {
    const family = FAMILIES[row.family] || FAMILIES.other;
    const shown = quantityText(row.energy.quantity);
    return {
      id: row.id,
      x: row.start.year,
      y: row.energy.gev,
      label: row.other ? `${row.label} †` : row.label,
      shape: family.shape,
      tone: family.tone,
      hollow: !row.collider,
      priority: row.collider ? 3 : 1, // colliders are labelled first, and a phone labels no other machine that needs a leader line
      href: `#/accelerator/${row.slug}`,
      aria: `${row.name}: ${shown}, ${quantityName(row)}, began operating ${startText(row)}. ${row.other ? `The record also gives ${quantityText(row.other.quantity)}. ` : ''}Opens the accelerator record.`,
      tip: [
        row.name,
        `${energyText(row.energy.gev)} · ${quantityName(row)}`,
        `Recorded as: ${shown}`,
        `Began operating ${startText(row)}`,
        row.energy.kind === 'interval' ? `Energy of its ${row.energy.label} interval` : null,
        row.other ? `† Also recorded: ${quantityText(row.other.quantity)}` : null,
        `Particles: ${row.particles.join(', ') || 'not recorded'}`,
      ].filter(Boolean),
    };
  });
  const yearNote = h('p', { class: 'ef-year-note ch-caption', id: 'ef-year-note', role: 'status' });
  const labelNote = h('span', { id: 'ef-label-note' });
  const chart = createChart(chartHost, {
    id: 'energy-frontier',
    title: 'Energy of each accelerator against the year it began operating',
    description: () => `${rows.length} accelerators, from ${Math.min(...years)} to ${Math.max(...years)}, on a linear year axis; energy from ${energyText(yLo)} to ${energyText(yHi)} on a logarithmic axis. `
      + `${rows.map((row) => `${row.label}: ${energyText(row.energy.gev)} ${row.collider ? 'centre-of-mass' : 'beam'} energy, ${startText(row)}`).join('; ')}. The same numbers are in the table below the chart.`,
    x: { kind: 'linear', domain: [xLo, xHi], label: 'Year the machine began operating', tickLabel: (v) => String(v) },
    y: { kind: 'log', domain: [yLo, yHi], label: 'Energy (log scale)', tickLabel: energyTick },
    points,
    omitCrowdedLabels: true,
    compactLeaderMinPriority: 3, // on a phone only a collider earns a label that needs a leader line
    legend: [
      {
        title: 'Particle type (colour and shape)',
        items: families.map((key) => ({ shape: FAMILIES[key].shape, tone: FAMILIES[key].tone, text: FAMILIES[key].label })),
      },
      {
        title: 'Energy drawn (filled or hollow)',
        items: [
          { shape: 'circle', tone: 'plain', text: '√s of a collider' },
          { shape: 'circle', tone: 'plain', hollow: true, text: 'Beam energy of any other machine' },
        ],
      },
    ],
    onOpen: (point) => ctx.navigate({ entity: { type: 'accelerator', slug: point.id.split(':')[1] } }),
    onDraw: ({ labelled, total }) => {
      labelNote.textContent = labelled < total
        ? `At this width ${total - labelled} of the ${total} markers carry no label; hover or focus one, or read the table, to name it. `
        : '';
    },
  });

  const notes = rows.filter((row) => row.other);
  const figure = h('div', { class: 'ch-block ef-figure' }, [
    chartHost,
    yearNote,
    h('p', { class: 'ch-caption' }, [
      h('strong', {}, 'A collider’s √s and a beam’s energy are not the same quantity. '),
      'A beam of energy E on a proton at rest has √s ≈ √(2 E mₚ c²): a 450 GeV beam gives about 29 GeV. The chart does not convert, which is why the markers differ. ',
      'Each marker opens its accelerator. ',
      labelNote,
    ]),
    notes.length ? h('ul', { class: 'ch-footnotes ef-footnotes' }, notes.map((row) => h('li', {}, [
      `† ${row.label}: drawn at ${quantityText(row.energy.quantity)} (${row.energy.kind === 'interval' ? `its ${row.energy.label} interval` : 'the record'}); the record also states ${quantityText(row.other.quantity)}.`,
    ]))) : null,
  ]);

  // ---- the same rows as a table
  const table = dataTable({
    caption: 'The plotted accelerators, in order of the year they began operating',
    className: 'ef-table',
    rows,
    rowId: (row) => row.id,
    columns: [
      { label: 'Accelerator', header: true, cell: accLink },
      { label: 'Began operating', numeric: true, cell: (row) => `${startText(row)}${row.start.label ? ` (${row.start.label})` : ''}` },
      { label: 'Energy drawn', cell: (row) => `${quantityText(row.energy.quantity)}` },
      { label: 'Quantity', cell: (row) => (row.collider ? '√s (collider, filled)' : 'Beam energy (hollow)') },
      { label: 'Energy (GeV)', numeric: true, cell: (row) => String(Number(row.energy.gev.toPrecision(4))) },
      { label: 'Particles', cell: (row) => row.particles.join(', ') },
      { label: 'Also recorded', cell: (row) => (row.other ? quantityText(row.other.quantity) : '') },
    ],
  });

  // ---- not plotted
  const unplotted = h('section', { class: 'ch-block ef-unplotted', 'aria-labelledby': 'ef-unplotted-h' }, [
    h('h3', { id: 'ef-unplotted-h' }, 'Not plotted'),
    skipped.length
      ? h('p', {}, 'These accelerators are in the Atlas but have no point, for the reason given. A machine missing here is a gap in the record, not a statement about the machine.')
      : h('p', { class: 'empty-note' }, 'Every accelerator in the Atlas has a sourced energy and a start of operation, so all are plotted.'),
    skipped.length ? dataTable({
      caption: 'Accelerators with no point on the chart, and why',
      className: 'ef-skipped',
      rows: skipped,
      rowId: (entry) => entry.id,
      columns: [
        { label: 'Accelerator', header: true, cell: (entry) => link({ type: 'accelerator', slug: entry.id.split(':')[1] }, entry.accelerator.name) },
        { label: 'Why it is not plotted', cell: (entry) => entry.reason },
      ],
    }) : null,
  ]);

  host.body.replaceChildren(lede, figure, unplotted, h('div', { class: 'ch-block' }, table));

  // ---- the year: markers after it fade, a line stands at it
  function paintYear() {
    const ts = timelineState || {};
    const hasYear = ts.year != null;
    const hasRange = !!ts.range;
    if (!hasYear && !hasRange) {
      chart.setFaded([]);
      chart.setXMarker(null);
      yearNote.textContent = '';
      yearNote.hidden = true;
      for (const tr of document.querySelectorAll('#view-host .ef-table tbody tr')) tr.classList.remove('is-faded');
      return;
    }
    const when = hasYear ? String(ts.year) : `${ts.range[0]}–${ts.range[1]}`;
    const late = rows.filter((row) => !startedBy(row, ts));
    const ids = new Set(late.map((row) => row.id));
    chart.setFaded(ids, `Had not begun operating ${hasYear ? 'in' : 'by'} ${hasYear ? when : ts.range[1]}`);
    chart.setXMarker(hasYear ? ts.year : null, when);
    for (const tr of document.querySelectorAll('#view-host .ef-table tbody tr')) tr.classList.toggle('is-faded', ids.has(tr.dataset.id));
    yearNote.hidden = false;
    yearNote.textContent = `${hasYear ? `In ${when}` : `By ${ts.range[1]}`}, ${rows.length - late.length} of the ${rows.length} plotted machines had begun operating`
      + `${late.length ? `; the ${late.length} that began later are faded` : ''}. Move the timeline to change the year.`;
  }
  paintYear();

  // ---- inputs and method
  const inputs = fillMethod(host.method, { rows, skipped, link, loader });
  host.announce(`${WORKING_TITLE}: ${rows.length} accelerators, energy against the year each began operating.`);

  return {
    update(next) {
      timelineState = next.timelineState;
      paintYear();
    },
    destroy() {
      chart.destroy();
      inputs.dispose();
    },
  };
}

// ----------------------------------------------------------- the method disclosure
function fillMethod(el, { rows, skipped, link, loader }) {
  const factorRows = Object.entries(ENERGY_SCALE_EV)
    .filter(([unit]) => rows.some((row) => row.energy.quantity.unit === unit))
    .map(([unit, ev]) => h('tr', {}, [
      h('th', { scope: 'row' }, unit),
      h('td', { class: 'ch-num' }, `${Number((ev / 1e9).toPrecision(6))} GeV`),
      h('td', { class: 'ch-num' }, String(rows.filter((row) => row.energy.quantity.unit === unit).length)),
    ]));

  const fieldTable = dataTable({
    caption: 'For each plotted point: the field its energy comes from, where in the record it is, and which interval gives its year',
    className: 'ch-method-table ef-field-table',
    rows,
    columns: [
      { label: 'Accelerator', header: true, cell: (row) => link({ type: 'accelerator', slug: row.slug }, row.name) },
      { label: 'Field used', cell: (row) => `${fieldName(row)} (${row.collider ? 'collider: √s' : 'not a collider: beam energy'})` },
      { label: 'Where in the record', cell: (row) => row.energy.pointer },
      { label: 'Year taken from', cell: (row) => `${row.start.pointer}${row.start.label ? ` (${row.start.label})` : ''}` },
    ],
  });

  const histories = rows.filter((row) => row.history.length > 0);
  const example = histories.find((row) => row.history[0].gev !== row.energy.gev) || null;
  const inputs = lazyInputs(el, {
    id: 'ef-inputs', loader, entries: rows,
    block: (row, sources, prov) => inputBlock(row, sources, prov, link),
  });

  el.replaceChildren(
    h('p', { class: 'ch-method-intro' }, 'The chart plots values the records already hold and computes nothing but a change of unit. Each marker is one accelerator at one energy and one year; the table below says which field and which interval each came from, and “Inputs” gives the quote and the sources behind every one.'),
    h('h3', {}, 'Which energy'),
    h('ul', { class: 'ch-method-list' }, [
      h('li', {}, [h('strong', {}, 'Colliders: √s. '), 'A collider is drawn at its centre-of-mass energy, the record’s `cms_energy`, and as a filled marker. A collider whose record has no sourced √s is not plotted: the chart does not derive one from the beam energies.']),
      h('li', {}, [h('strong', {}, 'Everything else: beam energy. '), 'A fixed-target accelerator, a synchrotron, a booster or a linac is drawn at the record’s `beam_energy`, as a hollow marker. For a beam on a fixed target, √s is far smaller than the beam energy, so a hollow marker is not comparable with a filled one on the same axis; this is a Livingston chart of what each machine delivers, not of what a collision can reach.']),
      h('li', {}, [h('strong', {}, 'Operating beats design. '), 'A record’s headline energy (`specs`) is often its design value. Where an interval of status “active” carries its own energy for the run it describes (the LHC’s runs, LEP1 and LEP2, CEBAF’s 4 and 6 GeV), the latest such interval gives the plotted energy, and the headline value is footnoted (†) if it differs. Where no interval carries one, the record’s stated value is drawn as the record words it, “design” included.']),
    ]),
    h('h3', {}, 'Which year'),
    h('p', {}, `The start of the first interval whose status is “active”: the year the machine began operating. A date marked planned is not a start, and a machine with no active interval (still in construction or approval) is not plotted. A machine is drawn once, at that year and at the energy above, even if it ran at a lower energy when it began or was upgraded later.${example ? ` ${example.label} began operating in ${example.start.year}, where its first recorded run was at ${quantityText(example.history[0].quantity)}, and is drawn at ${quantityText(example.energy.quantity)}.` : ''} The energies a record gives for its own runs are listed here in full for the machines that have them.`),
    histories.length ? h('ul', { class: 'ch-method-list' }, histories.map((row) => h('li', {}, [
      h('strong', {}, `${row.label}: `),
      row.history.map((entry) => `${entry.label}${entry.year ? ` (${entry.year})` : ''} ${quantityText(entry.quantity)}`).join('; '),
      '.',
    ]))) : null,
    h('h3', {}, 'Colour and shape'),
    h('p', {}, 'A marker’s colour and shape come from the first particle its record lists: electrons and positrons, protons (antiprotons and H⁻, which is stripped to protons, included), or ions (deuterons and alpha particles included). The table lists every particle a record gives; colour is never the only cue, because the shape differs too.'),
    h('h3', {}, 'The timeline'),
    h('p', {}, 'The timeline position fades the markers of machines that began operating after the selected year (or after the end of a selected range) and draws a line at the year. It changes nothing else: a machine is not moved to the energy it had in that year.'),
    h('h3', {}, 'Unit conversion'),
    h('p', {}, [
      'Energies are recorded in the unit their source uses and drawn in GeV. The factors below are ',
      h('strong', {}, 'copied from UNIT_SCALE[‘energy’] in hepgraph/atlas/schema.py'),
      ' (eV is the base unit there; the table divides by 10⁹ to give GeV). A check in the test suite fails if the two tables part. A value in a unit the table does not list, or a range with no single value, is not plotted.',
    ]),
    h('div', { class: 'ch-table-scroll' }, h('table', { class: 'ch-table ch-method-table' }, [
      h('caption', {}, 'Factors to GeV, for the units in use'),
      h('thead', {}, h('tr', {}, ['Recorded unit', 'One unit is', 'Points'].map((label) => h('th', { scope: 'col' }, label)))),
      h('tbody', {}, factorRows),
    ])),
    skipped.length ? h('h3', {}, 'Not plotted') : null,
    skipped.length ? h('p', {}, `${skipped.length} accelerator${skipped.length === 1 ? ' is' : 's are'} listed under the chart with the reason each has no point.`) : null,
    h('h3', {}, 'The field behind every point'),
    fieldTable,
    h('h3', {}, 'Inputs'),
    h('p', {}, 'Each point with the quote its energy and its start were read from, the place in the source, how sure the record is, and the sources behind them.'),
    inputs.holder,
  );
  return inputs;
}

/** One accelerator's inputs: its energy, the interval its year comes from, and the headline value where it was footnoted. */
function inputBlock(row, sources, prov, link) {
  const record = row.accelerator;
  const items = [
    claimItem(prov, sources, record, row.energy.pointer),
    claimItem(prov, sources, record, row.start.pointer),
    row.other ? claimItem(prov, sources, record, row.other.pointer) : null,
  ].filter(Boolean);
  return h('details', { class: 'ch-input' }, [
    h('summary', {}, `${row.name} — ${quantityText(row.energy.quantity)}, ${startText(row)}`),
    h('p', { class: 'ch-input-line' }, [
      'Drawn at ', h('strong', {}, energyText(row.energy.gev)), ` (${fieldName(row)}) in `, h('strong', {}, startText(row)),
      '. ', link({ type: 'accelerator', slug: row.slug }, 'Open the accelerator record'), '.',
    ]),
    items.length ? h('ul', { class: 'source-list' }, items) : h('p', { class: 'empty-note' }, 'No source is recorded for these values.'),
  ]);
}
