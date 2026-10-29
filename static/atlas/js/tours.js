// tours.js — the guided-tour player (docs/HEP_ATLAS_TEACHING_PLAN.md, workstream 3; the
// format is amendment A28 and `tours.json`).
//
// ROUTE   #/tour/<slug>?step=<n>[&present=1]   (state.js; `#/view/tour/<slug>` is rewritten to
//         it by app.js). The address holds only the tour and the step: the step supplies its
//         own year, selection, local map or view (tour-data.js reads them from the build's
//         `href`), so a pasted link, Back and Forward all land on the same picture.
//
// THE CARD  a compact, non-modal card over the left of the stage (a bottom sheet on a phone):
//         the tour's title, "Step N of M" with a progress bar, the step's title and text with
//         the phrases its claims cover marked, a Sources disclosure (each claim's quote, where
//         it is in the source, and the Atlas field it leans on), an optional question with
//         "Show answer" and its worked answer, and Back / Next.
//
// HOW A STEP IS APPLIED  app.js asks `resolve(raw)` for the state to draw: the same state with
//         the route swapped for the step's (a selection beside the globe, a local map, or a
//         full-stage view), so every existing route is drawn by the code that already draws
//         it. `frame()` then flies the globe with `showView(camera, { clearOf: card })`, and
//         `settle()` finishes (focus, announcements, the record button).
//
// PRESENTER MODE  `?present=1` or the card's "Present" button: large type; the arrow keys,
//         Page Up/Down and Space step (what a clicker sends); B blanks the screen (W whitens
//         it), A or Enter shows the answer, Escape leaves presenter mode, then the tour.
//         Nothing here sets a colour: the stage and card use the same tokens as everything
//         else, so a theme (?theme=projector) restyles them.

import * as loader from './loader.js';
import * as provenance from './provenance.js';
import { hasTex, readableNodes } from './tex.js';
import {
  calculationLine, clampStep, coveredSegments, fieldLabel, stepTarget, tourIdOf, tourMeta, tourSlug,
} from './tour-data.js';

const PHONE = window.matchMedia('(max-width: 900px)');
const BASE_TITLE = document.title;

function h(tag, attrs = {}, children = []) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (key === 'class') el.className = value;
    else if (key === 'text') el.textContent = value;
    else if (value !== null && value !== undefined && value !== false) el.setAttribute(key, value === true ? '' : value);
  }
  for (const child of [].concat(children)) {
    if (child == null || child === false) continue;
    el.appendChild((typeof child === 'string' || typeof child === 'number') ? document.createTextNode(String(child)) : child);
  }
  return el;
}

/** The step's sentence as DOM: the phrases its claims cover are marked (a dotted underline,
 * and `data-claims` naming them), and TeX in it is typeset by tex.js. */
function sentence(text, claims, mark = true) {
  const frag = document.createDocumentFragment();
  if (hasTex(text) || !mark) {
    frag.append(...readableNodes(text));
    return frag;
  }
  for (const segment of coveredSegments(text, claims)) {
    if (!segment.claims.length) frag.append(document.createTextNode(segment.text));
    else frag.append(h('span', { class: 'tour-covered', 'data-claims': segment.claims.map((i) => i + 1).join(' ') }, segment.text));
  }
  return frag;
}

function isTyping(target) {
  return !!target && typeof target.closest === 'function'
    && !!target.closest('input, textarea, select, [contenteditable=""], [contenteditable="true"]');
}

/**
 * `createPlayer({ card, main, getGlobe, navigate, refresh, index, searchInput })`
 *   card      #tour-card, the empty section index.html holds for it
 *   main      #atlas-main
 *   getGlobe  () => the globe API or null
 *   getState  state.get (a call that is no longer the current address stops)
 *   navigate  state.navigate
 *   refresh   () => re-run app.js's applyState for the current address (a panel opened or closed)
 *   index     atlas.json's id -> record map (names in Sources and on buttons)
 */
