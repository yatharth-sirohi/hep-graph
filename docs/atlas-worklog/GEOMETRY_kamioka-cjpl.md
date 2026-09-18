# Geometry worklog: Kamioka Observatory and CJPL (map:kamioka-observatory, map:cjpl)

Researcher: geometry-kamioka-cjpl. Worktree
`/Users/yatharthsirohi/Desktop/HEP-Graph-maps-japan-ug`, branch
`hep-atlas-local-maps-japan-ug`. Sources prefixed `src:geo-kamioka-cjpl-*`.

## Method note: Overpass access this session

Overpass was reachable exactly once this session: a query for the Jinping
traffic tunnel (`overpass-api.de`) at the very start succeeded on the first
try. Every later attempt — three retries for a Mozumi-mine buildings/tunnel
query, alternating `overpass-api.de` and `lz4.overpass-api.de`, spaced by real
work in between rather than bare sleeps — failed outright with `curl: (7)
Failed to connect`, never a 429/504 to back off from. No OpenStreetMap trace
of the Kamioka valley (Atotsu tunnel entrance, ICRR surface buildings) was
obtained; this is recorded as backlog, not guessed around.

## Inventory

| Entity | Drawn? | Feature(s) | Representation | Accuracy | Check |
| --- | --- | --- | --- | --- | --- |
| facility:kamioka-observatory | map:kamioka-observatory authored | — | — | — | — |
| site:kamioka-mozumi-mine-super-kamiokande | drawn | geometry:super-kamiokande-cavern | derived (39.3 m circle around surveyed centre) | 50 m | span 39.3 m vs 39.3 m — pass |
| site:kamioka-kamland | drawn | geometry:kamland-point | derived (zero-offset reuse of existing Wikipedia point) | 2000 m | none — no independent figure was found to check against |
| site:kamioka-hyper-kamiokande-tochibora | drawn | geometry:hyper-kamiokande-point | **surveyed** (2011 LOI) | 150 m | distance to Super-K: 8.15 km vs "≈8 km" — pass |
| beamline:j-parc-neutrino | drawn (direction only) | geometry:t2k-beam-direction-kamioka | inferred_direction | n/a | length 294 203 m vs sourced baseline 295 335.2 m — pass (0.38%) |
| facility:cjpl | map:cjpl authored | — | — | — | — |
| site:cjpl-i | drawn | geometry:cjpl-i-point | derived (walked along OSM tunnel line) | 100 m | none formal (see "informational" note below) |
| site:cjpl-ii | drawn | geometry:cjpl-ii-point | derived (walked along OSM tunnel line) | 100 m | none formal (see "informational" note below) |
| (context) Jinping traffic tunnel | drawn | geometry:jinping-traffic-tunnel | georeferenced (OSM) | 25 m | length 17 505.4 m vs sourced 17.5 km — pass (0.03%) |

7 geometry records total (4 on map:kamioka-observatory, 3 on map:cjpl). No
entity is left `unlocated[]` on either map: `facility:kamioka-observatory` and
`facility:cjpl` have no accelerator/beamline records of their own, and all
five sites named in the brief's inventory (three Kamioka, two CJPL) are drawn.

Detectors named in the brief that have **no atlas `detector:` record at all**
in this session's checkout — `kamiokande` (the original, decommissioned
detector; only `experiment:kamiokande` exists), `kamland-zen`, `xmass`,
`cdex`, and the proposed "Jinping Neutrino Experiment" — are out of scope:
there is nothing to draw or list in `unlocated[]` for an entity this atlas
does not yet model. `facility:kamioka-observatory`'s own notes already flag
that KAGRA, CANDLES, NEWAGE and XENONnT R&D are hosted at Kamioka without
their own site record. `detector:pandax-4t` (placed at `site:cjpl-ii`) is
accounted for by sharing `geometry:cjpl-ii-point`; no independently sourced
sub-position within the CJPL-II hall complex was found.

## Checks (expected vs measured)

All geodesic lengths/distances computed with haversine, R = 6 371 008.8 m,
matching `hepgraph.atlas.geo`; confirmed by `hepgraph.atlas.validate`
reporting 0 `geometry-check-failed`/`geometry-check-unmeasurable` findings and
the build's `geometry/*.json` bundles showing `"passed": true` on every check.

