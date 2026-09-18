# facilities — wave 3 research log

## Scope

Owner slug `facilities`. This workstream owns no experiments. It creates the 14 shared
laboratories (and their sites/accelerators) listed for the `facilities` row of the Wave 3
table in `docs/atlas-worklog/ID_REGISTRY.md`, so the other 15 wave-3 leads can reference
them: Brookhaven, SLAC, DESY, Jefferson Lab, Oak Ridge/SNS, Los Alamos, Argonne, PSI,
SNOLAB, Modane/LSM, Canfranc/LSC, CJPL, Boulby, and two new LNGS halls (A, C) under the
pre-existing `facility:lngs`. No `people/`, `experiments/`, `detectors/` or
`collaborations/` files were created. No coverage rows were written (per the brief: none
needed unless an experiment is created, which it was not).

One child agent (BNL + RHIC/AGS, `model: sonnet`) was spawned and its work was reviewed and
partly re-fixed by the lead (see "Children spawned" below). Every other facility (SLAC, DESY,
Jefferson Lab, ORNL/SNS, Los Alamos/LANSCE, Argonne, PSI, and all six underground labs plus
the two LNGS halls) was researched directly by the lead after repeated `Concurrent subagent
limit reached (20 max)` errors — this worktree is shared by ~16 concurrent wave-3 leads, so
the cap saturates quickly; per the coordinator's explicit instruction the lead did the
remaining research itself rather than continuing to retry for child capacity.

`WebSearch` exhausted its session-wide quota (200/200) partway through Group 1 research;
all subsequent lookups used `WebFetch` directly (official pages, Wikipedia as a documented
fallback, and the OpenStreetMap/Nominatim geocoder for coordinates) rather than search.

## Entities written

**Facilities (14):** `facility:brookhaven-national-laboratory`, `facility:slac`,
`facility:desy`, `facility:jefferson-lab`, `facility:oak-ridge-national-laboratory`,
`facility:los-alamos-national-laboratory`, `facility:argonne-national-laboratory`,
`facility:psi`, `facility:snolab`, `facility:modane-underground-laboratory`,
`facility:canfranc-underground-laboratory`, `facility:cjpl`,
`facility:boulby-underground-laboratory`. (`facility:lngs` already existed and was **not**
modified.)

**Sites (23):** `site:bnl-upton-campus`, `site:bnl-rhic-ip6-star`,
`site:bnl-rhic-ip8-phenix-sphenix`, `site:slac-menlo-park-campus`,
`site:slac-pep-ii-ir2-babar`, `site:slac-slc-collider-hall-sld`, `site:desy-hamburg-campus`,
`site:desy-hera-north-hall-h1`, `site:desy-hera-south-hall-zeus`, `site:jlab-newport-news`,
`site:ornl-sns-neutrino-alley`, `site:lanl-lansce`, `site:argonne-campus`,
`site:psi-villigen`, `site:snolab-underground-lab`, `site:lsm-frejus`, `site:lsc-canfranc`,
`site:cjpl-i`, `site:cjpl-ii`, `site:boulby-mine`, `site:lngs-hall-a`, `site:lngs-hall-c`.
(`site:lngs-hall-b` already existed and was **not** modified; its conventions were matched
exactly for the two new halls.) `site:snolab-sno-cavern` was **not** created: no distinct,
separately-sourced coordinate/description for the original SNO cavern (as opposed to the
general SNOLAB underground facility) was found in this session.

**Accelerators (10):** `accelerator:rhic`, `accelerator:ags`, `accelerator:slac-linac`,
`accelerator:pep-ii`, `accelerator:slc`, `accelerator:hera`, `accelerator:cebaf`,
`accelerator:sns`, `accelerator:lansce`, `accelerator:psi-hipa`. `accelerator:bnl-linac` and
`accelerator:bnl-booster` (both marked optional in the registry) were **not** created for
lack of time.

## Coordinate honesty summary (the load-bearing part of this record set)

Per A17/A23, a coordinate of `kind: detector`/`underground_lab` needs an official page or a
technical/geodetic paper (rank ≤ 7); a geocoder or Wikipedia point is only acceptable at
`kind: campus`, `confidence: approximate`. Status per site:

