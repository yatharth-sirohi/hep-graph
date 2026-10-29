# Follow-ups 2, colliders stream: the DAΦNE nuclear-physics experiments, ADONE, PADME, SCTF and STCF

Owner tag `colliders-2`. Worktree `HEP-Graph-ar-followups2`, branch `atlas-followups2`. Written 2026-10-26 (`verified_at` for every record; the calendar has moved on). Registry rows: `data/atlas/coverage/colliders-2.json` (15 rows appended, existing rows untouched).

## Scope

This pass takes over the deferred candidates of `COLLIDERS_2.md` ("Candidates considered and excluded"), in the brief's priority order: (1) the DAΦNE nuclear-physics experiments FINUDA, DEAR and SIDDHARTA, then SIDDHARTA-2 and PADME; (2) ADONE, the Frascati e+e- collider, and its experiments; (3) SCTF (BINP Novosibirsk) and STCF (Hefei), each only where a design report or an official project document names the host site. Amendment A26 counts the kaonic-atom and hypernuclear experiments as in scope because they share DAΦNE with the collider. Nothing was committed (the lead commits). INSPIRE, Neon and Vercel were not touched; `static/atlas/generated` was not touched and the build was not run.

Every record is tier D (accelerators, the new facility and the new site C), `researched: partial`. **No existing record was edited** except `data/atlas/coverage/colliders-2.json`, to which 15 rows were appended; `accelerator:dafne`, `facility:infn-lnf-frascati`, `site:infn-lnf-frascati`, `facility:binp-novosibirsk` and `site:binp-novosibirsk-akademgorodok` are only referenced.

## Counts

| type | new records |
|---|---|
| facilities | 1 (`facility:stcf-hefei`) |
| sites | 1 (`site:stcf-hefei-future-big-science-city`) |
| accelerators | 3 (`adone`, `stcf`, `sctf`) |
| experiments | 15 |
| detectors | 15 |
| collaborations | 13 |
| results | 8 |
| sources | 43 |
| coverage rows | 15 |

Shared record: `collaboration:adone-gamma-gamma` serves both `experiment:adone-gamma-gamma` and `experiment:adone-gamma-gamma-2`. `experiment:sctf` has no collaboration (none found).

## Entities written

Each interval row gives the URL of the first cited source and the verbatim quote (or locator) behind that date. Detectors and collaborations repeat their experiment's dates unless stated.

### 1. DAΦNE nuclear-physics experiments (FINUDA, DEAR, SIDDHARTA, SIDDHARTA-2)

Host: `facility:infn-lnf-frascati`, site `site:infn-lnf-frascati` (campus-grade, existing, approximate), accelerator `accelerator:dafne` (existing; its energies and feed links were not edited). Experiment kind `hadron_structure` (see "For the integrator"). Topics `topic:hadron-structure`, `topic:qcd`, `topic:nuclear-and-heavy-ion`.

#### experiment:finuda: FINUDA (completed)

Kind `hadron_structure`; facility `facility:infn-lnf-frascati`; accelerators `accelerator:dafne`; collaboration `collaboration:finuda`; topics `topic:hadron-structure`, `topic:qcd`, `topic:nuclear-and-heavy-ion`.

| interval | kind | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|---|
| proposal | lifecycle | 1993 | 2003-12 | proposed | approximate | https://arxiv.org/abs/hep-ex/0606033 “FINUDA (FIsica NUcleare a DAΦNE) (6) in 1993 for the study of hypernuclear spectroscopy” (Franzini & Moulson (2006), Section 1 (Introduction)) Note: Year of the proposal. The sources fetched give no approval, construction or installation dates (a 1997 talk expected FINUDA to be operational by the beginning of 1998, arXiv:hep-ex/9712026). The interval ends at the start of the first data taking. |
| DAΦNE data taking (two runs) | lifecycle | 2003-12 | 2007-06 | active | verified | https://arxiv.org/abs/nucl-ex/0506028 (+2 more) “The first FINUDA data taking at DAΦNE started in December 2003 and was successfully concluded in March 2004.” (FINUDA first-results paper (Phys. Lett. B 622, 2005), Introduction; end = end of the second data taking (arXiv:1011.2695)) Note: Start from the collaboration's own paper (December 2003); Franzini & Moulson date the first physics run November 2003 to March 2004. End = end of the second run (June 2007). FINUDA did not run between the two runs: DAΦNE was dedicated to KLOE from May 2004 to December 2005 (Franzini & Moulson). |
| data taking ended | lifecycle | 2007-06 | — | completed | approximate | https://arxiv.org/abs/0803.1450 (+1 more) “has recently completed experimental runs for the three main detectors, KLOE, FINUDA and DEAR” (Milardi (2008), abstract; start = end of the second data taking) Note: The start is the end of the second run (June 2007); the March 2008 accelerator report only says the runs were 'recently completed'. The same report notes the second interaction region was rebuilt to be ready for a possible future FINUDA run; no later run is recorded in the sources fetched. |
| first data taking | run | 2003-12 | 2004-03 | active | verified | https://arxiv.org/abs/nucl-ex/0506028 (+1 more) “The first FINUDA data taking at DAΦNE started in December 2003 and was successfully concluded in March 2004.” (FINUDA first-results paper (Phys. Lett. B 622, 2005), Introduction) Note: Franzini & Moulson: 250 pb^-1 delivered, of which 50 pb^-1 were used for machine studies and detector calibration and 200 pb^-1 for analysis. |
| second data taking | run | 2006-11 | 2007-06 | active | verified | https://arxiv.org/abs/1011.2695 (+2 more) “accumulated in the second data taking lasted from November 2006 to June 2007” (FINUDA hypernuclear spectroscopy paper (arXiv:1011.2695), Introduction) Note: 966 pb^-1 recorded (arXiv:1011.2695). The DAΦNE accelerator report gives April 2006 for the start of the second run (arXiv:0803.1450) and Franzini & Moulson expected it 'during summer 2006'; the collaboration's own dates are used. |

- Host role: `facility:infn-lnf-frascati`: https://arxiv.org/abs/nucl-ex/0506028 “that is, the φ-factory DAΦNE at the Frascati National Laboratories of I.N.F.N., Italy”
- Physics goal: https://arxiv.org/abs/nucl-ex/0506028 “allows for the simultaneous measurement of observables like excitation energy spectra, lifetimes and partial decay widths for mesonic and non-mesonic decay, with high statistics and good energy resolution (better than 1 MeV)”
- Note: Kind hadron_structure is the nearest Atlas kind for strangeness nuclear physics; FINUDA is described as a fixed-target experiment at an e+e- collider (Franzini & Moulson 2006). It used kaons from φ decays, not e+e- collisions as such.
- Note: FINUDA and DEAR shared the second DAΦNE interaction point; KLOE sat at the first.

- `detector:finuda` (completed): technology class `spectrometer`; placement `site:infn-lnf-frascati` 2003-12 to 2007-06 (approximate): https://arxiv.org/abs/hep-ex/0311006 “The FINUDA experiment has been installed in the interaction region previuosly occupied by the DEAR experiment.” Note: Campus-grade placement: no fetched source locates the DAΦNE second interaction region; the marker is the LNF campus point. FINUDA and DEAR shared the second interaction point and were installed alternately (Franzini & Moulson).
  Technology: https://arxiv.org/abs/nucl-ex/0506028 “The layers of the tracker are contained inside a superconducting solenoid, which provides a highly homogeneous (within 2% inside the tracking volume) magnetic field of 1.0 T over a cylindrical volume of 146 cm radius and 211 cm length.”
- `collaboration:finuda` (completed): host `facility:infn-lnf-frascati`; formation 1993 (approximate): https://arxiv.org/abs/hep-ex/0606033 “FINUDA (FIsica NUcleare a DAΦNE) (6) in 1993 for the study of hypernuclear spectroscopy”; intervals as the experiment's.

#### experiment:dear: DEAR (completed)

Kind `hadron_structure`; facility `facility:infn-lnf-frascati`; accelerators `accelerator:dafne`; collaboration `collaboration:dear`; topics `topic:hadron-structure`, `topic:qcd`, `topic:nuclear-and-heavy-ion`.

| interval | kind | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|---|
| proposal | lifecycle | 1995 | 2000 | proposed | approximate | https://arxiv.org/abs/hep-ex/0606033 “DEAR (DAΦNE Exotic Atom Research) (7) in 1995 for the spectroscopy of K-mesic hydrogen atoms” (Franzini & Moulson (2006), Section 1 (Introduction)) Note: Year of the proposal; the interval ends at the start of the test runs (2000). |
| test runs and detector optimization | lifecycle | 2000 | 2002 | commissioning | approximate | https://arxiv.org/abs/hep-ex/0606033 “After test runs and detector optimization during 2000–2001, DEAR took physics data in 2002.” (Franzini & Moulson (2006), Section 6.2.1) Note: Test runs and detector optimization took place in 2000-2001; the interval ends in 2002 when physics data taking began (year precision). |
| DAΦNE physics data taking (kaonic nitrogen, then hydrogen) | lifecycle | 2002 | 2002 | active | approximate | https://arxiv.org/abs/hep-ex/0606033 (+1 more) “After test runs and detector optimization during 2000–2001, DEAR took physics data in 2002.” (Franzini & Moulson (2006), Section 6.2.1) Note: Year precision. Kaonic nitrogen data in October 2002 and about 60 pb^-1 on hydrogen in December 2002 (Di Falco 2003). The accelerator report (Milardi 2008, arXiv:0803.1450) says the DEAR run lasted 'less than 5 months during 2002-2003'; the 2002 dates of the DEAR physics papers' authors are used. |
| data taking ended | lifecycle | 2002 | — | completed | approximate | https://arxiv.org/abs/hep-ex/0311006 (+1 more) “The DEAR experiment, concluded in 2002, has measured the de-excitation of kaonic atoms.” (Di Falco (2003), abstract) Note: Year precision; FINUDA was installed in DEAR's interaction region in 2003. Conflict: arXiv:0803.1450 gives 2002-2003 for the DEAR run (see the log). |

- Host role: `facility:infn-lnf-frascati`: https://arxiv.org/abs/nucl-ex/0703028 “DAΦNE - the electronpositron collider at Laboratori Nazionali di Frascati (LNF) turned out to be the ideal machine for this kind of research.”
- Physics goal: https://arxiv.org/abs/hep-ex/0311006 “has the goal of measuring the isospin dependent antikaon-nucleon scattering lengths”
- Note: Kind hadron_structure is the nearest Atlas kind for kaonic-atom (low-energy QCD) physics at an e+e- collider.
- Note: Franzini & Moulson call DEAR 'literally a tabletop experiment': it shared the second DAΦNE interaction point with FINUDA and could be assembled when FINUDA was retracted.

- `detector:dear` (completed): technology class `other`; placement `site:infn-lnf-frascati` 2002 to 2002 (approximate): https://arxiv.org/abs/hep-ex/0606033 “The apparatus shares the second DAΦNE interaction point with the FINUDA experiment” Note: Campus-grade placement: no fetched source locates the DAΦNE second interaction region; the marker is the LNF campus point. Year precision for the physics run; test runs in 2000-2001 are not located by a source.
  Technology: https://arxiv.org/abs/hep-ex/0311006 “The photons produced in the de-excitation of these atoms are detected by 16 CCD-55 (Charged Coupled Devices).”
