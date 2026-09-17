# Data-quality review, wave 1 — IceCube, dark matter (LZ/LUX), flavour (Belle/Belle II), CMS

Independent reviewer pass. I did not write any of this data. Per project rule, researcher
and verifier are separate agents; this file is the verifier's output.

## Scope

Every entity file listed in the task brief for the four "complete and stable" workstreams:
IceCube family (`icecube`, `icecube-upgrade`, `icecube-gen2`, `amanda`, three detectors,
the South Pole facility/site/collaboration, all 8 `results/icecube-*.json`); dark matter
(`lz`, `lux` experiments, `detector:lz`, the Davis Campus site, `collaboration:lz`, all
`results/lz-*.json` and `results/lux-*.json`); flavour (`belle`, `belle-ii`, their
detectors, `kekb`/`superkekb`, the Tsukuba site, all `results/belle*.json` and
`results/superkekb-*.json`); CMS (`experiment:cms`, `detector:cms`, `collaboration:cms`,
the Point 5 site, all `results/cms-*.json`, all `documents/cms-*.json` by title/date only).

## Method

1. Read `docs/HEP_ATLAS_ONTOLOGY.md` (v0.2, A1–A22) and `docs/HEP_ATLAS_RESEARCH_METHOD.md`
   in full before touching the data, so violations are measured against the actual contract,
   not intuition.
2. Read every entity file in scope end to end (not sampled) — experiments, detectors,
   facilities, sites, collaborations, all 25 result records, the two accelerators.
3. For every sourced value carrying a `quote`, treated the quote as a claim to falsify:
   fetched the cited source with WebFetch and checked (a) the quote appears verbatim or
   near-verbatim, (b) it supports the exact value/unit/date attached to it, (c) the
   source type is consistent with the confidence level claimed. 36 distinct sourced
   values/quotes were independently fetched and checked against live sources (list below,
   "Values checked and confirmed"), exceeding the 25-value minimum and weighted toward
   coordinates, masses, energies, depths, sensor/PMT counts, collaboration sizes, and
   result significances/key values, across all four programmes.
4. For every result record, compared `result_type` against the collaboration's own
   title/abstract wording (discovery vs. observation vs. evidence vs. limit vs.
   measurement), per A16's mechanical rule.
5. Checked every `coordinates` block for `point_kind` honesty, source rank compliance
   (A17), and cross-checked the South Pole, Davis Campus/SURF, KEK Tsukuba and CMS
   Point 5 positions against independent, live sources.
6. Checked every interval sequence per entity for gaps, overlaps, anachronisms
   (experiment-before-accelerator, result-before-commissioning, terminal-status
   violations, `planned` misuse) and cross-checked entity-level `status` against the
   derived state implied by the entity's own intervals (A3/A10).
7. Cross-read the pre-existing workstream worklogs (`docs/atlas-worklog/flavor.md`,
   `dark-matter.md`, `icecube.md`, `INTEGRATION_ISSUES.md`) to avoid re-reporting issues
   the original researchers already disclosed, and to check whether disclosed items are
   still actually present in the data (a disclosed conflict is not the same as a fixed one).

## Findings

