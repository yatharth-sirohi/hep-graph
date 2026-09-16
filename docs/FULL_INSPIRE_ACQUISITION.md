# Full INSPIRE acquisition — implementation and release gate

This is a v0.3 manual-build component, **not** a completed production graph.
The `cloud-database-migration` branch contains a resumable, privacy-minimising
source acquirer in `hepgraph/full_acquisition.py` and a compact index prototype
in `hepgraph/compact_graph.py`. No full crawl has run. No full INSPIRE data has
been written to Neon, the developer Mac, Git, or Vercel. The existing
`data/current.json` remains an incomplete demo.

## Storage minimization selected for v0.3

INSPIRE literature must still be **read** once because a collaboration graph
cannot be derived from author profiles alone. The lasting query index need
not retain paper objects, titles, abstracts, affiliations, or full profiles.
Its minimal shape is:

- author ID → delta-varint encoded qualifying work IDs;
- work ID → year, true author count, delta-varint encoded resolved author IDs;
- PhD adviser/student/source IDs where independently documented.

This is linear in author–work incidence rather than quadratic in the size of
large collaborations. Year and true author count are necessary to preserve
existing filters. Distinct work IDs are necessary for `min_shared` and route
evidence. Rich paper metadata can be hydrated by INSPIRE only when a route
is displayed. The returned evidence reference remains the stable INSPIRE
work ID; an INSPIRE metadata outage should affect richness, not invent or
remove a stored collaboration edge. Live author lookup/profile display can
continue, with the immutable graph ID defining path-search coverage.

The compact SQLite prototype preserves the existing neighborhood and evidence
semantics for synthetic tests across small/all/large-team, year,
minimum-shared, and genealogy filters. Against the **incomplete** bundled
pilot (5,249 authors, 1,180 works), it occupied 270,336 bytes versus
3,137,536 bytes for the earlier synthetic SQLite index, an 11.6× reduction.
Twelve pilot authors across six filter sets had no neighborhood mismatch.
This is not a full-corpus size or performance forecast: the pilot is biased,
and SQLite page overhead differs from Neon/Postgres. The production version
still needs a streaming compiler and provider, independent validation, and
load/latency measurements. The acquirer's temporary source spool retains
deduplication/identity evidence; it is disposable only after validation.
Separate metadata-only API count probes reported 120,955 records with 11–100
authors, 15,729 with 101–1,000, and 4,053 with more than 1,000. These live
query buckets are useful warnings about large-team skew, not disjoint audited
graph counts or a final storage forecast.

## What has been verified against INSPIRE

On 2026-09-16, read-only, rate-limited API probes returned 1,885,680 literature
records and 805,292 author records. INSPIRE accepted
`recid:1->10000` for literature and `control_number:[1000000 TO 1010000]`
for authors. A broad literature range of IDs 1–10,000,000 matched the
unfiltered literature count on that date; the same horizon must be checked
for both collections at build time. These are point-in-time observations, not
an upstream commitment to a stable query syntax or a full-corpus export.

The [official API documentation](https://github.com/inspirehep/rest-api-doc)
sets a limit of 15 requests per 5 seconds per IP, page size at most 1,000,
and a 10,000-result search window. The client uses at most one request per
second, honors 429 backoff, and recursively splits ID ranges until each has
at most 1,000 results. Every leaf is fetched in one page and committed only
after its count and IDs pass checks. The sanitizer stores only graph-relevant
metadata and omits email, abstracts, keywords, and full text, consistent
with the [INSPIRE terms](https://help.inspirehep.net/knowledge-base/terms-of-use/).

## Isolated build-worker procedure

Run only on a private ephemeral machine/container with sufficient temporary
disk, not a developer laptop or a Vercel request function. The example uses
a path *inside that worker*, not the repository. Keep the spool private and
delete it only after a validated durable snapshot exists elsewhere.

```sh
python -m hepgraph.full_acquisition build \
  --spool /private-build/ins-pull.sqlite \
  --ephemeral-worker
```

Re-running the same command resumes completed shards. Use `status` to inspect
progress or `verify` to rehash all committed shards and recheck upstream
counts. `plan` and `fetch` are available for fault diagnosis; `fetch
--max-partitions N` makes a bounded test run but cannot certify the source.
The spool records per-partition SHA-256 values and a source-accounting report.
That report deliberately leaves `source_complete=false` even when
`partition_accounting_passed=true`; it cannot unlock promotion. It does
**not** claim a transactionally consistent INSPIRE cutoff: the public
API has no documented point-in-time export, and an unchanged total alone
cannot exclude an in-place correction during a long crawl. A production
validator must resolve this with INSPIRE or a defensible reconciliation
method before calling the graph complete.

Failure stops the build without touching the active Neon branch. A changed
shard count, missing range, duplicate ID, missing record, corrupt payload,
or changed final collection count cannot produce the source report. The
source report also does not validate identity merges, duplicate works,
genealogy, filters, graph edges, HLBES exactness, latency, or Vercel preview.

## Cost gate before a full run

Small read-only samples (50 older papers, 50 recent papers, 50 author
profiles) produced mean sanitized source-spool JSON payloads of roughly 678,
846, and 484 bytes respectively. Even using only those unrepresentative means,
the *temporary acquisition spool* may exceed 1.7 GB before SQLite overhead
and unusually large team bylines. **The final compact graph should be far
smaller, but its full-corpus size is not measured yet.** This is a sizing
warning, not a quote. The active/previous/candidate requirement raises peak
cloud storage. [Neon Free currently includes 0.5 GB per project](https://neon.com/pricing),
so do not assume the final graph fits it until a representative load is
measured. Neon Launch lists
usage-based storage at $0.35/GB-month and compute at $0.106/CU-hour; actual
spend must be measured from a representative compiled index and bounded in
the Neon account. Vercel Pro's subscription, if purchased, does not include
this separate database bill. No paid plan or overage was enabled here.

## Remaining release work

1. Confirm with INSPIRE whether a bulk or point-in-time export is available;
   otherwise document an approved, consistent crawl/reconciliation policy.
2. Select private ephemeral build storage and compute, with a measured
   storage/compute budget; run the full acquisition there.
3. Compile the full corpus into the compact author/work incidence shape with
   bounded memory, conservative identity and duplicate handling, true author
   counts, DOI/arXiv provenance, doctoral evidence, and immutable versioned
   output. The existing `pipeline.py` materializes a small in-memory graph
   and is **not** a full-corpus compiler; `compact_graph.py` is a semantic
   prototype, not the streaming production compiler.
4. Load the compiled graph into a separately keyed Neon candidate, test
   the query provider and scientific/evidence regressions, benchmark against
   live INSPIRE, and produce independent checksums and completeness proof.
5. Connect the actual `hep-graph` Vercel project, run a pinned preview, then
   explicitly promote via the atomic pointer. Keep the previous graph for
   rollback. No scheduled or incremental updater is part of v0.3.

The Vercel connection currently exposes only `ouriowacity`; do not attach
Neon credentials to that unrelated project. The first full acquisition
cannot be honestly represented as complete until the above gates pass.
