// tour-data.js — the guided tours' pure parts: what a step asks the page to show, how its
// sentence is cut at the phrases its claims cover, which tours a topic belongs to, and
// how a referenced field is named for a reader. No DOM, no fetch, no state: the player
// (tours.js), the Tours list, the topic panel and the Node unit check all import it.
//
// The shape of a tour is amendment A28 (docs/HEP_ATLAS_ONTOLOGY.md) and `tours.json`
// (docs/HEP_ATLAS_BUNDLES.md). A step's `href` is the Atlas address the build wrote for
// it (`?y=<year>&sel=<id>#/map/<slug>`, `?y=<year>#/view/<name>/<arg>`, `?y=<year>#/<type>/<slug>`);
// the player applies the step through that address, so the route a step opens is the route
// a person would reach by following the link.

export const TOUR_ROUTE = 'tour';

/** `tour:higgs-hunt` -> `higgs-hunt`. */
export function tourSlug(id) {
  return String(id || '').replace(/^tour:/, '');
}

export function tourIdOf(slug) {
  return `tour:${slug}`;
}

/** The step a tour opens at: the 1-based `?step=` clamped into 1..count (1 when it is
 * missing or not a number). */
export function clampStep(step, count) {
  const n = Math.trunc(Number(step));
  const top = Math.max(1, Math.trunc(Number(count)) || 1);
  if (!Number.isFinite(n)) return 1;
  return Math.min(top, Math.max(1, n));
}

/** "7 steps · about 12 minutes". */
export function tourMeta(tour) {
  const steps = (tour.steps || []).length;
  const minutes = Number(tour.estimated_minutes);
  const parts = [`${steps} step${steps === 1 ? '' : 's'}`];
  if (Number.isFinite(minutes) && minutes > 0) parts.push(`about ${minutes} minute${minutes === 1 ? '' : 's'}`);
  return parts.join(' · ');
}

// ---------------------------------------------------------------- the step's route
// `href` is relative (`?y=2010#/view/beam-section/numi`), so it is read against a dummy
// origin; only its query and hash are used.
function readHref(href) {
  try {
    return new URL(String(href), 'http://atlas.invalid/atlas/');
  } catch (error) {
    return null;
  }
}

/**
 * What a step asks the page to show, read from its `href`:
 *   { year, sel, entity, stage }
 * `entity` is the route the page would open ({ type, slug }) or null, and `stage` says
 * which part of the page holds it: 'globe' (a selection beside the globe; also a step
 * with no route at all), 'map' (a local map, `sel` the feature in its drawer) or 'view'
 * (a full-stage view such as the beam section). The build lets a view beat a map and a
 * map beat a selection, and this follows its href rather than the step's own fields.
 */
export function stepTarget(step) {
  const target = { year: null, sel: null, entity: null, stage: 'globe' };
  if (!step) return target;
  const url = step.href ? readHref(step.href) : null;
  if (url) {
    const y = parseInt(url.searchParams.get('y'), 10);
    if (Number.isFinite(y)) target.year = y;
    const sel = url.searchParams.get('sel');
    if (sel) target.sel = sel;
    const match = /^#\/([a-z]+)\/(.+)$/.exec(url.hash || '');
    if (match) target.entity = { type: match[1], slug: decodeURIComponent(match[2]) };
  } else if (Number.isFinite(Number(step.year))) {
    target.year = Number(step.year);
  }
  if (target.entity) {
    if (target.entity.type === 'view') target.stage = 'view';
    else if (target.entity.type === 'map') target.stage = 'map';
  }
  return target;
}

// ------------------------------------------------------------ the step's sentences
/**
 * A step's text cut at the phrases its claims cover, as an ordered list of
 * `{ text, claims: [index, ...] }` segments that join back to the text exactly (a
 * segment with no claims is plain). Two claims whose phrases overlap split the overlap
 * into a segment that names both; a phrase that is not in the text (never expected: the
 * validator needs each to be a verbatim substring) simply marks nothing.
 */
