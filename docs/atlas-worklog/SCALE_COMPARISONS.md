# Scale comparisons (M4): worklog

Stream `atlas-m4-scale`, 2026-10-26. Two features:

1. **Compare with…** on every local map (`static/atlas/js/localmap-compare.js`,
   `static/atlas/js/views/scale-geometry.js`): another facility's footprint laid over
   this map at true scale; `?cmp=<facility>&cmpc=<lat>,<lon>`.
2. **Detector line-up** (`#/view/detector-scale`, `static/atlas/js/views/detector-scale.js`,
   `scale-detectors.js`): detectors drawn at one linear scale beside a 1.8 m person, and
   IceCube at its own stated scale. Working title: "Detector line-up" (the owner names it).

## Data added

Every new value is a sourced `specs` quantity on a detector record, with a verbatim quote
fetched on 2026-10-26 (`verified_at: "2026-10-26"`). New spec keys are ontology amendment
A31 (`docs/HEP_ATLAS_ONTOLOGY.md`) and are in `schema.SPEC_KEY_DIMENSIONS`, all `length`.
No new source record was needed: every source below already existed.

| detector | spec key | value | source | locator | quote (verbatim) |
| --- | --- | --- | --- | --- | --- |
| `detector:dune-far-detector-1` | `cryostat_width` | 15.1 m | https://arxiv.org/abs/2002.02967 (`src:dune-fd-tdr-vol-1`) | DUNE FD TDR Volume I, section 1.3.1 "Far Detector" | “Each LArTPC fits inside a cryostat of internal dimensions 15.1 m (w) × 14.0 m (h) × 62.0 m (l)” |
| `detector:dune-far-detector-1` | `cryostat_height` | 14.0 m | https://arxiv.org/abs/2002.02967 (`src:dune-fd-tdr-vol-1`) | DUNE FD TDR Volume I, section 1.3.1 "Far Detector" | “Each LArTPC fits inside a cryostat of internal dimensions 15.1 m (w) × 14.0 m (h) × 62.0 m (l)” |
| `detector:dune-far-detector-1` | `cryostat_length` | 62.0 m | https://arxiv.org/abs/2002.02967 (`src:dune-fd-tdr-vol-1`) | DUNE FD TDR Volume I, section 1.3.1 "Far Detector" | “Each LArTPC fits inside a cryostat of internal dimensions 15.1 m (w) × 14.0 m (h) × 62.0 m (l)” |
| `detector:katrin` | `main_spectrometer_length` | 23.23 m | https://arxiv.org/abs/2103.04755 (`src:geo-kit-katrin-design-paper`) | KATRIN design, construction and commissioning paper (arXiv:2103.04755), section 5.2.2 "Vacuum System of the Main Spectrometer" | “The vacuum vessel of the MS is 23.23 m long and has an inner diameter of 9.8 m.” |
| `detector:katrin` | `main_spectrometer_diameter` | 9.8 m | https://arxiv.org/abs/2103.04755 (`src:geo-kit-katrin-design-paper`) | KATRIN design, construction and commissioning paper (arXiv:2103.04755), section 5.2.2 "Vacuum System of the Main Spectrometer" | “The vacuum vessel of the MS is 23.23 m long and has an inner diameter of 9.8 m.” |
| `detector:juno` | `central_detector_diameter` | 35.4 m | https://arxiv.org/abs/2104.02565 (`src:juno-physics-detector-arxiv-2021`) | JUNO Physics and Detector (arXiv:2104.02565), section 3.2.1 "Central Detector scheme and requirements" | “The LS will be contained in a spherical Acrylic Vessel with an inner diameter of 35.4 m and a thickness of 120 mm.” |
| `detector:icecube` | `string_spacing` | 125 m | https://arxiv.org/abs/1612.05093 (`src:icecube-detector-paper-jinst-2017`) | IceCube instrumentation paper (arXiv:1612.05093), section 1.1.1 "IceCube In-Ice Array" | “The strings are deployed within a hexagonal footprint on a triangular grid with 125 m horizontal spacing, instrumenting a volume of one cubic kilometer of ice.” |
| `detector:super-kamiokande` | `inner_detector_diameter` | 33.8 m | https://www.phy.bnl.gov/~diwan/talks/talks/nusag-may-20/newwork/superk-NIM.pdf (`src:sk-nim-2003`) | Super-Kamiokande detector paper, NIM A 501 (2003) 418-462, section 4.1 "Tank, PMTs, and associated structures" | “The structure has inner dimensions 33.8 m (diameter) by 36.2 m (height), defining the ID which contains 32 ktons of water” |
| `detector:super-kamiokande` | `inner_detector_height` | 36.2 m | https://www.phy.bnl.gov/~diwan/talks/talks/nusag-may-20/newwork/superk-NIM.pdf (`src:sk-nim-2003`) | Super-Kamiokande detector paper, NIM A 501 (2003) 418-462, section 4.1 "Tank, PMTs, and associated structures" | “The structure has inner dimensions 33.8 m (diameter) by 36.2 m (height), defining the ID which contains 32 ktons of water” |
| `detector:nova-far-detector` | `width` | 15.5 m | https://arxiv.org/html/2512.20294 (`src:nova-arxiv-2025-monopole-search`) | NOvA monopole search (arXiv:2512.20294), detector description | “It is a segmented tracking calorimeter, of dimensions 15.5 m × 15.5 m × 59.8 m, with 896 planes of 384 PVC cells” |
| `detector:nova-far-detector` | `height` | 15.5 m | https://arxiv.org/html/2512.20294 (`src:nova-arxiv-2025-monopole-search`) | NOvA monopole search (arXiv:2512.20294), detector description | “It is a segmented tracking calorimeter, of dimensions 15.5 m × 15.5 m × 59.8 m, with 896 planes of 384 PVC cells” |
| `detector:lhcb` | `height` | 10 m | https://home.cern/science/experiments/lhcb (`src:lep-cern-lhcb-experiment-page`) | CERN LHCb experiment page, "LHCb" overview paragraph | “It is 21 metres long, 10 metres high and 13 metres wide, and sits 100 metres below ground near the town of Ferney-Voltaire, France.” |
| `detector:lhcb` | `width` | 13 m | https://home.cern/science/experiments/lhcb (`src:lep-cern-lhcb-experiment-page`) | CERN LHCb experiment page, "LHCb" overview paragraph | “It is 21 metres long, 10 metres high and 13 metres wide, and sits 100 metres below ground near the town of Ferney-Voltaire, France.” |

