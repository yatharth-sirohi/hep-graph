# icecube — research log

Agent: `icecube` (IceCube programme lead). Verified 2026-09-16. Branch `hep-atlas-globe`.

## Scope

Amundsen-Scott South Pole Station and the IceCube array site; the AMANDA →
IceCube → IceCube Upgrade → IceCube-Gen2 lineage; the IceCube, DeepCore and
IceTop detectors; the IceCube Collaboration; eight major results; five technical
documents; the coverage registry row set for this programme.

No child agents were spawned (the task explicitly forbade it), so every value
below was fetched and read by this agent.

## Entities written

Facilities
- `facility:amundsen-scott-south-pole-station`

Sites
- `site:south-pole-icecube`

Experiments
- `experiment:amanda`
- `experiment:icecube`
- `experiment:icecube-upgrade`
- `experiment:icecube-gen2`

Detectors
- `detector:icecube` (main)
- `detector:icecube-deepcore` (`parent_detector_id: detector:icecube`)
- `detector:icetop` (`parent_detector_id: detector:icecube`)

Collaborations
- `collaboration:icecube`

Results
- `result:icecube-evidence-extraterrestrial-neutrinos-2013` (evidence, 4σ)
- `result:icecube-txs-0506-056-multimessenger-2018` (observation)
- `result:icecube-txs-0506-056-prior-neutrino-flare-2018` (evidence, 3.5σ)
- `result:icecube-ngc-1068-evidence-2022` (evidence, 4.2σ)
- `result:icecube-galactic-plane-neutrinos-2023` (observation, 4.5σ)
- `result:icecube-glashow-resonance-candidate-2021` (first_detection, 6.05 ± 0.72 PeV)
- `result:icecube-deepcore-atmospheric-oscillations-2023` (precision_measurement)
- `result:icecube-sterile-neutrino-search-2020` (limit)

Documents
- `document:icecube-detector-paper-jinst-2017`
- `document:icecube-preliminary-design-document`
- `document:icecube-upgrade-design-and-science-goals-2019`
- `document:icecube-gen2-technical-design-report`
- `document:icecube-gen2-white-paper-2021`

Coverage
- `data/atlas/coverage/icecube.json` (4 rows)

## Sources added (26, all `src:icecube-*`)

Official IceCube pages (rank 1, `full_text`): `-official-detector-page`,
`-official-overview`, `-official-quick-facts`, `-official-collaboration-page`,
`-official-timeline`, `-official-beyond-icecube`,
`-official-amanda-data-release`, `-upgrade-update-15-2026`, `-gen2-tdr-page`.

Official facility (rank 2): `-nsf-south-pole-station`.

INSPIRE experiment records (rank 3, `partial`): `-inspire-experiment-record`
(1108514), `-gen2-inspire-experiment-record` (1811535),
`-amanda-inspire-experiment-record` (1110448).

Design / detector papers: `-preliminary-design-document-2001` (rank 4,
`partial`), `-detector-paper-jinst-2017` (rank 5, `partial`).

Press release (rank 9): `-upgrade-press-release-2026`.

arXiv / journal (rank 10, `full_text` abstracts): `-upgrade-design-icrc-2019`,
`-gen2-white-paper-2021`, `-result-astrophysical-neutrinos-science-2013`,
`-result-txs-multimessenger-science-2018`, `-result-txs-prior-science-2018`,
`-result-ngc1068-science-2022`, `-result-galactic-plane-science-2023`,
`-result-glashow-nature-2021`, `-result-deepcore-oscillations-prd-2023`,
`-result-sterile-neutrino-prl-2020`.

`data/atlas/sources/` was searched for these URLs before creating the records;
none of them was already present.

## Conflicts

| claim | source A | source B | chosen | why |
| --- | --- | --- | --- | --- |
| IceCube Upgrade string count | ICRC 2019 design paper (arXiv:1908.09441): "seven new columns of photosensors" | NSF/IceCube press release 12 Feb 2026 and the official *Beyond IceCube* page: "five more closely spaced … strings" / "deployed five new strings" | **five (as built)** | Two independent, later, official statements describe the built detector; the seven-string figure is the 2019 design and is kept in the notes of `experiment:icecube-upgrade` and `document:icecube-upgrade-design-and-science-goals-2019`. |
| Upgrade construction season | ICRC 2019: "will be constructed in the 2022/23 Antarctic Summer season" | Press release 2026: three field seasons 2023–2026, drilling and installation in the last one | **2023–2026** | A schedule from 2019 versus a report of what happened. |
| Upgrade module count | Feb 2025 field-season report on icecube.wisc.edu: "700 high-performance instruments" | Feb 2026 press release: "more than 600 new and enhanced light sensors and calibration instruments" | **>600** | Final, post-deployment figure; the 2025 page was read only as a WebFetch summary and is therefore not cited anywhere. |
| AMANDA-II operating span | AMANDA 7-year data-release page (2008): "AMANDA-II has operated from 2000 — 2006" | IceCube timeline: "AMANDA-II operated through 2009" | **1996–2009** for the AMANDA operating interval | The 2008 figure is the span of that particular dataset, not the detector lifetime; the timeline speaks about the detector. The 1996 start is corroborated by INSPIRE (`date_started` 1996-01-01) and by "after nine years of operation" as of 20 March 2005. |
| IceCube-Gen2 TDR identifier | Task brief: "TDR arXiv 2308.04141" | arXiv:2308.04141 is *Intermediate Charge-Breaking Phases and Symmetry Non-Restoration in the 2-Higgs-Doublet Model* (unrelated theory paper); the TDR is published at icecube-gen2.wisc.edu, Parts I–II July 2023 and Part III June 2024 | **collaboration-hosted TDR** | The brief's arXiv id is wrong; it is used nowhere in this partition. |
| Collaboration counts as-of date | Quick Facts: "About 450 scientists at 58 institutions in 14 countries conduct IceCube science (as of January 2025)" | Collaboration page: map "as of April 2025", "more than 450 people from 58 institutions in 14 countries" | **as_of 2025-01** with both sources | The Quick Facts page attaches an explicit as-of date to the counts themselves; the numbers agree. Both snapshots are recorded in `roster_snapshots`. |

