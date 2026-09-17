# Scientific and historical review — Fermilab/DUNE, other Fermilab neutrino experiments, Japan, CERN/ATLAS, historic LEP/SppS experiments

Reviewer scope (per assignment): everything NOT already covered by the prior
reviewer (IceCube, LZ/LUX, Belle/Belle II, CMS were out of scope here).
Covered: DUNE + LBNF/Fermilab/SURF; NOvA, MINOS, MINOS+, MINERvA, MicroBooNE,
SBND, ICARUS, MiniBooNE; T2K, K2K, Kamiokande, Super-K, Hyper-K + J-PARC/KEK/
Kamioka; ATLAS + CERN accelerator chain (LHC, HL-LHC, SPS, PS, PSB, Linac2,
Linac4, LEP, ISR); UA1, UA2, ALEPH, DELPHI, L3, OPAL.

Method: read every in-scope `experiment/`, `detector/`, `facility/`,
`accelerator/`, `beamline/`, `site/`, `collaboration/`, and `result/` file;
cross-checked ~35 technical quantities against the actual cited source (arXiv/
ar5iv full text, home.cern pages, collaboration pages, INSPIRE API) via
WebFetch/curl; ran `hepgraph.atlas.schema.state_at` for the sampled years
1975/1985/1995/2005/2012/2020/2026 across every in-scope experiment, detector,
accelerator and facility, plus a full-scope A10 consistency scan
(`status` field vs. `state_at(id, "2026", build_date="2026-09-17")`).

## Findings

### P1 — Fermilab's derived timeline state is permanently stuck at "construction", contradicting its own `status: "active"`

