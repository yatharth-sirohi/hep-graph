# Dark-matter coverage wave: dark-matter-2 (direct detection, A26)

Owner tag `dark-matter-2`. Branch `atlas-c1-darkmatter`. Registry rows: `data/atlas/coverage/dark-matter-2.json`. Date of every `verified_at`: 2026-10-26.

## Scope

Amendment A26 of `docs/HEP_ATLAS_ONTOLOGY.md`: every ground-based, underground, underwater and in-ice direct-detection dark-matter experiment that meets the inclusion bar (a named experiment or collaboration; a fixed site; published physics results, or approved and under construction, or a published design report naming the host site; within A26), plus AMoRE (neutrinoless double-beta decay, assigned with the Korean laboratories). Existing records were not duplicated; where a missing lineage link or result was added to an existing record only that field was edited (`experiments/xenon1t.json`, `dama-libra.json` and others: lineage; `lux.json`: collaboration id; `cdms-ii`: one result; `darkside-50/20k` and `deap-3600`: lineage, by the argon stream).

Written: 71 experiments, 74 detectors, 44 collaborations, 185 results, 407 sources, 10 facilities and 10 sites (all counts are files added on this branch; plus `collaboration:lux` and `detector:lux`).

Method: records were written with one build script per cluster, quotes copied from raw page or PDF text, and every quote re-fetched and compared by `scripts/atlas_quote_check.py`. Intervals are given at the precision a source gives; where a source gives a year only the interval is year-precision and marked `approximate`.

## Experiments written

| id | kind | status | tier | start | end | facility (site) | results |
|---|---|---|---|---|---|---|---|
| `experiment:amore-i` | double_beta_decay | completed | B | 2019 | 2023-04 | Yangyang Underground Laboratory (y2l-yangyang) | 2 |
| `experiment:amore-ii` | double_beta_decay | construction | B | 2024-06 |  | Yemilab (yemilab-handuk) | 1 |
| `experiment:amore-pilot` | double_beta_decay | completed | B | 2015-07 | 2018-12 | Yangyang Underground Laboratory (y2l-yangyang) | 2 |
| `experiment:anais-112` | direct_dark_matter | completed | B | 2000-12 | 2026-01 | Laboratorio Subterráneo de Canfranc (lsc-canfranc) | 3 |
| `experiment:ardm` | direct_dark_matter | completed | B | 2010 | 2020 | Laboratorio Subterráneo de Canfranc; CERN (cern-meyrin, lsc-canfranc) | 5 |
| `experiment:argo` | direct_dark_matter | proposed | C | 2025-07 |  | SNOLAB (snolab-underground-lab) | 0 |
| `experiment:bullkid-dm` | direct_dark_matter | proposed | C | 2025-10 |  | Laboratori Nazionali del Gran Sasso (lngs-hall-a) | 3 |
| `experiment:c-4` | direct_dark_matter | proposed | C | 2012-10 |  | Soudan Underground Laboratory (soudan-minos-far-detector) | 0 |
| `experiment:cdex-1` | direct_dark_matter | completed | B | 2010 | 2018-12-02 | China Jinping Underground Laboratory (cjpl-i) | 4 |
| `experiment:cdex-10` | direct_dark_matter | active | B | 2016 |  | China Jinping Underground Laboratory (cjpl-i) | 2 |
| `experiment:cdex-50` | direct_dark_matter | proposed | C | 2023-09 |  | China Jinping Underground Laboratory (cjpl-ii) | 0 |
| `experiment:cdms-i` | direct_dark_matter | completed | B | 1997 | 1999-09 | Stanford Underground Facility (stanford-underground-facility-hepl) | 3 |
| `experiment:cogent` | direct_dark_matter | active | B | 2009-08-21 |  | Soudan Underground Laboratory (soudan-minos-far-detector) | 5 |
| `experiment:cosine-100` | direct_dark_matter | completed | B | 2016 | 2023-03-14 | Yangyang Underground Laboratory (y2l-yangyang) | 7 |
| `experiment:cosine-100u` | direct_dark_matter | active | B | 2023-03 |  | Yemilab (yemilab-handuk) | 2 |
| `experiment:cosinus` | direct_dark_matter | commissioning | B | 2016 |  | Laboratori Nazionali del Gran Sasso (lngs-hall-b) | 4 |
| `experiment:cosme` | direct_dark_matter | completed | B | 1990 | 2002 | Laboratorio Subterráneo de Canfranc (lsc-canfranc) | 2 |
| `experiment:coupp-2kg` | direct_dark_matter | completed | C | 2005 |  | Fermi National Accelerator Laboratory (fermilab-main-campus) | 1 |
| `experiment:coupp-4kg` | direct_dark_matter | completed | B | 2009-08-19 | 2012 | Fermi National Accelerator Laboratory; SNOLAB (fermilab-main-campus, snolab-underground-lab) | 2 |
| `experiment:cygno` | direct_dark_matter | construction | B | 2019-01 |  | Laboratori Nazionali del Gran Sasso (lngs-hall-b) | 4 |
| `experiment:dama-libra` | direct_dark_matter | completed | B | 2002-10 | 2024 | Laboratori Nazionali del Gran Sasso (lngs-hall-b) | 5 |
| `experiment:dama-nai` | direct_dark_matter | completed | B | 1990 | 2002-07 | Laboratori Nazionali del Gran Sasso (lngs-hall-b) | 2 |
| `experiment:darkside-lowmass` | direct_dark_matter | proposed | C | 2022-09 |  | SNOLAB (snolab-underground-lab) | 0 |
| `experiment:darksphere` | direct_dark_matter | proposed | C | 2023-01 |  | Boulby Underground Laboratory (boulby-mine) | 0 |
| `experiment:delight` | direct_dark_matter | approved | C | 2022-09 |  | Vue-des-Alpes underground laboratory (vue-des-alpes-underground-laboratory) | 1 |
| `experiment:dm-ice17` | direct_dark_matter | completed | B | 2010-12 | 2016-12 | Amundsen-Scott South Pole Station (south-pole-icecube) | 3 |
| `experiment:dm32` | direct_dark_matter | completed | C | 1993-05 | 1994-12 | Laboratorio Subterráneo de Canfranc (lsc-canfranc) | 0 |
| `experiment:dmtpc` | direct_dark_matter | active | B | 2007 |  | Waste Isolation Pilot Plant; Massachusetts Institute of Technology (mit-cambridge-campus, wipp-surface-campus) | 4 |
| `experiment:drift` | direct_dark_matter | active | B | 2001 |  | Boulby Underground Laboratory (boulby-mine) | 2 |
| `experiment:elegant-v-nai` | direct_dark_matter | completed | C | 1992 |  | Oto Cosmo Observatory; Kamioka Observatory (ICRR, University of Tokyo) (kamioka-mozumi-mine-super-kamiokande, oto-cosmo-observatory) | 0 |
| `experiment:genius-tf` | direct_dark_matter | completed | C | 2000-12 | 2006 | Laboratori Nazionali del Gran Sasso (lngs-hall-b) | 3 |
| `experiment:hdms` | direct_dark_matter | completed | B | 1998-03 | 2006 | Laboratori Nazionali del Gran Sasso (lngs-hall-b) | 3 |
| `experiment:herald` | direct_dark_matter | proposed | B | 2018-10 |  | Laboratoire Souterrain de Modane (lsm-frejus) | 2 |
| `experiment:igex-dm` | direct_dark_matter | completed | B | 2000 | 2002 | Laboratorio Subterráneo de Canfranc (lsc-canfranc) | 2 |
| `experiment:index-dm` | direct_dark_matter | active | C | 2022-07 |  | Jaduguda Underground Science Laboratory (jaduguda-underground-science-laboratory) | 2 |
| `experiment:kims` | direct_dark_matter | completed | B | 2003 | 2012-12 | Yangyang Underground Laboratory (y2l-yangyang) | 5 |
| `experiment:kims-nai` | direct_dark_matter | completed | C | 2013-11 | 2015-01 | Yangyang Underground Laboratory (y2l-yangyang) | 1 |
| `experiment:mimac` | direct_dark_matter | active | B | 2007 |  | Laboratoire Souterrain de Modane (lsm-frejus) | 4 |
| `experiment:miniclean` | direct_dark_matter | completed | C | 2013 | 2019 | SNOLAB (snolab-underground-lab) | 1 |
| `experiment:moscab` | direct_dark_matter | completed | C | 2014 | 2021-06 | Laboratori Nazionali del Gran Sasso (lngs-hall-b) | 2 |
| `experiment:naiad` | direct_dark_matter | completed | B | 2000 | 2003 | Boulby Underground Laboratory (boulby-mine) | 2 |
| `experiment:newage` | direct_dark_matter | active | B | 2003 |  | Kamioka Observatory (ICRR, University of Tokyo) (kamioka-mozumi-mine-super-kamiokande) | 5 |
| `experiment:newsdm` | direct_dark_matter | commissioning | C | 2016-04 |  | Laboratori Nazionali del Gran Sasso (lngs-hall-c) | 2 |
| `experiment:orpheus` | direct_dark_matter | completed | C | 1999 | 2005 | University of Bern underground laboratory (bern-underground-laboratory) | 2 |
| `experiment:oscura` | direct_dark_matter | proposed | C | 2020 |  | SNOLAB (snolab-underground-lab) | 2 |
| `experiment:pandax-i` | direct_dark_matter | completed | B | 2014-05-26 | 2014-10-16 | China Jinping Underground Laboratory (cjpl-i) | 2 |
| `experiment:pandax-ii` | direct_dark_matter | completed | B | 2014-10 | 2019-06-29 | China Jinping Underground Laboratory (cjpl-i) | 5 |
| `experiment:pandax-xt` | direct_dark_matter | proposed | C | 2024-02 |  | China Jinping Underground Laboratory (cjpl-ii) | 0 |
| `experiment:picasso` | direct_dark_matter | completed | B | 2002-07 | 2014-01 | SNOLAB (snolab-underground-lab) | 5 |
| `experiment:pico-2l` | direct_dark_matter | decommissioned | B | 2013-10 | 2015-11 | SNOLAB (snolab-underground-lab) | 3 |
| `experiment:pico-40l` | direct_dark_matter | active | C | 2019 |  | SNOLAB (snolab-underground-lab) | 2 |
| `experiment:pico-500` | direct_dark_matter | construction | C | 2018-06 |  | SNOLAB (snolab-underground-lab) | 1 |
| `experiment:pico-60` | direct_dark_matter | decommissioned | B | 2010 | 2017-07 | Fermi National Accelerator Laboratory; SNOLAB (fermilab-main-campus, snolab-underground-lab) | 7 |
| `experiment:picolon` | direct_dark_matter | active | B | 2006 |  | Kamioka Observatory (ICRR, University of Tokyo) (kamioka-kamland, oto-cosmo-observatory) | 3 |
| `experiment:rosebud` | direct_dark_matter | completed | C | 1999 | 2011 | Laboratorio Subterráneo de Canfranc (lsc-canfranc) | 2 |
| `experiment:sabre-north` | direct_dark_matter | construction | B | 2016 |  | Laboratori Nazionali del Gran Sasso (lngs-hall-b, lngs-hall-c) | 4 |
| `experiment:sabre-south` | direct_dark_matter | construction | B | 2016 |  | Stawell Underground Physics Laboratory (stawell-underground-physics-laboratory) | 3 |
| `experiment:sbc` | direct_dark_matter | construction | C | 2021-02 |  | SNOLAB; Fermi National Accelerator Laboratory (fermilab-main-campus, snolab-underground-lab) | 2 |
| `experiment:simple` | direct_dark_matter | completed | B | 1999-07 | 2010-07-22 | Laboratoire Souterrain à Bas Bruit (lsbb-rustrel) | 5 |
| `experiment:spice` | direct_dark_matter | proposed | C | 2021-08 |  | Laboratoire Souterrain de Modane (lsm-frejus) | 3 |
| `experiment:tesseract` | direct_dark_matter | proposed | B | 2022 |  | Laboratoire Souterrain de Modane (lsm-frejus) | 5 |
| `experiment:texono` | direct_dark_matter | active | B | 1997 |  | Kuo-Sheng Reactor Neutrino Laboratory (ksnl-kuo-sheng-nuclear-power-station) | 3 |
| `experiment:tokyo-dark-matter-search` | direct_dark_matter | completed | B | 2000 | 2003 | Kamioka Observatory (ICRR, University of Tokyo) (kamioka-mozumi-mine-super-kamiokande) | 2 |
| `experiment:trex-dm` | direct_dark_matter | active | C | 2017 |  | Laboratorio Subterráneo de Canfranc (lsc-canfranc) | 3 |
| `experiment:warp` | direct_dark_matter | completed | B | 2004 | 2011 | Laboratori Nazionali del Gran Sasso (lngs-hall-b) | 2 |
| `experiment:xenon10` | direct_dark_matter | completed | B | 2002 | 2007-02-14 | Laboratori Nazionali del Gran Sasso (lngs-hall-b) | 3 |
| `experiment:xenon100` | direct_dark_matter | completed | B | 2008 | 2016 | Laboratori Nazionali del Gran Sasso (lngs-hall-b) | 6 |
| `experiment:xmass` | direct_dark_matter | completed | B | 2007-04 | 2019-02-01 | Kamioka Observatory (ICRR, University of Tokyo) (kamioka-mozumi-mine-super-kamiokande) | 5 |
| `experiment:zeplin-i` | direct_dark_matter | completed | B | 2001 | 2006 | Boulby Underground Laboratory (boulby-mine) | 1 |
| `experiment:zeplin-ii` | direct_dark_matter | completed | B | 2001-11 | 2006 | Boulby Underground Laboratory (boulby-mine) | 3 |
| `experiment:zeplin-iii` | direct_dark_matter | completed | B | 2006 | 2011-05-07 | Boulby Underground Laboratory (boulby-mine) | 4 |

## Dates and places, with the evidence behind each

Each interval: status, start, end, confidence, URL and verbatim quote. The placement row gives the site record used for the detector (the Atlas site is the host laboratory point unless the site record says otherwise).

### experiment:amore-i - AMoRE-I (completed)

- facility role: facility:yangyang-underground-laboratory 2019 to 2023-04 (verified); https://arxiv.org/abs/2407.05618; quote: "The first two, AMoRE-Pilot and AMoRE-I, were completed at the 700-meter-deep Yangyang Underground Laboratory (Y2L)."
- active 2019 to 2023 (approximate) AMoRE-I operation at Y2L; https://arxiv.org/abs/2407.05618; quote: "we operated AMoRE-I from 2019 to 2023"
- active 2020-12 to 2023-04 (verified) DAQ with the full 18-crystal array; https://arxiv.org/abs/2407.05618; quote: "data acquisition (DAQ) with the full eighteen-crystal detector array started in December 2020 and ended in April 2023"
- completed 2023-04 to  (approximate) completed (AMoRE-I data taking ended); https://arxiv.org/abs/2407.05618; quote: "data acquisition (DAQ) with the full eighteen-crystal detector array started in December 2020 and ended in April 2023"
- detector placement: site:y2l-yangyang

### experiment:amore-ii - AMoRE-II (construction)

- facility role: facility:yemilab 2024-06 to  (verified); https://arxiv.org/abs/2406.09698; quote: "AMoRE-II is currently being installed at the Yemi Underground Laboratory, located approximately 1000 meters deep in Jeongseon, Korea."
- construction 2024-06 to  (approximate) AMoRE-II installation at Yemilab; https://arxiv.org/abs/2406.09698; quote: "AMoRE-II is currently being installed at the Yemi Underground Laboratory, located approximately 1000 meters deep in Jeongseon, Korea."
- detector placement: site:yemilab-handuk

### experiment:amore-pilot - AMoRE-Pilot (completed)

- facility role: facility:yangyang-underground-laboratory 2015-07 to 2018-12 (verified); https://arxiv.org/abs/1903.09483; quote: "This stage of the project is carried out in the Yangyang underground laboratory at a depth of 700 m."
- active 2015-07 to 2018-12 (approximate) AMoRE-Pilot data taking at Y2L; https://centers.ibs.re.kr/html/cup/research/research_0303.html; quote: "AMoRE-Pilot, the pilot phase of the AMoRE project, is an experiment that has been running in the 700-m-deep Yangyang underground Laboratory (Y2L) since summer 2015"
- completed 2018-12 to  (approximate) completed (run ended); https://arxiv.org/abs/2005.05567; quote: "After completion of the AMoRE-Pilot run at the end of 2018"
- detector placement: site:y2l-yangyang

### experiment:anais-112 - ANAIS-112 (completed)

- facility role: facility:canfranc-underground-laboratory 2000-12 to 2026-01 (approximate); https://arxiv.org/abs/hep-ex/0111075; quote: "Before setting-up the whole experiment, a prototype is being developed in Canfranc in an attempt"
- proposed 2001 to 2011-02 (approximate) planned experiment (up to 107 kg of NaI(Tl) at Canfranc); https://arxiv.org/abs/hep-ex/0111075; quote: "ANAIS (Annual Modulation with NaI's) is an experiment planned to investigate seasonal modulation effects in the signal of galactic WIMPs using up to 107 kg of NaI(Tl) in the Canfranc Underground Laboratory (Spain)."
- construction 2000-12 to 2001-08 (approximate) first prototype (single 10.7 kg crystal) at Canfranc; https://arxiv.org/abs/hep-ex/0111075; quote: "By comparing the data recorded from December 2000 to August 2001 with the Monte Carlo"
- construction 2011-02 to 2012-12 (verified) ANAIS-0 prototype; https://arxiv.org/abs/1308.3478; quote: "was operated at hall B of LSC from February, 2011 to December, 2012"
- construction 2012-12 to 2015-03 (verified) ANAIS-25 prototype (two 12.5 kg Alpha Spectra modules); https://arxiv.org/abs/1604.05587; quote: "took data at the LSC from December 2012 to March 2015"
- construction 2015-03 to 2016-02 (approximate) ANAIS-37 prototype (ANAIS-25 plus a third module); https://arxiv.org/abs/1604.05587; quote: "data taking started five days later."
- construction 2012 to 2017-03 (approximate) production and installation of the nine ANAIS-112 modules; https://arxiv.org/abs/2607.24448; quote: "which were built by Alpha Spectra starting in 2012."
- commissioning 2017-03 to 2017-08-03 (verified) commissioning run; https://arxiv.org/abs/1812.01472; quote: "ANAIS-112 detector was assembled in early 2017 and the commissioning phase was performed from March to July."
- active 2017-08-03 to 2026-01 (verified) dark matter run (annual modulation data taking); https://gifna.unizar.es/anais/; quote: "ANAIS-112 is taking data at the Canfranc Underground Laboratory since August, 3rd, 2017."
- completed 2026-01 to  (approximate) completed (data taking ended); https://arxiv.org/abs/2607.24448; quote: "ANAIS-112 took data until January 2026, by which time it"
- detector placement: site:lsc-canfranc

### experiment:ardm - ArDM (completed)

- facility role: facility:canfranc-underground-laboratory 2012 to 2020 (verified); https://arxiv.org/abs/1307.0117; quote: "In early 2012 the transfer to its final place in the underground laboratory of Canfranc (LSC) was initiated with the installation of the vessel and the majority of the cryogenic parts."
- facility role: facility:cern  to 2012 (approximate); https://arxiv.org/abs/0912.2962; quote: "The experiment is presently under construction and commissioning on surface at CERN."
- approved 2010 to 2012 (verified) approved as LSC EXP-08-2010 / CERN RE18; https://arxiv.org/abs/1505.02443; quote: "Developed at CERN as Recognized Experiment RE18, the experiment has been approved in 2010 to be installed in the Spanish underground site LSC (Laboratorio Subterraneo de Canfranc)."
- construction  to 2013-04 (approximate) construction and surface tests at CERN, transfer to and assembly at LSC; https://arxiv.org/abs/1307.0117; quote: "It was constructed and operated at CERN [3, 4]."
- commissioning 2013-04 to 2015-02 (verified) underground commissioning with gas argon, then liquid-argon filling; https://arxiv.org/abs/1307.0117, https://arxiv.org/abs/1505.02443; quote: "First data taking at LSC was carried out for two weeks in April 2013"
- active 2015-02 to 2020 (approximate) liquid-argon data taking (single-phase Run I in 2015, later dual-phase run); https://arxiv.org/abs/1505.02443, https://indico.global/event/645/contributions/16365/; quote: "Now the project has entered the first period of physics data taking in the single-phase operation mode (ArDM Run I)."
- active 2015-02 to 2015 (approximate) ArDM Run I (single phase, liquid argon); https://arxiv.org/abs/1505.02443, https://arxiv.org/abs/1712.01932; quote: "Now the project has entered the first period of physics data taking in the single-phase operation mode (ArDM Run I)."
- active  to 2020 (uncertain) dual-phase run (Run II); https://indico.global/event/645/contributions/16365/; quote: "The ArDM experiment, a tonne-scale dual-phase liquid Argon TPC, has recently finished data taking in dual-phase mode."
- completed 2020 to  (uncertain) completed (dual-phase data taking ended; hardware reused for DArTinArDM); https://indico.global/event/645/contributions/16365/, https://lsc-canfranc.es/en/ardm/; quote: "The ArDM experiment, a tonne-scale dual-phase liquid Argon TPC, has recently finished data taking in dual-phase mode."
- detector placement: site:cern-meyrin
- detector placement: site:lsc-canfranc

### experiment:argo - ARGO (proposed)

- facility role: facility:snolab 2026-03 to  (approximate); https://arxiv.org/abs/2603.27372; quote: "SNOLAB’s Cube Hall has been selected as the prospective site."
- proposed 2025-07 to  (approximate) proposed; https://arxiv.org/abs/2507.11368, https://arxiv.org/abs/2603.27372; quote: "Late 2030s: Construction of ARGO, preferably at SNOLAB."
- detector placement: site:snolab-underground-lab

### experiment:bullkid-dm - BULLKID-DM (proposed)

- facility role: facility:lngs 2025-10 to  (approximate); https://arxiv.org/abs/2510.17682; quote: "While the final experiment with the full-scale detector will be located at the Gran Sasso underground laboratory in Italy for a minimized background activity"
- proposed 2025-10 to  (approximate) BULLKID-DM experiment planned for LNGS; https://arxiv.org/abs/2510.17682; quote: "While the final experiment with the full-scale detector will be located at the Gran Sasso underground laboratory in Italy for a minimized background activity"
- planned 2026-12 (planned) to  (approximate) planned installation of the 3-detector demonstrator at the LNGS cryo-platform; https://arxiv.org/abs/2601.13766; quote: "Installation of the demonstrator at the cryo-platform of Laboratori Nazionali del Gran Sasso (LNGS), with a background rate around 104 DRU, by the end of 2026."
- planned 2027 (planned) to  (approximate) planned installation of the final experiment at the LNGS cryo-platform; https://arxiv.org/abs/2601.13766; quote: "The plan is to install the final experiment at the cryo-platform of LNGS in 2027, after previous technological steps"
- detector placement: site:lngs-hall-a

### experiment:c-4 - C-4 (proposed)

- facility role: facility:soudan-underground-laboratory 2012-10 to  (approximate); https://arxiv.org/abs/1210.6282; quote: "The present plan is to locate the C-4 dark matter experiment in the proton-decay hall of the Soudan Underground Laboratory (2800 m.w.e. overburden), the same location as the CoGeNT and CDMS-II experiments."
- proposed 2012-10 to  (uncertain) design of the C-4 expansion; https://arxiv.org/abs/1210.6282; quote: "We describe the experimental design of C-4, an expansion of the CoGeNT dark matter search to four identical detectors each approximately three times the mass of the p-type point contact germanium diode presently taking data at the Soudan Underground Laboratory."
- detector placement: site:soudan-minos-far-detector

### experiment:cdex-1 - CDEX-1 (completed)

- facility role: facility:cjpl 2010 to 2018-12 (verified); https://arxiv.org/abs/1306.4135; quote: "at the China Jinping underground Laboratory where the rock overburden is more than 2400 m"
- active 2010 to 2018-12 (approximate) CDEX-1 / CDEX-1B operation; https://arxiv.org/abs/2309.01843; quote: "The first phase of the experiment, CDEX-1 [6], was installed and started operation in 2010 using a 1-kg single element pPCGe detector cooled by a cold-finger system."
- active 2014-09-27 to 2018-12-02 (verified) CDEX-1B annual-modulation data (Run 1 and Run 2); https://arxiv.org/abs/1904.12889; quote: "from September 27, 2014 to August 2, 2017 (Run 1), and subsequently without NaI(Tl) (replaced by passive copper shielding) from August 4, 2017 till December 2, 2018 (Run 2)"
- completed 2018-12 to  (approximate) completed (end of CDEX-1B data taking); https://arxiv.org/abs/1904.12889; quote: "from September 27, 2014 to August 2, 2017 (Run 1), and subsequently without NaI(Tl) (replaced by passive copper shielding) from August 4, 2017 till December 2, 2018 (Run 2)"
- detector placement: site:cjpl-i

### experiment:cdex-10 - CDEX-10 (active)

- facility role: facility:cjpl 2016 to  (uncertain); https://arxiv.org/abs/2209.00861; quote: "The LN cryostat and data acquisition (DAQ) systems are placed inside a polyethylene room at CJPL-I [23]."
- upgrade 2016 to 2017-02 (approximate) upgrade of CDEX-1 to CDEX-10; https://arxiv.org/abs/2309.01843; quote: "In 2016, the experiment was upgraded to the second phase, CDEX-10 [7]."
- active 2017-02-26 to  (uncertain) CDEX-10 operation; https://arxiv.org/abs/1802.09016; quote: "Data taking with C10B-Ge1 was performed from February 26, 2017 to November 7, 2017."
- detector placement: site:cjpl-i

### experiment:cdex-50 - CDEX-50 (proposed)

- facility role: facility:cjpl 2023-09 to  (approximate); https://arxiv.org/abs/2309.01843; quote: "This tank is situated at Hall C1 as part of the extension project of CJPL (CJPL-II) [17]."
- proposed 2023-09 to  (approximate) proposal / projected-sensitivity study; https://arxiv.org/abs/2309.01843; quote: "CDEX-50 is a next-generation project of the China Dark Matter Experiment (CDEX) that aims to search for dark matter using a 50-kg germanium detector array."
- detector placement: site:cjpl-ii

