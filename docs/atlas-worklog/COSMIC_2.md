# COSMIC_2: cosmic-frontier coverage (CMB, dark energy, cosmic rays, gamma rays)

Owner tag `cosmic-2`. Branch `atlas-c6-cosmic`, worktree `HEP-Graph-ar-c6-cosmic`. All sources were read on 2026-10-26. Scope is amendment A26 of `docs/HEP_ATLAS_ONTOLOGY.md`: ground-based experiments only, so no space missions and no gravitational-wave observatories.

## Summary

* **Written:** 36 experiments, 35 detectors, 24 collaborations, 13 new facilities, 23 new sites, 46 results, 3 topics, 193 new source records, 36 coverage rows (`data/atlas/coverage/cosmic-2.json`).
* **By area:** CMB 12 experiments; dark energy 6; cosmic rays 11; gamma rays 6; SWGO 1 (written by the parent).
* **New facilities (13, all assigned by the brief):** `akeno-observatory`, `apache-point-observatory`, `cerro-tololo-inter-american-observatory`, `dugway-hires-site`, `hanle-observatory`, `kitt-peak-national-observatory`, `ooty-cosmic-ray-laboratory`, `parque-astronomico-atacama`, `tunka-valley`, `vera-c-rubin-observatory`, `woomera-cangaroo-site`, `yakutsk-eas-array`, `yangbajing-cosmic-ray-observatory`.
* **Existing records edited (1):** `facility:amundsen-scott-south-pole-station`, one note that said SPT and MAPO were not recorded as sites of the facility (the CMB fork). The parent also extended `facility:parque-astronomico-atacama`, a record of this stream, when SWGO was added (summary sentence, one topic id, one source, one note).
* **Tiers:** DESI, DES and Rubin are tier B; everything else is tier C. INSPIRE was not contacted (STREAM_RULES), so no experiment carries `external.inspire_experiment`; each experiment note says so.
* **Verification:** every `quote` is a verbatim, whitespace-normalised substring of the page text fetched on 2026-10-26 for a source the record cites. The build scripts raise otherwise. The parent re-ran an independent audit over every record of the stream: 895 quotes checked, 0 failures (one coordinate quote, `site:mount-hopkins-whipple-10m`, is from the ar5iv HTML rendering of the same arXiv paper, which the builder read, and not from the arXiv abstract page).
* **Method:** the stream was split into four research forks (CMB, dark energy, cosmic rays, gamma rays) plus the parent, who wrote the three topics and SWGO and merged the rows and this log. The builders are idempotent scripts, kept in the session scratch directory and not committed.

## Contents

1. Part 1: CMB experiments (generated from the records).
2. Part 2: dark-energy surveys.
3. Part 3: cosmic-ray arrays.
4. Part 4: gamma-ray experiments.
5. Part 5: SWGO, IceTop and the three topics (parent).
6. Part 6: for the integrator, and checks run.

Each part has its own entity tables (start / end / status / site, with the URL and verbatim quote behind each date and coordinate), conflicts (claim / source A / source B / chosen / why), unresolved fields, and the candidates considered and excluded with the reason.

## Part 1. CMB experiments (fork `cmb`)

Ground-based CMB experiments under A26: SPT, BICEP/Keck, DASI, ACT, Simons Observatory, POLARBEAR / Simons Array, CLASS and CMB-S4; the Parque Astronomico Atacama facility, five sites, one detector record per instrument, collaborations where a named body exists, and headline results from the abstracts. The tables below are generated from the committed records; every quote is the verbatim string stored in the record and was machine-checked against the fetched page text when the record was written (and re-checked by the parent in an independent audit).

Counts: 12 experiments, 12 detectors, 1 facility, 5 sites, 7 collaborations, 14 results, 62 source records (`src:c2-cmb-*`). One existing record was edited: the note of `facility:amundsen-scott-south-pole-station` that said SPT and MAPO were not recorded as sites.

### Structure decisions

