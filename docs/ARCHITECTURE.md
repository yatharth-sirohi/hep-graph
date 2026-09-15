# Architecture

The canonical product is the existing Python HTTP service and browser application. Its default source is live INSPIRE; the small saved snapshot is a separate, explicitly scoped offline source. This release refines the existing architecture.

## Live request flow

```text
Select exact author ID → bounded preparation → shared public metadata cache
Select other author ID → equivalent preparation
Find connection → retained search job
  → direct-pair evidence check
  → both endpoint coauthor summaries and candidate two-hop checks
  → guided retrieval and bidirectional expansion
  → normalization + current-profile identity checks
  → exact BFS on retrieved evidence
  → evidenced result, explicit shortestness status, inspectable sources
```

`remote.py` owns fixed INSPIRE endpoints, field allowlists, pacing, response validation, expiring caches and in-flight coalescing. `prefetch.py` warms a selected identity, its compact coauthor summary and its first literature page under a bounded queue. It cannot start a catalogue crawl.

`deep_search.py` owns each query's in-memory SQLite evidence, visited frontiers, page cursors, candidate validation and exactness state. `discovery.py` provides a compact navigation graph from coauthor-summary IDs. Summary counts are retrieval hints; all displayed coauthor edges require qualifying paper records. Small historical navigation hints are also reverified against current sources.

`search_jobs.py` keeps each SQLite session on its owning worker. It manages continuation, cancellation, expiry, recent-query reuse and bounded result retention. New requests never move a SQLite connection across worker threads. Browser session storage contains a small job handle and query settings, not a local literature database.

`pipeline.py` normalizes only selected public fields, stable IDs, roles, dates, work deduplication and explicit doctoral evidence. `identity_guard.py` withholds contradictory authorship or doctoral links while preserving raw records and audit reasons. `historical.py` contains only narrowly reviewed, explicitly sourced historical supplements and exclusions.

`graph.py` uses author–paper incidence rather than materializing a clique for every large paper. Filters select eligible distinct works, then shared-work counts establish undirected researcher pairs. Each pair costs one hop. Doctoral metadata shares a coauthor pair; a permitted genealogy-only relationship adds one distinct hop.

## Saved source

The fixed JSON snapshot is immutable by version. Saved graph and centrality calculations use a cache keyed by snapshot version and every graph filter. The browser cannot launch the optional persistent importer. The frozen test-source fixture is independent of the production normalizer and replaces a clean clone's dependency on a local database.

## Boundaries

Live coverage is always partial. An exact local graph algorithm does not establish a global catalogue distance. Direct and proven two-hop results have explicit proof conditions; deeper results remain verified while continuation seeks improvement. API outages, truncation, identity uncertainty and resource limits remain visible.

The default listener is loopback. Public service hosting would require separate operational controls; publishing the source repository does not deploy the application. See [security review](SECURITY_REVIEW.md) and [API/storage limits](ON_DEMAND.md).
