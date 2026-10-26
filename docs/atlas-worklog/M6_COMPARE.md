# M6 research tools: Compare, Cite and Export (branch `atlas-m6-compare`)

Scope: `docs/HEP_ATLAS_TEACHING_PLAN.md` workstream 4 (the first two bullets). Feature
names are working titles ("Compare experiments"; the Cite and Download controls).
No entity data was written: nothing under `data/atlas/` changed.

## What was built

| Piece | Where | Notes |
| --- | --- | --- |
| Compare view | `#/view/compare/<slug>,<slug>[,…]`, `js/views/compare.js`, `compare-rows.js`, `compare-units.js`, `compare-route.js` | Registered in `registry.js` with a search entry; the table's code loads only when the route opens (`compare-route.js` is the few lines the globe's start-up needs). |
| Tray and "Add to compare" | `js/research/compare-tray.js` | Up to four; list in sessionStorage (try/catch), the Compare URL holds the list once open. Mounted by `app.js` (3 lines); the control is added to the experiment panel (`panels.js`). |
| Cite | `js/research/bibtex.js` (pure), `cite-panel.js` | A "Cite" section on result and document panels. |
| List export | `js/research/list-export.js`, `files.js` | "Download CSV" / "Download JSON" on the Results and Documents lists (`modes.js`). |
| Styles | `static/atlas/research.css` | Linked between `views.css` and `phone.css`; tokens only. |

## Decisions the owner may want to change

* **Where a value comes from.** Each row is read from the record's `key_specs` by label
  (baseline, depth, mass, energy), the sites' `depth` / `depth_mwe`, the detectors'
  `technology_class`, the collaboration's `membership`, the results bundle and the dated
  `intervals`. The spec's own label stays beside every value ("Detector mass" is never
  read as a target mass). The rules are listed in the view's "Inputs and method".
* **Source markers** link straight to the source URL (numbered footnotes under the
  table). A value is cited by its own provenance claim, else by the record's `/sources`.
  A value with no provenance shows "no source recorded"; a statement of absence ("Not yet
  proposed in 2010") carries none.
* **Status follows the timeline** (the same rule as the experiment panel's badge); its
  markers are those of the intervals in that state. The CSV row label carries the year.
* **Units.** Lengths, masses and energies are converted only by powers of ten, only when
  the recorded wording is one figure and one unit; otherwise the wording is kept as
  recorded and fixes the row's unit. Depths are read in metres. m.w.e. is never
  converted. The original is the tooltip (and "(recorded: …)" in the CSV).
* **CSV** starts with a BOM and `#` metadata lines (data version, access date, link,
  filter): read it with `comment='#'` and `utf-8-sig`. Cells that would read as formulas
  in a spreadsheet are prefixed with an apostrophe. An export is refused, not written,
  if the sources could not be loaded.
* **BibTeX** is `@misc` unless the record names a journal (none does today). Author is
  the result's collaboration; a document's owner is not made its author. Year is the
  record's `published` year, else the year of its `date` (an announcement-only result
  says "Announced <date>" in `note`). TeX math in a title is kept, other special
  characters are escaped, common physics symbols become TeX (so pdfLaTeX builds work).
  No DOI and no arXiv id: no entry, and the panel says so (2 of 109 results, 18 of 70
  documents today).

## Data findings (for the data streams)

* Six key specifications hold no usable quantity: five on ALICE (detector mass, length,
  solenoid field, Pb-Pb collision energy, cavern depth) are bare numbers with no unit, and
  SND@LHC's pseudo-rapidity coverage is null. Compare leaves them out rather than guess a
  unit.
* `site:ash-river-nova-far-detector` records `depth_mwe` as 3.6 m.w.e. (a surface hall);
  beside underground labs at thousands of m.w.e. it reads oddly, so the figure is worth a
  second look at the source.
* No result carries a journal, volume or page, and no document carries authors, so no
  entry can: adding `publication.journal` to the build would make Cite emit `@article`.
* `result:dune-far-site-excavation-2024` and `result:superkekb-luminosity-world-record-2026`
  have neither DOI nor arXiv id (news-grade results).

## Unresolved

* The tray is not in the URL outside the Compare route (by design; sessionStorage only).
* A mixed row such as 300 g beside 3.7 t reads in grams; the rule (no value under 1)
  prefers that to fractions. Rare in the current data.
