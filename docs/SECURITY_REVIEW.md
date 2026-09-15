# Service and public-repository review

Reviewed 15 September 2026 against the final Desktop source. This is a local,
read-only research demonstration. The review covers the HTTP boundary, live
INSPIRE client, temporary caching and jobs, static files, malformed upstream
responses, public-repository contents and storage limits.

## Final disposition

No known high-severity issue remains in the reviewed local MVP. The final
Python suite contains 354 passing tests; the seven browser suites contain 70
passing checks with zero uncaught errors. The project uses no API key or
credential for public INSPIRE reads.

This review does not certify an internet-hosted multi-user service. A public
GitHub source repository is not a public deployment.

## Findings fixed in this release

### Search result memory could exceed its advertised cap

The result LRU originally installed a complete worker result before it tried to
evict finished jobs. One result larger than the configured byte ceiling could
therefore exceed the bound briefly and then be silently evicted, including the
job that had just finished.

Every progress and final-result replacement is now serialized and admitted
before assignment. Closed compact results may be evicted; active or resumable
sessions are never discarded. If one update cannot fit, the job remains
queryable as an explicit `resource_limit` result and does not present an
unretained route. Tests cover both an oversized progress update and an oversized
final result under a 64 KiB test ceiling.

### Preparation could describe a missing identity as ready

Selected-author preparation previously treated any schema-valid author-search
response as a warmed identity, including an empty result or a different ID. It
now requires a current, non-deleted hit for which both the response hit ID and
`metadata.control_number` equal the exact requested numeric profile ID.

Empty, wrong-ID and deleted responses produce `failed/not_found` and skip
dependent facet and literature warmups. Transport failures may still yield a
truthful `partial` preparation when an independent warmup succeeded.

### Historical identity shortcuts

The live tests found modern Philip/P. Bergmann bylines attached to the Peter
Gabriel Bergmann profile and crossed Fermi/Teller adviser names and record IDs
in Chen-Ning Yang's profile. The identity guard now withholds the affected
occurrences or doctoral references, records the reason in coverage metadata,
and continues searching. It does not silently rewrite INSPIRE or infer the
intended person.

### Earlier request-boundary findings

The retained regression suite also covers fixes for:

- graph errors being masked as generic invalid input;
- saved-graph resource limits being returned with HTTP 200;
- mutable cached response objects escaping to callers;
- malformed author/literature payloads becoming uncaught server errors;
- aggregate expansion of a giant collaboration during degree centrality;
- late browser responses overwriting a newer query or source mode.

## HTTP and browser boundary

- Static files come from a fixed allowlist. Encoded traversal paths, local data
  files, test artifacts and arbitrary filesystem paths return 404.
- Query strings reject duplicate and unknown parameters, malformed ranges,
  invalid IDs, excessive fields and overlong URLs before starting work.
- Only the exact preparation, continue and cancel routes accept POST. They
  reject request bodies, transfer encoding and a supplied cross-origin Origin.
- HEAD cannot start an expensive search.
- Job IDs are unpredictable 128-bit values; job filters and endpoint direction
  are immutable.
- JSON uses `no-store`, `nosniff`, a same-origin content security policy, a
  strict referrer policy and a restrictive permissions policy.
- Source-provided titles, names and evidence are rendered as text. Browser
  tests include hostile-looking metadata strings.

The service binds to `127.0.0.1` by default. Binding it to a public interface
would require a deployment review, TLS termination, authentication/rate policy
appropriate to the audience and operational monitoring.

## Upstream INSPIRE controls

- Upstream hosts are fixed to the HTTPS INSPIRE author and literature APIs.
  Callers cannot supply a host or redirect destination.
- Query construction interpolates only parsed literal name tokens, exact
  numeric IDs or validated ORCIDs into fixed field expressions.
- Responses have a 4 MiB transport cap, bounded JSON nesting, finite-number
  validation and per-collection schema checks.
- Returned and cached records are reduced to explicit public metadata fields.
  Contact details, notes, abstracts, full text and unknown private fields are
  removed.
- HTTP-date and numeric `Retry-After` values are honored. Timeouts, rate limits,
  malformed responses and upstream downtime produce explicit incomplete or
  unavailable states, never a false `no_path` conclusion.
- Identical in-flight requests coalesce. Followers retain independent
  deadlines; errors are not cached.

## Resource and storage controls

| Resource | Bound |
| --- | ---: |
| Shared sanitized response data | 8 MiB, 256 entries, 15-minute TTL |
| Retained serialized search results | 8 MiB, 32 jobs, 20-minute TTL |
| Concurrent upstream requests | 8 |
| Active deep searches | 2 |
| Resumable deep-search sessions | 4 |
| Preparation workers / pending queue | 2 / 8 |
| Preparation statuses | 32, 10-minute TTL |

Search-session SQLite databases are in memory and remain on their owner worker
thread. Cancellation stops future retrieval and releases the session after an
already-running bounded transport call acknowledges it. Stopping the server
clears all live caches and search sessions.

The project does not start the optional ingestion pipeline during normal use.
It does not write a live literature mirror or a growing disk cache.

## Public-repository hygiene

The repository ignore rules exclude environment files, keys/certificates,
virtual environments, Python caches, local SQLite databases, downloaded cache
pages, generated screenshots, browser profiles, traces, logs and test results.
The intentional public data is limited to the 2.30 MB saved snapshot, its small
manifest and a 622 KB compressed public provenance fixture.

Before publication, the tracked-file set must pass:

- a filename and content secret scan;
- an absolute-home-path and personal-data scan;
- a large-file and generated-artifact review;
- a clean-clone installation, full test suite and server smoke test;
- remote commit/tree verification after push.

The final publication record in [Validation](VALIDATION.md) should be treated
as authoritative for those release gates.

## Residual limits

- Public scholarly metadata can be wrong or incomplete. Identity checks reduce
  false shortcuts but cannot establish every historical initial-only byline.
- The application is designed for a professor demonstration and local research
  exploration. It has no account system, abuse controls or production service
  monitoring.
- No software license has been selected. Public visibility does not grant a
  software license; linked sources and INSPIRE metadata retain their own terms.
