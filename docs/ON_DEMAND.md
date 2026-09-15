# Live API and bounded storage

Live INSPIRE is the default. No normal UI action runs the persistent importer, writes an INSPIRE disk cache, or starts a full-database harvest.

## API

| Route | Purpose |
| --- | --- |
| `GET /api/health` | Service and saved-snapshot version |
| `GET /api/dataset?mode=live` | Coverage, source policy and capabilities |
| `GET /api/cache` | Cache, preparation and search-retention counters |
| `GET /api/search?q=...&mode=live` | Bounded author/ORCID/exact-ID lookup |
| `POST /api/prepare?person=ID&mode=live&...filters` | Queue selected-endpoint preparation |
| `GET /api/preparations/ID` | Preparation status |
| `GET /api/path?source=ID&target=ID&mode=live` | Start or reuse a deep connection job |
| `GET /api/search-jobs/ID?mode=live` | Result and useful progress |
| `POST /api/search-jobs/ID/continue?mode=live` | Resume the same retained search state |
| `POST /api/search-jobs/ID/cancel?mode=live` | Stop unnecessary future search work |
| `GET /api/person/ID?mode=live` | Retrieved researcher profile; `summary=1` fetches identity only |
| `GET /api/neighborhood/ID?mode=live` | Bounded retrieved neighborhood |
| `GET /api/centrality?mode=snapshot` | Saved-snapshot centrality with explicit scope |
| `GET /api/ancestry/ID?mode=snapshot` | Directed saved doctoral ancestry/descendants |

Paper filters are `min_authors`, `max_authors`, `min_shared`, `year_start`, `year_end`; `genealogy` controls whether sourced genealogy-only links may establish paths. Small-team uses `min_authors=1&max_authors=10`; large-team uses `min_authors=11&max_authors=all`; all papers uses `min_authors=1&max_authors=all`. Existing custom numeric caps remain supported. Every filter is part of the cache/search identity.

POST controls are bodyless and reject supplied cross-origin requests. They accept only fixed routes and validated numeric IDs. HEAD cannot start an expensive path request. Exact source and target order is preserved in recent-job reuse; reverse queries are not silently reused with backward evidence or progress.

## Temporary storage

| Layer | Bound and lifetime |
| --- | --- |
| Shared metadata | 8 MiB serialized data; 256 entries; 15 minutes |
| Author, literature, summary and shared-paper responses | Separate observable categories sharing the metadata budget; defensive copies |
| Upstream requests | Eight in-flight leaders; identical calls coalesce; one new request per second per server process |
| Upstream response | At most 4 MiB; at most eight seconds per transport call within the caller's deadline |
| Preparation | Two workers, eight queued items, 32 retained statuses; ten-minute status expiry |
| Deep search | Two active jobs; four retained heavy sessions; memory-only evidence and cursors |
| Retained result data | Up to 32 records under a separate 8 MiB serialized-data budget; 20-minute expiry |
| Browser reconnect | A small session-storage job handle, exact pair and filters; no papers or graph cache |

In-flight buffers, Python objects and SQLite evidence use additional memory. The serialized cache limits do not describe total process RAM. Search graphs also enforce work/person/incidence and query-operation ceilings. Large-paper queries request five complete records per page; no author array is sliced.

Successful cache entries survive cancellation for reuse. Errors are not cached as successful results. A follower of a coalesced request retains its own deadline and cannot cancel another caller's shared transport. Rate-limit cooldowns apply to the whole client. An already-running network call can finish after Stop, within its transport timeout; subsequent search work is cancelled.

Search progress is preserved through automatic time/request continuation, browser refresh and reconnect. Reaching a hard memory ceiling or persistent source failure is explicit. When bounded retention releases an older verified session, its compact evidence result can remain available; further continuation requires retained state. Server restart clears temporary state.

The existing saved JSON and fixed test fixtures are small intentional files. Runtime databases, downloaded caches, test outputs and logs are ignored by Git. No recurring harvest or background full-catalogue job is installed.
