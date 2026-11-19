# HEP Atlas improvement loop

> Execute in this chat, one independently testable improvement at a time.

**Goal:** Repeatedly inspect a learner journey, select a substantive learning or exploration gap, implement it, verify it, and use the outcome to select the next cycle. The user explicitly delegated choosing and implementing improvements.

**Architecture:** Extend the existing buildless Atlas views and tour patterns. Keep scientific calculations pure, controls keyboard-accessible, links restorable, and claims sourced. Preserve HEP Graph and the existing feature branch. No accounts, tracking, paid services, merge, or production deployment.

**Working branch:** `atlas-learning-questions`, starting this loop at `b2add215`.

## Iteration 1 — Predict and test energy doubling

Finding: the lab already has an energy slider, source-backed baselines and an explanatory formula, but no active experiment that challenges the assumption that more energy always means more conversion.

- [x] Add failing independent calculation tests for a near-first-maximum energy-doubling experiment, including control rounding and unsupported ranges.
- [x] Add a real-browser regression for hidden/revealed explanation, point movement, keyboard activation, share URL and reset after manual edits.
- [x] Implement a short in-place prediction disclosure in the existing beam lab; use the existing formula and chosen teaching parameters. This is an exercise inside the existing view, not another tour player.
- [x] Explain the ideal phase change π/2 → π/4 and report actual probabilities at the control’s supported 0.01 GeV energies.
- [x] Verify Chromium and 360px mobile WebKit, retain screenshots, commit the cycle, and record the next evidence-based improvement.

## Loop ledger

2026-11-19: inspected authoritative worktree. Clean at `b2add215`; earlier feature report and current lab/test code read. Continuing existing branch and constraints. No automation was scheduled: this is an active improvement loop in the current chat.


Iteration 1 verified: the two new independent calculation tests failed first because the experiment export did not exist; the browser test failed first on the missing prediction control. The implemented exercise passes all 10 learning unit tests, Chromium desktop/360px and WebKit desktop/360px tests, and the repository suite (803 passed, 139 skipped). Actual doubled-energy results are 49.42% for T2K and 50.04% for DUNE; feedback explains the ideal 50% and the supported control rounding. Manual edits and restored energies clear stale feedback. Screenshots: `/tmp/hep-atlas-iterations/`; verification logs: `/tmp/hep-iteration1-*.log`.

## Iteration 2 — Compare baselines at fixed L/E

Finding: the baseline selector currently holds energy fixed, so changing the distance also changes the oscillation phase. The formula explains L/E, but learners cannot use the existing selector for a controlled comparison.

- [x] Add failing independent tests for proportional energy matching, supported rounding, invalid inputs, and requests outside 0.2–8 GeV.
- [x] Add URL/state and browser regressions for the fixed-L/E preference, actual T2K ↔ DUNE switching, keyboard input, Back/reload, and an out-of-range request.
- [x] Add an optional checkbox alongside the existing baseline selector. Preserve the default fixed-energy behavior. When checked, scale energy with baseline; explain the phase invariance and 0.01 GeV rounding using the already sourced formula.
- [x] Refuse an unreachable match with a visible, accessible explanation instead of silently clamping energy or changing the requested comparison.
- [x] Verify Chromium and mobile WebKit, run relevant regressions, record the outcome, and commit the cycle.


Iteration 2 verification: the new matcher/state tests failed first on missing exports and state. The new comparison browser test failed first on its missing checkbox. Both engines then passed desktop and 360px prediction/comparison tests, including actual T2K↔DUNE switching, keyboard checkbox/energy input, Back/forward/reload and an unreachable match. The full question→lab→Higgs-paper phone journey passed again in Chromium and WebKit. Full repository checks before review fixes: 806 passed, 139 skipped.

Independent review identified three edge cases, reproduced in failing browser regressions before fixes: the accepted view/tour alias lost e/le during startup, hidden referenced error text remained in Chromium’s computed accessibility description, and rounding hid why a target just below 0.2 GeV was refused. All four focused edge checks now pass in both engines; 23 learning/tour-player tests pass. A second review found all findings resolved with no new actionable issues. Final post-review repository verification: 807 passed, 139 skipped. Both engines also pass the final desktop/360px experiment suite. Cycle ready to commit.

## Iteration 3 — Turn evidence reading into the next question

Finding: both Higgs evidence trails explain the measurements and link to the papers, but the existing sourced mass-compatibility exercise (Higgs hunt, step 7) is not discoverable from those Results. Connecting it gives a learner a next action using what they just read, without duplicating the tour or inventing a second exercise.

- [ ] Test that both curated evidence entries target the existing step and that the target still contains both experiments’ measurements, the independent-error approximation and sourced working.
- [ ] Add a failing browser regression for evidence→question, keyboard reveal, worked answer, copied/deep links and Back on desktop Chromium and 360px WebKit.
- [ ] Add an optional next-question slot to the reusable evidence display. Keep its topic-specific content in the reviewed registry; reuse the panel’s existing tour-step navigation.
- [ ] Verify both pilots and optional/missing data, check the separate HEP Graph entry point, record results, and commit this cycle.
