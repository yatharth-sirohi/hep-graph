# PRECISION_2: precision, rare-process, antimatter and neutron experiments

Stream owner tag: `precision-2`. Branch `atlas-c5-precision` (worktree `HEP-Graph-ar-c5-precision`), coverage rows in
`data/atlas/coverage/precision-2.json`, topics in `data/atlas/topics/precision-2.json`. Date of all fetches: 2026-10-26.

## Scope

Amendment A26 of `docs/HEP_ATLAS_ONTOLOGY.md` brings antimatter and neutron-precision experiments into the Atlas. This stream
covers four groups:

1. **Antimatter at CERN** (kind `antimatter`): the Antiproton Decelerator, ELENA and LEAR with their experiments ALPHA (with
   ALPHA-g), AEgIS, ASACUSA, ATHENA, ATRAP, BASE, GBAR, PUMA and PS210.
2. **Muons and rare pion decays** (kind `muon_precision`): BNL E821, MuLan, MUSE, PEN, PiENu, PIONEER, the J-PARC muon g-2/EDM
   experiment (E34) and DeeMe, plus the new facility TRIUMF and the new site J-PARC MLF.
3. **Neutron EDM** (kind `neutron_precision`): the ILL Sussex-RAL-ILL experiment, the PSI nEDM experiment, n2EDM, nEDM@SNS and
   TUCAN.
4. **Neutron decay and lifetime, and kaons**: NIST BL2/BL3 (new facility NIST Center for Neutron Research), UCNtau, Nab,
   PERKEO III (kind `neutron_precision`) and KOTO II (kind `rare_kaon`).

Beyond the brief's list, three extras met the inclusion bar and were added: `experiment:nist-bl1` (the predecessor that carries
the published NIST lifetime result), `experiment:twist` (TRIUMF muon decay parameters, final results 2010) and `experiment:muedm`
(PSI frozen-spin muon EDM, `proposed`, with a concept paper naming PSI as host).

Topics `topic:antimatter` and `topic:neutron-physics` (both under `topic:precision-and-rare-processes`) were written first, so
every experiment references them.

Method. Sources were fetched with a curl-based tool that extracts plain text (HTML and PDF), so every `quote` is a verbatim
substring of the page or PDF read on 2026-10-26; the Atlas quote checker and an excerpt checker confirmed this for every new
quote and source excerpt. inspirehep.net was never contacted, so `external.inspire_experiment` is empty throughout and every
experiment is tier C (no tier A or B without an INSPIRE record). Existing records were reused by URL; nothing owned by another
stream was edited. A subagent attempt to parallelise the research was refused (concurrent-subagent limit), so all work was
done in this session.

Conventions used throughout, because the sources are often dated only by year:

* An interval start or end that is only a lower or upper bound (a paper date, the first dated run) is marked
  `confidence: approximate` or `uncertain` and says so in its note.
* A completed experiment has an `active` interval ending when data taking ended and a `completed` interval starting there
  (the pattern of `experiment:e949` and `experiment:lsnd`).
* Experiments that depend on the CERN Antimatter Factory carry a `shutdown` interval from 2026-08-31 (Long Shutdown 3), as
  `experiment:na62` does; the end is left open because no experiment-specific restart date is published.
* Coordinates are campus-grade and `approximate` (A17, A23); no hall-level position was available for any new site.


## Entities written

Files added by this stream: accelerators 3, collaborations 31, coverage 1, detectors 32, documents 4, experiments 31, facilities 2, results 29, sites 4, sources 102, topics 1.


### Facilities, sites and accelerators

| id | kind | status | dates (start to end) | site / coordinate | URL and verbatim quote behind each date and coordinate |
|---|---|---|---|---|---|
| facility:nist-center-for-neutron-research | reactor_site | active | NBSR operation (initial criticality 7 December 1967): 1967-12-07 to 2021-02-03 | site:nist-ncnr-gaithersburg | https://www.nist.gov/ncnr/about-ncnr/history; https://www.nist.gov/news-events/news/2023/03/nrc-authorizes-restart-nist-research-reactor: "1967: The NBSR achieves initial criticality on December 7, 1967, marking the start of its nuclear operations." |
| facility:nist-center-for-neutron-research | reactor_site | active | reactor shut down after the 3 February 2021 fuel-element incident: 2021-02-03 to 2026-05 | site:nist-ncnr-gaithersburg | https://www.nist.gov/news-events/news/2023/03/nrc-authorizes-restart-nist-research-reactor; https://www.nist.gov/ncnr/news-and-events/facility-news: "The NIST Center for Neutron Research reactor has been shut down since Feb. 3, 2021, when a single fuel element overheated and was damaged because it was not securely latched into place." |
| facility:nist-center-for-neutron-research | reactor_site | active | reactor operations resumed: 2026-05 to open | site:nist-ncnr-gaithersburg | https://www.nist.gov/ncnr/news-and-events/facility-news: "The NCNR resumed reactor operations in May following an extensive repair, maintenance, and upgrade project." |
| facility:triumf | accelerator_laboratory | active | established: 1968 to open | site:triumf-vancouver | https://www.triumf.ca/about: "Established in 1968 in Vancouver, TRIUMF is Canada’s particle accelerator centre." |
| accelerator:cern-ad | synchrotron | shutdown | operation (first physics 2000): 2000 to 2026-08-31 | site:cern-antiproton-decelerator-hall | https://home.cern/science/accelerators/antiproton-decelerator; https://cerncourier.com/a/antiprotons-come-with-all-the-trappings/; https://cerncourier.com/a/getting-up-to-speed-in-the-year-ad-2/; https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/: "Installed in 2000, the AD made the headlines in 2002 when large numbers of antihydrogen atoms were produced for the first time." |
| accelerator:cern-ad | synchrotron | shutdown | Long Shutdown 3 (Antimatter Factory): 2026-08-31 to open | site:cern-antiproton-decelerator-hall | https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/: "CERN’s injector complex and Antimatter Factory took their final steps towards Long Shutdown 3 (LS3) this morning, as the last particle beams were extracted and the machines fell silent." |
| accelerator:elena | synchrotron | shutdown | approved by CERN Council; construction and installation: 2011-06 to 2016-11 | site:cern-antiproton-decelerator-hall | https://home.cern/cern-sets-course-for-extra-low-energy-antiprotons/; https://home.cern/great-progress-across-board/: "Approved by CERN Council in June this year, ELENA is scheduled to deliver its first antiprotons in 2016." |
| accelerator:elena | synchrotron | shutdown | commissioning with beam: 2016-11 to 2018-10 | site:cern-antiproton-decelerator-hall | https://home.cern/great-progress-across-board/; https://home.cern/science/experiments/gbar: "Although this is a vital component, the ring can already be tested with beam, and that’s scheduled to start during the week of 14 November using an independent ion source." |
| accelerator:elena | synchrotron | shutdown | operation for the AD-ELENA experiments: 2018-10 to 2026-08-31 | site:cern-antiproton-decelerator-hall | https://home.cern/science/experiments/gbar; https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/: "GBAR was approved by the CERN Research Board in May 2012 and received its first beam of antiprotons from ELENA in October 2018." |
| accelerator:elena | synchrotron | shutdown | Long Shutdown 3 (Antimatter Factory): 2026-08-31 to open | site:cern-antiproton-decelerator-hall | https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/: "CERN’s injector complex and Antimatter Factory took their final steps towards Long Shutdown 3 (LS3) this morning, as the last particle beams were extracted and the machines fell silent." |
| accelerator:lear | storage_ring | decommissioned | operation: 1982 to 1996 | site:cern-meyrin | https://be-dep-op-leir.web.cern.ch/leir-history; https://cerncourier.com/a/antiprotons-come-with-all-the-trappings/: "Built in 1982, The Low Energy Antiproton Ring (LEAR) decelerated and stored antiprotons for various experiments throughout its 14 year lifetime." |
| accelerator:lear | storage_ring | decommissioned | closed (later converted into LEIR): 1996 to open | site:cern-meyrin | https://be-dep-op-leir.web.cern.ch/leir-history; https://cerncourier.com/a/antiprotons-come-with-all-the-trappings/: "When CERN's low-energy antiproton ring (LEAR) was closed in 1996 after more than 10 years of operation" |
| site:cern-antiproton-decelerator-hall | site (surface) | - | - | 46.233989, 6.046459 (campus, approximate, +/-60 m) on facility:cern | https://www.openstreetmap.org/way/24262953: "OSM way 24262953, timestamp_osm_base 2026-09-18T20:19:03Z; building=university, name "Antiproton Decelerator Hall"" |
| site:j-parc-mlf | site (surface) | - | - | 36.44805, 140.603815 (campus, approximate, +/-100 m) on facility:j-parc | https://www.openstreetmap.org/way/541633717: "OSM way 541633717 "Materials and Life Science Facility", Overpass out geom, timestamp_osm_base 2026-10-26T07:50:21Z" |
| site:nist-ncnr-gaithersburg | site (surface) | - | - | 39.1265629, -77.2183987 (campus, approximate, +/-150 m) on facility:nist-center-for-neutron-research | https://nominatim.openstreetmap.org/search?q=NIST+Center+for+Neutron+Research&format=jsonv2&limit=4: "lat 39.1265629, lon -77.2183987, name 'NIST Center for Neutron Research'" |
| site:triumf-vancouver | site (surface) | - | - | 49.2472455, -123.2295664 (campus, approximate, +/-300 m) on facility:triumf | https://nominatim.openstreetmap.org/search?q=TRIUMF+4004+Wesbrook+Mall+Vancouver&format=jsonv2&limit=3: "lat 49.2472455, lon -123.2295664, display_name 'TRIUMF, 4004, Wesbrook Mall, University of British Columbia" |

