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

## 10. Model routing

## 11. Remaining bottlenecks

## 12. Git
