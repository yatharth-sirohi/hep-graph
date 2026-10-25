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
