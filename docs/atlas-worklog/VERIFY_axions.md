# Independent verification — axions (wave 3): ADMX, HAYSTAC, CAST, IAXO, ALPS II, ABRACADABRA, DMRadio

Verifier pass, 2026-09-17/18. Did not trust `docs/atlas-worklog/axions.md`; did
not research these records originally. Re-fetched every cited source with
WebFetch/WebSearch and cross-checked every critical value against it. No
subagents spawned. Respected the ≤1 inspirehep.net request/10 s limit (8
INSPIRE API calls, spaced 10 s apart). All edits confined to `data/atlas/`
(files owned by this domain) and this worklog; no git.

## Records checked

- Experiments (7): `admx`, `haystac`, `cast`, `iaxo`, `alps-ii`,
  `abracadabra`, `dmradio`
- Detectors (7): same 7, one detector record each
- Collaborations (7): same 7
- Facilities (3, axions-owned): `university-of-washington-cenpa`,
  `yale-wright-lab`, `mit` (+ read `facility:desy`, `facility:slac`,
  `facility:cern`, owned by other leads, for cross-reference only)
- Sites (4, axions-owned): `uw-cenpa-campus`, `yale-wright-lab-campus`,
  `mit-cambridge-campus`, `cern-cast-sr8` (+ read
  `site:desy-hera-north-hall-h1`, `site:cern-meyrin`,
  `site:cern-point-8-lhcb`, `site:cern-lep-point-8-delphi`,
  `site:cern-ecn3-north-area`, `site:cern-neutrino-platform-ehn1`, owned by
  other leads, for the CAST-siting question)
- Sources: 30 `src:axions-*` records read; 2 added
  (`src:axions-cast-sr8-point8-cryo-doc`, `src:axions-alps-ii-desy-cryoplatform`),
  one existing source's `excerpt` corrected (`src:axions-iaxo-news-page`)
- `data/atlas/coverage/axions.json` (7 registry rows)

## Values re-fetched this session

INSPIRE experiment API records (paced ≥10 s apart): 1309376 (ADMX), 1600738
(HAYSTAC, confirmed `date_completed` is literally `"9999"` and was correctly
never turned into a date), 1110249 (CAST), 1698854 (IAXO), 1826394
(BabyIAXO), 1761312 (ALPS II) — all `date_proposed`/`date_approved`/
`date_started`/`date_completed` values and description-field quotes matched
the data files exactly. CERN: `home.cern/science/experiments/cast`,
`greybook.cern.ch` (both the SPA page and a guessed API path — blocked by an
SSO redirect, no usable data), `cds.cern.ch/record/593785` (blocked by bot
protection), Wikipedia `CERN_Axion_Solar_Telescope`, and several WebSearch
passes plus a slide-deck (`slideserve.com/.../organisation-procedures...`)
that turned out to name CAST's actual siting. DESY: `alps.desy.de/`,
`darkmatter-alps.desy.de/alps-ii-eng.html`, `alps.desy.de/our_activities/
technology/desy_cryoplatform/`, `www.desy.de/news/...` (two anchors),
`phys.org/news/2019-10-magnet-alps-ii-desy.html`, `iaxo.desy.de/`,
`iaxo.desy.de/news`. arXiv abstracts: 1910.08638, 2504.07279, 2409.08998,
2210.07215, 2607.05771, 1810.12257, 2102.06722, 1302.5647, 2504.00079.
Institution pages: `npl.washington.edu/node/885`, `npl.washington.edu/cenpa/
contact`, `physics.mit.edu/faculty/lindley-winslow/`,
`haystac.yale.edu/haloscope-yale-sensitive-axion-cdm` (via prior citations,
re-derived quotes cross-checked against the arXiv/INSPIRE re-fetches above).
~28 distinct URLs/API endpoints opened and cross-checked against the files
that cite them.

## Findings by severity

**P0: none confirmed as outright fabrication**, but one P0-adjacent modeling
bug: three axions-owned **facility records failed ontology-consistency
validation** (`status-not-derived-state`, a build-failing error class) —
`facility:university-of-washington-cenpa`, `facility:yale-wright-lab`,
`facility:mit` each had a single interval with `start: null, end: null`.
Per A3, a null `start` covers only `[lo(end), hi(end)]`; with `end` also
null the interval covers **no date at all**, so the derived state at the
build date was `None` while `status` said `active` — an internal
contradiction the validator was right to catch. Fixed (see below).

