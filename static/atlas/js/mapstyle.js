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
  // A temporary stop (the LHC's long shutdowns), not a closure: the ontology
  // reserves `decommissioned` and `completed` for the end of a thing's life, so
  // the reader must not take grey-and-"shut down" for either.
  shutdown: { dash: null, color: '#98a3a9', label: 'Temporarily shut down (long shutdown / upgrade)', hint: 'grey — a pause, not a closure' },
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
    ['legend-status-completed', 'Completed / decommissioned', 'grey'],
    ['legend-status-shutdown', 'Temporarily shut down (long shutdown / upgrade)', 'grey — a pause in operation, not a closure'],
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
    + 'its positional accuracy, labelled “position uncertainty ±N m — not the detector outline”: '
    + 'the circle is how well the position is known, not the size of the thing']);
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

// --- permanent labels -------------------------------------------------
// A shape that only names itself in a hover tooltip leaves a reader unable to
// tell the LHC from the SPS without hovering each one, so every drawn feature
// also carries a short permanent label. Which labels survive at a given zoom
// is decided in localmap.js (declutter, by `labelRank` and then size); what a
// label *says* is decided here, from the record's own names, never invented.

// Lower is more important. Rings and linacs are what the map is for, then the
// detector halls, caverns and tunnels that sit on them, then plain buildings,
// reference markers and the inferred bearings (which run long, so they come
// first among those), then the context outlines (campus boundaries, roads,
// water) that only get a label when nothing more important wants the room.
const LABEL_RANK = {
  ring: 0,
  linac: 1, beamline: 1, transfer_line: 1, array: 1,
  tunnel: 2, cavern: 2, hall: 2, experimental_area: 2, target_station: 2, string: 2, shaft: 2,
  building: 3, other: 3, direction_line: 3,
  boundary: 5,
  level_outline: 6,
  road: 7, water: 7,
};

// A site where an experiment's detector stands (an LHC point: ATLAS at Point 1,
// ALICE at Point 2, LHCb at Point 8) is one of the places a reader came to the
// map to find, so its label is a high-priority one, whatever kind of outline the
// build drew for it (review F17: CMS was labelled, ATLAS was not,
// because CMS's cavern is a point and ATLAS's site is a boundary polygon).
// They are placed ahead of the rings: a ring's label can stand at any of forty
// points along it, a small footprint's label at one of four beside it, so letting
// the rings choose first used to leave the footprint with nowhere to go.
const EXPERIMENT_SITE_RANK = -1;

export function labelRank(featureType, { experimentSite = false } = {}) {
  const rank = LABEL_RANK[featureType] != null ? LABEL_RANK[featureType] : 5;
  return experimentSite ? EXPERIMENT_SITE_RANK : rank;
}

// --- the circle around a position-only feature --------------------------------
// A Point is drawn as a circle of its positional accuracy. At KM3NeT/ARCA that
// is a 2 km ring on a map of an array a few hundred metres across, and next to
// the array's own label it read as the array. So the ring says what it is.

/** What the circle is not an outline of, from the kind of feature it surrounds. */
function outlineNoun(feature) {
  if (feature.entity_type === 'facility' || /\b(?:reference|site) marker\b/i.test(feature.name || '')) return 'site';
  if (['hall', 'cavern', 'building', 'shaft'].includes(feature.feature_type)) return feature.feature_type;
  return 'detector';
}

/** The three pieces of "position uncertainty ±2000 m — not the detector
 *  outline" (so a label can keep the figure and its unit on one line), or null
 *  when the feature has no recorded positional accuracy to state. */
export function uncertaintyParts(feature) {
  if (!(feature && feature.accuracy_m > 0)) return null;
  return {
    lead: 'position uncertainty',
    figure: `\u00b1${feature.accuracy_m} m`,
    tail: `\u2014 not the ${outlineNoun(feature)} outline`,
  };
}

/** "position uncertainty ±2000 m — not the detector outline", or '' when the
 *  feature has no recorded positional accuracy to state. */
export function uncertaintyLabel(feature) {
  const parts = uncertaintyParts(feature);
  return parts ? `${parts.lead} ${parts.figure} ${parts.tail}` : '';
}

/** True when every feature of a map is either a position with an accuracy
 *  circle or a derived stand-in shape, so nothing on it is a sourced outline
 *  and the reader needs the legend to know what the circles mean. */