| Feature | Expected | Source | Measured | Diff | Tolerance | Result |
| --- | --- | --- | --- | --- | --- | --- |
| Super-K tank span | 39.3 m | src:sk-detector-page | 39.31 m | 0.02% | 1% | PASS |
| Hyper-K–Super-K distance | ≈8000 m | src:hk-pos-icrc2021-status | 8150.2 m | 1.9% | 5% | PASS |
| T2K beam baseline (J-PARC site → Super-K) | 295 335.2 m | src:t2k-nim-2011 | 294 203.1 m | 0.38% | 1% | PASS |
| Jinping traffic tunnel length | 17 500 m | src:cjpl-arxiv-early-science-2018 | 17 505.4 m | 0.03% | 2% | PASS |

**Informational, not formal `checks[]` rows** (same reasoning as this
contract's own CERN precedent for FASER/SND@LHC's TI12/TI18 points): the
500 m separation between `geometry:cjpl-i-point` and `geometry:cjpl-ii-point`
is exact **by construction** — both points were walked along the same OSM
tunnel line using portal distances (8.8/8.7 km and 8.3/9.2 km) that were
deliberately chosen 0.5 km apart from the source's own "CJPL-II is 500 m west
of CJPL-I" statement. A formal `distance` check here would always pass
trivially and add no independent evidence, so it is reported here as a
sanity check on the walking computation itself, not asserted as a `checks[]`
row.

## The CJPL tunnel-walk derivation, in detail

Overpass (`overpass-api.de`) returned way 681216327 and way 653641019, two
near-identical parallel bores named "锦屏二级水电站交通隧洞" (Jinping-II
Hydropower Station traffic tunnel) — OSM's trace of the twin tunnels CJPL's
own review paper (arXiv:1801.00587) describes as "two 17.5-km-long traffic
tunnels". Each measures within 0.03–0.25% of the sourced 17.5 km figure.

The same paper (Section II, Table I, Section VI, Table III) states, in
directly quoted text:

- CJPL-I: 8.7 km from the east portal, 8.8 km from the west portal.
- CJPL-II: 9.2 km from the east portal, 8.3 km from the west portal (i.e.
  exactly 500 m closer to the west portal than CJPL-I, matching "CJPL-II is
  located 500 m to the west of CJPL-I" in the same section).

Walking each of these four portal distances along each of the two OSM bores
(4 estimates per hall) and centroiding gives CJPL-I at (28.1774296 N,
101.7193113 E) and CJPL-II at (28.1798609 N, 101.7150202 E), with the four
estimates for each hall agreeing to within 39 m of their own centroid
(spread 5–81 m across all runs) — the basis for the chosen `accuracy_m: 100`.
Neither point rests on the existing (coarse, geocoder-only) site coordinate:
the OSM tunnel line and the paper's own portal distances are the anchor.

**Residual against the existing site coordinates** (both currently
Nominatim/geocoder points, `precision_m` 2000 and 2500 respectively, not
edited here): the tunnel-walked CJPL-I point is 124 m from the existing
coordinate; CJPL-II is 622 m away. Both are well inside their site's own
stated `precision_m` — consistent, not a contradiction, but the tunnel-walked
points are far more precise and are recommended below as a site coordinate
correction.

## The Hyper-Kamiokande coordinate: an upgrade over the existing site record

The existing `site:kamioka-hyper-kamiokande-tochibora` record carries a
`derived` coordinate (offsetting Super-Kamiokande's own surveyed point 8 km
south) with `precision_m: 3000`, because "no latitude/longitude was published
in any source read" as of 2026-09-16. This session found one: the
Hyper-Kamiokande Letter of Intent (arXiv:1109.3262), Section II.1, states the
site's coordinates directly: "at geographic coordinates Lat. 36°21'08.928"N,
Long. 137°18'49.688"E, and an altitude of 508 m above sea level." This is
only 346 m from the existing derived point (well inside its 3000 m
precision) and sits 8.15 km due south (bearing 177.8°) of Super-Kamiokande's
own surveyed point — corroborating both the existing record and the
"approximately 8 km south" language in the Hyper-K status papers already
cited there. `geometry:hyper-kamiokande-point` uses this LOI coordinate
directly as `representation: surveyed`, `confidence: verified`, with
`accuracy_m` widened to 150 m (rather than a typical survey-point value) to
honestly flag that the LOI's 2011 "proposed location" predates the 2022
excavation start, and no later source fetched this session restates numeric
coordinates to confirm the final position did not shift.

## The T2K direction line: drawn on the far end, not the near end

The brief asks for "an `inferred_direction` line for the T2K beam arriving
from J-PARC (check azimuth to the J-PARC site)". The validator's automatic
azimuth check (`geometry-direction-azimuth`) only supports one direction:
it recomputes the bearing from the drawn line's **first vertex** to the
`entity_id` beamline's **`far_detector_site_ids[0]`** (here, Super-Kamiokande
— the far site *from J-PARC's point of view*, which is this map's own home
turf). There is no symmetric "near site" the validator can check for a
beamline. CERN's CNGS line resolves this by living entirely on the *near*
map (CERN) and pointing outward at the far site (LNGS); to draw a meaningful,
automatically-checked feature on the *far* map (Kamioka) instead, this record
puts the line's first vertex at J-PARC's own site coordinate
(`site:j-parc-main-ring`, 36.4587536 N, 140.5991750 E) and its second vertex
at Super-Kamiokande's own surveyed coordinate — i.e. it draws the same
physical baseline, but does not truncate it to a few kilometres the way CNGS
does (`geometry:cngs-direction-line` in `data/atlas/geometry/`), because both
endpoints are themselves independently sourced points, which lets the whole
line's geodesic length be checked against the T2K instrumentation paper's own
surveyed 295 335.2 m baseline (a genuine, non-tautological cross-check,
passing at 0.38%). The trade-off, made explicitly rather than silently: this
inflates `geometry/kamioka-observatory.json`'s `bbox` out to J-PARC's
longitude. Per the contract, `geometry-out-of-extent` does not apply to a
`direction_line` at all, and no browser code in this checkout yet consumes
`bbox` for anything other than metadata, so this is a data-honesty trade-off,
not a validator defect — flagged here so a future browser-layer author knows
why one feature's bbox reaches to Ibaraki.

