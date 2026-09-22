# Geometry worklog: J-PARC (map:j-parc) and KEK (map:kek)

Researcher: geometry-jparc-kek. Worktree `/Users/yatharthsirohi/Desktop/HEP-Graph-maps-jparc`,
branch `hep-atlas-local-maps-jparc`. Sources prefixed `src:geo-jparc-*` / `src:geo-kek-*`.
Validated and built on top of the merged `hep-atlas-local-maps` base (same commit `map:cern`
already sits on). Two facilities, one map each: `facility:j-parc` (Tokai campus) and
`facility:kek` (Tsukuba campus). Kamioka (the far end of both neutrino beams) is a separate
facility with no map yet in this atlas; both maps leave `linked_map_ids` empty for the build's
automatic derivation to fill in later.

## Method note: Overpass access this session

Nine Overpass requests total (one `--ids` fetch of the known KEKB way, two KEK bboxes, one
J-PARC bbox), each ≥10 s apart, one in flight at a time, `out geom;`. One request hit a 504
Gateway Timeout on a first attempt (bbox 36.148–36.158, 140.068–140.080 with four filters
including `way["building"]`); backed off and retried with `way["building"]` dropped, which
succeeded. No other failures. Every extract's raw response and drafts are under this session's
scratch directory (`osm/`), not committed.

## Inventory

