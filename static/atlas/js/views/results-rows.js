// results-rows.js — "Results as a story": which results sit in which lane, how a mark
// is formed, and how a link, a search entry or a panel names the view. Pure data and
// arithmetic over atlas.json and results.json (no DOM, no fetch), so panels.js and the
// search can use it without loading the view itself, and the unit check can run it
// under Node.
//
//   #/view/results-story                every lane
//   #/view/results-story/<topic-slug>   one topic: its lane, or the lanes under it
//
// LANES. A lane is one Atlas topic, a physics question ("Neutrino oscillations", "Higgs
// physics"). A result stands in every lane whose topic it is filed under, or under a
// sub-topic of it, so a result that answers two questions is drawn in both (and says
// so). A result in no lane stands in a last lane, "Filed under other topics", so no
// result is dropped. The lane list is the one editorial choice here; the membership is
// the records' own `topic_ids`.
//
// MARKS. The form of a mark is the claim the record carries, `result_type`: an
// observation (or discovery, or first detection), evidence, a limit, or neutral for
// everything else. `result_type` is a structured field that A16 checks against the
// claim's own wording; the significance, where a record has one, is a sourced string
// and is only ever printed as written. Nothing here parses prose to decide a form.

export const VIEW_NAME = 'results-story';
// The owner names features; this is the working title, and the only place it is written.
export const WORKING_TITLE = 'Results as a story';

/** The lane topics, in the order they are drawn. Consecutive lanes under one root topic
 * form a group, headed by that root's name. */
export const LANE_TOPICS = [
  'topic:neutrino-oscillations',
  'topic:solar-neutrinos',
  'topic:sterile-neutrinos',
  'topic:high-energy-astrophysical-neutrinos',
  'topic:supernova-neutrinos',
  'topic:neutrino-interactions',
  'topic:cevns',
  'topic:higgs-physics',
  'topic:electroweak-physics',
  'topic:top-physics',
  'topic:qcd',
  'topic:collider-bsm-searches',
  'topic:cp-violation',
  'topic:b-physics',
  'topic:charm-physics',
  'topic:rare-kaon-physics',
  'topic:precision-and-rare-processes',
  'topic:dark-matter',
  'topic:heavy-ion-physics-qgp',
];

/** The id of the last lane, for results filed under none of the lane topics. */
export const OTHER_LANE = 'lane:other';

// ---------------------------------------------------------------- the topic tree
function parentOf(atlas, topicId) {
  const topic = (atlas.topics || {})[topicId];
  return topic && topic.parent_id ? topic.parent_id : null;
}

/** The topic and every topic below it. */
export function descendantsOf(atlas, topicId) {
  const out = new Set([topicId]);
  let grew = true;
  while (grew) {
    grew = false;
    for (const topic of Object.values(atlas.topics || {})) {
      if (topic.parent_id && out.has(topic.parent_id) && !out.has(topic.id)) {
        out.add(topic.id);
        grew = true;
      }
    }
  }
  return out;
}

/** The root topic above a topic (itself when it has no parent). */
export function rootOf(atlas, topicId) {
  let current = topicId;
  for (let hop = 0; hop < 8; hop += 1) {
    const parent = parentOf(atlas, current);
    if (!parent) return current;
    current = parent;
  }
  return current;
}

// -------------------------------------------------------------------- the mark
/** What the form of a mark says. The neutral mark is not a weaker claim: the record states no
 * claim level for a measurement, an anomaly or a milestone. */
export const FORMS = {
  observation: { key: 'observation', label: 'Observation', meaning: 'the paper claims an observation or a discovery' },
  evidence: { key: 'evidence', label: 'Evidence', meaning: 'the paper claims evidence, short of an observation' },
  limit: { key: 'limit', label: 'Limit', meaning: 'a limit or an exclusion; no signal claimed' },
  neutral: { key: 'neutral', label: 'Measurement, anomaly, milestone', meaning: 'no claim level recorded (not a weaker claim)' },
};

const FORM_OF_TYPE = {
  observation: 'observation', discovery: 'observation', first_detection: 'observation',
  evidence: 'evidence', limit: 'limit',
};

/** The form of a result's mark, from `result_type` and nothing else. */
export function markForm(result) {
  return FORMS[FORM_OF_TYPE[result.result_type] || 'neutral'];
}

// -------------------------------------------------------------------- the date
function dateString(result) {
  const date = result.date;
  const raw = date && typeof date === 'object' ? (date.date || date.value) : date;
  return /^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?/.exec(String(raw || ''));
}

