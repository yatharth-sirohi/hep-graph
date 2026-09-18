# Geometry worklog: DESY, PSI, KIT Karlsruhe (map:desy, map:psi)

Researcher: geometry-desy-psi-kit. Worktree
`/Users/yatharthsirohi/Desktop/HEP-Graph-maps-desy`, branch
`hep-atlas-local-maps-desy`. Sources prefixed `src:geo-desy-*` / `src:geo-psi-*`.
Validated in-place (validator/build already present on this worktree).

## Method note: Overpass access this session

DESY's geometry was fetched cleanly through Overpass early in the session
(five queries, all HTTP 200, no rate-limit or timeout errors). Partway
through, once PSI research began, both mirrors
(`overpass-api.de` and `lz4.overpass-api.de`) stopped accepting connections
outright (`curl: (7) Couldn't connect to server`, not a 429/504 a backoff
would clear) and never recovered for the rest of the session — six separate
checks over roughly 25 minutes, spaced 45–90 s apart per the "back off 60 s"
rule, all failed the same way. I fell back to Nominatim
(`nominatim.openstreetmap.org`, 1 request/s, distinct service, same
underlying OSM data) for PSI's and KIT's campus boundaries, since Nominatim
returns full way geometry with `polygon_geojson=1`. Nominatim only supports
name search, not Overpass's tag/bbox queries, so it could not find the
*unnamed* buildings (PSI's Ring Cyclotron building, PSI's large experimental
hall, KIT's KATRIN spectrometer hall) the way Overpass's proximity-to-ring
search found DESY's unnamed halls. That gap is the reason PSI's accelerator
stays unlocated and no KIT map was produced at all (see below).

## Inventory

| Entity | Drawn? | Feature(s) | Representation | Accuracy | Check |
| --- | --- | --- | --- | --- | --- |
| facility:desy | map:desy authored | — | — | — |
| site:desy-hamburg-campus | drawn | geometry:desy-campus-boundary | georeferenced | 10 m | none (no official boundary figure) |
| site:desy-hera-north-hall-h1 | drawn | geometry:hera-halle-nord | georeferenced | 8 m | none formally asserted; centroid 37.7 m from the HERA ring |
| site:desy-hera-south-hall-zeus | **unlocated** | — | — | — | — |
| accelerator:hera | drawn | geometry:hera-tunnel-ring | georeferenced, **verified** | 20 m | length 6317.2 m vs 6336 m (DESY, tol 2%) — **pass**, 0.30% |
| detector:h1 | accounted via site:desy-hera-north-hall-h1 | (same hall) | — | — | — |
| detector:alps-ii | accounted via site:desy-hera-north-hall-h1 | (same hall) | — | — | — |
| detector:zeus | accounted via site:desy-hera-south-hall-zeus (unlocated) | — | — | — | — |
| detector:iaxo | **out of scope** | — | — | — | no `placements[]` recorded on the detector; the facilities workstream has not yet sited it on a `site:` id, so it has nothing for a map to draw or unlocate |
| (context) PETRA III | drawn | geometry:petra-iii-tunnel | georeferenced | 20 m | measured 2296.4 m vs the commonly-cited 2304 m (0.3%), reported as a residual, not a `checks[]` row (no rank ≤10 source fetched) |
| accelerator:doris (no atlas record exists) | n/a | — | — | — | no OSM trace found under 'DORIS'/'Doppel-Ring'; not an atlas entity either, so nothing to unlocate |
| facility:psi | map:psi authored | — | — | — | — |
| site:psi-villigen | drawn | geometry:psi-campus-boundary | georeferenced | 10 m | none (no official boundary figure) |
| accelerator:psi-hipa | **unlocated** | — | — | — | — |
| detector:meg / detector:meg-ii / detector:mu3e | accounted via site:psi-villigen | (same site) | — | — | — |
| facility:kit-karlsruhe | **no map produced** (see below) | — | — | — | — |

5 geometry records total (4 for DESY: HERA ring, campus boundary, North
Hall, PETRA III tunnel; 1 for PSI: campus boundary). 2 entities unlocated
(site:desy-hera-south-hall-zeus, accelerator:psi-hipa).

## Checks (expected vs measured)

All geodesic lengths computed with `hepgraph.atlas.geo.line_length_m`
(haversine, R = 6 371 008.8 m), matching the validator's own recomputation
(confirmed by 0 `geometry-check-failed` findings).

| Feature | Expected | Source | Measured | Diff | Tolerance | Result |
| --- | --- | --- | --- | --- | --- | --- |
| HERA ring | 6 336 m | src:geo-desy-hera-facts-page, "Length: 6336 metres" | 6 317.2 m | 0.30% | 2% | PASS |
| PETRA III tunnel | ~2 304 m (commonly cited, not independently sourced this session) | — | 2 296.4 m | 0.33% | — (informational only) | consistent |

The HERA ring's own OSM tags (`length=6336`, `depth=-25`) independently
match the fetched DESY facts page and Wikipedia's "10 to 25 m below ground
level, circumference of 6.3 km" — three independent readings agreeing to
within the tag's own precision.

## Site coordinate corrections (for the integrator)

All three currently rest on an apparently mis-geocoded ROR point; none are
applied here — this research does not edit existing site records.

```json
[
  {
    "site_id": "site:desy-hamburg-campus",
    "current": {"lat": 53.55073, "lon": 9.99302, "precision_m": 800, "source": "src:ror-01js2sh04"},
    "proposed": {"lat": 53.5770744, "lon": 9.8807554, "precision_m": 300, "kind": "campus"},
    "distance_from_current_m": 7972,
    "evidence": [
      "OSM way 276641657 ('Deutsches Elektronen-Synchrotron DESY'), tagged with DESY's own postal address (Notkestrasse 85, 22607 Hamburg); centroid 53.5771N, 9.8808E (src:geo-desy-osm-campus-boundary)",
      "src:desy-wikipedia's own excerpt, already cited by the existing site record: 'Primary campus in Hamburg-Bahrenfeld (53 34'33''N 9 52'46''E)' = 53.5758N, 9.8794E, 150 m from the OSM centroid"
    ],
    "note": "The ROR v2 record for DESY (ror.org/01js2sh04) appears to geocode to the wrong point -- about 8 km from DESY's actual Hamburg-Bahrenfeld campus, and from the very Wikipedia coordinate the existing site record cites in its own excerpt. Two independent fixes (OSM campus polygon, Wikipedia infobox) agree with each other to 150 m and disagree with ror-01js2sh04 by ~8 km; worth a fresh ROR API read to see if a different address field should have been used."
  },
  {
    "site_id": "site:desy-hera-north-hall-h1",
    "current": {"lat": 53.55073, "lon": 9.99302, "precision_m": 800, "source": "src:ror-01js2sh04"},
    "proposed": {"lat": 53.5901057, "lon": 9.8844408, "precision_m": 50, "kind": "detector"},
    "distance_from_current_m": 8401,
    "evidence": [
      "OSM way 131496014 ('HERA Halle Nord' building footprint), centroid 53.5901N, 9.8844E, 37.7 m from geometry:hera-tunnel-ring's own north end (src:geo-desy-osm-hera-halle-nord)",
      "Wikipedia 'HERA (particle accelerator)': 'H1 was a universal detector ... located in the HERA Hall North.'"
    ],
    "note": "This correction upgrades the site from a campus-grade fallback to an actual hall-building position; recommend kind: detector, precision_m in the 30-50 m range (building footprint accuracy), superseding the shared ROR point entirely."
  },
  {
    "site_id": "site:desy-hera-south-hall-zeus",
    "current": {"lat": 53.55073, "lon": 9.99302, "precision_m": 800, "source": "src:ror-01js2sh04"},
    "proposed": {"lat": 53.5770744, "lon": 9.8807554, "precision_m": 800, "kind": "campus"},
    "distance_from_current_m": 7972,
    "evidence": ["Same OSM campus polygon as the desy-hamburg-campus row above; no hall-specific fix found this session (see unlocated[])."],
    "note": "Interim fix only -- moves the fallback point onto the correct campus instead of leaving it 8 km away. A hall-specific position should replace this once ZEUS's South Hall building is identified (see backlog)."
  },
  {
    "site_id": "site:psi-villigen",
    "current": {"lat": 47.52682, "lon": 8.21486, "precision_m": 800, "source": "src:ror-03eh3y714"},
    "proposed": {"lat": 47.5375192, "lon": 8.2250675, "precision_m": 300, "kind": "campus"},
    "distance_from_current_m": 1415,
    "evidence": [
      "Area-weighted centroid of the combined OSM campus MultiPolygon, ways 28028409 / 26680824 / 26680821, all named 'Paul Scherrer Institut' (src:geo-psi-osm-campus-boundary)",
      "Named OSM locality nodes 'PSI West' (47.5368N, 8.2222E) and 'PSI Ost' (47.5386N, 8.2300E) both fall inside the proposed campus polygon, not near the current ROR point"
    ],
    "note": "Smaller discrepancy than DESY's (1.4 km vs 8 km) but still outside the current precision_m of 800 m; the ROR point sits just off the actual campus footprint."
  },
  {
    "site_id": "site:kit-campus-north",
    "current": {"lat": 49.09591, "lon": 8.42661, "precision_m": 1500, "source": "src:katrin-kit-campus-north-coordinates"},
    "proposed": {"lat": 49.1018534, "lon": 8.4331202, "precision_m": 800, "kind": "campus"},
    "distance_from_current_m": 813,
    "evidence": ["OSM way 155843597 ('Campus Nord', research_institute), fetched via Nominatim; centroid 49.1019N, 8.4331E. Cited here directly by its OSM URL (https://www.openstreetmap.org/way/155843597) since no committed geometry/source record uses it -- no KIT map was produced this session (see below)."],
    "note": "Minor refinement, well within the current 1500 m precision_m, so lower priority than the DESY/PSI rows above."
  }
]
```

## Conflicts and honesty calls

1. **PETRA III drawn as a context `tunnel`, not a `ring`.** No
   `accelerator:petra` record exists in the atlas yet (the ID registry lists
   it only as "optional"), and `feature_type: ring` requires an `entity_id`
   per the contract. Drawn with `entity_id: null`, `feature_type: tunnel`
   instead, exactly as `map:cern` drew the unattached Antiproton Decelerator
   Hall. DORIS has no OSM trace under that name or "Doppel-Ring" and, having
   no atlas entity either, is simply absent rather than unlocated.

2. **HERA Hall North stands in for two detectors.** `geometry:hera-halle-nord`
   carries `entity_id: site:desy-hera-north-hall-h1` (the site, not the
   detector, following `map:cern`'s Point-N convention so the validator's
   `map-entity-unaccounted` rule — which scans `entity_id`, not `site_id` —
   credits the site). Both `detector:h1` (1992–2007) and `detector:alps-ii`
   (active, in the same former HERA tunnel straight section) place at this
   one site id, so one feature accounts for both; it is not time-sliced
   because sites carry no independent `state_segments` in this schema
   version, the same minor over-display `map:cern`'s worklog already flagged.

3. **ZEUS's South Hall: a candidate rejected for lack of a name.** OSM way
   24892547 ("HalleSO", `building=service`) sits only 88.8 m from the HERA
   ring's own geometric south extreme — closer than most other named DESY
   buildings are to the ring — but nothing fetched this session names it as
   ZEUS's hall, and "SO" more plausibly abbreviates a compass/site code than
   "Süd" (South). Per the "nothing from memory" standard this is not drawn;
   it is named as a lead in the `unlocated[]` `backlog` instead of being
   guessed into the map.

4. **No KIT map produced.** Per the brief's explicit condition ("a KIT map
   only if you can source the KATRIN hall footprint; otherwise say so"): I
   could not source it. Wikipedia and the KATRIN/TLK official pages state
   only that the main spectrometer sits at "KIT Campus North" / "Tritium
   Laboratory Karlsruhe", with a Wikipedia-only coordinate
   (49.09583N, 8.43611E) that is a page-level pin, not a hall footprint.
   Reverse-geocoding that point (Nominatim) found only a named *point*
   ("Tritiumlabor Karlsruhe", an office/research node ~110 m away), not a
   building polygon. The KIT-published "Lageplan Campus Nord" site plan
   (https://www.kit.edu/downloads/campus-nord.pdf) is a graphical PDF with no
   extractable text layer for building labels, and per the contract an
   official PDF may only ever be cited, never traced as a to-scale shape
   anyway. I did find KIT Campus North's own OSM boundary (way 155843597,
   via Nominatim) but drawing a whole-campus boundary with nothing
   detector-specific inside it did not seem worth a whole map, matching the
   brief's framing of the KIT deliverable as conditional on the spectrometer
   building specifically. Nothing was written to `data/atlas/maps/`,
   `data/atlas/geometry/` or `data/atlas/sources/` for KIT.

5. **PSI: campus drawn, the accelerator itself is not.** `accelerator:psi-hipa`
   (the 48 m-circumference Ring Cyclotron) is real, active, and has a
   `site_id`, but its building has no distinct OSM name (four Nominatim name
   searches for "Ringzyklotron"/"Ring Cyclotron"/"Zyklotron"/"Cyclotron",
   bounded to the PSI campus, all returned zero results) and the Overpass
   outage prevented the tag/proximity search that found DESY's equally
   unnamed North Hall. This is recorded as `unlocated[]` on `map:psi` rather
   than skipping the whole PSI map, since the campus boundary itself is
   solidly sourced and MEG/MEG-II/Mu3e's site is accounted for through it.

6. **PSI campus drawn as a `MultiPolygon` from three separate OSM ways**,
   matching the official description that the site "spans ... Villigen and
   Wurenlingen on either side of the River Aare" (fetched from PSI's own
   Wikipedia page and corroborated by named OSM locality nodes "PSI West"
   and "PSI Ost" falling inside the respective polygons). All three came
   through Nominatim's `polygon_geojson=1`, not a direct Overpass extract;
   `osm.timestamp` records the access date since Nominatim's response has no
   `timestamp_osm_base` field the way an Overpass extract does.

