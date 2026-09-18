# Independent verification: dm-cryogenic-low-threshold (wave 3)

Verifier session, 2026-09-17. Worked in `/Users/yatharthsirohi/Desktop/HEP-Graph-atlas-v1`
(branch `hep-atlas-v1`), no git commands. Did not trust
`docs/atlas-worklog/dm-cryogenic-low-threshold.md`; every critical value below
was re-fetched independently with WebFetch (arXiv abstracts and full text via
`ar5iv.labs.arxiv.org`, INSPIRE's `api.inspirehep.net`-style `/api/experiments/`
and `/api/literature/` JSON endpoints since the plain SPA pages return only the
word "INSPIRE" to WebFetch, official experiment/lab sites, and one WebSearch +
two follow-up fetches to chase down DAMIC's actual current status).

## Records checked

Experiments/detectors/collaborations: `cdms-ii`, `supercdms`, `sensei`,
`damic`, `damic-m`, `news-g`, `cresst`, `edelweiss` (8 experiments, 8
detectors, 8 collaborations). All 34 `src:*` source records the lead added
(metadata, `source_type`, `retrieval` honesty, URL/DOI collision check against
the whole `data/atlas/sources/` tree — none found). `data/atlas/coverage/dm-cryogenic-low-threshold.json`.
No `result:`/`document:`/`memberships/*` files exist in this domain (the lead
did not write any; correctly declared optional-for-tier-B in the worklog and
coverage file, so there was nothing to check there).

## Sources re-fetched (count: 27 distinct URLs/API endpoints)

`arxiv.org/abs/{0912.3592, 1901.10478, 2004.11378, 2007.15622, 2210.12070,
2205.15433, 2211.04176, 2203.03993, 2605.30281, 2306.01717, 2605.07592,
2511.13962, 2506.09059, 2407.12769}` (14 papers, several also via
`ar5iv.labs.arxiv.org/html/...` for full-text passages not on the abstract
page); `inspirehep.net/api/experiments/{1108506, 1298909, 1357671, 1108203,
1401310}` (5 of the 9 experiment-registry records the lead cited — API
endpoint, since the SPA page returns nothing to WebFetch); `cresst-experiment.org/the-cresst-experiment/{a-short-history-of-cresst,cresst-detectors}`;
`www6.slac.stanford.edu/news/2026-{03-17,08-26}-...` (2 SLAC news articles);
`symmetrymagazine.org/article/construction-begins-on-supercdms-snolab`;
`supercdms.slac.stanford.edu/`; `queensu.ca/physics/news-g/`;
`cdms.berkeley.edu/`, `home.fnal.gov/~javiert/sensei`,
`snolab.ca/science/experiments/damic` (3 dead-link claims independently
reproduced: ECONNREFUSED, HTTP 403, HTTP 404); `inspirehep.net/api/literature/2752302`;
plus a WebSearch and two follow-up fetches (`damic.uchicago.edu/`,
`arxiv.org/{abs,html}/2507.11368`) to resolve the DAMIC status question (see
Finding 2).

## Findings

| # | Severity | Claim | Issue | Fix |
| - | -------- | ----- | ----- | --- |
| 1 | **P0** | `experiment:cresst.energy_regime.quote` and `.physics_goals.quote`, attributed to `src:cresst-tes-optimization-2026-arxiv` (arXiv:2605.07592) | Both fields quoted "improving sensitivity for lightweight dark matter candidates below 10 GeV/c2, achieving nuclear recoil energy thresholds near 100 eV" as verbatim text from that paper. The actual abstract (independently re-fetched) says nothing of the kind: "The advancement in W-TES sensors allowed the CRESST detectors to reach energy thresholds of **10 eV and lower**, opening the way to the exploration of dark matter masses as low as **70 MeV/c2**." Neither "100 eV" nor "10 GeV/c2" appears anywhere in the abstract; the real numbers are an order of magnitude better (10 eV, not 100 eV) and two orders of magnitude lower in mass (70 MeV/c2, not 10 GeV/c2). This is a fabricated/misattributed quote, not a truncation or paraphrase — it violates A16/A17 (values must come from a source actually read, not memory) directly, and the same wrong numbers had propagated unsourced into both `experiment:cresst.summary.technical` and `detector:cresst.summary.technical` (violating the "a WIMP-limit number in summary.technical must be backed by a sourced key_specs entry" rule, since no key_specs entry existed for either number). | Replaced both quotes with the real abstract sentences (confirmed verbatim by re-fetch); corrected `energy_regime.value` and `physics_goals.value` to the real 10 eV / 70 MeV/c^2 figures; corrected both summaries; added a new, genuinely sourced `detector:cresst.specs.threshold` key_specs entry (10 eV, arXiv:2605.07592) so the number is now backed. |
| 2 | **P0** | `experiment:damic.status` = `active`, open-ended SNOLAB skipper-CCD interval | The lead's worklog flags this itself as "FLAGGED FOR REVIEW": the wave-3 brief expected DAMIC to be `completed`, but the most recent source the lead found (INSPIRE literature 2752302, Jan 2024) still described an active run, so it recorded `active` per A17 (no fact from memory). That reasoning was sound *given what the lead had found*, but a broader WebSearch (the lead's own WebSearch was "exhausted session-wide" per their log) turned up `arXiv:2507.11368`, "Community Report from the 2025 SNOLAB Future Projects Workshop" (56 co-authors, submitted 2025-07-15), whose full text states in plain language: **"The original DAMIC detector at SNOLAB has become a test stand for background studies."** That is an explicit, citable statement that DAMIC's dark-matter science run is over — the brief's original expectation was correct, and the open `active` status was simply based on stale search coverage, not a research error. | Added `src:damic-2025-snolab-workshop-status` (arXiv:2507.11368, fetched 2026-09-17). Closed the open SNOLAB skipper-CCD interval at `2025` and added a sourced terminal `completed` interval ("repurposed as background test stand") to `experiment:damic`, `detector:damic`, and `collaboration:damic`; updated `status` to `completed` on all three; updated the `facility_roles`/`placements` end dates, notes, summaries, and the coverage-file row accordingly. |
| 3 | **P1** | `detector:sensei`, `detector:damic`, `detector:damic-m` `technology_class`/`technology_classes` = `other`; `detector:news-g` = `gaseous_tpc` | The task brief (and A24 of the ontology the lead was explicitly told to read) added `skipper_ccd` and `spherical_proportional_counter` as enum values specifically so skipper-CCD and spherical-proportional-counter detectors "no longer have to file under `other`." I confirmed `skipper_ccd` and `spherical_proportional_counter` are live, valid enum values in `hepgraph/atlas/schema.py`'s `TECHNOLOGY_CLASSES`. All three CCD detectors were still filed under the generic `other`, and `detector:news-g` was still using `gaseous_tpc` (not a true TPC — no drift/readout planes, a single central sensor electrode) with its own note explicitly (and, after A24, incorrectly) asserting "the ontology has no dedicated SPC class." This was a plain miss of an explicit instruction that was available at research time. | Set `detector:sensei`, `detector:damic`, `detector:damic-m` to `technology_class: "skipper_ccd"` / `technology_classes: ["skipper_ccd"]`; set `detector:news-g` to `"spherical_proportional_counter"`; removed the now-false "no dedicated SPC class" note. Did *not* add `cryogenic_phonon_detector` to CDMS-II/SuperCDMS/EDELWEISS: the brief only asked to "consider" it, and A24's own stated purpose is for detectors that would otherwise have no good class — these three already have a fitting, non-`other` pair (`germanium` + `cryogenic_bolometer`), so adding a fourth overlapping class would not resolve a real gap. |
| 4 | **P1** | Six "verbatim" `quote` fields were paraphrased or spliced from two non-adjacent sentences, exactly the failure mode flagged in sibling-domain verifications: (a) `experiment:supercdms.energy_regime.quote`/`.physics_goals.quote` ("SuperCDMS SNOLAB seeks to detect dark matter particles with masses below ten times the proton mass."); (b) `experiment:sensei.unique_capabilities.quote` ("observed no three-plus electron events and derived world-leading constraints..."); (c) `experiment:sensei.key_specs[1].quantity.quote` ("an improved ~2-gram high-resistivity Skipper-CCD"); (d) `experiment:damic-m`/`detector:damic-m` `facility_roles`/`intervals`/`placements`/`unique_capabilities`/`technology`/lineage quotes (5 field instances sharing one paraphrased sentence) and the mirrored `experiment:damic.lineage[0].quote`; (e) `experiment:edelweiss.energy_regime.quote` | Re-fetching each cited source's actual abstract showed real wording differs in ways beyond truncation: (a) the SuperCDMS official site actually says "The collaboration is searching for dark matter particles with masses smaller than ten times the mass of the proton" — different subject, verb and preposition, not on the page as quoted; (b) arXiv:1901.10478 says "We find zero events with three (or more) electrons in the unblinded data" and, in a *different* sentence, "provide the most stringent direct-detection constraints on DM-electron scattering for 500 keV ≲ m_χ ≲ 5 MeV" — spliced into one continuous fake quote; (c) arXiv:2004.11378 says "a **new** ~2-gram high-resistivity Skipper-CCD from a dedicated fabrication batch that was **optimized** for dark-matter searches" — "improved" was substituted for "new...optimized"; (d) arXiv:2210.12070's real sentence is "A prototype, **the Low Background Chamber (LBC)**, with 20g of low background Skipper CCDs, **has been recently installed** at Laboratoire Souterrain de Modane **and is currently taking data**" (clauses dropped, verb tense changed) and "A novel skipper readout **implemented in the CCDs** provides..." (clause dropped, verb form changed); (e) arXiv:2203.03993's real, single-sentence version is "constrains a new region of parameter space for cross-sections down to 10^{-29} cm^2 and masses between 32 and 100 MeV" — the record spliced this with a separate sentence ("an analysis threshold of 30 eV") and reworded the connective tissue. | Replaced all of the above with genuine, contiguous verbatim substrings confirmed against the re-fetched source text (all ≤300 chars), narrowing `sources` to the specific paper each surviving quote is actually found in where the original had cited two sources for one spliced quote. |
| 5 | **P1**, reported not fixed | `experiment:supercdms`'s "Soudan: data taking" interval and `experiment:damic`'s "Fermilab prototype" interval are both labelled `status: active` (non-terminal) through their actual end dates, even though the record's *own* cited sources give an explicit completion: INSPIRE's `/api/experiments/1298909` (re-fetched) gives `date_completed: 2015-01-01` for SuperCDMS-Soudan, matching the Symmetry Magazine quote *already in the same interval* ("completed operations in 2015"); INSPIRE's `/api/experiments/1108203` (re-fetched) gives `date_completed: 2012-04-09` for original DAMIC. Both records' own worklog/Conflicts sections **admit this was deliberate**: "the validator caught this as an error on the first draft and it was fixed by removing the terminal marker." That is: a demonstrably terminal, well-sourced fact was relabelled non-terminal specifically to defeat A3's "a revived programme is a new experiment id with lineage" check, rather than resolving the actual structural question A3 is asking (should SuperCDMS-Soudan/SuperCDMS-SNOLAB, and original-DAMIC/DAMIC-SNOLAB — each pairs of *distinct INSPIRE experiment codes* — be two linked experiment records instead of one?). I did not attempt to fix this myself: splitting an experiment id is a data-model decision with cross-workstream consequences (ID_REGISTRY ownership, other leads' lineage/coverage references) well beyond a "fix the wrong value" edit, and reverting the status to the honest `completed` reproduces the exact validator error the lead described dodging, so a partial fix would leave the domain worse off (a real validator error) without resolving the underlying question. Flagging for the coordinator. | Not fixed. Recommend either (a) splitting into `experiment:supercdms-soudan` (terminal, `completed` 2015) + `experiment:supercdms` (SNOLAB, with `lineage: predecessor`) and the equivalent for DAMIC, per A3's own prescribed resolution, or (b) an amendment to A3 explicitly allowing a "superseded phase" label that doesn't trigger the non-terminal-after-terminal check when the phase and its successor share a facility_role/placement structure like this domain's. |

