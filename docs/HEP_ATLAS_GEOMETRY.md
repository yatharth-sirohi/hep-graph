# HEP Atlas local-map geometry layer (contract v1, 2026-09-18)

This document is the contract for **to-scale local maps** of experimental
sites: the canonical geometry records, what the validator enforces, what the
build emits, what the browser draws, and how a campus is researched and
added. It is normative alongside ontology amendment A25 in
`docs/HEP_ATLAS_ONTOLOGY.md`; the bundle section here extends
`docs/HEP_ATLAS_BUNDLES.md`.

The requirement it answers: on a campus map a reader must see the physical
layout **to scale** — accelerator rings on their true paths, beamlines as
lines, detector halls and experimental areas as footprints, in their real
spatial relationship — with a metre scale bar and a north indicator. Pins,
unscaled diagrams and invented circles do not satisfy it. Where public
evidence cannot support a shape, the entity stays visible in an
"unlocated / geometry not verified" list with a sourced explanation; it is
never drawn.

## 1. Entities

Two new entity types, one file per record under `data/atlas/`:

| Type | Directory | Id | Role |
| --- | --- | --- | --- |
| `map` | `maps/` | `map:<facility-slug>` | One local map per facility (or per geographically separate campus of a facility): centre, extent, levels, unlocated list, schematics |
| `geometry` | `geometry/` | `geometry:<slug>` | One drawable feature: a GeoJSON shape linked to the entity it depicts, with representation class, accuracy, level, time validity, sources and checks |

Both carry the common fields (`id`, `type`, `schema`, `name`, `aliases`,
`summary`, `sources`, `links`, `notes`, `coverage`) with the usual A22
meaning for record-level `sources` (identity claims only).

### 1.1 `map`

```json
{
  "id": "map:cern",
  "type": "map",
  "schema": "hep-atlas/0.2",
  "name": "CERN — Meyrin, Prévessin and the LHC ring",
  "aliases": [],
  "facility_id": "facility:cern",
  "site_ids": ["site:cern-meyrin", "site:cern-point-1-atlas", "site:cern-point-5-cms"],
  "center": {"lat": 46.2600, "lon": 6.0600, "kind": "campus", "precision_m": 500,
             "sources": ["src:osm-lhc-relation-9512017"], "verified_at": "2026-09-18",
             "confidence": "derived", "locator": "centroid of OSM relation 9512017",
             "note": "Map centre only; not a claim about any structure."},
  "extent_m": 8000,
  "levels": [
    {"id": "surface", "name": "Surface", "kind": "surface", "depth_m": null, "note": ""},
    {"id": "lhc-tunnel", "name": "LHC/LEP tunnel (50–175 m below surface)", "kind": "underground",
     "depth_m": {"min": 50, "max": 175, "unit": "m", "dimension": "length", "display": "50–175 m",
                 "sources": ["src:cern-lhc-faq"], "verified_at": "2026-09-18", "confidence": "verified",
                 "quote": "…between 45 and 170 metres below the surface…"},
     "note": "Plan view; depth varies with the Jura slope."}
  ],
  "unlocated": [
    {"entity_id": "accelerator:linac4", "reason": "Linac4 sits inside the Meyrin site but no fetched public source gives its tunnel path; the OSM building footprint is drawn instead.",
     "sources": ["src:cern-linac4-page"], "backlog": "Find the Linac4 civil-engineering drawing or an official site plan with a scale bar; georeference against surveyed buildings.",
     "verified_at": "2026-09-18"}
  ],
  "schematics": [
    {"title": "CERN accelerator complex (schematic, not to scale)", "source_id": "src:cern-accelerator-complex-2022",
     "note": "Official schematic; topology only. Never drawn on the to-scale map."}
  ],
  "linked_map_ids": ["map:lngs"],
  "summary": {"plain": "…", "technical": "…"},
  "sources": ["src:cern-official-site"],
  "links": {"website": null},
  "notes": [],
  "coverage": {"tier": "A", "researched": "partial"}
}
```

Field rules:

