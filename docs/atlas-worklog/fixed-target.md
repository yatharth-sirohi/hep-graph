# fixed-target workstream worklog (Wave 3, v1.0)

## Scope

All 10 experiments in `data/atlas/coverage/fixed-target.json`: NA62 (flagship,
full depth), NA48, NA64, KTeV, SeaQuest, DarkQuest, SHiP, MATHUSLA, E949, KOTO.
Delegation to child agents was attempted per the brief's four-group split
(NA62+NA48; NA64+SHiP+MATHUSLA; KTeV+SeaQuest/DarkQuest; E949+KOTO), but the
Agent tool returned "Concurrent subagent limit reached" for every spawn
attempt except the very first (NA62+NA48), which itself hit the limit twice
before succeeding once, and none of the intended second-wave children (for
NA64/SHiP/MATHUSLA, KTeV/SeaQuest/DarkQuest, or E949/KOTO) could be spawned at
all. Per the orchestrator's mid-task correction, all research for the
remaining eight experiments was performed directly by this lead agent,
sequentially, rather than through further retries. No git commands were used.
No further subagents were spawned after the orchestrator's correction.

## Entities written

- `experiments/`: na62, na48, na64, ktev, seaquest, darkquest, ship, mathusla,
  e949, koto (10/10).
- `detectors/`: na62, na48, na64, ktev, seaquest, ship, e949, koto (8; no
  separate detector file for mathusla — no sourced placement — or darkquest —
  reuses the SeaQuest/SpinQuest apparatus, no distinct hardware sourced).
- `collaborations/`: na62, na48, na64, ktev, seaquest, ship, mathusla, e949,
  koto (9; no `collaboration:darkquest` — no source names a distinct DarkQuest
  collaboration separate from the SeaQuest/SpinQuest proponents).
- `sites/`: `site:cern-ecn3-north-area` (new; shared by na48, na62, ship),
  `site:fermilab-ktev-hall` (new), `site:fermilab-nm4-hall` (new; shared by
  seaquest and darkquest). Referenced without creating:
  `site:cern-neutrino-platform-ehn1` (na64, dune-owned),
  `site:bnl-upton-campus` (e949, facilities-owned),
  `site:j-parc-hadron-hall` (koto, muons-owned — already existed when this
  record was written, so not a dangling reference in practice).
- `documents/`: `document:na62-detector-jinst-2017` (owner_ids
  experiment/detector/collaboration:na62).
- `results/`: `result:na62-jhep-2021-measurement`,
  `result:na62-jhep-2025-observation`, `result:na62-2026-refined-measurement`
  (the third is a bonus, sourced only to a CERN news article about a
  conference talk, not a peer-reviewed paper — flagged accordingly).
- `sources/`: 33 new `src:` records, prefixed by experiment slug (`na62-*`,
  `na48-*`, `na64-*`, `ktev-*`, `seaquest-*`, `darkquest-*`, `ship-*`,
  `mathusla-*`, `e949-*`, `koto-*`). Full list: na62-official-site,
  na62-aim-page, na62-detector-jinst-2017, na62-gigatracker-arxiv-2019,
  na62-jhep-2021-measurement, na62-jhep-2025-observation,
  na62-cern-news-2026-refined-measurement,
  na62-collaboration-organisational-structure, na62-inspire-experiment-record,
  na62-cern-north-area-page, na48-cern-courier-fixed-target,
  na48-final-epsilon-prime-arxiv-2002, na48-kaon-experiments-arxiv-2011,
  na48-inspire-experiment-record, na64-official-site,
  na64-home-cern-experiments-page, na64-inspire-experiment-record,
  ship-official-site, ship-cern-courier-2016-spsc, ship-wikipedia-pointer,
  ship-inspire-experiment-record, mathusla-official-site,
  mathusla-inspire-experiment-record, ktev-design-report-1992,
  ktev-inspire-e832, ktev-inspire-e799, ktev-1999-cp-violation-conference,
  seaquest-spectrometer-arxiv-2017, seaquest-final-results-arxiv-2025,
  seaquest-inspire-experiment-record, seaquest-wikipedia-pointer,
  darkquest-proposal-arxiv-2022, e949-inspire-experiment-record,
  e949-first-year-physics-run-2004, e949-from-e787-to-e949-2001,
  e949-e787-combined-result-arxiv-2009, koto-official-site,
  koto-inspire-experiment-record.

