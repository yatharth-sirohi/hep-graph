# Progressive route delivery — Phase IV

## 1. Starting state

| | |
|---|---|
| `main` at start | `be57249`, equal to `origin/main`, clean tree |
| Production deployment | `hep-graph.vercel.app`, commit `be57249` (`/api/health` → `runtime.git_commit`) |
| Python suite | 461 passed, 1 xfailed |
| Branch | `progressive-route-delivery` |

`hepgraph/hlbes.py` and `hepgraph/deep_search.py` were not modified. The
engine already returned the moment a route passed validation and already
refused to re-report an equal-length route on continuation; nothing in it
needed to change to expose candidate-route events.

## 2. The problem being fixed

Before this phase a search that found a verified route **paused**. The job
went to `status: ok, can_continue: true`, the browser drew the route with
"exact search incomplete", and proving shortestness required the user to
press *Continue exact search* — twice, for Erin Visser → Matheus Hostert
(Phase III report, §12). The route on screen was correct; the wait for the
proof was the user's problem to manage.

The other half of the problem was invisible: while a search was still
running, the browser rebuilt the route cards on **every poll** (`renderPath`
was called from `consumeDeepResponse` for each `searching` response), so an
evidence panel a reader had opened closed again 1.5 s later.

## 3. Design

### 3.1 `best_route` is the server's; `displayed_route` is the browser's

The server publishes, on every job state, the best route the engine can
currently stand behind. The browser decides which route to show and never
swaps it under the reader:

| Side | Owns | Rule |
|---|---|---|
| `SearchJobs` (server) | `best_route`, `route_status`, `sequence_number`, `events`, `metrics` | derived in one place from the state being installed |
| `static/app.js` (browser) | `job.displayed`, `job.best`, `job.sequence`, the pending offer | a shorter `best_route` is *offered*; only a click changes `displayed` |

Authoritative job state lives where it did after Phase III: in the memory of
the server process that owns the job, advanced inside HTTP requests. Nothing
about delivery needed a new store; the browser holds only a job handle
(sessionStorage) and its own display choice.

### 3.2 One choke point: `SearchJobs._deliver`

Every mutation of a job's public state already passed through
`_replace_job_data` (slice results, progress publishes, cancel, resume, idle
reaping, retention-limit fallbacks, session retirement). `_deliver` runs
there, under `self.lock`, on the private candidate copy, and stamps:

| Field | Meaning |
|---|---|
| `sequence_number` | strictly increasing per job; minted only for states actually installed — a candidate refused by the retained-bytes cap leaves the counter and the timeline untouched |
| `best_route` | `{route_id, hops, alternatives, exact, found_at_seconds, version}` or `null`; `exact` is true only when the engine's own `global_shortest_proven` is true for that route |
| `paths[i].route_id` | SHA-1 (16 hex) of the ordered people IDs — the same route has the same identity in every state |
| `route_status` | `searching_no_path` · `verified_route_found` · `exact_route_proven` · `verified_search_stopped` · `search_incomplete` · `no_path` |
| `events` | `search_started`, `first_path_found`, `path_improved` (hops strictly decreased), `route_withdrawn`, `exact_proven`, `search_paused`, `search_resumed`, `search_stopped`, `search_finished`; bounded to 64 keeping the first entry |
| `metrics` | `time_to_first_verified_path`, `time_to_best_route`, `time_to_exact_proof`, `improvements`, `first_hops`, `best_hops`, `elapsed_seconds` (seconds since the job was created, by the jobs clock) |

An equal-length route replacing the primary one moves `best_route.route_id`
but raises no event and counts no improvement.

`route_status` is a pure function of `(status, has_route, proven)`:
`searching` → found/no-path; `cancelled` → `verified_search_stopped` if a
route exists else `search_incomplete`; `no_path` only when the engine said
so; `ok` with a proven route → `exact_route_proven`; everything else,
including a verified route whose shortestness is open, → `search_incomplete`.

### 3.3 Continue to the proof by itself

`_run_slice`'s automatic-continuation rule dropped its `status != 'ok'`
clause behind a new policy flag, `prove_after_route` (default true, reported
in `search_policy` and `/api/cache`). A verified route therefore leaves the
job `searching` with `progress.stage = prove_shortest`, still under every
existing guard: `max_auto_seconds`, stall detection (`max_stalled_runs`), the
memory ceiling, the idle reaper, and the cancel/retire re-check under the
lock. `prove_after_route=False` restores the pause-and-Continue behaviour
(covered by a test).

