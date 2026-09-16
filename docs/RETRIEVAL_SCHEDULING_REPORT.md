# Retrieval scheduling and batched neighbourhoods — Phase V

## 1. Starting state

| | |
|---|---|
| `main` at start | `9b2abb4` (Phase IV merged and reported), production serving `7b0bf88` |
| Python suite | 480 passed, 1 xfailed |
| Branch | `retrieval-scheduling` |

This phase implements the parts of an external audit (Codex) that were
correct, after measuring each claim first. The audit's own ordering —
batching, then streaming, then browser-side state — was not followed
blindly: measurement moved streaming off the list and put a hotspot the
audit had not seen at the top.

## 2. Measure first

### 2.1 Slice boundaries cost nothing in process

The audit attributed the local HTTP gap (19.5 s vs 8.8 s to a first route,
Phase III) to the five-second request slices and proposed one streaming
request instead. In process, Erin Visser → Hostert:

| Run | First route | Proven | Requests |
|---|---:|---:|---:|
| one continuous 120 s run | 8.6 s | 18.5 s | 30 |
| back-to-back 5 s slices | 8.8 s | 18.3 s | 30 |

The slice boundary itself is free. A profile of the sliced run is 17.6 s of
17.7 s inside `urllib` waiting on INSPIRE. Streaming would remove nothing
measurable from the engine; whatever the HTTP layer adds (~30 % locally in
Phase IV's numbers) is in `SearchJobs`, not in slicing. Not built.

### 2.2 The hotspot the audit missed: rebuilding the guarded snapshot

Production Hostert → Uppu (Phase IV, 273 requests) took 729 s against 278 s
locally, and each 5 s poll performed only 2–3 requests. A profiled 273-request
run in process:

| | seconds |
|---|---:|
| total (with profiler) | 492 |
| waiting on INSPIRE (`_ssl` read) | 167 |
| `DeepSession._snapshot` | 319 |
| of which `apply_identity_guard` (187 rebuilds) | 223 |
| of which name helpers (`_normal` ×70,933,925 calls) | 106 |

The live search invalidates its materialised snapshot after every retrieved
page and rebuilds it — pipeline normalisation, historical overlay, identity
guard, `Graph()` — before the next neighbourhood is read, and then hashes the
whole snapshot on every one of ~5 `_snapshot` calls per page to name its
version. The guard re-derived every byline/profile comparison from scratch
each time. On a long search CPU was twice the network time. Phase III had
profiled a 30-request search, found HLBES CPU rounding to zero, and stopped
there; that remains true of HLBES and was never true of the rebuild.

## 3. What changed

### 3.1 Identity guard: memoised pure helpers (`03f9fbe`)

Every name helper (`_normal`, `_words`, `_given_words`, `_given_initials`,
`_given_tokens`, `_comma_name`, `_profile_initials`, `_profile_given_tokens`,
`_explicit_profile_surname`, `_incompatible_full_given_forms`) and the three
conflict checks are pure functions of their string arguments; they are cached
(`functools.lru_cache`, 2¹⁸ entries, unhashable arguments fall back to the
plain call). The occurrence table is read once per guard run instead of once
per work. Results are byte-identical; the guard's suite, the real-collision
fixtures and the D6 `xfail` stand.

Measured on the same 5-second-slice Hostert → Uppu run: 492 s → 308 s
(per-request wall 1.8 s → 0.95 s); `_snapshot` 319 s → 126 s.

### 3.2 Snapshot rebuild without table writes, copies or repeated hashes (`af32691`)

`build_snapshot(persist=False, version=False)`, `apply_historical(copy_input=False,
version=False)`, `apply_identity_guard(copy_input=False, version=False)` for
the live path only: no `works`/`people` table rewrite per rebuild, no two
deep copies, no three intermediate content hashes. `_snapshot` hashes the
evidence once per materialisation and combines that digest with the call's
live coverage — the version is still a function of exactly what the returned
`Graph` received. The saved-snapshot pipeline keeps its defaults.

### 3.3 HLBES ordering (`4b7271c`, reviewed)

Ordering only; none of this can change a distance.

| Finding (audit) | Change |
|---|---|
| `_choose` ranked a side by its cheapest pending node but expanded its highest-scoring one | a side is ranked by the **sum** of the estimated cost of its whole pending layer (the layer must be read entirely to advance the radius) and the cheapest node in it is read first, routing score breaking ties |
| breadth discovery ranked sides by all open nodes | by the people at the side's shallowest open depth — its next layer |
| the meeting scan repeated a full intersection after every expansion | only nodes whose distance was just set or lowered are checked; provably and empirically (5,000 driven + 2,500 forced-lowering differential runs by the independent reviewer) identical bounds at every decision point |
| `_retrieval_cost` was the constant 4/2/1/1 model | remaining pages from the cursor's reported total, page size and distinct records received, plus the empty page that ends a floor or moving count |

One fixture (`test_cycles_do_not_repeat_nodes_and_sliced_continuation_keeps_ram_evidence`)
asserted the three-hop route the old order happened to find first; the
fixture's true shortest route is two hops and the test now says so.

### 3.4 Guide corridor: instrumented, and it yields (`4b7271c`, `af32691`)

`coverage.guide = {requests, routes_found, first_route, yielded, request_budget}`.
A corridor that has spent `GUIDE_REQUEST_BUDGET = 24` requests without
producing a route is cleared and stays cleared (the reviewer found the first
version was refilled one request at a time by later discoveries). Its worth
is now a number in every result rather than an assumption; §4 reports it.

### 3.5 Batched exact neighbourhoods (`dda87c6`, `aaa94a4`, `8188476`)

When HLBES asks for a person whose literature paging has not started, in
small- or medium-team mode, the oracle forms a union of that person and up to
seven others **on the same side at the same depth** in the same state and pages
`(authors.record.$ref:A OR …) AND author_count:…` instead. Exactness rules,
all tested:

- records are stored exactly as individual pages are; a member owns the union
  records that name them (`member_seen[m]`);
- **attestation** — what `_accounted` checks a person's coauthors against —
  comes only from union records naming **no other member**, which the union
  can only have returned through that member's own index term. An OR query
  cannot say which member's term returned a record naming two members, and
  crediting it to both would disable the index-disagreement canary (§5.2);
- a member is certified exhausted only when the **whole union** is read to
  exhaustion under `_page_done`'s rules (exact, stable total; every distinct
  record arrived; window not exceeded) **and** every coauthor the graph gives
  them is in their own attestation. Otherwise the member detaches and reads
  their own query from page one — exactly what would have happened without
  batching; `literature_short`, `literature_unreadable`, `literature_window`
  are inherited, never hidden;
