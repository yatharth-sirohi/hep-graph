# Release geometry stream arrays-a (2026-10-25)

Worktree `HEP-Graph-ar-arrays`, branch `atlas-release-arrays`. New sources are prefixed
`src:geo-arrays-*`. Facilities: Amundsen-Scott South Pole Station (IceCube, IceTop),
Pierre Auger Observatory, Telescope Array (Utah), LHAASO (Daocheng), Baikal-GVD.
Previous worklogs: `GEOMETRY_arrays.md`, `GEOMETRY_polar-sea.md`.

## Result at a glance

| Facility | Grade before | Grade after | New features | Principal check |
| --- | --- | --- | --- | --- |
| Amundsen-Scott South Pole (IceCube, DeepCore, IceTop) | marker only | layout to scale | 78 + 8 strings, 162 tanks (6 records), array footprint | footprint 0.868 km2 vs nominal 1 km2 (weak); spacing/tank checks in the record notes |
| Pierre Auger Observatory | partial | layout to scale | 1636 stations (21 records), main array outline rebuilt | outline 3098 km2 vs 3000 km2 (+3.25%) |
| Telescope Array (Utah) | partial | layout to scale | 507 stations (7 records), outline, CLF, 3 FD stations | outline 691.5 km2 vs ~700 km2; FD 20.8 km vs "about 21 km" |
| LHAASO (Daocheng) | partial | layout to scale | 1188 MDs (15 records), 3 WCDA pools, ED-array outline | 4911/305 ED split, 635 m radius, pool areas, outline span 1270 m |
| Baikal-GVD | partial | layout to scale (relative); 1500 m absolute | 11 clusters, 88 strings, with deployment years | cluster chord 117-120 m vs 117 m (R = 60 m heptagon) |

Changes in data/atlas: 69 geometry records and 14 sources added; the two Auger outlines updated; 5 maps edited; 2 geometry records removed (superseded):
`ta-array-point`, `baikal-gvd-cluster-footprint`; ED markers of LHAASO not drawn (2 MB bundle limit). The geometry LICENSE note gained a paragraph on the non-OSM licences.

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

* **Orientation:** the earlier worklog said no source gives it; v3 of the JINST paper does (the earlier read was probably of
  an earlier arXiv version; this was not checked). Chosen: v3.
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

## 3. Telescope Array (Utah)

Grade: **partial (one 6 km point) -> layout to scale** (507 stations on their grid, array outline with area
check, central laser, three fluorescence stations with distance checks). TAx4 not drawn.

### Sources and what was verified here

* **Station table.** TA Collaboration data release on Zenodo, DOI 10.5281/zenodo.8405760 ("Data of an extremely energetic cosmic ray
  observed by a surface detector array of Telescope Array experiment", T. Fujii, 2023-10-04, "Shared by the Telescope Array
  Collaboration"), licence cc-by-4.0 per the Zenodo API. Re-fetched: `Data_Release_TASD.zip` (800 716 bytes, md5
  15ebbb190709ddfb724ced94de8670f2), `1_event_display/TASDPosition.dat` = 507 rows `id x y z` in km; the release's `00memo` says only
  "TASDPosition.dat : The position information of TA SD". No origin, orientation or units are stated (units km per the
  event-display code in the same release).