### 3.4 Browser state machine

`routeState(data, job)` maps the server state plus the local display choice
onto the states the brief named; `#connection-results[data-route-state]`
exposes it for tests and assistive tooling.

| State | When | Title |
|---|---|---|
| `IDLE` | no job | — |
| `SEARCHING_NO_PATH` | `searching_no_path` | progress box only |
| `VERIFIED_ROUTE_FOUND` | `verified_route_found`, displayed = best | *Verified route shown · N hops · looking for a shorter one* |
| `BETTER_ROUTE_AVAILABLE` | `best_route.hops < displayed.hops` (any server status) | *Verified route shown · N hops · shorter route available* + offer bar |
| `EXACT_ROUTE_PROVEN` | `exact_route_proven` and displayed hops = proven hops | *Exact shortest path · N hops* |
| `VERIFIED_SEARCH_STOPPED` | `verified_search_stopped` | *Verified route · N hops · search stopped* |
| `SEARCH_INCOMPLETE` | limits hit, with or without a route | existing labels, *Continue* offered when `can_continue` |
| `NO_PATH` | `no_path` | existing label |

Rules enforced in `consumeDeepResponse`:

- an update with `sequence_number` lower than the last applied one is ignored
  whole (its polling obligation is still honoured);
- first route → displayed at once;
- shorter best → offer *"Shorter route found: 5 hops → 4 hops [Show shorter
  route]"*; if the proof arrived with it, *"Exact shortest path found: 4 hops
  [Show exact route]"*; the cards do not change;
- equal-length best → nothing (not an improvement); if the proof closes on
  that length, the displayed route is labelled exact too, because a proof is
  about a hop count, not a particular route;
- `route_withdrawn` event and the displayed route is no longer the best →
  the display is replaced (a retracted route must not stay up as verified)
  with a message saying why; without such an event (a job restarted on
  another server that has not re-found the route yet) the display stays;
- cards are rebuilt only when the displayed route changes;
  `renderPathHeading` refreshes title/meta/message on other polls;
- Stop keeps the displayed route, labels it `VERIFIED_SEARCH_STOPPED`, sends
  one cancel, polls no more; a pending offer stays (that route is verified
  too).

The offer lives in `#route-update`, `role="status" aria-live="polite"`, a
single line and one button above the result; no modal, no animation, no
auto-scroll. Timing is shown in the meta line: *first route after 11s,
proven shortest after 24s*.

Exports: `path_result` is the displayed route (it is `state.lastPath`);
`route_delivery` names `route_status`, `route_state`, `displayed_route_id`,
`displayed_is_best`, `best_route`, `sequence_number`, `metrics`, `events`.
The share link is the query URL as before; opening it re-runs the query and,
in the same tab session, re-attaches to the running job.

Refresh: the retained job handle is polled instead of a new job being started
(the shared URL restores the pair and re-runs the query); the browser has no
memory of its earlier display choice, so it shows the server's best route.

## 4. Tests

| File | What it pins |
|---|---|
| `tests/test_progressive_delivery.py` (14) | first → improved → proven without a Continue; strictly monotonic `sequence_number`; stable `route_id`; equal-length not an improvement; Stop preserves route (`verified_search_stopped`), Stop before a route is `search_incomplete` not `no_path`; legacy `prove_after_route=False` pauses; withdrawn route reported; progress-published route versioned; every state JSON round-trips; refused oversized state does not advance the sequence; HTTP responses carry the fields; invalid policy rejected |
| `tests/browser_progressive.cjs` (7, Playwright) | first route shown at once, progress continues, opened evidence survives a poll; shorter route offered not swapped, ARIA attributes, click shows it; stale version ignored, proof offered not forced, exact labels after click; Stop keeps the route, one cancel, no more polls; refresh re-attaches to the job and shows the best route; JSON export names displayed vs best; equal-length route not announced |
| `tests/browser_deep.cjs` (12) | unchanged scenarios; the early-route mock now uses the server's `paths` + `best_route` shape |

