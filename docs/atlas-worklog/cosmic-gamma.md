# cosmic-gamma worklog (wave 3 / v1.0 coverage expansion)

## Scope

Eight non-flagship cosmic-ray and gamma-ray observatories per
`data/atlas/coverage/cosmic-gamma.json`: Pierre Auger Observatory, Telescope
Array, HAWC, LHAASO, CTAO, MAGIC, VERITAS, H.E.S.S. Mandatory bar only
(facility, site, experiment, detector, collaboration, sources); no results or
technical documents (none of these are wave-3 flagships).

## Delegation note

The brief called for delegating four pairs of children (Auger+TA; HAWC+LHAASO;
CTAO+MAGIC; VERITAS+HESS). Every `Agent` call for this task failed with
"Concurrent subagent limit reached" (the session-wide cap of 20 concurrent
subagents shared across all 16 wave-3 leads), including retries and a
reduced-to-2-at-a-time attempt after the orchestrator's correction. Per the
orchestrator's follow-up instruction, all eight experiments were researched
and written directly by this lead agent (no children spawned), using WebSearch
and WebFetch itself. Every source cited below was fetched by this same agent
in this session; there is no separate "re-check the child's work" step because
there was no child.

A session interruption (usage-limit reset) occurred mid-way through Telescope
Array; work resumed from disk and Telescope Array's files were verified
complete before continuing to the remaining six experiments.

## Entities written

- **Pierre Auger Observatory**: `facility:pierre-auger-observatory`,
  `site:malargue-auger`, `experiment:pierre-auger-observatory`,
  `detector:pierre-auger-observatory`,
  `collaboration:pierre-auger-observatory`.
- **Telescope Array**: `facility:telescope-array-utah`,
  `site:telescope-array-utah-central-site`, `experiment:telescope-array`,
  `detector:telescope-array`, `collaboration:telescope-array`.
- **HAWC**: `facility:sierra-negra`, `site:hawc-sierra-negra`,
  `experiment:hawc`, `detector:hawc`, `collaboration:hawc`.
- **LHAASO**: `facility:lhaaso-daocheng`, `site:lhaaso-haizi-mountain`,
  `experiment:lhaaso`, `detector:lhaaso`, `collaboration:lhaaso`.
- **CTAO**: `facility:roque-de-los-muchachos-observatory` (shared with
  MAGIC), `site:roque-de-los-muchachos-gamma-ray-array` (shared with MAGIC),
  `facility:ctao-south-paranal`, `site:paranal-cta-south`,
  `experiment:ctao`, `detector:ctao` (two placements), `collaboration:ctao`.
- **MAGIC**: `experiment:magic`, `detector:magic`, `collaboration:magic`
  (references the shared Roque facility/site above; did not recreate them).
- **VERITAS**: `facility:fred-lawrence-whipple-observatory`,
  `site:mount-hopkins-veritas`, `experiment:veritas`, `detector:veritas`,
  `collaboration:veritas`.
- **H.E.S.S.**: `facility:hess-khomas-highland`,
  `site:khomas-highland-hess`, `experiment:h-e-s-s`, `detector:h-e-s-s`,
  `collaboration:h-e-s-s`.

40 entity files total (8 experiments x 5 record types, with CTAO/MAGIC
sharing one facility+site pair instead of each creating their own).

## Sources added (34 `src:cosmic-gamma-*` records)

Auger (7): official observatory page, official history-timeline page,
official AugerPrime page, official collaboration page, AugerPrime status
arXiv paper (2508.08056), Nominatim geocode of the Malargue address, INSPIRE
experiment record (recid 1110614).

Telescope Array (3): a 2026 collaboration arXiv paper (2605.19553, the only
readable source found this session), Nominatim geocode of Delta UT, INSPIRE
experiment record (recid 1307044).

HAWC (5): 2013 design paper (1310.0074, altitude), 2017 Crab Nebula paper
(1701.01778, "completed in early 2015"), 2025 "first 10 years" paper
(2512.03938, "began operations in March 2015"), Nominatim geocode of the
Sierra Negra peak, INSPIRE experiment record (recid 1108207).

LHAASO (5): 2019 Science Book (1905.02773, altitude/location), 2021
UHE-photons paper (2105.07967, "currently operating"), Nominatim geocode near
Haizi Mountain, INSPIRE experiment record (recid 1339331), IHEP LHAASO
homepage.

CTAO (7): homepage, about-us page, technology page, Nominatim geocodes of
Roque de los Muchachos and of Paranal, INSPIRE experiment record for CTA
(recid 1339486).

MAGIC (4): 2004 status paper (astro-ph/0407475, MAGIC-I October 2003),
2009 MAGIC-II status paper (0912.3673, stereoscopic inauguration), 2014
upgrade paper (1409.5594, La Palma location, 2011-2012 upgrade), INSPIRE
experiment record (recid 1110626).

VERITAS (5): official homepage, official specifications page (exact
coordinates/altitude/energy range), official history-timeline page, official
about-VERITAS page, INSPIRE experiment record (recid 1110615).

H.E.S.S. (4): official homepage, official site page (coordinates/altitude),
official about page (first light, telescope configuration, collaboration
size), INSPIRE experiment record (recid 1110512).

## Conflicts