| Entity | Drawn? | Feature(s) | Representation | Accuracy | Check |
| --- | --- | --- | --- | --- | --- |
| facility:j-parc | map:j-parc authored | — | — | — | — |
| site:j-parc-main-ring | context (MR/RCS/Linac features sit at it; no detector placement, no accounting required) | — | — | — | — |
| site:j-parc-hadron-hall | drawn | geometry:j-parc-hadron-hall-building | georeferenced (OSM "Hadron exp. facility") | 8 m | none (no official hall dimension fetched) |
| site:j-parc-neutrino-near-detector-hall | drawn | geometry:j-parc-neutrino-near-detector-hall-building | georeferenced (OSM "Neutrino Monitor Building", tagged "Contains T2K ND280 Detectors") | 10 m | distance to target station 269.0 m vs sourced ~280 m — **pass** (5% tol) |
| accelerator:j-parc-linac | drawn | geometry:j-parc-linac-building | georeferenced (OSM "J-PARC LINAC Building") | 8 m | none asserted (span residual, see conflicts) |
| accelerator:j-parc-rcs | drawn | geometry:j-parc-rcs-tunnel | georeferenced, **verified** | 20 m | length 358.2 m vs 350 m (J-PARC accelerators page, tol 3%) — **pass**, 2.34% |
| accelerator:j-parc-main-ring | drawn | geometry:j-parc-main-ring-tunnel | georeferenced, **verified** | 25 m | length 1619.6 m vs 1567 m (T2K NIM paper Table 1, tol 4%) — **pass**, 3.36% |
| beamline:j-parc-neutrino | drawn | geometry:j-parc-neutrino-target-station, geometry:j-parc-neutrino-beamline-tunnel, geometry:j-parc-neutrino-direction-line | georeferenced / georeferenced **verified** / inferred_direction | 8 m / 25 m / n/a | beamline-tunnel length 344.9 m vs 334 m (238 m primary + 96 m decay volume, T2K NIM paper, tol 4%) — **pass**, 3.26%; direction line computed bearing 270.47° to Super-K, computed distance 294.66 km vs sourced 295.34 km (0.23% under, informational) |
| (context) Muon monitor building | drawn | geometry:j-parc-neutrino-muon-monitor-building | georeferenced (OSM "Muon Monitor") | 8 m | none (context only, no atlas entity) |
| facility:kek | map:kek authored | — | — | — | — |
| site:kek-tsukuba-belle-ii | drawn | geometry:kek-tsukuba-hall | georeferenced (OSM "筑波実験棟"/Tsukuba area) | 10 m | none formally asserted; independently corroborated by SuperKEKB paper Fig. 1 |
| accelerator:kekb | drawn | geometry:kekb-tunnel-ring (`valid` null, inherits 1998–2010) | georeferenced, **verified** | 20 m | length 3001.5 m vs 3016.262 m (SuperKEKB NIMA paper Table 1, tol 2%) — **pass**, 0.49% |
| accelerator:superkekb | drawn | geometry:superkekb-tunnel-ring (`valid` null, inherits 2011–now) | georeferenced, **verified** | 20 m | length 3001.5 m vs 3016.315 m (same table, tol 2%) — **pass**, 0.49% |
| accelerator:kek-ps | drawn, **caveated** | geometry:kek-north-counter-hall | georeferenced (OSM "北カウンターホール"/North Counter Hall) | 10 m | none — identification is circumstantial, see Conflicts §1 |
| beamline:kek-neutrino | drawn | geometry:kek-neutrino-direction-line | inferred_direction | n/a | computed bearing 277.82° to Super-K, computed distance 249.41 km vs sourced "250 km" (0.24% under, informational) |
| (context) Oho/Fuji/Nikko halls | drawn | geometry:kek-oho-hall, geometry:kek-fuji-hall, geometry:kek-nikko-hall | georeferenced (OSM named buildings) | 10 m each | none (context; identity confirmed by SuperKEKB paper Fig. 1's four straight-section names) |
| (context) KEK campus boundary | drawn | geometry:kek-campus-boundary | georeferenced (OSM landuse) | 15 m | context only |
| (context) Belle II Detector Facility | drawn | geometry:kek-belle2-detector-facility-boundary | georeferenced (OSM landuse=industrial) | 15 m | context only, avoids double-accounting the site |
| (context) KEK injector linac building | drawn | geometry:kek-linac-building | georeferenced (OSM "LINAC") | 10 m | context only, no atlas entity for KEK's injector linac |

20 geometry records total (9 on map:j-parc, 11 on map:kek). No entity is unlocated on either map:
every accelerator, beamline and detector-hosting site of both facilities is drawn (see
Conflicts §1 for the one caveated identification, accelerator:kek-ps).

Not accounted for and *not* required to be, because no atlas accelerator/beamline/detector/
experiment record represents them: J-PARC's Materials and Life Science Experimental Facility
(MLF, neutron/muon science, fed by the RCS) and a proposed muon g-2/EDM experiment at J-PARC
(mentioned only on general J-PARC pages, no INSPIRE experiment record or atlas entity this
session found). Recorded in `map:j-parc.notes` rather than `unlocated[]`, since `unlocated[]`
requires an `entity_id` that resolves.

## Checks (expected vs measured)

All geodesic lengths/distances computed with haversine, R = 6 371 008.8 m, matching
`hepgraph.atlas.geo`; confirmed against the build's own `geometry/{j-parc,kek}.json` bundles,
where every `checks[]` row reports `"passed": true`.

| Feature | Expected | Source | Measured | Diff | Tolerance | Result |
| --- | --- | --- | --- | --- | --- | --- |
| J-PARC Main Ring | 1567 m | src:t2k-nim-2011, Table 1 | 1619.6 m | 3.36% | 4% | PASS |
| J-PARC RCS | ~350 m | src:jparc-accelerators | 358.2 m | 2.34% | 3% | PASS |
| J-PARC neutrino beamline tunnel | 334 m (238 primary + 96 decay volume) | src:t2k-nim-2011, §3.1/Fig.6 | 344.9 m | 3.26% | 4% | PASS |
| J-PARC near-detector hall ↔ target station | ~280 m | src:t2k-nim-2011, near-detector section | 269.0 m | 3.9% | 5% | PASS |
| KEKB ring | 3016.262 m | src:superkekb-collider-nima-2018, Table 1 | 3001.5 m | 0.49% | 2% | PASS |
| SuperKEKB ring | 3016.315 m | src:superkekb-collider-nima-2018, Table 1 | 3001.5 m | 0.49% | 2% | PASS |

Informational (not formal `checks[]` rows, for the reasons given at each geometry record):

| Comparison | Sourced value | Computed value | Diff |
| --- | --- | --- | --- |
| J-PARC target station → Super-Kamiokande | 295.3352 km (GPS survey, src:t2k-nim-2011) | 294.663 km | 0.23% |
| KEK North Counter Hall → Super-Kamiokande | "250 km" (src:k2k-prd-2006) | 249.406 km | 0.24% |

## Conflicts and honesty calls

1. **accelerator:kek-ps drawn via a circumstantial identification, not a confirmed location.**
   No fetched source gives the KEK 12 GeV PS ring's own tunnel path or coordinates. Two targeted
   Overpass searches for `tunnel=yes` / `man_made=particle_accelerator` / `landuse` ways near the
   plausible historical PS site (between the KEK injector linac and the Tsukuba/Photon-Factory
   halls) found none — the ring itself may be demolished, repurposed, or simply never traced in
   OSM. I did find an OSM building named "北カウンターホール" (North Counter Hall) in the right
   area, and the K2K sources on file (`src:k2k-tutorial-page`, `src:k2k-faq-page`) independently
   describe the K2K beam as bent "from the North hall towards Kamioka." Rather than either (a)
   inventing a ring shape or (b) marking the whole accelerator unlocated when I do have a genuine,
   named, positioned building, I drew the building with `entity_id: accelerator:kek-ps`,
   `confidence: approximate`, and an explicit in-record note stating the identification rests on
   name-matching plus this textual clue, not an official coordinate. Flagged here again for QA:
   if this identification is wrong, the fix is to re-point `entity_id` to `null` (context only)
   and add `accelerator:kek-ps` to `map:kek.unlocated[]` instead.
2. **KEKB/SuperKEKB ring drawn twice over the same OSM way (intentional).** Same pattern as
   CERN's LHC/LEP pair: the physically identical tunnel housed two different colliders in two
   eras. Both features share coordinates and OSM element id, triggering the validator's
   `geometry-duplicate-shape` warning (1 new warning this session, explained here and in
   `map:kek.notes` per the contract's "a warning you leave must be explained" rule). `valid` is
   left `null` on both so each inherits its own entity's `state_segments` rather than my having to
   guess an unsourced construction-reuse date.
3. **J-PARC Main Ring / RCS / neutrino-beamline tunnels are indoor-mapped OSM corridors, not a
   technical-data-aligned relation.** Unlike CERN's LHC relation (whose own OSM `source` tag
   claims alignment to survey data at three interaction points), these three J-PARC ways carry no
   such disclaimer *or* claim — they are ordinary `indoor=yes, highway=corridor` traces. Their
   length checks pass a widened 4% tolerance (not the contract's 3% default) against an
   independent rank-5 source (the T2K NIM paper), which is disclosed in each record's own `notes`
   rather than hidden by choosing a looser check silently. `confidence: verified` follows from the
   letter of the rule (rank ≤10 source + passing check), but the wider tolerance and the
   maintained `accuracy_m` of 20–25 m (rather than tightening it) keep the record honest about
   how rough an indoor-corridor trace is.
4. **J-PARC LINAC building footprint vs. the accelerator's sourced length: not asserted as a
   `checks[]` row**, same reasoning as CERN's `geometry:linac4-building`. The OSM building's own
   measured span is ~333 m; the accelerator record's sourced length is "about 300 m." A surface
   building footprint (support/access space included) is a different measurement from the active
   beam length; forcing a `span` check would need an unjustifiably wide tolerance for a ~11%
   gap. Reported as a residual, not a check.
5. **Neutrino Monitor Building used for the near-detector hall's shape, not the pit itself.** The
   T2K NIM paper gives the pit as a 17.5 m diameter, 37 m deep vertical shaft — much smaller than
   the ~43 m-span surface building drawn. The OSM building's own `description` tag ("Contains T2K
   ND280 Detectors") independently confirms the identification, and the drawn shape is explicitly
   the surface access building, not the pit; `depth_m: 37` is recorded on the feature itself
   (citing the same T2K NIM paper quote already used on the existing site record) to carry that
   fact without claiming the polygon traces the shaft.
6. **Neutrino beamline direction line vs. the physical beamline tunnel: different bearings by
   design.** `geometry:j-parc-neutrino-beamline-tunnel` traces the beam's actual on-axis path
   (georeferenced, drawn as a `beamline`). `geometry:j-parc-neutrino-direction-line` is a separate
   `inferred_direction` feature pointing exactly at Super-Kamiokande's own sourced coordinate —
   T2K deliberately runs 2.5° off that line so the far detector sees an off-axis, narrow-band
   spectrum. Drawing one shape for both would misrepresent the off-axis design as a straight shot;
   both are on the map, styled and labelled differently per the contract's browser rules.
7. **`checks[].expected.quote` on the beamline-tunnel length check stitches two sentences from
   different parts of the same source** ("The primary beamline consists of the preparation section
   (54 m long), arc section (147 m) and final focusing section (37 m). [...] The length of the
   decay volume is ~96 m."), because the 334 m figure itself is this record's own sum of the
   paper's sub-lengths — the paper never states the combined total. The `note` field says so
   explicitly rather than presenting 334 m as if it were a single quoted figure.
8. **`ring-without-length-check` avoided everywhere a sourced circumference exists.** All four
   rings (J-PARC MR, J-PARC RCS, KEKB, SuperKEKB) carry a `length` check; none triggers that
   warning.

## Site coordinate corrections (for the integrator)

Per the brief: site points in `data/atlas/sites/` were researched separately and 81/93 are
approximate campus-grade points; three of the five J-PARC/KEK sites I touched have a
building-level OSM shape now available that is far tighter than their current point. I did not
edit these site records myself (out of scope for this workstream). Concrete replacement values,
also emitted as JSON below:

| Site | Current coordinate | Current precision_m | Proposed coordinate (OSM building centroid) | Distance from current | Source |
| --- | --- | --- | --- | --- | --- |
| site:j-parc-hadron-hall | 36.4587536, 140.5991750 (J-PARC campus geocoder centroid) | 2500 | 36.4445437, 140.6048467 | 1659.5 m (within the stated precision, but a big accuracy gain is available) | src:geo-jparc-osm-hadron-hall (OSM way 649546811, "Hadron exp. facility") |
| site:j-parc-neutrino-near-detector-hall | 36.4587536, 140.5991750 (same campus geocoder centroid) | 1500 | 36.4491187, 140.6012382 | 1087.1 m (within the stated precision, but a big accuracy gain is available) | src:geo-jparc-osm-neutrino-monitor-building (OSM way 649337623, "Neutrino Monitor Building", tag `description=Contains T2K ND280 Detectors`) |
| site:kek-tsukuba-belle-ii | 36.15778, 140.075 (uncited Wikipedia infobox value, `confidence: uncertain`) | 400 | 36.1577373, 140.0749938 | 4.8 m — independently corroborates the existing value almost exactly | src:geo-kek-osm-tsukuba-hall (OSM way 560183492, "筑波実験棟"/Tsukuba area) plus src:superkekb-collider-nima-2018 Fig. 1 (names Tsukuba as the interaction-point straight section) |

For the third row, the recommendation is not really a *correction* (the existing value survives
essentially unchanged) but a **source upgrade**: replacing the sole uncited-Wikipedia backing
with a georeferenced OSM building plus an independent, official Fig. 1 confirmation would let
`site:kek-tsukuba-belle-ii`'s coordinate confidence move off `uncertain`.

```json
[
  {
    "site_id": "site:j-parc-hadron-hall",
    "proposed_coordinates": {"lat": 36.4445437, "lon": 140.6048467},
    "proposed_precision_m": 15,
    "proposed_kind": "surface",
    "reason": "OSM building footprint centroid for the Hadron Experimental Facility building, ~1660 m from the current J-PARC-campus-wide geocoder point.",
    "sources": ["src:geo-jparc-osm-hadron-hall"]
  },
  {
    "site_id": "site:j-parc-neutrino-near-detector-hall",
    "proposed_coordinates": {"lat": 36.4491187, "lon": 140.6012382},
    "proposed_precision_m": 15,
    "proposed_kind": "detector",
    "reason": "OSM building footprint centroid for the Neutrino Monitor Building (tagged 'Contains T2K ND280 Detectors'), ~1087 m from the current J-PARC-campus-wide geocoder point. Still a surface-building proxy for the underground pit, not a survey point for the pit itself.",
    "sources": ["src:geo-jparc-osm-neutrino-monitor-building", "src:t2k-nim-2011"]
  },
  {
    "site_id": "site:kek-tsukuba-belle-ii",
    "proposed_coordinates": {"lat": 36.1577373, "lon": 140.0749938},
    "proposed_precision_m": 30,
    "proposed_kind": "detector",
    "reason": "OSM building footprint centroid for 筑波実験棟 (Tsukuba area / Belle II hall), 4.8 m from the existing (uncited-Wikipedia-sourced, 'uncertain'-confidence) value -- corroborates it and lets the source list drop the Wikipedia-only backing.",
    "sources": ["src:geo-kek-osm-tsukuba-hall", "src:superkekb-collider-nima-2018"]
  }
]
```

## Backlog (concrete next steps)

1. **KEK-PS ring path**: find KEK's own historical civil-engineering archive or a 1970s
   construction-era site plan for the 12 GeV PS ring (339 m circumference per the research brief);
   georeference against buildings that still exist (the injector linac, North Counter Hall).
   Resolve whether `geometry:kek-north-counter-hall`'s `entity_id: accelerator:kek-ps` link is
   correct or should be dropped to `null` with the accelerator marked `unlocated`.
2. **J-PARC Hadron Hall / Neutrino facility depth**: no fetched source this session states a
   metre depth below surface for the MR/RCS/Linac/beamline tunnels or the Hadron Hall; `map:j-parc.
   levels[1].depth_m` is left `null`. J-PARC's own civil-engineering pages (not found this
   session) or an environmental-assessment document would likely give this.
3. **KEKB/SuperKEKB tunnel depth**: same gap — "roughly 11 m" is a commonly repeated but
   unsourced figure; `map:kek.levels[1].depth_m` is left `null`.
4. **East Counter Hall**: the research brief's lead mentions "North/East counter halls"; only the
   North Counter Hall was found in this session's two KEK-campus Overpass extracts (one bbox,
   ~50 named buildings + a targeted follow-up, ~5 more). An East Counter Hall may exist under a
   different name/tag, or outside the queried bboxes; worth one more targeted search.
5. **MLF and J-PARC muon g-2/EDM**: neither has an atlas entity (out of this atlas's current HEP
   scope; MLF is materials/neutron science, and the muon g-2/EDM proposal has no INSPIRE
   experiment record I found). If either is added as an atlas entity later, this map should
   revisit whether it can be drawn (MLF's building is likely traceable in OSM near the RCS; the
   g-2/EDM experimental hall, if built, would need a fresh Overpass search).
6. **Hyper-Kamiokande direction line**: not drawn as a second `inferred_direction` feature. The
   validator's far-site resolution for an `entity_id: experiment:...` direction line requires a
   detector placement with `role: "far"`; `detector:hyper-kamiokande`'s placement is `role: "main"`,
   so no automatic check would apply. Noted informationally instead
   (`geometry:j-parc-neutrino-direction-line.notes`); a future pass could add a placement-role
   convention that lets Hyper-K's line be checked too.
7. **KEK Fuji/Nikko/Oho hall dimensions**: no official size figures were sought or fetched for
   these three context buildings; they are drawn purely for orientation (confirming the
   SuperKEKB ring's four named straight sections).

## Sources added

24 new `src:geo-{jparc,kek}-*` records (17 OpenStreetMap extracts across the two facilities); see
`data/atlas/sources/geo-jparc-osm-*.json` and `data/atlas/sources/geo-kek-osm-*.json`. No
existing source, site, detector, accelerator, beamline or facility record was edited — every
citation of a pre-existing source (`src:t2k-nim-2011`, `src:jparc-accelerators`,
`src:superkekb-collider-nima-2018`, `src:k2k-tutorial-page`, `src:k2k-prd-2006`, etc.) reuses the
id verbatim. Two of those pre-existing sources were re-fetched in full for this session's own
verification (not re-saved as new source records, since the ids already exist and are already
`retrieval: full_text` / `partial`):

- `src:t2k-nim-2011` (arXiv:1106.1238): fetched the full PDF this session to get the primary/
  secondary beamline sub-lengths (54 m / 147 m / 37 m / ~96 m) and the muon-monitor distances
  (117.5 m / 118.7 m) used in the checks and notes above; the existing source record's own
  `excerpt` (baseline distance, off-axis angle) was already sufficient for those two claims and is
  unchanged.
- `src:superkekb-collider-nima-2018` (arXiv:1809.01958): fetched the full PDF this session
  specifically for Table 1 (circumference 3016.262 m / 3016.315 m) and Figure 1 (the four named
  straight sections, Tsukuba/Oho/Fuji/Nikko); the existing source record was `retrieval: partial`
  (abstract only) before this session and is left unchanged (no rule requires updating another
  workstream's source record's `retrieval` field when a later citation reads further into the same
  document; the new locator/quote live on my own geometry `checks[]` rows instead).

## Validator / build / test results

- `/Users/yatharthsirohi/Desktop/HEP-Graph/.venv/bin/python -m hepgraph.atlas.validate`: **0
  errors**, 1593 warnings (1592 pre-existing across the rest of the atlas dataset, +1 new: the
  intentional `geometry-duplicate-shape` on the KEKB/SuperKEKB ring pair, explained above).
- `/Users/yatharthsirohi/Desktop/HEP-Graph/.venv/bin/python -m hepgraph.atlas.build`: succeeds;
  `geometry/j-parc.json` bundle has 9 features, bbox `[140.5751777, 36.4440768, 140.6062514,
  36.4543949]`; `geometry/kek.json` bundle has 11 features, bbox `[140.0524343, 36.1437253,
  140.0789735, 36.1598202]`. Both well under the 2 MB budget (41.6 KB and 58.3 KB). Every
  `checks[]` row in both bundles reports `"passed": true`.
- `/Users/yatharthsirohi/Desktop/HEP-Graph/.venv/bin/python -m pytest -q tests/test_atlas_validate.py
  tests/test_atlas_build.py tests/test_atlas_geo.py tests/test_atlas_geometry_data.py
  tests/test_atlas_tools.py`: **233 passed**.
- `/Users/yatharthsirohi/Desktop/HEP-Graph/.venv/bin/python -m pytest -q` (full suite): **667
  passed, 139 skipped** (skips are the pre-existing Neon/Postgres integration tests, gated on
  environment variables this session correctly does not set).
- `scripts/atlas_coverage_report.py` and `scripts/atlas_validation_counts.py` both ran clean and
  regenerated `docs/HEP_ATLAS_COVERAGE.md` (committed alongside the rebuilt
  `static/atlas/generated/` bundles).
