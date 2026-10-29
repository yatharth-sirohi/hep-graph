# Follow-ups 3, limits B: six dark-matter limit results whose key value was an exposure

Date: 2026-10-29. Branch `atlas-next`. Model fix: `result:coupp-2kg-spin-dependent-limits-2008` (FIX_DATA2.md section 7).

## Scope

Six `result` records of `result_type: limit` had a `key_value` that was the exposure or live time of the
data set, not the limit the paper sets. For each I read the arXiv abstract page and the arXiv PDF (the
same source record in every case, so no new source files). Pages: `https://arxiv.org/abs/<id>` and
`https://arxiv.org/pdf/<id>`, both fetched 2026-10-29; "page N" is the PDF page. inspirehep.net and
Wikipedia were not used. No values come from memory.

Outcome: five records have no single-number limit in the paper (the limit is a plotted curve), so
`key_value` is now `null` and `key_value_text` quotes the exclusion statement, as coupp-2kg does. One
record (TEXONO ULEGe 2008) prints its limit in a table, so `key_value` is now a `cross_section`
quantity like cdex-1's. In every record the exposure or live time stays in `summary.technical`.
`verified_at` is `2026-10-29` on every new or changed sourced value.

## Table

| Record | Before (`key_value`) | After |
|---|---|---|
| `pico-2l-run2-2016` | exposure, "129 kg-days" | `key_value: null`; `key_value_text` "90% C.L. limits on the spin-dependent WIMP-proton and spin-independent WIMP-nucleon cross sections as functions of WIMP mass (Figs. 3 and 4)." |
| `pico-60-cf3i-2015` | time, "92.8 live days" | `key_value: null`; `key_value_text` "90% C.L. limits on the spin-independent WIMP-nucleon and spin-dependent WIMP-proton cross sections as functions of WIMP mass (Figs. 12 and 13)." |
| `texono-bosonic-dm-npcge-2019` | exposure, "314.15 kg days" | `key_value: null`; `key_value_text` "90% C.L. upper limits on the electron coupling g_aee of pseudoscalar bosonic super-WIMPs (Fig. 16) and on the vector-electric coupling alpha'/alpha of vector bosonic super-WIMPs (Fig. 17), as functions of mass in the sub-keV region." |
| `texono-pcge-wimp-limits-2013` | exposure, "39.5 kg-days" | `key_value: null`; `key_value_text` "90% confidence level exclusion plot of the spin-independent WIMP-nucleon cross section versus WIMP mass (Fig. 4)." |
| `texono-ulege-220ev-wimp-limits-2008` | exposure, "0.338 kg-day" | `key_value` cross_section, value 8.1e-40 cm^2, display "0.81 x 10^-39 cm^2" (SI WIMP-nucleon, 5 GeV, 90% CL) |
| `warp-first-physics-results-2007` | exposure, "about 100 kg x day" (approx) | `key_value: null`; `key_value_text` "90% C.L. spin-independent WIMP-nucleon upper limit as a function of WIMP mass, plotted in Fig. 8 (96.5 kg d, 55 keV threshold)." (replaces the earlier text "report a first upper limit ...", which moved into the note) |

## Quotes, URLs and locators

All quotes are copied from the PDF text layer. Where the PDF breaks a word at a line end ("WIMP-" / "proton"),
the quote joins it as the page reads.

### pico-2l-run2-2016

* URL: https://arxiv.org/abs/1601.03729 (PDF https://arxiv.org/pdf/1601.03729)
* Locator: Section VII (Results), page 4.
* Quote: "Limits at the 90% C.L. for the spin-dependent WIMP-proton and spin-independent WIMP-nucleon elastic scattering cross sections are calculated as a function of WIMP mass and are shown in Figs. 3 and 4."
* Fig. 3 caption (page 4) confirms the form: "The 90 % C.L. limit on the SD WIMP-proton cross section from Run-2 (Run-1 [8]) of PICO-2L is plotted in green (red)".
* Why no number: the abstract and the text give none; the limit is the curve of Fig. 3 (SD) and Fig. 4 (SI).
* Exposure kept: `summary.technical` already begins "129 kg-days at a 3.3 keV thermodynamic threshold". Abstract: "a total exposure of 129$\,$kg-days".