- `collaboration:dear` (completed): host `facility:infn-lnf-frascati`; formation 1995 (approximate): https://arxiv.org/abs/hep-ex/0606033 “DEAR (DAΦNE Exotic Atom Research) (7) in 1995 for the spectroscopy of K-mesic hydrogen atoms”; intervals as the experiment's.

#### experiment:siddharta: SIDDHARTA (completed)

Kind `hadron_structure`; facility `facility:infn-lnf-frascati`; accelerators `accelerator:dafne`; collaboration `collaboration:siddharta`; topics `topic:hadron-structure`, `topic:qcd`, `topic:nuclear-and-heavy-ion`.

| interval | kind | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|---|
| construction of the SIDDHARTA set-up | lifecycle | 2006 | 2009 | construction | approximate | https://arxiv.org/abs/nucl-ex/0703028 “The construction phase started in the second half of 2006 and will be finished in spring 2007.” (Marton (2007), section 'Setup development') Note: A 2007 plan: construction was to be finished in spring 2007 and the set-up installed at DAΦNE in 2007. The data were taken in 2009 (after DAΦNE's interaction-region changes of 2007-2008, arXiv:0803.1450), so the end of construction is taken as the start of data taking (year precision); no source fetched dates the installation. |
| DAΦNE data taking (kaonic hydrogen, helium and deuterium) | lifecycle | 2009 | 2009 | active | approximate | https://arxiv.org/abs/1105.3090 (+2 more) “Data were accumulated over six months in 2009 with integrated luminosities of ∼ 340 pb−1 for the hydrogen and ∼ 100 pb−1 for the deuterium measurement.” (SIDDHARTA kaonic hydrogen paper (Phys. Lett. B 704, 2011), Section 2) Note: Year precision; six months of data in 2009, the kaonic deuterium data in October 2009 (arXiv:1302.2797). The months of the six-month run are not given in the sources fetched. |
| data taking ended | lifecycle | 2009 | — | completed | approximate | https://arxiv.org/abs/1803.02587 “The most precise kaonic hydrogen measurement to-date, together with an exploratory measurement of kaonic deuterium, were carried out in 2009 by the SIDDHARTA collaboration” (Scordo et al. (arXiv:1803.02587), abstract) Note: Year precision; the end of the programme is inferred: the measurements 'were carried out in 2009' (past tense) and the apparatus was succeeded by SIDDHARTA-2, which no source dates before 2018. |
| kaonic deuterium run | run | 2009-10 | 2009-10 | active | verified | https://arxiv.org/abs/1302.2797 “The kaonic deuterium data were collected in October 2009, for a total integrated luminosity of about 100 pb−1.” (Bazzi et al. (arXiv:1302.2797), Section 2) |

- Host role: `facility:infn-lnf-frascati`: https://arxiv.org/abs/1105.3090 “The SIDDHARTA experiment was performed at the DAΦNE electronpositron collider at the Laboratori Nazionali di Frascati of INFN.”
- Lineage: `upgrade_of` `experiment:dear`: https://arxiv.org/abs/hep-ex/0311006 “An upgrade of the DEAR experiment called SIDDHARTA”
- Physics goal: https://arxiv.org/abs/1105.3090 “have determined the most precise values of the strong-interaction energy-level shift and width of the 1s atomic state”
- Note: Kind hadron_structure is the nearest Atlas kind for kaonic-atom (low-energy QCD) physics at an e+e- collider.
- Note: Milardi (2008) records that DAΦNE's interaction region was rebuilt for SIDDHARTA, with the crab-waist collision scheme first used for it (arXiv:0803.1450); the accelerator record is owned by another stream.

- `detector:siddharta` (completed): technology class `other`; placement `site:infn-lnf-frascati` 2009 to 2009 (approximate): https://arxiv.org/abs/1105.3090 “The SIDDHARTA experiment was performed at the DAΦNE electronpositron collider at the Laboratori Nazionali di Frascati of INFN.” Note: Campus-grade placement: no fetched source locates the DAΦNE interaction region used; the marker is the LNF campus point. Year precision.
  Technology: https://arxiv.org/abs/1105.3090 “The data acquisition system records the signal amplitudes seen by the 144 detectors along with the global time information.”
- `collaboration:siddharta` (completed): host `facility:infn-lnf-frascati`; formation not dated by a source (null); intervals as the experiment's.

#### experiment:siddharta-2: SIDDHARTA-2 (active)

Kind `hadron_structure`; facility `facility:infn-lnf-frascati`; accelerators `accelerator:dafne`; collaboration `collaboration:siddharta-2`; topics `topic:hadron-structure`, `topic:qcd`, `topic:nuclear-and-heavy-ion`.

| interval | kind | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|---|
| construction of the SIDDHARTA-2 apparatus | lifecycle | 2018 | 2022 | construction | approximate | https://arxiv.org/abs/1803.02587 (+1 more) “SIDDHARTA-2, is being realized to reach this goal” (Scordo et al. (arXiv:1803.02587), abstract) Note: As of March 2018 the upgraded apparatus 'is being realized' and the paper expects it to be installed on DAΦNE starting with 2018. In January 2022 the full apparatus was 'presently under installation' (arXiv:2201.09735), so the interval runs to 2022 (year precision); it overlaps the 2021 SIDDHARTINO pilot run, which used a reduced set-up. |
| DAΦNE data taking (SIDDHARTINO pilot run, then SIDDHARTA-2) | lifecycle | 2021 | — | active | approximate | https://arxiv.org/abs/2409.17845 (+2 more) “Since 2021, DAΦNE has been providing data to the SIDDHARTA experiment” (Milardi et al. (arXiv:2409.17845), Section 1) Note: Year precision. DAΦNE delivered data first to the preliminary SIDDHARTINO set-up (kaonic helium) and later to the final SIDDHARTA-2 configuration. The October 2026 review (arXiv:2610.35399) and INFN's laboratories page describe the experiment as operating at DAΦNE. |
| SIDDHARTINO pilot run (kaonic helium) | run | 2021 | 2021 | active | approximate | https://arxiv.org/abs/2201.09735 “a pilot run with a reduced setup, SIDDHARTINO, was performed in 2021 during the commissioning of the DAΦNE collider” (Sirghi et al. (arXiv:2201.09735), Section 1) Note: Year precision; the final period of SIDDHARTINO data taking was in June 2021 (arXiv:2201.09735). |
| kaonic deuterium campaign (2023-2024 data taking) | run | 2023 | 2024 | active | approximate | https://arxiv.org/abs/2610.35399 (+1 more) “The kaonic deuterium campaign was carried out with a cryogenic gaseous target during the 2023–2024 data-taking period.” (Sirghi et al. (arXiv:2610.35399), Section on kaonic deuterium) Note: Year precision. Deuterium operations 'started officially on the second half of May 2023' (arXiv:2409.17845) and a hydrogen-gas calibration run followed. |
| kaonic hydrogen measurement runs | run | 2023-12 | 2024-05 | active | verified | https://arxiv.org/abs/2607.13952 “The measurement was performed in two separate runs, from December 2023 to February 2024 and from April to May 2024, for a total integrated luminosity of 237 pb−1” (Bazzi et al. (arXiv:2607.13952), Section 3) Note: Two runs: December 2023 to February 2024 and April to May 2024. |

- Host role: `facility:infn-lnf-frascati`: https://arxiv.org/abs/2610.35399 “The SIDDHARTA-2 experiment at the DAΦNE electron–positron collider performs high-precision X-ray spectroscopy of kaonic atoms”
- Lineage: `upgrade_of` `experiment:siddharta`: https://w3.lnf.infn.it/accelerators/dafne/?lang=en “it is planned to install a new enhanced version of the SIDDHARTA detector on the accelerator”
- Physics goal: https://arxiv.org/abs/2409.17845 “to perform the first-ever measurement of kaonic deuterium X-ray transitions to the fundamental level”
- Note: Kind hadron_structure is the nearest Atlas kind for kaonic-atom (low-energy QCD) physics at an e+e- collider.
- Note: KAONNIS is the wider INFN-LNF kaon-nucleus programme that includes SIDDHARTA-2, AMADEUS and J-PARC measurements; only SIDDHARTA-2 is recorded here.
- Note: SIDDHARTA-2 papers seen in the sources fetched cover kaonic helium-4 (arXiv:2310.20584), kaonic neon (arXiv:2412.16101) and kaonic hydrogen (arXiv:2607.13952); no kaonic deuterium result was found as of 2026-10-26.
- Website `https://w3.lnf.infn.it/research/nuclear-physics/siddharta2/?lang=en`: https://w3.lnf.infn.it/research/nuclear-physics/siddharta2/?lang=en “KAONNIS: the SIDDHARTA-2 experiment”

- `detector:siddharta-2` (active): technology class `other`; placement `site:infn-lnf-frascati` 2021 to — (approximate): https://www.infn.it/en/infn-offices/laboratories/ “SIDDHARTA2, the experiment now operating at DAFNE, studies the features of exotic atoms.” Note: Campus-grade placement: no fetched source locates the DAΦNE interaction region; the marker is the LNF campus point. Year precision for the start.
  Technology: https://w3.lnf.infn.it/research/nuclear-physics/siddharta2/?lang=en “The SIDDHARTA-2 setup basically consists of a target filled with deuterium gas in cryogenic conditions, surrounded by Silicon Drift Detectors (SDD) specially developed to perform spectroscopic high precision measurements.”
- `collaboration:siddharta-2` (active): host `facility:infn-lnf-frascati`; formation not dated by a source (null); intervals as the experiment's.

Results:

