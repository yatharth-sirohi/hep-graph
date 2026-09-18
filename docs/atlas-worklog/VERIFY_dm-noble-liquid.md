# Independent verification: dm-noble-liquid (wave 3)

Verifier session, 2026-09-17. Worked in `/Users/yatharthsirohi/Desktop/HEP-Graph-atlas-v1`
(branch `hep-atlas-v1`), no git commands. Did not trust
`docs/atlas-worklog/dm-noble-liquid.md`; every critical value below was
re-fetched independently with WebFetch (and one raw `curl` pull of an arXiv
abstract and the LNGS Hall C page, to get ground-truth text a summarizer might
paraphrase).

## Records checked

Experiments/detectors/collaborations: `xenon1t`, `xenonnt`, `pandax-4t`,
`darkside-50`, `darkside-20k`, `deap-3600` (6 experiments, 6 detectors, 4
collaboration files: `xenon`, `pandax-4t`, `darkside`, `deap-3600`). Results:
`xenon1t-electronic-recoil-excess-2020`, `xenonnt-first-nr-search-2023`,
`xenonnt-b8-cevns-indication-2024`. Document: `xenonnt-instrument-paper`. All
26 `src:dm-noble-liquid-*` source records (metadata, `source_type`, `retrieval`
honesty; duplicate URL/DOI/arXiv check against the whole `data/atlas/sources/`
tree -- none found).

## Sources re-fetched (count: 14 distinct URLs/documents)

`arxiv.org/abs/2402.10446` (XENONnT instrument paper), `arxiv.org/abs/2408.02877`
(B8 CEvNS indication), `xenonexperiment.org/history/` (fetched twice: once
broad, once to confirm one exact sentence verbatim), `xenonexperiment.org/collaboration/`,
`www.snolab.ca/experiment/deap-3600/`, `www.lngs.infn.it/en/darkside` (fetched
twice via WebFetch + once via raw `curl` for ground-truth text),
`darkside.lngs.infn.it/` and `darkside.lngs.infn.it/?page_id=32`,
`arxiv.org/abs/2402.07566` (DarkSide-20k JINST), `pandax.sjtu.edu.cn/`,
`arxiv.org/abs/2006.09721` (XENON1T excess), `arxiv.org/abs/2303.14729`
(XENONnT first NR search), `arxiv.org/abs/1705.06655` (XENON1T first results,
fetched via WebFetch and raw curl for verbatim abstract), `arxiv.org/abs/2107.13438`
(PandaX-4T commissioning, ditto), `arxiv.org/abs/2207.11966` (DarkSide-50
low-mass 2023, ditto), `ar5iv.labs.arxiv.org/html/1712.01982` (DEAP-3600
detector paper, independent re-check of the researcher's own re-check).

## Findings

| # | Severity | Claim | Issue | Fix |
| - | -------- | ----- | ----- | --- |
| 1 | **P0** | `result:xenonnt-b8-cevns-indication-2024` `result_type` | Recorded as `first_detection` for a paper titled "**First Indication** of Solar 8B Neutrinos..." reporting only a **2.73σ** rejection of the background-only hypothesis (confirmed verbatim from the abstract). `first_detection` has **no keyword requirement** in `RESULT_CLAIM_KEYWORDS` (schema.py), so the mechanical A16 check never catches this -- it's a purely semantic defect. Elsewhere in this atlas `first_detection` is reserved for events that were actually detected (`icecube-glashow-resonance-candidate-2021`, `kamiokande-sn1987a-1987`), not a sub-evidence-threshold statistical indication. The record's own `notes` field argued this was the "conservative" choice, which is backwards: to a reader, "first_detection" reads as stronger than "evidence" or "observation", not weaker. This atlas already has the correct precedent for exactly this situation: `result:t2k-electron-neutrino-indication-2011`, a 2.5σ "indication" paper, is recorded as `measurement` with a note explaining the enum has no "indication" tier. | Changed `result_type` to `measurement`, matching the T2K precedent; rewrote the `notes` entry to explain the correction and cite the precedent. |
| 2 | **P2** | DarkSide-20k active mass quote, 4 occurrences (`experiment:darkside-20k.facility_roles[0].quote`, `.key_specs[0].quantity.quote`; `detector:darkside-20k.placements[0].quote`, `.specs.active_mass.quote`) and the source excerpt (`src:dm-noble-liquid-darkside-lngs-page`) | All quoted "...a two-phase LAr detector with a **50 tonnes active mass**" from `lngs.infn.it/en/darkside`. Raw-HTML ground truth (`curl`, confirmed independently) shows the page actually says "...a two-phase LAr detector with a **50 tonnes active volume**" -- "mass" was substituted for "volume". The *value* (50 t) is correct and matches the page; only the quoted wording was fabricated, violating A15's "verbatim" requirement for `quote`. (The same page separately states a more precise "49.7 t" active-volume figure elsewhere, for a different sentence about the TPC's PDU layout -- not confused with the 50 t figure, so no value-level error.) | Replaced the fabricated word in all 5 places with the verbatim phrase "50 tonnes active volume, 1000 times more than its predecessor DarkSide-50" (a real, longer verbatim substring of the source). |
| 3 | **P1** | DarkSide-50 operating-interval quote "**operated from 2013 to 2020**", 4 occurrences (`experiment:darkside-50.intervals[2,3].quote`, `detector:darkside-50.intervals[0,1].quote`) | Not a real substring of the LNGS page. Raw-HTML ground truth: "The DarkSide collaboration **operated** the DarkSide-50 detector, a dual-phase argon Time Projection Chamber (TPC), developed for use in a search for direct evidence of dark matter **from 2013 to 2020**." The two halves are ~15 words apart in one sentence; splicing them into a contiguous "quote" fabricates text that was never contiguous in the source. The underlying *fact* (2013-2020) is correctly supported by that same sentence, so this is a quote-fidelity defect, not a wrong value. | Replaced all 4 occurrences with the real, full, contiguous sentence (195 chars, within the 300-char cap) and rewrote the source excerpt (`src:dm-noble-liquid-darkside-lngs-page`) to stop stitching fragments together. |
| 4 | **P1** | Unsourced quantitative claims in `summary.technical` for `experiment:xenon1t` (7.7e-47 cm² at 35 GeV/c²), `experiment:pandax-4t` (3.8e-47 cm² at 30 GeV/c²), `experiment:darkside-50` (6e-43 cm² at 3 GeV/c²) | Each technical summary states a specific WIMP-nucleon cross-section limit as prose, but **no `key_specs` entry, no `result:` record, and no sourced field anywhere in the record backs the number** -- it exists only as free text. This is exactly the "no claims absent from sourced fields" failure mode the brief asked me to check for. For DarkSide-50 the situation was compounded: the source that supports the number (`src:dm-noble-liquid-darkside-50-lowmass-2023`, arXiv:2207.11966) was fetched and its `excerpt` already contained the correct number, but the source was **cited by nothing** (a live A22 validator warning I confirmed before fixing). I independently re-fetched all three abstracts (`arxiv.org/abs/1705.06655`, `/2107.13438`, `/2207.11966`) via both WebFetch and raw `curl` and confirmed all three numbers exactly. | Added a sourced `key_specs` entry (dimension `cross_section`, unit `cm^2`) to each of the three experiment records, citing the already-fetched source with a `locator` (abstract sentence) and `verified_at: 2026-09-17`. For DarkSide-50, also added the previously-uncited source to the record's top-level `sources` array, which resolves the A22 "cited by nothing" warning. |
| 5 | **P2** | `collaboration:xenon.summary.technical` said "...since **2006 (XENON10)**" while the record's own sourced `formation` value is **2002** (XENON10 development start, per the same quoted sentence: "development... started in 2002... XENON10 (operated 2006-2007)") | Internal inconsistency between the sourced field and the free-text summary describing the same fact with a different anchor year. | Reworded the technical summary to state both years consistently with the sourced quote ("since XENON10's development began in 2002 (XENON10 itself operated 2006-2007)"). |

