# HEP Atlas coverage

Generated 2026-09-18 by `scripts/atlas_coverage_report.py`. Every number here is
computed from `data/atlas/`; none of it is asserted by hand. The atlas does not
claim to contain every experiment in experimental high-energy physics, and the
interface says only "coverage updated" with this date.

## Entities in the atlas

| Type | Count |
| --- | ---: |
| accelerator | 31 |
| beamline | 6 |
| collaboration | 122 |
| detector | 135 |
| document | 70 |
| experiment | 131 |
| facility | 48 |
| geometry | 96 |
| institution | 529 |
| map | 16 |
| person | 12 |
| result | 109 |
| site | 93 |
| source | 1544 |
| topic | 42 |
| membership rows | 659 |

## Coverage by tier

Tier A experiments are flagships researched to full depth (results, technical
documents, key specifications); tiers B–D are researched to the mandatory bar
(identity, status, dated intervals, a located site, topics, summaries, an
official site, at least one authoritative source, a collaboration where one
exists) unless the row says otherwise. "Full" and "partial" are the
researcher's own claim in the registry row; the per-experiment table below
lists what each record still lacks regardless of that claim.

| Tier | Rows | Researched: full | Researched: partial | Not researched |
| --- | ---: | ---: | ---: | ---: |
| A | 23 | 21 | 2 | 0 |
| B | 76 | 11 | 65 | 0 |
| C | 17 | 2 | 15 | 0 |
| D | 15 | 4 | 11 | 0 |

## Independent verification by workstream

A workstream is independently verified when a different agent re-fetched its
cited sources and left a report at `docs/atlas-worklog/VERIFY_<owner>.md`.
Rows without one were verified only by their researcher and the validator.

| Workstream (owner) | Experiments | Independently verified |
| --- | ---: | --- |
| accelerator-neutrino-historical | 4 | yes — VERIFY_accelerator-neutrino-historical.md |
| astro-neutrino | 9 | yes — VERIFY_astro-neutrino.md |
| axions | 7 | yes — VERIFY_axions.md |
| cern-cms | 1 | yes — REVIEW_data_quality_wave1.md |
| cevns | 4 | yes — VERIFY_cevns.md |
| colliders-historical | 6 | yes — VERIFY_colliders-historical.md |
| colliders-lhc | 7 | yes — VERIFY_colliders-lhc.md |
| cosmic-gamma | 8 | yes — VERIFY_cosmic-gamma.md |
| dark-matter | 2 | yes — REVIEW_data_quality_wave1.md |
| dm-cryogenic-low-threshold | 9 | yes — VERIFY_dm-cryogenic-low-threshold.md |
| dm-noble-liquid | 6 | yes — VERIFY_dm-noble-liquid.md |
| dune-atlas-completion | 2 | yes — REVIEW_scientific.md |
| fermilab-neutrino-other | 8 | yes — REVIEW_scientific.md |
| fixed-target | 10 | yes — VERIFY_fixed-target.md |
| flavor | 2 | yes — REVIEW_data_quality_wave1.md |
| heavy-ions | 3 | yes — VERIFY_heavy-ions.md |
| historic-cern | 6 | yes — REVIEW_scientific.md |
| icecube | 4 | yes — REVIEW_data_quality_wave1.md |
| japan-neutrino | 5 | yes — REVIEW_scientific.md |
| muons | 6 | yes — VERIFY_muons.md |
| neutrino-mass-0vbb | 11 | yes — VERIFY_neutrino-mass-0vbb.md |
| reactor-solar-neutrino | 11 | yes — VERIFY_reactor-solar-neutrino.md |

## Coverage by category

Identified means the experiment is in the registry. Researched means a record
exists with sourced content. Gaps are computed per record, not declared.

| Category | Identified | Researched | Fully complete | Missing membership | Missing history | Missing results | Missing documents |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Accelerator neutrinos | 15 | 15 | 1 | 14 | 0 | 2 | 5 |
| Atmospheric neutrinos | 3 | 3 | 0 | 3 | 0 | 2 | 0 |
| Axions and ALPs | 7 | 7 | 0 | 7 | 1 | 7 | 7 |
| Coherent elastic neutrino-nucleus scattering | 4 | 4 | 0 | 4 | 0 | 3 | 3 |
| Colliders | 23 | 23 | 2 | 21 | 0 | 9 | 13 |
| Cosmic rays, gamma rays and astroparticle | 2 | 2 | 0 | 2 | 0 | 2 | 2 |
| Dark matter direct detection | 17 | 17 | 0 | 17 | 1 | 13 | 14 |
| Direct neutrino mass | 2 | 2 | 0 | 2 | 1 | 1 | 2 |
| Fixed target, rare kaons and long-lived particles | 10 | 10 | 0 | 10 | 1 | 9 | 9 |
| Gamma rays | 6 | 6 | 0 | 6 | 2 | 6 | 6 |
| Heavy ions | 3 | 3 | 0 | 3 | 0 | 1 | 3 |
| High-energy and astrophysical neutrinos | 13 | 13 | 0 | 13 | 0 | 10 | 10 |
| Muon precision and rare processes | 6 | 6 | 0 | 6 | 1 | 3 | 3 |
| Neutrinoless double beta decay | 9 | 9 | 0 | 9 | 3 | 9 | 9 |
| Reactor and low-energy neutrinos | 5 | 5 | 0 | 5 | 0 | 0 | 4 |
| Solar and radiochemical neutrinos | 6 | 6 | 0 | 6 | 0 | 2 | 6 |
| **All** | **131** | **131** | **3** | **128** | **10** | **79** | **96** |

