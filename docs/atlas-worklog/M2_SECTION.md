# M2 stream: the view framework and "Beam through the Earth"

Branch `atlas-m2-section`, 2026-10-26. Working title of the view: **Beam through the Earth** (the owner names features; the one place the title is written is `WORKING_TITLE` in `static/atlas/js/views/beam-rows.js`).

## What was built

| file | role |
|---|---|
| `static/atlas/js/state.js` | `view` added to `TYPE_PREFIX`: `#/view/<name>/<arg>` is an ordinary route (Back/Forward, pasted links, `?y=`) |
| `static/atlas/js/views/registry.js` | the table of views, `name -> { title, load: () => import(...), parent?, searchEntries? }`; the contract is documented at its top |
| `static/atlas/js/views/host.js` | the full-stage frame: heading, back control, "Inputs and method" disclosure, status line, loading and error states; loads a view's module only when its route opens |
| `static/atlas/js/views/beam-geometry.js` | the arithmetic (haversine, chord, dip, sagitta, light time, uncertainty), no DOM |
| `static/atlas/js/views/beam-rows.js` | which baseline rows are drawable, route arguments, status at a year, sourced off-axis angles, search entries; no DOM, so panels and tests use it without the view |
| `static/atlas/js/views/beam-section.js` | the view itself (SVG section, true-scale Earth, true-size dip, off-axis schematic, tables, sourced-baseline comparison, method) |
| `static/atlas/views.css` | the framework's and the view's styles (linked once in `index.html`) |
| `static/atlas/js/app.js`, `phone.js`, `panels.js` | route wiring (`is-view-route`, like `is-map-route`), the phone header, the links from beamline and experiment panels, view rows in the search box |

A later view is one module plus one line in `VIEWS`. Nothing of a view loads until its route is opened (checked in `tests/browser_atlas.cjs`).

## Computed values (spherical Earth, R = 6371.0 km, coordinates as recorded)

All seven baseline rows. `c` is the chord, `s` the surface distance, "dip" the angle below the local horizontal at the source (= Δσ/2), "deepest" the depth at mid-chord (sagitta), `t` the light travel time along the chord, `V` the vertical stretch the zoomed panel states, "Δ vs sourced" is chord minus the sourced baseline.

| route argument | from -> to | sourced | s (km) | c (km) | dip | deepest (km) | t (ms) | V | Δ vs sourced |
|---|---|---|---|---|---|---|---|---|---|
| `lbnf` | Fermilab -> SURF (DUNE) | 1285 km | 1287.63 | 1285.44 | 5.790° | 32.50 | 4.288 | ×20 | +0.44 km |
| `numi` | Fermilab -> Soudan (MINOS) | 735.3 km | 735.36 | 734.96 | 3.307° | 10.61 | 2.452 | ×20 | −0.34 km |
| `numi~1` | Fermilab -> Ash River (NOvA) | ~810 km | 811.67 | 811.12 | 3.650° | 12.92 | 2.706 | ×20 | +1.12 km |
| `j-parc-neutrino` | J-PARC -> Super-K (T2K) | 295.3352 km | 294.20 | 294.18 | 1.323° | 1.70 | 0.981 | ×50 | −1.16 km |
| `j-parc-neutrino~1` | J-PARC -> Hyper-K (T2HK) | about 295 km | 294.24 | 294.22 | 1.323° | 1.70 | 0.981 | ×50 | −0.78 km |
| `kek-neutrino` | KEK -> Super-K (K2K) | 250 km | 249.56 | 249.54 | 1.122° | 1.22 | 0.832 | ×50 | −0.46 km |
| `cngs` | CERN -> LNGS (OPERA) | 732 km | 731.26 | 730.86 | 3.288° | 10.49 | 2.438 | ×20 | −1.14 km |

Check values in the brief: DUNE 5.8° and ≈32 km (5.79°, 32.5 km); NuMI -> Soudan 3.3° and ≈10.6 km (3.31°, 10.61 km); T2K ≈1.33° and ≈1.7 km (1.32°, 1.70 km). The T2K dip is 1.323° from the two coordinates (294.2 km), 1.327° from the nominal 295 km and 1.328° from the surveyed 295.34 km: the 0.3 % is the difference between the great-circle distance of the two recorded points and the surveyed target-to-detector distance, not a different formula.

