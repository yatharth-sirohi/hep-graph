# Independent verification: fixed-target (wave 3)

Verifier session, 2026-09-17/18. Did not write the original fixed-target
records; treated `docs/atlas-worklog/fixed-target.md` as unverified claims,
not evidence. All source claims below were re-fetched with WebFetch/WebSearch
in this session (or, for INSPIRE, via the JSON API endpoint, since the HTML
pages are client-rendered and return no content to WebFetch). No git, no
subagents, ≤ 1 inspirehep.net request/10s observed throughout.

## Records checked

All ten experiment records and their matching `detectors/`, `collaborations/`
files, the three sites (`cern-ecn3-north-area`, `fermilab-ktev-hall`,
`fermilab-nm4-hall`), `documents/na62-detector-jinst-2017.json`, the three
`results/na62-*` records, `data/atlas/coverage/fixed-target.json`, and every
`src:na62-*`, `src:na48-*`, `src:na64-*`, `src:ktev-*`, `src:seaquest-*`,
`src:darkquest-*`, `src:ship-*`, `src:mathusla-*`, `src:e949-*`, `src:koto-*`
source record cited from them (34 source records read).

## Sources re-fetched this session (~30 distinct URLs/API calls)

arXiv abstracts: 2103.15389, 2412.12015, 2604.12649, 2607.16413 (x2, second
pass asked for verbatim reproduction), 1703.08501, hep-ex/0209064, 1112.5365,
1706.09990, hep-ex/0409064, 2606.11039, 2504.06692, 1811.00927, 2203.08322.
Official/press pages: home.cern (2026 refined-measurement article, NA64
experiments page), na62.web.cern.ch/Home/Aim.html, na64.web.cern.ch,
koto.kek.jp, mathusla-experiment.web.cern.ch, ship.web.cern.ch,
cerncourier.com (two articles: "Fixed target, striking physics", "SHiP to
chart hidden sector"). INSPIRE JSON API (`inspirehep.net/api/experiments/*`
and `/api/literature/*`): NA62 (1275752), NA48 (1108767), NA64 (1479798),
KTeV (1108757), KOTO (1108227), E949 (1108526), SeaQuest (1108442), SHiP
(1388776), MATHUSLA (1716435), plus two KTeV literature records
(510045, 345348). Two WebSearch queries for the SHiP 2024/2033 dating and
one for BDF/SHiP construction status.

## Findings and fixes

### P0 (fixed)

1. **A16 violation — result claim sourced to a press release.**
   `result:na62-2026-refined-measurement`'s `claim.quote` and `publication`
   were sourced only to `src:na62-cern-news-2026-refined-measurement`
   (`source_type: press_release`), which A16 explicitly forbids. By
   2026-09-17 a full arXiv paper restating the identical central value now
   exists: arXiv:2607.16413, "Measurement of the branching ratio of the
   K+ -> pi+ nu nubar decay" (NA62 Collaboration, submitted 17 July 2026,
   CERN-EP-2026-214), B(2016-2024) = (9.6+1.9-1.8)e-11, confirmed verbatim
   against the fetched abstract. Added `src:fixed-target-verify-na62-refined-arxiv-2607-16413`
   and re-sourced `claim`, `key_value`/`key_value_text`, `publication`,
   `publication_source_id` to it; kept the press release only for the
   `announced` date (2026-03-04, La Thuile conference preview) alongside a
   new `published` date (2026-07-17), mirroring the existing
   announcement-then-publication pattern already used elsewhere (e.g.
   `cms-higgs-boson-observation-2012`). Also noted an intermediate
   conference-proceedings preprint (arXiv:2604.12649) that restates the same
   value from a preliminary analysis. Propagated the fix into
   `experiment:na62`'s Run 2 interval/sources/notes and
   `data/atlas/coverage/fixed-target.json`.

