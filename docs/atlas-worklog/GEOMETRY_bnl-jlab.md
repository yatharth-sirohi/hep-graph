# Geometry worklog: Brookhaven National Laboratory (map:brookhaven-national-laboratory) and Jefferson Lab (map:jefferson-lab)

Researcher: geometry-bnl-jlab. Worktree `/Users/yatharthsirohi/Desktop/HEP-Graph-maps-bnl`,
branch `hep-atlas-local-maps-bnl`. Sources prefixed `src:geo-bnl-*` and `src:geo-jlab-*`.

## Method note: Overpass access this session

Overpass worked for the first ~15 minutes: five successful queries against
`overpass-api.de` found the RHIC ring, the AGS ring, the STAR and PHENIX/sPHENIX
hall footprints and several named context buildings (below). Partway through the
session, before any Jefferson Lab query could run, both permitted mirrors
(`overpass-api.de`, `lz4.overpass-api.de`) began refusing connections outright
(`Connection refused`, not a rate-limit `429`/`504`) on every subsequent attempt,
including a direct `curl` to `/api/status` (bypassing the extraction script
entirely) and a 10-minute, ~30-attempt background poll. Overpass never came back
this session. This matches the CERN researcher's own account
(`GEOMETRY_cern.md`) of the same shared service becoming unreachable under load
from concurrent HEP Atlas sessions.

Once Overpass was down, I switched to **Nominatim** (`nominatim.openstreetmap.org`),
a separate OSM web service that reads the same underlying planet database but
was still reachable. Nominatim's `search`/`lookup` endpoints with
`polygon_geojson=1` return full way/relation geometry for *named* places, so I
used it to fetch the BNL and JLab campus boundaries and two named buildings
(CEBAF Center, and by extension confirmed "Quark Place" as the JLab
experimental-hall street) — but its fuzzy name search could not find CEBAF's
racetrack tunnel or the individual Hall A/B/C/D footprints, which are almost
certainly present in OSM (as `way["tunnel"="yes"]` / named building ways, the
same tagging pattern the earlier BNL queries found) but are not indexed by
Nominatim's text search the way a landuse/amenity-tagged way is. This is why
BNL has a full ring-plus-halls map and Jefferson Lab does not: the outage
started between the two facilities, not because JLab's OSM data is any worse.

## Inventory