| site | kind | confidence | coordinate source | note |
| --- | --- | --- | --- | --- |
| bnl-upton-campus | campus | approximate | ROR geocode (rank 8) | campus centroid |
| bnl-rhic-ip6-star | campus | approximate | ROR geocode (rank 8) | per A23, reverted from an earlier `kind: detector` workaround; no rank≤7 source pins IP6 specifically (star.bnl.gov/phenix.bnl.gov 403'd; three technical PDFs returned corrupted binary) |
| bnl-rhic-ip8-phenix-sphenix | campus | approximate | ROR geocode (rank 8) | same as above; PHENIX Wikipedia infobox (rank 12, ~1.6 km away) kept only as corroboration, not a source |
| slac-menlo-park-campus | campus | approximate | Wikipedia (rank 12) | slac.stanford.edu unreachable (TLS cert error) in this session |
| slac-pep-ii-ir2-babar | campus | approximate | Wikipedia (rank 12) | no IR2-specific coordinate found |
| slac-slc-collider-hall-sld | campus | approximate | Wikipedia (rank 12) | no hall-specific coordinate found |
| desy-hamburg-campus | campus | approximate | Wikipedia (rank 12) | desy.de about page (rank 2) fetched for other facts, no coordinate given |
| desy-hera-north-hall-h1 | campus | approximate | Wikipedia (rank 12) | Wikipedia's H1 article confirms North Hall = H1 |
| desy-hera-south-hall-zeus | campus | approximate | Wikipedia (rank 12) | Wikipedia's ZEUS article confirms South Hall = ZEUS |
| jlab-newport-news | campus | approximate | Wikipedia (rank 12) | |
| ornl-sns-neutrino-alley | campus | approximate | Wikipedia (rank 12, ORNL campus centroid) | neutrons.ornl.gov/coherent 404'd; no coordinate for the hall itself found |
| lanl-lansce | campus | approximate | Wikipedia (rank 12) | TA-53 area, not a surveyed point |
| argonne-campus | campus | approximate | Wikipedia (rank 12) | anl.gov returned HTTP 403 on every attempt |
| psi-villigen | campus | approximate | Wikipedia (rank 12) | every psi.ch URL attempted (proscan/hipa, about, facts-and-figures, media/our-research) returned HTTP 404 |
| **snolab-underground-lab** | **underground_lab** | **verified** | **original SNO detector paper, Nucl. Instrum. Meth. A449 (2000) 172 (`detector_paper`, rank 5)** | the one genuinely rank≤7-sourced underground-lab point in this batch; 46°28'30"N 81°12'04"W, depth 2039 m to vessel centre, ~6000 m.w.e. |
| lsm-frejus | campus | approximate | OSM/Nominatim node tagged "Laboratoire Souterrain de Modane (LSM)" (rank 8) | official page states depth (1700 m) and founding (1981) but no coordinate |
| lsc-canfranc | campus | approximate | OSM/Nominatim node tagged "Laboratorio Subterráneo de Canfranc" (rank 8) | official page states depth (800 m) but no coordinate |
| cjpl-i | campus | approximate | OSM/Nominatim node (rank 8) | official pages state depth (2400 m) but no coordinate |
| cjpl-ii | campus | approximate | OSM/Nominatim (rank 8) + arXiv:1404.2651 distance statement | ~500 m west of CJPL-I per the second-phase-development paper; flagged by the validator's A23 rule (campus-grade point on a site holding a detector placement) — accepted as a warning |
| boulby-mine | campus | approximate | OSM/Nominatim node tagged "Cleveland Potash & Dark Matter Research Centre" (rank 8) | official page states depth (1.1 km) but no coordinate |
| lngs-hall-a, lngs-hall-c | underground_lab | approximate | LNGS's own "How to reach LNGS" address page (rank 2, official), reused from `site:lngs-hall-b`'s established pattern | LNGS publishes no per-hall coordinate; matches the precedent already accepted for Hall B |

**A23 note:** the validator was amended mid-session so that a site holding a detector
placement may keep `kind: campus` with `confidence: approximate`/`uncertain` and a note (a
warning, not an error) instead of being forced into a false `kind: detector`/
`underground_lab`. `site:bnl-rhic-ip6-star`/`ip8-phenix-sphenix` were reverted to this honest
`campus` state after the BNL child had (transparently, in its own note) set `kind: detector`
purely to satisfy the validator's placement rule before A23 existed. `site:cjpl-ii` and
`site:lsc-canfranc` were already written this way and needed no change.

## Sources added (49)

All fetched in this session (`accessed: 2026-09-17`), grep-checked against existing URLs/DOIs
before creation: `src:argonne-wikipedia`, `src:babar-wikipedia`, `src:bnl-about-history-*`,
`src:bnl-about-page`, `src:bnl-newsroom-*` (×4), `src:bnl-rhic-*` (×4, incl.
`src:bnl-rhic-phenix-wikipedia`), `src:bnl-ror-record`, `src:boulby-osm-nominatim`,
`src:boulby-stfc-about`, `src:cjpl-arxiv-early-science-2018`, `src:cjpl-arxiv-phase2-2014`,
`src:cjpl-osm-nominatim`, `src:cjpl-tsinghua-about-overview`, `src:cjpl-tsinghua-home`,
`src:desy-about-page`, `src:desy-wikipedia`, `src:h1-wikipedia`, `src:hera-wikipedia`,
`src:jlab-about-page`, `src:jlab-accelerator-page`, `src:jlab-wikipedia`,
`src:lanl-about-page`, `src:lansce-wikipedia`, `src:lsc-about-us`, `src:lsc-history`,
`src:lsc-osm-nominatim`, `src:lsm-official-site`, `src:lsm-osm-nominatim`,
`src:ornl-sns-page`, `src:ornl-wikipedia`, `src:psi-wikipedia`, `src:slac-wikipedia`,
`src:slc-wikipedia`, `src:sno-nim-detector-paper-2000`, `src:snolab-about-snolab`,
`src:snolab-about-us`, `src:snolab-facility-page`, `src:snolab-osm-nominatim`,
`src:snolab-underground-facilities`, `src:snolab-wikipedia`, `src:sns-wikipedia`,
`src:zeus-wikipedia`. BNL's child also reused `src:heavy-ions-rhic25-timeline` and
`src:heavy-ions-rhic-final-collisions-2026`, created concurrently by the `heavy-ions` lead
for the same BNL pages, rather than duplicating them.

## Conflicts

| claim | source A | source B | chosen | why | confidence |
| --- | --- | --- | --- | --- | --- |
| SNOLAB depth-in-water-equivalent | official SNOLAB pages (no m.w.e. figure found) | Wikipedia: "6010 m.w.e." (2070 m rock) | **replaced entirely**: the SNO detector paper's own "~6000 m water equivalent" (rank 5) | A17 forbids a detector/underground-lab-grade claim resting on Wikipedia alone when a real detector paper exists; the SNO paper is both higher-ranked and independently authoritative | verified |
| RHIC polarized p+p max energy | BNL press release (Run 22, 2021): "500 GeV" | secondary spin-physics literature (not re-fetched): up to 510 GeV | 500 GeV | only the officially-fetched, quoted figure is used; the 510 GeV figure was seen only in an unfetched search summary and was deliberately not used (A17) — logged by the BNL child | verified |
| LNGS Hall A/C occupants | none found | none found | omitted from summaries | official LNGS pages fetched (`lngs-overview`, `lngs-about-general`, `lngs-halls`→404) give only the collective three-hall description (100×20×18 m each); no page states which experiments occupy Hall A or Hall C individually, so that attribution is left out rather than guessed | n/a |
| BNL kind (`accelerator_laboratory` vs `research_laboratory`) | BNL's own history page centres accelerators (Cosmotron→AGS→RHIC) | BNL's `/about/` page calls it a "multidisciplinary laboratory" | `accelerator_laboratory` | matches the Fermilab precedent and BNL's historically defining machines; disclosed as a judgment call in the facility's own notes | verified (kind), noted judgment |

## Unresolved fields (honest gaps, not guessed)

- **PSI**: every official `psi.ch` URL attempted in this session returned HTTP 404
  (`/en/proscan/hipa`, `/en/media/our-research/...`, `/en/about`,
  `/en/lab-life-and-safety/facts-and-figures`, `/en/hipa`). Every claim on `facility:psi`,
  `site:psi-villigen` and `accelerator:psi-hipa` is therefore sourced to Wikipedia only (rank
  12) and marked `confidence: uncertain`/`approximate` with an explicit flag-for-review note.
- **Argonne**: `anl.gov` returned HTTP 403 on every attempt; same Wikipedia-only treatment.
  `topic_ids` is left empty — no HEP-Atlas topic clearly fits Argonne's broad multiprogram
  profile in this wave, and no accelerator was created for it (per the brief).
- **SLAC**: `slac.stanford.edu` returned a TLS certificate error; Wikipedia-only, flagged.
  `pep-ii`'s `feeds_accelerator_ids: ["accelerator:slac-linac"]` is recorded as an unsourced
  structural fact (no page fetched states the injection chain explicitly) — flagged in its
  notes for a future agent to source or remove.
- **JLab / ORNL / LANL**: founding and construction dates were only found on Wikipedia even
  where an official page was reachable for other facts (JLab's own `/about` and `/accelerator`
  pages don't state dates); those specific date fields are `confidence: uncertain`.
- **CEBAF's original commissioning date** (as opposed to the 1987 construction start and the
  2018-05-02 12 GeV dedication) was not found in this session and is not recorded.
- **CJPL-II's civil-engineering completion date** (reported elsewhere as December 2023) was
  not confirmed on any official CJPL page reachable in this session (`cjpl.tsinghua.edu.cn`
  gave only Chinese-language partial content; `pandax.sjtu.edu.cn/cjpl` gave no dates) and is
  therefore not recorded.
- **LSC's founding year**: the official history page dates the *research project's start* to
  1985; no separately-stated formal-establishment date for the present-day LSC consortium was
  found, so 1985 stands with a note explaining the distinction.
- **"Neutrino Alley" (ORNL)**: no official page (`neutrons.ornl.gov/coherent` → 404) gives a
  coordinate or confirms "underground" as its setting beyond the general COHERENT literature;
  flagged in the site's own notes.
- **KEK** (spec-mandated check, not owned by this lead): of the 9 pre-existing seed facilities
  checked (`amundsen-scott-south-pole-station`, `cern`, `fermilab`, `j-parc`,
  `kamioka-observatory`, `kek`, `lngs`, `soudan-underground-laboratory`, `surf`), only
  **`facility:kek` has `primary_site_id: null`**; all others already have a non-null
  `primary_site_id` with a coordinate. Not fixed, per instructions (not this lead's
  registry ownership) — reported here for the KEK-owning lead/orchestrator.

## Children spawned and what was re-checked

One child, **BNL + RHIC/AGS** (`general-purpose`, `model: sonnet`), given this brief, the
exact ids, and the exemplar files. It wrote `facility:brookhaven-national-laboratory`, the
three BNL sites, `accelerator:rhic` and `accelerator:ags`. The lead re-opened/independently
re-verified:
- **BNL founding (1947)** — matches `src:bnl-about-history-page`'s own quote; accepted.
- **RHIC circumference (3.86 km / 2.4 mi) and cms energies (200 GeV Au+Au, 500 GeV pol. p+p)**
  — cross-checked the child's cited BNL newsroom quotes against the source files it created;
  consistent and properly quoted; accepted.
- **AGS design energy (33 GeV, July 1960)** — matches `src:bnl-about-history-accelerators-page`
  verbatim; accepted.
- **RHIC IP6/IP8 coordinates** — re-examined per the coordinator's explicit flag: the child had
  set `kind: detector` with the campus-geocode value and `confidence: uncertain` solely to
  satisfy the (pre-A23) validator placement rule, fully disclosed in its own note. After A23
  was added, the lead **reverted both to `kind: campus`** (the honest state) rather than
  keeping the `detector`-kind workaround, added a Wikipedia-sourced PHENIX-position note as
  corroboration only, and re-ran the validator to confirm no error remains.
- **Two dangling-source citations** (`src:bnl-rhic-rhic25-timeline`,
  `src:bnl-newsroom-final-run-2026`) that briefly did not exist in the atlas were checked;
  by the time of the lead's validator run they resolved cleanly (the equivalent pages had
  been fetched and filed by the concurrently-running `heavy-ions` lead under different source
  ids, `src:heavy-ions-rhic25-timeline` / `src:heavy-ions-rhic-final-collisions-2026`, and the
  child's citations matched those ids' actual content) — no fabrication found, just a
  transient shared-worktree race; no fix was needed.

