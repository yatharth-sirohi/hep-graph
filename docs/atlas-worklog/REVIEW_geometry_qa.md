# QA / red-team review: HEP Atlas local-map geometry layer

Reviewer: independent QA pass, worktree `/Users/yatharthsirohi/Desktop/HEP-Graph-maps-qa`,
branch `hep-atlas-local-maps-qa` (branched from `hep-atlas-local-maps`, later merged
forward once more to pick up the reactor-neutrino maps and 25 applied site-coordinate
corrections). This reviewer authored none of the data under review; every finding below
was re-derived independently, not copied from the original researchers' own worklogs.

Scope (flagship maps, per the review brief): `map:cern`, `map:fermilab`,
`map:j-parc`, `map:kamioka-observatory`, `map:kek`, `map:desy`,
`map:brookhaven-national-laboratory`, `map:surf`, `map:snolab`,
`map:amundsen-scott-south-pole-station`, `map:km3net-arca`, plus a sample of
three array maps: `map:pierre-auger-observatory`, `map:hess-khomas-highland`,
`map:lhaaso-daocheng`. A full-atlas grep (not limited to these 14 maps) was
also run for the one systemic licensing gap this review found (see SS4), and
one map outside the flagship set (`map:roque-de-los-muchachos-observatory`)
was fixed as a result.

## 1. Method

1. Read the contract (`docs/HEP_ATLAS_GEOMETRY.md`), the coverage set, the
   research brief, and every relevant `docs/atlas-worklog/GEOMETRY_*.md`
   worklog for the facilities in scope.
2. Ran the pipeline gates directly in this worktree throughout:
   `python -m hepgraph.atlas.validate` (0 errors before and after every
   change), `python -m hepgraph.atlas.build` / `--check`, and
   `pytest -q tests/test_atlas_geometry_data.py tests/test_atlas_geo.py
   tests/test_atlas_validate.py tests/test_atlas_build.py`.
3. Did direct, hands-on verification myself wherever a claim was checkable
   without a subagent: recomputed the CNGS azimuth (CERN->LNGS) from scratch
   (haversine/initial-bearing, R=6,371,008.8 m) and matched the record to
   six decimal places; computed vertex-to-centroid radius spread for every
   ring geometry in scope to confirm racetrack/polygonal machines are not
   drawn as idealised circles; read `hepgraph/atlas/build.py` and
   `hepgraph/atlas/validate.py` directly rather than trusting paraphrases of
   validator behaviour; fetched OSM node 4425992583 directly via
   `api.openstreetmap.org` to confirm a subagent's claim before acting on
   it; ran a Python REPL against `hepgraph.atlas.build._Context` to test the
   entity-status-inheritance fix on real data before committing it.
4. Dispatched six independent research agents in parallel (general-purpose,
   full tool access, explicitly told to re-fetch sources/OSM themselves and
   compute their own residuals, not to re-read the original worklog as
   ground truth), one per facility group: CERN; Fermilab; J-PARC+KEK;
   BNL+DESY; the underground/polar cluster (SURF, SNOLAB, Kamioka, South
   Pole, KM3NeT-ARCA); the three sample array maps. Collected each one's
   final per-feature table, defect list and fit-for-production verdict.
5. Cross-checked every P0/P1 claim a subagent made against the actual data
   and, where feasible, an independent fetch of my own, before acting on it
   (see the individual defect entries below for what was independently
   reproduced and by whom).
6. Applied unambiguous, sourced P0/P1 fixes directly (canonicalised via
   `hepgraph.atlas.load.dump_json`, re-validated to 0 errors after each
   batch, committed). Left genuinely ambiguous or policy-level items open,
   listed in SS7.

## 2. Per-map findings

Each row's "independent re-derivation" was performed either by this
reviewer directly or by a dispatched subagent (noted); both fetched sources
fresh rather than trusting the original worklog.

### map:cern

