// glossary.js — the built-in glossary.
//
// `glossary.json` (data/atlas/glossary/, docs/HEP_ATLAS_BUNDLES.md) holds about thirty
// terms the panels use (m.w.e., off-axis angle, CL, σ, baseline, luminosity, ...), each a
// plain definition resting on a verbatim quote from a named source. The first use of a
// term in a record's text becomes a button (dotted underline) that opens a small popover:
// the definition, the source as a link, where in the source, and the quote itself.
//
// Accessible by construction:
//   * the term is a real <button> (aria-haspopup="dialog", aria-expanded, a name that
//     starts with the visible text), so Tab reaches it and Enter or Space opens it;
//   * the popover is a labelled, described, non-modal dialog; focus moves into it when
//     it opens, Escape closes it and puts focus back on the term, and so do the close
//     button, a click outside, and tabbing past its last control;
//   * it is positioned by JavaScript, fixed to the viewport, so opening it moves nothing
//     in the text, on a laptop or a phone; and a term wraps to no extra width or padding.
// The glossary is an enhancement: if its bundle is missing or fails to load, panels read
// exactly as they did.

import * as loader from './loader.js';

let loading = null;

/** The compiled terms: `[{ id, title, definition, source, locator, quote, patterns }]`. */
export function loadTerms() {
  if (!loading) {
    loading = loader.getGlossary().then((bundle) => compile((bundle && bundle.terms) || [])).catch((error) => {
      window.console.warn('HEP Atlas glossary unavailable', error);
      loading = null;
      return [];
    });
  }
  return loading;
}

/** Compile a bundle's terms into matchers (exported for the unit tests). */
export function compile(terms) {
  const compiled = [];
  for (const term of terms) {
    const patterns = [];
    for (const entry of term.match || []) {
      const source = typeof entry === 'string' ? entry : entry && entry.pattern;
      if (!source) continue;
      const caseSensitive = typeof entry === 'object' && entry.case === true;
      try {
        patterns.push(new RegExp(source, caseSensitive ? 'gu' : 'giu'));
      } catch (error) {
        // A pattern this browser cannot compile: that spelling is simply not matched.
      }
    }
    if (patterns.length) compiled.push({ ...term, patterns });
  }
  return compiled;
}

const WORD = /[\p{L}\p{N}]/u;

/** The first match of `term` in `text` that stands alone (not inside a longer word):
 * `{ index, length }` or null. */
export function firstMatch(term, text) {
  let best = null;
  for (const pattern of term.patterns) {
    pattern.lastIndex = 0;
    let match = pattern.exec(text);
    while (match) {
      const start = match.index;
      const end = start + match[0].length;
      const before = start > 0 ? text[start - 1] : '';
      const after = end < text.length ? text[end] : '';
      if (match[0] && !(before && WORD.test(before)) && !(after && WORD.test(after))) {
        if (!best || start < best.index || (start === best.index && match[0].length > best.length)) {
          best = { index: start, length: match[0].length };
        }
        break;
      }
      pattern.lastIndex = start + 1;
      match = pattern.exec(text);
    }
  }
  return best;
}

/**
 * Turn the first use of each unseen term inside `root`'s text into a glossary button.
 * `seen` (a Set of term ids) is shared across the paragraphs of one record, so a term is
 * marked once per record; it is updated here.
 */
export function annotate(root, seen, terms) {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode: (node) => (node.parentElement && node.parentElement.closest('.gloss-term, a, button, summary')
      ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT),
  });
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const node of nodes) annotateNode(node, seen, terms);
}

function annotateNode(node, seen, terms) {
  let current = node;
  for (;;) {
    const text = current.nodeValue;
    let best = null;
    for (const term of terms) {
      if (seen.has(term.id)) continue;
      const hit = firstMatch(term, text);
      if (hit && (!best || hit.index < best.index || (hit.index === best.index && hit.length > best.length))) {
        best = { ...hit, term };
      }
    }
    if (!best) return;
    seen.add(best.term.id);
    const parent = current.parentNode;
    const shown = text.slice(best.index, best.index + best.length);
    const after = text.slice(best.index + best.length);
    if (best.index > 0) parent.insertBefore(document.createTextNode(text.slice(0, best.index)), current);
    parent.insertBefore(termButton(best.term, shown), current);
    if (!after) {
      parent.removeChild(current);
      return;
    }
    current.nodeValue = after;
  }
}

function termButton(term, shown) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'gloss-term';
  button.dataset.gloss = term.id;
  button.textContent = shown;
  button.setAttribute('aria-haspopup', 'dialog');
  button.setAttribute('aria-expanded', 'false');
  button.setAttribute('aria-label', `${shown}, definition`);
  button.addEventListener('click', (event) => {
    event.preventDefault();
    if (activeButton === button) closePopover(); else openPopover(button, term);
  });
  return button;
}

// ------------------------------------------------------------------ popover
let pop = null;
let activeButton = null;
let listening = false;

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text != null) node.textContent = text;
  return node;
}

