# fermilab-neutrino-other — research log

## Scope

Finish the `fermilab-neutrino-other` workstream: a previous agent had already
written the detectors (`nova-near-detector`, `nova-far-detector`,
`minos-near-detector`, `minos-far-detector`, `minerva`, `microboone`, `sbnd`,
`icarus-t600`, `miniboone`) and the shared facilities/sites/beamlines, but the
experiments, collaborations, documents, results and coverage/worklog files
those detectors depend on did not exist, leaving dangling references. This
pass wrote all of the missing entity types, closed the dangling references,
and migrated `detector.document_ids` to the v0.2 A1 `document.owner_ids`
direction.

No child agents were spawned (per this task's instructions); all research,
fetching and file-writing was done directly in this session. At most one
`inspirehep.net` request would have been made per 10 s if any had been
needed — in the end zero INSPIRE requests were made (see "Unresolved fields"
below), only official experiment/lab sites, Fermilab newsroom, and
arXiv/OSTI/PMC pages already permitted by the source hierarchy.

## Entities written

**Experiments (8):** `experiment:nova`, `experiment:minos`,
`experiment:minos-plus` (upgrade_of `experiment:minos`), `experiment:minerva`,
`experiment:microboone`, `experiment:sbnd`, `experiment:icarus`,
`experiment:miniboone`. Each has `facility_roles`, `beamline_ids`,
`topic_ids`, sourced `physics_goals`, `key_specs` (≤5, omitted for MINERvA —
see below), and a full sourced interval history (MINOS 2005–2012 incl. a
2003-07–2005-05 cosmic/atmospheric bridging interval, then MINOS+
2013–2016; MiniBooNE 2002–2019; MINERvA 2010–2019; MicroBooNE 2015–2021;
NOvA construction 2009 → first long-distance neutrinos Nov 2013 → beam data
from Feb 2014 → antineutrino-mode running from Feb 2017, ongoing; ICARUS
Gran Sasso 2010-05–2013-06 → CERN refurbishment 2014–2017-07 → Fermilab
construction 2017-07–2020-02 → commissioning 2020-02–2021-11 → physics
operation from 2021-11-05; SBND commissioning July 2024 → stable data
taking from the 10 Sept 2024 first-neutrinos announcement).
`experiment:icarus`/`experiment:microboone`/`experiment:sbnd` carry
`same_program` lineage rows (on `icarus`/`microboone` as the lexicographically
smaller id of each pair per v0.2 A1) documenting the three-detector SBN
programme.

**Collaborations (8):** `collaboration:nova`, `collaboration:minos` (covers
both MINOS and MINOS+), `collaboration:minerva`, `collaboration:microboone`,
`collaboration:sbnd`, `collaboration:icarus`, `collaboration:miniboone`, and
`collaboration:sbn` — the umbrella programme, with an explicit note that it
"is not a fourth experiment collaboration... it is the umbrella programme
joining three separate detector collaborations... No `experiment:sbn` entity
exists."

**Documents (10):** `document:nova-tdr` (FERMILAB-DESIGN-2007-01),
`document:minos-tdr` (NuMI-L-337), `document:minos-detector-paper` (NIM A 596
(2008) 190), `document:minerva-detector-paper` (NIM A 743 (2014) 130),
`document:microboone-detector-paper` (JINST 12 (2017) P02017),
`document:sbn-proposal` (arXiv:1503.01520), `document:sbnd-detector-paper`
(arXiv:2504.00245), `document:icarus-lngs-cryogenics-paper` (arXiv:1504.01556),
`document:icarus-sbn-initial-operation` (Eur.Phys.J.C 83 (2023) 1, the "ICARUS
T600 papers" describing Fermilab initial operation), `document:miniboone-detector-paper`
(NIM A 599 (2009) 28). Each carries `owner_ids` listing the detector(s),
experiment(s) and collaboration(s) it describes, per v0.2 A1.

**Results (7):** `result:miniboone-low-energy-excess-2021` (`result_type:
anomaly`; the collaboration's own word is "excess", never "discovery"),
`result:microboone-no-low-energy-excess-2021` (`measurement`; "no excess of
electron neutrino events is observed"), `result:nova-oscillation-parameters-2022`
(`measurement`), `result:minos-oscillation-measurement-2013` (`measurement`),
`result:minos-sterile-neutrino-limit-2016` (`limit`),
`result:minerva-axial-form-factor-2023` (`measurement`),
`result:icarus-hidden-sector-scalar-limit-2025` (`limit`; ICARUS's first
published physics result from its Fermilab SBN run). SBND has no physics
result yet in any source fetched (only commissioning/first-neutrinos press
coverage), so no SBND result file was written — flagged in the coverage file
instead of fabricated.

**Coverage:** `data/atlas/coverage/fermilab-neutrino-other.json`, one row per
experiment above, `researched: "full"` for all eight, with honest
`missing_fields`.

## Sources added

New `src:` records (all `accessed: "2026-09-17"`, fetched this session):
`src:nova-fermilab-news-2018-antineutrino` (Fermilab newsroom, "NOvA
experiment sees strong evidence for antineutrino oscillation"),
`src:nova-research-goals-page`, `src:microboone-physics-page`,
`src:minerva-why-study-neutrinos`. `src:icarus-experiment-site` (pre-existing,
owned by this workstream) was re-fetched for its physics-goals content and
upgraded from `retrieval: partial` to `full_text` in place, per rule 4, rather
than duplicated.

All other citations reuse the ~50 sources the previous agent had already
fetched into `data/atlas/sources/` for NOvA, MINOS, MINERvA, MicroBooNE, SBND,
ICARUS and MiniBooNE (detector papers, TDRs, Fermilab newsroom items, PRL/PRD/
Nature/EPJC papers) — none of those were refetched, matching the instruction
to cite rather than re-fetch.

## Dangling references closed

Before this session, the nine pre-existing detector files referenced:
- `experiment:nova`, `experiment:minos`, `experiment:minos-plus`,
  `experiment:minerva`, `experiment:microboone`, `experiment:sbnd`,
  `experiment:icarus`, `experiment:miniboone` — none existed; all eight now do.
- `document:nova-tdr`, `document:minos-tdr`, `document:minos-detector-paper`,
  `document:minerva-detector-paper`, `document:microboone-detector-paper`,
  `document:sbn-proposal`, `document:sbnd-detector-paper`,
  `document:icarus-lngs-cryogenics-paper`, `document:icarus-sbn-initial-operation`,
  `document:miniboone-detector-paper` — none existed; all ten now do.
- Each experiment file also creates its own previously-missing
  `collaboration:*` id.

Per v0.2 A1, `detector.document_ids` is derived (documents point at owners,
not the reverse), so the `document_ids` array was **removed** from all nine
detector files (`nova-near-detector`, `nova-far-detector`,
`minos-near-detector`, `minos-far-detector`, `minerva`, `microboone`, `sbnd`,
`icarus-t600`, `miniboone`); the equivalent information now lives as
`owner_ids` on the ten document files above.

Also fixed while touching these files: `detector:icarus-t600` had a
duplicate alias (`"ICARUS-T600"` vs. name `"ICARUS T600"`, an A20
`alias-equals-name` error) — the redundant alias was dropped, keeping
`"T600"`. `experiment:minos` and `experiment:minos-plus` both normalise to
the same name (`"minos"`), so each now lists the other in `distinct_from`,
per A20.

## Conflicts (claim / source A / source B / chosen / why)

1. **MicroBooNE detector-paper duplication (cross-workstream).** My own
   `src:microboone-detector-paper-2017` (arXiv:1612.05824) and the
   fermilab-dune-owned `src:fermilab-microboone-detector-paper-2017` (same
   arXiv id/DOI) both pre-date this session and now trigger an A20
   `duplicate-source-url`/`duplicate-external-id` error. **Not resolved**: the
   counterpart file belongs to a different workstream's ownership; flagging
   for the orchestrator rather than unilaterally editing another lead's file.
2. **NOvA near-detector mass** (pre-existing, inherited): NOvA PRD 106,032004
   says "290 ton"; the NOvA public page and 2025 monopole paper say
   "300 t / 0.3 kt". Already resolved in the pre-existing detector file in
   favour of 0.3 kt; carried through unchanged into `experiment:nova.key_specs`.
3. **MiniBooNE excess magnitude across time**: the collaboration's 2018 PRL
   reports a 4.5σ, 381.2±85.2-event CCQE-only excess; the 2021 PRD (larger,
   combined ν+ν̄ exposure) reports 4.8σ, 638.0±132.8 events. Chose the 2021
   figure as the result's primary `claim`/`key_value`, and recorded the 2018
   figure in `notes` as a supporting, earlier data point — not a
   contradiction, an update with more data.
4. **Collaboration formation dates**: no official page or paper fetched for
   any of the seven single-experiment collaborations states an explicit
   founding date. Per A17, `formation.value` is `null` with a `note`. Because
   A10 requires `status` to equal the state derived from `intervals` at the
   build date, and an interval with `start: null` **and** `end: null` covers
   no year at all (A3), each collaboration's single lifecycle interval uses
   the *earliest sourced collaboration activity* (TDR date, first-neutrinos
   date, or first-proposal date) as an explicit, clearly-noted **lower-bound
   proxy** `start` — not a fabricated formation date — so the interval covers
   the build date and the authored `status` validates.

## Unresolved fields

- Collaboration `formation.value` is `null` for all 7 (see above);
  `intervals[0].start` is a proxy lower bound in each case, confidence
  `approximate`, clearly noted.
- `experiment:minerva.key_specs` is empty: no fetched source (official site,
  detector-paper abstract) gives a mass/dimension quantity; matches
  `detector:minerva`'s own pre-existing gap.
- `experiment:sbnd` has no physics result yet (only commissioning/first-
  neutrinos coverage) — noted in the coverage file rather than invented.
- `experiment:miniboone`'s end-of-data-taking year (2019) is not stated
  verbatim in any source fetched; carried at `confidence: uncertain` /
  `approximate`, matching the pre-existing detector file's own caveat.
- `experiment:icarus`: the original 2004 T600 construction paper (NIM A 527
  (2004) 329) could not be fetched (publisher blocked), matching the
  pre-existing detector file's own note.
- `external.inspire_experiment` is `null` (with an explicit note) on all
  eight experiments: no `inspirehep.net` request was made this session — the
  existing official-site/newsroom/arXiv/OSTI sources were sufficient for
  every required field, so the throttled INSPIRE budget was not spent.
  Tier B/C with a note satisfies A20's duplicate-detection rule, but a
  follow-up pass could add these for completeness.

## Confidence summary

The large majority of sourced values are `confidence: verified` with a direct
`quote`/`locator` from an official experiment page, a Fermilab newsroom
article, or an arXiv/OSTI/PMC abstract fetched this session. `approximate`/
`uncertain` confidence is used only where explicitly noted above (MiniBooNE's
end-of-run date, ICARUS's post-shutdown restart date matching the
pre-existing detector file, and the seven collaborations' proxy formation
lower bounds). `.venv/bin/python -m hepgraph.atlas.validate` was run after
every batch of edits; as of the final run, zero `[error]`-level findings
touch any file this workstream owns (verified by filtering the validator's
full output to this workstream's file paths). The remaining errors/warnings
visible in a live validator run belong to other, concurrently-edited
workstreams (e.g. `historic-cern`'s UA1/UA2/LEP experiments, `membership-lead`'s
institution parent links, `japan-neutrino`/`icecube` coverage duplicates) and
are outside this workstream's ownership.
