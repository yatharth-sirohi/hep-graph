# Exact neighbourhood optimization — Phase II

Search data-access only. `hepgraph/hlbes.py` was not modified: `git diff
main..HEAD -- hepgraph/hlbes.py` is empty. No file under `static/` or `data/`
was touched.

## 1. Executive summary

Phase I made shortestness provable. It also made it expensive: proving a
distance means exhausting a researcher's literature query, and the work-record
count rose 4.5× even as requests fell.

This phase went looking for the cost and found it was not where it looked.
Three things turned out to be true, all measured rather than assumed:

- **Field projection was already tight.** Trimming the only genuinely unused
  field is worth 14%. Not the problem.
- **Compression does not exist.** INSPIRE returns identical uncompressed bytes
  whatever the `Accept-Encoding`. Recorded so nobody tries again.
- **The page ceiling and the discovery accelerators were the problem.** The
  client capped pages at 100 where INSPIRE accepts 1000, and two subsystems
  written for the pre-HLBES engine were spending a third of all requests to
  find something HLBES already finds for free.

Together those two changes cut a representative hard query from 94 requests
and 85 s to 39 requests and 41 s, reaching the same proven four-hop answer.

## 2. Starting baseline

| | |
|---|---|
| Commit | `a4c6896` on `main`, verified clean and matching `origin/main` |
| Repository | private (verified) |
| Python suite | 415 passed |
| Branch | `exact-neighborhood-optimization` |

## 3. API investigation

Full detail, with every measured number, in
[`docs/INSPIRE_NEIGHBORHOOD_API_AUDIT.md`](INSPIRE_NEIGHBORHOOD_API_AUDIT.md).
The findings that drove the work:

| Question | Answer |
|---|---|
| Maximum page size | **1000**; 2000 returns HTTP 400 |
| Result window | `page × size ≤ 10000`, hard |
| Compression | **None**, under any `Accept-Encoding` |
| Server-side `author_count` filter | Exact: 0 violations in 40 records |
| Small-team payload | ~1.8 KB per record |
| Large-team payload | **~414 KB per record** |
| Batched OR query | 5 researchers, 1,850 works → one 1,840-work union |

## 4. What changed

### Page ceiling: 100 → 1000

The single biggest lever. Ellis's 1,127 qualifying small-team works cost twelve
requests at size 100 and two at size 1000, for linearly scaling bytes.

Page size is a correctness surface, not just a speed knob: page *N* means
different records at different sizes. So `_Cursor.page_size` is fixed at first
use and never changes mid-pagination, and an oversized response halves the
session ceiling and restarts that cursor from page one rather than resuming at
an offset that no longer means what it meant.

Large-team mode keeps its small pages: at 414 KB per record a page of more than
a handful exceeds the 4 MiB transport bound. That mode is payload-bound and no
page-size or projection change rescues it.

### Discovery hints: off by default

The facet navigator and the cross-frontier bridge were written for the engine
that preceded HLBES, which had no systematic way to notice that its two
frontiers had met. HLBES rescans every node both sides know after every
expansion. Measured against it, both only spend requests.

Witten → Visser, with request counts identical across two opposite run orders,
which is what rules out upstream caching as the explanation:

| Configuration | Requests | Time | Result |
|---|---:|---:|---|
| Both on (Phase I behaviour) | 94 | 85 s | proven, 4 hops |
| Bridge off | 68 | 75 s | proven, 4 hops |
| **Both off** | **39** | **41 s** | proven, 4 hops |

The hardest case agrees: Hostert → Einstein proves the same five hops in 128
requests instead of 143 and finds its first route at 27 s instead of 32 s.

Bridging without the navigator is actively harmful — 110 requests and no proof
— which is why the two are gated together rather than separately.

Both subsystems and all twelve of their tests are **retained**, behind
`DeepSearch(discovery_hints=True)`. The tests opt in explicitly so they keep
guarding the code if a future oracle change makes cheap hints worth having.

### Profile lookups pinned to 25

An exact-ID author lookup returns at most one record per requested ID and
batches cap at 25, so inheriting a 1000-record page size only enlarged the
request and its cache key. `prefetch.py` was moved to the same constant so the
warm-up stays byte-identical to the request deep search later makes.