7. **HERA tunnel ring reaches `confidence: verified`** on the strength of a
   rank-2 `official_facility_site` source (DESY's own "H1, ZEUS, HERMES"
   page, which states "Length: 6336 metres" verbatim) passing the length
   check against the OSM-measured 6317.2 m (0.30%, tolerance 2%) — the same
   pattern `map:cern` used for the LHC ring. HERA's own OSM way additionally
   carries `length=6336` and `depth=-25` tags matching this independently, a
   stronger cross-agreement than most of CERN's rings had.

## Backlog (concrete next steps, also in `map.unlocated[].backlog`)

1. ZEUS South Hall: once Overpass is reachable, search by proximity to
   `geometry:hera-tunnel-ring`'s southern arc the way `geometry:hera-halle-nord`
   was found for the north (the DESY building `HalleSO`, way 24892547, is
   the leading unconfirmed candidate); or find a ZEUS TDR / DESY GIS layer
   that names the building.
2. PSI HIPA: retry Overpass for an unnamed-building tag search inside the
   "PSI West" sub-area (near 47.5368N, 8.2222E); or request PSI's own
   site-plan/GIS layer for the Ring Cyclotron and the large experimental
   hall (πE5, housing MEG-II and Mu3e).
3. KIT KATRIN: once Overpass is reachable, a tag/proximity search around
   Wikipedia's KATRIN coordinate (49.09583N, 8.43611E) inside KIT Campus
   North (OSM way 155843597) should find the spectrometer hall building the
   same way DESY's and PETRA's unnamed structures were found; then author
   `map:kit-karlsruhe` per the brief.
