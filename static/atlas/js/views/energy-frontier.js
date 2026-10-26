// energy-frontier.js — "The energy frontier": a Livingston-style chart of the accelerators in the
// Atlas, their energy (logarithmic) against the year each energy began to apply.
//
//   #/view/energy-frontier
//
// A machine is a track: one point for every era the record gives an energy for, at the start year
// of that era, joined by a thin line in the machine's colour; the first point is its first operation.
// Where the Atlas dates no energy to a machine's start, the energy it records today is drawn at the
// start year as a dashed ring and said so: a machine never looks as if it began at its final energy.
//
// The chart toolkit is chart.js; which machines qualify, which field gives each its energy and which
// intervals its eras are, are frontier-rows.js (pure, shared with the panels and the search). This file
// puts them on the page, with the same points as a table, the machines that cannot be plotted and why,
// and the "Inputs and method" disclosure. Mounted by host.js through registry.js.

import { createChart, dataTable, h } from './chart.js';
import { claimItem, lazyInputs } from './chart-inputs.js';
import {
  AS_RECORDED_TODAY, ENERGY_SCALE_EV, FAMILIES, WORKING_TITLE, energyText, frontierData, startedBy,
} from './frontier-rows.js';
import { quantityText } from '../model.js';

/** A tick of the energy axis in the units a physicist reads: 10 keV, 10 MeV, 1 GeV, 100 GeV, 10 TeV. */
function energyTick(gev) {
  if (gev < 1e-3) return `${Math.round(gev * 1e6)} keV`;
  if (gev < 1) return `${Math.round(gev * 1000)} MeV`;
  if (gev < 1000) return `${Math.round(gev)} GeV`;
  return `${Math.round(gev / 1000)} TeV`;
}

const quantityName = (machine) => (machine.collider ? '√s, the centre-of-mass energy' : 'beam energy');
const fieldName = (machine) => (machine.collider ? 'cms_energy' : 'beam_energy');
const yearText = (point) => `${point.approx ? 'c. ' : ''}${point.year}`;

