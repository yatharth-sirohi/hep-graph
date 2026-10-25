# Release geometry stream "nine" (2026-10-25)

Worktree `/Users/yatharthsirohi/Desktop/HEP-Graph-ar-nine`, branch `atlas-release-nine`.
Scope: the nine facilities that `GEOMETRY_COVERAGE_SET.md` put outside the local-map coverage
set. The release requires every facility to open a working to-scale map. Sources are prefixed
`src:geo-<facility>-…`. Grades before: "no map" for all nine.

## Method notes common to all nine

* **Overpass was unreachable from this machine all session** (both `overpass-api.de` and
  `lz4.overpass-api.de` timed out after 30 s with 0 bytes on `/api/status`; `overpass.kumi.systems`
  also timed out). Every OpenStreetMap shape was therefore read from the **OSM API 0.6**
  (`api.openstreetmap.org/api/0.6/map.json?bbox=…` and `…/<type>/<id>/full.json`), which serves the
  same element data. The `osm.timestamp` on each record is the HTTP `Date` of that API response
  (an extract time, in UTC); the element's own `version` and last-edit `timestamp` are in the
  source `excerpt` and in the geometry `locator`. Raw responses are in the session scratch
  directory, not in the repository.
* Wayback Machine returned HTTP 429 ("suspected abusive bot traffic") after a few requests; it
  was not used as a source in the end.
* INSPIRE was not touched.
* The three `status-not-derived-state` **errors** reported by `hepgraph.atlas.validate` on
  `mu3e` (collaboration, detector, experiment) are pre-existing and date-dependent (the validator
  derives state at the current month, 2026-10); none of them is on a file this stream touched. The integrator confirmed they are time-driven, present on the base branch and being fixed elsewhere; this stream's bar is "0 errors other than these three" and no mu3e file was touched.

---

## 1. argonne-national-laboratory (`map:argonne-national-laboratory`)

**Grade: no map → partial (footprints only).** There is no accelerator, beamline or detector
record at Argonne in the atlas, so no ring/linac feature can carry an `entity_id`; every shape other
than the campus boundary is a context building (`entity_id: null`).

| Entity / feature | Status | Representation | accuracy_m | Check |
| --- | --- | --- | --- | --- |
| `site:argonne-campus` → `geometry:argonne-campus-boundary` (OSM way 4372309, fence/institutional landuse, 11 570 m perimeter, 5.47 km²) | drawn | georeferenced | 15 | none: no official boundary or acreage figure could be fetched (anl.gov 403) |
| Advanced Photon Source ring-shaped Experiment Hall → `geometry:argonne-aps-experiment-hall` (OSM multipolygon relation 3126234: outer way 232798777, inner way 232798786; outer perimeter 1239.5 m, inner 1133 m) | drawn (the hall, **not** the orbit) | georeferenced | 10 | none, see below |
| APS Linear Accelerator Tunnel (411) → `geometry:argonne-aps-linac-tunnel` (OSM way 1378754812) | drawn | georeferenced | 10 | none; function rests on the OSM name (`source=local knowledge`) |
| APS Injection Wing (412) → `geometry:argonne-aps-injection-wing` (OSM way 232798785) | drawn | georeferenced | 10 | none; same caveat |
| Building 203 "Physics Building" → `geometry:argonne-building-203-atlas` (OSM way 283559227; the building that houses ATLAS) | drawn (whole building, not the linac) | georeferenced | 10 | none |
| APS storage ring orbit (1104 m circumference) | **unlocated** (map row on `facility:argonne-national-laboratory`) | — | — | — |
| ATLAS accelerator layout (injectors, booster, ATLAS linac, target areas) | **unlocated** | — | — | — |

**Sources fetched and quoted**

