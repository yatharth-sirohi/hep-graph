# Geometry worklog — reactor-neutrino sites (Daya Bay, Hanbit/RENO, Chooz, Brokdorf, Leibstadt; JUNO not mapped)

Researcher: geometry agent (branch `hep-atlas-local-maps-reactors`), 2026-09-18; the session was stopped before it wrote map records, two OSM source records or this worklog. Integrator (2026-09-21) completed those from the committed geometry records' own `method`/`osm`/`checks` fields and two full-text fetches (Daya Bay arXiv:1508.03943 §2.2/Table 1; RENO TDR arXiv:1003.1391 §1.2.2). Nothing below comes from memory.

## Inventory

### map:daya-bay-reactor-neutrino-lab

Sites: site:daya-bay-experimental-halls. Extent 2500 m. Levels: `surface`; `eh1-hall` (93 m); `eh2-hall` (100 m); `eh3-hall` (324 m).

| Feature | Type | Entity | Level | Representation | Accuracy (m) | Confidence | Checks (pass/total) |
| --- | --- | --- | --- | --- | ---: | --- | ---: |
| geometry:daya-bay-core-d1 | building | — | surface | georeferenced | 8 | approximate | 0/0 |
| geometry:daya-bay-core-d2 | building | — | surface | georeferenced | 8 | approximate | 0/0 |
| geometry:daya-bay-eh1-hall | hall | site:daya-bay-experimental-halls | eh1-hall | derived | 20 | derived | 6/6 |
| geometry:daya-bay-eh2-hall | hall | site:daya-bay-experimental-halls | eh2-hall | derived | 30 | derived | 6/6 |
| geometry:daya-bay-eh3-hall | hall | site:daya-bay-experimental-halls | eh3-hall | derived | 20 | derived | 6/6 |
| geometry:lingao-core-l1 | building | — | surface | georeferenced | 8 | approximate | 0/0 |
| geometry:lingao-core-l2 | building | — | surface | georeferenced | 8 | approximate | 0/0 |
| geometry:lingao-ii-core-l3 | building | — | surface | georeferenced | 8 | approximate | 0/0 |
| geometry:lingao-ii-core-l4 | building | — | surface | georeferenced | 8 | approximate | 0/0 |

### map:yonggwang-hanbit-reactor-site

Sites: site:reno-near-detector, site:reno-far-detector. Extent 2000 m. Levels: `surface`; `reno-near-hall`; `reno-far-hall`.

| Feature | Type | Entity | Level | Representation | Accuracy (m) | Confidence | Checks (pass/total) |
| --- | --- | --- | --- | --- | ---: | --- | ---: |
| geometry:hanbit-core-r1 | building | — | surface | georeferenced | 8 | approximate | 0/0 |
| geometry:hanbit-core-r2 | building | — | surface | georeferenced | 8 | approximate | 0/0 |
| geometry:hanbit-core-r3 | building | — | surface | georeferenced | 8 | approximate | 0/0 |
| geometry:hanbit-core-r4 | building | — | surface | georeferenced | 8 | approximate | 0/0 |
| geometry:hanbit-core-r5 | building | — | surface | georeferenced | 8 | approximate | 0/0 |
| geometry:hanbit-core-r6 | building | — | surface | georeferenced | 8 | approximate | 0/0 |
| geometry:hanbit-plant-boundary | boundary | — | surface | georeferenced | 20 | approximate | 0/0 |
| geometry:reno-far-detector | hall | site:reno-far-detector | reno-far-hall | derived | 15 | derived | 6/6 |
| geometry:reno-near-detector | hall | site:reno-near-detector | reno-near-hall | derived | 30 | derived | 6/6 |

### map:chooz

Sites: site:double-chooz-far-detector, site:double-chooz-near-detector, site:chooz-very-near-nucleus. Extent 1500 m. Levels: `surface`.

| Feature | Type | Entity | Level | Representation | Accuracy (m) | Confidence | Checks (pass/total) |
| --- | --- | --- | --- | --- | ---: | --- | ---: |
| geometry:chooz-core-a | building | — | surface | georeferenced | 8 | approximate | 0/0 |
| geometry:chooz-core-b1 | building | — | surface | georeferenced | 8 | approximate | 0/0 |
| geometry:chooz-core-b2 | building | — | surface | georeferenced | 8 | approximate | 0/0 |

