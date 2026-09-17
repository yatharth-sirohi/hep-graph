# HEP Atlas research method (v0.2, 2026-09-16)

Companion to `docs/HEP_ATLAS_ONTOLOGY.md` (the data contract) and
`docs/HEP_ATLAS_SOURCES.md` (the source-type catalogue). The ontology says what
a record must look like; this document says how a researcher decides what to put
in it. Where the two disagree the ontology wins, and its v0.2 amendments A1–A22
win over its own body.

Audience: every research agent and every human reviewer. Rules that agents must
follow operationally are in `docs/atlas-worklog/RESEARCH_AGENT_RULES.md`; this
document is the reasoning behind them.

---

## 1. Source hierarchy

The atlas prefers the party closest to the fact, and prefers a party that has to
live with being wrong. A collaboration is the authority on its own detector; a
laboratory is the authority on its own accelerators; a journal article is the
authority on a measurement; nobody is the authority on somebody else's history.

**Ordering principle.** Between two sources that disagree, take the one that is
(1) primary rather than reporting, (2) official rather than third-party,
(3) technical rather than promotional, (4) newer rather than older *when the
fact can change*, and (5) older rather than newer when the newer source is
merely repeating the older one.

### 1.1 Derived rank table

`rank` is **derived from `source_type`** (A7/A18) and must never be authored in
a source file; the validator recomputes it. Lower is better.

| rank | `source_type` | what it is |
| --- | --- | --- |
| 1 | `official_experiment_site` | the collaboration's own web pages |
| 2 | `official_facility_site` | the host laboratory's own web pages |
| 3 | `experiment_registry` | CERN Greybook |
| 3 | `inspire_experiment_record` | INSPIRE `/experiments/<recid>` |
| 4 | `design_report` | CDR, TDR, technical proposal, letter of intent |
| 5 | `detector_paper` | the instrument paper for a detector |
| 6 | `hepdata` | the numbers behind a published figure or table |
| 7 | `pdg` | Review of Particle Physics review chapters |
| 8 | `institution_page` | a member institution's own group page |
| 8 | `geocoder` | ROR, GeoNames, OSM/Nominatim |
| 9 | `result_page` | a collaboration's public result page |
| 9 | `press_release` | a lab or collaboration press office |
| 9 | `project_document` | funding-agency and strategy documents (P5, ESPP, roadmaps) |
| 10 | `journal_article` | a refereed publication |
| 10 | `arxiv` | a preprint |
| 10 | `inspire_literature_record` | INSPIRE `/literature/<recid>` |
| 12 | `wikipedia` | Wikipedia |
| 12 | `wikidata` | Wikidata |
| 12 | `secondary` | anything else: news, blogs, talks, theses used as pointers |

**Rank is not a quality score for the claim; it is a distance-to-the-fact score.**
A PDG review chapter (rank 7) is a better source for "what is the world-average
top-quark mass" than a collaboration's own page (rank 1), because averaging is
what PDG is for. Rank decides tie-breaks, not topic fit.

### 1.2 What each rank is allowed to carry

- A value with `confidence: "verified"` must cite at least one source of **rank ≤ 10** (A17).
- Coordinates of `kind: detector` or `underground_lab` may **not** rest solely on a
  `geocoder` source or on any source of rank ≥ 8 (A17). Geocoder coordinates are
  `campus` or `headquarters` only.
- Rank ≥ 11 (`wikipedia`, `wikidata`, `secondary`) may be used **only as a pointer**:
  to find the real source, to disambiguate a name, or as a second corroborating
  source next to a better one. It may never be the sole source of a critical value.
- A `press_release` may establish *that* an announcement happened and *when*, but
  never the wording of a scientific claim (A16); see §6.
- A source whose `retrieval` is `failed` may not be cited at all (A18).

### 1.3 Reuse before creation

Before creating a `src:` record, grep `data/atlas/sources/` for the same URL or
DOI and reuse the existing id, updating `accessed`. Two source records sharing a
normalised URL or DOI is a build failure (A20). Every `src:` id carries the
programme slug of the agent that created it (`src:topic-…`, `src:dune-…`).

---

## 2. Experiment, collaboration, detector, facility, site

These four are different things and the atlas keeps them apart even when a
single word is used for all of them in conversation.

