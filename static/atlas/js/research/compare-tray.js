// compare-tray.js — the small tray that holds the experiments a reader has chosen to
// compare (at most four), and the "Add to compare" control on an experiment's panel.
//
// The tray's list lives in this module (and, so a reload does not lose it, in
// sessionStorage when the browser allows it). It is not a second source of truth about
// the comparison: once the Compare view is open, the URL (#/view/compare/a,b,c) is, and
// the view writes what it shows back here.
//
//   mountTray({ main, atlas, navigate })    once, at start: the tray on the stage
//   compareControl(experiment, navigate)    the control for an experiment panel
//   list() / has(slug) / add(slug) / remove(slug) / set(slugs) / clear() / subscribe(fn)

import { MAX_EXPERIMENTS, MIN_EXPERIMENTS, compareRoute } from '../views/compare-route.js';

const STORAGE_KEY = 'hep-atlas.compare';
const SLUG = /^[a-z0-9][a-z0-9-]*$/;

function read() {
  try {
    const parsed = JSON.parse(window.sessionStorage.getItem(STORAGE_KEY));
    return Array.isArray(parsed) ? [...new Set(parsed.filter((s) => typeof s === 'string' && SLUG.test(s)))].slice(0, MAX_EXPERIMENTS) : [];
  } catch (error) {
    return []; // storage blocked or empty: the tray simply starts empty
  }
}

function write(slugs) {
  try {
    window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(slugs));
  } catch (error) {
    /* storage blocked: the tray still works for this page view */
  }
}

let slugs = read();
const subscribers = new Set();

function changed() {
  write(slugs);
  for (const fn of [...subscribers]) fn(list());
}

export const list = () => [...slugs];
export const has = (slug) => slugs.includes(slug);
export const isFull = () => slugs.length >= MAX_EXPERIMENTS;

/** 'added', 'present' (already in the tray) or 'full' (four already). */
export function add(slug) {
  if (!SLUG.test(slug)) return 'invalid';
  if (slugs.includes(slug)) return 'present';
  if (slugs.length >= MAX_EXPERIMENTS) return 'full';
  slugs = [...slugs, slug];
  changed();
  return 'added';
}

export function remove(slug) {
  if (!slugs.includes(slug)) return;
  slugs = slugs.filter((s) => s !== slug);
  changed();
}

export function set(next) {
  const clean = [...new Set(next.filter((s) => SLUG.test(s)))].slice(0, MAX_EXPERIMENTS);
  if (clean.length === slugs.length && clean.every((s, i) => s === slugs[i])) return;
  slugs = clean;
  changed();
}

export const clear = () => set([]);

export function subscribe(fn) {
  subscribers.add(fn);
  return () => subscribers.delete(fn);
}

function h(tag, attrs = {}, children = []) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === 'class') el.className = value;
    else if (value !== null && value !== undefined) el.setAttribute(key, value);
  }
  for (const child of [].concat(children)) {
    if (child == null) continue;
    el.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
  }
  return el;
}

const nameOf = (atlas, slug) => {
  const record = (atlas.experiments || {})[`experiment:${slug}`];
  return record ? record.name : slug;
};

