# flagship-depth — research log

## Scope

Wave-3 flagship-depth pass (addendum) over 11 flagships: ATLAS, CMS, DUNE,
Super-Kamiokande, Hyper-Kamiokande, T2K, NOvA, IceCube, Belle II, LZ, JUNO.
Session was resumed once mid-task (a coordinator message reported the prior
run had hit the subagent/session limit); this log reflects the resumed
session's audit of what was already on disk plus the new work done in it. No
subagents were spawned (concurrency cap saturated per the brief; all research
was done directly, sequentially, respecting the ≤1 request/10s inspirehep.net
etiquette). No git commands were run.

**JUNO: not touched.** `docs/atlas-worklog/reactor-solar-neutrino.md` (the
owning lead's worklog) exists but is explicitly mid-run — it ends "*(Log
continues below as Borexino, GALLEX/GNO, SAGE and Homestake are completed.)*"
— so per the brief's explicit instruction ("do NOT edit JUNO's files if that
lead's worklog is absent or still in progress; report instead") JUNO's files
were left alone. For the record, JUNO already has full flagship depth on
disk: `experiment:juno`, `detector:juno`, `facility:juno-jiangmen`,
`site:juno-jiangmen-underground-lab`, `collaboration:juno`, 2 documents
(`document:juno-cdr` 2015 CDR arXiv:1508.07166, `document:juno-physics-and-detector`
2021 review arXiv:2104.02565) and 2 results (`result:juno-oscillation-parameters-2026`,
`result:juno-initial-performance-2026`), with an honest coverage row
(`data/atlas/coverage/reactor-solar-neutrino.json`, `researched: "partial"`,
missing_fields listing the unresolved underground coordinate precision,
collaboration formation date, leadership, membership counts and a
title-matching TDR).

## Audit of prior-session state (before any new edits)

The 10 non-JUNO flagships were already close to or at the mandatory+full-depth
bar from earlier work in this worktree (confirmed by reading every results/
documents file and grepping owner_ids/experiment_ids, not from memory):

| experiment | results (before) | documents (before) | key_specs (before) |
| --- | --- | --- | --- |
| ATLAS | 9 | 7 | 5 |
| CMS | 10 | 9 | 5 |
| DUNE | 2 (both technology_milestone, correctly labelled) | 7 | 5 |
| Super-Kamiokande | 3 | 1 | 4 |
| Hyper-Kamiokande | 0 (under construction — correct, not a gap) | 1 | 4 |
| T2K | 3 | 2 | **0 (missing)** |
| NOvA | 1 | 1 | 5 |
| IceCube | 8 | 2 (owned by `experiment:icecube`; 3 more "icecube-*"-named docs exist but are owned by `experiment:icecube-gen2`/`experiment:icecube-upgrade`, correctly not counted here) | 5 |
| Belle II | 2 | 2 (TDR `document:belle-ii-tdr-2010` already exists) | 4 |
| LZ | 2 (TDR + CDR + detector paper already exist, 3 documents) | 3 | 5 |

