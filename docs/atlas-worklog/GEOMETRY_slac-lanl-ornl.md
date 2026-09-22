# Geometry worklog: SLAC, Los Alamos (LANSCE), Oak Ridge (SNS)

Researcher: geometry-slac-lanl-ornl. Worktree
`/Users/yatharthsirohi/Desktop/HEP-Graph-maps-slac`, branch
`hep-atlas-local-maps-slac`. Sources prefixed `src:geo-slac-*`,
`src:geo-lanl-*`, `src:geo-ornl-*`. Validated on this branch (validator/build
modules already present, per `RESEARCH_AGENT_RULES.md`/the task brief).

## Method note: Overpass access this session

Overpass was in the same heavily-loaded state the CERN researcher documented:
`overpass-api.de` answered exactly one query (the SLAC extract, below) and
then refused every further connection for the rest of the session (TCP
`connection refused`, then `HTTP 429`, then `connection refused` again).
`lz4.overpass-api.de` never answered at all. Two more mirrors were tried and
rejected: `overpass.kumi.systems` answered but returned **zero elements**
even for a query (`name~"Klystron"` over the SLAC bbox) that `overpass-api.de`
had already answered with a match, and `overpass.osm.ch`'s own
`osm3s.timestamp_osm_base` field came back as the non-date string `"117111"`
— both are almost certainly partial/regional mirrors, not full planet copies,
and were dropped rather than trusted for a "nothing found" result. Midway
through the session the coordinator supplied two more mirrors;
`overpass.private.coffee` never connected, but **`maps.mail.ru/osm/tools/overpass/api/interpreter`
worked** and returned real, complete data (a 1,817-element extract of the
wider Los Alamos townsite; 25 real building footprints inside the SNS
complex) — though it 504-timed-out on anything heavier than a single
`building` filter over a sub-1 km box, so it could not answer the SLC-arc or
SNS-ring/linac searches attempted late in the session. **Nominatim**
(`nominatim.openstreetmap.org`, `/search` and `/lookup?...&polygon_geojson=1`)
stayed reachable throughout and, being a lighter-weight, differently-rate-limited
service, is the source of the LANSCE point and the full SNS complex boundary
polygon used below — `/lookup` returns real OSM element geometry directly,
which turned out to be a reliable fallback path when Overpass itself was
unreachable.

## Inventory

### SLAC (map:slac)

| Entity | Drawn? | Feature(s) | Representation | Accuracy | Check |
| --- | --- | --- | --- | --- | --- |
| facility:slac | map:slac authored | — | — | — | — |
| site:slac-menlo-park-campus | drawn | geometry:slac-property-boundary | georeferenced (OSM property boundary, way 634083231) | 20 m | none (context/site marker) |
| site:slac-pep-ii-ir2-babar | drawn | geometry:slac-pep-ir2-babar-hall | georeferenced (OSM building, name-matched + SLAC Area Map building 620) | 10 m | none formally asserted |
| site:slac-slc-collider-hall-sld | drawn | geometry:slac-collider-experimental-hall-sld + geometry:slac-collider-experimental-hall-dmradio | georeferenced (OSM building, name-matched + SLAC Area Map building 750) | 10 m | none formally asserted |
| accelerator:slac-linac | drawn | geometry:slac-linac-klystron-gallery | georeferenced, **verified** | 10 m | span 3,066.1 m vs 3,073.72 m (SLAC official, tol 2%) — **pass**, 0.25% |
| accelerator:pep-ii | drawn (partial) | geometry:slac-pep-ii-partial-ring | georeferenced, kept **approximate** | 30 m | not asserted — incomplete/unclosed ring road, see conflicts |
| accelerator:slc | **unlocated** | — (interaction point drawn via site:slac-slc-collider-hall-sld) | — | — | — |
| detector:babar | drawn (via its site) | geometry:slac-pep-ir2-babar-hall | georeferenced | 10 m | — |
| detector:sld | drawn (via its site) | geometry:slac-collider-experimental-hall-sld | georeferenced | 10 m | — |
| detector:dmradio | drawn (bonus, more specific than its own sourced placement) | geometry:slac-collider-experimental-hall-dmradio | georeferenced | 10 m | — |
| (context) 4 other PEP-II interaction regions, PEP Control Room, PEP Beam Facility/SSRL x2, End Station A, End Station B | drawn | geometry:slac-other-pep-and-end-station-buildings (MultiPolygon, 9 buildings) | georeferenced | 10 m | none (context only) |

