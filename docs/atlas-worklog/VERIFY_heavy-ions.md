# Independent verification: heavy-ions (Wave 3)

Verifier scope: STAR, PHENIX, sPHENIX (experiments/detectors/collaborations,
their two 2005 "perfect liquid" white-paper results) plus the BNL facility
records they depend on (`facility:brookhaven-national-laboratory`,
`accelerator:rhic`, `accelerator:ags`, `site:bnl-upton-campus`,
`site:bnl-rhic-ip6-star`, `site:bnl-rhic-ip8-phenix-sphenix`) and every
`src:heavy-ions-*` / `src:bnl-*` source they cite. Did not trust the
researcher's worklog (`docs/atlas-worklog/heavy-ions.md`); re-fetched sources
independently.

## Records checked

- `data/atlas/experiments/{star,phenix,sphenix}.json`
- `data/atlas/detectors/{star,phenix,sphenix}.json`
- `data/atlas/collaborations/{star,phenix,sphenix}.json`
- `data/atlas/results/{star,phenix}-perfect-liquid-whitepaper-2005.json`
- `data/atlas/facilities/brookhaven-national-laboratory.json`
- `data/atlas/sites/{bnl-upton-campus,bnl-rhic-ip6-star,bnl-rhic-ip8-phenix-sphenix}.json`
- `data/atlas/accelerators/{rhic,ags}.json`
- All 16 `src:heavy-ions-*` sources and all 15 `src:bnl-*` sources
  (facility/RHIC/AGS/site sources cited by the above), 31 source records total.

## Values re-fetched: 15

