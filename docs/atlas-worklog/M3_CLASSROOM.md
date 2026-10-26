# M3 classroom: projector mode, embed mode, glossary, plain/technical toggle

Branch `atlas-m3-classroom` (worktree `HEP-Graph-ar-m3-classroom`), 2026-10-26.

## Scope

1. Projector mode (`static/atlas/classroom.css`, `js/classroom.js`, `js/classroom-boot.js`).
2. Embed mode, `?embed=1` (same files), and the `frame-ancestors` split in `hepgraph/server.py`.
3. The glossary: `data/atlas/glossary/terms.json`, loader, validator rule, `glossary.json` bundle,
   `js/glossary.js` (annotation and popover).
4. The plain / technical summary toggle (`js/summary.js`, wired in `js/panels.js`).

Only item 3 writes data. Nothing else in `data/atlas/` changed.

## Entities written

* `data/atlas/glossary/terms.json`: 29 terms. Each has a plain definition (at most 45 words), a verbatim
  `quote` (at most 300 characters), a `locator`, `sources`, `confidence: verified`,
  `verified_at: 2026-10-26`, and the `match` patterns that find it in panel text.
* 8 new source records, `data/atlas/sources/glossary-*.json`: four PDG 2026 reviews (statistics, neutrino
  properties, neutrino beam lines, passage of particles through matter) and four CERN Courier pages.
  Every page returned HTTP 200 on 2026-10-26. The other 11 sources the terms cite already existed and were
  reused (same URL).

| term | source | url | locator |
| --- | --- | --- | --- |
| axion | src:topic-pdg-2026-axions | https://pdg.lbl.gov/2026/reviews/rpp2026-rev-axions.pdf | §89.1 Introduction |
| baseline | src:topic-pdg-2026-neutrino-mixing | https://pdg.lbl.gov/2026/reviews/rpp2026-rev-neutrino-mixing.pdf | §14.6.3.3 Long-baseline experiments |
| calorimeter | src:topic-pdg-2026-particle-detectors-accelerators | https://pdg.lbl.gov/2026/reviews/rpp2026-rev-particle-detectors-accel.pdf | §35.10.1 Calorimeters, Introduction |
| centre-of-mass-energy | src:cern-isr-page | https://home.cern/science/accelerators/intersecting-storage-rings | Page body, second paragraph (Intersecting Storage Rings) |
| cevns | src:glossary-cern-courier-cevns-2017 (new) | https://cerncourier.com/a/miniature-detector-first-to-spot-coherent-neutrino-nucleus-scattering/ | Second paragraph of the article (CERN Courier, 22 September 2017) |
| cherenkov-light | src:glossary-pdg-2026-passage-of-particles-through-matter (new) | https://pdg.lbl.gov/2026/reviews/rpp2026-rev-passage-particles-matter.pdf | §34.7 Cherenkov and transition radiation |
| confidence-level | src:glossary-pdg-2026-statistics (new) | https://pdg.lbl.gov/2026/reviews/rpp2026-rev-statistics.pdf | §40.4.2 Frequentist confidence intervals |
| cp-violation | src:topic-pdg-2026-cp-violation | https://pdg.lbl.gov/2026/reviews/rpp2026-rev-cp-violation.pdf | §13 CP Violation in the Quark Sector, opening paragraphs |
| cross-section | src:cern-lhc-page | https://home.cern/science/accelerators/large-hadron-collider | FAQ answer to 'What is luminosity?' |
| energy-threshold | src:topic-pdg-2026-dark-matter | https://pdg.lbl.gov/2026/reviews/rpp2026-rev-dark-matter.pdf | §27.6.2 Direct detection formalism |
| exposure | src:glossary-cern-courier-darkside-2018 (new) | https://cerncourier.com/a/defeating-the-background-in-the-search-for-dark-matter/ | Section 'Leading limits' |
| fiducial-volume | src:topic-pdg-2026-dark-matter | https://pdg.lbl.gov/2026/reviews/rpp2026-rev-dark-matter.pdf | §27.6.3 Current and future direct detection technologies |
| luminosity | src:cern-hilumi-lhc-page | https://home.cern/science/accelerators/hilumi-lhc | FAQ answer to 'What is luminosity?' |
| metres-water-equivalent | src:glossary-cern-courier-baksan-2017 (new) | https://cerncourier.com/a/baksan-scales-new-neutrino-heights/ | Section 'Current experiments' (Low Background Lab 3 at Baksan) |
| mixing-angle | src:glossary-pdg-2026-neutrino-properties (new) | https://pdg.lbl.gov/2026/reviews/rpp2026-rev-intro-neutrino-prop.pdf | Opening paragraph of 'Neutrino Properties' |
| muon-veto | src:topic-pdg-2026-particle-detectors-non-accelerator | https://pdg.lbl.gov/2026/reviews/rpp2026-rev-particle-detectors-non-accel.pdf | §36.6.5 Mitigation of backgrounds and active background discrimination |
| neutrino-mass-ordering | src:topic-pdg-2026-neutrino-mixing | https://pdg.lbl.gov/2026/reviews/rpp2026-rev-neutrino-mixing.pdf | §14.7 Combined Analysis of Experimental Results: The 3ν Paradigm |
| neutrino-oscillation | src:opera-cern-cngs-page | https://home.cern/science/accelerators/cern-neutrinos-gran-sasso | Page body, first paragraph (CERN Neutrinos to Gran Sasso) |
| neutrinoless-double-beta-decay | src:topic-pdg-2026-neutrino-mixing | https://pdg.lbl.gov/2026/reviews/rpp2026-rev-neutrino-mixing.pdf | §14.9.2 Dirac vs. Majorana: Neutrinoless Double-beta Decay |
| nuclear-recoil | src:topic-pdg-2026-particle-detectors-non-accelerator | https://pdg.lbl.gov/2026/reviews/rpp2026-rev-particle-detectors-non-accel.pdf | §36.4 Large time-projection chambers for rare event detection |
| off-axis-angle | src:glossary-pdg-2026-neutrino-beam-lines (new) | https://pdg.lbl.gov/2026/reviews/rpp2026-rev-nu-beams-parameters.pdf | §33 Neutrino Beam Lines at High-Energy Proton Synchrotrons, opening paragraph |
| overburden | src:lngs-overview | https://www.lngs.infn.it/en/lngs-overview | Page body, paragraph on the rock thickness above the Laboratory |
| photomultiplier-tube | src:topic-pdg-2026-particle-detectors-accelerators | https://pdg.lbl.gov/2026/reviews/rpp2026-rev-particle-detectors-accel.pdf | §35.2.1.1 Photomultiplier tubes |
| scintillator | src:topic-pdg-2026-particle-detectors-accelerators | https://pdg.lbl.gov/2026/reviews/rpp2026-rev-particle-detectors-accel.pdf | §35.3 Organic scintillators |
| significance-sigma | src:glossary-pdg-2026-statistics (new) | https://pdg.lbl.gov/2026/reviews/rpp2026-rev-statistics.pdf | §40.3.2 Tests of significance, p-values |
| sterile-neutrino | src:topic-pdg-2026-neutrino-mixing | https://pdg.lbl.gov/2026/reviews/rpp2026-rev-neutrino-mixing.pdf | §14.1 Neutrinos in the Standard Model: Massless Neutrinos |
| synchrotron | src:glossary-cern-courier-synchrotron-1960 (new) | https://cerncourier.com/a/a-comparison/ | Section 'The synchrotron' (CERN Courier, September 1960) |
| time-projection-chamber | src:topic-pdg-2026-particle-detectors-accelerators | https://pdg.lbl.gov/2026/reviews/rpp2026-rev-particle-detectors-accel.pdf | §35.6.4 Time-projection chambers |
| wimp | src:glossary-cern-courier-darkside-2018 (new) | https://cerncourier.com/a/defeating-the-background-in-the-search-for-dark-matter/ | Section 'Direct detection with liquid argon', second paragraph |

