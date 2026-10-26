// provenance.js — turns a provenance.json JSON pointer (`/intervals/1`,
// `/key_specs/0/quantity`, `/members/3`, …) into a human-readable claim
// label, and renders the Sources disclosure grouped by claim (one claim,
// then the sources that back it) instead of one row per (pointer, source).
//
// Every renderer's `sourcesDisclosure` (panels.js) goes through
// `renderClaimItems` so a fix here fixes every panel at once; the A23
// approximate-location note goes through `renderApproximateLocationNote` so
// it gets the same shape (a labelled claim, never a bespoke one-off row).

import { titleCase, fmtDate, quantityText } from './model.js';
import { quoteView } from './tex.js';

// A flat id -> record index (facilities/sites/accelerators/beamlines/
// experiments/detectors/collaborations/topics — the same one model.js's
// buildIndex() produces) so a placement/facility-role/lineage pointer can
// name the *other* entity it points at ("Point 5 cavern", not
// "site:demo-far-cavern"). Institutions aren't in it (they have their own
// bundle) — membership rows carry their own `name` already, so that path
// never needs the index.
let INDEX = null;

export function configure(index) {
  INDEX = index;
}

function h(tag, attrs = {}, children = []) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (k === 'class') el.className = v;
    else if (k === 'text') el.textContent = v;
    else if (v !== null && v !== undefined) el.setAttribute(k, v);
  }
  for (const child of [].concat(children)) {
    if (child == null) continue;
    el.appendChild((typeof child === 'string' || typeof child === 'number') ? document.createTextNode(String(child)) : child);
  }
  return el;
}

// RFC 6901: `~1` -> `/`, `~0` -> `~`.
function unescapeSegment(seg) {
  return seg.replace(/~1/g, '/').replace(/~0/g, '~');
}