* **Frame, by registration (this work).** Fig. 5 of arXiv:2103.01086 ("Surface detectors of the TAx4 experiment", NIM A 1019
  (2021) 165726) is a vector plot on latitude and longitude axes with 507 red markers for the TA SDs. A first agent read the 507 markers
  from the vector graphic; I re-ran the extraction and fit from a freshly fetched copy and reproduced every number: axis calibration residual 1.4e-5 deg
  (lon) and 1.1e-4 deg (lat), all 507 matched one-to-one, rotation -0.0012 deg, scale 1.00038, the CLF at table (0.006, 0.005) km,
  residuals after a 6 m mean shift median 14 m, 90th percentile 26 m, 99th percentile 40 m. Origin = the CLF, 39.296918 N 112.908733 W (arXiv:1410.3151
  section 5.1, verified in a fresh copy: "Surface Impact Position: Uniform, random distribution inside a circle of radius 25 km, centered at the CLF
  (39.296918 N Lat, 112.908733 W Long)"). Axes are true east and north (a UTM 12 grid would be rotated about 1.2 deg).
* **Three stations disagree with the figure** by 443 m (1806), 142 m (2212) and 133 m (1713). In the table 1806 and 2212 are 1.20 km from their grid
  neighbours while the figure positions would break the square grid; the table is used and the figure is blamed.
* **Projection choice matters at the 60 m level.** An ellipsoidal azimuthal-equidistant projection about the CLF (equal to a tangent-plane ENU within 1 m at
  25 km) fits the figure; a spherical equirectangular conversion would differ by up to 60 m at the corners. `accuracy_m` is 100 for the stations.
* **Fluorescence stations are figure readings.** No document fetched gives their coordinates. Fig. 1 of arXiv:1410.3151 is a to-scale layout
  (507 squares, 3 triangles, a circle for the CLF); its 505 drawn squares register one-to-one onto the table (scale 4.777 pt/km east-west,
  4.867 pt/km north-south, rms 0.27 pt, stations 1327 and 1428 not drawn). The triangle bounding-box centres give (x, y) km from the CLF
  of Middle Drum (-7.034, 19.621), Black Rock Mesa (17.037, -11.989), Long Ridge (-18.386, -9.806): 20.84, 20.83 and 20.84 km from the CLF, matching "equidistant" and the official "about 21 km"
  (arXiv:1801.09784 section 2, verified in a fresh copy). Using the triangle centroid instead would move each marker 0.3 km and spoil the equidistance, so the box centre is used.
  `accuracy_m` 500, `derived`.

### Inventory

| Entity | Drawn / unlocated | Record | Representation | accuracy_m | Check |
| --- | --- | --- | --- | ---: | --- |
| detector:telescope-array (507 SD stations) | drawn | geometry:ta-sd-stations-strip-01 .. -07 | derived | 100 | 507 stations (official 507), median nearest-neighbour 1.197 km vs 1.2 km grid (worklog only) |
| site:telescope-array-utah-central-site (array outline) | drawn | geometry:ta-sd-array-boundary | derived | 100 | area 691.5 km2 vs ~700 km2 (-1.2%, tol 5%): pass |
| Central Laser Facility | drawn | geometry:ta-clf | surveyed (published lat/lon) | 20 | rounded 39.30 N 112.91 W in arXiv:2103.01086 agrees |
| Black Rock Mesa, Long Ridge, Middle Drum FD stations | drawn | geometry:ta-fd-black-rock-mesa, -long-ridge, -middle-drum | derived (figure reading) | 500 | distance to the CLF 20.81, 20.81, 20.87 km vs "about 21 km" (tol 3%): pass |
| TAx4 (500 stations, 2.08 km) | not drawn | n/a | n/a | n/a | positions only in a figure |
| geometry:ta-array-point (6 km marker) | removed | superseded | n/a | n/a | n/a |

### Source conflicts

1. **Array area:** "approximately 700 km2" (arXiv:1201.4964 section 3, most papers) versus "about 730 km2" (arXiv:1110.0133, = 507 x 1.2 x 1.2). The hull is 691.5 km2. 700 is used.
2. **FD-FD separation:** "~35 km" (arXiv:1201.0002 Fig. 1 caption), "about 30 km" (arXiv:1801.09784); the figure readings give 31.5 to 39.7 km. Not used as a check.
3. **Middle Drum to the array:** arXiv:1801.09784 says the three FD are 3 km (Black Rock), 4 km (Long Ridge), 8 km (Middle Drum) from the SD border; the figure readings give 3.5, 4.9, 9.9 km to the nearest station centre. Middle Drum is about 1.3 km further than stated (mild mismatch, within the figure-reading slack plus the border definition).
4. **Frame origin:** inferred (registration), not stated by the release.
5. **Licence:** CC BY 4.0 requires attribution; carried in each record's `license` and shown under the map.

### Site coordinate corrections

```json
[
  {
    "site_id": "site:telescope-array-utah-central-site",
    "current": {"lat": 39.3, "lon": -112.9, "precision_m": 6000, "kind": "detector"},
    "proposed": {"lat": 39.296918, "lon": -112.908733, "precision_m": 100, "kind": "detector"},
    "source": "src:geo-arrays-ta-hybrid-spectrum-2014",
    "locator": "arXiv:1410.3151 section 5.1, MC thrown-event parameters, Surface Impact Position",
    "quote": "Surface Impact Position: Uniform, random distribution inside a circle of radius 25 km, centered at the CLF (39.296918 N Lat, 112.908733 W Long).",
    "note": "The CLF, which the papers call the centre of the SD array and equidistant from the three telescope stations. The centroid of the 507 stations is 4.0 km south of it (x +0.45 km, y -3.97 km from the CLF)."
  }
]
```

### Backlog

* Official latitude and longitude of Black Rock Mesa, Long Ridge and Middle Drum (a TA document). A research sub-agent reported that `telescopearray.org` redirected (HTTP 301) to a
  dynamic-DNS host, which it did not follow, and that the Rutgers (Ivanov) and Utah (Mallen) theses linked from older papers returned 404 (not re-checked here).
* A statement of the origin and orientation of the `TASDPosition.dat` frame, and its z datum (the sub-agent found the z column 12-16 m above the raw event dump's `POS` z; not re-checked; z is unused here).
* TAx4 station coordinates (only a figure) and the TALE infill; communication towers.

## 4. LHAASO (Daocheng)

Grade: **partial (one point) -> layout to scale** (1188 muon detectors, the three WCDA pools, the ED-array outline, all with
checks against stated dimensions). The 5216 individual EDs and the 18 WFCTA telescopes are not drawn.

### Sources and what was verified here

* **Coordinate.** LHAASO Science Book 2021 edition, chapter 1 (Chin. Phys. C 46, 030001 (2022), DOI 10.1088/1674-1137/ac3fa6; arXiv:1905.02773 v4,
  CC BY 3.0). Re-downloaded the 183-page PDF (54 MB) and read the abstract: "located at Mt. Haizi (4410 m a.s.l., 600 g/cm2, 29° 21’ 27.56” N, 100° 08’ 19.66” E) in Daocheng, Sichuan province".
  This is the coordinate already on `site:lhaaso-haizi-mountain` and the map (QA pass of 2026-09-21). The previous worklog's statement that
  the Science Book "remains unfetchable" is out of date: `curl` of the arXiv PDF followed by `pdftotext` works.
* **Layout.** Fig. 1 of the Science Book (PDF page 8) is a vector graphic with 5216 red squares (EDs), 1188 blue circles (MDs), three teal pools, a NORTH arrow pointing up and a 150 m scale bar.
  A research sub-agent extracted it; I redid the extraction independently from a fresh copy: (a) the same figure in the right panel of Fig. 1 of arXiv:2401.01038 (CC BY 4.0; 5216 red squares, 1188 blue circles, X (m)/Y (m)
  axes read from tick labels at 0.1248 pt/m east-west, 0.1206 pt/m north-south) and (b) a similarity registration of the Science Book figure onto it: 5215 of 5216 EDs within 2 m (median 0.16 m), scale 4.33 m per point, rotation 0.
  The two papers share one coordinate list.
* **Origin and scale checks that the text can test** (all pass with an origin at the mean of circle fits to the outer ED ring, the 575 m ED boundary and the outer MD ring):
  4911 EDs inside 575 m and 305 outside ("4911 EDs with 15 m spacing in a circle area with radius of 575 m, and the guarding ring array consisting of 305 EDs"); farthest ED 635.2 m ("outer radius of 635 m");
  pools measure 150.1 m x 150.1 m, 150.1 m x 150.1 m and 300.2 m x 110.1 m ("The pool 1 and 2 are both 150 m × 150 m. Pool 3 is 300 m × 110 m."), total 78,109 m2 ("78,000 m2"); the ED hull spans 1270.2 m (2 x 635 m).
* **Independent position check (OpenStreetMap).** Overpass (lz4 mirror, extract 2026-10-25T11:28:50Z) has the three pools as traced polygons (ways 1046559931, 1046559932, 1046559933, "Water Cherenkov Detector Array #3, #1, #2"). Their corners lie 1 to 3 m east and 2 to 10 m north of the placement here, with a
  best-fit rotation of about -0.9 deg (a rough trace). OSM way 1003419124 ("Kilometer-Square Array (LHAASO)") is a regular 38-gon of radius 619.8 m centred 2 m from the quoted coordinate: a drawn circle, not a trace, so it is not evidence. No OSM geometry is used in any record, and no record cites an OSM source.
* **Frame.** Origin = array centre placed at the quoted coordinate; x east, y north (NORTH arrow). The quoted coordinate is not defined in the source as the array centre; the pools versus OSM and the 164 m shift to the 2016 coordinate give `accuracy_m` 30.

### Why the EDs are not drawn

5216 EDs as 1 m markers are 26 000 vertices; the map bundle came to 3.55 MB and the build refuses bundles over 2 MB (`geometry/lhaaso-daocheng.json is 3548567 bytes, over the 2000000 byte limit`). The 1188 MDs as 6 m markers (the 36 m2 each has in the Science Book) fit
(bundle 0.68 MB). The ED array is represented by its outline (hull of the 45 vertices) with area and span checks. Allowing `MultiPoint` in `geo.GEOJSON_TYPES` (the browser already draws it) would let all 6404 detectors be two records.

### Inventory

| Entity | Drawn / unlocated | Record | Representation | accuracy_m | Check |
| --- | --- | --- | --- | ---: | --- |
| KM2A muon detectors (1188) | drawn | geometry:lhaaso-km2a-mds-block-01 .. -15 (k-d blocks, west to east) | derived | 30 | 1188 MDs (stated 1188); median nearest-neighbour 27.3 m vs 30 m (worklog only) |
| KM2A ED array (5216 EDs) | outline only | geometry:lhaaso-km2a-array-outline | derived | 30 | area 1.242 km2 vs 1.3 km2 (-4.4%, tol 5%) and span 1270.2 m vs 1270 m (tol 2%): pass |
| WCDA pools 1, 2, 3 | drawn | geometry:lhaaso-wcda-pool-1, -2, -3 | derived | 30 | area 22 559 m2 vs 22 500, 22 559 vs 22 500, 33 090 vs 33 000 m2 (tol 3%): pass |
| WFCTA (18 telescopes) | not drawn | n/a | n/a | n/a | text and figure disagree on the position |
| site:lhaaso-haizi-mountain anchor | drawn (existing) | geometry:lhaaso-array-point | surveyed | 50 | unchanged |

### Source conflicts

1. **Coordinate:** 29°21’27.56” N, 100°08’19.66” E (Science Book 2021 and, to 0.1”, the WCDA paper arXiv:2101.03508: 29°21’27.6”, 100°08’19.6”) versus 29°21’31” N, 100°08’15” E in the 2016 and 2018 papers (arXiv:1602.07600, arXiv:1802.04773; a pre-construction value, 164 m away) versus "100.01 E, 29.35 N" in arXiv:2010.06205 and arXiv:2401.01038 (about 12.5 km west; a typo copied between the two). The 2021 value is used.
2. **Counts:** ED totals 5195 (arXiv:2010.06205, arXiv:2101.03508, planning) versus 5216 (Science Book, arXiv:2401.01038, arXiv:2405.11826; 5216 is used and matches the figure); "1171 tanks" appears once in the Science Book against 1188; 4911+305 = 5216.
3. **Where the telescopes are:** Science Book section III.C: "The telescopes were installed at the southwest corner of the first pool"; the figure puts the WFCTA cluster at the junction of pools 1 and 2. Not drawn.
4. **Pool gaps:** text 2 m (pools 1-2) and 5 m (to pool 3); the figure shows about 3 m and 6 m. Immaterial at the 30 m accuracy.
5. **Area of the site:** 1.35 km2 (Science Book) versus 1.36 km2 (IHEP "Site" page). Not used.
6. **Design or as built:** not stated; the plotted EDs have a median nearest-neighbour distance of 13.6 m against a stated 15 m spacing (5th to 95th percentile 8.7 to 16.7 m), so the plot is not an ideal lattice.
7. **Licence:** CC BY 3.0 (Science Book). The records carry the DOI attribution; arXiv:2401.01038 is CC BY 4.0 (used for cross-checking only).

### Site coordinate corrections

None (the integrator already moved `site:lhaaso-haizi-mountain` to the Science Book coordinate).

### Backlog

* The 5216 ED markers (reproducible from the Science Book PDF page 8 with `pdftocairo -svg` and a similarity registration onto Fig. 1 of arXiv:2401.01038) once `MultiPoint` is allowed or the 2 MB bundle limit is raised.
* A statement of which point the quoted coordinate marks and whether the figure shows as-built positions; official WFCTA positions; WCDA cell positions (3120 cells of 5 m x 5 m, derivable but not drawn).

## 5. Baikal-GVD

Grade: **partial (one point and one assumed cluster circle) -> layout to scale for the relative arrangement** (eleven clusters, 88
strings, each with its deployment year), with the whole field's place on the lake known only to about 1500 m. This is the weakest of
the five records on absolute position and the integrator should weigh it accordingly.

### Sources and what was verified here

* **Site coordinate.** "located about 3.6 km offshore at 51° 46’N and 104° 24’E" (arXiv:2309.16310, ICRC 2023); the same 51° 46’ N, 104° 24’ E in arXiv:2011.09209, 2412.00164 ("3.6 km offshore and 1365 m deep") and 2507.01893 ("at about 4 km from the shore"; re-read in fresh copies of 2309.16310, 2412.00164 and 2507.01893).
  arXiv:1308.1833 (2013, early construction) says: "The geographical coordinates of the detector site are 51°50′N and 104°20′E" and places the site near the outfall of the Ivanovka river (re-read). The two are 8.7 km apart (7.4 km north-south, 4.6 km east-west). No document says what the point marks. 2020-2025 value used; the 2013 value recorded as a conflict.
* **Cluster layout.** Two published figures carry positions in metres and a north direction:
  Fig. 2 of arXiv:2108.00212 ("Positioning system for Baikal-GVD", ICRC 2021; "Reconstructed planar AM coordinates in GVD 2021. X is eastbound, Y is northbound.") plots the measured positions of the 8 strings of each of clusters 1-8 (and three instrumental strings), and Fig. 1 (right panel) of arXiv:2309.16310
  is a to-scale schematic top view for 2023 with a north arrow and a 0-100 m bar. A research sub-agent digitised both; I repeated the work from fresh copies: gridlines of the 2021 plot at 1.75 px/m (570, 920, 1270 px = X -400, -200, 0), 66 coloured markers detected (cluster 1 centre string (-19.7, -269.5) m, cluster 2 (-223.6, -392.9), cluster 8 (29.4, -693.1), the same values), and 97 green dots detected in the 2023 top view; a similarity registration of the
  schematic onto the measured plot matches 63 dots within 8 m (rms 3.1 m), scale 2.58 m per pixel. Clusters 1-11 each have 8 dots (one spurious detection, an inter-cluster string star, removed at cluster 5); the seven outer strings are 58-62 m from the central one (stated: "a regular heptagon with the radius of 60 m"); the widest chord of each cluster is 117.2-120.1 m
  as drawn (marker diagonals included) against 117.0 m expected for a regular heptagon of radius 60 m (check tolerance 4%).
* **Deployment years** read by me from the legend of Fig. 1 (left panel) of arXiv:2309.16310: 1: 2016, 2: 2017, 3: 2018, 4 and 5: 2019, 6 and 7: 2020, 8: 2021, 9 and 10: 2022, 11 and 12: 2023, 13: "Exp.". Used as each record's `valid.start`, so the timeline slider shows the field growing.
* Counts and later growth (verified in fresh copies): 96 strings and 3456 OMs in 2023 (arXiv:2309.16310); 14 clusters, 117 strings, 4212 OMs by April 2025 (arXiv:2507.01893); the JINR site (`baikal-gvd.jinr.ru/telescope`, re-fetched) says "16 независимых кластеров" and "более 4 896 оптических модулей" for 2026.

### Placement and why the accuracy is 1500 m

The frames of both figures have no stated origin and the coordinate is rounded to a minute (1.85 km in latitude, 1.15 km in longitude) and is not attached to a cluster. The centroid of the eleven central strings is placed on 51°46′ N, 104°24′ E in an azimuthal-equidistant projection with the figures' north up.
The pattern keeps its true size and orientation; `accuracy_m` is 1500 for its position. Representation `derived`, confidence `derived`.

### Inventory

| Entity | Drawn / unlocated | Record | Representation | accuracy_m | Check |
| --- | --- | --- | --- | ---: | --- |
| detector:baikal-gvd, clusters 1-11 (88 strings) | drawn | geometry:baikal-gvd-cluster-01 .. -11 | derived | 1500 (relative about 5) | span 117.2-120.1 m vs 117.0 m (regular heptagon, R = 60 m), tol 4%: pass |
| site:baikal-gvd-lake-baikal | drawn (existing) | geometry:baikal-gvd-site-point | surveyed | 2000 | unchanged |
| Clusters 12 and 13 | not drawn | n/a | n/a | n/a | incomplete in the top view (5 and 2-3 dots) |
| Clusters 14-16, inter-cluster and laser strings | not drawn | n/a | n/a | n/a | no top view with coordinates |
| Shore station | not drawn | n/a | n/a | n/a | no coordinate in any source |
| geometry:baikal-gvd-cluster-footprint (60 m circle at the site point) | removed | superseded | n/a | n/a | n/a |

### Source conflicts

1. **Site coordinate:** 51°46′N 104°24′E (2020-2025) versus 51°50′N 104°20′E (2013): 8.7 km apart; neither says what it marks. 2020-2025 used.
2. **Shore distance:** "about 3.6 km offshore" (2020-2024) versus "about 4 km from the shore" (2025) versus "beginning from about of three kilometers from the shore" (2013).
3. **Cluster spacing:** "approximately 300 m between the cluster centers" (2023), "reduced from 300 m to 250 m in 2022" and "250-300 m" (2025-2026); on the drawn layout the nearest-neighbour distance of a cluster centre is 201-266 m (eleven clusters), so the field is not a uniform lattice; the layout was not forced onto one.
4. **Optical-module depth range:** 750-1275 m (2023 figure axis and 2021 text: "between 750 and 1275 meters") versus the JINR page's "700 m" top and "1240 m" bottom module. Not used here (lakebed level depth unchanged at 1366 m).
5. **Number of clusters in 2023:** 12 implied by 96 strings (arXiv:2309.16310 text), 13 numbered in its figure (13 is "Exp."), 11 complete in the top view.
6. **Licence:** arXiv:2108.00212 and arXiv:2309.16310 are CC BY-NC-ND 4.0. Only positions (facts) were read from the figures; no image is copied. The integrator should confirm that is acceptable.

### Site coordinate corrections

None proposed: the published coordinate used is the one already on `site:baikal-gvd-lake-baikal`. (If the integrator wants the 2013 conflict noted on the site record: 51°50′N, 104°20′E, arXiv:1308.1833, "The geographical coordinates of the detector site are 51°50′N and 104°20′E".)

### Backlog

* A coordinate for any specific cluster or the shore station (cable landing near the Ivanovka river outfall): none in any document fetched; the JINR site names a "Береговая станция" without a position.
* The frame origin of the positioning-system coordinates (the Baikal-GVD positioning papers, or a geodetic reference point of the telescope).
* Top views for clusters 12-16 and the inter-cluster/laser strings (a 2025-2026 numeric layout); string positions measured after each season.

## Network use, limits and validation

* **Overpass** (one query at a time, at least 15 s apart, `User-Agent: HEP-Atlas-research/1.0 (...)`, small boxes, `[timeout:90]`): South Pole polar box (overpass-api.de, extract 2026-10-25T10:37:51Z); Auger names/towers/buildings (11:11:23Z); LHAASO area (two HTTP 502 from overpass-api.de, then the lz4 mirror answered, extract 11:27:51Z) and the pool/array ways with geometry (11:28:50Z); Baikal shore tags (11:42:02Z) and an `is_in` test (11:48:03Z; all six points fell in one large water area, so it proved nothing and was not used). Raw responses stayed in the scratch directory.
* **Web search budget.** The session's WebSearch budget (200 calls, shared by all agents) ran out during the Auger fluorescence-detector hunt, so no further searches could be made after that point; direct document fetches (arXiv, Zenodo, GitHub raw/API, project sites) were still possible and were used. No search engine was queried by other means.
* **INSPIRE** was not used. Three research sub-agents (Telescope Array, LHAASO, Baikal-GVD sources) ran read-only; their reports were treated as leads and every quote and number used above was re-fetched or recomputed here (see each section).
* `python -m hepgraph.atlas.validate`: 3 errors, all `status-not-derived-state` on `collaboration:mu3e`, `detector:mu3e`, `experiment:mu3e` (time-driven, pre-existing on the base branch, not touched), and the same 1588 warnings as the base branch: no warning is left on any file of this stream.
* `python -m hepgraph.atlas.build` succeeds; the largest bundles are `lhaaso-daocheng.json` 0.68 MB, `pierre-auger-observatory.json` 0.91 MB (budget 2 MB). Generated files were restored before each commit.
* `pytest -q`: 681 passed, 139 skipped (PostgreSQL-backed tests) at the last commit; `tests/test_atlas_geometry_data.py` executes every check written here against the real shapes.
* A browser pass on a local static server (build output, port 8761, stopped afterwards) opened #/map/amundsen-scott-south-pole-station, pierre-auger-observatory, telescope-array-utah, lhaaso-daocheng and baikal-deep-underwater-neutrino-telescope: all render; the South Pole map uses the polar projection with grid north up; on the LHAASO map the OpenStreetMap basemap shows the pools under the drawn pools.

## Integrator verification (2026-10-25)

Auger frame: converting the Los Leones FD origin used by opendata.auger.org's
own field-of-view drawing (E 459207, N 6071871) as UTM 19S / WGS 84 gives
35.495876 S, 69.449767 W, 23 m from OpenStreetMap node 1342506868 (Pierre Auger
Observatory communications tower, which the detector paper's Fig. 6 shows
directly behind the Los Leones FD building). OSM monitoring-station nodes
"Morriña" and "Tato" coincide with sdMap stations 321 and 440 to 0.1 m (likely
imported from the same data, so not independent). A PSAD56 reading would be
off by roughly 250 m. The WGS 84 assumption stands.
IceCube frame: the v3 instrumentation paper's "aligned with the Prime Meridian
(Grid North)" and the 883.9 m origin elevation were re-read in arXiv:1612.05093v3.
