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

## Summary

| Facility | Grade before | Grade after | What was added (representation, check) |
| --- | --- | --- | --- |
| Oak Ridge / SNS (map:oak-ridge-national-laboratory) | marker only | layout to scale (approximate) | linac structure 370 m (OSM way 892578460, georeferenced, approximate), Instrument Hall building 8700 (way 443660319, approximate), Guest House and 22 buildings; identified through ORNL's own interactive map; no checks; ring, HEBT, RTBT, target and Neutrino Alley unlocated |
| Argonne / APS (map:argonne-national-laboratory) | partial | layout to scale | APS storage ring orbit as a derived circle, R = 175.645 m from the published 1103.609 m circumference, concentric with the circular outlines of the experiment hall (accuracy 10 m); length check 1103.595 vs 1103.609 m (tautological, stated); ATLAS still unlocated |
| ISIS (map:isis-neutron-source) | partial | partial | nothing placeable; reasons, leads (R6, R5.3) and backlog rewritten |
| PSI (map:psi) | layout to scale | layout to scale | nothing placeable; Ring Cyclotron still unlocated; second-pass notes and backlog |
| KIT / KATRIN (map:kit-karlsruhe) | partial | layout to scale (derived, accuracy 20 m) | beam axis WGTS-to-detector coil centres 52.64 m at 16 deg and the main spectrometer vessel footprint 23.23 m x 9.8 m, from the Collaboration's orientation and Table 1 coil positions, positioned in the OSM hall outline by constraints; checks tautological (stated) |

### End state of this branch

* `python -m hepgraph.atlas.validate`: 3 errors, all the pre-existing `status-not-derived-state` findings on the mu3e records (not touched); no warning on any file of this stream.
* `python -m hepgraph.atlas.build` succeeds; generated bundles were restored before each commit and are not committed. `tests/test_atlas_geometry_data.py` passes; the full suite passes (682 passed, 139 skipped).
* The derived shapes were drawn to a scratch image and compared with the OSM outlines they depend on (KATRIN: vessel and detector end inside the outline, WGTS end inside TLK 452; APS: the orbit inside the hall annulus, 5.6 m outside the inner wall, with the infield buildings inside it).
  The maps were not opened in the browser pane (it was hidden during the session), so scale bars and tooltips were not checked.

### Method lessons