### experiment:cdms-i - CDMS I (completed)

- facility role: facility:stanford-underground-facility 1997 to 1999-09 (approximate); https://arxiv.org/abs/astro-ph/0203500; quote: "The first stage of the Cryogenic Dark Matter Search (CDMS I) operates at the Stanford Underground Facility, a tunnel 10.6 m beneath the Stanford University campus."
- active 1997 to 1999-09 (uncertain) WIMP-search data runs at the Stanford Underground Facility; https://arxiv.org/abs/astro-ph/9712343, https://arxiv.org/abs/astro-ph/0002471; quote: "we have begun taking data to search for WIMPs"
- completed 1999-09 to  (approximate) completed (last CDMS I data run); https://arxiv.org/abs/astro-ph/0002471, https://arxiv.org/abs/astro-ph/0203500; quote: "Between November, 1998, and September, 1999, 96 live days of data were obtained using 3 of 4 165 g Ge BLIP detectors."
- detector placement: site:stanford-underground-facility-hepl

### experiment:cogent - CoGeNT (active)

- facility role: facility:soudan-underground-laboratory 2009-08-21 to  (verified); https://arxiv.org/abs/1208.5737; quote: "The present CoGeNT detector is located at the Soudan Underground Laboratory (Soudan, Minnesota, USA)"
- commissioning 2009-08-21 to 2009-12-04 (verified) underground installation and cooldown at Soudan; https://arxiv.org/abs/1106.0650, https://arxiv.org/abs/1208.5737; quote: "Underground installation of this PPC at SUL took place on August 21, 2009."
- active 2009-12-04 to 2011-03 (verified) initial run (442 live days to 6 March 2011); https://arxiv.org/abs/1208.5737; quote: "spanning 442 live days over the period 4 December 2009 to 6 March 2011"
- shutdown 2011-03 to 2011-06-07 (approximate) outage after the Soudan access-shaft fire; https://arxiv.org/abs/1401.3295, https://arxiv.org/abs/1208.5737; quote: "Operation restarted on 7 June 2011 following a three month downtime."
- active 2011-06-07 to  (uncertain) continuous data taking after the fire (data set analysed to 23 April 2013); https://arxiv.org/abs/1401.3295, https://arxiv.org/abs/1401.6234; quote: "The presently examined cumulative dataset ends on 23 April 2013, spanning 1,237 days, of which 1,129 were live."
- detector placement: site:soudan-minos-far-detector

### experiment:cosine-100 - COSINE-100 (completed)

- facility role: facility:yangyang-underground-laboratory 2016 to 2023-03-14 (verified); https://arxiv.org/abs/1710.05299; quote: "The COSINE experiment is located in a recently established experimental area in the Y2L A5 tunnel."
- construction 2016 to 2016-09 (approximate) detector assembly at Y2L (early 2016) and commissioning; https://arxiv.org/abs/1710.05299; quote: "The construction and assembly of the COSINE-100 detector at Y2L took place in early 2016, and the physics run started in late September of 2016."
- active 2016-10-21 to 2023-03-14 (verified) physics data taking at Y2L (6.4 years); https://arxiv.org/abs/2409.13226; quote: "It began physics operation on October 21, 2016 and concluded on March 14, 2023, for relocation of the experimental site to Yemilab"
- completed 2023-03-14 to  (verified) completed (concluded for relocation to Yemilab); https://arxiv.org/abs/2409.13226; quote: "It began physics operation on October 21, 2016 and concluded on March 14, 2023, for relocation of the experimental site to Yemilab"
- detector placement: site:y2l-yangyang

### experiment:cosine-100u - COSINE-100U (active)

- facility role: facility:yemilab 2023-03 to  (verified); https://arxiv.org/abs/2608.11678; quote: "The COSINE-100U experiment is located at Yemilab in Jeongseon, Gangwon Province, Republic of Korea."
- construction 2023-03 to 2025-09 (approximate) decommissioning at Y2L, relocation, upgrade and installation at Yemilab; https://arxiv.org/abs/2608.11678; quote: "After COSINE-100 completed data taking in March 2023, the detector was upgraded to COSINE-100U and relocated to Yemilab"
- active 2025-09 to  (verified) physics data taking at Yemilab; https://arxiv.org/abs/2608.11678; quote: "Stable COSINE-100U physics data taking began at Yemilab in September 2025"
- active 2026-05 to  (verified) physics data taking at the nominal -30 C; https://arxiv.org/abs/2608.11678; quote: "Physics data taking at the nominal operating temperature of −30 ◦C began in May 2026."
- detector placement: site:yemilab-handuk

### experiment:cosinus - COSINUS (commissioning)

- facility role: facility:lngs 2021 to  (verified); https://arxiv.org/abs/2507.02429; quote: "COSINUS was constructed from 2021 to 2024 in the Laboratori Nazionali del Gran Sasso (LNGS) underground laboratories in central Italy."
- proposed 2016 to 2021 (approximate) R&D project and proposed NaI cryogenic calorimeter at LNGS; https://arxiv.org/abs/1603.02214; quote: "Both refrigerators are located in the LNGS underground site for obvious reasons of shielding against cosmic radiation."
- construction 2021 to 2024 (verified) construction of the experimental facility at LNGS; https://arxiv.org/abs/2507.02429; quote: "COSINUS was constructed from 2021 to 2024 in the Laboratori Nazionali del Gran Sasso (LNGS) underground laboratories in central Italy."
- commissioning 2022-06 to 2022-06 (verified) underground run of a 3.67 g NaI remoTES prototype at LNGS; https://arxiv.org/abs/2307.11139; quote: "In total about ten days of stream data were taken over the first two weeks of June, 2022."
- commissioning 2024 to  (approximate) commissioning of the cryostat and facility; first physics run (COSINUS-1pi Run1) awaited; https://arxiv.org/abs/2507.02429, https://indico.ific.uv.es/event/7986/contributions/28355/, https://arxiv.org/abs/2607.24448; quote: "In a second commissioning run in July 2024, the system was equipped with internal passive shielding: a 190 kg block of ultra-pure copper mounted on the Still plate at approximately 800 mK."
- detector placement: site:lngs-hall-b

### experiment:cosme - COSME (completed)

- facility role: facility:canfranc-underground-laboratory 1990 to 2002 (approximate); https://arxiv.org/abs/hep-ex/0101037; quote: "A small, natural abundance, germanium detector (COSME) has been operating recently at the Canfranc Underground Laboratory (Spanish Pyrenees)"
- active 1990 to 1992 (approximate) first operation of the COSME detector (Canfranc tunnel); https://arxiv.org/abs/hep-ex/0101037; quote: "compared to the previous set of data from 1990 to 1992"
- active 1998 to 2002 (approximate) second operation in the deeper, IGEX-type shield (2450 m.w.e.); https://arxiv.org/abs/hep-ex/0101037, https://arxiv.org/abs/hep-ph/0011318; quote: "The COSME detector has been running during the years 1998 and 1999 in these new conditions"
- completed 2002 to  (uncertain) completed (detector removed from the shield; no end date published); https://arxiv.org/abs/astro-ph/0211535; quote: "removal of the other detectors (RG-I, RG-III and COSME)"
- detector placement: site:lsc-canfranc

### experiment:coupp-2kg - COUPP-2kg (completed)

- facility role: facility:fermilab 2005 to  (approximate); https://arxiv.org/abs/0804.2886; quote: "Early in 2005 we installed a chamber containing 1.5 kg of CF3 I, an industrial refrigerant commonly used as a fire extinguisher, at the 350-foot depth of the NuMI (Neutrinos at the Main Injector) tunnel in Fermilab."
- active 2005 to  (approximate) operation at Fermilab (NuMI/MINOS tunnel); https://arxiv.org/abs/0804.2886; quote: "Early in 2005 we installed a chamber containing 1.5 kg of CF3 I, an industrial refrigerant commonly used as a fire extinguisher, at the 350-foot depth of the NuMI (Neutrinos at the Main Injector) tunnel in Fermilab."
- completed 2009-08 to  (uncertain) completed (successor chamber took over the pressure vessel); https://arxiv.org/abs/2401.07384, https://arxiv.org/abs/1008.3518; quote: "The COUPP 4 kg bubble chamber was the first such improvement, employing a larger synthetic fused silica bell jar inside the same pressure vessel used for the 2 kg chamber."
- detector placement: site:fermilab-main-campus

### experiment:coupp-4kg - COUPP-4kg (completed)

- facility role: facility:fermilab 2009-08-19 to 2010 (approximate); https://arxiv.org/abs/1008.3518; quote: "This letter reports results from a 3.5 kg CF3 I bubble chamber operated from August 19th to December 18th, 2009, in the MINOS near detector tunnel [7] at the Fermi National Accelerator Laboratory."
- facility role: facility:snolab 2010-09 to 2012 (approximate); https://arxiv.org/abs/1204.3094; quote: "We report results from a 4.0 kg CF3 I bubble chamber operated from September 2010 to August 2011 in the JDrift [9] of the SNOLAB deep underground laboratory."
- active 2009-08-19 to 2012 (approximate) operation (MINOS tunnel at Fermilab, then SNOLAB); https://arxiv.org/abs/1008.3518, https://arxiv.org/abs/1204.3094, https://indico.phys.hawaii.edu/event/456/contributions/1948/attachments/1489/1774/PICO_CosPA2013_Neilson.pdf; quote: "This letter reports results from a 3.5 kg CF3 I bubble chamber operated from August 19th to December 18th, 2009, in the MINOS near detector tunnel [7] at the Fermi National Accelerator Laboratory."
- completed 2012 to  (approximate) completed; https://indico.phys.hawaii.edu/event/456/contributions/1948/attachments/1489/1774/PICO_CosPA2013_Neilson.pdf; quote: "A second run in 2012 after replacing known neutron sources had similar results"
- active 2009-08-19 to 2009-12-18 (verified) run at Fermilab (3.5 kg CF3I); https://arxiv.org/abs/1008.3518; quote: "This letter reports results from a 3.5 kg CF3 I bubble chamber operated from August 19th to December 18th, 2009, in the MINOS near detector tunnel [7] at the Fermi National Accelerator Laboratory."
- active 2010-09 to 2011-08 (verified) run 1 at SNOLAB (4.0 kg CF3I); https://arxiv.org/abs/1204.3094; quote: "We report results from a 4.0 kg CF3 I bubble chamber operated from September 2010 to August 2011 in the JDrift [9] of the SNOLAB deep underground laboratory."
- active 2012 to 2012 (approximate) run 2 at SNOLAB; https://indico.phys.hawaii.edu/event/456/contributions/1948/attachments/1489/1774/PICO_CosPA2013_Neilson.pdf; quote: "A second run in 2012 after replacing known neutron sources had similar results"
- detector placement: site:fermilab-main-campus
- detector placement: site:snolab-underground-lab

### experiment:cygno - CYGNO (construction)

- facility role: facility:lngs 2022-02 to  (verified); https://arxiv.org/abs/2306.16856; quote: "that has been installed in underground Laboratori Nazionali del Gran Sasso in February 2022."
- proposed 2019-01 to 2025-10 (approximate) proposal (CDR 2019, TDR 2023) and prototype R&D (LIME); https://arxiv.org/abs/1901.04190, https://www.openaccessrepository.it/records/73356, https://www.openaccessrepository.it/record/76967; quote: "CYGNO is a new proposal supported by INFN, the Italian National Institute for Nuclear Physics"
- commissioning 2022-02 to 2024-05 (derived) LIME 50 L prototype (PHASE 0 R&D): underground data taking at LNGS (five periods); https://arxiv.org/abs/2306.16856, https://arxiv.org/abs/2603.22595; quote: "that has been installed in underground Laboratori Nazionali del Gran Sasso in February 2022."
- construction 2025-10 to  (approximate) CYGNO-04 (0.4 m^3) demonstrator under construction in LNGS Hall F; https://arxiv.org/abs/2510.23229, https://arxiv.org/abs/2603.22595, https://www.openaccessrepository.it/record/76967; quote: "Currently, the CYGNO Collaboration is constructing the detector demonstrator, CYGNO-04, in Hall F at Laboratori Nazionali del Gran Sasso (LNGS)."
- detector placement: site:lngs-hall-b

### experiment:dama-libra - DAMA/LIBRA (completed)

- facility role: facility:lngs 2003-03 to 2024 (uncertain); https://arxiv.org/abs/2607.24448; quote: "DAMA/LIBRA took data in two phases from 2003 to 2024."
- construction 2002-10 to 2003-03 (approximate) installation of DAMA/LIBRA; https://arxiv.org/abs/astro-ph/0305542; quote: "whose installation is started at fall 2002;"
- commissioning 2003-03 to 2003-09-09 (approximate) first operations and test runs; https://arxiv.org/abs/0804.2738; quote: "begun first operations in March 2003."
- active 2003-09-09 to 2010-09-08 (verified) DAMA/LIBRA-phase1 (seven annual cycles); https://arxiv.org/abs/1308.5109; quote: "DAMA/LIBRA-phase1 Sept. 9, 2003 - Sept. 8, 2010"
- upgrade 2010-10 to 2010-12-23 (approximate) second upgrade: all photomultipliers replaced (phase2); https://www.lngs.infn.it/en/dama; quote: "the second more important one has been carried out in Fall 2010"
- commissioning 2010-12-23 to 2011-09-09 (verified) DAMA/LIBRA-phase2 commissioning (first annual cycle); https://arxiv.org/abs/1805.10486; quote: "Dec. 23, 2010 – Sept. 9, 2011"
- active 2011-11-02 to 2024 (uncertain) DAMA/LIBRA-phase2 annual cycles; https://arxiv.org/abs/2607.24448; quote: "Phase 2 ran from 2010 to 2024."
- completed 2024 to  (uncertain) completed (data taking ended); https://arxiv.org/abs/2607.24448; quote: "DAMA/LIBRA took data in two phases from 2003 to 2024."
- detector placement: site:lngs-hall-b

### experiment:dama-nai - DAMA/NaI (completed)

- facility role: facility:lngs 1995 to 2002-07 (verified); https://arxiv.org/abs/astro-ph/0307403; quote: "which has been operative at the Gran Sasso National Laboratory of the I.N.F.N. for more than one decade"
- proposed 1990 to 1995 (approximate) proposal; https://arxiv.org/abs/astro-ph/0501412; quote: "The DAMA/NaI experiment was proposed in 1990 [9], designed and realized having"
- active 1995 to 2002-07 (approximate) DAMA/NaI data taking (seven annual cycles); https://arxiv.org/abs/2607.24448; quote: "DAMA/NaI which ran from 1995 to 2002 at LNGS."
- completed 2002-07 to  (verified) completed; https://www.lngs.infn.it/en/dama; quote: "the DAMA/NaI set-up (~100 kg highly radiopure NaI(Tl)), which has completed its data taking in July 2002."
- detector placement: site:lngs-hall-b

### experiment:darkside-lowmass - DarkSide-LowMass (proposed)

- facility role: facility:snolab 2025-07 to  (approximate); https://arxiv.org/abs/2507.11368; quote: "The primary plan involves placing DSLM’s inner detector inside the DEAP-3600 water tank at SNOLAB"
- proposed 2022-09 to  (approximate) proposed (conceptual design); https://arxiv.org/abs/2209.01177; quote: "A conceptual design for a new detector, DarkSide-LowMass, is presented, based on the DarkSide-50 detector and progress toward DarkSide-20k, optimized for a low-threshold electron-counting measurement."
- detector placement: site:snolab-underground-lab

### experiment:darksphere - DarkSPHERE (proposed)

- facility role: facility:boulby-underground-laboratory 2023-01 to  (approximate); https://arxiv.org/pdf/2301.05183; quote: "We present the conceptual design and the physics potential of DarkSPHERE, a proposed 3 m in diameter spherical proportional counter electroformed underground at the Boulby Underground Laboratory."
- proposed 2023-01 to  (approximate) conceptual design (proposed experiment); https://arxiv.org/pdf/2301.05183; quote: "We present the conceptual design and the physics potential of DarkSPHERE, a proposed 3 m in diameter spherical proportional counter electroformed underground at the Boulby Underground Laboratory."
- detector placement: site:boulby-mine

### experiment:delight - DELight (approved)

- facility role: facility:vue-des-alpes-underground-laboratory 2025-12 to  (approximate); https://arxiv.org/abs/2512.15278; quote: "In phase-I, DELight will be located at the Vue-des-Alpes (VdA) underground laboratory [18], a shallow lab in Switzerland with 230 m of rock overburden (∼630 mwe)."
- proposed 2022-09 to 2026-03 (approximate) proposed experiment (planning phase); https://arxiv.org/abs/2209.10950; quote: "The new ``Direct search Experiment for Light dark matter'', DELight, will be using superfluid helium as active target, instrumented with magnetic micro-calorimeters."
- approved 2026-03 to  (approximate) funded: DFG Research Unit 6006 (design, build and operate phase I); https://delight.kit.edu/scienceresults.html; quote: "The Deutsche Forschungsgemeinschaft (DFG) - German Research Foundation has awarded DELight the funding to design, build, and operate Phase-I of the experiment within the framework of the DFG Research Unit 6006"
- detector placement: site:vue-des-alpes-underground-laboratory

### experiment:dm-ice17 - DM-Ice17 (completed)

- facility role: facility:amundsen-scott-south-pole-station 2010-12 to 2017 (approximate); https://arxiv.org/abs/1401.4804; quote: "It was codeployed with IceCube 2457 m deep in the South Pole glacial ice in December 2010 and is the first such detector operating in the Southern Hemisphere."
- commissioning 2010-12 to 2011-06-16 (approximate) deployment with IceCube and commissioning; https://arxiv.org/abs/1602.05939; quote: "DM-Ice17, the first stage of the DM-Ice experimental program, was deployed at the geographic South Pole in December 2010 [36]."
- active 2011-06-16 to 2015-01-28 (verified) primary physics run; https://arxiv.org/abs/1602.05939; quote: "The analysis presented here covers the 3.6 year primary physics run of DM-Ice17 from June 16, 2011 to January 28, 2015."
- active 2015-01-28 to 2016-12 (uncertain) continued stable operation after the physics run; https://arxiv.org/abs/1612.07426; quote: "The detectors have continued stable operations since."
- completed 2017 to  (uncertain) completed (no end date published); https://arxiv.org/abs/1602.05939; quote: "DM-Ice17, the first step in the DM-Ice experimental program, consists of 17 kg of NaI(Tl) located at the South Pole under 2200 m.w.e. overburden of Antarctic glacial ice."
- detector placement: site:south-pole-icecube

### experiment:dm32 - DM32 (completed)

- facility role: facility:canfranc-underground-laboratory 1993-05 to 1994-12 (approximate); https://arxiv.org/abs/2607.24448; quote: "assembled and carried out the DM32 Experiment at Canfranc Underground Laboratory (LSC)."
- active 1993-05 to 1994-12 (approximate) data taking with three NaI(Tl) modules; https://arxiv.org/abs/2607.24448; quote: "4,613.6 kg·day of data taken between May 1993 and December 1994, DM32 set competitive limits on SI and SD coupling between DM particles and target nuclei"
- completed 1994-12 to  (approximate) completed (data taking ended); https://arxiv.org/abs/2607.24448; quote: "4,613.6 kg·day of data taken between May 1993 and December 1994, DM32 set competitive limits on SI and SD coupling between DM particles and target nuclei"
- detector placement: site:lsc-canfranc

### experiment:dmtpc - DMTPC (active)

- facility role: facility:wipp 2010-10 to  (approximate); https://arxiv.org/abs/1006.2928; quote: "The 10L detector described here began running underground at the Waste Isolation Pilot Plant outside Carlsbad, NM in October 2010. The depth of the WIPP site is 1.6 km water-equivalent."
- facility role: facility:mit  to  (approximate); https://arxiv.org/abs/1111.0220; quote: "To study detector backgrounds, a commissioning run was taken in a surface laboratory at MIT."
- commissioning 2007 to 2010-10 (approximate) development and surface-laboratory commissioning (10-L detector at MIT); https://arxiv.org/abs/1111.0220, https://arxiv.org/abs/0708.2370, https://arxiv.org/abs/1006.2928; quote: "To study detector backgrounds, a commissioning run was taken in a surface laboratory at MIT."
- active 2010-10 to  (uncertain) 10-L detector running underground at WIPP; https://arxiv.org/abs/1006.2928, https://arxiv.org/abs/1111.0220, https://arxiv.org/abs/1012.3912, https://arxiv.org/abs/2102.04596; quote: "The 10L detector described here began running underground at the Waste Isolation Pilot Plant outside Carlsbad, NM in October 2010. The depth of the WIPP site is 1.6 km water-equivalent."
- detector placement: site:mit-cambridge-campus
- detector placement: site:wipp-surface-campus

### experiment:drift - DRIFT (active)

- facility role: facility:boulby-underground-laboratory 2001 to  (uncertain); https://arxiv.org/abs/1110.0222; quote: "The DRIFT experiment has been operational at the Boulby Underground Laboratory in the UK since 2001"
- active 2001 to  (uncertain) DRIFT operation at Boulby; https://arxiv.org/abs/1110.0222; quote: "The DRIFT experiment has been operational at the Boulby Underground Laboratory in the UK since 2001"
- active 2009 to 2010 (approximate) DRIFT-IId run (47.4 live days); https://arxiv.org/abs/1110.0222; quote: "The current iteration (DRIFT II-d) collected 47.4 days of live-time data in 2009/10"
- detector placement: site:boulby-mine

### experiment:elegant-v-nai - ELEGANT V (NaI dark matter detector) (completed)

- facility role: facility:oto-cosmo-observatory 1997-04 to  (verified); https://www.rcnp.osaka-u.ac.jp/~annurep/2001/genkou/sec3/takahisa2.pdf; quote: "is used for ELEGANT V [3] from April in 1997."
- facility role: facility:kamioka-observatory 1992 to 1997-04 (uncertain); https://arxiv.org/abs/2607.24448; quote: "9 were assembled in 1992 and deployed at Kamioka Underground Laboratory."
- active 1992 to  (approximate) NaI modules deployed at the Kamioka underground laboratory (first configuration); https://arxiv.org/abs/2607.24448; quote: "9 were assembled in 1992 and deployed at Kamioka Underground Laboratory."
- active 1997-04 to  (verified) ELEGANT V in the Oto Cosmo Observatory (16 NaI scintillators, 0.76 tons); https://www.rcnp.osaka-u.ac.jp/~annurep/2001/genkou/sec3/takahisa2.pdf; quote: "is used for ELEGANT V [3] from April in 1997."
- completed 2006 to  (uncertain) completed (no end date published); https://arxiv.org/abs/astro-ph/0611700; quote: "thick old lead, which was used for the shield of ELEGANT V."
- detector placement: site:kamioka-mozumi-mine-super-kamiokande
- detector placement: site:oto-cosmo-observatory

### experiment:genius-tf - GENIUS-TF (completed)

- facility role: facility:lngs 2003-05-05 to 2006 (verified); https://arxiv.org/abs/hep-ph/0309170; quote: "After installation of the GENIUS-TF setup between halls A and B in Gran Sasso"
- proposed 2000-12 to 2001-03 (approximate) test facility proposed for LNGS; https://arxiv.org/abs/hep-ex/0012022; quote: "a small test version, the GENIUS test facility, will be build up at the Laboratorio Nazionale del Gran Sasso (LNGS)."
- approved 2001-03 to 2003-05-05 (verified) approved by the Gran Sasso Scientific Committee; funded; built; https://arxiv.org/abs/hep-ph/0309170; quote: "A small scale version of GENIUS, the GENIUS-Test-Facility has been approved by the Gran Sasso Scientific Committee in March 2001."
- active 2003-05-05 to 2006 (approximate) operation with four, then six, naked Ge detectors in liquid nitrogen; https://www.osti.gov/etdeweb/biblio/20565502, https://arxiv.org/abs/0812.1206; quote: "Since then the experiment has been running continuously, testing for the first time the novel technique in an underground laboratory and for a long-lasting period."
- completed 2006 to  (approximate) completed; https://arxiv.org/abs/0812.1206; quote: "the Genius-TF setup has run a total of six HPGe detectors during three years (2003–2006)"
- detector placement: site:lngs-hall-b

### experiment:hdms - HDMS (completed)

- facility role: facility:lngs 1998-03 to 2006 (approximate); https://arxiv.org/abs/astro-ph/0008339; quote: "The HDMS prototype was installed at LNGS in March 1998"
- active 1998-03 to 1999-07 (approximate) prototype detector (natural Ge crystals) at LNGS; https://arxiv.org/abs/astro-ph/0008339; quote: "The HDMS prototype was installed at LNGS in March 1998 and successfully took data over a period of about 15 month, until July 1999"
- upgrade 1999-07 to 2000-08 (approximate) inner crystal replaced by enriched 73Ge; final setup installed; https://arxiv.org/abs/hep-ph/0206151; quote: "the inner crystal of the detector has been replaced with a HPGe crystal of enriched 73 Ge"
- active 2000-08 to 2006 (approximate) final setup (enriched 73Ge inner crystal) taking data; https://arxiv.org/abs/hep-ph/0206151, https://www.osti.gov/etdeweb/biblio/20829911; quote: "The final setup started data taking in Gran Sasso in August 2000."
- completed 2006 to  (uncertain) completed (no shutdown date published); https://www.osti.gov/etdeweb/biblio/20829911; quote: "The HDMS (Heidelberg Dark Matter Search) setup at LNGS, operates the first enriched {sup 73}Ge detector worldwide"
- detector placement: site:lngs-hall-b

### experiment:herald - HeRALD (proposed)

- facility role: facility:modane-underground-laboratory 2024-01 to  (approximate); https://scoap3-prod-backend.s3.cern.ch/media/files/85193/10.1016/j.nuclphysb.2024.116465.pdf; quote: "Combined with the US-based SPICE and HeRALD technologies, the TESSERACT at LSM experiment will then allow to probe DM candidates over 12 orders of magnitude in mass"
- proposed 2018-10 to  (approximate) concept proposed (superfluid helium, calorimetric readout) and R&D; https://arxiv.org/abs/1810.06283; quote: "We name this concept “HeRALD”, helium roton apparatus for light dark matter."
- planned 2027 (planned) to 2028 (planned) (approximate) planned installation of the TESSERACT setups (including HeRALD) at LSM; https://indico-cdex.ep.tsinghua.edu.cn/event/175/contributions/2344/attachments/941/1407/TAUP2025%20(1).pdf; quote: "The two setups will be in LSM between 2027 and 2028"
- detector placement: site:lsm-frejus

