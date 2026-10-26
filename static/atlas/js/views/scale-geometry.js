// scale-geometry.js — the arithmetic behind "Compare with…" on the local map: lay one
// facility's footprint over another place at true scale. No DOM, no data loading:
// vertices in, vertices out, so the browser and the unit check
// (tests/test_atlas_scale_comparisons.py) run the very same code.
//
// THE METHOD (stated on the page as well)
//   A footprint is a set of GeoJSON vertices [lon, lat]. Its centre is the middle of
//   its bounding box, measured in a local azimuthal-equidistant plane around the
//   vertices' mean direction. Every vertex is then described by its OFFSET from that
//   centre: the great-circle distance d and the initial bearing θ at the centre. The
//   overlay puts the vertex at the same (d, θ) from the NEW centre:
//
//       q = p · cos(d/R) + (n · cos θ + e · sin θ) · sin(d/R)
//
//   with p the unit vector of the new centre and n, e the unit vectors of north and
//   east there. This is a translation ON THE SPHERE: ground distances from the centre
//   are preserved exactly, and distances between two vertices change only by terms of
//   order (d/R)², under 0.01 % for a 30 km footprint. Shifting latitude and longitude
//   by the same numbers of degrees would not do that: a degree of longitude is 111 km
//   at the equator and 28 km at 75°, so a ring moved north would shrink east–west.
//
//   Bearings are measured from true north. A map drawn in a polar projection has no
//   true north at its centre, so there "north" is the map's own grid north (the 0°
//   meridian points up on the south polar map, as the polar maps are drawn) — the
//   same convention the polar map uses, so an overlay is upright on it.
//
//   The Earth is the sphere of the atlas's geodesy (R = 6371.0088 km, the WGS 84 mean
//   radius), the same one the geometry validator and the map's scale bar use.

export const EARTH_RADIUS_M = 6371008.8;

/** Which features make up a facility's "principal footprint": its rings, outlines and
 * arrays, with the linear structures that tie them together. */
export const PRIMARY_TYPES = ['ring', 'array', 'boundary', 'linac', 'tunnel', 'beamline', 'transfer_line'];
/** A facility with none of those (an underground laboratory, a reactor site) is drawn
 * from its halls and caverns instead; and a facility with only buildings from those. */
export const SECONDARY_TYPES = ['cavern', 'hall', 'experimental_area', 'target_station', 'building'];

const rad = (degrees) => (degrees * Math.PI) / 180;
const deg = (radians) => (radians * 180) / Math.PI;

// ------------------------------------------------------------------ vectors
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const norm = (a) => Math.sqrt(dot(a, a));
const scale = (a, k) => [a[0] * k, a[1] * k, a[2] * k];
const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const unit = (a) => scale(a, 1 / norm(a));

/** Unit vector of a (latitude, longitude) in degrees. */
function toVec(lat, lon) {
  const phi = rad(lat);
  const lambda = rad(lon);
  return [Math.cos(phi) * Math.cos(lambda), Math.cos(phi) * Math.sin(lambda), Math.sin(phi)];
}

/** [lat, lon] in degrees of a unit vector, the longitude in (−180, 180]. */
function fromVec(v) {
  return [deg(Math.asin(Math.max(-1, Math.min(1, v[2])))), deg(Math.atan2(v[1], v[0]))];
}

/**
 * The local frame at a point: p (up), n (the direction "north") and e (east, = n × p).
 * With `polar` true the frame is the polar map's: grid north is the direction of the
 * 0° meridian from the south pole (and of the 180° meridian from the north pole), the
 * up of the map at that pole.
 */
export function frameAt(lat, lon, polar = false) {
  const p = toVec(lat, lon);
  let n;
  if (polar) {
    const ref = lat < 0 ? [1, 0, 0] : [-1, 0, 0];
    n = unit(add(ref, scale(p, -dot(ref, p))));
  } else {
    const phi = rad(lat);
    const lambda = rad(lon);
    n = [-Math.sin(phi) * Math.cos(lambda), -Math.sin(phi) * Math.sin(lambda), Math.cos(phi)];
  }
  return { p, n, e: cross(n, p) };
}

