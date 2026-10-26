# Underground labs: the muon-flux data stream (M5)

Branch `atlas-m5-underground`, 2026-10-26. Owner tag `underground-labs`. Researcher: M5 stream (Sonnet 5.5).
Feeds the "Going underground" chart (depth in m.w.e. against cosmic-ray muon flux, one point per laboratory).
Every number below was read today in the paper named, from a text extraction of its PDF, and every `quote` was
machine-checked against that extraction (whitespace-normalised, otherwise verbatim) before it was written.

## 1. Scope

* **Schema (A27).** New quantity dimension `muon_flux` (units `cm^-2 s^-1` base, `m^-2 s^-1`, `m^-2 d^-1`; the third
  is the unit EDELWEISS publishes in, and the CJPL review tabulates in it too), optional site field `muon_flux`, plausibility range
  1e-11 to 5e-2 cm^-2 s^-1, applied to the site field by a four-line addition to `check_specs` in
  `validate.py` (the range table alone only reaches `specs`, `key_specs` and `baselines`). Amendment text in
  `docs/HEP_ATLAS_ONTOLOGY.md` after A26, plus a row in the section 2.4 unit table and the section 3.2 site table.
  `schema.py` was touched only in `UNITS`, `UNIT_SCALE`, `PLAUSIBILITY_RANGES` and the site entry of `ENTITY_FIELDS`.
* **Build.** The stripper already passes every authored quantity through, so `muon_flux` reaches `atlas.json`
  (`value`, `unit`, `dimension`, `display`, `approx`) and `provenance.json` (`quote`, `sources`, `note`, ...) with no
  change to `build.py`; `tests/test_atlas_build.py::test_a27_site_muon_flux_reaches_the_bundle_and_its_provenance`
  pins that. Note for the chart: the bundle carries the value in the unit the source uses, so the chart must convert
  with `UNIT_SCALE['muon_flux']` (m^-2 s^-1 is 1e-4, m^-2 d^-1 is 1.157e-9, in cm^-2 s^-1).
* **Data.** The 12 `underground_laboratory` facilities (SNOLAB, LNGS, SURF, Kamioka, CJPL, LSM, Boulby, LSC, WIPP,
  Soudan, Baksan, JUNO) and their 18 underground sites. 29 values written: `muon_flux` on 15 sites, `depth_mwe` on
  12 (8 new, 2 corrected, 2 with a note and a source added), `depth` on 2 (1 new, 1 corrected). Vertical
  intensities (per steradian) appear only in notes, never as `muon_flux`.
* **Not created:** no site, facility, accelerator or experiment (see section 6).

## 2. What went into the chart (one row per site that carries a `muon_flux`)