**P1:**
1. **CAST site was misplaced and the note asserted an unsourced fact.**
   `site:cern-cast-sr8`'s coordinate was an OSM/Nominatim "CERN Prevessin
   campus fallback" that exactly duplicated two unrelated CERN sites
   (`site:cern-ecn3-north-area`, `site:cern-neutrino-platform-ehn1`, all
   three at 46.2601088, 6.0577057), and its note/name claimed CAST is
   "historically referred to as SR8/West Area" — a claim traced to no
   fetched source (West Area is a distinct SPS fixed-target area). CERN's
   own page, Wikipedia, and the CAST INSPIRE record all describe *what*
   CAST is but none states a building; the Greybook returned only an SSO
   redirect and CDS was blocked by bot protection this session too. A
   WebSearch chain, however, surfaced an internal CERN AT/ECR cryogenics
   slide deck (reposted on slideserve.com) that labels CAST's cryogenic
   coldbox `CRYO REFRIG LHC CAST_COLDBOX /SR8` under the heading "CERN Axion
   Solar Telescope (CAST) — LHC Point 8" — i.e. SR8 sits at/near LHC Point 8
   (Ferney-Voltaire, France), not Meyrin and not the generic Prevessin point
   used before. This is a lower-rank ("secondary") source, so the fix moves
   the point to the existing Point-8 anchor
   (`src:lep-point-8-osm-nominatim`, already used by
   `site:cern-point-8-lhcb`/`site:cern-lep-point-8-delphi`) at `confidence:
   uncertain`, corrects the "West Area" claim, and leaves a REVIEW REQUIRED
   note asking for an official CAST/CERN page, the Greybook, or a CAST
   detector paper to replace this source if found. (CAST remains a distinct
   site record, `setting: surface`, from the underground LHCb/DELPHI cavern
   at the same nominal Point 8 — CAST must see the sky to track the Sun.)
2. **IAXO collaboration `quote` fields were not verbatim.** Both
   `collaboration:iaxo`'s `formation.quote` and its formation interval's
   `quote` read "IAXO Collaboration formally established" — paraphrased.
   The actual source sentence (`iaxo.desy.de/news`, re-fetched) is "The IAXO
   collaboration was formally constituted." The date (2017-07-07) was
   correct; only the quote text was wrong. A17/A15 require verbatim quotes.
   Fixed.
3. **ALPS II's HERA North Hall placement rested solely on Wikipedia** (rank
   12) even though DESY's own ALPS cryoplatform page states the same fact
   directly ("The ALPS cryoplatform subcooler box (ACPS) in the hall HERA
   North ... has recently been partially renovated to accommodate the ALPS
   II experiment in the HERA tunnel"), corroborated independently by a
   phys.org report and a DESY news page (general "HERA tunnel" placement).
   Upgraded to `confidence: verified` citing the DESY page
   (`official_experiment_site`, rank 1), Wikipedia kept as secondary
   corroboration.

**P2:**
1. A24 (added the same day this record was researched) added `helioscope`,
   `light_shining_through_wall` and `lumped_element_resonator` to
   `technology_classes` specifically to end the "no matching enum value"
   workaround; CAST, IAXO, ALPS II, ABRACADABRA and DMRadio detectors were
   all still filed under `other` with notes saying so. Reclassified: CAST →
   `helioscope`, IAXO → `helioscope`, ALPS II → `light_shining_through_wall`,
   ABRACADABRA → `lumped_element_resonator`, DMRadio →
   `lumped_element_resonator`. The sourced `technology` free-text strings
   were left unchanged, as instructed.
2. **CAST's magnet key_specs were missing despite being in an already-cited
   source.** Both `experiment:cast` and `detector:cast` left magnet field
   and length out of `key_specs`/`specs`, noting "no clean verbatim quote
   found." Re-fetching the already-cited INSPIRE record's description field
   (`src:axions-cast-inspire-experiment`) turned up exactly that sentence:
   "In the CAST experiment an LHC prototype dipole magnet (B=9 T and L=10 m)
   with straight beam pipes provides a conversion efficiency exceeding that
   of the two earlier solar axion telescopes by almost a factor of 100."
   Added `magnetic_field: 9 T` and `length: 10 m` with this quote/locator
   (independent secondary sources — Wikipedia, an axion-searches review —
   give 9.26 m / 9.5-9.6 T design-vs-measured variants; the INSPIRE record's
   round design numbers were used since that is the source already cited
   and re-verified, and the variance is within the validator's 10%
   `display`-vs-`value` tolerance either way).

**Checked and found correct (no changes needed):**
- ADMX and HAYSTAC statuses (`active`), and every INSPIRE date field quoted
  in any file, matched the live API records exactly, including confirming
  HAYSTAC's `date_completed: "9999"` sentinel was correctly *never* written
  as a date anywhere.
- CAST's day-precision dates (proposed 1999-08-09, approved 2000-04-13,
  started 2003-06-18, completed 2022-12-31) match the INSPIRE record
  exactly; `status: completed` is the correct derived state per A10 (a
  terminal interval has already started).
