// scale-detectors.js — which detectors the true-scale line-up draws, and which
// recorded `specs` give each one its size. Pure data and arithmetic over atlas.json
// (no DOM, no fetch), so the view and the browser check read the same table.
//
// The ROSTER holds no sizes. It says, for each detector, what SHAPE to draw and which
// spec key supplies each dimension; every number comes from the detector's record
// (`specs.<key>`, a sourced quantity — its quote and sources are listed on the page).
// A detector whose record lacks a key is not drawn, and the view says so: a missing
// number is never filled in.

export const VIEW_NAME = 'detector-scale';
// The owner names features; this is the working title and the only place it is written.
export const WORKING_TITLE = 'Detector line-up';

/** Height of the person drawn beside every row, metres. A drawing convention, not data. */
export const PERSON_HEIGHT_M = 1.8;

/**
 * shape:
 *   'cylinder-v'  a cylinder standing on its end: width = diameter, height = height
 *   'cylinder-h'  a cylinder lying on its side: width = length, height = diameter
 *   'sphere'      a sphere: both = diameter
 *   'box'         a box seen from the side: width = length, height = height
 * `label` is the short name drawn under the shape (presentation, not a fact); `part`
 * names the piece of the instrument that is measured when it is not all of it.
 * `inner` is a second, inner outline of the same shape (a volume inside the first).
 */
export const ROSTER = [
  { id: 'detector:hyper-kamiokande', label: 'Hyper-Kamiokande', shape: 'cylinder-v', width: 'tank_diameter', height: 'tank_height', part: 'tank' },
  {
    id: 'detector:super-kamiokande', label: 'Super-Kamiokande', shape: 'cylinder-v', width: 'tank_diameter', height: 'tank_height', part: 'tank',
    inner: { width: 'inner_detector_diameter', height: 'inner_detector_height', part: 'inner detector' },
  },
  { id: 'detector:dune-far-detector-1', label: 'DUNE far-detector module', shape: 'box', width: 'cryostat_length', height: 'cryostat_height', part: 'one module’s cryostat' },
  { id: 'detector:nova-far-detector', label: 'NOvA far detector', shape: 'box', width: 'length', height: 'height', part: 'far detector' },
  { id: 'detector:atlas', label: 'ATLAS', shape: 'cylinder-h', width: 'length', height: 'diameter' },
  { id: 'detector:juno', label: 'JUNO', shape: 'sphere', width: 'central_detector_diameter', height: 'central_detector_diameter', part: 'central detector' },
  { id: 'detector:alice', label: 'ALICE', shape: 'box', width: 'length', height: 'diameter' },
  { id: 'detector:katrin', label: 'KATRIN', shape: 'cylinder-h', width: 'main_spectrometer_length', height: 'main_spectrometer_diameter', part: 'main spectrometer' },
  { id: 'detector:cms', label: 'CMS', shape: 'cylinder-h', width: 'length', height: 'diameter' },
  { id: 'detector:lhcb', label: 'LHCb', shape: 'box', width: 'length', height: 'height' },
  { id: 'detector:miniboone', label: 'MiniBooNE', shape: 'sphere', width: 'tank_diameter', height: 'tank_diameter', part: 'tank' },
  { id: 'detector:sno', label: 'SNO', shape: 'sphere', width: 'tank_diameter', height: 'tank_diameter', part: 'acrylic vessel' },
  { id: 'detector:lz', label: 'LZ', shape: 'cylinder-v', width: 'tank_diameter', height: 'tank_height', part: 'water shield' },
  { id: 'detector:star', label: 'STAR', shape: 'cylinder-h', width: 'length', height: 'diameter', part: 'TPC' },
];

/** IceCube is drawn on its own scale (its depth is a kilometre): the specs it reads. */
export const ICECUBE = {
  id: 'detector:icecube',
  depthMin: 'depth_min',
  depthMax: 'depth_max',
  volume: 'instrumented_volume',
  spacing: 'string_spacing',
  // The footprint comes from the geometry record that draws it on the South Pole map.
  footprintGeometry: 'geometry:icecube-array-footprint',
  footprintMap: 'map:amundsen-scott-south-pole-station',
};

