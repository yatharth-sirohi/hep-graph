# INSPIRE neighbourhood API audit

Measured against the live API on 2026-09-15 from
`hepgraph/pipeline.py:API_ROOT` (`https://inspirehep.net/api`). Every number
below came from a real request, not from documentation or memory. The probe
scripts paced themselves at 0.7 s and issued roughly forty requests in total.

Identities used: Hostert `1621061`, Pascoli `1019647`, Ellis `1010819`,
Witten `983328`, Rodgers `991505`, Aad `1066085`.

## A. How big is a neighbourhood, really

`q=authors.record.$ref:<id> AND author_count:<range>`, reading only `total`:

| Researcher | ≤10 works | >10 works |
|---|---:|---:|
| Hostert | 40 | 179 |
| Witten | 451 | 2 |
| Ellis | 1,127 | — |
| Aad | 8 | 1,515 |

Two different problems live here. In small-team mode a neighbourhood is a few
hundred to a thousand *cheap* records. In large-team mode it is a thousand or
more *catastrophically expensive* records.

## B. Payload per hit, small-team (Hostert, size=100)

| Field set | hits | bytes | bytes/hit |
|---|---:|---:|---:|
| Current `LITERATURE_FIELDS` | 40 | 70,856 | 1,771 |
| Minimal for adjacency | 40 | 61,155 | 1,528 |
| `control_number,authors.record,author_count,deleted` | 40 | 39,806 | 995 |

Field trimming is worth about 14% for the fields that are genuinely unused;
it is not where the cost is.

## C. Payload per hit, large-team (Aad `author_count:11+`, size=25)

| Field set | hits | bytes | bytes/hit |
|---|---:|---:|---:|
| Current `LITERATURE_FIELDS` | 25 | 10,352,493 | 414,099 |
| Minimal for adjacency | 25 | 7,059,296 | 282,371 |
| ids only | 25 | 4,775,680 | 191,027 |

**414 KB per record.** A single page of 25 is 10 MB, which already exceeds the
client's own `MAX_RESPONSE_BYTES` of 4 MiB — which is why `_literature_size`
drops to 5 records per page in this mode. Completing Aad's >10 neighbourhood
means 1,515 records at ~400 KB each: roughly 600 MB. Even stripped to bare
IDs it is ~290 MB, because the author list *is* the payload. This mode is
intrinsically expensive and no projection fixes it.

## D. Compression: not available

| Request header | Response `Content-Encoding` | Wire bytes |
|---|---|---:|
| none | none | 70,856 |
| `Accept-Encoding: gzip` | none | 70,856 |
| `Accept-Encoding: gzip, deflate, br` | none | 70,856 |

INSPIRE returned identical uncompressed bytes in all three cases. **There is no
compression win to take.** Recorded so nobody spends time on it again.

## E. Page size: the largest measured lever

Ellis, `author_count:1->10`, 1,127 qualifying works:

| size | HTTP | returned | bytes | time |
|---:|---:|---:|---:|---:|
| 100 | 200 | 100 | 89,792 | 1.04 s |
| 250 | 200 | 250 | 222,786 | 1.46 s |
| 500 | 200 | 500 | 444,310 | 2.19 s |
| 1000 | 200 | 1,000 | 889,725 | 2.66 s |
| 2000 | **400** | — | — | — |

**1,000 is the maximum accepted page size.** Bytes scale linearly, so a page of
1,000 costs one request and 2.66 s where ten pages of 100 cost ten requests and
about 10 s of paced wall time. The client currently caps `MAX_SIZE` at 100.

For Ellis this is twelve requests reduced to two.

## F. Result window

`page * size <= 10000` is a hard boundary:

| page | size | page×size | result |
|---:|---:|---:|---|
| 10 | 100 | 1,000 | 200, 100 hits |
| 40 | 250 | 10,000 | 200, **0 hits** |
| 20 | 500 | 10,000 | 200, **0 hits** |
| 11 | 1000 | 11,000 | **400** |

A query with more than 10,000 qualifying results can be read from but never
read to the end, so it can never certify a COMPLETE neighbourhood. The code
already treats this correctly (`MAX_RESULT_WINDOW` in `deep_search.py`).

## G. Server-side author-count filtering is exact

`author_count:1->10` over 40 returned Hostert records: **zero** violations of
the 1..10 bound. The filter agrees with the true byline count, so it is safe to
rely on for mode selection — as the code already does.

## H. Batched OR queries

Five researchers, `author_count:1->10`:

| | works |
|---|---:|
| Sum of individual totals | 1,850 |
| Union via one OR query | 1,840 |

A work containing any batched author and matching the count filter is returned
by the OR query, so paging the union to exhaustion certifies **every** batched
author's neighbourhood at once. Page 1 at size 250 already completed Hostert
(40/40) and Rodgers (56/56) outright.

Individually these five need roughly nineteen pages at size 100. As one union
at size 1000 they need two. The constraint is the 10,000 window in §F: a batch
whose union exceeds it certifies nobody, so batch size must be chosen against
the union total, which page 1 reports.

## I. Which fields are actually required

Checked against the code, not assumed:

| Field | Required by | Keep? |
|---|---|---|
| `authors.record` | adjacency itself | yes |
| `author_count` | mode filter, identity guard | yes |
| `authors.full_name` | identity guard byline check | yes |
| `authors.inspire_roles` | editor exclusion in `Graph` | yes |
| `titles.title` | erratum normalisation (`_STANDALONE_CORRECTION_TITLE`) | yes |
| `dois.value`, `arxiv_eprints.value` | duplicate union-find | yes |
| `earliest_date`, `preprint_date`, `imprints.date`, `publication_info.year` | year filters | yes |
| `deleted`, `new_record`, `deleted_records` | retraction handling | yes |
| `document_type`, `thesis_info.*` | doctoral edges | yes |
| `collaborations.value` | not referenced in graph construction | candidate |
| `authors.affiliations.value` | not referenced by the guard or `Graph` | **drop for discovery** |

`authors.affiliations.value` is the only field that is both droppable and
material, and it is material precisely because it is per-author: on a
3,000-author record it is 3,000 strings.

## Conclusions

1. Raise page size toward 1,000 in small-team mode. Largest measured win.
2. Drop `authors.affiliations.value` from discovery retrieval.
3. Batch a BFS layer into OR queries, bounded by the 10,000 window.
4. Compression: unavailable, do not revisit.
5. Large-team mode is payload-bound, not request-bound, and none of the above
   rescues it.
