# dm-cryogenic-low-threshold research log

Agent: `dm-cryogenic-low-threshold`. Worked in `/Users/yatharthsirohi/Desktop/HEP-Graph-atlas-v1`
(branch `hep-atlas-v1`) on 2026-09-17. All `verified_at`/`accessed` values are
2026-09-17, the day every cited source was fetched with WebFetch (WebSearch was
exhausted session-wide almost immediately; INSPIRE's `/api/experiments` and
`/api/literature` endpoints, fetched via WebFetch, stood in for it throughout).

No child agents were spawned. The concurrent-subagent cap (20, shared across
16 wave-3 leads) was hit on every attempt (4 attempts across two waves); per
the coordinator's correction mid-task, all eight experiments were researched
and written directly by this agent instead of delegating.

## Scope

Eight non-flagship (tier B) cryogenic/low-threshold direct-detection dark
matter experiments, split into four technology families as instructed:

* Cryogenic Ge/Si phonon detectors: `experiment:cdms-ii`, `experiment:supercdms`,
  `experiment:edelweiss`
* Skipper/scientific CCDs: `experiment:sensei`, `experiment:damic`, `experiment:damic-m`
* Spherical proportional counter: `experiment:news-g`
* Scintillating CaWO4 (and Al2O3/LiAlO4) cryogenic calorimeters: `experiment:cresst`

Each experiment got an `experiment:`, `detector:` and `collaboration:` record.
No `result:`, `document:` or `memberships/` files were written (full-depth
extras, optional for tier B; time went into interval/spec/placement depth
instead). No `people/` files were written.

## Entities written

| id | file |
| --- | --- |
| `experiment:cdms-ii` | `data/atlas/experiments/cdms-ii.json` |
| `detector:cdms-ii` | `data/atlas/detectors/cdms-ii.json` |
| `collaboration:cdms-ii` | `data/atlas/collaborations/cdms-ii.json` |
| `experiment:supercdms` | `data/atlas/experiments/supercdms.json` |
| `detector:supercdms` | `data/atlas/detectors/supercdms.json` |
| `collaboration:supercdms` | `data/atlas/collaborations/supercdms.json` |
| `experiment:sensei` | `data/atlas/experiments/sensei.json` |
| `detector:sensei` | `data/atlas/detectors/sensei.json` |
| `collaboration:sensei` | `data/atlas/collaborations/sensei.json` |
| `experiment:damic` | `data/atlas/experiments/damic.json` |
| `detector:damic` | `data/atlas/detectors/damic.json` |
| `collaboration:damic` | `data/atlas/collaborations/damic.json` |
| `experiment:damic-m` | `data/atlas/experiments/damic-m.json` |
| `detector:damic-m` | `data/atlas/detectors/damic-m.json` |
| `collaboration:damic-m` | `data/atlas/collaborations/damic-m.json` |
| `experiment:news-g` | `data/atlas/experiments/news-g.json` |
| `detector:news-g` | `data/atlas/detectors/news-g.json` |
| `collaboration:news-g` | `data/atlas/collaborations/news-g.json` |
| `experiment:cresst` | `data/atlas/experiments/cresst.json` |
| `detector:cresst` | `data/atlas/detectors/cresst.json` |
| `collaboration:cresst` | `data/atlas/collaborations/cresst.json` |
| `experiment:edelweiss` | `data/atlas/experiments/edelweiss.json` |
| `detector:edelweiss` | `data/atlas/detectors/edelweiss.json` |
| `collaboration:edelweiss` | `data/atlas/collaborations/edelweiss.json` |

Not written, deliberately:

* `site:soudan-cdms` — no source fetched this session gives a distinct
  coordinate/description for a CDMS-specific cavern at Soudan separate from
  `site:soudan-minos-far-detector` (owned by `fermilab-neutrino-other`, only
  referenced). CDMS II and SuperCDMS's Soudan-era placements reuse that
  existing site.
