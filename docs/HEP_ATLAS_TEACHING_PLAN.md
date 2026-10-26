# HEP Atlas — development plan: from reference atlas to the thing physicists open in class

2026-10-26. Follows the release (`docs/HEP_ATLAS_RELEASE_REPORT.md`).

## The goal

A physicist opens the Atlas and thinks "this is not just cool — I want to use
it", and an instructor thinks "I can put this in front of my students". Today the
Atlas is a trustworthy reference: every facility on a to-scale map, facts checked
against sources. What it is not yet is *a physics instrument you want to play
with*, or *a lesson you can teach from*. This plan is about those two things,
without giving up what makes it worth trusting.

## Where it stands (walked on production, 2026-10-26)

What works and must not be lost: every fact traces to a source; to-scale maps of
all 48 facilities; honest "not drawn" lists; a timeline; search that answers
real questions; phone layout; three browser engines.

What a physicist sees in the first ten seconds:

* **A database with a globe, not physics.** Flat green land on navy, small
  markers, and a left column that is mostly a legend and ~90 filter checkboxes.
  Nothing on screen says "neutrinos", "beam", "depth", "energy".
* **The physics is in the text, not the picture.** Selecting T2K flies to Japan
  and opens a well-written panel — but the 295 km beam, its 2.5° off-axis angle,
  the 1 km of rock over Super-K are paragraphs and a key-value table. The two
  selected labels overlap. NuMI (MINOS 735 km, NOvA 810 km) has no recorded
  baseline, so it draws no beam at all.
* **No comparison, no story.** Everything is one record at a time. The plots
  every student meets in their first HEP course — energy frontier vs year, muon
  flux vs depth, dark-matter limits, oscillation L/E — are nowhere, although much
  of their data is already in the Atlas.
* **Not built for a classroom.** No guided sequence, no projector-friendly mode,
  no way to export a figure with its scale bar and citation for a slide, no
  embed for a course page.

## Principles (unchanged, and binding on every feature below)

1. **Every mark on screen is traceable.** A drawn beam, a plotted point, a tour
   sentence cites a source; a computed view (a chord through the Earth, an L/E
   position) states its formula and inputs and shows its uncertainty.
2. **Physics-native visuals.** Show beams, depths, energies, scales and
   significances as the objects physicists draw on the board.
3. **Progressive disclosure.** The first view is simple and beautiful; depth is
   one click away; provenance two.
4. **Projector-first legibility.** Readable from the back of a lecture hall.
5. **Fast.** First globe < 2 s on a laptop; a tour step < 1 s; nothing new loads
   until asked.
6. Feature names are working titles; the owner names them.

## Workstreams

### 1. First impression — make the first ten seconds land

* **Landing view with a purpose.** Open on a curated view (the world's long-
  baseline neutrino beams, say) with a small "Start here" card: *Take a tour*,
  *Explore a question*, *Compare*, *Search*. Return visitors skip it.
* **A globe that looks like an instrument.** A stylised dark Earth with subtle
  relief/bathymetry (public-domain NASA/Natural Earth rasters, vendored), a
  thin atmosphere, crisp vector icons per facility kind (ring, mine shaft, dish,
  array, reactor), and markers sized by something meaningful (number of
  experiments) rather than all alike.
* **Beams as first-class objects.** Animated, labelled arcs for every
  long-baseline beam with its baseline ("J-PARC → Super-K, 295 km"). Add the
  missing NuMI baselines (MINOS, NOvA) and T2HK, from sources.
* **A calmer sidebar.** Legend becomes a compact key that opens on demand;
  filters stay grouped and collapsed; the globe gets the space.
* **Visual system.** One type scale with a math-capable face for notation
  (STIX Two for symbols), a status palette that survives colour-blindness and
  projectors, consistent card design for panels, subtle motion (respecting
  reduced motion).

