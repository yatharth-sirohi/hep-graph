# colliders-2: storage-ring and e+e- colliders past, present and proposed

Owner tag `colliders-2`. Worktree `HEP-Graph-ar-c2-colliders`, branch `atlas-c2-colliders`, base `bb673ea`. Registry rows: `data/atlas/coverage/colliders-2.json`. Written 2026-10-26.

## Scope

Amendment A26 widens the Atlas to all ground-based high-energy physics. This stream covers colliders the Atlas lacked: the e+e- storage rings and their detectors at IHEP Beijing (BEPC, BEPCII), Cornell (CESR), DESY (DORIS, PETRA), SLAC (SPEAR, PEP), INFN-LNF Frascati (DAΦNE), BINP Novosibirsk (VEPP-2M, VEPP-2000, VEPP-4M) and KEK (TRISTAN); two SppS experiments at CERN (UA4, UA5); and the proposed colliders FCC-ee, CEPC, ILC and CLIC, each only where a design report or a lab page names a host.

Inclusion bar: a named experiment or collaboration; a fixed ground location; and published physics results, or approved and under construction, or (for proposed machines) a design report naming the host. Every record is tier C (accelerators) or D (experiments, detectors, collaborations, results, documents), `researched: partial`; nothing is tier A or B.

**No existing record was changed** (`git diff --name-status` against the base shows additions only). INSPIRE, Neon and Vercel were not touched; Greybook (CERN) was read for UA4 and UA5 dates only.

## Counts

| type | new records |
|---|---|
| facilities | 4 |
| sites | 5 |
| accelerators | 16 |
| experiments | 31 |
| detectors | 30 |
| collaborations | 29 |
| results | 26 |
| documents | 10 |
| sources | 127 |
| coverage rows | 31 |

Shared records: `collaboration:cmd` serves CMD-1, CMD-2 and CMD-3; `detector:kloe` serves KLOE and KLOE-2. Crystal Ball, PLUTO and Mark II are single experiments that moved between rings and carry several accelerators.

## Entities written

Every interval row gives the URL of the first cited source and the verbatim quote (or locator) behind that date. Dates marked `approximate`, `derived` or `uncertain` are listed again under "Unresolved". Detectors and collaborations repeat their experiment's dates unless stated.

### Facilities

#### facility:binp-novosibirsk: Budker Institute of Nuclear Physics (active, accelerator_laboratory)

Primary site `site:binp-novosibirsk-akademgorodok`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| institute established | 1958-05 | — | active | verified | https://inp.nsk.su/budker-institute-of-nuclear-physics “was established in accordance with the resolution of the Council of Ministers of the USSR in May 1958” |

#### facility:cornell-wilson-lab: Wilson Synchrotron Laboratory, Cornell University (active, accelerator_laboratory)

Primary site `site:cornell-wilson-lab`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| laboratory dedicated | 1968-10 | — | active | derived | https://www.classe.cornell.edu/NewsAndEvents/50YearsLaterOct18.html “This October marks the 50th anniversary of the dedication of the Wilson Synchrotron Laboratory.” |

#### facility:ihep-beijing: Institute of High Energy Physics, Chinese Academy of Sciences (active, accelerator_laboratory)

Primary site `site:ihep-beijing-campus`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| institute established | 1973-02 | — | active | verified | http://english.ihep.cas.cn/au/hy/ “officially established in February 1973” |

#### facility:infn-lnf-frascati: INFN Frascati National Laboratories (active, accelerator_laboratory)

Primary site `site:infn-lnf-frascati`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| laboratories established | 1955 | — | active | verified | https://www.infn.it/en/infn-offices/laboratories/ “Established in 1955, the National Laboratories of Frascati are the top Italian research facility for studying nuclear and subnuclear physics with accelerators.” |

### Sites

| site | facility | lat, lon | kind | precision | conf. | evidence (URL, quote or locator) |
|---|---|---|---|---|---|---|
| site:binp-novosibirsk-akademgorodok | facility:binp-novosibirsk | 54.8487459, 83.1110685 | campus | 300 m | approximate | https://nominatim.openstreetmap.org/search?q=Budker%20Institute%20of%20Nuclear%20Physics%20Novosibirsk&format=json&limit=5&addressdetails=0 “"lat":"54.8487459","lon":"83.1110685"” Nominatim (OpenStreetMap geocoder) centroid of the institute's office polygon at 11 Academician Lavrentiev Avenue, Akademgorodok, Novosibirsk. Campus-grade only: the VEPP-2M, VEPP-2000 and VEPP-4M rin |
| site:cornell-wilson-lab | facility:cornell-wilson-lab | 42.4449654, -76.4730508 | campus | 300 m | approximate | https://nominatim.openstreetmap.org/search?q=Wilson%20Synchrotron%20Laboratory%20Ithaca&format=json&limit=5&addressdetails=0 “"lat":"42.4449654","lon":"-76.4730508"” Nominatim (OpenStreetMap geocoder) centroid of the Wilson Synchrotron Laboratory building, Cornell campus, Ithaca. Campus-grade only: the CESR ring (a half-mile-scale tunnel beneath the Cornell athlet |
| site:ihep-beijing-campus | facility:ihep-beijing | 39.9095054, 116.2462488 | campus | 500 m | approximate | https://nominatim.openstreetmap.org/search?q=Institute%20of%20High%20Energy%20Physics%20Beijing&format=json&limit=5&addressdetails=0 “"lat":"39.9095054","lon":"116.2462488"” Nominatim (OpenStreetMap geocoder) point for the institute, 19B Yuquan Road, Shijingshan District, Beijing. A geocoder gives a campus-grade location only: read it as the campus marker, not the positio |
| site:infn-lnf-frascati | facility:infn-lnf-frascati | 41.8228768, 12.6732335 | campus | 500 m | approximate | https://nominatim.openstreetmap.org/search?q=Laboratori%20Nazionali%20di%20Frascati&format=json&limit=5&addressdetails=0 “"lat":"41.8228768","lon":"12.6732335"” Nominatim (OpenStreetMap geocoder) centroid of the LNF research-institute polygon, Via Enrico Fermi 54, Frascati. Campus-grade only: the DAΦNE rings and the KLOE hall are not individually located by a |
| site:kek-tsukuba-campus | facility:kek | 36.1516751, 140.0725669 | campus | 1000 m | approximate | https://nominatim.openstreetmap.org/search?q=%E9%AB%98%E3%82%A8%E3%83%8D%E3%83%AB%E3%82%AE%E3%83%BC%E5%8A%A0%E9%80%9F%E5%99%A8%E7%A0%94%E7%A9%B6%E6%A9%9F%E6%A7%8B&format=json&limit=5&addressdetails=0 “"lat":"36.1516751","lon":"140.0725669"” Nominatim (OpenStreetMap geocoder) centroid of the KEK campus polygon (OSM way 100702753, about 1.8 km across); campus-grade only. The 3 km TRISTAN ring and its four experimental halls are not individ |

### Accelerators

#### accelerator:bepc: Beijing Electron-Positron Collider (completed)

Facility `facility:ihep-beijing`, site `site:ihep-beijing-campus`, kind collider.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| approval | 1983-04 | 1984-10 | approved | verified | http://english.ihep.cas.cn/au/hy/ “In April 1983, the State Council officially approved the proposal to construct the Beijing Electron Positron Collider (BEPC), submitted by the State Planning Commission.” (IHEP history page (timeline)) |
| construction | 1984-10 | 1988-10-16 | construction | verified | http://english.ihep.cas.cn/au/hy/ “In October 1984, the groundbreaking ceremony for the BEPC project was held, with Deng Xiaoping and other Party and State leaders participating.” (IHEP history page (timeline); end = first collisions) |
| e+e- collider operation | 1988-10-16 | 2004 | active | approximate | http://english.ihep.cas.cn/au/hy/ (+1 more) “On October 16, 1988, the first electron-positron collisions took place at BEPC.” (IHEP history page (timeline); end year from Briere, Harris & Mitchell (2016), section 3) |
| original BEPC | 1988-10-16 | 1995 | active | approximate | https://arxiv.org/abs/1603.09431 “originally operated from 1988 until 1995; it was then upgraded, increasing the reliability of the machine and approximately doubling its luminosity.” (Briere, Harris & Mitchell (2016), section 3) |
| upgrade of BEPC (reliability and luminosity) | 1995 | 1998 | upgrade | approximate | https://arxiv.org/abs/1603.09431 “The upgraded BEPC ran from 1998-2004, when a major upgrade to BEPCII was started.” (Briere, Harris & Mitchell (2016), section 3) |
| upgraded BEPC | 1998 | 2004 | active | approximate | https://arxiv.org/abs/1603.09431 “The upgraded BEPC ran from 1998-2004, when a major upgrade to BEPCII was started.” (Briere, Harris & Mitchell (2016), section 3) |
| BEPC replaced by BEPCII upgrade | 2004 | — | completed | approximate | http://english.ihep.cas.cn/au/hy/ “In January 2004, the BEPC Upgrade Project kicked off.” (IHEP history page (timeline)) |


#### accelerator:bepcii: Beijing Electron-Positron Collider II (commissioning)

Facility `facility:ihep-beijing`, site `site:ihep-beijing-campus`, kind collider.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| approval of the BEPC Upgrade Project | 2003-12 | 2004-01 | approved | verified | http://english.ihep.cas.cn/au/hy/ “In December 2003, the National Development and Reform Commission officially approved the BEPC Upgrade Project.” (IHEP history page (timeline)) |
| construction | 2004-01 | 2008-07 | construction | verified | http://english.ihep.cas.cn/au/hy/ “In January 2004, the BEPC Upgrade Project kicked off.” (IHEP history page (timeline); end = first collisions in July 2008) |
| commissioning | 2008-07 | 2009-07 | commissioning | verified | http://english.ihep.cas.cn/au/hy/ “In July 2008, the first collisions took place at BEPCII, the upgraded BEPC, and were observed by the new BESIII detector.” (IHEP history page (timeline); end = acceptance test, July 2009) |
| e+e- collider operation | 2009-07 | 2024-07-01 | active | verified | http://english.ihep.cas.cn/au/hy/ (+1 more) “In July 2009, the Upgrade Project, BEPCII, successfully passed the National Acceptance Test organized by the National Development and Reform Commission” (IHEP history page (timeline); end from the IPAC'26 paper (shutdown of BEPCII on July 1st, 2024)) |
| BEPCII upgrade: hardware replacement | 2024-07-01 | 2025-05 | upgrade | approximate | https://indico.jacow.org/event/95/contributions/13014/attachments/1362/6693/WEP1606_edited_version.pdf “The upgrade of Beijing Electron and Positron Collider-II (BEPCII) has begun since the shutdown of BEPCII on July 1st in 2024.” (Geng et al., IPAC'26 WEP1606, abstract) |
| commissioning of the BEPCII upgrade | 2025-05 | — | commissioning | verified | https://indico.jacow.org/event/95/contributions/13014/attachments/1362/6693/WEP1606_edited_version.pdf “the machine commissioning of BEPCII Upgrade project has started since May 2025 after recovery from the cryogenic system fault.” (Geng et al., IPAC'26 WEP1606, abstract) |

- Note: The BEPCII-U target parameters (beam energy up to 2.8 GeV, luminosity gains) appear in the IPAC'26 paper tables; they are not recorded as specs because the paper is a preliminary proceedings file.

#### accelerator:cepc: Circular Electron Positron Collider (proposed)

Facility `facility:ihep-beijing`, site `site:ihep-beijing-campus`, kind collider.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| proposal and design studies | 2012-09 | — | proposed | verified | https://cerncourier.com/a/cepc-matures-but-approval-is-on-hold/ (+3 more) “Chinese physicists formally proposed a dedicated electron–positron collider in September 2012.” (CERN Courier, 26 October 2025) |

- Note: The Atlas marker is the IHEP Beijing campus, the laboratory that develops the project, not the tunnel site: the 2023 accelerator TDR describes "forthcoming engineering design phase and site selection procedures", so no tunnel site has been selected.
- Note: The accelerator TDR (December 2023) anticipated "Construction is anticipated to begin around 2027-2028, pending government approval, with an estimated duration of 8 years." That schedule is superseded by the October 2025 statement that CEPC will not be in the 2026-2030 plan; no replacement schedule is published in the sources consulted, so no construction interval is recorded.
- Note: Study leader Wang Yifang (CERN Courier, 26 October 2025): "We plan to submit CEPC for consideration again in 2030, unless FCC is officially approved before then, in which case we will seek to join FCC, and give up CEPC."

#### accelerator:cesr: Cornell Electron Storage Ring (completed)

Facility `facility:cornell-wilson-lab`, site `site:cornell-wilson-lab`, kind collider.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| proposal | 1975 | 1977 | proposed | verified | https://www.classe.cornell.edu/Research/CLEO/WebHome.html “1975: CESR propsal submitted to NSF” (CLASSE CLEO page, "CESR and CLEO Timelines") |
| NSF funding approved | 1977 | 1977 | approved | verified | https://www.classe.cornell.edu/Research/CLEO/WebHome.html “1977: NSF funding approved” (CLASSE CLEO page, "CESR and CLEO Timelines") |
| construction | 1977 | 1979-04 | construction | approximate | https://www.classe.cornell.edu/public/CLNS/2002/CLNS02-1784/history.pdf “3 Construction, 1977-79” (Berkelman, "A Personal History of CESR and CLEO", contents; first electrons injected in early April 1979) |
| commissioning | 1979-04 | 1979-08-14 | commissioning | approximate | https://www.classe.cornell.edu/public/CLNS/2002/CLNS02-1784/history.pdf “the first electrons were injected into CESR the next morning, on what would have been April 2 if we had not stopped the clock” (Berkelman, chapter 3 (Construction, 1977-79)) |
| e+e- collider operation | 1979-08-14 | 2008-03-03 | active | verified | https://www.classe.cornell.edu/public/CLNS/2002/CLNS02-1784/history.pdf (+1 more) “It was on August 14 that we had the first measurable colliding beam luminosity.” (Berkelman, chapter 3; end from the CLASSE CLEO timeline (2008: running ends on March 3rd)) |
| CESR-c (charm-region running) | 2003 | 2008-03-03 | active | approximate | https://www.classe.cornell.edu/Research/CLEO/WebHome.html “2003: CLEO-c data collection started” (CLASSE CLEO page timelines (CESR: 2003-04 superferric wigglers)) |
| CLEO running ended; CESR continues as a light source | 2008-03-03 | — | completed | verified | https://www.classe.cornell.edu/Research/CLEO/WebHome.html “2008: Running ends on March 3rd” (CLASSE CLEO page, "CESR and CLEO Timelines") |

- Note: CESR continues to operate after 2008 as a synchrotron-light and accelerator-physics facility; photon science is outside the Atlas scope (A26), so this record covers the collider period.

#### accelerator:clic: Compact Linear Collider (proposed)

Facility `facility:cern`, site `site:cern-meyrin`, kind collider.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| design phase | 2012-02 | — | proposed | approximate | https://arxiv.org/abs/1202.5940 (+2 more) “This report describes the physics potential and experiments at a future multi-TeV e+e- collider based on the Compact Linear Collider (CLIC) technology.” (CLIC Conceptual Design Report vol. 2, arXiv:1202.5940 (first posted 26 February 2012)) |

- Note: The Atlas marker is the CERN Meyrin campus, the host laboratory named by the design report; the CLIC site would be 11 to 50 km long depending on the stage and has no exact location in the sources consulted.
- Note: The CERN CLIC page says the collaboration comprises "more than 70 institutes in more than 30 countries".

#### accelerator:dafne: DAΦNE (active)

Facility `facility:infn-lnf-frascati`, site `site:infn-lnf-frascati`, kind collider.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| first beams and commissioning | 1997 | 1999 | commissioning | approximate | https://w3.lnf.infn.it/accelerators/dafne/?lang=en “The first particle beams started circulating in DAΦNE in 1997.” (INFN-LNF DAFNE page) |
| e+e- collider operation (phi factory) | 1999 | — | active | approximate | https://www.infn.it/en/infn-offices/laboratories/ “In 1999, DAFNE started operating.” (INFN, Laboratories page (Frascati)) |
| KLOE-2 run with crab-waist collisions | 2014-11 | 2018-03-30 | active | verified | https://cerncourier.com/a/kloe-2-completes-data-taking-at-frascati-collider/ “The implementation of this innovative configuration by the DAΦNE team allowed KLOE-2 to collect an integrated luminosity of 5.5 fb−1 in a period of just over three years.” (CERN Courier, 1 June 2018) |

- Note: KLOE start: CERN Courier says KLOE first collected data in 1999; the LNF particle-physics page says it took data from 2000 to 2006.

