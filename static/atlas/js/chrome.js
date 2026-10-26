// chrome.js — the header's two quiet controls at laptop width: the Key popover
// and the Filters drawer. (The view switcher is plain buttons that app.js already
// wires; on a phone phone.js owns all of this through its own sheets, and these
// controls are display:none there.)
//
//   Key      a button that opens a popover with the marker shapes, the dots and
//            the status colours. A popover is transient: it closes on Escape, on
//            a click anywhere else, and when the Key button is pressed again.
//   Filters  a button, with a count badge, that opens the 240 px drawer over the
//            left of the stage. The drawer is modeless — the globe behind it stays
//            live so the person watches the markers respond — so it closes only
//            from its own × / the button / Escape while focus is inside it.
//
// Escape is handled in the capture phase so a popover or drawer that is open takes
// it before the record panel (app.js) does: one Escape closes one thing, the
// innermost.

const PHONE = window.matchMedia('(max-width: 900px)');

const $ = (id) => document.getElementById(id);

export function createChrome() {
  const keyBtn = $('key-btn');
  const keyPopover = $('key-popover');
  const keyStatus = $('key-status');
  const filtersBtn = $('filters-btn');
  const filtersBadge = $('filters-badge');
  const panel = $('filters-panel');
  const closeBtn = $('filters-close');
  const search = $('atlas-search');
  if (!keyBtn || !keyPopover || !filtersBtn || !panel) return { setFilterCount() {}, adoptStatusLegend() {}, closeAll() {} };

  function setKeyOpen(open, { restoreFocus = true } = {}) {
    if (open === !keyPopover.hidden) return;
    // Asked before the popover is hidden: a hidden element gives its focus up.
    const hadFocus = keyPopover.contains(document.activeElement);
    keyPopover.hidden = !open;
    keyBtn.setAttribute('aria-expanded', String(open));
    if (open) {
      keyPopover.focus({ preventScroll: true });
    } else if (restoreFocus && hadFocus) {
      keyBtn.focus({ preventScroll: true });
    }
  }

  function setDrawerOpen(open, { restoreFocus = true } = {}) {
    if (PHONE.matches) return; // phone.js owns this element as a sheet
    const isOpen = panel.classList.contains('is-open');
    if (open === isOpen) return;
    const hadFocus = panel.contains(document.activeElement);
    panel.classList.toggle('is-open', open);
    filtersBtn.setAttribute('aria-expanded', String(open));
    if (open) {
      panel.setAttribute('tabindex', '-1');
      panel.focus({ preventScroll: true });
    } else if (restoreFocus && hadFocus) {
      filtersBtn.focus({ preventScroll: true });
    }
  }

  keyBtn.addEventListener('click', () => setKeyOpen(keyPopover.hidden));
  filtersBtn.addEventListener('click', () => setDrawerOpen(!panel.classList.contains('is-open')));
  if (closeBtn) closeBtn.addEventListener('click', () => setDrawerOpen(false));

  document.addEventListener('pointerdown', (event) => {
    if (keyPopover.hidden) return;
    if (keyPopover.contains(event.target) || keyBtn.contains(event.target)) return;
    setKeyOpen(false, { restoreFocus: false });
  });

  // The popover holds no controls, so the next Tab takes focus straight out of it — to
  // the Filters button, or on into the page — and a popover left open behind that
  // focus is one the person has stopped reading. Focus leaving it closes it, as
  // Escape does, with focus staying where it went (it is not pulled back to the
  // button). Not a close: focus moving to the Key button itself (its own click
  // toggles), a pointer press on the button or in the popover (Safari does not focus
  // a button it is clicked on, and a click on the popover's text is not leaving it),
  // and the window losing focus while the popover has it (switching to another app).
  let pointerOnKey = false;
  document.addEventListener('pointerdown', (event) => {
    pointerOnKey = keyPopover.contains(event.target) || keyBtn.contains(event.target);
  }, true);
  for (const type of ['pointerup', 'pointercancel']) {
    document.addEventListener(type, () => { window.setTimeout(() => { pointerOnKey = false; }, 0); }, true);
  }
  keyPopover.addEventListener('focusout', (event) => {
    if (keyPopover.hidden || pointerOnKey) return;
    const next = event.relatedTarget;
    if (next && (keyPopover.contains(next) || next === keyBtn)) return;
    // relatedTarget is null when focus goes to nothing focusable and when the window
    // is deactivated; only the second leaves the page's own focus where it was.
    window.setTimeout(() => {
      if (keyPopover.hidden || pointerOnKey || keyPopover.contains(document.activeElement)) return;
      if (!next && !document.hasFocus()) return;
      setKeyOpen(false, { restoreFocus: false });
    }, 0);
  });

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape' || PHONE.matches) return;
    // Escape inside the search box belongs to the search box (search.js).
    if (search && event.target === search) return;
    if (!keyPopover.hidden) {
      event.stopPropagation();
      setKeyOpen(false);
      return;
    }
    const inDrawer = panel.contains(document.activeElement) || document.activeElement === filtersBtn;
    if (panel.classList.contains('is-open') && inDrawer) {
      event.stopPropagation();
      setDrawerOpen(false);
    }
  }, true);

  // Resizing across the phone breakpoint hands the same elements to phone.js.
  PHONE.addEventListener('change', () => {
    setKeyOpen(false, { restoreFocus: false });
    filtersBtn.setAttribute('aria-expanded', 'false');
  });

  return {
    /** Active filter count on the Filters button (0 hides the badge). */
    setFilterCount(count) {
      filtersBadge.hidden = count === 0;
      filtersBadge.textContent = String(count);
      filtersBtn.setAttribute('aria-label', count ? `Filters, ${count} active` : 'Filters');
    },
    /** The status legend is built by the timeline; it is part of the Key. */
    adoptStatusLegend(node) {
      if (node && keyStatus && node.parentNode !== keyStatus) keyStatus.appendChild(node);
    },
    closeAll() {
      setKeyOpen(false, { restoreFocus: false });
      setDrawerOpen(false, { restoreFocus: false });
    },
  };
}
