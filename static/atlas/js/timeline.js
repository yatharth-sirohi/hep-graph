// timeline.js — the year slider. Single-date and range modes, a restrained
// play button, keyboard (native to <input type=range>) and touch operable.

function clamp(v, lo, hi) {
  return Math.min(hi, Math.max(lo, v));
}

export function createTimeline(container, { minYear, maxYear, defaultYear, onChange }) {
  container.innerHTML = '';
  // A landmark, not just a group: #timeline-bar sits outside <main> as its
  // own top-level section (between the globe/panels and the footer), so
  // role="group" left it uncontained by any landmark (axe "region"). A
  // labelled region lets a screen-reader user jump to it directly, the way
  // they already can for the filters aside and the main content area.
  container.setAttribute('role', 'region');
  container.setAttribute('aria-label', 'Timeline');

  const modeRow = document.createElement('div');
  modeRow.className = 'timeline-modes';
  const yearBtn = document.createElement('button');
  yearBtn.type = 'button';
  yearBtn.className = 'mode-btn is-active';
  yearBtn.textContent = 'Single date';
  yearBtn.id = 'timeline-mode-year';
  const rangeBtn = document.createElement('button');
  rangeBtn.type = 'button';
  rangeBtn.className = 'mode-btn';
  rangeBtn.textContent = 'Range';
  rangeBtn.id = 'timeline-mode-range';
  const playBtn = document.createElement('button');
  playBtn.type = 'button';
  playBtn.className = 'mode-btn play-btn';
  playBtn.id = 'timeline-play';
  playBtn.setAttribute('aria-pressed', 'false');
  playBtn.textContent = '▶ Play';
  modeRow.append(yearBtn, rangeBtn, playBtn);

  const sliderRow = document.createElement('div');
  sliderRow.className = 'timeline-sliders';

  const yearInput = document.createElement('input');
  yearInput.type = 'range';
  yearInput.id = 'timeline-year';
  yearInput.min = String(minYear);
  yearInput.max = String(maxYear);
  yearInput.value = String(defaultYear);
  yearInput.setAttribute('aria-label', 'Year');

  const loInput = document.createElement('input');
  loInput.type = 'range';
  loInput.id = 'timeline-range-lo';
  loInput.min = String(minYear);
  loInput.max = String(maxYear);
  loInput.value = String(Math.max(minYear, defaultYear - 15));
  loInput.setAttribute('aria-label', 'Range start year');

  const hiInput = document.createElement('input');
  hiInput.type = 'range';
  hiInput.id = 'timeline-range-hi';
  hiInput.min = String(minYear);
  hiInput.max = String(maxYear);
  hiInput.value = String(defaultYear);
  hiInput.setAttribute('aria-label', 'Range end year');

  const rangeWrap = document.createElement('div');
  rangeWrap.className = 'timeline-range-wrap hidden';
  rangeWrap.append(loInput, hiInput);

  sliderRow.append(yearInput, rangeWrap);

  const readout = document.createElement('div');
  readout.className = 'timeline-readout';
  readout.id = 'timeline-readout';
  readout.setAttribute('aria-live', 'polite');

  const legend = document.createElement('div');
  legend.className = 'timeline-legend';
  legend.id = 'timeline-legend';

  container.append(modeRow, sliderRow, readout, legend);

  let mode = 'year';
  let playing = false;
  let timer = null;

  function legendHTML() {
    const shared = [
      ['dot active', 'Active'],
      ['dot construction', 'Construction / commissioning'],
      ['dot dimmed', 'Proposed / approved / planned'],
      ['dot possible', 'Uncertain (possible)'],
    ];
    return shared.map(([cls, label]) => `<span class="legend-item"><i class="${cls}"></i>${label}</span>`).join('');
  }

  function updateLegend() {
    legend.innerHTML = mode === 'year'
      ? `<strong>Status in ${yearInput.value}</strong>${legendHTML()}`
      : `<strong>Status across ${loInput.value}–${hiInput.value}</strong>${legendHTML()}`;
  }

  function emit() {
    if (mode === 'year') {
      readout.textContent = yearInput.value;
      onChange({ mode: 'year', year: Number(yearInput.value) });
    } else {
      if (Number(loInput.value) > Number(hiInput.value)) hiInput.value = loInput.value;
      readout.textContent = `${loInput.value} – ${hiInput.value}`;
      onChange({ mode: 'range', range: [Number(loInput.value), Number(hiInput.value)] });
    }
    updateLegend();
  }

  function setMode(next) {
    mode = next;
    yearBtn.classList.toggle('is-active', mode === 'year');
    rangeBtn.classList.toggle('is-active', mode === 'range');
    yearInput.classList.toggle('hidden', mode !== 'year');
    rangeWrap.classList.toggle('hidden', mode !== 'range');
    emit();
  }

  yearBtn.addEventListener('click', () => setMode('year'));
  rangeBtn.addEventListener('click', () => setMode('range'));
  yearInput.addEventListener('input', emit);
  loInput.addEventListener('input', emit);
  hiInput.addEventListener('input', emit);

  const PLAY_INTERVAL_MS = 900; // restrained: about one year per second
  function stopPlay() {
    playing = false;
    playBtn.textContent = '▶ Play';
    playBtn.setAttribute('aria-pressed', 'false');
    if (timer) clearInterval(timer);
    timer = null;
  }
  function startPlay() {
    playing = true;
    playBtn.textContent = '⏸ Pause';
    playBtn.setAttribute('aria-pressed', 'true');
    timer = setInterval(() => {
      if (mode === 'year') {
        const next = Number(yearInput.value) + 1;
        if (next > maxYear) { stopPlay(); return; }
        yearInput.value = String(next);
      } else {
        const span = Number(hiInput.value) - Number(loInput.value);
        const nextHi = Number(hiInput.value) + 1;
        if (nextHi > maxYear) { stopPlay(); return; }
        hiInput.value = String(nextHi);
        loInput.value = String(clamp(nextHi - span, minYear, maxYear));
      }
      emit();
    }, PLAY_INTERVAL_MS);
  }
  playBtn.addEventListener('click', () => (playing ? stopPlay() : startPlay()));

  updateLegend();
  // Deliberately no emit() here. Announcing the default year at construction
  // overwrote whatever the URL asked for, so a shared link carrying ?y= or ?r=
  // silently reset to the present. The caller seeds the timeline from the URL
  // and calls start() once, after that.

  return {
    /** Announce the current selection once, after the URL has been applied. */
    start() {
      emit();
    },
    setYear(year) {
      yearInput.value = String(clamp(year, minYear, maxYear));
      if (mode !== 'year') setMode('year'); else emit();
    },
    setRange(lo, hi) {
      loInput.value = String(clamp(lo, minYear, maxYear));
      hiInput.value = String(clamp(hi, minYear, maxYear));
      if (mode !== 'range') setMode('range'); else emit();
    },
    /** Reflects an externally-driven state (e.g. a restored URL, or another
     * subscriber reacting to state.navigate) into the slider UI *without*
     * re-emitting onChange — emitting here would re-call state.navigate and
     * loop forever between state.js and this module. */
    syncFromState({ year, range }) {
      // Which timeline mode to show follows from what the URL carries. The
      // caller's `mode` is the view mode ("collab"), not this one, so reading
      // it here silently dropped every shared range.
      if (range) {
        loInput.value = String(clamp(range[0], minYear, maxYear));
        hiInput.value = String(clamp(range[1], minYear, maxYear));
        mode = 'range';
      } else if (year != null) {
        yearInput.value = String(clamp(year, minYear, maxYear));
        mode = 'year';
      } else {
        return;
      }
      yearBtn.classList.toggle('is-active', mode === 'year');
      rangeBtn.classList.toggle('is-active', mode === 'range');
      yearInput.classList.toggle('hidden', mode !== 'year');
      rangeWrap.classList.toggle('hidden', mode !== 'range');
      readout.textContent = mode === 'year' ? yearInput.value : `${loInput.value} – ${hiInput.value}`;
      updateLegend();
    },
    getState() {
      return mode === 'year'
        ? { mode: 'year', year: Number(yearInput.value) }
        : { mode: 'range', range: [Number(loInput.value), Number(hiInput.value)] };
    },
    destroy() { stopPlay(); },
  };
}
