# Independent verification: reactor-solar-neutrino (wave 3)

Verifier did not research these records originally and treated
`docs/atlas-worklog/reactor-solar-neutrino.md` as untrusted narrative, not
evidence. All findings below come from re-fetching primary sources directly
(arXiv abstracts/full text, INSPIRE-HEP API, IOP/Nature/DOI-resolved pages,
Wikipedia) in this session, at ≤1 request/10s to inspirehep.net.

## Records checked

Deep, source-by-source re-verification (titles, dates, quotes, specs,
intervals, statuses):

- **JUNO** (flagship): experiment, detector, facility, site, both documents
  (CDR, Physics-and-Detector), both 2026 results (Nature 654 oscillation
  paper, Chin. Phys. C 50 initial-performance paper).
- **Daya Bay**: experiment, facility, 2012 discovery result, key baselines.
- **RENO**: experiment, detector, facility, 2012 observation result, key
  baselines.
- **Double Chooz**: 2012 evidence result (title/quote/sigma), key specs.
- **KamLAND**: 2002 first-results title (exact "Anti-Neutrino" spelling).
- **SNO**: 2001 CC-evidence and 2002 NC-evidence results (titles/quotes).
- **Borexino**: 2014 pp and 2020 CNO results (titles/DOIs/quotes), overburden.
- **SAGE**: 1999 capture-rate result (title/SNU values).
- **Homestake**: 1998 flux-measurement result (title casing verified against
  the IOPscience-typeset page, not just INSPIRE's normalized metadata; SNU
  value).
- **GALLEX/GNO, SNO+**: status/interval dates spot-checked against the
  brief's expected values (not independently re-fetched beyond what was
  already on file; see Unverifiable below).

Read first, as instructed: `docs/HEP_ATLAS_ONTOLOGY.md` amendments A1-A24,
`docs/atlas-worklog/RESEARCH_AGENT_RULES.md`,
`data/atlas/experiments/super-kamiokande.json` as the reviewed convention.

## Values re-fetched this session

Distinct primary/journal URLs actually fetched and read (not from memory):
**17** — arXiv abstract+HTML pages for 1508.07166 (JUNO CDR), 2104.02565
(JUNO Physics and Detector), 2511.14590 full text (JUNO initial performance,
PDF→text extracted), 1203.1669 (Daya Bay 2012), 2211.14988 full text (Daya
Bay final PRL 2023, PDF→text extracted), 1207.6632 (Double Chooz 2012),
hep-ex/0212021 (KamLAND 2002), nucl-ex/0106015 (SNO CC 2001), 2412.18711
(RENO final 2024), 1204.0626 (RENO 2012), astro-ph/9907113 (SAGE 1999),
2006.15115 (Borexino CNO 2020); Nature article page (JUNO oscillation,
s41586-026-10538-z); IOP DOI-resolved pages for Chin. Phys. C 50, 043001 and
ApJ 496, 505 (Homestake); IHEP news pages (JUNO detector-completion 2024,
first-results 2025); Wikipedia (Daya Bay, coordinates cross-check); 4
INSPIRE-HEP API queries (JUNO CPC record, Daya Bay 2012 record, RENO record
search, Homestake record).

## Findings by severity

### P0 (factual errors, flagship or status-changing)

1. **JUNO as-built PMT count was wrong.** `detector:juno.json` recorded
   `pmt_count: 20000`, sourced to an IHEP press release that rounds the
   design/production figure. The collaboration's own peer-reviewed
   "Initial performance results of the JUNO detector" (arXiv:2511.14590 =
   Chin. Phys. C 50, 043001 (2026)) states the actual installed count is
   **17,596** 20-inch PMTs (4,939 Hamamatsu dynode-PMTs + 12,657 NNVT
   MCP-PMTs), and 25,587 (not 25,000/25,600) 3-inch PMTs. Fixed, with the
   old value's provenance explained in a `note`.
2. **RENO's operating status was wrong.** `experiment:reno.json`,
   `detector:reno.json` and `facility:yonggwang-hanbit-reactor-site.json`
   all had `status: "active"` with an open-ended interval, because the
   original pass had fetched only the 2012 discovery paper (a 229-day
   analysis window) and explicitly left the question of continuation vs.
   shutdown unresolved. RENO's own 2024 final-dataset paper
   (arXiv:2412.18711) states plainly: "As of March 2023, the data
   acquisition was completed after a total of 3800 live days." Fixed:
   status changed to `completed` on all three records, with a day-precision
   terminal interval.
