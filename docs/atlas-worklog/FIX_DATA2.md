# FIX_DATA2: sentences as strong as their sources (2026-10-28)

Branch `atlas-fix-data2`. Scope: the data-and-wording findings of the independent
"sceptic" review of the Atlas (tours and records). Interface code is another
stream's. Sources were fetched on 2026-10-28 (no inspirehep.net, no Wikipedia);
changed values carry `verified_at: "2026-10-28"`.

Checks at the end: validator `0 errors, 1925 warnings` (the warning count is
unchanged from the base); `tests/test_atlas_tours.py`, `tests/test_atlas_validate*.py`
and the tour-player tests pass; full suite see the final report.

## 1. Tour `neutrino-oscillation-story`, step 1 (Homestake)

The Sun produces the number of neutrinos the solar model predicts; the chlorine
detector counted about a third of the predicted rate.

* Before: "The Sun produces one-third as many neutrinos as expected, wrote Raymond Davis, and this was the solar neutrino problem." (a reference claim to `result:homestake-flux-measurement-1998` `why_it_matters`).
* After: "It detected about one-third as many neutrinos as the standard solar model predicted, wrote Raymond Davis, and this was the solar neutrino problem." (own claim).
* Source: Davis, Nobel Lecture, https://www.nobelprize.org/uploads/2018/06/davis-lecture.pdf (`src:rf06-davis-nobel-lecture-2002`), section on the chlorine experiment results.
* Quote: "the current value from the Homestake chlorine experiment is 2.56 SNU (Cleveland et al., 1998) and the current prediction of the standard solar model is 7.6 SNU (Bahcall et al., 2001)". The same page: "The discrepancy between theory and experiment was a robust factor of three." 2.56 ÷ 7.6 = 0.34.
* The record `result:homestake-flux-measurement-1998` repeated Davis's shorthand ("found the Sun produces about one-third as many neutrinos as the standard solar model expects", and in `summary.plain`). `why_it_matters`, its quote, locator and `summary.plain` now state the comparison (2.56 SNU against 7.6 SNU, about a third of the predicted rate). The step title "The Sun's missing neutrinos" is the usual idiom and was kept.

## 2. SNO plain summary

