# Geometry worklog: North American underground laboratories

Researcher: geometry-us-ug. Worktree
`/Users/yatharthsirohi/Desktop/HEP-Graph-maps-us-ug`, branch
`hep-atlas-local-maps-us-ug`. Four maps: SURF (`map:surf`), SNOLAB
(`map:snolab`), Soudan Underground Laboratory
(`map:soudan-underground-laboratory`) and WIPP (`map:wipp`). Sources prefixed
`src:geo-<facility>-*`.

## Method note: Overpass access this session

`overpass-api.de` served SURF and SNOLAB bboxes without incident. The Soudan
query also succeeded on the first try. WIPP's first query hit `HTTP 504`
(60 s backoff), the retry hit `HTTP 429`, and `lz4.overpass-api.de` refused
the TCP connection outright — consistent with other concurrent researchers'
reports of Overpass being under heavy load. WIPP's extract was completed
against the `overpass.kumi.systems` mirror instead, which returned a valid
response but with a `timestamp_osm_base` about 3.5 months older than the
session date (`2026-06-01T08:52:28Z`); this is recorded verbatim in
`src:geo-wipp-osm-extract` rather than overwritten with today's date. One
query in flight at a time throughout, ≥10 s apart, small bboxes, `out geom;`.

## Inventory

| Entity | Drawn? | Feature(s) | Representation | Accuracy | Check |
| --- | --- | --- | --- | --- | --- |
| facility:surf | map:surf authored | — | — | — | — |
| site:surf-surface-campus | drawn | geometry:surf-administration-building | georeferenced (OSM building) | 10 m | none |
| site:surf-davis-campus-lz | drawn | geometry:surf-davis-campus-cavern | **surveyed** (SURF proceedings Table 5) | 50 m | none (Point) |
| site:surf-4850-level-dune-far-detector | **unlocated** | — | — | — | — |
| detector:homestake (placed at surf-surface-campus) | accounted via site | — | — | — | — |
| detector:lz, detector:majorana-demonstrator (placed at surf-davis-campus-lz) | accounted via site | — | — | — | — |
| detector:dune-far-detector-1/2 (placed at surf-4850-level-dune-far-detector) | accounted via unlocated site | — | — | — | — |
| (context) Yates Headframe | drawn | geometry:surf-yates-headframe | georeferenced (OSM building) | 10 m | — |
| (context) Yates Hoist | drawn | geometry:surf-yates-hoist | georeferenced (OSM building) | 10 m | — |
| (context) Ross Headframe | drawn | geometry:surf-ross-headframe | georeferenced (OSM building) | 10 m | — |
| (context) Ross Hoist | drawn | geometry:surf-ross-hoist | georeferenced (OSM building) | 10 m | — |
| facility:snolab | map:snolab authored | — | — | — | — |
| site:snolab-underground-lab | drawn | geometry:snolab-cavity | **derived** (22 m circle around the SNO paper's own point) | 30 m | span 22 m — **pass** (measured 21.98 m) |
| detector:sno, detector:sno-plus, detector:deap-3600, detector:damic, detector:supercdms, detector:nexo, detector:news-g (all placed at snolab-underground-lab) | accounted via site | — | — | — | — |
| (context) SNOLAB surface office | drawn | geometry:snolab-surface-office | georeferenced (OSM node) | 15 m | — |
| (context) Vale Creighton Mine surface site | drawn | geometry:snolab-creighton-mine-boundary | georeferenced (OSM landuse) | 20 m | — |
| facility:soudan-underground-laboratory | map:soudan-underground-laboratory authored | — | — | — | — |
| site:soudan-minos-far-detector | drawn | geometry:soudan-minos-far-detector-point | **surveyed** (MINOS PRD 2007) | 100 m | none (Point) |
| detector:minos-far-detector, detector:cdms-ii, detector:supercdms-soudan (all placed at soudan-minos-far-detector) | accounted via site | — | — | — | — |
| (context) Soudan Mine shaft house | drawn | geometry:soudan-mine-shaft-building | georeferenced (OSM building, NRHP-listed) | 10 m | — |
| facility:wipp | map:wipp authored | — | — | — | — |
| site:wipp-surface-campus | drawn | geometry:wipp-boundary | georeferenced (OSM landuse) | 20 m | none (see conflicts §3) |
| detector:exo-200 (placed at wipp-surface-campus) | accounted via site | — | — | — | — |
| (context) WIPP mine shaft building | drawn | geometry:wipp-mineshaft-building | georeferenced (OSM building) | 10 m | — |
| (context) WIPP mine shaft point | drawn | geometry:wipp-mineshaft-point | georeferenced (OSM node) | 15 m | — |

No accelerators or beamlines are recorded at any of the four facilities
(`facility_id` grep against `data/atlas/accelerators/` and `.../beamlines/`
returns nothing), so the `map-entity-unaccounted` accounting is entirely
about sites — every detector-hosting site of all four facilities is either
drawn (`entity_id` on a geometry record equals the site id — the rule the
validator actually checks, per `hepgraph/atlas/validate.py::_drawn_entities`)
or listed in `map.unlocated[]`. Confirmed by `hepgraph.atlas.validate`
reporting zero `map-entity-unaccounted` findings for these four maps.

14 new geometry records, 4 new bulk OSM sources, 1 entity unlocated
(`site:surf-4850-level-dune-far-detector`).

## Checks

| Feature | Expected | Source | Measured | Diff | Tolerance | Result |
| --- | --- | --- | --- | --- | --- | --- |
| SNOLAB cavity (span/diameter) | 22 m | src:sno-nim-detector-paper-2000, "barrel-shaped cavity, 22 m in diameter" | 21.98 m | 0.07% | 5% | PASS |

Point features (Davis Campus cavern, MINOS far-detector point) carry no
`checks[]` rows: a Point has fewer than two positions, so any `length`/
`area`/`span` row against it is unmeasurable
(`geometry-check-unmeasurable`) and would be a validator error, not a
passing check — the same reasoning CERN's researcher used for the
CMS cavern point. Both are instead `representation: surveyed` straight from
a rank-10-or-better paper, which is what earns them `confidence: verified`
without a check (contract §1.2).

## Residuals (informative; not formal `checks[]` rows)

| Comparison | Distance | Reading |
| --- | --- | --- |
| Yates Headframe (OSM way/512969103) vs. site:surf-davis-campus-lz's own surveyed point | 124 m | Corroborates that the Davis Campus (LZ, Majorana) sits right at the Yates Shaft, as SURF's own materials describe. |
| Administration Building (OSM way/512969102) vs. site:surf-surface-campus's own Nominatim point | 550 m | Well inside that site's precision_m (1000 m); flagged below as a correction candidate, not a contradiction. |
| Soudan Mine shaft house (OSM way/722791010) vs. site:soudan-minos-far-detector's own surveyed point | 127 m | Well inside that site's precision_m (100 m) × 3 allowance (300 m); a shaft collar need not sit directly above the underground chamber it serves. |
| SNOLAB surface office (OSM node/5403432442) vs. the SNO paper's underground cavity coordinate | 1145 m | Roughly consistent with snolab.ca's own "1.8 km" horizontal-distance figure between the 9 Shaft entrance and the underground facility (not identical, since the office node may not sit exactly above the shaft collar, and 1.8 km is along the access drift, not a straight horizontal line). |
| WIPP boundary (OSM way/389288415) centroid vs. site:wipp-surface-campus's own Wikipedia point | ~50 m | Consistent; both describe the same fenced site. |
| Yates Headframe vs. Ross Headframe clusters | 838 m | The two shaft complexes SURF's own materials describe as "about a mile apart" (loosely; not used as a sourced check — see conflicts). |

## Conflicts and honesty calls

1. **SNOLAB depth: 2039 m (SNO paper) vs. "2070 m" (SNOLAB's own pages).**
   The SNO NIM paper (`src:sno-nim-detector-paper-2000`) states "The center
   of the detector vessel is 2039 m below the surface"; SNOLAB's own facility
   page and Wikipedia both round to "2070 m (6800 ft) of overburden." These
   are plausibly different quantities (vertical depth to the vessel centre
   vs. rock overburden/water-equivalent measured along the access route), not
   necessarily a contradiction, but I used the more precise, directly-quoted
   vertical figure (2039 m) for `map:snolab`'s level depth rather than
   silently picking whichever number was more "official-sounding." Recorded
   in `levels[1].depth_m.note`.

2. **WIPP boundary area not asserted as a `checks[]` row.** The OSM
   `landuse=landfill` polygon (way/389288415) measures 1,187,824 m²
   (≈293.6 acres). A WebSearch synthesis reported "the Exclusive Use Area
   comprises approximately 293 acres" — a near-exact match — but the primary
   document I could actually fetch and read this session (WIPP's
   environmental-assessment Chapter 3, `wipp.energy.gov/library/acrsl/
   Chapter3.pdf`, extracted via `pdftotext` after WebFetch reported it as
   unparseable binary) names the four-tier land-use scheme (Property
   Protection Area, Exclusive Use Area, Off-Limits Area, 16-section
   land-withdrawal boundary) but does not itself state the EUA's acreage
   numerically. Per "nothing from memory," I did not cite the 293-acre
   figure as a sourced `checks[]` expected value; it is reported here as an
   informative residual instead.

3. **WIPP's two OSM mine-shaft features are not identified.** WIPP has four
   named shafts (waste, salt-handling, air-intake, exhaust); OSM tags the
   building at way/296041156 and the point at node/8684374640 only as
   `man_made=mineshaft`, 191 m apart, with no `name`. I drew both rather than
   guessing which is which — `geometry:wipp-mineshaft-building` and
   `geometry:wipp-mineshaft-point` say so explicitly in their own `method`
   and `notes`.

4. **EXO-200's own underground position is not drawn.** WIPP's North
   Experimental Area (655 m deep, per the existing `src:exo-200-doe-wipp-
   official-page`) is a level with no feature on it: no source fetched this
   session gives a horizontal offset or bearing from either surface shaft to
   the room EXO-200 occupied. I did **not** add a second `unlocated[]` row
   for this, because the map's completeness obligation
   (`map-entity-unaccounted`) is about the *site*
   (`site:wipp-surface-campus`), which is already drawn at the surface
   (`geometry:wipp-boundary`); adding a detector-level unlocated row here
   would go beyond what the validator asks for, but the gap is stated in the
   level's own `note` so it is not silently implied that the surface boundary
   somehow shows EXO-200's position.

5. **SNOLAB's other experiment halls share one point.** SNO+, DEAP-3600,
   DAMIC, SuperCDMS SNOLAB, nEXO and NEWS-G are all placed at
   `site:snolab-underground-lab` with no source giving each hall a distinct
   coordinate; `geometry:snolab-cavity` draws only the original SNO cavity
   (the one shape with a sourced size and centre) and its `method` says
   plainly that the other halls are not drawn separately. PICO and HALO,
   named in the brief's lead list, have no `detector` record in this atlas
   at all yet (checked `data/atlas/detectors/` and `data/atlas/experiments/`
   — neither exists), so they are outside this map's inventory entirely, not
   silently dropped from it.

## What is unlocated, and why (see `map.unlocated[]` on `map:surf`)

- **site:surf-4850-level-dune-far-detector** — the LBNF/DUNE far-detector
  caverns (two ~145 m caverns plus the Central Utility Cavern, per LBNF's own
  public excavation page, which also states the CUC is "190 m long, 20 m
  wide and 11 m high" per a search-engine extract of that same page, though
  my own WebFetch of it did not surface those numbers directly and I have
  not independently re-verified that specific quote from the primary page
  myself this session — so it is **not** cited as a sourced figure anywhere
  in the committed records, only mentioned here as a lead for the backlog).
  No source fetched this session states the caverns' horizontal offset or
  bearing from the Ross Shaft, a survey coordinate for the caverns, or a
  Homestake-mine-coordinate-system plan converted to lat/lon. Fermilab's
  "Volume 3: Long-Baseline Neutrino Facility for DUNE" design report
  (`lss.fnal.gov/archive/design/fermilab-design-2016-03.pdf`) returned
  `HTTP 403` to both WebFetch and a `curl -A 'Mozilla/5.0 ...'` retry. The
  existing site record's own coordinate is an explicit surface-proxy
  fallback (precision_m 2000, "REVIEW REQUIRED" in its own note) and was
  deliberately **not** used as a `derived`-shape anchor (its precision far
  exceeds any accuracy this shape could honestly claim).

## Backlog (concrete next steps, also in `map.surf.unlocated[].backlog`)

1. DUNE far-detector caverns: retry `lss.fnal.gov/archive/design/
   fermilab-design-2016-03.pdf` (403 this session) or the DUNE FD TDR's
   civil-engineering chapter for a cavern-layout figure with a stated offset
   from the Ross Shaft; failing that, ask SURF's or Fermilab's engineering
   group for a georeferenced site plan or the Homestake mine coordinate
   system's conversion to lat/lon.
2. WIPP: identify which of the four named shafts (waste, salt-handling,
   air-intake, exhaust) `geometry:wipp-mineshaft-building` and
   `geometry:wipp-mineshaft-point` are, and locate EXO-200's own room within
   the North Experimental Area (a DOE/EXO-200 site plan or a paper's stated
   offset from a shaft would resolve both).
3. SNOLAB: locate PICO and HALO (not yet `detector` records in this atlas at
   all — a gap for whichever workstream owns SNOLAB's detector inventory,
   not a geometry gap) and, once each SNOLAB-hosted detector has its own
   record, look for individual hall coordinates (a SNOLAB user handbook site
   plan, if one is published with a scale bar, would let each hall be drawn
   instead of sharing the one original-SNO-cavity point).
4. SURF: the ~137 named Lead, SD buildings mentioned in the brief were only
   partially drawn (5 of the SURF-specific ones: Yates Headframe/Hoist, Ross
   Headframe/Hoist, Administration Building); the Open Cut (historic surface
   pit) returned zero OSM elements under `landuse=quarry` or a name search
   this session and was not retried under other tags.
5. LBNF/DUNE CUC dimensions ("190 m long, 20 m wide, 11 m high") and the
   individual far-detector cavern dimensions ("145 m × 20 m × 28 m" per the
   task brief's own lead) were never independently confirmed by a source I
   personally fetched and read this session — worth a dedicated re-fetch
   attempt of `lbnf-dune.fnal.gov/how-it-works/excavations-and-structures/`
   (it loaded but a first WebFetch pass did not surface those numbers) before
   citing them anywhere.

## Site coordinate corrections (for the integrator)

```json
[
  {
    "site_id": "site:surf-surface-campus",
    "current": {"lat": 44.3474397, "lon": -103.7548247, "precision_m": 1000, "source": "src:surf-osm-nominatim (geocoder)"},
    "candidate": {"lat": 44.3517419, "lon": -103.751409, "precision_m": 50, "source": "src:geo-surf-osm-campus-buildings, OSM way/512969103 'Administration Building'"},
    "distance_from_current_m": 550,
    "reasoning": "The current point is a Nominatim search-result centroid for the whole 'Sanford Underground Research Facility, Lead, South Dakota' query, 550 m from any actual named SURF building. The candidate is a real, named SURF administration building footprint from the same OSM dataset, well within the current point's own 1000 m precision (no contradiction), but materially tighter. Not applied here per the geometry brief's 'do not edit existing records' rule -- reported for the integrator to review and apply if they agree a building footprint is a better campus anchor than a geocoder centroid."
  }
]
```

No other site coordinate correction is proposed: site:surf-davis-campus-lz,
site:snolab-underground-lab and site:soudan-minos-far-detector already carry
`verified`/precise coordinates that this session's new geometry reuses
directly (not independently re-derives), and site:surf-4850-level-dune-far-
detector and site:wipp-surface-campus remain the best available points given
what could be fetched this session (see Unlocated/Backlog above).

## Sources added

4 new `src:geo-*` records (all `source_type: openstreetmap`, rank 11):
`src:geo-surf-osm-campus-buildings`, `src:geo-snolab-osm-context`,
`src:geo-soudan-osm-shaft`, `src:geo-wipp-osm-extract`. See
`data/atlas/sources/geo-{surf,snolab,soudan,wipp}-*.json`. No existing
source, site, detector, accelerator or beamline record was edited; the new
geometry's non-OSM citations reuse existing source ids verbatim
(`src:lz-surf-heise-2015`, `src:lz-surf-davis-campus`,
`src:majorana-demonstrator-surf-news`, `src:sno-nim-detector-paper-2000`,
`src:minos-prd-2007-muon-charge-ratio`, `src:minos-detector-paper-2008`,
`src:exo-200-doe-wipp-official-page`, `src:dune-fd-tdr-vol-1`,
`src:fermilab-lbnf-dune-site`).

## Validator / build / test results

- `.venv/bin/python -m hepgraph.atlas.validate`: **0 errors**, 1592 warnings,
  4 informational — identical counts to the pre-existing baseline (verified
  by running validate before and after this session's changes); zero new
  findings of any severity reference `map:surf`, `map:snolab`,
  `map:soudan-underground-laboratory`, `map:wipp` or any of their geometry
  records.
- `.venv/bin/python -m hepgraph.atlas.build`: succeeds; four new bundles at
  `static/atlas/generated/geometry/{surf,snolab,soudan-underground-
  laboratory,wipp}.json` (6, 3, 2 and 3 features respectively; SNOLAB's
  bbox `[-81.2012545, 46.4695924, -81.1816585, 46.4751194]`; attribution
  `["© OpenStreetMap contributors (ODbL-1.0)"]` on all four). The pre-existing
  `atlas.json + manifest.json over the pilot budget` warning is unrelated to
  this session's work (whole-dataset size, not a maps/geometry defect).
- `scripts/atlas_coverage_report.py`: regenerated `docs/HEP_ATLAS_COVERAGE.md`;
  its "Local map geometry" table now lists all four new maps with correct
  feature/representation/unlocated/checks counts, and the "Facilities without
  a local map" list drops from 47 to 43 names.
- `.venv/bin/python -m pytest -q`: **667 passed, 139 skipped** (the skips are
  the Postgres/Neon-gated tests per `HEPGRAPH_TEST_DATABASE_URL`, unrelated
  to this work). `tests/test_atlas_geometry_data.py` in particular passed
  in full, including the canonical-JSON check (A11) that caught one
  self-inflicted bug: my first draft wrote geometry/map JSON with
  `ensure_ascii=True`, escaping the em dash in facility names as `—`
  instead of the literal UTF-8 character the repo's own `dump_json` writes;
  fixed and regenerated before committing.