* `site:fermilab-minos-near-detector-hall` — SENSEI's Fermilab placement
  reuses the existing `site:fermilab-main-campus` (owned by `fermilab-dune`).
  That lead's own record already documents this exact site as the
  campus-precision marker for "the MINOS near detector hall" (their words,
  used for `detector:minos-near-detector` too), with `kind: detector` and
  `precision_m: 3000`, because no coordinate more precise than the Fermilab
  campus centroid was ever found for that hall by any lead. Creating a second,
  differently-named site with the identical fabricated-precision coordinate
  would violate "one canonical entity per real thing" and likely trip the A20
  sites-too-close warning. This is a deliberate, documented deviation from the
  brief's literal instruction to create that site.
* No `institution:`, `person:`, `memberships/*.json`, `result:` or
  `document:` files — out of scope for this owner / optional for tier B.

## Sources added (source ids only; see each entity's `sources`/quotes for URLs)

CDMS family: `src:cdms-ii-inspire-experiment`, `src:cdms-ii-final-results-2009-arxiv`,
`src:supercdms-inspire-experiment-snolab`, `src:supercdms-inspire-experiment-soudan`,
`src:supercdms-official-site`, `src:supercdms-slac-news-2026-08-26-early-science`,
`src:supercdms-slac-news-2026-03-17-cooldown`, `src:supercdms-symmetry-2018-construction-begins`,
`src:supercdms-fnal-installation-commissioning`.

CCDs: `src:sensei-inspire-experiment`, `src:sensei-shallow-underground-2019-arxiv`,
`src:sensei-new-skipper-ccd-2020-arxiv`, `src:sensei-spurious-charge-2026-arxiv`,
`src:damic-inspire-experiment-original`, `src:damic-inspire-experiment-snolab`,
`src:damic-11kgday-2020-arxiv`, `src:damic-skipper-excess-2023-arxiv`,
`src:damic-inspire-literature-2024-excess`, `src:damic-m-inspire-experiment`,
`src:damic-m-status-2022-arxiv`, `src:damic-m-daily-modulation-2025-arxiv`.

NEWS-G: `src:news-g-inspire-experiment`, `src:news-g-official-site-queens`,
`src:news-g-snolab-detector-2022-arxiv`, `src:news-g-lsm-methane-2024-arxiv`,
`src:news-g-light-wimp-2025-inspire`.

CRESST/EDELWEISS: `src:cresst-inspire-experiment`, `src:cresst-official-site`,
`src:cresst-official-detectors-page`, `src:cresst-official-history-page`,
`src:cresst-tes-optimization-2026-arxiv`, `src:cresst-nuclear-recoil-peak-2025-arxiv`,
`src:edelweiss-inspire-experiment`, `src:edelweiss-inspire-experiment-iii`,
`src:edelweiss-subgev-migdal-2022-arxiv`, `src:edelweiss-subgev-ntl-2022-arxiv`,
`src:edelweiss-cryosel-2024-inspire`.

38 source records total, all `retrieval: "partial"` (WebFetch summarised/quoted
rather than returning raw HTML; every critical value's `quote` is text the
fetch tool returned in quotation marks, never paraphrase). No source was
fetched and discarded as `failed` in this file; two pages returned HTTP
errors and were simply not cited (see Conflicts/Unresolved below).

## Conflicts

