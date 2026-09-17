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
    </div>`;
}

async function main() {
  const { notice } = await loader.init();
  setNotice(notice);

  const [manifest, atlas, institutions, resultsBundle, documentsBundle, searchEntries] = await Promise.all([
    loader.getManifest(), loader.getAtlas(), loader.getInstitutions(),
    loader.getResults(), loader.getDocuments(), loader.getSearchEntries(),
  ]);
  void institutions;

  els.versionLabel.textContent = `Atlas data version ${manifest.data_version || manifest.version || ''} · coverage updated ${manifest.coverage_updated || manifest.build_date || ''}`;
  if (manifest.fixture && manifest.banner) {
    els.bannerLabel.textContent = manifest.banner;
    els.bannerLabel.classList.remove('hidden');
  }

  const index = buildIndex(atlas);
  renderLegend();

  let globeApi = null;
  const hasGL2 = globeModule.supportsWebGL2();

  function focusGlobe(id) {
    if (globeApi) globeApi.focus(id);
  }

  async function viewOnGlobe(collaborationId) {
    state.navigate({ entity: { type: 'collaboration', slug: collaborationId.split(':')[1] }, mode: 'collab' });
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
    setTimelineYear: (year) => { timeline.setYear(year); state.navigate({ year, range: null }, { replace: true }); },
  });

  search.init({
    inputEl: els.searchInput, listEl: els.searchResults, entries: searchEntries, navigate: state.navigate,
  });

  if (hasGL2) {
    try {
      if (!window.Globe) await loadVendorScript('vendor/globe.gl.min.js');
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
      fallback.render(els.fallbackContainer, { atlas, results: resultsBundle, navigate: state.navigate });
    }
  } else {
    els.globeContainer.classList.add('hidden');
    els.fallbackContainer.classList.remove('hidden');
    fallback.render(els.fallbackContainer, { atlas, results: resultsBundle, navigate: state.navigate });
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

    if (current.year != null) timeline.setYear(current.year);
    else if (current.range) timeline.setRange(current.range[0], current.range[1]);

    const isCollabMode = current.mode === 'collab' && current.entity && current.entity.type === 'collaboration';
    if (isCollabMode) {
      const collabId = `collaboration:${current.entity.slug}`;
      if (collabId !== lastCollabShown) {
        lastCollabShown = collabId;
        panels.setCollaborationContext(collabId);
        if (globeApi) {
          const membership = await loader.getMembership(collabId);
          globeApi.setCollaboration(collabId, membership);
        }
      }
    } else if (lastCollabShown) {
      lastCollabShown = null;
      if (globeApi) globeApi.clearCollaboration();
    }

    if (current.mode && current.mode !== 'collab') {
      modes.show(current.mode);
    } else {
      modes.show(null);
    }
    await panels.render(current.entity);
  }

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
