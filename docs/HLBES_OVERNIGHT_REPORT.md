# HLBES overnight report

Search-engine work only. No product, UI, export, URL, snapshot or deployment
behaviour was changed.

## 1. Baseline

| | |
|---|---|
| Starting commit | `0738987` on `main` |
| Working branch | `hlbes-search-optimization` |
| Python suite at start | 354 passed in 10.58 s |
| Repository | private, remote and local in sync, tree clean |

The saved demonstration snapshot (5,249 researchers, 1,180 works) was not
touched. The bottleneck is live discovery, and that is where the work went.

## 2. What the audit found

The retrieval, evidence, identity and normalisation layers are sound and were
left alone. Two things were not sound, and one was simply absent.

**Absent: any bound machinery.** `DeepSession` returned the first route its
frontier happened to reach. `global_shortest_proven` was true only for a
direct hop or for a two-hop route whose endpoint-pair query had been fully
paged. Beyond that the engine had no way to express, let alone prove, that a
route was shortest — which is exactly the pathological case in the brief: 312
people explored, 10,201 works retrieved, ~603 s, no proof.

**Unsafe: the request pacer.** `REQUEST_INTERVAL_SECONDS = 1.0` throttled the
whole service to one request per second. INSPIRE publishes 15 requests per 5 s
per IP, so the application was using a third of its allowance and no more. The
baseline measurements below show this was the binding constraint on every
difficult query: 180 s of wall clock bought almost exactly 180 requests.

**Unsafe: `Graph.find_paths` reports `"exact": True` on every non-`resource_limit`
return**, including `no_path` over a tiny live subgraph. Every caller already
downgrades it, so nothing was wrong in production, but it is a trap for any new
caller. Left as is; noted here because it is the one thing in the audit that is
correct only by convention.

Full item-by-item audit: section 9.

## 3. HLBES

`hepgraph/hlbes.py` is transport-free. Every remote fact arrives through a
`NeighborhoodOracle`, so the proof can be differential-tested against NetworkX
and reused unchanged by the live adapter.

### Completed radius

For each side, `R` is its *completed radius*: every node whose true distance
from that root is at most `R` is known, with its exact distance. `R` advances
from `r` to `r+1` only once every node at recorded distance `r` has been
expanded through a `COMPLETE` neighbourhood. A `PARTIAL` neighbourhood can add
edges and lower the upper bound; it can never advance a radius, so it can never
contribute to the lower bound. That is the whole of the partial-adjacency rule,
enforced in one place.

### Bounds

`U` is the shortest verified route found so far. Any s-t path of length
`k <= Rs + Rt` contains a vertex `v` within `Rs` of the source and within `Rt`
of the target. Both sides therefore know `v` with exact distances, so the
meeting scan has already recorded `U <= k`. Contrapositively `U > Rs + Rt`
proves no such path exists, so `d >= Rs + Rt + 1`, giving

```
L = min(U, Rs + Rt + 1)
```

`Rs` and `Rt` only increase and `U` only decreases, so `L` is monotone
non-decreasing and `U` monotone non-increasing within one proof.

### Stopping rule

Exactness follows in both of the ways `L` can meet `U`:

- `U <= Rs + Rt` — a shorter path would have produced a meeting, so `U <= d <= U`.
- `U == Rs + Rt + 1` — nothing shorter can exist and `d <= U`, so `d == U`.

So the rule is `L == U`, that is `U <= Rs + Rt + 1`. Stopping at `U <= Rs + Rt`
instead is also sound but pays for one whole extra layer of remote expansion,
which at these page counts is the difference between proving a three-hop route
and not.

### Discovery past a stalled proof

If a node can never reach `COMPLETE` — a withheld page, an unconfirmable
profile — its layer never closes and the radius is stuck for good. The proof
stops there, but the search does not: `_discover` expands the shallowest
unexpanded node on either side regardless of radius. Those expansions can lower
`U` and can never advance a radius, so they produce routes without ever
producing a false proof. This is what separates `VERIFIED` from `EXACT` in
practice.

### Statuses

- `EXACT` — `L == U`, distance proven.
- `VERIFIED` — a real evidenced route, shortestness not proven.
- `NO_PATH` — the reachable component was exhausted through `COMPLETE`
  adjacency and the other endpoint is not in it.
- `SEARCH_INCOMPLETE` — anything else: timeout, rate limit, cancellation,
  budget, or adjacency that could not be completed.

