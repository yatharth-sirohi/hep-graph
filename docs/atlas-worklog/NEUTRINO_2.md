# neutrino-2 worklog (coverage wave, neutrino and nucleon-decay experiments)

Branch `atlas-c4-neutrino`, worktree `~/Desktop/HEP-Graph-ar-c4-neutrino`. Owner tag `neutrino-2`; registry rows in `data/atlas/coverage/neutrino-2.json`; topic in `data/atlas/topics/neutrino-2.json`.

## Scope and outcome

Brief: the neutrino and nucleon-decay experiments the Atlas lacked (reactor, accelerator, atmospheric/nucleon decay, solar, double-beta decay, direct neutrino mass, telescopes) plus `topic:nucleon-decay`. **The stream stopped at a usage limit before it was finished.** Done to the full mandatory bar (experiment, detector, collaboration, located site on a facility, sourced intervals, headline result where a primary paper was retrievable, registry row): 18 experiments. Not started (queued as `researched: "none"` rows so the registry is honest): 23 candidates, listed under "Not done". One candidate was examined and excluded (HUNT).

Method: every quote in the data files was written through a helper that fetched the cited source today and refused any quote that was not verbatim (the same normaliser as `scripts/atlas_quote_check.py`); records were then re-checked with that script (`--only <slug>`): all quotes verbatim except one that the script could not refetch (news.fnal.gov timed out; the quote was verified when written). The helper library and scratch files lived in the session scratch directory and were lost when it was cleared, so this log was rebuilt from the committed records and the session notes.

Subagents: the first attempt to spawn research agents hit the concurrent-subagent limit and a later attempt was declined, so all research was done directly by this stream. No child output exists to re-check.

## Entities written

| type | count | ids |
|---|---|---|
| facilities | 9 | angra-npp, bugey-npp, european-spallation-source, kalinin-npp, palo-verde-ngs, sck-cen-mol, sm-3-reactor-dimitrovgrad, taishan-npp, trident-south-china-sea-site |
| sites | 12 | angra-npp-connie-container, bugey-npp-detector-halls, ess-lund, hanbit-neos-tendon-gallery, kalinin-npp-reactor-building, ornl-hfir, palo-verde-ngs-detector-laboratory, sck-cen-br2-reactor-hall, sm-3-reactor-riar-dimitrovgrad, taishan-npp-tao-basement, trident-south-china-sea-abyssal-plain, zinkgruvan-mine-essnusb-far-detector |
| experiments | 18 | annie, argoneut, bugey, ccfr, chooz, connie, danss, essnusb, jinping-neutrino-experiment, juno-tao, neos, neutrino-4, nutev, palo-verde, prospect, solid, stereo, trident |
| detectors | 19 | annie-detector, argoneut-detector, bugey-detector, ccfr-detector, chooz-detector, connie-detector, danss-detector, essnusb-far-detector, essnusb-near-detector, jinping-neutrino-experiment-detector, juno-tao-detector, neos-detector, neutrino-4-detector, nutev-detector, palo-verde-detector, prospect-antineutrino-detector, solid-detector, stereo-detector, trident-detector |
| collaborations | 17 | annie, argoneut, bugey, ccfr, chooz, connie, danss, essnusb, jinping-neutrino-experiment, neos, neutrino-4, nutev, palo-verde, prospect, solid, stereo, trident |
| results | 21 | annie-first-lappd-beam-neutrinos-2025, argoneut-first-argon-cc-cross-sections-2012, ccfr-strange-quark-content-1995, ccfr-structure-functions-2001, chooz-initial-results-1997, chooz-limits-1999, connie-2019-data-limits-2022, connie-first-results-2019, danss-sterile-neutrino-exclusion-2018, neos-reno-joint-sterile-search-2022, neos-sterile-neutrino-search-2017, neutrino-4-first-oscillation-effect-2018, neutrino-4-results-2021, nutev-weak-mixing-angle-2002, palo-verde-final-results-2001, palo-verde-initial-results-2000, prospect-final-sterile-search-2025, prospect-first-oscillation-search-2018, solid-very-short-baseline-search-2024, stereo-179-days-sterile-neutrino-limits-2020, stereo-235u-spectrum-sterile-rejection-2023 |
| topics | 1 | neutrino-2 |
| sources | 72 | 72 source records (listed under Sources added) |
| coverage | 1 | neutrino-2 |

New facilities: `facility:angra-npp`, `facility:bugey-npp`, `facility:european-spallation-source`, `facility:kalinin-npp`, `facility:palo-verde-ngs`, `facility:sck-cen-mol`, `facility:sm-3-reactor-dimitrovgrad`, `facility:taishan-npp`, `facility:trident-south-china-sea-site`.

## Sources added