- `result:finuda-12c-hypernuclear-spectroscopy-measurement-2005` (measurement, 2005-06-30, date kind preprint; experiments experiment:finuda): https://arxiv.org/abs/nucl-ex/0506028 “Λ-hypernuclei are produced and studied, with the FINUDA spectrometer, for the first time at an e+ e− collider: DAΦNE, the Frascati φ-factory.” Key value: “A preliminary analysis on 12 Λ C shows an energy resolution of 1.29 MeV FWHM on the hypernuclear levels, the best obtained so far with magnetic spectrometers at hadron facilities.” (https://arxiv.org/abs/nucl-ex/0506028).
- `result:finuda-6lh-evidence-2011` (evidence, 2011-12-19, date kind preprint; experiments experiment:finuda): https://arxiv.org/abs/1112.4529 “Evidence for the neutron-rich hypernucleus 6ΛH is presented from the FINUDA experiment at DAΦNE, Frascati” Key value: “The production rate of 6ΛH undergoing this two-body π- decay is determined to be (2.9\pm2.0)\cdot10-6/K-.” (https://arxiv.org/abs/1112.4529).
- `result:dear-kaonic-hydrogen-shift-width-measurement-2005` (precision_measurement, 2005-06-02, date kind publication; experiments experiment:dear): https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.94.212302 “The DEAR (DA$\ensuremath{\Phi}$NE exotic atom research) experiment measured the energy of x rays emitted in the transitions to the ground state of kaonic hydrogen.” Key value: “ε1s = −193±37(stat.)±6(syst.) eV and Γ1s = 249±111(stat.)± 30(syst.) eV” (https://arxiv.org/abs/nucl-ex/0703028).
- `result:siddharta-kaonic-hydrogen-shift-width-measurement-2011` (precision_measurement, 2011-05-16, date kind preprint; experiments experiment:siddharta): https://arxiv.org/abs/1105.3090 “Therefore, we have measured the K-series x rays of kaonic hydrogen atoms at the DAΦNE electron-positron collider of Laboratori Nazionali di Frascati, and have determined the most precise values of the strong-interaction energy-level shift and width of the 1s atomic state.” Key value: “The shift and width were determined to be ǫ1s = −283 ± 36(stat) ± 6(syst) eV and Γ1s = 541 ± 89(stat) ± 22(syst) eV, respectively.” (https://arxiv.org/abs/1105.3090).
- `result:siddharta2-kaonic-hydrogen-shift-width-measurement-2026` (precision_measurement, 2026-07-15, date kind preprint; experiments experiment:siddharta-2): https://arxiv.org/abs/2607.13952 “We report a new high-precision measurement of kaonic hydrogen X-ray transitions performed by the SIDDHARTA-2 experiment” Key value: “ε1s = −303.0 ± 17.0 (stat.) ± 2.5 (syst.) eV and Γ1s = 607 ± 62 (stat.) ± 6 (syst.) eV” (https://arxiv.org/abs/2607.13952).

### 1b. PADME (positron-on-target dark-photon search at the DAΦNE Beam Test Facility)

Host `facility:infn-lnf-frascati` / `site:infn-lnf-frascati`; kind `fixed_target`; topics `topic:dark-photons-dark-sectors`, `topic:accelerator-dark-matter-searches`. The experiment uses the positron beam of the DAΦNE linac at the Beam Test Facility (BTF-1), not the collider rings; `accelerator:dafne` is referenced because INFN describes the BTF as part of the DAΦNE complex and no linac record exists.

#### experiment:padme: PADME (active)

Kind `fixed_target`; facility `facility:infn-lnf-frascati`; accelerators `accelerator:dafne`; collaboration `collaboration:padme`; topics `topic:dark-photons-dark-sectors`, `topic:accelerator-dark-matter-searches`.

| interval | kind | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|---|
| proposal | lifecycle | 2015-01 | 2015-12 | proposed | approximate | https://arxiv.org/abs/1501.01867 (+1 more) “The PADME experiment proposes a search for the dark photon (A0 ) in the e+ e− → γA0 process in a positron-on-target experiment, exploiting the positron beam of the DAΦNE linac at the Laboratori Nazionali di Frascati, INFN.” (Raggi et al. (arXiv:1501.01867), abstract) Note: Start = the arXiv date (8 January 2015) of the earliest description fetched; the date of the proposal itself is not given. End = INFN's approval at the end of 2015. |
| approved by INFN; design and construction | lifecycle | 2015-12 | 2018 | construction | approximate | https://padme.lnf.infn.it/ “At the end of 2015 INFN has formally approved a new experiment, PADME, to search for invisible decays of the A' at the DAΦNE Linac in Frascati.” (PADME home page) Note: Start 'the end of 2015'. End: the page says the collaboration 'completed the design and the construction of the experimental apparatus in mid 2018' (year precision here). |
| commissioning | lifecycle | 2018 | 2019-07 | commissioning | approximate | https://arxiv.org/abs/2305.08684 (+1 more) “Since switching on in 2018 the experiment has collected more than 1013 positrons on target (PoT)” (Bertelli et al. (arXiv:2305.08684), abstract; end from arXiv:2205.03430) Note: Start = switching on in 2018 (the home page expected data from October 2018 to February 2019). End = July 2019, when data with a primary positron beam 'represented the completion of the commissioning of the experiment' (arXiv:2205.03430). |
| data taking at the DAΦNE Beam Test Facility | lifecycle | 2019-07 | — | active | approximate | https://arxiv.org/abs/2205.03430 (+1 more) “The PADME experiment explores the existence of a fifth force mediated by the so-called dark photon and connected with dark matter.” (INFN, Laboratories page (Frascati)) Note: Start = the end of commissioning (July 2019). INFN's page describes the experiment in the present tense; the latest data-taking campaign found is Run III (October to December 2022) and no end is stated. |
| Run II | run | 2020-07 | 2020-12 | active | approximate | https://arxiv.org/abs/2603.28685 “The PADME Run II data taking was realized in the second half of 2020.” (Dimitrova (arXiv:2603.28685), Section 2) Note: Second half of 2020; 430 MeV positrons, about 5.5 × 10^12 positrons on target (arXiv:2603.28685); dark-photon search data. |
| Run III (X17 resonance scan) | run | 2022-10 | 2022-12 | active | verified | https://arxiv.org/abs/2405.07203 (+1 more) “Run III, which took place from October to December 2022” (Bertelli et al. (arXiv:2405.07203), abstract) Note: Positron beam energy scanned between 262 and 296 MeV (√s from 16.4 to 17.4 MeV) in a three-month data-taking period. |

- Host role: `facility:infn-lnf-frascati`: https://padme.lnf.infn.it/ “The PADME experiment (Positron Annihilation into Dark Matter Experiment) at Laboratori Nazionali di Frascati of INFN aims to search for a “Dark Photon” using positron on target collision at the DAΦNE Beam Test Facility.”
- Physics goal: https://padme.lnf.infn.it/ “The experiment is designed to detect dark photon produced in positron on fixed target annihilation (e+e−→γ A) decaying to dark matter by measuring the final state missing mass.”
- Note: PADME uses the positron beam of the DAΦNE linac at the Beam Test Facility (BTF-1), not the DAΦNE collider rings; accelerator:dafne is listed because INFN describes the BTF as part of the DAΦNE complex and no separate linac record exists.
- Note: Kind fixed_target: a positron-on-fixed-target experiment (the 2022 paper calls it 'a fixed target experiment exploiting a positron beam').
- Website `https://padme.lnf.infn.it/`: https://padme.lnf.infn.it/ “The PADME experiment (Positron Annihilation into Dark Matter Experiment) at Laboratori Nazionali di Frascati of INFN aims to search for a “Dark Photon” using positron on target collision at the DAΦNE Beam Test Facility.”

- `detector:padme` (active): technology class `other`; placement `site:infn-lnf-frascati` 2018 to — (approximate): https://padme.lnf.infn.it/ “The PADME experiment (Positron Annihilation into Dark Matter Experiment) at Laboratori Nazionali di Frascati of INFN aims to search for a “Dark Photon” using positron on target collision at the DAΦNE Beam Test Facility.” Note: Campus-grade placement: no fetched source locates the BTF-1 hall; the marker is the LNF campus point. Start year = switching on in 2018.
  Technology: https://arxiv.org/abs/2505.24797 “The electromagnetic calorimeter (ECal) is a matrix of 616 Bismuth Germanate (BGO) crystals refurbished from CERN’s L3 Experiment at LEP”
- `collaboration:padme` (active): host `facility:infn-lnf-frascati`; formation not dated by a source (null); intervals as the experiment's.

Results:

- `result:padme-x17-resonance-search-limit-2025` (limit, 2025-05-30, date kind preprint; experiments experiment:padme): https://arxiv.org/abs/2505.24797 “A blind analysis has been performed. The data are consistent with the expected background in most of the explored energy range, and limits are set in previously unexplored regions of the available parameter space.” Key value: “The most significant deviation is found for s ≈ 16.90 MeV, corresponding to a global significance of approximately 2 standard deviations over the null hypothesis expectation.” (https://arxiv.org/abs/2505.24797).
- `result:padme-ee-to-gg-cross-section-measurement-2022` (measurement, 2022-10-26, date kind preprint; experiments experiment:padme): https://arxiv.org/abs/2210.14603 “This measurement is the first one based on the direct detection of the photon pair and one of the most precise for positron energies below 1 GeV.” Key value: “The measurement agrees with the Next to Leading Order QED prediction within the overall 6% uncertainty.” (https://arxiv.org/abs/2210.14603).

### 2. ADONE (Frascati e+e- collider, 1969-1993) and its experiments

Host `facility:infn-lnf-frascati`, site `site:infn-lnf-frascati` (existing campus point). Experiments are kind `collider`; topics `topic:collider-physics`, `topic:qcd` (plus `topic:hadron-structure` and `topic:charm-physics` where listed in the records). The key source is the INFN-LNF page by M. Preger and F. Murtas, "ADONE (1969-1993)" (Internet Archive capture of lnf.infn.it/acceleratori/adone), an official lab page that names the four first-generation experiments (Gamma-Gamma, Mu-Pion, Boson, BCF), the second-generation ones (Gamma-Gamma 2, MEA, Baryon-Antibaryon) and FENICE.

#### accelerator:adone: ADONE (completed)

Kind `collider`, is_collider True; facility `facility:infn-lnf-frascati`, site `site:infn-lnf-frascati`; particles electron, positron.

| interval | kind | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|---|
| construction | lifecycle | 1963 | 1967 | construction | approximate | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The construction of the new machine began in 1963” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: Year precision. The end is the year the first electron beam was stored ('the end of 1967'). |
| first beams and commissioning | lifecycle | 1967 | 1969 | commissioning | approximate | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ (+1 more) “The first electron beam was stored at the end of 1967.” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: Year precision. The first positron injections met the 'head-tail' instability, cured by a feedback system. Bonolis & Pancheri: ADONE 'started functioning at the end of 1968 and began taking data in 1969'. |
| e+e- collider operation | lifecycle | 1969 | 1993-04-26 | active | approximate | https://www.infn.it/en/infn-offices/laboratories/ (+2 more) “The study of the physics of electron-positron collisions started in 1969 with the ADONE accelerator.” (INFN, Laboratories page (Frascati)) Note: Start at year precision (the LNF history list dates the ADONE entry 17 November 1969, without saying what happened that day). End = shutdown. The ring ran as a collider 1969-1978 and 1990-1993 and as a single-beam source in between. |
| colliding-beam physics, first and second generation experiments | phase | 1969 | 1978 | active | approximate | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The first generation experiments, and successively the second generation ones, explored the physics of electron-positron collisions up to 3.0 GeV in the center of mass, from 1969 to 1978.” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: Year precision. |
| single-beam operation (synchrotron radiation and gamma-ray beams) | phase | 1978 | 1990 | active | approximate | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “In 1990, after several years dedicated to single beam operation for synchrotron radiation and nuclear physics, two beam operation with electrons and positrons was resumed to perform the last subnuclear physics experiment, FENICE, whose data taking lasted until the final shutdown of ADONE in 1993.” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: Year precision. 'After that time [1978] the storage ring was deeply modified' to serve as a synchrotron-radiation source (PULS, PWA) and a gamma-ray source (LADON, Jet Target); two-beam operation resumed in 1990. |
| e+e- operation resumed for FENICE | phase | 1990 | 1993-04-26 | active | approximate | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “In 1990, after several years dedicated to single beam operation for synchrotron radiation and nuclear physics, two beam operation with electrons and positrons was resumed to perform the last subnuclear physics experiment, FENICE, whose data taking lasted until the final shutdown of ADONE in 1993.” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: Year precision for the start; the same page elsewhere says 'in 1991, electron-positron operation was resumed' (see the log). Data taking lasted until the final shutdown. |
| J/psi run beyond the standard parameters | phase | 1974-11 | 1974-11 | active | approximate | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ (+2 more) “However, it was decided to push the performance of the machine beyond its standard parameters, in the energy range indicated by the american laboratories.” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: Month precision from the November 1974 discovery and the PRL received 18 November 1974. The J/psi lies about 0.1 GeV above ADONE's nominal operating energy; the signal appeared 'after three days' (LNF page) or 'in two days' (Bernardini et al.). Era spec cms_energy = about 3.1 GeV (the J/psi peak): https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “characterised by an extraordinary stability for its large mass, ~3.1 GeV” |
| ADONE shut down | lifecycle | 1993-04-26 | — | completed | verified | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “ADONE was shut down on April 26, 1993 to allow the construction of a new low energy, high luminosity collider, DAFNE, inside its building” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: After 24 years of operation (about 22000 hours of colliding beams and 5300 hours of single beams). |

- Spec `beam_energy` = 1.5 GeV per beam (verified): https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The 1.5 GeV per beam, 105 m long storage ring is divided into 12 equal cells” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page)
- Spec `circumference` = 105 m (verified): https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The 1.5 GeV per beam, 105 m long storage ring is divided into 12 equal cells” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: The page says the ring is 105 m long; recorded as the circumference.
- Spec `cms_energy` = 3.0 GeV (verified): https://arxiv.org/abs/1510.00933 “ADONE, the electron-positron collider with 3.0 GeV center of mass energy, was envisaged by Bruno Touschek as soon it became clear that AdA would work.” (Bernardini, Pancheri & Pellegrini, Section VI) Note: Design maximum; the INFN-LNF page says the experiments explored collisions 'up to 3.0 GeV in the center of mass'. About 3.1 GeV was reached for the J/psi in November 1974 (see the phase).
- Spec `injection_energy` = 350 MeV (injector linac) (verified): https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “a 350 MeV Linac, built by Varian (USA), was used as an electron and positron injector” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: The energy of the Varian injector linac.
- Spec `peak_luminosity` = 3 × 10^29 cm^-2 s^-1 (design, per crossing) (verified): https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “the achievement of the design luminosity of 3x10^29 cm^-2 s^-1 per crossing” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: The page states the design luminosity per crossing was achieved.
- Note: The sources fetched give both the design maximum (3.0 GeV centre-of-mass energy) and a brief push to about 3.1 GeV in November 1974 to study the J/psi; the headline value is the 3.0 GeV design maximum and the 1974 run is a dated phase (the energy-frontier chart then draws the headline as the energy 'as recorded today' at the start of operation).
- Note: After 1978 ADONE ran with single beams as a synchrotron-radiation source and a gamma-ray source; photon science is outside the Atlas scope (A26), so those phases are recorded only as dates. Collider running resumed in 1990-1991 for FENICE.
- Note: DAΦNE was built inside the ADONE building after the 1993 shutdown (INFN-LNF page).