* `facility_id` required; `site_ids` lists the facility's sites covered by
  this map (a site may appear on one map only). A facility with
  geographically separate campuses (Fermilab/Ash River/SURF, J-PARC/Kamioka)
  gets **one map per campus**; the off-campus destination is a *linked map*
  (`linked_map_ids`, authored or derived from beamline far sites and
  `related_facility_ids`), never drawn inside the source campus.
* `center` is a Coordinates value (any `kind`; `derived` confidence allowed)
  and is only the default camera position. `extent_m` is the half-width of
  the default view in metres (500–60 000).
* `levels[]`: every feature names one. `kind` ∈ `surface | underground |
  sea | lake | ice | mountain`. `depth_m` is an optional sourced Quantity of
  dimension `length` (value or min/max), **positive downwards**. Two levels
  may never be drawn on one unlabelled plane: the browser shows levels as
  separate toggles and lists each feature's level.
* `unlocated[]`: entities of this facility (accelerators, beamlines,
  detectors' sites, experiments) that the map does **not** draw, each with a
  sourced `reason` and a concrete research `backlog`. An entity may not be
  both drawn and unlocated (error). Every accelerator and beamline whose
  `facility_id` is this facility, and every site in `site_ids` holding a
  detector placement, must be either drawn or unlocated (warning
  `map-entity-unaccounted`): honesty is enforced, completeness is not. A
  site counts as drawn when a feature names it as `entity_id` **or** as
  `site_id` (a detector footprint drawn at the hall accounts for the hall).
* `schematics[]`: official diagrams offered as **links only**, labelled "not
  to scale". Schematic geometry is never a `geometry` record (see §1.2).

### 1.2 `geometry`

```json
{
  "id": "geometry:lhc-tunnel-ring",
  "type": "geometry",
  "schema": "hep-atlas/0.2",
  "name": "LHC tunnel (LEP tunnel), full ring",
  "aliases": [],
  "map_id": "map:cern",
  "entity_id": "accelerator:lhc",
  "site_id": null,
  "feature_type": "ring",
  "level_id": "lhc-tunnel",
  "depth_m": null,
  "representation": "georeferenced",
  "accuracy_m": 15,
  "method": "OpenStreetMap relation 9512017 (16 member ways, tunnel=yes, layer=-5) merged into one closed line; nodes kept verbatim.",
  "geometry": {
    "value": {"type": "LineString", "coordinates": [[6.0554657, 46.2356800], ["…", "…"]]},
    "sources": ["src:osm-lhc-relation-9512017", "src:cern-lhc-faq"],
    "verified_at": "2026-09-18",
    "confidence": "verified",
    "locator": "OSM relation 9512017 as of 2026-09-18T20:00Z; CERN FAQ 'The LHC is 26.7 km in circumference'",
    "note": "Confidence 'verified' rests on the passing circumference check against the official figure."
  },
  "checks": [
    {"kind": "length", "expected": {"value": 26659, "unit": "m", "dimension": "length", "display": "26 659 m"},
     "tolerance": 0.02, "sources": ["src:cern-lhc-faq"], "locator": "section 'Facts and figures'",
     "quote": "The LHC is 26,659 m in circumference"}
  ],
  "valid": {"start": "1985", "end": null},
  "license": {"name": "ODbL-1.0", "attribution": "© OpenStreetMap contributors",
              "url": "https://www.openstreetmap.org/copyright"},
  "osm": {"elements": ["relation/9512017"], "timestamp": "2026-09-18T20:00:50Z"},
  "summary": {"plain": "The 27-kilometre ring tunnel under the French–Swiss border that housed LEP and now houses the LHC."},
  "sources": ["src:osm-lhc-relation-9512017"],
  "links": {"website": null},
  "notes": [],
  "coverage": {"tier": "A", "researched": "full"}
}
```

Field rules:

* `map_id` required and must exist; `level_id` must be one of that map's
  `levels[].id`.
* `entity_id`: the record that opens when the feature is clicked —
  `accelerator | beamline | detector | site | experiment | facility`, or
  `null` for context features (`building`, `boundary`, `road`, `water`)
  that depict no atlas entity. A `ring`, `linac`, `beamline`, `transfer_line`,
  `cavern`, `hall`, `target_station`, `array`, `string` or `direction_line`
  **must** have an `entity_id`.
* `feature_type` ∈ `ring | linac | transfer_line | beamline | tunnel |
  shaft | cavern | hall | experimental_area | target_station | building |
  boundary | array | string | direction_line | level_outline | road | water |
  other`. Rings and tunnels are lines (`LineString` closed for a ring);
  halls, caverns, buildings, areas and boundaries are `Polygon` /
  `MultiPolygon`; strings, shafts and small instruments may be `Point`.
* `geometry` is a Sourced value whose `value` is a **GeoJSON geometry
  object** (RFC 7946: `[lon, lat]` order, WGS 84). Allowed types: `Point`,
  `LineString`, `MultiLineString`, `Polygon`, `MultiPolygon`. Polygons must be
  closed rings of ≥ 4 positions; lines ≥ 2 positions; every position within
  bounds; no `NaN`. Provenance (`sources`, `verified_at`, `confidence`,
  `quote | locator`, `note`) follows A15/A17: **a locator or quote is
  required** (the OSM element id and timestamp, or the drawing/table
  reference).
* `representation` (what kind of evidence the shape is):
  * `surveyed` — coordinates published by the laboratory or in a technical
    paper (survey tables, published lat/lon of a hall centre, a beam
    direction with a target position);
  * `georeferenced` — traced from imagery/GIS by a third party
    (OpenStreetMap, a national mapping agency) or from an official plan that
    was georeferenced against ≥ 3 surveyed control points (name them in
    `method`);
  * `derived` — computed from sourced parameters and sourced anchors (a
    1 000 m radius from a published circumference around a fitted centre;
    detector positions from published distances along a sourced beam axis).
    `method` must state the computation and its inputs; **a derived shape
    may not rest on an anchor whose `precision_m` exceeds its own
    `accuracy_m`** (no footprint from a 3 km campus point — error
    `geometry-derived-from-coarse-anchor`);
  * `inferred_direction` — a long-baseline neutrino direction: the
    great-circle azimuth from the sourced near point towards the sourced far
    site, clipped to the map extent. It is **not** a physical structure and
    is drawn and labelled as an inferred direction; the validator recomputes
    the azimuth from `entity_id`'s far site and fails if it differs by > 1°.
  * There is **no** `schematic` representation. A shape traced from an
    unscaled diagram is not a geometry record; it goes to `map.schematics`
    as a link.
* `accuracy_m` (required except for `inferred_direction`): estimated
  positional accuracy radius in metres, honest and rounded up: OSM building
  footprints ≈ 3–10 m, OSM tunnel lines 10–30 m, ring roads used as tunnel
  proxies ≥ 30 m, published minute-precision coordinates ≥ 20 m.
* `confidence`: `verified` requires a rank ≤ 10 source **and** either
  `representation: surveyed` or a passing `checks[]` row that cites a rank
  ≤ 10 source (an independent official figure confirms the georeferenced
  shape). OpenStreetMap alone (source type `openstreetmap`, rank 11) yields
  at most `approximate`; a `derived` shape is `derived`.
* `checks[]`: independent cross-checks the validator executes.
  `kind` ∈ `length` (geodesic length of a line / perimeter of a polygon),
  `area` (m²), `distance` (centroid-to-centroid to `to_geometry_id`),
  `azimuth` (initial bearing of a line, degrees), `span` (largest extent).
  `expected` is a Quantity with a `sources` list and a quote/locator;
  `tolerance` is a fraction (default 0.03). A failing check is an **error**
  (`geometry-check-failed`); a ring whose sourced circumference is known
  must carry a `length` check (`ring-without-length-check` warning).
* `valid: {start, end}` (optional Dates): when the *shape itself* has a
  lifetime different from its entity's (a hall that was rebuilt; a tunnel
  that predates the machine in it). Without it the feature inherits the
  entity's `state_segments`; context features without an entity and
  without `valid` are timeless.