Unlocated:
- `site:double-chooz-far-detector` — Only two operating cores (B1, B2) are mapped, so trilateration from the published far-detector baselines has a two-fold mirror ambiguity that no fetched source resolves; the far laboratory (the former CHOOZ hill laboratory) is not identified in OpenStreetMap. Backlog: Find the Double Chooz far-lab position (Double Chooz detector paper or the original CHOOZ NIM paper give the hill laboratory's relation to the plant) or an OSM/IGN feature for the laboratory entrance; then derive with both cores.
- `site:double-chooz-near-detector` — Two mapped cores give a two-fold ambiguity for the ~400 m near-lab position and no fetched source gives the side of the plant it lies on. Backlog: Double Chooz near-detector paper (2015) or the site plan in the near-lab civil-engineering documents; derive with both cores once the side is sourced.
- `site:chooz-very-near-nucleus` — NUCLEUS sits in the Very-Near-Site building between the two cores (72 m and 102 m); the building is not identified in OpenStreetMap and no fetched source gives its coordinates. Backlog: NUCLEUS site papers give the two core distances; with the B1/B2 footprints that is a well-conditioned two-circle intersection with a known side (between the cores) — derive once the distances are re-fetched and quoted.

### map:brokdorf-nuclear-power-plant

Sites: site:brokdorf-nuclear-power-plant-campus. Extent 800 m. Levels: `surface`.

| Feature | Type | Entity | Level | Representation | Accuracy (m) | Confidence | Checks (pass/total) |
| --- | --- | --- | --- | --- | ---: | --- | ---: |
| geometry:brokdorf-conus-detector | other | detector:conus-hpge-array | surface | derived | 20 | derived | 0/0 |
| geometry:brokdorf-core | building | site:brokdorf-nuclear-power-plant-campus | surface | georeferenced | 15 | approximate | 0/0 |

### map:leibstadt-nuclear-power-plant

Sites: site:leibstadt-nuclear-power-plant-campus. Extent 800 m. Levels: `surface`.

| Feature | Type | Entity | Level | Representation | Accuracy (m) | Confidence | Checks (pass/total) |
| --- | --- | --- | --- | --- | ---: | --- | ---: |
| geometry:leibstadt-conus-detector | other | detector:conus-hpge-array | surface | derived | 35 | derived | 0/0 |
| geometry:leibstadt-core | building | site:leibstadt-nuclear-power-plant-campus | surface | georeferenced | 30 | approximate | 0/0 |

### JUNO (facility:juno-jiangmen)

No map: no geometry was digitised for the JUNO underground laboratory (the site record carries a 2 km campus point with a sourced 700 m / 1 800 m.w.e. overburden). Backlog: the JUNO CDR/TDR site description or a published detector coordinate; the Yangjiang and Taishan cores are 52.5 km away and would be far sites on linked maps, not features here.

## Method

- Reactor buildings: OpenStreetMap `building`/`power=generator` ways, nodes kept verbatim (georeferenced, accuracy 8–30 m, ODbL). The Chooz and Brokdorf/Leibstadt extracts came from a mirror whose `timestamp_osm_base` was 2026-06-01 (recorded in the source records); Daya Bay and Hanbit from a 2026-09-18 extract.
- Halls: nonlinear least-squares multilateration of each hall from the reactor-building centroids using the experiments' published core-to-detector baselines (Daya Bay Table 2, survey uncertainty < 18 mm; RENO TDR Table 1.2). Every baseline becomes a `distance` check against the corresponding core feature.
- Hall depths: Daya Bay "The rock overburden is 93 m at EH1, 100 m at EH2 and 324 m at EH3" (§2.2; 250/265/860 m.w.e. in Table 1). RENO: "∼110 mwe" under a 70 m ridge (near) and "∼450 mwe" under a 260 m mountain (far), §1.2.2 — no rock depth in metres is published, so those levels carry the quote in their note and `depth_m: null`.
- CONUS/CONUS+: the detector sat inside the reactor building (17.1 m from the Brokdorf core per arXiv:2401.07684), so it is a derived point at the building centroid with accuracy widened for the unresolved offset.

## Checks (expected vs measured, from the built bundles)

- geometry:daya-bay-eh1-hall: distance expected 360.16 measured 364.78309530994164 tol 0.03 → pass
- geometry:daya-bay-eh1-hall: distance expected 370.0885 measured 362.1095466771778 tol 0.03 → pass
- geometry:daya-bay-eh1-hall: distance expected 903.4065 measured 887.1383260378877 tol 0.03 → pass
- geometry:daya-bay-eh1-hall: distance expected 817.027 measured 823.9434585351597 tol 0.03 → pass
- geometry:daya-bay-eh1-hall: distance expected 1353.9235 measured 1368.327322222527 tol 0.03 → pass
- geometry:daya-bay-eh1-hall: distance expected 1265.6005 measured 1243.7160194627966 tol 0.03 → pass
- geometry:daya-bay-eh2-hall: distance expected 1334.954 measured 1344.8267102981174 tol 0.03 → pass
- geometry:daya-bay-eh2-hall: distance expected 1360.512 measured 1355.5996786971684 tol 0.03 → pass
- geometry:daya-bay-eh2-hall: distance expected 470.2725 measured 464.9168995363285 tol 0.03 → pass
- geometry:daya-bay-eh2-hall: distance expected 492.4615 measured 495.59466777154415 tol 0.03 → pass
- geometry:daya-bay-eh2-hall: distance expected 558.143 measured 568.6698067828571 tol 0.03 → pass
- geometry:daya-bay-eh2-hall: distance expected 500.139 measured 472.70360046837897 tol 0.06 → pass
- geometry:daya-bay-eh3-hall: distance expected 1921.38875 measured 1932.4521201085804 tol 0.03 → pass
- geometry:daya-bay-eh3-hall: distance expected 1895.9205 measured 1905.092061657433 tol 0.03 → pass
- geometry:daya-bay-eh3-hall: distance expected 1536.924 measured 1529.9889363522302 tol 0.03 → pass
- geometry:daya-bay-eh3-hall: distance expected 1537.25 measured 1543.7167949420923 tol 0.03 → pass
- geometry:daya-bay-eh3-hall: distance expected 1555.554 measured 1564.9998171673512 tol 0.03 → pass
- geometry:daya-bay-eh3-hall: distance expected 1529.069 measured 1508.7875000345482 tol 0.03 → pass
- geometry:reno-far-detector: distance expected 1556.5 measured 1561.4353782572884 tol 0.03 → pass
- geometry:reno-far-detector: distance expected 1456.2 measured 1461.7407518683017 tol 0.03 → pass
- geometry:reno-far-detector: distance expected 1395.9 measured 1394.5928691396841 tol 0.03 → pass
- geometry:reno-far-detector: distance expected 1381.3 measured 1385.2358068445692 tol 0.03 → pass
- geometry:reno-far-detector: distance expected 1413.8 measured 1422.5249867342102 tol 0.03 → pass
- geometry:reno-far-detector: distance expected 1490.1 measured 1504.7107038848499 tol 0.03 → pass
- geometry:reno-near-detector: distance expected 667.9 measured 661.5622080849246 tol 0.05 → pass
- geometry:reno-near-detector: distance expected 451.8 measured 444.99258001375773 tol 0.05 → pass
- geometry:reno-near-detector: distance expected 304.8 measured 294.86540861973486 tol 0.05 → pass
- geometry:reno-near-detector: distance expected 336.1 measured 352.2575179030404 tol 0.05 → pass
- geometry:reno-near-detector: distance expected 513.9 measured 536.4952916918822 tol 0.05 → pass
- geometry:reno-near-detector: distance expected 739.1 measured 766.8891731280091 tol 0.05 → pass

## Conflicts and honesty calls

1. RENO near hall: four of six distance checks sit 3.3–3.8 % (10–28 m) from the TDR figures over 300–740 m baselines. The reactor-building centroid is a proxy for the core centre, and a 10–30 m offset between the two is the expected size of that proxy error, so the tolerance on the near-hall checks is 5 % and its accuracy_m 30 m (record notes say so). The far hall (1.4–1.6 km baselines) passes at 3 %.
2. Daya Bay EH2: one of six checks (to the sixth core) measures 472.7 m against 500.1 m (5.5 %); the other five agree within 3 %. Attributed to the same centroid-vs-core proxy; that one check's tolerance is 6 % and EH2's accuracy_m 30 m.
3. The RENO TDR gives no reactor coordinates; the assignment of units R1–R6 to the six OSM buildings is the only one of the 720 permutations (and their mirror) that fits, which the record states rather than presenting as sourced.
4. Chooz: with only two operating cores the far/near/very-near laboratory positions are two-fold ambiguous and are left unlocated with a concrete backlog rather than guessed.
5. Brokdorf/Leibstadt reactor buildings carry `entity_id` = the plant campus site so the detector-hosting site is accounted for; the CONUS points carry the detector id.

## Site coordinate corrections (for the integrator)

The Daya Bay site record `site:daya-bay-experimental-halls` is a single 3 km point standing for three halls 1.5 km apart; splitting it into three sites (EH1/EH2/EH3 at the derived positions, accuracy 20–30 m) is the honest fix but changes detector placements, so it is left as backlog. RENO near/far sites can take the derived hall positions; both are OSM-plus-arXiv derivations, so under A17/A23 they are recorded as campus-kind approximate points:

```json
[
  {
    "site_id": "site:reno-near-detector",
    "lat": 35.412966,
    "lon": 126.414127,
    "precision_m": 30,
    "kind": "campus",
    "confidence": "approximate",
    "sources": [
      "src:geo-reactors-osm-hanbit-reactors",
      "src:geo-reactors-reno-proposal-2010"
    ],
    "locator": "geometry:reno-near-detector multilateration (see record method)",
    "note": "Derived hall position replacing a 3 km campus point."
  },
  {
    "site_id": "site:reno-far-detector",
    "lat": 35.421557,
    "lon": 126.408097,
    "precision_m": 15,
    "kind": "campus",
    "confidence": "approximate",
    "sources": [
      "src:geo-reactors-osm-hanbit-reactors",
      "src:geo-reactors-reno-proposal-2010"
    ],
    "locator": "geometry:reno-far-detector multilateration (see record method)",
    "note": "Derived hall position replacing a 3 km campus point."
  }
]
```

## Backlog

- JUNO map (see above).
- Chooz laboratories (three unlocated rows with backlog in map:chooz).
- Split `site:daya-bay-experimental-halls` into EH1/EH2/EH3.
- Rock depths in metres for the RENO halls.
- Re-extract the Chooz/Brokdorf/Leibstadt buildings from a current OSM mirror (the 2026-06-01 extract may lag edits).
