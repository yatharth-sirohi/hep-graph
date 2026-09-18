# Geometry worklog: polar and deep-sea neutrino observatories

Researcher: geometry-polar-sea. Worktree `/Users/yatharthsirohi/Desktop/HEP-Graph-maps-polar`,
branch `hep-atlas-local-maps-polar`. New sources prefixed `src:geo-polar-*`.
Facilities covered: `facility:amundsen-scott-south-pole-station` (IceCube, DeepCore,
IceTop, ARA, AMANDA, IceCube Upgrade, IceCube-Gen2), `facility:km3net` (ARCA, ORCA),
`facility:baikal-deep-underwater-neutrino-telescope` (Baikal-GVD).

## Method note: Overpass access this session

Overpass (`overpass-api.de`, `lz4.overpass-api.de`) answered exactly **one** query
this session (the South Pole station-node search that produced
`geometry:south-pole-station-marker`), then refused every subsequent connection
outright -- `curl` exit 7 ("Failed to connect"/connection refused), not a
`429`/`504`, and this affected even `GET /api/status` on both mirrors. I backed
off repeatedly (20-25 s gaps, then background retry loops of 6-12 attempts at
15-25 s spacing, roughly 30+ minutes of the session in total) and both mirrors
stayed unreachable through the last check before finishing. This matches the
shared-load pattern `docs/atlas-worklog/GEOMETRY_cern.md` documents for the same
service. Net effect: I got the Amundsen-Scott South Pole Station's OSM point,
but a follow-up unrestricted building/`man_made` query (looking for the IceCube
Laboratory building or any other South Pole structure) never completed, and I
did not attempt separate queries for the KM3NeT shore towns or the Baikal shore
station because a sea/lake site has no OSM footprint of its own anyway (per the
research brief) and the only OSM-findable features left (onshore buildings) were
also blocked by the same outage. All backlogged below.

## Inventory

