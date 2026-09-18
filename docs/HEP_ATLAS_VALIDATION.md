# HEP Atlas validation

What was checked, by whom, and what it found. Counts here are computed from the
repository, not asserted. Where something was not checked, this document says
so; "extensively tested" is not a finding.

## 1. How the work was organised

The project was executed as parallel workstreams with independent review, on
the principle that the agent that researches a record never certifies it.

| Role | Count | What they produced |
| --- | ---: | --- |
| Ontology reviewers | 3 | Entity-schema, temporal-model and provenance reviews of the draft contract, before any data existed |
| Research workstreams | 10 | Fermilab and DUNE; the other Fermilab neutrino experiments; CERN and ATLAS; CMS; Japan; IceCube; dark matter; flavour; historic CERN; research topics |
| Data and platform | 2 | The schema, loader, validator, builder, scaffold and link checker; the globe application |
| Membership | 1 | Institution rosters, institution records and people |
| Independent reviewers | 4 | Data quality (wave 1), scientific and historical, user experience, performance and adversarial |
| Cleanup and integration | 2 | Source-backed defect closure; orchestrator integration |
| Wave 3 (v1.0) research leads | 16 | Fifteen experiment domains (LHC colliders; historical colliders; historical accelerator neutrinos; reactor, solar and radiochemical neutrinos; neutrino mass and 0νββ; astrophysical neutrinos; noble-liquid and cryogenic dark matter; axions; muons; fixed target and kaons; CEvNS; cosmic rays and gamma rays; heavy ions) and one facilities lead for the shared laboratories |
| Wave 3 independent verifiers | 15 | One per domain, re-fetching cited sources; thirteen were separate Sonnet agents, two (muons, cosmic-gamma) were done by the orchestrator after their agents were stopped — `docs/atlas-worklog/VERIFY_*.md` |
| Wave 3 engineering | 3 | W1 caching, lazy provenance, loading and error states, generated validation counts; W3 clustering, semantic zoom, filters and the coordinate-reading fix; W4 accessibility audit and the Chromium/Firefox/WebKit matrix |
| Wave 3 flagship depth | 1 | Results, documents and key specifications for the pre-existing flagships |

Nested delegation was used where it helped and abandoned when it did not: the
first wave of research leads spawned children, but rate limits made deep trees
unreliable, so later waves were single-agent workstreams with separate
verification. In wave 3 the session-wide cap of 20 concurrent agents meant
that only seven nested children ran; every lead otherwise researched its
domain itself, and a different agent verified it afterwards. Two stoppages of
the Sonnet session limit interrupted the wave; work resumed from disk each
time. Every workstream left a log under `docs/atlas-worklog/`; the agent and
verification counts are in §8.7.

## 2. What the atlas contains

The entity counts, the coverage registry by tier, the result-type
distribution and the link-check outcomes are generated in §8 by
`scripts/atlas_validation_counts.py` and checked against the data by
`--check`; this section deliberately carries no typed number. Two properties
of the result set are worth stating in words: every result carries the type
its own publication used, and no result is recorded as a discovery unless the
paper's title or abstract uses that word (A16 checks the keyword
mechanically for discovery, observation, evidence and first detection).

## 3. Automated checks

`python -m hepgraph.atlas.validate` enforces the contract in
`docs/HEP_ATLAS_ONTOLOGY.md`: structure and required fields, referential
integrity, id and alias collisions, date validity and interval ordering,
terminal-status semantics, derived-state agreement, unit and dimension
correctness with per-key plausibility ranges, display-versus-value magnitude,
coordinate kind and source quality, great-circle agreement between a recorded
baseline and its two sites, evidence-class consistency with source type,
claim-level quotes where the contract requires them, and duplicate sources by
normalised URL or DOI.

Errors fell from **368** at the first run against real data to **zero**, and
the pilot gate stayed green through every change.

