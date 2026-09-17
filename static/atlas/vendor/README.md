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

## Decision record

`docs/HEP_ATLAS_GLOBE_LIBRARY.md` — measured bytes, measured FPS, and why the
alternatives were rejected.
