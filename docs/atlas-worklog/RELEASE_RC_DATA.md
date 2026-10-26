# Release-candidate data fixes (rc-data stream, 2026-10-25)

Branch `atlas-release-rc-data`, from `b49cfb5`. Every change below answers a finding of the independent release-candidate review (ids F1 to F27 are the reviewer's) or one of the two data items added by the coordinator. Validator: `python -m hepgraph.atlas.validate` stayed at 0 errors after every batch. Wording-only rewrites (F8, plus the wording cleaned inside records touched for other findings) are logged in the companion file `docs/atlas-worklog/RELEASE_RC_DATA_F8.md`.

Sourcing rule used throughout: every value changed or added comes from a page fetched on 2026-10-25 (WebFetch, or a plain HTTPS request with a browser user agent where WebFetch is refused), with a verbatim `quote` or a `locator` on the value. inspirehep.net was not used. Where a page refuses scripted requests (www.fnal.gov, ornl.gov news pages, neutrons.ornl.gov, aps.org to the quote checker) the value carries a locator and the note says that the wording is not machine-checked.

## Commits (oldest first)


- `3db1b13` Atlas RC data: DUNE far-detector depth re-sourced to the TDR, ProtoDUNE-SP/DP placements end with operation, Fermilab website is fnal.gov (F9, F14, F16)
- `bab41ff` Atlas RC data: Fermilab context features get sourced valid windows; CDF/D0 hall wording dated (F15, F11)
- `f95017e` Atlas RC data: one CERN-sourced LS3 interval (to mid-2030) and one status rule across LHC experiments; XENONnT intervals say what is known (F10, F25)
- `06fce38` Atlas RC data: JUNO map retitled to what it draws, OPERA 5.1 sigma cited to the paper body (F21, F27)
- `beb29cf` Atlas RC data: dated wording replaces 'sources fetched this session' (COMET, CTAO, CUPID, EDELWEISS, H.E.S.S., nEXO, SENSEI, DEAP-3600, DarkSide-20k, DMRadio, DarkQuest) (F11)
- `ce0eaad` Atlas RC data: the SNS complex outline belongs to a new SNS complex site, not to Neutrino Alley; SNS construction start sourced (1999-12-15), dated 1.8 MW wording; ORNL website is ornl.gov (F1, F11)
- `20f15c8` Atlas RC data: map feature and site names say what is drawn (LHC/LEP point surface sites, CMS cavern position, hall positions) (F5)
- `dccc200` Atlas RC data: remove boilerplate process notes (derived-field, terminal-event, amendment ids, worklog pointers) from 327 records; CMS member rows say plainly why the roster is not public (F8)
- `17220c2` Atlas RC data: plain evidence wording in experiment and collaboration notes (no session, agent, validator or amendment language); stale cross-references removed (F8)
- `650d430` Atlas RC data: plain evidence wording in detector, accelerator and beamline notes; two campus-grade sites recorded as campus points, not detector points (F8)
- `23d2a42` Atlas RC data: site coordinate notes say what the point is and how precise it is (F8)
- `d76f2e8` Atlas RC data: map feature notes, method and summaries in plain words (F8)
- `41e20aa` Atlas RC data: map notes, not-drawn reasons and backlogs, facility and institution notes in plain words (F8)
- `5067bdd` Atlas RC data: coverage rows, results, documents and source notes in plain words; resolved dangling-reference items removed (F8)
- `fe718ae` Atlas RC data: campus outlines are timeless context, not tied to the hosted experiment's lifecycle (McMurdo Williams Field, BNL, ISIS/RAL, MIT, WIPP, SURF administration building); ATLAS institution counts reconciled and dated (175 institutions / 246 institutes / 197 rows)
- `c743bc9` Atlas RC data: second wording sweep (change-log labels, 'Second pass', 'Integrator', 'Currency check', owned-by remarks) and stale statements corrected in map and site notes (F8)
- `9cdd2b5` Atlas RC data: 'sources fetched' / 'fetched this session' wording replaced by 'sources consulted' and dated statements (F11)
- `c74cc4f` Atlas RC data: SLAC, KIT and PSI campus outlines are timeless context; JUNO map summary no longer says baselines are drawn (coordinator item a, F21)


## Summary by finding

| id | what changed | main sources |
| --- | --- | --- |
| F1 | The dashed SNS outline now belongs to a new site `site:ornl-sns-complex` ("Spallation Neutron Source (SNS) accelerator and target complex"); `site:ornl-sns-neutrino-alley` keeps COHERENT's corridor, is listed as not drawn, and says that its point is the complex centroid. `accelerator:sns` and the ORNL facility point at the complex site. | ORNL Q&A on Neutrino Alley; OSM way 907808191; COHERENT paper arXiv:2110.07730 |
| F5 | Geometry names of the LHC/LEP point boundaries say "surface site"; the CMS cavern point says "position (published coordinate, ±30 m)"; hall points say "position (derived point)"; site names that claimed a cavern or hall the map does not draw are neutral (old names kept as aliases). | none needed (naming) |
| F8 | Process language removed from provenance notes, map notes and not-drawn reasons/backlogs, summaries, coverage rows and source notes in about 800 of the 914 data files this stream touched. | see the F8 log |
| F9 | The far-detector depth now leads with the DUNE TDR sentence placing the far detector at the 4850 (foot) level; 1478 m is stated as the conversion of 4850 ft, with the SURF page as a secondary source. | DUNE FD TDR Vol. I section 1.2; SURF news page |
| F10 | One LS3 interval for every LHC experiment and detector: 2026-06-29 to mid-2030 (CERN), Run 4 from mid-2030. | home.cern LS3 page; CERN schedule news of 8 Oct 2024 |
| F11 | "As of the sources fetched this session" replaced by dated wording in COMET, CTAO, CUPID, EDELWEISS, H.E.S.S., nEXO, SENSEI, DEAP-3600, the CDF and D0 halls, SNS (1.8 MW dated 2026-09-17); SNS construction start sourced (15 Dec 1999). | APS News, ORNL, Holtkamp EPAC08 and per-record sources |
| F14 | `facility:fermilab` website is https://www.fnal.gov/. Facility ORNL website is https://www.ornl.gov/. | fnal.gov and ornl.gov home pages |
| F15 | Wilson Hall, MI-62, the Main Injector infield, MC-2, the campus boundary and the ICARUS hall have sourced `valid` windows. | Fermilab history pages, PAC 1999, FermiNews 2003, OSM history |
| F16 | ProtoDUNE-SP placement ends 2020-07 and the detector is `active` 2018-09 to 2020-07, then `completed`; ProtoDUNE-DP likewise. | CERN EP newsletter |
| F21 | `map:juno-reactor-baselines` retitled to what it draws; the baselines are in the summary with the JUNO sources. | arXiv:2511.14593; arXiv:2104.02565 |
| F25 | One status rule for LS3 (`upgrade` only where a fetched source says the experiment's own detector is being upgraded in LS3, else `shutdown`); XENONnT intervals say what is known. | CERN, ALICE, LHCb, ATHEXIS and LIDINE abstracts, Nikhef slides |
| F27 | OPERA's 5.1σ is cited to the paper body (Conclusions, p. 6 of arXiv:1507.01417); the abstract's "larger than 5σ" is stated beside it. | arXiv:1507.01417 |
| coord. (a) | Williams Field outline (and five other campus outlines) no longer follow the hosted experiment's lifecycle: timeless context. | n/a (geometry contract) |
| coord. (b) | ATLAS institution counts reconciled: 175 institutions / 246 institutes (official list, read 2026-10-25), "170+" on the collaboration page, 197 rows recorded. | atlaspo.cern.ch/public/institutions, atlas.cern/Discover/Collaboration |


## F1 (P0): the SNS outline was labelled "SNS Neutrino Alley"

Cause: `geometry:sns-complex-boundary` had `entity_id` and `site_id` `site:ornl-sns-neutrino-alley`, and the map labels a feature with its entity's name. The same site was `accelerator:sns`'s `site_id` and the ORNL facility's `primary_site_id`.

Fix (commit `ce0eaad`):
- New `site:ornl-sns-complex`, name "Spallation Neutron Source (SNS) accelerator and target complex", `setting` surface, coordinate = centroid of OSM way 907808191 (campus kind, approximate, 800 m precision, as before), sources `src:geo-ornl-osm-sns-boundary`, `src:ornl-sns-page`.
- `geometry:sns-complex-boundary` and `geometry:sns-linac-structure`: `entity_id` / `site_id` now `site:ornl-sns-complex`; the outline's name is "SNS accelerator and target complex outline"; its method, notes and summary say it marks the complex only.
- `accelerator:sns` `site_id` and `facility:oak-ridge-national-laboratory` `primary_site_id` now `site:ornl-sns-complex`.
- `site:ornl-sns-neutrino-alley` (COHERENT's site) keeps its name; its coordinate note says that the corridor's own position is not published and that the point is the complex centroid. Sources added: `src:geo-ornl-neutrino-alley-qa` (ORNL: "five detectors sited along a 164-foot, or 50-meter, long hallway that has come to be called Neutrino Alley ... The closest point in Neutrino Alley is about 20 meters from the SNS target.", https://www.ornl.gov/news/welcome-neutrino-alley-qa-ornls-marcel-demarteau, page dated 22 Dec 2020) and `src:cevns-coherent-csi-2022-full-dataset` (COHERENT, arXiv:2110.07730: "Neutrino Alley (NA), a basement hallway where background neutrons from the facility are heavily suppressed").
- `map:oak-ridge-national-laboratory`: `site_ids` has both sites; the not-drawn row for Neutrino Alley now names `site:ornl-sns-neutrino-alley` (it was filed under the facility) and says that the dashed outline is the complex, not the alley.
- The review's description "a basement corridor in the target building" is not claimed: no source consulted says which building houses the alley (the map's backlog asks for one).
- The validator now reports one more warning (`sites-too-close`: the two SNS sites share a point until the alley is located). `docs/atlas-worklog/ID_REGISTRY.md` has a row for the new id.

## F5 (P1): feature names

The map labels a feature with `entity_name || name` (`static/atlas/js/localmap.js` lines 641, 1196, 1586; `mapstyle.js` 364), so the geometry `name` alone does not change the label. Both were changed (commit `20f15c8`):
- Geometry names: `point1-atlas-boundary` "LHC Point 1 surface site (ATLAS)", the same form for Points 2, 5, 8 and the LEP points 2, 4, 8; `point5-cms-cavern` "CMS cavern position (published coordinate, ±30 m)"; the Daya Bay, RENO, SURF Davis Campus and Soudan point features end in "position (derived point)" / "(published coordinate ...)" instead of naming the hall as if it were the shape.
- Site names (old name kept as an alias): LHC Point 1 (ATLAS), Point 2 (ALICE), Point 5 (CMS), Cessy, Point 8 (LHCb); LEP Points 2, 4, 8; ECN3, CERN North Area; SPS Long Straight Sections 4 and 5; Boulby Mine (site of the underground laboratory); South Pole (IceCube site).
- Not changed because the shape is what the name says: CERN's other point features, the LNGS hall points ("undifferentiated position" is in their geometry names; their entity names are the halls themselves).
- For the integrator: if the map should show the shape's own name, that is a one-line change in `static/` (prefer `feature.name`, or show both).

Exact old -> new strings: appendix F.

## F8 (P1): process language in notes

Scope scanned: every string in `data/atlas` outside quotes, titles, ids and urls. Rules, counts and every old -> new pair are in `RELEASE_RC_DATA_F8.md`. In short: a deterministic pass removed 634 boilerplate strings (derived-field notes, terminal-event notes, amendment ids, worklog pointers, "flagged for review", CMS member-row wording); 12 rewrite groups handled the remaining ~2,000 strings by hand with an apply tool that checks the old text and refuses process wording; two further groups handled change-log labels. Stale cross-references ("owned by the facilities lead", "dangling until that lead lands") were deleted after checking that the referenced record exists (it does in almost every case); where a record really is absent the note says "does not exist in the Atlas yet". `site:cern-neutrino-platform-ehn1` and `site:fermilab-main-campus` carried `kind: detector` on 2-3 km campus points only to satisfy a rule; they are now `campus` points (shown as approximate), the honest form.

An invariants check confirmed that, across 663 changed files in the wording sweep, only text fields changed (notes, `note`, method, reason, backlog, technical/plain summaries, excerpt text, `missing_fields` items, link-check messages) and 0 non-string differences.

## F9 (P1): DUNE far-detector depth

`experiment:dune` `/key_specs/4/quantity`: old quote "The entire experiment will be located at the 4850 Level (1478 m) Davis Campus at the Sanford Lab Underground Research Facility (SURF)." (SURF news page about the MAJORANA Demonstrator). New lead quote, DUNE FD TDR Vol. I, section 1.2, arXiv PDF p. 25: "Figure 1.4 shows the cavern layout for the FD in the SURF underground area, also referred to as the 4850 (foot) level or 4850L." (https://arxiv.org/pdf/2002.02967, `src:dune-fd-tdr-vol-1`). 1478 m stays as the conversion 4850 ft × 0.3048 = 1478.3 m; the note says so, quotes the TDR glossary ("4850L The depth in feet (1480 m) of the top of the cryostats underground at SURF"), the ProtoDUNE-SP paper ("a far detector located at the 4850 ft level of Sanford Underground Research Facility (SURF)") and the SURF page only for the metre figure. Details and old/new text: appendix A.

Not changed (other files cite the MAJORANA page for a DUNE value): `sites/surf-4850-level-dune-far-detector.json` depth, `facilities/surf.json` depth, `maps/surf.json` item "4850 Level (1478 m)". The only SURF page giving 1478 m is the MAJORANA page; DUNE itself rounds to 1480 m.

## F10 and F25 part 1 (P1/P2): LS3 and status

Source (re-fetched 2026-10-25): https://home.cern/science/long-shutdown-3/: "The cryogenics team has been running the warm-up sequence since LS3 began on 29 June 2026." and "... stored ready to be used again once the accelerator resumes operation in mid-2030."; https://home.cern/new-schedule-cerns-accelerators/ (8 Oct 2024): "The start-up of the HL-LHC (Run 4) is now planned for June 2030."; https://home.cern/cern-bids-farewell-to-the-lhc-and-enters-long-shutdown-3/ (29 June 2026).

Old -> new for the LS3 interval of every experiment and detector: ATLAS 2026-06 → 2029 (planned) became 2026-06-29 → mid-2030; ATLAS Run 4 start 2029 became mid-2030 (planned); CMS 2026-06 → 2030 became 2026-06-29 → mid-2030 (confidence approximate); ALICE 2026-06 → 2029, status `shutdown` became `upgrade`, ending mid-2030; LHCb open-ended `shutdown` became `upgrade`, ending mid-2030; LHCf, TOTEM, FASER, SND@LHC, MoEDAL open-ended became `shutdown` ending mid-2030 (confidence `derived`). Encoding copied from `accelerator:lhc` (start day precision, end `{approx, date 2030, display "mid-2030", planned}`).

Status rule: `upgrade` only where a fetched source says that the experiment's own detector is being or will be upgraded in LS3: ATLAS and CMS (CERN farewell article: "In the LHC caverns, the ATLAS and CMS experiments will undergo extensive upgrades, effectively becoming renewed detectors."), ALICE (home.cern 25 Apr 2024: "Two detector upgrades of ALICE ... have recently been approved for installation during the next long shutdown of the LHC"; arXiv:2601.07405: "During the LHC Long Shutdown 3 (2026-29) ALICE will replace its three innermost tracking layers by a new detector, the “ITS3”."), LHCb (lhcb-outreach 8 May 2024: "The LHCb experiment will upgrade the inner part of the Electromagnetic Calorimeter and the electronics of the Ring Imaging Cherenkov detectors in the next LHC Long Shutdown (LS3)."; JINST 21 C03018). Otherwise `shutdown`: LHCf, TOTEM, FASER (arXiv:2503.19775: upgrade planned "by the start of the LHC Run 4", not tied to LS3), SND@LHC, MoEDAL (arXiv:2209.03988: MAPP-2 "planned for installation during the long shutdown (LS3)", a 2022 plan not confirmed in 2026). The top-level `status`, the intervals and the detector records agree. Appendix C has every field.

Left as is: the ATLAS feature article of 18 Jan 2023 ("currently planned for 2029") is superseded by CERN's October 2024 schedule and the note says so; `experiment:mathusla` (not in scope) still says "~2029".

## F25 part 2: XENONnT

Intervals now read: construction/upgrade (2018-12 to 2020); commissioning (2020 to 2021-07-06); science operations (2021-07-06 to the summer-2025 upgrade; confidence approximate, the last science data may predate the upgrade); detector upgrade (2025-07, earliest 2025-06, latest 2025-08, display "summer 2025", to 2026-03, earliest 2026-01, latest 2026-06, display "first half of 2026"); "Recommissioning after the 2025 upgrade (2026)" (status `commissioning`, from the same bounded date, open). Sources re-read: ATHEXIS abstract (June 2026) "Following upgrade operations conducted in 2025, the experiment began its new commissioning phase in 2026."; LIDINE abstract (talk 7 Oct 2026) "an overview of the XENONnT detector upgrade carried out in summer 2025 and present the status and first results of the subsequent commissioning campaign"; Nikhef slides (May 2026) "Commissioning until July, then start of data taking", "Upgrade completed". The summaries no longer say "has been running since 2020". Note for the integrator: the bounded start makes the present month derive `commissioning` with certainty `certain` (it was `possible`); restore a year-precision start to get hatching back. `detector:xenonnt` gained the 2020-2021 commissioning interval it lacked.

## F11 (P1): process wording in panels, SNS

- Dated wording replaced "as of the sources fetched this session" in COMET, CTAO, CUPID, EDELWEISS, H.E.S.S., nEXO, SENSEI, DEAP-3600, DarkSide-20k, DMRadio, DarkQuest (about 130 strings; appendix E). "As of 2026-10-25" is used only where the page was re-read that day, otherwise the source's own date or "No source consulted (checked <date>)".
- Where the old text contradicted the cited source the record was corrected, with the source: DEAP-3600 shielding (arXiv:1712.01982 section 1.1: "The outer steel shell is immersed in a 7.8-m-diameter shield tank filled with ultra-pure water and instrumented with 48 Hamamatsu R1408 PMTs serving as a muon veto."), EDELWEISS operating temperature (arXiv:2211.04176: "The TES is operated around 44 mK"), SENSEI at SNOLAB (arXiv:2312.13342: six Skipper-CCDs installed at SNOLAB in 2021; the ~100 g detector planned in 2020 is still not reported), DEAP-3600 summaries (21 Sept 2026 LRT2026 abstract, "newly initiated third fill run").
- CDF and D0 halls: `geometry:fermilab-cdf-hall`, `fermilab-d0-hall` and their sites no longer say "this session" or "shown at campus precision (~3 km)"; the marker is the building centroid (about 40 m).
- SNS (`accelerator:sns`, commit `ce0eaad`): "1.8 MW as of this session" became "1.8 MW on the official SNS page of 2026-09-17"; the interval "Construction (?-2006-04)" became "construction", start 1999-12-15 (display "15 December 1999 (ORNL: late 1999)"), end 2006-05. Sources: ORNL news 6 May 2005 (https://www.ornl.gov/news/spallation-neutron-source-knightjacobs-mark-successful-partnership/) "Construction on the state-of-the-art neutron facility began in late 1999."; APS News 1 May 2000 (https://www.aps.org/apsnews/2000/05/spallation-neutron-source-features-superconducting-linac) "Construction of the Spallation Neutron Source (SNS) facility began on December 15, 1999, with groundbreaking at the Oak Ridge, Tennessee site." (the checker cannot fetch aps.org, the quote is in the locator); N. Holtkamp, EPAC08 THPPGM03 (https://proceedings.jacow.org/e08/papers/thppgm03.pdf) "officially authorized for construction in FY1999 and finished at the end of May 2006". The end moved from 2006-04 (Wikipedia: "completed in April 2006") to 2006-05, the project's own finish; first beam on target was 28 April 2006 (ORNL news 1 May 2006), now a `commissioning` row (2006-04-28 to 2007-08) so the timeline has no gap.

## F14 (P1): lab websites

`facility:fermilab` `links.website`: https://lbnf-dune.fnal.gov/ → https://www.fnal.gov/ (`src:rc-fermilab-official-site`; page title "Fermilab | Home", headline "Fermilab is America's particle physics and accelerator laboratory"; the site returns HTTP 403 to scripts, so the value has a locator, no quote). Beyond the finding: `facility:oak-ridge-national-laboratory` website https://neutrons.ornl.gov/sns → https://www.ornl.gov/ (`src:rc-ornl-official-site`, title "Oak Ridge National Lab", "Oak Ridge National Laboratory delivers scientific discoveries and technical breakthroughs"). Other facilities whose website is a project site (KIT → KATRIN, Whipple → VERITAS, H.E.S.S., JUNO, LHAASO, McMurdo LDB → a payloads page) were left and are listed in appendix A.

## F15 (P2): Fermilab context features

`valid.start` added (with `sources`, `confidence`, `quote`/`locator`, `note` inside `valid`; the build and validator read only `start`/`end`): Wilson Hall 1973 (approximate; Fermilab History "A Brief History of Fermilab": "He guided the design of the distinctive high-rise Wilson Hall, which houses most of the lab’s offices and was completed in 1973."; the lab was dedicated 11 May 1974 and construction ran 1971-1974); MI-62 service building 1997 (derived; PAC 1999 MOCL3: "Completion of the Main Injector ring civil construction occurred in 1997"; the Aug 1994 TDR still describes MI-62 in the future tense); Main Injector infield grassland 1997 (derived; FermiNews Sept 2003 p. 5: "In 1997, the mitigated area was well on its way, and the Corps agreed that the wetlands were good enough to close the permit."); MC-2 building 2019-08 (uncertain: first appearance in OpenStreetMap, an upper bound; DOE CX-010394 of 12 June 2012 names MC-1 but not MC-2); campus boundary 1966-12-07 (approximate; "The AEC chose a 6,800 acre site at Weston, Illinois, on December 7, 1966."); and, beyond the finding, the ICARUS hall 2017-07 (Fermilab News 2017-07-25: "... until it is installed inside the new ICARUS building."), which had inherited ICARUS-T600's 2010 Gran Sasso start. Audit of all 34 Fermilab features: 29 inherit their entity's lifecycle, 5 are context features (all dated above), the CDF, D0, MiniBooNE and MINOS halls already had windows. Choices that are one string to flip are listed in appendix B.

## F16 (P2): ProtoDUNE-SP

Placement: start 2018, `end` null → end 2020-07; quote "ProtoDUNE-SP (NP04), the single-phase Horizontal Drift DUNE Far Detector prototype at the CERN Neutrino Platform, successfully operated from August 2018 to July 2020 in the CERN EHN1 experimental area" (CERN EP newsletter, https://ep-news-wp.web.cern.ch/dune-prototype-activities-neutrino-platform/, undated, tagged March-May 2022). Detector intervals: old one interval `completed` from 2018-09 → `active` 2018-08/09 to 2020-07, then `completed` from 2020-07 ("the NP04 cryostat was emptied from 22 July 2020 until 24 October 2020 marking the completion of ProtoDUNE-SP Phase I"). `specs.total_mass` null → 750 t (approximate; "With its ~750 tonnes of LAr, ProtoDUNE is the largest LArTPC ever operated."). `detector:protodune-dp` got the same treatment from "NP02 ... hosted a prototype of dual phase (liquid-vapor) argon TPC (ProtoDUNE-DP) in 2019-2020." (year precision; revert that file only if the extension is unwanted). Panel check: SP 2019 active, 2020-09 and 2026 absent (completed).

## F21 (P2): JUNO map title

`map:juno-reactor-baselines` `name`: "JUNO — Yangjiang and Taishan reactor complexes at the 52-53 km baseline" → "JUNO — experimental hall and the Yangjiang and Taishan reactor buildings" (id unchanged). `summary.plain`/`technical`: baselines stated with sources (arXiv:2511.14593: "is a 20 kton liquid-scintillator detector located 52.5 km from multiple reactor cores", "at an optimized distance of 52.5 km, equidistant from all reactor cores of the Yangjiang and Taishan Nuclear Power Plants (NPP)"; arXiv:2104.02565 section 1.2 and Table 1: "the experimental site is at equal distances of ∼53 km from the Yangjiang NPP and the Taishan NPP"; surveyed core distances 52.11 to 52.82 km, "surveyed with a Global Positioning System (GPS) to a precision of 1 meter"), and "No baseline lines or distance labels are drawn." Hall record renamed "... (published coordinate, reactor-buildings map)". `maps/juno-jiangmen.json` summary said "the 52-53 km baselines are on map:juno-reactor-baselines" as if drawn; it now says the reactor buildings, 52-53 km from the hall, are on that map.

## F27 (P2): OPERA significance

`result:opera-tau-neutrino-appearance-discovery-2015` `significance`: still 5.1σ, now cited to the paper body: Conclusions, p. 6 of arXiv:1507.01417 (https://arxiv.org/pdf/1507.01417): "Given the low background level and the observed number of ντ candidate events, we report the discovery of a ντ appearance in the CNGS neutrino beam with a significance of 5.1 σ."; Results, p. 6: "a (one-side) significance of 5.1 standard deviations is obtained, corresponding to a background fluctuation probability of 1.1 × 10−7". The abstract's own wording, "a significance larger than 5 σ", is stated in the note, the `key_value_text` locator and both summaries. Source: `src:rf08-opera-discovery-2015-arxiv-pdf`.

## Coordinator item (a): Williams Field outline (map:mcmurdo-ldb) and similar

Cause: `geometry:mcmurdo-williams-field-aerodrome` was tied to `site:mcmurdo-ldb-launch-site`, whose lifecycle is derived from ANITA's flights (active only in flight windows, `completed` from 2017-01), so the outline was not drawn in 2026. The outline depicts the aerodrome (OSM way 821080729), not the balloon facility and not ANITA.
Fix (commit `fe718ae`): `entity_id` → null (a context boundary, timeless by the geometry contract), `site_id` kept so the site stays accounted for; a plain note says why. The facility's own interval (active from 2003-12, from ANITA-LITE's launch) was not used: the facility is in the map's not-drawn list (its camp is not mapped), so tying the outline to it would be an error, and the facility interval starts too late for a 1950s airfield.
The same defect was found in eight more campus outlines whose site lifecycle either ended with the last hosted experiment (so the campus vanished from the present-day map) or began only with the first hosted experiment (so the campus appeared late): `bnl-upton-campus-boundary`, `isis-ral-campus-boundary`, `mit-campus-boundary`, `wipp-boundary`, `surf-administration-building` (not drawn in 2026), and `slac-property-boundary` (drawn only from 2022-01, status "construction"), `kit-campus-north-boundary` (from 2019-01), `psi-campus-boundary` (from 1998-05). Same fix and note (commit `fe718ae` for the first six, a later commit for SLAC, KIT and PSI). Built into a temporary directory to confirm: all of them have `state_segments: null` (always drawn). Not changed: the LHC and LEP point boundaries (they depict an experiment's own site, so the experiment's lifecycle is correct), and the Argonne, DESY and Jefferson Lab campus outlines, which already have no lifecycle (timeless). The `maps/juno-jiangmen.json` summary sentence about "the 52-53 km baselines" was reworded to "the Yangjiang and Taishan reactor buildings, 52-53 km from the hall, are on map:juno-reactor-baselines".

## Coordinator item (b): ATLAS institution counts

Facts (read 2026-10-25): https://atlas.cern/Discover/Collaboration: "170+" Institutions, "40" Countries, "over 5500 members and 3000 scientific authors". https://atlaspo.cern.ch/public/institutions (official list; no date but its footer): "Number of countries with ATLAS institutions: 40", "Total number of institutions: 175", Regular institutions 154, Cluster institutions 21, Institutes in clusters 76, Associate institutes 16, "Total number of institutes: 246", Technical Associate institutes 19, Tier-1 centres 10. The Atlas's `memberships/atlas.json` has 197 rows, all `official_institution_list`, recorded from the same list on 2026-09-17; 194 of the 197 quotes are found exactly on the page read today, 3 are not (Istinye University; TU Dresden Institute für Kern- und Teilchenphysik; Universität Innsbruck).
Diagnosis: nothing was wrong, the figures count different things. 170+ is the rounded headline; 175 is the list's institutions (154 regular plus 21 clusters); 246 is institutes (154, the 76 inside clusters, 16 associates); the 197 rows are institutes, a subset of the 246 (not all were recorded), and 19 technical associates and 10 Tier-1 centres are in neither total.
Fix (commit `fe718ae`): `collaboration:atlas` `membership.institution_count` 170 (approximate, "170+ Institutions") → 175 (verified, `src:atlas-institutions`, quote "Total number of institutions: 175", display "175 institutions (246 institutes counting cluster members and associates)"), with a note stating all of the above; `country_count` and `member_count` re-read (same values, `verified_at` 2026-10-25); the record's `notes` rewritten to say which figure is which; `memberships/atlas.json` `roster_snapshots[0].note` says that the 197 rows are institutes copied on 2026-09-17, a subset of the list's 246. The panel's "Partial roster: 197 confirmed institutions ... the full membership is larger" is now true of institutes (246) and no longer contradicts the key fact.

## Checks

## Checks

- Validator: `python -m hepgraph.atlas.validate` reports 0 errors and 1,596 warnings; the baseline before this stream was 1,594. The net +2 is: +1 `sites-too-close` (the two SNS sites share the complex centroid until the alley is located), +2 `coordinate-kind-approximate` (`site:cern-neutrino-platform-ehn1` and `site:fermilab-main-campus`, now honestly campus points), -1 "start unknown" (the SNS construction start is now sourced).
- Existing atlas tests (`tests/test_atlas_build.py`, `_geometry_data`, `_history`, `_pilot_acceptance`, `_validate`, `_validation_counts`, `_schema`, `_geo`): 314 passed, 1 skipped.
- Quote check (`scripts/atlas_quote_check.py`, same cache as the baseline, new URLs fetched online): baseline before this stream verbatim 3674, segments 307, skipped 195, unfetchable 6, near 3, missing 1; after: verbatim 3682, segments 319, skipped 195, unfetchable 6, near 3, missing 1. The sets of near, missing and unfetchable quotes are identical to the baseline (no new ones). The 29 number flags are unchanged.
- Wording sweep invariants: across 663 changed files in the sweep, 0 non-string differences from the previous commit (only text fields changed).
- `static/atlas/generated` was never rebuilt or committed (temporary builds went to the scratch directory).


## What remains (for the integrator)

- Generated bundles (`static/atlas/generated/*`) were not rebuilt or committed: they still carry the old titles, names, notes and the old `state_segments` (e.g. McMurdo Williams Field, the SNS outline label, JUNO map title). Rebuild after merging.
- Map labels use `entity_name || name` (F5): if the label should say what the shape is, that is a `static/` change.
- One more validator warning than before F1 (`sites-too-close`, the two SNS sites share a point) and two more from F8 (A23 `coordinate-kind-approximate` for `site:cern-neutrino-platform-ehn1` and `site:fermilab-main-campus`, now honestly campus points); no errors.
- Not fixed, outside the findings: other records citing the MAJORANA page for a DUNE value (`sites/surf-4850-level-dune-far-detector.json`, `facilities/surf.json`, `maps/surf.json`); `experiment:moedal` (open-ended approved/MAPP intervals make it derive `upgrade` for 2022-2026 while `detector:moedal` derives `active`); `experiment:mathusla` "~2029"; CUPID's status stays `proposed` although arXiv:2503.02894 (11 July 2025) says "CUPID construction activities have already started" (no construction start date, the site still uses the future tense), a decision for the integrator; H.E.S.S. II (CT5) commissioning date unrecorded (Max Planck Society article of 4 Oct 2012 says "saw its first light on 26 July", not used); `src:atlas-high-luminosity-feature` `date` is 2022 but the byline says 18 Jan 2023; `src:currency2-*` and a number of source records re-read on 2026-10-25 whose `accessed` was not bumped (list in appendix E); the `rank` value on new source files was left out because the validator says it is derived.
- The ATLAS roster rows (197) are a subset of the list's 246 institutes; completing them needs institution records for the missing ones. Three rows no longer match the list exactly.
- Open data questions found during the wording sweep are listed in `RELEASE_RC_DATA_F8.md`.

## Appendix F: old -> new for the lead's own edits (generated from git)

### F1 and SNS cluster (commit ce0eaad)

**data/atlas/accelerators/sns.json**
- `/intervals`: [{"confidence": "uncertain", "end": {"date": "2006-04", "note": "Month precision ('April 2006') from Wikipedia only; no official page fetched in this session confirms this date."}, "label": "construction completed", "note": "Sourced to Wikipedia only; flagged for review.", "quote": "completed in April 2006", "sources": ["src:sns-wikipedia"], "start": null, "status": "construction", "verified_at": "2026-09-17"}, {"confidence": "verified", "end": "2024-07-11", "label": "Proton Power Upgrade (1.4 → 2.8 MW)", "locator": "LINAC2024 THPB045 abstract/introduction: start = outage start; end = 'Neutron production for the user program resumed July 11th as planned at 1.3 GeV and 1.7 MW' (beam commissioning June 7 - early July 2024)", "note": "DATED 2026-10-25 (previously start/end null, status upgrade, open): this interval is the long installation outage of the Proton Power Upgrade project (August 2023 to April 2024), through beam commissioning (from 7 June 2024), to the resumption of user neutron production on 11 July 2024. The project itself is reported complete: ORNL, 18 May 2026, \"The completed proton power upgrade ensures SNS will remain the world's most powerful proton accelerator\"; t … → [{"confidence": "verified", "end": "2006-05", "label": "construction", "locator": "Start: ORNL news, 6 May 2005 (quoted); the day is from APS News, 1 May 2000: \"Construction of the Spallation Neutron Source (SNS) facility began on December 15, 1999, with groundbreaking at the Oak Ridge, Tennessee site.\" End: N. Holtkamp, EPAC08 THPPGM03, section \"What is SNS?\": \"finished at the end of May 2006\".", "note": "Construction began in late 1999 (ORNL), with groundbreaking on 15 December 1999 (APS News). The project was finished at the end of May 2006 according to N. Holtkamp (EPAC08); Wikipedia instead says \"completed in April 2006\", and the later, better-sourced date is used here.", "quote": "Construction on the state-of-the-art neutron facility began in late 1999.", "sources": ["src:rc-aps-news-2000-sns-construction", "src:rc-ornl-news-2005-sns-partnership", "src:rc-holtkamp-epac08-sns"], "start": {"date": "1999-12-15", "display": "15 December 1999 (ORNL: late 1999)"}, "status": "construction", "verified_at": "2026-10-25"}, {"confidence": "approximate", "end": "2007-08", "label": "commissioning (first beam on target, 28 April 2006)", "locator": "ORNL news, 1 May 2006 (\"First ne …
- `/notes/0`: kind is recorded as `linac`; the SNS accelerator complex also includes an accumulator ring (not separately modeled here). → kind is recorded as `linac`; the SNS accelerator complex also includes an accumulator ring, which this record does not model separately.
- `/site_id`: site:ornl-sns-neutrino-alley → site:ornl-sns-complex
- `/sources`: ["src:ornl-sns-page", "src:sns-wikipedia"] → ["src:ornl-sns-page", "src:sns-wikipedia", "src:rc-aps-news-2000-sns-construction", "src:rc-ornl-news-2005-sns-partnership", "src:rc-holtkamp-epac08-sns", "src:rc-ornl-news-2006-first-neutrons"]
- `/specs/beam_energy/note`: Sourced to Wikipedia only; no official page fetched in this session states the proton beam energy directly in GeV. → Sourced to Wikipedia only; no official page consulted (checked 2026-09-17) states the proton beam energy directly in GeV.
- `/specs/beam_power/display`: 1.4 MW (original design); upgraded to 2.8 MW; 1.8 MW as of this session → 1.4 MW (original design); upgraded to 2.8 MW; 1.8 MW on the official SNS page of 2026-09-17
- `/specs/beam_power/note`: The official SNS page states current operation 'Beam is on target at 1.8 MW' and that 'The Proton Power Upgrade project doubled the power capability of the SNS linear accelerator, from 1.4 to 2.8 megawatts.' The 1.4 MW value (original design/baseline) is recorded as the primary spec value; see note for the upgrade figures. → The official SNS page (read 2026-09-17) states current operation 'Beam is on target at 1.8 MW' and that 'The Proton Power Upgrade project doubled the power capability of the SNS linear accelerator, from 1.4 to 2.8 megawatts.' The 1.4 MW design value is recorded as the primary spec value; the upgrade figures are in this note and the display.
- `/summary/technical`: Spallation Neutron Source: a ~1 GeV proton linac and accumulator ring at ORNL delivering pulsed spallation neutrons from a liquid-mercury target; completed April 2006, first instruments commissioned August 2007; beam power upgraded from 1.4 MW design to 2.8 MW (Proton Power Upgrade), operating at 1.8 MW as of this session. → Spallation Neutron Source: a ~1 GeV proton linac and accumulator ring at ORNL delivering pulsed spallation neutrons from a liquid-mercury target; construction began in late 1999 and the project finished in May 2006, first instruments were commissioned in August 2007; beam power upgraded from the 1.4 MW design to 2.8 MW capability (Proton Power Upgrade), with the official SNS page of 2026-09-17 reporting 1.8 MW on target.

**data/atlas/facilities/oak-ridge-national-laboratory.json**
- `/links/website/locator`: <absent> → ORNL home page, title "Oak Ridge National Lab", heading "Science Solutions for the World"
- `/links/website/note`:  → The previous link, neutrons.ornl.gov/sns, is the page of the neutron user facility, not of the laboratory. The home page was read on 2026-10-25 with an automated fetch (its server refuses scripted requests, so no verbatim quote is checked); its title is "Oak Ridge National Lab" and its heading says "Oak Ridge National Laboratory delivers scientific discoveries and technical breakthroughs".
- `/links/website/sources/0`: src:ornl-sns-page → src:rc-ornl-official-site
- `/links/website/value`: https://neutrons.ornl.gov/sns → https://www.ornl.gov/
- `/links/website/verified_at`: 2026-09-17 → 2026-10-25
- `/notes/0`: kind is recorded as `research_laboratory` (no better single-value fit in FACILITY_KINDS for a large multiprogram DOE laboratory); the SNS accelerator itself is separately recorded as accelerator:sns. → kind is recorded as `research_laboratory` (the facility kinds have no better fit for a large multiprogram DOE laboratory); the SNS accelerator itself is a separate record, accelerator:sns.
- `/notes/1`: primary_site_id points at site:ornl-sns-neutrino-alley because that is the only site this wave creates for ORNL (per the ID registry); it is not meant to imply that hall is ORNL's literal main entrance. → The facility's marker is the Spallation Neutron Source complex (site:ornl-sns-complex), the only ORNL site in the Atlas; it is not ORNL's main entrance, and the laboratory's other campuses are not mapped.
- `/primary_site_id`: site:ornl-sns-neutrino-alley → site:ornl-sns-complex
- `/sources`: ["src:ornl-sns-page", "src:ornl-wikipedia", "src:rf13-ornl-overview"] → ["src:ornl-sns-page", "src:ornl-wikipedia", "src:rf13-ornl-overview", "src:rc-ornl-official-site"]

**data/atlas/geometry/sns-complex-boundary.json**
- `/entity_id`: site:ornl-sns-neutrino-alley → site:ornl-sns-complex
- `/geometry/note`: OpenStreetMap alone (source type openstreetmap, rank 11) yields at most `approximate` confidence; this is a whole-complex property boundary, not a claim about Neutrino Alley's own position within it. → OpenStreetMap alone (source type openstreetmap, rank 11) yields at most `approximate` confidence; this is the property outline of the whole SNS complex, not a claim about the position of any structure inside it.
- `/method`: OpenStreetMap way 907808191, named 'ORNL Spallation Neutron Source' (amenity=research_institute), fetched via the Nominatim /lookup endpoint with polygon_geojson=1 (Overpass itself refused every connection attempt for most of this session; see the worklog's method note). Nodes kept verbatim, no simplification. This is the outer boundary of the whole SNS linac/ring/target complex, not a trace of Neutrino Alley itself: Neutrino Alley is a basement corridor inside the target building, somewhere within this ~0.7 x 1.4 km footprint, and no more specific public source or OSM element for it was found this session. Used here, honestly widened in `accuracy_m`, as the best available anchor for the detector-hosting site. → OpenStreetMap way 907808191, named 'ORNL Spallation Neutron Source' (amenity=research_institute), fetched on 2026-09-18 through the Nominatim /lookup endpoint with polygon_geojson=1. Nodes kept verbatim, no simplification. The outline is the outer boundary of the whole SNS linac, ring and target complex (about 0.7 x 1.4 km). It does not locate any structure inside the complex, including the basement hallway 'Neutrino Alley'; `accuracy_m` is honestly widened to say so.
- `/name`: SNS accelerator/target complex boundary → SNS accelerator and target complex outline
- `/notes/0`: Neutrino Alley itself is officially described as a '164-foot, or 50-meter, long hallway' in the basement of the SNS target building, with its closest point 'about 20 meters from the SNS target' (src:geo-ornl-neutrino-alley-qa), but no coordinate, OSM element or published site plan locating this corridor within the complex was found this session; see the worklog backlog. → The outline stands for the whole SNS complex. Neutrino Alley, the hallway where COHERENT's detectors stand, is officially described as 164 feet (50 m) long with its closest point 'about 20 meters from the SNS target' (src:geo-ornl-neutrino-alley-qa), but no coordinate, OpenStreetMap element or published plan locates it inside the complex, so it is listed as not drawn.
- `/site_id`: site:ornl-sns-neutrino-alley → site:ornl-sns-complex
- `/summary/plain`: The outer property boundary of the whole SNS accelerator, accumulator-ring and target complex at Oak Ridge, used as the best available public anchor for Neutrino Alley, which lies somewhere in the target building's basement inside this footprint. → The outer boundary of the whole Spallation Neutron Source complex at Oak Ridge (linac, accumulator ring and target), as mapped in OpenStreetMap. It marks the complex only; it is not the position of any building or hall inside it.

**data/atlas/geometry/sns-linac-structure.json**
- `/site_id`: site:ornl-sns-neutrino-alley → site:ornl-sns-complex

**data/atlas/maps/oak-ridge-national-laboratory.json**
- `/levels/0/note`: Plan view of the SNS complex boundary, the linac structure, the Instrument Hall (building 8700) and the complex's other buildings. → Plan view of the SNS complex outline, the linac structure, the Instrument Hall (building 8700) and the complex's other buildings.
- `/levels/1/note`: Named for reference only: no feature is drawn on this level this session. Neutrino Alley is a basement hallway under the SNS target building (src:geo-ornl-neutrino-alley-qa), but no source fetched this session gives its depth below grade. → Named for reference only: nothing is drawn on this level. The COHERENT collaboration calls Neutrino Alley a basement hallway (src:cevns-coherent-csi-2022-full-dataset), but no source consulted gives its depth below grade or its position.
- `/notes/0`: Release pass 2 (2026-10-25): the linac structure and the Instrument Hall were placed by georeferencing ORNL's own interactive map ('Chestnut Ridge', labelled building polygons without coordinates) onto OpenStreetMap footprints; both are approximate and the method, its residuals and its limits are in the records and in docs/atlas-worklog/RELEASE_GEOMETRY_accel2.md. → The linac structure and the Instrument Hall were placed by georeferencing ORNL's own interactive map ('Chestnut Ridge', labelled building polygons without coordinates) onto OpenStreetMap footprints; both are approximate, and each record states the method, its residuals and its limits.
- `/notes/1`: COHERENT's four operating sub-detectors (CENNS-10, CsI, Ge, NaI) all sit in Neutrino Alley, officially 'about 20 meters from the SNS target' at its closest point and 50 m long overall (src:geo-ornl-neutrino-alley-qa); none is drawn individually, since no source gives any one detector's position along the alley or a coordinate/heading for the alley itself, only its overall length and closest-approach distance. → The dashed outline is the whole SNS complex (the site 'Spallation Neutron Source (SNS) accelerator and target complex'). It is not Neutrino Alley. COHERENT's four operating sub-detectors (CENNS-10, CsI, Ge, NaI) all sit in Neutrino Alley, officially 'about 20 meters from the SNS target' at its closest point and 50 m long overall (src:geo-ornl-neutrino-alley-qa); none is drawn, since no source gives the alley's coordinates or heading, or any detector's position along it.
- `/site_ids`: ["site:ornl-sns-neutrino-alley"] → ["site:ornl-sns-complex", "site:ornl-sns-neutrino-alley"]
- `/unlocated/1/backlog`: A COHERENT or SNS paper with a plan view of the target building basement and the alley (a scaled drawing or measured offsets from the target to each detector), or a basement drawing from ORNL; then place it from the 8700 footprint. → A COHERENT or SNS paper with a plan view of the target-building basement and the alley (a scaled drawing, or measured offsets from the target to each detector), or a basement drawing from ORNL; then place the alley from the 8700 footprint.
- `/unlocated/1/entity_id`: facility:oak-ridge-national-laboratory → site:ornl-sns-neutrino-alley
- `/unlocated/1/reason`: Neutrino Alley (the COHERENT detector corridor) and the target position. ORNL says the corridor is 50 m long and 'about 20 meters from the SNS target' at its closest point, and ORNL's map says the Instrument Hall (8700) 'contains the SNS back-end system including the heavy-metal target'; but no fetched source gives the target's position inside the 8700 footprint, the alley's bearing, or which building lies above it. The site is accounted for on the map by the complex boundary (drawn); the corridor and the COHERENT detectors are not drawn. → Neutrino Alley (the COHERENT detector corridor) and the target position. ORNL says the corridor is a 50 m hallway whose closest point is 'about 20 meters from the SNS target', and ORNL's map says the Instrument Hall (8700) 'contains the SNS back-end system including the heavy-metal target'; but no source consulted gives the target's position inside the 8700 footprint, the alley's bearing, or which building lies above it. The dashed outline on this map is the whole SNS complex, not the alley, so the corridor and the COHERENT detectors are not drawn.

**data/atlas/sites/ornl-sns-complex.json**
- `(new file)`:  → created

**data/atlas/sites/ornl-sns-neutrino-alley.json**
- `/coordinates/locator`: Centroid of OSM way 907808191 "ORNL Spallation Neutron Source" complex boundary → Centroid of OSM way 907808191 "ORNL Spallation Neutron Source" complex boundary (stands in for the corridor, whose position is unpublished)
- `/coordinates/note`: Correction: the previous ORNL-wide ROR point is 7 km from the SNS complex; this is the complex boundary centroid, not the Neutrino Alley basement itself. Previous record: campus point 36.01036, -84.26964 at 2000 m precision, sources ['src:facilities-verify-ornl-ror', 'src:ornl-wikipedia']; moved 3484 m (integrator, 2026-09-21, per docs/atlas-worklog/GEOMETRY_*.md). → The position of Neutrino Alley itself is not published. This point is the centroid of the outline of the whole SNS complex (OpenStreetMap way 907808191), so it says only that the corridor is somewhere inside the complex (800 m precision). ORNL describes the corridor as a 164-foot (50 m) hallway whose closest point is about 20 m from the SNS target; the COHERENT collaboration calls it a basement hallway. An earlier version of this record used the ORNL-wide ROR point, 7 km away; the outline centroid replaced it on 2026-09-21.
- `/notes/0`: setting is recorded as `underground` (a shielded sub-grade hallway per the COHERENT literature generally), though no official page fetched in this session confirms 'underground' specifically as opposed to ground-floor/basement; treat with caution. → "Underground" here means a below-grade hall: the COHERENT collaboration calls Neutrino Alley a basement hallway. No source consulted (checked 2026-10-25) gives its depth below grade, its bearing, or which building lies above it.
- `/sources`: ["src:ornl-sns-page", "src:ornl-wikipedia", "src:facilities-verify-ornl-ror", "src:geo-ornl-osm-sns-boundary"] → ["src:ornl-sns-page", "src:ornl-wikipedia", "src:facilities-verify-ornl-ror", "src:geo-ornl-osm-sns-boundary", "src:geo-ornl-neutrino-alley-qa", "src:cevns-coherent-csi-2022-full-dataset"]
- `/summary/plain`: A shielded corridor next to the neutron-producing target of the Spallation Neutron Source at Oak Ridge, Tennessee, used to detect neutrinos produced as a byproduct of the neutron beam. → A shielded basement hallway close to the neutron-producing target of the Spallation Neutron Source at Oak Ridge, Tennessee, used to detect neutrinos produced as a by-product of the neutron beam.
- `/summary/technical`: 'Neutrino Alley': a shielded basement hallway adjacent to the SNS liquid-mercury spallation target, exploited as a pion/muon-decay-at-rest neutrino source for CEvNS experiments (e.g. COHERENT); no official coordinate found in this session (see note). → "Neutrino Alley": a 50 m basement hallway whose closest point is about 20 m from the SNS liquid-mercury spallation target, exploited as a pion/muon-decay-at-rest neutrino source for CEvNS experiments (COHERENT). No published coordinate or plan locates it; the marker is the centroid of the SNS complex outline (see site:ornl-sns-complex).

**data/atlas/sources/rc-aps-news-2000-sns-construction.json**
- `(new file)`:  → created

**data/atlas/sources/rc-holtkamp-epac08-sns.json**
- `(new file)`:  → created

**data/atlas/sources/rc-ornl-news-2005-sns-partnership.json**
- `(new file)`:  → created

**data/atlas/sources/rc-ornl-news-2006-first-neutrons.json**
- `(new file)`:  → created

**data/atlas/sources/rc-ornl-official-site.json**
- `(new file)`:  → created


### F5 names (commit 20f15c8)

**data/atlas/geometry/daya-bay-eh1-hall.json**
- `/name`: Daya Bay near hall (EH1) → Daya Bay near hall (EH1) position (derived point)

**data/atlas/geometry/daya-bay-eh2-hall.json**
- `/name`: Ling Ao near hall (EH2) → Ling Ao near hall (EH2) position (derived point)

**data/atlas/geometry/daya-bay-eh3-hall.json**
- `/name`: Far hall (EH3) → Daya Bay far hall (EH3) position (derived point)

**data/atlas/geometry/point1-atlas-boundary.json**
- `/name`: CERN Point 1 surface site (ATLAS) → LHC Point 1 surface site (ATLAS)

**data/atlas/geometry/point2-alice-boundary.json**
- `/name`: CERN Point 2 surface site (ALICE) → LHC Point 2 surface site (ALICE)

**data/atlas/geometry/point2-l3-boundary.json**
- `/name`: CERN Point 2 surface site (L3, LEP era) → LEP Point 2 surface site (L3)

**data/atlas/geometry/point4-aleph-boundary.json**
- `/name`: CERN Point 4 surface site (ALEPH, LEP era) → LEP Point 4 surface site (ALEPH)

**data/atlas/geometry/point5-cms-boundary.json**
- `/name`: CERN Point 5 surface site (CMS) → LHC Point 5 surface site (CMS)

**data/atlas/geometry/point5-cms-cavern.json**
- `/name`: CMS underground cavern (surveyed point) → CMS cavern position (published coordinate, ±30 m)

**data/atlas/geometry/point8-delphi-boundary.json**
- `/name`: CERN Point 8 surface site (DELPHI, LEP era) → LEP Point 8 surface site (DELPHI)

**data/atlas/geometry/point8-lhcb-boundary.json**
- `/name`: CERN Point 8 surface site (LHCb) → LHC Point 8 surface site (LHCb)

**data/atlas/geometry/reno-far-detector.json**
- `/name`: RENO far detector hall → RENO far detector hall position (derived point)

**data/atlas/geometry/reno-near-detector.json**
- `/name`: RENO near detector hall → RENO near detector hall position (derived point)

**data/atlas/geometry/soudan-minos-far-detector-point.json**
- `/name`: Soudan Underground Laboratory, Level 27 (MINOS far detector, CDMS II, SuperCDMS Soudan) → Soudan Underground Laboratory, Level 27: cavern position (published coordinate; MINOS far detector, CDMS II, SuperCDMS Soudan)

**data/atlas/geometry/surf-davis-campus-cavern.json**
- `/name`: Davis Campus cavern, 4850 Level (LZ, Majorana Demonstrator) → Davis Campus cavern position, 4850 Level (published coordinate; LZ, Majorana Demonstrator)

**data/atlas/sites/boulby-mine.json**
- `/aliases`: ["Boulby Underground Laboratory site"] → ["Boulby Underground Laboratory site", "Boulby Mine underground laboratory"]
- `/name`: Boulby Mine underground laboratory → Boulby Mine (site of the underground laboratory)

**data/atlas/sites/cern-ecn3-north-area.json**
- `/aliases`: ["ECN3", "TCC8 + ECN3"] → ["ECN3", "TCC8 + ECN3", "ECN3 cavern, CERN North Area"]
- `/name`: ECN3 cavern, CERN North Area → ECN3, CERN North Area

**data/atlas/sites/cern-lep-point-2-l3.json**
- `/aliases`: ["Point 2", "LEP IP2"] → ["Point 2", "LEP IP2", "LEP Point 2 (L3 cavern)"]
- `/name`: LEP Point 2 (L3 cavern) → LEP Point 2 (L3)

**data/atlas/sites/cern-lep-point-4-aleph.json**
- `/aliases`: ["Point 4", "LEP IP4"] → ["Point 4", "LEP IP4", "LEP Point 4 (ALEPH cavern)"]
- `/name`: LEP Point 4 (ALEPH cavern) → LEP Point 4 (ALEPH)

**data/atlas/sites/cern-lep-point-8-delphi.json**
- `/aliases`: ["Point 8", "LEP IP8"] → ["Point 8", "LEP IP8", "LEP Point 8 (DELPHI cavern)"]
- `/name`: LEP Point 8 (DELPHI cavern) → LEP Point 8 (DELPHI)

**data/atlas/sites/cern-point-1-atlas.json**
- `/aliases`: ["Point 1", "IP1", "ATLAS cavern", "CERN Point 1"] → ["Point 1", "IP1", "ATLAS cavern", "CERN Point 1", "LHC Point 1 (ATLAS cavern)"]
- `/name`: LHC Point 1 (ATLAS cavern) → LHC Point 1 (ATLAS)

**data/atlas/sites/cern-point-2-alice.json**
- `/aliases`: ["Point 2", "IP2", "UX25 cavern", "ALICE cavern"] → ["Point 2", "IP2", "UX25 cavern", "ALICE cavern", "LHC Point 2 (ALICE cavern)"]
- `/name`: LHC Point 2 (ALICE cavern) → LHC Point 2 (ALICE)

**data/atlas/sites/cern-point-5-cms.json**
- `/aliases`: ["Point 5", "LHC Point 5", "CMS Point 5", "CMS experimental cavern UXC55", "Cessy"] → ["Point 5", "LHC Point 5", "CMS Point 5", "CMS experimental cavern UXC55", "Cessy", "LHC Point 5 — CMS cavern, Cessy"]
- `/name`: LHC Point 5 — CMS cavern, Cessy → LHC Point 5 (CMS), Cessy

**data/atlas/sites/cern-point-8-lhcb.json**
- `/aliases`: ["Point 8", "IP8", "LHCb cavern", "CERN Point 8"] → ["Point 8", "IP8", "LHCb cavern", "CERN Point 8", "LHC Point 8 (LHCb cavern)"]
- `/name`: LHC Point 8 (LHCb cavern) → LHC Point 8 (LHCb)

**data/atlas/sites/cern-sps-lss4-ua2.json**
- `/aliases`: ["LSS4", "UA2 experimental area", "Underground Area 2"] → ["LSS4", "UA2 experimental area", "Underground Area 2", "SPS Long Straight Section 4 (UA2 hall)"]
- `/name`: SPS Long Straight Section 4 (UA2 hall) → SPS Long Straight Section 4 (UA2)

**data/atlas/sites/cern-sps-lss5-ua1.json**
- `/aliases`: ["LSS5", "UA1 experimental area", "Underground Area 1"] → ["LSS5", "UA1 experimental area", "Underground Area 1", "SPS Long Straight Section 5 (UA1 hall)"]
- `/name`: SPS Long Straight Section 5 (UA1 hall) → SPS Long Straight Section 5 (UA1)

**data/atlas/sites/south-pole-icecube.json**
- `/aliases`: ["IceCube array", "South Pole ice (IceCube)"] → ["IceCube array", "South Pole ice (IceCube)", "South Pole — IceCube array"]
- `/name`: South Pole — IceCube array → South Pole (IceCube site)


### Coordinator items (a) and (b) (commits fe718ae and c74cc4f)

**data/atlas/collaborations/atlas.json**
- `/membership/country_count/note`: home.cern states 42 countries as of March 2022. → The collaboration page and the official institutions list both give 40 countries (list: 'Number of countries with ATLAS institutions: 40', read 2026-10-25); CERN's ATLAS page gave 42 countries in March 2022.
- `/membership/country_count/verified_at`: 2026-09-16 → 2026-10-25
- `/membership/institution_count/confidence`: approximate → verified
- `/membership/institution_count/display`: <absent> → 175 institutions (246 institutes counting cluster members and associates)
- `/membership/institution_count/locator`: atlas.cern, 'The ATLAS Collaboration', figures panel → atlaspo.cern.ch/public/institutions, summary block at the foot of the page (Number of countries 40; Total number of institutions 175: Regular institutions 154, Cluster institutions 21; Institutes in clusters 76; Associate institutes 16; Total number of institutes 246). The page carries no date of its own beyond its footer; read 2026-10-25.
- `/membership/institution_count/note`: The page states '170+', so 170 is a lower bound. home.cern states 245 institutes as of March 2022 - see the record notes. → This is the official ATLAS institutions list's own total. The collaboration's page atlas.cern/Discover/Collaboration gives the rounded headline '170+ Institutions' (read 2026-10-25), consistent with 175. The list counts 175 institutions (154 regular institutions and 21 clusters of institutes) and 246 institutes (the 154, the 76 institutes inside the clusters and 16 associates); it also lists 19 technical associates and 10 Tier-1 computing centres, which are not counted in either total. The Atlas holds 197 institution rows from the list as read on 2026-09-17 (see the roster snapshot), so those rows are institutes, not institutions, and they are not a complete copy of the list's 246.
- `/membership/institution_count/quote`: 170+ Institutions → Total number of institutions: 175
- `/membership/institution_count/sources`: ["src:atlas-collaboration-page"] → ["src:atlas-institutions", "src:atlas-collaboration-page"]
- `/membership/institution_count/value`: 170 → 175
- `/membership/institution_count/verified_at`: 2026-09-16 → 2026-10-25
- `/membership/member_count/verified_at`: 2026-09-16 → 2026-10-25
- `/notes`: ["CONFLICT on size: atlas.cern (the collaboration's own page) gives 'over 5500 members and 3000 scientific authors', '170+ Institutions', '40 Countries'; home.cern's ATLAS page gives 'More than 5500 scientists from 245 institutes in 42 countries (March 2022)'. The collaboration's own current figures are recorded; the two institution counts are almost certainly counting different things (member institutions vs. institutes including sub-groups), but no fetched source says so.", "The stated counts carry no publication date on the page; as_of is set to the month this partition was researched (2026-09) and the counts are marked approximate because the page gives them as 'over' and '170+'.", "Leadership rows are intentionally empty: no fetched source names the current spokesperson."] → ["Sizes from three official ATLAS pages, read 2026-10-25. The collaboration page (atlas.cern/Discover/Collaboration) says 'over 5500 members and 3000 scientific authors', '170+ Institutions', '40 Countries'. The official institutions list (atlaspo.cern.ch/public/institutions) counts 175 institutions, 246 institutes and 40 countries. CERN's ATLAS page gave 'More than 5500 scientists from 245 institutes in 42 countries' in March 2022. The institution figures differ only in what they count: institutions (175; '170+' on the collaboration page) versus institutes (246 on the list, 245 in 2022), where cluster members and associates count as institutes.", "The Atlas's 197 institution rows come from the official institutions list as read on 2026-09-17; they are institutes (a subset of the list's 246), not a count of institutions.", "The page gives its counts without a date; the membership 'as of' month (2026-09) is when the roster was recorded. The figures are lower bounds where the page says 'over' or '170+'.", "Leadership rows are empty: no source consulted names the current spokesperson."]

**data/atlas/geometry/bnl-upton-campus-boundary.json**
- `/entity_id`: site:bnl-upton-campus → null
- `/notes`: [] → ["This shape is context: it shows where the Upton campus of Brookhaven National Laboratory is, not an experiment or detector, so it is drawn in every year. It is tied to its site by place only; the site's own record follows the experiments hosted there and ends when they end, which would have hidden the campus from the years after its last experiment completed."]

**data/atlas/geometry/isis-ral-campus-boundary.json**
- `/entity_id`: site:isis-rutherford-appleton → null
- `/notes`: ["A mapped landuse polygon for the RAL campus, not a surveyed boundary; the neighbouring Harwell Campus and the UKAEA Harwell site are separate OSM polygons and are not drawn."] → ["This shape is context: it shows where the Rutherford Appleton Laboratory campus is, not an experiment or detector, so it is drawn in every year. It is tied to its site by place only; the site's own record follows the experiments hosted there and ends when they end, which would have hidden the campus from the years after its last experiment completed.", "A mapped landuse polygon for the RAL campus, not a surveyed boundary; the neighbouring Harwell Campus and the UKAEA Harwell site are separate OSM polygons and are not drawn."]

**data/atlas/geometry/mcmurdo-williams-field-aerodrome.json**
- `/entity_id`: site:mcmurdo-ldb-launch-site → null
- `/notes`: ["The atlas site record names Williams Field as the launch strip for ANITA-II and 'LDB Camp' for ANITA-LITE and ANITA-I; no fetched source separates the two, and NASA's diary places the balloon facility at Williams Field.", "OpenStreetMap also has two runway lines named Williams Field (2949 m and 1944 m, source LINZ) and a taxiway; they are not drawn: skiway positions change with the season and the ice, and the 2949 m line is 3.2 % short of the 10 000 ft (3048 m) given in the same polygon's description tag, which is not an official source."] → ["This outline is context: it depicts the aerodrome (an OpenStreetMap feature), not the balloon facility and not ANITA, so it is drawn in every year. The balloon facility (facility:mcmurdo-ldb) and the ANITA launch site (site:mcmurdo-ldb-launch-site) are tied to it by place only; the launch site's own record is active only in the years of ANITA flights, and a shape tied to it would have vanished between campaigns and after the programme ended in 2017. No source consulted dates the aerodrome's construction, so no lifetime window is given.", "The atlas site record names Williams Field as the launch strip for ANITA-II and 'LDB Camp' for ANITA-LITE and ANITA-I; no fetched source separates the two, and NASA's diary places the balloon facility at Williams Field.", "OpenStreetMap also has two runway lines named Williams Field (2949 m and 1944 m, source LINZ) and a taxiway; they are not drawn: skiway positions change with the season and the ice, and the 2949 m line is 3.2 % short of the 10 000 ft (3048 m) given in the same polygon's description tag, which is not an official source."]

**data/atlas/geometry/mit-campus-boundary.json**
- `/entity_id`: site:mit-cambridge-campus → null
- `/notes`: ["The campus is a mapped university-use outline of several separate parcels (Technology Square and the Kendall and Vassar Street blocks appear as their own rings), not a legal property boundary; it is a context shape."] → ["This shape is context: it shows where the MIT campus is, not an experiment or detector, so it is drawn in every year. It is tied to its site by place only; the site's own record follows the experiments hosted there and ends when they end, which would have hidden the campus from the years after its last experiment completed.", "The campus is a mapped university-use outline of several separate parcels (Technology Square and the Kendall and Vassar Street blocks appear as their own rings), not a legal property boundary; it is a context shape."]

**data/atlas/geometry/surf-administration-building.json**
- `/entity_id`: site:surf-surface-campus → null
- `/notes`: [] → ["This shape is context: it shows where the Sanford Lab Administration Building on the surface campus is, not an experiment or detector, so it is drawn in every year. It is tied to its site by place only; the site's own record follows the experiments hosted there and ends when they end, which would have hidden the campus from the years after its last experiment completed."]

**data/atlas/geometry/wipp-boundary.json**
- `/entity_id`: site:wipp-surface-campus → null
- `/notes`: [] → ["This shape is context: it shows where the WIPP surface area is, not an experiment or detector, so it is drawn in every year. It is tied to its site by place only; the site's own record follows the experiments hosted there and ends when they end, which would have hidden the campus from the years after its last experiment completed."]

**data/atlas/maps/mcmurdo-ldb.json**
- `/summary/technical`: One local map for facility:mcmurdo-ldb. OpenStreetMap: the Williams Field aerodrome polygon (way 821080729, source ADD, ICAO NZWD, 5.4 km2) as the site outline for site:mcmurdo-ldb-launch-site, and the McMurdo Station place node (515065315). The facility is placed at Williams Field by a NASA balloon-team diary. The LDB camp buildings and detector:anita's launch pads are unlocated; ANITA has no ground position. → One local map for facility:mcmurdo-ldb. OpenStreetMap: the Williams Field aerodrome polygon (way 821080729, source ADD, ICAO NZWD, 5.4 km2) as a timeless context outline at the place of site:mcmurdo-ldb-launch-site, and the McMurdo Station place node (515065315). The facility is placed at Williams Field by a NASA balloon-team diary. The LDB camp buildings and detector:anita's launch pads are unlocated; ANITA has no ground position.

**data/atlas/memberships/atlas.json**
- `/roster_snapshots/0/note`: <absent> → Institute rows copied from the official list as read on 2026-09-17: 197 rows. On 2026-10-25 the list counts 175 institutions and 246 institutes (cluster members and associates counted as institutes), plus 19 technical associates and 10 Tier-1 centres that are not rows here; so the rows are a subset of the list's institutes and the list has changed since the snapshot (three recorded institutes did not match any entry exactly on the page read on 2026-10-25).

**data/atlas/sources/atlas-collaboration-page.json**
- `/accessed`: 2026-09-16 → 2026-10-25

**data/atlas/sources/atlas-institutions.json**
- `/accessed`: 2026-09-17 → 2026-10-25


**data/atlas/geometry/auger-sd750-infill-boundary.json**
- `/notes/1`: Licence added 2026-10-25: sdMap.csv is released under CC BY-SA 4.0 (opendata.auger.org home page), so the derived geometry carries that licence name and attribution. → Licence: sdMap.csv is released under CC BY-SA 4.0 (opendata.auger.org home page), so the derived geometry carries that licence name and attribution.

**data/atlas/geometry/brokdorf-conus-detector.json**
- `/geometry/note`: CONUS's own paper (arXiv:2401.07684) states the detector sat 17.1 m from the reactor core center at Brokdorf, inside the reactor building itself (not a separate structure). No fetched source gives the azimuth of that 17.1 m offset from the core, so this point is the OSM 'Reaktorgebäude' building's own centroid (geometry:brokdorf-core), used directly as the detector's position; accuracy_m is 40 m (release geometry, underground stream): the unresolved 17.1 m offset plus up to ~21 m between the polygon centroid and the reactor axis (a circle fitted to the 13 vertices of the polygon's circular arc, radius 40.2 m, residual <= 2.7 m, is centred 20.4 m SSW of the centroid, at 9.3457897 E 53.8505931 … → CONUS's own paper (arXiv:2401.07684) states the detector sat 17.1 m from the reactor core center at Brokdorf, inside the reactor building itself (not a separate structure). No source consulted gives the azimuth of that 17.1 m offset from the core, so this point is the centroid of the OSM 'Reaktorgebäude' building (geometry:brokdorf-core), used directly as the detector's position. The stated accuracy is 40 m: the unresolved 17.1 m offset plus up to about 21 m between the polygon centroid and the reactor axis (a circle fitted to the 13 vertices of the polygon's circular arc, radius 40.2 m, residual <= 2.7 m, is centred 20.4 m SSW of the centroid, at 9.3457897 E 53.8505931 N; no source states w …
- `/method`: CONUS's own paper (arXiv:2401.07684) states the detector sat 17.1 m from the reactor core center at Brokdorf, inside the reactor building itself (not a separate structure). No fetched source gives the azimuth of that 17.1 m offset from the core, so this point is the OSM 'Reaktorgebäude' building's own centroid (geometry:brokdorf-core), used directly as the detector's position; accuracy_m is 40 m (release geometry, underground stream): the unresolved 17.1 m offset plus up to ~21 m between the polygon centroid and the reactor axis (a circle fitted to the 13 vertices of the polygon's circular arc, radius 40.2 m, residual <= 2.7 m, is centred 20.4 m SSW of the centroid, at 9.3457897 E 53.8505931 … → CONUS's own paper (arXiv:2401.07684) states the detector sat 17.1 m from the reactor core center at Brokdorf, inside the reactor building itself (not a separate structure). No source consulted gives the azimuth of that 17.1 m offset from the core, so this point is the centroid of the OSM 'Reaktorgebäude' building (geometry:brokdorf-core), used directly as the detector's position. The stated accuracy is 40 m: the unresolved 17.1 m offset plus up to about 21 m between the polygon centroid and the reactor axis (a circle fitted to the 13 vertices of the polygon's circular arc, radius 40.2 m, residual <= 2.7 m, is centred 20.4 m SSW of the centroid, at 9.3457897 E 53.8505931 N; no source states w …
- `/notes`: ["Integrator (2026-09-21): ODbL-1.0 licence added — the shape is derived from or copied from OpenStreetMap data (src:geo-reactors-osm-brokdorf-leibstadt-reactors), which makes it a derivative database under the ODbL regardless of the derivation step in between.", "Release geometry (underground): accuracy_m raised from 20 to 40 m; see method."] → ["The shape is derived from or copied from OpenStreetMap data (src:geo-reactors-osm-brokdorf-leibstadt-reactors), which makes it a derivative database under the ODbL regardless of the derivation step in between."]

**data/atlas/geometry/brokdorf-core.json**
- `/notes/0`: Integrator (2026-09-21): entity_id set to the plant campus site so the map accounts for the detector-hosting site; the reactor building is the structure the CONUS detectors sat in. → The shape is attached to the plant campus site so the map accounts for the detector-hosting site; the reactor building is the structure the CONUS detectors sat in.

**data/atlas/geometry/chooz-core-b1.json**
- `/notes/0`: Release geometry (underground): centroid separation of B1 and B2 is 163.3 m against 160 m (arXiv:1905.10258) and 165 m (arXiv:2009.05515); the 2006 TDR map caption says 140 m, which the OSM unit footprints do not support (16 % off) and is not used as a check. The footprints are whole nuclear-island buildings (~228 m span), not reactor-building domes, so the centroid is a proxy for the core axis good to a few tens of metres. → Centroid separation of B1 and B2 is 163.3 m against 160 m (arXiv:1905.10258) and 165 m (arXiv:2009.05515). The 2006 TDR map caption says 140 m, which the OSM unit footprints do not support (16 % off), so it is not used as a check. The footprints are whole nuclear-island buildings (~228 m span), not reactor-building domes, so the centroid is a proxy for the core axis good to a few tens of metres.

**data/atlas/geometry/daya-bay-eh1-hall.json**
- `/notes/0`: Integrator (2026-09-21): ODbL-1.0 licence added — the shape is derived from or copied from OpenStreetMap data (src:geo-reactors-osm-dayabay-reactors), which makes it a derivative database under the ODbL regardless of the derivation step in between. → The shape is derived from or copied from OpenStreetMap data (src:geo-reactors-osm-dayabay-reactors), which makes it a derivative database under the ODbL regardless of the derivation step in between.

**data/atlas/geometry/daya-bay-eh2-hall.json**
- `/notes/0`: Integrator (2026-09-21): the distance check to the sixth core measures 472.7 m against 500.1 m expected (5.5 %); the other five cores agree within 3 %. The 27 m residual is attributed to the reactor-building centroid standing in for that core's centre; tolerance on that one check is 6 % and accuracy_m is 30 m. → The distance check to the sixth core measures 472.7 m against 500.1 m expected (5.5 %); the other five cores agree within 3 %. The 27 m residual is attributed to the reactor-building centroid standing in for that core's centre; tolerance on that one check is 6 % and accuracy_m is 30 m.
- `/notes/1`: Integrator (2026-09-21): ODbL-1.0 licence added — the shape is derived from or copied from OpenStreetMap data (src:geo-reactors-osm-dayabay-reactors), which makes it a derivative database under the ODbL regardless of the derivation step in between. → The shape is derived from or copied from OpenStreetMap data (src:geo-reactors-osm-dayabay-reactors), which makes it a derivative database under the ODbL regardless of the derivation step in between.

**data/atlas/geometry/daya-bay-eh3-hall.json**
- `/notes/0`: Integrator (2026-09-21): ODbL-1.0 licence added — the shape is derived from or copied from OpenStreetMap data (src:geo-reactors-osm-dayabay-reactors), which makes it a derivative database under the ODbL regardless of the derivation step in between. → The shape is derived from or copied from OpenStreetMap data (src:geo-reactors-osm-dayabay-reactors), which makes it a derivative database under the ODbL regardless of the derivation step in between.

**data/atlas/geometry/fermilab-booster-ring.json**
- `/method`: Centre fixed by two independent least-squares circle fits to OpenStreetMap geometry that agree to within 0.2 m: (a) OSM way 21825283 'Booster Ring Road' (closed loop, 25 vertices, fit centre 41.836555,-88.263493, fitted radius 58.7 m, rms 0.8 m; path length 367.9 m, consistent with this road being an access loop inside the ring, not the ring itself); (b) OSM ways 272646259 'Booster Tower West' and 272646261 'Booster Tower East' (92 vertices of two arc-shaped RF-gallery building footprints that hug the ring wall, fit centre 41.836557,-88.263493, fitted radius 69.5 m, rms 7.9 m). Both centres coincide to <1 m. The Booster is sourced as a '474-meter-circumference synchrotron' (src:fermilab-mini … → Centre fixed by two independent least-squares circle fits to OpenStreetMap geometry that agree to within 0.2 m: (a) OSM way 21825283 'Booster Ring Road' (closed loop, 25 vertices, fit centre 41.836555,-88.263493, fitted radius 58.7 m, rms 0.8 m; path length 367.9 m, consistent with this road being an access loop inside the ring, not the ring itself); (b) OSM ways 272646259 'Booster Tower West' and 272646261 'Booster Tower East' (92 vertices of two arc-shaped RF-gallery building footprints that hug the ring wall, fit centre 41.836557,-88.263493, fitted radius 69.5 m, rms 7.9 m). Both centres coincide to <1 m. The Booster is sourced as a '474-meter-circumference synchrotron' (src:fermilab-mini …

**data/atlas/geometry/hess-ct1-4-square.json**
- `/method`: Quadrilateral whose four vertices are the centroids (hepgraph.atlas.geo.centroid) of the four corner-telescope footprints, OpenStreetMap ways 171900951 (north), 171900954 (east), 171900955 (south), 171900956 (west), joined N-E-S-W. Replaces the previous square, which had been placed on the array's published coordinate and so carried that coordinate's 200 m uncertainty. The perimeter check compares this OSM-derived quadrilateral with the published 120 m side (480 m perimeter): an independent test, because the OSM positions were not fitted to it. → Quadrilateral whose four vertices are the centroids of the four corner-telescope footprints, OpenStreetMap ways 171900951 (north), 171900954 (east), 171900955 (south), 171900956 (west), joined N-E-S-W. The perimeter check compares this OSM-derived quadrilateral with the published 120 m side (480 m perimeter): an independent test, because the OSM positions were not fitted to it.

**data/atlas/geometry/kit-campus-north-boundary.json**
- `/entity_id`: site:kit-campus-north → null
- `/notes`: ["A mapped campus outline estimated by an OSM contributor, not a cadastral boundary; it is a context shape."] → ["This shape is context: it shows where KIT Campus North is, not an experiment or detector, so it is drawn in every year. It is tied to its site by place only; the site's own record follows the experiments hosted there, which would have drawn the campus only from the date of the first hosted experiment.", "A mapped campus outline estimated by an OSM contributor, not a cadastral boundary; it is a context shape."]

**data/atlas/geometry/lansce-ta-53-boundary.json**
- `/method`: Los Alamos County's 'Technical_areas_LANL' polygon for TA-53 (LONG_NAME 'MESON PHYSICS FACILITY', 751 acres) used as published, simplified from 1006 to 110 vertices by Douglas-Peucker at 8 m (hepgraph.atlas.geo.simplify), well inside accuracy_m. The area is about 3 km long east to west; the LANSCE buildings occupy its middle and east parts. The boundary is the administrative technical-area line shown on public maps, not a fence line. → Los Alamos County's 'Technical_areas_LANL' polygon for TA-53 (LONG_NAME 'MESON PHYSICS FACILITY', 751 acres) used as published, simplified from 1006 to 110 vertices by Douglas-Peucker at 8 m, well inside the stated 20 m accuracy. The area is about 3 km long east to west; the LANSCE buildings occupy its middle and east parts. The boundary is the administrative technical-area line shown on public maps, not a fence line.

**data/atlas/geometry/leibstadt-core.json**
- `/notes`: ["Release geometry (underground): the earlier record (way 567961020, picked as the largest building near the plant's bus-stop node) was a different building; it is no longer drawn.", "entity_id is the plant campus site so the map accounts for the detector-hosting site; the reactor building is the structure the CONUS+ detector sits in."] → ["entity_id is the plant campus site so the map accounts for the detector-hosting site; the reactor building is the structure the CONUS+ detector sits in."]

**data/atlas/geometry/psi-campus-boundary.json**
- `/entity_id`: site:psi-villigen → null
- `/notes`: ["OSM's timestamp_osm_base is not available from Nominatim's response the way it is from a direct Overpass extract; osm.timestamp records the access date instead.", "This feature is linked to the PSI Villigen site and, through it, covers the site-hosted detector placements of MEG, MEG II and Mu3e; none of them has its own sourced hall footprint."] → ["This shape is context: it shows where the PSI Villigen/Würenlingen campus is, not an experiment or detector, so it is drawn in every year. It is tied to its site by place only; the site's own record follows the experiments hosted there, which would have drawn the campus only from the date of the first hosted experiment.", "OSM's timestamp_osm_base is not available from Nominatim's response the way it is from a direct Overpass extract; osm.timestamp records the access date instead.", "This feature is linked to the PSI Villigen site and, through it, covers the site-hosted detector placements of MEG, MEG II and Mu3e; none of them has its own sourced hall footprint."]

**data/atlas/geometry/reno-far-detector.json**
- `/notes/0`: Integrator (2026-09-21): ODbL-1.0 licence added — the shape is derived from or copied from OpenStreetMap data (src:geo-reactors-osm-hanbit-reactors), which makes it a derivative database under the ODbL regardless of the derivation step in between. → The shape is derived from or copied from OpenStreetMap data (src:geo-reactors-osm-hanbit-reactors), which makes it a derivative database under the ODbL regardless of the derivation step in between.

**data/atlas/geometry/reno-near-detector.json**
- `/notes/0`: Integrator (2026-09-21): checks against units 3–6 sit 3.3–3.8 % (10–28 m) from the TDR distances; over 300–740 m baselines that is the expected size of the offset between a reactor-building centroid and the core centre, so the tolerance is 5 % and accuracy_m 30 m rather than the fit residual alone. → Checks against units 3–6 sit 3.3–3.8 % (10–28 m) from the TDR distances; over 300–740 m baselines that is the expected size of the offset between a reactor-building centroid and the core centre, so the tolerance is 5 % and accuracy_m 30 m rather than the fit residual alone.
- `/notes/1`: Integrator (2026-09-21): ODbL-1.0 licence added — the shape is derived from or copied from OpenStreetMap data (src:geo-reactors-osm-hanbit-reactors), which makes it a derivative database under the ODbL regardless of the derivation step in between. → The shape is derived from or copied from OpenStreetMap data (src:geo-reactors-osm-hanbit-reactors), which makes it a derivative database under the ODbL regardless of the derivation step in between.

**data/atlas/geometry/slac-property-boundary.json**
- `/entity_id`: site:slac-menlo-park-campus → null
- `/notes`: [] → ["This shape is context: it shows where the SLAC National Accelerator Laboratory property is, not an experiment or detector, so it is drawn in every year. It is tied to its site by place only; the site's own record follows the experiments hosted there, which would have drawn the campus only from the date of the first hosted experiment."]

**data/atlas/geometry/soudan-minos-far-detector-point.json**
- `/notes/0`: Release geometry (underground): coordinate refined from 5 to 6 decimals and accuracy_m from 100 to 3 m after reading Sec. 6.5 of arXiv:0805.3170; the position is the detector midpoint, not the whole hall. → The coordinate is the six-decimal survey of arXiv:0805.3170 Sec. 6.5, with a stated accuracy of 3 m; the position is the detector midpoint, not the whole hall.

**data/atlas/maps/juno-jiangmen.json**
- `/summary/technical`: Published coordinate of the hall (arXiv:2104.02565) as a surveyed point with 150 m accuracy, and the OSM outline of the surface campus. The access shafts are not drawn (no coordinates published); the Yangjiang and Taishan reactor buildings and the 52-53 km baselines are on map:juno-reactor-baselines. → Published coordinate of the hall (arXiv:2104.02565) as a surveyed point with 150 m accuracy, and the OSM outline of the surface campus. The access shafts are not drawn (no coordinates published); the Yangjiang and Taishan reactor buildings, 52-53 km from the hall, are on map:juno-reactor-baselines.


## Appendices A to E: complete logs of the five source-checking sub-streams (old -> new with sources and quotes)



---

## Appendix A. DUNE depth, ProtoDUNE-SP/DP, Fermilab website (F9, F14, F16)

# dune agent log (rc-data, 2026-10-25)

Files changed: data/atlas/experiments/dune.json, detectors/dune-far-detector-1.json, dune-far-detector-2.json, dune-near-detector.json, protodune-sp.json, protodune-dp.json, facilities/fermilab.json. New source records: data/atlas/sources/rc-fermilab-official-site.json, data/atlas/sources/rc-cern-ep-news-dune-prototypes.json (no `rank` written: the validator says rank is derived). No existing source record was edited (not in the file list); the lead may bump `accessed` of src:dune-fd-tdr-vol-1, src:majorana-demonstrator-surf-news and src:dune-collaboration-site to 2026-10-25 if wanted.

Retrieval notes
- DUNE FD TDR Vol. I (arXiv 2002.02967): WebFetch rejects the 27 MB PDF (maxContentLength). The Figure 1.4 sentence was confirmed through WebFetch of the ar5iv HTML copy ("also referred to as the 4850 (foot) level or 4850l"); the verbatim PDF wording, the glossary entry and the page numbers come from the PDF text that scripts/atlas_quote_check.py fetched on 2026-10-25 (cache facts/cache, https://arxiv.org/pdf/2002.02967). The ar5iv copy is cut off before the glossary.
- https://www.fnal.gov/ returns HTTP 403 (Cloudflare "Just a moment") to WebFetch and curl; it loaded in the browser pane on 2026-10-25 (title "Fermilab | Home").
- https://ep-news-wp.web.cern.ch/dune-prototype-activities-neutrino-platform/ fetched with WebFetch and curl on 2026-10-25; the page carries no date, only the tags "March 2022 – May 2022".
- https://sanfordlab.org/news/majorana-demonstrator-project-4850-level-davis-campus, https://www.dunescience.org/ re-fetched 2026-10-25.

## F9  experiment:dune key_specs "Far detector depth" (/key_specs/4/quantity)

Sources and verbatim quotes
- LEAD (value `quote`): src:dune-fd-tdr-vol-1, §1.2 (sentence introducing Fig. 1.4), arXiv PDF p. 25 (printed p. 1-9): "Figure 1.4 shows the cavern layout for the FD in the SURF underground area, also referred to as the 4850 (foot) level or 4850L."  (quote check: verbatim; no number flag, 4850 ft = 1478.3 m is accepted by the checker)
- src:rf04-protodune-sp-performance-arxiv (existing): "a far detector located at the 4850 ft level of Sanford Underground Research Facility (SURF)" (quoted in `note`; verbatim in the cache text).
- SECONDARY (unit conversion, quoted in `note`): src:majorana-demonstrator-surf-news (SURF news page about the MAJORANA Demonstrator; DUNE is not mentioned on it): "will be located at the 4850 Level (1478 m) Davis Campus at the Sanford Lab Underground Research Facility (SURF)."  This is the only SURF page found that gives the 4850 Level in metres as 1478 m; other SURF pages give feet only (our-story: "the deepest in the United States at 4,850 feet") or 1,490 m (science-impact: "SURF is the deepest underground lab in the U.S. at 1,490 meters").
- TDR glossary, arXiv PDF p. 218 (printed p. C-202), quoted in `note`: "4850L The depth in feet (1480 m) of the top of the cryostats underground at SURF; used more generally to refer to the DUNE underground area." (DUNE's own metric figure is the rounded 1480 m.)
- Existing Snowmass 2022 (1500 m) and Heise 2024 (1490 m) statements kept in `note` (verbatim in cache text).
- The 1478 m value is kept as the unit conversion 4850 ft x 0.3048 = 1478.3 m, as instructed; the note now says so and says DUNE/TDR round to 1480 m / ~1.5 km.

Other uses of the MAJORANA page for DUNE values (NOT changed, not my files): sites/surf-4850-level-dune-far-detector.json (depth value, two copies at lines ~34 and ~68, same MAJORANA quote and the old "CHANGED 2026-10-25 ..." note), facilities/surf.json depth (line ~116), maps/surf.json (4850 Level (1478 m) item, line ~35). Also used for MAJORANA's own records (experiments/majorana-demonstrator.json, detectors/majorana-demonstrator.json), where it is on topic.

## F14  facility:fermilab links.website

Old: {"confidence":"verified","note":"www.fnal.gov could not be retrieved in this session (HTTP 403); the LBNF/DUNE project site is the fetched official Fermilab page.","sources":["src:fermilab-lbnf-dune-site"],"value":"https://lbnf-dune.fnal.gov/","verified_at":"2026-09-16"}
New: value "https://www.fnal.gov/", sources ["src:rc-fermilab-official-site"], locator "home page; page title \"Fermilab | Home\", headline \"Fermilab is America's particle physics and accelerator laboratory\"", verified_at 2026-10-25, note on the 403 and on lbnf-dune.fnal.gov being a project site. No `quote` was put on the value because the quote checker cannot fetch www.fnal.gov (HTTP 403 -> "unfetchable"); the page title/headline are in the locator and in the source `excerpt`.
Source record: src:rc-fermilab-official-site (url https://www.fnal.gov/, official_facility_site, retrieval full_text, accessed 2026-10-25). Also appended it to the record-level `sources`.
Other process-language edits in the same file: notes[0] and operator_text.note (see diff below).

Check of other facility/accelerator/beamline records whose links.website is a project or experiment site instead of the lab/facility site (NOT changed):
- facility:kit-karlsruhe -> https://www.katrin.kit.edu/ (KATRIN experiment site, not KIT)
- facility:oak-ridge-national-laboratory -> https://neutrons.ornl.gov/sns (SNS sub-site, not ornl.gov)
- facility:fred-lawrence-whipple-observatory -> https://veritas.sao.arizona.edu/ (VERITAS experiment site)
- facility:hess-khomas-highland -> https://hess-experiment.eu/ (H.E.S.S. collaboration site)
- facility:juno-jiangmen -> https://juno.ihep.cas.cn/ (JUNO experiment site)
- facility:lhaaso-daocheng -> http://english.ihep.cas.cn/lhaaso/ (LHAASO page on the IHEP site)
- facility:mcmurdo-ldb -> https://www.csbf.nasa.gov/antarctica/payloads.htm (a payloads page)
- beamline:lbnf -> https://lbnf-dune.fnal.gov/ is correct for a beamline/project record.
- No accelerator record uses an fnal.gov subdomain (all Fermilab accelerators have website null); no other facility uses lbnf-dune or any fnal subdomain.

## F16  detector:protodune-sp placement / intervals (and sibling detector:protodune-dp)

Source: src:rc-cern-ep-news-dune-prototypes, CERN EP department newsletter "DUNE prototype activities at the Neutrino Platform" (undated; tagged March 2022 – May 2022), https://ep-news-wp.web.cern.ch/dune-prototype-activities-neutrino-platform/ (official_facility_site, retrieval full_text).
Verbatim sentences used (all quote-check verbatim):
- "ProtoDUNE-SP (NP04), the single-phase Horizontal Drift DUNE Far Detector prototype at the CERN Neutrino Platform, successfully operated from August 2018 to July 2020 in the CERN EHN1 experimental area" -> interval 0 and placement.
- "the NP04 cryostat was emptied from 22 July 2020 until 24 October 2020 marking the completion of ProtoDUNE-SP Phase I (ProtoDUNE-I)" -> interval 1.
- "ProtoDUNE-II activities were initiated in November 2020 with the decommissioning of ProtoDUNE-I." and "The cryostat was opened by February 2021 and all detector components were removed from the cryostat by September 2021." -> quoted facts in notes.
- "With its ~750 tonnes of LAr, ProtoDUNE is the largest LArTPC ever operated." -> new specs.total_mass (approximate, 750 t), replacing null and the unsourced "about 0.8 kt" note.
- "NP02, the twin cryostat of NP04, hosted a prototype of dual phase (liquid-vapor) argon TPC (ProtoDUNE-DP) in 2019-2020." -> ProtoDUNE-DP intervals and placement.
Decisions: placement end = "2020-07" (end of operation, as for other detectors' placements); components were out of the cryostat only by September 2021 and that is stated in the placement note. Detector intervals split into active (start Aug-Sep 2018, end 2020-07) and completed (start 2020-07, no end), so the derived state is no longer "completed" from 2018. Start 2018-08/09: CERN says August 2018, DUNE site says data taking from September 2018 -> start {date 2018-09, earliest 2018-08, latest 2018-09, display "August-September 2018"}. state_at checks: SP 2019 active/certain; SP 2020-09 and 2026 absent (completed, as for BaBar etc.). DP: 2019 active/possible, 2020 completed/possible (year-precision bounds).

## Detailed old -> new (generated from git diff HEAD, JSON pointers)

### data/atlas/experiments/dune.json

- `/intervals/1/note`
  - old: `"Publication of the LBNF/DUNE CDR; used here as the design-maturity milestone, not as a formal approval date (a CD-1R date could not be sourced)."`
  - new: `"Publication of the LBNF/DUNE CDR; used here as the design-maturity milestone, not as a formal approval date (no source consulted, checked 2026-09-16, gives a CD-1R approval date)."`
- `/key_specs/4/quantity/display`
  - old: `"1478 m (4850-foot level); sources round this to about 1500 m"`
  - new: `"1478 m (4850-foot level, converted from feet); sources round this to 1480-1500 m"`
- `/key_specs/4/quantity/locator`
  - old: `"page 'The MAJORANA Demonstrator Project at the 4850 Level Davis Campus', paragraph on the shield and the underground location (the page states the level and its metric value)"`
  - new: `"DUNE FD TDR Vol. I, §1.2, the sentence introducing Fig. 1.4 (arXiv PDF p. 25, printed p. 1–9). Metric value: unit conversion of the 4850-foot level; compare the TDR glossary entry '4850L' (arXiv PDF p. 218, printed p. C–202) and SURF's page on the MAJORANA Demonstrator."`
- `/key_specs/4/quantity/note`
  - old: `"The 4850 Level is named for its depth in feet: 4850 ft x 0.3048 m/ft = 1478.3 m, the figure SURF itself gives ('4850 Level (1478 m)') and the one the local map uses. SURF's scientific director rounds it to 1500 m in the Snowmass 2022 paper (\"campuses at the 4850-foot level (1500 m, 4300 m.w.e.)\"); the same author gives 1490 m in a 2024 paper, and DUNE TDR Vol. I says \"approximately 1.5 km underground\". The water-equivalent overburden is the separate 4300 m.w.e. value. The far-detector modules are on the 4850 Level of SURF. CHANGED 2026-10-25: was value 1500 m, display \"1500 m of rock (4850-foot level)\" (the Snowmass 2022 rounding), which disagreed with the 1478 m of the map level. Placement of the DUNE far detector at this level: DUNE TDR Vol. I, §1.1.2 and Fig. 1.4 (arXiv PDF p. 25): \"the SURF underground area, also referred to as the 4850 (foot) level or 4850L\"; ProtoDUNE-SP paper (arXiv:2007.06722, PDF p. 12): \"a far detector located at the 4850 ft level of Sanford Underground Research Facility (SURF)\". The quote above is SURF's statement for the 4850 Level itself."`
  - new: `"DUNE places its far detector at the 4850-foot level of SURF: the TDR calls the underground area \"the 4850 (foot) level or 4850L\", and the ProtoDUNE-SP paper (arXiv:2007.06722, PDF p. 12) describes \"a far detector located at the 4850 ft level of Sanford Underground Research Facility (SURF)\". The value 1478 m is a unit conversion, not a depth measured for DUNE: 4850 ft x 0.3048 m/ft = 1478.3 m. For the metric figure, SURF's page on the MAJORANA Demonstrator (a different experiment, cited here only for the depth of the level in metres; DUNE is not mentioned on it) says \"will be located at the 4850 Level (1478 m) Davis Campus at the Sanford Lab Underground Research Facility (SURF).\" DUNE's own documents round the depth: the TDR glossary defines 4850L as \"The depth in feet (1480 m) of the top of the cryostats underground at SURF\" and Vol. I §1.3.1 says \"approximately 1.5 km underground\". SURF's scientific director rounds it to 1500 m in the Snowmass 2022 paper (\"campuses at the 4850-foot level (1500 m, 4300 m.w.e.)\") and gives 1490 m in a 2024 paper. The water-equivalent overburden is the separate 4300 m.w.e. value."`
- `/key_specs/4/quantity/quote`
  - old: `"The entire experiment will be located at the 4850 Level (1478 m) Davis Campus at the Sanford Lab Underground Research Facility (SURF)."`
  - new: `"Figure 1.4 shows the cavern layout for the FD in the SURF underground area, also referred to as the 4850 (foot) level or 4850L."`
- `/key_specs/4/quantity/sources/0`
  - old: `"src:majorana-demonstrator-surf-news"`
  - new: `"src:dune-fd-tdr-vol-1"`
- `/key_specs/4/quantity/sources/1`
  - old: `"src:surf-heise-snowmass-2022"`
  - new: `"src:rf04-protodune-sp-performance-arxiv"`
- `/key_specs/4/quantity/sources/2`
  - old: `"src:dune-fd-tdr-vol-1"`
  - new: `"src:majorana-demonstrator-surf-news"`
- `/key_specs/4/quantity/sources/3`
  - old: `"src:rf04-protodune-sp-performance-arxiv"`
  - new: `"src:surf-heise-snowmass-2022"`
- `/notes/1`
  - old: `"A CD-1R approval date could not be sourced from any page fetched in this session."`
  - new: `"No source consulted (checked 2026-09-16) gives a CD-1R approval date for LBNF/DUNE."`

### data/atlas/detectors/dune-far-detector-1.json

- `/intervals/1/note`
  - old: `"Fermilab stated in February 2024 that installation of the steel cryostat structure was planned to begin later that year; no confirmation of the actual start was fetched."`
  - new: `"Fermilab stated in February 2024 that installation of the steel cryostat structure was planned to begin later that year; no source consulted (checked 2026-09-16) confirms the actual start."`
- `/placements/0/note`
  - old: `"Installed in the north detector cavern on the 4850 Level at SURF; no installation start date is given in the fetched sources."`
  - new: `"Installed in the north detector cavern on the 4850 Level at SURF; none of the sources consulted gives an installation start date."`

### data/atlas/detectors/dune-far-detector-2.json

- `/notes/0`
  - old: `"Most quantities are unresolved: only the arXiv abstract of the vertical-drift TDR could be retrieved."`
  - new: `"Most quantities are unresolved: only the arXiv abstract of the vertical-drift TDR was consulted."`
- `/placements/0/note`
  - old: `"Second far detector module, to be installed in the south detector cavern at the SURF 4850 Level; no installation dates are given in the fetched abstract."`
  - new: `"Second far detector module, to be installed in the south detector cavern at the SURF 4850 Level; the abstract gives no installation dates."`
- `/specs/phase/note`
  - old: `"The vertical-drift module is a single-phase LArTPC with a different field and readout geometry; it replaced the earlier dual-phase concept. The fetched abstract does not use the phrase \"single-phase\" explicitly."`
  - new: `"The vertical-drift module is a single-phase LArTPC with a different field and readout geometry; it replaced the earlier dual-phase concept. The abstract does not use the phrase \"single-phase\" explicitly."`
- `/specs/readout/note`
  - old: `"The arXiv abstract is truncated before the readout is described and the full TDR text could not be fetched; the CRP terminology is not quoted from a fetched source."`
  - new: `"The arXiv listing truncates the abstract before the readout is described and the full report text was not consulted, so the \"charge readout plane (CRP)\" terminology is not backed by a quotation."`

### data/atlas/detectors/dune-near-detector.json

- `/intervals/0/note`
  - old: `"Publication of the Near Detector Conceptual Design Report. No construction start date for the near detector could be sourced from any page fetched in this session."`
  - new: `"Publication of the Near Detector Conceptual Design Report. No source consulted (checked 2026-09-16) gives a construction start date for the near detector."`
- `/notes/0`
  - old: `"Status \"proposed\" reflects the evidence available: the ND CDR (2021) is the latest near-detector design document that could be fetched, and no construction milestone was sourced."`
  - new: `"Status \"proposed\" reflects the evidence available: the ND CDR (2021) is the latest near-detector design document consulted (checked 2026-09-16), and none of the sources consulted gives a construction milestone."`
- `/placements/0/note`
  - old: `"Located on the Fermilab site just downstream of the neutrino source. A dedicated near-detector hall site id (site:fermilab-dune-near-detector-hall) is reserved in the registry but no coordinates for it could be sourced, so the campus site is used."`
  - new: `"Located on the Fermilab site just downstream of the neutrino source. No source consulted gives coordinates for a dedicated near-detector hall, so the Fermilab main-campus site is used."`

### data/atlas/detectors/protodune-sp.json

- `/intervals`
  - old: `[{"confidence": "uncertain", "end": null, "label": "operation at the CERN Neutrino Platform", "locator": "DUNE home page", "note": "The DUNE site states the first prototype started taking data in September 2018; no end date for ProtoDUNE-SP running could be sourced, so the terminal interval is left open (ontology §4 allows this with confidence \"uncertain\").", "quote": "The first started taking data in September 2018 and the second is under construction.", "sources": ["src:dune-collaboration-site", "src:dune-protodune-sp-performance-2020"], "start": "2018-09", "status": "completed", "verified_at": "2026-09-16"}]`
  - new: `[{"confidence": "verified", "end": "2020-07", "label": "operation at the CERN Neutrino Platform (ProtoDUNE-SP phase I)", "locator": "CERN EP department newsletter, article 'DUNE prototype activities at the Neutrino Platform' (undated; tagged March 2022 - May 2022), paragraph beginning \"ProtoDUNE-SP (NP04)\"", "note": "CERN's newsletter dates the operation from August 2018 to July 2020. The DUNE collaboration site says the first prototype \"started taking data in September 2018\", so the start is shown as August-September 2018.", "quote": "ProtoDUNE-SP (NP04), the single-phase Horizontal Drift DUNE Far Detector prototype at the CERN Neutrino Platform, successfully operated from August 2018 to July 2020 in the CERN EHN1 experimental area", "sources": ["src:rc-cern-ep-news-dune-prototypes", "src:dune-collaboration-site", "src:dune-protodune-sp-performance-2020"], "start": {"date": "2018-09", "display": "August-September 2018", "earliest": "2018-08", "latest": "2018-09"}, "status": "active", "verified_at": "2026-10-25"}, {"confidence": "verified", "end": null, "label": "phase I completed; detector decommissioned for ProtoDUNE-II", "locator": "CERN EP department newsletter, article 'DUNE prototype activities at the Neutrino Platform' (undated; tagged March 2022 - May 2022), paragraph beginning \"Following two years of successful operation\"; decommissioning: paragraph beginning \"ProtoDUNE-II activities were initiated\"", "note": "The same article says that ProtoDUNE-II activities were initiated in November 2020 with the decommissioning of ProtoDUNE-I, that the cryostat was opened by February 2021 and that all detector components were removed from it by September 2021. The completed state starts when operation ended (July 2020).", "quote": "the NP04 cryostat was emptied from 22 July 2020 until 24 October 2020 marking the completion of ProtoDUNE-SP Phase I (ProtoDUNE-I)", "sources": ["src:rc-cern-ep-news-dune-prototypes"], "start": "2020-07", "status": "completed", "verified_at": "2026-10-25"}]`
- `/notes/0`
  - old: `"The liquid argon mass (about 0.8 kt in the cryostat) could not be sourced from any page fetched in this session and is left null."`
  - new: `"Only the total liquid argon mass is entered (about 750 t, from the CERN newsletter); the active (instrumented) mass is not given in the sources consulted."`
- `/placements/0/end`
  - old: `null`
  - new: `"2020-07"`
- `/placements/0/locator`
  - old: `"abstract"`
  - new: `"CERN EP department newsletter, article 'DUNE prototype activities at the Neutrino Platform' (undated; tagged March 2022 - May 2022), paragraph beginning \"ProtoDUNE-SP (NP04)\"; ProtoDUNE-SP performance paper, abstract (installation in the CERN Neutrino Platform beam)"`
- `/placements/0/note`
  - old: `"Installed in the CERN Neutrino Platform test-beam hall (EHN1) in the CERN North Area."`
  - new: `"Installed in the CERN Neutrino Platform test-beam hall (EHN1) in the CERN North Area; operation there ended in July 2020. The CERN article adds that the NP04 cryostat was emptied from 22 July to 24 October 2020, that decommissioning for ProtoDUNE-II began in November 2020 and that all detector components were out of the cryostat by September 2021; it says the ProtoDUNE-II configuration will use the same cryostat. The performance paper's abstract says the detector \"is installed at the CERN Neutrino Platform in a specially-constructed beam\"."`
- `/placements/0/quote`
  - old: `"It is installed at the CERN Neutrino Platform in a specially-constructed beam that delivers charged pions, kaons, protons, muons and electrons with momenta in the range 0.3 GeV/c to 7 GeV/c."`
  - new: `"ProtoDUNE-SP (NP04), the single-phase Horizontal Drift DUNE Far Detector prototype at the CERN Neutrino Platform, successfully operated from August 2018 to July 2020 in the CERN EHN1 experimental area"`
- `/placements/0/sources`
  - old: `["src:dune-protodune-sp-performance-2020"]`
  - new: `["src:rc-cern-ep-news-dune-prototypes", "src:dune-protodune-sp-performance-2020"]`
- `/placements/0/verified_at`
  - old: `"2026-09-16"`
  - new: `"2026-10-25"`
- `/sources`
  - old: `["src:dune-protodune-sp-performance-2020", "src:dune-fd-tdr-vol-1", "src:dune-collaboration-site", "src:dune-cern-neutrino-platform-page", "src:rf04-protodune-sp-performance-arxiv"]`
  - new: `["src:dune-protodune-sp-performance-2020", "src:dune-fd-tdr-vol-1", "src:dune-collaboration-site", "src:dune-cern-neutrino-platform-page", "src:rf04-protodune-sp-performance-arxiv", "src:rc-cern-ep-news-dune-prototypes"]`
- `/specs/total_mass`
  - old: `null`
  - new: `{"approx": true, "confidence": "approximate", "dimension": "mass", "display": "about 750 t of liquid argon", "locator": "CERN EP department newsletter, article 'DUNE prototype activities at the Neutrino Platform' (undated; tagged March 2022 - May 2022), paragraph beginning \"ProtoDUNE-SP (NP04)\"", "note": "The article writes \"~750 tonnes of LAr\" for ProtoDUNE in its paragraph on ProtoDUNE-SP and does not say whether this is the cryostat's total or the instrumented mass; it is entered as the total liquid argon mass.", "quote": "With its ~750 tonnes of LAr, ProtoDUNE is the largest LArTPC ever operated.", "sources": ["src:rc-cern-ep-news-dune-prototypes"], "unit": "t", "value": 750, "verified_at": "2026-10-25"}`
- `/summary/plain`
  - old: `"A full-height prototype of the DUNE far detector, built at CERN and exposed to a test beam of known particles from 2018. It showed that the design works before the real detectors were built in South Dakota."`
  - new: `"A full-height prototype of the DUNE far detector, built at CERN and exposed to a test beam of known particles from 2018 to 2020. It showed that the design works before the real detectors were built in South Dakota."`
- `/summary/technical`
  - old: `"Single-phase LArTPC prototype at the CERN Neutrino Platform (EHN1) with a 7.2 × 6.0 × 6.9 m³ active volume, 3.6 m drift at 500 V/cm, full-size DUNE APAs, photon detectors and a cosmic-ray tagger, in a 0.3-7 GeV/c tagged charged-particle beam from 2018."`
  - new: `"Single-phase LArTPC prototype at the CERN Neutrino Platform (EHN1) with a 7.2 × 6.0 × 6.9 m³ active volume, 3.6 m drift at 500 V/cm, full-size DUNE APAs, photon detectors and a cosmic-ray tagger, in a 0.3-7 GeV/c tagged charged-particle beam. Operated from August 2018 to July 2020; decommissioning for ProtoDUNE-II began in November 2020."`

### data/atlas/detectors/protodune-dp.json

- `/intervals`
  - old: `[{"confidence": "uncertain", "end": null, "label": "construction and operation at the CERN Neutrino Platform", "locator": "Vol. I, §1.3.2", "note": "A10: an interval with `start: null` and `end: null` covers no date at all (A3: \"start: null covers only [lo(end), hi(end)]\"), so the derived state at the build date was `unrecorded` rather than `completed`. The DUNE FD TDR Vol. I (2020-02-07) states, in the past tense, that both ProtoDUNE prototypes had already been constructed and operated at CERN, but gives no explicit start or end date for ProtoDUNE-DP. `start` is set to the TDR's own publication year (2020) as a \"known complete by\" evidence bound, not a claim that this is the true construction date, which is not sourced. The dual-phase line was subsequently discontinued in favour of the vertical-drift design.", "quote": "The DUNE collaboration has constructed and operated two large prototype detectors, ProtoDUNE-SP, and ProtoDUNE-DP, at CERN.", "sources": ["src:dune-fd-tdr-vol-1"], "start": "2020", "status": "completed", "verified_at": "2026-09-17"}]`
  - new: `[{"confidence": "verified", "end": "2020", "label": "operation in the NP02 cryostat at the CERN Neutrino Platform", "locator": "CERN EP department newsletter, article 'DUNE prototype activities at the Neutrino Platform' (undated; tagged March 2022 - May 2022), paragraph beginning \"NP02, the twin cryostat of NP04\"", "note": "The CERN article gives the hosting period as years only (2019-2020). The DUNE FD TDR Vol. I (published 2020-02-07) says in the past tense that the collaboration \"has constructed and operated\" both ProtoDUNE prototypes at CERN.", "quote": "NP02, the twin cryostat of NP04, hosted a prototype of dual phase (liquid-vapor) argon TPC (ProtoDUNE-DP) in 2019-2020.", "sources": ["src:rc-cern-ep-news-dune-prototypes", "src:dune-fd-tdr-vol-1"], "start": "2019", "status": "active", "verified_at": "2026-10-25"}, {"confidence": "verified", "end": null, "label": "operation completed", "locator": "CERN EP department newsletter, article 'DUNE prototype activities at the Neutrino Platform' (undated; tagged March 2022 - May 2022), paragraph beginning \"NP02, the twin cryostat of NP04\"", "note": "Year precision: the article gives the last year of hosting (2020) and no month.", "quote": "NP02, the twin cryostat of NP04, hosted a prototype of dual phase (liquid-vapor) argon TPC (ProtoDUNE-DP) in 2019-2020.", "sources": ["src:rc-cern-ep-news-dune-prototypes"], "start": "2020", "status": "completed", "verified_at": "2026-10-25"}]`
- `/notes`
  - old: `["True start and end dates and the liquid argon mass are unresolved; only the DUNE FD TDR Vol. I description could be fetched. The interval's `start: 2020` is the TDR's publication year, used as a evidence bound (see intervals[0].note), not a sourced construction date."]`
  - new: `["The liquid argon mass is not stated in the sources consulted. Start and end are known to the year only (2019 to 2020), from the CERN newsletter.", "The CERN newsletter says that new solutions emerged from the ProtoDUNE-SP and ProtoDUNE-DP work for the second DUNE far detector module, which uses a vertical-drift layout, and that signal amplification in the gas phase was found not to be required."]`
- `/placements/0/end`
  - old: `null`
  - new: `"2020"`
- `/placements/0/locator`
  - old: `"Vol. I, figure caption, §1.3.2"`
  - new: `"CERN EP department newsletter, article 'DUNE prototype activities at the Neutrino Platform' (undated; tagged March 2022 - May 2022), paragraph beginning \"NP02, the twin cryostat of NP04\""`
- `/placements/0/note`
  - old: `"Installed alongside ProtoDUNE-SP in the CERN Neutrino Platform hall in the CERN North Area; no installation date sourced."`
  - new: `"Installed in the NP02 cryostat, the twin of the ProtoDUNE-SP cryostat, in the CERN Neutrino Platform hall in the CERN North Area (also shown in a figure caption of DUNE FD TDR Vol. I, §1.3.2). The CERN article gives the hosting period at year precision only."`
- `/placements/0/quote`
  - old: `"ProtoDUNE-SP and ProtoDUNE-DP cryostats in the CERN Neutrino Platform in CERN ’s North Area."`
  - new: `"NP02, the twin cryostat of NP04, hosted a prototype of dual phase (liquid-vapor) argon TPC (ProtoDUNE-DP) in 2019-2020."`
- `/placements/0/sources`
  - old: `["src:dune-fd-tdr-vol-1"]`
  - new: `["src:rc-cern-ep-news-dune-prototypes", "src:dune-fd-tdr-vol-1"]`
- `/placements/0/start`
  - old: `null`
  - new: `"2019"`
- `/placements/0/verified_at`
  - old: `"2026-09-16"`
  - new: `"2026-10-25"`
- `/sources`
  - old: `["src:dune-fd-tdr-vol-1", "src:dune-cern-neutrino-platform-page"]`
  - new: `["src:dune-fd-tdr-vol-1", "src:dune-cern-neutrino-platform-page", "src:rc-cern-ep-news-dune-prototypes"]`

### data/atlas/facilities/fermilab.json

- `/links/website/locator`
  - old: `"<absent>"`
  - new: `"home page; page title \"Fermilab | Home\", headline \"Fermilab is America's particle physics and accelerator laboratory\""`
- `/links/website/note`
  - old: `"www.fnal.gov could not be retrieved in this session (HTTP 403); the LBNF/DUNE project site is the fetched official Fermilab page."`
  - new: `"The laboratory's own site. Automated requests to www.fnal.gov are refused with HTTP 403, so the page was read in a web browser on 2026-10-25. The LBNF/DUNE project site (lbnf-dune.fnal.gov) is a separate project site and is not used as the laboratory's website."`
- `/links/website/sources/0`
  - old: `"src:fermilab-lbnf-dune-site"`
  - new: `"src:rc-fermilab-official-site"`
- `/links/website/value`
  - old: `"https://lbnf-dune.fnal.gov/"`
  - new: `"https://www.fnal.gov/"`
- `/links/website/verified_at`
  - old: `"2026-09-16"`
  - new: `"2026-10-25"`
- `/notes/0`
  - old: `"fnal.gov and history.fnal.gov returned HTTP 403 to every fetch attempt in this session; history and operator facts are taken from news.fnal.gov, lbnf-dune.fnal.gov, pip2.fnal.gov and the DUNE TDR."`
  - new: `"Automated requests to www.fnal.gov and history.fnal.gov were refused with HTTP 403 when first tried (2026-09-16), so history and operator facts are taken from news.fnal.gov, the LBNF/DUNE and PIP-II project sites, the laboratory's Leadership and Organization page and the DUNE TDR. The home page was read in a web browser on 2026-10-25."`
- `/operator_text/note`
  - old: `"Current operator. DOE awarded the management and operating contract to Fermi Forward Discovery Group, LLC (FFDG): \"The successful offeror is Fermi Forward Discovery Group, LLC (FFDG).\" and \"The new contractor will assume operations effective January 1, 2025\" (DOE Office of Science, 1 October 2024). Before that date the contractor was Fermi Research Alliance, LLC (DUNE Far Detector TDR, Vol. I, acknowledgements, PDF p. 2: \"Fermilab is managed by Fermi Research Alliance, LLC (FRA), acting under Contract No. DE-AC02-07CH11359.\"). REPLACED 2026-10-25: the earlier value named FRA, quoted from the DUNE TDR (a 2020 PDF, not the abstract page it was cited to), which is out of date."`
  - new: `"Current operator. DOE awarded the management and operating contract to Fermi Forward Discovery Group, LLC (FFDG): \"The successful offeror is Fermi Forward Discovery Group, LLC (FFDG).\" and \"The new contractor will assume operations effective January 1, 2025\" (DOE Office of Science, 1 October 2024). Before that date the contractor was Fermi Research Alliance, LLC (DUNE Far Detector TDR, Vol. I, acknowledgements, PDF p. 2: \"Fermilab is managed by Fermi Research Alliance, LLC (FRA), acting under Contract No. DE-AC02-07CH11359.\"). The DUNE TDR (2020) predates the change of contractor."`
- `/sources`
  - old: `["src:fermilab-lbnf-dune-site", "src:fermilab-news-birth-of-fermilab-2017", "src:dune-fd-tdr-vol-1", "src:fermilab-ror-record"]`
  - new: `["src:fermilab-lbnf-dune-site", "src:fermilab-news-birth-of-fermilab-2017", "src:dune-fd-tdr-vol-1", "src:fermilab-ror-record", "src:rc-fermilab-official-site"]`


---

## Appendix B. Fermilab context features, CDF/D0 halls (F15, F11)

# fnal-geo log (HEP Atlas release-candidate data stream, 2026-10-25)

Files edited (only these): `data/atlas/geometry/fermilab-*.json` (23 of the 34 records), `data/atlas/maps/fermilab.json`,
and 8 new source records `data/atlas/sources/rc-*.json` (listed below). Nothing committed. Validator: 0 errors (1603 warnings, all
of them present before or from other agents' files; no new warning from my files). Quote check (`--only fermilab`): 65 verbatim,
3 segments (the three pre-existing ones: a0-reference-point, main-injector-ring check 0, mc1-building depth), 1 skipped (a
geocoder site record, not mine); every quote I added is verbatim. `tests/test_atlas_geometry_data.py`: 8 passed.

## How the pages were read
`WebFetch` returned HTTP 403 for history.fnal.gov, www.fnal.gov/pub/ferminews and publicpoint.fnal.gov, and could not parse PDFs. Those
pages were read with a plain HTTPS request (browser User-Agent, the same way `scripts/atlas_quote_check.py` fetches them) and text
extraction in the scratch folder; the quote-check script then re-fetched and confirmed every quote on its own. news.fnal.gov
(2017 and 2018 ICARUS pages) and energy.gov (CX-010394) were also read with `WebFetch` / the same request. The Main Injector TDR
(FERMILAB-DESIGN-1994-01) and the PAC 1999 paper were read from the shared quote-check cache (fetched 2026-10-25 earlier today);
the PAC 1999 PDF was also re-read directly.

## F15: dated windows for context features (`valid`)
`valid` was extended beyond the bare `{start, end}` of the contract with `sources`, `verified_at`, `confidence`, `quote`/`locator`
and `note` so that the window carries its own evidence (the validator and build read only `start`/`end`; the quote checker reads
`quote`). If the lead prefers bare windows, delete those five extra keys and keep the plain statement already in `notes[]`.
The reader-facing statement is in each record's `notes[]`.

Rule used everywhere: a feature is drawn from the first date at which a fetched source shows the structure standing; where a
source gives only a range, the later, certain end of it, and the record says so. "Silence" (not drawing) was preferred to drawing a
structure before a source shows it.

| Feature | `valid.start` | confidence | Basis |
| --- | --- | --- | --- |
| geometry:fermilab-wilson-hall | 1973 | approximate | Fermilab History and Archives, "A Brief History of Fermilab" (https://history.fnal.gov/history-fermi.html): "He guided the design of the distinctive high-rise Wilson Hall, which houses most of the lab’s offices and was completed in 1973." Same site, "Art and Architecture" (https://history.fnal.gov/historical/art_arch/art_architecture.html): "it was built between 1971 and 1974" and "Shortly after the completion of Wilson Hall in 1973"; "The Last Bucket of Cement Goes Up" (https://history.fnal.gov/historical/art_arch/last_bucket.html): topping-out Thursday, April 5, 1973, NAL takes over the building "later this year". The lab was dedicated May 11, 1974. The lead's "groundbreaking 1968" is the laboratory's/Linac groundbreaking (December 1, 1968), not the building's; the pages date Wilson Hall's construction to 1971-1974 (a reprinted 1971 caption in work_proceeds.html says caisson construction began late in 1970). |
| geometry:fermilab-mi-62-service-building | 1997 | derived | PAC 1999 paper MOCL3 (https://epaper.kek.jp/p99/PAPERS/MOCL3.PDF) section 1: "Completion of the Main Injector ring civil construction occurred in 1997"; Main Injector TDR (Aug 1994) ch. 4: "The MI-52 and 62 service buildings (WBS 1.2.2.4) have the same dimensions and typical features except for the following variations." (MI-62 described in the future tense; MI-60 "was the first building ready for beneficial occupancy"); groundbreaking "March 22, 1993" (https://history.fnal.gov/historical/accelerator/accelerator_history.html). No source dates MI-62 itself. Not 1993 because the 1994 TDR still describes MI-62 as to be built. |
| geometry:fermilab-mi-infield | 1997 | derived | FermiNews, September 2003, p. 5 (https://www.fnal.gov/pub/ferminews/ferminews03-09-01/p5.html): "After we planted in 1992, the wetlands area was monitored by the Corps of Engineers for five years. In 1997, the mitigated area was well on its way, and the Corps agreed that the wetlands were good enough to close the permit." and replacement wetland "in the middle of the Main Injector ring"; PAC 1999 (ring civil complete 1997); groundbreaking 22 March 1993. No source gives the grassland's age; I did not use the MI groundbreaking (1993-03-22) as the start because the ring interior was regraded 1992-97. Using 1993-03-22 instead is a one-string change. |
| geometry:fermilab-mc2-building | 2019-08 | uncertain | No source names MC-2 or dates it (five web searches, DOE CX-010394, Muon Campus overview arXiv:2208.02889 HTML, g-2 TDR/Mu2e hits). Only evidence: OSM way 720556732 history, version 1 created 2019-08-31T16:47:52Z (https://api.openstreetmap.org/api/0.6/way/720556732/history) = upper bound; the "MC-" series dates from the Muon Campus program (DOE CX-010394, dated 2012-06-12, "establish a Fermilab Muon Campus Program", names MC-1, no MC-2) = lower bound 2012-06. Drawn from the upper bound. Using 2012-06 instead (lower bound) is a one-string change. |
| geometry:fermilab-campus-boundary | 1966-12-07 | approximate | "The AEC chose a 6,800 acre site at Weston, Illinois, on December 7, 1966." (brief history). OSM polygon area computed from its coordinates: 27.59 km2 = 6,817 acres (0.25 % from 6,800). |
| geometry:fermilab-icarus-hall | 2017-07 | approximate | Audit finding (not on the lead's list): the hall inherited detector:icarus-t600's lifecycle, which starts 2010-05 at Gran Sasso, so the Fermilab building was drawn as "active" 2010-2013 and "upgrade" 2014-2017. Fermilab News 2017-07-25 (https://news.fnal.gov/2017/07/icarus-detector-scheduled-arrive-fermilab-tomorrow/): "The 120-ton ICARUS detector will be located outside of the Short-Baseline Neutrino Far Detector building for the next couple of months until it is installed inside the new ICARUS building."; Fermilab News 2018-08-16 (https://news.fnal.gov/2018/08/icarus-neutrino-detector-installed-in-new-fermilab-home/): "a recently completed building". The built bundle now clips the entity statuses to 2017-07 on (construction 2017-07, commissioning 2020-02, active 2021-11), checked by building into a temporary directory. |

## Audit of all 34 Fermilab features (feature, decision, source)
Context features (`entity_id` null): see the first five rows above.
Features with an entity inherit the entity's lifecycle (`state_segments`) and need no window of their own; checked against the
entity intervals:

| Feature | Decision |
| --- | --- |
| a0-reference-point, tevatron-ring | inherit accelerator:fermilab-tevatron (active 1985-12..2011); ring has `valid.end` 2011. Unchanged. |
| booster-ring, booster-extraction-point | inherit accelerator:fermilab-booster (commissioning 1970-12-21). Unchanged. |
| linac | inherits accelerator:fermilab-linac (construction 1968-12-01). Unchanged. |
| main-injector-ring, recycler-ring | inherit the MI (approved 1991-10, construction 1993-03-22) and the Recycler (commissioning 1999-05). Unchanged (the MI ring is drawn from 1991-10 with the status "approved"). |
| cdf-hall, d0-hall, miniboone-hall, minos-near-surface, minos-near-hall | already carry their own `valid` windows. Unchanged except wording. |
| nova-near-surface, microboone-hall, sbnd-point, minos-near-detector-position, numi-* (6 features), numi-direction, bnb-beamline, bnb-target, lbnf-direction | inherit the entity lifecycle; none is drawn before its entity exists. Unchanged except wording. |
| mc1-building | inherits detector:muon-g-2 (construction 2013..2014-07). Unchanged. Observation: the entity has no state between 2014-07 and 2017-05-31, so the building is not drawn in those years although it stood (entity data, not mine). |
| seaquest-point | inherits detector:seaquest, whose only interval is "completed" from 2025-12; so the NM4 point is drawn only from 2025-12 on, not in the years SeaQuest ran. Unchanged (entity data, not mine). |
| bnb-beamline, bnb-target | entity beamline:bnb is "active" from 2008 only, although the MiniBooNE hall is drawn from 2002-09. Unchanged (entity data, not mine). |

## Other fixes made while rewriting process language
Stale statements corrected (they described a state of the data that no longer holds): CDF/D0 notes said the site records "still carry a
coarse 3 km campus point" to be corrected (the site records now carry the hall centroid, 40 m), and that the hall centroid "anchors the
Tevatron ring's derived centre" (the ring is now placed from the Main Injector TDR; the halls only lie just outside it); MC-1 note
(same site-point statement); minos-near-surface note said the cavern was not drawn (it is, geometry:fermilab-minos-near-hall);
miniboone note said the BNB target was unlocated (a derived target is drawn); map `summary` and `notes[0]` said the Main Injector
was placed "on the Indian Creek Road offset; 30 m" and that the NuMI/BNB features were all derived from OSM buildings and that SBND
was unlocated, and that no maps exist for Soudan and SURF (both exist). The unsourced Delivery Ring shape/circumference ("roughly
triangular, ~505 m ... by the task brief") was dropped from the Mu2e backlog because no source supports it. The unverified secondary
quotes in the Tevatron note (Wikipedia, "1000 m radius synchrotron") were reduced to a plain statement that secondary sources call
the ring circular, because they were never re-fetched.

## New source records (all `retrieval: full_text`, `accessed: 2026-10-25`)
- src:rc-fnal-history-brief-history (official_facility_site) https://history.fnal.gov/history-fermi.html
- src:rc-fnal-history-art-architecture (official_facility_site) https://history.fnal.gov/historical/art_arch/art_architecture.html
- src:rc-fnal-history-last-bucket (official_facility_site, date 1973-04-12) https://history.fnal.gov/historical/art_arch/last_bucket.html
- src:rc-fnal-ferminews-2003-09-main-injector-wetlands (press_release, 2003-09-01) https://www.fnal.gov/pub/ferminews/ferminews03-09-01/p5.html
- src:rc-fnal-news-2017-07-icarus-arrival (press_release, 2017-07-25)
- src:rc-fnal-news-2018-08-icarus-installed (press_release, 2018-08-16)
- src:rc-doe-cx-010394-fermilab-muon-campus (project_document, 2012-06-12) https://www.energy.gov/nepa/articles/cx-010394-categorical-exclusion-determination
- src:rc-osm-way-720556732-history (openstreetmap) https://www.openstreetmap.org/way/720556732/history
Existing records reused unchanged: src:rv-fnal-mi-commissioning-pac99, src:fermilab-geo-mi-tdr-1994, src:rv-fnal-history-accelerator-history
(its `accessed` is already 2026-10-25; the quote "The lab broke ground on the Main Injector on March 22, 1993." was re-read today).
Note for the lead: the existing record src:fermilab-geo-mi-dedication-1999 still has "see geometry worklog" and "this session" wording in its
`excerpt` (not my file).

## Every change, by file
Format: JSON pointer, old, new (long strings: only the changed span, marked `...`).

#### data/atlas/geometry/fermilab-wilson-hall.json

- `/valid`:
  - old: null
  - new: {"end": null, "start": "1973", "confidence": "approximate", "sources": ["src:rc-fnal-history-brief-history", "src:rc-fnal-history-art-architecture", "src:rc-fnal-history-last-bucket"], "verified_at": "2026-10-25", "quote": "He guided the design of the distinctive high-rise Wilson Hall, which houses most of the lab’s offices and was completed in 1973.", "locator": "Fermilab History and Archives: 'A Brief History of Fermilab' (paragraph on Robert Wilson); 'Art and Architecture', section 'Wilson Hall'; reprinted article 'The Last Bucket of Cement Goes Up' (topping-out, 5 April 1973)", "note": "The drawn window opens in the year the history pages give for completion; construction began in 1971."}
- `/notes`:
  - old: []
  - new: ["Fermilab History and Archives gives the completion of Wilson Hall as 1973 (\"was completed in 1973\"; \"Shortly after the completion of Wilson Hall in 1973\") and its construction span as 1971 to 1974 (\"it was built between 1971 and 1974\"). The sixteenth floor was topped out on 5 April 1973, and the laboratory was dedicated on 11 May 1974. The building is drawn from 1973, the year the pages give for completion; the foundation and first-phase work of 1971-72 is not drawn."]
- `/geometry/note`:
  - old: "Context building; entity_id null (Wilson Hall is not itself an atlas entity)."
  - new: "Context building: no atlas entity depicts Wilson Hall. The footprint is the OpenStreetMap outline of the completed building."
- `/summary/plain`:
  - old: "Context building; entity_id null (Wilson Hall is not itself an atlas entity)."
  - new: "Wilson Hall, Fermilab's high-rise laboratory and office building near the centre of the map, drawn as a context building from 1973, the year Fermilab's history pages give for its completion."
- `/sources/-`: added `src:rc-fnal-history-brief-history`
- `/sources/-`: added `src:rc-fnal-history-art-architecture`
- `/sources/-`: added `src:rc-fnal-history-last-bucket`

#### data/atlas/geometry/fermilab-campus-boundary.json

- `/valid`:
  - old: null
  - new: {"end": null, "start": "1966-12-07", "confidence": "approximate", "sources": ["src:rc-fnal-history-brief-history"], "verified_at": "2026-10-25", "quote": "The AEC chose a 6,800 acre site at Weston, Illinois, on December 7, 1966.", "locator": "Fermilab History and Archives, 'A Brief History of Fermilab'; OSM way/31974155 polygon area computed from its coordinates (27.6 km2, about 6,817 acres)", "note": "Start is the date the 6,800-acre site was chosen; the drawn outline is the 2026 OpenStreetMap polygon, whose area agrees with that acreage."}
- `/notes`:
  - old: []
  - new: ["The Atomic Energy Commission chose a 6,800-acre site at Weston, Illinois, on 7 December 1966 (Fermilab History and Archives). The OpenStreetMap outline drawn here encloses about 6,817 acres (computed from its coordinates), so it is drawn from that date. It is the outline as mapped in 2026, not a survey of the boundary in earlier years."]
- `/geometry/note`:
  - old: "OpenStreetMap-alone representation; caps at 'approximate' confidence per contract rules even though the tracing itself is precise. Context feature only (entity_id null); shown for orientation, not a claim about any drawn accelerator or detector."
  - new: "Context feature only: no atlas entity depicts the campus boundary, and it is shown for orientation. OpenStreetMap alone yields at most approximate confidence, even though the tracing is precise."
- `/summary/plain`:
  - old: "OpenStreetMap-alone representation; caps at 'approximate' confidence per contract rules even though the tracing itself is precise. Context feature only (entity_id null); shown for orientation, not ..."
  - new: "The outline of the Fermilab site (about 6,800 acres) as mapped in OpenStreetMap, drawn for orientation from the date the site was chosen, 7 December 1966."
- `/sources/-`: added `src:rc-fnal-history-brief-history`

#### data/atlas/geometry/fermilab-mi-62-service-building.json

- `/valid`:
  - old: null
  - new: {"end": null, "start": "1997", "confidence": "derived", "sources": ["src:rv-fnal-mi-commissioning-pac99", "src:fermilab-geo-mi-tdr-1994", "src:rv-fnal-history-accelerator-history"], "verified_at": "2026-10-25", "quote": "Completion of the Main Injector ring civil construction occurred in 1997", "locator": "PAC 1999 paper MOCL3, section 1 (Introduction); Main Injector Technical Design Handbook (August 1994), chapter 4 'Service Buildings' (WBS 1.2.2.4: 'The MI-52 and 62 service buildings'); Fermilab History and Archives, 'Accelerator History', section 'Main Injector' (groundbreaking 22 March 1993)", "note": "Start is the year the ring's civil construction was complete; this building's own completion date is not published in the sources consulted."}
- `/notes`:
  - old: []
  - new: ["No source consulted (checked 2026-10-25) gives the completion date of this building. The Main Injector Technical Design Handbook (August 1994) lists the MI-52 and MI-62 service buildings among the project's eleven service buildings and describes MI-62 in the future tense, and the 1999 commissioning paper says the ring's civil construction was complete in 1997 (groundbreaking was on 22 March 1993). The building is therefore drawn from 1997; it may have stood earlier."]
- `/method` (changed span only):
  - old: "... MI-62 stands at the MI-62 straight section. Release pass (gaps stream): with the ring now placed from the TDR's own site coordinates, the building lies 14.7 m from the tunnel and 53.6 m from the centre of the MI-62 straight section (it stood 7.4 m from the earlier, road-fitted ring, which was displaced 54 m); a service building need not stand over the mid..."
  - new: "... MI-62 stands at the MI-62 straight section. With the ring placed from the TDR's own site coordinates (placement revised 2026-10-25), the building lies 14.7 m from the tunnel and 53.6 m from the centre of the MI-62 straight section; it stood 7.4 m from the earlier, road-fitted ring, which was displaced 54 m. A service building need not stand over the mid..."
- `/summary/plain`:
  - old: "The service building at the MI-62 straight section of the Main Injector."
  - new: "The service building at the MI-62 straight section of the Main Injector, drawn from 1997, when the ring's civil construction was complete."
- `/sources/-`: added `src:rv-fnal-mi-commissioning-pac99`
- `/sources/-`: added `src:rv-fnal-history-accelerator-history`

#### data/atlas/geometry/fermilab-mi-infield.json

- `/valid`:
  - old: null
  - new: {"end": null, "start": "1997", "confidence": "derived", "sources": ["src:rc-fnal-ferminews-2003-09-main-injector-wetlands", "src:rv-fnal-mi-commissioning-pac99", "src:rv-fnal-history-accelerator-history"], "verified_at": "2026-10-25", "quote": "After we planted in 1992, the wetlands area was monitored by the Corps of Engineers for five years. In 1997, the mitigated area was well on its way, and the Corps agreed that the wetlands were good enough to close the permit.", "locator": "FermiNews, September 2003, p. 5 (restored sedge wetlands inside the Main Injector ring); PAC 1999 paper MOCL3, section 1 (ring civil construction complete in 1997); Fermilab History and Archives, 'Accelerator History' (Main Injector groundbreaking 22 March 1993)", "note": "Start is the year the ring's civil construction was complete and the replacement wetland inside the ring was accepted; no source gives the age of this grassland."}
- `/notes`:
  - old: []
  - new: ["No source consulted (checked 2026-10-25) gives the age of this grassland. It lies inside the Main Injector ring, whose civil construction began with the groundbreaking of 22 March 1993 and was complete in 1997. Fermilab's September 2003 newsletter says replacement wetland was built \"in the middle of the Main Injector ring\", planted in 1992, and that the Army Corps of Engineers closed its permit in 1997. The polygon is therefore drawn from 1997; farmland or earlier vegetation at this spot is not drawn."]
- `/geometry/note`:
  - old: "Context feature only (entity_id null): shown for orientation because it sits inside the undrawn Main Injector/Recycler ring, but it is explicitly NOT a representation of the ring/tunnel -- see map.unlocated for accelerator:fermilab-main-injector and accelerator:fermilab-recycler, and the geometry worklog 'Main Injector infield' section."
  - new: "Context feature only: shown for orientation because it lies inside the Main Injector/Recycler ring. It is not a representation of the ring or its tunnel, which are drawn separately (geometry:fermilab-main-injector-ring and geometry:fermilab-recycler-ring)."
- `/method`:
  - old: "OpenStreetMap way 1167765305 (natural=grassland), traced verbatim, 116 vertices. Investigated as a candidate Main Injector infield proxy per the research brief, then rejected as a ring proxy: its bounding span (1038 m N-S x 860 m E-W, matching the integrator's earlier estimate) is roughly the right order of magnitude for a ~3.3 km-circumference oval, but its own perimeter (5548 m) is 67% longer than the Main Injector's sourced circumference (3319.4 m, src:fermilab-geo-mi-tdr-1994) -- it traces an irregular natural-grassland/wetland boundary, not a clean racetrack inset, and cannot be used to derive or validate the ring's shape."
  - new: "OpenStreetMap way 1167765305 (natural=grassland), traced verbatim, 116 vertices. Considered as a proxy for the Main Injector ring and rejected: its bounding span (1038 m N-S x 860 m E-W) is of the right order of magnitude for a ~3.3 km-circumference oval, but its own perimeter (5548 m) is 67% longer than the Main Injector's sourced circumference (3319.4 m, src:fermilab-geo-mi-tdr-1994), and it traces an irregular natural-grassland/wetland boundary, not a clean racetrack inset, so it cannot be used to derive or validate the ring's shape."
- `/summary/plain`:
  - old: "Context feature only (entity_id null): shown for orientation because it sits inside the undrawn Main Injector/Recycler ring, but it is explicitly NOT a representation of the ring/tunnel -- see map...."
  - new: "A grassland polygon (OpenStreetMap) inside the Main Injector ring, drawn from 1997 for orientation only; it is not the ring or its tunnel."
- `/sources/-`: added `src:rc-fnal-ferminews-2003-09-main-injector-wetlands`
- `/sources/-`: added `src:rv-fnal-mi-commissioning-pac99`
- `/sources/-`: added `src:rv-fnal-history-accelerator-history`

#### data/atlas/geometry/fermilab-mc2-building.json

- `/valid`:
  - old: null
  - new: {"end": null, "start": "2019-08", "confidence": "uncertain", "sources": ["src:rc-osm-way-720556732-history", "src:rc-doe-cx-010394-fermilab-muon-campus"], "verified_at": "2026-10-25", "locator": "OSM way/720556732 history (api.openstreetmap.org/api/0.6/way/720556732/history): version 1 created 2019-08-31T16:47:52Z, changeset 73953436; DOE CX-010394, dated 2012-06-12 (Muon Campus program and the MC-1 Building; no MC-2)", "note": "Start is the building's first appearance in OpenStreetMap, an upper bound on its construction date; its actual construction date is not established."}
- `/notes`:
  - old: ["Integrator (2026-09-21): `site_id` cleared — the identification of MC-2 with the Mu2e hall is unconfirmed (see the map's unlocated row for detector:mu2e), so this context building must not stand for site:fermilab-mu2e-hall."]
  - new: ["No source consulted (checked 2026-10-25) names this building or gives its construction date. Its label belongs to the Muon Campus building series; the MC-1 building was proposed when the Muon Campus program was set up in 2012 (U.S. Department of Energy determination CX-010394, dated 12 June 2012, which does not mention MC-2). The earliest evidence that the building stands is its first appearance in OpenStreetMap on 31 August 2019, so it is drawn from August 2019; that date is when it was traced, not when it was built.", "No site is attached: the identification of MC-2 with the Mu2e hall is not confirmed (see the map's unlocated entry for detector:mu2e), so this building is not drawn as site:fermilab-mu2e-hall."]
- `/method`:
  - old: "OpenStreetMap way 720556732 'MC-2' footprint, traced verbatim, 84 m from MC-1 (way 720556725, confirmed as the Muon g-2 building). Drawn as a context feature (entity_id null, not detector:mu2e) because no source fetched this session confirms MC-2 is specifically the Mu2e hall -- the MC-1/MC-2 naming pattern and Muon Campus adjacency are suggestive but not sourced; a WebSearch and two WebFetch attempts (arXiv:2208.02889 'Muon Campus at Fermilab', both HTML and PDF) found no fetchable text naming MC-2."
  - new: "OpenStreetMap way 720556732 'MC-2' footprint, traced verbatim, 84 m from MC-1 (way 720556725, confirmed as the Muon g-2 building). Drawn as a context feature (entity_id null, not detector:mu2e) because no source consulted confirms MC-2 is specifically the Mu2e hall; the MC-1/MC-2 naming pattern and Muon Campus adjacency are suggestive but not sourced. As of 2026-09-18 a web search and two attempts to read the arXiv paper 'Muon Campus at Fermilab' (arXiv:2208.02889, HTML and PDF) found no text naming MC-2, and its HTML text contains no mention of it on 2026-10-25."
- `/summary/plain`:
  - old: "Candidate anchor for detector:mu2e's backlog (see map.unlocated), not a claim that this is confirmed to be the Mu2e hall."
  - new: "A building labelled MC-2 in OpenStreetMap, 84 m from the MC-1 (Muon g-2) building on the Fermilab Muon Campus. No source consulted identifies it or dates it; it is drawn from August 2019, when it first appears in OpenStreetMap. It is not confirmed to be the Mu2e hall."
- `/geometry/note`:
  - old: "Candidate anchor for detector:mu2e's backlog (see map.unlocated), not a claim that this is confirmed to be the Mu2e hall."
  - new: "Context building and a candidate anchor for the Mu2e entry in the map's unlocated list; it is not confirmed to be the Mu2e hall."
- `/sources/-`: added `src:rc-osm-way-720556732-history`
- `/sources/-`: added `src:rc-doe-cx-010394-fermilab-muon-campus`

#### data/atlas/geometry/fermilab-icarus-hall.json

- `/valid`:
  - old: null
  - new: {"end": null, "start": "2017-07", "confidence": "approximate", "sources": ["src:rc-fnal-news-2017-07-icarus-arrival", "src:rc-fnal-news-2018-08-icarus-installed"], "verified_at": "2026-10-25", "quote": "The 120-ton ICARUS detector will be located outside of the Short-Baseline Neutrino Far Detector building for the next couple of months until it is installed inside the new ICARUS building.", "locator": "Fermilab News, 2017-07-25, 'ICARUS detector scheduled to arrive at Fermilab today'; Fermilab News, 2018-08-16, 'ICARUS neutrino detector installed in new Fermilab home' ('a recently completed building')", "note": "Start is the first date a source describes the building as standing; its completion date is not given in the pages consulted."}
- `/notes`:
  - old: ["QA pass (2026-09-21): removed the `valid: {start: '2017-07', end: null}` window a previous pass set -- a preventive fix for a latent bug in hepgraph.atlas.build._feature_segments(): any `valid` dict with a non-null `start` and `end: null` hard-codes `status: 'active'` through build day regardless of the entity's real status, bypassing state_segments entirely. Currently harmless because detector:icarus-t600 genuinely is 'active' today, but this pattern produced a live false-'active' claim on three other records (geometry:lhc-tunnel-ring, geometry:fermilab-mc1-building, geometry:fermilab-microboone-hall) fixed the same way in this pass -- see docs/atlas-worklog/REVIEW_geometry_qa.md."]
  - new: ["The detector ran at Gran Sasso from 2010 to 2013 and was overhauled at CERN from 2014, so no Fermilab building stood for it in those years; the 2015 short-baseline proposal describes it as \"a new building\". The building is drawn from July 2017, when Fermilab News describes the detector arriving to be placed outside \"the Short-Baseline Neutrino Far Detector building\" until it is installed \"inside the new ICARUS building\"; the detector moved in on 14 August 2018 (\"a recently completed building\"). The building's own completion date is not given in the pages consulted."]
- `/geometry/note`:
  - old: "A QA pass should double-check this identification; no OSM tag names the building, though the positional match is strong and it is the only plausible candidate found in this area."
  - new: "No OpenStreetMap tag names the building; the positional match (603.1 m from the derived BNB target against the sourced 600 m, 0.7 degrees off the beam axis) is strong, and it is the only plausible candidate found in this area."
- `/summary/plain`:
  - old: "A QA pass should double-check this identification; no OSM tag names the building, though the positional match is strong and it is the only plausible candidate found in this area."
  - new: "The building that houses the ICARUS-T600 neutrino detector at Fermilab, identified by its position 600 m from the Booster Neutrino Beam target because no OpenStreetMap tag names it; drawn from July 2017."
- `/sources/-`: added `src:rc-fnal-news-2017-07-icarus-arrival`
- `/sources/-`: added `src:rc-fnal-news-2018-08-icarus-installed`

#### data/atlas/geometry/fermilab-cdf-hall.json

- `/geometry/note`:
  - old: "This is the surface building footprint, not a survey of the underground collision point. Its centroid also anchors the Tevatron ring's derived centre (see geometry:fermilab-tevatron-ring checks). The existing site record site:fermilab-cdf-collision-hall-b0 still carries a coarse 3 km campus point; this OSM position is a strictly better anchor and is flagged as a site coordinate correction in the geometry worklog for the integrator to apply."
  - new: "This is the surface building footprint, not a survey of the underground collision point. The Tevatron ring (geometry:fermilab-tevatron-ring) is placed independently of this footprint; the hall lies just outside the ring, as a surface building beside an underground collision hall should. The atlas site record site:fermilab-cdf-collision-hall-b0 now carries this footprint's centroid as its point (accuracy 40 m)."
- `/summary/plain`:
  - old: "This is the surface building footprint, not a survey of the underground collision point. Its centroid also anchors the Tevatron ring's derived centre (see geometry:fermilab-tevatron-ring checks). T..."
  - new: "The surface building (CDF Hall) at the Tevatron B0 straight section, above the CDF collision hall, from an OpenStreetMap footprint; drawn until October 2011."

#### data/atlas/geometry/fermilab-d0-hall.json

- `/geometry/note`:
  - old: "This is the surface building footprint, not a survey of the underground collision point. Its centroid also anchors the Tevatron ring's derived centre (see geometry:fermilab-tevatron-ring checks). The existing site record site:fermilab-d0-collision-hall still carries a coarse 3 km campus point; this OSM position is a strictly better anchor and is flagged as a site coordinate correction in the geometry worklog. This is also the first sourced coordinate found this session for the D0 hall at all -- the OSM Overpass probes the integrator ran earlier this session did not surface it (only CDF Hall); it was found by a dedicated name search for 'D0' within the campus bounding box."
  - new: "This is the surface building footprint, not a survey of the underground collision point. The Tevatron ring (geometry:fermilab-tevatron-ring) is placed independently of this footprint; the building lies just outside the ring, as a surface building beside an underground collision hall should. The atlas site record site:fermilab-d0-collision-hall now carries this footprint's centroid as its point (accuracy 40 m). As of 2026-09-18 this was the first sourced coordinate found for the D0 hall: an earlier OpenStreetMap query of the campus buildings returned only the CDF Hall, and this building was found by a name search for 'D0' within the campus bounding box."
- `/summary/plain`:
  - old: "This is the surface building footprint, not a survey of the underground collision point. Its centroid also anchors the Tevatron ring's derived centre (see geometry:fermilab-tevatron-ring checks). T..."
  - new: "The D0 Assembly Building at the Tevatron D0 straight section, above the D0 collision hall, from an OpenStreetMap footprint; drawn until December 2011."

#### data/atlas/geometry/fermilab-booster-ring.json

- `/method` (changed span only):
  - old: "...than the accelerator's own radius by 6-17 m. Haversine on R=6371008.8 m (schema.great_circle_m). Release pass (gaps stream, 2026-10-25): the first point of the 8 GeV line in the Ma..."
  - new: "...than the accelerator's own radius by 6-17 m. Distances are great-circle on a sphere of radius 6371008.8 m. Check added 2026-10-25: the first point of the 8 GeV line in the Ma..."
- `/notes/0`:
  - old: "Release pass (gaps stream): extraction-point check added; accuracy tightened to 10 m. Shape and centre unchanged."
  - new: "On 2026-10-25 an extraction-point check was added (see method) and accuracy tightened from 30 m to 10 m; shape and centre unchanged."

#### data/atlas/geometry/fermilab-bnb-target.json

- `/summary/plain`:
  - old: "Accuracy dominated by OSM building accuracy (~8 m each) plus the assumption of exact colinearity of target-LArTF-MiniBooNE (supported to within 1.3 m by the target-to-LArTF check below). No sourced..."
  - new: "A derived point for the Booster Neutrino Beam target, placed 541 m upstream of the MiniBooNE building along the line through the MiniBooNE and LArTF buildings; no published coordinate exists for the target itself."

#### data/atlas/geometry/fermilab-lbnf-direction.json

- `/summary/plain`:
  - old: "Not a physical structure; drawn and labelled as an inferred direction only. The true LBNF beam also points down (about 5.3 degrees below horizontal per src:dune-nd-cdr) toward SUR..."
  - new: "An inferred direction (great-circle bearing 287.7 degrees) from the Fermilab main-campus point toward the DUNE far detector at SURF in South Dakota. It is not a physical structure; the real beam also points downward, which this plan view cannot show."

#### data/atlas/geometry/fermilab-linac.json

- `/geometry/note`:
  - old: "No sourced length exists for this specific 400 MeV Linac (only its energy is sourced), so no length check is possible; confidence stays approximate per the contract's rule for an uncheckable shape."
  - new: "No sourced length exists for this specific 400 MeV Linac (only its energy is sourced), so no length check is possible and confidence stays approximate."
- `/summary/plain`:
  - old: "No sourced length exists for this specific 400 MeV Linac (only its energy is sourced), so no length check is possible; confidence stays approximate per the contract's rule for an uncheckable shape."
  - new: "An approximate line along the buildings that house the 400 MeV Linac (OpenStreetMap 'Linac Gallery' and 'LINAC-II'); no source gives the Linac's length, so the line is not checked against one."

#### data/atlas/geometry/fermilab-main-injector-ring.json

- `/method` (changed span only):
  - old: "...th the TDR's own published site coordinates (release pass, gaps stream); the ring is not traced in OSM. (1) Lattice..."
  - new: "...th the TDR's own published site coordinates (placement revised 2026-10-25); the ring is not traced in OSM. (1) Lattice..."
- `/method` (changed span only):
  - old: "...4 m, 0.06 % below the TDR circumference (the validator's sphere is smaller than the ellipsoid here). The tunnel is drawn from the design lattic..."
  - new: "...4 m, 0.06 % below the TDR circumference (the spherical earth model used for distances here is smaller than the ellipsoid). The tunnel is drawn from the design lattic..."
- `/notes/1`:
  - old: "Release pass (gaps stream): the earlier placement (fit to an OSM service road) was displaced 38-74 m (mean 54 m) from the position implied by the TDR's own site coordinates and was replaced; the shape is unchanged."
  - new: "On 2026-10-25 the earlier placement (a fit to an OSM service road), which was displaced 38-74 m (mean 54 m) from the position implied by the design handbook's own site coordinates, was replaced by that position; the shape is unchanged."

#### data/atlas/geometry/fermilab-recycler-ring.json

- `/notes/0`:
  - old: "geometry-duplicate-shape (warning) with geometry:fermilab-main-injector-ring is intentional: the two machines share one enclosure, exactly as geometry:lep-tunnel / geometry:lhc-tunnel-ring on map:cern."
  - new: "Identical coordinates to geometry:fermilab-main-injector-ring are intentional: the two machines share one enclosure, exactly as geometry:lep-tunnel / geometry:lhc-tunnel-ring on map:cern."
- `/notes/1`:
  - old: "Release pass (gaps stream): coordinates replaced together with the Main Injector ring (placement from the TDR site coordinates)."
  - new: "Coordinates replaced on 2026-10-25 together with the Main Injector ring (placement from the design handbook's site coordinates)."
- `/geometry/note`:
  - old: "Identical coordinates to geometry:fermilab-main-injector-ring on purpose (one tunnel, two rings); the validator's geometry-duplicate-shape warning is expected."
  - new: "Identical coordinates to geometry:fermilab-main-injector-ring on purpose: the two rings share one tunnel, so the same path is drawn twice."

#### data/atlas/geometry/fermilab-mc1-building.json

- `/geometry/note`:
  - old: "The existing site record site:fermilab-mc-1-muon-campus carries a coarse 4 km geocoder point; this OSM building position is a strictly better anchor and is flagged as a site coordinate correction in the geometry worklog. The g-2 TDR states the experimental hall floor is 12 ft (3.66 m) below grade; recorded as this feature's own depth_m rather than a separate level since no other feature shares that level."
  - new: "The atlas site record site:fermilab-mc-1-muon-campus now carries this building's centroid as its point (accuracy 40 m). The g-2 TDR states the experimental hall floor is 12 ft (3.66 m) below grade; this is recorded as the feature's own depth_m rather than as a separate level, since no other feature shares that level."
- `/summary/plain`:
  - old: "The existing site record site:fermilab-mc-1-muon-campus carries a coarse 4 km geocoder point; this OSM building position is a strictly better anchor and is flagged as a site coordinate correction i..."
  - new: "The MC-1 building on the Fermilab Muon Campus, which houses the Muon g-2 storage ring, from an OpenStreetMap footprint."
- `/notes/0` (changed span only):
  - old: "QA pass (2026-09-21): removed the `valid: {start: '2013', end: null}` window a previous pass set. hepgraph.atlas.build._feature_segments() treats any `valid` dict with a non-null `start` as an open-ended 'active' window through build day whenever `end` is null, overriding the entity's own state_segments entirely -- so this feature was rendering `status: 'active'` in the built bundle today even though detector:muon-g-2's own sourced timeline says otherwise (status 'completed' at build day 2026-09-21, confirmed by directly testing hepgraph.atlas.build._Context.status_at_build/segments). Removing `valid` restores the intended fallback (contract SS3: 'without it the feature inherits the entity's timeline'). This is a pipeline-code gap (hepgraph/atlas/build.py `_feature_segments`), not unique to this record -- see docs/atlas-worklog/REVIEW_geometry_qa.md."
  - new: "(removed)"

#### data/atlas/geometry/fermilab-microboone-hall.json

- `/notes/0` (changed span only):
  - old: "QA pass (2026-09-21): removed the `valid: {start: '2015-10', end: null}` window a previous pass set. hepgraph.atlas.build._feature_segments() treats any `valid` dict with a non-null `start` as an open-ended 'active' window through build day whenever `end` is null, overriding the entity's own state_segments entirely -- so this feature was rendering `status: 'active'` in the built bundle today even though detector:microboone's own sourced timeline says otherwise (status 'completed' at build day 2026-09-21, confirmed by directly testing hepgraph.atlas.build._Context.status_at_build/segments). Removing `valid` restores the intended fallback (contract SS3: 'without it the feature inherits the entity's timeline'). This is a pipeline-code gap (hepgraph/atlas/build.py `_feature_segments`), not unique to this record -- see docs/atlas-worklog/REVIEW_geometry_qa.md."
  - new: "(removed)"

#### data/atlas/geometry/fermilab-miniboone-hall.json

- `/geometry/note`:
  - old: "MiniBooNE's sourced baseline (541 m from the BNB target, src:miniboone-detector-paper-2009) could not be used as an independent checks[] row this session because no sourced BNB target coordinate exists to check the distance against; the target/decay-pipe itself is unlocated (see map.unlocated for beamline:bnb)."
  - new: "MiniBooNE's sourced baseline (541 m from the BNB target, src:miniboone-detector-paper-2009) is not used as an independent check on this footprint: no published coordinate for the BNB target exists to measure against, and the drawn target (geometry:fermilab-bnb-target) is itself placed 541 m from this building using that baseline."
- `/summary/plain`:
  - old: "MiniBooNE's sourced baseline (541 m from the BNB target, src:miniboone-detector-paper-2009) could not be used as an independent checks[] row this session because no sourced BNB target coordinate ex..."
  - new: "The MiniBooNE Detector Building, from an OpenStreetMap footprint; drawn from September 2002 to 2019."

#### data/atlas/geometry/fermilab-minos-near-surface.json

- `/geometry/note`:
  - old: "This is the SURFACE access building only. The MINOS near-detector cavern itself is 100 m underground (src:minos-detector-paper-2008, 'a 100 m deep underground cavern, under a 225 mwe overburden'; see map level 'near-detector-caverns') and its horizontal offset from this surface point is not sourced this session, so the cavern is not drawn separately."
  - new: "This is the SURFACE access building only. The MINOS near-detector cavern itself is 100 m underground (src:minos-detector-paper-2008, 'a 100 m deep underground cavern, under a 225 mwe overburden'; see map level 'near-detector-caverns') and is drawn separately as the surveyed MINOS enclosure (geometry:fermilab-minos-near-hall)."
- `/notes/0`:
  - old: "Release pass (gaps stream): this is the surface (MINOS Service Building) footprint. The surveyed MINOS enclosure (geometry:fermilab-minos-near-hall) begins 79 m north-north-west of its centroid, in line with the MINOS NIM paper's statement that the detector cart was pulled about 80 m from the base of the access shaft into the hall."
  - new: "This is the surface (MINOS Service Building) footprint. The surveyed MINOS enclosure (geometry:fermilab-minos-near-hall) begins 79 m north-north-west of its centroid, in line with the MINOS NIM paper's statement that the detector cart was pulled about 80 m from the base of the access shaft into the hall."
- `/summary/plain`:
  - old: "This is the SURFACE access building only. The MINOS near-detector cavern itself is 100 m underground (src:minos-detector-paper-2008, 'a 100 m deep underground cavern, under a 225 mwe overburden'; s..."
  - new: "The surface access building (MINOS Service Building) above the MINOS near-detector hall, from an OpenStreetMap footprint; the underground hall is drawn separately."

#### data/atlas/geometry/fermilab-nova-near-surface.json

- `/geometry/note` (changed span only):
  - old: "...nderground detector is not drawn separately. Release pass (gaps stream): the earlier distance check against a derived..."
  - new: "...nderground detector is not drawn separately. On 2026-10-25 the earlier distance check against a derived..."
- `/notes/0`:
  - old: "QA pass (2026-09-21): removed the `valid: {start: '2014-02-06', end: null}` window a previous pass set -- a preventive fix for a latent bug in hepgraph.atlas.build._feature_segments(): any `valid` dict with a non-null `start` and `end: null` hard-codes `status: 'active'` through build day regardless of the entity's real status, bypassing state_segments entirely. Currently harmless because detector:nova-near-detector genuinely is 'active' today, but this pattern produced a live false-'active' claim on three other records (geometry:lhc-tunnel-ring, geometry:fermilab-mc1-building, geometry:fermilab-microboone-hall) fixed the same way in this pass -- see docs/atlas-worklog/REVIEW_geometry_qa.md."
  - new: "(removed)"
- `/notes/0`:
  - old: "Release pass (gaps stream): confidence lowered from verified to approximate and the distance check removed; see geometry note. The building lies 861 m from the surveyed NuMI target (TDR beam sheet) and 75 m from the MINOS surface building."
  - new: "Confidence lowered from verified to approximate on 2026-10-25 and the distance check removed (see the geometry note). The building lies 861 m from the surveyed NuMI target (TDR beam sheet) and 75 m from the MINOS surface building."
- `/summary/plain`:
  - old: "This is the SURFACE building only, per its own OSM name. The NOvA near detector is '100 m underground' (src:nova-arxiv-2025-monopole-search); its horizontal offset from this surface point is not so..."
  - new: "The NOvA near-detector surface building, from an OpenStreetMap footprint. It is the shaft building above the detector, not the detector itself, which is about 100 m underground."

#### data/atlas/geometry/fermilab-numi-direction.json

- `/geometry/note`:
  - old: "Not a physical structure; drawn and labelled as an inferred direction only, per contract rules. The NuMI beam also served the MINOS far detector at Soudan (1985-2016) on a nearly identical bearing (336.2 degrees vs 335.6 degrees here, both computed from the same near point) -- not drawn separately to avoid clutter. Release pass (gaps stream): the near point is now the surveyed NuMI target; the line starts exactly where geometry:fermilab-numi-beamline begins."
  - new: "Not a physical structure; drawn and labelled as an inferred direction only. The NuMI beam also served the MINOS far detector at Soudan (1985-2016) on a nearly identical bearing (336.2 degrees vs 335.6 degrees here, both computed from the same near point) -- not drawn separately to avoid clutter. Since 2026-10-25 the near point is the surveyed NuMI target; the line starts exactly where geometry:fermilab-numi-beamline begins."
- `/summary/plain`:
  - old: "Not a physical structure; drawn and labelled as an inferred direction only, per contract rules. The NuMI beam also served the MINOS far detector at Soudan (1985-2016) on a nearly identical bearing ..."
  - new: "An inferred direction (great-circle bearing 335.6 degrees) from the NuMI target toward the NOvA far detector at Ash River, Minnesota. It is not a physical structure."

#### data/atlas/geometry/fermilab-sbnd-point.json

- `/geometry/note`:
  - old: "accuracy_m widened to 30 m specifically to cover the ~17 m candidate-footprint scatter, on top of the usual OSM/derivation uncertainty. A QA pass or a source naming the specific building would let this become a proper 'hall' polygon."
  - new: "Accuracy is set to 30 m to cover the ~17 m scatter between the two candidate footprints, on top of the usual OpenStreetMap and derivation uncertainty. A source naming the specific building would allow it to be drawn as a hall polygon."
- `/method` (changed span only):
  - old: "...ches, no OSM tag names either, and no source fetched this session distinguishes them. `feature_type` is `targe..."
  - new: "...ches, no OSM tag names either, and no source consulted (checked 2026-09-18) distinguishes them. `feature_type` is `targe..."
- `/notes/0`:
  - old: "Integrator (2026-09-21): feature_type corrected from target_station to other; this is a derived detector position, not a beam target."
  - new: "The feature type is 'other' (corrected on 2026-09-21 from target_station): this is a derived detector position, not a beam target."
- `/notes/1`:
  - old: "QA pass (2026-09-21): removed the `valid: {start: '2024-07', end: null}` window a previous pass set -- a preventive fix for a latent bug in hepgraph.atlas.build._feature_segments(): any `valid` dict with a non-null `start` and `end: null` hard-codes `status: 'active'` through build day regardless of the entity's real status, bypassing state_segments entirely. Currently harmless because detector:sbnd genuinely is 'active' today, but this pattern produced a live false-'active' claim on three other records (geometry:lhc-tunnel-ring, geometry:fermilab-mc1-building, geometry:fermilab-microboone-hall) fixed the same way in this pass -- see docs/atlas-worklog/REVIEW_geometry_qa.md."
  - new: "(removed)"
- `/summary/plain`:
  - old: "accuracy_m widened to 30 m specifically to cover the ~17 m candidate-footprint scatter, on top of the usual OSM/derivation uncertainty. A QA pass or a source naming the specific building would let ..."
  - new: "A derived point for the SBND detector, 110 m along the Booster Neutrino Beam axis from the derived target. Two nearby building footprints are almost equally good matches, so no building is drawn."

#### data/atlas/geometry/fermilab-seaquest-point.json

- `/geometry/note`:
  - old: "OSM node explicitly named and tagged for this experiment; confidence stays 'approximate' per the OSM-alone ceiling (no rank <=10 source independently confirms this exact point)."
  - new: "OpenStreetMap node named and tagged for this experiment; confidence is approximate because no primary source independently confirms this exact point."
- `/method` (changed span only):
  - old: "...nStreetMap node 4425992583, used verbatim (a POI node, not a building footprint). Independently found during a QA re-derivation pass: the geometry worklog (docs/atlas-worklog/GEOMETRY_fermilab.md) reported that 'a targeted OSM name search for NM4 returned no results' and left detector:seaquest / site:fermilab-nm4-hall unlocated on that basis; that specific narrow search was true, but a search for the experiment's own name ('SeaQuest') -- never tried in that session -- finds this node directly, independently confirmed by this reviewer with a direct fetch of https://api.openstreetmap.org/api/0.6/node/4425992583.json (not just trusting a subagent's report of it). accuracy_m 10 m follows the contract's floor for an OSM point/building-scale feature; feature_type 'other' (not 'hall') because this is a singl..."
  - new: "...nStreetMap node 4425992583, used verbatim (a point of interest, not a building footprint). A search of OpenStreetMap for the literal string 'NM4' returns nothing, but a search for the experiment's own name ('SeaQuest') finds this node, tagged name=SeaQuest and addr:housenumber=NM4 (fetched 2026-09-21 from https://api.openstreetmap.org/api/0.6/node/4425992583.json). accuracy_m is 10 m, the floor for an OpenStreetMap point or building-scale feature; the feature type is 'other' (not 'hall') because this is a singl..."
- `/notes/0`:
  - old: "QA pass (2026-09-21): removes detector:seaquest and site:fermilab-nm4-hall from map:fermilab.unlocated[] (see that map's own notes for the prior, now-superseded reason text)."
  - new: "detector:seaquest and site:fermilab-nm4-hall are drawn (since 2026-09-21) and are no longer listed as unlocated on the map."

#### data/atlas/geometry/fermilab-tevatron-ring.json

- `/notes/0` (changed span only):
  - old: "QA pass (2026-09-21): this record's own worklog (docs/atlas-worklog/GEOMETRY_fermilab.md SS2/SS5) flagged the Tevatron-as-circle judgement call as the single item most needing independent scrutiny, since no rank<=10 primary source it fetched uses the word 'circular' or states a numeric radius. Two independently dispatched QA reviewers re-derived this from scratch: both reproduced this record's own OSM circle fit (same centre/radius/vertex count, from a fresh Overpass fetch) and its CDF/D0 distance cross-checks to within a few metres; both also independently found lower-rank secondary sources (a Wikipedia statement that the Tevatron 'was a circular particle accelerator ... in a 6.28 km circumference ring', and independent descriptions of the same-tunnel, same-circumference predecessor Main Ring as 'a large (1000 m radius) synchrotron') that satisfy the research brief's rule 3 by its plain text, even though no fetched rank<=10 paper phrases it that way. Per 'nothing from memory', those secondary quotes are recorded here as a review finding, not cited as a new `sources` entry, since this reviewer did not independently re-fetch them. Confidence stays `derived` (not upgraded) and the shape stays drawn: the reviewers' conclusion is that the existing derived-circle representation is honest and, if anything, under-claimed its own justification -- not that it should be weakened or removed. See docs/atlas-worklog/REVIEW_geometry_qa.md for the full independent re-derivation."
  - new: "No primary source consulted uses the word 'circular' or states a numeric radius for the Tevatron. The circle is a derived representation: the sourced 6.3 km circumference, in the Main Ring tunnel it shared. Secondary sources describe the ring as circular, but they are not cited here. The shape stays derived."
- `/notes/1`:
  - old: "Release pass (gaps stream, 2026-10-25): re-placed from the Main Injector TDR relation and the Fermilab Site Coordinate System; the OSM ring-road centre it replaces was 41 m away. The A0 distance check replaces the two hall-centroid checks, which assumed the surface buildings stand on the ring."
  - new: "Re-placed on 2026-10-25 from the Main Injector design handbook's relation and the Fermilab Site Coordinate System; the OpenStreetMap ring-road centre it replaces was 41 m away. A distance check to the A0 point replaces the two hall-centroid checks, which assumed the surface buildings stand on the ring."
- `/method` (changed span only):
  - old: "...nce and the MI-60 relation below fits it (no fetched rank <= 10 source says \"circular\"). Centre from the Main Injec..."
  - new: "...nce and the MI-60 relation below fits it (no primary source consulted says \"circular\"). Centre from the Main Injec..."

#### data/atlas/maps/fermilab.json

- `/levels/1/note`:
  - old: "No source fetched this session gives the Booster tunnel's depth below grade; the ring itself is drawn (geometry:fermilab-booster-ring) but its depth is unsourced."
  - new: "As of 2026-09-18 no source consulted gives the Booster tunnel's depth below grade; the ring itself is drawn (geometry:fermilab-booster-ring) but its depth is unsourced."
- `/notes/0`:
  - old: "Far sites (not drawn on this map; see the geometry worklog for great-circle distances and bearings computed from the sourced site:fermilab-main-campus point): site:soudan-minos-far-detector (735.4 km, bearing 336.0 degrees, historical MINOS-era NuMI beam), site:ash-river-nova-far-detector (811.7 km, bearing 335.5 degrees, current NOvA-era NuMI beam), site:surf-4850-level-dune-far-detector (1287.6 km, bearing 287.7 degrees, LBNF beam). No map:soudan, map:ash-river or map:surf record exists yet in this branch, so linked_map_ids is empty; the integrator should populate it once those maps exist."
  - new: "Far sites (not drawn on this map; great-circle distances and bearings computed from the sourced site:fermilab-main-campus point): site:soudan-minos-far-detector (735.4 km, bearing 336.0 degrees, historical MINOS-era NuMI beam), site:ash-river-nova-far-detector (811.7 km, bearing 335.5 degrees, current NOvA-era NuMI beam), site:surf-4850-level-dune-far-detector (1287.6 km, bearing 287.7 degrees, LBNF beam). The Soudan and SURF sites have their own maps (map:soudan-underground-laboratory, map:surf); there is no map for the Ash River site. linked_map_ids on this map is empty."
- `/notes/2`:
  - old: "QA pass (2026-09-21): detector:seaquest and site:fermilab-nm4-hall are no longer unlocated. An independent QA re-derivation found (and this reviewer independently re-confirmed with a direct fetch) OpenStreetMap node 4425992583, tagged name=SeaQuest, addr:housenumber=NM4, in the campus bbox -- the prior 'no OSM trace' reason was narrowly true (a search for the literal string 'NM4' finds nothing) but gave a false overall impression, since a search for the experiment's own name finds it directly. Now drawn as geometry:fermilab-seaquest-point."
  - new: "detector:seaquest and site:fermilab-nm4-hall are drawn (geometry:fermilab-seaquest-point), from OpenStreetMap node 4425992583, tagged name=SeaQuest and addr:housenumber=NM4, inside the campus bounding box. A search of OpenStreetMap for the literal string 'NM4' finds nothing, which is why the experiment was first listed as unlocated; a search for the experiment's own name finds the node directly (checked 2026-09-21)."
- `/notes/3`:
  - old: "Release pass (2026-10-25): the Main Injector and Recycler are drawn. The shape is computed from the TDR's straight-section lengths, dipole counts and lattice listing (derived; see geometry:fermilab-main-injector-ring for the derivation and the independent 28.789277 m check). Gaps stream (2026-10-25): the ring is now placed with the TDR's own published site coordinates (Fermilab Site Coordinate System of Beams-doc-1148), accuracy 8 m; the earlier road-fitted placement was displaced 38-74 m. The earlier 'grassland' polygon geometry:fermilab-mi-infield remains context only."
  - new: "The Main Injector and Recycler are drawn (2026-10-25). The shape is computed from the TDR's straight-section lengths, dipole counts and lattice listing (derived; see geometry:fermilab-main-injector-ring for the derivation and the independent 28.789277 m check). The ring is placed with the TDR's own published site coordinates (Fermilab Site Coordinate System of Beams-doc-1148), accuracy 8 m; an earlier placement fitted to a road was displaced 38-74 m. The grassland polygon geometry:fermilab-mi-infield is context only."
- `/summary/plain` (changed span only):
  - old: "...1) the Tevatron ring are drawn to scale from OpenStreetMap and their sourced sizes, along with the CDF, D0, MINOS, NOvA, MiniBooNE, MicroBooNE and ICARUS detector buildings and the Muon g-2 MC-1 building. Derived target points and beamline axes for the BNB and NuMI beams are reconstructed from OpenStreetMap building positions and sourced beam distances, not from a coarse campus point. The 3.3 km Main Injector and Recycler ring (one shared tunnel, an oval with eight straight sections, shape from the design handbook) is drawn; PIP-II, Mu2e and a few fixed-target detector halls could ..."
  - new: "...1) the Tevatron ring are drawn to scale from their sourced sizes, along with the Main Injector and Recycler ring, the CDF, D0, MINOS, NOvA, MiniBooNE, MicroBooNE, SBND and ICARUS detector sites and the Muon g-2 MC-1 building. The NuMI beamline and its underground halls are drawn from the NuMI design report's published coordinates; the Booster Neutrino Beam target is a derived point reconstructed from building positions and the sourced MiniBooNE distance. The 3.3 km Main Injector and Recycler ring (one shared tunnel, an oval with eight straight sections, shape from the design handbook) is drawn; PIP-II, Mu2e, the DUNE near detector and a few fixed-target detector halls could ..."
- `/summary/technical` (changed span only):
  - old: "...al to-scale map of the Fermilab Batavia campus: a derived circle for the Booster ring (474 m sourced circumference, OSM-fit centre) and for the Tevatron ring (6.3 km sourced circumference, OSM ring-road-fit centre, cross-checked against the OSM-sourced CDF and D0 hall positions); georeferenced/derived OSM building footprints for the CDF Hall, D0 Assembly Building, MINOS and NOvA near-detector surface buildings, MiniBooNE Detector Building, the LArTF/MicroBooNE hall, a positionally-identified ICARUS-T600 hall and the Muon g-2 MC-1 building; derived target_station/beamline features for BNB and NuMI, each anchored on two independently-named OSM footprints rather than a coarse site point, with passing distance/azimuth checks; an approximate linac axis; context-only campus boundary, Main Injector-area grassland and MC-2 polygons; and inferred-direction lines for the NuMI and LBNF beams, now starting from the derived NuMI target. PIP-II, KTeV, Mu2e, SBND (candidate footprints found but not confidently identified), MINERvA, DONUT, SENSEI, DAMIC (prototype) and the DUNE near detector are unlocated, each with a sourced reason and backlog. SeaQuest/NM4 was added by a QA pass (2026-09-21) as an OSM-tagged point (geometry:fermilab-seaquest-point). Release pass 2026-10-25: Main Injector and Recycler drawn as derived 3319 m rings (TDR lattice shape, placed on the Indian Creek Road offset; 30 m)."
  - new: "...al to-scale map of the Fermilab Batavia campus. Rings: a derived circle for the Booster ring (474 m sourced circumference, OSM-fit centre, with the surveyed start of the 8 GeV line as an independent check) and for the Tevatron ring (6.3 km sourced circumference, centre placed from the Main Injector design handbook's survey relation and checked against the published A0 point), and the Main Injector and Recycler as derived 3319 m rings (lattice shape from the design handbook, placed with its published site coordinates; 8 m). Detectors: georeferenced OSM building footprints for the CDF Hall, D0 Assembly Building, MINOS and NOvA near-detector surface buildings, MiniBooNE Detector Building, the LArTF/MicroBooNE hall and the Muon g-2 MC-1 building, a positionally identified ICARUS-T600 hall, an OSM-tagged point for SeaQuest/NM4 and a derived point for SBND. Beams: the NuMI target, beamlines and underground halls from the NuMI design report's beam sheet (published site coordinates); a derived BNB target and beamline anchored on two independently named OSM footprints; an approximate linac axis; and inferred-direction lines for the NuMI and LBNF beams. Context features, each drawn only from a date given or bounded by a source: the campus boundary, Wilson Hall, the MI-62 service building, MC-2 and the Main Injector grassland. PIP-II, KTeV, Mu2e, MINERvA, DONUT, SENSEI, DAMIC (prototype) and the DUNE near detector are unlocated, each with a sourced reason and backlog."
- `/unlocated/2/reason`:
  - old: "No OpenStreetMap footprint or other sourced coordinate for the KTeV hall was found this session (a targeted OSM name search for 'KTeV' returned no results)."
  - new: "No OpenStreetMap footprint or other sourced coordinate for the KTeV hall was found (checked 2026-09-18; a targeted OSM name search for 'KTeV' returned no results)."
- `/unlocated/3/backlog` (changed span only):
  - old: "Second pass (2026-09-18): found a candidate building, OSM way 720556732 'MC-2' (drawn as context only, geometry:fermilab-mc2-building), 84 m from the confirmed MC-1/g-2 building -- plausible given the MC-1/MC-2 naming pattern, but a WebSearch and two WebFetch attempts (arXiv:2208.02889 'Muon Campus at Fermilab', HTML and PDF) found no fetchable text confirming MC-2 is specifically the Mu2e hall. Also found the former Antiproton Source buildings AP-0/AP-10/AP-30/AP-50 (OSM, src:fermilab-geo-osm-muon-campus) clustered near 41.8346,-88.2656, candidate anchors for the adjacent Delivery Ring (ex-Debuncher, sourced as roughly triangular and ~505 m in circumference by the task brief, but no source fetched this session states its shape/circumference directly, and three building centroids are not enough to justify drawing a triangle without a sourced vertex/side correspondence) -- not drawn, but useful context for whoever resolves MC-2. Confirming either would let Mu2e become a drawn `hall`. Gaps stream (2026-10-25): re-checked; the Mu2e TDR (arXiv:1501.05241, Fig. 6.120 and sections 1-2) and the Muon Campus overview (arXiv:2208.02889) contain no site coordinate and do not name the Mu2e building MC-2; further web searches for 'MC-2' with Mu2e found no source. Next: Fermilab's facilities directory or a Mu..."
  - new: "A candidate building, OSM way 720556732 'MC-2' (drawn as context only, geometry:fermilab-mc2-building), stands 84 m from the confirmed MC-1/g-2 building and is plausible given the MC-1/MC-2 naming pattern, but no fetchable text confirms MC-2 is specifically the Mu2e hall (checked 2026-09-18: a web search and two attempts to read arXiv:2208.02889 'Muon Campus at Fermilab', HTML and PDF). Re-checked 2026-10-25: the Mu2e TDR (arXiv:1501.05241, Fig. 6.120 and sections 1-2) and the Muon Campus overview (arXiv:2208.02889) contain no site coordinate and do not name the Mu2e building MC-2; further web searches for 'MC-2' with Mu2e found no source. The former Antiproton Source buildings AP-0/AP-10/AP-30/AP-50 (OSM, src:fermilab-geo-osm-muon-campus) cluster near 41.8346,-88.2656 and are candidate anchors for the adjacent Delivery Ring (ex-Debuncher), but no source consulted (checked 2026-09-18) states the ring's shape or circumference, and three building centroids are not enough to justify drawing a ring without a sourced vertex/side correspondence, so it is not drawn. Confirming either would let Mu2e become a drawn `hall`. Next: Fermilab's facilities directory or a Mu..."
- `/unlocated/5/reason`:
  - old: "No dedicated OpenStreetMap footprint or other sourced coordinate for the DONUT hall was found this session; the existing placement record for this 1997 fixed-target experiment cites only a Wikipedia pointer."
  - new: "No dedicated OpenStreetMap footprint or other sourced coordinate for the DONUT hall was found (checked 2026-09-18); the existing placement record for this 1997 fixed-target experiment cites only a Wikipedia pointer."
- `/unlocated/7/reason`:
  - old: "The original DAMIC prototype's Fermilab placement (2008-2012) has no dedicated hall coordinate sourced this session; the existing placement record notes only that a precise coordinate was not found."
  - new: "The original DAMIC prototype's Fermilab placement (2008-2012) has no dedicated hall coordinate in the sources consulted (checked 2026-09-18); the existing placement record notes only that a precise coordinate was not found."



---

## Appendix C. LHC LS3 and status, XENONnT (F10, F25)

# LOG: lhc-ls3 (F10, F25 part 1, F25 part 2)

Date of all fetches: 2026-10-25. Worktree: /Users/yatharthsirohi/Desktop/HEP-Graph-ar-rc-data (nothing committed).
Validator: 0 errors (1603 warnings, all pre-existing categories: derived `rank`/`document_ids`/`result_ids` fields, A9 SLists, hull gaps, campus-grade coordinates).
Quote check (scripts/atlas_quote_check.py, `--only` per file): no `near`/`missing`/`unfetchable` in any touched file; every quote I added is `verbatim` or `segments`. `skipped` rows are pre-existing quotes whose source is an inspirehep.net record (the script and the rules do not fetch those).

## Decisions

1. LS3 encoding, identical on every LHC experiment and detector record and equal to accelerator:lhc's interval: `start` = "2026-06-29" (day precision, CERN: "since LS3 began on 29 June 2026"); `end` = `{"approx": true, "date": "2030", "display": "mid-2030", "planned": true, "note": ...}`. accelerator:lhc itself carries no `earliest`/`latest` on this end date, so none were added; a year-precision date with `display` is exactly its encoding. accelerator:lhc already agrees with the CERN source (start 2026-06-29, end mid-2030), so it was not edited.
2. Status rule for LS3 (applied the same way in the experiment's top-level `status`, its intervals and its detector record): `upgrade` only where a fetched ALICE/ATLAS/CMS/LHCb/CERN source says the experiment's own detector is being (or is approved to be) upgraded in LS3 (ATLAS, CMS, ALICE, LHCb); otherwise `shutdown` (LHCf, TOTEM, FASER, SND@LHC, MoEDAL). A plan that is not tied to LS3, or an LS3 installation plan with no 2026 source and no formal approval found, is recorded in the note but does not change the status (FASER neutrino-detector upgrade "by the start of Run 4"; MoEDAL MAPP-2 "planned for installation during LS3", 2022-23 paper).
3. Run 4 (HL-LHC) for ATLAS now starts "mid-2030" (planned), no longer 2029. ATLAS's own January 2023 article is superseded and said so in the interval note.
4. XENONnT: the open-ended recommissioning state keeps `status: commissioning` and `confidence: approximate` (sources are collaboration talk abstracts and slides, source rank 12; they establish the start, not that commissioning is still going on). Dates carry `display` wording and A4-style bounds instead of bare years.

## Sources fetched today and the verbatim text used

CERN, Long Shutdown 3 page, https://home.cern/science/long-shutdown-3/ (src:cern-long-shutdown-3-page, accessed 2026-10-25):
- "The cryogenics team has been running the warm-up sequence since LS3 began on 29 June 2026." (item dated 5 August 2026)
- "...stored ready to be used again once the accelerator resumes operation in mid-2030." (same item)
- "This phase, known as “Long Shutdown 3” or “LS3”, is expected to last up to four years" (page intro)
- "The accelerator complex and its experiment facilities will gradually resume operation from mid-2028 onwards." (page intro; this is the injector complex and facilities, not the LHC, which is why 2028 is not used)
- "Work on the CMS muon system upgrade is now underway, with teams starting to install the new electronic system for the Drift Tube (DT) chambers." (item dated 17 September 2026)
- "The core of the CMS experiment, the pixel detector, has now been removed after 10 years of successful operations." (item dated 19 October 2026)

CERN, farewell article of 29 June 2026, https://home.cern/cern-bids-farewell-to-the-lhc-and-enters-long-shutdown-3/ (src:cern-ls3-farewell-2026):
- "Following its final physics run, the accelerator has been switched off to begin CERN’s Long Shutdown 3 (LS3)"
- "The LHC is currently shut down."
- "The HiLumi LHC, scheduled to begin operation in 2030"
- "In the LHC caverns, the ATLAS and CMS experiments will undergo extensive upgrades, effectively becoming renewed detectors." (ATLAS and CMS upgrade claim)

CERN, "New schedule for CERN's accelerators", 8 October 2024, https://home.cern/new-schedule-cerns-accelerators/ (new src:rc-cern-new-schedule-2024): "The start-up of the HL-LHC (Run 4) is now planned for June 2030."

ATLAS, High-Luminosity ATLAS page, https://atlas.cern/Discover/Detector/HiLumi-Upgrades (new src:rc-atlas-hilumi-upgrades-page): "Scheduled to run from 2030 to 2041, the HL-LHC will dramatically increase the collider's intensity"; "the next generation of detector technologies that are being installed at CERN during the long shutdown period prior to 2030".

ATLAS, feature article dated 18 January 2023, https://atlas.cern/Updates/Feature/High-Luminosity-ATLAS (src:atlas-high-luminosity-feature; the superseded 2029 source): "They will all be installed and commissioned during LS3 in time for the start of Run 4, currently planned for 2029." and "starting from 2029".

ALICE (upgrade claim): CERN news of 25 April 2024 written by the ALICE collaboration, https://home.cern/alice-gets-green-light-new-subdetectors/ (new src:rc-alice-its3-focal-approval-2024): "Two detector upgrades of ALICE, the dedicated heavy-ion physics experiment at the Large Hadron Collider (LHC), have recently been approved for installation during the next long shutdown of the LHC, which will take place from 2026 to 2028." (the 2026-2028 window and "early 2028" installation are older than CERN's mid-2030 schedule and are not used for dates). ALICE Collaboration, arXiv:2601.07405 (12 January 2026), https://arxiv.org/abs/2601.07405 (new src:rc-alice-its3-design-arxiv-2026): "During the LHC Long Shutdown 3 (2026-29) ALICE will replace its three innermost tracking layers by a new detector, the “ITS3”." ALICE site, https://alice-collaboration.web.cern.ch/ (src:colliders-lhc-alice-collaboration-site): "Further detector upgrades are being carried out for Run 4 until the end of 2033." (read as the Run 4 upgrade programme; it does not conflict with an LS3 ending in mid-2030).

LHCb (upgrade claim): LHCb outreach site, 8 May 2024, https://lhcb-outreach.web.cern.ch/2024/05/08/ecal-and-rich-sub-detector-enhancements-approved-for-construction/ (new src:rc-lhcb-ecal-rich-enhancements-2024): "The LHCb experiment will upgrade the inner part of the Electromagnetic Calorimeter and the electronics of the Ring Imaging Cherenkov detectors in the next LHC Long Shutdown (LS3)."; "Upgrade II will be installed during Long Shutdown 4 (LS4)"; LS3 "currently scheduled for the years 2026–28" (older than the mid-2030 schedule). JINST 21 C03018 (published 11 March 2026), https://iopscience.iop.org/article/10.1088/1748-0221/21/03/C03018 (new src:rc-lhcb-ecal-ls3-jinst-2026): "An enhancement of the LHCb electromagnetic calorimeter (ECAL) is foreseen during Long Shutdown 3 (LS3) of the LHC."; "In total, 176 new SpaCal modules with radiation-tolerant scintillating plastic fibers will be installed during LS3."

FASER (plan only, no upgrade status): FASER Collaboration, arXiv:2503.19775 (25 March 2025), https://arxiv.org/pdf/2503.19775 (new src:rc-faser-neutrino-upgrade-2025): "The current plan is to implement the upgrade of the FASER detector by the start of the LHC Run 4." faser.web.cern.ch home page: no mention of LS3 or an upgrade (checked 2026-10-25).

MoEDAL (plan only, no upgrade status): J. Pinfold, arXiv:2209.03988 v2 (13 March 2023), https://arxiv.org/html/2209.03988v2 (new src:rc-moedal-mapp-pinfold-2023): "MAPP-2 that is planned for installation during the long shutdown (LS3) prior to the startup of HL-LHC." moedal.web.cern.ch home page: no mention of LS3 or an upgrade (checked 2026-10-25).

SND@LHC: official site https://snd-lhc.web.cern.ch/ (new src:rc-snd-lhc-official-site), title text "SND@LHC: Scattering and Neutrino Detector at the LHC"; home page does not mention LS3 or an upgrade. home.cern/science/experiments/snd-lhc returns HTTP 404 and sndlhc.web.cern.ch does not resolve (checked 2026-10-25). LHCf (lhcf.web.cern.ch does not resolve) and TOTEM (totem.web.cern.ch redirects to a CERN login page): no experiment-specific LS3 source could be read.

XENONnT (all re-fetched 2026-10-25):
- ATHEXIS 2026 abstract, https://indico.cern.ch/event/1645696/contributions/7094892/ (conference 8-12 June 2026): "Following upgrade operations conducted in 2025, the experiment began its new commissioning phase in 2026."
- LIDINE 2026 abstract, https://indico.nikhef.nl/event/7584/contributions/31307/ (talk 7 October 2026): "I will also provide an overview of the XENONnT detector upgrade carried out in summer 2025 and present the status and first results of the subsequent commissioning campaign."
- Nikhef Dark Matter Jamboree slides (May 2026), https://indico.nikhef.nl/event/7799/sessions/2514/attachments/11042/17101/DM-Jamboree-Decowski-May26.pdf: "Upgrade completed replacing electrodes to increase drift field from 23 V/cm → 100 V/cm" (the PDF text extraction drops the "fi" ligature: "drift eld"); "1-year long operation: built clean-room in watertank"; "Everything back in place, 8.5 tons of LXe"; "Commissioning until July, then start of data taking"; timeline labels "12 month upgrade"; science runs SR0, SR1, SR2 listed.
- Science-run start 2021-07-06 is the pre-existing INSPIRE experiment record date (inspirehep.net not fetched, per the rules).

## New source records (data/atlas/sources/)
rc-atlas-hilumi-upgrades-page, rc-cern-new-schedule-2024, rc-alice-its3-focal-approval-2024, rc-alice-its3-design-arxiv-2026, rc-lhcb-ecal-rich-enhancements-2024, rc-lhcb-ecal-ls3-jinst-2026, rc-faser-neutrino-upgrade-2025, rc-moedal-mapp-pinfold-2023, rc-snd-lhc-official-site.
Reused records whose `accessed` was set to 2026-10-25 because I re-fetched them today: src:colliders-lhc-alice-collaboration-site, src:atlas-high-luminosity-feature. (src:cern-long-shutdown-3-page and src:cern-ls3-farewell-2026 already read 2026-10-25.)

## Changes, old -> new (generated by comparing each file with its content before my edits)
### data/atlas/collaborations/alice.json
- **interval** `collaboration`  (wording cleanup)
    - old: status=active; confidence=verified; start=1993-03-01; end=null
    - new: status=active; confidence=verified; start=1993-03-01; end=null
    - sources old: '["src:colliders-lhc-alice-30-years", "src:colliders-lhc-alice-inspire-experiment-record"]'
    - sources new: '["src:colliders-lhc-alice-30-years", "src:colliders-lhc-alice-inspire-experiment-record", "src:colliders-lhc-alice-collaboration-site"]'
    - verified_at old: '2026-09-17'
    - verified_at new: '2026-10-25'
    - note old: 'The collaboration continues to operate the ALICE experiment as of the sources fetched this session (2019/2019 hypertriton paper data; 2021 ALICE 2 upgrade completion; ongoing Run 3).'
    - note new: "The collaboration was still active according to the sources consulted: a hypertriton paper dated 2019, the completion of the ALICE 2 upgrade in 2021, and operation through LHC Run 3. As of 2026-10-25 ALICE's collaboration site says 'Further detector upgrades are being carried out for Run 4 until the end of 2033'."
- notes, old text removed or rewritten: `Institution-level membership rows (data/atlas/memberships/alice.json) belong to the membership-lead workstream and are not written here, per the Wave 3 brief (no roster file in this pass).`
- notes, old text removed or rewritten: `Leadership is left empty: no page fetched this session names a current ALICE spokesperson.`
- notes, old text removed or rewritten: `Derived field collaboration.experiment_ids is deliberately not written (v0.2 A1).`
- notes, new text: `Institution-level membership rows are in data/atlas/memberships/alice.json, not in this record.`
- notes, new text: `Leadership is left empty: no page consulted names a current ALICE spokesperson.`

### data/atlas/detectors/alice.json
- **top-level status**: `shutdown` -> `upgrade`
- **interval** `operating`  (wording cleanup)
    - old: status=active; confidence=verified; start=2009-11-23; end={date=2026-06, approx} note: "VERIFIER FIX (2026-09-17): capped at the LHC-wide Long Shutdown 3 boundary (see the added interval below); this record previously left this interval open-ended (end: null), which made detector:alice derive as permanently 'active' even during LS3, contradicting experiment:alice's own (correct) 'shutdown' status at the same date. ALICE cannot record collisions the LHC is not delivering."
    - new: status=active; confidence=verified; start=2009-11-23; end={date=2026-06, approx} note: 'Ends at the LHC-wide start of Long Shutdown 3 (June 2026); ALICE cannot record collisions the LHC is not delivering.'
    - end.note old: "VERIFIER FIX (2026-09-17): capped at the LHC-wide Long Shutdown 3 boundary (see the added interval below); this record previously left this interval open-ended (end: null), which made detector:alice derive as permanently 'active' even during LS3, contradicting experiment:alice's own (correct) 'shutdown' status at the same date. ALICE cannot record collisions the LHC is not delivering."
    - end.note new: 'Ends at the LHC-wide start of Long Shutdown 3 (June 2026); ALICE cannot record collisions the LHC is not delivering.'
- **interval** `Long Shutdown 3` -> `Long Shutdown 3 / ITS3 and FoCal upgrade`  (F10/F25 LS3)
    - old: status=shutdown; confidence=verified; start=2026-06; end=null
    - new: status=upgrade; confidence=approximate; start=2026-06-29; end={date=2030, display='mid-2030', approx, planned} note: 'CERN schedule: the LHC resumes operation in mid-2030; the rest of the CERN complex restarts in stages from mid-2028.'
    - quote old: 'null'
    - quote new: 'Two detector upgrades of ALICE ... have recently been approved for installation during the next long shutdown of the LHC'
    - locator old: "reused from experiment:alice's sourced Long Shutdown 3 interval (src:cern-ls3-farewell-2026)"
    - locator new: 'home.cern/science/long-shutdown-3, item of 5 August 2026 "The LHC is being warmed up from near absolute zero to room temperature"'
    - sources old: '["src:cern-ls3-farewell-2026"]'
    - sources new: '["src:rc-alice-its3-focal-approval-2024", "src:rc-alice-its3-design-arxiv-2026", "src:colliders-lhc-alice-collaboration-site", "src:cern-long-shutdown-3-page", "src:cern-ls3-farewell-2026"]'
    - verified_at old: '2026-09-17'
    - verified_at new: '2026-10-25'
    - note old: "VERIFIER-ADDED (2026-09-17): mirrors experiment:alice's Long Shutdown 3 interval so the detector-level derived status agrees with the experiment-level one; ongoing at verified_at."
    - note new: "The ITS3 (new inner tracking layers) and FoCal (forward calorimeter) upgrades are approved for installation during Long Shutdown 3. The bounds and the sources' wording are those of experiment:alice, whose interval note also records that the 2024 and 2026 ALICE-related sources use older LS3 dates than CERN's mid-2030 schedule."
- /placements/0/note: `Start approximated to the 1997 approval, when construction/installation at Point 2 began per the same paper; no fetched source gives an exact day the detector installation itself began at the site.` -> `Start approximated to the 1997 approval, when construction/installation at Point 2 began per the same paper; no source consulted gives an exact day the detector installation itself began at the site.`
- notes, old text removed or rewritten: `specs.total_mass/length/diameter reflect the as-built (2008) detector; the ALICE 2 upgrade (2021) replaced the ITS and TPC internals but no fetched source gives updated overall mass/dimension figures, so the original detector-paper values are kept with a note.`
- notes, old text removed or rewritten: `VERIFIER FIX (2026-09-17): status corrected 'active' -> 'shutdown' and a Long Shutdown 3 interval added (mirroring experiment:alice), because the prior record's open-ended 'operating' interval made the detector derive as permanently active even while CERN's LHC -- ALICE's only beam source -- is in Long Shutdown 3, contradicting experiment:alice's own status.`
- notes, new text: `specs.total_mass/length/diameter reflect the as-built (2008) detector; the ALICE 2 upgrade (2021) replaced the ITS and TPC internals but no source consulted gives updated overall mass/dimension figures, so the original detector-paper values are kept with a note.`
- notes, new text: `The detector record carries the same Long Shutdown 3 interval and status as experiment:alice, so that the two agree.`

### data/atlas/detectors/atlas.json
- **interval** `Phase-II upgrade (LS3)`  (F10/F25 LS3)
    - old: status=upgrade; confidence=approximate; start=2026-06; end={date=2029, approx, planned}
    - new: status=upgrade; confidence=approximate; start=2026-06-29; end={date=2030, display='mid-2030', approx, planned} note: 'CERN schedule: the LHC resumes operation in mid-2030; the rest of the CERN complex restarts in stages from mid-2028.'
    - quote old: 'They will all be installed and commissioned during LS3 in time for the start of Run 4, currently planned for 2029.'
    - quote new: 'the next generation of detector technologies that are being installed at CERN during the long shutdown period prior to 2030'
    - locator old: 'null'
    - locator new: 'home.cern/science/long-shutdown-3, item of 5 August 2026 "The LHC is being warmed up from near absolute zero to room temperature"'
    - sources old: '["src:atlas-high-luminosity-feature", "src:cern-long-shutdown-3-page"]'
    - sources new: '["src:atlas-high-luminosity-feature", "src:cern-long-shutdown-3-page", "src:cern-ls3-farewell-2026", "src:rc-atlas-hilumi-upgrades-page"]'
    - verified_at old: '2026-09-16'
    - verified_at new: '2026-10-25'
    - note old: 'Start (2026-06) is the scheduled beginning of Long Shutdown 3; the end date is the Run 4 start, itself described by the source as "currently planned" and therefore approximate/subject to change.'
    - note new: "Installation of the Phase-II upgrade detectors (ITk, HGTD, new trigger/DAQ and front-end electronics) during Long Shutdown 3; the bounds are the same as for experiment:atlas, whose interval note gives CERN's wording. An earlier end of 2029 (the Run 4 start in ATLAS's January 2023 feature article) is superseded by CERN's mid-2030 schedule."
- notes, old text removed or rewritten: `CONFLICT on the overall length: the 2008 JINST detector paper says 'The dimensions of the detector are 25 m in height and 44 m in length', while atlas.cern ('46m long') and home.cern ('At 46 m long, 25 m high and 25 m wide') say 46 m. The 46 m value from the collaboration's own current page is recorded in specs.length; the 44 m JINST value is kept in the note of that quantity. The most likely explanation is that the two figures count the forward shielding differently, but no fetched source says so.`
- notes, new text: `CONFLICT on the overall length: the 2008 JINST detector paper says 'The dimensions of the detector are 25 m in height and 44 m in length', while atlas.cern ('46m long') and home.cern ('At 46 m long, 25 m high and 25 m wide') say 46 m. The 46 m value from the collaboration's own current page is recorded in specs.length; the 44 m JINST value is kept in the note of that quantity. The most likely explanation is that the two figures count the forward shielding differently, but no source consulted says so.`

### data/atlas/detectors/cms.json
- **interval** `LHC Run 2`  (wording cleanup)
    - old: status=active; confidence=uncertain; start=2015; end=2018-12-03
    - new: status=active; confidence=uncertain; start=2015; end=2018-12-03
    - note old: "CERN states Run 2 ended on 3 December 2018 'after three fantastic years'; the exact 2015 restart date was not confirmed from a source fetched in this session, so the start is recorded at year precision."
    - note new: "CERN states Run 2 ended on 3 December 2018 'after three fantastic years'; no source consulted gives the exact 2015 restart date, so the start is recorded at year precision."
- **interval** `Long Shutdown 3 — Phase-2 upgrade`  (F10/F25 LS3)
    - old: status=upgrade; confidence=verified; start=2026-06; end={date=2030, approx, planned} note: 'HiLumi LHC scheduled to begin operation in 2030'
    - new: status=upgrade; confidence=approximate; start=2026-06-29; end={date=2030, display='mid-2030', approx, planned} note: 'CERN schedule: the LHC resumes operation in mid-2030; the rest of the CERN complex restarts in stages from mid-2028.'
    - quote old: "As of mid-2026, the accelerator complex and experimental facilities at CERN are undergoing major maintenance and upgrade work. This phase, known as 'Long Shutdown 3' or 'LS3', is expected to last up to four years."
    - quote new: 'In the LHC caverns, the ATLAS and CMS experiments will undergo extensive upgrades, effectively becoming renewed detectors.'
    - locator old: 'null'
    - locator new: 'home.cern/science/long-shutdown-3, item of 5 August 2026 "The LHC is being warmed up from near absolute zero to room temperature"'
    - verified_at old: '2026-09-16'
    - verified_at new: '2026-10-25'
    - note old: 'Phase-2 upgrade of CMS for the HL-LHC: new all-silicon tracker, new endcap calorimeter, MIP timing detector, muon and trigger/DAQ upgrades.'
    - note new: "Phase-2 upgrade of CMS for the HL-LHC: new all-silicon tracker, new endcap calorimeter, MIP timing detector, muon and trigger/DAQ upgrades. The bounds are the same as for experiment:cms, whose interval note gives CERN's wording and the upgrade work reported so far."
- /specs/solenoid_field/note: `Operating central flux density at the nominal 18.2 kA. The magnet was designed for and tested at 4 T, the value quoted on CMS's public pages; see worklog conflict C4.` -> `Operating central flux density at the nominal 18.2 kA. The magnet was designed for and tested at 4 T, the value quoted on CMS's public pages; the 4 T design value and the 3.8 T operating value are not reconciled.`
- /specs/total_mass/note: `The 2008 JINST detector paper and CERN's Point 5 page both give 12 500 t. CMS's own public detector page instead calls CMS 'The 14,000-tonne detector' while giving 12 500 t for the magnet coils plus return yoke; see worklog conflict C2.` -> `The 2008 JINST detector paper and CERN's Point 5 page both give 12 500 t. CMS's own public detector page instead calls CMS 'The 14,000-tonne detector' while giving 12 500 t for the magnet coils plus return yoke; the two figures are not reconciled.`
- notes, old text removed or rewritten: `ECAL crystal count, tracker silicon area in m² and the tracker |η| acceptance were not obtained from a source fetched in this session and are therefore absent.`
- notes, new text: `ECAL crystal count, tracker silicon area in m² and the tracker |η| acceptance were not found in any source consulted and are therefore absent.`

### data/atlas/detectors/faser.json
- **interval** `operating`  (wording cleanup)
    - old: status=active; confidence=verified; start=2022-07; end={date=2026-06, approx} note: 'VERIFIER FIX (2026-09-17): capped at the LHC-wide Long Shutdown 3 boundary; mirrors experiment:faser.'
    - new: status=active; confidence=verified; start=2022-07; end={date=2026-06, approx} note: 'Ends at the LHC-wide start of Long Shutdown 3 (June 2026); mirrors experiment:faser.'
    - end.note old: 'VERIFIER FIX (2026-09-17): capped at the LHC-wide Long Shutdown 3 boundary; mirrors experiment:faser.'
    - end.note new: 'Ends at the LHC-wide start of Long Shutdown 3 (June 2026); mirrors experiment:faser.'
- **interval** `Long Shutdown 3`  (F10/F25 LS3)
    - old: status=shutdown; confidence=verified; start=2026-06; end=null
    - new: status=shutdown; confidence=derived; start=2026-06-29; end={date=2030, display='mid-2030', approx, planned} note: 'CERN schedule: the LHC resumes operation in mid-2030; the rest of the CERN complex restarts in stages from mid-2028.'
    - quote old: 'null'
    - quote new: 'Following its final physics run, the accelerator has been switched off to begin CERN’s Long Shutdown 3 (LS3) ... The HiLumi LHC, scheduled to begin operation in 2030'
    - locator old: "reused from experiment:faser's sourced Long Shutdown 3 interval (src:cern-ls3-farewell-2026)"
    - locator new: 'home.cern/science/long-shutdown-3, item of 5 August 2026 "The LHC is being warmed up from near absolute zero to room temperature"'
    - sources old: '["src:cern-ls3-farewell-2026"]'
    - sources new: '["src:cern-long-shutdown-3-page", "src:cern-ls3-farewell-2026"]'
    - verified_at old: '2026-09-17'
    - verified_at new: '2026-10-25'
    - note old: 'VERIFIER-ADDED (2026-09-17): mirrors experiment:faser so the detector-level derived status agrees with the experiment-level one.'
    - note new: "The detector record carries the same Long Shutdown 3 interval as experiment:faser, whose interval note gives the evidence and CERN's wording for the bounds; the state is inferred from the LHC being shut down."
- notes, old text removed or rewritten: `No dimension/mass specs were sourced in this session; left out rather than guessed.`
- notes, old text removed or rewritten: `VERIFIER FIX (2026-09-17): status corrected 'active' -> 'shutdown' (see experiment:faser).`
- notes, new text: `No dimension/mass specs were sourced; left out rather than guessed.`
- notes, new text: `Status shutdown matches experiment:faser (Long Shutdown 3).`

### data/atlas/detectors/lhcb.json
- **top-level status**: `shutdown` -> `upgrade`
- **interval** `construction and installation`  (wording cleanup)
    - old: status=construction; confidence=uncertain; start=1998-09-17; end=2008-09
    - new: status=construction; confidence=uncertain; start=1998-09-17; end=2008-09
    - note old: "Mirrors experiment:lhcb's construction interval. VERIFIER NOTE (2026-09-17): confidence downgraded to 'uncertain' -- see experiment:lhcb's matching interval note for why INSPIRE's date_completed field (verbatim '2008-09', re-fetched and confirmed) should not be trusted at face value for an active, non-terminal experiment (contrast ATLAS/LHCf, whose date_completed is the honest INSPIRE placeholder '9999')."
    - note new: "Mirrors experiment:lhcb's construction interval. Confidence is 'uncertain': experiment:lhcb's matching interval note explains why INSPIRE's date_completed field ('2008-09') should not be taken at face value for an active, non-terminal experiment (ATLAS's and LHCf's records show the placeholder '9999' in the same field)."
- **interval** `operating`  (wording cleanup)
    - old: status=active; confidence=verified; start=2009-11-23; end={date=2026-06, approx} note: "VERIFIER FIX (2026-09-17): capped at the LHC-wide Long Shutdown 3 boundary (see the added interval below); previously open-ended (end: null), which made detector:lhcb derive as permanently 'active' during LS3, contradicting experiment:lhcb's own 'shutdown' status at the same date."
    - new: status=active; confidence=verified; start=2009-11-23; end={date=2026-06, approx} note: 'Ends at the LHC-wide start of Long Shutdown 3 (June 2026); LHCb cannot record collisions the LHC is not delivering.'
    - end.note old: "VERIFIER FIX (2026-09-17): capped at the LHC-wide Long Shutdown 3 boundary (see the added interval below); previously open-ended (end: null), which made detector:lhcb derive as permanently 'active' during LS3, contradicting experiment:lhcb's own 'shutdown' status at the same date."
    - end.note new: 'Ends at the LHC-wide start of Long Shutdown 3 (June 2026); LHCb cannot record collisions the LHC is not delivering.'
- **interval** `Long Shutdown 3` -> `Long Shutdown 3 / ECAL and RICH enhancements`  (F10/F25 LS3)
    - old: status=shutdown; confidence=verified; start=2026-06; end=null
    - new: status=upgrade; confidence=approximate; start=2026-06-29; end={date=2030, display='mid-2030', approx, planned} note: 'CERN schedule: the LHC resumes operation in mid-2030; the rest of the CERN complex restarts in stages from mid-2028.'
    - quote old: 'null'
    - quote new: 'The LHCb experiment will upgrade the inner part of the Electromagnetic Calorimeter and the electronics of the Ring Imaging Cherenkov detectors in the next LHC Long Shutdown (LS3).'
    - locator old: "reused from experiment:lhcb's sourced Long Shutdown 3 interval (src:cern-ls3-farewell-2026)"
    - locator new: 'home.cern/science/long-shutdown-3, item of 5 August 2026 "The LHC is being warmed up from near absolute zero to room temperature"'
    - sources old: '["src:cern-ls3-farewell-2026"]'
    - sources new: '["src:rc-lhcb-ecal-rich-enhancements-2024", "src:rc-lhcb-ecal-ls3-jinst-2026", "src:cern-long-shutdown-3-page", "src:cern-ls3-farewell-2026"]'
    - verified_at old: '2026-09-17'
    - verified_at new: '2026-10-25'
    - note old: "VERIFIER-ADDED (2026-09-17): mirrors experiment:lhcb's Long Shutdown 3 interval so the detector-level derived status agrees with the experiment-level one; ongoing at verified_at."
    - note new: "The inner part of the electromagnetic calorimeter is replaced and the RICH electronics are upgraded during Long Shutdown 3. The bounds and the sources' wording are those of experiment:lhcb, whose interval note also records that the 2024 LHCb page gives older LS3 dates than CERN's mid-2030 schedule."
- notes, old text removed or rewritten: `Placed at site:cern-point-8-lhcb (created in this pass). The detector paper (2008 JINST 3 S08005) was found but its full text was blocked by CERN's document-server bot protection (cds.cern.ch) and exceeded the fetch size limit at the SISSA mirror; only its abstract (via the INSPIRE literature API) is cited. Pseudorapidity coverage, dipole bending power, RICH/VELO/calorimeter/muon-system specs are left unsourced (missing_fields) rather than guessed from memory.`
- notes, old text removed or rewritten: `VERIFIER FIX (2026-09-17): status corrected 'active' -> 'shutdown' and a Long Shutdown 3 interval added (mirroring experiment:lhcb), because the prior record's open-ended 'operating' interval made the detector derive as permanently active even while CERN's LHC -- LHCb's only beam source -- is in Long Shutdown 3, contradicting experiment:lhcb's own status.`
- notes, new text: `Placed at site:cern-point-8-lhcb. The detector paper (2008 JINST 3 S08005) was found but its full text was blocked by CERN's document-server bot protection (cds.cern.ch) and exceeded the fetch size limit at the SISSA mirror; only its abstract (via the INSPIRE literature API) is cited. Pseudorapidity coverage, dipole bending power and the RICH/VELO/calorimeter/muon-system specs are left unsourced rather than guessed.`
- notes, new text: `The detector record carries the same Long Shutdown 3 interval and status as experiment:lhcb, so that the two agree.`

### data/atlas/detectors/lhcf.json
- **interval** `operating`  (wording cleanup)
    - old: status=active; confidence=verified; start=2009-11-23; end={date=2026-06, approx} note: 'VERIFIER FIX (2026-09-17): capped at the LHC-wide Long Shutdown 3 boundary; mirrors experiment:lhcf.'
    - new: status=active; confidence=verified; start=2009-11-23; end={date=2026-06, approx} note: 'Ends at the LHC-wide start of Long Shutdown 3 (June 2026); mirrors experiment:lhcf.'
    - end.note old: 'VERIFIER FIX (2026-09-17): capped at the LHC-wide Long Shutdown 3 boundary; mirrors experiment:lhcf.'
    - end.note new: 'Ends at the LHC-wide start of Long Shutdown 3 (June 2026); mirrors experiment:lhcf.'
- **interval** `Long Shutdown 3`  (F10/F25 LS3)
    - old: status=shutdown; confidence=verified; start=2026-06; end=null
    - new: status=shutdown; confidence=derived; start=2026-06-29; end={date=2030, display='mid-2030', approx, planned} note: 'CERN schedule: the LHC resumes operation in mid-2030; the rest of the CERN complex restarts in stages from mid-2028.'
    - quote old: 'null'
    - quote new: 'Following its final physics run, the accelerator has been switched off to begin CERN’s Long Shutdown 3 (LS3) ... The HiLumi LHC, scheduled to begin operation in 2030'
    - locator old: "reused from experiment:lhcf's sourced Long Shutdown 3 interval (src:cern-ls3-farewell-2026)"
    - locator new: 'home.cern/science/long-shutdown-3, item of 5 August 2026 "The LHC is being warmed up from near absolute zero to room temperature"'
    - sources old: '["src:cern-ls3-farewell-2026"]'
    - sources new: '["src:cern-long-shutdown-3-page", "src:cern-ls3-farewell-2026"]'
    - verified_at old: '2026-09-17'
    - verified_at new: '2026-10-25'
    - note old: 'VERIFIER-ADDED (2026-09-17): mirrors experiment:lhcf so the detector-level derived status agrees with the experiment-level one.'
    - note new: "The detector record carries the same Long Shutdown 3 interval as experiment:lhcf, whose interval note gives the evidence and CERN's wording for the bounds; the state is inferred from the LHC being shut down."
- /placements/0/note: `LHCf's two arms are physically in the TAN neutral-particle absorbers ±140 m from IP1, not in the ATLAS cavern itself; placed at site:cern-point-1-atlas (owned by cern-atlas, referenced only) per the id registry's explicit instruction that LHCf places at this existing site.` -> `LHCf's two arms are physically in the TAN neutral-particle absorbers ±140 m from IP1, not in the ATLAS cavern itself; the detector is placed at the existing site:cern-point-1-atlas.`
- notes, old text removed or rewritten: `VERIFIER FIX (2026-09-17): status corrected 'active' -> 'shutdown' (see experiment:lhcf).`
- notes, new text: `Status shutdown matches experiment:lhcf (Long Shutdown 3).`

### data/atlas/detectors/moedal.json
- **interval** `operating`  (wording cleanup)
    - old: status=active; confidence=uncertain; start=2009-12-02; end={date=2026-06, approx}
    - new: status=active; confidence=uncertain; start=2009-12-02; end={date=2026-06, approx}
    - note old: "Uses the approval date as a lower bound; no explicit installation/first-data date for the detector was found in this session (distinct from the experiment's own approval). End capped at the LHC switch-off for LS3 (2026-06)."
    - note new: "Uses the approval date as a lower bound; no explicit installation or first-data date for the detector was found (distinct from the experiment's own approval). End capped at the LHC switch-off for LS3 (2026-06)."
- **interval** `Long Shutdown 3`  (F10/F25 LS3)
    - old: status=shutdown; confidence=derived; start={date=2026-06, approx}; end=null
    - new: status=shutdown; confidence=derived; start=2026-06-29; end={date=2030, display='mid-2030', approx, planned} note: 'CERN schedule: the LHC resumes operation in mid-2030; the rest of the CERN complex restarts in stages from mid-2028.'
    - quote old: 'On Saturday 27 June at 6 am, the LHC’s Page 1 — the accelerator’s dashboard — said “goodbye” to collisions. The LHC operators dumped the last beams before the accelerator’s metamorphosis.'
    - quote new: 'Following its final physics run, the accelerator has been switched off to begin CERN’s Long Shutdown 3 (LS3) ... The HiLumi LHC, scheduled to begin operation in 2030'
    - locator old: 'null'
    - locator new: 'home.cern/science/long-shutdown-3, item of 5 August 2026 "The LHC is being warmed up from near absolute zero to room temperature"'
    - note old: 'Derived from the LHC-wide shutdown, as for the other LHC experiments in this atlas; no MoEDAL-specific announcement was fetched. Source for the shutdown: "On Saturday 27 June at 6 am, the LHC’s Page 1 — the accelerator’s dashboard — said “goodbye” to collisions. The LHC operators dumped the last beams before the accelerator’s metamorphosis." (home.cern, item dated 29 June 2026).'
    - note new: "The detector record carries the same Long Shutdown 3 interval as experiment:moedal, whose interval note gives the evidence and CERN's wording for the bounds; the state is inferred from the LHC being shut down."
- /placements/0/note: `MoEDAL is deployed inside the LHCb cavern at Point 8, surrounding the intersection region; placed at site:cern-point-8-lhcb (created by the lhcb pass of this same wave), role 'main' since MoEDAL's own detector fully occupies its NTD/trapping-detector footprint there (not a prototype).` -> `MoEDAL is deployed inside the LHCb cavern at Point 8, surrounding the intersection region; placed at site:cern-point-8-lhcb, role 'main' since MoEDAL's own detector fully occupies its NTD/trapping-detector footprint there (not a prototype).`

### data/atlas/detectors/snd-lhc.json
- **interval** `operating (LHC Run 3)`  (wording cleanup)
    - old: status=active; confidence=verified; start={date=2022, approx}; end={date=2026-06, approx} note: 'VERIFIER FIX (2026-09-17): capped at the LHC-wide Long Shutdown 3 boundary; mirrors experiment:snd-lhc.'
    - new: status=active; confidence=verified; start={date=2022, approx}; end={date=2026-06, approx} note: 'Ends at the LHC-wide start of Long Shutdown 3 (June 2026); mirrors experiment:snd-lhc.'
    - note old: 'VERIFIER-ADDED (2026-09-17): matches the corrected interval on experiment:snd-lhc.'
    - note new: 'Matches the operating interval on experiment:snd-lhc.'
    - end.note old: 'VERIFIER FIX (2026-09-17): capped at the LHC-wide Long Shutdown 3 boundary; mirrors experiment:snd-lhc.'
    - end.note new: 'Ends at the LHC-wide start of Long Shutdown 3 (June 2026); mirrors experiment:snd-lhc.'
- **interval** `Long Shutdown 3`  (F10/F25 LS3)
    - old: status=shutdown; confidence=verified; start=2026-06; end=null
    - new: status=shutdown; confidence=derived; start=2026-06-29; end={date=2030, display='mid-2030', approx, planned} note: 'CERN schedule: the LHC resumes operation in mid-2030; the rest of the CERN complex restarts in stages from mid-2028.'
    - quote old: 'null'
    - quote new: 'Following its final physics run, the accelerator has been switched off to begin CERN’s Long Shutdown 3 (LS3) ... The HiLumi LHC, scheduled to begin operation in 2030'
    - locator old: "reused from experiment:snd-lhc's sourced Long Shutdown 3 interval (src:cern-ls3-farewell-2026)"
    - locator new: 'home.cern/science/long-shutdown-3, item of 5 August 2026 "The LHC is being warmed up from near absolute zero to room temperature"'
    - sources old: '["src:cern-ls3-farewell-2026"]'
    - sources new: '["src:cern-long-shutdown-3-page", "src:cern-ls3-farewell-2026"]'
    - verified_at old: '2026-09-17'
    - verified_at new: '2026-10-25'
    - note old: 'VERIFIER-ADDED (2026-09-17): mirrors experiment:snd-lhc so the detector-level derived status agrees with the experiment-level one.'
    - note new: "The detector record carries the same Long Shutdown 3 interval as experiment:snd-lhc, whose interval note gives the evidence and CERN's wording for the bounds; the state is inferred from the LHC being shut down."
- notes, old text removed or rewritten: `VERIFIER FIX (2026-09-17): status corrected 'approved' -> 'shutdown' (via a sourced 'active' interval 2022-2026, then Long Shutdown 3). The prior record's own note already stated 'approved' likely understated SND@LHC's true operating status; this fix resolves that by sourcing the operating interval to the collaboration's own 2023 PRL (arXiv:2305.09383), which states data were collected 'in 2022', and capping it at the LHC-wide Long Shutdown 3 boundary already used for ALICE/LHCb/TOTEM/FASER/LHCf in this partition.`
- notes, old text removed or rewritten: `VERIFIER-ADDED (2026-09-17): technology and the TI18/480 m placement are now independently corroborated by the SND@LHC detector-description paper (arXiv:2210.02784), which states the detector sits '480 m downstream of the ATLAS interaction point, in the TI18 tunnel' -- confirming the placement fact that the prior record could only support with 'general knowledge of the FASER/SND@LHC forward programme' (site:cern-ti18-snd-lhc notes still flag the coordinate itself, only its lat/lon, as unverified).`
- notes, new text: `Status shutdown: the detector has a sourced 'active' interval from 2022 (the collaboration's 2023 PRL, arXiv:2305.09383, states data were collected 'in 2022'), capped at the LHC-wide start of Long Shutdown 3 as in experiment:snd-lhc.`
- notes, new text: `Technology and the TI18/480 m placement are corroborated by the SND@LHC detector-description paper (arXiv:2210.02784), which states the detector sits '480 m downstream of the ATLAS interaction point, in the TI18 tunnel'; the notes of site:cern-ti18-snd-lhc still flag the site's lat/lon as unverified.`

### data/atlas/detectors/totem.json
- **interval** `operating`  (wording cleanup)
    - old: status=active; confidence=verified; start=2009-11-28; end={date=2026-06, approx} note: "VERIFIER FIX (2026-09-17): capped at the LHC-wide Long Shutdown 3 boundary (see the added interval below); previously open-ended (end: null), which made detector:totem derive as permanently 'active' during LS3, contradicting experiment:totem's own 'shutdown' status at the same date."
    - new: status=active; confidence=verified; start=2009-11-28; end={date=2026-06, approx} note: 'Ends at the LHC-wide start of Long Shutdown 3 (June 2026); mirrors experiment:totem.'
    - end.note old: "VERIFIER FIX (2026-09-17): capped at the LHC-wide Long Shutdown 3 boundary (see the added interval below); previously open-ended (end: null), which made detector:totem derive as permanently 'active' during LS3, contradicting experiment:totem's own 'shutdown' status at the same date."
    - end.note new: 'Ends at the LHC-wide start of Long Shutdown 3 (June 2026); mirrors experiment:totem.'
- **interval** `Long Shutdown 3`  (F10/F25 LS3)
    - old: status=shutdown; confidence=verified; start=2026-06; end=null
    - new: status=shutdown; confidence=derived; start=2026-06-29; end={date=2030, display='mid-2030', approx, planned} note: 'CERN schedule: the LHC resumes operation in mid-2030; the rest of the CERN complex restarts in stages from mid-2028.'
    - quote old: 'null'
    - quote new: 'Following its final physics run, the accelerator has been switched off to begin CERN’s Long Shutdown 3 (LS3) ... The HiLumi LHC, scheduled to begin operation in 2030'
    - locator old: "reused from experiment:totem's sourced Long Shutdown 3 interval (src:cern-ls3-farewell-2026)"
    - locator new: 'home.cern/science/long-shutdown-3, item of 5 August 2026 "The LHC is being warmed up from near absolute zero to room temperature"'
    - sources old: '["src:cern-ls3-farewell-2026"]'
    - sources new: '["src:cern-long-shutdown-3-page", "src:cern-ls3-farewell-2026"]'
    - verified_at old: '2026-09-17'
    - verified_at new: '2026-10-25'
    - note old: "VERIFIER-ADDED (2026-09-17): mirrors experiment:totem's Long Shutdown 3 interval so the detector-level derived status agrees with the experiment-level one; ongoing at verified_at."
    - note new: "The detector record carries the same Long Shutdown 3 interval as experiment:totem, whose interval note gives the evidence and CERN's wording for the bounds; the state is inferred from the LHC being shut down."
- /placements/0/note: `TOTEM's Roman Pots and T1/T2 telescopes extend along the beamline well beyond the CMS cavern itself, but share the same interaction point; placed at the existing site:cern-point-5-cms (owned by cern-cms), referenced only, per the id registry.` -> `TOTEM's Roman Pots and T1/T2 telescopes extend along the beamline well beyond the CMS cavern itself, but share the same interaction point; the detector is placed at the existing site:cern-point-5-cms.`
- notes, old text removed or rewritten: `VERIFIER FIX (2026-09-17): status corrected 'active' -> 'shutdown' and a Long Shutdown 3 interval added (mirroring experiment:totem), because the prior record's open-ended 'operating' interval made the detector derive as permanently active even while CERN's LHC -- TOTEM's only beam source -- is in Long Shutdown 3, contradicting experiment:totem's own status.`
- notes, new text: `Status shutdown matches experiment:totem (Long Shutdown 3).`

### data/atlas/detectors/xenonnt.json
- **interval ADDED** `start of operation / commissioning`: status=commissioning; confidence=approximate; start=2020; end=2021-07-06; quote: 'XENONnT started its operation with about 8.6 tonnes of xenon in 2020.'; sources: ['src:dm-noble-liquid-xenon-official-history', 'src:dm-noble-liquid-xenonnt-inspire-experiment']  (reason: the detector record had no interval for 2020 to July 2021, which experiment:xenonnt carries)
- **interval** `science operations`  (F25 part 2)
    - old: status=active; confidence=verified; start=2021-07-06; end={date=2025, display='before the summer-2025 upgrade', approx}
    - new: status=active; confidence=approximate; start=2021-07-06; end={date=2025, display='before the summer-2025 upgrade', approx}
    - locator old: 'end: ATHEXIS 2026 and LIDINE 2026 talk abstracts'
    - locator new: 'start: INSPIRE experiment record, field date_started; end: ATHEXIS 2026 and LIDINE 2026 talk abstracts'
    - note old: 'END ADDED 2026-10-25 at year precision: the collaboration describes a detector upgrade "carried out in summer 2025" (LIDINE 2026 abstract) after which "the experiment began its new commissioning phase in 2026" (ATHEXIS 2026 abstract). The date of the last science-run data is not given by any fetched source. Previously open-ended.'
    - note new: "Start = the date_started field of INSPIRE's experiment record (6 July 2021). The Nikhef slides of May 2026 list science runs SR0, SR1 and SR2 before the upgrade. The date of the last science-run data is not given by any source consulted, and the end is year precision: it is set to the 2025 detector upgrade, which the collaboration says was 'carried out in summer 2025' (LIDINE 2026 abstract), after which 'the experiment began its new commissioning phase in 2026' (ATHEXIS 2026 abstract). The last science data may predate the upgrade."
- **interval** `detector upgrade (new TPC electrodes, drift field 23 → 100 V/cm)`  (F25 part 2)
    - old: status=upgrade; confidence=approximate; start={date=2025, display='summer 2025', approx}; end={date=2026, approx}
    - new: status=upgrade; confidence=approximate; start={date=2025-07, display='summer 2025', earliest='2025-06', latest='2025-08', approx} note: "Summer is stored as July with June-August bounds: the LIDINE 2026 abstract says the upgrade was 'carried out in summer 2025'."; end={date=2026-03, display='first half of 2026', earliest='2026-01', latest='2026-06', approx} note: "Bounded by the ATHEXIS 2026 abstract ('began its new commissioning phase in 2026'; talk at a conference held 8-12 June 2026) and the Nikhef slides of May 2026 ('Everything back in place, 8.5 tons of LXe'); the month is not given by any source consulted. March is the midpoint of the January-June bounds, not a reported date."
    - note old: 'Month of start and end not given by any fetched source (the slide timeline labels a "12 month upgrade" starting in 2025).'
    - note new: "The upgrade replaced the TPC electrodes to raise the drift field from 23 V/cm to 100 V/cm. LIDINE 2026 abstract: 'an overview of the XENONnT detector upgrade carried out in summer 2025'. The Nikhef slides of May 2026 call it a '1-year long operation' ('12 month upgrade' on their timeline), in which the electrode replacement itself took a few weeks, and say 'Upgrade completed'. The ATHEXIS abstract says 'Following upgrade operations conducted in 2025' the commissioning phase began in 2026. No source consulted gives the month the upgrade began or ended; the end is the start of the recommissioning interval below, bounded to the first half of 2026."
- **interval** `commissioning after the 2025 upgrade` -> `Recommissioning after the 2025 upgrade (2026)`  (F25 part 2)
    - old: status=commissioning; confidence=approximate; start={date=2026, approx}; end=null
    - new: status=commissioning; confidence=approximate; start={date=2026-03, display='first half of 2026', earliest='2026-01', latest='2026-06', approx} note: "Bounded by the ATHEXIS 2026 abstract ('began its new commissioning phase in 2026'; talk at a conference held 8-12 June 2026) and the Nikhef slides of May 2026 ('Everything back in place, 8.5 tons of LXe'); the month is not given by any source consulted. March is the midpoint of the January-June bounds, not a reported date."; end=null
    - note old: 'Nikhef slides (May 2026): "Commissioning until July, then start of data taking". The LIDINE 2026 abstract (talk of 7 October 2026) still reports "the status and first results of the subsequent commissioning campaign"; no fetched source says that post-upgrade science data taking has started, so the state is commissioning, not active.'
    - note new: "Last documented state. The ATHEXIS 2026 abstract (conference 8-12 June 2026) says the experiment 'began its new commissioning phase in 2026'. The Nikhef slides of May 2026 say 'Commissioning until July, then start of data taking'. The LIDINE 2026 abstract (talk of 7 October 2026) still reports 'the status and first results of the subsequent commissioning campaign'. No source consulted says that post-upgrade science data taking has started or that commissioning has ended, so the state is shown as commissioning, not active; whether it is still commissioning at 2026-10-25 is not confirmed. Before the upgrade the experiment ran science operations from July 2021 (see the interval above)."

### data/atlas/experiments/alice.json
- **top-level status**: `shutdown` -> `upgrade`
- **interval** `Expression of Interest`  (wording cleanup)
    - old: status=proposed; confidence=approximate; start=1992; end=1993-03-01
    - new: status=proposed; confidence=approximate; start=1992; end=1993-03-01
    - note old: 'Year precision only (Evian workshop, 1992); the exact date within 1992 is not stated in the excerpt fetched.'
    - note new: 'Year precision only (Evian workshop, 1992); the exact date within 1992 is not stated in the excerpt consulted.'
- **interval** `Technical Proposal and addenda`  (wording cleanup)
    - old: status=proposed; confidence=approximate; start=1995; end=1997-02-06
    - new: status=proposed; confidence=approximate; start=1995; end=1997-02-06
    - note old: "Year precision only: the detector paper confirms the sequence (Expression of Interest -> Letter of Intent -> Technical Proposal -> Addenda -> 1997 approval) but does not give the Technical Proposal's exact date within this fetched text. CERN Courier ('New kid on the block') independently dates the forward-muon-spectrometer addendum to 1995 ('included as an addendum to the Letter of Intent in 1995'); the Technical Proposal itself (CERN/LHCC/95-71) is widely cited as 1995 but that exact report was not fetched this session, so this interval is marked approximate rather than verified."
    - note new: "Year precision only: the detector paper confirms the sequence (Expression of Interest -> Letter of Intent -> Technical Proposal -> Addenda -> 1997 approval) but does not give the Technical Proposal's exact date in the text consulted. CERN Courier ('New kid on the block') dates the forward-muon-spectrometer addendum to 1995 ('included as an addendum to the Letter of Intent in 1995'); the Technical Proposal itself was not consulted, so this interval is marked approximate rather than verified."
- **interval** `Run 1`  (wording cleanup)
    - old: status=active; confidence=approximate; start=2010-03-30; end={date=2013, approx} note: 'Run 1 ended in early 2013 with Long Shutdown 1; no ALICE-specific or CERN page fetched this session gives the exact end date.'
    - new: status=active; confidence=approximate; start=2010-03-30; end={date=2013, approx} note: 'Run 1 ended in early 2013 with Long Shutdown 1; no ALICE-specific or CERN page consulted gives the exact end date.'
    - note old: 'This is an LHC machine-wide schedule fact (all four main LHC experiments, including ALICE, took data through the same run); no ALICE-specific start/end announcement was found in this session beyond the general LHC schedule pages already fetched by the cern-atlas partition.'
    - note new: 'This is an LHC machine-wide schedule fact (all four main LHC experiments, including ALICE, took data through the same run); no ALICE-specific start/end announcement was found beyond the general LHC schedule pages.'
    - end.note old: 'Run 1 ended in early 2013 with Long Shutdown 1; no ALICE-specific or CERN page fetched this session gives the exact end date.'
    - end.note new: 'Run 1 ended in early 2013 with Long Shutdown 1; no ALICE-specific or CERN page consulted gives the exact end date.'
- **interval** `Long Shutdown 3` -> `Long Shutdown 3 / ITS3 and FoCal upgrade`  (F10/F25 LS3)
    - old: status=shutdown; confidence=approximate; start={date=2026-06, approx}; end={date=2029, approx, planned}
    - new: status=upgrade; confidence=approximate; start=2026-06-29; end={date=2030, display='mid-2030', approx, planned} note: 'CERN schedule: the LHC resumes operation in mid-2030; the rest of the CERN complex restarts in stages from mid-2028.'
    - quote old: "Following its final physics run, the accelerator has been switched off to begin CERN's Long Shutdown 3 (LS3)."
    - quote new: 'Two detector upgrades of ALICE ... have recently been approved for installation during the next long shutdown of the LHC'
    - locator old: 'null'
    - locator new: 'home.cern/science/long-shutdown-3, item of 5 August 2026 "The LHC is being warmed up from near absolute zero to room temperature"'
    - sources old: '["src:cern-ls3-farewell-2026", "src:cern-long-shutdown-3-page"]'
    - sources new: '["src:rc-alice-its3-focal-approval-2024", "src:rc-alice-its3-design-arxiv-2026", "src:colliders-lhc-alice-collaboration-site", "src:cern-long-shutdown-3-page", "src:cern-ls3-farewell-2026"]'
    - verified_at old: '2026-09-17'
    - verified_at new: '2026-10-25'
    - note old: "Machine-wide LHC fact. ALICE's own collaboration site separately states further ALICE detector upgrades continue 'for Run 4 until the end of 2033' and that R&D is underway for a next-generation 'ALICE 3' experiment for HL-LHC Run 5 (src:colliders-lhc-alice-collaboration-site) - recorded here as a note rather than a further dated interval since no specific ALICE 3 approval/construction date has been sourced."
    - note new: "ALICE's own detector is being upgraded in this shutdown: the ITS3 (replacing the three innermost tracking layers) and the FoCal forward calorimeter. CERN news of 25 April 2024, written by the ALICE collaboration, says the two upgrades 'have recently been approved for installation during the next long shutdown of the LHC'. The ALICE Collaboration's January 2026 paper (arXiv:2601.07405) says 'During the LHC Long Shutdown 3 (2026-29) ALICE will replace its three innermost tracking layers by a new detector'. ALICE's site says 'Further detector upgrades are being carried out for Run 4 until the end of 2033'; that describes the upgrade programme for Run 4 and does not date the end of this shutdown. The 2024 and 2026 ALICE-related sources give LS3 as 2026-28 and 2026-29; this interval follows CERN's later schedule, in which the LHC resumes operation in mid-2030. The 2024 article dated the ITS3 and FoCal installation to early 2028; no 2026 source consulted confirms the current installation schedule. ALICE takes no data in this period because the LHC is off. Start and end are the LHC-wide Long Shutdown 3 dates. CERN's 5 August 2026 item says 'The cryogenics team has been running the warm-up sequence since LS3 began on 29 June 2026' and that the stored helium is kept 'ready to be used again once the accelerator resumes operation in mid-2030'; CERN's 29 June 2026 article says 'The HiLumi LHC, scheduled to begin operation in 2030'. The end is a schedule value, not a reported event."
- notes, old text removed or rewritten: `Derived fields (detector_ids, site_ids, result_ids, document_ids) are deliberately not written (v0.2 A1).`
- notes, old text removed or rewritten: `CONFLICT on ALICE's overall depth: the detector paper (2008 JINST 3 S08002) gives the UX25 cavern floor as 52 m underground with 28 m of overburden; home.cern separately states the detector 'sits in a vast cavern 56 m below ground'. Both are recorded (see site:cern-point-2-alice); no fetched source reconciles the two figures.`
- notes, old text removed or rewritten: `The Technical Proposal's exact submission date (commonly cited elsewhere as CERN/LHCC/95-71, 1995) was not confirmed from a page fetched in this session; the 'Technical Proposal and addenda' interval is therefore year-precision and marked approximate rather than verified.`
- notes, old text removed or rewritten: `No spokesperson or other leadership figure is named on any page fetched this session; collaboration.leadership is left empty rather than guessed.`
- notes, new text: `CONFLICT on ALICE's overall depth: the detector paper (2008 JINST 3 S08002) gives the UX25 cavern floor as 52 m underground with 28 m of overburden; home.cern separately states the detector 'sits in a vast cavern 56 m below ground'. Both are recorded (see site:cern-point-2-alice); no source consulted reconciles the two figures.`
- notes, new text: `The Technical Proposal's exact submission date was not confirmed from any page consulted; the 'Technical Proposal and addenda' interval is therefore year-precision and marked approximate rather than verified.`
- notes, new text: `No page consulted names a spokesperson or other current leadership figure; collaboration.leadership is left empty rather than guessed.`

### data/atlas/experiments/atlas.json
- **interval** `Run 1`  (wording cleanup)
    - old: status=active; confidence=approximate; start=2010-03-30; end={date=2013, approx} note: 'Run 1 ended in early 2013 with Long Shutdown 1; no CERN or ATLAS page fetched in this session gives the exact date, so year precision only.'
    - new: status=active; confidence=approximate; start=2010-03-30; end={date=2013, approx} note: 'Run 1 ended in early 2013 with Long Shutdown 1; no CERN or ATLAS page consulted gives the exact date, so year precision only.'
    - end.note old: 'Run 1 ended in early 2013 with Long Shutdown 1; no CERN or ATLAS page fetched in this session gives the exact date, so year precision only.'
    - end.note new: 'Run 1 ended in early 2013 with Long Shutdown 1; no CERN or ATLAS page consulted gives the exact date, so year precision only.'
- **interval** `Long Shutdown 3 / Phase-II upgrade`  (F10/F25 LS3)
    - old: status=upgrade; confidence=approximate; start=2026-06; end={date=2029, approx, planned}
    - new: status=upgrade; confidence=approximate; start=2026-06-29; end={date=2030, display='mid-2030', approx, planned} note: 'CERN schedule: the LHC resumes operation in mid-2030; the rest of the CERN complex restarts in stages from mid-2028.'
    - quote old: 'They will all be installed and commissioned during LS3 in time for the start of Run 4, currently planned for 2029.'
    - quote new: 'In the LHC caverns, the ATLAS and CMS experiments will undergo extensive upgrades, effectively becoming renewed detectors.'
    - locator old: 'null'
    - locator new: 'home.cern/science/long-shutdown-3, item of 5 August 2026 "The LHC is being warmed up from near absolute zero to room temperature"'
    - sources old: '["src:atlas-high-luminosity-feature", "src:cern-long-shutdown-3-page", "src:cern-ls3-farewell-2026"]'
    - sources new: '["src:atlas-high-luminosity-feature", "src:cern-long-shutdown-3-page", "src:cern-ls3-farewell-2026", "src:rc-atlas-hilumi-upgrades-page"]'
    - verified_at old: '2026-09-16'
    - verified_at new: '2026-10-25'
    - note old: 'Replacement of the inner tracker by the ITk, installation of the HGTD, new trigger/DAQ and new calorimeter and muon front-end electronics.'
    - note new: "Replacement of the inner tracker by the ITk, installation of the HGTD, new trigger/DAQ and new calorimeter and muon front-end electronics. Start and end are the LHC-wide Long Shutdown 3 dates. CERN's 5 August 2026 item says 'The cryogenics team has been running the warm-up sequence since LS3 began on 29 June 2026' and that the stored helium is kept 'ready to be used again once the accelerator resumes operation in mid-2030'; CERN's 29 June 2026 article says 'The HiLumi LHC, scheduled to begin operation in 2030'. The end is a schedule value, not a reported event. ATLAS's own page says the new detector technologies 'are being installed at CERN during the long shutdown period prior to 2030'. An earlier end of 2029 came from ATLAS's January 2023 feature article ('Run 4, currently planned for 2029'); that article predates CERN's October 2024 schedule revision, which moved the HL-LHC start-up to June 2030, so the 2029 date is superseded."
- **interval** `Run 4 (HL-LHC)`  (F10/F25 LS3)
    - old: status=planned; confidence=approximate; start={date=2029, approx, planned}; end=null
    - new: status=planned; confidence=approximate; start={date=2030, display='mid-2030', approx, planned} note: "CERN: 'once the accelerator resumes operation in mid-2030' (Long Shutdown 3 page, item of 5 August 2026)."; end=null
    - quote old: 'The high-luminosity phase of the LHC (HL-LHC) will provide an order of magnitude more data starting from 2029.'
    - quote new: 'The start-up of the HL-LHC (Run 4) is now planned for June 2030.'
    - sources old: '["src:atlas-high-luminosity-feature"]'
    - sources new: '["src:cern-long-shutdown-3-page", "src:rc-atlas-hilumi-upgrades-page", "src:rc-cern-new-schedule-2024"]'
    - verified_at old: '2026-09-16'
    - verified_at new: '2026-10-25'
    - note old: "Schedule value. CONFLICT: CERN's accelerator pages date the start of HL-LHC operation to 2030 (see accelerator:hl-lhc)."
    - note new: "Schedule value. CERN's 8 October 2024 article says 'The start-up of the HL-LHC (Run 4) is now planned for June 2030', and CERN's Long Shutdown 3 page (2026) gives mid-2030 for the accelerator's resumption. ATLAS's own January 2023 feature article still says 'starting from 2029' and 'currently planned for 2029'; it predates the revised schedule and is not used here. ATLAS's current HL-LHC page gives the HL-LHC era as 2030-2041."
- /unique_capabilities/0/note: `Muon deflection in the superconducting air-core toroids is stated in arXiv:2007.12539, section 2 (Run-2 detector description): "to measure the deflection of muons in a magnetic field generated by the superconducting air-core toroids". Value reworded from "The only LHC detector using ... which sets its overall size" because no fetched source states exclusivity or that the muon system sets the overall size; the official page calls the central toroid unique in particle physics.` -> `Muon deflection in the superconducting air-core toroids is stated in arXiv:2007.12539, section 2 (Run-2 detector description): "to measure the deflection of muons in a magnetic field generated by the superconducting air-core toroids". Value reworded from "The only LHC detector using ... which sets its overall size" because no source consulted states exclusivity or that the muon system sets the overall size; the official page calls the central toroid unique in particle physics.`
- /unique_capabilities/1/note: `Hermetic wording is from the official physics page: "The hermetic construction of ATLAS, however, makes it possible to search for this “dark matter”." Value reworded from "enabling missing-transverse-energy searches" (no fetched source states that phrase) to what the sources state.` -> `Hermetic wording is from the official physics page: "The hermetic construction of ATLAS, however, makes it possible to search for this “dark matter”." Value reworded from "enabling missing-transverse-energy searches" (no source consulted states that phrase) to what the sources state.`
- notes, old text removed or rewritten: `ATLAS was formed from the merger of the ASCOT and EAGLE proposals; no page fetched in this session states that on the record, so it is not carried as a sourced value.`
- notes, new text: `ATLAS was formed from the merger of the ASCOT and EAGLE proposals; no page consulted states that on the record, so it is not carried as a sourced value.`

### data/atlas/experiments/cms.json
- **interval** `Approved`  (wording cleanup)
    - old: status=approved; confidence=derived; start=1996-01-31; end=1998
    - new: status=approved; confidence=derived; start=1996-01-31; end=1998
    - note old: "Approval date from the INSPIRE experiment record. CMS's own history timeline instead labels 1993 'CMS project approved' — see worklog conflict C1. The end is derived from the start of construction at Point 5."
    - note new: "Approval date from the INSPIRE experiment record. CMS's own history timeline instead labels 1993 'CMS project approved'; the INSPIRE date is used here and the two are not reconciled. The end is derived from the start of construction at Point 5."
- **interval** `LHC Run 2`  (wording cleanup)
    - old: status=active; confidence=uncertain; start=2015; end=2018-12-03
    - new: status=active; confidence=uncertain; start=2015; end=2018-12-03
    - note old: "CERN states Run 2 ended on 3 December 2018 'after three fantastic years'. The exact 2015 restart date could not be confirmed from a source fetched in this session, so the start is recorded at year precision."
    - note new: "CERN states Run 2 ended on 3 December 2018 'after three fantastic years'. No source consulted gives the exact 2015 restart date, so the start is recorded at year precision."
- **interval** `Long Shutdown 3 — Phase-2 upgrade`  (F10/F25 LS3)
    - old: status=upgrade; confidence=verified; start=2026-06; end={date=2030, approx, planned} note: 'HiLumi LHC scheduled to begin operation in 2030'
    - new: status=upgrade; confidence=approximate; start=2026-06-29; end={date=2030, display='mid-2030', approx, planned} note: 'CERN schedule: the LHC resumes operation in mid-2030; the rest of the CERN complex restarts in stages from mid-2028.'
    - quote old: "As of mid-2026, the accelerator complex and experimental facilities at CERN are undergoing major maintenance and upgrade work. This phase, known as 'Long Shutdown 3' or 'LS3', is expected to last up to four years."
    - quote new: 'In the LHC caverns, the ATLAS and CMS experiments will undergo extensive upgrades, effectively becoming renewed detectors.'
    - locator old: 'null'
    - locator new: 'home.cern/science/long-shutdown-3, item of 5 August 2026 "The LHC is being warmed up from near absolute zero to room temperature"'
    - verified_at old: '2026-09-16'
    - verified_at new: '2026-10-25'
    - note old: 'Phase-2 upgrade of CMS for the HL-LHC: new all-silicon tracker, new high-granularity endcap calorimeter, MIP timing detector, muon system extensions and a new trigger/DAQ. The end date is from CERN’s schedule and is marked planned.'
    - note new: "Phase-2 upgrade of CMS for the HL-LHC: new all-silicon tracker, new high-granularity endcap calorimeter, MIP timing detector, muon system extensions and a new trigger/DAQ. Work is under way: CERN's Long Shutdown 3 page reports 'Work on the CMS muon system upgrade is now underway' (17 September 2026) and 'The core of the CMS experiment, the pixel detector, has now been removed after 10 years of successful operations.' (19 October 2026). Start and end are the LHC-wide Long Shutdown 3 dates. CERN's 5 August 2026 item says 'The cryogenics team has been running the warm-up sequence since LS3 began on 29 June 2026' and that the stored helium is kept 'ready to be used again once the accelerator resumes operation in mid-2030'; CERN's 29 June 2026 article says 'The HiLumi LHC, scheduled to begin operation in 2030'. The end is a schedule value, not a reported event."
- /key_specs/2/quantity/note: `CMS outreach pages also quote 14 000 t; see worklog conflict C2.` -> `CMS outreach pages also quote 14 000 t; this record uses the 12 500 t of the 2008 detector paper and CERN's Point 5 page, and the two figures are not reconciled (see detector:cms).`
- notes, old text removed or rewritten: `The CERN Greybook record could not be read in this session (the Greybook page returned no content to the fetcher), so the external.greybook code is null.`
- notes, old text removed or rewritten: `facility:cern, accelerator:lhc and accelerator:hl-lhc are owned by the cern-atlas workstream and are referenced here, not created.`
- notes, new text: `The CERN Greybook record could not be read (the Greybook page returned no content), so the external.greybook code is null.`

### data/atlas/experiments/faser.json
- **interval** `Run 3 (data-taking)`  (wording cleanup)
    - old: status=active; confidence=verified; start=2022-07; end={date=2026-06, approx} note: "VERIFIER FIX (2026-09-17): capped at the LHC-wide Long Shutdown 3 boundary (see the added interval below); previously open-ended (end: null). FASER has no beam source other than the LHC, so it cannot be 'active' while the LHC itself is shut down for LS3 (as already correctly modelled for experiment:alice, experiment:lhcb and experiment:totem in this same partition)."
    - new: status=active; confidence=verified; start=2022-07; end={date=2026-06, approx} note: 'Ends at the LHC-wide start of Long Shutdown 3 (June 2026); FASER has no beam source other than the LHC, so it cannot be active while the LHC is shut down.'
    - end.note old: "VERIFIER FIX (2026-09-17): capped at the LHC-wide Long Shutdown 3 boundary (see the added interval below); previously open-ended (end: null). FASER has no beam source other than the LHC, so it cannot be 'active' while the LHC itself is shut down for LS3 (as already correctly modelled for experiment:alice, experiment:lhcb and experiment:totem in this same partition)."
    - end.note new: 'Ends at the LHC-wide start of Long Shutdown 3 (June 2026); FASER has no beam source other than the LHC, so it cannot be active while the LHC is shut down.'
- **interval** `Long Shutdown 3`  (F10/F25 LS3)
    - old: status=shutdown; confidence=verified; start=2026-06; end=null
    - new: status=shutdown; confidence=derived; start=2026-06-29; end={date=2030, display='mid-2030', approx, planned} note: 'CERN schedule: the LHC resumes operation in mid-2030; the rest of the CERN complex restarts in stages from mid-2028.'
    - quote old: 'null'
    - quote new: 'Following its final physics run, the accelerator has been switched off to begin CERN’s Long Shutdown 3 (LS3) ... The HiLumi LHC, scheduled to begin operation in 2030'
    - locator old: "reused from accelerator:lhc's sourced Long Shutdown 3 interval (src:cern-ls3-farewell-2026)"
    - locator new: 'home.cern/science/long-shutdown-3, item of 5 August 2026 "The LHC is being warmed up from near absolute zero to room temperature"'
    - sources old: '["src:cern-ls3-farewell-2026"]'
    - sources new: '["src:cern-long-shutdown-3-page", "src:cern-ls3-farewell-2026", "src:rc-faser-neutrino-upgrade-2025"]'
    - verified_at old: '2026-09-17'
    - verified_at new: '2026-10-25'
    - note old: 'VERIFIER-ADDED (2026-09-17): FASER only detects particles from LHC collisions, so it shares the LHC-wide Long Shutdown 3 interval already sourced for ALICE, LHCb and TOTEM in this partition; ongoing at verified_at.'
    - note new: "FASER detects particles produced in LHC collisions, so it is idle while the LHC is shut down; this is an inference, since no FASER-specific statement about this shutdown was found. Status is shutdown, not upgrade. The collaboration's home page (checked 2026-10-25) does not mention LS3 or an upgrade. No source consulted says that upgrade work on FASER is under way in LS3. FASER's collaboration plans an upgraded neutrino detector: 'The current plan is to implement the upgrade of the FASER detector by the start of the LHC Run 4.' (FASER Collaboration, arXiv:2503.19775, March 2025). That is a plan, not a report of work in progress. Start and end are the LHC-wide Long Shutdown 3 dates. CERN's 5 August 2026 item says 'The cryogenics team has been running the warm-up sequence since LS3 began on 29 June 2026' and that the stored helium is kept 'ready to be used again once the accelerator resumes operation in mid-2030'; CERN's 29 June 2026 article says 'The HiLumi LHC, scheduled to begin operation in 2030'. The end is a schedule value, not a reported event."
- /energy_regime/note: `No FASER-specific energy value distinct from the LHC-wide Run 3 energy was found in this session.` -> `No FASER-specific energy value distinct from the LHC-wide Run 3 energy was found.`
- notes, old text removed or rewritten: `Derived fields (detector_ids, site_ids, result_ids, document_ids) deliberately not written (v0.2 A1).`
- notes, old text removed or rewritten: `Mandatory-bar-only pass: no results/technical documents written (FASER is not a wave-3 flagship).`
- notes, old text removed or rewritten: `VERIFIER FIX (2026-09-17): status corrected 'active' -> 'shutdown' and a Long Shutdown 3 interval added, reusing the same LHC-wide LS3 source already cited for ALICE/LHCb/TOTEM. The prior record left FASER's data-taking interval open-ended, so it derived as permanently active even though FASER cannot record anything while its only beam source (the LHC) is off for LS3.`
- notes, new text: `No results or technical documents are recorded for FASER yet.`
- notes, new text: `FASER cannot record anything while its only beam source (the LHC) is off for LS3, so its data-taking interval ends at the start of Long Shutdown 3 and its status is shutdown.`

### data/atlas/experiments/lhcb.json
- **top-level status**: `shutdown` -> `upgrade`
- **interval** `construction and installation`  (wording cleanup)
    - old: status=construction; confidence=uncertain; start=1998-09-17; end=2008-09
    - new: status=construction; confidence=uncertain; start=1998-09-17; end=2008-09
    - note old: "Start = date_approved (1998-09-17). VERIFIER NOTE (2026-09-17): end = INSPIRE's date_completed field, re-fetched and confirmed to read '2008-09' verbatim (not fabricated). But this field is NOT a routine construction-milestone field: on ATLAS's INSPIRE record (1108541) and on LHCf's (1126263), the same date_completed field reads '9999', which both those records correctly treat as INSPIRE's placeholder for 'ongoing, not completed' rather than a real date (see experiment:lhcf's interval note). LHCb is likewise an active, non-terminal experiment, so a literal 'completed' date is intrinsically implausible; unlike ATLAS/LHCf, LHCb's record has an actual date in this field rather than the placeholder, which is most likely either (a) a genuine INSPIRE data-entry anomaly, or (b) a real but differently-scoped milestone (e.g. detector installation/construction complete, consistent with first collisions 14 months later) that INSPIRE's schema does not distinguish from experiment completion. No source independent of this one INSPIRE field corroborates a September 2008 construction-complete date for LHCb, so confidence is downgraded from 'verified' to 'uncertain' and this interval must not be read as asserting LHCb 'completed' in 2008 (it is deliberately given the non-terminal status 'construction', not 'completed', for exactly this reason). Re-verify against the LHCb JINST detector paper or an LHCb-specific installation announcement if either becomes fetchable."
    - note new: "Start = date_approved (1998-09-17). End = INSPIRE's date_completed field, which reads '2008-09'. That field is not a routine construction-milestone field: on ATLAS's INSPIRE record (1108541) and on LHCf's (1126263) the same field reads '9999', which both records treat as INSPIRE's placeholder for 'ongoing, not completed' rather than a real date. LHCb is likewise an active, non-terminal experiment, so a literal 'completed' date is implausible; the value is most likely either an INSPIRE data-entry anomaly or a differently scoped milestone (for example detector installation or construction complete, consistent with first collisions 14 months later). No source independent of this one INSPIRE field corroborates a September 2008 construction-complete date for LHCb, so confidence is 'uncertain' and the interval is given the non-terminal status 'construction', not 'completed'; it must not be read as asserting that LHCb completed in 2008. The LHCb JINST detector paper or an LHCb-specific installation announcement would settle it."
- **interval** `Run 1`  (wording cleanup)
    - old: status=active; confidence=approximate; start=2010-03-30; end={date=2013, approx} note: 'Run 1 ended in early 2013 with Long Shutdown 1; no LHCb- or CERN-specific page fetched in this session gives the exact end date, so year precision only.'
    - new: status=active; confidence=approximate; start=2010-03-30; end={date=2013, approx} note: 'Run 1 ended in early 2013 with Long Shutdown 1; no LHCb- or CERN-specific page consulted gives the exact end date, so year precision only.'
    - locator old: "home.cern 'Key figures' table (reused from accelerator:lhc)"
    - locator new: "home.cern 'Key figures' table; the same Run 1 dates as accelerator:lhc"
    - note old: "LHCb records data throughout LHC Run 1 as one of the four main LHC experiments; dates reused from accelerator:lhc's sourced Run 1 interval since no LHCb-specific start/end date was found."
    - note new: "LHCb records data throughout LHC Run 1 as one of the four main LHC experiments; the dates are the LHC's Run 1 dates (accelerator:lhc), since no LHCb-specific start/end date was found."
    - end.note old: 'Run 1 ended in early 2013 with Long Shutdown 1; no LHCb- or CERN-specific page fetched in this session gives the exact end date, so year precision only.'
    - end.note new: 'Run 1 ended in early 2013 with Long Shutdown 1; no LHCb- or CERN-specific page consulted gives the exact end date, so year precision only.'
- **interval** `Long Shutdown 1`  (wording cleanup)
    - old: status=shutdown; confidence=uncertain; start={date=2013, approx}; end={date=2015, approx}
    - new: status=shutdown; confidence=uncertain; start={date=2013, approx}; end={date=2015, approx}
    - note old: "Bounded by the same sourced facts used for accelerator:lhc's Long Shutdown 1 interval; no LHCb-specific announcement was fetched in this session."
    - note new: "Bounded by the same sourced facts used for accelerator:lhc's Long Shutdown 1 interval; no LHCb-specific announcement was consulted."
- **interval** `Run 2`  (wording cleanup)
    - old: status=active; confidence=verified; start=2015; end=2018-12-03
    - new: status=active; confidence=verified; start=2015; end=2018-12-03
    - locator old: "reused from accelerator:lhc's sourced Run 2 interval"
    - locator new: "the same Run 2 dates as accelerator:lhc's sourced interval"
    - note old: 'LHCb records data throughout LHC Run 2; dates reused from accelerator:lhc since no LHCb-specific start/end date was found in this session.'
    - note new: "LHCb records data throughout LHC Run 2; the dates are the LHC's (accelerator:lhc), since no LHCb-specific start/end date was found."
- **interval** `Long Shutdown 2 / LHCb Upgrade I installation`  (wording cleanup)
    - old: status=upgrade; confidence=verified; start=2018-12-03; end=2023-04
    - new: status=upgrade; confidence=verified; start=2018-12-03; end=2023-04
    - note old: "CONFLICT/nuance: the LHC-wide Long Shutdown 2 ended and Run 3 pp collisions began on 5 July 2022 (see accelerator:lhc), but LHCb's own outreach page dates the completion of Upgrade I *installation* specifically to April 2023, nine months later. This record follows the LHCb-specific completion date rather than the LHC-wide Run 3 start, since Upgrade I (new VELO, new tracker, removal of the hardware trigger) is an LHCb-specific programme; the discrepancy likely reflects LHCb running in a partial/commissioning capacity for the first months of Run 3 while Upgrade I installation finished. No source fetched in this session resolves this explicitly."
    - note new: "The LHC-wide Long Shutdown 2 ended and Run 3 pp collisions began on 5 July 2022 (see accelerator:lhc), but LHCb's own outreach page dates the completion of Upgrade I installation to April 2023, nine months later. This interval follows the LHCb-specific completion date, since Upgrade I (new VELO, new tracker, removal of the hardware trigger) is an LHCb-specific programme. The gap likely reflects LHCb running in a partial or commissioning capacity for the first months of Run 3 while installation finished; no source consulted states this explicitly."
- **interval** `Run 3 (LHCb Upgrade I)`  (wording cleanup)
    - old: status=active; confidence=approximate; start=2023-04; end=2026-06
    - new: status=active; confidence=approximate; start=2023-04; end=2026-06
    - locator old: 'start: LHCb collaboration turns 30 page (Upgrade I installation completed April 2023); end: reused from accelerator:lhc, CERN LS3 announcement of 29 June 2026 (quote on the next interval)'
    - locator new: 'start: LHCb collaboration turns 30 page (Upgrade I installation completed April 2023); end: CERN LS3 announcement of 29 June 2026, the same switch-off date as accelerator:lhc'
    - note old: 'Start = LHCb Upgrade I installation completion (see previous interval); end = the LHC-wide switch-off for Long Shutdown 3, reused from accelerator:lhc.'
    - note new: 'Start = LHCb Upgrade I installation completion (see previous interval); end = the LHC-wide switch-off for Long Shutdown 3 (accelerator:lhc).'
- **interval** `Long Shutdown 3` -> `Long Shutdown 3 / ECAL and RICH enhancements`  (F10/F25 LS3)
    - old: status=shutdown; confidence=verified; start=2026-06; end=null
    - new: status=upgrade; confidence=approximate; start=2026-06-29; end={date=2030, display='mid-2030', approx, planned} note: 'CERN schedule: the LHC resumes operation in mid-2030; the rest of the CERN complex restarts in stages from mid-2028.'
    - quote old: '29 June, 2026 ... Following its final physics run, the accelerator has been switched off to begin CERN’s Long Shutdown 3 (LS3)'
    - quote new: 'The LHCb experiment will upgrade the inner part of the Electromagnetic Calorimeter and the electronics of the Ring Imaging Cherenkov detectors in the next LHC Long Shutdown (LS3).'
    - locator old: "CERN LS3 announcement, 29 June 2026; reused from accelerator:lhc's sourced Long Shutdown 3 interval"
    - locator new: 'home.cern/science/long-shutdown-3, item of 5 August 2026 "The LHC is being warmed up from near absolute zero to room temperature"'
    - sources old: '["src:cern-ls3-farewell-2026"]'
    - sources new: '["src:rc-lhcb-ecal-rich-enhancements-2024", "src:rc-lhcb-ecal-ls3-jinst-2026", "src:cern-long-shutdown-3-page", "src:cern-ls3-farewell-2026"]'
    - note old: "Ongoing at verified_at, matching accelerator:lhc's current status. No LHCb-specific Upgrade II activity is confirmed to be underway in this shutdown in any source fetched this session (LHCb Upgrade II is generally planned for LS4 in the early 2030s, not sourced here)."
    - note new: "LHCb's own detector is being enhanced in this shutdown: the inner part of the electromagnetic calorimeter (ECAL) is replaced and the RICH electronics are upgraded. LHCb's outreach site (8 May 2024) says 'The LHCb experiment will upgrade the inner part of the Electromagnetic Calorimeter and the electronics of the Ring Imaging Cherenkov detectors in the next LHC Long Shutdown (LS3)'. The LHCb ECAL group's JINST paper (published 11 March 2026) says 'An enhancement of the LHCb electromagnetic calorimeter (ECAL) is foreseen during Long Shutdown 3 (LS3) of the LHC' and 'In total, 176 new SpaCal modules with radiation-tolerant scintillating plastic fibers will be installed during LS3'. These are plans for the shutdown; no source consulted reports the installation as under way or finished. The main Upgrade II is a later step: 'Upgrade II will be installed during Long Shutdown 4 (LS4)' (LHCb outreach site, 2024). The 2024 page gives LS3 as 'currently scheduled for the years 2026–28'; this interval follows CERN's later schedule, in which the LHC resumes operation in mid-2030. Start and end are the LHC-wide Long Shutdown 3 dates. CERN's 5 August 2026 item says 'The cryogenics team has been running the warm-up sequence since LS3 began on 29 June 2026' and that the stored helium is kept 'ready to be used again once the accelerator resumes operation in mid-2030'; CERN's 29 June 2026 article says 'The HiLumi LHC, scheduled to begin operation in 2030'. The end is a schedule value, not a reported event."
- /energy_regime/note: `LHCb shares the LHC's collision energy history (see accelerator:lhc); no LHCb-specific energy value distinct from the LHC-wide figures was found in this session.` -> `LHCb shares the LHC's collision energy history (see accelerator:lhc); no LHCb-specific energy value distinct from the LHC-wide figures was found.`
- /key_specs/0/quantity/note: `CONFLICT: lhcb-outreach.web.cern.ch's own detector page states the detector mass as '4,500 tonne' without giving a breakdown; this record uses the 5600 t figure because it is independently corroborated, verbatim, by both the INSPIRE experiment registry and home.cern, whereas the outreach-page figure could not be confirmed with a verbatim quote in this session. Flagged for review.` -> `LHCb's outreach site gives its own detector page's mass as '4,500 tonne' without a breakdown. This record uses the 5600 t figure because both the INSPIRE experiment registry and home.cern state it verbatim, whereas the outreach-page figure could not be confirmed with a verbatim quote; the two figures are not reconciled.`
- notes, old text removed or rewritten: `Derived fields (detector_ids, site_ids, result_ids, document_ids) are deliberately not written (v0.2 A1).`
- notes, old text removed or rewritten: `A joint CMS+LHCb result, result:cms-lhcb-bs-to-mumu-observation-2015, already exists (owned by the cern-cms workstream) for the 2015 observation of the rare decay Bs⁰→μ⁺μ⁻; it is not duplicated here and is not referenced in result_ids since that field is derived/not authored (A1), but is worth noting as a related joint LHCb result.`
- notes, old text removed or rewritten: `CERN Greybook was not fetched in this session (external.greybook left null); INSPIRE experiment record 1110643 was used instead per the source hierarchy (Greybook/INSPIRE experiment record share rank 3).`
- notes, old text removed or rewritten: `Pseudorapidity coverage, dipole magnet field integral and RICH/VELO technical specs were sought (lhcb-outreach detector page, JINST detector paper) but the JINST PDF was blocked by CERN's bot-detection (Anubis) and exceeded the fetch size limit at its mirror; only the abstract was retrieved via the INSPIRE literature API. These specs are left out rather than guessed.`
- notes, new text: `A joint CMS+LHCb result, result:cms-lhcb-bs-to-mumu-observation-2015 (the 2015 observation of the rare decay Bs⁰→μ⁺μ⁻), has its own record and is not duplicated here.`
- notes, new text: `CERN Greybook was not consulted (external.greybook is null); INSPIRE experiment record 1110643 was used instead (Greybook and the INSPIRE experiment record share source rank 3).`
- notes, new text: `Pseudorapidity coverage, dipole magnet field integral and RICH/VELO technical specs were sought (LHCb outreach detector page, JINST detector paper), but the JINST PDF was blocked by CERN's bot protection and exceeded the fetch size limit at its mirror; only the abstract was retrieved, via the INSPIRE literature API. These specs are left out rather than guessed.`

### data/atlas/experiments/lhcf.json
- **interval** `operating`  (wording cleanup)
    - old: status=active; confidence=verified; start=2009-11-23; end={date=2026-06, approx} note: "VERIFIER FIX (2026-09-17): capped at the LHC-wide Long Shutdown 3 boundary (see the added interval below); previously open-ended (end: null). LHCf only records LHC beam particles, so it cannot be 'active' while the LHC itself is off for LS3."
    - new: status=active; confidence=verified; start=2009-11-23; end={date=2026-06, approx} note: 'Ends at the LHC-wide start of Long Shutdown 3 (June 2026); LHCf only records LHC beam particles, so it cannot be active while the LHC is off.'
    - note old: "INSPIRE's date_completed field for this record is '9999' -- INSPIRE's own placeholder for 'not completed/ongoing', not a real date -- so it is not used. Public knowledge is that LHCf ran mainly in short low-luminosity periods early in each LHC run (2009-2010, 2013, 2015-2016) and does not run continuously through high-luminosity physics, but no source fetched in this session states that schedule at reviewable precision, so a single open (now LS3-capped) 'active' interval is recorded instead of a richer run-by-run history."
    - note new: "INSPIRE's date_completed field for this record is '9999', INSPIRE's own placeholder for 'not completed/ongoing' and not a real date, so it is not used. No source consulted gives LHCf's run-by-run schedule, so a single operating interval, ending at the start of Long Shutdown 3, is recorded instead of a richer run-by-run history."
    - end.note old: "VERIFIER FIX (2026-09-17): capped at the LHC-wide Long Shutdown 3 boundary (see the added interval below); previously open-ended (end: null). LHCf only records LHC beam particles, so it cannot be 'active' while the LHC itself is off for LS3."
    - end.note new: 'Ends at the LHC-wide start of Long Shutdown 3 (June 2026); LHCf only records LHC beam particles, so it cannot be active while the LHC is off.'
- **interval** `Long Shutdown 3`  (F10/F25 LS3)
    - old: status=shutdown; confidence=verified; start=2026-06; end=null
    - new: status=shutdown; confidence=derived; start=2026-06-29; end={date=2030, display='mid-2030', approx, planned} note: 'CERN schedule: the LHC resumes operation in mid-2030; the rest of the CERN complex restarts in stages from mid-2028.'
    - quote old: 'null'
    - quote new: 'Following its final physics run, the accelerator has been switched off to begin CERN’s Long Shutdown 3 (LS3) ... The HiLumi LHC, scheduled to begin operation in 2030'
    - locator old: "reused from accelerator:lhc's sourced Long Shutdown 3 interval (src:cern-ls3-farewell-2026)"
    - locator new: 'home.cern/science/long-shutdown-3, item of 5 August 2026 "The LHC is being warmed up from near absolute zero to room temperature"'
    - sources old: '["src:cern-ls3-farewell-2026"]'
    - sources new: '["src:cern-long-shutdown-3-page", "src:cern-ls3-farewell-2026"]'
    - verified_at old: '2026-09-17'
    - verified_at new: '2026-10-25'
    - note old: 'VERIFIER-ADDED (2026-09-17): LHCf only detects particles from LHC collisions, so it shares the LHC-wide Long Shutdown 3 interval already sourced for ALICE, LHCb and TOTEM in this partition; ongoing at verified_at.'
    - note new: "LHCf records particles produced in LHC collisions, so it is idle while the LHC is shut down; this is an inference, since no LHCf-specific statement about this shutdown was found. Status is shutdown, not upgrade. No source consulted says that LHCf's own detector is being modified in LS3. Start and end are the LHC-wide Long Shutdown 3 dates. CERN's 5 August 2026 item says 'The cryogenics team has been running the warm-up sequence since LS3 began on 29 June 2026' and that the stored helium is kept 'ready to be used again once the accelerator resumes operation in mid-2030'; CERN's 29 June 2026 article says 'The HiLumi LHC, scheduled to begin operation in 2030'. The end is a schedule value, not a reported event."
- notes, old text removed or rewritten: `Derived fields (detector_ids, site_ids, result_ids, document_ids) deliberately not written (v0.2 A1).`
- notes, old text removed or rewritten: `Per the id registry, LHCf does not get a new site: its detector:lhcf record places at the existing site:cern-point-1-atlas (owned by cern-atlas), referenced only, not edited.`
- notes, old text removed or rewritten: `Mandatory-bar-only pass: no results/technical documents written (LHCf is not a wave-3 flagship).`
- notes, old text removed or rewritten: `VERIFIER FIX (2026-09-17): status corrected 'active' -> 'shutdown' and a Long Shutdown 3 interval added, reusing the same LHC-wide LS3 source already cited for ALICE/LHCb/TOTEM. The prior record left LHCf's operating interval open-ended, so it derived as permanently active even though LHCf cannot record anything while its only beam source (the LHC) is off for LS3.`
- notes, new text: `LHCf has no site record of its own: detector:lhcf is placed at the existing site:cern-point-1-atlas.`
- notes, new text: `No results or technical documents are recorded for LHCf yet.`
- notes, new text: `LHCf cannot record anything while its only beam source (the LHC) is off for LS3, so its operating interval ends at the start of Long Shutdown 3 and its status is shutdown.`

### data/atlas/experiments/moedal.json
- **interval** `MAPP upgrade approved`  (wording cleanup)
    - old: status=upgrade; confidence=verified; start=2021; end=null
    - new: status=upgrade; confidence=verified; start=2021; end=null
    - note old: 'Secondary label: MAPP (MoEDAL Apparatus for Penetrating Particles) is an approved extension to the main MoEDAL detector, not a full replacement; both intervals are treated as covering the same experiment record with an added label rather than as a separate experiment id, since no source fetched in this session treats MAPP as a distinct experiment with its own approval/collaboration.'
    - note new: 'Secondary label: MAPP (MoEDAL Apparatus for Penetrating Particles) is an approved extension to the main MoEDAL detector, not a full replacement; both intervals cover the same experiment record under an added label rather than a separate experiment id, since no source consulted treats MAPP as a distinct experiment with its own approval or collaboration.'
- **interval** `Long Shutdown 3`  (F10/F25 LS3)
    - old: status=shutdown; confidence=derived; start={date=2026-06, approx}; end=null
    - new: status=shutdown; confidence=derived; start=2026-06-29; end={date=2030, display='mid-2030', approx, planned} note: 'CERN schedule: the LHC resumes operation in mid-2030; the rest of the CERN complex restarts in stages from mid-2028.'
    - quote old: 'On Saturday 27 June at 6 am, the LHC’s Page 1 — the accelerator’s dashboard — said “goodbye” to collisions. The LHC operators dumped the last beams before the accelerator’s metamorphosis.'
    - quote new: 'Following its final physics run, the accelerator has been switched off to begin CERN’s Long Shutdown 3 (LS3) ... The HiLumi LHC, scheduled to begin operation in 2030'
    - locator old: 'null'
    - locator new: 'home.cern/science/long-shutdown-3, item of 5 August 2026 "The LHC is being warmed up from near absolute zero to room temperature"'
    - sources old: '["src:cern-long-shutdown-3-page", "src:cern-ls3-farewell-2026"]'
    - sources new: '["src:cern-long-shutdown-3-page", "src:cern-ls3-farewell-2026", "src:rc-moedal-mapp-pinfold-2023"]'
    - note old: 'Derived from the LHC-wide shutdown, as for the other LHC experiments in this atlas; no MoEDAL-specific announcement was fetched. Source for the shutdown: "On Saturday 27 June at 6 am, the LHC’s Page 1 — the accelerator’s dashboard — said “goodbye” to collisions. The LHC operators dumped the last beams before the accelerator’s metamorphosis." (home.cern, item dated 29 June 2026).'
    - note new: "MoEDAL searches for particles produced in LHC collisions, so it is idle while the LHC is shut down; this is an inference, since no MoEDAL-specific statement about this shutdown was found. Status is shutdown, not upgrade. The collaboration's home page (checked 2026-10-25) does not mention LS3 or an upgrade. No source consulted says that upgrade work on MoEDAL is under way in LS3. A 2022-23 paper describes MAPP-2, a planned second phase of the MAPP detector, as 'planned for installation during the long shutdown (LS3) prior to the startup of HL-LHC' (J. Pinfold, arXiv:2209.03988 v2); no 2026 source consulted confirms that installation has begun. Start and end are the LHC-wide Long Shutdown 3 dates. CERN's 5 August 2026 item says 'The cryogenics team has been running the warm-up sequence since LS3 began on 29 June 2026' and that the stored helium is kept 'ready to be used again once the accelerator resumes operation in mid-2030'; CERN's 29 June 2026 article says 'The HiLumi LHC, scheduled to begin operation in 2030'. The end is a schedule value, not a reported event."
- /energy_regime/note: `No MoEDAL-specific energy value distinct from the LHC-wide figures was found in this session.` -> `No MoEDAL-specific energy value distinct from the LHC-wide figures was found.`
- notes, old text removed or rewritten: `Derived fields (detector_ids, site_ids, result_ids, document_ids) deliberately not written (v0.2 A1).`
- notes, old text removed or rewritten: `MAPP (MoEDAL Apparatus for Penetrating Particles) is recorded as an alias and an additional 'upgrade' interval on this same experiment record, not as a separate experiment id; no source fetched in this session treats it as a distinct collaboration/experiment.`
- notes, old text removed or rewritten: `Mandatory-bar-only pass: no results/technical documents written (MoEDAL is not a wave-3 flagship).`
- notes, new text: `MAPP (MoEDAL Apparatus for Penetrating Particles) is recorded as an alias and an additional 'upgrade' interval on this experiment record, not as a separate experiment id; no source consulted treats it as a distinct collaboration or experiment.`
- notes, new text: `No results or technical documents are recorded for MoEDAL yet.`

### data/atlas/experiments/snd-lhc.json
- **interval** `approved / construction / commissioning`  (wording cleanup)
    - old: status=approved; confidence=verified; start=2021-03-17; end={date=2022, approx} note: "Year precision only: bounded above by the 2023 PRL's statement that SND@LHC recorded pp collision data in 2022; no source fetched gives an exact installation/commissioning-complete date."
    - new: status=approved; confidence=verified; start=2021-03-17; end={date=2022, approx} note: "Year precision only: bounded above by the 2023 PRL's statement that SND@LHC recorded pp collision data in 2022; no source consulted gives an exact installation/commissioning-complete date."
    - note old: "No separate proposal, construction-start or commissioning date was found; only the approval date is sourced. VERIFIER FIX (2026-09-17): a prior draft of this record left `status` at 'approved' although its own note already said the true state should be 'active', citing SND@LHC's publicly known Run 3 data-taking; that self-contradiction is fixed here by actually sourcing the operating interval below (arXiv:2305.09383 / PRL 131, 031802), rather than by asserting 'active' unsourced."
    - note new: 'No separate proposal, construction-start or commissioning date was found; only the approval date is sourced. The operating interval below is sourced to arXiv:2305.09383 / PRL 131, 031802.'
    - end.note old: "Year precision only: bounded above by the 2023 PRL's statement that SND@LHC recorded pp collision data in 2022; no source fetched gives an exact installation/commissioning-complete date."
    - end.note new: "Year precision only: bounded above by the 2023 PRL's statement that SND@LHC recorded pp collision data in 2022; no source consulted gives an exact installation/commissioning-complete date."
- **interval** `data-taking (LHC Run 3)`  (wording cleanup)
    - old: status=active; confidence=verified; start={date=2022, approx}; end={date=2026-06, approx} note: "VERIFIER FIX (2026-09-17): capped at the LHC-wide Long Shutdown 3 boundary (see the added interval below). SND@LHC only detects particles from LHC collisions, so it cannot be 'active' while the LHC itself is off for LS3 (as already modelled for ALICE, LHCb, TOTEM, FASER and LHCf in this partition)."
    - new: status=active; confidence=verified; start={date=2022, approx}; end={date=2026-06, approx} note: 'Ends at the LHC-wide start of Long Shutdown 3 (June 2026); SND@LHC only detects particles from LHC collisions, so it cannot be active while the LHC is off.'
    - note old: "VERIFIER-ADDED (2026-09-17): the SND@LHC Collaboration's own first-neutrino-observation paper states it used 'a data set of proton-proton collisions at sqrt(s) = 13.6 TeV collected by SND@LHC in 2022'. This directly establishes SND@LHC as an operating, data-taking experiment from 2022, correcting the prior 'approved'-only record (a P1 timeline error per the wave-3 verification brief). Year precision only; no exact first-data day/month is sourced."
    - note new: "The SND@LHC Collaboration's own first-neutrino-observation paper states it used 'a data set of proton-proton collisions at sqrt(s) = 13.6 TeV collected by SND@LHC in 2022'. This establishes SND@LHC as an operating, data-taking experiment from 2022. Year precision only; no exact first-data day or month is sourced."
    - end.note old: "VERIFIER FIX (2026-09-17): capped at the LHC-wide Long Shutdown 3 boundary (see the added interval below). SND@LHC only detects particles from LHC collisions, so it cannot be 'active' while the LHC itself is off for LS3 (as already modelled for ALICE, LHCb, TOTEM, FASER and LHCf in this partition)."
    - end.note new: 'Ends at the LHC-wide start of Long Shutdown 3 (June 2026); SND@LHC only detects particles from LHC collisions, so it cannot be active while the LHC is off.'
- **interval** `Long Shutdown 3`  (F10/F25 LS3)
    - old: status=shutdown; confidence=verified; start=2026-06; end=null
    - new: status=shutdown; confidence=derived; start=2026-06-29; end={date=2030, display='mid-2030', approx, planned} note: 'CERN schedule: the LHC resumes operation in mid-2030; the rest of the CERN complex restarts in stages from mid-2028.'
    - quote old: 'null'
    - quote new: 'Following its final physics run, the accelerator has been switched off to begin CERN’s Long Shutdown 3 (LS3) ... The HiLumi LHC, scheduled to begin operation in 2030'
    - locator old: "reused from accelerator:lhc's sourced Long Shutdown 3 interval (src:cern-ls3-farewell-2026)"
    - locator new: 'home.cern/science/long-shutdown-3, item of 5 August 2026 "The LHC is being warmed up from near absolute zero to room temperature"'
    - sources old: '["src:cern-ls3-farewell-2026"]'
    - sources new: '["src:cern-long-shutdown-3-page", "src:cern-ls3-farewell-2026"]'
    - verified_at old: '2026-09-17'
    - verified_at new: '2026-10-25'
    - note old: 'VERIFIER-ADDED (2026-09-17): shares the LHC-wide Long Shutdown 3 interval already sourced for ALICE, LHCb, TOTEM, FASER and LHCf in this partition; ongoing at verified_at.'
    - note new: "SND@LHC detects neutrinos and other particles produced in LHC collisions, so it is idle while the LHC is shut down; this is an inference, since no SND@LHC-specific statement about this shutdown was found. Status is shutdown, not upgrade. The collaboration's home page (checked 2026-10-25) does not mention LS3 or an upgrade. No source consulted says that SND@LHC's own detector is being upgraded in LS3. Start and end are the LHC-wide Long Shutdown 3 dates. CERN's 5 August 2026 item says 'The cryogenics team has been running the warm-up sequence since LS3 began on 29 June 2026' and that the stored helium is kept 'ready to be used again once the accelerator resumes operation in mid-2030'; CERN's 29 June 2026 article says 'The HiLumi LHC, scheduled to begin operation in 2030'. The end is a schedule value, not a reported event."
- /energy_regime/note: `No SND@LHC-specific energy value distinct from the LHC-wide figures was found in this session.` -> `No SND@LHC-specific energy value distinct from the LHC-wide figures was found.`
- /links/website: `null` -> `<absent>`
- /links/website/confidence: `<absent>` -> `verified`
- /links/website/note: `<absent>` -> ``
- /links/website/quote: `<absent>` -> `SND@LHC: Scattering and Neutrino Detector at the LHC`
- /links/website/sources/0: `<absent>` -> `src:rc-snd-lhc-official-site`
- /links/website/value: `<absent>` -> `https://snd-lhc.web.cern.ch/`
- /links/website/verified_at: `<absent>` -> `2026-10-25`
- notes, old text removed or rewritten: `Derived fields (detector_ids, site_ids, result_ids, document_ids) deliberately not written (v0.2 A1).`
- notes, old text removed or rewritten: `The official SND@LHC site (attempted at home.cern/science/experiments/snd-lhc [404, re-checked 2026-09-17], sndlhc.web.cern.ch and sndlhc.cern [DNS failure, re-checked 2026-09-17]) could not be fetched; only the INSPIRE experiment record and the collaboration's own PRL were used. links.website is left null rather than guessed.`
- notes, old text removed or rewritten: `Mandatory-bar-only pass: no results/technical documents written (SND@LHC is not a wave-3 flagship); the 2023 muon-neutrino-observation PRL was added only as timeline evidence for the 'active' interval, not as a flagship result record.`
- notes, old text removed or rewritten: `VERIFIER FIX (2026-09-17): status corrected 'approved' -> 'active' and a sourced data-taking interval added, citing arXiv:2305.09383 (SND@LHC Collaboration, 'Observation of Collider Muon Neutrinos with the SND@LHC Experiment', PRL 131, 031802 (2023)), which states data were collected 'in 2022'. The prior record left status at 'approved' citing an absence of a sourced first-data date, even though its own interval note already said the true state was 'active' -- a P1 timeline error per the wave-3 verification brief (SND@LHC has taken Run 3 data since 2022).`
- notes, new text: `The official SND@LHC site is snd-lhc.web.cern.ch (checked 2026-10-25); home.cern/science/experiments/snd-lhc returns 404 and sndlhc.web.cern.ch does not resolve (checked 2026-10-25).`
- notes, new text: `The 2023 muon-neutrino-observation PRL is used only as timeline evidence for the 'active' interval; no results or technical documents are recorded for SND@LHC yet.`
- notes, new text: `SND@LHC has taken Run 3 data since 2022: the collaboration's 2023 PRL (arXiv:2305.09383, 'Observation of Collider Muon Neutrinos with the SND@LHC Experiment', PRL 131, 031802) states data were collected 'in 2022'. SND@LHC cannot record anything while the LHC is off for LS3, so its status is shutdown.`

### data/atlas/experiments/totem.json
- **interval** `operating`  (wording cleanup)
    - old: status=active; confidence=verified; start=2009-11-28; end={date=2013, approx} note: 'Run 1 ended in early 2013 with Long Shutdown 1; reused from the LHC-wide run schedule since no TOTEM-specific end date was found.'
    - new: status=active; confidence=verified; start=2009-11-28; end={date=2013, approx} note: 'Run 1 ended in early 2013 with Long Shutdown 1; the end is the LHC-wide Run 1 end, since no TOTEM-specific end date was found.'
    - end.note old: 'Run 1 ended in early 2013 with Long Shutdown 1; reused from the LHC-wide run schedule since no TOTEM-specific end date was found.'
    - end.note new: 'Run 1 ended in early 2013 with Long Shutdown 1; the end is the LHC-wide Run 1 end, since no TOTEM-specific end date was found.'
- **interval** `Long Shutdown 1`  (wording cleanup)
    - old: status=shutdown; confidence=uncertain; start={date=2013, approx}; end={date=2015, approx}
    - new: status=shutdown; confidence=uncertain; start={date=2013, approx}; end={date=2015, approx}
    - note old: 'Reused from the LHC-wide Long Shutdown 1 schedule (accelerator:lhc); no TOTEM-specific announcement was fetched this session.'
    - note new: 'The LHC-wide Long Shutdown 1 schedule (accelerator:lhc); no TOTEM-specific announcement was consulted.'
- **interval** `Run 2 / CMS-TOTEM combined operation`  (wording cleanup)
    - old: status=active; confidence=verified; start=2015; end=2018-12-03
    - new: status=active; confidence=verified; start=2015; end=2018-12-03
    - note old: 'Run dates reused from the LHC-wide schedule (accelerator:lhc); the CMS-TOTEM combined-measurement partnership itself is TOTEM-specific and sourced to home.cern, whose page (August 2014) states it as a plan for 2015 ("will coordinate").'
    - note new: 'Run dates are the LHC-wide schedule (accelerator:lhc); the CMS-TOTEM combined-measurement partnership itself is TOTEM-specific and sourced to home.cern, whose page (August 2014) states it as a plan for 2015 ("will coordinate").'
- **interval** `Long Shutdown 2`  (wording cleanup)
    - old: status=shutdown; confidence=verified; start=2018-12-03; end=2022-07-05
    - new: status=shutdown; confidence=verified; start=2018-12-03; end=2022-07-05
    - locator old: "reused from accelerator:lhc's sourced Long Shutdown 2 interval (src:cern-lhc-prepares-new-achievements-2018, src:cern-run3-start-2022)"
    - locator new: 'the same Long Shutdown 2 dates as accelerator:lhc (src:cern-lhc-prepares-new-achievements-2018, src:cern-run3-start-2022)'
    - note old: 'Reused from the LHC-wide LS2 schedule; no TOTEM-specific announcement was fetched this session.'
    - note new: 'The LHC-wide LS2 schedule; no TOTEM-specific announcement was consulted.'
- **interval** `Run 3`  (wording cleanup)
    - old: status=active; confidence=approximate; start=2022-07-05; end=2026-06
    - new: status=active; confidence=approximate; start=2022-07-05; end=2026-06
    - locator old: "reused from accelerator:lhc's sourced Run 3 interval (src:cern-run3-start-2022, src:cern-ls3-farewell-2026)"
    - locator new: 'the same Run 3 dates as accelerator:lhc (src:cern-run3-start-2022, src:cern-ls3-farewell-2026)'
    - note old: 'Reused from the LHC-wide Run 3 schedule; no TOTEM-specific run status was fetched this session confirming continued Roman-Pot operation through all of Run 3.'
    - note new: 'The LHC-wide Run 3 schedule; no TOTEM-specific run status was consulted confirming continued Roman-Pot operation through all of Run 3.'
- **interval** `Long Shutdown 3`  (F10/F25 LS3)
    - old: status=shutdown; confidence=verified; start=2026-06; end=null
    - new: status=shutdown; confidence=derived; start=2026-06-29; end={date=2030, display='mid-2030', approx, planned} note: 'CERN schedule: the LHC resumes operation in mid-2030; the rest of the CERN complex restarts in stages from mid-2028.'
    - quote old: 'null'
    - quote new: 'Following its final physics run, the accelerator has been switched off to begin CERN’s Long Shutdown 3 (LS3) ... The HiLumi LHC, scheduled to begin operation in 2030'
    - locator old: "reused from accelerator:lhc's sourced Long Shutdown 3 interval (src:cern-ls3-farewell-2026)"
    - locator new: 'home.cern/science/long-shutdown-3, item of 5 August 2026 "The LHC is being warmed up from near absolute zero to room temperature"'
    - sources old: '["src:cern-ls3-farewell-2026"]'
    - sources new: '["src:cern-long-shutdown-3-page", "src:cern-ls3-farewell-2026"]'
    - verified_at old: '2026-09-17'
    - verified_at new: '2026-10-25'
    - note old: 'Reused from the LHC-wide LS3 schedule; ongoing at verified_at.'
    - note new: "TOTEM measures protons and particles from LHC collisions, so it is idle while the LHC is shut down; this is an inference, since no TOTEM-specific statement about this shutdown was found. Status is shutdown, not upgrade. No source consulted says that TOTEM's own detector is being modified in LS3. Start and end are the LHC-wide Long Shutdown 3 dates. CERN's 5 August 2026 item says 'The cryogenics team has been running the warm-up sequence since LS3 began on 29 June 2026' and that the stored helium is kept 'ready to be used again once the accelerator resumes operation in mid-2030'; CERN's 29 June 2026 article says 'The HiLumi LHC, scheduled to begin operation in 2030'. The end is a schedule value, not a reported event."
- /energy_regime/note: `No TOTEM-specific energy value distinct from the LHC-wide figures was found in this session.` -> `No TOTEM-specific energy value distinct from the LHC-wide figures was found.`
- /key_specs/0/quantity/note: `Corrected 2026-09-18 (release-candidate red team): the prior quote spliced two separate sentences from the page ("26 'Roman pot' detectors" and "'Roman Pots' with silicon sensors perform measurements of scattered protons.") into one that does not appear verbatim on the cited page, violating A15. Replaced with the sentence that actually supports the count.` -> `The quote is the phrase on the cited page that gives the count; an earlier version of the quote joined two separate sentences from the page, which did not appear verbatim.`
- notes, old text removed or rewritten: `Derived fields (detector_ids, site_ids, result_ids, document_ids) deliberately not written (v0.2 A1).`
- notes, old text removed or rewritten: `The official TOTEM site (totem.web.cern.ch) redirected to a CERN SSO login wall in this session and was not fetched; home.cern and the INSPIRE experiment record were used instead.`
- notes, old text removed or rewritten: `Run/shutdown intervals from Run 1 onward are the LHC-wide machine schedule (already sourced for accelerator:lhc and other LHC experiments in this wave) applied to TOTEM, since no TOTEM-specific run-by-run announcement was found; the 2015 CMS-TOTEM combined-measurement partnership is the one TOTEM-specific fact confirmed independently.`
- notes, old text removed or rewritten: `Mandatory-bar-only pass: no results/technical documents written (TOTEM is not a wave-3 flagship).`
- notes, new text: `As of 2026-10-25 the official TOTEM site (totem.web.cern.ch) redirects to a CERN single-sign-on login page and could not be read; home.cern and the INSPIRE experiment record were used instead.`
- notes, new text: `Run/shutdown intervals from Run 1 onward are the LHC-wide machine schedule (accelerator:lhc and the other LHC experiments' records) applied to TOTEM, since no TOTEM-specific run-by-run announcement was found; the 2015 CMS-TOTEM combined-measurement partnership is the one TOTEM-specific fact confirmed independently.`
- notes, new text: `No results or technical documents are recorded for TOTEM yet.`

### data/atlas/experiments/xenonnt.json
- **interval** `start of operation / commissioning`  (F25 part 2)
    - old: status=commissioning; confidence=approximate; start=2020; end=2021-07-06
    - new: status=commissioning; confidence=approximate; start=2020; end=2021-07-06
    - note old: 'Official site says operation started in 2020; INSPIRE experiment record gives date_started 2021-07-06, which is treated here as the end of commissioning / start of the sourced science-run interval below.'
    - note new: "The official site says operation started in 2020; INSPIRE's experiment record gives date_started 2021-07-06, used here as the end of commissioning and the start of the science-operations interval below."
- **interval** `science operations`  (F25 part 2)
    - old: status=active; confidence=verified; start=2021-07-06; end={date=2025, display='before the summer-2025 upgrade', approx}
    - new: status=active; confidence=approximate; start=2021-07-06; end={date=2025, display='before the summer-2025 upgrade', approx}
    - locator old: 'end: ATHEXIS 2026 and LIDINE 2026 talk abstracts'
    - locator new: 'start: INSPIRE experiment record, field date_started; end: ATHEXIS 2026 and LIDINE 2026 talk abstracts'
    - note old: 'Start date per the INSPIRE experiment record date_started field. Exact SR0/SR1 run boundaries were not confirmed by a source fetched in this session. END ADDED 2026-10-25 at year precision: the collaboration describes a detector upgrade "carried out in summer 2025" (LIDINE 2026 abstract) after which "the experiment began its new commissioning phase in 2026" (ATHEXIS 2026 abstract). The date of the last science-run data is not given by any fetched source. Previously open-ended.'
    - note new: "Start = the date_started field of INSPIRE's experiment record (6 July 2021). The Nikhef slides of May 2026 list science runs SR0, SR1 and SR2 before the upgrade. The date of the last science-run data is not given by any source consulted, and the end is year precision: it is set to the 2025 detector upgrade, which the collaboration says was 'carried out in summer 2025' (LIDINE 2026 abstract), after which 'the experiment began its new commissioning phase in 2026' (ATHEXIS 2026 abstract). The last science data may predate the upgrade."
- **interval** `detector upgrade (new TPC electrodes, drift field 23 → 100 V/cm)`  (F25 part 2)
    - old: status=upgrade; confidence=approximate; start={date=2025, display='summer 2025', approx}; end={date=2026, approx}
    - new: status=upgrade; confidence=approximate; start={date=2025-07, display='summer 2025', earliest='2025-06', latest='2025-08', approx} note: "Summer is stored as July with June-August bounds: the LIDINE 2026 abstract says the upgrade was 'carried out in summer 2025'."; end={date=2026-03, display='first half of 2026', earliest='2026-01', latest='2026-06', approx} note: "Bounded by the ATHEXIS 2026 abstract ('began its new commissioning phase in 2026'; talk at a conference held 8-12 June 2026) and the Nikhef slides of May 2026 ('Everything back in place, 8.5 tons of LXe'); the month is not given by any source consulted. March is the midpoint of the January-June bounds, not a reported date."
    - note old: 'Month of start and end not given by any fetched source (the slide timeline labels a "12 month upgrade" starting in 2025).'
    - note new: "The upgrade replaced the TPC electrodes to raise the drift field from 23 V/cm to 100 V/cm. LIDINE 2026 abstract: 'an overview of the XENONnT detector upgrade carried out in summer 2025'. The Nikhef slides of May 2026 call it a '1-year long operation' ('12 month upgrade' on their timeline), in which the electrode replacement itself took a few weeks, and say 'Upgrade completed'. The ATHEXIS abstract says 'Following upgrade operations conducted in 2025' the commissioning phase began in 2026. No source consulted gives the month the upgrade began or ended; the end is the start of the recommissioning interval below, bounded to the first half of 2026."
- **interval** `commissioning after the 2025 upgrade` -> `Recommissioning after the 2025 upgrade (2026)`  (F25 part 2)
    - old: status=commissioning; confidence=approximate; start={date=2026, approx}; end=null
    - new: status=commissioning; confidence=approximate; start={date=2026-03, display='first half of 2026', earliest='2026-01', latest='2026-06', approx} note: "Bounded by the ATHEXIS 2026 abstract ('began its new commissioning phase in 2026'; talk at a conference held 8-12 June 2026) and the Nikhef slides of May 2026 ('Everything back in place, 8.5 tons of LXe'); the month is not given by any source consulted. March is the midpoint of the January-June bounds, not a reported date."; end=null
    - note old: 'Nikhef slides (May 2026): "Commissioning until July, then start of data taking". The LIDINE 2026 abstract (talk of 7 October 2026) still reports "the status and first results of the subsequent commissioning campaign"; no fetched source says that post-upgrade science data taking has started, so the state is commissioning, not active.'
    - note new: "Last documented state. The ATHEXIS 2026 abstract (conference 8-12 June 2026) says the experiment 'began its new commissioning phase in 2026'. The Nikhef slides of May 2026 say 'Commissioning until July, then start of data taking'. The LIDINE 2026 abstract (talk of 7 October 2026) still reports 'the status and first results of the subsequent commissioning campaign'. No source consulted says that post-upgrade science data taking has started or that commissioning has ended, so the state is shown as commissioning, not active; whether it is still commissioning at 2026-10-25 is not confirmed. Before the upgrade the experiment ran science operations from July 2021 (see the interval above)."
- /summary/plain: `XENONnT is a tank of nearly six tonnes of liquid xenon deep under a mountain in Italy, watching for dark matter particles and other rare signals. It is the upgraded successor of XENON1T, has been running since 2020, and has set new dark matter limits and reported the first hint of solar neutrinos bouncing off xenon nuclei.` -> `XENONnT is a tank of nearly six tonnes of liquid xenon deep under a mountain in Italy, watching for dark matter and other rare signals. The upgraded successor of XENON1T, it began operating in 2020, took science data from 2021, was upgraded in 2025 and, per the collaboration's 2026 talks, is being recommissioned. It has set new dark matter limits.`
- /summary/technical: `Dual-phase xenon TPC upgrade of XENON1T: 8.5 t total / 5.9 t active liquid xenon in LNGS Hall B (INFN, ~1400 m rock). Construction began Dec 2018; operation began 2020. The first WIMP-search result (2023, 1.1 t-y exposure) set a spin-independent limit of 2.58 × 10⁻⁴⁷ cm² at 28 GeV/c². A 2024 analysis reported the first indication (2.73σ) of solar 8B neutrinos via coherent elastic neutrino-nucleus scattering.` -> `Dual-phase xenon TPC upgrade of XENON1T: 8.5 t total / 5.9 t active liquid xenon in LNGS Hall B (INFN, ~1400 m rock). Construction began Dec 2018; operation began 2020, science operations from July 2021, detector upgrade (new TPC electrodes, drift field raised from 23 to 100 V/cm) from summer 2025 to the first half of 2026, recommissioning in 2026. The first WIMP-search result (2023, 1.1 t-y exposure) set a spin-independent limit of 2.58 × 10⁻⁴⁷ cm² at 28 GeV/c². A 2024 analysis reported the first indication (2.73σ) of solar 8B neutrinos via coherent elastic neutrino-nucleus scattering.`

## Not changed / for the lead
- accelerator:lhc (read only): its Long Shutdown 3 interval already matches the CERN source (start 2026-06-29, end mid-2030, planned); no edit.
- src:atlas-high-luminosity-feature has `date: "2022"` but the page byline reads 18 January 2023 (source files are outside my brief; not edited).
- experiment:moedal (pre-existing, outside the findings): its `approved` (from 2009-12-02) and `upgrade` ("MAPP upgrade approved", from 2021) intervals are open-ended, so the experiment derives `upgrade` for 2022-2026 while detector:moedal derives `active` for the same months, and the experiment has no `active` interval. Fixing it needs a sourced end for the MAPP upgrade (CERN says the upgrade was done "in preparation for data taking during run 3") and sourced operating intervals; not attempted.
- experiment:mathusla (not mine) says it aims to go online with the HL-LHC "in ~2029"; that is the same superseded date.
- The recommissioning interval of XENONnT now derives `commissioning` with certainty `certain` from July 2026 on (its start is bounded to January-June 2026), where it used to derive `commissioning` / `possible` (year-precision start). The end is still unknown (the May 2026 slides planned commissioning "until July"); the note says so. If the lead prefers the hatched "possible" rendering for the open end, restore a year-precision start.
- Pre-existing quotes sourced to inspirehep.net remain unchecked by the script (class `skipped`).


---

## Appendix D. JUNO map title, OPERA significance (F21, F27)

# juno-opera change log (agent juno-opera, 2026-10-25)


## data/atlas/maps/juno-reactor-baselines.json

F21: map titled '... at the 52-53 km baseline' draws the hall point and the eight reactor buildings, not baselines. Retitled to what is drawn; baselines stated in summary and a note. Sources: arXiv:2511.14593 (html/abs, fetched 2026-10-25), arXiv:2104.02565 (ar5iv HTML full text fetched 2026-10-25: Sec. 1.2 and Table 1). Verbatim quotes: 'The detector is positioned near the first maximum of the solar-driven oscillations, at an optimized distance of 52.5 km, equidistant from all reactor cores of the Yangjiang and Taishan Nuclear Power Plants (NPP)' (arXiv:2511.14593, introduction); 'the experimental site is at equal distances of ∼53 km from the Yangjiang NPP and the Taishan NPP' and 'The distances from the detector site to the Yangjiang and Taishan cores are surveyed with a Global Positioning System (GPS) to a precision of 1 meter.' (arXiv:2104.02565 Sec. 1.2); Table 1 baselines YJ-1..6 52.74 52.82 52.41 52.49 52.11 52.19, TS-1 52.77, TS-2 52.64 km.

* `/name`
  * old: "JUNO — Yangjiang and Taishan reactor complexes at the 52-53 km baseline"
  * new: "JUNO — experimental hall and the Yangjiang and Taishan reactor buildings"

* `/notes`
  * old: ["Core numbering YJ-1..6 / TS-1..2 is assigned by matching the order of the measured distances to the order of the published baselines; the OSM ways carry no unit numbers. The Taishan EPR units 3 and 4 (baselines 52.32 and 52.20 km in the CDR) were not built; arXiv:2104.02565 says only that two more cores 'possibly' may be built.", "Far reactors: arXiv:2104.02565 Sec. 1.2 puts the Daya Bay complex 215 km (and Huizhou 265 km) from the detector, beyond a local map; Daya Bay has its own map (linked).", "Residual: the six Yangjiang buildings are all 96-101 m farther from the published hall coordinate than the surveyed baselines say, the Taishan buildings agree to <= 16 m. The sign pattern is that of a ~100 m displacement of the published coordinate toward SSW, or of an OSM registration offset between the two plants; the sources cannot separate them."]
  * new: ["Baseline statements by the collaboration: \"The detector is positioned near the first maximum of the solar-driven oscillations, at an optimized distance of 52.5 km, equidistant from all reactor cores of the Yangjiang and Taishan Nuclear Power Plants (NPP)\" (arXiv:2511.14593, introduction); \"the experimental site is at equal distances of ∼53 km from the Yangjiang NPP and the Taishan NPP\" (arXiv:2104.02565, Sec. 1.2). The surveyed per-core baselines in Table 1 of arXiv:2104.02565 span 52.11 to 52.82 km, so the equal-distance figure is nominal. Checked 2026-10-25.", "Core numbering YJ-1..6 / TS-1..2 is assigned by matching the order of the measured distances to the order of the published baselines; the OSM ways carry no unit numbers. The Taishan EPR units 3 and 4 (baselines 52.32 and 52.20 km in the CDR) were not built; arXiv:2104.02565 says only that two more cores 'possibly' may be built.", "Far reactors: arXiv:2104.02565 Sec. 1.2 puts the Daya Bay complex 215 km (and Huizhou 265 km) from the detector, beyond a local map; Daya Bay has its own map (linked).", "Residual: the six Yangjiang buildings are all 96-101 m farther from the published hall coordinate than the surveyed baselines say, the Taishan buildings agree to <= 16 m. The sign pattern is that of a ~100 m displacement of the published coordinate toward SSW, or of an OSM registration offset between the two plants; the sources cannot separate them."]

* `/sources`
  * old: ["src:juno-physics-detector-arxiv-2021", "src:geo-juno-physics-2015", "src:geo-juno-osm-yangjiang-reactors", "src:geo-juno-osm-taishan-reactors"]
  * new: ["src:juno-physics-detector-arxiv-2021", "src:geo-juno-physics-2015", "src:geo-juno-osm-yangjiang-reactors", "src:geo-juno-osm-taishan-reactors", "src:rf11-juno-arxiv-first-oscillation-2025"]

* `/summary/plain`
  * old: "The detector and the two nuclear power plants whose antineutrinos it measures, to scale: Yangjiang (six reactors) and Taishan (two reactors in operation), each about 52-53 km from the JUNO hall."
  * new: "The JUNO underground hall and the buildings of the two nuclear power plants whose antineutrinos it measures, to scale: six reactor buildings at Yangjiang and two at Taishan. The collaboration puts the detector 52.5 km from the reactor cores, and its surveyed distances to the individual cores run from 52.11 to 52.82 km. The map shows where the buildings stand; those baselines are checked against the drawn positions, but no baseline lines are drawn."

* `/summary/technical`
  * old: "Baseline map: published hall coordinate (arXiv:2104.02565), OSM reactor buildings of Yangjiang (six building=reactor ways) and Taishan (two nuclear-island buildings), with each building's centroid-to-hall distance checked against the GPS-surveyed baselines of Table 1 at 0.3 % tolerance. Companion to map:juno-jiangmen."
  * new: "Published hall coordinate (arXiv:2104.02565, Sec. 1.2) and OSM reactor buildings of Yangjiang (six building=reactor ways) and Taishan (two nuclear-island buildings). Each building's centroid-to-hall distance is checked at 0.3 % tolerance against the GPS-surveyed core baselines of arXiv:2104.02565 Table 1 (YJ-1 to YJ-6: 52.74, 52.82, 52.41, 52.49, 52.11, 52.19 km; TS-1, TS-2: 52.77, 52.64 km; surveyed to 1 m). The JUNO Collaboration gives the nominal baseline as 52.5 km (arXiv:2511.14593, introduction) and as about 53 km (arXiv:2104.02565, Sec. 1.2). No baseline lines or distance labels are drawn. Companion to map:juno-jiangmen."


## data/atlas/geometry/juno-baseline-hall-point.json

F21: name no longer says 'baseline map' (the map draws no baselines; the name stays distinct from geometry:juno-experimental-hall); note pointed at checks that live on the reactor-building records.

* `/name`
  * old: "JUNO underground experimental hall (published coordinate, baseline map)"
  * new: "JUNO underground experimental hall (published coordinate, reactor-buildings map)"

* `/notes/0`
  * old: "Cross-check: the distance from this point to the centroid of each of the six Yangjiang reactor buildings and the two Taishan buildings is within 0.2 % (<= 101 m) of the GPS-surveyed baselines of arXiv:2104.02565 Table 1 (see geometry:juno-baseline-hall-point checks); the Taishan distances agree to <= 16 m, the six Yangjiang ones are all 96-101 m longer (a spread of 5 m), i.e. the baselines would put the detector ~100 m closer to Yangjiang (about SSW) than the published coordinate does. The offset is within accuracy_m but is reported rather than hidden."
  * new: "Cross-check: the distance from this point to the centroid of each of the six Yangjiang reactor buildings and the two Taishan buildings is within 0.2 % (<= 101 m) of the GPS-surveyed baselines of arXiv:2104.02565 Table 1 (see the distance checks on the reactor-building records of this map); the Taishan distances agree to <= 16 m, the six Yangjiang ones are all 96-101 m longer (a spread of 5 m), i.e. the baselines would put the detector ~100 m closer to Yangjiang (about SSW) than the published coordinate does. The offset is within accuracy_m but is reported rather than hidden."


## data/atlas/results/opera-tau-neutrino-appearance-discovery-2015.json

F27: 5.1 sigma is in the body, not the abstract (abstract: 'a significance larger than 5 σ'). Source: https://arxiv.org/pdf/1507.01417 (fetched 2026-10-25; PDF text extracted locally). Verbatim, Conclusions p. 6: 'Given the low background level and the observed number of ντ candidate events, we report the discovery of a ντ appearance in the CNGS neutrino beam with a significance of 5.1 σ.' Results p. 6: 'a (one-side) significance of 5.1 standard deviations is obtained, corresponding to a background fluctuation probability of 1.1 × 10−7' and 'giving a significance of 5.1 standard deviations.' Abstract: 'with a significance larger than 5 σ.' Table III (p. 6): total expected background 0.25 ± 0.05, expected signal 2.64 ± 0.53, observed 5.

* `/date/note`
  * old: "Published as Phys. Rev. Lett. 115, 121802 (2015); submitted to arXiv 2015-07-06. `date` is the arXiv v1 submission date, earlier than the journal publication (A9: the display date is the earliest sourced public date)."
  * new: "Published as Phys. Rev. Lett. 115, 121802 (2015); submitted to arXiv 2015-07-06. `date` is the arXiv v1 submission date, earlier than the journal publication; the display date is the earliest sourced public date."

* `/key_value_text/locator`
  * old: "abstract / results section"
  * new: "abstract (first sentence quoted); Conclusions, p. 6 of the arXiv PDF (second sentence quoted)"

* `/key_value_text/note`
  * old: ""
  * new: "The abstract of the same paper gives the significance only as larger than 5 σ; 5.1 σ is the figure stated in the Results and Conclusions."

* `/notes/0`
  * old: "The record's title and claim.quote are the verbatim title of Phys. Rev. Lett. 115, 121802 (2015), which contains 'Discovery', satisfying A16's mechanical check for result_type 'discovery'."
  * new: "The record's title and claim.quote are the verbatim title of Phys. Rev. Lett. 115, 121802 (2015), which contains the word 'Discovery'."

* `/significance/locator`
  * old: "results section / conclusions"
  * new: "arXiv:1507.01417 (PDF), Conclusions, p. 6; the same figure is given in the Results section, pp. 5-6. The abstract says only 'larger than 5 σ'."

* `/significance/note`
  * old: ""
  * new: "The abstract states only a significance larger than 5 σ. The figure 5.1 σ is given in the body of the paper: in the Results section both test statistics (a combination of the per-channel p-values, one-sided, and a profile likelihood ratio) give 5.1 standard deviations, and the Conclusions state it as the significance of the discovery."

* `/significance/quote`
  * old: "a significance of 5.1 sigma"
  * new: "Given the low background level and the observed number of ντ candidate events, we report the discovery of a ντ appearance in the CNGS neutrino beam with a significance of 5.1 σ."

* `/significance/sources/0`
  * old: "src:opera-prl-2015-discovery"
  * new: "src:rf08-opera-discovery-2015-arxiv-pdf"

* `/significance/verified_at`
  * old: "2026-09-17"
  * new: "2026-10-25"

* `/summary/plain`
  * old: "OPERA reports the discovery of tau-neutrino appearance in the muon-neutrino beam sent from CERN to the Gran Sasso laboratory: five tau-neutrino candidate events against an expected background of about 0.25 events, at a significance of 5.1σ."
  * new: "OPERA reports the discovery of tau-neutrino appearance in the muon-neutrino beam sent from CERN to the Gran Sasso laboratory: five tau-neutrino candidate events against an expected background of about 0.25 events, at a significance the paper puts at 5.1σ (its abstract says only that it is larger than 5σ)."

* `/summary/technical`
  * old: "OPERA νμ→ντ appearance analysis of the CNGS data taken from 2008 to 2012: a fifth ντ candidate event found in an enlarged data sample; five candidates observed against a total background expectation of 0.25 ± 0.05 events (expected signal 2.64 ± 0.53 events for Δm²23 = 2.44×10⁻³ eV² and sin²2θ23 = 1), corresponding to the discovery of νμ→ντ oscillations in appearance mode with a significance of 5.1σ."
  * new: "OPERA νμ→ντ appearance analysis of the CNGS data taken from 2008 to 2012: a fifth ντ candidate event found in an enlarged data sample; five candidates observed against a total background expectation of 0.25 ± 0.05 events (expected signal 2.64 ± 0.53 events for Δm²23 = 2.44×10⁻³ eV² and sin²2θ23 = 1), corresponding to the discovery of νμ→ντ oscillations in appearance mode with a significance of 5.1σ (stated in the Results and Conclusions; the abstract says larger than 5σ)."


## data/atlas/experiments/opera.json

F27 (summary.technical qualifies the 5.1σ figure) and process-language cleanup of notes (the site:lngs-hall-c record now exists, so the 'dangling reference' notes are replaced by plain statements).

* `/intervals/0/note`
  * old: "Sole fetched source for this date range is Wikipedia (rank 12); no official OPERA/LNGS/CERN page giving construction dates was reachable in this session (operaweb.lngs.infn.it did not resolve; lngs.infn.it/en/opera returned HTTP 500). Flagged for review."
  * new: "The only source consulted for this date range is Wikipedia (rank 12). When checked on 2026-09-17 no official OPERA, LNGS or CERN page giving construction dates was reachable (operaweb.lngs.infn.it did not resolve; lngs.infn.it/en/opera returned HTTP 500), so the range is marked uncertain."

* `/intervals/1/note`
  * old: "Day-precision end date corroborated by src:opera-wikipedia ('The beam from CERN was stopped on 3 December 2012, ending data taking.') and by the CERN CNGS page's 'July 2006 to December 2012' beam-operation range; year precision start/end used here is from the primary PRL paper's own stated run range."
  * new: "Day-precision end date corroborated by Wikipedia ('The beam from CERN was stopped on 3 December 2012, ending data taking.') and by the CERN CNGS page's 'July 2006 to December 2012' beam-operation range; the year-precision start and end used here are the primary PRL paper's own stated run range."

* `/notes/0`
  * old: "Derived fields (detector_ids, site_ids, result_ids, document_ids) are deliberately not written (v0.2 A1)."
  * new: "Detector, site, result and document links are derived from the records that reference this experiment and are not stored here."

* `/notes/1`
  * old: "facility_roles/beamline detector-host site is site:lngs-hall-c, owned by the 'facilities' lead and not yet created in data/atlas/ when this record was written; expected dangling reference (see detector:opera and beamline:cngs)."
  * new: "The detector is hosted at site:lngs-hall-c (LNGS Hall C); the placement is recorded on detector:opera and the beam on beamline:cngs."

* `/notes/2`
  * old: "external.inspire_experiment left null: no INSPIRE experiment-registry lookup was performed in this session; OPERA is tier D so this is not mandatory (brief §'What you are producing')."
  * new: "The INSPIRE experiment-registry identifier is not recorded for OPERA; none has been looked up."

* `/notes/3`
  * old: "No official OPERA experiment website was reachable in this session (operaweb.lngs.infn.it did not resolve; lngs.infn.it/en/opera returned HTTP 500); links.website left null rather than guessed."
  * new: "The original OPERA website (operaweb.lngs.infn.it) did not resolve when checked on 2026-09-17 and lngs.infn.it/en/opera returned HTTP 500, so no website link is recorded; the experiment's own news page is cited from an Internet Archive capture of 2021-01-25."

* `/notes/4`
  * old: "OPERA is not on the brief's flagship list, so only the mandatory-bar record plus the one historically-important result (the 2015 discovery paper) were produced; no technical-document/TDR record was written in this pass."
  * new: "The atlas holds one result record for OPERA, the 2015 discovery paper; no technical-design or other document record has been written for it."

* `/summary/technical`
  * old: "Emulsion-cloud-chamber (lead/nuclear-emulsion 'brick') experiment in LNGS Hall C, receiving the CNGS muon-neutrino beam from the CERN SPS over a 732 km baseline. Took data 2008-2012 and reported discovery of νμ → ντ appearance at 5.1σ significance from five candidate tau-neutrino interactions, confirming long-baseline neutrino oscillation in appearance mode."
  * new: "Emulsion-cloud-chamber (lead/nuclear-emulsion 'brick') experiment in LNGS Hall C, receiving the CNGS muon-neutrino beam from the CERN SPS over a 732 km baseline. Took data 2008-2012 and reported discovery of νμ → ντ appearance at 5.1σ significance (the paper's abstract says larger than 5σ) from five candidate tau-neutrino interactions, confirming long-baseline neutrino oscillation in appearance mode."


## data/atlas/detectors/opera.json

Process-language cleanup (site:lngs-hall-c exists).

* `/notes/0`
  * old: "Placed at site:lngs-hall-c, owned by the 'facilities' lead and not yet created in data/atlas/ when this record was written; expected dangling reference until that lead lands."
  * new: "Placed at site:lngs-hall-c (LNGS Hall C)."

* `/placements/0/note`
  * old: "site:lngs-hall-c is owned by the 'facilities' lead; expected dangling reference until that record is created."
  * new: ""


## Not edited (outside the file list), to be fixed by the lead
* data/atlas/maps/juno-jiangmen.json `summary.technical`: '... the Yangjiang and Taishan reactor buildings and the 52-53 km baselines are on map:juno-reactor-baselines.' Suggested: '... the Yangjiang and Taishan reactor buildings, 52-53 km from the hall, are on map:juno-reactor-baselines.'
* data/atlas/sources/opera-prl-2015-discovery.json `excerpt` ('the discovery of numu -> nutau oscillations in appearance mode with a significance larger than 5 sigma ... a significance of 5.1 sigma') is not verbatim. Suggested: 'with a significance larger than 5 σ (abstract) ... we report the discovery of a ντ appearance in the CNGS neutrino beam with a significance of 5.1 σ (Conclusions)'.
* data/atlas/collaborations/opera.json `summary.technical` and data/atlas/coverage/accelerator-neutrino-historical.json (line 74 notes) state 5.1σ / '5.1 sigma' without noting the abstract's 'larger than 5 σ'; the figure itself is supported by the paper body.
* Generated outputs and docs carrying the old map title: static/atlas/generated/{search,atlas,coverage,text}.json, static/atlas/generated/geometry/juno-reactor-baselines.json, docs/HEP_ATLAS_COVERAGE.md line 348 (table row), docs/atlas-worklog/RELEASE_GEOMETRY_underground.md line 11 (prose, history).


---

## Appendix E. Dated wording replacing session language (F11)

# LOG -- agent dated-wording (F11: dated wording instead of process language)

Worktree /Users/yatharthsirohi/Desktop/HEP-Graph-ar-rc-data, nothing committed. All re-checks on 2026-10-25.
Only strings were changed (notes, notes[], summary.*, locators); no value, quote (except the one below), source list (except the one below), date or status was changed.
Method for "checked 2026-10-25": WebFetch of the live page; for PDFs the text of the PDF as fetched that day (WebFetch saves the PDF; the quote-check cache holds the same-day text). Pages that WebFetch cannot open (web.archive.org, deap3600.ca 403, snolab.ca 404) were read from the same-day quote-check cache of Internet Archive captures.

## Corrections made because the cited source contradicts the old text (details in the sections below)
1. detectors/deap-3600.json `/specs/shielding` -- old value said "no additional water or scintillator veto shield is described for DEAP-3600"; the cited detector paper (arXiv:1712.01982, Sec. 1.1 and Table 1) describes a 7.8 m water shield tank with 48 PMTs as a muon veto. Value, quote (segments, verified), locator, sources (detector paper added) and verified_at corrected.
2. detectors/edelweiss.json `/notes/0` -- old note said no source states an operating temperature; arXiv:2211.04176 and arXiv:2203.03993 give the NbSi TES working temperature (about 44 mK). Note rewritten with the quote.
3. experiments/sensei.json `/notes/1`, `/facility_roles/0/note`, `/summary/technical` -- old text said the SNOLAB SENSEI detector was "not confirmed as realized"; arXiv:2312.13342 reports six Skipper-CCDs (2.19 g active mass each) installed at SNOLAB in 2021 with a first science run 2022-09-09 to 2023-04-10 (the record's own SNOLAB intervals already carry this). The ~100 g detector planned in 2020 is still not reported.
4. experiments/deap-3600.json `/summary/plain`, `/summary/technical` -- undated "currently being upgraded" contradicted the record's own 2026 intervals (third fill described as "newly initiated" in the 21 September 2026 abstract, re-read today). Reworded with that date.
5. detectors/deap-3600.json `/notes/1` -- the energy-threshold note now mentions the 15 keVee nominal analysis threshold of Table 1 (not a nuclear-recoil value, so the old "not recorded" stays true).
6. collaborations/nexo.json `/notes/0` -- said "This record has no `intervals`" although it has one (2018 lower bound); reworded.
7. experiments/comet.json `/notes/1` -- the old note described a superseded coarse geocoder coordinate for site:j-parc-hadron-hall; the site now carries an OpenStreetMap building-footprint centroid (kind campus). Reworded to match the site record.

## Status claims re-checked (nothing changed)
* COMET: status construction; comet.kek.jp (checked 2026-10-25): latest dated entry CM48, 27-31 July 2026; no result, data-taking or commissioning statement.
* CTAO: status construction; press release 15 Oct 2026 ("a crucial step toward the full scientific operation"; LSTs "will undergo commissioning").
* CUPID: status proposed kept. arXiv:2503.02894 (v2, 11 Jul 2025), Conclusions: "CUPID construction activities have already started, including preparations for the cryostat upgrade and the setup of the detector assembly infrastructure" -- possibly stale `proposed`; reported to the lead, not changed.
* EDELWEISS: official site still does not resolve (edelweiss.in2p3.fr, www.edelweiss.in2p3.fr, http and https).
* H.E.S.S.: status active; live hess-experiment.eu shows "Due to precautionary security measures, we are taking down this web site/service temporarily." on 2026-10-25; sources are Internet Archive captures.
* nEXO: status proposed; nexo.llnl.gov "The nEXO experiment is under development." (undated; news items dated Dec. 21, 2021); the SNOLAB report of 26 May 2026 says "US led nEXO project was paused." (Dec 2024) -- status not changed.
* SENSEI: Fermilab operation still reported (arXiv:2605.30281, 28 May 2026; arXiv:2610.22418, 15 Oct 2026).
* DEAP-3600: see item 4; snolab.ca/experiment/deap-3600/ now returns 404, deap3600.ca returns 403 (captures read).
* DarkSide-20k: lngs.infn.it/en/darkside (undated, copyright 2026): "currently under construction in the LNGS Hall-C", "expected to begin operation in 2027".
* DMRadio: arXiv:2210.07215 "is being built"; arXiv:2607.05771 (7 July 2026) measured performance of the DMRadio-50L cryogenic system, future data taking.
* DarkQuest: arXiv:2203.08322 (16 Mar 2022, Snowmass contribution); no approval found (also a web search for later announcements).

## Existing source records re-read on 2026-10-25 (the lead may bump `accessed`; I did not edit sources/)
src:muons-comet-official-site (https://comet.kek.jp/), src:muons-arxiv-1812-09018, src:cosmic-gamma-ctao-official-homepage, src:cosmic-gamma-ctao-official-about-us-page (now https://www.ctao.org/organisation/), src:cosmic-gamma-ctao-official-technology-page (now https://www.ctao.org/emission-to-discovery/telescopes/), src:geo-arrays2-ctao-lst-inauguration-2026, src:cupid-experiment-official-page, src:cupid-arxiv-2503-02894, src:nexo-llnl-official-page, src:sensei-spurious-charge-2026-arxiv, src:currency2-sensei-snolab-first-results-arxiv-2312-13342, src:dm-noble-liquid-deap-3600-detector-paper, src:currency-deap3600-lrt2026-abstract, src:dm-noble-liquid-darkside-lngs-page, src:axions-dmradio-status-2022, src:axions-dmradio-cryo-2026, src:darkquest-proposal-arxiv-2022, src:edelweiss-subgev-migdal-2022-arxiv, src:edelweiss-subgev-ntl-2022-arxiv.
No new source records were needed.

## Not in my files (for the lead)
* 425 other files under data/atlas still contain "this session" / "sources fetched" / "fetched this" / "in this session" / "found this session" (geometry 39, documents 16, collaborations 70, maps 23, detectors 54, coverage 15, beamlines 3, facilities 23, sources 22, experiments 87, sites 45, results 16, accelerators 12).
* The coverage rows for my experiments carry process wording too: coverage/axions.json (experiment:dmradio: "this session", "PASS", "A24"), coverage/cosmic-gamma.json (experiment:h-e-s-s: "fetched this"), coverage/dm-cryogenic-low-threshold.json (experiment:edelweiss: "this session", "found this session"; experiment:sensei: "lead"), coverage/dm-noble-liquid.json (deap-3600: "lead"), coverage/fixed-target.json (darkquest: "wave"), coverage/muons.json (comet: "workstream", "Wave", "lead"), coverage/neutrino-mass-0vbb.json (cupid: "lead", "pass"; nexo: "lead").
* experiments/darkside-20k.json and experiments/dmradio.json (not assigned to me) still say "as of the source fetched" / "No INSPIRE experiment record was found ... this session" / "No dedicated DMRadio website was successfully fetched this session".
* detectors/cuore.json `/placements/0/note` still has the dangling-reference wording ("owned by the 'facilities' Wave 3 lead"); the CUPID notes now say CUORE's Hall A placement comes from detector:cuore.

## Unresolved
* CT5 (H.E.S.S. II) commissioning date: the collaboration pages give none; a Max Planck Society article dated 4 Oct 2012 (mpg.de/6373837, "saw its first light on 26 July") could settle it if the lead wants a sourced value.
* CUPID status (see above).


---

# Full change list

Date of all re-checks: 2026-10-25. Worktree: /Users/yatharthsirohi/Desktop/HEP-Graph-ar-rc-data (nothing committed).
'checked 2026-10-25' in a string means the source named was re-read that day (WebFetch, or the text of a PDF fetched that day); cached text of the quote-check run (same day) was used for PDFs.

Reason codes: process = process wording removed, substance kept; asof = dated wording, claim re-checked; STALE = claim contradicted by the cited source and corrected (see final report).

## data/atlas/experiments/comet.json

* `/intervals/0/note` -- dated wording
  * old: "Anchored to the Phase-I TDR (2018-12), the earliest dated evidence of the Phase-I programme found this session, as an approximate lower bound -- not a stated 'construction began' date. The collaboration's most recent dated activity found (collaboration meeting CM48, 27-31 July 2026) shows the programme is still ongoing; no data-taking or commissioning-complete statement was found."
  * new: "Anchored to the Phase-I Technical Design Report (December 2018), the earliest dated evidence of the Phase-I programme among the sources consulted, as an approximate lower bound -- not a stated 'construction began' date. The collaboration's site (comet.kek.jp, checked 2026-10-25) gives as its latest dated activity the CM48 collaboration meeting of 27-31 July 2026, which shows the programme is still ongoing; the site makes no statement that data taking or commissioning has been completed."
  * source/quote: https://comet.kek.jp/ (WebFetch 2026-10-25): 'COMET CM48 in 27/Jul.-31/Jul. 2026 at J-PARC.' is the only dated entry; no data-taking, commissioning or result statement on the page. https://arxiv.org/abs/1812.09018 (TDR, submitted 21 Dec 2018).
* `/notes/0` -- dated wording
  * old: "No physics results exist yet; the fetched TDR and official site describe an ongoing, staged construction/commissioning programme (most recent dated activity found: a collaboration meeting, CM48, in July 2026) with no data-taking or first-result statement. Stated explicitly rather than left to silence."
  * new: "No physics result is listed on the collaboration's site (comet.kek.jp, checked 2026-10-25). The Phase-I Technical Design Report (December 2018) describes a staged programme (Phase-I, then Phase-II) and the site shows continuing activity (latest dated entry: the CM48 collaboration meeting of 27-31 July 2026); neither reports data taking or a first physics result."
  * source/quote: https://comet.kek.jp/ (WebFetch 2026-10-25): 'COMET CM48 in 27/Jul.-31/Jul. 2026 at J-PARC.' is the only dated entry; no data-taking, commissioning or result statement on the page. https://arxiv.org/abs/1812.09018 (TDR, submitted 21 Dec 2018).
* `/notes/1` -- process wording removed, substance kept
  * old: "site:j-parc-hadron-hall was created by this workstream ('muons' owns it per the Wave-3 ID registry) specifically so the 'fixed-target' workstream can reference it for KOTO; its coordinate is a coarse, campus-level geocoder approximation (see the site record's own notes) and should be treated as such by any downstream reference."
  * new: "The coordinate of the J-PARC Hadron Hall site record (site:j-parc-hadron-hall) is approximate: the centroid of an OpenStreetMap building footprint, not a surveyed position of the COMET hall (see that record's own notes)."
  * source/quote: site record data/atlas/sites/j-parc-hadron-hall.json: coordinates.kind 'campus', 'Hadron Experimental Facility building footprint centroid' (the old note's 'coarse geocoder approximation' described a superseded point)
* `/summary/technical` -- dated wording
  * old: "...tion: more than 290 researchers from 48 institutes. No physics result has been produced yet as of the sources fetched this session."
  * new: "...tion: more than 290 researchers from 48 institutes. No physics result is listed on the collaboration's site as of 2026-10-25 (its latest dated entry is the CM48 meeting of 27-31 July 2026)."
  * source/quote: https://comet.kek.jp/ (WebFetch 2026-10-25): 'COMET CM48 in 27/Jul.-31/Jul. 2026 at J-PARC.' is the only dated entry; no data-taking, commissioning or result statement on the page. https://arxiv.org/abs/1812.09018 (TDR, submitted 21 Dec 2018).

## data/atlas/detectors/comet.json

* `/intervals/0/note` -- dated wording
  * old: "Anchored to the Phase-I TDR (2018-12), the earliest dated evidence of the Phase-I programme found this session, as an approximate lower bound -- not a stated 'construction began' date. The collaboration's most recent dated activity found (collaboration meeting CM48, 27-31 July 2026) shows the programme is still ongoing; no data-taking or commissioning-complete statement was found."
  * new: "Anchored to the Phase-I Technical Design Report (December 2018), the earliest dated evidence of the Phase-I programme among the sources consulted, as an approximate lower bound -- not a stated 'construction began' date. The collaboration's site (comet.kek.jp, checked 2026-10-25) gives as its latest dated activity the CM48 collaboration meeting of 27-31 July 2026, which shows the programme is still ongoing; the site makes no statement that data taking or commissioning has been completed."
  * source/quote: https://comet.kek.jp/ (WebFetch 2026-10-25): 'COMET CM48 in 27/Jul.-31/Jul. 2026 at J-PARC.' is the only dated entry; no data-taking, commissioning or result statement on the page. https://arxiv.org/abs/1812.09018 (TDR, submitted 21 Dec 2018).

## data/atlas/collaborations/comet.json

* `/formation/locator` -- process wording removed, substance kept
  * old: "COMET Phase-I TDR (arXiv:1812.09018) and comet.kek.jp; no formation date stated in either record fetched"
  * new: "COMET Phase-I TDR (arXiv:1812.09018) and comet.kek.jp; no formation date stated in either record consulted"
* `/formation/note` -- dated wording
  * old: "No fetched source states an explicit formation date."
  * new: "No source consulted (comet.kek.jp and the abstract of arXiv:1812.09018, both checked 2026-10-25) states an explicit formation date."
  * source/quote: https://comet.kek.jp/ and https://arxiv.org/abs/1812.09018 (WebFetch 2026-10-25): neither gives a formation date
* `/intervals/0/note` -- dated wording
  * old: "Anchored to the Phase-I TDR (2018-12), the earliest dated evidence of the Phase-I programme found this session, as an approximate lower bound -- not a stated 'construction began' date. The collaboration's most recent dated activity found (collaboration meeting CM48, 27-31 July 2026) shows the programme is still ongoing; no data-taking or commissioning-complete statement was found."
  * new: "Anchored to the Phase-I Technical Design Report (December 2018), the earliest dated evidence of the Phase-I programme among the sources consulted, as an approximate lower bound -- not a stated 'construction began' date. The collaboration's site (comet.kek.jp, checked 2026-10-25) gives as its latest dated activity the CM48 collaboration meeting of 27-31 July 2026, which shows the programme is still ongoing; the site makes no statement that data taking or commissioning has been completed."
  * source/quote: https://comet.kek.jp/ (WebFetch 2026-10-25): 'COMET CM48 in 27/Jul.-31/Jul. 2026 at J-PARC.' is the only dated entry; no data-taking, commissioning or result statement on the page. https://arxiv.org/abs/1812.09018 (TDR, submitted 21 Dec 2018).
* `/membership/country_count/note` -- dated wording
  * old: "Not stated on the official site page fetched."
  * new: "Not stated on the official site page (checked 2026-10-25)."
  * source/quote: https://comet.kek.jp/ (WebFetch 2026-10-25): only 'more than 290 researchers from 48 insitutes'
* `/notes/0` -- process wording removed, substance kept
  * old: "Leadership is left empty: person records are out of scope for this workstream."
  * new: "Leadership is not recorded in this record."
* `/notes/1` -- process wording removed, substance kept
  * old: "Derived field collaboration.experiment_ids is deliberately not written (v0.2 A1)."
  * new: "The experiment list is derived from the experiment records and is not stored here."
* `/summary/technical` -- dated wording
  * old: "International collaboration building COMET at the J-PARC Hadron Experimental Facility; per the collaboration's own site, more than 290 researchers from 48 institutes as of the most recent access (2026-09)."
  * new: "International collaboration building COMET at the J-PARC Hadron Experimental Facility; per the collaboration's own site, more than 290 researchers from 48 institutes (read 2026-09-17 and again 2026-10-25)."
  * source/quote: https://comet.kek.jp/ (WebFetch 2026-10-25): 'The COMET collaboration is composed of more than 290 researchers from 48 insitutes.'

## data/atlas/experiments/ctao.json

* `/intervals/0/note` -- dated wording
  * old: "...ower bound only (the year INSPIRE's CTA experiment record was created); no fetched source this session gives a construction-start date, a completion date, or a per-site percentage. CTAO's own wording implies construction and (partial) operation are concurrent, similar to how LST-1 and some MSTs are already reported elsewhere to be taking data on La Palma while the observatory as a whole is not complete. Status is kept at 'construction' pending a source that states otherw..."
  * new: "...ower bound only (the year INSPIRE's CTA experiment record was created). No source consulted (checked 2026-10-25) gives a construction-start date, a completion date or a per-site percentage. CTAO's own wording implies that construction and partial operation are concurrent: its press release of 15 October 2026 says the LST-1 prototype has produced results since 2020 even during its commissioning phase, while describing the completed LST sub-array as 'a crucial step toward the full scientific operation' of the observatory. Status is kept at 'construction' pending a source that states otherw..."
  * source/quote: https://www.ctao.org/news/the-large-sized-telescope-sub-array-is-inaugurated-on-ctao-north/ (WebFetch 2026-10-25; dateline 'La Palma, Spain, 15 October 2026'): 'a crucial step toward the full scientific operation of the Cherenkov Telescope Array Observatory (CTAO)'; 'More than 60 telescopes will be distributed between two observation stations'; 'Over the coming years, the LSTs will undergo commissioning and integration into CTAO operations.' https://www.ctao.org/organisation/ (WebFetch 2026-10-25): 'preparations for construction' at the two array sites; 'The construction and operation of the CTAO is a global initiative'.
* `/intervals/1/note` -- dated wording / process wording removed, substance kept
  * old: "Added 2026-10-25. CTAO press release, La Palma, 15 October 2026: 250 scientists \"celebrated the inauguration of the Large-Sized Telescope (LST) sub-array at the CTAO-North site\"; \"The completion of the four telescopes marks a significant milestone ... and represents a crucial step toward the full scientific operation\" of CTAO; \"With the three new LSTs (LST-2, LST-3, and LST-4) joining the existing LST-1, the four telescopes will become a true array\"; \"Over the coming years, the LSTs will undergo commissioning and integration into CTAO operations.\" LST-1, the prototype, has been observing 'even during its commissioning phase' since 2020. Recorded as a milestone annotation (kind phase) and not as a commiss..."
  * new: "CTAO press release, La Palma, 15 October 2026: 250 scientists \"celebrated the inauguration of the Large-Sized Telescope (LST) sub-array at the CTAO-North site\"; \"The completion of the four telescopes marks a significant milestone ... and represents a crucial step toward the full scientific operation\" of CTAO; \"With the three new LSTs (LST-2, LST-3, and LST-4) joining the existing LST-1, the four telescopes will become a true array\"; \"Over the coming years, the LSTs will undergo commissioning and integration into CTAO operations.\" LST-1, the prototype, has produced 'groundbreaking results since 2020', even during its commissioning phase. Recorded as a milestone annotation (kind phase) and not as a commiss..."
  * source/quote: press release 15 Oct 2026: 'Even during its commissioning phase, the Large-Sized Telescope prototype (LST-1) has produced groundbreaking results since 2020.'
* `/notes/0` -- process wording removed, substance kept
  * old: "site_ids, detector_ids, document_ids, result_ids are deliberately not written (v0.2 A1 derived fields)."
  * new: "Derived lists (site_ids, detector_ids, document_ids, result_ids) are not stored in this record; they are derived from the other records."
* `/notes/1` -- dated wording
  * old: "ctao.org's dedicated 'sites', 'arrays' and 'news' subpages returned 404 or empty JavaScript-shell content on every attempt this session; construction-phase details (e.g. LST-1's own commissioning date, per-site telescope counts already installed) were not sourced and are listed in missing_fields."
  * new: "On 2026-10-25 ctao.org/sites/ and ctao.org/arrays/ returned HTTP 404 and ctao.org/news/ returned only a page title with no article list. The pages that could be read give no commissioning date for LST-1 and no count of installed Medium- or Small-Sized Telescopes at either site (the press release of 15 October 2026 reports only that the four-telescope LST sub-array at CTAO-North is complete), so these are not recorded."
  * source/quote: WebFetch 2026-10-25: https://www.ctao.org/sites/ and /arrays/ -> HTTP 404; https://www.ctao.org/news/ -> page title only
  * source/quote: https://www.ctao.org/sites/ and /arrays/ -> HTTP 404, https://www.ctao.org/news/ -> page title only (WebFetch 2026-10-25); press release 15 Oct 2026: 'The completion of the four telescopes marks a significant milestone'; 'More than 60 telescopes will be distributed between two observation stations'; 'Over the coming years, the LSTs will undergo commissioning and integration into CTAO operations.'
* `/notes/2` -- process wording removed, substance kept
  * old: "No results or technical documents were written in this pass (non-flagship experiment; mandatory bar only per the wave-3 brief)."
  * new: "No results or technical documents are recorded for CTAO yet."
* `/summary/technical` -- dated wording
  * old: "... Data Management Centre in Zeuthen, Germany. Under construction as of the sources fetched this session."
  * new: "... Data Management Centre in Zeuthen, Germany. Under construction as of 2026-10-25 (CTAO press release of 2026-10-15 on the completed LST sub-array)."
  * source/quote: https://www.ctao.org/news/the-large-sized-telescope-sub-array-is-inaugurated-on-ctao-north/ (WebFetch 2026-10-25; dateline 'La Palma, Spain, 15 October 2026'): 'a crucial step toward the full scientific operation of the Cherenkov Telescope Array Observatory (CTAO)'; 'More than 60 telescopes will be distributed between two observation stations'; 'Over the coming years, the LSTs will undergo commissioning and integration into CTAO operations.' https://www.ctao.org/organisation/ (WebFetch 2026-10-25): 'preparations for construction' at the two array sites; 'The construction and operation of the CTAO is a global initiative'.

## data/atlas/detectors/ctao.json

* `/intervals/0/note` -- dated wording
  * old: "2015 is a lower bound only (the year INSPIRE's CTA experiment record was created); no fetched source this session gives a construction-start date."
  * new: "2015 is a lower bound only (the year INSPIRE's CTA experiment record was created); no source consulted (checked 2026-10-25) gives a construction-start date."
  * source/quote: https://www.ctao.org/news/the-large-sized-telescope-sub-array-is-inaugurated-on-ctao-north/ (WebFetch 2026-10-25; dateline 'La Palma, Spain, 15 October 2026'): 'a crucial step toward the full scientific operation of the Cherenkov Telescope Array Observatory (CTAO)'; 'More than 60 telescopes will be distributed between two observation stations'; 'Over the coming years, the LSTs will undergo commissioning and integration into CTAO operations.' https://www.ctao.org/organisation/ (WebFetch 2026-10-25): 'preparations for construction' at the two array sites; 'The construction and operation of the CTAO is a global initiative'.
* `/intervals/1/note` -- dated wording / process wording removed, substance kept
  * old: "Added 2026-10-25. CTAO press release, La Palma, 15 October 2026: 250 scientists \"celebrated the inauguration of the Large-Sized Telescope (LST) sub-array at the CTAO-North site\"; \"The completion of the four telescopes marks a significant milestone ... and represents a crucial step toward the full scientific operation\" of CTAO; \"With the three new LSTs (LST-2, LST-3, and LST-4) joining the existing LST-1, the four telescopes will become a true array\"; \"Over the coming years, the LSTs will undergo commissioning and integration into CTAO operations.\" LST-1, the prototype, has been observing 'even during its commissioning phase' since 2020. Recorded as a milestone annotation (kind phase) and not as a commiss..."
  * new: "CTAO press release, La Palma, 15 October 2026: 250 scientists \"celebrated the inauguration of the Large-Sized Telescope (LST) sub-array at the CTAO-North site\"; \"The completion of the four telescopes marks a significant milestone ... and represents a crucial step toward the full scientific operation\" of CTAO; \"With the three new LSTs (LST-2, LST-3, and LST-4) joining the existing LST-1, the four telescopes will become a true array\"; \"Over the coming years, the LSTs will undergo commissioning and integration into CTAO operations.\" LST-1, the prototype, has produced 'groundbreaking results since 2020', even during its commissioning phase. Recorded as a milestone annotation (kind phase) and not as a commiss..."
  * source/quote: press release 15 Oct 2026: 'Even during its commissioning phase, the Large-Sized Telescope prototype (LST-1) has produced groundbreaking results since 2020.'
* `/notes/0` -- process wording removed, substance kept
  * old: "document_ids deliberately not written (v0.2 A1 derived field)."
  * new: "The document list is derived from the document records and is not stored here."
* `/notes/1` -- dated wording
  * old: "Per-site current telescope counts (how many of each class are actually installed and operating today, as opposed to the design maximums) were not sourced this session."
  * new: "No source consulted (checked 2026-10-25) gives the current per-site counts of installed and operating Medium- and Small-Sized Telescopes, as opposed to the design maximums; the press release of 15 October 2026 reports the four-telescope LST sub-array at CTAO-North as complete, with commissioning of the array still ahead."
  * source/quote: https://www.ctao.org/news/the-large-sized-telescope-sub-array-is-inaugurated-on-ctao-north/ (WebFetch 2026-10-25; dateline 'La Palma, Spain, 15 October 2026'): 'a crucial step toward the full scientific operation of the Cherenkov Telescope Array Observatory (CTAO)'; 'More than 60 telescopes will be distributed between two observation stations'; 'Over the coming years, the LSTs will undergo commissioning and integration into CTAO operations.' https://www.ctao.org/organisation/ (WebFetch 2026-10-25): 'preparations for construction' at the two array sites; 'The construction and operation of the CTAO is a global initiative'.
  * source/quote: https://www.ctao.org/sites/ and /arrays/ -> HTTP 404, https://www.ctao.org/news/ -> page title only (WebFetch 2026-10-25); press release 15 Oct 2026: 'The completion of the four telescopes marks a significant milestone'; 'More than 60 telescopes will be distributed between two observation stations'; 'Over the coming years, the LSTs will undergo commissioning and integration into CTAO operations.'
* `/summary/technical` -- dated wording
  * old: "Imaging-atmospheric-Cherenkov arrays at two sites (La Palma / Paranal), using Large-, Medium- and Small-Sized Telescope classes (design maximum 4 LST + 23 MST + 37 SST) to cover 20 GeV-300 TeV; under construction as of the sources fetched this session."
  * new: "Imaging-atmospheric-Cherenkov arrays at two sites (La Palma / Paranal), using Large-, Medium- and Small-Sized Telescope classes (design maximum 4 LST + 23 MST + 37 SST) to cover 20 GeV-300 TeV; under construction as of 2026-10-25 (CTAO press release of 2026-10-15 on the completed LST sub-array)."
  * source/quote: https://www.ctao.org/news/the-large-sized-telescope-sub-array-is-inaugurated-on-ctao-north/ (WebFetch 2026-10-25; dateline 'La Palma, Spain, 15 October 2026'): 'a crucial step toward the full scientific operation of the Cherenkov Telescope Array Observatory (CTAO)'; 'More than 60 telescopes will be distributed between two observation stations'; 'Over the coming years, the LSTs will undergo commissioning and integration into CTAO operations.' https://www.ctao.org/organisation/ (WebFetch 2026-10-25): 'preparations for construction' at the two array sites; 'The construction and operation of the CTAO is a global initiative'.

## data/atlas/collaborations/ctao.json

* `/formation/note` -- dated wording
  * old: "...ot a traditional physics 'collaboration' with a formation meeting; no fetched source states when the ERIC was legally established. No formal 'collaboratio..."
  * new: "...ot a traditional physics 'collaboration' with a formation meeting; no source consulted (checked 2026-10-25) states when the ERIC was legally established. No formal 'collaboratio..."
  * source/quote: https://www.ctao.org/organisation/ (WebFetch 2026-10-25): no establishment date
* `/intervals/0/note` -- process wording removed, substance kept
  * old: "Start date is only a lower bound (the date this session's source was accessed/verified), not a sourced founding date for the CTAO Central Organisation/ERIC."
  * new: "Start date (2026) is only a lower bound, the year the CTAO homepage was read; it is not a sourced founding date for the CTAO Central Organisation / ERIC."
* `/notes/0` -- process wording removed, substance kept
  * old: "experiment_ids, document_ids deliberately not written (v0.2 A1 derived fields)."
  * new: "The experiment and document lists are derived from the other records and are not stored here."
* `/notes/2` -- dated wording
  * old: "membership counts left null: no fetched source states them in the sense of institution/scientist counts (only 'countries around the globe and one intergovernmental organisation' supporting it, per the homepage)."
  * new: "Membership counts are left empty: no source consulted (checked 2026-10-25) states institution or scientist counts (the homepage says only that the CTAO Central Organisation 'counts on the support of countries around the globe and one intergovernmental organisation')."
  * source/quote: https://www.ctao.org/ (WebFetch 2026-10-25): 'The CTAO Central Organisation counts on the support of countries around the globe and one intergovernmental organisation'; no institute/scientist counts
* `/notes/3` -- process wording removed, substance kept
  * old: "Leadership left empty: person records are out of scope this wave and none was sourced."
  * new: "Leadership is not recorded in this record."

## data/atlas/experiments/cupid.json

* `/intervals/0/locator` -- process wording removed, substance kept
  * old: "no fetched primary source gives an exact CUPID approval or construction-start date"
  * new: "no primary source consulted gives an exact CUPID approval or construction-start date"
* `/intervals/0/note` -- dated wording
  * old: "No source fetched in this session directly states CUPID's DOE Critical-Decision stage or a construction-start date with a quote this agent saw verbatim; a secondary web summary described CD-0 ('approval of mission need') and a prototype 'in construction' for mid-2025 data, but this agent could not re-verify that specific wording against a directly fetched primary source in this session, so status is recorded conservatively as `proposed` rather than `construction`. The official CUPID site describes the detector only in future tense ('CUPID will profit of ...'). `start` (2025) is the year of the earliest dated CUPID collaboration paper found in this session (a lower bound, not a true approval/construction date), chosen so a null/null interval does not derive to 'no presence'. Later check (arXiv:2503.02894, Conclusions): the paper states 'CUPID construction activities have already started, including preparations for the cryostat upgrade and the setup of the detector assembly infrastructure' and that data taking is expected 'in the very early years of the next decade'; the interval status was left as `proposed` pending an integrator decision on mapping this to the status vocabulary."
  * new: "No source consulted (checked 2026-10-25) states CUPID's DOE Critical Decision stage or a construction-start date. A secondary web summary described CD-0 ('approval of mission need') and a prototype 'in construction' for mid-2025 data; that wording was not found in any primary source consulted, so it is not recorded. The collaboration's site (cupidexperiment.org/experiment/, checked 2026-10-25) describes the detector only in the future tense ('CUPID will profit of ...'). `start` (2025) is the year of the earliest dated CUPID collaboration paper found (arXiv:2503.02894, submitted March 2025), a lower bound and not a true approval or construction date, chosen so that an interval with no start does not derive to 'no presence'. That paper's Conclusions state 'CUPID construction activities have already started, including preparations for the cryostat upgrade and the setup of the detector assembly infrastructure' and that data taking is expected 'in the very early years of the next decade'; the status is nonetheless kept at `proposed` because the paper gives no construction-start date and the collaboration's own site still uses the future tense."
  * source/quote: https://cupidexperiment.org/experiment/ (WebFetch 2026-10-25): 'CUPID will profit of the established CUORE cryogenic infrastructure'; no DOE Critical Decision mentioned; footer 'Copyright 2026 CUPID Collaboration'. https://arxiv.org/abs/2503.02894 (v1 1 Mar 2025, v2 11 Jul 2025; PDF text read 2026-10-25), Conclusions: 'CUPID construction activities have already started, including preparations for the cryostat upgrade and the setup of the detector assembly infrastructure. Based on current planning, data taking is expected to begin in the very early years of the next decade'. The PDF mentions DOE only in the funding acknowledgement.
* `/notes`
  * old list: ["Located in LNGS (reuses the existing CUORE cryostat, itself in Hall A): this record references site:lngs-hall-a, owned by the 'facilities' Wave 3 lead, which does not exist yet in this repository as of 2026-09-17 (dangling reference).", "facility:lngs already exists (owned by the fermilab-neutrino-other lead) and is referenced here, not edited.", "Status is recorded conservatively as 'proposed': the official CUPID site describes the detector only in future tense and no source fetched in this session gives an unambiguous 'under construction' statement with a verifiable quote. A secondary summary described a DOE CD-0 mission-need approval and a prototype under construction for mid-2025 data, which this agent could not re-verify against a directly fetched primary source; reported here for the domain lead's awareness.", "No INSPIRE experiment-registry lookup was performed in this session; external.inspire_experiment is left null with this note rather than guessed.", "Collaboration formation date not sourced in this session."]
  * new list: ["Located in LNGS in the existing CUORE cryostat, which the atlas places in Hall A (site:lngs-hall-a, via detector:cuore; that placement's source gives only the general LNGS location). The CUPID sources consulted state the general LNGS location, not the Hall A designation.", "Status is recorded conservatively as 'proposed': the collaboration's site describes the detector only in the future tense and no primary source consulted (checked 2026-10-25) gives an unambiguous 'under construction' statement or a construction-start date. The March 2025 paper (arXiv:2503.02894) says construction activities 'have already started' (see the interval note). A secondary summary of a DOE CD-0 mission-need approval and a prototype under construction for mid-2025 data was not found in any primary source consulted.", "No INSPIRE experiment-registry identifier is recorded for CUPID (external.inspire_experiment is empty).", "No source consulted (checked 2026-10-25) gives the collaboration's formation date."]
* `/summary/technical` -- dated wording
  * old: "CUPID (CUORE Upgrade with Particle IDentification): proposed ton-scale array of ~1500 Li2MoO4 scintillating bolometers targeting 0νββ of 100Mo (Qbb = 3034 keV), reusing the CUORE cryostat at LNGS. Successor to CUORE; no confirmed construction-start date sourced in this session."
  * new: "CUPID (CUORE Upgrade with Particle IDentification): proposed ton-scale array of ~1500 Li2MoO4 scintillating bolometers targeting 0νββ of 100Mo (Qbb = 3034 keV), reusing the CUORE cryostat at LNGS. Successor to CUORE; no source consulted (checked 2026-10-25) gives a construction-start date."
  * source/quote: https://cupidexperiment.org/experiment/ (WebFetch 2026-10-25): 'CUPID will profit of the established CUORE cryogenic infrastructure'; no DOE Critical Decision mentioned; footer 'Copyright 2026 CUPID Collaboration'. https://arxiv.org/abs/2503.02894 (v1 1 Mar 2025, v2 11 Jul 2025; PDF text read 2026-10-25), Conclusions: 'CUPID construction activities have already started, including preparations for the cryostat upgrade and the setup of the detector assembly infrastructure. Based on current planning, data taking is expected to begin in the very early years of the next decade'. The PDF mentions DOE only in the funding acknowledgement.

## data/atlas/detectors/cupid.json

* `/intervals/0/note` -- dated wording
  * old: "See experiment:cupid interval note; no confirmed physical-construction start date sourced in this session. `start` (2025) is the earliest dated CUPID collaboration paper found, a lower bound not a true start date."
  * new: "See the experiment:cupid interval note. No source consulted (checked 2026-10-25) gives a physical-construction start date. `start` (2025) is the year of the earliest dated CUPID collaboration paper found, a lower bound and not a true start date."
  * source/quote: https://cupidexperiment.org/experiment/ (WebFetch 2026-10-25): 'CUPID will profit of the established CUORE cryogenic infrastructure'; no DOE Critical Decision mentioned; footer 'Copyright 2026 CUPID Collaboration'. https://arxiv.org/abs/2503.02894 (v1 1 Mar 2025, v2 11 Jul 2025; PDF text read 2026-10-25), Conclusions: 'CUPID construction activities have already started, including preparations for the cryostat upgrade and the setup of the detector assembly infrastructure. Based on current planning, data taking is expected to begin in the very early years of the next decade'. The PDF mentions DOE only in the funding acknowledgement.
* `/notes`
  * old list: ["Placed at site:lngs-hall-a (dangling reference: owned by the 'facilities' lead, not yet created).", "Verification note (2026-09-17, src:0vbb-verify-*): the cited source confirms LNGS generally, not the Hall A designation specifically. CUPID is planned to reuse the CUORE cryostat, which is in Hall A, but no directly fetched source in this session states 'Hall A' for CUPID verbatim; confidence on the placement remains 'uncertain' for this reason as well as the unconfirmed construction timeline."]
  * new list: ["The cited sources confirm LNGS generally, not the Hall A designation specifically. CUPID is planned to reuse the CUORE cryostat, which the atlas places in Hall A (detector:cuore), but no source consulted (checked 2026-10-25) states 'Hall A' for CUPID verbatim; confidence in the placement is 'uncertain' for this reason as well as the unconfirmed construction timeline."]
* `/placements/0/note` -- process wording removed, substance kept
  * old: "site:lngs-hall-a is owned by the 'facilities' Wave 3 lead and does not exist yet in this repository (dangling reference). The cited source states the general LNGS location, not the Hall A designation; see record-level verification note."
  * new: "The cited source states the general LNGS location, not the Hall A designation; see the record-level note."

## data/atlas/collaborations/cupid.json

* `/formation/locator` -- process wording removed, substance kept
  * old: "no fetched source states an explicit CUPID collaboration formation date"
  * new: "no source consulted states an explicit CUPID collaboration formation date"
* `/formation/note` -- dated wording
  * old: "No source fetched in this session states an explicit formation date; left null (v0.2 A17)."
  * new: "No source consulted (checked 2026-10-25) states an explicit formation date; left empty."
  * source/quote: https://cupidexperiment.org/ (WebFetch 2026-10-25): no formation date; https://arxiv.org/abs/2503.02894: none
* `/notes/0` -- dated wording
  * old: "No source fetched in this session states institution/member/country counts; membership block left null per v0.2 A17."
  * new: "No source consulted (checked 2026-10-25) states institution, member or country counts; the membership block is left empty (the site shows member-institution logos without a count)."
  * source/quote: https://cupidexperiment.org/ (WebFetch 2026-10-25): 'Collaboration Members' section shows logos, no count
* `/notes/1` -- process wording removed, substance kept
  * old: "Institution-level membership rows and person records are owned by the membership-lead workstream and are not written here."
  * new: "Institution-level membership rows and person records are not recorded here."
* `/notes/2` -- process wording removed, substance kept
  * old: "Derived field collaboration.experiment_ids is deliberately not written (v0.2 A1)."
  * new: "The experiment list is derived from the experiment records and is not stored here."
* `/summary/technical` -- dated wording
  * old: "CUPID Collaboration: preparing the proposed ~1500-crystal Li2MoO4 scintillating-bolometer successor to CUORE at LNGS; institution/member/country counts and formation date not sourced in this session."
  * new: "CUPID Collaboration: preparing the proposed ~1500-crystal Li2MoO4 scintillating-bolometer successor to CUORE at LNGS; no source consulted (checked 2026-10-25) gives institution, member or country counts or a formation date."
  * source/quote: https://cupidexperiment.org/ (WebFetch 2026-10-25)

## data/atlas/experiments/edelweiss.json

* `/facility_roles/0/note` -- dated wording
  * old: "No source fetched this session states when EDELWEISS began hosting at LSM; start left null (unknown), not invented."
  * new: "No source consulted (checked 2026-10-25) states when EDELWEISS began hosting at LSM; the start is left unknown."
  * source/quote: edelweiss.in2p3.fr and www.edelweiss.in2p3.fr: WebFetch 2026-10-25 -> getaddrinfo ENOTFOUND (https and http). arXiv:2203.03993 and arXiv:2211.04176 full texts read 2026-10-25: no founding, approval, generation-transition or LSM start date.
* `/intervals/0/note` -- dated wording
  * old: "No source fetched this session (including the INSPIRE registry, which lists EDELWEISS, EDELWEISS-II and EDELWEISS-III as separate experiment records with no dates populated) gives a founding, approval or generation-transition date. Start is left null per A3/A17 rather than invented; only the current sub-GeV programme below carries dated, quoted evide..."
  * new: "No source consulted (the arXiv papers cited here, checked 2026-10-25; the INSPIRE registry, as read on 2026-09-17, lists EDELWEISS, EDELWEISS-II and EDELWEISS-III as separate experiment records with no dates populated) gives a founding, approval or generation-transition date. The start is left unknown; only the current sub-GeV programme below carries dated, quoted evide..."
  * source/quote: edelweiss.in2p3.fr and www.edelweiss.in2p3.fr: WebFetch 2026-10-25 -> getaddrinfo ENOTFOUND (https and http). arXiv:2203.03993 and arXiv:2211.04176 full texts read 2026-10-25: no founding, approval, generation-transition or LSM start date.
* `/links/website/note` -- dated wording
  * old: "URL from the INSPIRE record; DNS resolution failed (ENOTFOUND) for both edelweiss.in2p3.fr and www.edelweiss.in2p3.fr when checked 2026-09-17, so the site's current liveness is not confirmed."
  * new: "URL from the INSPIRE record; DNS resolution failed for both edelweiss.in2p3.fr and www.edelweiss.in2p3.fr when checked on 2026-09-17 and again on 2026-10-25, so the site's current liveness is not confirmed."
  * source/quote: edelweiss.in2p3.fr and www.edelweiss.in2p3.fr: WebFetch 2026-10-25 -> getaddrinfo ENOTFOUND (https and http). arXiv:2203.03993 and arXiv:2211.04176 full texts read 2026-10-25: no founding, approval, generation-transition or LSM start date.
* `/notes/1` -- dated wording
  * old: "No official EDELWEISS website could be reached this session (DNS failure); all sourcing for this record comes from arXiv papers and the INSPIRE registry."
  * new: "No official EDELWEISS website could be reached (checked 2026-10-25: edelweiss.in2p3.fr and www.edelweiss.in2p3.fr do not resolve); all sourcing for this record comes from arXiv papers and the INSPIRE registry."
  * source/quote: edelweiss.in2p3.fr and www.edelweiss.in2p3.fr: WebFetch 2026-10-25 -> getaddrinfo ENOTFOUND (https and http). arXiv:2203.03993 and arXiv:2211.04176 full texts read 2026-10-25: no founding, approval, generation-transition or LSM start date.
* `/notes/2` -- dated wording
  * old: "... detector generations before the current 200 g NbSi-TES programme) is NOT recorded: no source fetched this session states them. This is a significant gap relative to CRESST/CDMS's richer sourced histories and should be revisited with a working official site or a detector-history paper."
  * new: "... detector generations before the current 200 g NbSi-TES programme) is not recorded: no source consulted (checked 2026-10-25) states them. A working official site or a detector-history paper would settle this."
  * source/quote: edelweiss.in2p3.fr and www.edelweiss.in2p3.fr: WebFetch 2026-10-25 -> getaddrinfo ENOTFOUND (https and http). arXiv:2203.03993 and arXiv:2211.04176 full texts read 2026-10-25: no founding, approval, generation-transition or LSM start date.
* `/summary/technical` -- dated wording
  * old: "...w-on 'CRYOSEL' detector design is under development. Earlier EDELWEISS/EDELWEISS-II/III generations are not richly documented in this record for lack of a reachable official source this session."
  * new: "...w-on 'CRYOSEL' detector design is under development. Earlier EDELWEISS, EDELWEISS-II and EDELWEISS-III generations are not documented in detail here because no official EDELWEISS site could be reached (checked 2026-10-25)."
  * source/quote: edelweiss.in2p3.fr and www.edelweiss.in2p3.fr: WebFetch 2026-10-25 -> getaddrinfo ENOTFOUND (https and http). arXiv:2203.03993 and arXiv:2211.04176 full texts read 2026-10-25: no founding, approval, generation-transition or LSM start date.

## data/atlas/detectors/edelweiss.json

* `/notes/0` -- STALE: statement contradicted by the cited source; corrected
  * old: "Operating temperature (mK) not stated in any source fetched this session; earlier detector generations (Ge-NTD sensors, EDELWEISS-I/II/III arrays) not separately specified for lack of a reachable official source."
  * new: "The NbSi transition-edge sensor is operated at about 44 mK (arXiv:2211.04176: 'The TES is operated around 44 mK'; arXiv:2203.03993 gives the same working temperature). The cryostat base temperature and the operating temperatures of earlier detector generations (Ge-NTD sensors, EDELWEISS-I/II/III arrays) are not given by the sources consulted (checked 2026-10-25), and no official site could be reached for them."
  * source/quote: arXiv:2211.04176 PDF text (read 2026-10-25): 'The TES is operated around 44 mK, the temperature at which the transition between the normal and the superconducting states start to occur.'; arXiv:2203.03993: 'The film is maintained near the temperature of 44 mK, at which its transition between the superconducting and normal state occurs'. The old note said no source stated an operating temperature.
* `/placements/0/note` -- dated wording
  * old: "No source fetched this session gives a start date for this placement; left null (unknown) rather than invented."
  * new: "No source consulted (checked 2026-10-25) gives a start date for this placement; the start is left unknown."
  * source/quote: edelweiss.in2p3.fr and www.edelweiss.in2p3.fr: WebFetch 2026-10-25 -> getaddrinfo ENOTFOUND (https and http). arXiv:2203.03993 and arXiv:2211.04176 full texts read 2026-10-25: no founding, approval, generation-transition or LSM start date.

## data/atlas/collaborations/edelweiss.json

* `/intervals/1/note` -- process wording removed, substance kept
  * old: "Added to give a dated, covering interval matching experiment:edelweiss's current programme; the collaboration's founding date itself remains unsourced (see the earlier undated interval)."
  * new: "Matches the dates of experiment:edelweiss's current programme; the collaboration's founding date itself remains unsourced (see the earlier undated interval)."
* `/notes/0` -- dated wording
  * old: "No official EDELWEISS website could be reached this session (DNS failure on both edelweiss.in2p3.fr and www.edelweiss.in2p3.fr); no institution/member counts found in the arXiv papers fetched."
  * new: "No official EDELWEISS website could be reached (checked 2026-10-25: neither edelweiss.in2p3.fr nor www.edelweiss.in2p3.fr resolves); no institution or member counts appear in the arXiv papers consulted."
  * source/quote: edelweiss.in2p3.fr and www.edelweiss.in2p3.fr: WebFetch 2026-10-25 -> getaddrinfo ENOTFOUND (https and http). arXiv:2203.03993 and arXiv:2211.04176 full texts read 2026-10-25: no founding, approval, generation-transition or LSM start date.

## data/atlas/experiments/h-e-s-s.json

* `/intervals/1/note` -- process wording removed, substance kept
  * old: "Interval start reuses the first-light year (About page: 'Since its first light in 2002'); the Telescopes page says CT1-4 were installed between 2001 and 2003, and no source fetched gives a distinct 'full four-telescope array complete' date."
  * new: "Interval start reuses the first-light year (About page: 'Since its first light in 2002'); the Telescopes page says CT1-4 were installed between 2001 and 2003, and no source consulted gives a distinct 'full four-telescope array complete' date."
* `/notes/0` -- process wording removed, substance kept
  * old: "site_ids, detector_ids, document_ids, result_ids are deliberately not written (v0.2 A1 derived fields)."
  * new: "Derived lists (site_ids, detector_ids, document_ids, result_ids) are not stored in this record; they are derived from the other records."
* `/notes/1` -- dated wording
  * old: "CT5 (H.E.S.S. II) commissioning date not sourced this session; left null rather than using the commonly cited 2012 date, which was not seen in a fetched source."
  * new: "The collaboration's About, Telescopes and Site pages (Internet Archive captures of April-July 2026, read 2026-10-25) do not give the commissioning date of CT5 (H.E.S.S. II), so none is recorded. A Max Planck Society article dated 4 October 2012 (mpg.de/6373837) reports the first light of the 28 m telescope on 26 July; it is not a collaboration source and is not recorded as the commissioning date."
  * source/quote: https://hess-experiment.eu/ (WebFetch 2026-10-25): site shows 'Due to precautionary security measures, we are taking down this web site/service temporarily.' Internet Archive captures of hess-experiment.eu (about-hess 2026-05-01, telescopes April 2026, h-e-s-s-site 2026-07-29), text read 2026-10-25: telescopes page says only 'CT1-4 ... installed between 2001 and 2003' and that CT5 has a 28-meter mirror; the CT5 camera was replaced in October 2019 (FlashCam); no CT5 commissioning year. https://www.mpg.de/6373837/a-glimpse-into-turbulent-space (WebFetch 2026-10-25; article date October 04, 2012): 'The telescope has an antenna diameter of 28 metres and saw its first light on 26 July.'
  * source/quote: Internet Archive captures of hess-experiment.eu: about-hess (2026-05-01), telescopes (April 2026), h-e-s-s-site (2026-07-29); text read 2026-10-25 contains no CT5 commissioning year (CT1-4 'installed between 2001 and 2003'; CT5 camera replaced October 2019). Live hess-experiment.eu on 2026-10-25: 'Due to precautionary security measures, we are taking down this web site/service temporarily.'
* `/notes/2` -- process wording removed, substance kept
  * old: "No results or technical documents were written in this pass (non-flagship experiment; mandatory bar only per the wave-3 brief)."
  * new: "No results or technical documents are recorded for H.E.S.S. yet."
* `/notes/3` -- process wording removed, substance kept
  * old: "H.E.S.S. II (the 28 m CT5 telescope) is part of the array per the official site, but no fetched source dated its inauguration; the undated interval was removed on 2026-09-18 verification rather than kept without a quote."
  * new: "H.E.S.S. II (the 28 m CT5 telescope) is part of the array per the official site, but no collaboration source consulted gives the date of its inauguration, so no interval is recorded for it."
* `/summary/technical` -- dated wording
  * old: "...800 m altitude in the Khomas Highland, Namibia. First light 2002; the 28 m CT5 telescope's commissioning date was not confirmed by a source fetched this session."
  * new: "...800 m altitude in the Khomas Highland, Namibia. First light 2002; the collaboration's About, Telescopes and Site pages (Internet Archive captures, read 2026-10-25) do not give the commissioning date of the 28 m CT5 telescope."
  * source/quote: https://hess-experiment.eu/ (WebFetch 2026-10-25): site shows 'Due to precautionary security measures, we are taking down this web site/service temporarily.' Internet Archive captures of hess-experiment.eu (about-hess 2026-05-01, telescopes April 2026, h-e-s-s-site 2026-07-29), text read 2026-10-25: telescopes page says only 'CT1-4 ... installed between 2001 and 2003' and that CT5 has a 28-meter mirror; the CT5 camera was replaced in October 2019 (FlashCam); no CT5 commissioning year. https://www.mpg.de/6373837/a-glimpse-into-turbulent-space (WebFetch 2026-10-25; article date October 04, 2012): 'The telescope has an antenna diameter of 28 metres and saw its first light on 26 July.'
  * source/quote: Internet Archive captures of hess-experiment.eu: about-hess (2026-05-01), telescopes (April 2026), h-e-s-s-site (2026-07-29); text read 2026-10-25 contains no CT5 commissioning year (CT1-4 'installed between 2001 and 2003'; CT5 camera replaced October 2019). Live hess-experiment.eu on 2026-10-25: 'Due to precautionary security measures, we are taking down this web site/service temporarily.'

## data/atlas/detectors/h-e-s-s.json

* `/intervals/0/note` -- process wording removed, substance kept
  * old: "Start is the first-light year (About page: 'Since its first light in 2002'); the Telescopes page says CT1-4 were installed between 2001 and 2003, so the date the full four-telescope array operated is not given by a source fetched."
  * new: "Start is the first-light year (About page: 'Since its first light in 2002'); the Telescopes page says CT1-4 were installed between 2001 and 2003, so the date the full four-telescope array operated is not given by a source consulted."
* `/intervals/1/note` -- dated wording
  * old: "Commissioning date not sourced this session; publicly reported elsewhere as 2012 but not confirmed by a fetched source."
  * new: "The collaboration's About, Telescopes and Site pages (Internet Archive captures of April-July 2026, read 2026-10-25) give no commissioning date for CT5. A Max Planck Society article dated 4 October 2012 (mpg.de/6373837) reports the first light of the 28 m telescope on 26 July; it is not a collaboration source, so the start is left empty."
  * source/quote: https://hess-experiment.eu/ (WebFetch 2026-10-25): site shows 'Due to precautionary security measures, we are taking down this web site/service temporarily.' Internet Archive captures of hess-experiment.eu (about-hess 2026-05-01, telescopes April 2026, h-e-s-s-site 2026-07-29), text read 2026-10-25: telescopes page says only 'CT1-4 ... installed between 2001 and 2003' and that CT5 has a 28-meter mirror; the CT5 camera was replaced in October 2019 (FlashCam); no CT5 commissioning year. https://www.mpg.de/6373837/a-glimpse-into-turbulent-space (WebFetch 2026-10-25; article date October 04, 2012): 'The telescope has an antenna diameter of 28 metres and saw its first light on 26 July.'
  * source/quote: Internet Archive captures of hess-experiment.eu: about-hess (2026-05-01), telescopes (April 2026), h-e-s-s-site (2026-07-29); text read 2026-10-25 contains no CT5 commissioning year (CT1-4 'installed between 2001 and 2003'; CT5 camera replaced October 2019). Live hess-experiment.eu on 2026-10-25: 'Due to precautionary security measures, we are taking down this web site/service temporarily.'
* `/notes/0` -- process wording removed, substance kept
  * old: "document_ids deliberately not written (v0.2 A1 derived field)."
  * new: "The document list is derived from the document records and is not stored here."
* `/summary/technical` -- dated wording
  * old: "Hybrid imaging-atmospheric-Cherenkov array: four 12 m telescopes (since 2002) plus a central 28 m telescope (CT5, commissioning date not sourced this session) at 1800 m in the Khomas Highland, Namibia."
  * new: "Hybrid imaging-atmospheric-Cherenkov array: four 12 m telescopes (since 2002) plus a central 28 m telescope (CT5, commissioning date not given by the collaboration's pages as read on 2026-10-25) at 1800 m in the Khomas Highland, Namibia."
  * source/quote: https://hess-experiment.eu/ (WebFetch 2026-10-25): site shows 'Due to precautionary security measures, we are taking down this web site/service temporarily.' Internet Archive captures of hess-experiment.eu (about-hess 2026-05-01, telescopes April 2026, h-e-s-s-site 2026-07-29), text read 2026-10-25: telescopes page says only 'CT1-4 ... installed between 2001 and 2003' and that CT5 has a 28-meter mirror; the CT5 camera was replaced in October 2019 (FlashCam); no CT5 commissioning year. https://www.mpg.de/6373837/a-glimpse-into-turbulent-space (WebFetch 2026-10-25; article date October 04, 2012): 'The telescope has an antenna diameter of 28 metres and saw its first light on 26 July.'
  * source/quote: Internet Archive captures of hess-experiment.eu: about-hess (2026-05-01), telescopes (April 2026), h-e-s-s-site (2026-07-29); text read 2026-10-25 contains no CT5 commissioning year (CT1-4 'installed between 2001 and 2003'; CT5 camera replaced October 2019). Live hess-experiment.eu on 2026-10-25: 'Due to precautionary security measures, we are taking down this web site/service temporarily.'

## data/atlas/collaborations/h-e-s-s.json

* `/formation/note` -- dated wording
  * old: "No source fetched this session states a formal formation date distinct from the 2002 first-light date; the collaboration presumably formed earlier, during proposal/construction, but that is not sourced."
  * new: "No source consulted (checked 2026-10-25) states a formal formation date distinct from the 2002 first-light date; the collaboration presumably formed earlier, during proposal/construction, but that is not sourced."
  * source/quote: https://hess-experiment.eu/ (WebFetch 2026-10-25): site shows 'Due to precautionary security measures, we are taking down this web site/service temporarily.' Internet Archive captures of hess-experiment.eu (about-hess 2026-05-01, telescopes April 2026, h-e-s-s-site 2026-07-29), text read 2026-10-25: telescopes page says only 'CT1-4 ... installed between 2001 and 2003' and that CT5 has a 28-meter mirror; the CT5 camera was replaced in October 2019 (FlashCam); no CT5 commissioning year. https://www.mpg.de/6373837/a-glimpse-into-turbulent-space (WebFetch 2026-10-25; article date October 04, 2012): 'The telescope has an antenna diameter of 28 metres and saw its first light on 26 July.'
* `/notes/0` -- process wording removed, substance kept
  * old: "experiment_ids, document_ids deliberately not written (v0.2 A1 derived fields)."
  * new: "The experiment and document lists are derived from the other records and are not stored here."
* `/notes/2` -- process wording removed, substance kept
  * old: "Leadership left empty: person records are out of scope this wave and none was sourced."
  * new: "Leadership is not recorded in this record."

## data/atlas/experiments/nexo.json

* `/facility_roles/0/note` -- process wording removed, substance kept
  * old: "facility:snolab is owned by the 'facilities' Wave 3 lead and does not exist yet in this repository (dangling reference)."
  * new: "SNOLAB is the planned site, not yet an installed one: the nEXO site says the experiment 'will be built in SNOLAB' (future tense), and no source consulted (checked 2026-10-25) says the detector has been installed there."
  * source/quote: https://nexo.llnl.gov/nexo-overview (WebFetch 2026-10-25): 'will be built in SNOLAB, a deep mine'; https://nexo.llnl.gov/ (WebFetch 2026-10-25) image caption: 'nEXO will be located two kilometers underground in the SNOLAB Cryopit'. Note re-worded (not left empty) because confidence 'uncertain' requires a note.
* `/intervals/0/note` -- dated wording
  * old: "No fetched source gives a start date for this phase or confirms the detector itself is physically under construction; the collaboration describes itself as contributing to 'design and construction' of the eventual detector, but a secondary (non-fetched-with-quote) summary describes an anticipated construction start around 2026 and commissioning around 2032-2033, which this agent did not verify against a directly fetched primary source, so it is not recorded as a dated interval. Status is recorded as `proposed` rather than `construction` pending a clearer sourced statement. `start` (2018) is the date of the earliest dated nEXO design document found (the Pre-Conceptual Design Report), a lower bound on the design/preparation phase, not a true construction-start date."
  * new: "No source consulted (checked 2026-10-25) gives a start date for this phase or confirms that the detector itself is physically under construction; the collaboration describes itself as contributing to 'design and construction' of the eventual detector. A secondary summary describes an anticipated construction start around 2026 and commissioning around 2032-2033; that was not found in any primary source consulted, so it is not recorded as a dated interval. Status is recorded as `proposed` rather than `construction` pending a clearer sourced statement. `start` (2018) is the date of the earliest dated nEXO design document found (the Pre-Conceptual Design Report), a lower bound on the design and preparation phase, not a true construction-start date."
  * source/quote: https://nexo.llnl.gov/ (WebFetch 2026-10-25): 'The nEXO experiment is under development.'; news items all dated Dec. 21, 2021; no 'nEXO 2.0', no construction start. https://nexo.llnl.gov/nexo-overview (WebFetch 2026-10-25): 'will be built in SNOLAB, a deep mine'; 'A consortium of over 150 scientists and technologists from 31 institutions and eight countries ... contributing to the design and construction of nEXO'; future tense throughout; no calendar dates for construction.
* `/intervals/1/note` -- dated wording / process wording removed, substance kept
  * old: "Added 2026-10-25 as an annotation (kind phase; status stays `proposed`). SNOLAB Report, slides dated 26 May 2026, slide 26 'SNOLAB Cryopit Timeline' (read from the rendered slide): the first entry, dated 'Dec 2024', says \"US led nEXO project was paused.\"; the next entries are XLZD approved as a conceptual design study at SNOLAB (August 2025) and Canadian scientists joining the XLZD collaboration (March 2026). The nEXO website (nexo.llnl.gov, undated) still says \"The nEXO experiment is under development\", and SNOLAB's 31 July 2026 talk lists 'nEXO 2.0' among illustrative future-project ideas that 'does not indicate SNOLAB approval or space allocation'. No source says the project was cancelled, so it is not recorded as `cancelled`. The date is the one printed on the SNOLAB slide; the pause's own announcement was not found."
  * new: "Recorded as an annotation (kind phase) with status `proposed`. SNOLAB Report, slides dated 26 May 2026, slide 26 'SNOLAB Cryopit Timeline': the first entry, dated 'Dec 2024', says \"US led nEXO project was paused.\"; the next entries are XLZD approved as a conceptual design study at SNOLAB (August 2025) and Canadian scientists joining the XLZD collaboration (March 2026). The nEXO website (nexo.llnl.gov, undated; read again 2026-10-25) still says \"The nEXO experiment is under development\", and SNOLAB's 31 July 2026 talk lists 'nEXO 2.0' among illustrative future-project ideas that 'does not indicate SNOLAB approval or space allocation'. No source says the project was cancelled, so it is not recorded as `cancelled`. The date is the one printed on the SNOLAB slide; no source consulted gives the pause's own announcement."
  * source/quote: https://nexo.llnl.gov/ (WebFetch 2026-10-25): 'The nEXO experiment is under development.'; news items all dated Dec. 21, 2021; no 'nEXO 2.0', no construction start. https://nexo.llnl.gov/nexo-overview (WebFetch 2026-10-25): 'will be built in SNOLAB, a deep mine'; 'A consortium of over 150 scientists and technologists from 31 institutions and eight countries ... contributing to the design and construction of nEXO'; future tense throughout; no calendar dates for construction.
* `/notes/0` -- process wording removed, substance kept
  * old: "Planned for SNOLAB: this record references facility:snolab and site:snolab-underground-lab, both owned by the 'facilities' Wave 3 lead, neither of which exists yet in this repository as of 2026-09-17 (dangling references, ID_REGISTRY row 49)."
  * new: "Planned for the SNOLAB underground laboratory (facility:snolab, site:snolab-underground-lab)."
* `/notes/1` -- dated wording
  * old: "Status is recorded as 'proposed': no source fetched in this session confirms physical construction has begun. A secondary web summary described a phased 'nEXO 2.0' plan (construction start ~2026, commissioning ~2032-2033) that this agent could not verify against a directly fetched primary source in this session; it is reported here for the domain lead's awareness but not encoded as a sourced value."
  * new: "Status is recorded as 'proposed': no source consulted (checked 2026-10-25) confirms that physical construction has begun, and the nEXO site (nexo.llnl.gov, undated) says 'The nEXO experiment is under development.' A secondary web summary described a phased 'nEXO 2.0' plan (construction start ~2026, commissioning ~2032-2033); it was not found in any primary source consulted and is not recorded as a sourced value."
  * source/quote: https://nexo.llnl.gov/ (WebFetch 2026-10-25): 'The nEXO experiment is under development.'; news items all dated Dec. 21, 2021; no 'nEXO 2.0', no construction start. https://nexo.llnl.gov/nexo-overview (WebFetch 2026-10-25): 'will be built in SNOLAB, a deep mine'; 'A consortium of over 150 scientists and technologists from 31 institutions and eight countries ... contributing to the design and construction of nEXO'; future tense throughout; no calendar dates for construction.
* `/notes/2` -- process wording removed, substance kept
  * old: "No INSPIRE experiment-registry lookup was performed in this session; external.inspire_experiment is left null with this note rather than guessed."
  * new: "No INSPIRE experiment-registry identifier is recorded for nEXO (external.inspire_experiment is empty)."
* `/notes/3` -- dated wording
  * old: "Collaboration formation date not sourced in this session."
  * new: "No source consulted (checked 2026-10-25) gives the collaboration's formation date."
  * source/quote: https://nexo.llnl.gov/ (WebFetch 2026-10-25): 'The nEXO experiment is under development.'; news items all dated Dec. 21, 2021; no 'nEXO 2.0', no construction start. https://nexo.llnl.gov/nexo-overview (WebFetch 2026-10-25): 'will be built in SNOLAB, a deep mine'; 'A consortium of over 150 scientists and technologists from 31 institutions and eight countries ... contributing to the design and construction of nEXO'; future tense throughout; no calendar dates for construction.
* `/summary/technical` -- dated wording
  * old: "...al consortium of >150 scientists from 31 institutions in 8 countries; no confirmed construction start date in sources fetched in this session."
  * new: "...al consortium of >150 scientists from 31 institutions in 8 countries; as of 2026-10-25 the nEXO site (undated) still describes the experiment as under development, and no source consulted gives a construction start date."
  * source/quote: https://nexo.llnl.gov/ (WebFetch 2026-10-25): 'The nEXO experiment is under development.'; news items all dated Dec. 21, 2021; no 'nEXO 2.0', no construction start. https://nexo.llnl.gov/nexo-overview (WebFetch 2026-10-25): 'will be built in SNOLAB, a deep mine'; 'A consortium of over 150 scientists and technologists from 31 institutions and eight countries ... contributing to the design and construction of nEXO'; future tense throughout; no calendar dates for construction.

## data/atlas/detectors/nexo.json

* `/intervals/0/note` -- dated wording
  * old: "See experiment:nexo interval note; no confirmed physical-construction start date sourced in this session. `start` (2018) is the date of the earliest dated nEXO design document found (the Pre-Conceptual Design Report), a lower bound not a true start date."
  * new: "See the experiment:nexo interval note. No source consulted (checked 2026-10-25) gives a physical-construction start date. `start` (2018) is the date of the earliest dated nEXO design document found (the Pre-Conceptual Design Report), a lower bound and not a true start date."
  * source/quote: https://nexo.llnl.gov/ (WebFetch 2026-10-25): 'The nEXO experiment is under development.'; news items all dated Dec. 21, 2021; no 'nEXO 2.0', no construction start. https://nexo.llnl.gov/nexo-overview (WebFetch 2026-10-25): 'will be built in SNOLAB, a deep mine'; 'A consortium of over 150 scientists and technologists from 31 institutions and eight countries ... contributing to the design and construction of nEXO'; future tense throughout; no calendar dates for construction.
* `/intervals/1/note` -- dated wording / process wording removed, substance kept
  * old: "Added 2026-10-25 as an annotation (kind phase; status stays `proposed`). SNOLAB Report, slides dated 26 May 2026, slide 26 'SNOLAB Cryopit Timeline' (read from the rendered slide): the first entry, dated 'Dec 2024', says \"US led nEXO project was paused.\"; the next entries are XLZD approved as a conceptual design study at SNOLAB (August 2025) and Canadian scientists joining the XLZD collaboration (March 2026). The nEXO website (nexo.llnl.gov, undated) still says \"The nEXO experiment is under development\", and SNOLAB's 31 July 2026 talk lists 'nEXO 2.0' among illustrative future-project ideas that 'does not indicate SNOLAB approval or space allocation'. No source says the project was cancelled, so it is not recorded as `cancelled`. The date is the one printed on the SNOLAB slide; the pause's own announcement was not found."
  * new: "Recorded as an annotation (kind phase) with status `proposed`. SNOLAB Report, slides dated 26 May 2026, slide 26 'SNOLAB Cryopit Timeline': the first entry, dated 'Dec 2024', says \"US led nEXO project was paused.\"; the next entries are XLZD approved as a conceptual design study at SNOLAB (August 2025) and Canadian scientists joining the XLZD collaboration (March 2026). The nEXO website (nexo.llnl.gov, undated; read again 2026-10-25) still says \"The nEXO experiment is under development\", and SNOLAB's 31 July 2026 talk lists 'nEXO 2.0' among illustrative future-project ideas that 'does not indicate SNOLAB approval or space allocation'. No source says the project was cancelled, so it is not recorded as `cancelled`. The date is the one printed on the SNOLAB slide; no source consulted gives the pause's own announcement."
  * source/quote: https://nexo.llnl.gov/ (WebFetch 2026-10-25): 'The nEXO experiment is under development.'; news items all dated Dec. 21, 2021; no 'nEXO 2.0', no construction start. https://nexo.llnl.gov/nexo-overview (WebFetch 2026-10-25): 'will be built in SNOLAB, a deep mine'; 'A consortium of over 150 scientists and technologists from 31 institutions and eight countries ... contributing to the design and construction of nEXO'; future tense throughout; no calendar dates for construction.
* `/notes/0` -- process wording removed, substance kept
  * old: "Placed at site:snolab-underground-lab (dangling reference: owned by the 'facilities' lead, not yet created)."
  * new: "Placed at site:snolab-underground-lab, the SNOLAB underground laboratory."
* `/placements/0/note` -- process wording removed, substance kept
  * old: "site:snolab-underground-lab is owned by the 'facilities' Wave 3 lead and does not exist yet in this repository (dangling reference)."
  * new: "SNOLAB is the planned location: the nEXO site describes the detector in the future tense ('will be built in SNOLAB', 'will be located two kilometers underground in the SNOLAB Cryopit'); no source consulted (checked 2026-10-25) says it has been installed there."
  * source/quote: https://nexo.llnl.gov/nexo-overview (WebFetch 2026-10-25): 'will be built in SNOLAB, a deep mine'; https://nexo.llnl.gov/ (WebFetch 2026-10-25) image caption: 'nEXO will be located two kilometers underground in the SNOLAB Cryopit'. Note re-worded (not left empty) because confidence 'uncertain' requires a note.

## data/atlas/collaborations/nexo.json

* `/formation/locator` -- process wording removed, substance kept
  * old: "no fetched source states an explicit nEXO collaboration formation date"
  * new: "no source consulted states an explicit nEXO collaboration formation date"
* `/formation/note` -- dated wording
  * old: "No source fetched in this session states an explicit formation date; left null (v0.2 A17)."
  * new: "No source consulted (checked 2026-10-25) states an explicit formation date; left empty."
  * source/quote: https://nexo.llnl.gov/ (WebFetch 2026-10-25): 'The nEXO experiment is under development.'; news items all dated Dec. 21, 2021; no 'nEXO 2.0', no construction start. https://nexo.llnl.gov/nexo-overview (WebFetch 2026-10-25): 'will be built in SNOLAB, a deep mine'; 'A consortium of over 150 scientists and technologists from 31 institutions and eight countries ... contributing to the design and construction of nEXO'; future tense throughout; no calendar dates for construction.
* `/intervals/0/note` -- process wording removed, substance kept
  * old: "No fetched source states a formation date; status mirrors the pre-construction status of experiment:nexo. `start` (2018) is the earliest dated nEXO design document found, a lower bound not a true formation date."
  * new: "No source consulted states a formation date; status mirrors the pre-construction status of experiment:nexo. `start` (2018) is the earliest dated nEXO design document found, a lower bound not a true formation date."
* `/notes/0` -- STALE: statement contradicted by the cited source; corrected
  * old: "This record has no `intervals`: no fetched source states a formation date for this pre-construction collaboration."
  * new: "The collaboration interval starts in 2018, the earliest dated nEXO design document, as a lower bound; no source consulted (checked 2026-10-25) states a formation date for this pre-construction collaboration."
  * source/quote: https://nexo.llnl.gov/ (WebFetch 2026-10-25): 'The nEXO experiment is under development.'; news items all dated Dec. 21, 2021; no 'nEXO 2.0', no construction start. https://nexo.llnl.gov/nexo-overview (WebFetch 2026-10-25): 'will be built in SNOLAB, a deep mine'; 'A consortium of over 150 scientists and technologists from 31 institutions and eight countries ... contributing to the design and construction of nEXO'; future tense throughout; no calendar dates for construction.
* `/notes/1` -- process wording removed, substance kept
  * old: "Institution-level membership rows and person records are owned by the membership-lead workstream and are not written here."
  * new: "Institution-level membership rows and person records are not recorded here."
* `/notes/2` -- process wording removed, substance kept
  * old: "Derived field collaboration.experiment_ids is deliberately not written (v0.2 A1)."
  * new: "The experiment list is derived from the experiment records and is not stored here."

## data/atlas/experiments/sensei.json

* `/facility_roles/0/note` -- STALE: statement contradicted by the cited source; corrected
  * old: "A 2026-05 SENSEI paper still places the detector 'near the MINOS cavern' at Fermilab; a 2020 SENSEI paper described a ~100-gram detector 'planned' for SNOLAB, but no source fetched this session confirms that move has happened, so no SNOLAB facility_role/placement is recorded."
  * new: "A May 2026 SENSEI paper (arXiv:2605.30281) still places the detector 'near the MINOS cavern' at Fermilab. A SENSEI apparatus also operated at SNOLAB (installed 2021; first science run 2022-09-09 to 2023-04-10, arXiv:2312.13342; see the SNOLAB rows in the interval list), but no SNOLAB facility role or detector placement is recorded in this record."
  * source/quote: arXiv:2312.13342 (abstract page WebFetch 2026-10-25; submitted 20 Dec 2023, v2 23 Jan 2025; full text read 2026-10-25): 'six Skipper-CCDs in the SENSEI detector operating at SNOLAB'; 'for an active mass of 2.19 g' per CCD; 'The SENSEI apparatus at SNOLAB was installed in 2021.'; 'data taken from September 9, 2022 to April 10, 2023'; 'The SNOLAB setup has been upgraded with additional detectors for another science run.' arXiv:2605.30281 (WebFetch 2026-10-25; submitted 28 May 2026): 'Using the SENSEI detector near the MINOS cavern'. arXiv:2610.22418 (WebFetch 2026-10-25; submitted 15 Oct 2026): 'a SENSEI sensor placed underground in the MINOS cavern at Fermilab'.
* `/intervals/0/note` -- process wording removed, substance kept
  * old: "Year-precision date from the INSPIRE experiment registry (rank 3); no independently fetched proposal document."
  * new: "Year-precision date from the INSPIRE experiment registry (rank 3); no proposal document was consulted independently."
* `/intervals/1/note` -- process wording removed, substance kept
  * old: "End set to the paper's submission date (2019-01-29); the run itself may have started earlier in 2018, not independently pinned down by a fetched source."
  * new: "End set to the paper's submission date (2019-01-29); the run itself may have started earlier in 2018, which no source consulted pins down independently."
* `/intervals/3/note` -- process wording removed, substance kept
  * old: "Added 2026-10-25. The first-pass record had no SNOLAB history (its note says no explicit SNOLAB-operations source had been found). arXiv:2312.13342 gives the SNOLAB installation year; a SNOLAB placement for the detector is not added here (see the log: it needs a site placement and a map 'unlocated' entry, and maps/ was out of scope)."
  * new: "arXiv:2312.13342 gives the year the SENSEI apparatus was installed at SNOLAB. The SNOLAB installation is recorded here as a timeline entry only; no SNOLAB detector placement is recorded."
  * source/quote: arXiv:2312.13342 (abstract page WebFetch 2026-10-25; submitted 20 Dec 2023, v2 23 Jan 2025; full text read 2026-10-25): 'six Skipper-CCDs in the SENSEI detector operating at SNOLAB'; 'for an active mass of 2.19 g' per CCD; 'The SENSEI apparatus at SNOLAB was installed in 2021.'; 'data taken from September 9, 2022 to April 10, 2023'; 'The SNOLAB setup has been upgraded with additional detectors for another science run.' arXiv:2605.30281 (WebFetch 2026-10-25; submitted 28 May 2026): 'Using the SENSEI detector near the MINOS cavern'. arXiv:2610.22418 (WebFetch 2026-10-25; submitted 15 Oct 2026): 'a SENSEI sensor placed underground in the MINOS cavern at Fermilab'.
* `/intervals/4/note` -- dated wording
  * old: "Added 2026-10-25. First SNOLAB science run (arXiv:2312.13342). The same paper says \"The SNOLAB setup has been upgraded with additional detectors for another science run\"; no source fetched dates that later run or says whether it is taking data now. The Fermilab MINOS-cavern operation (next row, open) is still reported as ongoing in an arXiv paper of 15 October 2026 (a..."
  * new: "First SNOLAB science run (arXiv:2312.13342). The same paper says \"The SNOLAB setup has been upgraded with additional detectors for another science run\"; no source consulted (checked 2026-10-25) dates that later run or says whether it is taking data now. The Fermilab MINOS-cavern operation (the open Fermilab interval above) is still reported as ongoing in an arXiv paper of 15 October 2026 (a..."
  * source/quote: arXiv:2312.13342 (abstract page WebFetch 2026-10-25; submitted 20 Dec 2023, v2 23 Jan 2025; full text read 2026-10-25): 'six Skipper-CCDs in the SENSEI detector operating at SNOLAB'; 'for an active mass of 2.19 g' per CCD; 'The SENSEI apparatus at SNOLAB was installed in 2021.'; 'data taken from September 9, 2022 to April 10, 2023'; 'The SNOLAB setup has been upgraded with additional detectors for another science run.' arXiv:2605.30281 (WebFetch 2026-10-25; submitted 28 May 2026): 'Using the SENSEI detector near the MINOS cavern'. arXiv:2610.22418 (WebFetch 2026-10-25; submitted 15 Oct 2026): 'a SENSEI sensor placed underground in the MINOS cavern at Fermilab'.
* `/notes/0` -- dated wording
  * old: "No live official SENSEI website was found: the INSPIRE record's listed homepage (http://home.fnal.gov/~javiert/sensei) returned HTTP 403 when fetched 2026-09-17. links.website is left null rather than guessed."
  * new: "No live official SENSEI website was found: the INSPIRE record's listed homepage (http://home.fnal.gov/~javiert/sensei) returned HTTP 403 when requested on 2026-09-17 and again on 2026-10-25. links.website is left empty rather than guessed."
  * source/quote: WebFetch 2026-10-25 http://home.fnal.gov/~javiert/sensei -> HTTP 403 Forbidden
* `/notes/1` -- STALE: statement contradicted by the cited source; corrected
  * old: "A ~100-gram SENSEI detector at SNOLAB is described as 'planned' in a 2020 SENSEI paper, but the most recent SENSEI paper found this session (2026-05) still describes the operating detector as being 'near the MINOS cavern' at Fermilab, so no SNOLAB placement is recorded. This should be revisited if a more recent, explicit SNOLAB-operations source is found."
  * new: "A ~100-gram SENSEI detector at SNOLAB was described as 'planned' in a 2020 SENSEI paper. The December 2023 SNOLAB paper (arXiv:2312.13342) reports a SENSEI detector there with six Skipper-CCDs of 2.19 g active mass each, installed in 2021 and run from 9 September 2022 to 10 April 2023; it does not report a ~100 g detector. The most recent SENSEI paper consulted (arXiv:2605.30281, May 2026) still places the operating detector 'near the MINOS cavern' at Fermilab, so no SNOLAB placement is recorded. A more recent, explicit SNOLAB-operations source would settle the SNOLAB status."
  * source/quote: arXiv:2312.13342 (abstract page WebFetch 2026-10-25; submitted 20 Dec 2023, v2 23 Jan 2025; full text read 2026-10-25): 'six Skipper-CCDs in the SENSEI detector operating at SNOLAB'; 'for an active mass of 2.19 g' per CCD; 'The SENSEI apparatus at SNOLAB was installed in 2021.'; 'data taken from September 9, 2022 to April 10, 2023'; 'The SNOLAB setup has been upgraded with additional detectors for another science run.' arXiv:2605.30281 (WebFetch 2026-10-25; submitted 28 May 2026): 'Using the SENSEI detector near the MINOS cavern'. arXiv:2610.22418 (WebFetch 2026-10-25; submitted 15 Oct 2026): 'a SENSEI sensor placed underground in the MINOS cavern at Fermilab'.
* `/notes/2` -- dated wording
  * old: "site:fermilab-minos-near-detector-hall was not created: the existing site:fermilab-main-campus (owned by fermilab-dune) is already used as the campus-precision placement point for the MINOS near detector hall specifically (see its notes), and no source fetched this session gives a more precise, distinct coordinate for the hall. Reusing the existing site avoids a near-duplicate site with the same fabricated-precision coordinate."
  * new: "The detector is placed at the existing campus-level site (site:fermilab-main-campus), which is also used for the MINOS near detector hall (see that site's notes); no source consulted (checked 2026-10-25) gives a more precise coordinate for the hall, so no separate hall site exists."
  * source/quote: site record data/atlas/sites/fermilab-main-campus.json notes: 'campus precision', used for several Fermilab near detectors including the MINOS near detector
* `/summary/technical` -- STALE: statement contradicted by the cited source; corrected
  * old: "...ved ~2 g Skipper-CCD (2020 results), with operations continuing as of a 2026 backgrounds-characterization paper. A ~100 g detector at SNOLAB was described as planned in 2020 but not confirmed as realized by any source fetched this session."
  * new: "...ved ~2 g Skipper-CCD (2020 results), with operations continuing as of the May 2026 spurious-charge paper (arXiv:2605.30281). A ~100 g detector at SNOLAB was described as planned in 2020; the December 2023 paper (arXiv:2312.13342) reports a six-Skipper-CCD detector installed there in 2021 (2.19 g active mass per CCD), with a first science run from September 2022 to April 2023."
  * source/quote: arXiv:2312.13342 (abstract page WebFetch 2026-10-25; submitted 20 Dec 2023, v2 23 Jan 2025; full text read 2026-10-25): 'six Skipper-CCDs in the SENSEI detector operating at SNOLAB'; 'for an active mass of 2.19 g' per CCD; 'The SENSEI apparatus at SNOLAB was installed in 2021.'; 'data taken from September 9, 2022 to April 10, 2023'; 'The SNOLAB setup has been upgraded with additional detectors for another science run.' arXiv:2605.30281 (WebFetch 2026-10-25; submitted 28 May 2026): 'Using the SENSEI detector near the MINOS cavern'. arXiv:2610.22418 (WebFetch 2026-10-25; submitted 15 Oct 2026): 'a SENSEI sensor placed underground in the MINOS cavern at Fermilab'.

## data/atlas/detectors/sensei.json

* `/intervals/2/note` -- process wording removed, substance kept
  * old: "Added 2026-10-25. The first-pass record had no SNOLAB history (its note says no explicit SNOLAB-operations source had been found). arXiv:2312.13342 gives the SNOLAB installation year; a SNOLAB placement for the detector is not added here (see the log: it needs a site placement and a map 'unlocated' entry, and maps/ was out of scope)."
  * new: "arXiv:2312.13342 gives the year the SENSEI apparatus was installed at SNOLAB. The SNOLAB installation is recorded here as a timeline entry only; no SNOLAB detector placement is recorded."
  * source/quote: arXiv:2312.13342 (abstract page WebFetch 2026-10-25; submitted 20 Dec 2023, v2 23 Jan 2025; full text read 2026-10-25): 'six Skipper-CCDs in the SENSEI detector operating at SNOLAB'; 'for an active mass of 2.19 g' per CCD; 'The SENSEI apparatus at SNOLAB was installed in 2021.'; 'data taken from September 9, 2022 to April 10, 2023'; 'The SNOLAB setup has been upgraded with additional detectors for another science run.' arXiv:2605.30281 (WebFetch 2026-10-25; submitted 28 May 2026): 'Using the SENSEI detector near the MINOS cavern'. arXiv:2610.22418 (WebFetch 2026-10-25; submitted 15 Oct 2026): 'a SENSEI sensor placed underground in the MINOS cavern at Fermilab'.
* `/intervals/3/note` -- dated wording
  * old: "Added 2026-10-25. First SNOLAB science run (arXiv:2312.13342). The same paper says \"The SNOLAB setup has been upgraded with additional detectors for another science run\"; no source fetched dates that later run or says whether it is taking data now. The Fermilab MINOS-cavern operation (next row, open) is still reported as ongoing in an arXiv paper of 15 October 2026 (a..."
  * new: "First SNOLAB science run (arXiv:2312.13342). The same paper says \"The SNOLAB setup has been upgraded with additional detectors for another science run\"; no source consulted (checked 2026-10-25) dates that later run or says whether it is taking data now. The Fermilab MINOS-cavern operation (the open Fermilab interval above) is still reported as ongoing in an arXiv paper of 15 October 2026 (a..."
  * source/quote: arXiv:2312.13342 (abstract page WebFetch 2026-10-25; submitted 20 Dec 2023, v2 23 Jan 2025; full text read 2026-10-25): 'six Skipper-CCDs in the SENSEI detector operating at SNOLAB'; 'for an active mass of 2.19 g' per CCD; 'The SENSEI apparatus at SNOLAB was installed in 2021.'; 'data taken from September 9, 2022 to April 10, 2023'; 'The SNOLAB setup has been upgraded with additional detectors for another science run.' arXiv:2605.30281 (WebFetch 2026-10-25; submitted 28 May 2026): 'Using the SENSEI detector near the MINOS cavern'. arXiv:2610.22418 (WebFetch 2026-10-25; submitted 15 Oct 2026): 'a SENSEI sensor placed underground in the MINOS cavern at Fermilab'.
* `/notes/0` -- dated wording
  * old: "The device changed generations over the experiment's history (0.0947 g protoSENSEI in 2019 to a ~2 g Skipper-CCD from 2020); no single 'current' mass/pixel count as of 2026 was found in the sources fetched."
  * new: "The device changed generations over the experiment's history (0.0947 g protoSENSEI in 2019 to a ~2 g Skipper-CCD from 2020); none of the sources consulted (checked 2026-10-25) gives a single 'current' mass or pixel count for 2026."
  * source/quote: arXiv:2312.13342 (abstract page WebFetch 2026-10-25; submitted 20 Dec 2023, v2 23 Jan 2025; full text read 2026-10-25): 'six Skipper-CCDs in the SENSEI detector operating at SNOLAB'; 'for an active mass of 2.19 g' per CCD; 'The SENSEI apparatus at SNOLAB was installed in 2021.'; 'data taken from September 9, 2022 to April 10, 2023'; 'The SNOLAB setup has been upgraded with additional detectors for another science run.' arXiv:2605.30281 (WebFetch 2026-10-25; submitted 28 May 2026): 'Using the SENSEI detector near the MINOS cavern'. arXiv:2610.22418 (WebFetch 2026-10-25; submitted 15 Oct 2026): 'a SENSEI sensor placed underground in the MINOS cavern at Fermilab'.
* `/placements/0/note` -- dated wording
  * old: "Placed at the existing site:fermilab-main-campus (owned by fermilab-dune), which that lead's own notes already use as the campus-precision placement for the Fermilab MINOS near-detector hall (kind: detector, precision_m 3000); no source fetched this session gives a more precise coordinate for this specific cavern."
  * new: "Placed at the existing campus-level site site:fermilab-main-campus, which is also used for the Fermilab MINOS near-detector hall (kind detector, precision 3000 m); no source consulted (checked 2026-10-25) gives a more precise coordinate for this specific cavern."
  * source/quote: site record data/atlas/sites/fermilab-main-campus.json
* `/specs/active_mass/note` -- dated wording
  * old: "This is the protoSENSEI (2019) device's mass; the 2020 device was ~2 g (see notes). No mass figure for the current (2026) detector was found in the papers fetched this session."
  * new: "This is the protoSENSEI (2019) device's mass; the 2020 device was ~2 g (see notes). No mass figure for the current (2026) Fermilab detector is given in the papers consulted (checked 2026-10-25)."
  * source/quote: arXiv:2312.13342 (abstract page WebFetch 2026-10-25; submitted 20 Dec 2023, v2 23 Jan 2025; full text read 2026-10-25): 'six Skipper-CCDs in the SENSEI detector operating at SNOLAB'; 'for an active mass of 2.19 g' per CCD; 'The SENSEI apparatus at SNOLAB was installed in 2021.'; 'data taken from September 9, 2022 to April 10, 2023'; 'The SNOLAB setup has been upgraded with additional detectors for another science run.' arXiv:2605.30281 (WebFetch 2026-10-25; submitted 28 May 2026): 'Using the SENSEI detector near the MINOS cavern'. arXiv:2610.22418 (WebFetch 2026-10-25; submitted 15 Oct 2026): 'a SENSEI sensor placed underground in the MINOS cavern at Fermilab'.
* `/summary/technical` -- dated wording
  * old: "Skipper-CCD detector operated in the MINOS cavern at Fermilab; protoSENSEI (2018-2019) had 0.0947 g active mass across ~904,000 pixels in four amplifier quadrants, superseded by a ~2 g high-resistivity Skipper-CCD from 2020, with operations continuing as of 2026."
  * new: "Skipper-CCD detector operated in the MINOS cavern at Fermilab; protoSENSEI (2018-2019) had 0.0947 g active mass across ~904,000 pixels in four amplifier quadrants, superseded by a ~2 g high-resistivity Skipper-CCD from 2020, with operations continuing as of the May 2026 spurious-charge paper (arXiv:2605.30281)."
  * source/quote: arXiv:2312.13342 (abstract page WebFetch 2026-10-25; submitted 20 Dec 2023, v2 23 Jan 2025; full text read 2026-10-25): 'six Skipper-CCDs in the SENSEI detector operating at SNOLAB'; 'for an active mass of 2.19 g' per CCD; 'The SENSEI apparatus at SNOLAB was installed in 2021.'; 'data taken from September 9, 2022 to April 10, 2023'; 'The SNOLAB setup has been upgraded with additional detectors for another science run.' arXiv:2605.30281 (WebFetch 2026-10-25; submitted 28 May 2026): 'Using the SENSEI detector near the MINOS cavern'. arXiv:2610.22418 (WebFetch 2026-10-25; submitted 15 Oct 2026): 'a SENSEI sensor placed underground in the MINOS cavern at Fermilab'.

## data/atlas/collaborations/sensei.json

* `/notes/0` -- dated wording
  * old: "No institution/member counts found in any source fetched this session."
  * new: "No source consulted (checked 2026-10-25) gives institution or member counts."
  * source/quote: arXiv:2312.13342 (abstract page WebFetch 2026-10-25; submitted 20 Dec 2023, v2 23 Jan 2025; full text read 2026-10-25): 'six Skipper-CCDs in the SENSEI detector operating at SNOLAB'; 'for an active mass of 2.19 g' per CCD; 'The SENSEI apparatus at SNOLAB was installed in 2021.'; 'data taken from September 9, 2022 to April 10, 2023'; 'The SNOLAB setup has been upgraded with additional detectors for another science run.' arXiv:2605.30281 (WebFetch 2026-10-25; submitted 28 May 2026): 'Using the SENSEI detector near the MINOS cavern'. arXiv:2610.22418 (WebFetch 2026-10-25; submitted 15 Oct 2026): 'a SENSEI sensor placed underground in the MINOS cavern at Fermilab'.

## data/atlas/experiments/deap-3600.json

* `/facility_roles/0/note` -- process wording removed, substance kept
  * old: "facility:snolab is owned by the 'facilities' workstream and had not been created in this session; this is a dangling reference, expected per the ID registry and Wave 3 brief."
  * new: ""
* `/intervals/0/note` -- process wording removed, substance kept
  * old: "...planned spring/April 2015 switch-on (a schedule, not a confirmed event: planned per A4). The detector paper documents that the first fill instead began arou..."
  * new: "...planned spring/April 2015 switch-on (a schedule, not a confirmed event, hence marked planned). The detector paper documents that the first fill instead began arou..."
* `/intervals/1/note` -- process wording removed, substance kept
  * old: "END SET 2026-10-25. Previously open-ended with the note that no source said data taking had stopped; the collaboration states the second-fill data set ran from Nov 2016 to March 2020 and that upgrades have been ongoing \"since the end of the second fill run in 2020\"."
  * new: "The collaboration states that the second-fill data set ran from November 2016 to March 2020 (PASCOS 2025 slides) and that upgrades have been ongoing \"since the end of the second fill run in 2020\"."
* `/intervals/2/note` -- dated wording
  * old: "SNOLAB's own experiment page (accessed 2026-09-17) states the current status as 'Upgrading'. No source fetched this session gives the true start date of this phase; start is set to 2026-09, the month this status was confirmed, as the earliest date this interval can be anchored to without inventing one -- it is not a claim that the upgrade began that month. Secondary reporting (a 2025 SNOLAB workshop community report, arXiv:2507.11368) associates recent work with a planned 'third fill', but that document's body text could not be retrieved and quoted in this session, so no date from it is recorded. arXiv:2603.27372 (submitted 28 Mar 2026) corroborates ongoing 'hardware upgrades to mitigate residual challenging alpha-backgrounds for WIMP search'. RE-READ 2026-10-25: demoted to a phase annotation. The collaboration's abstracts of 22 June and 21 September 2026 describe a \"just-started\" / \"newly initiated third fill run\" with preliminary third-fill results, which conflicts with reading SNOLAB's \"Upgrading\" status label as a current absence of data taking. The SNOLAB page could not be re-opened. A 2025 plan said third-fill data taking would end \"~ summer 2026\" with decommissioning to make room for ARGOlite; no fetched source says whether that happened."
  * new: "SNOLAB's experiment page (read 2026-09-17; an Internet Archive capture of 25 May 2026 shows the same status) gives the status 'Upgrading'. No source consulted (checked 2026-10-25) gives the true start date of this phase; the start is set to 2026-09, the month this status was first read, as the earliest date the interval can be anchored to without inventing one -- it is not a claim that the upgrade began that month. A 2025 SNOLAB workshop community report (arXiv:2507.11368) is secondary reporting that associates recent work with a planned 'third fill'; its body text could not be retrieved and quoted, so no date from it is recorded. arXiv:2603.27372 (submitted 28 Mar 2026) corroborates ongoing 'hardware upgrades to mitigate residual challenging alpha-backgrounds for WIMP search'. The collaboration's abstracts of 22 June and 21 September 2026 describe a \"just-started\" / \"newly initiated third fill run\" with preliminary third-fill results, which conflicts with reading SNOLAB's \"Upgrading\" label as a current absence of data taking; this interval is therefore a phase annotation and not the detector's current state. The SNOLAB page no longer loads (HTTP 404 on 2026-10-25). A 2025 plan said third-fill data taking would end \"~ summer 2026\" with decommissioning to make room for ARGOlite; no source consulted says whether that happened."
  * source/quote: https://indico.stfc.ac.uk/event/1730/contributions/10969/ (WebFetch 2026-10-25; LRT2026, 21 Sept 2026): 'These improvements are now being evaluated in the newly initiated third fill run.'; 'Detector upgrades have been ongoing since the end of the second fill run in 2020'. SNOLAB experiment page (Internet Archive capture of 2026-05-25, text read 2026-10-25): 'Status Upgrading Participation 10 Countries 38 Institutions 82 People'; https://www.snolab.ca/experiment/deap-3600/ itself returned HTTP 404 on 2026-10-25; https://deap3600.ca/ returned HTTP 403 on 2026-10-25 (Internet Archive capture of 2026-10-17 read).
* `/intervals/4/note` -- process wording removed, substance kept
  * old: "...d (the 2025 plan ended it \"~ summer 2026\"; SNOLAB lists \"Upgrading\"). RE-CHECK 2026-10-25: the newest dated statement is a 30 July 2026 talk by a DEAP collaboration member: \"Now taking data with detector in the upgraded configuration\", \"New data taking with upgraded detector to mitigate backgrounds (2025 – present)\", \"New data collection in progress with upgraded DEAP-3600 at SNOLAB\". That confirms third-fill running at the end of July 2026 and gives the start year (2025) but not the month; the 21 September 2026 abstract (\"newly initiated third fill run\", preliminary results) is consistent. No source dated after 21 September reports the end of the run, and the 2025 plan's \"~ summer 2026\" end is therefore not confirmed. Confidence raised from uncertain to approximate (a talk is a rank-12 source; the start year is approximate)."
  * new: "...d (the 2025 plan ended it \"~ summer 2026\"; SNOLAB lists \"Upgrading\"). The newest dated statement is a 30 July 2026 talk by a DEAP collaboration member: \"Now taking data with detector in the upgraded configuration\", \"New data taking with upgraded detector to mitigate backgrounds (2025 – present)\", \"New data collection in progress with upgraded DEAP-3600 at SNOLAB\". That shows third-fill running at the end of July 2026 and gives the start year (2025) but not the month; the 21 September 2026 abstract (\"newly initiated third fill run\", preliminary results) is consistent. No source dated after 21 September reports the end of the run, so the 2025 plan's \"~ summer 2026\" end is not confirmed. Confidence is 'approximate': a talk is a rank-12 source and the start year is approximate."
  * source/quote: text preserved; removed the 'RE-CHECK 2026-10-25' label and the 'confidence raised from uncertain' history
* `/notes`
  * old list: ["DEAP-3600 is a single-phase liquid argon SCINTILLATION detector, not a two-phase time projection chamber: it has no drift field and no ionization/charge readout, and detects only scintillation light via its 255 PMTs, using pulse-shape discrimination of that scintillation signal (deap3600.ca; Astropart. Phys. 108 (2019) 1-23, Sec. 1). technology_classes lists 'noble_liquid_tpc'/'argon_tpc' only because the ontology's enum has no separate scintillator-only class, per the dark-matter lead's convention in docs/atlas-worklog/dark-matter.md; this should not be read as DEAP-3600 having TPC-style charge readout.", "facility:snolab and site:snolab-underground-lab are referenced but not created: they are owned by the 'facilities' workstream, which had not landed as of this session (checked via `ls data/atlas/facilities/` and `ls data/atlas/sites/`). Dangling references, expected per docs/atlas-worklog/ID_REGISTRY.md.", "No proposal/approval interval is recorded: the INSPIRE experiment record (recid 1108195) carries no date_proposed/date_approved/date_started fields, unlike some other experiment records, and no other source fetched this session gives those dates."]
  * new list: ["DEAP-3600 is a single-phase liquid argon SCINTILLATION detector, not a two-phase time projection chamber: it has no drift field and no ionization/charge readout, and detects only scintillation light via its 255 PMTs, using pulse-shape discrimination of that scintillation signal (deap3600.ca; Astropart. Phys. 108 (2019) 1-23, Sec. 1). technology_classes lists 'noble_liquid_tpc'/'argon_tpc' only because the ontology's technology-class list has no separate scintillator-only class; this should not be read as DEAP-3600 having TPC-style charge readout.", "No proposal or approval interval is recorded: the INSPIRE experiment record (recid 1108195, read 2026-09-17) carries no date_proposed, date_approved or date_started fields, and no other source consulted (checked 2026-10-25) gives those dates."]
* `/summary/plain` -- STALE: statement contradicted by the cited source; corrected
  * old: "...would make hitting an argon nucleus. It has taken data since late 2016 and is currently being upgraded for a further run."
  * new: "...would make hitting an argon nucleus. It has taken data since late 2016. After detector upgrades it began a third run, which the collaboration's abstract of 21 September 2026 describes as newly initiated."
  * source/quote: https://indico.stfc.ac.uk/event/1730/contributions/10969/ (WebFetch 2026-10-25): 'These improvements are now being evaluated in the newly initiated third fill run.'
* `/summary/technical` -- STALE: statement contradicted by the cited source; corrected
  * old: "... ~30 GeV/c² and searches for superheavy multi-scattering dark matter; currently in a hardware upgrade phase toward a further ('third') fill."
  * new: "... ~30 GeV/c² and searches for superheavy multi-scattering dark matter; after hardware upgrades since the end of the second fill (2020), a third fill with the upgraded detector was described as 'newly initiated' in the collaboration's abstract of 21 September 2026."
  * source/quote: https://indico.stfc.ac.uk/event/1730/contributions/10969/ (WebFetch 2026-10-25)

## data/atlas/detectors/deap-3600.json

* `/intervals/1/note` -- process wording removed, substance kept
  * old: "END SET 2026-10-25. Previously open-ended with the note that no source said data taking had stopped; the collaboration states the second-fill data set ran from Nov 2016 to March 2020 and that upgrades have been ongoing \"since the end of the second fill run in 2020\"."
  * new: "The collaboration states that the second-fill data set ran from November 2016 to March 2020 (PASCOS 2025 slides) and that upgrades have been ongoing \"since the end of the second fill run in 2020\"."
* `/intervals/2/note` -- dated wording
  * old: "SNOLAB's own experiment page (accessed 2026-09-17) states current status 'Upgrading'; no source fetched this session gives the true start date of this phase. Start is set to 2026-09, the month this status was confirmed, as the earliest defensible anchor rather than an invented date; see experiment:deap-3600 for the same reasoning. RE-READ 2026-10-25: demoted to a phase annotation. The collaboration's abstracts of 22 June and 21 September 2026 describe a \"just-started\" / \"newly initiated third fill run\" with preliminary third-fill results, which conflicts with reading SNOLAB's \"Upgrading\" status label as a current absence of data taking. The SNOLAB page could not be re-opened. A 2025 plan said third-fill data taking would end \"~ summer 2026\" with decommissioning to make room for ARGOlite; no fetched source says whether that happened."
  * new: "SNOLAB's experiment page (read 2026-09-17; an Internet Archive capture of 25 May 2026 shows the same status) gives the current status 'Upgrading'; no source consulted (checked 2026-10-25) gives the true start date of this phase. The start is set to 2026-09, the month this status was first read, as the earliest defensible anchor rather than an invented date; see experiment:deap-3600 for the same reasoning. The collaboration's abstracts of 22 June and 21 September 2026 describe a \"just-started\" / \"newly initiated third fill run\" with preliminary third-fill results, which conflicts with reading SNOLAB's \"Upgrading\" label as a current absence of data taking; this interval is therefore a phase annotation and not the detector's current state. The SNOLAB page no longer loads (HTTP 404 on 2026-10-25). A 2025 plan said third-fill data taking would end \"~ summer 2026\" with decommissioning to make room for ARGOlite; no source consulted says whether that happened."
  * source/quote: https://indico.stfc.ac.uk/event/1730/contributions/10969/ (WebFetch 2026-10-25; LRT2026, 21 Sept 2026): 'These improvements are now being evaluated in the newly initiated third fill run.'; 'Detector upgrades have been ongoing since the end of the second fill run in 2020'. SNOLAB experiment page (Internet Archive capture of 2026-05-25, text read 2026-10-25): 'Status Upgrading Participation 10 Countries 38 Institutions 82 People'; https://www.snolab.ca/experiment/deap-3600/ itself returned HTTP 404 on 2026-10-25; https://deap3600.ca/ returned HTTP 403 on 2026-10-25 (Internet Archive capture of 2026-10-17 read).
* `/intervals/4/note` -- process wording removed, substance kept
  * old: "...d (the 2025 plan ended it \"~ summer 2026\"; SNOLAB lists \"Upgrading\"). RE-CHECK 2026-10-25: the newest dated statement is a 30 July 2026 talk by a DEAP collaboration member: \"Now taking data with detector in the upgraded configuration\", \"New data taking with upgraded detector to mitigate backgrounds (2025 – present)\", \"New data collection in progress with upgraded DEAP-3600 at SNOLAB\". That confirms third-fill running at the end of July 2026 and gives the start year (2025) but not the month; the 21 September 2026 abstract (\"newly initiated third fill run\", preliminary results) is consistent. No source dated after 21 September reports the end of the run, and the 2025 plan's \"~ summer 2026\" end is therefore not confirmed. Confidence raised from uncertain to approximate (a talk is a rank-12 source; the start year is approximate)."
  * new: "...d (the 2025 plan ended it \"~ summer 2026\"; SNOLAB lists \"Upgrading\"). The newest dated statement is a 30 July 2026 talk by a DEAP collaboration member: \"Now taking data with detector in the upgraded configuration\", \"New data taking with upgraded detector to mitigate backgrounds (2025 – present)\", \"New data collection in progress with upgraded DEAP-3600 at SNOLAB\". That shows third-fill running at the end of July 2026 and gives the start year (2025) but not the month; the 21 September 2026 abstract (\"newly initiated third fill run\", preliminary results) is consistent. No source dated after 21 September reports the end of the run, so the 2025 plan's \"~ summer 2026\" end is not confirmed. Confidence is 'approximate': a talk is a rank-12 source and the start year is approximate."
  * source/quote: text preserved; removed the 'RE-CHECK 2026-10-25' label and the 'confidence raised from uncertain' history
* `/notes/0` -- process wording removed, substance kept
  * old: "...asses carries 'noble_liquid_tpc'/'argon_tpc' only because the ontology enum has no dedicated scintillator-only class, following the convention set by docs/atlas-worklog/dark-matter.md for LZ; this is a taxonomy accommodation, not a claim that DEAP-3600 has TPC..."
  * new: "...asses carries 'noble_liquid_tpc'/'argon_tpc' only because the ontology's technology-class list has no dedicated scintillator-only class; this is a taxonomy accommodation, not a claim that DEAP-3600 has TPC..."
* `/notes/1` -- STALE: statement contradicted by the cited source; corrected
  * old: "Energy threshold: not recorded. No source fetched this session states a single nuclear-recoil analysis energy threshold for DEAP-3600."
  * new: "Energy threshold: not recorded as a spec. The detector paper's design table (Table 1) gives a nominal analysis threshold of 15 keVee (electron-equivalent) for a 3 tonne-year exposure, not a nuclear-recoil energy; no source consulted (checked 2026-10-25) states a single nuclear-recoil analysis energy threshold for DEAP-3600."
  * source/quote: arXiv:1712.01982 (PDF text read 2026-10-25), Table 1: 'Nominal analysis threshold ... 15 keVee'; text after Table 1: 'energy ROI of 120-240 photoelectrons, corresponding to a nominal energy ROI of 15 to 30 keVee'
* `/placements/0/note` -- process wording removed, substance kept
  * old: "site:snolab-underground-lab is owned by the 'facilities' workstream and had not been created in this session; dangling reference, expected per the Wave 3 brief and ID registry."
  * new: ""
* `/specs/shielding/locator` -- STALE: statement contradicted by the cited source; corrected
  * old: "deap3600.ca, experiment description"
  * new: "Astropart. Phys. 108 (2019) 1-23 (arXiv:1712.01982), Sec. 1 and Sec. 1.1 (Detector Overview)"
  * source/quote: same as above
* `/specs/shielding/note` -- STALE: statement contradicted by the cited source; corrected
  * old: ""
  * new: "The rock-overburden clause is also stated on deap3600.ca ('a deep underground laboratory which uses the 2 km of rock overburden to filter out cosmic-ray muons'); the water shield tank and muon veto are described in the detector paper."
  * source/quote: explains the two sources
* `/specs/shielding/quote` -- STALE: statement contradicted by the cited source; corrected
  * old: "a deep underground laboratory which uses the 2 km of rock overburden to filter out cosmic-ray muons"
  * new: "2 km underground (6000 meters water equivalent overburden) at SNOLAB in Sudbury, Ontario ... The outer steel shell is immersed in a 7.8-m-diameter shield tank filled with ultra-pure water and instrumented with 48 Hamamatsu R1408 PMTs serving as a muon veto."
  * source/quote: same as above
* `/specs/shielding/sources` -- STALE: statement contradicted by the cited source; corrected
  * old list: ["src:dm-noble-liquid-deap-3600-official-site"]
  * new list: ["src:dm-noble-liquid-deap-3600-detector-paper", "src:dm-noble-liquid-deap-3600-official-site"]
  * source/quote: detector paper added as the source of the new value (existing source record, unchanged)
* `/specs/shielding/value` -- STALE: statement contradicted by the cited source; corrected
  * old: "2 km of rock overburden (6000 m.w.e.) at SNOLAB; no additional water or scintillator veto shield is described for DEAP-3600 in the sources fetched this session."
  * new: "2 km of rock overburden (6000 m.w.e.) at SNOLAB; the detector sits inside a 7.8 m diameter shield tank of ultra-pure water instrumented with 48 PMTs that serve as a muon veto."
  * source/quote: arXiv:1712.01982 (WebFetch of the PDF 2026-10-25; Sec. 1.1 Detector Overview): 'The outer steel shell is immersed in a 7.8-m-diameter shield tank filled with ultra-pure water and instrumented with 48 Hamamatsu R1408 PMTs serving as a muon veto.' Table 1 also lists 'Water shielding tank diameter x height 7.8 m x 7.8 m' and 'Number of Cherenkov veto PMTs 48'. The old value said no additional water or scintillator veto shield was described in the sources.
* `/specs/shielding/verified_at` -- STALE: statement contradicted by the cited source; corrected
  * old: "2026-09-17"
  * new: "2026-10-25"
  * source/quote: re-read the detector paper (WebFetch of the PDF) on 2026-10-25

## data/atlas/collaborations/deap-3600.json

* `/intervals/0/note` -- process wording removed, substance kept
  * old: "...ate_approved/date_started fields. 2015 is the earliest year for which this session found a dated, sourced account of collaboration activity (planning the detector's commissioning) and stands in for an unknown formation date; it is not itself a claim abo..."
  * new: "...ate_approved/date_started fields. 2015 is the earliest year for which a dated, sourced account of collaboration activity (planning the detector's commissioning) was found among the sources consulted, and it stands in for an unknown formation date; it is not itself a claim abo..."
* `/notes/0` -- dated wording
  * old: "No membership roster file (data/atlas/memberships/deap-3600.json) is written: this is a full-depth extra not required for a Tier B, non-flagship experiment, and no per-institution list (only aggregate counts) was found on deap3600.ca or snolab.ca in this session."
  * new: "No per-institution membership list is recorded: only aggregate counts were found on deap3600.ca and snolab.ca (checked 2026-10-25 through Internet Archive captures)."
  * source/quote: https://indico.stfc.ac.uk/event/1730/contributions/10969/ (WebFetch 2026-10-25; LRT2026, 21 Sept 2026): 'These improvements are now being evaluated in the newly initiated third fill run.'; 'Detector upgrades have been ongoing since the end of the second fill run in 2020'. SNOLAB experiment page (Internet Archive capture of 2026-05-25, text read 2026-10-25): 'Status Upgrading Participation 10 Countries 38 Institutions 82 People'; https://www.snolab.ca/experiment/deap-3600/ itself returned HTTP 404 on 2026-10-25; https://deap3600.ca/ returned HTTP 403 on 2026-10-25 (Internet Archive capture of 2026-10-17 read).
* `/notes/1` -- process wording removed, substance kept
  * old: "No person: or leadership records are created: DEAP-3600 is not a flagship in this wave and no spokesperson name with an INSPIRE author recid was fetched and verified in this session."
  * new: "No spokesperson or other leadership is recorded here."
* `/summary/technical` -- dated wording
  * old: "DEAP-3600 (DEAP) Collaboration: as of the SNOLAB experiment page (accessed 2026-09-17), 82 people from 38 institutions in 10 countries; operates the single-phase liquid argon scintillation detector at SNOLAB's 2 km level. Formation date not published in any source fetched this session."
  * new: "DEAP-3600 (DEAP) Collaboration: as of the SNOLAB experiment page (read 2026-09-17; an Internet Archive capture of 25 May 2026 shows the same figures), 82 people from 38 institutions in 10 countries; operates the single-phase liquid argon scintillation detector at SNOLAB's 2 km level. No source consulted (checked 2026-10-25) gives a formation date."
  * source/quote: https://indico.stfc.ac.uk/event/1730/contributions/10969/ (WebFetch 2026-10-25; LRT2026, 21 Sept 2026): 'These improvements are now being evaluated in the newly initiated third fill run.'; 'Detector upgrades have been ongoing since the end of the second fill run in 2020'. SNOLAB experiment page (Internet Archive capture of 2026-05-25, text read 2026-10-25): 'Status Upgrading Participation 10 Countries 38 Institutions 82 People'; https://www.snolab.ca/experiment/deap-3600/ itself returned HTTP 404 on 2026-10-25; https://deap3600.ca/ returned HTTP 403 on 2026-10-25 (Internet Archive capture of 2026-10-17 read).

## data/atlas/detectors/darkside-20k.json

* `/placements/0/note` -- process wording removed, substance kept
  * old: "site:lngs-hall-c is a dangling reference: owned by the \"facilities\" workstream, not yet created as of 2026-09-17."
  * new: ""
* `/summary/technical` -- dated wording
  * old: "Dual-phase (two-phase) liquid argon TPC, 50 t active mass, SiPM-based light readout, in LNGS Hall C. Under construction as of the sources fetched (2024)."
  * new: "Dual-phase (two-phase) liquid argon TPC, 50 t active mass, SiPM-based light readout, in LNGS Hall C. Under construction as of 2026-10-25 (LNGS DarkSide page, undated: 'currently under construction in the LNGS Hall-C'; arXiv:2402.07566, February 2024, reports the construction phase under way)."
  * source/quote: https://www.lngs.infn.it/en/darkside (WebFetch 2026-10-25; page undated, footer 'Copyright (c) 2026 INFN LNGS'): 'It is currently under construction in the LNGS Hall-C'; 'a two-phase LAr detector with a 50 tonnes active volume'; 'The experiment is expected to begin operation in 2027'. arXiv:2402.07566 (Feb 2024; PDF text read 2026-10-25): 'has entered the construction phase'.

## data/atlas/detectors/dmradio.json

* `/intervals/0/note` -- dated wording
  * old: "No fetched source gives an exact construction-start date. The 2022 status paper says the hardware 'is being built'; the 2026 cryogenic-system paper reports 'measured performance' of the built cryostat, showing construction/commissioning is well advanced by mid-2026."
  * new: "No source consulted (checked 2026-10-25) gives an exact construction-start date. The October 2022 status paper says the hardware 'is being built'; the July 2026 cryogenic-system paper reports 'measured performance' of the DMRadio-50L cryostat, which shows construction or commissioning well advanced by mid-2026."
  * source/quote: arXiv:2210.07215 (status paper, submitted 13 Oct 2022; PDF text read 2026-10-25): 'This experiment is being built on the Stanford University campus.' / 'This experiment is being built at SLAC National Lab.'. arXiv:2607.05771 (submitted 7 July 2026; abstract WebFetch 2026-10-25): 'We present the conceptual design, technical implementation, and measured performance of the hybrid cryogenic system'; text refers to future data-taking.
* `/summary/technical` -- dated wording
  * old: "... solenoidal magnet, 30-200 MHz) at SLAC; under construction as of the sources fetched this session."
  * new: "... solenoidal magnet, 30-200 MHz) at SLAC; under construction as of the October 2022 status paper (arXiv:2210.07215); a July 2026 paper (arXiv:2607.05771) reports measured performance of the DMRadio-50L cryogenic system and refers to future data taking."
  * source/quote: arXiv:2210.07215 (status paper, submitted 13 Oct 2022; PDF text read 2026-10-25): 'This experiment is being built on the Stanford University campus.' / 'This experiment is being built at SLAC National Lab.'. arXiv:2607.05771 (submitted 7 July 2026; abstract WebFetch 2026-10-25): 'We present the conceptual design, technical implementation, and measured performance of the hybrid cryogenic system'; text refers to future data-taking.
* `/technology/note` -- process wording removed, substance kept
  * old: "VERIFIER FIX (2026-09-17): classified under `other` by the original research pass, which noted no matching technology_classes enum value existed; v0.2 amendment A24 (2026-09-17) added `helioscope`, `light_shining_through_wall` and `lumped_element_resonator` to the ontology's technology_classes for exactly this gap. Reclassified as `lumped_element_resonator` with the sourced `technology` free-text description kept unchanged; no new claim is made beyond what was already sourced."
  * new: "Classified as `lumped_element_resonator`, the technology class for lumped-element LC haloscopes; the sourced `technology` free-text description is unchanged and no claim beyond it is made."

## data/atlas/experiments/darkquest.json

* `/intervals/0/note` -- dated wording
  * old: "This is the date of the Snowmass planning-document proposal, not a formal experiment-approval date; no source fetched this session states that DarkQuest has been formally approved or scheduled."
  * new: "This is the date of the Snowmass planning-document proposal, not a formal experiment-approval date; no source consulted (checked 2026-10-25: arXiv:2203.08322 and a web search for later announcements) states that DarkQuest has been formally approved or scheduled."
  * source/quote: https://arxiv.org/abs/2203.08322 (WebFetch 2026-10-25; submitted 16 March 2022; comment 'Contribution to Snowmass 2021'): no approval, funding or construction status in the abstract; WebSearch 2026-10-25 for later announcements found none (only the proposal and the ongoing SpinQuest programme).
* `/notes/0` -- process wording removed, substance kept
  * old: "Derived fields (detector_ids, site_ids, result_ids, document_ids) are deliberately not written (v0.2 A1)."
  * new: "Derived lists (detector_ids, site_ids, result_ids, document_ids) are not stored in this record; they are derived from the other records."
* `/notes/1` -- dated wording
  * old: "collaboration_ids left empty: no source fetched this session names a distinct 'DarkQuest Collaboration' separate from the SeaQuest/SpinQuest proponents; no collaboration:darkquest record was created rather than inventing one."
  * new: "collaboration_ids is empty: no source consulted (checked 2026-10-25) names a distinct 'DarkQuest Collaboration' separate from the SeaQuest/SpinQuest proponents, so no DarkQuest collaboration record exists."
  * source/quote: https://arxiv.org/abs/2203.08322 (WebFetch 2026-10-25; submitted 16 March 2022; comment 'Contribution to Snowmass 2021'): no approval, funding or construction status in the abstract; WebSearch 2026-10-25 for later announcements found none (only the proposal and the ongoing SpinQuest programme).
* `/notes/2` -- process wording removed, substance kept
  * old: "2026-09-17 fixed-target verification: `lineage` previously carried an `upgrade_of experiment:seaquest` row, but the cited source's own title ('DarkQuest: A dark sector upgrade to SpinQuest at the 120 GeV Fermilab Main Injector', arXiv:2203.08322) and abstract say DarkQuest upgrades SpinQuest (Fermilab E-1039, the spin-physics successor to SeaQuest that reuses the same spectrometer); the abstract fetched this session does not mention SeaQuest at all. Re-pointing `upgrade_of` at experiment:seaquest was not what the source said, so the row is removed rather than kept as a plausible-sounding substitute (ground rule 3: unknown is a value). experiment:spinquest is not created here (SpinQuest is out of this wave's ID_REGISTRY scope); the SpinQuest relationship is recorded only in prose, in this note and in `unique_capabilities`/`summary`, not as a `lineage` row to an id this workstream does not own."
  * new: "The cited source's own title ('DarkQuest: A dark sector upgrade to SpinQuest at the 120 GeV Fermilab Main Injector', arXiv:2203.08322) and abstract say DarkQuest upgrades SpinQuest (Fermilab E-1039, the spin-physics successor to SeaQuest that reuses the same spectrometer); the abstract does not mention SeaQuest at all. The lineage therefore carries no `upgrade_of experiment:seaquest` row, because the source does not say that. No SpinQuest experiment record exists, so the SpinQuest relationship is recorded only in prose (this note, `unique_capabilities` and `summary`), not as a lineage row."
  * source/quote: arXiv:2203.08322 (abstract and PDF text read 2026-10-25): title 'DarkQuest: A dark sector upgrade to SpinQuest at the 120 GeV Fermilab Main Injector'; body: 'E906/E1039 SeaQuest/SpinQuest spectrometer experiments at Fermilab'
* `/notes/3` -- dated wording
  * old: "No detector record created: DarkQuest is described as reusing the SeaQuest/SpinQuest apparatus at site:fermilab-nm4-hall (see experiment:seaquest and detector:seaquest) rather than a distinct new detector; no source fetched this session describes DarkQuest-specific hardware changes in enough detail to justify a separate detector file in this pass."
  * new: "No separate detector record exists: DarkQuest is described as reusing the SeaQuest/SpinQuest apparatus at site:fermilab-nm4-hall (see experiment:seaquest and detector:seaquest), and no source consulted (checked 2026-10-25) describes DarkQuest-specific hardware changes in enough detail to justify one."
  * source/quote: https://arxiv.org/abs/2203.08322 (WebFetch 2026-10-25; submitted 16 March 2022; comment 'Contribution to Snowmass 2021'): no approval, funding or construction status in the abstract; WebSearch 2026-10-25 for later announcements found none (only the proposal and the ongoing SpinQuest programme).
* `/summary/technical` -- dated wording
  * old: "Proposed dark-sector upgrade (Snowmass 2021 contribution, arXiv:2203.08322) to the SeaQuest/SpinQuest spectrometer at the 120 GeV Fermilab Main Injector, targeting visible decays of dark photons, axion-like particles and dark scalars in the MeV-GeV mass range; not yet formally approved as of the sources fetched this session."
  * new: "Proposed dark-sector upgrade (Snowmass 2021 contribution, arXiv:2203.08322) to the SeaQuest/SpinQuest spectrometer at the 120 GeV Fermilab Main Injector, targeting visible decays of dark photons, axion-like particles and dark scalars in the MeV-GeV mass range; no source consulted (checked 2026-10-25) reports a formal approval."
  * source/quote: https://arxiv.org/abs/2203.08322 (WebFetch 2026-10-25; submitted 16 March 2022; comment 'Contribution to Snowmass 2021'): no approval, funding or construction status in the abstract; WebSearch 2026-10-25 for later announcements found none (only the proposal and the ongoing SpinQuest programme).

