# Muons workstream worklog (Wave 3, v1.0)

Owner slug: `muons`. Session date: 2026-09-17. No git operations were performed
(per instructions); this workstream touched only `data/atlas/` and this file.

## Scope

Six experiments from `data/atlas/coverage/muons.json`:

- **Muon g-2** (Fermilab E989) -- flagship, full depth.
- **Mu2e** (Fermilab) -- flagship, full depth except results (none exist yet).
- **MEG** (PSI) -- mandatory bar + one exception result (2016 final limit).
- **MEG II** (PSI) -- mandatory bar + one exception result (2024 first-dataset limit).
- **Mu3e** (PSI) -- mandatory bar, no result (still under construction).
- **COMET** (J-PARC Hadron Experimental Facility) -- mandatory bar, no result.

**Process note:** the Agent tool's concurrent-subagent budget was exhausted by
other Wave-3 leads for the entire session (every `Agent` call returned
"Concurrent subagent limit reached", including on retry). Per the
coordinator's correction, no children were spawned; all research (WebFetch/
WebSearch, plus a handful of direct INSPIRE-HEP `api/experiments` and
`api/literature` lookups and OpenStreetMap Nominatim geocoder queries) was
done directly by this lead, sequentially. WebSearch's session-wide quota was
also exhausted partway through (200/200 calls used across all leads); the
remainder of the research relied on WebFetch to specific arXiv, INSPIRE-HEP,
official-site and Nominatim URLs.

## Entities written

**Sites** (`data/atlas/sites/`): `fermilab-mc-1-muon-campus.json`,
`fermilab-mu2e-hall.json`, `j-parc-hadron-hall.json` (the last owned by this
workstream per the Wave-3 ID registry specifically so the `fixed-target` lead
can reference it for KOTO).

**Experiments**: `muon-g-2.json`, `mu2e.json`, `meg.json`, `meg-ii.json`,
`mu3e.json`, `comet.json`.

**Detectors**: `muon-g-2.json`, `mu2e.json`, `meg.json`, `meg-ii.json`,
`mu3e.json`, `comet.json`.

**Collaborations**: `muon-g-2.json`, `mu2e.json`, `meg.json`, `meg-ii.json`,
`mu3e.json`, `comet.json`.

**Documents**: `muon-g-2-tdr.json` (arXiv:1501.06858), `mu2e-tdr.json`
(arXiv:1501.05241), `comet-phase1-tdr.json` (arXiv:1812.09018).

**Results** (flagship/exception depth only, per the brief): `muon-g-2-measurement-2021.json`,
`muon-g-2-measurement-2023.json`, `muon-g-2-measurement-2025.json`,
`meg-mu-to-e-gamma-limit-2016.json`, `meg-ii-mu-to-e-gamma-limit-2024.json`.

**Coverage**: `data/atlas/coverage/muons.json` rewritten with honest
`researched`/`missing_fields` per experiment (see table below).

## Sources added (24, all prefixed `src:muons-`)

| id | type | rank | what it supports |
| --- | --- | --- | --- |
| `muons-inspire-experiment-muon-g2` | inspire_experiment_record | 3 | recid 1108252, name, description |
| `muons-arxiv-2104-03281` | arxiv | 10 | 2021 result title/abstract/quote |
| `muons-arxiv-2308-06230` | arxiv | 10 | 2023 result title/abstract/quote |
| `muons-arxiv-2506-03069` | arxiv | 10 | 2025 final result, full verbatim abstract |
| `muons-arxiv-1501-06858` | design_report | 4 | Muon g-2 TDR, BNL E821 lineage quote |
| `muons-arxiv-1411-2555` | arxiv (full_text via ar5iv) | 10 | storage ring 7.112 m radius / 1.45 T field, verbatim |
| `muons-news-fnal-2025-final-result` | press_release | 9 | Run 1-6 dates, startup date, ring relocation, collaboration size |
| `muons-nominatim-fermilab` | geocoder | 8 | MC-1 / Mu2e Hall campus-level coordinates |
| `muons-inspire-experiment-mu2e` | inspire_experiment_record | 3 | recid 1108209, full description, date_proposed/date_approved |
| `muons-inspire-lit-mu2e-status-2022` | journal_article | 10 | 3x10^-17 single-event-sensitivity quote |
| `muons-inspire-lit-mu2e-status-2026` | journal_article | 10 | "initial data collection scheduled to begin in 2027", 25 m solenoid quote |
| `muons-arxiv-1501-05241` | design_report | 4 | Mu2e TDR |
| `muons-arxiv-1605-05081` | arxiv | 10 | MEG 2016 final limit, verbatim |
| `muons-arxiv-2310-12614` | arxiv | 10 | MEG II 2024 limit, verbatim |
| `muons-inspire-experiment-meg` | inspire_experiment_record | 3 | recid 1108527 |
| `muons-inspire-experiment-meg-ii` | inspire_experiment_record | 3 | recid 1679100, 6x10^-14 sensitivity goal quote |
| `muons-inspire-experiment-mu3e` | inspire_experiment_record | 3 | recid 1114537, 10^-16 sensitivity goal quote, HV-MAPS |
| `muons-inspire-experiment-comet` | inspire_experiment_record | 3 | recid 1108246 |
| `muons-psi-mu3e-site` | official_experiment_site | 1 | third pixel layer installed 2026-09-16 |
| `muons-meg-icepp-site` | official_experiment_site | 1 | MEG/MEG II detector description |
| `muons-comet-official-site` | official_experiment_site | 1 | 290+ researchers/48 institutes, CM48 meeting July 2026 |
| `muons-arxiv-1812-09018` | design_report | 4 | COMET Phase-I TDR, sensitivity goal quote |
| `muons-jparc-hadron-facility-page` | official_facility_site | 2 | Hadron Facility identity/description |
| `muons-nominatim-jparc` | geocoder | 8 | J-PARC campus-level coordinate (shared form with the existing `site:j-parc-main-ring` record) |

