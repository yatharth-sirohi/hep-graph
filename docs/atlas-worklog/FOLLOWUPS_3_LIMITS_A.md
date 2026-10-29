# Followups 3, limits A: five dark-matter limit results whose key value was an exposure

Date: 2026-10-29. Branch `atlas-next`. Model fix: `result:coupp-2kg-spin-dependent-limits-2008`
(FIX_DATA2.md section 7).

Each record below is a `limit` whose `key_value` was an exposure (or a live time), not the limit
the paper sets. All five papers publish their limit as a plotted curve (or, for HDMS, state it only
qualitatively in the abstract available) and give **no single cross-section number**, so in each
record `key_value` is now `null` and `key_value_text` is a sourced object, with
`verified_at: "2026-10-29"` and `confidence: "verified"`. The exposure was already in each
record's `summary.technical`, so no sourced fact was lost and no `summary` field was changed.
No new source records were needed (an arXiv abstract and its PDF are one source).

Pages read today: the arXiv abstract pages and the PDFs (`https://arxiv.org/pdf/<id>`, current
version) of the four arXiv papers, and the OSTI ETDEWEB pages for HDMS. Nothing from
inspirehep.net, Wikipedia or memory.

## Table

| Record | Before (`key_value`) | After (`key_value_text.value`) | Verbatim quote | URL and locator |
|---|---|---|---|---|
| `coupp-4kg-minos-limits-2010` | 28.1 kg d, quote "effective exposure of 28.1 kg-day" | "Spin-dependent WIMP-proton limits are the curve of Fig. 4, set from a 90% Poisson upper limit of 6.7 for the mean of the signal (three candidate events)." | "Interpreting the three events in the signal region as WIMP candidates results in a 90% Poisson upper limit of 6.7 for the mean of the signal. The resulting improved limits on spin-dependent WIMP-proton couplings are shown in Fig. 4." | https://arxiv.org/pdf/1008.3518 (v2), main text, PDF page 4, with the Fig. 4 caption |
| `coupp-4kg-snolab-limits-2012` | 553 kg d, quote "total exposure of 553 kg-days" | "The 90% C.L. spin-dependent WIMP-proton limit is the curve of Fig. 6, with all 20 observed single recoil events treated as WIMP candidates and no background subtraction." | "The 90% C.L. limit for this result is shown in blue, interpreting all 20 observed single recoil events as WIMP candidates with no background subtraction." | https://arxiv.org/pdf/1204.3094 (v2), Figure 6 caption, PDF page 7 |
| `dm-ice17-annual-modulation-2017` | 60.8 kg yr, quote "Taken over 3.6 years for a total exposure of 60.8 kg yr" | "DM-Ice17 data are consistent with no annual modulation in the 4-20 keV energy range." | "DM-Ice17 data are consistent with no modulation in the energy range of 4-20 keV" | https://arxiv.org/abs/1602.05939, abstract |
| `hdms-spin-dependent-wimp-neutron-limit-2005` | 85.48 kg d, quote "The results (85.48 kg d) improve" | "Improves the best existing limits on the WIMP-neutron spin-dependent cross-section (previously from xenon-129) for low WIMP masses." | "improve the best present existing limits on the WIMP-neutron spin-dependent cross-section (obtained from {sup 129}Xe) for low WIMP masses" | https://www.osti.gov/etdeweb/biblio/20829911, abstract (source `src:hdms-genius-tf-lessons-physica-scripta-2006`) |
| `pico-2l-first-results-2015` | 211.5 kg d, quote "with a total exposure of 211.5 kg-days" | "The 90% C.L. limit on the spin-dependent WIMP-proton cross section is the curve plotted in Fig. 6." | "The 90% C.L. limit on the SD WIMP-proton cross section from PICO-2L is plotted in red" | https://arxiv.org/pdf/1503.00008 (v2), Figure 6 caption, PDF page 5 |