After the review fixes: **477 passed, 1 xfailed** (the pre-existing D6 identity
case), 10/10 progressive and 12/12 deep-search browser checks, Chromium via
Playwright 1.63 against a local server that only served the UI.

## 5. Agent review

Implementation, correctness review and adversarial testing were done by
separate Claude Code agents (Claude Fable 5.1); no OpenAI model was involved.
Both reviewers worked read-only against commit `9870e70`.

**Correctness reviewer** — 7 findings, none high; all addressed in `7b0bf88`:

| # | Severity | Finding | Resolution |
|---|---|---|---|
| 1 | medium | Browser titled the displayed route *Exact shortest path* when the proven bound was a different (longer) hop count — reachable via the cross-server restart path | `routeState` never returns `EXACT_ROUTE_PROVEN` when displayed and best hop counts differ; browser test *a proof about a longer route does not label the shown route exact* |
| 2 | medium | Client treated *any* `route_withdrawn` event in the timeline as a withdrawal of the route on screen, so retracting an offered route cleared a still-verified displayed one with a false message | Only an event naming `displayed.routeId`, in a version newer than the last applied, takes the display down; two browser tests |
| 3 | medium | Automatic continuation ignored `global_shortest_proven`; a two-hop route proven by direct-pair exhaustion arrives with `can_continue: true` and was relabelled *searching for a shorter one* while requests kept being spent | Proven result is terminal in `_run_slice`; test `test_a_route_the_engine_already_calls_shortest_is_terminal_even_if_the_bound_is_open`; confirmed live on Witten → Ellis (16.0 s → 8.2 s) |
| 4 | low | `cancel()` on a finished proven job relabelled it `verified_search_stopped` with `exact: true` | Cancel of an `exact_route_proven` result returns it unchanged |
| 5 | low | Withdrawal detection relied on a client heuristic rather than the server's report | Server already emits `previous_route_id`; client now uses it (see 2) |
| 6 | low | `time_to_first_verified_path` keeps naming a later-withdrawn route | Kept as documented: it records when a route first passed verification; the timeline shows the withdrawal |
| 7 | low | Withdrawal explanation flashed for one poll | Kept on the job (`job.note`) until the displayed route changes; browser test |

Also removed: the unused `can_continue` parameter of `_route_status`, and the
duplicate `best_result` payload in retained job data.

**Adversarial tester** — 61 scratch tests (never added to the repository),
53 passed at `9870e70`; the failures reduce to six items:

| # | Severity | Finding | Resolution |
|---|---|---|---|
| 1 | medium | Same as reviewer's #3 | fixed as above |
| 2 | low | `time_to_best_route > time_to_exact_proof` after proof → withdrawal → new route (`exact_at` write-once) | withdrawal clears `exact_at`; test `test_withdrawing_a_proven_route_withdraws_its_proof` |
| 3 | low/medium | `paths` as a truthy non-list (`7`, `True`) raised `TypeError` out of `_deliver` → HTTP 500 on every poll | non-list `paths` is treated and published as no route |
| 4 | low | `route_status: no_path` published beside a non-null `best_route` | a route always wins over `no_path` |
| 5 | low | a proof published via the progress callback and then retracted by the slice result left `time_to_exact_proof` set — contrived: the real engine's progress payload carries no proof flag | not changed; noted |
| 6 | low | stale `global_shortest_proven` inherited by a new route when a result omits the key — the real `_result()` always emits it | unreachable after fix 1; noted |

Suspicious items it flagged: negative `hops` accepted (now rejected, ≥ 0
required); the idle reaper cancelling a search whose tab was throttled for
over `idle_seconds` (pre-existing Phase III behaviour, unchanged); two
sequence numbers minted by one `cancel()` (harmless: both states are real).
It held everything else it attacked: monotonic sequences across cancel,
resume, idle reaping, retention fallbacks, session retirement and engine
exceptions; `exact` only from a literal `True`; bounded, prefix-stable event
timelines under 400 route flips and 200 improvements; stall guards on an
engine that returns `ok` for ever; 16 concurrent pollers with a cancel/resume
storm; engine results that smuggle delivery fields are overwritten.

## 6. Benchmarks

Cadence mirrors the browser (poll again after 0.25 s when the previous poll
took over 1 s, else 1.5 s). Times are from the client's clock at the start
request; server `metrics` agreed to within 20 ms. No user action in any run.