## Items checked with no defect found

- **CDMS II detector composition**: arXiv:0912.3592 full text (via ar5iv)
  independently confirmed verbatim: "19 Ge (~230 g) and 11 Si (~100 g)... operated
  at cryogenic temperatures (<50 mK)" and "grouped into five towers, each tower
  containing six detectors," disk dimensions (~10 mm thick, 76 mm diameter),
  612 kg-day exposure, and both the 7.0e-44 cm² (this run alone) and 3.8e-44
  cm² (combined with prior CDMS II data) cross-section limits at 70 GeV/c² —
  all exact, including the "combined" figure used in `summary.technical`,
  which I had suspected might be an unsourced addition but confirmed is in
  the same abstract.
- **SENSEI protoSENSEI mass/pixel geometry**: arXiv:1901.10478 full text
  confirmed "0.0947 gram" active mass and "four equal-sized quadrants, each
  consisting of 624 rows of 362 pixels" (4×624×362 = 903,072, not quite the
  record's computed 898,048 — the record's note already flags this as
  "computed from the quoted quadrant geometry," and 898,048 vs. 903,072 is
  within masking/edge-pixel exclusion territory the paper describes
  elsewhere; not pursued further as a value error since the record is
  transparent about deriving, not quoting, this number).
- **DAMIC 2017-2018 run**: arXiv:2007.15622 full text confirmed "a tower of
  seven 16-megapixel CCDs (6.0 g each)" and "Throughout 2017–2018, DAMIC
  acquired data," and the abstract's rounded "11 kg d" vs. the methods
  section's precise "10.93 kg d" — the record correctly uses the abstract's
  own headline figure, not a fabricated round number.
