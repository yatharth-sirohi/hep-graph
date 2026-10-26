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

A first version drew each machine once, at its first operating year and its latest operating energy (the Tevatron at 1.96 TeV in 1985, the LHC at 13.6 TeV in 2010). That is wrong physics for a Livingston chart and was replaced by the rules below.

* **Eligible:** a machine with a dated start of operation (the start of its first `active` interval; a planned date is not a start) and an energy: an era's own value, or the headline value.
* **Field:** `is_collider` -> `specs.cms_energy` (√s, filled marker); otherwise `specs.beam_energy` (hollow). The two are different quantities and the chart says so; it never derives √s from beam energies (KEKB records only per-ring beam energies and is listed as not plotted).
* **One point per era:** an era is an interval of status `active` (kind `run`, `phase` or none) whose own `specs` carry the field (A3, A30). Its point stands at that interval's start year; the points of a machine are joined by a thin line in its colour. The first point is the first operation.
* **Energy as recorded today:** where no era dates an energy to the start, the headline `specs` value is drawn once at the first-operation year with a **dashed ring**, and the point, the legend and the table say "Energy as recorded today; the starting energy is not in the Atlas." The same point is added in front of a track whose first era starts after the first operation (RHIC). It is not joined to the track.
* **Headline value no era dates** (the LHC's 14 TeV design value, CEBAF's 12 GeV): footnoted (†), not drawn.
* **A range** (PSB's "0.8 to 1 GeV" era) has no single value and is not drawn.
* **Colour and shape:** the first particle the record lists: electrons/positrons, protons (also antiprotons and H⁻), ions (also deuterons and alphas).
* **Timeline:** points whose year is after the selected year (or after the end of a range) fade, with the line segment that ends at them; a machine's name fades when all its points have; a line stands at the year.
* **Sentence under the title** is computed: "The highest √s in the Atlas is the LHC's: 7 TeV (2010) → 13 TeV (2015) → 13.6 TeV (2022)."
* **Search:** `view` is first in `searchrank.js` TYPE_ORDER and the view carries the alias "energy frontier" (an exact match), so "energy frontier" and "going underground" lead to the views and not to the topic of the same name.

Checked on this branch's data (28 machines, 33 points, 24 of them dashed) and on a build of `atlas-next` (A30: 35 machines, 45 points, 29 dashed; the extra eras are AGS, FNAL Linac, FNAL Main Injector, J-PARC linac, KEK linac, PSB, SPS). A30's data is not on this branch; the code reads eras from any interval's `specs`, so it needs no change when it arrives.

## Notes for the data owners (not edited here)

* **Most machines are one dashed point.** Only the LHC (three runs), LEP (LEP1, LEP2), CEBAF (4 and 6 GeV) and RHIC (Run 22) carry dated energies on this branch. A dated starting energy would turn a dashed point into a true first point: the **Tevatron** (about 1.8 TeV in Run I, 1.96 TeV from Run II), **HERA**, **SLAC linac**, **SLC**, the **ISR**, **SPS**, **PS**, **KEKB/PEP-II**.
* **CEBAF:** the headline 12 GeV ("after the 2018 upgrade") is not on any interval; the 2018 upgrade interval carries no `specs`, so the track ends at 6 GeV (2000) with a footnote. Putting 12 GeV on that interval would add its point.
* **RHIC:** 200 GeV (Au+Au) is the headline and is drawn as recorded today at 2000; Run 22's 500 GeV (polarised p+p) is an era at 2021. The record has no Run 1 or 2001 energy.
* **KEKB** has no `cms_energy` (10.58 GeV); PIP-II has no active interval; HL-LHC has neither (LEAR has no energy on `atlas-next`).
* **PS and PSB** carry injection-energy eras (`injection_energy`, not plotted); PSB's 0.8 to 1 GeV extraction era is a range and is skipped.

## Start-here card

A fifth question ("How much does rock cut the cosmic-ray background?") was tried and **not kept**: with it the card scrolls at 1024×768 and 1280×720 and the three entries drop below the fold (without it only 1280×720 scrolls, by 10 px). It does not fit, so the entry points are the facility panels (underground laboratories), the accelerator panels and the search box.