## Conflicts

| claim | source A | source B | chosen | why | confidence |
| --- | --- | --- | --- | --- | --- |
| Mu2e single-event sensitivity | INSPIRE experiment record 1108209 (rank 3): "about 2.5 x 10^-17" | 2022 Mu2e status proceedings, PoS EPS-HEP2021 557 (rank 10): "an unprecedented single event sensitivity of 3x10^-17" | 2.5x10^-17, as `key_specs` primary value | Rank 3 (experiment_registry-class record) outranks rank 10 (conference proceedings) in the source hierarchy; the 3x10^-17 figure is noted alongside as a later, staged-plan (Run1+Run2) projection rather than treated as an error | verified (primary value), both quotes preserved in the `note` |
| Mu2e status/schedule | INSPIRE experiment record 1108209: "Commissioning is scheduled to begin in 2020" | 2026-07 status proceedings (PoS WIFAI2025 020): "initial data collection scheduled to begin in 2027" | 2027, from the 2026 source | The INSPIRE experiment record's own description text is a static snapshot last meaningfully updated around the 2016 CD-3 approval and is now ~6 years stale on schedule; the 2026 source is the most recently dated status statement fetched. The INSPIRE record is still used for the historical proposed/approved/CD-3 dates, which it is not stale on. | verified |
| NOvA-style TDR-anchored lower bound (methodology conflict, not a factual one) | COMET's construction interval had `start: null` (true "unknown"), which the validator's A10 state-derivation treats as never covering any date, producing a `status-not-derived-state` error against the authored `status: "construction"` | -- | Anchored `start` to `2018` (Phase-I TDR publication, arXiv:1812.09018), the earliest dated evidence of the Phase-I programme found this session, `confidence: "approximate"`, with a note that this is a lower bound and not a stated construction-start date | Matches the precedent set by `collaboration:nova`'s TDR-anchored formation interval (same technique, same caveat) | approximate |

## Unresolved fields (left `null`+note rather than guessed)

