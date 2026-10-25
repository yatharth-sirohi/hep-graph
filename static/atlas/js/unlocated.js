// unlocated.js — how a local map words an entity it does not draw.
//
// The geometry bundle records, for every entity a facility accounts for but the
// map cannot place, a `reason` and a `backlog`. They were written as a research
// log: record ids (`src:…`, `geometry:…`), the HTTP status a page returned, the
// session an extract was made in, the Overpass query that came back empty, and a
// "to do" list. That is honest, but it is not what a reader of a map is asking,
// which is simply "why is this not drawn?". So the reader gets one plain
// sentence, and the research stays one click away, in full, under
// "Research notes". Nothing is invented here: the sentence is lifted from the
// recorded reason, with ids turned into the names they stand for.
//
// Pure functions, no DOM: localmap.js does the rendering.

const ID_PREFIXES = 'src|source|geometry|beamline|site|facility|experiment|detector|accelerator|'
  + 'collaboration|institution|topic|map|result|document';
const ID_PATTERN = new RegExp(`\\b(?:${ID_PREFIXES}):[a-z0-9][a-z0-9_.\\-]*[a-z0-9]`, 'gi');

/** Every record id mentioned in `text`, in order, without repeats. */
export function recordIds(text) {
  return [...new Set(String(text || '').match(ID_PATTERN) || [])];
}

/**
 * `text` with each record id replaced by the name `resolve(id)` gives it, or
 * removed (with the brackets, "see" and commas it leaves dangling) when it has
 * no name. `entity_id` — a field name that leaked into prose — goes too.
 */
export function namedText(text, resolve) {
  let out = String(text || '').replace(ID_PATTERN, (id) => {
    const name = resolve ? resolve(id) : null;
    return name || '\u0000';
  });
  out = out.replace(/\bentity_id\s+/g, '');
  if (out.includes('\u0000')) {
    out = out
      .replace(/\s*\((?:see |cf\. |in )?\s*(?:\u0000[,;\s]*)+\)/g, '')
      .replace(/(?:,\s*|\s+and\s+|\s+or\s+)?\bsee\s+\u0000/gi, '')
      .replace(/\s*,?\s*\u0000/g, '')
      .replace(/\s*\(\s*\)/g, '');
  }
  return out.replace(/\s+([,;.:])/g, '$1').replace(/\s{2,}/g, ' ').trim();
}

// Words that make a clause a note about how the research went, not about the
// place. A clause that still has one after the rewrites below is left for the
// research notes.
const LOG_WORDS = new RegExp([
  'HTTP\\s*\\d{3}', 'this session', 'Overpass', 'web ?search', 'WebFetch', 'WebSearch',
  'connection refused', '\\bOSM (?:way|node|relation|API|name search|extract)', '\\bways? \\d{6,}',
  'Gaps stream', 'Release pass', '(?:First|Second|Third) pass', '\\b20\\d\\d-\\d\\d-\\d\\d\\b',
  'returned (?:zero|no|an? )', 're-?fetched', 'unreachable',
].join('|'), 'i');

const LOG_PAREN = /\s*\([^()]*(?:HTTP\s*\d{3}|this session|Overpass|web ?search|WebFetch|\bOSM (?:way|node|name search|extract|API)|\b20\d\d-\d\d-\d\d\b|already cited|existing placement record|its own facility_roles)[^()]*\)/gi;

/** Rewrites that drop a how-we-looked phrase and leave the finding standing:
 *  "no trace was found in two targeted Overpass queries" → "no trace was found". */