Where the exposure now lives: `summary.technical` of each record ("effective exposure of 28.1
kg-day"; "553 kg-days over three nucleation thresholds (437.4 kg-days effective for single
bubbles)"; "exposure 60.8 kg yr"; "85.48 kg d"; "211.5 kg-days at four recoil-energy
thresholds"). Each `key_value_text.note` says so.

## Per-record findings

* **coupp-4kg-minos-limits-2010.** The limit is Fig. 4 (spin-dependent proton cross-section
  against WIMP mass). The text gives "a 90% Poisson upper limit of 6.7 for the mean of the
  signal", which is an event count, not a cross section, so it was not made a `key_value`.
  The PDF has no "excluded" sentence; the quote is the nearest statement of the limit.
* **coupp-4kg-snolab-limits-2012.** The conclusion says "The resulting 90% C.L. limit plots for
  spin-dependent WIMP-proton and spin-independent WIMP-nucleon cross sections are presented in
  Figs 6 and 7, respectively." The Fig. 6 caption was quoted instead because the conclusion wraps
  "spin-" and "WIMP-" across line ends, so a copy from the PDF text is not clean. Fig. 6 is drawn
  with a band for the systematic uncertainty in the fluorine nucleation efficiency.
* **dm-ice17-annual-modulation-2017.** The abstract states a null result and gives no modulation
  amplitude. The WIMP limit is the 90% C.L. exclusion curve of Fig. 5 (PDF page 5, caption "WIMP
  exclusion limits at 90% C.L. from the 60.8 kg yr DM-Ice17 physics data set"). The text also
  gives a best-fit amplitude for one bin only (Det-1, 4-6 keV: 0.05 +- 0.03 counts/day/keV/kg),
  which is not the headline result, so it was not used.
* **hdms-spin-dependent-wimp-neutron-limit-2005.** No number found. The cited OSTI abstract has
  none. The original paper (Klapdor-Kleingrothaus, Krivosheina, Tomei, Phys. Lett. B 609, 226,
  2005; DOI 10.1016/j.physletb.2004.12.081) does not turn up on arXiv (searches by title words,
  author names and HDMS keywords found only the 2000-2003 HDMS papers and later reviews), the DOI
  page only redirects, and its OSTI ETDEWEB abstract (https://www.osti.gov/etdeweb/biblio/20845161)
  also states no cross-section value: "The results improve the best present existing limits on
  the WIMP-neutron spin-dependent cross section (obtained from {sup 129}Xe) for low WIMP masses."
  So `key_value` is null and the quote is the exclusion statement of the cited source. The review
  arXiv:0806.3917 shows this result as an exclusion curve labelled "HDMS05/SD" (so it is a curve),
  but it was not added as a source because it is a different document and the note does not need
  it; the note says only what the cited abstract shows.
* **pico-2l-first-results-2015.** The limit is Fig. 6 (SD WIMP-proton) and Fig. 7 (SI
  WIMP-nucleon); the conclusion says "the resulting 90% C.L. limit plots ... are presented in
  Figs. 7 and 6". No single number in the text.

## For the integrator (not changed, outside this brief)

1. **The arXiv abstract page and the current PDF disagree for the two COUPP-4kg papers.** The
   abstract text shown on arxiv.org/abs (the one the `claim` quotes and `why_it_matters` /
   `summary.plain` rest on) is the v1 wording; the current PDF (v2, 2011 and 2012, matching the
   journal versions) changed it.
   * `coupp-4kg-minos-limits-2010`: abs page "provides the strongest direct detection constraint
     to date on WIMP-proton spin-dependent scattering"; PDF v2 abstract "provides strong direct
     detection constraints on WIMP-proton spin-dependent scattering".
   * `coupp-4kg-snolab-limits-2012`: abs page "provides world best direct detection constraints
     on WIMP-proton spin-dependent scattering ... and demonstrates significant sensitivity for
     spin-independent interactions"; PDF v2 abstract "The remaining excess of single bubble
     events exhibits characteristics indicating the presence of an additional background. These
     data provide new direct detection constraints on WIMP-proton spin-dependent scattering for
     WIMP masses >20 GeV/c2 and demonstrate significant sensitivity for spin-independent
     interactions."
   The two records still quote the abs page verbatim and say so ("abstract"), so they are not
   false to their locator, but "strongest" and "world best" are not claims of the final papers,
   and `summary.plain` ("set the best limit of its time") and `why_it_matters` inherit them. The
   SNOLAB record also omits the paper's statement of an additional background. Suggested fix:
   requote the claim from the v2 abstract and soften `summary.plain` and `why_it_matters`.
2. `pico-2l-run2-2016`, `pico-60-cf3i-2015` and the TEXONO and WARP records of FIX_DATA2.md
   section 7 are other sessions' (FOLLOWUPS_3_LIMITS_B); they were left alone.

## Checks

* Quotes checked programmatically against the text extracted from the pages and PDFs read today
  (whitespace-normalised): all five found verbatim.
* `/Users/yatharthsirohi/Desktop/HEP-Graph/.venv/bin/python -m hepgraph.atlas.validate`, run from
  the worktree: `0 errors, 1894 warnings, 4 informational`. None of the warnings concerns these five
  records. `hepgraph.atlas.build` not run; nothing committed.
* PDFs were deleted from the scratch directory after extraction.

## Integrator follow-up: the two COUPP-4kg claims (2026-10-29)

The arXiv listing pages still carry the v1 abstracts ("the strongest direct detection constraint to date",
"world best direct detection constraints"); the papers themselves (PDF v2 of each) say "strong" and "new"
constraints, and the SNOLAB paper adds that "The remaining excess of single bubble events exhibits
characteristics indicating the presence of an additional background." Both records now quote the v2
abstracts in `claim` (locator names the version and date), `summary.plain` and `why_it_matters` no longer
say "strongest" or "best", the SNOLAB technical summary carries the additional background, and each record's
`notes` says why. Checked against https://arxiv.org/pdf/1008.3518 and https://arxiv.org/pdf/1204.3094
(text extracted with pdftotext). Every quote in this log and in LIMITS_B was re-checked by the integrator
against the PDF text (two match only after line-break hyphenation is ignored), the ULEGe number against
Table I of arXiv:0712.1645 (SI, 5 GeV: "< 0.81" in units of 10^-39 cm^2), and the HDMS quote against the
OSTI page.
