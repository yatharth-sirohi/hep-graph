# neutrino-2 worklog, part 2 (coverage wave: the 23 queued neutrino, nucleon-decay, double-beta and direct-mass candidates)

Branch `atlas-c4b-neutrino`, worktree `~/Desktop/HEP-Graph-ar-c4b-neutrino`, from the integration branch at `000c601`. Owner tag `neutrino-2`; the rows live in `data/atlas/coverage/neutrino-2.json` (updated in place). Part 1 of this wave is [NEUTRINO_2.md](NEUTRINO_2.md): its "Not done" list is this stream's brief.

## Scope and outcome

All 23 queued `researched: "none"` rows are now written to the mandatory bar (experiment, detector, a collaboration record where one exists, a located site on a facility, sourced and dated intervals, topics, summaries, at least one authoritative source, lineage where a source states it, a headline result record with an abstract quote, and the registry row). **None was excluded.** Two have no collaboration record (CUORICINO and Mainz: no source names one; PandaX-III reuses `collaboration:pandax-4t`). All are tier D, `researched: partial` for the experiment and `full` for the result records.

| type | new records |
|---|---|
| experiments | 23 |
| detectors | 24 (Kolar Gold Fields has a Phase I and a Phase II detector) |
| collaborations | 20 |
| results | 32 |
| facilities | 6: `facility:mont-blanc-laboratory`, `facility:kolar-gold-fields-underground-laboratory`, `facility:johannes-gutenberg-university-mainz`, `facility:inr-troitsk`, `facility:kirchhoff-institute-for-physics` (Heidelberg, ECHo), `facility:university-of-milano-bicocca` (HOLMES) |
| sites | 8: `site:baksan-bust-hall`, `site:inr-troitsk-nu-mass-facility`, `site:kamioka-candles-lab-d`, `site:kirchhoff-institute-for-physics-heidelberg`, `site:kolar-gold-fields-mines`, `site:mainz-institute-of-physics`, `site:milano-bicocca-university-campus`, `site:mont-blanc-tunnel-laboratory` |
| sources | 96 (6 are geocoder records; none from inspirehep.net, Wikipedia or cds.cern.ch) |

| experiment | kind (secondary) | status | first / latest interval start | placement site | results |
|---|---|---|---|---|---|
| `experiment:chorus` | accelerator_neutrino | completed | 1993 to 1997 | `site:cern-meyrin` | `chorus-final-numu-nutau-2007` |
| `experiment:nomad` | accelerator_neutrino | completed | end of 1991 to end of 1998 | `site:cern-meyrin` | `nomad-final-oscillation-limits-2001` |
| `experiment:cdhs` | accelerator_neutrino | completed | 1976-12 to 1984 | `site:cern-meyrin` | `cdhs-total-cc-cross-sections-1987` |
| `experiment:charm` | accelerator_neutrino | completed | 1977 to 1984-09-03 | `site:cern-meyrin` | `charm-structure-functions-1983` |
| `experiment:charm-ii` | accelerator_neutrino (electroweak_precision) | completed | 1983 to 1991-08-12 | `site:cern-meyrin` | `charm-ii-electroweak-parameters-1994` |
| `experiment:jsns2` | accelerator_neutrino | active | 2013-09 to 2021-01-12 | `site:j-parc-mlf` | `jsns2-first-sterile-search-2026` |
| `experiment:ccm` | accelerator_neutrino (cevns) | active | Fall 2019 to 2022 | `site:lanl-lansce` | `ccm-cherenkov-event-by-event-2025`, `ccm-first-leptophobic-dm-search-2021` |
| `experiment:frejus` | nucleon_decay (atmospheric_neutrino) | completed | 1982 to 1988-09-13 | `site:lsm-frejus` | `frejus-atmospheric-neutrino-oscillation-limits-1990`, `frejus-bl-violating-nucleon-decay-limits-1991`, `frejus-nucleon-decay-charged-lepton-limits-1991` |
| `experiment:nusex` | nucleon_decay (atmospheric_neutrino) | completed | 1980 to between March 1985 and July 2004; end of data taking not stated in any source consulted | `site:mont-blanc-tunnel-laboratory` | `nusex-atmospheric-neutrino-flux-1989`, `nusex-nucleon-decay-candidate-1983` |
| `experiment:soudan-2` | nucleon_decay (atmospheric_neutrino) | completed | 1989-04 to 2001-06 | `site:soudan-minos-far-detector` | `soudan-2-atmospheric-neutrino-oscillations-2003`, `soudan-2-nucleon-decay-lepton-k0-limits-1999` |
| `experiment:macro` | cosmic_ray (atmospheric_neutrino) | completed | 1989-03 to 2000-12 | `site:lngs-hall-b` | `macro-atmospheric-nu-oscillation-global-analysis-2004`, `macro-final-monopole-limit-2002` |
| `experiment:baksan-underground-scintillation-telescope` | cosmic_ray (astrophysical_neutrino,atmospheric_neutrino) | active | 1978 to 1978 | `site:baksan-bust-hall` | `baksan-bust-neutrino-burst-limit-2019` |
| `experiment:kolar-gold-fields-experiments` | nucleon_decay (atmospheric_neutrino,cosmic_ray) | completed | 1960 to 1993 | `site:kolar-gold-fields-mines` | `kgf-first-atmospheric-neutrinos-1965`, `kgf-proton-decay-claim-2000` |
| `experiment:heidelberg-moscow` | double_beta_decay | completed | 1990-08 to 2003-05 | `site:lngs-hall-a` | `heidelberg-moscow-evidence-claim-2001`, `heidelberg-moscow-majorana-mass-limit-1999` |
| `experiment:nemo-3` | double_beta_decay | completed | 2003-02 to 2010-12 | `site:lsm-frejus` | `nemo-3-mo100-final-limit-2015` |
| `experiment:supernemo-demonstrator` | double_beta_decay | active | 2018-11 to 2025-04-10 | `site:lsm-frejus` | `supernemo-demonstrator-calorimeter-commissioning-2024` |
| `experiment:candles` | double_beta_decay | active | Spring 2013 to Spring 2013 | `site:kamioka-candles-lab-d` | `candles-iii-low-background-48ca-2020` |
| `experiment:cuoricino` | double_beta_decay | completed | 2003-04 to 2008-06 | `site:lngs-hall-a` | `cuoricino-130te-final-limit-2010` |
| `experiment:pandax-iii` | double_beta_decay | construction | 2016-10 to 2016-10 | `site:cjpl-ii` | `pandax-iii-status-final-detector-constructed-2023` |
| `experiment:mainz-neutrino-mass` | neutrino_mass | completed | 1991 to 2001 | `site:mainz-institute-of-physics` | `mainz-final-neutrino-mass-limit-2004` |
| `experiment:troitsk-nu-mass` | neutrino_mass | active | 1985 to 2017-03 | `site:inr-troitsk-nu-mass-facility` | `troitsk-kev-sterile-neutrino-limits-2017`, `troitsk-neutrino-mass-limit-2011` |
| `experiment:echo` | neutrino_mass | active | 2013-06 to 2023-01 | `site:kirchhoff-institute-for-physics-heidelberg` | `echo-1k-neutrino-mass-limit-2025` |
| `experiment:holmes` | neutrino_mass | active | 2013 to 2025-03 | `site:milano-bicocca-university-campus` | `holmes-neutrino-mass-limit-2025` |

Kinds: the brief's `nucleon_decay` was kept where nucleon decay is the primary goal (Fréjus, NUSEX, Soudan 2, Kolar Gold Fields). MACRO and the Baksan telescope are `cosmic_ray` (their papers describe them as multipurpose cosmic-ray detectors, with monopole searches and neutrino bursts as the headline physics; there is no monopole kind), with the neutrino kinds as secondary kinds. The registry rows' `category` was updated to the experiment kind where it differed (MACRO, Baksan, Soudan 2, Fréjus, NUSEX, KGF).

## Method

- A helper library (in the session scratch directory, lost when it is cleared) fetched every cited source today and refused to write any `quote` that was not verbatim in it (the normaliser of `scripts/atlas_quote_check.py`); it also created source records with URL de-duplication under a lock, so parallel workers could not make two sources with one URL.
- The lead wrote the helper, then ran five forks of itself in parallel on disjoint experiments (F1 CERN West Area; F2 JSNS2, CCM, MACRO, Soudan 2, Baksan; F3 Fréjus, NUSEX, KGF; F4 double-beta decay; F5 direct neutrino mass). The forks wrote records and logs; the lead committed, applied the registry rows, made the integrator edits below, and reviewed the output. Parts 1 to 5 below are the forks' logs with their "For the integrator" and "Checks run" sections folded into the consolidated sections at the end.
- Review by the lead after the forks finished (a second reading of the output, not a re-research): the quote check was re-run over every new file (523 quotes, all verbatim, no number flags); every new summary, `why_it_matters` and claim was read; a script flagged every interval bound whose year or month is missing from its quote (the flagged rows were chained boundaries, dated news items or approximate rows with a note; none was found wrong); every superlative in a new text was traced to the source.

## Corrections made by the lead after reading the forks' output

- **Three result claims were truncated mid-sentence** (`result:frejus-bl-violating-nucleon-decay-limits-1991`, `result:macro-final-monopole-limit-2002`, `result:soudan-2-nucleon-decay-lepton-k0-limits-1999`): the A16 claim quote now carries the full sentence with its limit (each re-checked verbatim).
- **Superlatives not supported by the cited text were removed or scoped.** HOLMES's 27 eV bound was described as "the best for this method so far", which the Atlas's own ECHo-1k record (15 eV, arXiv:2509.03423, September 2025) contradicts; the HOLMES paper's own wording ("the most stringent upper bound ... ever obtained with a calorimetric measurement of 163Ho", March 2025) is now stated as dated to its time and the ECHo result is named. NOMAD's "tightest limit from any experiment" became the paper's own wording ("significantly more stringent than the previously published limits"); CHORUS's "most stringent ... emulsion" claim, the Mainz and Troitsk "best direct limit of its time" claims (not in the cited papers) and CCM's "first dark-sector limit from a liquid-argon detector at Lujan" were rewritten to what the sources state.

## Edits to existing records (the earlier stream's "For the integrator" list, and related)