*Accept when:* three persona reviewers (student, instructor, researcher), shown
the landing page cold, can say in one sentence what the Atlas is for and name a
next click; selected labels never overlap; beam arcs exist for every beamline
with a sourced baseline.

### 2. Show the physics — views you cannot get from a list

Each is a separate view, built only from Atlas records, with its inputs listed.

* **Beams through the Earth.** For each long-baseline pair, a cross-section of
  the Earth along the beam: the chord, its dip angle and maximum depth computed
  from the two surveyed coordinates (DUNE's 1285 km beam leaves at about 5.8° below horizontal and reaches
  about 32 km below the surface at mid-path — computed, shown with its inputs), the
  detectors' depths, the off-axis angle where sourced. Linked from every beam arc
  and experiment. *This is the single most "damn" visual the data already
  supports.*
* **Follow the proton.** On a facility's to-scale map, an animated path through
  the injector chain with the energy at each stage (CERN: Linac4 → PSB → PS →
  SPS → LHC; Fermilab: Linac → Booster → Main Injector → NuMI; J-PARC: linac →
  RCS → MR → neutrino line), on the true ring geometry the maps already hold.
  Energies from the accelerator records (add where missing, sourced).
* **Going underground.** All underground laboratories on one chart: depth in
  m.w.e. against measured muon flux, each lab clickable to its map and its
  experiments — the figure every dark-matter and neutrino student learns.
  Needs sourced muon-flux values per lab (a research task).
* **The energy frontier.** Beam energy (or √s) against year for the colliders
  and accelerators in the Atlas, coloured by particle type, built from their
  sourced intervals and specs — a Livingston-style chart whose every point opens
  its record.
* **Scale comparisons.** (a) Put any facility's footprint over any other map —
  or over the reader's own town, using their location in the browser only,
  never stored: "the LHC over Iowa City". (b) A detector line-up at true scale
  (Super-K, IceCube, ATLAS, CMS, a DUNE far-detector module, KATRIN's main
  spectrometer) with a human figure.
* **Results as a story, not a list.** A timeline of results by significance
  (evidence → observation), grouped by question (oscillations, CP violation,
  the Higgs, dark matter), each point opening its paper; later, exclusion plots
  (e.g. WIMP–nucleon cross-section limits) drawn from HEPData tables with each
  curve cited — data-heavy, so after the rest.

*Accept when:* each view states its inputs and formula, every plotted element
opens its record, and a physicist reviewer checking five computed numbers by
hand (chord depth, dip angle, an energy, a flux, a distance) finds them right.

### 3. Teach with it — the instructor's kit

* **Guided tours.** A tour is an authored sequence of steps (camera, timeline
  year, selection, map, one or two sourced sentences, an optional question). A
  player with next/back, progress and a link per step. Launch set, each built
  and fact-checked like the data:
  1. *The neutrino oscillation story* (Homestake → Super-K 1998 → SNO → KamLAND →
     T2K/NOvA → JUNO 2025)
  2. *The W and Z at CERN* (Gargamelle → UA1/UA2 1983)
  3. *The Higgs hunt* (LEP → Tevatron → ATLAS/CMS 2012)
  4. *Going underground for dark matter* (Soudan → LNGS → SNOLAB → SURF/LZ → Jinping)
  5. *Neutrino beams through the Earth* (K2K → CNGS → NuMI → T2K → DUNE)
  6. *How a collider complex works* (follow the proton at CERN)
* **Classroom modes.** Projector mode (light, high-contrast, large type);
  presenter mode (keyboard-driven tour, clicker-friendly); embed mode
  (`?embed=1`, minimal chrome, for course pages and LMS iframes).
* **Take it to a slide.** Export the current globe or map view as PNG/SVG with
  scale bar, north arrow, date, citation and licence footer; print-ready
  one-page facility sheets.
* **Built-in explanations.** A glossary popover for terms the panels use
  (m.w.e., off-axis, CL, σ, baseline, luminosity); a toggle between the plain
  and technical summary the records already carry.
