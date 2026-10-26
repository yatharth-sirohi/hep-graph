# HEP Atlas — plan to a release-ready version

Branch `atlas-release` (from `main` 1a475e7, 2026-10-25). The goal: every
facility in the Atlas has a working to-scale local map, the globe works the way
a reader expects, and what the Atlas states is checked against its sources.
The release merges to `main` and is verified on production.

## Where it starts (measured 2026-10-25 against the live build)

* 48 facilities, 39 maps. Of the 39-facility coverage set: 18 layouts to
  scale, 15 partial (footprints or points only), 5 marker only (PSI, SNS,
  LANSCE, Boulby, South Pole), JUNO has no map. Nine further facilities have
  no map by definition. 41 entities sit in "unlocated" lists.
* Globe walkthrough at 1440×900 found: a 340 px empty column beside the globe
  whenever no record is open; the globe keeps auto-rotating after a search
  selection, so the selected facility drifts away; overlapping labels in
  dense regions (US West, Europe); no country outlines, so the land mass is
  hard to read; the facility a reader selected is not highlighted; a long,
  flat filter list (≈90 checkboxes) with raw labels such as "Cevns".
* Data: validator 0 errors; link check 1,485/1,486 at the last run
  (2026-09-21). Spot findings: missing accents ("Laboratorio Subterraneo de
  Canfranc").

## Standards (unchanged from the geometry contract)

Nothing is drawn without a fetched source; derived shapes say how they were
derived; what cannot be sourced stays in the unlocated list with a backlog.
"Every facility has a working scale map" therefore means: every facility
opens a map with a metre scale bar showing whatever its public sources
support at true scale, and states plainly what it does not show. It never
means inventing a shape to fill a gap.

## How the work is done

* Implementation and research by Sonnet subagents, each in its own worktree
  (`../HEP-Graph-ar-<stream>`) on its own branch, merged into
  `atlas-release` by the integrator.
* The integrator re-opens the sources behind every new principal shape
  (circumference, lengths, positions) and opens every changed map in a real
  browser before merging. Subagent claims are not taken on trust.
* Tests: only where a regression would be silent (a contract the build and the
  browser share). Release acceptance is a human-style walkthrough of the
  built product: open each map, count what is drawn, use search, panels,
  timeline and filters as a reader would, at desktop and phone widths.
* After every round, a workup in `docs/atlas-worklog/RELEASE_ROUND_NN.md`:
  what changed, how the experience improved, why it is better.

## Rounds

| Round | Theme | Contents |
| --- | --- | --- |
| 1 | Globe that behaves | Empty column removed, selection stops rotation and flies to the facility, selected marker highlighted, label decluttering, country outlines, label/name fixes. Research streams for maps start in parallel. |
| 2 | Arrays to scale | Instrument positions for IceCube, Auger, H.E.S.S., CTAO-South, LHAASO, Telescope Array, La Palma, HAWC, VERITAS, Baikal-GVD (published station/telescope coordinates). |
| 3 | Accelerators to scale | PSI (HIPA), SNS, LANSCE, CEBAF, Fermilab Main Injector/Recycler — upgrade partial and marker-only maps. |
| 4 | Underground and reactors | JUNO (new map), Chooz, Brokdorf, Leibstadt, Boulby, Soudan, Baksan. |
| 5 | The remaining nine | Argonne, ISIS, ILL, KIT (KATRIN), MIT, Yale Wright Lab, CENPA, McMurdo LDB, Summit Station — a sourced footprint map for each. |
| 6 | Facts checked | Machine check that every quote is in its fetched source and every number matches; facility records re-read against official pages; corrections applied. |
| 7 | Panels and browsing | Facility, experiment and result panels; filter list grouped and collapsed; results and documents views. |
| 8 | Phone and keyboard | Phone-width layout of globe, panels and maps; keyboard path through search, panel and map. |
| 9 | Coverage and methodology | Regenerated coverage report and About page that match what ships; load-time and bundle-size check. |
| 10 | Release | Full walkthrough of all maps and views on the built product, fixes, merge to `main`, production verified by commit hash and the same walkthrough on the live URL. |

Rounds may be reordered when a finding demands it; the workups record what
actually happened.
