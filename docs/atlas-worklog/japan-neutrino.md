# japan-neutrino workstream — research log

## Scope

Completed the remainder of the japan-neutrino workstream (a prior agent had already
written `facility:j-parc`, `facility:kek`, `facility:kamioka-observatory`, the J-PARC
and KEK accelerators/beamlines, the two Kamioka sites, and a large set of `src:t2k-*`,
`src:sk-*`, `src:jparc-*`, `src:kek-*`, `src:k2k-*`, `src:hk-*` sources). This pass
wrote: T2K (experiment, collaboration, ND280, INGRID), K2K (experiment, collaboration),
Kamiokande (experiment), Super-Kamiokande (experiment, detector, collaboration),
Hyper-Kamiokande (experiment, detector, collaboration), 8 results, 4 documents, the
coverage registry row and this log. All critical values are sourced values citing
sources fetched with WebFetch in this session (`verified_at: 2026-09-17`); nothing
was taken from model memory.

## Entities written

- `experiment:t2k`, `collaboration:t2k`, `detector:nd280`, `detector:ingrid`
- `experiment:k2k`, `collaboration:k2k`
- `experiment:kamiokande`
- `experiment:super-kamiokande`, `detector:super-kamiokande`, `collaboration:super-kamiokande`
- `experiment:hyper-kamiokande`, `detector:hyper-kamiokande`, `collaboration:hyper-kamiokande`
- Lineage: `experiment:super-kamiokande` → predecessor `experiment:kamiokande`;
  `experiment:hyper-kamiokande` → predecessor `experiment:super-kamiokande`;
  `experiment:t2k` → predecessor `experiment:k2k` (all recorded once, on the later
  entity, as instructed).
- Results: `result:kamiokande-sn1987a-1987`, `result:sk-atmospheric-oscillation-evidence-1998`,
  `result:k2k-oscillation-measurement-2006`, `result:t2k-electron-neutrino-indication-2011`,
  `result:t2k-electron-neutrino-appearance-observation-2014`,
  `result:t2k-cp-violation-constraint-2020`, `result:sk-solar-neutrino-measurement-2024`,
  `result:sk-gd-first-antineutrino-search-2023`.
- Documents: `document:t2k-nim-2011`, `document:t2k-nd280-upgrade-tdr-2019`,
  `document:sk-nim-2003`, `document:hk-design-report-2018`.
- `data/atlas/coverage/japan-neutrino.json` (5 rows: T2K, K2K, Kamiokande,
  Super-Kamiokande, Hyper-Kamiokande).
- Extended (not recreated) `facility:kamioka-observatory` with one clarifying note
  about its 1995 founding date vs. the mine's much earlier scientific use (see
  Conflicts).

Also fixed at the coordinator's request after the pilot-acceptance gate flagged it:
added `experiment:t2k` (and `experiment:k2k`) to `detector:super-kamiokande.experiment_ids`
and `experiment:t2k` to `detector:hyper-kamiokande.experiment_ids`, since the same
physical detector serves as the far detector for the accelerator-neutrino
experiments as well as running its own programme; trimmed `experiment:t2k`'s
`summary.plain` from 68 to 55 words.

## Sources added

New: `src:sk-kamiokande-sn1987a-prl-1987` was created, then deleted once the
pre-existing (unprefixed) `src:kamiokande-prl-1987-sn1987a` and
`src:kamiokande-inspire-experiment` were discovered already in the repository
(evidently written by whichever earlier agent pass ran out of budget) and reused
instead — see Conflicts. `experiment:kamiokande.external.inspire_experiment` is now
set to 1110455 via `src:kamiokande-inspire-experiment`.

All other citations reuse the already-fetched `src:t2k-*`, `src:sk-*`, `src:k2k-*`,
`src:hk-*`, `src:jparc-*` records named in the task brief; each was re-opened with
WebFetch in this session (several PDF sources — `sk-nim-2003`, the T2K NIM PDF via
its direct URL, the HK PoS ICRC2021 proceedings PDF — could not be extracted as
text by the fetch tool; official HTML pages and the ar5iv HTML rendering of the two
arXiv PDFs (`t2k-nim-2011`, `t2k-status-2011-arxiv`) were used instead and are noted
where they substitute for a PDF that would not render).