### Experiments

One block per experiment; every dated interval and every detector placement carries its URL and quote. Each experiment also has a detector record (same slug unless noted: `detector:alpha` and `detector:alpha-g` for ALPHA) and a collaboration record of the same slug.


#### experiment:aegis: AEgIS

kind `antimatter`, status **shutdown**, tier C, host facility:cern; accelerators: accelerator:cern-ad, accelerator:elena; website: https://home.cern/science/experiments/aegis; collaboration: collaboration:aegis.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| phase 1: apparatus construction, commissioning and proof-of-principle measurements | commissioning (approximate) | 2011-06 to 2018-12 | https://arxiv.org/abs/1106.0209; https://arxiv.org/abs/2208.07050: "under construction at CERN" |
| phase 2: pulsed antihydrogen source and gravity-measurement preparation | active (approximate) | 2018-12 to 2026-08-31 | https://arxiv.org/abs/2208.07050; https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/: "AEgIS re-started its operation on the new CERN ELENA decelerator in late 2021, capturing its first antiprotons and commissioning its new antiproton energy degrading system and hardware/software control systems." |
| Long Shutdown 3 (no antiproton beam) | shutdown (verified) | 2026-08-31 to open | https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/: "CERN’s injector complex and Antimatter Factory took their final steps towards Long Shutdown 3 (LS3) this morning, as the last particle beams were extracted and the machines fell silent." |
| placement of detector:aegis | main at site:cern-antiproton-decelerator-hall (approximate) | 2011-06 to open | https://arxiv.org/abs/1106.0209: "under construction at CERN" |

#### experiment:alpha: ALPHA

kind `antimatter`, status **shutdown**, tier C, host facility:cern; accelerators: accelerator:cern-ad, accelerator:elena; website: https://alpha.web.cern.ch/; collaboration: collaboration:alpha.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| operation (ALPHA 1 from 2005, ALPHA 2 from 2012, ALPHA-g and ALPHA 3 from 2021) | active (verified) | 2005 to 2026-08-31 | https://alpha.web.cern.ch/experiments-alpha; https://home.cern/science/experiments/alpha; https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/: "ALPHA 1 (2005– 2012)" |
| Long Shutdown 3 (no antiproton beam) | shutdown (verified) | 2026-08-31 to open | https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/: "CERN’s injector complex and Antimatter Factory took their final steps towards Long Shutdown 3 (LS3) this morning, as the last particle beams were extracted and the machines fell silent." |
| placement of detector:alpha-g | main at site:cern-antiproton-decelerator-hall (approximate) | 2021 to open | https://alpha.web.cern.ch/experiments-alpha: "ALPHA-g (2021 – present)" |
| placement of detector:alpha | main at site:cern-antiproton-decelerator-hall (approximate) | 2012 to open | https://alpha.web.cern.ch/experiments-alpha: "ALPHA 2 (2012 – present)" |
| lineage | predecessor experiment:athena | - | https://home.cern/science/experiments/alpha |

#### experiment:asacusa: ASACUSA

kind `antimatter`, status **shutdown**, tier C, host facility:cern; accelerators: accelerator:cern-ad; website: https://home.cern/science/experiments/asacusa; collaboration: collaboration:asacusa.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| data taking at the Antiproton Decelerator | active (approximate) | 2000 to 2026-08-31 | https://cerncourier.com/a/antiprotons-come-with-all-the-trappings/; https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/: "This is the motivation behind CERN’s new AD, which supplies antiprotons to several experiments – ATRAP (son of TRAP at LEAR), ATHENA and ASACUSA." |
| Long Shutdown 3 (no antiproton beam) | shutdown (verified) | 2026-08-31 to open | https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/: "CERN’s injector complex and Antimatter Factory took their final steps towards Long Shutdown 3 (LS3) this morning, as the last particle beams were extracted and the machines fell silent." |
| placement of detector:asacusa | main at site:cern-antiproton-decelerator-hall (approximate) | 2000 to open | https://cerncourier.com/a/antiprotons-come-with-all-the-trappings/: "This is the motivation behind CERN’s new AD, which supplies antiprotons to several experiments – ATRAP (son of TRAP at LEAR), ATHENA and ASACUSA." |

#### experiment:athena: ATHENA

kind `antimatter`, status **completed**, tier C, host facility:cern; accelerators: accelerator:cern-ad; website: none; collaboration: collaboration:athena.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| data taking at the Antiproton Decelerator | active (approximate) | 2000 to 2004 | https://cerncourier.com/a/antiprotons-come-with-all-the-trappings/; https://home.cern/science/experiments/atrap: "This is the motivation behind CERN’s new AD, which supplies antiprotons to several experiments – ATRAP (son of TRAP at LEAR), ATHENA and ASACUSA." |
| completed | completed (verified) | 2004 to open | https://home.cern/science/experiments/atrap: "While the ATHENA experiment came to an end in 2004" |
| placement of detector:athena | main at site:cern-antiproton-decelerator-hall (approximate) | 2000 to 2004 | https://cerncourier.com/a/antiprotons-come-with-all-the-trappings/; https://home.cern/science/experiments/atrap: "This is the motivation behind CERN’s new AD, which supplies antiprotons to several experiments – ATRAP (son of TRAP at LEAR), ATHENA and ASACUSA." |

#### experiment:atrap: ATRAP

kind `antimatter`, status **completed**, tier C, host facility:cern; accelerators: accelerator:cern-ad; website: https://home.cern/science/experiments/atrap; collaboration: collaboration:atrap.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| data taking at the Antiproton Decelerator | active (approximate) | 2000 to 2026-08-31 | https://cerncourier.com/a/antiprotons-come-with-all-the-trappings/; https://home.cern/science/experiments/atrap: "This is the motivation behind CERN’s new AD, which supplies antiprotons to several experiments – ATRAP (son of TRAP at LEAR), ATHENA and ASACUSA." |
| completed (true end date not published; upper bound) | completed (uncertain) | 2026-08-31 to open | https://home.cern/science/accelerators/antiproton-decelerator: "Whereas ATRAP and ACE have now completed their experiments." |
| placement of detector:atrap | main at site:cern-antiproton-decelerator-hall (approximate) | 2000 to open | https://cerncourier.com/a/antiprotons-come-with-all-the-trappings/: "This is the motivation behind CERN’s new AD, which supplies antiprotons to several experiments – ATRAP (son of TRAP at LEAR), ATHENA and ASACUSA." |

#### experiment:base: BASE

