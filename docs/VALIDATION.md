# Validation and performance report

Validated 15 September 2026 on a 10-core Apple Silicon Mac (`Mac16,12`), macOS
25.6, with Python 3.14.7. Runtime code supports Python 3.11 and newer. All
numbers below are measured observations from the final Desktop source; no
counts or timings are estimated.

## Acceptance result

The final MVP passed its offline suites, browser suites, bounded live demo set,
and known two-hop live set. Every live route listed below passed an independent
response validator that checks endpoint identities, path continuity, repeated
nodes, edge-to-hop pairing, distinct works, full author-count filters,
qualifying document types, date bounds, canonical INSPIRE links, doctoral
direction/source, and the known Bergmann collision IDs.

| Verification | Result |
| --- | ---: |
| Python unit, graph, independent NetworkX, API, cache, concurrency, continuation, identity and service tests | **354 passed; final repeat runs 10.70 s and 10.72 s** |
| Browser acceptance, accuracy, evidence, preparation, continuation and resilience checks | **70/70 passed** |
| Final professor-demo live cases | **7/7 passed** |
| Final known two-hop live cases | **6/6 passed** |
| Uncaught browser errors in the automated suites | **0** |

The Python suite makes no network calls. Live checks are explicit and remain
outside ordinary test collection, which keeps clean-clone testing deterministic.

## Final professor-demo live run

The run used the default Small-team definition unless the row says Large-team.
“Exact” means a global shortest-path proof under the selected definition;
deeper routes are intentionally labeled verified rather than globally exact.

| Pair | Mode | Result | Wall time | App retrievals | New upstream calls | Repeat |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Hostert → Pascoli | Small-team | 1 hop, exact | 3.035 s | 4 | 3 | 1.4 ms |
| Hostert → Einstein | Small-team | 8 hops, verified | 12.131 s | 15 | 12 | 3.1 ms |
| Hostert → Dirac | Small-team + genealogy | 4 hops, verified | 3.040 s | 10 | 3 | 3.8 ms |
| Feynman → Wheeler | Small-team | 1 hop, exact | 1.008 s after endpoint preparation | 4 | 1 | 1.3 ms |
| Witten → Erin Visser | Small-team | 7 hops, verified | 50.520 s | 52 | 50 | 1.5 ms |
| Hostert → John Ellis | Small-team | 3 hops, verified | 6.052 s | 10 | 6 | 1.8 ms |
| Georges Aad → Braden Abbott | Large-team | 1 hop, exact | 6.118 s | 4 | 3 | 4.7 ms |

An “app retrieval” is a logical search request. The shared cache can satisfy it
without contacting INSPIRE. For the prepared Feynman–Wheeler case, three exact
author-profile reads were cache hits, so the connection search made one new
upstream request. The preparation itself made the two intentional identity
requests earlier while the endpoints were being selected.

The Witten case expanded 31 people and retrieved 218 works. The two historical
Hostert cases reused previously retrieved endpoint information: Dirac retrieved
37 works; Einstein retrieved 52. Repeat times refer to reconnecting to the same
completed retained job, not recomputing it.

## Known two-hop exactness regression

These cases exercise the proof boundary. A verified common collaborator proves
a two-hop route; exhaustive direct-pair pagination must also prove that no
one-hop connection qualifies before the app may label it globally shortest.

| Pair | Verified route | Time | Exact? |
| --- | --- | ---: | --- |
| Hawking → Vafa | Hawking — Strominger — Vafa | 7.063 s | Yes |
| Penrose → Strominger | Penrose — Hawking — Strominger | 5.052 s | Yes |
| Chandrasekhar → Teller | Chandrasekhar — Fermi — Teller | 8.092 s | Yes |
| Glashow → Ellis | Glashow — Schramm — Ellis | 6.072 s | Yes |
| Salam → Luttinger | Salam — Ward — Luttinger | 8.091 s | Yes |
| Kobayashi → Yamawaki | Kobayashi — Kugo — Yamawaki | 8.088 s | Yes |

All six passed, all six reported `global_shortest_proven: true`, and all six
reused their completed job in 1.5–2.4 milliseconds.

## Independent evidence review

The route validator is intentionally separate from the production graph code.
A second raw-source auditor fetched exact current author profiles and exact
literature records directly from INSPIRE, then checked both stable endpoint IDs
against each supporting byline.

- 180 unique public records were checked across ten representative historical
  and two-hop routes.
- A separate repaired Erin Visser → Einstein audit checked 29 unique records
  covering all ten displayed edges.
- The original false four-hop Visser → Einstein candidate was rejected because
  a modern Philip/P. Bergmann byline was incorrectly attached upstream to the
  historical Peter Gabriel Bergmann profile. The repaired ten-hop route retains
  only source-supported edges and makes no global-shortest claim.
- Chen-Ning Yang's current adviser array crosses the names and record IDs for
  Enrico Fermi and Edward Teller. HEP Graph withholds those conflicting native
  doctoral references instead of swapping or guessing them.

The frozen public provenance fixture independently reconstructs all 1,180 saved
works, 5,249 people and 43 doctoral records. Five whole-snapshot evidence tests
hydrate the fixture into an in-memory SQLite database and compare it with the
published saved JSON without importing the production normalizer.

