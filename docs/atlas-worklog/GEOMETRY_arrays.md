# Geometry worklog: ground-based astroparticle arrays

Researcher: geometry-arrays. Worktree `/Users/yatharthsirohi/Desktop/HEP-Graph-maps-arrays`,
branch `hep-atlas-local-maps-arrays`. Sources prefixed `src:geo-arrays-*`.
Facilities covered: Pierre Auger Observatory, H.E.S.S., CTAO-South (Paranal),
LHAASO (Daocheng), Telescope Array (Utah), Roque de los Muchachos (MAGIC +
CTAO-North/LST-1), Sierra Negra (HAWC), Fred Lawrence Whipple Observatory
(VERITAS) — eight facilities, eight maps.

## Method note: Overpass access this session

Overpass was **unreachable for the entire session**: every attempt from the
maintainer script (`overpass-api.de`) and a direct call to the `lz4` mirror
returned either `HTTP 504`, `HTTP 429`, or (for most of the session)
`Connection refused` — the same degraded-service pattern the CERN researcher
documented, but here it never recovered across roughly a dozen attempts spread
over the whole session (paced ≥60 s apart after each failure, small bboxes,
the maintainer script's own `HEP-Atlas-research/1.0` User-Agent, one query in
flight at a time). The brief's own leads specifically point to OpenStreetMap
for cross-checking H.E.S.S., Roque and Whipple telescope buildings; none of
that could be attempted. This is the single biggest gap in this pass — see
backlog. Everything below was researched instead via WebSearch/WebFetch of
official pages and arXiv papers, an r.jina.ai text-extraction proxy for PDFs
that WebFetch could not parse directly (their binary/FlateDecode streams
render as garbage to WebFetch's own PDF handling), and — for Pierre Auger —
the Observatory's own public Open Data release (real per-station survey
coordinates, better than anything Overpass would have offered).

## Inventory

| Entity | Drawn? | Feature(s) | Representation | Accuracy | Check |
| --- | --- | --- | --- | --- | --- |
| facility:pierre-auger-observatory | map authored | — | — | — | — |
| site:malargue-auger / experiment:pierre-auger-observatory | drawn | geometry:auger-sd1500-array-boundary (site), geometry:auger-sd750-infill-boundary (experiment) | derived (convex hull of real station survey data) | 50 m | area 3160.6 km² vs 3000 km² official figure — **pass**, 5.35% (tol 8%) |
| facility:hess-khomas-highland | map authored | — | — | — | — |
| site:khomas-highland-hess / experiment:h-e-s-s | drawn | geometry:hess-ct1-4-square (site), geometry:hess-ct5-point (experiment) | derived / surveyed | 200 m / 200 m | perimeter 480.01 m vs 480 m (4×120 m) — **pass**, 0.001% |
| facility:fred-lawrence-whipple-observatory | map authored | — | — | — | — |
| site:mount-hopkins-veritas / experiment:veritas | drawn | geometry:veritas-array-point | surveyed | 100 m | none (single reference point) |
| facility:ctao-south-paranal | map authored | — | — | — | — |
| site:paranal-cta-south / experiment:ctao | drawn | geometry:ctao-south-array-point | surveyed | 100 m | none (single reference point) |
| facility:roque-de-los-muchachos-observatory | map authored | — | — | — | — |
| site:roque-de-los-muchachos-gamma-ray-array / experiment:magic | drawn | geometry:magic-array-point (site) | georeferenced | 500 m | none |
| experiment:ctao (CTAO-North / LST-1) | drawn | geometry:ctao-north-lst1-point | georeferenced | 500 m | none |
| facility:sierra-negra | map authored | — | — | — | — |
| site:hawc-sierra-negra / experiment:hawc | drawn | geometry:hawc-array-point | surveyed | 600 m | none (single reference point) |
| facility:lhaaso-daocheng | map authored | — | — | — | — |
| site:lhaaso-haizi-mountain / experiment:lhaaso | drawn | geometry:lhaaso-array-point | georeferenced | 5000 m | none |
| facility:telescope-array-utah | map authored | — | — | — | — |
| site:telescope-array-utah-central-site / experiment:telescope-array | drawn | geometry:ta-array-point | surveyed | 6000 m | none (single reference point) |