- All six collaborations' `formation` dates: no source fetched this session states one.
- Muon g-2 and Mu2e results/key-specs: no single significance-vs-Standard-Model sigma figure for the 2023/2025 g-2 papers (the 2025 result's relationship to the Standard Model prediction is contested in the literature in ways not resolved by the abstract alone; left null rather than asserted).
- MEG, MEG II, Mu3e, COMET collaboration membership counts (institution/country/member counts): not stated in any source fetched this session (COMET's own site was the one exception, with 290+ researchers / 48 institutes).
- Precise (rank <= 7) coordinates for MC-1, the Mu2e Hall and the J-PARC Hadron Hall: `fnal.gov`/`muon.fnal.gov` returned HTTP 403/404 to every attempted fetch, and `mu2e.fnal.gov` returned HTTP 403; no J-PARC page fetched stated Hadron-Hall-specific coordinates. All three sites are recorded as `kind: campus`, `confidence: approximate`, sourced to an OpenStreetMap Nominatim landuse-polygon/amenity-node lookup performed in this session, with the limitation stated plainly in each site's own `notes`.
- Muon g-2's 2014-08 to 2017-04 interval gap (ring installation and magnetic-field mapping at Fermilab): no fetched source gave a dated, sourceable status for this period; left as a genuine gap (flagged by the validator as an `hull-gap` warning) rather than invented.
- BNL E821 lineage for Muon g-2, and the MECO lineage for Mu2e: recorded as sourced prose notes only, not as structured `lineage` rows, because the target ids (`experiment:bnl-e821`, a MECO id) belong to a different Wave-3 owner (`facilities`, for BNL) or do not exist/are out of scope at all (MECO).

## Children spawned

**None.** The Agent tool returned "Concurrent subagent limit reached" on every
attempt (the session-wide cap of 20 concurrent subagents was saturated by
other Wave-3 leads' own children throughout this session), and the
coordinator's correction explicitly said not to retry or wait, but to do the
research directly and sequentially instead. Every claim in every file listed
above was therefore fetched and checked by this lead itself, not delegated
and re-verified after the fact -- there was no second pass because there was
no first pass by anyone else.

## Dangling references (ids owned by other Wave-3 leads, not yet landed)

- `facility:psi`, `site:psi-villigen`, `accelerator:psi-hipa` -- owned by the
  `facilities` workstream. Referenced by `experiment:meg`, `experiment:meg-ii`,
  `experiment:mu3e` (facility_roles / accelerator context), their detector
  `placements`, and their collaborations' `host_facility_id`/`host_site_id`.
  Expected per the Wave-3 ID registry; not fixed by creating a competing
  `facility:psi` record.

## Confidence summary

- **Muon g-2**: high confidence on every critical field actually populated
  (storage ring diameter/field, all three result titles and the 127 ppb
  final value, Run 1-6 dates, BNL E821 relocation date) -- all quoted
  verbatim from the collaboration's own papers or Fermilab's own press
  release. Lower confidence / explicitly flagged: MC-1's coordinate (campus
  approximate only), the 2014-2017 interval gap, and the absence of a
  collaboration formation date.
- **Mu2e**: high confidence on the TDR, the solenoid-system length, the
  proposed/approved/CD-3 dates (all from the INSPIRE experiment record's own
  dated metadata fields) and the "no results yet" state (independently
  confirmed by two status papers three years apart, 2022 and 2026, neither of
  which reports data-taking as begun). Lower confidence: the exact
  single-event-sensitivity figure (two collaboration-sourced values exist,
  2.5x10^-17 and 3x10^-17; both recorded, primary chosen by source rank) and
  the Mu2e Hall coordinate (campus approximate).
- **MEG / MEG II**: high confidence on both branching-ratio limits (verbatim
  from the collaboration's own papers) and on MEG's 2009-2013 run dates.
  Lower confidence: collaboration formation dates and membership counts, not
  found for either.
- **Mu3e**: moderate confidence -- the physics goal and HV-MAPS technology
  are from INSPIRE's own experiment-record description; the only dated status
  evidence found is a single-sentence pixel-layer-installation update from
  the official site, one day before this session's `verified_at`.
- **COMET**: moderate confidence -- the TDR's sensitivity goal and detector
  design (CyDet/StrECAL) are solid; the current-status/interval dating is the
  weakest of the six records in this file, honestly reflected in
  `confidence: "approximate"` and an explicit note on the anchoring choice
  (TDR year as a lower bound, not a stated construction-start date).

## Validation and build

- `python -m hepgraph.atlas.validate`: re-run after fixes. Zero errors
  attributable to this workstream's files. Fixed during this session: an
  alias duplicating its own record's name (`experiment:meg-ii`), a duplicate
  alias under normalisation (`site:fermilab-mc-1-muon-campus`'s "MC1"/"MC-1"),
  six `collaboration.formation` values and two `result.significance` values
  missing a required `locator`, an invalid `publisher_id` (an experiment id)
  on six INSPIRE-experiment-record sources, two `display`/`value` unit-parsing
  mismatches in `key_specs` quantities (a stray "%" in COMET's display string
  was mis-parsed as its unit; Mu3e's bare "10^-16" display lacked the
  mantissa the parser needs), and a `status-not-derived-state` error on all
  three COMET records caused by an unbounded (`start: null`) construction
  interval, fixed by anchoring the interval to the Phase-I TDR's 2018
  publication date as an explicit approximate lower bound. Remaining
  findings that reference this workstream's files are the expected
  `facility:psi`/`site:psi-villigen` dangling references, the `A23`
  campus-grade-coordinate warnings on all three of this workstream's sites
  (self-documented, not an error), an honest 33-month hull-gap warning on
  Muon g-2, an `experiment-without-active-beam` warning on MEG II (its beam
  source, `accelerator:psi-hipa`, is a dangling reference), and
  `sites-too-close` warnings where this workstream's campus-approximate
  Fermilab/J-PARC points coincide with other leads' similarly-approximate
  points for the same two facilities.
- `python -m hepgraph.atlas.build`: succeeds, writes 31 files to
  `static/atlas/generated/` (the only warning is the whole-atlas
  `atlas.json`+`manifest.json` size budget, a pilot-wide figure driven by
  every Wave-3 lead's combined output, not specific to this workstream).