As of this writing (`.venv/bin/python -m pytest -q`, on the `hep-atlas-v1-w1`
worktree), the suite is **509 passed, 129 skipped** — not the "730 Python
tests" this paragraph previously claimed, which does not correspond to any
figure this run produces (total items, or passed, or passed+skipped, under
any split tried). The 129 skips are all environment-gated (`HEPGRAPH_TEST_DATABASE_URL`
/ `HEPGRAPH_TEST_POSTGRES_DSN` not set, and one A13 pilot-history case pending
real pilot data), not failures. Splitting by file: the seven `tests/test_atlas_*.py`
files (excluding `browser_atlas.cjs`, which is not pytest) run **204 passed,
1 skipped**; the remaining, pre-existing files run **304 passed, 128
skipped**. That pre-existing split does **not** match "527 passed with one
known expected failure" either — no `xfail` marker exists anywhere in the
current test suite (`grep -rn xfail tests/*.py` finds nothing), so the
"known expected failure" this paragraph described is not reproducible today;
it was true of an earlier point in the codebase's history (see e.g.
`docs/RETRIEVAL_SCHEDULING_REPORT.md`'s "527 passed, 1 xfailed (the
pre-existing D6 identity case)"), and either that case was fixed and its
`xfail` marker removed, or the test carrying it no longer exists — this
document cannot tell which from the current tree, so it states only what is
true now. Browser checks: `tests/browser_atlas.cjs` currently runs **17**
`record()`-wrapped checks (`grep -c 'await record(' tests/browser_atlas.cjs`),
not 14 — three were added closing P1-2 and P1-4 in
`docs/atlas-worklog/REVIEW_performance.md` (see that document's "Closure"
section). Section 8 below regenerates the entity/coverage/validator counts
mechanically on every run instead of restating them here by hand.

The new atlas tests cover the schema and temporal semantics, the validator
(one deliberately mutated fixture per rule), the build and its determinism,
the server routes including path traversal and (as of this pass) ETag/304
revalidation, the historical state assertions, and the pilot acceptance
gate.

## 4. The pilot acceptance gate

The specification fixes a gate before the atlas may be expanded: DUNE, ATLAS
and T2K must each answer a fixed list of questions from the data alone.
`tests/test_atlas_pilot_acceptance.py` encodes it and passes 17 of 17.

It asserts, from the canonical records rather than the built bundles, that DUNE
has near and far detectors at distinct located sites with the far site
underground, that a beamline connects them with a sourced baseline, that the
far detector's technology and mass are recorded, that the collaboration has
member institutions that can be placed on a globe; that ATLAS is at CERN and
linked to the LHC, that its detector is placed and specified, that its timeline
spans construction to running, that it is not shown operating in 1990, that its
results are curated with sources and openable references, and that its
collaboration spans at least ten countries; that T2K runs from J-PARC to
Kamioka with a sourced baseline, timeline, results and documents; and that
every resolved person carries a verified INSPIRE identifier.

## 5. Independent review findings

### Data quality, wave one (IceCube, LZ and LUX, Belle and Belle II, CMS)

Zero P0 findings. Every one of 36 independently re-fetched quotes matched its
source verbatim: no fabricated citation, no misattributed quote, no unit error,
no inflated result wording. Three P1 findings: a systemic result-dating defect
in the CMS results, where the contract requires an announcement date to win
over a later preprint; a detector-kind coordinate resting on a Wikipedia
infobox; and duplicate source records shared with other workstreams.

### Scientific and historical review (`REVIEW_scientific.md`)

Zero P0 findings across Fermilab and DUNE, the Fermilab neutrino programme,
Japan, CERN and ATLAS, and the historic experiments. 32 technical values were
re-fetched and matched word for word against their cited primary sources, and
`state_at` was swept across 1975, 1985, 1995, 2005, 2012, 2020 and 2026 for
every entity in scope. Its verdict: a physicist would trust this data. Its one
P1 — Fermilab derived as under construction in every year since 1969 — turned
out to be an unimplemented contract rule rather than a data error, and is
fixed: only lifecycle intervals may set the timeline state.

### Performance and adversarial review (`REVIEW_performance.md`)