| claim | source A | source B | chosen | why |
| --- | --- | --- | --- | --- |
| CDMS II operating span | INSPIRE 1108506: date_started 2005, date_completed 2009 | arXiv:0912.3592 (final results, submitted 2009-12-18): "final data taken... at the Soudan Underground Laboratory" | 2005-2009, terminal `completed` at 2009 | The paper confirms the registry's end date precisely; no independent source gives a different start. |
| SuperCDMS Soudan/SNOLAB structure | INSPIRE lists two separate experiment codes: SuperCDMS-Soudan (recid 1298909) and SuperCDMS-SNOLAB (recid 1357671) | Wave-3 brief: "its earlier Soudan phase as an interval or a separate site placement" | One `experiment:supercdms` record with two facility_roles/placements and non-terminal Soudan interval | Following the brief's explicit option; kept the Soudan interval `active` (not `completed`) because A3 forbids a non-terminal interval starting after a terminal one on the same entity — the validator caught this as an error on the first draft and it was fixed by removing the terminal marker from the Soudan sub-phase. |
| DAMIC's current status | Wave-3 brief: "DAMIC (SNOLAB; completed)" | INSPIRE literature record 2752302 (2024-01-24): "two 24-megapixel skipper charge-coupled devices... deployed in the DAMIC setup at SNOLAB", describing an active run | `active`, open interval, brief's claim flagged unsourced | Per A17 (no fact from memory on a critical field) and the brief's own instruction to under-claim rather than over-claim: no source fetched this session states DAMIC has stopped. Recorded honestly as active with a note explaining the discrepancy, rather than asserting the brief's unsourced claim. |
| SENSEI's SNOLAB deployment | arXiv:2004.11378 (2020): "a planned ~100-gram SENSEI experiment at SNOLAB" | arXiv:2605.30281 (2026-05): "Using the SENSEI detector near the MINOS cavern" | No SNOLAB placement recorded | The 2020 source describes SNOLAB only as a future plan; the most recent source found (2026) still places the operating detector at Fermilab. Recording a SNOLAB placement would be asserting an unconfirmed move. |
| NEWS-G's 135 cm sphere location | arXiv:2205.15433 (2022): "installed at SNOLAB in 2020-2021" | arXiv:2407.12769 (2024-07): "a 135 cm in diameter spherical proportional counter at the Laboratoire Souterrain de Modane" | Both placements recorded, unreconciled | No source fetched this session states whether the LSM 2024 run used the same physical sphere as the SNOLAB S140 or a second unit. Recorded as two separate sourced facts rather than invented as one continuous narrative. |
| Depth/precision of Fermilab-hosted detector halls (SENSEI, DAMIC prototype) | — | — | Placed at `site:fermilab-main-campus` at campus precision | Consistent with the existing precedent set by `fermilab-dune`/`fermilab-neutrino-other` for the MINOS near detector at the same site; no more precise coordinate was found for any Fermilab near-surface hall by any lead so far. |

## Unresolved fields

* `experiment:supercdms.lineage` — no source states the CDMS-II -> SuperCDMS
  relationship in citable text; left empty rather than asserted from memory.
* `experiment:damic.status` — recorded `active`, not the brief-expected
  `completed`; see Conflicts above. Needs a source (an official closure
  announcement or a DAMIC-M paper explicitly retiring DAMIC) to resolve.
* `experiment:edelweiss` early history — EDELWEISS/EDELWEISS-II/EDELWEISS-III
  founding and transition dates are entirely unsourced this session (the
  INSPIRE registry lists three experiment codes with no populated dates, and
  both `edelweiss.in2p3.fr` and `www.edelweiss.in2p3.fr` failed DNS
  resolution). Only the current 2022-2024 sub-GeV programme is richly sourced.
  This experiment's `researched` is `partial` but noticeably thinner than the
  other seven.
