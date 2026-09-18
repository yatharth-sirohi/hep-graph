# VERIFY colliders-lhc — Wave 3 independent verification

Verifier: independent review, no subagents. Did not trust `docs/atlas-worklog/colliders-lhc.md`
(the researcher's own worklog); every factual claim below was re-checked against a freshly
fetched source in this session. Repo: `/Users/yatharthsirohi/Desktop/HEP-Graph-atlas-v1`
(branch `hep-atlas-v1`, no git used). `verified_at` on all fixes: 2026-09-17.

## Records checked

- Experiments (7): `experiment:alice`, `experiment:lhcb`, `experiment:faser`,
  `experiment:snd-lhc`, `experiment:lhcf`, `experiment:totem`, `experiment:moedal`.
- Detectors (7): matching `detector:*` for the same seven.
- Collaborations (7): matching `collaboration:*` for the same seven.
- Sites (4): `site:cern-point-2-alice`, `site:cern-point-8-lhcb`, `site:cern-ti12-faser`,
  `site:cern-ti18-snd-lhc`.
- Results (6, all owned by alice/lhcb): `alice-jpsi-suppression-pbpb-2012`,
  `alice-strangeness-enhancement-pp-2017`, `alice-hypertriton-lifetime-2019`,
  `lhcb-pentaquark-observation-2015`, `lhcb-doubly-charmed-baryon-observation-2017`,
  `lhcb-cp-violation-charm-observation-2019`. (`cms-lhcb-bs-to-mumu-observation-2015` was
  checked and confirmed **not** owned by this partition — `collaboration_ids` is
  `["collaboration:cms"]` only, correctly excluded per its own notes.)
- Documents (5, all owned by alice/lhcb): `alice-detector-paper-2008`,
  `alice-its2-upgrade-tdr-2014`, `alice-tpc-upgrade-tdr-2013`, `lhcb-detector-paper-2008`,
  `lhcb-upgrade-framework-tdr-2012`.
- Sources: all 28 original `src:colliders-lhc-*` records, plus 2 added by this verification.
- Cross-checked for consistency (read-only, not edited): `experiments/atlas.json`,
  `experiments/cms.json`, `detectors/atlas.json`, and the shared LHC-schedule sources
  (`src:cern-lhc-page`, `src:cern-run3-start-2022`, `src:cern-ls3-farewell-2026`,
  `src:cern-long-shutdown-3-page`).

## Values re-fetched: ~38 independent WebFetch calls

Every INSPIRE experiment record cited by this partition was re-fetched from the live API
(`https://inspirehep.net/api/experiments/<recid>`) and every field value (`date_proposed`,
`date_approved`, `date_started`, `date_completed`) compared verbatim against what the data
files claim: ALICE (1110642), LHCb (1110643), FASER (1711193), SND@LHC (2032474), LHCf
(1126263), TOTEM (1110567), MoEDAL (1110581), plus ATLAS (1108541) for cross-comparison.
**Every one matched exactly — no fabricated or misquoted INSPIRE dates found anywhere in
this partition.**

All 6 ALICE/LHCb flagship result claims were re-fetched from arXiv and checked verbatim
(title, claim quote, significance, key value): 1907.06906, 1202.1383, 1606.07424 (ALICE);
1507.03414, 1903.08726, 1707.01621 (LHCb). All quotes and numbers are accurate.

All seven experiments' official/home.cern pages were re-fetched (ALICE, LHCb x2, FASER,
LHCf, TOTEM, MoEDAL-MAPP) and their quoted facts (masses, dimensions, membership counts,
locations) all matched verbatim. `lhcb-outreach.web.cern.ch/detector/`'s "4,500 tonne" and
`home.cern`'s "5,600-tonne" were both independently re-confirmed (the recorded conflict is
real, not invented). `home.cern/science/experiments/alice`'s "56 m below ground" was
re-confirmed against the ALICE detector paper's own "52 m" (the recorded conflict is real).
CDS (`cds.cern.ch`) bot-protection and the ALICE/LHCb JINST paywalls were independently
re-hit, confirming the researcher's claims of blocked full text rather than an excuse for
skipped work.

## Findings by severity

### P1 (2, both fixed)

