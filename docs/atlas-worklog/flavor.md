# Research log — flavor (Belle / Belle II, KEKB / SuperKEKB)

Agent: `flavor`. Worked in the `hep-atlas-globe` worktree.
All values verified on **2026-09-16** against sources fetched in this session.

## Scope

One deeply researched flavour programme at KEK, Tsukuba: the KEKB and SuperKEKB
colliders, the Belle and Belle II experiments, their detectors and
collaborations, the Tsukuba interaction region, six physics results plus one
technology milestone, and the five reference documents. `facility:kek` is owned
by the japan-neutrino workstream and was **referenced only, never created**; it
already exists in `data/atlas/facilities/kek.json`, so no reference dangles.

## Entities written (ids)

Sites
- `site:kek-tsukuba-belle-ii`

Accelerators
- `accelerator:kekb`
- `accelerator:superkekb` (lineage `upgrade_of` → `accelerator:kekb`)

Experiments
- `experiment:belle`
- `experiment:belle-ii` (lineage `predecessor` → `experiment:belle`)

Detectors
- `detector:belle`
- `detector:belle-ii`

Collaborations
- `collaboration:belle`
- `collaboration:belle-ii`

Results
- `result:belle-cp-violation-observation-2001`
- `result:belle-x3872-observation-2003`
- `result:belle-b-to-tau-nu-evidence-2006`
- `result:belle-d0-mixing-evidence-2007`
- `result:belle-ii-tau-mass-measurement-2023`
- `result:belle-ii-b-to-k-nunu-evidence-2023`
- `result:superkekb-luminosity-world-record-2026` (`technology_milestone`)

Documents
- `document:belle-detector-nima-2002`
- `document:belle-ii-tdr-2010`
- `document:belle-ii-physics-book-2019`
- `document:superkekb-collider-nima-2018`
- `document:kekb-accelerators-overview-nima-2003`

Coverage
- `data/atlas/coverage/flavor.json` (rows for `experiment:belle`, `experiment:belle-ii`)

## Sources added (ids)

Official experiment sites (rank 1)
- `src:belle2-collaboration-site` — https://www.belle2.org/
- `src:belle2-detector-page` — https://www.belle2.org/about_us/belle_ii_detector/
- `src:belle2-superkekb-page` — https://www.belle2.org/about_us/superkekb_accelerator/
- `src:belle2-collaboration-page-jp` — https://belle2.jp/the-collaboration/
- `src:belle2-rollin-2017` — https://belle2.jp/2017/06/26/belle-ii-detector-rolled-in/
- `src:belle2-institutes-list` — https://public.belle2.org/downloads/institutes.html
- `src:belle-legacy-site` — https://belle.kek.jp/

Official facility sites (rank 2)
- `src:kekb-ring-kek` — https://www2.kek.jp/accl/eng/fa_accl-en/kekb-ring/
- `src:superkekb-project-site` — https://www-superkekb.kek.jp/
- `src:superkekb-feature-story` — https://www-superkekb.kek.jp/feature-story
- `src:superkekb-run2-start-2024` — https://www2.kek.jp/ipns/en/news/5414/

INSPIRE experiment records (rank 3)
- `src:belle-inspire-experiment` — https://inspirehep.net/experiments/1108579
- `src:belle2-inspire-experiment` — https://inspirehep.net/experiments/1108235

Design report / detector paper (ranks 4–5)
- `src:belle2-tdr-2010` — arXiv:1011.0352 (KEK Report 2010-1)
- `src:belle-detector-nima-2002` — NIM A 479 (2002) 117, read via INSPIRE lit. 541364

Press releases (rank 9)
- `src:superkekb-lumi-record-2020` — https://www2.kek.jp/ipns/en/release/20200626/
- `src:superkekb-phase3-start-2019` — interactions.org copy of the KEK release

Journal / arXiv (rank 10)
- `src:belle2-espp-input-2025` — arXiv:2503.24155
- `src:belle2-physics-book-2019` — PTEP (2019), doi 10.1093/ptep/ptz106
- `src:belle2-tau-mass-2023` — arXiv:2305.19116
- `src:belle2-b-to-k-nunu-2023` — arXiv:2311.14647 / PRD 109, 112006
- `src:belle-cp-violation-2001` — arXiv:hep-ex/0107061 / PRL 87, 091802
- `src:belle-x3872-2003` — arXiv:hep-ex/0309032 / PRL 91, 262001
- `src:belle-b-to-tau-nu-2006` — arXiv:hep-ex/0604018 / PRL 97, 251802
- `src:belle-d0-mixing-2007` — arXiv:hep-ex/0703036 / PRL 98, 211803
- `src:superkekb-collider-nima-2018` — arXiv:1809.01958 / NIM A 907 (2018) 188
- `src:kekb-accelerators-overview-nima-2003` — NIM A 499 (2003) 1, via INSPIRE lit. 572361

Wikipedia (rank 12, pointer only)
- `src:belle2-wikipedia-coordinates` — https://en.wikipedia.org/wiki/Belle_II_experiment

