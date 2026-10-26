# HEP Atlas — release report (2026-10)

Branch `atlas-release` (from `main` 1a475e7), merged to `main` at the end of the
release. Plan: `docs/HEP_ATLAS_RELEASE_PLAN.md`. Round-by-round workups:
`docs/atlas-worklog/RELEASE_ROUND_01.md` … `RELEASE_ROUND_10.md`.

## What a reader gets

* **Every facility opens a to-scale map.** 48 facilities, 50 maps (JUNO and
  KM3NeT have two). Before: 39 maps for 38 facilities, nine facilities with none,
  Los Alamos empty in the current year. Each map shows what public sources
  support at true scale, with a metre scale bar, a north arrow, names on the
  shapes, and a plain list of what it does not draw and why.
* **Instruments, not dots.** IceCube's 86 strings, Auger's ~1,600 surface
  stations, Telescope Array's 507, LHAASO's detector arrays and pools, HAWC's 300
  tanks, the H.E.S.S., VERITAS, MAGIC and LST telescopes, Baikal-GVD's clusters,
  DUNE's far-detector caverns, Fermilab's NuMI line, CEBAF's racetrack, the APS
  ring, KATRIN's beamline.
* **A globe that behaves.** It fills the screen, flies to and rings what you
  select, keeps labels apart, shows country borders, highlights a topic's
  experiments, respects "reduce motion", and works on phones and tablets as
  bottom sheets.
* **Facts that hold up.** Every quote was machine-checked against its fetched
  source and every result's paraphrase audited against its quote; statuses are
  current to 2026-10-25.

## Numbers

| | `main` | release |
| --- | ---: | ---: |
| Facilities with a local map | 38 of 48 | 48 of 48 |
| Local maps | 39 | 50 |
| Geometry records | 174 | 368 (surveyed 42, georeferenced 219, derived 101, inferred direction 6) |
| Sources | 1,606 | 1,903 |
| Quotes found verbatim in their source | 2,595 of 3,829 checked | 3,682 + 319 joined segments of 4,206; 3 near-misses and 1 not found (each explained), 6 unreachable sources, 195 skipped by rule (INSPIRE, geocoders) |
| Validator errors | 3 (stale Mu3e status) | 0 |
| Results audited against their quotes | — | 109 of 109 |
| Browser checks (real build) | 76, Chromium only | 96 Chrome / 95 Firefox / 95 WebKit |
| Accessibility checks | 30 | 35, 0 axe violations |

## How it was built and checked

* Implementation and research by Sonnet subagents in their own worktrees (about
  30 streams); the integrator re-read the sources behind every principal shape,
  date and value change it merged (each workup lists what was re-checked), and
  walked the built product in a browser at desktop, tablet and phone sizes.
* Two independent Sonnet reviewers, who had not built the Atlas, used it as
  readers would (a PhD student, a theorist, a journalist on a phone, a sceptic
  checking sources, an explorer). The first found a wrong physics claim (T2K's
  CP result said 0 and ±π were excluded; the cited interval contains −π), the
  second confirmed 17 oscillation headlines against their abstracts and found
  the remaining presentation problems fixed in round 8.
* Unit tests were added only where a regression would be silent (small-polygon
  centroids; shapes with an end date but no start).

## Bugs fixed that predate this release

* Small polygons lost their centroid to floating-point cancellation (HAWC tanks
  by a median 107 m).
* A shape's validity window with an end but no start made it timeless — the
  Tevatron ring and the CDF and D0 halls were drawn on today's map.
* Results and Documents lists could not scroll on desktop.
* Globe.gl's start-up animation ran for readers who asked for reduced motion.
* Every Atlas file was a serverless invocation (no CDN caching).

## Known gaps (stated in the Atlas itself)

* Shapes no public source places stay in each map's "not drawn" list (DUNE near
  detector and LBNF target hall, ISIS synchrotron, PSI Ring Cyclotron, SNS ring,
  IceCube Upgrade strings, CTAO-South's layout, and others — 40-odd entries,
  each with its reason).
* Coverage of experiments is partial by design (131 researched); the coverage
  report says so.
* "Report an error" links to the GitHub repository, which is private.

## Deployment

`static/atlas/generated/` is committed; no build step runs on Vercel. Atlas
files are served by the Python function with `Cache-Control: public,
max-age=0, must-revalidate` for browsers and `Vercel-CDN-Cache-Control:
max-age=86400, stale-while-revalidate=604800` for Vercel's edge cache, which a
deployment empties.

**Verified on production (2026-10-26 UTC):** `main` 1679922 live within ~30 s;
CDN `MISS` → `HIT` on Atlas files; browser suite 95/95 applicable checks against
the live site; all 50 local maps render with 0 console errors; HEP Graph's route
search unaffected. Details: `docs/atlas-worklog/RELEASE_ROUND_10.md`.
