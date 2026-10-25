# Release geometry stream arrays-a (2026-10-25)

Worktree `HEP-Graph-ar-arrays`, branch `atlas-release-arrays`. New sources are prefixed
`src:geo-arrays-*`. Facilities: Amundsen-Scott South Pole Station (IceCube, IceTop),
Pierre Auger Observatory, Telescope Array (Utah), LHAASO (Daocheng), Baikal-GVD.
Previous worklogs: `GEOMETRY_arrays.md`, `GEOMETRY_polar-sea.md`.

## Method notes common to all five

* The contract (`docs/HEP_ATLAS_GEOMETRY.md` section 1.2, `geo.GEOJSON_TYPES`) allows no
  `MultiPoint`. Groups of stations, tanks or strings are therefore **MultiPolygons of small
  square markers**, one record per group of at most 400 vertices (80 squares per record at
  5 positions each; 78 for the IceCube strings). The marker size is stated in each record's
  `method` (a position marker; where a real instrument size is sourced it is that size). The
  browser already handles `MultiPoint` (`static/atlas/js/localmap.js`), so allowing it in
  `GEOJSON_TYPES` would let each array be one record; that is a `hepgraph/` change and was
  not made here.
* The validator's `area` formula (`geo._ring_area_m2`, longitude-latitude Chamberlain
  formula) is only exact for short edges near a pole: a 13-vertex hull of the IceCube strings
  measured 2.3% too large until each edge was subdivided to 10 m or less.
* Checks the validator can execute are length, area, distance, azimuth and span. Station
  counts and spacings cannot be written as `checks[]`; they are measured in this worklog and
  quoted in the record `method`/`notes` against the official figure.
* Downloaded files lived in the session scratch directory only (nothing under `data/` except
  records; no source file was copied into the repository).

## 1. Amundsen-Scott South Pole Station (IceCube, DeepCore, IceTop)

Grade: **marker only -> layout to scale** (86 in-ice strings, 162 IceTop tanks, array footprint with
an area check; ARA, AMANDA, IceCube Upgrade and Gen2 stay unlocated).

### Why it was unblocked

The earlier worklog (`GEOMETRY_polar-sea.md` conflict 1) concluded that no fetchable source
states how IceCube's (x, y) axes relate to true north, because `docs.icecube.aq` returns HTTP 401
(still true on 2026-10-25). Version 3 (6 Feb 2024) of the IceCube instrumentation paper
(arXiv:1612.05093, section 5.3 "Geometry Measurement", pp. 44-45) does state it:

> "The IceCube coordinate system origin is located at 46500’E, 52200’N, at an elevation of 2900 ft (883.9 m)."
>
> "aligned with the Prime Meridian (Grid North), pointing toward Greenwich, UK."

with the x-axis 90 degrees clockwise from y (Grid East), z up. The paper itself says nothing about where
that origin is in latitude and longitude (the grid moves with the ice). The anchor is the IceCube
Collaboration's own software repository: `icecube/i3astropy`, `src/i3astropy/__init__.py` line 25,
commit `60eb2fa41f97738d9855209720a994c19ed9b92f`: "This is the nominal location of the center of the
IceCube detector", `i3location = EarthLocation(lat=-89.9944 * deg, lon=-62.6081 * deg, height=883.9 * m)`.
The height equals the elevation of the frame origin, and the centre of the 86-string hull is within a few
metres of (0, 0), so the point is taken as the origin.

### Computation (recorded as `derived` with this method in every record)

1. Strings: `GeoCalibDetectorStatus_IC86_Merged.txt` in the IceCube repository `icecube/toise`
   (commit `a33aff4b279bbb78d5e628f1cc754481e87c3408`, 5160 rows `string DOM x y z`, metres). Every string
   is vertical (all 60 DOMs share one x, y; string 21 varies by 0.33 m); the string position is the mean.
