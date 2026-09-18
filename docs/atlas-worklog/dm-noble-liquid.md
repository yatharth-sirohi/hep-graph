# dm-noble-liquid research log (XENON1T, XENONnT, PandaX-4T, DarkSide-50, DarkSide-20k, DEAP-3600)

Agent: `dm-noble-liquid` (Wave 3 domain lead). Worked in
`/Users/yatharthsirohi/Desktop/HEP-Graph-atlas-v1` (branch `hep-atlas-v1`). No git
commands were run; the orchestrator commits. All `verified_at` values are
2026-09-17, the day every cited source was fetched with WebFetch (or
WebSearch -> WebFetch).

## Scope

All six noble-liquid direct-detection experiments assigned in
`docs/atlas-worklog/ID_REGISTRY.md`'s Wave 3 table:

* `experiment:xenon1t`, `experiment:xenonnt` -- researched directly by the lead.
  XENONnT is a flagship (full depth: results, document, richer intervals).
* `experiment:pandax-4t` -- researched directly by the lead.
* `experiment:darkside-50`, `experiment:darkside-20k` -- researched directly by
  the lead.
* `experiment:deap-3600` -- delegated to one child agent (model `sonnet`); every
  critical claim it returned was re-checked by the lead against the cited
  source before acceptance (see "Children spawned" below).

Delegation note: the brief called for four children (XENON pair; PandaX-4T;
DarkSide pair; DEAP-3600). Three of the four `Agent` calls failed with
"Concurrent subagent limit reached" (the orchestrator's shared cap of 20
subagents across all 16 Wave-3 leads). Per the orchestrator's follow-up
correction, the lead did not retry in a loop; instead it researched XENON1T,
XENONnT, PandaX-4T, DarkSide-50 and DarkSide-20k itself, sequentially, with
WebSearch/WebFetch, and let only the DEAP-3600 child (which had launched
successfully) run to completion.

`facility:lngs` and `site:lngs-hall-b` already existed (created by the
`dark-matter`/earlier leads) and are referenced, not recreated.
`facility:cjpl`, `site:cjpl-ii`, `site:lngs-hall-c`, `facility:snolab` and
`site:snolab-underground-lab` are owned by the `facilities` workstream and had
not landed as of this session; every reference to them is a **dangling
reference**, expected per the ID registry and brief (listed again below).

## Entities written

| id | file |
| --- | --- |
| `experiment:xenon1t` | `data/atlas/experiments/xenon1t.json` |
| `experiment:xenonnt` | `data/atlas/experiments/xenonnt.json` |
| `experiment:pandax-4t` | `data/atlas/experiments/pandax-4t.json` |
| `experiment:darkside-50` | `data/atlas/experiments/darkside-50.json` |
| `experiment:darkside-20k` | `data/atlas/experiments/darkside-20k.json` |
| `experiment:deap-3600` | `data/atlas/experiments/deap-3600.json` |
| `detector:xenon1t` | `data/atlas/detectors/xenon1t.json` |
| `detector:xenonnt` | `data/atlas/detectors/xenonnt.json` |
| `detector:pandax-4t` | `data/atlas/detectors/pandax-4t.json` |
| `detector:darkside-50` | `data/atlas/detectors/darkside-50.json` |
| `detector:darkside-20k` | `data/atlas/detectors/darkside-20k.json` |
| `detector:deap-3600` | `data/atlas/detectors/deap-3600.json` |
| `collaboration:xenon` | `data/atlas/collaborations/xenon.json` (shared by xenon1t + xenonnt) |
| `collaboration:pandax-4t` | `data/atlas/collaborations/pandax-4t.json` |
| `collaboration:darkside` | `data/atlas/collaborations/darkside.json` (shared by darkside-50 + darkside-20k) |
| `collaboration:deap-3600` | `data/atlas/collaborations/deap-3600.json` |
| `result:xenon1t-electronic-recoil-excess-2020` | `data/atlas/results/xenon1t-electronic-recoil-excess-2020.json` |
| `result:xenonnt-first-nr-search-2023` | `data/atlas/results/xenonnt-first-nr-search-2023.json` |
| `result:xenonnt-b8-cevns-indication-2024` | `data/atlas/results/xenonnt-b8-cevns-indication-2024.json` |
| `document:xenonnt-instrument-paper` | `data/atlas/documents/xenonnt-instrument-paper.json` |

26 `src:` records under `data/atlas/sources/dm-noble-liquid-*.json` (20 for the
XENON/PandaX/DarkSide group, written by the lead; 6 for DEAP-3600, written by
the child). No duplicate URL/DOI was created: every URL was grepped against
`data/atlas/sources/` before a new record was written.

Not written, deliberately:

* No `facilities/`, `sites/`, `institutions/`, `memberships/` or `people/`
  files anywhere in this scope -- every site this wave's experiments sit at is
  either already owned by another lead (`site:lngs-hall-b`) or explicitly
  owned by `facilities` and referenced as a dangling id (`site:lngs-hall-c`,
  `site:cjpl-ii`, `site:snolab-underground-lab`, `facility:cjpl`,
  `facility:snolab`).
* No membership roster files: no collaboration in this scope publishes a
  fetchable per-institution list small enough to be a "full-depth extra";
  only aggregate scientist/institution/country counts are recorded where a
  source states them (XENON, DEAP-3600) and left null otherwise (PandaX-4T,
  DarkSide).
* No `person:`/leadership records anywhere (out of scope this wave; belongs to
  `membership-lead` and needs INSPIRE author recids).
* No results/documents for PandaX-4T, DarkSide-50, DarkSide-20k or DEAP-3600:
  none of the four is a flagship, and the mandatory bar was prioritized over
  optional extras given the concurrency/time constraints described above.

## Sources added

All prefixed `src:dm-noble-liquid-...`. Grouped by rank:

* Official experiment sites (rank 1): `xenon-official-history`,
  `xenon-official-collaboration` (both xenonexperiment.org),
  `pandax-4t-official-site` (pandax.sjtu.edu.cn), `darkside-official-site`
  (darkside.lngs.infn.it), `deap-3600-official-site` (deap3600.ca, via child).
* Official facility sites (rank 2): `xenon-lngs-hall-b`, `darkside-lngs-page`
  (both lngs.infn.it), `deap-3600-snolab-page` (snolab.ca, via child).
* INSPIRE experiment records (rank 3): `xenonnt-inspire-experiment` (recid
  1807876), `xenon1t-inspire-experiment` (1386519),
  `pandax-4t-inspire-experiment` (1221671, the generic umbrella PandaX
  record), `darkside-20k-inspire-experiment` (1830577),
  `deap-3600-inspire-experiment` (1108195, via child). One INSPIRE etiquette
  note: an `inspirehep.net/api/experiments?q=legacy_name DarkSide-50` query
  returned zero hits -- **no INSPIRE experiments-collection record exists for
  DarkSide-50**, confirmed rather than assumed.
* Detector papers (rank 5): `xenonnt-instrument-paper` (arXiv:2402.10446, Eur.
  Phys. J. C 84 (2024) 8, 784), `xenon1t-detector-paper` (arXiv:1708.07051),
  `deap-3600-detector-paper` (arXiv:1712.01982, Astropart. Phys. 108 (2019)
  1-23, via child).
* arXiv/journal (rank 10): `xenonnt-first-nr-search-2023` (2303.14729, PRL
  131, 041003), `xenonnt-b8-cevns-2024` (2408.02877, PRL 133, 191002),
  `xenon1t-first-results-2017` (1705.06655), `xenon1t-excess-2020`
  (2006.09721, Phys. Rev. D 102, 072004), `pandax-4t-commissioning-run-2021`
  (2107.13438, PRL 127, 261802), `darkside-50-first-results-2015`
  (1410.0653, Phys. Lett. B 743, 456), `darkside-50-lowmass-2023`
  (2207.11966, Phys. Rev. D 107, 063001), `darkside-20k-jinst-2024`
  (2402.07566, JINST 19 C03058), `deap-3600-status-2026` (2603.27372, via
  child).
* Press release (rank 9): `deap-3600-phys-org-2015` (via child).

## Conflicts