kind `antimatter`, status **shutdown**, tier C, host facility:cern; accelerators: accelerator:cern-ad, accelerator:elena; website: https://base.web.cern.ch/; collaboration: collaboration:base.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| antiproton runs at the Antiproton Decelerator | active (approximate) | 2014 to 2026-08-31 | https://www.nature.com/articles/nature14861; https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/: "participated in the 2014 antiproton run and contributed to the data collection" |
| Long Shutdown 3 (no antiproton beam) | shutdown (verified) | 2026-08-31 to open | https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/: "CERN’s injector complex and Antimatter Factory took their final steps towards Long Shutdown 3 (LS3) this morning, as the last particle beams were extracted and the machines fell silent." |
| placement of detector:base | main at site:cern-antiproton-decelerator-hall (approximate) | 2014 to open | https://www.nature.com/articles/nature14861: "participated in the 2014 antiproton run and contributed to the data collection" |

#### experiment:deeme: DeeMe

kind `muon_precision`, status **commissioning**, tier C, host facility:j-parc; accelerators: accelerator:j-parc-rcs; website: none; collaboration: collaboration:deeme.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| detector manufacture and H-line construction | construction (approximate) | 2017 to 2022 | https://arxiv.org/abs/1911.07143; https://arxiv.org/abs/2203.07089: "Four tracking detectors have been manufactured in 2017" |
| commissioning (last dated status: March 2022) | commissioning (uncertain) | 2022 to open | https://arxiv.org/abs/2203.07089: "The H-line construction has been completed and it will become ready for commissioning in January 2022." |
| placement of detector:deeme | main at site:j-parc-mlf (approximate) | 2017 to open | https://arxiv.org/abs/1911.07143: "The DeeMe experiment is planned to search for muon-to-electron conversion at J-PARC MLF." |

#### experiment:e821: E821 (BNL muon g-2)

kind `muon_precision`, status **completed**, tier C, host facility:brookhaven-national-laboratory; accelerators: accelerator:ags; website: none; collaboration: collaboration:e821.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| data taking (runs R97 to R01) | active (verified) | 1997 to 2001 | https://arxiv.org/abs/hep-ex/0602035: "obtained in typically 3-4 month annual runs through 2001. In this paper, we indicate the running periods by the labels R97 - R01." |
| completed | completed (verified) | 2001 to open | https://arxiv.org/abs/hep-ex/0602035: "Many people have made important contributions towards the success of E821 over the past twenty years when this experiment was proposed, built and completed." |
| placement of detector:e821 | main at site:bnl-upton-campus (approximate) | 1997 to 2013 | https://arxiv.org/abs/hep-ex/0602035; https://news.fnal.gov/2025/06/muon-g-2-most-precise-measurement-of-muon-magnetic-anomaly/: "In 2013, Brookhaven's magnetic storage ring was transported from Long Island, New York, to Fermilab in Batavia, Illinois." |

#### experiment:gbar: GBAR

kind `antimatter`, status **shutdown**, tier C, host facility:cern; accelerators: accelerator:elena, accelerator:cern-ad; website: https://gbar.web.cern.ch/; collaboration: collaboration:gbar.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| approved by the CERN Research Board | approved (verified) | 2012-05 to 2018-10 | https://home.cern/science/experiments/gbar: "GBAR was approved by the CERN Research Board in May 2012 and received its first beam of antiprotons from ELENA in October 2018." |
| commissioning on ELENA | commissioning (approximate) | 2018-10 to 2022-12 | https://home.cern/science/experiments/gbar; https://home.cern/gbar-joins-anticlub/: "GBAR was approved by the CERN Research Board in May 2012 and received its first beam of antiprotons from ELENA in October 2018." |
| antihydrogen production and measurement preparation | active (approximate) | 2022-12 to 2026-08-31 | https://home.cern/gbar-joins-anticlub/; https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/: "At the end of 2022, during an operation that lasted several days, the GBAR collaboration detected some 20 antihydrogen atoms produced in this way, validating this "in-flight" production method for the first time." |
| Long Shutdown 3 (no antiproton beam) | shutdown (verified) | 2026-08-31 to open | https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/: "CERN’s injector complex and Antimatter Factory took their final steps towards Long Shutdown 3 (LS3) this morning, as the last particle beams were extracted and the machines fell silent." |
| placement of detector:gbar | main at site:cern-antiproton-decelerator-hall (verified) | 2018-10 to open | https://home.cern/science/experiments/gbar: "It operates in the Antiproton Decelerator (AD) Hall, using antiprotons slowed down by the ELENA facility." |

#### experiment:jparc-muon-g-2-edm: J-PARC muon g-2/EDM (E34)

kind `muon_precision`, status **construction**, tier C, host facility:j-parc; accelerators: accelerator:j-parc-rcs; website: https://g-2.kek.jp/; collaboration: collaboration:jparc-muon-g-2-edm.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| proposed to the J-PARC programme advisory committee | proposed (verified) | 2009 to 2019 | https://g-2.kek.jp/overview/: "The experiment was proposed to the J-PARC program advisory committee in 2009." |
| approved (stage-2) and under construction | construction (verified) | 2019 to open | https://g-2.kek.jp/overview/; https://www.j-parc.jp/c/press-release/2026/08/31001874.html: "With positive recommendations from the review committee and PAC, the experiment received the stage-2 status, a final stage of approval, from KEK in 2019." |
| start of the measurement (planned, late 2020s) | planned (verified) | 2028 (planned) to open | https://g-2.kek.jp/overview/: "The international collaboration has been preparing for the experiment aiming to start the experiment in the late 2020s." |
| placement of detector:jparc-muon-g-2-edm | main at site:j-parc-mlf (approximate) | 2022 to open | https://g-2.kek.jp/overview/; https://www.j-parc.jp/c/press-release/2026/08/31001874.html: "the completion of surface muon beamline construction and its first beam delivery in 2022" |

#### experiment:koto-ii: KOTO II

kind `rare_kaon`, status **proposed**, tier C, host facility:j-parc; accelerators: accelerator:j-parc-main-ring; website: https://koto2.kek.jp/; collaboration: collaboration:koto-ii.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| proposal submitted to the J-PARC PAC; Stage-1 status recommended | proposed (verified) | 2024-12-09 to open | https://osksn2.hep.sci.osaka-u.ac.jp/kotoii/; https://koto2.kek.jp/: "Dec 9, 2024 KOTO II proposal (link) was submitted to J-PARC PAC" |
| placement of detector:koto-ii | main at site:j-parc-hadron-hall (approximate) | 2024-12 to open | https://arxiv.org/abs/2501.14827; https://osksn2.hep.sci.osaka-u.ac.jp/kotoii/: "a new experimental area behind the primary beam dump" |
| lineage | predecessor experiment:koto | - | https://arxiv.org/abs/2501.14827 |

#### experiment:muedm: muEDM

kind `muon_precision`, status **proposed**, tier C, host facility:psi; accelerators: accelerator:psi-hipa; website: none; collaboration: collaboration:muedm.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| proposed at PSI; precursor phase in preparation | proposed (approximate) | 2022-01 to open | https://arxiv.org/abs/2201.06561; https://arxiv.org/abs/2409.20050: "We propose the first dedicated muon EDM search employing the frozen-spin technique at the Paul Scherrer Institute (PSI), Switzerland" |
| placement of detector:muedm | main at site:psi-villigen (approximate) | 2022-01 to open | https://arxiv.org/abs/2201.06561: "We propose the first dedicated muon EDM search employing the frozen-spin technique at the Paul Scherrer Institute (PSI), Switzerland" |

#### experiment:mulan: MuLan

kind `muon_precision`, status **completed**, tier C, host facility:psi; accelerators: accelerator:psi-hipa; website: none; collaboration: collaboration:mulan.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| commissioning measurement | commissioning (verified) | 2004 to 2006 | https://arxiv.org/abs/1211.0960: "Letters describing our 2004 commissioning measurement and 20062007 production measurements were published in Refs. [14, 15]." |
| production data taking (R06, R07) | active (verified) | 2006 to 2007 | https://arxiv.org/abs/1211.0960: "Letters describing our 2004 commissioning measurement and 20062007 production measurements were published in Refs. [14, 15]." |
| completed | completed (approximate) | 2007 to open | https://arxiv.org/abs/1211.0960: "Letters describing our 2004 commissioning measurement and 20062007 production measurements were published in Refs. [14, 15]." |
| placement of detector:mulan | main at site:psi-villigen (approximate) | 2004 to 2007 | https://arxiv.org/abs/1211.0960: "The experiment was conducted at the Paul Scherrer Institute using a time-structured, nearly 100%-polarized, surface muon beam" |

#### experiment:muse: MUSE