- **Files:** `data/atlas/facilities/fermilab.json`, `data/atlas/accelerators/fermilab-linac.json`
- **What the data says:** Both records carry `"status": "active"` at the top
  level, but `hepgraph.atlas.schema.state_at(record, Y, build_date="2026-09-17")`
  returns `{"status": "construction", ...}` for **every** year I tested from
  1969 through 2026 (today), with `active` only ever appearing as a
  `secondary_states` entry. Confirmed reproducibly:
  ```
  facility:fermilab            @2026 -> construction (secondary: ['active'])
  accelerator:fermilab-linac   @2026 -> construction (secondary: ['active'])
  ```
  This is a live A10 violation ("Entity-level `status` must equal the derived
  state at the build date") that a physicist using the timeline slider today
  would see as: *Fermilab is under construction* — which is false; Fermilab
  has been an operating national laboratory since the early 1970s and
  currently runs the Booster, Main Injector, Recycler, NuMI and BNB beams and
  hosts LBNF/DUNE construction (a genuinely separate, correctly-modelled
  `construction` interval on `experiment:dune`).
- **Root cause (verified in `hepgraph/atlas/schema.py`):** `fermilab.json`'s
  `"first accelerator groundbreaking"` interval (`start: "1968-12-01"`,
  `status: "construction"`, `end: null`, note: *"no end date given by the
  source"*) never terminates. Per A3's selection rule 2, "pick the latest
  `lo(start)`" decides between covering intervals. The competing `"founded"`
  interval is `status: active`, `start: "1967-06-15"` — clearly earlier — so
  that alone wouldn't cause the bug. The actual trigger is
  `accelerator:fermilab-linac`: its `"operating"` interval (status `active`)
  has `start: {"date": "2005", "earliest": "1968", ...}`; `Date.lo()` takes
  `min(own_date, earliest)`, so this interval's effective `lo(start)` is
  **1968-01-01** — earlier than the `"construction"` interval's plain
  `1968-12-01`. The construction interval therefore wins the "latest
  `lo(start)`" tie-break and, having `end: null`, wins it forever. The same
  mechanism applies to `facility:fermilab` (its own construction interval
  interacts the same way once `accelerator:fermilab-linac`'s pattern is
  present, and independently the facility's own two intervals reproduce the
  identical ordering).
- **Correction recommended:** give the `"first accelerator groundbreaking"` /
  `"construction"` interval on `facility:fermilab` (and the matching
  `"construction"` interval on `accelerator:fermilab-linac`) an end date —
  even an approximate one, e.g. `{"date": "1972", "approx": true, "note":
  "Fermilab's original 400 MeV linac and Main Ring were operational by 1972"}`
  — rather than leaving it open. More generally: **this looks like a
  class of bug, not a one-off typo.** Any non-terminal interval with
  `end: null` left open because "no completion date was sourced" for what was
  actually a finite historical construction/commissioning phase will
  permanently dominate the derived state if its `lo(start)` (which can be
  pulled backward by an `earliest` qualifier on a *later*, correctly-active
  interval) ends up later than or equal to that active interval's `lo(start)`.
  I recommend a validator warning: *"a covering interval with status in
  {construction, commissioning, upgrade, shutdown} and `end: null` whose
  `lo(start)` is ≥ a covering `active` interval's `lo(start)` — the derived
  state will never show `active`; either date the earlier interval's end or
  justify why it should out-rank the current operating state."*
- I re-ran the same status-vs-`state_at` scan across every other in-scope
  entity (all experiments, detectors, accelerators, facilities, beamlines,
  collaborations named in the assignment) — this is the **only** pair that
  fails outside of the expected/benign class (terminal `completed`/
  `decommissioned` entities correctly returning `None` past their terminal
  start, per A10's own stated exception — UA1, UA2, ALEPH, DELPHI, L3, OPAL,
  ISR, LEP, Linac2, KEKB, the Tevatron, KEK-PS, MINOS, MiniBooNE, MicroBooNE,
  ProtoDUNE, Soudan lab all behave correctly under that rule).

### P2 — Several `kind: detector`/`underground_lab` coordinates are, in substance, campus/postal-address geocoder points (self-disclosed, but matches the geography risk pattern called out in the brief)

- **Files:** `data/atlas/sites/surf-4850-level-dune-far-detector.json`,
  `data/atlas/sites/j-parc-neutrino-near-detector-hall.json`,
  `data/atlas/sites/fermilab-main-campus.json`
- What the data says / what I found: `site:surf-4850-level-dune-far-detector`
  (`kind: underground_lab`, the DUNE far-detector caverns 1.5 km
  underground) and `site:surf-surface-campus` (`kind: campus`) carry the
  **identical** lat/lon (44.3474397, -103.7548247) — the latter's own record
  says this is "Nominatim jsonv2 result for 'Sanford Underground Research
  Facility'." `site:j-parc-neutrino-near-detector-hall` (`kind: detector`,
  280 m downstream, 37 m-deep pit) shares its exact coordinates with
  `site:j-parc-main-ring` (`kind: campus`), both sourced to "Geocoder
  centroid of the J-PARC landuse polygon." `site:fermilab-main-campus`
  (`kind: detector`, precision_m 3000) is the single point used for
  MicroBooNE, SBND, MINOS near detector, NOvA near detector, MINERvA,
  ICARUS (far, at Fermilab) and the DUNE near detector alike — again an
  OSM/Nominatim campus centroid.
- All three records are candid about this in their own `note` fields
  (`"REVIEW REQUIRED: no geodetic coordinate for the 4850 Level caverns could
  be retrieved... used as a proxy"`; `"Not a surveyed detector coordinate"`;
  `"the coordinate itself is the OpenStreetMap/Nominatim polygon centroid for
  the whole ~27 km² Fermilab campus, not a surveyed position for any one
  detector hall"`), and `confidence` is `approximate`/`uncertain`, not
  `verified`, and A17's letter is technically respected (the geocoder source
  itself is *not* cited on the coordinate value, even though the number
  plainly came from it). So this is **not hidden fabrication** — it is
  exactly the honest "unknown is a value" behaviour the ontology asks for —
  but it is precisely the geography failure mode the review brief named
  ("a detector placed at a laboratory's postal address rather than its
  hall"), and it means the globe currently cannot show any horizontal
  separation between, e.g., the MINOS near detector hall, the NOvA near
  detector, MicroBooNE/SBND/ICARUS in the Liquid-Argon Test Facility area,
  and the future LBNF near-detector hall — they are all one 3 km-radius dot.
  By contrast, the two Kamioka sites and the Soudan site in the same scope
  *are* properly surveyed (GPS coordinates quoted directly from the SK NIM
  paper and the MINOS papers, precision 50–100 m) — showing the researchers
  clearly know how to do this correctly when a primary source states it; the
  gap is only where no such source could be found.
- **Recommendation:** treat these three coordinates as still-open
  `researched: "partial"` items (SURF's own site plans / DUNE's "excavations
  and structures" materials likely give real cavern coordinates; J-PARC's
  facility maps likely give the ND hall's real position; Fermilab's NuMI/BNB
  beamline maps would separate the near-detector halls). Until then, the
  worklog convention of `confidence: uncertain/approximate` +
  `"REVIEW REQUIRED"` should probably be surfaced as a build-level warning
  (a `detector`/`underground_lab` coordinate identical to a `campus`/
  `headquarters` coordinate on the same facility) since it's easy for a
  reviewer to miss in prose.

### P2 — Source-id naming and multi-collaboration claim attribution (minor, no wrong physics)

- `data/atlas/sources/ua1-inspire-w-z-discovery-papers.json` is named for UA1
  but is actually a single combined INSPIRE query covering **both** UA1 and
  UA2's 1983 W/Z papers (recids 188736, 189048, 190338, 191740), and it is
  cited as the *sole* source for `data/atlas/results/ua2-w-boson-observation-1983.json`'s
  claim. I confirmed via the INSPIRE API that all four titles/collaborations
  are correct as recorded, so there is no wrong attribution — just a
  confusing id (`ua1-...`) for a source that is really about UA1 *and* UA2.
  Recommend renaming to something collaboration-neutral
  (e.g. `src:cern-1983-w-z-discovery-papers`).
- `data/atlas/results/lep-three-neutrino-species-1989.json` attributes the
  1989 "number of light neutrino species" result jointly to ALEPH, DELPHI,
  L3 and OPAL, with `claim.quote: "Determination of the Number of Light
  Neutrino Species"`. I verified via the INSPIRE API that this exact title
  belongs **only** to the ALEPH paper (recid 282904, Phys.Lett.B 231 (1989)
  519); DELPHI's paper (282905) is titled "Measurement of the Mass and Width
  of the Z⁰ Particle...", L3's (282041) "A Determination of the Properties
  of the Neutral Intermediate Vector Boson Z⁰", OPAL's (282821) "Measurement
  of the Z⁰ Mass and Width with the OPAL Detector at LEP" — none contain
  "neutrino species" wording. The record's own `locator` already says "ALEPH
  paper title," so this is disclosed, not concealed, and the underlying
  physics claim is correct (all four experiments' first LEP running in 1989
  did jointly establish Nν ≈ 3). But a single representative quote is being
  used to stand in for four different papers with four different titles.
  Recommend using A16's `result.experiment_ids: [{"id","sources"}]`
  per-attribution mechanism to give each collaboration its own title/source
  rather than one shared `claim.quote`. This is the kind of thing worth a
  validator note ("a result whose `experiment_ids` lists N experiments but
  whose `claim.quote` matches only one of their paper titles").
- `experiment:nova`'s "Near detector mass" key_spec (`0.3 kt / 300 t`,
  sourced to a 2025 MINERvA-adjacent monopole-search paper) and the NOvA PRD
  106, 032004 (2022) oscillation paper I fetched independently both exist and
  say slightly different things: the 2022 paper states "**290 ton** Near
  Detector," the source actually cited for the 300 t figure does say "0.3 kt."
  Both are real, both are minor roundings of the same ~300 t detector — not
  an error, just an unlogged minor cross-source discrepancy (worth a note
  next to the value, per the research method's own conflict-logging
  convention, but far below the threshold of a defect).

## Values checked and confirmed against the primary source (WebFetch/curl, not from memory)

All of the following were re-fetched from the cited URL (arXiv/ar5iv full
text, home.cern, collaboration site, or the INSPIRE API) and the quoted text
in the data file was found verbatim or effectively verbatim in the source:

1. DUNE far detector fiducial mass "at least 10 kt" per module — DUNE FD TDR Vol. I (arXiv:2002.02967)
2. DUNE cryostat LAr mass "17.5 kt" each, "nearly 70 kt" total — same
3. DUNE 1300 km baseline language ("The 1300 km baseline offered by locating the FD at SURF...") — same
4. DUNE FD1 max drift length "3.5 m" at "500 V/cm" — same
5. DUNE hosted by Fermilab — same
6. LBNF baseline 1285 km (ProtoDUNE-SP performance paper, arXiv:2007.06722-equivalent record `dune-protodune-sp-performance-2020`) — consistent with TDR's own "~1300 km" rounding, both cited
7. NOvA far detector "14 kt... Ash River, Minnesota... ~810 km" — NOvA PRD 106, 032004 (arXiv:2108.08219)
8. NOvA off-axis angle "14.6 mrad", peak energy "1.8 GeV" — same
9. NOvA near detector "290 ton" (cross-checked against the record's own "0.3 kt / 300 t," see P2 note above)
10. MINOS far detector "Soudan, MN (47.8° N, 92.2° W), 735.3 km" — MINOS detector paper (arXiv:0805.3170)
11. MINOS far detector mass "5,400 metric ton" — same
12. MINOS near detector "282 plane, 980 metric ton" — same
13. MINOS magnetic fields "1.28 T" (near) / "1.42 T" (far) — same
14. T2K target-to-Super-K distance "295,335.2 ± 0.7 m" — T2K NIM A 659 (arXiv:1106.1238)
15. T2K off-axis angle "2.504 ± 0.004°" — same
16. J-PARC main ring "Circumference 1567 m," "~750 kW," "30 GeV" — same
17. J-PARC beam arc bend "80.7°... 104 m radius" — same
18. T2K target "91.4 cm... 2.6 cm diameter" graphite rod — same
19. Super-K tank "39.3 m diameter, 41.4 m height" — SK detector page (icrr.u-tokyo.ac.jp)
20. Super-K "11,129" inner PMTs, "~40%" photocoverage — same
21. Hyper-K "0.260 million metric tons" total / "0.188 million metric tons" fiducial — Frontiers in Physics 12:1378254 (2024)
22. Hyper-K tank "71 m high and 68 m diameter" — same
23. Hyper-K cavern excavation start "October 2022" — same
24. Hyper-K planned start "2027" vs "2028" conflict — independently reconfirmed as a real, still-live discrepancy between HK's own sources (not fabricated by the recorder)
25. LHC circumference "26 659 m" — home.cern LHC page
26. LHC Run 3 record "13.6 TeV" and first-beam/first-collision dates (10 Sep 2008 / 23 Nov 2009 / 30 Mar 2010) — same
27. LEP circumference "27-kilometre," initial energy "~91 GeV," final "209 GeV" (2000), tunnel construction Feb 1985, first beam 14 Jul 1989, closure 2 Nov 2000 — home.cern LEP page
28. UA1 central detector "5.8 m long, 2.3 m diameter," "800-tonne" magnet, ran "1981 until 1990" — home.cern UA1 page
29. ATLAS "46 m long, 25 m in diameter," "100 m below ground," "7,000 tonnes" — atlas.cern/Discover/Detector
30. J-PARC history milestones: construction start Dec 2001, Linac design energy Jan 2007, RCS design energy Oct 2007, MR 30 GeV Dec 2008 — j-parc.jp history page
31. ICARUS "760-ton" total / "476 ton" active mass, shipped to Fermilab Jul 2017, cryostats deployed Aug 2018, cryo-commissioning started 13 Feb 2020, beam restart 5 Nov 2021 — EPJC 2023 (arXiv:2301.08634)
32. LEP three-neutrino-species paper attribution — verified via INSPIRE API that recids 282904/282905/282041/282821 are indeed ALEPH/DELPHI/L3/OPAL respectively, each Phys.Lett.B 231 (1989) as recorded

Internally cross-checked (matched between experiment/detector/beamline/result
records without independent re-fetch, all self-consistent): MicroBooNE
170 t/90 t, 470 m, 2.6 m drift; SBND 112 t, 110 m; ICARUS 760 t/476 t, 600 m
Fermilab baseline, 19.6 m × 2 modules; MiniBooNE 541 m, 12.2 m tank, 818 t
oil, 1520 PMTs; NuMI/BNB/LBNF/J-PARC/K2K beam energies and beam powers;
ATLAS toroid/solenoid fields (3.5 T / 2 T), tracker pixel/strip counts;
UA2, ALEPH, DELPHI, L3, OPAL detector dimensions and magnet fields.

## History (`state_at`) sampled years 1975/1985/1995/2005/2012/2020/2026

Ran `schema.state_at` for every in-scope experiment, detector, accelerator
and facility at all seven sampled years (raw output retained in this
session's transcript). No time-travel found other than the Fermilab
construction-lock-in above: e.g. ATLAS is `None` in 1975/1985, `proposed` in
1995, `construction` in 2005, `active` in 2012, matching A13's own worked
example; DUNE is `None` until 2020 and `construction` in 2020/2026 exactly as
A13 specifies; UA1/UA2/ALEPH/DELPHI/L3/OPAL correctly show `None` in 1975 and
2005+ (pre-existence / post-terminal, per the A10 exception) and `active`
through their real 1981–1990 / 1989–2000 run windows; Kamiokande-observatory
correctly shows `None` in 1975 and 1985 (established 1995) even though
Kamiokande the *experiment* legitimately starts in 1983 — the facility's own
notes already flag and explain this expected "experiment before its host
facility" mismatch as intentional, not a bug.

## Geography

Sanford (SURF) far-detector site, Ash River (NOvA far detector), Soudan
(MINOS far detector), the two Kamioka mine sites, and the CERN LHC/SPS/LEP
points all carry real surveyed or GPS coordinates with sensible
`precision_m` (Soudan 100 m, SK mine 50 m from a GPS survey quoted in the
detector paper, CERN points inherited from prior tiers). The one systematic
gap is the Fermilab/J-PARC/SURF-underground "detector"-kind points discussed
above (P2), which are honestly disclosed but unresolved.

## What I could not verify

- Two source-level claims I could not independently re-fetch full text for
  (arXiv abstract pages only render metadata via WebFetch; I used the
  `ar5iv.labs.arxiv.org` HTML mirror successfully for every LaTeX-sourced
  paper I needed, but PDF-only or paywalled items — e.g. the original 2004
  ICARUS T600 NIM construction paper, which the record itself already flags
  as unfetchable — were not independently checked beyond what the data file
  already discloses).
- I did not attempt to re-verify every one of the ~140 in-scope INSPIRE
  `date_proposed`/`date_approved`/`date_completed` fields against the live
  INSPIRE API individually; I spot-checked the LEP-experiment set (4/4
  correct) and the UA1/UA2 set (paper titles/collaborations 4/4 correct) and
  trust the pattern holds given how consistently the rest of the dataset held
  up under fetching.
- Did not re-derive the ATLAS "92 million pixels" / "300,000 TRT straws"
  figures against the original JINST 2008 paper beyond the quotes already
  captured in the record (locator given, plausible, consistent with public
  knowledge of the ATLAS Inner Detector).

## Verdict

Across 32 independently re-fetched, quote-level-verified technical claims and
a full historical state_at sweep of every in-scope entity, I found **zero
P0 defects** (no false physics statements, no wrong result attributions, no
inflated claims — the dataset is unusually disciplined about using each
collaboration's own conservative wording, e.g. "observation" not "discovery"
for the 2012 Higgs paper, "indication"/2.5σ correctly kept out of "evidence,"
SN1987A correctly typed `first_detection` rather than generic `observation`).
I found one real **P1** bug (Fermilab's derived timeline state is
permanently pinned to "construction" due to an open-ended interval
interacting with the `earliest`-date lo() rule — a genuine, reproducible
defect a physicist would notice immediately on the timeline slider) and
three **P2** items (all self-disclosed geocoder-derived detector coordinates;
a confusingly-named shared source id; one multi-collaboration result using a
single collaboration's paper title as its representative quote). A physicist
would trust this data — the sourcing discipline, explicit conflict logging,
and conservative result-type wording are well above what I'd expect from an
automated research pass — with the one caveat that the Fermilab status bug
should be fixed before anyone screenshots the "current" state of the globe.
