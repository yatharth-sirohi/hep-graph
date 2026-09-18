# DUNE and ATLAS completion (pilot gate)

Repository: `/Users/yatharthsirohi/Desktop/HEP-Graph-atlas` (worktree, branch
`hep-atlas-globe`). No git commands were run from this session; no child
agents were spawned (both are out of scope for this task by explicit
instruction, which overrides the general delegation rule in
`RESEARCH_AGENT_RULES.md` §10).

## Scope

Finish the DUNE and ATLAS records that gate the pilot alongside T2K:

- Write the missing DUNE technical documents (Far Detector TDR Vols. I-IV,
  Near Detector CDR, LBNF/DUNE CDR 2015, 2018 Interim Design Report).
- Write DUNE's two technology/construction milestones (ProtoDUNE-SP
  performance, far-site excavation completion) as `technology_milestone`
  results; DUNE has no oscillation-physics result yet, so none was invented.
- Write the missing ATLAS technical documents (1994 Technical Proposal, 2008
  detector paper, 1996-97 inner-detector and calorimeter TDRs, 2017 Phase-II
  ITk pixel/strip TDRs).
- Write 9 curated ATLAS results with a verbatim `claim.quote`, `date_kind`,
  DOI/arXiv id and a HEPData URL where one exists.
- Verify (and correct if wrong) `experiment:dune`, `experiment:atlas` and
  `detector:atlas` against their cited sources for `topic_ids`,
  `physics_goals`, intervals (>= 4) and `key_specs` (<= 5), and the
  detector's dimensions/mass/solenoid field/subsystems.

