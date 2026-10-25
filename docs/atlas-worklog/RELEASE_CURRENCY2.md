# Release currency, second pass (2026-10-25)

Branch `atlas-release-currency2`. Build date for rule A10 is 2026-10-25. Every date and status below was read in this session from the cited page or PDF (curl + `pdftotext`, WebFetch, or the Browser pane for HTML pages); verbatim quotes were copied from the extracted text. INSPIRE was not used. New source records: `data/atlas/sources/currency2-*.json`. Method and the first pass: `docs/atlas-worklog/RELEASE_CURRENCY.md`.

Access note: several Fermilab hosts (indico.fnal.gov, nova-docdb, lss.fnal.gov, ftbf/mu2e/sbn sites, fnal.gov operations pages) refuse non-browser clients with HTTP 403; no attempt was made to get around that. Pages that load for a plain client (news.fnal.gov, pac.fnal.gov) were used.

Validator after each step: `python -m hepgraph.atlas.validate` reports 0 errors.

## 1. Fermilab restart (Main Injector / NuMI / NOvA)

Result: not confirmed. The newest source is the Fermilab PAC report of the 1-4 September 2026 meeting (posted October 2026, https://pac.fnal.gov/wp-content/uploads/2026/10/Final_Public_PAC_Report_Sept2026.pdf). It still states the restart as a plan: "Beam has already been established in Linac and Booster (Aug 26), MI will start up on September 21, stable beam is planned for October 1". It also reports progress (6 of 8 transformers operational, up from 3 at the April meeting; "A minimum of 2 Kautz transformers are needed to operate MI at full energy"; a new spare transformer "will be delivered in December") and that "The plan is for 12 weeks of operation in FY27, with a stretch goal of 20 weeks of operation, with a focus on the NuMI beam." No source dated after 21 September 2026 was reachable: the Fermilab newsroom (checked through 22 October 2026, including its RSS feed) has no item about a Main Injector or NuMI restart, and the sites that would carry beam status refused access. So the accelerator, the beamline and NOvA stay `shutdown` with the planned restart left in place; only notes and the planned-run schedule were updated.

Conflict recorded, not resolved: Fermilab's own 7 July 2026 feature (https://news.fnal.gov/2026/07/fermilab-marks-70-years-of-neutrino-science-and-leads-next-generation-experiment/) says "NOvA, another crucial neutrino experiment hosted by Fermilab, is the only currently operating long-baseline neutrino experiment in the United States ... NOvA is taking data and measuring neutrino oscillations over a 500-mile distance." The PAC reports of April and September 2026 are specific that the Main Injector has not delivered NuMI beam since July 2024, and the feature does not say which data NOvA takes, so `shutdown` (no NuMI beam data-taking) was kept; the detectors are not recorded as powered down. If the integrator prefers `active` for the experiment, the beam-off row would have to become a `phase` annotation (the validator would then warn A12, active with no active listed beamline).

Other NuMI-fed entities checked by grep: `minerva`, `minos`, `minos-plus` are `completed` (unchanged); `icarus` is `active` on the Booster Neutrino Beam (the FY26 BNB run ended 12 June 2026, "72.9%" uptime) and was left unchanged; `fermilab-booster` and `fermilab-linac` kept running ("Beam has already been established in Linac and Booster (Aug 26)"); `fermilab-recycler` keeps its NuMI-stacking role label (no new evidence).

New fact worth a follow-up, not applied (no entity in the Atlas for the experiments): April 2026 PAC: "FNAL has decided not to run SY120 before the long 2028-29 shutdown for budget reasons" (SY120 feeds the Fermilab Test Beam Facility and SpinQuest).

## 2. Change log

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
