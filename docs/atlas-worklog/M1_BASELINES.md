# M1 data stream: beamline baselines

Branch `atlas-m1-data`, date 2026-10-26. Every source below was fetched on that day (`verified_at` and the source records' `accessed` are 2026-10-26). The globe draws one arc per `baselines[]` row (`buildBeamArcs`, label `<beamline name>: <distance.display> baseline`). Each new row passed the A21 great-circle check (2 %) against the two site points as recorded; no site was moved and the check was not loosened.

## Baselines added or completed

| beamline | from -> to | value | great-circle (A21) | source URL | quote |
|---|---|---|---|---|---|
| `beamline:numi` (new) | `site:fermilab-main-campus` -> `site:soudan-minos-far-detector` | 735.3 km | 735.4 km, 0.01 % | https://arxiv.org/abs/0805.3170 (`src:minos-detector-paper-2008`, full text); corroborating https://ar5iv.labs.arxiv.org/html/1507.06690 (`src:fermilab-numi-beam-paper-2016`) | "The far detector, shown in Fig. 1, is located in Soudan, MN (47.8 N latitude, and 92.2 W longitude), 735.3 km from the NuMI beam production target at Fermilab" (§1). The NuMI beam paper rounds to "encountering the MINOS Far Detector (FD) 734 km away in the Soudan Mine in Minnesota". |
| `beamline:numi` (new) | `site:fermilab-main-campus` -> `site:ash-river-nova-far-detector` | ~810 km (approx) | 811.7 km, 0.2 % | https://arxiv.org/html/2512.20294 (`src:nova-arxiv-2025-monopole-search`); https://arxiv.org/abs/2108.08219 (`src:nova-prd-2022-oscillation-parameters`) | "the 14 kt Far Detector (FD) is located on the surface, 810 km from the target, near Ash River, Minnesota" (§II); PRD: "located at Ash River, Minnesota, ~810 km from the source" (§II) |
| `beamline:kek-neutrino` (new) | `site:kek-tsukuba-belle-ii` -> `site:kamioka-mozumi-mine-super-kamiokande` | 250 km | 249.6 km, 0.2 % | https://neutrino.kek.jp/k2k_faq.html (`src:k2k-faq-page`); https://arxiv.org/abs/hep-ex/0606032 (`src:k2k-prd-2006`) | "After passing through the near detectors, the neutrino beam enters the earth and emerges at Super-Kamiokande, 250 km away." PRD §III: "which is located 250 km away from KEK"; §I: "a neutrino flight distance of 250 km" |
| `beamline:j-parc-neutrino` (already present, completed) | `site:j-parc-main-ring` -> `site:kamioka-hyper-kamiokande-tochibora` | about 295 km (approx) | 294.2 km, 0.3 % | https://arxiv.org/abs/1805.04163 (`src:hk-design-report-2018`); https://pos.sissa.it/395/1192/pdf (`src:hk-pos-icrc2021-status`) | "about 295 km away from the J-PARC proton accelerator research complex in Tokai, Japan" (exec. summary); ICRC 2021: "The far detector site is located at Mt. Nĳugo-yama in the Tochibora-mine at Kamioka at a distance of 295 km from J-Parc." |
| `beamline:cngs` (already present, completed) | `site:cern-meyrin` -> `site:lngs-hall-c` | 732 km | 731.3 km, 0.1 % | https://home.cern/science/accelerators/cern-neutrinos-gran-sasso (`src:opera-cern-cngs-page`) | "to the Gran Sasso National Laboratory (LNGS), 732 kilometres away in Italy." (existing row quote "732 kilometres away in Italy" kept) |

Notes on the rows:

- NuMI also gains `far_detector_site_ids` = Soudan and Ash River (it was empty). Fermilab end is the campus-grade point (precision 3 km, uncertain), so both NuMI rows carry that caveat in `distance.note`.
- K2K: the KEK end is `site:kek-tsukuba-belle-ii`, the only KEK site in the Atlas (KEK `primary_site_id`; `accelerator:kek-ps` has no site). It is a proxy for the KEK-PS beamline site and the row says so. The existing `specs.baseline` (250 km, K2K PRD) stays; its note now points to the new row.
- T2HK: the row was already in the data (not only T2K -> Super-K). It now carries `status: "construction"` (the statuses enum, same vocabulary as intervals), a display of "about 295 km (Hyper-K, under construction)" so the globe label differs from the Super-K arc, and a note with the status evidence. The `status` key on a baseline row is an addition to the row shape; the build passes it through to `atlas.json`. Status sources: https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2024.1378254/full ("the excavations of the Hyper-K main cavern is underway"; "aims to start the operation of the Hyper-K detector in the Japanese fiscal year of 2027") and https://arxiv.org/abs/2602.14810 ("The excavation of the Hyper-Kamiokande cavern, 600 m underground, is complete."). The experiment record keeps the planned start (2027 to 2028). The official outline page (ICRR) and the wayback copy could not be fetched today (HTTP 503 and fetch block), so the 2028 date was not re-checked.
- CNGS: the baseline already had a quote, locator, source and confidence on the distance. The row lacked the row-level `confidence`, `note`, `sources` and `verified_at` that the other rows have; those are added, and the great-circle result is recorded in the distance note. The CERN end is still the Meyrin campus point (no sourced CNGS target coordinate).

## Off-axis angles

| record | field | value | source | quote |
|---|---|---|---|---|
| `beamline:numi` | `specs.off_axis_angle` (existing) | 14.6 mrad | `src:fermilab-nova-offaxis-dpf2017` | "The two detectors are placed 14.6 mrad off-axis from the center of the neutrino beam" |
| `experiment:nova` | `key_specs` "Off-axis angle" (existing) | 14.6 mrad | `src:nova-prd-2022-oscillation-parameters` | "Both detectors are centered 14.6 mrad off the beam axis and receive a narrow-band neutrino flux peaked at 1.8 GeV." (re-read today in arXiv:2108.08219 §II; arXiv:2512.20294 §II says "The detectors are 14.6 mrad off the axis of the NuMI beam") |
| `beamline:j-parc-neutrino` | `specs.off_axis_angle` (existing) | 2.504 +- 0.004 deg | `src:t2k-nim-2011` | "The measured off-axis angle is 2.504 +- 0.004 deg." |
| `experiment:t2k` | `key_specs` "Off-axis angle" (existing) | 2.5 deg | `src:t2k-nim-2011` | same |
| `experiment:hyper-kamiokande` | `key_specs` "Off-axis angle" (added, 5th of 5) | 2.5 deg | `src:hk-pos-icrc2021-status`, `src:hk-design-report-2018` | "At this location approximately 8km south of the Super-Kamiokande site, the neutrino beam from J-PARC will be exposed to the same off-axis angle of 2.5 degree"; design report §II.1.1: "The J-PARC beam is aimed 2.5 away from the Super-K and Hyper-K detectors" |

The brief said NOvA 14 mrad. Both NOvA collaboration papers read today state 14.6 mrad, which the data already carries, so the value was left at 14.6 mrad rather than rounded down. No source states a plain "14 mrad" that was fetched today.

## Not added (no separate site record)

All the detectors below sit on `site:fermilab-main-campus` (their `placements[].site_id`), the same point as the beamline, so a site-to-site baseline would be from a point to itself: great-circle 0 m, which the A21 check scores as an error, and a zero-length arc. No site record was invented. A note on `beamline:numi` and `beamline:bnb` records the sourced figures so a later stream that adds hall-level sites can use them. The A21 plausibility range for a baseline (100 m to 20 000 km) would in any case reject a near-detector distance below 100 m.

| beamline | detector | sourced distance | source URL | quote |
|---|---|---|---|---|
| NuMI | MINOS near detector | 1040 m | https://arxiv.org/abs/0805.3170 | "The near detector is 1040 m from the primary target and 330 m from the hadron absorber at the end of the decay pipe." (§6.1) |
| NuMI | NOvA near detector | ~1 km | https://arxiv.org/html/2512.20294 | "The 0.3 kt Near Detector is located 1 km downstream of the neutrino production target" |
| NuMI | MINERvA | not sourced (not fetched) | | |
| BNB | SBND | 110 m | https://arxiv.org/abs/2504.00245 (abstract); https://arxiv.org/abs/1503.01520 | "located 110 meters from the Booster Neutrino Beam (BNB) target at Fermilab"; SBN proposal: "which will be located 110 m from the BNB target" |
| BNB | MicroBooNE | 470 m | https://arxiv.org/abs/1503.01520 | "is located in the Liquid Argon Test Facility (LArTF) at 470 m" |
| BNB | ICARUS-T600 | 600 m | https://arxiv.org/abs/1503.01520 | "The T600 will be located 600 m from the BNB target." |

The MicroBooNE official page (https://microboone.fnal.gov/) states no distance, and https://icarus.fnal.gov/about/ returned HTTP 403, so the 470 m and 600 m figures rest on the 2015 SBN proposal only (the 2015 text is pre-construction; the SBND paper of 2025 confirms 110 m as built).

## Other sources that could not be read

- https://novaexperiment.fnal.gov/ and /how-does-nova-work/: no km figure, no off-axis angle (only "500-mile interstate trip" and "slightly off the centerline"); NOvA news (https://news.fnal.gov/2014/10/fermilabs-500-mile-neutrino-experiment-up-and-running/) says "placed 500 miles apart". The collaboration papers are used instead.
- https://www-sk.icrr.u-tokyo.ac.jp/en/hk/about/outline/ (HTTP 503), its web.archive.org copy (fetch blocked) and https://www-sk.icrr.u-tokyo.ac.jp/hk/news/ (HTTP 503).

## Files changed

`data/atlas/beamlines/{numi,kek-neutrino,j-parc-neutrino,cngs,bnb}.json`, `data/atlas/experiments/hyper-kamiokande.json`, and `accessed` dates on the 13 source records cited above. No new source records: every URL already had a record.

## Checks

`python -m hepgraph.atlas.validate`: 0 errors (1596 warnings, unchanged from before this stream). `python -m hepgraph.atlas.build` succeeded and all seven baselines appear in `atlas.json`; `static/atlas/generated` was restored afterwards.
