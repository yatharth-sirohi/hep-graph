# Release geometry stream "accel2" (2026-10-25)

Worktree `/Users/yatharthsirohi/Desktop/HEP-Graph-ar-accel2`, branch `atlas-release-accel2`.
Scope: the accelerators still unlocated at labs whose maps otherwise exist, starting from the backlogs of
`RELEASE_GEOMETRY_accel.md` and `RELEASE_GEOMETRY_nine.md`: Oak Ridge (SNS), Argonne (APS, ATLAS), ISIS, PSI (Ring
Cyclotron, Injector 2) and KIT (KATRIN). New sources are prefixed `src:geo-<facility>-...`. INSPIRE was not touched.

## Method notes

* OSM data was read from the OSM API 0.6 (`api.openstreetmap.org/api/0.6/map.json?bbox=...`, one tile at a time,
  at least 6 s apart; `/way/<id>/full.json`), as in the previous streams; Overpass was not used. Each `osm.timestamp`
  is the HTTP `Date` of the API response; element versions and edit times are in the source excerpts.
* The pre-existing validator errors are the three `status-not-derived-state` findings on the mu3e records (not touched).

---

## 1. Oak Ridge / SNS (`map:oak-ridge-national-laboratory`)

Grade before: marker only (complex boundary; accelerator:sns unlocated).
Grade after: **layout to scale, approximate** (the linac structure and the Instrument Hall (building 8700), plus 23
further footprints). The ring, HEBT and RTBT are still unlocated.

### What made it possible: ORNL's own interactive map

