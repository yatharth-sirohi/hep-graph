# Release geometry stream "accel" (2026-10-25)

Facilities: PSI, Oak Ridge (SNS), Los Alamos (LANSCE), Jefferson Lab, Fermilab.
Worktree `/Users/yatharthsirohi/Desktop/HEP-Graph-ar-accel`, branch `atlas-release-accel`.
New sources are prefixed `src:<facility>-geo-*` / `src:geo-*`.

## Method note: Overpass was down, OSM data came from the OSM API

`overpass-api.de` answered the first status probe with a TLS hang and then, for a
real query, with `HTTP 502 "This Overpass API server is currently at capacity"`;
`lz4.overpass-api.de`, `overpass.kumi.systems` and `overpass.private.coffee` did not
connect and `maps.mail.ru` returned a 504. Per the etiquette in the brief no retry
loop was run. Instead the OpenStreetMap API itself was used
(`https://api.openstreetmap.org/api/0.6/map?bbox=...` for small boxes, tiled to stay
under the 50 000-node limit, and `.../way/<id>/full` for single elements). That is a
read of the same OSM database; it returns the current version of each element but has
no `timestamp_osm_base`, so every `osm.timestamp` below is the HTTP `Date` of the
response, and each source record carries the element version and its own last-edit
timestamp. Raw responses are in the stream's scratch directory, not in the repository.
INSPIRE was not touched.

## Fermilab (map:fermilab)

Grade before: layout to scale (tier B), Main Injector, Recycler and PIP-II unlocated.
Grade after: layout to scale; Main Injector and Recycler drawn; PIP-II still unlocated.

### Inventory (new or changed)

| Entity | Status | Representation | accuracy_m | Check |
| --- | --- | --- | --- | --- |
| accelerator:fermilab-main-injector | drawn: geometry:fermilab-main-injector-ring (ring, level `mi-recycler-tunnel`) | derived | 30 | length 3319.37 m vs 3319.419 m (TDR Table 1-1), tolerance 0.2%: pass (0.0015%) |
| accelerator:fermilab-recycler | drawn: geometry:fermilab-recycler-ring (same plan-view path) | derived | 30 | length 3319.37 m vs "3.3 km" (NuMI paper), tolerance 1%: pass (0.59%) |
| (context) MI-62 service building | drawn: geometry:fermilab-mi-62-service-building (OSM way 272687522) | georeferenced | 8 | none (identity check below) |
| accelerator:fermilab-pip-ii | unlocated, reason and backlog rewritten | - | - | - |

### How the Main Injector was drawn (and why it is not a circle)

The TDR (`beamdocs.fnal.gov/AD/DocDB/0042/004294/001/fermilab-design-1994-01.pdf`,
the same mirror the earlier pass used) gives enough lattice data to compute the
plan-view shape exactly:

* Table 1-1: 216 dipoles of 6.1 m and 128 of 4.1 m, one field (17.2 kG), circumference
  3319.419 m, superperiodicity 2; ch. 2: eight straight sections of 138, 52, 69, 52,
  138, 52, 69, 52 m in the order MI-60, 62, 10, 22, 30, 32, 40, 52, each flanked by four
  12.9665 m dispersion-suppressor half-cells per side; normal half-cells are 17.2886 m.
* The number of normal half-cells in each arc (2, 12, 38, 2 per half ring) was counted
  from the dipole positions in the TDR's MAD listing (OCR of the appendix; about 300 of
  344 dipole rows were readable, enough to fix every run boundary; the sum 54 per half
  ring and the straight-section centres reproduce the table's own positions).
* Uniform field means bend angle proportional to dipole length, rho = 293.2 m. The
  integrated path closes, is 3319.414 m long, and is a "sheared oval" with one long
  103 degree arc and arcs of 41, 18 and 18 degrees.
* **Independent check of the reconstruction** (a TDR statement not used to build it):
  "The line from MI-52 to MI-62 is offset 28.789277 m from the MI-60 straight section
  and parallel to it." The reconstruction gives 28.74 m and 28.89 m (mean 28.82 m,
  0.1%) and parallel to 0.02 degrees.
* Placement: the shape was fitted (one rotation and one translation, no scaling) to the
  private service road OSM way 21813770 "Indian Creek Road" that encircles the ring.
  Trimmed least squares gives a 3.7 m standard deviation of road-to-ring distance at a
  constant 40 m offset (the road is outside the ring everywhere along the 2 km that
  follows it); a 10 m shift raises it to 5-8 m; the mirror-image shape gives 7.0 m.