| claim | source A | source B | chosen | why |
| --- | --- | --- | --- | --- |
| XENONnT total xenon mass | xenonexperiment.org/history/: "about 8.6 tonnes" | Instrument paper (Eur. Phys. J. C 84, 2024): "8.5 tonnes total mass in cryostat" | **8.5 t** | The peer-reviewed instrument paper's precise figure is used as the primary `key_specs`/`specs.total_mass` value; the collaboration site's rounded "about 8.6 t" is recorded in a `note`, not discarded. |
| XENONnT construction/commissioning start | xenonexperiment.org/history/: "XENONnT started its operation ... in 2020" | INSPIRE experiment record 1807876: `date_started` 2021-07-06 | **both, as separate intervals** | 2020 is used for a "start of operation/commissioning" interval; 2021-07-06 is used for the start of the sourced open "science operations" interval, since neither source states SR0/SR1 boundaries directly and the two figures plausibly describe different milestones (first data vs. the run this exposure figure is drawn from). |
| DarkSide-50 end of operations | LNGS facility page (lngs.infn.it/en/darkside): "operated from 2013 to 2020" | DarkSide's own collaboration site (darkside.lngs.infn.it) states construction/first-fill history through April 2015 but no end date; a 2023 paper (arXiv:2207.11966) analyzes "the entire dataset" without a date | **2020 (approximate)** | The LNGS facility page is the only source giving an explicit end year; used with `confidence: approximate` since it gives only a year, and the discrepancy is documented in a `note` rather than silently resolved. |
| DarkSide-50 active argon mass | DarkSide/LNGS pages: "50 kg" (nominal, gives the experiment its name) | First-results paper (arXiv:1410.0653): "(46.4+-0.7) kg active mass" (measured) | **both, as separate key_specs** | 50 kg is the design/nominal figure quoted by every official page; 46.4+-0.7 kg is the more precise measured figure from the first-results paper. Both are recorded rather than picking one and discarding the other. |
| DEAP-3600 total argon mass | Detector paper (arXiv:1712.01982): "can contain 3600 kg of LAr" (design capacity) | Same paper, Sec. 3.2: "approximately 3300 kg LAr ... stably maintained since ... November 2016" (actual fill) | **both, as separate specs** (via child, re-verified by lead) | 3600 kg is the design capacity (and the experiment's namesake); 3300 kg is the actual operating fill. Documented as consistent, not conflicting, in both the experiment and detector records. |

## Unresolved fields

* `experiment:pandax-4t` / `detector:pandax-4t` `specs.phase` -- **null**. No
  source fetched in this session (official site or the 2021 commissioning-run
  paper, checked directly for the words "dual-phase"/"two-phase") states
  PandaX-4T's TPC phase in those terms, even though sibling experiments
  (LZ, XENONnT) are confirmed dual-phase. Left null per A17 rather than
  assumed from general knowledge of the PandaX design family.
* `experiment:darkside-20k` data-taking start -- **not resolved**. arXiv:
  2402.07566 (Feb 2024) says "late 2026"; the LNGS facility page (checked
  2026-09-17) says "2027". Both quotes are recorded in a `note`; no single
  interval bound was invented to split the difference.
* `experiment:darkside-50` `external.inspire_experiment` -- **null with
  note**. Confirmed via an `inspirehep.net/api/experiments` query that no
  experiments-collection record exists for DarkSide-50 (only DarkSide-20k
  has one). This is an honest absence, not an oversight (A20 requires a note
  for a tier B experiment lacking this field; one is present).
* `collaboration:xenon`, `collaboration:darkside`, `collaboration:pandax-4t`,
  `collaboration:deap-3600` `formation` -- **null or uncertain-confidence
  proxy** in every case. No collaboration in this scope publishes a formal
  founding date; each uses the earliest dated project activity found (XENON10
  development start 2002; DarkSide-50 construction-complete 2012; PandaX-4T
  commissioning 2021) as a labelled lower bound, never as a claimed formation
  date.
* `collaboration:pandax-4t`, `collaboration:darkside` membership counts --
  **null**. No source fetched in this session states an aggregate
  scientist/institution/country count for either collaboration (institutions
  are named individually for PandaX but not counted).
* `experiment:darkside-20k`/`detector:darkside-20k` construction start date --
  anchored to **2024** (when arXiv:2402.07566 first confirms construction
  under way), explicitly flagged in every relevant `note` as a lower bound,
  not the true start date, to satisfy A10's requirement that a non-terminal
  status's derived state match an interval that actually covers the build
  date.
* `experiment:deap-3600` "upgrade" interval start -- anchored to **2026-09**
  (via child, re-verified by lead against snolab.ca directly: the "Upgrading"
  status word is confirmed verbatim), for the same reason as above.

## Children spawned and what was re-checked

One child completed successfully: **DEAP-3600** (`experiment:deap-3600`,
`detector:deap-3600`, `collaboration:deap-3600`, 6 sources), spawned with
`model: "sonnet"` per the mandatory model rule. Three other children (XENON
pair, PandaX-4T, DarkSide pair) failed at launch with "Concurrent subagent
limit reached" and were not retried in a loop, per the orchestrator's
correction; the lead researched those five experiments directly instead (see
Scope).

Re-verification performed on the DEAP-3600 child's critical claims, after the
child returned its report and before any of its files were treated as
accepted:

* Re-fetched `arxiv.org/abs/1712.01982` (abstract only shows a fiducial
  exposure figure) and then `ar5iv.labs.arxiv.org/html/1712.01982` (full
  text) directly. All four quoted specs matched **character for character**:
  "The cryostat consists of a 5-cm-thick spherical acrylic vessel (AV), 85 cm
  in inner radius which can contain 3600 kg of LAr."; "Fiducial mass, radius:
  1000 kg, 55 cm"; "DEAP-3600 is located 2 km underground (6000 meters water
  equivalent overburden) at SNOLAB in Sudbury, Ontario, Canada"; "The target
  volume is viewed by 255 8-inch-diameter Hamamatsu R5912-HQE high quantum
  efficiency (HQE) PMTs."
* Re-fetched `https://www.snolab.ca/experiment/deap-3600/` directly and
  confirmed the literal status word **"Upgrading"**, matching the child's
  claim and its choice of `status: "upgrade"` (not "active").
* Re-fetched `https://inspirehep.net/api/experiments/1108195` directly and
  confirmed `legacy_name: "DEAP-3600"`, matching `external.inspire_experiment:
  1108195`.

No discrepancy was found; the child's files were accepted as written. Its
"upgrade"-interval `start: "2026-09"` anchoring convention (documented as a
lower bound, not a true start date) was reviewed and judged consistent with
how the lead handled the identical problem for DarkSide-20k's construction
interval, so it was left as the child wrote it.

## Dangling references to ids another lead owns

* `facility:cjpl`, `site:cjpl-ii` -- owned by `facilities`; referenced by
  `experiment:pandax-4t` and `detector:pandax-4t`.
* `site:lngs-hall-c` -- owned by `facilities`; referenced by
  `experiment:darkside-50`, `experiment:darkside-20k`, `detector:darkside-50`,
  `detector:darkside-20k`.
* `facility:snolab`, `site:snolab-underground-lab` -- owned by `facilities`;
  referenced by `experiment:deap-3600`, `detector:deap-3600`,
  `collaboration:deap-3600`.

`facility:lngs` and `site:lngs-hall-b` are **not** dangling: both already
existed (created by an earlier lead) and were used as normal references for
`experiment:xenon1t`, `experiment:xenonnt` and their detectors.

## Confidence summary

* **verified** -- XENONnT/XENON1T mass specs and result claims; XENONnT's
  2023 WIMP limit and 2024 CEvNS-indication significance (2.73 sigma,
  correctly labelled `first_detection`, never "evidence"/"observation");
  XENON1T's 2020 excess claim (labelled `anomaly`, never "discovery"); Hall
  B/Hall C placements' quoted text; PandaX-4T's design and commissioning-run
  masses; DarkSide-50/-20k Hall C placement and DarkSide-20k's active mass;
  DEAP-3600's detector specs and current "Upgrading" status (re-verified by
  the lead).