### 6.1 Local (`python -m hepgraph.server`, fresh process, cold cache)

| Pair | Route | First verified route | Best route | Proven shortest | Improvements | Requests |
|---|---|---:|---:|---:|---:|---:|
| Feynman → Wheeler | 1 hop (direct, genealogy) | **1.5 s** | 1.5 s | 1.5 s | 0 | 4 |
| Hostert → Pascoli | 1 hop | **8.2 s** | 8.2 s | 8.2 s | 0 | 4 |
| Witten → Ellis | 2 hops (via Hanany) | **8.2 s** | 8.2 s | 8.2 s | 0 | 6 |
| Erin Visser → Hostert | 5 → **4 hops** (Gardiner, Isaacson, Fox) | **11.2 s** | 14.0 s | 24.1 s | 1 | 38 |
| Hostert → Feynman | 3 hops (Farzan, Cline) | **16.7 s** | 16.7 s | 18.4 s | 0 | 17 |
| Einstein → Dirac | 6 → **5 hops** (Bergmann, Sachs, Hawking, Sciama) | **9.6 s** | 32.0 s | 38.4 s | 1 | 56 |
| Dirac → Feynman | 4 hops (Eden, Brueckner, Bethe) | **12.0 s** | 12.0 s | 15.4 s | 0 | 21 |
| Hostert → Uppu | 5 hops (Conrad, Barlow, Jones, Paesani) | **278.0 s** | 278.0 s | 282.3 s | 0 | 260 |

Zero upstream failures in every run. Every run ended `exact_route_proven`
without a single user action; before this phase Visser → Hostert needed two
*Continue* presses for the same proof (Phase III report §12).

Two runs show the delivery layer doing exactly what it is for:

- **Einstein → Dirac**: a six-hop route on screen at 9.6 s, *"Shorter route
  found: 6 hops → 5 hops"* at 32 s, *"Exact shortest path found: 5 hops"* at
  38 s. Under the previous behaviour the reader saw the six-hop route, then a
  paused search.
- **Visser → Hostert**: five hops at 11.2 s, four at 14.0 s, proven at 24.1 s.

**Hostert → Uppu is engine-bound, not delivery-bound.** The timeline shows
HLBES holding an upper bound of 4 from 73 s to about 180 s; that candidate
never passed identity validation, the identity guard then removed a node and
the proof was rebuilt (`complete_neighborhoods` 62 → 2), and the only route
that survived validation appeared at 278 s. The layer built here never showed
the unverified four-hop candidate — which is the rule. 260 requests at the
0.5 s INSPIRE pacing is a floor of 130 s for that search regardless of how
results are delivered; shortening it is engine work (Phase III §15) and out
of scope.

**Witten → Ellis before the review fix** finished at 16.0 s although the
two-hop route was proven at 8.6 s: the engine proves a two-hop route by
exhausting the direct pair while the HLBES bound is formally open, so it
returned `can_continue: true` and the new continuation rule kept searching for
a shorter route that cannot exist. Found by the correctness reviewer, confirmed
live, fixed (§5); the re-run finished at 8.2 s.

### 6.2 Production (`hep-graph.vercel.app`, after merge)

Production served `7b0bf88` (checked through `/api/health` before the first
run); every poll of every search reached the same instance (`X-HEP-Instance`).

| Pair | Route | First verified route | Best route | Proven shortest | Improvements | Requests | Polls |
|---|---|---:|---:|---:|---:|---:|---:|
| Hostert → Pascoli | 1 hop | **1.9 s** | 1.9 s | 1.9 s | 0 | 4 | 1 |
| Witten → Ellis | 2 hops | **10.3 s** | 10.3 s | 10.3 s | 0 | 6 | 2 |
| Erin Visser → Hostert | 5 → **4 hops** | **12.4 s** | 15.3 s | 28.1 s | 1 | 38 | 7 |
| Hostert → Feynman | 3 hops | **20.1 s** | 20.1 s | 26.6 s | 0 | 23 | 6 |
| Einstein → Dirac | 6 → **5 hops** | **10.3 s** | 34.8 s | 43.7 s | 1 | 56 | 9 |
| Hostert → Uppu | 5 hops | **729 s** | 729 s | 749 s | 0 | 273 | 103 |