#### experiment:adone-gamma-gamma: Gamma-Gamma (ADONE) (completed)

Kind `collider`; facility `facility:infn-lnf-frascati`; accelerators `accelerator:adone`; collaboration `collaboration:adone-gamma-gamma`; topics `topic:collider-physics`, `topic:qcd`.

| interval | kind | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|---|
| ADONE data taking (first generation) | lifecycle | 1969 | 1978 | active | approximate | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The experimental activity on ADONE with colliding beams began in 1969 with four experiments” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: The INFN-LNF page dates the first and second generation experiments together ('from 1969 to 1978'); no source gives this experiment's own end date, so 1978 is the latest possible end and the interval is approximate. |
| data taking ended | lifecycle | 1978 | — | completed | approximate | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The first generation experiments, and successively the second generation ones, explored the physics of electron-positron collisions up to 3.0 GeV in the center of mass, from 1969 to 1978.” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: The INFN-LNF page dates the first and second generation experiments together ('from 1969 to 1978'); no source gives this experiment's own end date, so 1978 is the latest possible end and the interval is approximate. |

- Host role: `facility:infn-lnf-frascati`: https://w3.lnf.infn.it/adone/?lang=en “The higher energy and intensity evolution of AdA, ADONE, started the study of the electron-positron collisions physics in Frascati.”
- Physics goal: https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The "Gamma-Gamma" Experiment (with researchers from Frascati and Rome) had, as a principal goal, the detailed study of reactions with neutral particles in the final state.”

- `detector:adone-gamma-gamma` (completed): technology class `general_purpose_collider`; placement `site:infn-lnf-frascati` 1969 to 1978 (approximate): https://w3.lnf.infn.it/adone/?lang=en “Four out of the 12 avalaible straight sections could host the experimental detectors devoted to the study of the beam collision products.” Note: Campus-grade placement: no fetched source locates the ADONE experimental straight sections; the marker is the LNF campus point. The ADONE building later housed DAΦNE.
  Technology: https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “Its experimental setup included scintillator counters following lead plates for the conversion of the photons and spark chambers to show the produced showers.”
- `collaboration:adone-gamma-gamma` (completed): host `facility:infn-lnf-frascati`; formation not dated by a source (null); intervals as the experiment's.

#### experiment:adone-mu-pion: Mu-Pion (ADONE) (completed)

Kind `collider`; facility `facility:infn-lnf-frascati`; accelerators `accelerator:adone`; collaboration `collaboration:adone-mu-pion`; topics `topic:collider-physics`, `topic:qcd`, `topic:hadron-structure`.

| interval | kind | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|---|
| ADONE data taking (first generation) | lifecycle | 1969 | 1978 | active | approximate | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The experimental activity on ADONE with colliding beams began in 1969 with four experiments” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: The INFN-LNF page dates the first and second generation experiments together ('from 1969 to 1978'); no source gives this experiment's own end date, so 1978 is the latest possible end and the interval is approximate. |
| data taking ended | lifecycle | 1978 | — | completed | approximate | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The first generation experiments, and successively the second generation ones, explored the physics of electron-positron collisions up to 3.0 GeV in the center of mass, from 1969 to 1978.” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: The INFN-LNF page dates the first and second generation experiments together ('from 1969 to 1978'); no source gives this experiment's own end date, so 1978 is the latest possible end and the interval is approximate. |

- Host role: `facility:infn-lnf-frascati`: https://w3.lnf.infn.it/adone/?lang=en “The higher energy and intensity evolution of AdA, ADONE, started the study of the electron-positron collisions physics in Frascati.”
- Physics goal: https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The "Mu-Pion" Experiment (Frascati, Rome, Padua) was mainly dedicated to production of muon, pion and K meson pairs from the electron-positron annihilation.”

- `detector:adone-mu-pion` (completed): technology class `general_purpose_collider`; placement `site:infn-lnf-frascati` 1969 to 1978 (approximate): https://w3.lnf.infn.it/adone/?lang=en “Four out of the 12 avalaible straight sections could host the experimental detectors devoted to the study of the beam collision products.” Note: Campus-grade placement: no fetched source locates the ADONE experimental straight sections; the marker is the LNF campus point. The ADONE building later housed DAΦNE.
  Technology: https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The setup consisted of scintillation counters, spark chambers seen from above by means of characteristic long mirrors and water Cerenkov counters to separate the pions from K mesons.”
- `collaboration:adone-mu-pion` (completed): host `facility:infn-lnf-frascati`; formation not dated by a source (null); intervals as the experiment's.

#### experiment:adone-boson: Boson (ADONE) (completed)

Kind `collider`; facility `facility:infn-lnf-frascati`; accelerators `accelerator:adone`; collaboration `collaboration:adone-boson`; topics `topic:collider-physics`, `topic:qcd`, `topic:hadron-structure`.

| interval | kind | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|---|
| ADONE data taking (first generation) | lifecycle | 1969 | 1978 | active | approximate | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The experimental activity on ADONE with colliding beams began in 1969 with four experiments” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: The INFN-LNF page dates the first and second generation experiments together ('from 1969 to 1978'); no source gives this experiment's own end date, so 1978 is the latest possible end and the interval is approximate. |
| data taking ended | lifecycle | 1978 | — | completed | approximate | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The first generation experiments, and successively the second generation ones, explored the physics of electron-positron collisions up to 3.0 GeV in the center of mass, from 1969 to 1978.” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: The INFN-LNF page dates the first and second generation experiments together ('from 1969 to 1978'); no source gives this experiment's own end date, so 1978 is the latest possible end and the interval is approximate. |

- Host role: `facility:infn-lnf-frascati`: https://w3.lnf.infn.it/adone/?lang=en “The higher energy and intensity evolution of AdA, ADONE, started the study of the electron-positron collisions physics in Frascati.”
- Physics goal: https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The "Boson" Experiment , run by physicists from Frascati, Naples, Pavia and Rome, employed a very compact setup, made of scintillators and wire magnetostrictive chambers, well suited to detect charged particle final states under the maximum solid angle.”
- Note: The INFN-LNF page: 'The first evidence of an anomalous multiple production came in 1970 from the measurements of the "boson" experiment.' (a result record was not written: no publication abstract was fetchable).
- Note: Its place on the interaction straight section was later taken by the 'proton-antiproton' experiment of a Naples group; the page does not date this and the Baryon-Antibaryon experiment is recorded separately.

- `detector:adone-boson` (completed): technology class `general_purpose_collider`; placement `site:infn-lnf-frascati` 1969 to 1978 (approximate): https://w3.lnf.infn.it/adone/?lang=en “Four out of the 12 avalaible straight sections could host the experimental detectors devoted to the study of the beam collision products.” Note: Campus-grade placement: no fetched source locates the ADONE experimental straight sections; the marker is the LNF campus point. The ADONE building later housed DAΦNE.
  Technology: https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The "Boson" Experiment , run by physicists from Frascati, Naples, Pavia and Rome, employed a very compact setup, made of scintillators and wire magnetostrictive chambers, well suited to detect charged particle final states under the maximum solid angle.”
- `collaboration:adone-boson` (completed): host `facility:infn-lnf-frascati`; formation not dated by a source (null); intervals as the experiment's.

#### experiment:adone-bcf: BCF (completed)

Kind `collider`; facility `facility:infn-lnf-frascati`; accelerators `accelerator:adone`; collaboration `collaboration:adone-bcf`; topics `topic:collider-physics`, `topic:qcd`, `topic:hadron-structure`.

| interval | kind | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|---|
| ADONE data taking (first generation) | lifecycle | 1969 | 1978 | active | approximate | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The experimental activity on ADONE with colliding beams began in 1969 with four experiments” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: The INFN-LNF page dates the first and second generation experiments together ('from 1969 to 1978'); no source gives this experiment's own end date, so 1978 is the latest possible end and the interval is approximate. |
| data taking ended | lifecycle | 1978 | — | completed | approximate | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The first generation experiments, and successively the second generation ones, explored the physics of electron-positron collisions up to 3.0 GeV in the center of mass, from 1969 to 1978.” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: The INFN-LNF page dates the first and second generation experiments together ('from 1969 to 1978'); no source gives this experiment's own end date, so 1978 is the latest possible end and the interval is approximate. |