### Metrics

"Work records fetched" conflated a projected hit with a hydrated record, which
is exactly the distinction this phase trades on. Now separate:
`literature_pages`, `literature_hits`, hydrated `works`, and wire `bytes`
counted per cache layer at the one place the transport runs.

## 5. What was deliberately NOT changed

**Field projection.** `authors.affiliations.value` is the one droppable field
and is worth 14%. Taking it would mean a second projection for discovery, and
`store_record` upserts: a record first retrieved by a thin discovery query
would overwrite a fully hydrated one, so the evidence a path displays would
depend on which query happened to reach it first. Not worth 14%.

**Batched OR neighbourhood queries.** Measured and sound — the union of five
researchers is 1,840 works against 1,850 fetched individually, and paging the
union to exhaustion certifies every batched member at once. Not implemented
this phase: the completeness argument has to hold against the 10,000 result
window for the *union*, so a batch that overflows certifies nobody, and getting
that wrong produces exactly the false-COMPLETE failure this system is built to
prevent. Recorded in §11 as the strongest remaining lever.

**`hlbes.py`.** Frozen, as instructed. No correctness defect was found in it.

## 6. Completeness and exactness

Unchanged from Phase I and re-verified here. A neighbourhood is COMPLETE only
when every qualifying page has actually been retrieved; a lower-bound (`gte`)
count reads on until an empty page; a query whose results exceed the 10,000
window is marked incomplete rather than exhausted. PARTIAL adjacency may lower
an upper bound and never raise the lower one.

## 7. Correctness results

| | |
|---|---|
| Python suite | **445 passed, 1 xfailed** (baseline 415) |
| HLBES vs NetworkX | **24,000 pairs, 0 mismatches** |
| Live neighbourhood differential | 12 author/mode pairs, 0 mismatches |
| `hepgraph/hlbes.py` | byte-identical to `main` |

New tests: `tests/test_literature_paging.py` (paging is a correctness surface),
`tests/test_upstream_faults.py` (the adversarial reviewer's ten scenarios,
vendored so the evidence outlives the scratchpad), plus the live
`tests/live_neighborhood_diff.py`.

No original test was deleted. Five were amended: two pinned `MAX_SIZE = 100`
literals, two pinned the pre-change prefetch call list and cache limit, and one
`_fetch` stub returned a 2-tuple where the real `_fetch` returns three.

The one `xfail` is deliberate and documented — see §11.

## 8. Performance

Sixteen live pairs, cold cache, 180 s cap, `tests/live_benchmark.py`.
"Phase I" is `main` at `a4c6896`; "Phase II" is this branch. `P` = proven shortest.

| Query | Phase I | Phase II | Requests |
|---|---|---|---|
| Hostert → Pascoli | 1h 1.7 s **P** | 1h 1.6 s **P** | 4 → 4 |
| Hostert → Dirac | no route, 180 s | no route, 180 s | 188 → **119** |
| Hostert → Ellis | 2h 13.8 s **P** | 2h **6.3 s** **P** | 26 → **6** |
| Hostert → Feynman | 3h 21.6 s **P** | 3h **14.7 s** **P** | 33 → **15** |
| Hostert → Einstein | 5h 172.9 s **P** | 5h **142.2 s** **P** | 193 → **127** |
| Hostert → Witten | 3h 39.0 s **P** | 3h **6.3 s** **P** | 52 → **8** |
| Feynman → Wheeler | 1h 1.4 s **P** | 1h 1.4 s **P** | 4 → 4 |
| Witten → Visser | 4h 72.1 s **P** | 4h **35.7 s** **P** | 86 → **39** |
| Visser → Uppu | 4h 70.9 s **P** | 4h **23.3 s** **P** | 107 → **29** |
| Visser → Rodgers | 4h 102.5 s **P** | 4h 99.4 s **P** | 142 → **117** |
| Visser → Massey | no route, 180 s | no route, 180 s | 175 → **116** |
| Aad → Abbott (>10) | 1h 3.7 s **P** | 1h 3.8 s **P** | 4 → 4 |
| Pascoli → Wheeler | 3h 94.1 s **P** | 3h **12.9 s** **P** | 113 → **15** |
| Uppu → Ellis | 4h 115.8 s **P** | 4h 132.4 s **P** | 136 → **110** |
| Rodgers → Dirac | no route, 180 s | no route, 180 s | 202 → **133** |
| Ellis → Massey (all) | no route, 180 s | no route, 180 s | 226 → **187** |

