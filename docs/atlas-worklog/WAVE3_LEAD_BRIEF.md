# Wave 3 (v1.0) domain-lead brief — read completely before writing anything

Repository worktree: `/Users/yatharthsirohi/Desktop/HEP-Graph-atlas-v1` (branch
`hep-atlas-v1`). Run every command from that directory. Python is
`/Users/yatharthsirohi/Desktop/HEP-Graph/.venv/bin/python`. Do **not** use git
(no commit, checkout, stash, reset); the orchestrator commits. Never touch
`~/Desktop/HEP-Graph` (another session's checkout).

Today is 2026-09-17. `verified_at` and `accessed` are the day you actually read
the source.

## What you are producing

For every experiment in your `data/atlas/coverage/<owner>.json` file, a record
set that meets the **mandatory bar** (addendum §25):

- `experiments/<slug>.json`: name, aliases, `kind`, status, dated `intervals`
  (richest sourced history: proposal/approval/construction/commissioning/runs/
  shutdown/completed; `start: null` + note when a source does not say),
  `facility_roles`, `topic_ids` (from `data/atlas/topics/topics.json` only),
  `summary.plain` (≤ 60 words, no unexplained acronyms) and
  `summary.technical`, `links.website` (official site), `external.inspire_experiment`
  (INSPIRE experiment recid, with a record-level source whose URL contains it;
  tier A/B need it or a note), `key_specs` where a primary source gives them
  (each with `quote` or `locator`), `collaboration_ids`.
- `detectors/<slug>.json` with `placements: [{site_id, role, start, end, sources,…}]`,
  `technology_classes`, `specs` you can source.
- `collaborations/<slug>.json` where a collaboration exists (formation with
  source; `membership` counts only when a source states them; `leadership` only
  when sourced). A **membership roster file is a full-depth extra: do not write
  one** unless the collaboration's own public member list is fetchable and
  small; never build rosters from author lists in this wave.
- `sites/<slug>.json` with **verified coordinates**: `coordinates` is a FLAT
  sourced object exactly as `hepgraph/atlas/schema.py` and the existing site
  files define it: `{lat, lon, kind, precision_m, sources, verified_at,
  confidence, quote|locator, note}` (no `value` wrapper). When the ontology
  prose and `schema.py`/existing files disagree, the validator is the truth. Detector/underground-lab coordinates need an official page,
  a technical/geodetic paper or the facility's own site page stating them (rank
  ≤ 7); geocoder/Wikipedia/Wikidata coordinates are allowed only for
  `kind: campus|headquarters` and must be labelled `confidence: approximate`.
  If nothing better exists, record the campus point with `confidence:
  approximate`, `kind: campus`, and say so in `note`. **Never invent or
  "remember" a coordinate.** Sanity-check every coordinate against the country
  and the facility (lat ∈ [-90,90], lon ∈ [-180,180], sign and hemisphere).
- `sources/<owner>-<slug>.json` for every page you actually fetched (WebFetch
  or WebSearch→WebFetch). Before creating one, `grep -rl "<url or doi>"
  data/atlas/sources/` and reuse an existing record (update `accessed`).
  `retrieval` is required; a `failed` source may not be cited.
- Your coverage row updated honestly: `researched` ∈ {none, partial, complete},
  `missing_fields` listing exactly what is still absent (e.g.
  `["membership", "results", "documents"]`). Under-claim rather than over-claim.
- `docs/atlas-worklog/<owner>.md` with: Scope; Entities written; Sources added;
  Conflicts (claim / source A / source B / chosen / why / confidence); Unresolved
  fields; Children spawned and what you re-checked against the source yourself;
  Dangling references to ids another lead owns; Confidence summary.

Results, technical documents and institution rosters are **full-depth extras**
required only for flagships (ATLAS, CMS, ALICE, LHCb, DUNE, Super-K, Hyper-K,
T2K, NOvA, IceCube, KM3NeT, Belle II, JUNO, LZ, XENONnT, Muon g-2, Mu2e, NA62,
COHERENT). If one of these flagships is in your file, give it 2–4 major
results (`result.claim.quote` verbatim from the publication title/abstract or
the collaboration's own result page; wording follows the collaboration:
evidence is not discovery, a limit is not an observation; `date_kind`
required) and its key technical documents (TDR/CDR/detector paper as
`documents/<slug>.json` with `owner_ids`). Non-flagship results are welcome
only if you have time after every mandatory record is done.

