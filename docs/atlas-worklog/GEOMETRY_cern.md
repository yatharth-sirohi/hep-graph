# Geometry worklog: CERN (map:cern)

Researcher: geometry-cern. Worktree `/Users/yatharthsirohi/Desktop/HEP-Graph-maps-cern`,
branch `hep-atlas-local-maps-cern`. Sources prefixed `src:geo-cern-*`. Validated
after merging `hep-atlas-local-maps-pipeline` (the geometry validator/build
branch off the same base commit as this worktree).

## Method note: Overpass access this session

Overpass (`overpass-api.de`, `lz4.overpass-api.de`) was under heavy load from
concurrent HEP Atlas research sessions for most of this task: repeated
`rate_limited` and `timeout` runtime errors, and for one stretch outright
connection refusals (`curl: (7) Failed to connect ... port 443`) even to
`/api/status`. I paced retries (20-70 s backoffs, small bboxes, one query in
flight at a time) and worked on record-writing and web sources while waiting.
Every extract used below succeeded eventually; several secondary queries
(Meyrin boundary, Linac2, TI12/TI18 named search, UA1/UA2, CAST building, ISR
trace) returned zero elements even after retries — recorded as backlog below,
not guessed around.

## Inventory

| Entity | Drawn? | Feature(s) | Representation | Accuracy | Check |
| --- | --- | --- | --- | --- | --- |
| facility:cern | map:cern authored | — | — | — | — |
| site:cern-meyrin | drawn | geometry:meyrin-site-marker | georeferenced (reused existing Nominatim point) | 500 m | none (visual marker only) |
| site:cern-point-1-atlas | drawn | geometry:point1-atlas-boundary | georeferenced (OSM "CERN - Point 1 (ATLAS)") | 90 m | centroid residual 79.7 m vs site coord |
| site:cern-point-2-alice | drawn | geometry:point2-alice-boundary | georeferenced (OSM "CERN - Point 2 (Alice)") | 80 m | centroid residual 67.8 m |
| site:cern-point-5-cms | drawn | geometry:point5-cms-boundary + geometry:point5-cms-cavern | georeferenced / **surveyed** | 50 m / 30 m | boundary residual 40.5 m; cavern is the CMS paper's own point (verified) |
| site:cern-point-8-lhcb | drawn | geometry:point8-lhcb-boundary | georeferenced (OSM "CERN - Point 8 (LHCB)") | 45 m | centroid residual 35.8 m |
| site:cern-lep-point-2-l3 | drawn | geometry:point2-l3-boundary (LEP era only, `valid` 1989-07-14..2000-11-02) | georeferenced (same OSM polygon as Point 2/ALICE) | 80 m | same residual as above |
| site:cern-lep-point-4-aleph | drawn | geometry:point4-aleph-boundary (`valid` 1989-07-14..2000-11-02) | georeferenced (OSM "CERN - Point 4") | 65 m | centroid residual 55.7 m |
| site:cern-lep-point-8-delphi | drawn | geometry:point8-delphi-boundary (`valid` 1989-07-14..2000-11-02) | georeferenced (same OSM polygon as Point 8/LHCb) | 45 m | same residual as above |
| site:cern-sps-lss4-ua2 | **unlocated** | — | — | — | — |
| site:cern-sps-lss5-ua1 | **unlocated** | — | — | — | — |
| site:cern-ti12-faser | drawn | geometry:ti12-faser-point | **derived** (480 m walked along the LHC ring from IP1) | 60 m | straight-line distance from IP1 = 479.9 m vs sourced 480 m |
| site:cern-ti18-snd-lhc | drawn | geometry:ti18-snd-lhc-point | **derived** (480 m walked, opposite direction) | 60 m | straight-line distance from IP1 = 479.9 m vs sourced 480 m |
| site:cern-cast-sr8 | **unlocated** | — | — | — | — |
| site:cern-ecn3-north-area | **unlocated** | — | — | — | — |
| site:cern-neutrino-platform-ehn1 | drawn | geometry:ehn1-building-887 | georeferenced (OSM building "887") | 10 m | none formally asserted (see below) |
| accelerator:lhc | drawn | geometry:lhc-tunnel-ring | georeferenced, **verified** | 20 m | length 26 580 m vs 26 659 m (CERN, tol 2%) — **pass**, 0.30% |
| accelerator:lep | drawn | geometry:lep-tunnel-ring (`valid` 1989-07-14..2000-11-02) | georeferenced, **verified** | 20 m | length 26 580 m vs 27 000 m (CERN, tol 3%) — **pass**, 1.56% |
| accelerator:sps | drawn | geometry:sps-tunnel-ring | georeferenced, kept **approximate** (see conflicts) | 30 m | length 6 913 m vs 7 000 m (CERN "nearly 7 km", tol 3%) — **pass**, 1.24% |
| accelerator:ps | drawn | geometry:ps-tunnel-ring | georeferenced, **verified** | 15 m | length 634 m vs 628 m (CERN, tol 3%) — **pass**, 1.02% |
| accelerator:psb | drawn | geometry:psb-tunnel-ring | georeferenced, kept **approximate** (expected value is my own computation) | 15 m | length 159 m vs 157.08 m (2πr from CERN Courier's r = 25 m, tol 3%) — **pass**, 1.29% |
| accelerator:hl-lhc | **unlocated** | — | shares the LHC ring already drawn; new HL-LHC civil works not sourced | — | — |
| accelerator:isr | **unlocated** | — | no OSM trace, no source with a location | — | — |
| accelerator:linac2 | **unlocated** | — | no OSM trace, no source with a location | — | — |
| accelerator:linac4 | drawn | geometry:linac4-building | georeferenced (OSM building) | 8 m | span check *not* asserted (see conflicts) |
| beamline:cngs | drawn | geometry:cngs-direction-line | **inferred_direction** | n/a | azimuth 122.86° computed from site:cern-meyrin -> site:lngs-hall-c |
| (context) Antiproton Decelerator Hall | drawn | geometry:antiproton-decelerator-hall | georeferenced (OSM building) | 8 m | no atlas accelerator entity exists for AD/ELENA |
| (context) Prévessin site | drawn | geometry:prevessin-site-boundary | georeferenced (OSM "CERN - Site de Prévessin") | 20 m | context only, deliberately not used for ECN3/CAST |

21 geometry records total. 6 entities unlocated (accelerator:hl-lhc,
accelerator:isr, accelerator:linac2, site:cern-sps-lss4-ua2,
site:cern-sps-lss5-ua1, site:cern-cast-sr8, site:cern-ecn3-north-area — that's
7; see `map.unlocated[]` for the exact sourced reason/backlog per row).

## Checks (expected vs measured)

All geodesic lengths computed with haversine, R = 6 371 008.8 m, on the
as-drawn coordinates (same numbers the validator's own `geo.py` recomputed —
confirmed by `hepgraph.atlas.validate` reporting 0 `geometry-check-failed`
findings).

| Feature | Expected | Source | Measured | Diff | Tolerance | Result |
| --- | --- | --- | --- | --- | --- | --- |
| LHC ring | 26 659 m | src:cern-lhc-page, "Circumference 26 659 m" | 26 580.0 m | 0.30% | 2% | PASS |
| LEP ring | 27 000 m | src:cern-lep-page, "27-kilometre circumference" | 26 580.0 m | 1.56% | 3% | PASS |
| SPS ring | 7 000 m | src:cern-sps-page, "nearly 7 kilometres" | 6 913.3 m | 1.24% | 3% | PASS |
| PS ring | 628 m | src:cern-ps-page, "circumference of 628 metres" | 634.4 m | 1.02% | 3% | PASS |
| PSB ring | 157.08 m (my computation, 2πr) | src:geo-cern-courier-psb-hits-40, "a radius of 25 m (1/4 of the PS)" | 159.1 m | 1.29% | 3% | PASS |
| TI12 point | 480 m from IP1 | src:colliders-lhc-faser-inspire-experiment-record | 479.9 m (straight-line) | 0.02% | — (informational; not a `checks[]` row, see below) | consistent |
| TI18 point | 480 m from IP1 | src:colliders-lhc-snd-lhc-detector-arxiv-2022 | 479.9 m (straight-line) | 0.02% | — (informational) | consistent |

The TI12/TI18 distances are reported here rather than as `checks[]` rows
because `checks[].kind` has no "distance from a point along another
feature's line" kind that fits a derived Point (the `distance` kind is
centroid-to-centroid between two *geometry* records, and by construction the
derived point sits within a fraction of a metre of the 480 m target — the
walk function stops as soon as accumulated arc length passes 480 m, so a
formal check would trivially always pass and add no information).