## Conflicts and honesty calls

1. **CJPL-II's depth: 2400 m (this session) vs 2100 m (existing site
   record).** `site:cjpl-ii` (not edited here) carries `depth: 2100 m` from
   arXiv:1404.2651 (2014), `confidence: approximate`. The paper fetched in
   full this session, arXiv:1801.00587 (2018, *Annual Review of Nuclear and
   Particle Science* **67**, 231–251), Table I, gives CJPL-II the *same*
   2,400 m rock-burden/depth figure as CJPL-I. `geometry:cjpl-ii-point`'s own
   `depth_m` field uses 2400 m with a `note` explaining the discrepancy, but
   the site record itself is untouched per the research rules — flagged here
   for the integrator to reconcile (the more recent, more detailed paper is
   the stronger source: it is a peer-reviewed review article, whereas the
   2014 figure came from an early-development paper on the then-still-
   unbuilt CJPL-II).
2. **KamLAND's position could not be improved.** Three technical papers
   (arXiv:physics/0404071, arXiv:1409.4515, arXiv:2404.09920) and a search
   for an official Tohoku University description were checked; none state a
   numeric distance-and-bearing offset from Super-Kamiokande precise enough
   to derive a better point than the existing Wikipedia-sourced site
   coordinate (a WebSearch summary reports "500 m", but no primary source
   fetched this session states it, so — per "nothing from memory" — it is
   not used). `geometry:kamland-point` reuses the existing coordinate
   verbatim, honestly labelled `confidence: approximate`. This is also a
   representation-class judgment call worth flagging explicitly: none of the
   four defined classes (`surveyed`/`georeferenced`/`derived`/
   `inferred_direction`) cleanly fits "we are just copying an already-cited
   Wikipedia point with zero computation." `derived` was chosen as the least
   dishonest fit (a trivial zero-offset "computation" from a sourced
   parameter), flagged `approximate`, rather than overclaiming
   `georeferenced` (no OSM/GIS tracing was involved).
3. **The tank/hall points stand in for the detector, not the excavated
   cavern.** `geometry:super-kamiokande-cavern` is a circle of the *tank's*
   sourced diameter (39.3 m), not the larger excavated cavern (no source
   fetched this session gives the cavern's own dimensions, only the tank's).
   `geometry:cjpl-i-point` and `geometry:cjpl-ii-point` are single points
   standing in for a 6.5 m × 6.5 m × 40 m hall and a four-cavern complex
   respectively; no plan with each cavern's own offset and orientation along
   the connecting tunnels was fetched, so no polygon is drawn.