**1. SND@LHC was recorded `status: approved` although it has publicly taken LHC Run 3 data
since 2022 — exactly the P1 timeline error flagged in the verification brief.** The record's
own interval note already said "Status is nonetheless recorded as 'active' below... but no
source... states the first-data date," which was itself internally false (the field said
`approved`, not `active` — a pre-existing self-contradiction). Fetched the collaboration's
own paper, arXiv:2305.09383 / Phys. Rev. Lett. 131, 031802 (2023), "Observation of Collider
Muon Neutrinos with the SND@LHC Experiment": *"A data set of proton-proton collisions at
sqrt(s) = 13.6 TeV collected by SND@LHC in 2022 is used."* Also fetched the SND@LHC detector
paper (arXiv:2210.02784), which independently confirms the TI18/480 m siting fact the
prior record could only support with "general knowledge." **Fixed**: added source
`src:colliders-lhc-snd-lhc-2023-prl-muon-neutrino` and `src:colliders-lhc-snd-lhc-detector-arxiv-2022`;
added a sourced "data-taking" interval (2022, year precision) to `experiment:snd-lhc` and
`detector:snd-lhc`; populated `detector:snd-lhc.technology`/`specs.total_mass` (830 kg
tungsten target) from the newly-fetched detector paper; corrected `links.website`/placement
notes. `home.cern/science/experiments/snd-lhc` (404) and `sndlhc.web.cern.ch` (DNS failure)
were independently re-checked and confirmed still unreachable.

**2. Detector-level status contradicted experiment-level status for ALICE, LHCb and TOTEM —
and the same bug, previously unflagged, also affects FASER and LHCf.** `experiment:alice`,
`experiment:lhcb` and `experiment:totem` correctly derive `shutdown` during CERN's ongoing
Long Shutdown 3 (LS3, began 2026-06/07, confirmed against `home.cern`'s own LHC schedule
page and the already-cited `src:cern-ls3-farewell-2026`). But `detector:alice`,
`detector:lhcb` and `detector:totem` each had an **open-ended** "operating" interval
(`end: null`) with no LS3 boundary, so they derived `active` — a detector card and its
parent experiment card would show contradictory current status for the same physical thing.
Checking further found the identical mistake, unflagged, at the *experiment* level for
FASER and LHCf: both had an open-ended `active` "Run 3 (data-taking)" / "operating"
interval, so `experiment:faser` and `experiment:lhcf` (and their detectors) derived `active`
even though FASER and LHCf detect only particles produced in LHC collisions and cannot
record anything while the LHC itself is switched off. **Fixed**: capped the open interval
at `{"approx": true, "date": "2026-06"}` and added a sourced "Long Shutdown 3" `shutdown`
interval (reusing the already-cited `src:cern-ls3-farewell-2026`, no new fetch needed) on
`experiments/alice.json`, `detectors/alice.json`, `experiments/lhcb.json` (already had one;
only the detector needed it), `detectors/lhcb.json`, `experiments/totem.json` (already had
one; only the detector needed it), `detectors/totem.json`, `experiments/faser.json`,
`detectors/faser.json`, `experiments/lhcf.json`, `detectors/lhcf.json`. Top-level `status`
changed `active` → `shutdown` on all of `detector:alice`, `detector:lhcb`, `detector:totem`,
`experiment:faser`, `detector:faser`, `experiment:lhcf`, `detector:lhcf`. The newly-added
SND@LHC interval (finding 1) was built with the same LS3 cap from the start, so it does not
carry this bug.

### P2 (3 fixed, 2 flagged only)

**3. LHCb's INSPIRE `date_completed` field, fixed.** Re-fetched INSPIRE record 1110643 live:
`date_completed` genuinely reads `"2008-09"` (not fabricated). But cross-checking ATLAS
(1108541) and LHCf (1126263) shows the *same* field correctly reads INSPIRE's own
"ongoing/not completed" placeholder, `"9999"`, for both — which the LHCf record in this same
partition already recognises explicitly. LHCb is an active, non-terminal experiment, so a
literal "completed" date is intrinsically implausible; a populated (non-`9999`) value in
this field for a still-running experiment is either an INSPIRE data-entry anomaly or a
differently-scoped fact (e.g. "construction complete") that the schema doesn't distinguish
from experiment completion. The prior record used it uncritically at `confidence: verified`.
**Fixed**: downgraded confidence to `uncertain` with an explanatory note comparing to the
ATLAS/LHCf placeholder pattern, on both `experiments/lhcb.json` and `detectors/lhcb.json`.
The interval's *status* was already correctly non-terminal (`construction`, not
`completed`), so this was a confidence/documentation fix, not a status fix — the brief's
concern ("do not let a nonsensical field become a terminal interval") was already
structurally satisfied; what was missing was flagging that the field itself is anomalous.