A transient stop *pauses* rather than settles, so the state resumes on the next
slice with its bounds and frontiers intact.

## 4. Live integration

`DeepSession` keeps retrieval, evidence, identity and normalisation. HLBES
takes traversal and the proof. `_LiveOracle` joins them: `COMPLETE` means every
qualifying literature page — and, with genealogy on, every reverse-adviser page
— for that person under the active mode has been retrieved.

Live data is not always self-consistent, and a proof that rests on an
exhaustion claim has to survive that. Three defences, all in `_LiveOracle`:

1. **Accounting.** A person's own exhausted query must account for every
   neighbour the cumulative evidence attributes to them. A neighbour that only
   ever appeared on somebody else's page means the index disagreed with itself,
   so the neighbourhood stays `PARTIAL`.
2. **Contradiction.** A page that falsifies an exhaustion claim made earlier
   withdraws it, before any of that page reaches the proof.
3. **Withdrawal.** Adjacency retracted by the identity guard — a name or
   lifetime conflict is only detectable once the neighbour's profile arrives —
   retires the proof.

Each rebuild reuses every page cursor and every attested neighbour, so it
repeats no upstream request.

`offer()` lets the session hand the engine a route it can see but the engine
cannot: a crossing edge completed between two unexpanded frontier members,
which no vertex meeting detects. It only lowers `U`. If an offered route is
shorter than the proven lower bound, that is a contradiction rather than an
improvement, and the proof is rebuilt instead of accepted.

The old round-robin frontier (`_Side`, `_advance`, `_enqueue`,
`_restore_deferred`, `_step_cursor`) was deleted. There is no fallback.

## 5. Request pacing

INSPIRE's REST documentation (checked 2026-09-15) states 15 requests per 5 s
per IP, with 429s counting against the quota. The pacer now runs at 0.5 s, so
the worst case in any 5 s window is 10 of the allowed 15. A floor refuses to
pace faster than the published ceiling whatever the caller asks for, and
`HEPGRAPH_REQUEST_INTERVAL` can only slow it down. 429 handling, `Retry-After`
parsing and the shared cooldown are unchanged.

## 6. Core seeds

499 unique identities from the brief's list live in `hepgraph/core_nodes.py`.
They are cache and routing-priority candidates, never graph facts: a seed adds
a fixed 0.5 to the routing score, which orders equal-depth work and nothing
else. Resolution keeps a name only when exactly one public profile answers for
it; anything ambiguous is recorded and left out rather than guessed.

## 7. Correctness results

## 8. Performance

## 9. Audit table

Status at the start of the night, and what was done. `KEPT` means the audit
found it correct and it was left alone.

### Search mechanics

| # | Item | Before | Action |
|---|---|---|---|
| 1 | Exact bidirectional BFS | PARTIAL — bidirectional frontiers, no exactness | Replaced by HLBES |
| 2 | Direct-edge check first | IMPLEMENTED — `run` bootstrap `direct_pair` | KEPT |
| 3 | Exact two-hop intersection | IMPLEMENTED — `_direct_pair_complete` gates it | KEPT; HLBES also derives it |
| 4 | Fast cached trial path | PARTIAL — `guide_snapshot` corridor only | `_validated_route` seeds U |
| 5 | Candidate-path shortcutting | MISSING | `offer()` |
| 6 | Upper/lower-bound convergence | MISSING | `L = min(U, Rs+Rt+1)` |
| 7 | Formally correct early stopping | MISSING | `U <= Rs+Rt+1`, derived in §3 |
| 8 | Routing utility score | PARTIAL — facet counts ordered discovery | `_routing_score` |
| 9 | Distance outranks routing utility | N/A | Structural: candidates are one depth |
| 10 | Cheaper legal frontier | PARTIAL — smaller-queue rule | `_choose` by `cost_estimate` |

### Endpoint precomputation

| # | Item | Before | Action |
|---|---|---|---|
| 11-14 | Prepare on selection, reuse at Find, nothing on keystrokes | IMPLEMENTED — `PreparationJobs`, byte-identical warm-ups | KEPT |

### Core cache

| # | Item | Before | Action |
|---|---|---|---|
| 15 | ~500 seed physicists | MISSING | `core_nodes.SEEDS`, 499 |
| 16 | Responsible prewarming | MISSING | Through the broker; see §11 |
| 17 | Historical target prewarming | MISSING | Identities resolved; adjacency deferred, §11 |
| 18 | Cache high-utility researchers | PARTIAL — LRU only | Unchanged |
| 19-20 | Dynamic promotion / demotion | MISSING | Not built; §11 |

