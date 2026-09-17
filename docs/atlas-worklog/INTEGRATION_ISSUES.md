# HEP Atlas integration issues (orchestrator log)

Raised by workstream reports and orchestrator review; each is closed by a fix
plus, where possible, a validator rule so the class cannot recur.

| # | Severity | Issue | Raised by | State |
| --- | --- | --- | --- | --- |
| 1 | P1 | Duplicate source URLs across workstreams: `src:cms-cern-ls3-farewell-2026` vs `src:cern-ls3-farewell-2026`; `src:cern-long-shutdown-3-page` vs `src:cms-cern-long-shutdown-3-page`; `src:cms-cern-run2-conclusion-2018` vs `src:cern-run2-conclusion-2018`. A20 fails on this. Shared CERN pages need one owner. | dark-matter lead | open |
| 2 | P2 | `quote` longer than 300 characters in `experiments/icecube-gen2.json` (×2); `excerpt` over length in `sources/belle2-tdr-2010.json`, `sources/cms-higgs-portrait-arxiv-2022.json`, `sources/atlas-phase2-tdrs-inspire.json`. | dark-matter lead | open |
| 3 | P1 | SURF geography: the DUNE far-detector site falls back to an OpenStreetMap surface point at `precision_m` 2000 marked REVIEW REQUIRED; the LZ Davis Campus point (Heise arXiv:1503.01112 Table 5) is 700 m away. Both are underground points on the 4850 Level. Needs a geographic reviewer decision and one consistent treatment. | dark-matter lead | open |
| 4 | P2 | A17 edge case: the only published LZ detector coordinate is rank 10 (a journal paper); the rule forbids sole reliance on rank ≥ 8 for an underground lab. Currently co-cited with the rank-2 SURF page. Confirm this is the intended reading, or soften A17 for coordinates that only ever appear in the literature. | dark-matter lead | open |
| 5 | info | LZ has no ¹³⁶Xe 0νββ *result* — only a 2019 projected-sensitivity paper. The brief asked for one; the lead correctly refused. No record written. | dark-matter lead | closed |
| 6 | info | A newer LZ result (September 2026 EFT high-energy nuclear-recoil search, 2.6σ global) exists but has no arXiv id yet; recorded as a note, not a result. Revisit when posted. | dark-matter lead | open |

## Wave 2 (2026-09-17)

| # | Severity | Issue | Raised by | State |
| --- | --- | --- | --- | --- |
| 7 | P1 | Validator enforced the superseded §4 rule that a terminal interval needs an `end`, contradicting amendment A3. 12 false findings on the LEP detectors. | orchestrator | sent to pipeline |
| 8 | P1 | `duplicate-name` matched short acronym aliases, so Columbia, Cornell and Chulalongkorn "collided" as CU. 62 false findings across the ROR-derived institutions. | orchestrator | sent to pipeline |
| 9 | P1 | `status-not-derived-state` is wrong for entities whose presence has ended: a decommissioned accelerator derives to `None` at the build date, so its honest `status` is flagged. | orchestrator | sent to pipeline |
| 10 | P1 | `display-value-mismatch` mis-parses thousands separators ("26 659 m") and unicode scientific notation ("2.11 × 10³⁴"). 12 false findings. | orchestrator | sent to pipeline |
| 11 | P2 | `duplicate-source-url` rejects a chapter sharing its parent document's DOI; needs a `part_of` field. | orchestrator | sent to pipeline |
| 12 | P1 | Genuine duplicate source records across workstreams: the same home.cern pages, the SURF site, the CERN ROR record, the UA1 page and the MicroBooNE detector paper each exist under two ids. Needs one mechanical dedup pass once research settles. | multiple leads | open |
| 13 | P2 | Several Japan results are missing the required `links` field. | orchestrator | open |
| 14 | P2 | Super-Kamiokande construction starts before the recorded founding date of the Kamioka Observatory facility. Probably the observatory's formal establishment versus the mine's earlier use; needs a note either way. | orchestrator | open |

## From the independent data-quality review of wave 1 (report: REVIEW_data_quality_wave1.md)

Zero P0 findings. 36 of 36 independently re-fetched quotes matched their sources
verbatim; no fabricated citation, no unit error, no inflated result wording.

| # | Severity | Issue | State |
| --- | --- | --- | --- |
| 15 | P1 | Systemic in the CMS results: where a result carries an `announced` date earlier than its preprint, amendment A16 requires `date`/`date_kind` to use the announcement. Both CMS results with an `announced` field use the later preprint instead — 2 of 2, so a class rather than a slip. The LZ results implement the rule correctly. | open |
| 16 | P1 | `site:kek-tsukuba-belle-ii` carries `point_kind: detector` coordinates sourced only from a Wikipedia infobox (rank 12), which A17 forbids for a detector point. The flavour lead disclosed this honestly in its worklog, but it is still live. Needs a real source or a demotion to an approximate region. | open |
| 17 | P2 | Two coordinate-supporting quotes (CMS Point 5 from arXiv:1005.5332, the LZ Davis Campus from arXiv:1503.01112) could not be independently confirmed because only the abstract pages were retrievable. Plausible but unverified. | open |
| 18 | P2 | The Belle detector paper is paywalled; the record correctly leaves subsystem geometry null rather than inventing it. No action beyond keeping the disclosure. | closed |