## Items checked with no defect found

- **XENONnT mass**: instrument paper (arXiv:2402.10446) abstract confirmed
  verbatim: "It features an active target of 5.9 tonnes of cryogenic liquid
  xenon (8.5 tonnes total mass in cryostat)." Both `experiment:xenonnt` and
  `detector:xenonnt` correctly use 8.5 t / 5.9 t as the primary values and
  correctly note the collaboration site's rounded "about 8.6 tonnes" (also
  independently verified verbatim on `xenonexperiment.org/history/`) as a
  secondary, non-primary figure.
- **XENON1T interval dates**: the brief asked me to check "2016-2018"; the
  actual record correctly says **2015-2018** for the science-operations
  interval (matching the official history page's "ran ... from 2015 until
  2018" verbatim) and separately, correctly, records the 2016-11 to 2017-01
  first-results *run* as a narrower `kind: run` sub-interval. December 2018
  shutdown/upgrade-to-XENONnT wording verified verbatim. No error.
- **XENONnT commissioning/science-run boundary**: the record honestly carries
  two candidate anchors (2020 official-site wording vs. 2021-07-06 INSPIRE
  `date_started`) as two separate, clearly-labelled, non-conflicting
  intervals rather than picking one and hiding the other. No error.
- **DarkSide-20k construction status / DarkSide-50 end / DEAP-3600 "Upgrading"
  status**: `snolab.ca/experiment/deap-3600/` independently re-fetched,
  confirmed the literal word "Upgrading"; `lngs.infn.it/en/darkside`
  independently confirmed "operated from 2013 to 2020" (DarkSide-50, fact
  correct, only the *quote* needed a fix -- see finding 3) and "currently
  under construction" / "foreseen to begin operations in 2027" for
  DarkSide-20k, consistent with the record's schedule-conflict note (2027 vs.
  arXiv:2402.07566's "late 2026").
- **LNGS Hall B / Hall C and PandaX-4T at CJPL-II**: all placements verified
  against the cited sources. Note: `facility:cjpl`, `site:cjpl-ii`,
  `site:lngs-hall-c`, `facility:snolab`, `site:snolab-underground-lab`,
  which the researcher's worklog logged as **dangling references owned by the
  facilities workstream**, now all **exist** in `data/atlas/facilities/` and
  `data/atlas/sites/` (the facilities lead has since landed). This isn't a
  defect -- the references now resolve correctly and I confirmed no
  duplication or conflict -- but it means the worklog's "dangling reference"
  characterization is stale as of this verification.
- **Lineage direction (A1)**: `experiment:xenonnt` correctly stores
  `predecessor`/`upgrade_of` rows pointing at `experiment:xenon1t` on its own
  (successor's) record; `experiment:darkside-20k` correctly stores
  `predecessor` pointing at `experiment:darkside-50` on its own record.
  Matches the `lz.json` exemplar's convention; no `successor`/`upgraded_to`
  rows were incorrectly authored (those are derived-only per A1).
- **Quantities/units re-checked against primary sources**: XENON1T (3.2 t /
  2.0 t, arXiv:1708.07051), DarkSide-50 (50 kg nominal / 46.4±0.7 kg measured,
  30 t scintillator veto, 1 kt water Cherenkov veto, all from arXiv:1410.0653),
  DEAP-3600 (3600 kg design / 1000 kg fiducial at 55 cm / 6000 m.w.e. / 255
  PMTs, all re-verified independently against `ar5iv.labs.arxiv.org/html/1712.01982`
  in addition to the researcher's own claimed re-check), PandaX-4T (6 t total
  / 4 t sensitive target design, 3.7 t / 0.63 t·y commissioning-run figures).
  All matched exactly.
- **Result claims re-verified against abstracts**: XENON1T 2020 excess
  (2-3 keV excess, 3.4σ axion / 3.2σ neutrino-magnetic-moment / 3.0σ global
  4.0σ local bosonic-DM interpretation, all exact); XENONnT 2023 first NR
  search (2.58e-47 cm² at 28 GeV/c², 3.3-60.5 keV window, 1.1 t·y exposure,
  all exact).
- **source_type / retrieval honesty**: `inspire_experiment_record` used
  correctly (valid A18 enum value, rank 3); no source improperly marked
  `retrieval: summary` while carrying a `quote`; no `failed` source cited.
- **Duplicates**: scripted a full URL/DOI/arXiv-id collision check across
  every file in `data/atlas/sources/` (not just this domain) -- zero
  duplicates.
- **PandaX-4T `specs.phase: null`**: independently confirmed by fetching the
  commissioning-run abstract myself -- it does not use "dual-phase"/"two-phase"
  for PandaX-4T. Leaving it null (rather than assuming from sibling
  experiments) is the correct, A17-compliant choice, not an omission.
- **DarkSide-50 `external.inspire_experiment: null`**: plausible and
  consistent with how DarkSide-20k's own INSPIRE record (1830577) doesn't
  mention a DarkSide-50 sibling record; not independently re-queried against
  the INSPIRE API (would cost an extra INSPIRE request under the shared
  rate-limit etiquette rule for a low-risk, well-explained null), but the
  record's own note is specific and falsifiable if wrong.

## Unverifiable / left as-is

- Collaboration `formation` dates for all four collaborations (XENON 2002,
  DarkSide 2012, PandaX-4T 2021, DEAP-3600 null): no better source exists;
  correctly left as lower-bound proxies with `confidence: uncertain`, not
  claimed as true founding dates. Not re-searched further (would require the
  same web search the researcher already did, with the same likely
  no-result outcome).
- DarkSide-20k's true construction-start date and the late-2026-vs-2027
  schedule conflict: both sources (arXiv:2402.07566, LNGS page) independently
  re-confirmed; the conflict is real, not a research error, and the record
  handles it correctly (two schedules quoted, no invented resolution).

## Validation

`.venv/bin/python -m hepgraph.atlas.validate`: **0 errors attributable to any
file in this domain**, before and after fixes. (One pre-existing, unrelated
error elsewhere in the repo, `experiments/ship.json`, is outside this scope.)
The one domain warning that changed is `sources/dm-noble-liquid-darkside-50-lowmass-2023.json:
cited by nothing`, which is now resolved by finding 4's fix. All remaining
warnings touching this domain's files (SList shape for `physics_goals`/
`unique_capabilities`; derived `*_ids` fields present in source files; "no
accelerator active" for `direct_dark_matter` kind experiments; "start
unknown" for DarkSide-50's earliest interval) are the same pre-existing,
repo-wide conventions visible in the `lz.json` exemplar and essentially every
peer experiment file in the atlas, not defects in this domain.

## Verdict

**One P0, two P1, two P2 findings, all fixed in place** during this
verification session. The P0 (XENONnT CEvNS `result_type`) was the most
serious: it would have shown a 2.73σ statistical indication to a reader of
the atlas as if it were a confirmed detection, which is exactly the kind of
overclaim the ontology's A16 wording rule and this project's correctness
rules exist to prevent, and the automated validator cannot catch it because
`first_detection` carries no keyword check. Every other checked value
(masses, dates, statuses, placements, result numbers, lineage direction,
source honesty, duplicates) matched its cited source exactly on independent
re-fetch. With the five fixes applied, this domain's records are accurate to
their sources and I have no further findings.