## Rules that outrank speed

1. Read `docs/HEP_ATLAS_ONTOLOGY.md` — the **v0.2 amendment block A1–A22 at the
   top overrides the body** — and `docs/atlas-worklog/RESEARCH_AGENT_RULES.md`
   and `docs/atlas-worklog/ID_REGISTRY.md` (your ids are in the Wave 3 table).
2. **No fact from model memory on a critical field** (A17). Every coordinate,
   date, number, status, membership and result claim cites a source you
   fetched in this session and carries `quote` (≤ 300 chars, verbatim) or
   `locator`. If you cannot fetch a supporting source, the field is `null`
   with a `note`. "Start date unknown" is acceptable; an invented date is a
   P0.
3. Source hierarchy: official experiment site > official lab site > CERN
   Greybook / INSPIRE experiment record > TDR/CDR > detector paper > HEPData/PDG
   > institution page > result page > journal/arXiv > Wikipedia/Wikidata (rank
   12: pointer only, never the sole source of a critical value).
4. Never claim collaboration membership from institutional affiliation; never
   attach a person. **Do not create `people/` files in this wave.**
5. One canonical entity per real thing; check `data/atlas/experiments/` and
   `grep -ril "<name>" data/atlas/` for an existing record or alias before
   creating one. Use the exact ids from ID_REGISTRY.
6. Ids you do not own: reference them; never create them. A dangling reference
   to an id the registry assigns to `facilities` is expected until that lead
   lands — list it in your worklog.
7. INSPIRE etiquette: ≤ 1 request to inspirehep.net every 10 s per agent. Do
   not crawl. Never touch the INSPIRE importer, Neon or Vercel.
8. Fix classes, not examples: if the validator flags one of your records,
   check every sibling for the same mistake.

## Delegation

**Concurrency cap:** the whole session shares a limit of 20 concurrent
subagents across all leads. If `Agent` fails with "Concurrent subagent limit
reached", do NOT stop and do NOT retry in a loop: research the experiments
yourself, sequentially, in this same agent, and try one child again later
only if you still have several experiments left. Stopping with nothing
written is the one unacceptable outcome.

Spawn children (when capacity allows) with the Agent tool, `subagent_type:
"general-purpose"`, **`model: "sonnet"`** (mandatory — never opus), at most 2 at a time,
each owning 1–3 experiments and given (a) this file path, (b) the exact ids it
owns, (c) the exemplar files below. When a child returns, **you re-open the
cited source yourself for every coordinate, every interval bound at month/day
precision, every key spec and every result claim** before accepting; reject and
re-task on any unsourced value. Log what you re-checked.

Exemplars of the target shape (read one of each before starting):
`data/atlas/experiments/nova.json`, `data/atlas/detectors/miniboone.json`,
`data/atlas/sites/ash-river-nova-far-detector.json`,
`data/atlas/collaborations/nova.json`, `data/atlas/sources/` (any `nova-*`),
`data/atlas/results/nova-oscillation-parameters-2022.json`,
`data/atlas/documents/nova-tdr.json`, `data/atlas/coverage/fermilab-neutrino-other.json`.
Scaffold a skeleton with
`python -m hepgraph.atlas.scaffold experiment <slug> --facility <f> --collaboration <c> [--site <s>] --owner <owner> --tier <A|B|C|D> --name "<Name>"`
(it refuses to overwrite; it writes a placeholder source `src:<slug>-official-site`
with an `example.invalid` URL that you must replace or delete, and a facility
skeleton that you must delete if the facility belongs to another owner).

## Finishing

1. `python -m hepgraph.atlas.validate` must report **0 errors** attributable to
   your files (dangling references to `facilities`-owned ids excepted; list
   them). Fix warnings on your own records where they are real.
2. `python -m hepgraph.atlas.build` must succeed.
3. Write the worklog and update the coverage rows.
4. Return a structured report: entities written (ids), per-experiment
   `researched` state and `missing_fields`, sources added, conflicts, dangling
   ids, anything you could not source, and which children you spawned and
   what you re-verified. Do not return prose assurances; return evidence
   (source ids and quotes) for every critical claim you are asked about.
