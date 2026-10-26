# M1 round 2: Start-here answers, panels, the Key, two data items

Branch `atlas-m1-fixui`, 2026-10-26, from `atlas-m1` e4c1f05. Stream: card, panels,
Key, two data items. Not touched (another stream owns them): `globe.js`, `globe.css`,
the caption rules. `start.js` is unchanged (the questions live in `index.html`).

## What changed

### 1. The Start-here answers

| Question | Link | What the reader gets |
| --- | --- | --- |
| Where is DUNE's far detector? | `#/experiment/dune` | unchanged |
| Where was the Higgs discovered? | `#/result/atlas-higgs-observation-2012` | CERN selected and framed on the globe; panel: the place (`Where: CERN (local map)`), then `Announced the same day at CERN: CMS — Observation of a new boson at a mass of 125 GeV`, then the ATLAS summary |
| Which experiments study neutrino oscillations? | `#/topic/neutrino-oscillations` | the plain question, then the experiments (Current 11, Historical 13), the globe at a whole-Earth altitude; the physicist's overview is collapsed |
| How far does a neutrino beam travel? (replaces "How deep are the underground labs?") | `#/experiment/t2k` | T2K, the globe on its 295 km beam, Tokai to Kamioka |

Hints, as shipped: "ATLAS's 2012 paper with CMS's beside it; the globe flies to CERN";
"Lists them and lights their sites across the globe"; "Opens T2K; the globe flies to
its 295 km beam, Tokai to Kamioka". The card's lede is now "Particle-physics
facilities on to-scale maps, with every fact traced to its source." (coverage is
partial, so no "every major facility").