## Residuals: OSM boundary centroid vs. the site's own sourced coordinate

Reported per the brief's instruction to record conflicts between the OSM
cavern-area positions and the already-sourced (mostly OpenStreetMap-Nominatim
-derived) site coordinates. All are well inside the corresponding site
record's own `precision_m`, i.e. no contradiction — just confirmation that
two independent OSM queries (a Nominatim campus search done by an earlier
researcher, and this session's named-polygon search) agree to within ~40-80 m:

| Site | OSM boundary centroid | Site's sourced coordinate | Residual |
| --- | --- | --- | --- |
| site:cern-point-1-atlas | 46.2351068, 6.0538942 | 46.2355606, 6.0546968 (precision_m 500) | 79.7 m |
| site:cern-point-5-cms | 46.3097187, 6.0765792 | 46.3095, 6.077 (precision_m 30, **verified**, CMS paper) | 40.5 m |
| site:cern-point-2-alice | 46.2508919, 6.0205940 | 46.2514448, 6.0202234 (precision_m 300) | 67.8 m |
| site:cern-point-8-lhcb | 46.2417673, 6.0966980 | 46.2417561, 6.0971635 (precision_m 300) | 35.8 m |
| site:cern-lep-point-4-aleph | 46.3040513, 6.0369785 | 46.3041925, 6.0362827 (precision_m 300) | 55.7 m |

**Site coordinate correction for the integrator:** none of these residuals
exceed the recorded `precision_m`, so no correction is needed. Flagging one
useful upgrade opportunity instead: site:cern-point-5-cms's own coordinate
(46.3095, 6.077, from the CMS paper) is corroborated to 40.5 m by an
*independent* OSM polygon — a future pass could cite my
`geometry:point5-cms-boundary`/`point5-cms-cavern` records as a second,
independent confirmation of that site's coordinate in its own `checks`-style
provenance, though the atlas site schema (v0.2) does not currently have a
field for cross-record coordinate corroboration.

## Conflicts and honesty calls

1. **SPS ring kept "approximate" despite a passing check.** OSM way
   66473762's own `source` tag reads: *"A regular circle set as close as
   possible to intersect each surface site on the collider route. Surface
   sites drawn in from Yahoo! aerial imagery."* That is a mapper-fitted
   circle constrained by visible access points, not a walked/surveyed trace
   — unlike the LHC relation, whose own `source` tag says *"Geometry from
   technical data, aligned on IP2, IP5 and IP8"*. Per the research contract
   (§1.2, `representation` honesty), I widened `accuracy_m` to 30 m (the
   "ring-road/fitted-circle" tier) and left `confidence: approximate` even
   though the length check passes and the formal validator rule would allow
   `verified`. The PS and PSB ways carry no such disclaimer tag, so those two
   are `verified`; PSB is nonetheless kept `approximate` for the different
   reason below.

2. **PSB ring's expected circumference is my own computation, not a
   published figure.** No fetched CERN page states the PSB's circumference
   directly (`home.cern`'s PS Booster page, the PS page, and the accelerator-
   complex page were all checked and none give it). CERN Courier's "The PS
   Booster hits 40" states the radius, "a radius of 25 m (1/4 of the PS)" —
   I computed circumference = 2πr = 157.08 m myself and used that as the
   check's `expected` value, with the computation stated in `note`. Kept
   `approximate` rather than `verified` for this reason, even though the
   check passes.

3. **Linac4 building footprint vs. the accelerator's sourced length: not
   asserted as a checks[] row.** The OSM building polygon's own max span is
   ~107 m; the accelerator record's sourced length is 86 m ("Linac4 is 86
   metres long", src:cern-linac4-page). These are different measurements — a
   surface building footprint (which includes support/access space beyond
   the beamline) versus the active beam length — and forcing them into a
   `span` check would either fail outright (24% apart) or need an
   unjustifiably wide tolerance. Reported here as a residual instead of a
   check.

4. **EHN1/Building 887's "~330 m long, 55 m wide" figure was not used as a
   sourced check.** A WebSearch synthesis reported these dimensions, and the
   building-887 identification itself is corroborated by
   site:cern-neutrino-platform-ehn1's own note, but the two CERN pages that
   should carry the primary figure 404'd on fetch this session
   (`be-dep-ea.web.cern.ch/experimental-areas/north-area/ehn1` and
   `home.cern`'s "LS2 Report: Focus on the North area", which redirects to a
   dead page). Per the "nothing from memory" standard, I did not cite an
   unfetched number. The polygon's own measured max span (~296 m) is in the
   right range, noted as an informational residual, not a formal check.

5. **`geometry-duplicate-shape` warnings (3, intentional).** LHC/LEP share
   the exact same OSM ring (they are the same physical tunnel at different
   times — the sensible representation is two entity-linked features over
   the same coordinates, not one feature awkwardly time-sliced). Point 2's
   ALICE/L3 boundary and Point 8's LHCb/DELPHI boundary are the same OSM
   polygon for the same reason: a LEP experiment and its LHC-era successor
   occupy the physically identical fenced enclosure. All three pairs trigger
   the validator's `geometry-duplicate-shape` warning; left in place and
   explained here and in `map.notes` rather than avoided by omission, per
   the contract's "a warning you leave must be explained" rule.

6. **Boundary/point `entity_id` is the *site*, not the detector.** My first
   draft linked e.g. `geometry:point1-atlas-boundary` to `detector:atlas`.
   The validator's `map-entity-unaccounted` rule only counts a site as
   "drawn" when some geometry record's `entity_id` (not `site_id`) equals
   that site — it does not scan `site_id`. Re-pointed all eight Point-N
   boundaries and the two TI-tunnel points to their site ids
   (`site:cern-point-1-atlas` etc.) so that ATLAS/CMS/ALICE/LHCb's own
   detector-hosting sites, and FASER/SND@LHC's TI12/TI18 sites, are properly
   accounted. `geometry:point5-cms-cavern` keeps `entity_id: detector:cms`
   deliberately (it is a second, more specific feature — CMS's own surveyed
   point — layered on top of the site-level boundary, not a duplicate). One
   side effect: these boundary/point features now inherit `site:*`'s own
   timeline (sites have no independent `state_segments` in this schema
   version) rather than the hosted detector's operational hull, so e.g.
   `geometry:point1-atlas-boundary` will show as present in every year
   rather than only since ATLAS existed. This is a minor over-display, not a
   sourcing problem — flagged here for whoever owns the browser's year
   slider.

7. **TI12/TI18 derivation anchor.** FASER and SND@LHC are each sourced as
   "480 m downstream of the ATLAS interaction point" in their respective
   tunnels. site:cern-point-1-atlas's own coordinate is campus-grade
   (precision_m 500) and cannot anchor a 60 m-accuracy derivation (the
   contract's coarse-anchor rule, enforced by the validator as
   `geometry-derived-from-coarse-anchor`). Instead I walked 480 m along
   `geometry:lhc-tunnel-ring` itself (accuracy_m 20, aligned on technical
   data per its own OSM tag) from the ring's own IP1 node — the midpoint of
   LHC relation 9512017's insertion-1 segment. This anchors the derivation on
   the accurate ring, not the coarse site point. (First draft's `method`
   text literally named `site:cern-point-1-atlas` while explaining *why it
   wasn't the anchor* — the validator's coarse-anchor check naively scans
   `method`/`note` text for any `site:` id and flags the worst precision it
   finds, so that explanatory mention alone triggered the error. Reworded to
   describe the campus point without spelling out its id.)

8. **map.levels\[1\].depth_m.display drift.** First draft's display string
   "56–100 m (varies by point)" was flagged by A21 (`display-value-drift`,
   39.3%) because the validator's number-in-display parser reads the
   *first* number it finds ("56") and compares it to the quantity's
   min/max midpoint (78), not the range. Reworded to "≈78 m (56-100 m
   across the instrumented points)" so the leading number matches the
   midpoint.

