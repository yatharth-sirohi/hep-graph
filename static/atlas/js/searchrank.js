// searchrank.js — how the search box (search.js) matches and ranks a query.
//
// A query is read as words, not as one string. Text and query are folded the
// same way (case, accents, superscripts and punctuation all dropped), so
// "prevessin", "Prévessin" and "PREVESSIN" are one thing and "Super Kamiokande"
// finds "Super-Kamiokande".
//
//   1. Every word has to match (AND), each against the entry's name, its
//      aliases, its subtitle ("Observation · 2012") or — for experiments,
//      facilities and results — the names of the research topics the Atlas
//      files it under. That last step is what lets "Higgs"
//      reach ATLAS, CMS and CERN, and the CMS discovery paper whose own title
//      never says "Higgs". It uses only relations already in the data
//      (`topic_ids` on experiments and results, `experiment_ids` on
//      facilities); nothing is invented, and a row found this way says
//      which topic it came through.
//   2. Entries that match every word only once the words are relaxed (a plural
//      or a verb ending dropped: "neutrinos" -> "neutrino", "discovered" ->
//      "discover"; "discovery" also reads as "observation", the word the Atlas
//      uses for a discovery paper) follow the ones that match as typed.
//   3. If nothing matches every word either way, entries matching any word are
//      listed, those matching the most words first. A list that is never
//      empty while some word matches something: "No matches" is only said when
//      no word of the query is in the Atlas at all.
//
// Rows are ordered by how directly they answer: an exact or prefix match on a
// name or alias first (as before), then the words together in a name or alias,
// then spread over name and subtitle, then through a topic. The type order
// (experiment before facility before ...) and shorter names break ties.

//: Which kind of thing a person most likely means when several records match.
export const TYPE_ORDER = ['experiment', 'facility', 'collaboration', 'site', 'detector',
  'accelerator', 'beamline', 'topic', 'result', 'document', 'institution'];

// Question words and fillers: "where was the Higgs discovered" is about the
// Higgs and a discovery. Dropped only while some other word remains.
const STOPWORDS = new Set([
  'a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'and', 'or', 'is', 'was', 'were', 'are', 'be',
  'by', 'with', 'from', 'what', 'where', 'when', 'who', 'which', 'how', 'why', 'did', 'do', 'does',
  'it', 'its', 'about', 'this', 'that', 'as', 'into',
]);

// Query words that also mean something the Atlas files under another word,
// keyed by the relaxed (stemmed) form. Kept deliberately tiny.
const SYNONYMS = new Map([
  ['discover', ['observation']],
]);

/** Lower-case, accent-free, superscript-free text. */
export function fold(text) {
  return String(text == null ? '' : text)
    .normalize('NFKD')
    .replace(/\p{M}+/gu, '')
    .toLowerCase()
    .replace(/ß/g, 'ss')
    .replace(/æ/g, 'ae')
    .replace(/œ/g, 'oe')
    .replace(/[øð]/g, 'o')
    .replace(/[łŀ]/g, 'l')
    .replace(/đ/g, 'd');
}

/** Words of a text: runs of letters and digits. */
export function tokenize(text) {
  return fold(text).split(/[^\p{L}\p{N}]+/u).filter(Boolean);
}

/** A word with a plural or verb ending taken off ("oscillations" ->
 * "oscillation", "discovered" -> "discover"), when four letters or more are
 * left. Matched as a word *prefix*, so "oscillat" still finds "oscillation". */
export function stem(word) {
  for (const suffix of ['ies', 'ing', 'ed', 'es', 's', 'y']) {
    if (word.length - suffix.length >= 4 && word.endsWith(suffix)) {
      return word.slice(0, word.length - suffix.length);
    }
  }
  return word;
}

function typeRank(type) {
  const at = TYPE_ORDER.indexOf(type);
  return at < 0 ? TYPE_ORDER.length : at;
}

// One searchable piece of text: its words and, for words of three letters or
// more, the text with spaces and punctuation squeezed out ("superkamiokande").
function piece(text) {
  const words = tokenize(text);
  return { words, squeezed: words.join('') };
}

function pieceQuality(pieces, variant) {
  // 0 a whole word, 1 the start of a word, 2 inside a word or across a hyphen.
  let best = Infinity;
  for (const { words, squeezed } of pieces) {
    for (const word of words) {
      if (word === variant) return 0;
      if (best > 1 && word.startsWith(variant)) best = 1;
    }
    if (best > 2 && variant.length >= 3 && squeezed.includes(variant)) best = 2;
  }
  return best;
}

/** Builds the matcher over the search entries. `related` maps an entry id to
 * the research topics it is filed under: `{ id -> [{ name, aliases }] }`. */
