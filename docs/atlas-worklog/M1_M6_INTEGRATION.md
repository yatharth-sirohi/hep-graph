# M1–M6 integration: the teaching phase, merged and checked as one build

Integration branch `atlas-next`, 2026-10-28. It holds every M1–M6 stream, the
all-of-HEP coverage wave, the independent review and its two fix streams (data and
wording, interface and export), the "no Wikipedia" re-sourcing, and data follow-ups 2.
This is the build that goes to `main`.

## What is in it

| Milestone | What a reader gets | Workup |
|---|---|---|
| M1 first impression | Header view switcher, Key popover and Filters drawer in place of the sidebar; a Start-here card whose questions land; a shaded-relief globe with one icon per facility kind; labelled beam arcs for every beamline, with NuMI, K2K and T2HK baselines sourced | `M1_ROUND_01.md`, `M1_ROUND_02.md` |
| M2 beams and protons | Beam through the Earth (`#/view/beam-section/<beamline>`); Follow the proton (`?proton=N`), the injector chain of the timeline year on the true ring geometry at CERN, Fermilab, J-PARC, BNL, KEK, SLAC | `M2_ROUND_01.md` |
| M3 classroom | Six sourced tours with a player and presenter mode (`#/tour/<slug>?step=N`), projector theme, embed mode, a 29-term glossary, PNG export of the globe, a map or a view, and a printable facility sheet | `M3_ROUND_01.md` |
| M4 charts | Going underground (depth against cosmic-ray muon flux), the energy frontier (one point per dated era), Results as a story, the WIMP exclusion plot from HEPData, the detector line-up at true scale, footprint overlays at true scale | `M4_ROUND_01.md` |
| M5 data depth | Accelerator chains with dated feeds and stage energies, underground-lab muon flux (A27), detector dimensions (A31), and the coverage wave | `M5_COVERAGE_WAVE.md` |
| M6 research tools | Compare two to four experiments with sourced cells and CSV, BibTeX from recorded fields only, CSV/JSON list export, and HEP Graph × Atlas person pages | `M6_ROUND_01.md` |

Coverage, release → now:

| Records | Release (`main`) | This build |
|---|---|---|
| experiments | 131 | 413 |
| facilities | 48 | 101 |
| results | 109 | 523 |
| detectors | 135 | 410 |
| collaborations | 122 | 348 |
| accelerators | 31 | 65 |
| sites | 94 | 177 |
| sources | 1,927 | 3,315 |
| tours | 0 | 6 |

Direct dark matter is complete to the user's ask: LUX, LZ, ZEPLIN, XENON10/100/1T/nT,
PandaX-I/II/4T, DarkSide, DEAP-3600, XMASS, CDMS I/II, SuperCDMS, CRESST, EDELWEISS,
CoGeNT, CDEX, DAMA/NaI, DAMA/LIBRA with ANAIS-112, COSINE-100, SABRE, PICO and COUPP
among 71.

## What integration had to fix

The streams passed their own checks; the merged build did not until these were fixed.

- **Merges.**
  - A lost brace in `state.js` stopped the globe from starting.
  - A stacked hunk landed in the wrong place in the a11y test. It was replayed by
    context (`graft.py`) instead of stacking ours on theirs.
  - `views.css` was rebuilt as ours plus their appended rules.
- **Data conflicts, resolved by meaning.**
  - CEBAF kept the follow-up eras with the re-sourced intervals.
  - HERA took the eras with the cleaned sources.
  - The SLAC linac took the union of both sides, without Wikipedia.
  - `higgs-hunt` kept the fix-data2 text, with the Tevatron dated "from 2001".
- **Identifiers.**
  - `experiment:solid` was claimed twice, so the JLab one is now `solid-jlab`, with
    `distinct_from`.
  - The duplicate sources for Aidala and ANAIS-112 were repointed and deleted.
- **Interface, found only on the merged build.**
  - TeX in a bare script group (`10^{20} eV` with no `$`) was not typeset.
  - A result's Significance and Key value showed raw TeX.
  - Stacked chart labels ignored the "omit crowded labels" rule, so on a phone
    "FNAL Linac †" lay over "SPEAR".
  - The overlay key ignored `cmp`/`cmpc`.
  - A key press left the pointer flag set.
  - Results aliases started with the topic name.
  - The theme button sat before the Key popover.
  - The glossary title ran under the close button.
  - The quiet beam colour did not match the globe.
  - The topic camera fought the tour player.
  - Back pressed on a local map while a feature's record was still rendering (about
    80 ms) let the older render finish last and record the selection as shown, so
    Forward reopened nothing. Firefox failed this on every run; Chromium did when
    fast enough. Each full render now carries a serial, and an overtaken one records
    nothing and empties the drawer it wrote into late.
- **Server.** `frame-ancestors *` and the geolocation permission apply to `/atlas`
  only.
- **Bundle budget.** The raw `atlas.json` ceiling is now 3 MB. The 500 KB gzip limit
  is unchanged and is still the binding one: this build is about 2.54 MB raw, about
  447 KB gzipped. The next saving, lazy plain summaries, is noted in `schema.py`.