3. **Daya Bay's completion date and AD-configuration history were
   under-sourced.** The prior interval history used only Wikipedia
   (rank 12, year precision, `confidence: approximate`) for the 2020
   completion. The collaboration's own final oscillation paper (PRL 130,
   161802 (2023) = arXiv:2211.14988) gives an exact, three-configuration
   history: six-AD 2011-12-24 to 2012-07-28; eight-AD 2012-10-19 to
   2016-12-20; seven-AD 2017-01-26 to 2020-12-12 (one AD re-purposed for
   JUNO-related R&D). This also confirms the brief's stated completion date
   (2020-12-12) is correct — but it was not actually in the data before this
   pass. Fixed on both `experiment:daya-bay.json` and
   `facility:daya-bay-reactor-neutrino-lab.json`.

### P1 (paraphrased quotes presented as verbatim; missing sourced fields)

4. **Two JUNO claim-level quotes were paraphrased, not verbatim**, violating
   A15 ("`quote`: verbatim ≤300 chars seen in the fetched content"):
   - `experiment:juno.json` key_specs "Baseline to reactor cores" quoted
     "The underground facility, located 52.5 km from reactor cores" — the
     actual Nature abstract says "is a 20-ktonne liquid-scintillator
     detector located **52.5 km from multiple reactor cores**" (dropped
     "multiple", rewrote the lead clause). Fixed.
   - `experiment:juno.json` unique_capabilities and `detector:juno.json`
     specs.energy_resolution both quoted "an **anticipated** energy
     resolution of 3.02%/√E (MeV)" — the 2021 paper's abstract says
     "**effective** energy resolution", not "anticipated". Fixed in both
     places.
5. **JUNO civil-construction start (2015-01) was an undocumented gap.** Both
   `experiment:juno.json` and `facility:juno-jiangmen.json` explicitly noted
   "No source... states an explicit approval date between the 2015 CDR and
   the 2021 start of detector installation." The Initial-performance paper
   states directly: "The civil construction of the JUNO underground lab
   started in January 2015." Added as a new sourced interval on
   experiment/facility/detector; stale notes removed.
6. **JUNO `depth_mwe` was `null`** despite being flagged as a plausible gap.
   The same paper states the overburden is "1800 m.w.e." — consistent with
   the existing 700 m granite-rock figure (granite density ≈2.6 g/cm³ →
   ≈1800 m.w.e.). Added to `site:juno-jiangmen-underground-lab.json`.
7. **JUNO result `result:juno-initial-performance-2026.json` had no DOI**
   and its `claim`/`key_value_text`/`why_it_matters` quotes were sourced
   only to a URL (`cpc.ihep.ac.cn/news/...`) that renders as an empty
   JavaScript shell under a plain fetch — meaning the quotes attributed to
   it could not actually have been read from that page. Added DOI
   (10.1088/1674-1137/ae3dc1, confirmed via INSPIRE control_number 3084402)
   and re-sourced every quote to the arXiv preprint of the identical
   peer-reviewed paper, whose full text was fetched and checked directly.
8. **`document:juno-physics-and-detector.json` summary misattributed a
   statistic**: "20,000 20-inch PMTs (28.9% average photon detection
   efficiency)" implied 28.9% applied to all 20,000 tubes. The abstract
   states 28.9% for the 15,000 MCP-PMTs specifically and 28.1% for the
   other 5,000 dynode-PMTs. Fixed.

### P2 (judgment calls, not changed)

- `result:juno-initial-performance-2026.json` uses `result_type:
  "technology_milestone"`, not `"measurement"` as the task brief assumed.
  Both are valid enum values (§3.12); a detector-performance report (light
  yield, energy resolution, attenuation length) fits `technology_milestone`
  at least as well as `measurement`. Left unchanged as a defensible choice,
  not an error — flagging here rather than silently following the brief's
  unverified assumption.
- The brief's example title casing "Observation of **Electron-Antineutrino
  Disappearance** at Daya Bay" (title case) does not match the actual
  published title, confirmed independently via arXiv and INSPIRE:
  "Observation of **electron-antineutrino disappearance** at Daya Bay"
  (sentence case). The data file already had this right; no change made —
  noted here because the brief itself was slightly wrong.

## Not found / could not fix