## Per-experiment detail


### Accelerator neutrinos

| Experiment | State | Still missing |
| --- | --- | --- |
| DONUT | researched | institution membership, technical documents |
| DUNE | researched | — |
| ICARUS | researched | institution membership |
| K2K | researched | institution membership, technical documents |
| KARMEN | researched | institution membership, major results, technical documents |
| LSND | researched | institution membership, technical documents |
| MINERvA | researched | institution membership |
| MINOS | researched | institution membership |
| MINOS+ | researched | institution membership |
| MicroBooNE | researched | institution membership |
| MiniBooNE | researched | institution membership |
| NOvA | researched | institution membership |
| OPERA | researched | institution membership, technical documents |
| SBND | researched | institution membership, major results |
| T2K | researched | institution membership |

### Atmospheric neutrinos

| Experiment | State | Still missing |
| --- | --- | --- |
| Hyper-Kamiokande | researched | institution membership, major results |
| IceCube Upgrade | researched | institution membership, detector, major results |
| Super-Kamiokande | researched | institution membership |

### Axions and ALPs

| Experiment | State | Still missing |
| --- | --- | --- |
| ABRACADABRA | researched | institution membership, major results, technical documents |
| ADMX | researched | institution membership, major results, technical documents |
| ALPS II | researched | institution membership, major results, technical documents |
| CAST | researched | institution membership, major results, technical documents |
| DMRadio | researched | institution membership, historical intervals, major results, technical documents |
| HAYSTAC | researched | institution membership, major results, technical documents |
| IAXO | researched | institution membership, placeable geography, major results, technical documents |

### Coherent elastic neutrino-nucleus scattering

| Experiment | State | Still missing |
| --- | --- | --- |
| COHERENT | researched | institution membership |
| CONUS / CONUS+ | researched | institution membership, major results, technical documents |
| NUCLEUS | researched | institution membership, major results, technical documents |
| Ricochet | researched | institution membership, major results, technical documents |

### Colliders

| Experiment | State | Still missing |
| --- | --- | --- |
| ALEPH | researched | institution membership, placeable geography |
| ALICE | researched | institution membership |
| ATLAS | researched | — |
| BaBar | researched | institution membership, major results, technical documents |
| Belle | researched | institution membership |
| Belle II | researched | institution membership |
| CDF | researched | institution membership, technical documents |
| CMS | researched | — |
| D0 | researched | institution membership, technical documents |
| DELPHI | researched | institution membership, placeable geography |
| FASER | researched | institution membership, major results, technical documents |
| H1 | researched | institution membership, major results, technical documents |
| L3 | researched | institution membership, placeable geography |
| LHCb | researched | institution membership |
| LHCf | researched | institution membership, major results, technical documents |
| MoEDAL | researched | institution membership, major results, technical documents |
| OPAL | researched | institution membership, placeable geography |
| SLD | researched | institution membership, major results, technical documents |
| SND@LHC | researched | institution membership, major results, technical documents |
| TOTEM | researched | institution membership, major results, technical documents |
| UA1 | researched | institution membership, placeable geography, technical documents |
| UA2 | researched | institution membership, placeable geography, technical documents |
| ZEUS | researched | institution membership, major results, technical documents |

### Cosmic rays, gamma rays and astroparticle

| Experiment | State | Still missing |
| --- | --- | --- |
| Pierre Auger Observatory | researched | institution membership, major results, technical documents |
| Telescope Array | researched | institution membership, major results, technical documents |

### Dark matter direct detection

