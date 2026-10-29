# De-Wikipedia stream (branch `atlas-dewiki`)

Every citation of Wikipedia has been removed from the Atlas. Each value that rested on a Wikipedia article now cites a primary source and quotes it, or has been changed to what the primary source says, or has been removed. The 48 Wikipedia source records are deleted, and the validator now fails any source on wikipedia.org (`source-wikipedia`, error).

## Result

| | |
| --- | ---: |
| Wikipedia source records deleted | 48 |
| Records that cited them (107 JSON files) | 107, all logged below |
| Log rows | 344 |
| replaced: same value, now backed by a primary source | 90 |
| redundant: a primary source already in the record stated it; the Wikipedia id was dropped | 18 |
| changed: the primary source states something different | 46 |
| removed: no primary source found | 4 |
| unlisted: id only in the record-level `sources` list, nothing rested on it | 55 |
| reworded: prose that credited Wikipedia or relied on a Wikipedia-only fact | 131 |
| New source records | 57 (`src:dw-*`; an existing record is reused whenever its URL matches) |

Checks: `python -m hepgraph.atlas.validate` ends `0 errors, 1894 warnings, 4 informational` (baseline before this stream: 0 errors, 1925 warnings); the one new warning is `sites-too-close` on `site:baksan-sage-underground-lab` (see integrator notes). `python -m pytest -q`: 785 passed, 139 skipped (the skips need a PostgreSQL URL). `python -m hepgraph.atlas.build` succeeds; `static/atlas/generated` is not committed.

## How the work was done

Nine group agents each owned a disjoint set of records and re-fetched the primary sources. Every quote in this table was machine-checked as a verbatim substring of the text curl returned for the cited URL (HTML stripped; PDF through pdftotext, whitespace collapsed; arXiv sources were checked against the `/pdf/` or `/html/` rendering when the record URL is the abstract page). Two exceptions are listed under the integrator notes. `verified_at` is `2026-10-26` on every new or changed value, as the brief requires; `accessed` on new source records is the day the page was actually read, 2026-10-28.

Rows below are grouped by agent. `old source` is the Wikipedia source id that was cited (or `(text)` for prose). `quote` and `URL` are the NEW source's; for `redundant` rows they are those of the primary source that already backed the value.

## Removed or left unresolved

| Record | Value | Old source | Leads tried |
| --- | --- | --- | --- |
| collaborations/sage.json | leadership/0 (Zatsepin): Georgiy Zatsepin as a leading physicist | sage-wikipedia | SAGE 2009 and 1999 author lists (arXiv:0901.2200, astro-ph/9907131); Gavrin and Cleveland arXiv:nucl-ex/0703012; CERN Courier Baksan 2017 (mentions him only for the observatory proposal); web search |
| sites/jlab-newport-news.json | summary/technical ("214-acre"): 214-acre campus | jlab-wikipedia | JLab virtual-tour page, JLab site-plan PDF and the JLab 40th-anniversary release (fetched): the release says "170+ acre"; a JLab facilities page seen in search results lists 206 acres; no consistent official figure, and the 214-acre value was Wikipedia-only. |
| facilities/oak-ridge-national-laboratory.json | summary/technical (~10,000 acres): ~10,000 acres | ornl-wikipedia | ORNL overview page (no acreage); DOE Office of Science and ORNL pages found by search give 4,000+/4,421 acres for the lab site and ~33,000 acres for the reservation, none matches the Wikipedia-only 10,000. |
| collaborations/ship.json | formation: 2013-10 | ship-wikipedia-pointer | arXiv:1310.1762 (EoI), arXiv:1504.04956 (TP), ship.web.cern.ch (no history page), CERN Courier 2016-02 (says only that the collaboration formed in the two years between EoI and TP) |

Not removed but still open (a value the primary sources do not state, kept `null` with a note): `collaboration:ship` `formation` (the 2013 Expression of Interest has 16 authors and does not name SHiP); `facility:chooz` `operator` (the 2022 detector paper names EDF only as operator of the adjacent power plant); the Double Chooz near hall has no published coordinate (a campus-grade proxy is used); SAGE hall has no published coordinate (3.5 km inside the mountain, adit-entrance point used); DONUT/OPERA/LEGEND collaboration formation dates stay `null`.

## Changed values (primary source differs from the Wikipedia value)