* **approximate** -- DarkSide-50's operating-interval bounds (years only, no
  months); DarkSide-20k's construction-start anchor (2024) and the
  late-2026-vs-2027 schedule conflict; XENONnT's commissioning-to-science
  transition boundary; XENON1T's first-results run months (paraphrased by
  the fetch tool rather than a literal quoted sentence, recorded via
  `locator` instead of `quote`).
* **uncertain** -- every collaboration's `formation` proxy date (XENON 2002,
  DarkSide 2012, PandaX-4T 2021); the PandaX-4T INSPIRE record's applicability
  (generic umbrella record, not phase-specific); DarkSide-20k's lineage
  relation to DarkSide-50 (inferred from the collaboration's own framing of
  "previous argon-based detectors", not a source naming DarkSide-50
  specifically).
* **null with a note** -- PandaX-4T/DarkSide-50/DarkSide-20k/DEAP-3600
  collaboration membership counts (except DEAP-3600's SNOLAB-page figures);
  DarkSide-50's `external.inspire_experiment` (confirmed absent, not
  unsearched); PandaX-4T/DarkSide detector `specs.phase` gaps noted above;
  every collaboration's `leadership` (empty, no `person:` records created
  this wave).

## Validation

`python -m hepgraph.atlas.validate` (run repeatedly as files were added and
fixed): **0 errors attributable to any file in this scope** in every run,
including the final one. Three real errors were found and fixed during
research (an alias equal to its own record's name on `experiment:xenonnt`; two
`confidence: approximate` interval rows missing a required `note` on
`detector:darkside-50`; and `experiment:darkside-20k`/`detector:darkside-20k`
having `status: "construction"` with no interval whose start actually covered
the build date, fixed by sourcing a 2024 lower-bound start instead of leaving
`start: null`). All other warnings touching these files (SList shape for
`physics_goals`/`unique_capabilities`, "no accelerator active" for
direct-dark-matter experiments, derived-field-in-source-file for
`*_ids`/`document_ids`/`result_ids`) are the same pre-existing, repo-wide
conventions already present in the `lz.json` exemplar and every peer
experiment file, not defects introduced here.

`python -m hepgraph.atlas.build` succeeds (31 files written to
`static/atlas/generated/`); the only warning is the pre-existing,
repo-wide `atlas.json` + `manifest.json` bundle-size warning against the
three-experiment pilot budget, unrelated to this wave's additions.

Files were written with
`json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False) + "\n"` via
`hepgraph.atlas.load.dump_json` and carry `"schema": "hep-atlas/0.2"` (A11).