kind `muon_precision`, status **active**, tier C, host facility:psi; accelerators: accelerator:psi-hipa; website: none; collaboration: collaboration:muse.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| design and construction (lower bound: technical design report) | construction (approximate) | 2017-09 to 2022 | https://arxiv.org/abs/1709.09753; https://arxiv.org/abs/2602.10279: "Submitted on 27 Sep 2017" |
| data taking (beam times from 2022) | active (approximate) | 2022 to open | https://arxiv.org/abs/2602.10279: "The initial operation of the TCPV during MUSE’s 2022 and 2023 beam times used only the" |
| placement of detector:muse | main at site:psi-villigen (approximate) | 2022 to open | https://arxiv.org/abs/2602.10279: "using the Paul Scherrer Institute's PiM1 secondary beamline." |

#### experiment:n2edm: n2EDM

kind `neutron_precision`, status **commissioning**, tier C, host facility:psi; accelerators: accelerator:psi-hipa; website: none; collaboration: collaboration:n2edm.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| under construction at the PSI ultracold neutron source | construction (approximate) | 2021-01 to 2025-11 | https://arxiv.org/abs/2101.08730; https://arxiv.org/abs/2511.06884: "We present the design of a next-generation experiment, n2EDM, currently under construction at the ultracold neutron source at the Paul Scherrer Institute (PSI)" |
| commissioning | commissioning (approximate) | 2025-11 to open | https://arxiv.org/abs/2601.22960; https://arxiv.org/abs/2511.06884: "which is currently being commissioned at the ultracold neutron (UCN) source" |
| placement of detector:n2edm | main at site:psi-villigen (approximate) | 2021-01 to open | https://arxiv.org/abs/2101.08730: "currently under construction at the ultracold neutron source at the Paul Scherrer Institute (PSI)" |
| lineage | predecessor experiment:psi-nedm | - | https://arxiv.org/abs/2101.08730 |

#### experiment:nab: Nab

kind `neutron_precision`, status **commissioning**, tier C, host facility:oak-ridge-national-laboratory; accelerators: accelerator:sns; website: none; collaboration: collaboration:nab.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| design and preparation | proposed (approximate) | 2008-10 to 2018-11 | https://arxiv.org/abs/0810.0251: "The Nab collaboration will perform a precise measurement of 'a', the electron-neutrino correlation parameter, and 'b', the Fierz interference term in neutron beta decay, in the Fundamental Neutron Physics Beamline at the SNS" |
| commissioning and data-collection campaigns | commissioning (approximate) | 2018-11 to open | https://arxiv.org/abs/1811.10047; https://arxiv.org/abs/2511.16678: "The Nab spectrometer is being commissioned at the Fundamental Neutron Physics Beamline at the Spallation Neutron Source at Oak Ridge National Lab." |
| placement of detector:nab | main at site:ornl-sns-complex (approximate) | 2018-11 to open | https://arxiv.org/abs/1811.10047: "The Nab spectrometer is being commissioned at the Fundamental Neutron Physics Beamline at the Spallation Neutron Source at Oak Ridge National Lab." |

#### experiment:nedm-sns: nEDM@SNS

kind `neutron_precision`, status **construction**, tier C, host facility:oak-ridge-national-laboratory; accelerators: accelerator:sns; website: https://nedm.ornl.gov/; collaboration: collaboration:nedm-sns.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| development and design (plans paper, 2007) | proposed (approximate) | 2007-02 to 2018-10 | https://arxiv.org/abs/nucl-ex/0702024: "This experiment, which will be run at the 8.9 A Neutron Line at the Fundamental Neutron Physics Beamline (FNPB) at the Spallation Neutron Source (SNS) at the Oak Ridge National Laboratory" |
| construction | construction (approximate) | 2018-10 to open | https://arxiv.org/abs/1810.03718; https://nedm.ornl.gov/one-page-summary/: "requires five more years to complete construction and commissioning" |
| placement of detector:nedm-sns | main at site:ornl-sns-complex (approximate) | 2018-10 to open | https://nedm.ornl.gov/one-page-summary/: "The nEDM@SNS experiment is now being constructed at SNS’s Fundamental Neutron Physics Beam Line." |

#### experiment:nist-bl1: NIST beam neutron lifetime experiment BL1

kind `neutron_precision`, status **completed**, tier C, host facility:nist-center-for-neutron-research; accelerators: none listed; website: none; collaboration: collaboration:nist-bl1.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| lifetime measurement at NIST (2003 experiment) | active (approximate) | 2003 to 2005 | https://arxiv.org/abs/2506.01682; https://arxiv.org/abs/1309.2623: "It is largely the same as that used to perform the lifetime measurement at NIST in 2003." |
| completed | completed (verified) | 2005 to open | https://arxiv.org/abs/1309.2623: "The most precise determination of the neutron lifetime using the beam method was completed in 2005" |
| placement of detector:nist-bl1 | main at site:nist-ncnr-gaithersburg (approximate) | 2003 to 2005 | https://arxiv.org/abs/2506.01682; https://arxiv.org/abs/1309.2623: "It is largely the same as that used to perform the lifetime measurement at NIST in 2003." |

#### experiment:nist-bl2: NIST beam neutron lifetime experiment BL2

kind `neutron_precision`, status **completed**, tier C, host facility:nist-center-for-neutron-research; accelerators: none listed; website: none; collaboration: collaboration:nist-bl2.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| data taking with the BL2 apparatus | active (approximate) | 2018-07 to 2020-10 | https://arxiv.org/abs/2506.01682: "The data for this work were acquired between July 2018 and October 2020." |
| completed (NCNR reactor shut down 3 February 2021) | completed (approximate) | 2020-10 to open | https://arxiv.org/abs/2506.01682; https://www.nist.gov/news-events/news/2023/03/nrc-authorizes-restart-nist-research-reactor: "The data for this work were acquired between July 2018 and October 2020." |
| placement of detector:nist-bl2 | main at site:nist-ncnr-gaithersburg (approximate) | 2018-07 to 2020-10 | https://arxiv.org/abs/2506.01682: "The apparatus for these studies is part of the BL2 experiment to measure the neutron lifetime" |
| lineage | upgrade_of experiment:nist-bl1 | - | https://arxiv.org/abs/2506.01682 |

#### experiment:nist-bl3: NIST beam neutron lifetime experiment BL3

kind `neutron_precision`, status **construction**, tier C, host facility:nist-center-for-neutron-research; accelerators: none listed; website: none; collaboration: collaboration:nist-bl3.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| funded and under construction | construction (approximate) | 2022 to open | https://agenda.hep.wisc.edu/event/2257/contributions/33839: "The project received funding in 2022 and subsystems are now being developed and constructed." |
| first run at the NCNR (planned) | planned (verified) | 2027 (planned) to open | https://agenda.hep.wisc.edu/event/2257/contributions/33839: "The apparatus will be integrated offline in 2026 and will run at the NIST Center for Neutron Research after the facility returns to operation, expected in 2027." |
| placement of detector:nist-bl3 | main at site:nist-ncnr-gaithersburg (approximate) | 2027 (planned) to open | https://agenda.hep.wisc.edu/event/2257/contributions/33839: "will run at the NIST Center for Neutron Research after the facility returns to operation, expected in 2027" |

#### experiment:pen: PEN

kind `muon_precision`, status **completed**, tier C, host facility:psi; accelerators: accelerator:psi-hipa; website: none; collaboration: collaboration:pen.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| data taking (runs 2008-2010) | active (verified) | 2008 to 2010 | https://arxiv.org/abs/1210.5025: "During runs in 2008-10, PEN has accumulated over 2\times 10^7 \pi_{e2} events" |
| completed | completed (approximate) | 2010 to open | https://arxiv.org/abs/1210.5025: "During runs in 2008-10, PEN has accumulated over 2\times 10^7 \pi_{e2} events" |
| placement of detector:pen | main at site:psi-villigen (approximate) | 2008 to 2010 | https://arxiv.org/abs/1210.5025: "During runs in 2008-10, PEN has accumulated over 2\times 10^7 \pi_{e2} events" |

#### experiment:perkeo-iii: PERKEO III

