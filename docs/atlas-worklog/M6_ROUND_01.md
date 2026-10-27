# M6 — Research tools: compare, cite and export, and HEP Graph × Atlas

Integration branch `atlas-next`, 2026-10-26. Two implementation streams and
integrator checks.

## What changed

- **Compare** (`#/view/compare/<slug>,<slug>[,…]`): two to four experiments side
  by side.
  - Ten rows: status, dates, host and site, depth, baseline, mass, energy,
    technology, key results, collaboration size.
  - Every value carries a numbered link to its source, and a value the Atlas lacks
    reads "not recorded", never blank.
  - Readers fill it from an "Add to compare" tray on experiment panels.
  - The table downloads as CSV with a citations column and a header naming the
    data version and the access date.
- **Cite**: result and document panels offer a BibTeX entry built only from fields
  the record carries (DOI, arXiv id, title, collaboration, year), with copy and
  `.bib` download. A record with neither a DOI nor an arXiv id offers no entry and
  says why.
- **Export lists**: the Results and Documents lists, as filtered, download as CSV
  or JSON with their sources and a header describing the filter.
- **HEP Graph × Atlas**.
  - The only key the two share is the INSPIRE author id, and the Atlas names
    12 researchers.
  - `#/view/person/<inspire-id>` places a researcher's recorded institutions and
    experiments on a world map. It states that rosters are partial: an author the
    Atlas does not name is "unknown, not none". A database or API failure shows as
    an error, never as an empty record.
  - Experiment and collaboration panels link to HEP Graph's people.
  - HEP Graph's person profile links to the Atlas page, a 10-line change kept small
    because another session is working on that app.

## How the experience improved, and why it is better

A researcher deciding between three xenon experiments can now read their sourced
numbers side by side and take the table away with its citations. Anyone writing
a paper or slides can get a correct BibTeX entry without leaving the Atlas. The
Atlas and HEP Graph are now joined in both directions, honestly: only as far as
their shared identifiers go, and saying where they don't.

## Verified, and how

- The integrator opened LZ / XENONnT / PandaX-4T in Compare (0 console errors), and
  a person page (Atsuko K. Ichikawa → Tohoku). The person page reported the local
  API's database error as an error.
- The streams' checks:
  - BibTeX escaping and CSV quoting;
  - a person route with no database showing the error state;
  - accessibility with 0 violations, including the tray.
- During integration, a test that pinned the old count of 109 results was made
  count-independent, since the coverage wave doubled the results.
