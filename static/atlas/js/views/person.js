// person.js — "Researcher on the Atlas": where the Atlas places one INSPIRE author.
//
//   #/view/person/<inspire-author-id>          e.g. #/view/person/1005149
//
// The one join key with HEP Graph is the INSPIRE author record id, so the route carries
// it and nothing else. From it:
//   * the Atlas's own rosters (people/<collaboration>/<institution>.json) give the
//     collaborations and institutions where the Atlas has a membership row for this
//     author; collaboration.experiment_ids gives the experiments, their detector sites
//     give the places. Those are drawn on a world map, each place a link that opens the
//     record on the globe, and listed in a table;
//   * HEP Graph's own record (GET /api/person/<id>?summary=1, the existing same-origin
//     endpoint) is shown beside it: the name and the affiliation *names* INSPIRE reports.
//     Those names are not matched to Atlas institutions (a name is not an id).
//
// What is never claimed: the Atlas's rosters are partial, so an author with no row is
// UNKNOWN to the Atlas, not "on no experiment". And a failure is an error: an author the
// Atlas does not know, with HEP Graph unreachable, is a failed page (nothing could be
// said); an author the Atlas does know keeps its own rows, and the HEP Graph part says
// plainly that it failed. Mounted by host.js through registry.js.

import {
  PERSON_VIEW_TITLE, authorIdOf, fetchHepGraphPerson, hepGraphPersonUrl, parseAuthorId, rosterPeople,
} from '../hepgraph.js';
import { siteLatLon } from './beam-rows.js';

const SVG_NS = 'http://www.w3.org/2000/svg';

function h(tag, attrs = {}, children = []) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (key === 'class') el.className = value;
    else if (key === 'text') el.textContent = value;
    else if (value !== null && value !== undefined) el.setAttribute(key, value);
  }
  for (const child of [].concat(children)) {
    if (child == null) continue;
    el.appendChild((typeof child === 'string' || typeof child === 'number') ? document.createTextNode(String(child)) : child);
  }
  return el;
}

function s(tag, attrs = {}, children = []) {
  const el = document.createElementNS(SVG_NS, tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (key === 'class') el.setAttribute('class', value);
    else if (key === 'text') el.textContent = value;
    else if (value !== null && value !== undefined) el.setAttribute(key, String(value));
  }
  for (const child of [].concat(children)) {
    if (child == null) continue;
    el.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
  }
  return el;
}

const plural = (n, one, many = `${one}s`) => `${n} ${n === 1 ? one : many}`;
/** A message as a sentence: one full stop at the end, however it arrived. */
const sentence = (text) => `${String(text).replace(/\.+$/, '')}.`;
const idRoute = (id) => {
  const [type, slug] = String(id).split(/:(.+)/);
  return { type, slug };
};

/** A link to an Atlas record that opens it in this page (a plain href for a new tab). */
function recordLink(navigate, id, text, extra = {}) {
  const route = idRoute(id);
  const a = h('a', { href: `#/${route.type}/${route.slug}`, class: 'entity-link', ...extra }, text);
  a.addEventListener('click', (event) => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    navigate({ entity: route });
  });
  return a;
}

// ---------------------------------------------------------------- the rows
/** One row per membership the Atlas records for this author, joined to its records. */
function buildRows(authorRows, atlas, institutions) {
  return authorRows.map((row) => {
    const collaboration = atlas.collaborations && atlas.collaborations[row.collaboration_id];
    const experiments = ((collaboration && collaboration.experiment_ids) || [])
      .map((id) => atlas.experiments && atlas.experiments[id]).filter(Boolean);
    const institution = row.institution_id ? institutions[row.institution_id] || null : null;
    return { row, collaboration, experiments, institution };
  });
}

function placesOf(rows, atlas) {
  const institutions = new Map();
  const sites = new Map();
  for (const { institution, experiments } of rows) {
    const where = institution && siteLatLon(institution);
    if (where) institutions.set(institution.id, { record: institution, where });
    for (const experiment of experiments) {
      for (const siteId of experiment.site_ids || []) {
        const site = atlas.sites && atlas.sites[siteId];
        const at = site && siteLatLon(site);
        if (at && !sites.has(siteId)) sites.set(siteId, { record: site, where: at });
      }
    }
  }
  return { institutions: [...institutions.values()], sites: [...sites.values()] };
}