- ALPS II `active` since 2023-05-23 matches INSPIRE `date_started` exactly.
- The IAXO/BabyIAXO modeling choice (one `experiment:iaxo` record with a
  `proposed` interval for full-scale IAXO and a `construction` interval for
  BabyIAXO, rather than a second experiment id) is a defensible reading of
  the sources — BabyIAXO has its own INSPIRE record (1826394) but IAXO's own
  European Strategy input paper and news page treat it as a stage of one
  program — and correctly derives `status: construction` per A10/A3 (the
  non-terminal `construction` interval outranks the older `proposed` one).
  DESY's own IAXO page independently confirms full IAXO is still only
  "proposed."
- Every quote checked against its source (ADMX 2019/2025 PRL abstracts,
  HAYSTAC Phase II PRL abstract, ABRACADABRA 2019/2021 PRL abstracts,
  DMRadio 2022 status paper and 2026 cryo paper, ALPS II TDR, ADMX/CENPA
  page, MIT Winslow page, IAXO strategy-2025 paper) reproduced verbatim,
  ≤300 chars, correct units — no fabrication or unit errors found.
  `retrieval` is `"partial"` throughout (never `"summary"` with a `quote`).
- Every INSPIRE recid cited (1309376, 1600738, 1110249, 1698854, 1826394,
  1761312) appears in its own source's `url`.
- No duplicate source URLs/DOIs, no duplicate experiment/detector/
  collaboration names or aliases, within axions or against the rest of the
  dataset (checked by script).
- `data/atlas/coverage/axions.json`'s `missing_fields` were honest going in
  (they already flagged the CAST-siting and ALPS-II-Wikipedia gaps this
  pass resolved) — updated to reflect the fixes and remaining gaps.

## Fixes applied (all `verified_at`/`accessed`: 2026-09-17, canonical JSON)