### experiment:igex-dm - IGEX-DM (completed)

- facility role: facility:canfranc-underground-laboratory 2000 to 2002 (approximate); https://arxiv.org/abs/hep-ex/0002053; quote: "are currently operating in the Canfranc Underground Laboratory with an overburden of 2450 m.w.e. A recent upgrade has made it possible to use them in a search for WIMPs."
- active 2000 to 2002 (approximate) dark matter phase of IGEX at Canfranc (one enriched 76Ge detector); https://arxiv.org/abs/hep-ex/0002053, https://arxiv.org/abs/astro-ph/0211535; quote: "are currently operating in the Canfranc Underground Laboratory with an overburden of 2450 m.w.e. A recent upgrade has made it possible to use them in a search for WIMPs."
- completed 2002 to  (uncertain) completed (no end date published); https://arxiv.org/abs/astro-ph/0211535; quote: "The IGEX dark matter experiment is currently operating one germanium detector with this purpose in the Canfranc Underground Laboratory."
- detector placement: site:lsc-canfranc

### experiment:index-dm - InDEx (active)

- facility role: facility:jaduguda-underground-science-laboratory 2022-07 to  (approximate); https://arxiv.org/abs/2501.02833; quote: "installed at the 555m deep underground laboratory, JUSL during July to Dec 2022"
- commissioning 2022-07 to 2022-12 (approximate) installation and first run (JUSL); https://arxiv.org/abs/2501.02833; quote: "installed at the 555m deep underground laboratory, JUSL during July to Dec 2022"
- active 2022-12 to  (uncertain) InDEx runs (run 1 and run 2); https://arxiv.org/abs/2510.06921; quote: "The Indian Dark matter search Experiment (InDEx) has been initiated at Jaduguda Underground Science Laboratory (JUSL) to explore the low mass region of dark matter."
- detector placement: site:jaduguda-underground-science-laboratory

### experiment:kims - KIMS (completed)

- facility role: facility:yangyang-underground-laboratory 2003 to 2012-12 (verified); https://arxiv.org/abs/0704.0423; quote: "The KIMS experiment is located at the Yangyang Undeground Laboratory (Y2L) at a depth of 700 m under an earth overburden."
- construction 2003 to 2004-07 (approximate) Y2L and KIMS experiment constructed; https://link.springer.com/article/10.1007/s43673-024-00132-8; quote: "we have initiated non-accelerator astroparticle physics research with the construction of Y2L and the KIMS dark matter search experiment since 2003"
- active 2004-07 to 2012-12 (approximate) WIMP-search data taking with CsI(Tl) crystals; https://arxiv.org/abs/astro-ph/0509080; quote: "During the two-month period starting from July 2004, we have taken data for WIMP search using one crystal"
- active 2009-09 to 2012-12 (verified) stable running of the 12-crystal (103.4 kg) array; https://arxiv.org/abs/1404.3443; quote: "The 12 crystals operated stably between September 2009 and December 2012."
- completed 2012-12 to  (approximate) completed (CsI(Tl) data taking ended); https://arxiv.org/abs/1404.3443; quote: "In December 2012, the operation was temporarily halted in order to upgrade the detector modules."
- detector placement: site:y2l-yangyang

### experiment:kims-nai - KIMS-NaI (completed)

- facility role: facility:yangyang-underground-laboratory 2013-11 to 2016 (verified); https://arxiv.org/abs/1806.06499; quote: "The assembled detector modules are installed in the shielding structure that was used for the KIMS CsI(Tl) detector measurements at the Yangyang Underground Laboratory (Y2L)"
- active 2013-11 to 2015-01 (approximate) NaI(Tl) data taking for the published limits; https://arxiv.org/abs/1806.06499; quote: "The data were collected between November 2013 and January 2015 with configurations described in Ref. [25]."
- completed 2016 to  (uncertain) completed (succeeded by COSINE-100); https://arxiv.org/abs/1710.05299; quote: "KIMS and DM-Ice have joined to construct and operate a single experiment, named COSINE, at the Yangyang underground laboratory (Y2L) in Korea."
- detector placement: site:y2l-yangyang

### experiment:mimac - MIMAC (active)

- facility role: facility:modane-underground-laboratory 2012-06 to  (verified); https://arxiv.org/abs/1311.0616; quote: "The MIMAC bi-chamber prototype was installed at the Laboratoire Souterrain de Modane (LSM) in June 2012"
- construction 2007 to 2012-06 (approximate) project initiated at LPSC Grenoble; prototype development; https://arxiv.org/abs/1504.05865, https://arxiv.org/abs/1311.0616; quote: "The MIMAC experiment is a directional detection project initiated in 2007 at the Laboratoire de Physique Subatomique et de Cosmologie (LPSC Grenoble-France) [22] in collaboration with IRFU-Saclay, CPPM- Marseille, IRSN and recently the Tsinghua University."
- active 2012-06 to  (approximate) bi-chamber module operating at the Laboratoire Souterrain de Modane; https://arxiv.org/abs/1311.0616, https://arxiv.org/abs/2607.23527; quote: "The MIMAC bi-chamber prototype was installed at the Laboratoire Souterrain de Modane (LSM) in June 2012"
- active 2012-07-05 to 2012-10-12 (verified) first available bi-chamber data set at Modane; https://arxiv.org/abs/1311.0616; quote: "The first available data set of the bi-chamber prototype was started on July 5th 2012 and finished on October 12th 2012."
- detector placement: site:lsm-frejus

### experiment:miniclean - MiniCLEAN (completed)

- facility role: facility:snolab 2013 to 2019 (approximate); https://www.snolab.ca/experiment/miniclean/; quote: "MiniCLEAN began operating at SNOLAB in 2013 and began decommissioning in 2019."
- construction 2013 to 2014-03 (approximate) assembly at SNOLAB; https://www.snolab.ca/experiment/miniclean/, https://arxiv.org/abs/1403.4842; quote: "MiniCLEAN began operating at SNOLAB in 2013 and began decommissioning in 2019."
- commissioning 2014-03 to 2019 (approximate) final assembly, commissioning and cold-gas run; https://arxiv.org/abs/1403.4842, https://arxiv.org/abs/1903.06706, https://www.snolab.ca/experiment/miniclean/; quote: "The MiniCLEAN detector is undergoing finally assembly and commissioning at the SNOLAB facility in Sudbury, Canada."
- commissioning 2017-02 to 2017-04 (verified) cold argon gas run; https://arxiv.org/abs/1903.06706; quote: "Data used in this analysis were taken from February to April 2017"
- completed 2019 to  (approximate) completed (decommissioning began); https://www.snolab.ca/experiment/miniclean/; quote: "MiniCLEAN began operating at SNOLAB in 2013 and began decommissioning in 2019."
- detector placement: site:snolab-underground-lab

### experiment:moscab - MOSCAB (completed)

- facility role: facility:lngs 2021-06 to 2021-06 (uncertain); https://arxiv.org/abs/2106.13654; quote: "the apparatus was moved underground to the INFN Gran Sasso National Laboratories (LNGS)"
- commissioning 2014 to 2017-07 (uncertain) construction and surface commissioning at Milano-Bicocca; https://indico.ific.uv.es/event/2025/papers/1243/files/354-Article-MOSCAB-DM-ICHEP14.pdf; quote: "Here, we report as well in the construction and commissioning of the big detector of 40 kg at the Milano-Bicocca University."
- commissioning 2021-06 to 2021-06 (uncertain) background and neutron-sensitivity measurements underground at LNGS; https://arxiv.org/abs/2106.13654; quote: "the apparatus was moved underground to the INFN Gran Sasso National Laboratories (LNGS)"
- completed 2021-06 to  (uncertain) completed as a dark matter search (equipment repurposed for fast neutrons); https://arxiv.org/abs/2106.13654; quote: "MOSCAB equipment, a geyser-concept bubble-chamber originally thought for the search of dark matter in the form of WIMPs"
- detector placement: site:lngs-hall-b

### experiment:naiad - NaIAD (completed)

- facility role: facility:boulby-underground-laboratory 2000 to 2003 (verified); https://arxiv.org/abs/hep-ex/0504031; quote: "The NAIAD experiment (NaI Advanced Detector) for WIMP dark matter searches at the Boulby Underground Laboratory (North Yorkshire, UK) ran from 2000 until 2003."
- active 2000 to 2003 (verified) NaIAD operation; https://arxiv.org/abs/hep-ex/0504031; quote: "The NAIAD experiment (NaI Advanced Detector) for WIMP dark matter searches at the Boulby Underground Laboratory (North Yorkshire, UK) ran from 2000 until 2003."
- completed 2003 to  (approximate) completed; https://arxiv.org/abs/hep-ex/0504031; quote: "The NAIAD experiment (NaI Advanced Detector) for WIMP dark matter searches at the Boulby Underground Laboratory (North Yorkshire, UK) ran from 2000 until 2003."
- detector placement: site:boulby-mine

### experiment:newage - NEWAGE (active)

- facility role: facility:kamioka-observatory 2008-09 to  (verified); https://arxiv.org/abs/1002.1794; quote: "The first underground dark matter run with the NEWAGE-0.3a detector took place from September 11, 2008 until December 4, 2008 in Laboratory B, Kamioka Observatory"
- construction 2003 to 2007 (approximate) project start and development of the micro-TPC (surface-laboratory phase); https://arxiv.org/abs/1109.3099, https://arxiv.org/abs/2301.04779; quote: "We started a new project, NEw generation WIMP-search with Advanced Gaseous tracking device Experiment (NEWAGE) in 2003"
- active 2007 to  (approximate) underground direction-sensitive WIMP searches; https://arxiv.org/abs/2301.04779, https://indico.capa.unizar.es/event/40/contributions/849/; quote: "NEWAGE started direction-sensitive direct WIMP searches in an underground laboratory in 2007 and has updated the results since then."
- active 2008-09-11 to 2008-12-04 (verified) NEWAGE-0.3a first underground dark matter run (Run5, 0.524 kg d); https://arxiv.org/abs/1002.1794; quote: "The first underground dark matter run with the NEWAGE-0.3a detector took place from September 11, 2008 until December 4, 2008 in Laboratory B, Kamioka Observatory"
- active 2013-07 to 2017-08 (verified) NEWAGE-0.3b' run (Run14 to Run18, 434.85 live days); https://arxiv.org/abs/2005.05157; quote: "The search was carried out from July 2013 to August 2017 (Run14 to Run18) at the Kamioka underground laboratory."
- active 2017-12-12 to 2020-03-26 (verified) NEWAGE-0.3b'' run (eight periods, 318.0 live days); https://arxiv.org/abs/2301.04779; quote: "The measurement was carried out from December 12th, 2017 to March 26th, 2020, subdivided into eight periods."
- commissioning 2025 to  (approximate) upgraded low-RI detector installed, final commissioning started; https://indico-cdex.ep.tsinghua.edu.cn/event/175/contributions/2158/; quote: "The new detector was installed in the Kamioka underground observatory and the final commissioning was started."
- detector placement: site:kamioka-mozumi-mine-super-kamiokande

### experiment:newsdm - NEWSdm (commissioning)

- facility role: facility:lngs 2021 to  (approximate); https://pos.sissa.it/414/253/pdf; quote: "Several demonstration runs of the NEWSdm experiment were conducted at LNGS from 2021 to 2022 as a proof-of-principle."
- proposed 2016-04 to 2021 (approximate) NEWS letter of intent to LNGS and emulsion-facility construction; https://arxiv.org/abs/1604.04199, https://pos.sissa.it/414/253/pdf; quote: "Submitted on 14 Apr 2016"
- commissioning 2021 to  (uncertain) demonstration and pilot runs at LNGS (equatorial-telescope run in progress in 2024); https://pos.sissa.it/414/253/pdf, https://indico.cern.ch/event/1291157/contributions/5879766; quote: "Several demonstration runs of the NEWSdm experiment were conducted at LNGS from 2021 to 2022 as a proof-of-principle."
- detector placement: site:lngs-hall-c

### experiment:orpheus - ORPHEUS (completed)

- facility role: facility:bern-underground-laboratory 1999 to 2005 (approximate); https://arxiv.org/abs/hep-ex/9911028; quote: "in the Bern Underground Laboratory at 70 m.w.e."
- construction 1999 to 2002 (approximate) set-up of the 1 kg SSG detector; https://arxiv.org/abs/hep-ex/9911028; quote: "the ORPHEUS collaboration is setting up a 1kg SSG detector"
- active 2002 to 2005 (approximate) operation of the 0.45 kg SSG detector; https://arxiv.org/abs/astro-ph/0404311; quote: "The ORPHEUS dark matter detector is operating at our underground laboratory in Bern (70 m.w.e.)."
- active 2002 to 2002 (verified) run of two months at 170 mK; https://arxiv.org/abs/astro-ph/0404311; quote: "We were able to take data continuously during two months in 2002 at a temperature of 170 mK"
- active 2003 to 2003 (verified) run of three weeks at 115 mK; https://arxiv.org/abs/astro-ph/0404311; quote: "and during 3 weeks in 2003 at 115 mK"
- completed 2005 to  (uncertain) completed (no later activity found); https://arxiv.org/abs/physics/0502065; quote: "and with SSG of 0.5 kg (ORPHEUS) are in operation"
- detector placement: site:bern-underground-laboratory

### experiment:oscura - Oscura (proposed)

- facility role: facility:snolab 2023-04 to  (approximate); https://arxiv.org/abs/2304.04401; quote: "Oscura is planning to operate at SNOLAB with 2070 m overburden"
- proposed 2020 to  (approximate) R&D, conceptual design and design stage (not yet funded for construction); https://arxiv.org/abs/2202.10518; quote: "The R&D effort, which began in FY20, is currently entering the design phase with the goal of being ready to start construction in late 2024."
- detector placement: site:snolab-underground-lab

### experiment:pandax-i - PandaX-I (completed)

- facility role: facility:cjpl 2014-05-26 to 2014-10-16 (verified); https://arxiv.org/abs/1408.5114; quote: "PandaX-I, a low threshold dual-phase xenon experiment operating at the China Jinping Underground Laboratory"
- active 2014-05-26 to 2014-10-16 (verified) WIMP search run (80.1 live days); https://arxiv.org/abs/1505.00771; quote: "the full PandaX-I data set, starting from May 26, 2014 to Oct. 16, 2014, with a total of 80.1 live-day exposure"
- completed 2014-10 to  (approximate) completed; https://arxiv.org/abs/1505.00771; quote: "the full PandaX-I data set, starting from May 26, 2014 to Oct. 16, 2014, with a total of 80.1 live-day exposure"
- detector placement: site:cjpl-i

### experiment:pandax-ii - PandaX-II (completed)

- facility role: facility:cjpl 2015-11-21 to 2019-06-29 (verified); https://arxiv.org/abs/1607.07400; quote: "We report the WIMP dark matter search results using the first physics-run data of the PandaX-II 500 kg liquid xenon dual-phase time-projection chamber, operating at the China JinPing Underground Laboratory."
- construction 2014-10 to 2015-11 (uncertain) construction and installation; https://arxiv.org/abs/1602.06563; quote: "The construction and installation of the second stage of the PandaX experiment, PandaX-II, with a half-ton scale LXe target, commenced after PandaX-I."
- commissioning 2015-11-21 to 2015-12-14 (verified) commissioning run; https://arxiv.org/abs/1602.06563; quote: "A brief physics commissioning run was taken from Nov. 21 to Dec. 14, 2015"
- active 2016-03 to 2019-06-29 (approximate) physics runs (Runs 9-11) and calibration; https://arxiv.org/abs/2007.15469; quote: "including all data from March 2016 to August 2018"
- completed 2019-06-29 to  (verified) completed (official shutdown); https://arxiv.org/abs/2007.15469; quote: "before the official shutdown of PandaX-II on June 29, 2019"
- detector placement: site:cjpl-i

### experiment:pandax-xt - PandaX-xT (proposed)

- facility role: facility:cjpl 2024-02 to  (approximate); https://arxiv.org/abs/2402.03596; quote: "We propose a major upgrade to the existing PandaX-4T experiment in the China Jinping Underground Laboratory."
- proposed 2024-02 to  (approximate) proposal; https://arxiv.org/abs/2402.03596; quote: "We propose a major upgrade to the existing PandaX-4T experiment in the China Jinping Underground Laboratory."
- detector placement: site:cjpl-ii

### experiment:picasso - PICASSO (completed)

- facility role: facility:snolab 2002-07 to 2014-01 (verified); https://arxiv.org/abs/hep-ex/0312049; quote: "In July 2002, a new phase of the project started. A batch of six 1-liter detectors with an active mass of approximately 40g was installed in a gallery of the SNO observatory in Sudbury"
- active 2002-07 to 2014-01 (verified) data taking in the SNO gallery and at SNOLAB; https://arxiv.org/abs/hep-ex/0312049; quote: "In July 2002, a new phase of the project started. A batch of six 1-liter detectors with an active mass of approximately 40g was installed in a gallery of the SNO observatory in Sudbury"
- active 2007-06 to 2008-07 (verified) runs behind the 2009 two-detector result; https://arxiv.org/abs/0907.0307; quote: "The runs used for this analysis covered the period from June 2007 until July 2008"
- active 2012-03 to 2014-01 (verified) final data taking with 32 detector modules; https://arxiv.org/abs/1611.01499; quote: "Data taking with the upgraded set of 32 detector modules started in March 2012 and concluded in January 2014"
- completed 2014-01 to  (approximate) completed (data taking concluded; collaboration merged into PICO); https://arxiv.org/abs/1611.01499; quote: "collected an exposure of 231.4 kgd at SNOLAB between March 2012 and January 2014"
- detector placement: site:snolab-underground-lab

### experiment:pico-2l - PICO-2L (decommissioned)

- facility role: facility:snolab 2013-10-28 to 2016 (approximate); https://arxiv.org/abs/1503.00008; quote: "The PICO Collaboration (formed from the merger of PICASSO and COUPP) has now operated a 2.90 kg C3 F8 bubble chamber from October 2013 to May 2014 in the SNOLAB underground laboratory in Canada, at 6010 meters of water equivalent depth."
- active 2013-10-28 to 2015-11 (verified) data taking (runs 1 and 2); https://indico.phys.hawaii.edu/event/456/contributions/1948/attachments/1489/1774/PICO_CosPA2013_Neilson.pdf, https://www.picoexperiment.com/pico-2l/; quote: "Dark-matter data taking began Oct 28th, 2013."
- decommissioned 2016 to  (verified) decommissioned; https://www.picoexperiment.com/pico-2l/; quote: "PICO 2L was decommissioned in 2016."
- active 2013-10 to 2014-05 (verified) run 1 (3.2-8.1 keV thresholds); https://www.picoexperiment.com/pico-2l/; quote: "The first run of PICO-2L lasted from October 2013 to May 2014."
- active 2015-02 to 2015-11 (verified) run 2 (3.3 keV threshold); https://www.picoexperiment.com/pico-2l/; quote: "Run 2 ended in November 2015, and in January 2016 PICO reported the 2L bubble chamber was background free."
- detector placement: site:snolab-underground-lab

### experiment:pico-40l - PICO-40L (active)

- facility role: facility:snolab 2019 to  (verified); https://www.picoexperiment.com/pico-40l/; quote: "The detector began construction at SNOLAB in 2019 and was finished in 2020."
- construction 2019 to 2020 (verified) construction at SNOLAB; https://www.picoexperiment.com/pico-40l/; quote: "The detector began construction at SNOLAB in 2019 and was finished in 2020."
- upgrade 2021 to 2022 (verified) updates after the first phase; https://www.picoexperiment.com/pico-40l/; quote: "Based on lessons from that first phase, updates were made to the detector in 2021-2022."
- commissioning 2023 to 2023 (verified) commissioning; https://www.picoexperiment.com/pico-40l/; quote: "The next phase of PICO-40L began commissioning in 2023 and operations later that year."
- active 2023 to  (verified) operations; https://indico.fnal.gov/event/72820/contributions/341032/attachments/199654/278253/DPF_2026_PICO.pdf, https://www.picoexperiment.com/pico-40l/, https://www.picoexperiment.com/; quote: "Located at SNOLAB, running since 2023"
- detector placement: site:snolab-underground-lab

### experiment:pico-500 - PICO-500 (construction)

- facility role: facility:snolab 2018-06 to  (approximate); https://arxiv.org/abs/1806.01417; quote: "PICO-500 is a ton-scale bubble chamber to be deployed underground at SNOLAB that is currently in the design"
- approved 2018-06 to 2024-09 (approximate) funded; in design; https://arxiv.org/abs/1806.01417, https://arxiv.org/abs/1905.07367, https://web.archive.org/web/20240415002242/https://www.picoexperiment.com/pico-500/; quote: "supernova neutrinos via CEνNS using the example of the funded PICO-500 experiment"
- construction 2024-09 to 2027 (planned) (approximate) assembly and construction at SNOLAB (Cube Hall); https://indico.global/event/652/contributions/16913/, https://www.picoexperiment.com/pico-500/, https://cinp.ca/sites/default/files/2026-06/SNOLAB_2026CAP.pdf, https://indico.fnal.gov/event/72820/contributions/341032/attachments/199654/278253/DPF_2026_PICO.pdf, https://web.archive.org/web/20240415002242/https://www.picoexperiment.com/pico-500/; quote: "The PICO collaboration is in the process of deploying PICO-500, a large 250 litre chamber filled with C3F8 at SNOLAB"
- detector placement: site:snolab-underground-lab

### experiment:pico-60 - PICO-60 (decommissioned)

- facility role: facility:fermilab 2010 to 2012 (approximate); https://arxiv.org/abs/2401.07384; quote: "The COUPP 60 kg bubble chamber recently completed a successful engineering run at the MINOS near detector hall at Fermilab."
- facility role: facility:snolab 2012 to 2017 (approximate); https://astro.fnal.gov/new-world-leading-limit-on-dark-matter-search-from-pico-experiment/; quote: "Work began at Fermilab in 2005, and, after extensive testing, the detector was moved to SNOLAB in 2012."
- commissioning 2010 to 2012 (approximate) COUPP-60 commissioning and engineering run at Fermilab (MINOS near-detector hall); https://arxiv.org/abs/1008.3518, https://arxiv.org/abs/2401.07384; quote: "At the time of this writing, a 60 kg CF3 I COUPP bubble chamber is being commissioned."
- commissioning 2012 to 2013-06 (approximate) installation and commissioning at SNOLAB; https://astro.fnal.gov/new-world-leading-limit-on-dark-matter-search-from-pico-experiment/, https://indico.phys.hawaii.edu/event/456/contributions/1948/; quote: "Work began at Fermilab in 2005, and, after extensive testing, the detector was moved to SNOLAB in 2012."
- active 2013-06 to 2014-05 (verified) run 1 (CF3I); https://arxiv.org/abs/1510.07754; quote: "We report results from the first run of PICO-60, with a dark matter exposure of 3415 kg-days taken at SNOLAB between June 2013 and May 2014."
- upgrade 2014-07 to 2016 (verified) refurbishment (data taking suspended); https://www.picoexperiment.com/pico-60/; quote: "Between the summer of 2014 and 2016, data taking was suspended to allow the PICO-60 detector to be upgraded, cleaned, and refurbished."
- active 2016 to 2017-07 (verified) run 2 (C3F8); https://www.picoexperiment.com/pico-60/; quote: "Data taking resumed in 2016, but for run 2 the target was filled with C3F8 to improve the sensitivity to spin dependent dark matter interactions."
- decommissioned 2017 to  (verified) decommissioned; https://www.picoexperiment.com/pico-60/; quote: "PICO-60 was decommissioned after the end of the data taking in the summer of 2017."
- active 2016-11 to 2017-01 (verified) C3F8 first blind exposure (1167 kg-days at 3.3 keV); https://arxiv.org/abs/1702.07666; quote: "of 1167 kg-days, taken between November 2016 and January 2017."
- active 2017-04 to 2017-06 (verified) C3F8 second blind exposure (1404 kg-days at 2.45 keV); https://arxiv.org/abs/1902.04031; quote: "a second blind exposure was acquired between April and June 2017 at a threshold of 2.45 keV"
- detector placement: site:fermilab-main-campus
- detector placement: site:snolab-underground-lab

### experiment:picolon - PICOLON (active)

- facility role: facility:kamioka-observatory 2015 to  (approximate); https://arxiv.org/abs/1512.04645; quote: "The low background measurement was started in the summer of 2015 in Kamioka underground laboratory"
- construction 2006 to 2015 (approximate) R&D: thin multilayer NaI(Tl) detectors and radiopure crystals; first low-background measurement at Oto Cosmo Observatory (from September 2007); https://arxiv.org/abs/astro-ph/0611700; quote: "The WIMPs search project PICO-LON has been started with multilayer thin NaI(Tl) crystals."
- active 2015 to  (approximate) low-background measurements in the KamLAND area of the Kamioka underground laboratory; https://arxiv.org/abs/1512.04645; quote: "The low background measurement was started in the summer of 2015 in Kamioka underground laboratory"
- detector placement: site:kamioka-kamland
- detector placement: site:oto-cosmo-observatory

### experiment:rosebud - ROSEBUD (completed)

- facility role: facility:canfranc-underground-laboratory 1999 to 2011 (approximate); https://arxiv.org/abs/astro-ph/0112272; quote: "The ROSEBUD experiment for Direct Dark Matter detection settled in 1999 in the Canfranc Underground Laboratory."
- active 1999 to 2011 (approximate) WIMP search with cryogenic bolometers at the (old) Canfranc laboratory; https://arxiv.org/abs/astro-ph/0112272; quote: "The ROSEBUD experiment for Direct Dark Matter detection settled in 1999 in the Canfranc Underground Laboratory."
- completed 2011 to  (uncertain) completed (no end date published); https://indico.ific.uv.es/event/433/contributions/6777/attachments/4486/5019/ROSEBUD_CPAN2011.pdf; quote: "ROSEBUD is currently moving to the Hall B in the new LSC facilities planning to restart measurements in 2012."
- detector placement: site:lsc-canfranc

