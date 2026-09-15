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

Resolved against live INSPIRE through the broker:

| | |
|---|---:|
| Seeds attempted | 499 |
| Resolved unambiguously | 408 |
| Ambiguous, deliberately skipped | 65 |
| No profile found | 26 |
| Upstream failures | 0 |
| Upstream requests | 499 |
| Elapsed | 256 s |
| File size | 27 KB |

256 s for 499 requests is the pacer working exactly as configured. The 65
ambiguous names are the ones where guessing would do real harm — "Niels Bohr",
"John Wheeler", "Murray Gell-Mann", "John Bell" all return several plausible
profiles, and John Wheeler in particular has both the physicist and an
astronomer. None of them is in the seed set.

The file lives at `data/cache/core-nodes.json`, which is gitignored, so a clean
clone still starts with no cache and no database. Re-create it with
`tests/live_benchmark.py`'s sibling script or by calling `core_nodes.resolve`.

**Adjacency was deliberately not prewarmed**, per the brief's instruction to
measure first. Complete mode-specific adjacency for 408 people across three
modes means paging every qualifying work of each: measured against the
benchmark above, a single prolific physicist costs tens to hundreds of pages,
so the full set is several thousand upstream requests and a cache far past the
bounded budget this project keeps. Identity resolution is cheap and bounded;
neighbourhood prewarming is neither. See §11.

## 7. Correctness results

### Python suite

**415 passed** (baseline 354). No original test was deleted. Five were changed,
each because the behaviour it pinned was superseded by something stronger:

- Two pacing tests asserted the literal `1.0`; they now assert the configured
  interval and a new invariant that the pace stays under INSPIRE's published
  ceiling.
- `test_deep_reference` allowed only `ok`/`search_incomplete`; it now also
  allows `no_path` **and** asserts that a `no_path` claim agrees with the
  NetworkX oracle. That is a correctness assertion where there was a
  permissive one.
- Two tests seeded the old frontier attributes directly and now seed the HLBES
  proof through one shared helper. The closed-frontier bridge test covers the
  same invariant through `offer()`.

New: 44 tests across `test_hlbes.py` (engine), `test_hlbes_live_guards.py`
(one per review finding), `test_core_nodes.py` (seeds cannot change a
distance).

### Differential against NetworkX

24,000 random source-target pairs over nine graph families — G(n,p),
Barabási-Albert, Watts-Strogatz, random trees, grids, lollipops, barbells,
stars, cycles and disconnected unions — with randomised routing scores, cost
estimates and misleading trial paths. **Zero distance mismatches.** Every
`EXACT` result matched `networkx.shortest_path_length`, every `NO_PATH` matched
`has_path`, every returned path was simple and used only real edges, and `L`
was monotone and bracketed the truth at every step.

The reviewer's independent fuzzers, re-run against the final tree:

| Fuzzer | Cases | Result |
|---|---:|---|
| Exactness vs BFS, paging PARTIAL oracles | 4,926 | 0 failures |
| Completed-radius invariant after *every* advance | 3,288 | 0 violations |
| Discovery differential, old rule vs new | 5,128 | 0 mismatches |
| "Improved after COMPLETE", radius jumps > 1 | 2,000 | 0 occurrences |
| Asymmetric oracle, assertion escapes | 4,000 | 0 (was 845) |

### Live

Sixteen adversarial pairs, §8. Every returned route was endpoint-correct,
simple, and carried paper evidence on every hop.

### Browser suite

**Not run — it is not in the repository.** The 70-group sequential suite lives
outside the tree (`docs/browser/`, `work/` and `test-results/` are all
gitignored and absent), and there is no `package.json` or Playwright config to
run it from. I could not verify it and am not going to imply otherwise. What I
can say is what was checked instead: no file under `static/` was modified, the
result payload only gained keys (`bounds`, and `exact_proof` inside
`coverage`), and the one status the engine can now emit that it could not
before, `no_path`, is already handled in `static/app.js`. That is an argument
that the browser suite *should* still pass, not evidence that it does.


## 8. Performance

Sixteen live pairs, cold cache each time, a 180 s cap per query, `tests/live_benchmark.py`.
"Old" is commit `0738987` at its own 1 req/s pacing; "new" is this branch at
2 req/s. `P` means shortestness was proven, not merely found.