4. PETRA III: find a rank ≤10 source stating its circumference to turn the
   0.33% residual into a formal `checks[]` row (not required for a context
   feature, but would strengthen it), and consider creating
   `accelerator:petra` in the facilities workstream so the ring can be drawn
   as `feature_type: ring` with a proper `entity_id`.
5. detector:iaxo: needs a `placements[]` entry (a `site:` id at DESY) from
   the facilities/axions workstream before any geometry work can start on
   BabyIAXO.
6. FLASH I/II and the European XFEL tunnels: found in the same DESY Overpass
   extract (OSM ways 112472169, 281322116) but not drawn this session
   (optional per the brief, "if cheap" — deprioritised in favour of PSI/KIT
   once Overpass went down); FLASH has no atlas accelerator entity either,
   so it would be a context feature like PETRA III.

## Sources added

7 new source records: `src:geo-desy-osm-hera-tunnel`,
`src:geo-desy-osm-campus-boundary`, `src:geo-desy-osm-hera-halle-nord`,
`src:geo-desy-osm-petra-iii-tunnel`, `src:geo-desy-hera-facts-page` (all
OpenStreetMap except the last, an official DESY page), and
`src:geo-psi-osm-campus-boundary`. No existing source, site, detector,
accelerator or beamline record was edited — all citations of pre-existing
sources (`src:hera-wikipedia`, `src:desy-wikipedia`, `src:zeus-wikipedia`,
`src:facilities-verify-psi-hipa-page`) reuse the ids verbatim.

## Validator / build / test results

- `.venv/bin/python -m hepgraph.atlas.validate`: **0 errors**, 1592
  warnings, 4 informational (same warning count as before this session's
  changes — no new warning or informational finding was introduced by any
  DESY or PSI record).
- `.venv/bin/python -m hepgraph.atlas.build`: succeeds; `geometry/desy.json`
  has 4 features (HERA ring, campus boundary, North Hall, PETRA III tunnel);
  `geometry/psi.json` has 1 feature (campus boundary). No `geometry/kit-karlsruhe.json`
  was produced.
- `.venv/bin/python -m pytest -q`: **667 passed**, 139 skipped (all skips
  are pre-existing Postgres/Neon integration tests gated on env vars this
  task never touches).