kind `neutron_precision`, status **active**, tier C, host facility:ill-grenoble; accelerators: none listed; website: https://www.ph.nat.tum.de/ene/research/perkeo-iii/; collaboration: collaboration:perkeo-iii.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| commissioning run (continuous beam) | commissioning (approximate) | 2007 to 2008 | https://www.ph.nat.tum.de/ene/research/perkeo-iii/: "It was commissioned successfully in a first run at the Institute Laue-Langevin (ILL) in 2007." |
| measurement runs at the ILL (2008/2009, 2014/2015, 2019/2020) | active (approximate) | 2008 to open | https://www.ph.nat.tum.de/ene/research/perkeo-iii/: "In 2019 and 2020 we successfully performed a measurement of the beta spectrum with the aim to strongly improve the limits on the Fierz interfernce term b using an unpolarised, pulsed neutron beam." |
| placement of detector:perkeo-iii | main at site:ill-grenoble-reactor-hall (approximate) | 2007 to open | https://www.ph.nat.tum.de/ene/research/perkeo-iii/: "PERKEO III installed at the cold neutron beam line PF1b at the Institut Laue-Langevin, Grenoble, France." |

#### experiment:pienu: PiENu (PIENU)

kind `muon_precision`, status **completed**, tier C, host facility:triumf; accelerators: none listed; website: https://pienu.triumf.ca/; collaboration: collaboration:pienu.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| physics data taking (since 2009) | active (verified) | 2009 to 2012 | https://arxiv.org/abs/1006.0695; https://arxiv.org/abs/1509.08437: "The PIENU experiment is completely operational and taking physics data since 2009." |
| completed | completed (verified) | 2012 to open | https://arxiv.org/abs/1509.08437: "Data taking of the PIENU experiment was completed in 2012" |
| placement of detector:pienu | main at site:triumf-vancouver (approximate) | 2009 to 2012 | https://arxiv.org/abs/1006.0695; https://arxiv.org/abs/1506.05845: "a 75-MeV/c π + beam from the TRIUMF M13 channel" |

#### experiment:pioneer: PIONEER

kind `muon_precision`, status **approved**, tier C, host facility:psi; accelerators: accelerator:psi-hipa; website: https://www.psi.ch/en/pioneer; collaboration: collaboration:pioneer.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| proposal to the PSI programme advisory committee | proposed (approximate) | 2022-03 to 2025-04 | https://arxiv.org/abs/2203.01981: "PIONEER: Studies of Rare Pion Decays" |
| approved at PSI (high priority) | approved (uncertain) | 2025-04 to open | https://arxiv.org/abs/2504.06375; https://www.psi.ch/en/pioneer: "The experiment is approved at the Paul Scherrer Institute (PSI)." |
| placement of detector:pioneer | main at site:psi-villigen (approximate) | 2022 to open | https://www.psi.ch/en/pioneer: "PIONEER will be using the world’s most intense pion beam at PSI" |

#### experiment:ps210: PS210

kind `antimatter`, status **completed**, tier C, host facility:cern; accelerators: accelerator:lear; website: none; collaboration: collaboration:ps210.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| antihydrogen production run on LEAR | active (approximate) | 1995-09 to 1996 | https://home.cern/first-atoms-antimatter-produced-cern/; https://cerncourier.com/a/antiprotons-come-with-all-the-trappings/: "In September 1995, Prof. Walter Oelert and an international team from Jülich IKP-KFA, Erlangen-Nuernberg University, GSI Darmstadt and Genoa University succeeded for the first time in synthesising atoms of antimatter from their constituent antiparticles." |
| completed | completed (approximate) | 1996 to open | https://cerncourier.com/a/antiprotons-come-with-all-the-trappings/: "When CERN's low-energy antiproton ring (LEAR) was closed in 1996 after more than 10 years of operation" |
| placement of detector:ps210 | main at site:cern-meyrin (approximate) | 1995-09 to 1996 | https://home.cern/first-atoms-antimatter-produced-cern/: "In September 1995, Prof. Walter Oelert and an international team from Jülich IKP-KFA, Erlangen-Nuernberg University, GSI Darmstadt and Genoa University succeeded for the first time in synthesising atoms of antimatter from their constituent antiparticles." |

#### experiment:psi-nedm: nEDM experiment at PSI

kind `neutron_precision`, status **completed**, tier C, host facility:psi; accelerators: accelerator:psi-hipa; website: none; collaboration: collaboration:psi-nedm.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| data taking at the PSI ultracold neutron source (2015 to 2017) | active (approximate) | 2015 to 2017 | https://arxiv.org/abs/2001.11966; https://arxiv.org/abs/2101.08730: "A total of 54068 individual measurement cycles, during 2015 and 2016, were used to determine the change in the Larmor precession frequency of the neutron" |
| completed | completed (verified) | 2017 to open | https://arxiv.org/abs/2101.08730: "The project builds on experience gained with the previous apparatus operated at PSI until 2017" |
| placement of detector:psi-nedm | main at site:psi-villigen (approximate) | 2015 to 2017 | https://arxiv.org/abs/2001.11966; https://arxiv.org/abs/2101.08730: "The project builds on experience gained with the previous apparatus operated at PSI until 2017" |
| lineage | upgrade_of experiment:sussex-ral-ill-nedm | - | https://arxiv.org/abs/2101.08730 |

#### experiment:puma: PUMA

kind `antimatter`, status **shutdown**, tier C, host facility:cern; accelerators: accelerator:elena, accelerator:cern-ad; website: https://puma.web.cern.ch/; collaboration: collaboration:puma.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| project start | proposed (verified) | 2018-01 to 2021 | https://puma.web.cern.ch/: "The project began in January 2018, with acceptance as a CERN experiment (AD-09) in 2021" |
| approved as CERN experiment AD-09 | approved (verified) | 2021 to 2024-12 | https://puma.web.cern.ch/; https://home.cern/science/experiments/puma: "PUMA was approved in March 2021 and is expected to begin operation in 2025." |
| installation and commissioning with antiprotons | commissioning (approximate) | 2024-12 to 2026-08-31 | https://puma.web.cern.ch/; https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/: "installation of the primary apparatus since December 2024. Commissioning with antiprotons at the AD is ongoing." |
| Long Shutdown 3 (no antiproton beam) | shutdown (verified) | 2026-08-31 to open | https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/: "CERN’s injector complex and Antimatter Factory took their final steps towards Long Shutdown 3 (LS3) this morning, as the last particle beams were extracted and the machines fell silent." |
| placement of detector:puma | main at site:cern-antiproton-decelerator-hall (verified) | 2024-12 to open | https://puma.web.cern.ch/about: "The whole apparatus is currently installed at the AD Hall, with commissioning with antiprotons ongoing." |

#### experiment:sussex-ral-ill-nedm: ILL neutron EDM experiment (Sussex–RAL–ILL)

kind `neutron_precision`, status **completed**, tier C, host facility:ill-grenoble; accelerators: none listed; website: none; collaboration: collaboration:sussex-ral-ill-nedm.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| data taking at the ILL (1998 to 2002) | active (verified) | 1998 to 2002 | https://arxiv.org/abs/1509.04411: "The data were collected at ILL, Grenoble, between 1998 and 2002." |
| completed | completed (verified) | 2002 to open | https://arxiv.org/abs/1509.04411: "The data were collected at ILL, Grenoble, between 1998 and 2002." |
| placement of detector:sussex-ral-ill-nedm | main at site:ill-grenoble-reactor-hall (approximate) | 1998 to 2002 | https://arxiv.org/abs/hep-ex/0602020; https://arxiv.org/abs/1509.04411: "The data were collected at ILL, Grenoble, between 1998 and 2002." |

#### experiment:tucan: TUCAN

kind `neutron_precision`, status **commissioning**, tier C, host facility:triumf; accelerators: none listed; website: none; collaboration: collaboration:tucan.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| development of the advanced UCN source | construction (approximate) | 2017 to 2024 | https://www.rri.kyoto-u.ac.jp/news-en/20855; https://arxiv.org/abs/2507.05278: "Since then, development has continued on a new, advanced UCN source designed to deliver UCNs at world-leading intensity [3]." |
| commissioning of the source, first UCN production | commissioning (approximate) | 2024 to open | https://arxiv.org/abs/2507.05278; https://www.rri.kyoto-u.ac.jp/news-en/20855; https://triumf.ca/2025/06/30/new-ultracold-neutron-source-produces-record-for-canada/: "Substantial progress in 2024 allowed the collaboration to operate the complete source system, with the exception of the liquid deuterium cold moderator, resulting in the first production of UCNs." |
| placement of detector:tucan | main at site:triumf-vancouver (approximate) | 2024 to open | https://www.rri.kyoto-u.ac.jp/news-en/20855: "FIG. 1: The TRIUMF Meson Hall, where the TUCAN experiment is located." |