1. **A lab's own interactive map may be a data source.** ORNL's `map.ornl.gov` is a CampusTours app whose XML data files (`/xml/CL_ornl.xml`, `/xml/AL_ornl.xml`, found from the page's `any.xml`) hold labelled building polygons in image units. They carry no coordinates, but a similarity fit onto four identifiable OSM buildings (residuals 9-13 m, leave-one-out 15-30 m) identified the SNS linac and Instrument Hall footprints.
2. **Collaboration papers hide survey-grade layout tables.** The KATRIN air-coil paper's Table 1 lists the axial position of every coil system relative to the main spectrometer centre; a physics paper's Figure caption gave the azimuth. Search the field-modelling and systematics papers, not the instrument overview.
3. **Fit a circle to the outline before deciding what the outline is.** The APS hall's outer way is a 258-vertex circle (standard deviation 0.44 m); with the design report's "annular, concentric" statements and the published circumference, the orbit follows without a surveyed centre.
4. **When two hypotheses both fit by size, say so and stop.** At ISIS and PSI several buildings could hold the machine; no source chose between them, so none was drawn.

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

---

## 3. KIT / KATRIN (`map:kit-karlsruhe`)

Grade before: partial (footprints only, KATRIN outline typed `experimental_area`, beamline unlocated).
Grade after: **layout to scale (derived, accuracy 20 m)**: a beam axis and the main spectrometer vessel at published size,
direction and spacing, positioned inside the OSM hall outline by stated constraints.

### Sourced inputs (all fetched this session)

| Input | Value | Source |
| --- | --- | --- |
| Orientation of the experiment | "The experiment has an orientation of xi ~ 16 deg east to the local north N." | KATRIN Collaboration, arXiv:2207.06326, Fig. 2 caption (p. 4) |
| Position of each coil system along the axis, z = 0 at the centre of the main spectrometer | WGTS -38.87 m, DPS -27.25, CPS -20.58, PS1 -16.46, PS2 -12.10, PCH +12.18, DET +13.78 | Glueck et al., arXiv:1304.6569, Table 1 |
| Same direction from another angle | "aligned almost to south-north direction, with an angle of 14 deg relative to the horizontal earth field" (the horizontal field is itself a little east of true north, so consistent) | same paper, p. 5 |
| Main spectrometer vessel | 23.23 m long, 9.8 m inner diameter | arXiv:2103.04755 (already on file) |
| Where things stand | "Rear system and WGTS will be installed in the existing TLK building"; "The Tritium Laboratory (building 452)"; spectrometers "in new buildings at the 'green field' site north of TLK"; "~ 70 m long linear configuration"; monitor beam line in a different building | KATRIN Design Report 2004 (FZKA 7090), pp. 48, 88, 89, 53 (`katrin.kit.edu/publikationen/DesignReport2004-12Jan2005.pdf`) |

### What the OSM outline adds, and what it cannot

The earlier pass could not draw a line because it had no axis and no end points. Now the direction and the spacing are published.
What is still not published is **where z = 0 stands on the ground**. In the 16-degree frame the OSM KATRIN outline (way 394890935) is a stepped
53 m x 19 m polygon (a 35 m x 19 m wide part and an 18 m x 11 m narrow wing); the 99 x 94 m TLK 452 (way 99082477) lies to its south-west.
Three facts bound z = 0: the vessel lies in the outline, the detector coil lies in the outline, the WGTS stands in building 452. A 0.25 m grid search
gives 1806 feasible placements spanning 27 m along the axis and 9 m across it (centre drawn; largest distance from the centre to a feasible placement 19.7 m, so `accuracy_m` 20). Stricter, less
certain assumptions shrink the set (pre-spectrometer coils also in the outline: largest distance from the drawn centre 15 m; DPS and CPS also in the outline: 9 m), and the drawn centre is a feasible placement in all three sets. The
orientation is independent of the outline: the outline's long sides run at 15.8-16.1 deg, the Collaboration says 16 deg.

### Inventory

| Entity | Status | Representation | accuracy_m | Check |
| --- | --- | --- | --- | --- |
| detector:katrin (beam axis, WGTS coil centre to detector coil centre, 52.64 m) | drawn: geometry:kit-katrin-beamline-axis (`beamline`, derived) | derived | 20 | azimuth 16.0 deg vs 16 deg (tol 1 deg): pass, **tautological**; length 52.644 m vs 52.65 m (my difference of two Table 1 values), tol 0.5%: pass, **tautological** |
| detector:katrin (main spectrometer vessel footprint, 23.23 m x 9.8 m) | drawn: geometry:kit-katrin-main-spectrometer (`other`, derived) | derived | 20 | perimeter 66.051 m vs 66.06 m (2 x (23.23 + 9.8)), tol 0.5%: pass, **tautological** |
| detector:katrin (outline, TLK 451/452, campus boundary) | unchanged | georeferenced | | |
| rest of the beamline (rear section, detector end, DPS/CPS elements, pre-spectrometer, monitor beam line) | **unlocated**, row rewritten | | | |

The checks are labelled tautological because the shapes are built from the same numbers; the independent evidence is the 15.8-16.1 deg of the OSM outline,
the containment tests (vessel and detector in the outline, WGTS in TLK 452: all pass for the drawn placement) and the constraint set above.

### Conflicts and caveats

* The "about 70 m" overall length is not reproduced: 52.64 m is the sourced span between the WGTS and detector coil centres; the rest (rear section, detector system) has no published position.
* The OSM outline is the mapper's polygon; the earlier pass typed it `experimental_area` and left it so. Nothing here asserts it is "the hall"; the derived shapes only require that it contain the vessel and the detector coil.
* The Design Report describes buildings as planned (2004), with a transport hall that "will become part of TLK"; the as-built layout may differ. The drawn centre is consistent with the transport system lying in the outline's narrow wing, but that is not used as an input.

### Site coordinate corrections

Unchanged from the previous stream's proposal (site:kit-campus-north, option B hall-grade point at the outline centroid 49.09574 N, 8.435976 E, within 10 m of the drawn z = 0 point 49.0957631 N, 8.4359846 E).

### Backlog

* A surveyed KATRIN coordinate (main spectrometer centre or WGTS in the KIT Campus North coordinate system) or a dimensioned hall plan: then re-anchor the two shapes and cut accuracy_m to a few metres.
* Positions of the rear section and the detector end (to reach the 70 m), the monitor-spectrometer hall.

---

## 4. ISIS (`map:isis-neutron-source`)

Grade before and after: **partial** (footprints only). The synchrotron, the linac and the extracted proton beamlines are still unlocated.
Nothing could be placed from a source. Records changed: the map's unlocated row (reason and backlog rewritten, two sources added); no geometry added.

### What was found

* STFC's campus map (`https://www.ukri.org/wp-content/uploads/2023/07/STFC-070723-RutherfordAppletonLaboratoryCampusMap.pdf`, v2.3, 2022, an image with no text
  layer; read by eye for labels, not traced) labels R5.1-R5.5, R5.3 (a building with a rounded north end), R6, R6A, R55 and R80 between and beside the two target
  stations. Its legend names only R22, R27, R75, R83, R84, R87, R92, R97, R100 and the conference rooms. So the map says where the buildings are, not what holds the ring.
