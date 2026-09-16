# HEP Atlas ontology and data contract (v0.1, 2026-09-16)

This document is the interface contract between every HEP Atlas workstream:
research agents produce records in this shape, the validator enforces it, the
build step generates the browser bundles from it, and the globe renders those
bundles. Nothing in `hepgraph/` outside `hepgraph/atlas/` depends on it, and
HEP Graph (the people network) is unchanged by it.

Status of this document: **draft under review**. Reviewers challenge it; the
orchestrator resolves conflicts; the version number changes when a field's
meaning changes.

## 0. Ground rules

1. **Canonical data is JSON under `data/atlas/`**, one file per entity, human
   reviewed, diffable. HEP Graph is stdlib-only Python; JSON keeps that true
   (no YAML dependency). Generated bundles live under `static/atlas/generated/`
   and are never hand-edited.
2. **Provenance is data.** Every entity carries record-level `sources`. Every
   *critical* fact (coordinates, intervals, memberships, technical numbers,
   result claims, status) is a *sourced value* (§2.1), never a bare scalar.
3. **Unknown is a value.** `null` plus a `note` is correct when a source does
   not say. Fabricating a start date to make a card look complete is a P0
   defect.
4. **One canonical entity per real thing.** Aliases are lists on the entity.
   Super-K, Super-Kamiokande and SuperK are one experiment.
5. **Facility ≠ institution ≠ collaboration.** CERN exists three times with
   three ids and three roles (`facility:cern`, `institution:cern`,
   membership rows for `institution:cern` in collaborations). Fermilab the
   laboratory is `facility:fermilab`; Fermilab the collaboration member is
   `institution:fermilab`.
6. **Dates carry precision.** `"2008"` is a year, `"2008-09"` a month,
   `"2008-09-10"` a day; `approx: true` marks "~2030" and `planned: true`
   marks a date that has not happened.
7. **Evidence classes are displayed, not hidden.** A person drawn from a
   collaboration author list is labelled as such in the UI.

## 1. Identifiers

Ids are lower-case ASCII slugs with a typed prefix: `<type>:<slug>`.

| Prefix | Example | Notes |
| --- | --- | --- |
| `facility:` | `facility:fermilab`, `facility:lngs` | laboratory / observatory / site operator |
| `site:` | `site:surf-4850-level`, `site:fermilab-main-campus`, `site:south-pole-icecube` | one geographic point where a detector or machine physically is |
| `accelerator:` | `accelerator:lhc`, `accelerator:fermilab-main-injector` | |
| `beamline:` | `beamline:lbnf`, `beamline:numi`, `beamline:bnb`, `beamline:jparc-neutrino` | |
| `experiment:` | `experiment:dune`, `experiment:atlas`, `experiment:t2k` | |
| `detector:` | `detector:dune-fd1-hd`, `detector:super-kamiokande`, `detector:atlas` | |
| `collaboration:` | `collaboration:dune`, `collaboration:atlas` | |
| `institution:` | `institution:university-of-iowa`, `institution:cern` | |
| `person:` | `person:inspire:1019647` | INSPIRE author recid when resolved; `person:unresolved:<slug>` otherwise |
| `result:` | `result:atlas-higgs-observation-2012` | |
| `document:` | `document:dune-fd-tdr-vol-1` | |
| `topic:` | `topic:neutrino-oscillations` | |
| `src:` | `src:dune-collaboration-site`, `src:atlas-detector-jinst-2008` | |

Rules: ids never change once published; renaming means adding an alias and
keeping the id. Slugs use `-` only. A slug should be recognisable by a
physicist without a lookup.

## 2. Shared value types

### 2.1 Sourced value

```json
{
  "value": <any JSON>,
  "sources": ["src:..."],
  "verified_at": "2026-09-16",
  "confidence": "verified" | "derived" | "approximate" | "uncertain",
  "note": "optional free text; REQUIRED when confidence != verified"
}
```

`sources` must be non-empty and every id must exist in `data/atlas/sources/`.
`verified_at` is the date an agent actually read the source. The validator
rejects a sourced value whose `sources` is empty.

### 2.2 Date

A string: `"YYYY"`, `"YYYY-MM"` or `"YYYY-MM-DD"`. Precision is the string
length. Or an object when qualifiers are needed:

```json
{ "date": "2030", "approx": true, "planned": true, "note": "DUNE FD1 physics start per 2024 project schedule" }
```