* `depth_m` optional sourced Quantity (positive downwards) for the feature
  itself when it differs from the level's.
* `license`: required when the shape is copied or derived from third-party
  geodata (`ODbL-1.0` for OpenStreetMap, with the attribution string);
  `null` for the atlas's own derivations from published numbers. The build
  aggregates attributions per map and the browser displays them.
* `osm`: when OpenStreetMap contributed, the element ids (`way/…`,
  `relation/…`, `node/…`) and the `timestamp_osm_base` of the extract.
* `site_id`: the atlas site the feature stands at, when one exists. If that
  site's coordinates are `kind: detector|underground_lab` with
  `precision_m ≤ 100`, the feature's centroid must lie within
  `max(3 × precision_m, 150 m)` of the point (warning
  `geometry-site-mismatch`); a coarse (campus-grade) site point is never
  used to check or to derive anything.

### 1.3 Source records for geodata

* OpenStreetMap: source type `openstreetmap` (new, rank 11; A25),
  `url` = `https://www.openstreetmap.org/<type>/<id>` for a single element,
  or the Overpass query URL for an extract, `publisher` = "OpenStreetMap
  contributors", `date` = the extract timestamp, `retrieval: full_text`.
  One source record per principal element (ring, tunnel, hall) is preferred;
  bulk building footprints may share one extract source whose `excerpt`
  lists the element ids.
