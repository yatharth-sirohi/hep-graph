# Release geometry stream "arrays-b": ground-based gamma-ray and air-shower observatories

Researcher: arrays-b. Worktree `/Users/yatharthsirohi/Desktop/HEP-Graph-ar-arrays2`,
branch `atlas-release-arrays2`. Sources prefixed `src:geo-arrays2-*`. Date of
research: 2026-10-25. Starting point: `docs/atlas-worklog/GEOMETRY_arrays.md`
(its backlog item 1 and 5 and 6 were this stream's task).

Facilities: H.E.S.S. (Khomas Highland), CTAO-South (Paranal), Roque de los
Muchachos (MAGIC, LST-1..4, CTAO-North), Sierra Negra (HAWC), Fred Lawrence
Whipple Observatory (VERITAS).

## Method note: how OpenStreetMap was read this session

Overpass (`overpass-api.de` and the `lz4` mirror) answered `HTTP 502, "at
capacity ... query workers are busy and the request queue is full"` for the
H.E.S.S. query at 10:30 and 10:34 UTC. Rather than loop, the same small
bounding boxes (about 0.03 x 0.03 degrees, well under the API's 0.25 square
degree limit) were read once each through the OpenStreetMap editing API
`https://api.openstreetmap.org/api/0.6/map.json?bbox=W,S,E,N`, with the
`HEP-Atlas-research/1.0` User-Agent and at least 6 s between calls. That call
returns the current version of every element touching the box, so the data is
as current as Overpass would be, but it has no `osm3s.timestamp_osm_base`.
Each record therefore carries `osm.timestamp` = **the fetch time of the API
call** (the extract is a live read at that instant) and `locator` names every
element's version and last-edit timestamp. Raw responses are in the session
scratch directory, not in the repository. Fetch times (UTC, 2026-10-25):
H.E.S.S. 10:35:43, CTAO-South 10:38:39, Roque 10:38:47, HAWC/Sierra Negra
10:38:54, VERITAS 10:39:02.

Telescope polygons are used verbatim (no simplification). Confidence for an
OpenStreetMap trace is `approximate` throughout, even where a distance check
against an official figure passes: such a check confirms the relative placement
of the telescopes, not the outline of any one polygon.

Verification of the repository state at the end: see "Validator, build" at the
bottom.

---

## 1. H.E.S.S. (`map:hess-khomas-highland`)

Grade before: **partial** (2 features: a derived square at the published array
coordinate, a point for CT5). Grade after: **layout to scale** (9 features:
the CT1-CT4 array outline, five telescope footprints, control building,
residence building, site compound).

| Entity / feature | Drawn? | Representation | accuracy_m | Check (expected vs measured) |
| --- | --- | --- | ---: | --- |
| `geometry:hess-ct-north/east/south/west` (the four 12 m telescopes, experiment:h-e-s-s) | drawn | georeferenced (OSM ways 171900951/954/955/956) | 10 | distance to clockwise neighbour, expected 120 m: north-east 121.2, east-south 118.6, south-west 118.2, west-north 121.2 m: all pass at 3 % |
| `geometry:hess-ct5` (28 m telescope) | drawn | georeferenced (OSM way 171900953) | 10 | distance to each corner telescope, expected 84.85 m (= 120 m / sqrt 2, derived from the published square with CT5 at its centre): 86.0, 83.2, 84.7, 84.9 m: all pass at 3 % |
| `geometry:hess-ct1-4-square` (site:khomas-highland-hess) | drawn | derived (quadrilateral through the four corner-telescope centroids) | 10 | perimeter, expected 480 m (4 x 120 m): measured 479.2 m, pass at 3 % (0.17 %) |
| `geometry:hess-control-building` | drawn | georeferenced (OSM way 171900949) | 8 | none: no official dimension found |
| `geometry:hess-residence-building` | drawn | georeferenced (OSM way 171900957) | 8 | none: review says only "a few hundred meters away" (centroid is about 810 m from the square) |
| `geometry:hess-site-compound` | drawn | georeferenced (OSM landuse polygon, way 171900958) | 15 | none; a land-use outline, not a fence or survey boundary |
| `map.unlocated[]` | empty | | | nothing of this facility's inventory is unplaced |

Principal sources: OSM ways above (`https://www.openstreetmap.org/way/<id>`);
H.E.S.S. Telescopes page `https://www.mpi-hd.mpg.de/HESS/pages/about/telescopes/`
("arranged in form of a square with 120 m side length. The diagonal of the
square is oriented north-south"; "an single huge dish ... was added at the
center of the array"); Aharonian et al. 2006, Crab paper,
`https://arxiv.org/abs/astro-ph/0607333` ("placed in a square formation with a
side length of 120 metres"); Puhlhofer, Leuschner, Salzmann 2024,
`https://arxiv.org/abs/2405.11104` (control building, residence "a few hundred
meters away", CT5 reflector "equivalent to a circular reflector with a
diameter of 28 m").

Independent consistency checks that are not `checks[]` rows (a published
coordinate is not a shape): the collaboration's array coordinate
(23d16'18" S, 16d30'00" E, good to one arc-second) lies 20.7 m from the OSM
CT5 centroid, well inside the arc-second rounding plus a mapper's tracing error.

Source conflicts and judgement calls:

* OSM tags CT5 `telescope:diameter=25m`; the 2024 review states a reflector of
  24 m x 32 m, a circular equivalent of 28 m. The OSM tag is ignored. The CT5
  footprint's span (29.7 m) matches neither number exactly because it is the
  telescope structure.
* The four corner telescopes cannot be numbered CT1-CT4: no fetched source
  assigns telescope numbers to corners, and OSM names all four "H.E.S.S.".
  They are named by compass corner (a fact the H.E.S.S. page supports: the
  square's diagonal runs north-south, and the OSM centroids bear 0, 90, 180,
  270 degrees from CT5 to within 1.3 degrees).
* The earlier derived square (placed on the published array coordinate, 200 m
  accuracy) and the CT5 point that reused the same coordinate are replaced; the
  id `geometry:hess-ct1-4-square` is kept, `geometry:hess-ct5-point` is removed
  in favour of `geometry:hess-ct5` (a footprint, not a point).

Site coordinate corrections: none required. `site:khomas-highland-hess`
(-23.271667, 16.5, precision_m 200) is consistent with the OSM CT5 centroid
(20.7 m away). Optional tightening: the source states the coordinate to one
arc-second (about 30 m), so `precision_m` could be lowered from 200 to 50; this
is left to the integrator.

Not drawn and why (backlog):

1. CT1..CT4 numbering of the corner telescopes: a H.E.S.S. instrument paper or
   an array-layout table (ctapipe / H.E.S.S. DL3 release notes do not carry
   it).
2. Other unnamed OSM buildings in the compound (the review says the site has
   "multiple halls for the storage of spare parts and technical equipment"):
   none is identified as a hall, so none is drawn.
3. The 36 m / 13.6 m azimuth rails: stated as rail diameters in the review but
   not mapped.

---

## 2. VERITAS at the Whipple Observatory basecamp (`map:fred-lawrence-whipple-observatory`)

Grade before: **partial** (1 feature: a single reference point). Grade after:
**layout to scale** (6 features: array outline, four telescopes, basecamp
landuse outline).

| Entity / feature | Drawn? | Representation | accuracy_m | Check (expected vs measured) |
| --- | --- | --- | ---: | --- |
| `geometry:veritas-t1` .. `-t4` (experiment:veritas; four 12 m telescopes) | drawn | georeferenced (OSM nodes 664910895 T1, 664910802 T2, 664910876 T3, 664910849 T4) | 15 | spacings from Perkins and Maier 2009 Figure 1 labels, tolerance 7 %: T1-T2 99 m vs 105.3 (+6.4 %); T2-T4 102 vs 98.1 (-3.8 %); T4-T3 81 vs 81.6 (+0.7 %); T3-T1 127 vs 125.1 (-1.5 %); T3-T2 111 vs 112.2 (+1.1 %): all pass |
| `geometry:veritas-array-quadrilateral` (site:mount-hopkins-veritas) | drawn | derived (quadrilateral T1-T2-T4-T3 through the OSM nodes) | 15 | perimeter, expected 409 m (99+102+81+127): measured 410.1 m, pass at 3 % (0.27 %) |
| `geometry:veritas-basecamp-landuse` | drawn | georeferenced (OSM way 52218708, landuse polygon named FLWO) | 20 | none |
| basecamp buildings | not drawn | | | unnamed OSM polygons, no fetched source identifies them |
| `map.unlocated[]` | empty | | | nothing of this facility's inventory is unplaced |

The previous single point `geometry:veritas-array-point` is removed (the array
outline carries the site id).

Principal sources: OSM nodes `https://www.openstreetmap.org/node/664910895`
(T1), `/node/664910802` (T2), `/node/664910876` (T3), `/node/664910849` (T4);
OSM way `https://www.openstreetmap.org/way/52218708`; Perkins and Maier 2009,
`https://arxiv.org/abs/0912.3841` (text: "the new layout distances range from
81 m to 127 m"; the five spacings are labels on Figure 1, an aerial photograph
of the new layout, and are quoted from there in each check's `locator`).

Source conflicts and judgement calls:

* **The published "81 m to 127 m" is not the full range of the array.** Figure 1
  of Perkins and Maier labels the four sides of the new quadrilateral and the
  T2-T3 diagonal, and omits the other diagonal, T1-T4. OSM puts T1-T4 at
  171.7 m. The official layout diagram in Hanna and Mukherjee 2025
  (`https://arxiv.org/abs/2507.09813`, Figure 4, axes in metres, y north) shows
  T1 (new) at roughly x = 136 m and T4 at x = -35 m, i.e. about 170 m apart by
  eye, agreeing with OSM; the same figure places the old T1 about 35 m from T4,
  agreeing with Perkins' 35 m. A figure read by eye is not cited as a source or
  used in a check.
* **OSM T1-T2 is 105.3 m against the 99 m label (+6.4 %).** Within the 10-15 m
  tracing accuracy of a point on a 12 m dish for a 100 m baseline, but it is
  the reason the distance checks carry a 7 % tolerance rather than 3 %. The
  perimeter check (sum of four sides) is at 0.27 %, because the over- and
  under-estimates cancel.
* The published array coordinate on the existing map centre
  (31d40'30.21"N, 110d57'7.77"W) lies 24 m from the centroid of the OSM
  quadrilateral. Not a check.

Site coordinate corrections: none required (`site:mount-hopkins-veritas`,
precision_m 100, is consistent with the OSM positions to 24 m).

Not drawn and why (backlog):

1. Absolute telescope coordinates: no fetched text gives them. The VERITAS
   Eventdisplay software (GitHub `VERITAS-Observatory/Eventdisplay_v4`,
   Zenodo 18592127) is the likely place to find a telescope-position table and
   could replace the OSM points with a `surveyed` layout.
2. The T1-T4 diagonal as a published figure.
3. Basecamp buildings (administrative complex, control room): not identified
   in OSM.
4. The Whipple 10 m telescope on the Mount Hopkins summit, not part of this
   facility's inventory and out of the basecamp map's extent.

---

## 3. HAWC at Sierra Negra (`map:sierra-negra`)

Grade before: **partial** (1 feature: one reference point at a coordinate good
to 0.01 degree). Grade after: **layout to scale** (3 features: the 300 water
tanks, the tank-field outline, the observatory polygon). The map centre moves
from the paper's rounded coordinate to the centroid of the tank field.

| Entity / feature | Drawn? | Representation | accuracy_m | Check (expected vs measured) |
| --- | --- | --- | ---: | --- |
| `geometry:hawc-tanks` (detector:hawc; MultiPolygon of 300 footprints) | drawn | georeferenced (OSM ways 541455344 to 541455690, 300 ways, one editing session) | 5 | summed area, expected 12,556 m2 (= 300 x pi x (7.3 m/2)^2, derived from the paper's 300 tanks of 7.3 m): measured 13,142.9 m2, +4.7 %, pass at 6 % |
| `geometry:hawc-tank-field-hull` (site:hawc-sierra-negra) | drawn | derived (convex hull of all tank vertices, 33 vertices) | 10 | area vs "22,000 m2": 22,415.9 m2 (+1.9 %), pass at 5 %; area vs the levelled platform "about 22,395 m2": +0.09 %, pass at 3 % |
| `geometry:hawc-observatory-polygon` | drawn | georeferenced (OSM way 1563711916) | 15 | none (32,534 m2, bigger than the 22,395 m2 platform, so not compared) |
| outrigger array (345 tanks) | not drawn | | | no position source, none in OSM |
| HAWC Utility Building, counting house | not drawn | | | unnamed OSM polygons, none identified |
| `map.unlocated[]` | empty | | | the contract's `unlocated` rows name atlas entities; the outriggers are not an entity, so they are in the map notes and here |

Principal sources: OSM extract of the 300 ways
(`https://api.openstreetmap.org/api/0.6/map?bbox=-97.325,18.980,-97.295,19.005`,
way ids as above, e.g. `https://www.openstreetmap.org/way/541455344`); OSM way
`https://www.openstreetmap.org/way/1563711916`; HAWC ICRC 2013 contributions
`https://arxiv.org/abs/1310.0074` ("HAWC is composed of 300 water Cherenkov
detectors built over an area of 22,000 m2"; "Each tank is a cylinder of 7.3m
in diameter and 5m in height"; "an area of about 22,395 m2, corresponding to
the HAWC platform"); outriggers `https://arxiv.org/abs/1908.06650`.

Why this is believed: exactly 300 tank ways exist, tagged `height=5` and
`content=water` (the paper's 5 m tank height); the field outline's area matches
the paper's array and platform areas to 2 % and 0.1 %. Each tank polygon
encloses 43.8 m2 against 41.9 m2 for a 7.3 m circle (equivalent-circle diameter
7.47 m, longest chord 7.65 m): the mappers drew the tanks about 2 % wide, which
is the whole of the +4.7 % area-check residual; `accuracy_m` 5 for the position
is unaffected.

Source conflicts and judgement calls:

* The paper quotes three areas for the array: 22,000 m2 (array), "about
  22,500 m2" and "about 22,395 m2" (platform). The hull is 22,416 m2; two of the
  three are asserted as checks.
* The map centre was the rounded coordinate (18.99 N, 97.31 W); the tank field
  centroid is 587 m from it, inside the rounding box (+-0.005 degree is about
  550 m north-south and 520 m east-west), so the two do not conflict.

Site coordinate corrections (integrator to apply or not; the proposal rests on
an OSM trace, rank 11, corroborated by the paper's rounded coordinate):

```json
{"site_id": "site:hawc-sierra-negra",
 "current": {"lat": 18.99, "lon": -97.31, "precision_m": 600},
 "proposed": {"lat": 18.99480, "lon": -97.30767, "precision_m": 30},
 "source": "src:geo-arrays2-hawc-osm-tank-field",
 "locator": "centroid of the convex hull of the 300 OSM tank footprints (geometry:hawc-tank-field-hull)",
 "quote": "HAWC is composed of 300 water Cherenkov detectors built over an area of 22,000 m2 (hull area 22,416 m2); paper site coordinate 18.99 N, 97.31 W lies 587 m from the proposal, inside its rounding"}
```

Not drawn and why (backlog):

1. The 345 outrigger tanks (1.55 m diameter, "concentric circular symmetric" around
   the main array, 12 to 18 m apart, in sections A to E; arXiv:1908.06650):
   backlog is a HAWC outrigger layout table or GIS file; neither the text nor OSM
   gives positions.
2. HUB and counting house: none of the four unnamed OSM buildings near the
   array can be identified from the paper ("installed East to the tank array
   platform"). Backlog: a HAWC site plan.
3. The LMT on Sierra Negra (about 1.3 km south-west of the array) is a separate
   facility, not in this atlas facility's inventory, and is not drawn.

## Pipeline issue found while checking HAWC (for the integrator; `hepgraph/` not touched)

`hepgraph/atlas/geo.py::_ring_centroid` accumulates the shoelace sums in raw
longitude/latitude, without translating to a local origin. For a polygon a few
metres across at large coordinates this loses the significant digits: the
centroids of the 300 HAWC tank polygons (lon -97) are off by a median of 107 m
and a maximum of 532 m from the true centroid, while the H.E.S.S. footprints
(lon 16.5) are off by 0.1 to 1.0 m. It affects `distance` checks between small
polygons, `geometry-site-mismatch`, and the `measured.centroid` in the bundle,
not `area`, `length` or `span`. This stream therefore uses `distance` checks only
between H.E.S.S. footprints (error under 1 m on 120 m) and between VERITAS
points (exact), and measures the 300 tanks with an `area` check; the
MultiPolygon centroid happens to be off by only 3 m. Fix: subtract the first
vertex before accumulating.

---

## 4. Roque de los Muchachos: MAGIC, LST-1 to LST-4, CTAO-North (`map:roque-de-los-muchachos-observatory`)

Grade before: **partial** (2 features: two points on the same 500 m campus
coordinate). Grade after: **layout to scale** (8 features: MAGIC-I, MAGIC-II,
MAGIC counting house, LST-1, three newer LSTs, outline of the built
telescopes). The map centre moves from a 500 m geocode to CTAO-North's
published array coordinate.

| Entity / feature | Drawn? | Representation | accuracy_m | Check (expected vs measured) |
| --- | --- | --- | ---: | --- |
| `geometry:roque-magic-i` (experiment:magic) | drawn | georeferenced (OSM way 288251657) | 10 | none of its own; MAGIC-II's check measures against it |
| `geometry:roque-magic-ii` (experiment:magic) | drawn | georeferenced (OSM way 288251656) | 10 | distance to MAGIC-I, expected 85 m: measured 86.2 m (+1.4 %), pass at 4 % |
| `geometry:roque-magic-counting-house` | drawn | georeferenced (OSM way 288988538) | 8 | none |
| `geometry:roque-lst-1` (experiment:ctao) | drawn | georeferenced (OSM way 685521693) | 10 | distance to MAGIC-II (nearer MAGIC telescope), expected "~100 m": measured 96.0 m (-4.0 %), pass at 10 % |
| `geometry:roque-lst-new-a/b/c` (experiment:ctao; the three newer LSTs) | drawn | georeferenced (OSM ways 1263216283/84/85) | 10 | none: no published position or spacing |
| `geometry:roque-gamma-ray-telescope-cluster` (site:roque-de-los-muchachos-gamma-ray-array) | drawn | derived (convex hull of the six footprints) | 15 | none (hull is 32,500 m2, 284 m across; the published 0.5 km2 is the planned 13-telescope array, a different object) |
| CTAO-North's nine planned MSTs | not drawn | | | layout published only as an unscaled figure (linked under `schematics`) |
| `map.unlocated[]` | empty | | | everything in the facility's inventory is drawn; the MSTs are not an atlas entity |

Principal sources: OSM ways (`https://www.openstreetmap.org/way/288251657`
MAGIC I, `/way/288251656` MAGIC II, `/way/685521693` LST-1,
`/way/1263216283`, `/way/1263216284`, `/way/1263216285` newer LSTs,
`/way/288988538` counting house); Performance of the joint LST-1 and MAGIC
observations, `https://arxiv.org/abs/2310.01954` ("MAGIC is a system of two
IACTs, separated by a distance of 85 m"; LST-1 "is placed at a distance of only
~100 m from the MAGIC telescopes"); CTAO-North page
`https://www.ctao.org/emission-to-discovery/array-sites/ctao-north/` (array
coordinate "Latitude: 28º 45′ 43.7904″ North Longitude: 17º 53′ 31.218″ West";
"13 telescopes distributed over an area of about 0.5 km2: four Large-Sized
Telescopes ... and nine Medium-Sized Telescopes"); CTAO news of 2026-10-15
`https://www.ctao.org/news/the-large-sized-telescope-sub-array-is-inaugurated-on-ctao-north/`;
CTAO layout release `https://www.ctao.org/news/ctao-releases-layouts-for-alpha-configuration/`.

Status and time: all CTAO features inherit `experiment:ctao` (status
`construction`), so LST-1 (completed on site October 2018, "foreseen to become
the CTAO's first telescope once it has completed its commissioning") is drawn
amber like the three newer LSTs. CTAO announced on 2026-10-15 the inauguration
of the LST sub-array and "the completion of the four telescopes"; "over the
coming years, the LSTs will undergo commissioning and integration into CTAO
operations". The OSM tag "In Construction (3-24)" on the three newer LSTs is a
2024 note and out of date; it is not used. No `valid` window is set (the build
turns a `valid` start into a clip of the entity's own lifecycle, which would
not improve on the entity's status).

Source conflicts and judgement calls:

* **"~100 m from the MAGIC telescopes" versus two MAGIC telescopes.** OSM
  puts LST-1 at 96 m from MAGIC-II but 148 m from MAGIC-I. The paper's phrase
  is loose; the check is asserted against the nearer telescope at a 10 %
  tolerance and the MAGIC-I distance is not claimed.
* **The commonly cited MAGIC coordinate** (28d45'43"N 17d53'24"W, flagged as
  unverified in the earlier worklog) is within 7 m of the OSM MAGIC-I centroid
  (28.761958, -17.890065), but no primary source for it was fetched, so it is
  still not cited. CTAO-North's published array coordinate is a different
  point, 170 to 190 m west of the MAGIC telescopes (it is a reference point of
  the planned array, and the built telescopes lie 70 to 190 m from it).
* The three newer LSTs cannot be numbered LST-2, LST-3, LST-4 (OSM does not,
  and the CTAO figures are unscaled).
* OSM also maps FACT, the SuperWASP, GTC, WHT and other optical telescopes,
  which are not in this facility's inventory.

Site coordinate corrections (an official, precise source; integrator to apply):

```json
{"site_id": "site:roque-de-los-muchachos-gamma-ray-array",
 "current": {"lat": 28.757069, "lon": -17.8888436, "precision_m": 500, "kind": "campus"},
 "proposed": {"lat": 28.762164, "lon": -17.892005, "precision_m": 250, "kind": "detector"},
 "source": "src:geo-arrays2-ctao-north-array-page",
 "locator": "CTAO-North array page, 'Array Coordinates'",
 "quote": "Latitude: 28º 45′ 43.7904″ North Longitude: 17º 53′ 31.218″ West"}
```

`precision_m` 250 because the published coordinate is the array reference
point and MAGIC-I stands 190 m from it; the current point is a geocode of the
whole observatory, 600 m south-east of the telescopes.

Not drawn and why (backlog):

1. CTAO-North MSTs (nine planned): the as-requested layout coordinates (shift
   under 10 m) behind the CTAO figure; ask CTAO or find the construction-permit
   documents.
2. Numbering of the three newer LSTs and a published LST spacing, to add
   checks.
3. LST camera access towers (OSM service buildings), not drawn.

---

## 5. CTAO-South, Paranal (`map:ctao-south-paranal`)

Grade before: **partial** (1 feature). Grade after: **partial, unchanged**
(1 feature plus an official layout schematic link). This is the one facility in
the stream where the evidence did not allow an upgrade.

| Entity / feature | Drawn? | Representation | accuracy_m | Check |
| --- | --- | --- | ---: | --- |
| `geometry:ctao-south-array-point` (site:paranal-cta-south) | drawn (unchanged) | surveyed (published array coordinate) | 100 | none |
| 14 MSTs, 37 SSTs, 4 LST and 3 SST foundations | not drawn | | | no published coordinates |
| OSM way 939135727 (site outline) | considered, not drawn | | | 2.04 km2 vs the published ~3 km2 |

What was looked for and found:

* The CTAO site and news pages (fetched 2026-10-25) say the Alpha Configuration
  "defines the geographical positions of the elements in the array", and the
  release news says "the released layout coordinates correspond to the so-called
  'as-requested coordinates' ... any shift in the final positions would be
  limited to less than ten metres". The layout is published as two figures
  (`https://www.ctao.org/wp-content/uploads/CTAO_South_Alpha_Final2_2024.png` and the
  North equivalent). Both are schematic: no scale bar, no coordinate axes. They
  are linked on the map under `schematics` and are not traced.
* A web search pointed at the simulation layouts of the prod5
  instrument-response release (Zenodo record 5499840) as the only other place
  with positions; the Zenodo API answered 403 to this session and the files
  were not read. They are simulation layouts, not the as-requested layout, so
  they would not have been used for a `surveyed` pad.
* OpenStreetMap has no telescope, pad, foundation or road of the array at
  CTAO-South other than one polygon (way 939135727, "Cherenkov Telescope Array -
  Southern Hemisphere Site", `landuse=construction`, version 2 of 2025-02-25):
  a 20-node near-ellipse, 1.63 km across and 2.04 km2 in area. The official page
  says the array is "spread over three square kilometers" (the layout release
  says "51 telescopes over a ~3 km 2 area"); the polygon is 32 % smaller than that, so it cannot be the
  array footprint, and a site boundary must contain the array. Its centroid is
  374 m from the published array coordinate. It is not drawn because a plausible
  but wrong outline is worse than none.

Planned features and time: none are drawn, so there is nothing to date. Had
telescope pads been available they would inherit `experiment:ctao`'s
`construction` status; a pad with no built telescope would need a `valid`
window, which the current build turns into a clip of the entity's lifecycle (see
the RHIC note in `REVIEW_geometry_qa.md`).

Site coordinate corrections: none. `site:paranal-cta-south` already carries the
published coordinate (24d41'0.34"S, 70d18'58.84"W).

Backlog: the Alpha-configuration coordinate file (CTAO as-requested layout or
the construction-phase surveyed pad coordinates) from CTAO; until then the map
stays at one reference point. With it, 51 telescope pads and 7 foundations would
be `surveyed` points with an area check against the published ~3 km2.

---

## 6. Summary, site coordinate corrections, validator and build

| Facility | Grade before | Grade after | Features drawn | Checks (all pass) |
| --- | --- | --- | ---: | --- |
| H.E.S.S. | partial | layout to scale | 9 | 4 neighbour distances (120 m), 4 centre-to-corner distances (84.85 m), perimeter 480 m |
| CTAO-South | partial | partial (unchanged) | 1 | none |
| Roque de los Muchachos | partial | layout to scale | 8 | MAGIC separation 85 m, LST-1 to MAGIC ~100 m |
| Sierra Negra (HAWC) | partial | layout to scale | 3 | tank area, array area (22,000 m2) and platform area (22,395 m2) |
| Whipple (VERITAS) | partial | layout to scale | 6 | five published spacings (7 %), perimeter 409 m |

Site coordinate corrections, collected (details in each section):

1. `site:roque-de-los-muchachos-gamma-ray-array`: (28.757069, -17.8888436,
   precision 500, campus) to (28.762164, -17.892005, precision 250, detector);
   source `src:geo-arrays2-ctao-north-array-page`, quote "Latitude: 28º 45′
   43.7904″ North Longitude: 17º 53′ 31.218″ West". Official source.
2. `site:hawc-sierra-negra`: (18.99, -97.31, precision 600) to (18.99480,
   -97.30767, precision 30); source `src:geo-arrays2-hawc-osm-tank-field`
   (OSM, rank 11; corroborated by the paper's rounded coordinate and the 22,400 m2
   hull). The integrator may prefer to keep the paper coordinate.
3. Optional: `site:khomas-highland-hess` precision_m 200 to 50 (the source gives
   the coordinate to one arc-second).
4. None for `site:mount-hopkins-veritas` or `site:paranal-cta-south`.

Overpass: unavailable (HTTP 502, "at capacity") for the two H.E.S.S. queries; all
five extracts were read with the OSM API `map` call instead (see the method
note at the top). If an integrator wants `osm.timestamp` to be an Overpass
`timestamp_osm_base`, the five boxes can be re-queried when Overpass recovers;
the element ids and versions in every `locator` identify exactly what was used.

Validator, build and tests (run from this worktree, `main` venv):

* `python -m hepgraph.atlas.validate`: **3 errors, 1587 warnings** (1588 after the
  H.E.S.S. commit; the duplicate-shape warning on the two Roque points went with
  their replacement).
  The three errors are the pre-existing, time-driven `status-not-derived-state`
  findings for `collaboration:mu3e`, `detector:mu3e` and `experiment:mu3e`,
  which the integrator confirmed are not this stream's and are being fixed
  elsewhere; no mu3e file was touched. **No error or warning is reported on any
  file written or edited by this stream** (every `geometry/hess-*`,
  `veritas-*`, `hawc-*`, `roque-*`, `ctao-south-*` record, the five maps and the
  `geo-arrays2-*` sources). The warnings that mention these facilities are on
  records this stream did not edit (experiment/detector intervals for HAWC and
  VERITAS; the A23 campus-grade point warning on the Roque site record, which the
  correction above would clear).
* `python -m hepgraph.atlas.build`: succeeds. Largest bundle of this stream:
  `sierra-negra.json`, 392 KB (300 tank polygons), under the 2 MB cap. Generated
  files were restored and are not in any commit.
* Existing tests (not new ones): `tests/test_atlas_geometry_data.py`,
  `test_atlas_geo.py`, `test_atlas_build.py` (107 passed) and `pytest -k atlas`
  (352 passed, 1 skipped).
* Visual check on the built product (Chromium pane, local static server):
  `#/map/hess-khomas-highland`, `#/map/sierra-negra` and
  `#/map/roque-de-los-muchachos-observatory` render; the H.E.S.S. square shows
  its north-south diagonal with CT5 in the middle, the HAWC tank field spans
  about two scale-bar lengths (190 m), and the Roque telescopes sit on the
  ridge beside the road. VERITAS and CTAO-South were checked in the bundle
  only.

Pipeline issues for the integrator (nothing under `hepgraph/` was touched):

1. `geo.centroid` numerical error on small polygons at large coordinates
   (section 3 above).
2. `_feature_segments` turns any `valid` start into a clip of the entity's
   lifecycle; the planned CTAO pads that would have needed a future-dated
   `valid` could not be expressed. Not triggered here.
3. If the coverage grade counts structural feature types (as
   `GEOMETRY_COVERAGE_STATE.md` suggests), note that the telescope footprints here
   are `other` because no contract type fits a single telescope; each facility's
   structural feature is its `array` outline (`array` at H.E.S.S., VERITAS,
   HAWC and the Roque cluster outline). CTAO-South has none.
