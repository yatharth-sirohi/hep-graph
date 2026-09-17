# historic-cern research log

## Scope

UA1 and UA2 at CERN's SPS proton-antiproton collider (1981-1990), and the
four LEP experiments ALEPH, DELPHI, L3 and OPAL (1989-2000): experiments,
detectors, collaborations, five new sites, seven results (the 1983 W/Z
discovery papers, the 1989 three-neutrino-species determination, the 2006
LEP electroweak combination, and the 2003 LEP Higgs exclusion limit), and
four LEP detector-paper documents.

A previous agent in this workstream had fetched and recorded 27 source
stubs under `data/atlas/sources/` (ua1-*, ua2-*, aleph-*, delphi-*, l3-*,
opal-*, lep-*) but had not yet written any entity files. This session
re-fetched every one of those pages (plus several new ones) to pull the
actual quotes needed for sourced values, reused all 27 existing source
ids (updating `accessed` to 2026-09-17), and added 6 new source records
(3 OpenStreetMap/Nominatim geocoder lookups for LEP Points 2/4/8, one CERN
Courier article on the ALICE/L3 magnet, and two INSPIRE literature-search
records for the LEP detector papers and the 1989 neutrino-counting papers).

## Entities written

Experiments: `experiment:ua1`, `experiment:ua2`, `experiment:aleph`,
`experiment:delphi`, `experiment:l3`, `experiment:opal`.

Detectors: `detector:ua1`, `detector:ua2`, `detector:aleph`,
`detector:delphi`, `detector:l3`, `detector:opal`.

Collaborations: `collaboration:ua1`, `collaboration:ua2`,
`collaboration:aleph`, `collaboration:delphi`, `collaboration:l3`,
`collaboration:opal`.

Sites: `site:cern-sps-lss5-ua1`, `site:cern-sps-lss4-ua2`,
`site:cern-lep-point-4-aleph`, `site:cern-lep-point-8-delphi`,
`site:cern-lep-point-2-l3`. No site was written for OPAL (see Unresolved).

Results: `result:ua1-w-boson-observation-1983`,
`result:ua2-w-boson-observation-1983`, `result:ua1-z-boson-observation-1983`,
`result:ua2-z-boson-evidence-1983`, `result:lep-three-neutrino-species-1989`,
`result:lep-electroweak-precision-2006`, `result:lep-higgs-exclusion-2003`.

Documents: `document:aleph-detector-nim-1990`,
`document:delphi-detector-nim-1991`, `document:l3-detector-nim-1990`,
`document:opal-detector-nim-1991` (the four LEP NIM detector papers). The
original UA1/UA2 SPSC proposals were **not** written as documents; see
Unresolved fields.

Coverage: `data/atlas/coverage/historic-cern.json` (six rows).

## Sources added (new, this session)

`src:lep-point-2-osm-nominatim`, `src:lep-point-4-osm-nominatim`,
`src:lep-point-8-osm-nominatim`, `src:lep-cern-courier-l3-magnet-alice`,
`src:lep-inspire-detector-papers`, `src:lep-inspire-neutrino-species-1989`.

27 pre-existing source stubs were re-fetched and reused (accessed date
updated to 2026-09-17): all `ua1-*`, `ua2-*`, `aleph-*`, `delphi-*`,
`l3-*`, `opal-*` and most `lep-*` sources already present in
`data/atlas/sources/`.

## Conflicts