* Laboratory GIS / open-data portals: `source_type: official_facility_site`
  or `project_document` as appropriate; record the dataset licence in the
  geometry `license` field.
* Papers giving coordinates or distances: `detector_paper`,
  `journal_article`, `design_report` — cite page/table in `locator`, quote
  the figure.
* Never a screenshot, never a copied raster of an official PDF as a
  basemap. Imagery is used only as evidence *behind* a third party's
  tracing (OSM) or a lab's own published coordinates.

## 2. Validator rules (A25)

| Rule | Level | Meaning |
| --- | --- | --- |
| `geometry-geojson-invalid` | error | not an allowed GeoJSON type; coordinates out of range; polygon ring not closed / < 4 positions; line < 2 positions |
| `geometry-unknown-map`, `geometry-unknown-level` | error | `map_id` / `level_id` do not resolve |
| `geometry-entity-type` | error | `entity_id` type not allowed, or missing for a feature type that requires one |
| `geometry-out-of-extent` | error / warning | any position > 60 km from the map centre (error), > 3 × `extent_m` (warning) unless `direction_line` |
| `geometry-representation` | error | unknown class; `schematic`; `derived` without `method`; `georeferenced` from OSM without `osm.elements` or `license` |
| `geometry-accuracy` | error | `accuracy_m` missing / non-positive where required |
| `geometry-confidence` | error | `verified` without the required evidence (see §1.2) |
| `geometry-derived-from-coarse-anchor` | error | `derived` whose `method` names an anchor site whose `precision_m` > `accuracy_m` (the validator checks every `site:` id mentioned in `method` and `note`) |
| `geometry-check-failed` | error | a `checks[]` measurement outside tolerance; the message states expected, measured and tolerance |
| `geometry-check-unmeasurable` | error | a check kind the geometry type cannot answer |
| `ring-without-length-check` | warning | `feature_type: ring` with no `length` check |
| `geometry-direction-azimuth` | error | `inferred_direction` azimuth differs > 1° from the great-circle bearing to the entity's far site |
| `geometry-valid-order` | error | `valid.end` before `valid.start` |
| `geometry-outside-entity-hull` | warning | `valid` lies entirely outside the entity's existence hull |
| `geometry-site-mismatch` | warning | centroid too far from a precise site point (§1.2) |
| `geometry-duplicate-shape` | warning | two features of one map with identical coordinates |
| `map-unknown-facility`, `map-unknown-site`, `map-site-elsewhere` | error | references do not resolve; a site listed on two maps |
| `map-level-duplicate` | error | duplicate `levels[].id` |
| `map-center-far` | warning | centre > 30 km from the facility's primary site |
| `map-unlocated-drawn` | error | an `unlocated[]` entity also has a geometry feature on the map |
| `map-unlocated-unsourced` | error | an `unlocated[]` row without `sources` or without `backlog` |
| `map-entity-unaccounted` | warning | a facility accelerator/beamline, or a detector-hosting site of the map, that is neither drawn nor unlocated |
| `map-extent` | error | `extent_m` outside 500–60 000 |