Every computed chord agrees with its sourced baseline within the Earth-radius spread plus the two sites' recorded coordinate precision (the view tests this per row and says so; `tests/test_atlas_beam_section.py` asserts 0.5 %). The sourced baselines sit closer to the chord than to the surface distance (DUNE: 1285 against 1285.4 and 1287.6), which is why the comparison is drawn against the chord.

## Decisions worth knowing

* **Uncertainty is two stated parts, never one hidden bar.** Radius: the same Δσ at R = 6357 and 6378 km (the dip and central angle contain no R; for them the sphere is the approximation, stated in the method). Coordinates: Δσ ± (p₁ + p₂)/R, the two recorded precisions added linearly (a worst case). The tiles show the sum labelled "worst case"; the table shows both parts.
* **The vertical stretch is chosen per beam**, the largest of 5, 10, 20, 50, 100, 200 for which the section (deepest point plus deepest recorded detector) stands no taller than 0.55 of the chord; it is written in the figure ("vertical ×20" for the four ~700 to 1300 km beams, ×50 for the three ~250 to 295 km ones). The true-scale Earth and the dip at true size are drawn unstretched beside it.
* **Depth is overburden, not depth below sea level.** The record's `depth` (Super-K 1000 m of rock, DUNE 1478 m) is drawn below the site in the zoomed panel and not included in the computed chord; the method says what including it would change (about d/c: +0.07° for DUNE, +0.19° for T2K). Sites that record no depth say so in the figure.
* **Status follows the globe.** A row's own status wins over its beamline's, and the beamline's follows the selected year, so LBNF and T2HK are drawn dashed and labelled "under construction" (as the globe's arcs are), NuMI "shut down" and CNGS/K2K "completed" are drawn solid and still, and only a running beam has the flow animation (off under reduced motion). A year before the beam existed reads "Not yet built in <year>".
* **Off-axis angles** are taken from the "Off-axis angle" key specification of the experiment housed at the row's far end (T2K at Super-K 2.5°, Hyper-Kamiokande at Tochibora 2.5°, NOvA 14.6 mrad = 0.84°), never from the beamline's spec, because NuMI's spec belongs to NOvA's detectors only (MINOS sits on axis, so the Soudan row draws none). The schematic says "NOT TO SCALE"; the source is cited under it.
* **Citations load after the first paint.** `provenance.json` and `sources.json` (4.4 MB together) are fetched by the view itself, not by the panels, so the figure and numbers render from `atlas.json` alone and the sourced baseline's quote, locator and sources fill in a moment later.
* **Search** gets one row per drawable baseline from the registry (`name`: "Beam through the Earth: Fermilab -> SURF"; aliases include "DUNE beam", "T2K beam", "NOvA beam"), so "beam through the earth" and "DUNE beam" put the view first. The build and `search.json` are untouched.
* **Back** returns to the last non-view route the page saw (the beamline, the experiment, the globe); with none (a pasted link) to the view's parent, the beamline record; Escape does the same.

## Checks

* `tests/test_atlas_beam_section.py`: an independent Python implementation of the formulas against the brief's check values; the browser modules run under Node on the freshly built `atlas.json` agree with it to nine figures; the route, registry and stylesheet are wired once and the view's module is imported only dynamically.
* `tests/browser_atlas.cjs`: the route renders for DUNE and the dip shows 5.8° within 0.1°, the SVGs carry title and description, the numbers are in a table, reduced motion draws no flow; entry points, Back/Forward/Escape, search, the year query and error states; lazy loading; the phone layout.
* `tests/browser_atlas_a11y.cjs`: axe, WCAG 2.1 A/AA, on the view with "Inputs and method" shut and open.

## For the integrator

* Rebuild the bundles at merge; this branch commits no generated files.
* `static/atlas/generated` was current at branch point (`bb673ea`), so nothing was regenerated.
* Unresolved: the Fermilab and CERN ends are campus-grade points (3 km and 0.5 km precision), so DUNE's and CNGS's coordinate terms are dominated by them; a surveyed target position would tighten both. NuMI's Ash River end is quoted to 0.1° (8 km), the largest coordinate term of the seven.
