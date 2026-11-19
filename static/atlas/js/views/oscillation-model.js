// Two-flavor vacuum teaching model; the chosen parameters are illustrative,
// not a fit or an experiment's event prediction. Units follow T2K's explanation.
export const MODEL = Object.freeze({ deltaM2: 2.5e-3, thetaDeg: 45, phaseFactor: 1.267 });
export const ENERGY = Object.freeze({ min: 0.2, max: 8, initial: 0.6 });

function parameters(baselineKm, { deltaM2 = MODEL.deltaM2, thetaDeg = MODEL.thetaDeg } = {}) {
  if (!Number.isFinite(baselineKm) || baselineKm < 0 || !Number.isFinite(deltaM2) || deltaM2 <= 0
      || !Number.isFinite(thetaDeg) || thetaDeg < 0 || thetaDeg > 90) {
    throw new RangeError('Use a finite nonnegative baseline, positive mass splitting and a mixing angle from 0 to 90 degrees.');
  }
  return { deltaM2, thetaDeg };
}

export function oscillationProbability(baselineKm, energyGeV, options) {
  const { deltaM2, thetaDeg } = parameters(baselineKm, options);
  if (!Number.isFinite(energyGeV) || energyGeV <= 0) throw new RangeError('Energy must be finite and positive, in GeV.');
  return Math.sin(2 * thetaDeg * Math.PI / 180) ** 2
    * Math.sin(MODEL.phaseFactor * deltaM2 * baselineKm / energyGeV) ** 2;
}

// The first peak as L/E grows from zero: phase = pi/2. At fixed L it is
// the highest-energy oscillation maximum, not the leftmost peak of an E plot.
export function firstMaximumEnergy(baselineKm, options) {
  const { deltaM2 } = parameters(baselineKm, options);
  return 2 * MODEL.phaseFactor * deltaM2 * baselineKm / Math.PI;
}

export function normaliseEnergy(value) {
  if (value == null || String(value).trim() === '' || !Number.isFinite(Number(value))) return ENERGY.initial;
  return Math.min(ENERGY.max, Math.max(ENERGY.min, Number(value)));
}
