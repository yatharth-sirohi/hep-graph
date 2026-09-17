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