- if the union's total is a floor count or cannot be read inside INSPIRE's
  10,000-result window, nobody is certified from it: members detach (`solo`,
  so the same over-window union cannot re-form) and the page already read
  stays as evidence;
- people who already co-occur on a known record are not batched together (a
  root's coauthors all sit on the root's papers); such a union would only
  detach again and spend its pages for nothing;
- every union page advances every live member's token, so HLBES never parks
  a member whose union is still paging; a retired member is not re-attested;
  a person both sides know is batched with the side reading them;
  reverse-adviser pages, the direct-pair probe, guide pairs and profile
  hydration are unchanged;
- a member's `_retrieval_cost` is its share of the union's remaining pages.

Consequence: the union saves requests for layers of people who do **not**
co-publish with one another — collaborators of one person met through
different papers, discovered at the same depth — and costs nothing where they
do, because it is not formed there. §4 measures how often that is on real
pairs.

Live differential (`tests/live_batched_diff.py`, pre-fix rule; per-author work
sets are unaffected by the attestation rule): Hostert 40/40, Pascoli 176/176,
Visser 3/3, Rodgers 56/56, Massey 0/0 — identical union vs alone; **5 pages
individually, 1 as a union**. Synthetic suite (`tests/test_batched_neighborhoods.py`,
23 tests): random co-publishing communities driven to the exact proof give
identical status/hops/proof and identical COMPLETE neighbour sets with and
without batching and never more requests; a star of unrelated coauthors on each
side is read in fewer requests; the reviewer's hidden-record corpus gives the
same three-hop proof both ways.