/** Distance (metres) and bearing (radians, clockwise from the frame's north) of a
 * [lat, lon] point as seen from the frame's centre. */
export function offsetIn(frame, lat, lon, R = EARTH_RADIUS_M) {
  const v = toVec(lat, lon);
  const angle = Math.atan2(norm(cross(frame.p, v)), dot(frame.p, v));
  if (angle < 1e-15) return { distM: 0, bearing: 0 };
  return { distM: angle * R, bearing: Math.atan2(dot(v, frame.e), dot(v, frame.n)) };
}

/** The [lat, lon] reached from the frame's centre by `distM` metres on `bearing` radians. */
export function destinationIn(frame, distM, bearing, R = EARTH_RADIUS_M) {
  const a = distM / R;
  const direction = add(scale(frame.n, Math.cos(bearing)), scale(frame.e, Math.sin(bearing)));
  return fromVec(add(scale(frame.p, Math.cos(a)), scale(direction, Math.sin(a))));
}

/** Great-circle metres between two [lon, lat] vertices. */
export function distanceM(a, b, R = EARTH_RADIUS_M) {
  const va = toVec(a[1], a[0]);
  const vb = toVec(b[1], b[0]);
  return R * Math.atan2(norm(cross(va, vb)), dot(va, vb));
}

/** Length in metres of a [lon, lat] polyline. */
export function lineLengthM(coords, R = EARTH_RADIUS_M) {
  let total = 0;
  for (let i = 1; i < coords.length; i += 1) total += distanceM(coords[i - 1], coords[i], R);
  return total;
}

// ----------------------------------------------------------------- geometry
/** Every [lon, lat] vertex of a GeoJSON geometry, flattened. */
export function vertices(geometry) {
  const out = [];
  const walk = (c) => {
    if (typeof c[0] === 'number') out.push(c);
    else c.forEach(walk);
  };
  if (geometry && geometry.coordinates) walk(geometry.coordinates);
  return out;
}

/** A copy of a GeoJSON geometry with every vertex passed through `fn([lon, lat])`. */
export function mapVertices(geometry, fn) {
  const walk = (c) => (typeof c[0] === 'number' ? fn(c) : c.map(walk));
  return { type: geometry.type, coordinates: walk(geometry.coordinates) };
}

/**
 * The centre of a footprint and its size: the middle of the bounding box of `points`
 * ([lon, lat] each) in a local azimuthal-equidistant plane around their mean direction.
 * Returns { lat, lon, widthM, heightM } (the box's east–west and north–south extent).
 */
export function boundsCentre(points, polar = false) {
  if (!points.length) return null;
  let mean = [0, 0, 0];
  for (const [lon, lat] of points) mean = add(mean, toVec(lat, lon));
  const first = points[0];
  const [lat0, lon0] = norm(mean) < 1e-9 ? [first[1], first[0]] : fromVec(unit(mean));
  const frame = frameAt(lat0, lon0, polar);
  let minX = Infinity;
  let maxX = -Infinity;
  let minY = Infinity;
  let maxY = -Infinity;
  for (const [lon, lat] of points) {
    const { distM, bearing } = offsetIn(frame, lat, lon);
    const x = distM * Math.sin(bearing);
    const y = distM * Math.cos(bearing);
    minX = Math.min(minX, x);
    maxX = Math.max(maxX, x);
    minY = Math.min(minY, y);
    maxY = Math.max(maxY, y);
  }
  const mid = [(minX + maxX) / 2, (minY + maxY) / 2];
  const [lat, lon] = destinationIn(frame, Math.hypot(mid[0], mid[1]), Math.atan2(mid[0], mid[1]));
  return { lat, lon, widthM: maxX - minX, heightM: maxY - minY };
}

