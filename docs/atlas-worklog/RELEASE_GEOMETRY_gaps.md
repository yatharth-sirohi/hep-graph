# Release geometry stream: gaps

Branch `atlas-release-gaps`, 2026-10-25. Researcher: geometry stream "gaps" (Sonnet 5.5). Task: entities still sitting in a map's `unlocated[]` list after the earlier geometry streams: the DUNE far-detector caverns (SURF), Fermilab beamlines and halls, CERN halls and accelerators, the IceCube Upgrade strings, KEK-PS, SLC arcs, the ZEUS hall.

Method: every number below was read this session from a document fetched with curl (PDFs through `pdftotext`, tables checked against a rendered page image) or from the OSM editing API / Overpass. INSPIRE was not used. Raw downloads are in the session scratch directory, never in `data/`.

## 1. SURF (`map:surf`)

Grade before: partial (surface buildings and the Davis cavern point; the DUNE caverns unlocated). After: partial, now with the two LBNF/DUNE detector caverns drawn to scale on the 4850 Level (layout to scale at the level of the structures that have a published position). The Central Utility Cavern and the drifts are still not drawn.

### Inventory

| Entity | Drawn / unlocated | Representation | accuracy_m | Check result |
| --- | --- | --- | ---: | --- |
| site:surf-4850-level-dune-far-detector, north cavern (modules FD1 east, FD3 west) | drawn: `geometry:surf-dune-north-cavern` | derived | 30 | area 3148.1 m2 vs 3145.5 m2 expected (0.08 %, tolerance 3 %): pass |
| same site, south cavern (modules FD2 east, FD4 west) | drawn: `geometry:surf-dune-south-cavern` | derived | 30 | area 3148.1 m2 vs 3145.5 m2: pass |
| Central Utility Cavern (190 m x 19.3 m) | not drawn (not an atlas entity; map note) | n/a | n/a | n/a |
| detector:dune-far-detector-1, -2 | accounted through the site | n/a | n/a | n/a |

### How the caverns were placed