| Feature | Claim | Independent re-derivation | Residual | Verdict |
| --- | --- | --- | --- | --- |
| `geometry:lhc-tunnel-ring` | 26,659 m circumference; OSM relation 9512017 | Subagent fetched `relation/9512017/full.json` directly; coordinates bit-for-bit identical at every sampled index. Length re-confirmed via a *differently-worded* CERN source (LHC Project Report 79 / CDS 316527) than the one already cited | 0.30% | PASS |
| `geometry:lep-tunnel-ring` | Same tunnel; 27 km; valid 1989-07-14 -> 2000-11-02 | Dates re-confirmed via CERN's "The LEP story" / CERN Courier | 1.56% | PASS |
| `geometry:sps-tunnel-ring` | "nearly 7 km"; kept `georeferenced`/`approximate` despite a passing check | Subagent independently computed radius-spread (1.83%, near-uniform vertex spacing) confirming OSM way 66473762's own disclaimer tag ("a regular circle set as close as possible...") is accurate | 1.24% | PASS on the number; **representation-class judgement call reviewed, not changed -- see SS3** |
| `geometry:ps-tunnel-ring` | "628 m" | Re-fetched home.cern PS page; radius-spread 6.34% confirms a genuinely irregular (non-circle-fitted) trace | 1.02% | PASS |
| `geometry:psb-tunnel-ring` | 2*pi*r=157.08 m from a CERN Courier radius quote | Haversine recompute + radius-spread (6.25%, non-uniform) | 1.29% | PASS (Courier quote itself not independently re-fetched this pass -- low risk) |
| Point 1/2/5/8 boundaries (ATLAS/ALICE/CMS/LHCb) + LEP-era L3/ALEPH/DELPHI duplicates | OSM fenced-site polygons; LEP dates 1989-07-14 -> 2000-11-02 | Dates independently re-confirmed; validator run directly shows exactly 3 `geometry-duplicate-shape` findings for CERN, all explained | <=80 m, within tolerance | PASS -- **fixed P2**: 7 of these records were missing `osm.timestamp` despite the extract timestamp being on file in their own cited source; populated (SS5) |
| `geometry:ti12-faser-point`, `geometry:ti18-snd-lhc-point` | FASER/SND@LHC 480 m from IP1, anchored on the LHC ring (20 m), *not* the coarse Point-1 site (500 m) | Subagent independently fetched arXiv:2207.11427 / 2210.02784, re-walked 480 m along a fresh OSM fetch of the ring: bit-exact match to the committed points | 0.0 m | PASS -- the worklog's own self-flagged coarse-anchor risk is refuted, not confirmed |
| `geometry:cngs-direction-line` | Azimuth 122.86 degrees Meyrin->LNGS Hall C | Independently recomputed by this reviewer from scratch: 122.86094876...deg | 0.00 deg | PASS |
| `geometry:meyrin-site-marker` | Reference point, OSM/Nominatim-derived | **Fixed P2**: was `license: null` despite naming OSM relation 27005 in its own method text (see SS4) | n/a | fixed |
| unlocated[] (ISR, HL-LHC, Linac2, LSS4/UA2, LSS5/UA1, CAST/SR8, ECN3) | "No OSM trace found" | Subagent re-ran fresh Overpass searches for several; all still return 0 (one CAST search returned 4 false positives from a bare substring match on "castel", confirming the underlying "no real trace" conclusion but flagging the phrasing) | n/a | PASS |

**Verdict: fit for production.** The flagship LHC/LEP ring and the
FASER/SND@LHC anchor choice -- the two items the original researcher's own
worklog most asked a QA pass to scrutinise -- both hold up under independent
reconstruction from raw OSM data. Two small P2s fixed (osm.timestamp x7,
Meyrin licence).

### map:fermilab