* Before: "... that solved the decades-old mystery of the Sun's missing neutrinos by showing they change type on the way to Earth."
* After: "... filled with 1000 tonnes of heavy water. Its neutral-current measurement gave direct evidence that electron neutrinos produced in the Sun change flavour, and a total solar neutrino flux consistent with solar models."
* Source: arXiv:nucl-ex/0204008 (https://arxiv.org/abs/nucl-ex/0204008), title and abstract.
* Quotes: title "Direct Evidence for Neutrino Flavor Transformation from Neutral-Current Interactions in the Sudbury Neutrino Observatory"; abstract "providing strong evidence for solar electron neutrino flavor transformation. The total flux measured with the NC reaction is 5.09 ... x10^6/(cm^2 s), consistent with solar models."
* The tour's SNO step already says "direct evidence"; its claims were not changed.

## 3. KLOE and KLOE-2

* KLOE-2, before: "... recorded about 8 inverse femtobarns, the largest sample ever taken at the phi resonance." After: "... With KLOE it recorded about 8 inverse femtobarns, which CERN Courier called in 2018 the largest ever sample collected at the phi-resonance peak."
  Source: CERN Courier, 1 June 2018, https://cerncourier.com/a/kloe-2-completes-data-taking-at-frascati-collider/ . Quote: "an integrated luminosity of around 8 fb−1 (corresponding to around 24 billion φ-mesons) was acquired, representing the largest ever sample collected at the φ-resonance peak."
* KLOE, before: "The main experiment at Frascati's DAΦNE phi factory from 1999 to 2006. ... recorded about 2.5 inverse femtobarns ..." After: "An experiment at Frascati's DAΦNE phi factory that took data from about 1999 to 2006. ... With its successor KLOE-2 it recorded around 8 inverse femtobarns."
  * "Main" went: INFN-LNF (https://w3.lnf.infn.it/accelerators/dafne/?lang=en) lists KLOE, FINUDA, DEAR and SIDDHARTA as experiments that used DAΦNE "with different aims and at different times"; the "main particle physics experiment at LNF" statement on https://w3.lnf.infn.it/research/particle-physics/?lang=en is about KLOE-2 and the laboratory, not KLOE and DAΦNE.
  * The "2.5 fb-1" was not stated by any cited source (it is 8 − 5.5 by subtraction); replaced by the CERN Courier total.
  * Start: CERN Courier says 1999, INFN-LNF says 2000 (existing interval note); "from about 1999".

## 4. Tour chronology (all six tours checked step by step)

Rule applied: a step's `year` is not earlier than the latest event or published statement its sentences report; `select` must exist in that year.

| Tour / step | Before | After | Why |
|---|---|---|---|
| higgs-hunt / `tevatron` | year 2011, `accelerator:fermilab-tevatron` | year 2012, `facility:fermilab`, moved after the LHC step, retitled "The Tevatron's evidence" | reports the CDF+D0 combination of July 2012 (arXiv:1207.6436); the Tevatron, CDF and D0 are absent from the timeline in 2012 (state_at is None), so the step selects Fermilab. Order is now LEP, LEP limit, LHC (2011), Tevatron (2012), ATLAS, CMS |
| higgs-hunt / `lep` | 1999 | 2000 | "topped 209 GeV in 2000"; the 2461 pb-1 includes the 2000 data. `accelerator:lep` exists in 2000 |
| higgs-hunt / `lep-limit` | year 2003, second sentence "as ATLAS recalled in its discovery paper ... below 158 GeV" | same year, second sentence from the 2003 LEP paper itself | the 158 GeV figure is the 2012 paper's (2011 fits) and did not exist in 2003. Quote (arXiv:hep-ex/0306033, https://arxiv.org/pdf/hep-ex/0306033, Section 1): "indirect experimental limits are obtained from precision measurements of the electroweak parameters ... constrain its value to less than 193 GeV/c2 at the 95% confidence level" |
| higgs-hunt / `why-a-higgs` | 1990 | no `year` (optional, A28) | the second sentence reports how the 2012 ATLAS paper described the Higgs boson ("the only elementary particle in the SM that has not yet been observed"), which was not true in 1990 (top quark unobserved). The player does not move the timeline when a step has no year |
| neutrino-beams / `k2k` | 2001 | 2004 | "From June 1999 to November 2004". `beamline:kek-neutrino` exists in 2004 (completed) |
| neutrino-beams / `cngs` | 2011, `beamline:cngs` | 2015, `result:opera-tau-neutrino-appearance-discovery-2015` | cites OPERA, July 2015. CNGS is absent from the timeline from 2013, so the step selects the OPERA result; the `beam-section` view still wins the route and shows CNGS as completed |
| w-and-z / `sppbar-collider` | 1982, "From 1981 to 1990 CERN's SPS was used as a proton-antiproton collider" | 1982, "CERN's Super Proton Synchrotron was used as a proton-antiproton collider from 1981" | the 1990 end is not an event of 1982; the reference claim `accelerator:sps` `intervals.proton-antiproton collider (SppS)` still supports "from 1981" |
| w-and-z / `lep-neutrinos` | 1995, `accelerator:lep` | 2006, `result:lep-electroweak-precision-2006` | "A final combination of the LEP and SLC results" is arXiv:hep-ex/0509008 (Sept 2005), Phys. Rept. 2006. LEP is absent after 2000, so the step selects the result |
| going-underground / `gran-sasso` | 2017 | 2018 | "ran from 2015 until 2018"; `experiment:xenon1t` exists in 2018 (completed) |

Checked and left: all other steps (the regex scan for years later than the step year found only m.w.e. and depths such as 2070 and 2039). Notes on the two steps that look close: neutrino-oscillation `homestake` (1975) quotes Davis (2002) as the author of the comparison, whose 1/3 ratio he says "haven't changed much" since 1968; `numi` (2010) mentions NOvA's far detector distance, a geometric fact with no dated event.

## 5. CERN injector-fed experiments against Long Shutdown 3 (2026-08-31)

ALPHA was already consistent in this branch: `status: shutdown`, intervals `active 2005 to 2026-08-31` then `shutdown 2026-08-31`, same on `detector:alpha`, `detector:alpha-g` and `collaboration:alpha`; the validator's A10 check passes. The "Active in 2026" the reviewer saw is the interface: `statusForTimeline` in `static/atlas/js/model.js` reads a year selection at **month 7** (July), and ALPHA was running in July 2026. That is an interface question (the UI stream), not a data fix; I did not touch it.

Checked, nothing to change (experiment, detector and, where it exists, beamline records all end the active interval on 2026-08-31 and carry a `shutdown` interval citing `src:currency-cern-all-accelerators-2026-08-31`): ALPHA, ALPHA-g, AEgIS, ASACUSA, BASE, GBAR, PUMA (commissioning to 2026-08-31), NA61/SHINE, NA62, NA64, AMBER, `beamline:cern-north-area`, `accelerator:ps`, `psb`, `sps`, `linac4`, `cern-ad`, `elena`. COMPASS ended in 2022, ATRAP and ATHENA are completed. LHC-side experiments (ATLAS, CMS, ALICE, LHCb `upgrade`; FASER, LHCf, MoEDAL, SND@LHC, TOTEM `shutdown` from 2026-06-29) were done by an earlier pass. A script comparing every experiment's and detector's status with its accelerator or beamline status found no CERN injector-fed record that is `active` while its source is shut down.

For the integrator: `collaboration:na62`, `na64`, `snd-lhc`, `faser`, `lhcf`, `moedal`, `totem` stay `active` with no LS3 interval, while the antimatter and NA61/AMBER collaborations carry one. The Atlas has no stated rule for collaborations; I left them (a collaboration continues through a shutdown), but the two conventions are mixed.

## 6. Present-tense summaries on finished records

Rule: a `summary.plain` of a `completed`, `decommissioned` or `cancelled` record may not describe the thing as running; a `shutdown` record may not claim it is running now. Descriptions of an instrument's technique ("tracks the paths of particles") and identity statements for paused experiments ("NA62 is a CERN experiment that fires a beam of kaons ...") were left. The scan used a list of present-tense verbs plus currency words over all 600-odd terminal-status records; all 121 hits were read.

| Record | Before | After |
|---|---|---|
| experiment:star | "STAR is a house-sized, 1,200-tonne particle detector ... that has watched gold and other heavy atomic nuclei smash together since 2000" | "STAR was ... that watched ... from 2000 until RHIC's final run ended in February 2026" (interval end 2026-02-06, existing quote) |
| experiment:sphenix | "sPHENIX is a new, house-sized detector" | "sPHENIX was a house-sized detector ... It took data from 2023 until RHIC's final run ended in February 2026" |
| detector:sphenix | "A new ... detector ... that records" | "A ... detector ... that recorded" |
| collaboration:sphenix | "who built and now run sPHENIX" | "who built and ran sPHENIX" |
| experiment:pandax-4t | "PandaX-4T is a dark matter detector ... It has been taking data since 2021" | "PandaX-4T was ... It took data in three runs from 2021 and was shut down in April 2026" (intervals: "Shut down at Apr. 15th"; "After completing three data-taking runs, the PandaX-4T experiment concluded its operation and was decommissioned in May 2026.") |
| experiment:apex-jlab | "APEX searches for ..." | "APEX searched for ..." |
| experiment:crex | "CREX is PREX's sister experiment" | "CREX was PREX's sister experiment" |
| experiment:des | "it tests how dark energy and gravity shape the universe" | "it set out to test ..." |
| experiment:moscab | "MOSCAB ... is a bubble chamber" | "... was a bubble chamber" |
| experiment:muon-g-2 | "stores muons ... and watches them wobble" | "stored ... and watched them wobble" |
| experiment:e949 | "the same ultra-rare decay NA62 studies today" | "... NA62 also studies" |
| experiment:cmb-s4 | "it is being shut down in an orderly way" | "the project said it was proceeding with an orderly shutdown" (project page wording, existing interval note) |
| accelerator:fermilab-main-injector | "Its beam makes the NuMI neutrinos today" | "... but it has not operated since July 2024; a restart was planned for October 2026" (existing intervals: Fermilab PAC April and September 2026) |
| accelerator:ps | "CERN's oldest working accelerator ... it still feeds every beam" | "... until it paused for Long Shutdown 3 on 31 August 2026 it fed every beam ..." |
| experiment:nova | "Fermilab fires a beam of neutrinos 810 kilometres ... watching" | "when Fermilab's NuMI beam runs, it fires ... The beam has been off since July 2024." |
| experiment:spinquest | "SpinQuest fires Fermilab's 120 GeV proton beam" | "SpinQuest uses ... and has had no beam since summer 2024" |
| 11 completed collaborations (athena, atrap, mulan, nist-bl1, nist-bl2, pen, pienu, ps210, psi-nedm, sussex-ral-ill-nedm, twist) | "The international team of scientists who run the X experiment." | "... who ran ..." |

Not changed, listed for the integrator: `collaboration:cmd` has status `completed` (interval ends 1984) but its plain summary describes CMD-1, CMD-2 and CMD-3 at VEPP-2M and VEPP-2000 "since 1979"; one of the two is wrong. `accelerator:hera` has an empty `summary.plain`.

## 7. Result typing and key text

* `result:coupp-2kg-spin-dependent-limits-2008`: `key_value_text` was "An exposure in excess of 250 kg-days is obtained, with a live-time fraction reaching 80%." Now "Spin-dependent WIMP-proton couplings above the curve of Fig. 6 are excluded at 90% C.L." Quote: "Couplings above the line would have produced signals above observed backgrounds and are excluded to 90% C.L." (arXiv:0804.2886, https://arxiv.org/pdf/0804.2886, Fig. 6 caption). The paper publishes the limit as a curve and gives no single number, so `key_value` stays null. The main text says the limits come from "three independent large data sets adding up to 52 kg-days of exposure", not from the 250 kg-days; `summary.technical` now says so.
* `result:orpheus-first-results-2004`: `result_type` `measurement` to `limit`. The key text "The region above the curve is excluded at a 90% confidence level." is from Section 4.1 of arXiv:astro-ph/0404311 (https://arxiv.org/pdf/astro-ph/0404311), not the abstract as the locator said; locator corrected, value made specific (spin-independent, Fig. 12).
* Same pattern, not changed (limit results whose `key_value` is an exposure and not the limit): `coupp-4kg-minos-limits-2010` (abstract: "the strongest direct detection constraint to date on WIMP-proton spin-dependent scattering for WIMP masses >20 GeV/c2"), `coupp-4kg-snolab-limits-2012` (same wording, "world best"), `dm-ice17-annual-modulation-2017`, `hdms-spin-dependent-wimp-neutron-limit-2005`, `pico-2l-first-results-2015`, `pico-2l-run2-2016`, `pico-60-cf3i-2015` (live days), `texono-bosonic-dm-npcge-2019`, `texono-pcge-wimp-limits-2013`, `texono-ulege-220ev-wimp-limits-2008`, `warp-first-physics-results-2007`.

## 8. Tour answer "≈ 32 km" against the view's 32.5 km

`neutrino-beams-through-the-earth` / `lbnf`: the answer said "≈ 32 km" and "≈ 5.8°" from `digits: 2`. The calculation gives 32.48 km and 5.788°; the view (1285.4 km chord from the recorded coordinates) shows 32.5 km and 5.79°. Now `digits: 3`, values 32.5 and 5.79, answer text "≈ 32.5 km" and "≈ 5.79°", so tour and view agree to three significant figures. The validator re-evaluates both lines.

## Unresolved

* ALPHA "Active in 2026": interface (month-7 sampling), see section 5.
* The eleven limit results whose key value is an exposure (section 7).
* `collaboration:cmd` status against its summary; empty plain summary of `accelerator:hera`; mixed collaboration-status convention during LS3.
