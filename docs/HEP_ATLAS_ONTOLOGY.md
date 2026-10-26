# HEP Atlas ontology and data contract (v0.2, 2026-09-16)

This document is the interface contract between every HEP Atlas workstream:
research agents produce records in this shape, the validator enforces it, the
build step generates the browser bundles from it, and the globe renders those
bundles. Nothing in `hepgraph/` outside `hepgraph/atlas/` depends on it, and
HEP Graph (the people network) is unchanged by it.

Status of this document: **draft under review**. Reviewers challenge it; the
orchestrator resolves conflicts; the version number changes when a field's
meaning changes.


## v0.2 amendments (resolved from the entity-schema and temporal-model reviews)

These override anything below that contradicts them. Files written under v0.1
remain valid where the change is additive; the build normalises the rest.

**A1. One canonical direction per relation; inverses are derived at build.**
Canonical (kept in data files): `site.facility_id`, `accelerator.facility_id`,
`accelerator.feeds_accelerator_ids` (downstream), `beamline.accelerator_id`,
`beamline.facility_id`, `detector.experiment_ids`, `detector.placements`,
`experiment.collaboration_ids`, `experiment.facility_roles`,
`experiment.beamline_ids`, `experiment.accelerator_ids`, `experiment.topic_ids`,
`experiment.lineage` (only `predecessor`, `upgrade_of`, `same_program`,
`complementary`; the latter two live on the lexicographically smaller id),
`result.experiment_ids`, `document.owner_ids`, `institution.facility_id`,
`institution.parent_institution_id`, `facility.primary_site_id` (a choice),
`facility.operator_ids` (+ `operator_text` S). Derived (do not write; the
validator warns and the build ignores them): `facility.site_ids`,
`facility.accelerator_ids`, `facility.beamline_ids`, `facility.institution_id`,
`accelerator.beamline_ids`, `accelerator.serves_experiment_ids`,
`experiment.detector_ids`, `experiment.site_ids`, `experiment.result_ids`,
`*.document_ids`, `collaboration.experiment_ids`, `successor`/`upgraded_to`
lineage rows.

**A2. Placement has role and time.** `detector.placements: [{"site_id", "role":
"main"|"near"|"far"|"prototype"|"storage", "start": Date|null, "end": Date|null,
"sources", "verified_at", "confidence", "note"}]` replaces `detector.site_id`
and `detector.facility_id` (legacy scalar accepted and migrated as one `main`
placement with null dates). `experiment.facility_roles: [{"facility_id",
"role": "host"|"beam_source"|"detector_host"|"prototype_host", "sources"}]`
replaces `experiment.facility_ids` (legacy list accepted, role `host`).
`detector.parent_detector_id` for DeepCore/IceTop-style sub-arrays.