| Entity | Drawn? | Feature(s) | Representation | Accuracy | Check |
| --- | --- | --- | --- | --- | --- |
| facility:amundsen-scott-south-pole-station | map authored | -- | -- | -- | -- |
| site:south-pole-icecube | drawn | geometry:south-pole-station-marker | georeferenced (OSM node) | 300 m | none (reference point only) |
| site:south-pole-ara | **unlocated** | -- | -- | -- | -- |
| detector:icecube | **unlocated** | -- | -- | -- | -- |
| detector:icecube-deepcore | **unlocated** | -- | -- | -- | -- |
| detector:icetop | **unlocated** | -- | -- | -- | -- |
| detector:ara | **unlocated** | -- | -- | -- | -- |
| experiment:amanda | **unlocated** | -- | -- | -- | -- |
| experiment:icecube-upgrade | **unlocated** | -- | -- | -- | -- |
| experiment:icecube-gen2 | **unlocated** | -- | -- | -- | -- |
| facility:km3net (ARCA campus) | map authored | -- | -- | -- | -- |
| site:km3net-arca-capo-passero | drawn | geometry:km3net-arca-site-point | surveyed | 2000 m | none (point; corroborated by 2 independent sources) |
| detector:km3net-arca | drawn | geometry:km3net-arca-footprint | derived (LoI R=500 m) | 2000 m | none (tautological vs. own source, see below) |
| facility:km3net (ORCA campus) | map authored | -- | -- | -- | -- |
| site:km3net-orca-toulon | drawn | geometry:km3net-orca-site-point | surveyed | 2000 m | none (point; corroborated by 2 independent sources) |
| detector:km3net-orca | drawn | geometry:km3net-orca-footprint | derived (scaled from ARCA's R=500 m by string-spacing ratio) | 2000 m | none (own derivation, see below) |
| facility:baikal-deep-underwater-neutrino-telescope | map authored | -- | -- | -- | -- |
| site:baikal-gvd-lake-baikal | drawn | geometry:baikal-gvd-site-point | surveyed | 2000 m | none (point) |
| detector:baikal-gvd | drawn | geometry:baikal-gvd-cluster-footprint | derived (one cluster, 60 m radius per source) | 2000 m | none (tautological vs. own source, see below) |

7 geometry records total (1 South Pole marker + 2 ARCA features + 2 ORCA
features + 2 Baikal features; the map-authored rows above are not separate
geometry records). 4 maps: `map:amundsen-scott-south-pole-station`,
`map:km3net-arca`, `map:km3net-orca`, `map:baikal-deep-underwater-neutrino-telescope`.
8 entities unlocated, all at the South Pole (see below for the sourced reason on
each, also recorded verbatim in `map.unlocated[]`).

## Why no `checks[]` rows

Every drawn shape here is either (a) a bare `Point` reusing an already-sourced
coordinate, which has no length/area/span to independently cross-check, or (b)
a `derived` circle whose radius **is** the one sourced number being drawn
(the KM3NeT LoI's own `R=500 m` for ARCA, or the Baikal status paper's own
`60 m` string distance for one cluster). Adding a `checks[]` row that measures
the drawn circle's radius against the same figure it was drawn from would be
tautological -- draw exactly R, then "check" that R measures R -- not an
independent cross-check. `docs/atlas-worklog/GEOMETRY_cern.md` gives the same
reasoning for its TI12/TI18 derived points and I follow it here. Confidence
therefore stays `derived` (not `verified`) on all four circles, and `surveyed`
(not needing a check) on the three Points; none of this trips
`ring-without-length-check` because none of these features is a `ring`.

The one place I *did* look for an independent second figure and could not find
one: KM3NeT/ORCA's own footprint. See "Conflicts and honesty calls" below.

## Conflicts and honesty calls

1. **IceCube's 86-string array, IceTop and DeepCore are unlocated because the
   IceCube local coordinate system's true-north orientation could not be
   verified.** I fetched the IceCube detector paper (arXiv:1612.05093, full
   text via ar5iv) and the IceTop paper (arXiv:1207.6326, full text via ar5iv)
   directly: both describe the hexagonal 125 m string grid and the tank
   layout but neither states how the local (x,y) axes relate to true
   geographic north or the Prime Meridian. A `WebSearch` turned up secondary
   summaries claiming IceCube's own technical documentation
   (`docs.icecube.aq`, "Coordinate Systems") states grid north points toward
   Greenwich along the Prime Meridian, with a stated grid origin -- but that
   page returned **HTTP 401 Unauthorized** to every fetch attempt this
   session (`WebFetch` and a `curl` with a descriptive `User-Agent` both
   failed identically), so I could not read or quote it myself. I also tried
   the IceCube Preliminary Design Document PDF, the South Pole ice-transparency
   paper (arXiv:1301.5361) and the DeepCore paper (arXiv:1109.6096) looking for
   the same statement restated somewhere fetchable; none of them give it. Per
   the brief's "nothing from memory" standard, I did not georeference the
   array from a claim I could not independently verify, and left
   `detector:icecube`, `detector:icecube-deepcore` and `detector:icetop`
   unlocated with this reason. `experiment:amanda` and
   `experiment:icecube-upgrade` (both physically inside/adjacent to the same
   86-string footprint) and `experiment:icecube-gen2` (a proposed expansion
   around it) inherit the same gap and are unlocated for the same reason.
2. **ARA's five stations are unlocated for a related but distinct reason: no
   as-built positions, only a design concept.** The ARA overview paper
   (arXiv:2411.01761, fetched in full) states only "about 2 km from the
   IceCube Neutrino Observatory" with no map, spacing or per-station
   coordinates for A1-A5. The original ARA design paper (arXiv:1105.2854,
   fetched in full; new source `src:geo-polar-ara-design-2011`) describes the
   *baseline concept* of a future 37-station, 2 km hexagonal-grid array (only
   5 of the planned 37 were ever built) and separately states the 2011
   testbed sat "approximately 1.8 km grid East of the IceCube detector" -- a
   South Pole *grid* direction, which has the same unconvertible-to-true-north
   problem as IceCube's own coordinate system. I did not use a WebSearch
   synthesis claiming "ARA stations are on a hexagonal grid with 2 km
   spacing" as fact, because my own direct fetch of the primary ARA overview
   paper explicitly found no such per-station layout in that paper; I trust
   the direct fetch over the aggregation.
3. **ANTARES is out of `map:km3net-orca`'s scope, not merely skipped.**
   `site:antares-toulon` and `detector:antares` are real, well-sourced atlas
   records (ANTARES ran 2006-2022, ~10 km east of ORCA per the KM3NeT LoI),
   but `site:antares-toulon.facility_id` is `null` -- it does not belong to
   any atlas facility. Per the task brief's own framing ("ANTARES ... if it
   belongs to an atlas facility"), and per the contract's definition of
   `map.unlocated[]` as covering "entities of this facility", ANTARES is
   neither drawn nor unlocated on `map:km3net-orca`: it simply isn't part of
   `facility:km3net`'s inventory. I considered adding it as an informal
   context point anyway (its own coordinate is corroborated to ~11 km of
   ORCA's), but `site:antares-toulon.coordinates.precision_m` is 12000 m (an
   own-admitted "approximate", corroborated-not-published estimate, not a
   directly stated lat/lon), which is too coarse to place defensibly even as
   a rough marker. Documented as a backlog item on `map:km3net-orca.notes`
   instead of drawn.
4. **KM3NeT/ORCA's footprint circle is my own scaled estimate, not a sourced
   figure.** The Letter of Intent for KM3NeT 2.0 (arXiv:1601.07459, fetched
   in full via ar5iv) gives ARCA's building-block radius explicitly (Figure
   15 caption: "R=500 m, z=612 m"), but no fetched source gives the same
   number for ORCA. I tried three more papers directly (arXiv:2408.07015,
   arXiv:1701.05849, and km3net.org's "ARCA and ORCA detectors" page) hoping
   for an equivalent ORCA radius/diameter statement; all three give string
   spacing (~20 m for ORCA, ~90-100 m for ARCA) but never an overall
   footprint size. I derived `geometry:km3net-orca-footprint`'s radius
   (~105 m) by scaling ARCA's sourced 500 m by the ratio of the two arrays'
   sourced average string spacing (20:95, both quoted from the same LoI),
   on the stated assumption that both building blocks use the same 115-string
   layout pattern at different scale. This is explicit in the record's
   `method` and flagged `derived`/`confidence: derived`; a WebSearch synthesis
   independently suggested "~100 m radius, ~200 m diameter" for ORCA, which is
   consistent with my estimate, but I could not fetch and quote that claim
   from a primary source, so it is not cited anywhere in the data (see the
   record's `notes`).
5. **Baikal-GVD's full multi-cluster footprint is not drawn, only one
   cluster's.** The status paper (arXiv:2309.16310, fetched in full, twice,
   with different targeted prompts) directly states the per-cluster layout
   ("Seven peripheral strings are uniformly located at a 60 m distance around
   a central one") and the inter-cluster spacing ("~300 m... hexagonal
   pattern"), and separately states "3456 OMs attached to 96 vertical
   strings" -- 96/8 = 12 clusters by my own arithmetic on two numbers from the
   same paper, not an official cluster count stated in so many words. I did
   not draw a 12-cluster hexagonal-packing polygon for the whole array,
   because no source states that the as-deployed clusters actually fill a
   clean hexagonal packing (growth is described as ongoing and irregular
   year to year); doing so would assume a specific shape the source does not
   give. Only the single, directly-sourced 60 m-radius cluster circle is
   drawn, clearly labelled as one cluster, not the array.
6. **KM3NeT and Baikal shore stations: identified in prose, not drawn.**
   Portopalo di Capo Passero (ARCA's nearest town) is ~100 km from the ARCA
   site per the KM3NeT-It page and the LoI -- over the brief's 60 km context
   limit and the validator's 60 km hard error -- so it is out of scope for
   `map:km3net-arca` by rule, not by choice. La Seyne-sur-Mer (ORCA's shore
   town, ~40 km away, within the 60 km limit) is a candidate, but the actual
   *building* housing KM3NeT-Fr's control room has moved during the KM3NeT
   collaboration's own history (Institut Michel Pacha originally; the
   Brégaillon/Ifremer site since January 2024; the MEUST building once
   ready, per a WebSearch of km3net.org and CPPM pages) and Overpass access
   was down for the whole window I could have used to locate any of these
   buildings in OSM. Left as a backlog item, not guessed. Baikal-GVD's shore
   station is even less precisely located in what I could fetch: secondary
   sources describe it as "~4 km" from the lake site near the Ivanovka river
   outfall, but I could not independently fetch and quote a primary source
   for that distance, and again could not search OSM for it. Backlogged.

## What is unlocated, and why (see each map's `unlocated[]` for the sourced text)

All eight unlocated entries are on `map:amundsen-scott-south-pole-station`
(`site:south-pole-ara`, `detector:icecube`, `detector:icecube-deepcore`,
`detector:icetop`, `detector:ara`, `experiment:amanda`,
`experiment:icecube-upgrade`, `experiment:icecube-gen2`); see "Conflicts and
honesty calls" #1-2 above for the reasoning, reproduced with full sourcing in
each `unlocated[]` row. Both KM3NeT maps and the Baikal map have empty
`unlocated[]` lists: every accelerator/beamline/site-with-a-detector-placement
of those facilities is drawn.

## Backlog (concrete next steps, also in each map's `unlocated[].backlog`)

1. **IceCube coordinate-system orientation** (blocks IceCube, DeepCore,
   IceTop, AMANDA, the Upgrade and Gen2): get authenticated or otherwise
   public access to `docs.icecube.aq`'s "Coordinate Systems" page (it 401'd
   to every attempt this session), or find an equivalent statement in a
   fetchable IceCube-Gen2 TDR appendix, that states the local grid's
   true-north orientation with a citable locator. Then the 86 strings' local
   (x,y) positions -- or just the sourced hexagonal-footprint parameters
   (125 m spacing, ~1 km² area) -- can be converted to WGS 84 around a
   surveyed anchor.
2. **ARA station positions**: find a station-specific ARA deployment paper
   or GPS log giving A1-A5's actual coordinates (or IceCube-grid offsets,
   once #1 is resolved).
3. **South Pole buildings**: retry the Overpass query this session could not
   complete -- `way["building"](-90,-180,-89.98,180); way["man_made"](...)`
   -- for the IceCube Laboratory building and any other station structures,
   once Overpass access recovers.
4. **KM3NeT/ORCA footprint**: find a source stating ORCA's building-block
   radius/diameter directly (rather than relying on this worklog's scaled
   estimate from string spacing).
5. **KM3NeT and Baikal shore stations**: once Overpass recovers, search for
   the current KM3NeT-Fr control-room building near La Seyne-sur-Mer/Toulon
   (confirm which of Institut Michel Pacha / Brégaillon-Ifremer / MEUST is
   current) and for a Baikal-GVD shore-station building near the Ivanovka
   outfall; add as context features (feature_type `building`, entity_id
   `null`) if found within 60 km.
6. **Baikal-GVD full-array footprint**: find an official source (design
   reference paper or a cluster-position table) giving the actual deployed
   cluster count and layout as of a stated date, rather than deriving a
   count from two unrelated numbers in the status paper.
7. **ANTARES on the KM3NeT-ORCA map**: if `site:antares-toulon` is ever given
   a `facility_id` and a tighter-precision coordinate by whichever workstream
   owns it, it becomes eligible to draw (or formally unlocate) on
   `map:km3net-orca`.

## Site coordinate corrections

None. Every site coordinate this pass touched (`site:south-pole-icecube`,
`site:south-pole-ara`, `site:km3net-arca-capo-passero`,
`site:km3net-orca-toulon`, `site:baikal-gvd-lake-baikal`) was reused verbatim
as the anchor for the geometry records above; no independent, tighter position
was found this session that would upgrade any of them.

```json
[]
```

## Sources added

3 new `src:geo-polar-*` records:

- `src:geo-polar-osm-south-pole-station` -- OSM node 5314074411 (Overpass
  extract, the one query that succeeded before the outage).
- `src:geo-polar-ara-design-2011` -- ARA Collaboration, "Design and Initial
  Performance of the Askaryan Radio Array Prototype EeV Neutrino Detector at
  the South Pole" (arXiv:1105.2854).
- `src:geo-polar-icetop-detector-paper-2013` -- IceCube Collaboration,
  "IceTop: The surface component of IceCube" (arXiv:1207.6326).

All other citations reuse existing source ids verbatim
(`src:icecube-detector-paper-jinst-2017`, `src:icecube-nsf-south-pole-station`,
`src:icecube-official-detector-page`, `src:icecube-official-quick-facts`,
`src:icecube-official-timeline`, `src:icecube-upgrade-press-release-2026`,
`src:icecube-gen2-tdr-page`, `src:astro-neutrino-ara-overview-paper-2024`,
`src:astro-neutrino-km3net-it-site-page`, `src:astro-neutrino-km3net-fr-site-page`,
`src:astro-neutrino-km3net-loi-2016`, `src:astro-neutrino-baikal-gvd-status-2023-paper`).
No existing site, detector, experiment, facility or source record was edited.

## Validator / build / test results

- `.venv/bin/python -m hepgraph.atlas.validate`: **0 errors**, 1596 warnings, 4
  informational. The only new warning attributable to this pass that I chose
  to leave (rather than fix, since it is correct and expected) is
  `map-center-far` on `map:km3net-orca` ("the map centre is 1126.9 km from
  site:km3net-arca-capo-passero, the facility's primary site... a separate
  campus wants its own map") -- exactly the situation the brief asked for
  (two maps, ARCA and ORCA, 900 km apart, linked via `linked_map_ids`); the
  warning is the validator correctly confirming that a shared map would have
  been wrong. Two `display`-vs-`value` drift warnings I introduced by reusing
  existing sourced display strings verbatim were fixed by rewording to lead
  with the range's midpoint (mirroring `docs/atlas-worklog/GEOMETRY_cern.md`'s
  own fix for the same parser quirk); one `source-rank-mismatch` on
  `src:geo-polar-ara-design-2011` was fixed (rank corrected from 8 to 5 for
  `source_type: detector_paper`). All other warnings in the run pre-exist
  across the rest of the atlas dataset and are untouched by this pass.
- `.venv/bin/python -m hepgraph.atlas.build`: succeeds; 4 new map bundles
  generated (`geometry/amundsen-scott-south-pole-station.json` with 1 feature
  and 8 unlocated entries; `geometry/km3net-arca.json` and
  `geometry/km3net-orca.json` with 2 features and 0 unlocated each, linked to
  each other; `geometry/baikal-deep-underwater-neutrino-telescope.json` with 2
  features and 0 unlocated). The pre-existing `atlas.json` pilot-budget
  warning (over 400 000 bytes) is unrelated to this pass (the whole dataset,
  not these ~15 KB of new map/geometry records).
- `.venv/bin/python -m pytest -q tests/test_atlas_validate.py
  tests/test_atlas_build.py tests/test_atlas_geo.py
  tests/test_atlas_geometry_data.py tests/test_atlas_tools.py`: **233
  passed** (one canonical-JSON formatting failure was hit and fixed mid-session
  by re-serialising every new record through `hepgraph.atlas.load.dump_json`).