## Per-experiment researched state / missing_fields

See `data/atlas/coverage/fixed-target.json` for the authoritative row per
experiment (reproduced in summary): NA62 `full`; NA48, NA64, KTeV, SeaQuest,
DarkQuest, SHiP, MATHUSLA, E949, KOTO all `partial`. Each row lists its own
`missing_fields` honestly (membership counts, exact run-year boundaries not
independently confirmed this session, etc. — see the file for the per-
experiment detail rather than duplicating it here).

## Conflicts

| claim | source A | source B | chosen | why |
| --- | --- | --- | --- | --- |
| NA48 main-run data-taking years | CERN Courier-style secondary aggregation encountered mid-search ("1997, 1998, 1999 and 2000") | arXiv:hep-ex/0209064, the NA48 collaboration's own final epsilon'/epsilon paper, directly fetched ("1997, 1998, 1999 and 2001") | 1997-2001, per source B | Source B is the collaboration's own primary publication, directly fetched with a verbatim quote; source A was a search-engine paraphrase, not a page I fetched and quoted. |
| DarkQuest's "upgrade of" relation | Brief/ID_REGISTRY frame it as a successor to SeaQuest | The only source found (arXiv:2203.08322) titles DarkQuest a "dark sector upgrade to SpinQuest" (an intermediate spin-physics reuse of the SeaQuest spectrometer, E1039, out of this wave's scope) | `lineage: upgrade_of -> experiment:seaquest` recorded anyway, with a note flagging the SpinQuest simplification | SpinQuest has no record in this wave and creating one was out of scope; recording the lineage against experiment:seaquest (the id this workstream owns) is the closest honest approximation, clearly caveated. |
| SHiP's beam-dump site history | ID_REGISTRY/brief say SHiP was originally proposed for a different site before the 2020 European Strategy review moved it to ECN3 (per Wikipedia) | ship.web.cern.ch (official, current) only describes the current ECN3-era plan | Recorded only the ECN3 placement (current), with the pre-2020 site history mentioned in no entity field (not a sourced, actionable fact for this pass) | Avoided asserting an un-fetched historical detail; only what was directly confirmed is recorded. |

## Unresolved fields

- NA48/1 (2002) as a separate dated interval: only found via an unconfirmed
  secondary search aggregation, not a directly fetched primary source; not
  asserted as its own interval.
- KTeV and E949 exact calendar run-year breakdowns (commonly cited elsewhere
  as 1996-1997/1999-2000 for KTeV and 2002 for E949): not independently
  confirmed by any source fetched this session; left unrecorded rather than
  guessed.
- SeaQuest exact data-taking start/end years: same treatment — only bounded by
  the 2017 spectrometer paper and the December 2025 "final results" paper.
- SHiP's 2024 approval date and 2033 planned start: sourced only to a
  Wikipedia pointer (rank 12); the WebSearch tool's session budget was
  exhausted (200/200) before a rank <= 10 CERN Council/SPSC document could be
  located to corroborate it. Flagged `confidence: uncertain` throughout.
  Recommended follow-up: fetch a CERN Research Board/Council record directly.
- MATHUSLA's precise CERN placement (e.g. whether it is sited at Point 5/CMS):
  the official site says only "near ATLAS and CMS" on the surface, without
  naming an interaction point; no site record or placement was created rather
  than guessing.
- KOTO's February 2025 PRL result (from 2021 data): the official site
  confirms the headline fact and a supporting quote, but no `results/` file
  was written because the exact `result_type` (measurement vs. limit) and
  significance could not be confirmed by a source fetched this session.
- No collaboration membership counts (institutions/countries/members) were
  found for ANY of the 10 experiments' own official pages in this session;
  all left `null` with a note rather than estimated from third-party
  aggregations or author-affiliation lists (per rule 4: never claim
  membership from institutional affiliation).

## Children spawned and what was re-checked