#### accelerator:doris: Doppel-Ring-Speicher (completed)

Facility `facility:desy`, site `site:desy-hamburg-campus`, kind collider.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| e+e- collider operation (DORIS, DORIS II, DORIS III) | 1974 | 1993 | active | approximate | https://doris.desy.de/history/index_eng.html “The storage ring DORIS is build as an electron-positron collider for high energy physics.” (DORIS history page, 1974 entry; end from the 1993 entry) |
| DORIS (two rings) | 1974 | 1982 | active | approximate | https://arxiv.org/abs/2405.03430 “Towards the end of 1974, the two detectors PLUTO and DASP were placed in their respective collision points.” (Ziemann, "German Beams", DORIS section) |
| DORIS II (single ring) | 1982 | 1991 | active | verified | https://arxiv.org/abs/2405.03430 “DORIS was upgraded in 1982 to reemerge as DORIS II” (Ziemann, DORIS section) |
| DORIS III (ARGUS running) | 1991 | 1993 | active | verified | https://doris.desy.de/history/index_eng.html “In the second straight the very successful ARGUS detector is operating until 1993 for high energy physics.” (DORIS history page, 1991 entry) |
| collider operation ended | 1993 | — | completed | approximate | https://doris.desy.de/history/index_eng.html “DORIS is running as a dedicated source for synchrotron radiation.” (DORIS history page, 1993 entry) |

- Note: End of collider running: the DESY DORIS page says ARGUS operated "until 1993"; other sources give end of data taking in 1992. The record follows the DESY page (1993) and marks it approximate.

#### accelerator:fcc-ee: Future Circular Collider (electron-positron stage, FCC-ee) (proposed)

Facility `facility:cern`, site `site:cern-meyrin`, kind collider.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| Feasibility Study | 2021 | 2025-03 | proposed | verified | https://home.cern/science/accelerators/future-circular-collider (+1 more) “In 2021, CERN’s Member and Associate Member States, including France and Switzerland, mandated the Feasibility Study.” (home.cern FCC page (FAQ); end from the CERN Council press release of 22 May 2026) |
| preparatory phase | 2026 | 2032 (planned) | proposed | verified | https://home.cern/science/accelerators/future-circular-collider “2026–2032 Preparatory phase Further, more in‑depth studies commissioned by the CERN Member States” (home.cern FCC page, "What is the project timeline?") |
| civil engineering (if approved) | 2033 (planned) | 2040 (planned) | planned | approximate | https://home.cern/science/accelerators/future-circular-collider “2033 to 2040 Civil engineering phase” (home.cern FCC page, "What is the project timeline?") |
| installation (if approved) | after 2038 (planned) | ~2045 (planned) | planned | approximate | https://home.cern/science/accelerators/future-circular-collider “After 2038 FCC installation phase After 2045 FCC commissioning and operation” (home.cern FCC page, "What is the project timeline?"; end = start of the next stage on the same list) |
| commissioning and operation (if approved) | after 2045 (planned) | — | planned | approximate | https://home.cern/science/accelerators/future-circular-collider “If approved, the FCC would come online around 2045.” (home.cern FCC page, "When will the FCC start operating?") |

- Note: The Atlas marker is the CERN Meyrin campus, the host laboratory; the proposed ring lies underground beneath CERN and the surrounding regions of France and Switzerland (CERN FCC page).
- Note: Status is "proposed": the CERN Council decision on whether to build is planned for 2028 (CERN, 22 May 2026: "the Council will be in a position, by 2028, to take a decision on the FCC-ee").
- Note: The FCC programme page also describes a possible later proton-proton stage (FCC-hh); only the electron-positron stage is recorded here.

#### accelerator:ilc: International Linear Collider (proposed)

Facility `facility:kek`, site `site:kek-tsukuba-campus`, kind collider.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| Technical Design Report published; no site selected | 2013-06 | — | proposed | verified | https://arxiv.org/abs/1306.6327 (+3 more) “For Asia, two possible ILC candidate sites have been identified: Kitakami in the Tohoku district in northern Japan; and Sefuri in the Kyushu district in the south.” (ILC TDR Volume 1 (Executive Summary), arXiv:1306.6327) |

- Note: The ILC has no site. The Atlas marker is the KEK Tsukuba campus only because an accelerator record needs a facility and a site: KEK hosts the linear-collider workshop LCWS2026 (ILC NewsLine, 17 September 2026). It is NOT a candidate site; the 2013 TDR names Kitakami (Tohoku district, northern Japan) and Sefuri (Kyushu district) as the two possible ILC candidate sites for Asia.
- Note: The two detector designs, ILD and SiD, are described in the TDR; they are not recorded as experiments because no host site has been named for them.
- Note: The ILC International Development Team was created by ICFA to prepare the ILC Pre-Lab (linearcollider.org); the page fetched does not date its creation.

#### accelerator:pep: Positron-Electron Project (completed)

Facility `facility:slac`, site `site:slac-menlo-park-campus`, kind collider.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| construction | 1977-06 | 1980 | construction | approximate | https://ahro.slac.stanford.edu/sites/default/files/2024-04/Hallonsten_SSRL_HSNS.pdf “In June 1977 SLAC had began constructing its next big HEP machine, the PEP (Positron-Electron Project)” (Hallonsten, Physics in Perspective) |
| e+e- collider operation | 1980 | 1990 | active | approximate | https://ahro.slac.stanford.edu/resources/slac-history/milestones (+1 more) “1980: PEP operations begin” (SLAC Milestones; CERN Courier "SLAC at 50": "ran during the years 1980–1990") |
| collider operation ended | 1990 | — | completed | approximate | https://cerncourier.com/a/slac-at-50-honouring-the-past-and-creating-the-future/ “ran during the years 1980–1990” (CERN Courier, "SLAC at 50") |

- Note: The ring and its interaction regions are on the SLAC campus; the PEP site marker is the SLAC campus point. The existing PEP-II record places PEP-II at the IR-2 hall (site:slac-pep-ii-ir2-babar).

#### accelerator:petra: Positron-Electron Tandem Ring Accelerator (completed)

Facility `facility:desy`, site `site:desy-hamburg-campus`, kind collider.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| proposal | 1974-09 | 1975 | proposed | verified | https://arxiv.org/abs/2208.11076 “proposal for an e+ e− storage ring of 2304 m circumference” (Table 1, Timeline of the e+ e− storage ring PETRA) |
| approval | 1975 | 1976 | approved | verified | https://arxiv.org/abs/2208.11076 “approval by federal government” (Table 1 (1975, Fall)) |
| construction | 1976 | 1978-07 | construction | verified | https://arxiv.org/abs/2208.11076 “start of PETRA construction” (Table 1 (1976, Spring); end = July 1978 completion) |
| commissioning | 1978-07 | 1978-09 | commissioning | verified | https://arxiv.org/abs/2208.11076 “early completion of PETRA, start of operation” (Table 1 (1978, July)) |
| e+e- collider operation | 1978-09 | 1986-11-03 | active | verified | https://arxiv.org/abs/2208.11076 “first e+ e− collisions” (Table 1 (1978, September); end from the 1986 November 3 row "final shutdown of PETRA and experiments") |
| final shutdown as a collider | 1986-11-03 | — | completed | verified | https://arxiv.org/abs/2208.11076 “final shutdown of PETRA and experiments” (Table 1 (1986, November 3)) |

- Note: The DESY anniversary page says PETRA served as pre-accelerator for HERA "starting in 1986"; Bethke & Wagner (Eur. Phys. J. H 2022) say PETRA "came back to life in 1990 as PETRA-II" after the November 1986 shutdown. The record follows the latter for the collider/pre-accelerator distinction and only models the collider period.
- Note: PETRA II (HERA pre-accelerator) and PETRA III (synchrotron-radiation source) are not separate records here; photon science is outside the Atlas scope (A26).

#### accelerator:spear: Stanford Positron Electron Asymmetric Ring (completed)

Facility `facility:slac`, site `site:slac-menlo-park-campus`, kind collider.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| proposal | 1964 | 1970 | proposed | verified | https://cerncourier.com/a/the-ring-on-the-parking-lot/ “first proposed building the Stanford Positron-Electron Asymmetric Rings (SPEAR) in 1964” (CERN Courier, "The ring on the parking lot") |
| construction | 1970 | 1972 | construction | approximate | https://cerncourier.com/a/the-ring-on-the-parking-lot/ “In 1972, only 20 months after its construction had finally been agreed, the SPEAR electron-positron collider went into service” (CERN Courier, "The ring on the parking lot") |
| e+e- collider operation | 1972 | 1990 | active | verified | https://ahro.slac.stanford.edu/resources/slac-history/milestones “1972: SPEAR operations begin” (SLAC Milestones; end from the 1990 entry) |
| dedicated synchrotron-radiation facility; collider operation ended | 1990 | — | completed | verified | https://ahro.slac.stanford.edu/resources/slac-history/milestones “1990: SPEAR becomes a dedicated synchrotron radiation facility with its own independent injector.” (SLAC Milestones, 1990 entry) |

- Note: SSRL describes the tau as "discovered at SPEAR in 1976"; the discovery paper (Mark I, Phys. Rev. Lett. 35, 1489) is dated December 1975, the date used on the result record.
- Note: The ring and its detectors are on the SLAC campus; the SPEAR site marker is the SLAC campus point, not the ring.

#### accelerator:tristan: Tri Ring Intersecting STorage Accelerators in Nippon (completed)

Facility `facility:kek`, site `site:kek-tsukuba-campus`, kind collider.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| approval (phase 1, e+e- collider) | 1981-04 | 1981-11 | approved | verified | https://research.kek.jp/people/kondo/4thHistoryParticlePhysics/TristanKEKB_v0.pdf “The phase-1 TRISATN project was approved by the Japanese Government on April 1981 as a five year project.” (Kondo, "The TRISTAN and KEKB Colliders", section 1) |
| construction | 1981-11 | 1986-11-14 | construction | verified | https://research.kek.jp/people/kondo/4thHistoryParticlePhysics/TristanKEKB_v0.pdf “Groundbreaking Ceremony of TRISTAN on Nov. 1981” (Kondo, section 1 (Figure 1 caption); end = first e+e- collisions on 14 November 1986) |
| commissioning | 1986-11-14 | 1987-05 | commissioning | verified | https://research.kek.jp/people/kondo/4thHistoryParticlePhysics/TristanKEKB_v0.pdf (+1 more) “On November 14, 1986, just five year since the groundbreaking ceremony, TRISTAN achieved e+ e− collisions at the world’s highest centerof-mass energy of 50 GeV” (Kondo, section 1; KEK history page (1987 May: TRISTAN experiments began)) |
| e+e- collider operation | 1987-05 | 1995-12 | active | verified | https://www.kek.jp/en/about/history/ “1987 May：TRISTAN experiments began.” (KEK history page; end from the 1995 Dec entry) |
| TRISTAN experiments finished | 1995-12 | — | completed | verified | https://www.kek.jp/en/about/history/ “1995 Dec：TRISTAN experiments finished.” (KEK history page) |

- Note: Kondo gives "operation 1986-1995" and "data taking 1987-1995"; the KEK history page gives experiments May 1987 to December 1995. The record uses the KEK history page for the operating interval and the 14 November 1986 date for the first collisions.
- Note: The original design (1973) was a three-ring electron-proton facility; only the electron-positron main ring was built in phase 1 (Kondo).

#### accelerator:vepp-2000: VEPP-2000 (active)

Facility `facility:binp-novosibirsk`, site `site:binp-novosibirsk-akademgorodok`, kind collider.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| upgrade decision and construction | 2000 | 2007 | construction | approximate | https://vepp2k.inp.nsk.su/sites/default/files/First_VEPP-2000_en.pdf “In 2007, at the Institute of Nuclear Physics (Novosibirsk), the construction of the VEPP-2000 electron–positron collider was completed.” (Berkaev et al., JETP 113 (2011) 213, abstract; the introduction records the spring 2000 decision to modernise VEPP-2M) |
| commissioning and first experiments | 2007 | 2010 | commissioning | approximate | https://vepp2k.inp.nsk.su/sites/default/files/First_VEPP-2000_en.pdf “In October 2009, a CMD-3 (cryogenic magnetic detector) was installed at the VEPP-2000 facility, and the physics program with both the SND and CMD-3 particle detectors was started in the energy range of 1–1.9 GeV.” (Berkaev et al., JETP 113 (2011) 213, abstract) |
| e+e- collider operation | 2010 | — | active | approximate | https://vepp2k.inp.nsk.su/en/node/85 (+1 more) “VEPP-2000 e+e− collider at BINP was commissioned and started data taking with two detectors in 2010 with old injection chain.” (Shatunov et al., IPAC-2017 abstract (start); Solodov, Phi to Psi 2026 (still collecting data: "2025 data were collected with the reverse direction of the beams") |
| upgraded injection complex | 2013 | 2016 | upgrade | approximate | https://vepp2k.inp.nsk.su/en/node/85 (+1 more) “The injection chain was significantly upgraded in 2013-2016.” (Shatunov et al., IPAC-2017 abstract) |

- Note: The VEPP-2000 status page (vepp2k.inp.nsk.su/status) read zero beam currents on 23 October 2026; this is a snapshot of the control-system display, not evidence that the collider is decommissioned, and the record follows the 2026 CMD-3 statement that running continues in 2024-2026.

#### accelerator:vepp-2m: VEPP-2M (completed)

Facility `facility:binp-novosibirsk`, site `site:binp-novosibirsk-akademgorodok`, kind collider.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| e+e- collider operation | 1975 | 2000 | active | approximate | https://epaper.kek.jp/p95/ARTICLES/MAD/MAD04.PDF (+1 more) “started to operate for experiments at 1975” (Skrinsky (PAC 1995), section 1.3 (start); Silagadze essay on the SND site (end: "After 2000, it was upgraded to the VEPP-2000")) |
| upgraded to VEPP-2000 | 2000 | — | completed | approximate | https://wwwsnd.inp.nsk.su/SND_General/SND_experiment.pdf “After 2000, it was upgraded to the VEPP-2000 collider with an increased center-of-mass energy (up to 2 GeV).” (Silagadze, essay on the SND site, section I) |

- Note: The brief names VEPP-2000 and VEPP-4M; VEPP-2M is an addition because CMD-2 and SND ran on it.
- Note: Start-date conflict: Skrinsky (1995) "started to operate for experiments at 1975"; Berkaev et al. (2011) "Since 1974"; Shatunov (2018) "VEPP-2M (1972-2000)". The record follows Skrinsky (experiments) and notes the others.

#### accelerator:vepp-4m: VEPP-4M (active)

Facility `facility:binp-novosibirsk`, site `site:binp-novosibirsk-akademgorodok`, kind collider.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| e+e- collider operation (VEPP-4 and VEPP-4M) | 1980 | — | active | approximate | https://epaper.kek.jp/p95/ARTICLES/MAD/MAD04.PDF (+1 more) “Since 1980 the higher energy e+e- collider VEPP-4 is in operation at Novosibirsk” (Skrinsky (PAC 1995), section 1.5; the KEDR home page records KEDR experiments at VEPP-4M since 2002) |

- Note: The VEPP-4 to VEPP-4M upgrade date is not stated in the sources fetched; the record starts at the VEPP-4 start (1980).

### Experiments, detectors and collaborations

#### experiment:amy: AMY (completed)

Facility `facility:kek`; accelerators `accelerator:tristan`; detector `detector:amy`; collaboration `collaboration:amy`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| TRISTAN data taking | 1987-05 | 1995-12 | active | approximate | https://www.kek.jp/en/about/history/ “1987 May：TRISTAN experiments began.” (KEK history page; end from the 1995 Dec entry ("TRISTAN experiments finished")) |
| TRISTAN experiments finished | 1995-12 | — | completed | approximate | https://www.kek.jp/en/about/history/ “1995 Dec：TRISTAN experiments finished.” (KEK history page) |

- `detector:amy` (completed): placement `site:kek-tsukuba-campus` 1987-05 to 1995-12; intervals identical to the experiment.
- `collaboration:amy` (completed): host `facility:kek`; formation —; intervals identical to the experiment.
- Note: No AMY website was found; no URL recorded. Approval and construction dates are not given in the sources fetched.

#### experiment:argus: ARGUS (completed)

Facility `facility:desy`; accelerators `accelerator:doris`; detector `detector:argus`; collaboration `collaboration:argus`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| DORIS II data taking | 1982 | 1993 | active | approximate | https://arxiv.org/abs/2405.03430 (+1 more) “The higher energies of 5.6 GeV per beam allowed the two new detectors, ARGUS and Crystal Ball, to investigate pairs of B-mesons” (Ziemann, German Beams, DORIS section; end from DESY DORIS history page (1991 entry)) |
| ARGUS ended at DORIS | 1993 | — | completed | approximate | https://doris.desy.de/history/index_eng.html “In the second straight the very successful ARGUS detector is operating until 1993 for high energy physics.” (DESY DORIS history page, 1991 entry) |

