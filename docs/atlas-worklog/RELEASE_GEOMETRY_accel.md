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