| Site | m.w.e. | Flux as published | Unit of `value` | Flux in cm^-2 s^-1 | Confidence |
| --- | ---: | --- | --- | ---: | --- |
| `site:snolab-underground-lab` | 6000 | 3.31 × 10⁻¹⁰ cm⁻² s⁻¹ (± 0.01 stat., ± 0.09 syst.) | `cm^-2 s^-1` | 3.31e-10 | verified |
| `site:lngs-hall-a` | 3800 | 3.35 × 10⁻⁴ m⁻² s⁻¹ (± 0.0005 stat., ± 0.03 syst.) | `m^-2 s^-1` | 3.35e-08 | verified |
| `site:lngs-hall-b` | 3800 | 3.22 × 10⁻⁴ m⁻² s⁻¹ (± 0.08) | `m^-2 s^-1` | 3.22e-08 | approximate |
| `site:lngs-hall-c` | 3800 | 3.432 × 10⁻⁴ m⁻² s⁻¹ (± 0.003) | `m^-2 s^-1` | 3.43e-08 | verified |
| `site:surf-davis-campus-lz` | 4300 | 5.09 × 10⁻⁹ cm⁻² s⁻¹ (± 0.08 stat., ± 0.10 syst.) | `cm^-2 s^-1` | 5.09e-09 | verified |
| `site:kamioka-kamland` | 2700 | 1.49 × 10⁻⁷ cm⁻² s⁻¹ (± 0.11; published as 5.37 ± 0.41 m⁻² h⁻¹) | `cm^-2 s^-1` | 1.49e-07 | verified |
| `site:cjpl-i` | 6720 | 3.53 × 10⁻¹⁰ cm⁻² s⁻¹ (± 0.22 stat., ± 0.07 syst.) | `cm^-2 s^-1` | 3.53e-10 | verified |
| `site:cjpl-ii` | 6720 | 3.03 × 10⁻¹⁰ cm⁻² s⁻¹ (± 0.24 stat., ± 0.18 syst.) | `cm^-2 s^-1` | 3.03e-10 | verified |
| `site:lsm-frejus` | 4800 | 5.4 m⁻² d⁻¹ (± 0.2 stat., +0.5 −0.9 syst.) | `m^-2 d^-1` | 6.25e-09 | verified |
| `site:boulby-mine` | 2805 | 4.09 × 10⁻⁸ cm⁻² s⁻¹ (± 0.15) | `cm^-2 s^-1` | 4.09e-08 | verified |
| `site:lsc-canfranc` | 2450 | 5.26 × 10⁻³ m⁻² s⁻¹ (± 0.21) | `m^-2 s^-1` | 5.26e-07 | verified |
| `site:wipp-surface-campus` | 1585 | 4.77 × 10⁻⁷ cm⁻² s⁻¹ (+0.08 −0.10) | `cm^-2 s^-1` | 4.77e-07 | verified |
| `site:soudan-minos-far-detector` | 2070 | 1.65 × 10⁻⁷ cm⁻² s⁻¹ (± 0.02 stat., ± 0.1 syst.), E > 1 GeV | `cm^-2 s^-1` | 1.65e-07 | verified |
| `site:baksan-sage-underground-lab` | 4700 | 3.03 × 10⁻⁹ cm⁻² s⁻¹ (± 0.10) | `cm^-2 s^-1` | 3.03e-09 | verified |
| `site:juno-jiangmen-underground-lab` | 1800 | 0.004 m⁻² s⁻¹ (simulated) | `m^-2 s^-1` | 4e-07 | approximate |

How to read the table, and what the chart should know:

* **One point per laboratory.** LNGS has three points (Halls A, B, C, from LVD, MACRO and Borexino); plot Hall C
  (Borexino 2019, the most precise and the only one read from the primary paper) or all three. SURF is carried by
  the Davis Campus site only (the DUNE far-detector caverns on the same level have no measurement). Kamioka is
  carried by the KamLAND site only (the only measurement at Kamioka).
* **Mountain laboratories sit above the flat-overburden curve** (LNGS, LSM, Kamioka, CJPL, LSC): the quoted m.w.e.
  is a vertical or average depth, and the thinner rock at the flanks lets more muons in. Mei & Hime 2006 Table I and
  Woodley et al. 2024 Table III give equivalent flat-overburden depths if the chart wants them; they are quoted in
  the notes, not used as `depth_mwe`.
* **JUNO is a simulation**, `approximate`, with "simulated" in its `display`; no measurement exists. Hall B (MACRO)
  is `approximate` because only a second-hand quotation was read. Everything else is `verified`.
* **CJPL-II `depth_mwe` is `derived`**: the 6720 m.w.e. published for CJPL-I applies to the CJPL-wide ~2400 m of
  rock; no CJPL-II-specific figure exists.

## 3. Every value written

