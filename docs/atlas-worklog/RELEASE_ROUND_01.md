# Release round 1 — every facility opens a map; the dates are current

Integration branch `atlas-release`, 2026-10-25. Five research streams
(Sonnet subagents in their own worktrees) were merged after the integrator
re-opened the sources behind every principal shape and status change, and
opened every changed map in a browser.

## What changed

**Maps.** 39 maps covering 38 facilities → 50 maps covering all 48 facilities.
Geometry records 175 → 278, sources 1,606 → 1,756.

| Facility | Before | After | Principal evidence (re-checked by the integrator) |
| --- | --- | --- | --- |
| H.E.S.S. | partial | layout to scale | CT1–4 square, measured sides 118–121 m vs MPIK "square with 120 m side length" |
| VERITAS | partial | layout to scale | four telescopes, spacings 81.6–125 m vs "distances range from 81 m to 127 m" (arXiv:0912.3841) |
| HAWC | partial | layout to scale | all 300 tanks; hull 22,416 m² vs "300 water Cherenkov detectors spread over 22,000 m2" (arXiv:1310.0074) |
| La Palma (MAGIC, LST-1–4) | partial | layout to scale | MAGIC 86.2 m vs "separated by a distance of 85 m"; LST-1 96 m vs "∼100 m" (arXiv:2310.01954); LST sub-array inaugurated 2026-10-15 (CTAO news) |
| Fermilab | Main Injector unlocated | Main Injector + Recycler drawn | rebuilt from the 1994 design handbook lattice; 3319.37 m vs 3319.419 m and the independent 28.789277 m MI-60 offset |
| PSI | marker only | layout to scale | experimental hall 134 × 52 m vs "130x50x20 m3" (Seidel, KEK seminar) |
| LANSCE (Los Alamos) | marker only, **empty in 2026** | layout to scale | 30 m Proton Storage Ring vs "30-m-diameter Proton Storage Ring" (LA-UR-05-9402); linac building, Lujan Center |
| Jefferson Lab | partial | layout to scale | CEBAF racetrack from 11 numbered service buildings; Hall A 51.6 m vs "174 feet across" |
| ILL | no map | layout to scale | 60 m reactor building and 7 m core cylinder (IGORR 2005) |
| Summit Station | no map | layout to scale | seven RNO-G stations on the "1.25 km" grid (arXiv:2411.12922); skiway 5101 m vs 16,800 ft |
| JUNO | no map | partial, two maps | hall at the published 22°07′05″N 112°31′05″E; eight reactor buildings checked against the GPS-surveyed baselines |
| Chooz, Brokdorf, Leibstadt, Boulby, Soudan, Baksan | partial / marker | richer partial | Soudan MINOS footprint from the 0.7 m survey; Boulby shafts; Leibstadt's earlier map showed the wrong building — corrected |
| Argonne, ISIS, KIT, MIT, Yale, CENPA, McMurdo | no map | partial | sourced buildings and campus at true scale |

**Site points corrected** (each moved because a source showed the old point
wrong): Argonne 4.4 km (a geocoder point near Lemont, outside the campus),
LANSCE 2.8 km (the west tip of TA-53, not the accelerator), La Palma onto CTAO's
published array coordinate, Soudan to its 3 m survey, JUNO to its published
coordinate, Leibstadt 221 m, the two Chooz laboratories from published baselines.

**Dates.** Statuses that had silently gone stale since September were brought to
2026-10-25 from dated sources: the LHC's Run 3 ended 27 June 2026 and the CERN
injectors stopped 31 August (Long Shutdown 3); Fermilab's Main Injector has not
run since July 2024 (PAC report, April 2026); PandaX-4T was decommissioned in May
2026; KATRIN finished neutrino-mass data taking in October 2025; KamLAND and
KamLAND-Zen are in their upgrade; XENONnT is recommissioning; Mu3e's lifecycle
was rebuilt from PSI's news archive. The validator went from 3 errors to 0.

**Pipeline.** Two defects the research streams reported were fixed at the root:
polygon centroids lost up to 532 m to floating-point cancellation (every HAWC
tank was misplaced by a median 107 m; now 0.0 m), and nine more maps pushed
`atlas.json` over its 1.5 MB build cap — bundles are now written compact,
0.98 MB.

## How the experience improved, and why it is better

* A reader who opens **any** facility now gets a to-scale map with a metre scale
  bar. Before, nine facilities had none and Los Alamos opened on an empty map in
  the current year — the worst possible answer to "where is LANSCE?".
* At the observatories the reader now sees the instrument itself — 300 HAWC tanks,
  the H.E.S.S. square with CT5 at its centre, MAGIC beside the four LSTs — instead
  of a single dot. The layout is the science: array spacing sets the energy range.
* Fermilab finally shows the machine that makes its neutrino beams (Main Injector),
  next to the Tevatron and Booster, on its real path.
* Statuses a physicist would notice as wrong ("LHC: active", "PandaX-4T: active")
  are now right as of today, with a dated quote behind each.
* Every new shape says how it was obtained (survey, OpenStreetMap tracing, or a
  stated derivation) and carries a check against an official figure, so the
  honesty the Atlas promises extends to the new maps.

## Verified, and how

* Integrator re-fetched 18 principal sources (papers, lab pages, the Fermilab PAC
  report, CERN news) and matched each quoted figure.
* `scripts/atlas_walkthrough.cjs` opened every changed map in headless Chromium at
  1440×900: every map draws features in 2026, scale bar present, 0 console errors.
* Validator 0 errors; Atlas tests 353 passed.

## Not done yet (carried to the next rounds)

* SNS (Oak Ridge), the APS and ISIS rings, PSI's ring cyclotron, the KATRIN
  beamline — second accelerator pass running.
* CTAO-South: its layout is published only as unscaled figures; stays partial.
* Chooz near lab, JUNO shaft/portal, Baksan tunnel, Boulby lab: no source places
  them.
* Small features vanish at low zoom (JUNO's reactors at 10 km scale) — sent to
  the map-view stream.