| id | type | URL |
|---|---|---|
| `src:annie-2025-first-lappd-beam-neutrinos` | arxiv | https://arxiv.org/abs/2508.11111 |
| `src:annie-fnal-feature-2020-first-neutrinos` | official_facility_site | https://news.fnal.gov/2020/03/innovative-annie-sees-first-neutrinos-with-more-firsts-to-come/ |
| `src:annie-fnal-pac-2017-physics-proposal` | arxiv | https://arxiv.org/abs/1707.08222 |
| `src:annie-loi-2015` | arxiv | https://arxiv.org/abs/1504.01480 |
| `src:annie-official-site` | official_experiment_site | https://annie.fnal.gov/ |
| `src:argoneut-analysis-muons-2012` | arxiv | https://arxiv.org/abs/1205.6702 |
| `src:argoneut-jinst-2012-detector` | arxiv | https://arxiv.org/abs/1205.6747 |
| `src:argoneut-prl-2012-cc-cross-sections` | arxiv | https://arxiv.org/abs/1111.0103 |
| `src:bugey-mention-2011-reactor-antineutrino-anomaly` | arxiv | https://arxiv.org/abs/1101.2755 |
| `src:bugey-review-2000-reactor-oscillations` | arxiv | https://arxiv.org/abs/nucl-ex/0005002 |
| `src:bugey-rmp-2002-reactor-oscillation-experiments` | arxiv | https://arxiv.org/abs/hep-ph/0107277 |
| `src:ccfr-nevis-about` | official_experiment_site | https://www.nevis.columbia.edu/ccfr/intro.html |
| `src:ccfr-nevis-history-lab-e` | official_experiment_site | https://www.nevis.columbia.edu/ccfr/history.html |
| `src:ccfr-nevis-home` | official_experiment_site | https://www.nevis.columbia.edu/ccfr/index.html |
| `src:ccfr-prl-2001-structure-functions` | arxiv | https://arxiv.org/abs/hep-ex/0009041 |
| `src:ccfr-zphysc-1995-strange-quark` | arxiv | https://arxiv.org/abs/hep-ex/9406007 |
| `src:chooz-hepex0301017` | arxiv | https://arxiv.org/abs/hep-ex/0301017 |
| `src:chooz-hepex9711002` | arxiv | https://arxiv.org/abs/hep-ex/9711002 |
| `src:chooz-hepex9907037` | arxiv | https://arxiv.org/abs/hep-ex/9907037 |
| `src:connie-jhep-2020-light-mediators` | arxiv | https://arxiv.org/abs/1910.04951 |
| `src:connie-jhep-2022-2019-data` | arxiv | https://arxiv.org/abs/2110.13033 |
| `src:connie-jinst-2016-engineering-run` | arxiv | https://arxiv.org/abs/1604.01343 |
| `src:connie-prd-2019-exploring-low-energy` | arxiv | https://arxiv.org/abs/1906.02200 |
| `src:danss-jinst-2016-detector` | arxiv | https://arxiv.org/abs/1606.02896 |
| `src:danss-plb-2018-sterile-search` | arxiv | https://arxiv.org/abs/1804.04046 |
| `src:danss-recent-results-2019` | arxiv | https://arxiv.org/abs/1911.10140 |
| `src:danss-review-reactor-anomalies-2021` | arxiv | https://arxiv.org/abs/2109.13541 |
| `src:essnusb-cdr-2022` | arxiv | https://arxiv.org/abs/2206.01208 |
| `src:essnusb-ess-beam-on-dump-2025` | press_release | https://news.cision.com/european-spallation-source-eric/r/ess-achieves-beam-on-dump--accelerator-commissioning-underway,c4151601 |
| `src:essnusb-ess-story-page` | official_facility_site | https://europeanspallationsource.se/ess-mandate/ess-story |
| `src:geo-bugey-nominatim-cnpe` | geocoder | https://nominatim.openstreetmap.org/search?q=CNPE+du+Bugey&format=jsonv2&limit=1 |
| `src:geo-connie-nominatim-angra` | geocoder | https://nominatim.openstreetmap.org/search?q=Central+Nuclear+Almirante+%C3%81lvaro+Alberto&format=jsonv2&limit=1 |
| `src:geo-danss-nominatim-kalinin-npp` | geocoder | https://nominatim.openstreetmap.org/search?q=%D0%9A%D0%B0%D0%BB%D0%B8%D0%BD%D0%B8%D0%BD%D1%81%D0%BA%D0%B0%D1%8F+%D0%90%D0%AD%D0%A1&format=jsonv2&limit=1 |
| `src:geo-essnusb-nominatim-ess` | geocoder | https://nominatim.openstreetmap.org/search?q=European+Spallation+Source+Lund&format=jsonv2&limit=1 |
| `src:geo-essnusb-nominatim-zinkgruvan` | geocoder | https://nominatim.openstreetmap.org/search?q=Zinkgruvan&format=jsonv2&limit=1 |
| `src:geo-juno-tao-nominatim-taishan` | geocoder | https://nominatim.openstreetmap.org/search?q=Taishan+Nuclear+Power+Plant&format=jsonv2&limit=1 |
| `src:geo-neutrino-4-nominatim-riar` | geocoder | https://nominatim.openstreetmap.org/search?q=%D0%9D%D0%98%D0%98+%D0%B0%D1%82%D0%BE%D0%BC%D0%BD%D1%8B%D1%85+%D1%80%D0%B5%D0%B0%D0%BA%D1%82%D0%BE%D1%80%D0%BE%D0%B |
| `src:geo-palo-verde-nominatim-pvngs` | geocoder | https://nominatim.openstreetmap.org/search?q=Palo+Verde+Nuclear+Generating+Station&format=jsonv2&limit=1 |
| `src:geo-solid-nominatim-br2` | geocoder | https://nominatim.openstreetmap.org/search?q=BR2+reactor+Mol&format=jsonv2&limit=1 |
| `src:geo-test-hfir3` | openstreetmap | https://overpass-api.de/api/interpreter?data=%5Bout%3Ajson%5D%5Btimeout%3A25%5D%3B%28nwr%5B%22name%22~%22HFIR%7CIsotope%7CReactor%7COak%20Ridge%20National%22%2C |
| `src:jinping-1-ton-prototype-design-2017` | arxiv | https://arxiv.org/abs/1703.01478 |
| `src:jinping-cpc-2017-physics-prospects` | arxiv | https://arxiv.org/abs/1602.01733 |
| `src:jinping-official-site` | official_experiment_site | https://jinping.hep.tsinghua.edu.cn/ |
| `src:juno-tao-cdr-2020` | arxiv | https://arxiv.org/abs/2005.08745 |
| `src:juno-tao-iaea-2025-status` | project_document | https://conferences.iaea.org/event/402/contributions/35152/attachments/18939/32006/TAO_IAEA_250407.pdf |
| `src:neos-aap2018-proceedings` | arxiv | https://arxiv.org/abs/1911.06834 |
| `src:neos-iaea-2023-neos-ii-status` | project_document | https://conferences.iaea.org/event/337/contributions/26550/attachments/13789/22569/Seo_NEOS_IAEA_meeting_2023.pdf |
| `src:neos-prd-2022-neos-ii` | arxiv | https://arxiv.org/abs/2011.00896 |
| `src:neos-prl-2017-sterile-search` | arxiv | https://arxiv.org/abs/1610.05134 |
| `src:neos-review-sterile-2020` | arxiv | https://arxiv.org/abs/2001.03349 |
| `src:neutrino-4-jetpl-2019-first-observation` | arxiv | https://arxiv.org/abs/1809.10561 |
| `src:neutrino-4-prd-2021-results` | arxiv | https://arxiv.org/abs/2003.03199 |
| `src:neutrino-4-prd-2021-search` | arxiv | https://arxiv.org/abs/2005.05301 |
| `src:nutev-prl-2002-weak-mixing-angle` | arxiv | https://arxiv.org/abs/hep-ex/0110059 |
| `src:palo-verde-prd-2000-results` | arxiv | https://arxiv.org/abs/hep-ex/0003022 |
| `src:palo-verde-prd-2001-final` | arxiv | https://arxiv.org/abs/hep-ex/0107009 |
| `src:palo-verde-prl-2000-search` | arxiv | https://arxiv.org/abs/hep-ex/9912050 |
| `src:prospect-jphysg-2016-physics-program` | arxiv | https://arxiv.org/abs/1512.02202 |
| `src:prospect-nim-2019-detector` | arxiv | https://arxiv.org/abs/1808.00097 |
| `src:prospect-official-site` | official_experiment_site | https://prospect.yale.edu/ |
| `src:prospect-ornl-hfir-page` | official_facility_site | https://neutrons.ornl.gov/hfir |
| `src:prospect-prd-2021-improved-search` | arxiv | https://arxiv.org/abs/2006.11210 |
| `src:prospect-prl-2018-first-search` | arxiv | https://arxiv.org/abs/1806.02784 |
| `src:prospect-prl-2025-final-sterile-search` | arxiv | https://arxiv.org/abs/2406.10408 |
| `src:solid-jinst-2021-detector` | arxiv | https://arxiv.org/abs/2002.05914 |
| `src:solid-prd-2025-vsb-oscillation-search` | arxiv | https://arxiv.org/abs/2407.14382 |
| `src:stereo-jinst-2018-experiment` | arxiv | https://arxiv.org/abs/1804.09052 |
| `src:stereo-nature-2023-235u-spectrum` | arxiv | https://arxiv.org/abs/2210.07664 |
| `src:stereo-prd-2020-179-days` | arxiv | https://arxiv.org/abs/1912.06582 |
| `src:topic-nucleon-decay-nath-perez-2007-proton-stability` | arxiv | https://arxiv.org/abs/hep-ph/0601023 |
| `src:topic-nucleon-decay-superk-2020-p-to-epi0-mupi0` | arxiv | https://arxiv.org/abs/2010.16098 |
| `src:trident-natastron-2023-design` | arxiv | https://arxiv.org/abs/2207.04519 |