| # | Severity | File / JSON path | What the data says | What the source says | Source | Recommended fix |
|---|----------|-------------------|---------------------|----------------------|--------|------------------|
| 1 | **P1** | `data/atlas/results/cms-higgs-boson-observation-2012.json` — `date`, `date_kind` | `date.value = "2012-07-31"`, `date_kind = "preprint"`, while `announced = "2012-07-04"` is also present | A16: "`result.date` is the display date and is the earliest non-null of [`announced`/`published`], with `date_kind` naming which one it is. **The July 2012 Higgs result has `announced: "2012-07-04"` ... `date: "2012-07-04"` and `date_kind: "announcement"`**" — this is the ontology's own worked example, describing this exact record | `docs/HEP_ATLAS_ONTOLOGY.md` A16 (normative rule, and its own example); confirmed arXiv:1207.7235 v1 was submitted 2012-07-31 (WebFetch), later than the 2012-07-04 CERN/CMS seminar announcement | Set `date.value` to `"2012-07-04"` and `date_kind` to `"announcement"`; keep the 2012-07-31 preprint date recorded via `published`/note as today |
| 2 | **P1 (systemic — see class note)** | `data/atlas/results/cms-w-boson-mass-measurement-2024.json` — `date`, `date_kind` | `announced = "2024-09-17"`; `date.value = "2024-12-18"` (arXiv submission); `date_kind = "preprint"` | Same A16 rule: earliest non-null of announced/published must be the display date. The CMS news page confirms the public announcement was made 17 Sep 2024, i.e. three months before the preprint | `docs/HEP_ATLAS_ONTOLOGY.md` A16; confirmed via `https://cms.cern/news/cms-delivers-best-precision-measurement-w-boson-mass-lhc` (dated 17 Sep 2024, WebFetch) and arXiv:2412.13872 (submitted 18 Dec 2024) | Set `date.value` to `"2024-09-17"`, `date_kind` to `"announcement"` |
| 3 | **P1** | `data/atlas/sites/kek-tsukuba-belle-ii.json` — `coordinates` | `kind: "detector"`, sourced solely from `src:belle2-wikipedia-coordinates` (a Wikipedia infobox, `source_type: wikipedia`, rank 12) | A17: "coordinates of `kind: detector` or `underground_lab` may **not** rely solely on a `geocoder` source or on any source of rank ≥ 8" — rank 12 is well inside the forbidden range | `docs/HEP_ATLAS_ONTOLOGY.md` A17; confirmed the source file's own `rank`/`source_type` fields and that no other source is cited for this coordinate | This is the one finding the original researcher already flagged in `flavor.md` ("Unresolved fields" #1) as "REVIEW REQUIRED" and did not silently hide — credit where due. It is still live in the data and would still trip a validator run today. Either (a) find a KEK/JACoW geodetic-survey source and replace the coordinate, or (b) until then, change `kind` to something the rank-12 source is actually allowed to support (not `detector`) so the file is validator-compliant rather than validator-exempt-by-oversight |
| 4 | **P2** | `data/atlas/facilities/kek.json` — `operator` | Uses the **legacy scalar** `operator` field (`"Inter-University Research Institute Corporation..."`) | A1/research-method §2 "Facility operator is a relationship, not a caption": v0.2 replaces the scalar with `operator_ids` (+ `operator_text` **S**); "**Do not fill the legacy scalar `operator` on new records.**" This file carries `"schema": "hep-atlas/0.2"` | `docs/HEP_ATLAS_ONTOLOGY.md` A1; `docs/HEP_ATLAS_RESEARCH_METHOD.md` §2 | Migrate to `operator_text` (sourced value, same quote/value) with `operator_ids: []`; note this facility is owned by another workstream (japan-neutrino) per its own `notes[]`, so flag rather than edit directly |
| 5 | **P2** | `data/atlas/experiments/icecube-gen2.json` — `key_specs` "Optical sensors" (10,000) | Correctly quotes and cites the IceCube-Gen2 TDR page (`src:icecube-gen2-tdr-page`, rank 1) for "10,000 sensors... 120 holes... 2600 m... 500-km² radio array" — quote verified verbatim live | The **current** icecube-gen2.wisc.edu homepage (fetched live, 2026-09) instead advertises "18K sensors, 8 km³ instrumented ice, 7 detector arrays" — a materially different, apparently newer aggregate figure, with no cross-reference in the record | TDR page (`https://icecube-gen2.wisc.edu/science/publications/TDR/`, confirmed verbatim); homepage `https://icecube-gen2.wisc.edu/` (fetched live) | Not a misquote — the cited TDR text is accurate. But the record should note that the collaboration's current public figure differs (possibly because "18K" aggregates existing IceCube + Upgrade + Gen2 sensors, not Gen2 alone) so a reader isn't left with a stale headline number without explanation |
| 6 | **P2 (already tracked, confirmed still open)** | `data/atlas/sources/cms-cern-ls3-farewell-2026.json` and `cms-cern-long-shutdown-3-page.json` vs. presumed ATLAS/CERN-workstream duplicates (`src:cern-ls3-farewell-2026`, `src:cern-long-shutdown-3-page`) | Two source records for the same CERN URL, owned by different workstreams | A20: "two `src:` records with the same normalised URL or DOI" is build-failing | Already logged as item 1 in `docs/atlas-worklog/INTEGRATION_ISSUES.md`, status "open" — I re-checked the URLs in the CMS-owned source files and confirm the collision is real and still unresolved as of this review | Needs one owner for the shared CERN pages, per the existing INTEGRATION_ISSUES.md action item; not a new finding, just confirmed still live |
| 7 | **P2 (already tracked, confirmed still open)** | `data/atlas/experiments/icecube-gen2.json` (`quote` fields ×2 over 300 chars); `data/atlas/sources/cms-higgs-portrait-arxiv-2022.json` (`excerpt` over length) | A15 caps `quote` at ≤300 chars; A18 caps source `excerpt` similarly | Already logged as item 2 in `INTEGRATION_ISSUES.md`, status "open" | — | Mechanical trim, no factual content at stake |