- Host role: `facility:infn-lnf-frascati`: https://w3.lnf.infn.it/adone/?lang=en “The higher energy and intensity evolution of AdA, ADONE, started the study of the electron-positron collisions physics in Frascati.”
- Physics goal: https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The main goals of the BCF (Bologna, CERN, Frascati) were the measurement of the pion and K mesons form factors, and the search for heavy leptons.”
- Note: The INFN-LNF page: 'The final demonstration came in 1971 from the BCF group.' that the anomalous multiple production was hadronic (no publication abstract was fetchable).

- `detector:adone-bcf` (completed): technology class `general_purpose_collider`; placement `site:infn-lnf-frascati` 1969 to 1978 (approximate): https://w3.lnf.infn.it/adone/?lang=en “Four out of the 12 avalaible straight sections could host the experimental detectors devoted to the study of the beam collision products.” Note: Campus-grade placement: no fetched source locates the ADONE experimental straight sections; the marker is the LNF campus point. The ADONE building later housed DAΦNE.
  Technology: https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “Particular care had been paid to the calibration of the detectors, in order to guarantee a good particle identification by a system scintillation counters and spark chambers.”
- `collaboration:adone-bcf` (completed): host `facility:infn-lnf-frascati`; formation not dated by a source (null); intervals as the experiment's.

#### experiment:adone-gamma-gamma-2: Gamma-Gamma 2 (ADONE) (completed)

Kind `collider`; facility `facility:infn-lnf-frascati`; accelerators `accelerator:adone`; collaboration `collaboration:adone-gamma-gamma`; topics `topic:collider-physics`, `topic:qcd`.

| interval | kind | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|---|
| ADONE data taking (second generation) | lifecycle | 1974 | 1978 | active | uncertain | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ (+1 more) “The second generation detectors at ADONE had unique features to identify some peculiar aspects of the new particle, and in this way they were able to give significant contributions to the measurement of its properties.” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: No source dates the start of the second-generation detectors. The 1974 Phys. Rev. Lett. paper (received 18 November 1974) is signed by this group and the INFN-LNF page says the second-generation detectors contributed to the J/psi measurements, so the detector was operating by November 1974; 1974 is the latest possible start and the confidence is uncertain. End: The INFN-LNF page dates the first and second generation experiments together ('from 1969 to 1978'); no source gives this experiment's own end date, so 1978 is the latest possible end and the interval is approximate. |
| data taking ended | lifecycle | 1978 | — | completed | approximate | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The first generation experiments, and successively the second generation ones, explored the physics of electron-positron collisions up to 3.0 GeV in the center of mass, from 1969 to 1978.” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: The INFN-LNF page dates the first and second generation experiments together ('from 1969 to 1978'); no source gives this experiment's own end date, so 1978 is the latest possible end and the interval is approximate. |
| J/psi confirmation run | run | 1974-11 | 1974-11 | active | approximate | https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.33.1408 “We report on the results at ADONE to study the properties of the newly found 3.1-BeV particle.” (Phys. Rev. Lett. 33, 1408 (1974), abstract; received 18 November 1974) Note: Month precision: the J/psi was announced in November 1974 and the paper was received on 18 November 1974. |

- Host role: `facility:infn-lnf-frascati`: https://w3.lnf.infn.it/adone/?lang=en “The higher energy and intensity evolution of AdA, ADONE, started the study of the electron-positron collisions physics in Frascati.”
- Lineage: `upgrade_of` `experiment:adone-gamma-gamma`: https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The Gamma-Gamma 2 Experiment was the natural development of the Gamma-Gamma Detector”
- Physics goal: https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The Gamma-Gamma 2 Experiment was the natural development of the Gamma-Gamma Detector (scintillation counters, converters and spark chambers), covering a larger solid angle with a better sampling of electromagnetic and hadronic showers.”
- Note: The 1974 Phys. Rev. Lett. paper is signed 'The Gamma-Gamma Group'; the INFN-LNF page says the second-generation detectors contributed to the J/psi measurements, so the paper is attributed to Gamma-Gamma 2.

- `detector:adone-gamma-gamma-2` (completed): technology class `general_purpose_collider`; placement `site:infn-lnf-frascati` 1974 to 1978 (approximate): https://w3.lnf.infn.it/adone/?lang=en “Four out of the 12 avalaible straight sections could host the experimental detectors devoted to the study of the beam collision products.” Note: Campus-grade placement: no fetched source locates the ADONE experimental straight sections; the marker is the LNF campus point. The ADONE building later housed DAΦNE. Start year is the latest possible start (see the experiment record).
  Technology: https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The Gamma-Gamma 2 Experiment was the natural development of the Gamma-Gamma Detector (scintillation counters, converters and spark chambers), covering a larger solid angle with a better sampling of electromagnetic and hadronic showers.”


#### experiment:adone-mea: MEA (completed)

Kind `collider`; facility `facility:infn-lnf-frascati`; accelerators `accelerator:adone`; collaboration `collaboration:adone-mea`; topics `topic:collider-physics`, `topic:qcd`, `topic:hadron-structure`.

| interval | kind | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|---|
| ADONE data taking (second generation) | lifecycle | 1974 | 1978 | active | uncertain | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ (+1 more) “The second generation detectors at ADONE had unique features to identify some peculiar aspects of the new particle, and in this way they were able to give significant contributions to the measurement of its properties.” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: No source dates the start of the second-generation detectors. The 1974 Phys. Rev. Lett. paper (received 18 November 1974) is signed by this group and the INFN-LNF page says the second-generation detectors contributed to the J/psi measurements, so the detector was operating by November 1974; 1974 is the latest possible start and the confidence is uncertain. End: The INFN-LNF page dates the first and second generation experiments together ('from 1969 to 1978'); no source gives this experiment's own end date, so 1978 is the latest possible end and the interval is approximate. |
| data taking ended | lifecycle | 1978 | — | completed | approximate | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The first generation experiments, and successively the second generation ones, explored the physics of electron-positron collisions up to 3.0 GeV in the center of mass, from 1969 to 1978.” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: The INFN-LNF page dates the first and second generation experiments together ('from 1969 to 1978'); no source gives this experiment's own end date, so 1978 is the latest possible end and the interval is approximate. |
| J/psi confirmation run | run | 1974-11 | 1974-11 | active | approximate | https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.33.1408 “We report on the results at ADONE to study the properties of the newly found 3.1-BeV particle.” (Phys. Rev. Lett. 33, 1408 (1974), abstract; received 18 November 1974) Note: Month precision: the J/psi was announced in November 1974 and the paper was received on 18 November 1974. |

- Host role: `facility:infn-lnf-frascati`: https://w3.lnf.infn.it/adone/?lang=en “The higher energy and intensity evolution of AdA, ADONE, started the study of the electron-positron collisions physics in Frascati.”
- Physics goal: https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “In particular, the requirement of a complete analysis of the final states particle properties asked for a detector placed in a magnetic field to discriminate the charge and measure the particle momentum.”
- Note: Greco (arXiv:2502.09671, arXiv:2201.00775) cites an 'MEA Group' paper from 1970 (Nuovo Cimento A 70, 615) among the first multihadron results; the INFN-LNF page describes MEA as a second-generation detector, so this record follows the INFN-LNF page and the 1970 attribution is left unresolved.

- `detector:adone-mea` (completed): technology class `general_purpose_collider`; placement `site:infn-lnf-frascati` 1974 to 1978 (approximate): https://w3.lnf.infn.it/adone/?lang=en “Four out of the 12 avalaible straight sections could host the experimental detectors devoted to the study of the beam collision products.” Note: Campus-grade placement: no fetched source locates the ADONE experimental straight sections; the marker is the LNF campus point. The ADONE building later housed DAΦNE. Start year is the latest possible start (see the experiment record).
  Technology: https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “researchers from Frascati, Naples, Padua and Rome realised MEA (Magnete Esperienze Adone), a detector made of large gap chambers and spark chambers, placed inside a large solenoidal magnet.”
- `collaboration:adone-mea` (completed): host `facility:infn-lnf-frascati`; formation not dated by a source (null); intervals as the experiment's.

#### experiment:adone-baryon-antibaryon: Baryon-Antibaryon (ADONE) (completed)

Kind `collider`; facility `facility:infn-lnf-frascati`; accelerators `accelerator:adone`; collaboration `collaboration:adone-baryon-antibaryon`; topics `topic:collider-physics`, `topic:qcd`, `topic:hadron-structure`.

| interval | kind | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|---|
| ADONE data taking (second generation) | lifecycle | 1974 | 1978 | active | uncertain | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ (+1 more) “The second generation detectors at ADONE had unique features to identify some peculiar aspects of the new particle, and in this way they were able to give significant contributions to the measurement of its properties.” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: No source dates the start of the second-generation detectors. The 1974 Phys. Rev. Lett. paper (received 18 November 1974) is signed by this group and the INFN-LNF page says the second-generation detectors contributed to the J/psi measurements, so the detector was operating by November 1974; 1974 is the latest possible start and the confidence is uncertain. End: The INFN-LNF page dates the first and second generation experiments together ('from 1969 to 1978'); no source gives this experiment's own end date, so 1978 is the latest possible end and the interval is approximate. |
| data taking ended | lifecycle | 1978 | — | completed | approximate | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The first generation experiments, and successively the second generation ones, explored the physics of electron-positron collisions up to 3.0 GeV in the center of mass, from 1969 to 1978.” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: The INFN-LNF page dates the first and second generation experiments together ('from 1969 to 1978'); no source gives this experiment's own end date, so 1978 is the latest possible end and the interval is approximate. |
| J/psi confirmation run | run | 1974-11 | 1974-11 | active | approximate | https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.33.1408 “We report on the results at ADONE to study the properties of the newly found 3.1-BeV particle.” (Phys. Rev. Lett. 33, 1408 (1974), abstract; received 18 November 1974) Note: Month precision: the J/psi was announced in November 1974 and the paper was received on 18 November 1974. |

- Host role: `facility:infn-lnf-frascati`: https://w3.lnf.infn.it/adone/?lang=en “The higher energy and intensity evolution of AdA, ADONE, started the study of the electron-positron collisions physics in Frascati.”
- Physics goal: https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The Baryon-Antibaryon Experiment was designed to study proton-antiproton and, more generally, any baryon-antibaryon pair, similar to protons, but with a larger mass, looking mainly at the energy threshold of the reaction.”
- Note: The INFN-LNF page also lists a first-generation 'proton-antiproton' experiment of a Naples group that took the place of Boson; it does not say whether this is the same group or experiment, and none is recorded separately.

- `detector:adone-baryon-antibaryon` (completed): technology class `general_purpose_collider`; placement `site:infn-lnf-frascati` 1974 to 1978 (approximate): https://w3.lnf.infn.it/adone/?lang=en “Four out of the 12 avalaible straight sections could host the experimental detectors devoted to the study of the beam collision products.” Note: Campus-grade placement: no fetched source locates the ADONE experimental straight sections; the marker is the LNF campus point. The ADONE building later housed DAΦNE. Start year is the latest possible start (see the experiment record).
  Technology: https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The detector consisted in large liquid scintillators, wire chambers with magnetostrictive reading and flash tube chambers.”
- `collaboration:adone-baryon-antibaryon` (completed): host `facility:infn-lnf-frascati`; formation not dated by a source (null); intervals as the experiment's.

