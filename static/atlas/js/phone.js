// phone.js — the behaviour half of the phone layout (viewports <= 900 px, phones and portrait tablets).
// The look lives in phone.css; this file only does what CSS cannot:
//
//   * a header button that opens the filters/legend sheet (and, on a local
//     map, "Back to globe" and "Map layers" buttons that stay on screen),
//   * a grab bar on every bottom sheet — expand to full height, close —
//     with dialog semantics, focus moving in on open and back on close,
//   * resizing the globe/map stage to the strip the sheet leaves free, so
//     the thing you just selected is not hidden behind its own panel,
//   * moving two long footer/timeline texts into the filters sheet,
//   * hiding map-marker captions that would sit on top of each other.
//
// It never touches app state: it clicks the buttons the other modules
// already own (#map-back, #close-detail, #map-drawer-close, the Globe mode
// button) and listens to class changes. At widths above the breakpoint
// nothing here is active — activate() has not run, no node has been added,
// and deactivate() puts every moved node back — so the desktop DOM and
// layout are exactly what they were without this file.

const PHONE_QUERY = '(max-width: 900px)';
const mq = window.matchMedia(PHONE_QUERY);

const $ = (selector, root = document) => root.querySelector(selector);

const els = {
  main: document.getElementById('atlas-main'),
  header: document.querySelector('.atlas-header'),
  filters: document.getElementById('filters-panel'),
  mode: document.getElementById('mode-panel'),
  detail: document.getElementById('detail-panel'),
  timelineBar: document.getElementById('timeline-bar'),
  footer: document.querySelector('.atlas-footer'),
  versionLabel: document.getElementById('data-version-label'),
  search: document.getElementById('atlas-search'),
  filterControls: document.getElementById('filters-controls'),
};

let active = false;
// Everything activate() adds or moves registers its own undo here.
let undo = [];
let headerButtons = null;
let stageHeight = 0;
let stageTimer = null;

function pressEscape() {
  document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
}

// ----------------------------------------------------------------- sheets
// `toggled` sheets are opened by a button and carry `.is-open`; the others
// are shown and hidden by their own module through `.hidden`.
const SHEETS = {
  filters: {
    get: () => els.filters,
    toggled: true,
    opener: () => document.getElementById('phone-filters-btn'),
    closeLabel: 'Close views and filters',
    heading: 'Views & filters',
    dialogLabel: () => 'Views, filters and key',
  },
  layers: {
    get: () => $('.map-layers'),
    toggled: true,
    opener: () => document.getElementById('phone-layers-btn'),
    closeLabel: 'Close map layers',
    dialogLabel: () => 'Map layers, features and legend',
  },
  mode: {
    get: () => els.mode,
    closeLabel: 'Close panel',
    close: () => { const globe = $('#mode-buttons [data-mode=""]'); if (globe) globe.click(); else pressEscape(); },
    dialogLabel: (el) => headingText(el) || 'Browse',
  },
  detail: {
    get: () => els.detail,
    closeLabel: 'Close panel',
    close: () => { const real = document.getElementById('close-detail'); if (real) real.click(); else pressEscape(); },
    dialogLabel: (el) => headingText(el) || 'Details',
  },
  drawer: {
    get: () => $('.map-drawer'),
    closeLabel: 'Close panel',
    close: () => {
      const real = document.getElementById('map-drawer-close');
      if (real) real.click(); else pressEscape();
    },
    dialogLabel: () => 'Selected feature',
  },
  // The Start-here card (start.js) is already a bottom sheet here, with its own
  // close; it is listed only so the globe shrinks to the strip above it.
  start: {
    get: () => document.getElementById('start-card'),
    dialogLabel: () => 'Start here',
  },
  // The guided-tour card (tours.js) is a bottom sheet too: listed so the stage above it
  // shrinks to the strip it leaves (the card steps aside while the record sheet is open).
  tour: {
    get: () => document.getElementById('tour-card'),
    dialogLabel: () => 'Guided tour',
  },
};

function headingText(el) {
  const heading = el && el.querySelector('h2');
  return heading ? heading.textContent.trim() : '';
}