| record | edit | source |
|---|---|---|
| `experiment:double-chooz` | added lineage `{experiment:chooz, predecessor}` | `src:geo-chooz-dc-tdr-2006` (hep-ex/0606025): "Installation of the experiment will start with the far detector located at the former experimental site of the CHOOZ experiment." |
| `facility:chooz` | added an interval "hosting the CHOOZ neutrino experiment (reactor-neutrino site)" starting 1997-03-12, `approximate`, open; this clears the `experiment-before-facility` warning for CHOOZ. The idle years 1998-2011 are not documented (noted) | `src:chooz-hepex0301017`: "The data acquisition period extended over 450 days, from 12 March 1997 till 20 July 1998" |
| `experiment:juno` | added lineage `{experiment:juno-tao, same_program}` (the row lives on the lexicographically smaller id) | `src:juno-tao-cdr-2020` (arXiv:2005.08745): "The Taishan Antineutrino Observatory (TAO, also known as JUNO-TAO) is a satellite experiment of the Jiangmen Underground Neutrino Observatory (JUNO)." |
| `result:neos-reno-joint-sterile-search-2022` | `experiment:reno` is now an `{id, sources}` row; `collaboration:reno` and `detector:reno` added | `src:neos-prd-2022-neos-ii`: title "Search for sterile neutrino oscillation using RENO and NEOS data" and the author line "(The RENO and NEOS Collaborations)" |
| `experiment:cuore`, `experiment:cupid`, `experiment:gerda`, `experiment:legend`, `experiment:majorana-demonstrator`, `experiment:exo-200`, `experiment:nexo` | backwards or derived-type lineage rows repaired (F4; only `lineage` changed): CUORE now has CUORICINO as predecessor, CUPID has CUORE as predecessor and `upgrade_of`; GERDA has Heidelberg-Moscow as predecessor; LEGEND has GERDA and Majorana as predecessors; nEXO has EXO-200 as predecessor; the backwards rows on Majorana and EXO-200 were removed. `experiment:nexo` was outside the brief's list and was edited so no false row remained | see Part 4, "Lineage edits", for each quote |
| `experiment:katrin` | added lineage `{mainz-neutrino-mass, predecessor}` and `{troitsk-nu-mass, predecessor}` (F5; only `lineage` and one record-level source changed) | `src:mainz-neutrino-mass-hep-ex0412056`: "It combines the expertise from the foregoing experiments at Los Alamos [72], Mainz and Troitsk with the strength of a national laboratory ..." |
| `facility:soudan-underground-laboratory`, `facility:baksan-neutrino-observatory` | an earlier sourced interval each (Soudan 2 from 1989-04; the Baksan telescope from 1978); the Baksan file was rewritten in canonical form (large textual diff, content change limited to `intervals` and `sources`) | Parts 2 |
| `experiment:imb`, `result:imb-3-nucleon-decay-limits-1999` | `topic:nucleon-decay` added (IMB's 1999 result is a nucleon-decay limit, and the topic was unused) | the existing record-level sources of the IMB record |

`topic:nucleon-decay` is now used by Fréjus, NUSEX, Soudan 2, Kolar Gold Fields and IMB. Its parent stays `topic:precision-and-rare-processes` (see Part 1's log, "For the integrator").

## Part 1 (F1): CERN SPS West Area neutrino experiments (CHORUS, NOMAD, CDHS, CHARM, CHARM II)

Owner tag `neutrino-2`. Five experiments done to the mandatory bar (experiment, detector, collaboration, one headline result with an abstract quote, located site on `facility:cern`, dated intervals with quotes, registry row). No new facility, accelerator, beamline or site: all five detectors are placed at the existing campus-grade `site:cern-meyrin` as `approximate` (no fetched source locates the SPS West Area halls). `accelerator:sps` is listed on every experiment. Records were written through the helper library, which refused any quote that was not verbatim in the cited source's fetched text; `scripts/atlas_quote_check.py --only` (chorus, nomad, cdhs, /charm) then classified all 101 quotes as verbatim, 0 number flags. Validator: no finding of any kind on these records (the only global error at the time, `alias-equals-name` on `experiment:heidelberg-moscow`, belongs to another fork).

### Entities written

| id | type | status | start / end per interval (confidence) | site | URL and quote behind each date |
|---|---|---|---|---|---|
| experiment:chorus | experiment | completed | first operation (CERN Courier: began operation in 1993): 1993 / 1994 [commissioning, approximate]; data taking: 1994 / 1997 [active, verified]; completed: 1997 / - [completed, approximate] | site:cern-meyrin (via detector placement; facility:cern) | https://cerncourier.com/a/neutrinos-stop-going-west/ — "With the West Area well served with muon neutrinos, specialized detectors (NOMAD using kinematic techniques, and CHORUS using nuclear emulsion to observe the final state tau leptons) began operation in 1993."<br>https://arxiv.org/abs/0710.3361 — "The CHORUS experiment took data from 1994 to 1997."<br>https://arxiv.org/abs/0710.3361 — "The CHORUS experiment took data from 1994 to 1997." |
| detector:chorus-detector | detector | completed | placement main 1993 / 1997 [approximate] | site:cern-meyrin | https://cerncourier.com/a/neutrinos-stop-going-west/ — "With the West Area well served with muon neutrinos, specialized detectors (NOMAD using kinematic techniques, and CHORUS using nuclear emulsion to observe the final state tau leptons) began operation in 1993." |
| collaboration:chorus | collaboration | completed | follows the experiment's intervals; formation null | site:cern-meyrin | (intervals copy the experiment's quotes) |
| experiment:nomad | experiment | completed | approved: 1991-12 (approx; end of 1991) / 1993 [approved, approximate]; first operation (CERN Courier: began operation in 1993): 1993 / 1995 [commissioning, approximate]; data taking: 1995 / 1998 [active, verified]; completed: 1998-12 (approx; end of 1998) / - [completed, approximate] | site:cern-meyrin (via detector placement; facility:cern) | https://library.cern/archives/CERN_archive/guide/experimental_physics/SPS/isanomad — "NOMAD (Neutrino Oscillation MAgnetic Detector) or WA96 located in the West Area of SPS experiment was approved at the end of 1991."<br>https://cerncourier.com/a/neutrinos-stop-going-west/ — "With the West Area well served with muon neutrinos, specialized detectors (NOMAD using kinematic techniques, and CHORUS using nuclear emulsion to observe the final state tau leptons) began operation in 1993."<br>https://arxiv.org/abs/hep-ex/0106102 — "From 1995 to 1998 the experiment has collected 1 040 000 events with an identified muon, corresponding to about 1 350 000 νµ CC interactions" |
| detector:nomad-detector | detector | completed | placement main 1993 / 1998 [approximate] | site:cern-meyrin | https://library.cern/archives/CERN_archive/guide/experimental_physics/SPS/isanomad — "NOMAD (Neutrino Oscillation MAgnetic Detector) or WA96 located in the West Area of SPS experiment was approved at the end of 1991." |
| collaboration:nomad | collaboration | completed | follows the experiment's intervals; formation null | site:cern-meyrin | (intervals copy the experiment's quotes) |
| experiment:cdhs | experiment | completed | data taking: 1976-12 / 1984 [active, verified]; completed: 1984 / - [completed, approximate] | site:cern-meyrin (via detector placement; facility:cern) | https://web.archive.org/web/20210419090153/https://knobloch.web.cern.ch/CDHS/cdhs.html — "The experiment took data in the CERN neutrino beams from December 1976 until 1984."<br>https://web.archive.org/web/20210419090153/https://knobloch.web.cern.ch/CDHS/cdhs.html — "The experiment took data in the CERN neutrino beams from December 1976 until 1984." |
| detector:cdhs-detector | detector | completed | placement main 1976-12 / 1984 [approximate] | site:cern-meyrin | https://web.archive.org/web/20210419090153/https://knobloch.web.cern.ch/CDHS/cdhs.html — "The CDHS neutrino experiment at CERN was a collaboration of CERN, Dortmund, Heidelberg and Saclay (later joined by Warsaw) led by Jack Steinberger." |
| collaboration:cdhs | collaboration | completed | follows the experiment's intervals; formation null | site:cern-meyrin | (intervals copy the experiment's quotes) |
| experiment:charm | experiment | completed | proposal accepted: 1977 / 1978 [approved, approximate]; data taking (WA18): 1978 / 1984-09-03 [active, verified]; completed: 1984-09-03 / - [completed, verified] | site:cern-meyrin (via detector placement; facility:cern) | https://library.cern/archives/CERN_archive/guide/experimental_physics/SPS/isacharm — "In 1977 the proposal of the CHARM Collaboration (CERN-Hamburg-Amsterdam-Rome-Moscow Collaboration) to study semi-leptonic neutral current processes and muon polarization produced in neutrino and antineutrino interactions was accepted by the Experimental Physics (EP) Division."<br>https://library.cern/archives/CERN_archive/guide/experimental_physics/SPS/isacharm — "WA18: The data-taking of this SPS experiment began in 1978. WA18 started running with the complete apparatus in 1979, and was completed on the 3rd September 1984."<br>https://library.cern/archives/CERN_archive/guide/experimental_physics/SPS/isacharm — "WA18: The data-taking of this SPS experiment began in 1978. WA18 started running with the complete apparatus in 1979, and was completed on the 3rd September 1984." |
| detector:charm-detector | detector | completed | placement main 1978 / 1984-09-03 [approximate] | site:cern-meyrin | https://library.cern/archives/CERN_archive/guide/experimental_physics/SPS/isacharm — "WA18: The data-taking of this SPS experiment began in 1978." |
| collaboration:charm | collaboration | completed | follows the experiment's intervals; formation null | site:cern-meyrin | (intervals copy the experiment's quotes) |
| experiment:charm-ii | experiment | completed | preparation and setting-up (WA79): 1983 / 1986 [construction, approximate]; data taking (WA79): 1986 / 1991-08-12 [active, verified]; completed: 1991-08-12 / - [completed, verified] | site:cern-meyrin (via detector placement; facility:cern) | https://library.cern/archives/CERN_archive/guide/experimental_physics/SPS/isacharm — "CHARM 2 (Brussels IIHE-CERN-Hamburg-Louvain-Moscow-Munich-Naples-Rome Collaboration) experiments WA79: The preparation of this experiment began in 1983."<br>https://library.cern/archives/CERN_archive/guide/experimental_physics/SPS/isacharm — "The data-taking began in 1986. WA79 was completed on the 12th August 1991."<br>https://library.cern/archives/CERN_archive/guide/experimental_physics/SPS/isacharm — "The data-taking began in 1986. WA79 was completed on the 12th August 1991." |
| detector:charm-ii-detector | detector | completed | placement main 1986 / 1991-08-12 [approximate] | site:cern-meyrin | https://library.cern/archives/CERN_archive/guide/experimental_physics/SPS/isacharm — "The data-taking began in 1986. WA79 was completed on the 12th August 1991." |
| collaboration:charm-ii | collaboration | completed | follows the experiment's intervals; formation null | site:cern-meyrin | (intervals copy the experiment's quotes) |
| result:cdhs-total-cc-cross-sections-1987 | result | measurement | 1987-12 (publication) | - | https://link.springer.com/article/10.1007/BF01596895 — "Neutrino and antineutrino total charged current cross sections on iron were measured in the 100, 160, and 200 GeV narrow band beams at the CERN SPS in the energy range 10 to 200 GeV." |
| result:charm-ii-electroweak-parameters-1994 | result | precision_measurement | 1994 (publication) | - | https://iris.uniroma1.it/handle/11573/247020 — "We report final results on electroweak parameters from muon-neutrino electron scattering observed in the CHARM II detector from 1987 till 1991." |
| result:charm-structure-functions-1983 | result | measurement | 1983 (publication) | - | https://iris.uniroma1.it/handle/11573/242735 — "Inclusive neutrino and antineutrino charged current interactions were studied in the CHARM detector exposed to neutrino and antineutrino Wide Band Beams of the CERN 400 GeV SPS." |
| result:chorus-final-numu-nutau-2007 | result | limit | 2007-10-17 (preprint) | - | https://arxiv.org/abs/0710.3361 — "In a two-neutrino mixing scheme, a 90% C.L. upper limit of sin2 2θµτ < 4.4 × 10−4 is set for large ∆m2 , improving by a factor 1.5 the previously published CHORUS result." |
| result:nomad-final-oscillation-limits-2001 | result | limit | 2001-06-29 (preprint) | - | https://arxiv.org/abs/hep-ex/0106102 — "The "blind analysis" of all topologies yields no evidence for an oscillation signal." |

Collaboration records follow the experiment intervals (relabelled "collaboration ..."); `formation` is null with a note everywhere (no source dates a formation). Results use `coverage.researched: full`, experiments, detectors and collaborations `partial`, tier D.

### Sources added

| id | type | URL |
|---|---|---|
| `src:cdhs-hep-ex9707015` | arxiv | https://arxiv.org/abs/hep-ex/9707015 |
| `src:cdhs-knobloch-page-wayback` | official_experiment_site | https://web.archive.org/web/20210419090153/https://knobloch.web.cern.ch/CDHS/cdhs.html |
| `src:cdhs-zphysc-1987-total-cc-cross-sections` | journal_article | https://link.springer.com/article/10.1007/BF01596895 |
| `src:cern-wa-1103-4572` | arxiv | https://arxiv.org/abs/1103.4572 |
| `src:cern-wa-courier-neutrinos-stop-going-west-1998` | press_release | https://cerncourier.com/a/neutrinos-stop-going-west/ |
| `src:charm-cern-archives-guide` | official_facility_site | https://library.cern/archives/CERN_archive/guide/experimental_physics/SPS/isacharm |
| `src:charm-ii-iris-1994-electroweak-parameters` | institution_page | https://iris.uniroma1.it/handle/11573/247020 |
| `src:charm-iris-1983-structure-functions` | institution_page | https://iris.uniroma1.it/handle/11573/242735 |
| `src:chorus-0710-3361` | arxiv | https://arxiv.org/abs/0710.3361 |
| `src:chorus-hep-ex0206006` | arxiv | https://arxiv.org/abs/hep-ex/0206006 |
| `src:nomad-cern-archives-guide` | official_facility_site | https://library.cern/archives/CERN_archive/guide/experimental_physics/SPS/isanomad |
| `src:nomad-hep-ex0106102` | arxiv | https://arxiv.org/abs/hep-ex/0106102 |

`src:cdhs-knobloch-page-wayback` is an Internet Archive capture (19 Apr 2021) of the CDHS member J. Knobloch's CERN page; the live host `knobloch.web.cern.ch` no longer resolves. The two `institution_page` sources are the Sapienza IRIS repository records of Phys. Lett. B 123, 269 (1983) and B 335, 246 (1994): they reproduce the papers' abstracts and journal references; the journal pages (sciencedirect.com) answered HTTP 403 and `cds.cern.ch` was not used.

### Conflicts (claim / source A / source B / chosen / why)