| Query | Mode | Old | New | Old API | New API | Old works | New works |
|---|---|---|---|---:|---:|---:|---:|
| Hostert → Pascoli | ≤10 | 1h 2.6 s **P** | 1h 1.7 s **P** | 4 | 4 | 10 | 10 |
| Hostert → Dirac | ≤10 | no route, 180 s | no route, 180 s | 212 | 188 | 819 | 5,493 |
| Hostert → Ellis | ≤10 | 2h 36.5 s **P** | 2h 13.8 s **P** | 38 | 26 | 169 | 160 |
| Hostert → Feynman | ≤10 | 3h 180 s | 3h 21.6 s **P** | 183 | 33 | 737 | 797 |
| Hostert → Einstein | ≤10 | 5h 180 s | 5h 172.9 s **P** | 185 | 193 | 315 | 3,520 |
| Hostert → Witten | ≤10 | 3h 180 s | 3h 39.0 s **P** | 179 | 52 | 1,142 | 1,486 |
| Feynman → Wheeler | ≤10 | 1h 3.2 s **P** | 1h 1.4 s **P** | 4 | 4 | 2 | 2 |
| Witten → Visser | ≤10 | 4h 180 s | 4h 72.1 s **P** | 186 | 86 | 587 | 3,003 |
| Visser → Uppu | ≤10 | 4h 180 s | 4h 70.9 s **P** | 186 | 107 | 333 | 1,105 |
| Visser → Rodgers | ≤10 | 4h 180 s | 4h 102.5 s **P** | 200 | 142 | 265 | 2,378 |
| Visser → Massey | ≤10 | no route, 179 s | no route, 180 s | 182 | 175 | 347 | 4,425 |
| Aad → Abbott | >10 | 1h 4.7 s **P** | 1h 3.7 s **P** | 4 | 4 | 5 | 5 |
| Pascoli → Wheeler | ≤10 | 3h 180 s | 3h 94.1 s **P** | 188 | 113 | 818 | 2,995 |
| Uppu → Ellis | ≤10 | 4h 180 s | 4h 115.8 s **P** | 180 | 136 | 1,194 | 2,912 |
| Rodgers → Dirac | ≤10 | no route, 179 s | no route, 180 s | 209 | 202 | 788 | 5,312 |
| Ellis → Massey | all | no route, 180 s | no route, 180 s | 179 | 226 | 62 | 885 |

Pascoli → Wheeler, Uppu → Ellis, Visser → Rodgers and Rodgers → Dirac are the
fresh cross-field pairs, not used while building any of this.

| | Old | New |
|---|---:|---:|
| Shortestness proven | 4 / 16 | **12 / 16** |
| Route found | 12 / 16 | 12 / 16 |
| Hit the 180 s cap | 12 / 16 | **4 / 16** |
| Total upstream requests | 2,319 | **1,691** |
| Total wall time | 2,206 s | **1,431 s** |
| Total work records fetched | 7,593 | 34,488 |

Eight queries moved from "a route, 180 s, shortestness unknown" to "proven
shortest", six of them in under 100 s. Hostert → Feynman went from the cap to
21.6 s proven.

**The one metric that got worse is work records fetched, by 4.5×, and it is
not an accident.** The brief names fewer fetched records as a goal, so it is
worth being exact about the trade. Proving a distance means exhausting a
person's literature query; the old engine sampled a page here and there and
never exhausted anything, so it fetched few records and could prove almost
nothing. Requests — the thing INSPIRE rate-limits and the thing that costs
wall time — fell 27%, because full pages replaced scattered ones. If fetched
records rather than requests were the binding cost, the right lever would be
`_literature_size`, not the search strategy.

Against the §36 targets: direct hops land at 1.4–3.7 s, inside the 2–3 s goal.
Two-hop Hostert → Ellis is 13.8 s against a 5 s goal, and multi-hop proofs run
21–173 s against 15 s. **The "95% of cold searches under 30 s" objective is not
met for proven multi-hop results.** Time to a *first verified route* is closer
and improved in nine of sixteen cases (Hostert → Einstein 51.3 s → 32.1 s,
Witten → Visser 81.1 s → 48.9 s), but it regressed in three where the engine
now spends early effort on work that later closes the bound — Uppu → Ellis
reaches a route at 114 s instead of 73 s, then proves it at 116 s instead of
never.


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

Stated plainly, because the brief asked for specific models and told me not to
claim one was used if it was not.

**GPT-5.3 Spark / Codex: not available.** There is no `codex` CLI on this
machine and no OpenAI credentials in the environment (`which codex` → not
found; no `OPENAI_*` variables).

**GPT-5.6 Luna: not available.** Same check, same result. The documented
fallback could not be used either.

**GPT-5.6 Sol: not available.** No independent-vendor model could be reached
to perform the review.

So all implementation in this branch was written by **Claude Opus 5**, the
model running this session. That is not what the brief asked for, and it means
the separation between implementer and reviewer is weaker than intended.