Independently opened via WebFetch/WebSearch this session (not reused from the
worklog's claims):

1. `bnl.gov/rhic/star.php` — operational range, mass, membership counts, EIC link
2. `bnl.gov/rhic/sphenix.php` — status, mass, solenoid, lineage wording
3. `phenix.bnl.gov/experiment/concept.html` — formation/first-collision/end quotes
4. `bnl.gov/newsroom/news.php?a=122794` (final collisions) — date, wording
5. `bnl.gov/newsroom/news.php?a=122863` (EIC transformation) — detector fates
6. `bnl.gov/rhic/rhic25/` — timeline, first/final collision quotes
7. `bnl.gov/rhic/` — RHIC status wording
8. `arxiv.org/abs/nucl-ex/0501009` (STAR white paper) — title, date, wording
9. `arxiv.org/abs/nucl-ex/0410003` (PHENIX white paper) — title, date, wording
10. `arxiv.org/abs/nucl-ex/0301015` (STAR TPC paper) — dimensions quote
11. `inspirehep.net/api/experiments/1108784` (STAR) — recid
12. `inspirehep.net/api/experiments/1108852` (PHENIX) — recid
13. `inspirehep.net/api/experiments/1500624` (sPHENIX) — recid
14. `osti.gov/biblio/2338139` (sPHENIX construction/commissioning) — dates
15. `phys.org/news/2025-07-physics-results-sphenix-particle-detector.html` — date, wording
16. `bnl.gov/newsroom/news.php?a=26793` (sPHENIX CD-0) — date, quote

WebSearch used once, to look for a surveyed STAR/PHENIX interaction-point
coordinate (none found; existing campus-grade point stands, see finding 3).

## Findings

| # | Severity | Item | Description | Resolution |
|---|----------|------|--------------|------------|
| 1 | — (no defect) | Status: STAR/sPHENIX `completed` vs EIC conversion | Fetched `bnl.gov/newsroom/news.php?a=122863` ("Transformation of RHIC to EIC Begins"): STAR "will be disassembled and removed" (hall reused for the ePIC detector); sPHENIX mostly removed, one calorimeter reused. BNL's own copy calls it having "completed its 25th and final run." This is a genuine dismantling, not a temporary pause — `shutdown` (defined as temporary, e.g. an LHC long shutdown) would be wrong; `completed` is BNL's own word and matches the atlas-wide convention (LEP `decommissioned` but its experiments ALEPH/DELPHI/L3/OPAL all `completed`; same pattern used here and on `accelerator:rhic`, which is `decommissioned`-eligible but also recorded `completed` for the same A10 reason). No change needed. |
| 2 | P1 | `collaboration:phenix` interval collapsed | The single interval ran `1991-08 → null, status: completed`, meaning the derived per-year state for **every year from 1991 to 2026** — including 2005, 2010, when PHENIX was actively colliding beams — was `completed`. That is a false historical claim (contradicts `experiment:phenix`/`detector:phenix`'s own correctly-staged `active` 2000–2016 interval) and violates ontology §3.5 / RESEARCH_AGENT_RULES rule 8 ("must not collapse to one row when richer information exists"). **Fixed**: split into `active` (1991-08 → 2016) and `completed` (2016 → null), mirroring the experiment/detector staging. Re-validated: no new warnings, canonical JSON preserved. |
| 3 | — (already compliant) | BNL interaction-point site coordinates | Brief's premise ("carry campus-grade coordinates labelled `kind: detector` with confidence `uncertain`") does not match the files as found: both `site:bnl-rhic-ip6-star` and `site:bnl-rhic-ip8-phenix-sphenix` are already `kind: campus`, `confidence: approximate`, with a detailed note explaining the missing hall-level source (A23-compliant). Attempted a fresh WebSearch for a surveyed IP6/IP8 coordinate; found only "Building 510" / "6 o'clock position" prose, no lat/lon. Left as-is — already the honest record A23 calls for. |
| 4 | P2 | `src:bnl-rhic-phenix-wikipedia` uncited | Cited only in a coordinate `note` (prose), never in a `sources` array, triggering the `uncited-source` validator warning. It genuinely was used for corroboration (its 1.6 km-off infobox coordinate supports the campus-grade estimate). **Fixed**: added it to the top-level `sources` array of both IP6 and IP8 site files. Re-validated: warning gone. |
| 5 | — (verified correct) | PHENIX formation 1991-08, first collision 2000-06-15, end 2016 | All three verbatim-quoted and independently re-fetched from `phenix.bnl.gov/experiment/concept.html`; match exactly. |
| 6 | — (verified correct) | sPHENIX construction complete April 2023, first Au+Au 2023, lineage `upgrade_of` PHENIX | Re-fetched OSTI 2338139 abstract and BNL sPHENIX page; quotes match verbatim. Lineage `upgrade_of` is written only on `experiment:sphenix` (canonical direction, A1); `experiment:phenix` correctly has no reciprocal `successor` row. |
| 7 | — (verified correct) | STAR TPC "4 m × 4.2 m" | Re-fetched arXiv:nucl-ex/0301015 abstract; quote matches verbatim, plus pseudorapidity coverage (\|η\|<1.8). |
| 8 | — (verified correct) | Two 2005 white-paper results | Re-fetched both arXiv abstracts. Titles, arXiv ids, journal refs (Nucl. Phys. A757, 102-183 and 184-283) all match. Neither claim.quote nor summary uses "discovery"; STAR's own abstract explicitly hedges against "evidence"; `result_type: measurement` on both is correct and non-inflated. `date_kind: publication`, value `"2005"` matches the journal year. |
| 9 | — (verified correct) | RHIC energies/geometry/dates | 200 GeV Au+Au and 500 GeV polarised p+p (Run 22 press release, re-fetched), 3.86 km circumference (2.4 mi conversion, re-fetched), construction start 1991, first collisions 2000-06-12 (re-fetched, distinct from — and consistent with — PHENIX's own first-recorded-collision three days later on 2000-06-15), final beams 2026-02-06: all confirmed against source text. AGS 33 GeV / July 1960: confirmed. |
| 10 | — (checked, no issue) | INSPIRE recids | STAR 1108784, PHENIX 1108852, sPHENIX 1500624 all confirmed via `inspirehep.net/api/experiments/<id>` (legacy_name/long_name match). |
| 11 | — (checked, no issue) | Duplicates | Grepped all of `data/atlas/` for STAR/PHENIX/sPHENIX names and for every cited source URL/DOI: no duplicate entities, no duplicate source URLs anywhere in the atlas. |
| 12 | — (checked, no issue) | Canonical formatting | All 45 files in scope (experiments, detectors, collaborations, results, facility, sites, accelerators, all cited sources) already matched `json.dumps(sort_keys=True, indent=2, ensure_ascii=False)` + trailing newline, both before and after my two edits. |
| 13 | — (out of my scope, noted only) | `data/atlas/coverage/heavy-ions.json` missing_fields text still says the two BNL sites are "dangling" | They are no longer dangling (facilities lead landed them, A23-compliant). Coverage files are not in this verification's file list, so left untouched; noting for whoever next edits that file. |

## Fixes made (2 files edited, both re-validated and re-canonicalized)

1. `data/atlas/collaborations/phenix.json` — split the collapsed
   1991–present `completed` interval into `active` (1991-08 → 2016) +
   `completed` (2016 → null). This was the only substantive scientific/status
   defect found.
2. `data/atlas/sites/bnl-rhic-ip6-star.json` and
   `data/atlas/sites/bnl-rhic-ip8-phenix-sphenix.json` — added
   `src:bnl-rhic-phenix-wikipedia` to the record-level `sources` array
   (it was already relied on in the coordinate note but not formally cited).

No other files were modified.

## Unverifiable / left as-is

- STAR and sPHENIX collaboration formation dates (`null`): no source found
  this session either; the researcher's A17 reasoning for leaving them
  unsourced still holds.
- PHENIX/sPHENIX detector-level numeric specs (arm acceptance, magnet T·m,
  STAR magnet field): re-attempted none of these fetches (same paywalled/403
  primary papers the researcher hit); left omitted, correctly, rather than
  guessed.
- Exact STAR/PHENIX interaction-point geodetic coordinates: one fresh
  WebSearch attempt found no usable lat/lon; campus-grade approximate point
  stands (finding 3).

## Validator

`.venv/bin/python -m hepgraph.atlas.validate` (run after both fixes): the
repository-wide count fluctuates run to run because other wave-3 sessions
are editing the same shared worktree concurrently (per CLAUDE.md), but a
per-line scan of the output for every finding touching `star`, `phenix`,
`rhic`, `brookhaven`, `ags`, or a `bnl-*` file shows **zero `[error]`-level
findings** in any run. The only remaining findings touching this workstream's
files are warnings that are either intentional/honest by design
(`coordinate-kind-approximate` per A23, `hull-gap` for sPHENIX's two
documented sourcing gaps, `interval-start-unknown` for undocumented start
dates, `sites-too-close` as a direct consequence of three BNL sites sharing
one campus-grade coordinate) or pre-existing and out of this workstream's
ownership (`derived-field` warnings on `rank`, which the schema computes at
build time regardless of what's written).

## Verdict

**Pass, with one P1 fix applied.** The heavy-ions researcher's factual claims
(dates, quantities, quotes, INSPIRE ids, result wording) held up against
independent re-fetching of all 16 cited sources plus fresh checks of the
INSPIRE API and BNL's current EIC-transformation announcement. The one real
defect was a modeling error, not a factual one: `collaboration:phenix`'s
history was collapsed into a single interval that implied the collaboration
was "completed" for the 25 years it was actually active, fixed to mirror the
correctly-staged experiment/detector records. The BNL interaction-point site
coordinates that the verification brief flagged as a likely A23 violation
were, on inspection, already compliant — no fix was needed or made there
beyond citing an already-used corroborating source.
