# Independent verification: astro-neutrino (Wave 3)

Verifier scope: KM3NeT (FLAGSHIP), ANTARES, Baikal-GVD, ANITA, RNO-G, ARA,
ARIANNA, P-ONE, GRAND — all experiments/detectors/collaborations/facilities/
sites/documents/results this workstream owns, plus the coverage registry row
per experiment. Did not trust `docs/atlas-worklog/astro-neutrino.md`;
re-fetched sources independently via WebFetch (arXiv, ar5iv full text,
INSPIRE API, official collaboration/facility pages, Semantic Scholar for one
paywalled Nature abstract). No git; no subagents; ≤1 inspirehep.net request
per 10 s.

## Records checked

- `data/atlas/facilities/{km3net,baikal-deep-underwater-neutrino-telescope,mcmurdo-ldb,summit-station-greenland}.json`
- `data/atlas/sites/{km3net-arca-capo-passero,km3net-orca-toulon,antares-toulon,baikal-gvd-lake-baikal,mcmurdo-ldb-launch-site,summit-station-rno-g,south-pole-ara,moores-bay-arianna,cascadia-basin-p-one,grandproto300-dunhuang}.json`
- `data/atlas/experiments/{km3net,antares,baikal-gvd,anita,rno-g,ara,arianna,p-one,grand}.json`
- `data/atlas/detectors/{km3net-arca,km3net-orca,antares,baikal-gvd,anita,rno-g,ara,arianna,p-one,grand}.json`
- `data/atlas/collaborations/{km3net,antares,baikal-gvd,anita,rno-g,ara,arianna,p-one,grand}.json`
- `data/atlas/documents/{km3net-loi,km3net-tdr-2010}.json`
- `data/atlas/results/{km3net-uhe-neutrino-observation-2025,km3net-orca6-oscillation-parameters-2024,km3net-arca-diffuse-flux-limit-2026}.json`
- `data/atlas/coverage/astro-neutrino.json` (9 rows)
- Spot-checked most of the 72 `src:astro-neutrino-*` source records against
  the URLs cited in the entities above.

## Values re-fetched: 23

