# dark-matter research log (LZ / LUX)

Agent: `dark-matter`. Worked in the `hep-atlas-globe` worktree on 2026-09-16.
All `verified_at` values are 2026-09-16, the day every cited source was fetched
with WebFetch.

## Scope

One deeply researched direct-detection programme:

* `experiment:lz` — LUX-ZEPLIN, its detector, collaboration and site.
* `site:surf-davis-campus-lz` — the Davis Campus on the 4850 Level of SURF.
* `experiment:lux` — lineage only (LZ holds the `predecessor` pointer).
* LZ and LUX results and the four design/detector documents.

`facility:surf` and the other SURF sites are **referenced, not created**; they
belong to the `fermilab-dune` workstream, which had already written
`data/atlas/facilities/surf.json` and
`data/atlas/sites/surf-4850-level-dune-far-detector.json` by the time this work
finished, so all references resolve.

## Entities written

| id | file |
| --- | --- |
| `site:surf-davis-campus-lz` | `data/atlas/sites/surf-davis-campus-lz.json` |
| `experiment:lz` | `data/atlas/experiments/lz.json` |
| `experiment:lux` | `data/atlas/experiments/lux.json` |
| `detector:lz` | `data/atlas/detectors/lz.json` |
| `collaboration:lz` | `data/atlas/collaborations/lz.json` |
| `result:lz-first-wimp-search-2022` | `data/atlas/results/lz-first-wimp-search-2022.json` |
| `result:lz-ws2024-wimp-search-2024` | `data/atlas/results/lz-ws2024-wimp-search-2024.json` |
| `result:lux-first-wimp-search-2013` | `data/atlas/results/lux-first-wimp-search-2013.json` |
| `result:lux-complete-exposure-2016` | `data/atlas/results/lux-complete-exposure-2016.json` |
| `document:lz-tdr` | `data/atlas/documents/lz-tdr.json` |
| `document:lz-cdr` | `data/atlas/documents/lz-cdr.json` |
| `document:lz-detector-paper` | `data/atlas/documents/lz-detector-paper.json` |
| `document:lux-detector-paper` | `data/atlas/documents/lux-detector-paper.json` |

Coverage registry: `data/atlas/coverage/dark-matter.json` (rows for
`experiment:lz` and `experiment:lux`).

Not written, deliberately:

* `experiment:zeplin-iii`, `facility:boulby-underground-laboratory`,
  `site:boulby-zeplin` — the ID registry allows them, but no source giving
  Boulby coordinates *and* depth was fetched, so nothing was created.
  ZEPLIN-III is recorded as a note on `experiment:lz` instead.
* `collaboration:lux`, `detector:lux` — not in the ID registry for this
  workstream; LUX is held only as LZ lineage. `experiment:lux` therefore has an
  empty `collaboration_ids` with the explanatory note the ontology (§9) requires.
* `data/atlas/memberships/lz.json` — LZ does not publish an institution list on
  `lz.lbl.gov` (only aggregate counts), and `institution:` ids belong to
  `membership-lead`.
* No `person:` records; `collaboration:lz.leadership` is empty. The spokesperson
  (Rick Gaitskell) and operations manager (Simon Fiorucci) are named on
  lz.lbl.gov and recorded as a note, not as person rows, because those need
  INSPIRE author recids and belong to `membership-lead`.

## Sources added (23 fetched, 22 kept)

Official experiment site (rank 1): `src:lz-official-site`,
`src:lz-official-site-detector`, `src:lz-official-site-laboratory`,
`src:lz-official-site-publications`, `src:lz-official-site-press`.

Official facility site (rank 2, sanfordlab.org): `src:lz-surf-davis-campus`,
`src:lz-surf-cd4-news`, `src:lz-surf-startup-press-release`,
`src:lz-surf-assembly-news`.

INSPIRE experiment records (rank 3): `src:lz-inspire-experiment` (recid
1262631), `src:lux-inspire-experiment` (recid 1108192). One INSPIRE request per
10 s was respected; two requests were made in total.

Design reports (rank 4): `src:lz-tdr-arxiv` (1703.09144),
`src:lz-cdr-arxiv` (1509.02910).

Detector papers (rank 5): `src:lz-detector-paper-nima` (1910.09124 = NIM A 953
(2020) 163047, full text read through ar5iv), `src:lux-detector-paper-nima`
(1211.3788 = NIM A 704 (2013) 111).

arXiv / journal (rank 10): `src:lz-prl-first-results-2023` (2207.03764),
`src:lz-prl-ws2024-2025` (2410.17036), `src:lz-muon-flux-2026` (2602.16799),
`src:lz-surf-heise-2015` (1503.01112), `src:lz-surf-heise-2017` (1710.11584),
`src:lux-prl-first-results-2014` (1310.8214),
`src:lux-prl-complete-exposure-2017` (1608.07648).