* **Checks not used in the fit**: the OSM building named "MI-62" has its centroid 9 m
  from the derived centre of the MI-62 straight; the fitted MI-60 line is 1025.9 m from
  the centre of the Tevatron circle on this map, against the TDR's R + 11.823 m =
  1014.5 m ("The MI-60 straight section is parallel to the Tevatron FO straight section,
  separated from it by 11.823 m horizontally"); the F0 tangent direction estimated from
  the CDF and D0 halls differs from the fitted MI-60 heading by 6 degrees (the Tevatron
  circle is itself only good to about 60 m, so this is consistent, not tight).
* A road is a proxy for the tunnel, so accuracy_m is 30 (the ring-road tier) and
  confidence stays `derived`.

The Recycler is drawn on the same line because two sources say so: "The Recycler is a
fixed energy machine of 8 GeV located on the top of the MI with the same circumference
of 3.3 km" (NuMI paper, arXiv:1507.06690) and "installed in a common tunnel"
(Nagaitsev, arXiv:1408.0759, Fig. 5). Its height in the enclosure and any local sideways
offset are not sourced and not drawn.

Principal sources (re-open these):
* https://beamdocs.fnal.gov/AD/DocDB/0042/004294/001/fermilab-design-1994-01.pdf (ch. 1 Table 1-1; ch. 2 section 2.1)
* https://www.openstreetmap.org/way/21813770 (Indian Creek Road, version 15, 2026-05-07T14:51:20Z)
* https://www.openstreetmap.org/way/272687522 (building "MI-62")
* https://arxiv.org/abs/1408.0759 and https://arxiv.org/abs/1507.06690 (Recycler in the MI tunnel)

### Warnings left on Fermilab files

* `geometry-duplicate-shape` on `geometry:fermilab-recycler-ring`: intentional, one tunnel
  drawn for two machines (same pattern as LEP/LHC on map:cern).

### Source conflicts

None new. The earlier pass recorded MI-0274 (Recycler radius) as login-gated; it was not
needed. An unverified "~509.3 m bending radius" noted by the earlier pass is not used;
the radius here is computed from the TDR's dipole counts and lengths (293.2 m).

### Site coordinate corrections

None new for Fermilab.

### Remaining backlog (Fermilab)

* PIP-II: a dimensioned site plan or a published front-end coordinate and azimuth (CDR
  FERMILAB-DESIGN-2017-01 from a mirror other than lss.fnal.gov; the IWAA 2024 talk's
  layout slide read by a person). The tunnel is 210-215 m straight plus a 300 m
  transfer line to the Booster per the 2024 alignment papers; no coordinates are public.
* Mu2e, KTeV, MINERvA, DONUT, DUNE near detector, LBNF: nothing new in OSM
  (Nominatim name searches over the campus returned no results on 2026-10-25).

## PSI (map:psi)

Grade before: marker only (campus boundary, accelerator:psi-hipa unlocated).
Grade after: layout to scale (a verified hall plus principal buildings and the campus footprints); accelerator:psi-hipa still unlocated.

### What made it possible

PSI's own **Arealplan of 18.11.2015** (`https://indico.psi.ch/event/4127/attachments/7754/9862/PSIsitemapESS.pdf`,
hosted by PSI) has a text-layer legend that maps PSI's four-letter building codes to names
("WEHA Experimentierhalle B7", "WIHA Injektorhalle 2 B6", "WNAB UCN-Halle A7", "WNHA
Neutronenhalle B7", "WNLA Neutronenleiterhalle B7", "WMFA UCN-Betriebsgebäude A7",
"WNAA Nukleonenhalle A7"). The OSM mappers named the PSI buildings by exactly those codes,
which the earlier pass could not see through Nominatim. The plan itself was read for its
legend only; it was not traced and is not copied. A 2009 PSI talk (M. Seidel, J-PARC,
`https://www2.kek.jp/accl/legacy/seminar/file/mike_seidel_PSI_accelerators.pdf`, slide 6)
gives the experimental hall as "130x50x20 m3" and the Ring Cyclotron as "ø15m".

### Inventory