Only `date` is required inside the object. `approx` means the source gave an
approximate date; `planned` means the date is in the future relative to
`verified_at` of the enclosing sourced value. Seasons ("Spring 2008") are
stored as the month range's first month with `approx: true` and the season in
`note`.

### 2.3 Interval

```json
{
  "label": "Run 2",
  "status": "active",
  "start": <Date|null>,
  "end": <Date|null>,
  "sources": ["src:..."],
  "verified_at": "2026-09-16",
  "confidence": "verified",
  "note": ""
}
```

`status` is one of the experiment status enum (§4). `start: null` means "start
unknown", **not** "since forever"; the validator warns and the UI says
"start unknown". `end: null` with a non-terminal status means "ongoing at
`verified_at`". Intervals on one entity may not overlap unless they carry
different `label`s (e.g. `construction` and `commissioning` may overlap).

### 2.4 Quantity

```json
{
  "value": 1285,
  "unit": "km",
  "dimension": "length",
  "approx": true,
  "display": "~1300 km",
  "sources": ["src:dune-fd-tdr-vol-1"],
  "verified_at": "2026-09-16",
  "confidence": "verified",
  "note": "1284.9 km beam baseline, TDR Vol. I §1"
}
```

Recognised dimensions and units (the validator rejects mismatches):

| dimension | units |
| --- | --- |
| `length` | m, km, cm, mm |
| `mass` | kg, t, kt (1 kt = 1000 t) |
| `energy` | eV, keV, MeV, GeV, TeV |
| `power` | W, kW, MW |
| `luminosity` | cm^-2 s^-1 |
| `integrated_luminosity` | pb^-1, fb^-1, ab^-1 |
| `magnetic_field` | T |
| `depth_mwe` | m.w.e. |
| `volume` | m^3, km^3 |
| `count` | (unit `""`) |
| `time` | s, ms, ns, d, yr |
| `angle` | deg, mrad |
| `temperature` | K, mK |
| `pressure` | bar, Pa |
| `frequency` | Hz, kHz, MHz, GHz |

`display` is the source-conventional string shown in the UI; `value`/`unit`
are for comparison and validation. A range is `{"min": 0.6, "max": 10, "unit": "GeV", ...}`
in place of `value`.

### 2.5 Coordinates

```json
{
  "lat": 44.3520, "lon": -103.7510,
  "precision_m": 200,
  "kind": "detector" | "campus" | "underground_lab" | "headquarters" | "approximate_region",
  "sources": ["src:..."], "verified_at": "...", "confidence": "verified", "note": ""
}
```

`kind` tells the geographic reviewer what the point represents. A globe marker
for a detector must have `kind: detector` or `underground_lab`; a
`headquarters` point may only be used for institutions.

### 2.6 External reference

```json
{ "doi": "10.1016/j.physletb.2012.08.020", "arxiv": "1207.7214", "inspire": 1124337,
  "url": "https://...", "report_number": "CERN-PH-EP-2012-218", "hepdata": "https://www.hepdata.net/record/ins1124337" }
```

All fields optional; at least one must be present where a reference is required.

## 3. Entities

Every entity has: `id`, `type` (the id prefix), `name`, `aliases: []`,
`summary: {"plain": "...", "technical": "..."}` (plain ≤ 60 words, written for
a newcomer; technical for a graduate student), `sources: []` (record-level),
`links: {"website": Sourced(url)|null, ...}`, `notes: []` (free text for
reviewers), `coverage: {"tier": "A"|"B"|"C"|"D"|"E", "researched": "none"|"partial"|"full", "validated": bool}`.
Fields marked **S** are sourced values (§2.1); **Q** are quantities; **I**
are interval lists; **C** are coordinates.

### 3.1 Facility (`data/atlas/facilities/<slug>.json`)

| field | type |
| --- | --- |
| `kind` | `accelerator_laboratory` \| `underground_laboratory` \| `neutrino_observatory` \| `astroparticle_observatory` \| `reactor_site` \| `spallation_source` \| `research_laboratory` \| `polar_station` \| `deep_sea_site` |
| `operator` | **S** string (e.g. "Fermi Research Alliance for the U.S. DOE") |
| `country` | ISO 3166-1 alpha-2 list (CERN: `["CH","FR"]`) |
| `primary_site_id` | `site:` id for the main marker |
| `site_ids` | all `site:` ids belonging to this facility |
| `accelerator_ids`, `beamline_ids` | |
| `intervals` | **I** (founded, operating, closed) |
| `status` | current status from §4 |
| `specs` | map of **Q** (e.g. `depth`, `overburden`, `beam_power`) |
| `topic_ids` | research areas |
| `related_facility_ids` | |
| `institution_id` | the `institution:` id that plays this lab's member role, or null |

