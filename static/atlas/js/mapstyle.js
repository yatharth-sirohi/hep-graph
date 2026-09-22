// mapstyle.js — the four independent visual encodings of the local-map view
// (docs/HEP_ATLAS_GEOMETRY.md §4) and the legend that explains all four.
//
// The four are deliberately carried by *different* channels so none of them
// can be mistaken for another:
//
//   feature type      line weight, fill, and the base hue
//   status at year    dash pattern (and hue for "grey"/"amber" lifecycles)
//   level             a pale casing drawn behind underground features
//   representation    stroke opacity plus a text badge naming the class
//
// Nothing here is colour-only: every encoding is also written out in the
// left-hand list row, the tooltip and the legend, because colour alone is
// not an accessible encoding (§23) and, on a map of real places, a reader
// who cannot tell "derived" from "surveyed" is being misled about evidence.

import { titleCase } from './model.js';

// --- feature type -----------------------------------------------------
// `fill: true` means the shape is a footprint and is drawn filled; lines are
// never filled. `arrow` adds an arrowhead at the far end of the line.
const TYPE_STYLES = {
  ring: { color: '#54c6ba', weight: 5, fill: false, label: 'Ring / tunnel', hint: 'thick line' },
  tunnel: { color: '#54c6ba', weight: 5, fill: false, label: 'Ring / tunnel', hint: 'thick line' },
  linac: { color: '#54c6ba', weight: 4, fill: false, arrow: true, label: 'Linac', hint: 'thick line with an arrowhead' },
  beamline: { color: '#7fd1e6', weight: 3, fill: false, arrow: true, label: 'Beamline', hint: 'line with an arrowhead' },
  transfer_line: { color: '#7fd1e6', weight: 3, fill: false, arrow: true, label: 'Transfer line', hint: 'line with an arrowhead' },
  hall: { color: '#f2b441', weight: 2, fill: true, label: 'Hall / cavern / building', hint: 'filled footprint' },
  cavern: { color: '#f2b441', weight: 2, fill: true, label: 'Hall / cavern / building', hint: 'filled footprint' },
  building: { color: '#f2b441', weight: 2, fill: true, label: 'Hall / cavern / building', hint: 'filled footprint' },
  experimental_area: { color: '#f2b441', weight: 2, fill: true, label: 'Experimental area', hint: 'filled footprint' },
  target_station: { color: '#f2b441', weight: 2, fill: true, label: 'Target station', hint: 'filled footprint' },
  shaft: { color: '#f2b441', weight: 2, fill: true, label: 'Shaft', hint: 'small filled footprint' },
  array: { color: '#c98bd6', weight: 2, fill: true, label: 'Array', hint: 'filled footprint' },
  string: { color: '#c98bd6', weight: 2, fill: true, label: 'String', hint: 'point or small footprint' },
  boundary: { color: '#98a3a9', weight: 2, fill: false, typeDash: '2 6', label: 'Boundary', hint: 'thin dashed outline' },
  level_outline: { color: '#98a3a9', weight: 2, fill: false, typeDash: '2 6', label: 'Level outline', hint: 'thin dashed outline' },
  road: { color: '#7d8b96', weight: 2, fill: false, label: 'Road', hint: 'thin line' },
  water: { color: '#6fa8dc', weight: 1.5, fill: true, label: 'Water', hint: 'filled area' },
  direction_line: {
    color: '#c98bd6', weight: 2.5, fill: false, typeDash: '1 7', arrow: true,
    label: 'Inferred direction', hint: 'dotted line with an arrowhead — not a structure',
  },
  other: { color: '#9aa7b0', weight: 2, fill: false, label: 'Other', hint: 'thin line' },
};

export function typeStyle(featureType) {
  return TYPE_STYLES[featureType] || TYPE_STYLES.other;
}

// --- status at the selected year --------------------------------------
// Keyed by the status `state_segments` resolves to at the selected year or
// range (model.js statusForTimeline), never by the build-time `status`.
const STATUS_STYLES = {
  active: { dash: null, label: 'Active', hint: 'solid' },
  upgrade: { dash: null, label: 'Upgrade', hint: 'solid' },
  construction: { dash: '10 6', color: '#f2b441', label: 'Under construction', hint: 'dashed amber' },
  commissioning: { dash: '10 6', color: '#f2b441', label: 'Commissioning', hint: 'dashed amber' },
  completed: { dash: null, color: '#98a3a9', label: 'Completed', hint: 'grey' },
  decommissioned: { dash: null, color: '#98a3a9', label: 'Decommissioned', hint: 'grey' },
  shutdown: { dash: null, color: '#98a3a9', label: 'Shut down', hint: 'grey' },
  proposed: { dash: '2 5', label: 'Proposed', hint: 'dotted' },
  approved: { dash: '2 5', label: 'Approved', hint: 'dotted' },
  planned: { dash: '2 5', label: 'Planned', hint: 'dotted' },
  // A structure that exists in this year while its entity has no recorded
  // operating state (a tunnel before its machine, a hall after its
  // experiment): drawn grey and finely dashed so it can never be read as running.
  unrecorded: { dash: '4 4', color: '#98a3a9', label: 'Structure present, no operating status recorded', hint: 'grey, finely dashed' },
};

export function statusStyle(status) {
  return STATUS_STYLES[status] || { dash: null, label: status ? titleCase(status) : 'No recorded status', hint: 'solid' };
}

