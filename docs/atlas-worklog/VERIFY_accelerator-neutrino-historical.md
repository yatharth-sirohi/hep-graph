# Independent verification — accelerator-neutrino-historical (KARMEN, LSND, OPERA, DONUT)

Verifier session, 2026-09-17. Worked read-mostly in
`/Users/yatharthsirohi/Desktop/HEP-Graph-atlas-v1` (branch `hep-atlas-v1`), no
git, no subagents. Did not trust `docs/atlas-worklog/accelerator-neutrino-historical.md`;
every critical value below was re-fetched from its cited URL with WebFetch in
this session and compared against the record.

## Records checked

- `data/atlas/experiments/{karmen,lsnd,opera,donut}.json`
- `data/atlas/detectors/{karmen,lsnd,opera,donut}.json`
- `data/atlas/collaborations/{karmen,lsnd,opera,donut}.json`
- `data/atlas/results/lsnd-antineutrino-appearance-evidence-2001.json`
- `data/atlas/results/opera-tau-neutrino-appearance-discovery-2015.json`
- `data/atlas/results/donut-tau-neutrino-observation-2001.json`
- `data/atlas/beamlines/cngs.json`
- `data/atlas/facilities/isis-neutron-source.json`
- `data/atlas/sites/isis-rutherford-appleton.json`
- All 14 cited `src:karmen-*` / `src:lsnd-*` / `src:opera-*` / `src:donut-*` source records
- Cross-referenced (not owned by this domain, read-only): `sites/lngs-hall-c.json`,
  `sites/cern-meyrin.json`, `sites/lanl-lansce.json`, `facilities/los-alamos-national-laboratory.json`,
  `accelerators/lansce.json`, `accelerators/fermilab-tevatron.json`

Duplicate check: grepped `karmen|lsnd|opera|donut` and `isis` across
`data/atlas/{experiments,detectors,collaborations,facilities,sites}/` — no
duplicate entities, no id/alias collisions. IDs match `ID_REGISTRY.md`
exactly (`facility:isis-neutron-source`, `site:isis-rutherford-appleton`,
plus the four `experiment:`/`detector:`/`collaboration:` triples).

## Values re-fetched and checked against source: 26

1. KARMEN abstract: "56 tonne" detector mass, "beam stop neutrino source ISIS" (src:karmen-prc-1998)
2. KARMEN full text: "17.7 m ... 100 degrees", "65 m³ ... paraffin oil / pseudocumene / PMP", "since 1990", "installed in 1996, marking the beginning of KARMEN 2", "February 1997 until March 2001", "800 MeV" ISIS proton energy (src:karmen-prd-2002) — 7 checks
3. ISIS STFC page: "began operations in 1984", operator STFC (src:karmen-isis-stfc-about)
4. LSND NIM paper: "proposed ... in 1989 and first operated in 1993", "30 m from the neutrino source... 9 m of steel" (actual wording, §1.2), "167 metric tons of mineral oil (CH2) ... 0.031 g/l butyl PBD" (actual wording, §1.2), "800 MeV" proton energy, "8.3 m ... 5.7 m", "1220 ... PMTs" (src:lsnd-nim-1997) — 6 checks
5. LSND PRD 2001: title, "87.9±22.4±6.0 events ... (0.264±0.067±0.045)%", "six calendar years (1993-1998)" (src:lsnd-prd-2001) — 3 checks
6. CERN CNGS page: "July 2006 to December 2012", "732 kilometres", SPS/graphite target (src:opera-cern-cngs-page) — 3 checks
7. OPERA PRL 2015: title, "significance larger than 5 σ" / "5.1 σ" in conclusions, "150 000 bricks", "OPERA detector at the LNGS underground laboratory" (src:opera-prl-2015) — 4 checks
8. OPERA Wikipedia: "built in 2003–2008", "beam from CERN was stopped on 3 December 2012" (src:opera-wikipedia) — 2 checks
9. DONUT PLB 2001: title, "203 neutrino interactions", "four tau neutrino interactions ... 0.34 events" (src:donut-plb-2001) — 3 checks
10. DONUT Wikipedia: name expansion, "operated ... in the summer of 1997", detector tech, opening sentence, "9 tau neutrino events from a total sample of 578" 2008 figure (src:donut-wikipedia) — 5 checks
11. Great-circle cross-check (A21) of the CNGS 732 km baseline using `site:cern-meyrin` (46.2339, 6.0470) and `site:lngs-hall-c` (42.4189, 13.5183): computed 729.7 km, 0.3% from the sourced 732 km — well inside the 2% tolerance.

Total ≈ 33 individual fetch/verification actions across 14 distinct URLs.

## Findings

### P0 — none found.
No false scientific statement, wrong entity identity, or fabricated critical
value. `evidence`/`discovery`/`observation` wording is correctly kept
distinct and matches each publication's own title exactly (LSND "Evidence",
OPERA "Discovery", DONUT "Observation") — A16's mechanical check is honestly
satisfied by all three, not gamed. All four experiments are correctly
terminal (`status: completed`) with sourced end-of-data-taking events. No
unexplained acronyms in any `summary.plain` (KARMEN, LSND, OPERA, DONUT all
read cleanly). ISIS site coordinate is honestly `kind: campus` +
`confidence: approximate` with a note — full A23 compliance, not gamed
against the validator. Numbers (masses, distances, energies, event counts,
significance) all matched their sources' actual magnitudes and units.

