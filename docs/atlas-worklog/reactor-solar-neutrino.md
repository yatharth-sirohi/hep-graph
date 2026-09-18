# reactor-solar-neutrino — research log

## Scope

Wave 3 (v1.0) workstream covering 11 reactor/solar-neutrino experiments listed
in `data/atlas/coverage/reactor-solar-neutrino.json`: Daya Bay, Double Chooz,
JUNO, KamLAND, RENO, Borexino, GALLEX/GNO, Homestake, SAGE, SNO, SNO+.

Subagent capacity for this session was saturated for most of the run (a
20-concurrent-subagent cap shared across 16 wave-3 leads); per the
coordinator's explicit instruction, all research after the initial blocked
attempts was performed directly in this agent, sequentially, one experiment
at a time, with files written as each experiment finished rather than batched
at the end.

This log is updated incrementally as each experiment is finished, in the
order: JUNO, Daya Bay, KamLAND, SNO, SNO+, Double Chooz, RENO, Borexino,
GALLEX/GNO, SAGE, Homestake.

## Entities written so far

### JUNO (flagship — full depth)

- `facility:juno-jiangmen`, `site:juno-jiangmen-underground-lab`,
  `experiment:juno`, `detector:juno`, `collaboration:juno`
- `document:juno-cdr` (2015 CDR, arXiv:1508.07166), `document:juno-physics-and-detector`
  (2021 review paper, arXiv:2104.02565)
- `result:juno-oscillation-parameters-2026` (Nature 654, 343–348 (2026),
  "Measurement of reactor neutrino oscillation with the first JUNO data"),
  `result:juno-initial-performance-2026` (Chin. Phys. C 50, 043001 (2026),
  "Initial performance results of the JUNO detector")
- 10 sources under `src:juno-*`

### Daya Bay (mandatory bar)

- `facility:daya-bay-reactor-neutrino-lab`, `site:daya-bay-experimental-halls`,
  `experiment:daya-bay`, `detector:daya-bay-antineutrino-detectors`,
  `collaboration:daya-bay`
