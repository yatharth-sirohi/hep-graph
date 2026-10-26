// beam-geometry.js — the arithmetic behind "Beam through the Earth". No DOM, no
// data loading: two coordinates in, numbers out, so the browser view and the unit
// check (tests/test_atlas_beam_section.py) run the very same code.
//
// Model: a spherical Earth of mean radius R = 6371.0 km. The two sites are points
// on its surface; the neutrinos travel the straight chord between them. With the
// central angle Δσ (from the haversine of the two latitude/longitude pairs):
//
//   surface distance          s = R · Δσ
//   chord                     c = 2R · sin(Δσ / 2)
//   dip below local horizontal at the source        = Δσ / 2      (tangent–chord angle)
//   deepest point, at mid-chord (the sagitta)       = R · (1 − cos(Δσ / 2))
//   light travel time         t = c / c₀
//
// Nothing here knows about a particular beam.

export const EARTH_RADIUS_KM = 6371.0;
// The real radius runs from the polar 6357 km to the equatorial 6378 km: 0.3 %.
export const EARTH_RADIUS_POLAR_KM = 6357;
export const EARTH_RADIUS_EQUATORIAL_KM = 6378;
// The speed of light in vacuum, exactly, km/s.
export const LIGHT_SPEED_KM_S = 299792.458;

const rad = (degrees) => (degrees * Math.PI) / 180;
const deg = (radians) => (radians * 180) / Math.PI;

/** Central angle in radians between two [lat, lon] pairs given in degrees (haversine). */
export function centralAngle(a, b) {
  const dLat = rad(b[0] - a[0]);
  const dLon = rad(b[1] - a[1]);
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(rad(a[0])) * Math.cos(rad(b[0])) * Math.sin(dLon / 2) ** 2;
  return 2 * Math.asin(Math.min(1, Math.sqrt(h)));
}

/** Everything the section needs, from the central angle (radians) and a radius. */
export function fromAngle(dsigma, R = EARTH_RADIUS_KM) {
  const half = dsigma / 2;
  const chordKm = 2 * R * Math.sin(half);
  return {
    R,
    centralAngleRad: dsigma,
    centralAngleDeg: deg(dsigma),
    surfaceKm: R * dsigma,
    chordKm,
    dipRad: half,
    dipDeg: deg(half),
    sagittaKm: R * (1 - Math.cos(half)),
    lightMs: (chordKm / LIGHT_SPEED_KM_S) * 1000,
  };
}

/** The section between two [lat, lon] pairs, spherical Earth of radius R. */
export function sectionGeometry(a, b, R = EARTH_RADIUS_KM) {
  return fromAngle(centralAngle(a, b), R);
}

// The quantities that carry an uncertainty, by the key `sectionGeometry` returns.
export const UNCERTAIN_KEYS = ['centralAngleDeg', 'surfaceKm', 'chordKm', 'dipDeg', 'sagittaKm', 'lightMs'];

/**
 * How far the numbers could move, in two separate parts (both stated, never merged
 * into a hidden error bar):
 *
 *   radius       the same Δσ with the real radius at its smallest and largest
 *                (6357 and 6378 km), so a distance, depth or time moves by up to
 *                0.3 %. The dip and the central angle do not contain R at all;
 *                for them the sphere itself is the approximation (the Earth is
 *                flattened by 0.34 %), which this does not try to quantify.
 *   coordinates  both sites displaced by their recorded precision along the line
 *                that joins them: Δσ ± (p₁ + p₂) / R, a worst case that adds the
 *                two precisions linearly. `null` when a site records none.
 *
 * `precisionKm` is the sum of the two sites' precisions in km, or null.
 */
export function uncertainty(dsigma, precisionKm) {
  const low = fromAngle(dsigma, EARTH_RADIUS_POLAR_KM);
  const high = fromAngle(dsigma, EARTH_RADIUS_EQUATORIAL_KM);
  const nominal = fromAngle(dsigma);
  const radius = {};
  const coordinates = precisionKm == null ? null : {};
  for (const key of UNCERTAIN_KEYS) {
    radius[key] = { min: Math.min(low[key], high[key]), max: Math.max(low[key], high[key]) };
    if (coordinates) {
      const dAngle = precisionKm / EARTH_RADIUS_KM;
      const up = fromAngle(dsigma + dAngle)[key];
      const down = fromAngle(Math.max(0, dsigma - dAngle))[key];
      coordinates[key] = Math.max(Math.abs(up - nominal[key]), Math.abs(nominal[key] - down));
    }
  }
  return { radius, coordinates };
}

/**
 * Does a sourced length agree with the computed one? True when they differ by no
 * more than the radius spread plus the coordinate precision (both worst cases).
 */
export function agreesWithin(sourcedKm, computedKm, radiusRange, coordinateKm) {
  const reach = Math.max(computedKm - radiusRange.min, radiusRange.max - computedKm) + (coordinateKm || 0);
  return Math.abs(sourcedKm - computedKm) <= reach;
}

// The vertical exaggerations the zoomed panel may use. Stated in the figure.
export const EXAGGERATIONS = [5, 10, 20, 50, 100, 200];

/**
 * The largest exaggeration for which the section (the deepest chord point plus
 * the deepest recorded detector) still stands no taller than `maxRatio` of the
 * chord's length — tall enough to see the curvature, short enough to fit a screen.
 */
export function chooseExaggeration(chordKm, sagittaKm, deepestDetectorKm = 0, maxRatio = 0.55) {
  const extent = sagittaKm + Math.max(0, deepestDetectorKm);
  let chosen = EXAGGERATIONS[0];
  for (const factor of EXAGGERATIONS) {
    if ((extent * factor) / chordKm <= maxRatio) chosen = factor;
  }
  return chosen;
}

/**
 * The surface seen from the chord: `count + 1` points (x along the chord from its
 * midpoint, y above the chord, both in km) of the circle of radius R between the
 * two sites. y is not exaggerated here; the drawing multiplies it.
 */
export function surfaceProfile(dsigma, R = EARTH_RADIUS_KM, count = 96) {
  const half = dsigma / 2;
  const floor = R * Math.cos(half);
  const points = [];
  for (let i = 0; i <= count; i += 1) {
    const phi = -half + (dsigma * i) / count;
    points.push({ x: R * Math.sin(phi), y: R * Math.cos(phi) - floor });
  }
  return points;
}

/** The largest of 1, 2, 5 × 10ⁿ that does not exceed `value` (a round scale-bar length). */
export function niceLength(value) {
  if (!(value > 0)) return 0;
  const exponent = Math.floor(Math.log10(value));
  const base = 10 ** exponent;
  for (const step of [5, 2, 1]) {
    if (step * base <= value) return step * base;
  }
  return base;
}

/** A length in km as people read it: metres below 1 km, else one decimal place. */
export function formatKm(km, digits = 1) {
  if (!Number.isFinite(km)) return '';
  if (Math.abs(km) < 1) return `${Math.round(km * 1000)} m`;
  return `${km.toFixed(digits)} km`;
}