## Checks of the data

* `scripts/atlas_quote_check.py --only glossary`: 29 of 29 `verbatim`, 0 number flags (run independently
  of the researchers who picked the quotes).
* PDG section numbers in the locators were re-read from the extracted review text.
* `python -m hepgraph.atlas.validate`: 0 errors, 1596 warnings (the same count as before this branch), no
  `glossary-*` finding, and no `uncited-source` warning for the new sources (a glossary term now counts as
  citing its source).

## Conflicts

None between sources: each term has one source and one quote.

## Where the definition goes beyond its quote, or the quote does not contain the term

The definitions were rewritten to say only what each quote supports. Still weaker than the rest:

* **m.w.e.** The quote (CERN Courier on Baksan) states shielding "equivalent of 4900 m of water" and does not
  contain the abbreviation. No PDG review, LNGS, SURF or SNOLAB page that could be fetched defines it.
* **overburden.** The quote (LNGS overview) gives the rock thickness above the laboratory and the
  cosmic-ray reduction; the word "overburden" is not in it.
* **exposure.** No PDG review or lab page defines it. The quote is a DarkSide-20k sentence ("100 tonne x year in
  five years"); "detector mass times running time" is read from the unit.
* **energy threshold.** The PDG sentence shows what a threshold does ("energy thresholds around a few 100 eV -
  few keV") but does not define it; "the lowest energy a detector can register" is a plain reading.
* **fiducial volume and fiducial mass.** The quote defines the fiducial volume; "fiducial mass" is covered by
  the title only.
* **mixing angle, baseline, centre-of-mass energy, significance.** The quotes state the facts the definitions
  use (two large mixing angles; K2K's 250 km baseline; the ISR's 62 GeV against a 2000 GeV fixed target;
  significance as an equivalent number of standard deviations). The "5 sigma for a discovery" convention is not
  in the glossary because the page that states it could not be fetched from a script.
* The CEvNS and synchrotron terms rest on CERN Courier (CERN's magazine), not home.cern, because the
  COHERENT/ORNL, Fermilab, Symmetry and LBL pages returned 403 or a Cloudflare challenge to a script.

## Unresolved

* None of the 29 terms is unresolved. `decay length` (named in the brief) is not in the glossary: no panel text
  uses it (0 occurrences in all summaries), so it would never appear. It can be added with a sourced quote when
  the beam-section view needs it.

## Candidates considered and excluded

`background`, `Majorana` (only as a detector name), `pile-up`, `emittance`, `geoneutrino`, `beam dump`: used
rarely, or in more than one sense, so a first-use button could mark the wrong one. `threshold` on its own is
excluded for the same reason (it also means a particle-production threshold); only `energy threshold` and its
hyphenated forms match.

## For the integrator

* `glossary.json` is a new bundle: rebuild `static/atlas/generated/` at merge (it is not committed here).
* `state.js` gained `embed`, `theme` and `patchQuietly()`; `globe.js` reads `--beam-stroke-scale` and
  `--globe-amber`; `globeicons.js` reads `--globe-ink` (it read `--paper` and `--amber`, which projector mode
  redefines). `phone.js` moves the projector button into the filters sheet.
* An embedded view omits the footer, which is where the Atlas says its coverage is partial. The About page says
  so; a course page that embeds the Atlas should say it too.
