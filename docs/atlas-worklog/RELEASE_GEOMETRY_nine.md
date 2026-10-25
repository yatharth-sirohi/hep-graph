# Release geometry stream "nine" (2026-10-25)

Worktree `/Users/yatharthsirohi/Desktop/HEP-Graph-ar-nine`, branch `atlas-release-nine`.
Scope: the nine facilities that `GEOMETRY_COVERAGE_SET.md` put outside the local-map coverage
set. The release requires every facility to open a working to-scale map. Sources are prefixed
`src:geo-<facility>-…`. Grades before: "no map" for all nine.

## Method notes common to all nine

* **Overpass was unreachable from this machine all session** (both `overpass-api.de` and
  `lz4.overpass-api.de` timed out after 30 s with 0 bytes on `/api/status`; `overpass.kumi.systems`
  also timed out). Every OpenStreetMap shape was therefore read from the **OSM API 0.6**
  (`api.openstreetmap.org/api/0.6/map.json?bbox=…` and `…/<type>/<id>/full.json`), which serves the
  same element data. The `osm.timestamp` on each record is the HTTP `Date` of that API response
  (an extract time, in UTC); the element's own `version` and last-edit `timestamp` are in the
  source `excerpt` and in the geometry `locator`. Raw responses are in the session scratch
  directory, not in the repository.
* Wayback Machine returned HTTP 429 ("suspected abusive bot traffic") after a few requests; it
  was not used as a source in the end.
* INSPIRE was not touched.
* The three `status-not-derived-state` **errors** reported by `hepgraph.atlas.validate` on
  `mu3e` (collaboration, detector, experiment) are pre-existing and date-dependent (the validator
  derives state at the current month, 2026-10); none of them is on a file this stream touched. The integrator confirmed they are time-driven, present on the base branch and being fixed elsewhere; this stream's bar is "0 errors other than these three" and no mu3e file was touched.

---

## 1. argonne-national-laboratory (`map:argonne-national-laboratory`)

**Grade: no map → partial (footprints only).** There is no accelerator, beamline or detector
record at Argonne in the atlas, so no ring/linac feature can carry an `entity_id`; every shape other
than the campus boundary is a context building (`entity_id: null`).

| Entity / feature | Status | Representation | accuracy_m | Check |
| --- | --- | --- | --- | --- |
| `site:argonne-campus` → `geometry:argonne-campus-boundary` (OSM way 4372309, fence/institutional landuse, 11 570 m perimeter, 5.47 km²) | drawn | georeferenced | 15 | none: no official boundary or acreage figure could be fetched (anl.gov 403) |
| Advanced Photon Source ring-shaped Experiment Hall → `geometry:argonne-aps-experiment-hall` (OSM multipolygon relation 3126234: outer way 232798777, inner way 232798786; outer perimeter 1239.5 m, inner 1133 m) | drawn (the hall, **not** the orbit) | georeferenced | 10 | none, see below |
| APS Linear Accelerator Tunnel (411) → `geometry:argonne-aps-linac-tunnel` (OSM way 1378754812) | drawn | georeferenced | 10 | none; function rests on the OSM name (`source=local knowledge`) |
| APS Injection Wing (412) → `geometry:argonne-aps-injection-wing` (OSM way 232798785) | drawn | georeferenced | 10 | none; same caveat |
| Building 203 "Physics Building" → `geometry:argonne-building-203-atlas` (OSM way 283559227; the building that houses ATLAS) | drawn (whole building, not the linac) | georeferenced | 10 | none |
| APS storage ring orbit (1104 m circumference) | **unlocated** (map row on `facility:argonne-national-laboratory`) | — | — | — |
| ATLAS accelerator layout (injectors, booster, ATLAS linac, target areas) | **unlocated** | — | — | — |

**Sources fetched and quoted**

* APS orbit circumference: "The APS storage ring, 1104 m in circumference, has 40 periodic
  sectors." — OSTI record 283724, *The Advanced Photon Source list of parameters*
  (https://www.osti.gov/biblio/283724), read via WebFetch of the record abstract. Used for the
  `unlocated[]` reason and the notes, not as a `checks[]` row (no shape here measures the orbit).
* ATLAS building: "ATLAS is located in Building 203 at Argonne National Laboratory, the same
  building where Marie Goeppert-Mayer worked on her Nobel-prize winning contributions to the
  nuclear shell model." — Argonne Physics Division, *The ATLAS Facility at Argonne National
  Laboratory* (laboratory portrait ANL/PHY/PP-87036, 29 Jul 1997), OSTI record 505382,
  PDF page 1 (the PDF is a scan with no text layer; I read the page image). Its Figure 1 is an
  unscaled cutaway and is linked under `map.schematics`, never traced.

**Honesty calls and conflicts**

1. *The APS ring was not drawn as a ring.* OSM maps only the ring-shaped hall (inner outline ≈
   1133 m, outer ≈ 1240 m). The sourced 1104 m orbit is 2.6 % shorter than the inner outline,
   which is expected for a beam path inside a hall wall, but that is plausibility, not a
   measurement of the orbit. A `length` check on the hall polygon measures the outer ring
   (1240 m, +12 % vs 1104 m) and would fail; a loosened tolerance would be a fake check. No circle
   was fitted: the APS lattice is 40 sectors, and no source gives a radius and centre.
2. *Building 203 ≠ ATLAS.* The report identifies the building; the comb-shaped footprint
   (15 961 m², 266 m span) includes the Physics Division's offices and labs. It is labelled as the
   building, never as the accelerator.
3. anl.gov, www.phy.anl.gov, map.anl.gov and the sandbox mirror all returned HTTP 403 to
   every fetch (curl with a browser User-Agent and WebFetch); `eic-doccert.phy.anl.gov` does not
   resolve. The official ATLAS and APS prose pages could not be read, so the official quotes come
   from OSTI-hosted laboratory documents.

**Site coordinate corrections** (for the integrator; none applied here)

```json
[{"site_id": "site:argonne-campus",
  "current": {"lat": 41.67364, "lon": -88.00173, "precision_m": 800, "source": "src:ror-05gvnxz63"},
  "proposed": {"lat": 41.709622, "lon": -87.980823, "precision_m": 500, "kind": "campus"},
  "distance_from_current_m": 4361,
  "source": "src:geo-argonne-osm-campus-boundary (OSM way 4372309, 'Argonne National Laboratory', addr:street Cass Avenue 9700, barrier=fence, source=survey)",
  "quote": "OSM tags: addr:housenumber=9700, addr:street=Cass Avenue, name=Argonne National Laboratory, barrier=fence, landuse=institutional; centroid of the 131-node fence polygon.",
  "note": "The ROR point lies about 4.4 km south-west of the fenced campus, near the village of Lemont, and well outside the existing precision_m of 800."}]
```

**Remaining backlog**

1. APS storage-ring path: an APS Upgrade TDR survey/alignment table or a published lattice drawing
   with sector coordinates, to place the orbit and add a `length` check against 1104 m.
2. ATLAS: a Building 203 survey drawing or the ATLAS floor plan (a graphic at
   phy.anl.gov/atlas/facility/floorplan.html) georeferenced against ≥ 3 OSM building corners
   (cite, never copy); then the three target areas and the linac axis.
3. An official campus acreage or boundary figure (anl.gov is blocked from here) for an `area`
   check on the boundary.
4. Atlas-side: `accelerator` records for the APS and ATLAS would let the ring/linac be features
   with an `entity_id` (this stream may not create entities).
