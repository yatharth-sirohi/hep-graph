// chart-inputs.js — the "Inputs" list at the end of a chart's "Inputs and method": one disclosure per
// plotted record, with the quote, the place in the source, the confidence and the sources behind each
// value it rests on. The sources bundle (a few hundred kB) is fetched only when the reader first opens
// the disclosure, never to draw the chart.

import { h } from './chart.js';
import * as provenance from '../provenance.js';

/**
 * One claim, as the panels' Sources disclosure shows it, with the record's own `note` under its label
 * (the note is where a source's definitions and caveats are written). `pointer` is a JSON pointer into
 * the record, as provenance.json keys it (`/muon_flux`, `/intervals/5/specs/cms_energy`). Null when the
 * record has no claim there or no source.
 */
export function claimItem(prov, sources, record, pointer) {
  const claim = (prov[record.id] || {})[pointer];
  if (!claim) return null;
  const group = provenance.renderClaimItems({ [pointer]: claim }, sources, record)[0] || null;
  if (group && claim.note) {
    const note = h('div', { class: 'ch-claim-note' }, [h('span', { class: 'claim-locator-label' }, 'Note: '), claim.note]);
    const label = group.querySelector('.claim-label');
    if (label) label.after(note); else group.prepend(note);
  }
  return group;
}

/**
 * The list's container, ready to be placed in the method. `block(entry, sources, provenance)` builds one record's
 * disclosure. The sources are loaded when the enclosing <details> is first opened (at once if it already
 * is), with a Retry when they cannot be loaded; a failure is said, never an empty list.
 */
export function lazyInputs(method, { id, loader, entries, block }) {
  const holder = h('div', { class: 'ch-inputs', id, 'data-state': 'idle' },
    h('p', { class: 'loading-note' }, 'Open this section to load the sources of every value.'));
  const details = method.closest('details');
  const render = async () => {
    holder.dataset.state = 'loading';
    holder.replaceChildren(h('p', { class: 'loading-note', role: 'status' }, 'Loading the sources…'));
    try {
      const [sources, prov] = await Promise.all([loader.getSources(), loader.getProvenance()]);
      if (!holder.isConnected) return;
      holder.replaceChildren(...entries.map((entry) => block(entry, sources, prov)));
      holder.dataset.state = 'ready';
    } catch (error) {
      if (!holder.isConnected) return;
      const retry = h('button', { type: 'button', class: 'text-btn' }, 'Retry');
      retry.addEventListener('click', render);
      holder.replaceChildren(h('p', { class: 'error-note', role: 'alert' }, `Could not load the sources: ${error.message}. `), retry);
      holder.dataset.state = 'idle';
    }
  };
  const onToggle = () => {
    if (details && details.open && holder.dataset.state === 'idle') render();
  };
  if (details) {
    details.addEventListener('toggle', onToggle);
    if (details.open) window.setTimeout(onToggle, 0);
  }
  return { holder, dispose: () => { if (details) details.removeEventListener('toggle', onToggle); } };
}