| type | the question it answers | identity rule |
| --- | --- | --- |
| `facility` | *Who runs this place?* | one laboratory or observatory operator |
| `site` | *Where exactly is it?* | one geographic point where hardware physically sits |
| `experiment` | *What scientific programme is this?* | one approved programme with its own name, approval and physics goals |
| `collaboration` | *Who are the people and institutions?* | one signing body with a membership list and leadership |
| `detector` | *What is the apparatus?* | one instrument with its own technology and specifications |

Rules of thumb:

- **One experiment may have several detectors** (DUNE far detector modules, near
  detector) and **one detector may serve several experiments** over its life
  (`detector.experiment_ids` is a list, and `detector.placements[]` carries the
  role and the dates).
- **Experiment and collaboration are usually 1:1 but not always.** SBN is one
  programme run by three collaborations; Belle and Belle II are two experiments
  with two collaborations and overlapping people.
- **A collaboration outlives its detector.** Analysis continues after data
  taking; collaboration intervals and experiment intervals are separate.
- **A detector is not a site.** `detector:icarus-t600` is one instrument that has
  occupied three sites; the sites are three `site:` records and three
  `placements[]` rows.
- **A sub-array is a detector with a parent, not a subsystem.** A physically
  distinct, separately instrumented array that is nonetheless part of a larger
  detector's data-taking gets its own `detector:` record with
  `parent_detector_id` pointing at the whole (A2), rather than being folded
  into `subsystems[]`. `detector:icecube-deepcore` and `detector:icetop` each
  carry `parent_detector_id: "detector:icecube"` and their own
  `experiment_ids: ["experiment:icecube"]`; they are not IceCube subsystems
  because each has its own instrumentation, siting detail (DeepCore is the
  denser infill at the bottom of the array; IceTop is the surface array) and,
  in IceTop's case, its own distinct physics role (cosmic-ray air showers
  rather than in-ice Cherenkov light). Use `subsystems[]` instead when the
  component has no separate identity outside the parent instrument (a
  calorimeter inside ATLAS is a subsystem, not a `detector:` record).
- **Facility operator is a relationship, not a caption.** `facility.operator`
  (§3.1) is superseded by `facility.operator_ids` + `operator_text` (A1):
  `operator_ids` links to the `institution:` record(s) that actually run the
  site when that operator is itself modelled in the atlas (CERN operates
  `facility:cern` through `institution:cern`; Fermilab through
  `institution:fermilab`); `operator_text` is the sourced free-text fallback
  for an operator that is a consortium, agency or authority not otherwise
  represented as an `institution:` record (e.g. a state science authority
  running an underground lab). `institution.facility_id` is the reverse
  pointer, set on the operating institution's own record, and the two must
  agree. Do not fill the legacy scalar `operator` on new records.

### 2.1 Worked edge cases

**CERN.** CERN exists three times, with three ids and three roles (ontology §0.5):
`facility:cern` (the laboratory that hosts the LHC and the North Area),
`institution:cern` (the member institution that appears in ATLAS, CMS, DUNE and
other membership rosters), and membership rows for `institution:cern` inside each
collaboration file. The accelerators (`accelerator:lhc`, `accelerator:sps`, …)
belong to the facility, not to the institution. A CERN *experiment* such as NA62
is an `experiment:` record with a `facility_roles[]` row pointing at
`facility:cern` with role `host`.

**Fermilab.** The same three-way split: `facility:fermilab` (the laboratory and
its proton complex), `institution:fermilab` (the member institution in DUNE,
CMS, NOvA, …). Fermilab additionally plays `beam_source` for experiments whose
detectors are elsewhere.

**DUNE.** One experiment (`experiment:dune`), one collaboration
(`collaboration:dune`), several detectors (far detector modules, near detector),
and **two facilities with different roles**: `facility:fermilab` with role
`beam_source` (it provides the LBNF beam), and `facility:surf` with role
`detector_host` (the far detectors sit on the 4850-foot level). That is exactly
why `experiment.facility_roles[]` exists rather than a bare `facility_ids` list:
"DUNE is at Fermilab" and "DUNE is at SURF" are both true and mean different
things.

**SBN.** The Short-Baseline Neutrino programme is **one programme with three
experiments**: SBND, MicroBooNE and ICARUS each keep their own `experiment:`,
`collaboration:` and `detector:` records, all on the Booster Neutrino Beam.
`collaboration:sbn` exists as the joint body. The programme relationship is
expressed with `lineage` rows of relation `same_program`, written on the
lexicographically smaller id (A1), not by inventing a fourth experiment record.