11 geometry records total across 8 maps. No entity was left `unlocated[]`:
every one of these eight facilities has exactly one site and one
experiment/detector, and both are drawn on that facility's map (as required
by `map-entity-unaccounted`, which checks a *site* id, not a detector/
experiment id — see conflict #2 below). None of these facilities has an
`accelerator` or `beamline` record, so that half of the honesty rule is
vacuous here. What is genuinely missing is **finer-grained detail below the
level of an atlas entity** — individual telescope/tank/station positions —
which is not an omission the validator's `unlocated[]` mechanism covers
(there is no `site:` or `detector:` record per H.E.S.S. telescope, per
Auger fluorescence building, etc.), so it is recorded as backlog below and in
each geometry record's own `notes[]` instead.

## Checks (expected vs measured)

| Feature | Expected | Source | Measured | Diff | Tolerance | Result |
| --- | --- | --- | --- | --- | --- | --- |
| Auger SD1500 array area | 3000 km² | src:cosmic-gamma-auger-official-observatory-page, "3000 km2 array of 1660 particle detectors" | 3160.6 km² | +5.35% | 8% | PASS |
| H.E.S.S. CT1-4 square perimeter | 480 m (4×120 m) | src:geo-arrays-hess-telescopes-page, "square with 120 m side length" | 480.006 m | +0.001% | 2% | PASS |

The H.E.S.S. check is close to circular by construction (the square's own
120 m side is exactly what was used to build it, the same pattern the CERN
researcher used for the PSB ring): it confirms the geodesic-destination-point
computation was done correctly, not an independent fact. The Auger check is a
genuine independent cross-check: the polygon's 32 vertices are real surveyed
GPS station positions from the Observatory's own Open Data release, and the
area they enclose was never an input to that computation, only a downstream
consequence of it — the 5.35% gap comes from convex-hull-vs-true-footprint
overestimation and from "3000 km²" itself being a round public figure, not
from any circularity.

## Auger surface-detector array: what the Open Data release made possible

The brief's own leads suggested drawing Auger's footprint "through the
published FD/boundary points" if sourced, "else FD points only." Neither was
needed: the Pierre Auger Collaboration publishes `sdMap.csv` (UTM
northing/easting, altitude, activity window and sd1500/sd750 sub-array
membership for every station) as part of its Open Data release
(`https://opendata.auger.org/`, Zenodo record 10488964). This session
downloaded it directly (`curl` succeeded against `opendata.auger.org`
throughout, unlike Overpass), converted UTM zone 19S to WGS84 with the
standard Snyder inverse-UTM series, and computed a convex hull:

- **Main array** (`sd1500=1`, 1640 of 1690 rows): 32-vertex hull, area
  3160.6 km², perimeter 208.0 km. `geometry:auger-sd1500-array-boundary`,
  `representation: derived`, `accuracy_m: 50`.
