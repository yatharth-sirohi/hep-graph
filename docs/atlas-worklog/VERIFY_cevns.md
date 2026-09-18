# Independent verification — cevns (wave 3): COHERENT, CONUS/CONUS+, NUCLEUS, Ricochet

Verifier pass, 2026-09-17. Did not research these records; re-fetched every
cited source with WebFetch and cross-checked every critical value against it.
No subagents spawned. All work confined to `data/atlas/` (cevns-owned files
only) and this worklog.

## Records checked

- Experiments (4): `coherent`, `conus`, `nucleus`, `ricochet`
- Detectors (7): `coherent-csi`, `coherent-cenns-10`, `coherent-ge`,
  `coherent-nai`, `conus-hpge-array`, `nucleus-calorimeter-array`,
  `ricochet-cryocube`
- Collaborations (4): `coherent`, `conus`, `nucleus`, `ricochet`
- Results (4, all COHERENT): `coherent-observation-2017`,
  `coherent-argon-measurement-2021`, `coherent-csi-cross-section-2022`,
  `coherent-germanium-evidence-2024`
- Document (1): `coherent-proposal-2015`
- Facilities (3): `brokdorf-nuclear-power-plant`, `leibstadt-nuclear-power-plant`,
  `ill-grenoble` (+ read dangling `facility:chooz`, now landed by another lead)
- Sites (4): `brokdorf-nuclear-power-plant-campus`,
  `leibstadt-nuclear-power-plant-campus`, `ill-grenoble-reactor-hall`,
  `chooz-very-near-nucleus`
- Sources (25 `src:cevns-*` at start; 24 after this pass — one retired, see
  Fixes) plus the reused `src:topic-coherent-2017-cevns-observation`
- `data/atlas/coverage/cevns.json`, `hepgraph/atlas/schema.py` enums
  (`EXPERIMENT_KINDS`, `RESULT_TYPES`, `RESULT_CLAIM_KEYWORDS`), and
  `hepgraph/atlas/build.py` (search-bundle and principal-facility logic, to
  check the search-discoverability question the brief raised)

## Values re-fetched (WebFetch, this session)

24 distinct URLs opened and cross-checked against the file that cites them:
arXiv abstract pages 1708.01294, 2003.10630, 2110.07730, 2406.13806,
1509.08702, 2011.00210, 2401.07684, 2407.11912, 2501.05206 (abstract, then
full HTML text at `/html/2501.05206v1` to locate two quotes not present on
the abstract page), 1704.04320, 2211.04189, 2603.24450, 2208.01760,
2507.22751; `coherent.ornl.gov/the-collaboration/`,
`coherent.ornl.gov/the-coherent-detector-suite/`, `coherent.ornl.gov/`;
`inspirehep.net/experiments/1486780` (abs page returned nothing useful — a
JS-rendered page — refetched via `inspirehep.net/api/experiments/1486780`,
10 s after the first inspirehep.net request, staying at ≤1 request/10s);
Wikipedia pages for Brokdorf, Leibstadt, CONUS, ILL, Chooz nuclear power
plants. Every quote, title, date, mass, cross-section, significance and
coordinate checked this way matched the cited file **exactly**, with one
apparent mismatch that turned out to be a tooling artifact, not a research
error (see Findings).

## Findings by severity

**P0 (unresolved factual contradiction): none.** All four COHERENT result
titles, dates, `result_type`s and significance figures match their sources
verbatim (2017 observation, 6.7σ; 2021 "First Measurement" on argon; 2022
"Measurement... on CsI"; 2024 "Evidence... Germanium Array", 3.9σ). Detector
masses (14.6 kg CsI[Na], 22 kg CENNS-10, 8×2.2 kg=17.6 kg Ge-Mini, 185 kg
NaI[Tl]), the COHERENT collaboration's 2013 formation and "21 institutions
from 4 countries" (INSPIRE recid 1486780, confirmed legacy_name
`ORNL-SNS-COHERENT` via the API), Brokdorf's 17.1 m baseline / 2021-12-31
shutdown / 2023 move to Leibstadt, NUCLEUS's and Ricochet's commissioning
status against their 2026/2025 papers, and Ricochet's 8.8 m baseline all
check out.

**P1 — fixed:**

1. **CONUS+ was unreachable by name search.** `experiment:conus`'s `name`
   was plain `"CONUS"` with no alias (A20 correctly forbids a `"CONUS+"`
   alias — it normalises to the same string as the name). `search.json` is
   built only from `name`/`aliases` (plus a substring fallback on
   `subtitle`, which for an experiment is just its kind and host facility —
   never "CONUS+"). Confirmed by building `search.json`: typing "CONUS+"
   would surface `collaboration:conus` ("CONUS / CONUS+ Collaboration") and
   `detector:conus-hpge-array` ("CONUS / CONUS+ HPGe detector array") — both
   already renamed by the researcher — but **not** the experiment record
   itself, the one a search bar user most wants. **Fix:** renamed
   `experiment:conus`'s `name` to `"CONUS / CONUS+"`, matching the
   collaboration/detector convention already established in this same
   dataset; also updated the coverage registry row's `name` for consistency.
   Verified in the rebuilt `search.json` that "CONUS+" now matches the
   experiment.