| Site | Field | Change | Display | Confidence | URLs | Quote | Locator |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `site:snolab-underground-lab` | `muon_flux` | new | 3.31 × 10⁻¹⁰ cm⁻² s⁻¹ (± 0.01 stat., ± 0.09 syst.) | verified | https://arxiv.org/abs/0902.2776, https://arxiv.org/abs/2608.20504, https://arxiv.org/abs/astro-ph/0512125 | "The cosmic ray muon flux at SNO with zenith angle cos θzenith > 0.4 is measured to be (3.31±0.01 (stat.)±0.09 (sys.))×10−10 µ/s/cm2" | Abstract and Sec. V.A (Cosmic-Ray Muon Flux), Phys. Rev. D 80, 012001 (arXiv:0902.2776) |
| `site:snolab-underground-lab` | `depth_mwe` | note and sources extended | ~6000 m water equivalent | verified | https://arxiv.org/abs/nucl-ex/9910016, https://arxiv.org/abs/0902.2776, https://arxiv.org/abs/astro-ph/0512125 | "The granitic rock overburden (mainly norite) corresponds to approximately 6000 m water equivalent." |  |
| `site:lngs-hall-a` | `muon_flux` | new | 3.35 × 10⁻⁴ m⁻² s⁻¹ (± 0.0005 stat., ± 0.03 syst.) | verified | https://arxiv.org/abs/1909.04579, https://arxiv.org/abs/1808.04207 | "We report the value of the average muon flux measured from 1994 to 2017: I0µ = 3.35 ± 0.0005stat ± 0.03sys · 10−4 m−2 s−1" | Abstract and Sec. III, Phys. Rev. D 100, 062002 (arXiv:1909.04579) |
| `site:lngs-hall-a` | `depth_mwe` | new | 3800 m.w.e. | verified | https://arxiv.org/abs/1102.0208 | "The rock overburden of the laboratory is about 3100 m w.e. (minimum depth), or 3800 m w.e. (average depth)." | Section on LNGS; Table 1 (Pandola 2011) |
| `site:lngs-hall-b` | `muon_flux` | new | 3.22 × 10⁻⁴ m⁻² s⁻¹ (± 0.08) | approximate | https://arxiv.org/abs/1202.6403, https://arxiv.org/abs/1808.04207, https://arxiv.org/abs/2406.10339 | "Borexino is located in Hall C, while the cosmic muon flux has been measured previously by LVD in Hall A [4] and by MACRO in Hall B [16]. These experiments reported a flux of (3.31 ± 0.03) · 10−4 m−2 s−1 and (3.22 ± 0.08) · 10−4 m−2 s−1 , respectively." | Sec. 3 (The Cosmic Muon Flux), Borexino 2012; Table 1, Borexino 2019 |
| `site:lngs-hall-b` | `depth_mwe` | new | 3800 m.w.e. | verified | https://arxiv.org/abs/1102.0208 | "The rock overburden of the laboratory is about 3100 m w.e. (minimum depth), or 3800 m w.e. (average depth)." | Section on LNGS; Table 1 (Pandola 2011) |
| `site:lngs-hall-c` | `muon_flux` | new | 3.432 × 10⁻⁴ m⁻² s⁻¹ (± 0.003) | verified | https://arxiv.org/abs/1808.04207, https://arxiv.org/abs/1202.6403 | "We have measured the flux of cosmic muons in the Laboratori Nazionali del Gran Sasso at 3800 m w.e. to be (3.432 ± 0.003) · 10−4 m−2 s−1 based on ten years of Borexino data acquired between May 2007 and May 2017." | Abstract and Sec. 3; Table 1 (Hall C), JCAP 02 (2019) 046 (arXiv:1808.04207) |
| `site:lngs-hall-c` | `depth_mwe` | new | 3800 m.w.e. | verified | https://arxiv.org/abs/1808.04207, https://arxiv.org/abs/1102.0208 | "Borexino is an organic liquid scintillator detector situated at the LNGS, covered by a limestone overburden of 3800 m w.e." | Sec. 1 (Introduction), Borexino 2019 |
| `site:surf-davis-campus-lz` | `muon_flux` | new | 5.09 × 10⁻⁹ cm⁻² s⁻¹ (± 0.08 stat., ± 0.10 syst.) | verified | https://arxiv.org/abs/2602.16799, https://arxiv.org/abs/1602.07742, https://arxiv.org/abs/2603.06504 | "This rate corresponds to a muon flux of (5.09 ± 0.08stat. ± 0.10sys. ) × 10−9 cm−2 s−1 in the Davis Cavern." | Abstract and Sec. 5-6, arXiv:2602.16799 (v2, 7 Oct 2026) |
| `site:kamioka-kamland` | `muon_flux` | new | 1.49 × 10⁻⁷ cm⁻² s⁻¹ (± 0.11; published as 5.37 ± 0.41 m⁻² h⁻¹) | verified | https://arxiv.org/abs/0907.0066, https://arxiv.org/abs/astro-ph/0512125, https://arxiv.org/abs/2406.10339, https://arxiv.org/abs/1805.04163 | "The muon rate corresponds to an integrated muon intensity of Jµ = 5.37 ± 0.41 m−2 h−1" | Sec. III (Cosmic-ray muons), Phys. Rev. C 81, 025807 |
| `site:kamioka-kamland` | `depth_mwe` | new | ~2700 m.w.e. | verified | https://arxiv.org/abs/0907.0066 | "the vertical rock overburden is approximately 2700 meters water equivalent (mwe)" | Sec. II (Detector description and performance) |
| `site:kamioka-kamland` | `depth` | new | ~1000 m of rock | verified | https://arxiv.org/abs/0907.0066 | "The vertical overburden at KamLAND is approximately 1000 m of rock" | Sec. III (Cosmic-ray muons), Phys. Rev. C 81, 025807 |
| `site:kamioka-hyper-kamiokande-tochibora` | `depth_mwe` | new | 1750 m.w.e. | verified | https://arxiv.org/abs/1805.04163 | "with an overburden of 650 meters of rock or 1,750 meters-water-equivalent (m.w.e.)" | Sec. II.2 (Hyper-K candidate site), Hyper-Kamiokande Design Report |
| `site:cjpl-i` | `muon_flux` | new | 3.53 × 10⁻¹⁰ cm⁻² s⁻¹ (± 0.22 stat., ± 0.07 syst.) | verified | https://arxiv.org/abs/2007.15925, https://arxiv.org/abs/1305.0899, https://arxiv.org/abs/2406.10339 | "measured the cosmic-ray muon flux to be (3.53 ± 0.22stat. ± 0.07sys. ) × 10−10 cm−2 s−1" | Abstract and Sec. 6, Chin. Phys. C 45, 025001 (arXiv:2007.15925) |
| `site:cjpl-i` | `depth_mwe` | replaced (was ~2400 m.w.e.) | 6720 m.w.e. | verified | https://arxiv.org/abs/1305.0899, https://arxiv.org/abs/1404.2651, https://arxiv.org/abs/2406.10339 | "The water equivalent depth of CJPL is calculated to be 6720m as the product of the measured average rock density of 2.8g/cm3 and the depth of 2400m." | Sec. 4, Chin. Phys. C 37 (2013) 086001 (arXiv:1305.0899) |
| `site:cjpl-ii` | `muon_flux` | new | 3.03 × 10⁻¹⁰ cm⁻² s⁻¹ (± 0.24 stat., ± 0.18 syst.) | verified | https://arxiv.org/abs/2511.11050 | "The cosmic-ray muon flux is determined to be (3.03 ± 0.24 (stat) ± 0.18 (sys)) × 10−10 cm−2 s−1" | Abstract and Sec. 3, arXiv:2511.11050 |
| `site:cjpl-ii` | `depth_mwe` | replaced (was ~2100 m.w.e.) | ~6720 m.w.e. | derived | https://arxiv.org/abs/1404.2651, https://arxiv.org/abs/1305.0899, https://arxiv.org/abs/2511.11050 | "corresponds to the water equivalent depth of 6,720 m (assuming a rock density of 2.8 g/m 3)" | Sec. 2, Physics Procedia (2014), arXiv:1404.2651 |
| `site:cjpl-ii` | `depth` | replaced (was 2100 m rock overburden) | ~2400 m of vertical rock | verified | https://arxiv.org/abs/2511.11050, https://arxiv.org/abs/1801.00587 | "is shielded by approximately 2,400 m of vertical rock coverage" | Sec. 1, arXiv:2511.11050; Table I of arXiv:1801.00587 gives CJPL-II 2,400 m |
| `site:lsm-frejus` | `muon_flux` | new | 5.4 m⁻² d⁻¹ (± 0.2 stat., +0.5 −0.9 syst.) | verified | https://arxiv.org/abs/1302.7112, https://arxiv.org/abs/1102.0208, https://arxiv.org/abs/astro-ph/0512125 | "Souterrain de Modane (LSM) was measured to be Φµ = (5.4 ± 0.2+0.5 −0.9 ) muons/m /d" | Abstract and Sec. 3.6, Astropart. Phys. 44 (2013) 28 (arXiv:1302.7112) |
| `site:lsm-frejus` | `depth_mwe` | new | 4800 m.w.e. (average) | verified | https://arxiv.org/abs/1302.7112, https://arxiv.org/abs/1102.0208 | "an average rock overburden of 4800 m w. e. (meters water equivalent)" | Sec. 2, Astropart. Phys. 44 (2013) 28 (arXiv:1302.7112) |
| `site:boulby-mine` | `muon_flux` | new | 4.09 × 10⁻⁸ cm⁻² s⁻¹ (± 0.15) | verified | https://arxiv.org/abs/hep-ex/0306014, https://arxiv.org/abs/1102.0208, https://arxiv.org/abs/astro-ph/0512125, https://arxiv.org/abs/2406.10339 | "The muon flux in the laboratory is found to be (4.09±0.15)×10−8 cm−2 s−1" | Abstract and Sec. 4, Nucl. Instrum. Meth. A 511 (2003) 347 (hep-ex/0306014) |
| `site:boulby-mine` | `depth_mwe` | new | 2805 ± 45 m.w.e. | verified | https://arxiv.org/abs/hep-ex/0306014, https://arxiv.org/abs/1102.0208, https://arxiv.org/abs/astro-ph/0512125 | "This shows an effective vertical depth of 2805±45 metres of water equivalent" | Sec. 4 and Conclusions, Nucl. Instrum. Meth. A 511 (2003) 347 (hep-ex/0306014) |
| `site:lsc-canfranc` | `muon_flux` | new | 5.26 × 10⁻³ m⁻² s⁻¹ (± 0.21) | verified | https://arxiv.org/abs/1902.00868, https://arxiv.org/abs/1102.0208 | "The measured integrated muon flux is (5.26 ± 0.21) × 10−3 m−2 s−1 in the Hall A of the LAB2400" | Abstract and Sec. 3, Eur. Phys. J. C 79 (2019) 721 (arXiv:1902.00868) |
| `site:lsc-canfranc` | `depth_mwe` | new | 2450 m.w.e. (Hall B) | verified | https://arxiv.org/abs/1710.03837, https://arxiv.org/abs/1102.0208 | "The hut housing the experiment is at the hall B of LSC under 2450 m.w.e." | Sec. 1, ANAIS-112 (arXiv:1710.03837) |
| `site:wipp-surface-campus` | `muon_flux` | new | 4.77 × 10⁻⁷ cm⁻² s⁻¹ (+0.08 −0.10) | verified | https://arxiv.org/abs/astro-ph/0408486, https://arxiv.org/abs/astro-ph/0512125, https://arxiv.org/abs/2406.10339 | "WIPP (4.77±0.09) × 10−7 [6] 1.585±0.011" | Esch et al. 2005, Sec. 3.2, Eq. (9); Mei & Hime 2006, Table I (WIPP row) |
| `site:wipp-surface-campus` | `depth_mwe` | note and sources extended | 1585 m.w.e. | verified | https://arxiv.org/abs/1202.2192, https://arxiv.org/abs/astro-ph/0408486 | "EXO-200 is located at a depth of 1585 m water equivalent ... in the Waste Isolation Pilot Plant (WIPP) near Carlsbad, New Mexico" | The EXO-200 detector, part I: Detector design and construction (arXiv:1202.2192), site description |
| `site:soudan-minos-far-detector` | `muon_flux` | new | 1.65 × 10⁻⁷ cm⁻² s⁻¹ (± 0.02 stat., ± 0.1 syst.), E > 1 GeV | verified | https://arxiv.org/abs/1407.3246, https://arxiv.org/abs/astro-ph/0512125, https://arxiv.org/abs/2406.10339 | "The muon flux is found to be (1.65 ± 0.02(sta.) ± 0.1(sys.)) × 10−7 cm−2 s−1 (Eµ > 1 GeV)" | Abstract and Sec. on muon measurements at Soudan Mine, Phys. Rev. D 90, 122003 (arXiv:1407.3246) |
| `site:baksan-sage-underground-lab` | `muon_flux` | new | 3.03 × 10⁻⁹ cm⁻² s⁻¹ (± 0.10) | verified | https://arxiv.org/abs/0901.2200, https://arxiv.org/abs/1102.0208 | "The rock overburden is equivalent to 4700 m of water and the measured muon flux at the location of the experiment is (3.03±0.10)×10−9 /(cm2 s)." | Sec. II.A (Overview), SAGE collaboration, arXiv:0901.2200 |
| `site:juno-jiangmen-underground-lab` | `muon_flux` | new | 0.004 m⁻² s⁻¹ (simulated) | approximate | https://arxiv.org/abs/2104.02565 | "The muon rate and average energy in the JUNO detector are 0.004 Hz/m2 and 207 GeV estimated by simulation, taking the surveyed mountain profile into account." | Sec. 1.2 (JUNO site), JUNO Collaboration, arXiv:2104.02565 |

