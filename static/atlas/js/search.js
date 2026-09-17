// search.js — a typed global search over search.json, rendered as a
// keyboard-navigable combobox ("DUNE — Experiment", "Fermilab — Facility").

import { titleCase } from './model.js';

//: Which kind of thing a person most likely means when several records match.
const TYPE_ORDER = ['experiment', 'facility', 'collaboration', 'site', 'detector',
  'accelerator', 'beamline', 'topic', 'result', 'document', 'institution'];

export function init({ inputEl, listEl, entries, navigate }) {
  let active = -1;
  let shown = [];

  function label(entry) {
    return `${entry.name} — ${titleCase(entry.type)}`;
  }

  function close() {
    listEl.innerHTML = '';
    listEl.classList.add('hidden');
    inputEl.setAttribute('aria-expanded', 'false');
    inputEl.removeAttribute('aria-activedescendant');
    active = -1;
  }

  function select(entry) {
    inputEl.value = '';
    close();
    navigate({ entity: { type: entry.type, slug: entry.id.split(/:(.+)/)[1] } });
  }

  function setActive(index) {
    const items = listEl.querySelectorAll('.search-result');
    items.forEach((el, i) => el.classList.toggle('is-active', i === index));
    if (index >= 0 && items[index]) {
      items[index].scrollIntoView({ block: 'nearest' });
      inputEl.setAttribute('aria-activedescendant', items[index].id);
    } else {
      inputEl.removeAttribute('aria-activedescendant');
    }
    active = index;
  }

  function render(query) {
    const q = query.trim().toLowerCase();
    if (!q) { close(); return; }
    // Rank by how directly an entry answers the query, then by type. Typing
    // "DUNE" must offer the experiment first: it matches only through its
    // alias, while the beamline, collaboration and three detector records all
    // carry "DUNE" inside their names and would otherwise bury it.
    const score = (entry) => {
      const name = entry.name.toLowerCase();
      const aliases = entry.aliases.map((alias) => alias.toLowerCase());
      if (name === q || aliases.includes(q)) return 0;
      if (name.startsWith(q) || aliases.some((alias) => alias.startsWith(q))) return 1;
      if (name.includes(q) || aliases.some((alias) => alias.includes(q))) return 2;
      return 3;
    };
    const typeRank = (type) => {
      const at = TYPE_ORDER.indexOf(type);
      return at < 0 ? TYPE_ORDER.length : at;
    };
    shown = entries
      .map((entry) => ({ entry, rank: score(entry) }))
      .filter((row) => row.rank < 3 || row.entry.subtitle.toLowerCase().includes(q))
      .sort((a, b) => a.rank - b.rank
        || typeRank(a.entry.type) - typeRank(b.entry.type)
        || a.entry.name.length - b.entry.name.length)
      .map((row) => row.entry)
      .slice(0, 25);
    listEl.innerHTML = '';
    if (!shown.length) {
      listEl.appendChild(Object.assign(document.createElement('li'), {
        className: 'search-empty', textContent: 'No matches.',
      }));
    } else {
      shown.forEach((entry, i) => {
        const li = document.createElement('li');
        li.className = 'search-result';
        li.id = `search-result-${i}`;
        li.setAttribute('role', 'option');
        li.textContent = label(entry);
        li.addEventListener('mousedown', (event) => {
          event.preventDefault();
          select(entry);
        });
        listEl.appendChild(li);
      });
    }
    listEl.classList.remove('hidden');
    inputEl.setAttribute('aria-expanded', 'true');
    setActive(-1);
  }

  inputEl.addEventListener('input', () => render(inputEl.value));
  inputEl.addEventListener('keydown', (event) => {
    if (listEl.classList.contains('hidden')) return;
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      setActive(Math.min(active + 1, shown.length - 1));
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      setActive(Math.max(active - 1, 0));
    } else if (event.key === 'Enter') {
      if (active >= 0 && shown[active]) {
        event.preventDefault();
        select(shown[active]);
      }
    } else if (event.key === 'Escape') {
      close();
    }
  });
  inputEl.addEventListener('blur', () => setTimeout(close, 120));
  document.addEventListener('click', (event) => {
    if (!listEl.contains(event.target) && event.target !== inputEl) close();
  });
}