## Experiments: status, intervals and the evidence behind each date

### CHOOZ (`experiment:chooz`, kind `reactor_neutrino`, status `completed`, tier D)

Facility: facility:chooz; site(s): site:double-chooz-far-detector.

| interval | status | start | end | confidence | source | quote |
|---|---|---|---|---|---|---|
| data taking | active | 1997-03-12 | 1998-07-20 | verified | https://arxiv.org/abs/hep-ex/0301017 | The data acquisition period extended over 450 days, from 12 March 1997 till 20 July 1998 |
| completed | completed | 1998-07-20 | None | verified | https://arxiv.org/abs/hep-ex/0301017 | The data acquisition period extended over 450 days, from 12 March 1997 till 20 July 1998 |

### STEREO (`experiment:stereo`, kind `reactor_neutrino`, status `completed`, tier D)

Facility: facility:ill-grenoble; site(s): site:ill-grenoble-reactor-hall.

| interval | status | start | end | confidence | source | quote |
|---|---|---|---|---|---|---|
| installation and phase-I data taking | active | 2016-11 | 2020-11 | verified | https://arxiv.org/abs/1804.09052 | After its installation in November 2016, the Stereo detector recorded data over 2 reactor cycles |
| completed | completed | 2020-11 | None | verified | https://arxiv.org/abs/2210.07664 | until the experiment was shut down in November 2020 |

### NEOS (`experiment:neos`, kind `reactor_neutrino`, status `completed`, tier D)

Facility: facility:yonggwang-hanbit-reactor-site; site(s): site:hanbit-neos-tendon-gallery.

| interval | status | start | end | confidence | source | quote |
|---|---|---|---|---|---|---|
| NEOS phase I data taking | active | summer 2015 | 2016-05 | approximate | https://arxiv.org/abs/1911.06834 | NEOS phase I data taken from summer 2015 to spring 2016 at Hanbit power plant in ROK |
| detector removed during reactor inspection | shutdown | 2016-05 | 2018-09 | verified | https://arxiv.org/abs/1911.06834 | In May 2016, NEOS detector was paused and removed from tendon gallery due to reactor regular inspection. |
| NEOS-II data taking (one full fuel cycle) | active | 2018-09 | 2020-10 | verified | https://conferences.iaea.org/event/337/contributions/26550/attachments/13789/22569/Seo_NEOS_IAEA_meeting_2023.pdf | NEOS-II (Sept. 2018 – Oct. 2020) |
| completed | completed | 2020-10 | None | approximate | https://conferences.iaea.org/event/337/contributions/26550/attachments/13789/22569/Seo_NEOS_IAEA_meeting_2023.pdf | NEOS-II (Sept. 2018 – Oct. 2020) |

### DANSS (`experiment:danss`, kind `reactor_neutrino`, status `active`, tier D)

Facility: facility:kalinin-npp; site(s): site:kalinin-npp-reactor-building.

| interval | status | start | end | confidence | source | quote |
|---|---|---|---|---|---|---|
| data taking | active | 2016 | None | approximate | https://arxiv.org/abs/2109.13541 | The DANSS experiment [33,34] has been operated since 2016 at a LEU reactor of 3.1 GW thermal power in Kalinin, Russia |

### Neutrino-4 (`experiment:neutrino-4`, kind `reactor_neutrino`, status `completed`, tier D)

Facility: facility:sm-3-reactor-dimitrovgrad; site(s): site:sm-3-reactor-riar-dimitrovgrad.