| Experiment | State | Still missing |
| --- | --- | --- |
| CDMS II | researched | institution membership, major results, technical documents |
| CRESST | researched | institution membership, major results, technical documents |
| DAMIC | researched | institution membership, major results, technical documents |
| DAMIC-M | researched | institution membership, major results, technical documents |
| DEAP-3600 | researched | institution membership, major results, technical documents |
| DarkSide-20k | researched | institution membership, historical intervals, major results, technical documents |
| DarkSide-50 | researched | institution membership, major results, technical documents |
| EDELWEISS | researched | institution membership, major results, technical documents |
| LUX (Large Underground Xenon) | researched | collaboration, detector |
| LZ (LUX-ZEPLIN) | researched | institution membership |
| NEWS-G | researched | institution membership, major results, technical documents |
| PandaX-4T | researched | institution membership, major results, technical documents |
| SENSEI | researched | institution membership, major results, technical documents |
| SuperCDMS | researched | institution membership, major results, technical documents |
| SuperCDMS Soudan | researched | institution membership, major results, technical documents |
| XENON1T | researched | institution membership, technical documents |
| XENONnT | researched | institution membership |

### Direct neutrino mass

| Experiment | State | Still missing |
| --- | --- | --- |
| KATRIN | researched | institution membership, historical intervals, technical documents |
| Project 8 | researched | institution membership, major results, technical documents |

### Fixed target, rare kaons and long-lived particles

| Experiment | State | Still missing |
| --- | --- | --- |
| DarkQuest | researched | collaboration, historical intervals, detector, major results, technical documents |
| E949 | researched | institution membership, major results, technical documents |
| KOTO | researched | institution membership, major results, technical documents |
| KTeV | researched | institution membership, major results, technical documents |
| MATHUSLA | researched | institution membership, detector, major results, technical documents |
| NA48 | researched | institution membership, major results, technical documents |
| NA62 | researched | institution membership |
| NA64 | researched | institution membership, major results, technical documents |
| SHiP | researched | institution membership, major results, technical documents |
| SeaQuest | researched | institution membership, major results, technical documents |

### Gamma rays

| Experiment | State | Still missing |
| --- | --- | --- |
| CTAO | researched | institution membership, historical intervals, major results, technical documents |
| H.E.S.S. | researched | institution membership, major results, technical documents |
| HAWC | researched | institution membership, major results, technical documents |
| LHAASO | researched | institution membership, historical intervals, major results, technical documents |
| MAGIC | researched | institution membership, major results, technical documents |
| VERITAS | researched | institution membership, major results, technical documents |

### Heavy ions

| Experiment | State | Still missing |
| --- | --- | --- |
| PHENIX | researched | institution membership, technical documents |
| STAR | researched | institution membership, technical documents |
| sPHENIX | researched | institution membership, major results, technical documents |

### High-energy and astrophysical neutrinos

| Experiment | State | Still missing |
| --- | --- | --- |
| AMANDA | researched | collaboration, detector, major results, technical documents |
| ANITA | researched | institution membership, major results, technical documents |
| ANTARES | researched | institution membership, major results, technical documents |
| ARA | researched | institution membership, major results, technical documents |
| ARIANNA | researched | institution membership, major results, technical documents |
| Baikal-GVD | researched | institution membership, major results, technical documents |
| GRAND | researched | institution membership, major results, technical documents |
| IceCube | researched | institution membership |
| IceCube-Gen2 | researched | institution membership, detector, major results |
| KM3NeT | researched | institution membership |
| Kamiokande | researched | collaboration, detector, technical documents |
| P-ONE | researched | institution membership, major results, technical documents |
| RNO-G | researched | institution membership, major results, technical documents |

### Muon precision and rare processes

| Experiment | State | Still missing |
| --- | --- | --- |
| COMET | researched | institution membership, historical intervals, major results |
| MEG | researched | institution membership, technical documents |
| MEG II | researched | institution membership, technical documents |
| Mu2e | researched | institution membership, major results |
| Mu3e | researched | institution membership, major results, technical documents |
| Muon g-2 | researched | institution membership |

### Neutrinoless double beta decay

| Experiment | State | Still missing |
| --- | --- | --- |
| CUORE | researched | institution membership, major results, technical documents |
| CUPID | researched | institution membership, historical intervals, major results, technical documents |
| EXO-200 | researched | institution membership, major results, technical documents |
| GERDA | researched | institution membership, major results, technical documents |
| KamLAND-Zen | researched | institution membership, historical intervals, detector, major results, technical documents |
| LEGEND | researched | institution membership, major results, technical documents |
| Majorana Demonstrator | researched | institution membership, major results, technical documents |
| NEXT | researched | institution membership, major results, technical documents |
| nEXO | researched | institution membership, historical intervals, major results, technical documents |

### Reactor and low-energy neutrinos

| Experiment | State | Still missing |
| --- | --- | --- |
| Daya Bay | researched | institution membership, technical documents |
| Double Chooz | researched | institution membership, technical documents |
| JUNO | researched | institution membership |
| KamLAND | researched | institution membership, technical documents |
| RENO | researched | institution membership, technical documents |

### Solar and radiochemical neutrinos