## Unresolved fields

- **Array coordinates.** No official IceCube or NSF page publishes the array's
  latitude/longitude, and the JINST detector paper gives only "IceCube is
  located at Amundsen-Scott South Pole Station". The IceCube internal
  coordinate system is a local eastings/northings grid; `docs.icecube.aq`,
  which documents it, returned HTTP 401. `site:south-pole-icecube` therefore
  records the geographic South Pole (−90.0, 0.0) with `precision_m: 2000`,
  `confidence: approximate` and a note saying it is not a surveyed position.
  Widely circulated values such as 89.99°S / 63.45°W come from Wikipedia only
  and are inadmissible for detector coordinates under A17.
- **Per-season string deployment** (IC1/IC9/IC22/IC40/IC59/IC79/IC86). Not
  published on the official pages and not found in the fetched detector paper.
  Only the 2004 first string (#21), the 18 December 2010 last string and the
  seven-season span are recorded.
- **AMANDA** month-precision start/end and any decommissioning date; no
  AMANDA collaboration record (it merged into the IceCube Collaboration on
  20 March 2005, and `collaboration:amanda` is not an id this workstream owns);
  no AMANDA detector record.
- **DeepCore** depth range and sensor count: no DeepCore-specific numbers on
  the official pages; the parent array depth range is recorded with
  `confidence: uncertain` and a note.
- **IceTop** deployment dates and instrumented area: not published separately;
  the operating interval start is derived from the start of full 86-string
  operation and marked `derived`.
- **IceCube Upgrade**: exact module count, INSPIRE experiment record (none
  found — INSPIRE 1281974 is PINGU, a different concept), start of physics
  operation.
- **IceCube-Gen2**: no approval, funding or construction dates; the surface
  array is not modelled; the TDR PDFs (75 MB and 28 MB) were not parsed.
- **IceCube Preliminary Design Document**: the PDF at
  `icecube.wisc.edu/icecube/static/reports/IceCubeDesignDoc.pdf` was retrieved
  but its text layer could not be parsed, so the source is `retrieval: partial`,
  nothing quotes it, and its date is recorded at year precision (2001). The
  DocuShare copy (Document-6644) now requires authentication.
- **Collaboration leadership**: left empty because person records belong to the
  membership-lead workstream. The February 2026 press release names
  "Erin O'Sullivan, IceCube Spokesperson and a professor of physics at Uppsala
  University"; the timeline records Christian Spiering taking over as
  spokesperson at the 2005 AMANDA/IceCube merger.
- **Institution memberships** for `collaboration:icecube` are not written here
  (owned by membership-lead); only the published aggregate counts are recorded.

## Children spawned and what I re-checked

None — child agents were forbidden by the task. Every critical value was read
by this agent directly: all quotes attached to coordinates, key specs,
intervals and result date/significance/type were taken verbatim from the
fetched page or arXiv abstract text (official IceCube pages and NSF were
re-read as raw text to guarantee the quotes are exact).

## Confidence summary

- `verified`: IceCube geometry (5,160 DOMs, 86 strings, 1,450–2,450 m, 1 km³,
  DeepCore 8 strings / ~10 GeV / 70 m / 7 m, IceTop 81 stations / 324 DOMs /
  300 TeV–1 EeV), the construction and operation intervals (1999-11 proposal,
  2002-03 NSB award, 2004 → 2010-12-18 construction, 2011-05-13 full
  operation), collaboration formation (1999) and counts, all eight result
  claims, significances and dates, Upgrade approval (2019), seasons
  (2023–2026), five strings.
- `approximate`: station/site altitude (~2,835 m), member count (~450),
  Upgrade module count (>600), Gen2 volume (~8 km³), AMANDA depth range.
- `derived`: AMANDA 1996–2009 operating interval, IceTop operating start,
  Upgrade commissioning start, Gen2 "proposed" interval start, Gen2
  `same_program` lineage row.
- `uncertain`: AMANDA terminal (completed) event at year precision; DeepCore
  depth range inherited from the parent array; result significances recorded as
  `null` where the abstract gives none (TXS multimessenger, Glashow, DeepCore
  oscillations, sterile search).

## For the orchestrator

`data/atlas/coverage/backlog.json` still carries a stub row for
`experiment:icecube-gen2` (`researched: "none"`, `owner: null`). That entity is
now owned and researched in `data/atlas/coverage/icecube.json`; the backlog stub
should be dropped to avoid a duplicate registry row. I did not edit
`backlog.json` because it belongs to another workstream.
