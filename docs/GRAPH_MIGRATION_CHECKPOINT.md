# Graph migration checkpoint — 2026-09-16

## State and scope

Historical repository: `/Users/yatharthsirohi/Desktop/HEP-Graph`; branch `hep-atlas`; discovery-start HEAD `51321a9fc9f0d35cad9be858825fa214c9708142` (the checkpoint commit itself is the current HEAD after this scoped commit; run `git rev-parse HEAD`); local `origin/main` `ac0a63a4abdfc4b1210805dbf9dd500b466f5607` (not fetched). Existing uncommitted work before this task: modified `hepgraph/server.py`, untracked `data/atlas/`, `hepgraph/atlas/`, `tests/fixtures/atlas_minimal/`, `tests/test_atlas_server.py`. This phase does not alter those paths. No production migration, paid provisioning or fresh INSPIRE harvest was performed.

## Measurements and decisions

- Existing live audit: 40 Hostert <=10 works / 70,856 B; 25 Aad >10 works / 10,352,493 B; 1,000 maximum page, 10,000 result window; Aad >10 complete retrieval estimated ~600 MB. Source: `docs/INSPIRE_NEIGHBORHOOD_API_AUDIT.md`.
- Existing saved pilot `data/current.json`: 1,180 works, 5,249 people, 5,996 resolved work-author links, one 2,932-author paper; sample JSON 2,304,802 B. Minimal dense-ID work projection 140,093 B, gzip 35,430 B; 119 B/work lower bound.
- <=10 sample: 3,348 distinct pairs, 3,796 pair-work refs. Local SQLite prototype: incidence 184,320 B, incidence + precomputed small-team adjacency 389,120 B. Warm local single/batched median: incidence 0.053/0.055 ms; hybrid 0.026/0.031 ms. Thirty iterations, no network. Not a Vercel latency claim.
- A clique for the sample mega-paper alone would need 4,296,846 undirected pairs. Decision: hybrid <=10 adjacency plus all-paper incidence, immutable versions and a DB active-version pointer; HLBES remains unchanged.
- No verified full corpus count or large-team distribution. Scenario at pilot density: 1M works ~156 MB incidence SQLite or ~330 MB hybrid SQLite **before** profiles/evidence/history; 5M ~780 MB or ~1.65 GB. This is not a capacity quote.
- Scoped exactness: complete, validated graph through cutoff T can support “Exact shortest path in graph through T”; live-only/after-T facts and mixed partial traversal yield verified or incomplete, not present-day global exactness.

## Reproduction and checks

Commands used: `git status --short --branch`; `git branch --show-current`; `git rev-parse HEAD`; `git rev-parse origin/main`; `git log --oneline -20`; `git remote -v`; `rg` and source reads; `python3 /private/tmp/hep_graph_sample_measure.py` (local disposable benchmark script). Official references and details are in `docs/PRODUCTION_GRAPH_STORAGE_DESIGN.md`. No new live requests succeeded or were needed; the saved pilot and prior bounded live audit supplied the data.

Files changed by this phase: `docs/PRODUCTION_GRAPH_STORAGE_DESIGN.md` and this checkpoint only. No production data or credentials were added. No code behavior changed. Review/test: documentation and sample arithmetic checked locally; no application tests required for document-only changes. Verify with `git diff --check` and `git status --short` after placing these files in the repo. The existing Atlas edits remain uncommitted and must not be staged by a blanket `git add .`.

## Open questions and authorization

- INSPIRE has not documented an approved full bulk dump or reliable `updated` change feed in the official REST docs reviewed. Confirm with INSPIRE before full bootstrap; verify deletion/redirect coverage and stable partitioning.
- Obtain a stratified, modest sample of large-team and sparse/prolific records before sizing a full DB. Existing pilot is strongly biased and cannot determine the full author-count distribution.
- User account authorization is required before paid cloud DB/object storage, any credentials, a large harvest, or production cutover. Vendor choice can follow measured cost/region/security; no choice is needed to implement the provider seam.
- Snapshot completeness must be defined for coauthorship plus enabled genealogy and exactness labels tested in the UI. A stale complete snapshot supports only a time-scoped exact claim unless full post-cutoff coverage is proven.

## Exact next step after reset

Implement `GraphProvider` with `FixtureGraphProvider` and a `LiveInspireGraphProvider` wrapper around existing `DeepSession` behavior. Add differential fixtures for <=10, >10/all, year/min-shared, duplicate/erratum, identity conflicts, evidence, batch completeness and provider failure. Keep `hepgraph/hlbes.py` unchanged. Then add a private local synthetic snapshot provider/prototype and benchmark before any cloud setup. Run the relevant Python suite and commit only the new provider/tests/checkpoint work on a clean, reviewed branch or a scoped commit that excludes the existing Atlas changes.