function ensurePopover() {
  if (pop) return pop;
  pop = element('div', 'gloss-pop');
  pop.id = 'gloss-pop';
  pop.setAttribute('role', 'dialog');
  pop.setAttribute('aria-labelledby', 'gloss-pop-title');
  pop.setAttribute('aria-describedby', 'gloss-pop-def');
  pop.tabIndex = -1;
  pop.hidden = true;
  const title = element('p', 'gloss-pop-title');
  title.id = 'gloss-pop-title';
  const definition = element('p', 'gloss-pop-def');
  definition.id = 'gloss-pop-def';
  const source = element('p', 'gloss-pop-source');
  const quote = element('details', 'gloss-pop-quote');
  quote.append(element('summary', '', 'The source’s own words'), element('blockquote'));
  const close = element('button', 'gloss-pop-close', '×');
  close.type = 'button';
  close.setAttribute('aria-label', 'Close definition');
  close.addEventListener('click', () => closePopover());
  pop.append(title, definition, source, quote, close);
  pop.addEventListener('keydown', onPopoverKey);
  document.body.appendChild(pop);
  return pop;
}

function fillPopover(term) {
  pop.querySelector('.gloss-pop-title').textContent = term.title || term.term;
  pop.querySelector('.gloss-pop-def').textContent = term.definition;
  const source = pop.querySelector('.gloss-pop-source');
  source.textContent = '';
  if (term.source && term.source.url) {
    const link = element('a', '', term.source.title || term.source.url);
    link.href = term.source.url;
    link.target = '_blank';
    link.rel = 'noopener';
    source.append('Source: ', link);
    if (term.locator) source.append(` — ${term.locator}`);
  }
  const quote = pop.querySelector('.gloss-pop-quote');
  quote.hidden = !term.quote;
  quote.open = false;
  pop.querySelector('blockquote').textContent = term.quote || '';
}

/** Put the popover beside the term: below it when there is room, else above, clamped to
 * the viewport; fixed, so it never takes part in the page's layout. */
function place() {
  if (!pop || pop.hidden || !activeButton || !activeButton.isConnected) return;
  const rect = activeButton.getClientRects()[0] || activeButton.getBoundingClientRect();
  const viewportWidth = document.documentElement.clientWidth;
  const viewportHeight = window.innerHeight;
  if (rect.bottom < 0 || rect.top > viewportHeight) {
    closePopover({ restoreFocus: false });
    return;
  }
  const margin = 12;
  const width = pop.offsetWidth;
  const height = pop.offsetHeight;
  const left = Math.min(Math.max(margin, rect.left + rect.width / 2 - width / 2), Math.max(margin, viewportWidth - width - margin));
  const below = rect.bottom + 8;
  const above = rect.top - 8 - height;
  let top;
  if (below + height <= viewportHeight - margin) top = below;
  else if (above >= margin) top = above;
  else top = Math.max(margin, viewportHeight - height - margin);
  pop.style.left = `${Math.round(left)}px`;
  pop.style.top = `${Math.round(top)}px`;
}

function openPopover(button, term) {
  ensurePopover();
  if (activeButton) activeButton.setAttribute('aria-expanded', 'false');
  activeButton = button;
  fillPopover(term);
  pop.hidden = false;
  button.setAttribute('aria-expanded', 'true');
  button.setAttribute('aria-controls', 'gloss-pop');
  place();
  pop.focus({ preventScroll: true });
  if (!listening) {
    listening = true;
    document.addEventListener('keydown', onDocumentKey, true);
    document.addEventListener('pointerdown', onPointerDown, true);
    window.addEventListener('scroll', place, true);
    window.addEventListener('resize', place);
  }
}

/** Close the popover. Focus goes back to the term that opened it, unless something else
 * has taken it (a click elsewhere) or `restoreFocus` is false. */
export function closePopover({ restoreFocus = true } = {}) {
  if (!pop || pop.hidden) return;
  const hadFocus = pop.contains(document.activeElement);
  const button = activeButton;
  pop.hidden = true;
  activeButton = null;
  if (button) {
    button.setAttribute('aria-expanded', 'false');
    button.removeAttribute('aria-controls');
    if (restoreFocus && hadFocus && button.isConnected) button.focus({ preventScroll: true });
  }
  if (listening) {
    listening = false;
    document.removeEventListener('keydown', onDocumentKey, true);
    document.removeEventListener('pointerdown', onPointerDown, true);
    window.removeEventListener('scroll', place, true);
    window.removeEventListener('resize', place);
  }
}

// Escape closes this before it closes anything behind it (the record panel's own Escape
// is a bubbling listener on the document, which this capture-phase stop never reaches).
function onDocumentKey(event) {
  if (event.key !== 'Escape' || !pop || pop.hidden) return;
  event.stopPropagation();
  event.preventDefault();
  closePopover();
}

function onPointerDown(event) {
  if (!pop || pop.hidden) return;
  if (pop.contains(event.target) || (activeButton && activeButton.contains(event.target))) return;
  closePopover({ restoreFocus: false });
}

// Tabbing out of the popover (past its last control, or back out of its first) returns to
// the term, so keyboard focus is never stranded at the end of the page.
function onPopoverKey(event) {
  if (event.key !== 'Tab') return;
  const controls = [...pop.querySelectorAll('a[href], summary, button')].filter((el) => el.getClientRects().length);
  const first = controls[0];
  const last = controls[controls.length - 1];
  const active = document.activeElement;
  if (event.shiftKey && (active === pop || active === first)) {
    event.preventDefault();
    closePopover();
  } else if (!event.shiftKey && active === last) {
    closePopover();
    // No preventDefault: with focus back on the term, Tab continues to the text after it.
  }
}