**4. Self-contradictory coordinate notes on all four new sites, fixed.** Each of
`site:cern-point-2-alice`, `site:cern-point-8-lhcb`, `site:cern-ti12-faser`,
`site:cern-ti18-snd-lhc` had a `coordinates.note` that asserted, in the same paragraph, both
"kind is kept as 'detector' (not 'campus')... " and "kind is kept as 'campus' (not
relabelled 'detector')..." — leftover text from an earlier draft that the actual field value
(`"campus"`, correctly per A23) never matched. `cern-ti12-faser.json` and
`cern-ti18-snd-lhc.json` had the identical wrong `(kind: detector, confidence: uncertain)`
parenthetical in their outer `notes[]` array too. This is exactly the kind of "are the notes
honest" defect the brief asked to scrutinise: not a wrong value, but internally
contradictory documentation of a value. **Fixed**: rewrote all four `coordinates.note`
fields and the two outer-`notes[]` mentions to state only the actual value (`campus`),
removing the self-contradiction, and added a one-line changelog sentence to each so the
edit is auditable.

**5. MoEDAL: experiment/detector status disagree, flagged but not fixed.**
`experiment:moedal` derives `upgrade` (from an open-ended "MAPP upgrade approved" interval,
start 2021) while `detector:moedal` derives `active` (open-ended "operating" interval,
start 2009-12-02) — the same real thing, two different statuses. Unlike ALICE/LHCb/TOTEM/
FASER/LHCf/SND@LHC, MoEDAL's core detector elements are largely passive Nuclear Track
Detectors, so it isn't obviously true that MoEDAL's status should track LHC beam-on/off the
same way (a passive NTD stack does not stop "operating" just because there is no beam — it
keeps sitting there). No source fetched this session establishes either (a) whether the
2021-approved MAPP upgrade is still literally under way in 2026, or (b) whether MoEDAL,
like its neighbours, should also get an LS3 interval. Left as-is rather than guessing either
resolution; recorded here as an open item for the next MoEDAL-specific research pass.

**6. Cross-partition status-semantics inconsistency, checked and reported, not edited.**
ATLAS and CMS use `status: upgrade` for the current LS3-era interval (Phase-II
hardware-upgrade work, dated and sourced). ALICE, LHCb, TOTEM, FASER, LHCf and SND@LHC (this
partition) all use `status: shutdown` for the identical calendar period. Checked whether
this is a bug: LHCb's own record already states Upgrade II is scheduled for LS4, not this
shutdown; no sourced, dated upgrade programme places ALICE/TOTEM/FASER/LHCf/SND@LHC work
specifically inside LS3 (ALICE's "further upgrades... until the end of 2033" is undated
within that span, not LS3-specific). So the difference reflects genuinely different sourced
facts, not inconsistent methodology, and per the brief's instruction this is **reported, not
fixed by editing ATLAS/CMS or by inventing an unsourced "upgrade" label for the smaller
experiments**. It is nonetheless a real UX/consistency gap worth flagging to the wave-3
coordinator: a viewer will see CERN's two flagships as "under upgrade" and everything else
at CERN as merely "shut down" for what is, machine-wide, the same maintenance window.

### P0

None found. No false discovery/observation claims, no fabricated coordinates or dates, no
unsupported critical values, on either flagship. The two intentionally-flagged, sourced
conflicts already in the data (ALICE 52 m vs. 56 m cavern depth; LHCb 5600 t vs. 4500 t
detector mass) were both independently re-verified — each side's quote is accurate to its
own source — and remain correctly presented as open, cited conflicts rather than silently
resolved one way, which is what A15/A17 require. Read as "no unflagged/silent
contradiction," the wave-3 flagship bar (addendum §8) is met for both ALICE and LHCb.

## Fixes applied (full list, all `verified_at: 2026-09-17`)

- Added sources: `src:colliders-lhc-snd-lhc-2023-prl-muon-neutrino`,
  `src:colliders-lhc-snd-lhc-detector-arxiv-2022`.
- `experiments/snd-lhc.json`, `detectors/snd-lhc.json`: status `approved` → `shutdown` (via a
  newly-sourced `active` interval 2022 → LS3); technology/specs/placement populated from the
  new detector paper; self-contradictory note removed.