2. **Search subtitle named the closed Brokdorf plant, not the current
   Leibstadt host.** `experiment:conus.facility_roles` lists Brokdorf and
   Leibstadt both with `role: "host"`; `build.py`'s `_principal_facility()`
   (used for the search-result subtitle) breaks a role tie by list order and
   has a documented escape hatch — a role note containing "historic" is
   deprioritised (built for exactly this DUNE-at-CERN-prototype situation).
   Brokdorf's note said only "Original host, 2018-2023...", so the built
   subtitle read "Cevns · Brokdorf Nuclear Power Plant" for a currently
   active-at-Leibstadt experiment. **Fix:** reworded the note to "Historic
   host, 2018-2023, superseded by facility:leibstadt-nuclear-power-plant in
   2023...". Rebuilt and confirmed the subtitle now reads "Cevns · Leibstadt
   Nuclear Power Plant".
3. **COHERENT's technical summary overclaimed the NaI[Tl] array.**
   `experiments/coherent.json.summary.technical` said "NaI[Tl] arrays
   (initially 185 kg, later ton-scale)", stating a planned future expansion
   as an accomplished fact. The detector record it summarizes
   (`detectors/coherent-nai.json`) is explicit that the ton-scale array is
   "discussed on the same page as a plan, not independently verified as
   built in this pass." This is exactly the kind of prose overclaim ground
   rule 3 forbids in substance, even though it sits in a free-text summary
   field the validator doesn't check. **Fix:** reworded to "a 185 kg
   NaI[Tl] array (a ton-scale expansion is discussed as a plan but not
   independently confirmed as built)".
4. **A genuine new duplicate source, introduced by concurrent work.**
   Partway through this verification, the `reactor-solar-neutrino` lead
   landed `facility:chooz` and `src:chooz-npp-wikipedia`, citing the exact
   same URL as the cevns-owned `src:cevns-nucleus-chooz-wikipedia`
   (`en.wikipedia.org/wiki/Chooz_Nuclear_Power_Plant`). This produced a live
   `duplicate-source-url` **error**. Per rule 4 (reuse an existing source for
   the same URL instead of duplicating), repointed
   `sites/chooz-very-near-nucleus.json` to `src:chooz-npp-wikipedia` and
   deleted the now-orphaned `data/atlas/sources/cevns-nucleus-chooz-wikipedia.json`.
   Also refreshed that site's stale note claiming `facility:chooz` "does not
   exist yet" (it now does).

**P2 (noted, not changed — judgment calls, not clear errors):**

- `experiments/coherent.json`'s "detector deployment and physics operation"
  interval starts 2016 (approximate), while `detectors/coherent-csi.json`'s
  own "operating" interval starts 2015 (uncertain, explicitly a lower
  bound). Both are honestly hedged and explained in their own notes, but the
  two dates are in mild tension: if CsI plausibly ran from 2015, the
  experiment's active phase arguably started then too. Not fixed —
  resolving it would mean picking a specific year neither source states,
  which is exactly what the researcher was right to avoid.
- `result:coherent-argon-measurement-2021.significance.value` is `3.0` for
  a quote that says "greater than 3-sigma" — a defensible reading of a
  `>`-bound as its own threshold value, but arguably better flagged
  `confidence: approximate` rather than `verified`. Left as is; not a
  factual error.
- `result_type: "precision_measurement"` for the 2022 CsI paper (the brief
  said "Measurement" 2022): the paper's own title says "Measurement...",
  but the result is also explicitly the "most precise measurement of CEvNS
  yet" and extracts the weak mixing angle — `precision_measurement` is a
  valid enum value and a defensible, arguably more accurate choice than the
  brief's shorthand. Not changed.
- Several stale "does not exist yet in this repo as of 2026-09-17" notes on
  dangling references have since resolved themselves as other wave-3 leads
  landed `facility:oak-ridge-national-laboratory`, `site:ornl-sns-neutrino-alley`
  and `accelerator:sns` during this session (COHERENT's own placements/roles
  now resolve). Left as-is except where I was already editing the same note
  for another reason (`chooz-very-near-nucleus.json`); harmless staleness,
  not a validator finding.

## Verified as correctly handled (per the brief's specific asks)

- COHERENT Ge array 10 kg vs. 17.6 kg conflict: both recorded, 17.6 kg
  (Ge-Mini, the array that actually produced the sourced 2024 evidence
  result) used as the primary spec, 10 kg kept only as a separate,
  lower-confidence interval with the ambiguity documented. Reasonable.