- `detector:argus` (completed): placement `site:desy-hamburg-campus` 1982 to 1993; intervals identical to the experiment.
- `collaboration:argus` (completed): host `facility:desy`; formation —; intervals identical to the experiment.
- Note: The ARGUS-Fest web pages (argus-fest.desy.de) did not respond; no ARGUS website is recorded.

#### experiment:bes: BES (completed)

Facility `facility:ihep-beijing`; accelerators `accelerator:bepc`; detector `detector:bes`; collaboration `collaboration:bes`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| BEPC data taking (BESI) | 1989 | 1995 | active | approximate | https://arxiv.org/abs/1603.09431 “BESI operated from 1989 until 1995, when it was upgraded to BESII, and BEPC was also upgraded.” (Briere, Harris & Mitchell (2016), section 3) |
| upgraded to BESII | 1995 | — | completed | approximate | https://arxiv.org/abs/1603.09431 “BESI operated from 1989 until 1995, when it was upgraded to BESII, and BEPC was also upgraded.” (Briere, Harris & Mitchell (2016), section 3) |

- `detector:bes` (completed): placement `site:ihep-beijing-campus` 1989 to 1995; intervals identical to the experiment.
- `collaboration:bes` (completed): host `facility:ihep-beijing`; formation —; intervals identical to the experiment.
- Note: No BESI website exists; no URL is recorded.

#### experiment:bes-ii: BES-II (completed)

Facility `facility:ihep-beijing`; accelerators `accelerator:bepc`; detector `detector:bes-ii`; collaboration `collaboration:bes-ii`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| upgrade of BESI to BESII | 1995 | 1998 | construction | approximate | https://arxiv.org/abs/1603.09431 “BESI operated from 1989 until 1995, when it was upgraded to BESII, and BEPC was also upgraded.” (Briere, Harris & Mitchell (2016), section 3) |
| BEPC data taking (BESII) | 1998 | 2004 | active | approximate | https://arxiv.org/abs/1603.09431 “BESII operated from 1998 until 2004.” (Briere, Harris & Mitchell (2016), section 3) |
| ended with the BEPCII upgrade | 2004 | — | completed | approximate | https://arxiv.org/abs/1603.09431 “The upgraded BEPC ran from 1998-2004, when a major upgrade to BEPCII was started.” (Briere, Harris & Mitchell (2016), section 3) |

- `detector:bes-ii` (completed): placement `site:ihep-beijing-campus` 1998 to 2004; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| BEPC data taking (BESII) | 1998 | 2004 | active | approximate | https://arxiv.org/abs/1603.09431 “BESII operated from 1998 until 2004.” (Briere, Harris & Mitchell (2016), section 3) |
| ended with the BEPCII upgrade | 2004 | — | completed | approximate | https://arxiv.org/abs/1603.09431 “The upgraded BEPC ran from 1998-2004, when a major upgrade to BEPCII was started.” (Briere, Harris & Mitchell (2016), section 3) |

- `collaboration:bes-ii` (completed): host `facility:ihep-beijing`; formation —; intervals differ from the experiment (shared record).
- Note: No BESII website exists; no URL is recorded.

#### experiment:bes-iii: BES-III (shutdown)

Facility `facility:ihep-beijing`; accelerators `accelerator:bepcii`; detector `detector:bes-iii`; collaboration `collaboration:bes-iii`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| approval of the BEPC Upgrade Project | 2003-12 | 2004-01 | approved | verified | http://english.ihep.cas.cn/au/hy/ “In December 2003, the National Development and Reform Commission officially approved the BEPC Upgrade Project.” (IHEP history page (timeline)) |
| construction | 2004-01 | 2008-07 | construction | verified | http://english.ihep.cas.cn/au/hy/ “In January 2004, the BEPC Upgrade Project kicked off.” (IHEP history page (timeline)) |
| commissioning with the first BEPCII collisions | 2008-07 | 2009-07 | commissioning | verified | http://english.ihep.cas.cn/au/hy/ “In July 2008, the first collisions took place at BEPCII, the upgraded BEPC, and were observed by the new BESIII detector.” (IHEP history page (timeline); end = BEPCII acceptance test, July 2009) |
| BEPCII data taking | 2009-07 | 2024-07-01 | active | approximate | http://english.ihep.cas.cn/au/hy/ (+1 more) “In July 2009, the Upgrade Project, BEPCII, successfully passed the National Acceptance Test organized by the National Development and Reform Commission” (IHEP history page (timeline); end from the IPAC'26 paper (BEPCII shut down on 1 July 2024)) |
| BEPCII upgrade shutdown | 2024-07-01 | — | shutdown | approximate | https://indico.jacow.org/event/95/contributions/13014/attachments/1362/6693/WEP1606_edited_version.pdf “The upgrade of Beijing Electron and Positron Collider-II (BEPCII) has begun since the shutdown of BEPCII on July 1st in 2024.” (Geng et al., IPAC'26 WEP1606, abstract) |

- `detector:bes-iii` (shutdown): placement `site:ihep-beijing-campus` 2008-07 to —; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| commissioning with the first BEPCII collisions | 2008-07 | 2009-07 | commissioning | verified | http://english.ihep.cas.cn/au/hy/ “In July 2008, the first collisions took place at BEPCII, the upgraded BEPC, and were observed by the new BESIII detector.” (IHEP history page (timeline); end = BEPCII acceptance test, July 2009) |
| BEPCII data taking | 2009-07 | 2024-07-01 | active | approximate | http://english.ihep.cas.cn/au/hy/ (+1 more) “In July 2009, the Upgrade Project, BEPCII, successfully passed the National Acceptance Test organized by the National Development and Reform Commission” (IHEP history page (timeline); end from the IPAC'26 paper (BEPCII shut down on 1 July 2024)) |
| BEPCII upgrade shutdown | 2024-07-01 | — | shutdown | approximate | https://indico.jacow.org/event/95/contributions/13014/attachments/1362/6693/WEP1606_edited_version.pdf “The upgrade of Beijing Electron and Positron Collider-II (BEPCII) has begun since the shutdown of BEPCII on July 1st in 2024.” (Geng et al., IPAC'26 WEP1606, abstract) |

- `collaboration:bes-iii` (shutdown): host `facility:ihep-beijing`; formation —; intervals differ from the experiment (shared record).

#### experiment:cello: CELLO (completed)

Facility `facility:desy`; accelerators `accelerator:petra`; detector `detector:cello`; collaboration `collaboration:cello`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| proposal recommended for approval | 1976-10 | 1980-03 | proposed | verified | https://arxiv.org/abs/2208.11076 “October: 5 proposals recommended for approval (CELLO, JADE, Mark-J, PLUTO, TASSO)” (Bethke & Wagner (2022), Table 1 (1976, October)) |
| PETRA data taking | 1980-03 | 1986-11-03 | active | verified | https://arxiv.org/abs/2208.11076 “PLUTO had already operated [32] at the precursor storage ring DORIS, and was replaced at PETRA in March 1980 by the newly built CELLO detector [33].” (Bethke & Wagner (2022), section 2; end from Table 1 (1986, November 3)) |
| PETRA shut down; experiment ended | 1986-11-03 | — | completed | verified | https://arxiv.org/abs/2208.11076 “final shutdown of PETRA and experiments” (Bethke & Wagner (2022), Table 1 (1986, November 3)) |

- `detector:cello` (completed): placement `site:desy-hamburg-campus` 1980-03 to 1986-11-03; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| PETRA data taking | 1980-03 | 1986-11-03 | active | verified | https://arxiv.org/abs/2208.11076 “PLUTO had already operated [32] at the precursor storage ring DORIS, and was replaced at PETRA in March 1980 by the newly built CELLO detector [33].” (Bethke & Wagner (2022), section 2; end from Table 1 (1986, November 3)) |
| PETRA shut down; experiment ended | 1986-11-03 | — | completed | verified | https://arxiv.org/abs/2208.11076 “final shutdown of PETRA and experiments” (Bethke & Wagner (2022), Table 1 (1986, November 3)) |

- `collaboration:cello` (completed): host `facility:desy`; formation —; intervals differ from the experiment (shared record).
- Note: No CELLO website was found; no URL is recorded.

#### experiment:cleo: CLEO (completed)

Facility `facility:cornell-wilson-lab`; accelerators `accelerator:cesr`; detector `detector:cleo`; collaboration `collaboration:cleo`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| conception of the South Area Experiment | 1975 | 1977 | proposed | approximate | https://www.classe.cornell.edu/Research/CLEO/WebHome.html “1975: "South Area Experiment" group conceives CLEO” (CLASSE CLEO page, "CESR and CLEO Timelines") |
| construction | 1977 | 1979-10 | construction | approximate | https://www.classe.cornell.edu/public/CLNS/2002/CLNS02-1784/history.pdf “3 Construction, 1977-79” (Berkelman, contents; first CLEO run scheduled for October 1979) |
| CESR data taking (CLEO) | 1979-10 | 2008-03-03 | active | verified | https://www.classe.cornell.edu/public/CLNS/2002/CLNS02-1784/history.pdf (+1 more) “By October the luminosity was enough to schedule the first experimental run of the CLEO detector.” (Berkelman, chapter 3 (October 1979); CLASSE CLEO page ("from 1979 to 2008"; "2008: Running ends on March 3rd")) |
| CLEO-1 | 1979-10 | 1984 | active | derived | https://www.classe.cornell.edu/public/CLNS/2002/CLNS02-1784/history.pdf “By October the luminosity was enough to schedule the first experimental run of the CLEO detector.” (Berkelman, chapter 3; the CLEO-1.5 upgrade period begins in 1984) |
| CLEO-1.5 | 1984 | 1989 | active | approximate | https://www.classe.cornell.edu/public/CLNS/2002/CLNS02-1784/history.pdf “8 The First Upgrade, CLEO-1.5, 1984-89” (Berkelman, contents) |
| CLEO-2 | 1989 | 1995 | active | approximate | https://www.classe.cornell.edu/public/CLNS/2002/CLNS02-1784/history.pdf “10 The CLEO-2 Years, 1989-95” (Berkelman, contents) |
| CLEO-2.5 (CLEO II.V) | 1995 | 1999 | active | approximate | https://www.classe.cornell.edu/Research/CLEO/WebHome.html (+1 more) “1995: CLEO II.V with silicon vertex detector installed” (CLASSE CLEO page timeline; Berkelman chapter "The CLEO-2.5 Years 1995-1999") |
| CLEO-3 | 1999 | 2003 | active | approximate | https://www.classe.cornell.edu/Research/CLEO/WebHome.html “1999: CLEO III with RICH installed” (CLASSE CLEO page timeline) |
| CLEO-c | 2003 | 2008-03-03 | active | approximate | https://www.classe.cornell.edu/Research/CLEO/WebHome.html “2003: CLEO-c data collection started” (CLASSE CLEO page timeline) |
| CLEO running ended | 2008-03-03 | — | completed | verified | https://www.classe.cornell.edu/Research/CLEO/WebHome.html “2008: Running ends on March 3rd” (CLASSE CLEO page, "CESR and CLEO Timelines") |

- `detector:cleo` (completed): placement `site:cornell-wilson-lab` 1979-10 to 2008-03-03; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| CESR data taking (CLEO) | 1979-10 | 2008-03-03 | active | verified | https://www.classe.cornell.edu/public/CLNS/2002/CLNS02-1784/history.pdf (+1 more) “By October the luminosity was enough to schedule the first experimental run of the CLEO detector.” (Berkelman, chapter 3 (October 1979); CLASSE CLEO page ("from 1979 to 2008"; "2008: Running ends on March 3rd")) |
| CLEO running ended | 2008-03-03 | — | completed | verified | https://www.classe.cornell.edu/Research/CLEO/WebHome.html “2008: Running ends on March 3rd” (CLASSE CLEO page, "CESR and CLEO Timelines") |

- `collaboration:cleo` (completed): host `facility:cornell-wilson-lab`; formation 1975; intervals differ from the experiment (shared record).
- Note: The CLEO detector description is deliberately generic: detailed components per phase are in Berkelman and the CLEO II detector paper.

#### experiment:cmd-1: CMD-1 (completed)

Facility `facility:binp-novosibirsk`; accelerators `accelerator:vepp-2m`; detector `detector:cmd-1`; collaboration `collaboration:cmd`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| VEPP-2M data taking (CMD-1) | 1979 | 1984 | active | approximate | https://cmd.inp.nsk.su/?cmdc_history “1979 - 1984 Experiments with the CMD-1 detector at VEPP-2 collider” (CMD Collaboration web site, Collaboration History) |
| CMD-1 experiments ended | 1984 | — | completed | approximate | https://cmd.inp.nsk.su/?cmdc_history “1984 - 1992 Commissioning of the CMD-2 detector at VEPP-2M collider” (CMD Collaboration web site, Collaboration History) |

- `detector:cmd-1` (completed): placement `site:binp-novosibirsk-akademgorodok` 1979 to 1984; intervals identical to the experiment.
- `collaboration:cmd` (completed): host `facility:binp-novosibirsk`; formation 1979; intervals identical to the experiment.
- Note: CMD-1 is an addition to the brief; the CMD collaboration site dates it. The one-line history gives no physics results, so the record rests on the collaboration page only.

#### experiment:cmd-2: CMD-2 (completed)

Facility `facility:binp-novosibirsk`; accelerators `accelerator:vepp-2m`; detector `detector:cmd-2`; collaboration `collaboration:cmd`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| commissioning of CMD-2 | 1984 | 1992 | construction | approximate | https://cmd.inp.nsk.su/?cmdc_history “1984 - 1992 Commissioning of the CMD-2 detector at VEPP-2M collider” (CMD Collaboration web site, Collaboration History) |
| VEPP-2M data taking (CMD-2) | 1992 | 2000 | active | approximate | https://cmd.inp.nsk.su/?cmdc_history (+1 more) “1992 - 2000 Experiments with the CMD-2 detector at VEPP-2M collider” (CMD Collaboration web site, Collaboration History and CMD-2 Detector History) |
| CMD-2 experiments ended | 2000 | — | completed | approximate | https://cmd.inp.nsk.su/?cmdc_history “2000 - present Commissioning of the CMD-3 detector at VEPP-2000 collider” (CMD Collaboration web site, Collaboration History) |

- `detector:cmd-2` (completed): placement `site:binp-novosibirsk-akademgorodok` 1992 to 2000; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| VEPP-2M data taking (CMD-2) | 1992 | 2000 | active | approximate | https://cmd.inp.nsk.su/?cmdc_history (+1 more) “1992 - 2000 Experiments with the CMD-2 detector at VEPP-2M collider” (CMD Collaboration web site, Collaboration History and CMD-2 Detector History) |
| CMD-2 experiments ended | 2000 | — | completed | approximate | https://cmd.inp.nsk.su/?cmdc_history “2000 - present Commissioning of the CMD-3 detector at VEPP-2000 collider” (CMD Collaboration web site, Collaboration History) |

- `collaboration:cmd` (completed): host `facility:binp-novosibirsk`; formation 1979; intervals differ from the experiment (shared record).
- Note: CMD-2 shares the CMD collaboration record (collaboration:cmd, created with CMD-1). No technical description of the CMD-2 detector was retrieved.

#### experiment:cmd-3: CMD-3 (active)

Facility `facility:binp-novosibirsk`; accelerators `accelerator:vepp-2000`; detector `detector:cmd-3`; collaboration `collaboration:cmd`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| design, prototyping and commissioning | 2000 | 2009-10 | construction | approximate | https://cmd.inp.nsk.su/?cmd3_history “CMD-3 detector components are being designed, prototyped and commitioned at BINP.” (CMD Collaboration web site, CMD-3 Detector History and Status) |
| installation and first experimental season | 2009-10 | 2010 | commissioning | approximate | https://vepp2k.inp.nsk.su/sites/default/files/First_VEPP-2000_en.pdf “In October 2009, a CMD-3 (cryogenic magnetic detector) was installed at the VEPP-2000 facility, and the physics program with both the SND and CMD-3 particle detectors was started in the energy range of 1–1.9 GeV.” (Berkaev et al., JETP 113 (2011) 213, abstract) |
| VEPP-2000 data taking | 2010 | — | active | approximate | https://vepp2k.inp.nsk.su/en/node/85 (+1 more) “VEPP-2000 e+e− collider at BINP was commissioned and started data taking with two detectors in 2010 with old injection chain.” (Shatunov et al., IPAC-2017 abstract (two detectors, 2010); Solodov, Phi to Psi 2026 (1 fb^-1 collected; more data to be collected in 2024-2026)) |

