# Geometry worklog — European underground laboratories (LNGS, LSM Modane, LSC Canfranc, Boulby, Baksan)

Researcher: geometry agent (branch `hep-atlas-local-maps-euro-ug`), 2026-09-18/19. This worklog was
assembled by the integrator on 2026-09-21 from the committed map and geometry records because the
researcher session ended before writing it; every statement below is read from those records
(`method`, `note`, `checks`, `unlocated`), not from memory.

## Inventory

### map:lngs

Sites: site:lngs-hall-a, site:lngs-hall-b, site:lngs-hall-c. Extent 8000 m. Levels: `surface`; `gran-sasso-tunnel` (~1400 m (average)).

| Feature | Type | Entity | Level | Representation | Accuracy (m) | Confidence | Checks |
| --- | --- | --- | --- | --- | ---: | --- | ---: |
| geometry:lngs-external-labs-boundary | building | facility:lngs | surface | georeferenced | 10 | approximate | 0 |
| geometry:lngs-external-labs-point | other | facility:lngs | surface | surveyed | 30 | verified | 0 |
| geometry:lngs-hall-a | other | site:lngs-hall-a | gran-sasso-tunnel | derived | 400 | derived | 0 |
| geometry:lngs-hall-b | other | site:lngs-hall-b | gran-sasso-tunnel | derived | 400 | derived | 0 |
| geometry:lngs-hall-c | other | site:lngs-hall-c | gran-sasso-tunnel | derived | 400 | derived | 0 |
| geometry:lngs-lab-access-zone | tunnel | facility:lngs | gran-sasso-tunnel | derived | 50 | derived | 0 |
| geometry:lngs-tunnel-gran-sasso | tunnel | — | gran-sasso-tunnel | georeferenced | 25 | verified | 1 |