| Entity | Status | Representation | accuracy_m | Check |
| --- | --- | --- | --- | --- |
| site:psi-villigen | drawn: geometry:psi-campus-boundary (unchanged) and geometry:psi-experimental-hall-weha (hall, OSM way 28028423) | georeferenced, **verified** (hall) | 8 | perimeter 370 m vs 360 m (2 x (130 + 50), PSI 2009 talk), tol 5%: pass (+2.8%); area 6916 m^2 vs 6500 m^2, tol 8%: pass (+6.4%). OSM footprint 134.0 m x 52.4 m |
| (context) Injector 2 hall WIHA | geometry:psi-injector-2-hall-wiha (way 28028422), 52.1 m x 19.1 m | georeferenced, approximate | 8 | none (no official dimension found) |
| (context) SINQ building | geometry:psi-sinq-building (way 694278565), 124.8 m x 35.4 m | georeferenced, approximate | 8 | none |
| (context) UCN hall WNAB | geometry:psi-ucn-hall-wnab (way 736230166), 29.2 m x 12.8 m | georeferenced, approximate | 8 | none |
| (context) 109 other campus buildings | geometry:psi-campus-buildings (MultiPolygon) | georeferenced, approximate | 8 | none |
| accelerator:psi-hipa | **unlocated** (reason and backlog rewritten) | - | - | - |
| detector:meg, detector:meg-ii, detector:mu3e | accounted through site:psi-villigen; no hall attributed | - | - | - |

The hall's `verified` rests on identity (official legend) plus a passing size check against PSI's own
dimension; the polygon itself is still a third-party tracing. The expected perimeter and area are my
products of the quoted 130 m x 50 m (stated in each check's note).

### What could not be done

* **The Ring Cyclotron is not placed.** No fetched source says which building holds it: the Arealplan
  legend has no "Ringzyklotron" entry (it does have WEHA, WIHA, WNAA "Nukleonenhalle", WHFA
  "Hochfrequenzgebäude"), PSI's HIPA page and talks give its layout only as an unscaled diagram, and
  searches for "Nukleonenhalle" + Ringzyklotron found nothing. Candidate buildings (for example WNAA,
  WMHA, or the WEHA hall itself) were not chosen by shape; guessing would put a 15 m machine in a
  building because it is the right size. HIPA therefore stays unlocated, and WEHA/WIHA are drawn as
  context (WEHA as a `hall` of the site, WIHA as a building) rather than as HIPA's own features.
* MEG II and Mu3e: no source found that says which hall they are in (they are placed on the campus
  site); they are not attributed to WEHA. Mu3e records were not touched (known unrelated validator errors).
* No official figures were found for WIHA, SINQ, UCN-Halle (no checks).

### Site coordinate corrections

None new. `site:psi-villigen` was already moved onto the campus by the integrator on 2026-09-21.

### Warnings left on PSI files

None attributable to the PSI geometry or map records. The A23 warning on site:psi-villigen (campus-grade
point for a detector-holding site) is on an existing record.

### Backlog

* A PSI document naming the Ring Cyclotron's building (code in the Arealplan legend, a layout drawing with
  a scale bar, or a GIS layer); then take that building from OSM by its code.
* Official dimensions for the Injector 2 hall, SINQ halls, UCN hall (to add size checks).
* The hall of MEG II / Mu3e (the pi-E5 area) from a PSI document.

### Time check

