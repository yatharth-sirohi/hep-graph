import { patchQuietly } from '../state.js';
import { limitComparison, normaliseLimitProbe } from './limit-probe-model.js';

const PRIMARY = 'https://arxiv.org/pdf/2410.17036v3#page=8';
const ASSUMPTIONS = 'This comparison applies only under this paper’s spin-independent WIMP–nucleon, astrophysical and statistical assumptions. It does not test every dark-matter model.';
const INTERPRETATIONS = {
  above: 'Excluded at 90% CL by this result under its assumptions: this hypothetical cross section is above the reported upper limit at this exact mass.',
  below: 'Not excluded by this result: this hypothetical cross section is below its limit at this exact mass. This is not a detection or evidence that the model is true.',
  boundary: 'On the reported limit boundary. Equality with a stored or rounded upper limit is not a separate detection or a probability that the model is true.',
};
function h(tag, attrs = {}, children = []) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) el.setAttribute(key, value);
  if (tag === 'button') el.classList.add('text-btn');
  for (const child of [].concat(children)) el.append(child instanceof Node ? child : document.createTextNode(String(child)));
  return el;
}
const external = (url, label) => h('a', { href:url, target:'_blank', rel:'noopener' }, label);
const sci = value => Number(value).toExponential(3).replace('e', ' × 10^');