// ---------------------------------------------------------------- the map
// Equirectangular, 2 units per degree. The map runs from 84 N down to 58 S, and lower only
// when a place is further south (the South Pole): Antarctica would otherwise be a third of
// the picture and empty for almost everyone.
const MAP_W = 720;
const MAP_TOP = 84;
const mapX = (lon) => (lon + 180) * (MAP_W / 360);
const mapY = (lat) => (MAP_TOP - lat) * 2;

function landPath(land) {
  const parts = [];
  for (const feature of (land && land.features) || []) {
    const g = feature.geometry;
    const polygons = !g ? [] : g.type === 'MultiPolygon' ? g.coordinates : g.type === 'Polygon' ? [g.coordinates] : [];
    for (const polygon of polygons) {
      for (const ring of polygon) {
        // An edge that jumps across the antimeridian (|dlon| > 180) would be drawn straight
        // across the whole map; start a new sub-path there instead.
        parts.push(`${ring.map(([lon, lat], i) => {
          const jump = i && Math.abs(lon - ring[i - 1][0]) > 180;
          return `${i && !jump ? 'L' : 'M'}${mapX(lon).toFixed(1)} ${mapY(lat).toFixed(1)}`;
        }).join('')}Z`);
      }
    }
  }
  return parts.join('');
}

function drawMap({ places, land, name, navigate }) {
  const southmost = Math.min(...[...places.institutions, ...places.sites].map((entry) => entry.where.lat));
  const bottom = Math.max(-90, Math.min(-58, southmost - 8));
  const MAP_H = (MAP_TOP - bottom) * 2;
  const svg = s('svg', {
    class: 'pv-svg', viewBox: `0 0 ${MAP_W} ${MAP_H}`, role: 'group',
    'aria-labelledby': 'pv-map-title pv-map-desc', focusable: 'false',
  });
  svg.appendChild(s('title', { id: 'pv-map-title', text: `Where the Atlas places ${name}` }));
  svg.appendChild(s('desc', {
    id: 'pv-map-desc',
    text: `A flat world map with ${plural(places.institutions.length, 'institution')} (circles) and `
      + `${plural(places.sites.length, 'experiment site')} (diamonds). The table below lists the same places.`,
  }));
  svg.appendChild(s('rect', { class: 'pv-sea', x: 0, y: 0, width: MAP_W, height: MAP_H }));
  if (land) svg.appendChild(s('path', { class: 'pv-land', d: landPath(land) }));
  const mark = (entry, kind) => {
    const route = idRoute(entry.record.id);
    const a = s('a', {
      class: `pv-mark pv-mark-${kind}`, href: `#/${route.type}/${route.slug}`,
      'aria-label': `${entry.record.name} (${kind === 'inst' ? 'institution' : 'experiment site'}), open its Atlas record`,
      transform: `translate(${mapX(entry.where.lon).toFixed(1)} ${mapY(entry.where.lat).toFixed(1)})`,
    }, [
      s('title', { text: entry.record.name }),
      s('circle', { class: 'pv-hit', r: 14 }),
      kind === 'inst'
        ? s('circle', { r: 6 })
        : s('path', { d: 'M0 -8L8 0L0 8L-8 0Z' }),
    ]);
    a.addEventListener('click', (event) => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      navigate({ entity: route });
    });
    return a;
  };
  // Sites first so an institution on top of one stays the larger, clickable mark.
  for (const entry of places.sites) svg.appendChild(mark(entry, 'site'));
  for (const entry of places.institutions) svg.appendChild(mark(entry, 'inst'));
  return svg;
}

// ---------------------------------------------------------------- the table
function datesText(row) {
  if (row.start && row.end) return `${row.start} to ${row.end}`;
  if (row.start) return `since ${row.start}`;
  if (row.end) return `until ${row.end}`;
  return 'dates not recorded';
}

/** "Show on the globe": collaboration mode, which puts the collaboration's member institutions
 * (this person's among them) on the globe. Only offered where the Atlas has a roster. */
function globeLink(navigate, collaboration) {
  const slug = collaboration.id.split(':')[1];
  const data = new URLSearchParams(window.location.search).get('data');
  const a = h('a', {
    class: 'pv-globe-link',
    href: `?${data ? `data=${encodeURIComponent(data)}&` : ''}m=collab&c=${slug}#/collaboration/${slug}`,
  }, 'Show its institutions on the globe');
  a.addEventListener('click', (event) => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    navigate({ entity: { type: 'collaboration', slug }, mode: 'collab', collab: slug });
  });
  return a;
}