- `detector:cmd-3` (active): placement `site:binp-novosibirsk-akademgorodok` 2009-10 to —; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| installation and first experimental season | 2009-10 | 2010 | commissioning | approximate | https://vepp2k.inp.nsk.su/sites/default/files/First_VEPP-2000_en.pdf “In October 2009, a CMD-3 (cryogenic magnetic detector) was installed at the VEPP-2000 facility, and the physics program with both the SND and CMD-3 particle detectors was started in the energy range of 1–1.9 GeV.” (Berkaev et al., JETP 113 (2011) 213, abstract) |
| VEPP-2000 data taking | 2010 | — | active | approximate | https://vepp2k.inp.nsk.su/en/node/85 (+1 more) “VEPP-2000 e+e− collider at BINP was commissioned and started data taking with two detectors in 2010 with old injection chain.” (Shatunov et al., IPAC-2017 abstract (two detectors, 2010); Solodov, Phi to Psi 2026 (1 fb^-1 collected; more data to be collected in 2024-2026)) |

- `collaboration:cmd` (completed): host `facility:binp-novosibirsk`; formation 1979; intervals differ from the experiment (shared record).
- Note: CMD-3 shares the CMD collaboration record.

#### experiment:crystal-ball: Crystal Ball (completed)

Facility `facility:slac`; accelerators `accelerator:spear`, `accelerator:doris`; detector `detector:crystal-ball`; collaboration `collaboration:crystal-ball`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| approval (SLAC-SP-024) | 1975 | 1979 | approved | approximate | https://history.aip.org/catalog/icos/5291.html “The experiment was approved in 1975 and completed running in 1979.” (AIP Study of Multi-Institutional Collaborations, SLAC-SP-024) |
| SPEAR and DORIS II running | 1979 | 1987 | active | derived | https://arxiv.org/abs/nucl-ex/0302017 “It was built at SLAC and used for meson spectroscopy measurements there for three years. It was then used at DESY for five years of experiments and put in storage at SLAC from 1987 until 1996 when it was moved to BNL by our collaboration.” (Crystal Ball Collaboration, arXiv:nucl-ex/0302017 (detector description)) |
| SPEAR phase | 1979 | 1982 | active | derived | https://arxiv.org/abs/nucl-ex/0302017 “It was built at SLAC and used for meson spectroscopy measurements there for three years.” (arXiv:nucl-ex/0302017) |
| DORIS II phase | 1982 | 1987 | active | derived | https://arxiv.org/abs/2405.03430 (+1 more) “DORIS was upgraded in 1982 to reemerge as DORIS II” (Ziemann, German Beams, DORIS section (higher energies allowed ARGUS and Crystal Ball); arXiv:nucl-ex/0302017 (five years at DESY, storage from 1987)) |
| removed from DESY; stored at SLAC | 1987 | — | completed | approximate | https://arxiv.org/abs/nucl-ex/0302017 “put in storage at SLAC from 1987 until 1996 when it was moved to BNL by our collaboration” (arXiv:nucl-ex/0302017) |

- `detector:crystal-ball` (completed): placement `site:slac-menlo-park-campus` 1979 to 1982; `site:desy-hamburg-campus` 1982 to 1987; `site:slac-menlo-park-campus` 1987 to 1996; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| SPEAR and DORIS II running | 1979 | 1987 | active | derived | https://arxiv.org/abs/nucl-ex/0302017 “It was built at SLAC and used for meson spectroscopy measurements there for three years. It was then used at DESY for five years of experiments and put in storage at SLAC from 1987 until 1996 when it was moved to BNL by our collaboration.” (Crystal Ball Collaboration, arXiv:nucl-ex/0302017 (detector description)) |
| removed from DESY; stored at SLAC | 1987 | — | completed | approximate | https://arxiv.org/abs/nucl-ex/0302017 “put in storage at SLAC from 1987 until 1996 when it was moved to BNL by our collaboration” (arXiv:nucl-ex/0302017) |

- `collaboration:crystal-ball` (completed): host `facility:slac`; formation 1975; intervals differ from the experiment (shared record).
- Note: Placements and run periods at SPEAR and DORIS II are derived from "three years" and "five years" statements (see the interval notes); AIP says the SPEAR experiment "completed running in 1979", which contradicts this and is recorded as a conflict in the log.
- Note: The detector later ran at the Brookhaven AGS and at the Mainz MAMI accelerator; those hadron-physics programmes are not part of this record.

#### experiment:cusb: CUSB (completed)

Facility `facility:cornell-wilson-lab`; accelerators `accelerator:cesr`; detector `detector:cusb`; collaboration `collaboration:cusb`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| selected by the CESR Program Advisory Committee | 1978-02-15 | 1979 | approved | verified | https://www.classe.cornell.edu/public/CLNS/2002/CLNS02-1784/history.pdf “The winning entry was the sodium iodide and lead-glass array proposed by the group from Columbia and Stony Brook with Leon Lederman as spokesman.” (Berkelman, chapter 2 (CLEO Prehistory, 1975-77): the PAC met on February 15, 1978) |
| CESR data taking (north area) | 1979-08 | 1990 | active | derived | https://www.classe.cornell.edu/public/CLNS/2002/CLNS02-1784/history.pdf “CUSB under the leadership of the Franzinis had run in the north interaction region for eleven years” (Berkelman, chapter 10 (The CLEO-2 Years); "since the turn-on of CESR in 1979" (chapter 5)) |
| CUSB terminated | 1990 | — | completed | derived | https://www.classe.cornell.edu/public/CLNS/2002/CLNS02-1784/history.pdf “Upon the advice of the PAC I decided to terminate the CUSB experiment after one more run on the Υ(4S).” (Berkelman, chapter 10) |

- `detector:cusb` (completed): placement `site:cornell-wilson-lab` 1979-08 to 1990; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| CESR data taking (north area) | 1979-08 | 1990 | active | derived | https://www.classe.cornell.edu/public/CLNS/2002/CLNS02-1784/history.pdf “CUSB under the leadership of the Franzinis had run in the north interaction region for eleven years” (Berkelman, chapter 10 (The CLEO-2 Years); "since the turn-on of CESR in 1979" (chapter 5)) |
| CUSB terminated | 1990 | — | completed | derived | https://www.classe.cornell.edu/public/CLNS/2002/CLNS02-1784/history.pdf “Upon the advice of the PAC I decided to terminate the CUSB experiment after one more run on the Υ(4S).” (Berkelman, chapter 10) |

- `collaboration:cusb` (completed): host `facility:cornell-wilson-lab`; formation 1978-02-15; intervals differ from the experiment (shared record).
- Note: No CUSB website exists; no URL is recorded.

#### experiment:hrs: High Resolution Spectrometer (HRS) at PEP (completed)

Facility `facility:slac`; accelerators `accelerator:pep`; detector `detector:hrs`; collaboration `collaboration:hrs`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| PEP data taking | end of 1981 | ~1990 [1983 to 1990] | active | uncertain | https://www.osti.gov/biblio/5336175 (+1 more) “The High Resolution Spectrometer (HRS) has been collecting data at PEP since the end of 1981” (Argonne report ANL-HEP-CP-83-50 (J. M. Weiss), abstract) |
| completed running (upper bound) | ~1990 [1983 to 1990] | — | completed | uncertain | https://cerncourier.com/a/slac-at-50-honouring-the-past-and-creating-the-future/ “The Positron–Electron Project (PEP), a collider ring with a diameter almost 10 times larger than SPEAR, ran during the years 1980–1990.” (CERN Courier, "SLAC at 50: honouring the past and creating the future") |

- `detector:hrs` (completed): placement `site:slac-menlo-park-campus` end of 1981 to ~1990 [1983 to 1990]; intervals identical to the experiment.
- `collaboration:hrs` (completed): host `facility:slac`; formation —; intervals identical to the experiment.
- Note: HRS here is the High Resolution Spectrometer at SLAC PEP; it is unrelated to the LAMPF and Jefferson Lab spectrometers of the same name.
- Note: No HRS website exists; none is recorded. The last-data date is unresolved (see the interval notes).

#### experiment:jade: JADE (completed)

Facility `facility:desy`; accelerators `accelerator:petra`; detector `detector:jade`; collaboration `collaboration:jade`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| proposal | 1976-08 | 1976-10 | proposed | verified | https://arxiv.org/abs/2208.11076 “August JADE proposal submitted to DESY management” (Bethke & Wagner (2022), Table 2) |
| recommended for approval; construction and installation | 1976-10 | 1979-03 | approved | verified | https://arxiv.org/abs/2208.11076 “October JADE proposal recommended for approval by PRC” (Bethke & Wagner (2022), Table 2 (1976, October)) |
| PETRA data taking | 1979-03 | 1986-11-03 | active | verified | https://arxiv.org/abs/2208.11076 “March first data recorded (single e− -beam, Ebeam = 11.3 GeV)” (Bethke & Wagner (2022), Table 2 (1979, March); end from Table 2 (1986, Nov. 3)) |
| PETRA shut down; experiment ended | 1986-11-03 | — | completed | verified | https://arxiv.org/abs/2208.11076 “Nov. 3 shutdown of PETRA and the JADE experiment” (Bethke & Wagner (2022), Table 2 (1986)) |

- `detector:jade` (completed): placement `site:desy-hamburg-campus` 1979-02 to 1986-11-03; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| PETRA data taking | 1979-03 | 1986-11-03 | active | verified | https://arxiv.org/abs/2208.11076 “March first data recorded (single e− -beam, Ebeam = 11.3 GeV)” (Bethke & Wagner (2022), Table 2 (1979, March); end from Table 2 (1986, Nov. 3)) |
| PETRA shut down; experiment ended | 1986-11-03 | — | completed | verified | https://arxiv.org/abs/2208.11076 “Nov. 3 shutdown of PETRA and the JADE experiment” (Bethke & Wagner (2022), Table 2 (1986)) |

- `collaboration:jade` (completed): host `facility:desy`; formation 1976-08; intervals differ from the experiment (shared record).
- Note: No live JADE website was fetched; no URL is recorded. Data preservation and the 2022 open-data release are described in Bethke & Wagner (2022).

#### experiment:kedr: KEDR (active)

Facility `facility:binp-novosibirsk`; accelerators `accelerator:vepp-4m`; detector `detector:kedr`; collaboration `collaboration:kedr`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| VEPP-4M data taking | 2002 | — | active | verified | https://kedr.inp.nsk.su/ “In 2002 we started experiments with the universal magnetic detector KEDR at the e+e- collider VEPP-4M in the Budker institute of nuclear physics in Novosibirsk.” (KEDR home page) |
| psi-meson energy region | 2002 | 2018 | active | approximate | https://kedr.inp.nsk.su/ “Until 2018 experiments with the detector were carried out in the energy region of psi-mesons.” (KEDR home page) |
| R scan, 2E = 4.6-7 GeV | 2018 | 2020 | active | approximate | https://kedr.inp.nsk.su/ “From 2018 to 2020, the experiments were carried out in the 2E region from 4.6 to 7 GeV in order to accurately measure R.” (KEDR home page) |

- `detector:kedr` (active): placement `site:binp-novosibirsk-akademgorodok` 2002 to —; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| VEPP-4M data taking | 2002 | — | active | verified | https://kedr.inp.nsk.su/ “In 2002 we started experiments with the universal magnetic detector KEDR at the e+e- collider VEPP-4M in the Budker institute of nuclear physics in Novosibirsk.” (KEDR home page) |

- `collaboration:kedr` (active): host `facility:binp-novosibirsk`; formation 2002; intervals differ from the experiment (shared record).
- Note: The KEDR detector page was last modified in 2001; it lists the subsystems only.

#### experiment:kloe: KLOE (completed)

Facility `facility:infn-lnf-frascati`; accelerators `accelerator:dafne`; detector `detector:kloe`; collaboration `collaboration:kloe`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| DAΦNE data taking (KLOE) | 1999 | 2006 | active | approximate | https://cerncourier.com/a/kloe-2-completes-data-taking-at-frascati-collider/ (+1 more) “which began with the first data collected by KLOE in 1999” (CERN Courier, 1 June 2018 (start); INFN-LNF particle-physics page: "formerly took data from 2000 to 2006" (end)) |
| KLOE data taking ended | 2006 | — | completed | approximate | https://w3.lnf.infn.it/research/particle-physics/?lang=en “the continuation of the KLOE experiment that formerly took data from 2000 to 2006” (INFN-LNF particle-physics page) |

- `detector:kloe` (completed): placement `site:infn-lnf-frascati` 1999 to 2018-03-30; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| KLOE data taking | 1999 | 2006 | active | approximate | https://cerncourier.com/a/kloe-2-completes-data-taking-at-frascati-collider/ (+1 more) “which began with the first data collected by KLOE in 1999” (CERN Courier, 1 June 2018; INFN-LNF particle-physics page (end 2006)) |
| upgrade to KLOE-2 | 2006 | 2014-11 | upgrade | approximate | https://arxiv.org/abs/1002.2572 (+1 more) “After the completion of the KLOE data taking, a proposal [5, 6] has been presented for a physics program to be carried out with an upgraded KLOE detector, KLOE-2” (KLOE-2 Inner Tracker TDR (2010), introduction; run start from CERN Courier) |
| KLOE-2 data taking | 2014-11 | 2018-03-30 | active | verified | https://cerncourier.com/a/kloe-2-completes-data-taking-at-frascati-collider/ “then continued with KLOE-2 since November 2014” (CERN Courier, 1 June 2018) |
| data taking ended | 2018-03-30 | — | completed | verified | https://cerncourier.com/a/kloe-2-completes-data-taking-at-frascati-collider/ “On 30 March the KLOE-2 experiment concluded its data-taking campaign” (CERN Courier, 1 June 2018) |

- `collaboration:kloe` (completed): host `facility:infn-lnf-frascati`; formation —; intervals identical to the experiment.
- Note: KLOE-2 is recorded as the separate experiment:kloe-2; one detector record (detector:kloe) serves both.

#### experiment:kloe-2: KLOE-2 (completed)

Facility `facility:infn-lnf-frascati`; accelerators `accelerator:dafne`; detector `detector:kloe`; collaboration `collaboration:kloe-2`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| expression of interest and upgrade | 2006-03-31 | 2014-11 | proposed | verified | https://arxiv.org/abs/1002.2572 “Expression of interest for the continuation of the KLOE physics program at DAΦNE upgraded in luminosity and in energy, March 31, 2006” (KLOE-2 Inner Tracker TDR (2010), reference [5]) |
| DAΦNE data taking (KLOE-2) | 2014-11 | 2018-03-30 | active | verified | https://cerncourier.com/a/kloe-2-completes-data-taking-at-frascati-collider/ “then continued with KLOE-2 since November 2014” (CERN Courier, 1 June 2018) |
| data taking ended | 2018-03-30 | — | completed | verified | https://cerncourier.com/a/kloe-2-completes-data-taking-at-frascati-collider/ “On 30 March the KLOE-2 experiment concluded its data-taking campaign” (CERN Courier, 1 June 2018) |

- `detector:kloe` (completed): placement `site:infn-lnf-frascati` 1999 to 2018-03-30; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| KLOE data taking | 1999 | 2006 | active | approximate | https://cerncourier.com/a/kloe-2-completes-data-taking-at-frascati-collider/ (+1 more) “which began with the first data collected by KLOE in 1999” (CERN Courier, 1 June 2018; INFN-LNF particle-physics page (end 2006)) |
| upgrade to KLOE-2 | 2006 | 2014-11 | upgrade | approximate | https://arxiv.org/abs/1002.2572 (+1 more) “After the completion of the KLOE data taking, a proposal [5, 6] has been presented for a physics program to be carried out with an upgraded KLOE detector, KLOE-2” (KLOE-2 Inner Tracker TDR (2010), introduction; run start from CERN Courier) |
| KLOE-2 data taking | 2014-11 | 2018-03-30 | active | verified | https://cerncourier.com/a/kloe-2-completes-data-taking-at-frascati-collider/ “then continued with KLOE-2 since November 2014” (CERN Courier, 1 June 2018) |
| data taking ended | 2018-03-30 | — | completed | verified | https://cerncourier.com/a/kloe-2-completes-data-taking-at-frascati-collider/ “On 30 March the KLOE-2 experiment concluded its data-taking campaign” (CERN Courier, 1 June 2018) |

- `collaboration:kloe-2` (completed): host `facility:infn-lnf-frascati`; formation 2006-03-31; intervals differ from the experiment (shared record).
- Note: The KLOE-2 detector is detector:kloe (shared with KLOE).

#### experiment:mac: MAC (completed)