export function mount(ctx) {
  const { atlas, host, loader } = ctx;
  host.setTitle(WORKING_TITLE);
  const { rows, skipped, points: allPoints } = frontierData(atlas);
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
  const accLink = (machine) => link({ type: 'accelerator', slug: machine.slug }, machine.name);
  const hasEras = rows.some((row) => row.points.some((point) => point.kind === 'era'));
  const todayCount = allPoints.filter((point) => point.kind === 'today').length;

  host.setSubtitle(`${rows.length} accelerators · ${allPoints.length} points · energy against the year each energy began to apply`);

  // ---- the sentence a newcomer can read
  const colliderPoints = allPoints.filter((point) => point.machine.collider);
  const top = colliderPoints.reduce((best, point) => (!best || point.gev > best.gev ? point : best), null);
  let topSentence = '';
  if (top) {
    const eras = top.machine.points.filter((point) => point.kind === 'era');
    topSentence = eras.length > 1
      ? `The highest √s in the Atlas is the ${top.machine.label}’s: ${eras.map((point) => `${energyText(point.gev)} (${point.year})`).join(' → ')}.`
      : `The highest √s in the Atlas is ${energyText(top.gev)} (${top.machine.label}${top.kind === 'today' ? ', as recorded today' : `, ${top.year}`}).`;
  }
  const lede = h('p', { class: 'ch-lede' }, [
    'Each marker is an energy a machine had: the year it began across, the energy up, on a logarithmic axis. ',
    'A filled marker is a collider, drawn at √s, the energy available in a collision; a hollow one is any other machine, drawn at its beam energy. ',
    'A machine that ran at several energies is a line, from era to era. ',
    topSentence,
  ]);

  // ---- the chart
  const years = allPoints.map((point) => point.year);
  const gevs = allPoints.map((point) => point.gev);
  const xLo = Math.floor((Math.min(...years) - 4) / 5) * 5;
  const xHi = Math.max(2030, Math.ceil((Math.max(...years) + 4) / 5) * 5);
  const yLo = 10 ** Math.floor(Math.log10(Math.min(...gevs) * 0.9));
  const yHi = 10 ** Math.ceil(Math.log10(Math.max(...gevs) * 1.1));
  const families = [...new Set(rows.map((row) => row.family))];
  const chartHost = h('div', { class: 'ch-chart', id: 'ef-chart' });
  const chartPoints = allPoints.map((point) => {
    const machine = point.machine;
    const family = FAMILIES[machine.family] || FAMILIES.other;
    const shown = quantityText(point.quantity);
    const today = point.kind === 'today';
    const startsHere = point.index === 0;
    return {
      id: point.id,
      x: point.year,
      y: point.gev,
      group: machine.id,
      label: startsHere ? `${machine.label}${machine.other ? ' †' : ''}` : null,
      labelSide: 'left',
      shape: family.shape,
      tone: family.tone,
      hollow: !machine.collider,
      ring: today,
      priority: machine.collider ? 3 : 1, // colliders are labelled first, and a phone labels no other machine that needs a leader line
      href: `#/accelerator/${machine.slug}`,
      aria: `${machine.name}: ${shown}, ${quantityName(machine)}, ${today ? `from its first operation, ${yearText(point)}. ${AS_RECORDED_TODAY}` : `${point.label}, from ${yearText(point)}`}. `
        + `${startsHere && machine.other ? `The record also gives ${quantityText(machine.other.quantity)}. ` : ''}Opens the accelerator record.`,
      tip: [
        machine.name,
        `${energyText(point.gev)} · ${quantityName(machine)}`,
        `Recorded as: ${shown}`,
        today ? `Began operating ${yearText(point)}` : `${point.label}, from ${yearText(point)}`,
        today ? AS_RECORDED_TODAY : null,
        startsHere && machine.other ? `† Also recorded, not dated to an era: ${quantityText(machine.other.quantity)}` : null,
        `Particles: ${machine.particles.join(', ') || 'not recorded'}`,
      ].filter(Boolean),
    };
  });
  const chartLines = rows.map((machine) => ({
    tone: (FAMILIES[machine.family] || FAMILIES.other).tone,
    ids: machine.points.filter((point) => point.kind === 'era').map((point) => point.id),
  })).filter((line) => line.ids.length > 1);

  const yearNote = h('p', { class: 'ef-year-note ch-caption', id: 'ef-year-note', role: 'status' });
  const labelNote = h('span', { id: 'ef-label-note' });
  const legendEnergy = [
    { shape: 'circle', tone: 'plain', text: '√s of a collider' },
    { shape: 'circle', tone: 'plain', hollow: true, text: 'Beam energy of any other machine' },
  ];
  if (todayCount) legendEnergy.push({ shape: 'circle', tone: 'plain', hollow: true, ring: true, text: AS_RECORDED_TODAY.replace(/\.$/, '') });
  if (chartLines.length) legendEnergy.push({ tone: 'plain', line: true, text: 'One machine, era to era' });
  const chart = createChart(chartHost, {
    id: 'energy-frontier',
    title: 'Energy of each accelerator against the year each energy began to apply',
    description: () => `${rows.length} accelerators and ${allPoints.length} points, from ${Math.min(...years)} to ${Math.max(...years)}, on a linear year axis; energy from ${energyText(yLo)} to ${energyText(yHi)} on a logarithmic axis. `
      + `${rows.map((row) => `${row.label}: ${row.points.map((point) => `${energyText(point.gev)} ${yearText(point)}${point.kind === 'today' ? ' (as recorded today)' : ''}`).join(', ')}`).join('; ')}. The same numbers are in the table below the chart.`,
    x: { kind: 'linear', domain: [xLo, xHi], label: 'Year the energy began to apply', tickLabel: (v) => String(v) },
    y: { kind: 'log', domain: [yLo, yHi], label: 'Energy (log scale)', tickLabel: energyTick },
    points: chartPoints,
    lines: chartLines,
    omitCrowdedLabels: true,
    compactLeaderMinPriority: 3, // on a phone only a collider earns a label that needs a leader line
    legend: [
      {
        title: 'Particle type (colour and shape)',
        items: families.map((key) => ({ shape: FAMILIES[key].shape, tone: FAMILIES[key].tone, text: FAMILIES[key].label })),
      },
      { title: 'Energy drawn', items: legendEnergy },
    ],
    onOpen: (point) => ctx.navigate({ entity: { type: 'accelerator', slug: point.id.split('#')[0].split(':')[1] } }),
    onDraw: ({ labelled, total }) => {
      labelNote.textContent = labelled < total
        ? `At this width ${total - labelled} of the ${total} machines carry no label; hover or focus a marker, or read the table, to name it. `
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
      todayCount ? `${todayCount} of the ${allPoints.length} points are dashed: for those machines the Atlas records one energy, as it is today, and dates no energy to the start, so the energy a machine began with is not drawn. ` : '',
      'Each marker opens its accelerator. ',
      labelNote,
    ]),
    notes.length ? h('ul', { class: 'ch-footnotes ef-footnotes' }, notes.map((row) => h('li', {}, [
      `† ${row.label}: the record also states ${quantityText(row.other.quantity)}, which no era dates, so it is not drawn.`,
    ]))) : null,
  ]);

  // ---- the same points as a table
  const table = dataTable({
    caption: 'Every plotted point, by machine and year',
    className: 'ef-table',
    rows: allPoints,
    rowId: (point) => point.id,
    columns: [
      { label: 'Accelerator', header: true, cell: (point) => accLink(point.machine) },
      { label: 'Year', numeric: true, cell: (point) => yearText(point) },
      { label: 'Energy drawn', cell: (point) => quantityText(point.quantity) },
      { label: 'Energy (GeV)', numeric: true, cell: (point) => String(Number(point.gev.toPrecision(4))) },
      { label: 'Quantity', cell: (point) => (point.machine.collider ? '√s (collider, filled)' : 'Beam energy (hollow)') },
      { label: 'Which energy', cell: (point) => (point.kind === 'era' ? `Era: ${point.label}` : `First operation. ${AS_RECORDED_TODAY}`) },
      { label: 'Also recorded', cell: (point) => (point.index === 0 && point.machine.other ? quantityText(point.machine.other.quantity) : '') },
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

  // ---- the year: points after it fade, a line stands at it
  function paintYear() {
    const ts = timelineState || {};
    const hasYear = ts.year != null;
    const hasRange = !!ts.range;
    const tableRows = document.querySelectorAll('#view-host .ef-table tbody tr');
    if (!hasYear && !hasRange) {
      chart.setFaded([]);
      chart.setXMarker(null);
      yearNote.textContent = '';
      yearNote.hidden = true;
      for (const tr of tableRows) tr.classList.remove('is-faded');
      return;
    }
    const when = hasYear ? String(ts.year) : `${ts.range[0]}–${ts.range[1]}`;
    const late = allPoints.filter((point) => !startedBy(point, ts));
    const ids = new Set(late.map((point) => point.id));
    const begun = rows.filter((row) => startedBy({ year: row.first.year }, ts)).length;
    chart.setFaded(ids, `Applies from a later year than ${hasYear ? ts.year : ts.range[1]}`);
    chart.setXMarker(hasYear ? ts.year : null, when);
    for (const tr of tableRows) tr.classList.toggle('is-faded', ids.has(tr.dataset.id));
    yearNote.hidden = false;
    yearNote.textContent = `${hasYear ? `In ${when}` : `By ${ts.range[1]}`}, ${begun} of the ${rows.length} machines had begun operating`
      + `${late.length ? `; the ${late.length} point${late.length === 1 ? '' : 's'} for later years ${late.length === 1 ? 'is' : 'are'} faded` : ''}. Move the timeline to change the year.`;
  }
  paintYear();

  // ---- inputs and method
  const inputs = fillMethod(host.method, { rows, allPoints, skipped, link, loader, hasEras, todayCount });
  host.announce(`${WORKING_TITLE}: ${rows.length} accelerators, ${allPoints.length} points, energy against the year each energy began to apply.`);

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
function fillMethod(el, { rows, allPoints, skipped, link, loader, hasEras, todayCount }) {
  const factorRows = Object.entries(ENERGY_SCALE_EV)
    .filter(([unit]) => allPoints.some((point) => point.quantity.unit === unit))
    .map(([unit, ev]) => h('tr', {}, [
      h('th', { scope: 'row' }, unit),
      h('td', { class: 'ch-num' }, `${Number((ev / 1e9).toPrecision(6))} GeV`),
      h('td', { class: 'ch-num' }, String(allPoints.filter((point) => point.quantity.unit === unit).length)),
    ]));

  const fieldTable = dataTable({
    caption: 'For each plotted point: the field its energy comes from, where in the record it is, and which interval gives its year',
    className: 'ch-method-table ef-field-table',
    rows: allPoints,
    columns: [
      { label: 'Accelerator', header: true, cell: (point) => link({ type: 'accelerator', slug: point.machine.slug }, point.machine.name) },
      { label: 'Point', cell: (point) => (point.kind === 'era' ? `Era: ${point.label}` : 'As recorded today, at first operation') },
      { label: 'Field used', cell: (point) => `${fieldName(point.machine)} (${point.machine.collider ? 'collider: √s' : 'not a collider: beam energy'})` },
      { label: 'Where in the record', cell: (point) => point.pointer },
      { label: 'Year taken from', cell: (point) => point.startPointer },
    ],
  });

  const tracks = rows.filter((row) => row.points.filter((point) => point.kind === 'era').length > 1);
  const inputs = lazyInputs(el, {
    id: 'ef-inputs', loader, entries: rows,
    block: (row, sources, prov) => inputBlock(row, sources, prov, link),
  });

  el.replaceChildren(
    h('p', { class: 'ch-method-intro' }, 'The chart plots values the records already hold and computes nothing but a change of unit. Each marker is one energy of one accelerator at one year; the table below says which field and which interval each came from, and “Inputs” gives the quote and the sources behind every one.'),
    h('h3', {}, 'Which energy'),
    h('ul', { class: 'ch-method-list' }, [
      h('li', {}, [h('strong', {}, 'Colliders: √s. '), 'A collider is drawn at its centre-of-mass energy, the record’s `cms_energy`, as a filled marker. A collider whose record has no sourced √s is not plotted: the chart does not derive one from the beam energies.']),
      h('li', {}, [h('strong', {}, 'Everything else: beam energy. '), 'A fixed-target accelerator, a synchrotron, a booster or a linac is drawn at the record’s `beam_energy`, as a hollow marker. For a beam on a fixed target, √s is far smaller than the beam energy, so a hollow marker is not comparable with a filled one on the same axis; this is a Livingston chart of what each machine delivers, not of what a collision can reach.']),
    ]),
    h('h3', {}, 'One point per era'),
    h('p', {}, `A machine is drawn at every era its record gives an energy for: an interval of status “active” (a run, a phase, or a plain interval) whose own \`specs\` carry the field (amendments A3 and A30: earlier eras live in intervals with their own specs). The point stands at the start year of that interval, and the points of one machine are joined by a thin line in its colour. The first point is the machine’s first operation, the start of its first active interval; a planned date is not a start. ${tracks.length ? `Machines with more than one era here: ${tracks.map((row) => `${row.label} (${row.points.filter((point) => point.kind === 'era').map((point) => `${energyText(point.gev)} ${point.year}`).join(', ')})`).join('; ')}.` : 'No machine in the data loaded here has more than one era with an energy.'}`),
    h('h3', {}, 'Energy as recorded today'),
    h('p', {}, hasEras || todayCount
      ? `${todayCount} point${todayCount === 1 ? ' is' : 's are'} dashed. Where no era dates an energy to a machine’s start, the record’s headline energy (\`specs\`: the highest energy the machine delivers, extraction or design) is drawn at the year the machine began operating, with a dashed ring, and the point says: “${AS_RECORDED_TODAY}” A machine often began at a lower energy and was upgraded; the Atlas does not hold that earlier energy as a dated value, and the chart does not guess it. The same point is added ahead of a track whose first era starts after the first operation.`
      : 'No point is dashed here.'),
    h('h3', {}, 'A headline value no era dates'),
    h('p', {}, 'Where a machine has eras and its headline energy is not one of them (a design energy, or the energy after a later upgrade), the headline value is not drawn: nothing dates it. It is footnoted (†) under the chart and listed in the table’s “Also recorded” column.'),
    h('h3', {}, 'Colour and shape'),
    h('p', {}, 'A marker’s colour and shape come from the first particle its record lists: electrons and positrons, protons (antiprotons and H⁻, which is stripped to protons, included), or ions (deuterons and alpha particles included). The table lists every particle a record gives; colour is never the only cue, because the shape differs too.'),
    h('h3', {}, 'The timeline'),
    h('p', {}, 'The timeline position fades the points whose year is after the selected year (or after the end of a selected range) and draws a line at the year; a machine’s name fades only when all of its points have. A machine is not moved to the energy it had in that year: its earlier eras are the points before it.'),
    h('h3', {}, 'Unit conversion'),
    h('p', {}, [
      'Energies are recorded in the unit their source uses and drawn in GeV. The factors below are ',
      h('strong', {}, 'copied from UNIT_SCALE[‘energy’] in hepgraph/atlas/schema.py'),
      ' (eV is the base unit there; the table divides by 10⁹ to give GeV). A check in the test suite fails if the two tables part. A value in a unit the table does not list, or a range with no single value (an energy written as 0.8 to 1 GeV), is not plotted.',
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
    h('p', {}, 'Each machine with the quote its energies and its start were read from, the place in the source, how sure the record is, and the sources behind them.'),
    inputs.holder,
  );
  return inputs;
}

/** One accelerator's inputs: each point's energy, the interval each year comes from, and the headline value where it was footnoted. */
function inputBlock(row, sources, prov, link) {
  const record = row.accelerator;
  const pointers = [];
  for (const point of row.points) pointers.push(point.pointer, point.startPointer);
  if (row.other) pointers.push(row.other.pointer);
  const items = [...new Set(pointers)].map((pointer) => claimItem(prov, sources, record, pointer)).filter(Boolean);
  return h('details', { class: 'ch-input' }, [
    h('summary', {}, `${row.name} — ${row.points.map((point) => `${quantityText(point.quantity)} (${yearText(point)})`).join(', ')}`),
    h('p', { class: 'ch-input-line' }, [
      `Drawn at ${row.points.map((point) => `${energyText(point.gev)}${point.kind === 'today' ? ' as recorded today' : ''} in ${yearText(point)}`).join('; ')} (${fieldName(row)}). `,
      link({ type: 'accelerator', slug: row.slug }, 'Open the accelerator record'), '.',
    ]),
    items.length ? h('ul', { class: 'source-list' }, items) : h('p', { class: 'empty-note' }, 'No source is recorded for these values.'),
  ]);
}