| Feature | Claim | Independent re-derivation | Residual | Verdict |
| --- | --- | --- | --- | --- |
| `geometry:fermilab-tevatron-ring` | `derived` circle, radius from sourced 6.3 km circumference | **Two** independently dispatched subagents both re-fetched OSM "Outer Ring Road" fresh and reproduced the exact circle fit (same centre/radius/vertex count); both independently found secondary sources (Wikipedia: "a circular particle accelerator... 6.28 km circumference ring"; independent descriptions of the same-tunnel Main Ring as "1000 m radius") satisfying rule 3's plain text even though no rank<=10 paper phrases it that way | fit reproduced to <1 m | PASS -- documented in a note, not weakened (SS3) |
| `geometry:fermilab-cdf-hall`, `-d0-hall` | OSM building footprints | Fresh Overpass fetch; own shoelace-centroid recompute vs. independent OSM centre | 0.85 m / 0.93 m | PASS |
| `geometry:fermilab-bnb-target/-beamline`, `-numi-target/-beamline` | `derived`, anchored on named OSM buildings, not a coarse site | Independently confirmed the 541 m / ~1 km baselines via detector papers; `method` text audited to confirm no coarse `site:` anchor is actually used | n/a | PASS |
| `geometry:fermilab-mc1-building` (Muon g-2) | g-2 TDR quote | Independently found the identical quote (arXiv:1501.06858) plus a ResearchGate figure caption | n/a | PASS on identity -- **P0 status bug found and fixed, see SS3** |
| Main Injector / Recycler | Never drawn as a ring (racetrack machine) | Grepped every `fermilab-*.json`: zero records claim `entity_id: accelerator:fermilab-main-injector` | n/a | PASS |
| `detector:seaquest` / `site:fermilab-nm4-hall` unlocated | "No OSM trace... a search for 'NM4' returned no results" | Subagent found, and this reviewer independently re-fetched (`api.openstreetmap.org/api/0.6/node/4425992583.json`), a real OSM node named "SeaQuest" -- the narrow claim was true, the overall impression false | n/a | **P1, fixed: now drawn** (SS3) |

**Verdict: fit for production**, with one P0 (status bug) and one P1 (a
missed OSM node) fixed during this review.

### map:j-parc and map:kek

| Feature | Claim | Independent re-derivation | Residual | Verdict |
| --- | --- | --- | --- | --- |
| `geometry:kekb-tunnel-ring` / `superkekb-tunnel-ring` | Racetrack, not a circle; 3016.262 m / 3016.315 m | Subagent fetched OSM way 138322704 directly: all 53/53 vertices match the committed record exactly; downloaded and read the SuperKEKB PDF's Table 1 directly | 0.49% both | PASS -- radius-spread (10.1%, this reviewer) confirms genuinely non-circular |
| KEKB/SuperKEKB status honesty | `kekb.status: decommissioned` (1999-2010); `superkekb.status: active` | Cross-checked against real history; both correct | n/a | PASS |
| `accelerator:kek-ps` identification (the highest-risk item flagged by the original worklog) | Drawn via `geometry:kek-north-counter-hall` with a circumstantial (name-match) identification | **Already corrected on the merged integration branch** before this review reached it: `entity_id` is `null`, an in-record "Integrator" note explains why, and `accelerator:kek-ps` is in `map:kek.unlocated[]` with a sourced reason. Subagent independently searched for a better PS-ring source and found none either, and explicitly recommends leaving it exactly as now committed | n/a | **confirmed correct, no further action** |
| J-PARC MR/RCS/beamline tunnel lengths, 4% tolerance | 1567 m / ~350 m / 334 m; widened tolerance disclosed, not hidden | Subagent downloaded the T2K NIM PDF directly (not the abstract) and read Table 1/S3.1/Fig.6; independently recomputed all three lengths from raw coordinates, matching the worklog's own figures | 3.36% / 2.34% / 3.26%, all inside the disclosed 4% (MR/beamline) or 3% (RCS) | PASS |
| Neutrino direction line vs. beamline tunnel (2.5 deg off-axis by design) | Two genuinely different bearings | T2K NIM PDF read directly: "The off-axis angle is set at 2.5 deg"; measured 2.504+/-0.004 deg | n/a | PASS |
| `j-parc-neutrino-direction-line.json`, `kek-neutrino-direction-line.json` | `inferred_direction`, no OSM element traced | **Fixed P2**: both carried a stray ODbL license block inconsistent with every sibling `inferred_direction` record in the atlas; cleared (SS5) | n/a | fixed |

**Verdict: both fit for production.** The KEK-PS judgement call this review
was specifically asked to scrutinise turns out to already be correctly
resolved on the branch this worktree merged; confirmed independently, not
just trusted.

### map:brookhaven-national-laboratory and map:desy