Facility `facility:slac`; accelerators `accelerator:pep`; detector `detector:mac`; collaboration `collaboration:mac`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| approval | 1977 | 1980 | approved | approximate | https://history.aip.org/catalog/icos/5289.html “The experiment was approved in 1977 and completed running in 1986.” (AIP Study of Multi-Institutional Collaborations, SLAC-PEP-006) |
| PEP data taking | 1980 | 1986 | active | approximate | https://history.aip.org/catalog/icos/5289.html (+1 more) “The experiment was approved in 1977 and completed running in 1986.” (AIP catalogue, SLAC-PEP-006 (end 1986); SLAC Milestones: "1980: PEP operations begin" (start)) |
| completed running | 1986 | — | completed | approximate | https://history.aip.org/catalog/icos/5289.html “The experiment was approved in 1977 and completed running in 1986.” (AIP catalogue, SLAC-PEP-006) |

- `detector:mac` (completed): placement `site:slac-menlo-park-campus` 1980 to 1986; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| PEP data taking | 1980 | 1986 | active | approximate | https://history.aip.org/catalog/icos/5289.html (+1 more) “The experiment was approved in 1977 and completed running in 1986.” (AIP catalogue, SLAC-PEP-006 (end 1986); SLAC Milestones: "1980: PEP operations begin" (start)) |
| completed running | 1986 | — | completed | approximate | https://history.aip.org/catalog/icos/5289.html “The experiment was approved in 1977 and completed running in 1986.” (AIP catalogue, SLAC-PEP-006) |

- `collaboration:mac` (completed): host `facility:slac`; formation 1977; intervals differ from the experiment (shared record).
- Note: No MAC website exists; no URL is recorded.

#### experiment:mark-i: Mark I (completed)

Facility `facility:slac`; accelerators `accelerator:spear`; detector `detector:mark-i`; collaboration `collaboration:mark-i`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| proposal (SLAC-LBL Proposal) | 1971 | 1973-02 | proposed | verified | https://www.nobelprize.org/uploads/2018/06/perl-lecture.pdf “In 1971, we submitted the SLAC-LBL Proposal (Larsen et al. 1971) using the Mark I detector at SPEAR.” (Perl Nobel lecture, "The SLAC-LBL proposal") |
| SPEAR data taking | 1973-02 | 1977 | active | verified | https://www.nobelprize.org/uploads/2018/06/richter-lecture.pdf (+1 more) “The Mark I magnetic detector was ready to begin taking data in February 1973.” (Richter Nobel lecture, section 2.5; end from the SLAC AHRO Mark page (1977: dismantled and removed from SPEAR)) |
| dismantled and removed from SPEAR | 1977 | — | completed | verified | https://ahro.slac.stanford.edu/history-bits/mark “Dismantled and removed from SPEAR” (SLAC AHRO "MARK" page, detectors table (Mark I)) |

- `detector:mark-i` (completed): placement `site:slac-menlo-park-campus` 1973 to 1977; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| SPEAR data taking | 1973-02 | 1977 | active | verified | https://www.nobelprize.org/uploads/2018/06/richter-lecture.pdf (+1 more) “The Mark I magnetic detector was ready to begin taking data in February 1973.” (Richter Nobel lecture, section 2.5; end from the SLAC AHRO Mark page (1977: dismantled and removed from SPEAR)) |
| dismantled and removed from SPEAR | 1977 | — | completed | verified | https://ahro.slac.stanford.edu/history-bits/mark “Dismantled and removed from SPEAR” (SLAC AHRO "MARK" page, detectors table (Mark I)) |

- `collaboration:mark-i` (completed): host `facility:slac`; formation 1971; intervals differ from the experiment (shared record).
- Note: No Mark I website exists; no URL is recorded.

#### experiment:mark-ii: Mark II (completed)

Facility `facility:slac`; accelerators `accelerator:spear`, `accelerator:pep`, `accelerator:slc`; detector `detector:mark-ii`; collaboration `collaboration:mark-ii`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| SPEAR, PEP and SLC operation | 1977 | 1990 | active | verified | https://ahro.slac.stanford.edu/history-bits/mark “Mark II 1977 Installed at SPEAR” (SLAC AHRO "MARK" page, detectors table; end from the 1990 row (moved off SLC beamline)) |
| SPEAR phase | 1977 | 1979 | active | verified | https://ahro.slac.stanford.edu/history-bits/mark “1979 Moved to PEP at beginning of PEP program” (SLAC AHRO "MARK" page, detectors table) |
| PEP phase | 1979 | 1985 | active | approximate | https://ahro.slac.stanford.edu/history-bits/mark “1979 Moved to PEP at beginning of PEP program” (SLAC AHRO "MARK" page, detectors table (1979 move to PEP; 1985 return to PEP for testing)) |
| SLC phase | 1987 | 1990 | active | verified | https://ahro.slac.stanford.edu/history-bits/mark “1987 Rolled onto SLC beamline” (SLAC AHRO "MARK" page, detectors table) |
| moved off the SLC beamline | 1990 | — | completed | verified | https://ahro.slac.stanford.edu/history-bits/mark “1990 Moved off SLC beamline to east end of CEH” (SLAC AHRO "MARK" page, detectors table) |

- `detector:mark-ii` (completed): placement `site:slac-menlo-park-campus` 1977 to 1979; `site:slac-menlo-park-campus` 1979 to 1985; `site:slac-slc-collider-hall-sld` 1986 to 1990; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| SPEAR, PEP and SLC operation | 1977 | 1990 | active | verified | https://ahro.slac.stanford.edu/history-bits/mark “Mark II 1977 Installed at SPEAR” (SLAC AHRO "MARK" page, detectors table; end from the 1990 row (moved off SLC beamline)) |
| moved off the SLC beamline | 1990 | — | completed | verified | https://ahro.slac.stanford.edu/history-bits/mark “1990 Moved off SLC beamline to east end of CEH” (SLAC AHRO "MARK" page, detectors table) |

- `collaboration:mark-ii` (completed): host `facility:slac`; formation —; intervals differ from the experiment (shared record).
- Note: No Mark II website exists; no URL is recorded.
- Note: The brief lists "Mark II" under SPEAR and "Mark II at PEP" under PEP; the sources treat one detector with three accelerator stops, so one record carries all three phases.
- Note: Dates of the PEP phase are approximate: see the interval note.

#### experiment:mark-iii: Mark III (completed)

Facility `facility:slac`; accelerators `accelerator:spear`; detector `detector:mark-iii`; collaboration `collaboration:mark-iii`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| construction | 1978 | 1980 | construction | verified | https://ahro.slac.stanford.edu/history-bits/mark “Mark III 1978 Work begun on detector” (SLAC AHRO "MARK" page, detectors table) |
| commissioning at SPEAR | 1980 | 1981 | commissioning | verified | https://ahro.slac.stanford.edu/history-bits/mark “1980 Checkout of detector at SPEAR” (SLAC AHRO "MARK" page, detectors table) |
| SPEAR experimental program | 1981 | 1988 | active | verified | https://ahro.slac.stanford.edu/history-bits/mark “1981 Installed at SPEAR” (SLAC AHRO "MARK" page, detectors table; end from the 1988 row) |
| experimental program ended | 1988 | — | completed | verified | https://ahro.slac.stanford.edu/history-bits/mark “1988 Experimental program ends” (SLAC AHRO "MARK" page, detectors table) |

- `detector:mark-iii` (completed): placement `site:slac-menlo-park-campus` 1981 to 1988; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| commissioning at SPEAR | 1980 | 1981 | commissioning | verified | https://ahro.slac.stanford.edu/history-bits/mark “1980 Checkout of detector at SPEAR” (SLAC AHRO "MARK" page, detectors table) |
| SPEAR experimental program | 1981 | 1988 | active | verified | https://ahro.slac.stanford.edu/history-bits/mark “1981 Installed at SPEAR” (SLAC AHRO "MARK" page, detectors table; end from the 1988 row) |
| experimental program ended | 1988 | — | completed | verified | https://ahro.slac.stanford.edu/history-bits/mark “1988 Experimental program ends” (SLAC AHRO "MARK" page, detectors table) |

- `collaboration:mark-iii` (completed): host `facility:slac`; formation —; intervals differ from the experiment (shared record).
- Note: No Mark III website exists; no URL is recorded. The record is an addition to the brief (Mark III is not listed) because the SLAC archives page dates it fully.

#### experiment:mark-j: MARK J (completed)

Facility `facility:desy`; accelerators `accelerator:petra`; detector `detector:mark-j`; collaboration `collaboration:mark-j`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| proposal recommended for approval | 1976-10 | 1979-01 | proposed | verified | https://arxiv.org/abs/2208.11076 “October: 5 proposals recommended for approval (CELLO, JADE, Mark-J, PLUTO, TASSO)” (Bethke & Wagner (2022), Table 1 (1976, October)) |
| PETRA data taking | 1979-01 | 1986-11-03 | active | verified | https://www.desy.de/news/backgrounders/40_years_of_gluon/index_eng.html (+1 more) “Data-taking started in January 1979 by the detectors MARK J, PLUTO and TASSO.” (DESY backgrounder "The discovery of the gluon"; end from Bethke & Wagner (2022), Table 1) |
| PETRA shut down; experiment ended | 1986-11-03 | — | completed | verified | https://arxiv.org/abs/2208.11076 “final shutdown of PETRA and experiments” (Bethke & Wagner (2022), Table 1 (1986, November 3)) |

- `detector:mark-j` (completed): placement `site:desy-hamburg-campus` 1978-10 to 1986-11-03; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| PETRA data taking | 1979-01 | 1986-11-03 | active | verified | https://www.desy.de/news/backgrounders/40_years_of_gluon/index_eng.html (+1 more) “Data-taking started in January 1979 by the detectors MARK J, PLUTO and TASSO.” (DESY backgrounder "The discovery of the gluon"; end from Bethke & Wagner (2022), Table 1) |
| PETRA shut down; experiment ended | 1986-11-03 | — | completed | verified | https://arxiv.org/abs/2208.11076 “final shutdown of PETRA and experiments” (Bethke & Wagner (2022), Table 1 (1986, November 3)) |

- `collaboration:mark-j` (completed): host `facility:desy`; formation —; intervals differ from the experiment (shared record).
- Note: No MARK J website was found; no URL is recorded.
- Note: Collaboration leadership: J. Ellis (arXiv:1409.4232) writes "the Mark J collaboration led by Sam Ting".

#### experiment:nd: ND (completed)

Facility `facility:binp-novosibirsk`; accelerators `accelerator:vepp-2m`; detector `detector:nd`; collaboration `collaboration:nd`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| proposal | 1977 | 1982 | proposed | verified | https://wwwsnd.inp.nsk.su/SND_General/SND_experiment.pdf “Veniamin Sidorov and Sergei Serednyakov in 1977 proposed a project for a neutral detector (ND) in Novosibirsk for experiments at the VEPP-2M electron-positron collider.” (Silagadze, essay on the SND site, section I) |
| VEPP-2M data taking | 1982 | 1987 | active | approximate | https://wwwsnd.inp.nsk.su/SND_General/SND_experiment.pdf “ND was in operation at VEPP-2M during 1982-1987.” (Silagadze, essay on the SND site, section I) |
| data taking ended | 1987 | — | completed | approximate | https://wwwsnd.inp.nsk.su/SND_General/SND_experiment.pdf “ND was in operation at VEPP-2M during 1982-1987.” (Silagadze, essay on the SND site, section I) |

- `detector:nd` (completed): placement `site:binp-novosibirsk-akademgorodok` 1982 to 1987; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| VEPP-2M data taking | 1982 | 1987 | active | approximate | https://wwwsnd.inp.nsk.su/SND_General/SND_experiment.pdf “ND was in operation at VEPP-2M during 1982-1987.” (Silagadze, essay on the SND site, section I) |
| data taking ended | 1987 | — | completed | approximate | https://wwwsnd.inp.nsk.su/SND_General/SND_experiment.pdf “ND was in operation at VEPP-2M during 1982-1987.” (Silagadze, essay on the SND site, section I) |

- `collaboration:nd` (completed): host `facility:binp-novosibirsk`; formation 1977; intervals differ from the experiment (shared record).
- Note: No ND website exists beyond the SND pages; no URL recorded. ND is an addition to the brief; the SND essay states "The ND experiment yielded many new results", which supports the physics-results requirement.

#### experiment:pep-4-tpc: PEP-4 TPC (completed)

Facility `facility:slac`; accelerators `accelerator:pep`; detector `detector:pep-4-tpc`; collaboration `collaboration:pep-4-tpc`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| approval (PEP-4) | 1977 | 1982-01 | approved | approximate | https://history.aip.org/catalog/icos/5288.html “PEP-004 and PEP-009 were approved in 1977 and merged around 1985 and completed running in 1990.” (AIP Study of Multi-Institutional Collaborations, SLAC-PEP-004-009) |
| PEP data taking | 1982-04 | 1990 | active | verified | https://escholarship.org/content/qt7nj725kn/qt7nj725kn.pdf (+1 more) “installed in the PEP beam line in January 1982. Mter further checkout, data taking was started in April 1982.” (N. J. Hadley, LBL-16116 (1983), section 3.2 (start); AIP catalogue, SLAC-PEP-004-009 (end)) |
| completed running | 1990 | — | completed | approximate | https://history.aip.org/catalog/icos/5288.html “PEP-004 and PEP-009 were approved in 1977 and merged around 1985 and completed running in 1990.” (AIP catalogue, SLAC-PEP-004-009) |

- `detector:pep-4-tpc` (completed): placement `site:slac-menlo-park-campus` 1982-01 to 1990; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| PEP data taking | 1982-04 | 1990 | active | verified | https://escholarship.org/content/qt7nj725kn/qt7nj725kn.pdf (+1 more) “installed in the PEP beam line in January 1982. Mter further checkout, data taking was started in April 1982.” (N. J. Hadley, LBL-16116 (1983), section 3.2 (start); AIP catalogue, SLAC-PEP-004-009 (end)) |
| completed running | 1990 | — | completed | approximate | https://history.aip.org/catalog/icos/5288.html “PEP-004 and PEP-009 were approved in 1977 and merged around 1985 and completed running in 1990.” (AIP catalogue, SLAC-PEP-004-009) |

- `collaboration:pep-4-tpc` (completed): host `facility:slac`; formation 1977; intervals differ from the experiment (shared record).
- Note: No PEP-4 website exists; no URL is recorded. PEP-4 was merged with PEP-9 (the Two-Gamma experiment) around 1985 (AIP).

#### experiment:pluto: PLUTO (completed)

Facility `facility:desy`; accelerators `accelerator:doris`, `accelerator:petra`; detector `detector:pluto`; collaboration `collaboration:pluto`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| DORIS data taking | 1974 | 1978-10 | active | approximate | https://arxiv.org/abs/2405.03430 “Towards the end of 1974, the two detectors PLUTO and DASP were placed in their respective collision points.” (Ziemann, German Beams, DORIS section) |
| PETRA data taking | 1978-10 | 1980-03 | active | verified | https://arxiv.org/abs/2208.11076 (+1 more) “PLUTO had already operated [32] at the precursor storage ring DORIS, and was replaced at PETRA in March 1980 by the newly built CELLO detector [33].” (Bethke & Wagner (2022), section 2; DESY backgrounder) |
| PLUTO data taking (DORIS and PETRA) | 1974 | 1980-03 | active | approximate | https://arxiv.org/abs/2405.03430 (+1 more) “Towards the end of 1974, the two detectors PLUTO and DASP were placed in their respective collision points.” (Ziemann (DORIS start); Bethke & Wagner (2022), section 2 (replacement by CELLO in March 1980)) |
| PLUTO removed from PETRA; replaced by CELLO | 1980-03 | — | completed | approximate | https://arxiv.org/abs/2208.11076 “PLUTO had already operated [32] at the precursor storage ring DORIS, and was replaced at PETRA in March 1980 by the newly built CELLO detector [33].” (Bethke & Wagner (2022), section 2) |

- `detector:pluto` (completed): placement `site:desy-hamburg-campus` 1974 to 1978-10; `site:desy-hamburg-campus` 1978-10 to 1980-03; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| PLUTO data taking (DORIS and PETRA) | 1974 | 1980-03 | active | approximate | https://arxiv.org/abs/2405.03430 (+1 more) “Towards the end of 1974, the two detectors PLUTO and DASP were placed in their respective collision points.” (Ziemann (DORIS start); Bethke & Wagner (2022), section 2 (replacement by CELLO in March 1980)) |
| PLUTO removed from PETRA; replaced by CELLO | 1980-03 | — | completed | approximate | https://arxiv.org/abs/2208.11076 “PLUTO had already operated [32] at the precursor storage ring DORIS, and was replaced at PETRA in March 1980 by the newly built CELLO detector [33].” (Bethke & Wagner (2022), section 2) |