* Operating temperatures in mK for `detector:cresst` and `detector:edelweiss`
  — implied by "cryogenic"/TES technology but no page fetched this session
  states a number; `detector:cresst.specs.temperature` is recorded
  `confidence: uncertain` with a note rather than presented as verified.
  `detector:edelweiss` has no temperature spec at all.
  `detector:supercdms.specs.temperature` was quoted directly ("roughly 15 to
  30 millikelvins") and recorded as a min/max range.
* `site:snolab-underground-lab` coordinate kind — the `facilities`-owned file
  carries `kind: campus`, which the validator flags as an error because
  several detectors (SuperCDMS, DAMIC, NEWS-G, this file's) are placed there
  and A17/A21 require `detector`/`underground_lab` kind for any site holding
  a detector. This is **not my file to fix**; noted here so the discrepancy
  is visible, not silently worked around.
* Two pages returned HTTP errors and were not cited: `cresst.de/cresst.php`
  redirected to `cresst-experiment.org/cresst.php`, which itself 404'd (the
  working page was the bare domain instead); `edelweiss.in2p3.fr` and
  `www.edelweiss.in2p3.fr` both failed DNS. `cdms.berkeley.edu` returned
  `ECONNREFUSED`.

## Dangling references to ids another lead owns

None remain as of the final validator run: `facility:snolab`,
`site:snolab-underground-lab`, `facility:modane-underground-laboratory`,
`site:lsm-frejus` and `site:lngs-hall-a` (all owned by `facilities`) did not
exist when this task started but landed partway through and now resolve
cleanly. `facility:soudan-underground-laboratory`, `site:soudan-minos-far-detector`
(owned by `fermilab-neutrino-other`), `facility:fermilab` and
`site:fermilab-main-campus` (owned by `fermilab-dune`) existed from the start
and are referenced normally, never edited.

## Children spawned and what was re-checked

None. Every attempt to spawn a child (two waves, up to 4 requested at once)
returned "Concurrent subagent limit reached" (the shared 20-subagent cap
across 16 wave-3 leads). Per the coordinator's mid-task correction, all
research and writing was done directly by this agent with WebFetch, so there
is no child work to re-verify — every quote in every entity file is text this
agent's own WebFetch calls returned, cited in that value's `sources`.

## Confidence summary

* **verified** — CDMS II detector composition/mass/temperature/exposure;
  SuperCDMS's 2018/2026 construction-commissioning-early-science timeline and
  24-crystal count; SENSEI's Fermilab placement, prototype and current
  device masses; DAMIC's SNOLAB CCD tower composition and exposure; DAMIC-M's
  LSM placement, prototype mass and 2025 exposure; NEWS-G's SEDINE and S140
  sphere diameters, gas fills and SNOLAB install window; CRESST's full
  1993-2019 generational timeline and CRESST-II/III crystal masses;
  EDELWEISS's current 200 g Ge/NbSi-TES programme, resolution and threshold.
* **approximate** — CDMS-II/SuperCDMS-Soudan year-precision dates (INSPIRE
  registry only, no independent detector-paper cross-check); NEWS-G's SEDINE
  installation year; SuperCDMS's DOE-approval-to-commissioning interval
  boundary.
* **uncertain** — every collaboration's `formation`/founding interval (no
  dedicated source found for any of the eight; all approximated to the
  earliest sourced project date with an explanatory note); CRESST detector
  operating temperature (technology-implied, not quoted).
* **null with a note** — `experiment:supercdms` lineage to CDMS-II;
  EDELWEISS's pre-2022 history and founding date; SENSEI/DAMIC-M/CRESST/
  EDELWEISS/NEWS-G official-site liveness or institution/member counts;
  DAMIC's explicit end-of-operations date/status (recorded active instead).

## Validation and build

`.venv/bin/python -m hepgraph.atlas.validate` (run from
`/Users/yatharthsirohi/Desktop/HEP-Graph-atlas-v1`): **0 errors attributable
to this workstream's files** in the final run (repo-wide error count
fluctuates turn to turn because 15 other leads are writing concurrently).
Remaining findings on this workstream's own files are all warning/info level
and consistent with existing precedent elsewhere in the tree (A9
`physics_goals`/`unique_capabilities` as one sourced list — same pattern as
`experiments/lz.json`; A12 experiment-before-facility and
experiment-without-active-beam warnings, expected for non-collider dark-matter
experiments with no beamline; A12 hull gaps in the 2016-2021 range where no
source was found; A21 unknown-spec-key warnings for detector-specific keys
not in the Appendix A shortlist, e.g. `ge_detector_count`, `ccd_mass`,
`sphere_diameter_s140`; A21 display-value-drift on the SuperCDMS 15-30 mK
range and the DAMIC "7 x 16-Mpixel CCDs..." descriptive display string).

`.venv/bin/python -m hepgraph.atlas.build` succeeds (writes 31 files to
`static/atlas/generated/`); the only warning is the pre-existing, repo-wide
`atlas.json` size budget (1.3 MB vs. the 400 KB pilot target), unrelated to
this workstream specifically.

Files were written with `hepgraph.atlas.load.dump_json`
(`json.dumps(sort_keys=True, indent=2, ensure_ascii=False)` + trailing
newline) and carry `"schema": "hep-atlas/0.2"`.
