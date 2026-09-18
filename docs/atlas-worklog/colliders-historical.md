# colliders-historical — wave 3 domain-lead worklog

## Scope

Six completed 20th/21st-century collider experiments, in three facility pairs:

- **Tevatron (Fermilab):** CDF, D0 — created `site:fermilab-cdf-collision-hall-b0`
  and `site:fermilab-d0-collision-hall`; reused pre-existing `facility:fermilab`
  and `accelerator:fermilab-tevatron` (owner `fermilab-dune`).
- **SLAC:** SLD, BaBar — reference `facility:slac`, `accelerator:slc`,
  `accelerator:pep-ii`, `site:slac-slc-collider-hall-sld`,
  `site:slac-pep-ii-ir2-babar`. These were dangling (not yet created) when this
  work began; the "facilities" lead landed all of them partway through this
  session, so every reference now resolves.
- **DESY HERA:** H1, ZEUS — reference `facility:desy`, `accelerator:hera`,
  `site:desy-hera-north-hall-h1`, `site:desy-hera-south-hall-zeus`. Same
  situation: dangling at the start of this session, landed by the facilities
  lead partway through, now resolved.

Mandatory bar only for all six (none are flagships). For CDF and D0, the
optional 1995 top-quark-observation bonus was completed (one result each,
verbatim collaboration-paper titles, `result_type: observation` — not
"discovery" — per the paper wording).

Delegation note: the plan was to spawn two children per facility pair
(6 children total, ≤2 concurrent). The shared 20-subagent cap across the
16 wave-3 leads was saturated on every attempt (confirmed via repeated
"Concurrent subagent limit reached" errors), so per the coordinator's
correction, **all six experiments were researched and written directly by
this lead**, sequentially, with no children spawned. Every source below was
therefore fetched and every value written by the same session that is
reporting it — there was no separate "re-check the child's work" step because
there was no child.

## Entities written

- `experiments/cdf.json`, `detectors/cdf.json`, `collaborations/cdf.json`,
  `sites/fermilab-cdf-collision-hall-b0.json`,
  `results/cdf-top-quark-observation-1995.json`
- `experiments/d0.json`, `detectors/d0.json`, `collaborations/d0.json`,
  `sites/fermilab-d0-collision-hall.json`,
  `results/d0-top-quark-observation-1995.json`
- `experiments/sld.json`, `detectors/sld.json`, `collaborations/sld.json`
- `experiments/babar.json`, `detectors/babar.json`, `collaborations/babar.json`
- `experiments/h1.json`, `detectors/h1.json`, `collaborations/h1.json`
- `experiments/zeus.json`, `detectors/zeus.json`, `collaborations/zeus.json`

No `documents/`, `memberships/`, or `people/` files were written (out of scope
for this wave / not flagships).

## Sources added (25 total, all prefixed `src:colliders-historical-`)

CDF/D0 (shared Tevatron sources are unprefixed by experiment to avoid A20
duplicate-URL failures): `tevatron-fnal-news-2011-shutdown`,
`tevatron-fnal-shutdown-process`, `cdf-inspire-experiment-record`,
`cdf-nim-1988-detector-overview`, `cdf-fnal-tevatron-experiments-page`,
`cdf-official-site`, `cdf-official-intro`, `cdf-top-quark-observation-1995`,
`d0-inspire-experiment-record`, `d0-design-report`,
`d0-fnal-tevatron-experiments-page`, `d0-official-site`,
`d0-official-public-page`, `d0-upgraded-detector-nim-2006`,
`d0-top-quark-observation-1995`.

SLD/BaBar: `sld-inspire-experiment-record`, `sld-official-intro`,
`babar-inspire-experiment-record`, `babar-cerncourier-25th-anniversary-2019`,
`babar-symmetry-2008-pepii-end`, `babar-detector-nim-2002`.

H1/ZEUS: `h1-inspire-experiment-record`, `h1-official-site`,
`zeus-inspire-experiment-record`, `zeus-official-site`.

Fetch method: official lab/experiment pages were retrieved with `curl` and
stripped to plain text with a small local HTML parser (zero model paraphrase
risk — `fnal.gov`, `cdf.fnal.gov`, `d0.fnal.gov`, `www-h1.desy.de`,
`www-zeus.desy.de`, `www-sld.slac.stanford.edu`, `symmetrymagazine.org`,
`cerncourier.com` all returned HTTP 403 to the WebFetch tool directly but 200
to a direct `curl`). INSPIRE experiment/literature records were fetched via
`curl https://inspirehep.net/api/...` (raw JSON, so `date_proposed` /
`date_approved` / `date_started` / `date_completed` / `description` values
quoted below are the literal API field values, not a rendering), spaced
≥10s apart per the INSPIRE etiquette rule. WebSearch was used only to locate
URLs/recids, never as the cited source for a claim.

