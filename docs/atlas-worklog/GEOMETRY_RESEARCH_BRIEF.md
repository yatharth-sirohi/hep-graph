# Brief for local-map geometry researchers

You are digitising **to-scale geometry** for one facility of HEP Atlas.
Read `docs/HEP_ATLAS_GEOMETRY.md` (the contract) and
`docs/atlas-worklog/RESEARCH_AGENT_RULES.md` first. The standards below are
not negotiable; scope is (say what you could not do — never fake it).

## Standards

1. **Nothing from memory.** Every coordinate, distance, depth and date comes
   from a fetched source you cite. If you know where a hall is but cannot
   find a public source, it goes in `map.unlocated[]` with the reason.
2. **Honest representation.** `surveyed` only for published coordinates or
   survey tables; `georeferenced` for OpenStreetMap or other third-party
   tracings (record the element ids and extract timestamp); `derived` for
   anything you compute (state the computation in `method`);
   `inferred_direction` only for a long-baseline neutrino direction.
   A ring road, a pond or a landuse polygon is **not** a tunnel: using one
   as a proxy makes the record `derived` with `accuracy_m` ≥ 30 and an
   explicit `method`. Never derive a shape from a campus-grade point.
3. **No perfect circles unless justified.** A circle is allowed only when a
   source states the machine is circular (or gives a radius) *and* you have
   a sourced centre; then it is `derived` with a `length` check against the
   sourced circumference. Racetrack or polygonal machines (Main Injector,
   RHIC, SPS, KEKB, J-PARC MR) are never drawn as circles.
4. **Cross-check every principal feature** with a `checks[]` row
   (circumference, length, hall dimensions, inter-hall distance, published
   lat/lon) citing an official source. Without a check, confidence stays
   `approximate`.
5. **Two levels never share one unlabelled plane.** Underground tunnels,
   caverns and halls get their own `levels[]` entry with a sourced depth.
6. **Off-campus far detectors are linked maps or far sites, never drawn on
   the source campus.** A `direction_line` may show the first kilometres of
   the beam direction, labelled as inferred.
7. **Licences.** OpenStreetMap-derived shapes carry
   `license: {name: "ODbL-1.0", attribution: "© OpenStreetMap contributors",
   url: "https://www.openstreetmap.org/copyright"}`. Never copy an official
   PDF, plan or photo into the repository; cite it. Never publish
   security-sensitive detail (access control, guard posts, utility
   vulnerabilities) — accelerator enclosures, halls and public boundaries
   are fine, they are on every official campus map.
8. **Time.** A feature inherits its entity's timeline; give `valid` only when
   the shape's own lifetime differs (a tunnel older than the machine).
   Verify status from sources; do not assume every machine listed operates
   today.
9. **Validate.** `python -m hepgraph.atlas.validate` must report 0 errors for
   your files before you finish. Warnings you leave must be explained in
   your worklog.

## Tools

* **Overpass (OpenStreetMap)** — one query at a time, `[timeout:90]`, small
  bounding boxes, a descriptive `User-Agent`; mirrors:
  `https://overpass-api.de/api/interpreter`,
  `https://lz4.overpass-api.de/api/interpreter`. Save raw responses under
  your scratch directory (`osm/<facility>-<what>.json`), never under
  `data/`. Fetch element geometry with `out geom;`. Record
  `osm3s.timestamp_osm_base` as the extract timestamp. Useful filters:
  `way["tunnel"="yes"]`, `way["man_made"]`, `way["building"]["name"]`,
  `relation["name"~"…"]`, `way["landuse"]`.
* **Wikidata** for entity ids/coordinates as *leads only* (rank 12; never
  the sole source of a verified value).
* **Laboratory sources**: facility pages, TDRs, NIM detector papers (they
  often give hall coordinates or distances to the metre), civil-engineering
  pages, environmental assessments, open GIS portals (check the licence).
  `curl -A 'Mozilla/5.0 …'` works where a bare fetch is blocked; if a site
  returns 403 to everything, say so in the worklog and move on.
* Compute geodesic lengths with the haversine formula on R = 6 371 008.8 m
  (that is what the validator uses); keep ≤ 400 vertices per feature
  (simplify only if the simplified line stays within `accuracy_m` of the
  original).

## Records to produce

* `data/atlas/maps/<facility-slug>.json` (one per campus).
* `data/atlas/geometry/<facility-slug>-<feature>.json`, one per feature.
* `data/atlas/sources/<facility-slug>-geo-<what>.json` for every new source
  (`source_type: openstreetmap` for OSM elements; official types otherwise;
  `accessed` = today; `retrieval: full_text`; an `excerpt` ≤ 300 chars).
* A worklog `docs/atlas-worklog/GEOMETRY_<facility-slug>.md`: inventory
  table (entity → drawn / unlocated, representation, accuracy, check result),
  every source conflict, what you could not find and the concrete backlog.
* Do **not** edit existing site/detector/accelerator records except to add
  a source id to their `sources` list; report needed corrections in the
  worklog instead.

## Coordinates in existing records

Site points already in `data/atlas/sites/` were researched separately;
81 of 93 are approximate campus-grade points. Do not treat them as hall
positions. Where your research yields a surveyed hall position for a site
that currently carries an approximate point, record it in your worklog under
"site coordinate corrections" with the source; the integrator applies them.