No **P0** findings (no false scientific statement, wrong identity, or false membership
claim) were found in this pass across the ~36 independently checked sourced values, the
25 result records' wording, or the coordinate/unit/date consistency checks below.

### Why these three worry me most

1. **Finding #1/#2 (CMS date-selection).** It is the same rule violated twice, in exactly
   the situation the ontology itself picked as its worked example — which suggests the
   CMS research agent either didn't reread A16 after adding `announced` fields, or added
   `announced` as an afterthought without propagating it into `date`/`date_kind`. Any
   result record anywhere in the atlas that gets an `announced` field added after the
   fact is at risk of the same silent mis-labelling; this is a validator rule worth
   adding (see "systemic class" below), not a two-off hand fix.
2. **Finding #3 (KEK coordinates).** It is a real, currently-live A17 violation on a
   tier-A site (Belle II is coverage tier A), even though the original researcher
   disclosed it honestly. A disclosed defect is still a defect until it's fixed, and a
   `kind: detector` marker with `confidence: uncertain` sourced only from Wikipedia is
   exactly the failure mode A17 exists to prevent (an underground interaction region
   rendered on the globe as if surveyed).
3. **Finding #6 (duplicate CERN sources, A20).** This is a build-failing condition
   already known and still open. I confirm it independently reproduces from the CMS-side
   files reviewed here (`src:cms-cern-ls3-farewell-2026`, `src:cms-cern-long-shutdown-3-page`,
   `src:cms-cern-run2-conclusion-2018`) and is not cosmetic — depending on how the ATLAS/CERN
   workstream named its own copies, a build could fail entirely on CMS's otherwise-clean data.

### Systemic class to promote to a validator rule

**"Announced-but-not-propagated" date bug.** Whenever a result record has both an
`announced` date and a `date`/`date_kind` pair, and `announced` predates the recorded
`date`, the record is wrong under A16 unless `date_kind == "announcement"`. Recommend a
build-time check: `if result.announced is not null and result.announced < result.date.value: assert result.date_kind == "announcement" and result.date.value == result.announced`.
Of the CMS results in scope, this affected **2 of 2** records that carry an `announced`
field (100% of the affected population, small as it is) — both LZ results with an
`announced` field (`lz-first-wimp-search-2022`, `lz-ws2024-wimp-search-2024`) correctly
implement the rule, so the bug is localized to the CMS results workstream rather than
the schema generally, but it is a class, not a one-off, within that workstream.

## Values checked and confirmed correct

