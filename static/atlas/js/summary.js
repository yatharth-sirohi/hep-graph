// summary.js — a record's two summaries, and the toggle between them.
//
// Every record carries `summary.plain` (for a newcomer) and `summary.technical`. The
// plain one is the default; a small "Plain | Technical" toggle at the top of the record
// swaps every summary paragraph on the page in place (nothing re-renders, so open
// sections and scroll position stay), and the choice is remembered in localStorage
// (wrapped: a private window just forgets it). The same pass gives each paragraph its
// glossary terms (js/glossary.js): the first use of a term in the record's text is a
// button that opens its definition.
//
// A summary paragraph is built here, synchronously, with its plain text in place, so a
// panel never renders empty; `decorate()` runs after the panel is in the page.

import * as glossary from './glossary.js';

export const SUMMARY_KEY = 'hep-atlas.summary';
const MODES = ['plain', 'technical'];

let mode = readMode();

function readMode() {
  try {
    const stored = window.localStorage.getItem(SUMMARY_KEY);
    return MODES.includes(stored) ? stored : 'plain';
  } catch (error) {
    return 'plain';
  }
}

function writeMode(next) {
  try {
    window.localStorage.setItem(SUMMARY_KEY, next);
  } catch (error) {
    // Storage is unavailable; the choice lasts for this page only.
  }
}

export function summaryMode() {
  return mode;
}

/** `{ plain, technical }` for a record. The generated bundle keeps the plain summary
 * on the record (`summary.plain`) and moves the technical one into the lazily loaded
 * text bundle (`summary_technical`); the fixtures put both in the text bundle. */
export function summaryTexts(record, t) {
  const summary = (record && record.summary) || {};
  return {
    plain: summary.plain || (t && t.summary_plain) || null,
    technical: (t && t.summary_technical) || summary.technical || null,
  };
}

// Paragraph element -> { plain, technical }.
const texts = new WeakMap();

function textFor(entry) {
  if (mode === 'technical' && entry.technical) return { text: entry.technical, kind: 'technical' };
  if (entry.plain) return { text: entry.plain, kind: 'plain' };
  return { text: entry.technical || '', kind: 'technical' };
}

function fill(element) {
  const entry = texts.get(element);
  if (!entry) return;
  const { text, kind } = textFor(entry);
  element.textContent = text;
  element.dataset.summaryKind = kind;
  // Asked for the technical summary of a record that has none: the plain one is shown,
  // and the toggle says so.
  element.toggleAttribute('data-summary-fallback', mode === 'technical' && kind === 'plain');
}

/**
 * The summary paragraph of a record, or null when it has neither summary. `className`
 * goes on the <p>; `data-summary` marks it for decorate().
 */
export function summaryParagraph(record, t, className = '') {
  const entry = summaryTexts(record, t);
  if (!entry.plain && !entry.technical) return null;
  const element = document.createElement('p');
  if (className) element.className = className;
  element.setAttribute('data-summary', '');
  element.setAttribute('data-gloss', '');
  texts.set(element, entry);
  fill(element);
  return element;
}

function buildToggle(onChange) {
  const wrap = document.createElement('div');
  wrap.className = 'summary-toggle';
  const label = document.createElement('span');
  label.className = 'summary-toggle-label';
  label.id = `summary-toggle-label-${Math.random().toString(36).slice(2, 8)}`;
  label.textContent = 'Summary';
  const group = document.createElement('div');
  group.className = 'summary-toggle-group';
  group.setAttribute('role', 'group');
  group.setAttribute('aria-labelledby', label.id);
  for (const value of MODES) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'summary-toggle-btn';
    button.dataset.mode = value;
    button.textContent = value === 'plain' ? 'Plain' : 'Technical';
    button.addEventListener('click', () => onChange(value));
    group.appendChild(button);
  }
  const note = document.createElement('p');
  note.className = 'summary-toggle-note';
  note.hidden = true;
  note.textContent = 'No technical summary is recorded for this one, so the plain summary is shown.';
  wrap.append(label, group, note);
  return wrap;
}

/** Every summary paragraph of `container` takes the current mode's text and its
 * glossary terms (the first use of each term in the container's prose, in reading
 * order). Safe to call again: the paragraphs are refilled from scratch each time. */
async function refresh(container, toggle) {
  const paragraphs = [...container.querySelectorAll('[data-summary]')];
  for (const element of paragraphs) fill(element);
  for (const element of container.querySelectorAll('[data-hide-when]')) {
    element.hidden = element.dataset.hideWhen === mode;
  }
  if (toggle) {
    for (const button of toggle.querySelectorAll('.summary-toggle-btn')) {
      button.setAttribute('aria-pressed', String(button.dataset.mode === mode));
    }
    toggle.querySelector('.summary-toggle-note').hidden = !paragraphs.some((el) => el.hasAttribute('data-summary-fallback'));
  }
  const terms = await glossary.loadTerms();
  if (!terms.length || !container.isConnected) return;
  // The mode may have changed while the glossary loaded: annotate what is on the page.
  const seen = new Set();
  for (const element of container.querySelectorAll('[data-gloss]')) {
    if (element.hasAttribute('data-summary')) fill(element);
    glossary.annotate(element, seen, terms);
  }
}

/**
 * Called once per rendered record panel, right after it is in the page: adds the
 * toggle (when some summary has both versions) and the glossary terms.
 */
export function decorate(container) {
  glossary.closePopover({ restoreFocus: false });
  const paragraphs = [...container.querySelectorAll('[data-summary]')];
  let toggle = null;
  if (paragraphs.some((el) => { const e = texts.get(el); return e && e.plain && e.technical; })) {
    toggle = buildToggle((next) => {
      if (next === mode) return;
      mode = next;
      writeMode(next);
      glossary.closePopover({ restoreFocus: false });
      refresh(container, toggle);
    });
    const anchor = container.querySelector('.panel-section');
    if (anchor) anchor.before(toggle); else container.appendChild(toggle);
  }
  return refresh(container, toggle);
}