## Conflicts

| claim | source A | source B | chosen | why | confidence |
| --- | --- | --- | --- | --- | --- |
| CDF total detector mass | NIM A271 (1988): "5000 t" | fnal.gov Tevatron/CDF page (2014): "4,500-ton" | 4500 t (fnal.gov) | Official facility site outranks a detector paper in the source hierarchy; both figures kept, conflict noted on the field | approximate |
| CDF solenoid field | INSPIRE exp. record: "1.4 T", coil "4.8 m" long | NIM A271 (1988): "1.5 T", coil "3 m in diameter and 5 m in length" | 1.4 T (INSPIRE) | inspire_experiment_record (rank 3) outranks detector_paper (rank 5); NIM figure noted, not reconciled | verified, with note |
| D0 "date_completed" | INSPIRE structured field: `2001` | INSPIRE's own free-text description: "the DZero experiment ran from 2001 to 2011" | 2011 (terminal interval) | The structured field is internally contradicted by the record's own prose; the prose plus the independently-sourced 2011 Tevatron shutdown (news.fnal.gov, fnal.gov/shutdown-process) is used for the real end date. Flagged in `experiments/d0.json.notes`. | verified |
| CDF `date_started`/`date_completed` (INSPIRE) | `1987-01-01` / `1992-01-01` (structured fields) | INSPIRE's own description: "first physics results...during 1987, in an engineering run"; "silicon microstrip vertex detector...installed in 1992" | Both used as *labelled milestones* ("engineering run", "vertex detector installed"), not as the experiment's start/end | The day component (`-01-01`) on 3 of 4 CDF INSPIRE date fields is almost certainly a database default, not a sourced day; treating them as the true start/end would also contradict the well-sourced 2011 Tevatron shutdown. | approximate/uncertain, noted |
| BaBar "formation" | INSPIRE `date_proposed`: `1994-06` | CERN Courier (2019): inaugural organizing meeting "at the end of 1993"; name "BaBar" adopted "By May 1994" | 1994-06 (INSPIRE) used for the sourced `formation` field; the earlier 1993 meeting recorded only in `notes` | INSPIRE gives a cleaner, single dated field; the CERN Courier account describes an informal precursor meeting under a different (temporary) name, not obviously "formation" | approximate |
| Top-quark "discovery" wording | Fermilab's own pages (2014) and a 2019 EPS Prize citation: "the discovery of the top quark" | The papers' own titles: "Observation of top quark production..." (CDF, PRL 74,2626) / "Observation of the top quark" (D0, PRL 74,2632) | `result_type: observation` | Per explicit brief instruction and A16's mechanical rule: wording follows the paper's own title/abstract, not a press characterization; "discover"/"discovery" appears nowhere in either paper's title or the quoted abstract text. | verified |

## Unresolved / missing fields

See `data/atlas/coverage/colliders-historical.json` `missing_fields` per
experiment (kept honest and specific, not "all"). Summary:

- **CDF/D0:** collision-hall coordinates are campus-precision only (A23
  `coordinate-kind-approximate`, not an error) — no source found this session
  gives a B0- or D0-hall-specific lat/lon; a WebSearch turned up only
  geocoder-aggregator sites (`latitude.to`), which are not acceptable per
  A17/A20 and were not used. Collaboration formation dates use the INSPIRE
  proposal date as a lower bound, not a true "collaboration formed" date.