#### experiment:fenice: FENICE (completed)

Kind `collider`; facility `facility:infn-lnf-frascati`; accelerators `accelerator:adone`; collaboration `collaboration:fenice`; topics `topic:collider-physics`, `topic:qcd`, `topic:hadron-structure`.

| interval | kind | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|---|
| ADONE two-beam data taking for FENICE | lifecycle | 1990 | 1993-04-26 | active | approximate | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “In 1990, after several years dedicated to single beam operation for synchrotron radiation and nuclear physics, two beam operation with electrons and positrons was resumed to perform the last subnuclear physics experiment, FENICE, whose data taking lasted until the final shutdown of ADONE in 1993.” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: Year precision for the start. The same page says elsewhere that 'in 1991, electron-positron operation was resumed to study neutron-antineutron production ... (FENICE experiment)'; 1990 is taken from the sentence that dates the two-beam resumption and the FENICE data taking. The end is the ADONE shutdown on 26 April 1993. |
| data taking ended | lifecycle | 1993-04-26 | — | completed | verified | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “ADONE was shut down on April 26, 1993 to allow the construction of a new low energy, high luminosity collider, DAFNE, inside its building” (Preger & Murtas, ADONE (1969-1993), INFN-LNF page) Note: FENICE data taking 'lasted until the final shutdown of ADONE in 1993'. |

- Host role: `facility:infn-lnf-frascati`: https://w3.lnf.infn.it/adone/?lang=en “The higher energy and intensity evolution of AdA, ADONE, started the study of the electron-positron collisions physics in Frascati.”
- Physics goal: https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ “The FENICE experiment's goal is to overcome a gap in our knowledge about the internal structure of the neutron, by measuring its electromagnetic form factor through the reaction electron + positron -> neutron + antineutron.”
- Note: The INFN-LNF page calls FENICE 'the last subnuclear physics experiment' at ADONE.
- Note: No publication abstract was fetchable (Elsevier pages return 403), so no result record was written.

- `detector:fenice` (completed): technology class `general_purpose_collider`; placement `site:infn-lnf-frascati` 1990 to 1993-04-26 (approximate): https://w3.lnf.infn.it/adone/?lang=en “Four out of the 12 avalaible straight sections could host the experimental detectors devoted to the study of the beam collision products.” Note: Campus-grade placement: no fetched source locates the ADONE experimental straight sections; the marker is the LNF campus point. The ADONE building later housed DAΦNE.
  Technology: null (not described in the sources fetched).
- `collaboration:fenice` (completed): host `facility:infn-lnf-frascati`; formation not dated by a source (null); intervals as the experiment's.

Results:

- `result:adone-new-3-1-gev-particle-properties-measurement-1974` (measurement, 1974-12-02, date kind publication; experiments experiment:adone-gamma-gamma-2, experiment:adone-mea, experiment:adone-baryon-antibaryon): https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.33.1408 “We report on the results at ADONE to study the properties of the newly found 3.1-BeV particle.” Key value: none.

### 3a. STCF (Super Tau-Charm Facility, Hefei, China; proposed)

The host site is named by the STCF working group's talks (Hefei, 'Future Big Science City'; three candidate sites under geological exploration), not by the design reports, which name the Hefei city government and USTC as supporters; STREAM_RULES accepts a collaboration document. A new project-level facility and an area-marker site were created (owner colliders-2). No detector placement was written (see "For the integrator"). Topics `topic:collider-physics`, `topic:charm-physics`, `topic:hadron-structure`, `topic:flavor-physics`.

#### facility:stcf-hefei: Super Tau-Charm Facility site, Hefei (proposed) (proposed, accelerator_laboratory)

| interval | kind | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|---|
| STCF project (proposed 2011; Hefei named as the site in the project documents) | lifecycle | 2011-12 | — | proposed | approximate | https://indico.cern.ch/event/1595459/contributions/7058138/attachments/3288802/5879910/STCF_beauy2026v2.pdf (+1 more) “Proposed at “workshop for acc. Based high energy physics development strategy”” (Zhang (2026), slide 'Promotion of the program') Note: Start = the month the STCF was proposed (2011.12); the facility record starts with the project because the proposed collider and its experiment start then. The documents name Hefei as the host: the Anhui and Hefei governments launched the key-technology R&D in April 2022 ('Government of Anhui Province and Hefei City Launch the STCF Key Technology R&D', Zheng 2024), and the host city is not dated earlier in the sources fetched. Proposed, not approved. |

#### site:stcf-hefei-future-big-science-city: Hefei Future Big Science City (STCF project area)

Facility `facility:stcf-hefei`; coordinates 31.9630359, 117.1248532 (kind campus, approximate): https://nominatim.openstreetmap.org/search?q=%E5%90%88%E8%82%A5%E5%85%88%E8%BF%9B%E5%85%89%E6%BA%90&format=json&limit=5&addressdetails=0 “"lat":"31.9630359","lon":"117.1248532"” () Note: Area marker, not the STCF site: the project documents name only the Hefei 'Future Big Science City' and show three candidate sites under geological exploration (final site not selected). The point is the OpenStreetMap polygon of the Hefei Advanced Light Facility (HALF), which the project slides place in the same Future Big Science City next to the candidate sites; precision about 5 km.

#### accelerator:stcf: Super Tau-Charm Facility (STCF) (proposed)

Kind `collider`, is_collider True; facility `facility:stcf-hefei`, site `site:stcf-hefei-future-big-science-city`; particles electron, positron.

| interval | kind | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|---|
| proposal and design studies | lifecycle | 2011-12 | — | proposed | approximate | https://indico.cern.ch/event/1595459/contributions/7058138/attachments/3288802/5879910/STCF_beauy2026v2.pdf (+1 more) “Proposed at “workshop for acc. Based high energy physics development strategy”” (Zhang (2026), slide 'Promotion of the program') Note: Month from the 2026 project talk (2011.12); Physics World says it was first proposed in 2011 by Zhao Guangda. Design documents: Physics & Detector CDR (arXiv:2303.15790, 2023), accelerator CDR (arXiv:2509.11522, 2025). The accelerator CDR 'aims to secure support from the Chinese central government for its construction during the 15th Five-Year Plan (2026-2030)'; the June 2026 talk says the proposal was submitted in 2025 and defended for inclusion in that plan. No approval is reported in the sources fetched (as of 2026-10-26). |

- Spec `circumference` = about 860 m (collider ring) (verified): https://arxiv.org/abs/2509.11522 “The STCF collider is a dual-ring machine with a circumference of about 860 m.” (Accelerator CDR (arXiv:2509.11522), Section 4.1.4.1) Note: Collider ring; the talks give 800 to 1000 m for earlier layouts.
- Spec `cms_energy` = 7 GeV (upper end of the 2 to 7 GeV design range) (verified): https://arxiv.org/abs/2509.11522 “The main design goals of STCF are with a center-of-mass energy ranging from 2 to 7 GeV and a peak luminosity surpassing 5 × 10³⁴ cm⁻²s⁻¹ that is optimized at a center-of-mass energy of 4 GeV” (Accelerator CDR (arXiv:2509.11522), abstract) Note: Upper end of the design range of 2 to 7 GeV.
- Spec `peak_luminosity` = above 5 × 10^34 cm^-2 s^-1 (design goal at 4 GeV) (verified): https://arxiv.org/abs/2509.11522 “The main design goals of STCF are with a center-of-mass energy ranging from 2 to 7 GeV and a peak luminosity surpassing 5 × 10³⁴ cm⁻²s⁻¹ that is optimized at a center-of-mass energy of 4 GeV” (Accelerator CDR (arXiv:2509.11522), abstract) Note: A design goal ('surpassing'); the accelerator CDR's lattice studies also give about 1 × 10^35 cm^-2 s^-1 at a beam energy of 2 GeV.
- Note: The Atlas marker is an area point in Hefei's Future Big Science City: the project talks name the city district as the site (about 1 km²) and show three candidate sites under geological exploration, so no tunnel site has been selected.
- Note: The accelerator CDR says construction would 'commence as planned in 2027 or 2028' if approved; that is a plan, recorded here as a note, not as an interval.
- Note: Budget figures in the project talks (about 4.5 to 4.98 billion CNY for construction, 364 to 400 million CNY for the key-technology R&D) are not recorded as specs.

#### experiment:stcf: STCF (proposed)

Kind `collider`; facility `facility:stcf-hefei`; accelerators `accelerator:stcf`; collaboration `collaboration:stcf`; topics `topic:collider-physics`, `topic:charm-physics`, `topic:hadron-structure`, `topic:flavor-physics`.

| interval | kind | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|---|
| proposal and design studies | lifecycle | 2011-12 | — | proposed | approximate | https://indico.cern.ch/event/1595459/contributions/7058138/attachments/3288802/5879910/STCF_beauy2026v2.pdf (+1 more) “Proposed at “workshop for acc. Based high energy physics development strategy”” (Zhang (2026), slide 'Promotion of the program') Note: Month from the 2026 project talk (2011.12); Physics World says it was first proposed in 2011 by Zhao Guangda. Design documents: Physics & Detector CDR (arXiv:2303.15790, 2023), accelerator CDR (arXiv:2509.11522, 2025). The accelerator CDR 'aims to secure support from the Chinese central government for its construction during the 15th Five-Year Plan (2026-2030)'; the June 2026 talk says the proposal was submitted in 2025 and defended for inclusion in that plan. No approval is reported in the sources fetched (as of 2026-10-26). |

- Host role: `facility:stcf-hefei`: https://lpsc-indico.in2p3.fr/event/3268/contributions/7444/attachments/5299/8254/STCF-Overview.pdf “Site: Suburban "Future Big Science City” in Hefei”
- Lineage: `predecessor` `experiment:bes-iii`: https://physicsworld.com/a/china-mulls-plan-to-build-a-640m-super-tau-charm-factory/ “The STCF is seen as a natural successor to the Beijing Electron Positron Collider (BEPC)”
- Physics goal: https://arxiv.org/abs/2303.15790 “providing a unique platform for exploring the asymmetry of matterantimatter (charge-parity violation), in-depth studies of the internal structure of hadrons and the nature of non-perturbative strong interactions, as well as searching for exotic hadrons and physics beyond the Standard Model.”
- Note: Proposed only: the 2023 Physics & Detector CDR and the 2025 accelerator CDR are design reports; the host site (Hefei Future Big Science City) is named by the STCF working group's talks, not by a decision. No approval is reported in the sources fetched.

- `detector:stcf` (proposed): technology class `general_purpose_collider`; no placement recorded (A concept: no detector has been built. No placement is recorded: the host area (Hefei Future Big Science City) has no hall position, and a placement on the area-marker site would add an A23 approximate-coordinate warning; the experiment is located through facility:stcf-hefei and accelerator:stcf.)
  Technology: https://arxiv.org/abs/2303.15790 “consisting of three cylindrical layers located 6, 11 and 16 cm away from the interaction point, is proposed as a baseline option for the inner tracker”
- `collaboration:stcf` (proposed): host `facility:infn-lnf-frascati`; formation not dated by a source (null); intervals as the experiment's.

### 3b. SCTF (Super Charm-Tau Factory, BINP Novosibirsk; proposed)