* **SPT.** SPT-SZ, SPTpol and SPT-3G are three receivers of one telescope (LAMBDA and the SPT site describe them so), so `experiment:spt` is one record with the three receivers as dated `phase` intervals.
* **BICEP / Keck.** The sources present a series of instruments with separate dates, apertures and results, so BICEP1, BICEP2, the Keck Array, BICEP3 and BICEP Array are five experiment records sharing `collaboration:bicep-keck`, linked by `predecessor` / `same_program` lineage rows stated in the papers.
* **ACT.** ACT, ACTPol and AdvACT are receivers of one telescope (LAMBDA): one experiment, with the receivers as phases. ACT ended observing in 2022 and is `decommissioned`.
* **POLARBEAR / Simons Array.** One experiment with POLARBEAR-1 (Huan Tran Telescope) and the Simons Array (POLARBEAR-2 receivers) as phases, as the brief and LAMBDA treat them.
* **CMB-S4.** Recorded as `cancelled` (the Atlas enum; the agencies' words are "can no longer support"): the project page quotes the DOE/NSF statement of 9 July 2025 and says the project "is proceeding with an orderly shutdown". The experiment note quotes the statement exactly. The detector record exists only so the experiment has a located placement (never built).
* **Sites.** The South Pole instruments share one `site:south-pole-dark-sector` (no source gives separate coordinates for MAPO, the Dark Sector Laboratory and the SPT). On Cerro Toco ACT, the Simons Observatory, POLARBEAR's James Ax Observatory and CLASS each stand in a different spot within about a kilometre, so each has its own site record on `facility:parque-astronomico-atacama`.
* **Tiers.** All twelve experiments are tier C; INSPIRE was not contacted, so no `external.inspire_experiment` is set and every experiment note says why.

### Experiments

| id | kind | status | tier | intervals (label: start to end) |
|---|---|---|---|---|
| experiment:spt | cmb | active | C | operations: 2007-02 to (open) (active); SPT-SZ survey camera: 2008 to 2011 (active); SPTpol camera: 2012 to 2016 (active); SPT-3G camera: 2017-01 to (open) (active) |
| experiment:bicep1 | cmb | completed | C | observations: 2006-02 to 2008 (active); observations ended: 2008 to (open) (completed) |
| experiment:bicep2 | cmb | completed | C | observations: 2010 to 2012 (active); observations ended: 2012 to (open) (completed) |
| experiment:keck-array | cmb | decommissioned | C | observations: 2012 to late 2019 (active); decommissioned: late 2019 to (open) (decommissioned) |
| experiment:bicep3 | cmb | active | C | deployment and first season: 2014-2015 austral summer to 2016 (commissioning); science observations: 2016 to (open) (active) |
| experiment:bicep-array | cmb | active | C | observations: early 2020 to (open) (active) |
| experiment:dasi | cmb | completed | C | deployment: austral summer 1999-2000 to 2000 (commissioning); observations: 2000 to 2003 (active); observations ended: 2003 to (open) (completed) |
| experiment:act | cmb | decommissioned | C | operations: 2007 to 2022 (active); MBAC (first receiver): 2008 to 2010 (active); ACTPol: 2013 to 2016 (active); Advanced ACTPol (AdvACT): 2016 to 2022 (active); decommissioned: 2022 to (open) (decommissioned) |
| experiment:simons-observatory | cmb | active | C | construction: 2018-08 to 2024-04-25 (construction); science observations: 2024-06-03 to (open) (active); Large Aperture Telescope first light: 2025-02-22 to (open) (active) |
| experiment:polarbear | cmb | completed | C | observations (POLARBEAR-1 and Simons Array): 2012-01-10 to 2024 (active); POLARBEAR-1 (Huan Tran Telescope): 2012-01-10 to 2016-12 (active); Simons Array (POLARBEAR-2 receivers): 2019 to 2024 (active); programme completed: 2024 to (open) (completed) |
| experiment:class | cmb | active | C | observations: 2016-08-31 to (open) (active); 90 GHz telescope: 2018-06 to (open) (active) |
| experiment:cmb-s4 | cmb | cancelled | C | proposed: 2016-10-10 to 2025-07-09 (proposed); cancelled: 2025-07-09 to (open) (cancelled) |

### Dated intervals with their sources and quotes

| entity | interval | start | end | source URL | verbatim quote |
|---|---|---|---|---|---|
| experiment:spt | operations (active, verified) | 2007-02 | (open) | https://arxiv.org/abs/0907.4445 | The SPT has been operating at the South Pole since February 2007. |
| experiment:spt | SPT-SZ survey camera (active, verified) | 2008 | 2011 | https://lambda.gsfc.nasa.gov/product/spt/, https://arxiv.org/abs/1409.0850 | From 2008 to 2011, the SPT-SZ receiver carried out a 2500 square-degree survey of the southern sky at high galactic latitude. |
| experiment:spt | SPTpol camera (active, verified) | 2012 | 2016 | https://lambda.gsfc.nasa.gov/product/spt/, https://arxiv.org/abs/1910.05748 | From 2012 through 2016, the SPT was equipped with the polarization-sensitive SPTpol receiver |
| experiment:spt | SPT-3G camera (active, verified) | 2017-01 | (open) | https://lambda.gsfc.nasa.gov/product/spt/, https://arxiv.org/abs/1809.00033 | In January 2017, the SPT-3G receiver was installed on the SPT. |
| experiment:bicep1 | observations (active, approximate) | 2006-02 | 2008 | https://arxiv.org/abs/0906.4069, https://arxiv.org/abs/0906.1181 | BICEP has completed 3 years of successful observations at the South Pole beginning in 2006 February. |
| experiment:bicep1 | observations ended (completed, approximate) | 2008 | (open) | https://arxiv.org/abs/0906.1181, https://lambda.gsfc.nasa.gov/product/bicepkeck/, https://arxiv.org/abs/1310.1422 | During three seasons of observing at the South Pole (2006 through 2008) |
| experiment:bicep2 | observations (active, approximate) | 2010 | 2012 | https://arxiv.org/abs/1403.3985, https://lambda.gsfc.nasa.gov/product/bicepkeck/ | BICEP2 observed from the South Pole for three seasons from 2010 to 2012. |
| experiment:bicep2 | observations ended (completed, approximate) | 2012 | (open) | https://lambda.gsfc.nasa.gov/product/bicepkeck/ | BICEP2 was a 26-cm refracting telescope that observed the cosmic microwave background (CMB) from the National Science Foundation's Amundsen-Scott South Pole Station from 2010-2012. |
| experiment:keck-array | observations (active, approximate) | 2012 | late 2019 | https://arxiv.org/abs/2012.04047, https://lambda.gsfc.nasa.gov/product/bicepkeck/ | The Keck Array consisted of five Bicep2 -like 260 mm aperture receivers and started observations at 150 GHz in 2012. |
| experiment:keck-array | decommissioned (decommissioned, approximate) | late 2019 | (open) | https://arxiv.org/abs/2203.16556 | In late 2019, Keck was decommissioned and replaced by the Bicep Array telescope |
| experiment:bicep3 | deployment and first season (commissioning, approximate) | 2014-2015 austral summer | 2016 | https://lambda.gsfc.nasa.gov/product/bicepkeck/ | BICEP3, the successor to BICEP2, was deployed to the Dark Sector Laboratory at Amundsen-Scott South Pole Station in the 2014-2015 Austral summer season. |
| experiment:bicep3 | science observations (active, verified) | 2016 | (open) | https://arxiv.org/abs/2203.16556, https://arxiv.org/abs/1607.04668 | has been observing at the foreground-minimum 95 GHz since 2016 |
| experiment:bicep-array | observations (active, approximate) | early 2020 | (open) | https://arxiv.org/abs/2012.04047, https://lambda.gsfc.nasa.gov/product/bicepkeck/ | The 30/40 GHz receiver is designed to constrain the synchrotron foreground and has begun observing at the South Pole in early 2020. |
| experiment:dasi | deployment (commissioning, approximate) | austral summer 1999-2000 | 2000 | https://arxiv.org/abs/astro-ph/0104488 | The telescope was deployed at the Amundsen-Scott South Pole research station during the 1999--2000 austral summer and conducted observations of the CMB throughout the following austral winter. |
| experiment:dasi | observations (active, approximate) | 2000 | 2003 | https://arxiv.org/abs/astro-ph/0104488, https://arxiv.org/abs/astro-ph/0104489 | The telescope was deployed at the Amundsen-Scott South Pole research station during the 1999--2000 austral summer and conducted observations of the CMB throughout the following austral winter. |
| experiment:dasi | observations ended (completed, approximate) | 2003 | (open) | https://arxiv.org/abs/astro-ph/0409357 | We present the analysis of the complete 3-year data set obtained with the Degree Angular Scale Interferometer (DASI) polarization experiment |
| experiment:act | operations (active, approximate) | 2007 | 2022 | https://arxiv.org/abs/1007.0290, https://lambda.gsfc.nasa.gov/product/act/ | The telescope was commissioned in 2007 and has completed its third year of operations. |
| experiment:act | MBAC (first receiver) (active, verified) | 2008 | 2010 | https://lambda.gsfc.nasa.gov/product/act/, https://arxiv.org/abs/1007.0290 | mapped the CMB temperature anisotropies over an area of around 1000 square degrees from 2008 to 2010 |
| experiment:act | ACTPol (active, verified) | 2013 | 2016 | https://lambda.gsfc.nasa.gov/product/act/, https://arxiv.org/abs/1605.06569 | The second-generation, polarization-sensitive receiver ACTPol observed between 2013 and 2016. |
| experiment:act | Advanced ACTPol (AdvACT) (active, approximate) | 2016 | 2022 | https://lambda.gsfc.nasa.gov/product/act/, https://arxiv.org/abs/2503.14451 | The third generation Advanced ACTPol receiver extended the frequency coverage down to 20 GHz and surveyed 40% of the sky from 2016 to 2022. |
| experiment:act | decommissioned (decommissioned, approximate) | 2022 | (open) | https://lambda.gsfc.nasa.gov/product/act/ | The Atacama Cosmology Telescope took its final data in 2022 and has been decommissioned. |
| experiment:simons-observatory | construction (construction, approximate) | 2018-08 | 2024-04-25 | https://arxiv.org/abs/1808.07445, https://www.simonsfoundation.org/2024/06/03/simons-observatory-begins-hunt-for-echoes-of-the-big-bang-in-universes-oldest-light/ | The Simons Observatory (SO) is a new cosmic microwave background experiment being built on Cerro Toco in Chile, due to begin observations in the early 2020s. |
| experiment:simons-observatory | science observations (active, approximate) | 2024-06-03 | (open) | https://www.simonsfoundation.org/2024/06/03/simons-observatory-begins-hunt-for-echoes-of-the-big-bang-in-universes-oldest-light/, https://www.simonsfoundation.org/news/now-fully-online-simons-observatory-begins-probe-of-universes-birth/ | From a vantage point high in the Chilean Andes, cosmologists with the Simons Observatory have begun searching for evidence of what happened in the minuscule fraction of a second that followed the Big Bang. |
| experiment:simons-observatory | Large Aperture Telescope first light (active, verified) | 2025-02-22 | (open) | https://www.simonsfoundation.org/2025/03/17/simons-observatory-large-aperture-telescope-achieves-first-light-milestone/ | The Simons Observatory’s Large Aperture Telescope captured this first light image of Mars on February 22, 2025. |
| experiment:polarbear | observations (POLARBEAR-1 and Simons Array) (active, approximate) | 2012-01-10 | 2024 | https://arxiv.org/abs/1210.7768, https://lambda.gsfc.nasa.gov/product/polarbear/ | First light with the fully integrated experiment was achieved on January 10th, 2012 with a scan of Jupiter. |
| experiment:polarbear | POLARBEAR-1 (Huan Tran Telescope) (active, approximate) | 2012-01-10 | 2016-12 | https://lambda.gsfc.nasa.gov/product/polarbear/, https://arxiv.org/abs/2005.06168 | In subsequent years (2014-2016) the POLARBEAR survey was expanded to cover 670 square degrees of sky. |
| experiment:polarbear | Simons Array (POLARBEAR-2 receivers) (active, approximate) | 2019 | 2024 | https://lambda.gsfc.nasa.gov/product/polarbear/ | The Simons Array (2019 - 2024) consisted of an array of second generation Polarbear-2 receivers. |
| experiment:polarbear | programme completed (completed, approximate) | 2024 | (open) | https://lambda.gsfc.nasa.gov/product/polarbear/ | The Simons Array (2019 - 2024) consisted of an array of second generation Polarbear-2 receivers. |
| experiment:class | observations (active, verified) | 2016-08-31 | (open) | https://arxiv.org/abs/2309.00675, https://arxiv.org/abs/2501.11904 | This paper uses data from the 40 GHz telescope observations beginning 2016 August 31, after initial commissioning, and extending to 2022 May 19, when the telescopes were shut down for maintenance and instrument upgrades. |
| experiment:class | 90 GHz telescope (active, verified) | 2018-06 | (open) | https://arxiv.org/abs/2501.11904 | The first of the two 90 GHz telescope arrays was deployed in June 2018 and has been observing since then. |
| experiment:cmb-s4 | proposed (proposed, approximate) | 2016-10-10 | 2025-07-09 | https://arxiv.org/abs/1610.02743 | This book lays out the scientific goals to be addressed by the next-generation ground-based cosmic microwave background experiment, CMB-S4, envisioned to consist of dedicated telescopes at the South Pole, the high Chilean Atacama plateau and possibly a northern hemisphere site |
| experiment:cmb-s4 | cancelled (cancelled, verified) | 2025-07-09 | (open) | https://cmb-s4.org/ | On July 9, 2025, the U.S. Department of Energy (DOE), Office of Science, Office of High Energy Physics and the U.S. National Science Foundation (NSF) issued a statement informing the CMB-S4 Project that |
| facility:parque-astronomico-atacama | first CMB telescope operating in the park area (ACT) (active, approximate) | 2007 | (open) | https://arxiv.org/abs/1007.0290, https://arxiv.org/abs/2503.14451 | The telescope was commissioned in 2007 and has completed its third year of operations. |
| facility:parque-astronomico-atacama | territorial concession presented; park opened by CONICYT (active, approximate) | 2014-01-10 | (open) | https://www.conicyt.cl/astronomia/2014/01/10/conicyt-inaugura-parque-astronomico-atacama/?lang=en | The Minister of National Assets, Rodrigo Perez, presented the Territorial Concession 50 years the President (s) CONICYT, Mateo Budinich, an area of 36.381,02 hectares in the area called Pampa La Bola, Llano de Chajnantor, municipality of San Pedro de Atacama |
| collaboration:spt | collaboration active (active, approximate) | 2007-02 | (open) | https://arxiv.org/abs/0907.4445 | The SPT has been operating at the South Pole since February 2007. |
| collaboration:bicep-keck | collaboration active (active, approximate) | 2006-02 | (open) | https://arxiv.org/abs/0906.4069 | BICEP has completed 3 years of successful observations at the South Pole beginning in 2006 February. |
| collaboration:act | collaboration active (active, approximate) | 2007 | (open) | https://arxiv.org/abs/1007.0290 | The telescope was commissioned in 2007 and has completed its third year of operations. |
| collaboration:simons-observatory | collaboration active (active, approximate) | 2018-08 | (open) | https://arxiv.org/abs/1808.07445 | The Simons Observatory Collaboration |
| collaboration:polarbear | collaboration active (active, approximate) | 2012-01 | (open) | https://arxiv.org/abs/1210.7768 | First light with the fully integrated experiment was achieved on January 10th, 2012 with a scan of Jupiter. |
| collaboration:class | collaboration active (active, approximate) | 2016-08-31 | (open) | https://arxiv.org/abs/2309.00675 | This paper uses data from the 40 GHz telescope observations beginning 2016 August 31, after initial commissioning, and extending to 2022 May 19, when the telescopes were shut down for maintenance and instrument upgrades. |
| collaboration:cmb-s4 | collaboration active (active, approximate) | 2016-10-10 | (open) | https://cmb-s4.org/team/ | CMB-S4 comprises a scientific collaboration and a joint DOE/NSF construction project and operations program. |

(Detector intervals repeat the experiment intervals and are not listed again.)

### Facility, sites and coordinates

| id | kind / setting | coordinate (lat, lon, precision, kind) | altitude | source URL | verbatim quote (coordinate) |
|---|---|---|---|---|---|
| facility:parque-astronomico-atacama | astronomical_observatory | primary site site:act-cerro-toco | 363.8 km² (36,381.02 hectares) (area) | https://www.conicyt.cl/astronomia/2014/01/10/conicyt-inaugura-parque-astronomico-atacama/?lang=en, https://simonsobservatory.org/about/the-simons-observatory/, https://cmb-s4.org/experiment/sites/, https://arxiv.org/abs/2503.14451, https://lambda.gsfc.nasa.gov/product/class/, https://www.swgo.org/SWGOWiki/doku.php?id=site_press_release | - |
| site:south-pole-dark-sector (facility:amundsen-scott-south-pole-station) | ice | -90.000000, 0.000000, 1000 m, detector (approximate) | 2800 m | https://arxiv.org/abs/0906.4069, https://www.nsf.gov/geo/opp/ail/amundson-scott-south-pole-station, https://cmb-s4.org/experiment/sites/ | looking out through the roof of the Dark Sector Laboratory (DSL) building located 800 m from the geographic South Pole |
| site:act-cerro-toco (facility:parque-astronomico-atacama) | mountain | -22.958611, -67.787500, 100 m, detector (verified) | 5190 m | https://arxiv.org/abs/1007.0290 | Altitude 5190 m Longitude 67◦ 47′ 15′′ W Latitude 22◦ 57′ 31′′ S |
| site:simons-observatory-cerro-toco (facility:parque-astronomico-atacama) | mountain | -22.950000, -67.783333, 2000 m, detector (verified) | 5190 meters (17,000 feet) | https://simonsobservatory.org/instrumentation/site-and-advanced-simons-observatory/ | Site Coordinates: Longitude – 67 deg 47′ West \| Latitude 22 deg 57′ South \| Elevation Above Sea Level: 5190 meters (17,000 feet). |
| site:polarbear-james-ax-observatory (facility:parque-astronomico-atacama) | mountain | -22.958056, -67.786222, 100 m, campus (approximate) | 5.20 km | https://arxiv.org/abs/1312.6646 | West longitude 67◦ 47′ 10.4′′ , South latitude 22◦ 57′ 29.0′′ , elevation 5.20 km |
| site:class-cerro-toco (facility:parque-astronomico-atacama) | mountain | -22.960000, -67.790000, 1000 m, campus (approximate) | 5140 m | https://arxiv.org/abs/2309.00675 | −22.96◦ / − 67.79◦ 5140 m |

### Collaborations

| id | formation | member / institution / country counts | source |
|---|---|---|---|
| collaboration:spt | null (not sourced) | null / null / null (as_of None, derived) | https://pole.uchicago.edu/public/Collaboration.html, https://pole.uchicago.edu/public/Home.html |
| collaboration:bicep-keck | null (not sourced) | null / null / null (as_of None, derived) | http://bicepkeck.org/, https://lambda.gsfc.nasa.gov/product/bicepkeck/ |
| collaboration:act | null (not sourced) | null / null / null (as_of None, derived) | https://arxiv.org/abs/2503.14451, https://lambda.gsfc.nasa.gov/product/act/ |
| collaboration:simons-observatory | null (not sourced) | 350 / 50 / null (as_of None, official_institution_list) | https://simonsobservatory.org/about/the-simons-observatory/, https://www.simonsfoundation.org/2024/06/03/simons-observatory-begins-hunt-for-echoes-of-the-big-bang-in-universes-oldest-light/, https://arxiv.org/abs/1808.07445 |
| collaboration:polarbear | null (not sourced) | null / null / null (as_of None, derived) | https://arxiv.org/abs/1403.2369, https://arxiv.org/abs/1312.6646, https://lambda.gsfc.nasa.gov/product/polarbear/ |
| collaboration:class | null (not sourced) | null / null / null (as_of None, derived) | https://arxiv.org/abs/1911.04499, https://lambda.gsfc.nasa.gov/product/class/ |
| collaboration:cmb-s4 | null (not sourced) | null / null / 19 (as_of None, official_institution_list) | https://cmb-s4.org/team/, https://cmb-s4.org/ |

### Detectors

| id | experiments | site | technology class | status |
|---|---|---|---|---|
| detector:spt | experiment:spt | site:south-pole-dark-sector | other | active |
| detector:bicep1 | experiment:bicep1 | site:south-pole-dark-sector | other | completed |
| detector:bicep2 | experiment:bicep2 | site:south-pole-dark-sector | other | completed |
| detector:keck-array | experiment:keck-array | site:south-pole-dark-sector | other | decommissioned |
| detector:bicep3 | experiment:bicep3 | site:south-pole-dark-sector | other | active |
| detector:bicep-array | experiment:bicep-array | site:south-pole-dark-sector | other | active |
| detector:dasi | experiment:dasi | site:south-pole-dark-sector | other | completed |
| detector:act | experiment:act | site:act-cerro-toco | other | decommissioned |
| detector:simons-observatory | experiment:simons-observatory | site:simons-observatory-cerro-toco | other | active |
| detector:polarbear | experiment:polarbear | site:polarbear-james-ax-observatory | other | completed |
| detector:class | experiment:class | site:class-cerro-toco | other | active |
| detector:cmb-s4 | experiment:cmb-s4 | site:south-pole-dark-sector | other | cancelled |

### Results

| id | date (kind) | type | significance as stated | claim quote |
|---|---|---|---|---|
| result:bicep-keck-bk18-r-limit-2021 | 2021-10-01 (preprint) | limit | - | The likelihood analysis yields the constraint $r_{0.05}<0.036$ at 95% confidence. |
| result:bicep2-b-mode-detection-claim-2014 | 2014-03-17 (preprint) | anomaly | > 5σ excess of B-mode power over lensed-ΛCDM at 30 < l < 150; r = 0 disfavored at 7.0σ (before foreground subtraction) | We find an excess of $B$-mode power over the base lensed-LCDM expectation in the range $30< \ell< 150$, inconsistent with the null hypothesis at a significance of $> 5\sigma$. |
| result:bicep2-keck-planck-joint-r-limit-2015 | 2015-02-02 (preprint) | limit | Lensing B modes detected at 7.0σ | The final result is expressed as a likelihood curve for $r$, and yields an upper limit $r_{0.05}<0.12$ at 95% confidence. |
| result:bicep1-b-mode-limit-2010 | 2009-06-05 (preprint) | limit | - | The tensor-to-scalar ratio derived from the B-mode spectrum is r = 0.03+0.31-0.26, or r < 0.72 at 95% confidence, the first meaningful constraint on the inflationary gravitational wave background to come directly from CMB B-mode polarization. |
| result:dasi-first-cmb-polarization-detection-2002 | 2002-09-23 (preprint) | first_detection | E-mode polarization detected at 4.9σ | We report the detection of polarized anisotropy in the Cosmic Microwave Background radiation with the Degree Angular Scale Interferometer (DASI), located at the Amundsen-Scott South Pole research station. |
| result:dasi-first-season-power-spectrum-2001 | 2001-04-30 (preprint) | measurement | - | In addition, we detect a peak in the power spectrum at l approx 550 and power of similar magnitude at l approx 800 which are consistent with the second and third harmonic peaks predicted by adiabatic inflationary cosmological models. |
| result:act-cmb-lensing-first-detection-2011 | 2011-03-10 (preprint) | first_detection | 4σ detection of the lensing signal | We report the first detection of the gravitational lensing of the cosmic microwave background through a measurement of the four-point correlation function in the temperature maps made by the Atacama Cosmology Telescope. |
| result:act-dr6-power-spectra-lcdm-2025 | 2025-03-18 (preprint) | measurement | - | When combined with CMB lensing from ACT and Planck, and baryon acoustic oscillation data from DESI DR1, we measure a baryon density of $\Omega_b h^2=0.0226\pm0.0001$, a cold dark matter density of $\Omega_c h^2=0.118\pm0.001$, a Hubble constant of $H_0=68.22\pm0.36$ km/s/Mpc |
| result:spt-first-sz-selected-clusters-2008 | 2008-10-09 (preprint) | discovery | Clusters detected as decrements with greater than 5-sigma significance in the 150 GHz SPT map | We report the four most significant SPT detections of SZ clusters in this field, three of which were previously unknown and, therefore, represent the first galaxy clusters discovered with an SZ survey. |
| result:sptpol-b-mode-lensing-first-detection-2013 | 2013-07-22 (preprint) | first_detection | 7.7σ correlation between the SPTpol B modes and a lensing-B-mode template | In this Letter we present the first detection of gravitational lensing B modes, using first-season data from the polarization-sensitive receiver on the South Pole Telescope (SPTpol). |
| result:spt-3g-d1-power-spectra-cosmology-2025 | 2025-06-25 (preprint) | measurement | - | We present measurements of the temperature and E-mode polarization angular power spectra of the cosmic microwave background (CMB) from observations of 4% of the sky with SPT-3G, the current camera on the South Pole Telescope (SPT). |
| result:polarbear-lensing-evidence-2013 | 2013-12-23 (preprint) | evidence | 4.2σ (stat.+sys.) evidence for polarization lensing and lensing B modes | Evidence for the signal of polarization lensing and lensing $B$-modes is found at 4.2$\sigma$ (stat.+sys.) significance. |
| result:polarbear-b-mode-power-spectrum-2014 | 2014-03-10 (preprint) | measurement | No-lensing B-mode hypothesis rejected at 97.1% confidence | Including both systematic and statistical uncertainties, the hypothesis of no B-mode polarization power from gravitational lensing is rejected at 97.1% confidence. |
| result:class-90-ghz-reionization-optical-depth-2025 | 2025-01-21 (preprint) | measurement | Reionization detected at 99.4% significance in cross-correlation with Planck | Through cross-correlation with Planck, we detected the cosmic reionization at $99.4\%$ significance and measured the reionization optical depth $\tau=0.053^{+0.018}_{-0.019}$, marking the first ground-based attempt at such a measurement. |

### Conflicts (CMB)

| claim | source A | source B | chosen | why |
|---|---|---|---|---|
| AdvACT receiver phase span | LAMBDA ACT overview: 2016 to 2022 | ACT DR6 maps paper (arXiv:2503.14451): AdvACT data used for DR6 "collected from 2017-05-05 to 2022-07-02" | LAMBDA span (2016-2022) kept for the phase; DR6 dates quoted in the interval note | The DR6 dates bound the data set used, not the receiver deployment. |
| POLARBEAR site latitude | POLARBEAR instrument paper: 22 deg 57 min 29.0 sec S | POLARBEAR B-mode paper (arXiv:1403.2369): 29.03 sec | 29.0 sec | Both round to the same 100 m precision; the point is a campus-grade approximation anyway (physics-paper source only, A17). |
| BICEP/Keck collaboration name | Official site: "The Keck Array and BICEP2 Collaborations" | Official site: "The BICEP/Keck Collaboration" | one record, `collaboration:bicep-keck` | The official site presents them as one series; formation date not stated by any source, so the interval start is a lower bound (first BICEP1 observations). |
| Simons Observatory construction end year | 2024 Simons Foundation release (dated 3 June 2024): main construction completed on April 25 | no year stated beside the day | 2024-04-25 | Year inferred from the release date and the release's own dating of Jim Simons's death a few weeks later; confidence approximate, note in the record. |
| BICEP3 "active" in 2026 | Official publication list (checked 2026-10-26) includes 2026 papers | no 2026-dated source says BICEP3 is observing | active | Open-ended 2016 observing statement plus the 2024-2026 publication list; noted in the record. |
| Dark Sector instrument positions | BICEP1/2/3 in the Dark Sector Laboratory, 800 m from the pole | DASI and Keck Array/BICEP Array on the MAPO mount, 0.7 km from the pole; SPT in the same Dark Sector | one site, pole anchor with 1000 m precision | No source gives separate coordinates for the three; one site avoids three records on one point (noted on the site). |

### Unresolved fields (CMB)

* Collaboration formation dates for all seven CMB collaborations (null with note, or interval lower bounds); member, institution and country counts left null for SPT, BICEP/Keck, ACT, POLARBEAR and CLASS (no roster fetched); the Simons Observatory and CMB-S4 give undated approximate counts that are quoted in notes only.
* No official website: ACT (act.princeton.edu returned HTTP 403), POLARBEAR (bolo.berkeley.edu/polarbear refused connection), CLASS (sites.krieger.jhu.edu/class returned HTTP 403), DASI (the Chicago page now redirects to the department home page). Their `links.website` is null with a note.
* POLARBEAR-1 end date (not given by any source; phase interval note) and the Simons Array end year (2024, LAMBDA alone).
* Simons Observatory construction start (lower bound only: the 2018 science-goals paper says "being built").
* Coordinates: BICEP/Keck/SPT/DASI share an approximate pole anchor (1000 m); POLARBEAR and CLASS are campus-grade (physics-paper sources only); the Chilean CMB-S4 site was never recorded (no site exists for an unbuilt location).
* external.inspire_experiment for all twelve experiments (INSPIRE not contacted per STREAM_RULES); no people or membership rosters written.
* Result dates are arXiv v1 submission dates (date_kind preprint); journal references were not read except where a record note says so.

### Candidates considered and excluded or not assigned (CMB)

| candidate | decision | reason |
|---|---|---|
| COBE, WMAP, Planck, LiteBIRD | excluded | Space missions have no fixed site (A26). |
| Balloon-borne CMB experiments (BOOMERanG, MAXIMA, SPIDER, EBEX, PIPER, Taurus) | excluded | No fixed ground location (A26 inclusion bar: "at a fixed ground location"). |
| ABS (Atacama B-mode Search, Cerro Toco), QUIET (Chajnantor), CBI, QUaD (South Pole), ACBAR, TOCO / Python | not assigned: for the integrator | Completed ground-based CMB experiments with published results; in scope under A26 but outside this fork's assignment; each needs a researched site and dates. (The CLASS overview paper cited in the CLASS record names ABS as standing on Cerro Toco.) |
| Teide Observatory (Tenerife) CMB instruments: QUIJOTE, GroundBIRD, LSPE-STRIP, VSA | not assigned: for the integrator | In scope under A26; not researched; would need a Teide facility. |
| AliCPT (Ali CMB Polarization Telescope, Tibet) | not assigned: for the integrator | Possibly meets "under construction with a named site"; not researched; needs an Ali facility/site. |
| FYST / CCAT (Fred Young Submillimeter Telescope, Cerro Chajnantor) | not assigned: for the integrator | A submillimetre survey telescope with cosmology goals on the Chajnantor plateau; not researched; whether it is an HEP-relevant experiment under A26 is for the integrator to decide. |
| CMB-HD, SPT-3G+, South Pole Observatory | not assigned / not researched | Proposals or concepts mentioned in the literature; the bar needs a collaboration document or design report naming the site, which was not looked for. |
| SPT-SZ, SPTpol, SPT-3G as separate experiments | merged | Receivers of one telescope: phases of `experiment:spt`. |
| ACTPol, AdvACT as separate experiments | merged | Receivers of one telescope: phases of `experiment:act`. |
| POLARBEAR-2 as a separate experiment | merged | The Simons Array: phase of `experiment:polarbear` (the brief writes "POLARBEAR / Simons Array"). |
| SO:UK and SO:JP additional telescopes | not separate | Additions to the Simons Observatory (`experiment:simons-observatory` note). |


## Part 2. Dark-energy surveys (fork `de`)

### Scope

Ground-based dark-energy surveys under A26: DESI, DES, Rubin Observatory LSST, and the SDSS programme with its BOSS and eBOSS surveys; four observatory facilities (Kitt Peak, Cerro Tololo, Rubin, Apache Point) each with one telescope site; one instrument (detector) record per experiment; collaborations where a named body exists; headline results from the abstracts.

Counts written by this fork: 6 experiments, 5 detectors, 4 facilities, 4 sites, 4 collaborations, 9 results, 45 new source records.

#### Structure decisions

* **SDSS / BOSS / eBOSS.** The SDSS pages structure the programme as phases (SDSS-I/II 2000-2008, SDSS-III 2008-2014, SDSS-IV 2014-2020, SDSS-V 2020-) and call BOSS and eBOSS surveys *within* SDSS-III and SDSS-IV. Because BOSS and eBOSS have their own dates, target samples and dark-energy results, they are separate experiment records; `experiment:sdss` is the programme record with the four phases as `phase` intervals. BOSS and eBOSS each carry a `same_program` lineage row to `experiment:sdss` (on the lexicographically smaller id, A1), quoted from sdss.org. No eBOSS-predecessor-BOSS row is written: no fetched page uses the word predecessor or successor.
* **Rubin.** Rubin Observatory is operated by NSF NOIRLab and SLAC and has no single experiment collaboration, so the experiment record carries `collaboration:lsst-desc` (the LSST Dark Energy Science Collaboration, the named dark-energy body) and a note saying so.
* **DES.** The DES collaboration site (darkenergysurvey.org) returned HTTP 504 or timed out for every page except its home page, throughout the session, so DES dates and membership counts come from collaboration papers (arXiv) and a NOIRLab release.
* **Detectors.** One instrument record per experiment: the DESI focal-plane/fibre/spectrograph system, DECam, the Simonyi Survey Telescope with the LSST Camera, the SDSS 2.5-m telescope, and the BOSS spectrographs (shared by BOSS, eBOSS and SDSS).
* **Tiers.** DESI, DES and Rubin are tier B (researched at some depth, with the INSPIRE note); SDSS, BOSS and eBOSS tier C. INSPIRE was not contacted, so no `external.inspire_experiment` is set and every experiment note says why.

### Entities written

#### Experiments

| id | kind | status | tier | intervals (label: start to end) |
|---|---|---|---|---|
| experiment:desi | dark_energy_survey | active | B | DOE mission need approved (CD-0): 2012-09-18 to 2015-09-17 (proposed); performance baseline approved (CD-2): 2015-09-17 to 2016-06-22 (approved); construction: 2016-06-22 to 2019-10-22 (construction); commissioning: 2019-10-22 to 2020-12-14 (commissioning); survey validation: 2020-12-14 to 2021-05-14 (active); main survey (planned five years): 2021-05-14 to 2026-04-15 (active); extended survey: 2026-04-15 to (open) (active) |
| experiment:des | dark_energy_survey | completed | B | DES white paper (proposed survey): 2005-10 to 2008 (proposed); DECam construction: 2008 to 2012-09-12 (construction); first light and commissioning: 2012-09-12 to 2012-11-01 (commissioning); science verification: 2012-11-01 to 2013-02 (commissioning); survey observations (Y1 to Y6): 2013-08-15 to 2019-01-09 (active); observing completed: 2019-01-09 to (open) (completed) |
| experiment:rubin-lsst | dark_energy_survey | active | B | concept and community recommendation: 2001 to 2015 (proposed); construction: 2015 to 2025-10 (construction); system commissioning: 2025-03 to 2026-06-29 (commissioning); Legacy Survey of Space and Time: 2026-06-29 to (open) (active) |
| experiment:sdss | dark_energy_survey | active | C | first light and commissioning: 1998 to 2000 (commissioning); SDSS-I/II: 2000 to 2008 (active); SDSS-III: 2008 to 2014 (active); SDSS-IV: 2014 to 2020 (active); SDSS-V: 2020-10 to (open) (active) |
| experiment:boss | dark_energy_survey | completed | C | dark-time observations: Fall 2009 to Spring 2014 (active); observations completed: Spring 2014 to (open) (completed) |
| experiment:eboss | dark_energy_survey | completed | C | dark-time observations: 2014-07 to 2019-03 (active); observations completed: 2019-03 to (open) (completed) |

#### Dated intervals with their sources and quotes

| entity | interval | start | end | source URL | verbatim quote |
|---|---|---|---|---|---|
| experiment:desi | DOE mission need approved (CD-0) (proposed, verified) | 2012-09-18 | 2015-09-17 | https://arxiv.org/abs/2205.10939 | CD-0 Approve Mission Need 9/18/12 |
| experiment:desi | performance baseline approved (CD-2) (approved, verified) | 2015-09-17 | 2016-06-22 | https://arxiv.org/abs/2205.10939 | CD-2 Approve Performance Baseline 9/17/15 |
| experiment:desi | construction (construction, verified) | 2016-06-22 | 2019-10-22 | https://arxiv.org/abs/2205.10939 | CD-3 Approve Start of Construction 6/22/16 |
| experiment:desi | commissioning (commissioning, verified) | 2019-10-22 | 2020-12-14 | https://arxiv.org/abs/2205.10939 | Start of Commissioning 10/22/19 |
| experiment:desi | survey validation (active, verified) | 2020-12-14 | 2021-05-14 | https://arxiv.org/abs/2205.10939 | Start of Survey Validation 12/14/20 |
| experiment:desi | main survey (planned five years) (active, verified) | 2021-05-14 | 2026-04-15 | https://arxiv.org/abs/2205.10939, https://www.desi.lbl.gov/ | Start of the Main Survey 5/14/21 |
| experiment:desi | extended survey (active, verified) | 2026-04-15 | (open) | https://www.desi.lbl.gov/ | As of 15 April 2026, DESI has completed observations for its originally planned five-year survey. |
| experiment:des | DES white paper (proposed survey) (proposed, approximate) | 2005-10 | 2008 | https://arxiv.org/abs/astro-ph/0510346 | We describe the Dark Energy Survey (DES), a proposed optical-near infrared survey of 5000 sq. deg of the South Galactic Cap to ~24th magnitude in SDSS griz |
| experiment:des | DECam construction (construction, verified) | 2008 | 2012-09-12 | https://arxiv.org/abs/1504.02900 | in 2008 the project received approval from DOE to initiate construction |
| experiment:des | first light and commissioning (commissioning, verified) | 2012-09-12 | 2012-11-01 | https://arxiv.org/abs/1504.02900 | Official “First Light” was on the night of September 12 (UT), 2012. |
| experiment:des | science verification (commissioning, verified) | 2012-11-01 | 2013-02 | https://arxiv.org/abs/2101.05765, https://arxiv.org/abs/1601.00329 | Verification (SV) period (2012 November 1 through 2013 |
| experiment:des | survey observations (Y1 to Y6) (active, verified) | 2013-08-15 | 2019-01-09 | https://arxiv.org/abs/2601.14559 | between 2013 August 15 and 2019 January 9 |
| experiment:des | observing completed (completed, verified) | 2019-01-09 | (open) | https://noirlab.edu/public/news/noao1901 | On the night of 9 January 2019, the V. M. Blanco 4-meter telescope at the National Science Foundation’s (NSF) Cerro Tololo Inter-American Observatory (CTIO), high in the mountains of Chile, will close the camera’s shutter on the final image from the Dark Energy Survey (DES) |
| experiment:rubin-lsst | concept and community recommendation (proposed, approximate) | 2001 | 2015 | https://rubinobservatory.org/about/history | a 2001 report by the Astronomy and Astrophysics Survey Committee |
| experiment:rubin-lsst | construction (construction, verified) | 2015 | 2025-10 | https://rubinobservatory.org/about/history | In 2015 a traditional stone-laying ceremony was held on Cerro Pachón, in Chile, to commemorate the official start of construction. |
| experiment:rubin-lsst | system commissioning (commissioning, approximate) | 2025-03 | 2026-06-29 | https://rubinobservatory.org/about/history | In March 2025, the LSST Camera — the largest digital camera in the world — was installed on the telescope |
| experiment:rubin-lsst | Legacy Survey of Space and Time (active, verified) | 2026-06-29 | (open) | https://survey-strategy.lsst.io/progress/lsst/index.html, https://www.energy.gov/science/articles/action-nsf-doe-vera-c-rubin-observatory-begins-capturing-greatest-cosmic-movie | Rubin Observatory has begun the 10-year Legacy Survey of Space and Time (LSST) as of June 29, 2026. |
| experiment:sdss | first light and commissioning (commissioning, verified) | 1998 | 2000 | https://www.sdss.org/surveys/ | saw first light on its giant mosaic camera in 1998 and entered routine operations in 2000 |
| experiment:sdss | SDSS-I/II (active, verified) | 2000 | 2008 | https://www.sdss.org/surveys/ | SDSS: Prior Surveys (2000-2008) |
| experiment:sdss | SDSS-III (active, verified) | 2008 | 2014 | https://www.sdss.org/surveys/ | SDSS-III: Prior Surveys (2008-2014) |
| experiment:sdss | SDSS-IV (active, verified) | 2014 | 2020 | https://www.sdss.org/surveys/ | SDSS-IV: Surveys (2014-2020) |
| experiment:sdss | SDSS-V (active, verified) | 2020-10 | (open) | https://www.sdss.org/surveys/ | The SDSS-V Pioneering Panoptic Spectroscopy program started observing in October 2020 |
| experiment:boss | dark-time observations (active, verified) | Fall 2009 | Spring 2014 | https://www.sdss.org/surveys/boss/ | Dark time observations Fall 2009 - Spring 2014 |
| experiment:boss | observations completed (completed, verified) | Spring 2014 | (open) | https://www.sdss.org/surveys/boss/ | Dark time observations Fall 2009 - Spring 2014 |
| experiment:eboss | dark-time observations (active, verified) | 2014-07 | 2019-03 | https://www.sdss.org/surveys/eboss/ | Dark-time observations July 2014 – March 2019 |
| experiment:eboss | observations completed (completed, verified) | 2019-03 | (open) | https://www.sdss.org/surveys/eboss/ | Dark-time observations July 2014 – March 2019 |
| facility:kitt-peak-national-observatory | observatory founded (active, verified) | 1958 | (open) | https://noirlab.edu/public/programs/kitt-peak-national-observatory/ | Founded in 1958 |
| facility:cerro-tololo-inter-american-observatory | first observations (active, verified) | 1965 | (open) | https://noirlab.edu/public/programs/ctio/ | From the first observations in 1965 |
| facility:vera-c-rubin-observatory | concept and community recommendation (proposed, approximate) | 2001 | 2015 | https://rubinobservatory.org/about/history | a 2001 report by the Astronomy and Astrophysics Survey Committee |
| facility:vera-c-rubin-observatory | construction (construction, verified) | 2015 | 2025-10 | https://rubinobservatory.org/about/history | In 2015 a traditional stone-laying ceremony was held on Cerro Pachón, in Chile, to commemorate the official start of construction. |
| facility:vera-c-rubin-observatory | operations (active, verified) | 2025-10 | (open) | https://rubinobservatory.org/about/history | in October 2025, Rubin Observatory reached another defining moment: the official transition from construction to operations. |
| facility:apache-point-observatory | SDSS survey operations (active, verified) | 1998 | (open) | https://www.sdss.org/surveys/ | saw first light on its giant mosaic camera in 1998 and entered routine operations in 2000 |
| collaboration:desi | collaboration active (active, uncertain) | 2016-10 | (open) | https://arxiv.org/abs/1611.00036 | The DESI Experiment Part I: Science,Targeting, and Survey Design |
| collaboration:des | collaboration active (active, uncertain) | 2005-10 | (open) | https://arxiv.org/abs/astro-ph/0510346 | We describe the Dark Energy Survey (DES), a proposed optical-near infrared survey of 5000 sq. deg of the South Galactic Cap |
| collaboration:lsst-desc | collaboration active (active, uncertain) | 2012-11 | (open) | https://arxiv.org/abs/1211.0310 | This white paper describes the LSST Dark Energy Science Collaboration (DESC), whose goal is the study of dark energy and related topics in fundamental physics with data from the Large Synoptic Survey Telescope (LSST). |
| collaboration:sdss | collaboration active (active, approximate) | 2000 | (open) | https://www.sdss.org/surveys/ | saw first light on its giant mosaic camera in 1998 and entered routine operations in 2000 |
| detector:desi-instrument | construction (construction, verified) | 2016-06-22 | 2019-10-22 | https://arxiv.org/abs/2205.10939 | CD-3 Approve Start of Construction 6/22/16 |
| detector:desi-instrument | commissioning (commissioning, verified) | 2019-10-22 | 2020-12-14 | https://arxiv.org/abs/2205.10939 | Start of Commissioning 10/22/19 |
| detector:desi-instrument | operations (active, verified) | 2020-12-14 | (open) | https://arxiv.org/abs/2205.10939 | Start of Survey Validation 12/14/20 |
| detector:decam | construction (construction, verified) | 2008 | 2012-09-12 | https://arxiv.org/abs/1504.02900 | in 2008 the project received approval from DOE to initiate construction |
| detector:decam | operations (active, verified) | 2012-09-12 | (open) | https://arxiv.org/abs/1504.02900 | Official “First Light” was on the night of September 12 (UT), 2012. |
| detector:simonyi-survey-telescope-lsst-camera | construction (construction, verified) | 2015 | 2025-10 | https://rubinobservatory.org/about/history | In 2015 a traditional stone-laying ceremony was held on Cerro Pachón, in Chile, to commemorate the official start of construction. |
| detector:simonyi-survey-telescope-lsst-camera | operations (active, verified) | 2026-06-29 | (open) | https://survey-strategy.lsst.io/progress/lsst/index.html | Rubin Observatory has begun the 10-year Legacy Survey of Space and Time (LSST) as of June 29, 2026. |
| detector:sdss-2-5m-telescope | operations (active, verified) | 1998 | (open) | https://www.sdss.org/surveys/ | saw first light on its giant mosaic camera in 1998 and entered routine operations in 2000 |
| detector:boss-spectrographs | operations (active, verified) | Fall 2009 | (open) | https://www.sdss.org/surveys/boss/ | Dark time observations Fall 2009 - Spring 2014 |

#### Facilities, sites and coordinates

| id | kind / setting | status | coordinate (lat, lon, precision, kind) | altitude | source URL | verbatim quote (coordinate) |
|---|---|---|---|---|---|---|
| facility:kitt-peak-national-observatory (primary site:kitt-peak-mayall-telescope) | astronomical_observatory / mountain | active | 31.964028, -111.599889, 50 m, detector (verified) | 2123.2 m MSL | https://noirlab.edu/science/programs/kpno/telescopes/nicholas-mayall-4m-telescope | Coordinates 111º 35’ 59.6’W 31º 57’ 50.50’N |
| facility:cerro-tololo-inter-american-observatory (primary site:cerro-tololo-blanco-telescope) | astronomical_observatory / mountain | active | -30.168500, -70.804000, 50 m, detector (verified) | 2207 meters (7240 feet) | https://noirlab.edu/science/programs/ctio/telescopes/victor-blanco-4m-telescope | Coordinates 30°10.11'S 70°48.24'W |
| facility:vera-c-rubin-observatory (primary site:cerro-pachon-simonyi-survey-telescope) | astronomical_observatory / mountain | active | -30.245000, -70.749167, 200 m, detector (verified) | 2663 meters (8737 feet) | https://noirlab.edu/public/programs/vera-c-rubin-observatory/simonyi-survey-telescope/ | Coordinates 30º 14.7’S 70º 44' 57"W |
| facility:apache-point-observatory (primary site:apache-point-sdss-2-5m-telescope) | astronomical_observatory / mountain | active | 32.780361, -105.820417, 50 m, detector (verified) | 2788 m | https://www.sdss.org/instruments/ | Latitude 32° 46′ 49.30″ N, Longitude 105° 49′ 13.50″ W, Elevation 2788m |

#### Collaborations

| id | formation | member / institution / country counts | source |
|---|---|---|---|
| collaboration:desi | null (not sourced) | 1000 / 70 / 12 (as_of 2026-10, official_institution_list) | https://www.desi.lbl.gov/collaboration/, https://www.desi.lbl.gov/ |
| collaboration:des | null (not sourced) | 400 / 25 / null (as_of 2019-01, derived) | https://noirlab.edu/public/news/noao1901, https://www.darkenergysurvey.org/ |
| collaboration:lsst-desc | null (not sourced) | 1450 / null / 27 (as_of 2026-10, official_institution_list) | https://lsstdesc.org/, https://arxiv.org/abs/1211.0310 |
| collaboration:sdss | null (not sourced) | null / null / null (as_of None, derived) | https://www.sdss.org/collaboration/, https://www.sdss.org/surveys/, https://www.sdss.org/ |

#### Detectors

| id | experiments | site | technology class | status |
|---|---|---|---|---|
| detector:desi-instrument | experiment:desi | site:kitt-peak-mayall-telescope | spectrometer | active |
| detector:decam | experiment:des | site:cerro-tololo-blanco-telescope | other | active |
| detector:simonyi-survey-telescope-lsst-camera | experiment:rubin-lsst | site:cerro-pachon-simonyi-survey-telescope | other | active |
| detector:sdss-2-5m-telescope | experiment:sdss, experiment:boss, experiment:eboss | site:apache-point-sdss-2-5m-telescope | other | active |
| detector:boss-spectrographs | experiment:boss, experiment:eboss, experiment:sdss | site:apache-point-sdss-2-5m-telescope | spectrometer | active |

#### Results

| id | date (kind) | type | significance as stated | claim quote |
|---|---|---|---|---|
| result:boss-dr12-galaxy-clustering-cosmology-2016 | 2016-07-11 (preprint) | measurement | - | Combined with Planck 2015 cosmic microwave background measurements, our distance scale measurements simultaneously imply curvature {\Omega}_K =0.0003+/-0.0026 and a dark energy equation of state parameter w = -1.01+/-0.06, in strong affirmation of the spatially flat cold dark matter model |
| result:des-dynamical-dark-energy-2026 | 2026-05-26 (preprint) | measurement | 2.2σ deviation from a cosmological constant (full DES: SNe Ia, BAO and 3×2pt); 2.3σ with DESI DR2 BAO added; 3.0σ with primary CMB added | The combination yields $w_0=-0.84^{+0.10}_{-0.10}$ and $w_a=-0.44^{+0.60}_{-0.55}$, the tightest constraints ever obtained from a single survey, with $2.2\sigma$ deviation from a cosmological constant. |
| result:des-y3-3x2pt-cosmology-2021 | 2021-05-28 (preprint) | measurement | - | their combination yields clustering amplitude $S_8=0.776^{+0.017}_{-0.017}$ and matter density $\Omega_{\mathrm{m}} = 0.339^{+0.032}_{-0.031}$ in $\Lambda$CDM, mean with 68% confidence limits |
| result:des-y6-3x2pt-cosmology-2026 | 2026-01-21 (preprint) | measurement | 1.8σ (full-space) parameter difference from the CMB combination (Planck 2018, ACT-DR6, SPT-3G DR1); 2.6σ projected onto S8 | The combined analysis yields $S_8\equiv \sigma_8 (\Omega_{\rm m}/0.3)^{0.5} = 0.789^{+0.012}_{-0.012}$ and matter density $\Omega_{\rm m} = 0.333^{+0.023}_{-0.028}$ in $\Lambda$CDM (68\% CL) |
| result:desi-dr1-bao-cosmology-2024 | 2024-04-03 (preprint) | measurement | 2.6σ preference for w0 > -1 and wa < 0 from DESI+CMB; discrepant with ΛCDM at the 2.5σ, 3.5σ or 3.9σ levels when Pantheon+, Union3 or DES-SN5YR supernovae are added | This preference is 2.6$\sigma$ for the DESI+CMB combination, and persists or grows when SN~Ia are added in, giving results discrepant with the $\Lambda$CDM model at the $2.5\sigma$, $3.5\sigma$ or $3.9\sigma$ levels for the addition of Pantheon+, Union3, or DES-SN5YR datasets respectively. |
| result:desi-dr2-bao-cosmology-2025 | 2025-03-18 (preprint) | measurement | 3.1σ preference for the w0wa dynamical dark energy model over ΛCDM for DESI BAO + CMB; 2.8–4.2σ when also including SNe, depending on the SNe sample | This solution is preferred over $\Lambda$CDM at $3.1\sigma$ for the combination of DESI BAO and CMB data. When also including SNe, the preference for a dynamical dark energy model over $\Lambda$CDM ranges from $2.8-4.2\sigma$ depending on which SNe sample is used. |
| result:eboss-final-cosmological-implications-2020 | 2020-07-17 (preprint) | measurement | BAO data alone rule out dark-energy-free models at more than eight standard deviations (in an extension to flat ΛCDM allowing curvature) | We show that the BAO data alone are able to rule out dark-energy-free models at more than eight standard deviations in an extension to the flat, $\Lambda$CDM model that allows for curvature. |
| result:rubin-first-look-2025 | 2025-06-23 (announcement) | technology_milestone | - | On June 23, 2025, Rubin released its first public images and video in a globally coordinated release, anchored by a press conference in Washington, D.C. and livestreamed at more than 300 watch parties around the world. |
| result:sdss-lrg-baryon-acoustic-peak-2005 | 2005-01-10 (preprint) | measurement | - | We find a well-detected peak in the correlation function at 100h^{-1} Mpc separation that is an excellent match to the predicted shape and location of the imprint of the recombination-epoch acoustic oscillations on the low-redshift clustering of matter. |

### Conflicts

| claim | source A | source B | chosen | why |
|---|---|---|---|---|
| LSST start date | Rubin survey-strategy page: "as of June 29, 2026" | Rubin LSST page: "in June 2026"; Rubin About page: "in July 2026"; DOE Office of Science announcement dated 30 June 2026 | 2026-06-29 | The only day-precision statement from a Rubin page; the DOE blog date is the day after. The Rubin About page is the outlier (July). |
| Mayall telescope coordinates | NOIRLab science page: 31º 57’ 50.50’N, 111º 35’ 59.6’W, 2123.2 m MSL | NOIRLab public page: 31.9648° N, 111.5995° W, 2120 m | science page | More digits and an explicit MSL altitude; the two differ by under 100 m. |
| Rubin summit coordinates and altitude | NOIRLab Simonyi page: 30º 14.7’S 70º 44' 57"W, 2663 m | Ivezić et al. LSST overview (arXiv:0805.2366): S 30° 14′ 40.68″, W 70° 44′ 57.90″, 2652 m; NOIRLab Rubin Seeing Monitor page (different instrument): 30º 14' 41.27" S 70º 44' 51.80" W, 2612 m | NOIRLab Simonyi page (200 m precision) | Official facility page for the telescope itself; the three coordinate sets agree within ~200 m. |
| Blanco telescope start | NOIRLab Blanco page: "commissioned in 1974" (first light 1974) | NOIRLab release noao1901: "began operation in 1976" | not used | Not needed for any record; the CTIO facility interval uses "first observations in 1965". |
| End of DES observing | NOIRLab release (8 Jan 2019): final image "will" be taken on the night of 9 Jan 2019 | Y6 paper: allocated nights "between 2013 August 15 and 2019 January 9" | 2019-01-09 | Both agree on the date; the release is prospective, so the confidence note says no post-event page was fetched (darkenergysurvey.org down). |
| DES science-verification end | DES overview paper: "November 2012 to February 2013" | DES DR2 paper: SV period "2012 November 1 through 2013 February 22" | 2012-11-01 to 2013-02 (month precision) | The DR2 end date straddles a PDF column break so it cannot be quoted contiguously. |
| DESI collaboration formation | no source gives it | DESI instrument paper gives DOE CD-0 (2012-09-18) as the formal project start | formation null; interval lower bound 2016-10 (first DESI Collaboration paper fetched) | The project start is not the collaboration start. |

### Unresolved fields

* DESI, DES, LSST DESC and SDSS collaborations: formation dates (null with note); DESI leadership/institution roster; DES country count; SDSS member and institution counts ("hundreds of scientists at numerous institutions").
* DES: end of observing is dated from the 2019 NOIRLab release plus the Y6 allocation window; the DES website could not be fetched to confirm the final night. DES membership counts are lower bounds from the same release (member evidence class `derived`).
* Rubin: no single commissioning start date on the pages (March 2025 camera installation used, approximate); exact LSST start varies by page (see conflicts).
* Facility founding dates: Apache Point (no page gives one; the interval records the SDSS hosting start), Rubin (planning since the early 1990s; recorded from the 2001 recommendation).
* external.inspire_experiment for all six experiments (INSPIRE not contacted per STREAM_RULES); greybook ids not looked up.
* Instrument specs: detector `specs` only where the Atlas has a matching key (diameter); DESI fibre count, DECam pixel counts etc. are experiment `key_specs`. Sky coverage (deg²) cannot be a Quantity (no area unit deg²).
* No memberships/people rosters were written for any collaboration.
* Result publication dates are arXiv v1 submission dates (date_kind preprint); journal references were not read.

### Candidates considered and excluded

| candidate | decision | reason |
|---|---|---|
| Euclid, Nancy Grace Roman Space Telescope, SPHEREx, Planck, WMAP | excluded | Space missions have no fixed site (A26). |
| LSST as a separate experiment from "Rubin Observatory" | merged | One real thing (LSST is the Rubin survey; the Large Synoptic Survey Telescope was the project name before December 2019); recorded as `experiment:rubin-lsst` with aliases. |
| SDSS-V (Milky Way Mapper, Local Volume Mapper, Black Hole Mapper) | phase of experiment:sdss | A phase interval, not a separate experiment; its mappers are not dark-energy surveys. SDSS-V also uses the du Pont telescope at Las Campanas Observatory, Chile: site not recorded (for the integrator). |
| SDSS-I/II, SDSS-III, SDSS-IV as separate experiments | phases of experiment:sdss | Phases of one programme with one collaboration; BOSS and eBOSS are split out because they have their own results. |
| DESI Legacy Imaging Surveys (DECaLS, BASS, MzLS) | not assigned: for the integrator | Imaging inputs to DESI target selection obtained with DECam on the Blanco, the Bok 2.3-m and the Mayall; described in the DESI DR1 paper. Would be components of DESI, not stand-alone experiments. |
| DES Supernova Program (DES-SN), DES Y1/Y3/Y5 sub-analyses | part of experiment:des | Probes of the one survey; the Y5 SN results are not recorded as a separate result. |
| LSST DESC | recorded as a collaboration only | A science collaboration, not an experiment; attached to experiment:rubin-lsst. |
| HETDEX (Hobby-Eberly Telescope Dark Energy Experiment, McDonald Observatory, Texas) | not assigned: for the integrator | In scope (ground-based dark-energy spectroscopic survey) but outside this fork's assignment; needs a McDonald Observatory facility and site. |
| Hyper Suprime-Cam Subaru Strategic Program (Subaru, Maunakea) | not assigned: for the integrator | In scope (weak-lensing cosmology) but outside the assignment; needs a Subaru / Maunakea facility. |
| Subaru Prime Focus Spectrograph (PFS) cosmology survey | not assigned: for the integrator | In scope; needs a Subaru facility; status (operations start) not researched. |
| KiDS (Kilo-Degree Survey, VST at Paranal) | not assigned: for the integrator | In scope (weak lensing); needs an ESO Paranal VST site; the Paranal site record of CTAO-South exists but is not this telescope. |
| 4MOST, J-PAS, DESI-II / Spec-S5, MegaMapper | not assigned: for the integrator | In scope as under-construction or proposed ground-based spectroscopic surveys; each needs its own site and a design report naming it; not researched. |
| Pan-STARRS, ZTF, Dark Energy Camera Legacy Survey as standalone | not assigned: for the integrator | Time-domain and imaging surveys with dark-energy supernova programmes; mainly astronomy rather than HEP; not researched. |
| Earlier galaxy and supernova surveys (2dFGRS, 6dFGS, WiggleZ, VIPERS, SNLS, ESSENCE) | not assigned: for the integrator | Historical in-scope surveys with published BAO or supernova results; not researched; the SDSS-II/BOSS/eBOSS combination paper uses several of them as external data. |
| DESI Lyman-alpha DR2 key paper (30 July 2026 blog) | not recorded as a result | A companion paper to the DR2 BAO result already recorded; its arXiv abstract was not fetched. |

### For the integrator

* Topics `topic:cosmology`, `topic:dark-energy` (and `topic:cmb`) are referenced by every record in this slice and are created in `data/atlas/topics/cosmic-2.json` (Part 5); every reference resolves.
* Facility ids created: facility:kitt-peak-national-observatory, facility:cerro-tololo-inter-american-observatory, facility:vera-c-rubin-observatory, facility:apache-point-observatory (kind astronomical_observatory).
* Las Campanas Observatory (SDSS-V, du Pont telescope) is not created; a later stream could add it and a second SDSS placement.
* CTIO and Cerro Pachón are neighbouring NOIRLab sites; no `related_facility_ids` link between them is written (they are separate observatories).
* Rubin-derived records use `collaboration:lsst-desc`; if the integrator prefers an operations-partner record (NSF NOIRLab and SLAC) it can be added without changing the experiment id.
* Registry rows are in `data/atlas/coverage/cosmic-2.json` (6 rows for this part).

## Part 3. Cosmic-ray arrays (fork `cr`)

Builder: `scratchpad/cosmic2/build_cr.py` (+ `build_cr_exp.py`, `build_cr_res.py`, `build_cr_cov.py`).

### 1. Scope

Cosmic-ray (and cosmic-ray/gamma air-shower) experiments of A26: Fly's Eye, HiRes, AGASA, KASCADE and KASCADE-Grande, Tibet ASgamma, ARGO-YBJ, GRAPES-3, Tunka-133, TAIGA and the Yakutsk EAS array, with the six facilities the brief assigned
(`dugway-hires-site`, `akeno-observatory`, `yangbajing-cosmic-ray-observatory`, `ooty-cosmic-ray-laboratory`, `tunka-valley`, `yakutsk-eas-array`), their sites, collaborations where one is named, and headline results.
KASCADE and KASCADE-Grande sit at the existing `facility:kit-karlsruhe`/`site:kit-campus-north` (no separate site: the sources give 49.1 N, 8.4 E to 0.1 degree only). No existing record was edited.

Inclusion bar applied: named experiment; fixed ground location; published physics results; inside A26. Each new experiment has identity, dated intervals, a located site on a facility (through a detector `main` placement and `facility_roles`), topics, summaries, sources, a collaboration record where one is named, lineage where a source states it, and a coverage row. All are tier C (no INSPIRE ids were fetched; INSPIRE was never contacted).


### 2. Entities written

Counts: 11 experiments, 11 detectors, 8 collaborations, 6 facilities, 8 sites, 12 results, 48 sources (`src:c2-cr-*`), 11 coverage rows (in `data/atlas/coverage/cosmic-2.json`). Every date, coordinate and quantity carries a verbatim quote that the builder checked mechanically against the fetched page text (the build script raises if a quote is not a substring of the text it fetched on 2026-10-26).

#### 2.1 Facilities and sites

| entity | kind | status | primary site | key interval |
|---|---|---|---|---|
| `facility:dugway-hires-site` | astroparticle_observatory | completed | `site:dugway-hires-i` | first interval 'Fly's Eye I under construction' from 1978; ended 2006 |
| `facility:akeno-observatory` | astroparticle_observatory | active | `site:akeno-observatory` | first interval 'observatory operating' from 1977-04; open |
| `facility:yangbajing-cosmic-ray-observatory` | astroparticle_observatory | active | `site:yangbajing-cosmic-ray-observatory` | first interval 'Tibet air-shower arrays operating' from 1990; open |
| `facility:ooty-cosmic-ray-laboratory` | astroparticle_observatory | active | `site:ooty-cosmic-ray-laboratory` | first interval 'GRAPES-3 muon telescope operating' from 2000; open |
| `facility:tunka-valley` | astroparticle_observatory | active | `site:tunka-valley` | first interval 'air-Cherenkov experiments in the valley' from 1993; open |
| `facility:yakutsk-eas-array` | astroparticle_observatory | active | `site:yakutsk-eas-array-oktyomtsy` | first interval 'array operating' from 1973; open |

Coordinates and altitudes (every row is a verbatim quote from the cited page):

| site | lat, lon | kind / precision / confidence | altitude | URL | quote |
|---|---|---|---|---|---|
| `site:dugway-hires-i` | 40.19520, -112.83580 | detector / 100 m / verified | 1596 m | https://dpnc.unige.ch/ams/OLD_WebSite/ICRC-99/root/vol5/o4_5_13.pdf | HR1 -112.8358 W 40.1952 N 1596 |
| `site:dugway-hires-ii` | 40.13210, -112.95900 | detector / 100 m / verified | 1552 m | https://dpnc.unige.ch/ams/OLD_WebSite/ICRC-99/root/vol5/o4_5_13.pdf | HR2 -112.9590 W 40.1321 N 1552 |
| `site:dugway-flys-eye` | 40.00000, -113.00000 | campus / 60000 m / approximate | - | https://arxiv.org/abs/0706.1248 | The Fly’s Eye experiment was located at Dugway, Utah (40deg N, 113 deg W) |
| `site:akeno-observatory` | 35.78333, 138.50000 | detector / 3000 m / verified | 900 m | http://www-akeno.icrr.u-tokyo.ac.jp/AGASA/ | We constructed a very large surface array at the Akeno Observatory (35o 47' N, 138o 30' E) |
| `site:yangbajing-cosmic-ray-observatory` | 30.11056, 90.53056 | detector / 300 m / verified | 4300 m | https://argo.na.infn.it/argo_descr.html, https://www.icrr.u-tokyo.ac.jp/em/tibet_exp/exp_e.html | The site coordinates (latitude 300 06' 38'' N, longitude 900 31' 50'' E) |
| `site:ooty-cosmic-ray-laboratory` | 11.40000, 76.70000 | campus / 8000 m / approximate | 2200 m | https://arxiv.org/abs/2505.16440 | GRAPES-3 is a ground-based observatory located in the Nilgiri mountains in Ooty, India (11.4∘N, 76.7∘E, 2200 m above mean sea level). |
| `site:tunka-valley` | 51.49000, 103.04000 | campus / 2000 m / approximate | 670 m | https://arxiv.org/abs/2208.13757 | in the Tunka valley 50 km to the west from Lake Baikal (51.49 N, 103.04 E) |
| `site:yakutsk-eas-array-oktyomtsy` | 61.70000, 129.40000 | detector / 1500 m / verified | 100 m | https://ikfia.ysn.ru/en/eas/ | Geographical coordinates of the array are: latitude 61.70 N, longitude 129.40 E, 100 m above sea level (1020 g/cm2) |

#### 2.2 Experiments, intervals and the evidence behind each date

##### `experiment:flys-eye` - Fly's Eye (cosmic_ray) - status completed, tier C

Facility: `facility:dugway-hires-site`; collaboration: none (see notes); detector: `detector:flys-eye`.

| interval | status | start | end | URL | quote |
|---|---|---|---|---|---|
| Fly's Eye I construction | construction | 1978 | 1981 | https://indico.gssi.it/event/396/contributions/1289/attachments/694/1078/uhecr2022-history-v1-1.pdf | Construction of Fly’s Eye 1 1978-1981 |
| Fly's Eye operating | active | 1981 | 1992 | https://arxiv.org/abs/astro-ph/9806096 | which ran from 1981 to 1992 |
| data taking ended | completed | 1992 | - | https://arxiv.org/abs/astro-ph/9806096 | which ran from 1981 to 1992 |

##### `experiment:hires` - HiRes (cosmic_ray) - status completed, tier C

Facility: `facility:dugway-hires-site`; collaboration: `collaboration:hires`; detector: `detector:hires`.

| interval | status | start | end | URL | quote |
|---|---|---|---|---|---|
| HiRes prototype and MIA muon array (hybrid) | commissioning | 1993-08-23 | 1996-05-24 | https://arxiv.org/abs/astro-ph/0010652 | During the lifetime of this hybrid experiment between Aug. 23, 1993 and May. 24, 1996 |
| HiRes-I operation | active | 1997-05 | 2006 | https://dpnc.unige.ch/ams/OLD_WebSite/ICRC-99/root/vol5/o4_5_08.pdf, https://arxiv.org/abs/0706.1248 | The HiRes1 site has been in operation since May 1997 and has been collecting monocular data. |
| HiRes-II operation | active | Spring 1999 | 2006 | https://dpnc.unige.ch/ams/OLD_WebSite/ICRC-99/root/vol5/o4_5_08.pdf, https://arxiv.org/abs/0706.1248 | has been in operation since Spring 1999 |
| data taking ended | completed | 2006 | - | https://arxiv.org/abs/astro-ph/0703099 | operated on clear, moonless nights over a period of nine years (1997-2006) |

Lineage: `predecessor` -> `experiment:flys-eye` - A second-generation air fluorescence experiment, the High Resolution Fly’s Eye (HiRes) was proposed in the early 1990’s (https://arxiv.org/abs/0706.1248)

##### `experiment:agasa` - AGASA (cosmic_ray) - status completed, tier C

Facility: `facility:akeno-observatory`; collaboration: `collaboration:agasa`; detector: `detector:agasa`.

| interval | status | start | end | URL | quote |
|---|---|---|---|---|---|
| construction | construction | 1987 | 1990 | https://www.icrr.u-tokyo.ac.jp/prwps/about/history_eng.html | The construction of the 100km2 wide-area air shower detector, AGASA, started at the Akeno Observatory. |
| operation | active | 1990 | 2004-01 | https://www.icrr.u-tokyo.ac.jp/en/facility/4223/ | The AGASA had been in operation as the world's largest air-shower array for 13 years since 1990, but was terminated in January 2004 |
| operation ended | completed | 2004-01 | - | https://www.icrr.u-tokyo.ac.jp/en/facility/4223/ | The AGASA had been in operation as the world's largest air-shower array for 13 years since 1990, but was terminated in January 2004 |

##### `experiment:kascade` - KASCADE (cosmic_ray) - status completed, tier C

Facility: `facility:kit-karlsruhe`; collaboration: `collaboration:kascade`; detector: `detector:kascade`.

| interval | status | start | end | URL | quote |
|---|---|---|---|---|---|
| KASCADE operation | active | 1996 | 2012-12 | https://www.iap.kit.edu/kascade/english/index.php, https://arxiv.org/abs/1504.06696 | As an extension of the former KASCADE experiment running successfully since 1996 |
| data acquisition stopped | completed | 2012-12 | - | https://arxiv.org/abs/1504.06696 | KASCADE and its extension KASCADE-Grande stopped finally the active data acquisition of all its components including the radio EAS experiment LOPES end of 2012 after more than 20 years of data taking |

##### `experiment:kascade-grande` - KASCADE-Grande (cosmic_ray) - status completed, tier C

Facility: `facility:kit-karlsruhe`; collaboration: `collaboration:kascade-grande`; detector: `detector:kascade-grande`.

| interval | status | start | end | URL | quote |
|---|---|---|---|---|---|
| KASCADE-Grande operation | active | 2003-12 | 2012-12 | https://arxiv.org/abs/0906.4007, https://arxiv.org/abs/1504.06696 | The data presented here were taken from December 2003 to March 2009 |
| data acquisition stopped | completed | 2012-12 | - | https://arxiv.org/abs/1504.06696 | KASCADE and its extension KASCADE-Grande stopped finally the active data acquisition of all its components including the radio EAS experiment LOPES end of 2012 after more than 20 years of data taking |

Lineage: `upgrade_of` -> `experiment:kascade` - As an extension of the former KASCADE experiment running successfully since 1996, KASCADE-Grande was built by reassembling 37 stations of the former EAS-TOP experiment (https://www.iap.kit.edu/kascade/english/index.php)

##### `experiment:tibet-asgamma` - Tibet ASgamma (gamma_ray, secondary cosmic_ray) - status active, tier C

Facility: `facility:yangbajing-cosmic-ray-observatory`; collaboration: `collaboration:tibet-asgamma`; detector: `detector:tibet-asgamma`.

| interval | status | start | end | URL | quote |
|---|---|---|---|---|---|
| Tibet air-shower arrays (Tibet-I, -II, -III) | active | 1990 | - | https://arxiv.org/abs/astro-ph/0208107 | After three years of operation, starting in 1990, of the Tibet-I array |
| Tibet-III array | active | 1999 | - | https://arxiv.org/abs/0810.3757 | The Tibet-III air shower array, consisting of 533 scintillation detectors, has been operating successfully at Yangbajing in Tibet, China since 1999. |
| air-shower array with underground muon detectors | active | 2014 | - | https://arxiv.org/abs/1906.05521 | Since the beginning of 2014, a water-Cherenkov-type MD array with a total area of |

##### `experiment:argo-ybj` - ARGO-YBJ (gamma_ray, secondary cosmic_ray) - status completed, tier C

Facility: `facility:yangbajing-cosmic-ray-observatory`; collaboration: `collaboration:argo-ybj`; detector: `detector:argo-ybj`.

| interval | status | start | end | URL | quote |
|---|---|---|---|---|---|
| installation and commissioning | commissioning | 2006-06 | 2007-11 | https://arxiv.org/abs/0907.1164 | The ARGO-YBJ experiment started recording data with the whole central carpet in June 2006. The period until autumn 2007 has been mainly devoted to installation and debugging operations |
| stable data taking | active | 2007-11 | 2013-02 | https://arxiv.org/abs/1504.01510 | The ARGO-YBJ experiment has been in stable data taking from November 2007 till February 2013 |
| data taking ended | completed | 2013-02 | - | https://arxiv.org/abs/1504.01510 | The ARGO-YBJ experiment has been in stable data taking from November 2007 till February 2013 |

##### `experiment:grapes-3` - GRAPES-3 (cosmic_ray, secondary gamma_ray) - status active, tier C

Facility: `facility:ooty-cosmic-ray-laboratory`; collaboration: `collaboration:grapes-3`; detector: `detector:grapes-3`.

| interval | status | start | end | URL | quote |
|---|---|---|---|---|---|
| GRAPES-3 operation | active | 2000 | - | https://arxiv.org/abs/2505.16440 | In continuous operation since the year 2000 |

##### `experiment:tunka-133` - Tunka-133 (cosmic_ray) - status active, tier C

Facility: `facility:tunka-valley`; collaboration: `collaboration:taiga`; detector: `detector:tunka-133`.

| interval | status | start | end | URL | quote |
|---|---|---|---|---|---|
| Tunka-133 operation | active | 2009 | - | https://arxiv.org/abs/2104.03599 | is taking data since 2009 |

##### `experiment:taiga` - TAIGA (cosmic_ray, secondary gamma_ray) - status active, tier C

Facility: `facility:tunka-valley`; collaboration: `collaboration:taiga`; detector: `detector:taiga`.

| interval | status | start | end | URL | quote |
|---|---|---|---|---|---|
| TAIGA construction | construction | 2012 | 2022 | https://arxiv.org/abs/2208.13757 | In 2022, we completed the deployment and commissioning of the TAIGA-1 hybrid complex |
| TAIGA operation | active | 2013 | - | https://arxiv.org/abs/1903.07460 | was put into operation one year later, in 2013 |

Lineage: `same_program` -> `experiment:tunka-133` - the entire facility was later called TAIGA (Tunka Advanced Instrument for cosmic rays and Gamma Astronomy) (https://arxiv.org/abs/1903.07460)

##### `experiment:yakutsk-eas-array` - Yakutsk EAS array (cosmic_ray) - status active, tier C

Facility: `facility:yakutsk-eas-array`; collaboration: none (see notes); detector: `detector:yakutsk-eas-array`.

| interval | status | start | end | URL | quote |
|---|---|---|---|---|---|
| array operating | active | 1973 | - | https://arxiv.org/abs/2107.07528 | it has been continuously operating since 1973 |
| technical modernization | upgrade | 2019 | 2021 | https://arxiv.org/abs/2506.00517 | During the 2019-2021 period a significant technical modernization was conducted |

#### 2.3 Collaborations

| id | status | formation | note |
|---|---|---|---|
| `collaboration:hires` | completed | not published | No source read states a formation date. Dates are operating-period bounds, not formation dates. |
| `collaboration:agasa` | completed | not published | No source read states a formation date. Dates are operating-period bounds, not formation dates. |
| `collaboration:kascade` | completed | not published | No source read states a formation date. Dates are operating-period bounds, not formation dates. |
| `collaboration:kascade-grande` | completed | not published | No source read states a formation date. Dates are operating-period bounds, not formation dates. |
| `collaboration:tibet-asgamma` | active | not published | No source read states a formation date. Dates are operating-period bounds, not formation dates. |
| `collaboration:argo-ybj` | completed | not published | No source read states a formation date. Dates are operating-period bounds, not formation dates. |
| `collaboration:grapes-3` | active | not published | No source read states a formation date. Dates are operating-period bounds, not formation dates. |
| `collaboration:taiga` | active | not published | No source read states a formation date. Dates are operating-period bounds, not formation dates. |

#### 2.4 Results (claims quoted from abstracts)

| result | type | date (kind) | claim quote | significance |
|---|---|---|---|---|
| `result:agasa-spectrum-beyond-gzk-cutoff-1998` | measurement | 1998-07-18 (preprint) | The energy spectrum extends beyond 10^{20} eV and the energy gap between the highest energy event and the others is being filled up with recently observed events. | - |
| `result:argo-ybj-crab-nebula-five-years-2015` | measurement | 2015-02-19 (preprint) | The ARGO-YBJ air shower detector monitored the Crab Nebula gamma ray emission from 2007 November to 2013 February. | 21.1 standard deviations |
| `result:flys-eye-highest-energy-cosmic-ray-1995` | measurement | 1994-10-20 (preprint) | We report the detection of a 51-joule (320 +/- 90 EeV) cosmic ray by the Fly's Eye air shower detector in Utah. | - |
| `result:grapes-3-thundercloud-potential-2019` | measurement | 2019-03-23 (preprint) | Out of a total of 184 thunderstorms recorded during the interval April 2011-December 2014, the one on 1 December 2014 produced a massive potential of 1.3 GV. | - |
| `result:hires-gzk-suppression-2007` | observation | 2007-03-06 (preprint) | The High Resolution Fly's Eye (HiRes) experiment has observed the Greisen-Zatsepin-Kuzmin suppression (called the GZK cutoff) with a statistical significance of five standard deviations. | five standard deviations (5 sigma) |
| `result:kascade-grande-heavy-knee-2011` | observation | 2011-07-29 (preprint) | We report the observation of a steepening in the cosmic ray energy spectrum of heavy primary particles at about $8 \times 10^{16}$ eV. | - |
| `result:kascade-knee-light-elements-2005` | measurement | 2005-05-19 (preprint) | The resulting primary energy spectra show that the knee in the all particle spectrum is due to a steepening of the spectra of light elements | - |
| `result:taiga-crab-nebula-detection-2023` | measurement | 2023-01-26 (preprint) | A total of 163.5 excess events were detected, with a statistical significance of 8.5 sigma. | 8.5 sigma |
| `result:tibet-asgamma-crab-above-100-tev-2019` | first_detection | 2019-06-13 (preprint) | This is the first detection of photons with $E>100$ TeV from an astrophysical source. | 5.6 sigma statistical significance |
| `result:tibet-asgamma-diffuse-subpev-gamma-2021` | first_detection | 2021-04-12 (preprint) | We report, for the first time, the long-awaited detection of diffuse gamma rays with energies between 100 TeV and 1 PeV in the Galactic disk. | - |
| `result:tunka-133-energy-spectrum-2020` | measurement | 2020 (publication) | We present the all-particle energy spectrum, based on 7 seasons of operation. | - |
| `result:yakutsk-giant-showers-muon-excess-2025` | anomaly | 2025-05-31 (preprint) | These events have an abnormally high fraction of muons, which is beyond current model predictions. | - |
### 3. Conflicts (claim / source A / source B / chosen / why)

| claim | source A | source B | chosen | why |
|---|---|---|---|---|
| Fly's Eye start of data taking | 1981: Bird et al., arXiv:astro-ph/9806096, "which ran from 1981 to 1992" | 1982: Sokolsky & Thomson, arXiv:0706.1248, "The detectors were operated from 1982 to 1992"; Bertou et al., arXiv:astro-ph/0001516, "started to take data in 1982" | 1981, confidence `approximate` | the Fly's Eye group's own final paper; the one-year gap is stated in the interval note |
| Fly's Eye I - II spacing | 3.4 km: Bird et al. (1995, 1998) | 3.3 km: Sokolsky & Thomson (2007) | 3.4 km | the experiment's own papers |
| HiRes station separation and mirror area | 12.6 km, 3.7 m2 effective: HiRes PRL 100, 101101 (arXiv:astro-ph/0703099) | ~13 km, 3.8 m2: HiRes ICRC 1999 stereo paper; 12.5 km in a 2022 history talk | 12.6 km, 3.7 m2 | the collaboration's final, refereed paper |
| AGASA start of operation | 1990: ICRR Akeno Observatory page ("13 years since 1990") and ICRR chronology (completed 1990) | 1992: Anchordoqui et al., hep-ph/0206072; 1993: Sokolsky & Thomson ("Full operation ... began in 1993") | 1990 | the operating institute's own pages; the results page also dates the published data set to Feb. 17, 1990 - Jul. 31, 2002 |
| AGASA end | January 2004: ICRR | 2003: Rubtsov et al., astro-ph/0601449 ("operating from 1990 to 2003") | January 2004 | operator's statement |
| Yakutsk start | 1970: abstract of Alekseev et al., arXiv:2107.07528 | 1973: same paper's text; Glushkov et al. arXiv:0907.0374; 1974: arXiv:2506.00517 ("observation period of 1974-2024") | 1973 (approximate) | two independent statements agree; the others are in the interval note |
| Tibet ASgamma start | 1990 (Tibet-I array): Tibet ASgamma Collaboration, astro-ph/0208107 | ICRR chronology: "construction of air shower gamma ray detector in Tibet started" 1993, completed 1997; Tibet-III operating since 1999 (arXiv:0810.3757) | 1990 as the experiment's start, 1999 recorded as a phase | the collaboration's own paper; the ICRR dates are in the notes, not intervals, because a 1993 `construction` interval would override `active` under A3 |
| KASCADE duration | 1996-2012 (KIT IAP page: "running successfully since 1996"; KCDC: stopped end of 2012) | KCDC: "more than 20 years of data taking" | 1996-2012-12 | official page; the "more than 20 years" is not reconcilable and is flagged in the interval note |
| Tibet site coordinates | 90.53 E, 30.11 N: official Tibet AS-gamma page, astro-ph/0208107 | 90.522 E, 30.102 N: Tibet PRL 2019; 30 06' 38" N, 90 31' 50" E: ARGO-YBJ official page | ARGO's arcsecond point (30.1106 N, 90.5306 E), precision 300 m | all agree within ~1 km; one site serves both experiments |
| ARGO-YBJ cluster count | 153 vs 154 clusters in different papers | - | not recorded | not needed for the bar |
| Tibet sub-PeV paper identifier | brief: arXiv:1909.12535 | arXiv:1909.12535 is an unrelated computer-science preprint; the Tibet ASgamma paper "First Detection of sub-PeV Diffuse Gamma Rays from the Galactic Disk" is arXiv:2104.05181 (PRL 126, 141101) | 2104.05181 | read from the arXiv abstract pages |

Source-type choice worth review: the HiRes site coordinates come from the HiRes/Telescope Array ICRC 1999 paper on the Black Rock Hills R&D facility (`src:c2-cr-hires-icrc99-black-rock-hills`), filed as `detector_paper` (rank 5) so the `detector` coordinates do not rest on rank >= 8 (A17). It is a conference proceeding by the collaboration that tabulates the HiRes-I and HiRes-II positions; if the integrator prefers `journal_article` (rank 10), the two HiRes sites must become `campus`/`approximate`.

### 4. Unresolved fields

* Fly's Eye I and II: no coordinates beyond "about 40 N, 113 W"; `site:dugway-flys-eye` is a region marker (`kind: campus`, `approximate`, 60 km precision), the closest allowed kind. No collaboration name or website. Start 1981 vs 1982.
* HiRes: no working official website (www.cosmic-ray.org redirects to an unrelated dynamic-DNS host; Utah and Rutgers pages did not respond); collaboration formation, institution and member counts, leadership. The names of the HiRes-I hill are not given in any source read (the HiRes-II site is "Camel's Back Ridge" in the ICRC 1999 paper; the HiRes prototype sat "atop Little Granite Mountain" per the HiRes-MIA paper) so no hill name is recorded for HiRes-I.
* AGASA: collaboration formation, leadership person record (M. Teshima is marked spokesperson on the member page; no person record created).
* KASCADE / KASCADE-Grande: array-level coordinates; start of construction; collaboration formation; the web.ikp.kit.edu pages did not resolve (the KIT IAP page was used).
* Tibet ASgamma: no start date on the official page; reconciliation of 1990 and 1993-1997; continued operation in 2026 is not stated in any source read (last papers 2021).
* ARGO-YBJ: start of construction; collaboration formation; spokesperson person records.
* GRAPES-3: official site did not resolve; site coordinates only to 0.1 degree; start of the scintillator array (the 2000 start is the muon telescope's); formation date; roster.
* Tunka-133 / TAIGA: positions of individual detectors; official TAIGA site (404); collaboration formation; confirmation that Tunka-133 still takes data (last statement April 2021).
* Yakutsk: station-level coordinates; start year (1970/1973/1974); no named collaboration.
* Facilities: Akeno, Yangbajing, Ooty, Tunka and Yakutsk founding dates are taken from the first documented operation of the first hosted array, not from a founding statement (the Akeno Observatory's own date, April 1977, is sourced); operators are recorded only for Akeno (ICRR) and Yakutsk (Shafer Institute).

### 5. Candidates considered and excluded (or not assigned)

Excluded from new records, with reasons:

| candidate | decision | reason |
|---|---|---|
| IceTop | excluded | already covered: `detector:icetop` and `experiment:icecube` exist |
| Pierre Auger Observatory, Telescope Array, HAWC, LHAASO, H.E.S.S., MAGIC, VERITAS, CTAO | excluded | already present; no duplicates written (checked ids and names) |
| HiRes prototype and MIA muon array (1993-1996) | folded in | recorded as a commissioning phase of `experiment:hires` (hybrid with the Michigan Muon Array, Aug. 23, 1993 - May 24, 1996) |
| Tibet-I, Tibet-II, Tibet-III, high-density array, Tibet burst detector, underground muon-detector array | folded in | arrays of one collaboration at one site; phases/subsystems of `experiment:tibet-asgamma` |
| Tunka-4, Tunka-13, Tunka-25 | folded in | pathfinder arrays of the Tunka facility (TAIGA lecture); phases of the facility, no results of their own read |
| Tunka-Rex, Tunka-Grande, TAIGA-HiSCORE, TAIGA-IACT, TAIGA-MUON, Tunka-21cm | folded in | the TAIGA collaboration's lecture lists them as setups of one facility; recorded as subsystems of `detector:taiga` |
| LOPES (radio extension at KASCADE-Grande) | not assigned: for the integrator | named experiment with results at the KIT campus (KCDC abstract says "the radio EAS experiment LOPES"); outside the brief's list, not researched |
| Piccolo trigger array, KASCADE muon tracking detector, calorimeter | folded in | components of KASCADE(-Grande) |
| second GRAPES-3 muon telescope | excluded | recent proceedings mention a new telescope in progress; not read in full, so not recorded |

Not assigned (named in the brief, or found while reading; in scope of A26 and likely to meet the bar, not researched by this fork, for the integrator or another stream):

* CASA-MIA (Dugway Proving Ground; the HiRes-MIA paper places the surface arrays 3.4 km from the HiRes prototype) - candidate for `facility:dugway-hires-site`.
* EAS-TOP (Campo Imperatore, Gran Sasso; "running between 1987 and 2000" per the KIT KASCADE-Grande page; its 37 electromagnetic stations became Grande).
* MACRO-EAS (joint MACRO/EAS-TOP shower work at Gran Sasso) - not researched.
* Haverah Park (England; "ceased operation in July 1987 after a life of 19 years", Anchordoqui et al., hep-ph/0206072).
* Volcano Ranch (New Mexico; John Linsley's array; first coincident air-fluorescence observations, per the Sokolsky history talk).
* SUGAR (Sydney University Giant Air-shower Recorder, Australia; mentioned in hep-ph/0206072 and arXiv:0710.5508).
* Akeno 1 km2 array (1979-1990, the predecessor of AGASA at the same observatory; ICRR chronology says "completed" in 1979) - a candidate for `facility:akeno-observatory`.
* TALE (Telescope Array Low-energy Extension) - a component of Telescope Array, covered or to be covered inside that record.
* ASHRA (Hawaii), GAMMA and MAKET-ANI (Mount Aragats, Armenia; the KCDC page says MAKET-ANI data are now served by KCDC), ALPACA (Chacaltaya, Bolivia), the Baksan, Tien-Shan and Pamir stations, NEVOD-EAS - not researched by this fork; listed so the integrator can check them against the bar.

### 6. For the integrator

* `experiment:telescope-array` should list `experiment:agasa` as `predecessor`: the ICRR Akeno Observatory page (https://www.icrr.u-tokyo.ac.jp/en/facility/4223/) says AGASA was terminated in January 2004 "while handing over the observation to its larger scale hybrid successor Telescope Array (TA) in Utah, USA". This fork did not edit an existing record.
* `facility:kit-karlsruhe` has only a 2019 interval (KATRIN), so the validator warns that `experiment:kascade` (1996) and `experiment:kascade-grande` (2003-12) predate their facility. A founding or "KASCADE hosted" interval on that facility would clear it; the KIT IAP page (https://www.iap.kit.edu/kascade/english/index.php) gives 1996 for KASCADE.
* The Telescope Array Middle Drum fluorescence detector uses refurbished HiRes hardware; not sourced here, so no lineage row is written.
* ICRR chronology (https://www.icrr.u-tokyo.ac.jp/prwps/about/history_eng.html) also gives dates for the gamma-ray fork's CANGAROO ("The Cangaroo project started in Australia" in 1992; CANGAROO-2 began operation in 1999; four CANGAROO-3 telescopes completed in 2003). Passing on only.
* Topics: all topic ids used exist (`topic:cosmic-rays`, `topic:gamma-rays`, `topic:astroparticle-physics`); `topic:cosmology`, `topic:cmb`, `topic:dark-energy` are not referenced by any record of this fork.
* Coverage rows are in `data/atlas/coverage/cosmic-2.json` (owner `cosmic-2`, 11 rows for this part).
* Brief correction: the Tibet ASgamma sub-PeV paper is arXiv:2104.05181 (see conflicts).
* Facility naming: `facility:yangbajing-cosmic-ray-observatory` is named "Yangbajing Cosmic Ray Observatory" after the ARGO-YBJ detector paper's abstract; aliases carry "Yangbajing High Altitude Cosmic Ray Laboratory" (ARGO-YBJ's official page) and "Yangbajing International Cosmic Ray Observatory". `facility:dugway-hires-site` is named "Dugway Proving Ground (Fly's Eye and HiRes site)", the name the HiRes papers use ("U.S. Army Dugway Proving Ground").
* Site precision: all arXiv-sourced array positions (Ooty, Tunka valley, KASCADE via the campus site) are region-grade and appear on the globe as "approximate location"; surveyed positions would come from the collaborations.

### 7. Checks run

* Builder raises on any quote that is not a verbatim (whitespace-normalised) substring of the fetched page text; no quote was typed from memory (an early quote with an "2 steradians" gap was rejected by this check - the PDF text reads "2 pi steradians" with a garbled glyph - and replaced).
* `python -m hepgraph.atlas.validate`: no errors on any file of this fork; remaining findings on these files are warnings only (`coordinate-kind-approximate` x3 for the Fly's Eye, Ooty and Tunka sites; `experiment-before-facility` x2 for KASCADE at KIT; "no listed accelerator or beamline" on the cosmic-ray experiments, the same as every existing cosmic-ray record).
* `python -m hepgraph.atlas.build --out <scratch>` completed (version recorded in the scratch output only); nothing under `static/atlas/generated/` was written or committed.
* Pathspec commits: 3e01bb9 (sources, facilities, sites, experiments, detectors, collaborations) and 46ac8c3 (results and collaboration summary fixes).
## Part 4. Gamma-ray experiments (fork `gr`)


### Scope

Ground-based gamma-ray experiments assigned by the brief: Milagro (Fenton Hill, existing facility `facility:los-alamos-national-laboratory`), HEGRA (Roque de los Muchachos, existing `facility:roque-de-los-muchachos-observatory`), Whipple 10 m (existing `facility:fred-lawrence-whipple-observatory`), CANGAROO (new `facility:woomera-cangaroo-site`), MACE and HAGAR (new `facility:hanle-observatory`). SWGO and IceTop were handled by the parent (Part 5). No INSPIRE page was contacted; no coverage or topic file of the parent was written.

Written: 6 experiments, 6 detectors, 4 collaborations (MACE and HAGAR have no named collaboration in any source fetched), 2 new facilities, 5 new sites, 11 results, 29 new source records (two sources were reused by URL from other streams: the VERITAS timeline page and the HAWC design paper). Coverage rows: in `data/atlas/coverage/cosmic-2.json`.

### Entities written

#### Facilities and sites

| id | kind / setting | interval | coordinate (kind, confidence, precision) | quote and URL behind the coordinate |
|---|---|---|---|---|
| facility:woomera-cangaroo-site | astroparticle_observatory (new) | active 1992 to 2011; completed 2011 to open | primary site site:woomera-cangaroo | - |
| facility:hanle-observatory | astroparticle_observatory (new) | active 2008-09 to open | primary site site:hanle-gamma-ray-site | - |
| site:lanl-fenton-hill-milagro | site on facility:los-alamos-national-laboratory; mountain | - | 35.88, -106.68 (campus, approximate, 600 m) | "The detector was located at 106.68o W longitude, 35.88o N latitude in northern New Mexico at an altitude of 2630 m above sea level" - https://arxiv.org/abs/1110.0409 |
| site:roque-de-los-muchachos-hegra | site on facility:roque-de-los-muchachos-observatory; mountain | - | 28.75, -17.89 (detector, verified, 1000 m) | "(2200 m a.s.l., 28.750 N, 17.890 W) covering an area of about 200m · 200m" - https://arxiv.org/abs/astro-ph/9702059 |
| site:mount-hopkins-whipple-10m | site on facility:fred-lawrence-whipple-observatory; mountain | - | 31.6833, -110.8833 (campus, approximate, 2000 m) | "at the Whipple Observatory on Mt. Hopkins in southern Arizona (31∘ 41’ north, 110∘ 53’ west, alt = 2300 m)" - https://arxiv.org/abs/astro-ph/9602068 |
| site:woomera-cangaroo | site on facility:woomera-cangaroo-site; surface | - | -31.1, 136.7833 (campus, approximate, 2000 m) | "operated in Woomera, South Australia (longitude 136◦ 47′ E, latitude 31◦ 06′ S, 160 m a.s.l.)" - https://arxiv.org/abs/0712.3094, https://arxiv.org/abs/1207.6003 |
| site:hanle-gamma-ray-site | site on facility:hanle-observatory; mountain | - | 32.77944, 78.97639 (detector, verified, 100 m) | "Hanle in Ladakh, India (32^0 46^' 46^" N, 78^0 58^' 35^" E) at an altitude of 4270 m a.s.l." - https://arxiv.org/abs/1701.01120 |

#### Experiments (dates as of 2026-10-26)

| experiment | status | site | interval | start .. end | quote and URL |
|---|---|---|---|---|---|
| experiment:milagro | completed | site:lanl-fenton-hill-milagro | construction (construction; approximate) | - .. 1999 (approx.) | "The construction of the Milagro pond was completed in early 1999, and operations began in mid 1999." - https://arxiv.org/abs/astro-ph/0110513 |
|  |  |  | operation (active; verified) | 1999 (approx.) .. 2008 | "The construction of the Milagro pond was completed in early 1999, and operations began in mid 1999." - https://arxiv.org/abs/astro-ph/0110513, https://arxiv.org/abs/1110.0409 |
|  |  |  | data taking ended (completed; verified) | 2008 .. - | "operated from 2000 to 2008" - https://arxiv.org/abs/1110.0409 |
| experiment:hegra | completed | site:roque-de-los-muchachos-hegra | data taking (active; verified) | 1987 .. 2002 | "With its various types of detectors HEGRA was taking data between 1987 and 2002." - https://www.mpi-hd.mpg.de/hfm/HEGRA/ |
|  |  |  | data taking ended (completed; verified) | 2002 .. - | "With its various types of detectors HEGRA was taking data between 1987 and 2002." - https://www.mpi-hd.mpg.de/hfm/HEGRA/ |
| experiment:whipple-10m | decommissioned | site:mount-hopkins-whipple-10m | construction (construction; verified) | 1966 .. 1968 | "1966-68 Fazio and Weekes: Installation of SAO's Whipple 10m telescope at Mt. Hopkins; first purpose-built large reflector for TeV Gamma-ray Astronomy" - https://veritas.sao.arizona.edu/about-veritas/history-timeline |
|  |  |  | operation (active; verified) | 1968 .. 2013 | "this telescope was in operation from 1968 until its decommissioning in 2013" - https://veritas.sao.arizona.edu/whipple |
|  |  |  | gamma-ray programme closed down (shutdown; verified) | 1976 .. 1982 | "1976-82 Whipple/SAO gamma-ray program closed down" - https://veritas.sao.arizona.edu/about-veritas/history-timeline |
|  |  |  | telescope decommissioned (decommissioned; verified) | 2013 .. - | "this telescope was in operation from 1968 until its decommissioning in 2013" - https://veritas.sao.arizona.edu/whipple |
| experiment:cangaroo | completed | site:woomera-cangaroo | CANGAROO operations (active, lifecycle; verified) | 1992 .. 2011 | "It started from a 3.8-m telescope[1] (CANGAROO-I) in 1992." - https://arxiv.org/abs/astro-ph/0107578 |
|  |  |  | CANGAROO-I (3.8 m telescope) (active, phase; verified) | 1992 .. 1998 | "operated from 1992 to 1998 near Woomera, South Australia" - https://arxiv.org/abs/0906.4924 |
|  |  |  | CANGAROO-II (10 m mount, 7 m mirror) (active, phase; verified) | 1999 .. 2000 | "The second stage, CANGAROO- II, commenced in 1999 with the construction of a 10 m telescope mount with a mirror initially of 7 m diameter. The mirror was extended to 10 m in 2000" - https://arxiv.org/abs/astro-ph/0107578 |
|  |  |  | CANGAROO-III (10 m telescopes) (active, phase; verified) | 2000-03 .. 2011 | "The first telescope of this array is the upgraded version of the CANGAROO-II 7 m telescope and has been in operation since March 2000." - https://arxiv.org/abs/astro-ph/0106346 |
|  |  |  | observing activities ended (completed; verified) | 2011 .. - | "Eventually, the activities in Australia were stopped in 2011." - https://arxiv.org/abs/1207.6003 |
| experiment:mace | active | site:hanle-gamma-ray-site | installation and commissioning (construction; approximate) | - .. 2021-09 (approx.) | "which is presently being installed at Hanle in Ladakh, India" - https://arxiv.org/abs/1701.01120 |
|  |  |  | regular observations (active; verified) | 2021-09 .. - | "has been carrying out regular observations of Crab Nebula since September 2021" - https://arxiv.org/abs/2404.01649 |
| experiment:hagar | active | site:hanle-gamma-ray-site | regular observations (documented to December 2017) (active; verified) | 2008-09 .. 2017-12 | "Regular source observations are running since September 2008." - https://www.astrophys-space-sci-trans.net/7/501/2011/astra-7-501-2011.html |
|  |  |  | operation after 2017 (not documented) (active; uncertain) | 2017-12 .. - | "The HAGAR telescopes (Singh, et al. 2019) are located in Hanle in the Himalayas at 4500 m above sea level, on the same site as the 21 m diameter Cherenkov imaging telescope MACE" - https://arxiv.org/abs/2406.15037 |

#### Collaborations

| collaboration | status | formation | interval | quote and URL |
|---|---|---|---|---|
| collaboration:milagro | completed | not published | collaboration active (active; uncertain) 1999 (approx.) .. 2008 | "The construction of the Milagro pond was completed in early 1999, and operations began in mid 1999." - https://arxiv.org/abs/astro-ph/0110513 |
|  |  |  | data taking ended (completed; verified) 2008 .. - | "operated from 2000 to 2008" - https://arxiv.org/abs/1110.0409 |
| collaboration:hegra | completed | not published | collaboration active (active; approximate) 1987 .. 2002 | "With its various types of detectors HEGRA was taking data between 1987 and 2002." - https://www.mpi-hd.mpg.de/hfm/HEGRA/ |
|  |  |  | data taking ended (completed; verified) 2002 .. - | "With its various types of detectors HEGRA was taking data between 1987 and 2002." - https://www.mpi-hd.mpg.de/hfm/HEGRA/ |
| collaboration:whipple | completed | 1982 | collaboration active (active; approximate) 1982 .. 2013 | "1982 Whipple Collaboration formally constituted (Hawaii, Iowa State, SAO, U.C. Dublin, Durham)" - https://veritas.sao.arizona.edu/about-veritas/history-timeline |
|  |  |  | telescope decommissioned (completed; approximate) 2013 .. - | "this telescope was in operation from 1968 until its decommissioning in 2013" - https://veritas.sao.arizona.edu/whipple |
| collaboration:cangaroo | completed | not published | collaboration active (active; approximate) 1992 .. 2011 | "It started from a 3.8-m telescope[1] (CANGAROO-I) in 1992." - https://arxiv.org/abs/astro-ph/0107578 |
|  |  |  | observing activities ended (completed; verified) 2011 .. - | "Eventually, the activities in Australia were stopped in 2011." - https://arxiv.org/abs/1207.6003 |

#### Detectors

One per experiment: `detector:milagro`, `detector:hegra`, `detector:whipple-10m`, `detector:cangaroo-iii`, `detector:mace`, `detector:hagar`. Each carries a `main` placement at the experiment's site, technology class(es), specs (quoted) and the same dated intervals as its experiment.

#### Results (11)

| result | type | date (kind) | significance as the source states it | claim quote |
|---|---|---|---|---|
| result:cangaroo-3p8m-reanalysis-2009 | measurement | 2009-06-26 (preprint) | 4.5 sigma (Vela pulsar region, 1993-1995 data); no significant signal for PSR B1706-44 or the northeast rim of SN 1006 | "no significant TeV gamma-ray signals have been detected from compact regions around PSR B1706-44 or within the northeast rim of SN 1006" (https://arxiv.org/abs/0906.4924) |
| result:cangaroo-iii-rxj0852-2006 | observation | 2006-08-21 (preprint) | - | "We confirm the H.E.S.S. results about the morphology and the energy spectrum, and find the energy spectrum in the NW-rim is consistent with that of the whole remnant." (https://arxiv.org/abs/astro-ph/0608422) |
| result:hagar-crab-detection-2019 | measurement | 2019-02-04 (preprint) | about 20 sigma | "we report the detection of $\gamma$-rays from the Crab Nebula at a significance level of about 20$\sigma$, corresponding to a time averaged flux of (1.64$\pm$0.09) $\times10^{-10}$ photons cm$^{-2}$ sec$^{-1}$ above 230 GeV" (https://arxiv.org/abs/1902.01081) |
| result:hegra-cassiopeia-a-evidence-2001 | evidence | 2001-02-22 (preprint) | 5 sigma level | "TeV gamma ray emission was detected at the 5 sigma level, and a flux of (5.8 +- 1.2(stat) +- 1.2(syst)) 10^(-9) ph m^(-2) s^(-1) above 1 TeV was derived." (https://arxiv.org/abs/astro-ph/0102391) |
| result:hegra-crab-spectrum-2004 | measurement | 2004-07-06 (preprint) | - | "The spectrum extends up to energies of 80 TeV and is well matched by model calculations in the framework of inverse Compton scattering of various seed photons in the nebula" (https://arxiv.org/abs/astro-ph/0407118) |
| result:mace-crab-first-light-2024 | first_detection | 2024-04-02 (preprint) | - | "Here we report the detection of Very High Energy (VHE) gamma-ray emission from Crab Nebula above 80 GeV." (https://arxiv.org/abs/2404.01649) |
| result:milagro-10tev-excess-2008 | discovery | 2008-01-24 (preprint) | greater than 12 sigma significance (two localized regions); one region differs in spectrum from the isotropic cosmic-ray flux at 4.6 sigma | "An analysis of 7 years of Milagro data performed on a 10-degree angular scale has found two localized regions of excess of unknown origin with greater than 12 sigma significance." (https://arxiv.org/abs/0801.3827) |
| result:milagro-crab-background-rejection-2003 | observation | 2003-05-16 (preprint) | - | "The technique is used to detect TeV emission from the Crab nebula." (https://arxiv.org/abs/astro-ph/0305308) |
| result:milagro-cygnus-region-2006 | discovery | 2006-11-21 (preprint) | MGRO J2019+37: about 6 standard deviations above the average diffuse emission in the region (Cygnus region excess: 10.9 standard deviations) | "The TeV image shows at least one new source MGRO J2019+37 as well as correlations with the matter density in the region as would be expected from cosmic-ray proton interactions." (https://arxiv.org/abs/astro-ph/0611691) |
| result:whipple-crab-observation-1989 | observation | 1989 (publication) | 9.0 sigma | "a detection is reported at the 9.0-sigma level, corresponding to a flux of 1.8 x 10 to the -11th photons sq cm/s above 0.7 TeV (with a factor of 1.5 uncertainty in both flux and energy)" (https://mural.maynoothuniversity.ie/12618) |
| result:whipple-mrk421-detection-1992 | first_detection | 1992-08-06 (publication) | - | "We report here the detection of such photons from an extragalactic source, the giant elliptical galaxy Markarian 421." (https://www.nature.com/articles/358477a0) |


### Conflicts (claim / source A / source B / chosen / why)

| claim | source A | source B | chosen | why |
|---|---|---|---|---|
| Milagro start of operations | arXiv:astro-ph/0110513: "operations began in mid 1999"; the pond "has operated continuously since Jan. 2000" | arXiv:1110.0409 and the HAWC design paper (arXiv:1310.0074): "operated from 2000 to 2008" | start mid-1999 (approximate), end 2008 | the status paper is the detector's own report of when the pond began running; the 2000-2008 figure is a rounded span, and both agree on 2008. |
| Milagro altitude | status paper: "8,600 feet" (= 2621 m) | arXiv:1110.0409 and arXiv:astro-ph/0403097: 2630 m | 2630 m | stated in metres in two collaboration papers. |
| HEGRA start of data taking | MPIK official page: "taking data between 1987 and 2002" | arXiv:2406.15037: first telescope camera mid-1992, AIROBICC 1992-2002, five-telescope array completed 1997 | 1987 to 2002 for the experiment | the official page covers all detector types (the scintillator array was the first); individual instruments start later and are noted in the interval note. |
| HEGRA number of imaging telescopes | official page: six in operation | arXiv:astro-ph/9704098 and arXiv:astro-ph/0407118: system of five identical telescopes | six for the complex, five noted for the stereoscopic system | the sources count different things (CT1 plus the five-telescope system). |
| HEGRA position | arXiv:astro-ph/9702059: 28.750 N, 17.890 W | arXiv:astro-ph/9901199: 28.8 N, 17.9 W | 28.75 N, 17.89 W | finer value from the collaboration's experiment description. |
| Whipple 10 m site altitude | VERITAS basecamp record (existing site): 1268 m | arXiv:astro-ph/9602068: 31 41 N, 110 53 W, alt = 2300 m for the 10 m telescope | separate new site at 2300 m | the 10 m telescope was on the mountain, not at the basecamp where VERITAS stands. |
| Whipple 10 m start | Whipple page: "in operation from 1968" | VERITAS timeline: "1966-68 ... Installation of SAO's Whipple 10m telescope at Mt. Hopkins" | construction 1966-68, active 1968-2013 | the two sources describe installation and operation; both kept. |
| Whipple gamma-ray activity | Whipple page: "in operation from 1968 until its decommissioning in 2013" | timeline: "1976-82 Whipple/SAO gamma-ray program closed down" | active interval 1968-2013 plus a `shutdown` interval 1976-82 | the telescope existed throughout; the gamma-ray programme was dormant. |
| CANGAROO site altitude | four collaboration papers: 160 m a.s.l. | arXiv:2406.15037: 165 m (CANGAROO-I dark site 12 km north of Woomera); arXiv:astro-ph/0107578 table: 220 m | 160 m | most frequent and the one in the position string of the collaboration's own papers. |
| CANGAROO latitude | arXiv:astro-ph/0106346 prints "31 06 E" | arXiv:0712.3094 and arXiv:1207.6003: 31 06 S | south | the hemisphere letter in the status paper is a misprint (Woomera is in South Australia). |
| CANGAROO end | arXiv:1207.6003: "the activities in Australia were stopped in 2011" | arXiv:2406.15037: "A few years later this array terminated its operation" (no year) | 2011 | only dated statement; single source (see unresolved). |
| MACE first light | a proceedings abstract seen in a web search: April 2021 (not fetched) | arXiv:2404.01649: "regular observations of Crab Nebula since September 2021" | September 2021 | only the fetched collaboration paper is used. |
| Hanle altitude | MACE and HAGAR papers: 4270 m | arXiv:1110.6795: 4300 m; arXiv:2406.15037: 4500 m | 4270 m | the instrument papers. |
| Whipple Mrk 421 significance | Nature abstract text: "6er above background" | - | none recorded | the symbol is garbled in the retrieved abstract; not copied (rule: never invent). |
| CANGAROO early detections | CANGAROO-I papers (PSR B1706-44, SN 1006; not fetched) | arXiv:0906.4924 (collaboration reanalysis): "no significant TeV gamma-ray signals have been detected from compact regions around PSR B1706-44 or within the northeast rim of SN 1006"; Vela pulsar region 4.5 sigma | the reanalysis is recorded as a result; the original detections are not | the collaboration's own later paper does not support them; arXiv:2406.15037 says H.E.S.S. "could not confirm some of the CANGAROO results". |

### Unresolved (left null or flagged in the records)

* Milagro: construction start; collaboration formation date and member counts; outrigger tank count and installation date (the 2011 paper says the central reservoir was operated alone 2000-2004); a survey-grade position for the pond (only 0.01 degrees is published, so the site is `campus`/`approximate`).
* HEGRA: formation date and member counts; construction start; start dates of AIROBICC, the scintillator array and the muon towers.
* Whipple 10 m: dates of the camera upgrades (37, 109, 379 pixels); a telescope-pad position better than 1 arcminute (site is `campus`/`approximate`).
* CANGAROO: live official website (host no longer resolves; only an Internet Archive capture); telescope-level coordinates (site is `campus`/`approximate`); the date the four-telescope array became operational (only the 2001 plan for 2004 and the statement that T4 was operating after the 2004 observations); the 2011 end rests on one review.
* MACE: named collaboration, official website, start of construction, first-light date.
* HAGAR: named collaboration, official website, separate coordinate (shares the Hanle site), whether observations continue after December 2017 (second interval is `uncertain`).
* INSPIRE experiment ids for all six (INSPIRE was not contacted); all six rows are tier C so none is required.

### Candidates considered and not written

Everything below was judged against the inclusion bar (named, fixed ground site, published results or approved/under construction, in A26). "Not assigned" means the brief gave the item to the parent or the integrator, or it is outside this fork's list; the facts come from the Mirzoyan review (arXiv:2406.15037, https://arxiv.org/abs/2406.15037) unless noted.

| candidate | status of this fork's decision | reason / what the sources say |
|---|---|---|
| VERITAS, H.E.S.S., MAGIC, CTAO, HAWC, LHAASO | already in the Atlas | not duplicated. |
| STACEE (Sandia solar tower, New Mexico) | not assigned: for the integrator | review: solar-plant gamma-ray detector; "they stopped operating shortly afterwards"; dates, site coordinates and a primary source not fetched. Meets the bar in principle (named, fixed, published results). |
| CACTUS (California), CELESTE (France), GRAAL (Germany, Spain) | not assigned: for the integrator | the other three solar-plant Cherenkov experiments named in the review; CELESTE measured the Crab down to about 60 GeV (the review says its flux was underestimated by a factor 2.5). Sites and dates not fetched. |
| THEMISTOCLE (Themis, southern France) | not assigned: for the integrator | 18 widely spaced tracking telescopes, measured the Crab; same site as ASGAT and CAT. Dates not fetched. |
| ASGAT (Themis) | not assigned: for the integrator | non-imaging predecessor on the Themis site; no dates fetched. |
| CAT (Themis) | not assigned: for the integrator | imaging telescope with a 600-pixel camera, commissioned late 1996, "a successful telescope"; end date and a primary paper not fetched. Meets the bar. |
| GAMMA (Armenia, Aragats) | not assigned: not researched | no source fetched. |
| PACT (Pachmarhi, India) | not assigned: for the integrator | THEMISTOCLE-like array (Singh et al. 2009 cited in the review); dates and site not fetched. |
| TACTIC (Mt Abu, India) | not assigned: for the integrator | 9.5 m2 reflector, 349-pixel camera, "operating since 2001", reported source detections; strong candidate (named, fixed, results). Current status not fetched. |
| SHALON (Tien Shan) | not assigned: reliability | claimed operational since 1993; the review says its results "did not stand up to critical discussion or comparison with any other known results"; not recommended for inclusion without a primary source. |
| Japanese 7-Telescope Array (Dugway, Utah) | not assigned: for the integrator | three of seven telescopes installed 1996-1997 at the Dugway proving grounds, took data on Mrk 501 and 1ES 1959 in 1997, destroyed-container accident ended operations at the end of 1997; same area as Fly's Eye and HiRes (the cr fork's `facility:dugway-hires-site`). Published results not fetched. |
| CLUE (HEGRA site) | not assigned | nine 1.8 m telescopes with TMAE chambers, operated 1997-1999; reported the Crab, Mrk 421, Mrk 501 and the lunar shadow; HEGRA-site experiment. Primary paper not fetched. |
| Durham Mark 6 | not assigned: for the integrator | three-dish telescope, discovered PKS 2155-304 (Chadwick et al. 1999 per the review); site and dates not stated in the sources fetched. |
| BIGRAT, PeV-X | not assessed | no source describing either was fetched or found; nothing is claimed about them. |
| Yerevan (YerPhI) 1989 telescope | not assigned | prototype for the HEGRA stereo array per the review; no standalone results fetched. |
| Space gamma-ray missions (Fermi-LAT, EGRET, AGILE) | out of scope | A26: no fixed ground site. |
| ARGO-YBJ, Tibet AS-gamma, GRAPES-3, TAIGA, Yakutsk | assigned to the cr fork | not touched. |
| SWGO, IceTop | assigned to the parent | not touched. |

### For the integrator

1. Lineage rows to add on **existing** records (A1: `predecessor` lives on the successor; I did not edit records of other streams):
   * `experiment:hawc`: `predecessor` -> `experiment:milagro`; source `src:cosmic-gamma-hawc-design-paper-arxiv-2013`, quote "MILAGRO experiment, HAWCs predecessor" (arXiv:1310.0074, PDF text).
   * `experiment:magic` and `experiment:h-e-s-s`: `predecessor` -> `experiment:hegra`; source `src:c2-gr-hegra-official-page`, quote "A successor to the HEGRA Cherenkov telescopes is being built up at the HEGRA site: MAGIC. A direct successor to the stereoscopic system of Cherenkov telescopes is the H.E.S.S. experiment."
   * `experiment:veritas`: `predecessor` -> `experiment:whipple-10m`; source `src:c2-gr-whipple-official-page`, quote "The predecessor to VERITAS (Very Energetic Radiation Imaging Telescope Array System), this telescope was in operation from 1968 until its decommissioning in 2013".
2. Validator warnings that remain on this fork's files are by design: `coordinate-kind-approximate` (3 sites: Fenton Hill, Whipple 10 m, Woomera), `interval-start-unknown` (Milagro and MACE construction), `experiment-without-active-beam` (all six gamma-ray experiments, as for HAWC), `experiment-before-facility` for HEGRA and Whipple 10 m because the existing ORM and FLWO facility records start in 2003 (their own intervals reflect VERITAS and MAGIC/CTAO only; extending those facility intervals needs sources for the founding dates).
3. Source typing: five arXiv papers that describe the instrument itself are typed `detector_paper` (astro-ph/0110513, astro-ph/9702059, astro-ph/9704098, astro-ph/0106346, 1701.01120) and one `design_report` (astro-ph/0107578). The HEGRA site (`detector`, 1 km) and the MACE/Hanle site (`detector`, 100 m) rest on those; the Milagro, Whipple and Woomera coordinates rest on physics papers and are therefore `campus`/`approximate` (A23). Re-type or downgrade if the integrator disagrees.
4. Internet Archive sources: `src:c2-gr-milagro-official-page-wayback` and `src:c2-gr-cangaroo-official-page-wayback` are captures (the live pages are gone); the experiment `links.website` fields point at the captures with `confidence: approximate`.
5. Build size: a scratch build of this branch (all forks' files at the time) gave atlas.json + manifest.json = 1,230,784 bytes; the build fails above 1.5 MB (ontology section 8). The rest of the wave may push it over; the lazily loaded bundles are where growth is meant to go.
6. Quote extraction: quotes taken from PDFs come from `pdftotext` and keep its artifacts (for example "106.68o W", degree signs, "CANGAROO- II" at a line break); they are verbatim against the fetched text.
7. Coverage rows for the six experiments are in `data/atlas/coverage/cosmic-2.json` (owner cosmic-2, tier C).

### Checks run

* `python -m hepgraph.atlas.validate`: no errors on any file of this fork (the whole-tree validator line at the end of the stream is in Part 6).
* `python -m hepgraph.atlas.build --out <scratch dir>`: succeeds; static/atlas/generated was not touched.
## Part 5. SWGO, IceTop and topics (parent)

### 5.1 SWGO

SWGO (Southern Wide-field Gamma-ray Observatory) is in the brief only "if its site selection is sourced". It is: the collaboration's site-selection page announces the Atacama Astronomical Park, Pampa La Bola, on 12 August 2024, and the 2025 science paper (a design document with the baseline design) names the site. It is `proposed`: the sources say planning for construction "has begun", and none reports that construction started. Written: experiment, detector, collaboration, site `site:swgo-pampa-la-bola` on `facility:parque-astronomico-atacama` (created by the CMB fork), 6 sources (`src:c2-swgo-*`), one coverage row. Builder: `build_swgo.py`.

| entity | field | value | source URL | verbatim quote |
|---|---|---|---|---|
| experiment:swgo | interval 'R&D collaboration; observatory proposed' (proposed, verified) | 2019-07-01 to (open) | https://www.swgo.org/SWGOWiki/doku.php?id=press_release_en | Today, July 1st 2019, 39 research institutions from nine countries signed the agreement for the creation of a new international R&D collaboration for a future wide field-of-view gamma ray observatory in the southern hemisphere. |
| experiment:swgo | facility role | host of facility:parque-astronomico-atacama (announced 12 August 2024) | https://www.swgo.org/SWGOWiki/doku.php?id=site_press_release | announced that the Atacama Astronomical Park in Chile was selected as the site of the observatory. |
| collaboration:swgo | interval 'R&D collaboration' (active, verified) | 2019-07-01 to (open) | https://www.swgo.org/SWGOWiki/doku.php?id=press_release_en | Today, July 1st 2019, 39 research institutions from nine countries signed the agreement for the creation of a new international R&D collaboration for a future wide field-of-view gamma ray observatory in the southern hemisphere. |
| collaboration:swgo | formation | 2019-07-01 | https://www.swgo.org/SWGOWiki/doku.php?id=press_release_en | Today, July 1st 2019, 39 research institutions from nine countries signed the agreement for the creation of a new international R&D collaboration for a future wide field-of-view gamma ray observatory in the southern hemisphere. |
| collaboration:swgo | country_count | 16 (as_of 2026-10) | https://www.swgo.org/SWGOWiki/doku.php?id=collaboration | More than 90 research institutions from 16 countries have signed the agreement for the international R&D collaboration |
| collaboration:swgo | institution_count | 90 (as_of 2026-10) | https://www.swgo.org/SWGOWiki/doku.php?id=collaboration | More than 90 research institutions from 16 countries have signed the agreement for the international R&D collaboration |
| site:swgo-pampa-la-bola | coordinate | -22.9, -67.7875, precision 25000 m, campus (approximate) | https://arxiv.org/abs/2309.03053 | Pampa La Bola (current primary, elevation 4,750 m.a.s.l., 22.9° S) |
| site:swgo-pampa-la-bola | altitude | 4770 m | https://www.swgo.org/ | At an altitude of 4770 m. |
| detector:swgo | placement | site:swgo-pampa-la-bola (main, approximate) | https://www.swgo.org/ | Located in Atacama Astronomical Park, Chile. |

**Conflicts (SWGO).**

| claim | source A | source B | chosen | why |
|---|---|---|---|---|
| Latitude of Pampa La Bola | ICRC 2023 site paper (arXiv:2309.03053) text: "22.9° S" (elevation 4,750 m) | ICRC 2021 table (arXiv:2111.13158): "22.56 S"; ICRC 2023 overview table (arXiv:2309.04577): "22.25 S" | 22.9 deg S, with 25 km precision | The three print different digits for one site, probably different notations (degrees and minutes versus decimal degrees); the point is a regional anchor, and the note on the coordinate says so. |
| Altitude | SWGO home page and the 2024 site-selection page: 4,770 m | 2023 site paper: 4,750 m (the site was then still a candidate) | 4770 m | The collaboration's own pages after selection. |
| Number of partner countries | SWGO collaboration page: 16 countries | Michigan Tech release (August 2024) and the site-selection page list 15 | 16 | The collaboration page is the later and official statement (the Netherlands is listed there). |

**Unresolved (SWGO).** The longitude and a surveyed position of Pampa La Bola (no fetched source gives the longitude; the site point borrows the longitude of the sourced ACT position on Cerro Toco, in the same park, and says so); the array layout and tank counts (the design is not final); construction start (the August 2024 page says official efforts toward construction were "expected as early as 2026" and observations "before the end of the decade", both plans); INSPIRE experiment id (not contacted); no person records for the spokespersons.

**Why not `approved`?** No source consulted says the experiment is funded for construction. The collaboration page describes an R&D collaboration, and the site-selection page says that funding "will come from science agencies of participating nations".

### 5.2 IceTop (excluded)

`detector:icetop` already exists as a sub-array of `detector:icecube` under `experiment:icecube` (parent detector, kind `air_shower_array`, status active), so IceTop is covered by the IceCube records and is not duplicated.

### 5.3 Topics (`data/atlas/topics/cosmic-2.json`)

Three topics, depth 2: `topic:cosmology` (root), `topic:cmb` and `topic:dark-energy` (children). Sources are the Review of Particle Physics 2026 sections 25 (Cosmological Parameters), 28 (Dark Energy) and 29 (Cosmic Microwave Background), fetched as PDFs on 2026-10-26 (`src:topic-pdg-2026-cosmological-parameters`, `-dark-energy`, `-cosmic-microwave-background`; the section numbers follow the PDF headings). Each number or claim in an overview was checked against the PDF text; the anchors are:

| topic | claim in the overview | verbatim anchor in the PDG text |
|---|---|---|
| topic:cosmology | Matter and Lambda density parameters (Planck column) | Ωm                  0.315 ± 0.007              0.300 ± 0.004 |
| topic:cosmology | five to ten parameters | Typical comparisons of cosmological models with observational data now feature between five and ten parameters. |
| topic:cosmology | Hubble tension and evolving dark energy not securely established | Existing indications against it, such as the Hubble tension and hints of evolving dark energy, are not securely established |
| topic:cmb | discovered 1965; T = 2.7255 K | discovered in 1965 |
| topic:cmb | anisotropy levels | temperature anisotropies at the 10−5 level and polarization anisotropies at the 10−6 (and lower) level |
| topic:cmb | temperature mapping wrapping up | the program to map temperature anisotropies is effectively wrapping up, and attention is increasingly focusing on polarization measurements |
| topic:cmb | E and B modes | inflationary scalar perturbations give only E modes, while tensors generate roughly equal amounts of E and B |
| topic:cmb | tensor-to-scalar limit | The current limit on the tensor-to-scalar ratio is r . 0.04 |
| topic:cmb | sensitivity goal | pushing down to a sensitivity level of r ∼ 0.001 |
| topic:dark-energy | supernova evidence | supernova surveys by two independent teams provided direct evidence for accelerating cosmic expansion |
| topic:dark-energy | DESI operations and sample | DESI began full operations in May 2021, and its three-year data set includes over 30 million galaxies and quasars |
| topic:dark-energy | BAO-CMB tension | DESI Collaboration reports a tension of about 2σ between BAO and CMB alone |
| topic:dark-energy | significance for DESI+CMB | this difference corresponds to a frequentist significance of 3.1σ assuming Gaussian error distributions |
| topic:dark-energy | range with supernovae | to 4.2σ, but using the Pantheon+ SNe instead of DES reduces the significance to 2.8σ |

Not claimed in the topics: any value not printed by the PDG sections above; the PDG statements about the Planck satellite and LiteBIRD are not used as Atlas facts (satellites are out of scope, A26).

## Part 6. For the integrator, and checks run

### 6.1 Lineage rows to add on existing records

A1 keeps `predecessor` on the successor. The brief asks for lineage where a source states it, but the successors below are records of other streams, so they were left untouched (STREAM_RULES, Ownership). Each row is ready to paste; the quotes are verbatim from the cited sources.

| on record | relation | to | source | verbatim quote |
|---|---|---|---|---|
| experiment:hawc | predecessor | experiment:milagro | src:cosmic-gamma-hawc-design-paper-arxiv-2013 (arXiv:1310.0074, PDF text) | MILAGRO experiment, HAWCs predecessor |
| experiment:magic | predecessor | experiment:hegra | src:c2-gr-hegra-official-page | A successor to the HEGRA Cherenkov telescopes is being built up at the HEGRA site: MAGIC. |
| experiment:h-e-s-s | predecessor | experiment:hegra | src:c2-gr-hegra-official-page | A direct successor to the stereoscopic system of Cherenkov telescopes is the H.E.S.S. experiment. |
| experiment:veritas | predecessor | experiment:whipple-10m | src:c2-gr-whipple-official-page | The predecessor to VERITAS (Very Energetic Radiation Imaging Telescope Array System), this telescope was in operation from 1968 until its decommissioning in 2013 |
| experiment:telescope-array | predecessor | experiment:agasa | the ICRR Akeno Observatory page (https://www.icrr.u-tokyo.ac.jp/en/facility/4223/), cited by `experiment:agasa` | while handing over the observation to its larger scale hybrid successor Telescope Array (TA) in Utah, USA |

The fork logs above (Parts 3 and 4) give the same rows with their locators. The ICRR page quote was read by the cosmic-ray fork (see its "For the integrator" list in Part 3).

### 6.2 Other items

* **Bundle size.** `atlas.json` + `manifest.json` is 1,240,164 bytes with this stream, against 1,024,842 bytes at the base commit (`bb673ea`): +215,322 bytes for 36 experiments, 13 facilities and 23 sites. The build fails above 1.5 MB (ontology section 8). The other coverage streams (c1 to c7) will add more, so the merge is likely to cross the limit. The integrator should expect to raise the limit or move fields into the lazily loaded bundles. `static/atlas/generated/` was not committed.
* **Validator warnings left on this stream's files are by design:** `coordinate-kind-approximate` (sites with campus-grade or region-grade points: Fly's Eye, Ooty, Tunka valley, Fenton Hill, Whipple 10 m, Woomera, POLARBEAR, CLASS, SWGO and others), `interval-start-unknown`, `experiment-without-active-beam` (the generic "no accelerator or beamline" rule that every existing cosmic-ray record also gets), and `experiment-before-facility` for KASCADE (KIT facility starts 2019), HEGRA (Roque de los Muchachos starts 2003) and Whipple 10 m (Whipple Observatory starts 2003). Extending those three facility intervals needs sourced founding dates, which belong to the streams that own those facilities.
* **Brief correction.** The Tibet ASgamma sub-PeV paper is arXiv:2104.05181; the id 1909.12535 in the brief is an unrelated preprint. The result record uses 2104.05181.
* **Approximate coordinates.** `site:south-pole-dark-sector` (pole anchor, 1000 m) shares its anchor with `site:south-pole-icecube` and `site:south-pole-ara`, so the globe draws three markers on one point. `site:swgo-pampa-la-bola` is a 25 km regional anchor (Part 5).
* **Result typing.** `result:bicep2-b-mode-detection-claim-2014` is typed `anomaly` (the 2014 paper is titled "Detection of B-mode Polarization", and the 2015 joint analysis found "strong evidence for dust and no statistically significant evidence for tensor modes"); the record says so. The integrator may prefer another type.
* **CMB-S4 status.** Recorded as `cancelled` (an Atlas enum). The agencies' wording is quoted in the record: "DOE and NSF have jointly decided that they can no longer support the CMB-S4 Project", dated 9 July 2025 on the project page.
* **Facility interplay.** Parque Astronomico Atacama hosts ACT, the Simons Observatory, POLARBEAR / Simons Array, CLASS and (proposed) SWGO; CMB-S4 has a facility role on this facility and on the South Pole station, but no site exists for an unbuilt location in Chile, so only the South Pole placement is drawn.
* **Not written, in scope under A26 and not assigned** (details with reasons in Parts 1 to 4): HETDEX, Subaru HSC and PFS, KiDS, 4MOST, J-PAS, DESI-II / Spec-S5, Pan-STARRS, ZTF, ABS, QUIET, CBI, QUaD, Teide-site CMB instruments, AliCPT, FYST / CCAT, CASA-MIA, EAS-TOP, Haverah Park, Volcano Ranch, SUGAR, TALE, ASHRA, GAMMA (Armenia), STACEE, CELESTE, CAT, TACTIC, THEMISTOCLE, PACT and the Japanese 7-Telescope Array. Space missions (Planck, WMAP, COBE, Euclid, Roman, SPHEREx, LiteBIRD) and balloon payloads are excluded by A26.

### 6.3 Checks run

* `python -m hepgraph.atlas.validate`: **0 errors**, 1649 warnings, 4 informational (the base commit has 0 errors, 1596 warnings). Run on the whole tree after the last record was written.
* `python -m hepgraph.atlas.build --out <scratch>`: succeeds (81 files; version `9f306e13e948d15b` in the scratch output only). `static/atlas/generated/` was not written in the worktree or committed.
* `python -m pytest -q`: 689 passed, 139 skipped (PostgreSQL-backed tests skip without a throwaway database, as CLAUDE.md says).
* Independent quote audit (parent): 895 quotes and claim quotes across all 36 experiments, 35 detectors, 24 collaborations, 13 facilities, the sites and 46 results; each is a verbatim substring of the fetched text of a cited source (script `audit_quotes2.py` in the scratch directory). The three source excerpts present were checked too.
* Nothing was fetched from inspirehep.net; no Neon, Vercel or deployment command was run.