## 4. Measurements

### 4.1 Controlled A/B/C/D, in process, cold cache

Run by a benchmark agent on clean worktrees, one live process at a time, each
search as back-to-back 5-second slices (the shape the server drives), fresh
`RemoteClient` per run, no guide snapshot (so the guide corridor is not
exercised here — production has it; §4.2).

| Version | Commit | Contents |
|---|---|---|
| A | `9b2abb4` | what production ran when this phase started |
| B | `03f9fbe` | HLBES ordering, cursor cost model, guide instrumentation, identity-guard memoisation |
| C | `af32691` | B + batched unions (first rule) + cheap snapshot rebuilds |
| D | `8188476` | C with the canary-preserving union rule |

| Pair | Ver | First route | First hops | Proven | Hops | Requests | Lit. pages | Unions |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Witten → Ellis | A | 7.5 s | 2 | 7.5 s | 2 | 7 | 2 | – |
| | B | 7.7 s | 2 | 7.7 s | 2 | 7 | 2 | – |
| | C | 7.4 s | 2 | 7.4 s | 2 | 7 | 2 | 0 |
| | D | 7.1 s | 2 | 7.1 s | 2 | 7 | 2 | 0 |
| Visser → Hostert | A | **8.6 s** | 4 | 18.1 s | 4 | 30 | 12 | – |
| | B | 21.8 s | 4 | 21.8 s | 4 | 37 | 13 | – |
| | C | 22.9 s | 4 | 22.9 s | 4 | 36 | 12 | 2 |
| | D | 22.2 s | 4 | 22.2 s | 4 | 36 | 12 | 1 |
| Hostert → Feynman | A | 17.6 s | 3 | 17.7 s | 3 | 18 | 10 | – |
| | B | 11.9 s | 3 | 12.0 s | 3 | 14 | 7 | – |
| | C | 8.7 s | 3 | 8.7 s | 3 | 10 | 3 | 1 |
| | D | **7.9 s** | 3 | 7.9 s | 3 | 10 | 3 | 1 |
| Einstein → Dirac | A | 32.8 s | 5 | 32.8 s | 5 | 52 | 25 | – |
| | B | 28.6 s | 5 | 28.7 s | 5 | 49 | 23 | – |
| | C | 20.5 s | 5 | 20.5 s | 5 | 32 | 6 | 4 |
| | D | **20.6 s** | 5 | 20.6 s | 5 | 32 | 6 | 0 |
| Hostert → Uppu | A | 268.4 s | 5 | 272.3 s | 5 | 273 | 116 | – |
| | B | 240.0 s | 7 | 253.9 s | 5 | 325 | 117 | – |
| | C | 195.8 s | 7 | 204.0 s | 5 | 304 | 96 | 4 |
| | D | **212.0 s** | 7 | 222.4 s | 5 | 320 | 110 | 0 |

| Version | Requests | Literature pages | Wall |
|---|---:|---:|---:|
| A | 380 | 165 | 349 s |
| B | 432 | 162 | 324 s |
| C | 389 | 119 | 264 s |
| D | 405 | 133 | **280 s** |

Zero upstream failures in twenty runs. **Every pair's proven hop count is
identical across all four versions.** Routes are person-for-person identical
on four pairs; on Hostert → Uppu, A/B prove one five-hop route and C/D an
equally short different one (expansion order decides which of several
shortest routes is found first — expected).

Honest reading:

- **Wall: −20 % (A → D).** Almost all of it is the CPU work removed from the
  rebuild path (§3.1–3.2), not fewer requests.
- **Requests: +7 % (A → D).** The ordering changes are mixed: fewer on
  Hostert → Feynman (18 → 10) and Einstein → Dirac (52 → 32), more on
  Visser → Hostert (30 → 36) and Hostert → Uppu (273 → 320). Single cold
  runs against a live index; the ±10 % swings on the two long pairs are
  within what expansion-order changes do, and no version is uniformly better
  on requests.
