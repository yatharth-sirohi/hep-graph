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

## 12. Performance after

## 13. Tests

## 14. Agent review

## 15. Remaining bottlenecks

## 16. Git and deployment