See [Identity collisions](IDENTITY_COLLISIONS.md) for the detailed cases and
[Historical sources](HISTORICAL_SOURCES.md) for the explicit genealogy overlay.

## Adversarial coverage

The permanent live manifest contains 29 exact-ID cases spanning:

- direct and known two-hop connections;
- modern theory, neutrino, collider and astrophysics crossings;
- Feynman, Dirac, Einstein, Bohr, Landau, Hawking, Penrose, Weinberg, Witten,
  ’t Hooft, Gell-Mann, Schwinger, Fermi and Oppenheimer;
- Small-team, Large-team, All-papers, genealogy on/off and repeated-work modes;
- mega-collaboration, sparse, prolific, alias/diacritic and identity-collision
  behavior.

Cases with an independently known route assert a maximum hop count. Optional
stress cases accept a correctly labeled incomplete result; they still reject
invalid evidence, identity shortcuts, filter violations and false `no_path`
claims. The deliberately restrictive Hostert → Feynman `min_shared=2` stress
case exceeded its 180-second test allowance and was cancelled. It is retained
as an honest-incomplete stress case and is not used in the professor sequence.

## Saved-snapshot performance

The public benchmark was rerun without the excluded local SQLite database; it
hydrated only the 622 KB compressed public provenance fixture.

| Measurement | Result |
| --- | ---: |
| Read 2.30 MB snapshot | 1.44 ms |
| Parse snapshot | 8.15 ms |
| Build default graph (5,249 people, 1,153 eligible works) | 11.41 ms |
| 20 representative cold path calls, median / p95 | 0.0069 / 0.0408 ms |
| 20 repeat path calls, median / p95 | 0.0032 / 0.0224 ms |
| 100 deterministic random path calls, total | 5.52 ms |
| Exact harmonic centrality | 30.40 ms |
| Exact eccentricity on largest non-isolated component | 24.73 ms |
| Deterministic sampled betweenness | 19.68 ms |

The saved ATLAS work preserves a total author count of 2,932. Its first and
last resolved authors are one exact hop in All-papers mode and have no route in
the saved Small-team graph. This verifies that the filter uses the original
paper total rather than the number of currently displayed people.

## Cache, concurrency and continuation checks

The final process reported an 8 MiB shared-response ceiling and a separate 8
MiB retained-result ceiling. After two endpoint preparations and one direct
query, the response cache held 148,017 serialized bytes in seven entries.
Three search-time author reads were served from the exact-ID record cache.

Regression checks cover:

- in-flight request coalescing with independent caller deadlines;
- no error or missing-record negative cache poisoning;
- exact numeric author-record reuse only when every requested ID is fresh;
- 15-minute LRU/TTL expiry, 256 entries and 8 MiB aggregate response data;
- two active searches, four resumable sessions and 32 compact final results;
- continuation on the same worker-owned in-memory SQLite session;
- refresh/reconnect to a retained job and immutable filter keys;
- immediate cancellation, late-response isolation and bounded shutdown;
- a single oversized progress or final result becoming an explicit retained
  `resource_limit` response while remaining below the strict result-byte cap.

## Browser coverage

The Playwright suites exercised Live and Saved source switching, all three
paper modes, selected-author preparation, no preparation while typing, exact
and verified labels, incomplete states, Continue, Stop, stale-response guards,
same-pair PhD context, genealogy-only arrows, evidence links, JSON/SVG exports,
share-link restoration, profile pages, scoped centrality and a 390-pixel mobile
layout. All 70 checks passed with zero uncaught browser errors.

A separate real, non-mocked browser walkthrough selected Feynman and Wheeler
through live author search, displayed the exact one-hop result, opened two
paper records and the doctoral context, copied and reloaded the share URL,
downloaded a 9,559-byte JSON export and a valid 2,262-byte SVG, and observed no
browser warnings or errors. A real Hostert → Feynman `min_shared=2` search was
then stopped from the UI; the page immediately showed “search incomplete; no
no-path conclusion.” The Saved demo restored both five-hop alternatives and
calculated the explicitly scoped 5,249-person coauthor-degree table.

An initial attempt to run two heavy saved-browser suites simultaneously reached
the service's intended one-minute request-rate limit. The UI showed that limit
explicitly. The final acceptance and accuracy suites were rerun sequentially
against a fresh process and passed 17/17 and 11/11 respectively.

## Limits and interpretation

- INSPIRE is incomplete and can contain incorrect stable-profile links. A found
  route is evidence-backed; a missing result is not proof of disconnection.
- Live zero- and one-hop routes are globally exact. A live two-hop route is
  globally exact only after direct-pair exhaustion. Deeper routes remain
  verified unless a future algorithm supplies a broader proof.
- Live latency varies with upstream availability and rate limits. The Saved
  demo is the deterministic offline fallback.
- Centrality applies only to the saved snapshot and is not a ranking of all HEP.
- No complete INSPIRE database, multi-gigabyte mirror or unbounded disk cache
  was created. Live cache and search state disappear when the process stops.