### pico-60-cf3i-2015

* URL: https://arxiv.org/abs/1510.07754 (PDF https://arxiv.org/pdf/1510.07754)
* Locator: Section VI (WIMP search results), page 9; figures 12 and 13 on page 10.
* Quote: "The resulting 90% C.L. limit plots for spin-independent WIMP-nucleon and spin-dependent WIMP-proton cross sections are presented in Figs. 12 and 13."
* Fig. 13 caption (page 10): "The 90% C.L. limit on the SD WIMP-proton cross section from PICO-60 is plotted in blue".
* Why no number: the abstract says only "Stringent limits on weakly interacting massive particles interacting via spin-dependent proton and spin-independent processes are set"; the text gives curves. (The only numbers near a limit, mu = 5.8 and 5.4 in the Section on the optimal-interval cuts, are limits on an expected event count, not on a cross section.)
* Exposure kept: `summary.technical` already has "92.8 analysed live days (3415 kg-days taken June 2013-May 2014)". Abstract: "an analyzed exposure of 92.8 livedays".

### texono-bosonic-dm-npcge-2019

* URL: https://arxiv.org/abs/1811.11415 (PDF https://arxiv.org/pdf/1811.11415)
* Locator: Section 6 (Experimental Constraints), page 17; Figs. 16 and 17 (page 17 and page 18).
* Quote: "The 90% C.L. exclusion limits for coupling of χps as a function of mχ are shown in Fig. 16, results from other representative experiments are also superimposed."
* Vector boson (quoted in the note): "The upper limits on the electronic coupling of χv at 90% C.L. are derived using the same data and analysis technique." Fig. 16 caption: "Constraints on gaee of χps as a function of mass." Fig. 17 y axis is log10[alpha'/alpha], with alpha' = (e kappa)^2/4pi the "vector-electric fine-structure constant" of Section 2.
* Why no number: the limits are two curves against boson mass; no coupling is stated at a stated mass in the abstract or text (the only gaee value in the text, 1e-10, is the example coupling of the Fig. 1 interaction-rate illustration, not a limit).
* Exposure kept: `summary.technical` already begins "314.15 kg d from an n-type point-contact germanium detector at Kuo-Sheng". Abstract: "using 314.15 kg days of data from $n$-type Point-Contact Germanium detector".

### texono-pcge-wimp-limits-2013

* URL: https://arxiv.org/abs/1303.0925 (PDF https://arxiv.org/pdf/1303.0925)
* Locator: Figure 4 caption, page 4.
* Quote: "Exclusion plot of spin-independent χN coupling at 90% confidence level, superimposed with the results from other benchmark experiments and CoGeNT with and without surface background subtraction."
* Text on the same page: "Exclusion plot of σSI χN versus mχ at 90% confidence level is displayed in Figure 4." (mχ and the sigma subscript lose their formatting in the text layer.)
* Why no number: abstract says "Part of the parameter space in cross-section versus WIMP-mass implied by various experiments is probed and excluded." The Fig. 3 inset only illustrates "an allowed (excluded) cross-section at mχ =7 GeV"; its labels are illustrations, not the limit, so they are not used.
* Exposure moved in: `summary.technical` did not contain it (only `summary.plain` did). It now begins "39.5 kg-days of data from a p-type point-contact germanium (840 g fiducial, 926 g crystal)". Abstract: "39.5 kg-days of data taken with a p-type point-contact germanium detector of 840 g fiducial mass". I also added the paper's own statement "An order of magnitude improvement over our previous results[4] is achieved." (page 4) to `summary.technical`, since the record now has no number to show.

### texono-ulege-220ev-wimp-limits-2008 (numeric)

* URL: https://arxiv.org/abs/0712.1645 (PDF https://arxiv.org/pdf/0712.1645, latest version, which includes the two appendices added after v3)
* Locator: Table I, page 3; spin-independent row (sigma_chiN, units 10^-39 cm^2), first column (198-241 eV bin, "Sampling in mχ (GeV)" = 5).
* Quote: "Limit at 90% Confidence Level < 0.81"
* Value: 0.81 x 10^-39 cm^2 = 8.1e-40 cm^2, spin-independent WIMP-nucleon, mass 5 GeV, 90% CL. The abstract has no number ("The limits improve over previous results on both the spin-independent WIMP-nucleon and the spin-dependent WIMP-neutron cross-sections for WIMP mass between 3-6 GeV"); 5 GeV is inside that range.
* Cross-check in Appendix I (page 11, the discussion of the 55Fe spectrum and the selection efficiency): "the σχN limits (in units of 10−39 cm2 throughout in this Section) at mχ = 5 GeV would increase (become less constraining) from 0.81 to 0.88" under an alternative efficiency choice, so 0.81 is the baseline at 5 GeV.
* Other numbers in the same table, in the note and `summary.technical`: spin-dependent WIMP-neutron "< 2.40" in units of 10^-34 cm^2 at 5 GeV; "< 0.20" (SI, 10^-39 cm^2) and "< 0.59" (SD, 10^-34 cm^2) at 50 GeV (the 1.39-1.87 keV column). Only the SI 5 GeV value is the key value, as in cdex-1.
* Live time kept: `summary.technical` still has "0.338 kg d live time at Kuo-Sheng (30 m.w.e.)"; abstract "data acquisition live time of 0.338 kg-day".
* Table cell: the quote is the table row label and cell as the page prints them. The unit and the mass come from the row header and the sampling row of the same table, which the locator and the note name.

### warp-first-physics-results-2007

* URL: https://arxiv.org/abs/astro-ph/0701286 (PDF https://arxiv.org/pdf/astro-ph/0701286)
* Locator: Figure 8 caption, page 21.
* Quote: "90 % C.L. spin independent limits (solid blue curve) obtained by WARP-2.3l for a total fiducial exposure of 96.5 kg·d and a threshold of 55 keV."
* Text (Section 4, Results, page 15): "the 90% C.L. upper limit has been derived from the observation of zero events in the energy region above 55 keVion" and "the estimated WIMP-nucleon spin-independent cross section in cm2 vs. an hypothetical WIMP mass in GeV/c2" is shown in Figure 8.
* Why no number: the abstract and text print no cross-section value.
* Earlier key text kept in the note: Section 1, "report a first upper limit for the WIMP search with sensitivity comparable to the best published result".
* Exposure kept: `summary.technical` already has "96.5 kg d, 52.76 days live in the body of the paper". Abstract: "an accumulated fiducial exposure of about 100 kg x day".

## Unresolved

* None of the six pages failed to load.
* `texono-ulege-220ev-wimp-limits-2008`: the paper also states an SD limit; only the SI number is the key value because a record carries one. If the integrator wants the SD number as a displayed fact, it belongs in a second quantity, not in this record's `key_value`.

## Method note

`WebFetch` summarised the pages and refused to return the abstract verbatim, so I downloaded the arXiv abstract page and PDF of each paper to the scratchpad with `curl`, extracted text with `pdftotext`, and checked every quote as a substring of that text before writing it. The scratch PDFs were deleted afterwards.

## Check

`/Users/yatharthsirohi/Desktop/HEP-Graph/.venv/bin/python -m hepgraph.atlas.validate` from this worktree: `0 errors, 1894 warnings, 4 informational`. None of the warnings names these six records. I did not run `hepgraph.atlas.build` and did not commit. Files touched: the six result files and this log.
