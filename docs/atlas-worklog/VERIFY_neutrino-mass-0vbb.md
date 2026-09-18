# Independent verification: neutrino-mass-0vbb (wave 3)

Verifier session, 2026-09-17/18. Did not research these records originally; worked from
`docs/HEP_ATLAS_ONTOLOGY.md` amendments A1-A24 and `docs/atlas-worklog/RESEARCH_AGENT_RULES.md`
only, and treated `docs/atlas-worklog/neutrino-mass-0vbb.md` as untrusted. No git, no
subagents, worked in `/Users/yatharthsirohi/Desktop/HEP-Graph-atlas-v1` (branch `hep-atlas-v1`).

## Records checked

- **Experiments (11):** gerda, legend, majorana-demonstrator, exo-200, nexo, kamland-zen,
  next, cuore, cupid, katrin, project-8.
- **Detectors (11):** gerda, legend-200, majorana-demonstrator, exo-200, nexo, next-white,
  next-100, cuore, cupid, katrin, project-8.
- **Collaborations (11):** the same 11 programmes.
- **Results (1 in scope):** katrin-neutrino-mass-upper-limit-2025 (`kamland-first-results-2002`
  belongs to `experiment:kamland`, owned by the reactor-solar-neutrino lead, out of scope).
- **Facilities/sites owned by this lead (4):** facility:wipp, facility:kit-karlsruhe,
  site:wipp-surface-campus, site:kit-campus-north.
- **Coverage:** data/atlas/coverage/neutrino-mass-0vbb.json (all 11 rows).
- **Sources (~35 cited src: records read; see "Values re-fetched" below for which were
  independently re-fetched).**
- **Cross-checked, not edited (owned by other leads):** site:lngs-hall-a/-b/-c,
  detector:kamland, site:kamioka-kamland, site:surf-davis-campus-lz, facility:lngs,
  facility:surf, facility:snolab, facility:canfranc-underground-laboratory,
  facility:university-of-washington-cenpa — confirmed these now exist and resolve the
  dangling references the original agent flagged, and (for detector:kamland) confirmed
  its `experiment_ids` already includes `experiment:kamland-zen` with a proper sourced row.

## Values re-fetched

Approximately 35 WebFetch/WebSearch calls against ~20 distinct sources, at least once
each for: GERDA final-results abstract (arXiv:2009.06079) and the Phase I status paper
full text (arXiv:1710.07776); MAJORANA final-results abstract (arXiv:2207.07638) and the
SURF news page; EXO-200 final-results abstract (arXiv:1906.02723) and the detector design
paper full text (arXiv:1202.2192, for depth m.w.e. and active mass); KamLAND-Zen 2024
abstract (arXiv:2406.11438); CUORE 2024 abstract (arXiv:2404.04453) and the LBL press
release; LEGEND-200 first-results abstract (arXiv:2509.21166), the LEGEND official site,
and the LBL Nuclear Science Division article; KATRIN 2025 Science abstract
(arXiv:2406.13516); CUPID official page and arXiv:2503.02894 abstract; NEXT official
site, a specific NEXT news post, and arXiv:1210.4020; nEXO official site. Also searched
for (with mixed success) an explicit "Hall A" statement for CUORE, LEGEND-200 and CUPID
specifically (not just "at LNGS"), and for CUPID's DOE Critical-Decision stage.

## Findings by severity

### P0 — fabricated/non-verbatim `quote` fields presented as verbatim (A15/A18)

1. **GERDA** experiment `key_specs["Total exposure"].quantity.quote`: read "Total
   Exposure: 127.2 kg·yr (combining Phase I and Phase II data)" — this exact sentence
   does not appear in the cited paper. The abstract actually says "When combined with the
   result of Phase I, no signal is observed after 127.2 kg·yr of total exposure." **Fixed.**
2. **GERDA** experiment `intervals[Phase I].quote`: read "Phase I data taking of GERDA has
   started in November 2011 ... finished in May 2013 with 21.6 kg yr of exposure" —
   verified against the cited paper's full text; the real sentence is "The first phase
   (Phase I), from November 2011 to May 2013, accumulated an exposure of 21.6 kg·yr...".
   **Fixed**, and confidence raised approximate → verified since the real text now
   supports it.