export function coveredSegments(text, claims) {
  const body = String(text == null ? '' : text);
  const spans = [];
  (claims || []).forEach((claim, index) => {
    const phrase = claim && claim.covers;
    if (!phrase) return;
    const at = body.indexOf(phrase);
    if (at >= 0) spans.push({ start: at, end: at + phrase.length, index });
  });
  if (!spans.length) return [{ text: body, claims: [] }];
  const cuts = [...new Set([0, body.length, ...spans.flatMap((s) => [s.start, s.end])])].sort((a, b) => a - b);
  const segments = [];
  for (let i = 0; i + 1 < cuts.length; i += 1) {
    const [start, end] = [cuts[i], cuts[i + 1]];
    if (start === end) continue;
    const claimsHere = spans.filter((s) => s.start <= start && s.end >= end).map((s) => s.index);
    const last = segments[segments.length - 1];
    // Neighbours covered by the same claims read as one piece.
    if (last && last.claims.join() === claimsHere.join()) last.text += body.slice(start, end);
    else segments.push({ text: body.slice(start, end), claims: claimsHere });
  }
  return segments;
}

// --------------------------------------------------------- naming a referenced field
// Path segments that are the record's plumbing, not something a reader would name.
const PLUMBING = new Set(['value', 'quantity', 'key_specs']);

function spoken(segment) {
  const text = String(segment).replace(/_/g, ' ').trim();
  return text ? text.charAt(0).toUpperCase() + text.slice(1) : text;
}

/**
 * A reader's name for a dotted field path (`key_specs.Baseline`, `primary_beam.value.energy`,
 * `baselines.site:ash-river-nova-far-detector.distance`): the segments joined by " › ",
 * `value`, `quantity` and `key_specs` plumbing dropped, a record id replaced by its name (`nameOf(id)`
 * returns null for an id it does not know), a trailing "(far detector)" kept.
 */
export function fieldLabel(field, nameOf = () => null) {
  const segments = String(field || '').split('.').filter((s) => s && !PLUMBING.has(s));
  return segments.map((segment) => {
    if (/^[a-z_]+:[a-z0-9-]/.test(segment)) return nameOf(segment) || segment;
    return spoken(segment);
  }).join(' › ');
}

// ---------------------------------------------------- the tours that cover a topic
/** `topicId` and every topic below it (a tour on "neutrino oscillations" belongs under
 * "neutrino physics" too). `topics` is atlas.json's id -> record map. */
export function topicWithDescendants(topicId, topics) {
  const found = new Set([topicId]);
  let grew = true;
  while (grew) {
    grew = false;
    for (const topic of Object.values(topics || {})) {
      if (!found.has(topic.id) && topic.parent_id && found.has(topic.parent_id)) {
        found.add(topic.id);
        grew = true;
      }
    }
  }
  return found;
}

/**
 * The tours with a step about `topicId`: a step covers a topic when it selects the topic
 * itself, or selects a record (an experiment, a result) filed under it or under a topic
 * below it. `topicsOf(id)` names an entity's topic ids (atlas.json `topic_ids`, or the
 * results bundle's); nothing here is inferred from the tour's wording.
 * Returns `[{ tour, steps: [1-based step numbers] }]`, the most steps first, ties in
 * the authored order.
 */
export function toursCoveringTopic(topicId, tours, topics, topicsOf) {
  const wanted = topicWithDescendants(topicId, topics);
  const rows = [];
  tours.forEach((tour, order) => {
    const steps = [];
    (tour.steps || []).forEach((step, index) => {
      const selected = step.select;
      if (!selected) return;
      const own = selected.startsWith('topic:') ? [selected] : (topicsOf(selected) || []);
      if (own.some((id) => wanted.has(id))) steps.push(index + 1);
    });
    if (steps.length) rows.push({ tour, steps, order });
  });
  return rows.sort((a, b) => b.steps.length - a.steps.length || a.order - b.order)
    .map(({ tour, steps }) => ({ tour, steps }));
}

// ------------------------------------------------------------- reading a worked answer
/**
 * One line of a worked answer, for display: `name = value unit` from the line's own
 * `value`, never from `display`, which for a figure a record states in its quote is the
 * carrying field's text ("3600 kg" beside an 85 cm radius). A line from an Atlas field
 * says where it came from; a sourced constant carries its source; a computed line shows
 * its expression.
 */
export function calculationLine(line) {
  const value = line.value;
  const shown = typeof value === 'number' ? String(Number(value.toPrecision(12))) : String(value);
  const unit = line.unit ? ` ${line.unit}` : '';
  return {
    kind: line.expression ? 'computed' : line.ref ? 'atlas' : 'constant',
    name: line.name,
    valueText: `${shown}${unit}`,
    expression: line.expression || null,
    ref: line.ref || null,
    field: line.field || null,
    sources: line.sources || [],
  };
}