export function isPositionOnlyMap(features) {
  const isPoint = (f) => f.geometry && (f.geometry.type === 'Point' || f.geometry.type === 'MultiPoint');
  return features.length > 0 && features.some(isPoint)
    && features.every((f) => isPoint(f) || f.representation === 'derived');
}

// Past this many characters a label wraps onto a second line (the CSS caps its
// width) rather than being cut short: a truncated "Hanbit Nuclear Power…" is
// the same on six different reactor buildings.
const LABEL_MAX = 36;
const DIRECTION_LABEL_MAX = 44;
const LABEL_HARD_MAX = 64;
// Words that describe how well a shape is known, not what it is. They belong
// in the tooltip and the list row (which carry the representation class), not
// on a label that has a few dozen characters to name a building.
const EVIDENCE_QUALIFIER = new RegExp([
  'derived', 'approximate', 'reference', 'surveyed', 'undifferentiated', 'unidentified',
  'identified', 'identity', 'candidate', 'partial', 'partially', 'context only', 'same tunnel',
  'former', 'decommissioned', 'OSM', 'map centre', 'walked', 'footprint', 'survey', 'marker',
  'inferred', 'point', 'centre of', 'shared with', 'second shaft', 'not confirmed', 'surface',
].map((word) => `\\b${word}\\b`).join('|'), 'i');

const NAME_SUFFIX = /,\s*(full ring|tunnel|building|convex hull(?: of [^,]*)?)\s*$/i;

function tidy(text) {
  return text.replace(/\s+/g, ' ').replace(/\s+,/g, ',').trim();
}

function dropQualifiers(text) {
  return tidy(text
    .replace(/\s*--\s*inferred\b.*$/i, '')
    .replace(/\s*\(([^()]*)\)/g, (whole, inner) => (EVIDENCE_QUALIFIER.test(inner) ? '' : whole))
    .replace(NAME_SUFFIX, ''));
}

/** A trailing "(R1)"-style tag is what tells the six Hanbit reactor buildings
 *  apart, so it survives shortening; a long trailing parenthetical does not. */
function splitTag(text) {
  const match = /^(.*?)\s*(\([^()]{1,8}\))$/.exec(text);
  return match ? { head: match[1], tag: match[2] } : { head: text, tag: '' };
}

function withoutParens(text) {
  return tidy(text.replace(/\s*\([^()]*\)/g, ''));
}

/** Shorten by dropping parentheticals and then everything after the first
 *  comma. Never cuts mid-name: if nothing fits `max`, the longest option under
 *  LABEL_HARD_MAX is returned and the label wraps. */
function shortened(text, max) {
  const { head, tag } = splitTag(text);
  const room = max - (tag ? tag.length + 1 : 0);
  const bare = withoutParens(head);
  const first = tidy(bare.split(',')[0]);
  const join = (option) => (tag ? `${option} ${tag}` : option);
  if (first && first.length <= room) return join(first);
  if (bare && bare.length <= room) return join(bare);
  if (join(bare).length <= LABEL_HARD_MAX) return join(bare);
  if (bare.length <= LABEL_HARD_MAX) return bare;
  let cut = bare.slice(0, LABEL_HARD_MAX - 1);
  const space = cut.lastIndexOf(' ');
  if (space > 20) cut = cut.slice(0, space);
  return `${cut.replace(/[\s,;:-]+$/, '')}\u2026`;
}

/** An entity name labels a feature well only when it picks out that one
 *  feature (three Daya Bay halls share one entity name) and names the thing
 *  itself rather than the laboratory or campus around it. */
function usableEntityName(feature, entityNameCounts) {
  if (!feature.entity_name || entityNameCounts.get(feature.entity_name) !== 1) return '';
  if (feature.entity_type === 'facility') return '';
  if (feature.feature_type !== 'boundary' && /\bcampus\b/i.test(feature.entity_name)) return '';
  const name = dropQualifiers(feature.entity_name);
  return name.length <= LABEL_MAX ? name : '';
}

/**
 * The text of one feature's permanent label.
 *
 * `entityNameCounts` maps an entity name to how many features of the map carry
 * it. Returns `{ text, sub }` — `sub` is the second line, used only for an
 * inferred direction, which §4 requires to say it is not a structure.
 */