`https://map.ornl.gov/` is a CampusTours "AnyTour" application whose data files are public XML
(`https://map.ornl.gov/xml/CL_ornl.xml` combined data, `.../AL_ornl.xml` associations). One of its image maps, "Chestnut
Ridge" (`UMAP_2015071721664`, 7000 x 4000 px), carries seven labelled polygons: `8600 ... Central Laboratory and Office
Complex (CLO)`, `8610 CNMS`, `8630 Shull Wollan Center (JINS)`, `8640 Guest House`, `8700 Instrument Hall`, `Second
Target Station` and **`SNS LINEAR Accelerator and Klystron Gallery`** (a long, thin 49-vertex polygon). The polygons are in
the map's own image units, with no latitude/longitude; their building text says "Instrument Hall contains the SNS
back-end system including the heavy-metal target, a vessel of liquid mercury, and 20 active beam lines". This is the
lab's own labelling, which is what the earlier backlog ("an ORNL site map with a text legend") asked for. The polygons were
**not copied**; they were used only to identify OpenStreetMap footprints.

### The identification, with its numbers

The OSM extract of the complex (25 buildings; bbox -84.320,35.940,-84.285,35.965, read 2026-10-25T11:43:00Z) has one
building named by OSM mappers, `ORNL Guest House` with `addr:housenumber=8640` (way 892578468), and 24 unnamed ones.
A similarity transform (rotation, uniform scale, translation and one mirror) from the map's image units to metres was
fitted by least squares to four pairs: Guest House (named, number 8640 matches the ORNL label), and, by size and
position, CLO to way 892578439, 8700 to way 443660319 and JINS to way 892578446.

| Quantity | Value |
| --- | --- |
| Fitted scale, rotation | 673 m per image unit, 18 deg |
| Residual of the four anchors | 9, 13, 11, 11 m (centroid offsets) |
| Leave-one-out prediction of an omitted anchor | 8700: 30 m; CLO: 19 m; JINS: 15 m |
| ORNL linac polygon transformed, centroid vs OSM way 892578460 | 37 m (leave-one-out 37-66 m) |
| Long-axis direction, ORNL polygon vs OSM way | 20 deg vs 28 deg |
| Length along the long axis | 403 m (hand-drawn ORNL polygon) vs 369.8 m (OSM) |
| Other long thin buildings in the complex | none: way 892578439 spans 269 m but is 8042 m^2 (30 m wide on average) and lies about 550 m from the transformed linac polygon |

The identification is therefore consistent, not proven; the OSM way carries no name, and no source says "this OSM building
is the linac". Both records say so and are graded `approximate`.

Plausibility of the linac footprint against sourced numbers (not written as `checks[]`, because they are not like for
like): "The length of the linac tunnel is 1056 feet" (321.9 m) and "The tunnel dimensions are 14' wide by 10' high"; klystron
building "a building width of 30 feet" (PAC 2001, RPPH066, sections 2 and 2.1); "~330-m-long klystron gallery"
(PAC 2003, MOAL003); a front-end building of "11000 square feet". The OSM footprint is 369.8 m long (the tunnel plus the
front-end building) and 14.3 m wide on average (30 ft + 14 ft = 13.4 m plus walls).

### Inventory

| Entity | Status | Representation | accuracy_m | Check |
| --- | --- | --- | --- | --- |
| accelerator:sns | drawn: geometry:sns-linac-structure (OSM way 892578460; `linac`; the surface structure: front-end building, klystron gallery and tunnel, not the beam axis) | georeferenced, approximate | 10 | none (see plausibility above) |
| (context) building 8700 Instrument Hall | geometry:sns-instrument-hall-8700 (OSM way 443660319; contains the target per ORNL's text) | georeferenced, approximate | 10 | none (no published dimension) |
| (context) building 8640 Guest House | geometry:sns-guest-house-8640 (OSM way 892578468, named) | georeferenced | 8 | none |
| (context) 22 further buildings | geometry:sns-area-buildings (MultiPolygon, unlabelled) | georeferenced | 10 | none |
| site:ornl-sns-neutrino-alley | complex boundary (unchanged) | | | |
| accumulator ring (248.0 m), HEBT (169 m), RTBT (151 m) | **unlocated** (map row on facility:oak-ridge-national-laboratory) | - | - | - |
| target position and Neutrino Alley | **unlocated** | - | - | - |

### Dead ends (do not repeat)

* Roane County / Anderson County footprint layers: a web search found no building layer for either county; the Tennessee
  state STRUCTURES folder is empty (previous pass). The ORNL map above replaced that route.
* DOE NEPA documents (EIS-0247 supplement analyses SA-02 and SA-03, 2021 and 2025) describe the Second Target Station
  site and give no building numbers, coordinates or existing-structure dimensions.
* `www.ornl.gov` PDF maps (`visitor_map.pdf`) return 403; they are images and would not have been traced anyway.
* The only ring layout figure found (PAC 2003 TPPE011, Fig. 1) is a labelled schematic with no scale, coordinates or north;
  PAC 2003 MOAL003 Fig. 1 is an artist's impression overlaid on a photograph. Neither is a position source.

### Source conflicts

* Linac length: 1056 ft tunnel (321.9 m, PAC 2001) vs "~330-m-long klystron gallery" (PAC 2003) vs "1,000-foot linac" (ORNL
  news, 305 m) vs 369.8 m OSM footprint (which includes the front-end building). The stage lengths and the building are
  different things, so no check was written.

### Site coordinate corrections

None.

### Warnings left on these files

None attributable to the SNS records.

### Backlog

* A scaled SNS layout (site plan, civil drawing set, or a survey paper with ring-centre and linac-axis coordinates), to
  georeference the ring, HEBT and RTBT against the linac structure and the 8700 hall drawn here, then add length checks
  (248.0 m, 169 m, 151 m; PAC 2003 ROPA001).
* An official dimension for the linac structure or for building 8700 to turn the plausibility argument into a check.
* The target position inside 8700 and the Neutrino Alley bearing (COHERENT plan view).

---

## 2. Argonne / APS (`map:argonne-national-laboratory`)

Grade before: partial (footprints only). Grade after: **layout to scale** (a derived storage-ring orbit plus footprints).
ATLAS inside Building 203 is still unlocated.

### The APS orbit: what a circle can honestly claim

The earlier pass left the 1104 m orbit unlocated because "no source gives a radius and centre". The data over-determine it:

* **Radius, sourced**: the APS operations page `https://ops.aps.anl.gov/SRparameters/SRparameters.html` (M. Borland, 2024-08-27)
  gives "Circumference C 1103.609 m" and "There are 40 sectors in the ring". R = C / 2 pi = 175.645 m. The ring is 40 identical
  9-degree sectors, so a circle of the same circumference departs from the orbit by less than one sector's sagitta, 0.54 m.