**ProtoDUNE.** The ProtoDUNE detectors are **detectors, not experiments**, with
their own ids (`detector:protodune-*`), `experiment_ids` pointing at
`experiment:dune`, and a `placements[]` row with role `prototype` at a CERN site.
`experiment:dune` gains a `facility_roles[]` row for `facility:cern` with role
`prototype_host`. They are not a separate scientific programme; treating them as
one would double-count DUNE on the globe and in coverage.

**ICARUS moved between laboratories.** ICARUS T600 ran at LNGS, went to CERN for
overhaul, and now runs at Fermilab. That is **one detector id**
(`detector:icarus-t600`) with three `placements[]` rows, each carrying a
`site_id`, a `role` (`main`, `storage`) and its own `start`/`end`. Whether it is
one experiment or two is decided by the *programme*, not by the hardware: the
LNGS run and the Fermilab run have different beams, different physics goals and
different approvals, so they are separate `experiment:` records linked by
`lineage` relation `predecessor`. The `detector:` record is shared between them.
The general rule: **hardware continuity is recorded on the detector; programme
discontinuity is recorded as a new experiment with lineage.** A revived
programme is never the same experiment id (A3).

---

## 3. Scope boundary

The atlas covers **experimental high-energy, particle and astroparticle physics**:
the programmes a particle physicist would recognise as their own field, plus the
facilities, detectors, collaborations and people that make them work. Theory
without an experiment, and instruments that do not address a particle-physics
question, are out.

### 3.1 The test

An entity is in scope if **either** (a) it is an accelerator-based particle
physics programme, **or** (b) it materially participates in a question that is
listed in `data/atlas/topics/topics.json`, that is, a question a particle
physicist would take to Snowmass, to the European Strategy, or to a P5-style
prioritisation.

The 2023 P5 report frames the field as three themes — decipher the quantum
realm, illuminate the hidden universe, explore new paradigms in physics — and
six science drivers: elucidate the mysteries of neutrinos; reveal the secrets of
the Higgs boson; determine the nature of dark matter; understand what drives
cosmic evolution; search for direct evidence of new particles; pursue quantum
imprints of new phenomena. If an instrument does not serve one of those, it needs
a specific justification in `notes` to be admitted.

### 3.2 Explicit inclusions

| in scope | why |
| --- | --- |
| CTAO (Cherenkov Telescope Array Observatory) | very-high-energy gamma-ray observatory; its science case includes dark-matter annihilation searches, axion-like-particle conversion and Lorentz-invariance tests, and it is a particle-detection instrument (air-shower Cherenkov imaging), not an optical telescope |
| Pierre Auger Observatory | ultra-high-energy cosmic rays: composition, spectrum cutoff, hadronic interactions at energies above accelerator reach, and cosmogenic neutrino limits |
| HAWC | wide-field TeV air-shower array; Galactic PeVatron identification, dark-matter indirect searches, multimessenger follow-up |
| LHAASO | highest-energy gamma-ray and cosmic-ray measurements; PeVatron identification |
| IceCube, KM3NeT, Baikal-GVD | neutrino telescopes measuring astrophysical neutrinos and atmospheric oscillations |
| AMS-02, Fermi-LAT, DAMPE, CALET | space-borne particle spectrometers and pair-conversion telescopes measuring cosmic-ray and gamma-ray spectra used in dark-matter searches |
| RHIC, sPHENIX, STAR, ALICE, the Electron-Ion Collider | quark-gluon plasma and nucleon structure: QCD questions using particle-physics detectors, explicitly connected to the Energy Frontier in the Snowmass QCD and heavy-ion report |
| Reactor and spallation-source neutrino experiments (Daya Bay, JUNO, COHERENT, …) | neutrino mixing, coherent scattering, sterile searches |
| Underground rare-event laboratories (LNGS, SURF, SNOLAB, CJPL, Kamioka, Boulby, …) | host dark-matter, double-beta-decay and solar-neutrino experiments |
| PSI, TRIUMF, J-PARC MLF muon and pion beams | charged-lepton-flavour-violation and muon precision programmes |
| Gravitational-wave observatories (LIGO, Virgo, KAGRA) | **as multimessenger partners only**: they appear because joint neutrino/gamma/gravitational-wave events are a topic; their internal instrumentation is not researched to atlas depth |

### 3.3 Explicit exclusions

