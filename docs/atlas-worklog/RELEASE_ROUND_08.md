# Release round 8 — a second independent review of the release candidate

Integration branch `atlas-release`, 2026-10-25. A notation pass, then a second
Sonnet reviewer who had not built the Atlas used the release candidate as five
kinds of reader on three browser engines; two streams fixed what it found; the
integrator re-checked the changed facts and ran every suite on the merged build.

## What the reviewer confirmed

* 17 neutrino-oscillation headlines (Daya Bay, Double Chooz, RENO, NOvA, ORCA6,
  OPERA, DeepCore, MINOS, T2K ×3, K2K, KamLAND, MiniBooNE, LSND, SNO CC/NC) match
  their arXiv abstracts; the T2K correction holds; computed distances (Fermilab →
  SURF ≈ 1290 km, 288°) reproduce; ring sizes match scale bars; 787 panels show
  no "undefined", "NaN" or empty headings.
* 13 of 16 earlier findings fully fixed, three partly (all completed this round).

## What changed

**Physics typesetting.** 425 display strings now read like a physics text —
"2 × 10³⁴ cm⁻² s⁻¹", "νμ → ντ appearance at 5.1σ", "θ₁₃", "√s = 1.8 TeV",
"126.0 ± 0.4 (stat.) ± 0.4 (sys.) GeV" — without touching a single quote, number
or unit (the quote checker's per-item results are identical before and after).
Result headings show the Atlas's typeset name, with the paper's title verbatim
underneath.

**Result panels lead with the plain summary.** They used to open with the raw
abstract quote — for a third of results a repeat of the title, for a fifth raw
LaTeX ("$638.0 \pm 132.8$ … ($4.8 \sigma$)"). Now: the plain-language summary,
then "From the abstract: … 638.0 ± 132.8 … (4.8 σ)" typeset, with "Show
verbatim" for the text exactly as published.

**Three things that were simply wrong, fixed**

* Oak Ridge's map labelled the whole SNS complex "SNS Neutrino Alley" while
  listing Neutrino Alley as not drawn. The outline now belongs to a new SNS
  complex site; Neutrino Alley stays COHERENT's site with an honest note (its
  position is unpublished; it is "a basement hallway" ~20 m from the target).
* Seven panels printed "Near ([object Object]–present)"; dates with an
  uncertainty range now read "Near (c. 2009–present)".
* The timeline did not move the globe's clusters: at 1950 seven clusters still
  listed facilities that did not exist. Clusters now hold only what is present in
  the chosen year.

**Facts brought into line**

* One CERN-sourced Long Shutdown 3 for every LHC experiment: to mid-2030,
  HL-LHC start-up June 2030 ✓ (ATLAS said 2029). "Upgrade" only where a source
  says the experiment's own detector is being upgraded (ATLAS, CMS, ALICE,
  LHCb); the others read "shutdown".
* ATLAS: 175 institutions ✓ (246 institutes counting cluster members and
  associates ✓); roster wording no longer says "0 confirmed institutions".
* DUNE's far-detector depth cites DUNE's own TDR ("the 4850 (foot) level"), not a
  MAJORANA news page. SNS construction began 15 December 1999 (was "?"). Fermilab's
  website is fnal.gov. ProtoDUNE-SP ran August 2018 – July 2020.
* About 2,000 internal research notes ("REVIEW REQUIRED (A17)", "fetched this
  session", "Second pass") were rewritten as plain statements of the evidence
  and its limits, across ~800 records.
* Map feature names say what is drawn: "LHC Point 1 surface site (ATLAS)", "CMS
  cavern position (published coordinate, ±30 m)".
* Campus outlines (Williams Field, BNL, ISIS, MIT, WIPP, SLAC, KIT, PSI) had
  inherited an experiment's lifetime and vanished from today's map; they are
  timeless context now. Fermilab's Wilson Hall (1973), MI-62 and the Main
  Injector infield (1997) appear only from their sourced years.

**Interface**

* "Higgs discovery" and "where was the Higgs discovered" put the two 2012
  discovery papers first.
* Selecting a topic flies to its highlighted facilities.
* Uncertainty circles are hollow dashed rings, distinct from footprints.
* The depth view no longer invents a surface depth for tunnels whose depth is
  unrecorded.
* Each facility panel lists all its maps (JUNO's two, KM3NeT's two).
* Play has 1×/2×/5× speed.
* Phone Results start with the list, the filters folded.

## How the experience improved, and why it is better

The release candidate's remaining errors were the kind that cost a reader's trust
quietly: a label naming the wrong place, a date printed as "[object Object]", a
globe at 1950 full of facilities that did not exist, a quote pasted in LaTeX. A
reader now meets plain prose first, typeset physics, maps whose labels say what
the shape is, and a time slider that tells the truth.

## Verified, and how

* Integrator re-read: atlaspo.cern.ch institution totals (175 / 246); home.cern
  "postponing the start-up of the High-Luminosity LHC until June 2030"; browsed
  MiniBooNE's new panel and the 1950 globe.
* Browser suite on the merged build: Chrome 96/96, Firefox 95/95, WebKit 95/95;
  accessibility 35/35, 0 axe violations; full Python suite 682 passed; validator 0
  errors; quote checker: no new missing or near-miss quotes.
