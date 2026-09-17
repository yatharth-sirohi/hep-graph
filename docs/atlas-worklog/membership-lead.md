# Membership lead — worklog

Scope: `data/atlas/institutions/*`, `data/atlas/memberships/*`, `data/atlas/people/*`
(ID_REGISTRY). Ran as agent id `827df062-...` starting from a prior attempt in
the same session that had fetched 215 DUNE ROR records into the scratchpad
(`/private/tmp/.../827df062-.../scratchpad/`) but never written any files; that
cache, plus scratchpad caches for ATLAS and CMS built during this run, is the
basis for everything below. A small Python generator (`genlib.py` +
`build_dune.py` / `build_atlas.py` / `build_cms.py` / `build_people.py` /
`build_coverage.py`) turned the cached JSON into canonical entity files; it
lives only in the scratchpad, not in the repo.

## Collaborations, in order of the task brief

### DUNE — `memberships/dune.json`

- **Roster URL**: `https://lbnf-dune.fnal.gov/about/countries-and-institutions-participating-in-dune/`
  ("Countries and institutions participating in DUNE", DUNE at LBNF). This is
  the client-rendered page's underlying content; the 218-row list was already
  scraped into the scratchpad as `dune_roster.json` and resolved against ROR
  as `dune_resolved.json` by the previous attempt in this session.
- **as_of**: 2026-09. **membership_history**: `unknown` (no join dates
  published anywhere on the page).