- **Infill array** (`sd750=1`, 71 rows): 12-vertex hull, area 29.3 km²,
  perimeter 20.2 km. `geometry:auger-sd750-infill-boundary`, same
  representation/accuracy. This does **not** closely match the "23.5 km²,
  61-detector" infill figure quoted in a 2026 collaboration paper — no
  `checks[]` row is asserted for it (see conflict #1 below).

Both are convex hulls, not the true (mildly concave) instrumented boundary,
and both include every station ever flagged with that sub-array membership
regardless of the CSV's own `start`/`stop` activity window — i.e. the maximal
historical footprint. `accuracy_m: 50` is this session's own honest allowance
for both effects, since the dataset states no per-station GPS survey
precision.

## Conflicts and honesty calls

1. **Auger infill-array area mismatch, no check asserted.** The 71 stations
   flagged `sd750=1` in `sdMap.csv` enclose 29.3 km², 24.7% more than the
   "23.5 km², 61-detector" infill figure quoted in
   `src:cosmic-gamma-ta-arxiv-2026-recent-findings`-adjacent 2026 collaboration
   literature. The station *count* itself doesn't match either (71 vs 61), so
   this is very likely a different, looser definition of "infill station" in
   the CSV's own flag than whatever defines the quoted 61-detector array (it
   may include AMIGA/HEAT-related stations, or the dataset may reflect a
   later, larger, infill deployment than the quoted paper's). Rather than
   force a `checks[]` row against a figure that may not describe the same
   set — which would either fail outright or need an unjustifiably wide
   tolerance — this is reported as a residual, following the same principle
   the CERN researcher used for Linac4's building-footprint-vs-beam-length
   mismatch.
2. **`entity_id` is the site, not the detector/experiment, for the "primary"
   feature per map.** First draft linked every array feature to its
   `experiment:*` id. The validator's `map-entity-unaccounted` warning walks
   every `detector` record's `placements[].site_id` and checks whether *that
   site id* — not the detector id — appears as some geometry record's
   `entity_id`; it does not consult `site_id` on the geometry record at all.
   This is the exact same rule and the exact same fix the CERN researcher
   documented (their conflict #6). Re-pointed one "primary" feature per
   facility to its site id (`geometry:auger-sd1500-array-boundary`,
   `geometry:hess-ct1-4-square`, `geometry:veritas-array-point`,
   `geometry:ctao-south-array-point`, `geometry:magic-array-point`,
   `geometry:lhaaso-array-point`, `geometry:hawc-array-point`,
   `geometry:ta-array-point`); secondary features on the same map
   (`geometry:hess-ct5-point`, `geometry:auger-sd750-infill-boundary`,
   `geometry:ctao-north-lst1-point`) keep their more specific
   `experiment:*` entity link, which is still meaningful to click.
3. **A duplicate arXiv/URL source, caught by the validator, not by me.**
   First draft created `src:geo-arrays-hawc-coordinates-design-paper` citing
   arXiv:1310.0074 for the HAWC site coordinate, not realising the
   cosmic-gamma workstream had already created
   `src:cosmic-gamma-hawc-design-paper-arxiv-2013` for the same paper (for its
   altitude quote). `hepgraph.atlas.validate` correctly reported
   `duplicate-external-id` and `duplicate-source-url` (both errors). Per
   RESEARCH_AGENT_RULES §4 ("grep for the same URL/DOI and reuse it"),
   deleted my new source and re-pointed both citations (the geometry record's
   `geometry.sources` and the map's `sources`) to the existing id; a
   citing record's own `quote`/`locator` carries the specific claim
   regardless of which source record it points at, so no information was
   lost.
4. **HAWC and Telescope Array site-coordinate upgrades, used.** Both
   facilities' existing site records carry an explicitly-flagged coarse point
   (a geocode of a nearby peak/town, not the array itself). This session
   found the arrays' *own* published coordinates in their primary technical
   papers — see "Site coordinate corrections" below — and used those
   (not the old points) as each map's centre and the geometry `array`
   feature's own position, while leaving the underlying `site:` record
   untouched per the brief's rules.
5. **LHAASO and Roque coordinate candidates found but NOT used.** A tighter
   LHAASO coordinate (29°21'27.6"N, 100°08'19.6"E) and the commonly-quoted
   MAGIC coordinate (28°45'43"N 17°53'24"W) both appear repeatedly across
   independent WebSearch results, both attributed to a primary source (the
   LHAASO Science Book, arXiv:1905.02773; MAGIC/LST technical papers
   respectively). Every attempt to fetch either primary source directly this
   session failed to render as readable text: WebFetch on the raw PDF, the
   `ar5iv.labs.arxiv.org` HTML mirror, `arxiv.org/html/...`, and an
   `r.jina.ai` text-extraction proxy (which *did* work for several other
   PDFs this session — HAWC's design paper, the TA SD-array paper, three
   Auger fluorescence-detector papers) all returned either binary garbage,
   a 404, or an explicit "no coordinates found" answer for these two
   specific documents. Per the "nothing from memory / a quote you actually
   saw" standard, neither value is used in a geometry or map record; both are
   listed as unverified candidates below for whoever can get a clean fetch
   (a library PDF-to-text tool, or Overpass once it is reachable again, would
   likely resolve MAGIC's case via an OSM trace of the dish itself).

## What is not drawn, and why (backlog)

None of this is a formal `map.unlocated[]` row — there is no unresolved
*entity* (accelerator/beamline/site/experiment) at any of these eight
facilities; everything that has an atlas record is drawn. What follows is
finer detail below entity level, recorded here and in each affected
geometry record's own `notes[]` per the brief's "unlocated entries with
reasons" and "concrete backlog" instructions.

1. **All of H.E.S.S./VERITAS/MAGIC/LST-1/Roque's individual telescope
   positions.** The brief's own leads suggested using OpenStreetMap as a
   cross-check here specifically ("Roque, HESS, Whipple often mapped").
   Overpass refused every connection for the whole session (see method
   note); once it is reachable again, a `nwr["name"~"CT1|CT2|CT3|CT4|CT5"]`
   / `T1|T2|T3|T4` / `MAGIC|LST` search in a small bbox around each site's
   own coordinate should resolve these directly, the same way the CERN
   researcher resolved CERN's building footprints.
2. **Auger's four fluorescence-detector buildings** (Los Leones, Los
   Morados, Loma Amarilla, Coihueco). Despite fetching arXiv 1502.01323,
   0907.4282 and 1011.6523 (WebFetch directly and via an `r.jina.ai` proxy),
   the Auger Open Data portal's own dataset listing, and several web
   searches, no individual FD coordinate was seen verbatim in any fetched
   source this session — only the overall observatory bounding
   box/lat-lon. Backlog: an Auger GAP note, PhD thesis, or the
   `fdGeometry`-style dataset (not found under that name in the current Open
   Data release; only `fdPixelMap.csv`, which gives pixel pointing angles,
   not site coordinates) with per-site coordinates; or an OSM trace once
   Overpass recovers (these are named buildings, plausible OSM candidates).
3. **Telescope Array's 507-station 1.2 km SD grid and its three
   fluorescence-detector sites** (Black Rock Mesa, Long Ridge, Middle Drum).
   Coordinates for the three FD sites are extremely easy to find online, but
   every instance traces back to the same non-primary source
   (`cleardarksky.com`, an amateur-astronomy clear-sky-chart site — also
   Wikipedia's own footnote for these exact values), not to an official TA
   page or paper. `telescopearray.org` and known mirrors were unreachable
   this session (DNS/connection failures), matching what the existing
   facility record already documents. Backlog: the TA NIM/detector papers'
   own station tables (e.g. Kawai et al. or the individual FD design papers),
   or telescopearray.org once reachable.
4. **LHAASO's KM2A and WCDA shapes.** Both are well described in the
   literature — KM2A is explicitly stated to be circular (core radius
   ~575 m, outer guard ring to ~635 m) and WCDA is 78,000 m² across two
   150×150 m pools plus one 300×110 m pool — but neither can be honestly
   anchored: doing so would need a centre coordinate precise to well under
   each shape's own size, and the only coordinate available this session
   (a 5000 m-precision Nominatim geocode) is far too coarse
   (`geometry-derived-from-coarse-anchor`). Backlog: the precise LHAASO
   Science Book coordinate (see conflict #5) or an official IHEP/LHAASO site
   plan, once fetchable.
5. **HAWC's 300-tank footprint shape.** The array's own paper gives area
   (~20,000-22,500 m²) and per-tank size (7.3 m diameter) but no stated
   overall outline (circular/hexagonal/irregular) — "tanks are placed in
   joint pairs of rows" is a packing description, not a boundary. Not drawn
   as a polygon; backlog: a HAWC layout diagram or GIS file with tank-by-tank
   or corner coordinates.
6. **CTAO-South's planned telescope grid.** The eventual configuration (2
   LST + 14 MST + 37 SST) is published, but no individual pad coordinates
   are, consistent with the facility's own "construction" status. Backlog:
   CTAO's own construction-progress pages once telescopes are surveyed and
   published.

## Site coordinate corrections

Per the brief's instruction ("record it in your worklog under 'site
coordinate corrections' with the source; the integrator applies them").
Two solid corrections (fetched primary-source quotes, both notably tighter
than the existing points and about the array itself rather than a nearby
town/peak), plus two unverified candidates found but not confirmed by a
direct fetch this session.

```json
{
  "corrections": [
    {
      "site_id": "site:hawc-sierra-negra",
      "current": {"lat": 18.9862137, "lon": -97.3151017, "precision_m": 3000,
                   "note": "Nominatim geocode of the Sierra Negra peak"},
      "proposed": {"lat": 18.99, "lon": -97.31, "precision_m": 600},
      "source": "src:cosmic-gamma-hawc-design-paper-arxiv-2013",
      "locator": "The HAWC Gamma-Ray Observatory: Design, Calibration, and Operation, site-description section (text retrieved via an r.jina.ai proxy after WebFetch could not parse the PDF directly)",
      "quote": "The geographical latitude of the site is 18.99 ... The geographical longitude of the HAWC site, 97.31 W.",
      "status": "confirmed by direct fetch this session"
    },
    {
      "site_id": "site:telescope-array-utah-central-site",
      "current": {"lat": 39.3521777, "lon": -112.57717, "precision_m": 15000,
                   "note": "Nominatim geocode of the town of Delta, Utah; the existing record itself says this is NOT a survey point for the array"},
      "proposed": {"lat": 39.3, "lon": -112.9, "precision_m": 6000},
      "source": "src:geo-arrays-ta-site-paper",
      "locator": "The surface detector array of the Telescope Array experiment (arXiv:1201.4964), site-description section (ar5iv HTML mirror)",
      "quote": "The TA site is located in the desert about 1400 m above sea level centered at 39.3 N and 112.9 W in Millard County, Utah, USA",
      "status": "confirmed by direct fetch this session"
    },
    {
      "site_id": "site:lhaaso-haizi-mountain",
      "current": {"lat": 29.385696, "lon": 100.1483762, "precision_m": 5000,
                   "note": "Nominatim geocode of a rest area on the Haizi Mountain route"},
      "candidate": {"lat": 29.357667, "lon": 100.138778, "precision_m": 30},
      "candidate_source_claimed": "LHAASO Science Book, arXiv:1905.02773, said to state '(29 21'27.6\"N, 100 08'19.6\"E)'",
      "status": "UNVERIFIED: repeatedly attributed to this paper by independent WebSearch results, but no direct fetch this session (WebFetch on the PDF, ar5iv, arxiv.org/html, and an r.jina.ai proxy) could render the paper's own text to confirm it verbatim. Do not apply without independent confirmation."
    },
    {
      "site_id": "site:roque-de-los-muchachos-gamma-ray-array",
      "current": {"lat": 28.757069, "lon": -17.8888436, "precision_m": 500,
                   "note": "Nominatim geocode of the general observatory campus"},
      "candidate": {"lat": 28.761944, "lon": -17.89, "precision_m": 100},
      "candidate_source_claimed": "Commonly cited as 28d45'43\"N 17d53'24\"W in MAGIC/CTA secondary sources and Wikipedia",
      "status": "UNVERIFIED: no MAGIC/LST technical paper fetched this session (WebFetch, ar5iv, r.jina.ai) returned this coordinate verbatim. Do not apply without independent confirmation; would also still not separate MAGIC-I/MAGIC-II/LST-1 from each other."
    }
  ]
}
```

## Sources added

4 new `src:geo-arrays-*` records (see `data/atlas/sources/geo-arrays-*.json`):
the H.E.S.S. Telescopes page (array-layout quote), the Pierre Auger Open Data
`sdMap.csv` release, and the TA surface-detector-array paper. (A fifth,
duplicating an existing cosmic-gamma HAWC source, was created and then
deleted — see conflict #3.) No existing source, site, detector, facility or
experiment record was edited; every citation of a pre-existing source
(`src:cosmic-gamma-*`) reuses the id verbatim.

## Validator / build / test results

- `.venv/bin/python -m hepgraph.atlas.validate`: **0 errors**, 1594 warnings
  (all pre-existing across the rest of the atlas dataset except the two
  documented above: `map-center-far` on `map:pierre-auger-observatory`
  (centroid of the real array is ~40 km from the administrative HQ address,
  which is what it is) and `geometry-duplicate-shape` on
  `geometry:magic-array-point`/`geometry:ctao-north-lst1-point` (both
  experiments genuinely share one unresolved ~500 m patch of Roque de los
  Muchachos)).
- `.venv/bin/python -m hepgraph.atlas.build`: succeeds; all 8 new map bundles
  well under the 2 MB cap (largest is `pierre-auger-observatory.json` at
  12.3 kB).
- `.venv/bin/python -m pytest -q tests/test_atlas_validate.py
  tests/test_atlas_build.py tests/test_atlas_geo.py
  tests/test_atlas_geometry_data.py tests/test_atlas_tools.py`: **233
  passed**.
- `.venv/bin/python -m pytest -q` (full suite): **667 passed, 139 skipped**
  (skips are all pre-existing PostgreSQL-backed tests with no
  `HEPGRAPH_TEST_DATABASE_URL`/`HEPGRAPH_TEST_POSTGRES_DSN` set, unrelated to
  this work).
