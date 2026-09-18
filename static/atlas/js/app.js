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
import { buildIndex } from './model.js';

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
};

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
  els.legend.innerHTML = `
    <div class="legend-group"><strong>Facility shape</strong>
      <span class="legend-item"><i class="glyph ring"></i>Accelerator laboratory</span>
      <span class="legend-item"><i class="glyph triangle-down"></i>Underground laboratory</span>
      <span class="legend-item"><i class="glyph hexagon"></i>Neutrino observatory</span>
      <span class="legend-item"><i class="glyph diamond"></i>Astroparticle observatory</span>
      <span class="legend-item"><i class="glyph snowflake"></i>Polar station</span>
      <span class="legend-item"><i class="glyph square"></i>Reactor site</span>
    </div>
    <div class="legend-group"><strong>Institution dot</strong>
      <span class="legend-item"><i class="dot solid"></i>Confirmed / counted</span>
      <span class="legend-item"><i class="dot hollow"></i>Uncounted / historical</span>
    </div>
    <div class="legend-group"><strong>Location precision</strong>
      <span class="legend-item"><i class="dot approximate"></i>Approximate location (campus-grade coordinate)</span>
    </div>`;
}

async function main() {
  // Read the URL before anything else. The components created below call
  // state.navigate() as they initialise, and navigate() rebuilds the address
  // from the current state — so if the route has not been parsed yet, the
  // entity in a shared link is written out of the URL before it is ever read,
  // and every deep link opens the globe with no panel.
  state.init();

  const { notice } = await loader.init();
  setNotice(notice);

  // Only what the first view needs. institutions.json is half a megabyte and
  // is not read until a collaboration or an institution is opened; results and
  // documents are fetched when their modes are.
  const [manifest, atlas, searchEntries] = await Promise.all([
    loader.getManifest(), loader.getAtlas(), loader.getSearchEntries(),
  ]);
  const [resultsBundle, documentsBundle] = await Promise.all([
    loader.getResults(), loader.getDocuments(),
  ]);

  els.versionLabel.textContent = `Atlas data version ${manifest.data_version || manifest.version || ''} · coverage updated ${manifest.coverage_updated || manifest.build_date || ''}`;
  if (manifest.fixture && manifest.banner) {
    els.bannerLabel.textContent = manifest.banner;
    els.bannerLabel.classList.remove('hidden');
  }

  const index = buildIndex(atlas);
  renderLegend();

  // ---- filters (docs/HEP_ATLAS_ARCHITECTURE.md "Clustering and filters")
  const topicIndex = filtersModule.buildTopicIndex(atlas.topics);
  const filterPanel = filtersModule.createFilterPanel(els.filtersControls, {
    atlas,
    topicIndex,
    onChange: (nextFilters) => {
      state.navigate(filtersModule.filtersToPatch(nextFilters), { replace: true });
    },
  });

  let globeApi = null;
  let fallbackActive = false;
  const hasGL2 = globeModule.supportsWebGL2();

  function renderFallbackIfActive(current) {
    if (!fallbackActive) return;
    const filters = filtersModule.filtersFromState(current);
    const timelineState = current.range ? { range: current.range } : { year: current.year };
    fallback.render(els.fallbackContainer, {
      atlas, results: resultsBundle, navigate: state.navigate, filters, timelineState, topicIndex,
    });
  }

  function focusGlobe(id) {
    if (globeApi) globeApi.focus(id);
  }

  async function viewOnGlobe(collaborationId) {
    // `collab` keeps the context in the URL, so a link to an institution can say
    // which collaboration it is being viewed within.
    const slug = collaborationId.split(':')[1];
    state.navigate({ entity: { type: 'collaboration', slug }, mode: 'collab', collab: slug });
  }

  panels.init({
    el: els.detailPanel, atlas, index, navigate: state.navigate, focusGlobe, viewOnGlobe,
  });

  modes.init({
    container: els.modePanel,
    atlas,
    results: resultsBundle,
    documents: documentsBundle,
    navigate: state.navigate,
    highlightGlobe: (idSet) => globeApi && globeApi.setHighlight(idSet),
    setTimelineYear: (year) => timeline.setYear(year),
  });

  search.init({
    inputEl: els.searchInput, listEl: els.searchResults, entries: searchEntries, navigate: state.navigate,
  });

  if (hasGL2) {
    try {
      if (!window.Globe) await loadVendorScript('/atlas/vendor/globe.gl.min.js');
      globeApi = globeModule.createGlobe(els.globeContainer, {
        atlas,
        index,
        onSelect: (route) => state.navigate({ entity: route }),
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

  // ---- mode buttons / arcs toggle --------------------------------------
  els.modeButtons.addEventListener('click', (event) => {
    const btn = event.target.closest('.mode-toggle');
    if (!btn) return;
    state.navigate({ mode: btn.dataset.mode || null });
  });
  els.arcsToggle.addEventListener('change', () => {
    state.navigate({ arcs: els.arcsToggle.checked }, { replace: true });
  });

  // ---- share link -------------------------------------------------------
  els.shareBtn.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      els.shareStatus.textContent = 'Link copied.';
    } catch (error) {
      els.shareStatus.textContent = window.location.href;
    }
    window.setTimeout(() => { els.shareStatus.textContent = ''; }, 4000);
  });

  // ---- state <-> UI -----------------------------------------------------
  let lastCollabShown = null;
  async function applyState(current) {
    for (const btn of els.modeButtons.querySelectorAll('.mode-toggle')) {
      btn.classList.toggle('is-active', (btn.dataset.mode || null) === (current.mode || null));
    }
    els.arcsToggle.checked = !!current.arcs;
    if (globeApi) globeApi.setArcsEnabled(!!current.arcs);

    const filters = filtersModule.filtersFromState(current);
    filterPanel.setFilters(filters);
    if (globeApi) globeApi.setFilters(filters);
    renderFallbackIfActive(current);

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
            ? `Institution connections are off by default for collaborations over ${globeModule.INSTITUTION_ARC_THRESHOLD} institutions. Use the checkbox above to show them anyway.`
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

    if (current.mode && current.mode !== 'collab') {
      modes.show(current.mode);
    } else {
      modes.show(null);
    }
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
}

main().catch((error) => {
  window.console.error('HEP Atlas failed to start', error);
  const el = document.getElementById('data-notice');
  if (el) {
    el.textContent = `HEP Atlas could not load: ${error.message}`;
    el.classList.remove('hidden');
  }
});
