// Two-flavor vacuum teaching model; the chosen parameters are illustrative,
// not a fit or an experiment's event prediction. Units follow T2K's explanation.
export const MODEL = Object.freeze({ deltaM2: 2.5e-3, thetaDeg: 45, phaseFactor: 1.267 });
export const ENERGY = Object.freeze({ min: 0.2, max: 8, initial: 0.6 });
export const MIXING = Object.freeze({ min: 0, max: 45, initial: MODEL.thetaDeg });

function parameters(baselineKm, { deltaM2 = MODEL.deltaM2, thetaDeg = MODEL.thetaDeg } = {}) {
  if (!Number.isFinite(baselineKm) || baselineKm < 0 || !Number.isFinite(deltaM2) || deltaM2 <= 0
      || !Number.isFinite(thetaDeg) || thetaDeg < 0 || thetaDeg > 90) {
    throw new RangeError('Use a finite nonnegative baseline, positive mass splitting and a mixing angle from 0 to 90 degrees.');
  }
  return { deltaM2, thetaDeg };
}

function amplitude(thetaDeg) {
  return thetaDeg === 0 || thetaDeg === 90 ? 0 : Math.sin(2 * thetaDeg * Math.PI / 180) ** 2;
}

export function mixingAmplitude(thetaDeg = MODEL.thetaDeg) {
  parameters(0, { thetaDeg });
  return amplitude(thetaDeg);
}

export function oscillationProbability(baselineKm, energyGeV, options) {
  const { deltaM2, thetaDeg } = parameters(baselineKm, options);
  if (!Number.isFinite(energyGeV) || energyGeV <= 0) throw new RangeError('Energy must be finite and positive, in GeV.');
  return amplitude(thetaDeg)
    * Math.sin(MODEL.phaseFactor * deltaM2 * baselineKm / energyGeV) ** 2;
}

// A closed two-flavor vacuum model has no absorption or detector response.
// Survival means retaining the original flavor, not a transmitted event rate.
export function flavorProbabilities(baselineKm, energyGeV, options) {
  const conversion = oscillationProbability(baselineKm, energyGeV, options);
  return { conversion, survival: 1 - conversion };
}

// The first peak as L/E grows from zero: phase = pi/2. At fixed L it is
// the highest-energy oscillation maximum, not the leftmost peak of an E plot.
// Zero mixing or distance has no distinct peak.
export function firstMaximumEnergy(baselineKm, options) {
  const { deltaM2, thetaDeg } = parameters(baselineKm, options);
  if (baselineKm === 0 || amplitude(thetaDeg) === 0) return null;
  return 2 * MODEL.phaseFactor * deltaM2 * baselineKm / Math.PI;
}

export function normaliseEnergy(value) {
  if (value == null || String(value).trim() === '' || !Number.isFinite(Number(value))) return ENERGY.initial;
  // Both native controls support 0.01 GeV steps; normalize pasted and typed
  // values once so the curve, controls, and share URL describe the same point.
  return Math.round(Math.min(ENERGY.max, Math.max(ENERGY.min, Number(value))) * 100) / 100;
}

// These controls cover the distinct vacuum amplitudes with positive fixed Δm².
export function normaliseMixing(value) {
  if (value == null || String(value).trim() === '' || !Number.isFinite(Number(value))) return MIXING.initial;
  return Math.round(Math.min(MIXING.max, Math.max(MIXING.min, Number(value))));
}

/** A reproducible learner experiment on the real control grid. Returns null
 * rather than silently changing the question when its energies are out of range. */
export function doublingExperiment(baselineKm, options) {
  const maximum = firstMaximumEnergy(baselineKm, options);
  if (maximum == null || maximum < ENERGY.min || maximum > ENERGY.max) return null;
  const startEnergy = normaliseEnergy(maximum);
  const doubledEnergy = 2 * startEnergy;
  if (doubledEnergy > ENERGY.max) return null;
  const target = normaliseEnergy(doubledEnergy);
  return {
    startEnergy,
    doubledEnergy: target,
    startProbability: oscillationProbability(baselineKm, startEnergy, options),
    doubledProbability: oscillationProbability(baselineKm, target, options),
  };
}


/** Keep the vacuum phase L/E when moving to a different sourced baseline.
 * Check the unrounded target first: a clamped result would change the question. */
export function matchBaselineEnergy(fromBaselineKm, energyGeV, toBaselineKm) {
  parameters(fromBaselineKm);
  parameters(toBaselineKm);
  if (fromBaselineKm === 0 || toBaselineKm === 0 || !Number.isFinite(energyGeV)
      || energyGeV < ENERGY.min || energyGeV > ENERGY.max) {
    throw new RangeError('Use positive baselines and an energy within the lab’s supported range.');
  }
  const requestedEnergy = energyGeV * toBaselineKm / fromBaselineKm;
  return { requestedEnergy, energy: requestedEnergy < ENERGY.min || requestedEnergy > ENERGY.max
    ? null : normaliseEnergy(requestedEnergy) };
}