| claim | source A | source B | chosen | why |
| --- | --- | --- | --- | --- |
| UA1/UA2 collision energy | UA1 W/Z papers: "540 GeV" (1983) | INSPIRE UA1/UA2 experiment records' own long_name: "630 GeV" | both recorded | The SppS ran at 540 GeV in 1983 and later at up to 630 GeV; `energy_regime` records the range and cites both. |
| UA2 upgrade window | Task brief suggested "1987-1988" | CERN archives guide (src:ua2-cern-archives-guide): "Between 1985 and 1987, the UA2 detector was upgraded" | 1985-1987 (sourced) | Never invent a date to match a hint; the fetched CERN source is authoritative. |
| UA2 data-taking start | home.cern: "first collisions in December 1981" | INSPIRE experiment record 1109640: `date_started` "1981-11" | 1981-11 (INSPIRE) | INSPIRE gives month precision from a rank-3 experiment-registry field; home.cern's "December 1981" is recorded in a note as the narrative variant. |
| UA1 "project began" date | CERN archives guide: "The UA1 project began in 1976" | INSPIRE `date_proposed`: "1978-01-30" | both recorded, 1978 used as the proposal interval | 1976 reads as an idea/design-phase date, not a formal proposal; noted as context rather than used as a status interval start. |
| DELPHI end-of-data-taking date | home.cern DELPHI page: "In December 2000, DELPHI stopped taking data" | L3/OPAL pages and the general LEP shutdown: "2 November 2000" / "November 2000"; INSPIRE DELPHI `date_completed`: "2000" (year only) | 2000-12 (home.cern, DELPHI-specific) | DELPHI's own page is the most specific DELPHI-labelled source; the one-month discrepancy with the LEP-wide shutdown date is recorded rather than silently reconciled. |
| OPAL name expansion | INSPIRE: "OPAL: Omni Purpose Apparatus for LEP" | OPAL's own site: "an Omni-Purpose Apparatus at LEP" | both kept as aliases | Minor wording difference ("for" vs "at"); no reason to prefer one, both sourced. |
| "Number of light neutrino species" value | Four separate Oct 1989 papers (ALEPH 3.27+/-0.30, L3 3.42+/-0.48, DELPHI 2.4+/-0.4(stat)+/-0.5(syst), OPAL 3.1+/-0.4) | 2006 combination: 2.9840+/-0.0082 | 2006 value used as `key_value` on the 1989-dated result, with the four 1989 numbers recorded in `key_value_text`/notes | The task asked for a "determination that there are three light neutrino species" as one entity; the precise number only exists at 2006 precision, so the best-available figure is used with full attribution and the historical papers dated the claim itself. |

## Unresolved fields

- **UA1/UA2 SPS hall (LSS5 vs LSS4).** No fetched source (home.cern, the
  CERN archives guide for either experiment) states the Long Straight
  Section number explicitly; both archives-guide pages were checked
  specifically for "LSS"/"Long Straight Section"/"Point 4"/"Point 5"
  wording and found none. The site ids follow the pre-existing
  `ID_REGISTRY.md` reservation (`site:cern-sps-lss5-ua1`,
  `site:cern-sps-lss4-ua2`), but the assignment itself is unverified in
  this session; coordinates are `approximate_region` anchored on the CERN
  Meyrin site with `precision_m: 3000` and `confidence: "uncertain"`.
- **OPAL's LEP interaction point.** ALEPH (Point 4), DELPHI (Point 8) and
  L3 (Point 2) are each sourced (directly for ALEPH; by inference through
  the DELPHI/LHCb and L3/ALICE shared-cavern stories for the other two).
  No fetched source states OPAL's point number. By elimination among the
  ring's four instrumented points it would be Point 6, but per this
  workstream's rules that inference is not written: `experiment:opal` and
  `detector:opal` carry no site/placement, and this gap is recorded in
  their notes and in the coverage row's `missing_fields`.
- **UA1 and UA2 original SPSC proposals.** Not found as INSPIRE literature
  records (title/report-number searches returned nothing); CERN Document
  Server pages were blocked by bot protection (Anubis) in this session.
  No `document:` entity was written for either proposal.
- **UA1/UA2 collaboration sizes.** No official institution/member/country
  count was located for UA1 in any fetched source; `collaboration:ua1`
  therefore omits `membership`. UA2's CERN archives guide names 12
  institutions (used as `institution_count`), but gives no physicist
  headcount or country count.
- **Leadership/spokesperson names** for ALEPH, DELPHI, L3, OPAL and UA1
  were not sourced in this session (UA2's spokesmen, Pierre Darriulat and
  Luigi Di Lella, were sourced and are recorded with `person_id: null`,
  since person records belong to the membership-lead workstream).
- **Detector NIM-paper full text** (numeric specs for L3/OPAL magnet
  fields, subdetector dimensions) was not fetched beyond titles/abstracts;
  only the home.cern-sourced qualitative descriptions are recorded for
  those two detectors' `specs`.

## Children spawned

None. Per this session's explicit working instructions ("Do NOT spawn
child agents"), all research and writing was done directly by this agent;
rule 10 of `RESEARCH_AGENT_RULES.md` (delegate to child agents) was
overridden by that instruction.

## Confidence summary

Proposal/approval/data-taking/completion dates for all six experiments are
`verified`, sourced to INSPIRE experiment records (rank 3) and/or official
CERN pages (rank 2), with quotes or locators. The four 1983 W/Z discovery
results and the three LEP-wide results are `verified` against INSPIRE
literature records and arXiv abstracts. Site coordinates for the five new
sites are `approximate` (LEP points, geocoder-based, matching the existing
`site:cern-point-1-atlas` convention) or `uncertain` (UA1/UA2, SPS-ring
level only) and are flagged "REVIEW REQUIRED" in their own notes, per A17.
Collaboration membership counts are `approximate` where sourced at all.
