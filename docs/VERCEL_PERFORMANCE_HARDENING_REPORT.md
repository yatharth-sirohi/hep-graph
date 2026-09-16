# Vercel performance hardening — Phase III

## 1. Starting state

| | |
|---|---|
| `main` at start | `89912cb`, equal to `origin/main`, clean tree |
| Production deployment | `hep-graph.vercel.app`, commit `89912cb` (GitHub deployments API) |
| Python suite | 448 passed, 1 xfailed |
| Branch | `deployment-performance-hardening` |

`hepgraph/hlbes.py` was not modified.

## 2. Local vs Vercel

Erin Visser → Matheus Hostert; small-team (≤10), one shared work, all years,
genealogy on. Identical filters, identical code.

| Environment | Condition | Wall | First route | Result | INSPIRE requests |
|---|---|---:|---:|---|---:|
| Local | cold | **18.2 s** | 8.8 s | **4 hops, proven** | 30 |
| Local | immediate repeat, same process | 0.72 s | 0.23 s | 4 hops, proven | 0 (30 cache hits) |
| Vercel | cold | 241.7 s (cap) | — | no route | 13 |
| Vercel | immediate repeat | 240.5 s (cap) | 137.8 s | 5 hops, not proven | 20 |

Local finds and proves a **four-hop** route: Visser → Gardiner → Isaacson →
Patrick J. Fox → Hostert. The five-hop route the deployment displayed came from
the saved snapshot's guide corridor; its proof state had made six expansions.
The brief's suspicion of a shorter route was right about the length and wrong
about the people — it runs through Fox, not Pandey or Machado.

A control the brief did not ask for but that settles the matter:

| Environment | Query | Wall | Requests |
|---|---|---:|---:|
| Vercel, poll every 1.5 s | Hostert → Pascoli (1 hop, fresh) | **19.0 s** | 4 |
| Vercel, poll every 0.25 s | same query, fresh key | **2.6 s** | 4 |
| Local | same | 1.4 s | 4 |

Same code, same deployment, same four requests. Only how often a request was
open changed. Progress was a function of poll rate.

## 3. Where 89 seconds went

The deployed job issued one INSPIRE request every 10–40 seconds while its status
polls answered in 0.13 s. The job's own coverage record explains the gaps:

```
resource_limit: request deadline elapsed during transport
```

An 8 s upstream deadline expired while the process was frozen mid-request. The
engine classified that as a transient upstream failure and backed off
exponentially — 5, 10, 20, 40 s — which is exactly the spacing of the later
request timestamps (128 s → 152 s → 191 s → 225 s). Most of the 89 s, and of
the 241 s, was spent frozen or backing off from failures the freeze itself
caused.

INSPIRE was not slow: one upstream call routed through the deployment completes
in 0.55–0.65 s. Neither was Vercel's edge: `/api/health` answers in 0.13 s.

## 4. Deployment architecture

See [`VERCEL_SEARCH_EXECUTION_AUDIT.md`](VERCEL_SEARCH_EXECUTION_AUDIT.md) for
the request flow with the runtime source. In one paragraph: the entrypoint is a
`BaseHTTPRequestHandler`; Vercel's Python runtime serves it from a
`ThreadingHTTPServer` inside the function instance and ends the invocation once
the response is written; with no invocation open the process is frozen. The
search ran on a daemon thread that nothing registered with the platform, so it
ran only during the ~130 ms each poll was open — a 9 % duty cycle at a 1.5 s
poll interval.

## 5. Cache and state scope

Everything is per process: job registry, engine sessions, the response cache,
the request pacer, in-flight coalescing, endpoint preparation. Every one of 145
polls of the cold search found its job on the answering process, so instance
affinity held in practice; it is observed behaviour, not a guarantee, and the
browser now recovers from the case where it does not hold (§ 11).

## 6. Request limiter — process-local

Ten requests per five seconds, enforced per process. A single serving instance
stays under INSPIRE's published fifteen. Two instances serving concurrently
would not coordinate; documented, not fixed in this phase, pending measurement
of how often the platform actually scales out for this traffic.

## 7. Single-flight — process-local

Identical concurrent requests coalesce within a process only. Same status as § 6.

## 8. Why the UI said "100 works"

`works_retrieved` counts distinct literature records in the search's evidence
store. Across the cold run's polls it read 43 → 60 → 100 → 266 → 283; the
screenshot caught it passing 100. No production path pages at 100 — the
literature page ceiling is derived from the mode's author bound (855 in
small-team mode) and profile lookups are pinned to 25.

## 9. N+1 audit

Per-layer upstream counts for the local cold Erin → Hostert run: 17 author
lookups (profile hydration, batched up to 25 per request), 12 literature pages,
1 endpoint-pair query, 0 facets. Thirty requests certified twelve complete
neighbourhoods and 35 explored people: 2.5 requests per person, no per-work
fan-out. The deployment showed the same shape at a fraction of the rate.

## 10. Genealogy cost

