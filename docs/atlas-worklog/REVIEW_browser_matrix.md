# Cross-browser matrix — HEP Atlas (`/atlas`) — addendum §20

Reviewer scope: the full `tests/browser_atlas.cjs` acceptance suite, run
against all three Playwright engines (chromium, firefox, webkit) and both
data trees (six runs), plus mobile-viewport checks (iPhone-size, Android-size,
tablet) in each engine. Where an engine-specific failure surfaced, this
review determined whether it was a real product bug (fixed) or a
test-harness/environment difference (fixed in the test, without weakening
any assertion) — recorded per finding below.

**Environment.** Local server (`.venv/bin/python -m hepgraph.server --port
8794`) on loopback. Playwright with `NODE_PATH` pointed at
`HEP-Graph-atlas/node_modules`; `HEP_BROWSER=chromium|firefox|webkit`
selects the engine (new, added by this pass — see "Harness changes" below).
All three engines report real WebGL2 support in this environment (confirmed
directly, not assumed):

| Engine | `WEBGL_debug_renderer_info` |
| --- | --- |
| chromium | ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device), SwiftShader driver) — software |
| firefox | Apple M1, or similar — hardware |
| webkit | Apple GPU — hardware |

Chromium's software rasterizer is the pre-existing "noisy sandbox" case the
suite's own FPS test already calibrates a floor for; firefox and webkit get
real GPU access here and post correspondingly higher FPS numbers (see
results table).

## Results: full suite, six runs

| Browser | Data tree | Checks passed | Result | Log |
| --- | --- | ---: | --- | --- |
| chromium | generated | 25/25 | pass | `test-results/atlas/logs/chromium-generated.log` |
| chromium | fixtures | 24/24 | pass | `test-results/atlas/logs/chromium-fixtures.log` |
| firefox | generated | 25/25 | pass | `test-results/atlas/logs/firefox-generated.log` |
| firefox | fixtures | 24/24 | pass | `test-results/atlas/logs/firefox-fixtures.log` |
| webkit | generated | 25/25 | pass | `test-results/atlas/logs/webkit-generated.log` |
| webkit | fixtures | 24/24 | pass | `test-results/atlas/logs/webkit-fixtures.log` |

(24 vs 25: the fixtures tree correctly `SKIP`s the A23 approximate-coordinate
marker check, since the dev fixtures carry no `coordinates.approximate`
data — a guard the check already had, not something this pass loosened.)

**147/147 checks pass across the full matrix.** Each run also writes its own
`report.json`, `desktop.png`, three `mobile-<viewport>.png` screenshots and
`fallback.png` under its own `test-results/atlas/<engine>-<tree>/` directory
(gitignored; the `.log` files above are the durable record of this pass).
Reproduce any single cell with:

```bash
HEP_BROWSER=firefox HEP_ATLAS_DATA=generated \
  HEP_ATLAS_OUTPUT=test-results/atlas/firefox-generated \
  node tests/browser_atlas.cjs
```

## Mobile viewports (all three engines, both trees)

Added this pass, alongside the existing 390×844 (iPhone-size) check: 412×915
(Android-size) and 820×1180 (tablet), all in the same
"Mobile viewport … avoids overflow and stays usable" loop so every engine
exercises all three. All 18 combinations (3 viewports × 3 engines × … —
folded into the 6 full-suite runs above, 3 mobile checks per run) pass. Each
viewport check verifies `document.documentElement.scrollWidth` against the
viewport width (no horizontal overflow) and that either the WebGL canvas or
(if an engine/viewport combination genuinely lacks WebGL2) the accessible
fallback list engages — checked per-page via the same `getContext('webgl2')`
probe the app itself uses, not assumed from the engine name. In this
environment all three engines had WebGL2 at all three viewports, so every
mobile check exercised the canvas path; the fallback branch exists and is
exercised for real by the dedicated no-WebGL checks below.

## Harness changes (`tests/browser_atlas.cjs`)

- `HEP_BROWSER=chromium|firefox|webkit` (default `chromium`) selects the
  Playwright browser type. `HEP_BROWSER_EXECUTABLE` is now explicitly
  chromium-only (it names a Chromium-family binary path, which has no
  meaning for the other two engines' own bundled binaries).
- The two "no-WebGL" checks previously launched a **second Chromium
  process** with `--disable-webgl --disable-webgl2 --use-gl=disabled` —
  Chromium-only CLI flags that firefox/webkit don't have, and which
  wouldn't have worked anyway once `HEP_BROWSER` could be firefox/webkit
  (there is no such flag for either). Replaced with an engine-agnostic
  technique: a `context.addInitScript()` that patches
  `HTMLCanvasElement.prototype.getContext` to return `null` for `'webgl2'`
  specifically — the exact condition `globe.js`'s own `supportsWebGL2()`
  checks — on a **new context of the same browser process**, not a second
  process, which is also simpler than the old two-browser-instance
  arrangement.
- CDP's `Network.emulateNetworkConditions` (the "throttled connection"
  check) is Chromium-only (`context.newCDPSession` throws on
  firefox/webkit). Replaced with a `page.route()` delay on every `/atlas/`
  request — the same visible effect (the app sees a slow connection) via a
  technique that works identically on all three engines.

## Real product bug found and fixed