## Fixture-versus-generated divergence (orchestrator, 2026-09-17)

A class of bug that neither test suite could see, because the browser suite
loaded `?data=fixtures` and the Python suite built the fixture dataset. Three
separate features were dead against the real bundles while every test was green.

| # | Severity | Issue | State |
| --- | --- | --- | --- |
| 19 | P0 | Sites: the generated bundle nests coordinates, the fixtures flatten them. The globe read an undefined latitude, computed a NaN position and drew **no markers at all**. | fixed (loader accepts both) |
| 20 | P1 | Institutions in membership rows: same nesting split, so collaboration mode showed no institution dots. | fixed |
| 21 | P1 | Results and documents: the generated bundles are flat id maps, the fixtures wrap them under a named key. Results mode and the document library were **empty**. | fixed |
| 22 | P1 | Every cold deep link opened an empty globe: startup rebuilt the URL from uninitialised state, erasing the route before it was read. In-app navigation worked, so no test caught it. | fixed |

The lesson for the release gate: a test that exercises fixtures is not a test of
the product. `tests/browser_atlas.cjs` should run twice, once against each tree,
and `static/atlas/fixtures/build_fixture.py` should be regenerated from the
canonical nested shape so the two stop drifting.

## From the independent scientific and historical review

Zero P0 findings across Fermilab/DUNE, the Fermilab neutrino programme, Japan,
CERN/ATLAS and the historic experiments. 32 technical values re-verified
word-for-word against primary sources. Verdict: a physicist would trust it.

| # | Severity | Issue | State |
| --- | --- | --- | --- |
| 23 | P1 | `facility:fermilab` and `accelerator:fermilab-linac` derived to `construction` for every year from 1969 to today, because an open-ended groundbreaking milestone outranked the operating interval. Root cause: amendment A3 gives only lifecycle intervals the power to set state, and nothing implemented it. | fixed: runs and phases now decide only where no lifecycle interval covers the year; the two milestones are recorded as phases |
| 24 | P2 | Several detector coordinates are campus centroids reused for specific halls (the SURF 4850 Level caverns, the J-PARC near-detector hall, and one Fermilab campus point shared by seven near detectors). All self-disclosed with approximate confidence and review notes, so nothing is hidden, but they are not surveyed positions. | open |
| 25 | P2 | `src:ua1-inspire-w-z-discovery-papers` is named for UA1 but is a combined UA1 and UA2 query, and is cited as UA2's source too. Confusing id, correct content. | open |
| 26 | P2 | The 1989 three-neutrino-species result uses one ALEPH paper title as the shared claim quote for all four LEP collaborations, whose papers have different titles. The physics is right; the quote misrepresents three of the four. Should use per-attribution sources. | open |

## From the independent user-experience review

Four P0 defects, five P1, five P2. Its verdict: "a newcomer would not understand
what they're looking at, and an expert would not trust it past the first
timeline scrub — not because the underlying data is bad, but because four
field-name bugs between that data and the screen make the interface state things
the atlas's own data directly contradicts." Every one is the fixture-versus-real
divergence class again, this time in the detail panels.

| # | Severity | Issue | State |
| --- | --- | --- | --- |
| 27 | P0 | The panel's status badge ignored the selected year: ATLAS read "Upgrade" in 1995, SBND read "Active" in 1995 although it first took data in 2024. The globe used `state_segments` correctly; only the panel did not. | assigned |
| 28 | P0 | Plain-language summaries never rendered. Every record has a good `summary.plain`, but the panels read a field the bundle does not carry, so every panel said "No plain-language summary yet". | assigned |
| 29 | P0 | Every collaboration read "0 confirmed members" directly above a correct institution count. | assigned |
| 30 | P0 | All 56 documents showed blank titles and dates: the panel read `title` and `year`, the records carry `name` and `date`. | assigned |
| 31 | P1 | DUNE was labelled a historical experiment on Fermilab's panel, because only active and commissioning counted as current. | assigned |
| 32 | P0 | The globe's timeline did not filter anything: sites have no intervals of their own, so every marker showed in every year and the ATLAS cavern appeared a decade before it was dug. | fixed: a site's history is derived from the experiments placed there |

What the review praised, and what should be preserved: sources are consistently
inspectable with quotes and access dates; the evidence-class wording is
reproduced verbatim; the institution to person to HEP Graph handoff works
end to end; the no-WebGL fallback is a genuinely good accessible view; reduced
motion is honoured; and result-type wording is well calibrated against real
physics history everywhere it was spot-checked.
