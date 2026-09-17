# HEP Atlas — globe library evaluation (Phase 1)

Decision date: 2026-09-16. Decider: the Atlas globe/frontend workstream.
Measurements were taken on this machine (Apple M4, macOS 25.6) against the
project's own Python handler, not from documentation.

## Decision

**Globe.gl 2.44.0 (UMD single file), vendored to
`static/atlas/vendor/globe.gl.min.js`,** plus a locally generated
`static/atlas/vendor/land-110m.json` land outline so the globe never contacts a
network at runtime.

Runner-up: three.js + three-globe (smaller, same renderer, but we would
re-implement the arc/point/ring/label layers we need). Rejected: deck.gl
GlobeView, MapLibre globe, CesiumJS — reasons below.

## Hard constraints this project imposes

1. **No build step, no framework.** The library must ship a UMD/IIFE file that
   works from a plain `<script src>`.
2. **No external CDN at runtime.** Anything the library fetches while running
   (tiles, textures, workers, wasm, terrain, an Ion token) must be vendorable.
3. **The handler's CSP is `default-src 'self'; script-src 'self'`**
   (`hepgraph/server.py:314`). Measured with `curl -sI`. This kills inline
   `<script>`, `eval`, `new Function`, and `blob:` workers. Verified in
   Chromium: the first perf harness with an inline script was blocked outright.
4. **The handler only serves whitelisted extensions** (`ATLAS_CONTENT_TYPES`,
   `hepgraph/server.py:28`). `.geojson` 404s — measured. Vendored geometry is
   therefore named `.json`.

## Measured bytes

`curl` of each candidate's published UMD/browser bundle, then `gzip -9`:

| candidate | bundle | raw bytes | gzip bytes |
| --- | --- | ---: | ---: |
| **Globe.gl 2.44.0** | `dist/globe.gl.min.js` (bundles three r180 + three-globe) | **1,728,142** | **479,772** |
| three.js 0.150.1 | `build/three.min.js` | 613,740 | 154,076 |
| three.js 0.160.1 | `build/three.min.js` | 669,884 | 166,607 |
| three-globe 2.35.1 | `dist/three-globe.min.js` | 454,876 | 145,191 |
| deck.gl 9.0.38 | `dist.min.js` | 1,245,838 | 364,670 |
| MapLibre GL JS 5.6.0 | `dist/maplibre-gl.js` | 939,269 | 247,901 |
| CesiumJS 1.x | `Build/Cesium/` — not a single file | ~4 MB JS + a mandatory `Assets/`, `Workers/`, `Widgets/` tree (tens of MB) | n/a |

Also measured: three.js `build/three.min.js` is **gone** from r0.169 and
r0.180 (both return a 62-byte stub from jsDelivr). The last three.js releases
with a usable UMD build are the r0.15x–r0.16x line. **A "three.js custom" path
with no bundler is pinned to a two-year-old three.js**; Globe.gl's own bundle
carries a current three (`REVISION "180"`, grepped out of the vendored file)
because it is pre-bundled.

Vendored geometry: Natural Earth 110 m land, decoded from
`world-atlas@2.0.2/land-110m.json` (55,207 B TopoJSON) to plain GeoJSON with
coordinates rounded to 2 dp → **76,538 B**, one MultiPolygon feature. Rounding
to 2 dp is ≈1 km at the equator, invisible at globe zoom. Using TopoJSON
directly would have cost an extra `topojson-client` dependency; a full-precision
GeoJSON was ~250 KB.

**Total vendored payload: 1,804,680 B raw / ~497 KB over gzip.** The handler
sends `Cache-Control: public, max-age=300` only for `generated/`; vendor files
get `no-cache`, so the browser still revalidates but 304s.

## Measured rendering

Harness: `static/atlas/_perf.html` + `_perf.js` (deleted after the evaluation,
reproduced below), served by `.venv/bin/python -m hepgraph.server --port 8790`,
driven by the project's Playwright Chromium (`chromium-1217`, "Google Chrome for
Testing") at 1280×900, headless, `--use-angle=default`.

Scene: the vendored land MultiPolygon as `polygonsData`, **3,000 points**
(`pointsData`, the merged-geometry path), **300 great-circle arcs**
(`arcsData`), `controls().autoRotate = true`, frames counted over a 3 s window.

| scene | build time | sustained FPS |
| --- | ---: | ---: |
| land + 3,000 points + 300 **dash-animated** arcs | 39.6 ms | **46.76** |
| land + 3,000 points + 300 static arcs | 22.3 ms | **46.86** |
| 3,000 points + 300 dash-animated arcs, no land | 187.3 ms (cold) / — | 50.09 |

Reported context: `WebGL 2.0 (OpenGL ES 3.0 Chromium)`, unmasked renderer
`ANGLE (Apple, ANGLE Metal Renderer: Apple M4, Unspecified Version)`, one
canvas.