| Feature | Claim | Independent re-derivation | Residual | Verdict |
| --- | --- | --- | --- | --- |
| `geometry:bnl-rhic-ring` | Hexagonal (not circular), 3862 m official | Subagent fetched OSM way 50074088 directly: 34 nodes identical to committed record. BNL's own PDF fetched fresh: "2.4 miles". Independent physics literature: "hexagonally shaped... 3834 m" | 0.74% (0.03 m vs. the independent 3834 m figure) | PASS -- radius-spread 5.9% (this reviewer) confirms non-circular |
| `geometry:bnl-ags-ring` | Kept `approximate` (mapper-drawn `place=locality`, not a technical alignment) | Subagent fetched way 289305285 directly, confirmed the tag situation | 2.06% | PASS, judgement call independently endorsed |
| STAR / sPHENIX hall identification (buildings 1006/1006A, 1008/1008A) | Per BNL's own central-campus-map PDF | Subagent independently fetched the same PDF fresh (a different copy than the worklog's cached one) via `pdftotext` and found the identical building-number key | n/a | PASS |
| `geometry:hera-tunnel-ring` | 6336 m, OSM way 24973326 | Subagent fetched DESY's facts page and Wikipedia fresh: "Length: 6336 metres" / "6.3 km", "shut down 30 June 2007" | 0.30% | PASS on the number -- **P0 status bug found and fixed, see SS3** |
| `geometry:petra-iii-tunnel` | Context feature, `entity_id: null` (no `accelerator:petra` exists) | Grepped `data/atlas/accelerators/`: confirmed no petra/doris record | n/a | PASS |

**Verdict: both fit for production**, after the P0 status-bug fix in SS3 --
this is the single most consequential finding of the whole review (see
below): both maps' single most prominent feature (RHIC, HERA) was rendering
as an actively-operating machine in the live build, in direct contradiction
of their own entity records.

### map:surf, map:snolab, map:kamioka-observatory, map:amundsen-scott-south-pole-station, map:km3net-arca

