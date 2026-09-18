# neutrino-mass-0vbb — Wave 3 domain lead worklog

## Scope

Owner of coverage file `data/atlas/coverage/neutrino-mass-0vbb.json`: 11 non-flagship
experiments spanning neutrinoless double-beta decay (0νββ) and direct kinematic
neutrino-mass measurement — GERDA, LEGEND, Majorana Demonstrator (germanium);
EXO-200, nEXO, KamLAND-Zen, NEXT (xenon); CUORE, CUPID (cryogenic bolometers);
KATRIN, Project 8 (direct mass). Mandatory bar per `WAVE3_LEAD_BRIEF.md`: no
full-depth extras (no results/documents required; KATRIN's upper-limit result
added as a bonus). No membership rosters, no `people/` files, in this wave.

Delegation note: the shared session-wide cap of 20 concurrent subagents was
exhausted by other Wave 3 leads for the entire working session. Every `Agent`
call I made (one batch of 4, then a batch of 2) returned "Concurrent subagent
limit reached"; per the coordinator's explicit correction mid-task, I did not
retry in a loop and instead researched and wrote every one of the 11
experiments myself, sequentially, via WebSearch/WebFetch. No children were
spawned or needed re-checking as a result — every source below was fetched and
read directly by me in this session.

## Entities written

**Experiments** (`data/atlas/experiments/`): gerda, legend, majorana-demonstrator,
exo-200, nexo, kamland-zen, next, cuore, cupid, katrin, project-8.

**Detectors** (`data/atlas/detectors/`): gerda, legend-200, majorana-demonstrator,
exo-200, nexo, next-white, next-100, cuore, cupid, katrin, project-8.
(No `detector:legend-1000` — insufficient sourcing for a real record, per the
brief's instruction not to fabricate. No `detector:kamland-zen` — per
ID_REGISTRY it references the shared `detector:kamland` instead; see
"Dangling references" below.)

**Collaborations** (`data/atlas/collaborations/`): gerda, legend,
majorana-demonstrator, exo-200, nexo, kamland-zen, next, cuore, cupid, katrin,
project-8.

**Facilities** (`data/atlas/facilities/`, new, owned by this lead):
`facility:wipp` (EXO-200's host), `facility:kit-karlsruhe` (KATRIN's host).

**Sites** (`data/atlas/sites/`, new): `site:wipp-surface-campus`,
`site:kit-campus-north`.

**Results**: `results/katrin-neutrino-mass-upper-limit-2025.json` (the one
bonus result the brief asked for if time allowed).

**Sources**: 34 `src:` records under `data/atlas/sources/`, one per page
actually fetched via WebFetch or WebSearch→WebFetch this session, prefixed by
experiment slug (`src:gerda-…`, `src:katrin-…`, etc.) following the repo's
established per-experiment convention (consistent with `src:nova-…` etc. in
the exemplars) rather than the long `src:neutrino-mass-0vbb-…` form, since
experiment slugs are already uniquely owned by this lead and grepped for
collisions before creation.

**Coverage**: `data/atlas/coverage/neutrino-mass-0vbb.json` rewritten with
honest `researched: "partial"` and a real `status` + itemised `missing_fields`
for all 11 rows (previously all `"researched": "none"`).

## Sources added (representative; see `sources/` for the full 34)

GERDA: `src:gerda-mpi-hd-official-site` (official site, rank 1),
`src:gerda-mpp-institute-page`, `src:gerda-final-results-prl-2020` (arXiv:2009.06079),
`src:gerda-searching-conf-2017`. LEGEND: `src:legend-official-site`,
`src:legend-collaboration-page`, `src:legend-200-first-results-arxiv-2509`
(arXiv:2509.21166), `src:legend-wikipedia-overview` (rank 12, pointer only).
Majorana: `src:majorana-demonstrator-surf-news`,
`src:majorana-demonstrator-final-results-arxiv-2207` (arXiv:2207.07638),
`src:majorana-demonstrator-sdsmt-news`. EXO-200/nEXO: `src:exo-200-doe-wipp-official-page`,
`src:exo-200-wipp-wikipedia` (rank 12, campus point only), `src:exo-200-final-results-arxiv-1906`
(arXiv:1906.02723), `src:nexo-llnl-official-page`, `src:nexo-arxiv-1805-pcdr`
(arXiv:1805.11142). KamLAND-Zen: `src:kamland-zen-arxiv-2203-inverted-ordering`,
`src:kamland-zen-arxiv-2406-complete-dataset`. NEXT: `src:next-official-site`,
`src:next-collaboration-page`, `src:next-arxiv-1210-4020-original-proposal`,
`src:next-arxiv-2201-10907-status`. CUORE/CUPID: `src:cuore-arxiv-2404-lepton-number-violation`,
`src:cuore-lbl-newscenter-2025`, `src:cupid-experiment-official-page`,
`src:cupid-arxiv-2503-02894`. KATRIN: `src:katrin-official-site`,
`src:katrin-arxiv-2406-13516` (arXiv:2406.13516 / Science 388, 180-185),
`src:katrin-kit-campus-north-coordinates` (geocoder, campus point only).
Project 8: `src:project8-official-site`, `src:project8-doe-highlight-2015`,
`src:project8-arxiv-2503-08807-phase2`, `src:project8-cenpa-npl-node-1554`.

