# VERIFY_facilities — independent verification pass (wave 3, domain "facilities")

Verifier: independent agent, no prior involvement in `facilities.md`. Scope: the 13
facility records, 23 sites and 10 accelerators listed in the brief (Brookhaven,
SLAC, DESY, Jefferson Lab, Oak Ridge/SNS, Los Alamos/LANSCE, Argonne, PSI, SNOLAB,
Modane/LSM, Canfranc/LSC, CJPL, Boulby), skipping BNL records already covered by
the `heavy-ions` verifier except for one cross-record check (AGS -> RHIC feed).
No git used. Worked directly in `data/atlas/` and this file plus new
`src:facilities-verify-*` sources. `docs/atlas-worklog/facilities.md` was read
only to know what to distrust, per instructions, not trusted as ground truth.

## Records checked

- 13 facility records, all 23 sites, all 10 accelerators named in the brief.
- 6 `institution:` records for the same laboratories (Brookhaven, DESY, SLAC, PSI,
  Los Alamos, Argonne), found while checking for cross-record duplicates.
- Re-opened every `src:` record cited by the above (Wikipedia, OSM/Nominatim,
  official pages) to confirm `retrieval`/`source_type`/URL honesty.
- Cross-checked `docs/HEP_ATLAS_ONTOLOGY.md` A1/A7/A9/A10/A15/A17/A18/A20/A21/A23
  and `docs/HEP_ATLAS_SOURCES.md`'s rank table against every sourced value touched.

## Values re-fetched this session

~50 fetch operations (43 `WebFetch`, 7 `WebSearch`) against sources not previously
fetched by me, covering: 11 ROR API lookups (SLAC, DESY, JLab, ORNL, LANL, Argonne,
PSI, LSM, LSC, Boulby, CJPL — 2 of these matched nothing usable), ~20 official-page
attempts (`www6.slac.stanford.edu`, `jlab.org` x3, `lanl.gov`/`lansce.lanl.gov`,
`anl.gov` x2, `psi.ch` x5, `ornl.gov` x2, `desy.de` x2, `snolab.ca`, `lsm.in2p3.fr`,
`lsc-canfranc.es`, `boulby.stfc.ac.uk` x2, `cjpl.sjtu.edu.cn`), and ~9 Wikipedia/
secondary re-fetches for exact quotes (HERA, SLC, SLAC linac, SNS, Jefferson Lab/
CEBAF, BaBar). Every quoted number in the fixes below was seen in this session's
fetched content, not carried over from the prior agent's excerpts.

## Coordinate-source table: before -> after

