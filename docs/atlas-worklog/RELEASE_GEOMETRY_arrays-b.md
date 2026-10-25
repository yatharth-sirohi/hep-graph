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