Host `facility:binp-novosibirsk` / `site:binp-novosibirsk-akademgorodok` (existing campus point). The very preliminary 2018 conceptual design report (two parts) names 'a project of the Super Charm-Tau factory in the Budker Institute of Nuclear Physics (Novosibirsk, Russia)'. Topics as for STCF.

#### accelerator:sctf: Super Charm-Tau Factory (SCTF) (proposed)

Kind `collider`, is_collider True; facility `facility:binp-novosibirsk`, site `site:binp-novosibirsk-akademgorodok`; particles electron, positron.

| interval | kind | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|---|
| Super Charm-Tau factory project at BINP | lifecycle | 2018 | — | proposed | approximate | https://ctd.inp.nsk.su/wiki/images/4/47/CDR2_ScTau_en_vol1.pdf (+3 more) “CONCEPTUAL DESIGN REPORT PART ONE (physics program, detector) [very preliminary draft] Novosibirsk 2018” (SCTF Conceptual Design Report, Part One, title page) Note: Start = the 2018 conceptual design report (a 'very preliminary draft'); earlier tau-charm factory studies at BINP are cited in it (SLAC-Report-451, 1994; a 1995 'C-Tau in Novosibirsk' CDR) but are a different design. In 2020 BINP was still 'developing a Super Charm-Tau factory project' (arXiv:2005.09878). No approval, funding or construction is reported in the sources fetched, and none is dated after 2020; the project status as of 2026-10-26 is not confirmed. |

- Spec `cms_energy` = 5 GeV (upper end of the 2 to 5 GeV design range) (verified): https://ctd.inp.nsk.su/wiki/images/4/47/CDR2_ScTau_en_vol1.pdf “An electron-positron collider will operate in the range of center-of-mass energies from 2 to 5 GeV with unprecedented peak luminosity of about 1035 cm−2 c−1 and longitudinally polarized electrons at interaction point.” (SCTF CDR Part One, abstract) Note: Upper end of the design range; the same sentence gives a peak luminosity of about 10^35 cm^-2 s^-1 (not recorded as a spec because the PDF text prints the exponent as '1035').
- Note: The Atlas marker is the BINP campus: the 2018 CDR places the project 'in the Budker Institute of Nuclear Physics (Novosibirsk, Russia)' without a more precise site, so no tunnel site is recorded.
- Note: Parameters differ between documents: the 2018 CDR gives 2 to 5 GeV; the BINP project page also 2 to 5 GeV; a 2020 JINST conference paper (arXiv:2005.09878) says 2 to 7 GeV. The record follows the CDR.

#### experiment:sctf: SCTF (proposed)

Kind `collider`; facility `facility:binp-novosibirsk`; accelerators `accelerator:sctf`; collaboration ; topics `topic:collider-physics`, `topic:charm-physics`, `topic:hadron-structure`, `topic:flavor-physics`.

| interval | kind | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|---|
| Super Charm-Tau factory project at BINP | lifecycle | 2018 | — | proposed | approximate | https://ctd.inp.nsk.su/wiki/images/4/47/CDR2_ScTau_en_vol1.pdf (+3 more) “CONCEPTUAL DESIGN REPORT PART ONE (physics program, detector) [very preliminary draft] Novosibirsk 2018” (SCTF Conceptual Design Report, Part One, title page) Note: Start = the 2018 conceptual design report (a 'very preliminary draft'); earlier tau-charm factory studies at BINP are cited in it (SLAC-Report-451, 1994; a 1995 'C-Tau in Novosibirsk' CDR) but are a different design. In 2020 BINP was still 'developing a Super Charm-Tau factory project' (arXiv:2005.09878). No approval, funding or construction is reported in the sources fetched, and none is dated after 2020; the project status as of 2026-10-26 is not confirmed. |

- Host role: `facility:binp-novosibirsk`: https://ctd.inp.nsk.su/wiki/images/4/47/CDR2_ScTau_en_vol1.pdf “This document is focused on a project of the Super Charm Tau factory in the Budker Institute of Nuclear Physics (Novosibirsk, Russia).”
- Physics goal: https://ctd.inp.nsk.su/c-tau/ “The main purpose of the experiments at the collider is search for effects of CP-violation in the decays of charmed particles, tests of the Standard Model in the decay of the tau lepton, the search and study of an entirely new form of matter: glueballs, hybrids, etc.”
- Note: No collaboration record exists: the CDR author list (about 150 names at BINP, Novosibirsk State University, Sobolev Institute, Boreskov Institute of Catalysis and others) is a project team, and no named collaboration was found.
- Note: The BINP project page and CDR describe the project as the BINP response to the high-luminosity B factories and to the crab-waist collision scheme; no successor relation to an existing Atlas experiment is stated.

- `detector:sctf` (proposed): technology class `general_purpose_collider`; placement `site:binp-novosibirsk-akademgorodok` — to — (approximate): https://ctd.inp.nsk.su/wiki/images/4/47/CDR2_ScTau_en_vol1.pdf “This document is focused on a project of the Super Charm Tau factory in the Budker Institute of Nuclear Physics (Novosibirsk, Russia).” Note: Campus-grade placement: the CDR names the Budker Institute (Novosibirsk) but no hall or tunnel position; the marker is the BINP campus point.
  Technology: https://ctd.inp.nsk.su/c-tau/ “Realisation of the program will require the physical development of a universal magnetic detector with high momentum resolution for charged particles”


## Conflicts

| claim | source A | source B | chosen | why |
|---|---|---|---|---|
| FINUDA first run, start | FINUDA collaboration (arXiv:nucl-ex/0506028): "started in December 2003" | Franzini & Moulson (arXiv:hep-ex/0606033): "began in November 2003" | 2003-12 | The collaboration's own paper; the review is a secondary account. The month difference is stated in the interval note. |
| FINUDA second run, start | FINUDA collaboration (arXiv:1011.2695): "from November 2006 to June 2007" | Milardi (arXiv:0803.1450): "started in April 2006" | 2006-11 | The collaboration's own dates; the 2008 accelerator report, and the 2006 review (which expected the run to resume "during summer 2006"), describe machine schedules. |
| DEAR physics data | Franzini & Moulson: "DEAR took physics data in 2002"; Di Falco (hep-ex/0311006): "concluded in 2002" | Milardi (arXiv:0803.1450): "less than 5 months during 2002-2003" | 2002 (year precision) | Two sources agree on 2002; the dates are marked approximate. |
| ADONE first beams | INFN-LNF page: "The first electron beam was stored at the end of 1967." | Bonolis & Pancheri (arXiv:1511.00453): "ADONE started functioning at the end of 1968 and began taking data in 1969." | both used | Different milestones (first stored electron beam; working two-beam machine); the LNF page adds that positron storage was held up by the head-tail instability. Commissioning is recorded 1967 to 1969 (year precision). |
| FENICE / e+e- operation resumed | INFN-LNF page: "In 1990 ... two beam operation with electrons and positrons was resumed" | same page: "in 1991, electron-positron operation was resumed" | 1990 | The 1990 sentence also dates the FENICE data taking; the 1991 sentence sits in the machine summary. Approximate in both the accelerator phase and the experiment. |
| J/psi run duration at ADONE | INFN-LNF page: "After three days the signal of the new particle appeared" | Bernardini, Pancheri & Pellegrini (arXiv:1510.00933): "ADONE in two days reached it" | month precision (November 1974) | Only the month is recorded. |
| MEA first paper | Greco (arXiv:2502.09671, arXiv:2201.00775) cites an "MEA Group" paper of 1970 (Nuovo Cimento A 70, 615) among the first multihadron results | INFN-LNF page: MEA (Magnete Esperienze Adone) is a second-generation detector | INFN-LNF page | The attribution of the 1970 paper is left unresolved; MEA is dated as a second-generation experiment (start uncertain). |
| SCTF energy range | BINP CDR (2018) and project page: 2 to 5 GeV | Vadakeppattu et al. (arXiv:2005.09878, 2020): "2-7 GeV"; a 2018 eeFACT proceeding (search snippet only, not fetched) said 2 to 6 GeV | 2 to 5 GeV | The CDR is the design report; the later paper is an instrumentation talk. |
| STCF collaboration size | Physics World: about 500 scientists from 74 institutes | project talk: 82 institutions, 453 authors on the Physics & Detector CDR; arXiv lists 438 authors | all three stated in the collaboration note | Different dates and counting rules. |

## Unresolved

- FINUDA, DEAR, SIDDHARTA: no official collaboration website was reachable (the old LNF experiment pages time out or return 404), so `links.website` is null. SIDDHARTA-2's website is the INFN-LNF KAONNIS page (undated; its plans refer to 2020-2021).
- FINUDA: no approval, construction or installation dates were found; the interval before the first run is only "proposed" from 1993. DEAR: the proposal-to-test-run interval is bounded by two year-precision dates.
- SIDDHARTA: the months of the six-month 2009 run are not given in the sources fetched (only October 2009 for deuterium); construction end is inferred.
- SIDDHARTA-2: the kaonic deuterium result has not been published in the sources fetched; the experiment's collaboration roster was not retrieved.
- DAΦNE detector hall positions: no source locates the DAΦNE interaction regions or the BTF-1 hall, so all placements use the existing LNF campus point (approximate).
- Collaboration formation dates: FINUDA 1993 and DEAR 1995 are proposal years used as approximate lower bounds; all other collaborations are null.
- ADONE experiments: no per-experiment end date is published in the sources fetched; the INFN-LNF page dates the first and second generation experiments together ("from 1969 to 1978"), so 1978 is the latest possible end and every ADONE experiment end is approximate. The second-generation experiments (Gamma-Gamma 2, MEA, Baryon-Antibaryon) have no dated start: they were operating by November 1974 (PRL 33, 1408), and 1974 is recorded as the latest possible start with confidence `uncertain`.
- ADONE: the January 1963 construction start and the 26 April 1993 shutdown appear in a CERN Courier note ("Adieu ADONE", an INIS record that returns HTTP 403); the LNF page gives 1963 and 26 April 1993 directly, so nothing relies on the Courier. No official website exists for any ADONE experiment. No result record exists for Gamma-Gamma, Mu-Pion, Boson, BCF or FENICE: the journal abstracts (Elsevier) cannot be fetched and the lab page is not a publication abstract (A16). FENICE detector technology is null.
- PADME: no end of data taking is stated (the INFN page is in the present tense; the latest campaign found is Run III, October to December 2022); the start of the "active" interval (July 2019) is the end of commissioning, and the date of the 2015 proposal is not given (the arXiv date of the first description is used).
- STCF: approval is not reported (the June 2026 talk says the proposal was submitted in 2025 and defended for inclusion in the 2026-2030 plan); the tunnel site is not selected; the Physics World article is undated; the project website's "About us" text is IHEP boilerplate. No `document:` records were written for the two CDRs.
- SCTF: the project status after 2020 was not found in any fetched source (the BINP page footer reads 2011-2020); no named collaboration; the exact site inside Novosibirsk is not named.
- Membership lists, institution counts and `key_specs` were not attempted for any record.

## Candidates considered and excluded