| | Phase I | Phase II |
|---|---:|---:|
| Shortestness proven | 12 / 16 | 12 / 16 |
| Route found | 12 / 16 | 12 / 16 |
| Hit the 180 s cap | 4 / 16 | 4 / 16 |
| **Upstream requests** | 1,691 | **1,033 (−39%)** |
| **Wall time** | 1,431 s | **1,202 s (−16%)** |

Nothing got less exact and nothing stopped finding a route; the same answers
cost a third fewer requests. Hostert → Witten is the clearest case: 39 s and 52
requests became 6.3 s and 8.

Against the §71 query targets: Hostert → Feynman 21.6 s → **14.7 s** (goal was
no regression, preferred under 20 s). Witten → Visser 72 s → **35.7 s** (goal
under 45 s, met; stretch under 30 s, missed). Hostert → Einstein remains proven
exact at five hops under identical settings.

Against the §70 aspirational targets, honestly:

| Target | Result |
|---|---|
| ≥40% fewer upstream requests on hard queries | **Met per-query** (Witten −85%, Pascoli → Wheeler −87%); **−39%** in aggregate |
| ≥40% less wall time | **Missed** in aggregate (−16%); met on most individual hard queries |
| ≥90% less full literature hydration | **Not attempted** — see §11 |
| ≥70% fewer payload bytes | **Not met**; larger pages carry more records per request, and the win was in request count |

One query regressed: Uppu → Ellis, 115.8 s → 132.4 s, on 26 fewer requests.


## 8. Performance

## 9. Core cache

The existing manifest at `data/cache/core-nodes.json` was reused, not
regenerated: 499 seeds attempted, 408 resolved, 65 ambiguous and deliberately
skipped, 26 without a profile, 0 failures — 499 of 499 accounted for. The "499
rather than 500" in the brief is simply the curated list after de-duplication,
not a bookkeeping loss.

**Prewarming was not run.** The phase's own ordering (§46) puts it after the
oracle is efficient, and the oracle only became stable at the end of the
correction rounds below. Warming it now, on the strength of an evening's worth
of just-fixed paging code, would put hundreds of upstream requests behind
changes that three review rounds have each found something wrong with. The cost
is now known and small — most small-team neighbourhoods are one or two requests
at the derived page size — so this is a cheap first task for a session that
starts from a settled branch.

## 10. Agent review

No OpenAI model was available in this environment: there is no `codex` CLI and
no OpenAI credentials. Nothing was routed to Spark, Luna or Sol, and no
OpenAI-model validation occurred.

All implementation was done by **Claude Opus 5** (this session). Review was
delegated to **separate Claude Code agents** with no access to the
implementer's reasoning, instructed to run code rather than reason about it:

| Round | Agent | Outcome |
|---|---|---|
| 1 | Independent correctness reviewer | 11 findings, 2 regressions I introduced |
| 1 | Independent adversarial tester | 10 confirmed defects, 3 critical |
| 2 | Independent correctness reviewer | 11 findings, said **do not merge** |
| 3 | Independent verification reviewer | (see §12) |

That separation earned its keep. Round 1's adversarial tester found that page
arithmetic alone was deciding exhaustion, which my larger pages amplified
tenfold. Round 2 found that my own page-size change made a one-hop pair return
`search_incomplete` for ever — a hard product failure on the cheapest query the
product makes. Round 3 found that my fix for a lower-bound count was an
unbounded loop, strictly worse than `main`, and that a surname guard I added to
close a real identity hole was withholding 13 of 23 legitimate bylines.

Twice a fix of mine closed the reported instance and left an equivalent hole
beside it, which is exactly the failure mode the brief warned about. Both times
the next round caught it.


## 10. Agent review

## 11. Remaining limitations

Stated as found.

