// Ideal proton–proton kinematics; energies are total energies in GeV.
export const COLLISION_MODEL = Object.freeze({
  restEnergyGeV: 0.938272, // Rounded from PDG 2024 Table 1.1, not an exact constant.
  kinematicsURL: 'https://pdg.lbl.gov/2024/reviews/rpp2024-rev-kinematics.pdf#page=1',
  restEnergyURL: 'https://pdg.lbl.gov/2024/reviews/rpp2024-rev-phys-constants.pdf#page=1',
});
export const COLLISION_ENERGY = Object.freeze({ min:1, max:10000, default:450, step:0.1 });

export function normaliseCollisionEnergy(value) {
  if (!['number','string'].includes(typeof value) || String(value).trim() === '') return COLLISION_ENERGY.default;
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return COLLISION_ENERGY.default;
  return Math.round(Math.min(COLLISION_ENERGY.max, Math.max(COLLISION_ENERGY.min, parsed))*10)/10;
}

export function collisionEnergies(energyGeV) {
  const mu = COLLISION_MODEL.restEnergyGeV;
  if (!Number.isFinite(energyGeV) || energyGeV < mu) throw new RangeError('Total proton energy must be finite and at least its rest energy.');
  const fixedTargetGeV = Math.sqrt(2*mu*(mu+energyGeV));
  const headOnGeV = 2*energyGeV;
  if (![fixedTargetGeV,headOnGeV].every(Number.isFinite)) throw new RangeError('Collision energies overflow the numeric range.');
  return { beamEnergyGeV:energyGeV, fixedTargetGeV, headOnGeV };
}

export function quadrupleExperiment(energyGeV) {
  if (!Number.isFinite(energyGeV) || energyGeV < COLLISION_ENERGY.min || energyGeV > COLLISION_ENERGY.max/4) return null;
  const start=collisionEnergies(energyGeV),end=collisionEnergies(4*energyGeV);
  return { start,end,fixedFactor:end.fixedTargetGeV/start.fixedTargetGeV,headOnFactor:end.headOnGeV/start.headOnGeV };
}