| interval | status | start | end | confidence | source | quote |
|---|---|---|---|---|---|---|
| detector model measurements | commissioning | 2014 | 2016 | approximate | https://arxiv.org/abs/2005.05301 | The experiment Neutrino-4 had started in 2014 with a detector model and then was continued with a full-scale detector in 2016 - 2021. |
| full-scale detector data taking | active | 2016-06 | 2021 | approximate | https://arxiv.org/abs/2003.03199 | The measurements with reactor under operation have started in June 2016 and were continued till June 2019, when reactor was stopped for renovation. |
| completed | completed | 2021 | None | approximate | https://arxiv.org/abs/2005.05301 | The experiment Neutrino-4 had started in 2014 with a detector model and then was continued with a full-scale detector in 2016 - 2021. |

### Palo Verde (`experiment:palo-verde`, kind `reactor_neutrino`, status `completed`, tier D)

Facility: facility:palo-verde-ngs; site(s): site:palo-verde-ngs-detector-laboratory.

| interval | status | start | end | confidence | source | quote |
|---|---|---|---|---|---|---|
| data taking | active | 1998-09 | 2000-07 | verified | https://arxiv.org/abs/hep-ex/0107009 | The analysis and results are presented from the complete data set recorded at Palo Verde between September 1998 and July 2000. |
| completed | completed | 2000-07 | None | verified | https://arxiv.org/abs/hep-ex/0107009 | The analysis and results are presented from the complete data set recorded at Palo Verde between September 1998 and July 2000. |

### Bugey (`experiment:bugey`, kind `reactor_neutrino`, status `completed`, tier D)

Facility: facility:bugey-npp; site(s): site:bugey-npp-detector-halls.

| interval | status | start | end | confidence | source | quote |
|---|---|---|---|---|---|---|
| Bugey-4 and Bugey-3 measurements (dates of data taking not found) | active | None | 1995 | approximate | https://arxiv.org/abs/nucl-ex/0005002 | results from the reactors at ILL ... in 1981, at Goesgen ... in 1986, and at Bugey ... in 1995 have found no evidence for neutrino oscillations |
| completed | completed | 1995 | None | approximate | https://arxiv.org/abs/nucl-ex/0005002 | results from the reactors at ILL ... in 1981, at Goesgen ... in 1986, and at Bugey ... in 1995 have found no evidence for neutrino oscillations |

### SoLid (`experiment:solid`, kind `reactor_neutrino`, status `completed`, tier D)

Facility: facility:sck-cen-mol; site(s): site:sck-cen-br2-reactor-hall.

| interval | status | start | end | confidence | source | quote |
|---|---|---|---|---|---|---|
| construction of the 1.6 t detector | construction | 2016 | 2018-02 | approximate | https://arxiv.org/abs/2002.05914 | proceeding to the construction of a 1.6 ton detector in 2016-2017 |
| installation and commissioning | commissioning | 2018-02 | 2018-04-11 | approximate | https://arxiv.org/abs/2002.05914 | The SoLid detector installation was completed in February 2018 and was successfully commissioned near the BR2 reactor in spring 2018. |
| data taking | active | 2018-04-11 | 2020-07-02 | verified | https://arxiv.org/abs/2407.14382 | The dataset on which this analysis is based spans data taken between 11th April 2018 to 2nd July 2020. |
| completed | completed | 2020-07-02 | None | approximate | https://arxiv.org/abs/2407.14382 | The dataset on which this analysis is based spans data taken between 11th April 2018 to 2nd July 2020. |

### CONNIE (`experiment:connie`, kind `cevns`, status `active`, tier D)

Facility: facility:angra-npp; site(s): site:angra-npp-connie-container.

| interval | status | start | end | confidence | source | quote |
|---|---|---|---|---|---|---|
| engineering run with a 4 g prototype | commissioning | 2014 | mid 2016 | approximate | https://arxiv.org/abs/1906.02200 | The engineering prototype of the experiment was installed at the reactor site in late 2014 |
| data taking with the upgraded CCD array | active | mid 2016 | None | approximate | https://arxiv.org/abs/1906.02200 | A complete upgrade of the sensors was performed in mid 2016 |

### JUNO-TAO (`experiment:juno-tao`, kind `reactor_neutrino`, status `construction`, tier D)

Facility: facility:taishan-npp; site(s): site:taishan-npp-tao-basement.

| interval | status | start | end | confidence | source | quote |
|---|---|---|---|---|---|---|
| proposed (conceptual design report) | proposed | 2020-05 | 2024-09 | approximate | https://arxiv.org/abs/2005.08745 | Submitted on 18 May 2020 |
| construction (assembly in the plant) | construction | 2024-09 | None | approximate | https://conferences.iaea.org/event/402/contributions/35152/attachments/18939/32006/TAO_IAEA_250407.pdf | Assembling in Taishan • Started from Sept. 2024 |

### PROSPECT (`experiment:prospect`, kind `reactor_neutrino`, status `completed`, tier D)

Facility: facility:oak-ridge-national-laboratory; site(s): site:ornl-hfir.

| interval | status | start | end | confidence | source | quote |
|---|---|---|---|---|---|---|
| proposed (physics-programme paper) | proposed | 2015-12 | 2017-01 | approximate | https://arxiv.org/abs/1512.02202 | PROSPECT is conceived as a 2-phase experiment |
| construction | construction | 2017-01 | 2018-03 | approximate | https://arxiv.org/abs/1808.00097 | The production of the LiLS commenced in January 2017. |
| PROSPECT-I data taking at HFIR | active | 2018-03 | 2018-10 | verified | https://arxiv.org/abs/2406.10408 | PROSPECT-I detector data acquired between March and October 2018 |
| completed | completed | 2018-10 | None | approximate | https://arxiv.org/abs/2406.10408 | PROSPECT-I detector data acquired between March and October 2018 |

### Jinping Neutrino Experiment (`experiment:jinping-neutrino-experiment`, kind `solar_neutrino`, status `proposed`, tier D)

Facility: facility:cjpl; site(s): site:cjpl-ii.

| interval | status | start | end | confidence | source | quote |
|---|---|---|---|---|---|---|
| proposed (proposal and letter of intent) | proposed | 2015 | None | verified | https://arxiv.org/abs/1703.01478 | The Jinping Neutrino Experiment (hereafter referred to as the Jinping experiment) was proposed in 2015 |

### ESSnuSB (`experiment:essnusb`, kind `accelerator_neutrino`, status `proposed`, tier D)

Facility: facility:european-spallation-source; site(s): site:ess-lund, site:zinkgruvan-mine-essnusb-far-detector.