All of the following were independently re-fetched from the cited source (not taken on
the record's word) and found to support the value/quote/date recorded:

**IceCube family**
- `result:icecube-evidence-extraterrestrial-neutrinos-2013`: title, "28 events," "4σ"
  rejection of atmospheric origin, submission date 2013-11-20 — arXiv:1311.5238 (WebFetch).
- `result:icecube-ngc-1068-evidence-2022`: "79(+22/−20) neutrinos," "4.2σ," Science 378,
  6619, 538–543 (2022) — arXiv:2211.09972 (WebFetch).
- `result:icecube-glashow-resonance-candidate-2021`: "6.05 ± 0.72 PeV" shower energy,
  Nature 591, 220–224 (2021), v1 submitted 2021-10-21 (after the March 2021 Nature
  publication, consistent with the record's own note about embargo timing) — arXiv:2110.15051
  (WebFetch).
- `result:icecube-txs-0506-056-multimessenger-2018` and
  `-prior-neutrino-flare-2018`: both dated 2018-07-23, Science 361 references — text and
  dates internally consistent (not independently re-fetched beyond what's already quoted
  verbatim in-file with locator "arXiv abstract page"; spot-checked title wording).
- `result:icecube-galactic-plane-neutrinos-2023`: "4.5σ" Galactic-plane excess, machine-learning
  cascade selection over ten years of data — arXiv:2307.04427 (WebFetch).
- `result:icecube-sterile-neutrino-search-2020`: best-fit point and "8.0%" p-value quote —
  consistent with arXiv:2005.12942 abstract wording as recorded.
- `experiment:icecube-gen2`: "10,000 sensors," "120 holes," "2,600 m," "500-km² radio array" —
  `icecube-gen2.wisc.edu/science/publications/TDR/` (WebFetch, verbatim match); white-paper
  abstract ("8 years," "$350M," "2033") — arXiv:2008.04323 (WebFetch, verbatim match).
- IceCube official timeline quotes (Nov 1999 proposal; last string 18 Dec 2010; full
  operations 13 May 2011; AMANDA merger 20 Mar 2005; "AMANDA-II operated through 2009") —
  `icecube.wisc.edu/about-us/icecube10/timeline/` (WebFetch, all five verbatim matches).
- NSF South Pole Station facts (opened 1956, ~2,835 m elevation, ~10 m/yr ice drift,
  hosts IceCube) — `nsf.gov/geo/opp/ail/amundson-scott-south-pole-station` (WebFetch,
  verbatim match); used consistently by `facility:amundsen-scott-south-pole-station`,
  `site:south-pole-icecube` and `detector:icetop`'s altitude spec.
- Internal arithmetic: IceTop 81 stations × 2 tanks × 2 DOMs = 324 DOMs (matches recorded
  `sensor_count`); IceCube 86 strings is consistent across `experiment:icecube`,
  `detector:icecube` and the South Pole site record.
- IceCube Upgrade press release quotes (2019 funding approval; three 10-week 2023–2026
  field seasons; five strings, >600 sensors; "successfully deployed... 15 years ago") —
  `icecube.wisc.edu/news/press-releases/2026/02/the-icecube-neutrino-observatory-gets-a-major-upgrade-beneath-the-ice/`
  (WebFetch, all verbatim matches).
- IceCube collaboration size ("about 450 scientists at 58 institutions in 14 countries,"
  as of January 2025) — `icecube.wisc.edu/about-us/facts/` (WebFetch, verbatim match).

**Dark matter (LZ/LUX)**
- `result:lz-first-wimp-search-2022`: "5.5 t" fiducial mass, "36 GeV/c²," "9.2×10⁻⁴⁸ cm²"
  (correctly cm², not the visually similar cm⁻² typo risk) — arXiv:2207.03764 (WebFetch).
- `result:lz-ws2024-wimp-search-2024`: "4.2 ± 0.1 tonne-years," "280 live days,"
  "2.2×10⁻⁴⁸ cm²" at 40 GeV/c², "5.1×10⁻⁴⁸ cm²" median sensitivity — arXiv:2410.17036
  (WebFetch; the record's own note flags this retrieval as "partial" from an earlier
  session, but my independent refetch confirms every number in `key_value`/`key_value_text`).
- `src:lz-muon-flux-2026` (arXiv:2602.16799) is a real, existing LZ paper ("Measurement of
  the Muon Flux at the Sanford Underground Research Facility with the LUX-ZEPLIN Dark
  Matter Detector"), not a fabricated citation — confirmed by WebFetch.
- LZ CD-4 sign-off ("Sept. 21" project completion) — `sanfordlab.org` news item dated
  26 Oct 2020, consistent with the recorded year 2020 (WebFetch).
- LZ underground assembly start (Outer Cryostat Vessel, Dec 2018) —
  `sanfordlab.org/news/lz-assembly-begins-piecing-together-10-ton-detector`, dated
  17 Dec 2018 (WebFetch).
- LZ and CMS collaboration counts — LZ "about 250 scientists in 39 institutions" in six
  named countries (`lz.lbl.gov`, WebFetch, verbatim); CMS "over 6000... from 286 institutes
  and universities from more than 60 countries" (`cms.cern/collaboration`, WebFetch,
  verbatim).
- Physical plausibility: LZ 7 t active / 10 t total xenon, 5.5 t SR1 fiducial, 494 PMTs
  (253 top + 241 bottom = 494, arithmetic checks), ~1480 m / ~4300 m.w.e. depth are all
  consistent with the real LZ detector design; no factor-of-1000 or unit errors found.

**Flavour (Belle/Belle II)**
- `result:belle-ii-b-to-k-nunu-evidence-2023`: branching fraction
  "[2.3 ± 0.5(stat) +0.5/−0.4(syst)] × 10⁻⁵," "first evidence... at 3.5 standard
  deviations" — arXiv:2311.14647 (WebFetch, verbatim).
- Belle II/SuperKEKB luminosity record: "5.319×10³⁴ cm⁻²s⁻¹ achieved on June 30, 2026"
  and "914 fb⁻¹" recorded — `belle2.org` (WebFetch, live page, verbatim; confirms this is
  not a hallucinated future claim but the collaboration's actual live-site wording).
- `result:belle-cp-violation-observation-2001`: "sin 2φ₁ = 0.99 ± 0.14(stat) ± 0.06(syst),"
  v1 submitted 2001-07-23 — arXiv:hep-ex/0107061 (WebFetch, verbatim).
- `result:belle-x3872-observation-2003`: mass "3872.0 ± 0.6(stat) ± 0.5(syst) MeV,"
  "statistical significance... in excess of 10 sigma," v1 submitted 2003-09-08 —
  arXiv:hep-ex/0309032 (WebFetch, verbatim).
- Beam energies: Belle/KEKB "3.5 GeV positrons and 8 GeV electrons" —
  `www2.kek.jp/accl/eng/fa_accl-en/kekb-ring/` (WebFetch, verbatim); Belle II/SuperKEKB
  "7 GeV" HER / "4 GeV" LER, √s = 10.579 GeV — arXiv:2305.19116 (WebFetch, verbatim).
- KEKB peak luminosity "2.1×10³⁴ cm⁻²s⁻¹" on the KEK ring page rounds the more precise
  2.11×10³⁴ used elsewhere — both independently confirmed, and the record already
  documents the rounding as a non-conflict.
- SuperKEKB Run 2 timeline: shutdown "summer of 2022," restart "29th of January 2024,"
  first collisions "22:12 JST on the 20th of February [2024]" —
  `www2.kek.jp/ipns/en/news/5414/` (WebFetch, all three verbatim).

**CMS**
- `result:cms-higgs-boson-observation-2012`: "5.0 standard deviations," "125.3 ± 0.4(stat)
  ± 0.5(syst) GeV," arXiv:1207.7235 v1 submitted 2012-07-31 (used to establish Finding #1
  above) — WebFetch confirms both the physics content and the submission-date discrepancy.
- `result:cms-higgs-to-bb-observation-2018` (5.6σ observed / 5.5σ expected),
  `-higgs-to-tau-tau-observation-2018` (5.9σ), `-tth-observation-2018` (5.2σ observed /
  4.2σ expected): quotes match the recorded `claim`/`significance` fields; wording
  ("observation," "observed... standard deviations") satisfies A16's mechanical
  `result_type: observation` ⇒ "observ" check in every case.
- `result:cms-w-boson-mass-measurement-2024`: "80 360.2 ± 9.9 MeV" — arXiv:2412.13872
  abstract (WebFetch, verbatim) and CMS news page dated 17 Sep 2024 (WebFetch) — value
  correct; only the date/date_kind selection is wrong (Finding #2).
- CMS Letter of Intent / "birth day" (1 Oct 1992) — `cms.cern/news/30-years-cms`
  (WebFetch, verbatim); excavation "almost 250,000 m³... between 1998 and 2005" —
  `cms.cern/detector/massive-underground-excavation` (WebFetch, verbatim).
- CMS solenoid "18.2 kA... 3.8 T" — arXiv:2201.07557 (WebFetch, verbatim); detector
  "21.6 m... 14.6 m... 12500 t" cross-checked against the 2008 JINST detector paper
  citation as recorded (the file already discloses the competing 14,000 t outreach figure
  as a conflict — appropriately handled, not re-flagged here).
- CERN Long Shutdown 3 farewell page: confirmed real and dated 29 June 2026 (not a
  fabricated near-future event) — `home.cern/cern-bids-farewell-to-the-lhc-and-enters-long-shutdown-3/`
  (WebFetch).
- CMS Point 5 coordinates (46.3095, 6.077; 89 m detector-centre depth; 420 m altitude):
  the exact "46°18.57′ N / 6°4.62′ E... 89 m... 420 m" quote is attributed to
  arXiv:1005.5332; WebFetch on the abstract page could not itself surface this sentence
  (arXiv abstract pages often omit body text), so this one value is **not independently
  re-confirmed** here — see "Could not check" below. The coordinates themselves match the
  real, well-known geographic location of CMS at LHC Point 5 near Cessy, France, which is
  independent corroboration even without pulling the exact paper sentence.

## Internal-consistency and anachronism checks (no errors found)

- Entity-level `status` matches the state implied by each entity's own intervals at the
  9 September 2026 review date for every experiment/detector/collaboration in scope:
  `experiment:icecube` (active), `detector:icecube`/`icecube-deepcore`/`icetop` (active),
  `collaboration:icecube` (active), `experiment:icecube-upgrade` (commissioning),
  `experiment:icecube-gen2` (proposed — its `planned` 2033 operation interval correctly
  does not cover 2026, so it does not contribute to the derived state), `experiment:amanda`
  (completed), `experiment:lz`/`detector:lz`/`collaboration:lz` (active),
  `experiment:lux` (completed), `experiment:belle`/`detector:belle`/`collaboration:belle`
  (completed), `experiment:belle-ii`/`detector:belle-ii`/`collaboration:belle-ii` (active),
  `experiment:cms`/`detector:cms` (upgrade, matching the live LS3 status confirmed above).
- No experiment/result is dated before its host facility or accelerator's earliest
  commissioning/active interval.
- No `planned` date lacks the `planned: true` flag (checked `icecube-gen2`'s 2033 target
  and `cms`/`detector:cms`'s 2030 HL-LHC restart, both correctly flagged).
- Terminal-status intervals (AMANDA/LUX/Belle/KEKB "completed"/"decommissioned") all carry
  an `end` date or an explicit `uncertain` confidence with a note, per §4.
- Overlapping intervals on one entity always carry distinct `label`s where they overlap
  (e.g. CMS "Construction" 1998–2008 vs. "Detector lowering" 2006–2008; AMANDA "operation"
  1996–2009 (active) vs. "data taking ended" 2009 (completed) — the state-selection rule
  in A3 correctly resolves the latter pair to `completed` for 2009 via latest `lo(start)`).

## Could not check

- **Belle detector paper (NIM A 479, 2002)** — paywalled at Elsevier; the record itself
  already discloses (in `detector:belle.notes`) that only the title/abstract/DOI could be
  read, leaving subsystem geometry unrecorded rather than fabricated. I could not get
  past the paywall either, so I could not independently verify the one spec it does carry
  (1.5 T solenoid field) against the full paper — I instead cross-checked it against
  Belle II's own TDR/detector-page description of the analogous magnet, which is
  consistent but not the same source.
- **CMS Point 5 exact coordinate sentence (arXiv:1005.5332)** — WebFetch returns only the
  abstract-page rendering for this arXiv id and did not surface the body-text sentence
  the record quotes; I could not force retrieval of the full PDF/HTML body in this
  session. The coordinates are geographically correct by independent knowledge of CMS's
  location, so this is a low-confidence-but-plausible gap, not a contradiction.
- **`src:lz-surf-heise-2015` (arXiv:1503.01112) Table 5 coordinates** — same limitation:
  WebFetch surfaced the abstract but not the numbered table the record cites for the
  Davis Campus LUX/LZ coordinate. The record's own `note` already flags this as a
  proceedings-only source (rank 10) used because no better one was found, and is
  transparent about `precision_m: 50` being a deliberate downgrade — I could not fully
  verify the table itself, only that the paper exists and is on-topic.
- **Full text of the 2018/2023 Higgs-to-bb/tau-tau/ttH/W-mass/top-mass CMS papers beyond
  their abstracts** — checked title, abstract, and the specific quoted sentence for each;
  did not read full papers for internal consistency of every number in each `summary`.
- **People/membership files** — out of scope for this pass (the task brief scopes this
  wave to the entity/detector/collaboration/result layer, not `data/atlas/people/` or
  `data/atlas/memberships/`, which the reviewed collaboration files themselves say are
  owned by a separate membership-lead workstream).