#### experiment:twist: TWIST

kind `muon_precision`, status **completed**, tier C, host facility:triumf; accelerators: none listed; website: none; collaboration: collaboration:twist.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| data taking at TRIUMF (data from 2004 onwards) | active (approximate) | 2004 to 2010-10 | https://arxiv.org/abs/0810.3181; https://arxiv.org/abs/1010.4998: "The results presented here supersede those results and are based on an analysis of data taken in 2004" |
| completed | completed (approximate) | 2010-10 to open | https://arxiv.org/abs/1010.4998: "The TWIST Collaboration has completed a new measurement of the energy-angle spectrum of positrons from the decay of highly polarized muons." |
| placement of detector:twist | main at site:triumf-vancouver (approximate) | 2004 to 2010-10 | https://arxiv.org/abs/0810.3181; https://arxiv.org/abs/1010.4998: "The muons from pions that decayed on the surface of the target were transported by the M13 surface muon channel to the detector" |

#### experiment:ucntau: UCNτ

kind `neutron_precision`, status **upgrade**, tier C, host facility:los-alamos-national-laboratory; accelerators: accelerator:lansce; website: none; collaboration: collaboration:ucntau.

| interval | status | start to end | source URL and verbatim quote |
|---|---|---|---|
| data taking with the magneto-gravitational trap (2017 to 2022) | active (approximate) | 2017 to 2022 | https://arxiv.org/abs/2106.10375; https://arxiv.org/abs/2409.05560: "over two data acquisition campaigns in 2017 and 2018" |
| upgrade for the next level of precision | upgrade (uncertain) | 2022 to open | https://agenda.hep.wisc.edu/event/2257/contributions/33856; https://arxiv.org/abs/2409.05560: "an upgrade underway to achieve the next level of precision from the technique will be discussed." |
| placement of detector:ucntau | main at site:lanl-lansce (approximate) | 2017 to open | https://arxiv.org/abs/2106.10375; https://arxiv.org/abs/2409.05560: "Here we publish three years of data for the UCNtau experiment performed at the Los Alamos Ultra Cold Neutron Facility at the Los Alamos Neutron Science Center." |

### Results

| id | experiment | date (kind) | type | publication | claim quote (abstract) |
|---|---|---|---|---|---|
| result:aegis-pulsed-antihydrogen-2021 | experiment:aegis | 2021-02-08 (publication) | technology_milestone | https://www.nature.com/articles/s42005-020-00494-z | "We present here experimental results on the production of antihydrogen in a pulsed mode in which the time when 90% of the atoms are produced is known with an uncertainty of ~250 ns." |
| result:alpha-1s-2s-spectroscopy-2016 | experiment:alpha | 2016-12-19 (publication) | observation | https://www.nature.com/articles/nature21040 | "Here we report the observation of the 1S–2S transition in magnetically trapped atoms of antihydrogen." |
| result:alpha-fine-structure-2020 | experiment:alpha | 2020-02-19 (publication) | measurement | https://www.nature.com/articles/s41586-020-2006-5 | "Here we report measurements of the fine structure in the n = 2 states of antihydrogen, the antimatter counterpart of the hydrogen atom." |
| result:alpha-g-gravity-2023 | experiment:alpha | 2023-09-27 (publication) | measurement | https://www.nature.com/articles/s41586-023-06527-1 | "Here we show that antihydrogen atoms, released from magnetic confinement in the ALPHA-g apparatus, behave in a way consistent with gravitational attraction to the Earth." |
| result:alpha-laser-cooling-2021 | experiment:alpha | 2021-03-31 (publication) | technology_milestone | https://www.nature.com/articles/s41586-021-03289-6 | "Here we demonstrate laser cooling of antihydrogen ... we Doppler-cool a sample of magnetically trapped antihydrogen." |
| result:alpha-resonant-transitions-2012 | experiment:alpha | 2012-03-07 (publication) | measurement | https://www.nature.com/articles/nature10942 | "Here we report spectroscopy of a pure antimatter atom, demonstrating resonant quantum transitions in antihydrogen." |
| result:alpha-trapped-antihydrogen-2010 | experiment:alpha | 2010-11-17 (publication) | technology_milestone | https://www.nature.com/articles/nature09610 | "Here we demonstrate trapping of antihydrogen atoms." |
| result:asacusa-antihydrogen-source-2014 | experiment:asacusa | 2014-01-21 (publication) | technology_milestone | https://www.nature.com/articles/ncomms4089 | "Here we report the development of an antihydrogen source using a cusp trap for in-flight spectroscopy." |
| result:asacusa-antiprotonic-helium-spectroscopy-2011 | experiment:asacusa | 2011-07-27 (publication) | precision_measurement | https://www.nature.com/articles/nature10260 | "By comparing the results with three-body quantum electrodynamics calculations, we derived an antiproton-to-electron mass ratio of 1,836.1526736(23), where the parenthetical error represents one standard deviation." |
| result:athena-cold-antihydrogen-2002 | experiment:athena | 2002-09-18 (publication) | technology_milestone | https://www.nature.com/articles/nature01096 | "Here we demonstrate the production of antihydrogen atoms at very low energy by mixing trapped antiprotons and positrons in a cryogenic environment." |
| result:base-antiproton-charge-to-mass-2015 | experiment:base | 2015-08-12 (publication) | precision_measurement | https://www.nature.com/articles/nature14861 | "Here we report high-precision cyclotron frequency comparisons of a single antiproton and a negatively charged hydrogen ion (H−) carried out in a Penning trap system." |
| result:base-antiproton-magnetic-moment-2017 | experiment:base | 2017-10-19 (publication) | precision_measurement | https://www.nature.com/articles/nature24048 | "Here we report a high-precision measurement of ... in units of the nuclear magneton μN with a fractional precision of 1.5 parts per billion (68% confidence level)." |
| result:e821-final-report-2006 | experiment:e821 | 2006-02-20 (preprint) | precision_measurement | https://arxiv.org/abs/hep-ex/0602035 | "Data obtained at Brookhaven National Laboratory, using nearly equal samples of positive and negative muons, were used to deduce a_mu(Expt) = 11 659 208.0(5.4)(3.3) x 10^-10, where the statistical and systematic uncertainties are given, respectively." |
| result:gbar-antihydrogen-production-2023 | experiment:gbar | 2023-06-27 (preprint) | technology_milestone | https://arxiv.org/abs/2306.15801 | "We report on the first production of an antihydrogen beam by charge exchange of 6.1 keV antiprotons with a cloud of positronium in the GBAR experiment at CERN." |
| result:mulan-detailed-report-2012 | experiment:mulan | 2012-11-05 (preprint) | precision_measurement | https://arxiv.org/abs/1211.0960 | "together the data yield a muon lifetime of tau_{mu}(MuLan) = 2196980.3(2.2) ps (1.0 ppm), thirty times more precise than previous generations of lifetime experiments." |
| result:mulan-fermi-constant-2010 | experiment:mulan | 2010-10-05 (preprint) | precision_measurement | https://arxiv.org/abs/1010.0991 | "We report a measurement of the positive muon lifetime to a precision of 1.0 parts per million (ppm); it is the most precise particle lifetime ever measured." |
| result:nist-bl1-neutron-lifetime-2013 | experiment:nist-bl1 | 2013-09-10 (preprint) | precision_measurement | https://arxiv.org/abs/1309.2623 | "The updated lifetime is $\tau_n = (887.7 \pm 1.2 [\textrm{stat}] \pm 1.9 [\textrm{syst}])$ s." |
| result:nist-bl2-molecular-hydrogen-2025 | experiment:nist-bl2 | 2025-06-02 (preprint) | measurement | https://arxiv.org/abs/2506.01682 | "We demonstrate that charge exchange with molecular hydrogen can occur with trapped protons, and we determine the efficiency with which the molecular hydrogen ions in the trap are detected." |
| result:perkeo-iii-axial-vector-coupling-2019 | experiment:perkeo-iii | 2018-12-11 (preprint) | precision_measurement | https://arxiv.org/abs/1812.04666 | "From the electron spectra we obtain $\lambda = g_A/g_V = -1.27641(45)_\mathrm{stat}(33)_\mathrm{sys}$ which confirms recent measurements with improved precision." |
| result:perkeo-iii-fierz-term-limit-2019 | experiment:perkeo-iii | 2019-11-05 (preprint) | limit | https://arxiv.org/abs/1911.01766 | "We obtain a limit of b = 0.017(21) at 68.27 C.L., improving the previous best limit from neutron decay by a factor of four." |
| result:pienu-r-e-mu-2015 | experiment:pienu | 2015-06-18 (preprint) | precision_measurement | https://arxiv.org/abs/1506.05845 | "A new measurement of the branching ratio, ... This is in agreement with the standard model prediction and improves the test of electron-muon universality to the level of 0.1 %." |
| result:ps210-antihydrogen-production-1996 | experiment:ps210 | 1996-01-04 (announcement) | observation | https://infoscience.epfl.ch/record/208922 | "The production of eleven antihydrogen atoms is reported including possibly 2 ± 1 background signals, the observed yield agrees with theoretical predictions." |
| result:psi-nedm-neutron-edm-2020 | experiment:psi-nedm | 2020-01-31 (preprint) | measurement | https://arxiv.org/abs/2001.11966 | "The measured value of the neutron EDM is $d_{\rm n} = (0.0\pm1.1_{\rm stat}\pm0.2_{\rm sys})\times10^{-26}e\,{\rm cm}$." |
| result:sussex-ral-ill-nedm-limit-2006 | experiment:sussex-ral-ill-nedm | 2006-02-09 (preprint) | limit | https://arxiv.org/abs/hep-ex/0602020 | "The overall results may be interpreted as an upper limit on the absolute value of the neutron EDM of \|d_n\| < 2.9 x 10^{-26} e cm (90% CL)." |
| result:sussex-ral-ill-nedm-revised-limit-2015 | experiment:sussex-ral-ill-nedm | 2015-09-15 (preprint) | limit | https://arxiv.org/abs/1509.04411 | "We obtain a net result of ... which may be interpreted as a slightly revised upper limit on the magnitude of the EDM of" |
| result:twist-muon-decay-parameters-2010 | experiment:twist | 2010-10-24 (preprint) | precision_measurement | https://arxiv.org/abs/1010.4998 | "A simultaneous measurement of the muon decay parameters {\rho}, {\delta}, and (P_{\mu}){\xi} tests the Standard Model (SM) in a purely leptonic process and provides improved limits for relevant extensions to the SM." |
| result:ucntau-lifetime-2018 | experiment:ucntau | 2017-07-06 (preprint) | precision_measurement | https://arxiv.org/abs/1707.01817 | "the lifetime reported here (877.7 $\pm$ 0.7 (stat) +0.4/-0.2 (sys) s) is the first modern measurement of $\tau_n$ that does not require corrections larger than the quoted uncertainties." |
| result:ucntau-lifetime-2021 | experiment:ucntau | 2021-06-18 (preprint) | precision_measurement | https://arxiv.org/abs/2106.10375 | "Both techniques achieve consistent results and find a value $\tau_{n}=877.75\pm0.28_{\text{ stat}}+0.22/-0.16_{\text{ syst}}$~s." |
| result:ucntau-lifetime-final-2024 | experiment:ucntau | 2024-09-09 (preprint) | precision_measurement | https://arxiv.org/abs/2409.05560 | "when all the data from UCNtau are averaged we report an updated value for the lifetime of 877.82+/-0.22 (statistical)+0.20-0.17 (systematic) s." |

