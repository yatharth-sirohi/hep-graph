// bibtex.js — a BibTeX entry for an Atlas result or document.
//
// Pure (no DOM, no fetch): panels call it through cite-panel.js, and the unit check
// runs it under Node.
//
// THE RULE  An entry is built only from fields the record carries: its DOI and arXiv
//   identifier, its title, the collaboration that produced it (or its authors, if a
//   record ever lists them), the journal if the record names one, and a year. A field
//   the record does not carry is left out, never guessed: no journal is inferred from a
//   DOI, no author from a document's owner, no year from an arXiv number. A record with
//   neither a DOI nor an arXiv identifier gets no entry at all (citationFor says why).
//
// THE TEXT  Titles are stored as the paper printed them, sometimes as TeX ($B^0_s \to
//   \mu^+\mu^-$) and sometimes as plain text with Unicode (B⁻ → τ⁻ with a barred nu, 13 TeV, 50%).
//   bibtexEscape() keeps TeX math as it is, escapes the characters TeX would read as
//   commands outside math (& % # _ { } ^ ~ \ < >), and turns the symbols a physicist's
//   title uses most (Greek letters, arrows, ±, ×, the superscript signs, the dashes)
//   into the TeX a classic pdfLaTeX + BibTeX build understands. Any other character is
//   left as UTF-8.

const GREEK = {
  α: 'alpha', β: 'beta', γ: 'gamma', δ: 'delta', ε: 'epsilon', ζ: 'zeta', η: 'eta', θ: 'theta', κ: 'kappa',
  λ: 'lambda', μ: 'mu', µ: 'mu', ν: 'nu', ξ: 'xi', π: 'pi', ρ: 'rho', σ: 'sigma', τ: 'tau', υ: 'upsilon',
  φ: 'phi', χ: 'chi', ψ: 'psi', ω: 'omega', Γ: 'Gamma', Δ: 'Delta', Θ: 'Theta', Λ: 'Lambda', Ξ: 'Xi',
  Π: 'Pi', Σ: 'Sigma', Υ: 'Upsilon', Φ: 'Phi', Ψ: 'Psi', Ω: 'Omega', ℓ: 'ell',
};
const SYMBOLS = {
  '→': '\\to', '←': '\\leftarrow', '↔': '\\leftrightarrow', '±': '\\pm', '×': '\\times', '·': '\\cdot',
  '−': '-', '√': '\\surd', '≈': '\\approx', '≤': '\\leq', '≥': '\\geq', '∼': '\\sim', '∞': '\\infty',
  '°': '^{\\circ}',
};
const SUPERSCRIPT = {
  '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9', '⁺': '+', '⁻': '-',
};
// Characters that are text in TeX, spelled the TeX way.
const TEXT_ESCAPES = {
  '&': '\\&', '%': '\\%', '#': '\\#', _: '\\_', '{': '\\{', '}': '\\}', $: '\\$',
  '\\': '\\textbackslash{}', '^': '\\textasciicircum{}', '~': '\\textasciitilde{}',
  '<': '\\textless{}', '>': '\\textgreater{}', '|': '\\textbar{}',
  '–': '--', '—': '---', '‘': '`', '’': "'", '“': '``', '”': "''", '…': '\\ldots{}',
};
const COMBINING_BAR = /[\u0304\u0305]/;

function balanced(text) {
  let depth = 0;
  for (let i = 0; i < text.length; i += 1) {
    if (text[i] === '\\') { i += 1; continue; }
    if (text[i] === '{') depth += 1;
    else if (text[i] === '}') { depth -= 1; if (depth < 0) return false; }
  }
  return depth === 0;
}

/** Splits at unescaped "$": [{ math, text }]. An odd number of "$" means none of them is math. */
function splitMath(text) {
  const positions = [];
  for (let i = 0; i < text.length; i += 1) {
    if (text[i] === '\\') { i += 1; continue; }
    if (text[i] === '$') positions.push(i);
  }
  if (!positions.length || positions.length % 2 === 1) return [{ math: false, text }];
  const parts = [];
  let cursor = 0;
  for (let k = 0; k < positions.length; k += 2) {
    const open = positions[k];
    const close = positions[k + 1];
    if (open > cursor) parts.push({ math: false, text: text.slice(cursor, open) });
    // An empty pair ("$$") is nothing: TeX would read it as the start of a display equation.
    if (text.slice(open + 1, close).trim()) parts.push({ math: true, text: text.slice(open + 1, close) });
    cursor = close + 1;
  }
  if (cursor < text.length) parts.push({ math: false, text: text.slice(cursor) });
  return parts;
}