export function labelText(feature, entityNameCounts = new Map(), { experimentSite = false } = {}) {
  const own = dropQualifiers(feature.name || feature.entity_name || feature.id);
  // An experiment's site is labelled by the site's own name — "LHC Point 1
  // (ATLAS cavern)" — which is what a reader looks for, and a line shorter than
  // the build's name for the outline ("CERN Point 1 surface site (ATLAS)").
  if (experimentSite && feature.entity_name) {
    const siteName = dropQualifiers(feature.entity_name);
    if (siteName && siteName.length <= LABEL_MAX) return { text: siteName, sub: '' };
  }
  if (feature.feature_type === 'direction_line') {
    const split = /^(.*?)\s*(?:beam\s+)?direction\s+toward\s+(.+)$/i.exec(own);
    let text = own;
    if (split) {
      const where = withoutParens(split[2]);
      const what = tidy(split[1]).replace(/\s*beam$/i, '');
      text = `${what} beam \u2192 ${where}`;
      if (text.length > DIRECTION_LABEL_MAX) text = `\u2192 ${where}`;
    } else if (text.length > DIRECTION_LABEL_MAX) {
      text = shortened(text, DIRECTION_LABEL_MAX);
    }
    return { text, sub: 'inferred direction \u2014 not a structure' };
  }
  if (own.length <= LABEL_MAX) return { text: own, sub: '' };
  const entity = usableEntityName(feature, entityNameCounts);
  return { text: entity || shortened(own, LABEL_MAX), sub: '' };
}

/** Labels for a whole map. Two features that would read identically after
 *  shortening (Pierre Auger's two arrays) fall back to their longer,
 *  qualifier-free names, which the label is allowed to wrap. */
export function labelsFor(features, { isExperimentSite = () => false } = {}) {
  const counts = new Map();
  for (const f of features) {
    if (f.entity_name) counts.set(f.entity_name, (counts.get(f.entity_name) || 0) + 1);
  }
  const labels = new Map(features.map((f) => [f.id, labelText(f, counts, { experimentSite: isExperimentSite(f) })]));
  const seen = new Map();
  for (const f of features) {
    const key = labels.get(f.id).text.toLowerCase();
    seen.set(key, (seen.get(key) || []).concat(f));
  }
  for (const group of seen.values()) {
    if (group.length < 2) continue;
    for (const f of group) {
      const full = dropQualifiers(f.name || f.entity_name || f.id);
      const current = labels.get(f.id);
      if (f.feature_type !== 'direction_line' && full.length > current.text.length) {
        labels.set(f.id, { text: full, sub: current.sub });
      }
    }
  }
  return labels;
}

// --- series: many records, one label --------------------------------------
// The instrument-level array maps split one detector into several records
// ("Auger SD1500 stations, band 3 of 20", "LHAASO ... block 7 of 15", "Baikal-GVD
// cluster 4"). Labelling each would put twenty near-identical chips over the very
// array they describe, so a run of three or more is labelled once, at the middle
// of the whole run.

const SERIES_PATTERN = /\b(band|block|strip|cluster|string|station|part|section)s?\s+(\d+)(?:\s*-\s*(\d+))?(?:\s+of\s+(\d+))?/i;
export const SERIES_MIN_MEMBERS = 3;

/** `{ key, prefix, noun, total }` when this feature's name is one numbered
 *  member of a series, else null. Parenthetical remarks do not take part. */
export function seriesOf(feature) {
  const name = (feature.name || '').replace(/\s*\([^()]*\)/g, '');
  const match = SERIES_PATTERN.exec(name);
  if (!match) return null;
  const prefix = name.slice(0, match.index).replace(/[\s,;:-]+$/, '');
  if (!prefix) return null;
  const tail = name.slice(match.index + match[0].length).replace(/[\s,;:-]+$/, '').trim();
  const noun = match[1].toLowerCase();
  return {
    key: `${feature.feature_type}|${prefix.toLowerCase()}|${noun}|${tail.toLowerCase()}`,
    prefix,
    noun,
    total: match[4] ? Number(match[4]) : null,
  };
}

/** "Auger SD1500 stations: 20 bands" — the one label of a whole series. */
export function seriesLabel(info, count) {
  const n = info.total || count;
  const noun = info.noun === 'station' ? 'station groups' : `${info.noun}${n === 1 ? '' : 's'}`;
  return `${info.prefix}: ${n} ${noun}`;
}