## Conflicts

| claim | source A | source B | chosen | why |
| --- | --- | --- | --- | --- |
| GERDA end date | MPP institute page: "nine-year lifetime" (→2020) | Final-results PRL: submitted 2020-09 | Recorded a `completed` interval starting 2020 (year precision), with a separate `active` interval ending 2019-11 for Phase II data collection | Neither source gives an exact shutdown day; the two are consistent at year precision |
| EXO-200 phase structure | Secondary web summaries: Phase I 2011-2014, pause (WIPP incident), Phase II 2016-2018 | Directly fetched final-results paper: overall 2011-2018, 234.1 kg·yr | Recorded only the overall 2011-2018 span as sourced; the finer phase boundaries are reported in `notes` as unverified | The phase-boundary claim was never seen verbatim in a page this agent fetched directly (only in WebSearch synthesis text), so per A17 it is not encoded as a sourced value |
| CUORE isotope/detector mass | LBL news article: "988 crystals ... approximately 0.8 tonnes" | Secondary literature: "reached the tonne mass scale" | Recorded 0.8 t (the directly quoted figure) with a note flagging the "tonne-scale" framing as including non-crystal structural mass | Only the 0.8 t figure was seen verbatim in a fetched page |
| CUPID status | Official site: future tense only ("CUPID will…") | Secondary summary: DOE CD-0 approved, prototype "in construction" for mid-2025 | Recorded `status: proposed` (conservative) | The CD-0/construction claim was not seen verbatim in a directly fetched primary source in this session |
| Project 8 Phase III sensitivity unit | CENPA seminar page: "40 meV" | Ontology's `mass_energy` dimension has no meV unit | Recorded value/unit as 0.04 eV/c² with `display: "~0.04 eV/c^2 (40 meV)"` | A21 requires the parsed `display` number to match `value` within a factor of 10; converting satisfies both the ontology's fixed unit list and A21 |

## Unresolved fields

- Legend-1000's host site (LNGS vs SNOLAB) — not sourced to a confident, current decision; no site placement recorded, per the brief's explicit instruction not to guess.
- Exact Phase I/Phase II boundary dates for EXO-200; exact KamLAND-Zen 800 start date; exact NEXT-White start/end dates (all recorded as best-effort lower/upper bounds with `confidence: uncertain` and explicit notes, never presented as verified precision).
- Collaboration formation dates for all 11 collaborations — no source fetched in this session states an explicit formation date for any of them; all left `null` with a note, using a sourced lower-bound `start` on the collaboration's own `intervals` entry only where needed to avoid a null/null interval degenerating to "no presence" under the v0.2 A3 timeline model (see "Timeline-derivation fixes" below).
- INSPIRE experiment-registry recids for all 11 experiments — not looked up in this session (INSPIRE etiquette: ≤1 request/10s, and time was prioritized on primary-source research instead); all left `null` with a note. These are tier B, so a note suffices per the brief.
- CUORE/CUPID/KATRIN/Project 8/NEXT/nEXO/KamLAND-Zen/GERDA/LEGEND/Majorana/EXO-200 all lack results files beyond KATRIN's; non-flagship results were explicitly optional and only attempted where time allowed after the mandatory bar was met for all 11.
- Project 8's Phase II/III precise start dates (only publication-date lower bounds recorded, per the same A3 reasoning).

## Dangling references (at time of writing; several resolved mid-session)

Several ids I reference were dangling (owned by other Wave 3 leads who had not
yet landed) for much of this session, then **resolved as those leads landed
their files while I was still working**. I verified this by re-checking
`data/atlas/{facilities,sites,detectors}/` directly before finalizing, and
updated the stale "dangling reference" notes in my own files accordingly
rather than leaving them incorrect:

- `site:lngs-hall-a` (facilities lead) — used by GERDA, LEGEND-200, CUORE, CUPID placements. **Resolved** (now exists).
- `facility:snolab` / `site:snolab-underground-lab` (facilities lead) — used by nEXO. **Resolved**.
- `facility:canfranc-underground-laboratory` / `site:lsc-canfranc` (facilities lead) — used by NEXT. **Resolved**.
- `detector:kamland` / `site:kamioka-kamland` (reactor-solar-neutrino lead) — used by KamLAND-Zen. **Resolved**. Per ID_REGISTRY, `experiment:kamland-zen` deliberately does **not** own a `detector:kamland-zen` file; it references the shared `detector:kamland` instead, with Xe-specific technology/specs kept in the experiment's own `key_specs`. I did not edit `detector:kamland` itself (owned by another lead) to add `kamland-zen` to its `experiment_ids` — that cross-lead addition is flagged here for the reactor-solar-neutrino lead or the orchestrator to make.
- `facility:university-of-washington-cenpa` / `site:uw-cenpa-campus` (axions lead, also hosts ADMX) — used by Project 8. **Resolved**; I confirmed via `ls` before writing that the axions lead's file existed at that point and referenced it rather than creating a duplicate, per the brief's explicit warning about this exact id.

No dangling references remain unresolved in my files as of the final validator run.

## Timeline-derivation fixes (v0.2 A3/A10)

Several of my first-draft intervals used `start: null, end: null` to mean "no
known formation/start date, but the entity is clearly still active/proposed."
The validator (correctly) treats a null/null interval as covering **no** date
at all (A3), so the derived state at the build date came out `None` while my
`status` field said `active`/`proposed` — an A10 `status-not-derived-state`
error. Following the precedent already in this repo (`facility:lngs`'s own
file documents exactly this problem and its resolution), I fixed every
instance in my own files by giving the interval a real **lower-bound** start
date from the earliest solid, sourced fact available (e.g. KATRIN/KIT: 2019,
its sourced operating start; CUPID: 2025, its earliest dated collaboration
paper; nEXO: 2018, its Pre-Conceptual Design Report), explicitly labelled in
each note as a lower bound and not a true formation/founding date. This
resolved all `status-not-derived-state` errors in my files (was 13, now 0) and
all `record-sources-required` / `display-value-mismatch` / `missing-required-field`
/ `quantity-unit` / duplicate-alias errors I introduced (validator run:
0 errors attributable to `neutrino-mass-0vbb` files at final check).

## Children spawned and what I re-checked

**None.** The session-wide concurrent-subagent cap (20, shared across all 16
Wave 3 leads) was saturated for the entire task; every `Agent` tool call
returned "Concurrent subagent limit reached", both for a batch of 4 and later
a batch of 2. Per the coordinator's explicit mid-task correction, I did not
retry in a loop and instead performed all research and writing myself,
directly, via WebSearch/WebFetch — so there is nothing to "re-check" in the
delegation sense: every quote and locator cited in every file was read by me
in this session.

## Confidence summary

- **High confidence** (verified, quote from a directly fetched primary/official source): GERDA and Majorana Demonstrator completion status and final half-life limits; LEGEND-200's first result; EXO-200's final dataset result; KamLAND-Zen's two most recent half-life limits; CUORE's ongoing operation and 2024 result; NEXT-100's 2024 commissioning; KATRIN's 2025 upper-limit result (both the experiment key_spec and the standalone result file); Project 8's Phase I University-of-Washington demonstration.
- **Moderate/uncertain confidence** (recorded with explicit notes, never silently upgraded): CUPID's construction status (kept conservative as "proposed"); nEXO's construction timeline; NEXT-White's exact run dates; EXO-200's internal phase boundaries and detector active mass; LEGEND-1000's host site (left with no site placement at all).
- **Coordinates**: only `site:wipp-surface-campus` and `site:kit-campus-north` were created by this lead, both correctly labelled `kind: campus`, `confidence: approximate`, sourced to a geocoder/Wikipedia point only (never used as a `detector`/`underground_lab` coordinate), per A17/A23.
- Zero facts on critical fields (coordinates, intervals, key specs, results) came from model memory; every one traces to a `src:` record with a `quote` or `locator` fetched in this session, or is `null` with a note explaining why it could not be sourced.
