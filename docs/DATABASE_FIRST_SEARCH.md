# Database-first search with deferred hydration

How a route search works once the graph lives in PostgreSQL, what it may and may
not claim, and what still has to happen before production can be switched.

Status: **this is now the only way the application finds routes.** The live
INSPIRE traversal engine has been removed, not disabled. The import is complete
and validated (all 1,885,680 INSPIRE literature records reconciled, drift 0),
and searches run against it end to end. See
[Measured end to end](#11-measured-end-to-end).

## 1. The two stages

Previously one search drove INSPIRE directly: every frontier expansion fetched
full literature records, and a large-collaboration neighborhood cost 414 KB per
record ([INSPIRE_NEIGHBORHOOD_API_AUDIT.md](INSPIRE_NEIGHBORHOOD_API_AUDIT.md)
§C). Now:

**Stage 1 — route.** `NeonCompactGraphProvider` answers neighborhoods from the
work/author incidence tables. Nothing but identifiers, true author counts and
years is read. No titles, names or affiliations exist in the graph at all, so
traversal *cannot* accidentally fetch them.

**Stage 2 — verification and hydration.** Once a route settles, `Hydrator`
fetches the people and evidence works the answer actually displays -
deduplicated, paced, cached and budgeted - and the *same* response is used to
check the route: for every edge, INSPIRE's byline on the cited paper must list
both researchers. A contradiction withdraws the proof rather than displaying a
clean-looking edge, so a graph that has drifted from the source cannot present
itself as verified. Verification therefore costs no extra requests. `tests/test_graph_database_mode.py::test_no_paper_fetch_during_traversal`
is the enforcing test: it spies on the INSPIRE client and asserts zero calls
during expansion, then asserts calls appear only after delivery.

Identity resolution (`/api/search`, name → INSPIRE ID) still queries INSPIRE.
That is a name lookup, not traversal, and the compact graph stores no names.

```
 /api/path?mode=database
   └─ DatabaseGraphService.start_path
        ├─ pointer resolved once  ──> NeonCompactGraphProvider (pinned import_id)
        ├─ DatabaseSearchJobs      ──> HLBES proof, serialised to graph_search_job
        └─ Hydrator                ──> INSPIRE, only for the delivered route
```

## 2. Modules

| File | Role |
|---|---|
| `hepgraph/neon_graph_provider.py` | Read-only pinned provider; adjacency from incidence; honest UNKNOWN/PARTIAL/COMPLETE |
| `hepgraph/db_search_jobs.py` | Durable, version-pinned, resumable proofs (`graph_search_job`) |
| `hepgraph/graph_hydration.py` | Bounded, cached, deduplicated post-route metadata fetch |
| `hepgraph/graph_database_mode.py` | Serving mode: config, pointer, jobs, hydration, API payloads |
| `hepgraph/snapshot_validation.py` | Independent adversarial validator over a candidate import |
| `hepgraph/sql/genealogy_overlay.sql` | Separately versioned doctoral-edge overlay |

Enabled only when configured:

```
HEPGRAPH_GRAPH_DATABASE_URL=...        # read-only serving credential
HEPGRAPH_GRAPH_IMPORT_ID=...           # the pinned import
HEPGRAPH_GRAPH_OVERLAY_ID=...          # optional genealogy overlay
HEPGRAPH_GRAPH_CERTIFIED_COMPLETE=1    # ONLY after the validator passes
```

`HEPGRAPH_GRAPH_CERTIFIED_COMPLETE` is deliberately a separate variable from the
import id. Pointing the app at an import must never be the same act as
certifying it.

## 3. What the engine may claim

`HLBES` treats a COMPLETE neighborhood as proof, so a wrong COMPLETE does not
produce a slow answer — it produces a confidently wrong one. The provider
therefore returns COMPLETE only when the operator's certificate is present.

| Situation | Reported |
|---|---|
| Certified import, proof closed | `exact`, `global_shortest_proven: true` |
| Uncertified import, route found | `verified` — a real route, no shortest claim |
| Uncertified import, nothing found | `search_incomplete`, never `no_path` |
| Endpoint absent from the import | `search_incomplete`, reason `author_not_in_graph` |
| Genealogy on, no certified overlay | PARTIAL, reason `genealogy_overlay_uncertified` |
| Hub author over the visit budget | PARTIAL, reason `member_visit_budget_exceeded` |
| Database error | `GraphDatabaseError` → job `failed`, never an empty result |

The last row is the one that matters most: a dropped connection must never
become an empty COMPLETE neighborhood, because that is indistinguishable from
"this person has no collaborators" and would prove a false `no_path`.

Filters subset a certified universe, so they preserve a completeness claim. A
missing *edge class* (genealogy without an overlay) does not: the neighborhood
would be missing edges rather than merely filtered ones.

## 4. Version pinning is a mechanism, not a policy

`graph_search_job` stores `import_id`, `overlay_id`, `schema_version` and
`filter_key` as columns. Every slice re-checks them against the provider it was
handed; a mismatch ends the job with `graph_version_changed` rather than mixing
two graphs. A new search resolves the active pointer once, at creation.

This is what makes the rollback drill meaningful, and it is tested:
`test_a_running_job_keeps_its_pin_while_a_new_search_takes_the_new_version`
moves the pointer mid-flight and asserts the running job finishes on its
original version while the next search starts on the new one.

Durability is real, not nominal: the HLBES proof is serialised to the row, and
`test_a_fresh_engine_resumes_a_job_another_instance_started` resumes it with a
different engine object and provider, as a second serverless instance would.
`seen_key` is deliberately not serialised — it holds `hash()` values that differ
between interpreters — while `blocked`, the decision that key produced, is.

## 5. Feature parity

| Feature | Database mode | Note |
|---|---|---|
| Researcher search / disambiguation | **Yes** | Live INSPIRE identity resolution, unchanged |
| Route search, all hop counts | **Yes** | Zero-hop, direct, multi-hop, disconnected covered |
| Progressive / provisional results | **Yes** | `provisional: true` until settled |
| Continue / cancel | **Yes** | Same `/api/search-jobs/<id>[/continue|/cancel]` endpoints |
| Evidence list per edge | **Yes** | Refs from the graph, metadata hydrated |
| Paper titles, dates, DOI/arXiv links | **Yes** | Hydrated post-route |
| Researcher profile panel | **Yes** | `/api/person/...`, hydrated on open |
| Neighborhood view | **Yes** | `/api/neighborhood/...` |
| Filters (type, author count, shared works, years) | **Yes** | Semantics matched to `graph.py`, differential-tested |
| Coverage/version labelling | **Yes** | `/api/dataset` reports the pin and its limits |
| **Doctoral / genealogy edges** | **Yes** | Separately versioned overlay, 36,589 relations |
| **Doctoral lineage / family tree** | **Yes** | `/api/ancestry`, multi-generation, both directions |
| **Global centrality** | **No** — gap | Needs a separate large-graph implementation; not offered in this release |

The remaining gap is reported to the user, never silently dropped. The production
application serves only the pinned graph database and does not ship a local demo graph.

### Known limitations of the compact schema

- Ingest-time eligibility (document type, erratum titles, `author_count >= 2`,
  author-role filtering) is applied by the importer and **cannot be re-derived**
  from the stored columns. It is pinned by `schema_version`, not re-checked.
- Preprint/journal duplicate reconciliation is **not verifiable**: no DOI or
  arXiv identifiers are stored. Work IDs are unique by primary key, which is a
  weaker guarantee than canonical deduplication.
- `source_cutoff` is a **start marker**, not an atomic point-in-time view.
  INSPIRE offers no snapshot mechanism and no validated `updated` watermark.

## 6. Measured candidate state (read-only, 2026-09-16)

`CompactImportValidator` against `candidate-inspire-20260916`:

```
source_complete        FAIL   3 DISCOVER + 1 PENDING shard outstanding
record_reconciliation  FAIL   3 ranges never discovered:
                              [1–1,500,000] [1,500,001–2,250,000] [2,250,001–2,625,000]
source_window          FAIL   retrieval spans 2,839 s after the recorded cutoff
referential_integrity  PASS   0 orphan memberships across 3,257,865 rows
work_semantics         PASS   172,032 works, 0 member_count mismatches
duplicate_works        PASS   172,032 distinct work IDs
year_sanity            PASS   earliest 1895, none out of range
```

Present: 172,032 works, 3,257,865 memberships, 232,188 distinct authors,
covering record IDs 2,625,102–2,999,999 only — the newest ~12.5% of the declared
ID space. The importer process is not running.

`received_records_total` (244,662) exceeds `expected_records_total` (227,109)
because the counter records page *attempts* and the primary key deduplicates
retries; the stored row counts, not the counter, are authoritative.

## 7. Cost, measured rather than assumed

Actual sizes in the candidate branch:

| Table | Total | Heap | Index |
|---|---:|---:|---:|
| `inspire_compact_membership` | 771 MB | 213 MB | 558 MB |
| `inspire_compact_work` | 30 MB | 19 MB | 11 MB |
| **Total** | **801 MB** | | |

≈258 bytes per membership row all-in. Two observations:

1. **Indexes are 2.6× the heap.** Both the primary key and the
   `(import_id, author_id, work_id)` index repeat `import_id TEXT` in every
   tuple. A small integer surrogate for the import would cut roughly 15 bytes
   per index tuple — on the order of 750 MB at full corpus size. Worth doing
   before the next full import; changing it now would invalidate the existing
   resume checkpoints.
2. **Extrapolation.** At the observed 77.7% retention and ~19 memberships per
   work, a full INSPIRE corpus (~1.7M literature records) implies roughly 1.3M
   works and ~25M memberships, i.e. **≈6 GB** in this schema, or ≈4–5 GB with
   the integer-key change.

That is already far past Neon's 0.5 GB free tier — it is past it *now*, at 12.5%
of the corpus. A paid tier at roughly $0.35/GB-month puts storage near
**$2–3/month**, with compute on top; a lightly used project plausibly lands in
the **$5–25/month** range. The dominant uncertainty is query volume, not
storage. **No plan change has been made.**

## 8. Measured query performance

`tests/benchmark_graph_database.py` against local PostgreSQL 18.6, on a
synthetic corpus of 172,000 works and **8,575,846** memberships — deliberately
**2.6× denser** than the real candidate (3.26M memberships over the same work
count), so these are conservative. Median of five runs, local socket, so they
exclude network time:

| Query | Median | Max |
|---|---:|---:|
| Neighbors, median-degree author, small-team (≤10) | 0.6 ms | 26.9 ms |
| Neighbors, hub author (53 works), small-team | 0.7 ms | 7.8 ms |
| Neighbors, median-degree author, all modes | 15.8 ms | 50.4 ms |
| Neighbors, hub author, all modes | 18.1 ms | 62.9 ms |
| Batch of 32 authors, small-team | 13.4 ms | 85.8 ms |
| Edge evidence refs | 0.3 ms | 0.5 ms |
| Author existence check | 0.1 ms | 0.1 ms |

Small-team mode is fast because the author-count filter excludes mega
collaborations before the join. All-modes is an order of magnitude slower for
exactly the opposite reason, and is where the member-visit budget matters.

Batching is worth it: 32 authors in 13.4 ms is ~0.42 ms each against ~0.6 ms
individually, and more importantly it is **two** round trips instead of 64.
Over a real Neon connection the round trip, not the scan, will dominate small
queries — budget roughly 1–5 ms each way in-region, so co-locating the Vercel
functions with the Neon region is worth more than any further query tuning.

`EXPLAIN` confirms the intended plan: an index-only scan on
`inspire_compact_author_work` to find the author's works, an index scan on the
work primary key to apply the author-count and year filters, then an index-only
scan on the membership primary key to collect co-members — no sequential scans,
no materialised pair table.

## 9. Cutover gates

All must pass. Today, the first does not.

1. **Source completeness** — every shard DONE, every declared range discovered
   and reconciled. `CompactImportValidator.validate().gates["source_complete"]`.
2. **Independent validation report** filed via `PostgresSnapshotRegistry.mark_ready`
   (it refuses anything short of a full gate set).
3. **Differential tests** against `Graph` across the filter matrix.
4. **Benchmarks** at production scale with reviewed query plans.
5. **Rollback drill** — proven in tests, to be repeated against the real branch.
6. **API/UI parity check** in a real browser.

Until gate 1 passes, `HEPGRAPH_GRAPH_CERTIFIED_COMPLETE` must stay unset. The
app is fully usable in that state: it finds and evidences routes, and simply
declines to claim shortest-ness or absence.

## 10. Rollback

The pointer, not the data, is what moves.

```
# Promote (only a READY, validated candidate)
PostgresSnapshotRegistry(connection).promote(snapshot_id)

# Roll back to the previous known-good version, no rebuild
PostgresSnapshotRegistry(connection).rollback()
```

Both are single transactions with row locks. The superseded version is retained
as the rollback target. Searches already running stay pinned to the version they
started on; searches started afterwards take the restored version. If a running
job's provider no longer matches its pin, that job ends `failed` with
`graph_version_changed` — never a silently mixed answer.

To disable database serving entirely, unset `HEPGRAPH_GRAPH_DATABASE_URL`. The
application then reports graph search as unavailable; it does not fall back to
a differently scoped graph without an explicit deployment change.


## 11. Measured end to end

Against the live graph (1,261,552 works, 21,017,590 memberships) from a laptop
over WAN, small-team filters, genealogy off. Every route below settled inside a
single request - no polling - and every edge was confirmed against INSPIRE's
byline:

| Pair | Time | Hops | Proof | Edges confirmed |
|---|---:|---:|---|---:|
| Hostert → Pascoli | 4.24 s | 1 | exact | 1/1 |
| Witten → Ellis | 1.92 s | 2 | exact | 2/2 |
| Hostert → Feynman | 2.10 s | 3 | exact | 3/3 |
| Visser → Hostert | 5.75 s | 4 | exact | 4/4 |
| Einstein → Dirac | 4.57 s | 3 | exact | 3/3 |
| Hostert → Uppu | 11.46 s | 4 | exact | 4/4 |
| Unknown endpoint | 0.25 s | - | `search_incomplete`, `author_not_in_graph` | - |

For comparison, the removed live engine on production Vercel took **241.7 s on
Visser → Hostert and returned no route at all**; it now resolves in 5.75 s with
the same four-hop route its own report predicted (Visser → Gardiner → Isaacson
→ Fox → Hostert), proven shortest.

Two hop counts are *shorter* than the historical benchmarks (Einstein → Dirac
3 rather than 5, Hostert → Uppu 4 rather than 5). That is the expected
consequence of searching the whole corpus instead of a sampled demo snapshot:
more data admits shorter true routes.

**Certification is load-bearing, not cosmetic.** An uncertified graph returns
PARTIAL neighborhoods, which can never advance a completed radius, so the engine
cannot stop early and explores the component instead - the same searches took
minutes rather than seconds. Certifying a graph whose completeness has actually
been validated is what makes termination possible.


## 12. Doctoral lineage

Adviser relations are not collaboration topology. They come from INSPIRE's
`authors` collection, on the student's own record, so they load into
`graph_genealogy_edge` under their own `overlay_id` with their own certificate.
A neighborhood that includes doctoral edges is COMPLETE only when *both* the
import and the overlay are certified; otherwise it is PARTIAL, because the
neighborhood would be missing an edge class rather than merely filtered.

`hepgraph/genealogy_import.py` harvests it, reusing the shard protocol from
`fast_compact_import` rather than restating it, from **two** INSPIRE sources
that disagree about how much they know:

| Crawl | Source | Records | Import id |
| --- | --- | --- | --- |
| Author profiles | `advisors` on the student's own record | 29,404 | `genealogy-20260917` |
| Thesis supervisors | `supervisors` on the thesis, `document_type:thesis` | 27,194 | `genealogy-theses-20260917` |

The thesis side is the larger of the two and was missing entirely at first:
together they hold **73,171 relations, 50,255 of them doctoral**, over 52,683
people, of whom 35,979 have a doctoral adviser. Both crawls reconcile exactly
against INSPIRE's own counts. `source_kind` records which crawl a relation came
from, and the evidence link follows it - a thesis relation links to the thesis,
an adviser-field relation to the author profile.

A thesis repeats its supervisors inside `authors`, sometimes as plain authors
too, so anyone named supervisor anywhere on a thesis is never treated as its
student. Where two records still contradict each other - each thesis naming the
other's author as supervisor - the loop is impossible rather than merely
surprising, and the weaker side is withdrawn into `graph_genealogy_quarantine`
with the loop as its reason. Withdrawn evidence is kept, never deleted.

**Only relations INSPIRE typed `phd` are traversable.** The overlay stores every
supervision relation it records - master's, bachelor's, and 1,561 it left
untyped - because filtering at crawl time would discard real relationships and
re-deciding would mean crawling again. `DOCTORAL_DEGREES` is the single place
that decides what counts, and it is applied in the neighborhood query, the
evidence refs, author resolution, the profile panel and the lineage walk. An
untyped relation is precisely one INSPIRE did *not* call doctoral, so it is
stored and not traversed.

Acyclicity is checked exactly over the whole relation, not by a bounded walk:
a loop longer than the bound would otherwise pass unnoticed, and the first
version of that check could not fail at all because it carried the root in its
own visited path.

Supervision is a directed acyclic graph, not a tree: a person can have several
advisers, and lines rejoin. `ancestry()` walks it with a recursive CTE carrying
the visited path, so a cycle in the source cannot spin, and reports the
generation each relation was found at.

What this cannot tell you: INSPIRE records an adviser for only ~4% of its
authors, so an empty lineage is usually upstream silence rather than an
orphan. A further 5,241 records name an adviser INSPIRE has no record for;
those are counted, never matched by name.

**Wikidata supplies 854 relations INSPIRE does not have.** Wikidata states
`doctoral advisor` (P184) between items, and physics items often carry
`INSPIRE-HEP author ID` (P2930). Where both ends have one, the relation arrives
as *identifier to identifier*, with no name to match:
`hepgraph/wikidata_genealogy.py` resolves each BAI against INSPIRE and drops any
that does not resolve to exactly one record. Of 2,404 such pairs, 970 are
relations INSPIRE already records - an agreement rate that is itself the
quality check - and 854 are new, reaching 584 people the map did not hold at
all. They are served with `source_kind = 'wikidata'` and link to the item that
states them, so nothing Wikidata says is presented as something INSPIRE
published. A lead reversing a relation INSPIRE records is rejected, not served.

**Web research by language models was measured and mostly failed.** A pilot put
three weak-model agents on 18 people with instructions to cite sources. They
reported 13 high-confidence finds; verification against the cited pages upheld
**one**. Five cited the person's own INSPIRE record and quoted a
`"Doctoral Advisor:"` line that does not exist there, most of the rest
rediscovered `other`-typed relations the overlay already held, and one swapped
two record ids. The lesson is not that the agents were careless but that prose
sources let a model produce text shaped like evidence; a source keyed on
identifiers does not. Verify before storing, and prefer structured sources.

**Web research is staged, not merged.** `hepgraph/genealogy_research.py` holds
leads found off the open web in `graph_genealogy_research`: each carries the URL
it came from, a quote from that source, and why the adviser resolves to *that*
INSPIRE record rather than a same-named person. A lead whose adviser arrives as
a name instead of a record id is refused outright. Nothing in this table is
served as an INSPIRE relation, so the overlay's certificate keeps meaning what
it says; people already searched without result are remembered in
`graph_genealogy_research_miss` so the next batch does not retry them forever.
