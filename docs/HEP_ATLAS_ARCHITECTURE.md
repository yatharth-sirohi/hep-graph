# HEP Atlas architecture

HEP Atlas is a source-backed geographic and historical knowledge graph of
experimental high-energy physics. Its primary visualisation is a globe, but the
globe is a view over the graph, not the product. HEP Graph — the existing
researcher-to-researcher network over live INSPIRE data — is unchanged by it and
remains the people layer; the two connect through INSPIRE author identifiers.

```text
HEP Atlas
├── People        → HEP Graph (live INSPIRE, existing app)
├── Globe         → facilities, sites, experiments, collaborations, institutions
├── Research      → hierarchical topics
├── Major Results → curated, sourced result registry
└── History       → intervals on every entity and relationship
```

## 1. Layers

| Layer | Where | Nature |
| --- | --- | --- |
| Canonical data | `data/atlas/**/*.json` | Human-reviewed, one file per entity, diffable, provenance-carrying |
| Schema and rules | `hepgraph/atlas/schema.py` | Enums, units, date/interval semantics, derived-state rules |
| Geometry | `hepgraph/atlas/geo.py` | Geodesy and GeoJSON for the local-map layer: lengths, perimeters, spherical areas, centroids, azimuths, bbox, validation, simplification (A25) |
| Loader | `hepgraph/atlas/load.py` | Reads the canonical tree into a typed in-memory model |
| Validator | `hepgraph/atlas/validate.py` | Structural, referential, temporal, provenance, geometric and unit checks |
| Build | `hepgraph/atlas/build.py` | Generates the browser bundles under `static/atlas/generated/` |
| Link checker | `hepgraph/atlas/linkcheck.py` | Manual, polite; records link status back into source records |
| OSM extractor | `scripts/atlas_osm_extract.py` | Manual, one Overpass request; writes *draft* geometry records a researcher finishes by hand (A25) |
| Scaffold | `hepgraph/atlas/scaffold.py` | Creates skeleton files so adding an experiment is one command |
| Server | `hepgraph/server.py` | Additive routes `/atlas` and `/atlas/<file>`; no change to HEP Graph routes |
| Browser app | `static/atlas/` | Vanilla HTML/CSS/JS, vendored WebGL library, no build step |

The canonical data is never read by the browser. The browser reads only
generated bundles, so runtime browsing makes essentially no external requests
— in deliberate contrast to HEP Graph, whose pathfinding is live against
INSPIRE.

**One exception, added with the local-map layer (A25):** a local map route
(`#/map/<slug>`) offers OpenStreetMap standard basemap tiles behind the
to-scale geometry, which are fetched from `openstreetmap.org` while that
route is open. They are optional and toggleable (`bm=0` hides them), need no
API key and cost nothing; on tile failure the features still render on the
dark background and a notice says the basemap is unavailable. Nothing else in
the application fetches anything at runtime, and no other route loads tiles.
The geometry itself is atlas data and is never fetched from a third party at
runtime — it is built into `geometry/<slug>.json` like every other bundle.

## 2. Ontology

The full contract is `docs/HEP_ATLAS_ONTOLOGY.md`; the v0.2 amendment block at
its top is normative where it differs from the body. In summary:

- **Entities**: facility, site, accelerator, beamline, experiment, detector,
  collaboration, institution, person, result, document, topic, source.
- **Facility ≠ institution ≠ collaboration.** CERN is a facility, an
  institution and a collaboration member, with three ids and three roles.
- **Geography lives on sites.** An experiment has `facility_roles` (host, beam
  source, detector host, prototype host); a detector has `placements` with role
  and dates, so ICARUS can sit at Gran Sasso, then CERN, then Fermilab.
- **Relations have one canonical direction**; inverses are derived at build
  time, so two agents editing different partitions cannot desynchronise them.
- **Specs are typed quantities** with dimension and unit, not free text, so a
  1300 m versus 1300 km error is mechanically detectable.
- **Provenance is a value type.** Critical facts carry `sources`,
  `verified_at`, `confidence` and a claim-level `quote` or `locator`.
- **Membership carries an evidence class** — official roster, official
  institution list, INSPIRE author profile, current or historical publication
  affiliation, institutional page, self-reported, derived — and the interface
  says which one it is in words.

## 3. Temporal model

Every entity carries intervals with status, start, end, precision and sources.
Dates are strings whose precision is their length, optionally with `earliest`,
`latest`, `display` and a `planned` flag meaning "this comes from a schedule".

At build time each entity is reduced to `state_segments`: run-length-encoded
`[m0, m1, status, certainty]` in months since 1950-01. The slider, range mode,
playback and the historical tests all read that one structure.

