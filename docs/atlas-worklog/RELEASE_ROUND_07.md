# Release round 7 — what the independent review found, fixed

Integration branch `atlas-release`, 2026-10-25. Three Sonnet streams fixed the
review's findings (panels/search, maps/sources, data); the integrator merged
them, re-checked the audit's value changes against their sources, and ran the
full browser suite on three engines. Running those suites surfaced two
infrastructure problems that a reader in production would have felt as well.

## What changed

**Results now say what their papers say.** Every one of the 109 results was
audited field by field (name, key value, significance, both summaries, why it
matters) against its verbatim quote and the cited abstract — 898 logged edits.
Examples, each re-read by the integrator where marked ✓:

* ATLAS ttH: "5.8σ" is the 13 TeV result; the 7+8+13 TeV combination is 6.3σ ✓.
* LZ's 2024 search uses "roughly four to five times" the first run's exposure
  (4.2 t·yr total, 3.3 new ✓), not "twenty times".
* CMS top mass: the name said "measured to 0.37 GeV" — that is the uncertainty;
  it now reads 171.77 ± 0.37 GeV.
* MEG II no longer "ties the world's best limit"; Muon g-2's improvement is the
  paper's "over a factor of four"; CMS+LHCb Bs→μμ is "about four per billion".
* "First / only / strongest / definitive / proof" claims were removed or
  attributed to whoever makes them (SNO's NC result is the collaboration's
  "strong evidence", not "proved directly").
* `significance` always carries σ and says what it is; announcement dates from
  primary pages are recorded next to preprint/publication dates (ATLAS Higgs
  announced 2012-07-04 at the CERN seminar, UA1's W on 1983-01-20).

**Fermilab's machines have sourced lifecycles.** The Main Injector was "in
operation by 2005, earliest 1968", so the 1970 map drew it; it now runs
approved 1991 → ground broken 22 March 1993 ✓ → commissioning 1998 → dedicated
1 June 1999 ✓. Recycler, Linac and Booster likewise. SURF's depth is 1478 m
(4850 ft) ✓ everywhere, with the 1500 m rounding explained. Operators are quoted
from pages that state them (SDSTA for SURF; Fermi Forward Discovery Group for
Fermilab since 2025).

**Panels and search** — selecting a topic lights its experiments on the globe;
Results filters and sort live in the URL and survive Back; "where was the Higgs
discovered" finds both discovery papers and "Higgs" reaches ATLAS, CMS and CERN;
experiment panels list their detectors and the distance and bearing between
their sites (Fermilab → SURF ≈ 1290 km, 288° WNW); a far detector says its site
is drawn on the SURF map and only a bearing toward it on Fermilab's; a result
says where ("Where: CERN (local map)"); Play restarts at the end; the share link
has a usable phone fallback.

**Maps and sources** — Sources show where in a PDF a quote is ("In the source:
§II, PDF p. 12"), a PDF link, and no internal JSON pointers; unlocated entries
read as one plain sentence with the research notes folded away; position
circles are labelled "position uncertainty ±2000 m — not the detector outline";
ATLAS, ALICE, LHCb and CMS are labelled on the CERN map; a long shutdown reads
"Temporarily shut down (long shutdown / upgrade)", not "Shut down"; the faint
tile seams Leaflet left on every map are gone; the Results filters and the
About page fit a phone.

**Two infrastructure fixes found by running the suites**

1. *Every Atlas file was a serverless call.* Production served each file of each
   page load through the Python function (`x-vercel-cache: MISS`, ~40 calls a
   load), each counted against a per-address budget — the local test suite hit
   that budget and flaked; a lecture hall behind one address could too. Vercel's
   CDN now holds `/atlas` files through a CDN-only header
   (`Vercel-CDN-Cache-Control`), so browsers still revalidate and no deployment
   ever serves the previous build.
2. *A browser-visible `stale-while-revalidate`* (the first attempt at 1) made
   Firefox stall page loads; proven by running Firefox against the old header
   (92/92) and the new (hangs), and fixed by keeping it CDN-only.

## How the experience improved, and why it is better

* A theorist reading a headline number now gets the paper's number, with the
  paper's scope ("13 TeV" vs "combined") and the paper's verb.
* The time slider tells the truth about Fermilab: no Main Injector before 1991.
* The reader questions that failed in review — "where was the Higgs discovered",
  "what are DUNE's detectors", "where is the far detector" — now have direct
  answers one click away.
* Pages load from the CDN instead of waking a server for every file.

## Verified, and how

* Browser suite: Chrome 93/93, Firefox 92/92, WebKit 92/92 on the merged build;
  accessibility suite 35/35, 0 axe violations.
* Integrator re-read: arXiv 1806.00425 and 2410.17036 abstracts, SURF's "4850
  Level (1478 m)", the Fermilab history page's Main Injector dates (cached copy;
  the live page is now behind a bot check).
* Validator 0 errors; Atlas tests 353 passed; quote checker: results,
  facilities and accelerators at 0 missing / 0 near.

## Not done yet

* "Report an error" still points at the private GitHub repository (owner's
  decision).
* A second independent review of this release candidate is running.