### 3.2 Site (`data/atlas/sites/<slug>.json`)

| field | type |
| --- | --- |
| `facility_id` | owning facility or null (e.g. a reactor complex) |
| `coordinates` | **C** (required) |
| `setting` | `surface` \| `underground` \| `ice` \| `sea` \| `lake` \| `balloon` \| `mountain` |
| `depth` | **Q** `length` (rock overburden) and/or `depth_mwe` |
| `altitude` | **Q** `length` |
| `country` | ISO code |
| `place` | `{"city": "Lead", "region": "South Dakota", "country": "US"}` |

### 3.3 Accelerator

`kind` (`synchrotron`, `linac`, `storage_ring`, `collider`, `cyclotron`,
`booster`), `facility_id`, `site_id`, `particles: []`, `specs` (**Q**:
`beam_energy`, `cms_energy`, `circumference`, `length`, `peak_luminosity`,
`beam_power`, `protons_per_year`), `intervals` (**I**), `status`,
`feeds_accelerator_ids`, `serves_experiment_ids`, `beamline_ids`,
`document_ids`.

### 3.4 Beamline

`facility_id`, `accelerator_id` (parent), `primary_beam` (**S**: particle +
energy **Q**), `target` (**S** string), `secondary_beam` (**S**: e.g.
"muon neutrinos / antineutrinos, off-axis"), `specs` (**Q**: `beam_power`,
`proton_energy`, `peak_neutrino_energy`, `off_axis_angle`), `direction`
(**S** text), `near_detector_site_ids`, `far_detector_site_ids`,
`baselines: [{"from_site_id", "to_site_id", "distance": Q}]`, `intervals`,
`status`, `document_ids`.

### 3.5 Experiment

| field | type |
| --- | --- |
| `kind` | `collider` \| `fixed_target` \| `accelerator_neutrino` \| `reactor_neutrino` \| `solar_neutrino` \| `atmospheric_neutrino` \| `astrophysical_neutrino` \| `direct_dark_matter` \| `axion` \| `double_beta_decay` \| `neutrino_mass` \| `muon_precision` \| `rare_kaon` \| `long_lived_particle` \| `cosmic_ray` \| `gamma_ray` \| `heavy_ion` \| `cevns` \| `other` (an experiment can list a `secondary_kinds` array) |
| `collaboration_ids` | usually one |
| `facility_ids`, `site_ids`, `detector_ids`, `beamline_ids`, `accelerator_ids` | |
| `topic_ids` | many-to-many |
| `intervals` | **I** — the historical model; must not collapse to one row when richer information exists |
| `status` | current status (§4) as of the newest `verified_at` |
| `physics_goals` | **S** list of short strings |
| `unique_capabilities` | **S** list |
| `energy_regime` | **S** string |
| `key_specs` | ordered list of `{"label": "Baseline", "quantity": Q}` shown by default (≤ 5) |
| `lineage` | `[{"experiment_id", "relation": "predecessor" \| "successor" \| "upgrade_of" \| "upgraded_to" \| "same_program" \| "complementary", "sources": [...]}]` |
| `external` | `{"inspire_experiment": recid, "greybook": "code", "wikidata": "Q..."}` |
| `document_ids`, `result_ids` | |

### 3.6 Detector

`experiment_ids`, `facility_id`, `site_id`, `technology` (**S** string such
as "single-phase liquid argon TPC"), `technology_class` (`lar_tpc`,
`water_cherenkov`, `liquid_scintillator`, `xenon_tpc`, `argon_tpc`,
`cryogenic_bolometer`, `germanium`, `scintillating_crystal`,
`general_purpose_collider`, `forward_spectrometer`, `ice_cherenkov`,
`sea_cherenkov`, `radio`, `air_shower_array`, `imaging_atmospheric_cherenkov`,
`gaseous_tpc`, `emulsion`, `tracking_calorimeter`, `haloscope`,
`spectrometer`, `other`), `intervals`, `status`, `specs` (**Q** map;
recommended keys per class in Appendix A), `subsystems: [{"name", "description": S}]`,
`document_ids`.

### 3.7 Collaboration

