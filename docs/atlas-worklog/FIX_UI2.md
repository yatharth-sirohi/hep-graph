# FIX_UI2: interface fixes after the independent review of the integrated M1-M6 build

Branch `atlas-fix-ui2` (worktree `HEP-Graph-ar-fix-ui2`), server on port 8876. Nothing under
`data/atlas/` was touched. `static/atlas/generated/` was rebuilt to run the checks and is not committed.

## What was done, by item

| # | Finding | Fix | Where |
|---|---------|-----|-------|
| 1 | Projector theme: dark ink on dark rock in the beam figure (1.1:1) | The projector theme now redefines the figure tokens: a pale rock (top `#d3e2ec`, bottom `#aec6d6`), a darker beam, surface line, overlay and plot curves. Standard rock-top lightened by one notch (`#214759`) so its muted captions pass 4.5:1 too. Presenter mode compacts the part above the beam figure so the whole figure sits above the timeline bar at 1920x1080. | `classroom.css`, `views.css` |
| 2 | Export image on a view | The view host exposes a view's figure (`host.setExporter`, or `svg[data-export-figure]`); `export.js` composites it (shapes as the browser's image of the live SVG, text from the page's fonts) under the title band, year, and a footer with the citation and the view's address. Works for the beam section (section + whole Earth), underground, energy frontier (chart + legend as SVG), limits (plot + legend), results-story (the lanes as an SVG made for the call), detector line-up (line-up + IceCube). A view with no figure (compare, person, an error, a view still loading) disables the button with its reason in the tooltip and `aria-describedby`. A figure much taller than a slide (the timeline) is 1920 px wide and as tall as it needs. | `export.js`, `exportpaint.js`, `views/host.js`, each view |
| 3 | Beam headline | "the line to the far detector leaves X 5.8° below the horizon ... and reaches the far detector, 1478 m underground at SURF" (the recorded depth; "~" when approximate; "(its depth is not recorded)" otherwise). Off-axis beams add that the line is not the beam axis. | `views/beam-section.js` |
| 4 | DAMA/LIBRA with no counterweight | A "Tested by" section on a result that states a claim (significance, or observation/evidence/anomaly): results of experiments with a `complementary` lineage row to its own, plus results by other experiments whose own text names it (name, alias, DAMA, LIBRA). Never its own experiment or collaboration, never a technology milestone; open by default; says it does not judge. | `tested-by.js`, `panels.js` |
| 5 | Search | Empty state says coverage is partial. A word matches at a word start (or across a typed-away hyphen), never from the middle of a word ("libra" is not "calibration"). A typed phrase is compared with names word for word with simple plurals folded ("neutrino oscillation" gives the topic first). | `search.js`, `searchrank.js` |
| 6 | BibTeX year | An entry citing only the arXiv preprint (no journal, no DOI) takes the year from the arXiv id, else the record's own non-publication date; never a `published` year it does not carry (LZ 2022). | `research/bibtex.js` |
| 7 | Presenter mode on map steps | Layers column hidden, the drawer waits to be asked for ("Open the record for X"), the map has ~1130 px of 1920. The first Escape leaves presenter mode. | `tours.css`, `tours.js`, `localmap.js` |
| 8 | "Over my location" hangs | With `?cmp=` and no `cmpc` the address already is what it would become, so `navigate` did nothing and nothing redrew. The overlay is now synced directly; the 20 s limit is our own timer and always ends the wait (the position option's timeout does not count the time spent asking). | `localmap-compare.js` |
| 9 | Phone tour map steps | The player (button, card, section) is not offered on a phone while touring (the stage is ~240 px). Outside a tour the card shades the edge it can still scroll to and may take 56% of the stage. | `proton.css` |
| 10 | Results story labels | Labels are measured in the page's face (not 6.4 px a character), keep 3 px clear of a mark, stop before the band's edges, and carry a halo so a gridline does not strike through them. | `views/results-story.js`, `views.css` |
| 11 | Escape on Start here | Focus goes to what opened the card, else what had it before, else the search box; never the body. The footer's Start here now shows the card on a map or a view (the route hid it). | `start.js`, `atlas.css`, `views.css` |
| 12 | Limits plot keyboard | Every point is focusable with an accessible name; one tab stop per series, arrow keys / Home / End move along it, Enter announces; the figure is a `group`. | `views/limits.js` |
| 13 | Compare "Baseline" | "not applicable" unless the kind is accelerator or reactor neutrino (a baseline that is recorded is always shown). Said in the table, the CSV and the method. | `views/compare-rows.js`, `compare.js` |
| 14 | Embed note | One line stays in the embed footer: "Coverage: partial", linking to the coverage report in a new tab. | `classroom.css`, `classroom.js` |
| 15 | Facility sheet | Proposed, planned and approved machines (CERN: FCC-ee, CLIC) are listed apart, each with its status; machines under construction say so. | `export.js` |
| 16 | Start-here beam link | Lands on `#/view/beam-section/j-parc-neutrino`; hint and test updated. | `index.html`, `tests/browser_atlas.cjs` |

Also: a result panel's heading is typeset (`$\Lambda$CDM` showed as source); two result records hold `{id}` objects in
`experiment_ids`, which killed the Results list sorted or grouped by experiment, so `modes.js` now reads them as ids.

## Checks

* `tests/browser_atlas_a11y.cjs` (chromium): 56 passed, 0 failed, **0 WCAG axe violations** over 67 states, including
  every view in projector mode (new: axe plus an in-figure text-contrast scan that resolves SVG paint, which axe cannot),
  the export dialog and the disabled button.
* `tests/browser_atlas.cjs` (chromium): see "pre-existing failures" below; new checks for items 2, 3 (via the Start link),
  5, 7, 8, 10, 11, 12, 15, 16 pass. WebKit and Firefox: the view export, presenter and location checks pass; the
  projector contrast scan is 0 below 4.5:1 on both for the beam, charts, plot and line-up.
* `tests/browser_atlas_classroom.cjs`: 8 passed (the projector 7:1 body text scan and the embed state).
* pytest: full suite green apart from what is skipped for want of a database; new unit tests in
  `test_atlas_search_and_tested_by.py`, `test_atlas_research_tools.py`, `test_atlas_static_css.py`.

## Pre-existing failures (they fail identically on `96be806`, checked by serving that commit on 8876)

For the integrator and the data stream; none comes from this branch:

1. `Every result panel leads ... no raw TeX`: the abstract quote of `result:agasa-spectrum-beyond-gzk-cutoff-1998`
   holds `10^{20}` outside `$...$` (and `act-dr6-power-spectra-lcdm-2025`'s name `$\Lambda$CDM`, which the panel heading now typesets).
2. `Globe clusters count and name only the facilities present in the selected year`: 1975 names Wilson Synchrotron Laboratory.
3. `Local map: back and forward restore the selection`: flaky on this machine (fails 6 of 6 on the base, 1 of 3 here).
4. `Both charts on a phone`: energy frontier labels overlap or leave the chart at 390 px.
5. `result:cdhs-total-cc-cross-sections-1987` and `result:neos-reno-joint-sterile-search-2022` have `{id: ...}` objects in `experiment_ids`.
6. The WIMP plot test still expected PandaX-4T's minimum at 30 GeV; the data say 40 (corrected in `7fb76d4`), so the test now says 40.

## For the integrator

* Rebuild the bundles at merge (`python -m hepgraph.atlas.build`); `static/atlas/generated/` is not in this branch.
* "Tested by" reads `complementary` lineage rows (26 experiments carry them) and the results' own text. If the data
  stream adds an explicit "tests this claim" relation, `tested-by.js` is the one place to read it.
* Unresolved: the map drawer carries two stacked close buttons (`#map-drawer-close` and the panel's `#close-detail`) at
  the same place; the visible one leaves the map. Not in this brief; left alone.