Zero P0. No hang, crash, leak or security failure: eleven path-traversal
variants were refused, 400 concurrent asset requests never reached the query
workers or the search rate budget, and memory plateaus after repeated
navigation.

This paragraph previously said "four P1s, all fixed" and named findings —
missing compression, an unused institutions bundle, dropped share-link
years, and search ranking — that do not match what the review actually
recorded (`no compression` is that review's **P2-2**, not a P1, and it never
mentions search ranking at all; it may describe an earlier draft of the
review or a different one). The review states plainly that it is
"measure-and-report only" and "no application code was edited," so **none**
of its four real P1s were fixed by the time it was written. Its actual four
P1s, and their status as of this pass (`hep-atlas-v1-w1`, 2026-09-17):

| # | Finding | Status at review time | Status now | Evidence |
| --- | --- | --- | --- | --- |
| P1-1 | A share link's `y=`/`r=` is silently discarded on load | open | **fixed** | `static/atlas/js/timeline.js`'s `createTimeline` no longer emits at construction ("Deliberately no emit() here"); `app.js`'s `main()` calls `timeline.syncFromState(state.get())` before `timeline.start()` |
| P1-2 | Any panel open eagerly fetches ~2.2 MB of `provenance.json`+`sources.json` even with the Sources disclosure collapsed | open | **fixed this pass** | `static/atlas/js/panels.js`'s `sourcesDisclosure()` fetches only on the `<details>` `toggle` event; see `docs/atlas-worklog/REVIEW_performance.md`'s "Closure (2026-09-17)" section for measured bytes |
| P1-3 | Collaboration-mode drag FPS drops to ~15–20 with institutions+arcs | open | **still open** | Not addressed by this workstream (owned separately, `static/atlas/js/globe.js`); no clustering, LOD or marker-count reduction found in the current file |
| P1-4 | A slow/offline connection shows a blank page with no explanation | open | **fixed this pass** | `static/atlas/index.html` adds `#atlas-error` (`role="alert"`); `app.js` shows visible loading text in the existing `role="status"` notice for the whole cold load and a retry button on failure |

Two of four are closed; one (P1-3) remains open and is out of this
workstream's scope; one (P1-1) was already fixed by another change before
this pass and is verified here by reading the code, not re-measured.

### User-experience review (`REVIEW_ux.md`)

The most valuable review of the four. Four P0 defects, and its verdict was
blunt: "a newcomer would not understand what they're looking at, and an expert
would not trust it past the first timeline scrub — not because the underlying
data is bad, but because four field-name bugs between that data and the screen
make the interface state things the atlas's own data directly contradicts."
The status badge ignored the selected year, so ATLAS read "Upgrade" in 1995;
plain-language summaries existed in the data but never rendered; every
collaboration read "0 confirmed members" above a correct institution count; and
all 56 documents showed blank titles. All are fixed and independently
re-verified against the real bundles, along with four more of the same class
found while auditing for it — including topic pages that listed no experiments
and no results at all.

### Integration defects found by the orchestrator

Four bugs were invisible to both test suites because the browser tests loaded
the fixture tree and the Python tests built the fixture dataset. Against the
real data the globe drew **no markers at all**, collaboration mode showed no
institutions, results mode and the document library were **empty**, and every
shared deep link opened an empty globe. All four are fixed; the release gate
should run the browser suite against both trees, and the fixture generator
should be regenerated from the canonical shape so the two stop drifting.

A fifth was a product bug rather than a test gap: HEP Graph's per-address rate
limiter counted the atlas's static bundles, so browsing returned 429s and a
heavy atlas session would have locked the user out of the search API. Assets
now have their own budget and no longer occupy a query worker.

One near-miss is worth recording. The validator's duplicate-source rule
normalised URLs by stripping their query strings, so it proposed merging eleven
distinct INSPIRE searches into one record and the geocoder lookups for
Fermilab, CERN, J-PARC and Sanford Lab into a single source. Applying it would
have made one facility's coordinates appear to be sourced from a lookup for
somewhere else. The rule was wrong, not the data; the genuine duplicate count
was nine.