`experiment_ids`, `formation` (**S** Date), `intervals`, `status`,
`membership: {"as_of": "2026-09", "evidence_class": <§5>, "institution_count": S(int), "country_count": S(int), "member_count": S(int), "roster_source_ids": [...]}`,
`leadership: [{"role": "spokesperson", "person_id", "start", "end", "sources"}]`
(optional, sourced), `host_facility_id`, `host_site_id`.

Institution memberships are **not** embedded here; see §3.11.

### 3.8 Institution

`kind` (`university`, `national_laboratory`, `research_institute`,
`international_organization`, `agency`, `company`), `coordinates` (**C**,
`kind: campus|headquarters`), `place`, `country`, `external:
{"inspire_institution": recid, "ror": "https://ror.org/...", "grid": ""}`,
`facility_id` (if this institution operates a facility), `links.website`.

### 3.9 Person (`data/atlas/people/<slug>.json`)

Reuses HEP Graph identity: `id` is `person:inspire:<recid>` and
`external.inspire_author = <recid>`; `external.orcid` optional. Name-only
people are `person:unresolved:<slug>` and never receive a HEP Graph link.

```json
{
  "id": "person:inspire:1019647",
  "type": "person",
  "name": "Silvia Pascoli",
  "external": {"inspire_author": 1019647, "orcid": "0000-..."},
  "affiliations": [{"institution_id": "...", "start": Date|null, "end": Date|null, "role": <§6>, "sources": [], "verified_at": "", "confidence": ""}],
  "memberships": [{"collaboration_id": "...", "institution_id": "...", "start": Date|null, "end": Date|null, "role": <§6>, "evidence_class": <§5>, "sources": [], "verified_at": "", "confidence": ""}],
  "topic_ids": [],
  "hep_graph": {"available": true, "url": "/?source=1019647&mode=live"},
  "sources": []
}
```

`hep_graph.url` is derived at build time from the recid, never typed by hand.

### 3.10 Research topic (`data/atlas/topics/topics.json`, one file)

`[{"id": "topic:neutrino-oscillations", "name", "parent_id": "topic:neutrino-physics"|null, "question": "plain-language scientific question", "overview": "technical paragraph", "observables": ["..."], "sources": []}]`.
Depth ≤ 3. Topic ids referenced anywhere must exist here.

### 3.11 Institution membership (`data/atlas/memberships/<collaboration-slug>.json`)

```json
{
  "collaboration_id": "collaboration:dune",
  "as_of": "2026-09",
  "roster_sources": ["src:dune-institutions-page"],
  "default_evidence_class": "official_institution_list",
  "members": [
    {"institution_id": "institution:university-of-iowa", "start": null, "end": null,
     "evidence_class": "official_institution_list", "sources": ["src:dune-institutions-page"],
     "verified_at": "2026-09-16", "confidence": "verified", "note": "start date not published"}
  ]
}
```

Rule: `start: null` → UI shows "member as of <as_of>; join date not published".
The timeline treats a member with `start: null` as present only for years ≥
the collaboration's formation year and ≤ `as_of`, and labels this as
"membership history unknown" in the legend.

### 3.12 Major result (`data/atlas/results/<slug>.json`)

