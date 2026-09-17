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