- **Presence** is the existence hull from the earliest start to the earliest
  terminal event (or the build date).
- **State** at a time is chosen among covering intervals: operational statuses
  beat proposed/planned, then the latest start wins, then a fixed rank.
- **Certainty** is `certain` when the whole selection lies inside the interval
  at its stated precision, otherwise `possible`, which the globe hatches.
- Open intervals extend to the build date, not to the date someone verified
  them, so two records verified months apart behave identically.

This is what makes "show me 1995" defensible: nothing is displayed as operating
unless a sourced interval says it was.

## 4. Provenance and the source hierarchy

Sources are records with a type whose rank is derived, an access date, and a
retrieval mode (full text, partial, summary, failed). A value may not cite a
source that failed to retrieve, and a verbatim quote may not come from a
summarised retrieval. Rank ordering runs from the official experiment site
through laboratory sites, experiment registries, design reports, detector
papers, HEPData and the Particle Data Group, to journals and, last, secondary
sources. A `verified` value must cite something better than a secondary source.

The build splits provenance out of the main bundle into `provenance.json`,
keyed by entity and JSON pointer, so the globe stays small while every claim in
a panel can still be expanded to "why is this here".

## 5. Ingestion pipeline

```text
research agent (writes JSON + sources)
      ↓  validator (structure, references, time, units, geometry, provenance)
domain review  →  independent verifier (different agent, re-opens the sources)
      ↓  build (bundles, derived inverses, state segments, coverage outputs)
functional / UX / performance testing
      ↓  release
```

Adding an experiment is: `python -m hepgraph.atlas.scaffold experiment <slug>`,
fill the skeleton, add sources, validate, build. The coverage registry records
what is covered and what is only identified; `data/atlas/coverage/backlog.json`
holds every experiment named in the coverage scope that has not been researched
yet, so incompleteness is visible rather than implied.

## 6. Frontend rendering

The library choice and its justification are in
`docs/HEP_ATLAS_GLOBE_LIBRARY.md`. The application is plain modules loaded by
`static/atlas/index.html`: data loader, hash router and URL state, globe
renderer, timeline, detail panels, collaboration mode, topic mode, results
mode, search, and a non-WebGL fallback that renders the same data as lists and
tables. Bundles load lazily: the globe needs the manifest and `atlas.json`;
text, provenance, results, documents, institutions, memberships and people
arrive only when something asks for them. A collaboration's people are fetched
per institution, so ATLAS-scale rosters never load at once.

### 6b. Local map view

The to-scale campus view (`#/map/<facility-slug>`) implements
`docs/HEP_ATLAS_GEOMETRY.md` §4. It is a separate surface from the globe, not
a zoom level of it: the globe is a sphere of facilities; this is a Web
Mercator plan of one campus with a metre scale bar.

**Module map.** `static/atlas/js/localmap.js` owns the whole view — layout,
Leaflet instance, feature drawing, left-hand list, drawer and depth diagram.
`static/atlas/js/mapstyle.js` holds the four encoding tables and the legend
rows, as data, so nothing about how a feature looks is decided inside the
renderer. `app.js` contributes one block: it puts `.is-map-route` on
`#atlas-main`, points `panels.js` at the drawer's panel container, and hands
the route to `localmap.show()`. `panels.js` contributes one exported hook,
`localMapLinks(record)`, which renders the "Open local map" section for any
record carrying `map_id` or `geometry_map_ids`; the facility renderer and the
no-WebGL fallback table both offer it.

**Route and state.** `state.js` knows `map` as a route type and carries three
extra params, written only while a map route is active: `lv` (comma list of
visible level ids; absent means all), `bm` (`0` hides the basemap), and `sel`
(the entity id in the drawer, or a `geometry:` id for a context feature that
depicts no entity). The existing `y`/`r` timeline state applies unchanged, so
a link can name a campus, a level, a selection and a year at once. Everything
round-trips through back/forward, because selections are `pushState` and the
view is rebuilt from `popstate` like every other route.

**Layout.** Three columns: the layers-and-places list, the map stage, and a
collapsible drawer. The map holds at least 60 % of a 1280 px viewport with the
drawer open and the rest of the stage when it is shut. At ≤ 760 px the columns
stack (map, then list) and the drawer becomes a bottom sheet.

**Styling.** Four encodings, each on its own channel so none can be read as
another: feature **type** (line weight, fill, base hue), **status at the
selected year** resolved from `state_segments` through
`model.js statusForTimeline` (dash pattern; amber for construction and
commissioning, grey for finished), **level** (a pale casing behind subsurface
features), and **representation** (stroke opacity plus a text badge).
Boundaries and inferred-direction lines keep their own dot pattern, because
that pattern is what identifies them; their status reads from hue and from the
list. A feature outside the selected year is hidden, and only comes back —
ghosted — when "show features outside the selected year" is on. "Depth view"
opens an explicitly labelled vertical section with a metres axis; it is never
a second plan.