| out of scope | why |
| --- | --- |
| Optical and radio astronomy (VLT, JWST, ALMA, SKA, Hubble) | photons in the thermal regime, measuring astrophysical objects rather than particle properties; no particle-physics question depends on them in the way the topics list defines. Cosmological *surveys* that constrain neutrino mass or dark energy (DESI, Rubin/LSST, CMB-S4) are a **borderline set**: they are referenced from topics and results where they set a particle-physics parameter, but they are not given facility/detector records in the pilot |
| Most nuclear structure physics (FRIB, ISOLDE, GANIL, nuclear astrophysics beams) | measures properties of nuclei, not of the Standard Model's parameters. The exception is any programme feeding a particle-physics question: neutrinoless double beta decay, nuclear matrix elements for it, coherent neutrino scattering targets, or beta-decay endpoint spectroscopy |
| Applied and medical accelerators, synchrotron light sources, spallation neutron scattering | the accelerator is a tool for another field. A spallation source appears only in its role as a neutrino source (SNS for COHERENT) |
| Atomic, molecular and optical physics | out, except where an AMO experiment sets a particle-physics limit (electron EDM in polar molecules, atomic parity violation, optical-clock tests), which enters as a **result** attached to a topic rather than as a facility |
| Pure phenomenology and theory groups | the atlas maps experiments; theory enters as `document` records and as topic sources |
| Retired programmes with no surviving public documentation | not excluded in principle, but a programme for which no rank ≤ 10 source can be reached is recorded at coverage tier E with `researched: "none"` rather than filled in from memory |

**Borderline entries must say so.** Any entity admitted under a judgement call
carries a `notes` entry naming the topic that justifies it.

---

## 4. Establishing institution membership

Institution membership lives in `data/atlas/memberships/<collaboration-slug>.json`
(§3.11), never embedded in the collaboration record.

### 4.1 Evidence classes and their exact UI wording

Every membership row carries `evidence_class` and its own non-empty `sources`
(A19; `default_evidence_class` is removed). The UI wording below is normative —
it is what a viewer sees, and it must not be paraphrased in the interface.

| class | when it applies | exact UI wording |
| --- | --- | --- |
| `official_roster` | the collaboration's own member or author roster | `On the collaboration's own member list (as of <as_of>)` |
| `official_institution_list` | a collaboration- or lab-published institution list | `On the official institution list (as of <as_of>)` |
| `inspire_author_profile` | an INSPIRE author record naming the collaboration | `INSPIRE author profile lists this collaboration` |
| `publication_affiliation_current` | affiliation on a collaboration paper within 3 years of `as_of` | `Listed with this affiliation on a <collab> paper (<year>); current membership not confirmed` |
| `publication_affiliation_historical` | affiliation on an older collaboration paper | `Listed on a <collab> paper in <year>; may no longer be a member` |
| `institutional_page` | the institution's own page states that its group participates | `The institution's own page states participation (checked <date>)` |
| `self_reported` | a personal page or CV | `Self-reported` |
| `derived` | inferred, institution rows only | `Inferred, not verified` |

**Precedence when several classes apply** (strongest first):
`official_roster` > `official_institution_list` > `inspire_author_profile` >
`publication_affiliation_current` > `institutional_page` > `self_reported` >
`publication_affiliation_historical` > `derived`.

**Source-type consistency** is enforced: `official_*` requires a source of type
`official_experiment_site`, `official_facility_site` or `experiment_registry`;
`publication_*` requires `journal_article`, `arxiv`,
`inspire_literature_record`, `detector_paper` or `design_report`;
`institutional_page` requires `institution_page`.

**Counting.** A count labelled "member institutions" includes only `official_*`,
`inspire_author_profile`, `publication_affiliation_current` and
`institutional_page`. `derived` rows never render as solid dots and are excluded
from every count.

### 4.2 Current versus historical

- `publication_affiliation_current` requires `evidence_date` and **fails** when
  `as_of − evidence_date > 3 years`. If the only paper you can find is older,
  the row is `publication_affiliation_historical`, not "current".
- `publication_affiliation_historical` requires `end` or `known_until`. You may
  not assert that a 2009 author list proves present membership.
- A row is a solid, counted member at year *Y* only when `[start, end]` or
  `[known_since, known_until]` covers *Y* (A5). `known_since`/`known_until` are
  the earliest and latest **evidence** dates, never join dates, and
  `known_since ≤ known_until ≤ as_of` is enforced.