### Wave 3 independent verification (`VERIFY_*.md`, 2026-09-17/18)

Each of the fifteen wave-3 domains was verified by an agent that had not
researched it, by re-opening the cited sources. Across the fifteen reports the
verifiers re-fetched roughly 330 sources and recorded 14 P0, 51 P1 and 28 P2
findings; every P0 and P1 was fixed in place and logged, the P2s are documented
judgement calls (§8.7 gives the per-field counts and evidence;
`INTEGRATION_ISSUES.md` rows 38–54 give the classes). The dominant defect
class was not wrong numbers but **paraphrased or spliced "verbatim" quotes**:
values were usually right while the quote presented as evidence was not the
text on the page. Two quotes carried wrong values (CRESST thresholds an order
of magnitude off; a Mu2e solenoid length absent from its source); one 2.7σ
indication had been typed as a first detection; one result claim rested on a
press release; four statuses were stale against the collaborations' own papers
(DAMIC, RENO, SND@LHC, the JUNO PMT count). Two class-level fixes followed:
28 records whose whole lifetime sat in one terminal interval now carry an
operating interval and a terminal event (`collapsed-history` warns on the
class), and eleven sites that had been relabelled `detector` to satisfy the
validator are honest campus points under amendment A23.

The muons and cosmic-gamma verifiers were stopped before reporting; the
orchestrator verified those two domains itself and the reports say so. The
addendum §26 coverage red team and the flagship rosters beyond DUNE, ATLAS and
CMS were started and stopped by the user and were not completed.

## 6. Known limitations

- **Coverage is partial and says so.** Every experiment named in the
  specification's §30–§41 lists and every §42 seed facility exists, but the
  registry's own tier table (§8.2, and `docs/HEP_ATLAS_COVERAGE.md`) shows most
  tier B–D rows as `partial`: mandatory bar met, results and documents absent.
  The footer of the application states that coverage is partial. No coverage
  red team ran, so programmes outside the specification's lists are known to be
  missing (BESIII, KLOE, NA61/SHINE, PICO, DAMA/LIBRA, SuperNEMO, AMoRE, AMS-02
  and others); the coverage report's scope section is the place to look.
- **Membership is three collaborations deep.** DUNE, ATLAS and CMS only; the
  roster workstream for the other flagships was stopped before it produced
  anything. Collaboration records elsewhere carry counts only where the
  collaboration's own page states them.
- **People are a deliberate sample.** Twelve, each resolved to an INSPIRE
  author record and attached only on its own evidence.
- **Much geography is at campus precision and labelled so.** Amendment A23 lets
  a detector site rest on a campus-grade point when the record says so; the
  globe draws those markers dashed and the panel says "Approximate location".
  Around 76 sites carry the flag, including most LHC caverns, the RHIC
  interaction points, the reactor halls and the Fermilab experimental halls.
- **Verification depth varies.** Wave-3 domains were verified by re-fetching
  sources; the verifiers sampled rather than re-opened every one of ~1,500
  sources, and the paraphrased-quote class they found in every domain is the
  main residual risk for fields nobody re-fetched.
- **Link checking is a one-off run**, recorded in each source's `link_check`
  block (§8.1); a dead link never fails the build, and a 404 on the sole source
  of a `verified` value is listed for review rather than fixed automatically.

## 7. Reproducing this

```sh
python -m hepgraph.atlas.validate     # contract enforcement, non-zero on errors
python -m hepgraph.atlas.build --check  # bundles match what data/atlas/ implies
python -m pytest -q                   # see section 8.5 for the current count
python scripts/atlas_coverage_report.py --check     # coverage doc matches the data
node tests/browser_atlas.cjs                        # globe, panels, timeline, mobile, fallback
HEP_ATLAS_DATA=generated node tests/browser_atlas.cjs   # the same against real data
python scripts/atlas_validation_counts.py --check   # section 8 below matches the data
```