**The Higgs route, and why.** A result has no place of its own, so the route stays the
ATLAS result and the globe now selects *the facility the result names* (`app.js`
`selectionFor`): any result panel now flies to and marks where it was done. The two
discovery papers are made visible together by a derived rule, not an authored link:
`panels.js` `sameDayResults` finds results with the same full date, the same
`date_kind`, the same `result_type`, a shared facility and a shared topic. Over all 109
results it finds exactly three pairs, all true joint announcements: ATLAS+CMS Higgs
(2012-07-04), ATLAS+CMS Higgs ten years on (2022-06-30, "Preprint dated the same day"),
CDF+DØ top quark (1995-03-02). The label follows `date_kind` ("Announced", "Preprint
dated", "Published"). The `Where:` line moved up under the subtitle; its text is
unchanged (a test pins `Where: CERN (local map)`). Alternatives rejected: `#/facility/cern`
(no rule says which two of CERN's results come first); `?m=results&…` with the facility
(the results list covers the globe's left half and hides the marker).

**The topic camera.** `globe.js`'s `fitHighlight` falls back to "the densest region" when
the lit places span most of the Earth (that is the Asia-only view). It is already called
from `app.js`; the change is in `app.js` `frameTopic`: `fitView(points)` (exported by
`globe.js`) says whether a fit exists; if so `fitHighlight()` runs as before, otherwise
the camera goes to a whole-Earth view through `showView` (existing API) at altitude
2.6 to 3.4, looking from the spot (latitude within ±60°, 5° grid) from which the most lit
places are inside the camera's 76° reach. `model.js` has the pure `markerPoints` and
`worldView`. For neutrino oscillations that is (60° N, 15° E) at 3.4: North America,
Europe and East Asia are all on screen. IceCube (South Pole) cannot share a view with
them (antipodal), so it is the one lit place out of frame; the globe can be turned.

**Topic panel order**: h2, plain question, "24 experiments in the Atlas study this.
Their sites are lit on the globe; the rest is dimmed.", Experiments (open, counts in the
group headings), Related results, Technical overview (closed), Observables (closed).

### 2. Facility panels: the map link in the head

`panels.js` `localMapHeader`: under the status badge, one `◎ Open local map: <map name>`
link per map (JUNO and KM3NeT have two), each with its "N features drawn to scale · M not
drawn" line. The "Local map" card at the foot of the facility panel is gone (it was 420 px
below the fold on CERN's: now y=168 at 1440×900). Experiment, site, detector, accelerator
and beamline panels are unchanged.

### 3. The Key

* New entries, drawn not described: cluster badge (the globe's own cluster glyph plus its
  count), experiment-site dots (the globe's 12 px site glyph in three status colours),
  beam running (mini-SVG of the arc: cyan-blue gradient, flowing dashes, glow) and beam under
  construction or ended (dotted, dimmer). The beam colours are copies of `globe.js`'s
  `BEAM_COLOR`, `BEAM_GLOW_COLOR`, `BEAM_COLOR_QUIET` in `globeicons.js` `BEAM_KEY_COLORS`;
  `tests/test_atlas_static_css.py::test_key_beam_colours_match_the_globe_arcs` fails if
  they drift. The flow stops under `prefers-reduced-motion`.
* Institution dot colour: new token `--institution: #a3b0ff` (pale periwinkle) in
  `atlas.css`; the Key swatches use it. A pale grey-blue (the suggested colour) is 9 CIE76
  from Completed (#b3bec5) so would have merged with a status; `#a3b0ff` is at least 21 from
  every status colour, `--amber`, `--teal` and every facility-kind colour, and 8:1 on the
  ocean (`test_institution_colour_is_not_a_status_colour`).
* The popover closes when focus leaves it (Tab, Shift+Tab), the way Escape does, and not
  when the pointer is inside it or on its button (Safari does not focus a clicked button).

### 4. Wording

The card's lede (above). The Higgs answer is no longer ATLAS-only.

### 5. Data: K2K's origin

New `site:kek-ps-k2k-beamline`, "KEK 12 GeV proton synchrotron and K2K beamline (Tsukuba
campus)", `facility:kek`, setting surface. Linked from `beamline:kek-neutrino` (the
baseline's `from_site_id`), `accelerator:kek-ps` (`site_id`) and `map:kek` (`site_ids`, so
the site panel offers the map). Stale notes updated in `facility:kek`,
`accelerator:kek-ps`, the baseline's distance and spec notes, and
`geometry:kek-neutrino-direction-line` `method` (one sentence; no quote changed).

| Field | Value | Source and quote |
| --- | --- | --- |
| coordinate | 36.1520734, 140.0726871, kind `campus`, confidence `approximate`, precision 1100 m | area centroid of the OSM KEK campus polygon (way 100702753, 84 vertices; `src:geo-kek-osm-campus-boundary`); the farthest vertex is 1003 m from it. A17: a `campus` point may rest on a rank-8 source; it is not labelled `detector` (A23) |
| K2K beam from the KEK PS | quote on `coordinates.quote` | `src:k2k-tutorial-page` https://neutrino.kek.jp/k2k/ofl/tutorial/html/k2k-e.html, fetched 2026-10-26: "a high intensity muon neutrino beam with average evergy of 1.5 GeV, produced at KEK-PS, will be injected to Super-Kamiokande, located 250 km west of KEK." (the page's own spelling "evergy") |
| North hall | in the coordinate note | same page: "The primary proton beam will be bent from North hall to target station" |

A21: the great-circle distance to Super-Kamiokande is 249.44 km, 0.22 % from 250 km (the
Belle II point gave 249.6 km). Validator: 0 errors; the warning count is unchanged at
1596. `tests/test_atlas_k2k_origin.py` pins the link, the approximate campus point and the
2 % rule.

### 6. NuMI wording

`beamline:numi` `direction.value` said "734 km away" (the NuMI beam paper's rounded
figure). It now says "735.3 km from the NuMI target", sourced additionally to
`src:minos-detector-paper-2008`, with a note: the detector paper's 735.3 km from the
target; the beam paper gives a rounder 734 km without saying what it measures from; the
detector paper's survey figure from the upstream end of the first horn is 735.3380 km,
i.e. 735.3 km to the precision quoted. No quote was changed. (Note: the older
`distance.note` calls 734 km a rounding; 734 is 1.3 km from 735.3, so that is not
rounding of the same number, only a rounder figure with no stated reference point. The
new wording does not claim a cause.)

## For the integrator

1. **Institution dots on the globe are still amber until `globe.js` reads the new token.**
   `globe.js` draws them with `cssToken('--amber', …)`, the accent shared with cluster
   badges and selection, so changing `--amber` would recolour the whole interface; no
   institution token existed, so `--institution` was added and the Key uses it. Three
   one-token edits in `globe.js` finish it (checked here on a temporary copy: institution
   dots then draw `#a3b0ff`, then reverted; the cluster badge stays amber, as the Key shows).
   The patch is below (lines 1197, 1214, 1240 of e4c1f05). Until it lands, the Key's
   institution dot (periwinkle) does not match the globe's (amber).
2. The Key's beam colours are copies; the test above keeps them honest.
3. `static/atlas/generated/` was rebuilt for checking and restored before the commit.
4. Not mine, seen in passing: T2K's beam labels overlap at the default framing (captions),
   and a clipped caption fragment ("..") sits at the stage's left edge on the Higgs view.
5. Hard-coded in `index.html`: "295 km" in the T2K hint (T2K's panel shows 295 km from the
   record). If T2K's baseline changes, the hint must too.

```diff
@@ -1194,7 +1194,7 @@ export function createGlobe(container, {
-          color: cssToken('--amber', '#f2b441'),
+          color: cssToken('--institution', '#a3b0ff'),
@@ -1211,7 +1211,7 @@
-            color: [withAlpha(cssToken('--amber', '#f2b441'), 0.55), withAlpha(cssToken('--amber', '#f2b441'), 0.05)],
+            color: [withAlpha(cssToken('--institution', '#a3b0ff'), 0.55), withAlpha(cssToken('--institution', '#a3b0ff'), 0.05)],
@@ -1237,7 +1237,7 @@
-            color: [withAlpha(cssToken('--amber', '#f2b441'), 0.55), withAlpha(cssToken('--amber', '#f2b441'), 0.05)],
+            color: [withAlpha(cssToken('--institution', '#a3b0ff'), 0.55), withAlpha(cssToken('--institution', '#a3b0ff'), 0.05)],
```

## Unresolved

* No source consulted gives coordinates for the KEK-PS ring, the North hall or the K2K
  target station (the existing log `GEOMETRY_jparc-kek.md` found none either); the site is
  campus-grade only.
* The South Pole lit place is out of frame in the oscillations view (above).

## Candidates considered and rejected

* The North Counter Hall centroid (36.15203, 140.07230) as the site's point: 40 m from the
  campus centroid, but its identification with the PS is circumstantial in
  `geometry:kek-north-counter-hall`'s own notes, so a campus point with 1100 m precision is
  the honest claim.
* Recolouring `--amber` for institutions (breaks every other amber use); a CSS hue-rotate
  filter on institution markers (would double-apply once `globe.js` reads the token).

## Checks

* Chromium (system Chrome): `tests/browser_atlas.cjs` 102 passed; `tests/browser_atlas_a11y.cjs`
  40 passed, 0 axe violations across 27 states. Firefox and WebKit: not run in full (memory);
  the four-question walk and the Key's focus behaviour were run in both, same results as
  Chromium.
* `pytest -q`: 694 passed, 139 skipped (database-backed). Validator: 0 errors.
* Assertions changed on purpose: the card's description (lede), the four link hrefs and
  texts, the loop over the answers (T2K added, the old `?fk=underground_laboratory`
  filter step removed), and the Key's required terms (four added). No other assertion
  changed.
* Walked in a fresh context (no storage) at 1440×900 and 390×844 in Chromium; screenshots
  under the scratchpad `fixui/shots/`.