function withoutLogPhrases(clause) {
  return clause
    .replace(LOG_PAREN, '')
    .replace(/\s+(?:in|by|from|after|via)\s+(?:two |three |four |a |an |the )?(?:targeted |fresh |case-insensitive )*(?:Overpass|OSM API|OpenStreetMap API)[^;:.]*$/i, '')
    .replace(/\s+(?:in|during|from) this session(?:'s extract)?\b/gi, '')
    .replace(/\s+this session\b/gi, '')
    .replace(/\s+/g, ' ')
    .trim();
}

// ---------------------------------------------------------------- splitting

/** Index list of positions in `text` that are outside every bracket and quote. */
function depthZero(text) {
  const flags = new Array(text.length).fill(false);
  let depth = 0;
  let quote = null;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (quote) {
      if (ch === quote) quote = null;
    } else if (ch === '(' || ch === '[') depth += 1;
    else if ((ch === ')' || ch === ']') && depth > 0) depth -= 1;
    else if ((ch === '"' || ch === '“') && depth === 0) quote = ch === '"' ? '"' : '”';
    // A straight apostrophe is far more often an apostrophe than a quote mark;
    // only a quote that opens a word counts.
    else if (ch === "'" && depth === 0 && (i === 0 || /[\s(\[]/.test(text[i - 1]))) quote = "'";
    flags[i] = depth === 0 && !quote;
  }
  return flags;
}

// A full stop ends a sentence unless it ends an abbreviation, an initial or a
// figure number ("Vol. II", "A. C. Mezger", "Fig. 2", "e.g. …").
const ABBREVIATION = /(?:\b(?:Vol|Fig|Figs|Sec|Sect|No|Nos|approx|ca|cf|vs|Dr|St|Mt|Ref|Table|Eq|Eqs|pp|p|al)|\be\.g|\bi\.e|\b[A-Z])\.$/;

export function splitSentences(text) {
  const raw = String(text || '').replace(/\s+/g, ' ').trim();
  if (!raw) return [];
  const flags = depthZero(raw);
  const out = [];
  let start = 0;
  for (let i = 0; i < raw.length; i += 1) {
    if (raw[i] !== '.' || !flags[i]) continue;
    if (raw[i + 1] && raw[i + 1] !== ' ') continue;
    const head = raw.slice(start, i + 1);
    if (ABBREVIATION.test(head)) continue;
    const rest = raw.slice(i + 1).trimStart();
    if (rest && !/^[A-Z"'“‘(]/.test(rest)) continue;
    out.push(head.trim());
    start = i + 1;
  }
  const tail = raw.slice(start).trim();
  if (tail) out.push(tail);
  return out;
}

/** Split at every depth-zero occurrence of one of `seps` (single characters),
 *  keeping each separator with the clause it introduces. */
function splitClauses(text, seps) {
  const flags = depthZero(text);
  const out = [];
  let start = 0;
  let sep = '';
  for (let i = 0; i < text.length; i += 1) {
    if (flags[i] && seps.includes(text[i]) && text[i + 1] === ' ') {
      out.push({ sep, text: text.slice(start, i).trim() });
      sep = text[i];
      start = i + 1;
    }
  }
  out.push({ sep, text: text.slice(start).trim() });
  return out.filter((c) => c.text);
}

function joinClauses(clauses) {
  return clauses.map((c, i) => (i ? `${c.sep} ${c.text}` : c.text)).join('');
}

// -------------------------------------------------------------------- pick

const WHY_CUE = /\b(?:no|not|none|nothing|only|never|cannot|without|neither|unpublished|unconfirmed|unknown|undrawn|unlocated)\b/i;
// A clause that leans on the sentence it was cut from ("None of the four…").
const DANGLING = /^(?:none|neither|they|them|it|its|this|that|these|those|such|both|their|there|have|has|had|the paper|the page)\b/i;
const MAX_ONE = 300;
const MAX_PART = 170;
const wordCount = (s) => s.split(/\s+/).filter(Boolean).length;

function sentenceCase(text) {
  const t = text.replace(/^[\s,;:\u2014-]+/, '').replace(/^(?:but|and|so|nor|yet)\s+/i, '');
  return t ? t[0].toUpperCase() + t.slice(1) : t;
}

function closed(text) {
  // No dangling bracket: a clause cut inside a parenthesis loses that bracket.
  let out = text;
  while ((out.match(/\(/g) || []).length > (out.match(/\)/g) || []).length) {
    out = out.slice(0, out.lastIndexOf('(')).trim();
  }
  return out.replace(/[\s,;:\u2014-]+$/, '');
}

function endStop(text) {
  return /[.!?\u2026]$/.test(text) ? text : `${text}.`;
}

/** `text` without its bracketed asides, nested ones included. */
function withoutParentheses(text) {
  let out = '';
  let depth = 0;
  for (const ch of text) {
    if (ch === '(') depth += 1;
    else if (ch === ')' && depth > 0) depth -= 1;
    else if (depth === 0) out += ch;
  }
  return out.replace(/\s+([,;.:])/g, '$1').replace(/\s{2,}/g, ' ').trim();
}

/** One sentence's plain content: log clauses removed, nothing left over a
 *  reader cannot use. Null when nothing is left. */
function plainSentence(sentence) {
  const kept = splitClauses(sentence, ';:')
    .map((c) => ({ ...c, text: withoutLogPhrases(c.text) }))
    .filter((c) => c.text && !LOG_WORDS.test(c.text));
  if (!kept.length) return null;
  kept[0] = { sep: '', text: kept[0].text };
  const text = joinClauses(kept).replace(/\.$/, '');
  return wordCount(text) >= 4 ? text : null;
}

/** `text` cut down to `limit` characters without changing what it says where
 *  it can: first its bracketed asides go, then everything but the clause that
 *  says why, and only then is it clipped (with an ellipsis). */
function fit(text, limit) {
  if (text.length <= limit) return text;
  const bare = withoutParentheses(text);
  if (bare.length <= limit && wordCount(bare) >= 4) return bare;
  const standsAlone = (c) => {
    const t = c.text.replace(/^(?:but|and|so|nor|yet)\s+/i, '');
    return WHY_CUE.test(t) && !DANGLING.test(t) && wordCount(t) >= 5 && t.length <= limit;
  };
  // The widest break that still leaves a clause that says why, then the finer.
  for (const seps of [';:\u2014', ';:\u2014,']) {
    const why = splitClauses(bare, seps).find(standsAlone);
    if (why) return sentenceCase(closed(why.text));
  }
  const clauses = splitClauses(bare, ';:\u2014,');
  let keep = 0;
  while (keep < clauses.length && joinClauses(clauses.slice(0, keep + 1)).length <= limit) keep += 1;
  const out = keep ? joinClauses(clauses.slice(0, keep).map((c, i) => (i ? c : { ...c, sep: '' })))
    : bare.slice(0, Math.max(bare.lastIndexOf(' ', limit), 1));
  return `${closed(out)}\u2026`;
}

/**
 * The plain reason a reader sees for why an entity is not drawn: the lead
 * sentence of the recorded reason, which names what is missing, and, when that
 * sentence only describes the thing, the first one that says what no source
 * gives. `resolve(id)` names a record id or returns null; `name` is the
 * entity's name, used only when nothing in the recorded reason reads plainly.
 */
export function plainReason(reason, { resolve, name } = {}) {
  const sentences = splitSentences(namedText(reason, resolve)).map(plainSentence).filter(Boolean);
  const lead = sentences.find((s) => !DANGLING.test(s)) || sentences[0];
  if (!lead) {
    return `No source we could read gives a verified position or outline for ${name || 'this'}, so it is not drawn.`;
  }
  if (WHY_CUE.test(lead)) return endStop(fit(lead, MAX_ONE));
  const why = sentences.find((s) => s !== lead && WHY_CUE.test(s));
  if (!why) return endStop(fit(lead, MAX_ONE));
  return `${endStop(fit(lead, MAX_PART))} ${endStop(fit(why, MAX_PART))}`;
}

/**
 * Everything the research notes hold, with record ids named: the full reason as
 * recorded, what would settle it (the backlog), and the raw ids for a
 * maintainer.
 */
export function researchNotes(row, resolve) {
  return {
    reason: namedText(row.reason, resolve),
    backlog: namedText(row.backlog, resolve),
    ids: recordIds(`${row.reason || ''} ${row.backlog || ''}`),
  };
}