To regenerate section 8 itself with live pytest/browser figures instead of
"not provided": run the browser suite against both trees first (writing into
`test-results/atlas/`, which `--browser-results` scans by default), capture a
`pytest -q` log, then:

```sh
python -m pytest -q | tee /tmp/pytest.log
python scripts/atlas_validation_counts.py --pytest-log /tmp/pytest.log
```

and paste its output over section 8 below, keeping the two HTML comment
markers that bound it (search this file for "counts:begin" / "counts:end")
so `--check` can find the block again.

<!-- counts:begin -->

## 8. Final validation counts (addendum §41)

Generated at 2026-09-18 by `scripts/atlas_validation_counts.py`. Every figure below is computed directly from the repository at the moment this ran; nothing here is typed by hand. Run with `--check` to confirm this block still matches the current data.

### 8.1 Entities

| Type | Count |
| --- | ---: |
| Facilities | 48 |
| Sites | 93 |
| Accelerators | 31 |
| Beamlines | 6 |
| Experiments | 131 |
| Detectors | 135 |
| Collaborations | 122 |
| Institutions | 529 |
| People | 12 |
| Results | 109 |
| Documents | 70 |
| Topics | 42 |
| Sources | 1486 |
| Membership rosters | 3 |
| Coverage registry rows | 131 |

Of 1486 sources, 0 (0%) carry a recorded link-check status (`link_check.last_checked` or `link_check.http_status` is not null); the rest have never been through `python -m hepgraph.atlas.linkcheck`.

Results by the type their publication used: 32 observation, 22 measurement, 17 limit, 15 precision measurement, 15 evidence, 4 technology milestone, 2 anomaly, 1 first detection, 1 discovery.

### 8.2 Coverage registry, by tier and researched state

| Tier | Researched | Rows |
| --- | --- | ---: |
| A | full | 21 |
| A | partial | 2 |
| B | full | 11 |
| B | partial | 65 |
| C | full | 2 |
| C | partial | 15 |
| D | full | 4 |
| D | partial | 11 |

### 8.3 Validator findings (`python -m hepgraph.atlas.validate`)

| Level | Count |
| --- | ---: |
| error | 0 |
| warning | 1589 |
| info | 4 |

### 8.4 Integration issues (`docs/atlas-worklog/INTEGRATION_ISSUES.md`)

54 rows parsed across every severity/state table in that file.

| Severity | State | Rows |
| --- | --- | ---: |
| P0 | assigned | 4 |
| P0 | fixed | 2 |
| P0 | fixed (loader accepts both) | 1 |
| P0 | fixed from the collaborations' own papers | 1 |
| P0 | fixed in every verified domain; no mechanical check exists — the release note lists it as the main residual risk for unverified fields | 1 |
| P0 | fixed; a16 keyword check extended to `first_detection` (requires "detect"); kamiokande sn1987a relabelled `observation` to match its title | 1 |
| P1 | assigned | 1 |
| P1 | fixed | 8 |
| P1 | fixed (by a separate change; verified by this closure pass) | 1 |
| P1 | fixed mechanically; new warning `collapsed-history` | 1 |
| P1 | fixed with sourced intervals | 1 |
| P1 | fixed; amendment a23 lets an admitted approximation warn (`coordinate-kind-approximate`), the bundle carries `approximate | 1 |
| P1 | fixed; moedal (`upgrade` vs `active`) remains a documented p2 | 1 |
| P1 | open | 5 |
| P1 | open — out of this workstream's scope (`globe.js`, owned separately) | 1 |
| P1 | sent to pipeline | 4 |
| P1 | split into `experiment | 1 |
| P1 | upgraded to ror geocoder points (rank 8); boulby, cjpl, lsm keep osm points with notes | 1 |
| P2 | closed | 1 |
| P2 | fixed | 1 |
| P2 | fixed by repointing; validator `duplicate-source-url` caught each | 1 |
| P2 | fixed; amendment a24 adds the classes | 1 |
| P2 | open | 9 |
| P2 | open by design (a23) | 1 |
| P2 | sent to pipeline | 1 |
| info | closed | 1 |
| info | not done; stated in the release report | 1 |
| info | open | 1 |