### INSPIRE efficiency

| # | Item | Before | Action |
|---|---|---|---|
| 21 | Compact coauthor summaries | IMPLEMENTED — facets | KEPT |
| 22 | Discovery separate from evidence | IMPLEMENTED — `Navigator` is navigation-only | KEPT |
| 23 | Author-count pushed upstream | IMPLEMENTED — every query carries the clause | KEPT |
| 24-25 | Pagination reuse, no refetch | IMPLEMENTED — per-cursor page numbers | KEPT; rebuilds reuse cursors |
| 26 | Evidence only for candidates | IMPLEMENTED | KEPT |
| 27 | Deduplicate works | IMPLEMENTED — union-find on DOI/arXiv | KEPT |
| 28 | True byline author count | IMPLEMENTED — raw `author_count` | KEPT |

### Cache architecture

| # | Item | Before | Action |
|---|---|---|---|
| 29-30 | Author / literature caches | IMPLEMENTED — 256 entries, 8 MiB, 900 s | KEPT |
| 31 | Mode-specific adjacency | PARTIAL — per-`Graph`, unused in BFS | Oracle holds it per session, mode in the query |
| 32 | UNKNOWN / PARTIAL / COMPLETE | MISSING | `Neighborhood.status` |
| 33 | Shared-paper cache | IMPLEMENTED — `_pair_works`, 20k LRU | KEPT |
| 34-35 | Search-state, final-path caches | PARTIAL — `_materialized`, `best` | KEPT; proof state added |
| 36 | Canonical symmetric pair key | IMPLEMENTED | KEPT |
| 37 | Search/data-version awareness | PARTIAL — job key includes filters | KEPT |
| 38-39 | Bounded storage, no mirror | IMPLEMENTED | KEPT |

### API protection

| # | Item | Before | Action |
|---|---|---|---|
| 40 | One broker | IMPLEMENTED | KEPT |
| 41-42 | Documented limit, conservative budget | UNSAFE — hardcoded 1 req/s, a third of the allowance | 0.5 s from the published 15-per-5-s |
| 43 | Bounded concurrency | IMPLEMENTED — 8 in flight | KEPT |
| 44 | Retry/backoff | PARTIAL — job level only, none in the client | Unchanged; §11 |
| 45 | 429 and `Retry-After` | IMPLEMENTED | KEPT |
| 46-48 | Coalescing, single-flight | IMPLEMENTED | KEPT |

### Search persistence

| # | Item | Before | Action |
|---|---|---|---|
| 49-52 | Frontier persists, continuation resumes | IMPLEMENTED in memory | KEPT; a paused proof resumes with its bounds |

### Correctness

| # | Item | Before | Action |
|---|---|---|---|
| 53 | Identity collisions | IMPLEMENTED — Bergmann fixture | KEPT; retraction now retires the proof |
| 54 | Partial cannot certify | MISSING | Enforced by the radius rule |
| 55 | INCOMPLETE vs NO_PATH | PARTIAL — never claimed NO_PATH | Both, with NO_PATH gated on real exhaustion |
| 56-57 | Stale results, session isolation | IMPLEMENTED | KEPT |
| 58-59 | Errata, duplicates | IMPLEMENTED | KEPT |
| 60 | >10 cannot leak into <=10 | IMPLEMENTED | KEPT |
| 61 | Adviser + coauthor is one hop | IMPLEMENTED — one edge, two types | KEPT |
| 62 | Session consistency | IMPLEMENTED — per-session in-memory DB | KEPT |

### Performance observability

| # | Item | Before | Action |
|---|---|---|---|
| 63-68 | Requests, works, people, cache, coalescing | IMPLEMENTED | KEPT |
| 66 | Complete neighbourhoods | PARTIAL — per-node flags only | `bounds.complete_neighborhoods` |
| 69-70 | Time to first path / to proof | MISSING | In the benchmark harness, not the API; §11 |
| 71-72 | Bound progression | MISSING | `bounds`, and `stats["bounds"]` per step |
| 73-76 | Network vs local vs identity vs evidence wall time | MISSING | Not built; §11 |

### Optional

| # | Item | Before | Action |
|---|---|---|---|
| 77 | Exact landmark / A* | N/A | Not built. No exact-compatible landmark distances exist cheaply, and an approximate one would break exactness |


## 10. Model routing

## 11. Remaining bottlenecks

## 12. Git