### experiment:sabre-north - SABRE North (construction)

- facility role: facility:lngs 2018 to  (approximate); https://arxiv.org/abs/1807.08073; quote: "The first phase of the experiment is the SABRE Proof of Principle (PoP), a single 5kg crystal detector operated in a liquid scintillator filled vessel at Laboratori Nazionali del Gran Sasso (LNGS)."
- proposed 2016 to 2018 (approximate) proposal (twin NaI(Tl) detectors at LNGS and SUPL); https://arxiv.org/abs/1601.05307; quote: "The SABRE experiment aims to shed light on this controversy by detecting the annual modulation in the same target material as DAMA with twin detectors at LNGS in Italy and at SUPL in Australia."
- construction 2018 to 2020 (approximate) Proof-of-Principle (PoP) installation at LNGS; https://arxiv.org/abs/1807.08073; quote: "The PoP installation is underway with the goal of running in 2018 and performing the first in situ measurement of the crystal background and testing the veto efficiency, thus validating the SABRE concept."
- construction 2020 to 2022-02 (approximate) PoP and PoP-dry runs with the crystal NaI-33 (prototype data taking); https://arxiv.org/abs/2205.13849; quote: "The SABRE Proof-of-Principle phase was carried out in 2020-2021 at the Gran Sasso National Laboratory (LNGS), in Italy."
- construction 2022 to  (approximate) SABRE North physics detector: facilities, crystal production and installation at LNGS; https://indico.in2p3.fr/event/31806/contributions/136793/attachments/84092/125385/Terascale_SABRE_Tomei.pdf; quote: "SABRE North facilities @LNGS (2022-2023)"
- planned 2028 (planned) to  (approximate) planned physics data taking; https://indico.gssi.it/event/931/contributions/2969/attachments/1616/2858/SABRE_12.02.2026.pdf; quote: "Data taking starts in 2028"
- detector placement: site:lngs-hall-b
- detector placement: site:lngs-hall-c

### experiment:sabre-south - SABRE South (construction)

- facility role: facility:stawell-underground-physics-laboratory 2024 to  (approximate); https://arxiv.org/abs/2411.13889; quote: "The SABRE South detector is hosted at the Stawell Underground Physics Laboratory (SUPL), which"
- proposed 2016 to 2024 (approximate) proposal (twin NaI(Tl) detectors at LNGS and SUPL); https://arxiv.org/abs/1605.03299; quote: "I will discuss the status of the proposed SABRE experiment, which will be comprised of a pair of high purity 50-60 kg NaI crystal detectors with active veto shielding to be located in labs in the Northern and Southern Hemispheres respectively."
- construction 2024 to  (approximate) installation and assembly of SABRE South in SUPL; https://arxiv.org/abs/2411.13889; quote: "The construction of SUPL was completed in 2023, with the first access for SABRE South installation activities in early 2024."
- planned 2027-01 (planned) to  (approximate) planned stable physics data taking; https://indico.global/event/16402/contributions/164062/; quote: "Once stable data taking begins in January 2027, SABRE South will deliver a definitive test of the DAMA/LIBRA annual modulation signal at high statistical significance."
- detector placement: site:stawell-underground-physics-laboratory

### experiment:sbc - Scintillating Bubble Chamber (SBC) (construction)

- facility role: facility:snolab 2022-07 to  (approximate); https://arxiv.org/abs/2207.12400, https://arxiv.org/abs/2310.00442; quote: "A second functionally-identical detector with a focus on radiopure construction is being built for SBC's first dark matter search at SNOLAB."
- facility role: facility:fermilab 2021-02 to  (approximate); https://pos.sissa.it/390/632/, https://pos.sissa.it/441/337/, https://dm.ci.northwestern.edu/talks/2026_APS_Zhiheng.pdf; quote: "In this paper, we will present the overall design of the SBC experiment and provide an update on the ongoing construction at the Fermilab site."
- construction 2021-02 to  (approximate) construction (SBC-LAr10 at Fermilab; SBC-SNOLAB for the dark-matter search); https://pos.sissa.it/390/632/, https://arxiv.org/abs/2310.00442, https://dm.ci.northwestern.edu/talks/2026_APS_Zhiheng.pdf; quote: "In this paper, we will present the overall design of the SBC experiment and provide an update on the ongoing construction at the Fermilab site."
- active 2025-09 to  (verified) SBC-LAr10 calibration chamber operating at Fermilab (MINOS tunnel); https://dm.ci.northwestern.edu/talks/2026_APS_Zhiheng.pdf; quote: "10kg calibration chamber currently operating in MINOS underground tunnel"
- detector placement: site:fermilab-main-campus
- detector placement: site:snolab-underground-lab

### experiment:simple - SIMPLE (completed)

- facility role: facility:lsbb-rustrel 1999-07 to 2010-07 (verified); https://arxiv.org/abs/1404.4309; quote: "GESA site (505 m depth) of the Laboratoire Souterrain à Bas Bruit (LSBB) in southern France"
- active 1999-07 to 2010-07 (approximate) operation at the LSBB (prototype 1999-2000, Phase I 2004-2007, Phase II 2009-2010); https://arxiv.org/abs/astro-ph/0001511; quote: "started in July 1999. A decommissioned nuclear missile control center has been converted into an underground laboratory"
- active 2004 to 2007 (approximate) Phase I measurements in the GESA cavern; https://arxiv.org/abs/1504.05475; quote: "A preliminary evaluation of the original SIMPLE set-up in GESA (Phase I, 2004-2007)"
- active 2009-11-14 to 2010-02-05 (verified) Phase II Stage 1 science measurement; https://arxiv.org/abs/1404.4309; quote: "science measurements conducted between 14 November 2009 - 05 February 2010 (Stage 1) and 01 May - 22 July 2010 (Stage 2)"
- active 2010-05-01 to 2010-07-22 (approximate) Phase II Stage 2 science measurement; https://arxiv.org/abs/1404.4309; quote: "science measurements conducted between 14 November 2009 - 05 February 2010 (Stage 1) and 01 May - 22 July 2010 (Stage 2)"
- completed 2010-07 to  (uncertain) completed (last dated science measurement); https://arxiv.org/abs/1404.4309; quote: "science measurements conducted between 14 November 2009 - 05 February 2010 (Stage 1) and 01 May - 22 July 2010 (Stage 2)"
- detector placement: site:lsbb-rustrel

### experiment:spice - SPICE (proposed)

- facility role: facility:modane-underground-laboratory 2024-01 to  (approximate); https://scoap3-prod-backend.s3.cern.ch/media/files/85193/10.1016/j.nuclphysb.2024.116465.pdf; quote: "Combined with the US-based SPICE and HeRALD technologies, the TESSERACT at LSM experiment will then allow to probe DM candidates over 12 orders of magnitude in mass"
- proposed 2021-08 to  (approximate) SPICE/HeRALD R&D; proposed for LSM as a TESSERACT module; https://arxiv.org/abs/2108.02176; quote: "(SPICE/HeRALD Collaboration)"
- planned 2027 (planned) to 2028 (planned) (approximate) planned installation of the TESSERACT setups (including SPICE) at LSM; https://indico-cdex.ep.tsinghua.edu.cn/event/175/contributions/2344/attachments/941/1407/TAUP2025%20(1).pdf; quote: "The two setups will be in LSM between 2027 and 2028"
- detector placement: site:lsm-frejus

### experiment:tesseract - TESSERACT (proposed)

- facility role: facility:modane-underground-laboratory 2022 to  (approximate); https://scoap3-prod-backend.s3.cern.ch/media/files/85193/10.1016/j.nuclphysb.2024.116465.pdf; quote: "Since early 2022, the French CNRS-IN2P3 laboratories IP2I, LPSC, and IJCLab are discussing with the USA-based TESSERACT collaboration in order to 1) install a dedicated cryostat for TESSERACT at the underground Modane Laboratory (LSM)"
- proposed 2022 to  (approximate) proposed experiment with a dedicated cryostat at LSM; https://scoap3-prod-backend.s3.cern.ch/media/files/85193/10.1016/j.nuclphysb.2024.116465.pdf; quote: "Since early 2022, the French CNRS-IN2P3 laboratories IP2I, LPSC, and IJCLab are discussing with the USA-based TESSERACT collaboration in order to 1) install a dedicated cryostat for TESSERACT at the underground Modane Laboratory (LSM)"
- planned 2027 (planned) to 2028 (planned) (approximate) planned installation of the two TESSERACT setups at LSM; https://indico-cdex.ep.tsinghua.edu.cn/event/175/contributions/2344/attachments/941/1407/TAUP2025%20(1).pdf; quote: "The two setups will be in LSM between 2027 and 2028"
- planned 2028 (planned) to  (approximate) planned full integration of the TESSERACT setup at LSM; https://indico.capa.unizar.es/event/40/contributions/919/; quote: "Full integration of the TESSERACT setup at the Modane Underground Laboratory (LSM) is planned for 2028."
- detector placement: site:lsm-frejus

### experiment:texono - TEXONO (active)

- facility role: facility:kuo-sheng-reactor-neutrino-laboratory 2001-07 to  (verified); https://arxiv.org/abs/1608.00306; quote: "The Kuo-Sheng Reactor Neutrino Laboratory (KSNL) is located at a distance of 28 m from the core #1 of the Kuo-Sheng Nuclear Power Station operated by the Taiwan Power Company at the northern shore of Taiwan."
- proposed 1997 to 2000 (verified) conceptual design and construction of the Kuo-Sheng laboratory; https://arxiv.org/abs/1608.00306; quote: "Conceptual design discussions were initiated in 1997."
- commissioning 2000 to 2001-07 (approximate) laboratory built and commissioned; https://newsletter.sinica.edu.tw/reviews/en/news/read_news2eae.html?nid=3269; quote: "It built and commissioned the “Kuo-Sheng Reactor Neutrino Laboratory” at Nuclear Power Station II on the northern coast of Taiwan in 2000."
- active 2001-07 to  (approximate) operation at Kuo-Sheng (neutrino physics from July 2001; germanium dark-matter programme added 2004); https://arxiv.org/abs/1608.00306, https://arxiv.org/abs/2606.16864, https://newsletter.sinica.edu.tw/reviews/en/news/read_news2eae.html?nid=3269; quote: "First physics data taking started in July 2001."
- detector placement: site:ksnl-kuo-sheng-nuclear-power-station

### experiment:tokyo-dark-matter-search - Tokyo Dark Matter Search (completed)

- facility role: facility:kamioka-observatory 2000 to 2003 (approximate); https://arxiv.org/abs/astro-ph/0204411; quote: "The Tokyo group has performed the first underground dark matter search experiment from 2001 through 2002 at Kamioka Observatory(2700m.w.e)."
- commissioning 2000 to 2001-11-22 (approximate) detector system installed at Kamioka; LiF bolometer improved; https://arxiv.org/abs/astro-ph/0204411; quote: "since we installed the detector system in 2000 at Kamioka Observatory (2700m.w.e)"
- active 2001-11-22 to 2003 (approximate) underground dark matter runs with LiF (2001-2002) and NaF (2002-2003) bolometer arrays; https://arxiv.org/abs/astro-ph/0204411, https://arxiv.org/abs/astro-ph/0306365; quote: "The measurement was performed from November 22, 2001 through January 12, 2002."
- completed 2003 to  (uncertain) completed (no end date published); https://arxiv.org/abs/astro-ph/0306365; quote: "We have performed the underground dark matter search experiment with a sodium fluoride (NaF) bolometer array from 2002 through 2003 at Kamioka Observatory (2700 m.w.e.)."
- detector placement: site:kamioka-mozumi-mine-super-kamiokande

### experiment:trex-dm - TREX-DM (active)

- facility role: facility:canfranc-underground-laboratory 2017 to  (approximate); https://gifna.unizar.es/trex/?page_id=28; quote: "During 2017 into 2018 the experiment was installed at the hall A of LSC."
- approved 2017 to 2017 (approximate) approved by the LSC; https://gifna.unizar.es/trex/?page_id=28; quote: "The experiment was approved by the LSC at the beginning of 2017."
- construction 2017 to 2018 (approximate) installation in Hall A of the LSC; https://gifna.unizar.es/trex/?page_id=28; quote: "During 2017 into 2018 the experiment was installed at the hall A of LSC."
- commissioning 2018 to 2019 (approximate) commissioning and first engineering runs in Hall A; https://gifna.unizar.es/trex/?page_id=28; quote: "End of 2018 the experiment has started its first engineering runs at low pressure, and it faces the first physics runs for 2019."
- active 2019 to 2022-10 (approximate) data-taking campaigns in Hall A; https://arxiv.org/abs/2312.12622; quote: "during the 2019-2022 data taking campaigns"
- shutdown 2022-10 to 2023-07 (approximate) dismounted at the request of the LSC and re-installed in Lab2500; https://arxiv.org/abs/2312.12622; quote: "In October 2022, when the parts with surface contamination were going to be replaced, the experiment was completely dismounted after the request of the LSC management"
- active 2023-07 to  (approximate) data taking in Lab2500; https://arxiv.org/abs/2312.12622; quote: "the detector has been taking data, from July 2023"
- detector placement: site:lsc-canfranc

### experiment:warp - WArP (completed)

- facility role: facility:lngs 2004 to 2011 (approximate); https://arxiv.org/abs/astro-ph/0701286; quote: "This preliminary search for WIMP events has been performed at the Gran Sasso Laboratory with a small 2.3 litre table-top test chamber"
- approved 2004 to 2005 (verified) 100-litre detector approved and funded by INFN; https://arxiv.org/abs/astro-ph/0411491; quote: "The construction of the 100 liters detector has been approved and funded by INFN starting from 2004"
- construction 2005 to 2008 (approximate) construction and assembly of the 100-litre detector; https://arxiv.org/abs/1207.2292, https://iris.unipv.it/handle/11571/1165202; quote: "Construction of the 100-liter detector started in 2005 and by 2009 the detector had been commissioned at LNGS"
- commissioning 2008 to 2011 (approximate) commissioning and technical runs of the 100-litre detector; https://arxiv.org/abs/1207.2292, http://warp.lngs.infn.it/, https://iris.unipv.it/handle/11571/1165202; quote: "a second test was conducted in 2010, but high voltage problems persisted. No update on WARP140 has been reported recently."
- active 2005 to 2005 (approximate) 2.3-litre prototype WIMP-search data; https://arxiv.org/abs/1207.2292, https://arxiv.org/abs/astro-ph/0701286; quote: "from the 2.3-liter prototype were acquired in 2005"
- commissioning 2009 to 2011 (approximate) 100-litre technical runs; http://warp.lngs.infn.it/, https://iris.unipv.it/handle/11571/1165202; quote: "07/05/09:Started 100 liter filling procedure."
- completed 2011 to  (uncertain) completed (no physics run; programme ended without further reports); https://iris.unipv.it/handle/11571/1165202, https://arxiv.org/abs/1207.2292; quote: "Though it never actually performed a physics run, a technical run was taken in 2011, to characterise the detector response."
- detector placement: site:lngs-hall-b

### experiment:xenon10 - XENON10 (completed)

- facility role: facility:lngs 2006 to 2007 (approximate); https://xenonexperiment.org/history/; quote: "XENON10 (operated 2006 – 2007)"
- construction 2002 to 2006 (approximate) prototype development; https://xenonexperiment.org/history/; quote: "The development of the prototype detector XENON10 (operated 2006 – 2007) started in 2002 with a small group of scientists led by Professor Elena Aprile."
- active 2006 to 2007 (approximate) XENON10 operation; https://xenonexperiment.org/history/; quote: "XENON10 (operated 2006 – 2007)"
- active 2006-10-06 to 2007-02-14 (verified) WIMP search run (58.6 live days); https://arxiv.org/abs/0706.0039; quote: "A blind analysis of 58.6 live days of data, acquired between October 6, 2006 and February 14, 2007"
- completed 2007 to  (approximate) completed; https://xenonexperiment.org/history/; quote: "XENON10 (operated 2006 – 2007)"
- detector placement: site:lngs-hall-b

### experiment:xenon100 - XENON100 (completed)

- facility role: facility:lngs 2008 to 2016 (approximate); https://xenonexperiment.org/history/; quote: "first XENON100 operated with roughly 160 kg of xenon from 2008 until 2016"
- commissioning 2008 to 2009-10 (approximate) installation and commissioning at LNGS; https://arxiv.org/abs/0902.4253, https://xenonexperiment.org/history/; quote: "is currently in commissioning phase"
- active 2009-10 to 2016 (approximate) science operations; https://xenonexperiment.org/history/, https://arxiv.org/abs/1005.0380; quote: "first XENON100 operated with roughly 160 kg of xenon from 2008 until 2016"
- active 2009-10 to 2009-11 (verified) first science run (11.17 live days); https://arxiv.org/abs/1005.0380; quote: "11.17 live days of non-blind data, acquired in October and November 2009"
- active 2010-01 to 2010-06 (verified) second run (100.9 live days); https://arxiv.org/abs/1104.2549; quote: "In 100.9 live days of data, acquired between January and June 2010"
- active 2011 to 2012 (verified) third run (224.6 live days); https://arxiv.org/abs/1207.5988; quote: "operated at the Laboratori Nazionali del Gran Sasso (LNGS) for 13 months during 2011 and 2012"
- completed 2016 to  (approximate) completed; https://xenonexperiment.org/history/; quote: "first XENON100 operated with roughly 160 kg of xenon from 2008 until 2016"
- detector placement: site:lngs-hall-b

### experiment:xmass - XMASS (completed)

- facility role: facility:kamioka-observatory 2007-04 to 2019-02 (verified); https://arxiv.org/abs/1301.2815; quote: "The XMASS detector is located at the Kamioka Observatory of the Institute for Cosmic Ray Research, the University of Tokyo, Japan."
- construction 2007-04 to 2010-09 (verified) detector construction; https://arxiv.org/abs/1301.2815; quote: "Construction of the detector started in April 2007 and was completed in September 2010."
- commissioning 2010-10 to 2012-06 (verified) commissioning runs; https://arxiv.org/abs/1301.2815; quote: "were conducted from October 2010 to June 2012"
- upgrade 2012-06 to 2013-11 (approximate) refurbishment (copper covers on PMT window seals); https://arxiv.org/abs/1511.04807; quote: "In November 2013, after refurbishing the detector to reduce the radioactive background from the aluminum seal of the"
- active 2013-11-20 to 2019-02-01 (verified) stable data taking (1590.9 live days); https://arxiv.org/abs/2211.06204; quote: "Stable XMASS-I data taking accumulated a total live time of 1590.9 days between November 20, 2013 and February 1, 2019"
- completed 2019-02 to  (approximate) completed (data taking ended); https://arxiv.org/abs/2211.06204; quote: "Stable XMASS-I data taking accumulated a total live time of 1590.9 days between November 20, 2013 and February 1, 2019"
- detector placement: site:kamioka-mozumi-mine-super-kamiokande

### experiment:zeplin-i - ZEPLIN-I (completed)

- facility role: facility:boulby-underground-laboratory 2001 to 2006 (approximate); https://eprints.hud.ac.uk/id/eprint/14213/; quote: "The detector is located in the 2800 mwe depth UK Boulby Mine, and is surrounded by a liquid scintillator Compton veto and passive lead shielding."
- active 2001 to 2006 (approximate) ZEPLIN-I operation (shared with ZEPLIN-II); https://arxiv.org/abs/1112.0080; quote: "After 3 kg single phase ZEPLIN-I [1] and 31 kg double phase ZEPLIN-II [2] running between 2001 and 2006, ZEPLIN-III was the third generation of liquid xenon experiments deployed at Boulby."
- completed 2006 to  (approximate) completed; https://arxiv.org/abs/1112.0080; quote: "After 3 kg single phase ZEPLIN-I [1] and 31 kg double phase ZEPLIN-II [2] running between 2001 and 2006, ZEPLIN-III was the third generation of liquid xenon experiments deployed at Boulby."
- detector placement: site:boulby-mine

### experiment:zeplin-ii - ZEPLIN-II (completed)

- facility role: facility:boulby-underground-laboratory 2005 to 2006 (approximate); https://arxiv.org/abs/astro-ph/0703362; quote: "The ZEPLIN II dark matter detector has been operational at the Boulby Mine underground laboratory since 2005."
- construction 2001-11 to 2005 (approximate) construction; https://arxiv.org/abs/astro-ph/0111098; quote: "We describe the research and development program carried out by the UCLA - Torino group leading to the ZEPLIN II detector under construction for the Boulby Laboratory."
- active 2005 to 2006 (approximate) ZEPLIN-II operation; https://arxiv.org/abs/astro-ph/0703362; quote: "The ZEPLIN II dark matter detector has been operational at the Boulby Mine underground laboratory since 2005."
- completed 2006 to  (approximate) completed; https://arxiv.org/abs/1112.0080; quote: "After 3 kg single phase ZEPLIN-I [1] and 31 kg double phase ZEPLIN-II [2] running between 2001 and 2006, ZEPLIN-III was the third generation of liquid xenon experiments deployed at Boulby."
- detector placement: site:boulby-mine

### experiment:zeplin-iii - ZEPLIN-III (completed)

- facility role: facility:boulby-underground-laboratory 2006 to 2011 (verified); https://arxiv.org/abs/1112.0080; quote: "The ZEPLIN-III experiment searching for Weakly Interacting Massive Particles (WIMPs) operated in the Palmer Laboratory 1070 m underground (2850 m water equivalent) at the Boulby mine (North East of England) between 2006 and 2011."
- commissioning 2006 to 2008-02 (approximate) construction, commissioning and installation at Boulby; https://arxiv.org/abs/1112.0080; quote: "The ZEPLIN-III experiment searching for Weakly Interacting Massive Particles (WIMPs) operated in the Palmer Laboratory 1070 m underground (2850 m water equivalent) at the Boulby mine (North East of England) between 2006 and 2011."
- active 2008-02-27 to 2008-05-20 (verified) first science run (83 days); https://arxiv.org/abs/0812.1150; quote: "An analysis of this http URL of data acquired between February 27th 2008 and May 20th 2008"
- upgrade 2008-05 to 2010-06 (approximate) upgrade: low-background PMTs, anti-coincidence veto, calibration system; https://arxiv.org/abs/1112.0080; quote: "After the first science run (FSR) of 83 days [4, 5, 6], the ZEPLIN-III detector was upgraded;"
- active 2010-06-24 to 2011-05-07 (verified) second science run (319 days); https://arxiv.org/abs/1112.0080; quote: "The second science run (SSR) started on the 24th June 2010 and ended on the 7th May 2011"
- completed 2011-05 to  (approximate) completed (programme concluded); https://arxiv.org/abs/1110.4769; quote: "The ZEPLIN programme reaches thus its conclusion at Boulby, having deployed and exploited successfully three liquid xenon experiments of increasing reach."
- detector placement: site:boulby-mine

## Facilities and sites created

| facility | status | site | coordinate (kind, confidence) | depth | evidence |
|---|---|---|---|---|---|
| `facility:bern-underground-laboratory` | active | `site:bern-underground-laboratory` | 46.9510509, 7.4389317 (campus, approximate, 500 m); https://nominatim.openstreetmap.org/search?q=Sidlerstrasse+5+Bern+Switzerland&format=json; quote ""lat":"46.9510509","lon":"7.4389317"" | 70 m.w.e. | https://arxiv.org/abs/astro-ph/0404311, https://arxiv.org/abs/hep-ex/9911028, https://arxiv.org/abs/physics/0502065 |
| `facility:jaduguda-underground-science-laboratory` | active | `site:jaduguda-underground-science-laboratory` | 22.6556344, 86.349953 (campus, approximate, 5000 m); https://nominatim.openstreetmap.org/search?q=Jaduguda&format=jsonv2&limit=5; quote ""lat":"22.6556344","lon":"86.3499530"" | 555m deep | https://arxiv.org/abs/2501.02833, https://arxiv.org/abs/2510.06921, https://nominatim.openstreetmap.org/search?q=Jaduguda&format=jsonv2&limit=5 |
| `facility:kuo-sheng-reactor-neutrino-laboratory` | active | `site:ksnl-kuo-sheng-nuclear-power-station` | 25.2026362, 121.662658 (campus, approximate, 300 m); https://arxiv.org/abs/1608.00306, https://nominatim.openstreetmap.org/search?q=Kuosheng+Nuclear+Power+Plant&format=json; quote "The Kuo-Sheng Reactor Neutrino Laboratory (KSNL) is located at a distance of 28 m from the core #1 of the Kuo-Sheng Nuclear Power Station operated by the Taiwan Power Company at the northern shore of " | 30 meters of water equivalent | https://arxiv.org/abs/1608.00306, https://newsletter.sinica.edu.tw/reviews/en/news/read_news2eae.html?nid=3269, https://nominatim.openstreetmap.org/search?q=Kuosheng+Nuclear+Power+Plant&format=json |
| `facility:lsbb-rustrel` | active | `site:lsbb-rustrel` | 43.9286655, 5.4870457 (campus, approximate, 2000 m); https://nominatim.openstreetmap.org/search?q=Laboratoire+Souterrain+a+Bas+Bruit+Rustrel&format=json; quote ""lat":"43.9286655","lon":"5.4870457"" | 500 m, 1500 mwe | https://lsbb.eu/, https://lsbb.eu/histoire/, https://arxiv.org/abs/astro-ph/9910192 |
| `facility:oto-cosmo-observatory` | active | `site:oto-cosmo-observatory` | 34.2059829, 135.7363343 (campus, approximate, 6000 m); https://nominatim.openstreetmap.org/search?q=Oto+Gojo+Nara+Japan&format=json&limit=5; quote ""lat":"34.2059829","lon":"135.7363343"" | about 500 m, 1400 m w.e. | https://www.rcnp.osaka-u.ac.jp/~annurep/2001/genkou/sec3/takahisa2.pdf, https://www.rcnp.osaka-u.ac.jp/~takahisa/oto/, https://arxiv.org/abs/astro-ph/0611700 |
| `facility:stanford-underground-facility` | completed | `site:stanford-underground-facility-hepl` | 37.4282257, -122.1726725 (campus, approximate, 500 m); https://stanford.edu/group/hepl/directions.html, https://nominatim.openstreetmap.org/search?q=452+Lomita+Mall,+Stanford,+CA+94305&format=json, https://arxiv.org/abs/astro-ph/0203500; quote "Physics/Astrophysics Building (Varian II) at 452 Lomita Mall" | 17 meters water-equivalent | https://arxiv.org/abs/astro-ph/0203500, https://arxiv.org/abs/astro-ph/9712343, https://arxiv.org/abs/1010.4290 |
| `facility:stawell-underground-physics-laboratory` | active | `site:stawell-underground-physics-laboratory` | -37.0693057, 142.8067113 (campus, approximate, 1500 m); https://nominatim.openstreetmap.org/search?q=Stawell+Gold+Mine+Australia&format=json; quote ""lat":"-37.0693057","lon":"142.8067113"" | 1024 m underground, about 2900 m water equivalent | https://supl.org.au/our-story-so-far/, https://arxiv.org/abs/2211.03016 |
| `facility:vue-des-alpes-underground-laboratory` | active | `site:vue-des-alpes-underground-laboratory` | 47.0715347, 6.8786675 (campus, approximate, 1500 m); https://nominatim.openstreetmap.org/search?q=Tunnel+de+la+Vue-des-Alpes+Neuchatel&format=json; quote "" | 235 m of rock overburden, 620 m.w.e. | https://arxiv.org/abs/2202.06540, https://arxiv.org/abs/1606.03983, https://arxiv.org/abs/1505.07015 |
| `facility:yangyang-underground-laboratory` | active | `site:y2l-yangyang` | 38.019194, 128.499611 (underground_lab, verified, 300 m); https://arxiv.org/abs/1710.05299; quote "The Y2L facility is situated next to the underground generators of the Yangyang pumped-storage hydroelectric power plant under Mount Jumbong, 150 km east of Seoul in Korea (38◦ 010 09.1”N, 128◦ 290 58" | 2000 m water equivalent | https://centers.ibs.re.kr/html/cup/equipment/equipment_0401.html, https://centers.ibs.re.kr/html/cup/, https://arxiv.org/abs/1710.05299 |
| `facility:yemilab` | active | `site:yemilab-handuk` | 37.188639, 128.659406 (campus, approximate, 2000 m); https://arxiv.org/abs/2009.11155, https://arxiv.org/abs/1903.05368; quote "The Handuk iron mine location (latitude: 37.188639 deg, longitude: 128.659406 deg) in Jeongseon-gun, Gangwon province, Korea, where a new underground Yemilab (∼1000 m overburden) is currently being co" | 2,500 m w.e. | https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2024.1323991/pdf, https://link.springer.com/article/10.1007/s43673-024-00132-8, https://centers.ibs.re.kr/html/cup/equipment/equipment_0401.html |