function drawTable(rows, navigate, rosterListed) {
  const table = h('table', { class: 'pv-table' });
  table.appendChild(h('caption', {}, 'Memberships the Atlas records for this researcher'));
  table.appendChild(h('thead', {}, h('tr', {}, ['Collaboration', 'Experiments', 'Institution', 'Dates', 'What the Atlas has']
    .map((label) => h('th', { scope: 'col' }, label)))));
  const body = h('tbody');
  for (const { row, collaboration, experiments, institution } of rows) {
    const place = institution && institution.place
      ? [institution.place.city, institution.place.country].filter(Boolean).join(', ') : '';
    body.appendChild(h('tr', {}, [
      h('td', { 'data-label': 'Collaboration' }, collaboration
        ? [recordLink(navigate, collaboration.id, collaboration.name),
          rosterListed.has(collaboration.id) ? h('div', { class: 'pv-sub' }, globeLink(navigate, collaboration)) : null]
        : (row.collaboration_id || 'not recorded')),
      h('td', { 'data-label': 'Experiments' }, experiments.length
        ? h('ul', { class: 'pv-list' }, experiments.map((e) => h('li', {}, recordLink(navigate, e.id, e.name))))
        : 'none linked to this collaboration in the Atlas'),
      h('td', { 'data-label': 'Institution' }, institution
        ? [recordLink(navigate, institution.id, institution.name), place ? h('div', { class: 'pv-sub' }, place) : null]
        : (row.institution_id ? `${row.institution_id} (not in the Atlas's institution list)` : 'institution not recorded')),
      h('td', { 'data-label': 'Dates' }, datesText(row)),
      h('td', { 'data-label': 'What the Atlas has' }, row.evidence_label || 'evidence not labelled'),
    ]));
  }
  table.appendChild(body);
  return h('div', { class: 'pv-table-wrap' }, table);
}

// ---------------------------------------------------------------- HEP Graph
/** The HEP Graph slot: loading, the record, "not in the release", a partial, or an error. */
function fillHepGraph(slot, authorId, outcome, { retry }) {
  slot.replaceChildren();
  const openLink = h('a', { class: 'pv-hg-open', href: hepGraphPersonUrl(authorId), target: '_blank', rel: 'noopener' },
    'Open in HEP Graph →');
  if (!outcome) {
    slot.appendChild(h('p', { class: 'loading-note', role: 'status' }, 'Asking HEP Graph…'));
    return;
  }
  if (!outcome.ok) {
    slot.appendChild(h('div', { class: 'pv-hg-error', role: 'alert' }, [
      h('p', {}, `HEP Graph could not be reached: ${sentence(outcome.error.message)} What HEP Graph holds on this author is `
        + 'unknown here — this is a failure, not an empty record.'),
      h('button', { type: 'button', class: 'text-btn pv-retry' }, 'Retry'),
    ]));
    slot.querySelector('.pv-retry').addEventListener('click', retry);
    slot.appendChild(openLink);
    return;
  }
  const result = outcome.value;
  if (result.state === 'not_in_release') {
    slot.appendChild(h('p', {}, 'This author is not in HEP Graph’s current release. That is not evidence that they '
      + 'are absent from INSPIRE.'));
    return;
  }
  if (result.state === 'details_unavailable') {
    slot.appendChild(h('p', {}, `HEP Graph has this author, but their profile details could not be fetched just now (${result.reason}). `
      + 'Their name and affiliations are unknown here, not empty.'));
    slot.appendChild(openLink);
    return;
  }
  const person = result.person;
  const affiliations = Array.isArray(person.affiliations) ? person.affiliations : [];
  slot.appendChild(h('dl', { class: 'pv-dl' }, [
    h('div', {}, [h('dt', {}, 'Name in HEP Graph'), h('dd', {}, person.name || `INSPIRE author ${authorId}`)]),
    person.orcid ? h('div', {}, [h('dt', {}, 'ORCID'), h('dd', {}, person.orcid)]) : null,
    h('div', {}, [h('dt', {}, 'Affiliations INSPIRE reports'), h('dd', {}, affiliations.length
      ? h('ul', { class: 'pv-list' }, affiliations.map((a) => h('li', {}, a)))
      : 'none supplied')]),
  ]));
  slot.appendChild(h('p', { class: 'pv-note' }, 'These are institution names as INSPIRE spells them. The Atlas does not '
    + 'match them to its own institutions (a name is not an id), so they are not drawn on the map.'));
  slot.appendChild(openLink);
}

