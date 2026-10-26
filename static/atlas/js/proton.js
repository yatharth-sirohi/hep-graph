// proton.js — "Follow the proton": a player on a facility's to-scale local map that
// walks the injector chain of the selected year, stage by stage, on the geometry the
// map already holds (docs/HEP_ATLAS_TEACHING_PLAN.md, workstream 2).
//
// localmap.js loads this module only when a map is opened, and creates one player per
// map instance (createPlayer). The player owns:
//   * a control on the map ("Follow the proton"), and a card on the stage with the
//     transport (previous, play/pause, next), the stage's name, its energy in -> out
//     and where each number comes from;
//   * an overlay of the lit stages (a Leaflet pane above the map's own features, never
//     replacing them) and a dot that runs once round the stage's ring, or along its
//     line, when the Atlas draws one;
//   * the "energy ladder" in the layers column: every stage of the chain on a log scale,
//     each name opening the accelerator's record, each bar jumping to that step.
//
// What it refuses to do (principle 1, "every mark is traceable"):
//   * it never draws a path the bundle does not hold. A stage drawn only as a building
//     footprint is lit, and says the beam line inside it is not drawn; a stage with no
//     geometry is named, with the map's own reason; a transfer between two drawn stages
//     is a step of its own with no line;
//   * the dot is a marker, not a measurement: it says nothing about speed or about how
//     many turns a real beam makes, and the method note says so;
//   * the step is in the URL (`?proton=N`, state.js) and is the only thing that is.
//
// The chain itself (order, year, energies) is proton-chain.js: pure, and unit-checked.

import { statusStyle, typeStyle, accuracyText } from './mapstyle.js';
import { fmtDate } from './model.js';
import * as loader from './loader.js';
import * as provenance from './provenance.js';
import {
  WORKING_TITLE, titleForSpecies, chainAt, yearsWithChain, ladderRows, tickLabel, speciesOf, speciesWord, rangeGeV,
} from './proton-chain.js';

const CSS_HREF = '/atlas/proton.css';
const DOT_MS_RING = 4200;
const DOT_MS_LINE = 3000;
const DWELL_MS = { stage: 3500, transfer: 5500, undrawn: 6000, still: 6500 };

let cssPromise = null;
/** proton.css is loaded with the player, not with the page (nothing new loads until asked). */
export function ensureStyles() {
  if (cssPromise) return cssPromise;
  cssPromise = new Promise((resolve) => {
    const existing = document.querySelector(`link[href="${CSS_HREF}"]`);
    if (existing) { resolve(); return; }
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = CSS_HREF;
    link.onload = () => resolve();
    link.onerror = () => resolve(); // unstyled is better than absent: the card is plain HTML
    document.head.appendChild(link);
  });
  return cssPromise;
}

let sourcesPromise = null;
/** provenance.json and sources.json: loaded the first time a number's source is shown. */
function ensureSources() {
  if (!sourcesPromise) {
    sourcesPromise = Promise.all([loader.getProvenance(), loader.getSources()])
      .then(([prov, sources]) => ({ prov, sources }))
      .catch((error) => { sourcesPromise = null; throw error; });
  }
  return sourcesPromise;
}

function h(tag, attrs = {}, children = []) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (k === 'class') el.className = v;
    else if (k === 'text') el.textContent = v;
    else if (v !== null && v !== undefined && v !== false) el.setAttribute(k, v === true ? '' : v);
  }
  for (const child of [].concat(children)) {
    if (child == null || child === false) continue;
    el.appendChild((typeof child === 'string' || typeof child === 'number') ? document.createTextNode(String(child)) : child);
  }
  return el;
}

const ICONS = {
  play: '<path d="M4 2.5v11l9.5-5.5z" fill="currentColor"/>',
  pause: '<path d="M4 2.5h3v11H4zM9 2.5h3v11H9z" fill="currentColor"/>',
  prev: '<path d="M12.5 2.5v11L4 8z" fill="currentColor"/><path d="M2.5 2.5h1.8v11H2.5z" fill="currentColor"/>',
  next: '<path d="M3.5 2.5v11L12 8z" fill="currentColor"/><path d="M11.7 2.5h1.8v11h-1.8z" fill="currentColor"/>',
  close: '<path d="M3.5 3.5l9 9M12.5 3.5l-9 9" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
  proton: '<circle cx="8" cy="8" r="5.6" fill="none" stroke="currentColor" stroke-width="1.6"/><circle cx="12.3" cy="4.8" r="2.1" fill="currentColor"/>',
};

function icon(name) {
  const span = h('span', { class: 'pr-icon', 'aria-hidden': 'true' });
  span.innerHTML = `<svg viewBox="0 0 16 16" width="16" height="16" focusable="false">${ICONS[name]}</svg>`;
  return span;
}

function reducedMotion() {
  return typeof window.matchMedia === 'function' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

function routeOf(id) {
  const [type, slug] = String(id).split(/:(.+)/);
  return { type, slug };
}

/** The shortest of a record's names that is still a name: "PSB", "Linac4", "NuMI beamline". */
export function shortName(record) {
  const names = [record.name, ...(record.aliases || [])]
    .map((name) => String(name).replace(/\s*\([^)]*\)/g, '').trim())
    .filter((name) => name.length >= 2)
    .sort((a, b) => a.length - b.length);
  return names[0] || record.name;
}

const sigFig = (value) => {
  if (value >= 100) return String(Math.round(value));
  if (value >= 10) return String(Math.round(value * 10) / 10);
  return String(Math.round(value * 100) / 100);
};

/** The date range a link is recorded for, in words. */
function linkDatesText(link) {
  if (!link || link.kind === 'beamline') return 'while the beamline was in operation';
  const start = link.start != null ? fmtDate(link.start) : '';
  const end = link.end != null ? fmtDate(link.end) : '';
  if (start && end) return `${start} to ${end}`;
  if (start) return `since ${start}`;
  if (end) return `until ${end}`;
  return 'for the whole life of both machines (the Atlas default when a link carries no dates)';
}

