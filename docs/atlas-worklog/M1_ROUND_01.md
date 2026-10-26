# M1 round 1: first impression (data, interface, globe)

Integration branch `atlas-m1` (from `main` 6182106), 2026-10-26. Plan:
`docs/HEP_ATLAS_TEACHING_PLAN.md`, workstream 1. Three Sonnet streams worked in
their own worktrees (data, interface, globe); the integrator re-read the sources
behind every new number, walked each branch in a browser at 1440, 1024 and 375 px,
and merged.

## What changed

### Beams for every long-baseline beamline (data stream)

Seven beam arcs now have a sourced baseline. Before this round, NuMI had none, so
MINOS and NOvA drew no beam at all, and K2K had none either.

| Beam | Baseline | Source the integrator re-read |
| --- | --- | --- |
| NuMI → Soudan (MINOS) | 735.3 km | MINOS detector paper (arXiv:0805.3170): "735.3 km from the NuMI beam production target at Fermilab" |
| NuMI → Ash River (NOvA) | ~810 km | NOvA PRD 2022 (arXiv:2108.08219): "∼810 km from the source"; "centered 14.6 mrad off the beam axis" |
| KEK → Super-K (K2K) | 250 km | KEK K2K FAQ: "emerges at Super-Kamiokande, 250 km away" |
| J-PARC → Super-K (T2K) | 295 km | unchanged |
| J-PARC → Hyper-K (T2HK) | about 295 km, *under construction* | Hyper-K design report (arXiv:1805.04163): "about 295 km away from the J-PARC proton accelerator research complex"; cavern status (arXiv:2602.14810): "The excavation of the Hyper-Kamiokande cavern, 600 m underground, is complete." |
| CERN → Gran Sasso (CNGS) | 732 km | unchanged value; row completed with its sources |
| Fermilab → SURF (LBNF/DUNE) | 1285 km | unchanged |

Each distance passes the A21 check against the great-circle distance between the
two recorded sites (agreement within 0.01–0.3 %). Near detectors that share
Fermilab's campus point (MINOS ND, NOvA ND, SBND, MicroBooNE, ICARUS) get no arc,
because a beam from a point to itself would be 0 m long. Their sourced distances are
kept in notes. Full log: `M1_BASELINES.md`.

### A calmer interface and a visual system (interface stream)

* **The sidebar is gone.** It was 220 px of a view list, a legend and about 90
  checkboxes. The view switcher (Globe, Topics, Results, Documents) is now in the
  header. The legend is a **Key** popover that also holds the status colours.
  **Filters** is a drawer that shows how many filters are active. The globe gets
  the full width.
* **Start here.** A first visit to a bare `/atlas` opens a card that says what the
  Atlas is in one line and offers four questions, each a real deep link:
  * where DUNE's far detector is;
  * where the Higgs was discovered;
  * which experiments study neutrino oscillations;
  * how deep the underground labs are.

  It also offers Results, Search and the globe. Dismissing it is remembered. Shared
  links never show it. "Start here" in the footer reopens it.
* **One visual system.**
  * Type and colour: vendored Inter for the interface and STIX Two Math for
    notation (ν̄, θ₁₃, ±, √s); one type scale (12–32 px); spacing, radius and
    motion tokens.
  * Status colours: an Okabe–Ito palette that stays distinct under the three
    common colour-vision deficiencies and on a washed-out projector. A test
    computes the contrast and colour-blindness distances from the CSS itself.
  * Panels: every panel section is the same card.
* **Phone.** The same controls live in the "Views & filters" sheet. The
  integrator made the Start-here card a sheet that shrinks the globe to the strip
  above it, so the globe stays in view instead of hidden behind it.

### The globe (globe stream)

* **An Earth that looks like an instrument.** The image is Natural Earth's public-domain
  "Gray Earth with Shaded Relief, Hypsography, and Ocean Bottom". It is recoloured
  to slate land on a navy sea floor and encoded as a 4096 × 2048 WebP of 333 KB;
  the recipe is in `scripts/atlas_earth_texture.py` and `vendor/README.md`.
  * The first frame is painted in the image's own colours, so there is no flash of
    the old green land. The same colours are the fallback if the image fails.
  * Borders, coastlines and a thin teal atmosphere stay.
* **Icons that say what a facility is.** There is one glyph per kind, and the Key
  draws the very same SVGs:
  * a ring for accelerator labs;
  * a cavern for underground labs;
  * a detector module for neutrino observatories;
  * a dish for astroparticle sites;
  * a snowflake for polar stations;
  * a cooling tower for reactors;
  * a flask for research labs;
  * a starburst for spallation sources;
  * a telescope for astronomical observatories, added for the coverage wave.

  Marker size grows with the square root of the number of experiments (19–38 px).
  Hatching (uncertain), dashed outlines (approximate location), hollow
  (uncounted) and the selection ring keep their meaning. A pale keyline holds
  each glyph at ≥ 3:1 against the relief, including under a projector-style
  gamma lift.
* **Beams.** Every recorded baseline draws a labelled arc at mid-path, e.g.
  "J-PARC → Super-K · 295 km", with the distance formatted from the record.
  * A running beam flows; reduced motion makes it static.
  * A beam that is under construction (T2HK) or has ended is drawn quieter and
    dotted, with its status in the label.
  * T2K and T2HK share both ends, so the second arc rides higher and their labels
    stack.
  * Clicking an arc opens its beamline. Selecting a beamline or an experiment
    frames the whole baseline.
* **Selected labels never overlap.** Each selected caption takes the first free
  place around its halo, with a leader line when it has moved. T2K, for example,
  shows three rings, three captions and two beam labels with no overlap on
  desktop and phone. All captions are at least 12 px.
* **Framing.** `showView(view, {clearOf})` frames the landing view in the part of
  the stage the Start-here card leaves free: right of the card on a laptop, and
  the strip above it on a phone.
* **Measured:**
  * markers visible 540–573 ms after navigation (Chrome, 5 cold loads);
  * idle rotation at 60 fps;
  * 0 console errors.

## How the experience improved, and why it is better

The first thing a reader saw used to be a narrow globe beside a wall of checkboxes,
with nothing on screen saying what the Atlas was for. Now the globe fills the
window and a short card says what it is, with four concrete physics questions one
click away. All the controls are still there, one click away in the header.
The globe now looks like a physical object, with relief, sea floor and icons that
say "ring", "cavern", "reactor". Neutrino beams are drawn as labelled lines with
their distances, which used to be paragraphs in a side panel. A student who
selects T2K sees the 295 km beam from Tokai to Kamioka with every label
readable. This is the picture the M2 views build on.

## Verified, and how

* Integrator re-read every new baseline's source today (table above).
* Integrator walk of the merged interface at 1440, 1024 and 375 px:
  * Start-here card: all four questions work (DUNE flies to Fermilab and SURF and
    opens its panel).
  * The Key popover and Filters drawer open and close.
  * The phone sheet works.
* Interface stream suites on its branch: Chrome 100/100, Firefox 99/99, WebKit
  99/99, accessibility 38/38, pytest 689 passed.
* Merged build (`atlas-m1` af8c9e1 and later): Chrome 100/100, Firefox 99/99,
  WebKit 99/99, accessibility 38/38 with 0 axe violations over 27 states, pytest
  689 passed, validator 0 errors.
* WebKit first stopped after 70 checks, twice, with a page load timing out. The
  globe branch alone passed (99/99), and so did the merged build against a fresh
  server. The cause was the long-running local preview server, which had stopped
  answering a later connection. Vercel does not run that server.
