// app.js — HEP Atlas bootstrap. Wires loader, state, globe (or fallback),
// timeline, panels, modes and search together. No inline scripts anywhere:
// this file and everything it imports are same-origin <script type="module">.

import * as loader from './loader.js';
import * as state from './state.js';
import * as globeModule from './globe.js';
import { createTimeline } from './timeline.js';
import * as panels from './panels.js';
import * as modes from './modes.js';
import * as search from './search.js';
import * as fallback from './fallback.js';
import * as filtersModule from './filters.js';
import * as localmap from './localmap.js';
import { createChrome } from './chrome.js';
import * as startModule from './start.js';
import { createViewHost } from './views/host.js';
import { mountTray } from './research/compare-tray.js';
import { viewSearchEntries } from './views/registry.js';
import { buildIndex, topicMarkerIds } from './model.js';
import { facilityKeyEntries } from './globeicons.js';

const els = {
  dataNotice: document.getElementById('data-notice'),
  versionLabel: document.getElementById('data-version-label'),
  bannerLabel: document.getElementById('fixture-banner'),
  globeContainer: document.getElementById('globe-container'),
  fallbackContainer: document.getElementById('fallback-container'),
  modePanel: document.getElementById('mode-panel'),
  detailPanel: document.getElementById('detail-panel'),
  timelineBar: document.getElementById('timeline-bar'),
  modeButtons: document.getElementById('mode-buttons'),
  arcsToggle: document.getElementById('arcs-toggle'),
  arcsAutoOffNote: document.getElementById('arcs-auto-off-note'),
  filtersControls: document.getElementById('filters-controls'),
  legend: document.getElementById('marker-legend'),
  searchInput: document.getElementById('atlas-search'),
  searchResults: document.getElementById('search-results'),
  shareBtn: document.getElementById('share-link'),
  shareStatus: document.getElementById('share-status'),
  errorBanner: document.getElementById('atlas-error'),
  errorMessage: document.getElementById('atlas-error-message'),
  retryBtn: document.getElementById('atlas-retry'),
};

// P1-4 (docs/atlas-worklog/REVIEW_performance.md): on a slow or offline
// connection the page used to sit blank with no spinner and no text. These
// two states are the fix — both are plain visible text in an aria-live
// region, not a purely visual spinner, and the error state names what
// failed and offers a real retry instead of leaving the globe stage empty.
function showError(message) {
  if (els.errorMessage) els.errorMessage.textContent = message;
  if (els.errorBanner) els.errorBanner.classList.remove('hidden');
  setNotice(null);
}

if (els.retryBtn) {
  els.retryBtn.addEventListener('click', () => window.location.reload());
}

function loadVendorScript(src) {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = src;
    script.onload = resolve;
    script.onerror = () => reject(new Error(`Failed to load ${src}`));
    document.head.appendChild(script);
  });
}

function setNotice(text) {
  if (!text) {
    els.dataNotice.classList.add('hidden');
    els.dataNotice.textContent = '';
    return;
  }
  els.dataNotice.textContent = text;
  els.dataNotice.classList.remove('hidden');
}

function renderLegend() {
  // The facility glyphs are the very SVGs the globe draws, so the Key cannot drift
  // from the markers it explains.
  els.legend.innerHTML = `
    <div class="legend-group" id="legend-facility-kinds"><strong>Facility shape</strong></div>
    <div class="legend-group"><strong>Institution dot</strong>
      <span class="legend-item"><i class="dot solid"></i>Confirmed / counted</span>
      <span class="legend-item"><i class="dot hollow"></i>Uncounted / historical</span>
    </div>
    <div class="legend-group"><strong>Location precision</strong>
      <span class="legend-item"><i class="dot approximate"></i>Approximate location (campus-grade coordinate)</span>
    </div>`;
  const kinds = els.legend.querySelector('#legend-facility-kinds');
  for (const entry of facilityKeyEntries()) {
    const item = document.createElement('span');
    item.className = 'legend-item';
    entry.svg.setAttribute('aria-hidden', 'true');
    item.append(entry.svg, entry.label);
    kinds.append(item);
  }
}

