# Stream log: follow-ups (integration data stream)

Owner tag `followups`. Branch `atlas-followups`, cut from `atlas-next` at `e9d8f7b`. Registry file: `data/atlas/coverage/followups.json`. Every date and quote below was re-read on 2026-10-26 from the page or PDF named; a script (`SourceText.classify` from `scripts/atlas_quote_check.py`, run on the fetched text) checked the 35 quote fields added or changed on this branch: 33 are verbatim, and the two `near` ones are the same ALEPH abstract sentence in `claim` and in `key_value_text`, whose scan has an OCR text layer (see the LEP section).

## Scope

Seven small data follow-ups other streams left for the integrator:

1. Homestake dates sourced from Davis's Nobel lecture and the 1998 ApJ paper instead of Wikipedia.
2. The LEP light-neutrino result's `claim` re-sourced from the ALEPH paper.
3. NuMI prose made to agree with the 735.3 km baseline.
4. Five lineage rows from `COSMIC_2.md` Part 6.
5. Earlier facility start dates for KIT, Roque de los Muchachos and the Fred Lawrence Whipple Observatory.
6. `facility:hanford-site` with the 1953 Cowan-Reines Hanford attempt, and Columbia University pointed at Nevis.
7. The SLAC linac and PETRA feed links: skipped, see the end of this log.

## Results

| task | result |
| --- | --- |
| 1 Homestake | Intervals on `experiment:homestake`, `detector:homestake` and `collaboration:homestake` now rest on the Davis lecture and the 1998 paper. The facility sheet's operating years, derived from the active intervals, read 1967-1994 (were 1970-1994). |
| 2 LEP | `claim` and the headline quote of `result:lep-three-neutrino-species-1989` quote the printed ALEPH abstract (journal article, rank 10), not the research-portal transcription (rank 12). |
| 3 NuMI | `direction` now says 735.3 km and cites the MINOS detector paper; the note gives both quotes. |
| 4 Lineage | Five `predecessor` rows added; the successors derive at build. |
| 5 Facilities | Three facility records gain an earlier sourced first interval; 5 `experiment-before-facility` warnings cleared. |
| 6 Hanford, Nevis | New facility, site and experiment (plus a lineage row and registry row); `institution:columbia-university` points to `facility:nevis-laboratories`. |
| 7 Chains | Skipped on request. |

## Entities written

New: `facility:hanford-site`, `site:hanford-site`, `experiment:cowan-reines-hanford-1953`, nine sources (`src:fu-*`), `data/atlas/coverage/followups.json`.
Changed: the three Homestake records, `result:lep-three-neutrino-species-1989`, `beamline:numi`, `experiment:{hawc,magic,h-e-s-s,veritas,telescope-array}` (lineage), `facility:{kit-karlsruhe,roque-de-los-muchachos-observatory,fred-lawrence-whipple-observatory}`, `experiment:{cowan-reines-neutrino,kascade,hegra,milagro,agasa,whipple-10m}` (lineage or stale notes), `institution:columbia-university`, the Homestake, HAWC and tour records named below, `coverage/discoveries.json` (one stale missing-field removed), `ID_REGISTRY.md`, and one test.

### Dated values (start / end / status, with the URL and quote behind each)

#### `experiment:homestake` (and the same lifecycle on `detector:homestake`, `collaboration:homestake`)