No other children were spawned: repeated attempts for a second wave (SLAC+DESY,
JLab/ORNL/LANL/ANL/PSI) and a third (underground labs) all failed with
`Concurrent subagent limit reached (20 max)` (a cap shared across ~16 concurrent wave-3
leads). Per the coordinator's explicit instruction, the lead performed all remaining research
directly rather than continuing to retry for capacity.

## Dangling references to ids this lead does not own

None found pointing outward from this lead's own records (they reference only `facility:`,
`site:`, `accelerator:` and `src:` ids created in this same batch, or `topic:` ids that
already exist in `data/atlas/topics/topics.json`). Numerous *inbound* dangling references
from other leads' experiment/detector/collaboration files (e.g. `star.bnl.gov`-adjacent
detectors, SNOLAB/CJPL/LSC/LSM/Boulby/LNGS-hosted dark-matter and neutrino experiments) were
resolved by this batch landing; the validator run after this batch shows those `facilities`-
owned ids no longer dangling.

## Finishing checks

- `python -m hepgraph.atlas.validate`: **0 errors** attributable to any file this lead wrote
  or touched, confirmed by grepping the full error list for every facility/site/accelerator/
  source id above after each batch and again after the final batch (100 errors remain
  repo-wide, all in files this lead did not create — other leads' experiments, detectors and
  collaborations, actively being edited concurrently in this shared worktree).