How each quote was obtained today: the KATRIN design paper (arXiv:2103.04755), JUNO Physics
and Detector (arXiv:2104.02565), the DUNE TDR Volume I (arXiv:2002.02967) and the IceCube
instrumentation paper (arXiv:1612.05093) were fetched as PDFs and searched for the number;
the NOvA paper from arXiv's HTML; the LHCb sentence from home.cern; the Super-Kamiokande
inner-detector sentence from the NIM A 501 paper (`src:sk-nim-2003`, the archived copy at
phy.bnl.gov that the source record names).

### Re-verified, unchanged values

* Super-Kamiokande `tank_diameter` 39.3 m and `tank_height` 41.4 m: the sentence "…a cylindrical
  stainless steel tank, which is 39.3 m in diameter and 41.4 m in height…" read today on the
  Wayback copy (2026-09-13) of the official detector page, because the live site is returning
  HTTP 503 ("Notice of Temporary Website Suspension"). `verified_at` and `locator` updated.
  The brief said "inner tank": the 39.3 × 41.4 m figure is the stainless-steel **tank**; the
  PMT-lined **inner detector** inside it is 33.8 × 36.2 m (NIM paper, added above). The line-up
  draws the tank and, dashed, the inner detector.
* ATLAS 46 m × 25 m, ALICE 26 m × 16 m, LZ's water shield 8 m × 6 m: the sentences still read
  the same on atlas.cern/Discover/Detector, home.cern/science/experiments/alice and
  lz.lbl.gov/laboratory/ today.
* CMS 21.6 m × 14.6 m (JINST 2008), MiniBooNE 12.2 m (arXiv:0806.4201), STAR TPC 4 m × 4.2 m
  (arXiv:nucl-ex/0301015): existing records, not re-fetched.
