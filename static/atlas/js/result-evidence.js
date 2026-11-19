import { evidenceFor } from './result-evidence-data.js';

function h(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
  for (const child of [].concat(children)) if (child != null) node.append(child instanceof Node ? child : document.createTextNode(child));
  return node;
}
const source = (item) => h('a', { class: 'evidence-source', href: item.url, target: '_blank', rel: 'noopener' }, item.label);

/** Generic display for a reviewed evidence object. Interpretation, definitions,
 * comparison assumptions and conclusions belong to its data, never the display.
 * The shipped registry intentionally contains only the two Higgs pilot entries. */
export function renderEvidence(e, linkTo, tourStepLink) {
  if (!e) return null;
  const significance = e.significance;
  const quantities = significance ? [
    significance.observed ? h('div', {}, [h('dt', {}, e.observedLabel || 'Observed in the data'), h('dd', {}, significance.observed)]) : null,
    significance.expected ? h('div', {}, [h('dt', {}, e.expectedLabel || 'Expected'), h('dd', {}, significance.expected)]) : null,
  ] : [];
  return h('section', { class: 'result-evidence', 'aria-label': `${e.experiment || 'Result'} evidence trail` }, [
    h('h3', {}, 'Read the evidence'),
    e.paper ? h('p', { class: 'source-meta' }, `Primary paper: ${e.paper}. ${e.context || ''}`) : null,
    e.measurement ? h('h4', {}, 'What was measured') : null,
    e.measurement ? h('p', {}, e.measurement) : null,
    e.mass ? h('p', {}, e.mass) : null,
    significance ? h('h4', {}, significance.scope || 'Significance') : null,
    quantities.some(Boolean) ? h('dl', { class: 'evidence-significance' }, quantities) : null,
    significance?.at ? h('p', {}, significance.at) : null,
    ...(e.interpretation || []).map(text => h('p', {}, text)),
    e.definition ? h('details', {}, [h('summary', {}, 'Read the statistical definition in the paper'), source(e.definition)]) : null,
    significance?.note ? h('p', { class: 'evidence-caveat' }, significance.note) : null,
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
}

export function renderEvidenceTrail(resultId, linkTo, tourStepLink) {
  return renderEvidence(evidenceFor(resultId), linkTo, tourStepLink);
}