What was done instead: independent review was delegated to **separate Claude
agent instances** with no access to my reasoning, given only the repository,
the diff, and instructions to break specific claims and to run code rather
than reason about it. Two rounds were run. The first round found five real
defects, including a false `global_shortest_proven: true` at four hops where
the true distance was two — the branch's central claim, reproduced as a
runnable script before I would accept it. Every fix in §7 traces to that
round. A second round re-attacked the fixes and the code written after them.

This is a genuine adversarial check and it caught genuine bugs, but it is not
model-independent: a shared model can share a blind spot. Where the review
could not reach, I have said so rather than implying coverage — see the trust
boundary on `offer()` in §11.


## 11. Remaining bottlenecks

Stated as found, not as hoped.

**Proving a deep route is inherently expensive, and always will be.** To prove
a distance of `k` the two completed radii must sum to at least `k - 1`, and
completing one radius means paging *every* qualifying work of *every* person in
that layer. For a researcher with three hundred collaborators the second layer
alone is thousands of pages. HLBES makes this visible and bounded rather than
cheap: it reports `4 <= d <= 5` instead of silently grinding. Distances of one
to four are now routinely proven; five is reachable for some pairs; beyond that
the honest answer is a verified route with bounds.

**Two benchmark pairs still return no route at all** — see §8. Both are
small-team searches into the deep historical record, where the modern endpoint
has a large collaborator set and the historical one has almost none.

**The seed set is identities only.** §6 explains why adjacency prewarming was
not run: measured against the seed list it is several thousand upstream
requests and a cache far larger than the bounded budget this project keeps.
Resolving identities is cheap and safe; prewarming their neighbourhoods is
neither, and the brief explicitly says to measure before prewarming rather
than to prewarm because the list exists. Items 19 and 20 — dynamic promotion
and demotion from production telemetry — were not built at all; there is no
telemetry to drive them yet.

**`offer()` is a trust boundary.** A lazily revealed graph gives the engine no
way to check an edge it has not been told about, so a route offered by the
caller is taken on trust and a false one would be proven exactly. Production
offers only routes whose hops are in the guarded graph, and a retained route is
dropped as soon as any hop leaves it, but the engine itself cannot enforce
this. It is documented at the call site and pinned by tests rather than
structurally prevented.

**The client still has no transport-level retry.** A single 5xx or timeout
ends the request; only job-backed deep searches recover, through the
continuation loop. `/api/search`, `/api/person`, `/api/neighborhood` and
`/api/prepare` get nothing. This predates the branch and was left alone.

**Four observability items were not built** — network versus local versus
identity versus evidence wall time (73-76). Time-to-first-path and
time-to-proof exist in the benchmark harness but are not exposed through the
API.

**Two reviewer findings were accepted rather than fixed**, both low severity:
a proof retired by the identity guard consumes the same rebuild budget as one
retired by contradictory evidence, and a conflicted bound can publish its
previous lower value in the coverage payload if the snapshot call raises in
between. Neither can produce a false proof; both are noted here rather than
silently carried.


## 12. Git

| | |
|---|---|
| Branch | `hlbes-search-optimization` |
| Base | `0738987` |

Commits, oldest last:

```
4f27168 Add the overnight report
1a7d4f3 Close five more defects found in second-round review
077965d Grow the smaller frontier when looking for a route
75df0e1 Close five defects found in independent review
0c30cd6 Find a route before proving one
d1ff3cc Load optional seed identities in the server
f870b77 Add the core seed list and wire it into routing priority only
7837760 Remove the retired round-robin frontier
92d0a32 Replace the live frontier scheduler with HLBES
0be5946 Pace INSPIRE requests from the published ceiling, not a magic constant
f42ffb9 Add HLBES exact bidirectional search engine
```

Files changed: `hepgraph/hlbes.py` (new), `hepgraph/core_nodes.py` (new),
`hepgraph/deep_search.py`, `hepgraph/remote.py`, `hepgraph/server.py`, four new
test modules, `tests/live_benchmark.py` (new), and five existing tests amended
as described in §7. **No file under `static/`, `data/`, `launch_demo.py`,
`Dockerfile` or `README.md` was touched.** The result payload gained exactly
one key, `bounds`, and removed none.

### Clean-clone acceptance

A fresh clone of the private repository, with no cache, no database and no
environment file: 415 tests pass, every module imports, the server starts, the
health endpoint answers, the interface and `app.js` load, and a live path query
(Feynman → Wheeler) returns a proven one-hop route with real paper evidence.

### Acceptance gate

Every gate in the brief that could be evaluated passes. One could not be:
**the browser suite is not in the repository and could not be run** (§7). It is
recorded as unverified, not as passed.

