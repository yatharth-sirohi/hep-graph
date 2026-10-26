// cite-panel.js — the "Cite" section of a result or document panel: the record's BibTeX
// entry (bibtex.js), a button to copy it and one to download it as a .bib file. A record
// with neither a DOI nor an arXiv identifier gets a sentence saying so and no entry.

import * as loader from '../loader.js';
import { citationFor } from './bibtex.js';
import { accessDate, downloadFile } from './files.js';

function h(tag, attrs = {}, children = []) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (key === 'class') el.className = value;
    else if (value !== null && value !== undefined) el.setAttribute(key, value);
  }
  for (const child of [].concat(children)) {
    if (child == null) continue;
    el.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
  }
  return el;
}

function selectContents(node) {
  const range = document.createRange();
  range.selectNodeContents(node);
  const selection = window.getSelection();
  selection.removeAllRanges();
  selection.addRange(range);
}

/** The body of the "Cite" section for `record` (a result or a document); `atlas` supplies the collaborations. */
export function citeBody({ record, atlas }) {
  const citation = citationFor(record, { collaborations: (atlas && atlas.collaborations) || {} });
  if (!citation.ok) {
    return h('p', { class: 'empty-note cite-none' }, citation.reason);
  }
  const code = h('code', {}, citation.text);
  const entry = h('pre', { class: 'cite-entry', tabindex: '0', 'aria-label': `BibTeX entry for ${record.name || record.id}` }, code);
  const copy = h('button', { type: 'button', class: 'text-btn cite-copy' }, 'Copy BibTeX');
  const download = h('button', { type: 'button', class: 'text-btn cite-download' }, 'Download .bib');
  const status = h('span', { class: 'cite-status', role: 'status', 'aria-live': 'polite' });

  copy.addEventListener('click', async () => {
    status.classList.remove('is-error');
    try {
      await navigator.clipboard.writeText(citation.text);
      status.textContent = 'Copied to the clipboard.';
    } catch (error) {
      // No clipboard permission (a phone, an insecure origin): the entry is selected for the reader to copy.
      selectContents(code);
      status.textContent = 'Copying was not allowed here. The entry is selected: press Ctrl+C (⌘C on a Mac).';
    }
  });
  download.addEventListener('click', async () => {
    status.classList.remove('is-error');
    try {
      const manifest = await loader.getManifest();
      const version = manifest.data_version || manifest.version || 'unknown';
      const header = [
        `% From HEP Atlas, data version ${version}; record ${record.id}; accessed ${accessDate()}.`,
        '% Fields the record does not carry are left out, not guessed.',
      ];
      downloadFile(`${citation.key}.bib`, `${header.join('\n')}\n${citation.text}\n`, 'application/x-bibtex');
      status.textContent = `Downloaded ${citation.key}.bib.`;
    } catch (error) {
      status.classList.add('is-error');
      status.textContent = `The file could not be prepared: ${error.message}.`;
    }
  });

  return h('div', { class: 'cite' }, [
    entry,
    h('div', { class: 'cite-actions' }, [copy, download, status]),
    citation.missing.length
      ? h('p', { class: 'source-meta cite-missing' }, `Not carried by the record, so left out: ${citation.missing.join(', ')}.`)
      : null,
  ]);
}
