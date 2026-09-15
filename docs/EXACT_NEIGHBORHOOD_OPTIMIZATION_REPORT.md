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

## 8. Performance

## 9. Core cache

## 10. Agent review

## 11. Remaining limitations

## 12. Git