2. Origin in a South Pole azimuthal-equidistant plane: distance from the pole = colatitude x 6 371 008.8 m
   = 622.69 m, bearing = the longitude (62.6081 W) -> (E0, N0) = (-552.88, +286.48) m, with the 0 degree
   meridian as +N and 90 E as +E (the same plane the browser draws for a polar map).
3. A string at (x, y) is the point (E0 + x, N0 + y); the inverse projection gives lat/lon.
4. Orientation was confirmed independently against a published figure: Figure 21 (PDF page 17) of the review
   "Cosmic-Ray Physics at the South Pole" (Soldin, Evenson, Kolanoski, Watson, arXiv:2311.14474) plots all 86 string numbers against "grid
   easting (m)" and "grid northing (m)". A least-squares fit of the 86 label positions to the toise
   table gives a pure scale (0.155 pt/m, no rotation, no flip) with 0.8 pt (about 5 m) rms residual.
5. IceTop tanks: the toise file holds in-ice DOMs only, so the tank positions come from the GraphNeT
   table `icecube86.parquet` (`graphnet-team/graphnet`, commit `2e17d473f1b81eb5ee29a7b273eb61d0e70d5e1a`),
   whose in-ice rows equal the toise file to 2e-5 m and whose `dom_number` 61-64 are the four IceTop DOMs of each
   station (61, 62 = tank A; 63, 64 = tank B). It is a secondary copy (source type `secondary`), so the tank shapes stay
   `derived`. It agrees with the IceTop paper (arXiv:1207.6326) over all 81 stations: tank pairs median 9.82 m apart
   ("10 m apart"); pair midpoint a median 24.5 m from the hole ("placed nominally 25 m from the top of
   the corresponding in-ice hole"); lowest tank top z = 1944.54 m (tank 18A) and highest 1950.08 m (tank 74A), exactly as
   the paper states; the two DOMs of a tank 0.58 m apart (Table 3); 81 stations, 162 tanks.

### Inventory

| Entity | Drawn / unlocated | Record | Representation | accuracy_m | Check |
| --- | --- | --- | --- | ---: | --- |
| site:south-pole-icecube | drawn (existing OSM marker) | geometry:south-pole-station-marker | georeferenced | 300 | none (unchanged) |
| detector:icecube (strings 1-78) | drawn | geometry:icecube-strings-1-78 | derived | 500 (relative about 1) | median nearest-neighbour spacing 124.3 m vs official 125 m grid (worklog only) |
| detector:icecube-deepcore (strings 79-86) | drawn | geometry:icecube-deepcore-strings-79-86 | derived | 500 | Delaunay edges under 110 m between the 15 DeepCore strings span 40.9-104.9 m vs official 41-105 m; median of all 36 edges 71.8 m vs 72 m (worklog only) |
| detector:icecube (array outline) | drawn | geometry:icecube-array-footprint | derived | 500 | area 0.868 km2 vs nominal 1 km2 (one cubic kilometre over 1000 m), tolerance 15%: pass, weak |
| detector:icetop (162 tanks) | drawn | geometry:icetop-tanks-stations-01-27, -28-54, -55-81 | derived | 500 | spacing, offset and z agreement with the IceTop paper (worklog only) |
| site:south-pole-ara / detector:ara | unlocated | n/a | n/a | n/a | no as-built coordinates found |
| experiment:amanda | unlocated | n/a | n/a | n/a | no coordinates found |
| experiment:icecube-upgrade | unlocated | n/a | n/a | n/a | design layout only as images; five as-built strings not tabulated |
| experiment:icecube-gen2 | unlocated | n/a | n/a | n/a | proposed |

### Source conflicts

* **Orientation:** the earlier worklog said no source gives it; v3 of the JINST paper does (older arXiv versions
  did not carry the paragraph, or it was not read). Chosen: v3.
* **Absolute position of the array:** i3astropy `i3location` (89.9944 S, 62.6081 W) versus the Wikipedia/Wikidata point
  for IceCube (89.99 S, 63.4531 W), which OpenStreetMap node 5249487917 ("IceCube Neutrino Observatory", Overpass
  2026-10-25T10:37:51Z) copies. They are 489.4 m apart. Chosen: i3astropy (collaboration code, height equals the
  frame origin elevation; the Wikipedia point is rounded to 1 arcsecond of latitude and has no stated meaning).
  Because the true difference is of the order of the array size, and the ice drifts about 10 m a year (NSF, quoted
  on `site:south-pole-icecube`), `accuracy_m` is **500** for the whole pattern, while the pattern's own shape, scale
  and orientation are good to about 1 m.
* **Footprint size:** the paper gives a nominal "one cubic kilometer"; the hull of the 78 deployed strings is
  0.868 km2 (the full 91-site hexagon would be 1.015 km2), hence the 15% tolerance.

### Site coordinate corrections

```json
[
  {
    "site_id": "site:south-pole-icecube",
    "current": {"lat": -90.0, "lon": 0.0, "precision_m": 2000, "kind": "detector"},
    "proposed": {"lat": -89.9944, "lon": -62.6081, "precision_m": 500, "kind": "detector"},
    "source": "src:geo-arrays-icecube-i3astropy-location",
    "locator": "icecube/i3astropy src/i3astropy/__init__.py line 25 (commit 60eb2fa41f97738d9855209720a994c19ed9b92f)",
    "quote": "This is the nominal location of the center of the IceCube detector",
    "note": "Nominal, of unstated epoch; the array moves about 10 m a year relative to geographic coordinates. A competing point (89.99 S, 63.4531 W, Wikipedia/OSM) is 489 m away."
  }
]
```

### Backlog

* ARA stations A1-A5: a table of as-built coordinates in the South Pole grid (not found; a testbed offset of
  "approximately 1.8 km grid East of the IceCube detector" is the only number).
* AMANDA-II string coordinates; IceCube Upgrade as-built strings (IC93 geometry); IceCube-Gen2 sited layout.
* A dated, surveyed geographic position for one IceCube-fixed point (the IceCube Laboratory, or the surface
  cable origin), which would cut the 500 m absolute uncertainty to metres; `docs.icecube.aq` "Coordinate
  Systems" (HTTP 401) would be the place.
* IceCube Laboratory building footprint (not in OpenStreetMap on 2026-10-25).

## 2. Pierre Auger Observatory (Malargue)

Grade: **partial (two hulls) -> layout to scale** (every active surface-detector station drawn at its published
position, 1636 stations; the two array outlines kept with an area check). Fluorescence buildings not placed.

### What was done

* Re-fetched `https://opendata.auger.org/releases/3/auxiliary/sdMap.csv` (release 3, 20 March 2024, DOI
  10.5281/zenodo.10488964; 1689 stations, columns id, northing, easting, altitude, start, stop, sd1500, sd750). The data
  page (`/data.php`) says: "stop: GPS time of the last event detected by the station. The value is 1 if the station is
  still in operation". Licence (home page): "The Open Data are released under the (CC BY-SA 4.0) International
  License." Records derived from it therefore carry `license: CC-BY-SA-4.0` with the DOI attribution (the build prints it
  under the map). The two hull records from the previous pass had `license: null` and were updated.