Facility intervals:

- `facility:bern-underground-laboratory` active 1999 to  (uncertain) operating (earliest report read); https://arxiv.org/abs/hep-ex/9911028; quote: "in the Bern Underground Laboratory at 70 m.w.e."
- `facility:jaduguda-underground-science-laboratory` active 2022-07 to  (approximate) in use by InDEx (earliest dated use); https://arxiv.org/abs/2501.02833; quote: "installed at the 555m deep underground laboratory, JUSL during July to Dec 2022"
- `facility:kuo-sheng-reactor-neutrino-laboratory` proposed 1997 to 2000 (verified) design and construction of the laboratory; https://arxiv.org/abs/1608.00306; quote: "Conceptual design discussions were initiated in 1997."
- `facility:kuo-sheng-reactor-neutrino-laboratory` commissioning 2000 to 2001-07 (approximate) laboratory built and commissioned; https://newsletter.sinica.edu.tw/reviews/en/news/read_news2eae.html?nid=3269; quote: "It built and commissioned the “Kuo-Sheng Reactor Neutrino Laboratory” at Nuclear Power Station II on the northern coast of Taiwan in 2000."
- `facility:kuo-sheng-reactor-neutrino-laboratory` active 2001-07 to  (verified) operating (first physics data July 2001; operational in 2026); https://arxiv.org/abs/1608.00306, https://arxiv.org/abs/2606.16864; quote: "First physics data taking started in July 2001."
- `facility:lsbb-rustrel` active 1999-07 to  (uncertain) operating as a civilian underground laboratory (earliest dated use found); https://arxiv.org/abs/astro-ph/0001511; quote: "started in July 1999. A decommissioned nuclear missile control center has been converted into an underground laboratory"
- `facility:oto-cosmo-observatory` active 1997 to  (uncertain) laboratory constructed and in use; https://www.rcnp.osaka-u.ac.jp/~annurep/2001/genkou/sec3/takahisa2.pdf; quote: "has been constructed in the center of the tunnel which location is about 100 km south from Osaka University for ultra rare process nuclear spectroscopy in 1997."
- `facility:stanford-underground-facility` active 1997 to 2002-06 (approximate) hosting the CDMS I and first-tower CDMS II detectors; https://arxiv.org/abs/astro-ph/0203500, https://arxiv.org/abs/1010.4290; quote: "The first stage of the Cryogenic Dark Matter Search (CDMS I) operates at the Stanford Underground Facility, a tunnel 10.6 m beneath the Stanford University campus."
- `facility:stanford-underground-facility` completed 2002-06 to  (approximate) scientific use of the tunnel by CDMS ended; https://arxiv.org/abs/1010.4290; quote: "Four ~224 g germanium and two ~105 g silicon detectors were operated at the Stanford Underground Facility (SUF) between December 2001 and June 2002"
- `facility:stawell-underground-physics-laboratory` proposed 2014 to 2015 (verified) proposal; https://supl.org.au/our-story-so-far/; quote: "First proposed in 2014, the first phase for the development of SUPL was provided through $1.75 million funding in the 2015 Australian federal budget, matched by an equal grant from the Victorian state government."
- `facility:stawell-underground-physics-laboratory` approved 2015 to 2016 (verified) first-phase funding (2015 Australian federal budget); https://supl.org.au/our-story-so-far/; quote: "First proposed in 2014, the first phase for the development of SUPL was provided through $1.75 million funding in the 2015 Australian federal budget, matched by an equal grant from the Victorian state government."
- `facility:stawell-underground-physics-laboratory` construction 2016 to 2022-08 (approximate) construction; https://supl.org.au/our-story-so-far/; quote: "Construction started 2016 and was expected to be complete in 2017, however was delayed by a series of corporate mergers at the gold mine in 2015 and 2016."
- `facility:stawell-underground-physics-laboratory` active 2022-08 to  (verified) operating (laboratory completed and officially unveiled); https://supl.org.au/our-story-so-far/; quote: "The Stawell Underground Physics Laboratory (SUPL) was officially unveiled in August 2022."
- `facility:vue-des-alpes-underground-laboratory` active 2015-05 to  (approximate) laboratory in use (GeMSE installed); https://arxiv.org/abs/1505.07015; quote: "The setup will be installed in the Vue-des-Alpes underground lab near Neuchâtel (Switzerland)"
- `facility:yangyang-underground-laboratory` active 2003 to  (approximate) Y2L-A6 laboratory completed and operated; https://centers.ibs.re.kr/html/cup/equipment/equipment_0401.html; quote: "In 2003, when the Yangyang power plat was constructed, the Dark Matter Research Center (DMRC) of Seoul National University completed construction of the Y2L-A6 lab site having about 100 m2 area and located at ~700 m depth."
- `facility:yangyang-underground-laboratory` upgrade 2013-07 to 2014-12 (approximate) Y2L-A5 (~200 m2) built by IBS CUP; https://centers.ibs.re.kr/html/cup/equipment/equipment_0401.html; quote: "In July 2013, as soon as the Center for Underground Physics(CUP) was started as one of research centers of the IBS, the construction of another small underground experiment facility in the A5 tunnel was started, reaching completion at the end of 2014."
- `facility:yemilab` construction 2017-09 to 2022-09 (verified) Yemilab construction; https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2024.1323991/pdf; quote: "construction of the Yemilab began in September 2017"
- `facility:yemilab` commissioning 2022-09 to 2023-09 (approximate) interior fit-out for experiments; https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2024.1323991/pdf; quote: "With the completion of the fundamental structure of Yemilab, interior enhancements took place in 2023"
- `facility:yemilab` active 2023-09 to  (approximate) operating; experiments relocated from Y2L; https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2024.1323991/pdf; quote: "Starting in September 2023, the relocation of various facilities from Yangyang to Yemilab began."

## Collaborations

- `collaboration:amore` active: active 2009- (verified); formation: 2009
- `collaboration:anais` active: active 2001- (approximate); formation: unpublished
- `collaboration:ardm` completed: active 2004-2020 (approximate); completed 2020- (uncertain); formation: 2004
- `collaboration:bullkid-dm` active: active 2022-09- (approximate); formation: unpublished
- `collaboration:cdex` active: active 2010- (approximate); formation: unpublished
- `collaboration:cogent` active: active 2008- (uncertain); formation: unpublished
- `collaboration:cosine-100` active: active 2016- (approximate); formation: None
- `collaboration:cosinus` active: active 2016- (approximate); formation: unpublished
- `collaboration:cosme` completed: active 1990-2002 (approximate); completed 2002- (uncertain); formation: unpublished
- `collaboration:coupp` completed: active 2005-2013 (approximate); completed 2013- (approximate); formation: unpublished
- `collaboration:cygno` active: active 2019-01- (approximate); formation: unpublished
- `collaboration:dama` active: active 1990- (approximate); formation: 1990
- `collaboration:delight` active: active 2022-09- (approximate); formation: unpublished
- `collaboration:dm-ice` completed: active 2010-12-2017 (approximate); completed 2017- (uncertain); formation: unpublished
- `collaboration:dmtpc` active: active 2007- (uncertain); formation: unpublished
- `collaboration:drift` active: active 2001- (uncertain); formation: unpublished
- `collaboration:gadmc` active: active 2020-01- (uncertain); formation: unpublished
- `collaboration:genius` completed: active 1997-2006 (approximate); completed 2006- (uncertain); formation: unpublished
- `collaboration:hdms` completed: active 1998-03-2006 (approximate); completed 2006- (uncertain); formation: unpublished
- `collaboration:igex` completed: active 1999-2002 (approximate); completed 2002- (uncertain); formation: unpublished
- `collaboration:index-dm` active: active 2022-07- (approximate); formation: unpublished
- `collaboration:kims` completed: active 1999-2019 (approximate); completed 2019- (uncertain); formation: 1999
- `collaboration:lux` completed: active 2013-02-2016-05-02 (approximate); completed 2016-05-02- (approximate); formation: unpublished
- `collaboration:mimac` active: active 2007- (approximate); formation: unpublished
- `collaboration:miniclean` completed: active 2011-2019 (approximate); completed 2019- (approximate); formation: unpublished
- `collaboration:moscab` active: active 2014- (uncertain); formation: unpublished
- `collaboration:newage` active: active 2003- (approximate); formation: unpublished
- `collaboration:newsdm` active: active 2016-04- (approximate); formation: unpublished
- `collaboration:orpheus` completed: active 1999-2005 (approximate); completed 2005- (uncertain); formation: unpublished
- `collaboration:oscura` active: active 2020- (approximate); formation: unpublished
- `collaboration:picasso` completed: active 2002-07-2013-11 (approximate); completed 2013-11- (approximate); formation: unpublished
- `collaboration:pico` active: active 2013- (approximate); formation: 2013
- `collaboration:picolon` active: active 2006- (approximate); formation: unpublished
- `collaboration:rosebud` completed: active 1999-2011 (approximate); completed 2011- (uncertain); formation: unpublished
- `collaboration:sabre` active: active 2016- (approximate); formation: unpublished
- `collaboration:sbc` active: active 2021-02- (approximate); formation: unpublished
- `collaboration:simple` completed: active 1996-10-2015-04 (approximate); completed 2015-04- (uncertain); formation: unpublished
- `collaboration:tesseract` active: active 2021-08- (approximate); formation: unpublished
- `collaboration:texono` active: active 1997- (approximate); formation: 1997
- `collaboration:trex-dm` active: active 2009- (approximate); formation: unpublished
- `collaboration:ukdmc` completed: completed 2003- (uncertain); formation: unpublished
- `collaboration:warp` completed: active 2004-2011 (approximate); completed 2011- (uncertain); formation: unpublished
- `collaboration:xmass` completed: active 2007-04-2019-02 (approximate); completed 2019-02- (approximate); formation: unpublished
- `collaboration:zeplin` completed: active 2005-2011-05 (approximate); completed 2011-05- (approximate); formation: unpublished

## Results written

| result | experiment | type | date (kind) | publication |
|---|---|---|---|---|
| `result:amore-i-ca40-double-electron-capture-2026` | experiment:amore-i | limit | 2026-07-09 (preprint) | 2607.08039 |
| `result:amore-i-improved-limit-2025` | experiment:amore-i | limit | 2024-07-08 (preprint) | 2407.05618 |
| `result:amore-ii-lmo-calorimeters-2025` | experiment:amore-ii | technology_milestone | 2024-07-17 (preprint) | 2407.12227 |
| `result:amore-pilot-first-results-2019` | experiment:amore-pilot | limit | 2019-03-22 (preprint) | 1903.09483 |
| `result:amore-pilot-improved-limit-2024` | experiment:amore-pilot | limit | 2024-01-15 (preprint) | 2401.07476 |
| `result:anais-112-first-results-2019` | experiment:anais-112 | measurement | 2019-03-10 (preprint) | 1903.03973 |
| `result:anais-112-six-year-2025` | experiment:anais-112 | measurement | 2025-02-03 (preprint) | 2502.01542 |
| `result:anais-112-three-year-2021` | experiment:anais-112 | measurement | 2021-03-01 (preprint) | 2103.01175 |
| `result:ardm-backgrounds-and-psd-2017` | experiment:ardm | measurement | 2017-12-02 (preprint) | 1712.01932 |
| `result:ardm-detector-and-run1-2016` | experiment:ardm | technology_milestone | 2016-12-19 (preprint) | 1612.06375 |
| `result:ardm-first-ton-scale-lar-operation-2015` | experiment:ardm | technology_milestone | 2015-05-10 (preprint) | 1505.02443 |
| `result:ardm-scintillation-attenuation-length-2016` | experiment:ardm | measurement | 2016-11-08 (preprint) | 1611.02481 |
| `result:ardm-underground-commissioning-2013` | experiment:ardm | technology_milestone | 2013-09-16 (preprint) | 1309.3992 |
| `result:bullkid-kid-array-concept-2022` | experiment:bullkid-dm | technology_milestone | 2022-09-29 (preprint) | 2209.14806 |
| `result:bullkid-moderate-shield-background-2026` | experiment:bullkid-dm | measurement | 2026-05-04 (preprint) | 2605.02468 |
| `result:bullkid-surface-low-energy-spectrum-2023` | experiment:bullkid-dm | technology_milestone | 2023-08-28 (preprint) | 2308.14399 |
| `result:cdex-1-160-evee-2018` | experiment:cdex-1 | limit | 2017-10-18 (preprint) | 1710.06650 |
| `result:cdex-1-first-results-2013` | experiment:cdex-1 | limit | 2013-06-18 (preprint) | 1306.4135 |
| `result:cdex-1-limits-light-wimps-2014` | experiment:cdex-1 | limit | 2014-04-19 (preprint) | 1404.4946 |
| `result:cdex-10-exotic-dm-2022` | experiment:cdex-10 | limit | 2022-09-02 (preprint) | 2209.00861 |
| `result:cdex-10-first-results-2018` | experiment:cdex-10 | limit | 2018-02-25 (preprint) | 1802.09016 |
| `result:cdex-1b-annual-modulation-2019` | experiment:cdex-1 | limit | 2019-04-29 (preprint) | 1904.12889 |
| `result:cdms-i-exclusion-limits-2000` | experiment:cdms-i | limit | 2000-02-25 (preprint) | astro-ph/0002471 |
| `result:cdms-i-exclusion-limits-2002` | experiment:cdms-i | limit | 2002-03-27 (preprint) | astro-ph/0203500 |
| `result:cdms-i-preliminary-limits-1997` | experiment:cdms-i | limit | 1997-12-30 (preprint) | astro-ph/9712343 |
| `result:cdms-ii-first-run-soudan-2005` | experiment:cdms-ii | limit | 2005-07-08 (preprint) | astro-ph/0507190 |
| `result:cdms-ii-shallow-site-low-threshold-2010` | experiment:cdms-ii | limit | 2010-10-20 (preprint) | 1010.4290 |
| `result:cogent-annual-modulation-2011` | experiment:cogent | anomaly | 2011-06-03 (preprint) | 1106.0650 |
| `result:cogent-detector-and-backgrounds-2013` | experiment:cogent | measurement | 2012-08-28 (preprint) | 1208.5737 |
| `result:cogent-low-mass-excess-2010` | experiment:cogent | anomaly | 2010-02-25 (preprint) | 1002.4703 |
| `result:cogent-maximum-likelihood-2014` | experiment:cogent | measurement | 2014-01-24 (preprint) | 1401.6234 |
| `result:cogent-three-years-modulation-2014` | experiment:cogent | anomaly | 2014-01-14 (preprint) | 1401.3295 |
| `result:cosine-100-anais-112-combined-2025` | experiment:cosine-100 | limit | 2025-03-25 (preprint) | 2503.19559 |
| `result:cosine-100-annual-modulation-1-7-years-2019` | experiment:cosine-100 | measurement | 2019-03-25 (preprint) | 1903.10098 |
| `result:cosine-100-annual-modulation-3-years-2022` | experiment:cosine-100 | measurement | 2021-11-17 (preprint) | 2111.08863 |
| `result:cosine-100-dama-constraints-2021` | experiment:cosine-100 | limit | 2021-04-08 (preprint) | 2104.03537 |
| `result:cosine-100-first-results-2018` | experiment:cosine-100 | limit | 2019-06-05 (preprint) | 1906.01791 |
| `result:cosine-100-full-dataset-annual-modulation-2025` | experiment:cosine-100 | limit | 2024-09-20 (preprint) | 2409.13226 |
| `result:cosine-100-wimp-limits-0-7-kev-2025` | experiment:cosine-100 | limit | 2025-01-23 (preprint) | 2501.13665 |
| `result:cosine-100u-crystal-encapsulation-2026` | experiment:cosine-100u | technology_milestone | 2026-08-12 (preprint) | 2608.11678 |
| `result:cosine-100u-upgrade-2025` | experiment:cosine-100u | technology_milestone | 2024-09-24 (preprint) | 2409.15748 |
| `result:cosinus-deep-underground-prototype-2024` | experiment:cosinus | limit | 2023-07-20 (preprint) | 2307.11139 |
| `result:cosinus-facility-dama-challenge-2025` | experiment:cosinus | technology_milestone | 2025-07-03 (preprint) | 2507.02429 |
| `result:cosinus-first-cryogenic-nai-detector-2017` | experiment:cosinus | technology_milestone | 2017-05-31 (preprint) | 1705.11028 |
| `result:cosinus-remotes-particle-discrimination-2024` | experiment:cosinus | technology_milestone | 2023-07-20 (preprint) | 2307.11066 |
| `result:cosme-solar-axion-coupling-limit-2000` | experiment:cosme | limit | 2000-11-27 (preprint) | hep-ph/0011318 |
| `result:cosme-wimp-exclusion-2001` | experiment:cosme | limit | 2001-01-22 (preprint) | hep-ex/0101037 |
| `result:coupp-2kg-spin-dependent-limits-2008` | experiment:coupp-2kg | limit | 2008-04-17 (preprint) | 0804.2886 |
| `result:coupp-4kg-minos-limits-2010` | experiment:coupp-4kg | limit | 2010-08-20 (preprint) | 1008.3518 |
| `result:coupp-4kg-snolab-limits-2012` | experiment:coupp-4kg | limit | 2012-04-13 (preprint) | 1204.3094 |
| `result:cygno-bayesian-3d-reconstruction-2025` | experiment:cygno | technology_milestone | 2025-06-05 (preprint) | 2506.04973 |
| `result:cygno-first-optical-negative-ion-drift-2026` | experiment:cygno | observation | 2026-03-06 (preprint) | 2603.06837 |
| `result:cygno-light-yield-enhancement-2024` | experiment:cygno | technology_milestone | 2024-06-09 (preprint) | 2406.05713 |
| `result:cygno-lime-underground-campaign-2026` | experiment:cygno | technology_milestone | 2026-03-23 (preprint) | 2603.22595 |
| `result:dama-libra-first-results-2008` | experiment:dama-libra | measurement | 2008-04-17 (preprint) | 0804.2741 |
| `result:dama-libra-new-results-2010` | experiment:dama-libra | evidence | 2010-02-04 (preprint) | 1002.1028 |
| `result:dama-libra-phase1-final-2013` | experiment:dama-libra | evidence | 2013-08-23 (preprint) | 1308.5109 |
| `result:dama-libra-phase2-first-results-2018` | experiment:dama-libra | evidence | 2018-05-26 (preprint) | 1805.10486 |
| `result:dama-libra-phase2-further-results-2021` | experiment:dama-libra | evidence | 2021 (publication) | 10.15407/jnpae2021.04.329 |
| `result:dama-nai-evidence-summary-2003` | experiment:dama-nai | evidence | 2003-11-03 (preprint) | astro-ph/0311046 |
| `result:dama-nai-seven-annual-cycles-2003` | experiment:dama-nai | measurement | 2003-07-23 (preprint) | astro-ph/0307403 |
| `result:delight-mmc-resolution-2023` | experiment:delight | technology_milestone | 2023-10-12 (preprint) | 2310.08512 |
| `result:dm-ice17-annual-modulation-2017` | experiment:dm-ice17 | limit | 2016-02-18 (preprint) | 1602.05939 |
| `result:dm-ice17-first-data-2014` | experiment:dm-ice17 | measurement | 2014-01-20 (preprint) | 1401.4804 |
| `result:dm-ice17-muon-modulation-phosphorescence-2016` | experiment:dm-ice17 | measurement | 2015-09-08 (preprint) | 1509.02486 |
| `result:dmtpc-10l-surface-run-limit-2010` | experiment:dmtpc | limit | 2010-06-15 (preprint) | 1006.2928 |
| `result:dmtpc-charge-signal-background-rejection-2011` | experiment:dmtpc | technology_milestone | 2011-09-15 (preprint) | 1109.3501 |
| `result:dmtpc-directional-sensitivity-2017` | experiment:dmtpc | measurement | 2017-05-17 (preprint) | 1705.05965 |
| `result:dmtpc-head-tail-observation-2007` | experiment:dmtpc | technology_milestone | 2007-08-17 (preprint) | 0708.2370 |
| `result:drift-iid-low-threshold-2017` | experiment:drift | limit | 2016-12-31 (preprint) | 1701.00171 |
| `result:drift-iid-spin-dependent-2010` | experiment:drift | limit | 2010-10-14 (preprint) | 1010.3027 |
| `result:genius-tf-first-naked-ge-detectors-2003` | experiment:genius-tf | technology_milestone | 2003-09-15 (preprint) | hep-ph/0309170 |
| `result:genius-tf-ii-iii-long-term-stability-2006` | experiment:genius-tf | measurement | 2006-10-15 (publication) | 10.1016/j.nima.2006.07.048 |
| `result:genius-tf-radon-daughter-background-2004` | experiment:genius-tf | measurement | 2004-09-11 (publication) | 10.1016/j.nima.2004.05.033 |
| `result:hdms-final-setup-first-results-2002` | experiment:hdms | measurement | 2002-06-17 (preprint) | hep-ph/0206151 |
| `result:hdms-prototype-first-results-2000` | experiment:hdms | limit | 2000-08-22 (preprint) | astro-ph/0008339 |
| `result:hdms-spin-dependent-wimp-neutron-limit-2005` | experiment:hdms | limit | 2006-10 (publication) | 10.1088/0031-8949/2006/T127/019 |
| `result:herald-first-demonstration-2023` | experiment:herald, experiment:tesseract | technology_milestone | 2023-07-21 (preprint) | 2307.11877 |
| `result:herald-scintillation-yield-2021` | experiment:herald, experiment:tesseract | measurement | 2021-08-04 (preprint) | 2108.02176 |
| `result:igex-dm-improved-constraints-2001` | experiment:igex-dm | limit | 2001-10-25 (preprint) | hep-ex/0110061 |
| `result:igex-dm-new-constraints-2000` | experiment:igex-dm | limit | 2000-02-21 (preprint) | hep-ex/0002053 |
| `result:index-run1-2025` | experiment:index-dm | limit | 2025-01-06 (preprint) | 2501.02833 |
| `result:index-run2-2025` | experiment:index-dm | limit | 2025-10-08 (preprint) | 2510.06921 |
| `result:kims-csi-first-limit-2005` | experiment:kims | limit | 2005-09-05 (preprint) | astro-ph/0509080 |
| `result:kims-csi-limits-2007` | experiment:kims | limit | 2007-04-03 (preprint) | 0704.0423 |
| `result:kims-csi-low-mass-2014` | experiment:kims | limit | 2014-04-14 (preprint) | 1404.3443 |
| `result:kims-csi-solar-axions-2016` | experiment:kims | limit | 2016-04-06 (preprint) | 1604.01825 |
| `result:kims-csi-spin-dependent-limits-2012` | experiment:kims | limit | 2012-04-12 (preprint) | 1204.2646 |
| `result:kims-nai-limits-2018` | experiment:kims-nai | limit | 2018-06-18 (preprint) | 1806.06499 |
| `result:mimac-electron-recoil-discrimination-2016` | experiment:mimac | technology_milestone | 2016-02-04 (preprint) | 1602.01738 |
| `result:mimac-first-directional-limits-2026` | experiment:mimac | limit | 2026-07-26 (preprint) | 2607.23527 |
| `result:mimac-kev-proton-carbon-directionality-2023` | experiment:mimac | technology_milestone | 2023-12-20 (preprint) | 2312.12842 |
| `result:mimac-radon-progeny-tracks-2015` | experiment:mimac | first_detection | 2015-04-22 (preprint) | 1504.05865 |
| `result:miniclean-gaseous-argon-triplet-lifetime-2019` | experiment:miniclean | measurement | 2019-03-15 (preprint) | 1903.06706 |
| `result:moscab-fast-neutron-detection-2021` | experiment:moscab | technology_milestone | 2021-06-25 (preprint) | 2106.13654 |
| `result:moscab-geyser-chamber-tests-2017` | experiment:moscab | technology_milestone | 2017-07-31 (preprint) | 1708.00101 |
| `result:naiad-final-limits-2005` | experiment:naiad | limit | 2005-04-17 (preprint) | hep-ex/0504031 |
| `result:naiad-first-limits-2003` | experiment:naiad | limit | 2003-01-31 (preprint) | hep-ex/0301039 |
| `result:newage-0-3a-first-underground-2010` | experiment:newage | limit | 2010-02-09 (preprint) | 1002.1794 |
| `result:newage-0-3b-double-prime-2021` | experiment:newage | limit | 2021-01-25 (preprint) | 2101.09921 |
| `result:newage-0-3b-prime-3d-vector-2020` | experiment:newage | limit | 2020-05-11 (preprint) | 2005.05157 |
| `result:newage-3d-vector-2023` | experiment:newage | limit | 2023-01-12 (preprint) | 2301.04779 |
| `result:newage-surface-laboratory-limit-2007` | experiment:newage | limit | 2007-08-20 (preprint) | 0708.2579 |
| `result:newsdm-environmental-neutron-gran-sasso-2023` | experiment:newsdm | measurement | 2022-08-29 (preprint) | 2208.13366 |
| `result:newsdm-first-directional-emulsion-limit-2023` | experiment:newsdm | limit | 2023-10-10 (preprint) | 2310.06265 |
| `result:orpheus-first-results-2004` | experiment:orpheus | measurement | 2004-04-15 (preprint) | astro-ph/0404311 |
| `result:orpheus-ssg-nuclear-recoil-response-1994` | experiment:orpheus | technology_milestone | 1994-11-17 (preprint) | cond-mat/9411072 |
| `result:oscura-single-electron-traps-2024` | experiment:oscura | measurement | 2024-06-26 (preprint) | 2406.18502 |
| `result:oscura-skipper-ccd-sensors-2023` | experiment:oscura | technology_milestone | 2023-04-10 (preprint) | 2304.04401 |
| `result:pandax-i-first-results-2014` | experiment:pandax-i | limit | 2014-08-21 (preprint) | 1408.5114 |
| `result:pandax-i-low-mass-full-exposure-2015` | experiment:pandax-i | limit | 2015-05-04 (preprint) | 1505.00771 |
| `result:pandax-ii-54-ton-day-2017` | experiment:pandax-ii | limit | 2017-08-23 (preprint) | 1708.06917 |
| `result:pandax-ii-98-7-day-2016` | experiment:pandax-ii | limit | 2016-07-25 (preprint) | 1607.07400 |
| `result:pandax-ii-commissioning-run-2016` | experiment:pandax-ii | limit | 2016-02-21 (preprint) | 1602.06563 |
| `result:pandax-ii-full-exposure-2020` | experiment:pandax-ii | limit | 2020-07-30 (preprint) | 2007.15469 |
| `result:pandax-ii-spin-dependent-2016` | experiment:pandax-ii | limit | 2016-11-20 (preprint) | 1611.06553 |
| `result:picasso-alpha-neutron-discrimination-2008` | experiment:picasso | technology_milestone | 2008-07-10 (preprint) | 0807.1536 |
| `result:picasso-final-results-2016` | experiment:picasso | limit | 2016-11-04 (preprint) | 1611.01499 |
| `result:picasso-low-mass-wimp-limits-2012` | experiment:picasso | limit | 2012-02-06 (preprint) | 1202.1240 |
| `result:picasso-spin-dependent-limits-2005` | experiment:picasso | limit | 2005-02-15 (preprint) | hep-ex/0502028 |
| `result:picasso-spin-dependent-limits-2009` | experiment:picasso | limit | 2009-07-02 (preprint) | 0907.0307 |
| `result:pico-2l-first-results-2015` | experiment:pico-2l | limit | 2015-02-27 (preprint) | 1503.00008 |
| `result:pico-2l-run2-2016` | experiment:pico-2l | limit | 2016-01-14 (preprint) | 1601.03729 |
| `result:pico-60-c3f8-2017` | experiment:pico-60 | limit | 2017-02-24 (preprint) | 1702.07666 |
| `result:pico-60-c3f8-complete-exposure-2019` | experiment:pico-60 | limit | 2019-02-11 (preprint) | 1902.04031 |
| `result:pico-60-cf3i-2015` | experiment:pico-60 | limit | 2015-10-27 (preprint) | 1510.07754 |
| `result:pico-60-fermionic-absorption-2025` | experiment:pico-60 | limit | 2025-04-17 (preprint) | 2504.13089 |
| `result:pico-60-inelastic-dark-matter-2023` | experiment:pico-60 | limit | 2023-01-21 (preprint) | 2301.08993 |
| `result:pico-60-photon-mediated-2022` | experiment:pico-60 | limit | 2022-04-21 (preprint) | 2204.10340 |
| `result:pico-buffer-free-prototype-2019` | experiment:pico-40l, experiment:pico-500 | technology_milestone | 2019-05-17 (preprint) | 1905.07367 |
| `result:pico-electron-recoil-nucleation-2019` | experiment:pico-2l, experiment:pico-60, experiment:pico-40l | measurement | 2019-05-29 (preprint) | 1905.12522 |
| `result:picolon-annual-modulation-test-2025` | experiment:picolon | measurement | 2025-09-26 (preprint) | 2509.22021 |
| `result:picolon-radiopure-nai-development-2021` | experiment:picolon | technology_milestone | 2021-01-04 (preprint) | 2101.00759 |
| `result:picolon-radiopurity-ingot-94-2023` | experiment:picolon | measurement | 2023-09-25 (preprint) | 2309.13941 |
| `result:rosebud-canfranc-2001-report-2001` | experiment:rosebud | measurement | 2001-12-12 (preprint) | astro-ph/0112272 |
| `result:rosebud-first-results-2000` | experiment:rosebud | measurement | 2000-04-20 (preprint) | astro-ph/0004292 |
| `result:sabre-nai-33-direct-counting-2021` | experiment:sabre-north | measurement | 2020-12-04 (preprint) | 2012.02610 |
| `result:sabre-north-zone-refining-2026` | experiment:sabre-north | technology_milestone | 2026-01-22 (preprint) | 2601.15998 |
| `result:sabre-pop-dry-passive-shielding-2022` | experiment:sabre-north | measurement | 2022-05-27 (preprint) | 2205.13876 |
| `result:sabre-pop-high-sensitivity-characterization-2021` | experiment:sabre-north | measurement | 2021-05-19 (preprint) | 2105.09225 |
| `result:sabre-south-muon-flux-supl-2026` | experiment:sabre-south | measurement | 2026-03-12 (preprint) | 2603.11981 |
| `result:sabre-south-simulation-background-2023` | experiment:sabre-south | technology_milestone | 2022-05-27 (preprint) | 2205.13849 |
| `result:sabre-south-tdr-executive-summary-2025` | experiment:sabre-south | technology_milestone | 2024-11-21 (preprint) | 2411.13889 |
| `result:sbc-xenon-bubble-chamber-demonstration-2017` | experiment:sbc | technology_milestone | 2017-02-28 (preprint) | 1702.08861 |
| `result:sbc-xenon-bubble-chamber-low-threshold-2024` | experiment:sbc | technology_milestone | 2024-10-07 (preprint) | 2410.07241 |
| `result:simple-first-limits-2000` | experiment:simple | limit | 2000-01-28 (preprint) | astro-ph/0001511 |
| `result:simple-phase-ii-final-2012` | experiment:simple | limit | 2012-04-09 (preprint) | 1106.3014 |
| `result:simple-phase-ii-first-results-2010` | experiment:simple | limit | 2010-10-20 (preprint) | 1003.2987 |
| `result:simple-phase-ii-reanalysis-2014` | experiment:simple | limit | 2014-04-16 (preprint) | 1404.4309 |
| `result:simple-results-2005` | experiment:simple | limit | 2005-05-17 (preprint) | hep-ex/0505053 |
| `result:tesseract-bulk-silicon-phonon-bursts-2025` | experiment:tesseract, experiment:spice | measurement | 2025-05-22 (preprint) | 2505.16092 |
| `result:tesseract-first-limits-2025` | experiment:tesseract, experiment:spice | limit | 2025-03-05 (preprint) | 2503.03683 |
| `result:tesseract-stress-induced-phonon-bursts-2022` | experiment:tesseract, experiment:spice | measurement | 2022-08-04 (preprint) | 2208.02790 |
| `result:texono-bosonic-dm-npcge-2019` | experiment:texono | limit | 2018-11-28 (preprint) | 1811.11415 |
| `result:texono-pcge-wimp-limits-2013` | experiment:texono | limit | 2013-03-05 (preprint) | 1303.0925 |
| `result:texono-ulege-220ev-wimp-limits-2008` | experiment:texono | limit | 2007-12-11 (preprint) | 0712.1645 |
| `result:tokyo-lif-bolometer-kamioka-2002` | experiment:tokyo-dark-matter-search | limit | 2002-04-24 (preprint) | astro-ph/0204411 |
| `result:tokyo-naf-bolometer-kamioka-2003` | experiment:tokyo-dark-matter-search | limit | 2003-06-18 (preprint) | astro-ph/0306365 |
| `result:trex-dm-achievements-2023` | experiment:trex-dm | technology_milestone | 2023-12-19 (preprint) | 2312.12622 |
| `result:trex-dm-argon37-calibration-2025` | experiment:trex-dm | technology_milestone | 2025-10-07 (preprint) | 2510.05877 |
| `result:trex-dm-background-assessment-2018` | experiment:trex-dm | technology_milestone | 2018-12-11 (preprint) | 1812.04519 |
| `result:warp-argon-39-specific-activity-2007` | experiment:warp | measurement | 2006-03-06 (preprint) | astro-ph/0603131 |
| `result:warp-first-physics-results-2007` | experiment:warp | limit | 2007-01-10 (preprint) | astro-ph/0701286 |
| `result:xenon10-first-wimp-search-2007` | experiment:xenon10 | limit | 2007-05-31 (preprint) | 0706.0039 |
| `result:xenon10-light-dark-matter-2011` | experiment:xenon10 | limit | 2011-04-15 (preprint) | 1104.3088 |
| `result:xenon10-spin-dependent-2008` | experiment:xenon10 | limit | 2008-05-19 (preprint) | 0805.2939 |
| `result:xenon100-100-live-days-2011` | experiment:xenon100 | limit | 2011-04-13 (preprint) | 1104.2549 |
| `result:xenon100-225-live-days-2012` | experiment:xenon100 | limit | 2012-07-25 (preprint) | 1207.5988 |
| `result:xenon100-477-live-days-2016` | experiment:xenon100 | limit | 2016-09-20 (preprint) | 1609.06154 |
| `result:xenon100-axion-2014` | experiment:xenon100 | limit | 2014-04-05 (preprint) | 1404.1455 |
| `result:xenon100-first-results-2010` | experiment:xenon100 | limit | 2010-05-03 (preprint) | 1005.0380 |
| `result:xenon100-spin-dependent-2013` | experiment:xenon100 | limit | 2013-01-28 (preprint) | 1301.6620 |
| `result:xmass-annual-modulation-2-7-years-2018` | experiment:xmass | limit | 2018-01-30 (preprint) | 1801.10096 |
| `result:xmass-annual-modulation-2015` | experiment:xmass | limit | 2015-11-16 (preprint) | 1511.04807 |
| `result:xmass-direct-search-705-days-2018` | experiment:xmass | limit | 2018-04-06 (preprint) | 1804.02180 |
| `result:xmass-full-dataset-2022` | experiment:xmass | limit | 2022-11-11 (preprint) | 2211.06204 |
| `result:xmass-sub-gev-annual-modulation-2018` | experiment:xmass | limit | 2018-08-19 (preprint) | 1808.06177 |
| `result:zeplin-i-first-limits-2005` | experiment:zeplin-i | limit | 2005-06 (publication) | 10.1016/j.astropartphys.2005.02.004 |
| `result:zeplin-ii-first-limits-2007` | experiment:zeplin-ii | limit | 2007-01-30 (preprint) | astro-ph/0701858 |
| `result:zeplin-ii-inelastic-dark-matter-2009` | experiment:zeplin-ii | limit | 2009-06-22 (preprint) | 0906.4119 |
| `result:zeplin-ii-spin-dependent-2007` | experiment:zeplin-ii | limit | 2007-08-14 (preprint) | 0708.1883 |
| `result:zeplin-iii-first-science-run-2008` | experiment:zeplin-iii | limit | 2008-12-05 (preprint) | 0812.1150 |
| `result:zeplin-iii-inelastic-dark-matter-2010` | experiment:zeplin-iii | limit | 2010-03-29 (preprint) | 1003.5626 |
| `result:zeplin-iii-second-science-run-2011` | experiment:zeplin-iii | limit | 2011-10-21 (preprint) | 1110.4769 |
| `result:zeplin-iii-spin-dependent-2009` | experiment:zeplin-iii | limit | 2009-01-27 (preprint) | 0901.4348 |