A 23rd source, `src:lz-surf-heise-2024` (arXiv:2403.13671), was created and then
**deleted**: the `fermilab-dune` workstream already holds the same URL as
`src:surf-heise-opportunities-2024`, and A20 fails on two `src:` records sharing
a normalised URL. Nothing cites it.

Sources fetched but not citable: `https://sanfordlab.org/about-the-facility`
(HTTP 403) and `https://sanfordlab.org/experiment/davis-campus` (HTTP 500). No
`src:` record was created for either.

## Conflicts

| claim | source A | source B | chosen | why |
| --- | --- | --- | --- | --- |
| LZ fiducial mass | PRL 131, 041002 / arXiv:2207.03764 abstract: "using a fiducial mass of 5.5 t" | NIM A 953 (2020) 163047 §1: "7 active tonnes (5.6 tonnes fiducial)" | **5.5 t** | The 5.5 t figure is the fiducial mass actually used in the SR1 analysis; 5.6 t is the design value in the detector paper. Both are recorded in the `note`. |
| DOE CD-4 date | Sanford Lab news 2020-10-26: "U.S. Department of Energy officials on Sept. 21 formally signed off on project completion" | lz.lbl.gov home page: CD-4 completion approval "August 2020" | **2020-09-21** | The dated news item from the host laboratory gives a specific day and quotes the signing; the lz.lbl.gov summary gives only a month. Flagged for review. |
| Depth of the 4850 Level below the surface | LZ muon-flux paper arXiv:2602.16799: "vertical depth of about 1480 m" | Heise arXiv:2203.08293 "1500 m" (used by `site:surf-4850-level-dune-far-detector`); Heise arXiv:2403.13671 gives both "1490 m" and "1485 m" in one document | **1480 m (approx)** | The LZ collaboration's own measurement paper is the most specific about the Davis Cavern in particular. The spread (1480–1500 m) is inside the `approx` flag and is named in the `note`. |
| Water shield dimensions | lz.lbl.gov Laboratory: "8 meter diameter by 6 meter high water shield containing 70,000 gallons" | Heise arXiv:2403.13671: Davis Campus "stainless steel tank ... (7.6 m diameter, 6.4 m high)"; sanfordlab.org Davis Campus feature: "72,000-gallon (272,549 liters) water tank" | **8 m × 6 m (approx)** | Rank-1 official experiment site, describing LZ's own shield. Recorded `approx: true` with the competing figures in the `note`. |
| LUX operating dates | LUX papers: cooled and filled February 2013; WS2013 April–August 2013; WS2014-16 11 Sep 2014 – 2 May 2016 | INSPIRE experiment record 1108192: `date_started` 2014-10, `date_completed` 2016-05 | **the papers** | The collaboration's own publications are rank 10 but specific and self-consistent; the INSPIRE dates appear to describe only the second run. Noted on `experiment:lux`. |
| LZ outer detector scintillator mass | NIM A 953 §4.1: "Twenty-two tonnes of GdLS contained in 150 55-gallon drums" | — | **not recorded** | The 22 t figure describes the quantity procured and shipped in drums, not the mass in the outer detector acrylic tanks. No GdLS mass quantity is written rather than record a figure that may be the wrong one. |

## Unresolved fields

* `detector:lz` `specs.threshold` — **null**. No fetched official page or paper
  states a single nuclear-recoil analysis threshold. The SR1 paper's lowest
  quoted point is 50 % detection efficiency near 5.5 keV_nr, which is an
  efficiency point, not a threshold. Noted on the detector.
* `collaboration:lz.formation` — **null**. No founding date is published on
  lz.lbl.gov; the INSPIRE record's `date_proposed` 2014 / `date_approved` 2015 /
  `date_started` 2015 are project dates. The collaboration interval uses 2015
  with `confidence: uncertain` and the explanation in its `note`.
* LZ DOE Critical Decision milestones CD-0 / CD-1 / CD-2 / CD-3 — **not
  recorded**. Widely reported dates (CD-0 Sep 2012, CD-1 Apr 2015, CD-2 Aug
  2016, CD-3 Feb 2017) appear only in secondary sources; the DOE HEPAP slide
  deck that carries the milestone table is a 7.2 MB PDF that could not be read
  (binary). The `approved` interval therefore runs 2015 → 2018-12 with
  `confidence: approximate`.
* LZ commissioning bounds — `2020-10` → `2021-12` with `confidence:
  approximate`. Sourced only by "We are completing commissioning of the detector
  … will be looking at LZ data next year" (Sanford Lab, 26 Oct 2020) and the SR1
  start date.