- `collaboration:pluto` (completed): host `facility:desy`; formation —; intervals differ from the experiment (shared record).
- Note: No PLUTO website was found; no URL is recorded.
- Note: Two interval phases (DORIS, PETRA) are recorded with an umbrella interval; the later fate of the PLUTO detector after March 1980 is not covered by the sources fetched.

#### experiment:snd: SND (active)

Facility `facility:binp-novosibirsk`; accelerators `accelerator:vepp-2m`, `accelerator:vepp-2000`; detector `detector:snd`; collaboration `collaboration:snd`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| VEPP-2M data taking | 1995 | 2000 | active | approximate | https://wwwsnd.inp.nsk.su/SND_General/SND_experiment.pdf (+1 more) “An improved version of the neutral detector — the spherical neutral detector (SND) [4] — operated at the VEPP2M collider in 1995-2000.” (Silagadze, essay on the SND site, section I; SND General Info ("SND is taking its data since 1995")) |
| upgrade for VEPP-2000 | 2000 | 2010 | upgrade | approximate | https://wwwsnd.inp.nsk.su/SND_General/SND_experiment.pdf “SND was also upgraded for experiments at this new collider [5] and it operates at VEPP-2000 since 2010.” (Silagadze, essay on the SND site, section I) |
| VEPP-2000 data taking | 2010 | — | active | approximate | https://wwwsnd.inp.nsk.su/SND_General/SND_experiment.pdf “SND was also upgraded for experiments at this new collider [5] and it operates at VEPP-2000 since 2010.” (Silagadze, essay on the SND site, section I) |

- `detector:snd` (active): placement `site:binp-novosibirsk-akademgorodok` 1995 to 2000; `site:binp-novosibirsk-akademgorodok` 2010 to —; intervals identical to the experiment.
- `collaboration:snd` (active): host `facility:binp-novosibirsk`; formation —; intervals identical to the experiment.
- Note: SND shares one record for its VEPP-2M and VEPP-2000 phases; the SND page of 1996 describes the original detector.

#### experiment:tasso: TASSO (completed)

Facility `facility:desy`; accelerators `accelerator:petra`; detector `detector:tasso`; collaboration `collaboration:tasso`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| proposal recommended for approval | 1976-10 | 1979-01 | proposed | verified | https://arxiv.org/abs/2208.11076 “October: 5 proposals recommended for approval (CELLO, JADE, Mark-J, PLUTO, TASSO)” (Bethke & Wagner (2022), Table 1 (1976, October)) |
| PETRA data taking | 1979-01 | 1986-11-03 | active | verified | https://www.desy.de/news/backgrounders/40_years_of_gluon/index_eng.html (+1 more) “Data-taking started in January 1979 by the detectors MARK J, PLUTO and TASSO.” (DESY backgrounder "The discovery of the gluon"; end from Bethke & Wagner (2022), Table 1) |
| PETRA shut down; experiment ended | 1986-11-03 | — | completed | verified | https://arxiv.org/abs/2208.11076 “final shutdown of PETRA and experiments” (Bethke & Wagner (2022), Table 1 (1986, November 3)) |

- `detector:tasso` (completed): placement `site:desy-hamburg-campus` 1978-10 to 1986-11-03; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| PETRA data taking | 1979-01 | 1986-11-03 | active | verified | https://www.desy.de/news/backgrounders/40_years_of_gluon/index_eng.html (+1 more) “Data-taking started in January 1979 by the detectors MARK J, PLUTO and TASSO.” (DESY backgrounder "The discovery of the gluon"; end from Bethke & Wagner (2022), Table 1) |
| PETRA shut down; experiment ended | 1986-11-03 | — | completed | verified | https://arxiv.org/abs/2208.11076 “final shutdown of PETRA and experiments” (Bethke & Wagner (2022), Table 1 (1986, November 3)) |

- `collaboration:tasso` (completed): host `facility:desy`; formation —; intervals differ from the experiment (shared record).
- Note: No TASSO website was found; no URL is recorded.
- Note: The DESY backgrounder lists the collaboration as DESY with institutes from Aachen, Bonn, Hamburg, Imperial College, Oxford, the Rutherford Laboratory, the Weizmann Institute and Wisconsin; this is the 1979 composition, not a complete membership history.

#### experiment:topaz: TOPAZ (completed)

Facility `facility:kek`; accelerators `accelerator:tristan`; detector `detector:topaz`; collaboration `collaboration:topaz`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| TRISTAN data taking | 1987-05 | 1995-12 | active | approximate | https://www.kek.jp/en/about/history/ “1987 May：TRISTAN experiments began.” (KEK history page; end from the 1995 Dec entry ("TRISTAN experiments finished")) |
| TRISTAN experiments finished | 1995-12 | — | completed | approximate | https://www.kek.jp/en/about/history/ “1995 Dec：TRISTAN experiments finished.” (KEK history page) |

- `detector:topaz` (completed): placement `site:kek-tsukuba-campus` 1987-05 to 1995-12; intervals identical to the experiment.
- `collaboration:topaz` (completed): host `facility:kek`; formation —; intervals identical to the experiment.
- Note: No TOPAZ website was found; no URL recorded. Approval and construction dates are not given in the sources fetched.

#### experiment:ua4: UA4 (completed)

Facility `facility:cern`; accelerators `accelerator:sps`; detector `detector:ua4`; collaboration `collaboration:ua4`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| approval | 1979-01-18 | 1981 | approved | verified | https://greybook.cern.ch/api/experiments/search/experiment?name=UA4 “"approvalDate" : "18-01-1979"” (Greybook record for UA4 (JSON, experiment details)) |
| SppS data taking | 1981 | 1985-06-17 | active | derived | https://greybook.cern.ch/api/experiments/search/experiment?name=UA4 (+1 more) “"endDate" : "17-06-1985", "startDate" : "18-01-1979", "statusCode" : "DT", "statusDescription" : "Data Taking"” (Greybook record for UA4, status history (Data Taking row); start bounded by the first SppS collisions) |
| data taking completed | 1985-06-18 | — | completed | verified | https://greybook.cern.ch/api/experiments/search/experiment?name=UA4 “"endDate" : "17-06-1995", "startDate" : "18-06-1985", "statusCode" : "CM"” (Greybook record for UA4, status history (Completed row)) |

- `detector:ua4` (completed): placement `site:cern-sps-lss4-ua2` 1981 to 1985-06-17; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| SppS data taking | 1981 | 1985-06-17 | active | derived | https://greybook.cern.ch/api/experiments/search/experiment?name=UA4 (+1 more) “"endDate" : "17-06-1985", "startDate" : "18-01-1979", "statusCode" : "DT", "statusDescription" : "Data Taking"” (Greybook record for UA4, status history (Data Taking row); start bounded by the first SppS collisions) |
| data taking completed | 1985-06-18 | — | completed | verified | https://greybook.cern.ch/api/experiments/search/experiment?name=UA4 “"endDate" : "17-06-1995", "startDate" : "18-06-1985", "statusCode" : "CM"” (Greybook record for UA4, status history (Completed row)) |

- `collaboration:ua4` (completed): host `facility:cern`; formation 1979-01-18; intervals differ from the experiment (shared record).
- Note: No UA4 website exists. Greybook gives no institute list for UA4. Data taking is bounded by Greybook's Data Taking status end (17 June 1985) and the first SppS collisions (1981).

#### experiment:ua5: UA5 (completed)

Facility `facility:cern`; accelerators `accelerator:sps`; detector `detector:ua5`; collaboration `collaboration:ua5`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| approval | 1979-02-15 | 1981 | approved | verified | https://greybook.cern.ch/api/experiments/search/experiment?name=UA5 “"approvalDate" : "15-02-1979"” (Greybook record for UA5 (JSON, experiment details)) |
| SppS data taking | 1981 | 1989-02-15 | active | derived | https://greybook.cern.ch/api/experiments/search/experiment?name=UA5 (+1 more) “"endDate" : "14-02-1989", "startDate" : "15-02-1979", "statusCode" : "CM", "statusDescription" : "Completed"” (Greybook record for UA5, status history (Completed row); start bounded by the first SppS collisions) |
| experiment finished | 1989-02-15 | — | completed | verified | https://greybook.cern.ch/api/experiments/search/experiment?name=UA5 “"endDate" : null, "startDate" : "15-02-1989", "statusCode" : "FI", "statusDescription" : "Finished"” (Greybook record for UA5, status history (Finished row)) |

- `detector:ua5` (completed): placement `site:cern-sps-lss4-ua2` 1981 to 1989-02-15; intervals differ from the experiment, see below.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| SppS data taking | 1981 | 1989-02-15 | active | derived | https://greybook.cern.ch/api/experiments/search/experiment?name=UA5 (+1 more) “"endDate" : "14-02-1989", "startDate" : "15-02-1979", "statusCode" : "CM", "statusDescription" : "Completed"” (Greybook record for UA5, status history (Completed row); start bounded by the first SppS collisions) |
| experiment finished | 1989-02-15 | — | completed | verified | https://greybook.cern.ch/api/experiments/search/experiment?name=UA5 “"endDate" : null, "startDate" : "15-02-1989", "statusCode" : "FI", "statusDescription" : "Finished"” (Greybook record for UA5, status history (Finished row)) |

- `collaboration:ua5` (completed): host `facility:cern`; formation 1979-02-15; intervals differ from the experiment (shared record).
- Note: No UA5 website exists. Greybook gives no institute list for UA5.

#### experiment:venus: VENUS (completed)

Facility `facility:kek`; accelerators `accelerator:tristan`; detector `detector:venus`; collaboration `collaboration:venus`.

| interval | start | end | status | conf. | evidence (URL, quote) |
|---|---|---|---|---|---|
| TRISTAN data taking | 1987-05 | 1995-12 | active | approximate | https://www.kek.jp/en/about/history/ “1987 May：TRISTAN experiments began.” (KEK history page; end from the 1995 Dec entry ("TRISTAN experiments finished")) |
| TRISTAN experiments finished | 1995-12 | — | completed | approximate | https://www.kek.jp/en/about/history/ “1995 Dec：TRISTAN experiments finished.” (KEK history page) |

- `detector:venus` (completed): placement `site:kek-tsukuba-campus` 1987-05 to 1995-12; intervals identical to the experiment.
- `collaboration:venus` (completed): host `facility:kek`; formation —; intervals identical to the experiment.
- Note: No VENUS website was found; no URL recorded. Approval and construction dates are not given in the sources fetched.

### Results

| result | date | type | publication | claim (quote) and source |
|---|---|---|---|---|
| result:argus-b-mixing-observation-1987 | 1987-06 (publication) | observation | 10.1016/0370-2693(87)91177-4 | https://doi.org/10.1016/0370-2693(87)91177-4 “Observation of B0-B0 mixing” (Phys. Lett. B 192 (1987) 245, paper title (Crossref record; the antiparticle bar is lost in the metadata)) |
| result:bes-ii-ppbar-threshold-observation-2003 | 2003-03-07 (preprint) | observation | 10.1103/PhysRevLett.91.022001 | https://arxiv.org/abs/hep-ex/0303006 “Observation of a near-threshold enhancement in th p pbar mass spectrum from radiative J/psi-->gamma p pbar decays” (arXiv:hep-ex/0303006, title (as typed on arXiv)) |
| result:bes-ii-r-measurement-2002 | 2001-02-04 (preprint) | measurement | 10.1103/PhysRevLett.88.101802 | https://arxiv.org/abs/hep-ex/0102003 “We report values of $R = \sigma(e^+e^-\to {hadrons})/\sigma(e^+e^-\to\mu^+\mu^-)$ for 85 center-of-mass energies between 2 and 5 GeV measured with the upgraded Beijing Spectrometer at the Beijing Electron-Positron Collider.” (arXiv:hep-ex/0102003, abstract) |
| result:bes-tau-mass-measurement-1992 | 1992-03 (announcement) | measurement | 10.1103/PhysRevLett.69.3021 | https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.69.3021 “The mass of the ... lepton has been measured at the Beijing Electron-Positron Collider using the Beijing Spectrometer.” (Phys. Rev. Lett. 69, 3021 (1992), abstract (TeX markup on the APS page)) |
| result:besiii-zc3900-observation-2013 | 2013-03-24 (preprint) | observation | 10.1103/PhysRevLett.110.252001 | https://arxiv.org/abs/1303.5949 “Observation of a charged charmoniumlike structure in e+e- to pi+pi-J/psi at \sqrt{s}=4.26 GeV” (arXiv:1303.5949, title) |
| result:cleo-charmless-semileptonic-b-evidence-1990 | 1990-01-01 (publication) | evidence | 10.1103/PhysRevLett.64.16 | https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.64.16 “We report the first evidence of charmless semileptonic decays of B mesons.” (Phys. Rev. Lett. 64, 16 (1990), abstract) |
| result:cleo-upsilon-three-states-observation-1980 | 1980-04-28 (publication) | observation | 10.1103/PhysRevLett.44.1108 | https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.44.1108 “Observation of Three Upsilon States” (Phys. Rev. Lett. 44, 1108 (1980), title) |
| result:cmd-2-pion-form-factor-measurement-2006 | 2006-10-09 (preprint) | measurement | 10.1016/j.physletb.2007.01.073 | https://arxiv.org/abs/hep-ex/0610021 “We present a measurement of the pion form factor based on e+e- annihilation data from the CMD-2 detector in the energy range 0.6<sqrt(s)<1.0 GeV with a systematic uncertainty of 0.8%.” (arXiv:hep-ex/0610021, abstract) |
| result:cmd-3-pipi-cross-section-measurement-2023 | 2023-02-17 (preprint) | precision_measurement | 10.1103/PhysRevD.109.112002 | https://arxiv.org/abs/2302.08834 “The cross section of the process $e^+e^-\to\pi^+\pi^-$ has been measured in the center of mass energy range from 0.32 to 1.2 GeV with the CMD-3 detector at the electron-positron collider VEPP-2000.” (arXiv:2302.08834, abstract) |
| result:cusb-upsilon-observation-1980 | 1980-04-28 (publication) | observation | 10.1103/PhysRevLett.44.1111 | https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.44.1111 “states have been observed at the Cornell Electron Storage Ring as narrow peaks in” (Phys. Rev. Lett. 44, 1111 (1980), abstract) |
| result:hrs-qed-four-lepton-test-1990 | 1990-10-01 (publication) | measurement | 10.1103/PhysRevD.42.2180 | https://journals.aps.org/prd/abstract/10.1103/PhysRevD.42.2180 “The complete ... QED calculation agrees reasonably well with the data.” (Phys. Rev. D 42, 2180 (1990), abstract) |
| result:jade-planar-three-jet-observation-1980 | 1979-08-23 (announcement) | observation | 10.1016/0370-2693(80)90680-2 | https://doi.org/10.1016/0370-2693(80)90680-2 “Observation of planar three-jet events in e+e− annihilation and evidence for gluon bremsstrahlung” (Phys. Lett. B 91 (1980) 142, paper title (Crossref record)) |
| result:kedr-charmonium-parameters-measurement-2013 | 2013-11-29 (preprint) | measurement | None | https://arxiv.org/abs/1311.7530 “We report results of experiments performed with the KEDR detector at the VEPP-4M $e^+e^-$ collider. They include final results for the mass and other parameters of the $J/\psi$, $\psi(2S)$ and $\psi(3770)$ and $J/\psi\to\gamma\eta_c$ branching fraction determination.” (arXiv:1311.7530, abstract) |
| result:kedr-r-measurement-2016 | 2016-10-10 (preprint) | measurement | 10.1016/j.physletb.2017.04.073 | https://arxiv.org/abs/1610.02827 “Using the KEDR detector at the VEPP-4M $e^+e^-$ collider, we have determined the values of $R$ at thirteen points of the center-of-mass energy between 1.84 and 3.05 GeV.” (arXiv:1610.02827, abstract) |
| result:kloe-pipi-muon-anomaly-measurement-2008 | 2008-09-23 (preprint) | precision_measurement | 10.1016/j.physletb.2008.10.060 | https://arxiv.org/abs/0809.3950 “We present the analysis of a new data set corresponding to an integrated luminosity of 240 pb$^{-1}$. We have achieved a reduced systematic uncertainty with respect to previously published KLOE results.” (arXiv:0809.3950, abstract) |
| result:kloe-u-boson-search-limit-2011 | 2011-10-03 (preprint) | limit | 10.1016/j.physletb.2011.11.033 | https://arxiv.org/abs/1110.0411 “The existence of a light dark force mediator has been tested with the KLOE detector at DAPHNE. This particle, called U, is searched for using the decay chain phi-->etaU, eta-->pi+pi-pi0, U-->e+e-. No evidence is found in 1.5 fb-1 of data.” (arXiv:1110.0411, abstract) |
| result:mac-electroweak-muon-pairs-measurement-1985 | 1985-10-28 (publication) | precision_measurement | 10.1103/PhysRevLett.55.1831 | https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.55.1831 “A high-statistics measurement has been made of the process ... with the MAC detector at the SLAC storage ring PEP.” (Phys. Rev. Lett. 55, 1831 (1985), abstract) |
| result:mark-i-anomalous-lepton-evidence-1975 | 1975-12-01 (publication) | evidence | 10.1103/PhysRevLett.35.1489 | https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.35.1489 “Evidence for Anomalous Lepton Production in ... Annihilation” (Phys. Rev. Lett. 35, 1489 (1975), title) |
| result:mark-i-psi-discovery-1974 | 1974-12-02 (publication) | discovery | 10.1103/PhysRevLett.33.1406 | https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.33.1406 “Discovery of a Narrow Resonance in ... Annihilation” (Phys. Rev. Lett. 33, 1406 (1974), title) |
| result:mark-j-three-jet-discovery-1979 | 1979-08 (announcement) | discovery | 10.1103/PhysRevLett.43.830 | https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.43.830 “Discovery of Three-Jet Events and a Test of Quantum Chromodynamics at PETRA” (Phys. Rev. Lett. 43, 830 (1979), paper title) |
| result:pluto-upsilon-observation-1978 | 1978-05 (publication) | observation | 10.1016/0370-2693(78)90287-3 | https://doi.org/10.1016/0370-2693(78)90287-3 “Observation of a narrow resonance formed in e+e− annihilation at 9.46 GeV” (Phys. Lett. B 76 (1978) 243, paper title (Crossref record)) |
| result:snd-neutron-form-factor-measurement-2023 | 2023-09-11 (preprint) | measurement | None | https://arxiv.org/abs/2309.05241 “The results of the measurement of the $e^+e^- \to n \bar{n}$ cross section and effective neutron timelike form factor are presented.” (arXiv:2309.05241, abstract) |
| result:tasso-planar-events-evidence-1979 | 1979-06-18 (announcement) | evidence | 10.1016/0370-2693(79)90830-X | https://doi.org/10.1016/0370-2693(79)90830-x “Evidence for planar events in e+e− annihilation at high energies” (Phys. Lett. B 86 (1979) 243, paper title (Crossref record)) |
| result:topaz-total-hadronic-cross-section-measurement-1990 | 1990-01 (publication) | measurement | 10.1016/0370-2693(90)92052-K | https://doi.org/10.1016/0370-2693(90)92052-k “Measurement of the total hadronic cross sections in ... annihilation and determination of the standard model parameters” (Phys. Lett. B 234 (1990) 525, paper title (Crossref record)) |
| result:ua4-elastic-and-total-cross-section-measurement-1982 | 1982-11 (publication) | measurement | 10.1016/0370-2693(82)90888-7 | https://doi.org/10.1016/0370-2693(82)90888-7 “Measurement of the proton-antiproton elastic and total cross section at a centre-of-mass energy of 540 GeV” (Phys. Lett. B 117 (1982) 126, paper title (Crossref record)) |
| result:ua5-multiplicity-scaling-violations-measurement-1986 | 1986-02 (publication) | measurement | 10.1016/0370-2693(86)91304-3 | https://doi.org/10.1016/0370-2693(86)91304-3 “Scaling violations in multiplicity distributions at 200 and 900 GeV” (Phys. Lett. B 167 (1986) 476, paper title (Crossref record)) |