* Hyper-Kamiokande 68 m × 71 m and SNO's 12 m acrylic vessel: existing records; their sites
  (www-sk.icrr.u-tokyo.ac.jp, sno.phy.queensu.ca) could not be reached today (503 and no
  answer), so these were **not** re-verified.

### Conflicts

| claim | source A | source B | chosen | why |
| --- | --- | --- | --- | --- |
| ATLAS height | atlas.cern: "46m long, 25m in diameter" | home.cern: "46 m long, 25 m high and 25 m wide" | 25 m (diameter) | they agree; the record already says 25 m |
| LHC ring circumference (used to check the overlay) | CERN: 26 659 m | the OSM-traced ring record: 26 580 m measured | the record's shape, with CERN's figure shown beside it | the record's own 2 % check passes; the 0.3 % difference is the tunnel trace, listed on the page as "official figure" |

### Unresolved

* **IceCube footprint as a published figure.** The instrumentation paper says "a hexagonal
  footprint on a triangular grid with 125 m horizontal spacing, instrumenting a volume of one
  cubic kilometer", with no width or area, so no `footprint_*` spec was written. The line-up
  draws the footprint from the Atlas's own geometry record `geometry:icecube-array-footprint`
  (the hull of the 78 standard strings, 0.87 km², derived, ±500 m absolute, nominal 1 km² check
  passed at 15 % tolerance) and says so on the page.
* **ICARUS T600** "3.6 × 3.9 × 19.6 m³": the paper does not say which of 3.6 and 3.9 is the
  width and which the height, so the module is not in the line-up (it would need an unsourced
  assignment). Its `length` 19.6 m stays as it was.
* **DUNE far-detector module 2** (vertical drift) has no cryostat dimensions in its record; one
  module (horizontal drift) is drawn, as the brief asks.
* **Hyper-Kamiokande and SNO** not re-verified today (above).

### Candidates considered and excluded from the line-up

| detector | reason |
| --- | --- |
| ICARUS T600 | internal dimensions not labelled (above) |
| Muon g-2 ring | a 14.2 m **diameter** ring seen from above, not a side view; the line-up draws side views |
| Pierre Auger, Telescope Array, GRAND, ANITA, LHAASO, HAWC, IACT arrays | areas of 30 to 3000 km², tens of kilometres across: they are footprints and belong to the overlay, not a line-up of tens of metres |
| KM3NeT ARCA/ORCA, Baikal-GVD, ANTARES | instrumented volumes with no sourced footprint, and depths of a kilometre or more: like IceCube they need their own scale; IceCube is the one the brief names |
| NEWS-G (135 cm and 60 cm spheres), MiniBooNE-like small tanks | on the line-up's scale they are a pixel or two; NEWS-G is not sourced for a side view |
| DUNE near detector, MicroBooNE, SBND, ProtoDUNE | no length, width and height all sourced |

## Compare with…: decisions

* **Which footprint.** A facility's own map (`facility.map_id`). Rings, outlines and arrays
  (`ring`, `array`, `boundary`) with the linear structures that tie a campus together (`linac`,
  `tunnel`, `beamline`, `transfer_line`) when the map draws any; otherwise (underground
  laboratories, reactor sites) its halls, caverns and buildings. Positions with only an accuracy
  circle (`Point`) and inferred directions are never part of a footprint: they have no extent.
  Two records of one tunnel (LEP's and the LHC's have identical coordinates) are drawn once and
  named for both.
* **Method (also stated on the page).** Each vertex is described by its great-circle distance and
  initial bearing from the middle of the footprint's bounding box; the overlay puts it at that
  distance and bearing from the new centre, on the sphere R = 6371.0088 km. Distances from the
  centre are exact; distances between two points change by under 0.01 % at 30 km. The unit
  check moves the LHC ring over Iowa City, Svalbard and the South Pole and finds its length
  unchanged to about 1e-8 (the limit is 0.5 %). On a polar map "north" is the map's grid north.
* **Centre.** The view's centre at the moment of choosing (`cmpc`, rounded to 4 decimals, about
  11 m), or, for a link that names only `cmp`, the host map's recorded centre.
