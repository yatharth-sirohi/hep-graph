# Follow-ups 2 (second integration data stream): feed links, era energies, deferred hadron and collider candidates

Branch `atlas-followups2` (worktree `HEP-Graph-ar-followups2`, cut from the integration branch at `e01b954`). Registry owners: `hadron-2` (task 3, `data/atlas/coverage/hadron-2.json`), `colliders-2` (task 4, `data/atlas/coverage/colliders-2.json`). Source ids of this pass: `src:fu2-*` (tasks 1 and 2), `src:hadron2-*` and `src:colliders2-*` (tasks 3 and 4).

**Date convention.** Every record written by this stream carries `verified_at: "2026-10-26"`, as STREAM_RULES and the brief require. The work was interrupted twice (a usage limit stopped the first research agents, and the machine's scratch directory was cleared once), so part of the page and PDF fetching happened after 2026-10-26 (the session clock later read 2026-10-28); the quotes were re-checked verbatim against the live pages with `scripts/atlas_quote_check.py` (results under "Checks"). The `verified_at` date was kept at the stream's single date rather than split.

## Scope

1. **Feed links** that can now exist (all the records are merged): SLAC linac to SPEAR and PEP; PETRA to HERA (and DORIS to PETRA if a source states it); AGS to the EIC; `accelerator:hesr` (only if FAIR sources meet the bar).
2. **Era energies** for the energy-frontier chart: LEP2 year by year, the Tevatron, CEBAF's 12 GeV Upgrade, and every other collider whose headline energy is not its first and whose change a source dates (HERA, RHIC, LHC Run 1).
3. **Deferred hadron candidates** (`HADRON_2.md`): Mainz A4, JLab HAPPEX, G0, PRad, SLAC E158, SPS NA35, NA38, NA44, WA98, HELIOS.
4. **Deferred collider candidates** (`COLLIDERS_2.md`): ADONE and its experiments, SCTF and STCF, the DAPHNE nuclear-physics experiments FINUDA, DEAR and SIDDHARTA (plus SIDDHARTA-2 and PADME). The per-entity tables for task 4 are in `docs/atlas-worklog/FOLLOWUPS_2_colliders.md` (written by the research agent that did that task and checked by the lead; this file summarises it).

## Counts

| what | count |
|---|---|
| feed links written | 4 (`slac-linac` to `spear`, `slac-linac` to `pep`, `petra` to `hera`, `ags` to `eic`) |
| accelerator records edited for era energies | 6 (`lep`, `fermilab-tevatron`, `cebaf`, `hera`, `rhic`, `lhc`); for feed links 3 (`slac-linac`, `petra`, `ags`) |
| new dated era intervals | LEP 7, Tevatron 3, CEBAF 3 (and 2 re-sourced), HERA 2, RHIC 2 (specs on existing intervals), LHC 1 |
| new experiments (each with detector, collaboration, results, sources, registry row) | 10 hadron + 15 collider = 25 |
| new accelerators | 3 (`adone`, `sctf`, `stcf`) |
| new facility, new site | 1 (`facility:stcf-hefei`), 1 (`site:stcf-hefei-future-big-science-city`) |
| results | 16 hadron + 8 collider |
| source records | `fu2-*` 23, `hadron2-*` 53 new, `colliders2-*` 43 new |
| registry rows | 10 + 15 |
| existing records edited besides the above | `experiment:moller`, `experiment:na49`, `experiment:na50` (lineage rows), `tour:higgs-hunt` (one claim), `tests/test_atlas_charts.py` |

## Task 1: feed links

| link | start | end | URL | verbatim quote | confidence |
|---|---|---|---|---|---|
| `accelerator:slac-linac` to `accelerator:spear` | 1972 | 1990 | https://www6.slac.stanford.edu/news/2016-05-04-slacs-historic-linac-turns-50-and-gets-makeover, https://www.slac.stanford.edu/gen/grad/GradHandbook/slac.html, https://ahro.slac.stanford.edu/resources/slac-history/milestones | In 1972, the linac beams were for the first time injected into the SPEAR storage ring to produce exotic new particles in powerful electron-positron collisions. | approximate |
| `accelerator:slac-linac` to `accelerator:pep` | 1980 | 1990 | https://www.slac.stanford.edu/gen/grad/GradHandbook/slac.html, https://www6.slac.stanford.edu/news/2016-05-04-slacs-historic-linac-turns-50-and-gets-makeover, https://ahro.slac.stanford.edu/resources/slac-history/milestones | With the advent of colliding beam storage rings (SPEAR in 1972) and PEP (in 1980), which are discussed in more detail below, the SLAC linac also served as source and injector for electrons and positrons. | approximate |
| `accelerator:petra` to `accelerator:hera` | 1990 | 2007 | https://arxiv.org/abs/2208.11076, https://arxiv.org/abs/0805.3334, https://synchrotron60.desy.de/1978/index_eng.html | After its shutdown as particle collider in November 1986, PETRA came back to life in 1990 as PETRA-II, where it served as pre-accelerator for the electron-proton collider HERA until 2007. | verified |
| `accelerator:ags` to `accelerator:eic` | 2032 (planned) | open | https://proceedings.jacow.org/ipac2022/papers/wepotk014.pdf, https://arxiv.org/abs/2305.15593, https://www.bnl.gov/newsroom/news.php?a=122794 | To accomplish the acceleration process, the hadrons are pre-accelerated in the Alternating Gradient Synchrotron (AGS), extracted, and transferred to HSR for injection. | approximate |

Each link also carries a note with the other quotes behind its dates (the SPEAR end from SLAC Milestones, the PEP end from the CERN Courier, the PETRA dates from Bethke and Wagner, the EIC start window from the ePIC paper). All links are `A30` objects with `sources`, `quote`, `locator`, `confidence`, `verified_at`.

**Not created, with the reason.**

* **DORIS to PETRA: no link.** No source read states a feed from DORIS to PETRA. Bethke and Wagner (arXiv:2208.11076) call DORIS and SPEAR "PETRA's precursor e+ e- colliders" (earlier machines), and the DESY DORIS history page does not mention PETRA. A precursor is not a stage of the chain, so nothing was written; a note on `accelerator:petra` says so.
* **`accelerator:hesr` was not created.** The bar is facility, kind, status in FAIR's own wording, and the relation from SIS100. The facility (`facility:gsi-fair`), the kind (a storage ring) and a relation are sourced: the IPAC 2015 FAIR accelerator paper (Kester et al., GSI and Julich) says "The high-energy storage ring (HESR) is optimized for antiprotons of energy up to 14 GeV. This ring will operate with an internal target and associated detector set-up (PANDA).", lists it in the Modularized Start Version with a 575 m circumference, and says the SIS100 proton beam goes to the antiproton target; the PANDA website says "Antiprotons produced by a primary proton beam will then be filled into the High Energy Storage Ring (HESR)". But no FAIR or GSI source gives a current status or any date: the fair-center.eu pages never name the HESR; the October 2025 FAIR paper (arXiv:2510.14948) says the first project stage ("First Science+") is the SIS100, the Super-FRS and the beam transport lines, which excludes the HESR; the 2023 GSI/FAIR PANDA slides put the HESR with the p-linac, the CR and PANDA in "FAIR MSV", flattened text that does not date it. A record with no dated interval would break the mandatory bar (a start), and an unsourced `planned` start would be invented. `experiment:panda` keeps an empty `accelerator_ids`, as its note says.
* **AGS to the EIC** carries a planned `start` window (2032, from the 2023 ePIC paper's "expected to start operate in 2032"); the EIC's own start of operations is not dated in any BNL page read.

## Task 2: era energies

The chart (`static/atlas/js/views/frontier-rows.js`) draws a collider at `specs.cms_energy` once per `active` interval whose own `specs` carry it, and a machine with no dated energy as a dashed ring at the headline value in the first-operation year. Two findings drove the edits: an interval that starts earlier than the energy it carries is a false point, and an interval with a `kind` (`phase`, `run`) is an annotation, not a lifecycle state (`schema.state_at` takes only intervals without `kind`), so an era that must set the machine's state has to be a plain interval (CEBAF).

### What the chart now draws (from an in-memory build; checked in `tests/test_atlas_charts.py`)

| machine | points (year, energy) | before |
|---|---|---|
| `accelerator:lep` | LEP 1989 91 GeV; 1995 136; 1996 161.3; 1996 172; 1997 183; 1998 189; 1999 202; 2000 209 GeV | 1989 91 GeV and **1995 209 GeV** (the false point the reviewer found) |
| `accelerator:fermilab-tevatron` | 1985 1.6 TeV; 1986 1.8; 1992 1.8; 2001 1.96 TeV | one dashed ring: 1.96 TeV at 1985 |
| `accelerator:cebaf` | 1995 4 GeV; 2000 6; 2016 12 GeV | 1995 4 GeV, 2000 6 GeV; the 12 GeV headline footnoted |
| `accelerator:hera` | 1992 300 GeV; 1998 318 GeV | one dashed ring: 320 GeV at 1992 |
| `accelerator:rhic` | 2000 130 GeV; 2001 200; 2021 500 GeV | dashed ring 200 GeV at 2000, then 500 GeV in 2021 |
| `accelerator:lhc` | 2010 7 TeV; 2012 8; 2015 13; 2022 13.6 TeV | 2010 7 TeV; 2015 13; 2022 13.6 |

### LEP (`accelerator:lep`)

The LEP2 phase interval (start 1995) carried `cms_energy` 209 GeV and `beam_energy` 104.5 GeV; both were removed from it (the top-level `cms_energy` "up to 209 GeV" stays as the headline), and each data-taking year or run has its own `kind: run` interval with the highest centre-of-mass energy of that run and a derived half per beam (`confidence: derived`, no quote). The value is the highest of the run's energy points; the display names the others. Quotes were taken from collaboration papers.

| run interval | start | end | cms energy | URL | verbatim quote |
|---|---|---|---|---|---|
| LEP2 1995 run (130 and 136 GeV) | 1995 | 1995 | 136 GeV (data at 130 and 136 GeV) | https://arxiv.org/abs/hep-ex/9609018 | The inclusive one- and two-jet cross-sections are measured in collisions of quasi-real photons at e+e- centre-of-mass energies of 130 and 136 GeV using the OPAL detector at LEP. |
| LEP2 1996 run at 161 GeV (W-pair threshold) | 1996-06 | 1996-08 | 161.3 GeV | https://arxiv.org/abs/hep-ex/9704019 | We summarize the recent results from OPAL using 9.9 pb^-1 of data collected at \sqrt s = 161.3 GeV from June to August 1996. |
| LEP2 1996 run at 172 GeV | 1996-10 | 1996-11 | 172 GeV | https://arxiv.org/abs/hep-ph/9709380 | The determination of the W mass, both through the measurement of the WW production cross section at a center-of-mass energy of 161 GeV and through the study of the invariant mass distribution of W decay products in the 172 GeV run are described first. |
| LEP2 1997 run at 183 GeV | 1997 | 1997 | 183 GeV | https://arxiv.org/abs/hep-ex/9805020 | In 1997 each LEP experiment collected approximately 55 inv. pb of data at a center-of-mass energy of 183 GeV. |
| LEP2 1998 run at 189 GeV | 1998 | 1998 | 189 GeV | https://arxiv.org/abs/hep-ex/0103022 | The DELPHI detector at LEP has collected 54 pb^{-1} of data at a centre-of-mass energy around 183 GeV during 1997, 158 pb^{-1} around 189 GeV during 1998, and 187 pb^{-1} between 192 and 200 GeV during 1999. |
| LEP2 1999 run (192 to 202 GeV) | 1999 | 1999 | 202 GeV (data at 192 to 202 GeV) | https://arxiv.org/abs/hep-ex/0012026 | In 1999 the LEP experiments collected data at centre of mass energies between 192 and 202 GeV for about 900 pb-1 integrated luminosity. |
| LEP2 2000 run (up to 209 GeV) | 2000 | 2000-11-02 | 209 GeV (data at 205 to 209 GeV) | https://arxiv.org/abs/1302.3415 | These inputs combine the data collected in 1996 at 172 GeV, in 1997 at 183 GeV, in 1998 at 189 GeV, in 1999 at 192 − 202 GeV, and in 2000 at 205 − 209 GeV. |

Other sources used for the LEP dates (in the interval notes): the LEP Energy Working Group (arXiv:hep-ex/9901002: "The centre-of-mass energy of the large electron-positron (LEP) collider increased to 161 GeV in 1996"), the LEP electroweak combination (arXiv:1302.3415: "reached in 2000, the final year of LEP operation"; Table 1.1 and 3.1 give the mean actual energies 130.3 and 136.3, 161.3, 172.1, 182.7, 188.6, 191.6 to 201.8, 204.8 to 208.0 GeV), Miquel (arXiv:hep-ph/9709380: "The second run, in October and November 1996,"), and the CERN LEP page already cited by the record ("The collider's energy eventually topped 209 GeV in 2000.").

### Tevatron (`accelerator:fermilab-tevatron`)

| interval | start | end | cms energy | URL | verbatim quote |
|---|---|---|---|---|---|
| First proton-antiproton collisions (engineering test run, 1.6 TeV) | 1985-10-13 | 1985-10-13 | 1.6 TeV | https://history.fnal.gov/criers/FN_1985_10_23.pdf | achieved the first proton-antiproton collision at 1.6 TeV, the highest energy yet achieved in a laboratory. |
| 1.8 TeV collider era (Run 0 in 1987 and 1988-89, Run I in 1992-96) | 1986-11-30 | 1996-02 | 1.8 TeV | https://arxiv.org/abs/1109.1864 | Run I ultimately delivered a total integrated luminosity of 180 pb-1 to both CDF and D0 experiments at √s = 1800 GeV. |
| Run I (August 1992 to February 1996, 1.8 TeV) | 1992-08 | 1996-02 | 1.8 TeV | https://arxiv.org/abs/1109.1864 | Run I ultimately delivered a total integrated luminosity of 180 pb-1 to both CDF and D0 experiments at √s = 1800 GeV. |
| Run II | 2001-03 | 2011-09 | 1.96 TeV | https://arxiv.org/abs/1510.02992 | The Tevatron proton-antiproton collider at the Fermi National Accelerator Laboratory (Fermilab) operated at a collision energy of 1.96 TeV (980 GeV per beam) |

The "1.8 TeV collider era" interval runs from the first 1.8 TeV collisions (30 November 1986) to the end of Run I (February 1996) so that a view at any year in between (Run 0 in 1987 and 1988-89, Run I from August 1992) reads 1.8 TeV and not the 1.96 TeV headline; the collider took data only in runs inside it (the note lists them). Run I is also its own interval. The old Run II interval started in 2002 (Vellidis, DPF 2015); Shiltsev, a Fermilab accelerator physicist, writes "Run II was initiated in March of 2001 and continued through September 2011", which is used (conflict below). The Higgs-hunt tour claim "from 2002 through 2011 (Run II)" referenced that interval and now reads "from 2001 through 2011 (Run II)" with the energy and the dates on two claims.

### CEBAF (`accelerator:cebaf`)

| interval (status) | start | end | URL | verbatim quote |
|---|---|---|---|---|
| 4 GeV era (design energy reached 1995) (active) | 1995 | 2000 | https://accelconf.web.cern.ch/IPAC2015/papers/moxgb2.pdf | The CEBAF design included 42 cryomodules with each cryomodule containing 8 SRF cavities to achieve the design energy of 4 GeV. CEBAF reached design energy in 1995. |
| 6 GeV era (until the 12 GeV Upgrade shutdown) (active) | 2000 | 2012-05 | https://accelconf.web.cern.ch/IPAC2015/papers/moxgb2.pdf | The energy reach of 6 GeV of CEBAF was establish in 2000; CEBAF operated at energies up to 6 GeV until 2012. |
| 12 GeV Upgrade: 6 GeV operations ended, installation (upgrade) | 2012-05 | 2013-12 | https://cerncourier.com/a/cebaf-delivers-first-beams-following-upgrade/ | In May 2012, the accelerator was shut down for its 12 GeV upgrade. |
| 12 GeV Upgrade: beam commissioning (first beams to Hall D, 7 May 2014) (commissioning) | 2013-12 | 2016 | https://accelconf.web.cern.ch/IPAC2015/papers/moxgb2.pdf | 6 GeV beam operations terminated in 2012, and the accelerator tunnel portion of the upgrade was sufficiently complete by the end of 2013 to start of beam commissioning activities. |
| 12 GeV era (higher-energy experiments) (active) | 2016 | open | https://arxiv.org/abs/2408.16880 | The major construction of the accelerator upgrade to 12 GeV was completed in a six-month shut-down at the end of 2011 and a long shut-down throughout 2013. Since 2016, nuclear physics experiments at the higher beam energy have been performed. |
| 12 GeV Upgrade dedication (active) | 2018-05-02 | open | https://en.wikipedia.org/wiki/Thomas_Jefferson_National_Accelerator_Facility | On 2 May 2018 the CEBAF 12 GeV Upgrade Dedication Ceremony took place. |

The 4 GeV and 6 GeV intervals were Wikipedia-only (`confidence: uncertain`); they now rest on the IPAC 2015 JLab commissioning paper (Freyberger), the LINAC 2012 paper (Pilat) and the CERN Courier of 23 July 2014. The 6 GeV start is now year-precision (the old day, 6 August 2000, had no source outside the encyclopaedia). The upgrade shutdown and the beam-commissioning intervals are lifecycle intervals (status `upgrade`, `commissioning`), so CEBAF is not `active` from May 2012 to 2016; no experiment record warns for that gap (A12 checked). The 12 GeV headline is now a dated era value, not a footnote. Three intervals still rest on the encyclopaedia entry and were left (1987 construction start, 1994 first beam, 2018 dedication).

### HERA, RHIC, LHC

| interval | start | end | cms energy | URL | verbatim quote |
|---|---|---|---|---|---|
| `hera`: HERA I at 820 GeV protons (first data in summer 1992) | 1992 | 1998 | 300 GeV (verified) | https://arxiv.org/abs/hep-ex/9705001 | The data were taken with the H1 detector at the HERA storage ring in 1994, in which 27.5 GeV positrons collided with 820 GeV protons at a centre of mass energy sqrt{s}=300 GeV. |
| `hera`: HERA at 920 GeV protons (from 1998) | 1998 | 2007-06-30 | 318 GeV (derived) | https://arxiv.org/abs/hep-ex/0106022 | At HERA, new physics processes beyond the SM are probed in e^+/- proton collisions at a center of mass energy of 300-318 GeV. |
| `rhic`: first collisions / physics operations begin | 2000-06-12 | open | 130 GeV per colliding nucleon pair (Au+Au, Run 1) (verified) | https://arxiv.org/abs/nucl-ex/0106001 | Results from the PHENIX experiment for the first RHIC run with Au-Au collisions at a nucleon-nucleon center-of-mass energy of 130 GeV are presented. |
| `rhic`: full design energy reached (100 GeV/nucleon, Au+Au) | 2001-07-18 | open | 200 GeV per colliding nucleon pair (Au+Au, Run 2) (verified) | https://arxiv.org/abs/nucl-ex/0209015 | We show first results on phi -> K+K-, e+e-, low and intermediate mass dielectron continuum, single electrons from charm, and J/psi yields in proton-proton and Au-Au collisions at sqrt{s_{NN}}=200 GeV. |
| `lhc`: Run 1 at 8 TeV (2012) | 2012 | 2013 | 8 TeV (verified) | https://arxiv.org/abs/1207.7214 | The datasets used correspond to integrated luminosities of approximately 4.8 fb^-1 collected at sqrt(s) = 7 TeV in 2011 and 5.8 fb^-1 at sqrt(s) = 8 TeV in 2012. |

RHIC: the BNL release of 18 July 2001 supplies the per-nucleon beam energies ("In its first run, RHIC collided ions at a maximum energy of 65 billion electron volts (GeV) per nucleon ... The new collisions, at 100 GeV per nucleon"), so 130 and 200 GeV are twice those; the collaboration abstracts state 130 and 200 GeV directly. HERA's 318 GeV is `derived` (2 sqrt(27.5 x 920) = 318 GeV) from the sourced beam energies, with the abstract "300-318 GeV" as support; the headline 320 GeV ("about 320 GeV", Klein and Yoshida) is therefore footnoted by the chart as a value no era dates, which is accurate to the source. LHC: only the 2012 year of Run 1 was added (the ATLAS paper dates 7 TeV to 2011 and 8 TeV to 2012).

## Task 3: deferred hadron candidates (owner `hadron-2`)

Ten experiments were added; each has an experiment, a detector (placed at an existing campus-grade or hall site, so no new coordinates), a collaboration, one to three result records, sources and a registry row (tier B, or C for HELIOS and NA44, all `researched: partial`). Three existing records gained a sourced lineage row: `experiment:moller` (predecessor `experiment:slac-e158`, from the MOLLER proposal "will improve on this result by a factor of five"), `experiment:na49` (predecessor `experiment:na35`), `experiment:na50` (predecessor `experiment:na38`). HAPPEX, G0 and A4 are linked `complementary` (rows on `a4-mami` and `g0`).

The ten records were written by two research agents that a usage limit stopped before they logged or ran their own quote checks. The lead validated them (0 errors, no new warnings), ran the repository quote checker on every record (all quotes `verbatim`, 0 number flags) and reviewed every one against the mandatory bar (identity, time, place, content, tracking; checked by script: a status and dated interval, a host facility and placed detector, topics, `summary.plain` of 60 words or fewer, at least one source, a collaboration record, a registry row). The tables below are generated from the records.


#### `experiment:a4-mami`: A4 (MAMI) (completed); kind hadron_structure; host facility:mainz-mami; detector placed at `site:mainz-kph-campus`; accelerators accelerator:mami

| interval | start | end | status | confidence | URL | verbatim quote |
|---|---|---|---|---|---|---|
| data taking (earliest documented beam time: January 2003) | 2003-01 | 2018 | active | uncertain | https://www.blogs.uni-mainz.de/fb08-ag-maas/files/2017/06/Bastl_Baryons04.pdf | Data taking in January 03 |
| January 2003 beam time (transverse asymmetry, 855 MeV) | 2003-01 | 2003-01 | active | verified | https://www.blogs.uni-mainz.de/fb08-ag-maas/files/2017/06/Bastl_Baryons04.pdf | Data taking in January 03 |
| September 2003 beam time (transverse asymmetry, 569 MeV) | 2003-09 | 2003-09 | active | verified | https://www.blogs.uni-mainz.de/fb08-ag-maas/files/2017/06/Bastl_Baryons04.pdf | Data taking in September 03 |
| completed | 2018 | open | completed | uncertain | https://pos.sissa.it/346/116/pdf | The A4 collaboration at the MAMI accelerator has performed measurements at various beam energies between 300 MeV and 1.5 GeV both at forward and backward angles. |

* result `result:a4-beam-transverse-asymmetry-wide-energy-2020` (2020-02-14): 

* result `result:a4-strange-form-factors-backward-q2-022-2009` (2009-03-16): G_E^s(0.22) = 0.050 +- 0.038 +- 0.019 and G_M^s(0.22) = -0.14 +- 0.11 +- 0.11

* result `result:a4-strange-form-factors-q2-0230-2004` (2004-01-16): G_E^s + 0.225 G_M^s = 0.039 +- 0.034 at Q^2 = 0.230 (GeV/c)^2
* note: Hall not identified: the A4 experimental halls at MAMI are not located in any fetched source; placed at the institute's campus-grade site (site:mainz-kph-campus).
* note: Dates are partial and uncertain: January and September 2003 beam times are dated in a 2004 conference talk, the end is only bounded (before September 2018), and the start of the programme (1996, collaboration investigating strangeness) is dated by a 2007 thesis.
* note: Three results are recorded (2004, 2009, 2020); other A4 papers (Q^2 = 0.108 forward result, transverse-asymmetry papers of 2005 and 2017, deuterium result of 2016) are not.
* note: Official pages: the collaboration page and publication list are hosted by AG Maas, Johannes Gutenberg University Mainz; the page lists current and former members but states no start, end or status.

#### `experiment:happex`: HAPPEX (completed); kind hadron_structure; host facility:jefferson-lab; detector placed at `site:jlab-hall-a`; accelerators accelerator:cebaf

| interval | start | end | status | confidence | URL | verbatim quote |
|---|---|---|---|---|---|---|
| strange form factor programme (HAPPEX-I, HAPPEX-II and HAPPEX-He, HAP… | 1998 | 2009 | active | uncertain | https://arxiv.org/abs/nucl-ex/0402004 | Results were obtained in two separate data-taking runs, in 1998 and 1999 in Hall A at the Thomas Jefferson National Accelerator Facility (Jefferson Lab). |
| HAPPEX-I (1998 and 1999 runs) | 1998 | 1999 | active | verified | https://arxiv.org/abs/1207.5238 | The first generation HAPPEX experiment ran in 1998 and 1999 |
| HAPPEX-II and HAPPEX-He (2004 and 2005 runs) | 2004 | 2005 | active | verified | https://arxiv.org/abs/1207.5238 | The second generation HAPPEX experiments, HAPPEX-II and HAPPEXHelium took data in 2004 and 2005 |
| HAPPEX-III (2009 run) | 2009 | 2009 | active | verified | https://arxiv.org/abs/1207.5238 | with a data-taking run in 2009 |
| completed | 2009 | open | completed | uncertain | https://arxiv.org/abs/1207.5238 | with a data-taking run in 2009 |

* result `result:happex-i-ep-asymmetry-q2-0477-2000` (2000-06-06): A = -15.05 +- 0.98 (stat) +- 0.56 (syst) ppm at Q^2 = 0.477 (GeV/c)^2

* result `result:happex-ii-nucleon-strange-form-factors-2006` (2006-09-05): G_E^s = 0.002 +- 0.014 +- 0.007 at <Q^2> = 0.077 GeV^2

* result `result:happex-iii-strange-vector-form-factors-2011` (2011-07-05): A_PV = -23.80 +- 0.78 (stat) +- 0.36 (syst) ppm at Q^2 = 0.624 GeV^2
* note: One record covers the strange-form-factor programme (HAPPEX-I 1998-1999, HAPPEX-II and HAPPEX-He 2004-2005, HAPPEX-III 2009) as dated run intervals. The collaboration's later experiments PREX and PVDIS/MOLLER are separate records (experiment:prex, experiment:moller).
* note: Complementary to G0 and A4: the lineage rows live on the lexicographically smaller ids (experiment:a4-mami and experiment:g0).
* note: Run dates are year-level; no fetched source gives month-level run dates.
* note: Three results are recorded (HAPPEX-I 2000, HAPPEX-II/He 2006, HAPPEX-III 2011); other HAPPEX papers (arXiv:nucl-ex/9810012, nucl-ex/0402004, nucl-ex/0506010, nucl-ex/0506011) are not.

#### `experiment:g0`: G0 (completed); kind hadron_structure; host facility:jefferson-lab; detector placed at `site:jlab-hall-c`; accelerators accelerator:cebaf

| interval | start | end | status | confidence | URL | verbatim quote |
|---|---|---|---|---|---|---|
| installation and commissioning runs (first installed July-October 200… | 2002-07 | 2004-03 | commissioning | uncertain | https://arxiv.org/abs/1103.0761 | The G0 experiment was first installed in Hall C of Jefferson Lab during the period July 2002 to October 2002. |
| forward-angle production run (about March-May 2004) | 2004-03 | 2004-05 | active | verified | https://arxiv.org/abs/1103.0761 | The actual production runs for the forward angle measurement began about mid-March 2004 and continued until about May 2004 |
| installation of the backward-angle hardware | 2004-05 | 2006-03 | upgrade | uncertain | https://arxiv.org/abs/1103.0761 | Having completed the forward angle measurement, the new hardware for the back angle measurements was installed in Hall C, and commissioning and initial data-taking took place in March to May of 2006. |
| backward-angle commissioning and production (March 2006 to April 2007) | 2006-03 | 2007-04 | active | verified | https://arxiv.org/abs/1103.0761 | A long period of production running followed – including measurements with both hydrogen and deuterium targets, each at beam energies of 359 and 684 MeV – ending in April 2007. |
| completed | 2007-04 | open | completed | derived | https://arxiv.org/abs/1103.0761 | A long period of production running followed – including measurements with both hydrogen and deuterium targets, each at beam energies of 359 and 684 MeV – ending in April 2007. |

* result `result:g0-backward-angle-strange-quark-2009` (2009-09-28): Asymmetries on hydrogen and deuterium at Q^2 = 0.22 and 0.63 GeV^2

* result `result:g0-forward-angle-strange-quark-2005` (2005-06-17): Asymmetries measured over 0.12 < Q^2 < 1.0 GeV^2
* note: No website: the G0 collaboration page linked from the HAPPEX site (www.npl.illinois.edu/exp/G0/G0Main.html) returned HTTP 404 on 2026-10-26.
* note: Dates come from the operation history in the G0 apparatus paper (arXiv:1103.0761, section 8): installation July-October 2002, forward-angle production about mid-March to May 2004, backward-angle commissioning March-May 2006, production ending April 2007. The upgrade interval (new backward-angle hardware) is bounded by those dates, not separately dated.
* note: The 2005 forward-angle paper reported non-zero strange-quark contributions; the later HAPPEX-III result found the combined world data consistent with zero (see result:happex-iii-strange-vector-form-factors-2011).
* note: Complementary to HAPPEX and A4: the lineage rows live on the lexicographically smaller ids.

#### `experiment:prad`: PRad (completed); kind hadron_structure; host facility:jefferson-lab; detector placed at `site:jlab-hall-b`; accelerators accelerator:cebaf

| interval | start | end | status | confidence | URL | verbatim quote |
|---|---|---|---|---|---|---|
| PRad run (May-June 2016) | 2016-05 | 2016-06 | active | verified | https://arxiv.org/abs/2009.10510 | The PRad experiment was performed in Hall B at Jefferson Lab in May-June of 2016, using 1.1 GeV and 2.2 GeV electron beams. |
| completed | 2016-06 | open | completed | derived | https://arxiv.org/abs/2009.10510 | The PRad experiment completed in 2016, was the first high-precision |

* result `result:prad-proton-charge-radius-2019` (2019-11-06): r_p = 0.831 +- 0.007 (stat) +- 0.012 (syst) fm
* note: PRad-II (an upgraded proton-radius measurement, proposal arXiv:2009.10510 'approved by JLab PAC 48' per the arXiv comment) and the X17 search share the PRad collaboration wiki; they are not recorded here (for the integrator).
* note: Hall B placement is campus-grade (site:jlab-hall-b is the Hall B building footprint centroid); the PRad beam line and target position inside Hall B are not located in any fetched source.
* note: Run dates are those the collaboration gives in the PRad-II proposal (May-June 2016); no source fetched dates the proposal approval or earlier installation.

#### `experiment:slac-e158`: SLAC E158 (completed); kind electroweak_precision; host facility:slac; detector placed at `site:slac-menlo-park-campus`; accelerators accelerator:slac-linac

| interval | start | end | status | confidence | URL | verbatim quote |
|---|---|---|---|---|---|---|
| 2001 runs (spectrometer commissioning) | 2001-02 | 2002 | commissioning | uncertain | https://www.slac.stanford.edu/exp/e158/2001runs.html | Spectrometer Commissioning Plan -- first three days |
| data taking (three production runs, 2002 and 2003) | 2002 | 2003 | active | verified | https://arxiv.org/abs/hep-ex/0504049 | collected over three data runs in 2002 and 2003. |
| completed | 2003 | open | completed | derived | https://arxiv.org/abs/hep-ex/0403010 | E158 performed 3 physics runs in 2002 and 2003. |

* result `result:slac-e158-parity-nonconservation-moller-2004` (2003-12-10): A_PV = -175 +- 30 (stat) +- 20 (syst) ppb; electron weak charge Q_W^e = -0.053 +- 0.011

* result `result:slac-e158-weak-mixing-angle-2005` (2005-04-26): A_PV = -131 +- 14 (stat) +- 10 (syst) ppb
* note: Campus-grade placement: End Station A is not a separate site record, so the experiment's detector is placed at site:slac-menlo-park-campus (an approximate campus point of 2 km precision); the position of ESA inside the campus is not given by any fetched source.
* note: Successor: MOLLER at Jefferson Lab is the proposed improvement on this measurement (lineage row added on experiment:moller).
* note: Month-level run dates are not published in the fetched sources: the official site names '2002 spring run', '2002 fall run' and '2003 run' pages, and the proceedings state three physics runs in 2002 and 2003.
* note: The official site's main page is written in the future tense ('will use ... in a 5 month run') from before the runs; it is cited only for the beam and hall.
* note: The collaboration roster page (last modified 22 October 1999) lists CEA Saclay, Caltech, Kent State, Princeton, Smith College, SLAC, Syracuse, Jefferson Lab, UC Berkeley, UMass and Virginia.

#### `experiment:na34-helios`: HELIOS (NA34/2) (completed); kind heavy_ion; host facility:cern; detector placed at `site:cern-prevessin-north-area`; accelerators accelerator:sps

| interval | start | end | status | confidence | URL | verbatim quote |
|---|---|---|---|---|---|---|
| approval | 1984-11-15 | 1986 | approved | verified | https://greybook.cern.ch/api/experiments/search/experiment?name=NA34%2F2 | "approvalDate" : "15-11-1984" |
| ion-beam data taking (oxygen and sulphur beams) | 1986 | 1992 | active | uncertain | https://www.physi.uni-heidelberg.de/~specht/material/slides/HeavyIonPhysics_CERN_HJSpecht_8Sept2014.pdf | Beam times: first 16O 1986 first 32S 1987 last 32S 1992 Energies 60 and 200 AGeV |
| completed | 1992 | open | completed | uncertain | https://www.physi.uni-heidelberg.de/~specht/material/slides/HeavyIonPhysics_CERN_HJSpecht_8Sept2014.pdf | Beam times: first 16O 1986 first 32S 1987 last 32S 1992 Energies 60 and 200 AGeV |

* result `result:helios-transverse-energy-o-nucleus-1988` (1988-09): 
* note: Identity: HELIOS is the CERN experiment NA34. Hedberg's HELIOS page says it 'consisted of two fixed-target experiments at the SPS' (NA34/2, heavy ions; NA34/1, lepton production in hadronic interactions); Greybook lists NA34/2 with the synonym IONS/HELIOS (title 'Study of High Energy Densities over Extended Nuclear Volumes via Nucleus-Nucleus Collisions at the SPS'); Schukraft and Stock (arXiv:1505.06853) say NA34 '…
* note: Related but not recorded: HELIOS-3 (NA34/3, Greybook: 'Measurement of Low Mass Muon Pairs in Sulphur-Nucleus Collisions with an Optimized HELIOS Muon Spectrometer', approved 10 November 1988), the dimuon experiment that found the low-mass dimuon excess (Tserruya, arXiv:nucl-ex/9801007). It is a separate approved experiment and was not in the brief; listed for the integrator.
* note: Hall not identified: placed at the generic Prévessin North Area site (Greybook: beam H8).
* note: No collaboration website found (Greybook lists none). Heavy-ion papers of the HELIOS Collaboration are not on arXiv; the sources are Greybook, the Hedberg pages, Specht's 2014 slides and the 1988 and 1991 journal abstracts.
* note: CERES split off from HELIOS-3 to design a dedicated electron-pair experiment (arXiv:2603.10835, Section 3.1); no lineage row was written because that is a group split, not a predecessor relation.

#### `experiment:na35`: NA35 (completed); kind heavy_ion; host facility:cern; detector placed at `site:cern-neutrino-platform-ehn1`; accelerators accelerator:sps

| interval | start | end | status | confidence | URL | verbatim quote |
|---|---|---|---|---|---|---|
| proposal to the PS committee | 1982-01-26 | 1983-02-03 | proposed | verified | https://arxiv.org/abs/2603.08053 | The origins of the NA35 experiment at CERN can be traced back to a proposal [1] submitted by the GSI–LBL–Heidelberg–Marburg–Warsaw Collaboration to CERN’s Proton Synchrotron and Synchro-Cyclotron Com… |
| approval | 1983-02-03 | 1986 | approved | verified | https://greybook.cern.ch/api/experiments/search/experiment?name=NA35 | "approvalDate" : "03-02-1983" |
| data taking (light-ion beams at 60A and 200A GeV) | 1986 | 1992 | active | verified | https://arxiv.org/abs/2603.08053 | NA35 recorded data on collisions of p, d, 16 O, and 32 S beams at 60A GeV/c and 200A GeV/c with S, Ag, and Au targets from 1986 to 1992. |
| completed | 1992 | open | completed | verified | https://arxiv.org/abs/1505.06853 | NA35 was planned from 1981 onwards, and took SPS data from 1986 to 1992. |

* result `result:na35-strangeness-enhancement-s-s-1990` (1990-06): 
* note: Hall inferred: placed at the EHN1 site record because NA35 ran on the H2 beam line (Greybook: beam H2) and the NA61/SHINE Beams page says the H2 beam goes to Experimental Hall North 1; no fetched source names the NA35 hall directly (the same placement as NA49 and NA61/SHINE).
* note: Major components of the detector were inherited from the NA5 and NA24 experiments (arXiv:2603.08053); those experiments are not Atlas records.
* note: Successor: NA49 (the NA35 Collaboration initiated NA49 and NA49 replaced the streamer chamber by TPCs); the lineage row is on experiment:na49.
* note: The Greybook approval date (3 February 1983) is the original PS approval; the SPS first-generation approval was in November 1984 (Specht slides; Greybook status row). The approval interval keeps the Greybook experiment-level date.
* note: No membership, institution count or formation date was found; spokespersons per arXiv:2603.10835 were Reinhard Stock, then Peter Seyboth (Greybook lists Seyboth as spokesperson).

#### `experiment:na38`: NA38 (completed); kind heavy_ion; host facility:cern; detector placed at `site:cern-prevessin-north-area`; accelerators accelerator:sps

| interval | start | end | status | confidence | URL | verbatim quote |
|---|---|---|---|---|---|---|
| approval | 1985-09-12 | 1986 | approved | verified | https://greybook.cern.ch/api/experiments/search/experiment?name=NA38 | "approvalDate" : "12-09-1985" |
| data taking (proton, oxygen and sulphur beams) | 1986 | 1992 | active | uncertain | https://arxiv.org/abs/2603.10835 | It had started its data taking with oxygen beams in 1986 |
| completed | 1992 | open | completed | uncertain | https://arxiv.org/abs/hep-ph/0412158 | NA38 then collected a significantly larger sample of S+U events (see Table 7.2) |

* result `result:na38-jpsi-transverse-energy-dependence-o-u-1989` (1989-04-06): 
* note: Hall not identified: placed at the generic Prévessin North Area site (Greybook gives the beam line, H10, but no fetched source names the hall).
* note: NA38 reused the NA10 muon spectrometer (arXiv:2603.10835: 'built as a modest upgrade of the older NA10 experiment'); NA10 is not an Atlas record.
* note: NA50 followed NA38 (Specht 2014 slides, Tserruya 1998, arXiv:hep-ph/0412158); the lineage row (predecessor) is on experiment:na50.
* note: Spokesperson Louis Kluberg and contact person Peter Sonderegger (NA38 website, Greybook). No formation date or membership found.

#### `experiment:na44`: NA44 (completed); kind heavy_ion; host facility:cern; detector placed at `site:cern-prevessin-north-area`; accelerators accelerator:sps

| interval | start | end | status | confidence | URL | verbatim quote |
|---|---|---|---|---|---|---|
| approval | 1989-02-09 | 1992 | approved | verified | https://greybook.cern.ch/api/experiments/search/experiment?name=NA44 | "approvalDate" : "09-02-1989" |
| data taking (p, S and Pb beams) | 1992 | 1995 | active | uncertain | https://kaken.nii.ac.jp/en/grant/KAKENHI-PROJECT-03044102/ | we have accumulated a large amount of raw deta on 450-GeV proton-nucleus and 200-GeV/nucleon sulphur-nucleus collisions |
| completed | 1995 | open | completed | uncertain | https://web.archive.org/web/20140223084910/http://www.star.bnl.gov/~kopytin/thesis/node19.html | The data from the detector was used in the texture analysis of the hadron production (using the data recorded in 1994), and in the analysis of meson production in the collisions to normalize particle… |

* result `result:na44-particle-production-central-pb-pb-2002` (2002-02-21): 
* note: Start and end of data taking are not published in any fetched source: the start is an upper bound (by 1992) and the end a lower bound (1995), expressed as date ranges (earliest/latest); the status 'completed' is inferred.
* note: Hall not identified: placed at the generic Prévessin North Area site (Greybook: beam H4).
* note: Spokesperson Hans Bøggild (arXiv:2603.10835, Greybook); the NA44 Collaboration website lists members, institutions and publications behind a members-only page. No formation date or membership counts found.
* note: Related papers on arXiv (nucl-ex/9907013 strange meson enhancement, nucl-ex/9906006, nucl-ex/9808002, nucl-ex/9711004) were not used as sources.

#### `experiment:wa98`: WA98 (completed); kind heavy_ion; host facility:cern; detector placed at `site:cern-meyrin`; accelerators accelerator:sps

| interval | start | end | status | confidence | URL | verbatim quote |
|---|---|---|---|---|---|---|
| approval | 1992-04-16 | 1994 | approved | verified | https://greybook.cern.ch/api/experiments/search/experiment?name=WA98 | "approvalDate" : "16-04-1992" |
| data taking (Pb beam) | 1994 | 1996 | active | verified | https://arxiv.org/abs/nucl-ex/0108006 | The experiment took data with the 158·A GeV 208 Pb beams from the SPS in 1994, 1995, and 1996. |
| completed | 1996 | open | completed | verified | https://arxiv.org/abs/nucl-ex/0108006 | The layout of the WA98 experiment as it existed during the final WA98 run period in 1996 |

* result `result:wa98-direct-photons-central-pb-pb-2000` (2000-06-13): 
* note: Hall not identified: the experiment sat in the SPS West Area (WA designation; it used the Goliath magnet, which stood in the West Area until it moved to the North Area for NA57). The placement is the existing campus-level site:cern-meyrin (500 m precision), which is not a hall position, as for WA97.
* note: WA98 followed WA80 and WA93 (section title of arXiv:2603.10835, 'Experiments WA80 to WA93 to WA98'; Specht slides: 'followed WA80'); WA80 and WA93 are not Atlas records, so no lineage row was written.
* note: Approval: Greybook says 16 April 1992, the 2014 Specht slides say 1991; Greybook is used.
* note: Spokespersons: Hans Gutbrod, then Terry Awes from 1997 (arXiv:2603.10835). No formation date or membership found.

## Task 4: deferred collider candidates (owner `colliders-2`)

Full per-entity tables, conflicts, unresolved fields and exclusions: `docs/atlas-worklog/FOLLOWUPS_2_colliders.md`. Summary:

* **Added:** `accelerator:adone` (collider, 1969 to 26 April 1993, 3.0 GeV centre-of-mass design energy, a dated November 1974 phase at about 3.1 GeV) with seven experiments (Gamma-Gamma, Mu-Pion, Boson, BCF, Gamma-Gamma 2, MEA, Baryon-Antibaryon) and FENICE (1990 to 1993); FINUDA, DEAR, SIDDHARTA, SIDDHARTA-2 (DAPHNE, kaonic atoms and hypernuclei, filed `hadron_structure`) and PADME (`fixed_target`); `accelerator:sctf` (BINP, from the 2018 conceptual design report, which names BINP) and `accelerator:stcf` with `facility:stcf-hefei` and `site:stcf-hefei-future-big-science-city` (the STCF design reports and project talks name Hefei's Future Big Science City; the site marker is an area point of about 5 km precision, and the STCF tunnel site is not selected). 15 experiments, 15 detectors, 13 collaborations, 8 results, 43 sources, 15 registry rows.
* **Excluded:** the first-generation ADONE and FENICE results (the Elsevier abstracts return HTTP 403), LADON, Jet Target, PULS and PWA at ADONE, AMADEUS, an SCTF collaboration record (none exists in the sources), and a detector placement for the STCF experiment (the area marker would add an A23 notice; the experiment is hosted by `facility:stcf-hefei`).
* **Weak spots:** ADONE experiment ends are derived (1978); three second-generation experiments have an `uncertain` start (1974, the latest possible); SCTF's status after 2020 was not found.

## Conflicts

| claim | source A | source B | chosen | why |
|---|---|---|---|---|
| Tevatron Run II start | Vellidis (DPF 2015, existing record): "from 2002 through 2011 (Run II)" | Shiltsev (arXiv:1109.1864): "Run II was initiated in March of 2001 and continued through September 2011." | March 2001 | the accelerator physicist's account of the machine; both give 1.96 TeV |
| Tevatron start of collider operation | Shiltsev abstract: "beginning operation in December of 1985" | Fermilab timeline and the 23 October 1985 FermiNews: first collisions on 13 October 1985 at 1.6 TeV | both: the 1985-12 collider interval is kept; the 13 October event is a one-day engineering-test era | the October event preceded the year-long shutdown; the machine then ran fixed-target for two years (Holmes, arXiv:1109.2937) |
| PETRA as HERA's pre-accelerator | DESY anniversary page: "starting in 1986, as a preaccelerator" | Bethke and Wagner: shutdown as collider in November 1986, "came back to life in 1990 as PETRA-II ... pre-accelerator ... until 2007" | 1990 to 2007 | the paper dates the rebuilding; 1986 is the collider shutdown |
| LEP 1999 top energy | DELPHI abstract: "between 192 and 200 GeV during 1999" | Ferrer Ribas, L3 and the LEP combination: 192 to 202 GeV | 202 GeV | three sources; DELPHI's sentence is about its own sample |
| LEP 1995 energy | the strong-coupling review: 133 GeV | OPAL abstract: data at 130 and 136 GeV | 136 GeV (highest), display names 130 and 136 | 133 is the average of the two points |
| CEBAF design energy | Freyberger (IPAC 2015): "designed for 4 GeV", "three times the original design energy of 4 GeV" | Pilat (LINAC 2012): "Designed for a maximum energy of 6 GeV" | 4 GeV for the 1995 era; both noted | the later paper is by the project's commissioning team; the 6 GeV was reached in 2000 |
| CEBAF 6 GeV start | old record (encyclopaedia): 6 August 2000 | Freyberger: "established in 2000" | 2000, year precision | no non-encyclopaedic source gives the day |
| HERA 1998 energy step | Klein and Yoshida: proton energy 820 to 920 GeV in 1998, "about 320 GeV" | H1 and a HERA review abstract: 300 GeV (820 GeV protons) and "300-318 GeV" | 300 GeV (1992 to 1998), 318 GeV (derived, from 1998) | 2 sqrt(27.5 x 920) = 318 GeV |

The hadron and collider conflicts (approval dates of NA38, WA98 and NA35, ADONE dates, STCF coordinates and others) are in the per-record notes and in `FOLLOWUPS_2_colliders.md`.

## Unresolved (left empty, not guessed)

* `accelerator:hesr` (see Task 1): a current FAIR status and any date.
* Era energies not done because no source read dates the change: **SPEAR** (4.8 GeV "in the first few years", then up to about 8 GeV; the date of the step is not stated), **ISR** (first-collision energy and the step to 31.4 GeV/c), **PETRA** (no headline `cms_energy`; the yearly energies 13 to 46.8 GeV were not sourced), **TRISTAN** (50 to 64 GeV; no headline `cms_energy`), **DORIS**, **CESR**, **BEPC**, **PEP**; the HERA 2007 low-energy runs (460 and 575 GeV protons; their centre-of-mass energies are not stated in the sources read); RHIC proton-proton 500 GeV from 2009 and the Beam Energy Scan.
* CEBAF: the date of the first 12 GeV electrons: the JLab news item reports "Dec. 14" (12.065 GeV to Hall D) but prints no year, so the 12 GeV era starts at the review's "Since 2016" (year precision); the 1987, 1994 and 2018 CEBAF intervals still rest on an encyclopaedia entry.
* Tevatron: the energy of the February to May 1987 run (not stated in the sources read, so it sits inside the 1.8 TeV era without its own value).
* EIC: the start of operations (the AGS link uses the 2023 ePIC expectation, 2032).
* Hadron and collider records: month-level run dates, hall coordinates (all placed at campus-grade sites), membership counts, INSPIRE experiment ids (inspirehep.net not contacted), see each record's registry `missing_fields`.

## Candidates considered and excluded

* `accelerator:hesr` (above); DORIS to PETRA feed (above).
* From the hadron brief: NA60+ (proposed successor; not in the list), HELIOS-3 (NA34/3, the dimuon experiment: a separate approved experiment, left for a later pass), PRad-II and the PRad X17 search (not recorded).
* From the collider brief: see `FOLLOWUPS_2_colliders.md` ("Candidates considered and excluded").

## For the integrator

* **ID registry:** the new ids are appended to `docs/atlas-worklog/ID_REGISTRY.md`.
* **Tests:** `tests/test_atlas_charts.py` pins the chart points of LEP, the Tevatron, CEBAF, HERA, RHIC and the LHC; they change if a record is edited.
* **Tour:** one claim of `tour:higgs-hunt` was split in two (the Tevatron energy and the Run II dates) because the Run II start moved from 2002 to March 2001.
* **Schema note:** `kind` on an interval decides whether it sets the lifecycle state (no `kind`) or annotates it (`phase`, `run`). Era energies on `phase`/`run` intervals are safe for the chart; an era that must also be the machine's state (CEBAF) is a plain interval.
* **Sources:** no `rank` was written on new source records (it is derived and warns `A1` otherwise).
* **HERA footnote:** the chart will footnote HERA's 320 GeV headline (no era dates it); set the headline to 318 GeV if a plain point is preferred.
* **Open for later streams:** `experiment:panda` still has no accelerator (needs `accelerator:hesr`); the SPEAR, ISR, PETRA and TRISTAN era energies above.

## Checks

* `python -m hepgraph.atlas.validate`: `0 errors, 1818 warnings, 50 informational`, identical to the baseline of the branch point (the diff of the sorted output is empty: no new warning from any record of this stream; the new source records carry no `rank`).
* Quote checker (`scripts/atlas_quote_check.py`, live pages, one cache): run per record set after its last edit, with one shared cache. Accelerator records: `lep` 22 verbatim, `fermilab-tevatron` 16, `cebaf` 12, `hera` 13, `rhic` 14 verbatim and 1 segments (a pre-existing RHIC quote that elides text with "..."), `lhc` 18, `slac-linac` 6, `petra` 9, `ags` 8; no number flag on any quote of this stream (the flags that remain on `rhic` and `slac-linac` are older quantities: the RHIC circumference and the linac length). Hadron records (10 experiments, detectors, collaborations, results, the three lineage edits): every quote `verbatim`, 0 number flags (A4 21, HAPPEX 31, G0 24, PRad 20, E158 26, HELIOS 15, NA35 23, NA38 19, NA44 19, WA98 19, results 8+6+2+9+3+6+2+2+2+2, MOLLER 10, NA49 7, NA50 7). Collider records (56 files): 251 `verbatim`, 1 `skipped` (the geocoder coordinate of the STCF area marker), nothing else. The Fermilab and jlab.org hosts rate-limit or block repeated fetches (HTTP 403 and 429): a full re-run over all 117 changed record files was started at the end and stopped after 24 files, all `verbatim` except the one pre-existing RHIC item above, because the refetches were being throttled; the per-set runs above are the evidence.
* `python -m hepgraph.atlas.build`: `wrote 84 file(s) to static/atlas/generated (version dc72538fec7e47aa, removed 0 stale file(s))`; the size warning (2.0 MB against the 400 kB pilot budget) predates this stream. The generated files were reverted (`git checkout -- static/atlas/generated`) and the untracked build outputs removed before committing.
* `python -m pytest -q`: `774 passed, 139 skipped in 89.89s` (the skips need a PostgreSQL test database).