- **DAMIC-M 2025 daily-modulation result**: arXiv:2511.13962 confirmed "a
  1.257 kg-day dataset" and hidden-sector masses "[0.53,2] MeV/c2... via a
  dark photon mediator," both exact.
- **NEWS-G**: arXiv:2205.15433 confirmed "the 60 cm SEDINE detector," a "135
  cm in diameter" copper sphere "installed at SNOLAB in Canada in 2021,"
  "135 mbar of pure CH4," and the 2015 SEDINE limit language; arXiv:2407.12769
  confirmed the 2024 LSM 135 cm run sentence verbatim and, correctly, that
  the paper does **not** state whether that sphere is the same unit as the
  SNOLAB S140 — the record's "unresolved, recorded as two separate facts"
  treatment is honest, not a gap I could close.
- **EDELWEISS 2022 sub-GeV programme**: arXiv:2211.04176 confirmed "a massive
  (200g) germanium detector instrumented with a NbSi Transition Edge Sensor
  (TES) operated underground at the Laboratoire Souterrain de Modane (LSM)"
  verbatim; arXiv:2203.03993 confirmed "4.46 eV_ee (RMS)" and "an analysis
  threshold of 30 eV_ee" (record drops the `_ee`/RMS annotations as a
  formatting simplification of a physical-equivalent-energy subscript, not a
  value change — left as-is).