function pointerSegments(pointer) {
  return String(pointer || '')
    .replace(/^\//, '')
    .split('/')
    .filter((s) => s !== '')
    .map(unescapeSegment);
}

// Walks `record` along `path` (a mix of object keys and array indices given
// as numeric strings), returning undefined rather than throwing on a path
// that doesn't resolve — a claim label must never itself become an error.
function getPath(record, path) {
  let cur = record;
  for (const seg of path) {
    if (cur == null) return undefined;
    const key = /^\d+$/.test(seg) ? Number(seg) : seg;
    cur = cur[key];
  }
  return cur;
}

// "<status-or-role>, <start> – <end>". An open end reads "since <start>" when
// the start is a date (and just the start text otherwise), never a dash with
// nothing after it ("active, 2013-09 – )"); an open start reads "until <end>".
function rangeText(statusOrRole, start, end) {
  const head = statusOrRole || 'unrecorded';
  const startText = start ? fmtDate(start) : '';
  const endText = end ? fmtDate(end) : '';
  if (startText && endText) return `${head}, ${startText} – ${endText}`;
  if (startText) return `${head}, ${/^\d{4}/.test(startText) ? 'since ' : ''}${startText}`;
  if (endText) return `${head}, until ${endText}`;
  return head;
}

function fallbackLabel(segs) {
  return segs.map((seg) => (/^\d+$/.test(seg) ? `#${Number(seg) + 1}` : titleCase(seg))).join(' ');
}

// -------------------------------------------------------------- claimLabel
// `record` is the entity's own atlas.json/results.json/documents.json record
// (whatever `sourcesDisclosure`'s caller is already showing); for a
// collaboration record it should additionally carry a `members` array
// indexed by each row's authored `source_index` (panels.js builds this from
// the loaded membership bundle) so `/members/N` resolves to the right
// institution rather than whatever the display-sorted roster put at N.
export function claimLabel(pointer, record) {
  const field = String(pointer || '');
  const segs = pointerSegments(field);
  const isResult = record && record.type === 'result';
  const val = (path) => getPath(record, path);

  if (!segs.length) return { label: 'Record', field };

  // A22: the record-level `sources` pointer covers identity claims (name,
  // aliases, kind, external ids, summary, links, topic_ids, country, place).
  if (segs.length === 1 && segs[0] === 'sources') {
    return { label: 'Core identity (name, kind, links)', field };
  }

  // /intervals/N, /intervals/N/start|end, /intervals/N/specs/<key>
  if (segs[0] === 'intervals' && /^\d+$/.test(segs[1] || '')) {
    const interval = val(['intervals', segs[1]]) || {};
    const base = interval.label || titleCase(interval.kind || 'interval');
    if (segs.length === 2) {
      return { label: `Timeline: ${base} (${rangeText(interval.status, interval.start, interval.end)})`, field };
    }
    if (segs.length === 3 && (segs[2] === 'start' || segs[2] === 'end')) {
      return { label: `Timeline: ${base} — ${titleCase(segs[2])} date`, field };
    }
    if (segs.length === 4 && segs[2] === 'specs') {
      const key = segs[3];
      const value = interval.specs && interval.specs[key];
      return { label: `Timeline (${base}): ${titleCase(key)}${value != null ? ` ${quantityText(value)}` : ''}`, field };
    }
    return { label: `Timeline: ${base}`, field };
  }

  // /specs/<key> — facility/beamline/detector technical specs.
  if (segs[0] === 'specs' && segs.length === 2) {
    const key = segs[1];
    const value = val(['specs', key]);
    return { label: `${titleCase(key)}: ${quantityText(value)}`, field };
  }

  // /key_specs/N or /key_specs/N/quantity — the experiment panel's own
  // labelled headline specs.
  if (segs[0] === 'key_specs' && /^\d+$/.test(segs[1] || '')) {
    const spec = val(['key_specs', segs[1]]) || {};
    return { label: `${spec.label || 'Key specification'}: ${quantityText(spec.quantity)}`, field };
  }

  // /coordinates
  if (segs.length === 1 && segs[0] === 'coordinates') {
    const c = record && record.coordinates;
    return { label: c ? `Location (lat ${c.lat}, lon ${c.lon})` : 'Location', field };
  }

  // /placements/N — A2: {site_id, role, start, end}.
  if (segs[0] === 'placements' && /^\d+$/.test(segs[1] || '')) {
    const placement = val(['placements', segs[1]]) || {};
    const site = placement.site_id && INDEX ? INDEX.get(placement.site_id) : null;
    const siteName = (site && site.name) || placement.site_id || 'unknown site';
    return { label: `Placement: ${siteName} (${rangeText(placement.role, placement.start, placement.end)})`, field };
  }

  // /facility_roles/N — A2: {facility_id, role}.
  if (segs[0] === 'facility_roles' && /^\d+$/.test(segs[1] || '')) {
    const role = val(['facility_roles', segs[1]]) || {};
    const facility = role.facility_id && INDEX ? INDEX.get(role.facility_id) : null;
    const suffix = facility ? ` at ${facility.name}` : '';
    return { label: `Facility role: ${titleCase(role.role || 'role')}${suffix}`, field };
  }

  // /members/N — A5 collaboration roster row. `record.members` is expected
  // pre-reordered to authored `source_index` order by the caller.
  if (segs[0] === 'members' && /^\d+$/.test(segs[1] || '')) {
    const member = val(['members', segs[1]]) || {};
    return { label: `Membership: ${member.name || member.institution_id || 'unknown institution'}`, field };
  }
  if (segs[0] === 'memberships' && /^\d+$/.test(segs[1] || '')) {
    return { label: `Membership record #${Number(segs[1]) + 1}`, field };
  }
  if (segs[0] === 'affiliations' && /^\d+$/.test(segs[1] || '')) {
    return { label: `Affiliation #${Number(segs[1]) + 1}`, field };
  }

  // Result-only top-level scalars.
  if (segs.length === 1 && segs[0] === 'claim') return { label: isResult ? 'Result claim' : 'Claim', field };
  if (segs.length === 1 && segs[0] === 'date') return { label: isResult ? 'Result date' : 'Date', field };
  if (segs.length === 1 && (segs[0] === 'published' || segs[0] === 'announced')) {
    return { label: `${titleCase(segs[0])} date`, field };
  }
  if (segs.length === 1 && segs[0] === 'significance') {
    const value = record && record.significance;
    return { label: value ? `Significance: ${value}` : 'Significance', field };
  }
  if (segs.length === 1 && (segs[0] === 'key_value' || segs[0] === 'key_value_text')) {
    const value = record && (record.key_value_text || quantityText(record.key_value));
    return { label: value ? `Key value: ${value}` : 'Key value', field };
  }
  if (segs.length === 1 && segs[0] === 'official_url') return { label: 'Official link', field };

  // /links/<key>
  if (segs[0] === 'links' && segs.length === 2) {
    const key = segs[1];
    if (key === 'website') return { label: 'Official website', field };
    return { label: `${titleCase(key)} link`, field };
  }

  // /summary/…
  if (segs[0] === 'summary') return { label: 'Summary', field };

  // /formation — collaboration formation date.
  if (segs.length === 1 && segs[0] === 'formation') {
    const value = record && record.formation;
    return { label: value ? `Formation: ${fmtDate(value)}` : 'Formation date', field };
  }

  // /membership/<stat> — headline roster counts on the collaboration record.
  if (segs[0] === 'membership' && segs.length === 2) {
    return { label: `Membership ${titleCase(segs[1])}`, field };
  }

  if (segs.length === 1 && (segs[0] === 'operator' || segs[0] === 'operator_text')) {
    return { label: 'Operator', field };
  }
  if (segs.length === 1 && segs[0] === 'energy_regime') return { label: 'Energy regime', field };

  // /lineage/N — predecessor/successor/related-programme row.
  if (segs[0] === 'lineage' && /^\d+$/.test(segs[1] || '')) {
    const rel = val(['lineage', segs[1]]) || {};
    const other = rel.experiment_id && INDEX ? INDEX.get(rel.experiment_id) : null;
    const otherName = (other && other.name) || rel.experiment_id || 'another experiment';
    return { label: `Lineage: ${titleCase((rel.relation || '').replace(/_/g, ' '))} — ${otherName}`, field };
  }

  // /leadership/N
  if (segs[0] === 'leadership' && /^\d+$/.test(segs[1] || '')) {
    const row = val(['leadership', segs[1]]) || {};
    return { label: `Leadership: ${titleCase(row.role || 'role')}`, field };
  }

  // /baselines/N, /baselines/N/distance — beamline baseline distance.
  if (segs[0] === 'baselines' && /^\d+$/.test(segs[1] || '')) {
    const baseline = val(['baselines', segs[1]]) || {};
    return { label: `Baseline distance: ${quantityText(baseline.distance)}`, field };
  }

  // Long-text SList fields (A9): the value itself lives in text.json, not on
  // this record, so the label names the item rather than quoting it.
  if (segs[0] === 'physics_goals' && /^\d+$/.test(segs[1] || '')) {
    return { label: `Physics goal #${Number(segs[1]) + 1}`, field };
  }
  if (segs[0] === 'unique_capabilities' && /^\d+$/.test(segs[1] || '')) {
    return { label: `Unique capability #${Number(segs[1]) + 1}`, field };
  }
  if (segs[0] === 'subsystems') {
    const idx = /^\d+$/.test(segs[1] || '') ? `#${Number(segs[1]) + 1} ` : '';
    return { label: `Subsystem ${idx}description`.trim(), field };
  }
  if (segs.length === 1 && segs[0] === 'technology') return { label: 'Technology', field };
  if (segs.length === 1 && segs[0] === 'why_it_matters') return { label: 'Why it matters', field };
  if (segs.length === 1 && segs[0] === 'identity_evidence') return { label: 'Identity evidence', field };

  if (segs.length === 1 && ['depth', 'depth_mwe', 'depth_rock', 'altitude'].includes(segs[0])) {
    return { label: titleCase(segs[0]), field };
  }
  if (segs.length === 1 && ['primary_beam', 'secondary_beam', 'target', 'direction'].includes(segs[0])) {
    return { label: titleCase(segs[0]), field };
  }
  if (segs[0] === 'roster_snapshots') return { label: 'Roster snapshot', field };
  if (segs.length === 1 && segs[0] === 'roster_sources') return { label: 'Roster sources', field };

  // Unknown pointer: a title-cased path, never the raw pointer text.
  return { label: fallbackLabel(segs), field };
}

// ---------------------------------------------------------------- wording
const CONFIDENCE_WORDS = {
  verified: 'verified',
  approximate: 'approximate',
  uncertain: 'uncertain',
  derived: 'derived (not independently sourced)',
};

export function confidenceWord(confidence) {
  if (!confidence) return null;
  return CONFIDENCE_WORDS[confidence] || titleCase(confidence);
}

const SOURCE_TYPE_WORDS = {
  official_experiment_site: 'official experiment site',
  official_facility_site: 'official facility site',
  experiment_registry: 'experiment registry (Greybook)',
  inspire_experiment_record: 'INSPIRE experiment record',
  design_report: 'design report',
  detector_paper: 'detector paper',
  hepdata: 'HEPData record',
  pdg: 'Particle Data Group',
  institution_page: 'institution page',
  geocoder: 'geocoder',
  result_page: 'collaboration result page',
  press_release: 'press release',
  project_document: 'project document',
  journal_article: 'journal article',
  arxiv: 'arXiv preprint',
  inspire_literature_record: 'INSPIRE literature record',
  wikipedia: 'Wikipedia',
  wikidata: 'Wikidata',
  secondary: 'secondary source',
  inspire_record: 'INSPIRE record',
};

export function sourceTypeWord(sourceType) {
  if (!sourceType) return 'source';
  return SOURCE_TYPE_WORDS[sourceType] || titleCase(sourceType);
}

// --------------------------------------------------------- claim rendering
// One <li class="claim-group"> per pointer: its readable label, the quote
// with where to find it in the source (the claim's `locator`: page, section,
// table), the confidence, and the sources that back it — instead of one row
// per (pointer, source). The JSON pointer is a maintainer's handle, not
// something a reader can act on: it stays only as the label's `data-field`
// attribute, for maintainers (a hover tooltip showed it to every reader).

// Lower-case alphanumerics only, so a quote and a source excerpt compare equal
// despite curly quotes, hyphens, whitespace or markup-free punctuation.
function normText(text) {
  return String(text || '').normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
}

// A source's `excerpt` is the passage that source was read for. When the
// claim's quote sits inside it (or the other way round, allowing the authored
// "…" gaps between quote fragments), the record itself says the quote comes
// from that source.
export function sourceHoldsQuote(src, quote) {
  const excerpt = normText(src && src.excerpt);
  const whole = normText(quote);
  if (!excerpt || !whole) return false;
  // An excerpt only counts as "inside the quote" when it is long enough to be a
  // passage rather than a stray phrase.
  const passage = excerpt.length >= 24;
  if (excerpt.includes(whole) || (passage && whole.includes(excerpt))) return true;
  const fragments = String(quote).split(/\.\.\.|…/).map(normText).filter((f) => f.length >= 12);
  return fragments.some((f) => excerpt.includes(f) || (passage && f.includes(excerpt)));
}

// The sources whose own record carries the quote first; everything else keeps
// its authored order (a stable partition — nothing is dropped or invented).
export function orderSourcesForQuote(sources, quote) {
  if (!quote || sources.length < 2) return sources;
  const holders = sources.filter((src) => sourceHoldsQuote(src, quote));
  if (!holders.length || holders.length === sources.length) return sources;
  return [...holders, ...sources.filter((src) => !holders.includes(src))];
}

const PDF_URL = /\.pdf(?:$|[?#])/i;

// A direct PDF for the source, or null. Prefers an explicit PDF URL on the
// record, then the arXiv PDF for an arXiv id (recorded in `reference.arxiv`,
// or readable from an arxiv.org abstract URL).
export function sourcePdfUrl(src) {
  if (!src) return null;
  const ref = src.reference && typeof src.reference === 'object' ? src.reference : {};
  for (const url of [ref.pdf, ref.url, src.url]) {
    if (typeof url === 'string' && PDF_URL.test(url)) return url;
  }
  let arxivId = typeof ref.arxiv === 'string' ? ref.arxiv.trim() : '';
  if (!arxivId) {
    const m = /^https?:\/\/(?:www\.)?arxiv\.org\/(?:abs|pdf)\/(.+?)(?:\.pdf)?(?:[?#].*)?$/i.exec(src.url || '');
    if (m) arxivId = m[1];
  }
  arxivId = arxivId.replace(/^arxiv:/i, '');
  return arxivId ? `https://arxiv.org/pdf/${arxivId}` : null;
}

function sourceRow(src) {
  const pdf = sourcePdfUrl(src);
  const href = src.url || '#';
  const titleIsPdf = !!pdf && pdf === href;
  return h('li', { class: 'claim-source' }, [
    h('a', { href, target: '_blank', rel: 'noopener' }, src.title || src.id),
    titleIsPdf ? h('span', { class: 'source-type' }, 'PDF') : null,
    pdf && !titleIsPdf ? h('a', { class: 'source-pdf', href: pdf, target: '_blank', rel: 'noopener', 'aria-label': `PDF of ${src.title || src.id}` }, 'PDF') : null,
    h('span', { class: 'source-type' }, sourceTypeWord(src.source_type)),
    src.accessed ? h('span', { class: 'source-access' }, `Accessed ${src.accessed}`) : null,
  ]);
}

function claimGroup(pointer, provRecord, sourcesBundle, record) {
  const srcIds = provRecord.sources || [];
  const sources = srcIds.map((id) => sourcesBundle.byId[id]).filter(Boolean);
  if (!sources.length) return null;

  const { label, field } = claimLabel(pointer, record);
  const confidence = confidenceWord(provRecord.confidence);
  const locator = provRecord.locator ? String(provRecord.locator) : '';
  const ordered = orderSourcesForQuote(sources, provRecord.quote);

  return h('li', { class: 'claim-group' }, [
    h('div', { class: 'claim-label', 'data-field': field }, label),
    provRecord.quote ? h('div', { class: 'claim-evidence' }, quoteView(provRecord.quote)) : null,
    locator ? h('div', { class: 'claim-locator' }, [h('span', { class: 'claim-locator-label' }, 'In the source: '), locator]) : null,
    confidence ? h('div', { class: 'claim-confidence' }, `Confidence: ${confidence}`) : null,
    h('ul', { class: 'claim-sources' }, ordered.map(sourceRow)),
  ]);
}

// `entries` is `provenance[entityId]` ({pointer: provRecord}); returns an
// array of <li> nodes (the caller wraps them in one <ul>, alongside any A23
// approximate-location notes), or [] when nothing here has a resolvable
// source.
export function renderClaimItems(entries, sourcesBundle, record) {
  if (!entries) return [];
  const items = [];
  for (const [pointer, provRecord] of Object.entries(entries)) {
    const item = claimGroup(pointer, provRecord, sourcesBundle, record);
    if (item) items.push(item);
  }
  return items;
}

// A23: a linked site's admitted-approximate `/coordinates` note, rendered in
// the same claim-group shape as everything else in the Sources disclosure
// (a labelled claim, the pointer only as a data attribute) instead of a bespoke row.
// The headline keeps the established "Approximate location — <site name>"
// wording (the panel's own "Beam and sites" line already says the same
// thing next to the site link).
export function renderApproximateLocationNote(site, note) {
  const { field } = claimLabel('/coordinates', site);
  return h('li', { class: 'claim-group approximate-location-note' }, [
    h('div', { class: 'claim-label', 'data-field': field }, `Approximate location — ${site.name}`),
    h('div', { class: 'claim-evidence' }, note),
  ]);
}