// --- representation ---------------------------------------------------
// The evidence class behind the shape. `surveyed` and `georeferenced` are
// drawn at full strength; `derived` and anything approximate is drawn
// lighter *and* badged, because a reader must never take a computed shape
// for a measured one.
const REPRESENTATION_STYLES = {
  surveyed: { opacity: 1, badge: null, label: 'Surveyed', hint: 'coordinates published by the laboratory or a technical paper' },
  georeferenced: { opacity: 0.95, badge: null, label: 'Georeferenced', hint: 'traced from imagery or GIS by a third party, or from a georeferenced official plan' },
  derived: { opacity: 0.7, badge: 'derived', label: 'Derived', hint: 'computed from sourced parameters — lighter outline, badged "derived"' },
  inferred_direction: { opacity: 0.85, badge: 'inferred direction', label: 'Inferred direction', hint: 'a bearing, not a structure — dotted, badged, and labelled' },
};

export function representationStyle(representation) {
  return REPRESENTATION_STYLES[representation]
    || { opacity: 0.7, badge: representation || 'unclassified', label: titleCase(representation || 'unclassified'), hint: 'evidence class not recognised — drawn lighter and badged' };
}

export const LEVEL_KIND_LABEL = {
  surface: 'Surface', underground: 'Underground', sea: 'At sea',
  lake: 'In a lake', ice: 'In ice', mountain: 'In a mountain',
};

/** True when a level's features get the pale casing that marks "not at the
 * surface" — the level encoding, independent of type/status/representation. */
export function levelIsSubsurface(level) {
  return !!level && level.kind !== 'surface';
}

/**
 * The Leaflet path options for one feature, given the level it sits on, the
 * status resolved at the selected year, and whether it is being ghosted
 * (drawn only because "show features outside the selected year" is on).
 */
export function pathOptions(feature, { level, status, ghost = false } = {}) {
  const t = typeStyle(feature.feature_type);
  const s = statusStyle(status);
  const r = representationStyle(feature.representation);
  // Boundaries and inferred-direction lines keep their own dot pattern: it
  // is what identifies them as a boundary or as "not a structure", which
  // outranks showing status through the dash. Their status still reads from
  // the hue, the list row and the tooltip.
  const dash = t.typeDash || s.dash || null;
  const color = s.color || t.color;
  const opacity = (ghost ? 0.3 : 1) * r.opacity;
  return {
    color,
    weight: t.weight,
    opacity,
    dashArray: dash,
    fill: !!t.fill,
    fillColor: color,
    fillOpacity: t.fill ? (ghost ? 0.06 : 0.22) : 0,
    lineCap: 'round',
    lineJoin: 'round',
    interactive: true,
  };
}

/** The pale casing drawn *behind* a subsurface feature (the level encoding). */
export function casingOptions(feature, { ghost = false } = {}) {
  const t = typeStyle(feature.feature_type);
  return {
    color: '#f4f7f8',
    weight: t.weight + 6,
    opacity: ghost ? 0.08 : 0.22,
    dashArray: '14 10',
    fill: false,
    interactive: false,
    lineCap: 'butt',
  };
}

/** "±15 m · georeferenced" — the accuracy/representation string that §4
 *  requires in every tooltip and every list row. */
export function accuracyText(feature) {
  const r = representationStyle(feature.representation);
  if (feature.accuracy_m == null) {
    return feature.representation === 'inferred_direction'
      ? 'no positional accuracy — an inferred bearing, not a structure'
      : `accuracy not recorded · ${r.label.toLowerCase()}`;
  }
  return `±${feature.accuracy_m} m · ${r.label.toLowerCase()}`;
}

/** Rows for the legend, as plain data so the view can render them as text.
 *  Each row is [swatchClass, term, explanation]. */
export function legendGroups(levels) {
  const seenType = new Set();
  const typeRows = [];
  for (const key of ['ring', 'linac', 'beamline', 'hall', 'boundary', 'direction_line']) {
    const t = TYPE_STYLES[key];
    if (seenType.has(t.label)) continue;
    seenType.add(t.label);
    typeRows.push([`legend-type-${key}`, t.label, t.hint]);
  }
  const statusRows = [
    ['legend-status-active', 'Active', 'solid line'],
    ['legend-status-construction', 'Under construction / commissioning', 'dashed, amber'],
    ['legend-status-completed', 'Completed / decommissioned / shut down', 'grey'],
    ['legend-status-proposed', 'Proposed / approved', 'dotted'],
    ['legend-status-unrecorded', 'Structure present, no operating status recorded for the year', 'grey, finely dashed'],
    ['legend-status-outside', 'Not yet built, or already ended, in the selected year',
      'hidden — or ghosted, when “show features outside the selected year” is on'],
  ];
  const levelRows = (levels || []).map((level) => [
    levelIsSubsurface(level) ? 'legend-level-under' : 'legend-level-surface',
    level.name,
    levelIsSubsurface(level)
      ? 'drawn with a pale dashed casing behind it, and listed under this level'
      : 'drawn without a casing, and listed under this level',
  ]);
  const representationRows = ['surveyed', 'georeferenced', 'derived', 'inferred_direction']
    .map((key) => [`legend-rep-${key}`, REPRESENTATION_STYLES[key].label, REPRESENTATION_STYLES[key].hint]);
  representationRows.push(['legend-rep-point', 'Position only (a circle with a centre mark)',
    'no source gives this feature a footprint, so what is drawn is its position and a circle of '
    + 'its positional accuracy — the circle is the uncertainty, not the building']);
  return [
    { title: 'Feature type', note: 'What kind of thing the shape is.', rows: typeRows },
    { title: 'Status in the selected year', note: 'Read from the entity’s recorded history at the year on the timeline, not from a fixed label.', rows: statusRows },
    { title: 'Level', note: 'Two levels are never drawn on one unlabelled plane; use the level toggles and the depth diagram.', rows: levelRows },
    {
      title: 'Representation (what the shape is evidence of)',
      note: 'Every feature also carries its positional accuracy in metres.',
      rows: representationRows,
    },
  ];
}