* Inputs. J. Heise, "Construction and Science of SURF", https://arxiv.org/abs/2603.06504 (pdf https://arxiv.org/pdf/2603.06504, page 11), Table 4 "Location details for specific SURF underground laboratories", rows of the 4850L LBNF Campus: `FD1 (NE) 103.7546341 W 44.3459914 N`, `FD2 (SE) 103.7548042 W 44.3450261 N`, `FD3 (NW) 103.7556732 W 44.3460857 N`, `FD4 (SW) 103.7558433 W 44.3451204 N`, floor elevation 97 m (the 4910 level, 18 m below the 4850 floor of 115 m). The printed table heads its first column "Latitude" and its second "Longitude" but the cells under "Latitude" hold the W longitudes (checked on a rendered image of the page); the hemisphere letters make it unambiguous. The four points form a rectangle 83.29 m x 108.19 m whose long side runs on bearing 277.23 degrees (both pairs: 277.2327 and 277.2325).
* Which module is where. DUNE TDR Vol. III (https://arxiv.org/pdf/2002.03008, section 5.2): "The first detector will be built in the east side of the north cavern and the second detector will be built in the east side of the south cavern". Vol. IV (https://arxiv.org/pdf/2002.03010, section 1.3): "Each cavern houses two 10 kt modules, one either side of the central access drift. Between the two caverns is the central utility cavern". With the table's NE/SE/NW/SW labels this pairs FD1 with FD3 (north cavern) and FD2 with FD4 (south cavern), and makes the 83.29 m side the cavern long axis (the 108.19 m side then separates the caverns, leaving 34.5 m of rock between each cavern wall and the 19.3 m-wide CUC if the CUC is centred between them).
* Footprint. As-excavated size from the Fermilab LBNF/DUNE community meeting of 12 Dec 2023 (https://lbnf-dune.fnal.gov/wp-content/uploads/2023/12/Community-Informational-Meeting-Dec-2023.pdf, slide 27): "65' W, 521.5' L, 91.3' H N/S Detector Caverns" and "63.3' W, 623.3' L, 35.5' H Central Utility Cavern" = 19.81 m x 158.95 m (cavern), 19.3 m x 190.0 m (CUC). The shape is a rectangle of that size centred on the midpoint of each pair, long axis on the pair bearing. No survey outline exists in the sources found, so the ends and walls are idealised; the 28 m roof height and the 4910 floor are not in a plan view.

### Source conflict: cavern length

* DUNE TDR Vol. I (https://arxiv.org/pdf/2002.02967 Fig. 1.4 caption), Vol. III section 5.2 and Vol. IV: "144.5 m long, 19.8 m wide, and 28.0 m high", cryostats 65.8 m x 18.9 m, "A 12 m space between the cryostats". Fermilab slide of Dec 2023 (and May 2023): 521.5 ft = 158.95 m long, 65 ft = 19.81 m wide, 91.3 ft = 27.8 m high.
* Width and height agree. Length differs by 14.45 m (10 %). Evidence for the longer figure being the as-built one: (a) the table's module centres are 83.29 m apart, so two 65.8 m cryostats need at least 149.1 m, which the TDR length cannot hold (the TDR gap of 12 m gives 77.8 m separation); (b) Heise Table 2 "4850L LBNF/DUNE (nominal)" science area 9445 m2 equals 2 x 144.5 x 19.8 + 190 x 19.3 = 9389 m2 (0.6 %), while the "(laser scan)" row, 9958 m2, equals 2 x 158.95 x 19.81 + 3667 = 9965 m2 (0.07 %). The nominal-versus-laser-scan pair is the TDR length versus the longer one. Chosen: 158.95 m. The area check on each cavern row tests exactly this: expected (9958 - 3667) / 2 = 3145.5 m2 per cavern; with the TDR length the area would be 2861 m2 (9 % low, a failure at the 3 % tolerance).
* The expected value assumes the laser-scanned "science area" is two detector caverns plus the CUC; the nominal-row agreement above is the only support for that reading and is stated in the check's note.

### Corroborations and limits (not `checks[]` rows)

* The same table gives the Ross Campus points BHUC (NE) -103.7584188, 44.3462962 and CASPAR (SE); the 2015 Heise table (https://arxiv.org/abs/1503.01112 Table 5, UTM and geographic) has the same BHUC coordinate to 0.5 m (it is quoted to 0.01 arc-second), and the BHUC point is 54 m from the OSM Ross headframe centroid (-103.7578156, 44.3465258), as expected for a campus beside the shaft. The two tables disagree for the LBNF caverns because the 2015 table is an earlier layout: its "LBNF (10 kt Cavern)" -103.754989, 44.345853 and "(30 kt Cavern)" -103.755172, 44.345123 (from 44 deg 20' 45.07" N / 103 deg 45' 17.96" W and 44 deg 20' 42.44" N / 103 deg 45' 18.62" W) lie 32 m from FD1 and 31 m from FD2 respectively, i.e. the same layout moved by tens of metres.
* Accuracy 30 m. The table is a design-model list used for rock-overburden estimates; the coordinates are printed to 1 cm but the table does not say whether they are cryostat centres, pit centres or cone apexes, and the as-built excavation may differ from the model. The midpoint of a pair is insensitive to a symmetric offset; the axis from an 83 m baseline moves 1 degree for a 1.5 m transverse error.
* The LBNF page https://lbnf-dune.fnal.gov/how-it-works/excavations-and-structures/ confirms "Excavation work at the far site began in early 2019 and was completed in February 2024" and "LBNF carved out three long caverns; two of them will contain two far detector modules each, placed end to end".

### Site coordinate corrections (for the integrator)

* `site:surf-4850-level-dune-far-detector`: current 44.3474397, -103.7548247, kind underground_lab, precision_m 2000 (surface proxy from OSM, flagged REVIEW REQUIRED). Proposed: lat 44.3455559, lon -103.7552387 (mean of the four Table 4 module points; the centre of the two caverns), kind underground_lab, precision_m 100, confidence approximate (derived), source `src:geo-surf-heise-2026-review`, locator Table 4 rows FD1 to FD4, quote "FD1 (NE) 103.7546341 W 44.3459914 N 97 1420". The current proxy is 212 m from the proposed centre.

### Backlog

* Central Utility Cavern: an Arup excavation drawing or SURF laser-scan plan giving its offset along the cavern axis. The 3D slide shows it flanked by the two caverns and extending past both ends, which a rectangle could follow once the offset is published.
* A survey outline of the as-built caverns (SURF/Sanford Lab laser-scan campaign cited in Heise Table 2) to replace the idealised rectangle, and the Ross Shaft to cavern drift geometry.
* Resolve whether Table 4 FD points are cryostat centres, from the DUNE site coordinate-system note or from installation survey records.

## 2. Fermilab (`map:fermilab`)

Grade before: layout to scale for the campus rings, the Booster-neutrino short-baseline halls and the NuMI/MINOS surface buildings; the NuMI target and beam derived from OSM buildings (accuracy 30 m); the Main Injector placed by a fit to an OSM service road; underground NuMI structures, LBNF, DUNE ND and Mu2e unlocated. After: layout to scale, with the NuMI facility drawn from published survey coordinates (target, proton beam line, decay pipe, target hall, absorber hall, MINOS enclosure and detector position), the Main Injector and Recycler re-placed from the Main Injector TDR's own site coordinates, and two earlier records corrected (below). LBNF, the DUNE ND hall and Mu2e stay unlocated.

### The key find: a published conversion from Fermilab site coordinates to latitude and longitude

The earlier Fermilab worklogs could not convert Fermilab's local coordinates because the defining document (`ppd.fnal.gov/align/beams-doc-1148.html`) returns 403 to scripts. A copy is on the Internet Archive (`http://web.archive.org/web/2020/https://ppd.fnal.gov/align/beams-doc-1148.html`, fetched once, full text read). B. Oshinowo, "Fermilab Coordinate Systems", Beams-doc-1148 v4.0 (15 May 1997), section 4.2: Fermilab Site Coordinate System (FSCS = DUSAF, in feet) has its origin A0 at "N 41° 50' 14.312704" / W 88° 15' 41.143123"" (NAD83), false easting and northing 100000 ft at A0, +Y axis at geodetic azimuth "38° 16' 48.01429"", double stereographic projection, scale 1.000029251309483. The conversion is implemented here as a rotated tangent plane on GRS80 (within 0.2 m of the projection near A0). Tests of it, all passed:

| Test | Result |
| --- | --- |
| A0 (100000, 100000 ft) maps back to the published A0 | exact |
| NuMI beam sheet: bearing from the converted target to the published MINOS far-detector coordinate (47.820267 N, 92.241412 W, MINOS NIM paper Sec. 6.5) | 336.169 deg; the sheet's own beam axis gives 336.177 deg (0.008 deg) |
| Decay pipe length from converted coordinates | 674.19 m horizontal; station difference 2214.57 ft = 675.0 m (0.05 % after the 3.3 deg pitch) |
| 8 GeV line start (Booster extraction point, MI TDR P8_GEV survey: x = 99511.383 ft, y = 99309.844 ft) | 76.3 m from the centre of the OSM-fitted Booster circle; the sourced 474 m circumference gives radius 75.44 m (0.9 m) |
| NuMI target to MINOS near-detector row MIN_NO | 1038.9 m horizontal; MINOS NIM paper: "The near detector is 1040 m from the primary target" |
| End of the decay pipe from the target | 724.2 m; MINOS NIM paper: the beam "was sent 723 m past the target position" |
| MINOS enclosure upstream end to the OSM MINOS Service Building | 78.8 m; MINOS NIM paper: the detector cart "was pulled about 80 m from the base of the shaft into the near detector hall" |

### Sources used (all fetched this session)

* NuMI Facility TDR, FERMILAB-DESIGN-1998-01 Rev. 1.0 (`https://lss.fnal.gov/archive/design/fermilab-design-1998-01.pdf`, 403 to scripts; read from `http://web.archive.org/web/2016id_/https://lss.fnal.gov/archive/design/fermilab-design-1998-01.pdf`, 380 pages, `pdftotext`). Appendix A is the "beam sheet", "Site coordinates for beamline: horn2.ces": DUSAF x, y (ft) and station for every device from the MI-60 extraction to the downstream end of the MINOS hall. The scanned numbers were transcribed and every pair of consecutive rows checked against the station difference times cos(pitch): all 56 rows agree within 0.6 ft. Section 5.2 gives the enclosure sizes (target enclosure 220 ft x 27 ft, absorber enclosure 50 ft x 27 ft, MINOS enclosure 150 ft x 30 ft).
* Main Injector TDR, FERMILAB-DESIGN-1994-01 (`https://beamdocs.fnal.gov/AD/DocDB/0042/004294/001/fermilab-design-1994-01.pdf`): appendix "Main Injector Ring Site Coordinates (MI_19)" (MAD survey listing) and "8 GeV Line Site Coordinates".
* NuMI NIM paper arXiv:1507.06690 and MINOS NIM paper arXiv:0805.3170 for the cross-check figures; DOE/EA-1943 (`https://www.energy.gov/nepa/articles/ea-1943-final-environmental-assessment`, 12 000 lines of text read), LBNF CDR Vol. 3 arXiv:1601.05823, DUNE ND CDR arXiv:2103.13910, "Design of the LBNF beamline" arXiv:1704.04471 for LBNF.

### Inventory

| Entity | Drawn / unlocated | Representation | accuracy_m | Check result |
| --- | --- | --- | ---: | --- |
| beamline:numi target (rewritten `geometry:fermilab-numi-target`) | drawn | surveyed | 5 | distance to the MINOS detector position 1038.9 m vs 1040 m (MINOS paper), tolerance 1 %: pass |
| beamline:numi proton line, HQ101 to target (`geometry:fermilab-numi-primary-beamline`, 37 vertices) | drawn | surveyed | 5 | length 347.6 m vs "350 m beam line" (NuMI paper), 2 %: pass |
| beamline:numi neutrino axis, target to MINOS hall end (rewritten `geometry:fermilab-numi-beamline`) | drawn | surveyed | 5 | azimuth 336.18 deg vs 336.17 deg to the published Soudan coordinate (0.5 deg): pass |
| NuMI decay tunnel and pipe (`geometry:fermilab-numi-decay-pipe`) | drawn | surveyed | 5 | length 674.2 m vs 675 m (NuMI paper), 1 %: pass |
| NuMI target hall, 220 ft x 27 ft (`geometry:fermilab-numi-target-hall`) | drawn | derived | 15 | span 67.6 m vs "approximately 69 m long" (NuMI paper), 3 %: pass |
| NuMI absorber hall, 50 ft x 27 ft (`geometry:fermilab-numi-absorber-hall`) | drawn | derived | 15 | span 17.3 m vs 17.3 m from the paper's 15.2 m x 8.2 m: pass |
| detector:minos-near-detector position, row MIN_NO (`geometry:fermilab-minos-near-detector-position`) | drawn | surveyed | 5 | distance to the target 1038.9 m vs 1040 m: pass |
| MINOS enclosure, 150 ft x 30 ft, 105 m deep, hosting MINOS ND, MINERvA, ArgoNeuT, SENSEI (`geometry:fermilab-minos-near-hall`) | drawn | derived | 10 | none (all dimensions from one source; position checked through the detector point) |
| accelerator:fermilab-main-injector, accelerator:fermilab-recycler (re-placed) | drawn | derived | 8 (was 30) | length 3317.4 m vs 3319.419 m, 0.2 %: pass |
| detector:minerva, detector:sensei | unlocated (hosted in the drawn MINOS hall; own position not published) | n/a | n/a | n/a |
| beamline:lbnf, detector:dune-near-detector | unlocated | n/a | n/a | n/a |
| detector:mu2e, site:fermilab-mu2e-hall | unlocated | n/a | n/a | n/a |

The new NuMI features sit on a re-purposed level (`near-detector-caverns`, now "NuMI beam enclosures and MINOS near-detector hall (35-105 m below grade)", depth 105 m from the MINOS paper). The target is "approximately 114 ft. below surface grade level" at the beam (TDR 5.2.4) and the Target Hall is "approximately 41 m underground" (NuMI paper): both recorded on the features.

### How the halls were laid out

Corners are computed in the DUSAF plane from the beam axis (bearing 152.18332 deg counter-clockwise from site east, as listed on every sheet row from the target to the end): target hall, 220 ft upstream of the row DECAY (its downstream wall at the start of the decay pipe; the upstream wall then falls 2.5 ft downstream of the baffle row BAFLE1); absorber hall, 50 ft downstream of the row DENCU (the sheet's row MUOND1, 3 ft past that, and the 33 ft of rock to the first muon alcove agree); MINOS enclosure, 150 ft downstream of the row M ENCU (the sheet's rows M ENCD and ROCK fall 150.0 ft beyond it horizontally). The beam is assumed to run on each hall's centre line (the sources give no lateral offset), which is why these three are `derived`. The MINOS detector row MIN_NO is 85.6 ft inside the enclosure, matching the TDR's "85.5 ft from the upstream end".

### Main Injector and Recycler re-placed (correction to the earlier release pass)

* The earlier placement came from a fit of the TDR-derived shape to the OSM service road "Indian Creek Road". A ring road cannot fix a near-circular ring's rotation, and the record's own cross-checks (a single OSM building 9 m from a straight centre) could not detect the error.
* The MI TDR appendix lists site coordinates of every lattice element. Rows read from the scanned page (89 with all digits legible) were fitted by a rotation and translation (no scaling) of the same shape: rms 0.34 m, maximum 0.52 m, lattice origin within 0.5 m of the listed one. The fitted ring is displaced 38-74 m (mean 54 m) from the old one and rotated 5.7 degrees: the MI-60 straight now runs at geodetic azimuth 339.6 deg, against 339.51 deg from Beams-doc-1148 Appendix A ("FSCS Azimuth = 301° 13' 53.9"") and 339.51 deg in the NuMI sheet, where the old ring had 333.8 deg.
* Independent confirmations not used in the fit: the 8 GeV line survey in the same appendix ends 1.2 m from the new ring at path length 588 m, inside the MI-10 straight (570.5-639.7 m), but 9.6 m from the old ring at a position in the arc before it; the LBNF paper's 7.2 degree horizontal bend added to the new MI-10 heading (280.5 deg) gives 287.7 deg, the great-circle bearing from MI-10 to the SURF caverns (287.76 deg), where the old heading would be 5.7 degrees off.
* Side effects handled: `geometry:fermilab-recycler-ring` (identical coordinates, updated with it); `geometry:fermilab-mi-62-service-building` text (its "9 m from the centre of MI-62" statement belonged to the old placement; it is now 14.7 m from the tunnel and 53.6 m from the straight's centre, no contradiction); the OSM source `src:fermilab-geo-osm-indian-creek-road` is no longer cited by anything and was removed.
* Not touched: the Tevatron circle (derived, 60 m, from OSM ring roads). Beams-doc-1148 gives A0 on the Tevatron exactly (41.8373091 N, 88.2614286 W) and the MI-60 line 11.823 m from the F0 straight; with the Tevatron circumference those two facts put the circle centre 38 m from the OSM-fitted centre, inside its 60 m, so it could be tightened by a later pass.

### Source conflicts and corrections

1. NuMI target: the earlier derived position (from the MINOS surface building and 1040 m) is 103 m from the published one, along the beam axis. The MINOS Service Building is 79 m from the hall, so "building above the detector" was wrong; the earlier cross-check from the NOvA building (38.6 m from the first estimate) agreed only because the NOvA building is ~140 m upstream of its detector in the same way. Replaced.
2. `geometry:fermilab-nova-near-surface`: its distance check (964.9 m vs "1 km") had raised it to verified against the wrong target. The building is 861 m from the surveyed target, on the axis (0.8 m off): it is the shaft building, about 140 m upstream of the detector at 1 km. The check was removed and the confidence lowered to approximate.
3. MINOS NIM paper: "330 m from the hadron absorber" disagrees with the TDR geometry (1040 m minus 723.2 m = 316.8 m to the end of the decay pipe; 1036.6 ft = 316 m from the absorber enclosure to the detector face). Not used.
4. Target position within the hall: TDR "Target Enclosure ... 220 ft" vs NuMI paper "approximately 69 m long" (226 ft, includes the upstream extension): the drawn 220 ft is the internal dimension; the span check allows 3 %.
5. LBNF primary beam length: 328 m (1078 ft) "to the target" (CDR 5.3.2), "approximately 1,200 feet" (CDR 6.2.7 and 6.2.8), 1,000 ft (EA). Not resolved; see LBNF below.

### LBNF and the DUNE ND hall: why not drawn

No source gives a coordinate. The chain MI-10 straight (now surveyed) + extraction path length + 7.2 degree bend + 574 m along the bearing to SURF, with the ND hall 38-46 m east of Kirk Road (EA), fits together (the bend check above is exact), but the target stays uncertain to about 50 m through three unknowns (where the beam leaves the 69 m straight, which path length is built, where the bend is). Candidate ranges are in the map row. A 50 m uncertainty on 50 m halls is a marker, not a footprint; per the brief it is left unlocated with that backlog.

### Mu2e: not resolved

No document found ties Mu2e to OSM way 720556732 "MC-2". The Mu2e TDR (arXiv:1501.05241) has no site coordinates (Fig. 6.120 is a drawing); the Muon Campus review (arXiv:2208.02889) does not mention MC-2; two web searches returned nothing. `geometry:fermilab-mc2-building` stays a context feature.

### Site coordinate corrections (for the integrator)

* None for site records. The Fermilab site coordinate origin A0 is 41.8373091 N, 88.2614286 W (published, NAD83).

### Backlog

* LBNF: lattice or site plan in FSCS coordinates (see the map row), then DUNE ND hall 574 m along 287.7 deg.
* Mu2e: a document that names the building, or Mu2e Offline hall geometry.
* Tevatron ring: tighten from A0 and the MI-60 offset (above); the Booster ring from the 8 GeV line start (Booster extraction, 76.3 m from the OSM centre).
* NuMI: lateral offset of the target, absorber and MINOS halls from the beam axis (TDR figures 5-3 to 5-10, not text); the muon alcoves (rows MUON0, MUOND2, MUOND3) are not drawn.
* The NuMI sheet also lists the NuMI horns and baffles; not drawn (metres, not a map feature).

Method lesson for later streams: where a Fermilab design report prints "site coordinates" in feet, they are FSCS/DUSAF and convert with Beams-doc-1148. Converter used here: `fscs.py` in the session scratch directory (rotation by 38.28 degrees plus ellipsoid radii at A0; 15 lines).

## 3. CERN (`map:cern`)

Grade before: layout to scale for the LHC, LEP, SPS, PS and PSB rings, the eight LHC/LEP experiment enclosures and the Meyrin/Prévessin context; seven entities unlocated (UA1 and UA2 sites, CAST, ECN3, HL-LHC, Linac2, ISR). After: the same, plus the surface buildings that mark the UA1, UA2, CAST and ECN3 sites and both HL-LHC surface complexes; two entities stay unlocated (Linac2, ISR).

### The key find: building numbers

CERN names its buildings by number, OpenStreetMap carries those numbers as `name`/`addr:housenumber`, and the lab's public web map (MapCERN, https://maps.cern.ch/) is backed by an open ArcGIS REST service whose "Facilities" layer maps number to acronym and outline. The earlier name searches (UA1, UA2, LSS4, CAST, ECN3) could not succeed because no OSM element is named that way. Queried with a descriptive User-Agent, a few dozen requests: `https://maps.cern.ch/arcgis/rest/services/Hosted/Etages_v2_public/FeatureServer/114` (fields `numero`, `sigle`, `type_ouv`; 823 facilities) and the layer metadata. Found: 868-873 = BA1-BA6 (SPS access buildings), 2875 = SR8, 3155/3154/3180/3169/3168 = SD17/SE17/SU17/SF17/SHM17, 3555/3560/3581/3569/3577 = SD57/SE57/SU57/SF57/SHM57, 911 = BAA85, 918 = BX83. Licence: the service states none (`copyrightText` empty). Only identifiers and areas measured from the service polygons are used (as `expected` values in checks); no MapCERN geometry is copied into a record; shapes are the OSM polygons carrying the same numbers, whose centroids agree with the official ones to 0.7 to 3 m. If the integrator wants a licence statement, ask CERN's GIS group (support via the link in https://maps.docs.cern.ch/).

### Inventory

| Entity | Drawn / unlocated | Representation | accuracy_m | Check result |
| --- | --- | --- | ---: | --- |
| site:cern-sps-lss4-ua2 (UA2) | drawn as SPS access building BA4 (b.871, OSM way 68885471): `geometry:sps-ba4-access-building` | georeferenced, approximate | 8 | area 1463 m2 vs 1495 m2 (MapCERN outline), 5 %: pass |
| site:cern-sps-lss5-ua1 (UA1) | drawn as BA5 (b.872, OSM way 78502933): `geometry:sps-ba5-access-building` | georeferenced, approximate | 8 | area 1027 vs 1032 m2, 5 %: pass |
| site:cern-cast-sr8 (CAST) | drawn as SR8 building (b.2875, way 35204808): `geometry:cast-sr8-building` | georeferenced, approximate | 8 | area 964 vs 982 m2, 5 %: pass |
| site:cern-ecn3-north-area | drawn as the access building b.911 (way 44413082) and the counting rooms b.918 (way 44413083) | georeferenced, approximate | 8 | b.918 area 923 vs 936 m2, 5 %: pass; b.911 none |
| accelerator:hl-lhc | drawn as the five surface buildings at Point 1 (ways 1101838706/4/5, 975205197/6) and at Point 5 (ways 1525136503/4, 1371322442/39) | georeferenced, verified | 8 | total area 3256 m2 (Point 1) and 3351 m2 (Point 5) vs "3300 m2 of buildings" per Point (CERN Accelerating News): pass at 3 %; outlines within 3 m of the official ones |
| accelerator:linac2, accelerator:isr | unlocated | n/a | n/a | n/a |

### What is and is not shown

* UA1 and UA2 stood underground, in the caverns ECX5 and ECX4 (CERN SPS history page, https://be-dep-op-sps.web.cern.ch/history: "Excavation of the ECX4 and ECX5 caverns was started in 1979. By the summer of 1981, installation of the UA1 experiment was completed in ECX5, and likewise for UA2 in ECX4."). The building drawn is the surface access building of point 4 or 5 of the SPS. The link between cavern ECXn and building BAn rests on the shared point number plus CERN's CROME page, which lists the SPS areas as "BA1, BA2, BA4/ECA4, BA5 and BA6"; it is an inference, stated in the records, and the sites are drawn as approximate. The six BA buildings lie 62, 57, 60, 61 and 62 degrees apart around the centre of a circle fitted to the drawn SPS ring (radii 1071-1090 m against the ring's 1101 m, i.e. 10-30 m inside it), so the drawn ring passes within 30 m of every access point, consistent with its stated 30 m accuracy.
* CAST: the CAST site record places the experiment in SR8 (a secondary CERN cryogenics document); no official CAST page found names the building. MapCERN names building 2875 "SR8".
* ECN3: the NACONS table gives "Underground Experimental Cavern 3 (900) ... 1887 m2" and lists b.911 as "Access point for ECN3 underground cavern" and b.918 as "Counting rooms for ECN3 experimental cavern" (the table's m2 are gross floor areas over several levels, so they are not footprint checks). The cavern outline is not published; its building 900 is not in the public MapCERN layers.
* HL-LHC: "A cluster of three buildings is located at the head of the shaft" (SD, SU, SE), SF and SHM stand alone, "Per Point, the total surface corresponds to about 20000 m2, including 3300 m2 of buildings" (CERN Accelerating News issue 20, https://accelerating-news-arc.web.cern.ch/node/358.html); the project news names the shaft PM17 at Point 1 (https://hilumilhc.web.cern.ch/?p=872) and the buildings SU57, SD57, SE57 at Point 5 (https://hilumilhc.web.cern.ch/?p=2491). Not drawn: the PM shafts (9.7 m x 80 m), the US/UW cavern (16 m x 45 m), the 300 m UR gallery and the UA/UL galleries; no source gives their plan position. The task brief's "PM15/PM18" were not found in any source: the HL-LHC shafts at Points 1 and 5 are PM17 and PM57 in the project pages above.

### Source conflicts and honesty calls

1. The earlier site records put UA1, UA2 (and ECN3, CAST) at campus-grade points: LSS4 and LSS5 both at the Meyrin geocoder point (46.2338702, 6.0469869, 3 km), 5 km from where the buildings stand. Corrections below.
2. OSM maps SE57 and SU57 as one polygon (way 1525136504, 1018 m2) where the official outlines are 375 and 679 m2 (sum 1054 m2, 3 % more): drawn as mapped; the total-area check still passes.
3. NACONS areas (b.911: 396 m2, b.918: 847 m2) are gross floor areas, not footprints (b.911 footprint 283 m2 officially, 259 m2 in OSM; b.918 936 and 923 m2), so only MapCERN footprints are used as check values.

### Site coordinate corrections (for the integrator)

* `site:cern-sps-lss4-ua2`: current 46.2338702, 6.0469869, campus, 3000 m (Meyrin geocoder). Proposed 46.248855, 6.068604 (centroid of OSM way 68885471, SPS access building BA4 = b.871 = MapCERN 871 "BA4"), kind campus, precision_m 100 (the cavern is underground at an unpublished offset), sources `src:geo-cern-osm-sps-ba-sr8-buildings`, `src:geo-cern-mapcern-facilities`; quote "871 BA4 BÂTIMENT".
* `site:cern-sps-lss5-ua1`: current the same Meyrin point. Proposed 46.239102, 6.066901 (way 78502933, b.872 "BA5"), precision_m 100.
* `site:cern-cast-sr8`: current 46.2417561, 6.0971635, precision_m 1000. Proposed 46.242110, 6.096939 (way 35204808, b.2875 "SR8"), precision_m 100, confidence approximate (identification of CAST with the building rests on the cryogenics document).
* `site:cern-ecn3-north-area`: current 46.2601088, 6.0577057, precision_m 2000 (Prévessin campus). Proposed 46.264135, 6.061090 (b.911, access to the ECN3 cavern), precision_m 150.

### Backlog

* UA1/UA2 caverns: a CERN civil-engineering drawing or SPS layout giving the ECX4/ECX5 offset from BA4/BA5 and the cavern size (CERN Bulletin 41/1979, https://repository.cern/records/5kt26-j2q14/files/41-1979.pdf, returns 403 to scripts and is a scan without text; it reportedly describes the UA1/UA2 shafts and depths).
* ECN3 cavern: outline of building 900, or the SHiP/ECN3 high-intensity civil-engineering study with a plan.
* HL-LHC underground structures: HL-LHC TDR civil-engineering chapter with plan coordinates (the CYRM download returned HTTP 500 to scripts).
* Linac2 building number and ISR plan (see the map rows).
* CDS (cds.cern.ch) is behind an anti-bot challenge for scripts; not circumvented.
