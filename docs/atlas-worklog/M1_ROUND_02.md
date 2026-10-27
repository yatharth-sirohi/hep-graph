# M1 round 2 — what the first-impression review found, fixed

Integration branch `atlas-m1`, then `atlas-next`, 2026-10-26. An independent
Sonnet reviewer used the round-1 build cold, as a student on a phone, an
instructor on a projector and a researcher checking numbers. Two fix streams
(globe; card, panels, Key and data) addressed every finding, and the integrator
re-checked each fix in a browser.

## What changed

- **Safari and iPhone kept every selected caption.** A `filter: drop-shadow` on
  the marker wrapper clipped the offset caption and the selection ring to a
  square in WebKit. The glow now sits on the glyph only.
- **Selected labels never overlap.** The label-declutter scheduler dropped any
  request made while a pass was pending, so after a camera flight labels could
  stay overlapped until the window was resized. Every request is now honoured,
  with a final pass when the camera settles.
  - Measured over cold deep links to T2K, K2K, NOvA, MINOS, OPERA, DUNE, CERN and
    Hyper-K: 0 overlaps in 120 loads across Chrome, Firefox and WebKit.
  - The same check is a browser test.
- **Captions** clip at their end, not both ends, in WebKit. They read their size
  from `--marker-label-size`, which projector mode raises.
- **Beams are visible where they matter.**
  - Quiet (shut-down or completed) arcs are about 4.6 px dashes.
  - T2K and Hyper-K, which share their ends, fan 12 px apart.
  - A beam selection frames closer.
  - The first-visit view shows North America with the labelled 1285 km beam.
  - Labels keep the source's precision ("735.3 km", "~810 km").
  - A beam arc's description says it is drawn above the surface and that the
    beam travels straight through the Earth.
- **Start-here answers land.**
  - The Higgs question lands on CERN, selected, with ATLAS's and CMS's 2012
    papers.
  - Neutrino oscillations opens with its plain question and its experiments,
    framed so North America, Europe and East Asia are in view.
  - The depth question was replaced by "How far does a neutrino beam travel?"
    (T2K) until the depth chart existed (M4).
- **A complete Key.**
  - It adds cluster badges, site dots and beam arcs, drawn with the globe's own
    art.
  - Institution dots have their own colour, no longer the amber of
    "Construction".
  - Tabbing out of the Key closes it.
- **Facility map links** are in the panel header (CERN's was 420 px below the
  fold).
- **Data.**
  - K2K's beam now starts at a KEK proton-synchrotron site, not the Belle II hall.
  - NuMI's distance reads 735.3 km everywhere.
  - The card no longer claims to show "every major" facility.

## How the experience improved, and why it is better

The round-1 build looked right in Chrome but lost its labels on an iPhone, sometimes
left labels piled on each other, and answered two of its four opening questions
with the wrong screen. A first visitor now gets labels that never collide on any
engine, beams they can see, and four questions that each land on the answer.

## Verified, and how

- Integrator browser walks of each fix: Key art, the institution colour, header
  map links, the Start-here answers, and T2K at 1440 and 390 px.
- Suites on the merged build. The full three-engine result is in the M6 workup,
  which covers the final integrated build.