/** Pilot using an already loaded, reviewed limit row. Predictions remain visit-local. */
export function createLimitProbe({ row, value, onChange, onLocate, host }) {
  const defaultMass = row.units_check.mass;
  let setup = limitComparison(row, defaultMass, 10);
  let active = false, destroyed = false;
  const root = h('details', { class:'limit-probe' });
  const summary = h('summary', {}, 'Try a model point: what does a limit exclude?');
  const mass = h('select', { id:'limit-probe-mass' }, row.points.map(([x]) => h('option', { value:String(x) }, `${x} GeV/c²`)));
  const factor = h('fieldset', { id:'limit-probe-factor' }, h('legend', {}, 'Hypothetical cross section'));
  for (const [value,label] of [['.1','0.1 × the limit'],['1','1 × the limit'],['10','10 × the limit']]) {
    const input = h('input', { type:'radio', name:'limit-probe-multiplier', value });
    input.addEventListener('change', accept);
    factor.append(h('label', {}, [input,h('span', {}, label)]));
  }
  const previous = h('button', { type:'button' }, 'Previous published mass');
  const next = h('button', { type:'button' }, 'Next published mass');
  const stepMass = direction => {
    const at = row.points.findIndex(point => point[0] === setup.massGeV);
    const point = row.points[at + direction];
    if (point) { mass.value = String(point[0]); accept(); }
  };
  previous.addEventListener('click', () => stepMass(-1));next.addEventListener('click', () => stepMass(1));
  const notice = h('p', { class:'limit-probe-notice', role:'status' });notice.hidden = true;
  const published = h('output', { id:'limit-probe-published' });
  const hypothetical = h('output', { id:'limit-probe-model' });
  const choices = h('fieldset', { class:'limit-probe-choices' }, h('legend', {}, 'Predict: what can this result say about the hypothetical point?'));
  const check = h('button', { type:'button', id:'limit-probe-check' }, 'Check prediction');check.disabled = true;
  const feedback = h('p', { class:'limit-probe-feedback', role:'status', 'aria-live':'polite', 'aria-atomic':'true' });feedback.hidden = true;
  for (const [id, label] of [['above','Excluded under the paper’s assumptions'],['below','Not excluded by this result'],['boundary','On the reported boundary']]) {
    const input = h('input', { type:'radio', name:'limit-probe-prediction', value:id });
    input.addEventListener('change', () => { feedback.hidden = true; feedback.textContent = ''; check.disabled = false; });
    choices.append(h('label', {}, [input,h('span', {}, label)]));
  }
  function clearPrediction() {
    for (const input of choices.querySelectorAll('input')) input.checked = false;
    check.disabled = true;feedback.hidden = true;feedback.textContent = '';
  }
  function render() {
    mass.value = String(setup.massGeV);
    for (const input of factor.querySelectorAll('input')) input.checked = Number(input.value) === setup.factor;
    const at = row.points.findIndex(point => point[0] === setup.massGeV);
    previous.disabled = at === 0;next.disabled = at === row.points.length - 1;
    published.textContent = `${sci(setup.limitCm2)} cm² at ${setup.massGeV} GeV/c²`;
    hypothetical.textContent = `${sci(setup.modelCm2)} cm² (${setup.factor} × the limit, same mass)`;
  }
  function persist() { patchQuietly({ wimpProbe:active ? `${setup.massGeV},${setup.factor}` : null });host.exportChanged?.(); }
  function accept() {
    const next = limitComparison(row, Number(mass.value), Number(factor.querySelector('input:checked')?.value));
    if (!next) return;
    setup = next;notice.hidden = true;clearPrediction();render();persist();onChange(setup);
  }
  mass.addEventListener('change', accept);
  check.addEventListener('click', () => {
    const selected = choices.querySelector('input:checked');
    if (!selected) return;
    const supported = selected.value === setup.relation;
    feedback.dataset.outcome = supported ? 'supported' : 'revise';
    feedback.textContent = `${supported ? 'Supported. ' : 'Revise your prediction. '}${INTERPRETATIONS[setup.relation]}`;
    feedback.hidden = false;
  });
  const locate = h('button', { type:'button', class:'limit-probe-locate' }, 'Locate this mass on the chart');
  locate.addEventListener('click', () => onLocate(setup));
  root.append(summary,
    h('p', {}, 'Use one exact published LZ mass point. The triangle is a hypothetical model you set, not an observed event or a measurement.'),
    h('p', { class:'source-meta' }, `${row.label} · observed, power-constrained 90% CL upper limit. Expected sensitivity is a different quantity.`),
    notice,
    h('div', { class:'limit-probe-controls' }, [h('div', {}, [h('label', { for:mass.id }, ['Published mass',mass]),h('div', { class:'limit-probe-mass-steps' }, [previous,next])]),factor]),
    h('dl', { class:'limit-probe-values' }, [h('dt', {}, '○ Published limit'),h('dd', {}, published),h('dt', {}, '△ Hypothetical model'),h('dd', {}, hypothetical)]),
    locate,choices,check,feedback,
    h('details', { class:'limit-probe-method' }, [h('summary', {}, 'Assumptions and sources'),
      h('p', {}, 'Hypothetical cross section = chosen multiplier × the stored published upper limit at the selected mass. The mass must be a table row: no interpolation or fit is made.'),
      h('p', {}, ASSUMPTIONS),
      h('p', {}, 'A 90% confidence-level upper limit is not a 90% probability that a particle exists or that a particular model is true. This exercise reads the published boundary; it does not calculate a new confidence level, event rate or discovery significance.'),
      h('p', {}, 'Screen values are rounded to four significant figures; export notes retain the full stored and calculated numbers. The paper’s Figure 5 distinguishes the solid power-constrained limit from the expected sensitivity and discovery potential. The source table’s “limit” column is used here; “limit_unconstr” and expected-sensitivity columns are not used.'),
      external(PRIMARY, 'LZ primary paper · Figure 5 and preceding paragraph · PDF page 8'),
      external(`https://doi.org/${row.hepdata.table_doi}`, 'HEPData · SI cross section · version 2 · mass / limit columns'),
    ]));
  function update(nextValue) {
    const normalised = normaliseLimitProbe(nextValue);
    const nextActive = !!normalised;
    let next = setup;
    let missing = false;
    if (normalised) {
      const [m,f] = normalised.split(',').map(Number);
      next = limitComparison(row,m,f);
      if (!next) { next = limitComparison(row,defaultMass,10);missing = true; }
    }
    const changed = missing || nextActive !== active || next.massGeV !== setup.massGeV || next.factor !== setup.factor;
    setup = next;active = nextActive;root.open = active;
    notice.hidden = !missing;
    notice.textContent = missing ? `The requested mass is not a stored LZ table point. Showing the published ${defaultMass} GeV/c² point and 10 × its limit; choose an exact mass below.` : '';
    if (changed) clearPrediction();render();
    if (missing) persist();
    if (changed) onChange(active ? setup : null);
  }
  // Initial setup must not call the parent while its view is being constructed.
  const initial = normaliseLimitProbe(value);
  if (initial) {
    const [m,f] = initial.split(',').map(Number);
    const requested = limitComparison(row,m,f);
    if (requested) setup = requested;
    else { notice.hidden = false;notice.textContent = `The requested mass is not a stored LZ table point. Showing the published ${defaultMass} GeV/c² point and 10 × its limit; choose an exact mass below.`; }
    active = true;root.open = true;
    if (!requested) persist();
  }
  render();
  root.addEventListener('toggle', () => {
    if (destroyed || root.open === active) return;
    active = root.open;clearPrediction();persist();onChange(active ? setup : null);
  });
  return {
    element:root,
    get comparison() { return active ? setup : null; },
    update,
    exportNotes() {
      return active ? [
        `Interpretation exercise: ○ published LZ limit; △ hypothetical model point (not a measurement). Both at ${setup.massGeV} GeV/c².`,
        `Published observed power-constrained 90% CL upper limit: ${setup.limitCm2} cm². Hypothetical: ${setup.modelCm2} cm² = ${setup.factor} × limit.`,
        INTERPRETATIONS[setup.relation],ASSUMPTIONS,
        `LZ Figure 5 and preceding paragraph, PDF p.8: ${PRIMARY}`,
        `Exact source table: ${row.hepdata.table_doi}, version 2; mass / limit columns. No interpolation.`,
        `Reopen this exercise: ${window.location.href}`,
      ] : [];
    },
    destroy() { destroyed = true; },
  };
}