| Entity | Drawn? | Feature(s) | Representation | Accuracy | Check |
| --- | --- | --- | --- | --- | --- |
| facility:brookhaven-national-laboratory | map:brookhaven-national-laboratory authored | — | — | — |
| site:bnl-upton-campus | drawn | geometry:bnl-upton-campus-boundary | georeferenced (OSM/Nominatim relation 18896697) | 30 m | RHIC/AGS ring centroids fall inside the boundary bbox (consistency check, not a `checks[]` row) |
| site:bnl-rhic-ip6-star | drawn | geometry:bnl-star-hall | georeferenced (OSM buildings 1006/1006A) | 10 m | none possible (no official footprint figure fetched) |
| site:bnl-rhic-ip8-phenix-sphenix | drawn | geometry:bnl-phenix-sphenix-hall | georeferenced (OSM buildings 1008/1008A) | 10 m | none possible |
| accelerator:rhic | drawn | geometry:bnl-rhic-ring | georeferenced, **verified** | 20 m | length 3,833.7 m vs 3,862 m (BNL, tol 2%) — **pass**, 0.73% |
| accelerator:ags | drawn | geometry:bnl-ags-ring | georeferenced, kept **approximate** (see conflicts) | 30 m | length 790.5 m vs 807.1 m (BNL 1960 design table, tol 3%) — **pass**, 2.06% |
| (context) Building 488, Berkner Hall | drawn | geometry:bnl-berkner-hall-building | georeferenced (OSM building) | 8 m | — |
| (context) Building 930, Linear Accelerator (200 MeV) | drawn | geometry:bnl-linac-930-building | georeferenced (OSM building) | 8 m | — |
| (context) Building 901, Tandem Van de Graaff | drawn | geometry:bnl-tandem-van-de-graaff-building | georeferenced (OSM building) | 8 m | — |
| (context) Building 820, Accelerator Test Facility | drawn | geometry:bnl-accelerator-test-facility-building | georeferenced (OSM building) | 8 m | — |
| (context) Building 912, AGS Exp. Area | drawn | geometry:bnl-ags-experimental-area-building | georeferenced (OSM building) | 8 m | — |
| (context) Building 942, AGS Booster (approximate area) | drawn | geometry:bnl-ags-booster-area | georeferenced, heavily caveated | 40 m | — |
| accelerator:bnl-linac / accelerator:bnl-booster | **not an atlas entity** | — | — | — | never created in this atlas (ID_REGISTRY.md lists them "optional" for the 'facilities' partition); Buildings 930/901/942 above are drawn as unlinked context only |
| experiment:e949 | **no site/detector record exists** | — | — | — | facility_roles cite facility:brookhaven-national-laboratory only, no site_id field on experiments (A1); nothing to draw or unlocate. Candidate location noted below. |
| facility:jefferson-lab | map:jefferson-lab authored | — | — | — |
| site:jlab-newport-news | drawn | geometry:jlab-newport-news-campus-boundary | georeferenced (OSM/Nominatim way 246018258) | 25 m | address match to JLab's own site-plan document (identity corroboration, not a numeric check) |
| accelerator:cebaf | **unlocated** | — | — | — | Overpass outage (see map.unlocated[] and backlog) |
| (context) CEBAF Center building | drawn | geometry:jlab-cebaf-center-building | georeferenced (OSM/Nominatim way 319579555) | 10 m | — |

**map-entity-unaccounted status: clean for both maps.** Every accelerator and
site that exists as an atlas record for either facility is drawn or (for
accelerator:cebaf only) explicitly unlocated with a sourced reason and backlog.
`map:brookhaven-national-laboratory.unlocated` is empty; `map:jefferson-lab.unlocated`
has exactly the one row.

## Checks (expected vs measured)

All geodesic lengths computed with haversine, R = 6,371,008.8 m, on the
as-drawn coordinates (the numbers below are what `scripts/atlas_osm_extract.py`
printed when the shapes were fetched; `hepgraph.atlas.validate` independently
recomputed the same checks via `geo.py` and reported 0 `geometry-check-failed`
findings for these two maps).

| Feature | Expected | Source | Measured | Diff | Tolerance | Result |
| --- | --- | --- | --- | --- | --- | --- |
| RHIC ring | 3,862 m (2.4 mi) | src:geo-bnl-rhic-by-the-numbers, "ring is 2.4 miles in circumference" | 3,833.7 m | 0.73% | 2% | PASS |
| AGS ring | 807.1 m (computed: 2π × 421.5 ft mean radius) | src:geo-bnl-ags-1960-bulletin, "AGS Design Specifications... Mean radius 421.5 ft." | 790.5 m | 2.06% | 3% | PASS |

No numeric official figure was fetched this session for the STAR or
PHENIX/sPHENIX hall footprints (building dimensions), the BNL or JLab campus
boundary areas, or the CEBAF Center building, so none of those carry a
`checks[]` row — per the contract, "a shape with no possible cross-check stays
approximate", which all of them are.

## Conflicts and honesty calls

1. **AGS ring kept "approximate" despite a passing check.** OSM way 289305285
   is tagged `place=locality` (not `tunnel`, `building`, or `man_made`), i.e.
   it reads as a hand-drawn boundary around the visible ring feature in aerial
   imagery, not an official technical alignment — unlike the RHIC ring
   (way/50074088), which carries `highway=corridor`, `indoor=yes`, `tunnel=yes`
   directly. Per the same honesty principle the CERN researcher applied to the
   SPS ring (a mapper-fitted circle, kept `approximate` despite a passing
   check), I widened `accuracy_m` to 30 m and kept `confidence: approximate`
   even though the length check passes against a rank-2 official source.
