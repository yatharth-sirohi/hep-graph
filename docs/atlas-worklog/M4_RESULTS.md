# M4: Results as a story, and the WIMP exclusion plot

Branch `atlas-m4-results`. Working titles (the owner names features): "Results as a story"
(`views/results-rows.js`, `WORKING_TITLE`) and "WIMP exclusion plot" (`views/limits-rows.js`).

## Scope

1. `#/view/results-story[/<topic-slug>]`: every result of the Atlas as a mark at its date, in
   lanes by physics question (Atlas topics). A mark opens a card with the result's own page and its
   paper; a lane header opens its topic; the timeline year (`?y=`) draws a band and dims what comes
   after it; on a phone the lanes stack and scroll sideways together.
2. `#/view/limits/wimp-si`: published spin-independent WIMP-nucleon 90 % CL limits against WIMP
   mass, log-log, every curve cited, from HEPData tables stored in `data/atlas/limits/` (A29).

Entry points: topic panels ("See the results as a story", every topic that has a result), the
Results list, search ("results timeline", "<topic> timeline"); the dark-matter and
direct-detection topic panels, the LZ, XENONnT and PandaX-4T experiment panels, the three LZ and
XENONnT result panels, and search ("dark matter limits", "LZ limit", ...) for the plot.

## Claim level (A29, part a)

No new result field was added. `result_type` is the structured claim level (A16 already checks
observation, discovery, evidence and first_detection against the claim's own wording), and every
result that states a significance carries it as a sourced verbatim string (49 of 109 have a
value; 39 more carry a sourced null with a note; 21 have no block). The form of a mark is read from
`result_type` only; the significance is printed as written and never parsed.

| Form | `result_type` | Marks |
| --- | --- | --- |
| filled circle | observation, discovery, first_detection | 33 |
| ring | evidence | 16 |
| down triangle | limit | 17 |
| small dot (neutral) | measurement, precision_measurement, anomaly, technology_milestone | 43 |

Cases the view must not "fix": `muon-g-2-measurement-2021` states 3.3σ but is a precision
measurement (neutral mark); `icecube-galactic-plane-neutrinos-2023` is an "observation" at 4.5σ
(observation mark, 4.5σ in its card). 14 of the 49 observation or evidence results carry no
significance value in the Atlas; their cards say "no significance is recorded in the Atlas".

## Lanes

19 topic lanes (`LANE_TOPICS`) plus "Filed under other topics" (2 results: KATRIN's neutrino-mass
limit and SuperKEKB's luminosity record). A result stands in every lane whose topic it, or a
sub-topic, carries: 109 results, 147 marks, 35 results in more than one lane (the card says "Also
in", selecting a mark rings its copies).

## Data (A29, part b)

| File | HEPData record | Table | DOI of the paper | arXiv | Columns | Points |
| --- | --- | --- | --- | --- | --- | --- |
| `lz-2022-si-wimp-nucleon` | ins2107834 v1 (recid 144760) | SI cross section | 10.1103/PhysRevLett.131.041002 | 2207.03764 | mass, pc_limit | 40 of 40 |
| `lz-2024-si-wimp-nucleon` | ins2841863 v2 (recid 155182) | SI cross section | 10.1103/4dyc-z8zf | 2410.17036 | mass, limit | 26 of 26 |
| `xenonnt-2023-si-minimum` | none | (published minimum, from `result:xenonnt-first-nr-search-2023`) | n/a | 2303.14729 | n/a | 1 |
| `pandax-4t-2021-si-minimum` | none | (published minimum, from the PandaX-4T key spec) | n/a | 2107.13438 | n/a | 1 |

HEPData's headers carry no units. Units (GeV/c², cm²) are justified by the abstract: LZ 2022
"9.2×10⁻⁴⁸ cm² at 36 GeV/c²" is the table's pc_limit at 36 (9.16769e-48); LZ 2024 "2.2×10⁻⁴⁸ cm² ...
40 GeV/c²" is the table's `limit` at 40 (2.18168e-48). The validator enforces the match.
Table JSON hashes, retrieval date (2026-10-26) and licence (CC0) are recorded in each file.

## Unresolved

* **XENONnT and PandaX-4T limit curves are not on HEPData** (searched 2026-10-26 by arXiv id, DOI,
  title and collaboration; XENON1T is absent too). Only the one number each abstract publishes is
  drawn, as a hollow diamond that says so. A real curve needs a collaboration data release
  (XENONnT and PandaX publish elsewhere); that fetch was outside the brief (HEPData only) and needs
  the owner's go-ahead.
* **Neutrino fog**: no HEPData table, so none is drawn; the page says so.
* The PandaX-4T marker is the 2021 commissioning run (the only limit the Atlas records for it).

## For the integrator

* `host.js`: `returnTo` is the last non-view route the page saw. A view that links out to records
  (these two do) therefore returns to the record, not to where the view was opened from, after a
  history Back. Not changed here (framework file); worth a look at M-integration.
* `result_type: limit` for `icecube-sterile-neutrino-search-2020` and
  `km3net-arca-diffuse-flux-limit-2026`: their claim quotes do not state a limit (the A16 keyword
  check does not cover `limit`). The mark follows the record.
* `static/atlas/generated/` is rebuilt, not committed.