Distances are great-circle on the WGS 84 mean sphere (`schema.great_circle_m`);
polygon areas use the spherical excess formula. Both, and every other
measurement the validator makes, live in **`hepgraph/atlas/geo.py`** —
`polygon_area_m2`, `line_length_m`, `polygon_perimeter_m`, `centroid`,
`geometry_span_m`, `geometry_azimuth_deg`, `initial_bearing_deg`, `bbox`,
`geojson_problems` and a metre-tolerance Douglas-Peucker `simplify`.
(Contract v1 named `schema.polygon_area_m2`; the area function needs the
GeoJSON ring conventions `geo.py` defines, and `schema.py` stays the
vocabulary module holding only the scalar `great_circle_m`. Everything else
in the layer imports it from `geo`.) `geo.py` speaks GeoJSON `[lon, lat]`
order throughout and flips the arguments for `schema.great_circle_m` itself.

### 2.1 Decisions this contract left open

Implementation resolved these; they are normative from here on.

* **`azimuth` tolerance is in degrees, not a fraction.** §1.2 says
  `tolerance` is a fraction defaulting to 0.03, which is meaningless for a
  bearing (3 % of 350° is 10°, of 0.5° is nothing). An `azimuth` check reads
  its `tolerance` as absolute degrees and defaults to
  `schema.AZIMUTH_TOLERANCE_DEG` (1°), the same figure A25 fixes for a
  direction line. Every other kind keeps the fraction.
* **A `length` check on a polygon measures its outer ring(s) only.** A
  courtyard is not fence, so an `area` check and a `length` check on the same
  record stay comparable with the same published plan.
* **`geometry-out-of-extent` does not apply to a `direction_line` at all**,
  neither the 60 km error nor the 3 × `extent_m` warning: a far site is
  1 300 km away and clipping to the view is the browser's job (§4), not a
  data defect.
* **"Drawn or unlocated" (`map-entity-unaccounted`) is answered across every
  map of the same facility.** Fermilab's campus map and its Ash River map are
  two views of one inventory; an entity drawn on either is accounted for on
  both.
* **`map-site-elsewhere` also fires when a map lists a site whose
  `facility_id` names a different facility.** A site with no recorded
  facility is unknown, not misplaced, and is left alone.
* **`map-unlocated-unsourced` also requires a non-empty `reason`**, not only
  `sources` and `backlog`: a row that does not say why is not an admission.
* **A15 (quote or locator) applies to the `geometry` value and to every
  `checks[]` row.** The shape must name its OSM element and timestamp or its
  drawing reference, and a cross-check must say where its official figure is
  printed.
* **`geometry.level_id` is not an entity reference.** It names one of its own
  map's `levels[].id` (a local label such as `"surface"`), so it is in
  `schema.NON_REFERENCE_ID_KEYS` and `geometry-unknown-level` is what checks
  it; the generic dangling-reference rule skips it.
