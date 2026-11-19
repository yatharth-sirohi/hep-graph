// An interaction in the existing beam view, using its sourced baseline row.
import { allBeamRows } from './beam-rows.js';
import { ENERGY, firstMaximumEnergy, normaliseEnergy, oscillationProbability } from './oscillation-model.js';
import { patchQuietly } from '../state.js';

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
  for (const child of [].concat(children)) if (child != null) node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  return node;
}
function svgEl(tag, attrs = {}, text = '') {
  const node = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
  if (text) node.textContent = text;
  return node;
}
const sourceLink = (href, label) => el('a', { href, target: '_blank', rel: 'noopener' }, label);
const named = { 'j-parc-neutrino': 'T2K', lbnf: 'DUNE / LBNF' };
const decimal = (value, n = 3) => Number(value.toFixed(n)).toString();

export function createOscillationLab(ctx, row) {
  const root = el('section', { class: 'osc-lab', 'aria-labelledby': 'osc-title' });
  if (!(row.sourcedKm > 0)) return { element: root, update() {}, destroy() {} };
  let energy = normaliseEnergy(ctx.energyGeV);
  const baseline = row.sourcedKm;
  const maximum = firstMaximumEnergy(baseline);
  const rows = allBeamRows(ctx.atlas).filter(r => r.located && r.sourcedKm > 0);
  const select = el('select', { id: 'osc-baseline' }, rows.map(r => {
    const option = el('option', { value: r.arg }, `${named[r.arg] || r.label} · ${decimal(r.sourcedKm, 4)} km`);
    option.selected = r.arg === row.arg;
    return option;
  }));
  select.addEventListener('change', () => ctx.navigate({ entity: { type: 'view', slug: `beam-section/${select.value}` }, energy }));
  const range = el('input', { type: 'range', id: 'osc-energy', min: ENERGY.min, max: ENERGY.max, step: '.01',
    'aria-describedby': 'osc-control-help osc-readout' });
  const number = el('input', { type: 'number', id: 'osc-energy-number', min: ENERGY.min, max: ENERGY.max, step: '.01', inputmode: 'decimal' });
  const readout = el('output', { id: 'osc-readout', for: 'osc-energy osc-energy-number', 'aria-live': 'polite', 'aria-atomic': 'true' });
  const plot = el('div', { class: 'osc-plot' });
  const peak = el('button', { type: 'button', class: 'text-btn' }, 'Try the first maximum');
  const method = el('details', { class: 'osc-method' }, [
    el('summary', {}, 'Formula, parameters and sources'),
    el('p', { class: 'osc-formula' }, 'P(να → νβ) = sin²(2θ) sin²(1.267 Δm² L / E), α ≠ β'),
    el('p', {}, 'L is the sourced baseline in km; E is neutrino energy in GeV; Δm² is in eV². The factor 1.267 makes the phase dimensionless. P is a conversion probability from one flavor to another; survival is 1 − P.'),
    el('p', {}, 'Fixed teaching choices: θ = 45° (sin²(2θ) = 1), Δm² = 2.5 × 10⁻³ eV². These rounded inputs illustrate the atmospheric oscillation scale; they are not fitted parameters or an uncertainty band.'),
    el('p', {}, 'The first maximum occurs at phase π/2, so E₁ = 2 × 1.267 Δm² L / π. “First” counts peaks as L/E increases from zero; on an energy plot it is the highest-energy maximum. Doubling E at this peak halves the phase and gives P = 0.5 for the chosen mixing.'),
    el('p', {}, [sourceLink('https://t2k-experiment.org/neutrinos/beyond-the-standard-model/', 'T2K: two-flavor formula and units'), ' · ',
      sourceLink('https://pdg.lbl.gov/2024/reviews/rpp2024-rev-neutrino-mixing.pdf', 'PDG: neutrino mixing, vacuum and matter effects')]),
    el('p', {}, `Baseline input: ${decimal(baseline, 4)} km, from the beamline record’s distance field, rather than the coordinate-derived chord above. ${row.baseline.distance?.note || ''}`),
    el('p', {}, named[row.arg] === 'T2K'
      ? sourceLink('https://arxiv.org/pdf/1106.1238v2#page=10', 'T2K experiment paper: §3.6.1, PDF page 10, surveyed target–Super-K distance')
      : row.arg === 'lbnf' ? sourceLink('https://arxiv.org/pdf/2007.06722v4#page=12', 'DUNE ProtoDUNE-SP performance paper: §1, 1285 km baseline')
        : 'The original baseline citations appear in “Sourced baseline and computed distance” below.'),
  ]);
  root.append(
    el('h3', { id: 'osc-title' }, 'Oscillation lab'),
    el('p', { class: 'osc-model-note' }, 'Two-flavor vacuum teaching model. This is not a DUNE prediction, an observed event rate, or a substitute for three-flavor matter effects.'),
    el('p', {}, 'Keep the distance fixed and change the energy. Watch how the selected circle moves along the curve; compare it with the diamond marking the first maximum.'),
    el('div', { class: 'osc-controls' }, [
      el('label', { for: 'osc-baseline' }, 'Sourced baseline'), select,
      el('label', { for: 'osc-energy' }, 'Neutrino energy (GeV)'), range,
      el('label', { for: 'osc-energy-number' }, 'Set energy (GeV)'), number,
    ]),
    readout, plot,
    el('p', { id: 'osc-control-help', class: 'muted' }, 'Use the slider, arrow keys (0.01 GeV per step), or the number box. Range: 0.2–8 GeV.'),
    el('p', { class: 'osc-legend' }, '● Selected energy: solid guide · ◇ First maximum: dashed guide. Curve: illustrative conversion probability.'),
    el('p', { class: 'osc-maximum' }, `First maximum: ${decimal(maximum)} GeV at ${decimal(baseline, 4)} km; P = 100% for these teaching parameters.`),
    peak, method,
  );

  function draw() {
    const width = Math.max(260, Math.round(plot.getBoundingClientRect().width || 640));
    const height = 280;
    const left = 48, right = width - 18, top = 38, bottom = height - 44;
    const x = value => left + (value - ENERGY.min) / (ENERGY.max - ENERGY.min) * (right - left);
    const y = value => bottom - value * (bottom - top);
    const probability = oscillationProbability(baseline, energy);
    const svg = svgEl('svg', { viewBox: `0 0 ${width} ${height}`, width: '100%', height, role: 'img', 'aria-labelledby': 'osc-chart-title osc-chart-desc' });
    svg.append(svgEl('title', { id: 'osc-chart-title' }, 'Two-flavor conversion probability versus neutrino energy'),
      svgEl('desc', { id: 'osc-chart-desc' }, `At ${decimal(baseline,4)} km and ${decimal(energy)} GeV, conversion probability is ${(100*probability).toFixed(2)} percent. First maximum: ${decimal(maximum)} GeV. Circle is selected; diamond is maximum. This is an illustrative vacuum model.`));
    for (const tick of [0, .5, 1]) {
      svg.append(svgEl('line', { x1:left, x2:right, y1:y(tick), y2:y(tick), class:'osc-grid' }),
        svgEl('text', { x:left-8, y:y(tick)+5, 'text-anchor':'end' }, `${tick*100}%`));
    }
    for (const tick of [ENERGY.min, 2, 4, 6, 8]) svg.append(svgEl('text', { x:x(tick), y:bottom+21, 'text-anchor':'middle' }, String(tick)));
    svg.append(svgEl('text', { x:left, y:18 }, 'Conversion probability'),
      svgEl('text', { x:(left+right)/2, y:height-2, 'text-anchor':'middle' }, 'Neutrino energy (GeV)'));
    const points = Array.from({ length:1201 }, (_,i) => {
      const e = ENERGY.min+(ENERGY.max-ENERGY.min)*i/1200;
      return `${i?'L':'M'}${x(e).toFixed(2)},${y(oscillationProbability(baseline,e)).toFixed(2)}`;
    }).join(' ');
    svg.append(svgEl('path', { d:points, class:'osc-curve' }));
    if (maximum >= ENERGY.min && maximum <= ENERGY.max) {
      const mx=x(maximum), my=y(1);
      svg.append(svgEl('line', { x1:mx,x2:mx,y1:top,y2:bottom,class:'osc-max-guide' }),
        svgEl('path', { d:`M${mx},${my-10}l10,10 -10,10 -10,-10Z`, class:'osc-max-point' }));
    }
    svg.append(svgEl('line', { x1:x(energy),x2:x(energy),y1:y(probability),y2:bottom,class:'osc-selected-guide' }),
      svgEl('circle', { cx:x(energy),cy:y(probability),r:6,class:'osc-selected-point' }));
    plot.replaceChildren(svg);
  }
  function render() {
    range.value = String(energy);
    number.value = decimal(energy, 4);
    const percent = (oscillationProbability(baseline,energy)*100).toFixed(2);
    range.setAttribute('aria-valuetext', `${decimal(energy)} GeV; ${percent}% illustrative conversion probability`);
    readout.textContent = `E = ${decimal(energy)} GeV · P = ${percent}% · L/E = ${decimal(baseline/energy,1)} km/GeV`;
    draw();
  }
  function change(value) {
    energy = normaliseEnergy(value);
    patchQuietly({ energy }); // retain keyboard focus; no remount per slider step
    render();
  }
  range.addEventListener('input', () => change(range.value));
  number.addEventListener('change', () => change(number.value));
  peak.addEventListener('click', () => change(Math.round(maximum*100)/100));
  const observer = typeof ResizeObserver === 'undefined' ? null : new ResizeObserver(draw);
  observer?.observe(plot);
  render();
  return { element:root,
    update(next) { const restored=normaliseEnergy(next.energyGeV); if(restored!==energy){energy=restored;render();} },
    destroy() { observer?.disconnect(); },
  };
}