**A3. Timeline semantics (replaces §4 "Timeline semantics").** For an
imprecise date d, `lo(d)`/`hi(d)` are the first/last day it can denote
("2008" → 2008-01-01/2008-12-31). The slider selects a closed range
`[Y_lo, Y_hi]` at its resolution. An interval **covers** the selection iff
`lo(start) ≤ Y_hi` and (`end` null or `hi(end) ≥ Y_lo`); coverage is
**certain** if also `hi(start) ≤ Y_lo` and (`end` null or `lo(end) ≥ Y_hi`),
else **possible** (rendered hatched). `start: null` covers only
`[lo(end), hi(end)]`. Open intervals (`end: null`) extend to the **build date**
from `manifest.json`, not to `verified_at`; for years after the build date they
render dimmed "assumed ongoing" and are not counted as active.
**Presence** at Y uses the entity's existence hull `[lo(earliest start),
lo(earliest terminal start) or build date]`. **State** at Y is chosen among
covering intervals: (1) if any covering interval has status in {construction,
commissioning, active, shutdown, upgrade} or is terminal, drop {proposed,
approved, planned} candidates; (2) pick the latest `lo(start)`; (3) tie-break by
rank decommissioned > cancelled > completed > shutdown > upgrade > active >
commissioning > construction > approved > proposed > planned. Other covering
intervals become `secondary_states` (tooltip). Hull covers Y but no interval
does → state `unrecorded` (grey). Terminal statuses are events: `end` optional;
a non-terminal interval starting after a terminal start is an error (a revived
programme is a new experiment id with lineage). Results appear iff
`lo(result.date) ≤ Y_hi`. The build precomputes per-entity
`state_segments: [[m0, m1, status, certainty], …]` (months since 1950-01) in
`atlas.json`; slider, range mode, playback and the history tests read only
that. Range mode: presence = union; colour = state with the longest clipped
duration; tooltip lists all segments. Optional `Interval.kind:
"lifecycle"|"run"|"phase"` (default lifecycle) and optional `Interval.specs`
(map of Q) for values that change per run (LHC energy per run).

**A4. Dates.** The Date object gains optional `earliest`, `latest`
(`earliest ≤ date ≤ latest`) and `display` (source wording, e.g. "Spring 2008",
"~2030"); seasons: date = middle month, earliest/latest = first/last month
(spring 03–05, summer 06–08, autumn 09–11, winter 12–02). `planned: true` means
"the source is a schedule or plan, not a report of an event" and stays true
after the date passes (UI: "was planned for 2030"). A future date without
`planned: true` is an error.

**A5. Memberships.** `memberships/<collab>.json` gains required file-level
`"membership_history": "unknown"|"partial"|"complete"` and optional
`"roster_snapshots": [{"as_of", "sources"}]`. Rows gain `known_since`,
`known_until` (earliest/latest *evidence* dates, never join dates). A row is a
solid, counted member at Y only when `[start,end]` or `[known_since,
known_until]` covers Y; for Y between collaboration formation and
`known_since` it is a hollow "undated member" excluded from counts (unless
`membership_history: complete`); after `as_of` and before the build date it is
hollow "not re-verified". Count wording: "N confirmed members (+M undated)".
The v0.1 rule "present from formation year" is withdrawn.

**A6. Ids and people.** Person ids are `person:inspire-<recid>` (file
`people/inspire-<recid>.json`) or `person:unresolved-<collab>-<institution>-<name>`
(scoped; never merged across collaborations). Every `person:inspire-*` carries
`identity_evidence: {"method": "orcid"|"collaboration_page_link"|"inspire_profile_affiliation_match"|"institution_page_link", "sources": []}`.
Any entity may carry `superseded_by: id|null`; references resolve through it.
`hep_graph` is build-derived only. `memberships[].role` is dropped from people
(career stage lives on `affiliations[].role`); collaboration-level roles live
in `collaboration.leadership[].role` ∈ {spokesperson, deputy_spokesperson,
physics_coordinator, technical_coordinator, ib_chair, other}.

**A7. Sources.** `rank` is derived from `source_type` (table in
HEP_ATLAS_SOURCES.md); `source_type` gains `geocoder`, `press_release`,
`project_document`, `wikipedia`, `wikidata`, `experiment_registry` (Greybook),
`inspire_record`. `type` field of a source file is `"src"`. The build warns on
two sources with the same normalised DOI/URL. `document.source_id` (optional)
and `result.publication_source_id` (optional) cross-link when the same DOI is
both a source and a document/publication.

**A8. Units added to §2.4:** `energy` += meV, µeV, PeV, EeV; `mass` += g, mg;
`time` += min, h; `magnetic_field` += mT, G; `area` (m^2, km^2, cm^2);
`electric_field` (V/cm, kV/cm, kV/m); `exposure` (kg d, kg yr, t yr, kt yr);
`fraction` (%, ""); `volume` += L; `current` (A, mA); `cross_section` (cm^2,
b, mb, µb, nb, pb, fb, zb); `rate` (Hz, kHz, MHz); `mass_energy` (eV/c^2,
keV/c^2, MeV/c^2, GeV/c^2, TeV/c^2); `luminosity` += nb^-1 s^-1, Hz/nb;
`angle` += rad, µrad, arcmin, arcsec; `count` unit "" only.

**A9. Shapes.** `SList<T>` = `[Sourced<T>]` for `physics_goals`,
`unique_capabilities`, `subsystems[].description`. `result.key_value: Q|null`
and `result.key_value_text: S string|null`. `site.depth_rock: Q(length)`,
`site.depth_mwe: Q(depth_mwe)`. `beamline.primary_beam: {"particle": string,
"energy": Q}`. `countries: []` on facility, site, institution. `result.announced`
and `result.published` optional Dates; `result.date` remains the display date
(earliest non-null). Any `*_ids` list entry may be either an id string or
`{"id", "start", "end", "sources"}` to give a relationship its own interval
(PS → ISR 1971–1984); otherwise the build uses `hull(A) ∩ hull(B)`.
`detector.technology_classes: []` (primary first) alongside the legacy scalar;
`noble_liquid_tpc` is preferred with `specs.target_medium` (S) and
`specs.phase` (S: "single-phase"/"dual-phase") — `lar_tpc`/`xenon_tpc`/
`argon_tpc` remain accepted aliases. `accelerator.is_collider: bool`.

**A10. Coverage and status.** Entity-level `coverage.validated` and
`globe_ready` are build outputs; `registry` rows keep planning fields only
(`entity_id`/`experiment_id`, `tier`, `priority`, `owner`, `researched`,
`missing_fields`, `notes`). Entity `status` must equal the derived state at
the build date, **except** where a terminal interval has already started by
that date: presence ends there, so the derived state is `None` and `status`
must instead equal that terminal interval's own status. A decommissioned
accelerator says `decommissioned`, not nothing.

**A11. Every data file may carry `"schema": "hep-atlas/0.2"`; the build adds
it if missing. Canonical formatting: `json.dumps(sort_keys=True, indent=2,
ensure_ascii=False)` + trailing newline.**

**A12. Additional validations (build-failing unless marked warn):** date
regex/calendar validity, year ∈ [1900, 2100]; `hi(end) < lo(start)` error;
non-terminal after terminal error; result (non-milestone) dated before every
listed experiment's earliest commissioning/active start error; result dated
after build date error; future date without `planned` error; `verified_at`
earlier than a non-planned date in the same value error; membership
`start`/`end` > `as_of` error; `known_since ≤ known_until ≤ as_of` error;
warn: hull gap ≥ 12 months, `active` before `construction`, experiment before
its facility's founding, experiment active while no listed accelerator/beamline
is active, membership `end: null` for a completed collaboration (clamped at
build), build date − `verified_at` > 18 months, `approx` on a day-precision
date, `planned` date passed without a non-planned interval, membership row
whose institution lacks coordinates (dot excluded, not a failure), two sources
sharing a normalised URL/DOI, derived fields present in data files.

**A13. Historical tests** assert derived state, not presence:
`state_at(id, "1990") -> None | {"status", "certainty"}`; e.g. ATLAS 1990 is
None, ATLAS 1994 status ∈ {proposed, approved}, Belle 1997 status ∉ {active,
commissioning}, ALEPH 2001 is None on the default layer, DUNE 2026 status ==
construction.

**A14. Bundles.** `atlas.json` carries stripped values (`value/unit/display`,
`status/start/end/label`, `state_segments`) — provenance (`sources`,
`verified_at`, `confidence`, `note`) for every field moves to a lazy
`provenance.json` keyed by entity id and field path. People are never in
`search.json`; people search is delegated to HEP Graph live search.
`people/<collab>/_unknown.json` holds rows with no institution.

**A15. Claim-level evidence (from the provenance review).** Every sourced
value, quantity, coordinate, interval, membership/affiliation/lineage/
leadership/placement row may carry `quote` (verbatim ≤ 300 chars seen in the
fetched content) and `locator` ("p. 12, Table 1.1", "§4.2", "section
'Institutions'"). One of them is **required** for: coordinates, `key_specs`
quantities, baselines, result `date`/`significance`/`result_type`, membership
rows with an `official_*` class, collaboration `formation`, and interval
bounds at day or month precision. The source-level `excerpt` stays optional.
`sources` (source id → citing paths) is derived at build into `sources.json`;
never authored.

**A16. Results.** `result.claim: {"quote": "...", "locator": "", "sources": [...]}`
is required and must come from the publication title/abstract or the
collaboration's own result page (never a press release, PDG or Wikipedia).
Mechanical check: `result_type: discovery` requires "discover" in
`claim.quote` or the cited source title; `observation` requires "observ";
`evidence` requires "evidence". `result.experiment_ids` rows may be objects
`{"id", "sources"}` when attribution needs its own source. `result.date_kind:
"announcement"|"preprint"|"publication"` is required.

**A17. No from-memory values on critical fields.** Rule 5 of the agent rules
is amended: a critical field is either sourced (non-empty `sources`) or
`null` with a `note`. `confidence: uncertain` still requires a source; it
means the source itself is weak or ambiguous. A `verified` value must cite at
least one source of rank ≤ 10; coordinates of `kind: detector|underground_lab`
may not rely solely on `geocoder` or rank ≥ 8 sources (geocoder coordinates are
`campus|headquarters` only).

**A18. Sources.** `accessed` is required. New optional fields: `retrieval:
"full_text"|"partial"|"summary"|"failed"` (a source with `failed` may not be
cited; a `quote` on a `summary` retrieval is an error), `archive_url`,
`content_hash` (filled by the link checker), `publisher_id` (the
collaboration/facility/institution that publishes it). Rank mapping
(derived): official_experiment_site 1, official_facility_site 2,
experiment_registry 3, inspire_experiment_record 3, design_report 4,
detector_paper 5, hepdata 6, pdg 7, institution_page 8, geocoder 8,
result_page 9, press_release 9, project_document 9, journal_article 10,
arxiv 10, inspire_literature_record 10, wikipedia 12, wikidata 12,
secondary 12. `inspire_record` is retired in favour of the two explicit types.

**A19. Evidence classes.** Add `inspire_author_profile` (INSPIRE author record
lists the collaboration) and `self_reported` (personal page/CV). Every
`publication_affiliation_*` row requires `evidence_date`; `_current` fails
when `as_of − evidence_date > 3 y`; `_historical` requires `end` or
`known_until`. `derived` is forbidden on person rows (institution rows only,
hollow). Precedence when several apply: official_roster >
official_institution_list > inspire_author_profile >
publication_affiliation_current > institutional_page > self_reported >
publication_affiliation_historical > derived. Source-type consistency:
`official_*` ⇒ a source of type official_experiment_site /
official_facility_site / experiment_registry; `publication_*` ⇒
journal_article / arxiv / inspire_literature_record / detector_paper /
design_report; `institutional_page` ⇒ institution_page. Counts labelled
"member institutions" include official_*, inspire_author_profile,
publication_affiliation_current and institutional_page only. Affiliation rows
on people carry `evidence_class` and `evidence_date` too. Per-row
`evidence_class` and `sources` are required in membership files
(`default_evidence_class` is removed; `roster_sources` is documentation).
UI wording: official_roster → "On the collaboration's own member list (as of
<as_of>)"; official_institution_list → "On the official institution list (as
of <as_of>)"; inspire_author_profile → "INSPIRE author profile lists this
collaboration"; publication_affiliation_current → "Listed with this affiliation
on a <collab> paper (<year>); current membership not confirmed";
publication_affiliation_historical → "Listed on a <collab> paper in <year>; may
no longer be a member"; institutional_page → "The institution's own page states
participation (checked <date>)"; self_reported → "Self-reported"; derived →
"Inferred, not verified".

**A20. Duplicate detection (validator).** Fail: two entities of one type share
any `external.*` id, DOI, arXiv id, INSPIRE recid or ORCID; normalised
name/alias collision within a type (lower-case, strip non-alphanumerics and a
leading "the") unless both records list each other in `distinct_from: [id]`;
two `src:` records with the same normalised URL or DOI; alias equal to own
name; duplicate aliases in one record; tier A/B experiment without
`external.inspire_experiment` and without a note. Warn: two sites of one
facility within 100 m; an unresolved person whose normalised name equals a
resolved person's. Every `external.*` id needs a record-level source whose URL
contains that id (inspirehep.net/institutions/<recid>, ror.org/<id>,
inspirehep.net/experiments/<recid>).

**A21. Geometry and plausibility (validator).** `beamline.baselines[].distance`
must agree with the great-circle distance between the two sites within 2 %
(fail). A detector site more than 50 km from its facility's primary site warns
unless the experiment kind is accelerator_neutrino, astrophysical_neutrino or
cosmic_ray. Spec-key → dimension whitelist from Appendix A is enforced; per-key
plausibility ranges (baseline 0.1–20 000 km; overburden 0–12 000 m / 0–15 000
m.w.e.; altitude −500–6 000 m; cms_energy 100 MeV–1 000 TeV; beam_power 1 kW–
10 MW; total_mass 1 kg–10⁹ t) fail outside range; the number parsed from
`display` must match `value` after unit conversion within a factor 10 (fail)
and 5 % (warn). An interval whose `start.planned` is true may not have status
active/commissioning/completed/decommissioned. `power` gains GW; `mass` gains
Mt; `rate` gains "/yr".

**A22. Record-level `sources` is required non-empty on every entity and covers
only identity claims** (name, aliases, kind, external ids, summary, links,
topic_ids, country, place). Everything else listed as critical is a sourced
value or sourced row. `hep_graph` is never authored. A source cited by nothing
warns. Link-check failures never fail the build; a 404/410 that is the sole
source of a `verified` value is listed as "review required".

**A23. Approximate detector placement (2026-09-17).** A site that holds a
detector placement should carry a `detector`/`underground_lab` point. When no
fetched source gives the hall position, the honest record is a `campus` point
with `confidence: approximate` (or `uncertain`) and a `note` saying what is
missing; the validator then warns (`coordinate-kind-approximate`) instead of
failing, the globe draws the approximate marker style and the panel says
"approximate location". Relabelling a campus-grade point as `detector` to
satisfy the validator is forbidden; `kind` describes what the coordinate is,
`confidence` describes how well it is known.

**A24. Technology classes (2026-09-17).** `technology_classes` gains
`helioscope`, `light_shining_through_wall`, `lumped_element_resonator`,
`cryogenic_phonon_detector`, `skipper_ccd`, `spherical_proportional_counter`,
`radiochemical` and `magnetic_spectrometer`, so axion, low-threshold
dark-matter, radiochemical solar-neutrino and direct neutrino-mass detectors no
longer have to file under `other`. `other` remains for anything else, with the
technique described in the sourced `technology` string.

**A25. Local-map geometry layer (2026-09-18).** Two entity types are added:
`map` (`data/atlas/maps/<facility-slug>.json`, id `map:<slug>`) and
`geometry` (`data/atlas/geometry/<slug>.json`, id `geometry:<slug>`). A map is
one to-scale local map of a facility campus: `facility_id`, `site_ids`,
`center` (Coordinates, any kind), `extent_m`, `levels[]` (`id`, `name`,
`kind` ∈ surface|underground|sea|lake|ice|mountain, sourced `depth_m`
positive downwards), `unlocated[]` (`entity_id`, sourced `reason`,
`backlog`), `schematics[]` (links only, "not to scale"), `linked_map_ids`.
A geometry record is one drawable feature: `map_id`, `level_id`,
`entity_id` (accelerator|beamline|detector|site|experiment|facility, or
null for context), `feature_type`, `geometry` = Sourced<GeoJSON geometry>
(`[lon, lat]`, WGS 84; Point/LineString/MultiLineString/Polygon/
MultiPolygon), `representation` ∈ surveyed|georeferenced|derived|
inferred_direction (no schematic class exists), `accuracy_m`, `method`,
`checks[]` (length/area/distance/azimuth/span against a sourced expected
Quantity, validator-executed, failure is an error), optional `valid`
{start,end}, `depth_m`, `license` (ODbL attribution for OpenStreetMap-derived
shapes), `osm` (element ids + timestamp), `site_id`. A `verified` shape
needs a rank ≤ 10 source and either `surveyed` representation or a passing
check citing such a source; OpenStreetMap alone (`source_type:
openstreetmap`, rank 11) gives at most `approximate`. A `derived` shape may
not rest on an anchor coarser than its own accuracy (no footprint from a
campus point). Every accelerator, beamline and detector-hosting site of a
mapped facility is either drawn or listed in `unlocated[]` (warning
otherwise). Build: `atlas.json.maps`, derived `facility.map_id`,
`site.map_id`, `{accelerator,beamline,detector}.geometry_map_ids`, and a
lazy `geometry/<slug>.json` per map. Full contract, validator rule table and
bundle shapes: `docs/HEP_ATLAS_GEOMETRY.md`.

**A26. Coverage of the whole field (2026-10-26).** The Atlas aims to cover
ground-based, underground and underwater experimental high-energy physics:
the energy, neutrino, rare-process and cosmic frontiers, with high-energy
nuclear physics where it shares facilities and methods. Space missions (no
fixed site) and gravitational-wave observatories stay out of scope. Added
`facility.kind` `astronomical_observatory` (CMB and dark-energy telescopes)
and `experiment.kind` values `cmb`, `dark_energy_survey`, `nucleon_decay`,
`hadron_structure`, `electroweak_precision` (parity violation and weak-charge
measurements), `antimatter` and `neutron_precision` (EDM, lifetime, decay
correlations).

**A27. Cosmic-ray muon flux underground (2026-10-26).** New quantity
dimension `muon_flux` with units `cm^-2 s^-1` (base), `m^-2 s^-1` and
`m^-2 d^-1` (a source quoting per hour or per year is converted, and the
conversion is said in `note`), and an optional site field
`site.muon_flux: Q(muon_flux)`. The value is the **total** flux of
cosmic-ray muons at the site: muons per unit area per unit time summed over
all arrival directions, as the cited source defines it (through a horizontal
surface, through the cross section of a sphere, or a detector's rate divided
by its acceptance over all angles). `note` says which, with the energy
threshold, the hall and the detector when the source gives them. Beam muons
never go here, and the vertical intensity (per steradian) is not a flux: it
appears only in `note`. The measurement's uncertainty goes in `display`,
written so the leading number is the value (`3.4 × 10⁻⁴ m⁻² s⁻¹ (± 0.1)`),
because the A21 display check reads the first number it finds and takes its
unit from the quantity unless `display` names a listed ASCII unit. A
simulated expectation is `approximate` and its `display` says "simulated".
The validator applies a plausibility range of 1e-11 to 5e-2 cm^-2 s^-1 (the
deepest laboratory to sea level) to the site field. The chart of depth
against flux reads `depth_mwe` and `muon_flux` and nothing else.

**A28. Guided tours (2026-10-26).** One entity type is added: `tour`
(`data/atlas/tours/<slug>.json`, id `tour:<slug>`). A tour is an authored walk
through the Atlas for a teaching player (docs/HEP_ATLAS_TEACHING_PLAN.md,
workstream 3). Top level: `name` (a working title), optional `order`,
`summary` (what the tour is, not a fact), `audience`, `estimated_minutes`
(1-60), `sources` (the sources its **own** claims cite) and `steps[]` (5-9).
A step has `id`, `title`, `text` (one or two plain sentences for a first-year
student), `claims[]`, and optionally `camera` `{lat, lng, altitude}` (globe
radii, 0.05-4), `year` (the timeline position, 1900 to the build year),
`select` (an entity id of a routable type: facility, experiment,
collaboration, institution, topic, result, document, site, detector,
accelerator, beamline, map), `map` (the slug of a local map), `view`
`{"name", "arg"}` (name from the fixed list `beam-section`, whose `arg` is a
beamline slug; otherwise unchecked), and `question`. **Every factual claim in
`text` is a claim.** A claim names the phrase it supports, `covers` (a
verbatim substring of the text), and is either an *own claim* (`quote`
verbatim and non-empty, `locator`, `sources`, `confidence`, `verified_at`;
the sourced-value rules of §2.1, A15 and A17 apply) or a *reference*
`{"covers", "ref": "experiment:t2k", "field": "key_specs.Baseline"}` to an
Atlas field that is already sourced. A path is dotted; a segment into a list
picks the row by `label`, `id`, `name` or `to_site_id` (or by index); a
`key_specs` row resolves to its quantity; the value must sit under a node with
non-empty `sources`, and a reference may not lean on a field whose sources are
all rank 11 or lower (encyclopaedias, OpenStreetMap). A tour does not cite the
entities it walks through: it is left out of `provenance.json` and the
sources' `cited_by`, and its evidence travels in `tours.json`. A question is
`{prompt, answer, claims[], calculation[]}`; a worked answer uses only numbers
the Atlas or a sourced constant carries, and `calculation` is a list of lines,
each an Atlas input (`ref` + `field` + `unit` for a quantity, or `number` for
a figure a record states in words or in its quote), a sourced constant
(`value` + quote) or a computed line (`expression` over earlier names with
`+ - * / **`, `pi`, `sqrt`, `asin`; `digits` significant digits; `value`),
which the validator evaluates.

Validator rules (`hepgraph/atlas/tours.py`, reported through `validate.py`;
errors unless marked warn): the entity or field a reference names does not
exist or is not sourced; a quote or locator is empty; a step has no text or
more than two sentences; a sentence contains no covered phrase (an answer
sentence that is arithmetic is covered by its calculation); a number in the
text, a prompt or an answer lies outside every covered phrase; a number in a
covered phrase does not agree with the number its reference resolves to
(unit-converted and rounded: "1.5 km" agrees with 1,478 m) or with its quote;
a calculation does not evaluate to the stated value at its stated digits, or
an answer never states the result; `select` is not a routable type or the
selection does not exist in the step's `year` (the timeline would hide it);
`map` is not a map slug; `view.name` is not in the list (warn: `beam-section`
names no beamline); a camera is out of range; a tour has fewer than 5 or more
than 9 steps or fewer than 2 or more than 3 questions; an own claim cites a
source the tour's `sources` does not list; warn: a claim covers under half of
a sentence, a reference rests on a field that is not `verified`, a listed
source no claim cites. Whether a quote supports its sentence is a reviewer's
judgement; `python -m hepgraph.atlas.tours review <slug>` prints each sentence
with its evidence, and `... tours fields <entity-id>` lists the fields a claim
may reference.

Build: `static/atlas/generated/tours.json` (lazy; one file) =
`{"schema", "build_date", "order": [tour ids], "tours": {id: {name, summary,
audience, estimated_minutes, sources (own plus every source a reference
resolves to), steps[]}}}`. Each step keeps its fields, with every reference
resolved in place (`value`, `sources`, and the carrying field's `quote`,
`locator`, `confidence`) and an `href`: the Atlas URL that shows the step,
`?y=<year>#/<type>/<slug>` for a selection, `?y=<year>&sel=<id>#/map/<slug>`
for a map, and `?y=<year>#/view/<name>/<arg>` for a view (the route `state.js`
does not yet read; a view beats a map beats a selection). The counts in the
manifest gain `tours`.