/** When a result is drawn: `t` in years (2012.5 is mid-2012), the precision the record's
 * date string has, and its year. A year-only date is drawn at mid-year and says so. */
export function resultMoment(result) {
  const match = dateString(result);
  if (!match) return null;
  const year = Number(match[1]);
  if (!match[2]) return { t: year + 0.5, year, precision: 'year' };
  const month = Number(match[2]);
  if (!match[3]) return { t: year + (month - 0.5) / 12, year, precision: 'month' };
  const day = Number(match[3]);
  return { t: year + (month - 1) / 12 + (day - 1) / 365, year, precision: 'day' };
}

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

/** "4 July 2012", "June 1998" or "1998", as precise as the record's date. */
export function dateText(result) {
  const match = dateString(result);
  if (!match) return '';
  if (!match[2]) return match[1];
  const month = MONTHS[Number(match[2]) - 1];
  return match[3] ? `${Number(match[3])} ${month} ${match[1]}` : `${month} ${match[1]}`;
}

// ---------------------------------------------------------------- names and links
function stripParen(text) {
  return String(text || '').replace(/\s*\([^)]*\)/g, '').trim();
}

/** A short name for the experiment a result belongs to: its own name when it fits, else the
 * shortest alias that does ("LUX-ZEPLIN (LZ)" is "LUX-ZEPLIN", "Super-Kamiokande" stays). */
export function shortExperimentName(experiment, max = 14) {
  if (!experiment) return '';
  const name = stripParen(experiment.name);
  if (name.length <= max) return name;
  const fitting = (experiment.aliases || []).map(stripParen).filter((t) => t.length >= 2 && t.length <= max)
    .sort((a, b) => a.length - b.length);
  return fitting[0] || `${name.slice(0, max - 1).trimEnd()}…`;
}

/** The paper a result links to: arXiv first, then the DOI, then the official page. */
export function paperLink(result) {
  const publication = result.publication || {};
  if (publication.arxiv) return { href: `https://arxiv.org/abs/${publication.arxiv}`, label: `arXiv:${publication.arxiv}` };
  if (publication.doi) return { href: `https://doi.org/${publication.doi}`, label: `DOI ${publication.doi}` };
  if (publication.url) return { href: publication.url, label: 'the paper' };
  if (result.official_url) return { href: result.official_url, label: 'the collaboration’s result page' };
  return null;
}

export function viewHash(arg) {
  return arg ? `#/view/${VIEW_NAME}/${arg}` : `#/view/${VIEW_NAME}`;
}

// ------------------------------------------------------------------------ lanes
/** The route argument as `{ kind: 'all' }`, `{ kind: 'topic', topicId }` or `{ error }`. */
export function parseArg(atlas, arg) {
  const slug = String(arg || '').trim();
  if (!slug || slug === 'all') return { kind: 'all' };
  const topicId = `topic:${slug}`;
  if (!/^[a-z0-9-]+$/.test(slug) || !(atlas.topics || {})[topicId]) {
    return { error: `The Atlas has no topic called “${slug}”, so there are no results to tell as a story.` };
  }
  return { kind: 'topic', topicId };
}

function laneOf(atlas, topicId, results) {
  const below = descendantsOf(atlas, topicId);
  const root = atlas.topics[rootOf(atlas, topicId)];
  return {
    id: topicId,
    topicId,
    name: atlas.topics[topicId].name,
    group: root ? root.name : '',
    results: results.filter((r) => (r.topic_ids || []).some((t) => below.has(t))),
  };
}

/**
 * The lanes of a view, and the marks in them.
 *   scope all             every lane with a result, then the lane of results under none of them
 *   scope topic, a lane   that lane alone
 *   scope topic, above    the lanes below it, then a lane of whatever else is filed under it
 *   scope topic, neither  one lane for the topic itself (a topic no lane covers, e.g. reactor neutrinos)
 * Returns `{ lanes, results, total }`; `results` is every distinct result drawn: a result in two
 * lanes is one entry there and two marks.
 */
