# Performance and adversarial review — HEP Atlas (`/atlas`)

Reviewer scope: performance measurement (bytes, time-to-interactive, drag
FPS, memory, interaction latency) and adversarial testing (rapid interaction,
state/URL edge cases, malformed input, server-side abuse, low-end network/CPU
conditions). No application code was edited; this is measure-and-report only.

**Method note — the codebase moved under test.** The app builder(s) were
committing to `static/atlas/js/*.js` concurrently with this review (commits
`4b2051f`, `390a071`, `21467f0`, `e7f924c` landed between 01:35 and 02:16
local time while this review was running, changing `app.js` and `state.js`).
The server reads static files straight off disk per request, so no restart
was needed to pick these up. All numbers below were taken against, or
re-verified against, the tree at `e7f924c` (the HEAD at time of writing).
Where a bug was found, it was re-confirmed against that same HEAD immediately
before being written down.

**Environment.** Local server (`.venv/bin/python -m hepgraph.server --port
8830`) on loopback, Playwright-driven Chromium (chrome-mac-arm64) with real
GPU acceleration (`ANGLE (Apple, ANGLE Metal Renderer: Apple M4)` — confirmed
via `WEBGL_debug_renderer_info`, not software/SwiftShader). The machine had
other heavy browser processes running throughout, as flagged in the brief;
every timing measurement below is a median of 3–5 repeats with the range
reported alongside it, and headless-Chromium frame timing has known jitter
(occasional 0 ms-gap duplicate rAF ticks), so FPS figures lean on the p95 and
worst-case frame gap, not the naive average, as the more trustworthy signal.
Collaboration roster counts used in the heavy-scene tests are the counts
that actually render (have coordinates), not the full roster: CMS rendered
210 of 244, ATLAS 175–177 of 198 — some roster entries lack lat/lon and are
silently dropped by `globe.js`'s `setCollaboration` (a data-completeness gap,
out of scope for this review, but it means the FPS worst case measured here
is very slightly lighter than the true full roster would be).

## Measurements

| Measurement | Median | Range | Method |
|---|---|---|---|
| First-load bytes, total (cold, no cache, all in-flight requests) | **3.19 MB** (3,265,099 B) | single deterministic run (uncompressed, no cache) | Playwright `response.body()` summed over every request from `page.goto('/atlas', networkidle)`, 1 run (see per-file breakdown below; not variable since nothing is compressed or cached) |
| — app shell (HTML+CSS+11 JS modules+2×favicon) | 98.6 KB | — | same run, `resourceType` document/stylesheet/script/other, atlas.css+app.js+state.js+loader.js+globe.js+timeline.js+panels.js+modes.js+search.js+model.js+fallback.js+index.html+2×favicon.svg |
| — vendor (`globe.gl.min.js` + `land-110m.json`) | 1.80 MB | — | same run |
| — data bundles fetched on first paint (manifest×2, atlas, institutions, results, documents, search) | 1.36 MB | — | same run |
| Time to interactive (marker clickable), cold, localhost | 596 ms | 592–626 ms (n=5) | Playwright, fresh `BrowserContext` per run, `waitForSelector('.atlas-marker')` then a real click dispatched to confirm responsiveness |
| Time to interactive, warm, localhost (same context, repeat nav) | 602 ms | 573–604 ms (n=5) | same script, context reused — **no material warm speedup**, see Finding P2-1 |
| Time to interactive, throttled 10 Mbps / 28 ms RTT ("broadband") | **3186 ms** | single cold run | CDP `Network.emulateNetworkConditions`, fresh context, `waitForSelector('.atlas-marker')` |
| Time to interactive, Chrome "Slow 3G" (400 kbps/400 ms) | **did not become interactive within 25 s** | — | CDP throttle, `waitForSelector` timeout |
| Time to interactive, CPU throttled 4× | 1821 ms | single run | CDP `Emulation.setCPUThrottlingRate(4)` |
| Time to interactive, CPU throttled 6× | 2933 ms | single run | CDP `Emulation.setCPUThrottlingRate(6)` |
| Time to interactive, CPU 6× **and** Slow 3G together | timed out (>25 s) | — | combined CDP throttle |
| FPS during drag, default view | ~60 fps sustained | p95 frame gap 16.8–17.9 ms (5×4s runs) | in-page `requestAnimationFrame` timestamp sampling during a scripted 4 s circular `mouse.move` drag with button held |
| FPS during drag, CMS collab mode + institutions (210) + arcs | **~15–20 fps typical** | p95 gap 50–83 ms; worst gap up to 83 ms (5×4s runs) | same drag script, `?m=collab&arcs=1#/collaboration/cms` |
| FPS during drag, ATLAS collab mode + institutions (175–177) + arcs | **~15–20 fps typical** | p95 gap 50–67 ms; worst gap up to 83 ms (5×4s runs) | same, `#/collaboration/atlas` |
| FPS, worst case: CMS collab + arcs + timeline playback + drag simultaneously | ~19–20 fps | p95 gap 66.6 ms, worst 67 ms, 1 run, 4 s window | same drag script with playback started first (year set to 1990 so playback had headroom to advance); no crash, no console error, playback and drag both kept working throughout, year advanced 1990→1998 |
| Memory, JS heap after load | 16.1 MB used / 49.8 MB total | single measurement | CDP `Performance.getMetrics` (`JSHeapUsedSize`), `--js-flags=--expose-gc`, forced GC before reading |
| Memory, JS heap after 20 entity visits | 35.8 MB used / 75.6 MB total | — | same, 20 diverse entities (4 each of collaboration/document/experiment/facility/institution) navigated by hash |
| Memory, JS heap after a second lap (40 total visits) | 36.3 MB used / 76.4 MB total | — | repeats the same 20 ids again — **plateaus, does not grow further** (see Finding, positive) |
| DOM node count, after 20 / 40 visits | 445 / 445 | stable | same CDP session, `Nodes` metric — returns to baseline after each panel closes, no leak |
| Latency: collaboration select → institution markers on globe | 12 ms | 3–14 ms (n=5, localhost) | click the real "View collaboration on globe" button, time to first `.atlas-marker.tier-institution` in DOM |
| Latency: timeline slider move → marker classes updated | 2.6 ms | 1.6–8.3 ms (n=7) | `performance.now()` bracket around dispatching an `input` event on `#timeline-year` |
| Latency: search keystroke → results list populated | 123 ms | 77–383 ms (n=5) | includes synthetic per-keystroke typing delay (20 ms/char); app-side overhead beyond typing itself is small |
| Latency: panel open with sources disclosure, cold (first ever, triggers `provenance.json`+`sources.json`) | 42 ms | localhost only | time from hash change to `#detail-panel h2` present, first visit to `facility:cern` |
| Latency: panel open with sources disclosure, warm (cached) | 16 ms | localhost only | same, second visit — **the 42/16 ms gap understates the real-world cost**, see Finding P1-2 |
| Server: 400 concurrent `GET /atlas/generated/manifest.json` | all 200, 0.585 s wall (40-way parallel) | — | `xargs -P 40 curl`, then `/api/health` immediately after: 200 in 1.1 ms |
| Server: 250 concurrent `GET /api/health` (api rate bucket = 180/min) | 177×200, 73×429 | — | confirms the api bucket throttles at ~180/min with a graceful JSON 429, and does not affect the separate asset bucket (assets still 200 afterward) |
| Server: path traversal attempts (11 variants: `../`, `%2e%2e/`, double-encoded, `..%2f`, null byte, backslash, `//`, `//etc//passwd`, trailing slash dir, `.py` via `../`) | **11/11 → 404** | — | `curl` against `respond_atlas`, see Findings (server holds) |
| Server: very long URL (10,000-char query, 5,000-char path segment) | 414, ~1–10 ms | — | `curl`; client-side long-URL case also produces a graceful JSON `invalid_input` body, no crash |