* **Centre, fitted to the OSM hall**: the outer way of relation 3126234 (258 vertices) is a circle of R = 196.82 m with a 0.44 m
  standard deviation; the inner way (80 vertices) has notches (mazes, ratchets), but its 47 vertices on the circle (trimmed least
  squares) give R = 169.97 m and a centre 0.6 m from the outer one. Centre used: 41.7035178 N, 87.9881277 W.
* **Relation, sourced**: the 1987 Conceptual Design Report (ANL-87-15, OSTI-hosted scan at the University of North Texas Digital
  Library, `https://digital.library.unt.edu/ark:/67531/metadc282823/`): "The single-story experiment hall is an annular
  structure housing both the storage ring enclosure and the experiment floor" (p. IV.3-25), "The storage ring enclosure is
  located inside the inner perimeter wall of the experiment hall. ... The enclosure is basically circular in plan" (p. IV.3-16),
  "The inside wall of the concrete tunnel is parallel to the storage ring" (section 2.3.5.3), the hall "91 ft wide by 3472 ft
  (1060 m) in circumference at the storage ring centerline", and the machine-support buildings "in the infield".
* **Cross-checks not used in the construction**: the OSM annulus is 26.8 m wide against 91 ft = 27.7 m (-3.4%); the OSM APS linac
  building (411) and injection wing (412) lie 75-137 m and 44-81 m from the centre, inside the 170 m inner wall (infield).
* Drawn offset: 5.6 m outside the radius of the inner wall. The report's own cross-section (enclosure interior 11.6-18.9 ft wide,
  0.8 m walls, about 1.7 m of utility corridor) would put the beam 4-6 m outside the inner wall, so the drawn offset is plausible
  but not independently pinned; `accuracy_m` 10 and `derived`.

### Inventory (new or changed)

| Entity | Status | Representation | accuracy_m | Check |
| --- | --- | --- | --- | --- |
| APS storage ring (no accelerator record; attached to site:argonne-campus) | drawn: geometry:argonne-aps-storage-ring-orbit (ring, circle, 360 vertices) | derived | 10 | length 1103.595 m vs "Circumference C 1103.609 m", tol 0.2%: pass (tautological by construction, said so in the record) |
| ATLAS layout (injectors, booster, linac, target areas) | **unlocated**, reason extended | - | - | - |

### Conflicts and caveats

* The orbit is attached to `site:argonne-campus` because the atlas has no APS accelerator record (the contract needs an
  `entity_id` for a ring). The campus site has no state segments, so the ring is drawn in every year (as the campus boundary
  already is). The integrator may re-point it when `accelerator:aps` exists.
* Circumference: 1103.609 m (2024 lattice page) vs "1104 m" (OSTI parameter list) vs 1060 m (1987 design). No conflict at
  the as-built level; the design value is not used for position.
* `aps.anl.gov`, `anl.gov`, `www.phy.anl.gov` and the sandbox mirror return HTTP 403 to every fetch (re-tried): the ATLAS floor plan
  PDF (`.../ATLAS_floor_plan_Mar2022.pdf`) and `.../atlas-facility-layout-with-beam-locations` could not be read.

### Warnings left

None on the new or changed files.

### Backlog

* ATLAS: any reachable copy of the ATLAS floor plan or a Building 203 survey drawing with an identifiable building outline;
  then georeference against three OSM corners of Building 203 (cite, never copy) and place the linac axis.
* APS: an accelerator record for the APS (so the ring has its own `entity_id` and start date), and an APS survey table with
  the ring-centre coordinates to replace the fitted centre.