**Accessibility.** The left list is the accessible equivalent of the map, not
a summary of it: a browser test asserts the set of listed features equals the
set of drawn ones, and every row states the feature's type, level, status,
positional accuracy and representation class in words. Toggles are buttons
with `aria-pressed`; selection is announced through an `aria-live` region; the
map surface is `role="application"` with an `aria-label` that names the
keyboard alternative; the legend explains all four encodings as text; Escape
closes the depth diagram, then the drawer, then (through `app.js`) the route,
returning focus to whatever opened each. Colours are the existing dark-theme
tokens, and the a11y suite measures the rendered contrast of the view's own
text.

**Lazy loading and tiles.** Leaflet 1.9.4 is vendored at
`static/atlas/vendor/leaflet/` and its script and stylesheet are injected on
the first map route, never during the globe's cold load; the per-map geometry
bundle (`geometry/<slug>.json`) is fetched at the same moment. A browser test
asserts that loading the globe requests neither. The basemap is OpenStreetMap
standard tiles — no key, nothing paid, the mandatory attribution always
visible, and toggleable; on repeated tile failure the features stay on the
dark background and a notice says the basemap is unavailable. Those tile hosts
are the one third-party origin in the server's CSP, and only under `img-src`.

**What it refuses to do.** It draws nothing the build did not emit: an entity
with no sourced shape appears in the "Unlocated / geometry not verified" list
with its reason and research backlog, never as an invented circle. A failed
bundle fetch renders an error with a retry, never an empty map, because a
campus with no structures on it reads as a claim.

## 6a. Clustering, semantic zoom and filters

`static/atlas/js/globe.js` rebuilds the globe's marker/arc layer only on
real state changes — initial load, a camera zoom, a timeline move, a filter
change, or entering/leaving a collaboration — never per animation frame.
Each rebuild:

* **Coordinates.** `coordsOf()` reads either the flat dev-fixture shape
  (`{lat, lon}`) or the real build's nested shape
  (`{coordinates: {lat, lon, approximate}}`, A9/A23); a marker whose entity
  carries `coordinates.approximate: true` (typically a campus-grade point
  standing in for a not-yet-pinned hall) renders as a dashed, unfilled
  glyph and its accessible name gets an "(approximate location)" suffix —
  shape encodes it for sighted users, the label for everyone else. The
  fallback tables carry the same distinction as a "Location" column.