| Feature | Claim | Independent re-derivation | Residual | Verdict |
| --- | --- | --- | --- | --- |
| SURF Davis Campus / LZ depth | 1478 m (4850 ft) | Subagent fetched LZ's and Sanford Lab's own pages fresh: "nearly one mile... 1.5 km", "4850 Level"; 4850 ft x 0.3048 = 1478.3 m, exact unit match | 0 | PASS |
| `site:surf-4850-level-dune-far-detector` | Correctly unlocated, not invented | Grepped every geometry record's `entity_id`/`site_id`: none reference this site on `map:surf` | n/a | PASS |
| `geometry:snolab-cavity` | 22 m diameter, SNO paper's own point | Subagent fetched the SNO NIM paper (arXiv:nucl-ex/9910016) directly via `pdftotext`: exact verbatim match on both the diameter and the coordinate | 0.07% | PASS |
| `geometry:super-kamiokande-cavern` | 39.3 m, GPS-surveyed centre | Subagent fetched a *second*, independent primary paper (Fukuda et al., NIM A 501 (2003) 418-462): exact coordinate match; diameter rounds to "39 m" (0.8% off, informational) | 0 m (coordinate) | PASS |
| `geometry:hyper-kamiokande-point` + entity status | Surveyed 2011 LOI point; not claimed operating today | Detector/experiment records read directly: latest interval `status: construction`, next `planned` (2027-2028) -- correctly not shown as active | n/a | PASS |
| `geometry:t2k-beam-direction-kamioka` | `inferred_direction`, azimuth/length checkable | Subagent independently recomputed bearing (270.2619 deg) and length (294,203.1 m) from the two sourced endpoints; cross-check vs. the T2K NIM baseline passes at 0.38% (the azimuth check is tautological by construction here -- disclosed, not hidden) | 0.38% (length, the real check) | PASS |
| `map:amundsen-scott-south-pole-station` unlocated (IceCube, DeepCore, IceTop, ARA, AMANDA, Upgrade, Gen2) | All unlocated: IceCube's local-grid-to-true-north orientation is unverifiable (docs.icecube.aq 401s) | Subagent reproduced the 401, then found a working, unauthenticated substitute: `github.com/icecube/icetray-public`'s own `coordinates.rst`, stating the grid orientation verbatim -- a concrete backlog unblock, not yet applied (drawing the array is out of this review's scope) | n/a | Honest reporting confirmed; **see SS6 for the fit-for-production caveat** |
| `geometry:km3net-arca-footprint` | R=500 m from the KM3NeT 2.0 LoI's own figure caption | Subagent fetched arXiv:1601.07459 directly: exact verbatim match, including the site coordinate | 0 | PASS |

**Verdict:** SURF, SNOLAB, Kamioka and KM3NeT-ARCA are **fit for
production**. South Pole is **fit for production as an honest
low-detail placeholder** (see SS6) -- correct, not under-effort, but it
draws almost nothing of the facility IceCube is famous for, and a concrete
unblock for the main blocker now exists in the backlog.

### Array maps sample: map:pierre-auger-observatory, map:hess-khomas-highland, map:lhaaso-daocheng

| Feature | Claim | Independent re-derivation | Residual | Verdict |
| --- | --- | --- | --- | --- |
| `geometry:auger-sd1500-array-boundary` | 3160.6 km2 hull vs. "3000 km2" official | Subagent re-downloaded `sdMap.csv` from opendata.auger.org directly, wrote its own inverse-UTM-zone-19S converter from scratch, and recomputed the hull area via the repo's own `geo.py`: 3160.627 km2, matching | +5.35% (tol 8%) | PASS -- the official-page quote itself could not be reproduced live today (P2, citation drift, not the number) |
| `geometry:hess-ct1-4-square` | 480 m perimeter (4x120 m), circularity of the check genuinely disclosed | Subagent re-fetched a *second* official H.E.S.S./MPI page (exact coordinate + "120 m side length" match) and independently rebuilt the square's geodesic geometry from scratch, matching the file's vertices to ~2 mm | 0.001% | PASS |
| `geometry:hess-ct5-point` | `surveyed`/`verified` for a point inferred from "centre of the array" | Subagent flags this as arguably mis-classified (should be `derived`, like the honestly-labelled CT1-4 square); low practical risk | n/a | **P2, open -- see SS7** |
| `geometry:lhaaso-array-point` | 5000 m-accuracy Nominatim point; a tighter LHAASO Science Book coordinate repeatedly attributed but never fetched | Subagent found and fetched (on two independent mirrors) a *different*, peer-reviewed paper giving the identical coordinate to the hundredth of an arcsecond | 3253 m from the old point (inside its own claimed accuracy) | **P1, fixed: coordinate/representation/confidence upgraded (SS3)** |

**Verdict: all three fit for production.** Auger's and H.E.S.S.'s core
claims both survive independent re-derivation from raw data/geodesic
reconstruction; LHAASO's single point is now upgraded from an honest
placeholder to a verified, peer-reviewed coordinate.

## 3. The defect ledger, fixed

### P0 -- fixed

**Decommissioned/shut-down machines rendering as "active" in the live build**
(`hepgraph/atlas/build.py::_feature_segments`, lines ~1256-1283): any
geometry record whose `valid` dict has a non-null `start` and `end: null`
is hard-coded to `status: 'active'` through build day, completely
overriding the linked entity's real `state_segments`/`status`. Several
independent researchers hit this the same way: they set `valid.start` only
to record that a shape's own structural lifetime predates or differs from
its entity's, never intending an "still active" claim. Confirmed **live**
(rendering the wrong status in the actual built bundle on 2026-09-21) for:

- `data/atlas/geometry/lhc-tunnel-ring.json` (`accelerator:lhc.status:
  shutdown` -- LHC is in Long Shutdown 3 -- was rendering `active`)
- `data/atlas/geometry/hera-tunnel-ring.json` (`completed`, shut down
  2007-06-30 -- was rendering `active`)
- `data/atlas/geometry/bnl-rhic-ring.json` (`completed`, final run ended
  2026-02-06 -- was rendering `active`)
- `data/atlas/geometry/fermilab-mc1-building.json` (`detector:muon-g-2`,
  `completed`, final run ended 2023-05 -- was rendering `active`)
- `data/atlas/geometry/fermilab-microboone-hall.json` (`detector:microboone`,
  `completed`, data-taking ended 2021 -- was rendering `active`)

And **latent** (currently harmless because the entity happens to still be
active today, but a silent time bomb), fixed the same way for consistency:
`data/atlas/geometry/bnl-ags-ring.json`,
`data/atlas/geometry/fermilab-icarus-hall.json`,
`data/atlas/geometry/fermilab-nova-near-surface.json`,
`data/atlas/geometry/fermilab-sbnd-point.json`,
`data/atlas/geometry/leibstadt-conus-detector.json`. A full-atlas grep
confirmed these 10 are the only records with this exact pattern.

*Fix applied*: removed `valid` (set to `null`) on all ten, letting the
feature fall through to the contract's documented fallback ("without it the
feature inherits the entity's timeline"). Verified directly against
`hepgraph.atlas.build._Context.status_at_build`/`segments` for every
affected entity, and against the rebuilt bundles, before and after. Any
genuine shape-vs-entity nuance `valid` had captured (e.g. the HERA/LHC
tunnel predating its machine by 1-2 years) is preserved as a plain-text
`note` instead. Commit: `e2280ee`.

*Not fixed*: the root cause in `hepgraph/atlas/build.py` itself. This is a
pipeline-code defect, not a data defect, and out of scope for a data-only QA
pass to patch; flagged here for a maintainer with edit authority over
`hepgraph/atlas/build.py`. A proper fix would distinguish "this shape's
structural existence window" from "this shape's operating-status label",
rather than conflating both into a single hard-coded `'active'`.

### P1 -- fixed

1. **`data/atlas/geometry/lhaaso-array-point.json` /
   `data/atlas/maps/lhaaso-daocheng.json`**: replaced a 5000 m-accuracy
   OSM/Nominatim rest-area geocode with a peer-reviewed, collaboration
   -authored coordinate (Chinese Physics C 46, 030001 (2022),
   doi:10.1088/1674-1137/ac3fa6, independently fetched and confirmed
   verbatim on two mirrors during this review). `representation`
   georeferenced->surveyed, `confidence` approximate->verified, `accuracy_m`
   5000->50. New source `src:geo-lhaaso-cpc-2022-instruments`. Commit
   `8e7ce37`.
2. **`data/atlas/geometry/fermilab-seaquest-point.json`** (new) +
   `data/atlas/maps/fermilab.json`: drew `detector:seaquest` (NM4 building),
   previously unlocated on the basis of a search for the literal string
   "NM4"; a search for the experiment's own name finds OSM node 4425992583
   directly (independently re-fetched by this reviewer, not just trusted
   from a subagent). New source `src:geo-fermilab-osm-seaquest-node`.
   Commit `ed89376`.

### P2 -- fixed (licensing / provenance hygiene)

1. **Fermilab canonical-JSON**: 20 map/geometry records failed the A11
   canonical-JSON test (unescaped em-dash/(c)). Re-serialised via
   `hepgraph.atlas.load.dump_json`; no field values changed. Commit
   `5a010f1`.
2. **Missing ODbL licence on OSM/Nominatim-derived shapes** (see SS4 for the
   root cause): `data/atlas/geometry/meyrin-site-marker.json`,
   `lhaaso-array-point.json` (superseded by fix #1 above),
   `magic-array-point.json`, `ctao-north-lst1-point.json`. Commits `43e964a`,
   `ed89376`.
3. **Stray ODbL licence on `inferred_direction` records**:
   `j-parc-neutrino-direction-line.json`, `kek-neutrino-direction-line.json`
   carried a licence block despite `osm: null` and no OSM element ever
   traced, inconsistent with every sibling `inferred_direction` record in
   the atlas. Cleared. Commit `8e7ce37`.
4. **Missing `osm.timestamp`**: seven CERN Point-N boundary records
   (`point1-atlas-boundary.json`, `point2-alice-boundary.json`,
   `point5-cms-boundary.json`, `point8-lhcb-boundary.json`,
   `point2-l3-boundary.json`, `point4-aleph-boundary.json`,
   `point8-delphi-boundary.json`) had `osm.elements` populated but
   `osm.timestamp: null`, even though the extract's `timestamp_osm_base` was
   on file in each record's own cited source. Populated from that source.
   Commit `8e7ce37`.

### Documentation only (no data value changed)

`data/atlas/geometry/fermilab-tevatron-ring.json`: added a note recording
that two independently dispatched QA reviewers both reproduced the circle
fit from scratch and both found secondary corroboration (Wikipedia, Main
Ring descriptions) for the "circular" claim the worklog itself flagged as
unconfirmed by any rank<=10 source. Confidence stays `derived`; the shape
stays drawn. Commit `8e7ce37`.

## 4. Licensing verdict

**PASS, after fixes.** The contract requires every OSM-derived shape to
carry `license: {name: "ODbL-1.0", ...}`; the validator enforces this
automatically, but only for records citing a source whose `source_type` is
exactly `"openstreetmap"` (`hepgraph/atlas/validate.py` ~2519-2535). Several
records across the atlas predate the A25 `openstreetmap` source-type
convention and cite an older `source_type: "geocoder"` source instead (with
`publisher: "OpenStreetMap contributors / Nominatim"`) -- real OSM/Nominatim
data, just labelled in a way the validator's check does not recognise. This
review found and fixed five such records
(`meyrin-site-marker.json`, `lhaaso-array-point.json` [since re-sourced
away from OSM entirely], `magic-array-point.json`,
`ctao-north-lst1-point.json`) by a targeted grep of the 14 in-scope maps,
then confirmed by a **full-atlas** grep (all 132+ geometry records, not just
the 14 in scope) that these were the only instances: a repeat of the same
query after the fixes returns zero `representation: georeferenced` records
with `license: null` anywhere in the atlas. The underlying validator gap
itself (the `source_type == 'openstreetmap'` string check not also covering
`'geocoder'` sources whose publisher says OpenStreetMap/Nominatim) is a
schema/validator-level fix, not a data fix, and is flagged here for a
maintainer, not applied.

No copied official figure, plan, screenshot, or embedded image was found
anywhere in `data/` or `static/` for any facility: a filetype scan
(`png|jpg|jpeg|gif|svg|webp|pdf|tif`) across `data/atlas` and
`static/atlas` found nothing under `data/atlas` and only Leaflet's own
vendored marker icons under `static/atlas/vendor/`; a base64/data-URI grep
found hits only inside the vendored `leaflet.js` and `globe.gl.min.js`
library bundles, unrelated to any facility's own content. **No P0 copying
violation found.**

## 5. Security

No feature in any of the 14 in-scope maps depicts access control, guard
posts, checkpoints, or utility vulnerabilities (grepped every geometry/map
record for guard/checkpoint/access-control/restricted-area/badge-reader
language; one hit, "outer guard ring" on `lhaaso-array-point.json`, is
KM2A's own physics-detector outer ring, not a security feature). Everything
drawn is the kind of structure that already appears on the labs' own public
campus maps and schematics.

## 6. Fit-for-production verdict per map

| Map | Verdict | Key reason |
| --- | --- | --- |
| map:cern | Fit for production | LHC/LEP ring and FASER/SND@LHC anchor both hold up bit-exact under independent OSM reconstruction; 2 P2s fixed |
| map:fermilab | Fit for production | Tevatron circularity independently reconfirmed twice; P0 status bug and a P1 missed-feature both fixed |
| map:j-parc | Fit for production | All principal checks independently reproduced from primary PDFs |
| map:kek | Fit for production | KEK-PS's flagged judgement call already correctly resolved (confirmed, not just trusted); KEKB/SuperKEKB verified bit-exact |
| map:brookhaven-national-laboratory | Fit for production, after the P0 fix | RHIC's hexagonal ring verified to <1 m against a fresh OSM fetch; was rendering as a currently-operating collider before this pass |
| map:desy | Fit for production, after the P0 fix | HERA's ring verified to 0.30%; was rendering as a currently-operating collider (shut down 2007) before this pass |
| map:surf | Fit for production | LZ/DUNE depth and unlocated-far-detector honesty both independently confirmed |
| map:snolab | Fit for production | 22 m cavity verified against a fresh primary-paper fetch |
| map:kamioka-observatory | Fit for production | Super-K verified against a second, independent primary paper; Hyper-K's under-construction status correctly not shown as operating |
| map:amundsen-scott-south-pole-station | Fit for production **as an honest placeholder**, not yet a complete flagship map | Only 1 feature drawn, 8 entities honestly unlocated for a real, reproduced blocker; a concrete, citable unblock (`github.com/icecube/icetray-public`) now exists in the backlog but was not applied this pass |
| map:km3net-arca | Fit for production | R=500 m footprint verified verbatim against the LoI's own figure caption |
| map:pierre-auger-observatory | Fit for production | 3160.6 km2 hull independently reproduced from a from-scratch UTM conversion of the Collaboration's own released station data |
| map:hess-khomas-highland | Fit for production | Coordinate and "120 m square" independently reconfirmed against a second official page; geometry rebuilt from scratch to ~2 mm |
| map:lhaaso-daocheng | Fit for production, materially improved this pass | Coordinate upgraded from a 5000 m geocode to a 50 m peer-reviewed figure |

## 7. Fixed-vs-open ledger

**Fixed this pass** (10 commits on branch `hep-atlas-local-maps-qa`,
none pushed): Fermilab canonical-JSON (20 files); 5 missing-ODbL-licence
records; 2 stray-licence `inferred_direction` records; 7 missing
`osm.timestamp` records; the P0 status-inheritance bug on 10 records (5
live, 5 latent); the LHAASO coordinate upgrade; the Fermilab SeaQuest
addition; a documentation-only Tevatron note.

**Open** (not fixed, for a future pass or a different owner):

1. **`hepgraph/atlas/build.py::_feature_segments` root cause** (SS3): the
   data-level symptom is fixed on every affected record found; the
   pipeline-code bug itself is not. A code owner should fix the function so
   a `valid` window with `start` set and `end` null bounds the shape's
   *existence*, not its *status label*, or requires an explicit status
   alongside an open `end`.
2. **The `source_type: geocoder` vs `openstreetmap` license-check gap**
   (SS4): the data instances found are fixed; the validator's check itself
   still only recognises `source_type == 'openstreetmap'`. A future record
   citing a `geocoder`-typed OSM/Nominatim source would still slip through.
3. **`geometry:sps-tunnel-ring.json` representation class**: a subagent
   argues this arguably belongs on the `derived` side of the contract's own
   derived-vs-georeferenced line, since the underlying OSM way is itself a
   mapper-fitted circle rather than a wall trace. This reviewer's own
   reading is that "georeferenced" remains technically correct (the atlas
   traces a third party's way verbatim; it does not itself compute a
   circle) and that the existing mitigations (accuracy_m widened to 30 m,
   confidence held at `approximate`, extensively documented) already contain
   the practical risk. Left open as a maintainer judgement call, not
   reclassified.
4. **`geometry:hess-ct5-point.json`** representation/confidence
   (`surveyed`/`verified`) arguably overclaims for a point inferred from
   "centre of the array" rather than independently published for CT5
   itself; low practical risk (well inside its own 200 m accuracy_m). Not
   changed.
5. **South Pole's IceCube-array blocker**: a concrete, citable, working
   substitute for the docs.icecube.aq page that blocked the original
   researcher (`github.com/icecube/icetray-public`'s own `coordinates.rst`,
   giving the local-grid-to-true-north orientation) was found this pass but
   not applied -- drawing the 86-string footprint is new geometry work
   beyond this review's remit. Recommend prioritising it.
6. **Auger's official-page citation** for "3000 km2 array of 1660 particle
   detectors" no longer renders that text live at the cited URL (confirmed
   by two independent fetch methods); the number itself remains correct and
   well-corroborated elsewhere. Needs a re-sourced citation, not a changed
   fact.
7. **Site-record corrections** flagged by the original researchers and
   independently re-confirmed (not applied, by design) by this review's
   subagents: Fermilab (`site:fermilab-cdf-collision-hall-b0`,
   `-d0-collision-hall`, `-mc-1-muon-campus`), BNL (`site:bnl-rhic-ip6-star`,
   `-ip8-phenix-sphenix`, `site:jlab-newport-news` -- a ~13 km real error,
   not a refinement), DESY (`site:desy-hamburg-campus`,
   `-hera-north-hall-h1`, `-hera-south-hall-zeus`), Kamioka/CJPL
   (`site:cjpl-i`, `-ii`, `site:kamioka-hyper-kamiokande-tochibora`), SURF
   (`site:surf-surface-campus`), and now `site:lhaaso-haizi-mountain` (this
   review's own LHAASO fix updated the map/geometry records but, per the
   established "report, don't edit" convention this whole project uses for
   site records, left the site record itself on its old 5000 m-precision
   point). These belong to whoever owns `data/atlas/sites/`, not to this
   geometry QA pass; consolidated here for that handoff.
8. A subagent independently found that the Fermilab worklog's own
   machine-readable site-coordinate-correction block (SS7.7) has a
   10-19 m error in its own stated centroid vs. the true area-weighted
   (shoelace) centroid of the already-committed OSM polygons -- worth fixing
   before that block is ever applied, but it is worklog-only text, not yet
   applied to any `data/atlas/sites/` record, so nothing in the live data is
   wrong.

No coordinate, source, or claim was invented anywhere in this review. Every
fix above cites a source this reviewer or a dispatched subagent
independently fetched and confirmed.
