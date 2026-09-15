# INSPIRE metadata pipeline

`hepgraph.pipeline` is an **optional saved-snapshot maintenance tool**. The
normal Live INSPIRE application never invokes it. A clean public clone includes
the finished small snapshot and compressed evidence fixture, but no local
SQLite database or downloaded page cache.

When deliberately run by a maintainer, the pipeline creates only the
manifest-bounded subset of public INSPIRE metadata. It uses Python's standard
library and resumes interrupted work. It does not crawl author profiles found
in papers: a profile ID in a literature record creates a `literature_only`
person until an explicit `authors` manifest query supplies a profile. Never use
an unbounded manifest as a substitute for the live on-demand architecture.

## Optional maintenance commands

```sh
python -m hepgraph.pipeline ingest --manifest data/pilot.json \
  --db data/hepgraph.sqlite --cache data/cache
python -m hepgraph.pipeline build --db data/hepgraph.sqlite --output data/current.json \
  --manifest data/pilot.json
python -m hepgraph.pipeline import-jsonl --input external.jsonl --db data/hepgraph.sqlite
```

Before ingestion, review every manifest query and its limit, estimate the
expected cache size, and keep it modest. Local databases and cache pages are
ignored by Git and are not required to run the application.

Add `--refresh` to `ingest` to start configured queries again, including a
query that previously completed or failed.  Without it, completed checkpoints
are skipped and an interrupted query continues from its committed page.  Each
page is schema-checked, stored and checkpointed in a SQLite transaction.  The
sanitised, re-validatable cache page is reused when resuming an incomplete
query, so a network interruption does not require fetching an already cached
page again. The snapshot is written to a sibling temporary file and renamed
only after its entire build succeeds.

The active manifest is stored with ingestion.  Consequently the ordinary
`build --db … --output …` command retains its label, description, queries, and
examples; `--manifest` is optional only when deliberately building with a
different validated display configuration.

The importer requests at most 1,000 hits per page and 10,000 per configured
query. It keeps one page size for an entire query, including its final partial
page, so pagination offsets do not move. It makes requests sequentially, at no
more than one per second. A 429 or a transient 5xx/network error retries up to
five attempts. A 429 waits for `Retry-After` when supplied (at least five and
at most sixty seconds), otherwise it uses exponential waits starting at five
seconds. The final failure remains in the checkpoint and snapshot coverage.

## Manifest

```json
{
  "label": "Pilot: selected 2020–2021 papers",
  "description": "A query-scoped discovery subset; it is not a population census.",
  "literature": [
    {"query": "preprint_date:2020-01-01->2021-12-31 and collaboration:ATLAS", "limit": 500, "sort": "mostrecent"}
  ],
  "authors": [
    {"query": "name:Example", "limit": 25}
  ],
  "examples": [
    {"label": "Example connection", "source": "123", "target": "456"}
  ]
}
```

`label` is required. `description`, `literature`, `authors`, and `examples`
are optional.  Every query needs a non-empty `query` and an integer `limit`
from 1 through 10,000.  Literature may also supply `sort`.

## Minimal collection and privacy boundary

The requests use the public, fixed endpoints
`https://inspirehep.net/api/literature` and
`https://inspirehep.net/api/authors`.  Their `fields` parameter is an explicit
allowlist.  The cache is written only after the response has been reduced to
that allowlist, so it cannot retain unrelated returned values such as contact
details, notes, abstracts, keywords, or full text.

For literature, the retained fields are title, document type, author name,
author profile reference, `inspire_roles`, affiliation value, the upstream
`author_count`, documented preprint/publication date fields, DOI, arXiv
identifier, collaboration value, correction/deletion references, and thesis
degree type/date. `authors.roles` is intentionally never
used.  For author profiles, the retained fields are the documented name forms,
ORCID and INSPIRE BAI/ID identifiers, institution/current position, and the
adviser fields needed to assess PhD evidence.

## Meaning of the snapshot

The pipeline records every author occurrence by `(literature record ID,
position)` before export.  `author_count` is the larger of the explicit
upstream count and the number of selected author-role occurrences; it is never
the count of resolved profiles.  Only missing `inspire_roles` or an explicit
`author` role counts as coauthorship. Supervisor and editor roles therefore do
not create paper collaborations.

Dates use the earliest valid documented year. Within that year, a valid
INSPIRE `earliest_date` takes precedence and retains its reported precision;
a bare publication year must not erase a documented month or day, and a later
imprint must not replace an earlier preprint month. If `earliest_date` is
absent, use the earliest dated preprint, imprint, or thesis entry before a
bare publication-year fallback. Invalid calendar dates are ignored. Retrieval
timestamps never supply scholarly dates; missing dates are `unknown`.
A doctoral edge from a profile requires a non-hidden
`degree_type` of `PhD` and an adviser profile reference.  It notes uncertainty
when `curated_relation` is not true.  Thesis evidence additionally requires a
thesis document type, PhD thesis degree type, exactly one ordinary author as
the student, and a supervisor role. The HEP schema's normal author role is
sufficient; an unsupported `student` role is not required. Ambiguous thesis
authorship, non-PhD, hidden, and unresolved adviser assertions stay in the SQLite
audit table rather than becoming graph edges.

Tombstones are excluded.  `new_record` and `deleted_records` are replacement
references, not loose hints, and are followed when choosing the current record.
Stable record IDs are preserved. Exact normalized DOI or version-normalized
arXiv identifiers combine versions into one work. Contradictory author
memberships are logged in `dedup_conflicts`; the most complete authoritative
record supplies the work's authors rather than combining lists, preventing
invented collaborations. Merged works retain every raw source record ID in
`source_ids`, take the earliest documented date, and retain the largest explicit
author count.

`coverage.complete` is always `false`: configured search results and selected
profiles are a scoped subset. Each coverage query records the upstream total,
received count, and whether its configured limit truncated the available set.
Query progress and errors live separately in
`query_checkpoints` and `ingestion_state`, and failures are carried into each
snapshot's coverage section.

## JSONL imports

External bulk metadata is accepted line by line in either form:

```json
{"collection":"literature","record":{"id":"123","metadata":{...}}}
{"kind":"authors","record":{"control_number":456,"name":{...}}}
```

Only `literature` and `authors` are accepted. Each record passes exactly the
same allowlist and type validation as an API result. Bad lines are reported in
the command result and leave valid, already committed lines intact.
