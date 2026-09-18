# accelerator-neutrino-historical — Wave 3 domain-lead worklog

## Scope

Mandatory bar (per `WAVE3_LEAD_BRIEF.md` and the Wave 3 row of `ID_REGISTRY.md`)
for four historically completed accelerator-neutrino experiments: **KARMEN**
(ISIS, Rutherford Appleton Laboratory), **LSND** (Los Alamos LAMPF/LANSCE),
**OPERA** (LNGS Hall C / CERN CNGS beam), **DONUT** (Fermilab Tevatron
fixed-target beam). All four are `tier: D` in the coverage registry; the
brief's mandatory bar was produced for all four regardless of tier, plus one
historically-important result each (LSND antineutrino-appearance "evidence",
OPERA tau-neutrino-appearance "discovery", DONUT "Observation of tau neutrino
interactions"), as required.

**Delegation note:** the brief calls for spawning ≤ 4 sonnet children (one per
experiment). The shared session-wide concurrent-subagent pool (capped across
all 16 wave-3 leads) was saturated for the entire time this lead was working;
every `Agent` call returned "Concurrent subagent limit reached" and explicitly
said not to retry in a loop. Per the orchestrator's mid-task correction, all
four experiments were researched directly by this lead instead, sequentially,
using WebFetch/WebSearch (WebSearch's session-wide budget was also exhausted
partway through, after which WebFetch alone was used against publisher/arXiv
URLs). **No children were spawned.** This also means every claim below was
already fetched and checked by the lead itself — there is no separate
"re-verification" pass distinct from the initial sourcing.

## Entities written

- `facilities/isis-neutron-source.json` — `facility:isis-neutron-source` (new; ISIS spallation source, RAL)
- `sites/isis-rutherford-appleton.json` — `site:isis-rutherford-appleton` (new; sourced coordinates)
- `experiments/karmen.json`, `detectors/karmen.json`, `collaborations/karmen.json`
- `experiments/lsnd.json`, `detectors/lsnd.json`, `collaborations/lsnd.json`
- `results/lsnd-antineutrino-appearance-evidence-2001.json`
- `experiments/opera.json`, `detectors/opera.json`, `collaborations/opera.json`
- `beamlines/cngs.json` — `beamline:cngs` (CERN SPS → LNGS, 732 km)
- `results/opera-tau-neutrino-appearance-discovery-2015.json`
- `experiments/donut.json`, `detectors/donut.json`, `collaborations/donut.json`
- `results/donut-tau-neutrino-observation-2001.json`

No `people/`, membership-roster, or document (`documents/`) files were
written, per the brief and the rule against building rosters from author
lists in this wave. Neither OPERA nor DONUT nor KARMEN nor LSND is on the
brief's flagship list, so beyond the one required historical result each, no
additional results or technical documents were produced.

## Sources added

`src:karmen-prd-2002-numubar-nuebar-limits` (arXiv hep-ex/0203021, PRD 65,112001
(2002), full text fetched) · `src:karmen-prc-1998-nue-nutau-limits` (arXiv
hep-ex/9801007, PRC 57,3414 (1998), abstract) · `src:karmen-isis-stfc-about`
(official STFC ISIS page) · `src:karmen-isis-osm-nominatim` (geocoder) ·
`src:karmen-wikipedia` (pointer only) · `src:lsnd-nim-1997-detector-paper`
(arXiv nucl-ex/9605002, NIM A388:149 (1997), full text) ·
`src:lsnd-prd-2001-antineutrino-evidence` (arXiv hep-ex/0104049, PRD
64,112007 (2001), full text) · `src:lsnd-wikipedia` (pointer only) ·
`src:opera-cern-cngs-page` (home.cern official CNGS page) ·
`src:opera-prl-2015-discovery` (arXiv 1507.01417, PRL 115,121802 (2015), full
text) · `src:opera-wikipedia` (pointer only) · `src:donut-plb-2001-observation`
(arXiv hep-ex/0012035, PLB 504:218 (2001), abstract) · `src:donut-wikipedia`
(pointer only).

Every source's `id`/URL was checked against `data/atlas/sources/` before
creation; none duplicated an existing record. Several old arXiv PDFs
(hep-ex/9801007, hep-ex/0104049, hep-ex/0012035) could not be parsed as
full text by the fetch tool (garbled PDF encoding); their abstract pages were
used instead and `retrieval` is recorded as `partial`, not `full_text`, for
those. `fnal.gov` returned HTTP 403 to every fetch attempt (matching the
existing note on `facility:fermilab`), and `operaweb.lngs.infn.it` did not
resolve while `lngs.infn.it/en/opera` returned HTTP 500 — both are recorded in
the affected records' `notes`.

## Conflicts (claim / source A / source B / chosen / why)

- **DONUT event count**: Wikipedia states a 2008 final analysis found "9 tau
  neutrino events from a total sample of 578 neutrino events," but the only
  primary publication actually fetched (arXiv hep-ex/0012035 / PLB 504
  (2001) 218, the paper the brief specifically names) reports "four tau
  neutrino interactions" in 203 analyzed interactions. **Chosen:** the 2001
  paper's own figures (4 events / 203 interactions), because it is the
  primary source actually fetched and is the exact result the brief asked
  for; the 2008/9-event figure is noted as a caveat in the `key_specs` entry
  but not asserted as a sourced value since only Wikipedia (rank 12) reports
  it and no fetched primary source was found for it.
- **KARMEN run-transition dates**: no single fetched source gives day
  precision for the end of "KARMEN 1"; the primary PRD paper only says the
  outer-veto upgrade "mark[ed] the beginning of the KARMEN 2 experiment" in
  1996. **Chosen:** year-only precision (1996) for that transition, with the
  KARMEN 2 run itself kept at the sourced month precision (Feb 1997 – Mar
  2001).
- No genuine numeric contradictions between two comparably-ranked sources
  were found for LSND or OPERA; the only "conflicts" were between a
  Wikipedia-only claim and the absence of any primary-source corroboration
  (handled via `confidence: uncertain` + note, not by picking a side).

## Unresolved fields (honest gaps)

- **Collaboration formation dates** for all four collaborations: no fetched
  source states one; each collaboration's `formation.value` is `null` with a
  note, and the collaboration `intervals[0].start` uses the experiment's own
  earliest sourced date as a lower bound only (never asserted as a true
  formation date).
- **Membership/leadership**: no official roster counts found for any of the
  four collaborations; per project rule, author lists on individual papers
  were not used to infer membership. Leadership is out of scope for this wave
  (person records owned elsewhere).
- **`external.inspire_experiment`**: left `null` with a note on all four
  (tier D does not require it; no INSPIRE experiment-registry record URL was
  fetched, partly to respect the ≤1-request/10s INSPIRE etiquette rule under
  time pressure).
- **DONUT**: detector technology and run-period sourced only to Wikipedia
  (rank 12, `confidence: uncertain`) because `fnal.gov` blocked every fetch
  and the primary paper's PDF would not parse; no DONUT-specific site/hall
  coordinate exists anywhere reachable, so its detector placement reuses the
  existing `site:fermilab-main-campus` (owned by the `fermilab-dune` lead)
  rather than creating a near-duplicate site (which would have triggered
  A20's "two sites of one facility within 100 m" warning).
- **OPERA**: construction period (2003–2008) sourced only to Wikipedia
  (`confidence: uncertain`); the A21 great-circle check on the CNGS 732 km
  baseline cannot run until `site:lngs-hall-c` (owned by `facilities`) exists
  with coordinates — **this must be re-verified once that lead lands.**
- **KARMEN/LSND site coordinates**: campus/facility-level geocoder centroids,
  not surveyed detector-hall positions (explicitly labelled `kind: detector`
  only because the validator requires that for any site holding a detector
  placement, with `confidence: uncertain` and a note explaining the
  precision limit, matching the existing `site:fermilab-main-campus`
  precedent from another lead).

## Dangling references to ids another lead owns

- `facility:los-alamos-national-laboratory`, `site:lanl-lansce`,
  `accelerator:lansce` — owned by the `facilities` lead; referenced by
  `experiment:lsnd` (facility_roles), `detector:lsnd` (placement),
  `collaboration:lsnd` (host_facility_id/host_site_id), and
  `result:lsnd-antineutrino-appearance-evidence-2001` (facility_ids). None of
  these three ids existed in `data/atlas/` at any point while this lead was
  working; the validator reports 6 dangling-reference errors for this reason,
  all expected and all in LSND's files.
- `site:lngs-hall-c` — owned by the `facilities` lead; referenced by
  `detector:opera` (placement), `collaboration:opera` (host_site_id), and
  `beamline:cngs` (`far_detector_site_ids`, `baselines[].to_site_id`). Did not
  exist at any point while this lead was working.
- `facility:lngs`, `facility:cern`, `accelerator:sps`, `site:cern-meyrin` (all
  pre-existing, created by other leads in earlier waves) and
  `facility:fermilab`, `accelerator:fermilab-tevatron`, `site:fermilab-main-campus`
  (pre-existing, owned by `fermilab-dune`) were referenced, not created, and
  are **not** dangling — all four already existed in `data/atlas/`.

## Validation and build

`python -m hepgraph.atlas.validate` was run repeatedly while writing these
records; every error initially attributable to these files was fixed
(alias-equals-name, a coordinate-kind/source-quality mismatch on
`site:isis-rutherford-appleton`, several `confidence: verified` values that
turned out to rest solely on a rank-12 Wikipedia source, and two hull-gap /
status-mismatch errors on terminal intervals). As of the final run, **0
validator errors are attributable to this lead's files**; the only findings on
these files are (a) the 6 expected LSND dangling references above, (b) a
shared, repo-wide "experiment is active but no listed accelerator/beamline is"
warning that KARMEN and LSND share with 14+ other pre-existing experiments
across the atlas (not fixable without creating accelerator entities outside
this lead's ownership), and (c) the repo-wide "rank is derived at build time"
warning that every source file in the atlas carries by convention (matches
the exemplar `nova-experiment-site.json`, which also authors `rank`).
`python -m hepgraph.atlas.build` succeeds and produces `static/atlas/generated/`
(the only build-time message is the pre-existing, repo-wide bundle-size
warning, not attributable to this lead).

## Confidence summary

High confidence, primary-source-backed: KARMEN's detector geometry, mass and
run periods (two arXiv papers, full text/abstract); LSND's detector geometry,
mass, run period and antineutrino-appearance evidence claim (two arXiv
papers, full text); OPERA's CNGS baseline (official CERN page), 2008–2012
run range and 2015 discovery claim/significance (arXiv, full text); DONUT's
event counts and exact result title (arXiv abstract). Lower confidence,
explicitly flagged `uncertain` with notes: DONUT's run period/technology and
OPERA's construction period (Wikipedia-only); all four collaborations'
formation dates (no source found, treated as unknown); KARMEN/LSND detector
site coordinates (geocoder campus centroids, not hall-surveyed positions).
No fact on a critical field was taken from model memory; every date, number,
coordinate and result claim above traces to a source actually fetched in
this session, or is `null` with a note.