* **Questions.** Optional exercise cards on tour steps ("Estimate the
  neutrino's travel time from J-PARC to Super-K"; "Why is DUNE's far detector
  1.5 km underground?") with worked answers that cite the Atlas's own numbers.

*Accept when:* a reviewer playing an instructor builds a 10-minute lecture
segment from a tour and two exported figures without leaving the Atlas, on a
projector-sized screen, and a reviewer playing a student completes a tour and
its questions on a phone.

### 4. Researchers' daily use

* **Compare** two to four experiments side by side (target mass, baseline,
  depth, energy, status, key results), exportable as CSV with citations.
* **Cite and export**: BibTeX for results and documents (DOIs are in the data);
  CSV/JSON of any filtered list with its sources.
* **HEP Graph × Atlas**: from a person in HEP Graph, their experiments and
  institutions on the globe; from an experiment, a route to its people — only as
  far as the rosters support (partial today, and said so).

### 5. Depth of data (continuous)

* Long-baseline beam records completed (NuMI's MINOS/NOvA baselines, T2HK,
  ESSnuSB if in scope), accelerator energies per stage, muon flux and m.w.e. per
  underground lab — the data the new views need.
* Photographs and official diagrams per facility with licence tracking (CERN,
  Fermilab, KEK and others publish CC-licensed media) — the cheapest "this looks
  real" upgrade, gated on licence metadata per image.
* Continue the unlocated backlog (DUNE near detector, ISIS synchrotron, PSI Ring
  Cyclotron, SNS ring, IceCube Upgrade strings, CTAO-South).
* Raise more experiments to tier A; extend institution rosters.

## Sequencing

| Milestone | Contents | Why first |
| --- | --- | --- |
| **M1 — First impression** (2 rounds) | Landing view + Start-here card, globe visual pass, beam arcs for all beamlines (+ NuMI/T2HK data), calmer sidebar, selected-label fix, visual system | Everything else is judged through it |
| **M2 — Beams through the Earth + Follow the proton** (2 rounds) | The two views the existing data already supports best | Highest "damn" per unit of work |
| **M3 — Tours + classroom modes** (3 rounds) | Tour format and player, the six launch tours, projector/presenter/embed modes, export to slide | Turns the Atlas into a teaching tool |
| **M4 — Charts** (2–3 rounds) | Going underground, energy frontier, scale comparisons, results-as-story | Needs the M5 data tasks in parallel |
| **M5 — Data depth** (in parallel from M1) | Beam baselines, stage energies, muon fluxes, licensed photographs | Feeds M2 and M4 |
| **M6 — Research tools** | Compare, cite/export, HEP Graph × Atlas | After the teaching core is proven |

Same working method as the release: Sonnet streams in worktrees, the
integrator re-checks every sourced number and walks the product, a workup per
round, persona reviews at the end of each milestone, merge and verify on
production.

## How we will know it works

* **Persona reviews** at every milestone (student on a phone, instructor
  preparing a lecture on a projector, researcher checking numbers, outreach
  visitor), judged on: could they say what it is for, did they find the
  physics, did they want to keep going, and were the numbers right.
* **Real use**: the owner shows a tour to a class; the e-mail link collects what
  broke or confused. A lightweight, privacy-respecting count of tour starts and
  completions could be added if the owner wants it (none exists today).
* **Truth checks unchanged**: validator 0 errors, quote checker clean, every
  computed view's inputs listed, browser suites on three engines.

## Not doing (now)

* 3D detector models or VR — heavy, licence-fraught, and not what makes the
  physics legible.
* Anything that invents data for looks (no decorative "example" beams or
  placeholder photos).
* Accounts, comments or user-generated content.

## Decisions for the owner

1. Which milestone first (recommended: M1, then M2).
2. Whether to add a privacy-respecting usage count for tours.
3. Names for the new views and tours (working titles above).
4. Scope of photographs (official media only, or also Wikimedia Commons with
   licence tracking).