None found between sources within this workstream's own fetches. One
internal ambiguity resolved: NOvA-style "which status wins" question for
Pierre Auger — the AugerPrime upgrade interval (start 2015-11) and the
long-running data-taking interval (start 2004) both cover the present with
different labels; per A3's "latest `lo(start)` wins" rule the derived state is
`upgrade`, not `active`, even though existing-array data taking is
uninterrupted. Chosen: `status: "upgrade"` on both `experiment:` and
`detector:`, explained in each record's `notes`. This matches the brief's own
expectation ("Statuses from the observatories' own pages, e.g. AugerPrime
upgrade").

## Unresolved / missing fields (honest gaps, see also the coverage rows)

- **Telescope Array, MAGIC**: official sites (telescopearray.org,
  magic.mpp.mpg.de) never loaded this session — DNS failure, connection
  refused, and TLS certificate-verification failures respectively, on every
  attempt and every known mirror tried. All facts for these two experiments
  come from collaboration arXiv papers instead.
- **HAWC official site** (hawc-observatory.org, and the hawc.umd.edu redirect
  target): TLS certificate verification failed on every attempt.
- **CTAO's dedicated subpages** (`/sites/`, `/arrays/`, `/news/`, LST-1
  inauguration press release): returned HTTP 404 or an empty JavaScript
  shell (no server-rendered content) on every attempt; only the homepage,
  about-us and technology pages yielded readable text.
- **LHAASO's IHEP subpages** (`/oy/site/`, `/oy/sg/`): same empty-shell
  problem; KM2A/WCDA/WFCTA sub-array specifications are NOT recorded as a
  result (public knowledge of these names was deliberately NOT written into
  the data files per A17 — see the detector's own notes).
- **HAWC's design-paper PDF** (arXiv:1310.0074): WebFetch could not extract
  readable text from the PDF (binary/compressed content), so the tank count
  (300, commonly cited elsewhere) is not recorded.
- No source fetched this session states an explicit collaboration-formation
  date for Telescope Array, HAWC, LHAASO, CTAO (as an ERIC) or MAGIC; all
  five are left `null` with a `locator` explaining what was checked, per the
  NOvA exemplar's pattern.
- H.E.S.S.'s CT5 (28 m telescope, "H.E.S.S. II") commissioning date is
  commonly reported elsewhere as 2012, but no source fetched this session
  states it; left `null` rather than guessed.
- No array-centre survey-grade coordinates were found for Auger, Telescope
  Array, LHAASO, or either CTAO site; all use a geocoded anchor point
  (`kind: campus`, `confidence: approximate`) per the new A23 amendment
  rather than `kind: detector`, with an explicit note on each site record.
  VERITAS and H.E.S.S. DO have official-site-stated coordinates precise
  enough for `kind: detector`.
- No institution/member/country counts were sourced for Telescope Array,
  HAWC, LHAASO, CTAO, MAGIC or VERITAS (no page fetched states them). Auger
  (~400 scientists, 17 countries named) and H.E.S.S. (~200 scientists, "more
  than a dozen countries") have partial, sourced aggregate counts.

## Dangling references to ids owned by other leads

None. This workstream's ids (Roque de los Muchachos, Paranal, and all eight
experiment/detector/collaboration ids) are entirely self-contained per the
Wave 3 ID_REGISTRY row; no reference was made to any `facilities`-owned id.

## Validator / build status

`python -m hepgraph.atlas.validate`: 0 errors attributable to any
`cosmic-gamma`-owned file (confirmed by grepping the full validator output for
every entity/site/facility/source id created in this pass — zero matches
outside the `coverage-not-yet-researched` and `derived-field` informational
categories, both of which are pre-existing, codebase-wide conventions, not
defects). Remaining errors in the full report (`dangling-reference` for
`facility:chooz`, `status-not-derived-state` for `slac-linac`/`sns`/`mit`/
`university-of-washington-cenpa`/`yale-wright-lab`) all belong to other
workstreams. Fixed during this pass (own files only): duplicate alias,
missing `confidence`-required notes, `quote`-on-`summary`-retrieval sources
(A18), and three `status`/derived-state mismatches caused by intervals with
both `start` and `end` null (CTAO facility/experiment/detector — fixed by
anchoring each to a real, sourced, appropriately-caveated lower-bound date).

`python -m hepgraph.atlas.build`: succeeds; wrote 31 bundle files. The
400 KB `atlas.json`+`manifest.json` pilot-budget warning is pre-existing
(documented in the ontology as a warning, not a build failure, once past the
three-experiment pilot).

All 79 JSON files this workstream touched were reformatted to the canonical
`json.dumps(sort_keys=True, indent=2, ensure_ascii=False)` + trailing newline
shape per A11.

## Confidence summary

- **High confidence, well-sourced**: VERITAS (fully sourced from its own
  official site down to exact coordinates and a proposal-to-2012 interval
  history) and H.E.S.S. (official site: coordinates, altitude, first light,
  telescope configuration, collaboration size).
- **Medium confidence**: Pierre Auger (rich official-site history, but
  campus-only coordinates and no institution count) and MAGIC (solid dates
  from three collaboration papers, but no altitude and a shared, approximate
  site point).
- **Lower confidence / thinnest sourcing**: Telescope Array, HAWC, LHAASO and
  CTAO, where the primary official web presence could not be fetched at all
  (TA, HAWC, MAGIC: technical failures) or only partially rendered (LHAASO,
  CTAO: JavaScript-shell subpages), so status/interval history relies on a
  smaller number of arXiv papers and, for coordinates, on geocoded anchor
  points rather than official technical sources. Every value in every record
  is still either sourced with a quote/locator or explicitly `null` with a
  note; nothing was filled from memory.
