# Vendored runtime libraries for HEP Atlas

No build step and no CDN at runtime: every file here is served by
`hepgraph/server.py` from `/atlas/vendor/`. The handler's CSP is
`script-src 'self'`, so these must be real files, never inline or remote.
The handler also only serves whitelisted extensions, which is why the land
outline is `.json` and not `.geojson`.

Re-vendoring: `curl -sSL -o <file> <url>` then check the sha256 below. If the
hash changes, read the diff before committing it.

## globe.gl.min.js

| | |
| --- | --- |
| package | `globe.gl` |
| version | 2.44.0 |
| url | https://cdn.jsdelivr.net/npm/globe.gl@2.44.0/dist/globe.gl.min.js |
| bytes | 1728142 |
| sha256 | `3b5bfa647663072df455e4e993082f89fc8a06859d59de5bc13ebf534ac3b0b2` |
| licence | MIT (Vasco Asturiano) |
| bundles | three.js r180 (MIT), three-globe (MIT), and their deps |
| globals | `window.Globe` |

Contains no runtime fetch target: the only absolute URLs in the file are XML
namespaces, licence links and library homepages. Requires WebGL2.

## land-110m.json

| | |
| --- | --- |
| source package | `world-atlas` 2.0.2 (`land-110m.json`, TopoJSON, 55207 B) |
| url | https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/land-110m.json |
| derived by | decoding the TopoJSON to a GeoJSON `FeatureCollection` (one `MultiPolygon`) and rounding coordinates to 2 decimal places |
| bytes | 76538 |
| sha256 | `1e3f29d92af56d77a12fcceded66b60e05f5cc2d0de4c8ff7676d36ff9624cc8` |
| licence | Natural Earth data: public domain. `world-atlas` packaging: ISC (Mike Bostock). |

Fed to `Globe.polygonsData()` so the globe has coastlines without a raster
texture or a tile server.

## countries-borders-110m.json

| | |
| --- | --- |
| source package | `world-atlas` 2.0.2 (`countries-110m.json`, TopoJSON, 107761 B, sha256 `2516c915867c7baf18ddec727aec46c315541a07cfb3d79a6559b05d5e94eee8`) |
| url | https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json |
| underlying data | Natural Earth 1:110m Admin 0 - Countries |
| derived by | decoding the TopoJSON arcs and keeping only line work: arcs used by two countries become the `border` feature, arcs used by one country become the `coastline` feature (both one `MultiLineString`). Country names/ids are dropped. Touching arcs are chained end to end into longer paths (the same edges, fewer draw calls), the degenerate Antarctic edge along the pole is removed, and coordinates are rounded to 2 decimal places |
| bytes | 116137 |
| sha256 | `71451ca998744a66edf448d6f99533f8d4eed752e1d41424926019c6004ba330` |
| licence | Natural Earth data: public domain. `world-atlas` packaging: ISC (Mike Bostock). |

Drawn by `globe.js` as a `pathsData` layer (thin, low-contrast lines) on top of
the `land-110m.json` fill. It is fetched after the globe's first paint and the
globe works without it: if the request fails the land fill and its own coast
stroke simply stay as they were. The 110m scale is a political-geography aid
for orientation, not a survey: disputed and recently changed borders follow
Natural Earth's de facto line work and the atlas takes no position on them.

## leaflet/

The 2D map engine for the to-scale local-map view
(`docs/HEP_ATLAS_GEOMETRY.md` §4). Loaded **lazily** — `static/atlas/js/localmap.js`
injects the script and stylesheet the first time a `#/map/<slug>` route
opens, so the globe's cold load does not pay for it.

| | |
| --- | --- |
| package | `leaflet` |
| version | 1.9.4 |
| url | https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/ |
| licence | BSD-2-Clause (Volodymyr Agafonkin; `leaflet/LICENSE.txt`) |
| globals | `window.L` |
| WebGL | not required — the map view works in the no-WebGL fallback |

| file | bytes | sha256 |
| --- | --- | --- |
| `leaflet.js` | 147552 | `db49d009c841f5ca34a888c96511ae936fd9f5533e90d8b2c4d57596f4e5641a` |
| `leaflet.css` | 14806 | `a7837102824184820dfa198d1ebcd109ff6d0ff9a2672a074b9a1b4d147d04c6` |
| `images/layers.png` | 696 | `1dbbe9d028e292f36fcba8f8b3a28d5e8932754fc2215b9ac69e4cdecf5107c6` |
| `images/layers-2x.png` | 1259 | `066daca850d8ffbef007af00b06eac0015728dee279c51f3cb6c716df7c42edf` |
| `images/marker-icon.png` | 1466 | `574c3a5cca85f4114085b6841596d62f00d7c892c7b03f28cbfa301deb1dc437` |
| `images/marker-icon-2x.png` | 2464 | `00179c4c1ee830d3a108412ae0d294f55776cfeb085c60129a39aa6fc4ae2528` |
| `images/marker-shadow.png` | 618 | `264f5c640339f042dd729062cfc04c17f8ea0f29882b538e3848ed8f10edb4da` |

The `images/` sprites are referenced by `leaflet.css` (the layers control and
the default marker icon). They are vendored so the stylesheet never reaches
out to a CDN; the map view itself draws GeoJSON paths, not pin markers.

The only absolute URLs inside `leaflet.js` are the SVG namespace and the
library homepage: it fetches nothing at runtime. Tiles are a separate,
explicit choice made by `localmap.js` — OpenStreetMap standard tiles with the
mandatory attribution, no API key, toggleable, and the one third-party origin
named in the server's `img-src` (`hepgraph/server.py`).

## Decision record

`docs/HEP_ATLAS_GLOBE_LIBRARY.md` — measured bytes, measured FPS, and why the
alternatives were rejected.