- `python -m hepgraph.atlas.build`: **succeeds** (writes `static/atlas/generated/`,
  bundle version `82fe1715b2af402b`). The pre-existing "atlas.json + manifest.json over the
  400000-byte pilot budget" warning is a repo-wide, pre-existing condition unrelated to this
  batch.
- No `coverage/facilities.json` file was written (no experiments owned).
- No git commands were used; nothing outside `data/atlas/` and this file was touched.

## Confidence summary

- **Verified, rank ≤ 7, non-Wikipedia**: BNL founding/operator/RHIC/AGS facts (official BNL
  pages); DESY founding/operator (official `desy.de` page); LANL founding/operator (official
  `lanl.gov` page); ORNL operator and SNS beam-power figures (official `neutrons.ornl.gov/sns`
  page); JLab operator and CEBAF 6→12 GeV upgrade fact (official `jlab.org` pages); SNOLAB's
  underground-lab coordinate, vessel depth and water-equivalent shielding (the original SNO
  NIM A449 (2000) detector paper, rank 5); LSM's depth (1700 m) and founding (1981, official
  `lsm.in2p3.fr`); LSC's depth (800 m, official `lsc-canfranc.es`); Boulby's depth (1.1 km,
  official `boulby.stfc.ac.uk`); CJPL's depth figures (official `cjpl.tsinghua.edu.cn`
  pages); LNGS Hall A/C depth and coordinate (reused from the already-accepted Hall B
  pattern, official LNGS pages).
- **Uncertain/approximate, Wikipedia- or geocoder-only, explicitly flagged for review**: SLAC,
  PSI and Argonne almost entirely (official sites unreachable this session: TLS error, 404s,
  and 403 respectively); JLab's and ORNL's and LANL's and Argonne's founding/construction
  dates; PEP-II/SLC/HERA centre-of-mass energies and operating-date ranges; all campus-level
  coordinates for facilities where no official numeric coordinate was found (BNL upton/RHIC
  IPs, SLAC, DESY and its two halls, JLab, LANSCE, Argonne, PSI, SNOLAB's OSM fallback point
  — superseded by the SNO paper — LSM, LSC, CJPL-I/II, Boulby). None of these are presented
  as more certain than they are; every one carries a `note` saying so, per A17's rule that
  `confidence != verified` requires a note.
- **Left null with a note rather than guessed**: SNOLAB's own founding/opening year (the
  March 2011 "clean lab" date is Wikipedia-only and flagged, not treated as fully verified);
  CJPL-II's construction start/completion dates; CEBAF's original 6 GeV commissioning date;
  Neutrino Alley's precise setting/coordinate; Argonne's `topic_ids`.
