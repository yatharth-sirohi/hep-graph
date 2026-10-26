# M3 stream — "Take it to a slide" (export image, facility sheet)

Branch `atlas-m3-export`. Plan: `docs/HEP_ATLAS_TEACHING_PLAN.md`, workstream 3.
No data was written; there is nothing to source in this stream.

## What was built

* **Export image** (header, next to Key and Filters; a popover like the Key). PNG of the
  globe or of the open local map, two sizes: *Slide* (exactly 1920 x 1080: the view is fitted
  between a title band and a citation band) and *Twice the size on screen* (2 x the stage, plus
  the two bands). The dialog shows the picture that will be saved, the file name, and what
  happened to the map tiles; it follows the view while open (a year, a selection).
  In the image: the view; the selected entity's name (a map: the map's name) and a line under
  it; the timeline year or range, large; the footer
  `HEP Atlas — hep-graph.vercel.app/atlas — data version <manifest.version> — accessed <date>`;
  on a map also a metre scale bar (measured with Leaflet's own `distance()`), a north arrow
  (grid north at a pole) and a second footer line with the credits.
  File name: `hep-atlas_<slug>_<year>.png` (`t2k`, `cern-map`, `globe`; a range is `1990-2000`).
* **Facility sheet**: "Print facility sheet" in every facility panel builds `#print-sheet`
  (name, kind, status as of the timeline year, location, plain summary, key specifications,
  experiments hosted with their years, a to-scale snapshot of the facility's local map with
  scale bar, north arrow and credits, the sources in short form, the citation footer) and
  calls `window.print()`. `export.css` prints only the sheet while it is printing, and hides the
  page's chrome in any print.

## How it is made

* Globe: `globe.js` `captureFrame(pixelRatio)` renders the frame again at the export's pixel
  ratio and copies it in the same task (no `preserveDrawingBuffer`, which would cost every frame).
  `exportpaint.js` then draws the HTML overlays from the elements themselves: the very SVG glyphs
  `globeicons.js` built (serialized, haloed by whatever `filter` the stylesheet gives), caption
  and beam-label boxes (background, border, radius, shadow, opacity from computed style), text with the
  browser's own line breaks, and leader lines. A change to a stylesheet or to `globeicons.js`
  therefore shows up in the export with no change in `export.js`.
* Map: tiles are drawn from the `<img>` elements Leaflet already loaded (nothing is fetched for
  the export); the vector layer from the live SVG with computed paint written onto it; symbols
  and labels from their elements.
* **Tiles and CORS.** `tile.openstreetmap.org` answers `Access-Control-Allow-Origin: *`
  (checked with `curl -I`, 2026-10-26) and `localmap.js` already asks with `crossOrigin`, so the
  tiles can be drawn without tainting the canvas. This is checked at every export anyway: if the
  canvas comes out tainted, or the tiles of the view had not all arrived, the image is made
  without them (shapes on a plain background), the credit for tiles is not claimed, and the dialog
  says which. No tile proxy, no CSP change.
* Credits: a map export always lists the map record's own `attribution` strings (some maps
  carry CC-BY or municipal-GIS credits, not only OSM) in the footer; the sheet's snapshot also
  has them drawn on the image and in its caption.

## Decisions worth a second look

* The Slide preset *fits* the view (no cropping), so a stage narrower than 16:9 (the globe with a
  panel open) sits in the middle of the slide with margins; "twice the size" keeps the stage's own shape.
  Re-framing the globe for 16:9 would mean re-running the caption declutter at another size.
* A sheet's map snapshot needs the real map, so the button opens `#/map/<facility>` (replace, no new
  history entry), draws it, and puts the reader back (`state.navigate(..., { replace: true })`).
  If the facility's map is already open, that view is the snapshot.
* Key specifications: the facility's `specs`; 33 of 48 facilities have none, so an accelerator
  laboratory falls back to its current accelerators' own `specs` (labelled as such) and others say
  "None recorded in the Atlas". Experiment years are the first to last `active` interval (or
  "present"; "building (2017)" etc. for one that never ran).
* Not offered on a phone (header has no room; `export.css` hides it). Print works anywhere.
* A sheet lists at most 30 experiments and 8 sources and says "and N more"; the panel has all.

## For the integrator

Shared files touched, each by a few lines: `index.html` (link + header button), `app.js`
(import + `exportModule.init`), `panels.js` (import + one button in `renderFacility`),
`globe.js` (`captureFrame` on the API), `localmap.js` (`exportInfo()`), `about.html` (one
paragraph), `tests/browser_atlas.cjs` (two records, before the local-map block),
`tests/test_atlas_static_css.py` (`export.css` in the brace-balance list). New: `js/export.js`,
`js/exportpaint.js`, `export.css`. The embed/projector streams that hide the header will hide
Export with it, which is wanted.