export function createMatcher(entries, related = new Map()) {
  const rows = entries.map((entry) => {
    const own = [piece(entry.name), ...(entry.aliases || []).map(piece)];
    const topics = (related.get(entry.id) || []).map((topic) => ({
      name: topic.name,
      pieces: [piece(topic.name), ...(topic.aliases || []).map(piece)],
    }));
    return {
      entry,
      own,
      ownKeys: [tokenize(entry.name).join(' '), ...(entry.aliases || []).map((a) => tokenize(a).join(' '))],
      subtitle: [piece(entry.subtitle)],
      topics,
      rank: typeRank(entry.type),
    };
  });

  /** For one row and one word (with its spellings): where it is found. */
  function locate(row, variants) {
    let best = { level: Infinity, quality: Infinity, via: null };
    const consider = (level, quality, via) => {
      if (level < best.level || (level === best.level && quality < best.quality)) best = { level, quality, via };
    };
    for (const variant of variants) {
      const own = pieceQuality(row.own, variant);
      if (own < Infinity) consider(0, own, null);
      const sub = pieceQuality(row.subtitle, variant);
      if (sub < Infinity) consider(1, sub, null);
      // Through a topic only a whole word counts: "super" is not "supernova", and
      // "w" is not the W of "electroweak" — a topic should vouch for a word, not
      // for the start of one.
      if (variant.length >= 3) {
        for (const topic of row.topics) {
          if (pieceQuality(topic.pieces, variant) === 0) consider(2, 0, topic.name);
        }
      }
    }
    return best;
  }

  function score(row, wordVariants, phrase) {
    const located = wordVariants.map((variants) => locate(row, variants));
    const matched = located.filter((l) => l.level < Infinity);
    if (!matched.length) return null;
    const complete = matched.length === wordVariants.length;
    const level = Math.max(...matched.map((l) => l.level));
    const quality = matched.reduce((sum, l) => sum + l.quality, 0);
    let tier;
    if (complete && phrase) {
      if (row.ownKeys.includes(phrase)) tier = 0;
      else if (row.ownKeys.some((key) => key.startsWith(phrase))) tier = 1;
      else if (row.ownKeys.some((key) => key.includes(phrase))) tier = 2;
    }
    if (tier === undefined) tier = 3 + level;
    const via = matched.find((l) => l.via);
    return {
      row, complete, count: matched.length, tier, quality, via: level === 2 && via ? via.via : null,
    };
  }

  const byRank = (a, b) => a.tier - b.tier
    || a.quality - b.quality
    || a.row.rank - b.row.rank
    || a.row.entry.name.length - b.row.entry.name.length;

  /** Entries answering `query`, best first, as `{ entry, via }` (`via` names
   * the topic an entry was reached through, else null). */
  return function search(query, limit = 40) {
    const allWords = tokenize(query);
    if (!allWords.length) return [];
    const phrase = allWords.join(' ');
    const meaningful = allWords.filter((word) => !STOPWORDS.has(word));
    const words = meaningful.length ? meaningful : allWords;

    const asTyped = words.map((word) => [word]);
    const relaxed = words.map((word) => {
      const root = stem(word);
      return [...new Set([word, root, ...(SYNONYMS.get(root) || [])])];
    });

    // Words as typed first; then the relaxed spellings add whatever else matches
    // every word, after all of those (a sentence about a "discovered" Higgs
    // still reaches the "Observation of ..." papers, but "discovery" papers
    // that say exactly that stay on top).
    const exact = rows.map((row) => score(row, asTyped, phrase)).filter((s) => s && s.complete);
    const seen = new Set(exact.map((s) => s.row));
    const looser = rows.filter((row) => !seen.has(row)).map((row) => score(row, relaxed, phrase))
      .filter((s) => s && s.complete)
      .map((s) => ({ ...s, tier: s.tier + 10 }));
    if (exact.length || looser.length) {
      return [...exact, ...looser].sort(byRank).slice(0, limit).map((s) => ({ entry: s.row.entry, via: s.via }));
    }
    const any = rows.map((row) => score(row, relaxed, null)).filter(Boolean);
    return any
      .sort((a, b) => b.count - a.count || byRank(a, b))
      .slice(0, limit)
      .map((s) => ({ entry: s.row.entry, via: s.via }));
  };
}

/** The research topics each searchable record is filed under, from the Atlas's
 * own relations: an experiment's and a result's `topic_ids`, and a facility's
 * through the experiments it hosts. (A collaboration is not given topics: it is
 * its experiment under another name, and listing both would double every row.) */
export function buildRelatedTopics(atlas, results = []) {
  const topics = atlas.topics || {};
  const topicRecords = (ids) => [...new Set(ids)].map((id) => topics[id]).filter(Boolean)
    .map((topic) => ({ name: topic.name, aliases: topic.aliases || [] }));
  const experimentTopics = (experimentIds) => (experimentIds || [])
    .flatMap((id) => (atlas.experiments && atlas.experiments[id] ? atlas.experiments[id].topic_ids || [] : []));
  const related = new Map();
  const put = (id, ids) => {
    const list = topicRecords(ids);
    if (list.length) related.set(id, list);
  };
  for (const experiment of Object.values(atlas.experiments || {})) put(experiment.id, experiment.topic_ids || []);
  for (const facility of Object.values(atlas.facilities || {})) put(facility.id, experimentTopics(facility.experiment_ids));
  for (const result of results) put(result.id, result.topic_ids || []);
  return related;
}
