// An interaction in the existing beam view, using its sourced baseline row.
import { allBeamRows } from './beam-rows.js';
import { ENERGY, MODEL, doublingExperiment, firstMaximumEnergy, flavorProbabilities, matchBaselineEnergy, normaliseEnergy, oscillationProbability } from './oscillation-model.js';
import { patchQuietly } from '../state.js';
import { createTourStepLink } from '../tour-link.js';

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
  const select = el('select', { id: 'osc-baseline', 'aria-describedby': 'osc-baseline-help osc-baseline-error' }, rows.map(r => {
    const option = el('option', { value: r.arg }, `${named[r.arg] || r.label} · ${decimal(r.sourcedKm, 4)} km`);
    option.selected = r.arg === row.arg;
    return option;
  }));
  const keepRatio = el('input', { type: 'checkbox', id: 'osc-keep-ratio', 'aria-describedby': 'osc-baseline-help' });
  keepRatio.checked = Boolean(ctx.keepRatio);
  const baselineError = el('p', { id: 'osc-baseline-error', role: 'alert', hidden: '' });
  function clearBaselineError() {
    baselineError.hidden = true;
    baselineError.textContent = ''; // Hidden described text still reaches assistive technology.
  }
  keepRatio.addEventListener('change', () => {
    clearBaselineError();
    patchQuietly({ keepRatio: keepRatio.checked });
  });
  select.addEventListener('change', () => {
    const target = rows.find(r => r.arg === select.value);
    if (!target) return;
    let nextEnergy = energy;
    if (keepRatio.checked) {
      const match = matchBaselineEnergy(baseline, energy, target.sourcedKm);
      if (match.energy == null) {
        select.value = row.arg;
        const shown = decimal(match.requestedEnergy);
        const required = Number(shown) >= ENERGY.min && Number(shown) <= ENERGY.max
          ? `an energy just ${match.requestedEnergy < ENERGY.min ? `below ${ENERGY.min}` : `above ${ENERGY.max}`} GeV`
          : `${shown} GeV`;
        baselineError.textContent = `Keeping L/E at this baseline would need ${required}, outside the lab’s 0.2–8 GeV range. Change the energy or turn off “Keep L/E” and try again.`;
        baselineError.hidden = false;
        return;
      }
      nextEnergy = match.energy;
    }
    ctx.navigate({ entity: { type: 'view', slug: `beam-section/${target.arg}` }, energy: nextEnergy, keepRatio: keepRatio.checked });
  });
  const range = el('input', { type: 'range', id: 'osc-energy', min: ENERGY.min, max: ENERGY.max, step: '.01',
    'aria-describedby': 'osc-control-help osc-readout' });
  const number = el('input', { type: 'number', id: 'osc-energy-number', min: ENERGY.min, max: ENERGY.max, step: '.01', inputmode: 'decimal' });
  const readout = el('output', { id: 'osc-readout', for: 'osc-energy osc-energy-number', 'aria-live': 'polite', 'aria-atomic': 'true' });
  const plot = el('div', { class: 'osc-plot' });
  const peak = el('button', { type: 'button', class: 'text-btn' }, 'Try the first maximum');
  const experiment = doublingExperiment(baseline);
  const predictionAnswer = el('div', { id: 'osc-prediction-answer', class: 'osc-prediction-answer', hidden: '', role: 'status', 'aria-live': 'polite' });
  const testPrediction = el('button', { type: 'button', class: 'text-btn', 'aria-controls': 'osc-prediction-answer', 'aria-expanded': 'false' }, 'Test doubling on the curve');
  const prediction = experiment ? el('details', { class: 'osc-experiment' }, [
    el('summary', {}, 'Predict: what if the energy doubles?'),
    el('p', {}, `Start near the first maximum at ${decimal(experiment.startEnergy)} GeV, keeping this baseline fixed. Predict whether doubling the energy will raise, lower, or leave the conversion probability unchanged. Then test your prediction on the same curve.`),
    testPrediction, predictionAnswer,
  ]) : null;
  const survivalValue = el('dd', { class: 'osc-survival-value' });
  const conversionValue = el('dd', { class: 'osc-conversion-value' });
  const flavorBar = el('div', { class: 'osc-flavor-bar' });
  const flavorContext = el('p', { id: 'osc-flavor-context', class: 'muted' });
  const flavors = el('details', { class: 'osc-flavors' }, [
    el('summary', {}, 'Track both flavors'),
    el('p', {}, 'Two generic flavors: α is the original flavor, β the other. Change energy above to follow both probabilities.'),
    flavorContext,
    el('dl', { class: 'osc-flavor-values' }, [
      el('div', {}, [el('dt', {}, 'Original flavor α · solid'), survivalValue]),
      el('div', {}, [el('dt', {}, 'Other flavor β · striped'), conversionValue]),
    ]),
    flavorBar,
    el('p', { class: 'osc-formula' }, 'P(α → α) = 1 − P(α → β); total probability = 100%.'),
    el('p', {}, 'Flavor survival means keeping the original flavor. Changing flavor is different from absorption: this closed two-flavor vacuum model includes no absorption or detector response. The probabilities are not detected-event fractions or rates. Percentages are rounded to 0.01%.'),
    el('p', {}, sourceLink('https://t2k-experiment.org/neutrinos/beyond-the-standard-model/', 'T2K: “Atmospheric Neutrino Anomaly” and the two-flavor oscillation explanation')),
    el('p', { class: 'osc-flavor-evidence' }, [
      "Next: compare solar-neutrino measurements. This atmospheric-scale teaching model is not a fit to SNO's solar-neutrino data. ",
      createTourStepLink('neutrino-oscillation-story', 3, 'Try the SNO flux question', ctx.navigate),
    ]),
  ]);
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
      el('label', { for: 'osc-baseline' }, 'Sourced baseline'),
      el('div', { class: 'osc-baseline-controls' }, [select,
        el('label', { for: 'osc-keep-ratio', class: 'osc-keep-ratio' }, [keepRatio, 'Keep L/E when changing baseline']), baselineError]),
      el('label', { for: 'osc-energy' }, 'Neutrino energy (GeV)'), range,
      el('label', { for: 'osc-energy-number' }, 'Set energy (GeV)'), number,
    ]),
    readout, plot,
    el('p', { id: 'osc-control-help', class: 'muted' }, 'Use the slider, arrow keys (0.01 GeV per step), or the number box. Range: 0.2–8 GeV.'),
    el('p', { id: 'osc-baseline-help', class: 'muted' }, 'At fixed L/E, the oscillation phase and probability stay the same in this teaching model. “Keep L/E” scales energy with distance, rounded to 0.01 GeV, so the displayed values may differ slightly. Unchecked: energy stays fixed.'),
    el('p', { class: 'osc-legend' }, '● Selected energy: solid guide · ◇ First maximum: dashed guide. Curve: illustrative conversion probability.'),
    el('p', { class: 'osc-maximum' }, `First maximum: ${decimal(maximum)} GeV at ${decimal(baseline, 4)} km; P = 100% for these teaching parameters.`),
    peak, flavors, prediction, method,
  );

  function makePlot(width, height = 280, prefix = 'osc', fontSize = 14) {
    const scale = fontSize/14;
    const left = 48*scale, right = width - 18*scale, top = 38*scale, bottom = height - 44*scale;
    const x = value => left + (value - ENERGY.min) / (ENERGY.max - ENERGY.min) * (right - left);
    const y = value => bottom - value * (bottom - top);
    const probability = oscillationProbability(baseline, energy);
    const svg = svgEl('svg', { viewBox: `0 0 ${width} ${height}`, width: '100%', height, role: 'img', 'aria-labelledby': `${prefix}-chart-title ${prefix}-chart-desc` });
    svg.append(svgEl('title', { id: `${prefix}-chart-title` }, 'Two-flavor conversion probability versus neutrino energy'),
      svgEl('desc', { id: `${prefix}-chart-desc` }, `At ${decimal(baseline,4)} km and ${decimal(energy)} GeV, conversion probability is ${(100*probability).toFixed(2)} percent. First maximum: ${decimal(maximum)} GeV. Circle is selected; diamond is maximum. This is an illustrative vacuum model.`));
    for (const tick of [0, .5, 1]) {
      svg.append(svgEl('line', { x1:left, x2:right, y1:y(tick), y2:y(tick), class:'osc-grid' }),
        svgEl('text', { x:left-8*scale, y:y(tick)+5*scale, 'text-anchor':'end' }, `${tick*100}%`));
    }
    for (const tick of [ENERGY.min, 2, 4, 6, 8]) svg.append(svgEl('text', { x:x(tick), y:bottom+21*scale, 'text-anchor':'middle' }, String(tick)));
    svg.append(svgEl('text', { x:left, y:18*scale }, 'Conversion probability'),
      svgEl('text', { x:(left+right)/2, y:height-2*scale, 'text-anchor':'middle' }, 'Neutrino energy (GeV)'));
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
    for (const text of svg.querySelectorAll('text')) text.style.fontSize = `${fontSize}px`;
    return svg;
  }
  function draw() {
    plot.replaceChildren(makePlot(Math.max(260, Math.round(plot.getBoundingClientRect().width || 640))));
  }
  function makeFlavorBar(pair, converted, survived, prefix = 'osc-flavor') {
    const svg = svgEl('svg', { viewBox: '0 0 1000 60', width: '100%', height: 48,
      preserveAspectRatio: 'none', role: 'img', 'aria-labelledby': `${prefix}-title ${prefix}-desc` });
    svg.append(svgEl('title', { id: `${prefix}-title` }, 'The two flavor probabilities at the selected energy'),
      svgEl('desc', { id: `${prefix}-desc` }, `At ${decimal(energy)} GeV and ${decimal(baseline,4)} km, original-flavor survival is ${survived}% and conversion to the other flavor is ${converted}%. The solid and striped parts total 100% in this teaching model.`));
    const defs = svgEl('defs');
    const pattern = svgEl('pattern', { id: `${prefix}-stripes`, width: 20, height: 20, patternUnits: 'userSpaceOnUse' });
    pattern.append(svgEl('path', { d: 'M-5,5l10,-10 M0,20L20,0 M15,25l10,-10', class: 'osc-flavor-hatch' }));
    defs.append(pattern);svg.append(defs);
    const original = 1000 * pair.survival;
    svg.append(
      svgEl('rect', { x:0, y:10, width:original, height:40, class:'osc-survival-part', 'data-probability':'survival' }),
      svgEl('rect', { x:original, y:10, width:1000-original, height:40, fill:`url(#${prefix}-stripes)`, 'data-probability':'conversion' }),
      svgEl('rect', { x:0, y:10, width:1000, height:40, class:'osc-flavor-outline' }),
    );
    return svg;
  }
  function drawFlavors(pair, converted, survived) {
    flavorContext.textContent = `Selected energy: ${decimal(energy)} GeV · Baseline: ${decimal(baseline,4)} km`;
    survivalValue.textContent = `${survived}%`;
    conversionValue.textContent = `${converted}%`;
    flavorBar.replaceChildren(makeFlavorBar(pair, converted, survived));
  }
  // Export at a readable, viewport-independent size. The holder gives the
  // existing SVG painter real computed styles even when the disclosure is closed.
  function exportFigure() {
    const selected = energy;
    const pair = flavorProbabilities(baseline, selected);
    const converted = (100*pair.conversion).toFixed(2);
    const survived = (100-Number(converted)).toFixed(2);
    const holder = el('div', { class: 'osc-export-stage osc-plot', 'aria-hidden': 'true' });
    Object.assign(holder.style, { position:'fixed', left:'-10000px', top:'0', width:'800px', pointerEvents:'none' });
    const text = (x,y,value,size=18) => svgEl('text', { x,y,style:`font-size:${size}px` }, value);
    const chart = svgEl('svg', { width:800,height:400,viewBox:'0 0 800 400' });
    chart.append(text(16,22,'Two-flavor vacuum teaching model',20),
      text(16,46,`${named[row.arg] || row.label} · E = ${decimal(selected)} GeV · sourced L = ${decimal(baseline,4)} km`),
      text(16,68,'Not a DUNE prediction, observed event rate or substitute for three-flavor matter effects.',14));
    const curve = makePlot(800,320,'osc-export',18);
    curve.setAttribute('y','80');chart.append(curve);
    const balance = svgEl('svg', { width:800,height:100,viewBox:'0 0 800 100' });
    balance.append(text(16,23,`Original flavor α (solid): ${survived}%`),
      text(424,23,`Other flavor β (striped): ${converted}%`));
    const bar = makeFlavorBar(pair,converted,survived,'osc-export-flavor');
    bar.setAttribute('y','35');balance.append(bar);
    holder.append(chart,balance);document.body.append(holder);
    const baselineSource = row.arg === 'j-parc-neutrino'
      ? 'T2K experiment paper §3.6.1 (surveyed baseline): https://arxiv.org/pdf/1106.1238v2#page=10'
      : row.arg === 'lbnf' ? 'DUNE ProtoDUNE-SP performance paper §1 (baseline): https://arxiv.org/pdf/2007.06722v4#page=12'
        : `Baseline record and citations: ${location.origin}/atlas#/beamline/${row.beamline.id.split(':')[1]}`;
    return {
      figures:[chart,balance], layout:'column',
      notes:[
        'Two-flavor vacuum teaching model; no absorption or detector response. Not a DUNE prediction, observed event rate or substitute for three-flavor matter effects.',
        `Selected: E = ${decimal(selected)} GeV; sourced L = ${decimal(baseline,4)} km; conversion ${converted}%; original-flavor survival ${survived}%.`,
        'P(α→β) = sin²(2θ) sin²(1.267 Δm² L/E); L in km, E in GeV, Δm² in eV²; P(α→α) = 1 − P(α→β).',
        `θ = ${MODEL.thetaDeg}°; Δm² = ${MODEL.deltaM2.toExponential(1)} eV²; fixed teaching choices, not a fit or uncertainty band.`,
        `Curve: ${ENERGY.min}–${ENERGY.max} GeV, conversion probability 0–100%. Circle/solid guide: selected energy; diamond/dashed guide: first maximum (${decimal(maximum)} GeV).`,
        'Formula and interpretation: https://t2k-experiment.org/neutrinos/beyond-the-standard-model/',
        baselineSource,
        `Reopen this energy and baseline: ${location.href}`,
      ],
      release:()=>holder.remove(),
    };
  }
  function render() {
    range.value = String(energy);
    number.value = decimal(energy, 4);
    const pair = flavorProbabilities(baseline, energy);
    const percent = (pair.conversion*100).toFixed(2);
    // Round the displayed complement together so the displayed pair totals 100%.
    const survived = (100-Number(percent)).toFixed(2);
    range.setAttribute('aria-valuetext', `${decimal(energy)} GeV; ${percent}% illustrative conversion probability; ${survived}% original-flavor survival`);
    drawFlavors(pair, percent, survived);
    readout.textContent = `E = ${decimal(energy)} GeV · P = ${percent}% · L/E = ${decimal(baseline/energy,1)} km/GeV`;
    draw();
  }
  function change(value) {
    clearBaselineError();
    predictionAnswer.hidden = true;
    testPrediction.setAttribute('aria-expanded', 'false');
    energy = normaliseEnergy(value);
    patchQuietly({ energy }); // retain keyboard focus; no remount per slider step
    render();
    ctx.host?.exportChanged?.();
  }
  range.addEventListener('input', () => change(range.value));
  number.addEventListener('change', () => change(number.value));
  peak.addEventListener('click', () => change(Math.round(maximum*100)/100));
  testPrediction.addEventListener('click', () => {
    if (!experiment) return;
    change(experiment.doubledEnergy);
    predictionAnswer.replaceChildren(
      el('p', {}, `Conversion falls from ${(100 * experiment.startProbability).toFixed(2)}% at ${decimal(experiment.startEnergy)} GeV to ${(100 * experiment.doubledProbability).toFixed(2)}% at ${decimal(experiment.doubledEnergy)} GeV. The selected point on the curve now shows the doubled energy.`),
      el('p', {}, 'Why: at fixed distance, doubling the energy halves the oscillation phase, which is proportional to L/E. Starting exactly at phase π/2 would give phase π/4, so this model’s conversion probability would fall from 100% to 50%. The numbers above use the actual 0.01 GeV control rounding.'),
    );
    predictionAnswer.hidden = false;
    testPrediction.setAttribute('aria-expanded', 'true');
  });
  const observer = typeof ResizeObserver === 'undefined' ? null : new ResizeObserver(draw);
  observer?.observe(plot);
  render();
  return { element:root, exportFigure,
    update(next) {
      keepRatio.checked = Boolean(next.keepRatio);
      clearBaselineError();
      const restored = normaliseEnergy(next.energyGeV);
      if (restored !== energy) {
        clearBaselineError();
        predictionAnswer.hidden = true;
        testPrediction.setAttribute('aria-expanded', 'false');
        energy = restored;
        render();
        ctx.host?.exportChanged?.();
      }
    },
    destroy() { observer?.disconnect(); },
  };
}