- **Time to first route improved on four pairs and regressed on one.**
  Hostert → Feynman 17.6 → 7.9 s, Einstein → Dirac 32.8 → 20.6 s, Uppu
  268 → 212 s (a seven-hop verified route shown 10 s before the five-hop
  proof — progressive delivery at work). Visser → Hostert went the other way,
  8.6 → 22 s: the old order stumbled on a route early; the new one closes
  layers first and finds the four-hop route only when the proof does.
- **Batching under the exact rule saves essentially nothing on real pairs.**
  D formed no union at all on the two hardest pairs — the people HLBES reads
  at one depth mostly co-occur on records already known — and where unions
  formed (C) the request count was the same as without them on four pairs.
  The audit's "largest cold-search optimization" does not survive the
  requirement that exactness detection is unchanged; the code stays because
  it is proven neutral and it wins 4× on layers of unrelated people, but it
  is not a speed-up on the searches people actually run.


Which ordering change moved Visser → Hostert? Isolated in process (fresh
client each, keep-alive transport in place, same day):

| Pair | Variant | First route | Proven | Requests |
|---|---|---:|---:|---:|
| Visser → Hostert | current | 21.2 s | 21.2 s | 36 |
| | old breadth rank | 16.8 s | 21.1 s | 29 |
| | old `_choose` | 21.6 s | 21.6 s | 36 |
| | both old | 15.1 s | 19.1 s | 29 |
| Hostert → Feynman | current | 11.8 s | 11.8 s | 10 |
| | old breadth rank | 6.4 s | 6.8 s | 10 |
| Einstein → Dirac | current | 17.9 s | 17.9 s | 32 |
| | old breadth rank | 28.8 s | 28.8 s | 49 |

