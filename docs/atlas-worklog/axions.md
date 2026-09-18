# axions — wave 3 (v1.0) worklog

Domain lead session, 2026-09-17. Repository worktree
`/Users/yatharthsirohi/Desktop/HEP-Graph-atlas-v1`, no git used. All fetches
via WebFetch/WebSearch this session; `verified_at`/`accessed` = 2026-09-17
throughout.

## Scope

Seven non-flagship axion experiments from `data/atlas/coverage/axions.json`:
ADMX and HAYSTAC (haloscopes), CAST and IAXO (helioscopes), ALPS II
(light-shining-through-a-wall), ABRACADABRA and DMRadio (lumped-element).
Mandatory bar only (no results/documents/membership-roster files — none of
these seven are on the flagship list, and full-depth extras were out of time
budget this session).

## Delegation note (deviates from the brief's default plan)

The brief calls for delegating four children (haloscopes / helioscopes / LSW
/ lumped-element). Every `Agent` call this session returned "Concurrent
subagent limit reached" (the run shares a cap of 20 concurrent subagents
across ~16 leads). Per the coordinator's mid-session correction, I did not
retry in a loop; I researched and wrote all seven experiments myself,
sequentially, with my own WebFetch/WebSearch/Bash/Write tools. **No children
were spawned.** Consequently there is no separate "re-verification" step —
every quote, coordinate, date and status below was fetched and checked by me
directly, first-hand, against the source I cite.

The session was also interrupted once (a usage-limit reset) mid-way through
generating files; the resumed session picked up from the still-intact
generator script in the scratchpad and the sources already written to disk,
then finished facilities/sites/detectors/experiments/collaborations,
validated, and fixed every class of validator error found (see below).

## Entities written

- **Facilities/sites (created, owned by axions):**
  `facility:university-of-washington-cenpa` + `site:uw-cenpa-campus`;
  `facility:yale-wright-lab` + `site:yale-wright-lab-campus`;
  `facility:mit` + `site:mit-cambridge-campus`;
  `site:cern-cast-sr8` (under the existing `facility:cern`, owned by
  cern-atlas — not touched, only referenced).
- **Experiments:** `experiment:admx`, `experiment:haystac`,
  `experiment:cast`, `experiment:iaxo`, `experiment:alps-ii`,
  `experiment:abracadabra`, `experiment:dmradio`.
- **Detectors:** `detector:admx`, `detector:haystac`, `detector:cast`,
  `detector:iaxo`, `detector:alps-ii`, `detector:abracadabra`,
  `detector:dmradio`.
- **Collaborations:** `collaboration:admx`, `collaboration:haystac`,
  `collaboration:cast`, `collaboration:iaxo`, `collaboration:alps-ii`,
  `collaboration:abracadabra`, `collaboration:dmradio` (all seven have a
  named collaboration byline in their papers, so all seven got a lightweight
  collaboration record rather than an empty `collaboration_ids`).
- **No** `people/`, `memberships/`, `results/`, `documents/` files were
  written (out of scope / full-depth extras for non-flagship experiments).

## Sources added (28, all prefixed `axions-`, all rank <= 10)

Official/experiment sites: `admx-official-site`, `haystac-official-page`,
`iaxo-official-site`, `iaxo-news-page`, `alps-ii-official-site`.
CERN's own page: `cern-home-cast`. CENPA (official facility) pages:
`admx-cenpa-page`, `admx-cenpa-contact`. INSPIRE experiment records (rank 3,
fetched via the INSPIRE REST API, `inspirehep.net/api/experiments/<recid>`,
cited under the human-readable `inspirehep.net/experiments/<recid>` URL):
`admx-inspire-experiment` (1309376), `haystac-inspire-experiment` (1600738),
`cast-inspire-experiment` (1110249), `iaxo-inspire-experiment` (1698854),
`babyiaxo-inspire-experiment` (1826394), `alps-ii-inspire-experiment`
(1761312), `abracadabra-inspire-experiment` (1689129). arXiv papers (rank
10): `admx-prl-2020-invisible-axion`, `admx-prl-2025-1p1-1p3ghz`,
`haystac-prl-2025-phase-ii`, `iaxo-strategy-2025`, `alps-ii-tdr-2013`,
`abracadabra-prl-2019-first-results`, `abracadabra-prl-2021-broadband`,
`dmradio-status-2022`, `dmradio-cryo-2026`. Institution page:
`abracadabra-mit-winslow-page` (rank 8). Geocoder (OpenStreetMap/Nominatim,
rank 8, used only for `kind: campus` points per A17): `nominatim-uw-cenpa`,
`nominatim-yale-wright-lab`, `nominatim-mit`, `nominatim-cern-prevessin`.