- CONUS as one experiment record: defensible from the collaboration's own
  words — arXiv:2407.11912 verbatim: "continuing on this way the CONUS
  physics program started at the Brokdorf nuclear power plant... the same
  four... HPGe detectors produced for the former experiment, however
  refurbished." Confirmed by re-fetching the paper's full text.
- `kind: "cevns"` and `secondary_kinds: ["reactor_neutrino"]` are valid
  values in `hepgraph/atlas/schema.py`'s `EXPERIMENT_KINDS` tuple.
  COHERENT correctly omits the reactor secondary (it's spallation-source
  based, not reactor-based).
- Reactor site coordinates (Brokdorf, Leibstadt, ILL, Chooz) are honestly
  `kind: "campus"` / `confidence: "approximate"` under A23, each with a note
  naming what's missing (a detector-hall position); coordinates verified
  digit-for-digit against the cited Wikipedia infoboxes.
- INSPIRE recid 1486780 for COHERENT confirmed directly against the API
  (`legacy_name: "ORNL-SNS-COHERENT"`, `long_name: "COHERENT"`,
  `control_number: 1486780`).

## Validator / build status

`python -m hepgraph.atlas.validate`: because 16 wave-3 leads and other
sessions are landing files in this same worktree concurrently, the total
error count fluctuates run to run (19–45 across this session, entirely from
other workstreams' in-flight files — e.g. `facility:chooz`/Double Chooz
landing mid-session, `accelerator:sns`/`facility:mit` status mismatches).
**Zero error-severity findings are attributable to any cevns-owned file** in
every run taken after the fixes above, checked by grepping every error block
against `coherent|conus|nucleus|ricochet|brokdorf|leibstadt|ill-grenoble|
chooz-very-near|cevns` each time. The three expected `facility:chooz`
dangling references (`collaborations/nucleus.json`,
`experiments/nucleus.json`, `sites/chooz-very-near-nucleus.json`) resolved
themselves once that lead's facility record landed mid-session, and are no
longer dangling at all. Remaining warnings on cevns files are exactly the
expected `coordinate-kind-approximate` (A23, all 4 reactor sites),
`interval-start-unknown` (CONUS's two `start: null` intervals), and
`experiment-without-active-beam` (COHERENT and CONUS, both structurally
beam/reactor experiments with no accelerator/beamline entity in this wave).

`python -m hepgraph.atlas.build`: succeeds, writes 31 bundle files. Rebuilt
twice during this pass to confirm the two search-affecting fixes actually
changed `search.json` as intended.

## Fixes applied (files touched)

- `data/atlas/experiments/conus.json`: renamed to "CONUS / CONUS+"; reworded
  the Brokdorf `facility_roles` note to say "historic host"; two notes
  appended explaining both changes.
- `data/atlas/experiments/coherent.json`: corrected `summary.technical`'s
  NaI[Tl] ton-scale overclaim; one note appended.
- `data/atlas/sites/chooz-very-near-nucleus.json`: repointed from
  `src:cevns-nucleus-chooz-wikipedia` to `src:chooz-npp-wikipedia`
  (duplicate-URL fix); refreshed a stale dangling-reference note; one note
  appended.
- `data/atlas/coverage/cevns.json`: `name` for the CONUS row updated to
  match.
- `data/atlas/sources/cevns-nucleus-chooz-wikipedia.json`: deleted (orphaned
  duplicate of `src:chooz-npp-wikipedia` after the repoint above).

All edits written in canonical form
(`json.dumps(sort_keys=True, indent=2, ensure_ascii=False)` + trailing
newline), `verified_at`/fix-note dates `2026-09-17`.

## Unverifiable values (left as the researcher left them; correctly hedged)

CONUS/NUCLEUS/Ricochet collaboration formation dates and membership counts
(no official page found by either of us); NUCLEUS's exact distance from the
Chooz core; Ricochet's final full-CryoCube mass (only the 126 g commissioning
module is precisely sourced); exact CsI[Na]/NaI[Tl]/Ge installation dates for
COHERENT (bounded, not exact). None of these were asserted as facts anywhere
I could find — all are `null` with a note or explicitly flagged
approximate/uncertain.

## Verdict for COHERENT (flagship)

**Certifiable as zero unresolved factual contradictions.** Every quoted
title, date, mass, cross-section, significance figure and the INSPIRE recid
were independently re-fetched and matched exactly. The one prose overclaim
found (NaI[Tl] "later ton-scale") has been corrected. The Ge-mass conflict
(10 kg vs. 17.6 kg) is disclosed and handled defensibly rather than
resolved by guessing. CONUS, NUCLEUS and Ricochet (mandatory-bar depth) are
also clean at the error level; their P1 fixes were about discoverability and
a duplicate-source housekeeping issue, not factual accuracy.