Map notes (verbatim from the record):
- Linked map: map:cern, because beamline:cngs (CERN's own beamline, facility_id facility:cern) names site:lngs-hall-c as its far_detector_site_ids target (732 km baseline, 2006-2012 beam operation for OPERA/ICARUS). The CNGS direction line itself is drawn on map:cern, not here, since the beamline entity belongs to CERN's inventory, not LNGS's.
- geometry:lngs-hall-a, geometry:lngs-hall-b and geometry:lngs-hall-c intentionally share one derived coordinate (the midpoint of the sourced ~700 m access-zone stretch): no source fetched this session distinguishes the three halls' order or position within that zone. This will raise the validator's geometry-duplicate-shape warning for all three pairs; documented here and in the facility worklog per the contract's 'a warning you leave must be explained' rule, and not avoided by leaving any of the three sites unlocated, since a sourced (if coarse) position is available for all three and is more informative than omission.
- The Pandola 2011 overview (src:geo-euro-ug-pandola-2011) names several LNGS experiments not present in this atlas dataset (Gator, MACRO, WArP, LUNA, COBRA, DAMA/Libra, STELLA/GEMPI2); they are not listed in unlocated[] because they are not atlas entities this session may create (out of this geometry-research brief's scope) — flagged in the facility worklog as backlog for whichever lead owns LNGS's experiment roster.

### map:modane-underground-laboratory

Sites: site:lsm-frejus. Extent 10000 m. Levels: `surface`; `frejus-tunnel` (1700 m of rock).

| Feature | Type | Entity | Level | Representation | Accuracy (m) | Confidence | Checks |
| --- | --- | --- | --- | --- | ---: | --- | ---: |
| geometry:modane-carre-sciences-point | other | facility:modane-underground-laboratory | surface | georeferenced | 15 | approximate | 0 |
| geometry:modane-lsm-underground | other | site:lsm-frejus | frejus-tunnel | georeferenced | 100 | approximate | 0 |
| geometry:modane-tunnel-frejus | tunnel | — | frejus-tunnel | georeferenced | 35 | approximate | 1 |

Map notes (verbatim from the record):
- The pre-existing site:lsm-frejus coordinate (45.1962509, 6.6667021, precision_m 500, src:lsm-osm-nominatim) is an OSM/Nominatim point essentially co-located with the Carré Science surface outreach building (geometry:modane-carre-sciences-point), about 6.4 km from the underground laboratory itself by tunnel. See the facility worklog for a proposed correction using geometry:modane-lsm-underground's own coordinate.
- The Fréjus road tunnel gained a second, parallel tube in July 2025 (src:geo-modane-sftrf-second-tube-pr); geometry:modane-tunnel-frejus's representation is kept 'approximate' because this session could not confirm from OSM tags alone which of the two tubes its traced line follows over its full length (Overpass, which would have let this be resolved by relation membership, was unreachable). Both tubes run closely parallel and are the same length, so the practical effect on the laboratory's derived position is small.

### map:canfranc-underground-laboratory

Sites: site:lsc-canfranc. Extent 7500 m. Levels: `surface`; `somport-tunnels` (800 m under Mount Tobazo).

| Feature | Type | Entity | Level | Representation | Accuracy (m) | Confidence | Checks |
| --- | --- | --- | --- | --- | ---: | --- | ---: |
| geometry:canfranc-lab-underground | other | site:lsc-canfranc | somport-tunnels | georeferenced | 150 | approximate | 0 |
| geometry:canfranc-surface-building | building | facility:canfranc-underground-laboratory | surface | georeferenced | 10 | approximate | 0 |
| geometry:canfranc-tunnel-rail-somport-stub | tunnel | — | somport-tunnels | georeferenced | 50 | approximate | 0 |
| geometry:canfranc-tunnel-somport-road | tunnel | — | somport-tunnels | georeferenced | 20 | verified | 1 |

Map notes (verbatim from the record):
- The pre-existing site:lsc-canfranc coordinate (42.7493154, -0.5162702, kind campus, precision_m 500) is the same OSM feature as geometry:canfranc-surface-building, the laboratory's administrative offices at Canfranc-Estación, about 3.0 km from the underground laboratory itself (geometry:canfranc-lab-underground, an independently OSM-tagged feature 'Galería de evacuación 12', Aía). See the facility worklog for a proposed site coordinate correction and a proposed `kind` change to underground_lab.
- The historic Canfranc railway tunnel is only partially traced in OpenStreetMap (about 1.28 km of a tunnel usually cited at ~7.8 km); geometry:canfranc-tunnel-rail-somport-stub is drawn honestly as a partial trace rather than extended by guesswork. See the facility worklog backlog.

### map:boulby-underground-laboratory

Sites: site:boulby-mine. Extent 1200 m. Levels: `surface`; `boulby-underground` (1.1 km beneath the North York Moors).

| Feature | Type | Entity | Level | Representation | Accuracy (m) | Confidence | Checks |
| --- | --- | --- | --- | --- | ---: | --- | ---: |
| geometry:boulby-mine-boundary | boundary | site:boulby-mine | surface | georeferenced | 15 | approximate | 0 |

Map notes (verbatim from the record):
- This map is honestly thin: it can draw the mine's surface works site (traced from aerial imagery) and a sourced depth for the underground level, but no fetched source this session locates the specific shaft or the underground laboratory workings within that surface footprint. No detector is placed at site:boulby-mine in this atlas dataset (ZEPLIN and DRIFT, which the laboratory has hosted, are not yet atlas entities), so no entity besides the site itself needs accounting here.
- Overpass (which could plausibly find shaft-head buildings or man_made=mineshaft nodes by a bounding-box tag query) was unreachable throughout this session; see the facility worklog.

### map:baksan-neutrino-observatory

Sites: site:baksan-sage-underground-lab. Extent 800 m. Levels: `surface`; `andyrchi-tunnels` (up to ~2100 m (SAGE hall, vertical)).

| Feature | Type | Entity | Level | Representation | Accuracy (m) | Confidence | Checks |
| --- | --- | --- | --- | --- | ---: | --- | ---: |
| geometry:baksan-bno-building | building | facility:baksan-neutrino-observatory | surface | georeferenced | 10 | approximate | 0 |
| geometry:baksan-neutrino-village-boundary | boundary | — | surface | georeferenced | 15 | approximate | 0 |

Unlocated:
- `site:baksan-sage-underground-lab` — SAGE's own paper states the laboratory is 3.5 km from the tunnel/adit entrance, but no source fetched this session gives the tunnel's path or compass bearing into Mount Andyrchi, and OpenStreetMap does not appear to trace the tunnel (no matching way was found by name search, and a tag-based bounding-box search was not possible because Overpass was unreachable throughout this session). Deriving a position without a sourced bearing would be a guess, not a measurement. Backlog: Once Overpass is reachable, search a bounding box around the BNO building (way 1504181774) for tunnel=yes or man_made=adit ways; failing that, find a published topographic map or paper figure (e.g. an INR technical report) giving the tunnel's compass bearing so its line can be sourced rather than guessed, then walk 3.5 km along it per src:sage-1999-capture-rate.

Map notes (verbatim from the record):
- This map is honestly thin: the surface administrative building and the Neutrino settlement are drawn from OpenStreetMap, but the tunnels themselves and the SAGE underground hall are not, because no fetched source this session gives the tunnel's path/bearing and OpenStreetMap does not appear to trace it (no way was found via Nominatim name search for 'Baksan tunnel' or Cyrillic equivalents, and a bounding-box tag search that Overpass would have allowed was not possible — Overpass was unreachable throughout this session, see the facility worklog).
- SAGE's own 1999 paper (src:sage-1999-capture-rate) states the laboratory is '3.5 km from the entrance of a horizontal adit excavated into the side of Mount Andyrchi' with a 60x10x12 m chamber (src:geo-euro-ug-pandola-2011); this is recorded here and in the facility worklog as backlog for a future pass with Overpass access or a topographic source giving the tunnel's bearing.

## Checks (expected vs measured, from the built bundles)

- geometry:lngs-tunnel-gran-sasso: length expected 10176.0 measured 10186.542415069094 tolerance 0.02 → pass
- geometry:modane-tunnel-frejus: length expected 12870.0 measured 12862.19233963511 tolerance 0.02 → pass
- geometry:canfranc-tunnel-somport-road: length expected 8600.0 measured 8629.627983778615 tolerance 0.02 → pass

## Conflicts and honesty calls

- LNGS halls A, B and C are three `derived` points at one shared coordinate (the midpoint of the sourced access-zone stretch, accuracy 400 m): no fetched source distinguishes the halls' order along the zone. The validator's `geometry-duplicate-shape` warning on halls B and C is intentional and documented in the map notes; the halls are NOT drawn as footprints.
- LSM (Modane) and LSC (Canfranc): the pre-existing site coordinates are the surface outreach/administrative buildings, 6.4 km and 3.0 km respectively from the underground laboratories (see the map notes). The underground points drawn here are OSM-georeferenced with 100–150 m accuracy.
- Boulby and Baksan are honestly thin: surface works / settlement boundaries only; no shaft or underground hall position was sourced (Overpass was unreachable for most of the session).

## Site coordinate corrections (for the integrator)

The two underground laboratory points below replace surface-building points that were standing in for the labs. Both are OpenStreetMap-georeferenced (rank 11), so under A17/A23 they are recorded as `campus`-kind points with `confidence: approximate` unless a rank ≤ 10 source corroborates them.

```json
[
  {
    "site_id": "site:lsm-frejus",
    "lat": 45.140081,
    "lon": 6.688208,
    "precision_m": 100,
    "kind": "campus",
    "confidence": "approximate",
    "sources": [
      "src:geo-modane-osm-lsm-way"
    ],
    "locator": "OSM way 235115147, as of 2026-09-18T22:47:00Z",
    "note": "Underground laboratory position from geometry:modane-lsm-underground (OpenStreetMap-georeferenced, accuracy 100 m); the previous point was the surface building."
  },
  {
    "site_id": "site:lsc-canfranc",
    "lat": 42.774672,
    "lon": -0.529091,
    "precision_m": 150,
    "kind": "campus",
    "confidence": "approximate",
    "sources": [
      "src:geo-canfranc-osm-lab-underground"
    ],
    "locator": "OSM way 1075274236, as of 2026-09-18T23:05:00Z",
    "note": "Underground laboratory position from geometry:canfranc-lab-underground (OpenStreetMap-georeferenced, accuracy 150 m); the previous point was the surface building."
  }
]
```

## Backlog

- LNGS: a source ordering halls A/B/C along the access zone (LNGS site plan with scale, or the hall coordinates published in an experiment TDR) to replace the shared point with three footprints.
- Boulby: shaft-head buildings / man_made=mineshaft nodes via Overpass; the laboratory position at the 1.1 km level.
- Baksan: tunnel bearing and path (SAGE at 3.5 km from the adit entrance per the SAGE 1999 paper).
- Canfranc: the historic railway tunnel is only 1.28 km traced in OSM (of ~7.8 km).
- Modane: confirm which Fréjus tube the traced line follows (second tube opened July 2025).