* **LZ ¹³⁶Xe 0νββ half-life limit — does not exist.** The LZ publications page
  read on 2026-09-16 lists exactly one ¹³⁶Xe neutrinoless-double-beta entry, the
  2019 *projected* sensitivity paper (Phys. Rev. C 102, 014602, arXiv:1912.04248,
  median 90 % CL exclusion sensitivity 1.06 × 10²⁶ yr after 1000 live days).
  A projection is not a result and no `result:` record was created. The task
  brief assumed a measured limit; this is the honest finding.
* LZ 2026 result — on 2026-09-01 the collaboration posted an effective-field-
  theory nuclear-recoil search at higher energies reporting one candidate event
  and "tension with the background-only hypothesis at a global significance of
  2.6σ" (lz.lbl.gov, read 2026-09-16). No `result:` record: the paper was still
  being submitted to PRL and no arXiv identifier was available. Worth adding
  once it is posted.
* `experiment:lux` — no sourced interval covers August 2013 → September 2014
  (between the two WIMP search runs), and nothing covers LUX construction or
  installation before February 2013.
* ZEPLIN-III / Boulby — not created; see Scope.

## Coordinates and A17

`site:surf-davis-campus-lz` carries 44.3533 N, 103.751186 W
(`kind: underground_lab`, `precision_m: 50`), converted from
44° 21′ 11.88″ N / 103° 45′ 04.27″ W in Table 5, "Coordinates estimates for
various locations of interest", row "LUX Detector", of Heise, *The Sanford
Underground Research Facility at Homestake* (arXiv:1503.01112, J. Phys. Conf.
Ser. 606 012015). LZ occupies the same Davis Cavern that LUX used.

That source is `journal_article`, rank 10. A17 says coordinates of
`underground_lab` kind "may not rely **solely** on geocoder or rank ≥ 8
sources", so the official SURF Davis Campus page (`src:lz-surf-davis-campus`,
rank 2) is co-cited for the location itself. **A reviewer should decide whether
that satisfies A17 or whether the value must be downgraded**; it is the only
published coordinate found for the cavern after searching lz.lbl.gov,
sanfordlab.org, the LZ muon-flux and Davis-Cavern-background papers, and DUNE/
LBNF material. No geocoder value was used. (For comparison, the `fermilab-dune`
workstream's `site:surf-4850-level-dune-far-detector` falls back to an
OpenStreetMap surface position with `precision_m: 2000` and a "REVIEW REQUIRED"
note; the two sites are ~700 m apart, above the A20 100 m warning threshold.)

## Children spawned and what I re-checked

**None.** The invoking instructions overrode rule 10 and forbade spawning child
agents, so every value here was fetched and read by this agent directly. Each
quote in the data files is text returned by the WebFetch that is cited in that
value's `sources`. Where a fetch returned a paraphrase rather than verbatim text
(the arXiv abstract page for 2410.17036, the LZ CDR, the LZ TDR front matter)
the source carries `retrieval: "partial"` and only the strings the fetch
returned inside quotation marks are used; for the WS2024 result the
`claim.quote` is taken from the paper title, which came back verbatim.
Two specification values were re-fetched with a strict "copy character for
character, do not paraphrase" prompt before being written: the Davis Campus
coordinates (arXiv:1503.01112) and the LZ mass/PMT/veto numbers
(arXiv:1910.09124 via ar5iv).

## Confidence summary

* `verified` — LZ and LUX result claims, limits and dates; LZ active/fiducial/
  total xenon masses; TPC and outer-detector PMT counts; SR1 run dates; LUX run
  dates; CD-4 completion; site depth_mwe; site coordinates (with the A17 caveat
  above).
* `approximate` — site `depth_rock` (~1480 m), LZ water-tank dimensions, LZ
  commissioning and DOE-approval interval bounds, LZ member count ("about 250").
* `derived` — LZ collaboration country count (counted from the six countries
  the collaboration names).
* `uncertain` — the LZ collaboration lifetime interval (project dates standing
  in for a founding date); the LUX website URL taken from INSPIRE and not
  re-checked for liveness.
* `null` with a note — `detector:lz` energy threshold, `collaboration:lz`
  formation, LZ 0νββ result, GdLS mass, LUX collaboration/detector records.

## Validation

`hepgraph/atlas/validate.py` did not exist when this work finished (the package
contains `__init__.py`, `linkcheck.py`, `load.py`, `schema.py`), so the fallback
from rule 11 was run:

```
.venv/bin/python -c "import json,glob;[json.load(open(f)) for f in glob.glob('data/atlas/**/*.json',recursive=True)]"
```

which passes for the whole tree. In addition this agent checked its own files
for dangling references (none), duplicate source URLs across the whole
`data/atlas/sources/` directory (the one duplicate was removed, see above),
`quote` length ≤ 300 characters, and `summary.plain` ≤ 60 words. Files were
written with `json.dumps(sort_keys=True, indent=2, ensure_ascii=False)` plus a
trailing newline and carry `"schema": "hep-atlas/0.2"` (A11).
