# Release round 6 — three browser engines, maps that open on the machines, and an independent review

Integration branch `atlas-release`, 2026-10-25.

## What changed

**Firefox and Safari's engine.** Until now every browser check ran in Chromium.
Playwright's Firefox and WebKit were installed and the full browser suite run in
each. It found one real bug:

* *Search lost the list in Firefox and WebKit.* After opening a result from
  search, going back to the box and typing a new query produced a list that shut
  itself 40 ms later — a 120 ms "close on blur" timer from leaving the box
  survived the return. Focusing the box now cancels it.

The other cross-engine failures were in the tests, not the Atlas (Firefox has no
mobile emulation flag; WebKit on macOS does not focus a button on click), and
were fixed in the tests. Result: Chrome 79/79, Firefox 78/78, WebKit 78/78.

**Maps open on the machines, not the fence.** A campus boundary is context:
Fermilab's is 7 km across, and framing it left the rings a small knot in the
middle. Framing now uses the structures whenever there are any; Fermilab opens on
the Linac, Booster, Main Injector/Recycler and the NuMI line, labelled.

**Coverage report regenerated.** `docs/HEP_ATLAS_COVERAGE.md` now reports every
facility with a local map, the count of surveyed / georeferenced / derived
features per map, and 0 failed checks across all maps.

**An independent review.** A Sonnet reviewer who had not built the Atlas used it
as five kinds of reader (PhD student, theorist, journalist on a phone, a
physicist checking sources, an explorer) and reported 22 findings. The P0 was
fixed at once:

* *T2K's CP-violation result overstated its exclusion.* The record said
  CP-conserving values "(0, ±π) excluded at 3σ"; the cited abstract's
  normal-ordering 3σ interval [−3.41, −0.03] contains −π, so only δCP = 0 is
  excluded there. The key value, significance, summaries and why-it-matters now
  say exactly what the intervals support, in the collaboration's words ("an
  indication of CP violation").

The remaining findings are being fixed by three parallel streams (round 7):
topic highlighting and Results filters in the URL, search that finds "Higgs
discovery", detector lists on experiment panels, honest "drawn on the map"
wording for far detectors, phone layouts of the Results filters and the About
page, readable Sources (locators, no JSON pointers), the unlocated lists written
for readers rather than researchers, and an audit of every result's paraphrased
fields against its quotes.

## How the experience improved, and why it is better

* Firefox and Safari users can search the way Chrome users could.
* Opening Fermilab shows the accelerators first — what a visitor came to see.
* The most consequential kind of error — a headline physics claim stronger than
  the paper's — was caught by a reviewer reading as a theorist would, and
  corrected; the next round audits every result for the same pattern.

## Verified, and how

* Integrator traced the Firefox search failure (list rendered with 18 results,
  closed 44 ms later with focus still in the box) and confirmed the fix in
  Firefox, Chrome and WebKit.
* Integrator re-read arXiv:1910.03887's abstract for the T2K intervals and the
  "indication of CP violation" wording.
* Full browser suite on three engines (above); validator 0 errors; coverage
  report regenerated with `scripts/atlas_coverage_report.py`.

## Not done yet

* "Report an error" links to the GitHub repository, which is private: public
  readers get a 404. This needs the owner's decision (a public issue form, an
  e-mail address, or a public repository).
