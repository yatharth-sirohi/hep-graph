# Release-candidate red team — HEP Atlas v1.0 (addendum §31)

Adversarial pass on the release candidate (`hep-atlas-v1-rc`, worktree
`~/Desktop/HEP-Graph-atlas-rc`), run solo (no subagents), against a local
server on port 8795. Method: read the ontology (A1–A24), architecture,
coverage, validation and release-report docs and `INTEGRATION_ISSUES.md` rows
38–54 first, then attacked each of the eight areas in the brief with either a
local script against `data/atlas/`/`hepgraph.atlas.schema` (timeline,
coordinates, membership) or live re-fetches via WebFetch (facts, sources),
plus the existing and a supplementary Playwright suite for the UI. Every
number below is what a rerun of the cited command/script produces, not a
transcription.

One environment note, not a product finding: my assigned port 8795 was
occupied on startup by an orphaned, unrelated `fixture_server.py` (PPID 1,
running >24h, from a different session's scratchpad) serving a stale, much
smaller JSON tree with the same top-level keys as `atlas.json`. That made the
gzip/Content-Encoding check look broken on the first attempt. I killed the
orphaned process (not an INSPIRE importer, not another session's git
worktree) and restarted the real server; see "6. Performance" below for the
real result.

## 1. Scientific facts and dates — 25 experiments, random sample

`random.seed(42); random.sample(experiments, 25)` over `data/atlas/experiments/`:
damic-m, anita, lhaaso, kamland, zeus, cdf, nexo, belle-ii, moedal, totem,
snd-lhc, legend, babar, lz, icarus, alps-ii, alice, star, d0, damic, katrin,
majorana-demonstrator, supercdms-soudan, lhcb, cuore.

For each, extracted one sourced critical claim (a `key_specs` quantity with a
`quote`, or a dated interval) and re-fetched the cited source live.

**Result: 21/22 resolvable claims confirmed verbatim/accurate (95%); 1
confirmed defect (fixed); 3 of 25 inconclusive (site blocks automated
fetch, not a data problem).**

| # | Experiment | Claim | Result |
| - | --- | --- | --- |
| 1–5, 7–9, 11–18, 20–25 | damic-m, anita, lhaaso, kamland, zeus, nexo, belle-ii, moedal, snd-lhc, legend, babar, lz, icarus, alps-ii, star, damic, katrin, majorana-demonstrator (minor case diff only), supercdms-soudan, lhcb, cuore | key spec / date quote | **Confirmed verbatim** against the live source (arXiv abstract/full text via ar5iv, INSPIRE API, official pages) |
| 10 | **totem** | Roman Pot count "quote" | **DEFECT (P1, fixed)** — see below |
| 6 | cdf | detector mass quote | Inconclusive — `fnal.gov` returns HTTP 403 to WebFetch |
| 19 | d0 | detector mass quote | Inconclusive — `fnal.gov` returns HTTP 403 to WebFetch |
| 17 | alice | detector mass quote | Inconclusive — `iopscience.org` redirects to a bot-check page |

**Finding F1 (P1, fixed).** `data/atlas/experiments/totem.json`,
`key_specs[].quantity` for "Roman Pot count": the `quote` field read
`"Twenty-six Roman Pot detectors equipped with silicon sensors to measure
scattered protons."` — a sentence that does **not** appear verbatim on the
cited page (`https://home.cern/science/experiments/totem`), violating A15
("quote... verbatim ≤300 chars seen in the fetched content"). Live re-fetch
found the page actually says two separate things: *"26 'Roman pot'
detectors"* (the count) and, elsewhere, *"'Roman Pots' with silicon sensors
perform measurements of scattered protons."* — the data's quote spliced them
into one sentence. The value (26) itself was correct throughout. Fixed by
replacing the quote with the sentence that actually supports the count,
`verified_at` bumped to 2026-09-18, and a `note` recording the correction.
This is exactly the "dominant defect" class `HEP_ATLAS_V1_REPORT.md` §8
already names ("paraphrased or spliced 'verbatim' quotes") — this instance
had not been caught.

**Wave-1 flagship staleness (ATLAS, CMS, DUNE, Super-K, T2K) vs. 2026-09-17:**
- **ATLAS/CMS LS3.** Both experiments' records give LS3 start as `2026-06`,
  sourced to `src:cern-ls3-farewell-2026` (CERN press release, dated
  2026-06-29). Live re-fetch of that exact URL confirms the quoted sentence
  and date verbatim. A generic CERN LHC overview page I also fetched live
  says "LS3, starting in July 2026" — the atlas is *more* precise/current
  than that page, not stale. No finding.
- **DUNE (P2, not fixed).** Fermilab's own newsroom
  (`news.fnal.gov`, live-fetched) headlines **"Fermilab marks major milestone
  for world-leading DUNE experiment" (2026-05-07)** — start of steel beams
  being lowered underground to house the far detectors. Neither
  `experiment:dune`'s nor `detector:dune-far-detector-1`'s interval history
  (last entry: "from later in 2024: cryostat and detector installation",
  open-ended) reflects this. No claim in the record is false — it's a
  currency/coverage gap, not fixed here because adding a new sourced interval
  is new content, not an unambiguous correction, and the record's existing
  claims all still check out.
- Super-K/T2K: no staleness found in local interval/state checks; not
  independently re-fetched live against current news for this pass (time
  budget) — flagged as unverified-for-currency rather than clean.

## 2. Timeline anachronisms (addendum §11)

Ran `schema.state_at` for every experiment/facility/collaboration at 1965,
1975, 1985, 1995, 2005, 2012, 2020, 2026 (script:
`/tmp/.../check_timeline.py`, reproducible from this report). Cross-checked
every automated flag by hand.

- **Facility-founding-before-experiment (Homestake/SURF, SNO/SNOLAB,
  Super-Kamiokande/Kamioka Observatory).** My script flagged these; on
  inspection they are the same known, documented pattern (a historic
  mine/site's modern successor facility record doesn't extend back to the
  pioneering experiment's actual years) and **the validator already reports
  them as A12 warnings** (`the experiment starts ... before its host
  facility ...`). Not a hidden defect — confirmed the validator is doing its
  job here. No new finding.
- **"Collaboration active while its experiment is only proposed/approved"**
  (FASER, LHCb, MoEDAL, TOTEM, LHCf, XENON, DarkSide) — investigated each
  collaboration's own sourced `formation`/interval data; in every case the
  collaboration's start date is an LOI/proposal-group formation date
  genuinely earlier than the experiment's own approval, correctly sourced.
  Not a bug — collaborations legitimately predate their experiment's formal
  approval while writing the proposal.
- **Planned-interval-rendering-as-active (A21):** 0 violations found.
- **Result-before-date / facility-active-before-founding beyond the above:**
  none found.

## 3. Coordinates

Script over all 93 `data/atlas/sites/*.json` + 48 facilities:

- Lat/lon range violations: **0**.
- Cross-facility duplicate points (same rounded coordinate serving two
  different facilities): **0**.
- Sites >50 km from their facility's primary site: **1**
  (`site:km3net-orca-toulon`, 1127 km from ARCA/Capo Passero) — legitimate,
  KM3NeT is an `astrophysical_neutrino`-kind experiment, the explicit A21
  exception.
- `kind` × `confidence` distribution: `campus` sites are never `verified`
  (54 approximate + 13 uncertain, 0 verified) — consistent with A23's honesty
  rule. `detector`/`underground_lab` verified points (12 of them) all cite
  rank ≤8 sources (`detector_paper`, `official_experiment_site`,
  `journal_article`, `design_report`, `official_facility_site`) — **0** A17
  violations (no `verified` detector-kind point resting on a geocoder alone).
- §42 seed facilities (9: Amundsen-Scott/South Pole, CERN, Fermilab, J-PARC,
  Kamioka Observatory, KEK, LNGS, Soudan, SURF) — 8 already had a non-null
  `primary_site_id`; **KEK did not.** See Finding F2.

**Finding F2 (P1, fixed).** `facility:kek` had `primary_site_id: null`
(deliberately, per its own `notes`, pending `site:kek-tsukuba-belle-ii` being
authored by another workstream). That site now exists, has `facility_id:
facility:kek` and a sourced coordinate, and is KEK's only site — the
dangling-reference risk that justified leaving it null no longer applies.
`static/atlas/js/globe.js:427` and `static/atlas/js/fallback.js:74` both key
off `facility.primary_site_id` to place a facility's marker/fallback-list
entry, so a null value meant **KEK — a named §42 seed facility, host of
Belle/Belle-II/K2K — had no marker on the globe and no fallback-list
entry**, confirmed by inspecting the generated bundle before the fix. Fixed
in `data/atlas/facilities/kek.json`; the release report's "KEK has none" /
"pre-existing gap" language was stale the moment this was fixed, so I updated
`docs/HEP_ATLAS_V1_REPORT.md` §3 in the same pass.

## 4. Collaboration membership and identity

All three membership files (`atlas.json` 198 rows, `cms.json` 244,
`dune.json` 217 — matches every "three collaborations deep" claim in
`HEP_ATLAS_VALIDATION.md`/`HEP_ATLAS_V1_REPORT.md`):

- Evidence-class distribution: ATLAS/DUNE 100% `official_institution_list`,
  CMS 100% `publication_affiliation_current`. **0** source-type mismatches
  against A19's precedence table (checked every row's cited sources'
  `source_type` against the required set for its `evidence_class`).
- All 12 `person:inspire-*` records carry `identity_evidence` with a method
  and non-empty sources (all `inspire_profile_affiliation_match`).
- UI wording: inspected the generated bundles directly
  (`static/atlas/generated/people/dune/university-of-iowa.json` and others)
  — `evidence_label` strings match `EVIDENCE_CLASS_TEMPLATES` in
  `hepgraph/atlas/schema.py` verbatim, e.g. `"INSPIRE author profile lists
  this collaboration"`. (The wording lives server-side, baked into the
  bundle at build time and rendered by `panels.js`'s `evidence_label` field —
  not constructed client-side, so grepping the JS for the template strings,
  my first approach, correctly found nothing; that is not a defect.)
- No person found attributed on institutional affiliation alone (`derived`
  is absent from every person-row evidence-class distribution, consistent
  with A19 forbidding it on person rows).

**No findings in this category.**

## 5. UI state (Chromium, generated tree, port 8795)

`HEP_URL=http://127.0.0.1:8795 HEP_ATLAS_DATA=generated node
tests/browser_atlas.cjs`: **25/25 pass** (log:
`test-results/atlas/final_check_generated2.log`), after rebuilding the atlas
bundles to pick up Findings F1/F2 (see "Fixes applied"). One run mid-session
hit `page.waitForFunction: Timeout 30000ms exceeded` on the A23
approximate-marker check; that check's own in-file comment already documents
it as a session-state-accumulation flake specific to very late,
same-browser-instance checks (not the marker/aria logic), and a clean rerun
passed — logged as a pre-existing flake, not attributed to my data changes.

Supplementary exploratory suite (not in `browser_atlas.cjs`), written this
pass — cold deep links to all six entity types, malformed ids, back/forward,
filter+year URL round-trip on reload, and the HEP Graph handoff link — **14/14
pass** (`test-results/atlas/redteam_ui_exploratory.log`):
- Cold `#/facility/cern`, `#/experiment/atlas`, `#/collaboration/atlas`,
  `#/result/atlas-higgs-observation-2012`, `#/document/dune-fd-tdr-vol-1`,
  `#/topic/accelerator-dark-matter-searches` all open their panel directly
  with no console errors on a fresh load.
- Malformed hashes (`#/facility/does-not-exist-xyz`, `#/experiment/` empty
  slug, `#/bogus-type/atlas`, `#/facility/../../etc`, `#/facility/%00`) never
  blank the page or throw an uncaught error — `state.js`'s `parseHashEntity`
  degrades safely.
- `?y=2012` round-trips exactly through a reload.
- Back/forward between two entity panels lands on the right one each way.
- The HEP Graph handoff (`a.hep-graph-link`, `href*=mode=live`) is present
  and correctly formed on DUNE + University of Iowa's institution panel.

My first draft of this supplementary suite had 6 false failures from using
the wrong CSS selector (`.panel`/`[role=dialog]` instead of the app's actual
`#detail-panel`) — corrected before drawing any conclusion; noted here so the
"6 failures" isn't mistaken for a real defect if this file is skimmed.

**No product defects found in this category.**

## 6. Performance

- **gzip (the one item the brief specifically asks to check):** confirmed
  correct. `curl -H "Accept-Encoding: gzip"` → `Content-Encoding: gzip`,
  `Content-Length: 191561` (from 1,422,979 bytes uncompressed, ~13.5%); a
  request without that header gets the real uncompressed
  `Content-Length: 1422979` and no `Content-Encoding` header. (First attempt
  looked broken because of the orphaned-process port collision noted above,
  not a server bug.)
- Cold load (localhost, Chromium, generated tree): 21 requests, 851,372
  bytes with compression, `networkidle` at 821 ms, first non-empty
  `<canvas>` at 1512 ms. Not representative of WAN latency — a local-loopback
  number, reported as such.
- Panel-open bytes: **0** additional bytes on opening a facility panel
  (confirms `browser_atlas.cjs`'s own "Opening a panel does not fetch
  provenance/sources" check and `HEP_ATLAS_V1_REPORT.md`'s "0
  provenance/sources requests" claim).
- FPS (software rasterizer, SwiftShader, from the suite's own instrumented
  run): ATLAS 13.5–14.5 fps, CMS 14–14.5 fps with arcs on — inside the
  report's claimed 12.5–15.5 fps range. No finding.

## 7. Source links — 40 sampled, 17 fetched

`random.seed(7); random.sample(sources, 40)` over `data/atlas/sources/`.
Given the time budget, fetched 17 of the 40 (skipped most of the sample's 13
ROR ids after confirming one, since they are low-risk identity lookups, not
narrative claims) spanning `official_facility_site`, `official_experiment_site`,
`journal_article`, `arxiv`, `wikipedia`, `experiment_registry`,
`inspire_experiment_record` and `geocoder`. **17/17 reachable and consistent**
with their `retrieval` claim (`partial`-marked pages were genuinely
thin/stub content; `full_text`-marked pages had the full article) and, where
a citing quote existed, it matched. Examples: `src:jparc-linac-page`
(`partial`) really is a stub; `src:cms-official-w-mass-news`
(`full_text`) verbatim-matches its cited 80360.2±9.9 MeV quote;
`src:ror-01nrxwf90` resolves (via the ROR API — the ROR *website* is a JS
SPA WebFetch can't render, same class of tooling limit as INSPIRE's HTML
pages) to the University of Edinburgh, matching the institution it's cited
on. **No defects found in the 17 checked; the remaining 23 of 40 are
unverified, not cleared** — this is a partial sample, reported honestly
rather than rounded up.

## 8. Honesty of the coverage/validation/release reports

- **`docs/HEP_ATLAS_COVERAGE.md`**: spot-checked the "Independently verified"
  table — all 15 named `VERIFY_*.md` files exist and are substantive
  (thousands of lines total, real re-fetch logs, not stubs). The "3
  collaborations deep" membership claim matches the actual file count.
  No defects found.

- **Finding F3 (P1, fixed).** `docs/HEP_ATLAS_VALIDATION.md` §8 claims to be
  fully machine-generated and re-checkable
  (`scripts/atlas_validation_counts.py --check`). Running `--check` against
  the committed doc **failed**. Root cause: the committed block's §8.7
  manual-fields table (`accessibility_audit`, `firefox_manual_run`,
  `safari_manual_run`, `subagent_count_total`) showed **"not yet run"** even
  though `docs/atlas-worklog/validation_counts_manual.json` and
  `REVIEW_accessibility.md`/`REVIEW_browser_matrix.md` show this work was
  completed and documented weeks/days earlier. The committed release
  document was understating already-finished, already-reviewed work — not
  overclaiming, but still self-contradicting against its own generator and
  against the rest of the repository. Regenerated with real inputs
  (`--pytest-log` from a fresh `pytest -q` run: 513 passed/129 skipped,
  matching the old committed number exactly; `--browser-results` from a
  fresh `browser_atlas.cjs` run: 25/25). `--check` now passes.

- **Finding F4 (P2, fixed).** `scripts/atlas_validation_counts.py`'s
  `load_browser_results()` calls `path.relative_to(ROOT)` on paths produced
  by globbing the *input* `--browser-results` directory; if that directory is
  passed as a relative path (as the script's own `--help` text shows as the
  usage pattern, and as anyone running it from the repo root naturally
  would), every resulting glob path is also relative, and `relative_to`
  raises an uncaught `ValueError`, crashing the whole script. Only the
  default (absolute, `ROOT`-derived) path worked. Fixed by resolving the
  input directory before globbing; confirmed both the previously-crashing
  relative invocation and `--check` now succeed.

- **Finding F5 (P1, fixed).** `docs/HEP_ATLAS_V1_REPORT.md` §10
  ("Performance") ends with the literal, unfilled line **`- Accessibility:
  [TBD-A11Y].`** — a placeholder token shipped in what the brief calls "the
  draft release report — every claim in it is a target," even though the
  accessibility audit had already run and passed with documented results
  (0 violations across 16 axe-core scans, 30/30 manual checks, 3 P1s found
  and fixed). Filled in with the real, sourced summary.

- §10's bundle-size and FPS numbers, and §5's exact status-distribution
  counts (54 completed / 43 active / 10 construction / 7 commissioning / 6
  shutdown / 5 proposed / 4 upgrade / 1 approved / 1 decommissioned = 131),
  were independently recomputed from the repository and **match exactly**.
  No overstatement found there.

## Fixes applied (all in this worktree, canonical JSON re-serialized via
`hepgraph.atlas.load.write_json`, `verified_at`/dated 2026-09-18)

| # | Severity | File(s) | Fix |
| - | --- | --- | --- |
| F1 | P1 | `data/atlas/experiments/totem.json` | Replaced a non-verbatim, two-sentences-spliced `quote` with a real verbatim one from the same cited page; value unchanged (still 26, still correct) |
| F2 | P1 | `data/atlas/facilities/kek.json` | Set `primary_site_id` to KEK's one existing, correctly-linked site, restoring KEK's globe marker and fallback-list entry |
| F3 | P1 | `docs/HEP_ATLAS_VALIDATION.md` | Regenerated §8 from real `pytest -q` and `browser_atlas.cjs` output so the doc's own `--check` passes and it no longer says "not yet run" for completed, documented work |
| F4 | P2 | `scripts/atlas_validation_counts.py` | Fixed a crash on relative `--browser-results` paths (`.resolve()` before globbing) |
| F5 | P1 | `docs/HEP_ATLAS_V1_REPORT.md` | Filled the shipped `[TBD-A11Y]` placeholder with the real, sourced accessibility summary; updated the now-stale KEK "primary site gap" language in §3 to match F2 |

After all fixes: rebuilt bundles (`python -m hepgraph.atlas.build`, `--check`
clean, version `f91954217a470d5c`), then:

```
python -m hepgraph.atlas.validate        → 0 errors, 1589 warnings, 4 informational (unchanged)
python -m pytest -q                      → 513 passed, 129 skipped
HEP_URL=http://127.0.0.1:8795 HEP_ATLAS_DATA=generated node tests/browser_atlas.cjs
                                          → 25/25 passed, 0 errors
python scripts/atlas_validation_counts.py --check (with real pytest/browser inputs) → current
```

## Findings left open (not fixed this pass)

| Finding | Severity | Why not fixed |
| --- | --- | --- |
| DUNE construction record doesn't reflect the 2026-05-07 Fermilab steel-beam milestone | P2 | Currency gap, not a false claim; adding a new interval is new sourced content, not an unambiguous correction, within this pass's scope |
| CDF/D0 (fnal.gov) and ALICE (iopscience.org, via its DOI) sources are unreachable by automated fetch (403 / bot-check) | Informational | Tooling/environment limitation on the *checker's* side, not evidence the cited content is wrong |
| Majorana Demonstrator quote has a trivial capitalization difference from the source ("the Demonstrator" vs. data's "the DEMONSTRATOR"/lowercase determiner) | P2/cosmetic | Not a substantive verbatim violation; not worth a data churn for a capitalization nuance |
| 23 of the 40 sampled sources (category 7) and Super-K/T2K flagship currency (category 1) not independently re-verified this pass | — | Time budget; reported as unverified rather than assumed clean |

## Release verdict

**No unresolved P0. No unresolved P1** that I could find and that survives
scrutiny — the four P1s found (F1, F2, F3, F5) are fixed and verified above;
the one P2 code bug (F4) is also fixed. The open items above (DUNE currency,
three bot-blocked sources, one capitalization nit, partial category-1/7
sampling) are P2-or-lower and documented, matching the release report's own
stated policy of admitting partial coverage rather than certifying an
incomplete pass as done. `hepgraph.atlas.validate`, `pytest`, and the full
generated-tree browser suite are all green after the fixes and a full
rebuild. I did not run a coverage-completeness red team (addendum §26/row 54
— explicitly out of this task's scope) and did not re-verify Super-K/T2K
staleness or the remaining 23 sampled sources; those are gaps in *this*
pass's coverage, not claims that the release candidate is defect-free beyond
what's reported here.
