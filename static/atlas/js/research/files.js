// files.js — CSV text, JSON documents and file downloads for the research tools:
// the Compare table, the Results and Documents lists, and the BibTeX file.
//
// The text builders are pure (no DOM), so the unit check runs them under Node.
// downloadFile() is the only function that touches the page.

/** Prepended to a CSV so a spreadsheet reads it as UTF-8 (ν, ±, µ and the dashes survive). */
export const CSV_BOM = '\uFEFF';

// A cell that starts with one of these is read as a formula by a spreadsheet. The data is
// curated, but a downloaded file is opened in other people's spreadsheets: such a cell is
// prefixed with an apostrophe (the OWASP guidance), unless it is only a number.
const FORMULA_START = /^[=+\-@\t\r]/;
const PLAIN_NUMBER = /^[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?$/;

/** One CSV field, quoted as RFC 4180 asks: a field with a comma, a quote, a line break or an edge space is quoted, quotes doubled. */
export function csvField(value) {
  if (value == null) return '';
  let text = typeof value === 'string' ? value : String(value);
  if (FORMULA_START.test(text) && !PLAIN_NUMBER.test(text)) text = `'${text}`;
  if (/[",\r\n]/.test(text) || /^\s|\s$/.test(text)) return `"${text.replace(/"/g, '""')}"`;
  return text;
}

export function csvLine(fields) {
  return fields.map(csvField).join(',');
}

/** A metadata line of a CSV: "# text", on one line, never quoted (a quoted line would not read as a comment). */
export function csvComment(text) {
  return `# ${String(text).replace(/\s*[\r\n]+\s*/g, ' ').trim()}`;
}

/**
 * A whole CSV file: `preamble` lines (metadata: the data version, the access date, the
 * filter), the `header` row and the `rows`, CRLF-separated, with the BOM first.
 */
export function buildCsv({ preamble = [], header, rows }) {
  const lines = [
    ...preamble.map(csvComment),
    csvLine(header),
    ...rows.map(csvLine),
  ];
  return `${CSV_BOM}${lines.join('\r\n')}\r\n`;
}

/** A JSON document with its metadata first. */
export function buildJson(meta, rows) {
  return `${JSON.stringify({ meta, rows }, null, 2)}\n`;
}

/** The reader's local date as YYYY-MM-DD: the "accessed" date of a download. */
export function accessDate(now = new Date()) {
  const two = (n) => String(n).padStart(2, '0');
  return `${now.getFullYear()}-${two(now.getMonth() + 1)}-${two(now.getDate())}`;
}

/** A file name from parts: lower case, letters and digits, hyphens. */
export function fileName(parts, extension) {
  const stem = parts
    .map((part) => String(part).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, ''))
    .filter(Boolean)
    .join('-');
  return `${stem || 'hep-atlas'}.${extension}`;
}

/** Saves `text` as a file the reader chose to download (a Blob and a link; nothing is sent anywhere). */
export function downloadFile(name, text, mime) {
  const blob = new Blob([text], { type: `${mime};charset=utf-8` });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = name;
  link.rel = 'noopener';
  link.hidden = true;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 30000);
}