3. **NEXT-100** (3 field instances across `experiments/next.json` and
   `detectors/next-100.json`): quote read "NEXT-100: commissioned May 2024, operational at
   LSC since May 2024, producing first physics results as of December 2025" — this
   colon-led, three-clause sentence appears nowhere on the cited homepage; it is a
   constructed summary. The underlying facts are true (found a NEXT news post dated
   2025-05-27 confirming "operational... since May 2024", and a separate post dated
   2025-12-17 titled "First physics results with the NEXT-100 detector" corroborating the
   December claim) but were never fetched together as one sentence. **Fixed**: re-sourced
   to the 2025-05-27 news post with its actual sentence; the December claim is reported in
   a note rather than re-added as an unverified quote.
4. **CUPID** detector `specs.isotope.quote`: read "Target Isotope: Molybdenum-100
   (100Mo)" — not present on the official page, which instead says "the candidate isotope
   100Mo has a Q-value of 3034 keV (compared to 2527 keV of 130Te)". **Fixed.**
5. **Majorana Demonstrator** installation-start quote (4 occurrences: experiment,
   collaboration, detector ×2, and the source record's own `excerpt`): read "The
   collaboration began installing the detector at the 4850 Level Davis Campus underground
   in March 2012." The SURF page's actual sentence names the collaboration and the
   detector: "The MAJORANA Collaboration began installing the "MAJORANA Demonstrator
   (MJD)" detector at the 4850 Level Davis Campus underground in March 2012." Facts
   unchanged; wording was paraphrased. **Fixed** in all four files.

These five were caught by directly re-fetching every cited source and diffing its actual
text against the record's `quote` field — the same failure mode the brief warned "sibling
verifiers found ... in quotes." All five involved records whose underlying numeric/factual
content was correct; only the `quote` field itself misrepresented what the source said.

### P1 — sourcing/ontology-conformance gaps

6. **detector:katrin** `technology_class`/`technology_classes` was the legacy generic
   `"spectrometer"`. Ontology amendment A24 (2026-09-17) added `magnetic_spectrometer`
   specifically so "KATRIN's MAC-E filter spectrometer is `magnetic_spectrometer`" (per
   this task's own framing of A24, confirmed by reading A24's text, which names KATRIN's
   class of device as the reason the new value was added). **Fixed.**
7. **LEGEND-200** detector placement claimed `site_id: site:lngs-hall-a` citing only the
   LEGEND official site, whose fetched text says "Located at INFN Gran Sasso National
   Laboratory (LNGS)" — general LNGS, not Hall A specifically. Found and fetched a proper
   primary/official-facility source (LBL Nuclear Science Division, "LEGEND-200 Enters Data
   Production Phase", 2023-07-01) that states Hall A verbatim: "reuses the GERDA cryostat
   in Hall A of ... LNGS". **Fixed**: added `src:0vbb-verify-legend-200-hall-a-lbl` and
   re-pointed the placement's quote/locator to it.
8. **CUORE** and **CUPID** detector placements have the identical pattern (claim Hall A,
   cited source only confirms general LNGS). I independently corroborated via WebSearch
   that CUORE is genuinely in Hall A (multiple secondary sources agree), but could not find
   a directly fetchable primary/official source stating "Hall A" verbatim for CUORE or
   CUPID within a reasonable search budget (tried the CUORE cryostat paper, the Faraday
   room paper, the original CUORE TDR, an LNGS hall-by-hall search, and a Snowmass
   underground-facilities report — none gave the phrase in fetchable form; one official
   LNGS mirror had an expired TLS certificate). Rather than leave the placements
   overstated, **downgraded confidence**: CUORE's placement confidence/status from
   `verified` to `approximate`; CUPID's stays `uncertain`. Both now carry a note explaining
   the citation gap for a future pass. Not fabricated — flagged honestly instead.
9. **EXO-200**: `site:wipp-surface-campus.depth_mwe` was `null` with a note saying the
   agent could not verify the ~1624 m.w.e. secondary-summary figure. The task brief said
   EXO-200 papers give 1585 m.w.e.; I directly fetched the primary detector design paper
   (arXiv:1202.2192 via ar5iv full text) and confirmed "EXO-200 is located at a depth of
   1585 m water equivalent ... in [WIPP]" verbatim. **Fixed**: filled `depth_mwe` with 1585
   m.w.e., sourced to a new `src:0vbb-verify-exo-200-detector-design-arxiv-1202-2192`
   record; also used the same paper to confirm `detector:exo-200.specs.target_mass` (110 kg
   active liquid-xenon mass) verbatim and raised its confidence `uncertain` → `verified`.
   Left a note that a later EXO-200 paper instead reports ~1624 (+22/-21) m.w.e. (a
   subsequent re-estimate) — this discrepancy is not reconciled, reported honestly.

### P2 — documented gaps, no fabrication (reviewed, judged correct as-is)

10. GERDA has an unrecorded 30-month gap (2013-06 to 2015-11) between the sourced Phase I
    and Phase II intervals — the known Phase I→II upgrade/shutdown period, for which no
    source in this or the prior session gives a status. The validator already flags this
    (`A12` warning); added it explicitly to the record's notes and to
    `coverage.json`'s `missing_fields` rather than inventing an interval.
11. Several records (GERDA/LEGEND/MJD/EXO-200/nEXO/KamLAND-Zen/NEXT/CUORE/CUPID/KATRIN/
    Project 8 collaborations, and a few experiment intervals) use a sourced lower-bound
    year (the earliest dated fact available) as `start`, because a `null`/`null` interval
    would derive to "no presence" for entities that clearly exist. Checked every instance:
    each carries an explanatory `note` stating it is a lower bound, not the true formation
    date, and an appropriate `confidence` (`approximate`/`uncertain`). This is honest given
    the schema — the ontology's `Date.earliest`/`latest` qualifiers (A4) would be a cleaner
    mechanism, but nothing here reads as a fabricated real date once the note is read.
    Flagged as a style improvement for a future pass, not a defect.
12. CUORE's own operating history (commissioning 2017 → steady/active 2019, from the only
    source in this domain that gives these dates, an LBL press release) was checked against
    every other CUORE source fetched in this session (the 2024 arXiv abstract gives no
    dates) and found to be the only available sourced answer; left unchanged. The record
    already distinguishes 2017 (commissioning) from 2019 (steady data-taking) correctly
    rather than collapsing to "active since ~2019" as a real status boundary.

## Fixes applied (all within scope: `experiments/`, `detectors/`, `collaborations/`,
`facilities/wipp.json`, `facilities/kit-karlsruhe.json`, `sites/wipp-surface-campus.json`,
`sites/kit-campus-north.json`, `results/katrin-...json`, `coverage/neutrino-mass-0vbb.json`,
and new `src:0vbb-verify-*` records)

