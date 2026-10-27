# M3 — Teach with it: tours, classroom modes, export, explanations

Integration branch `atlas-next`, 2026-10-26. Four implementation and data streams,
plus integrator checks.

## What changed

### Guided tours (data, amendment A28) and the tour player

- **The format.** A tour is a sequence of steps. Each step has a camera, a year, a
  selection, a map or view, one or two plain sentences and an optional question.
  The validator checks that:
  - every sentence and every number is covered by a verbatim quote or by an Atlas
    field that is already sourced;
  - every referenced record exists in the step's year;
  - every worked answer's arithmetic comes out right.
- **Six launch tours** (working titles):
  - the neutrino oscillation story;
  - the W and Z at CERN, which brought in Gargamelle and its 1973 neutral-current
    result;
  - the Higgs hunt;
  - going underground for dark matter;
  - neutrino beams through the Earth, whose steps open the beam-section view;
  - how a collider complex works.
- **The player.**
  - `#/tour/<slug>?step=N` keeps one history entry per step.
  - A card shows progress, the text, its sources, and the questions with "Show
    answer".
  - On a phone it is a bottom sheet with a "Hide text" fold.
  - Readers reach tours from the Tours list in the header, a "Follow a guided
    tour" row on the Start-here card, topic panels and search.
- **Presenter mode** (`?present=1`): large type. The arrows, Page Up/Down and Space
  move between steps, which is what clickers send. B blanks the screen, A shows the
  answer, and Escape leaves.

The integrator checked the questions' arithmetic by hand:
- 295 km / c ≈ 0.98 ms;
- the 0.82σ difference between the ATLAS and CMS Higgs masses;
- 1/1.7×10⁻⁹ ≈ 590 million;
- 3600 kg of argon in an 85 cm sphere ≈ 1400 kg/m³;
- the dip of a straight chord to Soudan, 57.7 mrad against NuMI's published
  58 mrad;
- the CERN energy factors 12.5, 13, 17 and 15.

Four claims were re-read against their sources:
- LZ's exposure is "about 550 times" that of LUX's first run, which is the run the
  question names;
- K2K's 1.5 GeV average energy is on KEK's own page;
- the 2011 Higgs hints of 2.9σ and 3.1σ are quoted from ATLAS's 2012 paper;
- the injectors' Long Shutdown 3 date comes from a sourced record.

### Classroom modes

- **Projector mode** (`?theme=projector`, header toggle): a light theme with high
  contrast, 1.25× type, and thicker beams and keylines. It has 0 axe violations
  and body text at ≥ 7:1 contrast.
- **Embed mode** (`?embed=1`): minimal chrome, plus an "Open in HEP Atlas" link to
  the same view. The server allows framing for `/atlas` only; the HEP Graph app and
  the whole API keep `frame-ancestors 'none'`. A test pins that split.

### Built-in explanations

- **Glossary:** 29 terms, among them m.w.e., off-axis angle, baseline, CL, σ, √s,
  fiducial mass, TPC, WIMP, CEvNS and 0νββ. Each definition carries a quote from
  the PDG 2026 reviews or CERN. The first use of a term in a panel opens a popover
  with the definition, its source and the source's own words.
- **Plain/technical toggle:** every summary can switch between the plain and the
  technical version, and the choice is remembered.

### Take it to a slide

- **Export image:** the globe or a local map as a PNG, at 1920×1080 or twice the
  stage size. It carries the title, the year and a citation footer; maps add a
  metre scale bar and a north arrow. OpenStreetMap tiles are drawn (their server
  allows it); if a canvas would be tainted, the export says so and leaves the
  tiles out.
- **Facility sheet:** one printable page per facility, with the summary, key
  specifications, experiments by year, a to-scale map snapshot and the sources.
  All 48 original facilities fit on one page.

## How the experience improved, and why it is better

Before M3 the Atlas was something you explored on your own. Now an instructor can
open a sourced, fact-checked tour on the projector and step through it with a
clicker. They can pull an exported slide with a scale bar and a citation into
their own lecture, embed a view on a course page, and hand students a printed
facility sheet. A student meets "m.w.e." or "σ" with its definition one tap away,
sourced to the PDG.

## Verified, and how

- The integrator looked at the exported T2K slide, CERN's map slide and SURF's
  printed sheet, and checked projector mode and the glossary popover in a browser.
- During integration a projector-mode overlap in the glossary title was fixed, and
  so was the Key popover's keyboard order with the new header buttons.
- The streams' checks: tours played to the end on three engines; the export and
  print checks; the iframe embed; accessibility with 0 violations.
