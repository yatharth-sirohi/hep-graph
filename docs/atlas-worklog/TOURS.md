# Tours (owner tag: `tours`, branch `atlas-m3-tours`)

2026-10-26. Workstream 3 of `docs/HEP_ATLAS_TEACHING_PLAN.md`: the tour format, its
validator, the lazy `tours.json` bundle, the six launch tours, and
`experiment:gargamelle`.

## Scope

* **Format.** Amendment A28 in `docs/HEP_ATLAS_ONTOLOGY.md` (after A26; A27 belongs
  to another stream). A new entity type `tour` (`data/atlas/tours/<slug>.json`, id
  `tour:<slug>`). Code: `hepgraph/atlas/tours.py` (resolver, validator, bundle,
  authoring CLI), one line each in `schema.py` (type + field table), `validate.py`
  (`check_tours`) and `build.py` (writes `tours.json`; a tour is kept out of the
  stripper, so provenance and `cited_by` are unchanged). Bundle shape:
  `docs/HEP_ATLAS_BUNDLES.md`.
* **Authoring aids.** `python -m hepgraph.atlas.tours review <slug>` prints each
  sentence with the evidence under it; `... fields <entity-id>` lists the
  referenceable fields of a record; `... show <entity-id> <field>` resolves one.
* **Tours.** Six, in `data/atlas/tours/`, 6-8 steps and 2-3 questions each (list in
  the final report; the same list is `review <slug>`).
* **Gargamelle.** `experiment:gargamelle`, `detector:gargamelle`,
  `collaboration:gargamelle`, `result:gargamelle-neutral-currents-1973`, three
  sources, one coverage row (`data/atlas/coverage/tours.json`, tier C).
* **Tests.** `tests/test_atlas_tours.py` (real tree plus mutations that must fail).

## What the validator does and does not prove

It proves: every reference resolves to a sourced field; every quote is non-empty
and found in a fetched page when written; every sentence has a covered phrase and
every number lies inside one; each covered number agrees with the figure its
evidence states (rounded or unit-converted); the arithmetic in each worked answer
evaluates to the stated value; selections exist in the step's year; counts are 5-9
steps and 2-3 questions. It does **not** prove that a quote supports its sentence.
That was my own read, sentence by sentence, against the printed evidence, and was
not done by a second agent: both attempts to start independent fact-check agents
failed on the session's concurrent-agent limit. **An independent read is still
owed** (the integrator, or a reviewer agent with `review <slug>` in hand).

Every `OWN` quote was checked verbatim against the page text fetched today by the
authoring script before the file was written (`need()`; PDFs by the repository's
own loose rule, alphanumerics identical in order), and
`scripts/atlas_quote_check.py --only tours/` was run on the result: 24 of 25 quotes verbatim, 0 number flags; the one `missing` is the ATLAS-introduction quote in `higgs-hunt` step 5, where the PDF's running header falls inside the last clause (noted on the claim).

## Entities written