/** The shortest honest name for a chip: the experiment's name, or its shortest alias when the name is long. */
function chipName(atlas, slug) {
  const record = (atlas.experiments || {})[`experiment:${slug}`];
  if (!record) return slug;
  if (record.name.length <= 24) return record.name;
  const aliases = (record.aliases || []).filter((a) => a.length >= 3 && a.length < record.name.length && !/[/(]/.test(a));
  aliases.sort((a, b) => a.length - b.length);
  return aliases[0] || record.name;
}

/**
 * The tray: a card in the corner of the stage, drawn while it holds anything. On a view
 * route #atlas-main hides everything but the view, so it is out of the way there (the
 * Compare view has its own editor).
 */
export function mountTray({ main, atlas, navigate }) {
  const title = h('span', { class: 'compare-tray-title', id: 'compare-tray-title' }, 'Compare');
  const chips = h('ul', { class: 'compare-tray-chips' });
  const open = h('a', { class: 'primary-btn compare-tray-open', href: '#/view/compare/' }, 'Open comparison');
  const clearBtn = h('button', { type: 'button', class: 'text-btn compare-tray-clear' }, 'Clear');
  const hint = h('p', { class: 'compare-tray-hint' });
  const live = h('p', { class: 'visually-hidden', role: 'status', 'aria-live': 'polite' });
  const tray = h('aside', { class: 'compare-tray', id: 'compare-tray', 'aria-labelledby': 'compare-tray-title', hidden: '' }, [
    h('div', { class: 'compare-tray-row' }, [title, chips]),
    h('div', { class: 'compare-tray-row compare-tray-actions' }, [open, clearBtn]),
    hint,
    live,
  ]);
  main.appendChild(tray);

  open.addEventListener('click', (event) => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    if (list().length < MIN_EXPERIMENTS) return;
    navigate({ entity: compareRoute(list()) });
  });
  clearBtn.addEventListener('click', () => {
    clear();
    live.textContent = 'Compare tray emptied.';
  });

  function render() {
    const current = list();
    tray.hidden = current.length === 0;
    chips.replaceChildren(...current.map((slug) => {
      const name = chipName(atlas, slug);
      const remover = h('button', {
        type: 'button', class: 'compare-chip-remove', 'aria-label': `Remove ${nameOf(atlas, slug)} from the comparison`,
      }, '×');
      remover.addEventListener('click', () => {
        remove(slug);
        live.textContent = `Removed ${name}. ${list().length} in the tray.`;
      });
      return h('li', { class: 'compare-chip' }, [h('span', { class: 'compare-chip-name' }, name), remover]);
    }));
    const enough = current.length >= MIN_EXPERIMENTS;
    open.setAttribute('href', `#/view/compare/${current.join(',')}`);
    open.setAttribute('aria-disabled', enough ? 'false' : 'true');
    open.classList.toggle('is-disabled', !enough);
    hint.classList.toggle('is-needed', !enough);
    hint.textContent = enough
      ? `${current.length} of ${MAX_EXPERIMENTS}`
      : 'Add one more experiment from its panel to compare.';
  }
  subscribe(render);
  render();
  return { element: tray, render };
}

/**
 * "Add to compare" for an experiment's panel: adds or removes it, says why it cannot add
 * a fifth, and links to the comparison once two are in the tray.
 */
export function compareControl(experiment, navigate) {
  const slug = experiment.id.split(':')[1];
  const button = h('button', { type: 'button', class: 'text-btn compare-add' });
  const link = h('a', { class: 'compare-open-link', href: '#/view/compare/' });
  const status = h('span', { class: 'compare-add-status', role: 'status', 'aria-live': 'polite' });
  const wrap = h('div', { class: 'compare-control' }, [button, link, status]);

  function render() {
    const inTray = has(slug);
    const full = isFull() && !inTray;
    button.textContent = inTray ? 'Remove from compare' : 'Add to compare';
    button.setAttribute('aria-disabled', full ? 'true' : 'false');
    button.classList.toggle('is-disabled', full);
    button.setAttribute('aria-pressed', inTray ? 'true' : 'false');
    const current = list();
    link.hidden = !(inTray && current.length >= MIN_EXPERIMENTS);
    link.textContent = `Open comparison (${current.length})`;
    link.setAttribute('href', `#/view/compare/${current.join(',')}`);
    if (full) status.textContent = `The comparison holds ${MAX_EXPERIMENTS}; remove one to add this.`;
  }
  button.addEventListener('click', () => {
    if (has(slug)) {
      remove(slug);
      status.textContent = `Removed ${experiment.name} from the comparison.`;
    } else if (add(slug) === 'added') {
      status.textContent = `Added ${experiment.name} to the comparison (${list().length} of ${MAX_EXPERIMENTS}).`;
    } else {
      status.textContent = `The comparison holds ${MAX_EXPERIMENTS}; remove one to add this.`;
    }
    render();
  });
  link.addEventListener('click', (event) => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    navigate({ entity: compareRoute(list()) });
  });
  // Stay current while the panel is on screen (the tray can change from its own buttons);
  // let go once the panel has been replaced.
  const stop = subscribe(() => {
    if (!wrap.isConnected) { stop(); return; }
    const message = status.textContent;
    render();
    status.textContent = message;
  });
  render();
  return wrap;
}