Before creating any source I grepped `data/atlas/sources/` for the same
URL/DOI; none pre-existed except one unrelated PDG axion-review source
(`src:topic-pdg-2026-axions`, owned by the topics-method lead) which I did
not need to cite.

## Status research (spec section 36 — read carefully, not guessed)

- **ADMX**: `active`. INSPIRE record 1309376 (description, present tense)
  plus a 2025-04 PRL (arXiv:2504.07279, "In the most recent run, ADMX
  searched for axions between 1.10-1.31 GHz") establish it is still
  operating. No source found this session gives an exact founding/move-to-UW
  date with a checkable citation (see "rejected claim" below).
- **HAYSTAC**: `active`. INSPIRE record 1600738: `date_proposed 2010`,
  `date_approved 2011`, `date_completed "9999"` (INSPIRE's own sentinel for
  "no completion date" = still active), description "The detector was built
  and is in operation at Yale University's Wright laboratory." A 2024-09 PRL
  (arXiv:2409.08998) confirms an active Phase II run.
- **CAST**: `completed`, exact per the brief's instruction. INSPIRE record
  1110249 (which mirrors the CERN Greybook, `experiment_registry`/
  `inspire_experiment_record`, rank 3) gives day-precision dates:
  `date_proposed 1999-08-09`, `date_approved 2000-04-13`,
  `date_started 2003-06-18`, `date_completed 2022-12-31`. Recorded verbatim.
- **IAXO**: `construction` (driven by BabyIAXO), exactly matching the
  brief's steer. Full-scale IAXO's own site (iaxo.desy.de) says "The
  International Axion Observatory (IAXO) is a proposed fourth-generation
  axion helioscope" (`proposed`, INSPIRE `date_proposed 2013-08`). A 2025-04
  European-Strategy input paper (arXiv:2504.00079) states in its own words:
  "the detailed studies for BabyIAXO, which **is currently under
  construction**." Modelled as two intervals on one `experiment:iaxo`
  record (BabyIAXO's own INSPIRE record, 1826394, is noted but not made a
  second experiment id).
- **ALPS II**: `active`, "operating since 2023" confirmed to the day.
  INSPIRE record 1761312 gives `date_started: "2023-05-23"` directly as a
  structured field (not free text) — the cleanest date in this whole batch.
- **ABRACADABRA**: `completed`, "be careful about status" as instructed. The
  dedicated axion-search literature runs 2018 (arXiv:1810.12257, "first
  results from a 1 month search") to 2021 (arXiv:2102.06722, "we probe the
  hypothesis that axions constitute dark matter... in a broadband
  configuration"); an MIT faculty page (physics.mit.edu/faculty/
  lindley-winslow) independently corroborates completion: "demonstrated this
  technique with the ABRA-10cm experiment and is now working towards a
  larger and more sensitive experiment." I explicitly did **not** treat the
  same 10 cm hardware's later 2022-2026 gravitational-wave-search papers as
  continuing the axion program — different physics target, out of scope,
  noted on the record.
- **DMRadio**: `construction`, "design/construction" as instructed. A 2022
  status paper (arXiv:2210.07215, ar5iv full text) states outright "This
  experiment is being built on the Stanford University campus" (DMRadio-50L)
  and "This experiment is being built at SLAC National Lab" (DMRadio-m3); a
  2026-07 paper (arXiv:2607.05771) reports "measured performance" of the
  built DMRadio-50L cryostat, i.e. construction/commissioning well advanced
  by mid-2026, still short of "operating".

## Coordinates (A17 — campus-grade only, never invented)

- `site:uw-cenpa-campus`: 47.6593849, -122.3026450. CENPA's own contact page
  gives the shipping address ("4311 Mason Place NE, Seattle, WA 98195");
  geocoded via OpenStreetMap/Nominatim. `kind: campus`, `confidence:
  approximate`.
- `site:yale-wright-lab-campus`: 41.3190182, -72.9207433. Wright Lab's own
  "Visit" page gives "272 Whitney Ave, New Haven, CT 06511"; Nominatim
  resolved this directly to the "Wright Laboratory" building footprint.
  `kind: campus`, `confidence: approximate`.
- `site:mit-cambridge-campus`: 42.3582529, -71.0966272. No specific
  building/lab address for ABRACADABRA was found; campus-level Nominatim
  geocode of "Massachusetts Institute of Technology, Cambridge, MA" only.
  `kind: campus`, `confidence: approximate`.
- `site:cern-cast-sr8`: 46.2601088, 6.0577057. CAST sits in an SPS-fed
  experimental hall (SR8/West Area) on CERN's Prevessin site; no source
  fetched this session gives a precise SR8 building coordinate, so — per the
  brief's explicit fallback instruction — the CERN Prevessin campus point
  (Nominatim) is used, `kind: campus`, `confidence: approximate`, flagged in
  `note` as coarse (~3 km precision placeholder). This coincides (0 m) with
  two other CERN sites already in the atlas (`site:cern-ecn3-north-area`,
  `site:cern-neutrino-platform-ehn1`) that apparently use the same
  Prevessin-area fallback — flagged by the validator as `sites-too-close`
  (warning), left as-is rather than nudging coordinates to hide it.

All four sanity-checked: lat/lon within range, correct hemisphere/sign for
US (positive lat, negative lon) and France (positive lat, positive lon).

## Kind / technology_class

All seven experiments: `kind: "axion"` (an exact match in the ontology's
`EXPERIMENT_KINDS` enum). ADMX and HAYSTAC: `technology_class: "haloscope"`
(exact enum match). **CAST, IAXO, ALPS II, ABRACADABRA and DMRadio have no
matching enum value** — the ontology's `TECHNOLOGY_CLASSES` list has no
"helioscope", "light-shining-through-walls" or "lumped-element" entry. All
five are recorded as `technology_class: "other"` with a descriptive
`technology` (S) free-text field explaining the real technique, and a note
on each record flagging the enum gap for a future ontology amendment.

## Conflicts

| claim | source A | source B | chosen | why | confidence |
| --- | --- | --- | --- | --- | --- |
| ADMX built at LLNL in 1995, moved to UW in 2010 | Wikipedia (no checkable primary citation in the article) | (none found) | **not recorded** as a dated interval | A17 forbids a critical date resting solely on Wikipedia; left as an open item in `facilities/university-of-washington-cenpa.json` notes and `experiments/admx.json` notes instead of a fabricated/undated interval | n/a (omitted) |
| HAYSTAC's overburden/site-hall coordinate | (none found; only the street address) | — | campus-level Nominatim geocode | no building-interior coordinate sourced | approximate |
| ALPS II's exact DESY hall | brief's steer ("HERA North Hall" if sourced) | no source fetched this session says "North Hall" specifically (only "HERA tunnel"/generic DESY) | **no placements[] row written** | forcing `site:desy-hera-north-hall-h1` without a supporting quote would violate A17; safer to leave the field empty and flag it than assert an unconfirmed hall | n/a (omitted) |
| HAYSTAC newly-scanned mass range display vs. value | quantity `min/max` midpoint (18.37 ueV) | display text listing the literal band boundaries (17.28-19.46 ueV) | display rewritten to lead with the midpoint number, sub-bands kept in prose | avoids the A21 display/value drift warning without changing the underlying sourced numbers | verified |

## Unresolved fields / missing_fields

See `data/atlas/coverage/axions.json` for the authoritative per-experiment
list; in short, across all seven: no collaboration membership counts or
leadership were sourced (left as an empty, honest `membership` block per the
`cdms-ii.json` pattern); no results/documents records were written
(non-flagship, full-depth extra, skipped for time); several numeric magnet
specs (ADMX field/cavity volume, CAST magnet field/length, IAXO/ALPS II
magnet specs) were not found with a clean verbatim quote and were left out
of `key_specs` rather than guessed; DMRadio has no INSPIRE experiment record
(API query returned zero hits) and no dedicated website was successfully
fetched.

## Dangling references (ids I don't own, expected per ID_REGISTRY)

- `experiment:iaxo` / `collaboration:iaxo`: `facility:desy` (owner:
  `facilities`) — **still dangling** as of the last validate run this
  session (facility:desy not yet on disk).
- `experiment:alps-ii` / `collaboration:alps-ii`: `facility:desy` — same,
  still dangling.
- `experiment:dmradio` / `collaboration:dmradio` / `detector:dmradio`:
  `facility:slac` and `site:slac-menlo-park-campus` — **landed by the
  facilities lead partway through this session**; I re-checked and added a
  proper `detector:dmradio` placement at `site:slac-menlo-park-campus` for
  the DMRadio-m3 sub-experiment once it appeared, and updated the
  now-stale "dangling" notes on the experiment/collaboration records to
  reflect that it landed.
- `experiment:iaxo` / `collaboration:iaxo` and `experiment:alps-ii` /
  `collaboration:alps-ii`: `facility:desy` — **landed by the facilities lead
  later in this session**; re-checked and the now-stale "dangling" notes
  were updated on all four records.
- `experiment:alps-ii` / `detector:alps-ii`: `site:desy-hera-north-hall-h1`
  — also landed later in this session. Once it existed I read the
  facilities lead's own site file and found it cites `src:h1-wikipedia`
  ("The HERA North Hall, where the H1 detector was located, is now used for
  the new ALPS experiment") — independent corroboration of the pairing I
  had declined to assert on my own sourcing. I added the
  `detector:alps-ii` placement at that site, `confidence: approximate` (not
  `verified`, since the sole supporting source is Wikipedia, rank 12, per
  A17) rather than `verified`.

## Validator / build status

`python -m hepgraph.atlas.validate`: 0 errors attributable to axions files
other than the two still-expected `facility:desy` dangling references
(4 finding lines: 2 on `experiment:iaxo`/`collaboration:iaxo`, 2 on
`experiment:alps-ii`/`collaboration:alps-ii`). Every other validator error
class the axions files originally triggered was fixed, not suppressed:
`alias-equals-name` (removed a redundant DMRadio alias), `claim-evidence-
required` (added quotes/locators to three month/day-precision intervals),
`quote-too-long` (trimmed one 351-char quote), `status-not-derived-state`
(14 findings — every entity whose declared `status` didn't match its
interval-derived state at the build date; fixed by giving each "currently
true" interval a real, sourced-or-conservatively-approximated `start` bound
instead of leaving `start`/`end` both null, per A3's rule that a fully
null-null interval covers nothing), and `derived-field` (stripped the
build-derived `rank` field from all 28 sources and `document_ids`/
`result_ids` from all experiments/detectors). Remaining warnings on axions
files (11): one `coordinate-kind-approximate` and two `sites-too-close` on
`site:cern-cast-sr8` (inherent to the campus-level CERN fallback, documented
above), four `experiment-without-active-beam` (ADMX/HAYSTAC/ALPS
II/ABRACADABRA are lab-based, not accelerator-fed, so this heuristic doesn't
apply — no accelerator/beamline ids were ever claimed), and four `hull-gap`
warnings (ADMX 2020-2024, ABRACADABRA 2019-2020 — honest sourcing gaps, not
filled with invented intervals).

`python -m hepgraph.atlas.build`: succeeds (last run produced
`static/atlas/generated/manifest.json` version `828c41a5f029b27f`, 31
files, atlas.json 1.22 MB — the repo-wide bundle-size warning is pre-existing
and not attributable to this session's ~50 KB of axions data).

## Confidence summary

High confidence, directly sourced: all seven `kind`/`status` values, CAST's
full day-precision proposed/approved/started/completed dates, ALPS II's
day-precision operating-since date, IAXO/BabyIAXO's construction status,
DMRadio's two magnet specs, all four site coordinates (campus-grade,
correctly flagged `approximate`). Lower confidence / explicitly flagged:
ADMX's pre-2019 history (no sourced date this session), ABRACADABRA's exact
completion boundary (inferred from publication cadence, not a stated "this
program is complete"), HAYSTAC's "2018" operational start (a proxy from the
earliest sourced milestone, not a stated commissioning date), and every
`technology_class: "other"` record (ontology enum gap, not a sourcing gap).