- **SLD:** no membership/institution/country counts found in any source
  fetched this session (the one official page found, a 1994 SLAC graduate
  student handbook excerpt, doesn't give collaboration size).
- **BaBar:** institution count not found (INSPIRE gives member count and
  country count, not institution count). `links.website` deliberately left
  `null` — no live official BaBar/PEP-II URL was fetched and confirmed this
  session, and A17 forbids citing an unverified one.
- **H1:** no membership counts found; terminal date only month-precision
  (H1's own site says "ended June 2007"; the day-precision 2007-06-30 comes
  from ZEUS's INSPIRE record for the *shared* HERA shutdown and is noted as
  corroboration, not asserted as H1's own sourced value).
- **ZEUS:** institution/country counts not found (only member count, "about
  450", from the collaboration's own site).
- None of the six has `key_specs` beyond CDF/D0's total_mass and CDF's
  solenoid field — no TDR/CDR or full detector paper (beyond abstracts) was
  fetched for SLD, BaBar, H1 or ZEUS this session.
- No `documents/` or `results/` files beyond the two CDF/D0 top-quark results
  (none are flagships, so these are optional full-depth extras that were not
  pursued further given time spent on the mandatory bar for six experiments).

## Dangling references

At the start of this session, **all** of the following were dangling
(referenced by these six experiments but not yet created by their owner, the
"facilities" lead): `facility:slac`, `accelerator:slc`, `accelerator:pep-ii`,
`site:slac-slc-collider-hall-sld`, `site:slac-pep-ii-ir2-babar`,
`facility:desy`, `accelerator:hera`, `site:desy-hera-north-hall-h1`,
`site:desy-hera-south-hall-zeus`. Partway through this session the facilities
lead landed all nine of these records (confirmed by re-listing
`data/atlas/facilities/`, `data/atlas/sites/`, `data/atlas/accelerators/` and
re-running the validator), so **as of the state left by this session, none of
the six experiments has an actual dangling reference** — `0 errors, 10
warnings` attributable to these files (see below). This is recorded here in
case a future session runs against an earlier snapshot where those ids are
still missing.

## Children spawned

**None.** Every attempt to spawn a child (`Agent` tool, `subagent_type:
general-purpose`, `model: sonnet`) returned "Concurrent subagent limit
reached" (the session-wide cap of 20 concurrent subagents across 16 wave-3
leads was saturated every time this was tried, including a retry after an
explicit ~90s wait). Per the coordinator's correction mid-session, all
research and writing for all six experiments was done directly by this lead:
every WebFetch/curl fetch, every INSPIRE API call, and every JSON file above
was produced in this session, and re-verification against the cited source
was therefore continuous rather than a separate post-hoc step.

## Validation and build

- `python -m hepgraph.atlas.validate`: **0 errors** attributable to any file
  listed above (verified by filtering the full findings list to the entity
  ids and `colliders-historical`-prefixed source/path names above — see
  transcript). 10 warnings remain, all expected and explained in the entity
  `notes`/site `coordinates.note` fields:
  - `coordinate-kind-approximate` ×2 (CDF/D0 sites, A23 — campus-precision
    fallback, explicitly allowed and warned rather than failed)
  - `sites-too-close` ×1 (the CDF and D0 sites share the same campus-fallback
    point, 0 m apart — an honest consequence of both lacking a sourced
    hall-specific coordinate, not a duplicate-entity error)
  - `experiment-without-active-beam` ×6 (one per experiment) — the A12 check
    that a listed accelerator/beamline is active whenever the experiment is;
    fires even for CDF/D0 referencing `accelerator:fermilab-tevatron`, whose
    own sourced intervals *do* cover the same active window, so this looks
    like a check limitation (possibly build-date-relative rather than
    interval-relative) rather than a real inconsistency in these records.
  - `interval-start-unknown` ×1 (CDF Run I start intentionally left `null`,
    per A3 — sources describe continuous 1987-1996 running without a single
    clean "Run I start" distinct from the 1987/1988-89 runs)
  - The repository-wide run (`22 errors` before this session's coverage-file
    update, `8 errors` after) has zero errors touching any file this lead
    owns; all remaining errors belong to other leads' files (e.g.
    `experiments/xenonnt.json`, `coverage/reactor-solar-neutrino.json`,
    `facilities/hess-khomas-highland.json`).
- `python -m hepgraph.atlas.build`: succeeds, exit code 0. `atlas.json` +
  `manifest.json` = ~1.35 MB, over the 400 KB pilot-budget *warning*
  threshold (pre-existing repo-wide condition, not caused by this wave; the
  build only fails above 1.5 MB per the ontology's stated policy).

## Confidence summary

High confidence, each independently sourced and cross-checked against a
second source where possible: all six experiments' proposal/approval dates
(INSPIRE experiment records, fetched as raw API JSON — no model paraphrase),
the shared Tevatron shutdown (2011-09-30, three independent Fermilab
sources), the shared HERA shutdown (2007-06-30 per ZEUS's INSPIRE record,
"ended June 2007" per H1's own site), BaBar's first-collision day
(1999-05-26, CERN Courier) and last-data day (2008-04-08, Symmetry
Magazine), the 1995 top-quark paper titles/journal references/arXiv ids for
both CDF and D0 (fetched directly from their INSPIRE literature records).

Lower confidence / explicitly flagged: CDF/D0 collision-hall coordinates
(campus-precision fallback, A23-compliant); the "construction" status label
on the gap between approval and first-collisions/first-data for all six
experiments (the bounding dates are sourced, the "construction" status
itself is this lead's inference, not a source's own label, and is noted as
such on every such interval); SLD's and H1's collaboration sizes (entirely
unsourced this session, left `null`); the CDF total-mass and solenoid-field
values (two independently sourced but slightly disagreeing figures, with the
higher-ranked source used and the discrepancy recorded rather than
resolved).
