// underground.js — "Going underground": every underground laboratory site that records both a
// depth in m.w.e. and a cosmic-ray muon flux, as depth (x) against flux (y, logarithmic).
//
//   #/view/underground
//
// The chart toolkit is chart.js; which sites qualify, the unit conversion and the labels are
// underground-rows.js (pure, shared with the panels and the search). This file puts them on the
// page, with the table of the same numbers, the sites that have a depth but no flux, and the
// "Inputs and method" disclosure. Mounted by host.js through registry.js.

import { createChart, dataTable, h } from './chart.js';
import {
  MUON_FLUX_SCALE, WORKING_TITLE, depthOnlyRows, fluxRange, fluxText, isApproximate, sciText, undergroundData,
} from './underground-rows.js';
import { claimItem, lazyInputs } from './chart-inputs.js';

const DECADES = (ratio) => Math.floor(Math.log10(ratio));

export function mount(ctx) {
  const { atlas, host, loader } = ctx;
  host.setTitle(WORKING_TITLE);
  const data = undergroundData(atlas);
  if (!data.rows.length) {
    host.fail('The data loaded here records no muon flux for any underground laboratory, so there is nothing to plot. '
      + 'That says nothing about the muon flux itself: only that this Atlas build holds no value for it.');
    return null;
  }

  let destroyed = false;
  let chart = null;
  let inputs = null;
  const details = host.method.closest('details');

  const link = (route, text) => {
    const a = h('a', { class: 'entity-link', href: `#/${route.type}/${route.slug}` }, text);
    a.addEventListener('click', (event) => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      ctx.navigate({ entity: route });
    });
    return a;
  };

  async function build() {
    let prov;
    try {
      prov = await loader.getProvenance();
    } catch (error) {
      if (destroyed) return;
      host.fail(`The records behind the chart could not be loaded: ${error.message}. Nothing is drawn without them: `
        + 'which values are approximate is read from them.', {
        retry: () => {
          host.body.replaceChildren(h('p', { class: 'loading-note', role: 'status' }, 'Loading…'));
          build();
        },
      });
      return;
    }
    if (destroyed) return;
    if (details) details.hidden = false;
    draw(prov);
  }

  function draw(prov) {
    const { rows, skipped } = data;
    const claimOf = (row, pointer) => (prov[row.id] || {})[pointer] || null;
    const entries = rows.map((row) => ({
      row,
      hollow: isApproximate(row.fluxQuantity, claimOf(row, '/muon_flux')),
      range: fluxRange(row.fluxQuantity),
    }));
    const byId = new Map(entries.map((entry) => [entry.row.id, entry]));
    const hasHollow = entries.some((entry) => entry.hollow);

    // ---- the heading's second line and the sentence a newcomer can read
    const fluxes = rows.map((row) => row.flux);
    const top = rows.find((row) => row.flux === Math.max(...fluxes));
    const bottom = rows.find((row) => row.flux === Math.min(...fluxes));
    const decades = DECADES(top.flux / bottom.flux);
    host.setSubtitle(`${rows.length} laboratory sites · depth in metres of water equivalent against cosmic-ray muon flux`);
    const lede = h('p', { class: 'ch-lede' }, [
      'Rock stops cosmic-ray muons, so the deeper a laboratory, the quieter it is. Each marker is one site: the rock above it, in metres of water equivalent (m.w.e.), across; the muon flux that still reaches it, up. ',
      `The fluxes recorded here span more than ${decades} orders of magnitude, from ${fluxText(top.flux)} at ${top.label} (${top.depthMwe} m.w.e.) to ${fluxText(bottom.flux)} at ${bottom.label} (${bottom.depthMwe} m.w.e.).`,
    ]);

    // ---- the chart
    const depths = rows.map((row) => row.depthMwe);
    const xLo = Math.floor((Math.min(...depths) - 250) / 500) * 500;
    const xHi = Math.ceil((Math.max(...depths) + 250) / 500) * 500;
    const yLo = 10 ** Math.floor(Math.log10(Math.min(...fluxes) * 0.9));
    const yHi = 10 ** Math.ceil(Math.log10(Math.max(...fluxes) * 1.1));
    const chartHost = h('div', { class: 'ch-chart', id: 'ug-chart' });
    const points = entries.map(({ row, hollow, range }) => ({
      id: row.id,
      x: row.depthMwe,
      y: row.flux,
      yErr: range,
      label: row.label,
      shape: 'circle',
      tone: 'measured',
      hollow,
      href: `#/site/${row.slug}`,
      aria: `${row.label}: ${row.depthQuantity.display}; muon flux ${row.fluxQuantity.display}, which is ${fluxText(row.flux)}${hollow ? '; approximate or simulated' : ''}. Opens the site record.`,
      tip: [row.site.name, `Depth: ${row.depthQuantity.display}`, `Flux: ${row.fluxQuantity.display}`, `= ${fluxText(row.flux)}`, hollow ? 'Approximate or simulated (hollow marker)' : null].filter(Boolean),
    }));
    const legendItems = [{ shape: 'circle', tone: 'measured', text: 'Measured, as the source publishes it' }];
    if (hasHollow) legendItems.push({ shape: 'circle', tone: 'measured', hollow: true, text: 'Approximate, or a simulation rather than a measurement' });

    chart = createChart(chartHost, {
      id: 'underground',
      title: 'Cosmic-ray muon flux against depth for underground laboratory sites',
      description: () => `${rows.length} sites, depth in metres of water equivalent from ${xLo} to ${xHi} on a linear axis, muon flux in cm^-2 s^-1 from ${yLo} to ${yHi} on a logarithmic axis. `
        + `${rows.map((row) => `${row.label}: ${row.depthMwe} m.w.e., ${fluxText(row.flux)}`).join('; ')}. The same numbers are in the table below the chart.`,
      x: { kind: 'linear', domain: [xLo, xHi], label: 'Depth (m.w.e.)' },
      y: { kind: 'log', domain: [yLo, yHi], label: 'Muon flux (cm⁻² s⁻¹)' },
      points,
      legend: [{ title: 'Markers', items: legendItems }],
      onOpen: (point) => ctx.navigate({ entity: { type: 'site', slug: byId.get(point.id).row.slug } }),
    });
    const stacks = stackedRows(rows);
    const figure = h('div', { class: 'ch-block ug-figure' }, [
      chartHost,
      h('p', { class: 'ch-caption' }, [
        h('strong', {}, 'Flux is on a logarithmic axis. '),
        'Each marker opens its site. ',
        hasHollow ? 'A hollow marker is approximate or simulated. ' : '',
        'No error bars are drawn: the records write their uncertainty as text, not numbers (see Inputs and method). ',
        stacks.length ? `${stacks.map((s) => s.labels.join(', ')).join('; ')} share one depth and nearly one flux, so their markers overlap and their labels are stacked in the order of the markers. ` : '',
      ]),
    ]);
    // The accessible name of the chart sits on the SVG; the figure itself is a plain block so it is not announced twice.

    // ---- depth known, flux not recorded
    const depthOnly = depthOnlyRows(atlas);
    const depthSection = h('section', { class: 'ch-block ug-depth-only', 'aria-labelledby': 'ug-depth-h' }, [
      h('h3', { id: 'ug-depth-h' }, 'Depth known, flux not recorded'),
      depthOnly.length
        ? h('p', {}, 'These sites record a depth in m.w.e. but no cosmic-ray muon flux, so they have no marker. A site missing here is a gap in the Atlas, not a measurement of zero or of the surface rate.')
        : h('p', { class: 'empty-note' }, 'Every site with a recorded depth in m.w.e. also records a flux.'),
      depthOnly.length ? h('ul', { class: 'entity-list ug-depth-list' }, depthOnly.map((row) => h('li', { class: 'entity-link-with-meta' }, [
        link({ type: 'site', slug: row.slug }, row.site.name),
        ` — ${row.depthQuantity.display}`,
        row.facility ? [' · ', link({ type: 'facility', slug: row.facility.id.split(':')[1] }, row.facility.name)] : null,
      ].flat()))) : null,
      skipped.length ? h('p', { class: 'ch-note' }, `Not plotted although they record a muon flux: ${skipped.map((entry) => `${entry.site.name} (${entry.reason})`).join('; ')}.`) : null,
    ]);

    // ---- the same rows as a table
    const table = dataTable({
      caption: 'The plotted sites, in order of depth: the values as recorded, and the flux in cm⁻² s⁻¹ as plotted',
      className: 'ug-table',
      rows: entries,
      rowId: (entry) => entry.row.id,
      columns: [
        { label: 'Site', header: true, cell: (entry) => link({ type: 'site', slug: entry.row.slug }, entry.row.site.name) },
        { label: 'Laboratory', cell: (entry) => (entry.row.facility ? link({ type: 'facility', slug: entry.row.facility.id.split(':')[1] }, entry.row.facility.name) : '') },
        { label: 'Depth (m.w.e.)', numeric: true, cell: (entry) => entry.row.depthQuantity.display },
        { label: 'Flux as recorded', cell: (entry) => entry.row.fluxQuantity.display },
        { label: 'Flux (cm⁻² s⁻¹)', numeric: true, cell: (entry) => fluxText(entry.row.flux) },
        { label: 'Marker', cell: (entry) => (entry.hollow ? 'Approximate or simulated (hollow)' : 'Measured (filled)') },
      ],
    });
    host.body.replaceChildren(lede, figure, depthSection, h('div', { class: 'ch-block' }, table));

    host.setExporter(() => chart.exportFigures());
    inputs = fillMethod(host.method, { rows, entries, link, loader, prov });
    host.announce(`${WORKING_TITLE}: ${rows.length} laboratory sites, depth in metres of water equivalent against muon flux.`);
  }

  build();

  return {
    update() { /* nothing here depends on the year */ },
    destroy() {
      destroyed = true;
      if (chart) chart.destroy();
      if (inputs) inputs.dispose();
    },
  };
}