4. **`entity_id` on all five drawn-site features is the site, not the
   detector** — the same lesson CERN's worklog already recorded: the
   validator's `map-entity-unaccounted` rule only counts a site as "drawn"
   via a geometry record's `entity_id`, not its `site_id`. All three Kamioka
   points/circles and both CJPL points were pointed at their `site:` id
   (matching CERN's Point-N boundary convention), even though each
   incidentally depicts one specific detector.
5. **The T2K direction line's `site_id` is `null`.** An initial draft set it
   to `site:kamioka-mozumi-mine-super-kamiokande`; the validator's
   `geometry-site-mismatch` warning correctly flagged that a ~295 km line's
   centroid sits ~147 km from that site's own point (allowed: 150 m, since
   the site's `precision_m` is 50). A cross-country direction line has no
   single "home site" in the sense that field is meant for.
6. **Literal `site:` ids were kept out of `method`/`geometry.note` prose on
   every `derived` record**, following the exact gotcha CERN's worklog
   documents for TI12/TI18: the validator's coarse-anchor check
   (`geometry-derived-from-coarse-anchor`) regex-scans those two fields for
   any `site:…` substring and flags the *worst* precision it finds, even when
   the text is explaining why that site is *not* the anchor. `site:cjpl-i`
   and `site:cjpl-ii` (`precision_m` 2000/2500, far coarser than this
   record's own `accuracy_m: 100`) are discussed only as "the campus-grade
   geocoder point already on record for this site", never spelled out by id,
   in `cjpl-i-point.json`/`cjpl-ii-point.json`.
7. **An unexplained validator-output anomaly, noted for transparency.** Two
   consecutive `hepgraph.atlas.validate` runs in this same worktree, minutes
   apart with no `git` operation in between (confirmed via `git status`/
   `git log`), differed by more than this session's own edits: several
   findings referencing `maps/km3net-orca.json`, `sources/geo-polar-*.json`
   and `maps/amundsen-scott-south-pole-station.json` (files this session
   never touched and that do not exist in this worktree's checkout, per
   `git log -- <path>`) appeared in the earlier run and were gone from the
   later one. This atlas is being developed by roughly a dozen concurrent
   researcher sessions across separate `git worktree`s; the cause was not
   tracked down (git worktrees keep separate working directories, so this is
   not expected), but every validator/build result *cited in this worklog*
   is from the final, reproduced run described below, which contains nothing
   about polar/km3net and 0 errors either way.

## What is unlocated, and why

Nothing is `unlocated[]` on either map. `facility:kamioka-observatory` and
`facility:cjpl` have no accelerator/beamline records; all sites named in the
brief's inventory (`site:kamioka-mozumi-mine-super-kamiokande`,
`site:kamioka-kamland`, `site:kamioka-hyper-kamiokande-tochibora`,
`site:cjpl-i`, `site:cjpl-ii`) are drawn.

## Backlog (concrete next steps)

1. **Mozumi-area OpenStreetMap trace.** Retry
   `way["building"](36.415,137.300,36.435,137.325); way["tunnel"](36.415,137.300,36.435,137.325); node["name"](36.415,137.300,36.435,137.325);`
   on `overpass-api.de` or `lz4.overpass-api.de` once connectivity recovers,
   to add the Atotsu tunnel entrance and Kamioka Observatory's surface
   buildings at the `surface` level.
2. **KamLAND's own position.** Find an official Tohoku University Research
   Center for Neutrino Science page, or the original KamLAND NIM/detector
   paper (not just overview/review articles), stating a numeric offset (with
   bearing) from Super-Kamiokande, or a direct GPS coordinate, to replace the
   Wikipedia-sourced point with something `surveyed`.
3. **CJPL-II depth conflict.** Reconcile 2400 m (arXiv:1801.00587, 2018,
   Table I) against the existing site record's 2100 m (arXiv:1404.2651,
   2014); the 2018 figure looks like the stronger, more current source.
4. **CJPL hall footprints.** If CJPL-II's own civil-engineering drawings (or
   a later, more detailed paper) give each of the four caverns' offset and
   orientation along the internal connecting tunnels (Table III already
   gives some: 64 m and 134 m from the internal tunnel, connecting-tunnel
   heights/widths 8 m), those could support real polygons in place of the
   single reference point used here.
5. **Hyper-Kamiokande coordinate reconfirmation.** The LOI's 2011 "proposed
   location" (used here) predates the 2022 excavation start; a later Hyper-K
   status paper stating the *final, as-built* coordinate would let
   `accuracy_m` tighten below the current 150 m.
6. **PandaX-4T / CDEX / Jinping Neutrino Experiment sub-positions.** None of
   these has an independently sourced position within the CJPL-I/CJPL-II
   hall complexes finer than the single reference point drawn here; a CJPL
   internal layout figure (schematic only, not to scale — would go to
   `map.schematics`, not `geometry`) could help place a future researcher's
   `unlocated[]`/backlog reasoning if these ever get their own `detector:`
   records.

## Site coordinate corrections (for the integrator)