| interval | status | start | end | confidence | source | quote |
|---|---|---|---|---|---|---|
| design study (conceptual design report) | proposed | 2018 | None | verified | https://arxiv.org/abs/2206.01208 | An EU-supported Design Study has been carried out during the years 2018-2022 |

### TRIDENT (`experiment:trident`, kind `astrophysical_neutrino`, status `proposed`, tier D)

Facility: facility:trident-south-china-sea-site; site(s): site:trident-south-china-sea-abyssal-plain.

| interval | status | start | end | confidence | source | quote |
|---|---|---|---|---|---|---|
| proposed (design paper and pathfinder results) | proposed | 2022-07 | None | approximate | https://arxiv.org/abs/2207.04519 | Submitted on 10 Jul 2022 |

### CCFR (`experiment:ccfr`, kind `accelerator_neutrino`, status `completed`, tier D)

Facility: facility:fermilab; site(s): site:fermilab-main-campus.

| interval | status | start | end | confidence | source | quote |
|---|---|---|---|---|---|---|
| E616 (as "CCFRR") and E701 runs | active | 1979 | 1982 | verified | https://www.nevis.columbia.edu/ccfr/history.html | E616, run in 1979, was the first experiment to take advantage of the high-energy neutrino beam in Lab E. |
| E744 run | active | 1985 | 1985 | verified | https://www.nevis.columbia.edu/ccfr/history.html | The Lab E neutrino era hit its stride with E744, run in 1985, and E770, run in 1987 and 1988. |
| E770 run | active | 1987 | 1988 | verified | https://www.nevis.columbia.edu/ccfr/history.html | The Lab E neutrino era hit its stride with E744, run in 1985, and E770, run in 1987 and 1988. |
| completed (CCFR data taking; detector continued as NuTeV) | completed | 1988 | None | approximate | https://www.nevis.columbia.edu/ccfr/intro.html | The CCFR collaboration collected data from two fixed-target runs at Fermilab in 1985 (experiment E744) and 1987-88 (experiment E770). |

### NuTeV (`experiment:nutev`, kind `accelerator_neutrino`, status `completed`, tier D)

Facility: facility:fermilab; site(s): site:fermilab-main-campus.

| interval | status | start | end | confidence | source | quote |
|---|---|---|---|---|---|---|
| 1996-97 fixed-target run | active | 1996 | 1997 | verified | https://arxiv.org/abs/hep-ex/0110059 | High-purity ν and ν beams were provided by the Sign Selected Quadrupole Train (SSQT) beamline at the Fermilab Tevatron during the 1996-1997 fixed target run. |
| completed | completed | 1997 | None | approximate | https://arxiv.org/abs/hep-ex/0110059 | High-purity ν and ν beams were provided by the Sign Selected Quadrupole Train (SSQT) beamline at the Fermilab Tevatron during the 1996-1997 fixed target run. |

### ANNIE (`experiment:annie`, kind `accelerator_neutrino`, status `active`, tier D)

Facility: facility:fermilab; site(s): site:fermilab-main-campus.

| interval | status | start | end | confidence | source | quote |
|---|---|---|---|---|---|---|
| Phase I approved | approved | 2015-02 | 2016-04 | approximate | https://arxiv.org/abs/1707.08222 | Phase I of ANNIE was approved by the Fermilab PAC in late February of 2015 |
| Phase I (PMT-only test-beam run) | active | 2016-04 | 2017 | approximate | https://arxiv.org/abs/1707.08222 | Phase I was approved by the PAC in Spring of 2015, commissioned in April 2016. The collaboration has been taking data since May of 2016. |
| Phase II installation and commissioning | commissioning | 2019-07 | 2020 | approximate | https://annie.fnal.gov/ | Phase II detector for the full physics program of the experiment was installed in July 2019 and data taking was started in 2020. |
| Phase II data taking | active | 2020 | None | approximate | https://annie.fnal.gov/ | Phase II detector for the full physics program of the experiment was installed in July 2019 and data taking was started in 2020. |

### ArgoNeuT (`experiment:argoneut`, kind `accelerator_neutrino`, status `completed`, tier D)

Facility: facility:fermilab; site(s): site:fermilab-main-campus.

| interval | status | start | end | confidence | source | quote |
|---|---|---|---|---|---|---|
| commissioning in the MINOS near-detector hall | commissioning | 2009-03 | 2009-09 | approximate | https://arxiv.org/abs/1205.6747 | The ArgoNeuT detector was commissioned for the physics run in the MINOS-ND hall at Fermilab in spring 2009. |
| physics run in the NuMI low-energy beam | active | 2009-09 | 2010-02 | verified | https://arxiv.org/abs/1205.6702 | ArgoNeuT operated in the NuMI low-energy beam line directly upstream of the MINOS Near Detector from September 2009 to February 2010 |
| completed | completed | 2010-02 | None | approximate | https://arxiv.org/abs/1205.6702 | ArgoNeuT operated in the NuMI low-energy beam line directly upstream of the MINOS Near Detector from September 2009 to February 2010 |

## Coordinates written (new facilities and sites)

All are campus-grade (`kind: campus`, `confidence: approximate`) points with their precision stated; none is labelled `detector` or `underground_lab` (A17/A23). Method: Nominatim (OpenStreetMap) lookup of the plant or laboratory, or, for TRIDENT, the position stated in the design paper.