One child agent was successfully spawned (NA62+NA48, model `sonnet`,
`subagent_type: general-purpose`) but it also hit "Concurrent subagent limit
reached" on its first two launch attempts; the third attempt succeeded and
the child began work. Before the child's work could be reviewed, the
orchestrator's session-limit reset message indicated NA62/NA48/NA64 already
existed on disk with coverage rows still marked `none` — i.e., a prior attempt
(from before the reported session interruption) had written the na62, na48
and na64 entity files but not yet updated the coverage rows or worklog. This
lead re-verified every one of those pre-existing files against this session's
own re-fetch of the same primary sources (na62.web.cern.ch, the JINST/JHEP
arXiv abstracts, the CERN North Area experimental-areas page, the INSPIRE
experiment API) before building on them, and fixed a round of validator
errors found in them (missing `coverage` blocks, a missing top-level
`sources` array on `experiments/na62.json`, an INSPIRE source URL that did
not literally contain `inspirehep.net/experiments/<recid>`, a `quote` resting
on a `summary`-retrieval source, `confidence: verified` values backed only by
a rank-12 source, and a display/value unit mismatch on the GigaTracker timing
spec). No other children were spawned after the orchestrator's "do not spawn
children" instruction; all research for NA64 (verification only, since it
already existed), KTeV, SeaQuest, DarkQuest, SHiP, MATHUSLA, E949 and KOTO was
performed directly by this lead agent using WebFetch/WebSearch, with every
critical claim cited to a source fetched in this session.

## Dangling references to ids another lead owns

None outstanding. Every non-owned id referenced (`facility:cern`,
`accelerator:sps`, `facility:fermilab`, `accelerator:fermilab-tevatron`,
`accelerator:fermilab-main-injector`, `site:fermilab-main-campus`,
`facility:brookhaven-national-laboratory`, `site:bnl-upton-campus`,
`accelerator:ags`, `facility:j-parc`, `accelerator:j-parc-main-ring`,
`site:j-parc-hadron-hall`, `site:cern-neutrino-platform-ehn1`,
`accelerator:lhc`) already existed on disk at the time each referencing file
was written, confirmed via `ls`/`cat` before use. The validator's
`dangling-reference` findings (11 total) are all attributable to other
workstreams (reactor-solar-neutrino's `facility:chooz`, cosmic-gamma's HESS/
VERITAS collaboration ids, membership-lead's one unresolved person id) — none
are this workstream's.

## Confidence summary

- **High confidence (verified, rank <= 10 primary sources, direct quotes):**
  NA62's full run history, both mandatory 2021/2025 results (verbatim titles
  and significance confirmed by directly fetching the arXiv abstract pages),
  the NA62 detector paper and GigaTracker timing spec, NA48's 1997-2001 run
  and NA48/2 2003-2004 sub-run, NA64's proposal/approval dates and H4-in-EHN1
  citation, KOTO's run history (all directly quoted from koto.kek.jp).
- **Medium confidence (sourced but rank-12-only or otherwise flagged
  `approximate`/`uncertain`):** NA48's facility-role/approval interval (CERN
  Courier only), SHiP's 2024 approval and 2033 start (Wikipedia only), KTeV's
  and SeaQuest's and E949's exact run-year boundaries, MATHUSLA's entire
  timeline, DarkQuest's lineage relation to SeaQuest (actually sourced as an
  upgrade to SpinQuest).
  All site coordinates for `cern-ecn3-north-area`, `fermilab-ktev-hall` and
  `fermilab-nm4-hall` are honestly campus/facility-level approximations
  (`confidence: uncertain`, large `precision_m`), following the same pattern
  already established by `site:cern-neutrino-platform-ehn1` and
  `site:fermilab-main-campus` — no precise coordinate was invented for any of
  them.
- **Explicitly unresolved (`null` + note, not guessed):** all 10
  collaborations' membership counts; several exact run-year boundaries (see
  "Unresolved fields" above); MATHUSLA's overall entity `status` (left `null`
  because no interval has a non-planned start date covering the present, so
  the A10-derived state is genuinely unrecorded — recording any non-null
  status would have been unsupported).

`.venv/bin/python -m hepgraph.atlas.validate` reports 0 errors attributable to
this workstream's files (verified by re-running after every fix round); the
remaining warnings on this workstream's files (`sites-too-close` from reusing
honest campus-level coordinates, `interval-start-unknown` on genuinely undated
starts, one `unknown-spec-key` for the GigaTracker timing spec, which has no
Appendix A entry for the `spectrometer` technology class) are expected
consequences of honest sourcing, not defects.
`.venv/bin/python -m hepgraph.atlas.build` succeeds.