const UNIT_TO_M = { m: 1, cm: 0.01, mm: 0.001, km: 1000, ft: 0.3048, in: 0.0254 };

/** A length quantity as metres, or null when it is not a number or not a length. */
export function metresOf(quantity) {
  if (!quantity || typeof quantity !== 'object') return null;
  if (typeof quantity.value !== 'number' || !Number.isFinite(quantity.value) || quantity.value <= 0) return null;
  if (quantity.dimension && quantity.dimension !== 'length') return null;
  const factor = UNIT_TO_M[quantity.unit];
  return factor ? quantity.value * factor : null;
}

/** `{ key, value (m), display, approx }` for one spec of a record, or null. */
export function lengthSpec(record, key) {
  const quantity = record && record.specs ? record.specs[key] : null;
  const metres = metresOf(quantity);
  if (metres == null) return null;
  return { key, metres, display: quantity.display || `${quantity.value} ${quantity.unit}`, approx: !!quantity.approx };
}

/**
 * The drawable line-up: for each ROSTER entry whose record carries every spec it needs,
 * its shape and dimensions; and for each one that does not, what was missing.
 */
export function buildLineup(atlas, roster = ROSTER) {
  const drawn = [];
  const skipped = [];
  for (const entry of roster) {
    const record = (atlas.detectors || {})[entry.id];
    if (!record) {
      skipped.push({ id: entry.id, name: entry.id, reason: 'the record is not in this data build' });
      continue;
    }
    const width = lengthSpec(record, entry.width);
    const height = lengthSpec(record, entry.height);
    const missing = [entry.width, entry.height].filter((key, i) => !(i === 0 ? width : height));
    if (missing.length) {
      skipped.push({ id: entry.id, name: record.name, reason: `its record has no sourced ${missing.join(' / ')}` });
      continue;
    }
    let inner = null;
    if (entry.inner) {
      const iw = lengthSpec(record, entry.inner.width);
      const ih = lengthSpec(record, entry.inner.height);
      // An inner outline that is missing or larger than the outer one is left out, not guessed.
      if (iw && ih && iw.metres <= width.metres && ih.metres <= height.metres) inner = { width: iw, height: ih, part: entry.inner.part };
    }
    drawn.push({
      id: entry.id, label: entry.label, record, shape: entry.shape, part: entry.part || null, width, height, inner,
    });
  }
  return { drawn, skipped };
}

/**
 * Shelf-pack the shapes into rows at one scale: tallest first, a new row when the next
 * slot would pass `rowWidthM`. A shape's slot is `slotOf(entry)` metres wide (at least
 * its own width: the view widens it to fit the label). Every row shares the scale; a
 * row's height is its tallest shape. Returns
 * [{ items: [{ entry, x (metres from the row's start to the slot) }], widthM, heightM }].
 */
export function packRows(entries, rowWidthM, gapM, slotOf = (entry) => entry.width.metres) {
  const sorted = entries.slice().sort((a, b) => b.height.metres - a.height.metres || b.width.metres - a.width.metres);
  const rows = [];
  let row = null;
  for (const entry of sorted) {
    const need = slotOf(entry);
    if (!row || (row.items.length && row.widthM + gapM + need > rowWidthM)) {
      row = { items: [], widthM: 0, heightM: 0 };
      rows.push(row);
    }
    const x = row.items.length ? row.widthM + gapM : 0;
    row.items.push({ entry, x });
    row.widthM = x + need;
    row.heightM = Math.max(row.heightM, entry.height.metres);
  }
  return rows;
}

/** Search rows, so the search box reaches the line-up. */
export function scaleSearchEntries() {
  return [{
    type: 'view',
    id: `view:${VIEW_NAME}`,
    name: WORKING_TITLE,
    aliases: ['detector sizes', 'detector scale', 'how big is a detector', 'detector size comparison',
      'scale comparison', 'detectors to scale', 'Super-Kamiokande size', 'ATLAS size', 'IceCube size'],
    subtitle: 'Detectors drawn at one true scale beside a person',
  }];
}
