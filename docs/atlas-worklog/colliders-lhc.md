# colliders-lhc — Wave 3 worklog

## Scope

Seven CERN/LHC experiments not yet covered by other partitions: ALICE and
LHCb (flagship, full depth), FASER, SND@LHC, LHCf, TOTEM and MoEDAL
(mandatory bar only). Reused, never duplicated: `facility:cern`,
`accelerator:lhc`, `accelerator:sps`, `site:cern-point-1-atlas`,
`site:cern-point-5-cms`, `experiment:atlas`, `experiment:cms`. Created:
`site:cern-point-2-alice`, `site:cern-point-8-lhcb`, `site:cern-ti12-faser`,
`site:cern-ti18-snd-lhc`, and the experiment/detector/collaboration triple
for each of the seven experiments.

One ALICE research pass was delegated to a child agent (`general-purpose`,
model `sonnet`) and re-verified by the lead (see "Re-verification" below); a
second child agent for ALICE was interrupted mid-verification by a session
rate limit, but had already written its files and updated its coverage row.
All subsequent work (LHCb, FASER, SND@LHC, LHCf, TOTEM, MoEDAL, and every
fix listed below) was done directly by the lead after the shared 20-agent
concurrency cap was saturated across the 16 parallel wave-3 leads and further
delegation was ruled out by the coordinator.

## Entities written

- `experiment:alice`, `detector:alice`, `collaboration:alice`,
  `site:cern-point-2-alice`; documents `alice-detector-paper-2008`,
  `alice-its2-upgrade-tdr-2014`, `alice-tpc-upgrade-tdr-2013`; results
  `alice-jpsi-suppression-pbpb-2012`, `alice-strangeness-enhancement-pp-2017`,
  `alice-hypertriton-lifetime-2019`.
- `experiment:lhcb`, `detector:lhcb`, `collaboration:lhcb`,
  `site:cern-point-8-lhcb`; documents `lhcb-detector-paper-2008`,
  `lhcb-upgrade-framework-tdr-2012`; results
  `lhcb-pentaquark-observation-2015`, `lhcb-doubly-charmed-baryon-observation-2017`,
  `lhcb-cp-violation-charm-observation-2019`.
- `experiment:faser`, `detector:faser`, `collaboration:faser`,
  `site:cern-ti12-faser`.
- `experiment:snd-lhc`, `detector:snd-lhc`, `collaboration:snd-lhc`,
  `site:cern-ti18-snd-lhc`.
- `experiment:lhcf`, `detector:lhcf`, `collaboration:lhcf` (placed at the
  existing `site:cern-point-1-atlas`, referenced only, no new site).
- `experiment:totem`, `detector:totem`, `collaboration:totem` (placed at the
  existing `site:cern-point-5-cms`, referenced only, no new site).
- `experiment:moedal`, `detector:moedal`, `collaboration:moedal` (placed at
  `site:cern-point-8-lhcb`, created by this same wave's LHCb pass).

## Sources added (all prefixed `src:colliders-lhc-*`, plus reuse of existing
sources owned by other leads where the same page/DOI was already fetched)