- Between the collaboration's formation and `known_since` the row renders hollow
  as an "undated member" and is excluded from counts, unless the file declares
  `membership_history: "complete"`. Every membership file must declare
  `membership_history` as `unknown`, `partial` or `complete`.
- After `as_of` and before the build date the row renders hollow as
  "not re-verified".
- The v0.1 rule that a member with `start: null` is present from the formation
  year is **withdrawn**.

### 4.3 "Join date not published"

Almost no collaboration publishes when an institution joined. The correct record
is `start: null` with `note: "join date not published"`, not a guessed year. The
UI then shows *"member as of \<as_of>; join date not published"* and the timeline
legend says "membership history unknown". Inventing a start date to make a card
look complete is a P0 defect (ontology §0.3).

### 4.4 Roster snapshots

`roster_snapshots: [{"as_of", "sources"}]` records each time the roster was read.
This is how the atlas can later say "the list grew from 178 to 209 institutions
between 2022 and 2026" without pretending to know each individual join date.
`roster_sources` is documentation of where the file came from, not a substitute
for per-row `sources`.

---

## 5. Establishing person membership

People are the most sensitive records in the atlas and the most easily got wrong.

- **INSPIRE ids only.** A resolved person is `person:inspire-<recid>` with
  `external.inspire_author = <recid>` (A6). A person you cannot resolve is
  `person:unresolved-<collab>-<institution>-<name>` and is **scoped**: never
  merged across collaborations, never given a HEP Graph link. Two unresolved
  rows with the same name in different collaborations stay two rows.
- **Identity evidence is required.** Every `person:inspire-*` carries
  `identity_evidence.method` ∈ {`orcid`, `collaboration_page_link`,
  `inspire_profile_affiliation_match`, `institution_page_link`} with its own
  sources. Matching on name alone is not identity evidence.
- **`derived` is forbidden on person rows** (A19). If you cannot establish a
  person's membership from an actual source, you do not create the row.
- **Roles only when a source states them.** `affiliations[].role` is one of
  `faculty`, `staff_scientist`, `postdoc`, `graduate_student`,
  `other_researcher`, `historical_member`, `unknown`; anything other than
  `unknown` requires a source that says so (an institution page, a group page).
  Inferring "postdoc" from a publication list is not allowed.
  `memberships[].role` no longer exists on people (A6); collaboration-level roles
  live in `collaboration.leadership[]` with roles `spokesperson`,
  `deputy_spokesperson`, `physics_coordinator`, `technical_coordinator`,
  `ib_chair`, `other`, each sourced and dated.
- **Author-list-derived people must be labelled as such.** A person extracted
  from a collaboration author list carries
  `evidence_class: "publication_affiliation_current"` or
  `"publication_affiliation_historical"` with the paper's `evidence_date`, and
  the UI shows the wording in §4.1 verbatim. An author list is evidence that a
  person was on a paper, not that they are a member today, and never evidence of
  their role.
- **Affiliation rows carry `evidence_class` and `evidence_date` too.** A person's
  institution is as much a claim as their membership.
- **People are never in `search.json`** (A14); people search is delegated to HEP
  Graph live search by INSPIRE recid. `hep_graph.url` is derived at build time
  from the recid and never typed by hand.
- **Do not crawl.** Institution pages are read individually, not scraped en
  masse; INSPIRE is limited to one request every 10 s per agent.

---

## 6. Selecting and wording results

### 6.1 The selection standard

A `result:` record is created only when **all** of the following hold:

1. The collaboration itself presented it as a result — a publication, a
   conference presentation with a public note, or a result page. Not a rumour,
   not a plot in a talk without a note.
2. It is one of: a first observation or discovery; evidence for a process; a
   measurement that is the world's best or the first of its kind; a limit that
   defines the current frontier for that parameter; a documented anomaly; a first
   detection of a source or messenger; or a technology milestone (first operation
   of a new detector type at scale, a record resolution).
3. It matters to a topic in `topics.json`. A result with no `topic_ids` is a
   review flag.
4. It has a `publication` external reference or an `official_url`.

Routine updates of an existing measurement are **not** separate results; they
update the existing record's numbers and `date`. The atlas is a map, not a
bibliography.

### 6.2 Wording: use the collaboration's own

Use the collaboration's vocabulary and do not inflate it:
`discovery` > `observation` > `evidence` > `measurement` / `precision_measurement`
> `limit` > `anomaly`. If the collaboration says "evidence", the record says
`evidence`, whatever the significance quoted elsewhere.

