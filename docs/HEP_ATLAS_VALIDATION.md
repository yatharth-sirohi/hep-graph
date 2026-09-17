# HEP Atlas validation

What was checked, by whom, and what it found. Counts here are computed from the
repository, not asserted. Where something was not checked, this document says
so; "extensively tested" is not a finding.

## 1. How the work was organised

The project was executed as parallel workstreams with independent review, on
the principle that the agent that researches a record never certifies it.

| Role | Count | What they produced |
| --- | ---: | --- |
| Ontology reviewers | 3 | Entity-schema, temporal-model and provenance reviews of the draft contract, before any data existed |
| Research workstreams | 10 | Fermilab and DUNE; the other Fermilab neutrino experiments; CERN and ATLAS; CMS; Japan; IceCube; dark matter; flavour; historic CERN; research topics |
| Data and platform | 2 | The schema, loader, validator, builder, scaffold and link checker; the globe application |
| Membership | 1 | Institution rosters, institution records and people |
| Independent reviewers | 4 | Data quality (wave 1), scientific and historical, user experience, performance and adversarial |
| Cleanup and integration | 2 | Source-backed defect closure; orchestrator integration |

Nested delegation was used where it helped and abandoned when it did not: the
first wave of research leads spawned children, but rate limits made deep trees
unreliable, so later waves were single-agent workstreams with separate
verification. Every workstream left a log under `docs/atlas-worklog/`.

## 2. What the atlas contains

| Entity | Count |
| --- | ---: |
| Experiments | 30 |
| Collaborations | 25 |
| Detectors | 32 |
| Accelerators | 21 |
| Sites | 22 |
| Facilities | 9 |
| Beamlines | 5 |
| Institutions | 529 |
| People | 12 (all resolved to INSPIRE author records) |
| Major results | 62 |
| Technical documents | 55 |
| Research topics | 42 |
| Sources | 956, of which 952 are cited by at least one record |
| Membership rosters | 3 collaborations, 659 institution rows |
| Coverage registry rows | 128 |
| Canonical data files | 1,770 |

Results carry the type their publication used: 19 observations, 11 limits, 10
precision measurements, 8 evidence, 8 measurements, 2 first detections, 3
technology milestones and 1 anomaly. No result is recorded as a discovery,
because none of the cited publications uses that word of itself.

## 3. Automated checks

`python -m hepgraph.atlas.validate` enforces the contract in
`docs/HEP_ATLAS_ONTOLOGY.md`: structure and required fields, referential
integrity, id and alias collisions, date validity and interval ordering,
terminal-status semantics, derived-state agreement, unit and dimension
correctness with per-key plausibility ranges, display-versus-value magnitude,
coordinate kind and source quality, great-circle agreement between a recorded
baseline and its two sites, evidence-class consistency with source type,
claim-level quotes where the contract requires them, and duplicate sources by
normalised URL or DOI.

Errors fell from **368** at the first run against real data to **16** at the
time of writing, and the pilot gate stayed green through every change.

The test suite runs 730 tests. The pre-existing HEP Graph suite is unchanged at
527 passed with one known expected failure, verified in isolation; the
remainder are new atlas tests covering the schema and temporal semantics, the
validator (one deliberately mutated fixture per rule), the build and its
determinism, the server routes including path traversal, the historical state
assertions, and the pilot acceptance gate.

## 4. The pilot acceptance gate

The specification fixes a gate before the atlas may be expanded: DUNE, ATLAS
and T2K must each answer a fixed list of questions from the data alone.
`tests/test_atlas_pilot_acceptance.py` encodes it and passes 17 of 17.

It asserts, from the canonical records rather than the built bundles, that DUNE
has near and far detectors at distinct located sites with the far site
underground, that a beamline connects them with a sourced baseline, that the
far detector's technology and mass are recorded, that the collaboration has
member institutions that can be placed on a globe; that ATLAS is at CERN and
linked to the LHC, that its detector is placed and specified, that its timeline
spans construction to running, that it is not shown operating in 1990, that its
results are curated with sources and openable references, and that its
collaboration spans at least ten countries; that T2K runs from J-PARC to
Kamioka with a sourced baseline, timeline, results and documents; and that
every resolved person carries a verified INSPIRE identifier.

## 5. Independent review findings

### Data quality, wave one (IceCube, LZ and LUX, Belle and Belle II, CMS)

Zero P0 findings. Every one of 36 independently re-fetched quotes matched its
source verbatim: no fabricated citation, no misattributed quote, no unit error,
no inflated result wording. Three P1 findings: a systemic result-dating defect
in the CMS results, where the contract requires an announcement date to win
over a later preprint; a detector-kind coordinate resting on a Wikipedia
infobox; and duplicate source records shared with other workstreams.

### Scientific and historical review, and user-experience review

In progress at the time of writing; their reports are
`docs/atlas-worklog/REVIEW_scientific.md` and `REVIEW_ux.md`.

### Integration defects found by the orchestrator

Four bugs were invisible to both test suites because the browser tests loaded
the fixture tree and the Python tests built the fixture dataset. Against the
real data the globe drew **no markers at all**, collaboration mode showed no
institutions, results mode and the document library were **empty**, and every
shared deep link opened an empty globe. All four are fixed; the release gate
should run the browser suite against both trees, and the fixture generator
should be regenerated from the canonical shape so the two stop drifting.

A fifth was a product bug rather than a test gap: HEP Graph's per-address rate
limiter counted the atlas's static bundles, so browsing returned 429s and a
heavy atlas session would have locked the user out of the search API. Assets
now have their own budget and no longer occupy a query worker.

One near-miss is worth recording. The validator's duplicate-source rule
normalised URLs by stripping their query strings, so it proposed merging eleven
distinct INSPIRE searches into one record and the geocoder lookups for
Fermilab, CERN, J-PARC and Sanford Lab into a single source. Applying it would
have made one facility's coordinates appear to be sourced from a lookup for
somewhere else. The rule was wrong, not the data; the genuine duplicate count
was nine.

## 6. Known limitations

- **Coverage is partial and says so.** 128 experiments are identified, 29 are
  researched, 2 are complete on every axis. `docs/HEP_ATLAS_COVERAGE.md` is
  generated from the data and lists what each researched record still lacks.
- **Membership is three collaborations deep.** DUNE's roster is effectively
  complete from the collaboration's own page; ATLAS captured 198 rows; CMS
  rests on a recent paper's author affiliations because the collaboration's
  roster requires a login, and is labelled as publication affiliation rather
  than an official list.
- **People are a deliberate sample.** Twelve, each resolved to an INSPIRE
  author record and attached only on its own evidence. No person is attached to
  a collaboration because their institution belongs to it.
- **Some geography is at campus precision.** Where no authoritative source
  gives a hall position, the record says so rather than inventing one; the
  interaction points of two LEP experiments are inferred and OPAL's is absent,
  because no fetched source states it.
- **Link checking is manual.** `python -m hepgraph.atlas.linkcheck` records
  status back into source records; it is not run in the build and a dead link
  never fails it.

## 7. Reproducing this

```sh
python -m hepgraph.atlas.validate     # contract enforcement, non-zero on errors
python -m hepgraph.atlas.build        # regenerate static/atlas/generated/
python -m pytest -q                   # 730 tests
python scripts/atlas_coverage_report.py --check   # coverage doc matches the data
node tests/browser_atlas.cjs          # globe, panels, timeline, mobile, fallback
```