// --------------------------------------------------------------------- the player
export function createPlayer(host) {
  const { L, atlas, mapMeta, bundle } = host;
  const facility = (atlas.facilities || {})[mapMeta.facility_id];
  const facilityName = facility ? facility.name : mapMeta.name;

  const years = yearsWithChain(atlas, mapMeta.facility_id, bundle, 1931, 2026);
  const available = years.length > 0;

  let attached = false;
  let open = false;
  let playing = false;
  let step = 0;
  let chain = null;
  let chainYear = null;
  let pending;
  let phase = 'idle'; // 'camera' | 'dot' | 'dwell' | 'idle'
  let dwellTimer = 0;
  let cameraTimer = 0;
  let raf = 0;
  let dot = null;
  let overlay = null; // { renderer, pane, done, current, dot, trail }
  let controlButton = null;
  let sectionEl = null;
  let card = null;
  let status = null;
  let lastSig = '';
  let slotsRun = 0;

  // ------------------------------------------------------------------ the year
  function yearInfo() {
    const state = host.getTimeline();
    if (state.range) return { year: state.range[1], note: `${state.range[0]}–${state.range[1]} is selected; showing ${state.range[1]}, the end of the range` };
    const year = state.year != null ? state.year : Number(String(atlas.build_date || '').slice(0, 4)) || 2026;
    return { year, note: null };
  }

  function currentChain() {
    const { year } = yearInfo();
    if (!chain || chainYear !== year) {
      chain = chainAt(atlas, mapMeta.facility_id, year, bundle);
      chainYear = year;
    }
    return chain;
  }

  function nearestYears(year) {
    const earlier = [...years].reverse().find((y) => y < year);
    const later = years.find((y) => y > year);
    return [earlier, later].filter((y) => y != null);
  }

  function title() {
    return titleForSpecies(currentChain().species || 'proton');
  }

  // ------------------------------------------------------------- the stage text
  function energyText(spec, year) {
    if (!spec) return null;
    const q = spec.quantity;
    const text = q.display || `${q.value} ${q.unit}`;
    let note = '';
    if (spec.origin === 'interval' && spec.label) note = ` (${spec.label})`;
    else if (spec.eraGap) note = ` (the record's design or current value: no run is recorded in ${year})`;
    return { text, note };
  }

  function next(stageId) {
    return chain.stages.find((s) => s.feederId === stageId) || null;
  }

  function speciesLine(stage) {
    const record = stage.record;
    const sp = speciesOf(record);
    if (record.type === 'beamline') return `${chain.species === 'lepton' ? 'Electrons and positrons' : 'Protons'} on the target`;
    if (sp.hminus) {
      const after = next(stage.id);
      const afterSp = after ? speciesOf(after.record) : null;
      const note = after && afterSp && !afterSp.hminus
        ? ` They become protons when the electrons are stripped off at injection into ${shortName(after.record)}.` : '';
      return `H⁻ ions: hydrogen atoms carrying one extra electron.${note}`;
    }
    return titleCaseFirst(speciesWord(chain.species));
  }

  function titleCaseFirst(text) {
    return text.charAt(0).toUpperCase() + text.slice(1);
  }

  function geometryLine(stage) {
    const g = stage.geometry;
    if (!g.drawn) return null;
    const lead = g.pathFeature || g.features[0];
    const more = g.features.length > 1 ? ` and ${g.features.length - 1} more shape${g.features.length > 2 ? 's' : ''}` : '';
    const first = `Drawn on this map: ${lead.name}${more} (${typeStyle(lead.feature_type).label.toLowerCase()}) · ${accuracyText(lead)}.`;
    if (g.path) {
      const partial = g.pathFeature.geometry.type === 'MultiLineString';
      return `${first} The dot runs ${partial ? 'along the traced parts of it' : 'along it'} once${g.pathNote ? `: ${g.pathNote}` : ''}.`;
    }
    return `${first} No dot runs: ${g.pathNote || 'the Atlas draws no path for the beam here'}.`;
  }

  function notDrawnReason(stage) {
    const row = ((bundle.map || {}).unlocated || []).find((u) => u.entity_id === stage.id);
    if (row) return host.plainReason(row.reason, shortName(stage.record));
    return `The Atlas holds no geometry for ${shortName(stage.record)} on this map, so it is named here and not drawn.`;
  }

  // -------------------------------------------------------------- source links
  /** A slot a source link is poured into once provenance.json has arrived. */
  function sourceSlot(entityId, pointer) {
    return h('span', { class: 'pr-src', 'data-entity': entityId, 'data-pointer': pointer });
  }

  async function fillSources(root) {
    const slots = root.querySelectorAll('.pr-src, .pr-claims');
    if (!slots.length) return;
    const run = ++slotsRun;
    let data;
    try {
      data = await ensureSources();
    } catch (error) {
      if (run !== slotsRun) return;
      for (const el of root.querySelectorAll('.pr-src')) el.textContent = 'source unavailable';
      const claims = root.querySelector('.pr-claims');
      if (claims) {
        const retry = h('button', { type: 'button', class: 'text-btn' }, 'Retry');
        retry.addEventListener('click', () => { claims.textContent = 'Loading the sources…'; fillSources(root); });
        claims.replaceChildren(h('p', { class: 'error-note', role: 'alert' }, `Could not load the sources: ${error.message}. `), retry);
      }
      return;
    }
    if (run !== slotsRun) return;
    const { prov, sources } = data;
    for (const el of root.querySelectorAll('.pr-src')) {
      const entry = ((prov[el.dataset.entity] || {})[el.dataset.pointer]) || null;
      const src = entry ? (entry.sources || []).map((id) => sources.byId[id]).find((s) => s && s.url) : null;
      if (!src) { el.textContent = 'no source recorded'; continue; }
      const title = String(src.title || src.id).replace(/\s*\(.*$/, '');
      const link = h('a', { href: src.url, target: '_blank', rel: 'noopener', class: 'pr-src-link' }, `source: ${title.length > 46 ? `${title.slice(0, 45).trimEnd()}…` : title}`);
      el.replaceChildren(link);
    }
    const claims = root.querySelector('.pr-claims');
    if (claims) {
      const groups = JSON.parse(claims.dataset.groups || '[]');
      const blocks = groups.map((group) => {
        const record = host.index.get(group.entity);
        const picked = {};
        for (const pointer of group.pointers) if ((prov[group.entity] || {})[pointer]) picked[pointer] = prov[group.entity][pointer];
        const items = provenance.renderClaimItems(picked, sources, record);
        return h('div', { class: 'pr-claim-block' }, [
          h('h4', {}, record ? record.name : group.entity),
          items.length ? h('ul', { class: 'source-list' }, items) : h('p', { class: 'empty-note' }, 'No source is recorded for these values.'),
        ]);
      });
      claims.replaceChildren(...blocks);
    }
  }

  function claimsDisclosure(groups) {
    const filled = groups.filter((g) => g.pointers.length);
    if (!filled.length) return null;
    const body = h('div', { class: 'pr-claims', 'data-groups': JSON.stringify(filled) }, 'Loading the sources…');
    return h('details', { class: 'pr-sources' }, [h('summary', {}, 'Sources and quotes'), body]);
  }

  // ----------------------------------------------------------------- the card
  function energyRow(label, spec, entityId, year) {
    const e = energyText(spec, year);
    return h('div', { class: 'pr-energy-cell' }, [
      h('dt', {}, label),
      h('dd', {}, e ? [h('span', { class: 'pr-energy-value' }, e.text), e.note ? h('span', { class: 'pr-energy-note' }, e.note) : null, sourceSlot(entityId, spec.pointer)]
        : h('span', { class: 'pr-energy-none' }, 'not recorded in the Atlas')),
    ]);
  }

  function recordLink(record, text) {
    const route = routeOf(record.id);
    const a = h('a', { class: 'entity-link', href: `#/${route.type}/${route.slug}` }, text || 'Open the record');
    a.addEventListener('click', (event) => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      host.navigate({ entity: route });
    });
    return a;
  }

  function statusChip(stage, year) {
    if (!stage.status) return null;
    const label = statusStyle(stage.status).label;
    const approx = stage.certainty === 'possible' ? ' (dates for this year are approximate)' : '';
    return h('span', { class: `status-badge status-${stage.status}` }, `${label} in ${year}${approx}`);
  }

  function alsoLines(stage) {
    const lines = [];
    const feeds = stage.alsoFeeds.map((a) => `${shortName(atlas.accelerators[a.id] || atlas.beamlines[a.id] || { name: a.name })} (${a.why})`);
    if (feeds.length) lines.push(['Also fed from here', feeds.join('; ')]);
    const fed = stage.alsoFedBy.map((a) => shortName(atlas.accelerators[a.id] || { name: a.name }));
    if (fed.length) lines.push(['Also receives beam from', fed.join('; ')]);
    return lines.length
      ? h('dl', { class: 'pr-also' }, lines.flatMap(([k, v]) => [h('dt', {}, k), h('dd', {}, v)])) : null;
  }

  function stageContent(item, year) {
    const { stage } = item;
    const e = stage.energies;
    const kind = !stage.drawn ? 'Not drawn on this map' : `Stage ${item.stageNumber} of ${chain.stages.length}`;
    const groups = [];
    const pointers = [];
    if (e.energyOut) pointers.push(e.energyOut.pointer);
    if (e.energyIn) pointers.push(e.energyIn.pointer);
    groups.push({ entity: stage.id, pointers });
    const branch = stage.role === 'branch' && stage.feederId
      ? h('p', { class: 'pr-branch' }, `A branch: it is fed from ${shortName(atlas.accelerators[stage.feederId] || atlas.beamlines[stage.feederId])}, not from the stage before it in this list.`) : null;
    const energies = stage.type === 'beamline'
      ? [energyRow('Protons on the target', e.energyOut, stage.id, year)]
      : [energyRow('Energy in', e.energyIn, stage.id, year), energyRow('Energy out', e.energyOut, stage.id, year)];
    return [
      h('p', { class: 'pr-kind' }, kind),
      h('h3', { class: 'pr-stage-name', id: 'pr-stage-name' }, stage.record.name),
      h('p', { class: 'pr-chips' }, [statusChip(stage, year), ' ', recordLink(stage.record)]),
      branch,
      h('dl', { class: 'pr-energies' }, energies),
      h('p', { class: 'pr-species' }, [h('strong', {}, 'Beam: '), speciesLine(stage)]),
      stage.drawn
        ? h('p', { class: 'pr-geom' }, geometryLine(stage))
        : h('p', { class: 'pr-geom pr-notdrawn' }, [h('strong', {}, 'Not drawn on this map. '), notDrawnReason(stage)]),
      alsoLines(stage),
      claimsDisclosure(groups),
    ];
  }

  function transferContent(item, year) {
    const { from, to, link } = item;
    // Into a beamline the beam arrives at the beamline's own proton energy (a Main Injector
    // that is also a Tevatron injector still sends 120 GeV down NuMI); between two
    // machines it leaves the first at its output and enters the second at its input.
    const intoBeamline = to.type === 'beamline';
    const out = intoBeamline ? to.energies.energyOut : from.energies.energyOut;
    const inn = intoBeamline ? null : to.energies.energyIn;
    const outGeV = out ? rangeGeV(out.quantity) : null;
    const inGeV = inn ? rangeGeV(inn.quantity) : null;
    const same = intoBeamline || (out && inn && outGeV && inGeV && Math.abs(outGeV.hi - inGeV.hi) < 1e-9);
    const outOwner = intoBeamline ? to.id : from.id;
    const rows = same
      ? [energyRow('Handed over at', out, outOwner, year)]
      : [energyRow(`Leaves ${shortName(from.record)} at`, out, from.id, year), energyRow(`Arrives in ${shortName(to.record)} at`, inn, to.id, year)];
    const groups = [{ entity: outOwner, pointers: out ? [out.pointer] : [] }];
    if (link && link.pointer) groups.push({ entity: from.id, pointers: [link.pointer] });
    if (inn && !same) groups.push({ entity: to.id, pointers: [inn.pointer] });
    const fromHminus = speciesOf(from.record).hminus;
    const toHminus = speciesOf(to.record).hminus;
    return [
      h('p', { class: 'pr-kind' }, 'Transfer'),
      h('h3', { class: 'pr-stage-name', id: 'pr-stage-name' }, `${shortName(from.record)} → ${shortName(to.record)}`),
      h('dl', { class: 'pr-energies' }, rows),
      fromHminus && !toHminus
        ? h('p', { class: 'pr-species' }, [h('strong', {}, 'Beam: '), 'H⁻ ions become protons here, when the electrons are stripped off at injection.']) : null,
      h('p', { class: 'pr-geom pr-notdrawn' }, [
        h('strong', {}, 'No line is drawn. '),
        `The Atlas has no sourced coordinates for the transfer line that joins ${from.record.name} to ${to.record.name}, so the map shows both and nothing between them.`,
      ]),
      h('p', { class: 'pr-key' }, 'On the map the solid outline is the machine the beam leaves; the dotted outline is the one it enters.'),
      h('p', { class: 'pr-link-dates' }, [h('strong', {}, 'Recorded: '), `${from.record.name} feeds ${to.record.name} ${linkDatesText(link)}.`]),
      claimsDisclosure(groups),
    ];
  }

  function emptyContent(info) {
    const near = nearestYears(info.year);
    const wrap = h('div', { class: 'pr-empty' }, [
      h('p', { class: 'pr-kind' }, 'No chain in this year'),
      h('h3', { class: 'pr-stage-name', id: 'pr-stage-name' }, `No injector chain with two drawn stages is recorded for ${info.year}`),
      h('p', {}, 'That is a statement about the Atlas’s records, not about the laboratory: an earlier or later year may have one.'),
    ]);
    if (near.length) {
      wrap.appendChild(h('p', { class: 'pr-empty-years' }, near.map((y) => {
        const button = h('button', { type: 'button', class: 'text-btn pr-year-btn' }, `Show ${y}`);
        button.addEventListener('click', () => host.navigate({ year: y, range: null }));
        return button;
      })));
    }
    return [wrap];
  }

  function buildCard() {
    const closeBtn = h('button', { type: 'button', class: 'pr-close', 'aria-label': 'Close the player' }, icon('close'));
    closeBtn.addEventListener('click', () => host.navigate({ proton: null }));
    const heading = h('h2', { class: 'pr-title', id: 'pr-title', tabindex: '-1' });
    const context = h('p', { class: 'pr-context' });
    const head = h('div', { class: 'pr-head' }, [h('div', { class: 'pr-titles' }, [heading, context]), closeBtn]);

    const prev = h('button', { type: 'button', class: 'pr-btn pr-prev' }, [icon('prev'), h('span', {}, 'Previous')]);
    const play = h('button', { type: 'button', class: 'pr-btn pr-play' }, [icon('play'), h('span', {}, 'Play')]);
    const nextBtn = h('button', { type: 'button', class: 'pr-btn pr-next' }, [h('span', {}, 'Next'), icon('next')]);
    prev.addEventListener('click', () => go(step - 1));
    nextBtn.addEventListener('click', () => go(step + 1));
    play.addEventListener('click', togglePlay);
    const transport = h('div', { class: 'pr-transport', role: 'group', 'aria-label': 'Steps' }, [prev, play, nextBtn]);
    const progress = h('div', { class: 'pr-progress' });
    const counter = h('p', { class: 'pr-counter', id: 'pr-counter' });
    const content = h('div', { class: 'pr-content' });
    const hint = h('p', { class: 'pr-hint' }, 'Left and right arrow keys step; Escape closes. The dot is a marker for where the stage lies, not a measurement of the beam.');
    const method = h('details', { class: 'pr-method' }, [
      h('summary', {}, 'How this is worked out'),
      h('p', {}, [h('strong', {}, 'Which machines, in what order. '),
        'Every accelerator of this laboratory that the Atlas records as active, commissioning, upgrading or in a long shutdown in July of the selected year, joined by the dated “feeds” links that hold that year (a link with no dates holds for the life of both machines). The chain is the longest run of links that carries the same particle. A beamline joins it only where this map draws it; other machines a stage also feeds are named under it. Nothing is written down in advance: change the year and the chain changes.']),
      h('p', {}, [h('strong', {}, 'Energies. '),
        'For each stage, the value in the era or run of its record that covers the year (the latest-starting one), otherwise the record’s own value (ontology amendment A30). “Energy in” is the energy at which the machine receives beam.']),
      h('p', {}, [h('strong', {}, 'The map. '),
        'Only geometry in the Atlas’s own map record is lit. A transfer line, a beam line inside a building footprint and an inferred direction are never drawn. The dot runs once along a ring or line when there is one; it marks where the stage lies, not how fast the beam goes, and a real beam makes many thousands of turns.']),
    ]);
    status = h('p', { class: 'visually-hidden', role: 'status', 'aria-live': 'polite', id: 'pr-status' });
    card = h('section', { class: 'pr-card hidden', id: 'pr-card', 'aria-labelledby': 'pr-title' }, [head, transport, counter, progress, content, method, hint, status]);
    card.addEventListener('keydown', onCardKey);
    card._parts = { heading, context, prev, play, nextBtn, progress, counter, content };
    host.stage.appendChild(card);
  }

  function onCardKey(event) {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    const tag = event.target && event.target.tagName;
    if (tag === 'SUMMARY' || tag === 'A') {
      if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    }
    if (event.key === 'ArrowRight') { event.preventDefault(); go(step + 1); }
    else if (event.key === 'ArrowLeft') { event.preventDefault(); go(step - 1); }
    else if (event.key === 'Home') { event.preventDefault(); go(1); }
    else if (event.key === 'End') { event.preventDefault(); go(chain.steps.length); }
  }

  function renderCard() {
    const parts = card._parts;
    const info = yearInfo();
    const c = currentChain();
    parts.heading.textContent = title();
    parts.context.textContent = `${facilityName} · ${info.year}${info.note ? ` — ${info.note}` : ''}`;
    const total = c.steps.length;
    // aria-disabled, not disabled: pressing Next on the last step must not drop the
    // keyboard reader's focus into the page.
    const off = (button, value) => (value ? button.setAttribute('aria-disabled', 'true') : button.removeAttribute('aria-disabled'));
    off(parts.prev, !total || step <= 1);
    off(parts.nextBtn, !total || step >= total);
    off(parts.play, !total);
    const atEnd = total && step >= total;
    parts.play.replaceChildren(icon(playing ? 'pause' : 'play'), h('span', {}, playing ? 'Pause' : (atEnd ? 'Play again' : 'Play')));
    parts.progress.replaceChildren();
    if (!total) {
      parts.counter.textContent = '';
      parts.content.replaceChildren(...emptyContent(info).filter(Boolean));
      return;
    }
    const item = c.steps[step - 1];
    const stageCount = c.stages.length;
    parts.counter.textContent = item.kind === 'stage'
      ? `Step ${step} of ${total} · stage ${item.stageNumber} of ${stageCount}`
      : `Step ${step} of ${total} · between stages`;
    for (const s of c.steps) {
      const seg = h('span', { class: `pr-seg is-${s.kind}${s.index === step ? ' is-current' : ''}${s.index < step ? ' is-done' : ''}${s.kind === 'stage' && !s.stage.drawn ? ' is-undrawn' : ''}` });
      parts.progress.appendChild(seg);
    }
    parts.progress.setAttribute('role', 'img');
    parts.progress.setAttribute('aria-label', `Step ${step} of ${total}`);
    const nodes = item.kind === 'stage' ? stageContent(item, info.year) : transferContent(item, info.year);
    parts.content.replaceChildren(...nodes.filter(Boolean));
    fillSources(parts.content);
  }

  // ---------------------------------------------------------------- the ladder
  function rungText(row) {
    const e = row.step.stage.energies;
    const out = e.energyOut && e.energyOut.quantity;
    const inn = e.energyIn && e.energyIn.quantity;
    const text = (q) => (q ? (q.display || '') : '');
    if (row.step.stage.type === 'beamline') return `${text(out)} on target`;
    if (inn && out) return `${text(inn)} → ${text(out)}`;
    return out ? `→ ${text(out)}` : 'energy not recorded';
  }

  function ladderEl() {
    const c = currentChain();
    const info = yearInfo();
    if (!c.steps.length) return null;
    const { rows, lo, hi } = ladderRows(c);
    const span = hi - lo;
    const pos = (v) => ((Math.log10(v) - lo) / span) * 100;
    const list = h('ol', { class: 'pr-ladder', style: `--pr-decades: ${span}`, 'aria-label': `Energy ladder for ${info.year}, log scale` });
    for (const row of rows) {
      const { stage } = row.step;
      const current = open && row.step.index === step;
      const bar = h('span', { class: 'pr-bar-track' });
      const values = [row.inGeV, row.outGeV, row.inLo, row.outLo].filter((v) => v != null && v > 0);
      if (values.length) {
        const left = pos(Math.min(...values));
        const right = pos(Math.max(...values));
        if (right - left > 0.6 && (row.inGeV != null || row.outLo != null)) {
          bar.appendChild(h('span', { class: `pr-bar${stage.drawn ? '' : ' is-undrawn'}`, style: `left:${left.toFixed(2)}%;width:${(right - left).toFixed(2)}%` }));
        } else {
          bar.appendChild(h('span', { class: `pr-pin${stage.drawn ? '' : ' is-undrawn'}`, style: `left:${right.toFixed(2)}%` }));
        }
      }
      const go1 = h('button', {
        type: 'button', class: 'pr-bar-btn',
        'aria-label': `Step ${row.step.index}: ${stage.record.name}, ${rungText(row)}${stage.drawn ? '' : ', not drawn on this map'}. Show it on the map.`,
      }, bar);
      go1.addEventListener('click', () => openAt(row.step.index));
      const item = h('li', { class: `pr-rung${current ? ' is-current' : ''}${stage.role === 'branch' ? ' is-branch' : ''}`, 'aria-current': current ? 'step' : null }, [
        h('div', { class: 'pr-rung-head' }, [
          h('span', { class: 'pr-rung-no', 'aria-hidden': 'true' }, String(row.step.stageNumber)),
          recordLink(stage.record, shortName(stage.record)),
          h('span', { class: 'pr-rung-energy' }, rungText(row)),
        ]),
        go1,
        stage.drawn ? null : h('span', { class: 'pr-rung-flag' }, 'not drawn on this map'),
      ]);
      list.appendChild(item);
    }
    const ticks = [];
    // Six decades do not fit six labels in a narrow column: every second decade is named.
    const every = span > 4 ? 2 : 1;
    for (let i = lo; i <= hi; i += every) {
      ticks.push(h('span', { class: `pr-tick${i === lo ? ' is-first' : ''}${i === hi ? ' is-last' : ''}`, style: `left:${(((i - lo) / span) * 100).toFixed(2)}%` }, tickLabel(i)));
    }
    return h('div', { class: 'pr-ladder-wrap' }, [list, h('div', { class: 'pr-axis', 'aria-hidden': 'true' }, ticks)]);
  }

  function paintLadder() {
    if (!sectionEl) return;
    const slot = sectionEl.querySelector('.pr-ladder-slot');
    if (slot) slot.replaceChildren(...[ladderEl()].filter(Boolean));
  }

  /** The "Follow the proton" section of the layers column: what it is, the button, the ladder. */
  function renderSection() {
    const info = yearInfo();
    const c = currentChain();
    const names = titleForSpecies(c.species || 'proton');
    const button = h('button', {
      type: 'button', class: 'map-toggle pr-start', 'aria-pressed': open ? 'true' : 'false',
    }, [
      h('span', { class: 'map-toggle-name' }, names),
      h('span', { class: 'map-toggle-meta' }, c.steps.length
        ? `${c.stages.length} stages in ${info.year}: ${c.stages.map((s) => shortName(s.record)).slice(0, 6).join(' → ')}${c.stages.length > 6 ? ' …' : ''}`
        : `no chain with two drawn stages in ${info.year}`),
    ]);
    button.addEventListener('click', () => (open ? host.navigate({ proton: null }) : openAt(1)));
    const details = h('details', { class: 'map-section pr-section', open: true }, [
      h('summary', {}, names),
      h('div', { class: 'map-section-body' }, [
        h('p', { class: 'map-note' }, 'Walk the beam through this laboratory’s accelerator chain, one stage at a time, with its energy at each step. The order and every number come from the Atlas’s accelerator records for the year selected on the timeline.'),
        button,
        h('div', { class: 'pr-ladder-slot' }),
        c.steps.length ? h('p', { class: 'map-note' }, 'Energy ladder: each bar spans the energy a stage receives and delivers, on a logarithmic axis. A name opens its record; a bar shows that step on the map.') : null,
      ]),
    ]);
    sectionEl = details;
    paintLadder();
    return details;
  }

  // ------------------------------------------------------------------- overlay
  function ensureOverlay() {
    if (overlay) return overlay;
    const map = host.map();
    if (!map.getPane('protonPane')) {
      const pane = map.createPane('protonPane');
      pane.style.zIndex = 450;
      pane.style.pointerEvents = 'none';
    }
    overlay = {
      renderer: L.svg({ pane: 'protonPane', padding: 0.4 }),
      done: L.layerGroup().addTo(map),
      current: L.layerGroup().addTo(map),
      dot: L.layerGroup().addTo(map),
    };
    return overlay;
  }

  function featureLayers(stage, cls, weight) {
    const { renderer } = ensureOverlay();
    const layers = [];
    for (const f of stage.geometry.features) {
      const g = f.geometry;
      if (g.type === 'Point' || g.type === 'MultiPoint') {
        const points = g.type === 'Point' ? [g.coordinates] : g.coordinates;
        for (const [lon, lat] of points) {
          layers.push(L.circle([lat, lon], {
            renderer, pane: 'protonPane', radius: f.accuracy_m > 0 ? f.accuracy_m : 25, className: `${cls} pr-area`, weight: 2, interactive: false,
          }));
        }
        continue;
      }
      const isLine = g.type === 'LineString' || g.type === 'MultiLineString';
      layers.push(L.geoJSON(g, {
        renderer, pane: 'protonPane', className: `${cls} ${isLine ? 'pr-line' : 'pr-area'}`, interactive: false,
        style: () => ({ weight: isLine ? weight : 2, className: `${cls} ${isLine ? 'pr-line' : 'pr-area'}` }),
      }));
    }
    return layers;
  }

  function clearOverlay({ dotToo = true } = {}) {
    if (!overlay) return;
    overlay.done.clearLayers();
    overlay.current.clearLayers();
    if (dotToo) overlay.dot.clearLayers();
  }

  function paintOverlay(item) {
    const c = currentChain();
    ensureOverlay();
    clearOverlay();
    const stageOfStep = item.kind === 'stage' ? item.stage : null;
    const earlier = new Set();
    for (const s of c.steps) {
      if (s.index >= item.index) break;
      if (s.kind === 'stage' && s.stage.drawn) earlier.add(s.stage.id);
    }
    // A transfer shows the machine it leaves as done and the one it enters as next.
    for (const stage of c.stages) {
      if (earlier.has(stage.id)) featureLayers(stage, 'pr-done', 3).forEach((layer) => overlay.done.addLayer(layer));
    }
    if (stageOfStep && stageOfStep.drawn) {
      featureLayers(stageOfStep, 'pr-glow', 11).forEach((layer) => overlay.current.addLayer(layer));
      featureLayers(stageOfStep, 'pr-current', 5).forEach((layer) => overlay.current.addLayer(layer));
    } else if (item.kind === 'transfer') {
      featureLayers(item.from, 'pr-glow pr-from', 10).forEach((layer) => overlay.current.addLayer(layer));
      featureLayers(item.from, 'pr-current pr-from', 4).forEach((layer) => overlay.current.addLayer(layer));
      featureLayers(item.to, 'pr-glow pr-to', 10).forEach((layer) => overlay.current.addLayer(layer));
      featureLayers(item.to, 'pr-current pr-to', 4).forEach((layer) => overlay.current.addLayer(layer));
    }
  }

  function boundsOf(stages) {
    let bounds = null;
    for (const stage of stages) {
      for (const f of stage.geometry.features) {
        const b = L.geoJSON(f.geometry).getBounds();
        if (!b.isValid()) continue;
        bounds = bounds ? bounds.extend(b) : L.latLngBounds(b.getSouthWest(), b.getNorthEast());
      }
    }
    return bounds;
  }

  function cameraFor(item, { animate = !reducedMotion() } = {}) {
    const stages = item.kind === 'stage' ? (item.stage.drawn ? [item.stage] : []) : [item.from, item.to];
    const bounds = boundsOf(stages);
    if (!bounds) return false;
    host.cameraFit(bounds, { animate, card });
    return true;
  }

  // ---------------------------------------------------------------- the moving dot
  function pathPoints(parts) {
    const pts = [];
    const cum = [];
    let total = 0;
    parts.forEach((part) => {
      part.forEach((p, i) => {
        if (pts.length && i > 0) {
          const q = pts[pts.length - 1];
          const k = Math.PI / 180;
          const dy = (p[0] - q[0]) * k * 6371008.8;
          const dx = (p[1] - q[1]) * k * 6371008.8 * Math.cos(((p[0] + q[0]) / 2) * k);
          total += Math.hypot(dx, dy);
        }
        pts.push(p);
        cum.push(total);
      });
    });
    return { pts, cum, total };
  }

  function pointAt(path, fraction) {
    const target = path.total * fraction;
    let i = 1;
    while (i < path.cum.length - 1 && path.cum[i] < target) i += 1;
    const a = path.pts[i - 1];
    const b = path.pts[i];
    const span = path.cum[i] - path.cum[i - 1];
    const t = span > 0 ? Math.min(1, Math.max(0, (target - path.cum[i - 1]) / span)) : 0;
    return { latlng: [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t], index: i, t };
  }

  function stopMotion() {
    window.cancelAnimationFrame(raf);
    raf = 0;
    window.clearTimeout(dwellTimer);
    window.clearTimeout(cameraTimer);
    dwellTimer = 0;
    cameraTimer = 0;
  }

  function dwellFor(item) {
    if (reducedMotion()) return DWELL_MS.still;
    if (item.kind === 'transfer') return DWELL_MS.transfer;
    return item.stage.drawn ? DWELL_MS.stage : DWELL_MS.undrawn;
  }

  function startDwell() {
    window.clearTimeout(dwellTimer);
    phase = 'dwell';
    dwellTimer = window.setTimeout(advance, dwellFor(currentChain().steps[step - 1]));
  }

  function finishRun() {
    phase = 'idle';
    if (playing) startDwell();
  }

  function advance() {
    const total = currentChain().steps.length;
    if (step >= total) {
      playing = false;
      phase = 'idle';
      renderCard();
      return;
    }
    go(step + 1);
  }

  function startDot(item) {
    const o = ensureOverlay();
    o.dot.clearLayers();
    const path = item.kind === 'stage' && item.stage.drawn && item.stage.geometry.path ? pathPoints(item.stage.geometry.path) : null;
    if (!path || path.pts.length < 2 || reducedMotion()) { finishRun(); return; }
    const closed = item.stage.geometry.pathFeature.feature_type === 'ring';
    const duration = closed ? DOT_MS_RING : DOT_MS_LINE;
    const start = path.pts[0];
    const halo = L.circleMarker(start, { renderer: o.renderer, pane: 'protonPane', radius: 15, className: 'pr-dot-halo', interactive: false });
    const marker = L.circleMarker(start, { renderer: o.renderer, pane: 'protonPane', radius: 7, className: 'pr-dot', interactive: false });
    const trail = L.polyline([start, start], { renderer: o.renderer, pane: 'protonPane', className: 'pr-trail', weight: 6, interactive: false });
    o.dot.addLayer(trail);
    o.dot.addLayer(halo);
    o.dot.addLayer(marker);
    dot = { path, duration, progress: 0, last: 0, marker, halo, trail };
    phase = 'dot';
    runDot();
  }

  /** Advance the dot from where it is (a pause keeps `progress`). */
  function runDot() {
    if (!dot) return;
    dot.last = 0;
    const tick = (now) => {
      if (!dot) return;
      if (!dot.last) dot.last = now;
      dot.progress = Math.min(1, dot.progress + (now - dot.last) / dot.duration);
      dot.last = now;
      const at = pointAt(dot.path, dot.progress);
      dot.marker.setLatLng(at.latlng);
      dot.halo.setLatLng(at.latlng);
      dot.trail.setLatLngs([...dot.path.pts.slice(0, at.index), at.latlng]);
      if (dot.progress >= 1) { raf = 0; finishRun(); return; }
      raf = window.requestAnimationFrame(tick);
    };
    raf = window.requestAnimationFrame(tick);
  }

  // -------------------------------------------------------------- stepping
  function signatureOf(c, n) {
    const item = c.steps[n - 1];
    if (!item) return `none|${c.steps.length}`;
    const ids = item.kind === 'stage' ? item.stage.id : `${item.from.id}>${item.to.id}`;
    return `${n}|${item.kind}|${ids}|${c.steps.length}`;
  }

  function enterStep(n) {
    stopMotion();
    dot = null;
    step = n;
    const c = currentChain();
    renderCard();
    paintLadder();
    if (!c.steps.length) { clearOverlay(); phase = 'idle'; return; }
    const item = c.steps[step - 1];
    paintOverlay(item);
    const text = item.kind === 'stage'
      ? `Step ${step} of ${c.steps.length}: ${item.stage.record.name}${item.stage.drawn ? '' : ', not drawn on this map'}.`
      : `Step ${step} of ${c.steps.length}: transfer from ${item.from.record.name} to ${item.to.record.name}, no line drawn.`;
    status.textContent = '';
    window.setTimeout(() => { if (status) status.textContent = text; }, 30);
    lastSig = signatureOf(c, n);
    // Camera first, then the dot; a stage with nothing to show just waits.
    const moved = cameraFor(item);
    if (moved && !reducedMotion()) {
      phase = 'camera';
      const map = host.map();
      const begin = () => { window.clearTimeout(cameraTimer); map.off('moveend', begin); if (phase === 'camera' && step === n) startDot(item); };
      map.once('moveend', begin);
      cameraTimer = window.setTimeout(begin, 1800);
    } else {
      startDot(item);
    }
  }

  /** The reader's step: through the URL, which is the one source of truth. */
  function go(n) {
    const total = currentChain().steps.length;
    if (!total) return;
    const target = Math.max(1, Math.min(total, n));
    if (target === step) return;
    host.navigate({ proton: target }, { replace: true });
  }

  function openAt(n) {
    if (open) { go(n); return; }
    host.navigate({ proton: n });
  }

  function togglePlay() {
    const total = currentChain().steps.length;
    if (!total) return;
    if (playing) {
      playing = false;
      window.clearTimeout(dwellTimer);
      window.cancelAnimationFrame(raf);
      raf = 0;
      if (phase === 'dwell') phase = 'idle';
      renderCard();
      return;
    }
    playing = true;
    if (step >= total && phase !== 'dot') {
      renderCard();
      go(1);
      return;
    }
    renderCard();
    if (phase === 'dot') runDot();
    else if (phase === 'idle') startDwell();
  }

  function openUi() {
    open = true;
    card.classList.remove('hidden');
    host.stage.classList.add('proton-open');
    host.cameraSave();
    if (controlButton) controlButton.setAttribute('aria-pressed', 'true');
    ensureStyles();
    window.requestAnimationFrame(() => {
      const heading = card && card._parts.heading;
      if (heading && open) heading.focus({ preventScroll: true });
    });
  }

  function closeUi() {
    open = false;
    playing = false;
    stopMotion();
    dot = null;
    phase = 'idle';
    step = 0;
    clearOverlay();
    if (card) card.classList.add('hidden');
    host.stage.classList.remove('proton-open');
    if (controlButton) controlButton.setAttribute('aria-pressed', 'false');
    host.cameraRestore();
    paintLadder();
    if (sectionEl) {
      const start = sectionEl.querySelector('.pr-start');
      if (start) start.setAttribute('aria-pressed', 'false');
    }
    lastSig = '';
  }

  /** The URL's step: open, move or close the player to match. */
  function sync(n) {
    if (!attached) { pending = n; return; }
    if (n == null) {
      if (open) closeUi();
      return;
    }
    const c = currentChain();
    const total = c.steps.length;
    const target = total ? Math.max(1, Math.min(n, total)) : 1;
    const wasOpen = open;
    if (!wasOpen) openUi();
    if (total && target !== n) host.navigate({ proton: target }, { replace: true });
    // A year that changes the card's wording but not what the step is (same machines, same
    // place in the chain) is a new caption, not a new camera move and a new dot.
    if (!wasOpen || signatureOf(c, target) !== lastSig) enterStep(target);
    else { renderCard(); paintLadder(); }
    if (sectionEl) {
      const start = sectionEl.querySelector('.pr-start');
      if (start) start.setAttribute('aria-pressed', 'true');
    }
  }

  // ------------------------------------------------------------------- attach
  function addControl() {
    const map = host.map();
    const Control = L.Control.extend({
      options: { position: 'topleft' },
      onAdd() {
        const bar = L.DomUtil.create('div', 'leaflet-bar leaflet-control pr-control');
        controlButton = h('button', {
          type: 'button', class: 'pr-control-btn', id: 'proton-control', 'aria-pressed': open ? 'true' : 'false',
          title: `${WORKING_TITLE}: walk the beam through this laboratory's injector chain`,
        }, [icon('proton'), h('span', { class: 'pr-control-text' }, titleForSpecies('proton'))]);
        controlButton.addEventListener('click', () => (open ? host.navigate({ proton: null }) : openAt(1)));
        L.DomEvent.disableClickPropagation(bar);
        bar.appendChild(controlButton);
        return bar;
      },
    });
    new Control().addTo(map);
    // A map of electrons names itself so.
    window.requestAnimationFrame(() => {
      const text = controlButton && controlButton.querySelector('.pr-control-text');
      if (text) text.textContent = title();
    });
  }

  let resizeTimer = 0;
  function onResize() {
    // A stage that changed size (a sheet opening, a phone turning) moves the lit stage
    // from under the card: fit it again, without flying.
    if (!open || !chain || !chain.steps.length) return;
    window.clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(() => {
      if (!open || phase === 'camera') return;
      const item = currentChain().steps[step - 1];
      if (item) cameraFor(item, { animate: false });
    }, 180);
  }

  async function attach() {
    await ensureStyles();
    buildCard();
    if (available) addControl();
    host.map().on('resize', onResize);
    attached = true;
    if (pending !== undefined) { const n = pending; pending = undefined; sync(n); }
  }

  function detach() {
    stopMotion();
    window.clearTimeout(resizeTimer);
    attached = false;
    open = false;
    dot = null;
    slotsRun += 1;
    if (card) card.remove();
    card = null;
    overlay = null; // the map's own removal takes the layers with it
    host.stage.classList.remove('proton-open');
  }

  function closeFromEscape() {
    if (!open) return false;
    host.navigate({ proton: null });
    if (controlButton && document.body.contains(controlButton)) controlButton.focus({ preventScroll: true });
    return true;
  }

  return {
    available, attach, detach, sync, renderSection, closeFromEscape,
    isOpen: () => open,
    years: () => years,
  };
}