| interval | status | start | end | source and quote |
| --- | --- | --- | --- | --- |
| construction | construction | 1965 | 1967 | Cleveland et al. 1998, section 1 (https://iopscience.iop.org/article/10.1086/305343/pdf): "The Homestake solar neutrino experiment was built in the period 1965–1967" |
| operation | active | 1967 | 1994 (approximate) | Davis, Nobel Lecture 2002, p. 68 (https://www.nobelprize.org/uploads/2018/06/davis-lecture.pdf): "The Homestake experiment became operational in 1967." The end is the end of the data set below (see conflicts). |
| standard data set (rise-time counting), `kind: phase` | active | 1970 | 1994 | Cleveland et al. 1998, section 7.1: "Our standard data set consists of 108 solar neutrino observations made between 1970 and 1994." Start also: Davis, p. 72: "We began using this new system in 1970, and after about one year of observations, a clear neutrino signal was observed." |
| completed | completed | 1994 (approximate) | | Same 7.1 quote; a bound, not a shutdown date. |

The detector's placement now starts 1967 (Davis; the 1998 paper, section 3.1: "The Homestake Solar Neutrino Observatory is located in the Homestake Gold Mine, at Lead, South Dakota"). The experiment's host-facility role cites the same sentence and SURF's "Our story" (https://sanfordlab.org/our-story): "SURF is indelibly linked to the history of the Homestake Mine, which operated from 1876 until 2001." Source records `src:homestake-1998-flux-measurement` (now the PDF URL, full text, with a verbatim excerpt; the old excerpt was a paraphrase and the old URL sat behind a bot challenge) and `src:rf06-davis-nobel-lecture-2002` were refreshed. The tour note and `tests/test_atlas_tours.py` referred to the old Wikipedia-only interval and were updated (the test now puts a rank-12 source on a real interval).

The facility sheet text is `operatingYears()` in `static/atlas/js/export.js`: the start of the first `active` interval to the end of the last one. It is not stored anywhere else. A build to a scratch directory and the same arithmetic give "1967–1994", from these intervals.

#### `result:lep-three-neutrino-species-1989`

ALEPH, Phys. Lett. B 231, 519-529 (1989), abstract on printed p. 521, read from the scanned article held by the Scuola Normale Superiore repository (https://ricerca.sns.it/bitstream/11384/1735/4/Determination-light-neutrino.pdf; `src:fu-aleph-nuspecies-plb231-1989`, journal article, rank 10): "Within the constraints of the standard electroweak model, the number of light neutrino species is found to be Nν = 3.27 ± 0.30. This result rules out the possibility of a fourth type of light neutrino at 98% CL." The page image was read to check the number and the symbols; the scan's text layer renders them as "Nv= 3.27 + 0.30", which is why the checker class is `near` (0.97), not `verbatim`.

#### `beamline:numi`

MINOS detector paper (https://arxiv.org/pdf/0805.3170), section 1: "735.3 km from the NuMI beam production target at Fermilab"; section 6.5: "735.3380 km from the upstream end of the first horn of the neutrino beamline" and "as the beam travels approximately NNW". NuMI beam paper (https://arxiv.org/pdf/1507.06690), section 1: "encountering the MINOS Far Detector (FD) 734 km away in the Soudan Mine in Minnesota"; section 2.1: "To point towards the Soudan Laboratory the proton beam had to be inclined downward by 58 mrad."

#### Lineage rows (all `predecessor`, on the successor, `verified_at` 2026-10-26)

| on | to | URL | quote |
| --- | --- | --- | --- |
| `experiment:hawc` | `experiment:milagro` | https://arxiv.org/pdf/1310.0074, ICRC 2013 contribution "HV Cable Manufacture and Testing for the HAWC observatory", PDF p. 3 (page image read: the paper prints "HAWCs", no apostrophe) | "This cable type was successfully used for the outriggers in the MILAGRO experiment, HAWCs predecessor." |
| `experiment:magic` | `experiment:hegra` | https://www.mpi-hd.mpg.de/hfm/HEGRA/ | "A successor to the HEGRA Cherenkov telescopes is being built up at the HEGRA site: MAGIC." |
| `experiment:h-e-s-s` | `experiment:hegra` | same page | "A direct successor to the stereoscopic system of Cherenkov telescopes is the H.E.S.S. experiment." |
| `experiment:veritas` | `experiment:whipple-10m` | https://veritas.sao.arizona.edu/whipple | "The predecessor to VERITAS (Very Energetic Radiation Imaging Telescope Array System), this telescope was in operation from 1968 until its decommissioning in 2013" |
| `experiment:telescope-array` | `experiment:agasa` | https://www.icrr.u-tokyo.ac.jp/en/facility/4223/ | "while handing over the observation to its larger scale hybrid successor Telescope Array (TA) in Utah, USA" |

The relation is `predecessor` in all five: each quote calls the earlier experiment the predecessor or the later one its successor; none supports `complementary` or `upgrade_of`. The HEGRA page does not name the HEGRA telescopes in the H.E.S.S. sentence; the row's note says it follows the page's description of them.

#### Facilities

| facility | interval | status | start | end | source and quote |
| --- | --- | --- | --- | --- | --- |
| `facility:kit-karlsruhe` | Forschungszentrum Karlsruhe (predecessor institution on Campus North) | active | 1956 | 2009-10-01 | KIT history page (https://www.kit.edu/kit/english/history.php): "the fathers establishing the Kernreaktor Bau- und Betriebsgesellschaft mbH (Nuclear Reactor Construction and Operation Company), the later Kernforschungszentrum Karlsruhe (KfK, Karlsruhe Nuclear Research Center), in 1956 entered new territory" |
| | KIT (merger) | active | 2009-10-01 | | same page: "On October 01, 2009 did both institutions merge into the new legal entity of KIT." Campus North: "The premises of Campus North in Eggenstein-Leopoldshafen, the former Karlsruhe Research Center." |
| | hosting KATRIN (unchanged) | active | 2019 | | `src:katrin-official-site` (note reworded) |
| `facility:roque-de-los-muchachos-observatory` | observatory officially inaugurated | active (approximate) | 1985 | | IAC history (https://www.iac.es/en/about-us/history): "In 1985 the Official Inauguration of the Instituto de Astrofísica de Canarias and the Teide and Roque de los Muchachos Observatories took place" |
| `facility:fred-lawrence-whipple-observatory` | established as the Smithsonian Mount Hopkins Observatory | active | 1966 | | CfA FLWO page (https://www.cfa.harvard.edu/flwo): "From its establishment in 1966 as the Smithsonian Mount Hopkins Observatory, FLWO has hosted a world-class suite of telescopes designed for a wide variety of purposes." Renamed: "During his tenure, SAO developed the Mount Hopkins Observatory, which was renamed for Whipple in 1981." |

KASCADE (1996) and KASCADE-Grande (2003) stood on the Forschungszentrum site before KIT existed as a legal entity; the KASCADE page itself says "The experiment was situated on site of the former Forschungszentrum Karlsruhe (now Karlsruhe Institute of Technology, KIT". The KIT facility therefore starts with the predecessor institution, as the brief suggested, and the facility note says so. The Whipple 10 m telescope's earliest interval (construction, 1966) now equals the observatory's start, so it no longer warns.

#### Hanford

| entity | status | start | end | source and quote |
| --- | --- | --- | --- | --- |
| `facility:hanford-site`: plutonium production | active | 1943 | 1989 | https://www.hanford.gov/page.cfm/hanfordMission: "Plutonium production took place between 1943 and 1989." B Reactor page (https://www.hanford.gov/page.cfm/BReactor): "Construction of B Reactor began in October 1943. Fuel was loaded into the reactor on Sept. 13, 1944, and it reached full power in February 1945." |
| `facility:hanford-site`: environmental cleanup mission | active | 1989 | | mission page: "Hanford cleanup began in 1989, when a landmark agreement was reached between DOE, the U.S. Environmental Protection Agency, and the Washington State Department of Ecology." |
| `site:hanford-site` | | | | 46.5328494, -119.4931078, campus, approximate, 20 km: Nominatim, OSM relation 14064419 (the boundary centroid, as for `site:savannah-river-site`): `"osm_id":14064419,"lat":"46.5328494","lon":"-119.4931078"` |
| `experiment:cowan-reines-hanford-1953`: Hanford run | active | spring 1953 (April, earliest March, latest May) | by the end of 1953 (bound) | Reines Nobel Lecture (https://www.nobelprize.org/uploads/2018/06/reines-lecture.pdf), "The Hanford Experiment": "Our entourage arrived at Hanford in the spring of 1953." |
| `experiment:cowan-reines-hanford-1953`: completed | completed | by the end of 1953 (bound, approximate) | | Science 124, 103 (https://www.nssp.uni-saarland.de/lehre/Vorlesung/Kernphysik_SS19/History/Papers/Cowan_Reines.pdf): "A tentative identification of the free neutrino was made in an experiment performed at Hanford (1) in 1953." Lecture: "After a few months of operation we concluded that we had done all we could in the face of an enormous reactor-independent background." |

The new experiment meets the mandatory bar: identity (name, alias, kind), time (two intervals), place (host on `facility:hanford-site`, a located site), content (two topics, summaries, no website exists, two authoritative sources, no collaboration exists, lineage on the successor), tracking (`coverage/followups.json`, tier D). Key specs: 300 L scintillator and 90 photomultiplier tubes ("We had a 300 liter liquid scintillator viewed by 90, 2 inch photomultiplier tubes."). `experiment:cowan-reines-neutrino` carries the `predecessor` row ("Encouraged by the Hanford results, we considered how it might be possible to build a detector which would be even more discriminating in its rejection of background."). The `completed` start is the end of 1953 so that no active interval starts after the terminal one (A3).

`institution:columbia-university` now has `facility_id: facility:nevis-laboratories`, supported by the Nevis page (https://www.nevis.columbia.edu/what-we-do.html): "Nevis Labs is a physics research facility operated by Columbia University's Physics Department."

## Conflicts

| claim | source A | source B | chosen | why |
| --- | --- | --- | --- | --- |
| Homestake start | Wikipedia and the 1998 abstract: 1970 | Davis: operational in 1967; 1998 paper: built 1965-1967 | both, as different intervals: operation from 1967, standard data set from 1970 | 1970 is when rise-time counting began and the 108-observation data set starts; 1967 is when the detector first ran |
| Homestake end | Wikipedia: "operated continuously from 1970 until 1994" | 1998 paper (accepted October 1997): the standard data set ends 1994, but the detector "has been measuring" since 1970, and the paper lists it among "the four operating solar neutrino detectors" | 1994 as the end of the data set, `approximate`, with a note that no source read dates the end of operation | the Wikipedia sentence is not what the paper says; the data set end is the only sourced 1994 |
| NuMI baseline | NuMI beam paper: 734 km | MINOS detector paper: 735.3 km (735.3380 km from the horn) | 735.3 km | the MINOS paper states its reference points; 734 km has none and is not a rounding of 735.3 (the old baseline note said it was, and is corrected) |
| NuMI direction | record: "north-west" | MINOS paper: "approximately NNW"; NuMI paper: "further north" | north-north-west | the only sourced wording |
| ALEPH abstract | research-portal transcription: "this results rules out of the possibility" | printed abstract: "This result rules out the possibility" | the printed abstract | primary source |
| FLWO start | facility note: "founded 1968 ... per public knowledge, not independently sourced" | CfA FLWO page: establishment in 1966 | 1966 | official page; the 10 m telescope's own 1968 operation start is consistent |
| Roque de los Muchachos start | IAC: agreement internationalising the observatory signed 26 May 1979 | IAC: official inauguration 1985 | 1985, `approximate`, with the 1979 agreement in the note | the inauguration is the dated opening event; no source read dates first observation |
| Hanford start | hanford.gov mission page: plutonium production from 1943 | B Reactor page: fuel loaded 13 September 1944 | 1943 | the page's own wording; both quotes are in the interval note |

## Unresolved

* **Homestake end of operation.** Not stated in any source read. The completed interval is a bound (end of the 1970-1994 data set).
* **Homestake, still Wikipedia-only** (`src:homestake-wikipedia` stays cited): experiment `key_specs` target volume (380 m³; Davis says "100,000 gallons (378,000 liters)") and `unique_capabilities`, collaboration `leadership`, detector `specs.target_mass` and the "dry-cleaning fluid" gloss. They were outside the brief.
* **Homestake still warns `experiment-before-facility`** against `facility:surf` (2004). The SURF record's "Homestake gold mine" interval has `start: null` because 1876 is outside the supported 1900-2100 range, so the mine's start cannot be recorded.
* **Eight `experiment-before-facility` warnings remain**, each needing a sourced facility start: CDMS-II (Soudan), HAWC (Sierra Negra), Homestake (SURF), Pierre Auger, RNO-G (Summit Station), SAGE (Baksan), SNO (SNOLAB), Super-Kamiokande (Kamioka).
* **Hanford:** which reactor, its coordinates, the end of the run, the 1953 Physical Review report (not read), a detector record.
* **KIT:** no source read dates the Tritium Laboratory Karlsruhe. **Roque de los Muchachos:** no source read dates the first observation; the 1979 agreement is in a note, not an interval.
* **LEP:** the other four sources of `key_value_text` (L3, DELPHI, OPAL and the portal) are research-portal records of rank 12; the final LEP+SLD value is rank 10.
* **Columbia:** one `facility_id` per institution; Columbia is a whole university, so the link says only that it operates Nevis.

## Candidates considered and excluded

* CERN Document Server for the ALEPH abstract: it answers with a bot-detection challenge, which was not bypassed. ScienceDirect (HTTP 403), the Smithsonian Institution Archives (HTTP 500) and the Nobel Prize biographical page (HTTP 403) were unreachable.
* An alias "Project Poltergeist" for the Hanford experiment: no source read applies the name to it.
* `complementary` or `upgrade_of` for any of the five lineage rows: no quote says so.
* A 1979 `approved` interval for the Roque de los Muchachos Observatory: the agreement is not a project approval.
* Fixing the Homestake Wikipedia-only specs and the other eight facility starts (see Unresolved): outside the brief.
* Any change to `static/atlas/generated`, and any contact with INSPIRE, Neon or Vercel: none made.

## Task 7: feed links, skipped

`docs/atlas-worklog/ACCELERATOR_CHAINS.md` ("For the integrator") lists two links that need records the colliders stream is creating: `{"id": "accelerator:spear"}` and `{"id": "accelerator:pep"}` in `accelerator:slac-linac` `feeds_accelerator_ids` (source `src:slac-grad-handbook`), and `accelerator:petra` feeding `accelerator:hera` (source `src:hera-collider-physics-klein-yoshida-2008`, Table 1). Neither `accelerator:spear`, `accelerator:pep` nor `accelerator:petra` exists on this branch, so nothing was written. Add the links when those records merge.

## Checks

* `python -m hepgraph.atlas.validate`: 0 errors, 1649 warnings, 4 informational. The base (`e9d8f7b`) has 0 errors, 1653 warnings, 4 informational. `experiment-before-facility` fell from 13 to 8; `experiment-without-active-beam` rose from 112 to 113 (the new Hanford experiment, like every reactor experiment with no accelerator).
* `python -m hepgraph.atlas.build --out <scratch>`: succeeds; `static/atlas/generated` was not written or committed. The derived `successor` rows appear on Milagro, HEGRA (twice), Whipple 10 m, AGASA and the Savannah River experiment.
* `python -m pytest -q`: 713 passed, 139 skipped (PostgreSQL-backed tests skip without a throwaway database), with `tests/test_atlas_tours.py::test_route_types_match_state_js` deselected: it fails on `atlas-next` itself (`state.js` route names against `T.ROUTABLE_TYPES`) and is unrelated to this branch.
* Nothing was fetched from inspirehep.net; no Neon, Vercel or deployment command was run.