New source records (18, all `arxiv`, `full_text`, accessed 2026-10-26; ids start `src:ug-`):
`src:ug-anais-112-lsc-2017`, `src:ug-borexino-jcap-2012-muon-flux`, `src:ug-borexino-jcap-2019-muon-modulation`, `src:ug-boulby-muon-flux-2003`, `src:ug-cjpl-ii-muon-flux-2025`, `src:ug-cjpl-muon-telescope-2013`, `src:ug-deap3600-muon-flux-snolab-2026`, `src:ug-edelweiss-muon-background-2013`, `src:ug-esch-wipp-muon-flux-2005`, `src:ug-jne-cjpl-muon-flux-2021`, `src:ug-kamland-spallation-prc-2010`, `src:ug-lvd-prd-2019-muon-flux`, `src:ug-majorana-davis-muon-flux-2017`, `src:ug-mei-hime-2006`, `src:ug-sno-muon-flux-prd-2009`, `src:ug-trzaska-canfranc-muon-flux-2019`, `src:ug-woodley-mute-2024`, `src:ug-zhang-mei-soudan-2014`.

Existing sources reused: `src:lz-muon-flux-2026`, `src:geo-surf-heise-2026-review`, `src:geo-euro-ug-pandola-2011`,
`src:rf09-sage-iii-arxiv`, `src:hk-design-report-2018`, `src:juno-physics-detector-arxiv-2021`,
`src:cjpl-arxiv-phase2-2014`, `src:cjpl-arxiv-early-science-2018`.