2. **AGS ring's expected circumference is my own computation, not a directly
   quoted circumference.** The 1960 BNL Bulletin Board ("Brookhaven's AGS
   Begins Operation", `src:geo-bnl-ags-1960-bulletin`) states the ring's
   diameter in one place ("842.9 feet in diameter, about one-half mile in
   circumference") and its own "AGS Design Specifications" table gives "Mean
   radius: 421.5 ft." separately. I computed circumference = 2π × 421.5 ft =
   2,648.3 ft = 807.1 m myself, stated the computation in the check's `note`,
   and used the *table's own number* (mean radius) as the `quote`/`locator`
   rather than the looser prose "about one-half mile" figure.
3. **Building-number identifications rest on two independent OSM tag matches
   plus one official cross-reference, not memory.** I did not assume "1006 =
   STAR" or "913 = AGS Ring" from general knowledge. Each identification is
   triple-checked: (a) the OSM element's own `name` tag (e.g. "1006", "913 -
   ASG Ring" [OSM's own typo for AGS]); (b) BNL's official central-campus-map
   PDF (`src:geo-bnl-central-campus-map`, fetched and read this session),
   whose building-number key independently states "AGS Ring 913", "Booster
   (AGS) 942", and whose separate "North Area Facility" inset labels map point
   2 (buildings "1006, 1006A") as "STAR DETECTOR / WIDE ANGLE HALL" and map
   point 3 (buildings "1008, 1008A") as "sPHENIX DETECTOR / MAJOR FACILITY
   HALL / SUPPORT BUILDING"; (c) for STAR/PHENIX specifically, a spatial
   consistency check — both hall centroids sit within 55-100 m of the RHIC
   ring's own drawn line (vertex-distance approximation), consistent with an
   interaction-region hall built against the ring, not a coincidence of
   numbering alone.
4. **AGS Booster (Building 942) drawn as an unlinked, heavily-caveated
   context feature, not a ring.** OSM way 996525504 is tagged `place=locality`
   with name "942 - AGS Booster" — a small (span 84 m) hand-labelled area, not
   a tunnel or building trace of the Booster synchrotron's actual ring. No
   `accelerator:bnl-booster` entity exists in this atlas (ID_REGISTRY.md lists
   it as an optional id never created), so even if the shape were trustworthy
   it could not be drawn as a `ring` (which requires an `entity_id`). Drawn as
   `feature_type: "other"`, `entity_id: null`, `accuracy_m: 40`, with the
   method field spelling out that it is not a verified structure outline.
5. **BNL campus boundary fetched from Nominatim, not Overpass, after the
   outage.** `geometry:bnl-upton-campus-boundary` (OSM relation 18896697,
   `landuse=commercial`) came from `nominatim.openstreetmap.org/search`, a
   different OSM web service than the one named in the brief and rules
   (Overpass). It is still third-party OpenStreetMap data under the same
   ODbL licence and carries the same `openstreetmap` source type and
   `approximate` confidence ceiling as every other OSM-alone shape in this
   atlas; I flag the tool substitution here for transparency, not because it
   changes the representation class.
6. **Jefferson Lab site coordinate is wrong by about 13 km — a real error,
   not a refinement.** `site:jlab-newport-news`'s existing coordinate
   (36.98038, -76.42975, from a ROR v2 geocoder record, `precision_m` 800)
   does not describe the Jefferson Lab campus. Nominatim's own search for
   "Thomas Jefferson National Accelerator Facility" returns an OSM way at
   37.0961464, -76.4815621 (bounding box roughly 37.091-37.101 N,
   76.491-76.475 W) whose address, "12000 Jefferson Avenue, Newport News,
   Virginia 23606", is the *exact* street address Jefferson Lab's own
   site-plan document gives for Building 12, the CEBAF Center ("12 CEBAF
   Center - 12000 Jefferson Ave.", `src:geo-jlab-site-plan-detail`). Two
   independent sources — a third-party OSM/Nominatim geocode and JLab's own
   internal building list — agree with each other and disagree with the
   existing ROR-derived site coordinate by about 13 km, well outside that
   record's own 800 m `precision_m`. See "Site coordinate corrections" below;
   per the research contract I did not edit the existing record myself.
7. **AGS/RHIC tunnel depths left `null`.** BNL's 1960 Bulletin Board
   describes the AGS ring only qualitatively as underground ("UNDERGROUND
   MAGNET TUNNEL" diagram label; digging "a circular trench to house magnet
   tunnel"), with no metres/feet-below-grade figure. No source fetched this
   session states a specific depth for the RHIC tunnel either (OSM's
   `layer=-5` tag confirms it is underground but is not a metric depth). Both
   `map:brookhaven-national-laboratory.levels[].depth_m` are `null` with a
   note, per A17, rather than guessed.
8. **JLab tunnel depth: two official pages disagree (25 ft vs 30 ft).**
   `jlab.org/node/14330` ("CEBAF") says "about 25 feet below ground";
   `jlab.org/about/visitors/science/unique` ("Why is JLab Unique?") says "The
   base of the tunnel is 30 feet below the Earth's surface." Both are
   official Jefferson Lab pages fetched this session. Recorded as a range
   (7.6-9.1 m) on `map:jefferson-lab.levels[1].depth_m` with both quotes and
   both sources, rather than silently picking one.

## What is unlocated, and why (see `map.unlocated[]` for the sourced text)

- **accelerator:cebaf** (Jefferson Lab) — Overpass became unreachable before
  any JLab query could run (see "Method note" above). Nominatim's fuzzy name
  search, which did work for the campus boundary and CEBAF Center, returned no
  results for "Hall A/B/C/D", "CEBAF" (beyond the Center and Cebaf Boulevard),
  or "Accelerator Tunnel" — these are almost certainly present in OSM as
  untagged-for-search building/tunnel ways, not absent from OSM, but Nominatim
  could not surface them. No official source gives a georeferenced trace
  either; Jefferson Lab's own site-plan document names the tunnel and halls
  and shows their layout in an aerial photo, but that photo carries no scale
  bar or coordinate grid, so tracing it by eye would not be a sourced
  geometry.

## Backlog (concrete next steps, also in `map.unlocated[].backlog`)

1. **CEBAF racetrack + Halls A-D**: re-run
   `python scripts/atlas_osm_extract.py --map jefferson-lab --bbox 36.968,-76.445,36.993,-76.415 --filter 'way["tunnel"="yes"]' --filter 'way["name"~"CEBAF|Hall A|Hall B|Hall C|Hall D",i]'`
   once Overpass is reachable again; cross-check the tunnel's length against
   "7/8 of a mile" (~1,408 m, `src:geo-jlab-node-14330-cebaf-page` and
   `src:geo-jlab-accelerator-unique-page`, both already fetched and cited on
   `map:jefferson-lab`) and the building numbers already confirmed in
   `src:geo-jlab-site-plan-detail` (999 = Accelerator Tunnel, 101 = Hall A,
   94 = Hall B, 96 = Hall C, 203 = Hall D).
2. **AGS Booster (accelerator:bnl-booster) and BNL Linac
   (accelerator:bnl-linac)**: these have no atlas accelerator entity at all
   (ID_REGISTRY.md, "facilities" row, lists them as optional and unmade).
   Buildings 942/930/901 are drawn here as unlinked context only. A future
   pass that creates these entities can promote `geometry:bnl-ags-booster-area`
   to a proper `ring`/`accelerator` feature once a better OSM trace or an
   official source (not just a `place=locality` tag) is found for the
   Booster's actual ring.
3. **E949's location at BNL**: no atlas site or detector record exists for
   E949 (an AGS fixed-target experiment). Building 912, "AGS Exp. Area"
   (drawn here as `geometry:bnl-ags-experimental-area-building`, entity_id
   null), is a plausible candidate area for whoever creates that site record
   — not asserted as E949's location here, since no source fetched this
   session ties E949 specifically to Building 912.
4. **RHIC and AGS tunnel depths**: no fetched source gives a metres-below-
   grade figure for either tunnel (see conflict #7); the BNL Design Report
   Vol. I or a NIM overview paper (Nucl. Instrum. Meth. A 499 (2003) 235,
   named in the research brief but not fetched this session) may have it.
5. **BNL's remaining ~140 named OSM buildings**: the brief's lead mentioned
   "an OSM survey found ~150 named buildings"; this pass drew the 5 most
   directly accelerator-relevant ones by name search (Berkner Hall, Linear
   Accelerator, Tandem Van de Graaff, Accelerator Test Facility, AGS Exp.
   Area) plus the two detector halls. A fuller campus texture pass (dozens
   more numbered buildings) is possible but was out of scope for the time
   available this session.
6. **JLab depth conflict (25 ft vs 30 ft)**: worth a targeted fetch of a
   JLab technical/design document (e.g. the original CEBAF Design Report or
   a NIM paper on the accelerator) to resolve which figure — or whether both
   are correct at different points along the tunnel — is authoritative.

## Site coordinate corrections

Written to a JSON list for the integrator per the brief's instructions
(4 rows: 1 real correction, 2 refinements, 1 "no change needed" confirmation).
Not applied to the site records themselves (out of scope for a geometry
researcher). The full list, with `site_id`, `lat`, `lon`, `precision_m`,
`kind`, `sources`, `locator` and a `note` explaining each:

```json
[
  {
    "site_id": "site:jlab-newport-news",
    "lat": 37.0989568, "lon": -76.4815705, "precision_m": 500, "kind": "campus",
    "sources": ["src:geo-jlab-nominatim-campus-boundary", "src:geo-jlab-site-plan-detail"],
    "locator": "Vertex-average centroid of the campus boundary, OSM/Nominatim relation search for 'Thomas Jefferson National Accelerator Facility' (way/246018258, amenity=research_institute, address '12000 Jefferson Avenue, Newport News, Virginia 23606'). Independently corroborated by Jefferson Lab's own site-plan document, which gives the identical street address for Building 12 ('12 CEBAF Center - 12000 Jefferson Ave.'). A second, tighter Nominatim point for the same way (its own reported centroid) is 37.0961464, -76.4815621, within 310 m of the value recorded here.",
    "note": "CORRECTION, not a refinement: the existing coordinate (36.98038, -76.42975, source src:facilities-verify-jlab-ror, a ROR v2 geocoded point, precision_m 800) is approximately 13.0 km south-southeast of the true campus location. Recommend replacing the coordinate entirely, not merely tightening precision_m."
  },
  {
    "site_id": "site:bnl-rhic-ip6-star",
    "lat": 40.8794304, "lon": -72.8780173, "precision_m": 100, "kind": "detector",
    "sources": ["src:geo-bnl-osm-star-hall", "src:geo-bnl-central-campus-map"],
    "locator": "Vertex-average centroid of OSM building footprints way/471294025 ('1006') and way/471294133 ('1006A'), combined. Identity confirmed by BNL's own central-campus-map, whose 'North Area Facility' inset labels map point 2, keyed to buildings '1006, 1006A', as 'STAR DETECTOR / WIDE ANGLE HALL'.",
    "note": "REFINEMENT: existing coordinate (40.86954, -72.88677, campus-wide ROR point, precision_m 1500) is ~526 m from this value, well inside its own precision_m -- not a contradiction, a tighter replacement. Recommend kind: campus -> detector."
  },
  {
    "site_id": "site:bnl-rhic-ip8-phenix-sphenix",
    "lat": 40.8831273, "lon": -72.8822600, "precision_m": 100, "kind": "detector",
    "sources": ["src:geo-bnl-osm-phenix-sphenix-hall", "src:geo-bnl-central-campus-map"],
    "locator": "Vertex-average centroid of OSM building footprints way/471294039 ('1008') and way/471294038 ('1008A'), combined. Identity confirmed by BNL's own central-campus-map, map point 3, keyed to '1008, 1008A', labelled 'sPHENIX DETECTOR / MAJOR FACILITY HALL / SUPPORT BUILDING'.",
    "note": "REFINEMENT: existing coordinate is ~529 m from this value, well inside its own precision_m of 1500. Recommend kind: campus -> detector."
  },
  {
    "site_id": "site:bnl-upton-campus",
    "lat": null, "lon": null, "precision_m": null, "kind": "campus",
    "sources": ["src:geo-bnl-nominatim-campus-boundary"],
    "locator": "OSM/Nominatim relation 18896697 ('Brookhaven National Laboratory', landuse=commercial); its own reported centroid is 40.8745102, -72.8667428, about 1.77 km from the existing site coordinate.",
    "note": "NO CORRECTION NEEDED: existing coordinate is comfortably inside its own precision_m of 3000. Listed for completeness only."
  }
]
```

## Sources added

14 new source records: 9 `src:geo-bnl-*` (5 OpenStreetMap/Nominatim extracts,
1 BNL fact sheet, 1 BNL campus-map PDF, 1 BNL 1960 historical bulletin, 1
Nominatim campus-boundary relation) and 5 `src:geo-jlab-*` (2
OpenStreetMap/Nominatim extracts, 1 JLab site-plan PDF, 2 official jlab.org
pages); see `data/atlas/sources/geo-bnl-*.json` and
`data/atlas/sources/geo-jlab-*.json`. No existing source, site, detector,
accelerator or beamline record was edited.

## Validator / build / test results

- `.venv/bin/python -m hepgraph.atlas.validate`: **0 errors**, 1,592 warnings,
  4 informational — the exact same warning/informational count as the
  pre-existing baseline (i.e. this pass introduced zero new warnings; one
  drafted display-string A21 warning on `map:jefferson-lab`'s depth quantity
  was caught and fixed before finishing, the same class of issue the CERN
  researcher hit on `map:cern`).
- `.venv/bin/python -m hepgraph.atlas.build`: succeeds; `geometry/brookhaven-
  national-laboratory.json` has 11 features, bbox
  `[-72.901262, 40.8463541, -72.836824, 40.8949077]`;
  `geometry/jefferson-lab.json` has 2 features, bbox
  `[-76.490768, 37.0907812, -76.4747628, 37.1012222]`; both attribute
  `["© OpenStreetMap contributors (ODbL-1.0)"]`. `scripts/atlas_coverage_report.py`
  regenerates a "Local map geometry" table row for each map (11/0/0/2 checks
  passed for BNL; 2/1 unlocated for JLab) with no changes needed to the
  script itself.
- `.venv/bin/python -m pytest -q tests/test_atlas_validate.py
  tests/test_atlas_build.py tests/test_atlas_geo.py
  tests/test_atlas_geometry_data.py tests/test_atlas_tools.py`: **233
  passed**.
- `.venv/bin/python -m pytest -q` (full suite): **667 passed, 139 skipped**
  (skips are the PostgreSQL/Neon integration tests, which skip without
  `HEPGRAPH_TEST_DATABASE_URL`/`HEPGRAPH_TEST_POSTGRES_DSN` per CLAUDE.md;
  none of this session's work touches the database layer).