| site | lat, lon | precision (m) | source | locator / quote |
|---|---|---|---|---|
| `site:angra-npp-connie-container` | -23.01016, -44.45636 | 1000 | https://nominatim.openstreetmap.org/search?q=Central+Nuclear+Almirante+%C3%81lvaro+Alberto&format=jsonv2&limit=1 | Nominatim result for "Central Nuclear Almirante Álvaro Alberto" (way 175358417): Central Nuclear Almirante Álvaro Alberto, Cunhambebe, Angra dos Reis, Rio de Janeiro, Região Sudeste, 23948-000, Brasil |
| `site:bugey-npp-detector-halls` | 45.79944, 5.26727 | 1000 | https://nominatim.openstreetmap.org/search?q=CNPE+du+Bugey&format=jsonv2&limit=1 | Nominatim result for "CNPE du Bugey" (way 42017156): Centre Nucléaire de Production d'Electricité du Bugey, Saint-Vulbas, Belley, Ain, Auvergne-Rhône-Alpes, France métropolitaine, 01150, France |
| `site:ess-lund` | 55.73693, 13.25101 | 500 | https://nominatim.openstreetmap.org/search?q=European+Spallation+Source+Lund&format=jsonv2&limit=1 | Nominatim result for "European Spallation Source Lund" (way 164163815): European Spallation Source, Gårdstångabacken, Brunnshög, Öster, Lund, Lunds kommun, Skåne län, 224 84, Sverige |
| `site:hanbit-neos-tendon-gallery` | 35.41107, 126.41638 | 700 | https://www.openstreetmap.org/way/387266330; https://arxiv.org/abs/1610.05134 | The NEOS detector was installed in the tendon gallery of reactor unit 5 of the Hanbit Nuclear Power Complex in Yeonggwang, Korea. |
| `site:kalinin-npp-reactor-building` | 57.90895, 35.06564 | 1500 | https://nominatim.openstreetmap.org/search?q=%D0%9A%D0%B0%D0%BB%D0%B8%D0%BD%D0%B8%D0%BD%D1%81%D0%BA%D0%B0%D1%8F+%D0%90%D0%AD%D0%A1&format=jsonv2&limit=1 | Nominatim result for "Калининская АЭС" (way 564414439): Калининская АЭС, Удомельский муниципальный округ, Тверская область, Центральный федеральный округ, Россия |
| `site:ornl-hfir` | 35.9302, -84.30992 | 2000 | https://overpass-api.de/api/interpreter?data=%5Bout%3Ajson%5D%5Btimeout%3A25%5D%3B%28nwr%5B%22name%22~%22HFIR%7CIsotope%7CReactor%7COak%20Ridge%20National%22%2Ci%5D%2835.86%2C-84.40%2C35.99%2C-84.20%29%3B%29%3Bout%20center%20tags%3B | centroid of OSM way 300971334 "Oak Ridge National Laboratory" (campus outline) |
| `site:palo-verde-ngs-detector-laboratory` | 33.38447, -112.8644 | 1500 | https://nominatim.openstreetmap.org/search?q=Palo+Verde+Nuclear+Generating+Station&format=jsonv2&limit=1 | Nominatim result for "Palo Verde Nuclear Generating Station" (way 28706177): Palo Verde Nuclear Generating Station, Maricopa County, Arizona, United States |
| `site:sck-cen-br2-reactor-hall` | 51.21585, 5.0959 | 150 | https://nominatim.openstreetmap.org/search?q=BR2+reactor+Mol&format=jsonv2&limit=1 | Nominatim result for "BR2 reactor Mol" (way 133624022): BR2 Nuclear Reactor, Boeretang, Mol, Laakdal, Turnhout, Antwerpen, Vlaanderen, 2400, België / Belgique / Belgien |
| `site:sm-3-reactor-riar-dimitrovgrad` | 57.90895, 35.06564 | 2500 | https://nominatim.openstreetmap.org/search?q=%D0%9D%D0%98%D0%98+%D0%B0%D1%82%D0%BE%D0%BC%D0%BD%D1%8B%D1%85+%D1%80%D0%B5%D0%B0%D0%BA%D1%82%D0%BE%D1%80%D0%BE%D0%B2+%D0%9C%D1%83%D0%BB%D0%BB%D0%BE%D0%B2%D0%BA%D0%B0&format=jsonv2&limit=1 | Nominatim result for "НИИ атомных реакторов Мулловка" (way 564414439): Калининская АЭС, Удомельский муниципальный округ, Тверская область, Центральный федеральный округ, Россия |
| `site:taishan-npp-tao-basement` | 21.91222, 112.97959 | 1500 | https://nominatim.openstreetmap.org/search?q=Taishan+Nuclear+Power+Plant&format=jsonv2&limit=1 | Nominatim result for "Taishan Nuclear Power Plant" (way 435061160): 台山核电站, 赤溪镇, 台山市, 江门市, 广东省, 中国 |
| `site:trident-south-china-sea-abyssal-plain` | 17.4, 114.0 | 30000 | https://arxiv.org/abs/2207.04519 | an area near 114.0◦ E, 17.4◦ N was selected as a suitable location to build a large scale deep-sea detector |
| `site:zinkgruvan-mine-essnusb-far-detector` | 58.81592, 15.10747 | 3000 | https://nominatim.openstreetmap.org/search?q=Zinkgruvan&format=jsonv2&limit=1 | Nominatim result for "Zinkgruvan" (node 321191173): Zinkgruvan, Askersunds kommun, Örebro län, Sverige |

## Conflicts (claim / source A / source B / chosen / why)

