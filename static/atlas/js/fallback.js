// fallback.js — when WebGL2 is unavailable, render the same data as
// accessible lists and tables instead of the globe. Detail panels are
// reused unchanged (panels.js does not depend on the globe being present).

import { titleCase, fmtDate } from './model.js';

function h(tag, attrs = {}, children = []) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (k === 'class') el.className = v;
    else if (v !== null && v !== undefined) el.setAttribute(k, v);
  }
  for (const child of [].concat(children)) {
    if (child == null) continue;
    el.appendChild((typeof child === 'string' || typeof child === 'number') ? document.createTextNode(String(child)) : child);
  }
  return el;
}

function linkCell(route, text, navigate) {
  const a = h('a', { href: `#/${route.type}/${route.slug}` }, text);
  a.addEventListener('click', (event) => {
    event.preventDefault();
    navigate({ entity: route });
  });
  const td = h('td', {}, a);
  return td;
}

function table(caption, headers, rows) {
  const t = h('table', { class: 'fallback-table' });
  t.appendChild(h('caption', {}, caption));
  const thead = h('thead', {}, h('tr', {}, headers.map((header) => h('th', { scope: 'col' }, header))));
  const tbody = h('tbody', {}, rows);
  t.append(thead, tbody);
  return t;
}

export function render(container, { atlas, results, navigate }) {
  container.innerHTML = '';
  container.setAttribute('role', 'region');
  container.setAttribute('aria-label', 'HEP Atlas, accessible list view');

  container.appendChild(h('div', { class: 'fallback-notice', role: 'status' }, [
    h('strong', {}, 'The interactive 3D globe is not shown. '),
    'Your browser does not report WebGL2 support (or a real GPU is unavailable), so the HEP Atlas '
      + 'data is shown here as accessible lists and tables with the same detail panels instead.',
  ]));

  const facilityRows = Object.values(atlas.facilities).sort((a, b) => a.name.localeCompare(b.name)).map((f) => {
    const tr = h('tr', {});
    tr.appendChild(linkCell({ type: 'facility', slug: f.id.split(':')[1] }, f.name, navigate));
    tr.append(h('td', {}, titleCase(f.kind)), h('td', {}, titleCase(f.status)), h('td', {}, (f.country || []).join(', ')));
    return tr;
  });
  container.appendChild(table('Facilities', ['Name', 'Kind', 'Status', 'Country'], facilityRows));

  const experimentRows = Object.values(atlas.experiments).sort((a, b) => a.name.localeCompare(b.name)).map((e) => {
    const tr = h('tr', {});
    tr.appendChild(linkCell({ type: 'experiment', slug: e.id.split(':')[1] }, e.name, navigate));
    const facilities = (e.facility_ids || []).map((fid) => atlas.facilities[fid] && atlas.facilities[fid].name).filter(Boolean).join(', ');
    tr.append(h('td', {}, titleCase(e.kind)), h('td', {}, facilities), h('td', {}, titleCase(e.status)));
    return tr;
  });
  container.appendChild(table('Experiments', ['Name', 'Kind', 'Facility', 'Status'], experimentRows));

  const collabRows = Object.values(atlas.collaborations).sort((a, b) => a.name.localeCompare(b.name)).map((c) => {
    const tr = h('tr', {});
    tr.appendChild(linkCell({ type: 'collaboration', slug: c.id.split(':')[1] }, c.name, navigate));
    const host = c.host_facility_id && atlas.facilities[c.host_facility_id];
    tr.append(h('td', {}, host ? host.name : ''), h('td', {}, (c.membership && c.membership.count_label) || ''));
    return tr;
  });
  container.appendChild(table('Collaborations', ['Name', 'Host facility', 'Membership'], collabRows));

  const resultRows = results.list.slice().sort((a, b) => (b.month || 0) - (a.month || 0)).map((r) => {
    const tr = h('tr', {});
    tr.appendChild(linkCell({ type: 'result', slug: r.id.split(':')[1] }, (r.name || r.title), navigate));
    tr.append(h('td', {}, fmtDate(r.date) || ''), h('td', {}, titleCase(r.result_type)), h('td', {}, r.significance || ''));
    return tr;
  });
  container.appendChild(table('Results', ['Title', 'Date', 'Type', 'Significance'], resultRows));
}
