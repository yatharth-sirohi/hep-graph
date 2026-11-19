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

- [x] Test that both curated evidence entries target the existing step and that the target still contains both experiments’ measurements, the independent-error approximation and sourced working.
- [x] Add a failing browser regression for evidence→question, keyboard reveal, worked answer, copied/deep links and Back on desktop Chromium and 360px WebKit.
- [x] Add an optional next-question slot to the reusable evidence display. Keep its topic-specific content in the reviewed registry; reuse the panel’s existing tour-step navigation.
- [x] Verify both pilots and optional/missing data, check the separate HEP Graph entry point, record results, and commit this cycle.


Iteration 3 verified: the new registry test failed on its missing destination, and the browser test failed on the missing evidence→question link. Both pilots now reach the existing sourced step 7, reveal its independent-error calculation by keyboard, and restore the result with Back. The optional generic renderer remains free of pilot-specific assumptions. Extracted topic-tour links use the same helper. Review found native links dropping data/embed/theme and then retaining a stale theme after a later toggle; both cases received failing-before/passing-after browser checks, including opening the actual copied href. The final review found no remaining blockers.

Final iteration 3 verification: full repository suite 808 passed, 139 skipped; focused learning/evidence/tour-player suite 24 passed; Chromium and WebKit each passed desktop and 360px evidence→question, keyboard, working, Back, native/copied links, theme changes, embed/data preservation and optional-data checks. Separate HEP Graph browser regression passed (mocked API boundary; no production writes). Preserved-snapshot validation: 0 errors, 1892 existing warnings, 4 informational; 84 generated files match. No scientific source values changed.

## Iteration 4 — Investigate cold-page navigation lifecycle

Finding from the iteration 3 browser run: very rapid cross-document navigation can let deferred globe scenery fetches begin while WebKit is leaving the document, producing access-control errors. The identical focused sequence reproduced six errors on unchanged main and six on the feature branch. `globe.js` and `loader.js` match main. Trace points to the first-frame timeout calling `loadEarthTexture()` / `loadBorders()` after navigation has started. This is a separate existing lifecycle issue, not a failed probability or lesson-link assertion.

The native-link learner test waits for startup requests to settle before moving between documents and retains a strict zero-page-error assertion. Its final run passes both engines and sizes. At the end of iteration 3, the rapid-unload stress case was recorded for cycle 4; no errors were filtered from the test.

- [x] Turn the main/feature reproducer into a focused regression and trace the document lifecycle boundary.
- [x] Implement an Atlas-only fix for work scheduled on a departing document, preserving normal cold loads and restored history pages.
- [x] Verify rapid navigation plus Back/forward restoration in Chromium and WebKit, and rerun the relevant learning journey.
- [x] Review, record and commit the cycle before choosing the next learning improvement.


Iteration 4 outcome: a lifecycle trace proved both scenery requests were being created after `beforeunload`, before `pagehide`, while the document was still reported visible. The focused regression failed before implementation. Requests now start directly in globe `ready()`; decoding/application remain asynchronous, existing once-only guards and fallbacks remain, and no unload listeners were added. The old first-paint comments were corrected. Independent review found no correctness, fallback or history blockers.

Final verification: Chromium and WebKit 360px both pass four rapid cold-page exit cycles with zero browser errors, normal scenery requests, real Back/forward recovery of energy and fixed-L/E state, and a slow-assets case. That case holds both optional requests, checks the base canvas is visible, opens the real beam question and changes energy by keyboard before releasing either request. It does not measure first-frame timing or prove a persisted browser-cache hit. The full connected mobile question→lab→primary-paper journey passes again in both engines. Repository suite: 808 passed, 139 skipped. Logs: `/tmp/hep-iteration4-*.log` and ignored `test-results/atlas-iterations/`.

## Iteration 5 — Track both flavors in the teaching model

Finding: the lab plots and announces conversion, while original-flavor survival appears only in the formula disclosure. A newcomer answering why beams traverse Earth can confuse loss of the starting flavor with absorption. The existing two-flavor formula already determines both outcomes; no new experimental prediction is needed.

The T2K explanation was checked again on 19 November: its “Atmospheric Neutrino Anomaly” passage distinguishes the observed flavor deficit from absorption at those energies, and “The Resolution — Neutrino Oscillations” supplies the two-flavor conversion formula. Source: <https://t2k-experiment.org/neutrinos/beyond-the-standard-model/>. Survival = 1 − conversion follows from the closed two-flavor teaching model.

- [x] Add meaningful calculation regressions at no mixing, a first maximum, and half-phase, with probabilities bounded and summing to one.
- [x] Add an optional in-place “Track both flavors” disclosure under the current chart: original-flavor and converted-flavor probabilities, text labels and a non-color visual that follows the existing energy control.
- [x] Keep the two generic flavors explicit; distinguish flavor survival from absorption and detector event counts. Reuse the current formula/source and model limitations, without adding another tour or URL control.
- [x] Verify keyboard disclosure/energy changes, first-maximum and doubling actions, fixed-L/E switching, 360px layout and restored URLs in Chromium/WebKit; review and record the cycle.


Iteration 5 outcome: the existing energy control now drives a native “Track both flavors” disclosure below the curve. It shows original-flavor survival and conversion as a solid/striped balance with text percentages and an explicit selected-energy/sourced-baseline caption. The closed two-flavor model, no absorption/detector response, generic flavors and distinction from detected-event fractions/rates are stated. No new tour, URL field or model parameter was added. The range’s accessible value contains both outcomes; the new definition list is not another live region.

The calculation and browser tests failed first for the missing helper/disclosure. Final verification: 15 focused learning tests pass; 809 repository tests pass, 139 skip. Chromium and WebKit pass desktop and 360px values, keyboard, first maximum, doubling, fixed-L/E switching, caption updates, reload/Back and phone beam-tour energy controls without advancing the step. Both engines pass the full connected mobile question→lab→primary-paper journey again. Scoped axe WCAG A/AA checks on the expanded lab find zero violations in standard and projector themes at 360px. Independent review found no actionable issue, confirmed the primary source and swept all 1,562 T2K/DUNE control-energy pairs for bounds, complement and display rounding. Actual screen-reader speech/timing was not measured.

## Iteration 6 — Take the oscillation lab to a lesson

Finding: `beam-section.js` registers an export containing only the zoomed Earth section and whole-Earth diagram (`host.setExporter`, around line 624). The selected oscillation curve and two-flavor balance are omitted. An instructor can share the live energy URL but cannot save the worked model visual with the current Export image flow. The teaching plan explicitly asks for reusable, sourced classroom figures.

- [ ] Inspect the existing host/export interfaces and reproduce what the beam view currently saves.
- [ ] Add a way to export the selected oscillation lab through the existing image-export machinery, while preserving the existing beam-geometry export.
- [ ] Carry the actual selected energy, sourced baseline, formula/units/chosen parameters, teaching-model qualification and citations into the saved figure; avoid implying an event prediction or measured uncertainty.
- [ ] Verify keyboard/mobile controls, current-state capture and downloaded artifact legibility in Chromium/WebKit, including updated energy and baseline selection; review, record and commit the cycle.
