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

*(Log continues below as SNO, SNO+, Double Chooz, RENO, Borexino, GALLEX/GNO,
SAGE and Homestake are completed.)*
