# Evidence search, shortestness and continuation

## Definition

The graph contains researchers. Each eligible coauthor pair is one undirected hop. Shared-work counts never create fractional distances. A coauthor pair can carry explicit doctoral metadata without adding another degree. When genealogy supplementation is enabled, a separately sourced PhD-only pair may establish one visually distinct hop.

Eligibility uses full author count, scholarly date, permitted document types, distinct-work normalization and the selected minimum shared-work count. Small-team is ≤10 authors, large-team is >10, and all papers has neither bound. Paper filters affect coauthorship; they do not rewrite doctoral facts.

## Search sequence

1. **Prepare selected identities.** Selecting an exact record starts bounded, reusable identity, coauthor-summary and first-page preparation. Keystrokes do not trigger graph traversal.
2. **Check the direct pair.** Retrieve current endpoint profiles and shared-paper pages using both numeric author references. A valid direct edge proves distance one. Self queries prove distance zero.
3. **Check two-hop candidates.** Inspect both endpoint summaries before pursuing deeper guide corridors. Shared neighbors suggest exact pair checks, and every hop must acquire eligible paper evidence.
4. **Expand from both ends.** Retain visited identities, predecessor information, bibliography cursors and evidence. Prefer smaller available frontiers; bound optional cross-frontier queries. Candidate summaries and historical hints can guide acquisition, but never establish displayed edges.
5. **Validate the candidate.** Fetch current public profiles for every person in each displayed alternative. Apply name, role, date, count, correction and identity guards, then run exact unweighted BFS on the resulting graph. A rejected candidate sends the search back to alternatives.
6. **Continue when needed.** A verified deeper route remains inspectable. Continue exact search resumes the same worker and evidence rather than starting at depth zero. The already returned route is not repeatedly rediscovered and returned as new progress.

## What is proven?

A found path proves its retrieved edges. Exact BFS establishes shortestness within that retrieved, filtered graph. It cannot by itself rule out unseen upstream edges.

Live results distinguish:

| Result | Justification |
| --- | --- |
| Zero hops | Same verified researcher identity |
| One hop | Direct qualifying evidence; no shorter connection between distinct people is possible |
| Two hops, global shortestness proven | Both hops verified and the complete direct-pair check rules out one hop |
| Verified deeper path | Every hop verified; global shortestness remains unproven |
| Search incomplete | A missing source, limit, ambiguity or failed retrieval prevented completion |

The two-hop proof requires an exact, consistent direct-query total and enough actual records from all required pages. A lower-bound `gte` total, missing relation, changing total or short page cannot establish exhaustive direct absence. `coverage.direct_pair` records pages checked, actual records seen, reported total, its exactness and completion. An identity-conflicting direct paper is withheld rather than used as a shortcut.

No bounded failure is labeled “no connection exists.” Live zero/one/two-hop proof flags refer to the selected documented graph definition and source interpretation, not a claim that INSPIRE is an error-free biography of every researcher. Deeper global proof is deliberately not claimed.

## Discovery versus evidence

The official `/api/literature/facets` endpoint supplies up to 100 author buckets. The parser accepts only numeric INSPIRE author IDs, drops names and unrelated aggregations, preserves truncation indicators and rejects malformed counts. Returned counts are **not** final shared-work counts. A facet includes ineligible or unresolved data and can omit neighbors.

The compact navigation graph is bounded to 20,000 candidate people and 100,000 links. It proposes corridors only. The saved snapshot and eight historical ID-pair hints can also guide retrieval, but their records are not copied into the live evidence graph. Every proposed hop is checked again against current records and the exact selected filters.

Each live graph stores canonical author–paper incidence; it does not expand an ATLAS paper into millions of pair records. Large-team or uncapped queries use five complete literature records per page to stay within the transport response bound. Later-page cursors use the actual page size; no author list is truncated.

## Identity safeguards

Names are search/display labels; numeric author IDs are identity keys. Alias and diacritic handling does not merge profiles. Final candidate validation refreshes the relevant current profiles. Explicit incompatible initials or full given names, conflicting full identities on an initials-only profile, and narrowly reviewed historical source errors can make an authorship occurrence unresolved.

For a documented deceased profile, a matching initials-only byline more than two years after the recorded death year is withheld pending identity review. This is an uncertainty safeguard, not a claim that posthumous publication is impossible. Full stated matching names, unknown dates and the publication-delay window are not rejected by that rule alone.

Native PhD entries are also checked against the referenced current adviser profile. A contradictory stated adviser name is withheld; the app does not swap record IDs or infer the intended relationship. Raw source data and exclusions remain auditable. See [identity collisions](IDENTITY_COLLISIONS.md).

## Budgets and retained state

| Allowance | Initial slice | Continuation slice |
| --- | ---: | ---: |
| Time | 300 s | 900 s |
| Retrieval calls | 240 | 720 |
| Work ceiling | 20,000 | 50,000 |
| Person ceiling | 30,000 | 50,000 |
| Nominal literature page size | 100 | 100 |
| Large-team/uncapped page size | 5 | 5 |

These are ceilings, not target acquisition sizes. A found route normally needs a small fraction. Source failures and time/request checkpoints can continue automatically for up to two hours, subject to cancellation, stalled-progress detection and hard memory limits. A verified route pauses with a clear continuation action. Job retention is bounded separately from result caching; see [storage policy](ON_DEMAND.md).

Every session's SQLite connection stays on the worker that created it. Stop prevents new search work; an already running shared request may finish within its transport timeout and safely warm the cache. Browser refresh stores only a job handle and reconnects to the retained job. New settings create a distinct search key.

## Verification

Permanent tests cover independent NetworkX comparisons, arbitrary endpoints outside the saved sample, multiple pages, 102-author late-page evidence, false summary edges, direct-query pagination, lower-bound totals, short/malformed pages, cancellation, retained continuation, identity correction, unavailable sources and memory ceilings. [Current validation](VALIDATION.md) records actual offline, browser and real-source results.
