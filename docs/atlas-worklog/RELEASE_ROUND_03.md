# Release round 3 — every quote checked against its source

Integration branch `atlas-release`, 2026-10-25. One stream (a Sonnet lead with
13 Sonnet triage children) built a machine checker and repaired what it found;
the integrator re-opened the sources behind a sample of the value changes before
merging.

## What changed

**A checker that reads the sources** — `scripts/atlas_quote_check.py` collects
every sourced value that carries a quote (3,832), fetches each cited source once
(HTML, PDF, arXiv full text, Internet Archive fallback; INSPIRE and geocoders are
skipped by rule), normalises both sides and classifies each quote. Its report is
`docs/atlas-worklog/RELEASE_QUOTE_CHECK.md`; every edit is logged in
`docs/atlas-worklog/RELEASE_FACTS.md`.

| class | before | after |
| --- | ---: | ---: |
| verbatim (incl. identical alphanumerics) | 2,595 | 3,351 |
| verbatim segments joined by "…" | 77 | 230 |
| near-miss | 136 | 7 |
| not found in the source | 643 | 22 |
| source unreachable | 170 | 7 |

The 22 remaining "not found" are all in the newest geometry and map records of
the parallel map streams; every entity, result, membership and site file is now
at 0 near/missing.

**Values corrected** — 102 values in 58 files changed because the cited source
said something else. Examples re-opened by the integrator:

* The University of Iowa was listed as an ATLAS institution; CERN's ATLAS
  institutions page lists only Iowa State. Removed (Iowa is a CMS institution).
* Baksan's depth "2100 m" rested on Wikipedia; INR's own page gives the gallium
  laboratory "at a depth of 4700 m.w.e". Corrected.
* SENSEI's pixel count 898,048 → 903,552: the paper's quadrants are "624 rows of
  362 pixels", four of them.
* Daya Bay's detector intervals, GERDA's Phase I/II, Double Chooz's far-detector
  dates, SAGE's commissioning, NOvA's sin²θ₂₃ (0.57 +0.03/−0.04) and three
  result dates were brought to what the papers state.
* KamLAND's 18 m sphere is the containment vessel (the balloon is 13 m); RNO-G
  has 15 deep antennas per station, not per string; Brokdorf is a pressurised-,
  not boiling-, water reactor.
* Claims the sources did not support were trimmed to what they say (ATLAS and
  nEXO "unique capabilities", several "why it matters" lines).

**Sources repaired** — 41 new source records (full-text copies where a DOI led
only to an abstract), 44 repaired (Wayback `archive_url` for H.E.S.S., ANTARES,
Super-K/Hyper-K, SNOLAB, XENON and DEAP-3600 pages that are down or block us).
The 244 CMS roster quotes, which were INSPIRE shorthand not present in the cited
paper, now quote the paper's own affiliation lines.

## How the experience improved, and why it is better

The Atlas's promise is that when it shows a quote under "Sources", the reader
can open the link and find those words saying that thing. Before this round
about one quote in six could not be found in its source — paraphrased, spliced,
or from a page that had moved. Now essentially all can, and the values next to
them were corrected wherever the source disagreed. A physicist spot-checking the
Atlas will find what they look for.

## Verified, and how

* Integrator re-opened: CERN's ATLAS institutions page (Iowa State only), INR's
  Baksan page ("4700 m.w.e"), the SENSEI paper ("624 rows of 362 pixels").
* The stream spot-checked 30 random verbatim quotes against their surrounding
  text (29 support their value; the 30th is an address quoted for a hall
  coordinate that is already labelled approximate).
* Validator 0 errors after the merge (11 new derived-field warnings, which the
  build ignores); Atlas tests 353 passed; bundles rebuilt.

## Not done yet

* The 22 geometry/map quotes from the map streams (round 6 cleanup).
* Coordinate quotes that are street addresses (LNGS halls, CAST, ECN3, EHN1,
  Malargüe) — the values are already labelled approximate; better sources wanted.
* 65 number flags are derived values (counts, conversions) with notes; not errors.