| entity | status / dates | place | sources and the quote behind each date |
| --- | --- | --- | --- |
| `experiment:gargamelle` | completed. PS beam 1970-12 to 1976; SPS beam 1976 (approximate: the end of the PS period) to 1979; completed 1979 | `facility:cern` (host); no detector placement, see conflicts | start: CERN Courier 2009 "took its first pictures in December 1970"; end of PS and SPS periods: home.cern Gargamelle page "It operated from 1970 to 1976 with a muon-neutrino beam produced by the CERN Proton Synchrotron, before moving to the Super Proton Synchrotron (SPS) until 1979."; completion: same page "in 1979 the chamber ceased operation after cracks had appeared that proved impossible to repair" |
| `detector:gargamelle` | completed, mirrors the experiment | none (A23 ruled out, below) | 4.8 m long, 2 m diameter, 1000 t, nearly 12 m³ of freon (CF3Br): home.cern page, "Gargamelle was 4.8 metres long and 2 metres in diameter. It weighed 1000 tonnes and held nearly 12 cubic metres of heavy-liquid freon (CF3Br)." |
| `collaboration:gargamelle` | completed; span of data taking | host site `site:cern-meyrin` | "spread over seven institutes in six European countries" (CERN Courier 2009); no formation date found, `formation` is null |
| `result:gargamelle-neutral-currents-1973` | observation (the collaboration's own title says "Observation"); announced 1973-07-19, published 1973-09-03 | `facility:cern` | announcement: CERN Courier 2009 "On 19 July 1973, Paul Musset presented the results of both hadronic and leptonic analyses in a seminar at CERN."; publication: "On 3 September 1973 the Gargamelle collaboration published two papers in the same issue of Physics Letters"; claim: title of Phys. Lett. B 46 (1973) 138 from the Crossref record (DOI 10.1016/0370-2693(73)90499-1; the publisher page returned 403 and was not worked around, so the abstract was not read) |
| `src:tours-gargamelle-cern-page`, `-courier-2009`, `-plb46-138-crossref` | accessed 2026-10-26 | | https://home.cern/science/experiments/gargamelle ; https://cerncourier.com/a/gargamelle-the-tale-of-a-giant-discovery/ ; https://doi.org/10.1016/0370-2693(73)90499-1 (Crossref metadata, `retrieval: partial`) |
| `src:tours-nist-codata-speed-of-light`, `-nasa-earth-fact-sheet`, `-tevatron-higgs-evidence-arxiv-1207-6436`, `-atlas-higgs-observation-arxiv-1207-7214-pdf`, `-dune-fd-tdr-vol-1-pdf` | accessed 2026-10-26 | | c = 299 792 458 m/s (CODATA 2022 value page); Earth volumetric mean radius 6371.000 km (NASA fact sheet); CDF+D0 combination abstract; the ATLAS 2012 paper's introduction (full-text URL, no `reference` so it does not collide with the existing abstract-page source under A20); the DUNE TDR executive summary "Situated underground" passage (full-text URL, same reason) |

Existing sources reused by own claims: `src:rf06-davis-nobel-lecture-2002`,
`src:lngs-overview`, `src:lep-arxiv-higgs-search-2003`.

## Conflicts

| claim | source A | source B | chosen | why |
| --- | --- | --- | --- | --- |
| how many hadronic neutral-current events, and when | home.cern: "By July 1973 they had confirmed as many as 166 hadronic events, and one electron event" | CERN Courier 2009: "by March 1973 there were as many as 166 hadronic NC candidates (102 neutrino events and 64 antineutrino events)" | the Courier (March 1973, candidates, split by beam); the tour says "as many as 166 hadronic candidates" and gives no date for the electron event | the count agrees; the Courier is more specific, and "confirmed" is a stronger word than the paper's own |
| when Homestake started | Davis Nobel lecture: "The Homestake experiment became operational in 1967" (and the solar neutrino problem "was born in 1967") | `experiment:homestake` interval "continuous operation 1970 to 1994" (Wikipedia only, rank 12, approximate); Cleveland et al. 1998: "has been measuring the flux of solar neutrinos since 1970" | the tour says "from 1970", citing the 1998 paper, and never gives 1967 or 1994 | not mine to edit; listed for the integrator below |
| Gargamelle detector placement | placing it on `site:cern-meyrin` (campus point) satisfies "a located site" | the build derives a site's presence from the detectors placed there, so the main CERN campus marker would exist only 1970-1979 (and A23 warns `coordinate-kind-approximate` on it) | no placement; the experiment sits on `facility:cern`, the collaboration names the campus as host (as UA1 does) | a placement would change an existing record's behaviour; the validator is unchanged at 0 errors and 1596 warnings (the baseline) |

## Decisions worth a second look

* **Every claim is either quoted or referenced**, and references are preferred.
  A reference may not rest on a field whose best source is rank >= 11 (the
  encyclopaedia-sourced Homestake fields), which is why the Homestake step
  carries two own claims from the Davis lecture instead.
* **No superlatives.** "First" appears twice, each from a source that says it
  ("the first direct evidence of the weak neutral current", CERN; "Its first
  results", KamLAND/LZ, which the records name results). Nowhere "largest",
  "newest", "only" except ATLAS's own "the only elementary particle in the SM
  that has not yet been observed", attributed to the ATLAS paper.
* **Statuses and tenses** follow the records at 2026-10-26: PandaX-4T "was",
  KamLAND "watched", DUNE and LBNF "will", the CERN injector chain "fell silent"
  on 31 August 2026 (Long Shutdown 3), the LHC's Run 3 in the past tense.
* **Numbers in the questions** come from the cited fields (`ref`), from a
  number a quote states (`number`), or from two sourced constants (c, Earth
  radius). Where the Atlas carries a rounded figure ("1.5 km" against 1478 m) the
  text keeps the rounded form and the validator checks the rounding.

## Unresolved

* Gargamelle: INSPIRE id (not consulted, importer's rate budget); the hall of the
  PS neutrino area and the SPS West Area; the collaboration's formation date and
  institution list; the abstract of Phys. Lett. B 46 (1973) 138 (publisher page
  blocked); a PS neutrino-beam record (`beamline_ids` is empty).
* `view.arg` for `beam-section` is checked only as a warning (a beamline slug);
  the M2 stream owns the route and may name arguments differently.
* The player is another stream's; `step.href` for a view uses the planned
  `#/view/<name>/<arg>` route.

## Candidates considered and excluded

* A step on the Tevatron top-quark discovery in the Higgs tour: relevant only
  through precision electroweak fits, which no fetched source ties to the Higgs
  mass in a quotable sentence.
* A "why underground" question built on m.w.e. defined as depth times density:
  no fetched primary source defines it in one sentence; the m.w.e.-per-metre
  question states only the arithmetic.
* The LEP "could LEP have made the Higgs" threshold question: needs the
  Higgsstrahlung mechanism sourced; not fetched.
* Placing Gargamelle at a new hall site: no source gives its position.

## For the integrator

* The six tours, the A28 text, `tours.py` and the bundle doc are on this branch;
  `static/atlas/generated/` was not committed (rebuild at merge; `tours.json`
  is about 130 KB).
* `experiment:homestake` (rank-12 Wikipedia interval; Davis says 1967) and
  `result:lep-three-neutrino-species-1989`'s `claim` node (rank 12 source) are
  weak records other streams own.
* `beamline:numi` `direction` says "734 km away" where the same record's
  baselines say 735.3 km; the tours cite only the 58 mrad.
* Re-run `python -m hepgraph.atlas.validate` after merging the coverage
  streams: the tours will report `tour-claim-number-mismatch` if a field they
  reference changes a number (e.g. accelerator energies), which is the intent.
