// search.js — a typed global search over search.json, rendered as a
// keyboard-navigable combobox ("DUNE — Experiment", "Fermilab — Facility").
//
// ARIA 1.2 editable combobox with list autocomplete: focus stays in the text
// box; the highlighted option is named by aria-activedescendant. The first
// option is active as soon as a list appears, so typing a name and pressing
// Enter opens the best match; ArrowUp/ArrowDown move through the options,
// Escape closes the list (a second Escape clears the box).

import { titleCase } from './model.js';

//: Which kind of thing a person most likely means when several records match.
const TYPE_ORDER = ['experiment', 'facility', 'collaboration', 'site', 'detector',
  'accelerator', 'beamline', 'topic', 'result', 'document', 'institution'];

export function init({ inputEl, listEl, entries, navigate }) {
  let active = -1;
  let shown = [];
  // A polite live region that says how many options the list holds, so a
  // screen-reader user hears that typing produced results (or none).
  const statusEl = document.getElementById('search-status');

  function label(entry) {
    return `${entry.name} — ${titleCase(entry.type)}`;
  }

  function announce(text) {
    if (statusEl) statusEl.textContent = text;
  }

  function isOpen() {
    return !listEl.classList.contains('hidden');
  }

  function close() {
    listEl.innerHTML = '';
    listEl.classList.add('hidden');
    inputEl.setAttribute('aria-expanded', 'false');
    inputEl.removeAttribute('aria-activedescendant');
    shown = [];
    active = -1;
    announce('');
  }

  function select(entry) {
    inputEl.value = '';
    close();
    navigate({ entity: { type: entry.type, slug: entry.id.split(/:(.+)/)[1] } });
  }

  function setActive(index) {
    const items = listEl.querySelectorAll('.search-result');
    items.forEach((el, i) => {
      el.classList.toggle('is-active', i === index);
      el.setAttribute('aria-selected', i === index ? 'true' : 'false');
    });
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
      // Not an option: it can never be activated or chosen. role=presentation
      // keeps it out of the listbox's option count; the live region says it.
      listEl.appendChild(Object.assign(document.createElement('li'), {
        className: 'search-empty', textContent: 'No matches.',
      }));
      listEl.lastChild.setAttribute('role', 'presentation');
    } else {
      shown.forEach((entry, i) => {
        const li = document.createElement('li');
        li.className = 'search-result';
        li.id = `search-result-${i}`;
        li.setAttribute('role', 'option');
        li.setAttribute('aria-selected', 'false');
        li.textContent = label(entry);
        li.addEventListener('mousedown', (event) => {
          event.preventDefault();
          select(entry);
        });
        // One highlighted row at a time: hovering moves the active option
        // instead of leaving the keyboard's row and the pointer's both lit.
        li.addEventListener('mousemove', () => { if (active !== i) setActive(i); });
        listEl.appendChild(li);
      });
    }
    listEl.classList.remove('hidden');
    inputEl.setAttribute('aria-expanded', 'true');
    // The best match is highlighted from the start, so Enter has a target.
    setActive(shown.length ? 0 : -1);
    announce(shown.length
      ? `${shown.length} result${shown.length === 1 ? '' : 's'}; press Enter to open ${label(shown[0])}`
      : 'No matches.');
  }

  inputEl.addEventListener('input', () => render(inputEl.value));
  inputEl.addEventListener('keydown', (event) => {
    // Enter confirming an IME composition is not a request to open anything.
    if (event.isComposing || event.keyCode === 229) return;
    const { key } = event;
    if (key === 'ArrowDown' || key === 'ArrowUp') {
      // Alt+arrow is the combobox shorthand for "show the list" and must not
      // move the highlight; a closed list with text in the box reopens.
      if (!isOpen()) {
        if (!inputEl.value.trim()) return;
        event.preventDefault();
        render(inputEl.value);
        return;
      }
      event.preventDefault();
      if (event.altKey || !shown.length) return;
      const step = key === 'ArrowDown' ? 1 : -1;
      setActive((active + step + shown.length) % shown.length);
    } else if (key === 'Enter') {
      if (!isOpen()) {
        // The list was dismissed (Escape) but the box still holds a query:
        // Enter asks for it again rather than doing nothing.
        if (!inputEl.value.trim()) return;
        render(inputEl.value);
      }
      if (active >= 0 && shown[active]) {
        event.preventDefault();
        select(shown[active]);
      } else if (isOpen()) {
        event.preventDefault(); // "No matches." — nothing to open
      }
    } else if (key === 'Escape') {
      // Escape belongs to the search box while it has something to dismiss;
      // otherwise it falls through to app.js, which closes the record panel.
      if (isOpen()) {
        event.stopPropagation();
        close();
      } else if (inputEl.value) {
        event.stopPropagation();
        inputEl.value = '';
      }
    }
  });
  inputEl.addEventListener('blur', () => setTimeout(close, 120));
  document.addEventListener('click', (event) => {
    if (!listEl.contains(event.target) && event.target !== inputEl) close();
  });
}
