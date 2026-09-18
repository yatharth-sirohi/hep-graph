# heavy-ions worklog (Wave 3 / v1.0)

Owner: `heavy-ions`. Scope per `data/atlas/coverage/heavy-ions.json`: three
non-flagship (tier B) RHIC heavy-ion experiments — STAR, PHENIX, sPHENIX.
ALICE is explicitly out of scope (owned by `colliders-lhc`). All work is
under `data/atlas/` and this file; no git; no children were spawned (the
session-wide concurrent-subagent pool was saturated by the other 15 wave-3
leads at delegation time, so research below was done directly rather than
delegated, per the coordinator's standing instruction to keep going rather
than block).

## Scope

- `experiment:star`, `detector:star`, `collaboration:star`
- `experiment:phenix`, `detector:phenix`, `collaboration:phenix`
- `experiment:sphenix`, `detector:sphenix`, `collaboration:sphenix`
- Two non-flagship "extra" results (added because time remained after the
  mandatory bar): the 2005 RHIC "perfect liquid" white papers, one per
  collaboration, using each collaboration's own title wording and never the
  word "discovery" per the brief.

`facility:brookhaven-national-laboratory`, `accelerator:rhic`,
`site:bnl-rhic-ip6-star` and `site:bnl-rhic-ip8-phenix-sphenix` are owned by
the `facilities` lead. They did not exist when this record set was first
drafted; the facilities lead's BNL child has since landed all four (plus
`accelerator:ags` and `site:bnl-upton-campus`) and reused two of this
workstream's sources (`src:heavy-ions-star-bnl-facility-page`,
`src:heavy-ions-rhic-final-collisions-2026`, `src:heavy-ions-rhic-run25-start-2025`
appear cited from `data/atlas/sites/bnl-rhic-ip6-star.json`,
`sites/bnl-rhic-ip8-phenix-sphenix.json` and `accelerators/rhic.json`). All
four references were re-checked against the landed files after they appeared:
`hepgraph.atlas.validate` reports **zero dangling-reference findings** on any
heavy-ions file.

## Entities written