## Conflicts, unresolved fields and exclusions: lead

### Excluded or deferred candidates (reason)

- **XLZD and DARWIN**: not recorded. The XLZD Design Book (arXiv:2410.17137, Eur. Phys. J. C 85 (2025) 1192) and the DARWIN/XLZD paper (arXiv:2404.19524) describe a 60-80 t liquid-xenon observatory but do not name a host site. The design book says Boulby, LNGS, Kamioka, SURF and SNOLAB have expressed interest and that the collaboration is working towards an inclusive down-selection; STFC/XLZD pages read on 2026-10-26 still show no selected site. The inclusion bar needs a design report that names the host site, and a placement needs a located site, so the bar is not met. DARWIN's 2016 design study (arXiv:1606.07001) only uses the LNGS depth for estimates. **Re-add when the siting decision is published** (experiment:xlzd, proposed, DARWIN as predecessor; the build scripts in this stream show the pattern of `experiment:pandax-xt`).
- **PandaX-III** (136Xe 0vbb high-pressure gas TPC at CJPL): double-beta-decay experiment, left to the neutrino/0vbb stream; not created here.
- **COSINE-200**: excluded by the Korean-labs work: described as a possible next phase in COSINE-100 papers, but no design or proposal document naming it with a host site was found (note on `experiment:cosine-100u`).
- **CYGNUS** (multi-site directional network), **D3**, **NITEC**: excluded in the directional stream log below (no fixed host site, no approval or results, or detector R&D only).
- **DEAP-1, DarkSide-10, ARGOlite, DArTinArDM** (argon): technology or assay results only, no dark-matter physics result; **DEAP-1** and **DarkSide-10** can be added if a physics result is accepted from their pulse-shape papers. See the argon log below.
- **NEON** (reactor CEvNS in Korea): belongs to the cevns stream.
- **EURECA, MALBEK, GEDEON, the full GENIUS, IGEX (0vbb) and Heidelberg-Moscow (0vbb)**: see the germanium/cryogenic log below.
- **QUEST-DMC, QROCODILE, ALETHEIA, DAREDEVIL, CRYOSEL, KIPM at NEXUS**: low-mass log below (published or prototype, no source names a host site).

### Notes on records edited or reconciled by the lead

- `experiment:cdms-ii` already records its `active` interval from 2005, but the CDMS collaboration's first Soudan result (arXiv:astro-ph/0405033, May 2004) predates it: A12 forbids a result dated before the active start, so only the 2005 first-run result (arXiv:astro-ph/0507190) was added. The existing intervals look late against the papers (first Soudan data are reported for 2003); not edited because the record belongs to another stream.
- `experiment:lux` gained `collaboration:lux` and `detector:lux` (built from the quotes already on the LUX record); its two results now name them.
- Cross-links added with verbatim quotes: XENON1T predecessor XENON100; CDEX-1 predecessor TEXONO (the 2016 TEXONO overview) and complementary to CoGeNT; PICASSO same_program PICO-60 (merger statement on the PICO site); `complementary` rows on DAMA/LIBRA to KIMS, XMASS, PICO-60, ZEPLIN-III, SABRE South and XENON10, and from ANAIS-112, COSINE-100 and CDEX-1 to DAMA/LIBRA, each quoted from the other experiment's own abstract.
- No lineage row was added where no source states the relation: ZEPLIN-III to LZ (the name 'LUX-ZEPLIN' only), PandaX-II to PandaX-4T, CDMS I to CDMS II.

### Conflicts recorded by the lead (claim / source A / source B / chosen / why)

| claim | source A | source B | chosen | why |
|---|---|---|---|---|
| ZEPLIN-I discrimination power | Alner et al., Astropart. Phys. 23 (2005) 444: sensitivity minimum 1.1e-6 pb | Phys. Lett. B 637 (2006) 156 (arXiv:astro-ph/0512120): sensitivity nearer 1e-3 pb; reply arXiv:astro-ph/0701859 | the collaboration's published limit, with the dispute in the result and experiment notes | the Atlas states what the collaboration published and records that it was disputed; no side adjudicated |
| ZEPLIN-I and ZEPLIN-II run years | arXiv:1112.0080: 'ZEPLIN-I and ZEPLIN-II running between 2001 and 2006' (one shared period) | arXiv:astro-ph/0703362: ZEPLIN-II 'operational ... since 2005' | shared period on ZEPLIN-I (approximate), 2005-2006 on ZEPLIN-II | no source gives ZEPLIN-I's own end |
| XENON100 run period | XENON history page: 2008-2016 (years only) | arXiv:1609.06154: 477 live days Jan 2010 - Jan 2014; arXiv:1005.0380: first data Oct-Nov 2009 | lifecycle interval from the history page (approximate) plus exact run intervals | both are sourced; they describe different things (existence of the detector vs data taking) |
| Boulby depth for the ZEPLIN experiments | 2850 m.w.e. (arXiv:1112.0080) | 2805 m.w.e. (arXiv:astro-ph/0701858); 2800 mwe (ZEPLIN-I abstract) | each experiment cites its own paper | different papers, same mine |
| XMASS end of stable data taking | collaboration paper (arXiv:2211.06204): 1 Feb 2019 | other (non-cited) sources give 20 Feb 2019 for the shutdown | 1 Feb 2019, month precision | primary source preferred; no shutdown date read in a primary source |
| PandaX-II hall | PandaX-II papers: 'China JinPing Underground Laboratory' only | arXiv:2107.13438 calls CJPL-II 'newly expanded' | site:cjpl-i, confidence approximate | the hall is not named by the PandaX-II papers |

### Unresolved (lead clusters: XENON, XMASS, Boulby, PandaX, CDEX, LUX, InDEx, cross-links)

- INSPIRE experiment ids for all new experiments (INSPIRE was not contacted); `external.inspire_experiment` is null with a note.
- XENON10/XENON100: both sat in the LNGS interferometer tunnel (no Atlas site record); `site:lngs-hall-b` referenced with a note.
- ZEPLIN-I/II individual start and end months; ZEPLIN-II first-run dates; DRIFT current status (latest paper read: 2017).
- PandaX-I/II construction start dates; CDEX-10 status after 2018; collaboration formation dates and rosters for XMASS, UKDMC, ZEPLIN, DRIFT, CDEX, LUX, InDEx.
- LUX: collaboration formation date and roster; the LUX website URL was not re-fetched (as recorded on `experiment:lux`).
- InDEx: operator and rock overburden (m.w.e.) of the Jaduguda Underground Science Laboratory; run-2 dates; whether data taking continues; the coordinate is the town of Jaduguda (campus-grade, approximate).

### For the integrator

- **Bundle size**: with this branch `atlas.json` is about 1.39 MB (limit: the build fails above 1.5 MB, warns above 400 KB). Other coverage streams will add more: the budget check or the bundle split needs attention at merge.
- `facility:snolab` starts 2011-03, but PICASSO ran at SNO from 2002 and COUPP-4kg at SNOLAB from 2010: the validator warns `experiment-before-facility`; the facility's interval belongs to another stream.
- New campus-grade (approximate) site points raise A23 warnings by design: Bern, LSBB Rustrel, Stawell, Jaduguda, Vue-des-Alpes and others; each note says what source is missing.
- `facility:vue-des-alpes-underground-laboratory` was created by the low-mass work for DELight (its host is in Switzerland, not Modane); `facility:oto-cosmo-observatory`, `facility:kuo-sheng-reactor-neutrino-laboratory`, `facility:stanford-underground-facility`, `facility:bern-underground-laboratory`, `facility:lsbb-rustrel`, `facility:jaduguda-underground-science-laboratory`, `facility:yangyang-underground-laboratory`, `facility:yemilab` and `facility:stawell-underground-physics-laboratory` are the other new laboratories.
- Pre-existing oddity not touched: `experiment:damic` and `experiment:damic-m` each name the other as `predecessor`.
- TEXONO's neutrino-physics programme at Kuo-Sheng is not recorded here (the neutrino stream may extend `experiment:texono`).
- Collaboration-level mergers (PICASSO + COUPP into PICO; DM-Ice + KIMS-NaI into COSINE-100) are recorded only as experiment lineage rows.


## Stream log: argon