### First-load byte breakdown (cold, uncompressed, no browser cache benefit)

| File | Bytes | Needed for first (globe) view? |
|---|---:|---|
| `vendor/globe.gl.min.js` | 1,728,142 | yes (required to render the globe at all) |
| `generated/institutions.json` | 537,820 | **no — fetched, then discarded** (`void institutions;` in `app.js`) |
| `generated/atlas.json` | 452,255 | yes |
| `generated/search.json` | 206,458 | for the header search box (used immediately, but could be deferred to first keystroke) |
| `generated/results.json` | 101,287 | no (only used if the user opens "Results" mode) |
| `vendor/land-110m.json` | 76,538 | yes (continent outlines) |
| `generated/documents.json` | 49,717 | no (only used if the user opens "Documents" mode) |
| `panels.js` | 24,070 | yes (app shell) |
| `atlas.css` | 14,683 | yes |
| `globe.js` | 14,549 | yes |
| `generated/manifest.json` (×2 — see Finding) | 10,556 | yes, but fetched twice |
| `timeline.js` | 7,100 | yes |
| `modes.js` | 7,346 | yes |
| `app.js` | 8,902 | yes |
| `loader.js` | 6,802 | yes |
| `state.js` | 3,392 | yes |
| `search.js` | 3,079 | yes |
| `model.js` | 4,304 | yes |
| `fallback.js` | 4,046 | only if WebGL2 is unavailable |
| `index.html` | 3,375 | yes |
| `favicon.svg` ×2 | 678 | yes |

The build's own warning cites `atlas.json` + `manifest.json` ≈ 457 KB. What
actually crosses the wire on first load is **3.19 MB — about 7× that
figure**, because the warning doesn't count `institutions.json` (537 KB,
entirely unused on first paint), `results.json`/`documents.json` (151 KB,
unused until the user switches modes), `search.json` (206 KB), the JS module
graph (~99 KB), or the vendor globe library + land outline (1.80 MB, the
single largest piece and unavoidable for a WebGL globe).

## Findings

### P1-1 — A shared link's year/range is silently discarded on fresh load