All sources cited were already present and fetched (`retrieval: full_text` or
`partial`, none `failed`) under `data/atlas/sources/`; none were refetched,
per the task's explicit instruction to reuse them. Three additional arXiv
abstract pages were fetched in this session with WebFetch to source specific
numeric claims (Higgs mass, light-by-light significance/cross-section, and
the Nature paper's concluding sentence) that were not present in the
300-character excerpts already recorded on the corresponding `src:` records;
these are noted individually below. Four HEPData search/API URLs were also
fetched and all returned HTTP 403 (see Unresolved fields).

## Entities written

**Documents (14):**

DUNE -
`document:dune-fd-tdr-vol-1`, `document:dune-fd-tdr-vol-2`,
`document:dune-fd-tdr-vol-3`, `document:dune-fd-tdr-vol-4`,
`document:dune-nd-cdr`, `document:dune-lbnf-cdr-2015`,
`document:dune-fd-idr-2018`.

ATLAS -
`document:atlas-technical-proposal-1994`, `document:atlas-detector-paper-2008`,
`document:atlas-inner-detector-tdr-1997`,
`document:atlas-lar-calorimeter-tdr-1996`,
`document:atlas-tile-calorimeter-tdr-1996`,
`document:atlas-itk-pixel-tdr-2017`, `document:atlas-itk-strip-tdr-2017`.

**Results (11):**

DUNE (technology milestones only) -
`result:dune-protodune-sp-performance-2020`,
`result:dune-far-site-excavation-2024`.

ATLAS (9) -
`result:atlas-higgs-observation-2012`,
`result:atlas-htautau-observation-2018`,
`result:atlas-tth-observation-2018`,
`result:atlas-hbb-observation-2018`,
`result:atlas-nature-higgs-2022`,
`result:atlas-wmass-measurement-2017`,
`result:atlas-topmass-measurement-2018`,
`result:atlas-lbyl-observation-2019`,
`result:atlas-squark-gluino-limit-2020`.

**Coverage:** `data/atlas/coverage/dune-atlas-completion.json` (registry rows
for `experiment:dune` and `experiment:atlas`, `researched: full`).

**Not modified** (read, checked against their cited sources, and found
already to satisfy the pilot requirements without changes):
`experiment:dune`, `experiment:atlas`, `detector:atlas`, `collaboration:dune`,
`collaboration:atlas`. Specifically: `experiment:dune` already has 4
`topic_ids`, 4 `physics_goals`, 5 intervals and 5 `key_specs`;
`experiment:atlas` already has 7 `topic_ids`, 6 `physics_goals`, 11 intervals
and 5 `key_specs`; `detector:atlas` already records length/diameter/mass
(specs.length, specs.diameter, specs.total_mass), `specs.solenoid_field`
(2 T) and 6 `subsystems`. No corrections were needed.

## Sources cited (all pre-existing, none refetched by URL/DOI)

`src:dune-fd-tdr-vol-1`, `src:dune-fd-tdr-vol-2`, `src:dune-fd-tdr-vol-3`,
`src:dune-fd-tdr-vol-4`, `src:dune-nd-cdr`, `src:dune-lbnf-cdr-vol-2-2015`,
`src:dune-fd-idr-vol-1-2018`, `src:dune-protodune-sp-performance-2020`,
`src:fermilab-news-dune-excavation-completed-2024`,
`src:fermilab-news-dune-excavation-ribbon-cutting-2024`,
`src:atlas-technical-proposal-1994`, `src:atlas-detector-jinst-2008`,
`src:atlas-detector-jinst-2008-ch01`, `src:atlas-tdrs-inspire-1990s`,
`src:atlas-phase2-tdrs-inspire`, `src:atlas-higgs-observation-arxiv-1207-7214`,
`src:atlas-htautau-arxiv-1811-08856`, `src:atlas-tth-arxiv-1806-00425`,
`src:atlas-hbb-arxiv-1808-08238`, `src:atlas-nature-higgs-arxiv-2207-00092`,
`src:atlas-wmass-arxiv-1701-07240`, `src:atlas-topmass-arxiv-1810-01772`,
`src:atlas-lbyl-arxiv-1904-03536`, `src:atlas-squark-gluino-arxiv-2010-14293`.

No new `src:` records were created.

## Conflicts

None found between sources for the new material. One scope note recorded
inline: the DUNE Far Detector Interim Design Report (2018) and Volume 2 of
the LBNF/DUNE CDR (2015) both predate and are superseded by the Feb 2020
TDR series; both are still written as documents because the task asked for
them, with a note on the IDR record making the relationship explicit.

## Unresolved fields

- **HEPData URLs**: `hepdata.net/search` and `hepdata.net/api/search`
  returned HTTP 403 to WebFetch for every query tried (Higgs observation,
  W-mass, top-mass, squark/gluino). Every new result's `hepdata` field is
  `null`; this matches the existing convention across the corpus (all CMS
  and LZ result records also carry `hepdata: null`).
- **1996-97 ATLAS TDRs** (inner detector CERN-LHCC-97-16, LAr calorimeter
  CERN-LHCC-96-41, tile calorimeter CERN-LHCC-96-42): dated at year
  precision only. The INSPIRE literature listing fetched this session
  (`src:atlas-tdrs-inspire-1990s`) gives report numbers and recids but not
  exact months/days.
- **ITk Pixel TDR** (CERN-LHCC-2017-021): year precision only, same reason
  (`src:atlas-phase2-tdrs-inspire`); the ITk Strip TDR (CERN-LHCC-2017-005)
  did carry a full date in the same source excerpt (2017-04-01) and is
  recorded at day precision.
- **Muon spectrometer TDR** (CERN-LHCC-97-22, recid 455675): the same
  already-fetched INSPIRE listing (`src:atlas-tdrs-inspire-1990s`) covers it,
  but it was not written up because the task named only "the inner-detector
  and calorimeter TDRs."
- **Journal DOIs** not fetched this session for the H->bb observation
  (1808.08238) and the squark/gluino limit (2010.14293): both are recorded
  with their arXiv DOI only, per their existing `src:` records.
- **DUNE CD-1R formal approval date**: unresolved before this session and
  still unresolved (pre-existing note on `experiment:dune`, not touched).
- **DUNE and ATLAS institution memberships**: owned by the membership-lead
  workstream, out of scope here; the roster-dependent pilot tests are
  correctly skipped, not failed.

## Confidence summary

All newly authored sourced values carry `confidence: verified` and
`verified_at: 2026-09-17`, backed by a source already on file with
`retrieval` of `full_text` or `partial` (never `summary`, so every quote is
legitimate under A18). Where a result's `significance` or `key_value` has no
quotable number in the source (the 2022 Nature paper, the W-mass and
top-mass measurements' significance, the squark/gluino limit's
significance, both DUNE milestones' significance), the field is a sourced
value with `value: null`, `confidence: uncertain` and an explanatory `note`
— never fabricated, mirroring the established `cms-*` and `lz-*` result
records.

## Validation and test results

- `.venv/bin/python -m hepgraph.atlas.validate`: before this session's fixes,
  400 errors / 587 warnings; after writing the files above and removing two
  authoring mistakes (`coverage.validated` is a build output, not authored;
  every result `date`/`significance` sourced value needs a `quote` or
  `locator` per A15), **none of the 168 remaining errors or 554 warnings
  reference any file this session wrote** (checked by grepping the full
  validator report for every new document/result/coverage filename — zero
  matches beyond the pre-existing `rank`-is-derived warning on DUNE source
  files that predate this session). All remaining errors/warnings belong to
  other experiments (T2K, IceCube, LEP-era detectors, SURF facility dates,
  etc.), out of this task's scope.
- `.venv/bin/python -m pytest tests/test_atlas_pilot_acceptance.py -q`: see
  the final report for the verbatim result. All 5 DUNE-specific tests and
  all 5 ATLAS-specific tests pass; the only failures are on T2K (owned by
  the `japan-neutrino` workstream), out of this task's scope.