7 geometry records, 1 entity unlocated (`accelerator:slc`; see `map.unlocated[]`
for the sourced reason/backlog).

### Los Alamos National Laboratory / LANSCE (map:los-alamos-national-laboratory)

| Entity | Drawn? | Feature(s) | Representation | Accuracy | Check |
| --- | --- | --- | --- | --- | --- |
| facility:los-alamos-national-laboratory | map authored | — | — | — | — |
| site:lanl-lansce | drawn | geometry:lansce-site-marker | georeferenced (single OSM node) | 150 m | none (marker only) |
| accelerator:lansce | **unlocated** | — | — | — | — |
| detector:lsnd | **unlocated** (informational; not required by the validator, added for honesty) | — | — | — | — |

1 geometry record, 1 required entity unlocated (`accelerator:lansce`) plus one
voluntary informational row (`detector:lsnd`).

### Oak Ridge National Laboratory / SNS (map:oak-ridge-national-laboratory)

| Entity | Drawn? | Feature(s) | Representation | Accuracy | Check |
| --- | --- | --- | --- | --- | --- |
| facility:oak-ridge-national-laboratory | map authored | — | — | — | — |
| site:ornl-sns-neutrino-alley | drawn | geometry:sns-complex-boundary | georeferenced (OSM complex boundary, way 907808191) | 100 m | none (whole-complex proxy, see conflicts) |
| accelerator:sns | **unlocated** | — | — | — | — |