* APS orbit circumference: "The APS storage ring, 1104 m in circumference, has 40 periodic
  sectors." — OSTI record 283724, *The Advanced Photon Source list of parameters*
  (https://www.osti.gov/biblio/283724), read via WebFetch of the record abstract. Used for the
  `unlocated[]` reason and the notes, not as a `checks[]` row (no shape here measures the orbit).
* ATLAS building: "ATLAS is located in Building 203 at Argonne National Laboratory, the same
  building where Marie Goeppert-Mayer worked on her Nobel-prize winning contributions to the
  nuclear shell model." — Argonne Physics Division, *The ATLAS Facility at Argonne National
  Laboratory* (laboratory portrait ANL/PHY/PP-87036, 29 Jul 1997), OSTI record 505382,
  PDF page 1 (the PDF is a scan with no text layer; I read the page image). Its Figure 1 is an
  unscaled cutaway and is linked under `map.schematics`, never traced.

**Honesty calls and conflicts**

1. *The APS ring was not drawn as a ring.* OSM maps only the ring-shaped hall (inner outline ≈
   1133 m, outer ≈ 1240 m). The sourced 1104 m orbit is 2.6 % shorter than the inner outline,
   which is expected for a beam path inside a hall wall, but that is plausibility, not a
   measurement of the orbit. A `length` check on the hall polygon measures the outer ring
   (1240 m, +12 % vs 1104 m) and would fail; a loosened tolerance would be a fake check. No circle
   was fitted: the APS lattice is 40 sectors, and no source gives a radius and centre.
2. *Building 203 ≠ ATLAS.* The report identifies the building; the comb-shaped footprint
   (15 961 m², 266 m span) includes the Physics Division's offices and labs. It is labelled as the
   building, never as the accelerator.
3. anl.gov, www.phy.anl.gov, map.anl.gov and the sandbox mirror all returned HTTP 403 to
   every fetch (curl with a browser User-Agent and WebFetch); `eic-doccert.phy.anl.gov` does not
   resolve. The official ATLAS and APS prose pages could not be read, so the official quotes come
   from OSTI-hosted laboratory documents.

**Site coordinate corrections** (for the integrator; none applied here)

```json
[{"site_id": "site:argonne-campus",
  "current": {"lat": 41.67364, "lon": -88.00173, "precision_m": 800, "source": "src:ror-05gvnxz63"},
  "proposed": {"lat": 41.709622, "lon": -87.980823, "precision_m": 500, "kind": "campus"},
  "distance_from_current_m": 4361,
  "source": "src:geo-argonne-osm-campus-boundary (OSM way 4372309, 'Argonne National Laboratory', addr:street Cass Avenue 9700, barrier=fence, source=survey)",
  "quote": "OSM tags: addr:housenumber=9700, addr:street=Cass Avenue, name=Argonne National Laboratory, barrier=fence, landuse=institutional; centroid of the 131-node fence polygon.",
  "note": "The ROR point lies about 4.4 km south-west of the fenced campus, near the village of Lemont, and well outside the existing precision_m of 800."}]
```

**Remaining backlog**

1. APS storage-ring path: an APS Upgrade TDR survey/alignment table or a published lattice drawing
   with sector coordinates, to place the orbit and add a `length` check against 1104 m.
2. ATLAS: a Building 203 survey drawing or the ATLAS floor plan (a graphic at
   phy.anl.gov/atlas/facility/floorplan.html) georeferenced against ≥ 3 OSM building corners
   (cite, never copy); then the three target areas and the linac axis.
3. An official campus acreage or boundary figure (anl.gov is blocked from here) for an `area`
   check on the boundary.
4. Atlas-side: `accelerator` records for the APS and ATLAS would let the ring/linac be features
   with an `entity_id` (this stream may not create entities).

---

## 2. isis-neutron-source (`map:isis-neutron-source`)

**Grade: no map → partial (footprints only).** No accelerator, beamline or target-station record
exists for ISIS, so the two target-station buildings are context features attached to the site by
`site_id`. The synchrotron could not be placed.

| Entity / feature | Status | Representation | accuracy_m | Check |
| --- | --- | --- | --- | --- |
| `site:isis-rutherford-appleton` → `geometry:isis-ral-campus-boundary` (OSM way 69870055, landuse polygon, 4648 m perimeter, 0.755 km²) | drawn | georeferenced | 15 | none (no official boundary figure) |
| Target Station 1 building R55 → `geometry:isis-ts1-building-r55` (OSM building:part way 1454005510; 5528 m², 116 m span) | drawn (the hall, not the target) | georeferenced | 10 | none |
| Target Station 2 building R80 → `geometry:isis-ts2-building-r80` (OSM way 750266080, "R80 (TS2)"; 7395 m², 122 m span) | drawn | georeferenced | 10 | none |
| ISIS proton synchrotron, 163 m circumference | **unlocated** | — | — | — |
| `detector:karmen` (17.7 m from the target, 100° to the beam) | **unlocated** | — | — | — |

**Sources fetched and quoted**

* "Target Station 1 (R55)" and "Target Station 2 (R80)" — ISIS, *Safety information*
  (https://www.isis.stfc.ac.uk/safety-information/), fetched in full. Same page: "Radiation surveys
  are carried out in R55 and R80 before the start of every user cycle". This is what ties the OSM
  building names to the target stations.
* "The 163 m circumference, 800 MeV, 50 Hz rapid cycling synchrotron accelerates up to 3·10^13
  protons per pulse." — IPAC 2014 MOPRI115, *Activation Models of the ISIS Collectors*
  (https://proceedings.jacow.org/IPAC2014/html/auth1826.htm), abstract as returned by WebFetch.
  Used in the `unlocated[]` reason, not as a check (no shape here measures the ring).
  Corroborated by an NI/ISIS case study ("the beam makes 12,000 revolutions of the 163 m
  circumference").
* A 2022 ISIS talk (Faircloth, indico.stfc.ac.uk event 509) has the hidden caption "ISIS Target
  Station 1 in Building R55" on a photo slide; not cited, because a picture caption in a slide
  deck is weaker than the safety page.

**Honesty calls and conflicts**

1. OSM has no ring, tunnel or synchrotron hall for ISIS (searched the whole RAL bbox for
   "synchrotron", "isis", "target", "accelerator"). The only OSM element named "ISIS" is a
   983 m² building tagged R5.1; its function is not stated by any source, so it is not drawn. The
   enclosing OSM building way 200338759 (R55 plus the smaller R5.1–R5.5 block) is not drawn as the
   hall: its own fixme says "R55 is the experimental hall only", so the `building:part` named R55
   is used. A 163 m ring would have a diameter near 52 m (not a claim: no source states the ring
   is circular, radius or centre), and no sourced building or centre exists to draw one.
2. KARMEN: the detector record has a sourced 17.7 m / 100° offset from the ISIS target, but the
   target and beam axis have no sourced coordinates and the site point is 1500 m campus-grade.
   Not derived (rule: never derive a shape from a campus-grade point).
3. `site:isis-rutherford-appleton` counts as drawn through the campus-boundary feature, so no
   `map-entity-unaccounted` warning is raised for the KARMEN-hosting site; `detector:karmen` is
   listed explicitly as unlocated regardless.

**Site coordinate corrections**: none. The site point (51.570862, -1.315498) is 0.07 km from the
centroid of the OSM RAL polygon (51.570768, -1.315704), well inside its 1500 m precision.

**Remaining backlog**

1. Synchrotron: an ISIS/STFC site plan or design report placing the ring in the R5 complex,
   georeferenced against ≥ 3 OSM building corners; then a `length` check against 163 m.
2. Target positions and the proton-beam axis (site plan or KARMEN technical paper) to place
   KARMEN from its sourced 17.7 m / 100° offset.
3. The ISIS linac (70 MeV) and the beamline from the synchrotron to TS2 (the TS2 extraction
   line); no fetched source gives either.
4. An official RAL campus boundary/area for an `area` check.

---

## 3. ill-grenoble (`map:ill-grenoble`)

**Grade: no map → layout to scale** (a structural hall with a passing official check, footprints,
and a derived core cylinder). No accelerator or beamline exists for ILL.

| Entity / feature | Status | Representation | accuracy_m | Check |
| --- | --- | --- | --- | --- |
| `site:ill-grenoble-reactor-hall` → `geometry:ill-reactor-hall` (OSM way 191447189, name:en "Reactor Hall", ref ILL 5; 42-node near-circle, vertex radii 29.76–29.96 m) | drawn, `feature_type: hall` | georeferenced, confidence **verified** | 5 | `span` expected 60 m (ILL engineering paper, inner-shell diameter) vs measured 59.79 m, tolerance 3 % → **pass** (0.35 %) |
| ILL Guide Hall 1 → `geometry:ill-guide-hall-1-ill7` (OSM way 191447188, ref ILL 7; 6654 m², 142 m span) | drawn, `hall` on `facility:ill-grenoble` | georeferenced | 8 | none (no official dimension fetched) |
| ILL Guide Hall 2 → `geometry:ill-guide-hall-2-ill22` (OSM way 191447185, ref ILL 22; 3360 m², 95 m span) | drawn | georeferenced | 8 | none |
| EPN campus boundary → `geometry:ill-epn-campus-boundary` (OSM way 64549604, 352 000 m², 939 m span; shared with the ESRF) | drawn, context | georeferenced | 15 | none |
| Reactor core cylinder → `geometry:ill-reactor-core-cylinder` (7 m circle at the building's centre) | drawn, context | **derived** | 5 | none (the diameter is the input) |
| `detector:ricochet-cryocube` (8.8 m from the core) | **unlocated** | — | — | — |

**Sources fetched and quoted**

* "The building consists of a cylindrical concrete shell of 60 m diameter and 40 m height (inner
  shell)" and "The centre of the raft supports a concrete cylinder 7 m in diameter, 2 m thick and
  15 m in height. This cylinder is the core of the reactor." — L. Germane (ILL), J.-M. Thiry,
  F. Plewinski, *Seismic strengthening of the ILL High Flux Reactor building*, IGORR 10 (2005), §2
  (https://www.igorr.com/_media/proceedings:2005_igorr10:germane-seismic_strengthening_of_the_ill_high_flux_reactor.pdf),
  full text read with pdftotext.
* "Guide hall 1 (ILL7)", "Guide hall 2 (ILL22)" — ILL, *Take a virtual 360° tour of the ILL*
  (https://www.ill.eu/en/the-facility/take-a-virtual-360-tour-of-the-ill/), fetched in full.

**Honesty calls and conflicts**

1. *Reactor hall `verified`.* The span check confirms that the OSM outline is the 60 m cylindrical
   reactor building (not another building at that spot); the location itself rests on OSM (cadastre
   import, source tag `cadastre-dgi-fr`, 2012). This is the contract's rule (rank ≤ 10 source plus a
   passing check) and the same pattern as the LHC/HERA rings; the check is on the footprint's
   size, not on its position. The 60 m figure is the *inner shell*; the OSM outline is the outer
   footprint and still measures 59.79 m, so the two agree within 0.35 %. An *area* check
   (π·30² = 2827 m² vs 2785 m²) was not written: that would derive its expectation from the
   diameter rather than quote an official area.
2. *ILL 5 = reactor building.* ILL's own building naming ("reactor building (ILL5)") appeared only
   in a web-search snippet of ILL's installations page, which returned HTTP 503 on every direct
   fetch (`www2017.ill.eu`). It is **not** cited. The number rests on the OSM tag plus the passing
   60 m diameter check.
3. *ILL 22 = Guide Hall 2* rests on the building number matching exactly between OSM's `ref` and
   ILL's page; OSM gives no name for it.
4. *Core cylinder is a circle.* Allowed here because a source gives the cylinder's diameter (7 m) and
   its position (centre of the circular foundation raft under a cylindrical building whose
   outline is itself near-circular, radii within 0.2 m). `derived`, accuracy 5 m. It is the
   cylinder housing the pool and vessel, not the fuel element.
5. *Ricochet not placed.* Only "8.8 meters away from the 58 MW research nuclear reactor core" is
   sourced (src:cevns-ricochet-fast-neutron-2022): a distance without a bearing.
6. **`hepgraph.atlas.geo.centroid` defect (report, not fixed; `hepgraph/` is off-limits).** It
   multiplies absolute lon/lat in the polygon cross product, so for a polygon only a few metres
   across it loses precision: for the 7 m core circle `measured.centroid` in the bundle comes out
   at 45.205763 N instead of 45.206099 N (37 m off). The shape itself, its area and its span are
   right and the browser does not use `measured.centroid`; the fix is to subtract the first vertex
   before forming the cross products.

**Site coordinate corrections** (for the integrator; none applied here)

```json
[{"site_id": "site:ill-grenoble-reactor-hall",
  "current": {"lat": 45.206239, "lon": 5.692774, "precision_m": 200, "kind": "campus", "source": "src:cevns-ill-wikipedia"},
  "proposed": {"lat": 45.206099, "lon": 5.692848, "precision_m": 30, "kind": "campus"},
  "distance_from_current_m": 17,
  "source": "src:geo-ill-osm-reactor-hall (OSM way 191447189) with src:geo-ill-igorr-2005-reactor-building",
  "quote": "The building consists of a cylindrical concrete shell of 60 m diameter and 40 m height (inner shell)",
  "note": "Centroid of the circular reactor building (also the reactor-core axis). The existing point is already within 17 m; the improvement is mainly the precision (200 m -> 30 m). The Ricochet detector itself is 8.8 m from this axis in an unsourced direction."}]
```

**Remaining backlog**

1. Ricochet CryoCube position: an installation drawing, or a paper giving the room/bearing from
   the core; then a point on the 8.8 m circle about the core cylinder.
2. Official dimensions of the guide halls (ILL annual reports 1992–1995 on ill.eu may list them;
   ILL's installations-overview page was unreachable, HTTP 503) for `span`/`area` checks.
3. The H-beam tubes and neutron-guide paths from the reactor to the guide halls; no fetched source.
4. ILL's building-number page, to cite "ILL5/ILL7/ILL22" directly once ILL's site is reachable.

---

## 4. kit-karlsruhe (`map:kit-karlsruhe`)

**Grade: no map → partial (footprints only).** The previous KIT worklog (`GEOMETRY_desy-psi-kit.md`)
found no KATRIN building because Overpass was down and Nominatim cannot search by tag. The OSM API
bounding-box read found a named element, so a map is now possible; the beamline itself is still
not placeable.

| Entity / feature | Status | Representation | accuracy_m | Check |
| --- | --- | --- | --- | --- |
| `site:kit-campus-north` → `geometry:kit-campus-north-boundary` (OSM way 155843597, 2.04 km², 2584 m span, `source=estimate`) | drawn | georeferenced | 30 | none (no official figure) |
| `detector:katrin` → `geometry:kit-katrin-experiment-outline` (OSM way 394890935 "Karlsruhe-Tritium-Neutrino-Experiment", 13 nodes, 879 m², 55.6 m long at bearing 16°, man_made=observatory indoor=yes) | drawn as `experimental_area` | georeferenced | 10 | none; the 55.6 m long axis is shorter than the ≈ 70 m setup, so no length check is asserted |
| TLK building 451 → `geometry:kit-tlk-building-451` (OSM way 99082515, ref 451; 792 m²) | drawn | georeferenced | 10 | none |
| TLK building 452 → `geometry:kit-tlk-building-452` (OSM way 99082477, ref 452; 3374 m²) | drawn | georeferenced | 10 | none |
| KATRIN beamline axis and components (source, transport, pre-spectrometer, main spectrometer, detector; overall ≈ 70 m) | **unlocated** (map row on `facility:kit-karlsruhe`) | — | — | — |

**Sources fetched and quoted**

* "Figure 1: Schematic view of the KATRIN experimental setup. The overall length of the setup is about
  70 m." and "the WGTS magnet cryostat system was positioned in the TLK hall" — KATRIN
  collaboration, *The Design, Construction, and Commissioning of the KATRIN Experiment*
  (arXiv:2103.04755v3, JINST), full text read. The same paper gives the main spectrometer vessel as
  "23.23 m long and has an inner diameter of 9.8 m", and orientation as upstream (south) to
  downstream (north), with no azimuth.
* "The overall length of the experiment exceeds 70 meters" — https://www.katrin.kit.edu/1032.php
  (official KATRIN page, fetched).
* "Building 451/452" — KIT Tritium Laboratory Karlsruhe handout
  (https://www.tlk.kit.edu/downloads/Handout-TLK.pdf), address block; same handout "KATRIN is hosted
  at TLK".
* Corroboration only (rank 12, no source record): de.wikipedia "KATRIN" gives 49.095717 N,
  8.436117 E (49° 5′ 44.6″ N, 8° 26′ 10″ E) and en.wikipedia 49.09583 N, 8.43611 E; the OSM outline
  centroid (49.09574 N, 8.435976 E) is about 10 m from the German value.

**Honesty calls and conflicts**

1. *The beamline was not drawn as a line.* A line along the outline's long axis would have been a
   guess at both end points (the outline is 55.6 m, the setup is ≈ 70 m; the source cryostat sits in
   the TLK hall, outside the outline) and at the lateral position inside a 12–16 m strip. No
   fetched source gives an azimuth or any end-point coordinate. Left in `unlocated[]`.
2. *The outline is typed `experimental_area`, not `hall`.* Whether the OSM mapper meant the spectrometer
   hall or the beamline footprint is not stated; the KATRIN paper gives no hall dimensions or
   building number. It overlaps OSM building 460 and abuts the east end of TLK 452. The map's
   grade therefore stays "partial".
3. *TLK 451/452 identification* rests on the OSM `ref` matching "Building 451/452" in the KIT
   handout; which one holds the WGTS is not stated. The 1600 m² quoted in the handout is the TLK's
   laboratory area, not a footprint, and is not used as a check.
4. The campus outline carries the mapper's `source=estimate`, so its accuracy is 30 m rather than 15.

**Site coordinate corrections** (for the integrator; none applied here)

```json
[{"site_id": "site:kit-campus-north",
  "current": {"lat": 49.09591, "lon": 8.42661, "precision_m": 1500, "kind": "campus", "source": "src:katrin-kit-campus-north-coordinates"},
  "proposed_option_a_campus": {"lat": 49.099694, "lon": 8.431813, "precision_m": 600, "kind": "campus",
     "source": "src:geo-kit-osm-campus-north (centroid of OSM way 155843597)", "distance_from_current_m": 567},
  "proposed_option_b_katrin_hall": {"lat": 49.09574, "lon": 8.435976, "precision_m": 30, "kind": "detector",
     "source": "src:geo-kit-osm-katrin-outline (centroid of OSM way 394890935; de.wikipedia 49.095717, 8.436117 within 10 m)",
     "quote": "name=Karlsruhe-Tritium-Neutrino-Experiment, short_name=KATRIN, man_made=observatory", "distance_from_current_m": 680},
  "note": "The site holds only detector:katrin, so option B (hall-grade point) is the one that would remove the A23 'campus-grade point' warning; the old point is inside the campus polygon, so option A is only a refinement."}]
```

**Remaining backlog**

1. As-built KATRIN layout: the TDR as-built update or a geodetic survey giving the beam axis
   azimuth and end points; then draw the beamline and check it against 70 m.
2. KIT Campus North GIS (with licence) or a building directory naming the spectrometer hall
   (OSM building 460 is the leading candidate, unconfirmed) and giving its dimensions.
3. Which TLK building houses the WGTS/transport sections.
4. The monitor-spectrometer hall and the parallel monitor beamline (mentioned in the KATRIN
   paper's Figure 1 caption); not located in any fetched source.