* **Semantic zoom (§70).** Below `FACILITY_CLUSTER_ALTITUDE` nearby
  facilities render individually; at or above it they merge into a cluster
  marker (§17). Below `SITE_VISIBLE_ALTITUDE` site/experiment-tier markers
  are drawn at all; above it only the facility tier is (far zoom = "major
  facilities only"). Site markers are intentionally **not** geometrically
  clustered — each stays individually addressable by id — since the far
  zoom tier already keeps them off-screen entirely and merging them would
  make specific caverns/halls unreachable by direct id (used elsewhere for
  timeline/testing).
* **Clustering algorithm.** A single-pass greedy radius merge
  (`clusterByRadius`): each item joins the first existing cluster within a
  radius (degrees) of that cluster's running centroid, else it starts a new
  one. The radius scales with camera altitude (`facilityClusterRadiusDeg`,
  `institutionClusterRadiusDeg`) and uses the shortest signed longitude
  delta so clustering near the antimeridian doesn't see a false 350°+ gap.
  Grid-bucket clustering was tried first and rejected: two markers a few
  hundred km apart can fall into different buckets purely from where the
  grid lines land, which is exactly the class of bug this feature exists to
  fix (see the CERN/LNGS example below).
* **Cluster expansion always disables clustering for the whole tier, not
  just the clicked pair** (`expandTargetAltitude`). A first version zoomed
  in exactly enough to separate the *clicked* cluster's own two members by
  their angular spread — this broke down the moment a cluster sat inside a
  denser region than that pair alone: the wave-3 tree has a run of ~14
  European facilities each within a few hundred km of a neighbour (CERN,
  LNGS, Brokdorf, DESY, Leibstadt, Karlsruhe, …), so zooming in "just
  enough" for one pair routinely landed the camera at an altitude where
  that pair separated into two *different* clusters, each freshly
  re-merged with other nearby facilities the click never mentioned —
  `facility:cern` never appeared as its own marker no matter how many
  times "CERN, Brokdorf" was clicked. The fix: every activation zooms below
  the fixed altitude at which clustering turns off for that entire tier
  (`FACILITY_CLUSTER_ALTITUDE` for facilities; `MIN_CLUSTER_ALTITUDE` for
  institutions, which have no intermediate gate — see below), which is
  local-density-independent by construction and also guarantees
  termination: altitude strictly decreases on every activation, converging
  to `MIN_CLUSTER_ALTITUDE` (clustering off for every tier, everywhere) in
  a bounded number of clicks regardless of how tightly packed the region
  is.
* **Institutions.** In collaboration mode, institution dots cluster the
  same way, at every zoom level (not just "far"), since a single
  collaboration can have hundreds of members in a small region.
  `INSTITUTION_ARC_THRESHOLD` (150) is a real constant, not a heuristic:
  above that many rendered (post-filter, post-timeline) members, arcs
  default off for that collaboration (`isArcsForcedOff()`), and app.js
  resets the `arcs` URL/UI state accordingly the first time a large
  collaboration is entered. The "Show institution connections" checkbox
  always reflects and controls exactly what's drawn — it is never silently
  overridden — so re-enabling it after the reset still works.
* **Arcs are capped to what's drawn.** An institution connection arc exists
  only for the currently visible/clustered institution marker set (a
  cluster gets one arc to its centroid, not one per member), so zooming out
  to cluster institutions also shrinks the arc count, and arc dash
  animation is off unconditionally (a continuously re-animated dash on a
  couple hundred arcs was a standing per-frame cost regardless of user
  interaction — REVIEW_performance.md P1-3).
* **Label budget (§70, "do not show 5,000 labels simultaneously").**
  `LABEL_BUDGET` (40) caps simultaneously visible marker *labels* — glyphs
  and click/focus targets are never hidden by the budget, only the text
  caption (`.atlas-marker.no-label .atlas-marker-label { display: none }`).
  Cluster badges (the count *is* the label) always count toward the budget
  first; individual markers fill the remainder in facility → site →
  institution priority order.
* **Filters** (`static/atlas/js/filters.js`) are pure predicate functions —
  `facilityMatches`, `siteMatches`, `experimentMatches`,
  `collaborationMatches`, `institutionMatches` — shared verbatim by
  `globe.js` (marker/cluster visibility), `fallback.js` (the no-WebGL
  tables) and the filter panel's own per-option counts, so a filtered-out
  entity disappears from every surface identically. Facets: experiment
  status (the exact derived status at the selected year, A3), the coarser
  active/completed/planned era group (a relabelling of `model.js`'s
  `statusEra`, never a second ranking rule), research topic (hierarchical —
  selecting a parent matches every descendant, `buildTopicIndex`), facility
  kind, experiment kind, and geographic region (`REGION_BY_COUNTRY`, a
  static ISO-3166 alpha-2 → continent table; an unmapped code is visible as
  "Unknown" rather than silently dropped). Facets AND together; multiple
  values within one facet OR. A site itself carries no kind/topic of its
  own, so an experiment-kind/topic filter matches a site through the
  experiments hosted there (`buildSiteExperimentIndex`); an institution
  matches through its collaboration's experiment(s), and status/era facets
  don't apply to institutions at all (a membership row has no lifecycle
  status). Filters live in the URL (`t`, `s`, `er`, `fk`, `ek`, `rg` — the
  first two predate the filter panel and are reused with comma-separated
  OR-lists) alongside the existing timeline/mode/collab state, so they are
  deep-linkable and survive reload and back/forward through `state.js`'s
  existing `navigate`/`init` contract.

Concrete example this design fixed: in the real bundle, CERN and LNGS
(Laboratori Nazionali del Gran Sasso, ~730 km apart) sat close enough on
screen at the default overview zoom that clicking the CERN marker could hit
LNGS's DOM element instead — a real, user-visible bug, not just a
performance concern. Clustering the two into one "2 facilities" marker
(expandable by click or Enter) removes the overlap entirely: there is
exactly one hit-testable element at that position until the user zooms in
or expands it.

## 7. HEP Graph integration

People reuse INSPIRE author identifiers. Where a person is resolved, the build
derives a link into HEP Graph's existing researcher view; no pathfinding,
identity or evidence logic is duplicated. Unresolved people are kept, labelled,
and never linked. The atlas adds no write paths and no new upstream requests to
the existing application.

## 8. Deployment

The atlas is served by the same Python handler as HEP Graph, from static files
with a content-hashed data version. Generated bundles are cacheable for five
minutes; the application shell is not cached. Nothing in the atlas holds server
state, so it is unaffected by the per-process job and cache behaviour that
governs HEP Graph's live searches.
