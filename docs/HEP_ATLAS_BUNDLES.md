# HEP Atlas generated bundles (v0.2)

`hepgraph/atlas/build.py` turns `data/atlas/` into the files under
`static/atlas/generated/`.  **This document is the contract the globe frontend
codes against.**  The ontology (`docs/HEP_ATLAS_ONTOLOGY.md`, amendments
A1-A22) governs the *input*; this governs the *output*.

Rules that hold for every bundle:

* **Canonical JSON.** `json.dumps(sort_keys=True, indent=2, ensure_ascii=False)`
  plus a trailing newline (A11).  Byte-for-byte deterministic: two builds of
  the same data produce identical files.  `build.py --check` rebuilds into a
  temporary directory and fails when anything differs.
* **No provenance in the hot path.** `atlas.json` carries *stripped* values
  only.  `sources`, `verified_at`, `confidence`, `note`, `quote` and `locator`
  for every field move to the lazily loaded `provenance.json` (A14).
* **Derived fields are added here, never authored.** Inverse relations (A1),
  `status`, `state_segments`, `hep_graph`, source `rank` and `cited_by`,
  coverage `validated` / `globe_ready`, and the A25 map links
  `facility.map_id`, `site.map_id` and
  `{accelerator,beamline,detector}.geometry_map_ids`.
* **Months.** Every month index is *months since 1950-01*
  (`(year - 1950) * 12 + (month - 1)`).  Dates before 1950 give negative
  indices; nothing is clamped.  `manifest.epoch` states the epoch.
* **Size.** The build fails when `atlas.json` exceeds 1 500 000 bytes and
  prints a per-type size table; the pilot budget is 400 KB for
  `atlas.json` + `manifest.json` together.  A `geometry/<slug>.json` bundle
  fails the build above 2 000 000 bytes (A25).

## Caching (closes P2-2 / part of P1-2 in `REVIEW_performance.md`)

Every response under `/atlas/**` — the app shell, vendored JS, and every
generated bundle — is served by one Python handler,
`hepgraph.server.Handler.respond_atlas`, in both places this runs:

* locally, via `python -m hepgraph.server`;
* in production, because `pyproject.toml` names `hepgraph.server:Handler` as
  the entry point Vercel's Python runtime loads (see
  `docs/VERCEL_SEARCH_EXECUTION_AUDIT.md` §"Runtime"). `vercel.json` carries
  no `routes`/`headers`/static-build config of its own, so there is no
  separate static-hosting layer with independent caching rules to keep in
  sync with the Python one.

Because both environments are the same code path, the bundle-versioning
question (revalidation vs. immutable content-hashed URLs) has one answer
instead of two designs to keep aligned. This build picked **ETag
revalidation over content-hashed URLs**:

* `respond_atlas` computes a strong ETag (`"` + first 32 hex chars of the
  SHA-256 of the file's bytes + `"`) for every file it serves, cached
  in-process keyed by `(path, mtime_ns, size)` so an unchanged file is not
  re-hashed on every request.
* Every response carries `Cache-Control: public, max-age=0, must-revalidate`
  — always revalidate, never serve a bundle that is more than one round
  trip stale.
* A request with a matching `If-None-Match` gets a bodyless `304`; a stale
  or absent one gets the normal `200` with the full bytes and a fresh ETag.

This was chosen over content-hashed, immutably-cached URLs
(`atlas.<hash>.json`, `Cache-Control: max-age=31536000, immutable`) because
that design needs `build.py` (owned by another workstream during this pass)
to rewrite every bundle reference in `manifest.json`/`index.html`/`loader.js`
to a hashed path, and needs a second, unhashed manifest URL to bootstrap the
lookup — real value once the build genuinely never touches an old path
byte-for-byte, but more moving parts than this pass's scope of
`loader.js`/`server.py` justified. Revalidation gets the same practical
result for this app (an unchanged reload costs one small request instead of
re-downloading ~4.9 MB of bundles) with a change contained to the server and
the loader's fetch options. Revisit content-hashed URLs if the entity that
owns `build.py` wants immutable, CDN-cacheable bundle URLs independent of a
live round trip.

`static/atlas/js/loader.js` fetches every bundle without `cache: 'no-store'`
now (default browser cache mode), so the conditional-GET machinery above is
actually used; `manifest.json` is fetched the same way — "revalidated", per
the product requirement, means the browser always asks the server whether
its copy is current, which `max-age=0, must-revalidate` guarantees regardless
of cache mode.

## Stripping rules

| input shape | shape in `atlas.json` |
| --- | --- |
| Sourced value `{"value": V, "sources": …}` | `V` |
| SList `[Sourced<T>, …]` | `[T, …]` |
| Quantity | `{"value", "unit", "dimension", "display", "approx"}` (`min`/`max` instead of `value` for a range) |
| Coordinates | `{"lat", "lon", "precision_m", "kind"}` plus `"approximate": true` when the canonical confidence is approximate/uncertain (A23); the globe draws such points in the approximate style and the panel says "Approximate location" |
| Interval | `{"label", "status", "start", "end", "kind"}` (`specs` kept when present) |
| Date object `{"date": D, …}` | `D` when it carries no qualifier, else `{"date", "approx", "planned", "display"}` |
| Placement / facility role / leadership / lineage / membership row | its non-provenance keys |

A stripped `start` / `end` is always the plain `"YYYY[-MM[-DD]]"` string or a
date object as above, never a `ParsedDate`.

## Provenance pointers

`provenance.json` is keyed by entity id, then by a **JSON pointer into the
authored record** (RFC 6901: `/` separated, array indices are numbers).

```
"experiment:demo": {
  "/key_specs/0/quantity": {
    "sources": ["src:demo-tdr"], "verified_at": "2026-09-16",
    "confidence": "verified", "note": "", "quote": null, "locator": "Vol. I §1.2"
  }
}
```

Membership rows live under the collaboration id with pointers of the form
`/members/3`; person rows under the person id (`/memberships/0`).

---

## `manifest.json`

Loaded first, on every page view.

```json
{
  "schema": "hep-atlas/0.2",
  "version": "9f2c4d6a1b0e5837",
  "build_date": "2026-09-16",
  "epoch": {"year": 1950, "month": 1},
  "counts": {
    "facilities": 1, "sites": 2, "accelerators": 1, "beamlines": 1,
    "experiments": 1, "detectors": 1, "collaborations": 1, "institutions": 2,
    "people": 2, "results": 1, "documents": 1, "topics": 3, "sources": 8,
    "memberships": 1, "coverage": 1
  },
  "timeline": {"min_month": 210, "max_month": 920, "min_year": 1967, "max_year": 2026},
  "bundles": {
    "atlas.json": {"bytes": 23456, "sha256": "…"},
    "memberships/demo.json": {"bytes": 1234, "sha256": "…"}
  }
}
```

`version` is the first 16 hex characters of the SHA-256 of every generated
file's content except `manifest.json` itself, so it changes exactly when the
data changes.  `timeline.min_month` / `max_month` span every entity's
`state_segments`.

## `atlas.json`

Loaded first.  One key per entity type, each an object keyed by id.

```json
{
  "schema": "hep-atlas/0.2",
  "version": "9f2c4d6a1b0e5837",
  "build_date": "2026-09-16",
  "facilities": {"facility:demo-lab": { … }},
  "sites": {"site:demo-lab-campus": { … }},
  "accelerators": { … }, "beamlines": { … }, "experiments": { … },
  "detectors": { … }, "collaborations": { … }, "topics": { … },
  "maps": {"map:demo-lab": { … }}
}
```

`institutions`, `results`, `documents`, `sources` and people are **not** in
`atlas.json`; they have their own bundles.  Long text is not here either
(see `text.json`); `summary.plain` stays.

A record, using `experiment:demo` (abridged, real fixture output):

```json
{
  "id": "experiment:demo",
  "type": "experiment",
  "name": "Demo Experiment",
  "aliases": ["DEMO", "Demo Neutrino Experiment"],
  "summary": {"plain": "A fictional long-baseline neutrino experiment used to test the atlas."},
  "kind": "accelerator_neutrino",
  "secondary_kinds": ["atmospheric_neutrino"],
  "collaboration_ids": ["collaboration:demo"],
  "facility_roles": [{"facility_id": "facility:demo-lab", "role": "host", "start": null, "end": null}],
  "facility_ids": ["facility:demo-lab"],
  "beamline_ids": ["beamline:demo-beam"],
  "accelerator_ids": [{"id": "accelerator:demo-synchrotron", "start": "2010-03", "end": null}],
  "topic_ids": ["topic:neutrino-oscillations", "topic:cp-violation-leptons"],
  "intervals": [
    {"label": "proposal", "status": "proposed", "start": "2005", "end": "2008", "kind": "lifecycle"},
    {"label": "Run 2", "status": "active", "start": "2017", "end": null, "kind": "run"}
  ],
  "state_segments": [[660, 671, "proposed", "possible"], [816, 920, "active", "certain"]],
  "status": "active",
  "key_specs": [
    {"label": "Baseline",
     "quantity": {"value": 1285, "unit": "km", "dimension": "length", "display": "~1300 km", "approx": true}}
  ],
  "lineage": [],
  "external": {"inspire_experiment": 1234567, "greybook": "DEMO", "wikidata": null},
  "site_ids": ["site:demo-far-cavern"],
  "detector_ids": ["detector:demo-far-detector"],
  "result_ids": ["result:demo-oscillation-observation-2020"],
  "document_ids": ["document:demo-tdr"],
  "coverage": {"tier": "A", "researched": "full", "validated": true, "globe_ready": true}
}
```

* `state_segments` is `[[m0, m1, status, certainty], …]`, both months
  inclusive, contiguous runs of equal `(status, certainty)` over the entity's
  existence hull (A3).  `status` may be `"unrecorded"`.  `certainty` is
  `"certain"` or `"possible"` (hatched).
* `status` is the derived state at the build date, which A10 requires to equal
  the authored `status`.
* Derived inverse lists, added per A1:
  `facility`: `site_ids`, `accelerator_ids`, `beamline_ids`, `institution_id`,
  `experiment_ids`, `document_ids`;
  `accelerator`: `beamline_ids`, `serves_experiment_ids`,
  `fed_by_accelerator_ids`, `document_ids`;
  `beamline`: `experiment_ids`, `document_ids`;
  `experiment`: `facility_ids`, `site_ids`, `detector_ids`, `result_ids`,
  `document_ids`, plus inverse `lineage` rows (`successor`, `upgraded_to`, and
  the mirror of `same_program` / `complementary`);
  `detector`: `document_ids`;
  `collaboration`: `experiment_ids`, `document_ids`;
  `site`: `document_ids`.

## `provenance.json`

Loaded on first panel open.  `{entity_id: {json_pointer: record}}`, where the
record is `{"sources", "verified_at", "confidence", "note", "quote",
"locator"}` with `null` for anything the author did not give.

## `text.json`

Loaded on first panel open.  `{entity_id: {field: value}}` for the long-text
fields of `schema.LONG_TEXT_FIELDS`:

```json
{
  "experiment:demo": {
    "summary_technical": "Long-baseline nu_mu -> nu_e appearance with a 10 kt LArTPC far detector.",
    "notes": [],
    "physics_goals": ["Measure delta_CP", "Determine the neutrino mass ordering"],
    "unique_capabilities": ["Wide-band beam with a 1285 km baseline"]
  },
  "topic:neutrino-physics": {"overview": "Neutrinos are neutral leptons interacting only weakly."}
}
```

## `results.json`

```json
{"result:demo-oscillation-observation-2020": {
  "id": "result:demo-oscillation-observation-2020",
  "type": "result",
  "name": "Observation of demo oscillations",
  "title": "Observation of demo oscillations",
  "result_type": "observation",
  "date": "2020-03-15",
  "date_kind": "publication",
  "month": 843,
  "announced": "2020-02-11",
  "published": "2020-03-15",
  "experiment_ids": ["experiment:demo"],
  "collaboration_ids": ["collaboration:demo"],
  "facility_ids": ["facility:demo-lab"],
  "detector_ids": ["detector:demo-far-detector"],
  "topic_ids": ["topic:neutrino-oscillations"],
  "key_value": null,
  "key_value_text": "sin^2(2 theta) = 0.5",
  "significance": "5.2σ",
  "publication": {"doi": "10.0000/demo-result", "arxiv": "2003.00001", "inspire": 1790000},
  "official_url": "https://example.org/demo-experiment/results/2020",
  "official_url_kind": "official",
  "hepdata": null,
  "summary": {"plain": "The experiment saw neutrinos change type over 1300 kilometres."}
}}
```

`month` is the result date in months since the epoch, so the slider can filter
without re-parsing dates.  `claim`, `why_it_matters` and the technical summary
are in `text.json`.

`official_url_kind` (added for A4) is derived, never authored: `null` when
`official_url` is absent, else `"arxiv"` or `"doi"` when the URL normalises to
the same target as `publication.arxiv` (an `arxiv.org/abs/<id>` or `/pdf/<id>`
link, any version suffix) or `publication.doi` (a `doi.org/<doi>` link,
case-folded), else `"official"`. This lets the panel avoid showing the same
target twice under both its real link and a redundant "Official page" —
across the generated bundle 37 of 109 results had `official_url` equal to
their own arXiv link before this was added.

## `documents.json`

`{document_id: stripped record}` — `doc_type`, `date`, `owner_ids`,
`reference`, `volumes`, `source_id`, `name`, `summary.plain`.

## `sources.json`

```json
{"src:demo-tdr": {
  "id": "src:demo-tdr",
  "type": "src",
  "source_type": "design_report",
  "rank": 4,
  "title": "Demo Experiment Technical Design Report",
  "publisher": "Demo Collaboration",
  "url": "https://doi.org/10.0000/demo-tdr",
  "archive_url": null,
  "accessed": "2026-09-16",
  "date": "2015-06",
  "excerpt": "The far detector holds 10 kt of liquid argon.",
  "retrieval": "full_text",
  "link_check": {"last_checked": null, "http_status": null, "redirect": null},
  "cited_by": {"experiment:demo": ["/key_specs/0/quantity", "/intervals/1"]}
}}
```

`rank` is always the derived A18 rank of `source_type`; whatever the file said
is ignored.  `cited_by` maps each citing entity id to the sorted list of JSON
pointers that cite it (record-level citations use the pointer `"/sources"`).

## `institutions.json`

`{institution_id: stripped record}` with `coordinates`, `place`, `country`,
`countries`, `kind`, `external`, `facility_id`, `parent_institution_id`,
`name`, `aliases`, `summary.plain`, and the derived
`collaboration_ids` this institution is a member of.

## `memberships/<collaboration-slug>.json`

Loaded when a collaboration is selected.

```json
{
  "collaboration_id": "collaboration:demo",
  "as_of": "2026-09",
  "membership_history": "partial",
  "roster_sources": ["src:demo-institution-list"],
  "roster_snapshots": [{"as_of": "2026-09"}],
  "formation": "2005-06",
  "counts": {"confirmed": 2, "undated": 0},
  "members": [
    {
      "institution_id": "institution:university-of-iowa",
      "name": "University of Iowa",
      "country": "US",
      "coordinates": {"lat": 41.6611, "lon": -91.5302, "precision_m": 100, "kind": "campus"},
      "start": null, "end": null,
      "known_since": "2012", "known_until": "2026-09",
      "known_since_month": 744, "known_until_month": 920,
      "evidence_class": "official_institution_list",
      "evidence_label": "On the official institution list (as of 2026-09)",
      "render": "solid",
      "counted": true,
      "note": "join date not published; first seen on the 2012 roster",
      "source_index": 0
    }
  ]
}
```

`source_index` is this row's position in the *authored* roster file, before
the display sort below reorders `members`. The collaboration's provenance
pointers (`/members/3`) are RFC 6901 pointers into that authored order, so a
client resolving one into an institution name (Task A4's claim labels) must
look up `source_index === 3`, not array position 3 of the sorted list.

`render` / `counted` / `counts` are evaluated **at the build date**; the
frontend recomputes them per slider year with the A5 rule using `start`,
`end`, `known_since`, `known_until`, `as_of` and `membership_history`.
`evidence_label` is the exact A19 wording with its placeholders filled.
A member whose institution has no coordinates keeps its row (with
`"coordinates": null`) and is simply not drawn.

## `people/<collaboration-slug>/<institution-slug>.json`

Loaded when an institution dot is clicked.  Rows whose membership names no
institution go to `people/<collaboration-slug>/_unknown.json`.

```json
{
  "collaboration_id": "collaboration:demo",
  "institution_id": "institution:university-of-iowa",
  "people": [
    {
      "id": "person:inspire-1019647",
      "name": "Demo Spokesperson",
      "start": "2012", "end": null,
      "evidence_class": "official_roster",
      "evidence_label": "On the collaboration's own member list (as of 2026-09)",
      "evidence_date": "2026-09",
      "hep_graph": {"available": true, "url": "/?source=1019647&mode=live"}
    }
  ]
}
```

`hep_graph.url` exists only for `person:inspire-*` ids; an unresolved person
gets `{"available": false}` and no URL.


## `atlas.json` &rarr; `maps` (A25)

One entry per local map, keyed by `map:<slug>`.  Present and empty when no
campus has been researched, so the frontend can rely on the key.

```json
"map:demo-lab": {
  "id": "map:demo-lab",
  "name": "Demo Laboratory \u2014 main campus",
  "facility_id": "facility:demo-lab",
  "site_ids": ["site:demo-lab-campus"],
  "center": {"lat": 41.8325, "lon": -88.2525},
  "extent_m": 3000,
  "levels": [{"id": "surface", "name": "Surface", "kind": "surface", "depth_m": null},
             {"id": "ring-tunnel", "name": "Synchrotron tunnel (9 m below grade)",
              "kind": "underground",
              "depth_m": {"value": 9, "unit": "m", "dimension": "length", "display": "9 m",
                          "approx": false}}],
  "feature_count": 4,
  "to_scale_count": 3,
  "unlocated_count": 1,
  "linked_map_ids": [],
  "attribution": ["\u00a9 OpenStreetMap contributors (ODbL-1.0)"],
  "bundle": "geometry/demo-lab.json",
  "coverage": {"tier": "A", "researched": "partial"},
  "state_segments": [[214, 214, "active", "possible"], [215, 920, "active", "certain"]],
  "status": "active"
}
```

* `center` is the stripped Coordinates reduced to `lat`/`lon`; its kind,
  precision and sources are in `provenance.json` at `/center`.  It is the
  default camera position, nothing more.
* `levels[].depth_m` strips like any Quantity: numbers here, sources in
  `provenance.json`.
* `to_scale_count` excludes `inferred_direction` features, which are
  directions rather than structures.
* `linked_map_ids` is the authored list **union** the derived ones: the map
  of any far site a beamline of this facility points at, and the map of any
  `related_facility_ids` entry that has one.
* `attribution` is the sorted unique `"<attribution> (<licence name>)"` of
  every feature that carries a licence; the browser shows it on the map.
* `state_segments` and `status` are the **facility's**.  A map is a view of a
  facility and never claims a history of its own.

## `geometry/<map-slug>.json` (A25)

Lazy, one per map, loaded only when a `#/map/<slug>` route opens.  The build
fails when one exceeds 2 MB.

```json
{
  "schema": "hep-atlas/0.2",
  "version": "9f2c4d6a1b0e5837",
  "build_date": "2026-09-16",
  "map": { "…the stripped map record…",
           "unlocated": [{"entity_id": "experiment:demo", "entity_name": "Demo Experiment",
                          "entity_type": "experiment", "reason": "…", "backlog": "…",
                          "sources": ["src:demo-experiment-site"]}],
           "schematics": [{"title": "… (schematic, not to scale)", "url": "https://…",
                           "source_id": "src:demo-lab-site", "note": "…"}] },
  "bbox": [-88.2787324, 41.8287752, -88.2481587, 41.8382248],
  "attribution": ["\u00a9 OpenStreetMap contributors (ODbL-1.0)"],
  "features": [{
    "id": "geometry:demo-synchrotron-ring",
    "name": "Demo Synchrotron tunnel, full ring",
    "feature_type": "ring", "level_id": "ring-tunnel",
    "entity_id": "accelerator:demo-synchrotron", "entity_type": "accelerator",
    "entity_name": "Demo Synchrotron", "site_id": "site:demo-lab-campus",
    "representation": "derived", "accuracy_m": 120, "method": "…", "depth_m": null,
    "geometry": {"type": "LineString", "coordinates": [[-88.2545, 41.8382248], …]},
    "measured": {"length_m": 3300.0007, "area_m2": null, "centroid": [-88.2545, 41.8335]},
    "checks": [{"kind": "length", "expected_m": 3300.0, "measured_m": 3300.0007,
                "unit": "m", "tolerance": 0.02, "passed": true,
                "sources": ["src:demo-lab-site"]}],
    "state_segments": [[588, 599, "active", "possible"], …], "status": "active",
    "provenance": {"sources": ["src:demo-lab-site"], "verified_at": "2026-09-16",
                   "confidence": "derived", "locator": "…", "quote": null, "note": "…"},
    "license": null, "osm": null
  }],
  "source_titles": {"src:demo-lab-site": {"title": "…", "url": "https://…",
                                          "source_type": "official_facility_site"}},
  "entity_index": {"accelerator:demo-synchrotron": ["geometry:demo-synchrotron-ring"]}
}
```

* `features` are sorted by `id`.  Coordinates are emitted with **7 decimals**
  (about 11 mm), which is what makes the bundle byte-deterministic.
* `geometry` is the **bare GeoJSON object** — the authored value's `sources`,
  `confidence`, `locator`, `quote` and `note` are in `provenance` on the same
  feature (a geometry bundle is already lazy, so its provenance travels with
  it rather than going to `provenance.json`).
* `measured` is recomputed by the build, never authored: geodesic length (a
  polygon's is its outer-ring perimeter), spherical-excess area, and a
  representative centroid.
* `checks[].expected_m` and `measured_m` are in the base unit of the kind —
  metres, square metres, or **degrees** for an `azimuth`; `unit` says which.
  `passed` is `true`/`false`, and `null` only for a row that could not be
  executed (which the validator reports as an error, so it should never
  reach a committed bundle).
* `state_segments` come from the feature's own `valid` window when it has one
  (the entity's segments clipped to the window; uncovered months are `unrecorded` — a window is a structure's lifetime, never an operating state), otherwise from the entity it depicts.  A
  context feature with neither is `null` and is drawn in every year.
* `bbox` is `[minLon, minLat, maxLon, maxLat]` over every feature, `null`
  when the map draws nothing yet.
* `source_titles` covers every source cited anywhere in the bundle — features,
  checks, unlocated rows, level depths, schematics and the map record — so
  the panel can name a source without loading `sources.json`.
* `entity_index` maps an entity id to the features that depict it, so the
  drawer can highlight every shape of one machine at once.  Context features
  depict nothing and are absent from it.

## `search.json`

```json
{"schema": "hep-atlas/0.2",
 "entries": [["experiment", "experiment:demo", "Demo Experiment",
              ["DEMO", "Demo Neutrino Experiment"], "Accelerator neutrino · Demo Laboratory"]]}
```

Each entry is `[type, id, name, aliases, subtitle]`.  **People are never in
`search.json`** (A14): person search is delegated to HEP Graph live search.
Sorted by `(type, id)`.

A25 adds `map` entries, whose subtitle is `"Local map · <facility name>"`:

```json
["map", "map:demo-lab", "Demo Laboratory — main campus", [], "Local map · Demo Laboratory"]
```

## `graph.json`

```json
{"schema": "hep-atlas/0.2",
 "edges": [
   {"type": "USES_BEAMLINE", "from": "experiment:demo", "to": "beamline:demo-beam",
    "start": "2010-03", "end": null, "start_month": 723, "end_month": null},
   {"type": "MEMBER_OF", "from": "institution:university-of-iowa", "to": "collaboration:demo",
    "start": "2012", "end": null, "start_month": 744, "end_month": null}
 ]}
```

Edge types are those of ontology §7.  An edge's interval is the **explicit
object form** when the authored `*_ids` entry carried `start`/`end` (A9),
otherwise the intersection of the two endpoints' existence hulls; the months
are the month indices of `lo(start)` and `hi(end)` (`null` for an open end).
Edges are sorted by `(type, from, to)`.

## `coverage.json`

```json
{"schema": "hep-atlas/0.2",
 "rows": [{
   "name": "Demo", "entity_id": "experiment:demo", "category": "accelerator_neutrino",
   "facility": "Demo Laboratory", "status": "active", "tier": "A", "priority": 1,
   "researched": "full", "missing_fields": [], "owner": "fixture", "notes": "",
   "validated": true, "globe_ready": true
 }]}
```

`data/atlas/coverage/*.json` are merged; a duplicate `entity_id` fails the
build.  `validated` and `globe_ready` are **build outputs** (A10):

* `validated` — the entity exists and the validator reports no *error*
  attributed to it;
* `globe_ready` — `validated`, and the experiment resolves to at least one
  site with coordinates whose `kind` is `detector` or `underground_lab`, and
  it has at least one interval with a known start.

A25 adds two more keys alongside `rows`:

```json
{"maps": [{"map_id": "map:demo-lab", "name": "Demo Laboratory — main campus",
           "facility_id": "facility:demo-lab", "feature_count": 4,
           "representations": {"surveyed": 1, "georeferenced": 1,
                               "derived": 1, "inferred_direction": 1},
           "unlocated_count": 1, "checks_passed": 1, "checks_failed": 0}],
 "facilities_without_a_map": [{"facility_id": "facility:cern", "name": "CERN"}]}
```

`facilities_without_a_map` names every facility nobody has drawn.  That is
not a defect — it is the only way the coverage report cannot quietly read as
though the atlas maps everything it contains.
