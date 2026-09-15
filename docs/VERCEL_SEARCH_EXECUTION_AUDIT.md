# How a deep search executes on Vercel

Measured on 2026-09-15 against the production deployment
`hep-graph.vercel.app` at commit `89912cb`, verified equal to `origin/main`
through the GitHub deployments API. Every number below came from a request,
not from a document.

## The observation that started this

Erin Visser → Matheus Hostert, small-team mode, one shared work, all years,
genealogy on, took ~89 s on the deployment after exploring twelve people. The
same search locally:

| | Wall | Result | INSPIRE requests |
|---|---:|---|---:|
| Local, cold | **18.2 s** | 4 hops, **proven** | 30 |
| Local, immediate repeat (same process) | 0.72 s | 4 hops, proven | 0 upstream (30 cache hits) |
| Vercel, cold | **241.7 s** (capped) | no route | 13 in 222 s of search time |
| Vercel, immediate repeat | 240.5 s (capped) | 5 hops at 138 s, not proven | 20 |

Local finds and proves a **four**-hop route (Visser → Gardiner → Isaacson →
Patrick J. Fox → Hostert). The deployment's five-hop route came from the saved
snapshot's guide corridor, not from the proof: its HLBES state had made six
expansions.

## Where the time went

Not INSPIRE. A single upstream call routed through the deployment
(`/api/search?q=…&live=1`) completes in 0.55–0.65 s end to end. Not the
network to Vercel either: `/api/health` answers in 0.13 s.

The deployed search made **one INSPIRE request every 10–40 seconds**, while
each poll of its status returned in 0.13 s. Its own coverage record carried
the tell:

```
resource_limit: request deadline elapsed during transport
```

on a two-author pair query — an 8 s deadline that expired while the request was
in flight. The engine treats that as a transient upstream failure and backs off
exponentially (5, 10, 20, 40 s), which is exactly the spacing of the later
request timestamps: 128 s → 152 s → 191 s → 225 s.

## Why: the worker only runs while a request is open

### Transport

`GET /api/path?…&search=deep` created a job, started a **daemon thread**
running the engine, and returned immediately. The browser then polled
`GET /api/search-jobs/{id}` every 1.5 s. All of it — the job registry, the
engine session with its SQLite evidence store, page cursors, the request
cache, the request pacer, in-flight coalescing, endpoint preparation — lives in
one module-global `State` per process (`server.py:_state_for_handler`).

### Runtime

`pyproject.toml` names `hepgraph.server:Handler`, a `BaseHTTPRequestHandler`.
Vercel's Python runtime (`vercel_runtime/vc_init.py`) serves that class from a
`ThreadingHTTPServer` inside the function instance and, after each response,
drains any `wait_until` **awaitables** and sends an IPC `end` for the
invocation. Nothing registers a plain thread with the platform. When no
invocation is open the execution environment is frozen, as the underlying
Lambda model has always done; Fluid compute keeps an instance warm and lets
invocations share it, but it does not keep the process running with none in
flight.

So the daemon thread ran only during the ~130 ms each poll was open, every
1.5 s: roughly a 9 % duty cycle, and any upstream call that spanned a freeze
saw its deadline expire while it was suspended.

### The proof

Same fresh one-hop query (Hostert → Pascoli), same deployment, changing only
how often the client polls:

| Poll interval | Wall time | Requests/s |
|---:|---:|---:|
| 1.5 s | **19.0 s** | 0.21 |
| 0.25 s | **2.6 s** | 1.66 |
| (local) | 1.4 s | — |

Seven times faster from poll rate alone. Progress is a function of how often a
request happens to be open, which is the definition of the defect.

Instance switching was **not** the cause: all 145 polls of the cold search
found their job, so they reached the same process. The state was there; the
thread meant to advance it was not running.

## What changed

**The search advances inside requests.** `SearchJobs` no longer starts a
thread. `start()` runs a first bounded slice (3 s) before it answers, so a
direct connection is usually returned by the start request itself. Every poll
runs another bounded slice (5 s) before answering. `continue` runs one
immediately. Exactly one request drives a given job at a time — a per-job lock;
a poll arriving while another is driving just reads the current state. A
transient upstream failure schedules the next attempt rather than sleeping
inside somebody's request.

This also changed a contract inside the engine. `DeepSession` insisted on a
single owner *thread* because its in-memory SQLite connection was thread-bound.
The invariant that actually matters is that calls never overlap; the connection
is now opened `check_same_thread=False` and the driving lock guarantees the
exclusion. The test fakes assert exactly that — no two calls on a session
overlap — instead of a thread identity.

**Endpoint preparation runs inside its POST** for the same reason. Its worker
pool had the identical problem: on the deployment a preparation was usually
still incomplete when Find was pressed. It now costs the preparing request
about two seconds and actually happens.

**A poll that finds its job unknown restarts the search** instead of
dead-ending. Job state is per process, and while every poll of the measured
searches reached the same process, nothing guarantees it. The browser now
starts the same search again on whichever process answered, says so in the
progress line, and limits itself to two restarts.

**The health endpoint reports the build commit, deployment id, region and a
per-process instance id**, and every JSON response carries that id in an
`X-HEP-Instance` header, so instance affinity can be measured rather than
assumed.

## What is still process-local

Everything: the job registry, engine sessions, the response cache, the pacer,
in-flight coalescing, preparation results. With Fluid compute concentrating
traffic on warm instances this held for every measured search, but it is
observed behaviour, not a guarantee. Two consequences are documented rather
than fixed in this phase:

- Two instances each believe they may make ten requests per five seconds.
  Aggregate outbound traffic can exceed the intended service-wide budget when
  the platform scales out; it stays under INSPIRE's published fifteen while a
  single instance serves.
- Request coalescing is per instance. Identical concurrent requests on
  different instances each go upstream.

Whether a shared store is warranted is a measurement question for the preview
deployment, using the instance header now available.

## The "100 works retrieved"

`works_retrieved` is the number of distinct literature records in the search's
evidence store. It read 43 → 60 → 100 → 266 → 283 across the cold run's polls,
passing through 100 at 128 s as a running count. No production path pages at
100; the literature page ceiling is derived from the mode's author bound
(855 records for small-team) and profile lookups use 25.