2. **A23 violation — campus-grade coordinates dishonestly labelled `detector`.**
   `site:cern-ecn3-north-area`, `site:fermilab-ktev-hall` and
   `site:fermilab-nm4-hall` all had `coordinates.kind: "detector"` while each
   record's own `coordinates.note` admits the point is a reused *campus*
   coordinate with no surveyed hall/cavern position ("Treat this as campus
   precision, not cavern/hall precision"). A23 explicitly forbids exactly
   this: relabelling a campus point `detector` to satisfy the validator.
   Confirmed the effect directly in `hepgraph/atlas/validate.py`
   (`check_coordinates`): with `kind: detector`, the A23 branch never
   triggers, so the validator passed silently; with the honest `kind:
   campus` (which all three already had `confidence: approximate|uncertain`
   and a note for), it correctly emits a `coordinate-kind-approximate`
   *warning* instead. Fixed `kind` to `"campus"` in all three files and
   re-ran the validator to confirm the warning now fires as intended.

3. **Lineage contradicted its own cited source.** `experiment:darkquest`'s
   `lineage` asserted `{"experiment_id": "experiment:seaquest", "relation":
   "upgrade_of"}`, sourced to arXiv:2203.08322. Refetched that paper: its
   title is "DarkQuest: A dark sector upgrade to **SpinQuest** at the 120 GeV
   Fermilab Main Injector" and the abstract never mentions SeaQuest. The
   record's own prose note already flagged this as "a simplification," but
   the structured `lineage` field still asserted a relationship the source
   does not support. Removed the row (`lineage: []`); SpinQuest
   (Fermilab E-1039) is out of this wave's `ID_REGISTRY` scope, so no
   `experiment:spinquest` id was created to replace it — the relationship is
   now recorded only in prose (existing `unique_capabilities`/`summary`
   text, plus an updated note), per ground rule 3 ("unknown is a value").

### P1 (fixed)

4. **MATHUSLA `status: null` masked an available date.** Both
   `experiment:mathusla` and `collaboration:mathusla` had their only interval
   at `start: null`, which under A3 covers no year at all, so the derived
   state was `unrecorded` and `status` was written as `null` to match — even
   though the collaboration's first public proposal, the MATHUSLA Letter of
   Intent (arXiv:1811.00927, submitted 2 Nov 2018, confirmed by direct
   fetch), gives a citable anchor. Anchored both intervals at `2018-11` and
   corrected `status` to `"proposed"` (experiment) and `"active"`
   (collaboration); added `src:fixed-target-verify-mathusla-loi-arxiv-1811-00927`.
   Updated `data/atlas/coverage/fixed-target.json` to match.

5. **SHiP 2024 approval under-sourced.** The `approved for ECN3` interval on
   `experiment:ship` rested only on a Wikipedia pointer (rank 12,
   `confidence: uncertain`), even though the brief's target rank (≤10) was
   reachable: arXiv:2606.11039, "The SHiP/NA67 experiment at the ECN3
   high-intensity beam facility at the CERN SPS" (SHiP Collaboration,
   9 June 2026), states verbatim in its abstract "approved in 2024,"
   corroborated by a second 2025 SHiP paper (arXiv:2504.06692) and by CERN
   Courier ("SHiP to chart hidden sector," 3 May 2024, secondary/rank 12).
   Added `src:fixed-target-verify-ship-bdf-ecn3-arxiv-2606-11039` and
   upgraded that interval to `confidence: verified`. Left the `2033`
   planned-start interval as `uncertain`/Wikipedia-sourced: the CERN Courier
   article quotes an *earlier* internal aim (commission the facility by
   end-2030, detector 2031), and later 2025/2026 conference talks found via
   WebSearch describe a 2032-2033 first-physics window, but no rank ≤10
   source stating "2033" verbatim was directly fetched this session, so the
   existing honest hedge was kept rather than upgraded on secondary
   aggregation. Also confirmed (but did not act on) that at least one 2026
   SHiP paper now calls the programme "SHiP/NA67" — flagged as a follow-up,
   not asserted as a renaming, since `ship.web.cern.ch` itself still uses
   only "SHiP".