* OSM carries the same numbers: R6 is way 200338539 ("industrial", 4 611 m^2), the R5.x block is inside way 200338759 (its fixme: "R55 is the experimental hall only.
  The smaller building is split into R5.1, R5.2, R5.3 and R5.4"), R55 is the building:part way 1454005510 and R80 is way 750266080. An extract of the RAL area (bbox
  -1.325..-1.305 x 51.565..51.577, 2026-10-25T19:45Z) has no circular outline.
* Sourced size: "a 52 m diameter proton synchrotron" (CERN Courier, 15 March 2000) agrees with the 163 m circumference of IPAC 2014; neither gives a centre.
* Dead ends: ISIS safety page (only R55 and R80), ISIS annual review 2018 (no building numbers for the machines), RAL-TR-2012-010 (an R55 tunnel statement, abstract only), a building.co.uk
  feature on the ISIS second target station (no layout), UKRI tender notices (R69, R132, R3 media centre; nothing on the machine halls), searches for "R6", "R5.3", "synchrotron hall" with ISIS.
* A 52 m ring would fit inside R6 (4 611 m^2) and inside the rounded part of R5.3 by size alone, so several buildings would "look right"; that is exactly why none was drawn.

### Inventory

| Entity | Status |
| --- | --- |
| ISIS synchrotron (163 m), linac (70 MeV), EPB lines | **unlocated**, rewritten reason with leads (R6, R5.3; unconfirmed) |
| TS1 (R55), TS2 (R80), RAL boundary | unchanged (context) |
| detector:karmen | unchanged (**unlocated**) |

### Backlog

* An ISIS/STFC document with a building register or site plan that names the synchrotron hall (and the linac and EPB tunnels) by R-number; then take the outline from OSM.

---

## 5. PSI (`map:psi`)

Grade before and after: **layout to scale** (hall WEHA verified plus buildings). The Ring Cyclotron is still unlocated; Injector 2 is represented only by its hall as context.
Records changed: the map's unlocated row (second-pass notes and backlog), one source added (PSI's Ring Cyclotron page). No geometry added.

### What was found

* PSI's Ring Cyclotron page (`https://www.psi.ch/en/cas/ring`) gives injection and extraction radii (2.1 m and 4.5 m) and says nothing about the building. The Injector 2 page,
  the HIPA info page, the Kiselev 2024 talk (a labelled 3-D picture "Experimental hall WEHA ... 590-MeV-Ring cyclotron ... SINQ ... UCN" without scale), the HB2012 (Seidel), Cyclotrons 2022
  and arXiv 1707.07970 / 1903.08935 papers carry no building statement.
* The full Arealplan 2015 legend (re-read from its text layer) lists WEHA Experimentierhalle, WIHA Injektorhalle 2, WHFA Hochfrequenzgebaeude, WYCA Niederenergieareal C, WNAA Nukleonenhalle, WMHA Montagehalle and others,
  and has no entry for the Ring Cyclotron or its vault.
* Decision on WIHA: PSI's legend calls it "Injektorhalle 2", the hall of Injector 2, and the earlier pass drew it as context. It was **not** attached to accelerator:psi-hipa
  because that record's main machine is the Ring Cyclotron: attaching the hall would let the map claim HIPA is drawn while its 590 MeV stage is not.

### Backlog

* A PSI layout drawing with building codes (or the "HIPA info" elog layout) that names the building of the Ring Cyclotron vault.

## Integrator verification (2026-10-25)

* APS circumference re-read on ops.aps.anl.gov/SRparameters: "Circumference C 1103.609 m".
* KATRIN orientation: arXiv:2207.06326 gives "ξ ≈ 16°" in the Fig. 2 caption but "ξ ≈ 17°" in the Sec. 2 text; 16° kept because the OSM hall outline runs at 15.8–16.1°. Recorded as a note on geometry:kit-katrin-beamline-axis.