The map's features carry the campus site's timeline (active from 2026-09 back to the site's first placement);
`geometry:psi-campus-buildings` and the context buildings have no entity and no `valid`, so they are timeless.
Built bundle: all six features present in 2026.

## Jefferson Lab (map:jefferson-lab)

Grade before: partial (campus boundary and CEBAF Center only; accelerator:cebaf unlocated).
Grade after: layout to scale (derived racetrack, four halls, tunnel straights, service buildings, campus buildings).

### What made it possible: the City of Newport News footprint layer

OSM still has no CEBAF element (re-checked 2026-10-25 through the OSM API: 5 786 ways in the box
-85.5..-76.46 x 37.085..37.11, none is a tunnel, hall or ring). The earlier worklog's backlog asked for "a
non-OSM source". The city publishes **building footprints** as open data
(`https://maps.nnva.gov/gis/rest/services/Operational/Building/MapServer/0`, found through the city GeoHub
catalog at geohub.nnva.gov; "photo derived building polygons digitized from 2016 Aerial photography and manually
updated polygons based on site and building plans"; terms: public information, no warranty). Its Jefferson Lab
polygons carry `BLDGNOTE = 'Jefferson Lab #NNN'`, and the numbers are the same ones as the list of buildings on
JLab's own site plan (`src:geo-jlab-site-plan-detail`): #101 Hall A, #94 Hall B, #96 Hall C, #203 Hall D,
#999 Accelerator Tunnel (as #999-01 and #999-02), #39/#49/#63/#50 East Arc Service E2-E5, #68/#56/#40/#45
West Arc Service W2-W5, #21 North Extractor Service, #82 South Extractor Service, #53 Injector Service.
One query over the campus box returned 330 footprints (saved in scratch, not committed).

### The racetrack is derived, and the data over-determine it

* The two #999 footprints are parallel strips 265 m long and 4.5-5 m wide (the tunnel is "about 14 feet across
  and 10 feet high"), axes at bearing 63.6 degrees, **160.7 m apart**.
* The eight arc service buildings lie on two semicircles. A circle fitted to E3-E5 and one fitted to W3-W5 (centres
  on the mid-line between the straights) have radius **80.3 m, equal to half the straight separation**; the six
  fitted buildings sit within 0.6 m of their circles, E2 within 0.2 m, W2 within 4.4 m (it is at the arc's end).
  The extractor and injector service buildings (#21, #82, #53) lie within 1.5 m of the extended straight lines.
  A circle through three points always exists; the independent facts are that its centre falls on the mid-line, its
  radius equals the separation of two lines that were not used in the fit, and E2/E1/W1 fall on the tangent points
  and lines. The 1986 design paper (`tu2-3`, "average arc radius of 80 m") agrees.
* The centre line (two straights of 403.4 m between the arc tangent points, two semicircles) is **1311 m**.

### Inventory

| Entity | Status | Representation | accuracy_m | Check |
| --- | --- | --- | --- | --- |
| accelerator:cebaf | drawn: geometry:jlab-cebaf-racetrack (ring, level `cebaf-tunnel`) | derived | 20 | length 1311.3 m vs "about 7/8 of a mile" (1408 m), tolerance 7.5% (the half-step of eighth-mile rounding): pass, -6.9%, **weak, see conflict** |
| accelerator:cebaf (straights) | geometry:jlab-cebaf-tunnel-999-01 / -999-02 (tunnel polygons from the city layer) | georeferenced, approximate | 10 | none (no official as-built straight length found) |
| accelerator:cebaf (halls) | geometry:jlab-hall-a (#101), -b (#94), -c (#96), -d (#203; valid from 2017) | georeferenced | 10 | Hall A **verified**: span 51.6 m vs "174 feet across" (53.0 m), tol 5%: pass (-2.6%). B, C, D approximate (no official size found) |
| (context) arc, extractor, injector service buildings | geometry:jlab-cebaf-service-buildings (11 footprints) | georeferenced | 10 | the anchors of the arcs |
| (context) 70 other campus buildings | geometry:jlab-campus-buildings | georeferenced | 10 | CEBAF Center (#12) is not repeated: city and OSM outlines are 6.8 m apart, areas 5221 m^2 vs 5262 m^2 |
| site:jlab-newport-news | campus boundary (unchanged, OSM) and CEBAF Center (unchanged, OSM) | | | |

The map centre was moved onto the racetrack (derived, 50 m) and `extent_m` set to 800; the old centre was the
vertex mean of the campus boundary, 470 m to the north.

### Source conflicts

* **Derived tunnel length 1311 m vs the official "about 7/8 of a mile" (1408 m): -6.9%.** `node/14330` and
  `science/unique` both say 7/8 mile; neither gives a figure to better than an eighth of a mile, so 13/16 to 15/16
  mile (1310-1508 m) is the range the words allow and the derived line sits at its lower edge. The check tolerance
  (7.5%) is that rounding half-step, not a value fitted to pass; the record is `derived` and the discrepancy is
  stated in the record's notes. A real extra 100 m of tunnel (spreader/recombiner geometry, beam-switchyard
  connections, or a longer beam path than the tunnel centre line) cannot be excluded from these sources.
* The tunnel depth conflict recorded earlier (25 ft vs 30 ft on two official pages) is unchanged.
* `#999-01` = North LINAC (building 01) and `#999-02` = South LINAC (building 02) is an inference from the part
  numbers and the north/south positions; the records name them "building 999, part 01/02" and say so.

### What was not done

* The beam switchyard, the tunnels to the halls and the cross-section of the arcs (five stacked beamlines) are not
  drawn; no source gives their paths.
* Halls B, C, D have no official size to check against.

### Site coordinate corrections

None. `site:jlab-newport-news` is a campus point (already corrected by the integrator) and was not used as an anchor.

### Warnings left

None attributable to the JLab files.

### Backlog

* An official straight-section length or a JLab figure with a scale to confirm the 403 m straights and the
  total length (the CEBAF 12 GeV design report or a NIM paper on the machine layout).
* Official sizes for Halls B, C, D.
* The same approach (a municipal or county footprint layer with the lab's own numbers) is worth trying for other
  laboratories whose OSM coverage is empty.

### Time check

The ring, tunnel strips and halls take accelerator:cebaf's timeline (active in 2026-10); Hall D is valid from 2017.
The campus-building features have no entity and no `valid` (timeless). Built bundle: all eleven features present in 2026.