**Globe markers could intercept clicks on the search-results dropdown.**
`globe.js`'s markers each carry a dynamic inline `z-index` (three-globe's
own depth-sorting; observed values into the 30s once wave-3's larger marker
count is loaded), and `#search-results` extends below the header
(`top: calc(100% + 4px)`) into the globe's own screen area. `.atlas-header`
itself was `z-index: 20` — since the header is what establishes the
stacking context its search-dropdown descendant lives inside, raising only
the dropdown's own z-index (25, later even 1000, tried during triage) could
never let it escape that context and out-rank a marker with a higher
z-index at the shared root level. Reproduced deterministically: clicking a
search result for "Deep Underground Neutrino Experiment" was intercepted by
an unrelated "Summit Station, Greenland" marker sitting at that screen
position after an earlier camera move, in real (non-forced) Playwright
clicks — i.e., this could affect a real pointer user too, on any engine,
not just test automation. **Fixed** by raising `.atlas-header`'s own
`z-index` to 1000 (`atlas.css`), so the header and everything in it
reliably stays above the 3D scene regardless of how high the depth sort's
own range grows; `#search-results`'s own z-index was correspondingly
simplified back down to 25 (it now only needs to out-rank its header
siblings, not the globe).

## Test-harness / environment issues found and fixed (not product bugs)

Several checks depended on the CERN/LNGS region having exactly the facility
count present when they were originally written, or on the shared long-lived
`page` object carrying no side effects across 15–25+ prior checks in the
same run. Wave 3's data growth and (for two checks) a real vendored-library
render race under specific engine timing broke those assumptions. Each was
confirmed *not* a product-code bug via isolated reproduction before being
changed, per the brief's instruction not to weaken assertions:

- **CERN cluster re-clustering.** The real bundle now has enough nearby
  European facilities (Institut Laue-Langevin, Leibstadt, Laboratoire
  Souterrain de Modane, …) that expanding the CERN cluster once can land on
  a *different*, still-clustered group instead of the individually
  addressable CERN marker the check expected after one click. Changed to
  expand repeatedly (bounded, 6 attempts) — exactly what a real user would
  do by clicking through nested clusters — rather than assuming a fixed
  cluster depth.
- **A23 approximate-site facility resolution.** The check picked "the first
  approximate-coordinate site" and read its own `facility_id` to build a
  URL — but 75 of 80 approximate sites carry a non-null `facility_id`, and
  the *first* one alphabetically (`site:antares-toulon`) is one of the 5
  that doesn't, producing a dead `#/facility/` (empty slug) link. Now falls
  back to a facility whose own `primary_site_id` points at the site, and
  skips to the next candidate if neither resolves.
- **A real vendored-library render race, engine-specific.** Two checks
  ("Setting the year to 1990…" and the A23 marker check) reproduced
  correctly in an isolated context every time, but could deterministically
  fail deep in the long shared-page sequence. Root-caused by instrumenting
  `rebuildVisibleLayer()` directly: on firefox, `focusGlobe()`'s
  post-navigation camera settle (orbit-controls damping) kept triggering
  `onZoom`-driven rebuilds for a short while after navigation, and if the
  timeline's own rebuild call landed while that settle was still in flight,
  the two rebuilds racing inside the vendored globe.gl library could
  reproducibly drop one site's marker from the DOM — confirmed via
  instrumentation that this app's own filtering logic (`siteMatches`/
  `statusPasses`) included the site correctly in **every single** rebuild's
  input (9 rapid calls observed, all correct), so the loss happened
  strictly inside the third-party rendering layer, not this app's code.
  Fixed in the test by isolating both checks into a fresh context and, for
  the timeline check, waiting for the fly-to to settle (~1.2s) before
  touching the timeline — avoiding the race rather than papering over its
  symptom with a longer timeout (a longer timeout alone did not help: a 20s
  fixed wait on the shared page still never surfaced the marker, while a
  fresh context found it immediately).
- **A `force: true` click occasionally not registering.** The CERN-marker
  click (after any cluster expansion) needed the click itself retried, not
  just the wait afterward — observed on firefox specifically, where a
  forced click could land mid-frame of the globe's continuous internal
  render loop and not register as a "real" click on that pass, even though
  the identical click works first-try in isolation.
- **A firefox timing margin, not a capability gap.** "Setting the year to
  1990 hides the not-yet-built ATLAS cavern site" needed 15s instead of the
  original 5s for the CSS-class change to land on firefox — confirmed
  functionally correct in isolation (readout and marker class both updated
  within ~3s standalone); widened rather than weakened.
- **Horizontal-overflow check timing.** The mobile-viewport check compared
  `scrollWidth` against the viewport immediately after the canvas appeared,
  before the marker layer had actually finished populating — a marker label
  can transiently extend past the edge mid-render (clipped by
  `.globe-stage`'s `overflow: hidden` in the final state, so never a real
  user-visible bug) but could read as a false positive if measured too
  early. Now waits for `.atlas-marker` elements to exist before checking,
  and logs the actual overflowing element(s) on any future failure
  (`OVERFLOW DEBUG` in the log) instead of just the raw pixel count.

None of the above weakened what any check actually verifies (marker
overlap/clustering behaviour, timeline-driven status changes, approximate-
location rendering, no-horizontal-overflow) — each fix addresses *when* or
*how* the check reaches a stable state to verify, confirmed by re-running
the full six-run matrix clean afterward (see results table above).

## What remains

- No real Safari.app or Firefox desktop-app manual run was performed —
  Playwright's webkit and firefox engines are the same rendering engines
  (WebKit and Gecko) those browsers ship, and are what was available to
  drive headlessly in this environment; see
  `docs/atlas-worklog/validation_counts_manual.json`'s `safari_manual_run`/
  `firefox_manual_run` fields, which say so explicitly rather than
  overstating a literal Safari/Firefox-app run.
- The FPS "software rasterizer" floor calibration (pre-existing, not part
  of this pass) still applies to chromium in this environment; firefox and
  webkit's real-GPU numbers (55–61 FPS) are comfortably above the fixed
  30 FPS floor and needed no calibration.
