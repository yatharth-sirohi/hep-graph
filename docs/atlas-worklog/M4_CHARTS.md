# M4 stream: the chart toolkit, "Going underground" and "The energy frontier"

Branch `atlas-m4-charts`, 2026-10-26. Working titles (the owner names features): **Going underground** and **The energy frontier**, each written once, as `WORKING_TITLE` in `static/atlas/js/views/underground-rows.js` and `frontier-rows.js`. Routes `#/view/underground` and `#/view/energy-frontier`.

## What was built

| file | role |
|---|---|
| `static/atlas/js/views/chart.js` | the shared toolkit: linear and log scales and their ticks (`logTicks`, `linearTicks`, `powerOfTen`: 10⁻⁸ with superscripts), SVG axes, markers (circle, square, diamond, triangle; filled or hollow), labelled points that open their record, label placement (off each other and the markers, with leader lines; coincident markers labelled as a stack), a tooltip, a legend, `dataTable` (the same rows as an HTML table that becomes cards on a phone), a year marker, fading. Token colours (`ch-tone-*`, views.css) |
| `static/atlas/js/views/chart-inputs.js` | the "Inputs" list of a method: one disclosure per plotted record with the quote, locator, confidence, the record's own note and its sources; sources are fetched only when the disclosure is first opened |
| `underground-rows.js`, `underground.js` | which sites qualify, the A27 unit conversion (copied, see below), labels, search entry; the view |
| `frontier-rows.js`, `energy-frontier.js` | which accelerators qualify, the field, interval and energy each point uses, the reasons for the rest, search entry; the view |
| `registry.js` | two entries; nothing loads until a route opens |
| `panels.js` | a "See the physics" card on underground-laboratory facility panels and on every accelerator panel (a machine the chart cannot place says so); a "Cosmic-ray muon flux" row on the site panel (the chart opens that record and it did not show the flux) |
| `views.css` | `ch-*` classes and the `--chart-*` tones (each an existing atlas.css token) |
| `tests/test_atlas_charts.py` | the unit conversions and the log ticks only |
| `tests/browser_atlas.cjs`, `browser_atlas_a11y.cjs` | one check per view (renders, N points = eligible records, a click opens its record), entry points, a phone check, axe on both views (closed and with every input open) |

## Rules the charts follow

### Going underground

* **Eligible:** a site with a numeric `depth_mwe` and a numeric `muon_flux` (15 sites). x: depth in m.w.e., linear; y: flux in cm⁻² s⁻¹, log.
* **Units:** the bundle keeps each source's unit. `MUON_FLUX_SCALE` in `underground-rows.js` is a **copy** of `UNIT_SCALE['muon_flux']` in `hepgraph/atlas/schema.py` (`cm^-2 s^-1` 1, `m^-2 s^-1` 1e-4, `m^-2 d^-1` 1e-4/86400); the method says so and `test_the_copied_unit_scales_equal_the_schema` fails if they part. A flux in an unlisted unit is not plotted and is named under the chart.
* **Error bars:** drawn only from a numeric `min`/`max` around the value. No record carries one (the uncertainty is written in `display`), so none is drawn; the method says why. Prose is not parsed.
* **Hollow markers:** `approx: true` on the flux, or `confidence` `approximate`/`uncertain` in provenance (JUNO, a simulation; LNGS Hall B, a second-hand quotation). The chart waits for `provenance.json` before drawing so a marker never changes style after it appears.
* **Depth known, flux not recorded:** every site with a numeric `depth_mwe` and no `muon_flux` (5: SURF 4850 Level, Super-K, Hyper-K, Double Chooz far, Ash River). Sites with only a rock depth in metres are not listed: that depth is not on the axis.
* **Click:** a point (or its label) opens the *site* record, which is the measured thing; the table also links each laboratory.

### The energy frontier

* **Eligible:** a numeric energy in the field for the machine's kind and a dated start of operation: 28 of 31 accelerators.
* **Field:** `is_collider` → `specs.cms_energy` (√s, filled marker); otherwise `specs.beam_energy` (hollow). The two are different quantities and the chart says so; it never derives √s from beam energies (KEKB records only per-ring beam energies and is listed as not plotted).
* **Operating beats design:** where an `active` interval carries its own value of the field (A3, `Interval.specs`: the LHC's runs, LEP1/LEP2, CEBAF's 4 and 6 GeV, RHIC's Run 22), the latest such interval gives the energy and the headline `specs` value is footnoted (†) if it differs. Otherwise the record's stated value is drawn.
* **Year:** the start of the first `active` interval (a planned date is not a start). A machine is drawn once, at that year, even if it ran lower when it began.
* **Colour and shape:** the first particle the record lists: electrons/positrons, protons (also antiprotons and H⁻), ions (also deuterons and alphas).
* **Timeline:** machines that began after the selected year (or after the end of a range) fade, a line stands at the year, and the table rows fade.

## Notes for the data owners (not edited here)

* **CEBAF:** the record's headline `beam_energy` is 12 GeV ("after the 2018 upgrade") but the interval for the 2018 upgrade carries no `specs`, so the chart draws the latest *interval* energy, 6 GeV, and footnotes the 12 GeV. Putting 12 GeV on the 2018 interval would move the point.
* **RHIC:** drawn at 500 GeV (Run 22, polarised p+p), footnoting 200 GeV (Au+Au, the headline). A student expects 200 GeV at 2000; an Au+Au energy on an interval would settle which is "the" energy.
* **Tevatron** is drawn at 1.96 TeV from 1985; the record gives 1.96 TeV (Run II, 2002) as its one √s and carries no Run I energy.
* **KEKB** has no `cms_energy` (10.58 GeV); PIP-II has no active interval; HL-LHC has neither.
* Search: "energy frontier" returns the topic *Collider physics* before the view (type order in `searchrank.js` has no `view`); not changed here.

## Start-here card

A fifth question ("How much does rock cut the cosmic-ray background?") was tried and **not kept**: with it the card scrolls at 1024×768 and 1280×720 and the three entries drop below the fold (without it only 1280×720 scrolls, by 10 px). It does not fit, so the entry points are the facility panels (underground laboratories), the accelerator panels and the search box.
