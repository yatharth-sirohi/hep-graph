# Graph operations — v0.3 migration status

## Current behavior (2026-09-16)

HEP Graph **does not yet serve a production graph snapshot**. Its normal path is live INSPIRE; the bundled `data/current.json` is a selected, incomplete offline demo and cannot certify global shortest paths. The provider boundary now preserves per-neighborhood completeness and pins version/filter semantics for live HLBES, but the private cloud snapshot and manual lifecycle have **not** been deployed. No automatic refresh job runs.

Do not present this document as instructions to promote the demo file. The operations below are acceptance requirements, not commands available today.

## To see the current data version

Today, `GET /api/health` reports the bundled demo version and service runtime, **not** a production graph cutoff or validation certificate. There is no active production snapshot ID, build time, cutoff or age to report yet. A v0.3 maintainer status command/endpoint must provide all five, plus schema and validation state, without exposing private storage URLs or credentials.

## To create or resume a candidate refresh

**Not operational yet.** The eventual one-action manual `build` must allocate a unique candidate ID, estimate scope, acquire INSPIRE data into private cloud storage with bounded rate and memory, checkpoint each stable partition, compile an immutable graph, produce a checksummed manifest and load indexes. A failed build leaves production untouched and can be resumed by candidate ID or explicitly discarded. A full rebuild is the v0.3 default. Never run a full harvest from the developer Mac or commit its artifacts to Git.

## To validate and benchmark

**Not operational yet.** The candidate must pass completeness (all partitions accounted for, zero failed shards and no result-window truncation), global identity and duplicate checks, true author-count and correction rules, all graph modes and filters, evidence/HLBES fixtures, snapshot/live shadow comparisons, checksum and index checks. Measure first verified route, exact proof, total time, INSPIRE neighborhood calls, graph-store queries, CPU and evidence hydration against the existing live path. Only a passing candidate may enter `READY`. A builder reaching the end is not a validation certificate.

## To preview

**Not operational yet.** Pin a Vercel preview deployment to the specific `READY` candidate while production remains pinned to its prior snapshot. Exercise researcher search, ambiguity, INSPIRE ID, ORCID, direct/two-/multi-hop, exact versus verified, progressive routes, cancellation, evidence, filters, genealogy, exports and share links. Never point normal traffic at an incomplete candidate.

## To promote or roll back

**Not operational yet.** Promotion must be a distinct, explicit maintainer action after validation, benchmark and preview. It atomically switches a single active pointer; existing searches and their evidence remain pinned to their original version. Retain the previous known-good snapshot. Rollback atomically restores that pointer, without INSPIRE retrieval or index reconstruction. Both operations require tests and an operational drill before first cutover.

## Exactness and freshness

In v0.3, “Exact” must mean exact under the selected filters within the validated, pinned graph snapshot through its stated `source_cutoff`; it must not imply real-time INSPIRE completeness. Live researcher lookup and rich metadata may continue. A live-discovered route can be **Verified** but cannot turn a mixed, incomplete neighborhood into global snapshot proof. Distinguish `AUTHOR_NOT_IN_SNAPSHOT`, `SEARCH_INCOMPLETE`, `LIVE_FALLBACK_USED` and `GRAPH_PROVIDER_ERROR` from `NO_PATH`. Snapshot age is visible but is not itself corruption.

## Cost and authorization gate

No paid cloud resources or full INSPIRE acquisition have been initiated. `FREE_TIER_STORAGE_DECISION.md` selects Turso as a conditional free-tier target, but a full dataset has not been sized against its storage/write quotas. Before that stage, obtain an approved source acquisition approach, measure representative corpus size and large-team skew, and estimate **one-time build** separately from **monthly serving**. The repo's earlier scenario estimates are not a provider quote. Never enable a paid plan or overages merely to finish a build. v0.3 should incur zero scheduled synchronization executions.

## Future (v0.4+)

A scheduler could later call the same build and validation operations. Automatic polling, deltas, reconciliation, scheduled rebuilds, auto-promotion and automatic cleanup are intentionally absent from v0.3; no placeholders or recurring workers should be provisioned for them now.