1 geometry record, 1 required entity unlocated (`accelerator:sns`). COHERENT's
four sub-detectors (CENNS-10, CsI, Ge, NaI) are not individually
unlocated-listed (detectors are not in the validator's required "drawn or
unlocated" set) but are discussed in Conflicts below.

## Checks (expected vs measured)

| Feature | Expected | Source | Measured | Diff | Tolerance | Result |
| --- | --- | --- | --- | --- | --- | --- |
| SLAC linac (Klystron Gallery span) | 3,073.72 m | src:geo-slac-at-a-glance, "Our linear accelerator structure is 3,073.72 meters long" | 3,066.1 m | 0.25% | 2% | PASS |

Only one formal `checks[]` row was written this session (all other drawn
features are buildings/boundaries with no independent published dimension, or
the deliberately incomplete PEP-II ring, discussed below). The klystron-gallery
check is unusually strong evidence because the official figure is stated for
*this exact structure* (SLAC's own "By the Numbers" page calls it the "linear
accelerator structure", i.e. the building measured, not a proxy), which is why
`confidence: verified` was used rather than `approximate` — the pattern the
contract's §1.2 confidence rule is built for.

## Site coordinate corrections (for the integrator)

All three facilities' detector-hosting sites currently carry the *same*
generic geocoder-derived campus point (or, for LANSCE/SNS, a coarser one), and
in every case an OSM-sourced, more specific point is available and disagrees
with the recorded coordinate by more than its own `precision_m`:

```json
[
  {
    "site_id": "site:slac-menlo-park-campus",
    "current": {"lat": 37.45383, "lon": -122.18219, "precision_m": 1000},
    "suggested": {"lat": 37.41656745086245, "lon": -122.20998802597693, "precision_m": 2000},
    "residual_m": 4582,
    "evidence": "Centroid of OpenStreetMap way 634083231 ('SLAC National Accelerator Laboratory' property boundary)",
    "source": "src:geo-slac-osm-property-boundary"
  },
  {
    "site_id": "site:slac-pep-ii-ir2-babar",
    "current": {"lat": 37.45383, "lon": -122.18219, "precision_m": 1000},
    "suggested": {"lat": 37.419142962924376, "lon": -122.19673639707415, "precision_m": 30},
    "residual_m": 4952,
    "evidence": "Centroid of OpenStreetMap way 232494155 ('PEP Interation Region 2'), corroborated by the official SLAC Area Map's building 620",
    "source": "src:geo-slac-osm-ir2-babar"
  },
  {
    "site_id": "site:slac-slc-collider-hall-sld",
    "current": {"lat": 37.45383, "lon": -122.18219, "precision_m": 1000},
    "suggested": {"lat": 37.418333871732855, "lon": -122.19487721964103, "precision_m": 30},
    "residual_m": 4779,
    "evidence": "Centroid of OpenStreetMap way 232494549 ('Collider Experimental Hall (CEH)'), corroborated by the official SLAC Area Map's building 750",
    "source": "src:geo-slac-osm-collider-hall"
  },
  {
    "site_id": "site:lanl-lansce",
    "current": {"lat": 35.88808, "lon": -106.30697, "precision_m": 800},
    "suggested": {"lat": 35.8725644, "lon": -106.2890098, "precision_m": 150},
    "residual_m": 2365,
    "evidence": "OpenStreetMap node 8041862150, named 'LANSCE'",
    "source": "src:geo-lanl-osm-lansce-node"
  },
  {
    "site_id": "site:ornl-sns-neutrino-alley",
    "current": {"lat": 36.01036, "lon": -84.26964, "precision_m": 2000},
    "suggested": {"lat": 35.95268192792727, "lon": -84.30044038845206, "precision_m": 800},
    "residual_m": 7011,
    "evidence": "Centroid of OpenStreetMap way 907808191 ('ORNL Spallation Neutron Source' complex boundary) -- still only the whole-complex boundary, not Neutrino Alley itself specifically, hence the wide suggested precision_m",
    "source": "src:geo-ornl-osm-sns-boundary"
  }
]
```

All five residuals were computed with `hepgraph.atlas.geo.haversine_m`
(R = 6,371,008.8 m) between the site's currently-recorded coordinate and the
OSM-derived point/centroid above. None of these corrections were applied to
the site records themselves, per the brief's "do not edit existing records"
rule; they are reported here for the integrator.

## Conflicts and honesty calls

1. **PEP-II's ring is drawn only partially, and no length check is asserted.**
   OpenStreetMap has two ways both named "PEP Ring Road" (26309158,
   1,320.2 m; 26309159, 699.0 m), but their endpoints do not meet — together
   they trace about 2,019 m of track, not a closed loop, against the PEP-II
   Conceptual Design Report's official "each with a circumference of 2200 m"
   (src:geo-slac-pepii-cdr-osti). Per the contract, a ring road is not the
   buried beam tunnel itself; `feature_type` is `beamline` (not `ring`, since
   the shape is neither closed nor a full-circumference claim) and
   `accuracy_m` is widened to 30 m, the ring-road-proxy tier. No `checks[]`
   row is written because a length check against an admittedly-incomplete,
   unclosed shape would not be a meaningful circumference measurement; the
   ~181 m (8%) shortfall is reported here instead as a residual, matching how
   the CERN worklog handled SPS's mapper-fitted-circle caveat.

2. **DMRadio-m3's true location (Building 750) is better-sourced than its own
   detector record's placement.** `detector:dmradio`'s only sourced placement
   is the generic SLAC campus point (`site:slac-menlo-park-campus`), with a
   note admitting no IR/building-specific source was fetched for it. This
   session found one: Brouwer et al., Phys. Rev. D 106, 103008 (2022),
   states plainly "DMRadio-m3 will be located in Building 750 at SLAC
   National Accelerator Laboratory, the former site of the SLD detector."
   The official SLAC Area Map independently confirms building 750 is the
   "Collider Experimental Hall (CEH)" — the same OSM polygon already drawn
   for `site:slac-slc-collider-hall-sld`. Rather than edit `detector:dmradio`'s
   placement (out of scope for this pass — see the brief's "do not edit
   existing detector records" rule), a second, entity-linked geometry feature
   (`geometry:slac-collider-experimental-hall-dmradio`) was drawn over the
   *same* shape as the SLD hall, citing the DMRadio paper directly. This is
   an intentional `geometry-duplicate-shape` warning, the same pattern the
   CERN worklog used for its LEP/LHC and LEP-experiment/LHC-experiment pairs:
   two different, independently-sourced occupants of one physical building at
   different times. **Suggested follow-up for whoever owns `detector:dmradio`:**
   re-point its placement's `site_id` to `site:slac-slc-collider-hall-sld`
   (or a similarly precise successor) once this cross-reference is reviewed.

3. **SLC's own arcs are unlocated; only its interaction point is drawn.** No
   OpenStreetMap element (named or otherwise) traces the SLC's north/south
   collider arcs or final-focus system between the end of the linac and the
   Collider Experimental Hall, and no fetched source gives their path in
   coordinates (the SLC Design Handbook, SLAC-R-714, was not fetched this
   session — it does not appear to be online as a scanned/searchable PDF).
   `site:slac-slc-collider-hall-sld` is drawn (via the Collider Experimental
   Hall building, entity-linked to the site itself for `map-entity-unaccounted`
   purposes), which is why `accelerator:slc` is listed `unlocated` with a
   reason that explicitly says the interaction point is drawn elsewhere,
   following the same "ring already drawn, machine itself unlocated"
   precedent CERN used for HL-LHC.

4. **The Klystron Gallery is drawn as the linac's own feature, honestly as a
   `building`, not a `linac`.** The above-ground Klystron Gallery structure
   (OSM way 162058026) runs directly over the buried linac beam tunnel it
   powers, and SLAC's own "By the Numbers" page states the *structure itself*
   (not a proxy) is 3,073.72 m long — an unusually clean, high-confidence
   match (0.25%) to the OSM measurement. `feature_type: building` was kept
   (matching the CERN worklog's Linac4-building precedent) rather than
   `linac`, since the drawn shape is the surface building's own footprint,
   not an asserted centerline of the buried beam path.

5. **LANL/TA-53's core is genuinely almost unmapped in OpenStreetMap, not
   merely unreached.** A working Overpass mirror (`maps.mail.ru`) was used
   late in the session to directly test a 700 m box around the one named
   "LANSCE" node: it returned **zero building ways**. Combined with zero
   Nominatim hits for "LANSCE Linac", "Area A", "Lujan Neutron Scattering
   Center" and "Weapons Neutron Research", this is treated as a real data gap
   rather than a network problem, and `accelerator:lansce` and `detector:lsnd`
   are both left unlocated rather than derived from a coarse anchor. TA-53 is
   also security-sensitive, so even if a building had been found, only a
   publicly-shown accelerator/experimental area would have been drawn (per
   the research brief).

6. **LSND's position was not derived, even though a distance is sourced, for
   lack of a sourced *direction*.** LSND's own NIM paper gives "about 30 m
   from the A6 proton beam stop" (src:lsnd-nim-1997-detector-paper), and a
   2020 NIM-A paper on LANSCE's Area A independently states a (different,
   later-proposed) FPNS target sits "near the center of Area A, some 100 m
   downstream of the end of the 800-MeV accelerator"
   (src:geo-lanl-fpns-area-a-nim-2020) — useful confirmation that Area A's
   target region is roughly 100 m past the linac's end, but neither source
   gives the switchyard/Line-A beamline's heading, and the linac's own end
   point is not itself located this session (see point 5). Deriving a point
   from an unsourced direction would not be honest per the contract's
   "derived" rules; LSND is left undrawn.

7. **SNS's linac and accumulator ring are inside a drawn boundary, but not
   separately traced, and no building is guessed at.** The SNS accumulator
   ring's official circumference is "the 271-yard-long ring" (247.8 m per
   src:geo-ornl-sns-ppu-ring), and the linac's length is stated differently
   across eras and pages: "1,000-foot linac" (304.8 m, a 2005 pre-completion
   article, src:geo-ornl-sns-cold-linac-2005) versus a "355-yard" (~325 m)
   figure elsewhere; a commonly-quoted ~493 m post-Proton-Power-Upgrade total
   appears only in unfetched secondary summaries and is **not** used per the
   "nothing from memory" rule. `maps.mail.ru` did return the SNS complex's 25
   individual building footprints once reachable, but none carries a name or
   tag beyond generic `building=yes`/`service` (one, irrelevantly, is the
   "ORNL Guest House"). One unlabeled way (892578460) is an unusually long,
   thin rectangle — span 370 m, area 5,294 sq m, implied width ~14 m —
   geometrically consistent with the linac-length range, but identifying it
   as the linac from shape alone, with no name, tag, or independent
   positional corroboration, would be this researcher's inference rather than
   a sourced claim, so it is reported only as a backlog lead, not drawn.
   `accelerator:sns` stays unlocated; the complex's outer boundary
   (`geometry:sns-complex-boundary`) is drawn instead, entity-linked to
   `site:ornl-sns-neutrino-alley` since that is the map's one detector-hosting
   site, with `accuracy_m` honestly widened to 100 m because the boundary is
   not itself a claim about Neutrino Alley's specific position.

8. **Neutrino Alley and its four COHERENT sub-detectors are not drawn
   individually.** An official ORNL Q&A page (src:geo-ornl-neutrino-alley-qa)
   gives Neutrino Alley's own length ("a 164-foot, or 50-meter, long
   hallway") and its closest approach to the target ("about 20 meters"), and
   the existing `detector:coherent-csi` record separately cites 19.3 m for
   CsI specifically — but no source found this session gives a coordinate,
   heading, or OSM element for the alley itself, nor any other individual
   detector's position along it. All four sub-detectors' hosting site
   (`site:ornl-sns-neutrino-alley`) is accounted for via the complex boundary
   feature; the detectors themselves are not required to be drawn or
   unlocated by the validator (only detector-*hosting sites* are), so no
   `unlocated[]` row was added for them, but the gap is recorded here per the
   brief's "say what you could not do" standard.

9. **`geometry-duplicate-shape` warning (1, intentional).**
   `geometry:slac-collider-experimental-hall-sld` and
   `geometry:slac-collider-experimental-hall-dmradio` share one OSM polygon
   (way 232494549 / SLAC building 750): SLD occupied it 1991-1998, DMRadio-m3
   occupies it today. Explained in point 2 above and in `map:slac.notes`.

## Backlog (concrete next steps, also in each map's `unlocated[].backlog`)

1. **SLAC / SLC arcs**: find the SLC Design Handbook (SLAC-R-714, December
   1984) or a civil-engineering site plan showing the arc paths from the end
   of the linac to the Collider Experimental Hall; georeference against the
   linac and hall footprints already drawn.
2. **SLAC / PEP-II ring**: retry Overpass (any working mirror) for the
   remaining ~180 m of ring road not yet traced, or find an official PEP-II
   site plan with a scale bar to close the loop and support a proper `length`
   check against the CDR's 2,200 m figure.
3. **LANSCE**: no further Overpass retry is expected to help (a working
   mirror already returned zero buildings within 700 m of the facility);
   find a public LANSCE facilities brochure or environmental-assessment site
   plan with a scale bar and at least three surveyed control points.
4. **LSND**: find a LANSCE/LAMPF-era civil-engineering drawing or the
   original LSND proposal's site plan giving Line A's/Area A's beamline
   heading and the A6 beam stop's coordinates or its distance and bearing
   from a surveyed LANSCE control point.
5. **SNS linac/ring**: retry Overpass (a fuller query — name/landuse tags,
   the ring's characteristic near-circular shape) once a mirror answers
   reliably within its timeout; investigate unlabeled way 892578460 (span
   370 m) as a linac-building candidate via an official annotated aerial
   photo or civil-engineering site plan before drawing it.
6. **Neutrino Alley**: find an ORNL/SNS site plan, environmental assessment,
   or COHERENT proposal document giving Neutrino Alley's own coordinate,
   heading, or a per-detector position along its length.
7. **DMRadio-m3 placement**: flag `detector:dmradio`'s own record for a
   possible `site_id` update to `site:slac-slc-collider-hall-sld` given the
   Building-750 sourcing found this session (see Conflicts, point 2).

## Sources added

19 new source records (`src:geo-slac-*` x 10, `src:geo-lanl-*` x 4,
`src:geo-ornl-*` x 3, plus 2 more counted above): 8 OpenStreetMap extracts (6
SLAC, 1 LANL node, 1 ORNL boundary), 2 official SLAC facility pages, 1
official SLAC building-number map, 1 PEP-II Conceptual Design Report
abstract, 1 DMRadio-m3 journal article, 2 official LANL pages/papers, 3
official/journal ORNL sources. See `data/atlas/sources/geo-{slac,lanl,ornl}-*.json`.
No existing source, site, detector, accelerator or beamline record was
edited; all citations of pre-existing sources (e.g. `src:slac-wikipedia`,
`src:lsnd-nim-1997-detector-paper`) reuse the ids verbatim.

## Validator / build / test results

- `.venv/bin/python -m hepgraph.atlas.validate`: **0 errors**, 1593 warnings
  (all pre-existing across the rest of the atlas dataset except the one
  intentional `geometry-duplicate-shape` warning explained above, and the
  pre-existing A20/A23 site-coordinate warnings on the five sites listed in
  "Site coordinate corrections", which this session's findings corroborate
  rather than cause).
- `.venv/bin/python -m hepgraph.atlas.build`: succeeds; `geometry/slac.json`
  (7 features, bbox `[-122.239715, 37.4117633, -122.1934708, 37.4218774]`),
  `geometry/los-alamos-national-laboratory.json` (1 feature),
  `geometry/oak-ridge-national-laboratory.json` (1 feature); all three well
  under the 2 MB bundle limit; attribution
  `["© OpenStreetMap contributors (ODbL-1.0)"]` on all three.
- `.venv/bin/python -m pytest -q tests/test_atlas_validate.py
  tests/test_atlas_build.py tests/test_atlas_geo.py
  tests/test_atlas_geometry_data.py tests/test_atlas_tools.py`: **233
  passed**.
- `scripts/atlas_coverage_report.py`: regenerated; the new "Local map
  geometry" table row for each of the three maps matches this worklog's
  inventory counts.
