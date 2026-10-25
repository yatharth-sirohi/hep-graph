# Release currency, second pass (2026-10-25)

Branch `atlas-release-currency2`. Build date for rule A10 is 2026-10-25. Every date and status below was read in this session from the cited page or PDF (curl + `pdftotext`, WebFetch, or the Browser pane for HTML pages); verbatim quotes were copied from the extracted text. INSPIRE was not used. New source records: `data/atlas/sources/currency2-*.json`. Method and the first pass: `docs/atlas-worklog/RELEASE_CURRENCY.md`.

Access note: several Fermilab hosts (indico.fnal.gov, nova-docdb, lss.fnal.gov, ftbf/mu2e/sbn sites, fnal.gov operations pages) refuse non-browser clients with HTTP 403; no attempt was made to get around that. Pages that load for a plain client (news.fnal.gov, pac.fnal.gov) were used.

Validator after each step: `python -m hepgraph.atlas.validate` reports 0 errors.

## 1. Fermilab restart (Main Injector / NuMI / NOvA)

Result: not confirmed. The newest source is the Fermilab PAC report of the 1-4 September 2026 meeting (posted October 2026, https://pac.fnal.gov/wp-content/uploads/2026/10/Final_Public_PAC_Report_Sept2026.pdf). It still states the restart as a plan: "Beam has already been established in Linac and Booster (Aug 26), MI will start up on September 21, stable beam is planned for October 1". It also reports progress (6 of 8 transformers operational, up from 3 at the April meeting; "A minimum of 2 Kautz transformers are needed to operate MI at full energy"; a new spare transformer "will be delivered in December") and that "The plan is for 12 weeks of operation in FY27, with a stretch goal of 20 weeks of operation, with a focus on the NuMI beam." No source dated after 21 September 2026 was reachable: the Fermilab newsroom (checked through 22 October 2026, including its RSS feed) has no item about a Main Injector or NuMI restart, and the sites that would carry beam status refused access. So the accelerator, the beamline and NOvA stay `shutdown` with the planned restart left in place; only notes and the planned-run schedule were updated.

Conflict recorded, not resolved: Fermilab's own 7 July 2026 feature (https://news.fnal.gov/2026/07/fermilab-marks-70-years-of-neutrino-science-and-leads-next-generation-experiment/) says "NOvA, another crucial neutrino experiment hosted by Fermilab, is the only currently operating long-baseline neutrino experiment in the United States ... NOvA is taking data and measuring neutrino oscillations over a 500-mile distance." The PAC reports of April and September 2026 are specific that the Main Injector has not delivered NuMI beam since July 2024, and the feature does not say which data NOvA takes, so `shutdown` (no NuMI beam data-taking) was kept; the detectors are not recorded as powered down. If the integrator prefers `active` for the experiment, the beam-off row would have to become a `phase` annotation (the validator would then warn A12, active with no active listed beamline).

Other NuMI-fed entities checked by grep: `minerva`, `minos`, `minos-plus` are `completed` (unchanged); `icarus` is `active` on the Booster Neutrino Beam (the FY26 BNB run ended 12 June 2026, "72.9%" uptime) and was left unchanged; `fermilab-booster` and `fermilab-linac` kept running ("Beam has already been established in Linac and Booster (Aug 26)"); `fermilab-recycler` keeps its NuMI-stacking role label (no new evidence).

New fact worth a follow-up, not applied (no entity in the Atlas for the experiments): April 2026 PAC: "FNAL has decided not to run SY120 before the long 2028-29 shutdown for budget reasons" (SY120 feeds the Fermilab Test Beam Facility and SpinQuest).

## 2. SNO+ (acrylic vessel repair and restart)

Result: the repair is confirmed by two dated sources, the restart is only a plan, and the tellurium placeholder was wrong by a year. SNO+ (experiment and detector) moves from `active` to `shutdown` with a planned autumn 2026 restart.

- LIP Advisory Committee 2026 (27-28 April 2026), J. Maneira, slide 5 "SNO+ TIMELINE AND PLANS" (https://indico.lip.pt/event/2184/contributions/7460/attachments/5713/9308/Advisory2026_NeutrinoPhysics.pdf): "Acrylic Vessel Repairs leak in AV, height identified, lowering water now to repair, autumn restart". The slide's timeline figure (rendered and read, not text) shows the scintillator-phase bar ending before the 2026 tick, "Repairs" over 2026-2027 and the green "Fill 0.5% Te" bar starting at 2028 (then "0.5% data", "Fill 1.5% Te", "1.5% data"). Text: "Submitted proposal for 1.5% loading".
- SNOLAB Report, slides dated 2026/05/26 (https://cinp.ca/sites/default/files/2026-06/SNOLAB_2026CAP.pdf), slides 16-17 "SNO+ Cavity Access for Repairs": "No damage to the neck. AV was not stuck", "Anchor point good. No degradation of structure", "Installing lights"; the cavity photograph shows the PMT array with the water level lowered.
- Not found: any source after 26 May 2026 on whether the autumn restart happened (the SNO+ site snoplus.phy.queensu.ca does not answer from here; snolab.ca has no news index; the newest SNO+ arXiv paper, 2604.05746 of 7 April 2026, is a reactor-neutrino analysis using data "between May 2022 and July 2025"). The shutdown stays until a source reports the restart.
- Judgement: "autumn restart" is ambiguous (scintillator data-taking vs water fill); it cannot be the tellurium fill, which the same slide puts in 2028. The shutdown's end is therefore recorded as a planned, approximate date (autumn 2026: date 2026-10, earliest 2026-09, latest 2026-11).

## 3. CTAO LST sub-array

Result: confirmed; recorded as a milestone annotation, not a status change. https://www.ctao.org/news/the-large-sized-telescope-sub-array-is-inaugurated-on-ctao-north/ (La Palma, 15 October 2026): "celebrated the inauguration of the Large-Sized Telescope (LST) sub-array at the CTAO-North site"; "With the three new LSTs (LST-2, LST-3, and LST-4) joining the existing LST-1, the four telescopes will become a true array"; "Over the coming years, the LSTs will undergo commissioning and integration into CTAO operations." The record structure does not support per-telescope intervals (one aggregate `detector:ctao` for both sites; the LSTs exist only as map geometry), the article gives no commissioning dates for LST-2 to LST-4 and says commissioning is still ahead, and the rest of CTAO is unbuilt, so a `phase` row (status construction, 2026-10-15) was added to `experiment:ctao` and `detector:ctao` and the observatory status stays `construction`.


## 4. Audit leads from the first pass

### 4.1 SNS proton power upgrade

Result: confirmed and dated. ORNL, 18 May 2026 (https://www.ornl.gov/news/sns-upgrade-accelerates-neutron-research-boosts-data-quality): "The completed proton power upgrade ensures SNS will remain the world's most powerful proton accelerator" and the linac "is well along the path to 2.8 megawatts". So the project is complete, but the delivered power is still being ramped. The dates come from the LINAC2024 paper by the project team (https://www.osti.gov/servlets/purl/2448167): "The long installation outage began in August 2023 and concluded in April 2024"; "Beam commissioning commenced June 7th"; "Neutron production for the user program resumed July 11th as planned at 1.3 GeV and 1.7 MW". The Atlas had an undated, open-ended `upgrade` row (start and end null, so it covered nothing) and an open-ended operating row from 2007-08 that ignored the 2023-24 outage. Fixed to: active 2007-08 to 2023-08, upgrade 2023-08 to 2024-07-11, active from 2024-07-11. Status stays `active`. Not changed: `specs.beam_energy` ("~1 GeV", Wikipedia) now reads 1.3 GeV in the project paper; left for a spec pass.

### 4.2 HAYSTAC

Result: Phase II data-taking is over and the Phase III upgrade was under way in March 2026; status `active` -> `upgrade` (experiment and detector). The collaboration's own paper, arXiv:2510.15848v3 (revised 21 January 2026), dates the data-taking: "phase I (January 2016–July 2017)", phase II(a) September 2019-April 2020, II(b) July 2021-November 2021, "phase II(c) and II(d) (September 2022–August 2024)", II(e) July 2022. APS Global Physics Summit abstract (19 March 2026, https://meetings-archive.aps.org/smt/2026/apr-v89/1/): "In preparation for Phase III, HAYSTAC is currently upgrading to a multi-rod cavity that can perform high-frequency searches with a high FOM ... summarize the Phase III testing and commissioning at Yale"; a second abstract (same session) says the new high-resolution channel "will be commissioned for HAYSTAC Phase III". The Atlas had the run "Phase II" starting 2024 (a publication date) and an open-ended operating row from 2018. Not found: any source after March 2026 on the start of Phase III data-taking (a search result pointed to a November 2026 talk listing at indico.global/event/16402 that could not be opened, so it was not used). The upgrade stays open.

### 4.3 Project 8

Result: Phase II is over and the collaboration is working on Phase III apparatus, so the experiment is no longer `active`; recorded as `upgrade` (judgement, see below). The collaboration site (https://www.project8.org/about/, news items on the home page to 12 May 2026): "Currently, Project 8 has finished a demonstration of this technique." and "Currently, efforts are focused on Phase III. We are developing demonstrators of various technologies and working on our detector simulations and event analysis." arXiv:2503.08807 (11 March 2025): "Phase II of Project 8 ... was a crucial demonstration of CRES’s potential". APS DNP, 19 October 2025: "Project 8 is now entering Phase III". Phenomenology 2026 (May 2026): "the upcoming phase of Project 8 will demonstrate the first realization of cavity-based CRES using Cavity CRES Apparatus (CCA)"; the cubic-metre apparatus "is being designed". The Atlas had Phase II `active` from 2025-03 (the publication month of the apparatus paper) with no end and Phase III as an undated `proposed` row that covered nothing. Phase II's start and end are only bounded (first tritium result on arXiv 9 December 2022; past tense in March 2025), not dated. Judgement: the Atlas has no "R&D hiatus" status; `upgrade` (existing experiment between data-taking phases, next apparatus in development) was preferred over `proposed` (implies unbuilt) and `construction` (the sources describe R&D and design). Change it if the integrator prefers another word.

### 4.4 nEXO

Result: pause confirmed by SNOLAB's own report; status stays `proposed`. SNOLAB Report (slides dated 26 May 2026, https://cinp.ca/sites/default/files/2026-06/SNOLAB_2026CAP.pdf), slide 26 "SNOLAB Cryopit Timeline", first entry "Dec 2024": "US led nEXO project was paused." (read from the rendered slide). No source says cancelled; nexo.llnl.gov (undated) still says "The nEXO experiment is under development"; SNOLAB's 31 July 2026 talk lists "nEXO 2.0" only as an illustrative future-project idea ("does not indicate SNOLAB approval or space allocation"). A `phase` annotation (status `proposed`, from 2024-12) was added to the experiment and detector; the pause's own announcement was not found.

### 4.5 SENSEI (SNOLAB runs)

Result: the SNOLAB runs were missing and are now recorded as intervals; status stays `active`. arXiv:2312.13342 (SENSEI at SNOLAB, 20 December 2023): "The SENSEI apparatus at SNOLAB was installed in 2021"; first science data "taken from September 9, 2022 to April 10, 2023"; "The SNOLAB setup has been upgraded with additional detectors for another science run" (not dated). The Fermilab MINOS-cavern operation is still described as current in arXiv:2610.22418 (15 October 2026). Not done (follow-up for the integrator): a SNOLAB placement for `detector:sensei` and an `unlocated`/drawn entry on the SNOLAB map were not added, because the Atlas rules put maps/ out of scope for this stream and an undrawn placement raises an A25 warning; the first pass had left the placement out for lack of an explicit SNOLAB source, which now exists.

### 4.6 P-ONE first line and the STRAW pathfinder

Result: nothing of P-ONE has been in the water since July 2023, and the first full-scale line (P-ONE-1) is built and tested but not reported deployed. The experiment and its detector move from `commissioning`/`active` to `construction`. Sources (official P-ONE news): the STRAW moorings "were disconnected and recovered during last month’s summer 2023 #ONCAbyss expedition" (ONC item of 24 August 2023); P-ONE-1 "was fully assembled and integrated" on 28 April 2026 ("nearly three years of coordinated international development and engineering efforts"); it "successfully completed its final pre-deployment shallow-water test" on 23 June 2026; "the collaboration aims to deploy P-ONE-1 ... by the end of August 2026"; Demonstrator final assembly at TRIUMF "between 2027 and 2028". The news page has nothing newer than 23 June 2026 and no other report of a deployment was found, so the deployment is recorded as a planned phase (August 2026) and the experiment as `construction`; if the line is in fact deployed the state would be `commissioning`. The first-pass rows had treated STRAW as operating with no end, which is why the experiment read `commissioning`.

### 4.7 RNO-G station count and drilling

Result: eight stations confirmed (35 planned); the 2023 pause ended by 2025; status stays `construction`. Summit Station project page for the 2026 season (https://geo-summit.org/summit-station/research-projects/collaborative-research-wou-mma-robust-searches-ultrahigh-energy-neutrinos-rno-g): "the eight existing RNO-G stations (Sites 11, 12, 13, 14, 21, 22, 23, and 24)"; "boreholes drilled in 2025 (Sites 15, 25, 34, and 35) and 2026 (Site 45)"; "Between July and August, the science team will bring five new RNO-G stations online". ARENA 2026 abstracts (June 2026): "RNO-G currently consists of eight autonomous stations"; "As of March 2026, eight of these stations have already been commissioned". Not found: any report of the outcome of the June-August 2026 season, so the five new stations are a planned row, not counted. The "deployment paused" row now ends in 2025 (approximate upper bound).

### 4.8 ARA

Result: no status change. The planned upgrade partly happened: arXiv:2509.18368 (22 September 2025): "In 2024, two of the five ARA stations received DAQ upgrades", with "2024-2025 season upgrades" and RFSoC DAQ "foreseen in the coming years". ARENA 2026 abstracts call ARA "five independent stations which have been taking data for over a decade"; arXiv:2603.00341 (27 February 2026) reports "nearly 30 station-years of livetime accumulated". None says which stations are live in 2026 or what the 2025-26 and 2026-27 seasons did, so the 'reduced-scale operation' row (2 of 5 live in the 2024 paper) was kept and its note updated.

## Change log (every edit, for re-opening)

- **accelerator:fermilab-main-injector** — intervals["no Main Injector beam (transformer failures)"].note/sources; intervals["NuMI run..."].label/note/quote/sources
  - old: planned run labelled "NuMI run, 20 weeks (planned)", quote from the April 2026 PAC report only; shutdown note ended at "should be re-checked"
  - new: label "NuMI run (planned: 12 weeks, stretch goal 20)", sources add the Sept 2026 PAC report; shutdown note records "MI will start up on September 21, stable beam is planned for October 1" and the transformer count; status stays `shutdown`, planned end stays 2026-10 (month)
  - source: https://pac.fnal.gov/wp-content/uploads/2026/10/Final_Public_PAC_Report_Sept2026.pdf (meeting 1-4 September 2026, posted October 2026)
  - quote: "The plan is for 12 weeks of operation in FY27, with a stretch goal of 20 weeks of operation, with a focus on the NuMI beam."
- **beamline:numi** — same two interval edits as the Main Injector; status stays `shutdown`
- **experiment:nova** — intervals["no NuMI beam (Main Injector transformer failures)"].note/sources; intervals["NuMI run..."] label/note/quote/sources
  - old: note without the September 2026 report; planned run "NuMI run, 20 weeks (planned)"
  - new: note adds the Sept 2026 PAC plan and the unresolved conflicting 7 July 2026 Fermilab statement; planned run relabelled as for the Main Injector; status stays `shutdown`
  - sources: https://pac.fnal.gov/wp-content/uploads/2026/10/Final_Public_PAC_Report_Sept2026.pdf ; https://news.fnal.gov/2026/07/fermilab-marks-70-years-of-neutrino-science-and-leads-next-generation-experiment/
  - quote: "NOvA is taking data and measuring neutrino oscillations over a 500-mile distance." (7 July 2026; the conflicting statement) | "MI will start up on September 21, stable beam is planned for October 1" (PAC, September 2026)
- **detector:nova-far-detector**, **detector:nova-near-detector** — status / intervals
  - old: status `active`; "operating" 2014-02-06 open-ended (the first pass had changed only the experiment record)
  - new: status `shutdown`; "operating" ends 2024-07; new derived interval "no NuMI beam (Main Injector transformer failures)" 2024-07 -> planned 2026-10 (mirrors experiment:nova, same conflict note)
  - source: https://pac.fnal.gov/wp-content/uploads/2026/06/Public_PAC_Report_April_2026.pdf
  - quote: "The MI has not operated since July 2024"
- **experiment:sno-plus**, **detector:sno-plus** — status / intervals
  - old: status `active`; "liquid-scintillator phase" 2022 open-ended; (experiment only) planned "tellurium-loading phase" start 2027 (an unsourced placeholder)
  - new: status `shutdown`; scintillator phase ends 2026-04 (approximate, "by April 2026"); new interval "acrylic vessel leak repair" 2026-04 (approximate) -> planned autumn 2026 (2026-10, earliest 2026-09, latest 2026-11); (experiment only) planned tellurium phase relabelled "tellurium-loaded phase (planned: 0.5% Te fill from 2028)", start 2028 (approximate, from the slide's timeline figure)
  - sources: https://indico.lip.pt/event/2184/contributions/7460/attachments/5713/9308/Advisory2026_NeutrinoPhysics.pdf ; https://cinp.ca/sites/default/files/2026-06/SNOLAB_2026CAP.pdf
  - quote: "leak in AV, height identified, lowering water now to repair, autumn restart" (LIP slide, 27-28 April 2026) | "Fill 0.5% Te" (same slide; year read from the figure) | "No damage to the neck. AV was not stuck" (SNOLAB report, 26 May 2026)
- **experiment:ctao**, **detector:ctao** — intervals (added)
  - old: construction 2015 open-ended (only)
  - new: plus phase "LST sub-array (LST-1 to LST-4, CTAO-North) completed and inaugurated", 2026-10-15; status unchanged (`construction`)
  - source: https://www.ctao.org/news/the-large-sized-telescope-sub-array-is-inaugurated-on-ctao-north/ (record `src:geo-arrays2-ctao-lst-inauguration-2026`, re-read this session)
  - quote: "celebrated the inauguration of the Large-Sized Telescope (LST) sub-array at the CTAO-North site"
- **accelerator:sns** — intervals (status stays `active`)
  - old: construction (..2006-04); upgrade "Proton Power Upgrade (1.4 -> 2.8 MW)" start null, end null (covered nothing); active "operational (first instruments commissioned)" 2007-08 open-ended
  - new: active 2007-08 .. 2023-08; upgrade 2023-08 .. 2024-07-11 (verified); new active "operating with the upgraded linac (1.3 GeV; power ramping toward 2.8 MW)" from 2024-07-11 (open)
  - sources: https://www.osti.gov/servlets/purl/2448167 (LINAC2024 THPB045); https://www.ornl.gov/news/sns-upgrade-accelerates-neutron-research-boosts-data-quality
  - quote: "The long installation outage began in August 2023 and concluded in April 2024." | "Neutron production for the user program resumed July 11th as planned at 1.3 GeV and 1.7 MW." | "The completed proton power upgrade ensures SNS will remain the world's most powerful proton accelerator" (18 May 2026)
- **experiment:haystac**, **detector:haystac** — status / intervals
  - old: status `active`; "built and in operation" 2018 (approximate) open-ended; "Phase II squeezed-state run" (kind run) 2024 (approximate, a paper's submission date) open-ended
  - new: status `upgrade`; "built and in operation" 2016-01 .. 2024-08 (verified); run "Phase I data-taking" 2016-01 .. 2017-07 (added); run "Phase II squeezed-state run" 2019-09 .. 2024-08; new interval "Phase III upgrade (multi-rod cavity) and commissioning at Yale" (upgrade) from 2024-08 (approximate), open
  - sources: https://arxiv.org/abs/2510.15848 ; https://meetings-archive.aps.org/smt/2026/apr-v89/1/
  - quote: "phase I (January 2016–July 2017) scanned axion masses from 23.15 µeV–24.0 µeV" | "phase II(c) and II(d) (September 2022–August 2024) which scanned 17.28 µeV–18.44 µeV and 18.71 µeV–19.46 µeV" | "In preparation for Phase III, HAYSTAC is currently upgrading to a multi-rod cavity that can perform high-frequency searches with a high FOM" (19 March 2026)
- **experiment:project-8** — status / intervals
  - old: status `active`; "Phase II" active from 2025-03 open-ended; "Phase III: atomic tritium R&D" `proposed`, start null, end null
  - new: status `upgrade`; Phase II start no later than 2022-12 (approximate bound), end 2025-03 (approximate bound, "over by"); Phase III relabelled "Phase III: apparatus R&D (cavity-CRES demonstrators, atomic-tritium source); no data-taking", status `upgrade`, from 2025-10 (approximate), open
  - sources: https://www.project8.org/about/ ; https://arxiv.org/abs/2503.08807 ; https://arxiv.org/abs/2212.05048 ; https://meetings-archive.aps.org/dnp/2025/p02/1/ ; https://indico.global/event/16413/contributions/153844/
  - quote: "Currently, efforts are focused on Phase III. We are developing demonstrators of various technologies and working on our detector simulations and event analysis." | "Phase II of Project 8, in addition to setting the first CRES-based neutrino mass limit, was a crucial demonstration of CRES’s potential as a precision measurement technique"
  - note: `upgrade` is a judgement (no R&D-hiatus status); detector:project-8 (Phase I apparatus, `commissioning`) was not changed
- **experiment:nexo**, **detector:nexo** — intervals (added; status stays `proposed`)
  - old: design and construction preparation 2018 open-ended
  - new: plus phase "US-led project paused (listed by SNOLAB, December 2024)" from 2024-12 (approximate)
  - source: https://cinp.ca/sites/default/files/2026-06/SNOLAB_2026CAP.pdf (SNOLAB Report, 26 May 2026, slide 26)
  - quote: "US led nEXO project was paused."
- **experiment:sensei**, **detector:sensei** — intervals (added; status stays `active`)
  - old: protoSENSEI 2018 .. 2019-01; science operations at Fermilab MINOS cavern 2019-01 open
  - new: plus phase "SNOLAB: SENSEI apparatus installed" 2021; run "SNOLAB Run 1 (first science run)" 2022-09-09 .. 2023-04-10
  - source: https://arxiv.org/abs/2312.13342
  - quote: "The SENSEI apparatus at SNOLAB was installed in 2021." | "based on data taken from September 9, 2022 to April 10, 2023"
- **experiment:p-one** — status / intervals
  - old: status `commissioning`; "pathfinder programme deployed and taking data" 2019-01 open-ended
  - new: status `construction`; pathfinder row ends 2023-07 (recovered); new construction interval "P-ONE-1 first full-scale line and demonstrator construction (line integrated, awaiting deployment)" from 2023 (approximate lower bound), open; phases 2026-04-28 (integrated), 2026-06-23 (wet test); planned phase "P-ONE-1 deployment at Cascadia Basin (planned)" 2026-08
  - sources: https://www.pacific-neutrino.org/main-menu/news/the-recovered-straw-pathfinder-hardware-is-back-in-germany-for-analysis ; https://www.pacific-neutrino.org/main-menu/news/successful-integration-of-first-detector-line-p-one-1-1 ; https://www.pacific-neutrino.org/main-menu/news/successful-wet-test-of-p-one-1-in-vancouvers-granville-island
  - quote: "The three moorings (a 500-metre string and two 150 metre in length) were disconnected and recovered during last month’s summer 2023 #ONCAbyss expedition" | "On April 28, the 1 km-long detector line P-ONE-1 was fully assembled and integrated" | "the collaboration aims to deploy P-ONE-1, including the full acoustic calibration infrastructure on the seafloor, by the end of August 2026"
- **detector:p-one** — status / intervals
  - old: status `active`; "STRAW pathfinder operating" 2019-01 open-ended
  - new: status `construction`; STRAW row ends 2023-07; new construction interval "P-ONE-1 first full-scale line: integrated 2026-04-28, wet-tested 2026-06-23, awaiting deployment" from 2023 (approximate)
  - sources: same three P-ONE news pages
- **experiment:rno-g**, **detector:rno-g** — intervals (status stays `construction`)
  - old: "deployment paused" 2023 open-ended
  - new: pause ends 2025 (approximate upper bound); new construction interval "construction resumed (2025 drilling; eight stations commissioned; 35 planned)" from 2025; (experiment only) run "eight stations commissioned" from 2026-03 and planned phase "2026 season: five new stations to be brought online (planned)" 2026-07 .. 2026-08
  - sources: https://geo-summit.org/summit-station/research-projects/collaborative-research-wou-mma-robust-searches-ultrahigh-energy-neutrinos-rno-g ; https://indico.kit.edu/event/5380/contributions/22645/ ; https://indico.kit.edu/event/5380/contributions/22649/
  - quote: "antennas in boreholes drilled in 2025 (Sites 15, 25, 34, and 35) and 2026 (Site 45)" | "As of March 2026, eight of these stations have already been commissioned with more to follow each year."
- **experiment:ara**, **detector:ara** — note/sources only (no status or date change)
  - new: note records the 2024 DAQ upgrade of two stations and the June 2026 abstracts
  - sources: https://arxiv.org/abs/2509.18368 ; https://indico.kit.edu/event/5380/contributions/22635/
  - quote: "In 2024, two of the five ARA stations received DAQ upgrades, improving the existing electronics"
