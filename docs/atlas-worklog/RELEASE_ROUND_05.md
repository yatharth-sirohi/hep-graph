# Release round 5 — panels, search and filters a reader can use; three hidden bugs

Integration branch `atlas-release`, 2026-10-25. One Sonnet frontend stream
(panels, search, filters) was merged; running the full browser and
accessibility suites on the merged build then exposed three real bugs, which the
integrator fixed at the root.

## What changed

**Search** — typing "Fermilab" and pressing Enter now opens Fermilab. The first
option is active as the list appears (a highlighted row, `aria-activedescendant`),
arrows move, Escape closes the list (and no longer also closes the open record).

**Record panels**

* Key specifications no longer wrap one character per line: DUNE's values had
  28 px of width in the 340 px panel ("128 / 5 / km"); labels now sit above
  values, 307 px wide, and a figure never splits from its unit.
* Sections the Atlas has nothing for are not drawn as empty headings. The panel
  ends with one honest line — "None recorded in the Atlas: Historical
  experiments, Documents. Coverage is partial, so this is not evidence that none
  exist" — linked to the coverage report. All 787 entity panels were opened at
  desktop and phone width: 0 empty headings, 0 bare "None", 0 console errors.
* 119 of 122 collaborations have no curated roster; their panels used to request
  a roster file that does not exist (a 404 per open). The manifest is consulted
  first; a roster that exists but fails to load now shows as an error, not as
  "not curated".

**Filters** — every group is collapsible; "Research topic" and "Experiment kind"
(the long ones) start closed and show "3 selected" on their header; "Clear all
filters" appears while any filter is active.

**Results and Documents** — "Move timeline here" used to rebuild the whole list,
throwing away its scroll, filters and focus; the list now keeps its place.

**Three bugs found by running the suites on the merged build**

1. *Ended structures drawn as present.* A shape whose validity window had an end
   but no start (the Tevatron ring, the CDF and D0 halls, the CONUS detector at
   Brokdorf) was built with no timeline at all — drawn in every year, so the
   Tevatron appeared on the 2026 map of Fermilab. An open start now means "as far
   back as the entity goes"; the Tevatron ring runs 1985–2011, and selecting it
   in 2026 draws it ghosted with the notice "no longer there in 2026". Guarded by
   a data test.
2. *Motion despite "reduce motion".* Globe.gl's start-up animation scaled and
   spun the globe for about a second, gliding markers ~110 px even for a reader
   whose system asks for reduced motion (this predates the release — `main` does
   it too). It is now off for those readers.
3. *A closed filter group re-opened itself* when another filter was ticked right
   after closing it (the browser reports the close asynchronously).

## How the experience improved, and why it is better

* Search behaves like every search box a reader has used: type, Enter, done.
* A panel says what the Atlas knows and states plainly what it does not, instead
  of a column of empty headings that read as "nothing exists".
* The filter list fits on a screen; a reader can see at a glance what is
  filtering the globe.
* The map no longer shows a collider that shut down in 2011 as part of today's
  Fermilab — the kind of quiet error that undermines trust in everything else.
* Readers with vestibular sensitivity get a still globe from the first frame.

## Verified, and how

* `tests/browser_atlas.cjs`: 79/79 on the real build (real GPU, 60 fps with
  institution dots). `tests/browser_atlas_a11y.cjs`: 35/35, 0 axe violations
  over 24 states.
* Integrator traced the reduced-motion glide frame by frame (camera fixed,
  canvas fixed, marker easing 664 → 551 px) to `animateIn`, and confirmed the
  marker is still from its first frame after the fix.
* Four test assertions that raced the app (reading a section before its toggle
  handler ran; clicking where two rings touch) were made to wait on observable
  state; the Sources disclosure now exposes `data-state` for that.
* Validator 0 errors; Atlas tests 353 passed.

## Not done yet

* Institution dots blink out for ~0.4 s while the camera flies to a collaboration
  (cosmetic).
* Findings of the independent newcomer review (running) are the next round.
