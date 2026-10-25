# Release round 2 — the globe, the maps and the phone behave as a reader expects

Integration branch `atlas-release`, 2026-10-25. Three frontend streams (globe,
local map, phone; Sonnet subagents) were merged through a trial integration,
walked in a real browser by the integrator, and run through the full browser
suite against the real build. Two more research streams added instrument-level
arrays and a second accelerator pass.

## What changed

**Globe** (`globe.js`, `app.js`, `atlas.css`, `model.js`)

* The globe fills the stage. A 340 px empty column used to sit beside it whenever
  no record was open (the grid reserved the panel's track); the canvas also
  overflowed its container by 58 px.
* Choosing a facility (search, deep link, marker) stops the rotation for good and
  flies the camera to it in about a second; the selected marker carries an amber
  ring and an always-on caption, and clears when the panel closes. Before, the
  globe kept spinning and the facility drifted out of view.
* Labels are decluttered in screen space after every camera move: 0 overlapping
  label pairs on five dense deep links at four zoom levels (up to 6 before).
* Country borders and coastlines (Natural Earth 1:110m, public domain, vendored,
  116 KB, loaded after the first frame).
* Kind labels read "CEvNS", "Long-Lived Particle (LLP)", "Gamma-Ray" instead of
  slug title-case ("Cevns").

**Local maps** (`localmap.js`, `mapstyle.js`)

* Every map opens framed on what it draws (56 px padding), not on a stored centre:
  Fermilab used to open with its rings clipped off three edges; JUNO's baseline
  map now shows the hall and both reactor complexes 52 km away.
* Shapes carry their names on the map (CERN: "LHC tunnel", "SPS tunnel",
  "PS Booster tunnel"…), placed by priority and decluttered; a series of array
  records gets one label ("Auger SD1500 stations: 20 bands") instead of 23.
* A feature smaller than 8 px gets a point symbol, so H.E.S.S.'s telescopes and
  JUNO's reactors no longer vanish at the default zoom.
* When the chosen year hides everything, the map says so over the map with a
  one-click "Show features from all years".
* A reset-view button; hover tooltips no longer stack "Super Proton Synchrotron"
  one word per line.

**Phone and tablet** (`phone.css`, `phone.js`, up to 900 px)

* The sidebar and record panels were squeezed into a ~60 px strip under the
  globe. They are now bottom sheets — "Filters & legend", the record, the
  Results/Topics/Documents list, the map's layers and its selection drawer —
  with expand, close, Escape and focus management; the globe re-centres in the
  strip that stays visible. Portrait tablets (768 px) get the same layout instead
  of a 208 px globe beside an open record.

**Desktop bug found on the way:** the Results and Documents lists could not be
scrolled at all — `.mode-body` had no rule, so an 8,000 px list was clipped by
the panel. Fixed.

**Data merged this round**

* Instrument-level arrays: IceCube (86 strings, DeepCore, IceTop), Auger
  (~1,600 surface stations), Telescope Array (507), LHAASO (1,188 muon
  detectors, three pools), Baikal-GVD (11 clusters). The Auger frame was
  verified by the integrator: the Los Leones FD origin lands 23 m from the
  observatory's own communications tower in OpenStreetMap.
* Second accelerator pass: APS storage-ring orbit (1103.609 m), KATRIN beamline
  axis and main spectrometer, SNS linac building and instrument hall.
* Second currency pass: SNO+ vessel repair, SNS power upgrade, NOvA detectors
  follow the NuMI outage, HAYSTAC and Project 8 between phases, P-ONE back to
  construction, RNO-G restarted, nEXO paused, CTAO LST sub-array inaugurated.

## How the experience improved, and why it is better

* The first thing a reader does — search for a lab — now ends with the lab in
  front of them, ringed and named, instead of a panel beside a globe that keeps
  turning it away.
* A map can be read without hovering: names are on the shapes, small structures
  stay visible, and the view starts on the facility rather than on empty land.
* On a phone the Atlas is usable at all: before, filters and panels could not be
  reached.
* Results and Documents, the two list views, work on desktop for the first time
  since the dense-browsing change.

## Verified, and how

* Integrator walked the trial build at 1440×900, 768×1024 and 375×812: search →
  Fermilab (fly-to, halo, panel), CERN and JUNO maps (labels, framing), the phone
  sheet, the Results list scroll (8,085 px list, 403 px window, scrolls).
* `tests/browser_atlas.cjs` against the real build: 76/76 passed. Its ring-scale
  check measures the Main Injector at 1056 m drawn diameter vs 1057 m expected.
  One flaky assertion (it read a details element before its toggle handler ran)
  was fixed in the test.
* Map walkthrough: all 50 maps draw, scale bar present, 0 console errors.
* Validator 0 errors; Atlas tests 353 passed.

## Not done yet

* Search: Enter does not open the top result; record panels show empty section
  headings; spec values wrap one character per line in the DUNE panel; the
  filter list is long and flat — panels stream running.
* 48 shapes still unlocated (DUNE far-detector caverns, LBNF, UA1/UA2 halls…) —
  gaps stream running.
* Only Chromium was used for browser checks.