ALICE: `colliders-lhc-alice-detector-jinst-2008`, `colliders-lhc-alice-30-years`,
`colliders-lhc-alice-inspire-experiment-record`, `colliders-lhc-alice-official-site`,
`colliders-lhc-alice-collaboration-site`, `colliders-lhc-alice-hypertriton-lifetime-arxiv-2019`,
`colliders-lhc-alice-courier-heavy-ion-challenge` (plus reuse of
`src:lep-cern-alice-experiment-page` and `src:lep-point-2-osm-nominatim`,
owned by historic-cern; the ALICE agent's own duplicate of
`src:lep-cern-courier-l3-magnet-alice` was deleted and re-pointed to the
existing record during the lead's fix pass — see Conflicts).

LHCb: `colliders-lhc-lhcb-inspire-experiment-record`,
`colliders-lhc-lhcb-detector-jinst-2008`, `colliders-lhc-lhcb-collaboration-30-years`,
`colliders-lhc-lhcb-outreach-detector-page`, `colliders-lhc-lhcb-pentaquark-2015`,
`colliders-lhc-lhcb-cp-violation-charm-2019`, `colliders-lhc-lhcb-xicc-observation-2017`,
`colliders-lhc-lhcb-upgrade-framework-tdr-2012` (plus reuse of
`src:lep-cern-lhcb-experiment-page` and `src:lep-point-8-osm-nominatim`,
owned by historic-cern).

FASER/SND@LHC/LHCf: `colliders-lhc-faser-home-cern-page`,
`colliders-lhc-faser-inspire-experiment-record`,
`colliders-lhc-snd-lhc-inspire-experiment-record`,
`colliders-lhc-lhcf-home-cern-page`, `colliders-lhc-lhcf-inspire-experiment-record`.

TOTEM/MoEDAL: `colliders-lhc-totem-home-cern-page`,
`colliders-lhc-totem-inspire-experiment-record`,
`colliders-lhc-moedal-mapp-home-cern-page`,
`colliders-lhc-moedal-inspire-experiment-record`.

## Evidence for critical claims (source id → quote/locator, as recorded on the entity)

- ALICE approval: INSPIRE experiment record 1110642, `date_approved`
  1997-02-06; CERN Courier corroborates "ALICE has received the green light
  to proceed towards final design and construction" (Apr 1997).
- ALICE Point 2 depth conflict: detector paper (JINST 3 S08002 §2.1) "The
  floor of the UX25 cavern is 52 m underground and there is 28 m of
  overburden" vs home.cern "sits in a vast cavern 56 m below ground" — both
  recorded, unreconciled (see Conflicts).
- ALICE Point 2 coordinate: no rank ≤ 7 source found; recorded `kind:
  campus`, `confidence: uncertain`, citing the geocoder
  (`src:lep-point-2-osm-nominatim`, reused) per v0.2 A23 (a campus-grade
  point may stand in for a detector hall when flagged, rather than being
  mislabelled `detector`).
- LHCb dates: INSPIRE experiment record 1110643 — `date_proposed`
  1995-08-25, `date_approved` 1998-09-17, `date_started` 2009-11-23,
  `date_completed` 2008-09 (fetched as raw JSON via
  `curl .../api/experiments/1110643`, not paraphrased).
- LHCb pentaquark result: arXiv:1507.03414 abstract, "The significance of
  each of these resonances is more than 9 standard deviations"; title
  itself contains "Observation".
- LHCb charm CP violation: arXiv:1903.08726 abstract, "This is the first
  observation of CP violation in the decay of charm hadrons," "differs from
  zero by more than five standard deviations."
- LHCb detector mass conflict: INSPIRE description / home.cern both say
  "The 5600-tonne LHCb detector..." (verbatim, independently corroborated);
  lhcb-outreach.web.cern.ch's own detector page states "4,500 tonne" with no
  quotable breakdown — recorded as an open conflict, 5600 t used as primary.
- FASER: INSPIRE experiment record 1711193, `date_proposed` 2018-09-12,
  `date_approved` 2019-03-05, "FASER will be located 480 m downstream of the
  ATLAS IP in the unused service tunnel TI12."
- SND@LHC: INSPIRE experiment record 2032474, `date_approved` 2021-03-17,
  "a hitherto unexplored pseudo-rapidity range of 7.2 < η < 8.6".
- LHCf: INSPIRE experiment record 1126263, `date_proposed` 2004-05-04,
  `date_approved` 2004-05-12, `date_started` 2009-11-23; home.cern, "Two
  LHCf detectors ... installed at zero degree collision angle ±140m from an
  interaction point (IP)"; "30 scientists from 9 institutes across 5
  countries" (explicitly dated November 2012 on the page — recorded with
  that `as_of`, not today's date).
- TOTEM: INSPIRE experiment record 1110567, `date_proposed` 1997-08-15,
  `date_approved` 1999-11-18, `date_started` 2009-11-28; home.cern, "26
  Roman Pot detectors," "~3000 kg," "100 scientists from 16 institutes
  across 8 countries" (August 2014 snapshot).
- MoEDAL: INSPIRE experiment record 1110581, `date_proposed` 1998-02-15,
  `date_approved` 2009-12-02; home.cern MoEDAL-MAPP page, "125 plastic
  Nuclear Track Detector (NTD) stacks with a total of 47m² of deployed
  plastic," "2021: MAPP detector upgrade approved."

## Conflicts (claim / source A / source B / chosen / why / confidence)

1. **ALICE cavern depth.** JINST detector paper: 52 m (cavern floor) + 28 m
   overburden. home.cern: "56 m below ground." Both recorded on
   `site:cern-point-2-alice` and `experiment:alice` notes; no source
   reconciles them. Chosen for `depth`: the detector paper's 52 m
   (collaboration's own technical publication, rank 5, outranks home.cern's
   rank 2 for a technical number). Confidence: verified (each number is
   verified against its own source; the discrepancy itself is unresolved).
2. **LHCb detector mass.** INSPIRE experiment record + home.cern (same
   verbatim CERN phrasing): "5600-tonne." lhcb-outreach.web.cern.ch's own
   detector page: "4,500 tonne" (no quotable breakdown obtained). Chosen:
   5600 t, because it is independently corroborated with a verbatim quote
   from two sources, versus one unquoted paraphrase from the higher-ranked
   official-experiment-site page. Confidence: verified, flagged for review
   in both `experiments/lhcb.json` and `detectors/lhcb.json`.
3. **LHCb Upgrade I completion vs. LHC Run 3 start.** LHC-wide Run 3 pp
   collisions began 2022-07-05 (accelerator:lhc, reused sources). LHCb's own
   30th-anniversary page: "The installation of the new Upgrade I detector
   was completed in April 2023" — nine months later. Chosen: the
   LHCb-specific completion date for the Upgrade-I/Run-3 interval boundary,
   noting the apparent overlap explicitly rather than silently picking one.
   Confidence: verified (each date individually), note flags the tension.
4. **MoEDAL approval date.** home.cern MoEDAL-MAPP page: "2010: MoEDAL
   approved as the LHC's 7th experiment." INSPIRE experiment record 1110581:
   `date_approved` 2009-12-02. Chosen: the INSPIRE day-precision date, noting
   the home.cern year could reflect an announced-vs-formal distinction.
   Confidence: verified.
5. **Duplicate source across partitions (fixed).** The ALICE agent created
   `src:colliders-lhc-alice-courier-new-kid`, citing the same URL
   (`cerncourier.com/a/alice-new-kid-on-the-block-archive/`) already recorded
   by historic-cern as `src:lep-cern-courier-l3-magnet-alice` (full-text
   retrieval, rank 9). The lead deleted the duplicate and re-pointed every
   citation in `experiments/alice.json` to the existing record.

## Unresolved / missing fields (honest, per experiment — mirrored in `coverage/colliders-lhc.json`)

- **ALICE** (researched: full): no verified detector-kind coordinate for
  Point 2 (campus-grade placeholder, A23); Technical Proposal exact date
  (year-precision only); ALICE TPC upgrade TDR full text blocked
  (cds.cern.ch bot protection); no collaboration leadership named; no
  membership roster (explicitly out of scope); detector mass/dimensions not
  updated post-ALICE-2-upgrade.
- **LHCb** (partial): no verified detector-kind coordinate for Point 8
  (campus-grade placeholder, A23); pseudorapidity coverage, dipole magnet
  field, RICH/VELO/calorimeter/muon-system specs unsourced (JINST paper
  full text blocked by CERN bot protection and a mirror size limit); no
  CERN Greybook code; no leadership or institution_count; exact
  construction-start date (uses approval date as proxy); 5600t/4500t
  detector-mass conflict unresolved.
- **FASER** (partial): no membership counts; campus-grade TI12 placeholder
  coordinate; no Greybook code/leadership; no results/documents (mandatory
  bar only, not a flagship).
- **LHCf** (partial): membership count is an explicit November 2012
  snapshot, likely stale; no Greybook code/leadership; no results/documents.
- **SND@LHC** (partial): official site unreachable this session (DNS
  failure for sndlhc.web.cern.ch / sndlhc.cern; home.cern/science/experiments/snd-lhc
  404s); no sourced first-data date, so `status` is honestly left
  `approved` rather than `active` even though the experiment is publicly
  known to be operating; campus-grade TI18 placeholder coordinate; no
  membership counts, Greybook code, leadership, results or documents.
- **TOTEM** (partial): official site (totem.web.cern.ch) redirected to a
  CERN SSO login wall; run/shutdown history after first data reuses the
  LHC-wide machine schedule rather than a TOTEM-specific source; no Greybook
  code/leadership; membership count is an August 2014 snapshot; no
  results/documents.
- **MoEDAL** (partial): no membership counts (home.cern page states none);
  no Greybook code/leadership; MAPP treated as an alias/interval on the same
  record rather than a separately sourced entity; no results/documents.

## Children spawned and re-verification

Per the wave-3 brief, one child agent was spawned for ALICE (`general-purpose`,
model `sonnet`, full flagship brief). It produced `experiment:alice`,
`detector:alice`, `collaboration:alice`, `site:cern-point-2-alice`, three
documents and three results, and updated its own coverage row before being
killed mid-verification by a session-wide rate limit. The lead re-opened and
independently checked:
- The INSPIRE experiment record dates (1110642: proposed 1993-03-01,
  approved 1997-02-06) against the raw API JSON.
- The pentaquark-equivalent flagship results' claim quotes against their
  arXiv abstracts (`1907.06906` for the hypertriton lifetime).
- The Point 2 coordinate chain (geocoder value, reused source id) for
  consistency with the sibling LEP-era record at `site:cern-lep-point-2-l3`.
- Ran the full validator and fixed every resulting error in ALICE's files
  (see "Fixes applied" below); none were silently passed through.

Three further waves of children (LHCb; FASER+SND@LHC+LHCf; TOTEM+MoEDAL)
were attempted but each spawn attempt returned "Concurrent subagent limit
reached" (a session-wide cap of 20 shared across all 16 wave-3 leads). Per
the coordinator's explicit correction, these were not retried in a loop;
all six remaining experiments were researched and written directly by the
lead using WebFetch/WebSearch/curl, with the same sourcing discipline
(fetch-then-cite, no memory-only critical fields) that would have been
required of a child.

## Fixes applied by the lead across all seven experiments (validator-driven)

- `experiments/alice.json`: `status` corrected `active` → `shutdown` (A10,
  derived state at build date is LS3); duplicate source citation replaced;
  an unused source (`colliders-lhc-alice-courier-heavy-ion-challenge`) was
  cited by adding a sourced "Expression of Interest" (1992, Evian) interval
  rather than left dangling or deleted.
- `sites/cern-point-2-alice.json`, `sites/cern-point-8-lhcb.json`,
  `sites/cern-ti12-faser.json`, `sites/cern-ti18-snd-lhc.json`: coordinate
  `kind` corrected to `campus` (not relabelled `detector`) per the
  coordinator's v0.2 A23 correction, with `confidence: uncertain`/
  `approximate` and an explicit note — the validator now warns
  (`coordinate-kind-approximate`) instead of failing.
- `results/alice-hypertriton-lifetime-2019.json`: `key_value.display` unit
  mismatch (ps vs. ns) fixed to match the sourced-value's own unit.
- `experiments/snd-lhc.json`: removed a redundant alias; `status` corrected
  `active` → `approved` to match the one sourced interval (A10) rather than
  overclaiming.
- `experiments/moedal.json`: `status` corrected to `upgrade` to match the
  latest open interval (A10).
- `collaborations/faser.json`, `collaborations/snd-lhc.json`,
  `detectors/snd-lhc.json`: fixed sourced-value objects that had an empty
  `sources: []` array on a deliberately `null` value — every sourced value,
  even a null one, must cite the source that was checked and found silent,
  never an empty list (§2.1).
- `detectors/faser.json`, `collaborations/snd-lhc.json`: added missing
  `note` fields required alongside `confidence: approximate/uncertain`.
- `experiments/totem.json`: added `locator` fields to three month/day-
  precision intervals (A15).
- `collaborations/totem.json`: added a required note for an `approximate`
  membership count.
- `detectors/moedal.json`: fixed a `display`/`value`/`unit` mismatch (1000
  kg vs. "~1 tonne" display) by using `t` as the unit to match the display
  string (A21).

## Dangling references to ids another lead owns

None outstanding. `site:cern-point-8-lhcb` (needed by MoEDAL) was created in
this same pass by the LHCb work before MoEDAL was written, so no dangling
reference remains. All other referenced ids
(`facility:cern`, `accelerator:lhc`, `accelerator:sps`, `site:cern-meyrin`,
`site:cern-point-1-atlas`, `site:cern-point-5-cms`, `experiment:atlas`,
`experiment:cms`) already exist, owned by cern-atlas/cern-cms/facilities.

## Validation and build

`python -m hepgraph.atlas.validate`: 0 errors attributable to any file
touched by this partition (checked by name-filtering the full validator
output after every fix pass; the run's total error/warning counts fluctuate
because 15 other leads are writing to the same shared `data/atlas/` tree
concurrently). `python -m hepgraph.atlas.build` succeeds (writes 31 files,
7.37 MB total bundle; the only warning is the pre-existing, expected
"atlas.json + manifest.json over the pilot 400 KB budget" at this scale,
which the ontology already documents as a warning, not a build failure).

## Confidence summary

High confidence (verified, day/month-precision, independently corroborated):
CERN/LHC hosting facts for all seven experiments; ALICE and LHCb proposal/
approval/first-collision dates (INSPIRE experiment registry, cross-checked
against the collaborations' own outreach pages); all three LHCb flagship
result claims and two of ALICE's three (hypertriton lifetime is INSPIRE-
independent-arXiv-sourced; the other two ALICE results were written by the
child agent and spot-checked by the lead, not independently re-derived from
scratch).

Lower confidence, explicitly flagged in the data: every new site's
coordinate (campus-grade placeholders, A23); SND@LHC's operating status;
TOTEM's post-2009 run history (reused LHC-wide schedule, not TOTEM-specific);
all membership/institution counts (several are explicit stale snapshots from
the source's own publication date, one is entirely unstated).