Local cold, Erin → Hostert, genealogy **off**: 70.2 s, 68 requests, 70 people —
slower than with genealogy on (18.2 s, 30 requests). The doctoral overlay
contributed a useful edge here; it is not a cost to remove.

## 11. What changed

Nothing in `hlbes.py`. Nothing in how neighbourhoods are certified. The
changes are to *when the engine gets to run*.

**Searches advance inside requests** (`hepgraph/search_jobs.py`). `start()`
runs a bounded first slice (3 s) before it answers, so a direct connection is
usually returned by the start request itself. Every poll runs a 5 s slice
before answering; `continue` runs one immediately. Exactly one request drives
a given job at a time, enforced by a per-job lock; a poll that arrives while
another is driving reads the current state. A transient upstream failure
schedules the next attempt instead of sleeping inside somebody's request.

**The engine's ownership contract changed from a thread to a lock.**
`DeepSession` required a single owner thread because its in-memory SQLite
connection was thread-bound. The invariant that matters is that calls never
overlap; the connection is opened `check_same_thread=False` and the driving
lock provides the exclusion. The test fakes now assert exactly that.

**The slice allowance starts work; it never truncates a request.** The first
version handed the slice deadline to the HTTP client, so a request begun late
in a 5 s slice got a one-second transport timeout or was refused by the pacer,
and each was logged as an upstream failure — which the continuation logic then
backed off from for 5, 10, 20 s. Measured over local HTTP: 2 of 70 polls
actually drove, first route at 24 s instead of 9. Now a started request keeps
the full network timeout, a refusal caused by our own deadline is tagged by the
client and ends the slice as an unlogged checkpoint, and only a *new* entry in
the failure log earns a retry delay.

**Abandoned searches expire.** A job advances only when polled, so a closed
tab left a job `searching` for ever and its TTL never started; two of them
would have held both active slots and refused every later search. A job not
driven for two minutes is stopped honestly and releases its slot.

**Endpoint preparation runs inside its POST** (`hepgraph/prefetch.py`). Its
worker pool had the identical freeze problem. It costs the preparing request
about two seconds and actually happens.

**The browser restarts a search whose job is unknown to the answering
process** (`static/app.js`), at most twice, and says so in the progress line.
Job state is per process; every measured poll reached the same one, but
nothing guarantees it.

**Forensics.** `/api/health` reports the build commit, deployment id, region
and a per-process instance id; every JSON response carries the instance id in
`X-HEP-Instance`.


## 12. Performance after

## 13. Tests

| | |
|---|---|
| Python suite at start | 448 passed, 1 xfailed |
| Python suite now | **458 passed, 1 xfailed** |
| `hlbes.py` | unchanged; the 24,000-pair NetworkX differential is re-run in § 12 |

Tests that encoded the old thread model were ported, not deleted: the fakes
assert that no two calls on a session overlap (the invariant that matters)
instead of a thread identity, and tests that need a slice in flight drive one
on a helper thread. New tests cover the six review findings, the idle reaper,
the checkpoint-versus-failure distinction, the deadline handling in `_fetch`,
and inline preparation.

The known identity `xfail` (unrelated-surname byline carrying a profile's
`$ref`) is unchanged; see § 15.


## 14. Agent review

Implementation: Claude Fable 5.1 (this session). Review: separate Claude Code
agents with no access to the implementer's reasoning, instructed to run code
rather than reason about it. No OpenAI model was available or used.

**Round 1, independent correctness reviewer** — attacked the request-driven
driver, the relaxed session ownership, the inline preparation, and the browser
restart. It re-ran everything against the tree as it stood at the end of the
review because the tree moved under it. Six confirmed defects, all in code
written in this phase, each reproduced by a script before I touched it:

1. `cancel()` landing between a slice's cancel check and its continuation block
   left a job `searching`, undrivable, unresumable and unreapable — an active
   slot and an engine session held until the process died. The continuation
   block now re-checks under the lock `cancel()` writes with.
2. `resume()` did not stamp `last_driven_at`, so a search continued after the
   user had read its result for a few minutes was reaped as abandoned by any
   concurrent request — sometimes by `resume()` itself.
3. The same stamp was written only *after* a slice, so the reaper could cancel
   a slice already in flight at the idle boundary.
4. A poll decided it was due, released the registry lock, then took the drive
   lock; a cancel in between finalized the job and the poll opened a fresh
   engine session nobody would ever close.
5. Counting requests as progress meant a dead upstream never registered as
   stalled: flat five-second retries for two hours where the old worker backed
   off and paused.
6. A victim retired while its last slice was releasing the drive lock kept an
   open session with no owner.

Also: the browser's restart-on-404 left a fresh server job running if the user
moved on mid-restart; a completed inline preparation answered 202. The reviewer
confirmed by inspection that the lock discipline has no inversion (every
registry→drive path acquires non-blocking), that no SQLite access escapes the
drive lock, that `_slice()` preserves the session-wide ceilings, and that
`hlbes.py` is byte-identical to `main`.

Every item was fixed and pinned by a regression test in
`tests/test_search_jobs.py` before the next round.


## 15. Remaining bottlenecks

## 16. Git and deployment