6. **Spliced (non-verbatim) quote on the flagship record.** NA62's
   `physics_goals[0].quote` read "Measure the very rare kaon decay K+ ->
   pi+ nu nubar at the CERN SPS to extract a 10% measurement of the CKM
   parameter \|Vtd\|." Refetching na62.web.cern.ch/Home/Aim.html, the actual
   sentence is "**NA62 initially proposed to** measure the very rare kaon
   decay..." — the quote dropped the leading clause and capitalised
   "measure" to make it read as a bare imperative. This is exactly the
   splicing failure mode called out in the assignment brief. Fixed to the
   full, verbatim sentence, and added a note that the page itself frames the
   10% figure as the *initial* proposed precision (not the precision
   actually achieved — the delivered results are 20% or worse).

7. **Canonical-formatting violations (A11).** `json.dumps(sort_keys=True,
   indent=2, ensure_ascii=False)` was not followed (non-alphabetical, "field
   order" formatting instead) in: `experiments/{na62,na48,na64,ktev,koto,darkquest}.json`,
   `detectors/{na62,na64}.json`, `collaborations/na62.json`,
   `sites/cern-ecn3-north-area.json` (fixed as a side effect of finding #2),
   `documents/na62-detector-jinst-2017.json`,
   `results/{na62-jhep-2021-measurement,na62-jhep-2025-observation}.json`.
   Reformatted all of these to canonical order; no content changed beyond
   what is listed under the other findings above. (`seaquest`, `ship`,
   `mathusla`, `e949`, `ktev`-collaboration/detector, etc. were already
   canonical.) Note this is a repo-wide issue — many files outside this
   verifier's scope (other domains' `sno`, `juno`, `reno`, etc.) are also
   non-canonical — but only in-scope files were touched.

### P2 (documented, not changed)

8. `detector:na62`'s "commissioning" interval end (2015) is a defensible
   but unstated inference from the JINST paper's "early performance...from
   2014 and 2015 data," not an explicit "commissioning ended in 2015"
   sentence; `confidence: verified` slightly overstates how directly this
   boundary is sourced. Left as-is (a reasonable reading, not a
   contradiction).

9. Structurally identical facts carry different confidence: `experiment:na48`'s
   "completed" interval (start 2004, no end) is `confidence: uncertain`
   ("no source states an explicit end-of-programme date"), while
   `detector:na48`'s equivalent terminal-event row for the same fact is
   `confidence: verified`. Both are defensible; flagged for consistency,
   not fixed.

10. `experiment:seaquest`'s "completed" interval is anchored on the
    **December 2025** "Final SeaQuest results" paper rather than the actual
    end of data-taking (commonly cited elsewhere as ~2017, but not confirmed
    by any source fetched in this session or the original pass). This is
    honest (no fabricated date) but leaves 2018-2024 as an `unrecorded` gap
    in the derived state timeline rather than showing "completed" throughout
    — a materially misleading rendering even though every individual value
    is correctly sourced. A source giving the actual data-taking end year
    was not found within this session's budget; recommended as a follow-up
    for whoever next touches SeaQuest.

11. `detector:na62.specs.gigatracker_track_time_resolution` is not an
    Appendix A spec key (pre-existing validator warning, not an error); no
    clearly correct substitute key exists for a spectrometer-class timing
    figure, so left as-is, consistent with several other detectors' custom
    keys elsewhere in the repo (`ge_detector_count`, `pixel_count`, etc.).

## Checked and found correct (no changes)

- NA62 2021/2025/2607.16413 result titles, dates, branching-ratio values,
  uncertainties and significance all match their arXiv abstracts verbatim
  (3.4σ / 10.6+4.0-3.4e-11; >5σ / 13.0+3.3-3.0e-11; 9.6+1.9-1.8e-11 with 20%
  precision).
- NA48 approval year (1991, CERN Courier verbatim), final-epsilon'-paper run
  years (1997/1998/1999/2001 — the record's existing "CONFLICT" note
  correctly preferred the primary source over a secondary aggregation
  claiming "2000"), and NA48/2 2003-2004 data-set quote, all confirmed
  verbatim.
- NA64: proposal (Jan 2014), CERN Research Board approval (9 March 2016),
  100-150 GeV electron beam, 2016 operations start — all confirmed verbatim
  against na64.web.cern.ch and home.cern.
- KOTO, MATHUSLA (aside from the status fix), SeaQuest spectrometer, E949
  (both cited arXiv papers) quotes all checked verbatim against fetched
  abstracts/pages; no splicing found beyond finding #6.
- INSPIRE recids for all nine experiments that carry one (NA62 1275752,
  NA48 1108767, NA64 1479798, KTeV 1108757, KOTO 1108227, E949 1108526,
  SeaQuest 1108442, SHiP 1388776, MATHUSLA 1716435) confirmed correct via
  the INSPIRE JSON API. DarkQuest's `inspire_experiment: null` is honest
  (no proposal-stage INSPIRE experiment record exists).
- Units, dimensions and `display`/`value` cross-checks on the key_specs
  present (NA62 400 GeV beam momentum, 65 ps GigaTracker resolution;
  MATHUSLA 40x40x11 m decay volume) all correct.
- `data/atlas/coverage/fixed-target.json` `missing_fields` entries were
  spot-checked against the record content and are honest, except the three
  now-stale ones corrected above (NA62 press-release note, DarkQuest
  lineage note, MATHUSLA/SHiP status/sourcing notes).
- No duplicate ids, aliases, DOIs, arXiv ids, INSPIRE recids or source
  URLs/DOIs across fixed-target records (confirmed by the validator's A20
  checks — 0 errors touch this domain).

## Unverifiable values (left as-is, already honestly hedged by the original pass)

- NA48/1 (2002) sub-programme dates (no rank ≤10 source found by either
  pass).
- Exact KTeV, SeaQuest and E949 calendar run-year breakdowns (all already
  correctly left `null`/uncertain rather than asserted from memory).
- SHiP's exact first-physics-data year (2033 vs. an earlier-quoted 2031
  facility-commissioning target — see finding #5).

## Validator

`.venv/bin/python -m hepgraph.atlas.validate` (run from
`/Users/yatharthsirohi/Desktop/HEP-Graph/.venv/bin/python`, against this
worktree), run three times to confirm stability: **0 errors attributable to
fixed-target in every run.** The first two runs (4, then transiently 30,
errors) reflected other domains only: `experiments/gallex-gno.json` /
`results/borexino-pp-first-detection-2014.json`, and then a same-worktree
race with a concurrent verifier agent mid-write on SAGE records (this
worktree is evidently shared by more than one verifier session; its
untracked `sage-*`/`VERIFY_axions.md` files are not mine). A clean re-run
after that write settled shows **1 error in the whole repository**
(`results/sage-capture-rate-1999.json`, again a different domain), **0**
touching fixed-target, and 0 warnings/errors on any of the new
`src:fixed-target-verify-*` sources. All fixed-target-relevant findings are
warnings-only after the fixes above (e.g. `coordinate-kind-approximate` now
correctly fires for the three campus-grade sites instead of being silently
bypassed).

## Verdict: NA62 (flagship)

**Clean as of this pass.** One P0 (A16 press-release claim source) and one
P1 (spliced quote) were found directly on NA62/its result records and are
now fixed with re-fetched, verbatim-checked, rank-appropriate sources; every
other NA62 fact checked (three result papers, JINST detector paper,
GigaTracker paper, aim page, INSPIRE recid, North Area beamline claim) was
independently re-confirmed verbatim against the live source with no
contradictions found. Zero unresolved factual contradictions remain on
NA62 after this verification pass.