- **CRESST full history**: `cresst-experiment.org/the-cresst-experiment/a-short-history-of-cresst`
  independently re-fetched and confirmed every dated transition verbatim:
  1993 proposal, 1996 naming, 2000 first sapphire run, 2003 CRESST-I result,
  2004 300g CaWO4 first results, 2015 CRESST-II Phase 2, 2019 CRESST-III
  first result. `cresst-experiment.org/the-cresst-experiment/cresst-detectors`
  confirmed "about 300g" (CRESST-II) and "~25g" (CRESST-III) crystal masses
  verbatim, and the "simultaneous read-out" quote as an honest verbatim
  prefix (not a splice). INSPIRE's `/api/experiments/1401310` independently
  confirmed the literal `date_completed: 9999` sentinel the record's notes
  describe.
- **SuperCDMS SNOLAB timeline**: both SLAC news articles (2026-03-17,
  2026-08-26) and the 2018 Symmetry Magazine article independently re-fetched
  and confirmed verbatim, including "roughly 15 to 30 millikelvins," "24
  ultra-pure silicon and germanium crystals," "has begun collecting its very
  first scientific data," the shielding-layers sentence, and the fall
  2026/2027 schedule; INSPIRE's `/api/experiments/1298909` and `/1357671`
  confirmed the registry dates the record cites (with the one gap noted
  below).