### Documents and topics

- document:jparc-muon-g-2-edm-new-approach-2019 (physics_paper, 2019-01): https://arxiv.org/abs/1901.03047
- document:muse-tdr-2017 (technical_design_report, 2017-09): https://arxiv.org/abs/1709.09753
- document:pioneer-proposal-2022 (technical_proposal, 2022-03): https://arxiv.org/abs/2203.01981
- document:puma-design-2022 (conceptual_design_report, 2022): https://link.springer.com/article/10.1140/epja/s10050-022-00713-x
- topic:antimatter (parent topic:precision-and-rare-processes): sources https://home.cern/science/accelerators/antiproton-decelerator; https://www.nature.com/articles/nature21040; https://www.nature.com/articles/s41586-023-06527-1; https://www.nature.com/articles/nature24048
- topic:neutron-physics (parent topic:precision-and-rare-processes): sources https://arxiv.org/abs/1105.3694; https://arxiv.org/abs/2001.11966; https://arxiv.org/abs/2106.10375; https://arxiv.org/abs/1710.02504

### Sources

102 source records were added (`src:precision-2-*`); existing records were reused by URL (for example `src:currency-cern-all-accelerators-2026-08-31`, `src:geo-cern-osm-ad-hall`, `src:muons-news-fnal-2025-final-result`, `src:topic-review-chupp-2019-electric-dipole-moments`). Every quote and every source excerpt was checked verbatim against the fetched page (see the checks section).


## Conflicts

| claim | source A | source B | chosen | why |
|---|---|---|---|---|
| Is ATRAP still running? | CERN's older ATRAP page: "While the ATHENA experiment came to an end in 2004, ATRAP is still in operation." | CERN's AD page: "Whereas ATRAP and ACE have now completed their experiments." (undated) | `completed`, with no real end date | The AD page also mentions ELENA, so it is the later statement. The completed interval starts at 2026-08-31 as an explicit UPPER BOUND (confidence `uncertain`); the true end of ATRAP data taking is unknown. |
| How many antihydrogen atoms did PS210 make? | CERN press release, 4 January 1996: nine atoms | PS210 collaboration summary abstract (Hyperfine Interact. 109, 191, 1997): "eleven antihydrogen atoms ... including possibly 2 ± 1 background signals" | Both recorded; the collaboration's own wording is the result claim | The Physics Letters B abstract could not be fetched verbatim (ScienceDirect and CDS blocked). |
| MuLan G_F | PRL 106, 041803 (arXiv:1010.0991): 1.1663788(7) x 10^-5 GeV^-2 (0.6 ppm) | Detailed report PRD 87, 052003 (arXiv:1211.0960): 1.1663787(6) x 10^-5 GeV^-2 (0.5 ppm) | Two result records, one per paper | The later report supersedes the first number; both are the collaboration's own. |
| TUCAN's first ultracold neutrons | arXiv:2507.05278 v4 (July 2026): first UCN production after progress "in 2024" | KURNS and TRIUMF news: record-setting production on 13 June 2025 | Commissioning interval starts 2024 (approximate); the 13 June 2025 run is in its note | The record run is a later, better-documented event than the first production. |
| When will BL3 run? | BL3 collaboration (CIPANP, June 2025): run at the NCNR "after the facility returns to operation, expected in 2027" | NIST facility news (updated 12 August 2026): "The NCNR resumed reactor operations in May" (2026) | Both recorded (BL3 planned interval 2027; NCNR active from 2026-05) | They are consistent: the reactor is back earlier than the abstract expected; no later BL3 schedule was found. |
| Which NIST experiment gave the 2013 lifetime? | The brief lists BL2/BL3 | arXiv:1309.2623 re-analyses the 2003-2005 measurement, which a 2025 paper calls BL1 | The 2013 result is attached to a new `experiment:nist-bl1` (predecessor of BL2) | BL2 has no published lifetime result; its dated data (July 2018 to October 2020) support a 2025 systematics paper. |
| PEN's decay channel | (the stream brief described PEN as pion beta decay) | arXiv:1210.5025: PEN measures the pi+ -> e+ nu(gamma) branching ratio; pion beta decay was PIBETA | PEN recorded as a pi -> e nu experiment | Primary source. |
| PIONEER approval date | PSI page: "accepted as a high priority experiment" (undated) | arXiv:2504.06375 (April 2025): "The experiment is approved at the Paul Scherrer Institute" | `approved` from 2025-04 as an UPPER BOUND | No fetched source gives the approval day. |

## Unresolved fields

Collected from the coverage rows (`missing_fields`); the common gaps are:

* **Collaboration records:** no source gave a formation date, a membership count or leadership for any new collaboration, so
  every `formation` is null with a note and no `membership` or `leadership` is recorded. No membership roster files were written
  (not fetchable and small).