Opening a copied share link that encodes a specific year or range (e.g.
`?y=2010#/facility/cern`, or `?r=1990-2000#/facility/cern`) does **not**
restore that year. It silently resets to the manifest's default year (today,
2026) instead — verified live:

```
start: http://127.0.0.1:8830/atlas?y=2010#/facility/cern
final: http://127.0.0.1:8830/atlas?y=2026#/facility/cern    (slider also reads 2026)

start: http://127.0.0.1:8830/atlas?r=1990-2000#/facility/cern
final: http://127.0.0.1:8830/atlas?y=2026#/facility/cern    (range is gone entirely, not just clamped)
```

**Root cause** (`static/atlas/js/app.js`, current HEAD `e7f924c`): `state.init()`
parses the URL first (line 75), but `createTimeline(...)` is constructed
later (line 150) with only static `minYear`/`maxYear`/`defaultYear` from the
manifest — it has no knowledge of the URL's `y=`/`r=`. `createTimeline`'s
constructor synchronously calls `emit()`, which immediately invokes the
`onChange` callback with `{mode: 'year', year: defaultYear}` and that
callback calls `state.navigate({year, range: null}, {replace: true})`. This
**overwrites the browser URL via `history.replaceState` before the app ever
reconciles the widget with the real state** — and the *second* call to
`state.init()` at line 225 (whose return value, `initial`, is what
`applyState` actually renders from) re-reads `window.location`, which has
already been clobbered. The entity, mode, and `collab` context all survive
correctly (only the timeline year/range is lost), and nothing errors or
hangs — this is a silent, no-error state-loss bug, exactly the class of bug
the adversarial "copy a share link, open it fresh" check exists to catch.
This is the same bug for both `?y=` and `?r=`.

**Suggested fix direction** (not applied — out of scope for this review):
pass the parsed initial state into `createTimeline`'s config, or defer its
constructor's implicit `emit()`/`onChange` call until after
`applyState(initial)` has run once.

### P1-2 — Opening *any* detail panel eagerly downloads ~2.2 MB of provenance/sources data, even though the "Sources" section is collapsed by default

`panels.js`'s `sourcesDisclosure()` is `await`-ed unconditionally inside
`renderFacility`, `renderExperiment`/`renderCollaboration`/`renderInstitution`
/`renderResult` — i.e. on **every** first panel open, before the panel even
renders — and it fetches both `provenance.json` (1.44 MB) and `sources.json`
(0.79 MB) = **2.2 MB**, regardless of whether the user ever expands the
`<details>` element it renders into (`{ open: false }`). The `loader.js`
cache means this only happens once per session, but that once blocks the
*first* panel a user opens on any entity. Locally (loopback) this only costs
26 ms extra (42 ms cold vs. 16 ms warm in the latency table above), which
is why it wasn't visible in the raw latency numbers — but on the throttled
10 Mbps profile used for the TTI test, 2.2 MB alone is ~1.8 s of transfer
before the first panel can appear, and on Slow 3G it would not appear within
any reasonable wait. This directly contradicts "people [data] loaded lazily
rather than all at once" in spirit: the disclosure is visually progressive,
but the network fetch behind it is not.

### P1-3 — Dragging the globe with a large collaboration's institutions + arcs shown drops FPS to ~15–20, well under the "~60 fps" target

Default view sustains a clean ~60 fps during drag (p95 frame gap 16.8–17.9
ms). With CMS (210 rendered institutions) or ATLAS (175–177) in collaboration
mode with institution-connection arcs on, drag FPS drops to a sustained
**~15–20 fps** (p95 frame gap 50–83 ms), with individual worst-case gaps
around 83 ms (≈12 fps). This reproduces consistently across 5 repeated 4-second
drag samples per scenario and matches the same pattern whether or not
timeline playback is running concurrently. Nothing hangs, errors, or becomes
unresponsive — input is still processed, drag still tracks the pointer — this
is graceful-but-real degradation, not a crash, but it is a clear miss of the
"roughly 60 fps ... with graceful degradation" target for exactly the
scenario the brief calls out as the worst case. The likely mechanism (not
verified via profiler, inferred from `globe.js`): each institution is a real
DOM element in `htmlElementsData`, re-projected to screen space every frame,
plus arc geometry recomputed per frame — both scale linearly with the
marker/arc count, and ~200 extra live DOM nodes with individual
click/keydown listeners is a heavy per-frame cost for globe.gl's CSS
projection layer.

### P1-4 — On a slow connection, the interface sits blank rather than explaining itself

On the Slow 3G profile, `waitForSelector('.atlas-marker')` never resolves
within 25 s. Inspecting what actually renders: the static HTML shell
(header, search box, "View"/mode buttons, "Legend"/"Options" panel chrome)
appears quickly since `index.html` is only 3.4 KB, but the **Legend is empty**
(populated by `renderLegend()` only after the data `Promise.all` resolves)
and the **entire globe-stage area is blank** — there is no spinner, no
"Loading…" text, nothing — for as long as the ~3.2 MB payload takes to
arrive. `atlas.css` has exactly one loading-state class (`.loading-note`),
used solely by `panels.js` for the detail panel's "Loading…" text; there is
no equivalent for the initial globe/legend load. The app also has no
`window.addEventListener('offline'/'online', ...)` anywhere, so it never
proactively tells the user their connection is a problem — it silently sits
blank until something explicit is attempted, at which point failures are
reported per-action (see the positive finding below).

