import { evidenceFor } from './result-evidence-data.js';

function h(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
  for (const child of [].concat(children)) if (child != null) node.append(child instanceof Node ? child : document.createTextNode(child));
  return node;
}
const source = (item) => h('a', { class: 'evidence-source', href: item.url, target: '_blank', rel: 'noopener' }, item.label);

let readerSerial = 0;

/** Optional reading aid: scientific responses, quantities and sources come from reviewed data. */
function renderChannelReader(spec) {
  if (!spec?.channels?.length || !spec.flavors?.length) return null;
  const prefix = `evidence-channels-${++readerSerial}`;
  const controls = h('fieldset', { class:'evidence-channel-controls', 'aria-describedby':`${prefix}-intro` }, h('legend', {}, 'Choose a reaction'));
  const name = h('h5', { class:'evidence-channel-name' });
  const reaction = h('p', { class:'evidence-channel-reaction' });
  const sensitivity = h('p', { class:'evidence-channel-sensitivity' });
  const signal = h('p', { class:'evidence-channel-signal' });
  const status = h('p', { class:'visually-hidden evidence-channel-status', role:'status', 'aria-live':'polite', 'aria-atomic':'true' });
  const responses = spec.flavors.map(flavor => {
    const state = h('span', { class:'evidence-flavor-state' });
    const node = h('li', { class:'evidence-flavor' }, [h('strong', {}, flavor.label), state]);
    return { flavor, state, node };
  });
  const rows = spec.channels.map(channel => {
    const selected = h('span', { class:'evidence-channel-selection' }, 'Selected reaction');
    const node = h('tr', { 'data-channel':channel.id }, [
      h('th', { scope:'row' }, [channel.label, selected]),
      h('td', {}, [h('strong', {}, channel.flux.value),
        h('span', { class:'evidence-channel-error' }, `Stat. ${channel.flux.stat}`),
        h('span', { class:'evidence-channel-error' }, `Syst. ${channel.flux.syst}`)]),
    ]);
    return { channel, selected, node };
  });
  function show(channel, announce = false) {
    name.textContent = channel.label;
    reaction.textContent = channel.reaction;
    sensitivity.textContent = channel.sensitivity;
    signal.textContent = `Signal: ${channel.signal}`;
    const accepts = new Set(channel.probes);
    for (const { flavor, state, node } of responses) {
      const probed = accepts.has(flavor.id);
      node.dataset.probed = String(probed);
      state.textContent = probed ? '✓ Probed' : '— Not probed';
    }
    for (const row of rows) {
      const on = row.channel.id === channel.id;
      row.selected.hidden = !on;
      row.node.classList.toggle('is-selected', on);
    }
    if (announce) status.textContent = `${channel.label}. ${channel.sensitivity}`;
  }
  for (const [index,channel] of spec.channels.entries()) {
    const input = h('input', { type:'radio', name:prefix, id:`${prefix}-${channel.id}`, value:channel.id, 'aria-controls':`${prefix}-response` });
    input.checked = index === 0;
    input.addEventListener('change', () => { if (input.checked) show(channel, true); });
    controls.append(h('label', { for:input.id }, [input,h('span', {}, channel.label)]));
  }
  show(spec.channels[0]);
  const citation = item => item ? h('p', { class:'source-meta' }, [source(item), h('span', {}, ` · ${item.locator}`)]) : null;
  return h('section', { class:'evidence-channel-reader', 'aria-labelledby':`${prefix}-title` }, [
    h('h4', { id:`${prefix}-title` }, spec.title),
    h('p', { id:`${prefix}-intro` }, spec.intro), controls, status,
    h('div', { id:`${prefix}-response` }, [name,reaction,sensitivity,
      h('ul', { class:'evidence-flavors', 'aria-label':'Active-flavor sensitivity' }, responses.map(r=>r.node)), signal]),
    citation(spec.reactionSource),
    h('p', { class:'evidence-caveat' }, spec.assumption),
    h('table', { class:'evidence-channel-fluxes' }, [
      h('caption', {}, [h('span', {}, `${spec.quantityLabel} · ${spec.units}`), spec.unitsDescription ? h('span', { class:'evidence-channel-units source-meta' }, spec.unitsDescription) : null]),
      h('thead', {}, h('tr', {}, [h('th', { scope:'col' }, 'Reaction'),h('th', { scope:'col' }, 'Reported value and errors')])),
      h('tbody', {}, rows.map(r=>r.node)),
    ]), citation(spec.fluxSource),
  ]);
}

/** Generic display for a reviewed evidence object. Interpretation, definitions,
 * comparison assumptions and conclusions belong to its data, never the display.
 * Only explicitly reviewed pilots receive a card; absent entries stay absent. */
export function renderEvidence(e, linkTo, tourStepLink) {
  if (!e) return null;
  const significance = e.significance;
  const quantities = significance ? [
    significance.observed ? h('div', {}, [h('dt', {}, e.observedLabel || 'Observed in the data'), h('dd', {}, significance.observed)]) : null,
    significance.expected ? h('div', {}, [h('dt', {}, e.expectedLabel || 'Expected'), h('dd', {}, significance.expected)]) : null,
  ] : [];
  const root = h('section', { class: 'result-evidence', 'aria-label': `${e.experiment || 'Result'} evidence trail` }, [
    h('h3', {}, 'Read the evidence'),
    e.paper ? h('p', { class: 'source-meta' }, `Primary paper: ${e.paper}. ${e.context || ''}`) : null,
    e.measurement ? h('h4', {}, 'What was measured') : null,
    e.measurement ? h('p', {}, e.measurement) : null,
    e.mass ? h('p', {}, e.mass) : null,
    renderChannelReader(e.channelReader),
    significance ? h('h4', {}, significance.scope || 'Significance') : null,
    quantities.some(Boolean) ? h('dl', { class: 'evidence-significance' }, quantities) : null,
    significance?.at ? h('p', {}, significance.at) : null,
    ...(e.interpretation || []).map(text => h('p', {}, text)),
    e.definition ? h('details', {}, [h('summary', {}, 'Read the statistical definition in the paper'), source(e.definition)]) : null,
    significance?.note ? h('p', { class: 'evidence-caveat evidence-significance-note' }, significance.note) : null,
    e.evidence?.length ? h('h4', {}, 'Follow the claim to the paper') : null,
    e.evidence?.length ? h('ol', { class: 'evidence-items' }, e.evidence.map(item => h('li', {}, [
      source(item), h('p', { class: 'source-meta' }, item.locator), h('p', {}, item.supports),
    ]))) : null,
    e.conclusion ? h('p', { class: 'evidence-caveat' }, e.conclusion) : null,
    e.companion && linkTo ? linkTo({ type: 'result', slug: e.companion.slug }, e.companion.label) : null,
    e.nextQuestion && tourStepLink ? h('div', { class: 'evidence-next-question' }, [
      h('h4', {}, e.nextQuestion.title),
      h('p', {}, e.nextQuestion.description),
      tourStepLink(e.nextQuestion.tour, e.nextQuestion.step, e.nextQuestion.label),
    ]) : null,
  ]);
  root.addEventListener('keydown', event => {
    const blank = document.getElementById('tour-blank');
    if ((!blank || blank.hidden) && ['Enter',' '].includes(event.key) && event.target.closest('button,a,summary')) event.stopPropagation();
  });
  return root;
}

export function renderEvidenceTrail(resultId, linkTo, tourStepLink) {
  return renderEvidence(evidenceFor(resultId), linkTo, tourStepLink);
}