`accessed` was bumped to 2026-09-17 on the source files actually re-fetched in this
session (the `t2k-inspire-experiment`, `k2k-inspire-experiment`, `sk-inspire-experiment`,
`hk-inspire-experiment`, `kamiokande-inspire-experiment` records also had their `url`
corrected from the INSPIRE `/api/experiments/<recid>` endpoint to the bare
`/experiments/<recid>` page, which is what the validator's external-id-source check
and a human reader both expect).

## Conflicts (claim / source A / source B / chosen / why)

1. **SN1987A source duplication.** A source `src:kamiokande-prl-1987-sn1987a` (and
   `src:kamiokande-inspire-experiment`) already existed, unused, evidently left by an
   earlier, budget-exhausted pass at this exact task — but without the `sk-`/prefix
   convention this workstream otherwise uses. I initially fetched the paper fresh via
   the INSPIRE literature API and wrote a new, redundantly-prefixed source, which the
   validator correctly flagged as a duplicate DOI. Chose to delete my new source and
   cite the pre-existing one instead (it has a materially better excerpt: the exact
   burst time, "23 February, 7:35:35 UT (+-1 min), 13 sec duration"), per rule 4
   (reuse a source with the same DOI/URL rather than duplicating).
2. **T2K institution/member counts.** `t2k-experiment.org/t2k/collaboration/` states
   "about 560 members from 75 institutes in 14 countries and CERN"; the separate
   `t2k-experiment.org/t2k/institutes/` page instead lists ~90 currently-participating
   institutions (plus 14 past) across ~18 countries. Neither page is dated. Chose the
   collaboration page's aggregate as the primary sourced value (closer to an official
   "about us" summary) and recorded the institutes-page figures as a conflict note on
   `collaboration:t2k.membership`, with `confidence: approximate`.
3. **Hyper-Kamiokande fiducial mass.** The outline-page comparison table gives
   "260000 ton (190000 ton)" (190 kt fiducial); the 2024 Frontiers in Physics status
   article gives "0.260 million metric tons" total and "0.188 million metric tons"
   fiducial (188 kt). Chose 188 kt (matches the task brief and the more precise,
   citable journal article) and recorded the 190 kt outline-table figure as an
   unreconciled conflict on both `experiment:hyper-kamiokande.key_specs` and
   `detector:hyper-kamiokande.specs.fiducial_mass`.
4. **Hyper-Kamiokande PMT count.** The same official outline-page table gives
   "50cm diameter / about 40000" for Hyper-Kamiokande, while the outline page's own
   prose elsewhere states "20,000 ultra high sensitivity photosensors and 1,000
   compound eye photosensors". These are two different numbers on the same official
   site with no way to reconcile them from what was fetched. Chose 20,000 (a specific
   sensor count, not qualified as a design maximum, and matching the task brief's
   "~20,000 PMTs") as the primary value; recorded 40,000 as an explicit, unresolved
   conflict in both the experiment and detector records and in
   `coverage/japan-neutrino.json`.
5. **Hyper-Kamiokande planned start of operation.** The 2020 approval press release
   and T2K's own "T2K and beyond" page project 2027; the current (2026) official
   outline page instead says "aims to start experimentation in 2028". Recorded as a
   Date with `earliest: "2027"`, `latest: "2028"`, `display: "2028"`, `planned: true`,
   rather than silently picking one.
6. **Kamioka Observatory founding vs. Kamiokande/Super-K construction dates.** The
   facility record (written by an earlier pass) dates the "Kamioka Observatory" to
   1995, but Kamiokande began taking data in 1983 and Super-Kamiokande's cavity
   excavation began December 1991 — both years before that founding date. Added a
   note to `facility:kamioka-observatory` clarifying that 1995 is when the named
   administrative facility was established, not when underground physics began at
   the site, so the resulting `experiment-before-facility` validator warning is
   explained rather than silent (this does not change any sourced date on either
   experiment record).
