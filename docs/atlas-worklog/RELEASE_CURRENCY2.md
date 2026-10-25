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

## 4. Change log

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
