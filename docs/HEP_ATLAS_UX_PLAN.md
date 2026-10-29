# HEP Atlas: a calmer first experience

2026-10-29. The content is solid; the interface puts too much in front of a
newcomer at once. This plan changes how things are presented, never what is
there.

## Where it stands

The Atlas covers 413 experiments, 101 facilities, 523 results, 50 to-scale
local maps, 6 guided tours, and a set of physics views: the beam through the
Earth, going underground, the energy frontier, results as a story, the WIMP
limits, and the detector line-up. Every fact is sourced.

What a first-time visitor meets (walked through on production, 1440×900 and
phone):

- **The header has ten controls** (five tabs, search, Key, Filters, Projector,
  Export image). None says what it does until it is clicked. "Key" and
  "Filters" give no hint that they are about the globe.
- **Two bars sit at the bottom.**
  - The timeline: "Single date", "Range", "Play", "1×", a slider and the year.
    Nothing says the slider is the year the globe shows.
  - The footer opens with `Atlas data version 0b0d250cf3575fc6 · coverage
    updated …`, a hash a reader cannot use.
- **Record panels open on controls, not on the answer.**
  - On DUNE: the title, a type, a status pill, the collaboration, "See the
    physics", "Add to compare" and a "Summary Plain/Technical" switch all come
    before one sentence says what DUNE is.
  - The panel is about 2,100 px tall, with ten sections.
  - On CERN, the summary is followed by a block of aliases, the operator and
    the country before the experiments.
  - On a result, the answer (what was found, how significant) sits below a
    paper title, a same-day note and a quoted abstract.