ATLAS, CMS, DUNE, Hyper-Kamiokande, IceCube and LZ already met the brief's bar
(2–4 results where physics results exist; documented absence where they
don't) and needed no new results or documents — only a coverage-row audit.
**CMS had no coverage row at all** (see below) despite the entity being fully
researched; this was the one real gap found outside NOvA/Super-K/T2K/Belle II.

## Entities written / changed this session

**New results** (each with `claim.quote` verbatim from the title/abstract or
the collaboration's own result page, `date`, `date_kind`, `experiment_ids`,
`sources`):

- `result:nova-t2k-joint-oscillation-analysis-2025` — "Joint neutrino
  oscillation analysis from the T2K and NOvA experiments", Nature 646,
  818-824 (2025), arXiv:2510.19888. `result_type: measurement`.
  `experiment_ids: [experiment:nova, experiment:t2k]` (attributed to both;
  it is a genuinely joint collaboration paper). Quote: *"Here, we carry out
  the first joint analysis of data sets from NOvA and T2K, the two currently
  operating long-baseline neutrino oscillation experiments..."* Brings NOvA
  to 2 results (2022 PRD + this).
- `result:sk-dsnb-limit-2025` — "Search for Diffuse Supernova Neutrino
  Background with 956.2 days of Super-Kamiokande Gadolinium Dataset",
  arXiv:2511.02222 (Nov 2025, accepted ApJ). `result_type: limit`.
  Quote: *"No significant excess over background predictions was found in a
  DSNB spectrum-independent analysis, and 90% C.L. upper limits on the
  astrophysical electron anti-neutrino flux were set."* Brings Super-K to 4
  results (1998 atmospheric-oscillation evidence, 2023 SK-Gd first
  astrophysical-antineutrino search, 2024 solar-neutrino precision
  measurement, this 2025 DSNB limit) — matching the brief's explicit list.
- `result:belle-ii-vcb-measurement-2025` — "Determination of |Vcb| using
  B→Dℓνℓ Decays at Belle II", arXiv:2506.15256, Phys. Rev. D 112, 112009
  (2025). `result_type: precision_measurement`. Quote: *"we obtain |Vcb| =
  (39.2 ± 0.4 (stat.) ± 0.6 (sys.) ± 0.5 (th.)) × 10^-3"*. Brings Belle II to
  3 results (2023 B→Kνν̄ evidence — already correctly worded "evidence", not
  "observation" — 2023 τ-mass measurement, this 2025 |Vcb| measurement).

**New sources** (`src:flagship-depth-*`, grepped `data/atlas/sources/` first
for the same URL/DOI/arXiv id in every case — none existed):

- `src:flagship-depth-nova-inspire-experiment` — INSPIRE experiment record
  https://inspirehep.net/experiments/1108441 (`source_type:
  inspire_experiment_record`, rank 3).
- `src:flagship-depth-nova-t2k-joint-2025` — arXiv:2510.19888 (rank 10).
- `src:flagship-depth-sk-dsnb-2025` — arXiv:2511.02222 (rank 10).
- `src:flagship-depth-belle2-vcb-2025` — arXiv:2506.15256 (rank 10).

**Experiment edits:**

- `experiment:nova`: added `external.inspire_experiment: 1108441`, cited
  by the new INSPIRE source (record-level `sources`, per A20). Removed a
  now-stale note that said no INSPIRE lookup had been performed. Found the
  recid via `inspirehep.net/api/experiments?q=nova%20fermilab` → legacy_name
  `FNAL-E-0929`, confirmed by fetching `inspirehep.net/api/experiments/1108441`
  (name "NOvA: Numi off-axis Neutrino Appearance Experiment", collaboration
  NOvA, institution Fermilab).
- `experiment:t2k`: added 4 `key_specs` (previously the field was entirely
  absent), all quoted from the already-on-disk `src:t2k-nim-2011` (NIM A 659
  (2011) 106-135, arXiv:1106.1238, `retrieval: full_text`) — re-fetched the
  arXiv PDF and extracted verbatim table/sentence text with `pdftotext`:
  - Baseline: 295 km. Quote: *"The measured distance between the target and
    the center position of Super-Kamiokande is 295,335.2 +- 0.7 m."*
  - Off-axis angle: 2.5° (2.504° measured). Quote: *"The measured off-axis
    angle is 2.504 +- 0.004 deg."*
  - ND280 magnet field: 0.2 T. Quote: *"The ND280 off-axis detector is built
    around the old CERN UA1/NOMAD magnet providing a dipole magnetic field of
    0.2 T, to measure momenta with good resolution and determine the sign of
    charged particles produced by neutrino interactions."* (§4.3.1 "UA1
    Magnet")
  - Beam power (design): ~750 kW. Quote: *"Beam power ∼750 kW"* (Table 1,
    "Machine design parameters of the J-PARC MR for the fast extraction").

**Coverage rows updated** (all `researched: "full"`, `missing_fields` kept
honest — nothing invented):

- `data/atlas/coverage/fermilab-neutrino-other.json` (NOvA): notes updated
  for the 2nd result and the new `external.inspire_experiment`; added an
  explicit `missing_fields` entry documenting that a standalone NOvA
  detector/NIM paper was searched for and not found (see Conflicts below).
- `data/atlas/coverage/japan-neutrino.json` (Super-Kamiokande, T2K,
  Hyper-Kamiokande): Super-K notes updated to 4 results; T2K notes updated
  for the 4 new key_specs; Hyper-Kamiokande notes/missing_fields made
  explicit that zero results is a fact about construction status, not an
  omission.
- `data/atlas/coverage/flavor.json` (Belle II): notes updated to 3 results.
- `data/atlas/coverage/cern-cms.json` (**new file** — CMS had no coverage
  row anywhere in `data/atlas/coverage/`, confirmed by grepping every file
  for `"experiment:cms"`; ID_REGISTRY assigns `experiment:cms` etc. to owner
  `cern-cms`, and no such coverage file existed). Added the missing registry
  row (`researched: "full"`, `tier: "A"`) describing the entity's already-full
  state (10 results, 9 documents, 5 key specs, `external.inspire_experiment
  = 1108642`) without touching the entity files themselves, since they were
  already correct.
- ATLAS and DUNE (`data/atlas/coverage/dune-atlas-completion.json`) and LZ
  (`data/atlas/coverage/dark-matter.json`) and IceCube
  (`data/atlas/coverage/icecube.json`) were read and cross-checked against
  their entity files but **not edited** — their existing rows were already
  accurate (`researched: "full"`, honest `missing_fields`, correct result/
  document counts) and needed no correction.

## Sources added

`src:flagship-depth-nova-inspire-experiment`,
`src:flagship-depth-nova-t2k-joint-2025`, `src:flagship-depth-sk-dsnb-2025`,
`src:flagship-depth-belle2-vcb-2025`. All four were fetched live in this
session (WebFetch/WebSearch→WebFetch); the INSPIRE fetches respected the
≤1 request/10 s etiquette (interleaved with non-INSPIRE fetches and separated
by multi-second tool round-trips).

## Conflicts / gaps found

- **NOvA NIM detector paper not found.** The brief asked to add "the NOvA
  NIM detector paper" alongside the existing TDR. I searched INSPIRE
  literature (`collaboration NOvA AND title detector`, and author-scoped
  queries) and `novaexperiment.fnal.gov/publications/` and found only
  subsystem/component papers — "Liquid scintillator production for the NOvA
  experiment" (NIM A 799 (2015) 1, arXiv:1504.04035), "The NuMI Neutrino
  Beam" (NIM A 806 (2016) 279, arXiv:1507.06690, which is a beamline paper,
  not a detector paper), and the "Library Event Matching" algorithm paper
  (NIM A 778 (2015) 31) — plus the 2007 TDR (already on file as
  `document:nova-tdr`). No standalone refereed paper titled anything like
  "The NOvA Detector" turned up. Per A17 (no fabrication), I did not create a
  document record mislabelling one of these as the general NOvA detector
  paper; the gap is recorded honestly in NOvA's `missing_fields` instead.
- **Super-Kamiokande coverage row was already overclaiming before this
  session.** `data/atlas/coverage/japan-neutrino.json` said "4 results
  recorded" for Super-K while only 3 result files existed on disk
  (`sk-atmospheric-oscillation-evidence-1998`, `sk-gd-first-antineutrino-search-2023`,
  `sk-solar-neutrino-measurement-2024`). Adding `result:sk-dsnb-limit-2025`
  in this session makes the claim true rather than correcting the count
  downward; noted here since it is exactly the kind of under/over-claim the
  brief asks leads to watch for.
- **`result.key_value` unit mismatches (self-caught, fixed before validating).**
  My first draft of the NOvA-T2K and Belle-II |Vcb| results used `key_value`
  (a Quantity) with units (`eV^2`, dimensionless `""`) that are not in the
  ontology's dimension whitelist (§2.4 has no eV² or bare-ratio unit); the
  validator would have failed both (`A21` factor-mismatch and unknown-unit
  errors — caught locally before running the validator once I noticed the
  precedent). Both were moved to `key_value_text` instead, matching the
  existing pattern already used by `result:nova-oscillation-parameters-2022`
  for the same class of multi-parameter/dimensionless result.

## Unresolved fields

- NOvA: no standalone detector/NIM paper (see Conflicts); collaboration
  formation date and leadership remain unsourced (pre-existing gap, not
  addressed this session — out of scope: leadership/formation dates were not
  on this session's priority list and no new source was fetched for them).
- Super-Kamiokande, Hyper-Kamiokande, T2K: collaboration leadership
  (spokesperson) remains unsourced (pre-existing gap).
- Belle II, LZ: institution-roster / membership fields remain owned by
  membership-lead and untouched, per the brief's explicit "do not write
  people/ or memberships/" instruction.
- CMS: HEPData record URLs and collaboration leadership remain unsourced
  (pre-existing gap on the entity file, not touched this session since the
  entity itself was already correct — only the missing coverage row was
  added).

## Children spawned

None. The brief's concurrency cap was reported saturated by the coordinator
before this session resumed ("No git; no subagents"), so all research in
this session was performed directly and sequentially.

## Validation and build

- `python -m hepgraph.atlas.validate`: **0 errors** across the whole
  `data/atlas/` tree at the end of this session (1589 pre-existing warnings,
  4 informational, none newly introduced by this session's files — checked
  by grepping the validator output for every touched file/id after each
  edit). The only findings on my own new/edited files are the same
  `rank-is-derived` informational-style warning that every other source file
  in the repository already carries (A1: `rank` is written but ignored at
  build time; kept for human readability, consistent with existing
  convention).
- `python -m hepgraph.atlas.build`: succeeds; wrote 31 bundle files
  (`atlas.json` + `manifest.json` = 1,425,364 bytes, over the 400 KB pilot
  budget — a pre-existing, repository-wide warning per the ontology doc's
  own note that this is "now a warning threshold rather than a target",
  unrelated to this session's changes).

## Confidence summary

High confidence on every new sourced value: all four new sources were
fetched live in this session (three via WebFetch of the arXiv abstract page,
one via the INSPIRE experiments API, plus a `pdftotext` extraction of the
already-cited T2K NIM paper's full PDF for the T2K key_specs quotes), and
every `claim.quote` above is verbatim from the abstract/title or the cited
table, ≤300 characters, checked by re-reading the fetched text myself (not
delegated to a child, since none was spawned). The one deliberately
low-confidence area is the missing NOvA detector paper, which is reported as
absent rather than guessed. CMS's underlying entity data was reviewed but
not independently re-verified line-by-line in this session (it was already
present and internally consistent, e.g. `external.inspire_experiment:
1108642`, 5 key specs, working `links.website`); only the missing coverage
row was added.

## Per-experiment before → after depth table (results / documents / key_specs)

| experiment | before | after | action |
| --- | --- | --- | --- |
| ATLAS | 9/7/5 | 9/7/5 | none needed; coverage row already accurate |
| CMS | 10/9/5 | 10/9/5 | added missing coverage row only (`cern-cms.json`) |
| DUNE | 2/7/5 | 2/7/5 | none needed; both results already labelled `technology_milestone` |
| Super-Kamiokande | 3/1/4 | **4**/1/4 | added 2025 DSNB limit result |
| Hyper-Kamiokande | 0/1/4 | 0/1/4 | none invented; coverage row made explicit that 0 is correct |
| T2K | 3/2/0 | 3/2/**4** | added 4 key_specs (baseline, off-axis angle, ND280 field, beam power) |
| NOvA | 1/1/5 | **2**/1/5 | added joint NOvA-T2K 2025 result + `external.inspire_experiment`; NIM detector paper searched for and not found |
| IceCube | 8/2/5 | 8/2/5 | none needed; verified the 2017 JINST paper is correctly owned by `experiment:icecube` |
| Belle II | 2/2/4 | **3**/2/4 | added 2025 |Vcb| measurement |
| LZ | 2/3/5 | 2/3/5 | none needed; WS2024 result and TDR/CDR/detector-paper docs already present and correctly worded |
| JUNO | (full, untouched) | (full, untouched) | not edited — owning lead's worklog is still in progress |
