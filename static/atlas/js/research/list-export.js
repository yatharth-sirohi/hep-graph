// list-export.js — "Download CSV" and "Download JSON" for the Results and Documents
// lists, as filtered. The file holds the rows on screen, in the order on screen, with
// their ids, names, dates, experiments (or owners), DOI and arXiv identifiers and the URLs
// of the sources the Atlas cites for each record. Its header says which Atlas data
// version it came from, which filter produced it and when it was downloaded.
//
// The row builders are pure (the unit check runs them under Node); exportBar() is the
// two buttons.

import * as loader from '../loader.js';
import { fmtDate } from '../model.js';
import {
  accessDate, buildCsv, buildJson, downloadFile, fileName,
} from './files.js';

const slugOf = (id) => String(id).split(/:(.+)/)[1];

/** The URLs of the sources the Atlas cites for a record, once each, in provenance order. */
export function sourceUrlsOf(id, provenance, sourcesById) {
  const urls = [];
  for (const claim of Object.values((provenance && provenance[id]) || {})) {
    for (const sourceId of (claim && claim.sources) || []) {
      const url = sourcesById[sourceId] && sourcesById[sourceId].url;
      if (url && !urls.includes(url)) urls.push(url);
    }
  }
  return urls;
}

const nameOfId = (atlas, id) => {
  const group = { experiment: 'experiments', collaboration: 'collaborations', detector: 'detectors', beamline: 'beamlines', accelerator: 'accelerators', facility: 'facilities' }[String(id).split(':')[0]];
  const record = group && atlas[group] && atlas[group][id];
  return (record && record.name) || id;
};

/** Rows of the Results list: plain objects, arrays kept as arrays (JSON as is, CSV joined). */
export function resultRows(records, { atlas, provenance, sourcesById, base }) {
  return records.map((result) => {
    const publication = result.publication || {};
    return {
      id: result.id,
      name: result.name || result.title || '',
      title: result.title || '',
      date: fmtDate(result.date),
      date_kind: result.date_kind || '',
      result_type: result.result_type || '',
      experiments: (result.experiment_ids || []).map((id) => nameOfId(atlas, id)),
      experiment_ids: result.experiment_ids || [],
      doi: publication.doi || '',
      arxiv: publication.arxiv || '',
      url: publication.url || result.official_url || '',
      atlas_url: `${base}#/result/${slugOf(result.id)}`,
      source_urls: sourceUrlsOf(result.id, provenance, sourcesById),
    };
  });
}

/** Rows of the Documents list. */
export function documentRows(records, { atlas, provenance, sourcesById, base }) {
  return records.map((doc) => {
    const reference = doc.reference || {};
    return {
      id: doc.id,
      name: doc.name || '',
      doc_type: doc.doc_type || '',
      date: fmtDate(doc.date),
      owners: (doc.owner_ids || []).map((id) => nameOfId(atlas, id)),
      owner_ids: doc.owner_ids || [],
      doi: reference.doi || '',
      arxiv: reference.arxiv || '',
      report_number: reference.report_number || '',
      url: reference.url || '',
      atlas_url: `${base}#/document/${slugOf(doc.id)}`,
      source_urls: sourceUrlsOf(doc.id, provenance, sourcesById),
    };
  });
}

const LISTS = {
  results: { title: 'Results', noun: 'results' },
  documents: { title: 'Documents', noun: 'documents' },
};

const joined = (value) => (Array.isArray(value) ? value.join(' | ') : value);

/**
 * The CSV and the JSON of a list: `meta` is `{ list, dataVersion, accessed, filter, shown,
 * total, link }`; `rows` are resultRows() or documentRows().
 */
export function listFiles(kind, rows, meta) {
  const noun = LISTS[kind].noun;
  const full = {
    source: 'HEP Atlas',
    list: LISTS[kind].title,
    data_version: meta.dataVersion,
    filter: meta.filter,
    rows_shown: meta.shown,
    rows_in_list: meta.total,
    accessed: meta.accessed,
    link: meta.link,
  };
  const header = rows.length ? Object.keys(rows[0]) : [];
  const csv = buildCsv({
    preamble: [
      `HEP Atlas: ${noun} list`,
      `Atlas data version: ${meta.dataVersion}`,
      `Filter: ${meta.filter}`,
      `Rows: ${meta.shown} of ${meta.total} ${noun}`,
      `Accessed: ${meta.accessed}`,
      `Link: ${meta.link}`,
      'Columns holding several values (experiments, owners, source_urls) separate them with " | ".',
    ],
    header,
    rows: rows.map((row) => header.map((key) => joined(row[key]))),
  });
  return { csv, json: buildJson(full, rows), header };
}

/**
 * The two buttons. `snapshot()` is asked at the moment of the click and returns what is
 * on screen then: `{ records, filter, total }` (records in the order shown).
 */
export function exportBar({ kind, atlas, snapshot }) {
  const make = (text, cls) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = `text-btn export-btn ${cls}`;
    b.textContent = text;
    return b;
  };
  const csvButton = make('Download CSV', 'export-csv');
  const jsonButton = make('Download JSON', 'export-json');
  const status = document.createElement('span');
  status.className = 'export-status';
  status.setAttribute('role', 'status');
  status.setAttribute('aria-live', 'polite');
  const bar = document.createElement('div');
  bar.className = 'export-bar';
  bar.setAttribute('role', 'group');
  bar.setAttribute('aria-label', `Download the ${LISTS[kind].noun} shown`);
  bar.append(csvButton, jsonButton, status);

  async function run(format) {
    const { records, filter, total } = snapshot();
    status.classList.remove('is-error');
    if (!records.length) {
      status.textContent = `Nothing to download: no ${LISTS[kind].noun} match the filters.`;
      return;
    }
    status.textContent = 'Preparing the file…';
    try {
      // The sources of every record are in provenance.json: fetched when asked for, not before.
      const [provenance, sources, manifest] = await Promise.all([loader.getProvenance(), loader.getSources(), loader.getManifest()]);
      const base = `${window.location.origin}${window.location.pathname}`;
      const build = kind === 'results' ? resultRows : documentRows;
      const rows = build(records, { atlas, provenance, sourcesById: sources.byId, base });
      const accessed = accessDate();
      const files = listFiles(kind, rows, {
        dataVersion: manifest.data_version || manifest.version || 'unknown',
        accessed,
        filter,
        shown: records.length,
        total,
        link: window.location.href,
      });
      const name = fileName(['hep-atlas', kind, accessed], format);
      downloadFile(name, format === 'csv' ? files.csv : files.json, format === 'csv' ? 'text/csv' : 'application/json');
      status.textContent = `Downloaded ${name}: ${records.length} of ${total}.`;
    } catch (error) {
      status.classList.add('is-error');
      status.textContent = `The file could not be prepared: ${error.message}. Try again.`;
    }
  }
  csvButton.addEventListener('click', () => { run('csv'); });
  jsonButton.addEventListener('click', () => { run('json'); });
  return bar;
}