- **The Results list opens on 523 rows, newest first.** The top of the list
  is 2026 technical papers ("Upgraded NaI(Tl) Crystal Encapsulation for
  COSINE-100U"). Above them are five filter menus, a sort menu, two group
  buttons and two download buttons, and every row has a "Move timeline here"
  button.
  - The type tags ("Limit", "Evidence", "Anomaly") are physics jargon with no
    explanation.
- **The Filters drawer has two status lists.** "Active / completed / planned"
  and a twelve-option "Experiment status" sit one above the other, with more
  than forty checkboxes in all, open at once.
- **The Key is complete but dense.** It has five unlabelled-looking groups of
  about 25 entries.

## Principles

1. **Nothing is removed.** Every fact, link, control and caveat stays one
   click or one hover away. Changes are to order, grouping, wording and what
   is open by default.
2. **Answer first, then go deeper.** Every panel opens on what the thing is,
   where it is, its status, and why it matters. Specifications, lists,
   documents and sources follow, collapsed, each saying how many items it
   holds.
3. **Every control says what it does,** in its label or in a tooltip, in
   plain words.
4. **One way to do one thing.** Related actions sit together, and duplicate
   paths are grouped under one heading.
5. **Teach as you go.** Jargon a newcomer meets in a label ("Limit",
   "Evidence", "Commissioning") carries a one-line meaning.

## The changes

### 1. Orientation
- **Start here card.** Adds a short "How to use the Atlas" block: what a symbol
  is, how to open one, what the year slider does, and where the Key and
  Filters are. The tour and the four questions stay.
- **Header.**
  - Every tab and tool gets a plain tooltip ("Topics: browse by physics
    question", "Filters: show only some places on the globe").
  - "Key" becomes "Map key". "Export image" becomes "Save image".
  - A "Help" button reopens Start here, so it is not only in the footer.
- **Timeline.**
  - A visible label: "Year on the globe".
  - Tooltips on "Single date", "Range", "Play" and the speed button.
- **Footer.** The first line becomes plain counts and the coverage caveat
  ("413 experiments · 101 facilities · 523 results — partial coverage, see the
  coverage report"). The data version and update date stay at its end, in
  smaller type.

### 2. Record panels (experiment, facility, result, and the rest)
- **The lede comes first.** Title, then type and status on one line, then the
  plain summary, then the actions.
- **One "Explore" row of clearly labelled actions:** beam through the Earth,
  local map, charts, compare, print sheet. It replaces the loose lines
  scattered above the summary.
- **"Summary: Plain / Technical"** becomes **"Reading level: Simple /
  Technical"**, with a tooltip.
- **Section headings carry counts:** "Detectors (5)", "Results (12)",
  "Sources".
- **Long secondary lists are collapsed by default.** These are the detectors,
  the local map list, and a facility's aliases, operator and country (as an
  "At a glance" list).
- **On a result,** the answer is pulled up:
  - the plain summary and a highlighted "What was found" box (significance and
    key value) sit right under the title;
  - "Where", "Same day" and the paper title follow as smaller context lines;
  - the abstract excerpt follows those.
- **The closing "None recorded in the Atlas…" line** stays, styled as a quiet
  footnote.

### 3. Results list
- **A new default order, "Landmarks first".**
  - Discoveries and first detections come first, then observations and
    evidence, then measurements, limits and milestones.
  - Each band is headed and newest-first within it, and all 523 results are
    still listed.
  - "Date (newest first)" and the other orders stay in the sort menu.
- **The filter, sort and group controls fold into one "Filter and sort"
  disclosure,** closed by default on every screen. Its summary says what is in
  force.
- **"Move timeline here" becomes a quieter "Show [year] on globe" link.**
- **Result-type tags carry a plain meaning on hover and focus,** and a short
  legend of the types sits above the list.

### 4. Filters drawer
- **A one-line explanation at the top:** "Show only some places on the globe.
  The numbers are how many experiments match."
- **The simple status group stays open.** The twelve-option detailed status
  is collapsed under "Detailed status", and the remaining groups are collapsed
  with their counts in the heading.

### 5. Map key
- **One plain sentence opens each group:** "Shape: what kind of place",
  "Colour: its status in the year shown", "Rings and numbers: places close
  together", "Lines: particle beams".

## Out of scope for this pass
- New content, data changes, or a new visual identity.
- Re-architecting the views (beam section, charts). They already lead with
  a headline.
- The phone sheet structure. It already folds the header into "Views &
  filters", and it inherits the panel and list changes.

## Done when
- A newcomer can open the Atlas and, without guessing, say what the symbols,
  the slider, the Key and the Filters do.
- A newcomer can open DUNE, CERN or the Higgs result and read what it is
  before any control.
- A newcomer can open Results and see the landmarks first.
- Every fact that was on a panel is still there.
- The change is on `main` and live on production.

## What shipped (2026-10-29)

Every item above shipped, plus the Topics list. No record content was changed or
removed.

- **Orientation.**
  - Start here has a "How to use the Atlas" block in a two-column card that
    fits a laptop screen without scrolling.
  - The header has a Help button, "Map key" and "Save image", and every tab and
    tool has a tooltip.
  - The timeline is captioned "Year on the globe", and its controls have
    tooltips.
  - The footer reads "413 experiments · 101 facilities · 523 results — partial
    coverage…", with the data version at its end.
- **Record panels** (`panels.js` `arrangePanel`, all eleven record types and
  the local map's drawer).
  - The order is: the name; kind and status on one line; "Reading level:
    Plain / Technical" (`summary.js`); the summary; who runs it; one "Explore"
    box of links; then the sections.
  - A facility's Overview is now "At a glance". Sections that are lists show
    their length.
  - An experiment's detectors and the local-map list are closed by default.
  - The record panel is 400 px wide on screens 1280 px and wider.
  - A result opens on its summary and a "What was found" box (significance,
    key value, date). Where, the same-day papers, the paper title and the
    abstract follow.
- **Results list** (`modes.js`, `result-types.js`, `state.js`).
  - The default order is "Landmarks first", in three headed bands: discoveries
    and first detections (15); observations, evidence and anomalies (109);
    measurements, limits and milestones.
  - "Date (newest first)" and the other orders are still in the sort menu.
  - "Filter, sort and download" is one closed disclosure.
  - "What the result types mean" explains each type, and each type tag has the
    same text on hover.
  - "Move timeline here" is now "Show 2012 on globe".
- **Filters.**
  - A sentence opens the drawer.
  - The groups have plain names: "Running, finished or planned", "Detailed
    status", "Physics topic", "Kind of place", "Kind of experiment", "Region".
  - Only the first and the regions are open, and every heading shows how many
    choices it holds.
- **Map key.** A sentence opens it, and the group headings say what each group
  shows ("Shape: what kind of place", "Colour: status in 2026", "Lines:
  particle beams").
- **Topics.** Each field of physics is a heading with its question underneath
  ("Dark matter: What is the invisible matter that dominates the mass of
  galaxies…").