| candidate | decision | reason |
|---|---|---|
| ADONE first-generation and FENICE results | not written | The journal abstracts (Elsevier) return HTTP 403; the INFN-LNF history page is not a publication abstract, so no A16 claim quote can be taken. Only the 1974 Phys. Rev. Lett. paper (APS abstract fetchable) has a result record. |
| LADON, Jet Target, PULS and PWA at ADONE (1978-1990) | not created | Photonuclear and synchrotron-radiation facilities on the ADONE ring; the machine phases are recorded on `accelerator:adone`, the programmes themselves are outside the collider stream (A26 excludes photon science). |
| The Naples "proton-antiproton" experiment (took Boson's straight section) | not created | Not dated in the source and possibly the same effort as Baryon-Antibaryon; noted on both records. |
| AMADEUS and other KAONNIS activities at DAΦNE/J-PARC | not created | Not in the brief's list; the INFN-LNF KAONNIS page says AMADEUS and the J-PARC measurements are "not described in detail". |
| ILD, SiD, CLIC and CEPC detector concepts | unchanged | Excluded by `COLLIDERS_2.md` (no host site); STCF and SCTF differ because their project documents name Hefei and BINP Novosibirsk. |
| SCTF collaboration | not created | The CDR author list is a project team; no named collaboration was found. |

## For the integrator

- **Experiment kinds.** FINUDA, DEAR, SIDDHARTA and SIDDHARTA-2 are filed as `hadron_structure` (the nearest A26 kind for strangeness nuclear physics and kaonic atoms; Franzini & Moulson call FINUDA "a fixed-target experiment at an e+e- collider"). If another kind is preferred (`fixed_target`, or a new `nuclear_structure`), the four experiments and their coverage rows change together. PADME is `fixed_target`.
- **DAΦNE.** `accelerator:dafne` is untouched. Its `summary.technical` already names FINUDA, DEAR, SIDDHARTA and SIDDHARTA-2; the integrator may add dated phases for the experiment eras (FINUDA runs, DEAR 2002, SIDDHARTA 2009, SIDDHARTA-2 from 2021) and the crab-waist luminosity record: Milardi (arXiv:0803.1450, arXiv:1608.06150) states the crab-waist scheme was first applied for SIDDHARTA (2009, peak luminosity 4.53e32 cm^-2 s^-1) and that DAΦNE's interaction region was rebuilt for it. Those facts are for the accelerator record, which the lead owns. `experiment:padme` lists `accelerator:dafne` as its accelerator (the linac and BTF).
- **ADONE on the energy-frontier chart.** `accelerator:adone` carries a headline `cms_energy` of 3.0 GeV (the design maximum, quoted from Bernardini, Pancheri & Pellegrini) and one dated phase of about 3.1 GeV in November 1974 (the J/psi run). The chart therefore draws 3.0 GeV "as recorded today" at 1969 and 3.1 GeV at 1974. The brief said the headline is the maximum; it was kept at the design value because the 3.1 GeV push was a one-off beyond the machine's standard parameters. Set the headline to 3.1 GeV if the integrator prefers (the 1969 point would then read 3.1 GeV, which no source supports).
- **STCF area marker and detector placement.** `site:stcf-hefei-future-big-science-city` is a campus-grade area marker (about 5 km; the OSM polygon of the Hefei Advanced Light Facility, in the same Future Big Science City) and not the STCF site. `detector:stcf` has no placement on purpose: a placement on that point adds one A23 `coordinate-kind-approximate` validator warning (1818 to 1819). Add the placement (start null, role main, quote 'Site: Suburban "Future Big Science City” in Hefei' from the DIS2024 talk) if the integrator accepts that warning. `accelerator:stcf` and `facility:stcf-hefei` carry the marker. If the globe draws accelerators, the STCF and SCTF markers must not be read as sites.
- **STCF facility.** `facility:stcf-hefei` is a project-level `proposed` facility (kind accelerator_laboratory) with no operator; its lead is USTC. Merge it into a USTC facility record if one is later created.
- **Proposed colliders** `accelerator:stcf` and `accelerator:sctf` have registry rows through their experiments; neither is on the energy-frontier chart (not operating).
- **Date fields marked `uncertain`** (the starts of the three second-generation ADONE experiments) are deliberate: no source dates them; they are the latest possible start.
- Ids for `ID_REGISTRY.md` are listed in the final report.


## Sources created by this pass

| source id | type | URL |
|---|---|---|
| src:colliders2-adone-new-3-1-gev-particle-prl-1974 | journal_article | https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.33.1408 |
| src:colliders2-bernardini-pancheri-pellegrini-touschek-arxiv | arxiv | https://arxiv.org/abs/1510.00933 |
| src:colliders2-bonolis-pancheri-birth-of-colliding-beams-arxiv | arxiv | https://arxiv.org/abs/1511.00453 |
| src:colliders2-dear-kaonic-hydrogen-prl-2005 | journal_article | https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.94.212302 |
| src:colliders2-di-falco-latest-results-from-dafne-arxiv | arxiv | https://arxiv.org/abs/hep-ex/0311006 |
| src:colliders2-finuda-12lc-first-results-arxiv | arxiv | https://arxiv.org/abs/nucl-ex/0506028 |
| src:colliders2-finuda-evidence-6lh-arxiv | arxiv | https://arxiv.org/abs/1112.4529 |
| src:colliders2-finuda-hypernuclear-spectroscopy-arxiv | arxiv | https://arxiv.org/abs/1011.2695 |
| src:colliders2-finuda-mesonic-weak-decay-arxiv | arxiv | https://arxiv.org/abs/0905.0623 |
| src:colliders2-franzini-moulson-physics-of-dafne-arxiv | arxiv | https://arxiv.org/abs/hep-ex/0606033 |
| src:colliders2-hefei-half-nominatim | geocoder | https://nominatim.openstreetmap.org/search?q=%E5%90%88%E8%82%A5%E5%85%88%E8%BF%9B%E5%85%89%E6%BA%90&format=json&limit=5&addressdetails=0 |
| src:colliders2-lnf-adone-page | official_facility_site | https://w3.lnf.infn.it/adone/?lang=en |
| src:colliders2-lnf-adone-preger-murtas-wayback | official_facility_site | https://web.archive.org/web/20170424234320/http://www.lnf.infn.it/acceleratori/adone/ |
| src:colliders2-lnf-siddharta2-page | official_facility_site | https://w3.lnf.infn.it/research/nuclear-physics/siddharta2/?lang=en |
| src:colliders2-marton-kaonic-atoms-at-lnf-arxiv | arxiv | https://arxiv.org/abs/nucl-ex/0703028 |
| src:colliders2-milardi-dafne-2023-24-report-arxiv | arxiv | https://arxiv.org/abs/2409.17845 |
| src:colliders2-milardi-dafne-interaction-regions-arxiv | arxiv | https://arxiv.org/abs/0803.1450 |
| src:colliders2-padme-commissioning-arxiv | arxiv | https://arxiv.org/abs/2205.03430 |
| src:colliders2-padme-experiment-at-lnf-arxiv | arxiv | https://arxiv.org/abs/1501.01867 |
| src:colliders2-padme-run2-dark-photon-search-arxiv | arxiv | https://arxiv.org/abs/2603.28685 |
| src:colliders2-padme-run3-beam-arxiv | arxiv | https://arxiv.org/abs/2405.07203 |
| src:colliders2-padme-status-prospects-arxiv | arxiv | https://arxiv.org/abs/2305.08684 |
| src:colliders2-padme-two-photon-cross-section-arxiv | arxiv | https://arxiv.org/abs/2210.14603 |
| src:colliders2-padme-website | official_experiment_site | https://padme.lnf.infn.it/ |
| src:colliders2-padme-x17-search-arxiv | arxiv | https://arxiv.org/abs/2505.24797 |
| src:colliders2-physicsworld-china-mulls-stcf | press_release | https://physicsworld.com/a/china-mulls-plan-to-build-a-640m-super-tau-charm-factory/ |
| src:colliders2-scordo-siddharta-to-siddharta2-arxiv | arxiv | https://arxiv.org/abs/1803.02587 |
| src:colliders2-sctf-cdr-part1 | design_report | https://ctd.inp.nsk.su/wiki/images/4/47/CDR2_ScTau_en_vol1.pdf |
| src:colliders2-sctf-cdr-part2 | design_report | https://ctd.inp.nsk.su/wiki/images/2/23/CDR2_ScTau_en_vol2.pdf |
| src:colliders2-sctf-project-page | official_experiment_site | https://ctd.inp.nsk.su/c-tau/ |
| src:colliders2-sctf-tpc-inner-tracker-arxiv | arxiv | https://arxiv.org/abs/2005.09878 |
| src:colliders2-siddharta-kaonic-deuterium-prelim-arxiv | arxiv | https://arxiv.org/abs/1302.2797 |
| src:colliders2-siddharta-kaonic-helium-arxiv | arxiv | https://arxiv.org/abs/1108.5612 |
| src:colliders2-siddharta-kaonic-hydrogen-arxiv | arxiv | https://arxiv.org/abs/1105.3090 |
| src:colliders2-siddharta2-kaonic-atom-measurements-arxiv | arxiv | https://arxiv.org/abs/2610.35399 |
| src:colliders2-siddharta2-kaonic-hydrogen-arxiv | arxiv | https://arxiv.org/abs/2607.13952 |
| src:colliders2-siddhartino-kaonic-helium-arxiv | arxiv | https://arxiv.org/abs/2201.09735 |
| src:colliders2-stcf-cdr-accelerator-arxiv | design_report | https://arxiv.org/abs/2509.11522 |
| src:colliders2-stcf-cdr-vol1-physics-detector-arxiv | design_report | https://arxiv.org/abs/2303.15790 |
| src:colliders2-stcf-overview-liu-dis2024 | project_document | https://lpsc-indico.in2p3.fr/event/3268/contributions/7444/attachments/5299/8254/STCF-Overview.pdf |
| src:colliders2-stcf-overview-zheng-2024 | project_document | https://indico.pnp.ustc.edu.cn/event/1948/contributions/17297/attachments/6672/10749/STCF-Overview-Zheng-upload.pdf |
| src:colliders2-stcf-progress-zhang-beauty2026 | project_document | https://indico.cern.ch/event/1595459/contributions/7058138/attachments/3288802/5879910/STCF_beauy2026v2.pdf |
| src:colliders2-stcf-project-site | official_experiment_site | http://stcf.ustc.edu.cn/ |


## Checks run

Run on 2026-10-26 (the stream's date) from the worktree, after the last record was written:

- Validator `python -m hepgraph.atlas.validate`: `0 errors, 1818 warnings, 50 informational`, identical to the committed baseline; there is no finding on any record of this pass. (An earlier draft with a detector placement on the new STCF area marker gave 1819 warnings; that placement was removed, see above.)
- Quote checker `python scripts/atlas_quote_check.py --cache <cache> --only <fragment>` once per directory and slug (experiments, detectors, collaborations and results for finuda, dear, siddharta, adone, fenice, padme; accelerators, facilities and sites for stcf, sctf, adone): 251 quotes `verbatim`, 1 `skipped` (the Nominatim coordinate quote of the geocoder source, which the checker never fetches), 0 `segments`, 0 `near`, 0 `missing`, 0 `unfetchable`, 0 number flags.
- The build and the test suite were not run (the brief forbids the build).