**Corrected source record:** `src:cjpl-arxiv-phase2-2014` carried an excerpt ("CJPL-I rock overburden 2400 m (2400
m.w.e.); CJPL-II rock overburden 2100 m (2100 m.w.e.)") that the paper does not contain. It said `summary`
retrieval. Read in full today: it gives about 2,400 m of vertical rock for the middle of the tunnels, "overburdens
of about 2.4 km of rock" for the new halls, and a water-equivalent depth of 6,720 m. Excerpt rewritten from the text,
`retrieval` now `full_text`.

Prose repaired because it repeated the wrong numbers: `summary.technical` of `site:cjpl-i` and `site:cjpl-ii`.
The note on `site:kamioka-kamland` (Wikipedia's "105 m.w.e.") now points at the KamLAND paper that fills the field.

## 4. Conflicts (claim / source A / source B / chosen / why)

| Claim | Source A | Source B | Chosen | Why |
| --- | --- | --- | --- | --- |
| CJPL-I water-equivalent depth | earlier record: 2400 m.w.e. (credited to arXiv:1404.2651 summary) | Wu et al. 2013 and arXiv:1404.2651 text: 6720 m.w.e. (2.8 g/cm^3 x 2400 m) | 6720 | the record repeated the rock thickness in metres; both papers read in full say 6720. Woodley 2024 infers 6.20 ± 0.13 km.w.e. from the flux; noted, not used |
| CJPL-II rock depth and m.w.e. | earlier record: 2100 m, 2100 m.w.e. | arXiv:2511.11050: about 2,400 m of vertical rock; arXiv:1801.00587 Table I: 2,400 m; arXiv:1404.2651: about 2.4 km | 2400 m; 6720 m.w.e. `derived` | 2100 appears in no paper read. Another stream's notes (`maps/cjpl.json`, `geometry/cjpl-ii-point.json`) say the site "carries 2100 m"; that is now corrected |
| CJPL-I muon flux | Wu et al. 2013: (2.0 ± 0.4) x 10^-10 (plastic telescope, no angular correction) | JNE 2021: (3.53 ± 0.22 ± 0.07) x 10^-10, called the efficiency-corrected value by the 2025 CJPL-II paper | JNE | the 2018 CJPL review still tabulates the old one (0.17 per m^2 per day); the later papers of the same group supersede it |
| SNOLAB muon flux | SNO 2009: (3.31 ± 0.01 ± 0.09) x 10^-10 | DEAP-3600 2026: (3.71 ± 0.25 ± 0.09) x 10^-10 (Cube Hall), 1.4 sigma apart | SNO | far smaller error; DEAP in notes |
| SNOLAB m.w.e. | NIM 2000: about 6000 (kept) | PRD 2009: 5890 ± 94; Mei & Hime: 6.011 ± 0.1 km.w.e. | 6000 kept | agree within about 2%; invisible on a log axis. DEAP-3600 prints "(5.89 ± 0.94) km.w.e.", an apparent slip for ± 94 m; not used |
| LNGS depth | LNGS-wide average 3800 m.w.e. (Pandola; Borexino) | LVD: "minimal depth of 3100 m w.e."; MACRO: 3700 hg/cm^2 for Hall B; Mei & Hime flat-equivalent 2.96-3.1 km.w.e. | 3800 on all three halls | the only figure stated for the laboratory; the halls are 80 m apart. LNGS web pages give 1400 m of rock and no m.w.e. |
| LNGS Hall A flux | LVD 2019: 3.35 ± 0.0005 ± 0.03 (1994-2017) | LVD 2001-2008: 3.31 ± 0.03; LVD 1992-2016: 3.3332 ± 0.0005; GERDA: 3.47 ± 0.07 (all 10^-4 m^-2 s^-1) | LVD 2019 | the longest LVD data set, with a systematic error |
| Borexino error | abstract: ± 0.003 | text: ± 0.001 | ± 0.003 | the abstract's is the total quoted by Woodley 2024 |
| Soudan muon flux | Zhang & Mei 2014: 1.65 x 10^-7 (E > 1 GeV) | MINOS far detector: 1.77 x 10^-7 (as quoted); Mei & Hime: (2.0 ± 0.2) x 10^-7 (thesis) | Zhang & Mei | the only peer-reviewed measurement Woodley 2024 knows; others in notes |
| WIPP m.w.e. | 1585 (EXO-200 design paper) | 1624 (+22/-21) (later EXO-200 paper, noted earlier by another stream, not re-read) | 1585 | Esch et al. 2005 independently give 1585 (+11/-6) |
| SURF flux | LZ 2026: 5.09 ± 0.08 ± 0.10 (top of Davis cavern) | Majorana 2017: 5.31 ± 0.17 (nearby cavern); vertical intensity 5.38 x 10^-9 cm^-2 s^-1 sr^-1 (1983) | LZ | newest, smallest error; the vertical intensity is not a flux |
| Kamioka flux | KamLAND 2010: 5.37 ± 0.41 m^-2 h^-1 = 1.49 x 10^-7 | an earlier KamLAND report (via Mei & Hime): 1.58 ± 0.21 x 10^-7; Hyper-K design report, MUSIC: 1.54 x 10^-7 at Super-K | KamLAND 2010 | a measurement beats a calculation, and the newer beats the older |
| LSM flux | EDELWEISS 2013: 5.4 m^-2 d^-1 (horizontal surface) | Fréjus 1989 via Pandola: 5.76 x 10^-5 m^-2 s^-1 (about 5 per m^2 per day); via Mei & Hime: 5.47 x 10^-9 cm^-2 s^-1 | EDELWEISS | newest, and it states the surface definition |
| LSM rock depth | site record: 1700 m | EDELWEISS: 1800 m at zero degrees | 1700 kept | different convention (average vs vertical); only noted |
| Canfranc m.w.e. | ANAIS-112 (Hall B): 2450 | Pandola: about 2400 (maximum, new lab) | 2450 | an explicit hall; flux is from Hall A, said in the note |
| Boulby m.w.e. | Robinson 2003: 2805 ± 45 effective vertical depth | Pandola: 2850 minimum, 3450 average | 2805 | the figure paired with the measured flux |
| Baksan m.w.e. | SAGE 1999 and 2009: 4700 | Pandola: 4800 vertical depth | 4700 kept | two SAGE papers; the review differs by 2% |
| JUNO | yellow book 2015: 0.0030 Hz/m^2, 215 GeV | 2021 paper: 0.004 Hz/m^2, 207 GeV; 2025 spallation study: 5.0 x 10^-7 cm^-2 s^-1 (search snippet, not read) | 0.004 | the collaboration's current figure, after the hall moved 60 m |

## 5. Unresolved

* **No muon flux recorded for:** `site:kamioka-mozumi-mine-super-kamiokande` (no measurement; the only number is the
  Hyper-K design report's MUSIC calculation, 1.54 x 10^-7 cm^-2 s^-1, referred to in the KamLAND note),
  `site:kamioka-hyper-kamiokande-tochibora` (calculated 7.55 x 10^-7 at a basing point 600 m deep, about 20% uncertain),
  `site:surf-4850-level-dune-far-detector` (no measurement in the far-detector caverns).
* **JUNO has no measured flux.** The simulated 0.004 Hz/m^2 stands in; a measurement from the 2025-2026 data would
  replace it. No JUNO paper read reports one.
* **Hall B (MACRO)** rests on a quotation: MACRO's own paper (Phys. Rev. D 52, 3793, 1995) is not on arXiv and was not
  read. **Baksan's** original is an INR report of 1991 that Pandola cites; the SAGE paper's own number is used.
* **LNGS and Canfranc depth per hall** is not published; the lab-wide figure is used and flagged.
* **SNOLAB's own pages** (`snolab.ca`) returned 404 or no text from this machine, so no official m.w.e. figure was
  checked; the SNO papers carry it.
* The LSC and LNGS web pages give no m.w.e. and no muon flux.
* The 29 written values were read from arXiv PDF text, not from the journal versions. If a journal version differs
  from the arXiv text, the journal wins; none was checked.

## 6. Considered and excluded; for the integrator

* **Underground sites of non-laboratory facilities were left alone:** Daya Bay halls, RENO near and far, Double Chooz
  near and far (`depth_mwe` 300 already present), the CERN caverns, the J-PARC near-detector pit, ORNL SNS neutrino
  alley. They are `setting: underground` but are reactor sites, collider caverns or beamline pits, not laboratories.
  The Daya Bay record covers several halls, so a hall would have to be named if it were ever filled.
* **Not in the Atlas, so not created (belong to another stream):** Y2L (COSINE-100; Woodley et al. 2024 Table III lists
  (3.795 ± 0.110) x 10^-7 and (4.459 ± 0.132) x 10^-7 cm^-2 s^-1), Yemilab, SUPL (SABRE South; (3.65 ± 0.41) x 10^-8
  cm^-2 s^-1 in the same table), and, as leads only, Pyhasalmi (a row of Pandola 2011 Table 1) and SURF's 800L, 2000L and 7400L levels
  (the 2026 SURF review says 7400L is expected to have a flux more than 30 times lower than 4850L). All Table III
  numbers are second-hand: the primary papers were not read.
* **Stale notes in other streams' files** (not edited): `data/atlas/maps/cjpl.json` and
  `data/atlas/geometry/cjpl-ii-point.json` say the CJPL-II site "carries 2100 m"; after this branch it carries 2400 m.
  `site:juno-jiangmen-underground-lab` still shows the CDR's 700 m rock; the 2021 paper gives 693.35 m to the detector
  centre (the geometry stream already uses it).
* **Merge note:** `RELEASE_GEOMETRY_underground.md` proposes a coordinate correction for the same JUNO site file that
  gains `muon_flux` here; both are small key changes in a key-sorted file.

## 7. Checks run

* `python -m hepgraph.atlas.validate`: 0 errors, 1596 warnings, 4 informational (the same warning count as the
  branch point; none from this work). A deliberately wrong flux (3.03e-14) was rejected with `plausibility-range`
  and `display-value-mismatch`, then restored.
* `python -m hepgraph.atlas.build`: wrote 81 files; `muon_flux` present on 15 sites in `atlas.json`;
  `static/atlas/generated` restored with `git checkout` before committing.
* `pytest`: the new tests `test_a27_muon_flux_units_and_range` and
  `test_a27_site_muon_flux_reaches_the_bundle_and_its_provenance` pass; full suite 691 passed, 139 skipped
  (PostgreSQL-backed tests skip without a throwaway database).
* Every quote was matched against the extracted PDF text by script. Two extraction artefacts are noted on the
  values: the EDELWEISS quote has lost the superscript of m^2, and Esch et al.'s equation is jumbled in the extracted
  text, which is why the WIPP quote is the Mei & Hime table row.