- **Tests.** Five were pinned to release data and were made data-independent or
  updated to the merged eras; one read the page too early:
  - the BibTeX count of 109 results;
  - route types (which now exclude `view` and `tour`);
  - the drawer's Back;
  - the LHC, LEP and Tevatron era points;
  - cluster names containing ", ";
  - the filter round-trip, which read the region box once after a reload. The
    box is checked about half a second after it is built, so the test now waits
    for that, up to 15 s. Six sampled Firefox loads all checked it before any
    marker was drawn;
  - two checks that assumed Chromium's reporting:
    - The person route expected the endpoint's 503 as a console error, which
      Firefox does not log for a failed fetch. The 503 is now checked on the
      response.
    - Compare on a phone read a `::before` label's computed `content`, which
      Firefox reports as `attr(data-label)` rather than the name;
  - the chart label check, which measured labels with `getBoundingClientRect`.
    Firefox returns the line box of every font in the stack there (24.5 px for a
    15 px label, against 19 px in Chromium), so the LNGS halls, stacked 21 px apart,
    "overlapped" in Firefox only. A 2× screenshot shows them clear. The check now
    uses the glyph box (`getBBox` through `getScreenCTM`), which both engines agree
    on.
- **Test setup.** The local server must run with `HEPGRAPH_ASSET_RATE_LIMIT`
  raised. Otherwise the suite's ~140 fresh contexts trip the asset limit, get 429s,
  and a panel test times out.

## Checks on the final build

The suites ran on bundle `6976bd35bff5100f` (built 2026-10-28). The committed
bundle is `78f3ff2b50f424ab`, built 2026-10-29. Rebuilt with each date, every
file is the same apart from `build_date`, `version` and the manifest's hashes of
those files. The application code was last changed in `4ffa17d`; later commits
touch only the tests.

- Validator: 0 errors.
- pytest: 792 passed, 139 skipped (PostgreSQL tests without a throwaway database),
  on the final code.
- Browser suite:

  | Engine | Result | Run on |
  |---|---|---|
  | Chromium | 141 passed, 0 failed | `4ffa17d`, then the changed tests again on the final code |
  | Firefox | 140 passed, 0 failed | two runs: the first 109 tests on `4ffa17d`, the last 31 on the final tests |
  | WebKit | 140 passed, 0 failed | `af672ba`, which differs from `4ffa17d` only by one early return since removed; the person test again on the final tests |

- Accessibility suite (chromium, `571269d`, before the local-map fix): 56 passed,
  0 axe violations across 67 states.
- The source-quote check was not rerun. Its cache was lost in a reboot, and an
  uncached crawl of the cited sources takes hours. The coverage wave had its own
  hand verification (`VERIFY_COVERAGE_WAVE.md`: 134 items, 34 corrections).
- The local test server must run with `HEPGRAPH_ASSET_RATE_LIMIT` raised (above).

## Follow-ups

Fixed after the ship, on 2026-10-29:

- **Limit results.** All 11 limit results now state their limit, not an exposure.
  - Ten papers draw the limit as a curve. Those records quote the exclusion
    statement and have no single number.
  - TEXONO ULEGe 2008 tabulates it: SI < 0.81 × 10⁻³⁹ cm² at 5 GeV, 90% CL.
  - Two COUPP-4kg claims followed the arXiv listing's v1 abstracts ("strongest",
    "world best"). They now follow the papers' final text ("strong", "new").
  - Logs: `FOLLOWUPS_3_LIMITS_A.md` and `FOLLOWUPS_3_LIMITS_B.md`.
- **CMD, HERA and Mu2e.** Log: `FOLLOWUPS_3_DATA.md`.
  - `collaboration:cmd` is active.
  - HERA has its plain and technical summaries.
  - Mu2e's counts, CD-3 date, run start, sensitivity and solenoid length now rest
    on primary sources, not INSPIRE.
- **Map drawer.** It shows one ×. The record's own "Close panel" button, which left
  the map instead of clearing the selection, is gone from the drawer.
- **Sourced experiment rows.** A16 allows `{id, sources}` rows in a result's
  `experiment_ids`. The results bundle now carries them as plain ids, and the
  sources stay in `provenance.json`.
- **Numeric key values.** A result's "Key value" row showed only `key_value_text`,
  and nothing in the front end read `key_value`. So 95 results' sourced numbers,
  every numeric limit among them, never appeared. The row now falls back to the
  quantity, with plain-text exponents shown whole ("0.81 × 10⁻³⁹ cm²", not
  "10⁻39").

Still open:

- Lazy plain summaries, to keep the gzip budget as coverage grows. `atlas.json`
  is about 447 KB gzipped by the builder's measure, and 457 KB as served.
- `experiment:mu2e` still has an INSPIRE-only "approved 2010-08" date, which
  conflicts with Syphers (October 2009). Its July 2026 status paper says it is
  moving from installation to commissioning.