* Only stations with stop = 1 are drawn: 1587 flagged sd1500 (including the 22 that are also sd750) in 20 north-to-south
  bands of 79 or 80 (`geometry:auger-sd1500-stations-band-01` .. `-20`) and 49 infill-only stations
  (`geometry:auger-sd750-infill-stations`). 53 stations with a recorded stop time are left out.
* Each station is a 3.6 m square marker, 3.6 m being the tank diameter in the Observatory paper
  (arXiv:1502.01323 section 3.1: "A surface detector station consists of a 3.6 m diameter water tank").
* `geometry:auger-sd1500-array-boundary` was rebuilt as the hull of the 1587 active stations (31 vertices, 3097.6 km2;
  the previous version used every station ever flagged, 3158 km2) with its area check retightened from 8% to 5%.

### Assumption that is not in the source

The data page says "UTC" (sic) coordinates and states no zone or datum. They are read as UTM zone 19 south on WGS 84
(EPSG:32719, `pyproj`), because only zone 19 puts the numbers at Malargue and GPS surveys are WGS 84. If the
Collaboration used another datum the whole array shifts; `accuracy_m` is 50 and confidence `approximate` for that
reason. The converted extent (34.93-35.52 S, 68.91-69.66 W) agrees with the previous pass's independent conversion.