## What is unlocated, and why (see `map.unlocated[]` for the sourced text)

- **accelerator:isr** — no OpenStreetMap trace (three name-pattern searches
  in the Meyrin bbox, including a final round-2 retry, all returned zero
  elements) and no fetched source gives coordinates.
- **accelerator:hl-lhc** — physically the same ring as accelerator:lhc
  (already drawn); its own new civil works are not located by any source
  fetched this session.
- **accelerator:linac2** — no OpenStreetMap trace (name search for
  "Linac 2"/"LINAC2" returned zero elements) and no fetched CERN page gives
  a location.
- **site:cern-sps-lss4-ua2** / **site:cern-sps-lss5-ua1** — no OpenStreetMap
  trace (name search for "UA1|UA2|LSS4|LSS5" across the SPS-ring bbox
  returned zero elements); the existing site records' own coordinates are
  Meyrin-campus fallbacks with precision_m 3000, too coarse to anchor
  anything.
- **site:cern-cast-sr8** — no OpenStreetMap trace (name search for "CAST"
  near Point 8 returned zero elements); the existing site record already
  documents that no official page gives a coordinate more precise than the
  Point 8 campus point.
- **site:cern-ecn3-north-area** — ECN3 is an underground cavern with no
  surface footprint of its own; only the outer Prévessin fence (drawn as
  context, `geometry:prevessin-site-boundary`) and 77 numbered surface
  buildings with no "ECN3" name were found. Drawing the whole Prévessin
  boundary as ECN3's own shape would misrepresent a small cavern as
  occupying the entire campus, so it stays unlocated instead.