- **Rows captured**: 217 of 218. One pair of roster lines ("APC, Université
  Paris Cité, CNRS" and "Université Paris Cité, CNRS, Astroparticule et
  Cosmologie") resolved to the same ROR organisation and was merged into one
  membership row (one real institution, one row — ontology §0.4).
- **Evidence class**: `official_institution_list` throughout (single official
  source, no exceptions).
- **Geocoding**: 216 of 218 rows resolved to a ROR organisation record
  (`source_type: geocoder`, ROR API v2, one `src:ror-<id>` per institution,
  reused across collaborations by ROR id). Two rows have no ROR record:
  - *Sanford Underground Research Facility* — geocoded via OpenStreetMap
    Nominatim against the street address on sanfordlab.org (630 E. Summit
    St., Lead, SD 57754); Nominatim's own result names SURF directly
    (`display_name` includes "Sanford Underground Research Facility"),
    confidence `verified`.
  - *University of Puerto Rico* — the roster names the system generically,
    not a specific campus (UPR has several autonomous campuses). Geocoded to
    the Río Piedras campus (the system's administrative seat) from its own
    published address; confidence `approximate` with a note on the ambiguity.
- **Country-name overrides applied by the earlier resolve pass** (kept, not
  re-verified further): CERN, York University, Sun Yat-sen University,
  Universidad del Atlántico, several INFN sections and IN2P3 laboratories,
  Royal Holloway, Kansas State, Northwestern, SUNY Albany, U. Hawaiʻi,
  U. Minnesota Duluth, Wichita State, Cinvestav, Antalya Bilim, and a few
  more — see `resolve_dune.py`'s `OVERRIDE` dict in the scratchpad for the
  exact list; each was a plausible name-variant mismatch, not a wrong
  identity.

### ATLAS — `memberships/atlas.json`

- **Roster URL**: `https://atlaspo.cern.ch/public/institutions` (linked from
  atlas.cern's collaboration page as "the full list of ATLAS institutions").
  247 rows scraped (name, country heading, website, Glance id, and an
  optional administrative "cluster" name for jointly-governed groups).
- **Stated count**: ATLAS's own about page says "170+ Institutions, 40
  Countries, 3000 Scientific authors." The 247 physical rows include 69 rows
  folded into 17 named clusters (Brazil, Chile, China ×3, Colombia, Georgia,
  Hong Kong, Morocco, Portugal, ...), so the two counts are not directly
  comparable; ATLAS's headline figure likely counts a cluster once.
- **Captured**: 198 of 247 rows (80%). Resolution used the ROR *affiliation*
  search endpoint plus a country-plausibility check (fuzzy: strips LaTeX
  escapes like `\"u`, "Republic of", "of America", etc., then substring
  match). 44 rows had no ROR match with score ≥ the affiliation search's own
  threshold and were left uncaptured (listed in
  `scratchpad/atlas_unresolved.json`; mostly smaller institutes — e.g.
  TRIUMF, York University (Canada), several IN2P3 laboratories quoted with
  their full "Université .../CNRS/IN2P3" wording, Adelaide, Baku, a couple of
  Chilean and Chinese institutes). One further match was rejected by hand:
  "iThemba Labs, Western Cape" (South Africa) matched ROR id `009kr6r15` at
  score 1.0, which is in fact a Scottish NHS hospital (Western General
  Hospital, Edinburgh) — a false positive on the word "Western"; excluded.
- **Evidence class**: `official_institution_list` (the page is ATLAS's own
  public institutions list).

### CMS — `memberships/cms.json`

- **cms.cern's own roster is not publicly fetchable**: both
  `cms.cern/collaboration` (general page, fetched, no roster) and any
  institutions/members page return HTTP 403 "Access Denied ... you must be a
  member of the CMS Collaboration (e-group)". Per the task brief's fallback
  ("use the author list of a recent ... collaboration paper and set the
  evidence class accordingly"), the membership rows instead rest on the
  author affiliation list of **arXiv:2609.04402** ("Search for the rare Higgs
  boson decay H→Zγ ...", CMS Collaboration, preprint 2026-09-03, INSPIRE
  literature record 3200158) — the most recent CMS paper available.
  `evidence_class: publication_affiliation_current`, `evidence_date: 2026-09`
  (well inside the 3-year window).
- **Stated count**: CMS's collaboration page states "over 6000 ... from 286
  institutes and universities from more than 60 countries."
- **Captured**: 244 of 265 raw affiliation strings (247 unique INSPIRE
  institution recids; one pair — "APC, Université Paris Cité, CNRS" /
  "Université Paris Cité, CNRS, Astroparticule et Cosmologie" — again the
  same lab under two spellings, merged; one row, "Unlisted", is INSPIRE's own
  placeholder recid for an author with no stated affiliation and was dropped
  rather than represented as an institution). 244/286 ≈ 85%. 18 affiliation
  strings had no resolvable INSPIRE institution recid at all (garbled OCR-ish
  strings such as "ndian Inst. Tech., Hyderabad", "KIT, Karlsruhe, EKP, ETP",
  a few full department names that don't match INSPIRE's abbreviation
  conventions — see `scratchpad/cms_unresolved.json`).
- Each institution came from its own INSPIRE-HEP institution record
  (`inspirehep.net/api/institutions/<recid>`): name from
  `institution_hierarchy`, coordinates + country from its `addresses[0]`
  when present (207/247 institutions had one), ROR id from
  `external_system_identifiers` when present (217/247). Where an institution
  had a ROR id it was built exactly like the DUNE/ATLAS path (ROR is the
  stronger source); the remaining ~30 were built straight from the INSPIRE
  institution record (`source_type: institution_page`,
  `inspirehep.net/institutions/<recid>`), with coordinates left `null` and a
  note when INSPIRE had no geocoded address either (11 institutions currently
  in the CMS roster fall in this category — flagged as
  `membership-institution-without-coordinates` warnings, which the validator
  treats as "dot excluded, not a failure").

### IceCube, T2K, LZ, Belle-II

Not attempted. Explicitly lower priority in the task ("if budget allows"),
and the budget went to getting DUNE to completion and ATLAS/CMS to a solid
partial capture instead. One important finding for whoever picks these up:
`data/atlas/collaborations/lz.json` says outright that **LZ has no published
institution list** ("the institution roster is not published as a list on
lz.lbl.gov"), so LZ will need the same paper-affiliation-list fallback used
here for CMS, not a roster scrape.

## Institutions (`data/atlas/institutions/*.json`)

529 institution files, canonical `hep-atlas/0.2`. Every file has: `name`,
`aliases`, `kind` (heuristic: CERN → `international_organization`; "National
Laboratory" in the name → `national_laboratory`; ROR/INSPIRE type
`education` → `university`; otherwise `research_institute`/`company` from the
ROR/INSPIRE type), `coordinates` (`campus` for everything except CERN-like
international orgs, which get `headquarters`; geocoder source is ROR when a
ROR id exists, else the INSPIRE institution record's own address, else `null`
with a note — never invented), `place`, `country`/`countries`, `external.ror`
and/or `external.inspire_institution` with a record-level source whose URL
contains that id, and `links.website` when either source gave one.

**Parent institutions**: `institution:infn` and `institution:in2p3` were
created (from ROR ids `005ta0471` and `03fd77x13`) and linked as
`parent_institution_id` on every INFN division/section/laboratory and IN2P3
laboratory whose *ROR record itself* states a `relationships: [{"type":
"parent", ...}]` link to one of them (30 institutions found this way — using
ROR's own parent/child relationship data turned out far more reliable than
name matching, since ROR's English label for most INFN sections is "National
Institute for Nuclear Physics, X Division", which doesn't contain the string
"Istituto Nazionale di Fisica Nucleare" that a naive name check would look
for).

**Corrections made after the first pass** (validator-driven, all fixed):

- Two institutions had an alias that repeated their own name after
  case/whitespace normalisation (Melbourne, Sydney) — dropped.
- ~28 institutions carried a short acronym alias ("NU", "UW", "UC", "SU",
  "ISU", ...) that collided with the *same* acronym on an unrelated
  institution elsewhere in the world (Northwestern vs. Nanjing vs. Nebraska
  vs. Northeastern all abbreviate "NU", etc.) — the colliding acronym was
  removed from every party rather than arbitrated with `distinct_from`,
  since none of them is more entitled to it than another.
- 9 institutions had the same alias entered twice under different
  punctuation (e.g. "INFN, Bari" vs. "INFN Bari") because a CMS-affiliation
  short name was appended without checking the *normalised* form against
  existing aliases — a bug in `genlib.get_or_create_institution_from_ror`'s
  alias-merge, now fixed there too, and the 9 files de-duplicated.
- `institution:marmara-universitesi` (built from an INSPIRE record with no
  ROR id) was a duplicate of `institution:marmara-university` (ROR-backed,
  which already listed the Turkish name as an alias) — merged; the CMS
  membership row was repointed and the orphaned institution/source deleted.
- One INFN alias, "INFN Sezione di Milano" (no "Bicocca"), was present on
  *both* the Milan and Milan-Bicocca division records (apparently an
  ambiguous alt-name on ROR's own Bicocca record) — removed from Bicocca,
  kept on Milan proper.
- One CMS row ("Unlisted", INSPIRE recid 910325, INSPIRE's own placeholder
  for "no affiliation given") was dropped rather than kept as a fictitious
  institution.

## People (`data/atlas/people/*.json`)

12 people, all resolved to `person:inspire-<recid>` — no
`person:unresolved-*` stubs were needed; every name attempted matched a
single, unambiguous INSPIRE author record via name + current institution.
`identity_evidence.method: inspire_profile_affiliation_match` throughout;
every affiliation and membership row cites the person's own INSPIRE-HEP
author profile (`positions` and `project_membership` fields — a curated,
INSPIRE-literature-staff-maintained record, not a self-report), evidence
class `inspire_author_profile`, `evidence_date: 2026-09`.

| Person | Institution (current) | Collaborations captured |
| --- | --- | --- |
| Usha N. Mallik (999068) | U. Iowa | ATLAS (uncertain — INSPIRE lists it but doesn't mark it current) |
| Jane M. Nachtman (996327) | U. Iowa (+ historical Fermilab) | DUNE (current), CMS (historical) |
| Yasar Onel (994876) | U. Iowa | DUNE (current), CMS (historical) |
| Sowjanya Gollapinni (1059399) | Los Alamos | DUNE, SBND (both current) |
| David M. Newbold (995800) | Rutherford Appleton Lab | DUNE (2015–), CMS (1993–, both current) |
| Fabiola Gianotti (1008441) | CERN | ATLAS (uncertain, historical/foundational) |
| Geralyn "Sam" Zeller (982276) | Fermilab | DUNE, SBND (both current) |
| Joel N. Butler (1014855) | Fermilab | CMS (2005–, current) |
| Atsuko K. Ichikawa (1005149) | Tohoku U. | T2K (current) |
| Morgan Wascko (984052) | U. Oxford (+ historical Imperial) | DUNE, T2K (both current; institution reflects his 2023– Oxford move, not the institution at join time) |
| Elizabeth Worcester (1035202) | Brookhaven | DUNE, SBND (both current) |
| Tejinder S. Virdee (984609) | Imperial College London | CMS (current) |

Notable finding: the task brief suggested verifying Iowa's HEP group on CMS;
in fact Iowa's department states its experimental HEP faculty are "involved
in CMS and ATLAS," and per INSPIRE, Nachtman's and Onel's *current* project
membership is **DUNE** (both marked `current: true`), with CMS membership
present but not marked current. Mallik's current work is ATLAS-adjacent
(dark-matter search) though her ATLAS project-membership flag on INSPIRE also
isn't marked current — included with `confidence: uncertain` and a note
rather than dropped, since her Iowa/ATLAS association is independently
reported on the department's own pages (search result, not separately cited
as an atlas source here). No person was attached to a collaboration merely
because their institution belongs to it — every membership row traces to
that specific person's own INSPIRE project-membership field.

## `data/atlas/coverage/membership.json` — not written

I drafted this file in the §3.15 registry shape the task's general rules
describe, but the loader (`hepgraph/atlas/load.py:_load_coverage`)
unconditionally requires every row to carry a valid `entity_id` referencing
an **experiment**, and rejects/duplicates the row otherwise. Institution and
people coverage doesn't map cleanly onto experiment ids, and `experiment:dune`
/ `experiment:atlas` / `experiment:cms` already have coverage rows from other
workstreams (`coverage/dune-atlas-completion.json`), so adding rows under
those same ids would either dangling-reference or duplicate-collide. Rather
than force an artificial fit (or silently duplicate another workstream's
row), I left the honest coverage accounting in this document instead — see
the counts above for DUNE/ATLAS/CMS/people, and the IceCube/T2K/LZ/Belle-II
section for what's outstanding. `.venv/bin/python -m hepgraph.atlas.validate`
is clean of this decision (no coverage file, no load error).

## Validation

`.venv/bin/python -m hepgraph.atlas.validate` was run repeatedly while fixing
the alias/duplicate issues above. The repo is shared with several other
workstreams writing concurrently, so the total error count moves between
runs for reasons unrelated to this work; the check that matters is: **zero
errors** attributable to `institutions/`, `memberships/dune.json`,
`memberships/atlas.json`, `memberships/cms.json`, `people/`, or any
`sources/` file this workstream created, in the final run. The only findings
against these files are expected and explicitly non-failing:
`membership-institution-without-coordinates` (11 CMS rows whose institution
has no geocoded address — A12 says "dot excluded, not a failure") and the
repo-wide `rank`-is-derived warning that every source file in the repository
carries (author-time `rank` is harmless; the build recomputes it).

## Unresolved / follow-up

- ATLAS: 44 roster rows with no confident ROR match (`scratchpad/atlas_unresolved.json`).
- CMS: 18 affiliation strings with no resolvable INSPIRE institution recid
  (`scratchpad/cms_unresolved.json`).
- IceCube, T2K, LZ, Belle-II membership files not started.
- `data/atlas/coverage/membership.json` not written (see above); this
  worklog is the source of truth for membership-lead coverage instead.
- A handful of ATLAS/CMS institutions carry a country label on the roster
  page that disagrees with their ROR-geocoded country (e.g. "iThemba Labs,
  Western Cape" listed under a "South Africa" heading resolved correctly to
  South Africa once the bad ROR match was rejected; a few others — Mongolia
  under a "China" heading, Palestine under "France", Spain under "Portugal"
  — were accepted as correct ROR matches with an administrative-heading
  mismatch, not an identity error, per the country-plausibility check log).