function isOpen(sheet) {
  const el = sheet.get();
  if (!el || !el.isConnected) return false;
  if (sheet.toggled) return el.classList.contains('is-open');
  return !el.classList.contains('hidden') && el.getClientRects().length > 0;
}

function setExpanded(el, on) {
  el.classList.toggle('is-expanded', on);
  const button = $(':scope > .sheet-bar .sheet-expand', el);
  if (!button) return;
  button.setAttribute('aria-expanded', String(on));
  button.setAttribute('aria-label', on ? 'Collapse panel to half height' : 'Expand panel to full height');
  const text = $('.sheet-expand-text', button);
  if (text) text.textContent = on ? 'Collapse' : 'Expand';
}

function buildBar(sheet, el) {
  const bar = document.createElement('div');
  bar.className = 'sheet-bar';
  const expand = document.createElement('button');
  expand.type = 'button';
  expand.className = 'sheet-expand';
  expand.innerHTML = '<span class="sheet-grip" aria-hidden="true"></span>'
    + '<span class="sheet-expand-text" aria-hidden="true">Expand</span>';
  expand.addEventListener('click', () => setExpanded(el, !el.classList.contains('is-expanded')));
  const close = document.createElement('button');
  close.type = 'button';
  close.className = 'sheet-close';
  close.setAttribute('aria-label', sheet.closeLabel);
  close.innerHTML = '<span aria-hidden="true">×</span>';
  close.addEventListener('click', () => {
    if (sheet.toggled) closeToggled(sheet); else sheet.close();
  });
  bar.append(expand, close);
  return bar;
}

// The owning module rewrites a sheet's children (panels.js sets innerHTML on
// every render; the map redraws its sidebar), which removes the bar, so it is
// put back whenever it is missing. Direct children only, so the bar's own
// insertion cannot loop.
function decorate(sheet) {
  const el = sheet.get();
  if (!el || el.dataset.phoneSheet) return;
  el.dataset.phoneSheet = '1';
  el.setAttribute('role', 'dialog');
  el.removeAttribute('aria-modal');
  const label = () => el.setAttribute('aria-label', sheet.dialogLabel(el));
  label();
  const ensureBar = () => {
    if (!active) return;
    const first = el.firstElementChild;
    if (!first || !first.classList.contains('sheet-bar')) {
      el.prepend(buildBar(sheet, el));
      if (sheet.heading && !$(':scope > .phone-sheet-heading', el)) {
        const h2 = document.createElement('h2');
        h2.className = 'phone-sheet-heading';
        h2.textContent = sheet.heading;
        el.firstElementChild.after(h2);
      }
      setExpanded(el, el.classList.contains('is-expanded'));
    }
    if (!sheet.toggled) label();
  };
  ensureBar();
  const childObserver = new MutationObserver(ensureBar);
  childObserver.observe(el, { childList: true });
  undo.push(() => {
    childObserver.disconnect();
    delete el.dataset.phoneSheet;
    el.removeAttribute('role');
    el.removeAttribute('tabindex');
    el.classList.remove('is-open', 'is-expanded');
    // The aside / section keep the label they were authored with.
    const authored = { filters: 'Filters', layers: 'Map layers, places and legend', mode: null, detail: null, drawer: 'Selected feature' };
    const key = Object.keys(SHEETS).find((k) => SHEETS[k] === sheet);
    if (authored[key]) el.setAttribute('aria-label', authored[key]); else el.removeAttribute('aria-label');
    for (const node of el.querySelectorAll(':scope > .sheet-bar, :scope > .phone-sheet-heading')) node.remove();
  });
}

function openToggled(sheet) {
  const el = sheet.get();
  if (!el) return;
  for (const other of [SHEETS.filters, SHEETS.layers]) if (other !== sheet) closeToggled(other, false);
  el.classList.add('is-open');
  el.setAttribute('tabindex', '-1');
  const opener = sheet.opener();
  if (opener) opener.setAttribute('aria-expanded', 'true');
  el.focus({ preventScroll: true });
}