### Inventory

| Entity | Drawn / unlocated | Record | Representation | accuracy_m | Check |
| --- | --- | --- | --- | ---: | --- |
| detector:pierre-auger-observatory (1587 main-array stations) | drawn | geometry:auger-sd1500-stations-band-01 .. -20 | surveyed | 50 | median nearest-neighbour 1489.5 m vs official 1500 m triangular grid (worklog only) |
| same, infill-only stations (49) | drawn | geometry:auger-sd750-infill-stations | surveyed | 50 | median nearest-neighbour of the 71 sd750 stations 742.7 m vs official 750 m (worklog only) |
| site:malargue-auger (array outline) | drawn | geometry:auger-sd1500-array-boundary | derived | 50 | area 3097.6 km2 vs 3000 km2 (+3.25%, tol 5%): pass |
| experiment:pierre-auger-observatory (infill outline) | drawn | geometry:auger-sd750-infill-boundary | derived | 50 | none asserted (29.3 km2 vs "23.5 km2, 61-detector", see conflict 3) |
| Fluorescence detectors Los Leones, Los Morados, Loma Amarilla, Coihueco | not drawn | not atlas entities (no site records) | n/a | n/a | n/a |
| 53 stations with a stop time | not drawn | n/a | n/a | n/a | n/a |

Station altitudes in the table run 1344 m to 1619 m against the paper's "detectors located at altitudes between 1340 m and 1610 m".

### Source conflicts

1. **Station count.** The paper says "Currently more than 1660 surface detector stations are operational" (section 3.6, 2015); the
   release (2024) marks 1636 stations in operation (1565 main + 49 infill + 22 both) and lists 1689 stations in all. Not
   reconcilable from fetched sources (stations lost, retired, or the flag lags); the drawn set is the release's own.
2. **Latitude and longitude of the array.** The paper says the array lies "between latitudes 35.0 and 35.3 S and between longitudes
   69.0 and 69.4 W"; the stations span 34.93-35.52 S and 68.91-69.66 W. The sentence is rough; the table was used.
3. **Infill size.** The abstract says "a 23.5 km2, 61-detector infilled array with 750 m spacing"; 71 stations carry sd750 = 1 and their hull
   is 29.3 km2 (the 49 infill-only stations alone: 25.8 km2). No check is asserted.
4. **Licence.** The CC BY-SA 4.0 share-alike clause applies to the derived coordinates; the integrator should confirm the
   repository's data licence note (`data/atlas/geometry/LICENSE.md` currently speaks only of OSM-derived records).

### Site coordinate corrections

None (`site:malargue-auger` is the Observatory's address in the town, already documented as not the array).

### Backlog

* Coordinates of the four fluorescence buildings (Los Leones, Los Morados, Loma Amarilla, Coihueco), the CLF and XLF: none in the papers
  fetched (arXiv:0907.4282, 1502.01323, 1604.03637, 2007.09035, 1011.6523), none in Open Data (`fdPixelMap.csv` is pointing only).
  Overpass has communication-tower nodes operated by the Observatory at (-35.496078, -69.4498211) on Cerro Los Leones and
  (-35.1143142, -69.6000234), but no building footprints. Needs an Auger GAP note, the Offline detector configuration, or a mapped footprint.
* An explicit statement of the UTM zone and datum of `sdMap.csv`.
* AERA radio antennas, HEAT, AMIGA unitary cell and AugerPrime surface scintillator positions; stopped stations with their date windows.
