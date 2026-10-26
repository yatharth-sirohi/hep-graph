# Release round 4 — the shapes that matter most, placed from survey data

Integration branch `atlas-release`, 2026-10-25. One Sonnet research stream
worked the highest-value entries left in the maps' "unlocated" lists; the
integrator re-read the coordinate-system definition and the coordinate tables
it rests on before merging, and opened the changed maps.

## What changed

**DUNE's far-detector caverns (SURF)** — drawn on the 4850 Level for the first
time, north and south caverns, from the four module coordinates published in
Heise 2026 (arXiv:2603.06504, Table 4) and the 158.95 × 19.81 m excavated size
(LBNF community meeting, Dec 2023). Area check 3148 m² vs 3145.5 m². The SURF
far-detector site point moved onto the centre of the four modules (it had been a
surface proxy 212 m away).

**Fermilab, re-placed from its own survey frame.** Fermilab's design reports
give element positions in the Fermilab Site Coordinate System (origin A0, Y axis
at azimuth 38°16′48.01429″, Beams-doc-1148). Converting those tables showed that
the Main Injector and Recycler, placed in round 1 by fitting the ring road around
them, were 38–74 m off and rotated 5.7° — a road fixes a ring's centre, not its
rotation. They are now placed from the Main Injector TDR's site-coordinate
appendix (rigid fit to 89 rows, 0.34 m rms), confirmed three independent ways
(MI-60 azimuth 339.6° vs 339.51°; the 8 GeV line ends 1.2 m from the ring; the
LBNF 7.2° bend points at SURF to 0.06°). The Tevatron moved 41 m and its accuracy
tightened from 60 m to 10 m.

**NuMI, newly drawn** — target, primary proton line, decay pipe (674.2 m vs
675 m), target hall, absorber hall and the MINOS underground enclosure that also
hosts MINERvA, ArgoNeuT and SENSEI; the old NuMI target point was 103 m off. Beam
azimuth 336.18° vs 336.17° published.

**CERN** — the surface access buildings of the halls where UA1 and UA2 found the
W and Z (BA5, BA4), CAST's SR8, ECN3 (NA62), and the HL-LHC surface complexes at
Points 1 and 5 (3256 / 3351 m² vs CERN's "3300 m² of buildings" per point). The
UA1/UA2/CAST/ECN3 site points, which had sat on a shared Meyrin geocoder point
up to 3 km away, now sit on their own buildings.

## How the experience improved, and why it is better

* The most-asked-about experiment of the next decade, DUNE, now shows where its
  detectors are — a kilometre and a half underground in Lead, beside the Ross
  shaft — instead of a note saying the caverns are not located.
* Fermilab's map shows the whole neutrino chain: Booster → Main Injector → NuMI
  target → decay pipe → MINOS hall, on true paths, and the ring that feeds it is
  where the lab's own surveyors put it, not where a road suggested.
* A reader looking for "where the W and Z were discovered" now finds the UA1 and
  UA2 buildings on the SPS ring rather than a dot in the Meyrin car park.
* Round 1 accepted a shape that was 54 m off on average; this round caught it
  with better evidence. The Atlas records the change and why.

## Verified, and how

* Re-read in the archived Beams-doc-1148: origin "N 41° 50' 14.312704"",
  "W 88° 15' 41.143123"", Y-axis azimuth "38° 16' 48.01429"", false easting
  "X = 100000.000 ft".
* Re-read in arXiv:2603.06504 Table 4: FD1 (NE) 103.7546341 W 44.3459914 N …
  FD4 (SW); the site point is their mean (44.3455559 N, 103.7552387 W).
* Confirmed the MI TDR contains its "Main Injector Ring Site Coordinates"
  appendix.
* Opened Fermilab, SURF and CERN in the browser: all draw, labelled, 0 console
  errors. Validator 0 errors.

## Not done yet

* LBNF target hall and DUNE near-detector hall: no published coordinate; the
  design-stage chain leaves ~50 m of uncertainty, so they stay unlocated.
* IceCube Upgrade strings (only the design layout is published; drawing it would
  show never-built strings), KEK-PS, SLC arcs, ZEUS hall, Linac2, ISR, Mu2e hall.
* Fermilab frames its whole campus boundary, so the accelerator core starts small
  on screen — framing should favour structures over boundaries.