| site | kind | before | after |
| --- | --- | --- | --- |
| bnl-upton-campus / bnl-rhic-ip6-star / bnl-rhic-ip8-phenix-sphenix | campus | ROR (rank 8) | **unchanged** (already correct; BNL is the heavy-ions verifier's territory) |
| slac-menlo-park-campus | campus | Wikipedia (12) | **ROR ror.org/05gzmn429 (8)**, Wikipedia kept as corroboration |
| slac-pep-ii-ir2-babar | campus | Wikipedia (12) | **ROR (8)**; IR-2/BaBar naming itself was uncited — added a Phys.org quote (12) that actually confirms it |
| slac-slc-collider-hall-sld | campus | Wikipedia (12) | **ROR (8)** |
| desy-hamburg-campus | campus | Wikipedia (12) | **ROR ror.org/01js2sh04 (8)** |
| desy-hera-north-hall-h1 | campus | Wikipedia (12) | **ROR (8)**; H1 pairing already corroborated |
| desy-hera-south-hall-zeus | campus | Wikipedia (12) | **ROR (8)**; ZEUS pairing already corroborated |
| jlab-newport-news | campus | Wikipedia (12) | **ROR ror.org/02vwzrd76 (8)**, new src |
| ornl-sns-neutrino-alley | campus | Wikipedia (12) | **ROR ror.org/01qz5mb56 (8)**, new src; still ORNL campus centroid, not the corridor itself |
| lanl-lansce | campus | Wikipedia (12) | **ROR ror.org/01e41cf67 (8)** |
| argonne-campus | campus | Wikipedia (12) | **ROR ror.org/05gvnxz63 (8)**; anl.gov still 403 for prose facts |
| psi-villigen | campus | Wikipedia (12) | **ROR ror.org/03eh3y714 (8)**; psi.ch itself now reachable too (see fixes) |
| lsm-frejus | campus | OSM (8) | unchanged (8->8); ROR's own match for "Laboratoire Souterrain de Modane" is a wrong record — a Czech "participation" entry in Prague — not usable |
| lsc-canfranc | campus | OSM (8) | unchanged (8->8), but ROR ror.org/02zcam055 (8) added as a second, corroborating geocoder (~830 m from the OSM point; both noted) |
| cjpl-i / cjpl-ii | campus | OSM (8) | unchanged; no ROR entry exists for CJPL |
| boulby-mine | campus | OSM (8) | unchanged; no ROR entry exists for Boulby; official STFC page re-fetched, still no numeric coordinate |
| snolab-underground-lab | underground_lab | SNO detector paper (5) | unchanged, already the strongest possible source |
| lngs-hall-a / -b / -c | underground_lab | official LNGS page (2) | unchanged, already correct |

Net: **11 of 16 upgradeable campus points moved from Wikipedia-only (rank 12) to
ROR-geocoder (rank 8)**; 5 OSM-only points (already rank 8) could not be improved
in rank (2 have no ROR entry at all — Boulby, CJPL; LSM's ROR match is wrong; LSC
got a second corroborating rank-8 source). No point was ever promoted past
`kind: campus`/`confidence: approximate` without a rank <= 5 source, per A17/A23 —
SNOLAB and LNGS remain the only two labs in this batch with anything stronger.

## Findings by severity

**P0 (none found).** No fabricated coordinates, no invented dates, no `verified`
value resting solely on a rank > 10 source, no silent "no path"/"shortest"
overreach (not applicable to this domain), no derived field re-authored as fact.

**P1 (fixed):**
1. `accelerator:psi-hipa.specs.beam_power` was **1.3 MW**, sourced only to a
   Wikipedia sentence about current beam *allocation* to SINQ/SmuS, not the
   facility's own headline figure. PSI's own official page
   (`psi.ch/en/cas/hipa`, now reachable — it 404'd for the prior agent) states
   **"HIPA ... provides a 1.4 MW proton beam"**, matching the value the brief
   itself names. Corrected, confidence raised to `verified`.
2. `accelerator:hera.specs` had **no `beam_energy`/`proton_energy` fields at
   all**. The prior record's own note claimed no schema key existed for a
   per-species accelerator energy; `hepgraph/atlas/schema.py`'s
   `SPEC_KEY_DIMENSIONS` in fact already defines `proton_energy` (dimension
   `energy`) and `beam_energy` is the generic energy key — the omission was a
   mistaken assumption, not a real schema gap. Added both (27.5 GeV e-/e+,
   920 GeV p), matching the brief's stated expectation, re-confirmed via a
   second, independently-fetched DESY-hosted page.
3. Two **A10 status/derived-state errors** pre-existed in this domain:
   `accelerator:slac-linac` had `status: active` with an **empty `intervals`
   list** (so the build derived `None`), and `accelerator:sns` had two
   intervals both with `start: null` (neither covers the build date). Fixed
   by adding sourced intervals (SLAC linac operating since 1966; SNS
   instruments commissioned August 2007), both re-fetched from Wikipedia this
   session.
4. **8 of 10 accelerator records had empty `summary.plain`/`summary.technical`**
   (`slac-linac`, `pep-ii`, `slc`, `hera`, `cebaf`, `sns`, `lansce`,
   `psi-hipa`) — a violation of the ontology's own required-field rule
   (`summary` is required, and `RESEARCH_AGENT_RULES.md` #14 sets a word
   budget) that the validator does not mechanically check. Written from
   already-cited, already-sourced facts on each record; no new claims.
5. `site:slac-pep-ii-ir2-babar`'s own name/id asserts BaBar sat at PEP-II's
   "Interaction Region 2," but neither of its two cited sources (SLAC
   Wikipedia, BaBar Wikipedia) actually says this — re-checked both this
   session and confirmed the claim is absent from both. Independently
   confirmed via a 2006 Phys.org article quoting BaBar's own control-room
   name ("BaBar's Interaction Region 2 control room") and cited.
6. `accelerator:ags.feeds_accelerator_ids` was an **empty list** despite the
   record's own already-cited quote stating "The AGS ... delivers [particles]
   to the Relativistic Heavy Ion Collider after acceleration" — the canonical
   A1 downstream relation was described in prose but never written into the
   structured field. Added `accelerator:rhic`. (This is the one BNL-adjacent
   cross-check the brief allows outside the heavy-ions verifier's territory.)
7. `accelerator:cebaf`'s interval history jumped straight from "construction
   begins 1987" to "12 GeV Upgrade dedication 2018," skipping CEBAF's own
   operating history that the already-cited Wikipedia source gives in full:
   first beam 1994-07-01, 4 GeV design energy reached 1995, "enhanced design
   energy" of 6 GeV reached 2000-08-06 — exactly the "4/6 GeV before the
   upgrade" figures the brief asks to check. `RESEARCH_AGENT_RULES.md` #8
   ("give the richest sourced history... do not collapse to one row") was
   violated; added the three missing intervals with per-interval
   `specs.beam_energy`.
8. Six `institution:` records for these same laboratories (Brookhaven, DESY,
   SLAC, PSI, Los Alamos, Argonne) already carry `coordinates` from the exact
   same ROR organizations I independently queried — matching to 5 decimal
   places, which is strong cross-validation of the ROR fetches — but every
   one had **`facility_id: null`**, breaking the canonical A1 link between
   the facility and the institution that plays its collaboration-member
   role (ontology SS0.5). Set `facility_id` on all six.
9. `facility:psi`'s founding interval and website were Wikipedia-only/
   `uncertain` because the prior session found every `psi.ch` URL 404ing.
   `psi.ch` (root, `/en`, `/en/about`, `/en/about/history-of-psi`,
   `/en/cas/hipa`, and a HIPA-anniversary news story) is fully reachable this
   session. Upgraded founding to a day-precision official quote ("On 1
   January 1988 ... merged to form the Paul Scherrer Institute, PSI") and the
   website field to the official homepage.
10. `facility:slac`'s website/operator were Wikipedia-only/`uncertain`
    because the prior session hit a TLS error on `slac.stanford.edu`.
    `www6.slac.stanford.edu` is reachable this session and confirms the same
    address/operator wording already recorded; upgraded to `verified`.

**P2 (documented, not changed):**
- Argonne's official site (`anl.gov`, `/about`, `/our-history`, root) returned
  HTTP 403 on every attempt in this session too; all Argonne prose facts
  (founding date, operator) remain Wikipedia-only/`uncertain` — consistent
  with the prior session, re-confirmed rather than assumed stale.
- Jefferson Lab's founding date remains Wikipedia-only: `jlab.org/about` is
  reachable but states no founding year; `jlab.org/about/history` 404s; the
  official factsheet PDF fetched but rendered as unreadable binary. A
  `WebSearch` snippet surfaced "founded August 3, 1984" but per A17 this
  cannot be used without an actual fetched, readable source — left as-is.
- ORNL's "Neutrino Alley" still has no official coordinate;
  `neutrons.ornl.gov/coherent` still 404s. The ORNL campus ROR point is at
  least now a real geocoder value rather than a Wikipedia infobox, but it is
  no closer to the actual corridor than before — the note says so.
- SLC's brief-quoted "50 GeV per beam" is real (Wikipedia: "an RF linear
  accelerator that accelerated electrons and positrons up to 50 GeV") but is
  the linac's *design maximum*, not the ~45.5-45.6 GeV/beam actually used to
  sit on the Z resonance (implied by the record's own, unchanged, ~91 GeV
  cms value). Recorded both, with a note making the distinction explicit
  rather than silently picking one.
- HERA's circumference is recorded as 6.3 km (Wikipedia); an independently
  fetched DESY-hosted page states 6.4 km for the same ring. Not resolved
  (both are secondary/rank-12-equivalent quality here) — flagged rather than
  silently overwritten.

## Fixes applied (file list)

New sources (`data/atlas/sources/`): `facilities-verify-jlab-ror`,
`facilities-verify-ornl-ror`, `facilities-verify-lsc-ror`,
`facilities-verify-slac-official-home`, `facilities-verify-psi-official-home`,
`facilities-verify-psi-history-page`, `facilities-verify-psi-hipa-page`,
`facilities-verify-psi-hipa-turns-50`, `facilities-verify-hera-desy-ameyer`,
`facilities-verify-babar-ir2-physorg`. Reused (not duplicated) existing sources
`src:ror-02ex6cf31/01js2sh04/05gzmn429/03eh3y714/01e41cf67/05gvnxz63` (already
created by an institution-focused workstream) and `src:slac-wikipedia`,
`src:jlab-wikipedia`, `src:hera-wikipedia`, `src:slc-wikipedia`,
`src:sns-wikipedia`, `src:psi-wikipedia` (re-fetched with new quotes this
session).

Modified: `facilities/psi.json`, `facilities/slac.json`; `sites/slac-menlo-park-
campus.json`, `sites/slac-pep-ii-ir2-babar.json`, `sites/slac-slc-collider-hall-
sld.json`, `sites/desy-hamburg-campus.json`, `sites/desy-hera-north-hall-h1.json`,
`sites/desy-hera-south-hall-zeus.json`, `sites/jlab-newport-news.json`,
`sites/ornl-sns-neutrino-alley.json`, `sites/lanl-lansce.json`,
`sites/argonne-campus.json`, `sites/psi-villigen.json`, `sites/lsc-canfranc.json`;
`accelerators/psi-hipa.json`, `accelerators/hera.json`, `accelerators/slc.json`,
`accelerators/slac-linac.json`, `accelerators/pep-ii.json`,
`accelerators/cebaf.json`, `accelerators/sns.json`, `accelerators/lansce.json`,
`accelerators/ags.json`; `institutions/brookhaven-national-laboratory.json`,
`institutions/desy.json`, `institutions/slac-national-accelerator-laboratory.json`,
`institutions/paul-scherrer-institute.json`,
`institutions/los-alamos-national-laboratory.json`,
`institutions/argonne-national-laboratory.json`.

## Unverifiable values (left as-is, honestly flagged)

Argonne founding/operator/website (anl.gov 403); Jefferson Lab founding year;
CJPL's exact coordinate and CJPL-II completion date (`cjpl.sjtu.edu.cn` does not
resolve; `cjpl.tsinghua.edu.cn` gives no coordinate); Boulby's exact underground
coordinate; LSM's exact coordinate beyond the OSM node; SNOLAB's own
founding/opening date (Wikipedia-only); LNGS Hall A/C individual experiment
occupants. None of these were guessed or upgraded past their honest confidence.

## Seed-list table (spec's 22-facility list)

| facility | in atlas? | `primary_site_id` coordinates present? | kind / confidence |
| --- | --- | --- | --- |
| CERN | yes | yes | campus / approximate |
| Fermilab | yes | yes | detector / uncertain (pre-existing; outside this domain) |
| Brookhaven | yes | yes | campus / approximate |
| SLAC | yes | yes | campus / approximate (now ROR, was Wikipedia) |
| Jefferson Lab | yes | yes | campus / approximate (now ROR, was Wikipedia) |
| KEK | yes | **no — `primary_site_id: null`** | n/a (flagged by the prior facilities lead too; not this domain's id to fix) |
| J-PARC | yes | yes | campus / approximate |
| DESY | yes | yes | campus / approximate (now ROR, was Wikipedia) |
| LNGS | yes | yes | underground_lab / approximate |
| SURF | yes | yes | campus / approximate |
| SNOLAB | yes | yes | underground_lab / **verified** |
| Kamioka | yes | yes | underground_lab / verified |
| South Pole | yes | yes | detector / approximate |
| KM3NeT | yes (as `facility:km3net`) | yes | detector / verified |
| Baikal | yes | yes | detector / verified |
| Oak Ridge/SNS | yes | yes | campus / approximate (now ROR, was Wikipedia) |
| Los Alamos | yes | yes | campus / approximate (now ROR, was Wikipedia) |
| Argonne | yes | yes | campus / approximate (now ROR, was Wikipedia) |
| Modane | yes | yes | campus / approximate (OSM, unchanged) |
| Canfranc | yes | yes | campus / approximate (OSM, ROR added as corroboration) |
| CJPL | yes | yes | campus / approximate (OSM, unchanged) |
| Boulby | yes | yes | campus / approximate (OSM, unchanged) |

21 of 22 seed facilities have a `primary_site_id` with coordinates; only KEK is
missing one, which is a pre-existing gap outside this domain's ownership.

## Verdict

`python -m hepgraph.atlas.validate`: this domain's files contribute **0 errors**
(confirmed by grepping the full error list for every facility/site/accelerator/
institution/source id touched, both immediately after each batch of edits and
again at the end). The repo-wide error count fluctuates run-to-run (3-27 during
this session) because this is a shared worktree with concurrent sessions editing
other domains simultaneously (per `CLAUDE.md`); every fluctuation checked
traced to files this domain does not own (`fermilab`, `mit`,
`university-of-washington-cenpa`, `yale-wright-lab`, `xenonnt`, `supercdms`,
`detectors/cupid.json` transiently unparseable mid-write by another session).
`python -m hepgraph.atlas.build` succeeds. No P0s found. 10 P1s fixed (2 real
factual corrections — PSI HIPA beam power, missing HERA beam energies; 2 real
A10 bugs; 1 uncited naming claim closed; 1 missing canonical relation; 1
incomplete interval history; 6 missing institution<->facility links; 2 facility
records upgraded from unreachable-official-site fallbacks to reachable
official sources). 11 of 16 upgradeable coordinate points moved from
Wikipedia-only to a rank-8 ROR geocode; the remaining 5 (Boulby, CJPL x2, LSM,
LSC) could not be improved in rank because no ROR record exists for them (LSC
got a second corroborating ROR citation regardless). No coordinate was ever
promoted past `campus`/`approximate` without a source that actually licenses
that under A17/A23.