Zero upstream failures. Phase III's Visser → Hostert needed a 9.6–12.1 s
first route plus two Continue presses to reach the proof; the same proof now
arrives 28 s after the click with no action, and the shorter route is
announced at 15 s.

**Hostert → Uppu on Vercel took 2.6× its local time (729 s vs 278 s) for the
same 260–273 requests.** The per-poll record explains it: each ~5 s slice
performed only 2–3 INSPIRE requests and the poll itself took 7.05 s on
average (max 13.7 s). At ~0.6 s per request that is under 2 s of network per
slice; the rest is CPU in the process between requests, and it grows with the
evidence retrieved (this search accumulated over ten thousand works). The
suspect is the materialised snapshot — `build_snapshot`, the identity guard
and `Graph()` — which is invalidated after every fetch and rebuilt on the
next neighbourhood query, so a long search pays an O(evidence) rebuild per
request. Phase III profiled a short search and found HLBES CPU rounding to
zero; that remains true, but it is not the whole per-request cost on a long
one. This is the largest measured bottleneck left and is recorded here for the
next phase; it is not a delivery-layer issue, and the delivery layer behaved
correctly throughout (the unverified 4-hop candidate that HLBES held as an
upper bound from 111 s to 365 s was never shown).

## 7. Acceptance criteria

| # | Criterion | Evidence |
|---|---|---|
| 1 | First verified route shown immediately, before the proof | every benchmark row: first route at 1.5–16.7 s (Uppu 278 s, engine-bound), proof later; browser test *first verified route appears at once* |
| 2 | Exact search continues in the background | job stays `searching` with `stage: prove_shortest`; every run ended `exact_route_proven` with no user action |
| 3 | Shorter route announced, never auto-swapped | browser tests *a shorter route is announced and never swapped in by itself*, *a stale version is ignored and the proof is offered, not forced*; Einstein → Dirac and Visser → Hostert live |
| 4 | `best_route` and `displayed_route` separate | server `best_route` / browser `job.displayed`; export names both |
| 5 | Stop preserves the verified route | `test_stop_preserves_the_verified_route_and_names_the_state`; browser test *stop keeps the verified route on screen* |
| 6 | Exact proof while viewing an older route is offered, not forced | browser test (proof offer text *Exact shortest path found: 3 hops*); stale/equal/longer cases covered |
| 7 | Monotonic versioning, stale updates ignored | `test_sequence_numbers_are_strictly_monotonic_and_route_ids_stable`, refused-state test, stale browser test |
| 8 | Equal-length routes are not improvements | `test_an_equal_length_route_is_not_an_improvement`; browser test |
| 9 | Metrics T_first / T_best / T_exact with improvement timeline | `metrics` + `events` on every state; §6 tables |
| 10 | Existing exactness tests intact, HLBES untouched | `hlbes.py`, `deep_search.py` byte-identical; 477 passed, 1 pre-existing xfail |
| 11 | Exports / share reflect the displayed route with `route_status` | `route_delivery` block; browser test *the export names the displayed route and the delivery state* |
| 12 | Refresh restores the best route | browser test *a refresh restores the server's best route* (retained job polled, no new job) |
| 13 | Vercel-deployed build works | preview for `9870e70` built (`Success`, SSO-protected as before); production at `7b0bf88` measured in §6.2 |

## 8. Git and deployment

| | |
|---|---|
| Branch | `progressive-route-delivery`, three commits: `9870e70` (feature), `7b0bf88` (review fixes), this report |
| `main` | fast-forwarded to `7b0bf88` and pushed; report committed on `main` afterwards |
| Production | `hep-graph.vercel.app` served `7b0bf88` (`/api/health` → `runtime.git_commit`) before and during §6.2 |
| Repository | private; no force-push, no history rewrite; no secrets, credentials or absolute local paths committed |

Not done, deliberately: the share link still encodes the query, not a route
(a route is evidence held in one server process's memory; the export carries
it). The equal-length alternative set shown for a displayed route is refreshed
only when the primary route is unchanged. Hostert → Uppu's 278 s first route is
an engine matter (identity-guard proof rebuild) recorded here for the next
phase, not a delivery defect.