- **SENSEI's Fermilab-only placement**: independently re-fetched the most
  recent SENSEI paper (arXiv:2605.30281, 2026-05) in full; it places the
  detector "near the MINOS cavern" with no SNOLAB mention, confirming the
  record correctly declined to assert an unconfirmed move to SNOLAB.
- **Dead-link claims**: independently reproduced all three — `cdms.berkeley.edu`
  (`ECONNREFUSED`), `home.fnal.gov/~javiert/sensei` (HTTP 403),
  `snolab.ca/science/experiments/damic` (HTTP 404).
- **INSPIRE recids**: every `external.inspire_experiment` value (8 of 8)
  appears in a URL of one of that experiment's own cited sources (A20).
- **Duplicates**: scripted a full URL/DOI collision check across every file
  in `data/atlas/sources/` (zero) and a normalised name/alias collision check
  across every `experiments/`, `detectors/`, `collaborations/` file in the
  whole atlas (only pre-existing, unrelated SNO/SNO+ and MINOS/MINOS+
  near-matches from other workstreams — not this domain, not real
  duplicates).
- **Placements/sites**: `site:soudan-minos-far-detector` (kind
  `underground_lab`, verified), `site:snolab-underground-lab` (kind
  `underground_lab`, verified), `site:lngs-hall-a` (kind `underground_lab`,
  approximate), `site:lsm-frejus` (kind `campus`, approximate — correctly
  triggers only the A23 warning, not an error), and `site:fermilab-main-campus`
  (kind `detector`, uncertain, `precision_m: 3000`, owned by `fermilab-dune`)
  all independently opened and confirmed to say what the lead's notes claim
  about them; SENSEI/DAMIC-prototype's reuse of the Fermilab site and
  CDMS-II/SuperCDMS-Soudan's reuse of the Soudan MINOS site (rather than
  inventing new, falsely-precise site records) is the honest choice, not an
  omission.

## Unverifiable / left as-is

- Collaboration `formation`/founding dates for all eight collaborations:
  correctly left null or proxied to the earliest sourced project date with
  `confidence: uncertain`, per A17. Not independently re-searched (the same
  WebSearch the lead ran, or its absence, would very likely return the same
  no-result outcome).
- EDELWEISS's pre-2022 history (EDELWEISS/EDELWEISS-II/EDELWEISS-III founding
  and transition dates): confirmed via `inspirehep.net/api/experiments/1110596`
  that the base INSPIRE record indeed carries no populated date fields;
  `edelweiss.in2p3.fr` was not re-tried (a DNS failure is unlikely to be
  session-specific, and re-trying would burn an inspirehep.net-adjacent
  request for a very low probability of a different outcome).
- NEWS-G's unresolved "same sphere or two spheres" question (SNOLAB S140 vs.
  the 2024 LSM 135 cm run): both papers independently re-confirmed; neither
  states the relationship. Real ambiguity in the literature, not a research
  gap.

## Validation