- `result:daya-bay-observation-2012` ("Observation of electron-antineutrino
  disappearance at Daya Bay", PRL 108, 171803 (2012), 5.2σ)
- 4 sources under `src:daya-bay-*`

### KamLAND (mandatory bar)

- `site:kamioka-kamland` (new, under the EXISTING `facility:kamioka-observatory`
  owned by japan-neutrino — that facility file was not touched),
  `experiment:kamland`, `detector:kamland` (id fixed exactly as required by the
  neutrino-mass-0νββ lead's `kamland-zen` files, which already exist on disk
  and reference this id), `collaboration:kamland`
- `result:kamland-first-results-2002` ("First Results from KamLAND: Evidence
  for Reactor Anti-Neutrino Disappearance", arXiv:hep-ex/0212021, verbatim
  title confirmed by direct fetch, not assumed from the brief's paraphrase)
- 4 sources under `src:kamland-*`

## Sources added

All `src:juno-*`, `src:daya-bay-*`, `src:kamland-*` files under
`data/atlas/sources/` (see file listing; not duplicated here for brevity).
Every one was fetched directly with WebFetch (or reached via an INSPIRE API
WebFetch) in this session; `retrieval: "partial"` throughout since WebFetch
returns a processed/summarised extraction rather than raw full text.

## Conflicts found

- **JUNO baseline**: CDR (arXiv:1508.07166, 2015) says "53 km"; the 2026
  Nature paper says "52.5 km". Chose 52.5 km (more precise, more recent,
  peer-reviewed) as the `key_specs` value, noted the CDR's rounder figure.
- **KamLAND overburden**: Wikipedia states "105 m.w.e.", which is implausible
  next to the ~2700 m.w.e. established for the same Kamioka/Mozumi mine by
  `facility:kamioka-observatory` (sourced by japan-neutrino from the ICRR page
  and the Super-K NIM paper). Chose to record neither value (left null) rather
  than propagate a likely-erroneous secondary figure or silently override
  another workstream's better-sourced number.
- **Daya Bay AD count**: 6 antineutrino detectors in the 2012 discovery-paper
  configuration vs. 8 in the final configuration (2013 detector-assembly
  paper). Both recorded as separate intervals with different labels rather
  than collapsed to one.

## Unresolved fields (see also each coverage row's `missing_fields`)

- JUNO: no rank≤ 7 source found for the underground hall's exact coordinates
  despite an extensive search (CDR full text via a 328-page PDF text search
  for "latitude/longitude/coordinate", the 2021 physics paper, an arXiv
  radon-control paper, and Wikipedia's own citation trail, which itself
  resolves to an uncited 2014 conference slide). Recorded `kind: campus`,
  `confidence: approximate` per v0.2 A17/A23 (the newly-added amendment that
  downgrades this from a validator error to a warning
  `coordinate-kind-approximate`) rather than fabricating precision.
- Daya Bay: the official experiment site (dayabay.ihep.ac.cn, and a Berkeley
  Lab mirror dayabay.lbl.gov) was unreachable (timeout / connection refused)
  on every attempt; all facts instead come from INSPIRE, the 2012 discovery
  paper, the 2013 detector-assembly paper, and Wikipedia. Hall-specific
  coordinates for the near/near/far halls were not found in any rank≤ 7
  source, so one shared campus/approximate point stands in for all three
  (see `site:daya-bay-experimental-halls` note).
- KamLAND: the official site's homepage loaded but every guessed URL for a
  technical/"About KamLAND" sub-page 404'd; detector structural specs (PMT
  count, vessel dimensions) and coordinates rely on Wikipedia only.

## Dangling references to ids another lead owns

- None yet for JUNO/Daya Bay/KamLAND (Daya Bay and JUNO's facilities are
  wholly own-created; KamLAND's site sits under the pre-existing
  `facility:kamioka-observatory`, owned by japan-neutrino, referenced only).
- Remaining experiments (SNO, SNO+, Double Chooz, Borexino, GALLEX/GNO, SAGE,
  Homestake) will reference `facility:snolab`/`site:snolab-*` and
  `site:lngs-hall-a`/`site:lngs-hall-c` (owned by the `facilities` lead, not
  yet landed) — expected dangling references, to be listed here as each
  experiment is written.

## Children spawned and re-verification

Four `Agent` launches were attempted for Wave 1 delegation (Daya Bay+RENO+
Double Chooz, JUNO, KamLAND+Borexino, SNO+SNO+) at `model: sonnet`, all of
which failed immediately with "Concurrent subagent limit reached" (a 20-slot
cap shared by 16 wave-3 leads running at the same time). Per the
coordinator's explicit instruction, no further delegation was attempted;
**all research and writing above was performed directly by this lead agent**,
so there is no child output to re-verify — every source cited above was
fetched directly in this session and its quotes checked against the fetched
content before being written into a JSON file.

## Confidence summary (running)

JUNO: high confidence on the two published 2026 results and the CDR/physics-
book facts; low confidence on the exact hall coordinate (flagged, downgraded
to `campus`/`approximate`) and on membership counts (sourced from IHEP's
press release rather than a dedicated JUNO members page). Daya Bay: high
confidence on the 2012 discovery result and baseline/reactor-power figures
(direct from the PRL abstract); low confidence on hall coordinates,
membership counts and most interval dates (official site unreachable).
KamLAND: high confidence on the 2002 first-results paper; low confidence on
detector structural specs and coordinates (Wikipedia-only) and the collab's
membership.

### SNO (mandatory bar)

- `experiment:sno`, `detector:sno`, `collaboration:sno` (referencing the
  EXISTING `facility:snolab`/`site:snolab-underground-lab`, owned by the
  `facilities` lead — those files were not touched; reused the existing
  `src:sno-nim-detector-paper-2000` source record after independently
  re-fetching the same arXiv page in this session).
- `result:sno-cc-evidence-2001` (arXiv:nucl-ex/0106015, 3.3σ evidence) and
  `result:sno-nc-evidence-2002` (arXiv:nucl-ex/0204008, 5.3σ evidence,
  "Direct Evidence for Neutrino Flavor Transformation..."), both verbatim
  titles/abstracts confirmed by direct fetch.
- A full, day/month-precision, sourced interval history (cavity excavation
  1990-03/1993-05, construction to 1999-04, commissioning 1999-05/1999-11,
  three data-taking phases with month precision, shutdown 2006-11, drained
  2007-05) came directly from the official site's own "SNO Milestones" page.
- 6 sources under `src:sno-*`.

### SNO+ (mandatory bar)

- `experiment:sno-plus`, `detector:sno-plus`, `collaboration:sno-plus`
  (referencing the same existing `facility:snolab`/`site:snolab-underground-lab`).
  `experiment:sno-plus.lineage` carries the canonical `upgrade_of`
  `experiment:sno` row.
- `distinct_from` added on both the `sno`/`sno-plus` collaboration and
  detector pairs after the validator flagged a normalised-name collision
  ("SNO+" strips to the same slug as "SNO" once punctuation is removed).
- No results written this pass (time-boxed to the mandatory bar); the
  official site mentions a January 2025 reactor-oscillation result and a
  December 2024 low-background solar-scattering result, both left as
  `missing_fields` rather than fabricated without reading the actual papers.
- 3 sources under `src:sno-plus-*`.

### Double Chooz (mandatory bar)

- `facility:chooz` (EXACT id, also referenced by the cevns workstream for
  NUCLEUS — confirmed via `grep`/`ls` that `site:chooz-very-near-nucleus`
  already exists on disk referencing this facility id once it landed),
  `site:double-chooz-near-detector`, `site:double-chooz-far-detector`,
  `experiment:double-chooz`, `detector:double-chooz`,
  `collaboration:double-chooz`.
- `result:double-chooz-evidence-2012` ("Reactor electron antineutrino
  disappearance in the Double Chooz experiment", arXiv:1207.6632, 2.9σ
  evidence).
- 4 sources under `src:double-chooz-*` plus `src:chooz-npp-wikipedia`.

### RENO (mandatory bar)

- `facility:yonggwang-hanbit-reactor-site`, `site:reno-near-detector`,
  `site:reno-far-detector`, `experiment:reno`, `detector:reno`,
  `collaboration:reno`.
- `result:reno-observation-2012` ("Observation of Reactor Electron
  Antineutrino Disappearance in the RENO Experiment", arXiv:1204.0626, 4.9σ
  observation).
- 3 sources under `src:reno-*` plus `src:hanbit-npp-wikipedia`.

### Cross-lead fix: detector:kamland <-> experiment:kamland-zen

Per the coordinator's request, added `experiment:kamland-zen` to
`detector:kamland.experiment_ids` (as a sourced relationship object, not a
bare string) after independently fetching the full text of the original
KamLAND-Zen paper (arXiv:1211.3863) and finding the exact sentence: "The
KamLAND-Zen ... experiment consists of 13 tons of Xe-loaded liquid
scintillator ... suspended at the center of the KamLAND detector by film
straps." New source `src:kamland-zen-arxiv-1211-first-phase` added.

## Conflicts found (continued)

- **RENO/Double Chooz/SNO/SNO+ "no confirmed shutdown or continuation"
  intervals**: several 2012-era discovery papers report only a fixed
  analysis-window dataset (e.g. RENO's 229-day window). Rather than either
  fabricate a shutdown date or assert indefinite continued operation from
  memory, these intervals were left `end: null` (which the ontology defines
  as "ongoing at `verified_at`", not a claim of certainty) with an explicit
  note; this produced (and then resolved) several `status-not-derived-state`
  validator errors during this pass.
- **SNO name collision**: "SNO Collaboration"/"SNO+ Collaboration" and "SNO
  detector"/"SNO+ detector" normalise (per A20: lower-case, strip
  non-alphanumerics) to the same string once the "+" is stripped. Resolved
  with reciprocal `distinct_from` fields rather than renaming either record.

## Validator posture

After each pair of experiments, `hepgraph.atlas.validate` was run and every
`[error]`-level finding attributable to this workstream's own files was
fixed (added missing `note`/`quote`/`locator` fields, split collapsed
terminal-status intervals into an operating interval + a terminal event per
A3, fixed `display` strings that drifted from `value` by more than an order
of magnitude, added `distinct_from` for the SNO/SNO+ name collision, and
gave each of this workstream's new facilities at least one interval so its
`status` field has something to derive against). The **one intentional
exception** is `coordinate-kind-approximate` warnings (v0.2 A23, added
mid-session): every site this workstream created without a rank≤ 7
coordinate source is deliberately left `kind: campus`/`confidence:
approximate` rather than mislabelled `detector`/`underground_lab` to pass
validation — this now warns rather than fails, per A23.

*(Log continues below as Borexino, GALLEX/GNO, SAGE and Homestake are
completed.)*