## Backlog (concrete next steps, also in `map.unlocated[].backlog`)

1. ISR: find a 1970s ISR design-report site plan or CERN's historical
   civil-engineering archive; georeference against Meyrin buildings that
   still exist.
2. HL-LHC: locate the new shafts/caverns (e.g. PM18, PM15) via CERN's
   HL-LHC civil-engineering pages once published with coordinates.
3. Linac2: find its building number/plan via a historical-photo or
   civil-engineering page (stood near the current Linac4/PSB area before
   2018-2020 demolition).
4. UA1 (LSS5) / UA2 (LSS4): an SPS civil-engineering drawing, or the
   detector papers' own stated azimuthal position along the SPS ring.
5. CAST: ask CERN's GIS/survey group directly, or find an open-days site
   plan showing the platform's position relative to Point 8.
6. ECN3: CERN's North Area civil-engineering/BE-DEP-EA drawings, or a
   detector-paper survey coordinate from NA62/NA48.
7. Meyrin site boundary: no landuse/fence polygon comparable to Prévessin's
   was found under several name patterns; try Overpass with the site's OSM
   relation/way id directly if it can be found via a different route (e.g.
   Nominatim's own polygon id, which the existing site record's Nominatim
   citation does not currently record).
8. EHN1/Building 887 dimensions: retry `be-dep-ea.web.cern.ch` and the
   `home.cern` North Area LS2 report (both 404'd this session) or find a
   live mirror, to get a citable "330 m long" quote.
9. LHC/LEP tunnel's full-ring depth range: the oft-quoted "45-170 m" (or
   "50-175 m") figure appears on Wikipedia and secondary sites without an
   attributable primary citation; CERN's own civil-engineering pages fetched
   this session state only per-point depths (used instead). Worth another
   pass at `home.cern`'s FAQ/civil-engineering pages once the North Area
   pages are back up, or the LHC Design Report Vol. I.