* **Where an A25 rule says something more specific than a generic rule, the
  generic rule steps aside** (validate.py's "one defect, one rule"):
  `geometry-unknown-map` owns `map_id` resolution, `map-unknown-facility` and
  `map-unknown-site` own theirs, `geometry-entity-type` owns the entity type,
  `geometry-representation` owns the representation enum, and
  `geometry-confidence` owns the whole `verified` test including the rank
  half that `verified-source-rank` would otherwise report twice.
* **`map.center` is range-checked but its `kind` is free.** It is a camera
  position, not a marker: the globe's kind-vs-entity rules would be
  meaningless for it. The GeoJSON arrays of a `geometry` record are not
  Coordinates and are never walked by the coordinate rules;
  `geometry-geojson-invalid` owns them.
* **A `checks[]` row the validator cannot execute is an error**
  (`geometry-check-unmeasurable`), never a silent pass. A check nobody can
  answer is not evidence.
* **`checks[].expected_m` / `measured_m` in the bundle are in the base unit
  of the check kind** — metres, square metres, or degrees for an `azimuth`.

## 3. Build outputs

* `atlas.json` gains `"maps": {map_id: {…}}` with, per map: `id`, `name`,
  `facility_id`, `site_ids`, `center` (`{lat, lon}`), `extent_m`, `levels`
  (stripped), `feature_count`, `to_scale_count` (features whose
  representation is not `inferred_direction`), `unlocated_count`,
  `linked_map_ids` (authored ∪ derived from beamline far sites and
  `related_facility_ids` that have maps), `attribution` (sorted unique
  attribution strings), `bundle` (`"geometry/<slug>.json"`), `coverage`,
  `state_segments`/`status` inherited from the facility. `facility` and
  `site` records gain derived `map_id`; `accelerator`, `beamline` and
  `detector` records gain derived `geometry_map_ids` (maps on which they are
  drawn). `manifest.counts` gains `maps` and `geometry`.
* `geometry/<map-slug>.json` (lazy, one per map):

```json
{
  "schema": "hep-atlas/0.2", "version": "…", "build_date": "2026-09-18",
  "map": { "…stripped map record…", "unlocated": [{"entity_id", "entity_name", "entity_type", "reason", "backlog", "sources": ["src:…"]}],
           "schematics": [{"title", "url", "source_id", "note"}] },
  "bbox": [minLon, minLat, maxLon, maxLat],
  "attribution": ["© OpenStreetMap contributors (ODbL)"],
  "features": [
    {"id": "geometry:lhc-tunnel-ring", "name": "…", "feature_type": "ring", "level_id": "lhc-tunnel",
     "entity_id": "accelerator:lhc", "entity_type": "accelerator", "entity_name": "Large Hadron Collider",
     "site_id": null, "representation": "georeferenced", "accuracy_m": 15, "method": "…",
     "depth_m": null, "geometry": {"type": "LineString", "coordinates": [[…]]},
     "measured": {"length_m": 26653.4, "area_m2": null, "centroid": [lon, lat]},
     "checks": [{"kind": "length", "expected_m": 26659, "measured_m": 26653.4, "tolerance": 0.02, "passed": true, "sources": ["src:cern-lhc-faq"]}],
     "state_segments": [[…]], "status": "active",
     "provenance": {"sources": ["src:…"], "verified_at": "2026-09-18", "confidence": "verified", "locator": "…", "quote": null, "note": "…"},
     "license": {"name": "ODbL-1.0", "attribution": "…", "url": "…"}, "osm": {"elements": ["relation/9512017"], "timestamp": "…"}}
  ],
  "source_titles": {"src:cern-lhc-faq": {"title": "…", "url": "…", "source_type": "official_facility_site"}},
  "entity_index": {"accelerator:lhc": ["geometry:lhc-tunnel-ring"]}
}
```

  `state_segments` come from `valid` when present (a single `active`
  segment over `[lo(start), hi(end) or build date]`), otherwise from the
  entity; a context feature with neither has `null` and is drawn in every
  year. Coordinates are emitted with 7 decimals. The build fails when a
  map bundle exceeds 2 MB.
* `search.json` gains `map` entries (`["map", "map:cern", "CERN — …", [], "Local map · CERN"]`).
* `coverage.json` and `scripts/atlas_coverage_report.py` gain a "Local map
  geometry" table: per map, features by representation class, unlocated
  count, checks passed/failed, and every facility **without** a map listed
  by name.

## 4. Browser contract

* Route `#/map/<facility-slug>`; query `lv` (comma list of visible level
  ids; default all), `bm` (`0` hides the basemap), `sel` (an entity id shown
  in the drawer, e.g. `sel=accelerator:lhc`), plus the existing `y`/`r`
  timeline state. Back/forward and pasted links restore everything.
* Layout (laptop): left column = layer and place list (levels, feature
  types, representation legend, the "Unlocated / geometry not verified"
  list, linked maps); centre = the map filling the stage; right =
  collapsible drawer showing the selected entity's normal detail panel
  (panels.js) plus the feature's shape facts (type, level, depth,
  representation, accuracy, method, checks, sources, licence). Mobile:
  stacked, drawer as a bottom sheet.
* Map engine: vendored Leaflet 1.9.4 (BSD-2-Clause; `static/atlas/vendor/leaflet/`)
  loaded **only** when a map route is opened; Web Mercator with the scale
  control computed at the view centre (`L.control.scale`, metric), a north
  indicator, zoom controls, keyboard panning. Web Mercator's scale error
  across a ≤ 60 km view is < 0.1 %, which the geometry test suite asserts
  by projecting sourced baselines.