function closeToggled(sheet, restoreFocus = true) {
  const el = sheet.get();
  if (!el || !el.classList.contains('is-open')) return;
  const hadFocus = el.contains(document.activeElement);
  el.classList.remove('is-open');
  setExpanded(el, false);
  const opener = sheet.opener();
  if (opener) {
    opener.setAttribute('aria-expanded', 'false');
    if (restoreFocus && hadFocus) opener.focus({ preventScroll: true });
  }
}

// ------------------------------------------------------- header controls
const ICON_SLIDERS = '<svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true" focusable="false">'
  + '<path d="M3 5h8M15 5h2M3 10h2M9 10h8M3 15h9M16 15h1" stroke="currentColor" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
  + '<circle cx="13" cy="5" r="2" fill="currentColor"/><circle cx="7" cy="10" r="2" fill="currentColor"/>'
  + '<circle cx="14" cy="15" r="2" fill="currentColor"/></svg>';
const ICON_LAYERS = '<svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true" focusable="false">'
  + '<path d="M10 3l7 4-7 4-7-4zM3 11l7 4 7-4M3 14.5l7 4 7-4" stroke="currentColor" stroke-width="1.6" fill="none" stroke-linejoin="round" stroke-linecap="round"/></svg>';

function headerButton(id, html, attrs = {}) {
  const button = document.createElement('button');
  button.type = 'button';
  button.id = id;
  button.className = 'phone-action';
  button.innerHTML = html;
  for (const [key, value] of Object.entries(attrs)) button.setAttribute(key, value);
  return button;
}

function buildHeaderButtons() {
  const wrap = document.createElement('div');
  wrap.className = 'phone-actions';
  const filters = headerButton('phone-filters-btn',
    `${ICON_SLIDERS}<span class="phone-action-text">Views &amp; filters</span><span class="phone-badge" hidden></span>`,
    { 'aria-haspopup': 'dialog', 'aria-controls': 'filters-panel', 'aria-expanded': 'false' });
  const back = headerButton('phone-map-back-btn',
    '<span aria-hidden="true">←</span><span class="phone-action-text">Back to globe</span>');
  const layers = headerButton('phone-layers-btn',
    `${ICON_LAYERS}<span class="phone-action-text">Map layers</span>`,
    { 'aria-haspopup': 'dialog', 'aria-controls': 'map-layers', 'aria-expanded': 'false' });
  back.hidden = true;
  layers.hidden = true;
  wrap.append(back, layers, filters);
  const anchor = $('.search-wrap', els.header);
  els.header.insertBefore(wrap, anchor);

  filters.addEventListener('click', () => {
    const sheet = SHEETS.filters;
    if (sheet.get().classList.contains('is-open')) closeToggled(sheet); else openToggled(sheet);
  });
  layers.addEventListener('click', () => {
    const sheet = SHEETS.layers;
    if (!sheet.get()) return;
    if (sheet.get().classList.contains('is-open')) closeToggled(sheet); else openToggled(sheet);
  });
  back.addEventListener('click', () => {
    const real = document.getElementById('map-back');
    if (real) real.click(); else pressEscape();
  });
  undo.push(() => wrap.remove());
  headerButtons = { wrap, filters, back, layers };
}

function updateFilterBadge() {
  if (!headerButtons) return;
  const count = els.filterControls
    ? els.filterControls.querySelectorAll('.filter-chip:not(.filter-clear-all)').length : 0;
  const badge = $('.phone-badge', headerButtons.filters);
  badge.hidden = count === 0;
  badge.textContent = String(count);
  headerButtons.filters.setAttribute('aria-label',
    count ? `Views & filters, ${count} filter${count === 1 ? '' : 's'} active` : 'Views & filters');
}