/** Groups of rows of one facility with one depth: their markers stand in a column. */
function stackedRows(rows) {
  const groups = new Map();
  for (const row of rows) {
    const key = `${row.site.facility_id}|${row.depthMwe}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(row);
  }
  return [...groups.values()].filter((group) => group.length > 1).map((group) => {
    const fluxes = group.map((row) => row.flux);
    return { labels: group.map((row) => row.label).sort(), spread: (Math.max(...fluxes) - Math.min(...fluxes)) / Math.min(...fluxes) };
  });
}

// ----------------------------------------------------------- the method disclosure
function fillMethod(el, { rows, entries, link, loader, prov }) {
  const factorText = (factor) => {
    if (factor === 1) return '1';
    const exponent = Math.floor(Math.log10(factor));
    const mantissa = factor / 10 ** exponent;
    return `${Number(mantissa.toPrecision(4))} × 10${String(exponent).replace(/[0-9-]/g, (c) => '⁰¹²³⁴⁵⁶⁷⁸⁹⁻'['0123456789-'.indexOf(c)])}`;
  };
  const unitRows = Object.entries(MUON_FLUX_SCALE).map(([unit, factor]) => {
    const users = rows.filter((row) => row.fluxQuantity.unit === unit);
    const example = users[0];
    return h('tr', {}, [
      h('th', { scope: 'row' }, unit.replace('^-2', '⁻²').replace('^-1', '⁻¹')),
      h('td', { class: 'ch-num' }, factorText(factor)),
      h('td', {}, users.length ? `${users.length} site${users.length === 1 ? '' : 's'}` : 'none'),
      h('td', {}, example ? `${example.label}: ${sciText(example.fluxQuantity.value)} ${example.fluxQuantity.unit.replace('^-2', '⁻²').replace('^-1', '⁻¹')} × ${factorText(factor)} = ${fluxText(example.flux)}` : ''),
    ]);
  });

  const groups = stackedRows(rows);
  const inputs = lazyInputs(el, {
    id: 'ug-inputs', loader, entries, block: (entry, sources) => inputBlock(entry, prov, sources, link),
  });
  el.replaceChildren(
    h('p', { class: 'ch-method-intro' }, [
      'The chart plots two recorded values for each site and computes nothing but a change of unit. Every value, with its quote, its place in the source and the sources behind it, is listed under “Inputs” below; the same numbers are in the table under the chart.',
    ]),
    h('h3', {}, 'What is plotted'),
    h('ul', { class: 'ch-method-list' }, [
      h('li', {}, [h('strong', {}, 'Depth, horizontal axis, linear. '), 'The site’s recorded depth in metres of water equivalent (m.w.e.): the rock overburden written as the thickness of water with the same mass per unit area, so rock of density ρ g/cm³ and thickness d metres is about ρ·d m.w.e. A site records one figure. For a laboratory under a mountain it is a vertical or an average depth, as that record’s note says, and the flux at a given figure is higher than under a flat overburden of the same depth, because muons also arrive through the thinner rock of the flanks. Do not read a curve through the points.']),
      h('li', {}, [h('strong', {}, 'Flux, vertical axis, logarithmic. '), 'The site’s recorded cosmic-ray muon flux: the total number of muons per unit area per second, summed over all arrival directions (amendment A27). Per each record’s note it is the flux through a horizontal surface (most records), through the cross-section of a sphere, or a detector’s rate divided by its acceptance over all angles; the note says which, with the energy threshold, the hall and the detector when the source gives them, and some papers state no reference surface. The choice changes a flux by a factor of order one, which a logarithmic axis of four decades hides. The vertical intensity per steradian that some papers quote is not a flux and is not plotted.']),
    ]),
    h('h3', {}, 'Unit conversion'),
    h('p', {}, [
      'The bundle keeps every flux in the unit its source uses. The view converts each to cm⁻² s⁻¹ before plotting with the factors below, which are ',
      h('strong', {}, 'copied from UNIT_SCALE[‘muon_flux’] in hepgraph/atlas/schema.py'),
      ' (amendment A27), the scale the validator uses: 1 m⁻² is 10⁻⁴ cm⁻², and one day is 86 400 s. A check in the test suite fails if the two tables part. A flux in a unit that table does not list is not plotted and is named under the chart.',
    ]),
    h('div', { class: 'ch-table-scroll' }, h('table', { class: 'ch-table ch-method-table' }, [
      h('caption', {}, 'Factors to cm⁻² s⁻¹, and one worked example for each unit in use'),
      h('thead', {}, h('tr', {}, ['Recorded unit', 'Factor', 'Used by', 'Example'].map((label) => h('th', { scope: 'col' }, label)))),
      h('tbody', {}, unitRows),
    ])),
    h('h3', {}, 'Uncertainty and error bars'),
    h('p', {}, 'Every record writes the uncertainty of its flux only in its display text (for example “± 0.09 syst.”), not as numbers, and the chart does not read numbers out of prose. So it draws no error bars; the written uncertainty is beside every value in the table and in the record. The chart does draw a bar for any record that carries a numeric minimum and maximum around its value, converted with the same factors; none does today. On an axis spanning four decades, an uncertainty of tens of per cent is about the width of one marker.'),
    h('h3', {}, 'Markers'),
    h('p', {}, 'A filled marker is a value its source gives as a measurement. A hollow marker is a record marked approximate (its approximate flag, or a confidence of “approximate” or “uncertain” in the provenance), which includes a simulated expectation: no measurement stands behind it, and its record says so.'),
    groups.length ? h('h3', {}, 'Several sites at one laboratory') : null,
    groups.length ? h('p', {}, groups.map((group) => `${group.labels.join(', ')} record the same depth and fluxes within ${Math.max(1, Math.round(group.spread * 100))} % of one another, so the markers overlap; each is labelled and each opens its own site. `).join('')) : null,
    h('h3', {}, 'Inputs'),
    h('p', {}, 'Each value below with the quote it was read from, the place in the source, how sure the record is, and the sources it rests on. The note under a label is the record\u2019s own: where a source defines its flux, its detector and its energy threshold.'),
    inputs.holder,
  );
  return inputs;
}

/** One site's inputs: the depth and the flux, each with its note, quote, place in the source and sources. */
function inputBlock(entry, prov, sources, link) {
  const { row } = entry;
  const depth = claimItem(prov, sources, row.site, '/depth_mwe');
  const flux = claimItem(prov, sources, row.site, '/muon_flux');
  return h('details', { class: 'ch-input' }, [
    h('summary', {}, `${row.site.name} — ${row.depthQuantity.display}; ${row.fluxQuantity.display}`),
    h('p', { class: 'ch-input-line' }, [
      'Plotted at ', h('strong', {}, `${row.depthMwe} m.w.e.`), ' and ', h('strong', {}, fluxText(row.flux)),
      row.fluxQuantity.unit === 'cm^-2 s^-1' ? ' (already in that unit)' : ` (recorded as ${sciText(row.fluxQuantity.value)} ${row.fluxQuantity.unit.replace('^-2', '⁻²').replace('^-1', '⁻¹')})`,
      '. ', link({ type: 'site', slug: row.slug }, 'Open the site record'), '.',
    ]),
    h('ul', { class: 'source-list' }, [depth, flux].filter(Boolean)),
    !depth && !flux ? h('p', { class: 'empty-note' }, 'No source is recorded for these values.') : null,
  ]);
}