10. SPS and PS/PSB tunnel depths: no fetched source states either this
    session; `map.levels[2]` and `[3]` are left with `depth_m: null`.

## Sources added

15 new `src:geo-cern-*` records (12 OpenStreetMap extracts, one CERN
Courier article, one CDS schematic-diagram record); see
`data/atlas/sources/geo-cern-*.json`. No existing source, site, detector,
accelerator or beamline record was edited — all citations of pre-existing
sources (e.g. `src:cern-lhc-page`, `src:cms-muon-charge-ratio-paper-2010`,
`src:colliders-lhc-faser-inspire-experiment-record`) reuse the ids verbatim.

## Validator / build / test results

- `.venv/bin/python -m hepgraph.atlas.validate`: **0 errors**, 1592
  warnings (all pre-existing across the rest of the atlas dataset except 3:
  the intentional `geometry-duplicate-shape` warnings on the LHC/LEP ring
  pair and the two LEP/LHC Point-2 and Point-8 boundary pairs, explained
  above).
- `.venv/bin/python -m hepgraph.atlas.build`: succeeds; `geometry/cern.json`
  bundle has 21 features, bbox `[6.0108582, 46.1899106, 6.1451968,
  46.3108673]`, attribution `["© OpenStreetMap contributors (ODbL-1.0)"]`.
- `.venv/bin/python -m pytest -q tests/test_atlas_validate.py
  tests/test_atlas_build.py tests/test_atlas_geo.py
  tests/test_atlas_geometry_data.py tests/test_atlas_tools.py`: **232
  passed**.
