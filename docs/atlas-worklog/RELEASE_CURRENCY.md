# Release currency stream (2026-10-25)

Branch `atlas-release-currency`. Build date for rule A10 is today, 2026-10-25. Every date and status below was read in this session from the cited page or PDF (curl + text extraction, or WebFetch); verbatim quotes were copied from the extracted text, not from search snippets. INSPIRE was not used. Source records added: `data/atlas/sources/currency-*.json`.

Validator: `python -m hepgraph.atlas.validate` reports 0 errors (1588 warnings, the same count as before this stream).

Note on formatting: `experiments/kamland.json` and `detectors/kamland.json` were not in canonical A11 form (unsorted keys), so rewriting them re-serialised the whole file; the semantic change is only the interval edit listed below.

## 1. Mu3e (experiment, detector, collaboration)

Why the validator failed: the only construction interval ended 2026-09, so the derived state at 2026-10 was `proposed` (experiment, collaboration) or `unrecorded` (detector) while `status` said `construction`. The fix is a sourced lifecycle that stays open: construction has no end because the detector is still being finished and no source reports physics operation.

| Interval (experiment) | Dates | Status | Source | Verbatim evidence |
| --- | --- | --- | --- | --- |
| proposed | 2012-01-23 .. 2013-01 | proposed | INSPIRE record 1114537 (kept, start); https://www.psi.ch/en/mu3e/news-archive (end) | "The international research committee for particle physics at the ring cyclotron under the chairmanship of Dr. Cyrus Hoffman acknowledged the scientific case and approved the proposal." (item dated 16. January 2013) |
| approved | 2013-01 .. open | approved | https://www.psi.ch/en/mu3e/news-archive | same quote |
| Phase I construction | 2018-12 (approximate, lower bound) .. open | construction | https://arxiv.org/abs/1812.06540 ; https://indico.sns.it/event/140/contributions/1342/ ; https://www.psi.ch/en/mu3e/news/layer-3-pixel-modules-installed | "The first phase of the Mu3e experiment is under construction at PSI" (arXiv:1812.06540v1, 16 Dec 2018; the same paper plans construction to "begin in 2019"). June 2026 abstract: "Phase I, currently under construction at the piE5 beamline at PSI". |
| first integration run (run) | 2021-05 .. 2021-06 | commissioning | https://www.psi.ch/en/mu3e/mu3e (entry "May/June 2021") | "During an extensive campaign at PSI, the Mu3e collaboration for the first time operated parts of the detector inside the experiment magnet and with muon beam stopping on a target in the center of the experiment." |
| cosmic run (run) | 2022-05 .. 2022-06 | commissioning | https://www.psi.ch/en/mu3e/mu3e (entry "May/June 2022") | "This setup was used to develop commissioning and tuning procedures for the sensors, advance DAQ integration, develop user interfaces, check timing and finally to detect cosmic ray muons passing through the set-up." |
| June 2025 beam time (run) | 2025-06 | commissioning | https://indico.sns.it/event/140/contributions/1342/ ; https://www.psi.ch/en/mu3e/news/successful-mu3e-beam-time | "In preparation for Phase I data-taking, a crucial commissioning campaign took place in June 2025"; "In June, Mu3e took three weeks of muon beam at PSI." |
| 2026 installation of the central station (phase) | 2026-07-10 .. 2026-09-24 | construction | https://www.psi.ch/en/mu3e/news ; https://www.psi.ch/en/mu3e/news/mu3e-craned-into-the-area | "Mu3e has installed the vertex detector for the 2026 beamtime, marking an important milestone in the detector assembly." (10.07.2026); end: "Today Mu3e was craned from the staging setup to the PiE5 area, where the experiment was inserted into the Mu3e magnet." (24.09.2026) |
| pixel-tracker installation, third layer (phase; existing row, now day precision) | 2026-09-16 | construction | https://www.psi.ch/en/mu3e ; https://www.psi.ch/en/mu3e/news/layer-3-pixel-modules-installed | "The third layer of the Mu3e pixel detector was sucessfully installed." |
| two-month beam time (planned run) | 2026-10 .. 2026-11 | planned | https://www.psi.ch/en/mu3e/news/layer-3-pixel-modules-installed | "The layer three installation is the last big installation before our two month beam time in October and November." |
| first physics run (planned) | 2027 | planned | https://indico.sns.it/event/140/contributions/1342/ | "an outlook on the 2026 campaign leading towards the physics run, anticipated in 2027" |

Detector and collaboration records mirror these rows (detector: construction + the two installation phases; collaboration: proposed, approved, construction). `status` stays `construction` in all three and now equals the derived state. Current state as of 2026-10-25: the newest PSI news item is dated 24.09.2026; no fetched source reports that the October-November beam time has started, so the entity is recorded as construction, not active. Formation date of the collaboration remains unsourced (null).