### 8.5 Python test suite

Source: a local `pytest -q` log (outside the repository tree, path not recorded).

| Outcome | Count |
| --- | ---: |
| passed | 513 |
| skipped | 129 |

### 8.6 Browser test results

1 result file(s) found under `test-results/atlas`.

| File | Status | Checks passed | Uncaught errors | Checked at |
| --- | --- | ---: | ---: | --- |
| test-results/atlas/report.json | passed | 23/23 | 0 | 2026-09-18T17:04:18.190Z |

### 8.7 Manual / human-verified fields

From `docs/atlas-worklog/validation_counts_manual.json` — anything a script cannot check for itself.

| Field | Value | Evidence |
| --- | --- | --- |
| accessibility_audit | not yet run | not yet run |
| coverage_red_team | not run | addendum §26 agent was started and stopped by the user; see INTEGRATION_ISSUES.md row 54 |
| experiments_independently_reviewed | 101 (wave 3) + 30 (waves 1–2, REVIEW_data_quality_wave1.md / REVIEW_scientific.md) | docs/HEP_ATLAS_COVERAGE.md "Independent verification by workstream" |
| factual_corrections_from_qa_P0 | 14 | VERIFY_*.md finding tables: dm-noble 1, dm-cryogenic 2, fixed-target 3, neutrino-mass 5, reactor-solar 3 |
| factual_corrections_from_qa_P1 | 51 | VERIFY_*.md finding tables (sum of P1 rows across the 15 reports), plus two orchestrator class fixes: 28 collapsed histories split, 11 sites relabelled campus under A23 |
| firefox_manual_run | not yet run | not yet run |
| flagships_fully_reviewed | 19 of 19 | ATLAS, CMS, DUNE, Super-K, T2K: REVIEW_scientific.md + REVIEW_data_quality_wave1.md; Hyper-K, NOvA, IceCube, Belle II, LZ: REVIEW_data_quality_wave1.md / REVIEW_scientific.md + flagship-depth.md orchestrator check; ALICE, LHCb: VERIFY_colliders-lhc.md; KM3NeT: VERIFY_astro-neutrino.md; JUNO: VERIFY_reactor-solar-neutrino.md; XENONnT: VERIFY_dm-noble-liquid.md; Muon g-2, Mu2e: VERIFY_muons.md; NA62: VERIFY_fixed-target.md; COHERENT: VERIFY_cevns.md |
| independent_verification_workstreams_wave3 | 15 | docs/atlas-worklog/VERIFY_*.md — 13 by separate Sonnet agents; muons and cosmic-gamma by the orchestrator after their verifiers were stopped by the user |
| nested_subagents_spawned_by_leads | 7 | Reported in lead worklogs: facilities (BNL), colliders-lhc (ALICE), astro-neutrino (KM3NeT, ANTARES+Baikal-GVD, radio detectors), dm-noble-liquid (DEAP-3600), fixed-target (NA62+NA48); the 20-agent cap blocked the rest. |
| qa_P2_remaining_documented | 28 | VERIFY_*.md P2 rows left as documented judgement calls; INTEGRATION_ISSUES.md rows 52–53 |
| research_workstreams_wave3 | 16 | docs/atlas-worklog/<owner>.md for the 15 experiment domains and facilities, plus flagship-depth.md |
| safari_manual_run | not yet run | not yet run |
| source_conflict_count | 106 | Rows in the "Conflicts" tables of the research worklogs (docs/atlas-worklog/*.md, counted by script on 2026-09-18) |
| subagent_count_total | not yet run | not yet run |
| subagents_spawned_by_orchestrator | 37 | Agent tool calls in the v1.0 session: W1, W3, W4; 16 wave-3 leads (15 domains + facilities); 15 domain verifiers; flagship-depth; flagship-membership and coverage red team (both stopped by the user before producing output). All Sonnet. |

<!-- counts:end -->