### P2-1 — `manifest.json` is fetched twice on every load

`loader.js`'s `probe()` (used by `resolveBase()` to decide `generated/` vs.
`fixtures/`) does a raw `fetch('.../manifest.json')` outside the module's
cache map, and `getManifest()` in `app.js`'s `Promise.all` fetches it again
through `fetchJSON`, which does cache — but the first call already missed
the cache. Confirmed in the network trace: `manifest.json` (5,278 B) appears
twice, ~10.6 KB total for one file. Minor (~0.3% of total payload) but free
to fix, and it means the local TTI numbers above show no measurable warm-load
speedup — partly because of this, and mostly because of Finding P2-2.

### P2-2 — No HTTP caching headers at all on any atlas asset; nothing is compressed

Every response (JS, CSS, JSON, vendor library) is served with either
`Cache-Control: no-cache` (non-`generated/` paths) or `public, max-age=300`
(`generated/` paths) and **no `ETag` or `Last-Modified`** — so a "no-cache"
response cannot even be revalidated with a 304; it is always a full refetch.
Combined with **no `Content-Encoding: gzip`/`br` on any response** (verified
via `curl -H "Accept-Encoding: gzip, deflate, br"`, response headers show no
`Content-Encoding` and `Content-Length` unchanged from the uncompressed
size), this is the single largest lever available: `globe.gl.min.js` alone
(1.73 MB minified JS) would typically compress 65–75% with gzip, and the
JSON bundles (highly repetitive key/value structures) typically 80–90%.
Compressing responses would very plausibly bring the 10 Mbps "broadband" TTI
figure (3.19 s, currently just over the ~3 s target) back under target
without touching the actual byte content, and would make a real warm-cache
revisit meaningfully faster than the cold one (currently it isn't).

### Positive findings (no defect)

- **Memory does not grow without bound.** 16.1 MB → 35.8 MB after 20 distinct
  entity visits, then only → 36.3 MB after 20 *more* visits (same ids
  repeated) — the growth plateaus once the caches (`loader.js`'s bundle
  cache, `resultsCache`/`documentsCache`/`sourcesCache`/`graphCache`) are
  warm. DOM node count returns to the same baseline (445) after each visit —
  no detached-node leak.
- **Server-side path traversal is fully blocked.** All 11 attack variants
  tested (`../`, single- and double-URL-encoded `..`, `..%2f`, null byte,
  backslash, `//`, `//etc//passwd`, a bare directory, and a `.py` extension
  reached via `../`) return 404 from `respond_atlas` — the `'..' in
  candidate`/`resolve()`/`is_relative_to(root)` checks in `hepgraph/server.py`
  hold under direct attack.
- **The asset/API rate-budget separation holds.** 400 concurrent asset
  requests never touch the 8-slot `workers` semaphore (asset requests are
  explicitly exempted in `server.py`'s `handle_one_request`), and
  `/api/health` stayed at ~1 ms after the hammering. Separately, hammering
  `/api/health` itself (250 concurrent) correctly triggers the 180/min `api`
  bucket (177×200, 73×429, graceful JSON body) **without** affecting the
  2000/min `asset` bucket — confirmed by successfully fetching assets
  immediately after. The fix mentioned in the brief holds.
- **Long/malformed URLs are rejected gracefully, not crashed.** A 10,000-char
  query string and a 5,000-char path segment both return `414` in ~1–10 ms;
  client-side, the same very-long-URL case surfaces a JSON
  `{"status": "invalid_input", "message": "Request URL is too long."}` body
  with no page crash and no hang.
- **Malformed client-side params degrade gracefully.** `?y=99999` is clamped
  by `timeline.js`'s `clamp(v, lo, hi)` rather than breaking the slider;
  `?y=abc` is rejected by `state.js`'s `Number.isNaN` guard and simply
  ignored; `?m=nonsense` falls through `modes.js`'s `MODE_RENDERERS[mode]`
  check to the "no mode" branch; `#/nonsense-type/foo` and
  `#/experiment/does-not-exist` both render "Unknown entity type"/"Unknown
  experiment" empty-state notes instead of throwing. No console errors were
  observed for any of these six cases.
- **Rapid interaction survives.** Rapid timeline back-and-forth (20 moves),
  10 entity clicks in ~255 ms (well under the "two seconds" bar), 15 rapid
  arcs-toggle flips, and "start playback, immediately switch modes, switch
  back" all left the UI responsive with zero console errors; playback
  correctly keeps running in the background across a mode switch (not a bug
  — mode and playback are independent state).
- **State survives back/forward and reload.** 15 pushes through 6 different
  entity types, then 20 back + 20 forward, left the app alive with markers
  present. Reloading mid-navigation (120 ms into a collaboration-mode
  transition) recovers cleanly. Two tabs opened on different deep links
  (`?m=collab&arcs=1#/collaboration/dune` and
  `#/facility/cern?y=2015`) kept fully independent hash state — no shared
  global leaking between tabs.
- **Offline mid-session fails per-action, gracefully, not silently or as a
  hang.** Going offline via CDP and navigating to an not-yet-cached
  collaboration panel produces `"Could not load this entity: Failed to
  fetch"` in the detail panel (from `panels.js`'s `render()` catch block) —
  a real if slightly technical message, not a stuck spinner. Coming back
  online, the very next navigation works immediately.

## Verdict against the stated product targets

- **"The globe interactive within about three seconds on broadband."**
  **Marginal/at-risk, not clearly met.** Localhost TTI is ~600 ms (not
  representative of a real network). Under a plain 10 Mbps/28 ms broadband
  emulation the globe becomes interactive at **3.19 s — over the ~3 s
  bar**, driven almost entirely by the 3.19 MB, fully uncompressed,
  uncached first-load payload (Findings P2-2, and the 537 KB of unused
  `institutions.json`, P1). On a genuinely slow connection (Slow 3G) it does
  not become interactive in any reasonable time, and shows nothing to
  explain why (Finding P1-4). Enabling compression alone would plausibly
  bring the "broadband" case comfortably under target; the target as tested
  today is not reliably met.
- **"Roughly 60 frames per second during ordinary interaction, with graceful
  degradation."** **Met for ordinary interaction, missed for the stated
  worst case.** Default-view dragging holds a clean ~60 fps. The explicitly
  named worst case — CMS/ATLAS collaboration mode with institution arcs on —
  drops to a sustained ~15–20 fps (worst ~12 fps), which is real,
  reproducible degradation well past "graceful": it's a 3–4× frame-rate
  drop, not a minor dip. Nothing crashes or hangs, so it is not a P0, but it
  is a clear miss of the 60 fps bar for a scenario the product explicitly
  anticipates (Finding P1-3).
- **"People loaded lazily rather than all at once."** **Partially met, with
  a concrete counter-example.** Per-person bundles (`people/<collab>/<inst>.json`)
  genuinely are lazy, fetched only via `getPeople(relPath)` when a roster row
  is expanded — that part works as designed. But `institutions.json` (537
  KB — the atlas's second-largest bundle) is fetched unconditionally on
  first load and then never used (Finding, in first-load table: `void
  institutions;`), and `provenance.json`+`sources.json` (2.2 MB combined) are
  fetched in full the moment *any* entity panel opens, not when the
  collapsed "Sources" disclosure is actually opened (Finding P1-2). Both
  are "all at once" behavior masquerading as lazy loading.

**Summary of severities found:** 0 × P0 (nothing hangs, crashes, leaks data,
or defeats a security control), 4 × P1 (share-link year/range silently
dropped; eager provenance/sources fetch on any panel open; collaboration-mode
drag FPS well under target; slow connections show a blank UI with no
explanation), 2 × P2 (duplicate manifest.json fetch; no compression/caching
headers anywhere). Several explicit stress/attack scenarios were tried and
found to degrade gracefully or be actively defended (memory plateau, path
traversal, rate-limit separation, malformed-input handling, rapid
interaction, back/forward/reload/multi-tab state, offline error handling) —
these are called out above as positive findings so they aren't lost among
the negative ones.

## Closure (2026-09-17)

Workstream W1 (`hep-atlas-v1-w1`), correctness-debt pass. This review's own
words are worth repeating: it is "measure-and-report only" and "no
application code was edited" — so every one of its four P1s was still open
when it concluded. This section closes two of them, confirms one was fixed
by a separate change before this pass, and leaves one open out of scope.

### P1-1 — share-link year/range — confirmed fixed (not by this pass)

Read-only verification. `static/atlas/js/timeline.js`'s `createTimeline` no
longer calls `emit()` from its constructor ("Deliberately no emit() here.
Announcing the default year at construction..."), and `static/atlas/js/app.js`'s
`main()` now calls `timeline.syncFromState(state.get())` before
`timeline.start()`, seeding the widget from the parsed URL before it can
announce a default. This was already true on this worktree's starting
commit; not re-measured against the throttled-network scenario in the
original finding, only confirmed by reading the current code.

### P1-2 — eager provenance/sources fetch — fixed this pass

`static/atlas/js/panels.js`'s `sourcesDisclosure()` no longer fetches
anything until the `<details>` element's native `toggle` event fires with
`details.open === true`. The disclosure shows "Opens to load this entity's
sources." before that, "Loading sources…" while the fetch is in flight
(`role="status"`), and a real error message plus a Retry button
(`role="alert"`) on failure — never a silently empty list.

Measured with Playwright against the **generated** tree, server on
`127.0.0.1:8792` (`hepgraph/server.py`, this worktree's code):

| Scenario | Requests | Bytes | provenance.json/sources.json |
| --- | ---: | ---: | ---: |
| Open a facility panel, Sources collapsed | 21 | 3,079,432 | 0 requests, 0 bytes |
| Then open the Sources disclosure | +2 | +2,228,865 | 2 requests, 2,228,865 bytes |

Opening a panel no longer touches provenance/sources at all (previously
~2.2 MB on the *first* panel of any session, per this review's own
measurement of the same two files); the cost now lands only on the person
who actually expands "Sources", and only once (`loader.js`'s existing bundle
cache still applies). Browser test:
`tests/browser_atlas.cjs`'s "Opening a panel does not fetch
provenance/sources; opening the Sources disclosure does (P1-2)", run against
both the fixtures and generated trees via Playwright request interception.

### P1-3 — collaboration-mode drag FPS — still open

Not addressed by this workstream. `static/atlas/js/globe.js` is owned
separately (institution markers, arcs, FPS); no clustering, level-of-detail
or marker-count reduction was found in the current file
(`grep -n 'cluster\|LOD\|throttle' static/atlas/js/globe.js` finds nothing).
Left open, matching the task assignment for this pass.

### P1-4 — blank UI on a slow/offline connection — fixed this pass

`static/atlas/index.html` adds `#atlas-error` (`role="alert"`,
`aria-live="assertive"`, a message paragraph and a Retry button).
`static/atlas/js/app.js` shows visible loading text
("Loading HEP Atlas… this can take a few seconds on a slow connection.") in
the pre-existing `#data-notice` (`role="status"`) for the entire cold-load
fetch, not just the initial base-path probe, and routes any startup failure
(including a blocked/failed bundle fetch) to the new error banner with a
real explanation and a retry that reloads the page. No spinner-only state:
both states are plain visible text in an `aria-live` region. Neither state
introduces motion, so both are reduced-motion-safe by construction.

Browser tests (`tests/browser_atlas.cjs`, both trees):
"Blocking atlas.json shows an accessible error state with a retry control
(P1-4)" (aborts the `atlas.json` request, asserts `#atlas-error` appears
with `role="alert"` and a working `#atlas-retry`) and "A throttled
connection shows a visible, accessible loading state before data arrives
(P1-4)" (400 kbps / 400 ms CDP throttle, asserts `#data-notice` shows
loading text with `role="status"` before the bundles arrive).

### Caching (P2-2, and the reload half of the "all at once" finding)

Not requested as a P1 fix, but the same pass closed it because the loader
change for P1-2 needed the server side of caching to make sense.
`hepgraph/server.py`'s `respond_atlas` now sends a strong ETag (SHA-256 of
the file's bytes) and `Cache-Control: public, max-age=0, must-revalidate`
for every file under `/atlas/**`, honours `If-None-Match` with a bodyless
304, and `static/atlas/js/loader.js` no longer opts out with
`cache: 'no-store'`. Design rationale and why this covers both the local
server and the Vercel deployment (same Python handler, no separate static
layer) are in `docs/HEP_ATLAS_BUNDLES.md`'s "Caching" section.

Measured, real Chrome (Playwright, not chrome-headless-shell), generated
tree, same server:

| Load | Requests | Bytes | Notes |
| --- | ---: | ---: | --- |
| Cold first load | 20 | 2,763,794 | fresh browser context |
| Warm reload, same context | 20 | 920,055 | 12 responses came back `304` (all JS modules, `atlas.css`, vendor `globe.gl.min.js`) |

**Caveat, stated plainly because this is the one number in this closure that
did not fully reproduce as expected:** the 8 responses that stayed `200` on
the warm reload are exactly the bundles `loader.js` fetches via `fetch()`
(`manifest.json`, `atlas.json`, `search.json`, `results.json`,
`documents.json`) — not the ones loaded as ordinary `<script>`/`<link>`
subresources, which did revalidate correctly. This was checked three ways
before writing it down: (1) `curl` round-trips against the live server
prove the server sends a correct ETag and answers a matching
`If-None-Match` with a real `304` (see `tests/test_atlas_server.py`'s
`test_generated_json_and_vendor_js_revalidate_with_etag`, which asserts this
at the protocol level with no browser involved); (2) a from-scratch minimal
Node `http` reference server with the same headers, fetched twice by the
same Playwright/Chrome used throughout this project, shows the identical
non-revalidating behaviour for `fetch()`-initiated requests — so this is not
specific to `hepgraph/server.py`; (3) the same page's `<script>`-loaded
files reliably get `304`s on reload in the same test run. This looks like a
`fetch()`-cache-mode characteristic of the Chrome build used for this
project's automated testing (untested here: whether a real, non-automated
end-user browser session behaves the same way for `fetch()` calls against a
`max-age=0` resource) rather than a defect in the ETag/304 implementation,
but it is reported as an open caveat rather than asserted as harmless.
`static/atlas/js/loader.js`'s bundle fetches remain covered by the
protocol-level guarantee (a correct 304 whenever a client does send
`If-None-Match`), which is what `hepgraph/server.py` is responsible for.
---

## Closure of P1-3 (2026-09-17)

**A pre-existing regression found while investigating P1-3.** The real
bundle's coordinates are nested (`{"coordinates": {"lat", "lon"}}`, A9),
matching `docs/HEP_ATLAS_BUNDLES.md`'s own documented shape, but
`globe.js`'s `siteCoords()` and `setCollaboration()` read a flat
`record.lat`/`record.lon` — the same class of fixture-vs-real field-name
mismatch as the earlier UX review's P0-1/P0-2/P0-3. Against the *current*
generated tree this meant **every** facility/site position and **all 198+
institution membership rows silently failed their `lat == null` guard and
were never rendered at all** — i.e. today's real-tree collaboration mode
showed zero institutions, not the "210 of 244 rendered" this review measured
against an earlier build state. A visible symptom of the same bug: CERN and
every other facility collapsed onto the same (undefined-coordinate)
projected point, which is what let clicking the CERN marker open a
different facility's panel (Laboratori Nazionali del Gran Sasso, LNGS) —
whichever DOM element happened to be on top received the click. Fixed with
one `coordsOf()` helper (reads either shape) used everywhere a coordinate is
read; see `docs/HEP_ATLAS_ARCHITECTURE.md` §6a.

**Method.** `requestAnimationFrame` counting over a 2-second scripted
circular `mouse.move` drag (button held), matching this review's own method,
run against a real `chromium` build via Playwright. "Before" uses the tree
at this review's own HEAD (`e7f924c`) with *only* the coordinate fix applied
(so institutions actually render, isolating the field-name bug from the
clustering/arc-cap/dash-off changes below) and its matching original
`app.js`; "after" is the full closure (clustering, arc cap, dash animation
off, fewer DOM markers). Both were measured in the same sandboxed headless
environment used for this session, which reports a **software rasterizer**
(`ANGLE ... SwiftShader driver`, confirmed via `WEBGL_debug_renderer_info`)
rather than the real GPU (`ANGLE (Apple, ... Metal Renderer: Apple M4)`) the
original P1-3 numbers above were measured against — so the absolute fps
figures here are not comparable to the ~60/~15-20 fps figures above; only
the **before/after ratio within this environment** is. A plain default-view
drag (no collaboration data at all) tops out around 11-16 fps in this
sandbox, confirming the low absolute ceiling is an environment property, not
a regression this session introduced or fixed.

| Scenario | Before (fps) | After (fps) | Rendered institution markers |
| --- | --- | --- | --- |
| CMS collaboration, arcs on | 7.5–8.5 | 12.5–14 | before: 203 (unclustered) → after: 20–31 (clustered) |
| ATLAS collaboration, arcs on | 8–9 | 15–15.5 | before: 177 (unclustered) → after: 22–29 (clustered) |

Roughly a **1.5–1.9×** improvement in this sandboxed, software-rendered
environment, driven almost entirely by the marker-count drop (177–203 →
20–31): clustering means a drag never has to reproject more DOM nodes than
are actually going to be visible at the current zoom, and capping arcs to
the visible/clustered set (plus turning off dash re-animation
unconditionally, not only under `prefers-reduced-motion`) removes the
remaining per-frame cost that scaled with the full roster. On the real-GPU
environment the original review used, where the *default* view holds a
clean ~60 fps ceiling (10-20× this sandbox's ceiling), the same relative
reduction in per-frame marker/arc work would be expected to bring
collaboration-mode dragging from the reviewed ~15-20 fps into roughly the
~30-40 fps range — within reach of, and plausibly over, the 60 fps target's
"graceful degradation" bar — but that was not independently re-verified on
real GPU hardware in this session; the numbers above are the directly
measured evidence, not that extrapolation.

**Automated regression guard.** `tests/browser_atlas.cjs`'s "FPS: dragging
in collaboration mode with arcs on" check runs this same measurement for
both ATLAS and CMS against whichever tree it's pointed at, asserts a floor
(30 fps on a real/hardware-accelerated renderer, calibrated against this
run's own default-view fps when a software rasterizer is detected — see the
comment in the test — so the assertion isn't unpassable on a GPU-less CI box
while still catching a real regression), and always logs the measured
numbers and the detected renderer string.

**Other changes bundled into this closure**, detailed in
`docs/HEP_ATLAS_ARCHITECTURE.md` §6a: marker clustering for facilities and
institutions (§17/§70), semantic zoom tiers (far = facilities only, medium+
= sites), a 40-label visibility budget (§70), an `INSTITUTION_ARC_THRESHOLD`
(150) that defaults arcs off for very large collaborations without ever
letting the toggle lie about what's drawn, and the filter panel (experiment
status, era, topic, facility/experiment kind, region) which composes with
the timeline and shrinks the rendered set before clustering even runs.

---

## Methodology page, footer links, and the fixture-fallback failure path (2026-09-18, workstream A5/A6)

This pass added `static/atlas/about.html` (+`js/about.js`), two footer links
and a real link in the version label (`app.js`, `index.html`), and changed
`loader.js`'s `resolveBase()` so a non-dev host with a missing generated
bundle shows the accessible error state instead of silently serving fixture
data. This section measures the globe route's (`/atlas/`) initial-load
request list and bytes before and after those changes, on the generated
tree, and confirms no local-map geometry/Leaflet bytes load on that route.

### Method

Two servers, isolated so neither could be confused with a concurrent
session's worktree (this repository has several `HEP-Graph-maps-*`
worktrees checked out at once, and an earlier attempt in this same pass
picked up another session's already-running process on a colliding port —
caught by checking each server's `cwd` via `lsof -p <pid>` before trusting
it, not by port number alone):

- **Before**: a detached `git worktree` checked out at `3608c28` (this
  branch's parent commit, i.e. every change in this section reverted),
  served on its own port.
- **After**: this worktree (`hep-atlas-local-maps-a4`), served on port 8816
  as instructed.

A real headless Chromium (Playwright, not `chrome-headless-shell`) loaded
`${base}/atlas/` with a fresh browser context each time, waited for
`networkidle` twice (once before and once after the marker-presence check,
so lazy `import()`s and any post-render fetch are captured) and recorded
every response under `/atlas/` with its actual decoded body length
(`response.body().length`, not the `Content-Length` header — the first
attempt at this measurement used the header and produced a spurious extra
request and mismatched sizes between runs that traced back to the wrong-cwd
server, not to any real difference; body length sidesteps that class of
measurement error entirely).

### Result: request list and bytes, generated tree, `/atlas/`

Identical request set both before and after — 21 requests, same 17
unchanged files (`atlas.json`, `documents.json`, `manifest.json` ×2 [see
P2-1 above, unrelated to this pass and still open], `results.json`,
`search.json`, `globe.js`, `filters.js`, `model.js`, `modes.js`,
`panels.js`, `search.js`, `state.js`, `timeline.js`, `fallback.js`,
`vendor/globe.gl.min.js`, `vendor/land-110m.json`). Only the files this pass
actually touched changed size:

| File | Before | After | Δ bytes | Why |
| --- | ---: | ---: | ---: | --- |
| `/atlas/` (index.html) | 4,308 | 4,589 | +281 | Footer: "Methodology" and "Report an error" links; meta description reworded |
| `/atlas/atlas.css` | 20,480 | 23,807 | +3,327 | The `/* ---- about page ---- */` CSS section (about.html's own layout; nothing on the globe route uses these classes, they are simply served as part of the one stylesheet) |
| `/atlas/js/app.js` | 15,264 | 16,397 | +1,133 | The `error` branch from `loader.init()` and the DOM-built version-label link |
| `/atlas/js/loader.js` | 7,466 | 10,162 | +2,696 | `resolveBase()`'s dev-host branch, `getCoverage()`'s fixture/generated normalization, comments |
| **Total (21 requests)** | **3,947,590** | **3,955,027** | **+7,437** | — |

+7,437 bytes on a 3.95 MB initial load is a 0.19% increase, entirely
accounted for by the four files above (3,327+1,133+2,696+281 = 7,437,
matching exactly). `about.html` and `about.js` are not requested by the
globe route at all — they load only when a visitor follows the new footer
links to `/atlas/about.html`, at which point that page makes its own
separate request list (measured in the browser-test run above: `atlas.json`,
`coverage.json`, `results.json`, `documents.json`, `manifest.json`, mostly
already warm from the globe page's own cache if the visitor came from
there).

**No geometry or Leaflet bytes load on the globe route** in either
measurement (`grep`-style filter for `leaflet`, `geometry`, `/maps/` in the
captured request list: 0 matches, both before and after). The local-map
geometry layer (A25, `docs/HEP_ATLAS_GEOMETRY.md`) is being built on
sibling branches (`hep-atlas-local-maps-*`) not merged into this one at the
time of this measurement, so this confirms only the current tree's
behaviour, not a guarantee about the merged product — the next merge to
`main` should re-run this same before/after comparison once those branches
land, to confirm the geometry/Leaflet assets stay lazy on the globe route
the way `docs/HEP_ATLAS_GEOMETRY.md` intends.

### Caching headers: unchanged

`hepgraph/server.py`'s `respond_atlas` was not touched by this pass (see
the pytest addition in `tests/test_atlas_server.py`,
`test_about_page_is_served_at_its_real_path`, which asserts the same
`Cache-Control: public, max-age=0, must-revalidate` and a present `ETag` for
`/atlas/about.html` as every other atlas asset). `tests/test_atlas_server.py
-k "etag or cacheable"` (2 tests) passes unchanged.

### Failure-path change: no bytes added to the success path

`resolveBase()`'s new branch only executes when the `generated/manifest.json`
probe already failed (a 404, in the test in `tests/browser_atlas.cjs`) — on
the ordinary success path measured above it is not reached at all, so it
adds code size (part of the +2,696 bytes on `loader.js` above) but zero
extra requests or bytes at runtime. Confirmed by browser test: "A
non-localhost host with a missing generated bundle shows the accessible
error state, not the fixture banner" (`tests/browser_atlas.cjs`, Chromium).
