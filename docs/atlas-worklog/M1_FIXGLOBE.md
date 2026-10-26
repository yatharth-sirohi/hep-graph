# M1 round 2: globe-side fixes (branch `atlas-m1-fixglobe`)

Owner: the globe fix stream. Files: `js/globe.js`, `globe.css`, the marker, caption and
beam rules in `atlas.css` and `phone.css`, and one constant in `js/start.js`. No data
was written, so there are no entity tables.

## What changed and why

| # | Finding | Change |
|---|---|---|
| 1 | WebKit lost every selected caption and clipped the rings | `filter: drop-shadow` is on the glyph `svg` only. The marker wrapper has no filter (WebKit clips what hangs outside a filtered element's box to a square). |
| 2 | Declutter pass dropped | `scheduleDeclutter` never returns without a follow-up: a request that arrives while a pass waits makes it be followed by another; a pass is also followed by another when the camera moved since the previous one or when a selected marker or beam had no screen position yet (bounded at 30). Beam pill sizes come from unseen copies of the pill (`.bl-measure`), not a canvas estimate that ignored italics and padding. |
| 3 | WebKit cut captions at both ends | `text-align: left` on the caption. |
| 4 | Beams invisible | Quiet arcs 4.6 px (5.8 selected), dashes a fixed size on screen (10 px dash, 6 px gap), dots (5/8 px) for a beam yet to run. Arcs that share both places are fanned out sideways by 12 px (height alone is invisible from above). A beam selection frames at 0.054 radii per degree, never closer than 0.30. First view `{44, -70, 1.8}`: North America with CERN and Gran Sasso at the far limb, so the 1,285 km beam is drawn and labelled. |
| 5 | 12 px captions on a projector | `--marker-label-size: clamp(12px, 0.75vw, 15px)`, declared with `:where(:root)` (any other declaration wins); every caption, count and pill reads it; the pill is `2em` high; cluster badges grow with it; changing it rebuilds them. Declutter checked at 20 px. |
| 6 | "735 km" for 735.3 km | `formatBaselineKm` keeps the recorded value to one decimal and marks an approximate one in the source's own words ("~810 km", "about 295 km"). |
| 7 | Cluster counts overlap in a phone strip | Under 220 px of visible globe the container gets `is-short-strip`: glyphs only (hover or focus still names a marker). |
| 8 | Arc above the surface, beam through the Earth | Pills carry `aria-describedby` and a `title` with one sentence saying so; the arc's hover tooltip ends with it. Nothing visible is added. |

Also: institution dots and their arcs read `--institution` (fallback `#a3b0ff`), per the
UI stream's note; cluster badges and selection stay amber.

## Checks

Server on 8865 from this worktree, `HEP_ATLAS_DATA=generated`, one browser at a time.

* Cold loads of `/atlas?welcome=0#/experiment/<x>` and `#/facility/cern` at 1440x900, five
  each, waited until the selected captions and pills had not moved for 1.5 s, then every
  selected caption and beam-pill box compared pairwise. t2k, k2k, nova, minos, opera,
  dune, cern in Chrome, Firefox and WebKit: 0 of 105 loads overlapped; hyper-kamiokande:
  0 of 15. Before the fix, with the CPU throttled 6x in Chrome: t2k 3 of 6, k2k 5 of 6.
  After, the same throttle: 0 of 12.
* Chrome at 1920x1080 with the label size forced to 20 px: no overlap on t2k, dune, nova,
  k2k, opera, cern.
* WebKit: T2K shows its 3 captions and full rings; DUNE names Fermilab and SURF; on a
  390 px phone "Roque de los Muchachos Observatory" is cut at the end only.
* `tests/browser_atlas.cjs` (chromium) 101 passed, `tests/browser_atlas_a11y.cjs` 38 passed
  with 0 axe violations, `pytest` 689 passed, 139 skipped (no database).
* One browser check added: no overlapping selected captions or beam pills after a cold
  deep link (CPU throttled in Chromium).

## Unresolved, for the integrator

* The no-card default view (`ready()`: 20 N, 10 E, altitude 2.4) is unchanged, so a returning
  visitor's globe still shows no labelled beam. Only `FIRST_VIEW` moved.
* During a flight on a very loaded machine the captions can overlap for a few seconds
  before the trailing passes catch up; they always end clear. Measured 3 to 9 s after
  load on a machine at load average 36, 0 by 13 s.
* The first view is now a closer globe (altitude 1.8, about 620 px across at 1440x900).