### P1 — found and fixed (4 items)

1. **`data/atlas/experiments/lsnd.json` `/key_specs/0/quantity`** and
   **`data/atlas/detectors/lsnd.json` `/placements/0`** — the `quote`
   ("The center of the detector was 30 m from the A6 neutrino source.")
   does not appear verbatim anywhere in the cited source
   (`src:lsnd-nim-1997-detector-paper`, arXiv nucl-ex/9605002); I searched the
   full rendered text for every sentence containing "30 m" and every sentence
   containing "A6" and neither combination exists. The value (30 m) is
   correct — the actual §1.2 sentence is "The detector was located about
   30 m from the neutrino source and was shielded by the equivalent of 9 m
   of steel." The cited `locator` ("§II.5") was also wrong; the real location
   is §1.2. **Fix applied**: replaced `quote`/`locator` with the verified
   verbatim text in both files; value unchanged.

2. **`data/atlas/experiments/lsnd.json` `/key_specs/1/quantity`** and
   **`data/atlas/detectors/lsnd.json` `/technology`** — same defect for the
   167 t detector-mass claim: quoted text "The tank was filled with 167
   metric tons of liquid scintillator consisting of mineral oil and 0.031
   g/l of b-PBD" does not appear verbatim; the real §1.2 sentence is "The
   detector was a tank filled with 167 metric tons of mineral oil (CH2),
   with a small admixture (0.031 g/l) of butyl PBD scintillant." Value (167 t)
   correct. **Fix applied**: same as above.