let lastMapRoute = null;
function syncRoute() {
  if (!active || !headerButtons) return;
  const isMap = els.main.classList.contains('is-map-route');
  // A view (js/views/) has no filters, layers or sheets: its own frame carries a back
  // control, so the header buttons step aside there as well.
  const isView = els.main.classList.contains('is-view-route');
  document.body.classList.toggle('phone-map', isMap);
  headerButtons.filters.hidden = isMap || isView;
  headerButtons.back.hidden = !isMap;
  headerButtons.layers.hidden = !isMap;
  const offGlobe = isMap || isView;
  if (offGlobe !== lastMapRoute) {
    // A route change starts with every toggled sheet shut.
    closeToggled(SHEETS.filters, false);
    closeToggled(SHEETS.layers, false);
    // The globe stage is display:none on a map route, and any resize event
    // fired meanwhile (a sheet opening, the phone rotating) made globe.js
    // measure it as 0 x 0. Measure it again now that it is back.
    if (lastMapRoute && !offGlobe) window.requestAnimationFrame(() => window.dispatchEvent(new Event('resize')));
    lastMapRoute = offGlobe;
  }
  attachMapSheets();
}

function attachMapSheets() {
  if (!active) return;
  decorate(SHEETS.layers);
  decorate(SHEETS.drawer);
  watchSheets();
}

// ------------------------------------------------- sheet state -> layout
function syncStage() {
  if (!active) return;
  let height = 0;
  let covered = false;
  for (const sheet of Object.values(SHEETS)) {
    if (!isOpen(sheet)) continue;
    const el = sheet.get();
    if (el.classList.contains('is-expanded')) covered = true;
    height = Math.max(height, el.offsetHeight);
  }
  const next = covered ? 0 : height;
  if (Math.abs(next - stageHeight) < 1) return;
  stageHeight = next;
  els.main.style.setProperty('--sheet-h', `${next}px`);
  // The globe and Leaflet both size themselves from window resize.
  window.clearTimeout(stageTimer);
  stageTimer = window.setTimeout(() => window.dispatchEvent(new Event('resize')), 60);
}

let watched = new WeakSet();
let sheetObserver = null;
let sizeObserver = null;
let lastOpen = new Map();

function onSheetClassChange() {
  if (!active) return;
  // Exclusivity: a record or a list replaces the toggled sheets, and a
  // selection on the map replaces the layers sheet.
  const detailOpen = isOpen(SHEETS.detail);
  const modeOpen = isOpen(SHEETS.mode);
  const drawerOpen = isOpen(SHEETS.drawer);
  if (detailOpen || modeOpen) closeToggled(SHEETS.filters, false);
  if (drawerOpen) closeToggled(SHEETS.layers, false);
  for (const [key, sheet] of Object.entries(SHEETS)) {
    const open = isOpen(sheet);
    const el = sheet.get();
    if (el && !open && el.classList.contains('is-expanded')) setExpanded(el, false);
    if (key === 'mode' && open && !lastOpen.get('mode')) focusHeading(el);
    if (lastOpen.get(key) && !open && (key === 'mode' || key === 'drawer')) returnFocus(key, el);
    lastOpen.set(key, open);
  }
  syncStage();
}

// modes.js and the map hand focus back to the control that opened a list or a
// selection — a button inside a sheet that has since closed, which cannot take
// it. When focus is left on <body> (or in the panel that just went away), it
// goes to the header button that reaches the same place.
function returnFocus(key, el) {
  const now = document.activeElement;
  if (now && now !== document.body && !(el && el.contains(now))) return;
  const target = key === 'drawer' ? headerButtons && headerButtons.layers : headerButtons && headerButtons.filters;
  if (target && !target.hidden) target.focus({ preventScroll: true });
}

function focusHeading(el) {
  const heading = el && el.querySelector('h2');
  if (!heading) return;
  heading.setAttribute('tabindex', '-1');
  heading.focus({ preventScroll: true });
}

function watchSheets() {
  if (!sheetObserver) {
    sheetObserver = new MutationObserver(onSheetClassChange);
    sizeObserver = new ResizeObserver(() => syncStage());
    undo.push(() => {
      sheetObserver.disconnect();
      sizeObserver.disconnect();
      sheetObserver = null;
      sizeObserver = null;
      watched = new WeakSet();
    });
  }
  for (const sheet of Object.values(SHEETS)) {
    const el = sheet.get();
    if (!el || watched.has(el)) continue;
    watched.add(el);
    sheetObserver.observe(el, { attributes: true, attributeFilter: ['class', 'hidden'] });
    sizeObserver.observe(el);
  }
}