* **INSPIRE experiment records:** not queried by rule; `external.inspire_experiment` is empty on every experiment, which is why no
  record is tier A or B.
* **Hall-level coordinates:** none. All sites are campus-grade `approximate` points. The two OpenStreetMap-derived points
  (`site:cern-antiproton-decelerator-hall` and `site:j-parc-mlf`) are building-footprint centroids computed on 2026-10-26; the
  TRIUMF and NCNR points are Nominatim results.
* **Approval dates:** not found for ALPHA, AEgIS, ASACUSA, ATHENA, ATRAP, BASE (the first BASE antiproton run is 2014), MUSE,
  nEDM@SNS, TUCAN, Nab and the other experiments that carry a "lower bound" start.
* **Official websites:** none reachable or none found for E821 (SSL certificate failure on g-2.bnl.gov), MuLan, MUSE, PEN (SSL
  failure on galileo.phys.virginia.edu), the PSI nEDM, n2EDM, TUCAN (DNS failure), the NIST experiments, UCNtau, Nab, DeeMe,
  TWIST (timeout) and muEDM. The AEgIS and ASACUSA experiment sites need JavaScript or a CERN login, so the CERN experiment pages
  are used as the official pages.
* **Status after the last dated source:** DeeMe (March 2022), UCNtau upgrade (June 2025), BL3 (June 2025), PERKEO III (analysis of
  2019-2020 runs), PUMA (undated page), E34 beyond the August 2026 press release, muEDM (September 2024).
* **Results not recorded because no abstract could be quoted:** ATRAP's 2002 papers (APS blocks fetches), the original PS210
  Physics Letters B abstract (the 1997 collaboration summary is used instead), the final MuCap paper, the Nab early results
  mentioned in arXiv:2511.16678.
* **Warnings left in the validator output (10, all intrinsic):** `experiment-without-active-beam` on `experiment:pienu`,
  `experiment:twist`, `experiment:sussex-ral-ill-nedm`, `experiment:nist-bl1`, `experiment:nist-bl2` and `experiment:perkeo-iii` (no
  TRIUMF cyclotron record exists, and reactors are not accelerators or beamlines in the Atlas), and `coordinate-kind-approximate` on
  `site:cern-antiproton-decelerator-hall`, `site:j-parc-mlf`, `site:nist-ncnr-gaithersburg` and `site:triumf-vancouver` (campus-grade
  points, by design under A23).

## Candidates considered and excluded (or not added)

| candidate | decision | reason and source |
|---|---|---|
| ACE (Antiproton Cell Experiment, AD-4) | excluded | Biomedical study of antiprotons for cancer therapy, outside A26's high-energy physics scope. CERN: "The Antiproton Cell Experiment (ACE) started in 2003 and was completed in 2013." (https://home.cern/science/experiments/ace) |
| PAX (antiProtonic Atom X-ray spectroscopy), first user of the AD's TELMAX test beamline | not added | No published physics result and no design report found; CERN news of 6 June 2025 describes it as the first user of TELMAX (https://home.cern/antiprotons-test-standard-model/). |
| BASE-STEP (transportable antiproton trap) | folded into `experiment:base` | CERN's BASE page treats it as a BASE development; the 5 June 2025 TELMAX news item lists it as a separate permanent AD experiment, but it has no results of its own. |
| TRAP (LEAR, predecessor of ATRAP), CPLEAR (LEAR), other LEAR-era experiments | not added | CERN's ATRAP page names TRAP as ATRAP's predecessor, but no start or end date was found in a fetchable source; CPLEAR and the LEAR hadron experiments belong to the flavour and hadron streams. LEAR itself exists because of PS210. |
| HIKE (CERN high-intensity kaon programme) | excluded | Not approved: "the decision not to continue CERN's kaon programme with the proposed HIKE experiment" (CERN Courier, 7 November 2025, https://cerncourier.com/mainz-muses-on-future-of-kaon-physics/). Its proposal is arXiv:2311.08231. |
| BL3 conceptual design report (2021) | not used | Cited by the BL2 paper as "unpublished" (arXiv:2506.01682). BL3 itself is included on the strength of the collaboration's June 2025 abstract. |
| MuCap, MuSun, FAST (PSI) | not added | MuCap's 2007 abstract (arXiv:0704.2072) and 2004 data set are citable, but the end of data taking and the final published result were not found in a fetched source. |
| SINDRUM I and II (PSI), MuSEUM (J-PARC), LEMING, Mu-MASS, MACE, PRISM, MICE, muX | not added | Not researched in the time available; none is excluded on scientific grounds. |
| CERN muon g-2 experiments (CERN I to III) | not added | Not researched; their results appear in the E821 report's Table I. |
| UCNA (LANL), aSPECT (ILL/Mainz), abBA, BRAND (ESS), PERC (MLZ), NNBAR/HIBEAM (ESS) | not added | UCNA's results are citable (arXiv:1210.7048, arXiv:1712.00884) but its run dates were not found in a fetched source; the others need a new facility record (MLZ, ESS) and were not researched. |
| CERN Greybook | not used | The Greybook is a JavaScript application with no static text. |

## For the integrator

* `accelerator:ps` should list `accelerator:cern-ad` in `feeds_accelerator_ids` (the AD page: "A proton beam coming from the PS (Proton Synchrotron) is fired into a block of metal"). This stream did not edit `accelerator:ps`.
* `experiment:muon-g-2` should gain a lineage row `predecessor: experiment:e821` (its record says E821 had no record yet; the ring was moved to Fermilab in 2013). This stream did not edit the muon-g-2 record.
* `experiment:koto-ii` carries a `predecessor` row to `experiment:koto` (the KOTO II proposal: "The experiment is a successor to the KOTO experiment"); nothing to edit on KOTO.
* `geometry:antiproton-decelerator-hall` is a context feature with `entity_id: null` (its method text says no AD record existed); it can now point at `accelerator:cern-ad`. `site:cern-antiproton-decelerator-hall` uses the same OSM footprint.
* `map:j-parc` says the MLF and the muon g-2/EDM experiment have no atlas entities; `site:j-parc-mlf`, `experiment:jparc-muon-g-2-edm` and `experiment:deeme` now exist and could be drawn (the MLF building is OSM way 541633717 "Materials and Life Science Facility", extracted 2026-10-26 via Overpass).
* `facility:psi`, `facility:ill-grenoble` and `facility:oak-ridge-national-laboratory` could add `topic:neutron-physics` to their `topic_ids` (owned elsewhere).
* PUMA will move to ISOLDE; the Atlas has no ISOLDE site, so the placement is the AD hall only.
* No `accelerator:triumf` record exists; PiENu, TWIST and TUCAN therefore list no accelerator, which is the cause of two of the intrinsic `experiment-without-active-beam` warnings.
* Bundle size: `atlas.json` is 1,137,570 bytes after this stream alone (budget warning at 400 KB, build failure above 1.5 MB); merging the other coverage-wave streams may approach the limit.
* The Atlas has no source type for a conference abstract; the BL3 and UCNtau CIPANP 2025 abstracts are typed `project_document` (rank 9).
* The coordinates of `site:cern-antiproton-decelerator-hall` and `site:j-parc-mlf` rest on OpenStreetMap (rank 11) and those of TRIUMF and the NCNR on Nominatim (rank 8); all are `approximate` campus points and none is the sole support of a `verified` value.

## Checks run

* `python -m hepgraph.atlas.validate`: 0 errors on the whole Atlas; this stream's files carry the 10 intrinsic warnings listed above and nothing else.
* `python -m hepgraph.atlas.build`: succeeded (81 files, atlas.json 1,137,570 bytes); `static/atlas/generated` was reverted before every commit.
* Quote check: every `quote` in every new file was confirmed verbatim, or as `segments` for quotes joined by an ellipsis, against the page it cites, by `scripts/atlas_quote_check.py` run over the files this branch changed (about 425 quotes, none failing); every source excerpt was checked against its page by a companion script. The only items not fetched are geocoder and OpenStreetMap sources (skipped by the checker); their coordinates carry a `locator`, and the geocoder records quote the Nominatim result line.
* `pytest -q`: 689 passed, 139 skipped (PostgreSQL-backed tests skip without a throwaway database).

