// A hypothetical point compared with one exact published row. No interpolation,
// confidence calculation, event-rate model, or expected-sensitivity conversion.
export const LIMIT_PROBE_SLUG = 'lz-2024-si-wimp-nucleon';
const FACTORS = [.1, 1, 10];

export function normaliseLimitProbe(value) {
  if (typeof value !== 'string') return null;
  const parts = value.split(',');
  if (parts.length !== 2 || parts.some(p => !p.trim())) return null;
  const [mass, factor] = parts.map(Number);
  return Number.isFinite(mass) && mass > 0 && FACTORS.includes(factor) ? `${mass},${factor}` : null;
}

export function limitComparison(row, mass, factor) {
  if (row?.type !== 'limit_curve' || row.columns?.x?.unit !== 'GeV/c^2'
      || row.columns?.y?.unit !== 'cm^2' || !Number.isFinite(mass) || mass <= 0 || !FACTORS.includes(factor)) return null;
  const point = row.points?.find(p => p[0] === mass);
  const limit = point?.[1], model = limit * factor;
  if (!Number.isFinite(limit) || limit <= 0 || !Number.isFinite(model) || model <= 0) return null;
  return { massGeV: mass, limitCm2: limit, modelCm2: model, factor,
    relation: factor === 1 ? 'boundary' : factor > 1 ? 'above' : 'below' };
}

export function comparisonDomain(domain, comparison) {
  if (!comparison) return { ...domain };
  const low = Math.min(comparison.limitCm2, comparison.modelCm2);
  const high = Math.max(comparison.limitCm2, comparison.modelCm2);
  // Reserve space for the complete circle/triangle, not only their centers.
  const padding = .05 * (Math.log10(domain.y1) - Math.log10(domain.y0));
  const lower = Math.log10(low) - padding, upper = Math.log10(high) + padding;
  return { ...domain,
    y0: lower < Math.log10(domain.y0) ? 10 ** Math.floor(lower) : domain.y0,
    y1: upper > Math.log10(domain.y1) ? 10 ** Math.ceil(upper) : domain.y1 };
}
