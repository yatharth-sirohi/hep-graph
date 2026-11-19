# HEP Atlas connected learning implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Complete the three learning improvements in the user request, preserving HEP Graph and existing Atlas routes, data and tours.

**Architecture:** Reuse targeted steps of the six existing tours for the three question entry points and their sourced checkpoints. Mount an accessible SVG oscillation lab inside the existing beam section, using recorded (not coordinate-derived) baseline lengths. Add a reusable, optional evidence display to Results, populated only for the ATLAS and CMS 2012 entries.

**Tech Stack:** Existing Python server and validators, buildless JavaScript modules, CSS/SVG, pytest/Node and Playwright.

**Spec:** User request; docs/HEP_ATLAS_TEACHING_PLAN.md and docs/HEP_ATLAS_UX_PLAN.md.

## Global constraints

- Start from verified current main, preserve all existing records and the HEP Graph coauthorship application.
- No accounts, tracking, paid services, production deployment or merge.
- Two-flavor vacuum teaching model only; explicitly exclude event rates, DUNE predictions and three-flavor matter effects.
- Keep observed and expected significance separate, identify local versus global and never combine ATLAS and CMS significance.
- Test Chromium and mobile WebKit at 360px, keyboard, Back and pasted links.

## Review focus

- Invalid/nonfinite energy URLs must not produce NaN, empty charts or invalid controls.
- Range adjustments must retain focus and restore from shared links and Back.
- Tour UI must leave the visual and lab usable at 360px.
- Paper page locators must refer to explicit versions; ATLAS 6.0/4.9 table values must not be confused with final 5.9/4.9 text values.
- Uncurated results must retain their normal display without manufactured evidence.

### Task 1: Oscillation calculation, state and beam interaction

Files: create static/atlas/js/views/oscillation-model.js and oscillation-lab.js; modify views/beam-section.js, views/host.js, state.js and views.css; create tests/test_atlas_learning.py.

Interfaces: oscillationProbability(Lkm,EGeV,parameters), firstMaximumEnergy(Lkm,parameters), normaliseEnergy(value); lab consumes resolved beam row and context; energy URL parameter e, scoped to beam view and beam tour.

- [ ] Write and run calculation and URL regression tests, observe failure.
- [ ] Implement calculation (1.267, delta m squared 0.0025 eV squared, theta 45 degrees), valid 0.2–8 GeV input, live selected circle and dashed maximum/diamond on labeled SVG, numeric alternative, baseline selector using sourced records, method and sources.
- [ ] Run regression tests and verify keyboard/URL behavior.

### Task 2: Question-first tour entries

Files: modify static/atlas/index.html, existing three data/atlas/tours/*.json and tour player only as needed; regenerate bundles.

- [ ] Add browser regression that opens each exact question, checks its view and prediction reveal.
- [ ] Link to beam tour step 5, underground tour step 6 with chart, Higgs tour step 6 with Results story; add concise visual instructions and sourced checkpoints. Reuse player, no second system.
- [ ] Regenerate bundles, run validator and tour tests.

### Task 3: Optional readable evidence trail

Files: create static/atlas/js/result-evidence-data.js and result-evidence.js; modify panels.js and atlas.css.

- [ ] Write failing tests for two evidence records and absence elsewhere.
- [ ] Add measurement, distinct observed/expected local significance, meaning and exact versioned figure/passage links. Link to companion result; no cross-experiment significance.
- [ ] Run tests, primary-source check, validator and bundle check.

### Task 4: Full journey and reviewable delivery

Files: create tests/browser_atlas_learning.cjs and docs/atlas-worklog/LEARNING_2026-11-19.md.

- [ ] Chromium and 360px mobile WebKit: question, reveal, keyboard energy change, explain, baseline change, shared URL, Back, Results evidence and primary paper navigation.
- [ ] Run relevant existing Atlas browser suites and full pytest; verify HEP Graph search configuration/behavior and routes.
- [ ] Review changes, commit feature branch, report exact local routes, sources, passing checks and any remaining limits. Do not merge/deploy.

## Progress

Main verified over GitHub fetch on 2026-11-19: 19e7ed9067ea7d69ab3b5a01b7bd70d97cef22f8; no open PRs; prior atlas-ux clean at same commit. Reused that isolated worktree on new atlas-learning-questions branch. Main checkout has unrelated untracked .claude/launch.json, preserved. The managed-worktree tool did not return; canceled that request and verified Git still lists only the two original checkouts. Reused the clean Atlas checkout; no duplicate worktree was created.

Verification notes: Initial regression tests failed before implementation. Focused calculation/navigation/evidence/tour tests now pass. Chromium desktop and 360px mobile journey pass, including real versioned arXiv PDF navigation and HTTP 200. Existing HEP Graph browser regression passes. The full suite found an old trailing-slash assumption in the tour-player test; updated it to the existing no-argument view URL pattern. A November-dated validator reports five status mismatches also reproduced on unchanged main; the October 29 data snapshot validates with zero errors. Bundle regeneration preserves that data verification date rather than implying a new survey of records.

Final review fixes: normalized off-step energy to the supported 0.01 GeV grid; strengthened the browser test to switch DUNE → T2K → Back with physical numbers; moved all Higgs-specific prose and definitions into the two pilot data objects and tested generic rendering with a synthetic object; restored the entire prior underground exercise under a validated Go deeper disclosure; pinned DUNE’s PDF to the verified v4. All review findings were addressed. A separately reproduced delayed horizontal-scroll event closed phone result cards; recording the scroll position when opening the card fixes the real chart→result journey.

Verification: 33 focused tests; full Python suite 801 passed / 139 skipped; full connected journey Chromium and WebKit desktop and 360px passed; final compact phone-control check passed in both engines; new lab/evidence axe check 0 WCAG A/AA violations; snapshot validator 0 errors and build check 84 matching files. Comprehensive legacy browser suite is still running.