**A confirmed identity hole is documented, not fixed.** The coauthor guard
compares given names, and those rules return False once the surnames already
differ, so a byline of an unrelated surname carrying a profile's record
reference passes every gate: a 2023 paper bylined "Schmidt, Anna" can resolve
to a physicist who died in 2002. A surname check was written and reverted —
measured against realistic INSPIRE name forms it withheld 13 of 23 legitimate
bylines (particles like *de Boer* and *al-Hassan*, Spanish double surnames,
hyphenated and married names, transliterations, and every two-token
native-order name such as *Wang Ping*, which the existing surname parser reads
as Given Surname). Withholding real collaborations is worse harm than the hole.
It is pinned as a strict `xfail` in `tests/test_upstream_faults.py` with the
evidence. A correct fix needs name-form parsing this phase did not attempt.

**Discovery and evidence are still not separated.** The §70 target of a 90%
cut in full literature hydration is not met, because that work was not
attempted: the audit showed that a second, thinner projection for discovery
would let `store_record` overwrite fully hydrated records with partial ones,
and the phase's measured wins turned out to be elsewhere. This is the largest
remaining lever after batching.

**Batched OR neighbourhood queries were measured but not built.** Five
researchers' 1,850 works union to 1,840, and paging the union certifies all
five at once. The completeness argument has to hold against the 10,000 window
for the *union*, and getting that wrong produces exactly the false-COMPLETE
failure three review rounds were spent eliminating. It is the strongest
remaining lever and deserves its own phase.

**Large-team mode is payload-bound and untouched.** At ~414 KB per record,
completing one prolific ATLAS member's `>10` neighbourhood is hundreds of
megabytes. No projection or page size changes that.

**Core prewarming was not run** — see §9.

**Known and accepted, each confirmed by review:** one large page can still
evict the warmed author-record index, because author records share the main
LRU and are the smallest entries (the threshold moved from ~3 pages to ~23, the
failure mode did not change); `_page_ceiling` is only ever lowered, so one
oversized response pins a session for its lifetime; the direct-pair loop lacks
the short-page escape that per-person pagination now has; the guide-pair reset
detects an in-call shrink but not a size that merely differs from the one its
saved page was taken at (unreachable in-product, since the ceiling only
decreases); and an erratum carrying a *fuller* byline than the paper it
corrects still loses those extra authors, since the two bylines are not merged.


## 12. Git

Branch `exact-neighborhood-optimization`, based on `a4c6896`. Commits, newest first:

```
b410596 Pin the two fixes that mutation testing showed were unguarded
fad05c2 Record final benchmark numbers and limitations
1f5508f Act on the third review round
ac1df78 Report core cache status and agent review rounds
796c6d4 Act on the final pre-merge review, including reverting one of my own fixes
9bdb414 Close the ten defects an adversarial review confirmed, and keep its tests
8a8a80d Fix the regressions two independent reviews found in this branch
3234380 Pin the page-size rules with tests and a live neighbourhood differential
2e45a22 Turn off discovery hints by default and measure why
888fccd Spend discovery requests only while no route is known
460b900 Audit INSPIRE neighbourhood retrieval against the live API
```

Files changed: `hepgraph/deep_search.py`, `hepgraph/remote.py`,
`hepgraph/prefetch.py`, `hepgraph/pipeline.py`, one dead local removed from
`hepgraph/identity_guard.py`, three new test modules, two new live harnesses,
and two documents. **`hepgraph/hlbes.py` is byte-identical to `main`**, and no
file under `static/` or `data/` was touched.

### Clean-clone acceptance

A fresh clone of the private repository, with no cache, no database and no
environment file: **447 passed, 1 xfailed**; every module imports; the server
starts; health, index and `app.js` all answer; live author search works; and a
live path query (Feynman → Wheeler) returns a proven one-hop route with real
paper evidence. No machine-specific path is required — the two vendored
harnesses were rewritten to resolve their own location.

### Review outcome

The third review round returned **MERGE**, having confirmed each fix by
instrumented comparison against both the previous commit and `main` — most
decisively a probe asserting that the page size `_page_done` reasons about
equals the size actually sent upstream: 5 violations on the previous commit, 0
on this one. Two randomized differentials (148 and 146 end-to-end searches
against NetworkX ground truth) and the vendored fault suite found no new
defect.

Its two non-blocking notes were both acted on: the missing regression coverage
is now two mutation-checked tests, and the window-tail recall difference is
recorded in §11.