Every one of these was fetched with WebFetch in this session; every source record
carries `accessed: 2026-09-16` and a `retrieval` value. No source is marked
`failed`, and no source is cited that was not read.

## Conflicts

| claim | source A | source B | chosen | why |
| --- | --- | --- | --- | --- |
| SuperKEKB design/target peak luminosity | 8×10³⁵ cm⁻²s⁻¹ — SuperKEKB accelerator paper (arXiv:1809.01958 / NIM A 907, 2018) and belle2.org "goal of increasing the instantaneous luminosity by a factor of ~40 to 8.0x10³⁵" and www-superkekb.kek.jp "The target luminosity is 8×10³⁵" | 6.0×10³⁵ cm⁻²s⁻¹ — Belle II input to the European Strategy, arXiv:2503.24155 (2025) | **6.0×10³⁵** recorded as `specs.design_luminosity`; 8×10³⁵ quoted in its `note` | The 2025 collaboration document is the most recent statement of the machine's target; the older value is preserved verbatim, not discarded. The task brief also gave 6×10³⁵. |
| KEKB peak luminosity | 2.11×10³⁴ cm⁻²s⁻¹ — belle.kek.jp and the 2020 KEK IPNS press release | 2.1×10³⁴ cm⁻²s⁻¹ — KEK Accelerator Laboratory KEKB ring page | **2.11×10³⁴** | The KEKB ring page rounds; two independent sources give the three-digit value. |
| Belle data-taking start | May 1999 — INSPIRE experiment record KEK-BF-BELLE (`date_started`) | "June 1999" / first B events on 1 June 1999 — secondary accounts found in search snippets only, not fetched | **1999-05** with a note | Rule 5/A17: only a fetched source may set a critical value. The June date is recorded in the interval `note` as unconfirmed. |
| Belle II Run 1 start | 2018 — "Belle II began collecting electron-positron collision data in 2018 ('Run 1')" (arXiv:2503.24155) | 11 March 2019 — KEK press release "SuperKEKB Phase 3 (Belle II Physics Run) Starts" | **2019-03-11** for the Run 1 / Phase 3 *physics* interval, with a separate Phase 2 commissioning interval for 2018 | The 2018 collisions were the Phase 2 pilot run without the full vertex detector; the atlas keeps both as separate intervals rather than collapsing them. |
| Belle II recorded integrated luminosity | 914 fb⁻¹ — belle2.org, read 2026-09-16 | "about 575 fb⁻¹" — arXiv:2503.24155 (March 2025) | **914 fb⁻¹** | Not a real conflict: the figures are 18 months apart. Both are quoted in the field note. |
| Belle II peak luminosity | 5.319×10³⁴ on 30 June 2026 — belle2.org | 5.1×10³⁴ — arXiv:2503.24155 (2025); 2.22×10³⁴ on 15 June 2020 — KEK IPNS | **5.319×10³⁴ (2026-06-30)** | Same machine, successive records; the earlier two are recorded in notes on `accelerator:superkekb` and on the milestone result. |

## Unresolved fields

1. **`site:kek-tsukuba-belle-ii` coordinates — REVIEW REQUIRED.** No official KEK,
   SuperKEKB or Belle II page, and no technical paper reachable in this session,
   publishes latitude/longitude for the Tsukuba interaction region. KEK's own
   access page gives only the postal address (1-1 Oho, Tsukuba, Ibaraki 305-0801);
   the campus and SuperKEKB pages carry maps as images, not coordinates; searches
   of arXiv/JACoW for a geodetic survey paper returned nothing usable. The record
   therefore carries 36.15778 N, 140.07500 E from the Wikipedia infobox for the
   Belle II experiment (rank 12), `confidence: "uncertain"`, `precision_m: 300`,
   and an explicit note that **v0.2 A17 does not accept a rank-12 source as the
   sole source for `kind: detector` coordinates**. A site cannot be written
   without coordinates (§9), so the value is present and flagged rather than
   silently omitted. Replace it with a KEK survey/geodetic source when one is found.
2. **`site:kek-tsukuba-belle-ii.depth`** — null. SuperKEKB is often described as
   roughly 11 m underground, but not on any source fetched here.
3. **`detector:belle` subsystems and dimensions** — empty. The Belle detector
   paper (NIM A 479 (2002) 117) is paywalled at Elsevier and blocked to automated
   fetching (`linkinghub.elsevier.com` returns only a redirect shell). Only the
   title, abstract fragment, DOI and journal reference were obtained, via the
   INSPIRE literature record. The 1.5 T solenoid field is the only sourced spec.
4. **`detector:belle-ii` overall dimensions and per-subsystem quantities** — the
   TDR body (arXiv:1011.0352) was not fetched, only its abstract page. The
   detector's 8 m height and 1400 t mass come from the collaboration's roll-in
   article; the mass is recorded as `specs.total_mass`, the height only in a note
   because `height` is not in the Appendix A spec-key whitelist for
   `general_purpose_collider`.