Read this as: **~47 FPS is the headless compositor's ceiling here, not the
scene's cost.** Turning off the per-frame dash-shader animation changed FPS by
0.1 and build time by 17 ms — the GPU is not the limiter at 10× the Atlas's
real marker count (the Atlas pilot is tens of facilities/sites, hundreds of
institution dots in collaboration mode, and under a hundred arcs). The
brief's "thousands of points + hundreds of arcs at 60 FPS" is met with
headroom on a real (non-headless) compositor.

Harness source, for reproduction:

```js
const land = await (await fetch('/atlas/vendor/land-110m.json')).json();
new Globe(el).polygonsData(land.features).polygonAltitude(0.005)
  .pointsData(pts).pointAltitude('size').pointRadius(0.25)
  .arcsData(arcs).arcStroke(0.3);
```

## Criterion-by-criterion

| criterion | Globe.gl | three.js custom | deck.gl GlobeView | MapLibre globe | CesiumJS |
| --- | --- | --- | --- | --- | --- |
| vendorable, no bundler | **yes** — one UMD file, measured working under CSP `script-src 'self'` | yes, but only on a pinned r0.16x (no UMD after that) | UMD `dist.min.js` exists, but GlobeView examples assume ES modules + layer packages | UMD yes | no — multi-directory runtime tree, `CESIUM_BASE_URL`, worker + wasm loading |
| bytes | 1.73 MB / 480 KB gz | 0.61 MB + we write the layers | 1.25 MB / 365 KB gz | 0.94 MB / 248 KB gz **+ tiles** | ~4 MB + assets |
| runtime network | **none** — grepped the bundle: only `w3.org`/licence/docs URLs, no fetch target | none | none | **fatal** — a globe with no basemap is a grey ball; self-hosting vector tiles + glyphs + sprites is a data project of its own | **fatal** — imagery/terrain default to Cesium Ion |
| WebGL1 / WebGL2 | WebGL2 (three r180 dropped `WebGL1Renderer` at r163) | WebGL1 possible only on the old pinned line | WebGL2 only (luma.gl v9) | WebGL2 for globe projection | WebGL1+2 |
| touch | yes — OrbitControls pinch/drag, `pointerdown` picking | yes, we wire it | yes | yes | yes |
| perf at our scale | **measured above** | equal (same renderer) | equal or better at 10⁵⁺ | n/a | heavier |
| non-colour marker shapes | **yes, two ways** — `customLayerData` with arbitrary three.js meshes (extruded `THREE.Shape` glyphs), and `htmlElementsData` with inline SVG that keeps the DOM accessible | yes, by hand | via `IconLayer` + a sprite atlas we must generate | symbol layer + sprite sheet | billboards + atlas |
| label declutter / clustering | `labelsData` has `labelIncludeDot`/resolution but **no built-in declutter**; we cluster and cull ourselves in the data layer (same for every candidate except MapLibre) | by hand | `CollisionFilterExtension` (real declutter) | real declutter | real declutter |
| licence | **MIT** (three MIT, three-globe MIT) | MIT | Apache-2.0 | BSD-3-Clause (+ tiles have their own terms) | Apache-2.0 (+ Ion terms) |
| Safari / Firefox | three r180 targets both; WebGL2 is Safari 15+ | same | luma.gl v9 WebGL2 fine | globe projection needs recent Safari | fine |
| theming | full — `backgroundColor`, `globeMaterial`, per-polygon cap/side/stroke colour; no imagery needed | full | full | basemap style JSON | imagery-driven |
| WebGL-absence detection | trivial and **must be done before construction** — `canvas.getContext('webgl2')` guard, because `new Globe()` throws without a context | same | same | same | same |

## Why not the runner-up

three.js + three-globe is 1.07 MB raw (0.61 + 0.45), i.e. 38 % less than
Globe.gl's single file, and it is what Globe.gl wraps. We rejected it because:

- the saving is 660 KB **raw** but only ~180 KB gzipped, on a page the user
  loads once;
- three-globe's own UMD still needs a three.js UMD, and that pins us to
  r0.150/r0.160 — a knowingly stale renderer with no security or Safari fixes;
- Globe.gl is the part we would otherwise write: pointer picking against a
  sphere, `pointOfView` camera animation with easing, the arcs layer's
  great-circle interpolation and altitude-by-length curve, the rings layer, the
  HTML-elements layer that gives us accessible DOM markers. That is the
  decluttering-adjacent code we actually need and the code most likely to be
  subtly wrong.

The one thing we do **not** get free from any candidate at this scale is label
decluttering; we implement it in `js/globe/declutter.js` against projected
screen coordinates, which is library-independent.

## Risks accepted

- **WebGL2 required.** Safari < 15 and WebGL1-only GPUs get the non-WebGL
  fallback browse view, which the brief requires anyway. The guard checks
  `getContext('webgl2')` specifically.
- **480 KB gz of vendor JS** is the largest asset in the repo. Mitigated by
  loading it only after the WebGL2 guard passes — the fallback view never
  downloads it.
- **Pinned by sha256**, so an upstream change cannot silently alter the bundle.

## Vendored files

See `static/atlas/vendor/README.md` for version, URL, licence and sha256.