// ------------------------------------------------------- moved long texts
// The timeline's colour legend and the footer's data-version sentence are
// the two things that made the bottom of the screen 330 px tall. Both move
// into the filters sheet, where they are read once, and move back when the
// layout leaves phone width.
function moveInto(node, host) {
  if (!node || !host || node.parentNode === host) return;
  const parent = node.parentNode;
  const next = node.nextSibling;
  host.appendChild(node);
  undo.push(() => parent.insertBefore(node, next && next.parentNode === parent ? next : null));
}

// A disclosure section of the filters sheet. `first` puts it right under the
// sheet's heading, `before` in front of another node; the default is the end.
function ensureSheetSection(id, title, { open = true, first = false, before = null } = {}) {
  const sheet = els.filters;
  let section = document.getElementById(id);
  if (section) return $('.phone-section-body', section);
  section = document.createElement('details');
  section.id = id;
  section.className = 'phone-section';
  section.open = open;
  section.innerHTML = `<summary>${title}</summary><div class="phone-section-body"></div>`;
  if (first) {
    const anchor = $(':scope > .phone-sheet-heading', sheet) || $(':scope > .sheet-bar', sheet);
    if (anchor) anchor.after(section); else sheet.prepend(section);
  } else if (before && before.parentNode === sheet) {
    sheet.insertBefore(section, before);
  } else {
    sheet.appendChild(section);
  }
  undo.push(() => section.remove());
  return $('.phone-section-body', section);
}

function moveLongTexts() {
  // The laptop header's view switcher and Key popover content live in the sheet
  // here, as its first section and a collapsed "Key" (markers, dots and the
  // status colours, which the timeline's legend is part of) before the filters.
  const views = document.getElementById('mode-buttons');
  if (views && views.parentNode === els.header) {
    moveInto(views, ensureSheetSection('phone-views-section', 'View', { first: true }));
  }
  const key = document.getElementById('key-body');
  if (key && key.parentNode !== els.filters && !key.closest('.phone-section')) {
    const filtersSection = $(':scope > .filters-disclosure', els.filters);
    moveInto(key, ensureSheetSection('phone-key-section', 'Key', { open: false, before: filtersSection }));
  }
  if (els.versionLabel && els.versionLabel.textContent.trim() && els.versionLabel.parentNode === els.footer) {
    moveInto(els.versionLabel, ensureSheetSection('phone-data-section', 'About this data'));
  }
}

// -------------------------------------------------------- label declutter
// A world view puts a dozen ten-pixel captions on a 360 px globe and they
// overprint each other. Captions are only decoration (every marker carries
// its own accessible name and tooltip), so a caption that would land on a
// higher-priority one is hidden; the marker and its tap target stay.
let declutterTimer = null;

function overlap(a, b) {
  return !(a.right <= b.left || a.left >= b.right || a.bottom <= b.top || a.top >= b.bottom);
}

function declutter() {
  if (!active || els.main.classList.contains('is-map-route') || els.main.classList.contains('is-view-route')) return;
  const stage = document.getElementById('globe-stage');
  if (!stage) return;
  const box = stage.getBoundingClientRect();
  const cx = box.left + box.width / 2;
  const cy = box.top + box.height / 2;
  const candidates = [];
  const taken = [];
  for (const marker of document.querySelectorAll('.atlas-marker')) {
    const glyph = marker.firstElementChild;
    const rect = glyph ? glyph.getBoundingClientRect() : marker.getBoundingClientRect();
    if (!rect.width || !rect.height) continue;
    // Glyphs are obstacles for captions whether or not their own caption shows.
    taken.push({ left: rect.left - 2, right: rect.right + 2, top: rect.top - 2, bottom: rect.bottom + 2, owner: marker });
    const label = marker.querySelector('.atlas-marker-label');
    if (!label || marker.classList.contains('no-label')) continue;
    if (marker.classList.contains('tier-site') || marker.classList.contains('tier-institution')) continue;
    const tx = rect.left + rect.width / 2;
    const ty = rect.top + rect.height / 2;
    candidates.push({
      marker,
      label,
      priority: marker.classList.contains('is-cluster') ? 0 : 1,
      distance: Math.hypot(tx - cx, ty - cy),
    });
  }
  candidates.sort((a, b) => a.priority - b.priority || a.distance - b.distance);
  // Clear first so every caption is measured at its natural size.
  for (const c of candidates) c.marker.classList.remove('phone-label-off');
  const kept = [];
  for (const c of candidates) {
    const r = c.label.getBoundingClientRect();
    if (!r.width) continue;
    const hit = kept.some((k) => overlap(r, k))
      || taken.some((t) => t.owner !== c.marker && overlap(r, t));
    if (hit) c.marker.classList.add('phone-label-off'); else kept.push(r);
  }
}