- **CHOOZ start of data taking.** Final article: "The data acquisition period extended over 450 days, from 12 March 1997 till 20 July 1998"; its Table 1 caption gives 7 April 1997 for the tabulated neutrino runs. Chosen 12 March 1997 (the stated acquisition period). Site: no separate CHOOZ hall coordinate exists; the existing Double Chooz far-hall site is reused because the Double Chooz design report says its far detector went to "the former experimental site of the CHOOZ experiment" (placement kept `approximate`).
- **STEREO start.** JINST detector paper: installed November 2016 (phase I, defects repaired summer 2017, phase II from October 2017); Nature paper counts only high-quality data from October 2017 to the November 2020 shutdown. Chosen November 2016 to November 2020 with the October 2017 start in the note. Nature publication date (12 January 2023, seen only in a search snippet of an offline page) was not used; results carry arXiv v1 dates.
- **NEOS dates and rate.** PRL gives only "eight-month data-taking period"; a collaboration proceedings says summer 2015 to spring 2016 and "In May 2016 ... removed"; NEOS-II is dated "Sept. 2018 - Oct. 2020" only by a January 2023 collaboration talk. Chosen those, with season precision for the start. arXiv v1 abstract (1965/day, S/B 23, seen in a search snippet) differs from the published one (1976/day, S/B 22); only the published abstract is quoted.
- **DANSS start.** A conference summary (not fetchable) said April 2016 commissioning and regular data from October 2016; the fetchable review says "operated since 2016". Chosen year 2016. Distance range: design paper 10-12 m, PLB 2018 10.7-12.7 m as built; chosen the latter.
- **Neutrino-4 significance and end.** The three papers give 3.5 sigma (sin^2 2theta ~ 0.38), sin^2 2theta = 0.26 +- 0.08 +- 0.05, and 2.9 sigma (0.36 +- 0.12); both the first (2018) and the final published (2021) claims are recorded as separate `anomaly` results. Data taking: PRD says the full-scale detector ran 2016-2021; the 2020 paper says reactor-on measurements ran June 2016 to June 2019 with background to January 2020. Chosen end 2021 (year). arXiv:2003.03199 carries JETP Lett. 112 (2020) 199, not PRD 104, 032003 (which is arXiv:2005.05301). PROSPECT's final paper states the Neutrino-4 best-fit point is ruled out at more than five sigma; recorded as PROSPECT's statement, not a retraction.
- **Palo Verde baseline.** Initial PRL "about 800 m"; final PRD 750 m and 890 m. Chosen the PRD figures.
- **Bugey dates.** A review says Bugey reported in 1995, its table labels the integral result 1994, another review's figure says "Bugey 3, 96". Chosen end 1995 as an upper bound (approximate); no start. Baselines: one review text says 15-40 m, others 15, 40, 95 m; chosen 15, 40, 95 m.
- **SoLid end.** JINST paper: data "up to june 2020"; 2024 paper: data set 11 April 2018 to 2 July 2020. Chosen 2 July 2020.
- **CONNIE kind and CCD count.** The brief files CONNIE under reactor experiments; its goal is CEvNS, so it is `cevns` with secondary kind `reactor_neutrino` (as CONUS, NUCLEUS, Ricochet). The 2019 abstract analyses 8 CCDs (47.6 g) while its section II describes a 14-CCD array; chosen the analysed 8-CCD mass.
- **JUNO-TAO baseline and start.** The 2020 design report says about 30 m and operation in 2022; the April 2025 status talk says 44 m at -9.6 m depth, assembly from September 2024 and commissioning data taking planned for May 2025. Chosen 44 m and status `construction` (no source confirms later progress; an interval with a planned start cannot be commissioning/active).
- **Jinping mass.** Letter of intent: 4 kt target, 2 kt fiducial (nu-e) and 3 kt (IBD); the 2017 prototype paper plans two detectors of 1 kt fiducial each. Chosen the letter of intent; status stays `proposed`.
- **ESSnuSB far site and ESS status.** The design report evaluates Zinkgruvan (360 km) and Garpenberg (540 km); chosen Zinkgruvan (preferred in its executive summary). ESS: design report (2022) says under construction, ESS press release of 16 May 2025 reports beam on dump; no fetched source reports beam on target, so `construction`.
- **TRIDENT coordinate.** The paper gives "an area near 114.0 E, 17.4 N"; chosen a campus-kind approximate point with 30 km precision (a `detector` coordinate may not rest on a rank-10 source). Facility country left empty (no jurisdiction stated).
- **CCFR scope.** The CCFR home page counts two runs (E744 1985, E770 1987-88) but its history page also covers E616 (1979) and E701 (1982) under the earlier name CCFRR; one experiment record with four `run` intervals. A search summary mentioning 1990-91 is not supported by any fetched source and was not used.
- **ANNIE.** Phase I end: 2017 proposal "has been operating since April 2016" vs home page "successfully completed in 2017" (chosen 2017). Mass: Fermilab feature "25 tons of gadolinium loaded water" in the tank vs home page "26-ton water-based neutrino detector" (chosen 26 t). The 2015 letter of intent says "Atmospheric" in the name; later papers "Accelerator".
- **ArgoNeuT commissioning.** "spring 2009" (season precision), first candidate 27 May 2009, physics run September 2009 to February 2010.

## Unresolved fields

- **All 18 experiments:** `external.inspire_experiment` is empty (inspirehep.net must not be contacted); all are tier D with `researched: partial`; collaboration formation dates and member/institution counts are empty (no official roster found); official websites exist only for PROSPECT, CCFR, ANNIE and Jinping.
- **Coordinates:** every site is a campus-grade point (see the table); no hall-level coordinate was found for any detector. Hanbit unit numbers could not be mapped to the OpenStreetMap reactor buildings, so the NEOS point is the plant centre (precision ~700 m).
- **Bugey:** no start or end of data taking, no headline `result` record: the primary Bugey papers (Declais 1994; Achkar 1995, 1996) are not on arXiv and publisher pages returned 403; `cds.cern.ch` served a proof-of-work bot check (Anubis), which was not bypassed. Bugey-1 and Bugey-2 are not recorded.
- **DANSS:** month of start; whether it is still running on 2026-10-26 (recorded as ongoing, last figures 7.7 M events by March 2023 from a conference summary); the post-2018 DANSS papers were not located (arXiv API rate-limited).
- **JUNO-TAO:** whether commissioning or data taking has started; no results.
- **NEOS:** the NEOS-II sterile-neutrino result was not found; **SoLid:** journal reference of the 2024 letter; **CONNIE:** skipper-CCD (2021-22) results seen only as conference abstracts; **Neutrino-4:** whether the announced successor setup was built.
- **Jinping, ESSnuSB, TRIDENT:** no approval or construction decision found; TRIDENT pilot (10 strings, ~2026) status unknown.
- **CCFR/NuTeV/ANNIE/ArgoNeuT:** Lab E, the SciBooNE hall and the MINOS near-detector hall have no coordinates in the sources read (the Fermilab main-campus point is reused). ANNIE has no neutron-multiplicity paper yet; ArgoNeuT's later papers are not recorded.

## Candidates considered and excluded, or not done

**Excluded after examination**

- **HUNT (High-energy Underwater Neutrino Telescope):** fails "a published design document names its host site". The collaboration's own talk (IFCPPL 2024, slide "Lake Baikal vs. South China Sea") compares the two candidate sites without choosing; the ICRC 2025 proceedings (PoS(ICRC2025)1061) describe "a proposed next-generation neutrino observatory with an instrumented volume of approximately 30 cubic kilometers" and name no site. Press reports of a prototype at a designated site came only through search summaries and were not confirmed by a primary source. Revisit when one site is named with a coordinate.