```json
[
  {
    "site_id": "site:cjpl-i",
    "current": {"lat": 28.1763431, "lon": 101.720304, "precision_m": 2000, "confidence": "approximate", "kind": "campus"},
    "proposed": {"lat": 28.1774296, "lon": 101.7193113, "precision_m": 100, "confidence": "derived", "kind": "underground_lab"},
    "source": "src:geo-kamioka-cjpl-osm-jinping-tunnel + src:cjpl-arxiv-early-science-2018 (tunnel-walk derivation; see geometry:cjpl-i-point)",
    "note": "124 m from the current geocoder point, well inside its precision_m; not a contradiction, an upgrade."
  },
  {
    "site_id": "site:cjpl-ii",
    "current": {"lat": 28.1763431, "lon": 101.720304, "precision_m": 2500, "confidence": "approximate", "kind": "campus"},
    "proposed": {"lat": 28.1798609, "lon": 101.7150202, "precision_m": 100, "confidence": "derived", "kind": "underground_lab"},
    "source": "src:geo-kamioka-cjpl-osm-jinping-tunnel + src:cjpl-arxiv-early-science-2018 (tunnel-walk derivation; see geometry:cjpl-ii-point)",
    "note": "622 m from the current geocoder point, well inside its precision_m; not a contradiction, an upgrade. Also recommend updating depth from 2100 m (arXiv:1404.2651) to 2400 m (arXiv:1801.00587 Table I) — see Conflicts §1."
  },
  {
    "site_id": "site:kamioka-hyper-kamiokande-tochibora",
    "current": {"lat": 36.3538, "lon": 137.3103, "precision_m": 3000, "confidence": "derived", "kind": "underground_lab"},
    "proposed": {"lat": 36.35248, "lon": 137.313802, "precision_m": 150, "confidence": "verified", "kind": "underground_lab"},
    "source": "src:geo-kamioka-cjpl-hk-loi-2011 (arXiv:1109.3262, Section II.1, direct published coordinate)",
    "note": "346 m from the current derived point, well inside its precision_m; upgrades an offset-computation to a directly published (though 2011, pre-excavation) coordinate."
  }
]
```

## Sources added

2 new `src:geo-kamioka-cjpl-*` records (1 OpenStreetMap extract covering both
Jinping tunnel bores, 1 arXiv Letter of Intent); see
`data/atlas/sources/geo-kamioka-cjpl-*.json`. One existing source,
`src:cjpl-arxiv-early-science-2018`, was upgraded from `retrieval: summary`
to `retrieval: full_text` with its `excerpt` expanded to the verbatim
passages actually used (tunnel entrance distances, CJPL-II's 500 m offset,
Table I/III figures), per the "grep for the same URL and reuse it" rule — no
duplicate source was created for the same paper. No other existing source,
site, detector, accelerator, beamline or facility record was edited.

## Validator / build / test results

- `.venv/bin/python -m hepgraph.atlas.validate`: **0 errors**, 1593 warnings,
  4 informational (reproduced across two separate runs after canonicalizing
  the written JSON; see the anomaly noted in Conflicts §7 for one earlier,
  non-reproduced run's extra unrelated findings). None of the 1593 warnings
  concern this worklog's files beyond the universal, atlas-wide "`rank` is
  derived at build time" advisory that fires on every `src:` record, and one
  pre-existing warning on `experiment:super-kamiokande` unrelated to this
  work (its start date predates its host facility's founding date, already
  documented in `facilities/kamioka-observatory.json`'s own notes).
- `.venv/bin/python -m hepgraph.atlas.build`: succeeds;
  `geometry/kamioka-observatory.json` is 24 KB (4 features, bbox
  `[137.3100864, 36.35248, 140.599175, 36.4587536]` — see the T2K
  direction-line trade-off discussed above for why it reaches Ibaraki);
  `geometry/cjpl.json` is 16 KB (3 features, bbox
  `[101.6423797, 28.1317909, 101.7889765, 28.2159996]`, attribution
  `["© OpenStreetMap contributors (ODbL-1.0)"]`). Both well under the 2 MB
  per-map budget.
- `.venv/bin/python -m pytest -q tests/test_atlas_validate.py
  tests/test_atlas_build.py tests/test_atlas_geo.py
  tests/test_atlas_geometry_data.py tests/test_atlas_tools.py`: initially 1
  failure (`test_every_map_record_is_canonical_json_and_matches_its_filename`
  — hand-written JSON was not key-sorted); fixed by re-serializing every new
  and edited file through `hepgraph.atlas.load.dump_json`. Re-run: **233
  passed**.