`result.claim` is **required**:

```json
"claim": {"quote": "...", "locator": "abstract", "sources": ["src:..."]}
```

- `claim.quote` is **verbatim** text from the publication title or abstract, or
  from the collaboration's own result page. It may **never** come from a press
  release, from PDG, or from Wikipedia (A16). Maximum 300 characters.
- Mechanical check: `result_type: discovery` requires "discover" in
  `claim.quote` or in the title of a cited source; `observation` requires
  "observ"; `evidence` requires "evidence".
- `significance` is recorded **exactly as reported** ("5.9σ local", "6.7 sigma
  confidence level"), as a sourced string, not recomputed.
- A `discovery` with an empty `significance` fails validation; a `discovery`
  whose source says "evidence" is rejected in review.

### 6.3 `date` and `date_kind`

`result.date_kind` is **required** and is one of:

| value | meaning |
| --- | --- |
| `announcement` | the date the collaboration first presented it publicly (seminar, press event) |
| `preprint` | the date the preprint appeared |
| `publication` | the date of the refereed publication |

`result.announced` and `result.published` may both be recorded; `result.date` is
the display date and is the earliest non-null of them, with `date_kind` naming
which one it is. The July 2012 Higgs result has `announced: "2012-07-04"`,
`published` in August/September 2012, `date: "2012-07-04"` and
`date_kind: "announcement"`.

Validator constraints: a non-milestone result dated before every listed
experiment's earliest commissioning or active start is an error; a result dated
after the build date is an error; results appear on the timeline at year *Y* iff
`lo(result.date) ≤ Y_hi`.

### 6.4 Attribution

`result.experiment_ids` may contain plain ids or `{"id", "sources"}` objects when
attribution itself needs a source (joint results, results reassigned between a
detector and its successor). Do not attribute a combination to one of its inputs.

---

## 7. Selecting documents

A `document:` record is created for a document a reader would actually want to
open: the conceptual and technical design reports, the technical proposal or
letter of intent, the detector paper, the performance paper, run plans, beam
design reports, upgrade reports, and data releases. `doc_type` comes from the
§3.13 enum.

- `reference.url` is **required**; a document with no URL fails validation.
- Multi-volume reports are **one** document with `volumes: [{"title", "reference"}]`,
  not one record per volume.
- `owner_ids` point at the experiments, facilities, accelerators, beamlines,
  detectors or collaborations the document describes; `document_ids` on those
  entities are derived at build and must not be authored (A1).
- When the same DOI is both a source and a document, link them with
  `document.source_id` rather than duplicating the record (A7).
- Physics papers are documents only when they are landmark or definitional for
  the entity; otherwise they are sources on a result.

---

## 8. Dates and precision

### 8.1 Precision is the string length

`"2008"` is a year, `"2008-09"` a month, `"2008-09-10"` a day. For an imprecise
date *d*, `lo(d)` and `hi(d)` are the first and last day it can denote (A3). Do
not pad a year out to a day to look precise; do not round a day back to a year
to avoid checking.

### 8.2 Qualifiers

The Date object (A4) may carry:

- `approx: true` — the source itself gave an approximate date ("~2030"). A day-
  precision date with `approx` is a validator warning: if you know the day, it is
  not approximate.
- `planned: true` — **the source is a schedule or a plan, not a report of an
  event**. This is the most misread field in the schema. `planned` stays true
  after the date passes, so the UI can say "was planned for 2030" rather than
  silently asserting that it happened. A future date **without** `planned: true`
  is an error; a `planned` date that has passed with no non-planned interval is
  a warning that someone must go and check what actually happened.
- `earliest` / `latest` — the window the source allows, with
  `earliest ≤ date ≤ latest`.
- `display` — the source's own wording, shown in the UI ("Spring 2008", "~2030").

Seasons are stored as the middle month with `earliest`/`latest` at the first and
last month of the season (spring 03–05, summer 06–08, autumn 09–11, winter
12–02) and the season text in `display`.

### 8.3 Intervals

Give the **richest sourced history**: proposal, approval, construction,
commissioning, runs, shutdowns, upgrades, completion. Do not collapse a known
history into a single row. Intervals on one entity may not overlap unless they
carry different labels.

- `start: null` means "start unknown", **not** "since forever"; the UI says
  "start unknown".
- `end: null` on a non-terminal interval means ongoing, and extends to the
  **build date** from `manifest.json`, not to `verified_at`. Years after the
  build date render dimmed as "assumed ongoing" and are not counted as active.
- Terminal statuses (`completed`, `decommissioned`, `cancelled`) are events and
  need no `end`. A non-terminal interval starting after a terminal start is an
  error: a revived programme is a new experiment id with `lineage`.
- Interval bounds at **day or month precision require a `quote` or `locator`**
  (A15). If you can name the day, you can name where you read it.
- An interval whose `start.planned` is true may not carry status `active`,
  `commissioning`, `completed` or `decommissioned` (A21).
- Entity-level `status` must equal the derived state at the build date, or the
  validator errors (A10). Do not hand-maintain a status that contradicts the
  intervals.

### 8.4 Never fabricate precision

Never derive an exact date from an approximate source. "Construction began in the
mid-1990s" becomes `{"date": "1995", "approx": true, "display": "mid-1990s",
"earliest": "1994", "latest": "1996"}`, with a note — not `"1995-01-01"`.

---

## 9. Representing uncertainty

Every sourced value carries `confidence` ∈ {`verified`, `derived`, `approximate`,
`uncertain`}. A `note` is **required** whenever `confidence != "verified"`.

| value | what it asserts | when to use it | exact UI wording |
| --- | --- | --- | --- |
| `verified` | a source of rank ≤ 10 states this value directly | the normal case | *(no badge shown)* |
| `derived` | the atlas computed it from sourced inputs | unit conversion, a great-circle distance from two sourced coordinates, a total from sourced parts | `Calculated from other sourced values` |
| `approximate` | the source gives it approximately or as a round number | "about 1300 km", "~40 000 PMTs" | `The source gives an approximate value` |
| `uncertain` | a source exists but is weak, ambiguous, or contradicted | two sources disagree and neither is clearly better; the source is rank ≥ 11; the wording is ambiguous | `The source is unclear or sources disagree` |

Three rules that are easy to get wrong:

1. **`uncertain` still needs a source** (A17). It means *the source* is weak, not
   that you are guessing. A field with no source is `null` plus a `note`, full
   stop. A sourced value with an empty `sources` list is rejected.
2. **`derived` on a value is not the same as `derived` in an evidence class.**
   The first is an arithmetic statement about the atlas's own computation; the
   second is a membership claim nobody verified, and is forbidden on people.
3. **`null` is a legitimate value.** "Unknown is a value" (ontology §0.3): `null`
   with a `note` saying what you looked at and what it did not say is a better
   record than a plausible number.

A `verified` value whose only source later 404s is not silently downgraded: the
link checker lists it as "review required" and a human decides (A22).

---

## 10. Recording and resolving source conflicts

Conflicts are data, not noise. They are how the atlas earns trust.

### 10.1 Recording

1. Record the value you chose as a normal sourced value, citing the source you
   believe.
2. Set `confidence: "uncertain"` if the disagreement is unresolved, or keep
   `verified` if the losing source is clearly superseded.
3. Put the rejected value, its source, and the reason in the value's `note`:
   *"CERN Greybook gives 1998; the collaboration's own history page gives
   1997-11; took the collaboration page (rank 1 over rank 3)."*
4. Cite **both** sources on the value where both are genuine evidence, so the
   sources panel shows the reader what the disagreement was.
5. Log the conflict in `docs/atlas-worklog/<agent>.md` under **Conflicts** in the
   form *claim / source A / source B / chosen / why*. The worklog is the audit
   trail; the note is what the reader sees.

### 10.2 Resolving

In order:

1. **Primary over reporting.** The party that did the thing beats the party that
   wrote about it.
2. **Rank.** Lower rank wins between sources of comparable topic fit (§1.1).
3. **Purpose fit.** A source whose job is this number wins over a source that
   mentions it in passing: PDG for world averages, HEPData for the numbers behind
   a figure, the TDR for a design parameter, the run plan for a schedule.
4. **Recency, but only for facts that change.** Institution counts, statuses and
   schedules: newest wins. Historical dates: the newest source is often just
   copying an older one, so prefer the source closest to the event.
5. **Unit and definition check before declaring a conflict.** Most apparent
   disagreements are total versus fiducial mass, design versus achieved
   luminosity, beam energy versus centre-of-mass energy, or announcement versus
   publication date. Say which definition you took.
6. **If genuinely unresolved:** `confidence: "uncertain"`, both sources cited,
   both values in the `note`, and a line in the worklog's **Unresolved fields**.
   Never average two sourced values into a third that no source states.

### 10.3 Superseded records

An entity that turns out to be a duplicate is not deleted: it gains
`superseded_by: <id>` and references resolve through it (A6). Two records that
look like duplicates but are genuinely distinct must list each other in
`distinct_from: [id]`, or the duplicate detector fails the build (A20).

---

## 11. Coverage tiers

`coverage.tier` states how deeply the atlas intends to cover an entity; it is a
**plan**, not an achievement. `coverage.researched` (`none`/`partial`/`full`) is
the achievement, and `validated` and `globe_ready` are build outputs that must
not be authored (A10). Both live alongside the registry rows in
`data/atlas/coverage/<workstream>.json`.

| tier | meaning | what a tier-complete record contains |
| --- | --- | --- |
| **A** | Flagship. A programme a newcomer would expect to find and explore in depth. | Full history (proposal → approval → construction → commissioning → runs → shutdowns → upgrades), every detector with technology and key specs, sited coordinates of `kind: detector`/`underground_lab`, collaboration with a dated institution roster and leadership, the major results with `claim.quote`, the design reports and detector papers, and an INSPIRE experiment id. Examples: ATLAS, CMS, DUNE, IceCube, Super-Kamiokande, LHCb, Belle II. |
| **B** | Major. Scientifically important and well documented, but not a landing page. | Intervals to at least construction/active/completion granularity, the principal detector with its main specs, correct sites, a roster snapshot with `membership_history` declared, the two or three defining results, the TDR or detector paper, and an INSPIRE experiment id. Examples: NOvA, T2K, MicroBooNE, LZ, XENONnT, NA62, Pierre Auger. |
| **C** | Covered. Appears correctly on the globe and in search, with a real summary. | Identity, kind, host facility and site with coordinates, a lifecycle interval, a sourced plain-language summary, topic links, and at least one result or document. Roster may be absent. Examples: smaller running experiments, historical programmes with good documentation. |
| **D** | Listed. Present so the map is not misleading by omission. | Identity, host facility, an approximate lifecycle interval, topic links, and a record-level source. Explicitly incomplete: `researched: "none"` or `"partial"` with `missing_fields` filled in honestly. |
| **E** | Named only. Known to exist, not yet researched, or no reachable sources. | The id, name, aliases, one source, and a `notes` entry saying why it is at tier E. Never rendered as a globe marker with invented coordinates. |

Rules:

- **Every experiment named in the specification's required-coverage sections
  appears in the registry from day one**, with `researched: "none"` until an
  agent does the work. The registry is the honest statement of what the atlas
  covers, including what it does not.
- **`missing_fields` must be honest.** A tier-A row with `researched: "full"` and
  an empty `missing_fields` is a claim that a reviewer will check.
- **Tier A and B rows require `external.inspire_experiment`**, or an explicit
  note saying why the experiment has no INSPIRE experiment record (A20).
- Tier is not prestige. A historically decisive but sparsely documented
  programme can be tier C; a well documented small experiment can be tier B.
  Tier answers "how much of this do we intend to hold?", not "how good was it?".

---

## 12. Topics

`data/atlas/topics/topics.json` is a single file holding the whole taxonomy
(§3.10), maximum depth 3. Every `topic_id` referenced anywhere must exist there.

Authoring rules applied to the current file:

- `question` is plain language, ≤ 40 words, and is a real question a
  non-specialist would ask, not a restatement of the topic name.
- `overview` is 60–120 words, written for a reader who knows some physics, and
  **verified against a fetched source**. Physics is never written from memory.
- **Hypothetical things are named as hypothetical.** Sterile neutrinos, axions,
  dark photons, heavy neutral leptons, supersymmetric partners, WIMPs, the
  Majorana nature of the neutrino and neutrinoless double beta decay are
  described as conjectured, hypothetical or unobserved, with the current status
  of the search stated plainly.
- `observables` lists what an experiment actually measures for this topic, in the
  vocabulary of the cited review, so results and experiments can be matched to it.
- Every leaf carries at least one authoritative reference: a PDG review chapter,
  a Snowmass 2021 report or topical-group report, the 2023 P5 report, or a
  refereed review article. Community roadmaps are cited for programme statements
  and PDG for physics statements, not the other way round.
