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

Everything existing still passes: BENCH_PY_RESULT.

## 5. Agent review

AGENT_REVIEW_SECTION

## 6. Benchmarks

Cadence mirrors the browser (poll again after 0.25 s when the previous poll
took over 1 s, else 1.5 s). Times are from the client's clock at the start
request; server `metrics` agreed to within 20 ms. No user action in any run.

### 6.1 Local (`python -m hepgraph.server`, fresh process, cold cache)

LOCAL_BENCH_TABLE

### 6.2 Production (`hep-graph.vercel.app`, after merge)

VERCEL_BENCH_TABLE

## 7. Acceptance criteria

ACCEPTANCE_TABLE

## 8. Git and deployment

GIT_SECTION