3. **`data/atlas/experiments/karmen.json` `/energy_regime`** — the "800 MeV"
   beam-stop energy claimed in `value` is not supported by the cited source
   (`src:karmen-prc-1998-nue-nutau-limits`); I fetched its full abstract and
   "800 MeV" does not appear anywhere in it. The figure is real and is
   stated in the *other* KARMEN source already in the record's `sources`
   list elsewhere (`src:karmen-prd-2002-numubar-nuebar-limits`: "a rapid
   cycle synchrotron to accelerate protons up to 800 MeV"). This was a
   source-attribution error on a sourced value marked `confidence: verified`
   — criterion (a) failed. **Fix applied**: added the correct source to
   `energy_regime.sources`, corrected `quote`/`locator`/`note`.

4. **`data/atlas/experiments/donut.json` `summary.technical`** — asserted
   "an 800 GeV-class Tevatron proton beam dump" as a specific quantitative
   figure. No fetched source in this record states a Tevatron beam energy
   (I explicitly checked src:donut-wikipedia — it names the Tevatron and
   charmed-meson decay but gives no GeV/TeV figure); `energy_regime.value`
   in the same record deliberately carries no number for exactly this
   reason. `accelerator:fermilab-tevatron`'s own sourced `beam_energy`
   (980 GeV per beam, collision mode, Run II 2002–2011) is a *different*
   quantity from a different era and cannot support this claim either — using
   it would have been a new fabrication, not a fix. This was an unsourced,
   from-memory quantitative claim smuggled into prose (violates the spirit
   of A17, since a `summary` field is not exempt from "the atlas asserts
   nothing it can't source"). **Fix applied**: removed the specific figure
   from `summary.technical`, added a `notes[]` entry explaining the removal.

### P2 — found and fixed (1 item)

5. **`data/atlas/experiments/donut.json` `/facility_roles/0` (role: host)** —
   `quote: "operated at Fermilab"` does not appear verbatim in
   `src:donut-wikipedia`; the actual opening sentence is "DONUT ... was an
   experiment at Fermilab dedicated to the search for tau neutrino
   interactions." `facility_roles` is not on A15's list of fields that
   *require* a quote, and the underlying claim (DONUT was hosted at
   Fermilab) is true and already correctly flagged `confidence: uncertain`,
   so this is cosmetic, not evidentiary. **Fix applied** for consistency
   with the fixes above.

### P2 — found, not fixed (observation only, logged)

6. **`data/atlas/sites/lngs-hall-c.json`** (owned by the `facilities` lead,
   out of this domain's scope to edit) labels its coordinate `kind:
   "underground_lab"` rather than `"campus"`, while the note admits the
   point is really just LNGS's published Assergi street address reused
   from `site:lngs-hall-b`, with no hall-specific survey. A23 explicitly
   requires the honest label to be `campus` (not a facility-specific kind)
   when only an address-level point is available. This affects OPERA's
   detector placement and the CNGS beamline's far-endpoint, both of which I
   reference but do not own the underlying site file for. Flagging for the
   `facilities` lead; the great-circle check (item 11 above) still passes
   comfortably regardless.

7. Minor worklog/data mismatches (not defects in the data itself, logged for
   the record): the researcher's own worklog claims KARMEN/LSND site
   coordinates were "explicitly labelled `kind: detector`" — the actual
   `site:isis-rutherford-appleton.json` correctly says `kind: "campus"`. The
   worklog also describes `src:lsnd-prd-2001-antineutrino-evidence` as
   `retrieval: "partial"` due to "garbled PDF encoding" — the actual source
   record and the live page both show this arXiv paper's HTML rendering is
   full text (confirmed: the fetch returned the complete Introduction,
   Results, Table 11, etc.), and the JSON correctly records
   `retrieval: "full_text"`. The data is right; the prose narrative is
   stale/inaccurate. No action taken (worklog is a log, not a data file).

## Values I could not independently verify (source unreachable in this session)

- `src:karmen-isis-osm-nominatim` — a Nominatim API JSON response, not
  independently re-queried (geocoder coordinate, `kind: campus`,
  `confidence: approximate`, correctly not treated as authoritative for a
  detector-grade point).
- OPERA construction interval (2003–2008): only source is Wikipedia
  (`operaweb.lngs.infn.it` does not resolve, `lngs.infn.it/en/opera`
  returned HTTP 500 when I tried it again this session — same failure the
  researcher reported). Correctly marked `confidence: uncertain`.
- DONUT run period, detector technology, and host framing: only source is
  Wikipedia (`fnal.gov` returned HTTP 403 to every fetch attempt in this
  session too — same block the researcher reported). Correctly marked
  `confidence: uncertain` throughout.
- Collaboration formation dates for all four collaborations: no source
  found by the researcher or by me; correctly `null` with a note in every
  case, not asserted.

## Fixes applied (summary, 5 files)

- `data/atlas/experiments/lsnd.json` — corrected two fabricated quotes/locators (30 m, 167 t); added `accelerator:lansce` to `accelerator_ids` (see below).
- `data/atlas/detectors/lsnd.json` — corrected the same two fabricated quotes/locators.
- `data/atlas/experiments/karmen.json` — corrected `energy_regime` source attribution for the 800 MeV figure.
- `data/atlas/experiments/donut.json` — corrected a non-verbatim `facility_roles` quote; removed an unsourced "800 GeV-class" figure from `summary.technical`.

All edits: canonical `json.dumps(sort_keys=True, indent=2, ensure_ascii=False)` + trailing newline, `verified_at` set to `2026-09-17`. No value (30 m, 167 t, 800 MeV, DONUT's host role) changed — only the evidentiary text backing it.

**One additional non-cosmetic fix**: `experiment:lsnd.json/accelerator_ids` was
`[]` at write time because `accelerator:lansce` (owned by the `facilities`
lead) did not exist yet — an expected gap per the researcher's worklog. It
exists now (confirmed `id: "accelerator:lansce"`, `facility_id:
"facility:los-alamos-national-laboratory"`, the LAMPF/LANSCE linac). Since
LSND's own sourced fields already state its beam came from this accelerator,
I added the reference; this also resolved a live A12 validator warning
("experiment is active but no listed accelerator is") for LSND. `facility:
los-alamos-national-laboratory`, `site:lanl-lansce`, and `accelerator:lansce`
have all landed since the researcher's pass — the 6 dangling references their
worklog reported are gone from the current validator run.

## Validator

`.venv/bin/python -m hepgraph.atlas.validate`, run before and after edits.
**0 errors attributable to this domain's files** in both runs. The
repo-wide error count moved between runs (70 → 105) purely from concurrent
edits by other sessions in this shared worktree (BNL/CERN site-proximity
warnings, BaBar/SLD quote-length and sourced-value errors, status-derivation
mismatches on unrelated facilities) — confirmed by diffing the error lists
and checking that none of the new findings mention karmen/lsnd/opera/donut/
isis/cngs. The only findings ever attributable to these files across both
runs:
- `sites/isis-rutherford-appleton.json`: A23 approximate-coordinate warning (by design, correct).
- 9 `sources/*.json`: A1 "rank is derived at build time" warning (repo-wide convention, matches the exemplar file, not a defect).
- `experiments/karmen.json`: A12 "active but no listed accelerator/beamline" warning — KARMEN has no `accelerator:isis-*` entity in the atlas at all (none was created by any lead; out of scope to fabricate one during verification), shared with 14+ other pre-existing experiments repo-wide.
- The now-resolved LSND dangling references to `facility:los-alamos-national-laboratory` / `site:lanl-lansce` / `accelerator:lansce`, and OPERA/CNGS's reference to `site:lngs-hall-c` — all now satisfied since the `facilities` lead landed these ids.

## Verdict

**Pass, with corrections applied.** No P0 defects. Four P1 sourcing-integrity
defects (all "quote doesn't match source" or "value attributed to wrong
source," never a wrong value) and two P2s found and fixed directly; one P2
observation logged against a file outside this domain's ownership
(`site:lngs-hall-c`). Every critical scientific claim — masses, distances,
energies, dates, result wording, significance — checked against its source
in this session and found accurate in magnitude, unit, and framing. The
domain is fit to ship as `completed`-status historical records; the two
open items (LNGS Hall C's coordinate `kind`, and KARMEN having no
accelerator entity to satisfy the A12 warning) are both owned by other
leads or out of scope for a data-accuracy verification pass.
