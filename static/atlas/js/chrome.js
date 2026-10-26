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
    keyPopover.hidden = !open;
    keyBtn.setAttribute('aria-expanded', String(open));
    if (open) {
      keyPopover.focus({ preventScroll: true });
    } else if (restoreFocus && keyPopover.contains(document.activeElement)) {
      keyBtn.focus({ preventScroll: true });
    }
  }

  function setDrawerOpen(open, { restoreFocus = true } = {}) {
    if (PHONE.matches) return; // phone.js owns this element as a sheet
    const isOpen = panel.classList.contains('is-open');
    if (open === isOpen) return;
    panel.classList.toggle('is-open', open);
    filtersBtn.setAttribute('aria-expanded', String(open));
    if (open) {
      panel.setAttribute('tabindex', '-1');
      panel.focus({ preventScroll: true });
    } else if (restoreFocus && panel.contains(document.activeElement)) {
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
