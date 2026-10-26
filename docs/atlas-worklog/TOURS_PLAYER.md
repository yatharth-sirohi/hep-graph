# Tour player and presenter mode (owner tag: `tours-player`, branch `atlas-m3-player`)

2026-10-26. Workstream 3 of `docs/HEP_ATLAS_TEACHING_PLAN.md`, the player half: it plays the
tours of `docs/atlas-worklog/TOURS.md` (A28, `tours.json`). Feature names are working titles.

## What it is

* **Route.** `#/tour/<slug>?step=<n>` (1-based). `#/view/tour/<slug>` and a query typed inside the
  hash (`#/tour/<slug>?step=3`) read as the same route; the address is rewritten to
  `?step=3#/tour/<slug>`. The address holds only the tour and the step (and `y=`, which the step
  sets): each step supplies its own year, selection, local map or view, so reload, a pasted link,
  Back and Forward land on the same picture. One history entry per step. A step past the end or
  before the start is clamped; an unknown tour says so, listing the tours that exist.
* **Applying a step** (`js/tours.js`, `js/tour-data.js`). The player reads the build's `href`
  (a view beats a map beats a selection) and hands app.js a state with the tour route swapped for
  the step's route (`resolve`), so the selection beside the globe, the local map and the beam
  section are drawn by the code that already draws them. The step's year goes onto the timeline
  and the globe; the globe flies with `showView(camera, { clearOf: card })` (a jump under
  reduced motion). The record opens in the right-hand column beside the card, not under it.
  Local maps and views take the whole stage, so the stage gives the card its column
  (`#atlas-main.has-tour { padding-left }`) rather than a card over a to-scale map.
* **Card.** Tour title, "Step N of M" with a progress bar (`role=progressbar`) and the step's
  year, the step title, the text with every phrase a claim covers marked (dotted underline; TeX
  through `tex.js`), a "Sources (n)" disclosure (loads `sources.json` only when opened; each
  claim's quote, its place in the source, its confidence, its sources, and for a reference the
  Atlas field it leans on), the question with "Show answer" (the worked answer, "How it was
  worked out" and "Sources for the answer"), and Back / Next ("Finish" on the last step).
  Exit (×) and Finish return to the globe. Focus: the card on arrival, then Next keeps it, so
  Next, Next, Next works from the keyboard. A polite status line announces each step.
* **Presenter mode** (`?present=1`, or the card's "Present"). Large type (`clamp`ed 22–32 px
  text), a wider card, the key list. Arrow Right/Left, Page Down/Up and Space (Shift+Space back)
  step; Home/End jump; B blanks (W whitens), any key restores without acting; A, Enter or
  Arrow Down shows the answer, Arrow Up hides it. Escape leaves presenter mode, then closes the
  record, then leaves the tour. The record stays closed unless the step selects something (every
  launch step does). Nothing in `tours.css` sets a colour except the blank screen, so a theme
  that redefines the tokens (`?theme=projector`) restyles the card and its type.
* **Entry points.** A "Tours" button in the header view switcher (hidden when the build has no
  `tours.json`) opens a list: name, length, summary, the steps, "Start the tour", "Present it".
  The Start-here card leads with a "Take a tour" row that opens the list. A topic panel lists the
  tours with a step about it ("3 of 8 steps"; a step covers a topic when it selects the topic or
  a record filed under it or below it), each opening at the first such step. Search finds a tour
  by its name and by the words of its summary (`search.json` gains a `tour` row per tour; the
  build, not the browser, writes it).
* **Phone (≤ 900 px).** The card is a bottom sheet (`phone.js` lists it so the globe shrinks to
  the strip above it); the head folds into the title row; "Present" is not offered. A phone shows
  one sheet at a time, so the record is not opened beside the card: "Open the record for X" opens
  it and the card yields; the sheet's own close brings the card back.
* **Leaving.** The record's × closes only the record. Following a link out of the record, picking
  a marker, searching or any header button leaves the tour; a "Resume tour: … · step n of m"
  pill brings it back at the same step (Exit and Finish do not leave one).

## Changes outside the player

* `state.js`: the `tour` route, `?step=` and `?present=` (written only on a tour route; leaving a
  tour forgets both; opening another tour starts at step 1), a query typed inside the hash.
* `app.js`: `applyState` resolves a tour route first; the globe and filter panel now also follow a
  timeline position that arrives with the address (Back/Forward, a step's year), not only the
  slider (`applyTimelineToGlobe`).
* `panels.js`: `render(route, ts, { focus })`; a render ticket so a slow earlier record never
  lands over a later one (Next pressed twice); the topic panel's tours section.
* `loader.js` `getTours()` (lazy; `null` when the manifest does not list `tours.json`).
* `build.py`: one `tour` search row per tour. `searchrank.js`: `tour` sorts after `topic`.
* `modes.js` (`tours` mode), `start.js`, `phone.js`, `provenance.js` (`renderEvidenceItem`),
  `index.html`, `atlas.css` / `views.css` (the full-stage rules leave the card alone),
  `tours.css` (new, linked between `views.css` and `phone.css`).

## Checks

* `tests/test_atlas_tour_player.py` (Node, on the real tours): every step's href reads back as its
  own fields; sentences cut at covered phrases join back exactly; `?step=` clamps and every route
  spelling reads the same; the address round-trips and forgets step and presenter flag on leaving;
  a topic lists its tours; field labels; a worked line shows its own value; wiring.
* `tests/browser_atlas.cjs`, the `Tours:` checks (generated tree; `HEP_ONLY=^Tours` runs only
  them): all six tours played to Finish with the keyboard, asserting each step's year, address and
  route; `?step=` round trip with Back/Forward/reload/clamp/aliases; a question and its Sources;
  presenter keys; entry points and lazy loading of `tours.json`; the resume pill, the record's ×
  and the camera clearing the card; the phone sheet.

## Playthrough (six tours, 1440 px and 390 px)

See the final report and "For the integrator" below.

## For the integrator

* (filled in after the playthrough)
