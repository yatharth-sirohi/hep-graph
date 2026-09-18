# cevns — Wave 3 worklog

## Scope

Four experiments from `data/atlas/coverage/cevns.json`: COHERENT (flagship, full
depth), CONUS (mandatory bar), NUCLEUS (mandatory bar), Ricochet (mandatory
bar). Per WAVE3_LEAD_BRIEF.md and ID_REGISTRY.md's Wave 3 `cevns` row.

**Delegation note:** the brief calls for delegating three children (COHERENT;
CONUS; NUCLEUS+Ricochet). Every `Agent` call to spawn a child failed with
"Concurrent subagent limit reached" (a session-wide cap of 20 shared across all
16 wave-3 leads). The orchestrator/coordinator confirmed mid-task: do not loop
retrying, research sequentially myself instead, at most 2 children when
capacity exists, and never stop with nothing written. Capacity never freed up
during this run, so **no children were spawned**; all research (WebFetch/
WebSearch), source citation and file-writing below was done directly by this
lead agent, one experiment at a time. Every claim is still sourced to a page
fetched in this session — the self-check that would normally apply to a
child's output was applied to my own drafts (re-reading the ontology/schema
constraints and re-running the validator after every batch of files).

## Entities written

**COHERENT** (flagship, full depth):
- `experiments/coherent.json` — kind `cevns`, status `active`
- `detectors/coherent-csi.json` (CsI[Na], 14.6 kg, decommissioned)
- `detectors/coherent-cenns-10.json` (LAr, 22 kg, active)
- `detectors/coherent-ge.json` (Ge-Mini, 8×2.2 kg = 17.6 kg, active)
- `detectors/coherent-nai.json` (NaI[Tl], 185 kg initial array, active)
- `collaborations/coherent.json` (formed 2013, 21 institutions/4 countries)
- `results/coherent-observation-2017.json` ("Observation of Coherent Elastic
  Neutrino-Nucleus Scattering", 6.7σ)
- `results/coherent-argon-measurement-2021.json` ("First Measurement of
  Coherent Elastic Neutrino-Nucleus Scattering on Argon")
- `results/coherent-csi-cross-section-2022.json` ("Measurement of the
  Coherent Elastic Neutrino-Nucleus Scattering Cross Section on CsI by
  COHERENT")
- `results/coherent-germanium-evidence-2024.json` ("Evidence of Coherent
  Elastic Neutrino-Nucleus Scattering with COHERENT's Germanium Array", 4th
  result, added since COHERENT is a flagship with time for the 2-4 range)
- `documents/coherent-proposal-2015.json` (arXiv:1509.08702, technical_proposal)
- 9 `sources/cevns-coherent-*.json` + reused/updated `src:topic-coherent-2017-cevns-observation`

References without creating (dangling, owned by `facilities`): `facility:oak-ridge-national-laboratory`, `site:ornl-sns-neutrino-alley`, `accelerator:sns`.

**CONUS** (mandatory bar):
- `experiments/conus.json` — kind `cevns`, secondary `reactor_neutrino`, status `active`
- `detectors/conus-hpge-array.json` (4×1 kg HPGe, reused at both sites)
- `collaborations/conus.json`
- `facilities/brokdorf-nuclear-power-plant.json`, `sites/brokdorf-nuclear-power-plant-campus.json`
- `facilities/leibstadt-nuclear-power-plant.json`, `sites/leibstadt-nuclear-power-plant-campus.json`
- 7 `sources/cevns-conus-*.json`

**NUCLEUS** (mandatory bar):
- `experiments/nucleus.json` — kind `cevns`, secondary `reactor_neutrino`, status `commissioning`
- `detectors/nucleus-calorimeter-array.json` (CaWO4/Al2O3 cryogenic calorimeters)
- `collaborations/nucleus.json`
- `sites/chooz-very-near-nucleus.json` (references dangling `facility:chooz`)
- 4 `sources/cevns-nucleus-*.json`

**Ricochet** (mandatory bar):
- `experiments/ricochet.json` — kind `cevns`, secondary `reactor_neutrino`, status `commissioning`
- `detectors/ricochet-cryocube.json` (Ge/Zn cryogenic calorimeters, CryoCube)
- `collaborations/ricochet.json`
- `facilities/ill-grenoble.json`, `sites/ill-grenoble-reactor-hall.json`
- 2 `sources/cevns-ricochet-*.json`

**Coverage**: `data/atlas/coverage/cevns.json` updated with honest
`researched`/`missing_fields`/`notes` per experiment (see file; summary below).

## Sources added

24 new `src:cevns-*` records plus one existing `src:topic-coherent-2017-cevns-observation`
updated (`accessed` refreshed, `retrieval` corrected from `summary` to
`partial` since a `quote` is cited from it). All are pages actually fetched
this session via WebFetch (arXiv abstract/HTML pages, the official COHERENT
site, INSPIRE experiment/literature API records, Wikipedia infoboxes for
facility coordinates). WebSearch's session-wide budget (200 calls, shared
across all leads) was exhausted partway through COHERENT research; all
research after that point used WebFetch only (direct arXiv/INSPIRE/Wikipedia
URLs), including all of CONUS, NUCLEUS and Ricochet.

## Conflicts

| Claim | Source A | Source B | Chosen | Why | Confidence |
| --- | --- | --- | --- | --- | --- |
| COHERENT Ge array mass | Official detector-suite page: "10kg array... scheduled to be deployed later in 2020" | arXiv:2406.13806 (2024 evidence paper): "eight 2.2 kg ICPC detectors" = 17.6 kg | 17.6 kg (Ge-Mini) as the primary spec; 10 kg recorded only as a separate, lower-confidence interval | The 17.6 kg figure is the one tied to the actual sourced physics result (3.9σ evidence); it's unclear if the 10 kg 2020 announcement is the same physical array or an earlier generation, so they are not merged | approximate/verified (split) |
| COHERENT CsI baseline quote | arXiv:2110.07730 extraction returned "CEvNS was first observed in NA, 19.3 m..." | — | Used only to source the 19.3 m figure, not detector identity (the 2017 Science paper is the source of record for "first observed... using CsI[Na]") | Likely an OCR/extraction artifact ("NA" for "CsI" or similar); flagged in `experiments/coherent.json` notes | verified (for the number only) |
| NOvA/Brokdorf/etc. n/a | — | — | — | — | — |
| CONUS one-record vs. two-record decision | Brief allowed either interpretation | arXiv:2407.11912 ("The CONUS+ experiment"): "continuing on this way the CONUS physics program... the same four... HPGe detectors produced for the former experiment, however refurbished" | One record `experiment:conus`, no `CONUS+` alias literal string (see below) | Explicit collaboration statement of continuity, same hardware, same collaboration | verified |
| Brokdorf CONUS-detector distance | Wikipedia ("CONUS experiment" page): "17 m" | arXiv:2011.00210 (primary): "17.1m" | 17.1 m | Primary source preferred over Wikipedia | verified |
| Brokdorf reactor shutdown vs. CONUS detector operation | Wikipedia (Brokdorf NPP page): reactor "ceased operations on 31 December 2021" | arXiv:2501.05206: "the reactor at KBR stopped operation" (2023 move) | Recorded reactor shutdown as 2021-12-31 (facility) and the physical CONUS/Leibstadt move as "in 2023" (experiment/detector); noted in `facilities/brokdorf-nuclear-power-plant.json` that CONUS continued taking (presumably background) data at the site for some time after the reactor itself shut down | Two different real-world events (reactor shutdown vs. detector relocation), each with its own source | verified |
| NUCLEUS/Ricochet distance-from-core numbers | brief text (secondhand) | primary papers fetched this session | Only Ricochet's 8.8 m (arXiv:2208.01760) is sourced; NUCLEUS's exact distance is not sourced (only "very near" is verified) and is left null with a note | No fetched source gives a precise NUCLEUS number | Ricochet: verified; NUCLEUS: null/uncertain |

## Unresolved fields (see coverage rows for the full, per-experiment list)

- COHERENT: exact detector installation dates (only approximate/bounded),
  collaboration leadership, collaboration member headcount, ORNL/SNS facility
  chain (dangling).
- CONUS: collaboration formation date, membership counts, official website,
  INSPIRE record (none found), exact Brokdorf start date.
- NUCLEUS: exact distance from the Chooz reactor core, precise site
  coordinate, collaboration formation/membership, website, INSPIRE record,
  facility:chooz (dangling).
- Ricochet: precise final CryoCube mass (only the smaller commissioning
  module's mass is sourced), collaboration formation/membership, website,
  INSPIRE record, precise detector-hall coordinate.

## Children spawned and what I re-checked

None spawned (see Delegation note above — the shared subagent cap never
freed up during this run). Because there were no children, "checking a
child's work" does not apply; instead, every critical value below was sourced
directly by this lead agent via WebFetch/WebSearch in this session and is
cited with a `quote`/`locator` in the entity file itself, then re-verified a
second time against the validator (coordinate sanity, mass/energy unit and
plausibility-range checks, A16 result-type keyword checks, A20 duplicate-name
checks) after every batch of writes, iterating until 0 errors attributable to
these files remained.

## Dangling references (ids owned by other Wave 3 leads)

- `facility:oak-ridge-national-laboratory`, `site:ornl-sns-neutrino-alley`,
  `accelerator:sns` — owned by `facilities`; referenced from COHERENT's
  experiment/collaboration/detector files. Expected per WAVE3_LEAD_BRIEF.md.
- `facility:chooz` — owned by `reactor-solar-neutrino` (Double Chooz row of
  ID_REGISTRY); referenced from NUCLEUS's experiment/collaboration/site files.
  Expected per WAVE3_LEAD_BRIEF.md.

## Validator / build status

`python -m hepgraph.atlas.validate`: **0 errors** attributable to any
`cevns`-owned file (checked explicitly, category by category, against every
error-severity finding class in the full validator run). Remaining findings
that touch these files are all either the two expected dangling references
above, or warnings: `coordinate-kind-approximate` (A23 — Brokdorf, Leibstadt,
ILL and Chooz sites are campus-grade points because no fetched source gives a
more precise detector-hall coordinate; each carries `confidence: approximate`
and an explanatory `note`, which is exactly what A23 asks for), `interval-start-unknown`
(a few `start: null` intervals where no source states an exact date), and
`experiment-without-active-beam` (all four cevns experiments are reactor/
spallation-source experiments with no `accelerator`/`beamline` entity created
in this wave, or a dangling one for COHERENT — a structural, expected
consequence of scope, not a real problem).

`python -m hepgraph.atlas.build`: succeeds (writes 31 bundle files). The
pilot bundle-size warning ("atlas.json + manifest.json is over the pilot
budget of 400000 bytes") is a pre-existing, repo-wide condition from the
accumulated wave-3 data of all 16 leads, not something introduced by or
fixable within this workstream alone.

## Confidence summary

- **High confidence, multiply-sourced**: COHERENT's four detector masses and
  three mandated result titles/dates (2017/2021/2022), all quoted verbatim
  from the arXiv abstract pages of the actual publications; CONUS's one-vs-two
  record decision (explicit "continuing... the same... detectors... however
  refurbished" quote); Ricochet's and NUCLEUS's current status (commissioning),
  each independently verified against a 2025/2026 primary paper rather than
  taken on the brief's word.
- **Medium confidence**: all facility/site coordinates (Brokdorf, Leibstadt,
  ILL, Chooz) — sourced from Wikipedia infoboxes only, campus-grade,
  explicitly marked `confidence: approximate` with a note, per the ontology's
  fallback rule when no official/geodetic source was found or reachable in
  this pass.
- **Low confidence / explicitly flagged**: COHERENT's CsI[Na] detector
  installation/decommissioning exact dates (bounded, not exact); CONUS's,
  NUCLEUS's and Ricochet's collaboration formation dates and membership
  counts (no fetched source states them, left `null` with a note rather than
  estimated or taken from author-list counting, which the ontology forbids).
- No coordinate, date, mass, status or result claim in any of these files
  comes from model memory: every one carries a `sources` entry pointing at a
  `src:` record for a page fetched in this session, with a `quote` or
  `locator`.