export function buildLanes(atlas, results, scope) {
  const dated = results.filter((r) => resultMoment(r));
  let lanes;
  if (scope.kind === 'all') {
    lanes = LANE_TOPICS.filter((id) => (atlas.topics || {})[id]).map((id) => laneOf(atlas, id, dated));
    const inLane = new Set(lanes.flatMap((lane) => lane.results.map((r) => r.id)));
    lanes.push({
      id: OTHER_LANE, topicId: null, name: 'Filed under other topics', group: 'Other topics',
      results: dated.filter((r) => !inLane.has(r.id)),
    });
  } else {
    const { topicId } = scope;
    if (LANE_TOPICS.includes(topicId)) {
      lanes = [laneOf(atlas, topicId, dated)];
    } else {
      const below = descendantsOf(atlas, topicId);
      lanes = LANE_TOPICS.filter((id) => below.has(id)).map((id) => laneOf(atlas, id, dated));
      const inLane = new Set(lanes.flatMap((lane) => lane.results.map((r) => r.id)));
      const rest = dated.filter((r) => (r.topic_ids || []).some((t) => below.has(t)) && !inLane.has(r.id));
      if (!lanes.length) {
        lanes = [laneOf(atlas, topicId, dated)];
      } else if (rest.length) {
        lanes.push({
          id: OTHER_LANE, topicId, name: `Other results under ${atlas.topics[topicId].name}`,
          group: atlas.topics[topicId].name, results: rest,
        });
      }
    }
  }
  lanes = lanes.filter((lane) => lane.results.length);
  const seen = new Map();
  for (const lane of lanes) for (const r of lane.results) if (!seen.has(r.id)) seen.set(r.id, r);
  return { lanes, results: [...seen.values()], total: seen.size };
}

/** The lanes each result stands in, by result id: `Map(resultId -> [lane, ...])`. */
export function lanesByResult(lanes) {
  const out = new Map();
  for (const lane of lanes) {
    for (const r of lane.results) {
      if (!out.has(r.id)) out.set(r.id, []);
      out.get(r.id).push(lane);
    }
  }
  return out;
}

/** How many results of each form a set of results holds. */
export function formCounts(results) {
  const counts = { observation: 0, evidence: 0, limit: 0, neutral: 0 };
  for (const r of results) counts[markForm(r).key] += 1;
  return counts;
}

// ------------------------------------------------------------ links and search
/** The link a topic panel offers: `{ slug, title, hint }`, or null when no result is filed under
 * the topic (or under a topic below it). `results` is the results bundle's list. */
export function storyLinkForTopic(atlas, topicId, results = []) {
  const topic = (atlas.topics || {})[topicId];
  if (!topic) return null;
  const below = descendantsOf(atlas, topicId);
  const count = results.filter((r) => resultMoment(r) && (r.topic_ids || []).some((t) => below.has(t))).length;
  if (!count) return null;
  return {
    slug: `${VIEW_NAME}/${topicId.split(':')[1]}`,
    title: 'See the results as a story',
    hint: `${count} result${count === 1 ? '' : 's'} on a timeline, grouped by physics question, each opening its paper`,
  };
}

/** Search rows of the view, the shape search.json rows take: one for every lane and for the topics
 * above them, and one for all of them. */
export function resultsSearchEntries(atlas) {
  const topics = atlas.topics || {};
  const ids = new Set(LANE_TOPICS.filter((id) => topics[id]));
  for (const id of [...ids]) ids.add(rootOf(atlas, id));
  const entries = [{
    type: 'view',
    id: `view:${VIEW_NAME}/all`,
    name: `${WORKING_TITLE}: every question`,
    aliases: [WORKING_TITLE, 'results timeline', 'timeline of results', 'discoveries timeline', 'results by year',
      'physics results story', 'evidence and observation timeline'],
    subtitle: 'Timeline of the Atlas’s results by physics question',
  }];
  for (const id of ids) {
    const name = topics[id].name;
    entries.push({
      type: 'view',
      id: `view:${VIEW_NAME}/${id.split(':')[1]}`,
      name: `${WORKING_TITLE}: ${name}`,
      // No alias starts with the topic's own name: a search for "Higgs" means the topic,
      // and the timeline is found by "Higgs timeline" or "timeline of Higgs results".
      aliases: [`timeline of ${name} results`, `results timeline: ${name}`, `results story: ${name}`,
        `story of ${name} discoveries`],
      subtitle: 'Results on a timeline',
    });
  }
  return entries;
}

/** Where "Back" goes from a pasted link: the topic when the view is about one. */
export function resultsParent(arg, atlas) {
  const scope = parseArg(atlas, arg);
  if (scope.kind !== 'topic') return null;
  return { route: { type: 'topic', slug: scope.topicId.split(':')[1] }, label: `Back to ${atlas.topics[scope.topicId].name}` };
}
