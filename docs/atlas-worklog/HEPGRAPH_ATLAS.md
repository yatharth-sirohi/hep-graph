# HEP Graph × Atlas (M6, workstream 4)

Scope: from a person in HEP Graph, their experiments and institutions on the Atlas;
from an Atlas experiment or collaboration, a route to its people in HEP Graph. Only as
far as the data supports it. No new database work, no INSPIRE traffic, no Neon.

## The join keys that exist

| Key | Atlas | HEP Graph |
| --- | --- | --- |
| INSPIRE **author** record id (`1005149`, the `recid` of `inspirehep.net/authors/<id>`) | `person:inspire-<recid>`; `external.inspire_author`; `src:inspire-author-<recid>` has that URL | the person id everywhere: `/api/person/<id>`, `?source=<id>`, the compact graph's `author_id` |
| INSPIRE **institution** record id | `institution.external.inspire_institution` on **28 of 529** institutions (the other 499 carry a ROR id, not an INSPIRE one) | **none**: no table, route or response carries an institution id |
| Collaboration / experiment name | `collaboration:*` (122), `experiment:*` (131), `experiment.external.inspire_experiment` | **none**: the compact tables hold `work_id, year, author_count, member_count` and `(work_id, author_id)` only. No collaboration tag, no names, no affiliations |

So the only usable join is the **author id**, in both directions. There is no
institution join and no collaboration join on the HEP Graph side.

## What each side can answer today

**Atlas, from its own bundles (no API, no database).**
`people/<collaboration>/<institution>.json` rows carry `id`, `name`, the collaboration
and institution of the membership, its dates and its evidence label. The generated build
has **12 people with INSPIRE author ids** (17 bundles, 5 collaborations: ATLAS, CMS, DUNE,
SBND, T2K). Each membership row joins to an institution (coordinates) and, through
`collaboration.experiment_ids`, to experiments and their detector sites. That is enough
to place a person on a map **if the Atlas has a row for them** (12 people today).
It is not enough for anyone else, and the Atlas bundle does not ship a person's
non-collaboration affiliations (a person file lists them, the people bundles do not).

**HEP Graph, from what exists.**
`GET /api/person/<id>?summary=1` returns `{status, person:{id, name, orcid, affiliations,
profile_status, source_url}}`. `affiliations` are **institution names** (INSPIRE
`positions`), fetched from INSPIRE at request time and held only in a process cache; the
database is not involved beyond "is this author in the release". Without a configured
database the route answers `503 {"status":"unavailable"}`; an author outside the release
answers `200 {"status":"not_found"}`; an upstream hydration failure answers a placeholder
(`details_unavailable`). It cannot list a collaboration's people, a person's experiments,
or anyone by institution.

## What it means for the two directions

**HEP Graph person -> Atlas.** A link "See on the HEP Atlas →" in the person panel to
`/atlas/#/view/person/<recid>`. (The panel is built in `static/app.js` `openProfile`;
`static/index.html` holds only its empty container, so the 10-line change is in `app.js`
and `index.html` is untouched.) The Atlas page joins the id to its own people bundles:

* found: institutions and experiments from the Atlas's own rows, drawn on a flat world map
  (each mark opens its Atlas record) and in a table with the evidence label per row. Where the
  collaboration has a roster, "Show its institutions on the globe" opens collaboration mode,
  which draws every institution on that roster (this person's included). The view itself is a
  full-stage page like the beam section; it is not drawn on the 3D globe, and the globe does
  not single out this person's institution;
* not found: **unknown, not none**. Twelve people are resolved; the rosters are partial;
  "no experiment recorded" is never shown as a fact;
* HEP Graph's own record of the person (name, INSPIRE-reported affiliation names) is
  shown beside it, *not* matched to Atlas institutions (names are not ids, and a
  guessed match would be a claim the data cannot back);
* the API or database being unavailable is an **error**: for an author the Atlas does not
  know it replaces the page (nothing else could be said); for one it does know, the
  Atlas's own rows still show and the HEP Graph part says plainly that it failed.

**Atlas experiment or collaboration -> HEP Graph people.** HEP Graph's front end accepts
only `source`, `target`, `with` (person ids) and the filters; it has **no query for a
collaboration, experiment or name**, and no endpoint lists a collaboration's people. So
the "People in HEP Graph →" section can only (a) open HEP Graph's person search, which
cannot be pre-filled with a collaboration name, and say that, and (b) list the few named
people the Atlas has matched to INSPIRE author ids for that collaboration, each linking to
`/?source=<recid>` and to the Atlas person page. Both are labelled partial.

## Out of scope (needs new work, and database growth is not allowed)

* Tagging works or authors with collaborations in the compact graph (the HEP Graph
  response for "people of ATLAS" would need it).
* Institution ids in HEP Graph responses; an institution join for the 28 + 499 records.
* A build-time id -> bundles index. The person page scans the manifest's `people/`
  bundles (17 files today). That is fine at this size; past a few hundred bundles the
  build should emit `people/index.json` instead.
* Non-collaboration affiliations from person files (`affiliations[]`): not in the shipped
  bundles.
