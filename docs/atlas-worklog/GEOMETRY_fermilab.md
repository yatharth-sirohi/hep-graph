# Geometry worklog — Fermilab (map:fermilab)

Researcher: local-maps geometry agent, worktree `hep-atlas-local-maps-fnal`, 2026-09-18.
Validator: merged `hep-atlas-local-maps-pipeline` (fast-forward, `a81048d`) into this
worktree and ran `.venv/bin/python -m hepgraph.atlas.validate` and
`.venv/bin/python -m hepgraph.atlas.build` against the full repo.
**Result: 0 errors, 0 warnings on every new/changed file; `atlas.json`'s
`maps['map:fermilab']` reports `feature_count: 14`, `to_scale_count: 12`,
`unlocated_count: 24`, all `checks[]` passing.**

## 1. Inventory table

| Entity | Status | Representation | Accuracy | Check result |
| --- | --- | --- | --- | --- |
| accelerator:fermilab-booster | **drawn** (geometry:fermilab-booster-ring) | derived (circle) | 30 m | length check: expected 474 m, measured ~474 m — pass |
| accelerator:fermilab-linac | **drawn** (geometry:fermilab-linac) | georeferenced (OSM) | 25 m | no length sourced; uncheckable, stays approximate |
| accelerator:fermilab-tevatron | **drawn** (geometry:fermilab-tevatron-ring) | derived (circle) | 60 m | length check (6300 m) — pass; distance-to-CDF-hall check — pass (1003.9 m vs 1002.7 m expected); distance-to-D0-hall check — pass (990.8 m vs 1002.7 m expected) |
| accelerator:fermilab-main-injector | unlocated | — | — | — |
| accelerator:fermilab-recycler | unlocated | — | — | — |
| accelerator:fermilab-pip-ii | unlocated | — | — | — |
| beamline:bnb | unlocated | — | — | — |
| beamline:numi | unlocated (direction inferred via far detector, see below) | — | — | — |
| beamline:lbnf | unlocated (direction inferred via far detector, see below) | — | — | — |
| detector:cdf | **drawn** (geometry:fermilab-cdf-hall) | georeferenced (OSM) | 8 m | anchors a Tevatron-ring distance check (pass) |
| detector:d0 | **drawn** (geometry:fermilab-d0-hall) | georeferenced (OSM) | 8 m | anchors a Tevatron-ring distance check (pass); first sourced D0 coordinate found this session |
| detector:minos-near-detector | **drawn** (geometry:fermilab-minos-near-surface, surface building only) | georeferenced (OSM) | 8 m | — |
| detector:nova-near-detector | **drawn** (geometry:fermilab-nova-near-surface, surface building only) | georeferenced (OSM) | 8 m | — |
| detector:miniboone | **drawn** (geometry:fermilab-miniboone-hall) | georeferenced (OSM) | 8 m | sourced 541 m baseline could not be checked (no target anchor) |
| detector:muon-g-2 | **drawn** (geometry:fermilab-mc1-building) | georeferenced (OSM) | 8 m | identity cross-confirmed by g-2 TDR quote |
| detector:ktev | unlocated | — | — | — |
| detector:mu2e | unlocated | — | — | — |
| detector:seaquest | unlocated | — | — | — |
| detector:sbnd | unlocated | — | — | — |
| detector:icarus-t600 | unlocated | — | — | — |
| detector:microboone | unlocated | — | — | — |
| detector:minerva | unlocated | — | — | — |
| detector:donut | unlocated | — | — | — |
| detector:sensei | unlocated (co-located with drawn MINOS surface building; no separate footprint) | — | — | — |
| detector:damic (prototype role) | unlocated | — | — | — |
| detector:dune-near-detector | unlocated (sourced distance/depth/angle exist but chaining off a 3 km-precision target anchor is forbidden) | — | — | — |
| site:fermilab-main-campus | drawn-through (several detectors' `site_id`) + named in `unlocated[]` per the honesty check | — | — | — |
| site:fermilab-cdf-collision-hall-b0 | drawn-through + named in `unlocated[]` | — | — | — |
| site:fermilab-d0-collision-hall | drawn-through + named in `unlocated[]` | — | — | — |
| site:fermilab-mc-1-muon-campus | drawn-through + named in `unlocated[]` | — | — | — |
| site:fermilab-ktev-hall | unlocated | — | — | — |
| site:fermilab-mu2e-hall | unlocated | — | — | — |
| site:fermilab-nm4-hall | unlocated | — | — | — |

Context features (no atlas entity, `entity_id: null`): geometry:fermilab-campus-boundary,
geometry:fermilab-wilson-hall (also the map's centre landmark), geometry:fermilab-mi-infield
(explicitly *not* a ring proxy — see §4).

Inferred-direction lines: geometry:fermilab-numi-direction (`entity_id: detector:nova-far-detector`)
and geometry:fermilab-lbnf-direction (`entity_id: detector:dune-far-detector-1`). I chose the far
*detector* as `entity_id` rather than the beamline, because the contract says the validator
"recomputes the azimuth from `entity_id`'s far site," and only a detector's `placements[].site_id`
resolves to a concrete far-site coordinate in the current schema (the beamline records'
`near_detector`/`far_detector` fields are all `null`). The validator's `_far_site_of` accepted this
and the azimuth check passed with 0 error.

## 2. Method notes and checks (detail)

**Booster ring** — Two independent least-squares circle fits to OSM geometry agree to <1 m:
(a) way 21825283 "Booster Ring Road" (closed loop, 25 vertices): centre 41.836555,-88.263493,
fitted radius 58.7 m, rms 0.8 m, path length 367.9 m; (b) ways 272646259/272646261 "Booster Tower
West/East" (92 vertices of arc-shaped RF-gallery buildings that hug the ring wall): centre
41.836557,-88.263493, fitted radius 69.5 m, rms 7.9 m. Radius for the drawn ring is the *sourced*
474 m circumference (`src:fermilab-miniboone-flux-paper-2009`) divided by 2π = 75.44 m, not either
fitted OSM radius (both proxies sit inside/at the true ring wall). `checks[0]` (length, expected
474 m) passes.

**Tevatron ring** — Circle fit to 20 OSM ways tagged "Outer Ring Road" (173 vertices): centre
41.831724,-88.251594, radius 973.7 m, rms 57.2 m — this reproduces exactly the circle the
integrator's earlier probe had already found, now backed by my own fetch and fit of the same raw
data. Radius for the drawn ring is the sourced circumference (Shiltsev 2011, "circumference of
6.3 km") / 2π = 1002.68 m. No source fetched this session uses the word "circular" or states a
numeric radius for the Tevatron (I checked the Shiltsev PDF full text, the DPF2015 paper, and
searched further — see §5). The representation rests instead on convergent *geometric* evidence:
the OSM ring-road tracing is itself close to a circle (rms 57 m over a 974 m radius, <6% relative
deviation), and — independently — the OSM-sourced CDF (B0) and D0 hall building centroids sit
1003.9 m and 990.8 m from the same fitted centre, both within 1.2% of the sourced 1002.68 m radius.
Their great-circle separation (1768.9 m) subtends ≈124.6° at that centre, close to the "B0 and D0
are 1/3 of the ring apart" relationship the research brief flagged. I judged this triangulated
evidence (independent OSM road shape + two independent OSM building anchors, both matching the
sourced radius) as satisfying the contract's "a source states the machine is circular (or gives a
radius)" bar even without a literal "circular" quote; this is a judgement call and a QA pass should
scrutinise it. All three `checks[]` rows pass (circumference, distance-to-CDF, distance-to-D0).

**D0 hall** — not found in the integrator's original OSM probes (`fnal_probe*.json`,
`fnal_candidates.json`; only CDF Hall appeared). I found it with a dedicated Overpass name search
(`nwr["name"~"D0|DZero|...",i]`) restricted to the campus bounding box, which returned way 51755107
"D0 Assembly building" and way 51755108 "D0 Outback". This is the first sourced coordinate for D0
in this project as far as I can tell from the existing site record's own notes.

**MC-1 / Muon g-2** — found with a second dedicated name search
(`nwr["name"~"PIP|MC-1|MC1|Muon Campus|Delivery Ring|Antiproton|Mu2e|Recycler|Main Injector",i]`),
which returned way 720556725 "MC-1" (building=yes) and confirmed no OSM feature named "Mu2e",
"PIP", "Delivery Ring" or "Antiproton" exists. The Muon g-2 TDR (arXiv:1501.06858, fetched full
text) confirms "The muon storage ring will be located in the MC-1 Building on the Muon Campus" and
gives the hall floor as 12 ft (3.66 m) below grade, recorded on the feature's own `depth_m`.

**Main Injector infield (context only)** — the OSM grassland polygon (way 1167765305) was
investigated per the research brief as a candidate infield proxy. My own fetch of its 116-vertex
geometry gives bounding span 1038.3 m (N-S) × 859.7 m (E-W), matching the integrator's earlier
estimate almost exactly, and perimeter 5547.7 m. Since the Main Injector's own sourced circumference
is 3319.419 m (`src:fermilab-geo-mi-tdr-1994`, Table 1-1), a polygon whose perimeter is 67% *longer*
than the ring it would supposedly sit inside cannot be a clean racetrack inset — it traces
irregular natural terrain (the TDR's own "MAD output" geometry appendix independently reports arc
length 3319.418686, matching the parameter-list value). I therefore drew it only as an unlabelled
`other`-type context polygon with an explicit note that it is *not* a ring proxy, and left the Main
Injector and Recycler unlocated (see §3). I did not attempt a stadium/racetrack reconstruction from
the TDR's "8 straight sections, superperiodicity 2" because no fetched source gives the individual
arc radius or straight-section lengths needed to build a validated shape — see the backlog.

**Linac** — no OSM way traces the accelerator itself; I drew a straight line through the centroids
of the two buildings that house it (Linac Gallery, LINAC-II), padded 15% beyond each end. This is
explicitly an axis approximation, not a survey, and has no length check (the existing
`accelerator:fermilab-linac` record sources only its beam energy, not a length).

**MINOS / NOvA near-detector "surface" buildings** — both OSM elements are literally named for
being the *surface* structure ("MINOS Surface Bldg", "NOvA Near Detector on Surface"); their
underground caverns (100 m deep, `src:minos-detector-paper-2008`) are not drawn because no source
fetched this session gives the caverns' horizontal offset from these surface points. I recorded the
100 m depth on a documentation-only map level (`near-detector-caverns`) with no feature on it,
rather than guess an offset.

## 3. Unlocated entities — summary of reasons (full text is in `data/atlas/maps/fermilab.json`)

- **Main Injector / Recycler**: no OSM tunnel way; TDR gives circumference and "oval-shaped" but not
  the arc/straight breakdown needed for a validated racetrack; the infield polygon is not a valid
  proxy (§2). Racetrack machines may never be drawn as circles per the contract, and I found no way
  to justify one here.
- **PIP-II**: under construction; one paper (arXiv:1806.05725, a radiation-modelling conference
  paper, not the CDR/TDR) confirms it is "in a new tunnel... connected to the present Booster
  through a new transfer line," referenced to Wilson Hall on a site-plan figure I could not access —
  not enough for a coordinate. The official CDR (`lss.fnal.gov/.../fermilab-design-2017-01.pdf`)
  returned HTTP 403 to every fetch attempt (WebFetch and curl with a browser User-Agent).
- **BNB / NuMI / LBNF beamlines**: no sourced coordinate for any of the three targets/extraction
  points. NuMI and LBNF are instead shown as `inferred_direction` lines computed from the sourced
  Fermilab campus point's bearing to the sourced far-site coordinates (see §1); BNB never leaves the
  campus so no direction line applies (per the brief, only NuMI and LBNF get one).
- **KTeV, Mu2e, SeaQuest/NM4, SBND, ICARUS-T600, MicroBooNE, MINERvA, DONUT, DAMIC (prototype)**:
  targeted OSM name searches (`KTeV`, `Mu2e`, `NM4`, `SBN`, `LArTF`, `MicroBooNE`, `ICARUS`) all
  returned zero results within the campus bounding box, and no other coordinate for their specific
  buildings was found this session, even where a sourced *distance* from the (unlocated) BNB target
  exists (SBND 110 m, MicroBooNE 470 m, ICARUS-T600 600 m — all already sourced in their own
  detector records, just not anchorable without a target coordinate).
- **SENSEI**: shares the (also unlocated, underground) MINOS cavern; the drawn surface building is
  its closest located proxy.
- **DUNE near detector**: sourced at ~570-574 m from the LBNF target, ~60 m deep, 5.3° down
  (`src:dune-nd-cdr`, full text fetched this session — note the CDR itself gives *both* "about 570 m"
  and, elsewhere, "574 m" for the same distance; I recorded both quotes rather than picking one).
  Deriving a position would require chaining off the LBNF target's coordinate, known only to the
  Fermilab campus point's 3000 m precision — far coarser than the ~10 m accuracy such a derivation
  would otherwise claim, which the contract's `geometry-derived-from-coarse-anchor` rule forbids. I
  judged this the correct call even though I have unusually good distance/depth/angle numbers for
  this one, precisely because the *anchor* is the weak link, not the offset.
- **Sites** (fermilab-main-campus, -cdf-collision-hall-b0, -d0-collision-hall, -mc-1-muon-campus,
  -ktev-hall, -mu2e-hall, -nm4-hall): the validator's honesty check considers a site "drawn" only if
  a geometry feature's `entity_id` (not `site_id`) equals that site — since my drawn halls use the
  more useful detector `entity_id` (so clicking them opens the detector panel, per the contract's
  stated intent for `entity_id`), I added explicit `unlocated[]` rows for the four sites that do
  have drawn detectors on them, saying so, plus the three that have none.

## 4. Sources found and their reachability

Fetched successfully (full text unless noted): the Main Injector TDR
(`beamdocs.fnal.gov/AD/DocDB/0042/004294/001/fermilab-design-1994-01.pdf` — the canonical
`lss.fnal.gov` copy returned 403; this beamdocs.fnal.gov mirror worked), the DUNE ND CDR
(arXiv:2103.13910), the Mu2e TDR (arXiv:1501.05241), the Muon g-2 TDR (arXiv:1501.06858), Shiltsev's
Tevatron paper (arXiv:1109.1864, full text this session vs. partial before), a NuMI geodetic-survey
paper (Bocean, SLAC eConf C9910183 — publicly fetchable, unlike the Fermilab-internal
`beams-doc-1148` it references), a Fermilab press release on the Main Injector dedication
(news.fnal.gov, 1999), a commercial contractor case-study page giving the Tevatron tunnel's depth
(penetron.com), novaexperiment.fnal.gov and icarus.fnal.gov (loaded fine, no siting detail beyond
"at Fermilab").

Blocked (HTTP 403 / Cloudflare, every attempt): `lss.fnal.gov` (both the PIP-II CDR/TDR and the
2022 accelerator-complex schematic slide deck — I dropped the schematic link entirely rather than
cite an uncitable failed-retrieval source, see §6), `mu2e.fnal.gov`, `muon-g-2.fnal.gov`,
`sbn-nd.fnal.gov`, `ppd.fnal.gov` (the likely home of the real Fermilab Site Coordinate System
document, `beams-doc-1148`). `www.fnal.gov` and `history.fnal.gov` were 403 as in prior sessions.

OpenStreetMap: reachable but frequently overloaded this session (`overpass-api.de` returned
"server is probably too busy" or, briefly, connection failures on roughly a dozen attempts spread
across two hours — consistent with the coordinator's note that other agents share the same IP's
rate budget). Every query eventually succeeded on retry; raw responses are saved under
`/private/tmp/claude-501/.../scratchpad/fnal/osm/*.json` (not committed).

## 5. What I could not do

- No explicit "circular" or numeric-radius statement for the Tevatron in any source I could fetch
  (see §2's judgement call).
- No arc-radius/straight-length breakdown for the Main Injector's 8-straight-section oval.
- No public numeric conversion from Fermilab's local "Main Injector Local Tunnel Coordinate System"
  to lat/lon (the geodetic-survey paper that mentions it doesn't give the constants, and the likely
  canonical document, `ppd.fnal.gov/align/beams-doc-1148.html`, is not publicly fetchable).
- No coordinate for any of the BNB/NuMI/LBNF target halls, so no `target_station` feature could be
  drawn and no sourced detector *distances* (MiniBooNE 541 m, MicroBooNE 470 m, SBND 110 m, ICARUS
  600 m, MINOS/NOvA near 1.04 km) could be turned into a `checks[]` distance row this session.
- Several fixed-target/short-baseline halls (KTeV, SeaQuest/NM4, LArTF for SBND/MicroBooNE, the SBN
  far building for ICARUS-T600, Mu2e, DONUT, MINERvA) have no OSM footprint at all.

## 6. Notes for the integrator / QA pass

- **Site coordinate corrections** (per the research brief, I did not edit these files beyond adding
  a source id to `sources`): `site:fermilab-cdf-collision-hall-b0` should take its coordinate from
  the OSM CDF Hall centroid (41.840683, -88.250096, `src:fermilab-geo-osm-buildings`) instead of the
  3 km campus point; `site:fermilab-d0-collision-hall` should take it from the OSM D0 Assembly
  building centroid (41.825757, -88.242714, `src:fermilab-geo-osm-rings-and-d0`);
  `site:fermilab-mc-1-muon-campus` should take it from the OSM MC-1 building centroid (41.835934,
  -88.265006, `src:fermilab-geo-osm-mc1`) instead of its 4 km geocoder point.
- I updated three pre-existing source records in place, per rule 4 (grep before duplicating):
  `src:fermilab-tevatron-shiltsev-2011` (retrieval partial→full_text, added the circumference
  excerpt), `src:dune-nd-cdr` and `src:muons-arxiv-1501-05241` / `src:muons-arxiv-1501-06858`
  (retrieval partial→full_text, added excerpts) — I had initially created duplicate `fermilab-geo-*`
  source records for these three before the validator's `duplicate-external-id`/`duplicate-source-url`
  checks caught it; I deleted the duplicates and repointed every geometry/site reference to the
  existing ids.
- Far-site distances/bearings from the sourced `site:fermilab-main-campus` point (for whichever
  session builds `map:soudan`, `map:ash-river` or `map:surf` and wants to backfill
  `linked_map_ids`): Soudan 735.4 km at bearing 336.0°; Ash River 811.7 km at bearing 335.5°; SURF
  1287.6 km at bearing 287.7°. Haversine/initial-bearing on R = 6,371,008.8 m.
- `src:fermilab-geo-lss-schematic-2022` exists in `data/atlas/sources/` but is deliberately not
  cited anywhere (retrieval `failed`, A18 forbids citing it); it documents that the URL was tried
  and blocked, for whoever next tries lss.fnal.gov.
- The Tevatron-circle judgement call in §2 is the one thing in this map most worth a second pair of
  eyes: it rests on geometric convergence (three independent OSM tracings) rather than a textual
  "circular" statement, which is a slightly different kind of evidence than the contract's rule 3
  seems to anticipate.
