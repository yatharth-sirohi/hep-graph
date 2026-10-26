// start.js — the "Start here" card.
//
// A first visit (a bare /atlas: no hash, no query, nothing remembered) opens on a
// card over the stage that says what the Atlas is and offers four ways in that all
// work today: a question (each a real deep link), the Results view, the search box,
// and the globe itself. A footer "Start here" button reopens it. Return visitors
// and anyone arriving through a shared link — which always carries a hash or a query
// — never see it unasked.
//
// A "Take a tour" row leads the options when the data build carries guided tours (js/tours.js):
// it opens the Tours list. The row is hidden otherwise, and its text counts the tours.
//
// The card is a non-modal dialog: labelled, described, focused when it opens,
// dismissed by Escape or its close button. Dismissing it by any route remembers that
// (localStorage, wrapped in try/catch: a private window or blocked storage just means
// it shows again next time). `?welcome=0` skips it for one load, which is what the
// browser tests and an embedder want; nothing is stored for that.

import * as state from './state.js';

export const STORAGE_KEY = 'hep-atlas.start-here';

// The camera the globe frames behind the card, for a globe that can be told where to
// look (`globeApi.showView`): the North Atlantic, where the long-baseline neutrino
// programmes (Fermilab to South Dakota, CERN to Gran Sasso) and the two biggest
// colliders sit within one hemisphere.
export const FIRST_VIEW = { lat: 38, lng: -30, altitude: 2.6 };

function readDismissed() {
  try {
    return window.localStorage.getItem(STORAGE_KEY) === 'dismissed';
  } catch (error) {
    return false;
  }
}

function writeDismissed() {
  try {
    window.localStorage.setItem(STORAGE_KEY, 'dismissed');
  } catch (error) {
    // Storage is unavailable; the card will simply show again next visit.
  }
}

/** True for a bare /atlas with nothing remembered: the only time the card opens unasked. */
export function isFirstVisit(loc = window.location) {
  if (loc.hash || loc.search) return false;
  return !readDismissed();
}

/**
 * Wires the card. `getGlobe()` returns the globe API once it exists (or null).
 * Returns { openFirstVisit, open, close }.
 */
export function createStartHere({
  card, reopenButton, searchInput, getGlobe, firstVisit, tours = false, tourCount = null,
}) {
  if (!card) return { openFirstVisit() {}, open() {}, close() {} };
  const toursRow = document.getElementById('start-tours');
  if (toursRow) {
    toursRow.hidden = !tours;
    const hint = document.getElementById('start-tours-hint');
    if (hint && tourCount) {
      hint.textContent = `${tourCount} short, sourced walk${tourCount === 1 ? '' : 's'} through the Atlas, each with a question or two on the way`;
    }
  }
  let opener = null;
  let lastRoute = null;

  const isOpen = () => !card.hidden;

  function frameGlobe() {
    const globe = getGlobe && getGlobe();
    // `clearOf` frames the view in the part of the stage the card leaves free.
    if (globe && typeof globe.showView === 'function') globe.showView({ ...FIRST_VIEW }, { clearOf: card });
  }

  function open({ trigger = null, frame = false } = {}) {
    opener = trigger;
    card.hidden = false;
    if (reopenButton) reopenButton.setAttribute('aria-expanded', 'true');
    lastRoute = routeKey(state.get());
    card.focus({ preventScroll: true });
    if (frame) frameGlobe();
  }

  function close({ remember = true, restoreFocus = true } = {}) {
    if (!isOpen()) return;
    const hadFocus = card.contains(document.activeElement);
    card.hidden = true;
    if (reopenButton) reopenButton.setAttribute('aria-expanded', 'false');
    if (remember) writeDismissed();
    if (restoreFocus && hadFocus && opener && opener.isConnected) opener.focus({ preventScroll: true });
    opener = null;
  }

  card.addEventListener('click', (event) => {
    const link = event.target.closest('a[data-start-link]');
    if (link) {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      close({ restoreFocus: false });
      state.navigate(state.patchFromLink(link.getAttribute('href')));
      return;
    }
    const button = event.target.closest('[data-start-action]');
    if (!button) return;
    const action = button.dataset.startAction;
    close({ restoreFocus: false });
    if (action === 'results') state.navigate({ mode: 'results', entity: null });
    else if (action === 'search' && searchInput) searchInput.focus();
    // "globe" and "close": closing is all there is to do.
  });

  if (reopenButton) {
    reopenButton.addEventListener('click', () => {
      if (isOpen()) close({ remember: false });
      else open({ trigger: reopenButton });
    });
  }

  // Escape closes the card before it closes anything behind it; the search box keeps
  // its own Escape (it closes its suggestion list).
  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape' || !isOpen() || event.target === searchInput) return;
    event.stopPropagation();
    close();
  }, true);

  // Picking something elsewhere — a marker, a search result, a mode — is the person
  // having started; the card gets out of the way (and is remembered as done).
  state.subscribe((current) => {
    if (!isOpen()) return;
    const key = routeKey(current);
    if (key !== lastRoute) close({ restoreFocus: false });
  });

  return {
    open,
    close,
    /** The one place the card opens unasked: a first visit. */
    openFirstVisit() {
      if (!firstVisit) return;
      open({ frame: true });
    },
  };
}

function routeKey(current) {
  if (!current) return '';
  const entity = current.entity ? `${current.entity.type}/${current.entity.slug}` : '';
  return `${entity}|${current.mode || ''}`;
}
