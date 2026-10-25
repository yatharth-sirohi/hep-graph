# Release geometry stream: underground / reactor sites

Branch `atlas-release-underground`, 2026-10-25. Researcher: geometry stream "underground" (Sonnet 5.5). Facilities: JUNO, Chooz, Brokdorf, Leibstadt, Boulby, Soudan, Baksan. Nothing below comes from memory: every coordinate, distance and depth is quoted from a document fetched in this session (PDFs fetched with curl and read with `pdftotext`; OSM from Overpass, raw responses kept in the session scratch directory, never in `data/`). INSPIRE was not used. Overpass was queried one request at a time, at least 10 s apart, with `User-Agent: HEP-Atlas-research/1.0`; the one 429 and two 502 answers were waited out and retried.

Validation bar given by the integrator: `hepgraph.atlas.validate` reports 0 errors other than the three time-driven `status-not-derived-state` errors on mu3e (not touched).

## 1. JUNO (facility:juno-jiangmen)

Grade before: NO MAP. After: two maps, `map:juno-jiangmen` (campus, tier A partial) and `map:juno-reactor-baselines` (baseline map, tier B partial). `map:juno-jiangmen` is the facility's primary map (alphabetically first, so the derived `facility.map_id` points at it); the baseline map is its authored linked map.

Why two maps: the Yangjiang and Taishan reactors are 52-53 km from the hall. They cannot sit on a 2 km campus map (contract: far sites are linked maps), but the brief asks for them at the published baselines, so they live on a second map of the same facility (precedent: `map:km3net-arca` / `map:km3net-orca` for one facility) centred between the three places, with the hall repeated as a point so each baseline is a measurable `distance` check on one map.

### Inventory

| Entity | Map | Drawn / unlocated | Representation | accuracy_m | Check result |
| --- | --- | --- | --- | ---: | --- |
| site:juno-jiangmen-underground-lab (hall) | juno-jiangmen | drawn: `geometry:juno-experimental-hall` (Point, level `underground-hall`, depth 693.35 m) | surveyed (published coordinate) | 150 | none possible on a Point (see below); consistency with the 8 baselines is checked on the baseline map |
| JUNO surface campus (context) | juno-jiangmen | drawn: `geometry:juno-surface-campus` (OSM way 905454906) | georeferenced | 15 | none (no official area/perimeter found) |
| vertical shaft, inclined tunnel / portal, ancillary caverns | juno-jiangmen | unlocated (row on facility:juno-jiangmen) | n/a | n/a | n/a |
| hall (same point) | juno-reactor-baselines | drawn: `geometry:juno-baseline-hall-point` | surveyed | 150 | n/a |
| Yangjiang reactor buildings YJ-1..YJ-6 | juno-reactor-baselines | drawn, six OSM `building=reactor` ways | georeferenced | 15 | distance to hall vs GPS baseline, all pass at 0.3 % (table below) |
| Taishan EPR buildings TS-1, TS-2 | juno-reactor-baselines | drawn, two OSM buildings each containing one `power=generator` EPR node | georeferenced | 15 | distance to hall vs baseline pass at 0.3 %; separation 252.5 m pass at 3 % |

Checks (expected vs measured; hall = published coordinate, buildings = centroid of the OSM polygon):

| Core | Published baseline (arXiv:2104.02565 Table 1) | Measured | Difference |
| --- | ---: | ---: | ---: |
| YJ-1 | 52 740 m | 52 824 m | +84 m |
| YJ-2 | 52 820 m | 52 922 m | +102 m |
| YJ-3 | 52 410 m | 52 497 m | +87 m |
| YJ-4 | 52 490 m | 52 588 m | +98 m |
| YJ-5 | 52 110 m | 52 235 m | +125 m |
| YJ-6 | 52 190 m | 52 312 m | +122 m |
| TS-1 | 52 770 m | 52 754 m | -16 m |
| TS-2 | 52 640 m | 52 631 m | -9 m |
| Taishan core separation | 252.5 m | 256.6 m | +1.6 % |
| Yangjiang max core separation (YJ-5 to YJ-2) | 736 m | 696.9 m | -5.3 % (tolerance 6 %) |

Principal sources (the integrator can re-open these):