/**
 * Move a vertex from one centre to another, keeping its distance and bearing.
 * `from` and `to` are { lat, lon, polar } — `polar` selects grid north (see above).
 */
export function translator(from, to) {
  const source = frameAt(from.lat, from.lon, !!from.polar);
  const target = frameAt(to.lat, to.lon, !!to.polar);
  return ([lon, lat]) => {
    const { distM, bearing } = offsetIn(source, lat, lon);
    const [outLat, outLon] = destinationIn(target, distM, bearing);
    return [outLon, outLat];
  };
}

// --------------------------------------------------------------- the footprint
/** True for a shape with extent: a Point is a position and an accuracy circle, an
 * inferred direction is a bearing; neither is a footprint. */
function hasExtent(feature) {
  const type = feature.geometry && feature.geometry.type;
  if (!type || type === 'Point' || type === 'MultiPoint') return false;
  return feature.representation !== 'inferred_direction' && feature.feature_type !== 'direction_line';
}

/**
 * The features of a map bundle that make up its principal footprint, and which tier
 * they came from: 'primary' (rings, outlines, arrays …), 'secondary' (halls, caverns,
 * buildings) or null when the map draws nothing with an extent. Every one of them is a
 * geometry record of the map, drawn as the record is — nothing is invented here.
 */
export function footprintFeatures(bundle) {
  const drawn = ((bundle && bundle.features) || []).filter(hasExtent);
  const primary = drawn.filter((f) => PRIMARY_TYPES.includes(f.feature_type));
  if (primary.length) return { features: primary, tier: 'primary' };
  const secondary = drawn.filter((f) => SECONDARY_TYPES.includes(f.feature_type));
  if (secondary.length) return { features: secondary, tier: 'secondary' };
  return { features: [], tier: null };
}

/**
 * The footprint of `bundle` moved onto `target` ({ lat, lon, polar? }). `sourcePolar`
 * says the source map is drawn in a polar projection. Returns null when the map has no
 * footprint; otherwise
 *   { tier, centre: {lat, lon, widthM, heightM}, features: [{ id, name, featureType,
 *     geometry (translated), lengthM, areaM2, officialLengthM, accuracyM, representation,
 *     entityId }] }
 */
export function placeFootprint(bundle, target, sourcePolar = false) {
  const { features: all, tier } = footprintFeatures(bundle);
  if (!all.length) return null;
  // Two records that depict one tunnel (LEP's and the LHC's) are one shape on the
  // ground: drawn once, named for both.
  const merged = new Map();
  for (const f of all) {
    const key = JSON.stringify(f.geometry.coordinates);
    const seen = merged.get(key);
    if (seen) {
      const name = f.entity_name || f.name;
      if (!seen.names.includes(name)) seen.names.push(name);
    } else {
      merged.set(key, { feature: f, names: [f.entity_name || f.name] });
    }
  }
  const features = [...merged.values()].map(({ feature, names }) => ({ ...feature, entity_name: names.join(' / ') }));
  const points = features.flatMap((f) => vertices(f.geometry));
  const centre = boundsCentre(points, sourcePolar);
  const move = translator({ lat: centre.lat, lon: centre.lon, polar: sourcePolar }, target);
  return {
    tier,
    centre,
    features: features.map((f) => ({
      id: f.id,
      name: f.entity_name || f.name,
      featureType: f.feature_type,
      geometry: mapVertices(f.geometry, move),
      lengthM: f.measured ? f.measured.length_m : null,
      areaM2: f.measured ? f.measured.area_m2 : null,
      // The official figure the record's own length check was made against, when it has one.
      officialLengthM: (() => {
        const check = (f.checks || []).find((c) => c.kind === 'length' && c.expected_m != null);
        return check ? check.expected_m : null;
      })(),
      accuracyM: f.accuracy_m == null ? null : f.accuracy_m,
      representation: f.representation,
      entityId: f.entity_id || null,
    })),
  };
}