* **Location.** Only the click on "Over my location" calls `navigator.geolocation`. The position
  stays in a module variable: it is not in the address (`cmpc` is cleared), the history state,
  local or session storage or a cookie, and nothing is sent. The OpenStreetMap basemap is switched
  off while the overlay sits over the reader (its tile requests would say where they are) unless
  they turn it on, and the panel says so. The browser check asserts all of this.
* **No typed city.** A city box needs a gazetteer, and every coordinate in it would need a source
  and a quote; the only alternative is a network geocoder, which the brief rules out. So the
  control offers geolocation only.
* **Not offered on a polar map.** The South Pole maps use an azimuthal projection that is
  accurate only near the pole, so "over my location" would draw a distorted overlay thousands of
  kilometres from its centre; the button says why it is unavailable.
* **Overlay look.** Pink dashed lines (`--view-overlay`, a hue no map feature uses), no clicks,
  labelled "<facility>: overlay at true scale" at the top of the footprint, and a legend and
  method disclosure in the "Compare with…" section.

## The one server change, and why it is narrow

`hepgraph/server.py` sent `Permissions-Policy: camera=(), microphone=(), geolocation=()` on every
response. With `geolocation=()` the browser refuses `navigator.geolocation` outright ("Geolocation
access has been blocked because of a permissions policy"), found when the browser check clicked
"Over my location", so the feature cannot work without a change. The change:

* `geolocation=(self)` **only** for paths under `/atlas`; every other route (HEP Graph, the API)
  keeps `geolocation=()`. `camera` and `microphone` stay `()` everywhere.
* `(self)`, never `*` and never a third-party origin: the page's own origin may ask, and the browser
  still prompts the reader on each use. Frames cannot (`frame-ancestors 'none'` is unchanged).
* The Content-Security-Policy is untouched. Nothing is sent: the position is read in the page and
  kept in memory (the geolocation code never reaches `fetch`; `connect-src 'self'` still holds).
* `tests/test_atlas_server.py::test_geolocation_is_allowed_to_the_atlas_pages_only` pins both
  header values.
* The change only takes effect when the server is deployed; this stream deployed nothing.

## Detector line-up: decisions

* One linear scale for the 14 side views (px per metre, the same on both axes), packed tallest
  first into rows; every row has a ruler, grid lines every 10 m (or the next round step) and a
  1.8 m person. "Larger / Smaller / Fit to the page" change the scale for all shapes together.
* IceCube is a kilometre deep and cannot share that scale, so it has its own linear panel with a
  1 km bar; the line-up's detectors are drawn again there at the same scale to show how small
  they are. No log or broken axis is used, and the page says so.
* Shapes are simplified solids (cylinder on its end, cylinder on its side, sphere, box) seen
  from the side; the method says the real instruments are not these solids. The dimensions that
  are drawn are exactly the spec keys in `ROSTER` (`scale-detectors.js`); a detector whose
  record lacks one is listed as "Not drawn", never drawn from a guess.
* The status word under a name ("under construction", "no longer operating") follows the
  timeline year, from the record's `state_segments`.
* The method section lists every dimension with its value, source link, locator, confidence,
  and the quote, read from `provenance.json` and `sources.json` after the first paint.

## For the integrator

* `registry.js`: one entry (`detector-scale`) and one import line.
* `state.js`: `cmp` and `cmpc` (map routes only); `navigate()` drops them when the route's entity
  changes.
* `localmap.js`: a lazy `import('./localmap-compare.js')`, a "Compare with…" sidebar section, the
  overlay's points in `frameToFeatures`/`frameSignature`, and the basemap rule in `applyBasemap`.
* `panels.js`: a quiet link "See its size at true scale" on the detectors the line-up draws.
* `views.css`: `--view-overlay`, the overlay and `ds-*` rules (appended at the end).
* `hepgraph/server.py`: `Permissions-Policy` allows geolocation to `/atlas` only (see "The one
  server change"); it needs the integrator's deploy to take effect.
* `schema.py` and the ontology: spec keys of amendment A31 (the number may need to change at
  merge: A28 and A30 are already taken on other branches).

<!-- caller: code sections below -->