7. **T2K's own two "predecessor" collaboration names.** `t2k-experiment.org`'s
   collaboration page states a smaller, differently-named collaboration formed in
   2002 and was "expanded, and launched using the name 'T2K'" in 2006; no source
   fetched gives the 2002 name. Recorded both years as separate intervals on
   `collaboration:t2k` rather than collapsing to one formation date.

## Unresolved fields (recorded as `null` + note, or otherwise flagged)

- `experiment:kamiokande`: exact end/decommissioning date (no source states one;
  the Kamiokande-II interval is left open, `status: completed`, `end: null`,
  `confidence: uncertain`, per the terminal-status-without-end exception).
  `collaboration:kamiokande` was deliberately not created (ID_REGISTRY assigns only
  the experiment id to this workstream, and no source separates a distinct
  Kamiokande collaboration/roster from Super-Kamiokande's).
- `detector:ingrid`: module count, per-module mass, iron/scintillator layer counts —
  not published in the T2K experiment paper (NIM A 659) as fetched; a dedicated
  INGRID instrumentation paper was not retrieved in this session.
- `detector:nd280`: total/per-subsystem mass not found in the sources fetched.
- `collaboration:k2k`: institution/member/country counts — no source fetched
  publishes numeric totals for K2K (only the qualitative "Japan-Korea-US" wording).
  Collaboration formation date is also unresolved (only the 1999 start of data
  taking is sourced).
- `experiment:t2k`: no source distinguishes a formal "approved" milestone from the
  INSPIRE record's bare "proposed" metadata field (2001-06-13, recorded at
  `confidence: approximate` since it comes from a paraphrased API field rather than
  continuous prose); the exact 2013 J-PARC hadron-hall radiation-accident shutdown
  start date is likewise only approximately back-computed from the known 26 May
  2014 resumption date and a stated "1-year shutdown".
- Two SK PMT figures from the detector paper (NIM A 501, 2003) could not be
  extracted — the fetch tool could not read that PDF as text in this session — so
  `detector:super-kamiokande.specs.pmt_count` cites the official detector page
  instead (11,129), cross-checked against the INSPIRE record's rounder "11,200".

## Confidence summary

Most interval bounds, key specs, and result claims are `confidence: verified` with
a direct quote from an official page or the paper's own title/abstract. Lower
confidence (`approximate`/`uncertain`) is used, with a note in every case, for: the
T2K/K2K "proposed"/formation dates drawn from paraphrased INSPIRE-API fields rather
than prose; the Hyper-Kamiokande PMT count and fiducial mass (conflicting official
figures, see Conflicts #3–4); the 2013 T2K shutdown start date (back-computed); and
Kamiokande's and K2K's open-ended terminal intervals (no sourced end date). No date,
coordinate, mass, or PMT count was taken from memory; every quantity in `key_specs`
and every detector `specs` entry carries a `quote` or `locator` per A15.

## Validator / test status

`.venv/bin/python -m hepgraph.atlas.validate`: zero errors remain in files owned by
this workstream, except one pre-existing `load` error —
`coverage/japan-neutrino.json: duplicate coverage row for 'experiment:k2k'` — caused
by a stale, `owner: null`, `researched: "none"` placeholder row for K2K already
present in the orchestrator-owned `data/atlas/coverage/backlog.json` (seeded before
this workstream researched K2K). This is not edited here, following the same
precedent already visible in the repository: `coverage/icecube.json` has an
identical unresolved duplicate against `backlog.json`'s `experiment:icecube-gen2`
row, and `coverage/historic-cern.json` has the same duplicate for ALEPH/DELPHI/L3/
OPAL — all are backlog-reconciliation issues for the orchestrator, not something an
individual workstream file should resolve by editing another workstream's file.

`.venv/bin/python -m pytest tests/test_atlas_pilot_acceptance.py -q`: 16 passed,
1 skipped (people not yet ingested); all T2K assertions
(`test_t2k_runs_from_jparc_to_kamioka`, `test_t2k_baseline_is_recorded_with_a_source`,
`test_t2k_has_timeline_results_and_documents`,
`test_every_pilot_experiment_can_be_summarised_for_a_newcomer`) pass.
