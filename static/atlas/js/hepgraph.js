// hepgraph.js — the Atlas side of "HEP Graph x Atlas" (docs/atlas-worklog/HEPGRAPH_ATLAS.md).
//
// The one join key between the two products is the INSPIRE *author* record id
// (`person:inspire-1005149` here, `/api/person/1005149` and `?source=1005149` there).
// HEP Graph carries no institution or collaboration id, so nothing here joins on one.
//
// Used by the person view (views/person.js) and by the collaboration and experiment
// panels (panels.js). Nothing is drawn here; every failure is thrown, never turned
// into an empty answer.

import * as loader from './loader.js';

export const PERSON_VIEW = 'person';
/** The owner names features: the working title, and the only place it is written. */
export const PERSON_VIEW_TITLE = 'Researcher on the Atlas';

/** `1005149`, `inspire-1005149` or `person:inspire-1005149` -> `'1005149'`; else null. */
export function parseAuthorId(arg) {
  let text = String(arg == null ? '' : arg).trim();
  try { text = decodeURIComponent(text); } catch (error) { /* a stray % is not an id */ }
  const match = /^(?:person:)?(?:inspire-)?([1-9][0-9]{0,11})$/.exec(text);
  return match ? match[1] : null;
}

/** The author id of an Atlas person id, or null for an unresolved person. */
export function authorIdOf(personId) {
  const match = /^person:inspire-([1-9][0-9]{0,11})$/.exec(String(personId || ''));
  return match ? match[1] : null;
}

export const personViewRoute = (authorId) => ({ type: 'view', slug: `${PERSON_VIEW}/${authorId}` });

/** HEP Graph's front end restores `?source=<id>` into its "From" field. */
export const hepGraphPersonUrl = (authorId) => `/?source=${authorId}`;

/** HEP Graph's front end has no query for a collaboration, experiment or name. */
export const HEP_GRAPH_SEARCH_URL = '/';

/** The manifest's `people/...` bundle paths, for one collaboration or all of them. */
export async function peopleBundlePaths(collaborationId = null) {
  const manifest = await loader.getManifest();
  const bundles = manifest && manifest.bundles;
  // A manifest that cannot list its bundles cannot say there are none.
  if (!bundles || typeof bundles !== 'object') throw new Error('the data manifest does not list its bundles');
  const names = Array.isArray(bundles) ? bundles : Object.keys(bundles);
  const prefix = collaborationId ? `people/${String(collaborationId).split(':')[1]}/` : 'people/';
  return names.filter((name) => name.startsWith(prefix)).sort();
}

/** Every person row of the people bundles, each with the collaboration and institution of
 * the bundle it came from (the generated bundles keep those on the bundle, the fixtures on
 * the row as well). Throws if any listed bundle cannot be read: a partial scan would turn
 * a failure into "this person is not listed". */
export async function rosterPeople(collaborationId = null) {
  const paths = await peopleBundlePaths(collaborationId);
  const bundles = await Promise.all(paths.map((path) => loader.getPeople(path)));
  const rows = [];
  bundles.forEach((bundle, index) => {
    if (!bundle) throw new Error(`the people file ${paths[index]} is listed but could not be read`);
    for (const person of bundle.people || []) {
      rows.push({
        ...person,
        collaboration_id: person.collaboration_id || bundle.collaboration_id || null,
        institution_id: 'institution_id' in person ? person.institution_id : (bundle.institution_id || null),
      });
    }
  });
  return { rows, bundleCount: paths.length };
}

/**
 * HEP Graph's record of an author, from the existing same-origin endpoint
 * `/api/person/<id>?summary=1`:
 *   { state: 'ok', person }        name, orcid, affiliations (INSPIRE institution *names*)
 *   { state: 'not_in_release' }    HEP Graph's release does not include this author
 *   { state: 'details_unavailable', reason }   in the release, details could not be fetched
 * Anything else (no database configured, a failing store, rate limit, no answer) throws:
 * that is an error, never "no data".
 */
export async function fetchHepGraphPerson(authorId) {
  let response;
  try {
    response = await window.fetch(`/api/person/${encodeURIComponent(authorId)}?summary=1`, {
      headers: { Accept: 'application/json' },
    });
  } catch (error) {
    throw new Error('the HEP Graph service did not answer');
  }
  let body = null;
  try {
    body = await response.json();
  } catch (error) {
    body = null;
  }
  if (response.ok && body && body.status === 'not_found') return { state: 'not_in_release' };
  if (response.ok && body && body.status === 'ok' && body.person) {
    if (body.person.details_unavailable) {
      return { state: 'details_unavailable', reason: body.person.reason || 'unknown' };
    }
    return { state: 'ok', person: body.person };
  }
  const message = body && typeof body.message === 'string' && body.message ? body.message : `HTTP ${response.status}`;
  throw new Error(message);
}