Independently opened via WebFetch this session (not reused from the
worklog's claims):

1. `arxiv.org/abs/1601.07459` + `ar5iv.labs.arxiv.org/html/1601.07459` (KM3NeT LoI) — ARCA/ORCA coordinates, depths, offshore distances, ANTARES relative-position sentence, Pylos mention, document date
2. `inspirehep.net/api/literature/2879193` — title, journal ref, DOI, publication year for the flagship result
3. `api.semanticscholar.org` (DOI 10.1038/s41586-024-08543-1) — verbatim "120 PeV" muon-energy abstract sentence (Nature itself is paywalled)
4. `km3net.org/observation-of-an-ultra-high-energy-cosmic-neutrino-with-km3net` — 220 PeV / 12 Feb 2025 announcement wording
5. `km3net.org/the-observation-of-an-ultra-high-energy-cosmic-neutrino-at-the-bottom-of-the-sea` — "13 February 2023" / "220 peta-electronvolts" quotes
6. `arxiv.org/abs/2408.07015` (ORCA6) — title, date, full abstract (oscillation parameters)
7. `arxiv.org/abs/2608.06163` (ARCA diffuse-flux limit) — confirmed this 2026 paper is real and matches the file's claims
8. `km3net.org/the-construction-of-km3net-the-next-generation-neutrino-telescope-has-begun` — "3 December 2015" installation-start quote, "8 December 2015" publish date
9. `inspirehep.net/api/experiments/1108236` (KM3NeT recid)
10. `km3net.org/welcome-orca-42` — "42 detection units" / 8 July 2026 quote
11. `arxiv.org/abs/2504.09473` + ar5iv full text (ANTARES two-decades paper) — formation 1996, first-line 2006-02-14, completion 2008-05-29, switch-off 2022-02-12, 885 OMs, 12 lines, 2475 m, 40 km offshore
12. `en.wikipedia.org/wiki/ANTARES_(telescope)` — coordinates, completion date, OM/line count (cross-check only, not sole source)
13. `arxiv.org/abs/2309.16310` + ar5iv full text (Baikal-GVD status paper) — coordinates, 1366 m depth, first-cluster-2016, **2018-2022 continuous data-taking** (new finding, see Findings)
14. `arxiv.org/abs/2010.12279` + ar5iv full text (RNO-G JINST design paper) — exact coordinate sentence, ice/firn depths
15. `www.phys.hawaii.edu/~anita/campaigns/anita-iii` — "set to launch in December 2013" (stale schedule, confirmed)
16. `arxiv.org/abs/1803.02719` (ANITA-III paper) — actual December 2014 launch, 22-day flight
17. `arxiv.org/abs/1902.04005` (ANITA-IV paper) — December 2016 launch, 28-day flight
18. `arxiv.org/abs/2411.01761` + ar5iv full text (ARA overview paper) — 5 stations, 100-200 m, 2012-2018, "A3 and A5+PA" current-data sentence
19. `arianna.ps.uci.edu/` and `/research` — re-confirmed the "decommissioned" vs. "eight stations… currently" conflict live
20. `arxiv.org/abs/2304.07179` + ar5iv full text (ARIANNA 2023 results paper) — **"operated successfully until it was decommissioned"** and "seven identical" stations (new corroborating evidence, see Findings)
21. `pacific-neutrino.org/` — re-fetched 2026-09-18; confirmed "In 2026, the first detection line of P-ONE will be deployed" is still future tense, P-ONE-1 only integrated/wet-tested so far
22. `inspirehep.net/api/experiments/{1108484,1826393,1911572,1108245}` — ANITA, RNO-G, ARA, ARIANNA recids
23. `www.km3net.org/wp-content/uploads/2023/05/KM3NeT_DS_TDR-published-in-2010.pdf` — HEAD request, confirms the TDR PDF is live at the URL whose filename corroborates the 2010-03 date choice

All quotes checked appear verbatim in the fetched text (within normal
sub/superscript-stripping for the Nature abstract's asymmetric error bars,
noted as a P2 below). No fabricated numbers, hemispheres, or units found.

## Findings by severity

**P0 (none found).** No factual contradictions in the KM3NeT flagship
records: ARCA (36°16'N 16°06'E, 3500 m) and ORCA (42°48'N 06°02'E, 2450 m)
match the LoI word-for-word, including the "~10 km west of ANTARES" relative
statement; the 2025 Nature observation's title, journal reference, DOI and
120/220 PeV figures are correct and properly distinguished (reconstructed
muon energy vs. inferred neutrino energy); ORCA6 and the 2026 ARCA
diffuse-flux-limit papers are real and accurately summarized; TDR
2010-vs-2009 conflict is transparently resolved and corroborated by the PDF's
own filename. **Verdict for KM3NeT: clean — zero unresolved factual
contradictions found in the flagship record.**

**P1 — fixed:**
1. `experiment:p-one` (`status: proposed`) contradicted `detector:p-one`
   (`status: active`): a detector cannot be running for an experiment that
   has nothing built. Re-fetched the official site (2026-09-18) and
   confirmed the STRAW pathfinder has been genuinely active at Cascadia
   Basin since 2019-01, while P-ONE-1 (the real first production line) has
   only been integrated/wet-tested on land, not yet deployed ("will be
   deployed" is still future tense). Added a `commissioning` interval to
   `experiment:p-one` and changed its status to `commissioning`, matching
   `detector:p-one`. Flagged to me by the coordinator; independently
   confirmed from dated sources before fixing.
2. `experiment:grand` (`status: proposed`) contradicted `detector:grand`
   (`status: commissioning`): GRANDProto300 has been genuinely deployed and
   growing (13→65 antennas) since 2023-06. Added a matching `commissioning`
   interval and status to `experiment:grand`. Flagged to me by the
   coordinator; confirmed and fixed.
3. `experiment:baikal-gvd` and `detector:baikal-gvd` were flatly
   `construction`, but the workstream's own cited source (arXiv:2309.16310)
   states "The Baikal-GVD data collected in 2018-2022 indicate the presence
   of cosmic neutrino flux..." — the array has been taking real physics data
   continuously since 2018, the same overlapping build/operate pattern the
   workstream itself used for KM3NeT (`commissioning`). This was an internal
   inconsistency within the workstream (KM3NeT got the richer treatment,
   Baikal-GVD didn't, despite equally strong evidence) rather than a
   coordinator-flagged item. Added a `commissioning` interval and updated
   status on both `experiment:baikal-gvd` and `detector:baikal-gvd`.
4. All three status changes propagated to `data/atlas/coverage/astro-neutrino.json`
   (rows for p-one, grand, baikal-gvd), whose `status` field had gone stale.

**P1 — verified as correct, strengthened evidence (no data change needed to
the conclusion):**
5. ARIANNA `decommissioned` vs. the research page's "eight ARIANNA stations
   are taking data" conflict: the original resolution ("home page more
   current than inner page") was weak reasoning. Found a much stronger,
   dated, peer-reviewed source already cited elsewhere in the file
   (arXiv:2304.07179, April 2023) that explicitly states "The array was
   completed in 2015 and operated successfully until it was decommissioned"
   and consistently describes the array as **seven** stations, never eight —
   independently corroborating both the decommissioned status and casting
   further doubt on the "eight stations" claim as stale copy. Updated the
   interval notes/sources to cite this stronger evidence instead of resting
   on the original weak reasoning.

**P2 — cosmetic/minor, fixed:**
6. `detector:ara`, `experiment:ara`, `site:south-pole-ara` all carried a
   `value: 200` alongside `min: 100, max: 200` on the depth-range quantity,
   diverging from the established range convention (`icecube.json` uses
   `min`/`max` only, no `value`). Removed the redundant `value` field on all
   three files to match convention. Note: this does not fully silence the
   validator's `display-value-drift` warning (the parser grabs the display
   string's *first* number and compares it to the min/max midpoint, so any
   range quantity produces a >5% warning) — confirmed this same warning
   fires on `site:south-pole-icecube`'s reviewed depth range too, so it is a
   pre-existing, atlas-wide validator quirk, not something specific to this
   workstream.

**P2 — noted, not changed:**
7. `arXiv:2879193`'s "We detect a muon with an estimated energy of 120
   petaelectronvolts (PeV)" quote (in `result:km3net-uhe-neutrino-observation-2025`)
   silently drops the paper's asymmetric error bars (actual abstract:
   "120⁻⁶⁰⁺¹¹⁰ PeV" per Semantic Scholar's rendering) without an ellipsis.
   The central value and meaning are unchanged; flagged for awareness since
   the rule requires *verbatim* quotes, but Nature's own abstract is
   paywalled so this could not be re-verified against Nature's primary
   HTML/PDF directly, only cross-checked via a third-party summarizer.
8. `facility:km3net`/`experiment:km3net`'s "installation begins" interval
   `locator` says "km3net.org, 8 December 2015 news item" while `start` and
   the quote say "3 December 2015" — not an error (the article was
   *published* 8 Dec 2015 describing an event on 3 Dec 2015; confirmed live),
   but momentarily reads as a date mismatch. Left as is; the source record's
   own `date` field (2015-12-08) already disambiguates this correctly.

**Coordinate/DMS conversions checked (all correct):** ARCA 36°16'N 16°06'E →
36.2667, 16.1000; ORCA 42°48'N 06°02'E → 42.8000, 6.0333; Baikal-GVD 51°46'N
104°24'E → 51.7667, 104.4000; RNO-G 72°35'46"N 38°25'19"W → 72.5961,
-38.4219 (west correctly negative); ARIANNA/Minna Bluff 78°31'S 166°25'E →
-78.5167, 166.4167 (south correctly negative). ANTARES's derived 42.8°N
6.17°E is an honest, transparently-documented arithmetic inference (no
source states ANTARES's own degrees directly) and the eastward-offset
direction from ORCA is correct.

**"Coarse regional pointer" sites (P-ONE/Barkley Sound, GRAND/Dunhuang,
ARIANNA/Minna Bluff):** correctly implement the A23 exception — `kind:
campus`, `confidence: uncertain`, explicit note that the point is a named
place near, not at, the array. This is the spec-sanctioned honest treatment
(the alternative, nulling the placement, would trip the "experiment without
facility or site" build-failing check per §9, and A23 was written
specifically to sanction exactly this pattern); no change made.

**Facility structure (KM3NeT: one facility, two sites):** matches the
ID_REGISTRY's explicitly offered alternative ("facility:km3net-arca-capo-passero,
facility:km3net-orca-toulon **or one facility with two sites**"); not a
defect.

**Duplicate detection:** `site:south-pole-ara` sits at the same degenerate
geographic-pole anchor as the pre-existing `site:south-pole-icecube`
(0 m apart, both under `facility:amundsen-scott-south-pole-station`); the
validator flags this as a warning (A20), and both records' notes honestly
explain why (no ARA-specific survey exists; the pole is used as an
honest, generously-sized anchor with a documented ~2 km real-world offset).
Not treated as an error — this is the same honest-uncertainty pattern A23
sanctions, just for a degenerate point rather than a coastal pointer.

**Unverifiable values (left as recorded, could not independently confirm):**
- ANTARES's own precise degrees (no single fetched source states them
  directly; only the corroborated inference).
- RNO-G/ARA/GRAND/P-ONE collaboration formation dates (genuinely not stated
  in any source I could find either).
- Baikal-GVD's exact first-cluster date (2015 press account vs. 2016 status
  paper; both already recorded transparently).
- Whether P-ONE-1's first detection line has been deployed since my
  2026-09-18 re-check (site still said "will be deployed" as of that fetch).

## INSPIRE recids re-verified

KM3NeT 1108236, ANITA 1108484, RNO-G 1826393, ARA 1911572, ARIANNA 1108245 —
all confirmed live via `inspirehep.net/api/experiments/<recid>` against the
`legacy_name`/`name` fields; all source URLs use the canonical
`/experiments/<recid>` form (not `/api/...`).

## Validation and build

`.venv/bin/python -m hepgraph.atlas.validate`: **0 errors attributable to
any file this workstream owns**, confirmed by isolating the `[error]`-level
sections and grepping for every astro-neutrino entity/file pattern (checked
three times across the session: before fixes, after the P-ONE/GRAND/
Baikal-GVD status fixes, and after the ARA depth-quantity cleanup). The
repository's total error count fluctuated during the session (3 → 30 → 8)
because other concurrent sessions were editing unrelated `homestake`/`sage`/
etc. files at the same time (per CLAUDE.md, several sessions share this
checkout); none of that churn touched astro-neutrino files, confirmed by
re-diffing the error list against our file patterns each time.
`json.load()` succeeds on all 118 files this workstream touches or created.

## Fixes applied (all logged above with sources)

1. `experiment:p-one`, `detector:p-one` — added a `commissioning` interval/
   status to the experiment record so it agrees with the detector's `active`
   pathfinder status instead of contradicting it.
2. `experiment:grand` — added a `commissioning` interval/status so it agrees
   with `detector:grand`'s `commissioning` status instead of `proposed`.
3. `experiment:baikal-gvd`, `detector:baikal-gvd` — added a `commissioning`
   interval/status reflecting sourced continuous data-taking since 2018,
   changed from a bare `construction` label.
4. `data/atlas/coverage/astro-neutrino.json` — updated the `status` field
   and `notes` for the p-one, grand and baikal-gvd rows to match.
5. `experiment:arianna` — strengthened the decommissioned-status sourcing/
   note with the dated 2023 collaboration paper's corroborating quote.
6. `detector:ara`, `experiment:ara`, `site:south-pole-ara` — removed a
   redundant `value` field on the 100-200 m depth-range quantity to match
   the `min`/`max`-only range convention used elsewhere in the atlas.

All edited files re-serialized as canonical JSON
(`json.dumps(sort_keys=True, indent=2, ensure_ascii=False)` + trailing
newline). No files outside `data/atlas/` and this worklog were touched; no
git commands were run.