The `_choose` fix is neutral on requests. The breadth rank (frontier = the
side's shallowest open layer) costs 7 requests on Visser → Hostert and saves
17 on Einstein → Dirac, with Hostert → Feynman identical in requests (its
time difference is network variance on identical work). 78 requests against
88 over the three; kept, with the trade recorded here.

### 4.1a Time to first route is not always the proof

On Hostert → Uppu every post-A version shows a seven-hop verified route 10 s
before the five-hop proof, and the browser announces the shorter route when it
lands (Phase IV). On Visser → Hostert the new order finds no route until the
four-hop one, at 21 s; the old order stumbled on the same four-hop route at
8–15 s depending on the run. That is the one measured regression of this
phase in the metric that matters most to a waiting user.

### 4.2 Where the remaining time goes (D, Hostert → Uppu, profiled)

| | seconds | share |
|---|---:|---:|
| wall (profiler on) | 248 | |
| network total | 169 | 68 % |
| — reading responses (`SSL read`) | 85 | 34 % |
| — **TLS handshake** | 42 | 17 % |
| — **TCP connect** | 40 | 16 % |
| — DNS | 2 | |
| pacer sleep | 8 | 3 % |
| `_snapshot` (233 rebuilds of 2,659 calls) | 56 | 22 % |
| — `build_snapshot` | 32 | |
| — `apply_identity_guard` | 12 | |
| — `Graph()` | 4 | |

Half of the network time is **connection setup**: every one of 320 requests
opened its own DNS + TCP + TLS connection because the transport used
`urllib.request.urlopen` per call. That is the largest remaining item, it is
exactness-neutral, and it was not on the audit's list. §4.3.

### 4.3 Keep-alive transport

`231ccab`: `_KeepAliveTransport` replaces the per-call `urllib` opener. A
lock-protected per-host pool of `http.client.HTTPSConnection` (four idle, 60 s
idle age, expiry on borrow, no background thread); a connection is borrowed
for one request and returned only when its body was read completely and the
server did not answer `Connection: close`; on any failure it is closed. A
reused connection that fails before any response byte (`RemoteDisconnected`,
`BadStatusLine`, reset, broken pipe, `SSLError`) is retried once on a fresh
one with the remaining timeout — the post-freeze case on Vercel. Timeouts are
never retried. Non-2xx statuses, redirects included and never followed, raise
`urllib.error.HTTPError` with the response headers, so `_fetch_json` and the
429 `Retry-After` cooldown are unchanged; HTTPS only; body read capped at
`MAX_RESPONSE_BYTES + 1`. Counters in `cache_info()["transport"]`. 24 new
tests, five of them against a real local TLS server.

Twelve sequential live calls: one connection opened, eleven reused; cold call
743 ms, reused 221 ms before pacing.

| Hostert → Uppu, in process, 5 s slices | wall | requests | per request |
|---|---:|---:|---:|
| start of phase (`9b2abb4`) | 492 s | 273 | 1.80 s |
| guard memoised (`03f9fbe`) | 308 s | 325 | 0.95 s |
| + cheap rebuild + unions (`8188476`) | 248 s | 320 | 0.78 s |
| **+ keep-alive (`231ccab`)** | **201 s** | 320 | **0.63 s** |

(Wall with the profiler on; production build A measured 272 s without it.)
What is left in the profile: response reads 78 s, `_snapshot` 60 s (of which
`build_snapshot` 35 s, identity guard 13 s), pacer sleep ~8 s. An incremental
`build_snapshot` is the next item, not taken here.


### 4.4 Production

PRODUCTION_SECTION

## 5. Agent review

Implementation, correctness review and adversarial testing were done by
separate Claude Code agents (Claude Fable 5.1); no OpenAI model was involved.
Reviewers worked read-only against committed hashes in clean worktrees.

### 5.1 Scheduling commit `4b7271c`

No high-severity findings. Evidence gathered by the reviewer: a randomised
differential of the incremental meeting scan against the previous full
intersection over 5,000 driven runs (COMPLETE/PARTIAL/UNKNOWN oracles, random
scores and costs, random `offer()` calls) — identical expansion order, bounds
sequence, status, distance and path length in every run — plus 2,500 runs
driving `_expand` deeper-first to force the distance-lowering branch the live
driver never reaches (3,139 lowering events; identical again); 1,500 random
graphs with extreme costs/scores for starvation or false `NO_PATH` — none.

| # | Severity | Finding | Resolution |
|---|---|---|---|
| 1 | medium (test-only) | the commit shipped a test whose expectation was wrong (the proof closes before the target root is read) | already deleted in `ecb5600` |
| 2 | low | a guide corridor that yielded was refilled one request at a time by later discoveries | `_queue_guide_bridge` respects `guide_yielded` (`af32691`) |
| 3 | low | `guide_requests` under-counted profile requests when the pair fetch ended the slice | attributed before re-raising (`af32691`) |
| 4 | low | `_retrieval_cost` ignored a moving total | `exact=stable_total and stable` (`af32691`) |

### 5.2 Batched neighbourhoods `dda87c6`/`aaa94a4`

The reviewer confirmed the mechanics — pagination, detach, shrink, slicing,
token advancement, JSON accounting, one union per person, endpoints never
batched, `test_deep_reference` genuinely exercising unions — and found one
substantive defect:

| # | Severity | Finding | Resolution |
|---|---|---|---|
| 1 | **high (conditional)** | crediting a union record to every member it names disabled the index-disagreement canary: with two records hidden from one member's own index term, the union proved a **four-hop route exact where individual paging correctly found three** (`wrong_l_corpus`) | `8188476`: attest only from records naming no other member; members with unexplained coauthors are not certified and read their own query; people already co-occurring on a known record are not batched together; the reviewer's corpus is now `test_the_union_keeps_the_index_disagreement_canary` |
| 2 | low | `cursor.union` not released on exhaustion | released (`8188476`) |
| 3 | low | a retired member was re-attested by later union pages | only live members are attested (`8188476`) |
| 4 | low/medium | a person both sides know was batched with the left side regardless of which side was reading them | side with the person at its completed radius preferred (`8188476`) |
| 5 | low | every member of an over-window union becomes `solo`, including small ones | kept; noted |
| 6 | low | `literature_hits` double-counts a detached member's re-read page 1 | kept (same as shrinks; `works` is distinct) |
| 7 | low | a shrunk individual cursor becomes batchable again | kept; records already fetched remain evidence |

The reviewer's own assessment of #1 before the fix: the baseline is equally
exposed to a *single* hidden record in other configurations, so the union
removed a detector rather than creating a new failure class — but the rule
here is that exactness is never weakened, so the detector was restored rather
than documented away. The cost is that a union certifies only people who do
not co-publish with their same-layer companions; the exclusion rule keeps
unions from being formed where that is already known to be false.

### 5.3 Re-review of `8188476`

A fresh adversarial agent re-ran the previous reviewer's corpora against
`8188476` and added ten targeted ones (consistent-plus-hidden mixes,
three-member records, coauthor sets empty at exhaustion and gained later,
duplicate author refs, deeper non-member hidden records, `min_shared=2`,
genealogy, both-sides membership, retire-and-recreate) and a 40-seed fuzz with
15 % of works hidden from one author's index term.

**Verdict: the claim holds.** Union paging never certified a member that
individual paging would not; the `wrong_l_corpus` search gives three hops,
proven, at every page size in both modes; zero wrong exact claims against BFS
on the true adjacency; every union-certified member stays subject to `_audit`
withdrawal exactly like an individually certified one; solo detach never
parks; all-detach layers terminate; no union of one can form. The soundness
argument it confirmed: a record naming only one union member can only have
matched that member's term in an OR query, so a member's union attestation is
a subset of its own-term attestation, and both modes certify iff the graph's
coauthors are within it.

| # | Severity | Finding | Resolution |
|---|---|---|---|
| 1 | medium (cost) | when co-publication surfaces only through the union, every named member detaches and re-reads: worst case 2× a layer's requests; on random co-publishing corpora batching is neutral to +20 % requests, on the unrelated-layer star 4× cheaper | measured on real pairs in §4, which decides the default |
| 2 | low | dead `_oracle is None` branch at certification | removed |
| 3 | low (pre-existing, both modes) | the canary is coauthor-level, not record-level, under `min_shared=2` | noted; not introduced here |
| 4 | low | a union-certified cursor reported `literature_next_page: 1` | set to the union's next page |


### 5.4 Keep-alive transport `231ccab`

The independent review agent for this commit was terminated by an API session
limit before it began; the transport was therefore reviewed by the
coordinating agent (not independently), against the questions the agent had
been given: a connection is pooled only when `len(body) <= MAX_RESPONSE_BYTES`
and `response.isclosed()` and not `will_close`, so a truncated or undrained
body can never poison the next response; borrow and return are under one
lock and a connection is held by one request at a time; the stale retry
applies only to a reused connection, only before response bytes, never to
timeouts, and uses the remaining timeout; the retry is not re-paced (the
server never saw the failed request); redirects and other non-2xx statuses
surface as `HTTPError`; a fresh-connection failure is reported at once. No
defect found. The 24 tests, including five over a real local TLS server,
cover each of those paths.

## 6. Not built, and why

| Audit item | Decision |
|---|---|
| One streaming search request | §2.1: slice boundaries cost nothing in process; the Vercel gap was CPU per request (§2.2), now removed at source. Streaming would also trade the request-driven design's resumability for one long connection on a 300 s function cap. |
| Web Worker + IndexedDB evidence cache | The app deliberately keeps author and paper records in server memory only and stores nothing but a job handle in the browser; persisting sanitised INSPIRE records on users' machines is a product decision, not a performance one, and the audit itself placed it after measurement. |
| Direct browser → INSPIRE | Audit placed it last, "only after measuring the hybrid"; not measured here. |
| JavaScript/WASM HLBES | Audit and measurement agree: HLBES CPU rounds to zero. |

## 7. Git and deployment

GIT_SECTION
