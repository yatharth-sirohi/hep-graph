// classroom.js — the classroom modes, once the app is up (js/classroom-boot.js has
// already set the theme and the embed class before the first paint).
//
//   Projector mode   a light, high-contrast theme with larger type (classroom.css).
//                    The header's Projector button toggles it; the choice is remembered
//                    in localStorage (wrapped: a private window just forgets it) and
//                    written to the address as ?theme=, so a shared link carries it.
//                    A link's own ?theme= wins over the remembered choice and is never
//                    stored. On a phone the button lives in the "Views & filters" sheet
//                    (phone.js moves it; the handler here is on the element itself).
//   Embed mode       ?embed=1: classroom.css hides the search, the view switcher, the
//                    filters, the footer and the timeline; this file keeps the
//                    "Open in HEP Atlas" link pointed at the same view at full size, and
//                    shows the timeline for a route that needs it (a local map).

import * as state from './state.js';

export const THEME_KEY = 'hep-atlas.theme';
const root = document.documentElement;

export function currentTheme() {
  return root.getAttribute('data-theme') === 'projector' ? 'projector' : 'standard';
}

function remember(theme) {
  try {
    window.localStorage.setItem(THEME_KEY, theme);
  } catch (error) {
    // Storage is unavailable; the choice lasts for this page only.
  }
}

/** Apply a theme now. Fires `atlas:themechange` so canvas code (the globe's beam
 * arcs) can restyle itself from the new tokens. */
export function applyTheme(theme) {
  const projector = theme === 'projector';
  if (projector) root.setAttribute('data-theme', 'projector'); else root.removeAttribute('data-theme');
  const button = document.getElementById('theme-btn');
  if (button) {
    button.setAttribute('aria-pressed', String(projector));
    button.classList.toggle('is-active', projector);
    const stateText = button.querySelector('.theme-btn-state');
    if (stateText) stateText.textContent = projector ? 'On' : 'Off';
  }
  document.dispatchEvent(new CustomEvent('atlas:themechange', { detail: { theme: projector ? 'projector' : 'standard' } }));
}

/** The address of this view at full size: the same route and filters, no `embed`. */
export function fullSizeHref(href = window.location.href) {
  const url = new URL(href);
  url.searchParams.delete('embed');
  return url.toString();
}

export function init() {
  const button = document.getElementById('theme-btn');
  applyTheme(currentTheme());
  if (button) {
    button.addEventListener('click', () => {
      const next = currentTheme() === 'projector' ? 'standard' : 'projector';
      applyTheme(next);
      remember(next);
      // Quietly: the theme changes nothing the panels or the globe draw, so it must
      // not re-render an open record.
      state.patchQuietly({ theme: next });
    });
  }

  if (root.classList.contains('is-embed')) {
    const link = document.getElementById('embed-open');
    // The coverage line that stays in the footer opens beside the frame, not inside it.
    const coverage = document.querySelector('.atlas-footer .footer-coverage');
    if (coverage) {
      coverage.setAttribute('target', '_blank');
      coverage.setAttribute('rel', 'noopener');
    }
    const arrivedWithTimeline = root.classList.contains('embed-timeline');
    const sync = (current) => {
      if (link) link.setAttribute('href', fullSizeHref());
      const map = !!(current && current.entity && current.entity.type === 'map');
      root.classList.toggle('embed-timeline', arrivedWithTimeline || map);
    };
    state.subscribe(sync);
    sync(state.get());
  }
}