### Conflicts (claim / source A / source B / chosen / why)
1. End of ArDM dark matter data taking. UCLA DM 2020 abstract (https://indico.global/event/645/contributions/16365/, read raw, no Anubis wall on the contribution page): 'has recently finished data taking in dual-phase mode' (conference of 25-28 March 2020, cancelled) / an encyclopaedia entry found during search (not cited) says 2019 / chosen: `completed` from 2020 with confidence `uncertain`, described as an upper bound; no primary source gives the date.
2. ArDM Run I wording. arXiv:1505.02443 (May 2015): 'first period of physics data taking in the single-phase operation mode' / arXiv:1612.06375 and 1712.01932: 'single-phase commissioning run in 2015' / chosen: lifecycle `active` from 2015-02 (the collaboration's own report), run interval 'ArDM Run I' to 2015; note records both wordings.
3. ArDM rock overburden. arXiv:1612.06375 Sec. 2.1: 'about 2500 m water-equivalent' / DArTinArDM LIDINE 2022 talk: 2400 m.w.e. for Hall A / chosen: 2500 (collaboration paper), approximate; the talk was not used.
4. MiniCLEAN start. SNOLAB page: 'began operating at SNOLAB in 2013' / arXiv:1403.4842 (March 2014): 'Assembly ... is underway', cooling planned for summer 2014 / arXiv:1903.06706: cold-gas run Feb-Apr 2017, no liquid run documented / chosen: construction from 2013 (approximate; 'operating' read as presence/assembly), commissioning from 2014-03, completed 2019 (SNOLAB 'Completed'; 'began decommissioning in 2019'). The lead's brief expected `commissioning`; SNOLAB's own status page says Completed, so `completed` is used.
5. SNOLAB MiniCLEAN page counts: tagline 'researchers from 7 US institutions' vs participation box '5 institutions, 16 people' / no count recorded.
6. WArP programme start. 2013 review (arXiv:1207.2292): 'started their program at LNGS in the late 1990s' and also 'was proposed in 2004' / INFN approval and funding 'starting from 2004' (arXiv:astro-ph/0411491) / chosen: approved 2004; collaboration interval starts 2004 (approximate, lower bound for the formal programme).
7. WArP 100-litre detector: review says 'commissioned at LNGS by 2009' / A. Zani 2014 says 'assembled in 2008 ... never actually performed a physics run, a technical run was taken in 2011' / chosen: construction 2005-2008, commissioning and technical runs 2008-2011, completed 2011 (uncertain). No source states an end of the programme.
8. DarkSide-50 end (not my record): existing record 2013-2020 (LNGS page) vs SNOLAB 2025 community report 'a 50 kg double-phase TPC that operated at LNGS ... until early 2018' (arXiv:2507.11368, Sec. 5.4). Not changed; flagged for the integrator.

### Unresolved fields
- ArDM: start of construction at CERN (null); start of the dual-phase run (null); exact end of data taking and decommissioning date; any dual-phase physics result; official website; collaboration roster/member count; building on the CERN Meyrin site used for the surface test.
- MiniCLEAN: approval date; exact start of construction; any liquid-argon run (a 2018 natural-argon fill mentioned in the brief was not found in any fetchable source); decommissioning date; physics result (none published); website; roster.
- WArP: hall of the 100-litre detector; dates of the filling and technical runs (collaboration news '07/05/09' is dd/mm or mm/dd, read as 2009 only); end of programme; roster; WArP -> DarkSide lineage (no source states it; arXiv:1109.2979 only cites WARP for the technique and the DarkSide-50 papers describe DarkSide-10 as the design basis).
- ARGO: approval/funding; schedule beyond the report's 'late 2030s' construction goal; single- vs dual-phase design; website.
- DarkSide-LowMass: approval/funding/schedule; site is a 'primary plan' only.
- GADMC: founding date (only an upper bound, January 2020), roster; website.
- Coordinates: none created (all detectors use existing site records: lsc-canfranc, snolab-underground-lab, lngs-hall-b, cern-meyrin; all campus-grade as already recorded).

### Excluded candidates (reason)
- DEAP-1 (7 kg prototype, data taking 2007-2011 per arXiv:1406.0462; operated underground at SNOLAB per arXiv:1211.0909): its papers (arXiv:0904.2930 'Measurement of the scintillation time spectra and pulse-shape discrimination ... with DEAP-1', arXiv:1211.0909 'Radon backgrounds in the DEAP-1 ...', arXiv:1406.0462 'In order to study the background of a LAr dark matter detector and characterize the PSD, the DEAP collaboration built a small scale prototype, DEAP-1') are technology and background studies in support of DEAP-3600; no WIMP-search result. Not an Atlas experiment; DEAP-1 -> DEAP-3600 lineage therefore cannot be recorded.
- DarkSide-10 (10 kg prototype; Princeton runs 2010-2011, then LNGS Hall C in 2011): arXiv:1204.6218 is a light-yield measurement and arXiv:1109.2979 a programme overview; no physics result.
- ARGOlite (1 t prototype of underground argon in the DEAP-3600 water tank at SNOLAB, 'early 2030s' / 2028-2031): no results, no approval (funding 'requested ... under the 2025 CFI IF application'), no design report; only plans in arXiv:2507.11368 Sec. 5.5 and a CAP 2025 abstract. Described in ARGO's notes.
- DArTinArDM (LSC Exp-13-2019; arXiv:2001.08077, 2001.08106, 2609.39400): a 39Ar assay chamber inside the ArDM LAr bath that supports DarkSide-20k; the 2026 paper reports a 39Ar specific activity measurement but it is not a dark matter search. Recorded only in ArDM's notes; a candidate for the detector R&D / low-background stream.
- GAP-TPC (arXiv:1601.00819): a concept paper; names no host site or approval.
- CDEX-10 liquid-argon prototype (arXiv:1512.04258): a Compton-veto prototype for the germanium CDEX programme, not an argon dark matter search.
- ALETHEIA (arXiv:2511.08954 etc.): liquid helium, not argon (other stream).
- CLEAN (full-scale, 40-120 t single phase; arXiv:1110.1005): conceptual successor of MiniCLEAN with no site or approval; mentioned only in the MiniCLEAN notes.

### For the integrator
- Lineage edits in existing records (only `lineage`): darkside-50 += same_program -> deap-3600, miniclean; deap-3600 += same_program -> miniclean; darkside-20k += complementary -> darkside-lowmass. All rest on the SNOLAB report quote 'The Global Argon Dark Matter Collaboration (GADMC) is the result of joint international efforts by DEAP-3600, miniCLEAN, DarkSide-50, and ARDM' (arXiv:2507.11368, Sec. 5.4) / the DarkSide-LowMass quote in Sec. 5.4. ArDM (+3 rows), ARGO (+2 rows: same_program with darkside-20k and deap-3600) and DarkSide-LowMass (predecessor darkside-50) carry their own rows. Under A1 same_program/complementary live on the lexicographically smaller id.
- collaboration:darkside carries the aliases 'Global Argon Dark Matter Collaboration' and 'GADMC' (not mine); collaboration:gadmc is a separate record named 'Global Argon Dark Matter Collaboration (GADMC)' so that the A20 alias rule passes. Consider removing the two aliases from collaboration:darkside and adding "GADMC" as an alias of collaboration:gadmc.
- experiment:darkside-50 end date (2018 vs 2020) - see conflict 8. experiment:deap-3600 has an interval 'upgrade 2026-09 -> open, phase detector upgrade (third fill)' that looks mis-dated next to 'third fill ... data taking is ongoing' (arXiv:2603.27372) - not touched.
- MiniCLEAN detector technology_class is `other` (single-phase scintillation-only, no TPC); a `noble_liquid_scintillator` class would suit it and DEAP-3600, which is filed as `noble_liquid_tpc`/`argon_tpc` with an explicit note.
- Coverage rows: `.dm2/frag/argon.coverage.json` (5 rows: ArDM B, WArP B, MiniCLEAN C, ARGO C, DarkSide-LowMass C).
- Possibly missing from the whole wave (not mine): CCM (Coherent CAPTAIN-Mills, a liquid argon detector at LANL looking for accelerator-produced light dark matter) and SBC (scintillating bubble chamber with argon/xenon at SNOLAB).
- During my work the shared worktree briefly had a validator error from another agent's file (`experiments/genius-tf.json`, A20 duplicate alias); at the last run the whole atlas had 0 errors.


## Stream log: directional

### Conflicts

* **NEWAGE start**: claim A: 'We started a new project, NEw generation WIMP-search with Advanced Gaseous tracking device Experiment (NEWAGE) in 2003' (arXiv:1109.3099). Claim B: 'NEWAGE started direction-sensitive direct WIMP searches in an underground laboratory in 2007' (arXiv:2301.04779); first underground dark matter run 2008-09-11 to 2008-12-04 in Laboratory B (arXiv:1002.1794). Chosen: three dated phases: construction 2003-2007, active from 2007, facility role/placement at Kamioka from 2008-09. Why: the claims describe different things (project start, start of underground searches, first underground dark matter run in a named hall).
* **NEWAGE Laboratory B coordinates**: claim A: '(36.25’N, 137.18’E)' in arXiv:2301.04779 and arXiv:2101.09921 (the PDF text layer drops the degree sign). Claim B: '(36◦ 25’N, 137◦ 18’E)' in arXiv:1002.1794 and arXiv:2005.05157. Chosen: no coordinate recorded: the facility's primary site (Mozumi mine) is referenced with a placement note. Why: the two readings agree once degree signs are restored (36 deg 25 min N, 137 deg 18 min E); Laboratory B is not the Super-Kamiokande cavern and has no site record.
* **CYGNO demonstrator size**: claim A: '1 m3 volume' demonstrator (CDR, 2019; arXiv:1901.04190; arXiv:2001.02453). Claim B: '0.4 m3' CYGNO-04 'forced the rescaling of the PHASE 1 active volume and design to a 0.4 m3' (TDR, 2023; arXiv:2603.22595). Chosen: 0.4 m^3 for CYGNO-04 (the current design); 50 L for LIME. Why: the TDR is the later design report and gives the reason (time and Hall F space).
* **CYGNO-04 status**: claim A: 'to be completed in 2026' (arXiv:2603.22595, March 2026). Claim B: 'is constructing the detector demonstrator, CYGNO-04, in Hall F' (arXiv:2510.23229 v2, April 2026). Chosen: status `construction` (open). Why: no source read says it was completed; 'to be completed in 2026' is a plan, not a completion.
* **MIMAC active volume**: claim A: '6 liter active volume' (abstract of arXiv:2607.23527). Claim B: '10.8 × 10.8 × 25 cm3' per chamber, two chambers (same paper), about 5.8 L in total. Chosen: 6 L, as the abstract states. Why: consistent within rounding; the abstract's figure is the one quoted.
* **NEWSdm location**: claim A: 'The NEWSdm experiment, located in the Gran Sasso underground laboratory in Italy' (ICHEP 2022 proceedings). Claim B: the 2023 directional limit was taken 'at the ground floor of the Science Building B in Nagoya University' (arXiv:2310.06265). Chosen: placement at LNGS hall C (demonstration shield); the limit's result record carries no facility. Why: both are true of different activities; Nagoya is not an Atlas facility.
* **DMTPC current status**: claim A: 'currently deployed underground at the Waste Isolation Pilot Plant' (arXiv:1012.3912, 2010). Claim B: 2021 Annual Review describes DMTPC in the past tense and says 'A 1 m3 detector was constructed, but to our knowledge not deployed' (arXiv:2102.04596). Chosen: status `active` with `uncertain` confidence and an open interval; no end date invented. Why: no source states that the WIPP run ended.

### Unresolved fields

* NEWAGE: no official website found; collaboration formation date, leadership and roster unpublished; Laboratory B has no coordinates or site record; the 2015 NEWAGE-0.3b result (PTEP 2015, 043F01) is not recorded (paper not on arXiv, journal pages return HTTP 403); dates of the 2025 upgrade installation/commissioning (year precision only).
* MIMAC: only an LPSC group page (undated, partly outdated) as a website; hall and coordinates of the detector inside the Laboratoire Souterrain de Modane (site record is an approximate OpenStreetMap point); whether the Modane run still takes data (open interval, approximate); collaboration formal founding date and roster; arXiv:2607.23527 is a July 2026 preprint (no journal reference yet), and its abstract does not give the WIMP mass of the quoted limit.
* DMTPC: end of the WIPP run and current activity (no source after 2017; interval uncertain); dates of the MIT surface run; no WIPP dark matter result found; underground coordinates (WIPP site record is a campus-grade surface point); roster and formation date.
* CYGNO: approval date and the true start/completion of CYGNO-04 construction (October 2025 is only the first source stating it); end of the LIME underground campaign (derived: February 2022 plus about 27 months); Hall F has no site record (Hall B used, same coordinate); no reachable official website; no dark matter limit published yet.
* NEWSdm: official website news-dm.lngs.infn.it (named on slides) did not respond; CDR submission/approval dates not verified in a readable primary source; status after July 2024; Nagoya University has no facility record; roster unpublished.

### Excluded candidates

* **CYGNUS (the proposed multi-site directional network, CYGNUS-TPC / CYGNUS-1000)**: Excluded: fails the fixed-site, approval and results criteria. The feasibility study (arXiv:2008.12587) says "We propose a modular and multi-site observatory consisting of time projection chambers (TPCs) filled with helium and SF$_6$ at atmospheric pressure." and only shows "the locations of some of the candidate sites under consideration" (Fig. 2, captioned "Proposed sites for a network of Cygnus detectors", with labels Kamioka, Boulby and Gran Sasso); for its calculations the paper says "assume the entire 1000 m3 is located at Boulby, UK", a study assumption, not a host-site decision. No approval, construction or result was found. CYGNO's abstract calls CYGNUS a "proto-collaboration" (arXiv:2202.05480). Its one concrete module with a site is CYGNO (recorded). Revisit if a named CYGNUS module is approved at a fixed site.
* **D3 (Directional Dark Matter Detector, LBNL / University of Hawaii)**: Excluded: an R&D programme, not an experiment with a dark matter host site. The 2021 review calls it "an R&D collaboration between Lawrence Berkeley National Laboratory and the University of Hawaii" (arXiv:2102.04596); the lab prototype photo is "at University of Hawaii" (arXiv:1402.0043); its later detectors were deployed for beam-background monitoring in Belle II ("BEAST II beam background measurement project at SuperKEKB", arXiv:2106.13079). The review mentions a feasibility-demonstration dark matter limit from the BEAST TPCs; the primary paper was not located or read. The planned m^3-scale detector (arXiv:1402.0043) names no site. Candidate for the integrator only if the owner wants R&D collaborations.
* **NITEC (negative-ion TPC with GEMPix readout, INFN)**: Excluded: detector R&D only. arXiv:1710.01994 reports drift velocities measured with "the NITEC detector" ("NITEC is a Time Projection Chamber with 5 cm drift distance readout by a GEMPix"); no host site, approval, design report naming a site or physics result.
* **DRIFT**: Exists as `experiment:drift`; not touched. Its "complementary" lineage to the experiments here is not stated by any source read, so no lineage rows were added.
* **DMTPC 20-liter and 1 m^3 detectors**: Not recorded as detectors: the 20-liter detector was "currently under commissioning" at MIT in 2010 (arXiv:1012.3912) and the 2021 review says the 1 m^3 detector was "constructed, but to our knowledge not deployed"; no result or site.
* **MIMAC-He3 (2004 3He micro-TPC concept) and MIMAC-35cm**: Folded into `experiment:mimac` (same project, earlier concept and planned upgrade); the concept paper is arXiv:astro-ph/0412273, MIMAC-35cm is the planned upgrade (arXiv:2607.23527) measured so far in a surface laboratory (arXiv:2602.17880).
* **CYGNO-30 / CYGNO PHASE 2**: Future scale-up named in the TDR; no site, approval or design report: not recorded.
* **Ion Fluorescence Chamber (IFC)**: Seen only as an arXiv title (arXiv:2203.10198, a concept); not read, no site or results: excluded.
* **TREX-DM and other non-directional gas TPCs**: Out of this assignment (not directional). If no other agent covers TREX-DM (a micro-pattern gas TPC at Canfranc), the integrator should check; it was not researched here.
* **NEWAGE 2015 result**: Not a separate experiment; the paper (PTEP 2015, 043F01) was not readable, so no result record exists (see unresolved).

### For the integrator

* No cross-agent lineage rows were added. Possible (unsourced, so not written) relations: DRIFT (`experiment:drift`) is the other directional dark matter experiment of the same kind; the CYGNUS proto-collaboration is the umbrella naming CYGNO (not an Atlas experiment).
* New records are in `data/atlas/{experiments,detectors,collaborations}/{newage,mimac,dmtpc,cygno,newsdm}.json`, 19 `results/` files with these slugs (newage-*, mimac-*, dmtpc-*, cygno-*, newsdm-*) and new `sources/` files with the same prefixes plus `directional-recoil-detection-review-2021` and `news-letter-of-intent-2016`. Coverage rows: `.dm2/frag/directional.coverage.json`.
* Missing site records that would improve placements: LNGS Hall F (CYGNO-04, NEWSdm emulsion facility), Kamioka Laboratory B (NEWAGE), the underground WIPP location (DMTPC), a facility for Nagoya University (NEWSdm surface exposure). The existing hall/campus records share approximate coordinates; none was edited.
* CYGNO is `construction` and NEWSdm is `commissioning`; both are open-ended with approximate/uncertain confidence. DMTPC is `active` only by the no-invented-end-date rule (see conflicts).
* TREX-DM (Canfranc, non-directional micro-pattern TPC) was not covered by this assignment.


## Stream log: droplets

### Conflicts (claim / source A / source B / chosen / why)

1. **SIMPLE Phase II Stage 2 dates.** 1 May to 22 July 2010 (arXiv:1404.4309, Sec. V, "science measurements") / 12 April to
   22 July 2010 (arXiv:1106.3014, "Stage 2 data was obtained") / "Stage 2, 2010-2011" and "Phase II of SIMPLE (2009-2011)"
   (arXiv:1504.05475, Introduction). Chosen: the 2014 paper's dates for the two `run` intervals (the most detailed and the
   collaboration's own), lifecycle end 2010-07 marked approximate, `completed` interval marked uncertain. Why: the 2015 paper
   may count the later analysis, not data taking; no source states a shutdown.
2. **SIMPLE 2012 vs 2014 numbers (same data).** sigma_p(SD) 4.2e-3 pb (arXiv:1106.3014 v3, PRL 108, 201302) / 4.3e-3 pb (arXiv:1404.4309,
   after removing 1.94 kg d of installation data). Chosen: two separate result records; the 2014 paper is the re-analysis.
3. **arXiv versions.** For 1106.3014 and 1003.2987 the quoted abstract is the PRL-accepted version whose arXiv comment says the
   contours changed ("slightly weakened limit contours"; "corrected SI contour"), so those two results are dated by the latest version;
   every other arXiv result is dated by v1 and carries a note naming the version whose abstract is quoted.
4. **TREX-DM installation date.** "During 2017 into 2018 ... installed at the hall A of LSC" (official page) / "installed at the end
   of 2018" (arXiv:2312.12622) / "moved underground in 2018" (arXiv:1812.04519). Chosen: construction 2017 to 2018 and commissioning
   2018 to 2019 (year precision, approximate). Why: the three statements are compatible at year precision.
5. **PICASSO "SNOLAB" in 2002.** The 2002 detectors sat in the SNO water-purification gallery (arXiv:hep-ex/0312049); the facility record
   `facility:snolab` starts 2011-03 (uncertain, Wikipedia-sourced). Chosen: host role on `facility:snolab` from 2002-07 with a note;
   the validator warns (`experiment-before-facility`); see the integrator section.
6. **LSBB depth.** 500 m of rock over the deepest hall (arXiv:astro-ph/9910192 abstract; the official history page says "plus de 500
   mètres") / 505 m for the GESA cavern (arXiv:1404.4309) / 518 m deepest vault (arXiv:1005.0158, read, not cited). Chosen: 500 m on
   the site; 505 m as the SIMPLE detector's depth spec. Not contradictory (different points).
7. **PICASSO official site says "presently taking data".** The page is undated and its news list ends in February 2017; the final paper
   says data taking ended January 2014. Chosen: the paper; the website value is kept with a stale-page note.

### Unresolved fields (null or uncertain, each with a note in the record)

* PICASSO: founding date of the collaboration and roster; date and end of the Montreal preliminary runs; end of the SNO-gallery
  phase; the "Ladder Lab" at SNOLAB (October to December 2010) is not an Atlas hall; no formal lineage row to PICO yet.
* SIMPLE: end of data taking (2010 vs 2011 sources); collaboration founding date and roster; **no official website** (the group's Lisbon
  page named on the LSBB page does not resolve; the two archive addresses tried returned 404); LSBB founding / conversion date (earliest dated use
  July 1999 only); **LSBB coordinate is campus-grade (OpenStreetMap, approximate)**: no paper or official page read gives a latitude and
  longitude; the archived LSBB "Coordonnées" article was not captured.
* TREX-DM: no WIMP exclusion limit from TREX-DM data exists in any source read (3 performance/background results, tier C); the
  collaboration is a project of the Zaragoza group (the papers never say "collaboration"), no formation date or roster; operating status
  after December 2025 unconfirmed.
* ORPHEUS: end of operation (no source after the February 2005 review; `completed` is inferred and uncertain); the Bern laboratory's
  opening date, position (campus-grade point of the group's address, Sidlerstrasse 5) and present status; no official website; the 2002
  conference results (refs 16-18 of the 2004 paper) were not read; no numerical limit in any abstract.
* MOSCAB: date of the move to LNGS (between July 2017 and June 2021), the LNGS hall (placed on the facility's primary site
  `site:lngs-hall-b` as a placeholder, flagged in the placement note), current status, collaboration roster and founding date; no
  dark matter result.

### Excluded candidates (with reasons)

* **COUPP, PICO (PICO-2L, PICO-60, PICO-40L, PICO-500), SBC, SPICE**: superheated-liquid bubble chambers, but the tree already holds
  records for them written by another agent (collaborations coupp, pico, sbc; experiments coupp-2kg, coupp-4kg, pico-*, spice); not duplicated.
* **KamLAND-PICO / PICOLON**: NaI(Tl) scintillator projects (arXiv:1407.3542), not superheated droplets; PICOLON already exists.
* **SIMPLE's 1996 to 1999 prototype work near Paris** (26 m calcite overburden, arXiv:astro-ph/9610266, arXiv:astro-ph/0001511): an
  unnamed shallow site 40 km south of Paris, R&D only; recorded in the SIMPLE collaboration's start date, not as a separate experiment.
* **PICASSO's "Picasso Lab" in Montreal**: a surface R&D laboratory, no results from it as an experiment; part of the PICASSO history.
* **Tokyo, Gran Sasso and other SSG prototypes before ORPHEUS** (arXiv:cond-mat/9411072): the Bern SSG recoil-response paper is kept as an
  ORPHEUS `technology_milestone`; no other named superheated-granule experiment with a fixed site was found.
* **BUBBLE / neutron-dosimetry droplet detectors**: not dark matter searches.
* No other superheated-liquid, granule or droplet dark matter experiment meeting the bar turned up in the arXiv title and abstract
  searches and web searches I ran ("superheated" with "dark matter", "droplet", "granules", "geyser", "bubble"; PICASSO, SIMPLE,
  ORPHEUS, MOSCAB, TREX-DM titles and authors). The searches are not exhaustive for non-arXiv literature.
* MOSCAB was **included** despite being borderline: bar item 3 (published design report naming the host site) rests on arXiv:1708.00101,
  which names LNGS as the planned site; if the lead prefers a stricter reading it can be dropped by deleting the five `moscab` files
  (experiment, detector, collaboration, two results) and the coverage row.

### For the integrator (cross-agent lineage and loose ends)

**PICASSO's merger with COUPP into PICO** (verbatim, all checked against the fetched text):

* PICASSO official news page, https://www.picassoexperiment.ca/news.php, item "November 2013": "The PICASSO and COUPP collaborations
  decide to join forces !" and "The new collaboration is called PICO (picoexperiment.com)".
* arXiv:1611.01499 (PICASSO final results), Sec. 1: "the most stringent limits set by PICO (formed from a merger of PICASSO and COUPP)".
* arXiv:1503.00008 (PICO-2L, Phys. Rev. Lett. 114, 231302): "The PICO Collaboration (formed from the merger of PICASSO and COUPP)".
* arXiv:1611.01499, abstract, for a `predecessor` or `upgrade_of` row if wanted: "The pioneering efforts of the PICASSO experiment have paved
  the way forward for a next generation detector incorporating much of this technology and experience into larger mass bubble chambers."
* `collaboration:pico` (another agent's record) already says "formed by the merger of COUPP and PICASSO" from a CosPA 2013 abstract and
  dates its start to 2013; the PICASSO news item dates the decision to November 2013, consistent. `collaboration:picasso` ends with a
  `completed` interval from 2013-11 citing that news item. Suggested lineage (not written, since the PICO records belong to another
  agent): on `experiment:picasso`, a `predecessor` row pointing to the PICO experiment the owner prefers (arXiv:1503.00008 reports the PICO-2L chamber run
  from October 2013 to May 2014) or a `same_program` row; or a collaboration-level link only.

Other items:

* `facility:snolab` starts 2011-03 (uncertain, Wikipedia-sourced), yet SNO and its water-purification gallery hosted PICASSO from July 2002
  and SNOLAB's own pages call it an expansion of SNO. The validator warns for `experiment:picasso`. Re-date the facility (SNO from 1999/2000)
  or accept the warning.
* New facilities: `facility:lsbb-rustrel` (Laboratoire Souterrain à Bas Bruit, Rustrel, FR; status active; operator CNRS and Avignon
  Université per lsbb.eu) and `facility:bern-underground-laboratory` (University of Bern, 70 m.w.e.; status active but uncertain).
  Both sites carry campus-grade approximate points (A17/A23 warnings expected). Other streams that mention LSBB (for example the MIGA
  atom interferometer, ELGAR, or a geophysics stream) should reuse `facility:lsbb-rustrel`.
* `collaboration:trex-dm` is the T-REX project of the Universidad de Zaragoza (GIFNA/CAPA). The same group runs ANAIS-112 at the same
  laboratory as a separate experiment (`collaboration:anais`); they are deliberately not merged. T-REX also develops the CAST/IAXO Micromegas
  readouts (official page); `experiment:iaxo` exists in the tree and no lineage to it was written.
* `site:lngs-hall-b` hosts `experiment:moscab` only as a placeholder (hall unknown).
* `src:simple-lsbb-project-page` is an Internet Archive capture of the LSBB page on SIMPLE (original URL dead; `archive_url` recorded).
  The two Nominatim sources are geocoders (skipped by the checker, rank 8, campus-grade points only).


## Stream log: lowmass

### 3. Conflicts (claim / source A / source B / chosen / why)

1. TESSERACT schedule at LSM. NPB 2024: planning to produce a concept by end of 2025 and first searches in 2026. LBNL news (5 Mar 2025): "Construction is slated to begin in 2025, with the experiment coming online around 2029". TAUP 2025 slides (24 Aug 2025): "The two setups will be in LSM between 2027 and 2028" (timeline slide: commissioning at LSM 2027, first science data taking 2028). CPAD abstract (Oct 2025) and IDM 2026 abstract (June 2026): 2028 ("Full integration of the TESSERACT setup at the Modane Underground Laboratory (LSM) is planned for 2028."). Chosen: the two latest, as `planned` intervals (2027-2028; 2028). Why: the most recent sources; the earlier ones are recorded in the notes.
2. SPICE and HeRALD as separate experiments. The collaboration's own site: "developing two experiments, SPICE and HeRALD"; Comm. Phys. 2026 review: "the SPICE experiment", "the HeRALD experiment"; but NPB 2024 calls them "detector technologies" and CPAD 2025 / LBNL call them "detector modules" of TESSERACT. Chosen: separate records linked `same_program` to experiment:tesseract, with a note in each record. Why: the collaboration's official statement and named, separately described programmes; if the integrator prefers one record, delete herald/spice (and their detectors) and move the two helium results to tesseract.
3. First-limits abstract (arXiv:2503.03683) prints the resolution as "361.5 +- 0.4 MeV/c^2" (a unit slip; the TESSERACT silicon prototype resolves a few hundred meV). Not used as a number. The 258.5 meV figure comes from arXiv:2505.16092.
4. DELight host. The assignment guessed Modane; no DELight source read names Modane. The TAUP 2025 overview (arXiv:2512.15278): "In phase-I, DELight will be located at the Vue-des-Alpes (VdA) underground laboratory". Chosen: Vue-des-Alpes. The KIT release of 2 April 2026 says only "in an underground laboratory".
5. DELight phase-I helium volume: 10 L (arXiv:2209.10950 v2, "The first DELight detector cell will hold a 4He volume of 10 L") vs ~1 L (arXiv:2512.15278 and delight.kit.edu: "~1L volume"; phase II 10 L). Chosen ~1 L (newer, official). 
6. Vue-des-Alpes overburden: 230 m / ~630 mwe (DELight paper) vs 235 m / 620 m.w.e. (GeMSE papers, the laboratory's users). Chosen the GeMSE values.
7. Oscura detector size: 28 gigapixels (white paper, arXiv:2202.10518) vs 26 gigapixels (JINST paper, arXiv:2304.04401). Detector text says 28 (white paper); the JINST figure is not used.
8. Oscura schedule: white paper (Feb 2022) "ready to start construction in late 2024"; SNOLAB 2025 report: design stage finished, "technically ready to begin construction, but a clear funding path for the full-scale experiment has not yet been secured". Chosen: `proposed` with no construction interval (no source reports construction).
9. DarkSPHERE size: 3 m (2023 conceptual design), 1.4 m (a University of Liverpool studentship page), 30 cm version in preparation (IOP April 2026 and IDM June 2026 abstracts). Recorded the 3 m design with a note; no source states the final size.
10. BULLKID-DM dice: "more than 2000" (abstract) vs 2300 (table); mass 800 g is stable.
11. DELight status. `approved` (DFG Research Unit 6006 funding "to design, build, and operate Phase-I", March 2026, official page) although the 2025 version of the first paper still says "currently in its planning phase". Chosen `approved` from 2026-03; a cryogenic platform is being built in Heidelberg, which is not enough for `construction`.

### 4. Unresolved fields

- external.inspire_experiment is null on all seven experiments (INSPIRE not consulted).
- TESSERACT, SPICE, HeRALD: no source gives the founding date of the collaboration, SPICE or the TESSERACT name; member counts not published; no approval date for the LSM installation (slides of two earlier talks say "Selected for DOE funding starting FY25", scope unstated, not cited as an interval); the April 2026 APS abstract on HeRALD (https://meetings-archive.aps.org/smt/2026/apr-h92/6/) returned HTTP 403 and is not cited; the surface prototype lab (sub-basement of Birge Hall, UC Berkeley) has no Atlas site; the French Ge/Si module has no record (proposal only).
- Oscura: no standalone website (Fermilab page used, partly dated); no approval or funding statement; no physics result; no source gives the SNOLAB lab area.
- DELight: coordinates of the laboratory (approximate tunnel centre only); the host of phases II and III; the operator of the laboratory; no laboratory website; no dark matter result.
- BULLKID-DM: hall within LNGS ("cryo-platform", placed on the Hall A record only as an approximate LNGS point); no website; approval/funding not stated; no dark matter result.
- DarkSPHERE: final size; approval/funding; no result.

### 5. Excluded candidates (reason)

1. QUEST-DMC (superfluid 3He bolometer, Lancaster/Royal Holloway/Sussex): published concept and sensitivity papers (EPJC 84, 248; JCAP 2025; JLTP 2024) but no source names a host site; the detector is "located at the surface" (arXiv:2505.17995), a facility "located at the planet's surface" (arXiv:2310.11304); Boulby appears only as a material-screening site. Fails the fixed-site part; no physics result. Reconsider if the lead accepts a surface laboratory (A26 'ground-based') once a source names the laboratory.
2. QROCODILE (SNSPD nanowire): published PRL 135, 081002 (2025) with world-leading limits (30 keV to MeV), but a surface table-top run in a dilution cryostat; neither the paper nor the collaboration's pages nor the university release name where it ran; the underground run (NILE QROCODILE) names no site. Fails the fixed-site part. If the lead accepts the University of Zurich (the first author's affiliation) as the site, it could be added as a tier-C experiment with the PRL result (claim "report new world-leading constraints on the interactions of sub-MeV dark matter particles with masses as low as 30 keV").
3. ALETHEIA (liquid-helium TPC, CIAE Beijing): 30 g prototype R&D at CIAE; the 10 kg detector "would be operated underground" with no site named; no result. Fails the fixed-site part.
4. DAREDEVIL (INFN-LNGS GaAs and other low-gap calorimeters, EPJC 84, 749 (2024); IDM 2026 talk): detector-development project; first GaAs calorimeter test in a dilution refrigerator; no experiment design naming a host, no physics result. Fails.
5. CRYOSEL (Ge heat-and-charge detectors with SSED, EDELWEISS/Ricochet lineage) and TES4DM: detector R&D prototypes of the French module proposed for TESSERACT; not experiments.
6. KIPM at NEXUS (Caltech/Fermilab kinetic-inductance phonon detector): detector test at the NEXUS facility; no named experiment, no host decision, no result.
7. MIGDAL (observation of the Migdal effect, IDM 2026 talk): a measurement of an atomic effect that supports low-mass dark matter searches, not a dark matter search itself; not read in detail; the integrator may judge it.
Also not mine: LDMX and other accelerator searches; NEWSdm (already written by another agent), CYGNO, TREX-DM, COSINUS, SBC (assigned elsewhere); NEWS-G3 (inside experiment:news-g); HVeV@CUTE (SuperCDMS); ROSEBUD (older, not newer low-mass; not checked).

### 6. For the integrator

- **New facility and site created against the letter of the brief.** The brief says to create a laboratory only if the assignment says so; DELight (approved, phase-I host named) needs one and none existed, so facility:vue-des-alpes-underground-laboratory and site:vue-des-alpes-underground-laboratory were written. To undo: delete data/atlas/{facilities,sites}/vue-des-alpes-underground-laboratory.json, the four DELight records (experiments, detectors and collaborations delight.json, results/delight-mmc-resolution-2023.json) and their sources, and drop the DELight coverage row.
- Suggested cross-links not written (rows would sit on records owned by others): TESSERACT's French Ge/Si module "is based on the recent developments performed by the EDELWEISS [34] and RICOCHET [12,54,13] collaborations" (NPB, Sec. 2); Oscura "unifies the expertise and infrastructure developed through DAMIC, SENSEI, and DAMIC-M" (SNOLAB 2025 report, Sec. 4.5; DAMIC-M "has expressed interest in continuing R&D with CCDs at LSM as part of the development of the next-generation OSCURA experiment", same report); DarkSPHERE builds on NEWS-G (written on the DarkSPHERE record as `same_program`).
- A22/A25: no geometry map was written for the new site.
- DarkSPHERE reuses src:geo-boulby-darksphere-2023 (its URL is the arXiv pdf, so the duplicate-source check did not match the abs URL; the validator would otherwise flag A20).
- All seven coverage rows are category direct_dark_matter, owner dark-matter-2, in .dm2/frag/lowmass.coverage.json.


## Stream log: pico

### Conflicts

| claim | source A | source B | chosen | why |
|---|---|---|---|---|
| PICO-500 start of commissioning | SNOLAB report 2026-05-26 (src:currency2-snolab-report-2026-05-26): "Expect to begin commissioning toward the end of 2026 with science operations starting in 2027"; UCLA DM 2025 abstract: "scheduled start of commissioning in late 2026" | PICO talk, DPF 2026 (20-24 July 2026): "Timeline: fluid fill in early 2027, with commissioning beginning mid-to-late 2027." | B, as the planned end (2027) of the `construction` interval; no commissioning interval (A21 forbids a planned start on a realised status) | Later and from the collaboration itself; A is recorded in the interval note. |
| PICO-500 size | PICO home page: "a target mass approximately 250 kg"; arXiv:1806.01417 (2018): initial 1 t of C3F8 | PICO-500 page, UCLA abstract, DPF 2026: active volume about 250 litres (250 L) | 250 L (key spec, approximate) | Three independent statements agree; mass and the 1 t design are older or inconsistent. Both are in the spec note. |
| Hall of PICO-2L | PICO-2L page: 'located in the ladder labs'; PICO-60 page: 'Unlike PICO-2L, this larger detector was located in the ladder lab area' | CosPA 2013 slides: PICO-2L re-used 'the old COUPP-4 location', which arXiv:1204.3094 puts in the J-Drift | No hall asserted | The three statements cannot all hold; the SNOLAB site record is one point anyway. |
| SNOLAB start vs COUPP-4kg | facility:snolab (not owned here) starts 2011-03 (Wikipedia-sourced) | arXiv:1204.3094: COUPP-4kg operated in SNOLAB from September 2010 | Record the paper's dates; the validator warns experiment-before-facility for coupp-4kg and pico-60 | SNOLAB hosted earlier experiments (SNO); the facility interval is another stream's. Left for the integrator. |
| COUPP-2kg fill | Science 2008 abstract: 1.5 kg of CF3I | Fustin dissertation: the 'COUPP 2 kg bubble chamber' | Name COUPP-2kg, key spec 1.5 kg | The paper's own number for the fill; the 2 kg name is the chamber's. |
| COUPP-60 vs PICO-60 | Fermilab news 2017: 'The PICO-60 detector was originally called COUPP-60' | Brief: separate records with COUPP-60 -> PICO-60 lineage | One experiment `experiment:pico-60` (alias COUPP-60, commissioning at Fermilab as its first intervals) | A4: one canonical entity per real thing; COUPP-60 never produced results under its own name (its only run is PICO-60 run 1). The lead may split it. |
| When PICO-40L runs | arXiv:1905.07367 (2019): 'will take WIMP search data starting in 2019' | Official PICO-40L page: construction 2019-2020, updates 2021-2022, commissioning 2023, operations later in 2023 | Official page | Later, by the collaboration; the 2019 sentence was a forecast. |
| SBC-LAr10 stage | Snowmass white paper (July 2022): 'is now being commissioned at Fermilab'; PoS TAUP2023 (2024): 'SBC is building its first prototype at Fermilab' | SBC talk 2026-03-17: moved to MINOS 2024-05, first fill 2025-09, ~6 months of data taking | Construction 2021-02 to 2022-07, commissioning 2022-07 to 2025-09, active from 2025-09 (approximate) | The 2026 talk gives the detailed history; the two older sentences describe the same prototype at earlier stages. |
| Status label on SNOLAB's PICO page | snolab.ca/experiment/pico (read 2026-10-26): Status 'Commissioning' | PICO home (Dec 2025 capture) and DPF 2026: PICO-40L operating since 2023 | PICO-40L `active`; PICO-500 `construction` | The SNOLAB label covers the whole programme and is not dated; PICO's own pages are specific. |

### Unresolved fields

- COUPP collaboration formation date and roster; PICO formation date (only 'between April 2013 and 13 November 2013'); SBC formation date and roster. PICO's SNOLAB-page counts (68 people, 19 institutions, 7 countries) are undated.
- COUPP-2kg end of operation (completed row 2009-08 is `uncertain`); COUPP-4kg move date to SNOLAB and dates of the 2012 run.
- PICO-60: start of COUPP-60 commissioning (year 2010 is `approximate`: 'being commissioned' in a paper of August 2010), exact move date in 2012, start of run 2 (2016) and end (summer 2017).
- PICO-40L: months for commissioning and start of operations (2023); no physics-results paper yet.
- PICO-500: start of construction (bracketed April 2024 to March 2025); funding decision date (first 'funded' source is June 2018); schedule conflict (see Conflicts).
- SBC: no official website; SBC-SNOLAB installation date; SBC-LAr10 construction start (2021-02 is the first dated proceedings); no DM or CEvNS physics result yet.
- No official COUPP website reachable (an Internet Archive capture of coupp.fnal.gov returned 404); `links.website` of coupp records is empty.
- `external.inspire_experiment` is null on every experiment (INSPIRE not contacted).
- Coordinates: no hall-level site for the NuMI/MINOS tunnel or the SNOLAB halls.

### Excluded candidates

- PICASSO and SIMPLE: belong to agent `droplets` (already written by it, as are MOSCAB and ORPHEUS).
- PICO-250L (ton-scale concept named in 2013-14 talks, e.g. CosPA 2013 abstract "PICO-250L, a ton-scale experiment, is currently in the engineering and design phase"; a Moriond 2014 slide pairs it with the words '500 Kg Scale Bubble Chamber'; the March 2012 dissertation mentions 'a 500 kg bubble chamber is also under development'): only talks and a thesis remark, no design report naming a host site, and no source says it became PICO-500. Fails the bar as a separate record; noted in the PICO-500 record.
- COUPP-500 (the 500 kg chamber in the Fustin dissertation): same reason as PICO-250L.
- COUPP-60 as a separate experiment record: merged into `experiment:pico-60` (see Conflicts).
- InDEx (Indian Dark matter search Experiment, superheated C2H2F4 emulsion droplet detectors at the 555 m deep Jaduguda Underground Science Laboratory, JUSL, India; first result arXiv:2501.02833, run 2 in Phys. Rev. D 112, 042003 (2025), arXiv:2510.06921): meets the bar (named, fixed underground site, published results) but needs a NEW facility and site (JUSL is not in the Atlas) and is a droplet detector; my assignment forbids creating facilities, so it is left for the lead (details under 'for the integrator').
- KamLAND-PICO (arXiv:1407.3542): NaI(Tl) scintillator project, not a bubble chamber (PICO-LON family).
- CIRTE (COUPP Iodine Recoil Threshold Experiment, arXiv:1304.6001), the Drexel Bubble Chamber (arXiv:1905.07367), the 30-g xenon bubble chamber at Northwestern (arXiv:1702.08861, 2410.07241; recorded only as SBC precursor results) and snowball chambers (arXiv:2401.15064): R&D or calibration test chambers, not dark-matter experiments with a named fixed site.
- SBC reactor CEvNS version (arXiv:2101.08785, 2207.12400): a stated option with no named host site or design report.
- Bubble Chamber Detectors with Light Nuclear Targets (arXiv:2203.11319): neutrino-cross-section white paper, not dark matter.
- Xenon Bubble Chambers for Direct Dark Matter Detection (arXiv:1601.05131) and the 1996 'Dark Matter Search with Moderately Superheated Liquids' (hep-ex/9602004): concept papers with no named experiment and site.
- PICO-40L physics results: none published; not invented. The two PICO-40L-linked result records are a prototype design validation (Drexel) and the electron-recoil nucleation model (with a PICO-40L projection).

### For the integrator

**PICASSO and COUPP merged into PICO** (verbatim sentences from the sources I read; use for lineage rows and for `collaboration:picasso` / `collaboration:coupp` -> `collaboration:pico`):

- src:pico-official-site-home (capture of 31 December 2025): "PICO is a joint collaboration formed by the merger of the PICASSO and COUPP collaborations."
- src:pico-2l-first-results-2015 (arXiv:1503.00008): "The PICO Collaboration (formed from the merger of PICASSO and COUPP) has now operated a 2.90 kg C3 F8 bubble chamber from October 2013 to May 2014 in the SNOLAB underground laboratory in Canada, at 6010 meters of water equivalent depth."
- src:pico-cospa2013-abstract (13 November 2013): "I will discuss a suite of bubble chambers for dark matter detection in various stages of development by the former COUPP collaboration and the new PICO collaboration, formed by the merger of COUPP and PICASSO."
- src:pico-cospa2013-slides (summary slide): "COUPP and PICASSO have merged to form the PICO collaboration to search for dark matter with superheated liquid detectors."
- PICASSO final paper (arXiv:1611.01499, abstract; source record belongs to `droplets`): "The pioneering efforts of the PICASSO experiment have paved the way forward for a next generation detector incorporating much of this technology and experience into larger mass bubble chambers."

Suggested links: the merger is stated at collaboration level only. No source I read gives an experiment-level lineage from `experiment:picasso`. COUPP experiment lineage is already in place: `experiment:coupp-4kg` predecessor `experiment:coupp-2kg`; `experiment:pico-2l` and `experiment:pico-60` predecessor `experiment:coupp-4kg`; `experiment:pico-40l` predecessor `experiment:pico-60`; `experiment:pico-500` upgrade_of `experiment:pico-40l`. If a PICASSO link is wanted, `same_program` with the CosPA 2013 slide sentence is the honest relation (edit only the lineage field).

Other points:

- `experiment:pico-60` has alias COUPP-60 and covers the COUPP-60 commissioning at the MINOS near-detector hall (prototype placement at Fermilab) and the 2012 move; a separate `experiment:coupp-60` was not created (see Conflicts).
- `facility:snolab` (not mine) starts 2011-03 from Wikipedia; COUPP-4kg is documented at SNOLAB from September 2010 (arXiv:1204.3094). Two validator warnings (experiment-before-facility) follow from that.
- Placements still at campus or whole-lab precision for the local-map layer: COUPP-2kg, COUPP-4kg (Fermilab run), COUPP-60 engineering run, SBC-LAr10 (all in the NuMI/MINOS tunnel at Fermilab, a hall with no site record); at SNOLAB: COUPP-4kg (J-Drift), PICO-60 and PICO-40L (Ladder Labs), PICO-500 (Cube Hall).
- InDEx / JUSL candidate for whoever may create the facility: JUSL is described as a "555m deep underground laboratory" (arXiv:2501.02833, abstract: "installed at the 555m deep underground laboratory, JUSL during July to Dec 2022"); InDEx run 1: 500 ml tetrafluoroethane (C2H2F4) superheated emulsion detector, 48.6 days at 5.87 keV, 2.47 kg-days; run 2: 1.95 keV threshold, 70.4 g active liquid, 102.48 days (arXiv:2510.06921, Phys. Rev. D 112, 042003). Proceedings: arXiv:2509.00873. No source I read says InDEx is a PICO detector.
- The SNOLAB 'Experiments' page lists PICO with Status 'Commissioning' (7 countries, 19 institutions, 68 people); it is undated and covers the programme.
- The PICO website (picoexperiment.com) is gone (HTTP 410 on 2026-10-26) but captured by the Internet Archive; the website links are `uncertain` for that reason. If a successor site appears the links should be updated.
- arXiv:2401.07384 is a 2012 PhD dissertation posted to arXiv in 2024 (source type `arxiv`, rank 10); it carries the COUPP chamber history (COUPP 2 kg chamber is the predecessor of the 4 kg chamber; the 60 kg chamber's engineering run at the MINOS near-detector hall).


## Stream log: nai-rest-ge

### Conflicts
| claim | source A | source B | chosen | why |
|---|---|---|---|---|
| Completion of the GENIUS-TF external shielding | PhD thesis (arXiv:0812.1206): 'In November 2003 the external shielding of Genius-TF was completed' | NIMA 530 abstract (OSTI 20565502): 'the completion of the external shielding, which took place in December 2003' | neither used for an interval boundary | both are second-hand; only noted in the experiment's notes |
| Hall of GENIUS-TF | 'between halls A and B' (arXiv:hep-ph/0309170) | Atlas has three LNGS hall records sharing one point | site:lngs-hall-b | all three share one approximate point; note on the placement |
| DAQ/detector naming of IGEX dark matter detector | 2000 proceedings: '2 kg 76Ge IGEX detector (RG-2)' (hep-ph/0011318) | 2002 talk: 'One of the IGEX detectors of 2.2 kg (active mass ~2.0 kg)' (astro-ph/0211535) | 2.2 kg / ~2.0 kg active from the 2002 talk; RG-2 mentioned only as the 2000 name | not certain that it is the same detector |
| SUPL / other agents' items | none in this slice | | | |

### Unresolved fields (nobody published / not readable)
* HDMS: shutdown date (last evidence: a May 2006 conference paper that has it operating); hall within LNGS; website; abstract of Phys. Lett. B 609 (2005) 226 (not on arXiv, publisher blocked; its spin-dependent WIMP-neutron limit is recorded from the 2006 Physica Scripta paper that cites it, exposure 85.48 kg d, no cross-section value); collaboration formation date and roster.
* GENIUS-TF: construction start (funded by June 2002, first detectors installed 5 May 2003); exact end (thesis: 2003-2006); no dark matter limit published in the sources read; website (the 2003 home page www.mpi-hd.mpg.de/non_acc/ gave only an empty Internet Archive capture).
* ROSEBUD: start beyond 'settled in 1999' (the slide 'ROSEBUD 1995 - 2011' is ambiguous and not used); end (latest evidence Nov 2011); results of 2007-2010 (BGO, LiF, sapphire scintillating bolometers) not read; live website (404; Internet Archive capture of 28 April 2017 read: a frames page with only its title text, recorded `uncertain`).
* IGEX-DM: start of the dark matter phase (first paper February 2000: 'A recent upgrade...'); end (latest evidence Nov 2002).
* COSME: operation between 1992 and 1998; end (removed from the shield by Nov 2002); the 1990-1992 first-operation papers (Garcia et al.) not read.
* Tokyo search: end (latest run Dec 2002 - Jan 2003); no named collaboration; website.
* Statuses of all six are `completed` with `uncertain` confidence where no source gives the end: the completed interval starts at the year of the latest evidence and is labelled as such (no end date was invented).

### Excluded candidates (reason)
* **IGEX (neutrinoless double-beta decay experiment)**: primarily 0vbb. Quote (arXiv:hep-ex/0002053, abstract): "The IGEX Collaboration enriched 76Ge double-beta decay detectors are currently operating in the Canfranc Underground Laboratory". Its dedicated dark matter phase, with its own DAQ 'IGEX-DM' ("The data acquisition system for the low-energy region used in dark matter searches (referred to as IGEX-DM) is based on standard NIM electronics", same paper), IS recorded as experiment:igex-dm: a quote shows the dark matter search is a named, separate experiment, as the assignment allows.
* **Heidelberg-Moscow**: primarily 0vbb. Quote (arXiv:hep-ph/0404062, abstract): "The HEIDELBERG-MOSCOW experiment, which is the most sensitive double beta decay experiment since ten years". Its WIMP limits (arXiv:hep-ex/9811045: "New results after 0.69 kg yr of measurement with an enriched 76Ge detector of the Heidelberg--Moscow experiment") are a by-product analysis of the double-beta data with no separate dark matter detector or DAQ.
* **EURECA**: no design report and no approval. Oxford group page (https://users.physics.ox.ac.uk/~kraus/research/EURECA.htm): "EURECA (European Rare Event Calorimeter Array) is a proposed one tonne dark matter experiment using cryogenic detectors." and "We aim to begin construction in the Laboratoire Souterrain de Modane sometime after 2013." EDELWEISS-II paper (arXiv:1106.1454): "The installation site would be an extension of the present Laboratoire Souterrain de Modane." EDELWEISS (arXiv:1305.2808, 2013): "further plans for a next generation experiment, EURECA, are discussed". Never approved or funded for construction in any source read; the RPScint'2008 proceedings (arXiv:0903.1539) are a workshop. (The brief's bar would admit a *proposed* EURECA if the lead wishes to relax the assignment's 'design report AND approved' rule; the host would be facility:modane-underground-laboratory.)
* **MALBEK** (Majorana Low-background BEGe at KURF): host facility is the Kimballton Underground Research Facility, not an Atlas facility and I may not create it. Quote (arXiv:1407.2238, abstract): "we have deployed a modified, low-background broad energy germanium detector at the Kimballton Underground Research Facility". The paper (a Majorana R&D proceedings) discusses backgrounds in the WIMP region of interest and surface-event contamination, with no limit in the abstract (its body analyses 89.5 kg-d for a WIMP search below 10 GeV/c^2). Listed for the integrator.
* **GEDEON**: "a proposed extension of the IGEX dark matter search" (arXiv:astro-ph/0211535); no design report or approval.
* **GENIUS (the full observatory)**: "GENIUS is a proposal for a large scale detector of rare events." (arXiv:hep-ex/0012022); only its test facility was approved and built.
* **ORPHEUS (Bern)**: meets the bar, but is covered by the droplets agent (facility:bern-underground-laboratory, $D/frag/droplets.*); not duplicated.
* **SIMPLE, PICASSO, COUPP/PICO and other bubble/droplet detectors, directional, argon and low-mass cryogenic (TESSERACT, SPICE/HeRALD...) projects**: other agents' slices ($D/frag/*.coverage.json); not researched here.
* **Tokyo programme's surface and shallow-site phases** (21 g LiF at the Hongo campus, arXiv:hep-ex/9709019; eight 21 g LiF absorbers at Nokogiriyama, about 15 m.w.e., arXiv:hep-ex/9904034): sites not in the Atlas; kept in the notes of experiment:tokyo-dark-matter-search, no results recorded.
* **ELEGANT VI** (25 CaF2 scintillators for WIMPs at the Oto Cosmo Observatory; RCNP annual report 2001, https://www.rcnp.osaka-u.ac.jp/~annurep/2001/genkou/sec3/takahisa2.pdf: "ELEGANT VI consists of 25 CaF2 scintillators surrounded by 20 CsI scintillators."): not researched; it shares the Oto facility with ELEGANT V (the parent's item 3). Flagged for the parent.
* **NaI/CsI family, SABRE, DM-Ice, PICOLON/ELEGANT V, COSINUS, COSINE-200**: the parent's items.

### For the integrator
* Add the coverage rows of `$D/frag/nai-rest-ge.coverage.json` (6 rows, owner dark-matter-2, tiers B x4 / C x2).
* Proposed lineage rows (I did not edit existing records). `complementary` rows live on the lexicographically smaller id:
  1. on experiment:dama-nai: {"experiment_id": "experiment:hdms", "relation": "complementary", "quote": "HDMS should be able to test the DAMA evidence region within about three years", "locator": "arXiv:hep-ph/0206151, Sec. 3", "sources": ["src:hdms-first-results-final-setup-2003"], "confidence": "approximate", note: 'DAMA evidence region' of the 2000-2002 DAMA/NaI results}.
  2. on experiment:dama-nai: {"experiment_id": "experiment:genius-tf", "relation": "complementary", "quote": "With about 40 kg of natural Ge detectors operated in liquid nitrogen, GENIUS-TF could exclude (or directly confirm) the DAMA annual modulation signature within about two years of measurement.", "locator": "arXiv:hep-ex/0012022, abstract", "sources": ["src:genius-tf-test-facility-2002"]}.
  3. on experiment:dama-nai: {"experiment_id": "experiment:igex-dm", "relation": "complementary", "quote": "The new IGEX exclusion contour enters, by the first time, the DAMA region by using only raw data, with no background discrimination, and excludes its upper left part.", "locator": "arXiv:hep-ex/0110061, abstract", "sources": ["src:igex-dm-improved-constraints-2002"]}.
  4. on experiment:naiad (UKDMC NaI): {"experiment_id": "experiment:tokyo-dark-matter-search", "relation": "complementary", "quote": "Our results excluded the parameter space complementary to the results obtained by NaI detectors of UKDMC experiment.", "locator": "arXiv:astro-ph/0306365, abstract", "sources": ["src:tokyo-naf-bolometer-kamioka-2003"]}.
  Already written in my own files: experiment:cosme same_program experiment:igex-dm (quote "The COSME detector described below, is also operating in the same shield at Canfranc.", arXiv:hep-ex/0002053, Sec. 2; confidence approximate: the papers do not call them one programme).
* Candidates that need a new facility (not created): MALBEK at the Kimballton Underground Research Facility (KURF; arXiv:1407.2238: "Kimballton Underground Research Facility (KURF) in Ripplemead, Virginia"; "MALBEK was moved to KURF on 12 January 2010. The KURF building is on the 14th level of the Kimballton mine at an overburden of 1450 meters of water equivalent shielding."; "Results from an analysis of 89.5 kg-d of data are presented here."; a 465 g Canberra BEGe, an R&D detector of the Majorana Demonstrator); EURECA would use facility:modane-underground-laboratory if the lead relaxes the rule.
* The parent's records for NaI/CsI/CaF2 neighbours may want a pointer to ELEGANT VI (Oto Cosmo Observatory), see Exclusions.
* Cross-agent notes: the SUPL facility record gives construction 'completed in August 2022'/unveiled August 2022 while the SABRE South TDR says 'The construction of SUPL was completed in 2023' (parent's item).
* Conflict with brief wording: the assignment excludes IGEX; I record IGEX-DM (the dark matter phase, separately named in the papers) and exclude only the 0vbb experiment. If the lead disagrees, delete experiment/detector:igex-dm, collaboration:igex and the two igex-dm results and the lineage row on experiment:cosme.


## Checks run

- Validator: `python -m hepgraph.atlas.validate` ended `0 errors, 1677 warnings, 4 informational` (1596 warnings before this stream; the new ones are `experiment-without-active-beam`, `coordinate-kind-approximate` on the new approximate sites, `unknown-spec-key`, `hull-gap` and `experiment-before-facility`).
- Build: `python -m hepgraph.atlas.build` succeeded (81 bundle files; `atlas.json` about 1.39 MB against a 1.5 MB failure threshold: see "For the integrator"); `static/atlas/generated` was restored before committing.
- Tests: `pytest -q tests/test_atlas_*.py` (schema, validate, build, history, geo, tools, validation counts, pilot acceptance, geometry data): 338 passed, 1 skipped.
- Quote check (`scripts/atlas_quote_check.py` classifier over every file added or edited on this branch): 2029 quotes; 2020 verbatim, 3 verbatim by segments, 5 skipped (geocoder coordinate quotes), 1 unfetchable (a pre-existing `deap-3600` quote that the Atlas already lists as blocked, HTTP 403).