// ---------------------------------------------------------------- mount
export async function mount(ctx) {
  const { arg, atlas, host, loader, navigate } = ctx;
  const authorId = parseAuthorId(arg);
  host.setTitle(PERSON_VIEW_TITLE);
  // The map marks places without naming them (the table beside it does), so a picture of it alone
  // would say nothing: no image is offered.
  host.setExportReason('The map marks places without naming them (the table below does), so it is not offered as an image.');
  if (!authorId) {
    host.fail(`“${arg}” is not an INSPIRE author id. The route takes the number from an INSPIRE author link, `
      + 'for example #/view/person/1005149.');
    return null;
  }
  host.setSubtitle(`INSPIRE author ${authorId}`);

  const route = window.location.hash;
  let alive = true;
  const stale = () => !alive || window.location.hash !== route;
  let hepGraphOutcome = null;
  let slot = null;

  const askHepGraph = () => {
    hepGraphOutcome = null;
    if (slot) fillHepGraph(slot, authorId, null, { retry: askHepGraph });
    const asked = fetchHepGraphPerson(authorId).then(
      (value) => ({ ok: true, value }),
      (error) => ({ ok: false, error }),
    ).then((outcome) => {
      hepGraphOutcome = outcome;
      if (slot && !stale()) fillHepGraph(slot, authorId, outcome, { retry: askHepGraph });
      return outcome;
    });
    return asked;
  };

  async function run() {
    host.body.replaceChildren(h('p', { class: 'loading-note', role: 'status' }, 'Looking this author up in the Atlas and in HEP Graph…'));
    // host.fail() hides the "Inputs and method" disclosure; a retry that succeeds shows it again.
    const methodBox = host.method.closest('details');
    if (methodBox) methodBox.hidden = false;
    const hepGraph = askHepGraph();
    let scan;
    let institutions;
    try {
      [scan, institutions] = await Promise.all([rosterPeople(), loader.getInstitutions()]);
    } catch (error) {
      if (stale()) return;
      host.fail(`The Atlas’s people records could not be read (${error.message.replace(/\.$/, '')}), so nothing can be said about this author yet.`, { retry: run });
      return;
    }
    const ownRows = scan.rows.filter((row) => authorIdOf(row.id) === authorId);
    if (!ownRows.length) {
      // Unknown to the Atlas. Only HEP Graph could say more, so a failure there is the page's failure.
      const outcome = await hepGraph;
      if (stale()) return;
      if (!outcome.ok) {
        host.fail(`HEP Graph could not be reached (${outcome.error.message.replace(/\.$/, '')}). The Atlas has no membership row for this `
          + 'author, and without HEP Graph nothing else is known. That is a failure to look, not a finding that the author '
          + 'is on no experiment.', { retry: run });
        return;
      }
    }
    if (stale()) return;

    const rows = buildRows(ownRows, atlas, institutions);
    const knownPeople = new Set(scan.rows.map((row) => authorIdOf(row.id)).filter(Boolean));
    const knownCollaborations = new Set(scan.rows.map((row) => row.collaboration_id).filter(Boolean));
    const name = (ownRows[0] && ownRows[0].name)
      || (hepGraphOutcome && hepGraphOutcome.ok && hepGraphOutcome.value.person && hepGraphOutcome.value.person.name)
      || PERSON_VIEW_TITLE;
    host.setTitle(name);

    const page = h('div', { class: 'pv' });
    const experimentIds = new Set(rows.flatMap((r) => r.experiments.map((e) => e.id)));
    const institutionIds = new Set(rows.map((r) => r.row.institution_id).filter(Boolean));
    const collaborationIds = new Set(rows.map((r) => r.row.collaboration_id).filter(Boolean));
    page.appendChild(h('p', { class: 'pv-lede' }, rows.length
      ? `${name} has ${plural(rows.length, 'membership')} recorded in the Atlas: ${plural(collaborationIds.size, 'collaboration')} `
        + `at ${plural(institutionIds.size, 'institution')}, reaching ${plural(experimentIds.size, 'experiment')}.`
      : `The Atlas has no membership recorded for INSPIRE author ${authorId}. That is unknown, not none.`));
    page.appendChild(h('p', { class: 'pv-partial', role: 'note' }, [
      h('strong', {}, 'The Atlas’s institution rosters are only partial. '),
      `It names ${plural(knownPeople.size, 'researcher')} with an INSPIRE author id, in ${plural(knownCollaborations.size, 'collaboration')} `
      + `(${plural(scan.bundleCount, 'people file')}); every other researcher is simply not in its rosters. A person or a membership `
      + 'missing here is unknown to the Atlas, not evidence that it does not exist.',
    ]));

    if (rows.length) {
      const places = placesOf(rows, atlas);
      // A roster is what collaboration mode draws; a collaboration with none has no globe view.
      const rosterListed = new Set();
      await Promise.all([...collaborationIds].map(async (cid) => {
        if (await loader.isBundleListed(`memberships/${cid.split(':')[1]}.json`)) rosterListed.add(cid);
      }));
      let land = null;
      try { land = await loader.getLandOutline(); } catch (error) { land = null; }
      if (stale()) return;
      const total = places.institutions.length + places.sites.length;
      const unplaced = rows.filter((r) => !(r.institution && siteLatLon(r.institution))).length;
      if (!total) {
        page.appendChild(h('p', { class: 'pv-note' }, 'No institution or experiment site of these memberships has a recorded '
          + 'position in the Atlas, so there is no map. The table lists them.'));
      } else page.appendChild(h('figure', { class: 'pv-figure' }, [
        h('div', { class: 'pv-map' }, drawMap({ places, land, name, navigate })),
        h('figcaption', { class: 'pv-caption' }, [
          h('span', { class: 'pv-key' }, [h('i', { class: 'pv-key-inst' }), ' institution']),
          h('span', { class: 'pv-key' }, [h('i', { class: 'pv-key-site' }), ' experiment site (every site of the collaboration’s experiments)']),
          ` · ${plural(total, 'place')} drawn. Each mark opens its Atlas record.`,
          unplaced ? ` ${plural(unplaced, 'membership row')} without an institution position in the Atlas: not drawn.` : '',
          land ? '' : ' (The coastline file did not load; the marks are still positioned.)',
        ]),
      ]));
      page.appendChild(h('section', { class: 'pv-section' }, [h('h3', {}, 'Where the Atlas places them'), drawTable(rows, navigate, rosterListed)]));
    }

    const hgSection = h('section', { class: 'pv-section pv-hepgraph' }, [h('h3', {}, 'In HEP Graph')]);
    slot = h('div', { class: 'pv-hg-slot' });
    hgSection.appendChild(slot);
    page.appendChild(hgSection);
    host.body.replaceChildren(page);
    fillHepGraph(slot, authorId, hepGraphOutcome, { retry: askHepGraph });

    host.method.replaceChildren(
      h('h3', {}, 'The join'),
      h('p', {}, `The route carries one thing: the INSPIRE author record id (${authorId}). It is the id of an Atlas person (`
        + `person:inspire-${authorId}) and the id HEP Graph uses (/api/person/${authorId}). Neither side holds an institution `
        + 'or collaboration id for the other, so nothing else is joined.'),
      h('h3', {}, 'Inputs'),
      h('ul', {}, [
        h('li', {}, `The Atlas's people files, one per collaboration and institution (${plural(scan.bundleCount, 'file')} read): `
          + 'who is listed, at which institution, with which dates and evidence.'),
        h('li', {}, 'atlas.json and institutions.json: collaboration to experiments, experiments to detector sites, and the '
          + 'recorded coordinates of institutions and sites (campus-grade points, not building positions).'),
        h('li', {}, 'HEP Graph: GET /api/person/<id>?summary=1, the existing same-origin endpoint. Its affiliations are '
          + 'institution names that INSPIRE reports; they are shown as text and never matched to Atlas institutions.'),
      ]),
      h('h3', {}, 'What this does not say'),
      h('ul', {}, [
        h('li', {}, 'The rosters are partial. No row means unknown, not "no experiment".'),
        h('li', {}, 'A membership row is for a collaboration; the experiments listed are the ones the Atlas links to that '
          + 'collaboration, not a claim about each analysis the person has worked on.'),
        h('li', {}, 'A person’s other affiliations (for example a second institution on their INSPIRE profile) are not in '
          + 'the people files, so they are not on the map.'),
        h('li', {}, 'A failure of the Atlas’s files or of HEP Graph is shown as a failure, never as an empty list.'),
      ]),
      h('h3', {}, 'The map'),
      h('p', {}, 'Equirectangular projection (longitude and latitude drawn straight), coastline from Natural Earth 110m. '
        + 'Circles are institutions, diamonds are experiment sites; both open the Atlas record. “Show its institutions on the globe” opens collaboration mode, which draws every institution on the collaboration’s roster, this researcher’s included, and is offered only where the Atlas has a roster.'),
    );
    host.announce(rows.length
      ? `${name}: ${plural(rows.length, 'membership')} in the Atlas.`
      : `${name}: no membership recorded in the Atlas.`);
    return null;
  }

  await run();
  return { destroy() { alive = false; } };
}
