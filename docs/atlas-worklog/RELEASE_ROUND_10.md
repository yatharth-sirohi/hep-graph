# Release round 10 — merged to main, live on production, checked on the live site

2026-10-25 (US Central evening; production clock 2026-10-26 UTC).

## What changed

* PR #3 (`atlas-release` → `main`) merged as `1679922`; Vercel deployed it to
  production within about 30 s (`/api/health` → `git_commit` 1679922…, region
  cle1, environment production).
* Two last fixes found on the live site, shipped as a follow-up to `main`:
  * the phone timeline's year wrapped onto its own line once the speed button
    was added; the slider now gives way first, so the year stays on the row from
    360 px up (measured at 320/360/375/390/414 px, no horizontal overflow);
  * a browser check read the topic highlight mid-flight on production's slower
    start; it now reads the settled globe (the Atlas itself was correct: 5 lit,
    the rest muted).

## Verified on the live site (https://hep-graph.vercel.app/atlas)

| Check | Result |
| --- | --- |
| Production commit | `/api/health` reports the merge commit |
| CDN | `/atlas/js/app.js`: first request `x-vercel-cache: MISS`, then `HIT`; browsers still see `Cache-Control: public, max-age=0, must-revalidate`; the CDN-only header is not exposed |
| Browser suite against production (Chrome) | 95 of 95 applicable checks pass (the 96th maps a fake host to a local server and can only run locally, where it passes) |
| All 50 local maps on production | 50/50 draw, scale bar present, 0 console errors |
| HEP Graph unaffected | `/api/path` Feynman → Wheeler settles exact, 1 hop |
| Human walkthrough (integrator, browser pane) | topic highlight and fly-to (neutrino oscillations → East Asia), DUNE on a phone (SURF, Fermilab, CERN ringed), SURF map with the DUNE caverns and hollow uncertainty rings |

## How the experience improved, and why it is better

Readers now get, at hep-graph.vercel.app/atlas, everything rounds 1–9 built —
every facility on a to-scale map, a globe that follows them, and facts that match
their sources — served from the CDN instead of a serverless call per file.

## Left for the owner

* "Report an error" points at the private GitHub repository (404 for the public).
* Known cosmetic: markers blink out for about 0.4 s while the camera flies to a
  selection (the globe library rebuilds its marker layer).
* Shapes no public source places stay listed per map as "not drawn", with the
  reason (DUNE near detector, ISIS synchrotron, PSI Ring Cyclotron, SNS ring,
  IceCube Upgrade strings, CTAO-South, …).