function startDeclutter() {
  window.clearInterval(declutterTimer);
  declutterTimer = window.setInterval(() => {
    if (document.hidden) return;
    declutter();
  }, 400);
  undo.push(() => {
    window.clearInterval(declutterTimer);
    declutterTimer = null;
    for (const marker of document.querySelectorAll('.phone-label-off')) marker.classList.remove('phone-label-off');
  });
}

// ------------------------------------------------------------- keyboard
function onEscape(event) {
  if (!active || event.key !== 'Escape') return;
  if (event.target === els.search) return; // search.js owns Escape in its own box
  for (const sheet of [SHEETS.filters, SHEETS.layers]) {
    if (sheet.get() && sheet.get().classList.contains('is-open')) {
      event.stopPropagation();
      closeToggled(sheet);
      return;
    }
  }
}

// ----------------------------------------------------------- life cycle
function activate() {
  if (active || !els.main || !els.header || !els.filters) return;
  active = true;
  undo = [];
  buildHeaderButtons();
  decorate(SHEETS.filters);
  decorate(SHEETS.mode);
  decorate(SHEETS.detail);

  // Choosing a view from the sheet is the end of the sheet's job.
  const modeButtons = document.getElementById('mode-buttons');
  if (modeButtons) {
    const onModeClick = (event) => {
      if (event.target.closest('.mode-toggle')) closeToggled(SHEETS.filters, false);
    };
    modeButtons.addEventListener('click', onModeClick);
    undo.push(() => modeButtons.removeEventListener('click', onModeClick));
  }

  document.addEventListener('keydown', onEscape, true);
  undo.push(() => document.removeEventListener('keydown', onEscape, true));

  // Phone placeholder: the long one is cut off at this width.
  if (els.search) {
    const original = els.search.getAttribute('placeholder');
    els.search.setAttribute('placeholder', 'Search the atlas');
    undo.push(() => els.search.setAttribute('placeholder', original));
  }

  // Things that appear after the data has loaded.
  const lateObserver = new MutationObserver(() => {
    syncRoute();
    moveLongTexts();
    updateFilterBadge();
  });
  lateObserver.observe(els.main, { childList: true, attributes: true, attributeFilter: ['class'] });
  if (els.timelineBar) lateObserver.observe(els.timelineBar, { childList: true });
  if (els.footer) lateObserver.observe(els.footer, { childList: true, subtree: true, characterData: true });
  if (els.filterControls) lateObserver.observe(els.filterControls, { childList: true, subtree: true });
  undo.push(() => lateObserver.disconnect());

  watchSheets();
  lastMapRoute = null;
  syncRoute();
  moveLongTexts();
  updateFilterBadge();
  onSheetClassChange();
  startDeclutter();
}

function deactivate() {
  if (!active) return;
  active = false;
  for (const fn of undo.reverse()) fn();
  undo = [];
  headerButtons = null;
  document.body.classList.remove('phone-map');
  els.main.style.removeProperty('--sheet-h');
  stageHeight = 0;
  window.clearTimeout(stageTimer);
  window.dispatchEvent(new Event('resize'));
}

function apply() {
  if (mq.matches) activate(); else deactivate();
}

mq.addEventListener('change', apply);
apply();