Schedule slip recorded in the planned row: commissioning run expected 2020 (arXiv:1812.06540), first physics data-taking "estimated for 2026" (arXiv:2501.14667 section 3; arXiv:2503.22461 section 2.3, which also says data-taking resumes at the end of 2028 after a HIPA long shutdown in 2027-2028), now "anticipated in 2027" (June 2026). How 2027 fits the HIPA shutdown is not stated by any source fetched.

## 2. Transitions recorded as ending in 2026

- LHC Run 3 / Long Shutdown 3: yes, Run 3 ended in June 2026 as scheduled. CERN, 29 June 2026 (item on https://home.cern/science/long-shutdown-3/): "On Saturday 27 June at 6 am, the LHC’s Page 1 — the accelerator’s dashboard — said “goodbye” to collisions. The LHC operators dumped the last beams before the accelerator’s metamorphosis." and (5 August 2026) "The cryogenics team has been running the warm-up sequence since LS3 began on 29 June 2026." The experiments (ATLAS, CMS, LHCb, TOTEM, ALICE, FASER, LHCf, SND@LHC, detectors atlas/cms) all already had a dated LS3 successor interval (month 2026-06, consistent), so they were left unchanged. `accelerator:lhc` was refined to day precision and its LS3 end corrected from a planned 2028 to mid-2030 (see change log).
- Extra consequence of the same transition, not on the brief: the other CERN accelerators stopped on 31 August 2026 ("CERN’s injector complex and Antimatter Factory took their final steps towards Long Shutdown 3 (LS3) this morning, as the last particle beams were extracted and the machines fell silent."). PS, PSB, SPS and Linac4 were still `active` open-ended; NA62 and NA64 (SPS North Area) and MoEDAL (LHC) were too. Fixed (see change log).
- RHIC: final run ended 2026-02-06, confirmed against https://www.bnl.gov/newsroom/news.php?a=122794. STAR and sPHENIX correctly record a `completed` terminal interval from 2026-02-06. Correction: the RHIC note said the EIC reuses "part of the sPHENIX detector hall"; BNL (13 April 2026, https://www.bnl.gov/newsroom/news.php?a=122863) says the interaction region occupied by STAR becomes the ePIC site and sPHENIX will be disassembled except its outer hadronic calorimeter. Neither detector is recorded as decommissioned because no source reports that disassembly has started.
- SuperCDMS SNOLAB: the successor to commissioning exists (early-science `active` from 2026-08, SLAC 26 August 2026, "has begun collecting its very first scientific data"). Commissioning start corrected from 2026-03 to 2026-01 (collaboration talk of 29 July 2026: "Reached base temperature in Jan 2026"). Planned SR1b ("Cooldown and data taking: early 2027") added. Currency limit: no source newer than 26 August 2026 was found; the July talk anticipated the first run "to continue until Sept 2026" followed by a full warm-up, so the experiment may already be warming up, which no source reports.
- IceCube Upgrade: deployment is complete (five strings in the 2025/26 season) and commissioning is ongoing as of 21 September 2026 (arXiv:2609.24387: "The recently deployed IceCube Upgrade is presently in its commissioning phase before its integration into the IceCube data acquisition."); science data-taking is planned for "fall 2026" (added as a planned interval).

## 3. Scan for statuses that change before 2027-01

Throwaway script (not committed): `/private/tmp/claude-501/-Users-yatharthsirohi-Desktop-HEP-Graph/eed887c7-349d-45f2-a24f-fe22c2d1c9c2/scratchpad/currency/scan.py`. It compares `state_at` at 2026-10 and 2027-01 for every entity and lists intervals that end or start in the window.

- Before this stream: no entity had an interval ending between 2026-10-25 and 2027-01-31. The only finds were three `planned` ends dated 2011-12 (J-PARC main ring, J-PARC neutrino beamline, T2K) that had never been replaced; fixed with "2012 January Operation resumed and user operation started." from https://j-parc.jp/c/en/about/history.html (facility-wide statement, confidence stays derived).
- The scan cannot see an open-ended `active` interval that has already ended. A delegated audit of the 100 or so non-terminal experiments, accelerators and beamlines for 2025-2026 changes found the ones listed in the change log (KamLAND, KamLAND-Zen, PandaX-4T, XENONnT, DEAP-3600, Ricochet, ALPS II, CONUS, KATRIN, Fermilab Main Injector / NuMI / NOvA). Each was re-fetched and the quoted text confirmed before editing.
- After this stream, statuses that will change by 2027-01 if the plans hold: Fermilab Main Injector, NuMI and NOvA (planned restart October 2026, unconfirmed), Ricochet (first science phase planned to end at the end of 2026), XENONnT (upgrade/commissioning dates are year-level), Mu3e (planned beam time October-November 2026), IceCube Upgrade (science data planned fall 2026), SuperCDMS (SR1a ends, warm-up, SR1b early 2027).

## 4. Change log

- **experiment:mu3e** — intervals
  - old: proposed 2012-01-23 open; construction 2026-09..2026-09 (only)
  - new: proposed 2012-01-23..2013-01; approved 2013-01; construction 2018-12 (approx, open); runs 2021-05/06, 2022-05/06, 2025-06; phase 2026-07-10..09-24 and 2026-09-16; planned beam time 2026-10/11; planned physics run 2027
  - sources: https://www.psi.ch/en/mu3e/news-archive; https://arxiv.org/abs/1812.06540; https://www.psi.ch/en/mu3e/news; https://www.psi.ch/en/mu3e/news/layer-3-pixel-modules-installed; https://indico.sns.it/event/140/contributions/1342/
  - quote: "The international research committee for particle physics at the ring cyclotron under the chairmanship of Dr. Cyrus Hoffman acknowledged the scientific case and approved the proposal. | The first phase of the Mu3e experiment is under construction at PSI"
- **detector:mu3e** — intervals
  - old: construction 2026-09..2026-09 (only)
  - new: construction 2018-12 (approx, open); phase rows 2026-07-10..09-24 and 2026-09-16
  - sources: https://arxiv.org/abs/1812.06540; https://www.psi.ch/en/mu3e/news
  - quote: "The first phase of the Mu3e experiment is under construction at PSI"
- **collaboration:mu3e** — intervals
  - old: proposed 2012-01-23 open; construction 2026-09..2026-09
  - new: proposed 2012-01-23..2013-01; approved 2013-01; construction 2018-12 (approx, open)
  - sources: https://www.psi.ch/en/mu3e/news-archive; https://arxiv.org/abs/1812.06540
  - quote: "The international research committee for particle physics at the ring cyclotron under the chairmanship of Dr. Cyrus Hoffman acknowledged the scientific case and approved the proposal. | The first phase of the Mu3e experiment is under construction at PSI"
- **accelerator:lhc** — intervals[Run 3].end
  - old: 2026-06
  - new: 2026-06-27
  - sources: https://home.cern/science/long-shutdown-3/
  - quote: "On Saturday 27 June at 6 am, the LHC’s Page 1 — the accelerator’s dashboard — said “goodbye” to collisions. The LHC operators dumped the last beams before the accelerator’s metamorphosis."
- **accelerator:lhc** — intervals[Long Shutdown 3].start
  - old: 2026-06
  - new: 2026-06-29
  - sources: https://home.cern/science/long-shutdown-3/
  - quote: "The cryogenics team has been running the warm-up sequence since LS3 began on 29 June 2026."
- **accelerator:lhc** — intervals[Long Shutdown 3].end
  - old: {'approx': True, 'date': '2028', 'note': "'The accelerator complex and its experiment facilities will gradually resume operation from mid-2028 onwards' (home.cern/science/long-shutdown-3).", 'planned': True}
  - new: planned 2030 (mid-2030)
  - sources: https://home.cern/science/long-shutdown-3/
  - quote: "stored ready to be used again once the accelerator resumes operation in mid-2030"
- **accelerator:ps** — status / intervals
  - old: status active; "operating" open-ended
  - new: status shutdown; operating interval ends 2026-08-31; new shutdown interval 2026-08-31 -> planned 2028
  - sources: https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/; https://home.cern/accelerator-report-final-countdown-cerns-injector-complex-enters-its-last-stretch-before-ls3/
  - quote: "CERN’s injector complex and Antimatter Factory took their final steps towards Long Shutdown 3 (LS3) this morning, as the last particle beams were extracted and the machines fell silent."
- **accelerator:psb** — status / intervals
  - old: status active; "operating" open-ended
  - new: status shutdown; operating interval ends 2026-08-31; new shutdown interval 2026-08-31 -> planned 2028
  - sources: https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/; https://home.cern/accelerator-report-final-countdown-cerns-injector-complex-enters-its-last-stretch-before-ls3/
  - quote: "CERN’s injector complex and Antimatter Factory took their final steps towards Long Shutdown 3 (LS3) this morning, as the last particle beams were extracted and the machines fell silent."
- **accelerator:sps** — status / intervals
  - old: status active; "operating" open-ended
  - new: status shutdown; operating interval ends 2026-08-31; new shutdown interval 2026-08-31 -> planned 2028
  - sources: https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/; https://home.cern/accelerator-report-final-countdown-cerns-injector-complex-enters-its-last-stretch-before-ls3/
  - quote: "CERN’s injector complex and Antimatter Factory took their final steps towards Long Shutdown 3 (LS3) this morning, as the last particle beams were extracted and the machines fell silent."
- **accelerator:linac4** — status / intervals
  - old: status active; "CERN's proton source" open-ended
  - new: status shutdown; operating interval ends 2026-08-31; new shutdown interval 2026-08-31 -> planned 2028
  - sources: https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/; https://home.cern/accelerator-report-final-countdown-cerns-injector-complex-enters-its-last-stretch-before-ls3/
  - quote: "CERN’s injector complex and Antimatter Factory took their final steps towards Long Shutdown 3 (LS3) this morning, as the last particle beams were extracted and the machines fell silent."
- **experiment:na62** — status / intervals
  - old: status active; "Run 2" open-ended
  - new: status shutdown; "Run 2" ends 2026-08-31; new shutdown interval from 2026-08-31 (derived)
  - sources: https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/
  - quote: "CERN’s injector complex and Antimatter Factory took their final steps towards Long Shutdown 3 (LS3) this morning, as the last particle beams were extracted and the machines fell silent."
  - note: derived from the SPS stop; no experiment-specific source
- **detector:na62** — status / intervals
  - old: status active; "operating" open-ended
  - new: status shutdown; "operating" ends 2026-08-31; new shutdown interval from 2026-08-31 (derived)
  - sources: https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/
  - quote: "CERN’s injector complex and Antimatter Factory took their final steps towards Long Shutdown 3 (LS3) this morning, as the last particle beams were extracted and the machines fell silent."
  - note: derived from the SPS stop; no experiment-specific source
- **experiment:na64** — status / intervals
  - old: status active; "operating" open-ended
  - new: status shutdown; "operating" ends 2026-08-31; new shutdown interval from 2026-08-31 (derived)
  - sources: https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/
  - quote: "CERN’s injector complex and Antimatter Factory took their final steps towards Long Shutdown 3 (LS3) this morning, as the last particle beams were extracted and the machines fell silent."
  - note: derived from the SPS stop; no experiment-specific source
- **detector:na64** — status / intervals
  - old: status active; "operating" open-ended
  - new: status shutdown; "operating" ends 2026-08-31; new shutdown interval from 2026-08-31 (derived)
  - sources: https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/
  - quote: "CERN’s injector complex and Antimatter Factory took their final steps towards Long Shutdown 3 (LS3) this morning, as the last particle beams were extracted and the machines fell silent."
  - note: derived from the SPS stop; no experiment-specific source
- **experiment:moedal** — status / intervals
  - old: status upgrade
  - new: status shutdown; shutdown interval from 2026-06 (derived from the LHC switch-off)
  - sources: https://home.cern/science/long-shutdown-3/
  - quote: "On Saturday 27 June at 6 am, the LHC’s Page 1 — the accelerator’s dashboard — said “goodbye” to collisions. The LHC operators dumped the last beams before the accelerator’s metamorphosis."
  - note: derived
- **detector:moedal** — status / intervals
  - old: status active
  - new: status shutdown; shutdown interval from 2026-06 (derived from the LHC switch-off)
  - sources: https://home.cern/science/long-shutdown-3/
  - quote: "On Saturday 27 June at 6 am, the LHC’s Page 1 — the accelerator’s dashboard — said “goodbye” to collisions. The LHC operators dumped the last beams before the accelerator’s metamorphosis."
  - note: derived
- **accelerator:rhic** — intervals[final run].note
  - old: EIC reuses "part of the sPHENIX detector hall"
  - new: EIC reuses "a large detector hall"; STAR interaction region becomes the ePIC site; sPHENIX to be disassembled except its outer HCal; removal programme about six years from 2026-04-13
  - sources: https://www.bnl.gov/newsroom/news.php?a=122863
  - quote: "will be taken apart to make way for the new ePIC detector being designed and constructed for the Electron-Ion Collider | The removal process is expected to take place over a period of six years"
- **experiment:star** — intervals[RHIC final run].note/sources
  - old: Marks the end of RHIC operations in the 25th and final run. STAR's own future (decommissioning vs. continued data analysis only) is not detailed in fetched sources; BNL states the RHIC science mission continues 'until we analyze all the data and publish all the papers.'
  - new: BNL, 13 April 2026: STAR, "which captured the first collisions at the Relativistic Heavy Ion Collider (RHIC) in 2000 and ran through every RHIC run until Feb. 6, 2026, will be taken apart to make way for the new ePIC detector being designed and constructed for the Electron-Ion Collider"; the STAR interaction region becomes the site of ePIC. Disassembly is part of a six-year removal programme begun 13 April 2026; no source fetched reports that STAR's disassembly has started, so the status stays completed (operations ended), not decommissioned.
  - sources: https://www.bnl.gov/newsroom/news.php?a=122863
  - quote: "will be taken apart to make way for the new ePIC detector being designed and constructed for the Electron-Ion Collider"
  - note: status stays completed
- **detector:star** — intervals[RHIC final run].note/sources
  - old: (empty)
  - new: BNL, 13 April 2026: the STAR detector "will be taken apart to make way for the new ePIC detector being designed and constructed for the Electron-Ion Collider"; no source fetched reports that its disassembly has started, so the status stays completed.
  - sources: https://www.bnl.gov/newsroom/news.php?a=122863
  - quote: "will be taken apart to make way for the new ePIC detector being designed and constructed for the Electron-Ion Collider"
  - note: status stays completed
- **experiment:sphenix** — intervals[RHIC final run].note/sources
  - old: (empty)
  - new: BNL, 13 April 2026: the sPHENIX detector, "which took data from 2023 to 2026, will be disassembled, but its outer hadronic calorimeter" ... will be used in the new detector for the Electron-Ion Collider"; "One major component of the sPHENIX detector — its outer hadronic calorimeter — will be reused for this new EIC experiment." No source fetched reports that disassembly has started, so the status stays completed.
  - sources: https://www.bnl.gov/newsroom/news.php?a=122863
  - quote: "which took data from 2023 to 2026, will be disassembled, but its outer hadronic calorimeter"
  - note: status stays completed
- **detector:sphenix** — intervals[RHIC final run].note/sources
  - old: (empty)
  - new: BNL, 13 April 2026: sPHENIX "will be disassembled" except its outer hadronic calorimeter, which is to be reused in ePIC; no source fetched reports that disassembly has started, so the status stays completed.
  - sources: https://www.bnl.gov/newsroom/news.php?a=122863
  - quote: "which took data from 2023 to 2026, will be disassembled, but its outer hadronic calorimeter"
  - note: status stays completed
- **experiment:supercdms** — commissioning start / construction end / planned run
  - old: commissioning start 2026-03, construction end 2026-03, no successor schedule
  - new: commissioning start 2026-01 (construction end 2026-01); planned SR1b early 2027; early-science note updated
  - sources: https://indico.global/event/16618/contributions/158582/attachments/74425/144354/WilsonLDW26.pdf; https://www6.slac.stanford.edu/news/2026-08-26-supercdms-snolab-begins-preliminary-phase-dark-matter-hunt
  - quote: "Reached base temperature in Jan 2026 | Cooldown and data taking: early 2027"
- **detector:supercdms** — commissioning start / construction end / planned run
  - old: commissioning start 2026-03, construction end 2026-03, no successor schedule
  - new: commissioning start 2026-01 (construction end 2026-01); planned SR1b early 2027; early-science note updated
  - sources: https://indico.global/event/16618/contributions/158582/attachments/74425/144354/WilsonLDW26.pdf; https://www6.slac.stanford.edu/news/2026-08-26-supercdms-snolab-begins-preliminary-phase-dark-matter-hunt
  - quote: "Reached base temperature in Jan 2026 | Cooldown and data taking: early 2027"
- **experiment:icecube-upgrade** — intervals
  - old: construction 2023..2026-02; commissioning 2026-02 open
  - new: unchanged, plus Sept 2026 confirmation source and planned science start fall 2026
  - sources: https://arxiv.org/abs/2609.24387
  - quote: "The 5 commissioned strings work well and are expected to start taking science data with the rest of the detector in fall 2026."
- **experiment:katrin** — status / intervals
  - old: status active; measurement campaigns 2019 open-ended
  - new: status commissioning; measurement campaigns end 2025-10-26; TRISTAN commissioning from 2026-04
  - sources: https://www.mpi-hd.mpg.de/mpi/en/public-relations/news/news-item/1000-days-of-neutrino-mass-measurements; https://www.deib.polimi.it/eng/news-and-events/details/1504; https://www.mpi-hd.mpg.de/mpi/en/public-relations/news/news-item/1000-days-of-katrin-data
  - quote: "on Oct 26th KATRIN accomplished its goal of 1000 measurement days of probing the endpoint region of the tritium beta-decay spectrum with unprecedented sensitivity, marking the completion of its neutrino-mass data taking. | celebrated the achievement of 1,000 days of neutrino measurements with the inauguration of phase 2 of the project: the commissioning of a new and more sophisticated detector, TRISTAN."
- **detector:katrin** — status / intervals
  - old: status active; measurement campaigns 2019 open-ended
  - new: status commissioning; measurement campaigns end 2025-10-26; TRISTAN commissioning from 2026-04
  - sources: https://www.mpi-hd.mpg.de/mpi/en/public-relations/news/news-item/1000-days-of-neutrino-mass-measurements; https://www.deib.polimi.it/eng/news-and-events/details/1504; https://www.mpi-hd.mpg.de/mpi/en/public-relations/news/news-item/1000-days-of-katrin-data
  - quote: "on Oct 26th KATRIN accomplished its goal of 1000 measurement days of probing the endpoint region of the tritium beta-decay spectrum with unprecedented sensitivity, marking the completion of its neutrino-mass data taking. | celebrated the achievement of 1,000 days of neutrino measurements with the inauguration of phase 2 of the project: the commissioning of a new and more sophisticated detector, TRISTAN."
- **experiment:kamland** — status / intervals
  - old: status active; active 2002-01-17 open-ended
  - new: status upgrade; active ends 2024-08-27; upgrade 2024-08-27 -> planned 2028
  - sources: https://arxiv.org/abs/2606.29381; https://indico-cdex.ep.tsinghua.edu.cn/event/175/contributions/2276/attachments/860/1264/TAUP2025_KamLANDZen_KellyWeerman.pdf; https://conference-indico.kek.jp/event/352/contributions/7333/attachments/4925/8069/Q-EYES2025_ishidoshiro.pdf
  - quote: "KamLAND began data taking in March 2002 and ended data taking in August 2024. | Last physics run on August 27th 2024 | Stop KamLAND DAQ: Aug. 2024"
- **detector:kamland** — status / intervals
  - old: status active; active 2002-01-17 open-ended
  - new: status upgrade; active ends 2024-08-27; upgrade 2024-08-27 -> planned 2028
  - sources: https://arxiv.org/abs/2606.29381; https://indico-cdex.ep.tsinghua.edu.cn/event/175/contributions/2276/attachments/860/1264/TAUP2025_KamLANDZen_KellyWeerman.pdf; https://conference-indico.kek.jp/event/352/contributions/7333/attachments/4925/8069/Q-EYES2025_ishidoshiro.pdf
  - quote: "KamLAND began data taking in March 2002 and ended data taking in August 2024. | Last physics run on August 27th 2024 | Stop KamLAND DAQ: Aug. 2024"
- **experiment:kamland-zen** — status / intervals
  - old: status active; active 2022 (lower bound) open-ended
  - new: status upgrade; KamLAND-Zen 800 data taking 2019-02-05..2024-01-12; upgrade from 2024-01 -> planned 2029
  - sources: https://arxiv.org/abs/2406.11438
  - quote: "KamLAND-Zen 800 completed data-taking in January 2024 to start dismantling the current KamLAND detector in preparation for a detector upgrade, KamLAND2-Zen."
- **experiment:pandax-4t** — status / intervals
  - old: status active; science operations 2021 open-ended
  - new: status completed; science operations end 2026-04-15; completed 2026-04-15; decommissioned 2026-05
  - sources: https://indico.ihep.ac.cn/event/28557/contributions/223888/; https://arxiv.org/abs/2607.02405; https://indico.ihep.ac.cn/event/28557/contributions/223732/attachments/104759/141514/PandaX-report-xiangyicui.pdf
  - quote: "After completing three data-taking runs, the PandaX-4T experiment concluded its operation and was decommissioned in May 2026. | Shut down at Apr. 15th"
- **detector:pandax-4t** — status / intervals
  - old: status active; science operations 2021 open-ended
  - new: status completed; science operations end 2026-04-15; completed 2026-04-15; decommissioned 2026-05
  - sources: https://indico.ihep.ac.cn/event/28557/contributions/223888/; https://arxiv.org/abs/2607.02405; https://indico.ihep.ac.cn/event/28557/contributions/223732/attachments/104759/141514/PandaX-report-xiangyicui.pdf
  - quote: "After completing three data-taking runs, the PandaX-4T experiment concluded its operation and was decommissioned in May 2026. | Shut down at Apr. 15th"
- **experiment:xenonnt** — status / intervals
  - old: status active; science operations 2021-07-06 open-ended
  - new: status commissioning; science operations end 2025 (approx); upgrade summer 2025 -> 2026; commissioning from 2026
  - sources: https://indico.cern.ch/event/1645696/contributions/7094892/; https://indico.nikhef.nl/event/7584/contributions/31307/; https://indico.nikhef.nl/event/7799/sessions/2514/attachments/11042/17101/DM-Jamboree-Decowski-May26.pdf
  - quote: "Following upgrade operations conducted in 2025, the experiment began its new commissioning phase in 2026."
- **detector:xenonnt** — status / intervals
  - old: status active; science operations 2021-07-06 open-ended
  - new: status commissioning; science operations end 2025 (approx); upgrade summer 2025 -> 2026; commissioning from 2026
  - sources: https://indico.cern.ch/event/1645696/contributions/7094892/; https://indico.nikhef.nl/event/7584/contributions/31307/; https://indico.nikhef.nl/event/7799/sessions/2514/attachments/11042/17101/DM-Jamboree-Decowski-May26.pdf
  - quote: "Following upgrade operations conducted in 2025, the experiment began its new commissioning phase in 2026."
- **experiment:deap-3600** — status / intervals
  - old: status upgrade; science operations 2016-11 open-ended; upgrade 2026-09 open-ended (SNOLAB "Upgrading")
  - new: status active; second fill ends 2020-03; upgrade 2020-03..2025-02; third fill active from ~2025 (uncertain); 2026-09 SNOLAB-label interval demoted to a phase annotation
  - sources: https://indico.stfc.ac.uk/event/1730/contributions/10969/; https://indico.global/event/15553/contributions/145960; https://indico.global/event/442/contributions/125209; https://conference.ippp.dur.ac.uk/event/1371/contributions/8460/attachments/6556/8928/PASCOS_Pushparaj.pdf
  - quote: "These improvements are now being evaluated in the newly initiated third fill run. | 3 Year Dataset (Nov 2016 to March 2020) | The installation of these upgrades was finished in February 2025"
  - note: the status change upgrade -> active is a judgement between two conflicting sources; see the interval notes
- **detector:deap-3600** — status / intervals
  - old: status upgrade; science operations 2016-11 open-ended; upgrade 2026-09 open-ended (SNOLAB "Upgrading")
  - new: status active; second fill ends 2020-03; upgrade 2020-03..2025-02; third fill active from ~2025 (uncertain); 2026-09 SNOLAB-label interval demoted to a phase annotation
  - sources: https://indico.stfc.ac.uk/event/1730/contributions/10969/; https://indico.global/event/15553/contributions/145960; https://indico.global/event/442/contributions/125209; https://conference.ippp.dur.ac.uk/event/1371/contributions/8460/attachments/6556/8928/PASCOS_Pushparaj.pdf
  - quote: "These improvements are now being evaluated in the newly initiated third fill run. | 3 Year Dataset (Nov 2016 to March 2020) | The installation of these upgrades was finished in February 2025"
  - note: the status change upgrade -> active is a judgement between two conflicting sources; see the interval notes
- **experiment:ricochet** — status / intervals
  - old: status commissioning; commissioning 2025 open-ended
  - new: status active; commissioning ends 2025-07; science phase 2025-07 -> planned end 2026
  - sources: https://indico.in2p3.fr/event/37960/contributions/172562/; https://indico-cdex.ep.tsinghua.edu.cn/event/175/contributions/2295/attachments/1033/1565/20250827_Novati_Ricochet_TAUP.pdf
  - quote: "RICOCHET began its first science phase in July 2025 with 18 detectors installed, and is foreseen to complete at the end of 2026."
- **experiment:alps-ii** — status / intervals
  - old: status active; operating 2023-05-23 open-ended
  - new: status upgrade; operating ends 2024-05; upgrade from 2024-05 (start approximate)
  - sources: https://arxiv.org/abs/2512.14110
  - quote: "searched for axions and similar lightweight particles in its first science campaign from February to May 2024 | Currently, the optical system of ALPS II is being upgraded aiming for another two orders of magnitude sensitivity increase."
- **detector:alps-ii** — status / intervals
  - old: status active; operating 2023-05-23 open-ended
  - new: status upgrade; operating ends 2024-05; upgrade from 2024-05 (start approximate)
  - sources: https://arxiv.org/abs/2512.14110
  - quote: "searched for axions and similar lightweight particles in its first science campaign from February to May 2024 | Currently, the optical system of ALPS II is being upgraded aiming for another two orders of magnitude sensitivity increase."
- **experiment:conus** — intervals[Brokdorf]
  - old: start None, end 2024-01
  - new: start 2018, end 2022
  - sources: https://arxiv.org/abs/2605.22815
  - quote: "Germany from 2018-2022 and Leibstadt (KKL), Switzerland from 2023"
- **accelerator:fermilab-main-injector** — status / intervals
  - old: status active; "operating" open-ended
  - new: status shutdown; operating ends 2024-07; no-beam shutdown 2024-07 -> planned restart 2026-10 (unconfirmed)
  - sources: https://pac.fnal.gov/wp-content/uploads/2026/06/Public_PAC_Report_April_2026.pdf; https://indico.jacow.org/event/95/contributions/13614/
  - quote: "The MI has not operated since July 2024 | A 20 week run is planned from October 2026 to Feb 2027 to run NuMI."
- **beamline:numi** — status / intervals
  - old: status active; "NOvA / MINOS+ / MINERvA era" open-ended
  - new: status shutdown; operating ends 2024-07; no-beam shutdown 2024-07 -> planned restart 2026-10 (unconfirmed)
  - sources: https://pac.fnal.gov/wp-content/uploads/2026/06/Public_PAC_Report_April_2026.pdf; https://indico.jacow.org/event/95/contributions/13614/
  - quote: "The MI has not operated since July 2024 | A 20 week run is planned from October 2026 to Feb 2027 to run NuMI."
- **experiment:nova** — status / intervals
  - old: status active; beam operation 2014-02-06 open-ended
  - new: status shutdown; beam operation ends 2024-07; no-beam interval 2024-07 -> planned 2026-10 (derived from NuMI, unconfirmed restart)
  - sources: https://pac.fnal.gov/wp-content/uploads/2026/06/Public_PAC_Report_April_2026.pdf
  - quote: "The MI has not operated since July 2024 | Following the record achievement, the Main Injector complex suffered a series of failures that have prevented NuMI beam."
  - note: derived from the beam source
- **accelerator:j-parc-main-ring** — intervals[2011 earthquake shutdown].end
  - old: {'date': '2011-12', 'planned': True}
  - new: 2012-01
  - sources: https://j-parc.jp/c/en/about/history.html
  - quote: "2012 January Operation resumed and user operation started."
  - note: facility-wide statement
- **beamline:j-parc-neutrino** — intervals[2011 earthquake shutdown].end
  - old: {'date': '2011-12', 'planned': True}
  - new: 2012-01
  - sources: https://j-parc.jp/c/en/about/history.html
  - quote: "2012 January Operation resumed and user operation started."
  - note: facility-wide statement
- **experiment:t2k** — intervals[2011 earthquake shutdown].end
  - old: {'date': '2011-12', 'planned': True}
  - new: 2012-01
  - sources: https://j-parc.jp/c/en/about/history.html
  - quote: "2012 January Operation resumed and user operation started."
  - note: facility-wide statement
- **accelerator:fermilab-main-injector** — planned run added
  - old: (none)
  - new: planned NuMI run 2026-10 -> 2027-02
  - sources: https://pac.fnal.gov/wp-content/uploads/2026/06/Public_PAC_Report_April_2026.pdf
  - quote: "A 20 week run is planned from October 2026 to Feb 2027 to run NuMI."
- **beamline:numi** — planned run added
  - old: (none)
  - new: planned NuMI run 2026-10 -> 2027-02
  - sources: https://pac.fnal.gov/wp-content/uploads/2026/06/Public_PAC_Report_April_2026.pdf
  - quote: "A 20 week run is planned from October 2026 to Feb 2027 to run NuMI."
- **experiment:nova** — planned run added
  - old: (none)
  - new: planned NuMI run 2026-10 -> 2027-02
  - sources: https://pac.fnal.gov/wp-content/uploads/2026/06/Public_PAC_Report_April_2026.pdf
  - quote: "A 20 week run is planned from October 2026 to Feb 2027 to run NuMI."
- **experiment:ricochet** — intervals[pre-construction/construction].end
  - old: None
  - new: 2025 (approx)
  - sources: https://indico-cdex.ep.tsinghua.edu.cn/event/175/contributions/2295/attachments/1033/1565/20250827_Novati_Ricochet_TAUP.pdf
  - quote: "The installation and phased commissioning are completed."
  - note: housekeeping so the old open construction interval does not outlive commissioning

## 5. Found but not applied

From the delegated audit (a read-only agent per batch). Items marked (opened) I re-opened myself; the others are the agent's report and have not been re-read by me.

- experiment:sno-plus (opened): LIP advisory-committee slides, 27-28 April 2026 (https://indico.lip.pt/event/2184/contributions/7460/attachments/5713/9308/Advisory2026_NeutrinoPhysics.pdf): "Acrylic Vessel Repairs leak in AV, height identified, lowering water now to repair, autumn restart"; timeline row "Repairs ... Fill 0.5% Te ... 0.5% data". Contradicts the Atlas placeholder "tellurium-loading 2027" and may mean the scintillator phase has paused. Not applied: single slide, "autumn restart" is ambiguous, no pause date.
- accelerator:sns: ORNL news of 18 May 2026 calls the proton power upgrade "completed" (WebFetch only; no completion date). The Atlas keeps an open `upgrade` interval.
- experiment:haystac (Phase III upgrade, APS abstract 19 Mar 2026), experiment:project-8 (Phase III current focus, undated About page), experiment:nexo ("US led nEXO project was paused", SNOLAB report 26 May 2026), experiment:sensei (SNOLAB runs missing from the record), experiment:p-one (STRAW recovered July 2023; first line deployment target end of August 2026 unconfirmed), experiment:rno-g (8 stations operating, drilling resumed 2025), experiment:ctao (LST sub-array inaugurated 15 October 2026, overall status still construction), experiment:ara (planned upgrade outcome unknown): medium confidence or status unchanged; left for a data-quality pass.
- accelerator:lansce (low-energy operation in 2024), accelerator:ags (no source on AGS beam after the RHIC final run), accelerator:fermilab-recycler (role label), j-parc main ring and neutrino beamline (power figures 830-900 kW, 1.3 MW planned by 2028), experiment:meg-ii (data taking "through 2025-2026"), experiment:cuore (near its 3 tonne-year stopping exposure), experiment:darkside-20k (late-2026 start unrealistic), experiment:comet (beam early 2028), experiment:damic-m (installation summer 2026): schedule drift or role wording, no state change.

## 6. Unresolved

- Whether the Fermilab Main Injector / NuMI / NOvA restart planned for October 2026 happened (Fermilab pages were not reachable and the shared web-search budget ran out). The Atlas records a shutdown from 2024-07 with a planned restart in 2026-10; re-check before release.
- Whether SuperCDMS is still in its early-science run or already warming up; whether the Mu3e October-November 2026 beam time has begun; whether the DEAP-3600 third fill is still taking data.
- KamLAND start day (2002-01-17 from Wikipedia vs "March 2002" in the 2026 collaboration paper).