async function main() {
  // Read the URL before anything else. The components created below call
  // state.navigate() as they initialise, and navigate() rebuilds the address
  // from the current state — so if the route has not been parsed yet, the
  // entity in a shared link is written out of the URL before it is ever read,
  // and every deep link opens the globe with no panel.
  // Decided from the address as it arrived — the timeline rewrites it (?y=) as it starts.
  const firstVisit = startModule.isFirstVisit();
  state.init();

  // The header's Key and Filters buttons answer from the first paint, not only once
  // the data has arrived (the Key's marker legend needs none of it).
  renderLegend();
  const chrome = createChrome();

  // Visible text in an aria-live region (#data-notice is role="status"),
  // shown for the whole cold-load fetch below, not just the initial probe —
  // on a throttled connection this is what used to be a blank globe stage
  // with no explanation (P1-4).
  setNotice('Loading HEP Atlas… this can take a few seconds on a slow connection.');

  const { notice, error } = await loader.init();
  // On a non-dev host with no generated bundle, loader.init() reports an
  // error instead of a base path (see loader.js's resolveBase): showing the
  // fixture tree there would masquerade development data as the real atlas.
  // Stop before any get*() call, which would otherwise fail against a null
  // base with a confusing "nullmanifest.json" message.
  if (error) {
    showError(error);
    return;
  }

  // Only what the first view needs. institutions.json is half a megabyte and
  // is not read until a collaboration or an institution is opened; results and
  // documents are fetched when their modes are.
  const [manifest, atlas, searchEntries] = await Promise.all([
    loader.getManifest(), loader.getAtlas(), loader.getSearchEntries(),
  ]);
  const [resultsBundle, documentsBundle] = await Promise.all([
    loader.getResults(), loader.getDocuments(),
  ]);

  // Replace the loading text with the fixture-fallback notice, if any, or
  // clear it now that the cold load has actually finished.
  setNotice(notice);

  // Coverage is partial and the footer says so: the atlas holds what its
  // registry has researched, not every experiment in the field (spec §104).
  // "the coverage report" is a real link to the methodology page's live
  // Coverage section (about.html reads the same manifest/coverage bundles,
  // so it can never drift from these numbers) — built with DOM calls rather
  // than an HTML string so nothing here depends on escaping manifest text.
  const counts = manifest.counts || {};
  els.versionLabel.textContent = '';
  els.versionLabel.appendChild(document.createTextNode(
    `Atlas data version ${manifest.data_version || manifest.version || ''} · coverage updated ${manifest.coverage_updated || manifest.build_date || ''}`
  ));
  if (counts.experiments) {
    els.versionLabel.appendChild(document.createTextNode(
      ` · ${counts.experiments} experiments researched — partial coverage of the field, see `
    ));
    const coverageLink = document.createElement('a');
    coverageLink.href = '/atlas/about.html#coverage';
    coverageLink.className = 'footer-link';
    coverageLink.textContent = 'the coverage report';
    els.versionLabel.appendChild(coverageLink);
  } else {
    els.versionLabel.appendChild(document.createTextNode(' · partial coverage of the field'));
  }
  if (manifest.fixture && manifest.banner) {
    els.bannerLabel.textContent = manifest.banner;
    els.bannerLabel.classList.remove('hidden');
  }

  const index = buildIndex(atlas);

  // ---- filters (docs/HEP_ATLAS_ARCHITECTURE.md "Clustering and filters")
  const topicIndex = filtersModule.buildTopicIndex(atlas.topics);
  // Built once and reused (mirrors topicIndex above), rather than inside the
  // fallback's own render() on every state change — same site->experiment
  // lookup globe.js already builds for marker visibility (filters.js's
  // siteMatches needs it because a site carries no kind/topic_ids of its own).
  const siteExperimentIndex = filtersModule.buildSiteExperimentIndex(atlas);
  const filterPanel = filtersModule.createFilterPanel(els.filtersControls, {
    atlas,
    topicIndex,
    onChange: (nextFilters) => {
      state.navigate(filtersModule.filtersToPatch(nextFilters), { replace: true });
    },
  });

  let globeApi = null;
  let fallbackActive = false;
  const startHere = startModule.createStartHere({
    card: document.getElementById('start-card'),
    reopenButton: document.getElementById('start-here-link'),
    searchInput: els.searchInput,
    getGlobe: () => globeApi,
    firstVisit,
  });
  const hasGL2 = globeModule.supportsWebGL2();

  function renderFallbackIfActive(current) {
    if (!fallbackActive) return;
    const filters = filtersModule.filtersFromState(current);
    const timelineState = current.range ? { range: current.range } : { year: current.year };
    fallback.render(els.fallbackContainer, {
      atlas, results: resultsBundle, navigate: state.navigate, filters, timelineState, topicIndex, siteExperimentIndex,
    });
  }

  // The camera follows the *selection* (applyState -> globeApi.select), which
  // runs the moment the route changes. The panels also announce an id when
  // they finish rendering, and re-render on every filter and timeline change;
  // flying the camera on each of those is what used to pull it back after the
  // person had moved it, so this callback is deliberately inert.
  function focusGlobe() {}

  async function viewOnGlobe(collaborationId) {
    // `collab` keeps the context in the URL, so a link to an institution can say
    // which collaboration it is being viewed within.
    const slug = collaborationId.split(':')[1];
    state.navigate({ entity: { type: 'collaboration', slug }, mode: 'collab', collab: slug });
  }

  panels.init({
    el: els.detailPanel, atlas, index, navigate: state.navigate, focusGlobe, viewOnGlobe,
  });

  // The compare tray (js/research/compare-tray.js): the experiments chosen with "Add to
  // compare", in a corner of the stage while it holds any.
  mountTray({ main: document.getElementById('atlas-main'), atlas, navigate: state.navigate });

  // The views' frame (js/views/host.js): mounted lazily, only when a `#/view/...` route opens.
  const views = createViewHost({
    main: document.getElementById('atlas-main'), atlas, index, loader, navigate: state.navigate,
  });

  modes.init({
    container: els.modePanel,
    atlas,
    results: resultsBundle,
    documents: documentsBundle,
    navigate: state.navigate,
    getState: state.get,
    setTimelineYear: (year) => timeline.setYear(year),
  });

  // Views (js/views/registry.js) add their own rows, so "beam through the Earth" and
  // "DUNE beam" reach the beam section without the build knowing about views.
  search.init({
    inputEl: els.searchInput,
    listEl: els.searchResults,
    entries: [...searchEntries, ...viewSearchEntries(atlas)],
    navigate: state.navigate,
    // Experiments, facilities and results are also found through the research
    // topic they are filed under (search "Higgs", reach ATLAS, CMS and CERN).
    atlas,
    results: resultsBundle.list,
  });

  if (hasGL2) {
    try {
      if (!window.Globe) await loadVendorScript('/atlas/vendor/globe.gl.min.js');
      globeApi = globeModule.createGlobe(els.globeContainer, {
        atlas,
        index,
        onSelect: (route) => state.navigate({ entity: route }),
        coverElements: [els.detailPanel, els.modePanel],
      });
      globeApi.ready();
      window.addEventListener('resize', () => globeApi.resize());
    } catch (error) {
      window.console.error(error);
      els.globeContainer.classList.add('hidden');
      els.fallbackContainer.classList.remove('hidden');
      fallbackActive = true;
      renderFallbackIfActive(state.get());
    }
  } else {
    els.globeContainer.classList.add('hidden');
    els.fallbackContainer.classList.remove('hidden');
    fallbackActive = true;
    renderFallbackIfActive(state.get());
  }

  // ---- timeline -------------------------------------------------------
  const timeline = createTimeline(els.timelineBar, {
    minYear: (manifest.timeline && manifest.timeline.min_year) || 1950,
    maxYear: (manifest.timeline && manifest.timeline.max_year) || new Date().getFullYear() + 10,
    defaultYear: (manifest.timeline && manifest.timeline.default_year) || new Date().getFullYear(),
    onChange: (t) => {
      if (globeApi) {
        if (t.mode === 'year') globeApi.setYear(t.year); else globeApi.setRange(t.range[0], t.range[1]);
      }
      const timelineState = t.mode === 'year' ? { year: t.year } : { range: t.range };
      filterPanel.updateForTimeline(timelineState);
      state.navigate(t.mode === 'year' ? { year: t.year, range: null } : { year: null, range: t.range }, { replace: true });
    },
  });

  // The status legend the timeline builds is part of the Key popover now, not a
  // row of the timeline bar.
  chrome.adoptStatusLegend(document.getElementById('timeline-legend'));

  // ---- mode buttons / arcs toggle --------------------------------------
  els.modeButtons.addEventListener('click', (event) => {
    const btn = event.target.closest('.mode-toggle');
    if (!btn) return;
    state.navigate({ mode: btn.dataset.mode || null });
  });
  els.arcsToggle.addEventListener('change', () => {
    state.navigate({ arcs: els.arcsToggle.checked }, { replace: true });
  });

  // ---- Escape closes the open panel (§23) -------------------------------
  // The detail panel and the topic/results/docs mode panel are the only two
  // dismissible overlays; the filters panel and legend are always-visible
  // <details> that don't need this. panels.js's own render(null, ...) branch
  // returns focus to whatever opened the panel, so this only needs to decide
  // *which* panel Escape should close, in "closest" order: detail panel
  // first (it renders on top of the mode panel), then the mode panel.
  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    const current = state.get();
    if (current.entity && current.entity.type === 'view') {
      views.back();
    } else if (current.entity) {
      state.navigate({ entity: null });
    } else if (current.mode && current.mode !== 'collab') {
      state.navigate({ mode: null });
    }
  });

  // ---- share link -------------------------------------------------------
  // Copying needs clipboard permission, which many phones (and any page on a
  // non-secure origin) do not give. Then the address goes into a read-only field
  // that is already selected, with the instruction for the device in use, rather
  // than being dumped into the status line as an unexplained URL.
  let shareTimer = 0;
  function clearShareStatus() {
    window.clearTimeout(shareTimer);
    els.shareStatus.textContent = '';
    els.shareStatus.classList.remove('is-fallback');
  }
  function showShareFallback(url) {
    const touch = window.matchMedia('(max-width: 900px), (pointer: coarse)').matches;
    const message = document.createElement('span');
    message.className = 'share-status-text';
    message.textContent = touch ? 'Press and hold to copy' : 'Press Ctrl+C (⌘C on a Mac) to copy';
    const field = document.createElement('input');
    field.type = 'text';
    field.readOnly = true;
    field.className = 'share-url';
    field.value = url;
    field.setAttribute('aria-label', 'Share link');
    const done = document.createElement('button');
    done.type = 'button';
    done.className = 'text-btn share-done';
    done.textContent = 'Done';
    done.addEventListener('click', () => { clearShareStatus(); els.shareBtn.focus({ preventScroll: true }); });
    field.addEventListener('keydown', (event) => {
      if (event.key !== 'Escape') return;
      event.stopPropagation(); // dismisses this, not the record panel behind it
      done.click();
    });
    els.shareStatus.replaceChildren(message, field, done);
    els.shareStatus.classList.add('is-fallback');
    // Selected on the tap itself (iOS only honours it inside the gesture), so
    // press-and-hold or the keyboard shortcut copies the whole link.
    field.focus({ preventScroll: true });
    field.select();
    field.setSelectionRange(0, url.length);
  }
  els.shareBtn.addEventListener('click', async () => {
    clearShareStatus();
    const url = window.location.href;
    try {
      await navigator.clipboard.writeText(url);
    } catch (error) {
      showShareFallback(url);
      return;
    }
    els.shareStatus.textContent = 'Link copied.';
    shareTimer = window.setTimeout(clearShareStatus, 4000);
  });

  // ---- state <-> UI -----------------------------------------------------
  let lastCollabShown = null;
  // Which topic the globe is currently highlighting for (or null).
  let highlightedTopic = null;
  async function applyState(current) {
    for (const btn of els.modeButtons.querySelectorAll('.mode-toggle')) {
      const on = (btn.dataset.mode || null) === (current.mode || null);
      btn.classList.toggle('is-active', on);
      btn.setAttribute('aria-pressed', String(on));
    }
    els.arcsToggle.checked = !!current.arcs;
    if (globeApi) globeApi.setArcsEnabled(!!current.arcs);

    const filters = filtersModule.filtersFromState(current);
    filterPanel.setFilters(filters);
    chrome.setFilterCount(Object.values(filters).reduce((sum, list) => sum + list.length, 0));
    if (globeApi) globeApi.setFilters(filters);
    renderFallbackIfActive(current);

    // An open topic highlights the facilities and sites of its experiments and
    // mutes the rest, for exactly as long as that topic is the open route. It is
    // derived from the route here — not set by the Topics list when a link is
    // clicked — so it survives the panel opening, and a link, a search result or
    // Back/Forward reaches the same picture.
    if (globeApi) {
      const topicId = current.entity && current.entity.type === 'topic'
        ? `topic:${current.entity.slug}` : null;
      if (topicId !== highlightedTopic) {
        highlightedTopic = topicId;
        const markers = topicId ? topicMarkerIds(atlas, topicId) : null;
        globeApi.setHighlight(markers && markers.size ? markers : null);
        // The camera goes to what is lit: the places the topic is about.
        if (markers && markers.size) globeApi.fitHighlight();
      }
    }

    // The open panel's entity: highlight its markers and fly the camera there
    // (a no-op while it is unchanged). In collaboration mode setCollaboration()
    // below owns the camera, so only the highlight is applied.
    if (globeApi) {
      const entity = current.entity && current.entity.type !== 'map' && current.entity.type !== 'view'
        ? `${current.entity.type}:${current.entity.slug}` : null;
      const cameraOwnedByCollaboration = current.mode === 'collab'
        && !!current.entity && current.entity.type === 'collaboration';
      globeApi.select(entity, { fly: !cameraOwnedByCollaboration });
    }

    timeline.syncFromState(current);

    // A shared institution link carries its collaboration in `c`.
    if (current.collab) panels.setCollaborationContext(`collaboration:${current.collab}`);

    const isCollabMode = current.mode === 'collab' && current.entity && current.entity.type === 'collaboration';
    if (isCollabMode) {
      const collabId = `collaboration:${current.entity.slug}`;
      if (collabId !== lastCollabShown) {
        lastCollabShown = collabId;
        panels.setCollaborationContext(collabId);
        if (current.collab !== current.entity.slug) {
          state.navigate({ collab: current.entity.slug }, { replace: true });
        }
        if (globeApi) {
          const membership = await loader.getMembership(collabId);
          if (!membership) {
            // The build wrote no roster for this collaboration (a shared link
            // can still ask for one): there are no institutions to put on the
            // globe, so leave collaboration mode. The record panel says why.
            lastCollabShown = null;
            panels.setCollaborationContext(null);
            state.navigate({ mode: null, collab: null }, { replace: true });
            return;
          }
          await globeApi.setCollaboration(collabId, membership);
          // §75: default the arcs off for very large collaborations
          // (INSTITUTION_ARC_THRESHOLD, docs/atlas-worklog/REVIEW_performance.md
          // "Closure of P1-3"). This only resets the default on first
          // *entering* a large collaboration — the checkbox stays a normal,
          // bidirectional toggle afterwards (it always reflects exactly
          // what's drawn; see globe.js's arcsData assembly).
          const forcedOff = globeApi.isArcsForcedOff();
          els.arcsAutoOffNote.classList.toggle('hidden', !forcedOff);
          els.arcsAutoOffNote.textContent = forcedOff
            ? `Institution connections are off by default for collaborations over ${globeModule.INSTITUTION_ARC_THRESHOLD} institutions. Open Filters and tick \u201cShow institution connections\u201d to show them anyway.`
            : '';
          if (forcedOff && current.arcs) {
            state.navigate({ arcs: false }, { replace: true });
            return;
          }
        }
      }
    } else if (lastCollabShown) {
      lastCollabShown = null;
      if (globeApi) globeApi.clearCollaboration();
      els.arcsAutoOffNote.classList.add('hidden');
      els.arcsAutoOffNote.textContent = '';
    }

    // ---- views (js/views/) -- begin ---------------------------------------
    // `#/view/<name>/<arg>` takes over #atlas-main the way the local map does: the
    // globe stage, the lists and the record panel step aside and the view's frame
    // (views/host.js) holds the whole stage. A view loads its module only now.
    const viewRoute = current.entity && current.entity.type === 'view' ? current.entity : null;
    const mainEl = document.getElementById('atlas-main');
    mainEl.classList.toggle('is-view-route', !!viewRoute);
    document.body.classList.toggle('is-view-route', !!viewRoute);
    if (viewRoute) {
      mainEl.classList.remove('is-map-route');
      document.body.classList.remove('is-map-route');
      chrome.closeAll();
      modes.show(null);
      els.detailPanel.classList.add('hidden');
      els.detailPanel.innerHTML = '';
      if (localmap.isOpen()) {
        localmap.hide();
        panels.init({
          el: els.detailPanel, atlas, index, navigate: state.navigate, focusGlobe, viewOnGlobe,
        });
      }
      await views.show(current);
      return;
    }
    views.hide(current);
    // ---- views -- end -----------------------------------------------------

    if (current.mode && current.mode !== 'collab') {
      modes.show(current.mode, current);
    } else {
      modes.show(null);
    }
    // ---- local map view (docs/HEP_ATLAS_GEOMETRY.md §4) -- begin --------
    // `#/map/<slug>` takes over #atlas-main: filters, globe stage and mode
    // panel step aside for a three-column map layout, and panels.js is
    // re-pointed at the map's drawer so the selected entity gets its normal
    // detail panel there rather than in the (now hidden) side panel.
    const mapRoute = current.entity && current.entity.type === 'map' ? current.entity : null;
    document.getElementById('atlas-main').classList.toggle('is-map-route', !!mapRoute);
    document.body.classList.toggle('is-map-route', !!mapRoute);
    if (mapRoute) chrome.closeAll();
    if (mapRoute) {
      const mapTimeline = current.range ? { range: current.range } : { year: current.year };
      modes.show(null);
      els.detailPanel.classList.add('hidden');
      els.detailPanel.innerHTML = '';
      panels.init({
        el: localmap.drawerPanelEl(), atlas, index, navigate: state.navigate, focusGlobe, viewOnGlobe,
      });
      await localmap.show(current, {
        atlas, index, navigate: state.navigate, panels, timelineState: mapTimeline,
        loaderBase: loader.base(),
      });
      return;
    }
    if (localmap.isOpen()) {
      localmap.hide();
      panels.init({
        el: els.detailPanel, atlas, index, navigate: state.navigate, focusGlobe, viewOnGlobe,
      });
    }
    // ---- local map view -- end ------------------------------------------

    // Same shape the timeline itself tracks: a range takes precedence over a
    // single year (matches timeline.js's own onChange payload and globe.js's
    // setYear/setRange split), so the detail panel's status badge always
    // reflects exactly what's currently selected.
    const timelineState = current.range ? { range: current.range } : { year: current.year };
    await panels.render(current.entity, timelineState);
  }

  // Seed the timeline from the URL before it announces anything, so a shared
  // link that names a year or a range keeps it.
  timeline.syncFromState(state.get());
  timeline.start();

  state.subscribe((current) => { applyState(current); });
  const initial = state.init();
  await applyState(initial);
  startHere.openFirstVisit();
}

main().catch((error) => {
  window.console.error('HEP Atlas failed to start', error);
  const offline = typeof navigator !== 'undefined' && navigator.onLine === false;
  showError(offline
    ? 'You appear to be offline, so HEP Atlas could not load. Check your connection and retry.'
    : `HEP Atlas could not load: ${error.message}. Check your connection and retry.`);
});