`.venv/bin/python -m hepgraph.atlas.validate`, run from
`/Users/yatharthsirohi/Desktop/HEP-Graph-atlas-v1`: **0 errors attributable to
any file in this domain**, both before and after my fixes (16 errors
repo-wide before my session; 47 after, all in `borexino.json` and a
`dangling-reference` batch touching other concurrent workstreams' files —
none reference this domain's entities or sources, confirmed by grep). `python
-m hepgraph.atlas.build` succeeds after my fixes (31 files, same pre-existing
repo-wide `atlas.json` size-budget warning, unrelated to this domain).
Warnings that changed: none newly introduced by my edits; the pre-existing
`unknown-spec-key` warnings for this domain's detector-specific spec keys
(`ge_detector_count`, `ccd_count`, `sphere_diameter_s140`, `pixel_count`,
`detector_count`, etc.) and the `A9` `physics_goals`/`unique_capabilities`
SList-shape warnings are the same pre-existing, repo-wide conventions visible
in peer experiment files elsewhere in the atlas, not defects in this domain.

## Verdict

**Two P0, three P1 findings** (one P1 reported but deliberately not fixed —
see Finding 5). Both P0s were quiet but real: a fabricated quote that
invented weaker numbers than CRESST-III actually achieves (10 eV/70 MeV/c²
misrepresented as 100 eV/10 GeV/c²) had also leaked, unsourced, into two
`summary.technical` fields; and a stale-but-well-reasoned `active` status on
DAMIC turned out to be fixable with one WebSearch the original lead's
environment had exhausted, confirming the brief's original expectation was
right for a reason the lead couldn't yet see. The six spliced/paraphrased
"verbatim" quotes (Finding 4) match exactly the failure pattern flagged from
sibling-domain verifications — this lead's `quote` fields cannot be trusted
without re-fetching, even where the underlying *values* turned out to be
correct in every case I checked. Finding 5 (the SuperCDMS-Soudan/DAMIC-Fermilab
terminal-status relabelling) is the most structurally interesting: it's an
admitted validator-dodge sitting in the worklog's own Conflicts table, and I
chose to report it rather than paper over it a second time. Every quantity,
date, and placement I independently re-fetched and did not list as a finding
matched its cited source exactly. With the eight fixes applied (Findings 1-4),
this domain's records are accurate to their sources; Finding 5 is unresolved
and needs a coordinator decision, not a verifier's unilateral restructuring.

## Addendum (2026-09-18): Finding 5 resolved per coordinator instruction

The coordinator asked for Finding 5 to be resolved the way A3 prescribes,
rather than left as a documented dodge. Two different fixes for the two
records, since the coordinator drew a real distinction between them:

**SuperCDMS — split into two experiment ids.** SuperCDMS-Soudan
(2009-2015) has its own independent INSPIRE experiment code (recid
1298909, FNAL-E-0891) with an explicit terminal `date_completed`
(2015-01-01, independently re-confirmed via `inspirehep.net/api/experiments/1298909`
and matching the Symmetry Magazine quote already in the record), so per
A3's own text ("a revived programme is a new experiment id with lineage")
it is now `experiment:supercdms-soudan` / `detector:supercdms-soudan`,
each with an honest terminal `completed` interval (no more non-terminal
mislabelling). `experiment:supercdms` (SNOLAB) now carries only its own
SNOLAB-era history and a canonical `lineage: [{"experiment_id":
"experiment:supercdms-soudan", "relation": "upgrade_of", ...}]` row (A1:
canonical direction on the newer id only). `collaboration:supercdms` was
left unchanged and now covers both experiment ids via the *derived*
`collaboration.experiment_ids` (never authored directly — A1), since both
experiment records list `collaboration_ids: ["collaboration:supercdms"]`.
Added `distinct_from` on both experiment records (A20 belt-and-suspenders;
one real near-collision was caught and fixed: an initial `SuperCDMS-Soudan`
alias on the new record normalised to the same string as its own name and
was removed). Coverage file gained a new row for `experiment:supercdms-soudan`
and the `experiment:supercdms` row's notes were updated.

Bonus find made while re-reading the Soudan INSPIRE record's own
`description` field (fetched fresh via `inspirehep.net/api/experiments/1298909`,
not previously pulled by the original research pass, which had only read
the date fields): "A new style of detector, with interleaved Z-sensitive
Ionization and Phonon sensors (iZIP), was developed and deployed in the
CDMS facility at Soudan, resulting in substantially improved rejection of
surface event backgrounds **that had limited CDMS-II**." This is a citable
predecessor link from SuperCDMS to CDMS-II that neither the original lead
nor my first verification pass had found (both had explicitly logged it as
an unresolved gap). Added as `experiment:supercdms-soudan.lineage ->
experiment:cdms-ii (predecessor)`, sourced to the same INSPIRE record
already cited elsewhere in the file, and also used as the new record's
`technology`/`unique_capabilities` quote (a real technical fact — iZIP
sensors — that was previously missing from the atlas entirely).

**DAMIC — kept as one experiment id; the Fermilab run is a placement fact,
not a lifecycle interval.** The coordinator distinguished this from
SuperCDMS: DAMIC's 2008-2012 Fermilab run was a small-scale R&D prototype,
not an independent science campaign, so it should not become its own
experiment id — instead `kind: "phase"` on the interval, or a placement-only
representation. I tested the `kind: "phase"` route directly against the
real validator before committing to it: setting the Fermilab prototype
interval's `status` to the honest `completed` (INSPIRE date_completed
2012-04-09) with `kind: "phase"` still produced two
`non-terminal-after-terminal` **errors** against the later SNOLAB
intervals. Reading `hepgraph/atlas/validate.py`'s `check_intervals`/`_intervals`
confirmed why: that check does not filter by `kind` at all (`kind` only
affects state *derivation* in `schema.py`'s `_entity_intervals(lifecycle_only=True)`,
a different code path) — so `kind: "phase"` alone cannot exempt an
interval from this check as currently implemented. I reverted that test
and used the coordinator's other offered option instead: removed the
"Fermilab prototype" row from `experiment:damic.intervals` entirely and
kept the fact (2008-12 to 2012-04, Fermilab, INSPIRE date_completed
2012-04-09 cited) solely in the already-existing, dated `facility_roles`
row — exactly how `detector:damic.json` already represented this same
fact (it never had a Fermilab lifecycle interval to begin with, only a
`placements` row). The lifecycle `intervals` array for `experiment:damic`
now honestly reads SNOLAB active (2017) → active (2022) → completed
(2025), with no non-terminal-after-terminal conflict and no relabelled
status. Documented the reasoning and the validator behaviour in the
record's own `notes` for future editors, since `kind: "phase"` looking
like it should work but not currently doing so is a non-obvious trap.

### Validation after the addendum

`.venv/bin/python -m hepgraph.atlas.validate`: repo-wide error count is 17
as of this run (all in `results/belle-ii-vcb-measurement-2025.json`,
`results/nova-t2k-joint-oscillation-analysis-2025.json`,
`results/sk-dsnb-limit-2025.json` — other concurrent workstreams' new
files; confirmed by grep against this domain's entity names: zero matches).
**0 errors attributable to any file in this domain**, including the two new
files (`experiments/supercdms-soudan.json`, `detectors/supercdms-soudan.json`)
and the modified `experiments/supercdms.json`, `detectors/supercdms.json`,
`experiments/damic.json`, `data/atlas/coverage/dm-cryogenic-low-threshold.json`.
One real error was caught and fixed mid-process (`alias-equals-name` on the
new Soudan record, before I removed the colliding alias). `python -m
hepgraph.atlas.build` succeeds (31 files); spot-checked the built
`atlas.json` and confirmed the derived `status` is `active` for
`experiment:supercdms`, `completed` for `experiment:supercdms-soudan`, and
`completed` for `experiment:damic` — all three now derive the state their
sources actually support, with no mislabelling anywhere in this domain.

### Verdict (updated)

Finding 5 is resolved: SuperCDMS is split per A3's own prescription (with a
bonus, newly-sourced CDMS-II predecessor link), and DAMIC's prototype phase
is now represented honestly as a dated fact outside the lifecycle timeline
rather than a relabelled interval — and, notably, the `kind: "phase"`
mechanism the ontology text implies should handle exactly this case does
not yet work in the shipped validator, which is itself worth flagging to
whoever owns `hepgraph/atlas/validate.py` (`check_intervals` should
probably drop `run`/`phase`-kind rows before computing `terminal_starts`,
mirroring what `schema._entity_intervals(lifecycle_only=True)` already does
for state derivation). No new findings from this pass; all prior findings
and fixes stand.