- `data/atlas/experiments/star.json` — kind `heavy_ion`, status `completed`
  (RHIC's 25th and final run ended 2026-02-06), `external.inspire_experiment:
  "1108784"`, `key_specs` (mass, TPC diameter/length), lineage none.
- `data/atlas/detectors/star.json` — `technology_classes: ["gaseous_tpc"]`,
  one placement at `site:bnl-rhic-ip6-star` (main, 2000 → 2026-02-06).
- `data/atlas/collaborations/star.json` — formation `null` (unsourced, see
  Unresolved below), membership 609 collaborators / 55 institutions / 12
  countries (BNL's own page).
- `data/atlas/experiments/phenix.json` — kind `heavy_ion`, status `completed`
  (finished data-taking 2016), `external.inspire_experiment: "1108852"`.
- `data/atlas/detectors/phenix.json` — `technology_classes: ["spectrometer"]`,
  one placement at `site:bnl-rhic-ip8-phenix-sphenix` (main, 2000-06-15 →
  2016).
- `data/atlas/collaborations/phenix.json` — formation `1991-08` (sourced,
  verbatim), no membership counts found.
- `data/atlas/experiments/sphenix.json` — kind `heavy_ion`, status
  `completed` (same RHIC closure as STAR), `external.inspire_experiment:
  "1500624"`, `lineage: [{experiment_id: experiment:phenix, relation:
  upgrade_of}]`.
- `data/atlas/detectors/sphenix.json` — `technology_classes:
  ["general_purpose_collider"]`, one placement at the same IP8 site as
  PHENIX (main, 2023 → 2026-02-06).
- `data/atlas/collaborations/sphenix.json` — formation `null` (only the DOE
  CD-0 project milestone, 2017-01-13, is sourced).
- `data/atlas/results/star-perfect-liquid-whitepaper-2005.json` — STAR's
  2005 white paper, `result_type: "measurement"` (never discovery).
- `data/atlas/results/phenix-perfect-liquid-whitepaper-2005.json` — PHENIX's
  2005 white paper, `result_type: "measurement"` (never discovery).

No `sites/`, `facilities/` or `accelerators/` files were created (all owned
by `facilities`). No `people/` or `memberships/` files were created.
`data/atlas/coverage/heavy-ions.json` updated: all three rows `researched:
"partial"`, `status: "completed"`, honest `missing_fields`.

## Sources added (16, all prefixed `src:heavy-ions-`)

Directly fetched this session (WebFetch), each with `retrieval` set
accurately (`full_text` when the needed facts were confirmed verbatim,
`partial` when only an abstract/excerpt was retrieved):

- `src:heavy-ions-star-bnl-facility-page` — bnl.gov/rhic/star.php (official_facility_site)
- `src:heavy-ions-star-tpc-paper` — arXiv:nucl-ex/0301015 abstract (detector_paper)
- `src:heavy-ions-star-detector-overview-inspire` — INSPIRE 608101, bibliographic only (detector_paper)
- `src:heavy-ions-star-inspire-experiment` — inspirehep.net/experiments/1108784
- `src:heavy-ions-phenix-concept-history` — phenix.bnl.gov/experiment/concept.html (official_experiment_site)
- `src:heavy-ions-phenix-inspire-experiment` — inspirehep.net/experiments/1108852
- `src:heavy-ions-sphenix-bnl-facility-page` — bnl.gov/rhic/sphenix.php
- `src:heavy-ions-sphenix-inspire-experiment` — inspirehep.net/experiments/1500624
- `src:heavy-ions-sphenix-cd0-news-2017` — bnl.gov/newsroom/news.php?a=26793
- `src:heavy-ions-sphenix-construction-commissioning-2024` — osti.gov/biblio/2338139 abstract
- `src:heavy-ions-sphenix-first-physics-results-2025` — phys.org 2025-07-18 article
- `src:heavy-ions-rhic25-timeline` — bnl.gov/rhic/rhic25/
- `src:heavy-ions-rhic-run25-start-2025` — bnl.gov/newsroom/news.php?a=122346
- `src:heavy-ions-rhic-final-collisions-2026` — bnl.gov/newsroom/news.php?a=122794 (RHIC's 25th/final run ended 2026-02-06 — this fact drives the `completed` status on all three experiments)
- `src:heavy-ions-star-perfect-liquid-whitepaper-2005` — arXiv:nucl-ex/0501009
- `src:heavy-ions-phenix-perfect-liquid-whitepaper-2005` — arXiv:nucl-ex/0410003

## Conflicts

| claim | source A | source B | chosen | why | confidence |
| --- | --- | --- | --- | --- | --- |
| STAR "operational" year range | BNL STAR page: "operational from 2000-2026" (likely a template computed against the current year, not a fixed historical statement) | BNL "final collisions" article: final RHIC collisions were 2026-02-06 | Kept both: `start: "2000"` sourced to the BNL page, terminal `end`/new interval `start: "2026-02-06"` sourced independently to the final-collisions article | The 2026 end date needed independent corroboration since a "current year" template isn't itself evidence of a historical end date; the final-collisions article supplies that independently. | verified |
| sPHENIX lineage relation to PHENIX: "upgrade_of" vs "predecessor" | BNL page: "sPHENIX is a radical makeover of the PHENIX experiment" | — | `upgrade_of` | BNL's own wording ("makeover of") frames sPHENIX as built on/replacing PHENIX at the same hall rather than an unrelated new detector; `upgrade_of` is the canonical direction under v0.2 A1 and is written on sPHENIX's own record (not `successor` on PHENIX's, which is a derived inverse). | verified (source), approximate (classification judgment) |
| PHENIX/sPHENIX detector-level numeric specs (arm acceptance, magnet T·m) | Search-engine synthesis of PHENIX NIM A499 (2003) papers | — (no successful direct WebFetch of the primary text: ScienceDirect returned 403, the PHENIX muon-arm PDF fetched but was unreadable binary, INSPIRE literature pages returned empty JS shells) | Omitted; recorded as a missing field | A17 forbids sourcing a critical numeric field from a search-engine paraphrase rather than content actually fetched this session. Under-claiming (leaving `key_specs`/`specs` sparse) was chosen over recording an unverified number. | n/a (not recorded) |
| STAR magnet field strength (commonly ~0.5 T) | Search-engine synthesis of the STAR magnet-subsystem paper (NIM A499:633-639) | — (star.bnl.gov PDF returned 403; INSPIRE record 608100 returned an empty page) | Omitted; recorded as a missing field | Same A17 reasoning as above. | n/a (not recorded) |
| STAR detector-overview paper (NIM A499:624-632, the specific paper the brief names) full text | INSPIRE 608101 (bibliographic metadata only) | STAR TPC subsystem paper, NIM A499:659-678 (same journal volume, full abstract fetched) | Used the TPC paper's verbatim abstract for the TPC diameter/length key_specs; the overview paper is cited by id/locator only, no quote | The overview paper's own full text was not retrievable this session (no arXiv id, no accessible journal page); the TPC paper is a legitimate companion primary source in the same volume and was actually fetched. | verified (TPC facts), n/a (overview paper, locator only) |
| STAR/PHENIX 2005 "perfect liquid" result wording | STAR abstract: "the measurements themselves do not yet establish unequivocal evidence for a transition to this new form of matter" | — | `result_type: "measurement"` for both, never "evidence" or "discovery" | STAR's own abstract explicitly hedges against "evidence"; the brief also explicitly forbids "discovery." PHENIX's abstract doesn't contain the word "evidence" either, so "measurement" was used uniformly rather than mixing mechanical-check categories inconsistently. | verified |

## Unresolved fields

- STAR and sPHENIX collaboration **formation dates**: no directly-fetched
  source states one. Left `null` with `locator`+`note` (STAR: the BNL STAR
  page, fetched in full, never gives one; sPHENIX: the DOE CD-0 announcement
  is the earliest sourced institutional milestone, 2017-01-13, but that is a
  project-approval date, not a collaboration-formation date). Secondary
  compilations found via search (STAR proposal ~1990-91, PAC approval July
  1991, construction start early 1993) were **not** used because they were
  never independently confirmed via a direct fetch this session (A17).
- PHENIX/sPHENIX **detector key_specs** (central/muon arm acceptance, magnet
  T·m, calorimeter granularity): every primary-paper fetch attempt failed
  (403s, unreadable PDF binary, empty JS-rendered INSPIRE pages). Left out
  rather than sourced from search-engine paraphrases.
- STAR **magnet field strength**: same reasoning, omitted.
- **sPHENIX TDR/design-report document** and the **2025-07-18 first-physics
  results** as a `results/` record: both flagged by the brief as time-permitting
  extras; not reached this session.
- **STAR construction/approval interval precision**: BNL's own page gives
  only the coarse "2000-2026" operating range; no fetched source gives a
  construction-start or PAC-approval date, so STAR's own pre-2000 history is
  thinner than PHENIX's (which had a strong official history page).
- Two small, honestly-reported gaps in sPHENIX's sourced timeline (2017-02 to
  2020-12, and all of 2022) surface as `hull-gap` validator warnings; a 2021
  magnet-installation milestone was added (sourced) to shrink the larger gap,
  but no sourced event was found to close the remainder. Left as warnings
  rather than invented.
- `experiments/star.json` triggers the `experiment-without-active-beam`
  warning at 2000-01 because `accelerator:rhic`'s own sourced interval (owned
  by `facilities`) does not mark RHIC active that early; this depends on
  another lead's data and was not changed here.

## Dangling references (now resolved)

At initial drafting, `facility:brookhaven-national-laboratory`,
`accelerator:rhic`, `site:bnl-rhic-ip6-star` and
`site:bnl-rhic-ip8-phenix-sphenix` did not exist and were referenced as
dangling ids per `ID_REGISTRY.md`. The facilities lead's BNL child has since
landed all of them (plus `accelerator:ags`, `site:bnl-upton-campus`) and
reused several of this workstream's own sources when doing so. All
references were re-checked against the landed files: `hepgraph.atlas.validate`
reports **zero `dangling-reference` findings** on any file this workstream
owns. Entity `notes[]` were updated in place to record that the ids landed
rather than leaving stale "does not exist" language.

`experiment:phenix` (referenced by `experiment:sphenix`'s `lineage` row) is
owned by this same workstream and was written in the same session, so it was
never actually dangling.

## Historically relevant heavy-ion programmes deliberately not covered

Per the brief's instruction to scope out rather than silently omit: the
following historically important heavy-ion facilities/experiments are
**deliberately not researched** in this wave (out of the `heavy-ions` scope,
which is limited to the three RHIC experiments in
`data/atlas/coverage/heavy-ions.json`) and no placeholder records exist for
them:

- **CERN SPS heavy-ion programme**: NA49, NA50, NA60 (fixed-target heavy-ion
  experiments at the CERN Super Proton Synchrotron, 1990s-2000s).
- **Bevalac** (Lawrence Berkeley Laboratory's Bevatron/SuperHILAC combined
  heavy-ion accelerator, 1970s-1990s), one of the earliest relativistic
  heavy-ion physics programmes.
- **AGS heavy-ion fixed-target experiments** E802/E866 (and related AGS
  heavy-ion runs at Brookhaven that preceded RHIC).

This list should let the coverage report state the exclusion explicitly
rather than reading as an oversight. If a future wave extends the
`heavy-ions` (or a new `heavy-ion-historical`) coverage file to include them,
the ids above are free (not claimed by any Wave 3 `ID_REGISTRY.md` row as of
this writing).

## Children spawned

None. The Agent tool returned "Concurrent subagent limit reached" (the
session-wide pool of 20 was saturated by the other 15 wave-3 leads
delegating at the same time) on every attempt, including a single
sequential retry. Per the coordinator's standing instruction ("do not stop,
do not retry in a loop; research the experiments yourself, sequentially"),
all research in this file was performed directly via WebSearch/WebFetch by
this lead, and every claim above was verified against the source at the time
it was written (there was no child hand-off to re-check).

## Confidence summary

- **High confidence / verified, directly-quoted**: PHENIX formation
  (1991-08), first collision (2000-06-15) and end of data-taking (2016);
  STAR's 1,200 t mass and 55-institution/12-country/609-collaborator
  membership; STAR TPC dimensions (4 m × 4.2 m) and pseudorapidity coverage;
  sPHENIX's 1,000 t mass, reused 20-ton BaBar solenoid, DOE CD-0 date
  (2017-01-13), construction-complete date (2023-04), first Au+Au
  commissioning data (2023), first physics results (2025-07-18); RHIC's 25th
  and final run closure (2026-02-06, driving all three experiments' terminal
  `completed` status); all three INSPIRE experiment recids
  (1108784/1108852/1500624); both 2005 white-paper titles and non-inflated
  result wording.
- **Lower confidence / explicitly flagged**: STAR and sPHENIX collaboration
  formation dates (null, unsourced); sPHENIX's `upgrade_of` vs `predecessor`
  lineage classification (a judgment call from BNL's "radical makeover"
  wording, not a term the source uses directly); PHENIX/sPHENIX detector
  technology_class assignments (`spectrometer` / `general_purpose_collider`,
  the closest enum matches, not verbatim source terms).
- **Deliberately absent rather than guessed**: PHENIX/sPHENIX arm-acceptance
  and magnet-field key_specs; STAR magnet field strength; sPHENIX TDR
  document and first-physics-results record.