- `experiments/alice.json`, `detectors/alice.json`: detector interval capped at LS3, LS3
  shutdown interval added, detector `status` `active` → `shutdown`.
- `experiments/lhcb.json`, `detectors/lhcb.json`: LHCb `date_completed` interval confidence
  `verified` → `uncertain` with explanatory note; detector interval capped at LS3, LS3
  shutdown interval added, detector `status` `active` → `shutdown`.
- `experiments/totem.json`, `detectors/totem.json`: detector interval capped at LS3, LS3
  shutdown interval added, detector `status` `active` → `shutdown`.
- `experiments/faser.json`, `detectors/faser.json`: LS3 boundary and shutdown interval added
  at both levels (previously missing entirely); `status` `active` → `shutdown` at both
  levels; summary updated.
- `experiments/lhcf.json`, `detectors/lhcf.json`: same as FASER.
- `sites/cern-point-2-alice.json`, `sites/cern-point-8-lhcb.json`,
  `sites/cern-ti12-faser.json`, `sites/cern-ti18-snd-lhc.json`: removed self-contradictory
  "kind is kept as detector / kind is kept as campus" note text; added the new SND@LHC
  detector-paper source to `cern-ti18-snd-lhc.json` and strengthened its placement
  corroboration note.
- All edited files re-serialized with `json.dumps(sort_keys=True, indent=2,
  ensure_ascii=False)` + trailing newline.

## Unverifiable values (left as-is, already honestly flagged by the prior record)

- ALICE/LHCb Point 2/Point 8 cavern coordinates: still campus-grade placeholders
  (`confidence: uncertain`/`approximate`). Independently confirmed no official CERN page
  (`voisins.cern`, `home.cern/about/where-cern`) gives surveyed coordinates for either point;
  the OSM/Nominatim "CERN - Point 2 (Alice)" way was independently confirmed to exist and be
  a fence/industrial-landuse polygon, not a surveyed detector-hall position — the "campus,
  uncertain" labelling is honest.
- ALICE cavern depth (52 m vs. 56 m) and LHCb detector mass (5600 t vs. 4500 t): both sides
  of each conflict independently re-verified verbatim; genuinely unresolved by any source
  fetched.
- ALICE Technical Proposal exact date (year-precision only, CERN/LHCC/95-71 not fetched).
- LHCb pseudorapidity coverage, dipole field, RICH/VELO/calorimeter specs: JINST paper still
  blocked by CERN bot protection (re-confirmed this session).
- MoEDAL/detector status disagreement (finding 5): needs a MoEDAL-specific source, not
  guessed.

## Verdict per flagship

**ALICE — PASS with fixes applied.** All sourced facts (dates, results, masses, quotes)
independently re-verified accurate. One real cross-consistency bug found and fixed
(detector status contradicting experiment status during LS3). The 52 m/56 m depth conflict
is real, sourced on both sides, and transparently flagged — not a defect.

**LHCb — PASS with fixes applied.** All sourced facts independently re-verified accurate,
including all three flagship results verbatim. The suspicious `date_completed` field was
confirmed genuine (not fabricated) but its confidence was appropriately downgraded given
cross-comparison with ATLAS/LHCf's honest "9999" placeholder. Same detector/experiment
status bug found and fixed. The 5600 t/4500 t mass conflict is real, sourced on both sides,
and transparently flagged — not a defect.

**FASER, TOTEM, LHCf, MoEDAL — mandatory bar met**, plus the LS3-status bug found and fixed
for FASER/TOTEM/LHCf. MoEDAL's status disagreement is flagged, not fixed (see finding 5).

**SND@LHC — the primary target item was a genuine P1 defect, now fixed.** Status corrected
from `approved` to a properly sourced `active` (2022) → `shutdown` (LS3) history, using the
collaboration's own 2023 PRL, which the prior researcher did not find despite it being
directly named in the verification brief.

## Validator

`.venv/bin/python -m hepgraph.atlas.validate` (via
`/Users/yatharthsirohi/Desktop/HEP-Graph/.venv/bin/python`): **0 errors attributable to any
file in this partition** (checked by filtering the full validator output for every entity id
and filename in this partition, before and after all fixes). Total repo-wide error count
fluctuates run to run because other wave-3 leads write to the same shared `data/atlas/`
tree concurrently, per the project's known-shared-tree convention; none of the errors present
in either run belong to alice/lhcb/faser/snd-lhc/lhcf/totem/moedal/the four new sites/any
`colliders-lhc-*` source.
