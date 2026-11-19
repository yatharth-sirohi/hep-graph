# HEP Atlas iterative learning improvements — 19 November 2026

The user asked for an active inspect→choose→implement→verify loop. Work continues on the existing `atlas-learning-questions` branch, starting this loop at `b2add215`. No automation, production deployment, merge, tracking, account or paid service was added. The original [connected learning report](LEARNING_2026-11-19.md) retains the baseline/source audit and existing data and comprehensive-suite limits.

## Cycle 1: predict and test energy doubling

Committed as `00dca966`. The beam lab now offers an in-place prediction experiment near its first maximum. A keyboard-accessible button moves the actual curve marker to doubled energy and reveals why the phase halves. It reports the actual supported control values: T2K 0.60→1.20 GeV gives 49.42%; DUNE 2.59→5.18 GeV gives 50.04%. It distinguishes those rounded results from the ideal 100%→50% calculation. Manual edits or restored energy clear stale feedback.

Verification: tests failed before implementation; 10 learning unit tests passed afterward. Chromium and WebKit passed desktop and 360px predict/reveal, marker movement, energy URLs, keyboard focus and feedback reset checks. Full repository suite: 803 passed, 139 skipped.

## Cycle 2: compare at the same L/E

The existing baseline selector gains an optional “Keep L/E” checkbox. It scales energy with distance before rounding to the lab’s 0.01 GeV increment, making a controlled T2K/DUNE comparison possible. Default behavior still holds energy fixed. A match outside 0.2–8 GeV is refused with an accessible explanation, and the original setup stays selected. The checkbox is restored by `le=1` in beam-view and beam-tour URLs; it is cleared when leaving that scope.

The calculation follows the lab’s existing cited two-flavor vacuum formula with fixed teaching parameters. Equal L/E gives equal phase and conversion probability in that model; rounding is explicit. It remains an illustrative teaching model, not a DUNE prediction, event-rate calculation or substitute for three-flavor matter effects.

The final review found and resolved alias-state loss, obsolete hidden text in the computed accessible description, and a misleading rounded boundary refusal. Both engines pass four focused review regressions; 23 calculation/navigation/tour-player tests pass. Both engines also pass the desktop/360px comparison tests and the complete phone question→lab→result→primary-paper journey. Final post-review repository verification: **807 passed, 139 skipped**. The independent review confirmed all findings resolved.

## Local routes and sources

Use the current local server at `http://127.0.0.1:8876` while the loop is running. From the feature checkout, restart it with the repository environment’s `python -m hepgraph.server --port 8876` when needed.

- T2K experiment and prediction: <http://127.0.0.1:8876/atlas?e=0.6#/view/beam-section/j-parc-neutrino>
- T2K ready to compare at fixed L/E: <http://127.0.0.1:8876/atlas?e=0.6&le=1#/view/beam-section/j-parc-neutrino>
- Corresponding DUNE setup at supported energy: <http://127.0.0.1:8876/atlas?e=2.61&le=1#/view/beam-section/lbnf>
- Beam question with comparison enabled: <http://127.0.0.1:8876/atlas?step=5&e=2.5&le=1#/tour/neutrino-beams-through-the-earth>
- ATLAS evidence: <http://127.0.0.1:8876/atlas#/result/atlas-higgs-observation-2012>
- CMS evidence: <http://127.0.0.1:8876/atlas#/result/cms-higgs-boson-observation-2012>
- Existing sourced mass-compatibility question: <http://127.0.0.1:8876/atlas?step=7#/tour/higgs-hunt>
- Separate HEP Graph coauthorship search: <http://127.0.0.1:8876/>

No scientific source values were changed in these cycles. Sources remain the [T2K experiment paper, §3.6.1](https://arxiv.org/pdf/1106.1238v2#page=10), [DUNE baseline passage, §1](https://arxiv.org/pdf/2007.06722v4#page=12), [T2K two-flavor formula and units](https://t2k-experiment.org/neutrinos/beyond-the-standard-model/), [PDG mixing review](https://pdg.lbl.gov/2024/reviews/rpp2024-rev-neutrino-mixing.pdf), and the versioned [ATLAS](https://arxiv.org/pdf/1207.7214v1) and [CMS](https://arxiv.org/pdf/1207.7235v1) papers. The previous report records exact figures and passages. Claims about phase changes and matching L/E are derived from the displayed formula.

Logs and screenshots for this loop are retained locally under `/tmp/hep-atlas-iterations/` and `/tmp/hep-iteration*.log`; final review artifacts will also be copied to the ignored `test-results/atlas-iterations/` directory. Screen-reader hardware and physical phones have not been tested. Existing database-environment skips, aging-data validation findings and legacy monolithic-browser timing limits remain as documented in the original report.