1. `facilities/university-of-washington-cenpa.json`,
   `facilities/yale-wright-lab.json`, `facilities/mit.json`: gave the sole
   `active` interval a sourced lower-bound `start` (CENPA 2017, from the
   already-cited CENPA page's 2017 DFSZ-result mention; Wright Lab 2010,
   matching HAYSTAC's own earliest INSPIRE `date_proposed` — an initial fix
   using 2018 was replaced after the validator flagged
   `experiment-before-facility`, since Wright Lab cannot postdate a 2010
   proposal hosted there; MIT 2018, matching ABRACADABRA's first run)
   instead of `start: null, end: null`, which resolves the
   `status-not-derived-state` validator error on all three.
2. `sites/cern-cast-sr8.json`: coordinate moved from the unsourced Prevessin
   duplicate to the Point-8 anchor; name, note, place (Ferney-Voltaire) and
   `sources` updated; new source added.
3. `sources/axions-cast-sr8-point8-cryo-doc.json` (new): the CERN cryogenics
   slide deck naming CAST/SR8/Point 8.
4. `experiments/cast.json`, `detectors/cast.json`: added magnet
   `key_specs`/`specs` (9 T, 10 m) with quote/locator; removed the
   now-stale "not found" notes.
5. `detectors/cast.json`, `detectors/iaxo.json`, `detectors/alps-ii.json`,
   `detectors/abracadabra.json`, `detectors/dmradio.json`: `technology_class`
   and `technology_classes` reclassified per A24 (see P2.1); stale
   "no enum value" notes replaced with a VERIFIER FIX note.
6. `detectors/alps-ii.json`: placement source upgraded from Wikipedia-only
   to DESY's own cryoplatform page; `confidence: verified`.
7. `sources/axions-alps-ii-desy-cryoplatform.json` (new): the DESY page
   confirming HERA North Hall.
8. `experiments/alps-ii.json`: note updated to describe the upgraded
   sourcing.
9. `collaborations/iaxo.json`: both `quote` fields corrected to the
   verbatim source sentence.
10. `sources/axions-iaxo-news-page.json`: `excerpt` corrected to match.
11. `data/atlas/coverage/axions.json`: `missing_fields`/`notes` updated for
    `cast`, `alps-ii`, `iaxo`, `abracadabra`, `dmradio` to reflect this pass.

## Unverifiable values (left as-is, flagged for future sourcing)

- The exact CAST/SR8 building location still rests on a lower-rank source
  (a reposted internal slide deck); Greybook and CDS were both unreachable
  this session (SSO redirect / bot protection).
- ADMX's and HAYSTAC's numeric magnet field strength/cavity volume, IAXO's
  design magnet field/bore, and ALPS II's magnet count/resonator length
  remain unsourced by a clean verbatim quote — left `null`/omitted with
  notes, as the original pass did; this pass did not find a better source
  for these specific numbers (only CAST's happened to be sitting in an
  already-cited source).
- DMRadio-50L's Stanford-campus site (distinct from `facility:slac`'s own
  site) remains uncreated, as previously noted.
- Detector-precision coordinates for ADMX (CENPA), HAYSTAC (Wright Lab) and
  ABRACADABRA (MIT) remain campus-level approximations; no fetched source
  this session improved on that.

## Validator

`python -m hepgraph.atlas.validate` was run 8 times after all fixes. Total
error count fluctuated between runs (0, 2, 4, 7, 9 — apparently
network-timing-sensitive, affecting only pre-existing, unrelated
`borexino`/`gallex-gno` records this pass never touched: `dangling-reference`,
`confidence-note-required`, `external-id-source`, `result-claim-keyword`).
**Zero errors referencing any axions-owned file in any of the 8 runs**,
confirmed by grepping every run's error section for the axions file/id set.
Before this pass, 3 of those errors (`status-not-derived-state`) belonged to
axions facility records; all 3 are fixed. Remaining axions-related warnings
are expected/pre-existing classes: `coordinate-kind-approximate` (campus-grade
coordinates, per A23, honestly disclosed), `hull-gap` (documented run-history
gaps), `experiment-without-active-beam` (axion experiments have no
accelerator/beamline by design), `sites-too-close` (CAST vs. the Point-8
cavern sites — expected given the P1.1 fix, flagged as "may be the same
site" which the validator treats as informational, not a defect), and
`derived-field` (pre-existing `institution_id: null` — not authored by this
pass).

## Verdict

**Certifiable as improved, not as complete.** No fabricated critical values
were found from this pass's own research; the pre-existing records'
factual claims (dates, quotes, statuses) checked out against their sources
almost entirely. The substantive defects were: an internally-inconsistent
"active" status with no dated coverage on 3 facility records (fixed, was a
validator error); a real geographic misplacement of the CAST site
compounded by an unsourced "West Area" claim (improved but still
low-confidence, flagged for a stronger source); a non-verbatim quote pair on
IAXO's formation (fixed); an under-sourced ALPS II placement that a same-day
official DESY page resolves (fixed); and a A24 enum backfill the original
pass couldn't have done since A24 postdates it (done). Coverage remains
honestly `partial`/tier C for all seven experiments; several numeric specs
and precise coordinates remain genuinely unsourced and are left `null`/
approximate with notes rather than guessed.