/** The text of a non-math stretch as tokens: { math, text } where `math` tokens are bare TeX math. */
function escapeStretch(stretch) {
  const tokens = [];
  const push = (math, text) => {
    const previous = tokens[tokens.length - 1];
    if (math && previous && previous.math) previous.text += text;
    else tokens.push({ math, text });
  };
  const chars = [...stretch];
  for (let i = 0; i < chars.length; i += 1) {
    const ch = chars[i];
    const next = chars[i + 1];
    const base = GREEK[ch] ? `\\${GREEK[ch]}` : (/[A-Za-z]/.test(ch) ? ch : null);
    if (ch === '\\' && next === '$') {
      push(false, '\\$'); // an escaped dollar sign in TeX source is a dollar sign
      i += 1;
    } else if (base && next && COMBINING_BAR.test(next)) {
      push(true, `\\bar{${base}}`);
      i += 1;
    } else if (GREEK[ch]) {
      push(true, `\\${GREEK[ch]}`);
    } else if (SYMBOLS[ch]) {
      push(true, SYMBOLS[ch]);
    } else if (SUPERSCRIPT[ch]) {
      // A run of superscript characters is ONE superscript: "10⁻³" is 10^{-3}, not two (TeX refuses a double one).
      let run = ch;
      while (chars[i + 1] && SUPERSCRIPT[chars[i + 1]]) { i += 1; run += chars[i]; }
      push(true, `^{${[...run].map((c) => SUPERSCRIPT[c]).join('')}}`);
    } else if (TEXT_ESCAPES[ch]) {
      push(false, TEXT_ESCAPES[ch]);
    } else {
      push(false, ch);
    }
  }
  return tokens;
}

/**
 * Text for a BibTeX field value: TeX math ($...$) kept as written, every other character
 * that TeX would read as a command escaped, common physics symbols written as TeX.
 * Whitespace runs become one space. The result has balanced braces.
 */
export function bibtexEscape(value) {
  const text = String(value == null ? '' : value).replace(/\s+/g, ' ').trim();
  const out = [];
  const push = (math, body) => {
    const previous = out[out.length - 1];
    if (math && previous && previous.math) previous.text += body;
    else out.push({ math, text: body });
  };
  for (const part of splitMath(text)) {
    if (part.math && balanced(part.text)) {
      push(true, part.text);
    } else {
      // Unbalanced math is not trusted as TeX: its dollar signs are text.
      const stretch = part.math ? `$${part.text}$` : part.text;
      for (const token of escapeStretch(stretch)) push(token.math, token.text);
    }
  }
  return out.map((token) => (token.math ? `$${token.text}$` : token.text)).join('').replace(/ {2,}/g, ' ').trim();
}

/** For identifiers and links (doi, eprint, url): no escaping, but never an unbalanced brace. */
export function bibtexVerbatim(value) {
  return String(value == null ? '' : value).replace(/\s+/g, '').replace(/\{/g, '%7B').replace(/\}/g, '%7D');
}

/** A BibTeX key from an Atlas id ("result:atlas-higgs-observation-2012" -> "atlas-higgs-observation-2012"). */
export function bibtexKey(id) {
  return String(id).replace(/^[a-z]+:/, '').replace(/[^A-Za-z0-9:_.+-]+/g, '-');
}

const yearOf = (value) => {
  const text = value && typeof value === 'object' ? value.date : value;
  const match = /^(\d{4})/.exec(typeof text === 'string' ? text : '');
  return match ? match[1] : null;
};

/** The year an arXiv identifier says: 2207.03764 -> 2022 (new style, YYMM), astro-ph/0311046 -> 2003 and
 * hep-ex/9801007 -> 1998 (old style, YYMM too; the archive began in 1991). Null when it is neither. */
export function arxivYear(id) {
  const text = String(id == null ? '' : id).trim().replace(/^arxiv:\s*/i, '');
  const match = /^(\d{2})\d{2}\.\d{4,5}(?:v\d+)?$/.exec(text)
    || /^[a-z-]+(?:\.[A-Za-z-]+)?\/(\d{2})\d{2}\d{3}(?:v\d+)?$/.exec(text);
  if (!match) return null;
  const yy = Number(match[1]);
  return String(yy >= 91 ? 1900 + yy : 2000 + yy);
}