**Not done (stream stopped at the usage limit; each has a `researched: "none"` row in the registry with its lead)**

- Accelerator neutrino: CHORUS, NOMAD, CDHS, CHARM, CHARM II (all CERN, existing `facility:cern`); JSNS2 (J-PARC MLF); CCM (LANL Lujan Center).
- Atmospheric and nucleon decay: Frejus (Modane), NUSEX (new `facility:mont-blanc-laboratory`), Soudan 2, MACRO (LNGS Hall B), Baksan Underground Scintillation Telescope, Kolar Gold Fields experiments (only if well sourced; new facility).
- Double-beta decay: Heidelberg-Moscow, NEMO-3, SuperNEMO demonstrator, CANDLES, CUORICINO, PandaX-III (only if it meets the bar).
- Direct neutrino mass: Mainz and Troitsk tritium experiments (new facilities Johannes Gutenberg University Mainz and INR Troitsk), ECHo, HOLMES (facilities not assigned in the brief; would need creating).
- Result records for the headline results named in the brief that depend on undone experiments: the Heidelberg-Moscow limit. Done: CHOOZ theta13 limit, PROSPECT, STEREO and DANSS reactor-anomaly tests, NuTeV sin^2 theta_W anomaly.

**Extra candidates noticed but outside this brief (not created, to avoid colliding with other streams):** TEXONO, Nucifer, MUNU, Goesgen and Rovno (reactor); SciBooNE (Fermilab); LVD and Mont Blanc LSD (underground); IGEX, CUPID-0, CUPID-Mo, COBRA (double-beta); INO (India-based Neutrino Observatory, which pairs naturally with the Kolar Gold Fields history).

**Source constraint noticed:** `cds.cern.ch` (CERN Document Server) answered with a proof-of-work bot check; it was not bypassed, so old CERN neutrino papers (CHORUS/NOMAD/CDHS/CHARM) must come from arXiv or other fetchable sources.

## For the integrator

- **Parent topic.** `topic:nucleon-decay` has parent `topic:precision-and-rare-processes` (nucleon decay is a search for an extremely rare process; the brief allowed neutrino-physics or none). Change `parent_id` in `data/atlas/topics/neutrino-2.json` if you prefer `topic:neutrino-physics`. No experiment references the topic yet (its experiments were not reached).
- **Committed records that need edits (not touched here):**
  - `experiment:double-chooz`: add lineage `{relation: predecessor, experiment_id: experiment:chooz}` (support: "Installation of the experiment will start with the far detector located at the former experimental site of the CHOOZ experiment", `src:geo-chooz-dc-tdr-2006`).
  - `facility:chooz`: its only interval starts 2011 and triggers `experiment-before-facility` for CHOOZ (1997); it should start no later than 1997-03 (`src:chooz-epjc-2003-final-article`).
  - `experiment:juno`: add a `complementary` or `same_program` row to `experiment:juno-tao` (lives on the lexicographically smaller id); source `src:juno-tao-cdr-2020` ("TAO is a satellite experiment of the Jiangmen Underground Neutrino Observatory (JUNO)").
  - `experiment:katrin`: Mainz and Troitsk (not yet written) would be its predecessors.
  - `experiment:cuore`: its lineage row `predecessor: experiment:cupid` is backwards (CUPID is CUORE's successor); the CUORICINO row would also live there. `experiment:gerda` has `predecessor: experiment:legend` (backwards) and `experiment:legend` holds derived `successor` rows (warned by the validator).
  - `experiment:reno`: result `result:neos-reno-joint-sterile-search-2022` lists it as a co-experiment.
- **Suggested new entities (not created, outside the brief):** `accelerator:ess-linac`, `beamline:essnusb` (ESS to Zinkgruvan, 360 km), a Zinkgruvan mine facility (the far site is attached to `facility:european-spallation-source` for now); an `accelerator`/`beamline` for BNB-related ANNIE is already covered by `beamline:bnb`.
- **Id notes:** `src:neutrino-4-prd-2021-results` is the 2020 JETP Lett. analysis paper (arXiv:2003.03199), not the PRD paper (`src:neutrino-4-prd-2021-search`, arXiv:2005.05301); the id is a misnomer kept because the file already existed. Several source ids carry the experiment slug as prefix; shared review sources (`src:bugey-*`) are cited by Bugey only.
- **Display-value warnings:** range quantities (`40-100 MW`) trigger `display-value-drift`; they are intentional ranges.

## Checks run

- `python -m hepgraph.atlas.validate` on the final tree: **0 errors, 1707 warnings, 50 informational** (baseline before this stream: 0 errors, 1596 warnings, 4 informational; the 46 extra informational lines are the 23 queued backlog rows, each reported twice, for `entity_id` and `experiment_id`, as "not in the atlas yet"). New warnings are the expected kinds: campus-grade coordinates under detector sites (A23), no listed accelerator/beamline for reactor experiments, `unknown-spec-key` for `sensitive_volume` / `active_volume`, `display-value-drift` on one range, hull gaps between runs (CCFR, ANNIE, SoLid), interval starts unknown (Bugey).
- `python -m hepgraph.atlas.build`: succeeded ("wrote 81 file(s)", 149 experiments, 57 facilities, 106 sites, 130 results, 43 topics); the bundle-budget notice (atlas.json + manifest.json over the 400 KB pilot budget, under the 1.5 MB failure threshold) was already present before this stream. `static/atlas/generated` was restored with `git checkout -- static/atlas/generated` before committing.
- `python -m pytest -q` (full suite, run on the fresh build): **689 passed, 139 skipped** (the skips are the PostgreSQL-backed tests that need a throwaway database URL).
- Quote check: `scripts/atlas_quote_check.py --only annie` and `--only argoneut` give all quotes verbatim except one ANNIE quote whose source (news.fnal.gov) timed out in the script (verified verbatim when written); every other record was checked at write time by the helper that fetched each cited source and refused non-verbatim quotes (0 problem quotes on each batch re-check with the repository's checker).
- No inspirehep.net, Neon or Vercel access; no push; `cds.cern.ch` bot check not bypassed.