- `data/atlas/experiments/gerda.json` — 2 quote fixes (#1, #2), added gap note (#10).
- `data/atlas/experiments/next.json` — quote fix + re-source (#3).
- `data/atlas/experiments/majorana-demonstrator.json` — quote fix (#5) + note.
- `data/atlas/experiments/exo-200.json` — sources list updated (#9).
- `data/atlas/detectors/next-100.json` — 2 quote fixes + re-source (#3).
- `data/atlas/detectors/cupid.json` — quote fix (#4); placement note (#8).
- `data/atlas/detectors/katrin.json` — technology_class fix (#6).
- `data/atlas/detectors/legend-200.json` — re-sourced Hall A placement (#7).
- `data/atlas/detectors/cuore.json` — confidence downgrade + note (#8).
- `data/atlas/detectors/exo-200.json` — target_mass fix (#9).
- `data/atlas/detectors/majorana-demonstrator.json` — quote fix ×2 (#5).
- `data/atlas/collaborations/majorana-demonstrator.json` — quote fix (#5).
- `data/atlas/sites/wipp-surface-campus.json` — depth_mwe filled (#9).
- `data/atlas/sources/majorana-demonstrator-surf-news.json` — excerpt corrected (#5).
- `data/atlas/coverage/neutrino-mass-0vbb.json` — missing_fields/notes updated for
  gerda, exo-200, cuore, cupid, katrin, legend to reflect the above.
- New source records: `src:0vbb-verify-legend-200-hall-a-lbl`,
  `src:0vbb-verify-exo-200-detector-design-arxiv-1202-2192`,
  `src:0vbb-verify-next-100-commissioned-news`.

## Verified correct (no defect found)

- All seven headline half-life limits + exposures — GERDA (>1.8e26 yr, 127.2 kg·yr),
  MJD (>8.3e25 yr, 64.5 kg·yr), EXO-200 (>3.5e25 yr, 234.1 kg·yr), KamLAND-Zen (>3.8e26 yr,
  2.1 t·yr), CUORE (>3.5e25 yr, 90% **C.I.** — verbatim, correctly not "C.L."), LEGEND-200
  (>0.5e26 yr) and the combined GERDA+MJD+LEGEND-200 figure (>1.9e26 yr, both 90% CL), and
  KATRIN (mν < 0.45 eV, 90% CL) — all match the actual fetched abstracts exactly, unit and
  confidence-level wording included.
- `results/katrin-neutrino-mass-upper-limit-2025.json`: `result_type: "limit"` (not
  inflated), `claim.quote` verbatim-correct, `date_kind: "publication"` correctly set.
- `detector:kamland` (owned by reactor-solar-neutrino) already lists `experiment:kamland-
  zen` in its `experiment_ids` with a proper sourced row; `site:kamioka-kamland` exists.
  Both previously-dangling references now resolve. Reported, not edited (out of scope).
- Majorana Demonstrator's site note honestly discloses that it shares LZ's coordinate
  point at `site:surf-davis-campus-lz` rather than presenting a fabricated distinct one.
- Every experiment in this domain has a `null` `external.inspire_experiment` with an
  explanatory note, satisfying A20's tier-A/B requirement.
- Technology classes: CUORE and CUPID both correctly use `cryogenic_bolometer` (A24).
- `data/atlas/sources/kamland-zen-arxiv-1211-first-phase.json`, initially suspected of
  being an orphan source, is in fact cited by `detector:kamland` (a different domain's
  file) — not a defect.

## Unverifiable in this pass

- CUPID's DOE Critical-Decision stage / construction status beyond CD-0 (~2019); no
  fetchable 2025 primary source found. "proposed" status left unchanged (conservative and
  still defensible).
- NEXT-White's precise 2016/2021 run-boundary years (already flagged `uncertain` by the
  original author; unchanged).
- The CUORE/CUPID "Hall A" source gap (finding #8) is only half-resolved: LEGEND-200 now
  has a verbatim source; CUORE and CUPID do not, and were downgraded/flagged instead of
  fixed outright.
- The EXO-200 depth_mwe discrepancy (1585 m.w.e., construction paper, now recorded, vs.
  ~1624 m.w.e., a later paper) is not reconciled — both are genuine values from different
  EXO-200-era publications; flagged in a note rather than picking one silently.

## Validator

`.venv/bin/python -m hepgraph.atlas.validate` was run repeatedly. The total error count
fluctuated between runs (0-17) due to what is almost certainly concurrent editing by
another workstream elsewhere in this shared worktree — every error observed across six
separate runs was in `results/belle-ii-vcb-measurement-2025.json` or
`results/nova-t2k-joint-oscillation-analysis-2025.json`, both entirely outside this
domain (belle-ii, nova/t2k). **Zero errors were ever attributable to any
neutrino-mass-0vbb file** (grepped every run's error block for gerda/legend/majorana/
exo-200/nexo/kamland-zen/next/cuore/cupid/katrin/project-8/wipp/kit-karlsruhe file paths;
no match in any run). Warnings attributable to this domain (A12 no-accelerator warnings
on non-accelerator experiments, A23 approximate-coordinate warnings on campus-grade
sites, A1 derived-`rank`-field warnings present on every `src:` record in the repository)
are all expected/systemic, not defects.

## Verdict

The domain's core physics claims (half-life limits, exposures, confidence levels, the
KATRIN mass limit) were sound before this pass and remain sound. The real problem this
verification found was **not** wrong numbers but **fabricated verbatim quotes** on five
separate claims across four experiments (GERDA ×2, NEXT-100, CUPID, Majorana
Demonstrator) — text presented in a `quote` field as if lifted character-for-character
from a cited source when it was in fact a paraphrase or a constructed multi-fact
sentence. All five are fixed, in every file where they occurred, with the real verbatim
text and (where the original citation didn't support the more specific claim) a better
source. Two further sourcing gaps (LEGEND-200 Hall A citation; EXO-200 depth_mwe) were
fixed with newly fetched primary sources; two similar gaps (CUORE/CUPID Hall A) could not
be fully closed and were downgraded/flagged instead of left overstated or invented. One
ontology-conformance fix (KATRIN's `magnetic_spectrometer` class per A24) was applied.
No P0 finding involved an incorrect physics number — the numbers were consistently
correct; the citations backing some of them were not what they claimed to be. 0 validator
errors attributable to this domain across six runs.