export function createPlayer({
  card, main, getGlobe, getState, navigate, refresh, index, searchInput,
}) {
  if (!card) {
    return {
      resolve: async (raw) => ({ ...raw, entity: null }), leave() {}, frame() {}, settle() {}, active: () => false,
      ownsCamera: () => false, panelRoute: (current) => current.entity, interceptPanelNavigate: () => false,
      mapFraming: () => null, takePanelFocus: () => false,
    };
  }

  let dom = null;
  let tour = null;
  let step = null;
  let stepNo = 0;
  let target = null;
  let activeKey = null;
  let framePending = false;
  let mapFramePending = false;
  let settlePending = false;
  let dismissedKey = null; // the step whose record panel the reader closed
  let phoneKey = null; // phone: the step whose record the reader asked for
  let present = false;
  let blank = null;
  let paused = null; // a tour left by following something else: { slug, step, name, count }
  let exiting = false;
  let opener = null;
  let serial = 0;
  let lastFocus = null;
  let answerOpen = false;
  let collapsed = false; // phone: the sheet is folded down to its controls
  let focusRecord = false; // the reader asked for the record: focus goes to it
  let focusCard = false; // the record was closed: focus comes back to the card

  const nameOf = (id) => {
    const record = index && index.get ? index.get(id) : null;
    return (record && record.name) || null;
  };

  // ---------------------------------------------------------------- the card
  function ensureDom() {
    if (dom) return dom;
    const kicker = h('p', { class: 'tour-kicker' }, 'Guided tour');
    const presentBtn = h('button', { type: 'button', class: 'tour-chip tour-present', 'aria-pressed': 'false' }, 'Present');
    const closeBtn = h('button', { type: 'button', class: 'tour-close', 'aria-label': 'Exit the tour' }, h('span', { 'aria-hidden': 'true' }, '×'));
    const head = h('div', { class: 'tour-head' }, [kicker, presentBtn, closeBtn]);
    const title = h('h2', { class: 'tour-title', id: 'tour-title' });
    const count = h('span', { class: 'tour-count', id: 'tour-count' });
    const year = h('span', { class: 'tour-year' });
    const barFill = h('i');
    const bar = h('div', { class: 'tour-bar', role: 'progressbar', 'aria-labelledby': 'tour-count', 'aria-valuemin': '1' }, barFill);
    const progress = h('div', { class: 'tour-progress' }, [h('p', { class: 'tour-meta' }, [count, year]), bar]);
    const body = h('div', { class: 'tour-body', id: 'tour-body' });
    const back = h('button', { type: 'button', class: 'text-btn tour-back' }, 'Back');
    // Phone only (tours.css): fold the sheet down to its controls so a view or a map above it
    // can be seen whole, and bring the text back.
    const collapse = h('button', {
      type: 'button', class: 'text-btn tour-collapse', 'aria-expanded': 'true', 'aria-controls': 'tour-body',
    }, 'Hide text');
    const next = h('button', { type: 'button', class: 'primary-btn tour-next' }, 'Next');
    const nav = h('div', { class: 'tour-nav' }, [back, collapse, next]);
    const hint = h('p', { class: 'tour-hint' },
      'Arrow keys, Page Up/Down or Space to step · B blanks the screen · A shows the answer · Esc leaves presenter mode');
    const status = h('p', { class: 'visually-hidden', role: 'status', 'aria-live': 'polite' });
    card.replaceChildren(head, title, progress, body, nav, hint, status);
    card.setAttribute('role', 'region');
    card.setAttribute('aria-label', 'Guided tour');
    card.setAttribute('tabindex', '-1');

    presentBtn.addEventListener('click', () => setPresent(!present));
    closeBtn.addEventListener('click', () => exit());
    back.addEventListener('click', () => go(stepNo - 1));
    collapse.addEventListener('click', () => setCollapsed(!collapsed));
    next.addEventListener('click', () => (stepNo >= tour.steps.length ? exit() : go(stepNo + 1)));
    card.addEventListener('focusin', (event) => { lastFocus = event.target; });

    const blankEl = h('div', { class: 'tour-blank', id: 'tour-blank', hidden: true, 'aria-hidden': 'true' });
    blankEl.addEventListener('click', () => setBlank(null));
    document.body.appendChild(blankEl);

    const resume = h('div', { class: 'tour-resume', id: 'tour-resume', hidden: true });
    const resumeBtn = h('button', { type: 'button', class: 'tour-resume-btn' });
    const resumeClose = h('button', { type: 'button', class: 'tour-resume-close', 'aria-label': 'Dismiss' }, h('span', { 'aria-hidden': 'true' }, '×'));
    resume.append(resumeBtn, resumeClose);
    main.appendChild(resume);
    resumeBtn.addEventListener('click', () => {
      if (!paused) return;
      const { slug, step: at } = paused;
      navigate({ entity: { type: 'tour', slug }, step: at, mode: null });
    });
    resumeClose.addEventListener('click', () => { paused = null; updatePill(); });

    dom = {
      kicker, presentBtn, closeBtn, title, count, year, bar, barFill, body, back, collapse, next, hint, status, blankEl, resume, resumeBtn,
    };
    return dom;
  }

  function showCard() {
    ensureDom();
    if (card.hidden) {
      const active = document.activeElement;
      opener = active && active !== document.body && !card.contains(active) ? active : null;
    }
    card.hidden = false;
    main.classList.add('has-tour');
    document.body.classList.add('is-touring');
  }

  function hideCard() {
    if (!dom) return;
    card.hidden = true;
    card.classList.remove('is-yielding');
    main.classList.remove('has-tour');
    document.body.classList.remove('is-touring', 'is-presenting', 'tour-record-open');
    card.classList.remove('is-collapsed');
    main.style.removeProperty('--tour-w');
    document.title = BASE_TITLE;
    setBlank(null);
  }

  function announce(text) {
    dom.status.textContent = '';
    window.setTimeout(() => { dom.status.textContent = text; }, 30);
  }

  function messageCard(heading, message, { retry = null, list = null } = {}) {
    ensureDom();
    dom.title.textContent = heading;
    dom.count.textContent = '';
    dom.year.textContent = '';
    dom.barFill.style.width = '0%';
    dom.bar.hidden = true;
    dom.back.hidden = true;
    dom.next.hidden = true;
    card.classList.add('is-message');
    const parts = [h('p', { class: 'tour-text' }, message)];
    if (retry) {
      const button = h('button', { type: 'button', class: 'text-btn' }, 'Retry');
      button.addEventListener('click', retry);
      parts.push(button);
    }
    if (list && list.length) {
      parts.push(h('p', { class: 'tour-q-kicker' }, 'The tours in this Atlas'));
      parts.push(h('ul', { class: 'entity-list' }, list.map((t) => {
        const a = h('a', { href: `#/tour/${tourSlug(t.id)}`, class: 'entity-link' }, t.name);
        a.addEventListener('click', (event) => {
          event.preventDefault();
          navigate({ entity: { type: 'tour', slug: tourSlug(t.id) }, step: 1 });
        });
        return h('li', {}, a);
      })));
    }
    dom.body.replaceChildren(...parts);
  }

  function renderLoading() {
    messageCard('Guided tour', 'Loading the tour…');
    dom.body.firstChild.setAttribute('role', 'status');
  }

  // ------------------------------------------------------------ the step's content
  function evidenceLabel(claim, where) {
    return [`“${claim.covers}”`, where ? h('span', { class: 'claim-where' }, ` · ${where}`) : null];
  }

  function evidenceNote(claim) {
    if (!claim.ref) return null;
    const entity = nameOf(claim.ref) || claim.ref;
    const field = fieldLabel(claim.field, nameOf);
    const value = claim.value != null && claim.value !== '' ? ` = ${claim.value}` : '';
    return `From the Atlas: ${entity} › ${field}${value}`;
  }

  /** A "Sources" disclosure over `items` ({ claim, where }); the sources bundle is
   * fetched when it first opens, never before. */
  function sourcesDisclosure(items, label = 'Sources') {
    const details = h('details', { class: 'panel-section tour-sources', 'data-state': 'idle' });
    details.appendChild(h('summary', {}, `${label} (${items.length})`));
    const body = h('div', { class: 'panel-section-body' }, [h('p', { class: 'empty-note' }, 'Opens to load the sources.')]);
    details.appendChild(body);
    let loaded = false;
    let busy = false;
    async function load() {
      if (loaded || busy) return;
      busy = true;
      details.dataset.state = 'loading';
      body.replaceChildren(h('p', { class: 'loading-note', role: 'status' }, 'Loading sources…'));
      try {
        const bundle = await loader.getSources();
        const nodes = items.map(({ claim, where }) => provenance.renderEvidenceItem({
          label: evidenceLabel(claim, where),
          note: evidenceNote(claim),
          quote: claim.quote,
          locator: claim.locator,
          confidence: claim.confidence,
          sourceIds: claim.sources,
          id: null,
        }, bundle));
        body.replaceChildren(h('ul', { class: 'source-list' }, nodes));
        loaded = true;
        details.dataset.state = 'loaded';
      } catch (error) {
        details.dataset.state = 'error';
        const retry = h('button', { type: 'button', class: 'text-btn' }, 'Retry');
        retry.addEventListener('click', load);
        body.replaceChildren(h('p', { class: 'error-note', role: 'alert' }, `Could not load sources: ${error.message}`), retry);
      } finally {
        busy = false;
      }
    }
    details.addEventListener('toggle', () => { if (details.open) load(); });
    return details;
  }

  function workingList(question) {
    const lines = (question.calculation || []).map(calculationLine);
    if (!lines.length) return null;
    return h('ol', { class: 'tour-working' }, lines.map((line) => {
      if (line.kind === 'computed') {
        return h('li', {}, [line.name, ' = ', h('span', { class: 'tour-calc-how' }, `${line.expression} = `), h('strong', {}, line.valueText)]);
      }
      const how = line.kind === 'atlas'
        ? ` the Atlas: ${nameOf(line.ref) || line.ref} › ${fieldLabel(line.field, nameOf)}`
        : ' a sourced constant (see Sources)';
      return h('li', {}, [line.name, ' = ', h('strong', {}, line.valueText), h('span', { class: 'tour-calc-how' }, ` — ${how.trim()}`)]);
    }));
  }

  function questionCard() {
    const q = step.question;
    if (!q) return null;
    const claims = q.claims || [];
    const promptClaims = claims.filter((c) => c.in === 'prompt');
    const answerClaims = claims.filter((c) => c.in !== 'prompt');
    const answer = h('div', { class: 'tour-answer', id: 'tour-answer', hidden: !answerOpen }, [
      h('p', { class: 'tour-q-answer' }, sentence(q.answer, answerClaims)),
      workingList(q) ? h('details', { class: 'panel-section' }, [h('summary', {}, 'How it was worked out'), h('div', { class: 'panel-section-body' }, workingList(q))]) : null,
      // The answer's own claims and the ones its working leans on (the figures in the question).
      claims.length ? sourcesDisclosure(claims.map((claim) => ({ claim, where: claim.in === 'prompt' ? 'in the question' : 'in the answer' })), 'Sources for the question and answer') : null,
    ]);
    const toggle = h('button', {
      type: 'button', class: 'text-btn tour-answer-btn', 'aria-expanded': String(answerOpen), 'aria-controls': 'tour-answer',
    }, answerOpen ? 'Hide answer' : 'Show answer');
    toggle.addEventListener('click', () => setAnswer(!answerOpen));
    return {
      node: h('section', { class: 'tour-question', 'aria-label': 'Question' }, [
        h('p', { class: 'tour-q-kicker' }, 'Question'),
        h('p', { class: 'tour-q-prompt' }, sentence(q.prompt, promptClaims)),
        toggle,
        answer,
      ]),
      promptClaims,
    };
  }

  function setCollapsed(on) {
    collapsed = !!on;
    card.classList.toggle('is-collapsed', collapsed);
    dom.collapse.setAttribute('aria-expanded', String(!collapsed));
    dom.collapse.textContent = collapsed ? 'Show text' : 'Hide text';
  }

  // Scrolls the card's own body, never the page (scrollIntoView also scrolls every ancestor,
  // which on a phone slides the whole screen up).
  function scrollBodyTo(el) {
    const box = dom.body;
    const top = el.getBoundingClientRect().top - box.getBoundingClientRect().top + box.scrollTop;
    box.scrollTop = Math.max(0, top - 8);
  }

  function setAnswer(open) {
    answerOpen = open;
    const toggle = card.querySelector('.tour-answer-btn');
    const answer = card.querySelector('.tour-answer');
    if (!toggle || !answer) return;
    answer.hidden = !open;
    toggle.setAttribute('aria-expanded', String(open));
    toggle.textContent = open ? 'Hide answer' : 'Show answer';
    // A laptop shows the question and its answer together, from the top of the question card;
    // a phone's short sheet shows the answer itself.
    if (open) {
      const target_ = PHONE.matches ? answer : card.querySelector('.tour-question');
      if (target_) scrollBodyTo(target_);
    }
  }

  // The record a step points at: the one beside the globe, or a local map's drawer (`sel`).
  function recordId() {
    if (!target) return null;
    if (target.stage === 'globe') return target.entity ? `${target.entity.type}:${target.entity.slug}` : null;
    if (target.stage === 'map') return target.sel || null;
    return null;
  }

  function recordButton() {
    const id = recordId();
    if (!id) return null;
    const name = nameOf(id);
    const button = h('button', { type: 'button', class: 'text-btn tour-record-btn' }, name ? `Open the record for ${name}` : 'Open the record');
    button.addEventListener('click', openPanel);
    return button;
  }

  function renderStep() {
    ensureDom();
    const count = tour.steps.length;
    card.classList.remove('is-message');
    dom.bar.hidden = false;
    dom.back.hidden = false;
    dom.next.hidden = false;
    dom.title.textContent = tour.name;
    dom.count.textContent = `Step ${stepNo} of ${count}`;
    dom.year.textContent = target.year != null ? String(target.year) : '';
    dom.bar.setAttribute('aria-valuemax', String(count));
    dom.bar.setAttribute('aria-valuenow', String(stepNo));
    dom.bar.setAttribute('aria-valuetext', `Step ${stepNo} of ${count}`);
    dom.barFill.style.width = `${Math.round((stepNo / count) * 100)}%`;
    dom.back.disabled = stepNo <= 1;
    dom.next.textContent = stepNo >= count ? 'Finish' : 'Next';
    dom.next.setAttribute('aria-label', stepNo >= count ? 'Finish the tour and return to the globe' : `Next: step ${stepNo + 1}`);
    dom.back.setAttribute('aria-label', stepNo > 1 ? `Back: step ${stepNo - 1}` : 'Back');
    card.setAttribute('aria-label', `Guided tour: ${tour.name}`);
    document.title = `${tour.name} · step ${stepNo} of ${count} · HEP Atlas`;

    const question = questionCard();
    const items = [
      ...(step.claims || []).map((claim) => ({ claim, where: null })),
      ...(question ? question.promptClaims.map((claim) => ({ claim, where: 'in the question' })) : []),
    ];
    dom.body.replaceChildren(...[
      h('h3', { class: 'tour-step-title' }, hasTex(step.title) ? readableNodes(step.title) : step.title),
      h('p', { class: 'tour-text' }, sentence(step.text, step.claims || [])),
      recordButton(),
      items.length ? sourcesDisclosure(items) : null,
      question ? question.node : null,
    ].filter(Boolean));
    dom.body.scrollTop = 0;
    updateRecordButton();
  }

  // --------------------------------------------------------------- moving about
  function go(n) {
    if (!tour) return;
    const next = clampStep(n, tour.steps.length);
    if (next === stepNo) return;
    navigate({ step: next });
  }

  function exit() {
    exiting = true;
    paused = null;
    const back = opener;
    navigate({ entity: null, step: null, present: false, mode: null });
    if (back && back.isConnected) back.focus({ preventScroll: true });
  }

  function setPresent(on) {
    navigate({ present: !!on }, { replace: true });
  }

  function applyPresent() {
    present = !!present;
    document.body.classList.toggle('is-presenting', present);
    if (dom) {
      dom.presentBtn.setAttribute('aria-pressed', String(present));
      dom.presentBtn.textContent = present ? 'Presenting' : 'Present';
      dom.presentBtn.setAttribute('aria-label', present ? 'Presenter mode is on; turn it off' : 'Turn on presenter mode');
    }
    if (!present) setBlank(null);
    // Presenter mode changes what waits to be asked for on a map step (the record's drawer).
    if (target && activeKey) updateRecordButton();
  }

  function setBlank(kind) {
    blank = kind;
    if (!dom) return;
    dom.blankEl.hidden = !kind;
    dom.blankEl.classList.toggle('is-white', kind === 'white');
  }

  function panelHidden() {
    return dismissedKey === activeKey || (PHONE.matches && phoneKey !== activeKey);
  }

  function closePanel() {
    dismissedKey = activeKey;
    phoneKey = null;
    focusCard = true;
    refresh();
  }

  function openPanel() {
    dismissedKey = null;
    phoneKey = activeKey;
    focusRecord = true;
    refresh();
  }

  function updateRecordButton() {
    if (!dom) return;
    const button = card.querySelector('.tour-record-btn');
    const hasRecord = !!recordId();
    // A local map's drawer is a column of its own on a laptop and shows by itself, but a phone's is a sheet,
    // and presenter mode keeps the stage for the map (tours.css): in both, the drawer waits to be asked for.
    const waits = PHONE.matches || (present && target.stage === 'map');
    const asked = !!hasRecord && phoneKey === activeKey;
    // Beside the globe the record opens by itself (and can be closed, then asked for again).
    const hidden = !hasRecord || !(target.stage === 'globe' ? panelHidden() : waits && phoneKey !== activeKey);
    if (button) button.hidden = hidden;
    // A phone shows one sheet at a time: while the record is open the card steps aside.
    card.classList.toggle('is-yielding', asked && PHONE.matches);
    document.body.classList.toggle('tour-record-open', asked && waits);
  }

  // ----------------------------------------------------------------- the keyboard
  function onKey(event) {
    if (!tour || card.hidden || !activeKey) return;
    const typing = isTyping(event.target);
    const stop = () => { event.preventDefault(); event.stopImmediatePropagation(); };
    if (blank) {
      if (['Shift', 'Control', 'Alt', 'Meta', 'CapsLock'].includes(event.key)) return;
      stop();
      setBlank(null);
      return;
    }
    if (event.key === 'Escape') {
      if (typing && event.target === searchInput) return;
      stop();
      if (present) setPresent(false);
      else if (!card.classList.contains('is-message') && !panelHidden() && target && target.entity && target.stage === 'globe' && !PHONE.matches) closePanel();
      else exit();
      return;
    }
    if (!present || typing || event.ctrlKey || event.metaKey || event.altKey) return;
    const key = event.key;
    // A clicker's keys act on the tour, not on whichever button the pointer last pressed.
    const act = (fn) => {
      stop();
      if (document.activeElement && card.contains(document.activeElement) && document.activeElement !== card) document.activeElement.blur();
      fn();
    };
    if (key === 'ArrowRight' || key === 'PageDown' || (key === ' ' && !event.shiftKey)) act(() => go(stepNo + 1));
    else if (key === 'ArrowLeft' || key === 'PageUp' || (key === ' ' && event.shiftKey)) act(() => go(stepNo - 1));
    else if (key === 'Home') act(() => go(1));
    else if (key === 'End') act(() => go(tour.steps.length));
    else if (key === 'b' || key === 'B' || key === '.') act(() => setBlank('black'));
    else if (key === 'w' || key === 'W' || key === ',') act(() => setBlank('white'));
    else if ((key === 'a' || key === 'A' || key === 'Enter' || key === 'ArrowDown') && step && step.question) act(() => setAnswer(true));
    else if (key === 'ArrowUp' && step && step.question) act(() => setAnswer(false));
  }
  document.addEventListener('keydown', onKey);

  PHONE.addEventListener('change', () => { if (activeKey) refresh(); });

  // -------------------------------------------------------------------- the pill
  function updatePill() {
    if (!dom) return;
    const show = !!paused && !activeKey;
    dom.resume.hidden = !show;
    if (show) dom.resumeBtn.textContent = `Resume tour: ${paused.name} · step ${paused.step} of ${paused.count}`;
  }

  // ------------------------------------------------------------- the app's hooks
  /** The state to draw for a tour route: the step's route in place of `tour/<slug>`. Null
   * when the call has been superseded or has rewritten the address (the rewrite re-enters). */
  async function resolve(raw) {
    ensureDom();
    const slug = raw.entity.slug;
    const ticket = ++serial;
    const stageOnly = () => ({ ...raw, entity: null, mode: null, collab: null });
    if (!tour || tour.id !== tourIdOf(slug)) {
      activeKey = null;
      showCard();
      renderLoading();
    } else {
      showCard();
    }
    let data;
    try {
      data = await loader.getTours();
    } catch (error) {
      if (ticket !== serial) return null;
      messageCard('This tour could not be loaded', `${error.message}. Check your connection and retry.`, {
        retry: () => { refresh(); },
      });
      return stageOnly();
    }
    if (ticket !== serial || getState() !== raw) return null;
    const found = data ? data.byId.get(tourIdOf(slug)) : null;
    if (!data) {
      tour = null;
      messageCard('No tours here', 'This data build has no guided tours.');
      return stageOnly();
    }
    if (!found) {
      tour = null;
      activeKey = null;
      messageCard('No such tour', `The Atlas has no tour called “${slug}”.`, { list: data.list });
      return stageOnly();
    }
    const count = found.steps.length;
    const n = clampStep(raw.step, count);
    if (raw.step !== n) {
      navigate({ step: n }, { replace: true });
      return null;
    }
    tour = found;
    stepNo = n;
    step = found.steps[n - 1];
    target = stepTarget(step);
    present = !!raw.present;
    applyPresent();
    const key = `${found.id}#${n}`;
    if (key !== activeKey) {
      // A new step: lay out its card, then write its year and selection into the state
      // once (a replace, so Back still goes from step to step) and draw from that.
      activeKey = key;
      framePending = true;
      mapFramePending = true;
      settlePending = true;
      dismissedKey = null;
      phoneKey = null;
      answerOpen = false;
      paused = null;
      updatePill();
      renderStep();
      setCollapsed(false); // a new step's text is shown, whatever the last one did
      const patch = { mode: null, collab: null, sel: target.sel };
      if (target.year != null) { patch.year = target.year; patch.range = null; }
      navigate(patch, { replace: true });
      return null;
    }
    // A phone's map drawer was closed (its selection cleared): the card comes back.
    if (target.stage === 'map' && phoneKey === activeKey && !raw.sel) phoneKey = null;
    updateRecordButton();
    return {
      ...raw, entity: target.entity, mode: null, collab: null, tourKey: key,
    };
  }

  /** A route that is not a tour's: the card goes. A tour left by following something else is
   * remembered for the "Resume" pill; one left by its own Exit is not. */
  function leave() {
    if (!activeKey && card.hidden) return;
    if (activeKey && tour && !exiting) {
      paused = { slug: tourSlug(tour.id), step: stepNo, name: tour.name, count: tour.steps.length };
    }
    exiting = false;
    serial += 1;
    activeKey = null;
    framePending = false;
    mapFramePending = false;
    settlePending = false;
    hideCard();
    updatePill();
  }

  /** Called by app.js with the globe stage showing: fly to the step's camera, clear of the card.
   * `current` is the state resolve() returned; a call that belongs to a step the reader has
   * already left (Next pressed twice quickly) does nothing. */
  function frame(current) {
    if (!framePending || !activeKey || !current || current.tourKey !== activeKey) return;
    framePending = false;
    const globe = getGlobe();
    if (globe && typeof globe.showView === 'function' && target.stage === 'globe' && step.camera) {
      globe.showView(step.camera, { clearOf: card });
    }
  }

  function settle(current) {
    if (!activeKey || !current || current.tourKey !== activeKey) return;
    if (!settlePending) {
      updateRecordButton();
      if (focusCard) {
        focusCard = false;
        const record = card.querySelector('.tour-record-btn');
        (record && !record.hidden ? record : card).focus({ preventScroll: true });
      }
      return;
    }
    settlePending = false;
    framePending = false;
    updateRecordButton();
    announce(`Step ${stepNo} of ${tour.steps.length}: ${step.title}`);
    // Whatever the step opened (a record, a map, a view) took focus; it goes back to the
    // control that was being used, so Next, Next, Next works from the keyboard. On arrival
    // (nothing in the card in use yet) the card itself takes it.
    if (!card.contains(document.activeElement)) {
      let wanted = lastFocus && card.contains(lastFocus) && !lastFocus.hidden ? lastFocus : card;
      if (wanted.disabled) wanted = dom.next;
      wanted.focus({ preventScroll: true });
    }
  }

  return {
    resolve,
    leave,
    frame,
    settle,
    active: () => !!activeKey,
    ownsCamera: () => !!activeKey && !!step && !!step.camera && !!target && target.stage === 'globe',
    /** The record panel's route for the state app.js is drawing: the step's own, unless the
     * reader closed it, or a phone has not been asked for it. */
    panelRoute: (current) => (activeKey && panelHidden() ? null : current.entity),
    /** For a local map step: `{ frameSelection, reframe }` for localmap.show(). A step frames what
     * it is about; `reframe` is true once, when the step opens, so a map the reader has moved is
     * framed again for the next step but not on every redraw. Null when no tour is on screen. */
    mapFraming(current) {
      if (!activeKey || !current || current.tourKey !== activeKey) return null;
      const reframe = mapFramePending;
      mapFramePending = false;
      return { frameSelection: true, reframe };
    },
    /** True once after the reader asked for the record ("Open the record"): it takes focus then,
     * where a record that simply follows each step leaves focus in the card. */
    takePanelFocus() {
      const asked = focusRecord;
      focusRecord = false;
      return asked;
    },
    /** The panel's × (a patch of `{ entity: null }`) closes the panel and keeps the tour. */
    interceptPanelNavigate(patch) {
      if (!activeKey || !patch || patch.entity !== null || Object.keys(patch).length !== 1) return false;
      closePanel();
      return true;
    },
    describe: tourMeta,
  };
}