| Experiment | State | Still missing |
| --- | --- | --- |
| Borexino | researched | institution membership, technical documents |
| GALLEX/GNO | researched | institution membership, major results, technical documents |
| Homestake | researched | institution membership, technical documents |
| SAGE | researched | institution membership, technical documents |
| SNO | researched | institution membership, technical documents |
| SNO+ | researched | institution membership, major results, technical documents |

## Local map geometry

To-scale campus maps (ontology A25). A feature is `surveyed` when the laboratory
published its coordinates, `georeferenced` when a third party traced it from
imagery or an official plan, `derived` when it was computed from sourced numbers,
and `inferred_direction` when it is a neutrino direction rather than a structure.
Checks are independent official figures the validator re-measures on every run.

| Map | Facility | Features | Surveyed | Georeferenced | Derived | Inferred direction | Unlocated | Checks passed | Checks failed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Amundsen-Scott South Pole Station — IceCube and ARA | Amundsen-Scott South Pole Station | 1 | 0 | 1 | 0 | 0 | 8 | 0 | 0 |
| Baikal-GVD — southern Lake Baikal site | Baikal Deep Underwater Neutrino Telescope | 2 | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| CERN — Meyrin, Prévessin and the LHC ring | CERN | 21 | 1 | 17 | 2 | 1 | 7 | 5 | 0 |
| China Jinping Underground Laboratory (CJPL) | China Jinping Underground Laboratory | 3 | 0 | 1 | 2 | 0 | 0 | 1 | 0 |
| DESY — Hamburg-Bahrenfeld campus and the HERA ring | Deutsches Elektronen-Synchrotron | 4 | 0 | 4 | 0 | 0 | 1 | 1 | 0 |
| Fermilab — Batavia, Illinois | Fermi National Accelerator Laboratory | 22 | 0 | 12 | 8 | 2 | 19 | 9 | 0 |
| J-PARC — Tokai accelerator complex | J-PARC (Japan Proton Accelerator Research Complex) | 9 | 0 | 8 | 0 | 1 | 0 | 4 | 0 |
| Kamioka Observatory — Mozumi and Tochibora mines | Kamioka Observatory (ICRR, University of Tokyo) | 4 | 1 | 0 | 2 | 1 | 0 | 3 | 0 |
| KEK — Tsukuba campus | KEK (High Energy Accelerator Research Organization) | 11 | 0 | 10 | 0 | 1 | 1 | 2 | 0 |
| KM3NeT/ARCA — Capo Passero deep-sea site | KM3NeT | 2 | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| KM3NeT/ORCA — Toulon deep-sea site | KM3NeT | 2 | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| PSI — Villigen and Wurenlingen campus | Paul Scherrer Institute | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 0 |
| SNOLAB — Vale Creighton Mine, Sudbury, Ontario | SNOLAB | 3 | 0 | 2 | 1 | 0 | 0 | 1 | 0 |
| Soudan Underground Laboratory, Soudan, Minnesota | Soudan Underground Laboratory | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| SURF — Sanford Underground Research Facility, Lead, South Dakota | Sanford Underground Research Facility | 6 | 1 | 5 | 0 | 0 | 1 | 0 | 0 |
| WIPP — Waste Isolation Pilot Plant, Carlsbad, New Mexico | Waste Isolation Pilot Plant | 3 | 0 | 3 | 0 | 0 | 0 | 0 | 0 |

### Facilities without a local map (33)

Named rather than counted, so the gap cannot be read as coverage:

Argonne National Laboratory, Baksan Neutrino Observatory, Boulby Underground Laboratory, Brokdorf Nuclear Power Plant, Brookhaven National Laboratory, CTAO-South (Paranal), Center for Experimental Nuclear Physics and Astrophysics (CENPA), Chooz Reactor Neutrino Site, Daya Bay Reactor Neutrino Laboratory, Fred Lawrence Whipple Observatory, H.E.S.S. site, Khomas Highland, ISIS Neutron and Muon Source, Institut Laue-Langevin, Jiangmen Underground Neutrino Observatory, Karlsruhe Institute of Technology, Campus North, LHAASO (Daocheng), Laboratoire Souterrain de Modane, Laboratori Nazionali del Gran Sasso, Laboratorio Subterraneo de Canfranc, Leibstadt Nuclear Power Plant, Los Alamos National Laboratory, Massachusetts Institute of Technology, McMurdo Long Duration Balloon Facility, Oak Ridge National Laboratory, Pierre Auger Observatory, Roque de los Muchachos Observatory, SLAC National Accelerator Laboratory, Sierra Negra (HAWC site), Summit Station, Greenland, Telescope Array (Utah), Thomas Jefferson National Accelerator Facility, Yale Wright Laboratory, Yonggwang (Hanbit) Reactor Neutrino Site.


## What is deliberately out of scope

See `docs/HEP_ATLAS_RESEARCH_METHOD.md` for the scope boundary and the
reasons behind each inclusion and exclusion.