* Hall coordinate: JUNO Collaboration, "JUNO Physics and Detector", https://arxiv.org/pdf/2104.02565, Sec. 1.2: "The geographic location is 112° 31’05” E and 22° 07’05” N." (existing record `src:juno-physics-detector-arxiv-2021`). Same figures in https://arxiv.org/pdf/1507.05613 Sec. 1.3.1 (`src:geo-juno-physics-2015`): "east longitude 112° 31’05” and north latitude 22° 07’05”".
* Baselines: the same paper, Table 1, "surveyed with a Global Positioning System (GPS) to a precision of 1 meter"; core separations "between 89 m and 736 m" (Yangjiang), "252.5 m" (Taishan).
* Depth: same paper, Sec. 1.2: "the vertical overburden for the detector center is 693.35 m (1800 m.w.e)".
* Access: CDR https://arxiv.org/pdf/1508.07166 Sec. 10.1.2 (`src:juno-cdr-arxiv-2015`).
* Reactor buildings: OSM ways 1174744705/706/708/709/711/713 (Yangjiang), 520344774/778 (Taishan), extracts of 2026-10-25T10:40:01Z and 10:42:05Z; campus way 905454906 (10:43:04Z).

### Source conflicts and honesty calls

1. Published coordinate vs the baselines. The six Yangjiang buildings are 84-125 m farther from the published coordinate than the surveyed baselines say; the two Taishan buildings agree to <= 16 m. A pure displacement of the published point of ~100 m toward SSW (bearing ~205°) would remove both, and so would a ~100 m registration offset between the OSM tracings of the two plants; the sources cannot tell these apart. Handling: the hall stays the published coordinate (that is what a source states), `accuracy_m` 150 (arc-second rounding alone is ~21 m, plus the paper's own statement that the hall was moved ~60 m from the design position, with no statement which position the coordinate describes), confidence `approximate` although the representation is `surveyed`. The check tolerance on the baselines is 0.3 % (~155 m at 52 km) so the check fails a coordinate that is more than ~150 m wrong, which is its job.
2. Core separations. OSM domes give 79 m minimum and 697 m maximum against the published 89 m and 736 m (arXiv:1507.05613 says 88 m / 736 m). Only the maximum is a check (6 % tolerance); the minimum is 11 % off and is not used as a check. Probable cause: oblique-imagery offset of ~60 m tall domes in the tracing.
3. Unit labels. The OSM ways carry no unit numbers. YJ-n / TS-n are assigned by matching the order of measured distances to the order of the published baselines. Within each Yangjiang pair the odd unit is the north-eastern one; no source confirms this numbering, and the geometry records say so in `method`.
4. Shaft depth and length figures disagree across the JUNO documents: vertical shaft 581 m (CDR Sec. 10.1.2), 589 m (CDR Sec. 10.2.2.2), 564 m (arXiv:2104.02565); inclined shaft 1,340 m at 42.6 % (CDR) vs 1266 m at 42.5 % (arXiv:2104.02565, after the ~60 m move). The level depth uses the 2021 figure; none of the shaft figures is drawn.
5. Hall footprint not drawn: a 43.5 m (water pool) circle around a 150 m-accuracy point would carry false precision, and the hall outline orientation is not published as coordinates.

### Site coordinate corrections (for the integrator)

* `site:juno-jiangmen-underground-lab`: current 22.11827, 112.51867, kind campus, precision 2000 m (Wikipedia, rank 12). New: lat 22.1180556, lon 112.5180556 (112 + 31/60 + 5/3600 and 22 + 7/60 + 5/3600), kind `underground_lab`, precision_m 150, confidence approximate, source `src:juno-physics-detector-arxiv-2021` (plus `src:geo-juno-physics-2015`), quote "The geographic location is 112° 31’05” E and 22° 07’05” N." Note: kept approximate because of conflict 1; the Wikipedia point is 68 m from the published coordinate, consistent with it.

### Backlog

* Portal and vertical-shaft coordinates (JUNO civil drawings, TDR / construction paper civil chapter, or an OSM feature for the Dongkeng quarry shaft). With the portal the inclined shaft can be drawn from its horizontal run, 1266 m x cos(atan 0.425).
* Resolve the ~100 m Yangjiang residual: an independently surveyed Yangjiang core coordinate, or a JUNO survey document giving the detector position in a stated datum.
* Hall outline (the final-design hall dimensions with an orientation).

## 2. Chooz (facility:chooz, `map:chooz`)

Grade before: partial (three OSM unit footprints; far, near and very-near sites all unlocated). After: partial, now with two derived laboratory positions (far lab, NUCLEUS very-near-site room) and cross-checks on the unit footprints; the near laboratory stays unlocated.

### Inventory

| Entity | Drawn / unlocated | Representation | accuracy_m | Check result |
| --- | --- | --- | ---: | --- |
| Chooz B1, B2 unit footprints (OSM ways 331249625, 331249628) | drawn (existing records) | georeferenced | 8 | B1 to B2 centroid separation 163.3 m vs 160 m (arXiv:1905.10258) and 165 m (arXiv:2009.05515): both pass at 3 % |
| Chooz A (way 331248511) | drawn (existing) | georeferenced | 8 | none |
| site:double-chooz-far-detector (far laboratory in the hill) | drawn: `geometry:chooz-far-laboratory`, level `far-lab` | derived | 200 | none (circular if taken against the baselines it was computed from) |
| site:chooz-very-near-nucleus (NUCLEUS VNS room) | drawn: `geometry:chooz-vns-position` | derived | 40 | none |
| office building hosting the VNS (way 331249709, context) | drawn: `geometry:chooz-vns-host-building` | georeferenced | 10 | distances to B1/B2 centroids 79.8 m / 99.5 m vs 72 m / 102 m (15 % tolerance): pass |
| site:double-chooz-near-detector | unlocated | n/a | n/a | n/a |

### How the far laboratory was placed (derived, accuracy 200 m)

* Inputs: Double Chooz TDR https://arxiv.org/pdf/hep-ex/0606025 Sec. 2.1: "The far detector is located at a distance of 1114.6 ± 0.1 m from RE, and at 997.9 ± 0.1 m from RW" (1115 m / 998 m in https://arxiv.org/pdf/2009.05515 Sec. 2); the two OSM unit centroids (163.3 m apart).
* Which core is nearer: the TDR labels cores RE/RW (east/west) but the OSM east unit is B2 and the TDR's own Fig. 2/3 and its "close to the old Chooz A" caption are figure-based. Decision: the nearer core is B2, because Double Chooz PRD 86, 052008 (https://arxiv.org/pdf/1207.6632) Table V predicts 3422.4 far-detector events from B2 against 2910.9 from B1 with both reactors on (equal nominal power, flux ~ 1/L²; the distance ratio would give 1.25, the table 1.18). This contradicts reading the TDR's RW as the geographic west unit B1 (see conflicts).
* Mirror choice: the two circles meet at (4.7983695 E, 50.0975524 N) and (4.8026622 E, 50.0845921 N). IGN RGE ALTI elevations (Géoplateforme altimetry API, queried 2026-10-25): plant ground 114.7 m; northern solution 138.1 m (23 m rise, cannot give the ~300 m.w.e. ≈ 107 m of rock the TDR quotes), southern solution 239.4 m on a hill. The southern solution is also 209 m from the OSM "Chooz A" building (TDR Fig. 3 caption: hall "located close the old Chooz A underground power plant").
* Sensitivity (why accuracy_m is 200): circle centres 163 m apart, radii ~1 km: 5 m of error in the core separation moves the point ~25 m, a 20-30 m perpendicular offset of one core from its footprint centroid rotates the pair and moves it ~100-170 m.
* Not used: any bearing from a figure; imagery.

### How the VNS was placed (derived, accuracy 40 m)

NUCLEUS (https://arxiv.org/pdf/1905.10258 Sec. 2.1): "The baseline of the VNS to the two reactor cores is 72 m to B-1, and 102 m to B-2 respectively"; the room is in "the basement of a five-story office building" between the units. Circle intersection about the B1 and B2 centroids: a thin lens (two solutions 59 m apart). The southern solution lies inside OSM way 331249709 (8.9 m from its centroid); the northern is in no building (66 m from the nearest). The opposite assignment (72 m to B2) would put the solutions 20-30 m from the building's centroid distances; the adopted one agrees within 8 m. The building is identified by position only; no source outlines it.

### Source conflicts

1. Unit separation: 140 m (TDR 2006 map caption), 160 m (NUCLEUS), 165 m (Double Chooz 2021), 163.3 m (OSM centroids). The 140 m value is not used (16 % off).
2. Far baselines assigned to cores: TDR RW 997.9 m vs the Table V neutrino-yield ratio (B2, the east unit, is nearer). Resolved in favour of the measured yields; the TDR's RE/RW naming may refer to the figure's orientation. Not independently verified: the far-lab position would move ~1.6 km (to the south-west mirror pair at 4.7820 E, 50.0818 N, 214 m a.s.l.) if the TDR labels were geographic and Table V mislabelled.
3. Near-lab baselines: 290.7/260.3 m (TDR 2006 preliminary, "good estimates within 30%") vs 469/355 m (arXiv:2009.05515, built lab) vs ~400 m average (several papers).
4. Reactor building outline: the OSM units are whole nuclear-island footprints (~15 000 m², ~228 m span), so the centroids are only proxies for the core axes.

### Near-laboratory candidates (not drawn; backlog)

With 355 m to B1 and 469 m to B2 (pairing implied by the iso-flux design, the farther core of the far lab being also the farther core of the near lab): 4.7932676 E 50.0927424 N (132.2 m a.s.l.) and 4.7949525 E 50.0876553 N (107.9 m). With the opposite pairing: 4.7853808 E 50.0916671 N (114.8 m) and 4.7870657 E 50.0865800 N (105.7 m). None sits under a clear hill; nothing in the fetched sources selects one.

### Site coordinate corrections (for the integrator)

* `site:double-chooz-far-detector`: current 50.09, 4.78944, campus, precision 2000 m (Wikipedia). Proposed: lat 50.0845921, lon 4.8026622, kind campus, precision_m 200, confidence approximate (derived), sources `src:geo-chooz-dc-tdr-2006`, `src:double-chooz-2012-evidence`, `src:geo-chooz-osm-extract-2026-10`, `src:geo-chooz-ign-alti-api`; locator `geometry:chooz-far-laboratory`.
* `site:chooz-very-near-nucleus`: current 50.09, 4.78944 (Wikipedia, precision 300 m). Proposed: lat 50.0893716, lon 4.7900335, precision_m 40, derived, sources `src:geo-chooz-nucleus-2019`, `src:geo-chooz-osm-extract-2026-10`; locator `geometry:chooz-vns-position`.
* `site:double-chooz-near-detector`: unchanged (unlocated).

### Backlog

* The EDF CNPE de Chooz site plan behind NUCLEUS Fig. 2 (marks near and far sites) or any civil plan with a scale; an IGN/OSM feature for the far-lab entrance (the "Marinière" gallery of the TDR) would replace the derived far-lab point and settle conflict 2.
* Reactor-building (containment) centres for B1/B2 instead of whole-unit centroids.
* Near laboratory: see candidates above.

## 3. Brokdorf (`map:brokdorf-nuclear-power-plant`) and Leibstadt (`map:leibstadt-nuclear-power-plant`)

Grade before: partial / partial. After: partial / partial, with one wrong building identification corrected (Leibstadt), one official-dimension check added (Brokdorf), accuracy of the Brokdorf detector point widened to the honest value, and context buildings added. Neither facility has an accelerator or beamline; both stay "partial" because no source publishes the reactor-core or reactor-building outline.

### Inventory

| Entity | Map | Drawn / unlocated | Representation | accuracy_m | Check result |
| --- | --- | --- | --- | ---: | --- |
| site:brokdorf-nuclear-power-plant-campus (reactor-building complex, OSM way 87723028 "Reaktorgebäude") | Brokdorf | drawn (existing `geometry:brokdorf-core`) | georeferenced | 15 | none (no official outline) |
| detector:conus-hpge-array (CONUS, 17.1 m from the core) | Brokdorf | drawn (existing point, accuracy widened 20 to 40 m) | derived | 40 | none |
| on-site interim fuel store (OSM way 87722984) | Brokdorf | drawn (new `geometry:brokdorf-fuel-store`) | georeferenced | 8 | perimeter 250.3 m vs 240 m = 2 x (93 + 27): +4.3 %, pass at 6 % |
| Maschinenhaus / turbine hall (way 87722992), context | Brokdorf | drawn (new) | georeferenced | 8 | none |
| site:leibstadt-nuclear-power-plant-campus (reactor building, OSM way 608881797, dome) | Leibstadt | drawn (existing id `geometry:leibstadt-core`, content replaced) | georeferenced | 10 | none |
| detector:conus-hpge-array (CONUS+, 20.7 m from the core, 12.45 m from the axis) | Leibstadt | drawn (existing point moved ~190 m, accuracy 35 to 30 m) | derived | 30 | none |
| main building complex (way 31487680), context | Leibstadt | drawn (new) | georeferenced | 10 | none |

### What changed and why

* Leibstadt reactor building. The earlier record drew OSM way 567961020 (a 1319 m² building) because it was the largest building nearest the plant's bus-stop node, and said so. The OSM data of 2026-10-25 contain a dome-roofed `building:part` (way 608881797, 1719 m², circular part radius 23.0 m, residual <= 1.4 m) whose polygon contains the plant's `power=generator` node (BWR-1, 1220 MW, node 257712288) 7 m from its centroid. That is the reactor building; the old building is 190 m SSW of it and is no longer drawn. Both CONUS+ and the map centre followed. Identification is by tags, not by name, so confidence stays `approximate`.
* Leibstadt CONUS+ point = centre of the circle fitted to the dome (2.1 m from the polygon centroid), taken as the reactor axis; the detector is within 12.45 m of the axis (arXiv:2407.11912: "12.45 m horizontal distance from the reactor central axis", azimuth not published); accuracy 30 m.
* Brokdorf. The "Reaktorgebäude" polygon is the whole reactor-building complex (130 m span, 9227 m²), not the containment cylinder. A circle fitted to its 13 arc vertices has radius 40.2 m (residual <= 2.7 m) and is centred 20.7 m SSW of the polygon centroid (9.3457897 E, 53.8505931 N); whether that arc is concentric with the core is not stated, so the CONUS point keeps the centroid and its accuracy is raised from 20 m to 40 m (17.1 m published offset + up to ~21 m centroid-to-axis).
* Brokdorf interim fuel store: BASE's "Allgemeine Vorprüfung zur Feststellung der UVP-Pflicht" for SZL Brokdorf (https://www.uvp-portal.de/sites/default/files/2023-12/UVP-Vorpr%C3%BCfung%20SZL%20KBR%20R%C3%BCckf%C3%BChrung%20Abschluss%20Vorpr%C3%BCfung%20Stand%2027.11.2023%20zur%20Ver%C3%B6ffentlichung_Barrierefrei.pdf, Sec. 3): "Das Lagergebäude mit Empfangsbereich und Lagerhalle ist ca. 93 m lang, 27 m breit und 24 m hoch (inklusive Aufbauten)." The OSM outline is 93.8 m x 31.8 m (area 2980 m² vs 2511 m² for 93 x 27, so it includes the annex); only the perimeter is used as a check, at 6 %.

### Source conflicts and failed leads

* BGZ site flyer gives the store as 93 m x 27 m x 23 m, the BASE document 24 m high including superstructures: height is not drawn, so no impact.
* No official reactor-building diameter was found for either plant: the Brokdorf decommissioning UVP annex (schleswig-holstein.de `uvpBericht_TBH_Anhang_V.pdf`, 21 MB) and the KKL construction reportage (bewehrungstechnik.ch) contain none; further web searches were not possible (the session's search budget was exhausted). The CONUS and CONUS+ papers give detector offsets only.
* Overpass: primary mirror returned 502/504 repeatedly; the Leibstadt "all features" extract came from lz4.overpass-api.de.

### Site coordinate corrections (for the integrator)

* `site:leibstadt-nuclear-power-plant-campus`: current 47.60306, 8.18472 (Wikipedia, campus, precision 200 m) is 221 m from the reactor building, outside its own precision. Proposed: lat 47.601617, lon 8.182700, kind campus, precision_m 100, approximate, source `src:geo-leibstadt-osm-extract-2026-10`, locator OSM way 608881797 (dome-roofed building part).
* `site:brokdorf-nuclear-power-plant-campus`: 53.85083, 9.34472 is 74 m from the reactor-building polygon centroid: consistent with its 200 m precision, no change.

### Backlog

* An official reactor-building (containment) diameter and an outline or core coordinate for Brokdorf and Leibstadt, to replace OSM complex polygons and the fitted axes.
* The azimuth of the detector offsets (CONUS 17.1 m, CONUS+ 12.45 m) from the CONUS papers' figures, which would turn the two points into positions good to a few metres.