Results whose publisher blocks automated access carry the paper title as the claim, and say so in the record: `result:argus-b-mixing-observation-1987`, `result:jade-planar-three-jet-observation-1980`, `result:pluto-upsilon-observation-1978`, `result:tasso-planar-events-evidence-1979`, `result:topaz-total-hadronic-cross-section-measurement-1990`, `result:ua4-elastic-and-total-cross-section-measurement-1982`, `result:ua5-multiplicity-scaling-violations-measurement-1986`.

### Documents

| document | date | type | URL | source |
|---|---|---|---|---|
| document:cepc-cdr-volume-1-2018 | 2018-09 | conceptual_design_report | https://arxiv.org/abs/1809.00285 | https://arxiv.org/abs/1809.00285 |
| document:cepc-cdr-volume-2-2018 | 2018-11 | conceptual_design_report | https://arxiv.org/abs/1811.10545 | https://arxiv.org/abs/1811.10545 |
| document:cepc-tdr-accelerator-2023 | 2023-12 | technical_design_report | https://arxiv.org/abs/2312.14363 | https://arxiv.org/abs/2312.14363 |
| document:clic-cdr-volume-2-2012 | 2012-02 | conceptual_design_report | https://arxiv.org/abs/1202.5940 | https://arxiv.org/abs/1202.5940 |
| document:clic-project-implementation-plan-2018 | 2019-03 | technical_design_report | https://arxiv.org/abs/1903.08655 | https://arxiv.org/abs/1903.08655 |
| document:fcc-feasibility-study-report-vol-1-2025 | 2025-03 | conceptual_design_report | https://cds.cern.ch/record/2928193 | https://home.cern/science/accelerators/future-circular-collider |
| document:fcc-feasibility-study-report-vol-2-2025 | 2025-03 | conceptual_design_report | https://cds.cern.ch/record/2928793 | https://home.cern/science/accelerators/future-circular-collider |
| document:fcc-feasibility-study-report-vol-3-2025 | 2025-03 | conceptual_design_report | https://cds.cern.ch/record/2928194 | https://home.cern/science/accelerators/future-circular-collider |
| document:ilc-tdr-volume-1-2013 | 2013-06 | technical_design_report | https://arxiv.org/abs/1306.6327 | https://arxiv.org/abs/1306.6327 |
| document:ilc-tdr-volume-3-ii-2013 | 2013-06 | technical_design_report | https://arxiv.org/abs/1306.6328 | https://arxiv.org/abs/1306.6328 |

### Sources

127 source records, all `src:colliders2-*`, each reusing an existing record by URL where one existed. Types: official facility and experiment sites, design reports (arXiv), journal abstracts (APS), CERN Greybook, CERN Courier and lab news offices, project documents and project histories; the AIP ICOS catalogue and university portals are `secondary`.

## Conflicts

| claim | source A | source B | chosen | why |
|---|---|---|---|---|
| VEPP-2M start | Skrinsky (1995): "started to operate for experiments at 1975" | Berkaev et al. (2011): "Since 1974"; Shatunov (2018): "VEPP-2M (1972-2000)" | Skrinsky (1975, experiments) | It is the only source that dates the start of experiments; the others are noted in the record. |
| Crystal Ball end of SPEAR running | AIP ICOS: approved 1975, "completed running in 1979" | Ziemann / DESY: three years at SPEAR, then five years at DESY, then storage at SLAC from 1987 | SPEAR phase about 1979-1982, DORIS II 1982-1987 (derived) | AIP's end date cannot be reconciled with the DESY history; the derived dates are marked `derived`. |
| ARGUS end of running | DESY DORIS page: stopped for high energy physics in 1993 | Other sources: 1992 | 1993 | Official DESY page is the higher-ranked source; recorded as approximate. |
| KLOE start of data taking | CERN Courier: 1999 | INFN-LNF: 2000 | 1999 | Year precision; the discrepancy is in the interval note. |
| UA4 / UA5 first data | Greybook "Data Taking" row starts at approval (UA4, 1979) | CERN Archives: first SppS collision in summer 1981 | 1981 | Greybook's start is an approval date, not a first-data date; marked `derived`. |
| CMD-1 accelerator | CMD page: "VEPP-2 collider" | Skrinsky: VEPP-2 ran only in 1967-1970 | VEPP-2M | The CMD-1 period 1979-1984 cannot be VEPP-2. |
| PETRA three-jet result type | DESY and CERN Courier: "discovery of the gluon" | TASSO paper title: "Evidence for planar events" | TASSO is `evidence`; MARK J carries the `discovery` row only where its own paper says so | A16: the result type follows the wording of the paper, not later retrospectives. |
| FCC-ee construction timeline | home.cern FCC page, compact timeline: installation 2038-2046, start-up late 2040s | Same page, FAQ list: installation after 2038, operation after 2045, "around 2045" | FAQ list | More specific; the difference (about a year) is in the interval note. |
| CEPC construction schedule | CEPC accelerator TDR (Dec 2023): "Construction is anticipated to begin around 2027-2028, pending government approval" | CERN Courier, 26 Oct 2025: CEPC "will not be considered for inclusion in China's next five-year plan (2026-2030)"; resubmission planned for 2030 | No construction interval recorded | The TDR schedule is superseded and nothing replaces it. |
| BEPCII and BESIII status | IPAC'26 paper: BEPCII upgrade under commissioning since May 2025; design luminosity reported achieved 28 April 2026 | BESIII collaboration continues to publish | BEPCII `commissioning`; BESIII `shutdown` | No source fetched says BESIII physics data taking has resumed; the collaboration is recorded as active. |

## Unresolved fields

- **Last HRS data.** Bracketed between 1983 (Argonne report written while data taking continues) and 1990 (end of PEP operation); 1990 is an upper bound, marked `uncertain`. No source states when HRS stopped.
- **BESIII data taking after 1 July 2024.** BEPCII is in commissioning; no source fetched says whether BESIII has resumed physics data taking.
- **ILC and CEPC sites.** Neither has a selected site. The ILC marker is the KEK Tsukuba campus and the CEPC marker is the IHEP Beijing campus, as anchors that the schema requires (an accelerator needs a facility and a site with sourced coordinates); both are flagged in the records. No coordinate was invented for Kitakami or Sefuri: a geocoder may back only campus and headquarters points (A17) and no fetched source gives coordinates for either candidate area.
- **FCC Feasibility Study Report volumes.** The CERN Document Server records (Anubis challenge) could not be read; the three document records rest on the home.cern page that lists them, and carry no abstract.
- **Abstracts not retrievable.** The publisher abstracts for ARGUS B0-B0bar mixing (1987), TASSO (1979), JADE (1980), PLUTO (1978), TOPAZ (1990), UA4 (1982) and UA5 (1986) are behind Elsevier and DESY bot challenges, which were not bypassed; the claim is the paper title. The brief asked for an abstract quote for the ARGUS mixing result, which could not be supplied.
- **Website, key specifications, documents and membership.** Not attempted for the experiments (tier D mandatory bar); see the per-row `missing_fields` in the coverage file.
- **Approval dates** for most pre-1990 experiments are missing or taken from the AIP ICOS catalogue (secondary).
- **Date precision.** The following intervals are approximate, derived or uncertain:

| entity | interval | start | end | conf. | note |
|---|---|---|---|---|---|
| facility:cornell-wilson-lab | laboratory dedicated | 1968-10 | — | derived | Month derived from "This October marks the 50th anniversary" in an article dated 19 October 2018; the article does not give the day. |
| accelerator:bepc | e+e- collider operation | 1988-10-16 | 2004 | approximate | Start is the sourced first-collision date; the end is the year the upgrade to BEPCII started (year precision). |
| accelerator:bepc | original BEPC | 1988-10-16 | 1995 | approximate | Year precision. |
| accelerator:bepc | upgrade of BEPC (reliability and luminosity) | 1995 | 1998 | approximate | The review says BEPC ran until 1995, was then upgraded, and the upgraded machine ran from 1998; the interval between is taken as the upgrade period. |
| accelerator:bepc | upgraded BEPC | 1998 | 2004 | approximate | Year precision. |
| accelerator:bepc | BEPC replaced by BEPCII upgrade | 2004 | — | approximate | BEPC data taking ended in 2004 when the BEPCII upgrade began; BEPCII (accelerator:bepcii) is the rebuilt two-ring machine on the same site. |
| accelerator:bepcii | BEPCII upgrade: hardware replacement | 2024-07-01 | 2025-05 | approximate | Hardware replacement finished by the end of 2024; the end of this interval is the start of machine commissioning in May 2025 (same abstract). |
| accelerator:cesr | construction | 1977 | 1979-04 | approximate | Year-precision start; the end is the first electron injection in April 1979 (same source). |
| accelerator:cesr | commissioning | 1979-04 | 1979-08-14 | approximate | The first electrons were injected on or about 2 April 1979 (the author recalls); the first measurable colliding-beam luminosity came on 14 August 1979. |
| accelerator:cesr | CESR-c (charm-region running) | 2003 | 2008-03-03 | approximate | CLEO-c took data at the lower, charm-threshold energies enabled by the superferric wigglers installed in 2003-04. |
| accelerator:clic | design phase | 2012-02 | — | approximate | Start = the posting of the CDR volume on physics and detectors; earlier CLIC design work is not recorded. The Project Implementation Plan (2018/2019) states CLIC is "under development by international collaborations hosted by CERN". The CERN page and the plan  |
| accelerator:dafne | first beams and commissioning | 1997 | 1999 | approximate | LNF says first beams circulated in 1997; INFN's laboratories page says DAFNE "started operating" in 1999 (taken as the end of commissioning). |
| accelerator:dafne | e+e- collider operation (phi factory) | 1999 | — | approximate | INFN (2026) says SIDDHARTA2 is "now operating at DAFNE", so the collider is still in use. KLOE took data from 1999 (CERN Courier) or 2000 (LNF) to 2006; KLOE-2 from November 2014 to 30 March 2018; SIDDHARTA-2 and PADME since. |
| accelerator:doris | e+e- collider operation (DORIS, DORIS II, DORIS III) | 1974 | 1993 | approximate | Year-precision start (the page gives no month); end is the year the page says DORIS became a dedicated synchrotron-radiation source. |
| accelerator:doris | DORIS (two rings) | 1974 | 1982 | approximate | Original double-ring machine (DOppel-RIng-Speicher), initially up to 3 GeV per beam; end = the 1982 upgrade to DORIS II. |
| accelerator:doris | collider operation ended | 1993 | — | approximate | Particle-physics running ended; DORIS then served only as a synchrotron-radiation source (until 2012 per Ziemann, "German Beams"). This record covers the collider only. |
| accelerator:fcc-ee | civil engineering (if approved) | 2033 (planned) | 2040 (planned) | approximate | Planned date from the project schedule, not a reported event. Conditional on a positive Council decision, expected by 2028. |
| accelerator:fcc-ee | installation (if approved) | after 2038 (planned) | ~2045 (planned) | approximate | Planned date from the project schedule, not a reported event. The same page's compact timeline gives the installation phase as 2038-2046 and start-up in the "late 2040s", which differs from this list by about a year; the FAQ list is followed here. |
| accelerator:fcc-ee | commissioning and operation (if approved) | after 2045 (planned) | — | approximate | Planned date from the project schedule, not a reported event. |
| accelerator:pep | construction | 1977-06 | 1980 | approximate | Start is the month stated by Hallonsten; end is the year PEP operations began (SLAC Milestones). |
| accelerator:pep | e+e- collider operation | 1980 | 1990 | approximate | Year precision; the SLAC page gives the start, CERN Courier gives the 1980-1990 span. The end of collider running is not dated more precisely in the sources fetched. |
| accelerator:pep | collider operation ended | 1990 | — | approximate | The PEP ring was later reused for the high-energy ring of PEP-II (accelerator:pep-ii). |
| accelerator:spear | construction | 1970 | 1972 | approximate | Funding agreed in 1970 (about 20 months before service in 1972); year precision. |
| accelerator:vepp-2000 | upgrade decision and construction | 2000 | 2007 | approximate | Year precision: decision in spring 2000 to modernise VEPP-2M (introduction), construction completed 2007 (abstract). |
| accelerator:vepp-2000 | commissioning and first experiments | 2007 | 2010 | approximate | First beam tests (round beams at 508 MeV) from 2007; CMD-3 installed October 2009; the first experimental season was completed in summer 2010. |
| accelerator:vepp-2000 | e+e- collider operation | 2010 | — | approximate | Year precision for the start. The injection chain was upgraded in 2013-2016 (IPAC-2017 abstract); CMD-3 reported on 8 June 2026 that more data (x3) are to be collected in 2024-2026. |
| accelerator:vepp-2000 | upgraded injection complex | 2013 | 2016 | approximate | Injection-chain upgrade within the operating period; the 2016/2017 run was the first reported with the new BINP injection complex (VEPP-2000 news, 12 July 2017). |
| accelerator:vepp-2m | e+e- collider operation | 1975 | 2000 | approximate | Start = the year VEPP-2M started operating for experiments (Skrinsky). Other BINP sources date the machine earlier: "Since 1974" (Berkaev et al. 2011) and "VEPP-2M (1972-2000)" (Shatunov 2018). The end is the 2000 decision and upgrade to VEPP-2000. |
| accelerator:vepp-2m | upgraded to VEPP-2000 | 2000 | — | approximate | Year precision. In spring 2000 the Institute decided to modernise VEPP-2M into VEPP-2000 (Berkaev et al.); the old machine was not continued. |
| accelerator:vepp-4m | e+e- collider operation (VEPP-4 and VEPP-4M) | 1980 | — | approximate | Skrinsky dates the VEPP-4 collider operation from 1980 (maximum 5.5 GeV per beam then); the VEPP-4M upgrade date was not found in the sources fetched. KEDR has taken data at VEPP-4M since 2002 and published new results in 2025 (arXiv:2506.02421). |
| experiment:amy | TRISTAN data taking | 1987-05 | 1995-12 | approximate | The detector's own start and end dates are not given in the sources fetched; the dates are those of the TRISTAN experimental programme (May 1987 to December 1995). Kondo writes that data taking ran 1987-1995. |
| experiment:amy | TRISTAN experiments finished | 1995-12 | — | approximate | Programme end date, applied to this detector. |
| experiment:argus | DORIS II data taking | 1982 | 1993 | approximate | Start is tied to the 1982 DORIS II upgrade (first-data date not stated); the end is the year the DESY DORIS page says ARGUS stopped operating for high energy physics (other sources give 1992). |
| experiment:argus | ARGUS ended at DORIS | 1993 | — | approximate | Year precision; see the active interval. |
| experiment:bes | BEPC data taking (BESI) | 1989 | 1995 | approximate | Year precision. BEPC first collided on 16 October 1988; BES published its first physics paper (the tau mass) in March 1992 (IHEP history page). |
| experiment:bes | upgraded to BESII | 1995 | — | approximate | BESII is recorded as the separate experiment:bes-ii. |
| experiment:bes-ii | upgrade of BESI to BESII | 1995 | 1998 | approximate | The upgrade replaced the central drift chamber with a revamped MARK II vertex detector and replaced the main drift chamber and the barrel time-of-flight system. |
| experiment:bes-ii | BEPC data taking (BESII) | 1998 | 2004 | approximate | Year precision. |
| experiment:bes-ii | ended with the BEPCII upgrade | 2004 | — | approximate | Year precision. |
| experiment:bes-iii | BEPCII data taking | 2009-07 | 2024-07-01 | approximate | Start is the BEPCII acceptance-test month. The end is the BEPCII shutdown date for the upgrade, not a BESIII-specific statement. |
| experiment:bes-iii | BEPCII upgrade shutdown | 2024-07-01 | — | approximate | The collider has been shut down for its upgrade since 1 July 2024 and was in commissioning in 2026 (design luminosity reported achieved 28 April 2026); no fetched source states whether BESIII physics data taking has resumed, so the experiment is recorded as in |
| experiment:cleo | conception of the South Area Experiment | 1975 | 1977 | approximate | The page gives the year the study group conceived CLEO; the date of the formal proposal is not stated. |
| experiment:cleo | construction | 1977 | 1979-10 | approximate | Year-precision start; the end is the first CLEO run in October 1979. |
| experiment:cleo | CLEO-1 | 1979-10 | 1984 | derived | End = start of the CLEO-1.5 upgrade period (Berkelman chapter 8 title); the transition year is approximate. |
| experiment:cleo | CLEO-1.5 | 1984 | 1989 | approximate | Chapter title dates; year precision. |
| experiment:cleo | CLEO-2 | 1989 | 1995 | approximate | Chapter title dates; year precision. |
| experiment:cleo | CLEO-2.5 (CLEO II.V) | 1995 | 1999 | approximate | Year precision. |
| experiment:cleo | CLEO-3 | 1999 | 2003 | approximate | Year precision; end = start of CLEO-c data collection in 2003. |
| experiment:cleo | CLEO-c | 2003 | 2008-03-03 | approximate | Year precision for the start; running ended 3 March 2008. |
| experiment:cmd-1 | VEPP-2M data taking (CMD-1) | 1979 | 1984 | approximate | Year precision. The page says "VEPP-2 collider"; VEPP-2 itself ran only in 1967-1970 (Skrinsky), so VEPP-2M is meant. |
| experiment:cmd-1 | CMD-1 experiments ended | 1984 | — | approximate | Year precision; the CMD-2 detector followed. |
| experiment:cmd-2 | commissioning of CMD-2 | 1984 | 1992 | approximate | Year precision; the page calls the whole period "commissioning". |
| experiment:cmd-2 | VEPP-2M data taking (CMD-2) | 1992 | 2000 | approximate | Year precision. |
| experiment:cmd-2 | CMD-2 experiments ended | 2000 | — | approximate | Year precision; the CMD-2 detector was followed by CMD-3 at VEPP-2000. |
| experiment:cmd-3 | design, prototyping and commissioning | 2000 | 2009-10 | approximate | The page dates the CMD-3 work "2000 - present"; the end of construction is the installation in October 2009 (Berkaev et al.). |
| experiment:cmd-3 | installation and first experimental season | 2009-10 | 2010 | approximate | The first experimental season was completed in summer 2010. |
| experiment:cmd-3 | VEPP-2000 data taking | 2010 | — | approximate | Year precision. |
| experiment:crystal-ball | approval (SLAC-SP-024) | 1975 | 1979 | approximate | AIP gives approval in 1975. Its "completed running in 1979" conflicts with the three years at SPEAR derived below and is not used for the end of running (see log). |
| experiment:crystal-ball | SPEAR and DORIS II running | 1979 | 1987 | derived | No source states exact start and end dates. Derived: put in storage at SLAC from 1987, five years at DESY (DORIS II upgraded in 1982, Ziemann), three years before that at SPEAR, so about 1979-1982 at SPEAR and 1982-1987 at DESY. |
| experiment:crystal-ball | SPEAR phase | 1979 | 1982 | derived | Three years at SLAC before DESY; derived dates (see the umbrella interval). |
| experiment:crystal-ball | DORIS II phase | 1982 | 1987 | derived | Start from the 1982 DORIS II upgrade, end from "put in storage at SLAC from 1987". |
| experiment:crystal-ball | removed from DESY; stored at SLAC | 1987 | — | approximate | The e+e- programme ended with the detector going into storage; it later ran at Brookhaven (AGS) and Mainz (hadron physics, outside this record). |
| experiment:cusb | CESR data taking (north area) | 1979-08 | 1990 | derived | Start: CUSB had run "since the turn-on of CESR in 1979"; the month is taken from the first colliding-beam luminosity on 14 August 1979 (chapter 3); end derived as 1979 + eleven years (the PAC terminated CUSB after one more Υ(4S) run in the early CLEO-2 era). C |
| experiment:cusb | CUSB terminated | 1990 | — | derived | Year derived (see the active interval); the detector was dismantled afterwards. |
| experiment:hrs | PEP data taking | end of 1981 | ~1990 [1983 to 1990] | uncertain | Start: "since the end of 1981". The end of HRS data taking was not found in any source consulted. It is bracketed between 1983 (the Argonne report is written while data taking continues; 120 pb-1 accumulated) and the end of PEP operation in 1990 ("ran during t |
| experiment:hrs | completed running (upper bound) | ~1990 [1983 to 1990] | — | uncertain | The end of HRS data taking was not found in any source consulted. It is bracketed between 1983 (the Argonne report is written while data taking continues; 120 pb-1 accumulated) and the end of PEP operation in 1990 ("ran during the years 1980–1990", CERN Courie |
| experiment:kedr | psi-meson energy region | 2002 | 2018 | approximate | Year precision. |
| experiment:kedr | R scan, 2E = 4.6-7 GeV | 2018 | 2020 | approximate | Year precision; further plans include the upsilon region. |
| experiment:kloe | DAΦNE data taking (KLOE) | 1999 | 2006 | approximate | Start 1999 per CERN Courier; LNF gives 2000. End 2006 per LNF (the KLOE-2 expression of interest followed in March 2006). Year precision. |
| experiment:kloe | KLOE data taking ended | 2006 | — | approximate | Year precision. KLOE data continue to be analysed (CERN Courier). |
| experiment:mac | approval | 1977 | 1980 | approximate | AIP catalogue record (secondary source); year precision. End of the interval = start of PEP operations (1980). |
| experiment:mac | PEP data taking | 1980 | 1986 | approximate | End from the AIP catalogue. The start is taken as the start of PEP operations in 1980; the date of the first MAC data was not found. By May 1983 MAC had been exposed to 40 pb-1 at PEP (SLAC-PUB-3118). |
| experiment:mac | completed running | 1986 | — | approximate | Year precision. |
| experiment:mark-ii | PEP phase | 1979 | 1985 | approximate | The page records the move to PEP in 1979, the 1982 selection as first SLC detector and a 1985 upgrade and return to PEP for testing; the date it left PEP for the upgrade is not stated, so the end year is approximate. |
| experiment:nd | VEPP-2M data taking | 1982 | 1987 | approximate | Year precision. |
| experiment:nd | data taking ended | 1987 | — | approximate | Year precision. The improved SND followed in 1995. |
| experiment:pep-4-tpc | approval (PEP-4) | 1977 | 1982-01 | approximate | AIP catalogue record (secondary source); year precision. The detector was first assembled in the fall of 1981 and installed in the PEP beam line in January 1982 (Hadley thesis). |
| experiment:pep-4-tpc | completed running | 1990 | — | approximate | Year precision. |
| experiment:pluto | DORIS data taking | 1974 | 1978-10 | approximate | Year-precision start; the end is the move into the PETRA beam in October 1978. |
| experiment:pluto | PLUTO data taking (DORIS and PETRA) | 1974 | 1980-03 | approximate | Union of the two phases. PLUTO is recorded as ending in March 1980 when CELLO replaced it at PETRA; whether PLUTO took data elsewhere later (for example back at DORIS) is not stated in the sources fetched. |
| experiment:pluto | PLUTO removed from PETRA; replaced by CELLO | 1980-03 | — | approximate | End of PLUTO at PETRA; later activity of the detector, if any, is not sourced here. |
| experiment:snd | VEPP-2M data taking | 1995 | 2000 | approximate | Year precision. |
| experiment:snd | upgrade for VEPP-2000 | 2000 | 2010 | approximate | VEPP-2M was modernised into VEPP-2000 after 2000; the first VEPP-2000 season with SND was 2009/2010 (Berkaev et al.). |
| experiment:snd | VEPP-2000 data taking | 2010 | — | approximate | Year precision. SND results published in 2025 (e.g. arXiv:2510.09019) show continued operation. |
| experiment:topaz | TRISTAN data taking | 1987-05 | 1995-12 | approximate | The detector's own start and end dates are not given in the sources fetched; the dates are those of the TRISTAN experimental programme (May 1987 to December 1995). Kondo writes that data taking ran 1987-1995. |
| experiment:topaz | TRISTAN experiments finished | 1995-12 | — | approximate | Programme end date, applied to this detector. |
| experiment:ua4 | SppS data taking | 1981 | 1985-06-17 | derived | Greybook's Data Taking row runs from the approval date (18 January 1979) to 17 June 1985, so its start is not a first-data date. The start is taken as 1981, the year the SPS first collided protons and antiprotons ("In summer 1981 the first collision ... was re |
| experiment:ua5 | SppS data taking | 1981 | 1989-02-15 | derived | Greybook records one "Completed" row from approval (15 February 1979) to 14 February 1989 and no separate Data Taking row, so neither a first-data nor a last-data date is stated. The start is the year of the first SppS collisions (summer 1981, CERN Archives gu |
| experiment:venus | TRISTAN data taking | 1987-05 | 1995-12 | approximate | The detector's own start and end dates are not given in the sources fetched; the dates are those of the TRISTAN experimental programme (May 1987 to December 1995). Kondo writes that data taking ran 1987-1995. |
| experiment:venus | TRISTAN experiments finished | 1995-12 | — | approximate | Programme end date, applied to this detector. |

## Candidates considered and excluded

| candidate | decision | reason |
|---|---|---|
| EIC, HERMES, HERA-B, Gargamelle | excluded by the brief | Owned by other streams. |
| ILD and SiD (ILC detector concepts) | excluded | They are described in the ILC TDR (Vol. 4 and Vol. 3.II abstract), but the ILC has no host site, so no host site can be named for them (STREAM_RULES: proposed experiments need a design report naming experiment and host site). |
| CEPC reference detector (TDR, October 2025, arXiv:2510.05260) | excluded | The CEPC site has not been selected (accelerator TDR); the design report names China, not a place. |
| CLIC detector (CLICdet, CLIC_ILD, CLIC_SiD) | excluded | The design documents name CERN as host of the project but no site for the detector. |
| FCC-ee detector concepts (CLD, IDEA and others) | excluded | Described in the Feasibility Study Report Vol. 1, whose CDS record could not be read; not verified. |
| SCTF (BINP Super c-tau factory) | candidate, not researched | Optional extra in the brief; no source was fetched for it in this pass. |
| STCF (Super Tau-Charm Facility, China) | candidate, not researched | Would need a new facility; its location is not established by any source read here. The MIT PPC blog (30 October 2025) says China is still considering a Super Tau/Charm factory for the five-year plan under discussion; no design report was read. |
| LEP3, LCF (Linear Collider Facility at CERN), FCC-hh, SPPC, muon collider | excluded | Outside the brief's list of proposed colliders; no design report was read for any of them. |
| ADONE (Frascati) and its experiments | candidate, not researched | Not in the brief's accelerator list; LNF facility record exists to host it. |
| DORIS: DASP, DASP II, LENA; SPEAR: DELCO and others; PEP: DELCO, ASP, free-quark search; VEPP-2M: OLYA; VEPP-4: MD-1 | candidates, not researched | Not in the brief's experiment list; each would need a source for its dates. |
| ISR experiments (CERN) | not created | Not in the brief. `accelerator:isr` exists; confirm with the historic-CERN stream that the ISR experiments are owned there. |
| DAΦNE experiments FINUDA, DEAR, SIDDHARTA, SIDDHARTA-2, PADME | not created | Hadron and nuclear physics at DAΦNE; belong to the hadron-nuclear stream. |
| Mark III at SPEAR | created | Added to the brief's list (SPEAR Mark I, II) because the AIP catalogue and the SLAC AHRO page cover it. |

## For the integrator

- **Anchors for the proposed colliders.** `accelerator:ilc` sits on `facility:kek` / `site:kek-tsukuba-campus` and `accelerator:cepc` on `facility:ihep-beijing` / `site:ihep-beijing-campus` only because the schema needs a facility and a located site. Both records say so. If the globe draws accelerators, the ILC and CEPC markers must not be read as sites. FCC-ee and CLIC sit on `site:cern-meyrin` (the host laboratory).
- **KEK sites.** `site:kek-tsukuba-campus` is new (TRISTAN and the ILC anchor). `facility:kek` already has `site:kek-tsukuba-belle-ii`; merge the two campus points if the integrator prefers one.
- **No topics, institutions, people or memberships** were written. Topic ids used are existing ones (`topic:collider-physics`, `topic:electroweak-physics`, `topic:qcd`, `topic:b-physics`, others listed in each experiment).
- **Proposed colliders have no coverage rows** because registry rows are per experiment; none of the four proposed colliders has an experiment record.
- **BESIII** is recorded `shutdown`; update when the BEPCII upgrade commissioning ends and BESIII data taking resumes.
- **STCF** (a Super Tau-Charm Facility in China) needs a new facility if a stream takes it; its host location was not established here. **ISR experiments** and the **DAΦNE hadron-nuclear experiments** should be assigned (see exclusions).
- **ARGUS B0-B0bar mixing** has only the paper title as its claim; replace when an abstract is available from a source that permits automated access.
- **Greybook** ids are recorded for UA4 and UA5 only (`external.greybook`); no INSPIRE ids were recorded (INSPIRE was not contacted).

## Checks run

Run on 2026-10-26 from the worktree after the last data commit:

- Validator `python -m hepgraph.atlas.validate`: `0 errors, 1611 warnings, 4 informational`. The only findings on this stream's files are five A23 informational notices (campus-grade site points: IHEP Beijing, Cornell Wilson Lab, INFN-LNF Frascati, BINP Akademgorodok, KEK Tsukuba campus).
- Build `python -m hepgraph.atlas.build`: wrote 81 files (version 3b482e8bb053f89a), the coverage registry merged without a duplicate id; `static/atlas/generated` restored with `git checkout -- static/atlas/generated` and not committed.
- Tests `python -m pytest -q`: `689 passed, 139 skipped` (the skips need `HEPGRAPH_TEST_DATABASE_URL` or `HEPGRAPH_TEST_POSTGRES_DSN`).