| Record | Field | Old value | New value | New source | Why |
| --- | --- | --- | --- | --- | --- |
| sites/slac-slc-collider-hall-sld.json | summary.technical | housing the SLD (SLAC Large Detector) (1989-1998) | SLD replaced Mark II in 1991 and ran until the SLC ended in June 1998 | slac-grad-handbook | "SLD 1989-1998" was the SLC period; the SLD itself arrived in 1991 (SLC termination June 1998 per the SLD-site SLC page). |
| facilities/brokdorf-nuclear-power-plant.json | summary.technical (1440 MWe) | 3.9 GWth / 1440 MWe pressurized water reactor | 3.9 GWth pressurised water reactor (1,480 MWe gross, 1,410 MWe net) | dw-nuklearesicherheit-brokdorf | The 1440 MWe figure was Wikipedia-only; the federal data sheet gives 1,480 MW gross / 1,410 MW net. |
| facilities/leibstadt-nuclear-power-plant.json | intervals/0 (reactor operation, start) | start 1984-05-24 (approximate) | start 1984-12-15 (start of continuous operation, verified) | dw-kkl-chronik | The operator's chronicle gives 15 Dec 1984 for the start of continuous operation; the 24 May 1984 date (Wikipedia 'commission date') is in no primary source found. |
| facilities/ill-grenoble.json | summary.technical (58.3 MW) and notes[1] | 58.3 MW research reactor (Wikipedia) | 58 MW thermal power | dw-ill-reactor-overview | ILL's own page says 58 megawatts thermal power (the Ricochet paper also says 58 MW); the 58.3 MW figure was Wikipedia-only. |
| sites/ill-grenoble-reactor-hall.json | coordinates | 45.206239, 5.692774 (Wikipedia infobox, approximate) | 45.206099, 5.692848 (OSM reactor-hall centroid, approximate, 100 m) | geo-ill-osm-reactor-hall | No coordinate published by ILL or the Ricochet paper; campus-grade OSM point instead (about 17 m from the old one). |
| sites/ill-grenoble-reactor-hall.json | summary.technical (58.3 MW) | ILL 58.3 MW research reactor | 58 MW thermal power | dw-ill-reactor-overview | Follows ILL's own figure; 58.3 MW was Wikipedia-only. |
| sites/brokdorf-nuclear-power-plant-campus.json | coordinates | 53.85083, 9.34472 (Wikipedia infobox, approximate) | 53.850777, 9.345842 (OSM reactor-building centroid, approximate, 100 m) | geo-reactors-osm-brokdorf-leibstadt-reactors | No operator or paper coordinate found; campus-grade OSM point instead (about 74 m east of the old one). |
| experiments/gallex-gno.json | unique_capabilities/0 | Radiochemical gallium target sensitive to the lowest-energy (pp) solar neutrinos, below the threshold of water-Cherenkov or chlorine-based detectors | Radiochemical gallium target with a 233 keV threshold, low enough to detect the lowest-energy (pp) solar neutrinos, below the roughly 0.8 MeV sensitivity of the chlorine experiment | dw-mpik-gallex-gno-history | The water-Cherenkov comparison is not stated by the page and was dropped; the chlorine comparison is stated. |
| experiments/gallex-gno.json | summary/technical | ...GALLEX 1991-1997 (73.1 SNU capture rate) then GNO 1998-2003 (62.9 SNU), led by the MPIK Heidelberg... | GALLEX re-evaluated 73.1 SNU; GNO 62.9 SNU; GALLEX headed by MPIK Heidelberg, GNO by the INFN Milano group | dw-mpik-gallex-gno-history | MPIK page: 73.1 SNU is the re-evaluated GALLEX result (original 77.5), GNO headed by the Milano group; GNO paper: 62.9 SNU. |
| detectors/homestake.json | specs/target_mass | null (only the 380 m3 / 100,000 gallon volume known) | 615 t perchloroethylene (C2Cl4) | dw-nobel-2002-physics-advanced-information | The Nobel Committee states the mass of the C2Cl4 filling, so the value is no longer left unset. |
| collaborations/homestake.json | leadership/0 | Raymond Davis Jr. and John N. Bahcall named as having headed the experiment (role spokesperson) | Raymond Davis Jr. (role other: built and administered the experiment); Bahcall no longer listed as a leader | vf-davis-nobel-biographical-2002 | Primary source credits Bahcall with the solar-model prediction, not leadership; no formal spokesperson title is stated. |
| collaborations/sage.json | leadership/0 | Vladimir Gavrin, Georgiy Zatsepin and Thomas J. Bowles named as leading physicists (role spokesperson) | Vladimir Gavrin (leads SAGE, as of 2017) and Thomas J. Bowles (led the American side), both role other | glossary-cern-courier-baksan-2017 | Bowles row: arXiv:nucl-ex/0703012 quote "We thank Thomas Bowles for leading the American side of the SAGE collaboration for many years" (src src:dw-gavrin-cleveland-2007-radiochemical-arxiv-nucl-ex-0703012). |
| collaborations/sage.json | notes/0 | Joint Institute for Nuclear Research (Russia) and Los Alamos National Laboratory (USA) named as participants on Wikipedia | Institute for Nuclear Research of the Russian Academy of Sciences, Los Alamos, NIST, University of Washington per the paper author list | rf09-sage-iii-arxiv | The participant is INR RAS (Moscow), not JINR as the Wikipedia article says; the technical summary already said INR. |
| sites/baksan-sage-underground-lab.json | coordinates | 43.2756 N, 42.6903 E (Wikipedia infobox 43°16'32"N 42°41'25"E), campus, precision 3000 m | 43.2756023 N, 42.6921682 E (OpenStreetMap node 4244310615, Main adit entrance), campus, approximate, precision 3500 m | geo-baksan-osm-main-adit | Surface point at the adit entrance; the laboratory is 3.5 km inside the mountain (CERN Courier, SAGE 1999 paper), hence precision 3500 m. Point moved about 146 m east. No published coordinate of the underground laboratory found. |
| sites/baksan-sage-underground-lab.json | summary/plain+technical | ~2100 m (6900 ft) underground | under about 2100 m of rock (4700 m.w.e.) |  | Rock thickness 2100 m is from the Baksan 2016 presentation already cited in depth; the "6900 ft" conversion and the word underground-depth wording came from Wikipedia and were dropped. |
| experiments/borexino.json | intervals/0 | construction 1990 - 2004 | construction 1991-08 - 2004 | rfua-borexino-about | The 1990 R&D start has no primary source; the official timeline dates the detailed proposal to August 1991 and structure completion to 2004. |
| experiments/borexino.json | intervals/1 | data taking 2007-05 - 2021-10 | 2007-05-16 - 2021-10-07 | rfua-borexino-about | Official timeline gives the first and last DAQ run days. |
| experiments/borexino.json | intervals/2 | shut down 2021-10 | shut down 2021-10-07 | rfua-borexino-about | Day precision from the official timeline. |
| collaborations/borexino.json | intervals/0 | collaboration active 1990 - 2021-10 | 1991-08 - 2021-10-07 | rfua-borexino-about | Old 1990 lower bound (detector R&D start) unsourced; replaced by the official detailed-proposal date, still marked uncertain. |
| collaborations/borexino.json | intervals/1 | completed (data taking) 2021-10 | 2021-10-07 | rfua-borexino-about | Day precision from the official timeline. |
| detectors/borexino.json | intervals/0 | data taking 2007-05 - 2021-10 | 2007-05-16 - 2021-10-07 | rfua-borexino-about | Official timeline gives first and last DAQ run days. |
| detectors/borexino.json | intervals/1 | shut down 2021-10 | 2021-10-07 | rfua-borexino-about | Day precision from the official timeline. |
| detectors/borexino.json | placements/0 | 2007-05 - 2021-10 | 2007-05-16 - 2021-10-07 | rfua-borexino-about | Operating period at Hall C, same dates as the data-taking interval. |
| experiments/kamland.json | intervals/0 | start 2002-01-17 | start 2002-01 | dw-kamland-motoki-online-monitoring-2004 | KamLAND-member sources give 22 Jan (Motoki) and 21 Jan (Hatakeyama) 2002, the 2026 collaboration paper says March 2002; no source gives 17 Jan, so month precision. |
| detectors/kamland.json | intervals/0 | start 2002-01-17 | start 2002-01 | dw-kamland-motoki-online-monitoring-2004 | KamLAND-member sources give 22 Jan (Motoki) and 21 Jan (Hatakeyama) 2002, the 2026 collaboration paper March 2002; no source gives 17 Jan. |
| detectors/kamland.json | placements/0 | start 2002-01-17 | start 2002-01 | dw-kamland-motoki-online-monitoring-2004 | Same start as the data-taking interval. |
| experiments/sno-plus.json | intervals/0 | water-fill commissioning 2017 - 2019 | 2017-05 - 2019-07 | dw-sno-plus-detector-jinst-2021 | SNO+ detector paper gives month precision (May 2017 - July 2019). |
| experiments/sno-plus.json | intervals/1 | liquid-scintillator phase start 2022 | start 2022-05 | dw-snolab-news-sno-plus-fill-2022 | SNOLAB news of 17 May 2022 announces the scintillator fill and PPO loading complete. |
| detectors/sno-plus.json | intervals/0 | water-fill commissioning 2017 - 2019 | 2017-05 - 2019-07 | dw-sno-plus-detector-jinst-2021 | SNO+ detector paper gives month precision. |
| detectors/sno-plus.json | intervals/1 | liquid-scintillator phase start 2022 | start 2022-05 | dw-snolab-news-sno-plus-fill-2022 | SNOLAB news of 17 May 2022 announces the scintillator fill and PPO loading complete. |
| facilities/lngs.json | intervals/0 | laboratory operating, start 1987 (research center fully operational) | start 1987 = end of excavation, uncertain; new construction row 1982-1987 | dw-lngs-pandola-underground-overview-2011 | No official page says the lab became operational in 1987; a lab staff paper says the excavation was completed in 1987 (and started in 1982, which the official Italian page confirms), so 1987 stays a lower bound. |
| accelerators/cebaf.json | intervals/0 (construction begins) | start 1987-02-13 | start 1987-02 | dw-jlab-fifteen-years-beam-on-target | JLab states only the month; the day-precision date was Wikipedia-only and is dropped. |
| accelerators/cebaf.json | intervals/3 (4 GeV design energy achieved) | start 1995 | start 1995-11 | dw-jlab-fifteen-years-beam-on-target | JLab gives the month; the Wikipedia-only value had year precision only. |
| accelerators/cebaf.json | intervals/4 (6 GeV enhanced design energy reached) | start 2000-08-06; "enhanced design energy" of 6 GeV | start 2000-08; 6.07 GeV delivered | dw-jlab-archives-page | JLab gives only the month and 6.07 GeV; the day and the "enhanced design energy" wording were Wikipedia-only. |
| accelerators/cebaf.json | intervals/4/specs/beam_energy | 6 GeV | 6.07 GeV | dw-jlab-archives-page | Value follows the energy JLab reports delivering. |
| facilities/jefferson-lab.json | intervals/0 (laboratory founded) | start 1984 (year only) | start 1984-08-03 | dw-jlab-40th-anniversary-open-house | JLab's own 40th-anniversary release gives the day; the Wikipedia-only value was the year. |
| accelerators/sns.json | intervals/1 (commissioning) end | end 2007-08 (first instruments, Wikipedia) | end 2008 (user experiments began) | dw-ornl-twenty-years-sns | ORNL (2026) dates the start of user experiments to 2008, not August 2007; the row end now follows ORNL and stays approximate. |
| accelerators/sns.json | intervals/2 (operational: first instruments commissioned) | start 2007-08 (first three instruments, Wikipedia) | start 2008 (user experiments began) | dw-ornl-twenty-years-sns | ORNL says user experiments began in 2008; the August 2007 date was Wikipedia-only and is not supported by ORNL or by the 2007 ORNL user-program calls consulted. |
| accelerators/sns.json | specs/beam_energy | ~1 GeV | 1.3 GeV (1.0 GeV originally) | currency2-sns-ppu-completion-linac2024 | ORNL's LINAC2024 paper gives both energies; the Wikipedia-only "about one GeV" is the pre-upgrade energy. |
| collaborations/ship.json | intervals/0 (collaboration start) | 2013-10 | 2015-04-08 (lower bound) | dw-ship-technical-proposal-2015-arxiv-1504-04956 | Start moved from the EoI month to the date of the first collaboration-issued document; still uncertain because it is only a lower bound. |
| sites/cascadia-basin-p-one.json | coordinates | 48.89889, -125.27444 (Barkley Sound, kind campus, 250 km) | 47.76667, -127.76667 (kind detector, approximate, 3 km) | dw-p-one-straw-pathfinder-arxiv-1810-13265 | The STRAW paper gives the real Cascadia Basin site position (about 220 km from the old coastal stand-in), so the point moves. |
| sites/grandproto300-dunhuang.json | coordinates | 40.14111, 94.66389 (Dunhuang city, kind campus, 50 km) | 40.99434, 93.94177 (XiaoDuShan site, kind detector, approximate, 5 km) | dw-grand-gp13-first-look-arxiv-2307-12769 | The GRAND collaboration publishes the array site coordinates; the city stand-in was about 113 km from it. Corroborated by arXiv:2507.06629 (40.99 N, 93.94 E). |
| sites/moores-bay-arianna.json | coordinates | -78.5167, 166.4167 (Minna Bluff, kind campus, 30 km) | -78.74205, 165.04023 (prototype station GPS position, kind campus, approximate, 2 km) | astro-neutrino-arianna-arxiv-prototype-2010 | The old point was Minna Bluff, about 40 km away; the same 78 44.523' S, 165 02.414' E is printed in arXiv:1410.7134; kept as campus kind because both papers are rank-10 arXiv records (A17). |
| sites/wipp-surface-campus.json | coordinates | 32.37167, -103.79361 | 32.375, -103.79278 (kind campus, approximate, 2 km) | 0vbb-verify-exo-200-detector-design-arxiv-1202-2192 | The EXO-200 detector paper gives 32°22′30″N 103°47′34″W for WIPP, 0.4 km from the old value; kept as a campus-grade point because the paper does not say surface or underground. |
| experiments/muon-g-2.json | intervals/2 (ring relocation, end 2014-07) | end 2014-07 (arrival date at MC-1, 2014-07-30) | end 2014 (year precision); quote now the CERN Courier sentence | dw-cerncourier-muon-g2-ring-2014 | The 2014-07-30 date appeared in no primary source; the CERN Courier article says re-assembly began in MC-1 in summer 2014. |
| detectors/muon-g-2.json | intervals/0 (ring relocation, end 2014-07) | end 2014-07 (arrival date at MC-1, 2014-07-30) | end 2014 (year precision); quote now the CERN Courier sentence | dw-cerncourier-muon-g2-ring-2014 | The 2014-07-30 date appeared in no primary source; the CERN Courier article says re-assembly began in MC-1 in summer 2014. |

## Every value, by group

### DESY, HERA, H1, ZEUS, ALPS II (`desy-hera`)

| Record | Field | Old source | Action | Old value | New value | New source | URL | Quote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| accelerators/hera.json | intervals/0 (operation 1992 - 2007-06-30) | hera-wikipedia | replaced | start 1992, end 2007-06-30 (uncertain) | start 1992, end 2007-06-30 (verified) | dw-desy-hera-pointing-the-way | https://pr.desy.de/sites/sites_desygroups/sites_extern/site_pr/content/e104098/e104111/HERA_Pointing_the_way_eng.pdf | The Hadron-Electron Ring Accelerator HERA went into operation at DESY in 1992. Research operation was concluded at the end of June 2007 and the accelerator was switched off. |
| accelerators/hera.json | intervals/1 (completed 2007-06-30) | hera-wikipedia | replaced | completed from 2007-06-30 (uncertain) | completed from 2007-06-30 (verified) | dw-hera-ew-bsm-zhang-arxiv-0812-4662 | https://arxiv.org/abs/0812.4662 | The electron-proton collider HERA ended its data taking on June 30, 2007. |
| detectors/alps-ii.json | placements/0 | h1-wikipedia | redundant | site:desy-hera-north-hall-h1 (verified) | site:desy-hera-north-hall-h1 (verified) | axions-alps-ii-desy-cryoplatform | https://alps.desy.de/our_activities/technology/desy_cryoplatform/ | in the HERA North Hall at DESY, which has recently been partially renovated to accommodate the ALPS II experiment in the HERA tunnel. |
| facilities/desy.json | intervals/0 (laboratory founded 1959-12-18) | desy-wikipedia | redundant | 1959-12-18 | 1959-12-18 | desy-about-page | https://www.desy.de/about_desy/index_eng.html | Established in Hamburg on 18 December 1959 |
| facilities/desy.json | summary.technical (Hamburg-Bahrenfeld, Zeuthen) | desy-wikipedia | replaced | Hamburg-Bahrenfeld, second site at Zeuthen | unchanged text, now backed by a note | dw-desy-petra4-location | https://petra4.desy.de/location/index_eng.html | The DESY research and technology centre, parts of the University of Hamburg and other top scientific institutes already ensure that the Bahrenfeld location has international appeal. |
| geometry/desy-campus-boundary.json | geometry (campus boundary polygon) | desy-wikipedia | redundant | OSM way 276641657 polygon | OSM way 276641657 polygon (unchanged) | geo-desy-osm-campus-boundary | https://www.openstreetmap.org/way/276641657 | name=Deutsches Elektronen-Synchrotron DESY; addr:street=Notkestraße; addr:housenumber=85; addr:postcode=22607; addr:city=Hamburg |
| geometry/hera-halle-nord.json | geometry (HERA Halle Nord footprint) / locator / method | hera-wikipedia | replaced | Wikipedia: 'H1 ... located in the HERA Hall North' | DESY brochure: 'H1 in the North Hall' | dw-desy-hera-pointing-the-way | https://pr.desy.de/sites/sites_desygroups/sites_extern/site_pr/content/e104098/e104111/HERA_Pointing_the_way_eng.pdf | In 1992, the first two HERA experiments went into operation: H1 in the North Hall and ZEUS in the South Hall. |
| maps/desy.json | levels/1/depth_m (HERA tunnel depth 10-25 m) | hera-wikipedia | replaced | 10-25 m (uncertain, Wikipedia only) | 10-25 m (verified) | dw-desy-hera-pointing-the-way | https://pr.desy.de/sites/sites_desygroups/sites_extern/site_pr/content/e104098/e104111/HERA_Pointing_the_way_eng.pdf | the tunnel boring machine HERAKLES wound its way through Hamburg’s sandy soil, 10 to 25 meters deep underground. |
| maps/desy.json | unlocated/0 sources (ZEUS South Hall) | zeus-wikipedia | replaced | ZEUS South Hall pairing | ZEUS South Hall pairing | dw-desy-hera-pointing-the-way | https://pr.desy.de/sites/sites_desygroups/sites_extern/site_pr/content/e104098/e104111/HERA_Pointing_the_way_eng.pdf | In 1992, the first two HERA experiments went into operation: H1 in the North Hall and ZEUS in the South Hall. |
| sites/desy-hamburg-campus.json | coordinates (campus centroid) | desy-wikipedia | redundant | 53.5770744, 9.8807554 (campus, 300 m, approximate) | unchanged | geo-desy-osm-campus-boundary | https://www.openstreetmap.org/way/276641657 | name=Deutsches Elektronen-Synchrotron DESY; addr:street=Notkestraße; addr:housenumber=85; addr:postcode=22607; addr:city=Hamburg |
| sites/desy-hamburg-campus.json | summary.plain (Bahrenfeld district) | desy-wikipedia | replaced | Bahrenfeld district of Hamburg | unchanged text, now backed by a note | dw-desy-petra4-location | https://petra4.desy.de/location/index_eng.html | The DESY research and technology centre, parts of the University of Hamburg and other top scientific institutes already ensure that the Bahrenfeld location has international appeal. |
| sites/desy-hera-north-hall-h1.json | notes/1 (H1 in North Hall, now ALPS) | h1-wikipedia | replaced | Wikipedia: 'The HERA North Hall, where the H1 detector was located, is now used for the new ALPS experiment' | DESY brochure (H1 in the North Hall) + DESY ALPS page (hall renovated for ALPS II) | dw-desy-hera-pointing-the-way | https://pr.desy.de/sites/sites_desygroups/sites_extern/site_pr/content/e104098/e104111/HERA_Pointing_the_way_eng.pdf | In 1992, the first two HERA experiments went into operation: H1 in the North Hall and ZEUS in the South Hall. |
| sites/desy-hera-south-hall-zeus.json | notes/1 (ZEUS in South Hall) | zeus-wikipedia | replaced | Wikipedia: 'The HERA South Hall where the ZEUS experiment was located.' | DESY brochure: 'ZEUS in the South Hall' | dw-desy-hera-pointing-the-way | https://pr.desy.de/sites/sites_desygroups/sites_extern/site_pr/content/e104098/e104111/HERA_Pointing_the_way_eng.pdf | In 1992, the first two HERA experiments went into operation: H1 in the North Hall and ZEUS in the South Hall. |

Prose reworded (credited or relied on Wikipedia):

| Record | Field | Old source | Note |
| --- | --- | --- | --- |
| accelerators/hera.json | notes/1 | hera-wikipedia | Note now credits the primary sources. |
| experiments/alps-ii.json | notes/1 | wikipedia (text mention) | Removed the sentence about an earlier Wikipedia-only placement. |
| geometry/desy-campus-boundary.json | method (text) | desy-wikipedia | Dropped the Wikipedia infobox cross-check. |
| sites/desy-hera-south-hall-zeus.json | coordinates.note (history of previous record) | desy-wikipedia | Wikipedia id removed from the record-history sentence; coordinate itself rests on the OSM campus polygon. |
| accelerators/hera.json | specs/beam_energy/note | wikipedia (text mention) | Note no longer names Wikipedia; the value already cites Klein & Yoshida. |

Only in the record-level `sources` list (nothing rested on it):

`sites/desy-hera-north-hall-h1.json` (desy-wikipedia, hera-wikipedia), `sites/desy-hera-south-hall-zeus.json` (desy-wikipedia, hera-wikipedia)

### SLAC, SLC, PEP-II, BaBar, SLD (`slac`)

| Record | Field | Old source | Action | Old value | New value | New source | URL | Quote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| accelerators/pep-ii.json | intervals/0 (operation 1999 - 2008) | slac-wikipedia | replaced | 1999 - 2008 (year precision, uncertain) | 1999 - 2008-04-07 (verified) | dw-pep-ii-last-year-epac2008-talk | https://accelconf.web.cern.ch/e08/talks/tuxg01_talk.pdf | 1999-2007: Y4S data for BaBar (433 fb-1) ... Turned off PEP-II April 7, 2008 |
| accelerators/pep-ii.json | intervals/1 (completed) | slac-wikipedia | replaced | 2008 (uncertain) | 2008-04-07 (verified) | dw-pep-ii-last-year-epac2008-talk | https://accelconf.web.cern.ch/e08/talks/tuxg01_talk.pdf | Turned off PEP-II April 7, 2008 |
| accelerators/pep-ii.json | specs/circumference | slac-wikipedia | replaced | 2.2 km (1.4 mi), uncertain | 2.2 km (2,200 m per ring), verified | geo-slac-pepii-cdr-osti | https://www.osti.gov/biblio/10112145 | each with a circumference of 2200 m |
| accelerators/slc.json | intervals/0 (operation 1989 - 1998) | slac-wikipedia,slc-wikipedia | replaced | 1989 - 1998 (year precision, uncertain) | 1989 - 1998-06 (approximate) | dw-slc-alr-sld-page | https://www-sldnt.slac.stanford.edu/alr/slc.htm | The experimental physics program using the SLC started with the MarkII detector in 1989 ... lack of federal funding for this program led to its termination in June of 1998 |
| accelerators/slc.json | intervals/1 (completed) | slac-wikipedia,slc-wikipedia | replaced | 1998 (uncertain) | 1998-06 (verified) | dw-slc-alr-sld-page | https://www-sldnt.slac.stanford.edu/alr/slc.htm | lack of federal funding for this program led to its termination in June of 1998 |
| accelerators/slc.json | specs/beam_energy | slc-wikipedia | replaced | up to 50 GeV (design/maximum per beam), uncertain | up to 50 GeV (maximum per beam), verified | slac-grad-handbook | https://www.slac.stanford.edu/gen/grad/GradHandbook/slac.html | Starting in 1983, extensive modifications and additions to the existing linac enabled it to simultaneously accelerate and collide 50 GeV electrons and positron bunches on a pulse-to-pulse basis. |
| facilities/slac.json | intervals/0 (laboratory founded 1962) | slac-wikipedia | replaced | 1962 (uncertain) | 1962 (verified) | geo-slac-at-a-glance | https://www6.slac.stanford.edu/about/lab-overview/at-a-glance | Founded in 1962 with 200 employees |
| maps/slac.json | unlocated/0 (SLC arcs and final focus) | slc-wikipedia | replaced | cited the encyclopedia article on the SLC | cites the SLAC handbook page on the SLC arcs | slac-grad-handbook | https://www.slac.stanford.edu/gen/grad/GradHandbook/slac.html | This new machine, the SLAC Linear Collider or SLC, separated the beams at the end of the accelerator, guiding them through two opposing magnetic arcs and focusing them on each other |
| sites/slac-menlo-park-campus.json | summary.technical (address 2575 Sand Hill Road) | slac-wikipedia | replaced | 2575 Sand Hill Road, Menlo Park | unchanged | facilities-verify-slac-official-home | https://www6.slac.stanford.edu | 2575 Sand Hill Road Menlo Park, CA 94025-7015 |
| sites/slac-slc-collider-hall-sld.json | summary.technical | slc-wikipedia | changed | housing the SLD (SLAC Large Detector) (1989-1998) | SLD replaced Mark II in 1991 and ran until the SLC ended in June 1998 | slac-grad-handbook | https://www.slac.stanford.edu/gen/grad/GradHandbook/slac.html | Physics at the SLC started in 1988 with the Mark II detector, replaced in 1991 by the SLD (SLAC Large Detector) |

Prose reworded (credited or relied on Wikipedia):

| Record | Field | Old source | Note |
| --- | --- | --- | --- |
| accelerators/slac-linac.json | summary.technical | slac-wikipedia | "Injector for the SLC" contradicted the record's own note; the SLC used the linac itself. |
| accelerators/slc.json | summary.technical | slc-wikipedia | Dropped "by design", which only the encyclopedia article supported. |
| facilities/slac.json | notes/0 | slac-wikipedia | Note no longer says the date rests on the encyclopedia. |
| facilities/slac.json | operator_text.note | slac-wikipedia | Dropped the reference to Wikipedia-sourced wording; the value already cites the official site. |
| facilities/slac.json | summary.plain | slac-wikipedia | "Longest in the world" is not stated by SLAC pages read; Nobel claim is backed by the SLAC milestones page. |
| facilities/slac.json | summary.technical | slac-wikipedia | Official wording. |
| sites/slac-menlo-park-campus.json | summary.plain | slac-wikipedia | Wording follows the SLAC handbook page. |
| sites/slac-menlo-park-campus.json | coordinates.note | slac-wikipedia | History note listed the encyclopedia article among the previous point's sources; coordinates themselves already cite OSM. |
| sites/slac-pep-ii-ir2-babar.json | notes/1 | slac-wikipedia,babar-wikipedia | The sentence only said what the encyclopedia articles do not state; replaced by the sources that do. |
| sites/slac-pep-ii-ir2-babar.json | coordinates.note | slac-wikipedia | History note only; coordinates already cite OSM and the SLAC area map. |
| sites/slac-slc-collider-hall-sld.json | coordinates.note | slac-wikipedia | History note only; coordinates already cite OSM and the SLAC area map. |

Only in the record-level `sources` list (nothing rested on it):

`accelerators/pep-ii.json` (babar-wikipedia), `accelerators/slac-linac.json` (slac-wikipedia), `facilities/slac.json` (slac-wikipedia), `sites/slac-pep-ii-ir2-babar.json` (slac-wikipedia), `sites/slac-pep-ii-ir2-babar.json` (babar-wikipedia), `sites/slac-slc-collider-hall-sld.json` (slac-wikipedia,slc-wikipedia)

### Chooz, Double Chooz, Daya Bay, RENO (`chooz-daya-reno`)

| Record | Field | Old source | Action | Old value | New value | New source | URL | Quote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| collaborations/double-chooz.json | intervals/0 | double-chooz-wikipedia | replaced | end 2017-12 (month from "late December 2017") | end 2017-12, approximate ("end of 2017") | rf04-double-chooz-detectors-2022 | https://arxiv.org/pdf/2201.13285 | its data taking started first, in April 2011 ... Both detectors ran in parallel for about three years, until the end of 2017, when neutrino data taking was stopped. |
| collaborations/double-chooz.json | intervals/1 | double-chooz-wikipedia | replaced | start 2017-12 (month from "late December 2017") | start 2017-12, approximate ("end of 2017") | rf04-double-chooz-detectors-2022 | https://arxiv.org/pdf/2201.13285 | Both detectors ran in parallel for about three years, until the end of 2017, when neutrino data taking was stopped. |
| detectors/double-chooz.json | technology | double-chooz-wikipedia | replaced | Calorimetric liquid-scintillator detector consisting of four concentric cylindrical vessels, with a gadolinium-loaded liquid-scintillator target | Liquid-scintillator detector whose main detector has four nested cylindrical volumes: a gadolinium-loaded scintillator target, a gadolinium-free scintillator gamma catcher, a buffer oil and an optically separated liquid-scintillator veto | rf04-double-chooz-detectors-2022 | https://arxiv.org/abs/2201.13285 | a main detector comprising four cylindrical volumes filled with organic liquids. From the inside towards the outside there were volumes containing gadolinium-loaded scintillator, gadolinium-free scintillator, a buffer oil and, optically separated, another liquid scintillator acting as veto system. |
| detectors/double-chooz.json | intervals/1 | double-chooz-wikipedia | replaced | end 2017-12 (month from "late December 2017") | end 2017-12, approximate ("end of 2017") | rf04-double-chooz-detectors-2022 | https://arxiv.org/pdf/2201.13285 | After construction of the new near laboratory and detector, data taking with the second detector started at the end of 2014. Both detectors ran in parallel for about three years, until the end of 2017, when neutrino data taking was stopped. |
| detectors/double-chooz.json | intervals/2 | double-chooz-wikipedia | replaced | start 2017-12 (month from "late December 2017") | start 2017-12, approximate ("end of 2017") | rf04-double-chooz-detectors-2022 | https://arxiv.org/pdf/2201.13285 | Both detectors ran in parallel for about three years, until the end of 2017, when neutrino data taking was stopped. |
| experiments/daya-bay.json | intervals/3 | daya-bay-wikipedia | redundant | start 2020-12-12 | start 2020-12-12 (unchanged) | reactor-solar-verify-daya-bay-final-prl-2023 | https://arxiv.org/html/2211.14988 | Seven-AD operation occurred from 26 January 2017 until 12 December 2020 (1417 days) |
| experiments/double-chooz.json | intervals/1 | double-chooz-wikipedia | replaced | end 2017-12 (month from "late December 2017") | end 2017-12, approximate ("end of 2017") | rf04-double-chooz-detectors-2022 | https://arxiv.org/pdf/2201.13285 | After construction of the new near laboratory and detector, data taking with the second detector started at the end of 2014. Both detectors ran in parallel for about three years, until the end of 2017, when neutrino data taking was stopped. |
| experiments/double-chooz.json | intervals/2 | double-chooz-wikipedia | replaced | start 2017-12 (month from "late December 2017") | start 2017-12, approximate ("end of 2017") | rf04-double-chooz-detectors-2022 | https://arxiv.org/pdf/2201.13285 | Both detectors ran in parallel for about three years, until the end of 2017, when neutrino data taking was stopped. |
| experiments/double-chooz.json | physics_goals/0 | double-chooz-wikipedia | replaced | Measure or set a limit on the θ₁₃ neutrino mixing angle via reactor antineutrino disappearance | Measure the neutrino mixing angle θ₁₃ via reactor antineutrino disappearance using near and far detectors | rf04-double-chooz-detectors-2022 | https://arxiv.org/pdf/2201.13285 | with the goal of measuring a fundamental parameter in the context of neutrino oscillation, the mixing angle θ13 ... the disappearance of the electron antineutrinos in the far detector is observed in order to extract θ13 |
| facilities/chooz.json | intervals/1 | double-chooz-wikipedia | replaced | start 2011 (quote: located at 1050 m from the reactor cores of the Chooz nuclear power plant in France) | start 2011-04 (approximate lower bound) | rf04-double-chooz-detectors-2022 | https://arxiv.org/pdf/2201.13285 | Since the far detector could be installed in the existing laboratory of the original CHOOZ experiment [9], its data taking started first, in April 2011. |
| facilities/chooz.json | operator | double-chooz-wikipedia | replaced | null (cited the encyclopedia) | null (unchanged) | rf04-double-chooz-detectors-2022 | https://arxiv.org/pdf/2201.13285 | two almost identical detectors located at the Chooz-B nuclear power plant operated by the EDF company |
| facilities/daya-bay-reactor-neutrino-lab.json | intervals/1 | daya-bay-wikipedia | redundant | start 2020-12-12 | start 2020-12-12 (unchanged) | reactor-solar-verify-daya-bay-final-prl-2023 | https://arxiv.org/html/2211.14988 | Seven-AD operation occurred from 26 January 2017 until 12 December 2020 (1417 days) |
| sites/double-chooz-far-detector.json | depth_mwe | double-chooz-wikipedia | replaced | 300 m.w.e. (approximate) | 300 m.w.e. (verified) | rf04-double-chooz-detectors-2022 | https://arxiv.org/pdf/2201.13285 | Both detectors were in underground laboratories with shielding against cosmic radiation of 120 m w.e. in the near and 300 m w.e. in the far detector. |
| sites/daya-bay-experimental-halls.json | coordinates | daya-bay-wikipedia | replaced | 22.5953, 114.5431 (3000 m precision) | 22.608322, 114.544676 (campus, approximate, 1000 m precision) | geo-reactors-daya-bay-nim-2016 | https://arxiv.org/abs/1508.03943 | Baselines from the antineutrino detector centers to the reactor core centers in the Daya Bay (D1, D2), Ling Ao (L1-2) and Ling Ao-II (L3-4) Nuclear Power Plants is given in meters. |
| sites/double-chooz-near-detector.json | coordinates | chooz-npp-wikipedia | replaced | 50.09, 4.78944 (2000 m precision; Chooz power-plant point) | 50.089661, 4.790167 (campus, approximate, 500 m precision) | rf04-double-chooz-detectors-2022 | https://arxiv.org/pdf/2201.13285 | The near detector was installed in a new underground laboratory at around 400 m from the nuclear cores. |
| sites/double-chooz-near-detector.json | sources/summary (400 m) | double-chooz-wikipedia | replaced | near detector ~400 m from the reactors (summary.technical) | unchanged | rf04-double-chooz-detectors-2022 | https://arxiv.org/pdf/2201.13285 | The near detector was installed in a new underground laboratory at around 400 m from the nuclear cores. |

Prose reworded (credited or relied on Wikipedia):

| Record | Field | Old source | Note |
| --- | --- | --- | --- |
| collaborations/double-chooz.json | notes/0 | double-chooz-wikipedia | Dropped the sentence that credited the encyclopedia. |
| detectors/double-chooz.json | placements/1 note; intervals/0 note | double-chooz-wikipedia | Removed encyclopedia mentions and the uncited remark about the 2019 paper. |
| detectors/double-chooz.json | summary.technical | double-chooz-wikipedia | Wording follows the primary source. |
| experiments/double-chooz.json | intervals/0 note | double-chooz-wikipedia | Removed encyclopedia mention. |
| facilities/chooz.json | notes/0 | double-chooz-wikipedia | Removed encyclopedia mention. |
| facilities/daya-bay-reactor-neutrino-lab.json | notes/0 | daya-bay-wikipedia | Removed encyclopedia mention. |
| sites/double-chooz-far-detector.json | notes/0 | double-chooz-wikipedia | "Inside a hill" dropped from the note; it is attributed to the TDR in the summary, not to the encyclopedia. |

Only in the record-level `sources` list (nothing rested on it):

`experiments/reno.json` (hanbit-npp-wikipedia), `sites/chooz-very-near-nucleus.json` (chooz-npp-wikipedia), `sites/reno-far-detector.json` (hanbit-npp-wikipedia), `sites/reno-near-detector.json` (hanbit-npp-wikipedia), `sites/double-chooz-far-detector.json` (chooz-npp-wikipedia)

### CONUS, Brokdorf, Leibstadt, ILL, KARMEN, LSND, JUNO (`cevns`)

| Record | Field | Old source | Action | Old value | New value | New source | URL | Quote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| facilities/brokdorf-nuclear-power-plant.json | intervals/0 (reactor operation 1986-10-14 .. 2021-12-31) | cevns-conus-brokdorf-wikipedia | replaced | start 1986-10-14, end 2021-12-31 (approximate) | start 1986-10-14 (first grid synchronisation), end 2021-12-31 (expiry of power-operation authorisation); now verified | dw-nuklearesicherheit-brokdorf | https://www.nuklearesicherheit.de/en/nuclear-facilities/nuclear-power-plants-in-germany/brokdorf-nuclear-power-plant/ | First grid synchronisation14 October 1986 ... Expiry of authorisation for power operation in accordance with the German Atomic Energy Act (AtG)31 December 2021 |
| facilities/brokdorf-nuclear-power-plant.json | intervals/1 (decommissioned from 2021-12-31) | cevns-conus-brokdorf-wikipedia | replaced | start 2021-12-31 (approximate) | start 2021-12-31 (verified) | dw-base-brokdorf-abschaltung | https://www.base.bund.de/de/nukleare-sicherheit/atomausstieg/abgeschaltete-akw/brokdorf/brokdorf.html | Am 31.12.2021 ging das Atomkraftwerk Brokdorf endgültig vom Netz. |
| facilities/brokdorf-nuclear-power-plant.json | summary.technical (1440 MWe) | cevns-conus-brokdorf-wikipedia | changed | 3.9 GWth / 1440 MWe pressurized water reactor | 3.9 GWth pressurised water reactor (1,480 MWe gross, 1,410 MWe net) | dw-nuklearesicherheit-brokdorf | https://www.nuklearesicherheit.de/en/nuclear-facilities/nuclear-power-plants-in-germany/brokdorf-nuclear-power-plant/ | Thermal reactor power3.900 MW ... Gross electric capacity1.480 MW |
| facilities/leibstadt-nuclear-power-plant.json | intervals/0 (reactor operation, start) | cevns-conus-leibstadt-wikipedia | changed | start 1984-05-24 (approximate) | start 1984-12-15 (start of continuous operation, verified) | dw-kkl-chronik | https://www.kkl.ch/unternehmen/ueber-uns/chronik | Am 15. Dezember 1984 nimmt das Kernkraftwerk Leibstadt mit Bewilligung der Bundesbehörden seinen Dauerbetrieb auf. |
| facilities/leibstadt-nuclear-power-plant.json | operator | cevns-conus-leibstadt-wikipedia | replaced | Kernkraftwerk Leibstadt AG (uncertain) | Kernkraftwerk Leibstadt AG (verified) | dw-ensi-kkl-psue-2022-stellungnahme | https://ensi.admin.ch/de/wp-content/uploads/sites/2/2025/12/Sicherheitstechnische_Stellungnahme_zur_periodischen_Sicherheitsueberpruefung_2022_des_Kernkraftwerks_Leibstadt.pdf | Die Bewilligungsinhaberin des Kernkraftwerks Leibstadt ist eine Aktiengesellschaft mit dem Namen Kernkraftwerk Leibstadt AG |
| facilities/leibstadt-nuclear-power-plant.json | summary.technical (1285 MWe nameplate) | cevns-conus-leibstadt-wikipedia | replaced | 3.6 GWth boiling water reactor (1285 MWe nameplate) | 3.6 GWth General Electric BWR-6 (1285 MWe gross, 1233 MWe net rated) | dw-kkl-unser-kraftwerk | https://www.kkl.ch/kernenergie/unser-kraftwerk | Nennleistung brutto: 1285 MW elektrisch |
| facilities/ill-grenoble.json | intervals/0 (operation, start 1967) | cevns-ill-wikipedia | replaced | start 1967 (approximate; "Founded in 1967") | start 1967-01-19 (verified; institute founded by intergovernmental agreement) | dw-ill-historical-overview | https://www.ill.eu/en/about-the-ill/history/historical-overview/ | The ILL was founded on 19 January 1967 with the signing of an agreement between the governments of the French Republic and the Federal Republic of Germany. |
| facilities/ill-grenoble.json | operator | cevns-ill-wikipedia | replaced | Institut Laue-Langevin (a tripartite French-German-British research organisation) (uncertain) | Institut Laue-Langevin (an international research centre funded and managed by France, Germany and the United Kingdom) (verified) | dw-ill-at-a-glance | https://www.ill.eu/about-the-ill | Funded and managed by France, Germany and the United Kingdom, and in scientific partnership with 10 other countries, ILL is located in a dynamic and scientifically rich city of Grenoble |
| facilities/ill-grenoble.json | summary.technical (58.3 MW) and notes[1] | cevns-ill-wikipedia | changed | 58.3 MW research reactor (Wikipedia) | 58 MW thermal power | dw-ill-reactor-overview | https://www.ill.eu/en/the-facility/the-ill-high-flux-reactor/reactor-overview/ | Its core consists of a single fuel element of enriched uranium (almost 10 kg) cooled by heavy water (thermal power 58 megawatts). |
| sites/ill-grenoble-reactor-hall.json | coordinates | cevns-ill-wikipedia | changed | 45.206239, 5.692774 (Wikipedia infobox, approximate) | 45.206099, 5.692848 (OSM reactor-hall centroid, approximate, 100 m) | geo-ill-osm-reactor-hall | https://www.openstreetmap.org/way/191447189 |  |
| sites/ill-grenoble-reactor-hall.json | summary.technical (58.3 MW) | cevns-ill-wikipedia | changed | ILL 58.3 MW research reactor | 58 MW thermal power | dw-ill-reactor-overview | https://www.ill.eu/en/the-facility/the-ill-high-flux-reactor/reactor-overview/ | Its core consists of a single fuel element of enriched uranium (almost 10 kg) cooled by heavy water (thermal power 58 megawatts). |
| sites/brokdorf-nuclear-power-plant-campus.json | coordinates | cevns-conus-brokdorf-wikipedia | changed | 53.85083, 9.34472 (Wikipedia infobox, approximate) | 53.850777, 9.345842 (OSM reactor-building centroid, approximate, 100 m) | geo-reactors-osm-brokdorf-leibstadt-reactors | https://www.openstreetmap.org/way/87723028 |  |

Prose reworded (credited or relied on Wikipedia):

| Record | Field | Old source | Note |
| --- | --- | --- | --- |
| facilities/brokdorf-nuclear-power-plant.json | notes[0] (2018-2023) | cevns-conus-brokdorf-wikipedia | Aligned to the CONUS 2026 paper, which dates the Brokdorf period 2018-2022. |
| sites/brokdorf-nuclear-power-plant-campus.json | summary.technical (reactor type) |  | Not a Wikipedia value: the site summary wrongly said boiling water; also 2018-2023 aligned to 2018-2022 data taking. |
| sites/leibstadt-nuclear-power-plant-campus.json | coordinates.note | cevns-conus-leibstadt-wikipedia | Note no longer credits Wikipedia. |
| experiments/conus.json | facility_roles[0].note and summary.technical (2018-2023) | cevns-conus-wikipedia | The 2018 start came from the article (April 2018); the CONUS 2026 paper dates Brokdorf data taking 2018-2022, the interval already used it. |
| collaborations/conus.json | formation.note | cevns-conus-wikipedia | Formation value stays null; the note no longer cites the encyclopaedia. |
| collaborations/conus.json | intervals/0.note | cevns-conus-wikipedia | Interval start stays 2023 (collaboration, not data taking). |
| collaborations/conus.json | notes[0] (2018-2023) | cevns-conus-wikipedia | Aligned to arXiv:2605.22815. |

Only in the record-level `sources` list (nothing rested on it):

`sites/leibstadt-nuclear-power-plant-campus.json` (cevns-conus-leibstadt-wikipedia), `sites/juno-jiangmen-underground-lab.json` (juno-wikipedia-coordinates), `experiments/karmen.json` (karmen-wikipedia), `experiments/lsnd.json` (lsnd-wikipedia), `experiments/conus.json` (cevns-conus-wikipedia)

### SAGE, GALLEX/GNO, Homestake (`gallium-chlorine`)

| Record | Field | Old source | Action | Old value | New value | New source | URL | Quote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| detectors/gallex-gno.json | specs/target_mass | gallex-wikipedia | replaced | 30.3 t gallium | 30.3 t gallium | rf05-gno-complete-results-arxiv | https://arxiv.org/abs/hep-ex/0504037 | in a 100-ton gallium chloride target (containing 30.3 tons of gallium) |
| detectors/gallex-gno.json | technology | gallex-wikipedia | replaced | Radiochemical gallium detector (quote about 101 t GaCl3-HCl solution) | unchanged text; confidence uncertain -> verified | dw-mpik-gallex-gno-history | https://www.mpi-hd.mpg.de/lin/research_history.en.html | Gallium as target allows neutrino interaction via νe + 71Ga → 71Ge + e–. ... Germanium is removed from the solution as volatile germanium chloride (GeCl4). ... Finally, it is placed together with Xenon into a miniaturized proportional counter. |
| experiments/gallex-gno.json | facility_roles/0 | gallex-wikipedia | replaced | host: facility:lngs (uncertain) | host: facility:lngs (verified) | rf05-gno-complete-results-arxiv | https://arxiv.org/abs/hep-ex/0504037 | The Gallium Neutrino Observatory (GNO) experiment at the Laboratori Nazionali del Gran Sasso (LNGS) has recorded solar neutrinos with energies above 233 keV |
| experiments/gallex-gno.json | key_specs/0/quantity | gallex-wikipedia | replaced | 30.3 t gallium (101 t GaCl3-HCl solution) | same value | dw-mpik-gallex-gno-history | https://www.mpi-hd.mpg.de/lin/research_history.en.html | As already mentioned the GALLEX target consists of 30.3 t gallium in the form of a concentrated GaCl3-HCl solution (total weight 101 t). |
| experiments/gallex-gno.json | physics_goals/0 | gallex-wikipedia | replaced | Detect low-energy (pp-chain) solar neutrinos via the radiochemical gallium-to-germanium reaction and measure the total solar neutrino capture rate | Detect low-energy solar neutrinos from the proton-proton fusion chain via the radiochemical gallium-to-germanium reaction and measure their flux | dw-mpik-gallex-gno-history | https://www.mpi-hd.mpg.de/lin/research_history.en.html | The threshold of this reaction is 233 keV, low enough to detect neutrinos from the initial proton fusion chain. ... GNO aimed to measure the flux of solar electron neutrinos from the proton-proton fusion during a full solar cycle. |
| experiments/gallex-gno.json | unique_capabilities/0 | gallex-wikipedia | changed | Radiochemical gallium target sensitive to the lowest-energy (pp) solar neutrinos, below the threshold of water-Cherenkov or chlorine-based detectors | Radiochemical gallium target with a 233 keV threshold, low enough to detect the lowest-energy (pp) solar neutrinos, below the roughly 0.8 MeV sensitivity of the chlorine experiment | dw-mpik-gallex-gno-history | https://www.mpi-hd.mpg.de/lin/research_history.en.html | The experiment of Davis had to face fundamental problems: It was only sensitive to neutrinos with a energy higher than ∼0.8 MeV ... The threshold of this reaction is 233 keV, low enough to detect neutrinos from the initial proton fusion chain. |
| experiments/gallex-gno.json | summary/technical | gallex-wikipedia | changed | ...GALLEX 1991-1997 (73.1 SNU capture rate) then GNO 1998-2003 (62.9 SNU), led by the MPIK Heidelberg... | GALLEX re-evaluated 73.1 SNU; GNO 62.9 SNU; GALLEX headed by MPIK Heidelberg, GNO by the INFN Milano group | dw-mpik-gallex-gno-history | https://www.mpi-hd.mpg.de/lin/research_history.en.html | performed by the international collaboration with scientists from France, Germany, Italy, Israel, Poland and the US, headed by MPIK Heidelberg ... After corrections the overall GALLEX result has slightly decreased down to (73.1 ± 7.2) SNU. ... GNO was the successor project of GALLEX, with scientists from Italy and Germany, now headed by the Milano group of the INFN. |
| detectors/homestake.json | specs/target_mass | homestake-wikipedia | changed | null (only the 380 m3 / 100,000 gallon volume known) | 615 t perchloroethylene (C2Cl4) | dw-nobel-2002-physics-advanced-information | https://www.nobelprize.org/uploads/2018/06/advanced-physicsprize2002-3.pdf | The tank contained 615 tonnes of C2Cl4, an agent normally used for dry cleaning. |
| detectors/homestake.json | technology | homestake-wikipedia | replaced | 'dry-cleaning fluid' gloss credited to Wikipedia | gloss kept, now sourced to the Nobel autobiography | vf-davis-nobel-biographical-2002 | https://www.nobelprize.org/prizes/physics/2002/davis/biographical/ | The detector itself consisted of a 100,000-gallon tank filled with perchloroethylene, a solvent most commonly used for dry cleaning of clothing. |
| experiments/homestake.json | unique_capabilities/0 | homestake-wikipedia | replaced | First experiment to directly detect solar neutrinos, and the first to reveal the 'solar neutrino problem' (a measured rate about one-third of the theoretical prediction) | First experiment to detect solar neutrinos, and the one that revealed the 'solar neutrino problem' (about one-third of the prediction) | dw-nobel-2002-physics-advanced-information | https://www.nobelprize.org/uploads/2018/06/advanced-physicsprize2002-3.pdf | Davis discovered solar neutrinos. Solar neutrino fluxes measured by him have always been below the calculated ones, this being known as the “solar neutrino problem”. |
| collaborations/homestake.json | leadership/0 | homestake-wikipedia | changed | Raymond Davis Jr. and John N. Bahcall named as having headed the experiment (role spokesperson) | Raymond Davis Jr. (role other: built and administered the experiment); Bahcall no longer listed as a leader | vf-davis-nobel-biographical-2002 | https://www.nobelprize.org/prizes/physics/2002/davis/biographical/ | I built a much larger experiment in the Homestake Gold Mine in Lead, South Dakota. ... I transferred administration of the Homestake experiment to the University of Pennsylvania |
| experiments/sage.json | facility_roles/0 | sage-wikipedia | replaced | host: facility:baksan-neutrino-observatory (uncertain) | host: facility:baksan-neutrino-observatory (verified) | glossary-cern-courier-baksan-2017 | https://cerncourier.com/a/baksan-scales-new-neutrino-heights/ | This idea was implemented in two experiments: GALLEX in the Gran Sasso National Laboratory and SAGE at Baksan. |
| experiments/sage.json | physics_goals/0 | sage-wikipedia | replaced | Measure the flux of low-energy (pp-chain) solar neutrinos via the radiochemical gallium-to-germanium reaction | Measure the solar neutrino capture rate with a gallium metal target, via the radiochemical gallium-to-germanium reaction that reaches the low-energy (pp-chain) neutrinos | rf09-sage-iii-arxiv | https://arxiv.org/abs/0901.2200 | The Russian-American experiment SAGE began to measure the solar neutrino capture rate with a target of gallium metal in December 1989. |
| collaborations/sage.json | leadership/0 | sage-wikipedia | changed | Vladimir Gavrin, Georgiy Zatsepin and Thomas J. Bowles named as leading physicists (role spokesperson) | Vladimir Gavrin (leads SAGE, as of 2017) and Thomas J. Bowles (led the American side), both role other | glossary-cern-courier-baksan-2017 | https://cerncourier.com/a/baksan-scales-new-neutrino-heights/ | SAGE, which has been in operation since 1986 and is led by Vladimir Gavrin, is located 3.5 km from the tunnel entrance |
| collaborations/sage.json | leadership/0 (Zatsepin) | sage-wikipedia | removed | Georgiy Zatsepin as a leading physicist |  |  |  |  |
| collaborations/sage.json | notes/0 | sage-wikipedia | changed | Joint Institute for Nuclear Research (Russia) and Los Alamos National Laboratory (USA) named as participants on Wikipedia | Institute for Nuclear Research of the Russian Academy of Sciences, Los Alamos, NIST, University of Washington per the paper author list | rf09-sage-iii-arxiv | https://arxiv.org/abs/0901.2200 | Institute for Nuclear Research, Russian Academy of Sciences, 117312 Moscow, Russia T. J. Bowles, S. R. Elliott, and W. A. Teasdale Los Alamos National Laboratory, Los Alamos, New Mexico 87545, USA |
| facilities/baksan-neutrino-observatory.json | intervals/1 | sage-wikipedia | replaced | 1989-12 (quote from Wikipedia: The experiment began measuring the solar neutrino capture rate with the gallium target in December 1989) | 1989-12 (same) | rf09-sage-iii-arxiv | https://arxiv.org/abs/0901.2200 | The Russian-American experiment SAGE began to measure the solar neutrino capture rate with a target of gallium metal in December 1989. |
| sites/baksan-sage-underground-lab.json | coordinates | sage-wikipedia | changed | 43.2756 N, 42.6903 E (Wikipedia infobox 43°16'32"N 42°41'25"E), campus, precision 3000 m | 43.2756023 N, 42.6921682 E (OpenStreetMap node 4244310615, Main adit entrance), campus, approximate, precision 3500 m | geo-baksan-osm-main-adit | https://www.openstreetmap.org/node/4244310615 | SAGE, which has been in operation since 1986 and is led by Vladimir Gavrin, is located 3.5 km from the tunnel entrance |
| sites/baksan-sage-underground-lab.json | summary/plain+technical | sage-wikipedia | changed | ~2100 m (6900 ft) underground | under about 2100 m of rock (4700 m.w.e.) |  |  |  |

Prose reworded (credited or relied on Wikipedia):

| Record | Field | Old source | Note |
| --- | --- | --- | --- |
| experiments/gallex-gno.json | notes/1 | gallex-wikipedia | Sentence crediting Wikipedia rewritten. |
| experiments/homestake.json | summary/plain | homestake-wikipedia | Davis lecture: the solar neutrino problem 'was born in 1967 and lived until the turn of the century'. |
| collaborations/homestake.json | formation/note | homestake-wikipedia | Value stays null; note no longer credits Wikipedia. |
| collaborations/homestake.json | summary/plain+technical | homestake-wikipedia | Autobiography: signal about one-third of the standard solar model flux calculated by John Bahcall. |
| experiments/sage.json | intervals/0 (note) | sage-wikipedia | Note no longer names Wikipedia; interval itself already rests on the SAGE papers. |
| experiments/sage.json | intervals/2 (note) | sage-wikipedia | Open end stays uncertain; the unconfirmed Wikipedia end/ongoing claims were dropped. |
| experiments/sage.json | key_specs/0/quantity (note) | sage-wikipedia | Value 50 t already rests on the SAGE 2009 paper. |
| detectors/sage.json | intervals/0 (note) | sage-wikipedia | Interval end stays open; note rewritten without Wikipedia. |
| detectors/sage.json | specs/target_mass (note) | sage-wikipedia | Value 50 t already rests on the SAGE 2009 paper. |
| collaborations/sage.json | summary/plain+technical | sage-wikipedia | Zatsepin dropped (no sourced role). |
| facilities/baksan-neutrino-observatory.json | notes/0 | sage-wikipedia | The start month now rests on the SAGE 2009 paper. |
| sites/baksan-sage-underground-lab.json | depth (note) | sage-wikipedia | Depth 2100 m already rests on the Baksan 2016 presentation. |
| facilities/baksan-neutrino-observatory.json | specs/depth (note) | sage-wikipedia | Depth value 4700 m.w.e. already rests on the INR RAS page and the SAGE 1999 paper; sentence no longer credits Wikipedia. |
| experiments/gallex-gno.json | summary/plain | gallex-wikipedia | The GALLEX target was a GaCl3-HCl solution, not liquid gallium metal; wording corrected to the MPIK description. |

Only in the record-level `sources` list (nothing rested on it):

`detectors/sage.json` (sage-wikipedia)

### KamLAND, Borexino, SNO+, SNOLAB, LNGS (`solar-ls`)

| Record | Field | Old source | Action | Old value | New value | New source | URL | Quote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| experiments/borexino.json | intervals/0 | borexino-wikipedia | changed | construction 1990 - 2004 | construction 1991-08 - 2004 | rfua-borexino-about | https://borex.lngs.infn.it/about-borexino/ | Official detailed proposal: August 1991 ... Detector structures construction completed in 2004 |
| experiments/borexino.json | intervals/1 | borexino-wikipedia | changed | data taking 2007-05 - 2021-10 | 2007-05-16 - 2021-10-07 | rfua-borexino-about | https://borex.lngs.infn.it/about-borexino/ | First DAQ run started on May 16, 2007 ... Last DAQ run (#36744) stopped on Oct 7, 2021 |
| experiments/borexino.json | intervals/2 | borexino-wikipedia | changed | shut down 2021-10 | shut down 2021-10-07 | rfua-borexino-about | https://borex.lngs.infn.it/about-borexino/ | Last DAQ run (#36744) stopped on Oct 7, 2021 |
| experiments/borexino.json | key_specs/0/quantity | borexino-wikipedia | redundant | 278 t | 278 t | borexino-pp-first-detection-2014 | https://doi.org/10.1038/nature13702 | The buffer and target scintillator masses are 889 and 278 t, respectively. |
| experiments/borexino.json | key_specs/1/quantity | borexino-wikipedia | replaced | 3800 m.w.e. | 3800 m.w.e. | ug-borexino-jcap-2012-muon-flux | https://arxiv.org/abs/1202.6403 | Cosmic-muon flux and annual modulation in Borexino at 3800 m water-equivalent depth |
| collaborations/borexino.json | intervals/0 | borexino-wikipedia | changed | collaboration active 1990 - 2021-10 | 1991-08 - 2021-10-07 | rfua-borexino-about | https://borex.lngs.infn.it/about-borexino/ | Official detailed proposal: August 1991 ... Last DAQ run (#36744) stopped on Oct 7, 2021 |
| collaborations/borexino.json | intervals/1 | borexino-wikipedia | changed | completed (data taking) 2021-10 | 2021-10-07 | rfua-borexino-about | https://borex.lngs.infn.it/about-borexino/ | Last DAQ run (#36744) stopped on Oct 7, 2021 |
| detectors/borexino.json | intervals/0 | borexino-wikipedia | changed | data taking 2007-05 - 2021-10 | 2007-05-16 - 2021-10-07 | rfua-borexino-about | https://borex.lngs.infn.it/about-borexino/ | First DAQ run started on May 16, 2007 ... Last DAQ run (#36744) stopped on Oct 7, 2021 |
| detectors/borexino.json | intervals/1 | borexino-wikipedia | changed | shut down 2021-10 | 2021-10-07 | rfua-borexino-about | https://borex.lngs.infn.it/about-borexino/ | Last DAQ run (#36744) stopped on Oct 7, 2021 |
| detectors/borexino.json | placements/0 | borexino-wikipedia | changed | 2007-05 - 2021-10 | 2007-05-16 - 2021-10-07 | rfua-borexino-about | https://borex.lngs.infn.it/about-borexino/ | First DAQ run started on May 16, 2007 ... Last DAQ run (#36744) stopped on Oct 7, 2021 |
| detectors/borexino.json | specs/target_mass | borexino-wikipedia | redundant | 278 t | 278 t | borexino-pp-first-detection-2014 | https://doi.org/10.1038/nature13702 | The buffer and target scintillator masses are 889 and 278 t, respectively. |
| detectors/borexino.json | technology | borexino-wikipedia | replaced | nylon sphere of PC+PPO scintillator with PMTs, buffer, water Cherenkov veto | same | dw-borexino-cno-2020-fulltext | https://arxiv.org/html/2006.15115 | The SSS contains the organic liquid and supports the photomultipliers (PMTs) ... is the active medium of a Cherenkov muon tagger. ... The inner nylon vessel (IV), concentric to the SSS, contains a solution of Pseudocumene (PC) as solvent and PPO (2,5-diphenyloxazole) as fluor |
| experiments/kamland.json | facility_roles/0 | kamland-wikipedia | replaced | host facility:kamioka-observatory (uncertain) | same, uncertain | dw-kamland-dsnb-2026-fulltext | https://arxiv.org/html/2606.29381 | The KamLAND detector was located 1000 m underground at Mt. Ikenoyama in Kamioka, Japan. |
| experiments/kamland.json | intervals/0 | kamland-wikipedia | changed | start 2002-01-17 | start 2002-01 | dw-kamland-motoki-online-monitoring-2004 | https://arxiv.org/abs/hep-ex/0405074 | In January 22, 2002, KamLAND started the data-taking. |
| experiments/kamland.json | key_specs/0/quantity | kamland-wikipedia | replaced | ~1000 t | ~1000 t | dw-kamland-dsnb-2026-fulltext | https://arxiv.org/html/2606.29381 | The ID contained 1 kton of LS enclosed in a 13-m-diameter nylon/EVOH (ethylene-vinyl alcohol copolymer) balloon, which was supported by non-scintillating buffer oil. |
| collaborations/kamland.json | intervals/0 | kamland-wikipedia | replaced | start 2002-01 | start 2002-01 | dw-kamland-motoki-online-monitoring-2004 | https://arxiv.org/abs/hep-ex/0405074 | In January 22, 2002, KamLAND started the data-taking. |
| detectors/kamland.json | intervals/0 | kamland-wikipedia | changed | start 2002-01-17 | start 2002-01 | dw-kamland-motoki-online-monitoring-2004 | https://arxiv.org/abs/hep-ex/0405074 | In January 22, 2002, KamLAND started the data-taking. |
| detectors/kamland.json | placements/0 | kamland-wikipedia | changed | start 2002-01-17 | start 2002-01 | dw-kamland-motoki-online-monitoring-2004 | https://arxiv.org/abs/hep-ex/0405074 | In January 22, 2002, KamLAND started the data-taking. |
| detectors/kamland.json | specs/pmt_count | kamland-wikipedia | replaced | 1879 | 1879 | dw-kamland-first-results-2002-fulltext | https://arxiv.org/html/hep-ex/0212021 | An array of 1,879 photomultiplier tubes (PMTs), mounted on the inner surface of the containment vessel, completes the inner detector (ID) system. |
| detectors/kamland.json | specs/target_mass | kamland-wikipedia | replaced | ~1000 t | ~1000 t | dw-kamland-dsnb-2026-fulltext | https://arxiv.org/html/2606.29381 | The ID contained 1 kton of LS enclosed in a 13-m-diameter nylon/EVOH (ethylene-vinyl alcohol copolymer) balloon, which was supported by non-scintillating buffer oil. |
| sites/kamioka-kamland.json | coordinates | kamland-wikipedia | replaced | 36.4225, 137.3153 (campus, approximate, 2000 m) | same point | dw-kamland-iwamoto-thesis-2003 | https://web.archive.org/web/20141006103219/http://kamland.lbl.gov/Dissertations/IwamotoToshiyuki-DoctorThesis.pdf | KamLAND coordinate is read out by the Japanese map with a scale of 1 to 25,000, and the result is following. East longitude is 137.3153, north latitude is 36.4225 |
| geometry/kamland-point.json | geometry | kamland-wikipedia | replaced | Point [137.3153, 36.4225] | same point | dw-kamland-iwamoto-thesis-2003 | https://web.archive.org/web/20141006103219/http://kamland.lbl.gov/Dissertations/IwamotoToshiyuki-DoctorThesis.pdf | KamLAND coordinate is read out by the Japanese map with a scale of 1 to 25,000, and the result is following. East longitude is 137.3153, north latitude is 36.4225 |
| experiments/sno-plus.json | intervals/0 | sno-plus-wikipedia | changed | water-fill commissioning 2017 - 2019 | 2017-05 - 2019-07 | dw-sno-plus-detector-jinst-2021 | https://arxiv.org/html/2104.11687 | The water phase was used to collect physics data by operating SNO+ as a water Cherenkov detector from May 2017 to July 2019 while filled with 905 tonnes of UPW. |
| experiments/sno-plus.json | intervals/1 | sno-plus-wikipedia | changed | liquid-scintillator phase start 2022 | start 2022-05 | dw-snolab-news-sno-plus-fill-2022 | https://www.snolab.ca/news/the-sno-experiment-completes-scintillator-fill-and-ppo-loading/ | The SNO+ experiment completes scintillator fill and PPO loading May 17, 2022 ... has completed the liquid scintillator detector fill and PPO loading marking a huge milestone for the experiment. |
| experiments/sno-plus.json | key_specs/0/quantity | sno-plus-wikipedia | replaced | 780 t | 780 t | dw-sno-plus-about-page | https://snoplus.phy.queensu.ca/about.html | The heart of the SNO+ detector is a 12m diameter acrylic sphere filled with 780 tonnes of liquid scintillator |
| collaborations/sno-plus.json | intervals/0 | sno-plus-wikipedia | replaced | collaboration start 2017 (lower bound) | start 2017 (lower bound) | dw-sno-plus-detector-jinst-2021 | https://arxiv.org/html/2104.11687 | In the first operating phase of the experiment, or “water phase”, the SNO+ detector was initially filled with light water (H2O) in May 2017. |
| detectors/sno-plus.json | intervals/0 | sno-plus-wikipedia | changed | water-fill commissioning 2017 - 2019 | 2017-05 - 2019-07 | dw-sno-plus-detector-jinst-2021 | https://arxiv.org/html/2104.11687 | The water phase was used to collect physics data by operating SNO+ as a water Cherenkov detector from May 2017 to July 2019 while filled with 905 tonnes of UPW. |
| detectors/sno-plus.json | intervals/1 | sno-plus-wikipedia | changed | liquid-scintillator phase start 2022 | start 2022-05 | dw-snolab-news-sno-plus-fill-2022 | https://www.snolab.ca/news/the-sno-experiment-completes-scintillator-fill-and-ppo-loading/ | The SNO+ experiment completes scintillator fill and PPO loading May 17, 2022 ... has completed the liquid scintillator detector fill and PPO loading marking a huge milestone for the experiment. |
| detectors/sno-plus.json | placements/0 | sno-plus-wikipedia | replaced | start 2017 | start 2017 | dw-sno-plus-detector-jinst-2021 | https://arxiv.org/html/2104.11687 | In the first operating phase of the experiment, or “water phase”, the SNO+ detector was initially filled with light water (H2O) in May 2017. |
| detectors/sno-plus.json | specs/target_mass | sno-plus-wikipedia | replaced | 780 t | 780 t | dw-sno-plus-about-page | https://snoplus.phy.queensu.ca/about.html | The heart of the SNO+ detector is a 12m diameter acrylic sphere filled with 780 tonnes of liquid scintillator |
| detectors/sno-plus.json | technology | sno-plus-wikipedia | replaced | SNO vessel and PMT structure, water then LS, eventually tellurium-loaded | SNO vessel, PMTs and support structure, water then LS (tellurium clause dropped here) | dw-sno-plus-about-page | https://snoplus.phy.queensu.ca/about.html | a 12m diameter acrylic sphere filled with 780 tonnes of liquid scintillator ... The acrylic sphere, PMTs and PMT support structure were from the original SNO Experiment. ... Previously, the detector was filled with ultrapure water and operated as a water Cherenkov detector. |
| facilities/lngs.json | intervals/0 | lngs-wikipedia-history | changed | laboratory operating, start 1987 (research center fully operational) | start 1987 = end of excavation, uncertain; new construction row 1982-1987 | dw-lngs-pandola-underground-overview-2011 | https://arxiv.org/pdf/1102.0208 | After the initial proposal by the INFN President A. Zichichi in 1979, the actual excavation started in 1982, in coincidence with the freeway 10-km tunnel, and was completed in 1987. |
| facilities/snolab.json | intervals/0 | snolab-wikipedia | replaced | start 2011-03 (uncertain) | start 2011-03 (approximate) | dw-snolab-updates-2011-04 | https://web.archive.org/web/20110715024429/http://www.snolab.ca/public/updates/index.html | The last area of the laboratory has now been given the “clean” designation and was opened for occupancy in March 2011. This means the entire lab is operating as a clean lab |

Prose reworded (credited or relied on Wikipedia):

| Record | Field | Old source | Note |
| --- | --- | --- | --- |
| experiments/borexino.json | summary.technical | borexino-wikipedia | Dates in the summary follow the changed intervals. |
| experiments/kamland.json | summary.technical | kamland-wikipedia | Follows the changed interval start. |
| detectors/kamland.json | notes/1 | kamland-wikipedia | Note no longer credits Wikipedia. |
| detectors/kamland.json | summary.technical | kamland-wikipedia | Follows the changed interval start. |
| sites/kamioka-kamland.json | notes/0 | kamland-wikipedia | The 105 m.w.e. figure is still not recorded; the sentence no longer attributes it to Wikipedia. |
| geometry/kamland-point.json | method | kamland-wikipedia | Text no longer credits Wikipedia. |
| geometry/kamland-point.json | summary.plain | kamland-wikipedia | Text no longer credits Wikipedia. |
| facilities/lngs.json | notes/2 | lngs-wikipedia-history | Text no longer credits Wikipedia. |
| facilities/snolab.json | notes/1 | snolab-wikipedia | Text no longer credits Wikipedia. |
| sites/snolab-underground-lab.json | notes/0 | snolab-wikipedia | Sentence no longer mentions Wikipedia. |

Only in the record-level `sources` list (nothing rested on it):

`experiments/borexino.json` (borexino-wikipedia), `detectors/borexino.json` (borexino-wikipedia), `experiments/kamland.json` (kamland-wikipedia), `detectors/kamland.json` (kamland-wikipedia), `sites/kamioka-kamland.json` (kamland-wikipedia), `geometry/kamland-point.json` (kamland-wikipedia), `experiments/sno-plus.json` (sno-plus-wikipedia), `detectors/sno-plus.json` (sno-plus-wikipedia), `facilities/lngs.json` (lngs-wikipedia-history), `facilities/snolab.json` (snolab-wikipedia), `sites/snolab-underground-lab.json` (snolab-wikipedia)

### JLab, PSI, LANSCE, SNS, ORNL, Argonne (`labs`)

| Record | Field | Old source | Action | Old value | New value | New source | URL | Quote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| accelerators/cebaf.json | intervals/0 (construction begins) | jlab-wikipedia | changed | start 1987-02-13 | start 1987-02 | dw-jlab-fifteen-years-beam-on-target | https://www.jlab.org/news/stories/fifteen-years-beam-target | Construction on what came to be called the Continuous Electron Beam Accelerator Facility began in February of 1987 |
| accelerators/cebaf.json | intervals/1 (12 GeV Upgrade dedication) | jlab-wikipedia | replaced | 2018-05-02 | 2018-05-02 | dw-jlab-archives-page | https://www.jlab.org/info_resources/archives | On Wednesday, May 2, 2018, the CEBAF 12 GeV Upgrade Dedication Ceremony took place |
| accelerators/cebaf.json | intervals/2 (first beam delivered to an experimental hall) | jlab-wikipedia | replaced | 1994-07-01 | 1994-07-01 | dw-jlab-fifteen-years-beam-on-target | https://www.jlab.org/news/stories/fifteen-years-beam-target | On July 1, 1994, Jefferson Lab's accelerator delivered an electron beam into one of its experimental halls for the first time. |
| accelerators/cebaf.json | intervals/3 (4 GeV design energy achieved) | jlab-wikipedia | changed | start 1995 | start 1995-11 | dw-jlab-fifteen-years-beam-on-target | https://www.jlab.org/news/stories/fifteen-years-beam-target | The machine reached full-design energy, 4 GeV, in November 1995. |
| accelerators/cebaf.json | intervals/3/specs/beam_energy | jlab-wikipedia | replaced | 4 GeV | 4 GeV | dw-jlab-fifteen-years-beam-on-target | https://www.jlab.org/news/stories/fifteen-years-beam-target | The machine reached full-design energy, 4 GeV, in November 1995. |
| accelerators/cebaf.json | intervals/4 (6 GeV enhanced design energy reached) | jlab-wikipedia | changed | start 2000-08-06; "enhanced design energy" of 6 GeV | start 2000-08; 6.07 GeV delivered | dw-jlab-archives-page | https://www.jlab.org/info_resources/archives | In August 2000, the accelerator delivered 6.07 GeV (billion electron volts), 150% of the original CEBAF energy. |
| accelerators/cebaf.json | intervals/4/specs/beam_energy | jlab-wikipedia | changed | 6 GeV | 6.07 GeV | dw-jlab-archives-page | https://www.jlab.org/info_resources/archives | In August 2000, the accelerator delivered 6.07 GeV (billion electron volts), 150% of the original CEBAF energy. |
| facilities/jefferson-lab.json | intervals/0 (laboratory founded) | jlab-wikipedia | changed | start 1984 (year only) | start 1984-08-03 | dw-jlab-40th-anniversary-open-house | https://www.jlab.org/news/releases/jefferson-lab-celebrate-virginia-science-loversr-june-8-open-house-event | Jefferson lab was founded August 3, 1984. |
| sites/jlab-newport-news.json | summary/technical ("214-acre") | jlab-wikipedia | removed | 214-acre campus |  |  |  |  |
| accelerators/lansce.json | intervals/0 (opened as LAMPF) | lansce-wikipedia | replaced | 1972-06 | 1972-06 | dw-lanl-nss-2022-accelerating-innovation | https://www.lanl.gov/media/publications/national-security-science/1122-accelerating-innovation | on June 9, 1972, the much-anticipated energy of 800 million electron volts was achieved, making LAMPF the most powerful linear accelerator in the world at that time. |
| accelerators/lansce.json | specs/beam_energy | lansce-wikipedia | replaced | 800 MeV | 800 MeV | geo-lanl-linac-page | https://www.lanl.gov/science-engineering/science-facilities/lansce/facilities/linac | The third and longest stage of the accelerator (800m) is the side-coupled-cavity linac, where particles are accelerated to their final energy of 800 MeV. |
| accelerators/psi-hipa.json | intervals/0 (Ring Cyclotron went into operation) | psi-wikipedia | replaced | 1974 | 1974 | psi-geo-ring-cyclotron-page | https://www.psi.ch/en/cas/ring | The Ring cyclotron is a separated sector cyclotron with a fixed beam energy of 590 MeV, built by PSI and commissioned in 1974. |
| facilities/psi.json | intervals/0 (institute created, EIR + SIN merger) | psi-wikipedia | redundant | 1988-01-01 | 1988-01-01 | facilities-verify-psi-history-page | https://www.psi.ch/en/about/history-of-psi | On 1 January 1988, the Swiss Federal Institute for Reactor Research (EIR) and the Swiss Institute for Nuclear Research (SIN) merged to form the Paul Scherrer Institute, PSI. |
| facilities/psi.json | operator_text | psi-wikipedia | replaced | Part of the ETH Domain of the Swiss Confederation (the Swiss Federal Institutes of Technology system) | Part of the ETH Domain, the group of Swiss federal research institutions that also includes ETH Zurich, EPFL, WSL, Empa and Eawag | dw-ethrat-overview-eth-domain | https://ethrat.ch/en/eth-domain/ | The ETH Domain comprises the two Federal Institutes of Technology ETH Zurich and EPFL, the four research institutes PSI, WSL, Empa and Eawag, as well as the ETH Board |
| sites/psi-villigen.json | summary/technical (Villigen and Wurenlingen, Aargau) | psi-wikipedia | replaced | municipalities of Villigen and Wurenlingen, Canton of Aargau | same wording | dw-ag-aargaumobil-psi-2019 | https://www.ag.ch/media/kanton-aargau/bvu/mobilitaet-und-verkehr/aargaumobil/191114-aargaumobil-psi-def-doc-x.pdf | Das PSI liegt etwa in der Mitte zwischen den Städten Zürich und Basel, in den Aargauer Gemeinden Villigen und Würenlingen direkt an der Aare. |
| accelerators/sns.json | intervals/1 (commissioning) end | sns-wikipedia | changed | end 2007-08 (first instruments, Wikipedia) | end 2008 (user experiments began) | dw-ornl-twenty-years-sns | https://www.ornl.gov/news/twenty-years-of-discovery-science-at-the-spallation-neutron-source/ | Since user experiments began in 2008, tens of thousands of researchers from all over the world have used the scientific instruments at the SNS First Target Station |
| accelerators/sns.json | intervals/2 (operational: first instruments commissioned) | sns-wikipedia | changed | start 2007-08 (first three instruments, Wikipedia) | start 2008 (user experiments began) | dw-ornl-twenty-years-sns | https://www.ornl.gov/news/twenty-years-of-discovery-science-at-the-spallation-neutron-source/ | Since user experiments began in 2008, tens of thousands of researchers from all over the world have used the scientific instruments at the SNS First Target Station |
| accelerators/sns.json | specs/beam_energy | sns-wikipedia | changed | ~1 GeV | 1.3 GeV (1.0 GeV originally) | currency2-sns-ppu-completion-linac2024 | https://www.osti.gov/servlets/purl/2448167 | Increasing the beam energy from 1.0 to 1.3 GeV |
| facilities/oak-ridge-national-laboratory.json | intervals/0 (laboratory founded) | ornl-wikipedia | redundant | 1943 | 1943 | rf13-ornl-overview | https://www.ornl.gov/overview-ornl/ | Since its founding in 1943 as part of the Manhattan Project, ORNL has been at the forefront of scientific discovery and innovation. |
| facilities/oak-ridge-national-laboratory.json | operator_text | ornl-wikipedia | redundant | UT-Battelle, LLC (a partnership of the University of Tennessee and Battelle Memorial Institute) for the U.S. Department of Energy | UT-Battelle, LLC for the U.S. Department of Energy | ornl-sns-page | https://neutrons.ornl.gov/sns | Oak Ridge National Laboratory is managed by UT-Battelle LLC for the US Department of Energy |
| facilities/oak-ridge-national-laboratory.json | summary/technical (~10,000 acres) | ornl-wikipedia | removed | ~10,000 acres |  |  |  |  |
| facilities/argonne-national-laboratory.json | intervals/0 (re-chartered as Argonne National Laboratory) | argonne-wikipedia | replaced | 1946-07-01 | 1946-07-01 | dw-uchicago-argonne-75-years | https://news.uchicago.edu/story/argonne-national-laboratory-celebrates-75-years-scientific-discovery | on July 1, 1946, the lab was formally chartered as Argonne National Laboratory |
| facilities/argonne-national-laboratory.json | links/website | argonne-wikipedia | replaced | https://www.anl.gov/ | https://www.anl.gov/ | dw-doe-national-laboratories-page | https://www.energy.gov/national-laboratories | Argonne National Laboratory (ANL) is a federally funded research and development center located in Lemont, Illinois, and is the largest national laboratory in the Midwestern United States. |
| facilities/argonne-national-laboratory.json | operator_text | argonne-wikipedia | replaced | The University of Chicago, through its subordinate UChicago Argonne LLC, for the U.S. Department of Energy | The University of Chicago, through its subordinate UChicago Argonne LLC, for the U.S. Department of Energy | dw-doe-national-laboratories-page | https://www.energy.gov/national-laboratories | It is sponsored by the U.S. Department of Energy and operated by the University of Chicago through UChicago Argonne LLC. |
| sites/argonne-campus.json | summary/technical (Downers Grove Township; 9700 S. Cass Avenue) | argonne-wikipedia | replaced | Downers Grove Township, DuPage County, Illinois (Lemont mailing address), 9700 S. Cass Avenue | Argonne National Laboratory campus, southwest DuPage County, Illinois (Lemont address), 9700 Cass Avenue. | dw-doe-history-argonne-national-laboratory | https://www.osti.gov/opennet/manhattan-project-history/Places/MetLab/argonne.html | Argonne moved to a new site located on 1,500 acres in southwest DuPage County, Illinois |

Prose reworded (credited or relied on Wikipedia):

| Record | Field | Old source | Note |
| --- | --- | --- | --- |
| accelerators/cebaf.json | specs/beam_energy note | jlab-wikipedia | Note cited the Wikipedia id for the 2018 dedication; it now points at the interval backed by the JLab archives page. |
| accelerators/cebaf.json | notes/1 | jlab-wikipedia | Note credited Wikipedia for the history; rewritten to name the JLab pages. |
| accelerators/cebaf.json | summary/technical | jlab-wikipedia | Dropped the Wikipedia-only "enhanced design energy" wording and aligned the dates with the JLab sources. |
| sites/jlab-newport-news.json | coordinates/note | jlab-wikipedia | Note listed the Wikipedia id among the previous point's sources; the coordinate itself already rests on the OSM polygon and JLab site plan. |
| accelerators/psi-hipa.json | notes/0 | psi-wikipedia | Dropped the comparison with the 1.3 MW figure and the 1974 corroboration that credited the Wikipedia article. |
| accelerators/psi-hipa.json | specs/beam_energy note | psi-wikipedia | Note said "upgraded from Wikipedia-only"; the value already cites PSI's HIPA page. |
| accelerators/psi-hipa.json | specs/beam_power note | psi-wikipedia | Dropped the sentence contrasting the value with a 1.3 MW figure from the Wikipedia article. |
| facilities/psi.json | notes/0 | psi-wikipedia | Note said operator_text remained Wikipedia-only; it is now sourced to PSI and the ETH Board. |
| sites/psi-villigen.json | coordinates/note | psi-wikipedia | Note listed the Wikipedia id among the previous point's sources; the coordinate itself rests on OSM polygons. |
| accelerators/sns.json | intervals/0 note (construction) | sns-wikipedia | Note contrasted the end date with a "completed in April 2006" claim from the Wikipedia article; the comparison is dropped, the sourced May 2006 end is unchanged. |
| accelerators/sns.json | summary/technical | sns-wikipedia | Replaced "~1 GeV" and "first instruments commissioned in August 2007" (Wikipedia-only) with the ORNL-sourced 1.0/1.3 GeV and 2008 user-experiment start. |
| facilities/argonne-national-laboratory.json | notes/0 | argonne-wikipedia | Note said every claim was sourced to Wikipedia only; rewritten to name the DOE, DOE History Program and UChicago sources. |
| facilities/argonne-national-laboratory.json | summary/technical (Downers Grove Township; Site A) | argonne-wikipedia | Dropped "Downers Grove Township" and "Site A of the Metallurgical Laboratory" (Wikipedia-only); kept Lemont and DuPage County (DOE pages) and the Metallurgical Laboratory lineage (DOE History Program). |

Only in the record-level `sources` list (nothing rested on it):

`accelerators/cebaf.json` (jlab-wikipedia), `facilities/jefferson-lab.json` (jlab-wikipedia), `sites/jlab-newport-news.json` (jlab-wikipedia), `accelerators/lansce.json` (lansce-wikipedia), `sites/lanl-lansce.json` (lansce-wikipedia), `accelerators/psi-hipa.json` (psi-wikipedia), `facilities/psi.json` (psi-wikipedia), `sites/psi-villigen.json` (psi-wikipedia), `accelerators/sns.json` (sns-wikipedia), `facilities/oak-ridge-national-laboratory.json` (ornl-wikipedia), `sites/ornl-sns-neutrino-alley.json` (ornl-wikipedia), `facilities/argonne-national-laboratory.json` (argonne-wikipedia), `sites/argonne-campus.json` (argonne-wikipedia)

### OPERA, DONUT, SHiP, SeaQuest, PHENIX/STAR, Belle II (`beams`)

| Record | Field | Old source | Action | Old value | New value | New source | URL | Quote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| experiments/donut.json | facility_roles/0 | donut-wikipedia | replaced | was an experiment at Fermilab dedicated to the search for tau neutrino interactions | The DONUT experiment (Fermilab E872) was designed to observe the charged current interactions | donut-plb-2001-observation | https://arxiv.org/pdf/hep-ex/0012035 | The DONUT experiment (Fermilab E872) was designed to observe the charged current interactions |
| collaborations/opera.json | intervals/0 (collaboration start 2003) | opera-wikipedia | replaced | OPERA, in Hall C of the Gran Sasso underground labs, was built in 2003–2008. | The construction of the detector started in 2003 and it was completed in Summer 2008. | dw-opera-jinst-2009-detector | https://doi.org/10.1088/1748-0221/4/04/P04018 | The construction of the detector started in 2003 and it was completed in Summer 2008. |
| detectors/opera.json | intervals/0 (operating 2008-2012-12-03) | opera-wikipedia | redundant | 2008 .. 2012-12-03 | 2008 .. 2012-12-03 | opera-prl-2015-discovery | https://arxiv.org/html/1507.01417 | The experiment took data from 2008 to 2012 in the CERN Neutrinos to Gran Sasso beam |
| detectors/opera.json | intervals/1 (end of data taking 2012-12-03) | opera-wikipedia | redundant | 2012-12-03 | 2012-12-03 | rf08-opera-news-wayback | https://web.archive.org/web/20210125003644/http://operaweb.lngs.infn.it/spip.php?rubrique14 | 3 December 2012 After 5 years of operation the CNGS beam was stopped. |
| experiments/opera.json | intervals/0 (construction 2003-2008) | opera-wikipedia | replaced | OPERA, in Hall C of the Gran Sasso underground labs, was built in 2003–2008. | The construction of the detector started in 2003 and it was completed in Summer 2008. | dw-opera-jinst-2009-detector | https://doi.org/10.1088/1748-0221/4/04/P04018 | The construction of the detector started in 2003 and it was completed in Summer 2008. |
| experiments/opera.json | intervals/1 (data taking 2008-2012-12-03) | opera-wikipedia | redundant | 2008 .. 2012-12-03 | 2008 .. 2012-12-03 | opera-prl-2015-discovery | https://arxiv.org/html/1507.01417 | The experiment took data from 2008 to 2012 in the CERN Neutrinos to Gran Sasso beam |
| experiments/opera.json | intervals/2 (completed 2012-12-03) | opera-wikipedia | redundant | 2012-12-03 | 2012-12-03 | rf08-opera-news-wayback | https://web.archive.org/web/20210125003644/http://operaweb.lngs.infn.it/spip.php?rubrique14 | 3 December 2012 After 5 years of operation the CNGS beam was stopped. |
| experiments/ship.json | intervals/0 (Expression of Interest, 2013-10) | ship-wikipedia-pointer | replaced | 2013-10 (Wikipedia pointer, uncertain) | 2013-10 | dw-ship-eoi-2013-arxiv-1310-1762 | https://arxiv.org/pdf/1310.1762 | CERN-SPSC-2013-024 / SPSC-EOI-010 October 8, 2013 Proposal to Search for Heavy Neutral Leptons at the SPS |
| experiments/ship.json | intervals/2 (approved for ECN3, 2024) | ship-wikipedia-pointer | redundant | 2024 | 2024 | fixed-target-verify-ship-bdf-ecn3-arxiv-2606-11039 | https://arxiv.org/abs/2606.11039 | approved in 2024 |
| experiments/ship.json | intervals/3 (planned experiment start 2033) | ship-wikipedia-pointer | replaced | 2033 (planned, uncertain) | 2033 (planned, approximate) | fixed-target-verify-ship-bdf-ecn3-arxiv-2606-11039 | https://arxiv.org/pdf/2606.11039 | Approved in 2024 and to be built within the coming years at the CERN SPS, it will begin data taking in 2033. |
| detectors/ship.json | intervals/0 (approved, not yet built, 2024) | ship-wikipedia-pointer | replaced | 2024 (Wikipedia pointer, uncertain) | 2024 | fixed-target-verify-ship-bdf-ecn3-arxiv-2606-11039 | https://arxiv.org/abs/2606.11039 | approved in 2024 |
| detectors/ship.json | intervals/1 (planned 2033) | ship-wikipedia-pointer | replaced | 2033 planned, label planned construction/operation | 2033 planned, label planned start of data taking | fixed-target-verify-ship-bdf-ecn3-arxiv-2606-11039 | https://arxiv.org/pdf/2606.11039 | Approved in 2024 and to be built within the coming years at the CERN SPS, it will begin data taking in 2033. |
| detectors/ship.json | placements/0 (start 2033 planned) | ship-wikipedia-pointer | replaced | 2033 planned (Wikipedia pointer) | 2033 planned | fixed-target-verify-ship-bdf-ecn3-arxiv-2606-11039 | https://arxiv.org/pdf/2606.11039 | Approved in 2024 and to be built within the coming years at the CERN SPS, it will begin data taking in 2033. |
| collaborations/ship.json | formation | ship-wikipedia-pointer | removed | 2013-10 | null | dw-ship-technical-proposal-2015-arxiv-1504-04956 | https://arxiv.org/pdf/1504.04956 |  |
| collaborations/ship.json | intervals/0 (collaboration start) | ship-wikipedia-pointer | changed | 2013-10 | 2015-04-08 (lower bound) | dw-ship-technical-proposal-2015-arxiv-1504-04956 | https://arxiv.org/pdf/1504.04956 | CERN-SPSC-2015-016 SPSC-P-350 8 April 2015 ... Technical Proposal A Facility to Search for Hidden Particles (SHiP) at the CERN SPS The SHiP Collaboration |
| detectors/seaquest.json | placements/0 (NM4 hall) | seaquest-wikipedia-pointer | replaced | NM4 hall placement (Wikipedia pointer, no quote) | NM4 hall placement | dw-doe-cx-002672-seaquest | https://www.energy.gov/node/339859 | Fermilab proposes to build and operate a spectrometer in the New Muon 4 (NM4) Hall and renovate the 120 giga-electron volt (GeV) beam line from enclosure B to NM4. |
| experiments/seaquest.json | facility_roles/1 (beam_source Main Injector) | seaquest-wikipedia-pointer | replaced | The spectrometer paper confirms the 120 GeV proton beam; the Fermilab Main Injector as the specific source machine is corroborated by src:seaquest-wikipedia-pointer (rank 12) rather than stated verbatim in the arXiv abstract text retrieved. | The spectrometer paper states that the 120 GeV proton beam comes from the Fermilab Main Injector. | seaquest-spectrometer-arxiv-2017 | https://arxiv.org/pdf/1706.09990 | The SeaQuest uses the 120 GeV proton beam ... from the Fermilab Main Injector. |
| experiments/seaquest.json | physics_goals/0 | seaquest-wikipedia-pointer | replaced | d-bar/u-bar asymmetry via Drell-Yan + nuclear modification | unchanged | seaquest-final-results-arxiv-2025 | https://arxiv.org/abs/2512.17564 | Final SeaQuest results on the flavor asymmetry of the proton light-quark sea with proton-induced Drell-Yan process |
| sites/fermilab-nm4-hall.json | notes/1 (building identity) and aliases | seaquest-wikipedia-pointer | replaced | The building identity ('NM4 Bldg.') rests on a Wikipedia pointer only; no other source consulted (checked 2026-09-17) names the building. | The hall name ('New Muon 4 (NM4) Hall') is taken from the U.S. DOE categorical-exclusion determination CX-002672 (19 May 2010) for the Drell-Yan SeaQuest project, which describes the E906/SeaQuest spectrometer as proposed for that hall. | dw-doe-cx-002672-seaquest | https://www.energy.gov/node/339859 | Fermilab proposes to build and operate a spectrometer in the New Muon 4 (NM4) Hall and renovate the 120 giga-electron volt (GeV) beam line from enclosure B to NM4. |

Prose reworded (credited or relied on Wikipedia):

| Record | Field | Old source | Note |
| --- | --- | --- | --- |
| collaborations/donut.json | formation | donut-wikipedia | Value was already null; it no longer cites Wikipedia and its note no longer implies a lower bound. |
| experiments/donut.json | key_specs/1/quantity/note | donut-wikipedia | The 2008 figure (9 events in 578) is now attributed to the collaboration paper arXiv:0711.0728, not to an encyclopaedia. |
| maps/fermilab.json | unlocated/5 (detector:donut) | donut-wikipedia | The sentence that said the placement cites only a Wikipedia pointer was stale (it cites the DONUT paper); re-pointed. |
| collaborations/opera.json | formation | opera-wikipedia | Value was already null; no longer cites Wikipedia. |
| experiments/ship.json | notes/1 and summary.technical | ship-wikipedia-pointer | Removed the 'rests only on a Wikipedia pointer' wording; summary no longer says 'per secondary reporting'. |
| detectors/ship.json | notes/0 | ship-wikipedia-pointer | Removed Wikipedia attribution. |
| experiments/seaquest.json | notes/0 | seaquest-wikipedia-pointer | NM4 hall name and Main Injector attribution now come from the DOE record and the spectrometer paper. |

Only in the record-level `sources` list (nothing rested on it):

`detectors/donut.json` (donut-wikipedia), `sites/bnl-rhic-ip6-star.json` (bnl-rhic-phenix-wikipedia), `sites/bnl-rhic-ip8-phenix-sphenix.json` (bnl-rhic-phenix-wikipedia), `sites/kek-tsukuba-belle-ii.json` (belle2-wikipedia-coordinates)

### ANITA, ARA, ARIANNA, ANTARES, GRAND, P-ONE, LEGEND, EXO-200 (`astro-misc`)

| Record | Field | Old source | Action | Old value | New value | New source | URL | Quote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| collaborations/legend.json | formation | legend-wikipedia-overview | replaced | null (note credited a Wikipedia summary) | null (unchanged) | dw-legend-arxiv-1709-01980 | https://arxiv.org/abs/1709.01980 | Building on this success, the LEGEND collaboration has been formed to pursue a tonne-scale 76 Ge experiment. |
| collaborations/legend.json | summary.plain / summary.technical (GERDA+MAJORANA combination) | legend-wikipedia-overview | redundant |  |  | legend-official-site | https://legend-exp.org/ | By combining the technological expertise and experience from the GERDA experiment and MAJORANA DEMONSTRATOR, LEGEND is expected to reach a design sensitivity two orders of magnitude greater than its predecessors. |
| sites/antares-toulon.json | coordinates | astro-neutrino-antares-wikipedia | redundant | 42.8, 6.17 | 42.8, 6.17 (unchanged) | rf13-antares-nim-2011 | https://arxiv.org/abs/1104.1607 | The ANTARES detector, located 40 km offshore from Toulon at 2475 ... 42◦ 48N, 6◦ 10E |
| sites/cascadia-basin-p-one.json | coordinates | astro-neutrino-p-one-wikipedia-barkley-sound | changed | 48.89889, -125.27444 (Barkley Sound, kind campus, 250 km) | 47.76667, -127.76667 (kind detector, approximate, 3 km) | dw-p-one-straw-pathfinder-arxiv-1810-13265 | https://arxiv.org/abs/1810.13265 | the ONC deep-sea infrastructure at Cascadia Basin dark site (47◦ 46’ N, 127◦ 46’ W), at a depth of ∼2600 m b.s.l. |
| sites/grandproto300-dunhuang.json | coordinates | astro-neutrino-grand-wikipedia-dunhuang | changed | 40.14111, 94.66389 (Dunhuang city, kind campus, 50 km) | 40.99434, 93.94177 (XiaoDuShan site, kind detector, approximate, 5 km) | dw-grand-gp13-first-look-arxiv-2307-12769 | https://arxiv.org/abs/2307.12769 | the selection of the XiaoDuShan site (E 93.94177◦ , N 40.99434◦ ), situated approximately 150 km north of Dunhuang city |
| sites/mcmurdo-ldb-launch-site.json | coordinates | astro-neutrino-anita-wikipedia-williams-field | replaced | -77.8675, 167.05667 (kind campus, 20 km) | -77.8675, 167.05667 (unchanged) | dw-osm-api-way-821080729 | https://api.openstreetmap.org/api/0.6/way/821080729.json | "gns:DMS_LAT":"77°52′03″S","gns:DMS_LONG":"167°03′24″E" |
| sites/moores-bay-arianna.json | coordinates | astro-neutrino-arianna-wikipedia-moore-bay | changed | -78.5167, 166.4167 (Minna Bluff, kind campus, 30 km) | -78.74205, 165.04023 (prototype station GPS position, kind campus, approximate, 2 km) | astro-neutrino-arianna-arxiv-prototype-2010 | https://arxiv.org/abs/1005.5193 | The prototype was deployed at GPS coordinates 780 44‟ 523” S, 1650 02‟ 414” East, about 110 kilometers south of McMurdo station). This is about 1 km from the original site coordinates. |
| sites/wipp-surface-campus.json | coordinates | exo-200-wipp-wikipedia | changed | 32.37167, -103.79361 | 32.375, -103.79278 (kind campus, approximate, 2 km) | 0vbb-verify-exo-200-detector-design-arxiv-1202-2192 | https://arxiv.org/abs/1202.2192 | EXO-200 is located at a depth of 1585 m water equivalent [21] in the Waste Isolation Pilot Plant (WIPP) near Carlsbad, New Mexico (32◦ 22’30”N 103◦ 47’34”W). |

Prose reworded (credited or relied on Wikipedia):

| Record | Field | Old source | Note |
| --- | --- | --- | --- |
| experiments/legend.json | notes[1] | legend-wikipedia-overview | Removed the Wikipedia credit; the null formation is explained on the collaboration record. |
| collaborations/km3net.json | notes[0] |  | Dropped the speculative Wikipedia/CORDIS attribution; no value rested on it. |
| experiments/anita.json | notes[4] | astro-neutrino-anita-wikipedia | Removed the Wikipedia pointer; the KICP corroboration sentence is kept. |
| experiments/ara.json | notes[1] | astro-neutrino-ara-wikipedia | Removed the pointer note; the overview paper already states the five stations and 2012-2018 deployment. |
| experiments/arianna.json | notes[3] | astro-neutrino-arianna-wikipedia | Removed the pointer note; the 7-station pilot array is sourced to arXiv:1909.00840. |
| experiments/exo-200.json | notes[0] | exo-200-wipp-wikipedia | Credit moved to the primary source. |
| sites/cascadia-basin-p-one.json | summary.technical | astro-neutrino-p-one-wikipedia-barkley-sound | Prose follows the new coordinate. |
| detectors/p-one.json | notes[0] and placements[0].note | astro-neutrino-p-one-wikipedia-barkley-sound | Prose and placement confidence follow the new site coordinate. |
| experiments/p-one.json | notes[0] | astro-neutrino-p-one-wikipedia-barkley-sound | Removed the Wikipedia mention and the stale Barkley Sound statement. |
| sites/grandproto300-dunhuang.json | summary.technical | astro-neutrino-grand-wikipedia-dunhuang | Prose follows the new coordinate. |
| detectors/grand.json | notes[0] and placements[0].note | astro-neutrino-grand-wikipedia-dunhuang | Prose and placement confidence follow the new site coordinate. |
| maps/mcmurdo-ldb.json | notes[1] | astro-neutrino-anita-wikipedia-williams-field | Credit moved to the OSM tags. |
| sites/moores-bay-arianna.json | summary.technical | astro-neutrino-arianna-wikipedia-moore-bay | Prose follows the new coordinate. |
| sites/wipp-surface-campus.json | notes[0] / coordinates.note / coordinates.locator | exo-200-wipp-wikipedia | Credit moved to the primary source. |
| maps/amundsen-scott-south-pole-station.json | notes[1], notes[4] |  | Dropped the Wikipedia attributions of the OSM node; no value rested on them. |

Only in the record-level `sources` list (nothing rested on it):

`experiments/legend.json` (legend-wikipedia-overview), `experiments/anita.json` (astro-neutrino-anita-wikipedia), `experiments/ara.json` (astro-neutrino-ara-wikipedia), `experiments/arianna.json` (astro-neutrino-arianna-wikipedia), `experiments/exo-200.json` (exo-200-wipp-wikipedia), `detectors/p-one.json` (astro-neutrino-p-one-wikipedia-barkley-sound), `detectors/grand.json` (astro-neutrino-grand-wikipedia-dunhuang), `sites/wipp-surface-campus.json` (exo-200-wipp-wikipedia)

### Integration pass: records outside the 107, stale prose, muon g-2, geometry notes, coverage registry (`final`)

| Record | Field | Old source | Action | Old value | New value | New source | URL | Quote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| experiments/muon-g-2.json | intervals/2 (ring relocation, end 2014-07) | wikipedia (named in note only) | changed | end 2014-07 (arrival date at MC-1, 2014-07-30) | end 2014 (year precision); quote now the CERN Courier sentence | dw-cerncourier-muon-g2-ring-2014 | https://cerncourier.com/a/muon-g-2-storage-ring-starts-a-new-life/ | Then, during summer this year, the next milestone was achieved as re-assembly of the storage ring began in the newly completed MC-1 building at Fermilab |
| detectors/muon-g-2.json | intervals/0 (ring relocation, end 2014-07) | wikipedia (named in note only) | changed | end 2014-07 (arrival date at MC-1, 2014-07-30) | end 2014 (year precision); quote now the CERN Courier sentence | dw-cerncourier-muon-g2-ring-2014 | https://cerncourier.com/a/muon-g-2-storage-ring-starts-a-new-life/ | Then, during summer this year, the next milestone was achieved as re-assembly of the storage ring began in the newly completed MC-1 building at Fermilab |
| geometry/slac-linac-klystron-gallery.json | method | (text; Wikipedia article named) | replaced | (per Wikipedia's Linear particle accelerator article, the gallery stretches above the path of the accelerator tunnel) | SLAC public-tours page statement | dw-slac-public-tours-klystron-gallery | https://www6.slac.stanford.edu/virtual-tour/klystron-gallery | SLAC is home to the historic 2-mile-long klystron gallery above the world’s longest linear particle accelerator. |

Prose reworded (credited or relied on Wikipedia):

| Record | Field | Old source | Note |
| --- | --- | --- | --- |
| geometry/baksan-bno-building.json | geometry/note | (text) | The comparison was with the old Wikipedia-derived site point, which has been replaced. |
| geometry/hera-tunnel-ring.json | method | (text) | Dropped the encyclopedia as a corroborating source. |
| geometry/icecube-array-footprint.json | method | (text) | The comparison point is the OpenStreetMap IceCube point; the encyclopedia attribution is dropped. |
| geometry/icecube-deepcore-strings-79-86.json | method | (text) | The comparison point is the OpenStreetMap IceCube point; the encyclopedia attribution is dropped. |
| geometry/icecube-strings-1-78.json | method | (text) | The comparison point is the OpenStreetMap IceCube point; the encyclopedia attribution is dropped. |
| geometry/icetop-tanks-stations-01-27.json | method | (text) | The comparison point is the OpenStreetMap IceCube point; the encyclopedia attribution is dropped. |
| geometry/icetop-tanks-stations-28-54.json | method | (text) | The comparison point is the OpenStreetMap IceCube point; the encyclopedia attribution is dropped. |
| geometry/icetop-tanks-stations-55-81.json | method | (text) | The comparison point is the OpenStreetMap IceCube point; the encyclopedia attribution is dropped. |
| geometry/kit-katrin-experiment-outline.json | method | (text) | Corroboration-only comparison with an encyclopedia coordinate removed. |
| geometry/bnl-rhic-ring.json | method | (text) | Dropped an OSM cross-reference tag from the description. |
| geometry/bnl-ags-ring.json | method | (text) | Dropped an OSM cross-reference tag name from the description. |
| geometry/psi-sinq-building.json | method | (text) | Dropped an OSM cross-reference tag from the description. |
| sources/geo-baksan-osm-bno-building.json | excerpt | (text) | The comparison was with the old Wikipedia-derived site point (src:sage-wikipedia), which is being deleted. |
| detectors/daya-bay-antineutrino-detectors.json | intervals/1/note | (text) | Dropped the encyclopedia attribution of the earlier, superseded text. |
| detectors/picolon.json | placements/0/note | (text) | The KamLAND point no longer derives from the encyclopedia. |
| facilities/yonggwang-hanbit-reactor-site.json | notes/0 | (text) | The RENO hall points are multilaterated from OSM footprints and design-report baselines, not taken from an encyclopedia page. |
| experiments/admx.json | notes/0 | (text) | Rejected-candidate note: the attribution is dropped, the exclusion stays. |
| facilities/university-of-washington-cenpa.json | notes/1 | (text) | Rejected-candidate note: the attribution is dropped, the exclusion stays. |
| sites/cern-point-1-atlas.json | coordinates/note | (text) | Dropped an encyclopedia infobox from the list of places checked. |
| experiments/grand.json | notes/0 | (text) | Stale after the coordinate moved from the Dunhuang city stand-in to the published XiaoDuShan position. |
| coverage/accelerator-neutrino-historical.json | 0/missing_fields/2 | (text) | Coverage-registry text; the claim it described no longer holds after the de-Wikipedia pass. |
| coverage/accelerator-neutrino-historical.json | 0/notes | (text) | Coverage-registry text; the claim it described no longer holds after the de-Wikipedia pass. |
| coverage/accelerator-neutrino-historical.json | 3/missing_fields/0 | (text) | Coverage-registry text; the claim it described no longer holds after the de-Wikipedia pass. |
| coverage/accelerator-neutrino-historical.json | 3/missing_fields/3 | (text) | Coverage-registry text; the claim it described no longer holds after the de-Wikipedia pass. |
| coverage/astro-neutrino.json | 6/missing_fields/4 | (text) | Coverage-registry text; the claim it described no longer holds after the de-Wikipedia pass. |
| coverage/axions.json | 2/notes | (text) | Coverage-registry text; the claim it described no longer holds after the de-Wikipedia pass. |
| coverage/cevns.json | 1/missing_fields/4 | (text) | Coverage-registry text; the claim it described no longer holds after the de-Wikipedia pass. |
| coverage/cevns.json | 1/notes | (text) | Coverage-registry text; the claim it described no longer holds after the de-Wikipedia pass. |
| coverage/cevns.json | 3/notes | (text) | Coverage-registry text; the claim it described no longer holds after the de-Wikipedia pass. |
| coverage/dark-matter-2.json | 18/missing_fields/1 | (text) | Coverage-registry text; the claim it described no longer holds after the de-Wikipedia pass. |
| coverage/fixed-target.json | 6/notes | (text) | Coverage-registry text; the claim it described no longer holds after the de-Wikipedia pass. |
| coverage/reactor-solar-neutrino.json | 0/missing_fields/2 | (text) | Coverage-registry text; the claim it described no longer holds after the de-Wikipedia pass. |
| coverage/reactor-solar-neutrino.json | 0/notes | (text) | Coverage-registry text; the claim it described no longer holds after the de-Wikipedia pass. |
| coverage/reactor-solar-neutrino.json | 1/missing_fields/0 | (text) | Coverage-registry text; the claim it described no longer holds after the de-Wikipedia pass. |
| coverage/reactor-solar-neutrino.json | 2/missing_fields/0 | (text) | Coverage-registry text; the claim it described no longer holds after the de-Wikipedia pass. |
| coverage/reactor-solar-neutrino.json | 3/missing_fields/0 | (text) | Coverage-registry text; the claim it described no longer holds after the de-Wikipedia pass. |
| coverage/reactor-solar-neutrino.json | 3/missing_fields/1 | (text) | Coverage-registry text; the claim it described no longer holds after the de-Wikipedia pass. |
| coverage/reactor-solar-neutrino.json | 4/missing_fields/0 | (text) | Coverage-registry text; the claim it described no longer holds after the de-Wikipedia pass. |
| coverage/reactor-solar-neutrino.json | 6/missing_fields/2 | (text) | Coverage-registry text; the claim it described no longer holds after the de-Wikipedia pass. |
| coverage/reactor-solar-neutrino.json | 7/missing_fields/3 | (text) | Coverage-registry text; the claim it described no longer holds after the de-Wikipedia pass. |
| coverage/reactor-solar-neutrino.json | 8/missing_fields/0 | (text) | Coverage-registry text; the claim it described no longer holds after the de-Wikipedia pass. |
| coverage/reactor-solar-neutrino.json | 8/missing_fields/3 | (text) | Coverage-registry text; the claim it described no longer holds after the de-Wikipedia pass. |

## Notes for the integrator

**Quotes not read at the stated URL.** `src:dw-opera-jinst-2009-detector` is the JINST 4 P04018 DOI; iopscience is bot-blocked, so the abstract sentence ("The construction of the detector started in 2003 and it was completed in Summer 2008.") was verified on the OSTI/ETDEWEB copy of the same abstract (https://www.osti.gov/etdeweb/biblio/21262775). It supports the OPERA experiment and collaboration construction rows. The Moore Bay coordinate quote keeps the PDF text layer of arXiv:1005.5193 exactly as extracted ("780 44‟ 523” S, 1650 02‟ 414” East", which is 78 deg 44.523 min S, 165 deg 02.414 min E); the record note says so, and arXiv:1410.7134 prints the same position cleanly. No quote is WebFetch-only.

**Source records of lower certainty.** `dw-uchicago-argonne-75-years` is the University of Chicago news office, not Argonne (anl.gov is behind a bot challenge); `dw-doe-national-laboratories-page` backs Argonne `links.website` and `operator_text` (the link target itself is not in the quoted text); `dw-doe-history-argonne-national-laboratory` carries DuPage County and Metallurgical Laboratory lineage statements; `dw-nuklearesicherheit-brokdorf` is a federal portal data sheet typed `institution_page` (rank 8); `dw-lngs-pandola-underground-overview-2011` is a review by an LNGS staff scientist, not a lab page; `dw-kamland-iwamoto-thesis-2003` and `dw-snolab-updates-2011-04` point at Internet Archive snapshots because the original pages are unreachable; `dw-osm-api-way-821080729` is the OpenStreetMap API form of the Williams Field way already cited by `src:geo-mcmurdo-osm-williams-field-aerodrome`, kept separate only so the `gns:DMS_*` tags can be machine-checked.

**Coordinates that moved.** P-ONE Cascadia Basin by about 220 km (now the position the STRAW paper gives for the cabled site), GRANDProto300 by about 113 km (the XiaoDuShan position the GRAND Collaboration publishes), Moore Bay by about 40 km (prototype-station GPS), and by less than a kilometre: WIPP (0.4 km), Daya Bay halls (0.4 km), Brokdorf (74 m), ILL (17 m), the SAGE point (146 m, now the OpenStreetMap main adit entrance, precision 3500 m), the Double Chooz near-hall proxy. The validator is clean, but the integrator should look at the globe and the local maps for these sites when rebuilding. The new warning `sites-too-close` (SAGE hall 0 m from the BUST hall) comes from both using the adit-entrance anchor.

**Defects noticed in values this stream did not touch (not Wikipedia-derived).** `experiments/reno.json` `key_specs/2` quote ("2.8 GW_th") does not match the arXiv abstract text verbatim; the JUNO site `muon_flux` quote is not found on its arXiv abstract page, and the JUNO site `notes` cite an unchecked "secondary IHEP-related search summary"; `experiments/donut.json` `summary.plain` ("completing the direct detection of every particle the Standard Model predicts") overclaims; the BaBar record cites a symmetrymagazine.org article that returns HTTP 403 to curl; `src:borexino-inspire-experiment-record` is an inspirehep.net record (cited before this stream). Several older quotes of the gallium/chlorine records fail a mechanical check only because two-column arXiv PDFs interleave under pdftotext, INR pages decode as cp1251, or the IOP 1998 Homestake paper is bot-blocked.

**What still says "wikipedia" in `data/atlas/`.** Three OpenStreetMap source excerpts (`geo-kek-osm-kekb-ring`, `geo-bnl-osm-rhic-ring`, `geo-bnl-osm-ags-ring`) list the OSM objects' own `wikipedia=` tag verbatim, and a number of OSM excerpts list `wikidata=` tags. They are tag data of the OSM object, not citations, and were left unchanged. No source record has a wikipedia.org URL, `source_type: "wikipedia"` stays in the schema (rank table) and in `static/atlas/js/provenance.js`.

**Other repository changes.** `hepgraph/atlas/validate.py`: rule `source-wikipedia` (error) in `check_sources`, matching wikipedia.org in `url` or `archive_url` (any language edition, mobile host, or an archive wrapper such as web.archive.org/web/.../https://en.wikipedia.org/...). `tests/test_atlas_validate.py`: two one-line cases in `MUTATION_CASES`. `tests/test_atlas_tours.py`: the weak-source test used a Wikipedia source from the data; it now uses a rank-12 `secondary` source. `static/atlas/about.html`: the source-ranking list no longer says Wikipedia may be used as a pointer. `docs/HEP_ATLAS_VALIDATION.md` section 3 names the rule. The Section 8 counts of that document (for example Sources 1606) were already stale and should be regenerated with `scripts/atlas_validation_counts.py`.

## Wikipedia source records deleted

| Id | URL |
| --- | --- |
| argonne-wikipedia | https://en.wikipedia.org/wiki/Argonne_National_Laboratory |
| astro-neutrino-anita-wikipedia | https://en.wikipedia.org/wiki/Antarctic_Impulsive_Transient_Antenna |
| astro-neutrino-anita-wikipedia-williams-field | https://en.wikipedia.org/wiki/Williams_Field |
| astro-neutrino-antares-wikipedia | https://en.wikipedia.org/wiki/ANTARES_(telescope) |
| astro-neutrino-ara-wikipedia | https://en.wikipedia.org/wiki/Askaryan_Radio_Array |
| astro-neutrino-arianna-wikipedia | https://en.wikipedia.org/wiki/ARIANNA_Experiment |
| astro-neutrino-arianna-wikipedia-moore-bay | https://en.wikipedia.org/wiki/Moore_Bay |
| astro-neutrino-grand-wikipedia-dunhuang | https://en.wikipedia.org/wiki/Dunhuang |
| astro-neutrino-p-one-wikipedia-barkley-sound | https://en.wikipedia.org/wiki/Barkley_Sound |
| babar-wikipedia | https://en.wikipedia.org/wiki/BaBar_experiment |
| belle2-wikipedia-coordinates | https://en.wikipedia.org/wiki/Belle_II_experiment |
| bnl-rhic-phenix-wikipedia | https://en.wikipedia.org/wiki/PHENIX_detector |
| borexino-wikipedia | https://en.wikipedia.org/wiki/Borexino |
| cevns-conus-brokdorf-wikipedia | https://en.wikipedia.org/wiki/Brokdorf_Nuclear_Power_Plant |
| cevns-conus-leibstadt-wikipedia | https://en.wikipedia.org/wiki/Leibstadt_Nuclear_Power_Plant |
| cevns-conus-wikipedia | https://en.wikipedia.org/wiki/CONUS_experiment |
| cevns-ill-wikipedia | https://en.wikipedia.org/wiki/Institut_Laue%E2%80%93Langevin |
| chooz-npp-wikipedia | https://en.wikipedia.org/wiki/Chooz_Nuclear_Power_Plant |
| daya-bay-wikipedia | https://en.wikipedia.org/wiki/Daya_Bay_Reactor_Neutrino_Experiment |
| desy-wikipedia | https://en.wikipedia.org/wiki/DESY |
| donut-wikipedia | https://en.wikipedia.org/wiki/DONUT |
| double-chooz-wikipedia | https://en.wikipedia.org/wiki/Double_Chooz |
| exo-200-wipp-wikipedia | https://en.wikipedia.org/wiki/Waste_Isolation_Pilot_Plant |
| gallex-wikipedia | https://en.wikipedia.org/wiki/GALLEX |
| h1-wikipedia | https://en.wikipedia.org/wiki/H1_(particle_detector) |
| hanbit-npp-wikipedia | https://en.wikipedia.org/wiki/Hanbit_Nuclear_Power_Plant |
| hera-wikipedia | https://en.wikipedia.org/wiki/HERA_(particle_accelerator) |
| homestake-wikipedia | https://en.wikipedia.org/wiki/Homestake_experiment |
| jlab-wikipedia | https://en.wikipedia.org/wiki/Thomas_Jefferson_National_Accelerator_Facility |
| juno-wikipedia-coordinates | https://en.wikipedia.org/wiki/Jiangmen_Underground_Neutrino_Observatory |
| kamland-wikipedia | https://en.wikipedia.org/wiki/KamLAND |
| karmen-wikipedia | https://en.wikipedia.org/wiki/KARMEN |
| lansce-wikipedia | https://en.wikipedia.org/wiki/Los_Alamos_Neutron_Science_Center |
| legend-wikipedia-overview | https://en.wikipedia.org/wiki/Large_Enriched_Germanium_Experiment_for_Neutrinoless_BB_Decay |
| lngs-wikipedia-history | https://en.wikipedia.org/wiki/Laboratori_Nazionali_del_Gran_Sasso |
| lsnd-wikipedia | https://en.wikipedia.org/wiki/LSND |
| opera-wikipedia | https://en.wikipedia.org/wiki/OPERA_experiment |
| ornl-wikipedia | https://en.wikipedia.org/wiki/Oak_Ridge_National_Laboratory |
| psi-wikipedia | https://en.wikipedia.org/wiki/Paul_Scherrer_Institute |
| sage-wikipedia | https://en.wikipedia.org/wiki/Soviet%E2%80%93American_Gallium_Experiment |
| seaquest-wikipedia-pointer | https://en.wikipedia.org/wiki/SeaQuest_experiment |
| ship-wikipedia-pointer | https://en.wikipedia.org/wiki/Search_for_Hidden_Particles |
| slac-wikipedia | https://en.wikipedia.org/wiki/SLAC_National_Accelerator_Laboratory |
| slc-wikipedia | https://en.wikipedia.org/wiki/Stanford_Linear_Collider |
| sno-plus-wikipedia | https://en.wikipedia.org/wiki/SNO%2B |
| snolab-wikipedia | https://en.wikipedia.org/wiki/SNOLAB |
| sns-wikipedia | https://en.wikipedia.org/wiki/Spallation_Neutron_Source |
| zeus-wikipedia | https://en.wikipedia.org/wiki/ZEUS_(particle_detector) |