const clean = (value) => (typeof value === 'string' && value.trim() ? value.trim() : null);

/** Authors a record lists itself ({name} or a string each); nothing is read from anywhere else. */
function listedAuthors(record) {
  const list = record.authors || (record.publication && record.publication.authors) || (record.reference && record.reference.authors);
  if (!Array.isArray(list)) return [];
  return list.map((a) => clean(typeof a === 'string' ? a : a && a.name)).filter(Boolean);
}

/**
 * The BibTeX entry of a result or document record, or why there is none.
 *
 *   citationFor(record, { collaborations })   collaborations: id -> record (atlas.collaborations)
 *
 * `{ ok: true, key, type, fields, text, missing }`: `fields` are [name, value] pairs
 * (the values as written, before braces), `text` the entry and `missing` the fields a
 * reader would expect that the record does not carry. `{ ok: false, reason }` when the
 * record has neither a DOI nor an arXiv identifier.
 */
export function citationFor(record, { collaborations = {} } = {}) {
  const source = record.type === 'document' ? (record.reference || {}) : (record.publication || {});
  const doi = clean(source.doi);
  const arxiv = clean(source.arxiv) ? clean(source.arxiv).replace(/^arxiv:\s*/i, '') : null;
  if (!doi && !arxiv) {
    return {
      ok: false,
      reason: 'This record carries neither a DOI nor an arXiv identifier, so the Atlas offers no BibTeX entry for it. '
        + 'A citation needs one of them; the sources listed under “Sources” are where to look for it.',
    };
  }
  const title = clean(record.type === 'document' ? record.name : (record.title || record.name));
  const missing = [];

  // Who wrote it: the collaboration that produced a result, or authors the record lists.
  const listed = listedAuthors(record);
  const names = record.type === 'result'
    ? (record.collaboration_ids || []).map((id) => collaborations[id] && collaborations[id].name).filter(Boolean)
    : [];
  let author = null;
  if (listed.length) author = listed.map(bibtexEscape).join(' and ');
  else if (names.length) author = names.map((name) => `{${bibtexEscape(name)}}`).join(' and ');
  else missing.push('author');

  // When: the year it was published if the record says so, else the year of its own date. An entry
  // that cites only the arXiv preprint (no journal, no DOI) is dated by the preprint: the year in its
  // arXiv identifier, else the record's own preprint or announcement date. A `published` year (or a
  // publication date) that belongs to a journal
  // article the entry does not carry (LZ's first result: preprint 2022, published 2023) is not used.
  const journalField = clean(source.journal);
  const preprintOnly = Boolean(arxiv) && !doi && !journalField;
  let year;
  if (preprintOnly && record.type === 'result') {
    year = arxivYear(arxiv) || (record.date_kind === 'publication' ? null : yearOf(record.date));
  } else {
    const published = record.type === 'result' ? yearOf(record.published) : null;
    year = published || yearOf(record.date);
  }
  const published = record.type === 'result' && !preprintOnly ? yearOf(record.published) : null;
  if (!year) missing.push('year');
  const notes = [];
  if (record.type === 'result' && record.date_kind === 'announcement' && !published && yearOf(record.date)) {
    notes.push(`Announced ${typeof record.date === 'string' ? record.date : record.date.date}`);
  }
  const report = clean(source.report_number);
  if (report) notes.push(`Report number ${report}`);

  const journal = clean(source.journal);
  if (!journal) missing.push('journal');

  const fields = [];
  if (title) fields.push(['title', `{${bibtexEscape(title)}}`]);
  if (author) fields.push(['author', author]);
  if (journal) fields.push(['journal', bibtexEscape(journal)]);
  if (year) fields.push(['year', year]);
  if (doi) fields.push(['doi', bibtexVerbatim(doi)]);
  if (arxiv) {
    fields.push(['eprint', bibtexVerbatim(arxiv)]);
    fields.push(['archivePrefix', 'arXiv']);
  }
  const url = clean(source.url);
  if (url) fields.push(['url', bibtexVerbatim(url)]);
  if (notes.length) fields.push(['note', bibtexEscape(notes.join('; '))]);

  const type = journal ? 'article' : 'misc';
  const key = bibtexKey(record.id);
  const body = fields.map(([name, value], index) => `  ${name} = {${value}}${index < fields.length - 1 ? ',' : ''}`);
  return {
    ok: true, key, type, fields, missing, text: `@${type}{${key},\n${body.join('\n')}\n}`,
  };
}