- **CHORUS data-taking years.** Final-results paper (arXiv:0710.3361): "took data from 1994 to 1997"; conference summary hep-ex/0206006: "during the years 1994-1998" (CHORUS and NOMAD together); CERN Courier (27 Nov 1998): both began operation in 1993 and finished in September 1998. Chosen: active 1994-1997 (the experiment's own paper, the data set of the final analysis); 1993-1994 recorded as a `commissioning` ("first operation") interval, `approximate`, because the Courier says "began operation"; terminal event 1997, `approximate`.
- **NOMAD run.** Final paper: events collected "From 1995 to 1998"; Courier: operation from 1993, completion September 1998; Dore (EPJ H 37, 2012): "NOMAD (1994)"; CERN Archives: approved at the end of 1991, "data taking was completed at the end of 1998 ... detector was dismantled during the course of 1999". Chosen: approved 1991-12 (approx), commissioning 1993-1995 (approx), active 1995-1998, completed 1998-12 (approx). The September 1998 Courier date is not used for the NOMAD terminal event.
- **CDHS start.** Collaboration page: "from December 1976 until 1984"; Dore: "took data from 1977"; Courier: first SPS neutrino beams "early in 1977". Chosen December 1976 (the experiment's own statement), the others in the interval note. In 1983 the detector was split in two for a PS neutrino-oscillation experiment (Dore); not a separate record.
- **CHARM II run.** CERN Archives (WA79): preparation 1983, setting-up 1984, data taking began 1986, completed 12 August 1991; the 1994 abstract analyses data "from 1987 till 1991"; Courier: "From 1983-91"; Dore: "CHARMII (1982)". Chosen the archive dates (the experiment's own administrative record); preparation recorded as `construction`, approximate.
- **CDHS result attribution.** The Springer abstract page for Z. Phys. C 35, 443 (1987) does not name the collaboration. Attribution rests on the four CDHS institutes in the affiliations, the RMP review hep-ex/9707015 (cites it for CDHSW total cross sections) and the collaboration page's list of subjects; recorded as `experiment_ids` objects with sources and in the result's date note.
- **West Area location.** Sources name "the West Area of the SPS" but give no coordinate; Nominatim finds no West Area feature ("CERN West Area", "EHW1 CERN", "CERN SPS West Hall Meyrin" returned nothing). Chosen the existing CERN Meyrin campus site, placement `approximate`.

### Unresolved fields

- **All five:** hall-level coordinates; collaboration formation dates, leaderships and membership counts (the NOMAD CERN Archives page lists institutes "in 2003" but no count is recorded); `external.inspire_experiment` (inspirehep.net not contacted); official websites (none survives: choruswww.cern.ch and nomadinfo.cern.ch do not resolve, knobloch.web.cern.ch is offline).
- **CHORUS:** approval date; the 1997-2001 first-phase results (not located on arXiv by id).
- **NOMAD:** the detector paper (NIM A 404, 1998) is not on arXiv; charm, strange-particle and cross-section results are not recorded.
- **CDHS:** the 1984 oscillation-limit paper (Phys. Lett. B 134, 281) and the 1977-82 papers: abstracts not fetchable (a 1985 Dortmund thesis abstract exists at repository.cern/records/smt5g-38m14 but is a thesis, not a collaboration result, and was not used). Jack Steinberger has no person record on this branch, so no leadership row.
- **CHARM:** neutral-current and electroweak-angle results (a 1981 abstract with sin^2 theta = 0.220 +- 0.014 exists on iris.gssi.it but the repository record gives no journal reference or date beyond the year 1981, so it was not recorded). WA65 (1980-82) and PS181 (from 1983) are not separate records.
- **CHARM II:** inverse muon decay and oscillation-search results not recorded.

### Candidates excluded or not done

None excluded; all five assigned experiments are done. Not created: a West Area Neutrino Facility beamline or a West Area hall site (no coordinate source), BEBC and the Omega spectrometer (not assigned).

## Part 2 (F2): JSNS2, CCM, MACRO, Soudan 2, Baksan Underground Scintillation Telescope

### Scope

Five experiments from the neutrino-2 queue (JSNS2, CCM, MACRO, Soudan 2, Baksan Underground Scintillation Telescope), each taken to the mandatory bar: experiment, detector, collaboration, located site on a facility, dated intervals with quote and locator, topics, summaries, sources, and at least one headline result. Every quote was written through a helper that fetched the cited source today and refused non-verbatim text; the records were then re-checked with `scripts/atlas_quote_check.py` (all quotes verbatim except two existing records of other streams that cite an unreachable slide deck).

### Entities written

| id | type | status |
|---|---|---|
| `experiment:baksan-underground-scintillation-telescope` | experiment | active |
| `experiment:ccm` | experiment | active |
| `experiment:jsns2` | experiment | active |
| `experiment:macro` | experiment | completed |
| `experiment:soudan-2` | experiment | completed |
| `detector:baksan-underground-scintillation-telescope-detector` | detector | active |
| `detector:ccm-detector` | detector | active |
| `detector:jsns2-detector` | detector | active |
| `detector:macro-detector` | detector | completed |
| `detector:soudan-2-detector` | detector | completed |
| `collaboration:baksan-underground-scintillation-telescope` | collaboration | active |
| `collaboration:ccm` | collaboration | active |
| `collaboration:jsns2` | collaboration | active |
| `collaboration:macro` | collaboration | completed |
| `collaboration:soudan-2` | collaboration | completed |
| `result:baksan-bust-neutrino-burst-limit-2019` | result | - |
| `result:ccm-cherenkov-event-by-event-2025` | result | - |
| `result:ccm-first-leptophobic-dm-search-2021` | result | - |
| `result:jsns2-first-sterile-search-2026` | result | - |
| `result:macro-atmospheric-nu-oscillation-global-analysis-2004` | result | - |
| `result:macro-final-monopole-limit-2002` | result | - |
| `result:soudan-2-atmospheric-neutrino-oscillations-2003` | result | - |
| `result:soudan-2-nucleon-decay-lepton-k0-limits-1999` | result | - |
| `site:baksan-bust-hall` | site | - |

Edited existing records (own scope): `facility:soudan-underground-laboratory` (new interval 'Soudan 2 data taking in the underground laboratory', 1989-04 to 2001-06, source hep-ex/0307069); `facility:baksan-neutrino-observatory` (new interval 'hosting the Baksan Underground Scintillation Telescope', 1978 open, source INR page). The Baksan facility file was not in canonical A11 form (compact hand-written JSON); saving it re-sorted keys, so the git diff is large but only `intervals` and `sources` differ semantically. New facilities: none. New sites: `site:baksan-bust-hall`.

### Sources added

| id | type | URL |
|---|---|---|
| `src:baksan-bust-1301-1138` | arxiv | https://arxiv.org/abs/1301.1138 |
| `src:baksan-bust-1907-03019` | arxiv | https://arxiv.org/abs/1907.03019 |
| `src:baksan-bust-1907-05183` | arxiv | https://arxiv.org/abs/1907.05183 |
| `src:baksan-bust-astro-ph0212499` | arxiv | https://arxiv.org/abs/astro-ph/0212499 |
| `src:baksan-bust-pos-muto2022-035` | journal_article | https://pos.sissa.it/425/035/pdf |
| `src:ccm-2105-14020` | arxiv | https://arxiv.org/abs/2105.14020 |
| `src:ccm-2109-14146` | arxiv | https://arxiv.org/abs/2109.14146 |
| `src:ccm-2507-08886` | arxiv | https://arxiv.org/abs/2507.08886 |
| `src:ccm-2507-08887` | arxiv | https://arxiv.org/abs/2507.08887 |
| `src:ccm-2608-12616` | arxiv | https://arxiv.org/abs/2608.12616 |
| `src:ccm-dpf-2026-newmark-talk` | project_document | https://indico.fnal.gov/event/72820/contributions/340971/attachments/199703/278315/Newmark_DPF2026.pdf |
| `src:ccm-sbn-et-2024-schneider-talk` | project_document | https://indico.nevis.columbia.edu/event/6/contributions/17/attachments/16/17/SBN_ET_2024_CCM.pdf |
| `src:jsns2-1507-07076` | arxiv | https://arxiv.org/abs/1507.07076 |
| `src:jsns2-1705-08629` | arxiv | https://arxiv.org/abs/1705.08629 |
| `src:jsns2-2111-07482` | arxiv | https://arxiv.org/abs/2111.07482 |
| `src:jsns2-2602-06274` | arxiv | https://arxiv.org/abs/2602.06274 |
| `src:jsns2-official-site-collaborators` | official_experiment_site | https://research.kek.jp/group/mlfnu/eng/researcher.html |
| `src:jsns2-official-site-news` | official_experiment_site | https://research.kek.jp/group/mlfnu/eng/index.html |
| `src:jsns2-official-site-research` | official_experiment_site | https://research.kek.jp/group/mlfnu/eng/research.html |
| `src:macro-epjc-36-323-2004` | journal_article | https://doi.org/10.1140/epjc/s2004-01951-9 |
| `src:macro-hep-ex0207020` | arxiv | https://arxiv.org/abs/hep-ex/0207020 |
| `src:macro-hep-ex0210006` | arxiv | https://arxiv.org/abs/hep-ex/0210006 |
| `src:macro-hep-ex0612057` | arxiv | https://arxiv.org/abs/hep-ex/0612057 |
| `src:soudan-2-hep-ex0307069` | arxiv | https://arxiv.org/abs/hep-ex/0307069 |
| `src:soudan-2-hep-ex9611007` | arxiv | https://arxiv.org/abs/hep-ex/9611007 |
| `src:soudan-2-hep-ex9901024` | arxiv | https://arxiv.org/abs/hep-ex/9901024 |
| `src:soudan-2-hep-ex9910026` | arxiv | https://arxiv.org/abs/hep-ex/9910026 |

Reused existing sources: `src:geo-baksan-inr-bust` (https://www.inr.ru/rus/bno/lbpst.html), `src:rf12-inr-baksan-observatory-page` (https://www.inr.ru/eng/ebno.html), `src:geo-baksan-osm-main-adit`.

### Experiments: status, intervals, evidence, conflicts and unresolved fields

#### JSNS2 (`experiment:jsns2`, kind accelerator_neutrino, status active, tier D)
Facility `facility:j-parc`; site `site:j-parc-mlf` (existing, campus-grade MLF centroid, approximate; detector is on the MLF 3rd floor). Accelerator `accelerator:j-parc-rcs`. Records: experiment, `detector:jsns2-detector`, `collaboration:jsns2`, `result:jsns2-first-sterile-search-2026`.

| interval | status | start | end | confidence | source / quote |
|---|---|---|---|---|---|
| proposal submitted | proposed | 2013-09 | 2015-04 | verified | https://research.kek.jp/group/mlfnu/eng/research.html "The experimental proposal was submitted to the J-PARC PAC on September 2013 officially." |
| stage-1 approval | approved | 2015-04 | 2017-12 | verified | https://arxiv.org/abs/1507.07076 "On April 2015, the J-PARC E56 (JSNS2 ...) experiment officially obtained stage-1 approval from J-PARC." |
| construction | construction | 2017-12 | 2020-06-05 | verified | https://research.kek.jp/group/mlfnu/eng/index.html (item 2017.12) "The part of the detector construction work is started at J-PARC." |
| commissioning run and refill | commissioning | 2020-06-05 | 2021-01-12 | verified | same page (item 2020.6.5) "We started to take data from June-5. The first physics run (the commissioning run) will be continued for 10 days." |
| long physics runs, 24 m detector | active | 2021-01-12 | open | verified | same page (item 2021.1) "In 2021-Jan, we start the first long term physics run (Jan-12)." |

Conflicts: PMT count 193 (TDR design) vs 120 (news item 2020.1.16, as installed): recorded 120 with the TDR value in the note. Fiducial 17 t (TDR) vs a 2018 status report's 25 t module (search snippet only; not used). "Baseline" label avoided because the A21 plausibility range starts at 100 m (24 m is valid physically): key spec labelled "Distance from the mercury target", detector spec key `target_distance` (unknown-spec-key warning). Membership 54 collaborators / 21 institutions is dated 2017-11-22 on the page (later author lists are longer).
Unresolved: stage-2 approval date (the news page says the 26th PAC minutes of 2018-10 recommend it; the minutes were not fetched); JSNS2-II far detector (48 m) not a separate entity; collaboration formation; leadership (no person records); INSPIRE experiment id.

#### Coherent CAPTAIN-Mills (`experiment:ccm`, kind accelerator_neutrino, secondary cevns, status active, tier D)
Facility `facility:los-alamos-national-laboratory`; site `site:lanl-lansce` (existing campus-grade LANSCE point; no hall coordinate in the sources read); accelerator `accelerator:lansce`. Records: experiment, `detector:ccm-detector`, `collaboration:ccm`, `result:ccm-first-leptophobic-dm-search-2021` (limit), `result:ccm-cherenkov-event-by-event-2025` (technology_milestone).

| interval | status | start | end | confidence | source / quote |
|---|---|---|---|---|---|
| engineering runs (CCM120 2019, CCM200 2021) | commissioning | Fall 2019 (2019-10, 09-11) | 2022 | approximate | https://arxiv.org/abs/2105.14020 "An engineering run was performed in Fall 2019 to study the characteristics of the CCM120 detector" |
| CCM200 physics run | active | 2022 | open | approximate | https://indico.fnal.gov/event/72820/contributions/340971/attachments/199703/278315/Newmark_DPF2026.pdf "CCM200 Physics Run (2022-2024)" |

Conflicts: the physics run is labelled 2022-2024 in the July 2026 collaboration talk and "Mid-way through 3yr data taking period" in an April 2024 talk, but no source says it ended or that it continues; interval left open (status active), flagged approximate. Distance: 20 m (arXiv:2105.14020 abstract) vs "about 23 m" in a search summary only (not used). Fiducial 5 t (CCM120, arXiv:2109.14146) vs 7 t (CCM200, arXiv:2507.08886): the 7 t value is the key spec, the 5 t value is in the detector summary. "Baseline" label avoided (A21 floor of 100 m); `target_distance` is an unknown spec key (warning).
Unresolved: official website (none found); collaboration formation date and membership counts; whether CCM200 data taking continues in 2026; hall coordinate; INSPIRE experiment id. The CCM name is not related to the COHERENT collaboration (stated in a CCM talk).

#### MACRO (`experiment:macro`, kind cosmic_ray, secondary atmospheric_neutrino, status completed, tier D)
Facility `facility:lngs`; site `site:lngs-hall-b` (existing shared campus-grade LNGS point, approximate). Records: experiment, `detector:macro-detector`, `collaboration:macro`, `result:macro-atmospheric-nu-oscillation-global-analysis-2004` (measurement), `result:macro-final-monopole-limit-2002` (limit).

| interval | status | start | end | confidence | source / quote |
|---|---|---|---|---|---|
| data taking, detector under construction | active | 1989-03 | 1994-04 | verified | https://arxiv.org/abs/hep-ex/0210006 "Data were taken from March 1989 till april 1994 with the detector under construction and from the middle of 1994 till the end of 2000 with the full detector." |
| data taking, full detector | active | mid-1994 (approx) | 2000-12 | approximate | same quote; end: https://arxiv.org/abs/hep-ex/0612057 "The detector started data taking in 1989 and it was running until December 2000." |
| completed | completed | 2000-12 | - | verified | hep-ex/0612057, same quote |

Conflicts: dimensions 76.5 x 12 x 9.3 m^3 (hep-ex/0210006) vs 76.6 (hep-ex/0612057): chose 76.5 (the paper that also gives mass and acceptance), noted. LNGS overburden: "mean rock thickness of about 3700 m.w.e." (MACRO paper) vs 3800 m.w.e. average on `site:lngs-hall-b` (Pandola 2011): both kept, each with its source. Kind: MACRO is "designed to search for rare events and rare phenomena in the cosmic radiation" and "optimized for the search for GUT magnetic monopoles"; there is no monopole kind, so primary `cosmic_ray`, secondary `atmospheric_neutrino` (the coverage row's category was atmospheric_neutrino). Alias "Monopole, Astrophysics and Cosmic Ray Observatory" (the acronym's expansion from memory) was NOT recorded: no fetched source spells it out.
Unresolved: approval / construction-start dates (the 1993 NIM detector paper is not on arXiv); collaboration formation, size and roster; official website (none; experiment ended); hall coordinate; INSPIRE experiment id. Not recorded: nuclearite, WIMP and supernova-watch results.

#### Soudan 2 (`experiment:soudan-2`, kind nucleon_decay, secondary atmospheric_neutrino, status completed, tier D)
Facility `facility:soudan-underground-laboratory`; site `site:soudan-minos-far-detector` (existing; surveyed MINOS far-hall point reused as an approximate placement because Soudan 2 stood in a different cavern on the same 27th level; no coordinate for the Soudan 2 cavern in any source read). Records: experiment, `detector:soudan-2-detector`, `collaboration:soudan-2`, `result:soudan-2-nucleon-decay-lepton-k0-limits-1999` (limit), `result:soudan-2-atmospheric-neutrino-oscillations-2003` (observation). Edited `facility:soudan-underground-laboratory`: added interval "Soudan 2 data taking in the underground laboratory" (1989-04 to 2001-06) and its source.

| interval | status | start | end | confidence | source / quote |
|---|---|---|---|---|---|
| data taking | active | 1989-04 | 2001-06 | verified | https://arxiv.org/abs/hep-ex/0307069 "The calorimeter started data taking in April 1989 and ceased operation in June 2001" |
| completed | completed | 2001-06 | - | verified | same quote |

Conflicts: a search snippet (not fetched, not used) gave other start dates (a 1987 start in a lab FAQ; 1986 installation); the physics papers' April 1989 is used. Exposure end: hep-ex/9901024 uses data "between April 1989 and January 1998" (3.9 fiducial kt-yr) while hep-ex/0307069 covers the whole run to June 2001 (5.90 fiducial kt-yr). The UMN laboratory site (soudan.umn.edu) and its archive copy were unreachable (connection timeouts, archive.org HTTP 503), so no laboratory-founding date and no official experiment page was obtained.
Warnings left: facility hull gap 2001-07 to 2003-06 (24 months) between the new Soudan 2 interval and the MINOS-hall interval: nothing sourced covers the laboratory in that period; no accelerator/beamline for the experiment (a cosmic-ray / atmospheric experiment).
Unresolved: excavation / construction dates of the Soudan 2 cavern and detector (installation 1986-1993 appears only in an encyclopaedia snippet, not used); the proposal date; collaboration formation and roster (affiliations on the papers: Argonne, Minnesota, Oxford, Rutherford Appleton Laboratory, Tufts, Western Washington); the p to nu K+ limit paper (PLB 427, 1998) was not retrieved; INSPIRE id; official website.

#### Baksan Underground Scintillation Telescope (`experiment:baksan-underground-scintillation-telescope`, kind cosmic_ray, secondary astrophysical_neutrino and atmospheric_neutrino, status active, tier D)
Facility `facility:baksan-neutrino-observatory`; new site `site:baksan-bust-hall` (campus-grade point = OpenStreetMap Main adit entrance, node 4244310615, 43.2756023 N 42.6921682 E, precision 700 m, approximate; the INR page puts the hall 550 m inside the horizontal tunnel, no bearing published). A new site was created instead of reusing `site:baksan-sage-underground-lab` because the SAGE hall is 3.5 km in at 4700 m.w.e. whereas the telescope hall is 550 m in at 850 m.w.e. Records: experiment, `detector:baksan-underground-scintillation-telescope-detector`, `collaboration:baksan-underground-scintillation-telescope` (the INR laboratory/group), `result:baksan-bust-neutrino-burst-limit-2019` (limit). Edited `facility:baksan-neutrino-observatory`: added interval "hosting the Baksan Underground Scintillation Telescope" (1978, open).

| interval | status | start | end | confidence | source / quote |
|---|---|---|---|---|---|
| telescope operating | active | 1978 | open | approximate | https://www.inr.ru/rus/bno/lbpst.html "В 1978 г. осуществлен запуск 3200-канального подземного сцинтилляционного телескопа (ПСТ), одной из крупнейших подземных установок того времени." (open end: https://pos.sissa.it/425/035/pdf "The facility has been uninterruptedly used for this purpose since the middle of 1980.") |

Coordinate / depth: INR page "Телескоп расположен в горной выработке объемом 12000 куб. метров на расстоянии 550м от начала горизонтального тоннеля."; depth 850 m.w.e. from https://arxiv.org/abs/1907.03019 "at the effective depth of 8.5 × 104 g · cm−2 (850 m of w.e.)".

Conflicts: start 1978 (INR page: launch; 2013 paper: continuous measurements "since December of 1978") vs "constructed late in 1977" and neutrino-burst observation "since 1980" (physics started later) - chose 1978, year precision, notes carry the others. Counters: 3,180 (INR page), 3,184 (arXiv:1907.03019, used), 3,150 (2007 and 2013 proceedings). Mass 330 t total scintillator vs 240 t target of the burst monitor and 130 t in the three lower layers. Overburden 850 m.w.e. here vs "more than 800 m.w.e." on the INR English page. Kind: the INR page calls the telescope multipurpose (astrophysics, particle physics, cosmic rays): primary `cosmic_ray` (coverage row said atmospheric_neutrino).
Unresolved: whether it operates in 2026 (latest source: data to 31 December 2021; interval left open); hall coordinate; the SN 1987A detection paper (1987, not on arXiv) and an atmospheric-neutrino result record; collaboration formation and roster (it is an INR laboratory); INSPIRE id; the Soudan-style start of construction (1977) as a separate interval.

### Candidates excluded or not done

None of the five was excluded. Not recorded within these experiments (outside the bar, listed under each Unresolved): the JSNS2-II 48 m far detector as its own detector; MACRO nuclearite, WIMP and supernova-watch results; Soudan 2 p to nu K+ limit paper (PLB 427, not retrieved); BUST SN 1987A detection paper and atmospheric-neutrino results.

## Part 3 (F3): Fréjus, NUSEX, Kolar Gold Fields

Scope: three nucleon-decay experiments of the first generation (Fréjus at Modane, NUSEX at Mont Blanc, the Kolar Gold Fields experiments in India). Owner tag `neutrino-2`. Every quote in the records was written through the helper library, which refused any quote that was not verbatim in the text fetched from the cited URL today, and the repository checker `scripts/atlas_quote_check.py --only <slug>` then confirmed it: **frejus 32/32, nusex 20/20, kolar-gold-fields 25/25, mont-blanc 4/4 verbatim, 0 number flags**. Validator on the shared tree: 0 errors on all my ids; warnings only of the tolerated kinds (coordinate-kind-approximate, no accelerator/beamline listed).

### Entities written

| id | type | start / end / status / site | URL and quote behind each date and coordinate |
|---|---|---|---|
| `experiment:frejus` | experiment | status `completed`; host facility:modane-underground-laboratory | installation and commissioning [commissioning] 1982 to 1984-02-19 (approximate): https://arxiv.org/abs/1102.0208 — "The excavation started in 1979 and the first experiment - a 900 ton iron tracking calorimeter to search for proton decay (“Frejus experiment”) - was commissioned in 1982."<br>data taking [active] 1984-02-19 to 1988-09-13 (verified): https://mozart.physik.rwth-aachen.de/PLB269-227.pdf — "Continuous data taking started February 19, 1984 with a mass of 240 tons. The size of the detector was gradually increased until the final mass of 912 tons was reached in June 1985. Data taking ended September 13, 1988."<br>completed [completed] 1988-09-13 to None (verified): https://mozart.physik.rwth-aachen.de/PLB269-227.pdf — "Data taking ended September 13, 1988." |
| `detector:frejus-detector` | detector | status `completed`; site site:lsm-frejus | installation and commissioning [commissioning] 1982 to 1984-02-19 (approximate): https://arxiv.org/abs/1102.0208 — "The excavation started in 1979 and the first experiment - a 900 ton iron tracking calorimeter to search for proton decay (“Frejus experiment”) - was commissioned in 1982."<br>data taking [active] 1984-02-19 to 1988-09-13 (verified): https://mozart.physik.rwth-aachen.de/PLB269-227.pdf — "Continuous data taking started February 19, 1984 with a mass of 240 tons. The size of the detector was gradually increased until the final mass of 912 tons was reached in June 1985. Data taking ended September 13, 1988."<br>completed [completed] 1988-09-13 to None (verified): https://mozart.physik.rwth-aachen.de/PLB269-227.pdf — "Data taking ended September 13, 1988." |
| `collaboration:frejus` | collaboration | status `completed`; host site:lsm-frejus | collaboration active [active] 1984-02-19 to 1988-09-13 (verified): https://mozart.physik.rwth-aachen.de/PLB269-227.pdf — "Continuous data taking started February 19, 1984 with a mass of 240 tons. The size of the detector was gradually increased until the final mass of 912 tons was reached in June 1985. Data taking ended September 13, 1988."<br>collaboration completed [completed] 1988-09-13 to None (verified): https://mozart.physik.rwth-aachen.de/PLB269-227.pdf — "Data taking ended September 13, 1988." |
| `experiment:nusex` | experiment | status `completed`; host facility:mont-blanc-laboratory | funded and in preparation [construction] 1980 to 1982-06-01 (approximate): https://link.springer.com/chapter/10.1007/978-1-4613-3171-1_37 — "has been funded and is in the preparation stage"<br>data taking [active] 1982-06-01 to None (approximate): https://ntrs.nasa.gov/api/citations/19850027829/downloads/19850027829.pdf — "June 1st, 1982 In a cave aside the Mont Blanc Tunnel"<br>completed [completed] between March 1985 and July 2004; end of data taking not stated in any source consulted to None (uncertain): https://arxiv.org/abs/hep-ph/0407297 — "We note that NUSEX, Fréjus, Soudan, Kamiokande and IMB stopped data-taking and currently only Superkamiokande is active." |
| `detector:nusex-detector` | detector | status `completed`; site site:mont-blanc-tunnel-laboratory | data taking [active] 1982-06-01 to None (approximate): https://ntrs.nasa.gov/api/citations/19850027829/downloads/19850027829.pdf — "June 1st, 1982 In a cave aside the Mont Blanc Tunnel"<br>completed [completed] between March 1985 and July 2004; end of data taking not stated in any source consulted to None (uncertain): https://arxiv.org/abs/hep-ph/0407297 — "We note that NUSEX, Fréjus, Soudan, Kamiokande and IMB stopped data-taking and currently only Superkamiokande is active." |
| `collaboration:nusex` | collaboration | status `completed`; host site:mont-blanc-tunnel-laboratory | collaboration active [active] 1982-06-01 to None (approximate): https://ntrs.nasa.gov/api/citations/19850027829/downloads/19850027829.pdf — "June 1st, 1982 In a cave aside the Mont Blanc Tunnel"<br>collaboration completed [completed] between March 1985 and July 2004; end of data taking not stated in any source consulted to None (uncertain): https://arxiv.org/abs/hep-ph/0407297 — "We note that NUSEX, Fréjus, Soudan, Kamiokande and IMB stopped data-taking and currently only Superkamiokande is active." |
| `facility:mont-blanc-laboratory` | facility | status `active`; primary site site:mont-blanc-tunnel-laboratory | NUSEX installation planned [construction] 1980 to 1982-06-01 (approximate): https://link.springer.com/chapter/10.1007/978-1-4613-3171-1_37 — "The NUSEX apparatus will be installed in the Mont Blanc Tunnel and the data taking is expected to start in the middle of 1981."<br>hosting NUSEX [active] 1982-06-01 to None (uncertain): https://ntrs.nasa.gov/api/citations/19850027829/downloads/19850027829.pdf — "June 1st, 1982 In a cave aside the Mont Blanc Tunnel" |
| `site:mont-blanc-tunnel-laboratory` | site | 45.85963, 6.90759 (campus, approximate, ±1500 m); depth ~5000 m.w.e. | OSM geometry of the Mont Blanc Tunnel; mid-length point (see note) — sources https://overpass-api.de/api/interpreter?data=%5Bout%3Ajson%5D%5Btimeout%3A25%5D%3B%28way%284525912%29%3Bway%28205544546%29%3B%29%3Bout%20geom%20tags%3B, https://link.springer.com/chapter/10.1007/978-1-4757-0375-7_58; depth quote: "is at a depth of approximately 5000 m.w.e." |
| `experiment:kolar-gold-fields-experiments` | experiment | status `completed`; host facility:kolar-gold-fields-underground-laboratory | underground experiments [active] 1960 to 1993 (approximate): https://arxiv.org/abs/hep-ex/0008074 — "A series of experiments underground has been carried out deep underground in KGF since 1960."<br>completed [completed] 1993 to None (approximate): https://arxiv.org/abs/hep-ex/0008074 — "Since the management of KGF mines decided to start closing the mines in 1993, the proton decay experiment stopped data taking in 1993." |
| `detector:kolar-gold-fields-phase-i-detector` | detector | status `completed`; site site:kolar-gold-fields-mines | data taking [active] 1980-12 to 1993 (approximate): https://arxiv.org/abs/hep-ex/0008074 — "This 'Phase I' detector which comprised of 1600 proportional counters having a total weight of 140 tons of iron, was installed deep underground at the depth of 7000 hg/cm2 and started making observations on possible proton decay phenomenon at the end of 1980."<br>completed [completed] 1993 to None (approximate): https://arxiv.org/abs/hep-ex/0008074 — "Since the management of KGF mines decided to start closing the mines in 1993, the proton decay experiment stopped data taking in 1993." |
| `detector:kolar-gold-fields-phase-ii-detector` | detector | status `completed`; site site:kolar-gold-fields-mines | data taking [active] 1985 to 1993 (approximate): https://arxiv.org/abs/hep-ex/0008074 — "This detector became operational in 1985. The Phase II detector comprised of about 4000 proportional counters and total weight of 260 tons."<br>completed [completed] 1993 to None (approximate): https://arxiv.org/abs/hep-ex/0008074 — "Since the management of KGF mines decided to start closing the mines in 1993, the proton decay experiment stopped data taking in 1993." |
| `collaboration:kolar-gold-fields-experiments` | collaboration | status `completed`; host site:kolar-gold-fields-mines | collaboration active [active] 1960 to 1993 (approximate): https://arxiv.org/abs/hep-ex/0008074 — "A series of experiments underground has been carried out deep underground in KGF since 1960."<br>collaboration completed [completed] 1993 to None (approximate): https://arxiv.org/abs/hep-ex/0008074 — "Since the management of KGF mines decided to start closing the mines in 1993, the proton decay experiment stopped data taking in 1993." |
| `facility:kolar-gold-fields-underground-laboratory` | facility | status `decommissioned`; primary site site:kolar-gold-fields-mines | underground experiments [active] 1960 to 1993 (approximate): https://arxiv.org/abs/hep-ex/0008074 — "A series of experiments underground has been carried out deep underground in KGF since 1960."<br>mines closed; laboratory ended [decommissioned] 1993 to None (approximate): https://arxiv.org/abs/hep-ex/0008074 — "Since the management of KGF mines decided to start closing the mines in 1993, the proton decay experiment stopped data taking in 1993." |
| `site:kolar-gold-fields-mines` | site | 12.9546, 78.27313 (campus, approximate, ±5000 m); depth 7000 m.w.e. (7000 hg/cm²) | Nominatim result for "Kolar Gold Fields" (node 245614133): Kolar Gold Fields, Kolar Gold Field taluk, Kolar, Karnataka, 563115, India — sources https://nominatim.openstreetmap.org/search?q=Kolar+Gold+Fields&format=jsonv2&limit=1; depth quote: "was installed deep underground at the depth of 7000 hg/cm2" |

Results (all `coverage.researched: full`, tier D):

| id | type | date | claim quote (abstract) | date quote |
|---|---|---|---|---|
| `result:frejus-atmospheric-neutrino-oscillation-limits-1990` | limit | 1990-08-09 (publication) | "Three independent analyses have been performed and no evidence for neutrino oscillations has been found. The resulting limits onAm 2 for maximal mixing are more restrictive by more than one order of magnitude with respect to earlier measurements." | https://mozart.physik.rwth-aachen.de/PLB245-305.pdf — "9 August 1990" |
| `result:frejus-bl-violating-nucleon-decay-limits-1991` | limit | 1991-10-24 (publication) | "No signal is found for a sensitivity of 2.0 kiloton year. The lower limits on the partial lifetime for the various nucleon decay modes range from" | https://mozart.physik.rwth-aachen.de/PLB269-227.pdf — "24 October 1991" |
| `result:frejus-nucleon-decay-charged-lepton-limits-1991` | limit | 1991-09 (publication) | "Lower limits on the nucleon lifetime in channels containing at least one positron or muon are given. The analysis is based on 4 years of data taking with the Fréjus detector." | https://doi.org/10.1007/BF01551450 — "Published: September 1991" |
| `result:kgf-first-atmospheric-neutrinos-1965` | observation | 1965 (publication) | "In 1965, the first cosmic ray neutrino was observed in KGF by the Tata-Osaka-Durham group (Ref.3)." | https://cerncourier.com/a/remembering-a-cosmic-ray-pioneer-b-v-sreekantan-1925-2019/ — "in early 1965 they recorded the first atmospheric-neutrino event" |
| `result:kgf-proton-decay-claim-2000` | anomaly | 2000-08-30 (preprint) | "Deep underground in Kolar Gold Fields, in southern India, an experiment to detect proton decay had been carried out since the end of 1980. Analysis of data yielded the following results; (l) the life time of proton is about 1 x 1031 years," | https://arxiv.org/abs/hep-ex/0008074 — "[Submitted on 30 Aug 2000]" |
| `result:nusex-atmospheric-neutrino-flux-1989` | measurement | 1989 (publication) | "The measured flux of muon neutrinos is in very good agreement with predictions and no anomaly has been found in the ratio between the rate of electron and muon neutrino events." | https://doi.org/10.1209/0295-5075/8/7/005 — "The NUSEK Collaboration et al 1989 EPL 8 611" |
| `result:nusex-nucleon-decay-candidate-1983` | anomaly | 1983-01 (publication) | "In that time four fully contained events with at least a 10 cm track in iron have been recorded. Three of these can be definitely attributed to neutrino interactions. The fourth event can be explained by a number of possible proton decay modes." | https://www.osti.gov/biblio/5702014 — "01 January 1983" |

New facilities: `facility:mont-blanc-laboratory`, `facility:kolar-gold-fields-underground-laboratory`. New sites: `site:mont-blanc-tunnel-laboratory`, `site:kolar-gold-fields-mines`. Reused: `facility:modane-underground-laboratory`, `site:lsm-frejus` (Fréjus). Topics: existing `topic:nucleon-decay` (now used), `topic:atmospheric-neutrinos`, `topic:neutrino-oscillations`, `topic:cosmic-rays`. No accelerator, beamline, institution or membership records were written.

### Sources added

| id | type | URL |
|---|---|---|
| `src:frejus-hep-ph0407297` | arxiv | https://arxiv.org/abs/hep-ph/0407297 |
| `src:frejus-plb245-305-1990` | journal_article | https://mozart.physik.rwth-aachen.de/PLB245-305.pdf |
| `src:frejus-plb269-227-1991` | journal_article | https://mozart.physik.rwth-aachen.de/PLB269-227.pdf |
| `src:frejus-zphysc50-385-1991` | journal_article | https://doi.org/10.1007/BF01551450 |
| `src:geo-kgf-nominatim-town` | geocoder | https://nominatim.openstreetmap.org/search?q=Kolar+Gold+Fields&format=jsonv2&limit=1 |
| `src:kgf-cerncourier-sreekantan-2020` | press_release | https://cerncourier.com/a/remembering-a-cosmic-ray-pioneer-b-v-sreekantan-1925-2019/ |
| `src:kgf-hep-ex0008074` | arxiv | https://arxiv.org/abs/hep-ex/0008074 |
| `src:kgf-hep-ph9210238` | arxiv | https://arxiv.org/abs/hep-ph/9210238 |
| `src:nusex-epl-8-611-1989` | journal_article | https://doi.org/10.1209/0295-5075/8/7/005 |
| `src:nusex-ntrs-icrc1985-he6-2-6` | journal_article | https://ntrs.nasa.gov/api/citations/19850027829/downloads/19850027829.pdf |
| `src:nusex-osm-overpass-mont-blanc-tunnel` | openstreetmap | https://overpass-api.de/api/interpreter?data=%5Bout%3Ajson%5D%5Btimeout%3A25%5D%3B%28way%284525912%29%3Bway%28205544546%29%3B%29%3Bout%20geom%20tags%3B |
| `src:nusex-osti-5702014-1983` | journal_article | https://www.osti.gov/biblio/5702014 |
| `src:nusex-springer-bellotti-nucleon-stability-1980` | journal_article | https://link.springer.com/chapter/10.1007/978-1-4613-3171-1_37 |
| `src:nusex-springer-monopole83-price-1984` | journal_article | https://link.springer.com/chapter/10.1007/978-1-4757-0375-7_58 |

Reused (existing): `src:geo-euro-ug-pandola-2011` (Pandola, arXiv:1102.0208) for the Modane section. `src:frejus-hep-ph0407297` (A. Rubbia's review) is cited by Fréjus, NUSEX and also usable by Soudan 2 (fork F2); `src:kgf-hep-ph9210238` (Langacker's 1992 review) is cited by KGF and the NUSEX 1983 result. DOIs of the printed journal articles were taken from Crossref metadata (api.crossref.org lookups by title and volume); the Elsevier, IOP-print and AIP landing pages for the old papers are paywalled, so the pages actually fetched are the RWTH-Aachen hosted copies of PLB 245 and PLB 269, the Springer abstract page of Z. Phys. C 50, the IOPscience abstract page of EPL 8, 611, the OSTI record, and the NASA NTRS scan of the NUSEX ICRC 1985 paper.

### Conflicts (claim / source A / source B / chosen / why)

- **Fréjus start.** The 2011 review of European underground laboratories (Pandola, arXiv:1102.0208) says the 900 t iron tracking calorimeter was "commissioned in 1982"; the collaboration's own PLB 269 paper says "Continuous data taking started February 19, 1984 with a mass of 240 tons" and the final mass of 912 t was reached in June 1985. A 1985 ICRC proceedings (NASA NTRS, garbled text layer) says the detector was installed from October 1983 to May 1985. Chosen: a `commissioning` interval 1982 to 1984-02-19 (approximate, citing the review) followed by `active` from 1984-02-19 (collaboration's day-precision statement) to 1988-09-13 ("Data taking ended September 13, 1988"). The detector grew module by module, so installation overlapped data taking.
- **NUSEX end.** No fetched source dates the end of data taking. Lower bound: the 1985 ICRC paper reports 2.8 years of operation from 1 June 1982 (so running until about March 1985); upper bound: Rubbia's 2004 review (arXiv v1, 26 Jul 2004) says NUSEX "stopped data-taking". The EPL 8, 611 paper was received 22 November 1988. Chosen: status `completed`, the terminal interval's start given as an A4 date object (`date` 2004-07, `earliest` 1985-03, `latest` 2004-07, with a `display` saying the end is not stated). The validator accepts it; on the timeline NUSEX reads as completed, hatched (possible), from March 1985. Precedent for an upper-bound end: Bugey in NEUTRINO_2.md.
- **NUSEX start.** The 1985 ICRC paper (NASA scan, OCR text layer: "June 1st, 1982 In a cave aside the Mont Blanc Tunnel") gives 1 June 1982; the 1983 AIP proceedings say "operating since 1982"; Rubbia's table says 1982. Chosen 1982-06-01 (approximate, because the quote is an OCR text layer). Planned start was mid-1981 per the 1980 Bellotti communication; recorded as the end of a `construction` interval starting 1980.
- **NUSEX country and coordinate.** The tunnel crosses the French-Italian border; no source gives the cave position or the country of the cave. The site point is the mid-length point (cumulative great-circle length) of the OpenStreetMap trace of the tunnel (11.49 km; ways 4525912 + 205544546), 5.75 km from the French portal, hence in the French section; filed under FR with a 1500 m precision and a note. The Monopole '83 chapter says NUSEX "is situated half way along the road tunnel".
- **KGF depth unit.** The collaboration quotes hg/cm^2 (7000 for Phase I, 6045 for Phase II); recorded as m.w.e. with `confidence: derived` and a note (1 hg/cm^2 = 100 g/cm^2 = 1 m.w.e.). The CERN Courier obituary gives rock depths of 2300 m (neutrino telescopes of 1965; one of the 1980s detectors) and 2000 m (the other), and a maximum depth of 2700 m for the 1960s muon work; not used for the quantity because the units differ.
- **KGF end.** The collaboration's own paper: "the proton decay experiment stopped data taking in 1993" because the mines were to close in 1993. A magazine article found in a search says the laboratory ceased operation in 1992; not fetched, not used.
- **KGF result type.** The 2000 paper's title says "Experimental evidence for G.U.T. Proton Decay" and reports tau_p about 1e31 yr; other experiments (Mont Blanc, IMB, Kamiokande, Fréjus) set limits of order 1e33 yr, as the paper itself says. Recorded as `anomaly` (a claim not confirmed), not as `evidence`, with the paper's own quotation of the contradiction in the notes and Langacker's 1992 statement that no experiment has observed proton decay as context. The 1965 first atmospheric neutrino is `observation` (the A16 keyword check demands "detect" for `first_detection` and the cited texts say "observed").
- **KGF 1965 priority.** The Courier obituary says the Kolar event was recorded contemporaneously with Reines' South African mine experiment; both are said to be first. Recorded in the result's note; the claim quote is the collaboration's own 2000 statement because the 1965 paper was not fetchable.

### Unresolved fields

- **All three experiments:** `external.inspire_experiment` empty (inspirehep.net not contacted); no collaboration formation date, member count or institution count; no official website (none exists); no membership files.
- **Fréjus:** the 1989-90 papers with the headline p to e+ pi0 / mu+ pi0 limits (Nucl. Phys. B 313, 509; Phys. Lett. B 240, 237) and the detector paper (NIM A 262, 463) are paywalled, so no result record for them; the results written are PLB 269 and Z. Phys. C 50 (limits for 35 to 39 channels) and PLB 245. No hall coordinate (the detector uses `site:lsm-frejus`, the laboratory's approximate point). The numeric ranges in the result `key_value_text` come from flattened superscripts in the page text and are marked `approximate` with a note.
- **NUSEX:** end of data taking; the final nucleon-decay lifetime limits (Phys. Lett. B 133, 454 (1983) is not fetchable); the laboratory's founding date, operator and whether it still operates (the facility's open `active` interval is `confidence: uncertain`); the cave's exact position; whether Mont Blanc Laboratory should be linked to the later experiments there (LSD). The NASA NTRS scan's text layer is garbled in places, which is why two quotes keep OCR forms (noted in the interval notes).
- **KGF:** exact shaft/level coordinates; retirement date of the Phase I detector (both phases are recorded as ending when the experiment stopped in 1993); the primary 1965 neutrino paper and the 1981-82 candidate-event papers (Elsevier, not fetchable); facility operator.

### Candidates considered and excluded, or not done

- Indian Neutrino Observatory (INO): out of scope for this brief (a later proposal).
- LSD (Liquid Scintillation Detector) and LVD at Mont Blanc: the Mont Blanc Laboratory now exists as a facility, so LSD could be added later; it was not in this brief.
- HPW (Harvard-Purdue-Wisconsin) and the other 1980s proton-decay detectors: not in the brief.

## Part 4 (F4): neutrinoless double-beta decay (Heidelberg-Moscow, NEMO-3, SuperNEMO, CANDLES, CUORICINO, PandaX-III)

Scope: Heidelberg-Moscow, NEMO-3, SuperNEMO demonstrator, CANDLES, CUORICINO, PandaX-III, plus the double-beta lineage repairs on experiment:cuore, gerda, cupid, legend, majorana-demonstrator, exo-200 and nexo. Owner tag `neutrino-2`. All six experiments reached the mandatory bar (PandaX-III with caveats). Records were built by scripts that refused any quote not verbatim in the cited page (the `scripts/atlas_quote_check.py` normaliser); a second pass with that script (`--only <slug> --offline`) gave all quotes `verbatim`, 0 number flags, on every new record. Validator on these ids: 0 errors; only the tolerated warnings (no accelerator for an active experiment, campus-grade coordinate on a detector site).

### Entities written

New experiments 6, detectors 6, collaborations 4 (heidelberg-moscow, nemo-3, supernemo, candles), results 6, site 1 (`site:kamioka-candles-lab-d`), sources 24 (including 1 geocoder result and 4 project documents). No new facility. Existing records edited: 7 (lineage only).

| id | type | start / end / status / site | URL and quote behind each date and coordinate |
|---|---|---|---|
| `experiment:heidelberg-moscow` | experiment (kind `double_beta_decay`, tier D) | status `completed`; facility facility:lngs | |
|  | interval `data taking at LNGS` | active: 1990-08 to 2003-05 (verified) | https://arxiv.org/abs/hep-ph/0403018: "which collected data in the period August 1990 - May 2003" |
|  | interval `completed` | completed: 2003-05 to None (verified) | https://arxiv.org/abs/hep-ph/0403018: "which collected data in the period August 1990 - May 2003" |
| `detector:heidelberg-moscow-detector` | detector (`germanium`) | placement main at `site:lngs-hall-a` (derived) | https://arxiv.org/abs/0704.0063: "the experimental building of the experiment was built between Halls A and B in Gran Sasso" |
|  | collaboration | collaboration:heidelberg-moscow | |
| `result:heidelberg-moscow-evidence-claim-2001` | result `evidence` | 2002-01-24 (preprint) | https://arxiv.org/abs/hep-ph/0201231: "First evidence for neutrinoless double beta decay is observed giving first evidence for lepton number violation." |
| `result:heidelberg-moscow-majorana-mass-limit-1999` | result `limit` | 1999-02-10 (preprint) | https://arxiv.org/abs/hep-ex/9902014: "we set a lower limit on the half-life of the neutrinoless double beta decay in 76Ge of T_1/2 > 5.7 * 10^{25} yr at 90% C.L., thus excluding an effective Majorana neutrino mass greater than 0.2 eV" |
| `experiment:nemo-3` | experiment (kind `double_beta_decay`, tier D) | status `completed`; facility facility:modane-underground-laboratory | |
|  | interval `Phase I data taking` | active: 2003-02 to 2004-10 (verified) | https://arxiv.org/abs/1506.05825: "the first data taking period, labeled Phase I, from February 2003 until October 2004" |
|  | interval `Phase II data taking` | active: 2004-12 to 2010-12 (verified) | https://arxiv.org/abs/1506.05825: "The second data taking period between December 2004 until the end of running in December 2010 (Phase II)" |
|  | interval `completed` | completed: 2010-12 to None (verified) | https://arxiv.org/abs/1506.05825: "The second data taking period between December 2004 until the end of running in December 2010 (Phase II)" |
| `detector:nemo-3-detector` | detector (`tracking_calorimeter`) | placement main at `site:lsm-frejus` (verified) | https://arxiv.org/abs/1506.05825: "The NEMO-3 detector, which had been operating in the Modane Underground Laboratory from 2003 to 2010, was designed to search for neutrinoless double β (0νββ) decay." |
|  | collaboration | collaboration:nemo-3 | |
| `result:nemo-3-mo100-final-limit-2015` | result `limit` | 2015-06-18 (preprint) | https://arxiv.org/abs/1506.05825: "We therefore derive a lower limit on the half-life of 0νββ decays in 100 Mo of T1/2 (0νββ) > 1.1 × 10^24 yr at the 90% Confidence Level" |
| `experiment:supernemo-demonstrator` | experiment (kind `double_beta_decay`, tier D) | status `active`; facility facility:modane-underground-laboratory | |
|  | interval `assembly completed and commissioning` | commissioning: 2018-11 to 2025-04-10 (approximate) | https://indico.jinr.ru/event/1810/attachments/8934/14574/SuperNEMO_progress-report.pdf: "The most important result is the completion of the basic assembly of the SuperNEMO Demonstrator in November 2018" |
|  | interval `data taking` | active: 2025-04-10 to None (verified) | https://indico.in2p3.fr/event/36107/contributions/153937/attachments/93125/142497/SuperNEMO_Lyon2025.pdf: "Start of data acquisition: April 10th 2025" |
| `detector:supernemo-demonstrator-detector` | detector (`tracking_calorimeter`) | placement main at `site:lsm-frejus` (verified) | https://indico.jinr.ru/event/1810/attachments/8934/14574/SuperNEMO_progress-report.pdf: "Demosntrator (first module), mounted under the clean tent in the main hall of the LSM laboratory (Modane, France)" |
|  | collaboration | collaboration:supernemo | |
| `result:supernemo-demonstrator-calorimeter-commissioning-2024` | result `technology_milestone` | 2024-12-23 (preprint) | https://arxiv.org/abs/2412.18021: "A time alignment of about 120 ps and a time resolution around 615 ps have been achieved. Concerning the energy, an alignment of 7.5% has been obtained." |
| `experiment:candles` | experiment (kind `double_beta_decay`, tier D) | status `active`; facility facility:kamioka-observatory | |
|  | interval `CANDLES III data taking` | active: Spring 2013 to None (approximate) | https://arxiv.org/abs/1403.3329: "The CANDLES III experiment is presently taking data since Spring 2013 at the Kamioka underground laboratory, Japan." |
| `detector:candles-detector` | detector (`scintillating_crystal`) | placement main at `site:kamioka-candles-lab-d` (verified) | https://arxiv.org/abs/2008.09288: "The current setup of the detector system, which is called CANDLES-III, is installed at lab-D of the Kamioka Underground Laboratory (2700 m.w.e.) in the Institute of Cosmic Ray Research of the University of Tokyo." |
|  | collaboration | collaboration:candles | |
| `result:candles-iii-low-background-48ca-2020` | result `technology_milestone` | 2020-08-21 (preprint) | https://arxiv.org/abs/2008.09288: "we performed the first search for 0νββ decay in a low background condition using a detector on the scale of hundreds of kg of non-enriched Ca" |
| `experiment:cuoricino` | experiment (kind `double_beta_decay`, tier D) | status `completed`; facility facility:lngs | |
|  | interval `data acquisition` | active: 2003-04 to 2008-06 (verified) | https://arxiv.org/abs/1012.3266: "CUORICINO data acquisition started in April 2003 and ended in June 2008" |
|  | interval `completed` | completed: 2008-06 to None (verified) | https://arxiv.org/abs/1012.3266: "CUORICINO data acquisition started in April 2003 and ended in June 2008" |
| `detector:cuoricino-detector` | detector (`cryogenic_bolometer`) | placement main at `site:lngs-hall-a` (derived) | https://arxiv.org/abs/1612.04276: "The tower was operated in Hall A of LNGS, in the same dilution refrigerator that previously hosted the CUORICINO experiment" |
|  | collaboration | none written (no named collaboration found) | |
| `result:cuoricino-130te-final-limit-2010` | result `limit` | 2010-12-15 (preprint) | https://arxiv.org/abs/1012.3266: "We report the final result of the CUORICINO experiment. Operated between 2003 and 2008, with a total exposure of 19.75 kg·y of 130 Te, CUORICINO was able to set a lower bound on the 130 Te 0νββ half-life of 2.8 × 10^24 y" |
| `experiment:pandax-iii` | experiment (kind `double_beta_decay`, tier D) | status `construction`; facility facility:cjpl | |
|  | interval `first TPC module under construction` | construction: 2016-10 to None (approximate) | https://arxiv.org/abs/1610.08883: "The first 200 kg module is under construction and is expected to be deployed in the next 2-3 years." |
| `detector:pandax-iii-detector` | detector (`gaseous_tpc`) | placement main at `site:cjpl-ii` (approximate) | https://arxiv.org/abs/2311.13396: "The detector will be installed at the CJPL-II [17] after the performance test in Shanghai." |
|  | collaboration | collaboration:pandax-4t | |
| `result:pandax-iii-status-final-detector-constructed-2023` | result `technology_milestone` | 2023-11-22 (preprint) | https://arxiv.org/abs/2311.13396: "The technology is successfully demonstrated by a prototype detector. The final detector has been constructed." |
| `site:kamioka-candles-lab-d` | site (facility:kamioka-observatory) | 36.40898, 137.30825 campus, approximate, 3000 m | https://nominatim.openstreetmap.org/search?q=Kamioka+mine+Hida+Gifu&format=jsonv2&limit=1: Nominatim result for "Kamioka mine Hida Gifu" (node 759469233): Kamioka Mine, ICRR, Kamiokande, CLIO, 国道41号, 神岡町土, 飛驒市, 岐阜県, 506-1205, 日本 |

Results written: `result:heidelberg-moscow-majorana-mass-limit-1999` (limit), `result:heidelberg-moscow-evidence-claim-2001` (evidence, by part of the collaboration), `result:nemo-3-mo100-final-limit-2015` (limit), `result:supernemo-demonstrator-calorimeter-commissioning-2024` (technology_milestone), `result:candles-iii-low-background-48ca-2020` (technology_milestone), `result:cuoricino-130te-final-limit-2010` (limit), `result:pandax-iii-status-final-detector-constructed-2023` (technology_milestone).

### Sources added

| id | type | URL |
|---|---|---|
| `src:candles-1403-3329` | arxiv | https://arxiv.org/abs/1403.3329 |
| `src:candles-2008-09288` | arxiv | https://arxiv.org/abs/2008.09288 |
| `src:candles-umehara-dbd2023-slides` | project_document | https://www.rcnp.osaka-u.ac.jp/dbd23/Data/Prog/S206_Umehara.pdf |
| `src:cuoricino-0802-3439` | arxiv | https://arxiv.org/abs/0802.3439 |
| `src:cuoricino-1012-3266` | arxiv | https://arxiv.org/abs/1012.3266 |
| `src:cuoricino-1612-04276` | arxiv | https://arxiv.org/abs/1612.04276 |
| `src:cuoricino-hep-ex0501034` | arxiv | https://arxiv.org/abs/hep-ex/0501034 |
| `src:geo-candles-nominatim-kamioka-mine` | geocoder | https://nominatim.openstreetmap.org/search?q=Kamioka+mine+Hida+Gifu&format=jsonv2&limit=1 |
| `src:gerda-hep-ex0404039` | arxiv | https://arxiv.org/abs/hep-ex/0404039 |
| `src:heidelberg-moscow-0704-0063` | arxiv | https://arxiv.org/abs/0704.0063 |
| `src:heidelberg-moscow-1307-4720` | arxiv | https://arxiv.org/abs/1307.4720 |
| `src:heidelberg-moscow-hep-ex9902014` | arxiv | https://arxiv.org/abs/hep-ex/9902014 |
| `src:heidelberg-moscow-hep-ph0201231` | arxiv | https://arxiv.org/abs/hep-ph/0201231 |
| `src:heidelberg-moscow-hep-ph0403018` | arxiv | https://arxiv.org/abs/hep-ph/0403018 |
| `src:heidelberg-moscow-hep-ph0404088` | arxiv | https://arxiv.org/abs/hep-ph/0404088 |
| `src:nemo-3-1506-05825` | arxiv | https://arxiv.org/abs/1506.05825 |
| `src:pandax-iii-1610-08883` | arxiv | https://arxiv.org/abs/1610.08883 |
| `src:pandax-iii-2001-01356` | arxiv | https://arxiv.org/abs/2001.01356 |
| `src:pandax-iii-2311-13396` | arxiv | https://arxiv.org/abs/2311.13396 |
| `src:supernemo-demonstrator-1005-1241` | arxiv | https://arxiv.org/abs/1005.1241 |
| `src:supernemo-demonstrator-2412-18021` | arxiv | https://arxiv.org/abs/2412.18021 |
| `src:supernemo-demonstrator-jinr-pac-2021-talk` | project_document | https://indico.jinr.ru/event/1810/contributions/11309/attachments/8940/14581/03.2.%20SuperNEMO_PAC_21_Jan_2021.pdf |
| `src:supernemo-demonstrator-jinr-progress-report-2018-2020` | project_document | https://indico.jinr.ru/event/1810/attachments/8934/14574/SuperNEMO_progress-report.pdf |
| `src:supernemo-demonstrator-lyon2025-status-talk` | project_document | https://indico.in2p3.fr/event/36107/contributions/153937/attachments/93125/142497/SuperNEMO_Lyon2025.pdf |

Reused existing: `src:dm-noble-liquid-pandax-4t-official-site` (https://pandax.sjtu.edu.cn/, the PandaX-III website link and the 'R&D effort' wording). Sources for lineage rows: `src:cuoricino-1612-04276`, `src:gerda-hep-ex0404039`, existing `src:cupid-experiment-official-page`, `src:cupid-arxiv-2503-02894`, `src:legend-official-site`, `src:gerda-mpi-hd-official-site`, `src:exo-200-final-results-arxiv-1906`.

### Conflicts (claim / source A / source B / chosen / why)

- **Heidelberg-Moscow end of data taking.** NIM/PLB 2004 abstracts: August 1990 - May 2003; the 2001-2002 claim paper analyses August 1990 - May 2000 (a subset, not the end). Chosen 1990-08 to 2003-05 (abstract of hep-ph/0403018). A review (arXiv:0704.0063) says the first enriched detector was installed in July 1990 and the full set of five in 1995; the interval note carries it.
- **Heidelberg-Moscow hall.** No HdM paper names a hall; a review says the building was 'between Halls A and B' (first preparation in a tent in Hall C). The Atlas hall sites of LNGS share one campus-grade point; Hall A is used with confidence `derived` and a note.
- **Heidelberg-Moscow headline.** 1999 PRL (collaboration, limit 5.7e25 yr) vs 2001 claim (four authors, 'First evidence'). Both recorded and labelled; the claim record says it is by part of the collaboration (GERDA Phase I: 'Part of HdM published a claim to have observed'; CUORICINO PRL: 'contested ... also by other members of the same Heidelberg-Moscow Collaboration'). The later 4.2 sigma paper (hep-ph/0404088) is cited in a note, not recorded. GERDA's own result record (existing) is not edited.
- **NEMO-3 end.** Final-results paper: 'end of running in December 2010' and 'from 2003 to 2010'; June 2025 SuperNEMO talk and JINR 2021 talk: 'NEMO-3: 2003-2011' / 'Ran from 2003 to 2011'. Chosen the paper (December 2010).
- **SuperNEMO source mass.** 2018-2020 report: 6.3 kg of 82Se (expected sensitivity quoted for it); 2024 calorimeter paper and 2025 talk: 6.11 kg (34 foils). Chosen 6.11 kg (latest), 6.3 kg in the note.
- **SuperNEMO status.** No later source than the June 2025 talk ('Now in full data taking mode', 55.62 days accumulated): recorded `active` from 2025-04-10 with that caveat.
- **CANDLES depth.** PRD paper: Kamioka Underground Laboratory 2700 m.w.e.; December 2023 slides: '1000 m.w.e.' (likely rock depth). Chosen 2700 m.w.e. (paper), noted on the site.
- **CANDLES start.** A March 2014 review says 'presently taking data since Spring 2013'; the 2020 paper dates nothing (130.4 live days). Chosen Spring 2013 (approximate, season precision). Ongoing status rests on the December 2023 talk ('current operating detector system').
- **CUORICINO data span and limit.** 2008 PRC: data April 2003 - May 2006 (11.83 kg y, T1/2 > 3.0e24 yr); final paper: April 2003 - June 2008 (19.75 kg y, T1/2 > 2.8e24 yr). Chosen the final paper; the 2008 value is in a note. CUORICINO hall: no CUORICINO paper names it; CUORE-0's text puts the dilution refrigerator that previously hosted CUORICINO in Hall A (derived).
- **PandaX-III mass, shield and status.** 2016 design paper: 200 kg of 136Xe, water-tank shield; 2020 TPC paper and 2023 status paper: about 140 kg, dry shielding system at CJPL-II. Chosen 140 kg (latest) with the 200 kg in notes. Status: 2016 'first module under construction', 2023 'final detector constructed, to be installed at CJPL-II after tests in Shanghai', 2026 PandaX page 'a R&D effort to develop a high pressure gaseous Xenon TPC'. Chosen `construction` (last documented stage); flagged for the integrator.
- **Lineage directions.** Several existing rows said the opposite of what the sources say (see Lineage edits).

### Unresolved fields

- All six: `external.inspire_experiment` empty (inspirehep.net not contacted); collaboration formation dates and membership counts empty; coordinates are campus-grade points (no hall-level coordinate found).
- Official websites: none for HdM (finished experiment), NEMO-3 and SuperNEMO (nemo.in2p3.fr, nemo.lal.in2p3.fr, supernemo.org did not resolve), CUORICINO (cuore.lngs.infn.it failed TLS verification and was not fetched), CANDLES (rcnp page returned no text). Only PandaX-III has a link (the PandaX site).
- CUORICINO: no named collaboration found, so no collaboration record. PandaX-III reuses `collaboration:pandax-4t`.
- SuperNEMO: construction start and commissioning start dates; whether it still takes data on 2026-10-26; no physics result.
- CANDLES: dates before 2013, end of data taking, any half-life limit from a refereed source (a limit of 6.2e22 yr for 131 days x 86 kg is described in a Neutrino 2018 conference abstract that could not be fetched, so it is not recorded).
- PandaX-III: installation date and current status.
- Heidelberg-Moscow: spokesperson (Klapdor-Kleingrothaus is named as spokesman in the NIM paper; no `person:` record because INSPIRE must not be contacted).

### Candidates considered and excluded, or not done

Nothing on the list was left undone. PandaX-III was kept because it has a design report naming its site and a status paper reporting the detector built; it has no physics result, and its status is the weakest of the six. Extra candidates noticed, not created: IGEX (76Ge, the other 76Ge limit, reused by GERDA), CUORE-0 (first CUORE tower, named by CUORE's papers as a predecessor), CUPID-0 and CUPID-Mo (named as CUPID predecessors), ELEGANT VI (48Ca, CANDLES' predecessor design), NEMO-2.

### Lineage edits (only the `lineage` key of each file was changed)

| record | removed | added (quote) |
|---|---|---|
| `experiment:cuore` | {cupid, predecessor} (backwards: CUPID is CUORE's successor) | {cuoricino, predecessor}: "CUORE has been designed on the experience of the predecessor experiments CUORICINO [8] and CUORE-0 [9]" (arXiv:1612.04276, section 3) |
| `experiment:cupid` | {cuore, successor} (derived-type, wrong direction) | {cuore, predecessor}: "Using the information from the predecessor experiments CUORE, CUPID-0, and CUPID-Mo" (cupidexperiment.org/experiment); {cuore, upgrade_of}: "CUPID, the CUORE Upgrade with Particle IDentification" (arXiv:2503.02894) |
| `experiment:gerda` | {legend, predecessor} (backwards) | {heidelberg-moscow, predecessor}: "The setup allows to scrutinize with high significance on a short time scale the current evidence for neutrinoless double beta decay of 76 Ge using the existing 76 Ge detectors from the previous Heidelberg-Moscow and Igex experiments." (arXiv:hep-ex/0404039, abstract) |
| `experiment:legend` | {gerda, successor}, {majorana-demonstrator, successor} (derived-type) | {gerda, predecessor} and {majorana-demonstrator, predecessor}: "By combining the technological expertise and experience from the GERDA experiment and MAJORANA DEMONSTRATOR, LEGEND is expected to reach a design sensitivity two orders of magnitude greater than its predecessors." (legend-exp.org); the GERDA page adds "The LEGEND collaboration took over the setup with the goal to increase the amount of enriched Ge detectors to about 200 kg in the same cryostat." |
| `experiment:majorana-demonstrator` | {legend, predecessor} (backwards) | nothing (the correct row lives on legend) |
| `experiment:exo-200` | {nexo, predecessor} (backwards) | nothing (the correct row lives on nexo) |
| `experiment:nexo` | {exo-200, successor} (derived-type, wrong direction) | {exo-200, predecessor}: "nEXO [38, 39], the planned tonne-scale successor to EXO-200" (arXiv:1906.02723 conclusion) |

The nexo edit goes beyond the six records named in the brief (it was needed so as not to leave a false row); the lead should keep or revert it with the others.

## Part 5 (F5): direct neutrino-mass experiments (Mainz, Troitsk, ECHo, HOLMES)

Scope: Mainz neutrino-mass experiment, Troitsk nu-mass, ECHo, HOLMES (kind `neutrino_mass`, `topic:neutrino-mass-direct`), their facilities, sites, detectors, collaborations and headline results, plus the KATRIN lineage rows. All four meet the mandatory bar at tier D, researched `partial`; results `full`.

Method: every quote in the written records was checked verbatim against the fetched text of its cited source at write time (helper library `atlaslib`, same normaliser as `scripts/atlas_quote_check.py`), then re-checked with the repository's checker on the cached sources: `--only mainz` 24 verbatim, `troitsk` 24, `echo` 23, `holmes` 21, `inr-troitsk` 2, `kirchhoff` 2, `milano-bicocca` 2, `johannes-gutenberg-university-mainz` 2: all verbatim, 0 number flags. No inspirehep.net, Neon or Vercel access, no Wikipedia, no git commands.

### Entities written

| id | type | start / end / status / site |
|---|---|---|
| experiment:mainz-neutrino-mass | experiment | 1991 / 2001 / completed / site:mainz-institute-of-physics |
| detector:mainz-neutrino-mass-detector | detector | MAC-E filter; same intervals |
| result:mainz-final-neutrino-mass-limit-2004 | result | limit, 2004-12-20 (arXiv v1) |
| facility:johannes-gutenberg-university-mainz | facility (new) | research_laboratory; 1991 / open / active |
| site:mainz-institute-of-physics | site (new) | campus-grade point |
| experiment:troitsk-nu-mass | experiment | 1985 / open / active (uncertain after 2017) / site:inr-troitsk-nu-mass-facility |
| detector:troitsk-nu-mass-detector, collaboration:troitsk-nu-mass | detector, collaboration | |
| result:troitsk-neutrino-mass-limit-2011, result:troitsk-kev-sterile-neutrino-limits-2017 | results | limit, 2011-08-25 and 2017-03-31 (arXiv v1) |
| facility:inr-troitsk, site:inr-troitsk-nu-mass-facility | facility, site (new) | research_laboratory; campus-grade point |
| experiment:echo | experiment | 2013-06 / open / active / site:kirchhoff-institute-for-physics-heidelberg |
| detector:echo-detector, collaboration:echo | detector, collaboration | |
| result:echo-1k-neutrino-mass-limit-2025 | result | limit, 2025-09-03 (arXiv v1) |
| facility:kirchhoff-institute-for-physics, site:kirchhoff-institute-for-physics-heidelberg | facility, site (new) | research_laboratory; campus-grade point |
| experiment:holmes | experiment | 2013 / open / active / site:milano-bicocca-university-campus |
| detector:holmes-detector, collaboration:holmes | detector, collaboration | |
| result:holmes-neutrino-mass-limit-2025 | result | limit, 2025-03-10 (arXiv v1) |
| facility:university-of-milano-bicocca, site:milano-bicocca-university-campus | facility, site (new) | research_laboratory; campus-grade point |

Counts: 4 experiments, 4 detectors, 3 collaborations (none for Mainz), 5 results, 4 facilities, 4 sites, 19 sources (15 literature or web, 4 geocoder). `experiment:katrin` edited (lineage only).

New facilities: `facility:johannes-gutenberg-university-mainz`, `facility:inr-troitsk`, `facility:kirchhoff-institute-for-physics`, `facility:university-of-milano-bicocca`.

#### Intervals and the evidence behind each date

#### Mainz neutrino-mass experiment (`experiment:mainz-neutrino-mass`, kind `neutrino_mass`, status `completed`, tier D)
Facility: `facility:johannes-gutenberg-university-mainz`; site: `site:mainz-institute-of-physics`; detector `detector:mainz-neutrino-mass-detector`; collaboration: none (see notes); results: mainz-final-neutrino-mass-limit-2004

| interval | status | start | end | confidence | source | quote |
|---|---|---|---|---|---|---|
| phase I data taking | active | 1991 | 1994 | approximate | https://arxiv.org/abs/hep-ex/0412056 | Our spectrometer yielded first results in 1991 |
| phase II improvement programme (new frozen-T2 source, flow cryostat, background reduction) | upgrade | 1995 | 1997 | verified | https://arxiv.org/abs/hep-ex/0412056 | we performed in the years 1995-97 a substantial improvement program |
| phase II data taking | active | 1997 | 2001 | verified | https://arxiv.org/abs/hep-ex/0412056 | Extensive data taking took place in the years 1997 to 2001. |
| completed | completed | 2001 | None | approximate | https://arxiv.org/abs/hep-ex/0412056 | Extensive data taking took place in the years 1997 to 2001. |

#### Troitsk nu-mass (`experiment:troitsk-nu-mass`, kind `neutrino_mass`, status `active`, tier D)
Facility: `facility:inr-troitsk`; site: `site:inr-troitsk-nu-mass-facility`; detector `detector:troitsk-nu-mass-detector`; collaboration: ['collaboration:troitsk-nu-mass']; results: troitsk-kev-sterile-neutrino-limits-2017, troitsk-neutrino-mass-limit-2011

| interval | status | start | end | confidence | source | quote |
|---|---|---|---|---|---|---|
| tritium beta-decay neutrino-mass measurements | active | 1985 | 2005 | verified | https://arxiv.org/abs/1504.00544 | The corresponding measurements were done from 1985 to 2005 [24, 25] and the final results of these efforts were published in [19]. |
| proposal of the keV sterile-neutrino search at the Troitsk nu-mass facility | proposed | 2015-04 | 2017-03 | approximate | https://arxiv.org/abs/1504.00544 | We propose a new experiment to search for a sterile neutrino in a few keV mass range at the "Troitsk nu-mass" facility. |
| keV sterile-neutrino search: first measurements and continued operation | active | 2017-03 | None | uncertain | https://arxiv.org/abs/1703.10779 | We present the first measurements of tritium beta-decay spectrum in the electron energy range 16-18.6 keV. |

#### ECHo (`experiment:echo`, kind `neutrino_mass`, status `active`, tier D)
Facility: `facility:kirchhoff-institute-for-physics`; site: `site:kirchhoff-institute-for-physics-heidelberg`; detector `detector:echo-detector`; collaboration: ['collaboration:echo']; results: echo-1k-neutrino-mass-limit-2025

| interval | status | start | end | confidence | source | quote |
|---|---|---|---|---|---|---|
| proposal and design of ECHo | proposed | 2013-06 | 2017-06 | approximate | https://arxiv.org/abs/1306.2655 | In this talk we present the Electron Capture 163-Ho experiment ECHo, which aims to investigate the electron neutrino mass in the sub-eV range |
| ECHo-1k phase (medium-scale experiment, about 1 kBq of 163Ho) | active | 2017-06 | 2023-01 | approximate | https://link.springer.com/article/10.1140/epjst/e2017-70071-y | the strategies we have adopted to carry on the present medium scale experiment, ECHo-1K |
| ECHo-100k phase (aims at a sensitivity below 2 eV) | active | 2023-01 | None | approximate | https://arxiv.org/abs/2301.06455 | The results of the first phase of the experiment, ECHo-1k, have paved the way for the current phase, ECHo-100k, which aims at a sensitivity below 2 eV on the effective electron neutrino mass. |

#### HOLMES (`experiment:holmes`, kind `neutrino_mass`, status `active`, tier D)
Facility: `facility:university-of-milano-bicocca`; site: `site:milano-bicocca-university-campus`; detector `detector:holmes-detector`; collaboration: ['collaboration:holmes']; results: holmes-neutrino-mass-limit-2025

| interval | status | start | end | confidence | source | quote |
|---|---|---|---|---|---|---|
| funded by the European Research Council | approved | 2013 | 2014-02 | approximate | https://arxiv.org/abs/1412.5060 | HOLMES was funded in 2013 by the European Research Council with an Advanced Grant awarded to Prof. S. Ragazzi. |
| ERC grant period: design and set-up of the experiment | construction | 2014-02 | 2025-03 | approximate | https://arxiv.org/abs/1412.5060 | The Italian Istituto Nazionale di Fisica Nucleare (INFN) is the Host Institution for the grant which started on February 1st 2014 and will end on January 31st 2019. |
| physics runs and first result | active | 2025-03 | None | approximate | https://arxiv.org/abs/2503.19920 | With a total of 7 × 107 decay events recorded over two months and a Bayesian statistical analysis, we derive an upper limit of mβ < 27 eV/c2 at 90% credibility. |



#### Coordinates (all campus-grade, `kind: campus`, `confidence: approximate`; none labelled detector or underground_lab)

| site | lat, lon | precision (m) | source | locator |
|---|---|---|---|---|
| `site:mainz-institute-of-physics` | 49.99056, 8.23448 | 300 | https://nominatim.openstreetmap.org/search?q=Staudingerweg+7+Mainz&format=jsonv2&limit=1 | Nominatim result for "Staudingerweg 7 Mainz" (way 33817570): Institut für Physik, 7, Staudingerweg, Oberstadt, Mainz, Rheinland-Pfalz, 55128, Deutschland |
| `site:inr-troitsk-nu-mass-facility` | 55.46379, 37.27573 | 1000 | https://nominatim.openstreetmap.org/search?q=%D0%98%D0%BD%D1%81%D1%82%D0%B8%D1%82%D1%83%D1%82+%D1%8F%D0%B4%D0%B5%D1%80%D0%BD%D1%8B%D1%85+%D0%B8%D1%81%D1%81%D0%BB%D0%B5%D0%B4%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B9+%D0%A0%D0%90%D0%9D+%D0%A2%D1%80%D0%BE%D0%B8%D1%86%D0%BA&format=jsonv2&limit=1 | Nominatim result for "Институт ядерных исследований РАН Троицк" (way 447226735): Институт ядерных исследований РАН, улица Академика Черенкова, Троицк, район Троицк, Москва, Центральный федеральный округ, 108840, Россия |
| `site:kirchhoff-institute-for-physics-heidelberg` | 49.41629, 8.67192 | 300 | https://nominatim.openstreetmap.org/search?q=Kirchhoff-Institut+f%C3%BCr+Physik+Im+Neuenheimer+Feld+227+Heidelberg&format=jsonv2&limit=1 | Nominatim result for "Kirchhoff-Institut für Physik Im Neuenheimer Feld 227 Heidelberg" (relation 19328): Kirchhoff-Institut für Physik, 227, Im Neuenheimer Feld, Neuenheimer Feld, Neuenheim, Heidelberg, Baden-Württemberg, 69120, Deutschland |
| `site:milano-bicocca-university-campus` | 45.51367, 9.21131 | 600 | https://nominatim.openstreetmap.org/search?q=Universit%C3%A0+degli+Studi+di+Milano+Bicocca+Piazza+della+Scienza&format=jsonv2&limit=1 | Nominatim result for "Università degli Studi di Milano Bicocca Piazza della Scienza" (way 25102933): Università degli Studi di Milano Bicocca, Piazza della Scienza, Borgo Pirelli, Bicocca, Municipio 9, Milano, Rodano, Milano, Lombardia, 20126, Italia |

### Sources added

| id | type | URL |
|---|---|---|
| `src:echo-1306-2655` | arxiv | https://arxiv.org/abs/1306.2655 |
| `src:echo-1309-5214` | arxiv | https://arxiv.org/abs/1309.5214 |
| `src:echo-2107-13528` | arxiv | https://arxiv.org/abs/2107.13528 |
| `src:echo-2111-09945` | arxiv | https://arxiv.org/abs/2111.09945 |
| `src:echo-2301-06455` | arxiv | https://arxiv.org/abs/2301.06455 |
| `src:echo-2509-03423` | arxiv | https://arxiv.org/abs/2509.03423 |
| `src:echo-epjst-2017-gastaldo` | journal_article | https://link.springer.com/article/10.1140/epjst/e2017-70071-y |
| `src:echo-kip-heidelberg-site` | official_experiment_site | https://www.kip.uni-heidelberg.de/echo/ |
| `src:geo-echo-nominatim-kip-heidelberg` | geocoder | https://nominatim.openstreetmap.org/search?q=Kirchhoff-Institut+f%C3%BCr+Physik+Im+Neuenheimer+Feld+227+Heidelberg&format=jsonv2&limit=1 |
| `src:geo-holmes-nominatim-milano-bicocca` | geocoder | https://nominatim.openstreetmap.org/search?q=Universit%C3%A0+degli+Studi+di+Milano+Bicocca+Piazza+della+Scienza&format=jsonv2&limit=1 |
| `src:geo-mainz-nominatim-institut-fuer-physik` | geocoder | https://nominatim.openstreetmap.org/search?q=Staudingerweg+7+Mainz&format=jsonv2&limit=1 |
| `src:geo-troitsk-nominatim-inr` | geocoder | https://nominatim.openstreetmap.org/search?q=%D0%98%D0%BD%D1%81%D1%82%D0%B8%D1%82%D1%83%D1%82+%D1%8F%D0%B4%D0%B5%D1%80%D0%BD%D1%8B%D1%85+%D0%B8%D1%81%D1%81%D0%BB%D0%B5%D0%B4%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B9+%D0%A0%D0%90%D0%9D+%D0%A2%D1%80%D0%BE%D0%B8%D1%86%D0%BA&format=jsonv2&limit=1 |
| `src:holmes-1412-5060` | arxiv | https://arxiv.org/abs/1412.5060 |
| `src:holmes-1807-09269` | arxiv | https://arxiv.org/abs/1807.09269 |
| `src:holmes-2503-19920` | arxiv | https://arxiv.org/abs/2503.19920 |
| `src:mainz-neutrino-mass-hep-ex0412056` | arxiv | https://arxiv.org/abs/hep-ex/0412056 |
| `src:troitsk-nu-mass-1108-5034` | arxiv | https://arxiv.org/abs/1108.5034 |
| `src:troitsk-nu-mass-1504-00544` | arxiv | https://arxiv.org/abs/1504.00544 |
| `src:troitsk-nu-mass-1703-10779` | arxiv | https://arxiv.org/abs/1703.10779 |

### Conflicts (claim / source A / source B / chosen / why)

- **Mainz upper limit confidence level.** Abstract and section 6.3: m(nu_e) <= 2.3 eV/c^2 at 95% confidence level. Section 7 (conclusion) writes the same 2.3 eV/c^2 as "(90% C.L.)". Chosen 95% (abstract, final-result section, and the paper's own statement that (34) is the final limit).
- **Mainz data-taking years.** Abstract: "Extensive data taking took place in the years 1997 to 2001". Section 7: "Data taking on the search for the neutrino mass covered the years 1998 to 2001". Chosen 1997-2001 (abstract; the 1997 runs were the first with the improved setup). Phase I start: only "first results in 1991" and "the last spectrum from phase I taken in 1994" are stated, so phase I is 1991-1994 at year precision, approximate.
- **Troitsk measurement years.** The group's 2015 status paper: measurements "done from 1985 to 2005". The final-results paper (PRD 84, 112003): "The whole data set acquired from 1994 to 2004 was reanalyzed". Chosen 1985-2005 for the programme interval (verified, the group's own wording) and recorded 1994-2004 in the interval note.
- **Troitsk limit.** One abstract gives three 95% CL numbers: sensitivity limit 2.2 eV, Bayesian limit 2.12 eV, Feldman-Cousins limit 2.05 eV. The key value is the Bayesian 2.12 eV; the other two are in the notes.
- **HOLMES result date.** The arXiv abstract page says "[v1] Mon, 10 Mar 2025"; the paper's identifier 2503.19920 suggests a later March date. Chosen the date printed in the submission history. Published as Phys. Rev. Lett. 135, 141801 (2025) per the abstract page.
- **Mainz as a facility.** The brief names facility:johannes-gutenberg-university-mainz; the existing record `institution:johannes-gutenberg-university-mainz` is a different entity type and is not duplicated (validator reports no A20 collision).

### Unresolved fields

- **All four:** `external.inspire_experiment` empty (inspirehep.net not contacted); no INSPIRE or Greybook ids; all tier D, `researched: partial`.
- **Mainz:** no official website (finished experiment), no named collaboration (the authors are the Institut fuer Physik, Mainz, group, so no collaboration record); month of the phase I start; end of phase III (a KATRIN-preparation background study that was "presently running" in 2004); hall-level coordinate.
- **Troitsk:** whether the keV-sterile search still takes data on 2026-10-26 (last dated evidence is the March 2017 paper; a conference abstract mentions a planned TRISTAN-Troitsk upgrade); the dates of the keV-sterile measurements; no official website; hall coordinate; the hull has a gap 2006-2015 (no data taking recorded; the 2011-2013 papers re-analyse old data), which the validator reports as an A12 warning on the experiment, detector and collaboration.
- **ECHo:** no source dates the ECHo-1k data taking, the ECHo-100k start, or the approval. The three phase intervals are approximate: proposal from the earliest paper found (2013-06), ECHo-1k from the June 2017 overview that calls it "the present medium scale experiment", ECHo-100k from the January 2023 paper that calls it "the current phase". The ECHo-1k result is a preprint (no journal reference found). Location of the cryostat that measured the spectrum is not stated (placement at the Kirchhoff Institute is approximate: the institute coordinates the collaboration and fabricates the detectors).
- **HOLMES:** no official website found (several candidate hosts timed out or returned 404); dates of the two physics runs; the boundary between construction and operation is the March 2025 report date (approximate); where the 2025 runs were taken (the 2015 paper says the test-bed is set up at the University of Milano-Bicocca laboratory; the ERC grant host institution is INFN); current operation on 2026-10-26 not confirmed.

### Candidates excluded or not done

None of the four was excluded. Noticed but not created (outside the brief): the Los Alamos tritium experiment, Livermore and Zurich magnetic-spectrometer experiments (named in the Mainz paper), TRISTAN-Troitsk, KATRIN++; ECHo's isotope sources (ILL Grenoble) and ion implantation (RISIKO, Mainz) are not recorded as sites.

### Lineage edits

- `experiment:katrin` (only its `lineage` changed; verified with `git diff`): added `{experiment:mainz-neutrino-mass, predecessor}` and `{experiment:troitsk-nu-mass, predecessor}`, both citing `src:mainz-neutrino-mass-hep-ex0412056`, section 7: "It combines the expertise from the foregoing experiments at Los Alamos [72], Mainz and Troitsk with the strength of a national laboratory including expertise in handling large amounts of tritium." (the same paper calls KATRIN "the followup experiment").
- New rows on new records: `experiment:mainz-neutrino-mass` complementary `experiment:troitsk-nu-mass` ("They were proposed and realized independently in Mainz [21] and Troitsk [22,23]."); `experiment:echo` complementary `experiment:holmes` ("... is presently pursued by two collaborations, ECHo [2] and HOLMES [3].", `src:echo-2107-13528`).

## Conflicts, unresolved fields and exclusions

Per experiment, in Parts 1 to 5 above. In short: no hall-level coordinate was found for any of the 23 (every site is a campus-grade `approximate` point, none is labelled `detector` or `underground_lab`); no `external.inspire_experiment` (inspirehep.net not contacted); no collaboration formation dates or rosters; official websites exist only for JSNS2, ECHo, PandaX-III (the PandaX site) and the Baksan telescope (an INR page). Old CERN, Fréjus, NUSEX and KGF papers are mostly paywalled or pre-arXiv: their headline results are cited through repository copies of the abstracts (Sapienza IRIS for CHARM and CHARM II, the RWTH-hosted PDFs for Fréjus, NASA NTRS and OSTI for NUSEX) and the unfetchable ones are listed as unrecorded, not guessed. Excluded: none of the assigned candidates; PandaX-III is the weakest inclusion (a design report naming CJPL plus a 2023 status paper reporting the detector built; the 2026 PandaX site calls it "a R&D effort"). Noticed but not created (outside the brief): IGEX, CUORE-0, CUPID-0, CUPID-Mo, ELEGANT VI, NEMO-2, LSD and LVD at Mont Blanc, HPW, INO, the Los Alamos tritium experiment, TRISTAN-Troitsk, a West Area beamline and hall site.

## For the integrator

- **Judgement calls to keep or overturn.**
  - PandaX-III is `construction` (last documented stage); `proposed` is defensible given the PandaX site's wording.
  - `result:kgf-proton-decay-claim-2000` (title "Experimental evidence for G.U.T. Proton Decay") is typed `anomaly`: the collaboration's own paper admits that other experiments set limits near 1e33 yr, which contradicts its 1e31 yr claim. `result:heidelberg-moscow-evidence-claim-2001` is typed `evidence` because its abstract says "first evidence"; its record states that it is a claim by part of the collaboration and cites the GERDA and CUORICINO papers for the dispute. Its date is the arXiv v1 date (2002-01-24); the journal issue is dated 2001 (the slug follows the journal year).
  - NUSEX's end of data taking is unknown: the `completed` interval is a date window (1985-03 to 2004-07).
  - Soudan 2 is placed at the surveyed MINOS-hall point as an `approximate` stand-in (a different cavern of the same mine; noted on the placement).
- **Backlog the earlier stream's note anticipated.** `beamline:wanf` and a West Area site once a source gives coordinates (the CHORUS, NOMAD, CDHS, CHARM and CHARM II detectors all sit at the approximate `site:cern-meyrin`); `experiment:gargamelle` (same West Area programme) has no detector placement; `collaboration:pandax-4t` could be renamed `collaboration:pandax`; a Modane hall site for SuperNEMO when a coordinate is sourced; `experiment:kamiokande` and `experiment:super-kamiokande` could carry `topic:nucleon-decay` (their cited pages were unreachable today, so they were not edited).
- **Validator warnings added** (all tolerated kinds): `coordinate-kind-approximate` (8 new sites), `experiment-without-active-beam` (15, no accelerator or beamline for underground or table-top experiments), two `unknown-spec-key` (`target_distance` on JSNS2 and CCM: the A21 floor for `baseline` is 100 m, so a 20 to 24 m source distance is stored under another key), `hull-gap` (Troitsk 2006-2015 on three records; `facility:soudan-underground-laboratory` 2001-07 to 2003-06, because the laboratory's own dates could not be fetched). Cleared: three `experiment-before-facility` warnings (CHOOZ, CDMS-II, SAGE) and 46 "not in the atlas yet" informational lines.
- **A test already failing on the integration branch, unrelated to this stream:** `tests/test_atlas_tours.py::test_route_types_match_state_js` (`state.js` `TYPE_PREFIX` contains `view`, which `ROUTABLE_TYPES` in `hepgraph/atlas/tours.py` does not). Neither file was touched here.
- **The atlas bundle** is now 1.67 MB raw (301 KB gzipped) for `atlas.json` plus `manifest.json`: still under the 2.5 MB / 500 KB failure thresholds, over the 400 KB pilot budget (warning only).

## Checks run

- `python -m hepgraph.atlas.validate`: **0 errors, 1806 warnings, 4 informational** (baseline on the integration branch before this stream: 0 errors, 1780 warnings, 50 informational).
- `python -m hepgraph.atlas.build`: succeeded (83 files; 250 experiments, 82 facilities, 145 sites, 249 results, 48 topics); `static/atlas/generated` was restored with `git checkout -- static/atlas/generated` and the build's untracked outputs removed before committing.
- `python -m pytest -q`: 728 passed, 139 skipped (PostgreSQL-backed), 1 failed (the unrelated tours test above).
- `scripts/atlas_quote_check.py --offline` over the fetch cache: 523 quotes in the new files, all verbatim, no number flags; the forks also ran it per slug on their own records.
- No inspirehep.net, Neon or Vercel access; no push; `cds.cern.ch`'s bot check was not touched.