`experiment_ids`, `collaboration_ids`, `facility_ids`, `detector_ids`,
`date` (**S** Date; the publication or announcement date, say which in
`note`), `topic_ids`, `result_type` (`discovery`, `observation`, `evidence`,
`measurement`, `precision_measurement`, `limit`, `anomaly`, `first_detection`,
`technology_milestone`), `title` (the collaboration's wording), `summary`
(`plain`, `technical`), `why_it_matters`, `key_value` (**Q** or **S** string),
`significance` (**S** string exactly as reported, e.g. "5.9σ local"),
`publication` (External reference), `official_url` (**S**), `hepdata`
(url|null), `sources`.

The validator rejects a `discovery` whose `significance` note does not
exist; the scientific reviewer rejects a `discovery` whose source says
"evidence".

### 3.13 Technical document (`data/atlas/documents/<slug>.json`)

`doc_type` (`conceptual_design_report`, `technical_design_report`,
`technical_proposal`, `letter_of_intent`, `detector_paper`,
`performance_paper`, `physics_paper`, `run_plan`, `beam_design`,
`upgrade_report`, `public_note`, `hepdata_record`, `data_release`,
`software_documentation`, `review_article`), `date` (Date), `owner_ids`
(experiments, facilities, accelerators, beamlines, detectors, collaborations),
`reference` (External reference; `url` required), `volumes:
[{"title", "reference"}]` optional, `sources`.

### 3.14 Source (`data/atlas/sources/<slug>.json`)

```json
{
  "id": "src:dune-fd-tdr-vol-1",
  "type": "source",
  "source_type": "official_experiment_site" | "official_facility_site" | "experiment_registry" | "inspire_record" | "design_report" | "detector_paper" | "hepdata" | "pdg" | "institution_page" | "result_page" | "journal_article" | "arxiv" | "secondary",
  "rank": 1,
  "title": "Deep Underground Neutrino Experiment (DUNE) Far Detector Technical Design Report, Volume I: Introduction to DUNE",
  "publisher": "DUNE Collaboration / JINST",
  "url": "https://doi.org/10.1088/1748-0221/15/08/T08008",
  "reference": {"doi": "...", "arxiv": "2002.02967"},
  "accessed": "2026-09-16",
  "date": "2020-08",
  "excerpt": "optional ≤ 300 char quote supporting the claims that cite this source",
  "link_check": {"last_checked": null, "http_status": null, "redirect": null}
}
```

`rank` is the source-hierarchy position (1 = official experiment site … 12 =
secondary). The methodology document states when rank ≥ 11 is acceptable.

### 3.15 Coverage registry (`data/atlas/coverage/*.json`, merged at build)

```json
[{"name": "DUNE", "experiment_id": "experiment:dune", "category": "accelerator_neutrino",
  "facility": "Fermilab / SURF", "status": "construction", "tier": "A", "priority": 1,
  "researched": "full", "validated": true, "globe_ready": true,
  "missing_fields": [], "owner": "neutrino-lead", "notes": ""}]
```

Each workstream writes its own file (`coverage/<workstream>.json`); the build
merges them and fails on duplicate `experiment_id`. Every experiment named in
the specification's required-coverage sections appears here from day one, with `researched: "none"` until an agent does the
work. The registry is the honest statement of what the atlas covers.

## 4. Status enum

`proposed`, `approved`, `construction`, `commissioning`, `active`,
`shutdown` (temporary stop, e.g. LHC long shutdown), `upgrade`, `completed`
(data taking over, analysis may continue), `decommissioned`, `cancelled`,
`planned`.

Terminal statuses: `completed`, `decommissioned`, `cancelled`. A terminal
interval must have an `end` unless `confidence` is `uncertain` with a note.

Timeline semantics: at year *Y* an entity is **present** if some interval
covers *Y*; its **state** is that interval's status; a `proposed`/`planned`
state renders dimmed and never as "operating". An entity with no interval
covering *Y* is absent.

## 5. Membership evidence classes

| class | meaning | UI wording |
| --- | --- | --- |
| `official_roster` | collaboration's own member/author roster | "Collaboration roster" |
| `official_institution_list` | collaboration or lab published institution list | "Official institution list" |
| `publication_affiliation_current` | affiliation on a collaboration paper within the last 3 years of `as_of` | "Recent collaboration author affiliation" |
| `publication_affiliation_historical` | affiliation on an older collaboration paper | "Historical collaboration author affiliation" |
| `institutional_page` | the institution's own page says its group participates | "Institution states participation" |
| `derived` | inferred; must carry a `note` | "Derived; unverified" |

`derived` members never render as solid dots; they render hollow and are
excluded from counts labelled "member institutions".

## 6. Person roles

`faculty`, `staff_scientist`, `postdoc`, `graduate_student`,
`other_researcher`, `historical_member`, `unknown`. Assign anything other than
`unknown` only when a source states it (institution page, collaboration page).

## 7. Relationships (derived at build time from the fields above)

```
PERSON        --MEMBER_OF(interval, role, evidence)-->  COLLABORATION
PERSON        --AFFILIATED_WITH(interval, role)------->  INSTITUTION
INSTITUTION   --MEMBER_OF(interval, evidence)--------->  COLLABORATION
COLLABORATION --OPERATES----------------------------->  EXPERIMENT
EXPERIMENT    --LOCATED_AT---------------------------->  FACILITY / SITE
EXPERIMENT    --USES----------------------------------> DETECTOR
EXPERIMENT    --USES_BEAMLINE-------------------------> BEAMLINE
BEAMLINE      --FED_BY--------------------------------> ACCELERATOR
DETECTOR      --LOCATED_AT----------------------------> SITE
EXPERIMENT    --STUDIES-------------------------------> TOPIC
RESULT        --PRODUCED_BY---------------------------> EXPERIMENT
RESULT        --MEASURES------------------------------> TOPIC
EXPERIMENT    --PRECEDED_BY / SUCCEEDED_BY / UPGRADE_OF-> EXPERIMENT
DOCUMENT      --DESCRIBES-----------------------------> any owner
PERSON        --HAS_HEP_GRAPH_PROFILE-----------------> (HEP Graph, by INSPIRE recid)
```

The build emits these as an edge list in `generated/graph.json` so a later
feature (recommendations, theory groups, datasets, funders) can add edge
types without changing entity files.

## 8. Generated bundles (`static/atlas/generated/`)

| file | contents | loaded |
| --- | --- | --- |
| `manifest.json` | data version (content hash), build date, entity counts, timeline bounds, bundle sizes | first |
| `atlas.json` | facilities, sites, accelerators, beamlines, experiments (without long text), detectors, collaborations (without memberships), topics, lineage, intervals | first |
| `text.json` | long text: summaries, physics goals, notes | on first panel open |
| `results.json` | all results | results mode / panel |
| `documents.json` | all documents | panel |
| `sources.json` | all sources | "Sources" disclosure |
| `institutions.json` | all institutions with coordinates | collaboration mode |
| `memberships/<collab>.json` | one collaboration's institution rows | collaboration selected |
| `people/<collab>/<institution>.json` | people for one institution in one collaboration | institution clicked |
| `search.json` | typed search index `[type, id, name, aliases, subtitle]` | search focus |
| `graph.json` | edge list (§7) | on demand |

Bundle budget: `atlas.json` + `manifest.json` ≤ 400 KB uncompressed for the
pilot; the build fails above 1.5 MB and prints per-type sizes.

## 9. Validation (structural, build-failing)

Duplicate ids; unknown id prefix; dangling references (any `*_id`/`*_ids`);
missing coordinates on a site; latitude/longitude range; a `detector` marker
using `headquarters` coordinates; interval `end < start`; terminal status with
no end; overlapping same-label intervals; a result with no `sources` or no
`publication`/`official_url`; a `discovery` with empty `significance`;
quantity unit not in its dimension's list; sourced value with empty
`sources`; `confidence != verified` without a note; membership rows whose
institution has no coordinates; topic depth > 3; document with no `url`;
person id `person:inspire:` without a numeric recid; two institutions sharing
an INSPIRE institution recid or ROR; an experiment without a collaboration
**or** an explicit `notes` entry saying why; an experiment with no facility and
no site.

Historical tests (§60 of the specification) live in `tests/test_atlas_history.py`
and assert sampled-year states from the researched intervals.

## 10. Research output format for agents

Research agents return **files**, not prose: the JSON entity files above,
written into `data/atlas/…`, plus a short `RESEARCH_LOG` entry
(`docs/atlas-worklog/<agent>.md`) containing: scope, entities written, sources
added, conflicts found (claim / source A / source B / chosen / why),
unresolved fields, confidence. The orchestrator runs the validator on the
result before review.

## Appendix A — recommended detector spec keys by technology class

| class | keys |
| --- | --- |
| `lar_tpc` | `total_mass`, `active_mass`, `fiducial_mass`, `drift_length`, `readout` (S), `cryostat_count`, `drift_field`, `module_count` |
| `water_cherenkov` | `total_mass`, `fiducial_mass`, `pmt_count`, `tank_height`, `tank_diameter`, `photocoverage` |
| `liquid_scintillator` | `target_mass`, `fiducial_mass`, `pmt_count`, `energy_resolution` (S) |
| `xenon_tpc` / `argon_tpc` | `target_mass`, `active_mass`, `fiducial_mass`, `threshold` (energy), `depth`, `shielding` (S), `exposure` |
| `general_purpose_collider` | `length`, `diameter`, `total_mass`, `solenoid_field`, `toroid_field`, `tracker` (S), `calorimeters` (S), `muon_system` (S), `pseudorapidity_coverage` (S), `trigger_rate` |
| `ice_cherenkov` / `sea_cherenkov` | `instrumented_volume`, `sensor_count`, `string_count`, `depth_min`, `depth_max`, `energy_range` (S) |
| `haloscope` | `cavity_volume`, `magnetic_field`, `frequency_range`, `temperature` |
| `air_shower_array` | `area`, `station_count`, `altitude`, `energy_range` (S) |
| `imaging_atmospheric_cherenkov` | `telescope_count`, `mirror_area`, `energy_range` (S), `altitude` |
| `cryogenic_bolometer` / `germanium` | `isotope` (S), `isotope_mass`, `enrichment` (S), `temperature`, `depth` |