* Basemap: OpenStreetMap standard tiles with the mandatory attribution,
  toggleable, default on; on tile failure the features still render on the
  dark background and a notice says the basemap is unavailable. No API key,
  nothing paid.
* Styling encodes four things independently and the legend says so:
  **feature type** (ring/tunnel thick line, beamline line with arrowheads,
  hall/cavern/building filled polygon, boundary thin dashed, direction line
  dotted with an arrow and the label "inferred direction — not a
  structure"), **status at the selected year** from `state_segments`
  (active solid; construction/commissioning dashed amber; completed/
  decommissioned grey; proposed/approved dotted; not yet existing or ended
  at that year → hidden unless "show features outside the selected year" is
  on, then ghosted), **level** (underground features drawn with a distinct
  stroke pattern and listed under their level toggle; "Depth view" opens an
  explicitly labelled depth/level diagram, never a plan), **representation**
  (`derived` and `approximate` shapes get a lighter outline and a badge;
  every feature's `accuracy_m` is in its tooltip and list row).
* Clicking or keyboard-activating a feature navigates to
  `sel=<entity_id>`; the left list is the accessible equivalent (buttons
  with type, level, status, accuracy). The no-WebGL fallback opens the same
  map view (Leaflet needs no WebGL); the fallback tables gain a "Local map"
  link per facility.
* Off-campus destinations are listed under "Linked maps and far sites" with
  the great-circle distance and bearing, and link to their own map or site
  record.
* The globe's facility panel, site/accelerator/beamline/detector panels and
  search results all offer "Open local map" when `map_id` exists.

## 5. Research method (per campus)

1. **Inventory** the facility's accelerators, beamlines, detector-hosting
   sites and experiments from `data/atlas/`. Every one must end up drawn or
   in `unlocated[]`.
2. **Collect candidate geometry**, in this order of preference:
   official published coordinates or survey tables → official GIS/open-data
   services with a stated licence → OpenStreetMap (Overpass; record element
   ids and timestamp) → derivation from sourced parameters. Save every raw
   extract in your scratch directory; commit only the records.
3. **Cross-check** each principal feature against an independent official
   figure (circumference, length, hall dimensions, distance between two
   halls, published lat/lon) and record it as a `checks[]` row. A shape with
   no possible cross-check stays `approximate`.
4. **Decide the representation honestly.** A ring road is not a tunnel: if
   you fit a circle to it, the record is `derived`, `accuracy_m ≥ 30`, and
   the `method` says so. A campus-centroid point is not an anchor for
   anything.
5. **Write the map record**: centre, extent, levels with sourced depths,
   `unlocated[]` with reasons and backlog, official schematics as links,
   linked maps for off-campus far sites.
6. **Validate and build**: `python -m hepgraph.atlas.validate` (0 errors),
   `python -m hepgraph.atlas.build`, open `#/map/<slug>` and compare the
   scale bar against a known baseline.
7. **Record** what you could not do in the map's `unlocated[]` and in your
   worklog; a QA pass other than the researcher challenges coordinates,
   licences, shapes and status.

### 5.1 `scripts/atlas_osm_extract.py`

Step 2 has a helper for the OpenStreetMap case. It is a **maintainer tool**,
not part of the pipeline: it fetches shapes from Overpass, measures them and
writes *draft* records you then finish by hand.

```bash
# every building in a bounding box, plus the ring relation
python scripts/atlas_osm_extract.py --map cern \
    --bbox 46.22,6.03,46.26,6.08 \
    --filter 'way["building"]' --filter 'relation["railway"="rail"]'

# named elements, when you already know them
python scripts/atlas_osm_extract.py --map cern --ids relation/9512017,way/123456

# see the query without issuing it, or re-process a saved response
python scripts/atlas_osm_extract.py --map cern --ids way/123 --query-only
python scripts/atlas_osm_extract.py --map cern --ids way/123 --from-json raw.json
```

What it does, and what it deliberately does not:

* **One request per run**, 90-second timeout, `User-Agent
  HEP-Atlas-research/1.0`. Overpass is a donated public service and the
  script never retries in a loop.
* It **prints the measured length or perimeter, area and span of every
  shape** so you can compare each with the official published figure. It
  never writes the `checks[]` row for you — that row is a claim about a
  source, and only a person who read the source may make it.
* Every draft is `representation: georeferenced`, `confidence: approximate`,
  carries `license: ODbL-1.0` with the attribution, `osm.elements` and the
  extract timestamp, and a `notes` entry listing what is still missing. The
  matching `src:` record is `source_type: openstreetmap` (rank 11), which is
  why no draft it writes can be `verified`.
* Output goes to a scratch directory (printed on exit) unless you pass
  `--out DIR`; `--write-data` writes into `data/atlas/` and never overwrites
  an existing file. The raw Overpass response is saved beside the drafts so a
  reviewer can see the input.
* `feature_type` and `accuracy_m` are *guesses* from the OSM tags, floored at
  the §1.2 figures. Check both. A wrong guess left in a committed record is
  worse than `other`.

## 6. Adding a campus

The whole path from nothing to a working `#/map/<slug>`, for a maintainer.

**Files to create**, all under `data/atlas/`:

| File | What it is |
| --- | --- |
| `maps/<facility-slug>.json` | the map: centre, `extent_m`, `levels[]`, `unlocated[]`, `schematics[]` |
| `geometry/<slug>.json` | one per drawable feature |
| `sources/<slug>.json` | one per source the map or a feature cites |

**Commands, in order:**

```bash
# 1. inventory — what must end up drawn or unlocated
python -c "from hepgraph.atlas.load import load_atlas; a=load_atlas(); \
  print([i for i,r in a.by_type('accelerator').items() if r['facility_id']=='facility:<slug>'])"

# 2. draft the OSM shapes into a scratch directory (optional, see §5.1)
python scripts/atlas_osm_extract.py --map <slug> --bbox S,W,N,E --filter 'way["building"]'

# 3. write maps/<slug>.json by hand, then move the finished drafts into
#    data/atlas/geometry/ and data/atlas/sources/

# 4. validate — this must reach 0 errors before anything is committed
python -m hepgraph.atlas.validate

# 5. build and look at it
python -m hepgraph.atlas.build
#    then open #/map/<slug> and compare the scale bar with a known baseline

# 6. the two reports that must not drift
python scripts/atlas_coverage_report.py
python scripts/atlas_validation_counts.py

# 7. the full suite, including the real-data geometry test
.venv/bin/python -m pytest -q
```

**Checks before you commit:**

* `python -m hepgraph.atlas.validate` reports **0 errors**. Warnings are
  advice; `map-entity-unaccounted` in particular means you have not yet said
  what you could not place, and the honest fix is an `unlocated[]` row, not
  a deleted entity.
* `tests/test_atlas_geometry_data.py` stops skipping the moment your map
  lands, and then requires that every check you wrote **passes** against the
  real shapes. A check that cannot be executed counts as a failure.
* Every feature's `accuracy_m` is one you would defend out loud. §1.2 gives
  the floors: OSM footprints 3–10 m, OSM tunnel lines 10–30 m, a ring road
  used as a tunnel proxy ≥ 30 m, minute-precision published coordinates
  ≥ 20 m.
* Anything you could not place is in `unlocated[]` with a sourced `reason`
  and a `backlog` naming the document that would fix it.
* No OSM-derived shape claims `verified`, and every one carries its ODbL
  attribution.
* `python -m hepgraph.atlas.build --check` is clean after you commit the
  generated bundles, and the map's `geometry/<slug>.json` is under 2 MB. If
  it is not, simplify with `hepgraph.atlas.geo.simplify` (record the
  tolerance in `method`) or split the campus into two maps.

## 7. Licensing

OpenStreetMap data is © OpenStreetMap contributors under the ODbL 1.0.
Geometry records that copy or derive from it carry
`license.name: "ODbL-1.0"` and the attribution; the browser shows the
aggregated attribution on every map that uses it; `data/atlas/geometry/LICENSE.md`
states that the OSM-derived geometry records are made available under the
ODbL. Basemap tiles from openstreetmap.org are used within the OSMF tile
usage policy (light use, attribution displayed, default browser
`Referer`). Official laboratory PDFs, plans and images are **not** copied
into the repository; they are cited.
