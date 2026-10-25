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