5. **`accelerator:kekb` construction/commissioning intervals** — no fetched source
   dates the start of KEKB construction or first beam; only "started its operation
   in 1998" and "concluded its operation in June 2010" are recorded.
6. **`accelerator:kekb.specs.circumference`** — `confidence: "derived"`. The 3 km
   figure is belle2.org's description of SuperKEKB, which reuses the KEKB tunnel;
   no fetched source states the KEKB circumference directly.
7. **Leadership** — `collaboration:belle` and `collaboration:belle-ii` have empty
   `leadership`; no fetched page names spokespersons.
8. **Belle II membership `as_of`** — belle2.jp gives "over 1100 physicist and
   engineers from 122 institutions in 27 countries" with **no date**; `as_of` is
   set to the access month (2026-09) and the absence of a published date is noted.
   The official institute list (public.belle2.org) carries names but no totals.
9. **`collaboration:belle` formation** — `confidence: "uncertain"`, taken from the
   INSPIRE proposal/approval year (1994), not from a collaboration statement.
   Its membership counts (60+ institutions, 14 countries) are undated and are
   therefore tagged `evidence_class: "derived"`.
10. **τ-mass paper journal reference** — the arXiv abstract page carried no journal
    reference when read, so `result:belle-ii-tau-mass-measurement-2023` is recorded
    as a preprint. The PTEP article number "123C01" for the Belle II Physics Book
    was likewise not confirmed and is not recorded.
11. **`facility:kek`** — exists (owned by japan-neutrino) and is referenced by the
    site, both accelerators, both experiments' `facility_roles` and both
    collaborations' `host_facility_id`. Its `primary_site_id` was still `null` when
    this log was written; the japan-neutrino lead may wish to point it at a KEK
    campus site (not at `site:kek-tsukuba-belle-ii`, which is the collision hall).

## Children spawned and what I re-checked

**None.** The task brief forbade spawning child agents, so all fetching,
transcription and checking was done directly by this agent; every quote in the
data files was copied from content returned by a WebFetch call made here.

## Schema notes

- `experiment.facility_roles` and `detector.placements` are used (A2); the legacy
  scalars `detector.site_id` / `detector.facility_id` and `experiment.facility_ids`
  are not written.
- Derived fields (A1) are **not** authored: no `experiment.detector_ids`,
  `experiment.site_ids`, `experiment.result_ids`, `*.document_ids`,
  `accelerator.beamline_ids`, `accelerator.serves_experiment_ids` or
  `collaboration.experiment_ids`.
- Accelerator lineage (`superkekb upgrade_of kekb`) is expressed as a `lineage`
  list keyed on `accelerator_id`, mirroring `experiment.lineage`; A1 defines the
  canonical direction only for experiments, so this shape may need ratifying.
- `accelerator.specs.design_luminosity` and `accelerator.specs.collision_scheme`
  are keys outside the §3.3 list; they carry `dimension: luminosity` and a sourced
  string respectively.
- All files carry `"schema": "hep-atlas/0.2"` and canonical formatting
  (`sort_keys=True, indent=2, ensure_ascii=False`, trailing newline).

## Confidence summary

- **verified** — KEKB and SuperKEKB beam energies, SuperKEKB circumference, √s,
  peak and target luminosities, all interval bounds except those noted below, the
  1.5 T solenoid fields, the Belle II detector mass and subsystem list, both
  INSPIRE experiment recids, Belle II membership counts, and all seven result
  claims (each with a verbatim `claim.quote` from the paper title/abstract or the
  collaboration's own page, plus `date_kind`, DOI/arXiv where published).
- **derived** — KEKB circumference; Belle `energy_regime` and
  `unique_capabilities`; the SuperKEKB interaction-region installation interval
  (2016-06 → 2018-03, bounds inferred from the accelerator paper's Phase 1 and
  Phase 2 dates).
- **approximate** — Belle II collaboration `member_count` ("over 1100");
  Belle `institution_count` / `country_count`; KEKB integrated luminosity
  ("> 1000 fb⁻¹"); Belle II Physics Book formation year; the "summer of 2022"
  Run 1 / LS1 boundary.
- **uncertain** — the interaction-region coordinates (item 1 above),
  `collaboration:belle.formation`, and the three `significance` fields that are
  genuinely not reported (2001 CP-violation paper, τ-mass, luminosity milestone),
  each null with a note.

## Validation run

`hepgraph/atlas/validate.py` did not exist when this work finished (the module
contains `load.py`, `schema.py`, `scaffold.py`, `linkcheck.py`). The fallback
check from rule 11 was run and passes:

```
.venv/bin/python -c "import json,glob;[json.load(open(f)) for f in glob.glob('data/atlas/**/*.json',recursive=True)]"
```

In addition, every typed id referenced from a flavor-owned file was checked
against the set of ids present in `data/atlas/`: **no dangling references**, and
no `src:` record of mine shares a normalised URL or DOI with any other source in
the repository.