- No P0/P1 issues found in: KamLAND 2002 title spelling ("Anti-Neutrino",
  verified exact), Double Chooz 2012 evidence result (title, "evidence"
  wording, and 2.9σ/99.8% CL all verbatim from the abstract), SNO 2001/2002
  results (both titles verbatim, including the full reaction-formula title
  of the 2001 paper), Borexino pp/CNO results (titles, DOIs, and Nature
  volume/pages all verbatim), SAGE 1999 (title and 67.2/129 SNU verbatim),
  Homestake 1998 (title casing matches the IOPscience-typeset page exactly,
  even though INSPIRE's own metadata normalizes it to sentence case; SNU
  value verbatim).
- RENO baselines (294 m / 1383 m) and Double Chooz far-detector baseline
  (1050 m) are already recorded as key_specs with verbatim quotes, per A21
  (reactor-to-hall distances are not beamlines, so the great-circle check
  does not apply — correctly not invoked here).
- GALLEX/GNO (1991-1997, 1998-2003), SNO (completed 2006), SNO+ (scintillator
  phase 2022, tellurium planned), Homestake (1970-1994) intervals all match
  the brief's expected shape; not independently re-fetched beyond what was
  already on file (time-boxed) — see Unverifiable below.

## Unverifiable this session (left as pre-existing `missing_fields`, not
guessed)

- SAGE's current operating status (Wikipedia's own wording is internally
  contradictory; official Baksan/INR page still unreachable).
- Hall-specific coordinates for Daya Bay, RENO, Double Chooz (official sites
  still unreachable; shared campus/approximate points remain, correctly
  flagged `coordinate-kind-approximate` per A23).
- GALLEX/GNO capture-rate figures and membership counts (Wikipedia-only,
  already flagged uncertain/approximate in the original pass — not
  independently re-verified this session due to time).
- JUNO underground-hall coordinates at `detector`/`underground_lab`
  precision (still not found in any rank≤7 source; correctly left
  `kind: campus`/`confidence: approximate` per A17/A23).

## Fixes applied (files touched)

New sources (prefixed `src:reactor-solar-verify-`):
`data/atlas/sources/reactor-solar-verify-juno-cpc-2026-arxiv.json`,
`data/atlas/sources/reactor-solar-verify-daya-bay-final-prl-2023.json`,
`data/atlas/sources/reactor-solar-verify-reno-final-2024.json`.

Edited: `data/atlas/detectors/juno.json`, `data/atlas/experiments/juno.json`,
`data/atlas/facilities/juno-jiangmen.json`,
`data/atlas/sites/juno-jiangmen-underground-lab.json`,
`data/atlas/results/juno-initial-performance-2026.json`,
`data/atlas/sources/juno-cpc-initial-performance-2026.json`,
`data/atlas/documents/juno-physics-and-detector.json`,
`data/atlas/experiments/daya-bay.json`,
`data/atlas/facilities/daya-bay-reactor-neutrino-lab.json`,
`data/atlas/experiments/reno.json`, `data/atlas/detectors/reno.json`,
`data/atlas/facilities/yonggwang-hanbit-reactor-site.json`,
`data/atlas/coverage/reactor-solar-neutrino.json`.

Every edit uses canonical formatting
(`json.dumps(sort_keys=True, indent=2, ensure_ascii=False)` + trailing
newline) and `verified_at: "2026-09-18"`.

## Validator status

`.venv/bin/python -m hepgraph.atlas.validate`: **0 errors** repo-wide
(checked before and after this pass; introduced two transient errors mid-pass
— a duplicate-DOI across two Chin. Phys. C sources, and 3 over-length
quotes — both fixed before finishing). 1591 warnings remain, all pre-existing
repo-wide patterns (derived-field, coordinate-kind-approximate,
sourced-list-shape, etc.) or expected per A23; none attributable to this
verification pass are new errors.
`python -c "import json,glob;[json.load(open(f)) for f in glob.glob('data/atlas/**/*.json',recursive=True)]"`:
all files parse.

## Verdict for JUNO (flagship)

**Not zero-contradiction at the start of this pass.** Found and fixed one P0
factual error (wrong as-built PMT count, a ~12% discrepancy from the correct
figure) and two P1 paraphrased-as-verbatim quotes, plus closed a real
"missing interval" gap (civil construction start) that the original pass had
explicitly flagged as unresolved but that a source it had already listed
(the same paper) actually answers. After the fixes in this pass, I found
**no remaining factual contradictions** in the JUNO records against the
sources fetched and re-checked this session (CDR, Physics-and-Detector
paper, both 2026 results, IHEP news pages) — the bar this workstream was
held to.