**A30. Accelerator chains (2026-10-26).** `accelerator.feeds_accelerator_ids[]`
entries are id strings or A9 objects `{id, start?, end?, sources, quote, locator,
confidence, verified_at, note}`; a link without dates holds for hull(A) ∩ hull(B).
In `atlas.json` the list mixes strings and `{"id": …}` objects, and consumers
accept both. `specs.beam_energy` is the highest energy the machine delivers
(extraction or design; per beam for a collider). The new spec key
`specs.injection_energy` (dimension `energy`) is the energy at which the machine
receives beam in its current configuration. Earlier eras live in `intervals[]`
entries of `kind: "phase"` with their own `specs`. A view at year Y takes the
`specs` of the latest-starting covering interval that has the key, else the
top-level value. Momenta are stored in GeV with the display in GeV/c and a note.
Contract and evidence: `docs/atlas-worklog/ACCELERATOR_CHAINS.md`.

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
| `tour:` | `tour:higgs-hunt` | A28: a guided tour; never referenced by another entity |

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
| `muon_flux` | cm^-2 s^-1, m^-2 s^-1, m^-2 d^-1 (A27) |
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
| `muon_flux` | **Q** `muon_flux` (A27): total cosmic-ray muon flux through a horizontal surface |
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
interval is an **event**: `end` is optional, and where given it may not precede
`start` (A3). (An earlier draft required an end here; it was withdrawn, because
the end of ALEPH's `completed` is not a fact anyone can source.)

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

Bundle budget: `atlas.json` + `manifest.json` ≤ 400 KB uncompressed was set
against the three-experiment pilot and is now a warning threshold rather than a
target; at 30 experiments the bundle is ~457 KB. The build still fails above
1.5 MB and prints per-type sizes, and the lazily loaded bundles (provenance,
sources, institutions, text, graph) are where growth is expected to land.

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
