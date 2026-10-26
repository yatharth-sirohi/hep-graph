# Release notation stream (2026-10-25)

Branch `atlas-release-notation`. Display strings in `data/atlas/` that still used ASCII physics notation (`cm^-2 s^-1`, `GeV/c^2`, `+/-`, `nu_mu`, `theta_13`, `sqrt(s)`, `e+e-`, `1e34`, `x 10^-3`, ...) were rewritten in Unicode (`cm⁻² s⁻¹`, `GeV/c²`, `±`, `νμ`, `θ₁₃`, `√s`, `e⁺e⁻`, `10³⁴`, `× 10⁻³`, ...). Notation only: no number, sign, unit dimension or meaning changed.

## Result

- 425 strings changed in 222 files (all under `data/atlas/`; nothing in `sources/`, `geometry/`, `maps/`, `static/`, `hepgraph/`, `tests/`).
- `python -m hepgraph.atlas.validate`: 0 errors, 1594 warnings, 4 informational, identical to before the stream (the one warning whose text quotes a changed `display` string, `experiments/damic.json/key_specs/0/quantity/display`, now shows `7 × 16-Mpixel` instead of `7 x 16-Mpixel`).
- `python scripts/atlas_quote_check.py` against the cached sources: before and after are identical, per item (class, quote text and flags compared for all 4186 quote objects): verbatim 3674, segments 307, near 3, missing 1, unfetchable 6, skipped 195, number flags 29. No quote, excerpt, locator, source title, URL, id, numeric `value`/`min`/`max`/`unit`, date or key was edited (checked structurally against `HEAD`: the only differences are the listed strings, three added aliases, and nothing else; JSON key sets and array lengths are unchanged apart from those aliases).
- Files were edited in place, string literal by string literal, so every other byte is unchanged (53 of the 1287 entity files do not use sorted keys and would have been re-serialised by a normal JSON dump).
- `static/atlas/generated` was not touched (no build was run).

### Strings changed, by field type

| Field type | Strings |
| --- | ---: |
| summary.technical | 165 |
| provenance note | 45 |
| physics_goals / unique_capabilities | 41 |
| key_value_text.value | 31 |
| quantity display | 28 |
| key_value.display | 27 |
| energy_regime / technology / subsystems / spec text | 25 |
| topic text | 22 |
| notes[] | 17 |
| why_it_matters | 8 |
| summary.plain | 5 |
| name | 4 |
| significance | 4 |
| interval label | 3 |
| **total** | **425** |

Field types: `summary.*`, `why_it_matters`, `significance.*`, `key_value.display`, `key_value_text.value`, `...display` (spec and key-spec quantities), `physics_goals` / `unique_capabilities` / `energy_regime` / `technology` / `subsystems` / spec text values, topic texts (`observables`, `overview`, `question`), `notes[]` (Atlas-written record notes), `...note` (Atlas-written provenance notes), interval `label`, entity `name`.

## Names and aliases

Four entity names changed. The old form is added to `aliases` where the validator allows it (A20 forbids an alias whose normalised form equals the record's own name):

- `results/alice-jpsi-suppression-pbpb-2012.json`: old name "J/psi suppression at forward rapidity in Pb-Pb collisions at 2.76 TeV" added to `aliases`.
- `results/cdf-top-quark-observation-1995.json`: old name "Observation of Top Quark Production in ppbar Collisions with the Collider Detector at Fermilab" added to `aliases`.
- `results/lhcb-doubly-charmed-baryon-observation-2017.json`: old name "Observation of the doubly charmed baryon Xi_cc++" added to `aliases`.
- `results/sno-cc-evidence-2001.json`: old name "Measurement of the rate of ν_e+d→p+p+e− interactions produced by 8B solar neutrinos at the Sudbury Neutrino Observatory" NOT added: normalises equal to new name (validator forbids alias-equals-name; search already matches).

## One hand edit

`results/cdf-top-quark-observation-1995.json` `/notes/1` ended "(rendered here with the repository's ASCII "ppbar" convention)". With the name now `pp̄` that clause would have been false, so it now reads "(rendered here in Unicode notation as pp̄; the ASCII form "ppbar" is kept as an alias)". The rest of the note (including the quoted old name and the quoted published title with `pbar-p`) is untouched.

## How it was done

A script (scratch: `scratchpad/notation/{common,rules,phrases,driver,apply,jspan}.py`; the rules and the field allow-list are reproduced in the appendix) with:
1. an **allow-list of display fields** (pointer regexes) — everything else is never read for rewriting;
2. **protected spans** that are never rewritten even inside an allowed field: `src:`/`result:`/... ids, `` `code` `` spans, URLs, and quoted text (`'...'`, `"..."`, curly quotes, 8+ characters), which in notes is a verbatim source title or quote;
3. an **ordered rule list** for the unambiguous cases (exponents, `±`, `×`, `√`, `νx`/`ν̄x`, `θ₁₃`, `sin²2θ₁₃`, `Δm²`, `5 sigma` → `5σ`, `e⁺e⁻`, charges in decay processes, arrows) and an exact-phrase table for the ambiguous ones (the `D0` meson vs the D0 experiment, `tau tau` vs "tau neutrino", `gamma gamma` vs "gamma ray", ...);
4. a byte-preserving JSON editor (positions of string literals, not a re-dump) with a post-write structural check;
5. a hand review of every changed string, old → new (below). The review found and fixed one real bug in an earlier draft of the phrase table ("lepton nu" also matched "lepton number" and produced "lepton νmber"); phrase literals now carry word-boundary guards.

### Rules applied (strings touched)

| Rule | Strings |
| --- | ---: |
| exp | 175 |
| arrow | 48 |
| times-power-of-ten | 46 |
| e-notation | 36 |
| charge-plus | 29 |
| times-dimensions | 29 |
| plus-minus-slash | 27 |
| ee-charges | 21 |
| sigma-after-number | 20 |
| asym-err-slash | 20 |
| times-dimensions-unit | 19 |
| plus-minus-dash | 15 |
| nubar | 15 |
| nu-nubar | 15 |
| asym-err-compact | 14 |
| abs-eta | 10 |
| m3-after-number | 10 |
| theta-subscript-digits | 10 |
| nu-flavour | 9 |
| p-pbar | 8 |
| upsilon-4S | 7 |
| four-pi | 7 |
| pi0 | 7 |
| a-mu | 7 |
| delta-CP | 7 |
| jpsi | 7 |
| Z0 | 7 |
| sqrt | 6 |
| cm2-after-number | 5 |
| c2-units | 5 |
| charge-sequence | 5 |
| e+ gamma | 5 |
| nu-greek-underscore | 5 |
| mu- N -> e- N | 4 |
| epsilon-prime | 4 |
| Xi_cc++ unicode | 4 |
| pm-charge-sign | 4 |
| arrow-between-numbers | 3 |
| gamma gamma | 3 |
| nubar-flavour | 3 |
| tautau-charges | 3 |
| ppbar | 3 |
| W -> e nu | 3 |
| per-m3 | 2 |
| Ga(nu_e,e-)Ge | 2 |
| delta-m2 | 2 |
| eee-charges | 2 |
| dbar/ubar | 2 |
| sin2-theta-W | 2 |
| ttbar | 2 |
| asym-after-power | 2 |
| phi0 | 2 |
| ten-minus-exponent | 2 |
| unit-minus-exponent | 2 |
| Lambda_c+ | 2 |
| l+ l- | 2 |
| D0 to K | 2 |
| e-/e+ (hera note) | 1 |
| e- x e+ (pep-ii) | 1 |
| degrees-display | 1 |
| per-cm3 | 1 |
| nu_e + Cl -> Ar + e- (homestake note) | 1 |
| um x um | 1 |
| B0 system | 1 |
| B0-B0bar | 1 |
| B-Bbar (en dash) | 1 |
| long x 10 m | 1 |
| arrays x antennas (note) | 1 |
| Bs0->mu+mu- (note) | 1 |
| K0-K0bar | 1 |
| epsilon-power | 1 |
| eta-range | 1 |
| B-Bbar | 1 |
| e-p / e+p (zeus) | 1 |
| gamma-gamma | 1 |
| W -> lepton nu | 1 |
| B- -> tau- nu_tau-bar | 1 |
| arrow-long | 1 |
| phi-subscript-digit | 1 |
| B0->D- | 1 |
| D mu nu_mu | 1 |
| D0bar | 1 |
| delta-eta-phi | 1 |
| tau tau (final states) | 1 |
| W -> mu nu | 1 |
| theta-greek-W | 1 |
| spectral index gamma | 1 |
| gamma = 3.00 | 1 |
| D0->pi-pi+ | 1 |
| D0->K-K+ | 1 |
| Xi_cc++ (name) | 1 |
| Lambda_c+ K- pi+ pi+ | 1 |
| Lambda_b0 -> J/psi K- p | 1 |
| e+gamma | 1 |
| sin2-2theta-bare | 1 |
| delta_CP near pi/2 | 1 |
| arrow-double-ended | 1 |
| W -> e nu (pm) | 1 |
| ee-charges-unicode-minus | 1 |
| e-notation-paren | 1 |
| km2-after-number | 1 |
| alpha beta gamma | 1 |
| sin 2beta | 1 |
| B0 and Bs | 1 |
| Bs and B0 | 1 |
| K to pi pi | 1 |
| K to pi plus | 1 |
| D0 -> D0-bar | 1 |
| manual | 1 |

## Deliberately left alone

- **Quoted source text inside notes** (15 strings): e.g. `'Measurement of the branching ratio of the K+ -> pi+ nu nubar decay'`, `'greater than 1000 fb^-1'`, `"0.5%: best sensitivity to 130Te 0vbb (2x10^26 yr in 3 yrs)"`, `'The design luminosity of SuperKEKB is 8 x 10^35 /cm^2 /s ...'`. These reproduce what a source printed; changing them would misstate the source.
- **Prose words**, not notation: "gamma ray(s)" / "gamma-ray" (~66 strings), "tau neutrino" / "tau lepton" / "tau mass" (~55), "beta decay" / "beta spectrum" / "double beta" (~47), "alpha backgrounds" (2), "Lambda hyperon" (hypertriton), "(K0S, Lambda) ... (Xi, Omega)" in one ALICE summary, "sigma" used as a word with no number ("no sigma-level significance is reported", 14 strings), "Delta, Utah" (8: a town, not Δ).
- **Names that look like notation**: the D0 experiment/collaboration/detector/hall (23 strings), the CDF "B0" hall (7), "DMRadio-m3", "nu-cleus" (the NUCLEUS experiment's original name, 5), "cosmic-gamma" (a workstream name), "MS-bar".
- **Editorial arrows and inequalities in provenance notes**: `status corrected 'active' -> 'shutdown'`, `lineage: predecessor -> CUPID`, `Expression of Interest -> Letter of Intent -> ...` (12 strings) and `rank <= 10` / `rank<=7` (30 strings). They describe the data, not physics; arrows are converted only in display fields.
- **Letter subscripts written with an underscore**: `K_S`, `K_L`, `m_top`, `m_t`, `A_LR`, `ΔA_CP`, `y_CP`, `f_B`, `R_AA`, `GW_th`, `χ_c1`, `η_c`, `Δm²_ee`, `|U_e4|²`, `B_2016-2024` (29 strings). Unicode has no subscript for most of these letters and the repository already writes them this way. (Only digit subscripts were converted: `θ_13` → `θ₁₃`; and Greek+flavour pairs were written without the underscore: `ν_μ` → `νμ`, `θ_W` → `θW`, `δ_CP` → `δCP`, `a_μ` → `aμ`.)
- **`φ^CC(νe)`** in the SNO charged-current result (2 strings): there is no usable Unicode superscript "CC", so the caret stays; the `ν_e` and the units in the same strings were converted.
- **Isotopes** (`130Te`, `37Ar`, `71Ga(νe,e⁻)71Ge`) and **chemical formulas** (`TeO2`, `CaWO4`, `CH4`): not in the request and ambiguous to rewrite mechanically.
- **Hyphen-minus on negative numbers** (`-15.4`, `[-1.38π, 0.30π]`, `-0.159`): only the minus of asymmetric errors (`+0.5/-0.4` → `+0.5/−0.4`) and of exponents was typed as `−`/`⁻`; a leading minus was not touched.
- **Degrees in coordinate notes** (`42 deg 48 min N`, 5 notes): these restate a source's DMS wording; only the display value `2.504 ± 0.004°` was converted. Spelled-out "degrees"/"degree" (e.g. "2.5 degrees off-axis") is English, left as is.
- **Result `title` fields (18 results; the record panel heading and result lists read `result.title`)** still carry ASCII (`sqrt(s)=13 TeV`, `J/psi`, `10^...`, `K+ -> pi+ nu nubar`, `mu+ -> e+ gamma`, `ppbar`, `Z0 -> e+ e-`): the ontology defines `title` as the collaboration's own wording, i.e. a verbatim copy of the cited paper's title, which this stream's rules put out of scope together with source titles. The Unicode `name` of the same records is already clean (and is what search and several lists show). Decision for the release owner whether the panel heading should show `name` or `title` instead: `alice-jpsi-suppression-pbpb-2012`, `atlas-hbb-observation-2018`, `atlas-htautau-observation-2018`, `atlas-squark-gluino-limit-2020`, `atlas-topmass-measurement-2018`, `atlas-wmass-measurement-2017`, `cdf-top-quark-observation-1995`, `cms-high-mass-dilepton-search-2021`, `cms-lhcb-bs-to-mumu-observation-2015` (LaTeX `$B^0_s\to\mu^+\mu^-$`), `cms-top-quark-mass-measurement-2023`, `meg-ii-mu-to-e-gamma-limit-2024`, `meg-mu-to-e-gamma-limit-2016`, `na62-2026-refined-measurement`, `na62-jhep-2021-measurement`, `na62-jhep-2025-observation`, `ua1-w-boson-observation-1983`, `ua1-z-boson-observation-1983`, `ua2-z-boson-evidence-1983`.
- **`unit` fields** (`km^2`, `cm^-2 s^-1`, `TeV/c^2`, `fb^-1`, ...), **`aliases`** (ASCII forms are what a search user types), **`coverage/`** workstream notes, **`geometry/`** and **`sources/`**: out of scope by rule.

## Every changed string (file, pointer, old → new)


### data/atlas/accelerators/hera.json

- `/notes/0` (notes[])
  - old: 2026-09-17: added `specs.beam_energy` (27.5 GeV, e-/e+) and `specs.proton_energy` (920 GeV) using the existing Wikipedia citation plus an independently fetched DESY-hosted page (desy.de/~ameyer/hq/node16.html, a physicist's teaching notes on the desy.de domain, treated as `secondary` rank 12 rather than `official_facility_site` since it is not DESY's own institutional page). Both agree on 27.5/920 GeV and on the 320 GeV cms energy already recorded; confidence stays `uncertain` because no source of rank <= 10 has been fetched for these two numbers specifically.
  - new: 2026-09-17: added `specs.beam_energy` (27.5 GeV, e⁻/e⁺) and `specs.proton_energy` (920 GeV) using the existing Wikipedia citation plus an independently fetched DESY-hosted page (desy.de/~ameyer/hq/node16.html, a physicist's teaching notes on the desy.de domain, treated as `secondary` rank 12 rather than `official_facility_site` since it is not DESY's own institutional page). Both agree on 27.5/920 GeV and on the 320 GeV cms energy already recorded; confidence stays `uncertain` because no source of rank <= 10 has been fetched for these two numbers specifically.

### data/atlas/accelerators/kekb.json

- `/specs/integrated_luminosity/note` (provenance note)
  - old: Lower bound delivered/recorded over the whole KEKB programme; the legacy Belle page states 'greater than 1000 fb^-1', i.e. about 1 ab^-1.
  - new: Lower bound delivered/recorded over the whole KEKB programme; the legacy Belle page states 'greater than 1000 fb^-1', i.e. about 1 ab⁻¹.
- `/summary/technical` (summary.technical)
  - old: Asymmetric-energy e+e- double-ring collider (8 GeV HER × 3.5 GeV LER) operating on the Υ(4S) resonance, 3 km circumference; peak luminosity 2.11×10³⁴ cm⁻² s⁻¹ with crab cavities, more than 1 ab⁻¹ integrated.
  - new: Asymmetric-energy e⁺e⁻ double-ring collider (8 GeV HER × 3.5 GeV LER) operating on the Υ(4S) resonance, 3 km circumference; peak luminosity 2.11×10³⁴ cm⁻² s⁻¹ with crab cavities, more than 1 ab⁻¹ integrated.

### data/atlas/accelerators/lep.json

- `/summary/technical` (summary.technical)
  - old: 27 km e+e- storage-ring collider with four experiments (ALEPH, DELPHI, L3, OPAL). LEP1 ran at the Z pole (~91 GeV cms); after the 1995 upgrade LEP2 reached 209 GeV cms in 2000. Closed 2 November 2000; its tunnel now houses the LHC.
  - new: 27 km e⁺e⁻ storage-ring collider with four experiments (ALEPH, DELPHI, L3, OPAL). LEP1 ran at the Z pole (~91 GeV cms); after the 1995 upgrade LEP2 reached 209 GeV cms in 2000. Closed 2 November 2000; its tunnel now houses the LHC.

### data/atlas/accelerators/lhc.json

- `/specs/peak_luminosity/display` (quantity display)
  - old: 2 x 10^34 cm^-2 s^-1
  - new: 2 × 10³⁴ cm⁻² s⁻¹
- `/specs/peak_luminosity/note` (provenance note)
  - old: Routinely achieved start-of-fill luminosity in Run 2; the design value is 1e34 cm^-2 s^-1 (2008 JINST 3 S08003, chapter 1).
  - new: Routinely achieved start-of-fill luminosity in Run 2; the design value is 10³⁴ cm⁻² s⁻¹ (2008 JINST 3 S08003, chapter 1).
- `/summary/technical` (summary.technical)
  - old: Superconducting proton-proton (and heavy-ion) collider of 26 659 m circumference in the former LEP tunnel; 1232 main dipoles at 1.9 K; design 7 TeV/beam (14 TeV cms) at 1e34 cm^-2 s^-1; ran at 3.5-4 TeV/beam in Run 1, 6.5 TeV/beam in Run 2 and 6.8 TeV/beam in Run 3.
  - new: Superconducting proton-proton (and heavy-ion) collider of 26 659 m circumference in the former LEP tunnel; 1232 main dipoles at 1.9 K; design 7 TeV/beam (14 TeV cms) at 10³⁴ cm⁻² s⁻¹; ran at 3.5-4 TeV/beam in Run 1, 6.5 TeV/beam in Run 2 and 6.8 TeV/beam in Run 3.

### data/atlas/accelerators/pep-ii.json

- `/specs/cms_energy/display` (quantity display)
  - old: 10.58 GeV (Upsilon(4S) resonance)
  - new: 10.58 GeV (Υ(4S) resonance)
- `/specs/cms_energy/note` (provenance note)
  - old: Design centre-of-mass energy (mass of the Upsilon(4S)). The introduction of the same paper (arXiv:hep-ex/0105044) gives the beam energies as 9.0 GeV (electrons) and 3.1 GeV (positrons).
  - new: Design centre-of-mass energy (mass of the Υ(4S)). The introduction of the same paper (arXiv:hep-ex/0105044) gives the beam energies as 9.0 GeV (electrons) and 3.1 GeV (positrons).
- `/summary/technical` (summary.technical)
  - old: PEP-II B-factory: an asymmetric-energy electron-positron collider at SLAC (9 GeV e- x 3.1 GeV e+, cms 10.58 GeV, tuned to the Upsilon(4S) resonance), 2.2 km circumference, feeding the BaBar detector, 1999-2008.
  - new: PEP-II B-factory: an asymmetric-energy electron-positron collider at SLAC (9 GeV e⁻ × 3.1 GeV e⁺, cms 10.58 GeV, tuned to the Υ(4S) resonance), 2.2 km circumference, feeding the BaBar detector, 1999-2008.

### data/atlas/accelerators/slc.json

- `/specs/cms_energy/note` (provenance note)
  - old: Luminosity-weighted mean e+e- centre-of-mass energy measured by the SLD at the SLC: 91.26 +- 0.03 GeV (1996 run) and 91.237 +- 0.029 GeV (1997-98 run, calibrated to the Z mass). The recorded value 91 GeV is these figures rounded to the nearest GeV (approx flag set); the collider ran at the Z resonance. The earlier Wikipedia wording (about 90 GeV) is not used.
  - new: Luminosity-weighted mean e⁺e⁻ centre-of-mass energy measured by the SLD at the SLC: 91.26 ± 0.03 GeV (1996 run) and 91.237 ± 0.029 GeV (1997-98 run, calibrated to the Z mass). The recorded value 91 GeV is these figures rounded to the nearest GeV (approx flag set); the collider ran at the Z resonance. The earlier Wikipedia wording (about 90 GeV) is not used.

### data/atlas/accelerators/sns.json

- `/intervals/1/label` (interval label)
  - old: Proton Power Upgrade (1.4 -> 2.8 MW)
  - new: Proton Power Upgrade (1.4 → 2.8 MW)

### data/atlas/accelerators/superkekb.json

- `/summary/technical` (summary.technical)
  - old: Asymmetric e+e- double-ring collider, 7 GeV HER × 4 GeV LER at √s = 10.579 GeV, 3 km circumference, using the nano-beam scheme with a large crossing angle; target luminosity 6×10³⁵ cm⁻² s⁻¹ (originally 8×10³⁵), peak achieved 5.319×10³⁴ cm⁻² s⁻¹ on 30 June 2026.
  - new: Asymmetric e⁺e⁻ double-ring collider, 7 GeV HER × 4 GeV LER at √s = 10.579 GeV, 3 km circumference, using the nano-beam scheme with a large crossing angle; target luminosity 6×10³⁵ cm⁻² s⁻¹ (originally 8×10³⁵), peak achieved 5.319×10³⁴ cm⁻² s⁻¹ on 30 June 2026.

### data/atlas/beamlines/cngs.json

- `/summary/technical` (summary.technical)
  - old: CERN Super Proton Synchrotron protons directed onto a graphite target to produce a muon-neutrino beam aimed 732 km through the Earth's crust at LNGS; operated July 2006 to December 2012, providing the neutrino source for the OPERA experiment's nu_mu -> nu_tau appearance search.
  - new: CERN Super Proton Synchrotron protons directed onto a graphite target to produce a muon-neutrino beam aimed 732 km through the Earth's crust at LNGS; operated July 2006 to December 2012, providing the neutrino source for the OPERA experiment's νμ → ντ appearance search.

### data/atlas/beamlines/j-parc-neutrino.json

- `/baselines/0/distance/display` (quantity display)
  - old: 295,335.2 +- 0.7 m
  - new: 295,335.2 ± 0.7 m
- `/specs/off_axis_angle/display` (quantity display)
  - old: 2.504 +- 0.004 deg
  - new: 2.504 ± 0.004°
- `/target/value` (energy_regime / technology / subsystems / spec text)
  - old: Graphite rod, 91.4 cm long (1.9 interaction lengths), 2.6 cm diameter, 1.8 g/cm3, helium cooled, supported inside the first horn
  - new: Graphite rod, 91.4 cm long (1.9 interaction lengths), 2.6 cm diameter, 1.8 g/cm³, helium cooled, supported inside the first horn

### data/atlas/collaborations/opera.json

- `/summary/technical` (summary.technical)
  - old: Collaboration (140+ authors on its 2015 discovery paper) that built and operated the OPERA emulsion detector at LNGS Hall C on the CERN-to-Gran-Sasso (CNGS) neutrino beam from 2008 to 2012, reporting discovery of nu_mu -> nu_tau appearance at 5.1 sigma.
  - new: Collaboration (140+ authors on its 2015 discovery paper) that built and operated the OPERA emulsion detector at LNGS Hall C on the CERN-to-Gran-Sasso (CNGS) neutrino beam from 2008 to 2012, reporting discovery of νμ → ντ appearance at 5.1σ.

### data/atlas/detectors/aleph.json

- `/specs/tracker/value` (energy_regime / technology / subsystems / spec text)
  - old: Silicon-microstrip vertex detector (two double-sided layers), 8-coordinate inner drift chamber with trigger, and a 4.4 m x 3.6 m time projection chamber
  - new: Silicon-microstrip vertex detector (two double-sided layers), 8-coordinate inner drift chamber with trigger, and a 4.4 m × 3.6 m time projection chamber
- `/summary/technical` (summary.technical)
  - old: General-purpose LEP detector: silicon-microstrip vertex detector (two double-sided layers), an 8-coordinate inner drift chamber with trigger, a 4.4 m x 3.6 m time projection chamber, electromagnetic and hadron calorimeters, and a 6.3 m x 5.3 m superconducting coil providing a 1.5 T field.
  - new: General-purpose LEP detector: silicon-microstrip vertex detector (two double-sided layers), an 8-coordinate inner drift chamber with trigger, a 4.4 m × 3.6 m time projection chamber, electromagnetic and hadron calorimeters, and a 6.3 m × 5.3 m superconducting coil providing a 1.5 T field.

### data/atlas/detectors/alice.json

- `/specs/pseudorapidity_coverage/value` (energy_regime / technology / subsystems / spec text)
  - old: Central barrel |eta| < 0.9 (TPC/TOF; TRD |eta| < 0.84); forward muon spectrometer 2.5 < |eta| < 4.0 (polar angle 2-9 degrees)
  - new: Central barrel |η| < 0.9 (TPC/TOF; TRD |η| < 0.84); forward muon spectrometer 2.5 < |η| < 4.0 (polar angle 2-9 degrees)

### data/atlas/detectors/atlas.json

- `/specs/pseudorapidity_coverage/value` (energy_regime / technology / subsystems / spec text)
  - old: Precision tracking |eta| < 2.5; electromagnetic calorimetry |eta| < 3.2 extended to |eta| = 4.9 by the forward calorimeters; muon spectrometer |eta| < 2.7 (trigger 2.4)
  - new: Precision tracking |η| < 2.5; electromagnetic calorimetry |η| < 3.2 extended to |η| = 4.9 by the forward calorimeters; muon spectrometer |η| < 2.7 (trigger 2.4)
- `/specs/tracker/value` (energy_regime / technology / subsystems / spec text)
  - old: Silicon pixel detector (92 million pixels, innermost layer 3.3 cm from the beam), semiconductor tracker (about 4000 modules, 6 million silicon micro-strips over 60 m^2) and transition radiation tracker (300 000 thin-walled drift tubes)
  - new: Silicon pixel detector (92 million pixels, innermost layer 3.3 cm from the beam), semiconductor tracker (about 4000 modules, 6 million silicon micro-strips over 60 m²) and transition radiation tracker (300 000 thin-walled drift tubes)
- `/subsystems/0/description/value` (energy_regime / technology / subsystems / spec text)
  - old: Pixel detector, semiconductor tracker and transition radiation tracker inside the 2 T solenoid, reconstructing charged-particle tracks and vertices for |eta| < 2.5
  - new: Pixel detector, semiconductor tracker and transition radiation tracker inside the 2 T solenoid, reconstructing charged-particle tracks and vertices for |η| < 2.5
- `/summary/technical` (summary.technical)
  - old: General-purpose 4-pi collider detector: silicon pixel + SCT + TRT inner detector in a 2 T solenoid, liquid-argon EM and forward calorimetry, scintillator-tile hadronic calorimeter, and an air-core toroid muon spectrometer. Calorimetry to |eta| = 4.9, precision tracking to |eta| < 2.5, muon measurement to |eta| < 2.7.
  - new: General-purpose 4π collider detector: silicon pixel + SCT + TRT inner detector in a 2 T solenoid, liquid-argon EM and forward calorimetry, scintillator-tile hadronic calorimeter, and an air-core toroid muon spectrometer. Calorimetry to |η| = 4.9, precision tracking to |η| < 2.5, muon measurement to |η| < 2.7.
- `/technology/value` (energy_regime / technology / subsystems / spec text)
  - old: General-purpose 4-pi collider detector with a thin superconducting solenoid around the inner-detector cavity and three large superconducting air-core toroids around the calorimeters
  - new: General-purpose 4π collider detector with a thin superconducting solenoid around the inner-detector cavity and three large superconducting air-core toroids around the calorimeters

### data/atlas/detectors/borexino.json

- `/specs/target_mass/note` (provenance note)
  - old: 278 t is the active liquid-scintillator mass stated in the 2014 Nature pp-neutrino paper (Methods); Wikipedia's infobox gives the same figure with a 315 m3 volume.
  - new: 278 t is the active liquid-scintillator mass stated in the 2014 Nature pp-neutrino paper (Methods); Wikipedia's infobox gives the same figure with a 315 m³ volume.

### data/atlas/detectors/cms.json

- `/notes/1` (notes[])
  - old: ECAL crystal count, tracker silicon area in m^2 and the tracker |eta| acceptance were not obtained from a source fetched in this session and are therefore absent.
  - new: ECAL crystal count, tracker silicon area in m² and the tracker |η| acceptance were not obtained from a source fetched in this session and are therefore absent.

### data/atlas/detectors/coherent-cenns-10.json

- `/summary/technical` (summary.technical)
  - old: 22 kg liquid argon calorimeter (CENNS-10), operating in Neutrino Alley at the SNS since October 2016; produced the first CEvNS-on-argon measurement (2021, >3-sigma, two independent analyses).
  - new: 22 kg liquid argon calorimeter (CENNS-10), operating in Neutrino Alley at the SNS since October 2016; produced the first CEvNS-on-argon measurement (2021, >3σ, two independent analyses).

### data/atlas/detectors/coherent-csi.json

- `/summary/technical` (summary.technical)
  - old: 14.6 kg CsI[Na] scintillating crystal, low-background configuration, deployed in Neutrino Alley at the SNS; produced the 2017 first observation of CEvNS (6.7 sigma) and the 2022 cross-section measurement from the full dataset before decommissioning.
  - new: 14.6 kg CsI[Na] scintillating crystal, low-background configuration, deployed in Neutrino Alley at the SNS; produced the 2017 first observation of CEvNS (6.7σ) and the 2022 cross-section measurement from the full dataset before decommissioning.

### data/atlas/detectors/coherent-ge.json

- `/intervals/0/note` (provenance note)
  - old: The official detector-suite page describes an earlier, smaller planned array; it is not clear from fetched sources whether this is the same physical array later reported as Ge-Mini (8 x 2.2 kg = 17.6 kg) in the 2024 evidence paper, or a distinct earlier generation. Recorded as a separate, lower-confidence interval rather than merged with the sourced Ge-Mini figures.
  - new: The official detector-suite page describes an earlier, smaller planned array; it is not clear from fetched sources whether this is the same physical array later reported as Ge-Mini (8 × 2.2 kg = 17.6 kg) in the 2024 evidence paper, or a distinct earlier generation. Recorded as a separate, lower-confidence interval rather than merged with the sourced Ge-Mini figures.
- `/notes/1` (notes[])
  - old: Mass conflict: the official detector-suite page (undated, accessed 2026) describes a planned 10 kg array for 2020; the 2024 evidence paper (arXiv:2406.13806) describes an 8 x 2.2 kg = 17.6 kg array (Ge-Mini) operated June-August 2023, of which 5-7 detectors were stable enough for analysis. specs.target_mass below uses the Ge-Mini figure, which is the one that actually produced the sourced physics result; the 10 kg figure is recorded only in the interval note above.
  - new: Mass conflict: the official detector-suite page (undated, accessed 2026) describes a planned 10 kg array for 2020; the 2024 evidence paper (arXiv:2406.13806) describes an 8 × 2.2 kg = 17.6 kg array (Ge-Mini) operated June-August 2023, of which 5-7 detectors were stable enough for analysis. specs.target_mass below uses the Ge-Mini figure, which is the one that actually produced the sourced physics result; the 10 kg figure is recorded only in the interval note above.
- `/specs/target_mass/display` (quantity display)
  - old: 17.6 kg (8 x 2.2 kg)
  - new: 17.6 kg (8 × 2.2 kg)
- `/summary/technical` (summary.technical)
  - old: Ge-Mini: array of eight 2.2 kg inverted-coaxial point-contact (ICPC) high-purity germanium detectors, 1.5 keVee analysis threshold, operated at the SNS June-August 2023; yielded a 3.9-sigma rejection of the no-CEvNS hypothesis on natural germanium (2024).
  - new: Ge-Mini: array of eight 2.2 kg inverted-coaxial point-contact (ICPC) high-purity germanium detectors, 1.5 keVee analysis threshold, operated at the SNS June-August 2023; yielded a 3.9σ rejection of the no-CEvNS hypothesis on natural germanium (2024).

### data/atlas/detectors/conus-hpge-array.json

- `/specs/target_mass/display` (quantity display)
  - old: 4 kg (4 x 1 kg) nominal; 2.83 +/- 0.02 kg active at Leibstadt
  - new: 4 kg (4 × 1 kg) nominal; 2.83 ± 0.02 kg active at Leibstadt
- `/specs/target_mass/note` (provenance note)
  - old: Nominal array is four 1 kg point-contact HPGe detectors, reused at both sites. At Leibstadt only three of the four refurbished detectors were used in the Nov 2023-Jul 2024 analysis, giving an active mass of 2.83+/-0.02 kg; value/unit below record the original 4-detector nominal array mass.
  - new: Nominal array is four 1 kg point-contact HPGe detectors, reused at both sites. At Leibstadt only three of the four refurbished detectors were used in the Nov 2023-Jul 2024 analysis, giving an active mass of 2.83±0.02 kg; value/unit below record the original 4-detector nominal array mass.

### data/atlas/detectors/damic.json

- `/specs/ccd_mass/display` (quantity display)
  - old: ~42 g (7 x 6.0 g CCDs)
  - new: ~42 g (7 × 6.0 g CCDs)

### data/atlas/detectors/darkside-50.json

- `/specs/active_mass/note` (provenance note)
  - old: Nominal/design value; the first-results paper measured (46.4+-0.7) kg (arXiv:1410.0653).
  - new: Nominal/design value; the first-results paper measured (46.4±0.7) kg (arXiv:1410.0653).
- `/summary/technical` (summary.technical)
  - old: Dual-phase argon TPC, ~50 kg nominal active mass (46.4+-0.7 kg measured), surrounded by a 30 t liquid-scintillator neutron veto inside a 1 kt water-Cherenkov muon veto, in LNGS Hall C.
  - new: Dual-phase argon TPC, ~50 kg nominal active mass (46.4±0.7 kg measured), surrounded by a 30 t liquid-scintillator neutron veto inside a 1 kt water-Cherenkov muon veto, in LNGS Hall C.

### data/atlas/detectors/double-chooz.json

- `/placements/1/note` (provenance note)
  - old: Near detector construction/commissioning finished substantially later than the far detector. The collaboration's detector paper says data taking with the second (near) detector started at the end of 2014; Wikipedia says the beginning of 2015, and the 2019 Double Chooz theta13 paper uses two-detector data from January 2015, so the start is recorded as approximately December 2014.
  - new: Near detector construction/commissioning finished substantially later than the far detector. The collaboration's detector paper says data taking with the second (near) detector started at the end of 2014; Wikipedia says the beginning of 2015, and the 2019 Double Chooz θ₁₃ paper uses two-detector data from January 2015, so the start is recorded as approximately December 2014.
- `/specs/target_mass/display` (quantity display)
  - old: 10.3 m3 fiducial volume (~10 t)
  - new: 10.3 m³ fiducial volume (~10 t)
- `/specs/target_mass/note` (provenance note)
  - old: Recorded as an approximate mass equivalent of the stated fiducial volume (Gd-loaded liquid scintillator, density close to 1 t/m3); the paper itself gives volume, not mass, directly.
  - new: Recorded as an approximate mass equivalent of the stated fiducial volume (Gd-loaded liquid scintillator, density close to 1 t/m³); the paper itself gives volume, not mass, directly.
- `/summary/technical` (summary.technical)
  - old: Calorimetric Gd-loaded liquid-scintillator detectors (four concentric cylindrical vessels), ~10.3 m3 fiducial volume, at near (400 m, from the end of 2014) and far (1050 m, from the 2012 result onward) halls at the Chooz reactor site.
  - new: Calorimetric Gd-loaded liquid-scintillator detectors (four concentric cylindrical vessels), ~10.3 m³ fiducial volume, at near (400 m, from the end of 2014) and far (1050 m, from the 2012 result onward) halls at the Chooz reactor site.

### data/atlas/detectors/dune-far-detector-1.json

- `/summary/technical` (summary.technical)
  - old: Single-phase horizontal-drift LArTPC: 17.5 kt of liquid argon in a 15.1 x 14.0 x 62.0 m membrane cryostat, at least 10 kt fiducial, four drift volumes at 500 V/cm with a 3.5 m maximum drift and 150 APAs of wire readout, plus a photon detection system.
  - new: Single-phase horizontal-drift LArTPC: 17.5 kt of liquid argon in a 15.1 × 14.0 × 62.0 m membrane cryostat, at least 10 kt fiducial, four drift volumes at 500 V/cm with a 3.5 m maximum drift and 150 APAs of wire readout, plus a photon detection system.

### data/atlas/detectors/e949.json

- `/summary/technical` (summary.technical)
  - old: Stopped-kaon spectrometer at BNL, successor to the E787 apparatus, tracking the decay pion's range, energy and kinematics to isolate K+ -> pi+ nu nubar candidates from background.
  - new: Stopped-kaon spectrometer at BNL, successor to the E787 apparatus, tracking the decay pion's range, energy and kinematics to isolate K⁺ → π⁺ ν ν̄ candidates from background.

### data/atlas/detectors/gallex-gno.json

- `/summary/technical` (summary.technical)
  - old: Radiochemical gallium detector, 30.3 t Ga as 101 t GaCl3-HCl solution, at LNGS Hall A; 71Ga(nu_e,e-)71Ge reaction, chemically extracted and counted in campaigns rather than observed in real time.
  - new: Radiochemical gallium detector, 30.3 t Ga as 101 t GaCl3-HCl solution, at LNGS Hall A; 71Ga(νe,e⁻)71Ge reaction, chemically extracted and counted in campaigns rather than observed in real time.

### data/atlas/detectors/gerda.json

- `/summary/technical` (summary.technical)
  - old: Array of bare, enriched (76Ge) high-purity germanium point-contact detectors (~40 kg total) submerged directly in a 64 m3 liquid-argon cryostat that serves as both cooling medium and active veto, in LNGS Hall A.
  - new: Array of bare, enriched (76Ge) high-purity germanium point-contact detectors (~40 kg total) submerged directly in a 64 m³ liquid-argon cryostat that serves as both cooling medium and active veto, in LNGS Hall A.

### data/atlas/detectors/h-e-s-s.json

- `/specs/telescope_count/display` (quantity display)
  - old: 5 telescopes (4 x 12 m + 1 x 28 m)
  - new: 5 telescopes (4 × 12 m + 1 × 28 m)

### data/atlas/detectors/homestake.json

- `/specs/target_mass/note` (provenance note)
  - old: Wikipedia gives target volume (380 m3 / 100,000 gallons of perchloroethylene) but no source fetched this session converts this to a mass; left null rather than computed from an assumed density.
  - new: Wikipedia gives target volume (380 m³ / 100,000 gallons of perchloroethylene) but no source fetched this session converts this to a mass; left null rather than computed from an assumed density.
- `/summary/technical` (summary.technical)
  - old: Radiochemical chlorine-argon detector, 380 m3 perchloroethylene target, 1478 m (4850 ft) underground in the Homestake mine; ran 1970-1994, measured 37Ar production rate 2.56±0.16(stat)±0.16(syst) SNU.
  - new: Radiochemical chlorine-argon detector, 380 m³ perchloroethylene target, 1478 m (4850 ft) underground in the Homestake mine; ran 1970-1994, measured 37Ar production rate 2.56±0.16(stat)±0.16(syst) SNU.
- `/technology/note` (provenance note)
  - old: Reaction nu_e + 37Cl -> 37Ar + e- (inverse beta decay) and the extraction/counting steps: Cleveland et al. 1998 abstract (src:homestake-1998-flux-measurement). Perchloroethylene tank, argon extraction by helium sweep every two to three months: Davis Nobel lecture (quoted). The 'dry-cleaning fluid' gloss is from Wikipedia.
  - new: Reaction νe + 37Cl → 37Ar + e⁻ (inverse beta decay) and the extraction/counting steps: Cleveland et al. 1998 abstract (src:homestake-1998-flux-measurement). Perchloroethylene tank, argon extraction by helium sweep every two to three months: Davis Nobel lecture (quoted). The 'dry-cleaning fluid' gloss is from Wikipedia.

### data/atlas/detectors/hyper-kamiokande.json

- `/intervals/1/note` (provenance note)
  - old: Sub-milestones: cavern excavation expected complete 2024 per the same 2024 status article; the 2026 cavern-engineering paper (arXiv:2602.14810) reports the 69 m x 94 m cavern excavation complete; the official news page's most recent entry (4 Aug 2026, in Japanese) reports the water-tank lining work complete.
  - new: Sub-milestones: cavern excavation expected complete 2024 per the same 2024 status article; the 2026 cavern-engineering paper (arXiv:2602.14810) reports the 69 m × 94 m cavern excavation complete; the official news page's most recent entry (4 Aug 2026, in Japanese) reports the water-tank lining work complete.
- `/summary/technical` (summary.technical)
  - old: Water Cherenkov detector under construction, 68 m diameter x 71 m height, 260 kt total / 188 kt fiducial mass. Inner detector design centres on new large-aperture PMTs (order 20,000-40,000 depending on which official figure is used) plus ~1,000 multi-PMT 'compound eye' modules; outer veto up to 10,000 smaller PMTs. Housed in a purpose-excavated 69 m x 94 m cavern in the Tochibora mine, about 8 km from Super-Kamiokande.
  - new: Water Cherenkov detector under construction, 68 m diameter x 71 m height, 260 kt total / 188 kt fiducial mass. Inner detector design centres on new large-aperture PMTs (order 20,000-40,000 depending on which official figure is used) plus ~1,000 multi-PMT 'compound eye' modules; outer veto up to 10,000 smaller PMTs. Housed in a purpose-excavated 69 m × 94 m cavern in the Tochibora mine, about 8 km from Super-Kamiokande.

### data/atlas/detectors/icarus-t600.json

- `/summary/technical` (summary.technical)
  - old: Two adjacent 3.6 x 3.9 x 19.6 m liquid argon TPC modules holding 760 t of argon with 476 t active mass; operated in LNGS Hall B 2010-2013 on the CNGS beam, overhauled at CERN 2014-2017, and running at Fermilab as the SBN far detector 600 m from the BNB target.
  - new: Two adjacent 3.6 × 3.9 × 19.6 m liquid argon TPC modules holding 760 t of argon with 476 t active mass; operated in LNGS Hall B 2010-2013 on the CNGS beam, overhauled at CERN 2014-2017, and running at Fermilab as the SBN far detector 600 m from the BNB target.

### data/atlas/detectors/karmen.json

- `/summary/technical` (summary.technical)
  - old: Rectangular high-resolution liquid-scintillation calorimeter, 56 t total mass, 65 m^3 active liquid-scintillator volume (75% vol. paraffin oil, 25% vol. pseudocumene, 2 g/l PMP wavelength shifter) optically segmented into 512 independent central modules with gadolinium loading between module walls for thermal-neutron capture; located 17.7 m from the ISIS beam-stop target at 100 degrees to the proton beam.
  - new: Rectangular high-resolution liquid-scintillation calorimeter, 56 t total mass, 65 m³ active liquid-scintillator volume (75% vol. paraffin oil, 25% vol. pseudocumene, 2 g/l PMP wavelength shifter) optically segmented into 512 independent central modules with gadolinium loading between module walls for thermal-neutron capture; located 17.7 m from the ISIS beam-stop target at 100 degrees to the proton beam.

### data/atlas/detectors/km3net-orca.json

- `/specs/instrumented_volume/note` (provenance note)
  - old: Source states the design instrumented quantity as '7 Megatonnes of seawater'; converted to volume assuming seawater density approx. 1000 kg/m3 (1 t approx. 1 m3) to populate the schema's volume-dimension 'instrumented_volume' key. Design (final) figure for the completed 115-detection-unit building block; 42 detection units were actually installed as of 2026-07-08 (see intervals).
  - new: Source states the design instrumented quantity as '7 Megatonnes of seawater'; converted to volume assuming seawater density approx. 1000 kg/m³ (1 t approx. 1 m³) to populate the schema's volume-dimension 'instrumented_volume' key. Design (final) figure for the completed 115-detection-unit building block; 42 detection units were actually installed as of 2026-07-08 (see intervals).

### data/atlas/detectors/koto.json

- `/summary/technical` (summary.technical)
  - old: Hermetic CsI electromagnetic calorimeter with surrounding veto counters at the J-PARC Hadron Experimental Facility, reconstructing KL -> pi0(->gamma gamma) nu nubar candidates against visible-particle vetoes.
  - new: Hermetic CsI electromagnetic calorimeter with surrounding veto counters at the J-PARC Hadron Experimental Facility, reconstructing KL → π⁰(→γγ) ν ν̄ candidates against visible-particle vetoes.
- `/technology/value` (energy_regime / technology / subsystems / spec text)
  - old: Hermetic electromagnetic calorimeter and veto-counter system surrounding a neutral-kaon beamline, reconstructing KL -> pi0 (-> gamma gamma) decays while vetoing all other visible particles
  - new: Hermetic electromagnetic calorimeter and veto-counter system surrounding a neutral-kaon beamline, reconstructing KL → π⁰ (→ γγ) decays while vetoing all other visible particles

### data/atlas/detectors/lhcb.json

- `/summary/technical` (summary.technical)
  - old: Single-arm forward spectrometer at LHC Point 8: VELO, dipole magnet, two RICH detectors, tracking stations, calorimeters and a muon system arranged sequentially along the outgoing beam direction over ~20 m; 5600 t (per INSPIRE/home.cern; lhcb-outreach states 4500 t, unresolved conflict), 21 m x 10 m x 13 m.
  - new: Single-arm forward spectrometer at LHC Point 8: VELO, dipole magnet, two RICH detectors, tracking stations, calorimeters and a muon system arranged sequentially along the outgoing beam direction over ~20 m; 5600 t (per INSPIRE/home.cern; lhcb-outreach states 4500 t, unresolved conflict), 21 m × 10 m × 13 m.

### data/atlas/detectors/lhcf.json

- `/notes/0` (notes[])
  - old: home.cern gives detector mass (40 kg) and dimensions (30 cm x 80 cm x 10 cm) per arm as of a November 2012 page snapshot; recorded in specs below.
  - new: home.cern gives detector mass (40 kg) and dimensions (30 cm × 80 cm × 10 cm) per arm as of a November 2012 page snapshot; recorded in specs below.
- `/placements/0/note` (provenance note)
  - old: LHCf's two arms are physically in the TAN neutral-particle absorbers +-140 m from IP1, not in the ATLAS cavern itself; placed at site:cern-point-1-atlas (owned by cern-atlas, referenced only) per the id registry's explicit instruction that LHCf places at this existing site.
  - new: LHCf's two arms are physically in the TAN neutral-particle absorbers ±140 m from IP1, not in the ATLAS cavern itself; placed at site:cern-point-1-atlas (owned by cern-atlas, referenced only) per the id registry's explicit instruction that LHCf places at this existing site.
- `/summary/technical` (summary.technical)
  - old: Two identical imaging sampling calorimeters (Arm1, Arm2), tungsten/scintillator/position-sensitive-sensor construction, each ~40 kg, 30 cm x 80 cm x 10 cm, at zero-degree collision angle +-140 m from IP1.
  - new: Two identical imaging sampling calorimeters (Arm1, Arm2), tungsten/scintillator/position-sensitive-sensor construction, each ~40 kg, 30 cm × 80 cm × 10 cm, at zero-degree collision angle ±140 m from IP1.

### data/atlas/detectors/lz.json

- `/specs/shielding/value` (energy_regime / technology / subsystems / spec text)
  - old: Liquid xenon skin veto, a gadolinium-loaded liquid scintillator outer detector, and an 8 m x 6 m tank of 70,000 gallons of ultrapure water, under ~1480 m of rock.
  - new: Liquid xenon skin veto, a gadolinium-loaded liquid scintillator outer detector, and an 8 m × 6 m tank of 70,000 gallons of ultrapure water, under ~1480 m of rock.
- `/summary/technical` (summary.technical)
  - old: Dual-phase xenon TPC, ~1.5 m diameter and height, 145.6 cm drift, 7 active tonnes of a 10 t inventory, 5.5 t SR1 fiducial, 494 R11410 PMTs (253 top / 241 bottom), surrounded by a ~2 t instrumented Xe skin (131 PMTs), a gadolinium-loaded liquid scintillator outer detector (120 R5912 PMTs) and an 8 m x 6 m water shield in the Davis Cavern.
  - new: Dual-phase xenon TPC, ~1.5 m diameter and height, 145.6 cm drift, 7 active tonnes of a 10 t inventory, 5.5 t SR1 fiducial, 494 R11410 PMTs (253 top / 241 bottom), surrounded by a ~2 t instrumented Xe skin (131 PMTs), a gadolinium-loaded liquid scintillator outer detector (120 R5912 PMTs) and an 8 m × 6 m water shield in the Davis Cavern.

### data/atlas/detectors/microboone.json

- `/summary/technical` (summary.technical)
  - old: Single-phase liquid argon time projection chamber with 170 t total argon mass and 90 t inside the TPC, 2.56 x 2.325 x 10.368 m active volume, 2.6 m maximum drift, 8256 wires on three planes, 470 m from the BNB target.
  - new: Single-phase liquid argon time projection chamber with 170 t total argon mass and 90 t inside the TPC, 2.56 × 2.325 × 10.368 m active volume, 2.6 m maximum drift, 8256 wires on three planes, 470 m from the BNB target.

### data/atlas/detectors/miniboone.json

- `/intervals/0/note` (provenance note)
  - old: End year is not stated verbatim in any source fetched; the MiniBooNE 2021 PRD reports the final 18.75e20 POT neutrino-mode data set and the experiment is universally described as having run to 2019. Recorded as approximate.
  - new: End year is not stated verbatim in any source fetched; the MiniBooNE 2021 PRD reports the final 18.75 × 10²⁰ POT neutrino-mode data set and the experiment is universally described as having run to 2019. Recorded as approximate.

### data/atlas/detectors/moedal.json

- `/specs/area/display` (quantity display)
  - old: 47 m^2 (NTD plastic)
  - new: 47 m² (NTD plastic)
- `/summary/technical` (summary.technical)
  - old: 125 NTD stacks (47 m^2 total plastic), ~1 t of paramagnetic trapping detectors, TimePix pixel monitors; deployed in the LHCb cavern at Point 8, requiring no trigger or online DAQ for its main passive elements.
  - new: 125 NTD stacks (47 m² total plastic), ~1 t of paramagnetic trapping detectors, TimePix pixel monitors; deployed in the LHCb cavern at Point 8, requiring no trigger or online DAQ for its main passive elements.

### data/atlas/detectors/na48.json

- `/technology/value` (energy_regime / technology / subsystems / spec text)
  - old: Magnetic spectrometer (helium-filled tank with two drift chambers either side of a dipole magnet) plus liquid-krypton electromagnetic calorimeter, used to reconstruct KL/KS -> 2 pion decays
  - new: Magnetic spectrometer (helium-filled tank with two drift chambers either side of a dipole magnet) plus liquid-krypton electromagnetic calorimeter, used to reconstruct KL/KS → 2 pion decays

### data/atlas/detectors/na62.json

- `/subsystems/0/description/0/value` (energy_regime / technology / subsystems / spec text)
  - old: Low-mass, high-intensity silicon-pixel beam spectrometer providing 4D (position + time) tracking of individual beam particles at flux up to 2.0 MHz/mm^2, with 65 ps time resolution on tracks
  - new: Low-mass, high-intensity silicon-pixel beam spectrometer providing 4D (position + time) tracking of individual beam particles at flux up to 2.0 MHz/mm², with 65 ps time resolution on tracks
- `/summary/technical` (summary.technical)
  - old: Decay-in-flight spectrometer in the ECN3 cavern: GigaTracker beam-timing spectrometer (65 ps track time resolution, up to 2.0 MHz/mm^2 flux), RICH counter, LKr electromagnetic calorimeter, straw trackers and hermetic photon/particle veto systems, built 2009-2014 and operating since 2015.
  - new: Decay-in-flight spectrometer in the ECN3 cavern: GigaTracker beam-timing spectrometer (65 ps track time resolution, up to 2.0 MHz/mm² flux), RICH counter, LKr electromagnetic calorimeter, straw trackers and hermetic photon/particle veto systems, built 2009-2014 and operating since 2015.

### data/atlas/detectors/nova-far-detector.json

- `/summary/technical` (summary.technical)
  - old: 14 kt totally-active segmented tracking calorimeter of extruded PVC cells filled with mineral-oil-based liquid scintillator, 15.5 x 15.5 x 59.8 m, on the surface at Ash River 810 km from the NuMI target and 14.6 mrad off axis.
  - new: 14 kt totally-active segmented tracking calorimeter of extruded PVC cells filled with mineral-oil-based liquid scintillator, 15.5 × 15.5 × 59.8 m, on the surface at Ash River 810 km from the NuMI target and 14.6 mrad off axis.

### data/atlas/detectors/opal.json

- `/summary/technical` (summary.technical)
  - old: General-purpose LEP detector, about 12 m x 12 m x 12 m, arranged as concentric layers of tracking detectors, calorimeters and muon detectors around the beam pipe.
  - new: General-purpose LEP detector, about 12 m × 12 m × 12 m, arranged as concentric layers of tracking detectors, calorimeters and muon detectors around the beam pipe.

### data/atlas/detectors/pierre-auger-observatory.json

- `/placements/0/note` (provenance note)
  - old: Placement point is the Observatory campus; the physical array of stations is spread over the surrounding 3000 km^2 (see site:malargue-auger notes).
  - new: Placement point is the Observatory campus; the physical array of stations is spread over the surrounding 3000 km² (see site:malargue-auger notes).
- `/subsystems/0/description/0/value` (energy_regime / technology / subsystems / spec text)
  - old: Array of 1660 water-Cherenkov detector tanks spread over 3000 km^2, sampling the particle density of extensive air showers at ground level.
  - new: Array of 1660 water-Cherenkov detector tanks spread over 3000 km², sampling the particle density of extensive air showers at ground level.
- `/summary/technical` (summary.technical)
  - old: Hybrid surface-detector/fluorescence-detector system: 1660 water-Cherenkov tanks on a 1.5 km grid across 3000 km^2, plus 27 fluorescence telescopes in four buildings; currently being upgraded (AugerPrime) with scintillator panels, radio antennas, upgraded electronics and underground muon counters on each surface station.
  - new: Hybrid surface-detector/fluorescence-detector system: 1660 water-Cherenkov tanks on a 1.5 km grid across 3000 km², plus 27 fluorescence telescopes in four buildings; currently being upgraded (AugerPrime) with scintillator panels, radio antennas, upgraded electronics and underground muon counters on each surface station.

### data/atlas/detectors/protodune-sp.json

- `/summary/technical` (summary.technical)
  - old: Single-phase LArTPC prototype at the CERN Neutrino Platform (EHN1) with a 7.2 x 6.0 x 6.9 m^3 active volume, 3.6 m drift at 500 V/cm, full-size DUNE APAs, photon detectors and a cosmic-ray tagger, in a 0.3-7 GeV/c tagged charged-particle beam from 2018.
  - new: Single-phase LArTPC prototype at the CERN Neutrino Platform (EHN1) with a 7.2 × 6.0 × 6.9 m³ active volume, 3.6 m drift at 500 V/cm, full-size DUNE APAs, photon detectors and a cosmic-ray tagger, in a 0.3-7 GeV/c tagged charged-particle beam from 2018.

### data/atlas/detectors/ricochet-cryocube.json

- `/notes/1` (notes[])
  - old: Two mass figures from two different papers/phases: the full, final CryoCube is described only qualitatively as a 'kg-scale' Ge+Zn array (arXiv:2208.01760, a background-characterization paper for the planned final detector); the commissioning-phase mini-CryoCube module actually operated and characterized (arXiv:2507.22751) is precisely 3 x 42 g = 126 g of germanium. specs.target_mass below records the precisely-quoted mini-CryoCube figure.
  - new: Two mass figures from two different papers/phases: the full, final CryoCube is described only qualitatively as a 'kg-scale' Ge+Zn array (arXiv:2208.01760, a background-characterization paper for the planned final detector); the commissioning-phase mini-CryoCube module actually operated and characterized (arXiv:2507.22751) is precisely 3 × 42 g = 126 g of germanium. specs.target_mass below records the precisely-quoted mini-CryoCube figure.
- `/specs/target_mass/display` (quantity display)
  - old: 126 g (3 x 42 g Ge, mini-CryoCube commissioning module)
  - new: 126 g (3 × 42 g Ge, mini-CryoCube commissioning module)
- `/specs/target_mass/note` (provenance note)
  - old: 126 g is derived as 3 x 42 g from the quoted three 42-gram germanium cryogenic calorimeters (the source does not state the total). This is the commissioning-phase mini-CryoCube module actually characterized; the planned full CryoCube is described only qualitatively as 'kg-scale' combining Ge and Zn crystals (arXiv:2208.01760), with no precise total mass quoted in a source cited here.
  - new: 126 g is derived as 3 × 42 g from the quoted three 42-gram germanium cryogenic calorimeters (the source does not state the total). This is the commissioning-phase mini-CryoCube module actually characterized; the planned full CryoCube is described only qualitatively as 'kg-scale' combining Ge and Zn crystals (arXiv:2208.01760), with no precise total mass quoted in a source cited here.

### data/atlas/detectors/sage.json

- `/summary/technical` (summary.technical)
  - old: Radiochemical liquid-gallium-metal detector (50 t), 71Ga(nu_e,e-)71Ge reaction, at Baksan; chemically extracted and counted in periodic campaigns rather than observed in real time.
  - new: Radiochemical liquid-gallium-metal detector (50 t), 71Ga(νe,e⁻)71Ge reaction, at Baksan; chemically extracted and counted in periodic campaigns rather than observed in real time.

### data/atlas/detectors/sbnd.json

- `/notes/1` (notes[])
  - old: The SBN proposal (2015) describes the same detector under its earlier name LAr1-ND, with an active volume of 4.0 x 4.0 x 5.0 m containing 112 tons of liquid argon.
  - new: The SBN proposal (2015) describes the same detector under its earlier name LAr1-ND, with an active volume of 4.0 × 4.0 × 5.0 m containing 112 tons of liquid argon.
- `/summary/technical` (summary.technical)
  - old: 112 t active mass single-phase liquid argon TPC 110 m from the Booster Neutrino Beam target, the near detector of the Short-Baseline Neutrino programme; 4.0 x 4.0 x 5.0 m active volume in the SBN proposal design.
  - new: 112 t active mass single-phase liquid argon TPC 110 m from the Booster Neutrino Beam target, the near detector of the Short-Baseline Neutrino programme; 4.0 × 4.0 × 5.0 m active volume in the SBN proposal design.

### data/atlas/detectors/sensei.json

- `/specs/pixel_count/display` (quantity display)
  - old: ~904,000 pixels (4 x 624 x 362)
  - new: ~904,000 pixels (4 × 624 × 362)
- `/specs/pixel_count/note` (provenance note)
  - old: Computed as 4 x 624 x 362 = 903,552 from the quoted quadrant geometry; not stated as a single total in the source. Cross-check: the source gives an active area of 1.086 cm x 1.872 cm and 15 um x 15 um pixels (724 x 1248 pixels), and 0.0947 g total active mass at 1.0476e-7 g per pixel (about 904,000 pixels).
  - new: Computed as 4 × 624 × 362 = 903,552 from the quoted quadrant geometry; not stated as a single total in the source. Cross-check: the source gives an active area of 1.086 cm × 1.872 cm and 15 μm × 15 μm pixels (724 × 1248 pixels), and 0.0947 g total active mass at 1.0476 × 10⁻⁷ g per pixel (about 904,000 pixels).

### data/atlas/detectors/star.json

- `/subsystems/0/value` (energy_regime / technology / subsystems / spec text)
  - old: Time Projection Chamber (TPC): the central tracking detector, 4 m diameter x 4.2 m long, providing complete azimuthal charged-particle tracking within about |eta| < 1.8
  - new: Time Projection Chamber (TPC): the central tracking detector, 4 m diameter x 4.2 m long, providing complete azimuthal charged-particle tracking within about |η| < 1.8
- `/summary/technical` (summary.technical)
  - old: STAR: a 1,200 t heavy-ion collider detector at RHIC IP6, built around a 4 m diameter x 4.2 m long gaseous Time Projection Chamber inside a solenoidal magnet, providing full-azimuth charged-particle tracking within |eta| < 1.8.
  - new: STAR: a 1,200 t heavy-ion collider detector at RHIC IP6, built around a 4 m diameter x 4.2 m long gaseous Time Projection Chamber inside a solenoidal magnet, providing full-azimuth charged-particle tracking within |η| < 1.8.

### data/atlas/detectors/telescope-array.json

- `/placements/0/note` (provenance note)
  - old: Placement point is the approximate campus/central point; the physical array is spread over ~700 km^2 (TAx4: ~3000 km^2) around Delta, Utah.
  - new: Placement point is the approximate campus/central point; the physical array is spread over ~700 km² (TAx4: ~3000 km²) around Delta, Utah.
- `/subsystems/0/description/0/value` (energy_regime / technology / subsystems / spec text)
  - old: 507 plastic scintillation counters on a 1.2 km square grid covering about 700 km^2; extended by 500 additional TAx4 counters on a 2.08 km grid.
  - new: 507 plastic scintillation counters on a 1.2 km square grid covering about 700 km²; extended by 500 additional TAx4 counters on a 2.08 km grid.
- `/summary/technical` (summary.technical)
  - old: Hybrid surface-detector/fluorescence-detector system: 507 scintillator counters on a 1.2 km grid over ~700 km^2, plus 38 fluorescence telescopes at three sites; extended since 2019 by TAx4 (500 further counters on a 2.08 km grid, 12 new FD telescopes, ~3000 km^2 target coverage).
  - new: Hybrid surface-detector/fluorescence-detector system: 507 scintillator counters on a 1.2 km grid over ~700 km², plus 38 fluorescence telescopes at three sites; extended since 2019 by TAx4 (500 further counters on a 2.08 km grid, 12 new FD telescopes, ~3000 km² target coverage).

### data/atlas/detectors/ua1.json

- `/summary/technical` (summary.technical)
  - old: General-purpose (4-pi) collider detector: central six-chambered imaging drift chamber (5.8 m long, 2.3 m diameter) inside an 800-tonne conventional dipole magnet, 48 lead-layer ('gondola') electromagnetic subdetectors, hadron calorimetry and muon chambers requiring about 30 km of extruded aluminium.
  - new: General-purpose (4π) collider detector: central six-chambered imaging drift chamber (5.8 m long, 2.3 m diameter) inside an 800-tonne conventional dipole magnet, 48 lead-layer ('gondola') electromagnetic subdetectors, hadron calorimetry and muon chambers requiring about 30 km of extruded aluminium.
- `/technology/value` (energy_regime / technology / subsystems / spec text)
  - old: General-purpose (4-pi) collider detector with a central imaging drift chamber, electromagnetic and hadronic calorimetry and muon chambers around a conventional dipole magnet
  - new: General-purpose (4π) collider detector with a central imaging drift chamber, electromagnetic and hadronic calorimetry and muon chambers around a conventional dipole magnet

### data/atlas/detectors/xenonnt.json

- `/intervals/2/label` (interval label)
  - old: detector upgrade (new TPC electrodes, drift field 23 -> 100 V/cm)
  - new: detector upgrade (new TPC electrodes, drift field 23 → 100 V/cm)

### data/atlas/documents/comet-phase1-tdr.json

- `/summary/technical` (summary.technical)
  - old: arXiv:1812.09018: COMET Phase-I Technical Design Report, describing the CyDet/StrECAL detector design, the 3.2 kW 8 GeV J-PARC proton beam, and the Phase-I sensitivity goal of 3.1x10^-15 (7x10^-15 90% C.L. upper limit).
  - new: arXiv:1812.09018: COMET Phase-I Technical Design Report, describing the CyDet/StrECAL detector design, the 3.2 kW 8 GeV J-PARC proton beam, and the Phase-I sensitivity goal of 3.1×10⁻¹⁵ (7×10⁻¹⁵ 90% C.L. upper limit).

### data/atlas/documents/lux-detector-paper.json

- `/summary/technical` (summary.technical)
  - old: Design and construction of the LUX dual-phase xenon detector: 370 kg total xenon with a 100 kg design fiducial volume, targeting a spin-independent WIMP-nucleon cross section of 2e-46 cm2.
  - new: Design and construction of the LUX dual-phase xenon detector: 370 kg total xenon with a 100 kg design fiducial volume, targeting a spin-independent WIMP-nucleon cross section of 2 × 10⁻⁴⁶ cm².

### data/atlas/documents/lz-cdr.json

- `/summary/technical` (summary.technical)
  - old: LZ CDR (arXiv:1509.02910, LBNL-190005, September 2015): conceptual design of a ~10 tonne liquid xenon second-generation WIMP detector at SURF, sensitive from a few GeV/c2 to hundreds of TeV/c2.
  - new: LZ CDR (arXiv:1509.02910, LBNL-190005, September 2015): conceptual design of a ~10 tonne liquid xenon second-generation WIMP detector at SURF, sensitive from a few GeV/c² to hundreds of TeV/c².

### data/atlas/documents/lz-tdr.json

- `/summary/technical` (summary.technical)
  - old: LZ TDR (arXiv:1703.09144, LBNL-1007256, March 2017): design of the detector to be built at SURF, targeting a spin-independent WIMP-nucleon sensitivity of 3e-48 cm2.
  - new: LZ TDR (arXiv:1703.09144, LBNL-1007256, March 2017): design of the detector to be built at SURF, targeting a spin-independent WIMP-nucleon sensitivity of 3 × 10⁻⁴⁸ cm².

### data/atlas/experiments/atlas.json

- `/unique_capabilities/1/value` (physics_goals / unique_capabilities)
  - old: Hermetic calorimetry covering |eta| < 4.9 (nearly the entire solid angle), which the collaboration says makes it possible to search for dark matter
  - new: Hermetic calorimetry covering |η| < 4.9 (nearly the entire solid angle), which the collaboration says makes it possible to search for dark matter

### data/atlas/experiments/babar.json

- `/energy_regime/value` (energy_regime / technology / subsystems / spec text)
  - old: Asymmetric e+e- collisions at 10.58 GeV center-of-mass (the Upsilon(4S) resonance)
  - new: Asymmetric e⁺e⁻ collisions at 10.58 GeV center-of-mass (the Υ(4S) resonance)
- `/facility_roles/1/note` (provenance note)
  - old: The PEP-II asymmetric e+e- beams that BaBar recorded were produced and accelerated at SLAC; PEP-II was built by SLAC, Lawrence Berkeley National Laboratory and Lawrence Livermore National Laboratory.
  - new: The PEP-II asymmetric e⁺e⁻ beams that BaBar recorded were produced and accelerated at SLAC; PEP-II was built by SLAC, Lawrence Berkeley National Laboratory and Lawrence Livermore National Laboratory.
- `/summary/technical` (summary.technical)
  - old: General-purpose detector at the PEP-II asymmetric e+e- B-factory (SLAC), operating at the Upsilon(4S) resonance (10.58 GeV) to study CP violation in neutral B-meson decays via the entangled B0-B0bar pairs produced. First collisions 26 May 1999; data-taking ended 8 April 2008. Co-observed CP violation in the B0 system (2001) with Belle at KEK.
  - new: General-purpose detector at the PEP-II asymmetric e⁺e⁻ B-factory (SLAC), operating at the Υ(4S) resonance (10.58 GeV) to study CP violation in neutral B-meson decays via the entangled B⁰-B̄⁰ pairs produced. First collisions 26 May 1999; data-taking ended 8 April 2008. Co-observed CP violation in the B⁰ system (2001) with Belle at KEK.
- `/unique_capabilities/0/value` (physics_goals / unique_capabilities)
  - old: An asymmetric-energy e+e- collider tuned to the Upsilon(4S) resonance, giving the produced B and anti-B mesons a relativistic boost that lets their decay points be resolved -- essential for time-dependent CP-violation measurements
  - new: An asymmetric-energy e⁺e⁻ collider tuned to the Υ(4S) resonance, giving the produced B and anti-B mesons a relativistic boost that lets their decay points be resolved -- essential for time-dependent CP-violation measurements

### data/atlas/experiments/belle-ii.json

- `/energy_regime/value` (energy_regime / technology / subsystems / spec text)
  - old: e+e- collisions at √s = 10.579 GeV (Υ(4S) resonance)
  - new: e⁺e⁻ collisions at √s = 10.579 GeV (Υ(4S) resonance)
- `/summary/technical` (summary.technical)
  - old: Intensity-frontier e+e- experiment at SuperKEKB (√s = 10.579 GeV), aiming at 50 ab⁻¹ to probe flavour observables in B, charm and tau decays and to search for dark-sector states; 914 fb⁻¹ recorded by September 2026.
  - new: Intensity-frontier e⁺e⁻ experiment at SuperKEKB (√s = 10.579 GeV), aiming at 50 ab⁻¹ to probe flavour observables in B, charm and tau decays and to search for dark-sector states; 914 fb⁻¹ recorded by September 2026.
- `/unique_capabilities/value/0` (physics_goals / unique_capabilities)
  - old: Reconstruction of decays with neutrinos or photons using the precisely known e+e- initial state
  - new: Reconstruction of decays with neutrinos or photons using the precisely known e⁺e⁻ initial state
- `/unique_capabilities/value/2` (physics_goals / unique_capabilities)
  - old: The world's largest e+e- data set at the Υ(4S) resonance
  - new: The world's largest e⁺e⁻ data set at the Υ(4S) resonance

### data/atlas/experiments/belle.json

- `/energy_regime/value` (energy_regime / technology / subsystems / spec text)
  - old: e+e- collisions at the Υ(4S) resonance, √s ≈ 10.58 GeV
  - new: e⁺e⁻ collisions at the Υ(4S) resonance, √s ≈ 10.58 GeV
- `/summary/technical` (summary.technical)
  - old: B-factory experiment at the asymmetric-energy KEKB e+e- collider running at the Υ(4S); >1 ab⁻¹ recorded, establishing time-dependent CP violation in B⁰ decays, evidence for D⁰-D⁰bar mixing and B⁻→τ⁻ν, and the discovery of the X(3872).
  - new: B-factory experiment at the asymmetric-energy KEKB e⁺e⁻ collider running at the Υ(4S); >1 ab⁻¹ recorded, establishing time-dependent CP violation in B⁰ decays, evidence for D⁰-D⁰bar mixing and B⁻→τ⁻ν, and the discovery of the X(3872).
- `/unique_capabilities/value/0` (physics_goals / unique_capabilities)
  - old: Asymmetric-energy e+e- collisions at the Υ(4S) giving a boosted B–Bbar system for time-dependent CP-violation measurements
  - new: Asymmetric-energy e⁺e⁻ collisions at the Υ(4S) giving a boosted B–B̄ system for time-dependent CP-violation measurements

### data/atlas/experiments/cdms-ii.json

- `/energy_regime/value` (energy_regime / technology / subsystems / spec text)
  - old: keV-scale nuclear recoils, WIMP-nucleon spin-independent limit quoted near 70 GeV/c^2 WIMP mass
  - new: keV-scale nuclear recoils, WIMP-nucleon spin-independent limit quoted near 70 GeV/c² WIMP mass
- `/summary/technical` (summary.technical)
  - old: Second-generation Cryogenic Dark Matter Search: 19 Ge (~230 g) and 11 Si (~100 g) ionization-and-phonon detectors in five towers, operated below 50 mK at the Soudan Underground Laboratory. The final blind analysis (612 kg-day raw exposure, results submitted Dec 2009) observed two candidate events consistent with background, setting a 90% CL spin-independent WIMP-nucleon cross-section limit of 7.0e-44 cm^2 at 70 GeV/c^2 (3.8e-44 cm^2 combined with earlier CDMS II data).
  - new: Second-generation Cryogenic Dark Matter Search: 19 Ge (~230 g) and 11 Si (~100 g) ionization-and-phonon detectors in five towers, operated below 50 mK at the Soudan Underground Laboratory. The final blind analysis (612 kg-day raw exposure, results submitted Dec 2009) observed two candidate events consistent with background, setting a 90% CL spin-independent WIMP-nucleon cross-section limit of 7.0 × 10⁻⁴⁴ cm² at 70 GeV/c² (3.8 × 10⁻⁴⁴ cm² combined with earlier CDMS II data).

### data/atlas/experiments/cms.json

- `/physics_goals/1/value` (physics_goals / unique_capabilities)
  - old: Study proton-proton and lead-lead collisions at centre-of-mass energies up to 14 TeV and luminosities up to 10^34 cm^-2 s^-1
  - new: Study proton-proton and lead-lead collisions at centre-of-mass energies up to 14 TeV and luminosities up to 10³⁴ cm⁻² s⁻¹

### data/atlas/experiments/coherent.json

- `/unique_capabilities/0/value` (physics_goals / unique_capabilities)
  - old: Simultaneous deployment of multiple target nuclei (CsI, Ar, Ge, NaI) at one neutrino source to test the predicted N^2 (neutron-number-squared) dependence of the CEvNS cross section
  - new: Simultaneous deployment of multiple target nuclei (CsI, Ar, Ge, NaI) at one neutrino source to test the predicted N² (neutron-number-squared) dependence of the CEvNS cross section

### data/atlas/experiments/comet.json

- `/key_specs/0/quantity/display` (quantity display)
  - old: 7x10^-15 (design sensitivity 3.1x10^-15)
  - new: 7×10⁻¹⁵ (design sensitivity 3.1×10⁻¹⁵)
- `/key_specs/0/quantity/note` (provenance note)
  - old: The TDR states both a design sensitivity (3.1x10^-15) and the corresponding 90% C.L. upper limit if no signal is seen (7x10^-15); the upper-limit figure is recorded as the primary quantity with the design sensitivity in the note, both from the same quote.
  - new: The TDR states both a design sensitivity (3.1×10⁻¹⁵) and the corresponding 90% C.L. upper limit if no signal is seen (7×10⁻¹⁵); the upper-limit figure is recorded as the primary quantity with the design sensitivity in the note, both from the same quote.
- `/physics_goals/0/value` (physics_goals / unique_capabilities)
  - old: Search for neutrinoless muon-to-electron conversion in the field of an aluminium nucleus (mu- N -> e- N), a charged-lepton-flavor-violating process, in a staged Phase-I then Phase-II programme
  - new: Search for neutrinoless muon-to-electron conversion in the field of an aluminium nucleus (μ⁻ N → e⁻ N), a charged-lepton-flavor-violating process, in a staged Phase-I then Phase-II programme
- `/summary/technical` (summary.technical)
  - old: COMET (J-PARC Hadron Experimental Facility): stages a search for mu- N -> e- N conversion, using curved-solenoid muon transport from an 8 GeV, 3.2 kW proton beam off the J-PARC Main Ring. Phase-I targets a 90% C.L. branching-ratio upper limit of 7x10^-15 (design sensitivity 3.1x10^-15) using CyDet, a factor of 100 improvement over the previous (SINDRUM II) limit; StrECAL measures background in view of Phase-II. Collaboration: more than 290 researchers from 48 institutes. No physics result has been produced yet as of the sources fetched this session.
  - new: COMET (J-PARC Hadron Experimental Facility): stages a search for μ⁻ N → e⁻ N conversion, using curved-solenoid muon transport from an 8 GeV, 3.2 kW proton beam off the J-PARC Main Ring. Phase-I targets a 90% C.L. branching-ratio upper limit of 7×10⁻¹⁵ (design sensitivity 3.1×10⁻¹⁵) using CyDet, a factor of 100 improvement over the previous (SINDRUM II) limit; StrECAL measures background in view of Phase-II. Collaboration: more than 290 researchers from 48 institutes. No physics result has been produced yet as of the sources fetched this session.

### data/atlas/experiments/conus.json

- `/summary/technical` (summary.technical)
  - old: Reactor CEvNS experiment using an array of four 1 kg point-contact HPGe spectrometers; ran as CONUS at the Brokdorf nuclear power plant, Germany (17.1 m baseline, 3.9 GWth core, 2018-2023), then relocated as CONUS+ to the Leibstadt nuclear power plant, Switzerland (20.7 m baseline, 3.6 GWth core, from November 2023), reporting a first direct 3.7-sigma observation of reactor CEvNS in January 2025.
  - new: Reactor CEvNS experiment using an array of four 1 kg point-contact HPGe spectrometers; ran as CONUS at the Brokdorf nuclear power plant, Germany (17.1 m baseline, 3.9 GWth core, 2018-2023), then relocated as CONUS+ to the Leibstadt nuclear power plant, Switzerland (20.7 m baseline, 3.6 GWth core, from November 2023), reporting a first direct 3.7σ observation of reactor CEvNS in January 2025.

### data/atlas/experiments/cresst.json

- `/energy_regime/value` (energy_regime / technology / subsystems / spec text)
  - old: Sub-GeV WIMPs; CRESST-III reaches nuclear-recoil thresholds of 10 eV and lower, probing masses down to ~70 MeV/c^2
  - new: Sub-GeV WIMPs; CRESST-III reaches nuclear-recoil thresholds of 10 eV and lower, probing masses down to ~70 MeV/c²
- `/physics_goals/value/0` (physics_goals / unique_capabilities)
  - old: Direct detection of sub-GeV dark matter particles via elastic nuclear recoils in cryogenic crystal targets, with CRESST-III reaching thresholds of 10 eV and lower and probing WIMP masses down to ~70 MeV/c^2
  - new: Direct detection of sub-GeV dark matter particles via elastic nuclear recoils in cryogenic crystal targets, with CRESST-III reaching thresholds of 10 eV and lower and probing WIMP masses down to ~70 MeV/c²
- `/summary/technical` (summary.technical)
  - old: Cryogenic scintillating-crystal calorimeter dark matter search at LNGS; proposed 1993, named CRESST in 1996. CRESST-I used sapphire absorbers (2000-2003); CRESST-II introduced 300 g CaWO4 crystals (2004-2015, Phase 2 to 2019); CRESST-III (from 2019) uses ~25 g crystals, reaching nuclear-recoil thresholds of 10 eV and lower and probing WIMP masses down to ~70 MeV/c^2, with detector R&D ongoing as of 2026.
  - new: Cryogenic scintillating-crystal calorimeter dark matter search at LNGS; proposed 1993, named CRESST in 1996. CRESST-I used sapphire absorbers (2000-2003); CRESST-II introduced 300 g CaWO4 crystals (2004-2015, Phase 2 to 2019); CRESST-III (from 2019) uses ~25 g crystals, reaching nuclear-recoil thresholds of 10 eV and lower and probing WIMP masses down to ~70 MeV/c², with detector R&D ongoing as of 2026.

### data/atlas/experiments/cuore.json

- `/summary/technical` (summary.technical)
  - old: CUORE (Cryogenic Underground Observatory for Rare Events): tonne-scale array of 988 TeO2 bolometric crystals (19 towers) operated at ~10 mK in Hall A of LNGS. Began operating in 2017, steady data taking since 2019; the 2024 result set T1/2 0ν(130Te) > 3.5x10^25 yr (90% C.I.) with over 2 t·yr TeO2 exposure. Predecessor to CUPID, which will reuse its cryostat.
  - new: CUORE (Cryogenic Underground Observatory for Rare Events): tonne-scale array of 988 TeO2 bolometric crystals (19 towers) operated at ~10 mK in Hall A of LNGS. Began operating in 2017, steady data taking since 2019; the 2024 result set T1/2 0ν(130Te) > 3.5×10²⁵ yr (90% C.I.) with over 2 t·yr TeO2 exposure. Predecessor to CUPID, which will reuse its cryostat.

### data/atlas/experiments/damic-m.json

- `/energy_regime/value` (energy_regime / technology / subsystems / spec text)
  - old: Hidden-sector / light dark matter, roughly 0.5-1000 MeV/c^2 (electron-recoil channel)
  - new: Hidden-sector / light dark matter, roughly 0.5-1000 MeV/c² (electron-recoil channel)

### data/atlas/experiments/damic.json

- `/energy_regime/value` (energy_regime / technology / subsystems / spec text)
  - old: WIMPs of a few GeV/c^2 (silicon target); low-energy ionization excess near 100 eV under continued study
  - new: WIMPs of a few GeV/c² (silicon target); low-energy ionization excess near 100 eV under continued study
- `/key_specs/0/quantity/display` (quantity display)
  - old: 7 x 16-Mpixel CCDs, 6.0 g each (~42 g total)
  - new: 7 × 16-Mpixel CCDs, 6.0 g each (~42 g total)

### data/atlas/experiments/darkside-50.json

- `/key_specs/0/quantity/note` (provenance note)
  - old: "50 kg" is the nominal/design active mass used in the experiment's own name and the LNGS/collaboration pages. The first-results paper measured a more precise active mass of (46.4+-0.7) kg (arXiv:1410.0653, abstract).
  - new: "50 kg" is the nominal/design active mass used in the experiment's own name and the LNGS/collaboration pages. The first-results paper measured a more precise active mass of (46.4±0.7) kg (arXiv:1410.0653, abstract).
- `/key_specs/2/quantity/display` (quantity display)
  - old: 6e-43 cm^2 at 3 GeV/c^2 (90% CL)
  - new: 6 × 10⁻⁴³ cm² at 3 GeV/c² (90% CL)
- `/summary/technical` (summary.technical)
  - old: Dual-phase liquid argon TPC, ~50 kg active mass, in LNGS Hall C. First physics data (atmospheric argon) from late 2013; refilled with low-radioactivity underground argon in April 2015. Operated overall from 2013 to 2020 per LNGS's own page. Its final published analysis (2023) used the entire low-radioactivity-argon dataset to set a 90% CL limit of 6e-43 cm^2 for a 3 GeV/c^2 WIMP.
  - new: Dual-phase liquid argon TPC, ~50 kg active mass, in LNGS Hall C. First physics data (atmospheric argon) from late 2013; refilled with low-radioactivity underground argon in April 2015. Operated overall from 2013 to 2020 per LNGS's own page. Its final published analysis (2023) used the entire low-radioactivity-argon dataset to set a 90% CL limit of 6 × 10⁻⁴³ cm² for a 3 GeV/c² WIMP.

### data/atlas/experiments/daya-bay.json

- `/physics_goals/0/value` (physics_goals / unique_capabilities)
  - old: Measure the neutrino mixing angle theta_13 using reactor antineutrino disappearance
  - new: Measure the neutrino mixing angle θ₁₃ using reactor antineutrino disappearance
- `/summary/technical` (summary.technical)
  - old: Reactor-antineutrino oscillation experiment using up to eight functionally identical Gd-doped liquid-scintillator antineutrino detectors at near (470 m, 576 m) and far (1648 m) underground halls from six 2.9 GW_th reactor cores at the Daya Bay/Ling Ao nuclear power complex, Guangdong, China. Its 2012 result was the first observation of a non-zero theta_13 mixing angle via reactor antineutrino disappearance.
  - new: Reactor-antineutrino oscillation experiment using up to eight functionally identical Gd-doped liquid-scintillator antineutrino detectors at near (470 m, 576 m) and far (1648 m) underground halls from six 2.9 GW_th reactor cores at the Daya Bay/Ling Ao nuclear power complex, Guangdong, China. Its 2012 result was the first observation of a non-zero θ₁₃ mixing angle via reactor antineutrino disappearance.

### data/atlas/experiments/deap-3600.json

- `/summary/technical` (summary.technical)
  - old: Single-phase liquid argon scintillation detector (no drift field, no ionization/charge readout) at SNOLAB's 2 km level (6000 m.w.e.). Design target of 3600 kg LAr (~3300 kg maintained fill since Nov 2016), 1000 kg fiducial mass within a 55 cm radius, viewed by 255 8-inch Hamamatsu R5912-HQE PMTs. Sets the leading argon-target WIMP-nucleon exclusion limits above ~30 GeV/c2 and searches for superheavy multi-scattering dark matter; currently in a hardware upgrade phase toward a further ('third') fill.
  - new: Single-phase liquid argon scintillation detector (no drift field, no ionization/charge readout) at SNOLAB's 2 km level (6000 m.w.e.). Design target of 3600 kg LAr (~3300 kg maintained fill since Nov 2016), 1000 kg fiducial mass within a 55 cm radius, viewed by 255 8-inch Hamamatsu R5912-HQE PMTs. Sets the leading argon-target WIMP-nucleon exclusion limits above ~30 GeV/c² and searches for superheavy multi-scattering dark matter; currently in a hardware upgrade phase toward a further ('third') fill.

### data/atlas/experiments/delphi.json

- `/key_specs/0/quantity/display` (quantity display)
  - old: ~10 m long x 10 m diameter
  - new: ~10 m long × 10 m diameter

### data/atlas/experiments/double-chooz.json

- `/physics_goals/0/value` (physics_goals / unique_capabilities)
  - old: Measure or set a limit on the theta_13 neutrino mixing angle via reactor antineutrino disappearance
  - new: Measure or set a limit on the θ₁₃ neutrino mixing angle via reactor antineutrino disappearance

### data/atlas/experiments/e949.json

- `/physics_goals/0/value` (physics_goals / unique_capabilities)
  - old: Search for and measure the branching ratio of the rare kaon decay K+ -> pi+ nu nubar using stopped kaons, as the successor to E787
  - new: Search for and measure the branching ratio of the rare kaon decay K⁺ → π⁺ ν ν̄ using stopped kaons, as the successor to E787
- `/summary/technical` (summary.technical)
  - old: Stopped-kaon experiment at Brookhaven (successor to E787) measuring K+ -> pi+ nu nubar; by its first year of physics running (per a September 2004 paper) had collected 1.8x10^12 stopped kaons, giving a combined E787+E949 branching ratio of (1.47+1.30-0.89)x10^-10; the final combined analysis (PRD 79, 092004, 2009) found seven total signal events and Br = (1.73+1.15-1.05)x10^-10.
  - new: Stopped-kaon experiment at Brookhaven (successor to E787) measuring K⁺ → π⁺ ν ν̄; by its first year of physics running (per a September 2004 paper) had collected 1.8×10¹² stopped kaons, giving a combined E787+E949 branching ratio of (1.47+1.30−0.89)×10⁻¹⁰; the final combined analysis (PRD 79, 092004, 2009) found seven total signal events and Br = (1.73+1.15−1.05)×10⁻¹⁰.

### data/atlas/experiments/edelweiss.json

- `/energy_regime/value` (energy_regime / technology / subsystems / spec text)
  - old: Sub-GeV dark matter (32-100 MeV/c^2 via the Migdal effect) and traditional WIMP masses via nuclear recoils
  - new: Sub-GeV dark matter (32-100 MeV/c² via the Migdal effect) and traditional WIMP masses via nuclear recoils
- `/summary/technical` (summary.technical)
  - old: Cryogenic germanium bolometer dark matter search at the Laboratoire Souterrain de Modane; the current sub-GeV programme uses a 200 g Ge detector with an NbSi transition-edge sensor and Neganov-Trofimov-Luke phonon amplification, reaching a 4.46 eV electron-recoil resolution and a 30 eV analysis threshold, searching for WIMPs down to 32 MeV/c^2 via the Migdal effect (2022-2024 results); a follow-on 'CRYOSEL' detector design is under development. Earlier EDELWEISS/EDELWEISS-II/III generations are not richly documented in this record for lack of a reachable official source this session.
  - new: Cryogenic germanium bolometer dark matter search at the Laboratoire Souterrain de Modane; the current sub-GeV programme uses a 200 g Ge detector with an NbSi transition-edge sensor and Neganov-Trofimov-Luke phonon amplification, reaching a 4.46 eV electron-recoil resolution and a 30 eV analysis threshold, searching for WIMPs down to 32 MeV/c² via the Migdal effect (2022-2024 results); a follow-on 'CRYOSEL' detector design is under development. Earlier EDELWEISS/EDELWEISS-II/III generations are not richly documented in this record for lack of a reachable official source this session.

### data/atlas/experiments/exo-200.json

- `/summary/technical` (summary.technical)
  - old: EXO-200 (Enriched Xenon Observatory): cylindrical liquid-xenon time projection chamber (136Xe-enriched to 80.6%) at WIPP, ~655 m underground. Operated 2011-2018 with a pause for a WIPP underground incident unrelated to the experiment; final dataset totalled 234.1 kg·yr exposure, setting T1/2 0ν > 3.5x10^25 yr (90% C.L.). Predecessor to nEXO.
  - new: EXO-200 (Enriched Xenon Observatory): cylindrical liquid-xenon time projection chamber (136Xe-enriched to 80.6%) at WIPP, ~655 m underground. Operated 2011-2018 with a pause for a WIPP underground incident unrelated to the experiment; final dataset totalled 234.1 kg·yr exposure, setting T1/2 0ν > 3.5×10²⁵ yr (90% C.L.). Predecessor to nEXO.

### data/atlas/experiments/gallex-gno.json

- `/summary/technical` (summary.technical)
  - old: Radiochemical gallium solar-neutrino experiment at LNGS: 30.3 t gallium (as 101 t GaCl3-HCl solution), sensitive to pp-chain neutrinos via the 71Ga->71Ge reaction. Ran as GALLEX 1991-1997 (73.1 SNU capture rate) then as GNO 1998-2003 (62.9 SNU), led by the Max-Planck-Institut für Kernphysik, Heidelberg, with French, German, Italian, Israeli, Polish and American participation.
  - new: Radiochemical gallium solar-neutrino experiment at LNGS: 30.3 t gallium (as 101 t GaCl3-HCl solution), sensitive to pp-chain neutrinos via the 71Ga→71Ge reaction. Ran as GALLEX 1991-1997 (73.1 SNU capture rate) then as GNO 1998-2003 (62.9 SNU), led by the Max-Planck-Institut für Kernphysik, Heidelberg, with French, German, Italian, Israeli, Polish and American participation.

### data/atlas/experiments/gerda.json

- `/key_specs/1/quantity/note` (provenance note)
  - old: Recorded as a lower limit, not a measured value; unit 'yr' used descriptively (the ontology's `time` dimension units do not include a native way to express 10^26 years, so `display` carries the authoritative figure).
  - new: Recorded as a lower limit, not a measured value; unit 'yr' used descriptively (the ontology's `time` dimension units do not include a native way to express 10²⁶ years, so `display` carries the authoritative figure).
- `/summary/technical` (summary.technical)
  - old: GERmanium Detector Array (GERDA): search for neutrinoless double-beta decay of 76Ge using bare enriched-germanium detectors operated in a 64 m3 liquid-argon cryostat in Hall A of LNGS. Phase I (2011-2013) and Phase II (2015-2019) accumulated 127.2 kg·yr of exposure and set T1/2 > 1.8x10^26 yr (90% C.L.); superseded by LEGEND-200.
  - new: GERmanium Detector Array (GERDA): search for neutrinoless double-beta decay of 76Ge using bare enriched-germanium detectors operated in a 64 m³ liquid-argon cryostat in Hall A of LNGS. Phase I (2011-2013) and Phase II (2015-2019) accumulated 127.2 kg·yr of exposure and set T1/2 > 1.8×10²⁶ yr (90% C.L.); superseded by LEGEND-200.

### data/atlas/experiments/grand.json

- `/intervals/0/note` (provenance note)
  - old: Start is the 2018 white paper's submission date (arXiv v1, 23 Oct 2018); the full 200,000-antenna GRAND array (20 arrays x 10 000 antennas, stated in the quote; the paper also gives the total of 200 000 antennas) remains at the proposal stage as of the most recent prototype paper fetched (2026). This interval alone would leave experiment status 'proposed', but see the commissioning interval below for the GRANDProto300 prototype that has actually been deployed and is taking data (A3: a realised interval knocks out a merely-proposed one covering the same time).
  - new: Start is the 2018 white paper's submission date (arXiv v1, 23 Oct 2018); the full 200,000-antenna GRAND array (20 arrays × 10 000 antennas, stated in the quote; the paper also gives the total of 200 000 antennas) remains at the proposal stage as of the most recent prototype paper fetched (2026). This interval alone would leave experiment status 'proposed', but see the commissioning interval below for the GRANDProto300 prototype that has actually been deployed and is taking data (A3: a realised interval knocks out a merely-proposed one covering the same time).

### data/atlas/experiments/h-e-s-s.json

- `/key_specs/0/quantity/display` (quantity display)
  - old: 4 x 12 m telescopes
  - new: 4 × 12 m telescopes

### data/atlas/experiments/homestake.json

- `/key_specs/0/quantity/display` (quantity display)
  - old: 380 m3 (100,000 gallons) perchloroethylene
  - new: 380 m³ (100,000 gallons) perchloroethylene
- `/summary/technical` (summary.technical)
  - old: Radiochemical chlorine-argon solar-neutrino experiment in the Homestake Gold Mine, Lead, South Dakota, 1478 m (4850 ft) underground; 380 m3 (100,000 gal) perchloroethylene target. Operated continuously 1970-1994, measuring a 37Ar production rate of 2.56±0.16(stat)±0.16(syst) SNU, about one-third of the Standard Solar Model prediction -- the original 'solar neutrino problem', later resolved by neutrino oscillation (SNO, Super-Kamiokande).
  - new: Radiochemical chlorine-argon solar-neutrino experiment in the Homestake Gold Mine, Lead, South Dakota, 1478 m (4850 ft) underground; 380 m³ (100,000 gal) perchloroethylene target. Operated continuously 1970-1994, measuring a 37Ar production rate of 2.56±0.16(stat)±0.16(syst) SNU, about one-third of the Standard Solar Model prediction -- the original 'solar neutrino problem', later resolved by neutrino oscillation (SNO, Super-Kamiokande).

### data/atlas/experiments/hyper-kamiokande.json

- `/intervals/1/note` (provenance note)
  - old: Sub-milestones: cavern excavation expected complete 2024 per the same 2024 status article; the 2026 cavern-engineering paper (arXiv:2602.14810) reports the 69 m x 94 m cavern excavation complete; the official news page's most recent entry (4 Aug 2026, in Japanese) reports the water-tank lining work complete.
  - new: Sub-milestones: cavern excavation expected complete 2024 per the same 2024 status article; the 2026 cavern-engineering paper (arXiv:2602.14810) reports the 69 m × 94 m cavern excavation complete; the official news page's most recent entry (4 Aug 2026, in Japanese) reports the water-tank lining work complete.
- `/summary/technical` (summary.technical)
  - old: Next-generation underground water Cherenkov detector under construction in the Tochibora mine, Kamioka (69 m x 94 m cavern, excavation complete): 68 m diameter x 71 m height tank, 260 kt total / 188 kt fiducial mass, on the order of 20,000 new high-sensitivity photosensors. Approved by the Japanese government 12 February 2020; cavern excavation began October 2022. Will serve as the far detector (~295 km, 2.5 degree off-axis) for the upgraded J-PARC neutrino beam as T2K's successor.
  - new: Next-generation underground water Cherenkov detector under construction in the Tochibora mine, Kamioka (69 m × 94 m cavern, excavation complete): 68 m diameter x 71 m height tank, 260 kt total / 188 kt fiducial mass, on the order of 20,000 new high-sensitivity photosensors. Approved by the Japanese government 12 February 2020; cavern excavation began October 2022. Will serve as the far detector (~295 km, 2.5 degree off-axis) for the upgraded J-PARC neutrino beam as T2K's successor.

### data/atlas/experiments/k2k.json

- `/physics_goals/1/value` (physics_goals / unique_capabilities)
  - old: Measure muon-neutrino disappearance to probe the neutrino mass-squared difference around Delta m^2 ~ 1e-2 eV^2
  - new: Measure muon-neutrino disappearance to probe the neutrino mass-squared difference around Δm² ~ 10⁻² eV²
- `/summary/technical` (summary.technical)
  - old: Accelerator neutrino oscillation experiment: 12 GeV protons from KEK-PS on an aluminium target, decay-pipe muon-neutrino beam (mean energy ~1.5 GeV) monitored by a near detector complex at KEK, observed 250 km away at Super-Kamiokande. Ran June 1999 - November 2004; reported muon-neutrino disappearance consistent with oscillation at 4.3 sigma (Phys. Rev. D 74, 072003, 2006). Direct predecessor of T2K.
  - new: Accelerator neutrino oscillation experiment: 12 GeV protons from KEK-PS on an aluminium target, decay-pipe muon-neutrino beam (mean energy ~1.5 GeV) monitored by a near detector complex at KEK, observed 250 km away at Super-Kamiokande. Ran June 1999 - November 2004; reported muon-neutrino disappearance consistent with oscillation at 4.3σ (Phys. Rev. D 74, 072003, 2006). Direct predecessor of T2K.

### data/atlas/experiments/kamiokande.json

- `/key_specs/0/quantity/display` (quantity display)
  - old: 948 x 50cm PMTs
  - new: 948 × 50cm PMTs

### data/atlas/experiments/kamland-zen.json

- `/summary/technical` (summary.technical)
  - old: KamLAND-Zen: 745 kg of xenon (enriched in 136Xe) dissolved in liquid scintillator inside a balloon suspended within the KamLAND detector at Kamioka. The KamLAND-Zen 800 phase's complete dataset (2.1 t·yr exposure) sets T1/2 0ν > 3.8x10^26 yr (90% C.L.), improving on the prior phase's 970 kg·yr / 2.3x10^26 yr limit.
  - new: KamLAND-Zen: 745 kg of xenon (enriched in 136Xe) dissolved in liquid scintillator inside a balloon suspended within the KamLAND detector at Kamioka. The KamLAND-Zen 800 phase's complete dataset (2.1 t·yr exposure) sets T1/2 0ν > 3.8×10²⁶ yr (90% C.L.), improving on the prior phase's 970 kg·yr / 2.3×10²⁶ yr limit.

### data/atlas/experiments/karmen.json

- `/summary/technical` (summary.technical)
  - old: Liquid-scintillator calorimeter (56 t, 65 m^3 active volume) at the ISIS spallation neutron source, Rutherford Appleton Laboratory, 17.7 m from the beam-stop target at 100 degrees to the proton beam. Ran as KARMEN 1 from 1990 and, after an outer-veto upgrade in 1996, as KARMEN 2 from February 1997 to March 2001, setting limits on nu_e disappearance and on nu_mu_bar -> nu_e_bar appearance that excluded much of the LSND-favoured oscillation parameter space.
  - new: Liquid-scintillator calorimeter (56 t, 65 m³ active volume) at the ISIS spallation neutron source, Rutherford Appleton Laboratory, 17.7 m from the beam-stop target at 100 degrees to the proton beam. Ran as KARMEN 1 from 1990 and, after an outer-veto upgrade in 1996, as KARMEN 2 from February 1997 to March 2001, setting limits on νe disappearance and on ν̄μ → ν̄e appearance that excluded much of the LSND-favoured oscillation parameter space.

### data/atlas/experiments/koto.json

- `/physics_goals/0/value` (physics_goals / unique_capabilities)
  - old: Measure or bound the branching ratio of the CP-violating rare decay KL -> pi0 nu nubar
  - new: Measure or bound the branching ratio of the CP-violating rare decay KL → π⁰ ν ν̄
- `/summary/technical` (summary.technical)
  - old: J-PARC E14 KOTO: fixed-target experiment at the J-PARC Hadron Experimental Facility measuring/bounding the branching ratio of the CP-violating decay KL -> pi0 nu nubar. First physics run May 2013 (100 hours, 24 kW beam); physics running resumed April 2015; has published results from 2015, 2016-2018, 2018 and 2021 data, most recently in February 2025; successor to the KEK-PS E391a experiment.
  - new: J-PARC E14 KOTO: fixed-target experiment at the J-PARC Hadron Experimental Facility measuring/bounding the branching ratio of the CP-violating decay KL → π⁰ ν ν̄. First physics run May 2013 (100 hours, 24 kW beam); physics running resumed April 2015; has published results from 2015, 2016-2018, 2018 and 2021 data, most recently in February 2025; successor to the KEK-PS E391a experiment.

### data/atlas/experiments/ktev.json

- `/physics_goals/0/value` (physics_goals / unique_capabilities)
  - old: Measure direct CP violation in neutral kaon decays (Re(epsilon'/epsilon)) and search for rare KL decays
  - new: Measure direct CP violation in neutral kaon decays (Re(ε′/ε)) and search for rare KL decays
- `/summary/technical` (summary.technical)
  - old: Fermilab fixed-target kaon experiment (jointly E799-II and E832, together called KTeV / 'Kaons at the Tevatron'), designed 1992, measuring direct CP violation (Re(epsilon'/epsilon)) and rare KL decays; announced its landmark direct-CP-violation observation in 1999. Contemporary and complementary to CERN's NA48.
  - new: Fermilab fixed-target kaon experiment (jointly E799-II and E832, together called KTeV / 'Kaons at the Tevatron'), designed 1992, measuring direct CP violation (Re(ε′/ε)) and rare KL decays; announced its landmark direct-CP-violation observation in 1999. Contemporary and complementary to CERN's NA48.

### data/atlas/experiments/legend.json

- `/summary/technical` (summary.technical)
  - old: Staged germanium 0νββ programme combining GERDA and MAJORANA DEMONSTRATOR technology. LEGEND-200 (up to 200 kg of enriched-76Ge detectors in liquid argon at LNGS) began data taking in 2023 and reported a first-result exposure of 61 kg·yr and T1/2 0ν > 0.5x10^26 yr (90% CL); a combined GERDA+MAJORANA+LEGEND-200 analysis gives T1/2 0ν > 1.9x10^26 yr (90% CL). LEGEND-1000 (1 t enriched Ge) is in preparation, targeting a discovery sensitivity beyond 10^28 yr.
  - new: Staged germanium 0νββ programme combining GERDA and MAJORANA DEMONSTRATOR technology. LEGEND-200 (up to 200 kg of enriched-76Ge detectors in liquid argon at LNGS) began data taking in 2023 and reported a first-result exposure of 61 kg·yr and T1/2 0ν > 0.5×10²⁶ yr (90% CL); a combined GERDA+MAJORANA+LEGEND-200 analysis gives T1/2 0ν > 1.9×10²⁶ yr (90% CL). LEGEND-1000 (1 t enriched Ge) is in preparation, targeting a discovery sensitivity beyond 10²⁸ yr.

### data/atlas/experiments/lhaaso.json

- `/physics_goals/0/value` (physics_goals / unique_capabilities)
  - old: Measure the cosmic-ray energy spectrum, composition and anisotropy from 10^12 to 10^18 eV, and survey the sky as a wide-aperture gamma-ray telescope with sensitivity to PeV-scale ('PeVatron') sources.
  - new: Measure the cosmic-ray energy spectrum, composition and anisotropy from 10¹² to 10¹⁸ eV, and survey the sky as a wide-aperture gamma-ray telescope with sensitivity to PeV-scale ('PeVatron') sources.
- `/summary/technical` (summary.technical)
  - old: Multi-component air-shower observatory at 4410 m on Haizi Mountain, Sichuan, China, combining water-Cherenkov, muon/electromagnetic and Cherenkov-telescope sub-arrays (per public description; individual KM2A/WCDA/WFCTA specifications not sourced this session) to cover cosmic-ray energies of 10^12-10^18 eV and gamma rays above 100 TeV. Reported as already operating by May 2021, with UHE photons up to 1.4 PeV detected from twelve Galactic sources.
  - new: Multi-component air-shower observatory at 4410 m on Haizi Mountain, Sichuan, China, combining water-Cherenkov, muon/electromagnetic and Cherenkov-telescope sub-arrays (per public description; individual KM2A/WCDA/WFCTA specifications not sourced this session) to cover cosmic-ray energies of 10¹²-10¹⁸ eV and gamma rays above 100 TeV. Reported as already operating by May 2021, with UHE photons up to 1.4 PeV detected from twelve Galactic sources.

### data/atlas/experiments/lhcb.json

- `/notes/1` (notes[])
  - old: A joint CMS+LHCb result, result:cms-lhcb-bs-to-mumu-observation-2015, already exists (owned by the cern-cms workstream) for the 2015 observation of the rare decay Bs0->mu+mu-; it is not duplicated here and is not referenced in result_ids since that field is derived/not authored (A1), but is worth noting as a related joint LHCb result.
  - new: A joint CMS+LHCb result, result:cms-lhcb-bs-to-mumu-observation-2015, already exists (owned by the cern-cms workstream) for the 2015 observation of the rare decay Bs⁰→μ⁺μ⁻; it is not duplicated here and is not referenced in result_ids since that field is derived/not authored (A1), but is worth noting as a related joint LHCb result.
- `/unique_capabilities/0/value` (physics_goals / unique_capabilities)
  - old: A single forward-arm spectrometer (not a 4-pi enclosure) optimised for the forward-peaked production of b and c hadrons at a hadron collider
  - new: A single forward-arm spectrometer (not a 4π enclosure) optimised for the forward-peaked production of b and c hadrons at a hadron collider

### data/atlas/experiments/lhcf.json

- `/energy_regime/note` (provenance note)
  - old: Per the INSPIRE record's description, LHCf's detectors and electronics are optimised to operate during early LHC commissioning at luminosity below 10^30 cm^-2 s^-1.
  - new: Per the INSPIRE record's description, LHCf's detectors and electronics are optimised to operate during early LHC commissioning at luminosity below 10³⁰ cm⁻² s⁻¹.
- `/summary/technical` (summary.technical)
  - old: Forward-physics/cosmic-ray-calibration experiment: two compact imaging sampling calorimeters (tungsten plates, plastic scintillator, position-sensitive sensors) at zero-degree collision angle, +-140 m from LHC interaction point 1, covering pseudo-rapidity > 8.4. Proposed and approved May 2004; operated (mainly during early low-luminosity periods of each LHC run) from first collisions (23 Nov 2009) through June 2026; off since CERN's Long Shutdown 3 began.
  - new: Forward-physics/cosmic-ray-calibration experiment: two compact imaging sampling calorimeters (tungsten plates, plastic scintillator, position-sensitive sensors) at zero-degree collision angle, ±140 m from LHC interaction point 1, covering pseudo-rapidity > 8.4. Proposed and approved May 2004; operated (mainly during early low-luminosity periods of each LHC run) from first collisions (23 Nov 2009) through June 2026; off since CERN's Long Shutdown 3 began.
- `/unique_capabilities/0/value` (physics_goals / unique_capabilities)
  - old: Compact imaging calorimeters at zero-degree collision angle, sensitive to the pseudo-rapidity range greater than 8.4, giving LHCf access to particle production kinematics equivalent to a laboratory cosmic-ray energy of 10^17 eV
  - new: Compact imaging calorimeters at zero-degree collision angle, sensitive to the pseudo-rapidity range greater than 8.4, giving LHCf access to particle production kinematics equivalent to a laboratory cosmic-ray energy of 10¹⁷ eV

### data/atlas/experiments/lsnd.json

- `/summary/technical` (summary.technical)
  - old: 167 t mineral-oil/scintillator (Cherenkov + scintillation) detector at LAMPF/LANSCE, Los Alamos, 30 m from the A6 beam-stop neutrino source, using an 800 MeV proton beam. Took data 1993-1998 and reported a statistically significant excess of nu_e_bar candidate events consistent with nu_mu_bar -> nu_e_bar oscillation at short baseline, a result in tension with standard three-flavour oscillation and a long-standing driver of sterile-neutrino searches.
  - new: 167 t mineral-oil/scintillator (Cherenkov + scintillation) detector at LAMPF/LANSCE, Los Alamos, 30 m from the A6 beam-stop neutrino source, using an 800 MeV proton beam. Took data 1993-1998 and reported a statistically significant excess of ν̄e candidate events consistent with ν̄μ → ν̄e oscillation at short baseline, a result in tension with standard three-flavour oscillation and a long-standing driver of sterile-neutrino searches.

### data/atlas/experiments/lux.json

- `/physics_goals/value/0` (physics_goals / unique_capabilities)
  - old: Detect or exclude WIMPs with a spin-independent cross section per nucleon of 2e-46 cm2
  - new: Detect or exclude WIMPs with a spin-independent cross section per nucleon of 2 × 10⁻⁴⁶ cm²
- `/summary/technical` (summary.technical)
  - old: Dual-phase xenon TPC, 370 kg total / 250 kg active, in the Davis Cavern at SURF. WS2013 (85.3 live days, 118 kg fiducial) and WS2014-16 (332.0 live days) gave a combined 3.35e4 kg day exposure and a spin-independent limit of 1.1e-46 cm2 at 50 GeV/c2. Direct predecessor of LZ.
  - new: Dual-phase xenon TPC, 370 kg total / 250 kg active, in the Davis Cavern at SURF. WS2013 (85.3 live days, 118 kg fiducial) and WS2014-16 (332.0 live days) gave a combined 3.35 × 10⁴ kg day exposure and a spin-independent limit of 1.1 × 10⁻⁴⁶ cm² at 50 GeV/c². Direct predecessor of LZ.

### data/atlas/experiments/lz.json

- `/energy_regime/value` (energy_regime / technology / subsystems / spec text)
  - old: keV-scale nuclear recoils from WIMPs of a few GeV/c2 to hundreds of TeV/c2
  - new: keV-scale nuclear recoils from WIMPs of a few GeV/c² to hundreds of TeV/c²
- `/summary/technical` (summary.technical)
  - old: Second-generation G2 direct-detection experiment using a dual-phase xenon TPC with 7 active tonnes (5.5 t SR1 fiducial) in the Davis Cavern at SURF (~1480 m rock, ~4300 m.w.e.). SR1 (60 live days, Dec 2021 - May 2022) set a spin-independent WIMP-nucleon limit of 9.2e-48 cm2 at 36 GeV/c2; the 4.2 tonne-year WS2024 analysis reached 2.2e-48 cm2 at 40 GeV/c2. The programme targets 1,000 live days and also searches for 136Xe double beta decay.
  - new: Second-generation G2 direct-detection experiment using a dual-phase xenon TPC with 7 active tonnes (5.5 t SR1 fiducial) in the Davis Cavern at SURF (~1480 m rock, ~4300 m.w.e.). SR1 (60 live days, Dec 2021 - May 2022) set a spin-independent WIMP-nucleon limit of 9.2 × 10⁻⁴⁸ cm² at 36 GeV/c²; the 4.2 tonne-year WS2024 analysis reached 2.2 × 10⁻⁴⁸ cm² at 40 GeV/c². The programme targets 1,000 live days and also searches for 136Xe double beta decay.

### data/atlas/experiments/majorana-demonstrator.json

- `/summary/technical` (summary.technical)
  - old: MAJORANA DEMONSTRATOR: array of modular p-type point-contact HPGe detector arrays (up to 40.4 kg total, 27.2 kg enriched to ~88% in 76Ge) in vacuum cryostats, located in the Davis Campus at the 4850 Level (1478 m) of SURF. Installation began March 2012; final result accumulated 64.5 kg·yr of enriched exposure and set T1/2 0ν > 8.3x10^25 yr (90% C.L.). Its techniques and personnel carried into LEGEND.
  - new: MAJORANA DEMONSTRATOR: array of modular p-type point-contact HPGe detector arrays (up to 40.4 kg total, 27.2 kg enriched to ~88% in 76Ge) in vacuum cryostats, located in the Davis Campus at the 4850 Level (1478 m) of SURF. Installation began March 2012; final result accumulated 64.5 kg·yr of enriched exposure and set T1/2 0ν > 8.3×10²⁵ yr (90% C.L.). Its techniques and personnel carried into LEGEND.

### data/atlas/experiments/mathusla.json

- `/key_specs/0/quantity/display` (quantity display)
  - old: 11 m tall (proposed 40 m x 40 m x 11 m decay volume)
  - new: 11 m tall (proposed 40 m × 40 m × 11 m decay volume)
- `/summary/technical` (summary.technical)
  - old: Proposed large-volume (40 m x 40 m x 11 m, under revision) surface detector near the LHC, designed to reconstruct displaced decay vertices of neutral long-lived particles produced in pp collisions, with a background-free environment enabled by its surface location and distance from the interaction point; proposed to come online with the HL-LHC upgrade (~2029).
  - new: Proposed large-volume (40 m × 40 m × 11 m, under revision) surface detector near the LHC, designed to reconstruct displaced decay vertices of neutral long-lived particles produced in pp collisions, with a background-free environment enabled by its surface location and distance from the interaction point; proposed to come online with the HL-LHC upgrade (~2029).
- `/unique_capabilities/0/value` (physics_goals / unique_capabilities)
  - old: A large (proposed 40 m x 40 m x 11 m) surface detector, shielded from beam-related backgrounds by its distance and position above ground, giving a background-free environment with no trigger limitations for reconstructing displaced LLP decay vertices; can also function as a cosmic-ray telescope
  - new: A large (proposed 40 m × 40 m × 11 m) surface detector, shielded from beam-related backgrounds by its distance and position above ground, giving a background-free environment with no trigger limitations for reconstructing displaced LLP decay vertices; can also function as a cosmic-ray telescope

### data/atlas/experiments/meg-ii.json

- `/key_specs/0/quantity/display` (quantity display)
  - old: 6x10^-14
  - new: 6×10⁻¹⁴
- `/physics_goals/0/value` (physics_goals / unique_capabilities)
  - old: Search for the charged-lepton-flavor-violating decay mu+ -> e+ gamma with roughly an order of magnitude better sensitivity than MEG, targeting a branching-ratio sensitivity of 6x10^-14
  - new: Search for the charged-lepton-flavor-violating decay μ⁺ → e⁺ γ with roughly an order of magnitude better sensitivity than MEG, targeting a branching-ratio sensitivity of 6×10⁻¹⁴
- `/summary/technical` (summary.technical)
  - old: MEG II: upgrade of MEG on the PSI piE5 DC muon beamline, with an upgraded LXe calorimeter, new cylindrical drift chamber, timing counter and radiative decay counter, targeting a branching-ratio sensitivity of 6x10^-14 for mu+ -> e+ gamma. First physics run 2021; a ten-fold larger dataset collected 2022-2023 with data-taking continuing. See result:meg-ii-mu-to-e-gamma-limit-2024 for the first-dataset limit.
  - new: MEG II: upgrade of MEG on the PSI piE5 DC muon beamline, with an upgraded LXe calorimeter, new cylindrical drift chamber, timing counter and radiative decay counter, targeting a branching-ratio sensitivity of 6×10⁻¹⁴ for μ⁺ → e⁺ γ. First physics run 2021; a ten-fold larger dataset collected 2022-2023 with data-taking continuing. See result:meg-ii-mu-to-e-gamma-limit-2024 for the first-dataset limit.

### data/atlas/experiments/meg.json

- `/physics_goals/0/value` (physics_goals / unique_capabilities)
  - old: Search for the charged-lepton-flavor-violating decay mu+ -> e+ gamma down to a branching ratio of 10^-13
  - new: Search for the charged-lepton-flavor-violating decay μ⁺ → e⁺ γ down to a branching ratio of 10⁻¹³
- `/summary/technical` (summary.technical)
  - old: MEG (PSI-R-99-05): searched for mu+ -> e+ gamma using a liquid xenon calorimeter and a positron spectrometer (drift chamber + timing counter) on the PSI piE5 DC muon beamline. Data taking 2009-2013, 7.5x10^14 stopped muons on target; superseded by the upgraded MEG II. See result:meg-mu-to-e-gamma-limit-2016 for the final branching-ratio limit.
  - new: MEG (PSI-R-99-05): searched for μ⁺ → e⁺ γ using a liquid xenon calorimeter and a positron spectrometer (drift chamber + timing counter) on the PSI piE5 DC muon beamline. Data taking 2009-2013, 7.5×10¹⁴ stopped muons on target; superseded by the upgraded MEG II. See result:meg-mu-to-e-gamma-limit-2016 for the final branching-ratio limit.
- `/unique_capabilities/0/value` (physics_goals / unique_capabilities)
  - old: Combined a liquid xenon calorimeter with a positron spectrometer (drift chamber and timing counter) optimized on both the positron and gamma-ray sides for background-free operation at the 10^-13 branching-ratio level, using the world's most intense continuous (DC) muon beam at PSI
  - new: Combined a liquid xenon calorimeter with a positron spectrometer (drift chamber and timing counter) optimized on both the positron and gamma-ray sides for background-free operation at the 10⁻¹³ branching-ratio level, using the world's most intense continuous (DC) muon beam at PSI

### data/atlas/experiments/moedal.json

- `/key_specs/0/quantity/display` (quantity display)
  - old: 47 m^2
  - new: 47 m²
- `/summary/technical` (summary.technical)
  - old: Passive, non-electronic detector at LHC Point 8 (co-located with LHCb): 125 Nuclear Track Detector stacks (47 m^2 deployed plastic) plus ~1 t of paramagnetic trapping detectors and TimePix monitoring, searching for magnetic monopoles and other highly-ionizing BSM particles. Proposed February 1998, approved as the LHC's seventh experiment in December 2009; the MAPP extension was approved in 2021.
  - new: Passive, non-electronic detector at LHC Point 8 (co-located with LHCb): 125 Nuclear Track Detector stacks (47 m² deployed plastic) plus ~1 t of paramagnetic trapping detectors and TimePix monitoring, searching for magnetic monopoles and other highly-ionizing BSM particles. Proposed February 1998, approved as the LHC's seventh experiment in December 2009; the MAPP extension was approved in 2021.

### data/atlas/experiments/mu2e.json

- `/key_specs/0/quantity/display` (quantity display)
  - old: ~2.5x10^-17
  - new: ~2.5×10⁻¹⁷
- `/notes/1` (notes[])
  - old: Sensitivity-goal conflict: the INSPIRE experiment record (rank 3, closer to the original approved proposal) states 2.5x10^-17; a 2022 Mu2e collaboration status proceedings paper (rank 10) states 3x10^-17 for a staged Run-1+Run-2 plan. Both are recorded (primary value 2.5x10^-17, the other noted) rather than silently picking one; see the muons.md worklog Conflicts section.
  - new: Sensitivity-goal conflict: the INSPIRE experiment record (rank 3, closer to the original approved proposal) states 2.5×10⁻¹⁷; a 2022 Mu2e collaboration status proceedings paper (rank 10) states 3×10⁻¹⁷ for a staged Run-1+Run-2 plan. Both are recorded (primary value 2.5×10⁻¹⁷, the other noted) rather than silently picking one; see the muons.md worklog Conflicts section.
- `/physics_goals/0/value` (physics_goals / unique_capabilities)
  - old: Search for charged-lepton-flavor-violating, neutrino-less conversion of a muon to an electron in the field of an aluminum nucleus (mu- N -> e- N), a process forbidden in the Standard Model
  - new: Search for charged-lepton-flavor-violating, neutrino-less conversion of a muon to an electron in the field of an aluminum nucleus (μ⁻ N → e⁻ N), a process forbidden in the Standard Model
- `/summary/technical` (summary.technical)
  - old: Fermilab E973 (Mu2e): searches for coherent, neutrino-less mu- N -> e- N conversion in the field of an aluminum nucleus using a pulsed muon beam and a 25 m chain of three superconducting solenoids (production, transport, detector) feeding a straw-tube tracker, crystal calorimeter and cosmic-ray veto. Proposed 2008, approved 2010, CD-3 construction approval June 2016; as of the most recently fetched status report (2026-07) construction/installation is ongoing across all subsystems with initial data collection planned for 2027. No physics results have been produced yet.
  - new: Fermilab E973 (Mu2e): searches for coherent, neutrino-less μ⁻ N → e⁻ N conversion in the field of an aluminum nucleus using a pulsed muon beam and a 25 m chain of three superconducting solenoids (production, transport, detector) feeding a straw-tube tracker, crystal calorimeter and cosmic-ray veto. Proposed 2008, approved 2010, CD-3 construction approval June 2016; as of the most recently fetched status report (2026-07) construction/installation is ongoing across all subsystems with initial data collection planned for 2027. No physics results have been produced yet.

### data/atlas/experiments/mu3e.json

- `/key_specs/0/quantity/display` (quantity display)
  - old: 1x10^-16
  - new: 1×10⁻¹⁶
- `/physics_goals/0/value` (physics_goals / unique_capabilities)
  - old: Search for the lepton-flavor-violating decay of a positive muon into two positrons and one electron (mu+ -> e+e+e-) with a branching-ratio sensitivity of 10^-16
  - new: Search for the lepton-flavor-violating decay of a positive muon into two positrons and one electron (μ⁺ → e⁺e⁺e⁻) with a branching-ratio sensitivity of 10⁻¹⁶
- `/summary/technical` (summary.technical)
  - old: Mu3e (PSI, on the HiMB/piE5 beamline fed by accelerator:psi-hipa, referenced but owned by the 'facilities' workstream): searches for mu+ -> e+e+e- using an ultra-thin HV-MAPS silicon pixel tracker plus scintillating fibre and tile timing detectors, targeting a branching-ratio sensitivity of 10^-16. As of the most recently fetched official update (2026-09-24), the experiment had been craned into the PiE5 magnet after the third pixel layer was installed (2026-09-16); the detector remains under construction, a beam time was planned for October-November 2026, and no physics result has been produced yet.
  - new: Mu3e (PSI, on the HiMB/piE5 beamline fed by accelerator:psi-hipa, referenced but owned by the 'facilities' workstream): searches for μ⁺ → e⁺e⁺e⁻ using an ultra-thin HV-MAPS silicon pixel tracker plus scintillating fibre and tile timing detectors, targeting a branching-ratio sensitivity of 10⁻¹⁶. As of the most recently fetched official update (2026-09-24), the experiment had been craned into the PiE5 magnet after the third pixel layer was installed (2026-09-16); the detector remains under construction, a beam time was planned for October-November 2026, and no physics result has been produced yet.

### data/atlas/experiments/muon-g-2.json

- `/summary/technical` (summary.technical)
  - old: Fermilab E989: reuses the BNL E821 superconducting muon storage ring (7.112 m orbit radius, 1.45 T superferric field), relocated from Brookhaven in 2013, to remeasure the muon anomalous magnetic moment a_mu with higher statistics and reduced systematics than E821. Data-taking ran Runs 1-6, April 2018 to May 2023; the final combined result reached 127 ppb precision.
  - new: Fermilab E989: reuses the BNL E821 superconducting muon storage ring (7.112 m orbit radius, 1.45 T superferric field), relocated from Brookhaven in 2013, to remeasure the muon anomalous magnetic moment aμ with higher statistics and reduced systematics than E821. Data-taking ran Runs 1-6, April 2018 to May 2023; the final combined result reached 127 ppb precision.

### data/atlas/experiments/na48.json

- `/physics_goals/0/value` (physics_goals / unique_capabilities)
  - old: Measure direct CP violation in neutral kaon decays to two pions (the parameter Re(epsilon'/epsilon)) to determine whether CP violation arises directly in the decay process itself, not only in K0-K0bar mixing
  - new: Measure direct CP violation in neutral kaon decays to two pions (the parameter Re(ε′/ε)) to determine whether CP violation arises directly in the decay process itself, not only in K⁰-K̄⁰ mixing
- `/summary/technical` (summary.technical)
  - old: Fixed-target kaon experiment in the ECN3 cavern of the CERN SPS North Area (approved 1991), using concurrent KS/KL beams to measure direct CP violation (Re(epsilon'/epsilon) = (14.7 +- 2.2) x 10^-4, combining 1997-1999 and 2001 data). Continued as NA48/2 (2003-2004) studying charged-kaon CP violation and rare decays before the programme's infrastructure was reused by its successor, NA62.
  - new: Fixed-target kaon experiment in the ECN3 cavern of the CERN SPS North Area (approved 1991), using concurrent KS/KL beams to measure direct CP violation (Re(ε′/ε) = (14.7 ± 2.2) × 10⁻⁴, combining 1997-1999 and 2001 data). Continued as NA48/2 (2003-2004) studying charged-kaon CP violation and rare decays before the programme's infrastructure was reused by its successor, NA62.

### data/atlas/experiments/na62.json

- `/physics_goals/0/value` (physics_goals / unique_capabilities)
  - old: Measure the branching ratio of the very rare kaon decay K+ -> pi+ nu nubar to extract a percent-level measurement of the CKM matrix element |Vtd| and test the Standard Model
  - new: Measure the branching ratio of the very rare kaon decay K⁺ → π⁺ ν ν̄ to extract a percent-level measurement of the CKM matrix element |Vtd| and test the Standard Model
- `/summary/technical` (summary.technical)
  - old: Fixed-target kaon-decay experiment in the ECN3 cavern of the CERN SPS North Area, using a 400 GeV/c primary proton beam to produce a secondary/tertiary charged-kaon beam. Measures the branching ratio of K+ -> pi+ nu nubar via a decay-in-flight technique with GigaTracker beam-timing, RICH, LKr calorimeter and veto subsystems (arXiv:1703.08501). Constructed 2009-2014, commissioned 2014-2015, Run 1 data 2016-2018 (arXiv:2103.15389, 3.4 sigma evidence-level measurement), Run 2 from 2021 with upgraded beam intensity, reaching a 5 sigma observation with 2016-2022 data (arXiv:2412.12015) and a further refined measurement including 2023-2024 data reported in 2026.
  - new: Fixed-target kaon-decay experiment in the ECN3 cavern of the CERN SPS North Area, using a 400 GeV/c primary proton beam to produce a secondary/tertiary charged-kaon beam. Measures the branching ratio of K⁺ → π⁺ ν ν̄ via a decay-in-flight technique with GigaTracker beam-timing, RICH, LKr calorimeter and veto subsystems (arXiv:1703.08501). Constructed 2009-2014, commissioned 2014-2015, Run 1 data 2016-2018 (arXiv:2103.15389, 3.4σ evidence-level measurement), Run 2 from 2021 with upgraded beam intensity, reaching a 5σ observation with 2016-2022 data (arXiv:2412.12015) and a further refined measurement including 2023-2024 data reported in 2026.
- `/unique_capabilities/0/value` (physics_goals / unique_capabilities)
  - old: A decay-in-flight technique using a high-intensity (~750 MHz) unseparated hadron beam and precision timing (the GigaTracker beam spectrometer reaches 65 ps time resolution on tracks) to identify K+ -> pi+ nu nubar events against enormous backgrounds
  - new: A decay-in-flight technique using a high-intensity (~750 MHz) unseparated hadron beam and precision timing (the GigaTracker beam spectrometer reaches 65 ps time resolution on tracks) to identify K⁺ → π⁺ ν ν̄ events against enormous backgrounds

### data/atlas/experiments/na64.json

- `/unique_capabilities/0/value` (physics_goals / unique_capabilities)
  - old: Active beam-dump and missing-energy technique whose sensitivity to a hidden Z' coupling scales as epsilon^2 rather than epsilon^4 as in classical beam-dump searches
  - new: Active beam-dump and missing-energy technique whose sensitivity to a hidden Z' coupling scales as ε² rather than ε⁴ as in classical beam-dump searches

### data/atlas/experiments/news-g.json

- `/energy_regime/value` (energy_regime / technology / subsystems / spec text)
  - old: Sub-GeV/c^2 WIMPs (light dark matter)
  - new: Sub-GeV/c² WIMPs (light dark matter)
- `/physics_goals/value/0` (physics_goals / unique_capabilities)
  - old: Detect sub-GeV/c^2 WIMPs via single-ionization-electron sensitivity in spherical proportional counters
  - new: Detect sub-GeV/c² WIMPs via single-ionization-electron sensitivity in spherical proportional counters

### data/atlas/experiments/opal.json

- `/summary/technical` (summary.technical)
  - old: General-purpose LEP detector, roughly 12 m x 12 m x 12 m, with tracking detectors, calorimeters and muon detectors arranged in concentric layers ('like the layers of an onion') around the beam pipe. Approved by the CERN LEPC on 18 November 1982; ran from August 1989 to 2 November 2000 with about 200 physicists from 34 institutes in 8 countries.
  - new: General-purpose LEP detector, roughly 12 m × 12 m × 12 m, with tracking detectors, calorimeters and muon detectors arranged in concentric layers ('like the layers of an onion') around the beam pipe. Approved by the CERN LEPC on 18 November 1982; ran from August 1989 to 2 November 2000 with about 200 physicists from 34 institutes in 8 countries.

### data/atlas/experiments/opera.json

- `/summary/technical` (summary.technical)
  - old: Emulsion-cloud-chamber (lead/nuclear-emulsion 'brick') experiment in LNGS Hall C, receiving the CNGS muon-neutrino beam from the CERN SPS over a 732 km baseline. Took data 2008-2012 and reported discovery of nu_mu -> nu_tau appearance at 5.1 sigma significance from five candidate tau-neutrino interactions, confirming long-baseline neutrino oscillation in appearance mode.
  - new: Emulsion-cloud-chamber (lead/nuclear-emulsion 'brick') experiment in LNGS Hall C, receiving the CNGS muon-neutrino beam from the CERN SPS over a 732 km baseline. Took data 2008-2012 and reported discovery of νμ → ντ appearance at 5.1σ significance from five candidate tau-neutrino interactions, confirming long-baseline neutrino oscillation in appearance mode.

### data/atlas/experiments/pandax-4t.json

- `/key_specs/3/quantity/display` (quantity display)
  - old: 3.8e-47 cm^2 at 30 GeV/c^2 (90% CL)
  - new: 3.8 × 10⁻⁴⁷ cm² at 30 GeV/c² (90% CL)
- `/summary/technical` (summary.technical)
  - old: Dual-target-scale xenon TPC (6 t total xenon inventory, 4 t sensitive target) at CJPL-II, 2400 m underground. Commissioned 2021; the commissioning-run result (3.7 t target, 0.63 t-y exposure) excluded spin-independent WIMP-nucleon cross sections above 3.8e-47 cm^2 at 30 GeV/c^2 (90% CL).
  - new: Dual-target-scale xenon TPC (6 t total xenon inventory, 4 t sensitive target) at CJPL-II, 2400 m underground. Commissioned 2021; the commissioning-run result (3.7 t target, 0.63 t-y exposure) excluded spin-independent WIMP-nucleon cross sections above 3.8 × 10⁻⁴⁷ cm² at 30 GeV/c² (90% CL).

### data/atlas/experiments/phenix.json

- `/notes/2` (notes[])
  - old: key_specs left empty: central-arm/muon-arm acceptance and magnet field figures found via search (e.g. |eta|<0.35 central arms, 0.72 T*m muon magnet) come only from secondary characterisations of the PHENIX detector-overview and muon-arm NIM A499 (2003) papers; the primary papers themselves (ScienceDirect, and a PDF at phenix.bnl.gov) could not be retrieved as readable text in this session, so per A17 these numbers are omitted rather than sourced from an unverified paraphrase. Recorded as a missing_field in coverage.
  - new: key_specs left empty: central-arm/muon-arm acceptance and magnet field figures found via search (e.g. |η|<0.35 central arms, 0.72 T*m muon magnet) come only from secondary characterisations of the PHENIX detector-overview and muon-arm NIM A499 (2003) papers; the primary papers themselves (ScienceDirect, and a PDF at phenix.bnl.gov) could not be retrieved as readable text in this session, so per A17 these numbers are omitted rather than sourced from an unverified paraphrase. Recorded as a missing_field in coverage.

### data/atlas/experiments/pierre-auger-observatory.json

- `/physics_goals/0/value` (physics_goals / unique_capabilities)
  - old: Determine the origin, mechanism and composition of the highest-energy cosmic rays, above 10^18 eV, using a hybrid surface-detector and fluorescence-telescope array too large for a single detector type to catch enough events.
  - new: Determine the origin, mechanism and composition of the highest-energy cosmic rays, above 10¹⁸ eV, using a hybrid surface-detector and fluorescence-telescope array too large for a single detector type to catch enough events.
- `/physics_goals/1/value` (physics_goals / unique_capabilities)
  - old: Measure the ultra-high-energy cosmic-ray spectrum and search for the predicted GZK suppression of the flux above about 4x10^19 eV.
  - new: Measure the ultra-high-energy cosmic-ray spectrum and search for the predicted GZK suppression of the flux above about 4×10¹⁹ eV.
- `/summary/technical` (summary.technical)
  - old: Hybrid ultra-high-energy cosmic-ray observatory combining a 3000 km^2 surface array of 1660 water-Cherenkov detector stations with 27 fluorescence telescopes in Mendoza Province, Argentina. Proposed 1995, construction from 2000, partial-array data taking from 2004, full array inaugurated November 2008; currently undergoing the AugerPrime upgrade (scintillator, radio and underground-muon detectors added atop the existing water-Cherenkov stations) begun November 2015.
  - new: Hybrid ultra-high-energy cosmic-ray observatory combining a 3000 km² surface array of 1660 water-Cherenkov detector stations with 27 fluorescence telescopes in Mendoza Province, Argentina. Proposed 1995, construction from 2000, partial-array data taking from 2004, full array inaugurated November 2008; currently undergoing the AugerPrime upgrade (scintillator, radio and underground-muon detectors added atop the existing water-Cherenkov stations) begun November 2015.
- `/unique_capabilities/0/value` (physics_goals / unique_capabilities)
  - old: Hybrid detection: a 3000 km^2 surface array of water-Cherenkov tanks sampling shower particles at ground level, cross-calibrated against 27 fluorescence telescopes that image the longitudinal development of air showers on clear, dark nights.
  - new: Hybrid detection: a 3000 km² surface array of water-Cherenkov tanks sampling shower particles at ground level, cross-calibrated against 27 fluorescence telescopes that image the longitudinal development of air showers on clear, dark nights.

### data/atlas/experiments/project-8.json

- `/key_specs/1/quantity/display` (quantity display)
  - old: ~0.04 eV/c^2 (40 meV)
  - new: ~0.04 eV/c² (40 meV)
- `/key_specs/1/quantity/note` (provenance note)
  - old: This is the long-term Phase IV design goal using atomic tritium, not a current achieved sensitivity. The ontology's `mass_energy` dimension does not define a meV unit, so value/unit are recorded in eV/c^2 (0.04) while `display` keeps the source's own wording (40 meV).
  - new: This is the long-term Phase IV design goal using atomic tritium, not a current achieved sensitivity. The ontology's `mass_energy` dimension does not define a meV unit, so value/unit are recorded in eV/c² (0.04) while `display` keeps the source's own wording (40 meV).

### data/atlas/experiments/reno.json

- `/physics_goals/0/value` (physics_goals / unique_capabilities)
  - old: Measure the neutrino mixing angle theta_13 via reactor antineutrino disappearance using near and far identical detectors
  - new: Measure the neutrino mixing angle θ₁₃ via reactor antineutrino disappearance using near and far identical detectors
- `/summary/technical` (summary.technical)
  - old: Reactor-antineutrino oscillation experiment at the Hanbit (Yonggwang) Nuclear Power Plant, Korea, with identical near (294 m) and far (1383 m) detectors from a 6 x 2.8 GW_th reactor array. Its 2012 result observed reactor antineutrino disappearance at 4.9σ, sin²(2θ₁₃)=0.113±0.013(stat)±0.019(syst). Data acquisition ran 2011-08 to 2023-03 (3800 live days); a final-dataset measurement (arXiv:2412.18711) reports sin²2θ₁₃=0.0920 and |Δm²_ee|=2.57e-3 eV².
  - new: Reactor-antineutrino oscillation experiment at the Hanbit (Yonggwang) Nuclear Power Plant, Korea, with identical near (294 m) and far (1383 m) detectors from a 6 × 2.8 GW_th reactor array. Its 2012 result observed reactor antineutrino disappearance at 4.9σ, sin²(2θ₁₃)=0.113±0.013(stat)±0.019(syst). Data acquisition ran 2011-08 to 2023-03 (3800 live days); a final-dataset measurement (arXiv:2412.18711) reports sin²2θ₁₃=0.0920 and |Δm²_ee|=2.57 × 10⁻³ eV².

### data/atlas/experiments/ricochet.json

- `/summary/technical` (summary.technical)
  - old: Ricochet: reactor CEvNS experiment at the ILL research reactor (Grenoble, France), 8.8 m from the 58 MW reactor core, using a planned kg-scale CryoCube array of Ge and Zn cryogenic calorimeters; a 126 g (3 x 42 g Ge) mini-CryoCube commissioning module was operated and characterized in 2025.
  - new: Ricochet: reactor CEvNS experiment at the ILL research reactor (Grenoble, France), 8.8 m from the 58 MW reactor core, using a planned kg-scale CryoCube array of Ge and Zn cryogenic calorimeters; a 126 g (3 × 42 g Ge) mini-CryoCube commissioning module was operated and characterized in 2025.

### data/atlas/experiments/sage.json

- `/summary/technical` (summary.technical)
  - old: Radiochemical liquid-gallium solar-neutrino experiment at the Baksan Neutrino Observatory, Russia, under a rock overburden equivalent to 4700 m of water; 50 t gallium target. Measured a solar neutrino capture rate of 67.2 (+7.2/-7.0 stat) (+3.5/-3.0 syst) SNU over 1990-1997, about half the Standard Solar Model prediction of 129 SNU.
  - new: Radiochemical liquid-gallium solar-neutrino experiment at the Baksan Neutrino Observatory, Russia, under a rock overburden equivalent to 4700 m of water; 50 t gallium target. Measured a solar neutrino capture rate of 67.2 (+7.2/−7.0 stat) (+3.5/−3.0 syst) SNU over 1990-1997, about half the Standard Solar Model prediction of 129 SNU.

### data/atlas/experiments/seaquest.json

- `/physics_goals/0/value` (physics_goals / unique_capabilities)
  - old: Measure the antiquark flavor asymmetry (dbar/ubar) in the proton sea via the Drell-Yan process, and study how nuclear binding modifies the quark/antiquark structure of nucleons
  - new: Measure the antiquark flavor asymmetry (d̄/ū) in the proton sea via the Drell-Yan process, and study how nuclear binding modifies the quark/antiquark structure of nucleons
- `/summary/technical` (summary.technical)
  - old: Fixed-target Drell-Yan dimuon experiment (Fermilab E-906) in the NM4 hall, using a 120 GeV proton beam (Main Injector) on liquid-hydrogen, liquid-deuterium and solid nuclear targets to measure the proton's dbar/ubar sea-quark flavor asymmetry and nuclear modification effects; its final combined-data-set results were posted in December 2025.
  - new: Fixed-target Drell-Yan dimuon experiment (Fermilab E-906) in the NM4 hall, using a 120 GeV proton beam (Main Injector) on liquid-hydrogen, liquid-deuterium and solid nuclear targets to measure the proton's d̄/ū sea-quark flavor asymmetry and nuclear modification effects; its final combined-data-set results were posted in December 2025.

### data/atlas/experiments/sld.json

- `/summary/technical` (summary.technical)
  - old: General-purpose detector at the SLAC Linear Collider (SLC) e+e- Z factory; unique among the LEP/SLC-era Z-pole detectors for a highly polarized electron beam (>60% from 1993), used chiefly for a precision measurement of the left-right asymmetry A_LR and sin^2(theta_W)_eff, plus heavy-flavor and QCD studies. First data 1991-1992, ran to June 1998.
  - new: General-purpose detector at the SLAC Linear Collider (SLC) e⁺e⁻ Z factory; unique among the LEP/SLC-era Z-pole detectors for a highly polarized electron beam (>60% from 1993), used chiefly for a precision measurement of the left-right asymmetry A_LR and sin²θW_eff, plus heavy-flavor and QCD studies. First data 1991-1992, ran to June 1998.
- `/unique_capabilities/0/value` (physics_goals / unique_capabilities)
  - old: The only e+e- Z-factory detector with access to a highly polarized electron beam, letting certain electroweak measurements surpass the precision reachable at LEP with unpolarized beams
  - new: The only e⁺e⁻ Z-factory detector with access to a highly polarized electron beam, letting certain electroweak measurements surpass the precision reachable at LEP with unpolarized beams

### data/atlas/experiments/snd-lhc.json

- `/summary/technical` (summary.technical)
  - old: Stand-alone forward neutrino/long-lived-particle detector in the TI18 tunnel, covering the pseudo-rapidity range 7.2 < eta < 8.6, complementary to FASER. Approved 17 March 2021; recorded LHC Run 3 pp-collision data from 2022 (arXiv:2305.09383) through June 2026; off since CERN's Long Shutdown 3 began.
  - new: Stand-alone forward neutrino/long-lived-particle detector in the TI18 tunnel, covering the pseudo-rapidity range 7.2 < η < 8.6, complementary to FASER. Approved 17 March 2021; recorded LHC Run 3 pp-collision data from 2022 (arXiv:2305.09383) through June 2026; off since CERN's Long Shutdown 3 began.

### data/atlas/experiments/star.json

- `/summary/technical` (summary.technical)
  - old: Solenoidal Tracker at RHIC: a large-acceptance heavy-ion collider experiment centred on a 4 m diameter x 4.2 m long Time Projection Chamber providing full-azimuth charged-particle tracking within |eta| < 1.8, studying quark-gluon plasma formation in Au+Au and other collision systems at RHIC from 2000 through RHIC's 25th and final run, which concluded 2026-02-06.
  - new: Solenoidal Tracker at RHIC: a large-acceptance heavy-ion collider experiment centred on a 4 m diameter x 4.2 m long Time Projection Chamber providing full-azimuth charged-particle tracking within |η| < 1.8, studying quark-gluon plasma formation in Au+Au and other collision systems at RHIC from 2000 through RHIC's 25th and final run, which concluded 2026-02-06.

### data/atlas/experiments/super-kamiokande.json

- `/key_specs/2/quantity/display` (quantity display)
  - old: 11,129 x 50cm PMTs
  - new: 11,129 × 50cm PMTs

### data/atlas/experiments/t2k.json

- `/physics_goals/0/value` (physics_goals / unique_capabilities)
  - old: Discover muon-neutrino to electron-neutrino appearance (confirm theta_13 > 0)
  - new: Discover muon-neutrino to electron-neutrino appearance (confirm θ₁₃ > 0)
- `/summary/technical` (summary.technical)
  - old: Long-baseline accelerator neutrino oscillation experiment: a 30 GeV proton beam from the J-PARC main ring produces a narrow-band muon-(anti)neutrino beam, measured on-axis by INGRID and 2.5 degrees off-axis by ND280 at 280 m, then detected 295 km away at Super-Kamiokande. Data taking began January 2010; observed electron-neutrino appearance (evidence 2011, PRL 107 041801; observation 2014, PRL 112 061802) and reported a constraint on the CP-violating phase delta_CP (Nature 580, 339, 2020). Upgraded ND280 (Super-FGD, two high-angle TPCs, TOF) commissioned December 2023 alongside a beam-power record of 760 kW, beginning the T2K-II phase; Hyper-Kamiokande is its planned successor.
  - new: Long-baseline accelerator neutrino oscillation experiment: a 30 GeV proton beam from the J-PARC main ring produces a narrow-band muon-(anti)neutrino beam, measured on-axis by INGRID and 2.5 degrees off-axis by ND280 at 280 m, then detected 295 km away at Super-Kamiokande. Data taking began January 2010; observed electron-neutrino appearance (evidence 2011, PRL 107 041801; observation 2014, PRL 112 061802) and reported a constraint on the CP-violating phase δCP (Nature 580, 339, 2020). Upgraded ND280 (Super-FGD, two high-angle TPCs, TOF) commissioned December 2023 alongside a beam-power record of 760 kW, beginning the T2K-II phase; Hyper-Kamiokande is its planned successor.

### data/atlas/experiments/telescope-array.json

- `/intervals/1/note` (provenance note)
  - old: TAx4 expands the original TA aperture by a factor of four (~3000 km^2 target), adding 500 SDs on a 2.08 km grid and 12 new FD telescopes. September 2022 is the end of an analysis dataset window, not a stated end of TAx4 operations.
  - new: TAx4 expands the original TA aperture by a factor of four (~3000 km² target), adding 500 SDs on a 2.08 km grid and 12 new FD telescopes. September 2022 is the end of an analysis dataset window, not a stated end of TAx4 operations.
- `/summary/technical` (summary.technical)
  - old: Hybrid ultra-high-energy cosmic-ray observatory near Delta, Utah (~1400 m altitude): 507 plastic-scintillator surface-detector stations on a 1.2 km grid over ~700 km^2, plus 38 fluorescence telescopes at three sites (Middle Drum, Long Ridge, Black Rock Mesa). Taking data since 11 May 2008; extended since October 2019 by TAx4 (500 additional SDs on a 2.08 km grid, 12 new FD telescopes, target ~3000 km^2).
  - new: Hybrid ultra-high-energy cosmic-ray observatory near Delta, Utah (~1400 m altitude): 507 plastic-scintillator surface-detector stations on a 1.2 km grid over ~700 km², plus 38 fluorescence telescopes at three sites (Middle Drum, Long Ridge, Black Rock Mesa). Taking data since 11 May 2008; extended since October 2019 by TAx4 (500 additional SDs on a 2.08 km grid, 12 new FD telescopes, target ~3000 km²).

### data/atlas/experiments/ua1.json

- `/physics_goals/1/value` (physics_goals / unique_capabilities)
  - old: Search for the top quark, heavy leptons and supersymmetric particles, and study B-Bbar mixing, b-quark production, QCD jets and intermediate-boson and photon production
  - new: Search for the top quark, heavy leptons and supersymmetric particles, and study B-B̄ mixing, b-quark production, QCD jets and intermediate-boson and photon production
- `/summary/technical` (summary.technical)
  - old: General-purpose 4-pi collider detector at the CERN SppS (Super Proton-Antiproton Synchrotron), operated 1981-1990; central image drift chamber, electromagnetic and hadronic calorimetry and muon chambers around an 800-tonne dipole magnet. Co-discovered the W (Jan 1983) and Z (1983) bosons with UA2 and provided early limits on the top quark and supersymmetric particles.
  - new: General-purpose 4π collider detector at the CERN SppS (Super Proton-Antiproton Synchrotron), operated 1981-1990; central image drift chamber, electromagnetic and hadronic calorimetry and muon chambers around an 800-tonne dipole magnet. Co-discovered the W (Jan 1983) and Z (1983) bosons with UA2 and provided early limits on the top quark and supersymmetric particles.
- `/unique_capabilities/0/value` (physics_goals / unique_capabilities)
  - old: The largest imaging drift chamber of its day, giving UA1 a photographic, bubble-chamber-like view of each collision inside a general-purpose 4-pi detector
  - new: The largest imaging drift chamber of its day, giving UA1 a photographic, bubble-chamber-like view of each collision inside a general-purpose 4π detector

### data/atlas/experiments/veritas.json

- `/unique_capabilities/0/value` (physics_goals / unique_capabilities)
  - old: The highest sensitivity of any operating gamma-ray telescope array in the 100 GeV-10 TeV range at the time the specification was published, with a peak effective area of 100,000 m^2.
  - new: The highest sensitivity of any operating gamma-ray telescope array in the 100 GeV-10 TeV range at the time the specification was published, with a peak effective area of 100,000 m².

### data/atlas/experiments/xenon1t.json

- `/key_specs/2/quantity/display` (quantity display)
  - old: 7.7e-47 cm^2 at 35 GeV/c^2 (90% CL)
  - new: 7.7 × 10⁻⁴⁷ cm² at 35 GeV/c² (90% CL)
- `/summary/technical` (summary.technical)
  - old: First tonne-scale dual-phase xenon TPC dark matter search: 3.2 t total / 2.0 t active liquid xenon, built 2014-2015 and operated 2015-2018 in LNGS Hall B (~1400 m rock). Its first-results run (34.2 live days, Nov 2016 - Jan 2017) set a spin-independent WIMP-nucleon limit of 7.7e-47 cm^2 at 35 GeV/c^2. A 2020 analysis of low-energy electronic-recoil data reported an unexplained excess near 2-3 keV (tritium/axion/neutrino-magnetic-moment hypotheses considered, none confirmed). Stopped Dec 2018 to be upgraded into XENONnT.
  - new: First tonne-scale dual-phase xenon TPC dark matter search: 3.2 t total / 2.0 t active liquid xenon, built 2014-2015 and operated 2015-2018 in LNGS Hall B (~1400 m rock). Its first-results run (34.2 live days, Nov 2016 - Jan 2017) set a spin-independent WIMP-nucleon limit of 7.7 × 10⁻⁴⁷ cm² at 35 GeV/c². A 2020 analysis of low-energy electronic-recoil data reported an unexplained excess near 2-3 keV (tritium/axion/neutrino-magnetic-moment hypotheses considered, none confirmed). Stopped Dec 2018 to be upgraded into XENONnT.

### data/atlas/experiments/xenonnt.json

- `/intervals/3/label` (interval label)
  - old: detector upgrade (new TPC electrodes, drift field 23 -> 100 V/cm)
  - new: detector upgrade (new TPC electrodes, drift field 23 → 100 V/cm)
- `/summary/technical` (summary.technical)
  - old: Dual-phase xenon TPC upgrade of XENON1T: 8.5 t total / 5.9 t active liquid xenon in LNGS Hall B (INFN, ~1400 m rock). Construction began Dec 2018; operation began 2020. The first WIMP-search result (2023, 1.1 t-y exposure) set a spin-independent limit of 2.58e-47 cm^2 at 28 GeV/c^2. A 2024 analysis reported the first indication (2.73 sigma) of solar 8B neutrinos via coherent elastic neutrino-nucleus scattering.
  - new: Dual-phase xenon TPC upgrade of XENON1T: 8.5 t total / 5.9 t active liquid xenon in LNGS Hall B (INFN, ~1400 m rock). Construction began Dec 2018; operation began 2020. The first WIMP-search result (2023, 1.1 t-y exposure) set a spin-independent limit of 2.58 × 10⁻⁴⁷ cm² at 28 GeV/c². A 2024 analysis reported the first indication (2.73σ) of solar 8B neutrinos via coherent elastic neutrino-nucleus scattering.

### data/atlas/experiments/zeus.json

- `/physics_goals/0/value` (physics_goals / unique_capabilities)
  - old: Measure neutral- and charged-current deep inelastic and photoproduction processes in e-p and e+p collisions, identify jets and leptons with precision tracking, and search for new interactions and particles
  - new: Measure neutral- and charged-current deep inelastic and photoproduction processes in e⁻p and e⁺p collisions, identify jets and leptons with precision tracking, and search for new interactions and particles

### data/atlas/facilities/cern.json

- `/summary/technical` (summary.technical)
  - old: International intergovernmental accelerator laboratory (25 Member States as of 2026-09) straddling the CH/FR border at Meyrin. Operates the injector chain Linac4 -> PS Booster -> PS -> SPS feeding the 26.7 km LHC, plus its historical machines (ISR, SppS, LEP).
  - new: International intergovernmental accelerator laboratory (25 Member States as of 2026-09) straddling the CH/FR border at Meyrin. Operates the injector chain Linac4 → PS Booster → PS → SPS feeding the 26.7 km LHC, plus its historical machines (ISR, SppS, LEP).

### data/atlas/facilities/lngs.json

- `/summary/technical` (summary.technical)
  - old: INFN national laboratory at Assergi (L'Aquila), Italy, with three underground halls of roughly 100 x 20 x 18 m under about 1400 m of rock, hosting low-background neutrino, dark matter and double-beta-decay experiments; the ICARUS T600 ran in Hall B from 2010 to 2013.
  - new: INFN national laboratory at Assergi (L'Aquila), Italy, with three underground halls of roughly 100 × 20 × 18 m under about 1400 m of rock, hosting low-background neutrino, dark matter and double-beta-decay experiments; the ICARUS T600 ran in Hall B from 2010 to 2013.

### data/atlas/facilities/pierre-auger-observatory.json

- `/summary/technical` (summary.technical)
  - old: Hybrid ultra-high-energy cosmic-ray observatory in Mendoza Province, Argentina, combining a 3000 km^2 surface array of 1660 water-Cherenkov detector stations with 27 fluorescence telescopes in four buildings overlooking the array; operated by the international Pierre Auger Collaboration since inauguration in November 2008, currently undergoing the AugerPrime upgrade.
  - new: Hybrid ultra-high-energy cosmic-ray observatory in Mendoza Province, Argentina, combining a 3000 km² surface array of 1660 water-Cherenkov detector stations with 27 fluorescence telescopes in four buildings overlooking the array; operated by the international Pierre Auger Collaboration since inauguration in November 2008, currently undergoing the AugerPrime upgrade.

### data/atlas/facilities/telescope-array-utah.json

- `/summary/technical` (summary.technical)
  - old: Hybrid ultra-high-energy cosmic-ray observatory near Delta, Utah, USA, at about 1400 m altitude, comprising a 507-counter surface-detector array over ~700 km^2 and three fluorescence-detector stations; operating since 11 May 2008 and extended since 2019 by the four-times-larger TAx4 array.
  - new: Hybrid ultra-high-energy cosmic-ray observatory near Delta, Utah, USA, at about 1400 m altitude, comprising a 507-counter surface-detector array over ~700 km² and three fluorescence-detector stations; operating since 11 May 2008 and extended since 2019 by the four-times-larger TAx4 array.

### data/atlas/facilities/yonggwang-hanbit-reactor-site.json

- `/summary/technical` (summary.technical)
  - old: Reactor-neutrino site at the Hanbit (Yonggwang) Nuclear Power Plant, South Korea, hosting the RENO near (294 m) and far (1383 m) detector halls, 6 x 2.8 GW_th reactor array.
  - new: Reactor-neutrino site at the Hanbit (Yonggwang) Nuclear Power Plant, South Korea, hosting the RENO near (294 m) and far (1383 m) detector halls, 6 × 2.8 GW_th reactor array.

### data/atlas/results/alice-hypertriton-lifetime-2019.json

- `/key_value/display` (key_value.display)
  - old: 0.242 ns (+0.034/-0.038 stat, +/-0.017 syst) [= 242 ps in the source's own units]
  - new: 0.242 ns (+0.034/−0.038 stat, ±0.017 syst) [= 242 ps in the source's own units]

### data/atlas/results/alice-jpsi-suppression-pbpb-2012.json

- `/key_value/display` (key_value.display)
  - old: 0.545 +/- 0.032 (stat) +/- 0.083 (syst)
  - new: 0.545 ± 0.032 (stat) ± 0.083 (syst)
- `/key_value/note` (provenance note)
  - old: Nuclear modification factor R_AA for inclusive J/psi, 0-80% centrality.
  - new: Nuclear modification factor R_AA for inclusive J/ψ, 0-80% centrality.
- `/name` (name)
  - old: J/psi suppression at forward rapidity in Pb-Pb collisions at 2.76 TeV
  - new: J/ψ suppression at forward rapidity in Pb-Pb collisions at 2.76 TeV
- `/notes/0` (notes[])
  - old: result_type is 'measurement' rather than 'observation': although the abstract's passive wording ('is observed') would satisfy A16's keyword check for 'observation', J/psi suppression itself was already established at SPS/RHIC energies before ALICE; this paper measures the effect at LHC energy, so 'measurement' better matches the collaboration's own framing (a suppression factor with quoted uncertainties) and avoids over-classifying a measurement as a first observation.
  - new: result_type is 'measurement' rather than 'observation': although the abstract's passive wording ('is observed') would satisfy A16's keyword check for 'observation', J/ψ suppression itself was already established at SPS/RHIC energies before ALICE; this paper measures the effect at LHC energy, so 'measurement' better matches the collaboration's own framing (a suppression factor with quoted uncertainties) and avoids over-classifying a measurement as a first observation.
- `/summary/plain` (summary.plain)
  - old: ALICE measured how often J/psi particles (made of a charm quark and antiquark) survive lead-lead collisions at the LHC. The J/psi nuclear modification factor is larger than at the SPS and RHIC for the most central collisions, and models that produce J/psi from charm quarks in a deconfined phase can describe the data.
  - new: ALICE measured how often J/ψ particles (made of a charm quark and antiquark) survive lead-lead collisions at the LHC. The J/ψ nuclear modification factor is larger than at the SPS and RHIC for the most central collisions, and models that produce J/ψ from charm quarks in a deconfined phase can describe the data.
- `/summary/technical` (summary.technical)
  - old: ALICE measurement of inclusive J/psi production at forward rapidity (2.5 < y < 4) in Pb-Pb collisions at sqrt(s_NN) = 2.76 TeV: nuclear modification factor R_AA = 0.545 +/- 0.032 (stat) +/- 0.083 (syst) for the 0-80% most central collisions, with no significant dependence on centrality. The paper states that R_AA is larger than at the SPS and RHIC for most central collisions (the abstract says these features 'appear significantly different from measurements at lower collision energies') and that models including J/psi production from charm quarks in a deconfined partonic phase can describe the data.
  - new: ALICE measurement of inclusive J/ψ production at forward rapidity (2.5 < y < 4) in Pb-Pb collisions at √sNN = 2.76 TeV: nuclear modification factor R_AA = 0.545 ± 0.032 (stat) ± 0.083 (syst) for the 0-80% most central collisions, with no significant dependence on centrality. The paper states that R_AA is larger than at the SPS and RHIC for most central collisions (the abstract says these features 'appear significantly different from measurements at lower collision energies') and that models including J/ψ production from charm quarks in a deconfined partonic phase can describe the data.
- `/why_it_matters` (why_it_matters)
  - old: Charmonium (J/psi) production is studied in heavy-ion collisions as a probe of the quark-gluon plasma: in the colour-screening model, the in-medium dissociation probability of quarkonium states is expected to give an estimate of the initial temperature of the system. At LHC energy ALICE finds R_AA larger than at SPS and RHIC for the most central collisions, and reports that models with J/psi production from charm quarks in a deconfined partonic phase can describe the data.
  - new: Charmonium (J/ψ) production is studied in heavy-ion collisions as a probe of the quark-gluon plasma: in the colour-screening model, the in-medium dissociation probability of quarkonium states is expected to give an estimate of the initial temperature of the system. At LHC energy ALICE finds R_AA larger than at SPS and RHIC for the most central collisions, and reports that models with J/ψ production from charm quarks in a deconfined partonic phase can describe the data.

### data/atlas/results/alice-strangeness-enhancement-pp-2017.json

- `/summary/technical` (summary.technical)
  - old: ALICE measurement (pp at sqrt(s) = 7 TeV) of strange (K0S, Lambda) and multi-strange (Xi, Omega) hadron yields relative to pions as a function of charged-particle multiplicity. The collaboration presents 'the first observation of strangeness enhancement in high-multiplicity pp collisions': the yields relative to pions increase significantly with multiplicity and, at the highest multiplicities, reach values similar to those observed in Pb-Pb collisions.
  - new: ALICE measurement (pp at √s = 7 TeV) of strange (K0S, Lambda) and multi-strange (Xi, Omega) hadron yields relative to pions as a function of charged-particle multiplicity. The collaboration presents 'the first observation of strangeness enhancement in high-multiplicity pp collisions': the yields relative to pions increase significantly with multiplicity and, at the highest multiplicities, reach values similar to those observed in Pb-Pb collisions.

### data/atlas/results/atlas-hbb-observation-2018.json

- `/summary/technical` (summary.technical)
  - old: Search for H → bb̄ produced with a W or Z boson (VH) in 79.8 fb^-1 of 13 TeV data: observed (expected) significance 4.9 (4.3) standard deviations; combined with Run 1 and other Run 2 H → bb̄ searches: 5.4 (5.5) standard deviations, 'direct observation of the Higgs boson decay into b-quarks'. Ratio of the measured H → bb̄ yield to the Standard Model expectation 1.01 ± 0.12 (stat) +0.16/−0.15 (syst); VH production observed at 5.3 (4.8) standard deviations (Run 2 combination).
  - new: Search for H → bb̄ produced with a W or Z boson (VH) in 79.8 fb⁻¹ of 13 TeV data: observed (expected) significance 4.9 (4.3) standard deviations; combined with Run 1 and other Run 2 H → bb̄ searches: 5.4 (5.5) standard deviations, 'direct observation of the Higgs boson decay into b-quarks'. Ratio of the measured H → bb̄ yield to the Standard Model expectation 1.01 ± 0.12 (stat) +0.16/−0.15 (syst); VH production observed at 5.3 (4.8) standard deviations (Run 2 combination).

### data/atlas/results/atlas-higgs-observation-2012.json

- `/key_value/display` (key_value.display)
  - old: 126.0 +/- 0.4 (stat.) +/- 0.4 (sys.) GeV
  - new: 126.0 ± 0.4 (stat.) ± 0.4 (sys.) GeV
- `/significance/note` (significance)
  - old: The abstract gives 5.9 standard deviations (background fluctuation probability 1.7x10^-9); 'local' and the global significance are from the paper's main text.
  - new: The abstract gives 5.9 standard deviations (background fluctuation probability 1.7×10⁻⁹); 'local' and the global significance are from the paper's main text.
- `/summary/technical` (summary.technical)
  - old: Combined search: H → ZZ(*) → 4ℓ, γγ and WW(*) → eνμν in 8 TeV data (about 5.8 fb^-1) combined with 7 TeV results (about 4.8 fb^-1: ZZ(*), WW(*), bb̄, τ+τ−, plus improved ZZ(*) → 4ℓ and γγ analyses). 'Clear evidence for the production of a neutral boson with a measured mass of 126.0 ± 0.4 (stat) ± 0.4 (sys) GeV is presented'; the observation has a local significance of 5.9σ (background fluctuation probability 1.7×10⁻⁹) and is compatible with the production and decay of the Standard Model Higgs boson.
  - new: Combined search: H → ZZ(*) → 4ℓ, γγ and WW(*) → eνμν in 8 TeV data (about 5.8 fb⁻¹) combined with 7 TeV results (about 4.8 fb⁻¹: ZZ(*), WW(*), bb̄, τ⁺τ⁻, plus improved ZZ(*) → 4ℓ and γγ analyses). 'Clear evidence for the production of a neutral boson with a measured mass of 126.0 ± 0.4 (stat) ± 0.4 (sys) GeV is presented'; the observation has a local significance of 5.9σ (background fluctuation probability 1.7×10⁻⁹) and is compatible with the production and decay of the Standard Model Higgs boson.

### data/atlas/results/atlas-htautau-observation-2018.json

- `/summary/technical` (summary.technical)
  - old: 36.1 fb^-1 of 13 TeV data: H → ττ signal established with observed (expected) significance 4.4 (4.1) standard deviations; combined with 7 and 8 TeV data, 6.4 (5.4) standard deviations, which 'constitutes an observation of H → ττ decays'. Total H → ττ cross section at 13 TeV 3.77 +0.60/−0.59 (stat) +0.87/−0.74 (syst) pb; all measurements in agreement with Standard Model expectations.
  - new: 36.1 fb⁻¹ of 13 TeV data: H → ττ signal established with observed (expected) significance 4.4 (4.1) standard deviations; combined with 7 and 8 TeV data, 6.4 (5.4) standard deviations, which 'constitutes an observation of H → ττ decays'. Total H → ττ cross section at 13 TeV 3.77 +0.60/−0.59 (stat) +0.87/−0.74 (syst) pb; all measurements in agreement with Standard Model expectations.

### data/atlas/results/atlas-lbyl-observation-2019.json

- `/key_value/display` (key_value.display)
  - old: 78 +/- 13 (stat.) +/- 7 (syst.) +/- 3 (lumi.) nb
  - new: 78 ± 13 (stat.) ± 7 (syst.) ± 3 (lumi.) nb
- `/summary/technical` (summary.technical)
  - old: Ultraperipheral Pb+Pb collisions at 5.02 TeV per nucleon pair, 1.73 nb^-1 (Nov 2018): 59 gamma-gamma -> gamma-gamma candidates against a background of 12 +/- 3 events, 8.2 sigma significance, fiducial cross section 78 +/- 13 (stat.) +/- 7 (syst.) +/- 3 (lumi.) nb.
  - new: Ultraperipheral Pb+Pb collisions at 5.02 TeV per nucleon pair, 1.73 nb⁻¹ (Nov 2018): 59 γγ → γγ candidates against a background of 12 ± 3 events, 8.2σ significance, fiducial cross section 78 ± 13 (stat.) ± 7 (syst.) ± 3 (lumi.) nb.

### data/atlas/results/atlas-nature-higgs-2022.json

- `/summary/technical` (summary.technical)
  - old: Combination of ATLAS measurements of Higgs boson production and decay rates using the full Run 2 dataset (139 fb^-1 at 13 TeV) to study the Higgs boson's interactions with gluons, photons, W and Z bosons, b and t quarks and tau leptons, with indications of interactions with muons; published in Nature 607, 52–59 (2022).
  - new: Combination of ATLAS measurements of Higgs boson production and decay rates using the full Run 2 dataset (139 fb⁻¹ at 13 TeV) to study the Higgs boson's interactions with gluons, photons, W and Z bosons, b and t quarks and tau leptons, with indications of interactions with muons; published in Nature 607, 52–59 (2022).

### data/atlas/results/atlas-squark-gluino-limit-2020.json

- `/summary/technical` (summary.technical)
  - old: Search for squarks and gluinos in final states with jets and missing transverse momentum, no electrons or muons (139 fb^-1 at 13 TeV): no statistically significant deviation from the background expectation for any search strategy; 95% CL exclusion limit on the gluino mass of 2.30 TeV for a simplified model containing only a gluino and the lightest neutralino, assuming the latter is massless; in a simplified model of strong production of mass-degenerate first- and second-generation squarks, squark masses below 1.85 TeV are excluded for a massless lightest neutralino.
  - new: Search for squarks and gluinos in final states with jets and missing transverse momentum, no electrons or muons (139 fb⁻¹ at 13 TeV): no statistically significant deviation from the background expectation for any search strategy; 95% CL exclusion limit on the gluino mass of 2.30 TeV for a simplified model containing only a gluino and the lightest neutralino, assuming the latter is massless; in a simplified model of strong production of mass-degenerate first- and second-generation squarks, squark masses below 1.85 TeV are excluded for a massless lightest neutralino.

### data/atlas/results/atlas-topmass-measurement-2018.json

- `/key_value/display` (key_value.display)
  - old: 172.08 +/- 0.39 (stat) +/- 0.82 (syst) GeV
  - new: 172.08 ± 0.39 (stat) ± 0.82 (syst) GeV
- `/summary/technical` (summary.technical)
  - old: Lepton+jets ttbar candidates from 20.2 fb^-1 of 8 TeV data, three-dimensional template method: m_top = 172.08 +/- 0.39 (stat) +/- 0.82 (syst) GeV; a combination with previous ATLAS m_top measurements gives m_top = 172.69 +/- 0.25 (stat) +/- 0.41 (syst) GeV.
  - new: Lepton+jets tt̄ candidates from 20.2 fb⁻¹ of 8 TeV data, three-dimensional template method: m_top = 172.08 ± 0.39 (stat) ± 0.82 (syst) GeV; a combination with previous ATLAS m_top measurements gives m_top = 172.69 ± 0.25 (stat) ± 0.41 (syst) GeV.

### data/atlas/results/atlas-tth-observation-2018.json

- `/summary/technical` (summary.technical)
  - old: ttH production searched for with Higgs decays into bb̄, WW*, τ+τ−, γγ and ZZ* in up to 79.8 fb^-1 of 13 TeV data: observed significance 5.8 standard deviations (4.9 expected). Combined with ttH searches in 4.5 fb^-1 at 7 TeV and 20.3 fb^-1 at 8 TeV: 6.3 (5.1) standard deviations. Total ttH cross section at 13 TeV: 670 ± 90 (stat) +110/−100 (syst) fb, in agreement with the Standard Model prediction.
  - new: ttH production searched for with Higgs decays into bb̄, WW*, τ⁺τ⁻, γγ and ZZ* in up to 79.8 fb⁻¹ of 13 TeV data: observed significance 5.8 standard deviations (4.9 expected). Combined with ttH searches in 4.5 fb⁻¹ at 7 TeV and 20.3 fb⁻¹ at 8 TeV: 6.3 (5.1) standard deviations. Total ttH cross section at 13 TeV: 670 ± 90 (stat) +110/−100 (syst) fb, in agreement with the Standard Model prediction.

### data/atlas/results/atlas-wmass-measurement-2017.json

- `/key_value/display` (key_value.display)
  - old: 80370 +/- 19 MeV
  - new: 80370 ± 19 MeV
- `/summary/technical` (summary.technical)
  - old: W -> lepton nu candidates from 4.6 fb^-1 of 7 TeV data, template fits to lepton transverse momentum and transverse mass: m_W = 80370 +/- 19 MeV, combining statistical, experimental-systematic and modelling uncertainties.
  - new: W → lepton ν candidates from 4.6 fb⁻¹ of 7 TeV data, template fits to lepton transverse momentum and transverse mass: m_W = 80370 ± 19 MeV, combining statistical, experimental-systematic and modelling uncertainties.

### data/atlas/results/belle-b-to-tau-nu-evidence-2006.json

- `/key_value_text/value` (key_value_text.value)
  - old: Br(B- --> tau- nu_tau-bar) = (1.79 +0.56-0.49(stat) +0.46-0.51(syst))*10^-4
  - new: Br(B⁻ → τ⁻ ν̄τ) = (1.79 +0.56−0.49(stat) +0.46−0.51(syst))×10⁻⁴

### data/atlas/results/belle-cp-violation-observation-2001.json

- `/key_value_text/value` (key_value_text.value)
  - old: sin 2phi_1 = 0.99 +- 0.14(stat) +- 0.06(syst)
  - new: sin 2φ₁ = 0.99 ± 0.14(stat) ± 0.06(syst)
- `/summary/technical` (summary.technical)
  - old: Time-dependent measurement of the CP asymmetry with 29.1 fb^-1 at the Υ(4S), one B⁰ fully reconstructed as J/ψ K_S, ψ(2S) K_S, χ_c1 K_S, η_c K_S, J/ψ K_L or J/ψ K*⁰ and the flavour of the other identified from its decay products: sin 2φ₁ = 0.99 ± 0.14 (stat) ± 0.06 (syst). 'We conclude that we have observed CP violation in the neutral B meson system'; a zero value of sin 2φ₁ is ruled out at a level greater than 6σ.
  - new: Time-dependent measurement of the CP asymmetry with 29.1 fb⁻¹ at the Υ(4S), one B⁰ fully reconstructed as J/ψ K_S, ψ(2S) K_S, χ_c1 K_S, η_c K_S, J/ψ K_L or J/ψ K*⁰ and the flavour of the other identified from its decay products: sin 2φ₁ = 0.99 ± 0.14 (stat) ± 0.06 (syst). 'We conclude that we have observed CP violation in the neutral B meson system'; a zero value of sin 2φ₁ is ruled out at a level greater than 6σ.

### data/atlas/results/belle-d0-mixing-evidence-2007.json

- `/key_value_text/value` (key_value_text.value)
  - old: y_CP = (1.31 +- 0.32(stat.) +- 0.25(syst.))%
  - new: y_CP = (1.31 ± 0.32(stat.) ± 0.25(syst.))%

### data/atlas/results/belle-ii-b-to-k-nunu-evidence-2023.json

- `/key_value_text/value` (key_value_text.value)
  - old: B(B+ -> K+ nu nubar) = [2.3 +- 0.5(stat) +0.5-0.4(syst)] x 10^-5
  - new: B(B⁺ → K⁺ ν ν̄) = [2.3 ± 0.5(stat) +0.5−0.4(syst)] × 10⁻⁵

### data/atlas/results/belle-ii-tau-mass-measurement-2023.json

- `/summary/technical` (summary.technical)
  - old: Pseudomass-endpoint measurement in τ⁻ → π⁻π⁺π⁻ ν_τ using ~175 million e⁺e⁻ → τ⁺τ⁻ events in 190 fb⁻¹ at √s = 10.579 GeV, giving m_τ = 1777.09 ± 0.08(stat) ± 0.11(syst) MeV/c².
  - new: Pseudomass-endpoint measurement in τ⁻ → π⁻π⁺π⁻ ντ using ~175 million e⁺e⁻ → τ⁺τ⁻ events in 190 fb⁻¹ at √s = 10.579 GeV, giving m_τ = 1777.09 ± 0.08(stat) ± 0.11(syst) MeV/c².

### data/atlas/results/belle-ii-vcb-measurement-2025.json

- `/summary/technical` (summary.technical)
  - old: Inclusive-tag determination of |Vcb| from B0->D-(->K+pi-pi-) l+ nu_l and B+->D0bar(->K+pi-) l+ nu_l decays in 365 fb^-1 of Belle II Upsilon(4S) data, using the recoil variable w=v_B.v_D and lattice-QCD form-factor averages. Reports B(B0->D- l+ nu_l) = (2.06 +/- 0.05stat +/- 0.10sys)%, B(B+->D0bar l+ nu_l) = (2.31 +/- 0.04stat +/- 0.09sys)%, a lepton-flavor-universality ratio B(B->D e nu_e)/B(B->D mu nu_mu) = 1.020 +/- 0.020stat +/- 0.022sys, and |Vcb| = (39.2 +/- 0.4stat +/- 0.6sys +/- 0.5th)x10^-3.
  - new: Inclusive-tag determination of |Vcb| from B⁰→D⁻(→K⁺π⁻π⁻) l⁺ νl and B⁺→D̄⁰(→K⁺π⁻) l⁺ νl decays in 365 fb⁻¹ of Belle II Υ(4S) data, using the recoil variable w=v_B.v_D and lattice-QCD form-factor averages. Reports B(B⁰→D⁻ l⁺ νl) = (2.06 ± 0.05stat ± 0.10sys)%, B(B⁺→D̄⁰ l⁺ νl) = (2.31 ± 0.04stat ± 0.09sys)%, a lepton-flavor-universality ratio B(B→D e νe)/B(B→D μ νμ) = 1.020 ± 0.020stat ± 0.022sys, and |Vcb| = (39.2 ± 0.4stat ± 0.6sys ± 0.5th)×10⁻³.

### data/atlas/results/borexino-pp-first-detection-2014.json

- `/summary/technical` (summary.technical)
  - old: Spectral observations of pp neutrinos with the Borexino liquid-scintillator detector at LNGS: pp neutrino interaction rate 144 ± 13 (stat) ± 10 (syst) counts per day per 100 t, flux (6.6 ± 0.7) × 10^10 cm⁻² s⁻¹ in good agreement with the standard solar model prediction; the absence of pp neutrinos is excluded with a statistical significance of 10σ, and about 99% of the Sun's power (3.84 × 10^33 erg/s) is generated by proton–proton fusion.
  - new: Spectral observations of pp neutrinos with the Borexino liquid-scintillator detector at LNGS: pp neutrino interaction rate 144 ± 13 (stat) ± 10 (syst) counts per day per 100 t, flux (6.6 ± 0.7) × 10¹⁰ cm⁻² s⁻¹ in good agreement with the standard solar model prediction; the absence of pp neutrinos is excluded with a statistical significance of 10σ, and about 99% of the Sun's power (3.84 × 10³³ erg/s) is generated by proton–proton fusion.

### data/atlas/results/cdf-top-quark-observation-1995.json

- `/name` (name)
  - old: Observation of Top Quark Production in ppbar Collisions with the Collider Detector at Fermilab
  - new: Observation of Top Quark Production in pp̄ Collisions with the Collider Detector at Fermilab
- `/notes/1` (notes[])
  - old: title/name corrected in a 2026-09-17 verification pass: the record previously read "Observation of top quark production in ppbar collisions", dropping the published title's "with the Collider Detector at Fermilab" clause and its capitalisation; confirmed verbatim against journals.aps.org/prl/abstract/10.1103/PhysRevLett.74.2626, whose title is "Observation of Top Quark Production in pbar-p Collisions with the Collider Detector at Fermilab" (rendered here with the repository's ASCII "ppbar" convention).
  - new: title/name corrected in a 2026-09-17 verification pass: the record previously read "Observation of top quark production in ppbar collisions", dropping the published title's "with the Collider Detector at Fermilab" clause and its capitalisation; confirmed verbatim against journals.aps.org/prl/abstract/10.1103/PhysRevLett.74.2626, whose title is "Observation of Top Quark Production in pbar-p Collisions with the Collider Detector at Fermilab" (rendered here in Unicode notation as pp̄; the ASCII form "ppbar" is kept as an alias).
- `/summary/technical` (summary.technical)
  - old: CDF observation of top-quark pair production in ppbar collisions at sqrt(s) = 1.8 TeV using a 67 pb^-1 sample: a signal consistent with t t̄ decay to WW b b̄ but inconsistent with the background prediction by 4.8σ, with additional evidence from a peak in the reconstructed mass distribution; m_top = 176 ± 8 (stat) ± 10 (sys) GeV/c², t t̄ production cross section 6.8 +3.6/−2.4 pb.
  - new: CDF observation of top-quark pair production in pp̄ collisions at √s = 1.8 TeV using a 67 pb⁻¹ sample: a signal consistent with t t̄ decay to WW b b̄ but inconsistent with the background prediction by 4.8σ, with additional evidence from a peak in the reconstructed mass distribution; m_top = 176 ± 8 (stat) ± 10 (sys) GeV/c², t t̄ production cross section 6.8 +3.6/−2.4 pb.

### data/atlas/results/cms-higgs-boson-observation-2012.json

- `/key_value/display` (key_value.display)
  - old: 125.3 +/- 0.4 (stat.) +/- 0.5 (syst.) GeV
  - new: 125.3 ± 0.4 (stat.) ± 0.5 (syst.) GeV
- `/summary/technical` (summary.technical)
  - old: Search for the standard model Higgs boson in five decay modes (γγ, ZZ, WW, ττ, bb̄) with up to 5.1 fb^-1 at 7 TeV and 5.3 fb^-1 at 8 TeV: an excess with local significance 5.0 standard deviations at a mass near 125 GeV (5.8 expected for a standard model Higgs boson of that mass); a fit to the γγ and ZZ signals gives 125.3 ± 0.4 (stat) ± 0.5 (syst) GeV; the diphoton decay indicates a boson with spin different from one.
  - new: Search for the standard model Higgs boson in five decay modes (γγ, ZZ, WW, ττ, bb̄) with up to 5.1 fb⁻¹ at 7 TeV and 5.3 fb⁻¹ at 8 TeV: an excess with local significance 5.0 standard deviations at a mass near 125 GeV (5.8 expected for a standard model Higgs boson of that mass); a fit to the γγ and ZZ signals gives 125.3 ± 0.4 (stat) ± 0.5 (syst) GeV; the diphoton decay indicates a boson with spin different from one.

### data/atlas/results/cms-higgs-to-bb-observation-2018.json

- `/summary/technical` (summary.technical)
  - old: VH production (W or Z boson plus H → bb̄) in 41.3 fb^-1 of 13 TeV data recorded in 2017: combined with previous VH measurements at 7, 8 and 13 TeV, an excess at m_H = 125.09 GeV with a significance of 4.8 standard deviations (4.9 expected for the SM Higgs boson), signal strength 1.01 ± 0.22. Combined with CMS searches for H → bb̄ in other production processes: observed (expected) significance 5.6 (5.5) standard deviations, signal strength 1.04 ± 0.20.
  - new: VH production (W or Z boson plus H → bb̄) in 41.3 fb⁻¹ of 13 TeV data recorded in 2017: combined with previous VH measurements at 7, 8 and 13 TeV, an excess at m_H = 125.09 GeV with a significance of 4.8 standard deviations (4.9 expected for the SM Higgs boson), signal strength 1.01 ± 0.22. Combined with CMS searches for H → bb̄ in other production processes: observed (expected) significance 5.6 (5.5) standard deviations, signal strength 1.04 ± 0.20.

### data/atlas/results/cms-higgs-to-tau-tau-observation-2018.json

- `/summary/technical` (summary.technical)
  - old: 35.9 fb^-1 at 13 TeV: H → ττ signal established with a significance of 4.9 standard deviations (4.7 expected), best-fit signal strength 1.09 +0.27/−0.26 times the standard model expectation; combined with 7 and 8 TeV data, observed significance 5.9 standard deviations, equal to the expected significance.
  - new: 35.9 fb⁻¹ at 13 TeV: H → ττ signal established with a significance of 4.9 standard deviations (4.7 expected), best-fit signal strength 1.09 +0.27/−0.26 times the standard model expectation; combined with 7 and 8 TeV data, observed significance 5.9 standard deviations, equal to the expected significance.

### data/atlas/results/cms-high-mass-dilepton-search-2021.json

- `/summary/plain` (summary.plain)
  - old: CMS searched its 2016–2018 13 TeV data (up to 140 fb^-1) for electron or muon pairs from a heavy new particle and saw no significant deviation from the Standard Model background. The abstract says the limits are the most stringent to date on the masses of various spin-1 particles, spin-2 gravitons (Randall–Sundrum model) and spin-1 dark-matter mediators.
  - new: CMS searched its 2016–2018 13 TeV data (up to 140 fb⁻¹) for electron or muon pairs from a heavy new particle and saw no significant deviation from the Standard Model background. The abstract says the limits are the most stringent to date on the masses of various spin-1 particles, spin-2 gravitons (Randall–Sundrum model) and spin-1 dark-matter mediators.
- `/summary/technical` (summary.technical)
  - old: Dielectron and dimuon mass spectra from up to 140 fb^-1 of 13 TeV data (2016–2018): no significant deviation from the standard model background expectations; upper limits on narrow resonances relative to the Z boson (most stringent lower limits to date on masses of various spin-1 particles, Randall–Sundrum spin-2 gravitons and spin-1 dark-matter mediators), lower limits on the ultraviolet cutoff for four-fermion contact interactions and the ADD model, and a lepton-flavour-universality test at the TeV scale, which the abstract says is done for the first time.
  - new: Dielectron and dimuon mass spectra from up to 140 fb⁻¹ of 13 TeV data (2016–2018): no significant deviation from the standard model background expectations; upper limits on narrow resonances relative to the Z boson (most stringent lower limits to date on masses of various spin-1 particles, Randall–Sundrum spin-2 gravitons and spin-1 dark-matter mediators), lower limits on the ultraviolet cutoff for four-fermion contact interactions and the ADD model, and a lepton-flavour-universality test at the TeV scale, which the abstract says is done for the first time.

### data/atlas/results/cms-long-range-near-side-correlations-2010.json

- `/summary/technical` (summary.technical)
  - old: Two-particle Delta(eta)-Delta(phi) correlations in 7 TeV pp collisions show a pronounced near-side ridge at 2.0 < |Delta(eta)| < 4.8 for 1-3 GeV/c tracks in high-multiplicity events (980 nb^-1).
  - new: Two-particle Δη-Δφ correlations in 7 TeV pp collisions show a pronounced near-side ridge at 2.0 < |Δη| < 4.8 for 1-3 GeV/c tracks in high-multiplicity events (980 nb⁻¹).

### data/atlas/results/cms-top-quark-mass-measurement-2023.json

- `/key_value/display` (key_value.display)
  - old: 171.77 +/- 0.37 GeV
  - new: 171.77 ± 0.37 GeV
- `/summary/technical` (summary.technical)
  - old: 36.3 fb^-1 at 13 TeV, lepton+jets ttbar candidates, kinematic fit plus a profile likelihood over up to four observables: m_t = 171.77 +/- 0.37 GeV.
  - new: 36.3 fb⁻¹ at 13 TeV, lepton+jets tt̄ candidates, kinematic fit plus a profile likelihood over up to four observables: m_t = 171.77 ± 0.37 GeV.

### data/atlas/results/cms-tth-observation-2018.json

- `/summary/technical` (summary.technical)
  - old: Combination of ttH searches in WW, ZZ, gamma gamma, tau tau and bb final states at 7, 8 and 13 TeV (up to 5.1, 19.7 and 35.9 fb^-1): 5.2 sigma observed, 4.2 sigma expected, signal strength 1.26 +0.31 -0.26.
  - new: Combination of ttH searches in WW, ZZ, γγ, ττ and bb final states at 7, 8 and 13 TeV (up to 5.1, 19.7 and 35.9 fb⁻¹): 5.2σ observed, 4.2σ expected, signal strength 1.26 +0.31 -0.26.

### data/atlas/results/cms-w-boson-mass-measurement-2024.json

- `/key_value/display` (key_value.display)
  - old: 80 360.2 +/- 9.9 MeV
  - new: 80 360.2 ± 9.9 MeV
- `/summary/technical` (summary.technical)
  - old: W -> mu nu events from 2016 13 TeV data, high-granularity maximum likelihood fit to muon kinematics with in situ constraints on theory inputs: m_W = 80 360.2 +/- 9.9 MeV.
  - new: W → μ ν events from 2016 13 TeV data, high-granularity maximum likelihood fit to muon kinematics with in situ constraints on theory inputs: m_W = 80 360.2 ± 9.9 MeV.

### data/atlas/results/coherent-argon-measurement-2021.json

- `/key_value/display` (key_value.display)
  - old: 2.2e-39 cm^2 (+/- 0.7e-39)
  - new: 2.2 × 10⁻³⁹ cm² (± 0.7 × 10⁻³⁹)
- `/key_value/note` (provenance note)
  - old: Flux-averaged CEvNS cross section on argon. Value 2.2e-39 cm^2 is the quote's (2.2 +/- 0.7) x 10^-39 cm^2 written in scientific notation; the +/-0.7e-39 in the display is the same quote's uncertainty.
  - new: Flux-averaged CEvNS cross section on argon. Value 2.2 × 10⁻³⁹ cm² is the quote's (2.2 ± 0.7) × 10⁻³⁹ cm² written in scientific notation; the ±0.7 × 10⁻³⁹ in the display is the same quote's uncertainty.
- `/summary/technical` (summary.technical)
  - old: First CEvNS measurement on argon using the 24 kg active-mass CENNS-10 liquid-argon detector at the SNS; two independent analyses each prefer CEvNS over the background-only hypothesis at greater than 3σ, with a flux-averaged cross section of (2.2 ± 0.7)×10^-39 cm^2 consistent with the Standard Model prediction. The collaboration states that the neutron-number dependence of this result, together with its earlier CsI measurement, confirms the existence of the CEvNS process and improves constraints on non-standard neutrino interactions.
  - new: First CEvNS measurement on argon using the 24 kg active-mass CENNS-10 liquid-argon detector at the SNS; two independent analyses each prefer CEvNS over the background-only hypothesis at greater than 3σ, with a flux-averaged cross section of (2.2 ± 0.7)×10⁻³⁹ cm² consistent with the Standard Model prediction. The collaboration states that the neutron-number dependence of this result, together with its earlier CsI measurement, confirms the existence of the CEvNS process and improves constraints on non-standard neutrino interactions.
- `/why_it_matters` (why_it_matters)
  - old: Argon is a second, lighter target nucleus after CsI, so the pair of results traces how the CEvNS cross section depends on neutron number; the paper's introduction says this establishes the N^2 behavior predicted by the Standard Model. The introduction also notes that CEvNS from solar and atmospheric neutrinos forms the "neutrino floor" background in future dark-matter searches, which cross section measurements help quantify.
  - new: Argon is a second, lighter target nucleus after CsI, so the pair of results traces how the CEvNS cross section depends on neutron number; the paper's introduction says this establishes the N² behavior predicted by the Standard Model. The introduction also notes that CEvNS from solar and atmospheric neutrinos forms the "neutrino floor" background in future dark-matter searches, which cross section measurements help quantify.

### data/atlas/results/coherent-csi-cross-section-2022.json

- `/key_value/display` (key_value.display)
  - old: 1.65e-38 cm^2 (+0.30e-38/-0.25e-38)
  - new: 1.65 × 10⁻³⁸ cm² (+0.30 × 10⁻³⁸/−0.25 × 10⁻³⁸)
- `/key_value/note` (provenance note)
  - old: All CsI[Na] data collected before detector decommissioning (the abstract says the dataset was more than doubled since the first observation), with an updated quenching model. Value derived from the quote: (165 +30/-25) x 10^-40 cm^2 = 1.65e-38 cm^2 (+0.30e-38/-0.25e-38).
  - new: All CsI[Na] data collected before detector decommissioning (the abstract says the dataset was more than doubled since the first observation), with an updated quenching model. Value derived from the quote: (165 +30/−25) × 10⁻⁴⁰ cm² = 1.65 × 10⁻³⁸ cm² (+0.30 × 10⁻³⁸/−0.25 × 10⁻³⁸).
- `/key_value_text/value` (key_value_text.value)
  - old: Weak mixing angle sin^2(theta_W) = 0.220 (+0.028/-0.026) at Q^2 ~ (50 MeV)^2, alongside constraints on non-standard interactions and a test of lepton flavor universality using the neutrino beam's timing structure
  - new: Weak mixing angle sin²θW = 0.220 (+0.028/−0.026) at Q² ~ (50 MeV)², alongside constraints on non-standard interactions and a test of lepton flavor universality using the neutrino beam's timing structure
- `/significance/note` (significance)
  - old: The abstract fetched this session does not restate a single overall significance figure for the full dataset (the original 2017 observation's 6.7 sigma is superseded but not re-quoted here); left uncertain rather than inferred.
  - new: The abstract fetched this session does not restate a single overall significance figure for the full dataset (the original 2017 observation's 6.7σ is superseded but not re-quoted here); left uncertain rather than inferred.
- `/summary/technical` (summary.technical)
  - old: All CsI[Na] data collected before detector decommissioning (13.99 GWhr of integrated beam power passing the livetime criteria), more than doubling the dataset of the first observation, with an updated quenching model reducing systematic uncertainties: cross section (165 +30/−25)×10^-40 cm^2, consistent with the Standard Model and called the most precise measurement of CEvNS yet; weak mixing angle sin^2θ_W = 0.220 +0.028/−0.026 at Q^2 ≈ (50 MeV)^2; the collaboration reports leading constraints on neutrino non-standard interactions and a lepton-flavor-universality test using the beam's timing structure.
  - new: All CsI[Na] data collected before detector decommissioning (13.99 GWhr of integrated beam power passing the livetime criteria), more than doubling the dataset of the first observation, with an updated quenching model reducing systematic uncertainties: cross section (165 +30/−25)×10⁻⁴⁰ cm², consistent with the Standard Model and called the most precise measurement of CEvNS yet; weak mixing angle sin²θW = 0.220 +0.028/−0.026 at Q² ≈ (50 MeV)²; the collaboration reports leading constraints on neutrino non-standard interactions and a lepton-flavor-universality test using the beam's timing structure.

### data/atlas/results/coherent-germanium-evidence-2024.json

- `/key_value/display` (key_value.display)
  - old: 3.9 sigma
  - new: 3.9σ
- `/summary/technical` (summary.technical)
  - old: First detection of CEvNS on natural germanium using the Ge-Mini array (eight 2.2 kg ICPC high-purity germanium detectors, 1.5 keVee threshold) operated at the SNS June-August 2023: an on-beam excess of 20.6(+7.1/-6.3) counts over 10.22 GWh*kg exposure, rejecting the no-CEvNS hypothesis at 3.9 sigma, in agreement with the Standard Model prediction within 2 sigma.
  - new: First detection of CEvNS on natural germanium using the Ge-Mini array (eight 2.2 kg ICPC high-purity germanium detectors, 1.5 keVee threshold) operated at the SNS June-August 2023: an on-beam excess of 20.6(+7.1/−6.3) counts over 10.22 GWh*kg exposure, rejecting the no-CEvNS hypothesis at 3.9σ, in agreement with the Standard Model prediction within 2σ.

### data/atlas/results/coherent-observation-2017.json

- `/key_value/display` (key_value.display)
  - old: 6.7 sigma
  - new: 6.7σ

### data/atlas/results/d0-top-quark-observation-1995.json

- `/key_value_text/value` (key_value_text.value)
  - old: 17 candidate events observed against an expected background of 3.8+/-0.6; probability of a background fluctuation 2.0e-6 (4.6 standard deviations)
  - new: 17 candidate events observed against an expected background of 3.8±0.6; probability of a background fluctuation 2.0 × 10⁻⁶ (4.6 standard deviations)
- `/summary/technical` (summary.technical)
  - old: D0 search for the Standard Model top quark in ppbar collisions at sqrt(s)=1.8 TeV, integrated luminosity about 50 pb^-1, in the dilepton and single-lepton channels with and without b-quark tagging: 17 events observed against an expected background of 3.8 ± 0.6 events; probability of an upward background fluctuation 2.0×10^-6 (equivalent to 4.6 standard deviations). The paper concludes "we have observed the top quark" and measures its mass as 199 +19/−21 (stat) ± 22 (syst) GeV/c^2 and its production cross section as 6.4 ± 2.2 pb.
  - new: D0 search for the Standard Model top quark in pp̄ collisions at √s=1.8 TeV, integrated luminosity about 50 pb⁻¹, in the dilepton and single-lepton channels with and without b-quark tagging: 17 events observed against an expected background of 3.8 ± 0.6 events; probability of an upward background fluctuation 2.0×10⁻⁶ (equivalent to 4.6 standard deviations). The paper concludes "we have observed the top quark" and measures its mass as 199 +19/−21 (stat) ± 22 (syst) GeV/c² and its production cross section as 6.4 ± 2.2 pb.

### data/atlas/results/double-chooz-evidence-2012.json

- `/summary/technical` (summary.technical)
  - old: In 227.93 live days (33.71 GW-ton-years exposure), Double Chooz observed 8,249 candidate events versus an expectation of 8,937 for theta_13 = 0. A rate-plus-spectral-shape analysis gives sin²(2θ₁₃) = 0.109±0.030(stat)±0.025(syst), excluding the no-oscillation hypothesis at 99.8% CL (2.9σ).
  - new: In 227.93 live days (33.71 GW-ton-years exposure), Double Chooz observed 8,249 candidate events versus an expectation of 8,937 for θ₁₃ = 0. A rate-plus-spectral-shape analysis gives sin²(2θ₁₃) = 0.109±0.030(stat)±0.025(syst), excluding the no-oscillation hypothesis at 99.8% CL (2.9σ).

### data/atlas/results/dune-protodune-sp-performance-2020.json

- `/summary/technical` (summary.technical)
  - old: ProtoDUNE-SP (NP04), a single-phase LArTPC with an active volume of 7.2 × 6.0 × 6.9 m^3 at the CERN Neutrino Platform, exposed to a charged-particle beam of 0.3-7 GeV/c; the paper reports first performance results (noise and gain, dE/dx calibration, drift electron lifetime, photon-detector noise, sensitivity and time resolution): the measured values meet or exceed the DUNE far-detector specifications, in several cases by large margins.
  - new: ProtoDUNE-SP (NP04), a single-phase LArTPC with an active volume of 7.2 × 6.0 × 6.9 m³ at the CERN Neutrino Platform, exposed to a charged-particle beam of 0.3-7 GeV/c; the paper reports first performance results (noise and gain, dE/dx calibration, drift electron lifetime, photon-detector noise, sensitivity and time resolution): the measured values meet or exceed the DUNE far-detector specifications, in several cases by large margins.

### data/atlas/results/icarus-hidden-sector-scalar-limit-2025.json

- `/summary/technical` (summary.technical)
  - old: Search for long-lived particles from K → π + S decays with S → μ+μ− inside ICARUS-T600, using 2.41×10^20 POT from the NuMI beam at Fermilab. No new physics signal is observed; the paper sets world-leading limits on heavy QCD axions, as well as for the Higgs portal scalar among dedicated searches, and presents limits in a model-independent way applicable to any model predicting K → π + S(→ μμ) with a long-lived S.
  - new: Search for long-lived particles from K → π + S decays with S → μ⁺μ⁻ inside ICARUS-T600, using 2.41×10²⁰ POT from the NuMI beam at Fermilab. No new physics signal is observed; the paper sets world-leading limits on heavy QCD axions, as well as for the Higgs portal scalar among dedicated searches, and presents limits in a model-independent way applicable to any model predicting K → π + S(→ μμ) with a long-lived S.

### data/atlas/results/k2k-oscillation-measurement-2006.json

- `/key_value_text/note` (provenance note)
  - old: key_value (Quantity) is left null: the ontology's Quantity unit/dimension table has no unit for a mass-squared splitting (eV^2); the value is instead carried here as free text with a verbatim quote, per section 3.12 (key_value_text).
  - new: key_value (Quantity) is left null: the ontology's Quantity unit/dimension table has no unit for a mass-squared splitting (eV²); the value is instead carried here as free text with a verbatim quote, per section 3.12 (key_value_text).
- `/key_value_text/value` (key_value_text.value)
  - old: Best fit Delta m^2 = 2.8 x 10^-3 eV^2 (allowed range 1.9-3.5 x 10^-3 eV^2 at 90% CL, maximal mixing); 112 beam-originated neutrino events observed at Super-Kamiokande vs. 158.1(+9.2/-8.6) expected without oscillation.
  - new: Best fit Δm² = 2.8 × 10⁻³ eV² (allowed range 1.9-3.5 × 10⁻³ eV² at 90% CL, maximal mixing); 112 beam-originated neutrino events observed at Super-Kamiokande vs. 158.1(+9.2/−8.6) expected without oscillation.
- `/why_it_matters` (why_it_matters)
  - old: The paper says the K2K collaboration had previously reported evidence of neutrino oscillations in a man-made neutrino beam directed 250 km across Japan; this paper presents updated ν_μ disappearance measurements: 112 observed events against 158.1 expected without oscillation, a distorted energy spectrum, and an allowed Δm² region of 1.9 to 3.5 × 10⁻³ eV² at 90% CL.
  - new: The paper says the K2K collaboration had previously reported evidence of neutrino oscillations in a man-made neutrino beam directed 250 km across Japan; this paper presents updated νμ disappearance measurements: 112 observed events against 158.1 expected without oscillation, a distorted energy spectrum, and an allowed Δm² region of 1.9 to 3.5 × 10⁻³ eV² at 90% CL.

### data/atlas/results/kamiokande-sn1987a-1987.json

- `/key_value_text/value` (key_value_text.value)
  - old: A neutrino burst of 13-second duration observed in the Kamiokande-II detector on 23 February 1987, 7:35:35 UT (+/- 1 min).
  - new: A neutrino burst of 13-second duration observed in the Kamiokande-II detector on 23 February 1987, 7:35:35 UT (± 1 min).

### data/atlas/results/km3net-arca-diffuse-flux-limit-2026.json

- `/key_value_text/value` (key_value_text.value)
  - old: All-sky single-flavour astrophysical flux (single power law, 68% credible level): phi0 = 3.0(+2.1/-2.0)x10^-18 GeV^-1 cm^-2 s^-1 sr^-1, spectral index gamma = 3.00(+0.30/-0.35). No constraint obtained for the Galactic Ridge fit at current sensitivity. Based on the first KM3NeT/ARCA configurations (6, 8, 19, 21 active detection units), 640 days total livetime.
  - new: All-sky single-flavour astrophysical flux (single power law, 68% credible level): φ₀ = 3.0(+2.1/−2.0)×10⁻¹⁸ GeV⁻¹ cm⁻² s⁻¹ sr⁻¹, spectral index γ = 3.00(+0.30/−0.35). No constraint obtained for the Galactic Ridge fit at current sensitivity. Based on the first KM3NeT/ARCA configurations (6, 8, 19, 21 active detection units), 640 days total livetime.
- `/summary/technical` (summary.technical)
  - old: Diffuse astrophysical neutrino flux search using KM3NeT/ARCA's first configurations (6, 8, 19, 21 active detection units; 640 days livetime): all-sky single-power-law fit phi0 = 3.0(+2.1/-2.0)x10^-18 GeV^-1 cm^-2 s^-1 sr^-1, gamma = 3.00(+0.30/-0.35) at 68% credible level; no statistically significant results, upper limits derived for both the all-sky and Galactic Ridge searches.
  - new: Diffuse astrophysical neutrino flux search using KM3NeT/ARCA's first configurations (6, 8, 19, 21 active detection units; 640 days livetime): all-sky single-power-law fit φ₀ = 3.0(+2.1/−2.0)×10⁻¹⁸ GeV⁻¹ cm⁻² s⁻¹ sr⁻¹, γ = 3.00(+0.30/−0.35) at 68% credible level; no statistically significant results, upper limits derived for both the all-sky and Galactic Ridge searches.

### data/atlas/results/lep-higgs-exclusion-2003.json

- `/key_value/display` (key_value.display)
  - old: 114.4 GeV/c^2 (95% CL lower bound)
  - new: 114.4 GeV/c² (95% CL lower bound)
- `/key_value_text/value` (key_value_text.value)
  - old: Combined LEP2 direct-search data exclude a Standard Model Higgs boson lighter than 114.4 GeV/c^2 at 95% confidence level.
  - new: Combined LEP2 direct-search data exclude a Standard Model Higgs boson lighter than 114.4 GeV/c² at 95% confidence level.
- `/summary/technical` (summary.technical)
  - old: ALEPH, DELPHI, L3 and OPAL (the LEP Working Group for Higgs Boson Searches) combined 2461 pb^-1 of e+e- data at centre-of-mass energies between 189 and 209 GeV in a likelihood test of the background and signal-plus-background hypotheses (Phys. Lett. B 565, 2003, 61-75; arXiv:hep-ex/0306033): a lower bound of 114.4 GeV/c^2 is established at the 95% confidence level on the mass of the Standard Model Higgs boson, and upper bounds are set on the HZZ coupling for various assumptions concerning the decay of the Higgs boson.
  - new: ALEPH, DELPHI, L3 and OPAL (the LEP Working Group for Higgs Boson Searches) combined 2461 pb⁻¹ of e⁺e⁻ data at centre-of-mass energies between 189 and 209 GeV in a likelihood test of the background and signal-plus-background hypotheses (Phys. Lett. B 565, 2003, 61-75; arXiv:hep-ex/0306033): a lower bound of 114.4 GeV/c² is established at the 95% confidence level on the mass of the Standard Model Higgs boson, and upper bounds are set on the HZZ coupling for various assumptions concerning the decay of the Higgs boson.

### data/atlas/results/lep-three-neutrino-species-1989.json

- `/notes/0` (notes[])
  - old: This entity records the historic 1989 determinations of the number of light neutrino species; the final precision value (2.9840+/-0.0082, LEP+SLD, arXiv:hep-ex/0509008) is recorded separately as result:lep-electroweak-precision-2006 and is no longer used as this record's key_value (a review found it read as the 1989 result). date/date_kind reflect the 1989 papers.
  - new: This entity records the historic 1989 determinations of the number of light neutrino species; the final precision value (2.9840±0.0082, LEP+SLD, arXiv:hep-ex/0509008) is recorded separately as result:lep-electroweak-precision-2006 and is no longer used as this record's key_value (a review found it read as the 1989 result). date/date_kind reflect the 1989 papers.

### data/atlas/results/lhcb-cp-violation-charm-observation-2019.json

- `/key_value_text/value` (key_value_text.value)
  - old: ΔA_CP = (-15.4 ± 2.9) x 10^-4
  - new: ΔA_CP = (-15.4 ± 2.9) × 10⁻⁴
- `/summary/technical` (summary.technical)
  - old: Measurement of the CP-asymmetry difference ΔA_CP between D0→K−K+ and D0→π−π+ decays using about 6 fb−1 of 13 TeV pp data; combined with previous LHCb results, ΔA_CP = (−15.4±2.9)×10−4, which the paper says differs from zero by more than five standard deviations. The paper states this is the first observation of CP violation in the decay of charm hadrons.
  - new: Measurement of the CP-asymmetry difference ΔA_CP between D⁰→K⁻K⁺ and D⁰→π⁻π⁺ decays using about 6 fb⁻¹ of 13 TeV pp data; combined with previous LHCb results, ΔA_CP = (−15.4±2.9)×10⁻⁴, which the paper says differs from zero by more than five standard deviations. The paper states this is the first observation of CP violation in the decay of charm hadrons.
- `/why_it_matters` (why_it_matters)
  - old: The paper says CP violation had been established in the K- and B-meson systems but that its observation in the charm sector had not been achieved despite decades of searches. It reports the result as consistent with, although in magnitude at the upper end of, Standard Model expectations (10−4 to 10−3), and says further measurements will help establish whether it is consistent with the Standard Model or indicates new dynamics in the up-quark sector.
  - new: The paper says CP violation had been established in the K- and B-meson systems but that its observation in the charm sector had not been achieved despite decades of searches. It reports the result as consistent with, although in magnitude at the upper end of, Standard Model expectations (10⁻⁴ to 10⁻³), and says further measurements will help establish whether it is consistent with the Standard Model or indicates new dynamics in the up-quark sector.

### data/atlas/results/lhcb-doubly-charmed-baryon-observation-2017.json

- `/key_value_text/value` (key_value_text.value)
  - old: m(Ξcc++) = 3621.40 ± 0.72(stat) ± 0.27(syst) ± 0.14(Λc+) MeV/c^2
  - new: m(Ξcc⁺⁺) = 3621.40 ± 0.72(stat) ± 0.27(syst) ± 0.14(Λc⁺) MeV/c²
- `/name` (name)
  - old: Observation of the doubly charmed baryon Xi_cc++
  - new: Observation of the doubly charmed baryon Ξcc⁺⁺
- `/summary/plain` (summary.plain)
  - old: LHCb observed a baryon (a proton-like particle) containing two charm quarks, the Ξcc++, as a highly significant structure in its data. The quark model predicts such particles; an earlier claim by the SELEX experiment for a related state was not seen by several other searches.
  - new: LHCb observed a baryon (a proton-like particle) containing two charm quarks, the Ξcc⁺⁺, as a highly significant structure in its data. The quark model predicts such particles; an earlier claim by the SELEX experiment for a related state was not seen by several other searches.
- `/summary/technical` (summary.technical)
  - old: A highly significant structure in the Λc+K-π+π+ mass spectrum is identified as the weakly decaying doubly charmed baryon Ξcc++; the mass difference m(Ξcc++)-m(Λc+) is measured to be 1334.94±0.72(stat)±0.27(syst) MeV/c^2, giving m(Ξcc++)=3621.40±0.72±0.27±0.14 MeV/c^2.
  - new: A highly significant structure in the Λc⁺K⁻π⁺π⁺ mass spectrum is identified as the weakly decaying doubly charmed baryon Ξcc⁺⁺; the mass difference m(Ξcc⁺⁺)-m(Λc⁺) is measured to be 1334.94±0.72(stat)±0.27(syst) MeV/c², giving m(Ξcc⁺⁺)=3621.40±0.72±0.27±0.14 MeV/c².
- `/why_it_matters` (why_it_matters)
  - old: The quark model predicts doubly charmed baryons; in most calculations the Ξcc masses lie between 3500 and 3700 MeV/c², and the measured Ξcc++ mass is 3621.40 MeV/c². The paper describes a longstanding puzzle: SELEX reported a Ξcc+ state at 3519 MeV/c², which FOCUS, BaBar, Belle and an earlier LHCb search did not find (the paper notes these null results do not exclude the original observations because the production environments differ).
  - new: The quark model predicts doubly charmed baryons; in most calculations the Ξcc masses lie between 3500 and 3700 MeV/c², and the measured Ξcc⁺⁺ mass is 3621.40 MeV/c². The paper describes a longstanding puzzle: SELEX reported a Ξcc+ state at 3519 MeV/c², which FOCUS, BaBar, Belle and an earlier LHCb search did not find (the paper notes these null results do not exclude the original observations because the production environments differ).

### data/atlas/results/lhcb-pentaquark-observation-2015.json

- `/summary/technical` (summary.technical)
  - old: Amplitude analysis of Λb0→J/ψK−p decays (3 fb−1, 7 and 8 TeV pp collisions): a satisfactory fit of the J/ψ p mass spectrum needs two Breit-Wigner resonances, each with significance of more than 9 standard deviations, with masses 4380±8±29 MeV (width 205±18±86 MeV) and 4449.8±1.7±2.5 MeV (width 39±5±19 MeV). The preferred JP assignments are of opposite parity, with one state of spin 3/2 and the other 5/2. Interpreted as resonant states they must have minimal quark content ccuud.
  - new: Amplitude analysis of Λb⁰→J/ψK⁻p decays (3 fb⁻¹, 7 and 8 TeV pp collisions): a satisfactory fit of the J/ψ p mass spectrum needs two Breit-Wigner resonances, each with significance of more than 9 standard deviations, with masses 4380±8±29 MeV (width 205±18±86 MeV) and 4449.8±1.7±2.5 MeV (width 39±5±19 MeV). The preferred JP assignments are of opposite parity, with one state of spin 3/2 and the other 5/2. Interpreted as resonant states they must have minimal quark content ccuud.

### data/atlas/results/lsnd-antineutrino-appearance-evidence-2001.json

- `/summary/technical` (summary.technical)
  - old: LSND search for ν̄μ→ν̄e oscillations with ν̄μ from μ+ decay at rest (the paper's introduction calls these the final results using all the data): a total excess of 87.9 ± 22.4 ± 6.0 events consistent with ν̄e p → e+ n scattering was observed above the expected background, corresponding to an oscillation probability of (0.264 ± 0.067 ± 0.045)%. In conjunction with other known limits, the paper says the data suggest oscillations in the 0.2–10 eV²/c⁴ Δm² range, indicating a neutrino mass greater than 0.4 eV/c².
  - new: LSND search for ν̄μ→ν̄e oscillations with ν̄μ from μ+ decay at rest (the paper's introduction calls these the final results using all the data): a total excess of 87.9 ± 22.4 ± 6.0 events consistent with ν̄e p → e⁺ n scattering was observed above the expected background, corresponding to an oscillation probability of (0.264 ± 0.067 ± 0.045)%. In conjunction with other known limits, the paper says the data suggest oscillations in the 0.2–10 eV²/c⁴ Δm² range, indicating a neutrino mass greater than 0.4 eV/c².

### data/atlas/results/lux-complete-exposure-2016.json

- `/key_value/display` (key_value.display)
  - old: 1.1e-46 cm^2
  - new: 1.1 × 10⁻⁴⁶ cm²
- `/key_value/note` (provenance note)
  - old: Combined WS2013 + WS2014-16 spin-independent WIMP-nucleon limit at 90% CL and 50 GeV/c². The WS2014-16 exposure alone gives 2.2e-46 cm².
  - new: Combined WS2013 + WS2014-16 spin-independent WIMP-nucleon limit at 90% CL and 50 GeV/c². The WS2014-16 exposure alone gives 2.2 × 10⁻⁴⁶ cm².
- `/summary/technical` (summary.technical)
  - old: WS2014-16 exposure of 3.35×10⁴ kg day (332.0 live days, 11 Sep 2014 - 2 May 2016) in a dual-phase xenon TPC with 250 kg of active mass, combined with the earlier WS2013 exposure. No evidence of WIMP nuclear recoils; spin-independent WIMP-nucleon cross sections above 2.2e-46 cm² at 50 GeV/c² are excluded at 90% CL, strengthening to 1.1e-46 cm² when combined with the previously reported LUX exposure.
  - new: WS2014-16 exposure of 3.35×10⁴ kg day (332.0 live days, 11 Sep 2014 - 2 May 2016) in a dual-phase xenon TPC with 250 kg of active mass, combined with the earlier WS2013 exposure. No evidence of WIMP nuclear recoils; spin-independent WIMP-nucleon cross sections above 2.2 × 10⁻⁴⁶ cm² at 50 GeV/c² are excluded at 90% CL, strengthening to 1.1 × 10⁻⁴⁶ cm² when combined with the previously reported LUX exposure.

### data/atlas/results/lux-first-wimp-search-2013.json

- `/key_value/display` (key_value.display)
  - old: 7.6e-46 cm^2
  - new: 7.6 × 10⁻⁴⁶ cm²
- `/summary/technical` (summary.technical)
  - old: WS2013: 85.3 live days, 118 kg fiducial volume, April-August 2013. Data consistent with the background-only hypothesis; minimum 90% CL spin-independent WIMP-nucleon cross-section upper limit 7.6e-46 cm² at 33 GeV/c². The paper reports the data to be in disagreement with low-mass WIMP signal interpretations of the results from several recent direct detection experiments.
  - new: WS2013: 85.3 live days, 118 kg fiducial volume, April-August 2013. Data consistent with the background-only hypothesis; minimum 90% CL spin-independent WIMP-nucleon cross-section upper limit 7.6 × 10⁻⁴⁶ cm² at 33 GeV/c². The paper reports the data to be in disagreement with low-mass WIMP signal interpretations of the results from several recent direct detection experiments.

### data/atlas/results/lz-first-wimp-search-2022.json

- `/key_value/display` (key_value.display)
  - old: 9.2e-48 cm^2
  - new: 9.2 × 10⁻⁴⁸ cm²
- `/summary/technical` (summary.technical)
  - old: SR1: 60 live days, 5.5 t fiducial, 23 Dec 2021 - 11 May 2022. Data consistent with background only; spin-independent WIMP-nucleon cross sections above 9.2e-48 cm² rejected at 90% CL at 36 GeV/c², with limits also set on spin-dependent WIMP-neutron and WIMP-proton couplings for WIMP masses above 9 GeV/c².
  - new: SR1: 60 live days, 5.5 t fiducial, 23 Dec 2021 - 11 May 2022. Data consistent with background only; spin-independent WIMP-nucleon cross sections above 9.2 × 10⁻⁴⁸ cm² rejected at 90% CL at 36 GeV/c², with limits also set on spin-dependent WIMP-neutron and WIMP-proton couplings for WIMP masses above 9 GeV/c².

### data/atlas/results/lz-ws2024-wimp-search-2024.json

- `/key_value/display` (key_value.display)
  - old: 2.2e-48 cm^2
  - new: 2.2 × 10⁻⁴⁸ cm²
- `/summary/technical` (summary.technical)
  - old: WS2024: total exposure 4.2 ± 0.1 tonne-years from 280 live days, of which 3.3 ± 0.1 tonne-years and 220 live days are new, combined with the 60-live-day WS2022 exposure. A technique to tag 214Pb β-decay backgrounds is used for the first time, and enhanced recombination in 124Xe two-neutrino double electron capture decays is a noteworthy new background. No evidence for an excess over expected backgrounds; the strongest spin-independent exclusion is 2.2e-48 cm² at 40 GeV/c² (90% CL) and the best spin-independent median sensitivity is 5.1e-48 cm².
  - new: WS2024: total exposure 4.2 ± 0.1 tonne-years from 280 live days, of which 3.3 ± 0.1 tonne-years and 220 live days are new, combined with the 60-live-day WS2022 exposure. A technique to tag 214Pb β-decay backgrounds is used for the first time, and enhanced recombination in 124Xe two-neutrino double electron capture decays is a noteworthy new background. No evidence for an excess over expected backgrounds; the strongest spin-independent exclusion is 2.2 × 10⁻⁴⁸ cm² at 40 GeV/c² (90% CL) and the best spin-independent median sensitivity is 5.1 × 10⁻⁴⁸ cm².

### data/atlas/results/meg-ii-mu-to-e-gamma-limit-2024.json

- `/key_value_text/value` (key_value_text.value)
  - old: MEG II alone: B(mu+->e+gamma) < 7.5x10^-13 (90% C.L.); combined with MEG: < 3.1x10^-13 (90% C.L.)
  - new: MEG II alone: B(μ⁺→e⁺γ) < 7.5×10⁻¹³ (90% C.L.); combined with MEG: < 3.1×10⁻¹³ (90% C.L.)

### data/atlas/results/meg-mu-to-e-gamma-limit-2016.json

- `/key_value_text/value` (key_value_text.value)
  - old: BR(mu+ -> e+ gamma) < 4.2 x 10^-13 (90% C.L.)
  - new: BR(μ⁺ → e⁺ γ) < 4.2 × 10⁻¹³ (90% C.L.)

### data/atlas/results/miniboone-low-energy-excess-2021.json

- `/key_value/note` (provenance note)
  - old: Combined neutrino- and antineutrino-mode electron-like event excess, full MiniBooNE exposure (18.75e20 POT neutrino mode, 11.27e20 POT antineutrino mode).
  - new: Combined neutrino- and antineutrino-mode electron-like event excess, full MiniBooNE exposure (18.75 × 10²⁰ POT neutrino mode, 11.27 × 10²⁰ POT antineutrino mode).

### data/atlas/results/minos-oscillation-measurement-2013.json

- `/summary/technical` (summary.technical)
  - old: Combined NuMI beam and atmospheric-neutrino analysis: |Δm²|=(2.41+0.09-0.10)x10^-3 eV^2, sin^2(2θ)=0.950+0.035-0.036 (identical ν/ν̄ assumption); separate antineutrino fit gives |Δm̄²|=(2.50+0.23-0.25)x10^-3 eV^2, sin^2(2θ̄)=0.97+0.03-0.08, using 37.88 kton-years of atmospheric data plus beam exposure.
  - new: Combined NuMI beam and atmospheric-neutrino analysis: |Δm²|=(2.41+0.09−0.10)×10⁻³ eV², sin²2θ=0.950+0.035−0.036 (identical ν/ν̄ assumption); separate antineutrino fit gives |Δm̄²|=(2.50+0.23−0.25)×10⁻³ eV², sin²2θ̄=0.97+0.03−0.08, using 37.88 kton-years of atmospheric data plus beam exposure.

### data/atlas/results/muon-g-2-measurement-2021.json

- `/key_value_text/value` (key_value_text.value)
  - old: a_mu = 116,592,040(54) x 10^-11 (0.46 ppm)
  - new: aμ = 116,592,040(54) × 10⁻¹¹ (0.46 ppm)
- `/summary/technical` (summary.technical)
  - old: First results of the Fermilab Muon g-2 Experiment: a_μ(FNAL) = 116,592,040(54)×10⁻¹¹ (0.46 ppm), 3.3 standard deviations greater than the Standard Model prediction and in excellent agreement with BNL E821. Combined with previous measurements of both μ⁺ and μ⁻, the new experimental average is a_μ(Exp) = 116,592,061(41)×10⁻¹¹ (0.35 ppm), which increases the tension between experiment and theory to 4.2 standard deviations.
  - new: First results of the Fermilab Muon g-2 Experiment: aμ(FNAL) = 116,592,040(54)×10⁻¹¹ (0.46 ppm), 3.3 standard deviations greater than the Standard Model prediction and in excellent agreement with BNL E821. Combined with previous measurements of both μ⁺ and μ⁻, the new experimental average is aμ(Exp) = 116,592,061(41)×10⁻¹¹ (0.35 ppm), which increases the tension between experiment and theory to 4.2 standard deviations.

### data/atlas/results/muon-g-2-measurement-2023.json

- `/key_value_text/value` (key_value_text.value)
  - old: a_μ(FNAL) = 116,592,055(24)×10⁻¹¹ (0.20 ppm); new experimental world average a_μ(exp) = 116,592,059(22)×10⁻¹¹ (0.19 ppm), a factor of 2 improvement in precision
  - new: aμ(FNAL) = 116,592,055(24)×10⁻¹¹ (0.20 ppm); new experimental world average aμ(exp) = 116,592,059(22)×10⁻¹¹ (0.19 ppm), a factor of 2 improvement in precision
- `/summary/technical` (summary.technical)
  - old: Run-2 and Run-3 data (collected in 2019 and 2020) with more than 4 times the number of positrons from muon decay than the previous result from 2018 data; the systematic error is reduced by more than a factor of 2. these data alone give a_μ = 116,592,057(25)×10⁻¹¹ (0.21 ppm), and combined with the 2018 result a_μ(FNAL) = 116,592,055(24)×10⁻¹¹ (0.20 ppm); the new experimental world average a_μ(exp) = 116,592,059(22)×10⁻¹¹ (0.19 ppm) represents a factor of 2 improvement in precision.
  - new: Run-2 and Run-3 data (collected in 2019 and 2020) with more than 4 times the number of positrons from muon decay than the previous result from 2018 data; the systematic error is reduced by more than a factor of 2. these data alone give aμ = 116,592,057(25)×10⁻¹¹ (0.21 ppm), and combined with the 2018 result aμ(FNAL) = 116,592,055(24)×10⁻¹¹ (0.20 ppm); the new experimental world average aμ(exp) = 116,592,059(22)×10⁻¹¹ (0.19 ppm) represents a factor of 2 improvement in precision.

### data/atlas/results/muon-g-2-measurement-2025.json

- `/key_value_text/value` (key_value_text.value)
  - old: a_mu = 116,592,0705(148) x 10^-12 (127 ppb) combined with previous results; new experimental world average a_mu(exp) = 116,592,0715(145) x 10^-12 (124 ppb)
  - new: aμ = 116,592,0705(148) × 10⁻¹² (127 ppb) combined with previous results; new experimental world average aμ(exp) = 116,592,0715(145) × 10⁻¹² (124 ppb)
- `/summary/technical` (summary.technical)
  - old: New data taken from 2020 to 2023 (over 2.5 times the total statistics of the previous results): a_μ = 116,592,0710(162)×10⁻¹² (139 ppb) for the new datasets and 116,592,0705(148)×10⁻¹² (127 ppb) combined with the previous results; the new experimental world average, dominated by the measurements at FNAL, is a_μ(exp) = 116,592,0715(145)×10⁻¹² (124 ppb). The paper says the measurements at FNAL have improved the precision on the world average by over a factor of four. Fermilab's announcement calls it the third and final result.
  - new: New data taken from 2020 to 2023 (over 2.5 times the total statistics of the previous results): aμ = 116,592,0710(162)×10⁻¹² (139 ppb) for the new datasets and 116,592,0705(148)×10⁻¹² (127 ppb) combined with the previous results; the new experimental world average, dominated by the measurements at FNAL, is aμ(exp) = 116,592,0715(145)×10⁻¹² (124 ppb). The paper says the measurements at FNAL have improved the precision on the world average by over a factor of four. Fermilab's announcement calls it the third and final result.

### data/atlas/results/na62-2026-refined-measurement.json

- `/key_value/display` (key_value.display)
  - old: (9.6+1.9-1.8) x 10^-11
  - new: (9.6+1.9−1.8) × 10⁻¹¹
- `/key_value/note` (provenance note)
  - old: Branching ratio in units of 10^-11; stored as a bare count-like number because the ontology has no branching-ratio dimension. Confirmed verbatim in arXiv:2607.16413 abstract, corroborated by the earlier CERN news article. See key_value_text for the fully formatted value.
  - new: Branching ratio in units of 10⁻¹¹; stored as a bare count-like number because the ontology has no branching-ratio dimension. Confirmed verbatim in arXiv:2607.16413 abstract, corroborated by the earlier CERN news article. See key_value_text for the fully formatted value.
- `/key_value_text/value` (key_value_text.value)
  - old: B(K+ -> pi+ nu nubar) = (9.6+1.9-1.8) x 10^-11, combining data collected 2016-2024 (including newly analysed 2023-2024 data: B_2023-2024 = (7.2+2.3-2.1) x 10^-11), a relative precision of 20%
  - new: B(K⁺ → π⁺ ν ν̄) = (9.6+1.9−1.8) × 10⁻¹¹, combining data collected 2016-2024 (including newly analysed 2023-2024 data: B_2023-2024 = (7.2+2.3−2.1) × 10⁻¹¹), a relative precision of 20%
- `/notes/0` (notes[])
  - old: Originally sourced only to a CERN news article about a conference talk (press_release), which left claim.quote in violation of A16 (claim must come from the publication title/abstract or the collaboration's own result page, never a press release). Fixed 2026-09-17 during fixed-target wave-3 verification: claim, key_value corroboration, publication and publication_source_id now cite arXiv:2607.16413 (CERN-EP-2026-214, submitted 17 July 2026), 'Measurement of the branching ratio of the K+ -> pi+ nu nubar decay', which restates the identical (9.6+1.9-1.8) x 10^-11 central value first announced at the 2026 La Thuile conference.
  - new: Originally sourced only to a CERN news article about a conference talk (press_release), which left claim.quote in violation of A16 (claim must come from the publication title/abstract or the collaboration's own result page, never a press release). Fixed 2026-09-17 during fixed-target wave-3 verification: claim, key_value corroboration, publication and publication_source_id now cite arXiv:2607.16413 (CERN-EP-2026-214, submitted 17 July 2026), 'Measurement of the branching ratio of the K+ -> pi+ nu nubar decay', which restates the identical (9.6+1.9−1.8) × 10⁻¹¹ central value first announced at the 2026 La Thuile conference.

### data/atlas/results/na62-jhep-2021-measurement.json

- `/key_value/display` (key_value.display)
  - old: (10.6+4.0-3.4|stat +- 0.9syst) x 10^-11
  - new: (10.6+4.0−3.4|stat ± 0.9syst) × 10⁻¹¹
- `/key_value/note` (provenance note)
  - old: Branching ratio in units of 10^-11; stored as a bare count-like number because the ontology has no branching-ratio dimension. See key_value_text for the fully formatted value.
  - new: Branching ratio in units of 10⁻¹¹; stored as a bare count-like number because the ontology has no branching-ratio dimension. See key_value_text for the fully formatted value.
- `/key_value_text/value` (key_value_text.value)
  - old: BR(K+ -> pi+ nu nubar) = (10.6+4.0-3.4|stat +- 0.9syst) x 10^-11, based on 20 signal candidates with an expected background of 7.0 events
  - new: BR(K⁺ → π⁺ ν ν̄) = (10.6+4.0−3.4|stat ± 0.9syst) × 10⁻¹¹, based on 20 signal candidates with an expected background of 7.0 events
- `/summary/technical` (summary.technical)
  - old: Branching-ratio measurement of K+ -> pi+ nu nubar from the 2016-2018 NA62 data set: BR = (10.6+4.0-3.4|stat ± 0.9syst)×10⁻¹¹ at 68% CL, based on 20 signal candidates with an expected background of 7.0 events; the paper says this provides evidence for the decay, observed with a significance of 3.4σ.
  - new: Branching-ratio measurement of K⁺ → π⁺ ν ν̄ from the 2016-2018 NA62 data set: BR = (10.6+4.0−3.4|stat ± 0.9syst)×10⁻¹¹ at 68% CL, based on 20 signal candidates with an expected background of 7.0 events; the paper says this provides evidence for the decay, observed with a significance of 3.4σ.

### data/atlas/results/na62-jhep-2025-observation.json

- `/key_value/display` (key_value.display)
  - old: (13.0+3.3-3.0) x 10^-11
  - new: (13.0+3.3−3.0) × 10⁻¹¹
- `/key_value/note` (provenance note)
  - old: Branching ratio in units of 10^-11; stored as a bare count-like number because the ontology has no branching-ratio dimension. See key_value_text for the fully formatted value.
  - new: Branching ratio in units of 10⁻¹¹; stored as a bare count-like number because the ontology has no branching-ratio dimension. See key_value_text for the fully formatted value.
- `/key_value_text/value` (key_value_text.value)
  - old: B(K+ -> pi+ nu nubar) = (13.0+3.3-3.0) x 10^-11, from 51 signal candidates with an expected background of 18(+3/-2) events, combining data from 2016-2022
  - new: B(K⁺ → π⁺ ν ν̄) = (13.0+3.3−3.0) × 10⁻¹¹, from 51 signal candidates with an expected background of 18(+3/−2) events, combining data from 2016-2022
- `/summary/technical` (summary.technical)
  - old: Observation of K+ -> pi+ nu nubar (significance above 5σ; background-only p-value 2×10⁻⁷): B(K+ -> pi+ nu nubar) = (13.0+3.3-3.0)×10⁻¹¹ combining 2016-2022 data, including the 2021-2022 data taken at higher beam intensity after modifications to the beamline and detectors; 51 signal candidates with an expected background of 18(+3/-2) events. The paper says the decay becomes the smallest branching ratio measured with a signal significance above 5σ.
  - new: Observation of K⁺ → π⁺ ν ν̄ (significance above 5σ; background-only p-value 2×10⁻⁷): B(K⁺ → π⁺ ν ν̄) = (13.0+3.3−3.0)×10⁻¹¹ combining 2016-2022 data, including the 2021-2022 data taken at higher beam intensity after modifications to the beamline and detectors; 51 signal candidates with an expected background of 18(+3/−2) events. The paper says the decay becomes the smallest branching ratio measured with a signal significance above 5σ.

### data/atlas/results/nova-oscillation-parameters-2022.json

- `/key_value_text/value` (key_value_text.value)
  - old: Best fit: Δm²₃₂ = (2.41±0.07)×10⁻³ eV², sin²θ₂₃ = 0.57 +0.03/−0.04 (upper octant), best-fit point in the normal mass ordering; δ_CP near π/2 excluded by >3σ for the inverted ordering, values around 3π/2 disfavored at 2σ for the normal ordering
  - new: Best fit: Δm²₃₂ = (2.41±0.07)×10⁻³ eV², sin²θ₂₃ = 0.57 +0.03/−0.04 (upper octant), best-fit point in the normal mass ordering; δCP near π/2 excluded by >3σ for the inverted ordering, values around 3π/2 disfavored at 2σ for the normal ordering
- `/significance/note` (significance)
  - old: A multi-parameter oscillation measurement, not a single-significance discovery/observation; specific exclusions (e.g. delta_CP near pi/2 for inverted ordering) are quoted at different confidence levels in key_value_text.
  - new: A multi-parameter oscillation measurement, not a single-significance discovery/observation; specific exclusions (e.g. δCP near π/2 for inverted ordering) are quoted at different confidence levels in key_value_text.
- `/summary/technical` (summary.technical)
  - old: Joint νμ/ν̄μ disappearance and νe/ν̄e appearance fit within the three-flavor framework, with a 50% increase in neutrino-mode beam exposure over the previously reported results: best-fit point in the normal mass ordering and the upper octant of θ23, with Δm²₃₂ = (2.41±0.07)×10⁻³ eV² and sin²θ₂₃ = 0.57 +0.03/−0.04; values of δ_CP in the vicinity of π/2 are excluded by >3σ for the inverted mass ordering, and values around 3π/2 in the normal ordering are disfavored at 2σ.
  - new: Joint νμ/ν̄μ disappearance and νe/ν̄e appearance fit within the three-flavor framework, with a 50% increase in neutrino-mode beam exposure over the previously reported results: best-fit point in the normal mass ordering and the upper octant of θ23, with Δm²₃₂ = (2.41±0.07)×10⁻³ eV² and sin²θ₂₃ = 0.57 +0.03/−0.04; values of δCP in the vicinity of π/2 are excluded by >3σ for the inverted mass ordering, and values around 3π/2 in the normal ordering are disfavored at 2σ.
- `/why_it_matters` (why_it_matters)
  - old: The abstract says the data disfavor combinations of oscillation parameters that give rise to a large asymmetry in the rates of νe and ν̄e appearance, including values of the CP-violating phase δ_CP near π/2 (excluded by >3σ for the inverted mass ordering) and values around 3π/2 in the normal ordering (disfavored at 2σ).
  - new: The abstract says the data disfavor combinations of oscillation parameters that give rise to a large asymmetry in the rates of νe and ν̄e appearance, including values of the CP-violating phase δCP near π/2 (excluded by >3σ for the inverted mass ordering) and values around 3π/2 in the normal ordering (disfavored at 2σ).

### data/atlas/results/nova-t2k-joint-oscillation-analysis-2025.json

- `/key_value_text/value` (key_value_text.value)
  - old: |Δm²₃₂| = 2.43(+0.04/-0.03)×10⁻³ eV² (normal ordering) or -2.48(+0.03/-0.04)×10⁻³ eV² (inverted ordering); 3σ interval on δ_CP of [-1.38π, 0.30π] (normal) / [-0.92π, -0.04π] (inverted)
  - new: |Δm²₃₂| = 2.43(+0.04/−0.03)×10⁻³ eV² (normal ordering) or -2.48(+0.03/−0.04)×10⁻³ eV² (inverted ordering); 3σ interval on δCP of [-1.38π, 0.30π] (normal) / [-0.92π, -0.04π] (inverted)
- `/summary/technical` (summary.technical)
  - old: First joint three-flavor oscillation analysis of NOvA and T2K data sets, taking advantage of the experiments' complementary designs (the νμ→νe oscillation probability depends on both δ_CP and the mass ordering, which must be teased apart). Reports |Δm²₃₂| = 2.43 +0.04/−0.03 (normal ordering) or −2.48 +0.03/−0.04 (inverted ordering) ×10⁻³ eV², and a 3σ interval on δ_CP of [−1.38π, 0.30π] (normal) / [−0.92π, −0.04π] (inverted). The data show no strong preference for either mass ordering.
  - new: First joint three-flavor oscillation analysis of NOvA and T2K data sets, taking advantage of the experiments' complementary designs (the νμ→νe oscillation probability depends on both δCP and the mass ordering, which must be teased apart). Reports |Δm²₃₂| = 2.43 +0.04/−0.03 (normal ordering) or −2.48 +0.03/−0.04 (inverted ordering) ×10⁻³ eV², and a 3σ interval on δCP of [−1.38π, 0.30π] (normal) / [−0.92π, −0.04π] (inverted). The data show no strong preference for either mass ordering.

### data/atlas/results/sage-capture-rate-1999.json

- `/key_value/display` (key_value.display)
  - old: 67.2 (+7.2/-7.0 stat) (+3.5/-3.0 syst) SNU
  - new: 67.2 (+7.2/−7.0 stat) (+3.5/−3.0 syst) SNU
- `/key_value_text/value` (key_value_text.value)
  - old: 67.2 (+7.2/-7.0 stat) (+3.5/-3.0 syst) SNU, ~half the Standard Solar Model's 129 SNU prediction
  - new: 67.2 (+7.2/−7.0 stat) (+3.5/−3.0 syst) SNU, ~half the Standard Solar Model's 129 SNU prediction
- `/summary/technical` (summary.technical)
  - old: Solar neutrino capture rate on gallium, January 1990-December 1997, measured at 67.2 (+7.2/-7.0 stat) (+3.5/-3.0 syst) SNU, about half the Standard Solar Model prediction of 129 SNU.
  - new: Solar neutrino capture rate on gallium, January 1990-December 1997, measured at 67.2 (+7.2/−7.0 stat) (+3.5/−3.0 syst) SNU, about half the Standard Solar Model prediction of 129 SNU.

### data/atlas/results/sk-atmospheric-oscillation-evidence-1998.json

- `/key_value_text/value` (key_value_text.value)
  - old: Zenith-angle-dependent deficit of muon neutrinos inconsistent with expectations for no oscillation; data consistent with two-flavour nu_mu <-> nu_tau oscillation.
  - new: Zenith-angle-dependent deficit of muon neutrinos inconsistent with expectations for no oscillation; data consistent with two-flavour νμ ↔ ντ oscillation.

### data/atlas/results/sk-dsnb-limit-2025.json

- `/significance/note` (significance)
  - old: The abstract separately notes a spectral-fitting result with a ~1.2 sigma disagreement with the null-DSNB hypothesis, not a detection claim.
  - new: The abstract separately notes a spectral-fitting result with a ~1.2σ disagreement with the null-DSNB hypothesis, not a detection claim.

### data/atlas/results/sk-solar-neutrino-measurement-2024.json

- `/key_value/display` (key_value.display)
  - old: 2.336e6 cm^-2 s^-1 (all-SK-phase combined 8B flux)
  - new: 2.336 × 10⁶ cm⁻² s⁻¹ (all-SK-phase combined 8B flux)
- `/key_value/note` (provenance note)
  - old: Value taken from the paper text: 8B flux combined with all SK phases up to SK-IV, (2.336 ± 0.011 (stat.) ± 0.043 (syst.))×10⁶ cm⁻² s⁻¹; dimension 'luminosity' (cm^-2 s^-1) is the closest match in the ontology's unit table to a neutrino flux, though the physical quantity is a particle flux rather than a photon luminosity.
  - new: Value taken from the paper text: 8B flux combined with all SK phases up to SK-IV, (2.336 ± 0.011 (stat.) ± 0.043 (syst.))×10⁶ cm⁻² s⁻¹; dimension 'luminosity' (cm⁻² s⁻¹) is the closest match in the ontology's unit table to a neutrino flux, though the physical quantity is a particle flux rather than a photon luminosity.

### data/atlas/results/sno-cc-evidence-2001.json

- `/key_value_text/value` (key_value_text.value)
  - old: φ^CC(ν_e) = 1.75 ± 0.07 (stat) +0.12/-0.11 (sys) ± 0.05(theor) × 10^6 cm^-2 s^-1; 3.3σ difference vs Super-K ES flux
  - new: φ^CC(νe) = 1.75 ± 0.07 (stat) +0.12/−0.11 (sys) ± 0.05(theor) × 10⁶ cm⁻² s⁻¹; 3.3σ difference vs Super-K ES flux
- `/name` (name)
  - old: Measurement of the rate of ν_e+d→p+p+e− interactions produced by 8B solar neutrinos at the Sudbury Neutrino Observatory
  - new: Measurement of the rate of νe+d→p+p+e− interactions produced by 8B solar neutrinos at the Sudbury Neutrino Observatory
- `/summary/technical` (summary.technical)
  - old: Charged-current 8B solar-neutrino flux measured at SNO, φ^CC(ν_e) = 1.75 ± 0.07 (stat) +0.12/-0.11 (sys) ± 0.05(theor) × 10^6 cm^-2 s^-1; comparison to Super-Kamiokande's elastic-scattering flux yields a 3.3σ difference, evidence for a non-electron-flavour active component in the solar 8B flux; total active flux 5.44±0.99 × 10^6 cm^-2 s^-1, consistent with solar models.
  - new: Charged-current 8B solar-neutrino flux measured at SNO, φ^CC(νe) = 1.75 ± 0.07 (stat) +0.12/−0.11 (sys) ± 0.05(theor) × 10⁶ cm⁻² s⁻¹; comparison to Super-Kamiokande's elastic-scattering flux yields a 3.3σ difference, evidence for a non-electron-flavour active component in the solar 8B flux; total active flux 5.44±0.99 × 10⁶ cm⁻² s⁻¹, consistent with solar models.

### data/atlas/results/sno-nc-evidence-2002.json

- `/key_value_text/value` (key_value_text.value)
  - old: Non-electron flux 3.41 ×10^6 cm^-2 s^-1, 5.3σ > 0; total NC flux 5.09 ×10^6 cm^-2 s^-1
  - new: Non-electron flux 3.41 ×10⁶ cm⁻² s⁻¹, 5.3σ > 0; total NC flux 5.09 ×10⁶ cm⁻² s⁻¹
- `/summary/technical` (summary.technical)
  - old: Observations of neutral-current (NC) interactions on deuterium. Using the NC, elastic-scattering and charged-current reactions and assuming the standard 8B shape (5 MeV kinetic-energy threshold), the electron-neutrino component of the 8B flux is 1.76±0.05(stat)±0.09(syst) ×10^6 cm^-2 s^-1 and the non-electron-neutrino component is 3.41±0.45(stat)+0.48/-0.45(syst) ×10^6 cm^-2 s^-1, 5.3 standard deviations above zero; the total flux measured with the NC reaction, 5.09 (+0.44/-0.43 stat, +0.46/-0.43 syst) ×10^6 cm^-2 s^-1, is consistent with solar models.
  - new: Observations of neutral-current (NC) interactions on deuterium. Using the NC, elastic-scattering and charged-current reactions and assuming the standard 8B shape (5 MeV kinetic-energy threshold), the electron-neutrino component of the 8B flux is 1.76±0.05(stat)±0.09(syst) ×10⁶ cm⁻² s⁻¹ and the non-electron-neutrino component is 3.41±0.45(stat)+0.48/−0.45(syst) ×10⁶ cm⁻² s⁻¹, 5.3 standard deviations above zero; the total flux measured with the NC reaction, 5.09 (+0.44/−0.43 stat, +0.46/−0.43 syst) ×10⁶ cm⁻² s⁻¹, is consistent with solar models.

### data/atlas/results/t2k-cp-violation-constraint-2020.json

- `/summary/plain` (summary.plain)
  - old: T2K compared how often neutrinos and antineutrinos change type on their way across Japan and found a difference that excludes, at 3-sigma confidence, the CP-conserving value δCP = 0. The collaboration words it carefully as 'an indication of CP violation' — not yet a discovery.
  - new: T2K compared how often neutrinos and antineutrinos change type on their way across Japan and found a difference that excludes, at 3σ confidence, the CP-conserving value δCP = 0. The collaboration words it carefully as 'an indication of CP violation' — not yet a discovery.

### data/atlas/results/ua1-w-boson-observation-1983.json

- `/key_value/display` (key_value.display)
  - old: ~80 GeV/c^2
  - new: ~80 GeV/c²
- `/key_value_text/value` (key_value_text.value)
  - old: Six candidate W events (presented by UA1 at a CERN seminar on 20 January 1983) with an isolated high-transverse-energy electron and missing transverse energy, read as p-pbar -> W(+/-) + X, W(+/-) -> e(+/-) + nu
  - new: Six candidate W events (presented by UA1 at a CERN seminar on 20 January 1983) with an isolated high-transverse-energy electron and missing transverse energy, read as p-p̄ → W± + X, W± → e± + ν
- `/summary/technical` (summary.technical)
  - old: UA1 Collaboration, Phys. Lett. B 122 (1983) 103-116: isolated high-transverse-energy electrons with missing transverse energy at sqrt(s) = 540 GeV, with the signature of a two-body decay of a particle of mass ~80 GeV/c^2 and read as p-pbar -> W(+/-) + X, W -> e + nu. Six candidate events were presented by C. Rubbia at a CERN seminar on 20 January 1983; the discovery was announced at a CERN press conference on 25 January 1983.
  - new: UA1 Collaboration, Phys. Lett. B 122 (1983) 103-116: isolated high-transverse-energy electrons with missing transverse energy at √s = 540 GeV, with the signature of a two-body decay of a particle of mass ~80 GeV/c² and read as p-p̄ → W± + X, W → e + ν. Six candidate events were presented by C. Rubbia at a CERN seminar on 20 January 1983; the discovery was announced at a CERN press conference on 25 January 1983.

### data/atlas/results/ua1-z-boson-observation-1983.json

- `/key_value/display` (key_value.display)
  - old: ~95 GeV/c^2
  - new: ~95 GeV/c²
- `/key_value_text/value` (key_value_text.value)
  - old: Four electron-positron pairs and one muon pair with the signature of a two-body decay of a particle of mass ~95 GeV/c^2, read as p-pbar -> Z0 + X, Z0 -> l+ l-
  - new: Four electron-positron pairs and one muon pair with the signature of a two-body decay of a particle of mass ~95 GeV/c², read as p-p̄ → Z⁰ + X, Z⁰ → l⁺ l⁻
- `/summary/technical` (summary.technical)
  - old: UA1 Collaboration, Phys. Lett. B 126 (1983) 398: four e+e- pairs and one mu+mu- pair with the signature of a two-body decay of a particle of mass ~95 GeV/c^2; the events fit well the hypothesis p-pbar -> Z0 + X with Z0 -> l+ l-, where Z0 is the Intermediate Vector Boson postulated by the electroweak theories as the mediator of weak neutral currents.
  - new: UA1 Collaboration, Phys. Lett. B 126 (1983) 398: four e⁺e⁻ pairs and one μ⁺μ⁻ pair with the signature of a two-body decay of a particle of mass ~95 GeV/c²; the events fit well the hypothesis p-p̄ → Z⁰ + X with Z⁰ → l⁺ l⁻, where Z⁰ is the Intermediate Vector Boson postulated by the electroweak theories as the mediator of weak neutral currents.
- `/why_it_matters` (why_it_matters)
  - old: The paper identifies the Z0 as the Intermediate Vector Boson postulated by the electroweak theories as the mediator of weak neutral currents, and CERN announced the discovery of the Z boson on 1 June 1983, after the W announcement of 25 January 1983.
  - new: The paper identifies the Z⁰ as the Intermediate Vector Boson postulated by the electroweak theories as the mediator of weak neutral currents, and CERN announced the discovery of the Z boson on 1 June 1983, after the W announcement of 25 January 1983.

### data/atlas/results/ua2-w-boson-observation-1983.json

- `/key_value_text/value` (key_value_text.value)
  - old: Four candidate events with an isolated high-transverse-momentum electron (above 15 GeV) and large missing transverse energy opposite in azimuth, consistent with p-pbar -> W(+/-) + anything, W -> e + nu
  - new: Four candidate events with an isolated high-transverse-momentum electron (above 15 GeV) and large missing transverse energy opposite in azimuth, consistent with p-p̄ → W± + anything, W → e + ν
- `/summary/technical` (summary.technical)
  - old: UA2 Collaboration, Phys. Lett. B 122 (1983) 476-485: four candidate events with a single isolated high-p_T electron and missing transverse energy, consistent with p-pbar -> W(+/-) + anything, W -> e + nu. The result was presented by Luigi Di Lella at a CERN seminar (22 January 1983 per CERN's UA2 page; 'the following afternoon' after UA1's 20 January seminar per CERN's 2013 article), before the CERN announcement of the W discovery on 25 January 1983.
  - new: UA2 Collaboration, Phys. Lett. B 122 (1983) 476-485: four candidate events with a single isolated high-p_T electron and missing transverse energy, consistent with p-p̄ → W± + anything, W → e + ν. The result was presented by Luigi Di Lella at a CERN seminar (22 January 1983 per CERN's UA2 page; 'the following afternoon' after UA1's 20 January seminar per CERN's 2013 article), before the CERN announcement of the W discovery on 25 January 1983.

### data/atlas/results/ua2-z-boson-evidence-1983.json

- `/key_value/display` (key_value.display)
  - old: 91.9 +/- 1.3 (stat) +/- 1.4 (syst) GeV/c^2
  - new: 91.9 ± 1.3 (stat) ± 1.4 (syst) GeV/c²
- `/key_value_text/value` (key_value_text.value)
  - old: Eight events interpreted as p-pbar -> Z0 + anything, Z0 -> e+e- (or e+e-γ); four of the eight events are used to measure Mz = 91.9 +/- 1.3 (stat) +/- 1.4 (syst) GeV/c^2
  - new: Eight events interpreted as p-p̄ → Z⁰ + anything, Z⁰ → e⁺e⁻ (or e⁺e⁻γ); four of the eight events are used to measure Mz = 91.9 ± 1.3 (stat) ± 1.4 (syst) GeV/c²
- `/summary/plain` (summary.plain)
  - old: UA2 reported the observation of eight events interpreted as the Z0 boson decaying into an electron and a positron (sometimes with a photon). Four of them gave a Z mass of 91.9 ± 1.3 (stat) ± 1.4 (syst) GeV/c². The paper's title says 'Evidence for Z0 → e+e−'.
  - new: UA2 reported the observation of eight events interpreted as the Z⁰ boson decaying into an electron and a positron (sometimes with a photon). Four of them gave a Z mass of 91.9 ± 1.3 (stat) ± 1.4 (syst) GeV/c². The paper's title says 'Evidence for Z0 → e+e−'.
- `/summary/technical` (summary.technical)
  - old: UA2 Collaboration, Phys. Lett. B 129 (1983) 130: from a search for electron pairs in p-pbar collisions at sqrt(s) = 550 GeV, eight events interpreted as p-pbar -> Z0 + anything with Z0 -> e+e- or e+e-γ, where Z0 is the neutral Intermediate Vector Boson postulated by the unified electroweak theory; four of the events are used to measure Mz = 91.9 ± 1.3 (stat) ± 1.4 (syst) GeV/c². Received 11 August 1983; issue dated 15 September 1983.
  - new: UA2 Collaboration, Phys. Lett. B 129 (1983) 130: from a search for electron pairs in p-p̄ collisions at √s = 550 GeV, eight events interpreted as p-p̄ → Z⁰ + anything with Z⁰ → e⁺e⁻ or e⁺e⁻γ, where Z⁰ is the neutral Intermediate Vector Boson postulated by the unified electroweak theory; four of the events are used to measure Mz = 91.9 ± 1.3 (stat) ± 1.4 (syst) GeV/c². Received 11 August 1983; issue dated 15 September 1983.
- `/why_it_matters` (why_it_matters)
  - old: A second CERN collider experiment's measurement of the Z0 mass from four of its eight Z0 → e+e− candidate events, 91.9 ± 1.3 (stat) ± 1.4 (syst) GeV/c², published in the same year as UA1's Z paper.
  - new: A second CERN collider experiment's measurement of the Z⁰ mass from four of its eight Z⁰ → e⁺e⁻ candidate events, 91.9 ± 1.3 (stat) ± 1.4 (syst) GeV/c², published in the same year as UA1's Z paper.

### data/atlas/results/xenonnt-b8-cevns-indication-2024.json

- `/key_value_text/value` (key_value_text.value)
  - old: Measured 8B solar-neutrino flux of (4.7+3.6-2.3)e6 cm^-2 s^-1, consistent with results from the Sudbury Neutrino Observatory (SNO).
  - new: Measured 8B solar-neutrino flux of (4.7+3.6−2.3) × 10⁶ cm⁻² s⁻¹, consistent with results from the Sudbury Neutrino Observatory (SNO).
- `/notes/0` (notes[])
  - old: result_type is "measurement", not "first_detection", "evidence" or "observation": the collaboration's own title says "First Indication" and the paper reports only a 2.73 sigma rejection of the background-only hypothesis, below the 99.73% (3σ) confidence level that the T2K Nature paper (arXiv:1910.03887) describes as "considered as evidence in the particle physics community". The ontology's result_type enum has no "indication" tier; per the precedent already set in this atlas for an identical situation (result:t2k-electron-neutrino-indication-2011, a 2.5 sigma "indication" paper), the honest choice is "measurement", not the unconstrained "first_detection" type -- "first_detection" reads as an actual detection to a reader and is reserved elsewhere in this atlas (icecube-glashow-resonance-candidate-2021, kamiokande-sn1987a-1987) for events that were actually detected, not a sub-evidence-threshold statistical indication. Corrected during wave-3 independent verification (2026-09-17); the original record mislabeled this as first_detection.
  - new: result_type is "measurement", not "first_detection", "evidence" or "observation": the collaboration's own title says "First Indication" and the paper reports only a 2.73σ rejection of the background-only hypothesis, below the 99.73% (3σ) confidence level that the T2K Nature paper (arXiv:1910.03887) describes as "considered as evidence in the particle physics community". The ontology's result_type enum has no "indication" tier; per the precedent already set in this atlas for an identical situation (result:t2k-electron-neutrino-indication-2011, a 2.5σ "indication" paper), the honest choice is "measurement", not the unconstrained "first_detection" type -- "first_detection" reads as an actual detection to a reader and is reserved elsewhere in this atlas (icecube-glashow-resonance-candidate-2021, kamiokande-sn1987a-1987) for events that were actually detected, not a sub-evidence-threshold statistical indication. Corrected during wave-3 independent verification (2026-09-17); the original record mislabeled this as first_detection.

### data/atlas/results/xenonnt-first-nr-search-2023.json

- `/key_value/display` (key_value.display)
  - old: 2.58e-47 cm^2
  - new: 2.58 × 10⁻⁴⁷ cm²
- `/key_value/note` (provenance note)
  - old: Spin-independent WIMP-nucleon cross-section limit at 90% CL, WIMP mass 28 GeV/c^2.
  - new: Spin-independent WIMP-nucleon cross-section limit at 90% CL, WIMP mass 28 GeV/c².

### data/atlas/sites/cjpl-ii.json

- `/summary/technical` (summary.technical)
  - old: CJPL-II: a second-phase extension of CJPL, ~500 m west of CJPL-I along the same traffic tunnel, with four planned caverns (14 m x 14 m x 130 m each) and ~2100 m (2100 m.w.e.) rock overburden; civil engineering credited elsewhere to Tsinghua University and Yalong River Hydropower Development Company (not independently confirmed on an official page in this session).
  - new: CJPL-II: a second-phase extension of CJPL, ~500 m west of CJPL-I along the same traffic tunnel, with four planned caverns (14 m × 14 m × 130 m each) and ~2100 m (2100 m.w.e.) rock overburden; civil engineering credited elsewhere to Tsinghua University and Yalong River Hydropower Development Company (not independently confirmed on an official page in this session).

### data/atlas/sites/fermilab-main-campus.json

- `/coordinates/note` (provenance note)
  - old: This site is used as the placement for several Fermilab short-baseline and long-baseline near detectors (DUNE near detector, ICARUS, SBND, MicroBooNE, MiniBooNE, MINOS near detector, NOvA near detector, MINERvA), none of which has its own dedicated site record. `kind` is set to `detector` only because A17/the validator requires that for any site holding a detector placement; the coordinate itself is the OpenStreetMap/Nominatim polygon centroid for the whole ~27 km^2 Fermilab campus, not a surveyed position for any one detector hall. Real effort (LBNF/DUNE's own 'excavations and structures' page, its FAQ, and the Fermilab design reports) did not turn up published lat/lon for the near detector hall itself, only that it sits near Kirk Road and Giese Road on site and 60 m underground. Treat every placement at this site as campus-precision, not detector-hall precision. No coordinate is published on a Fermilab page that could be fetched directly (fnal.gov returned HTTP 403); the LBNF/DUNE site confirms the Batavia, Illinois location only.
  - new: This site is used as the placement for several Fermilab short-baseline and long-baseline near detectors (DUNE near detector, ICARUS, SBND, MicroBooNE, MiniBooNE, MINOS near detector, NOvA near detector, MINERvA), none of which has its own dedicated site record. `kind` is set to `detector` only because A17/the validator requires that for any site holding a detector placement; the coordinate itself is the OpenStreetMap/Nominatim polygon centroid for the whole ~27 km² Fermilab campus, not a surveyed position for any one detector hall. Real effort (LBNF/DUNE's own 'excavations and structures' page, its FAQ, and the Fermilab design reports) did not turn up published lat/lon for the near detector hall itself, only that it sits near Kirk Road and Giese Road on site and 60 m underground. Treat every placement at this site as campus-precision, not detector-hall precision. No coordinate is published on a Fermilab page that could be fetched directly (fnal.gov returned HTTP 403); the LBNF/DUNE site confirms the Batavia, Illinois location only.

### data/atlas/sites/grandproto300-dunhuang.json

- `/coordinates/note` (provenance note)
  - old: The collaboration papers place GRANDProto300 qualitatively (ICRC 2025: XiaoDuShan site in Dunhuang, a 2.5-hour drive from the city; JINST, arXiv:2509.21306: the 300-antenna stage will span about 200 km2 in the Gobi Desert near Xiaodushan, in northern Dunhuang, China) but give no numeric coordinates. This point is Dunhuang city itself (Wikipedia infobox, rank 12: 40°08′28″N 94°39′50″E = 40.14111, 94.66389), used only as the nearest real, named reference point; the 65-antenna array (GP300_s65, about 30 km2 per the JINST paper) lies somewhere in the Gobi Desert north of the city, not at this exact point. kind is campus with confidence uncertain, per A23, because this is a city-level regional pointer, not a surveyed array position.
  - new: The collaboration papers place GRANDProto300 qualitatively (ICRC 2025: XiaoDuShan site in Dunhuang, a 2.5-hour drive from the city; JINST, arXiv:2509.21306: the 300-antenna stage will span about 200 km² in the Gobi Desert near Xiaodushan, in northern Dunhuang, China) but give no numeric coordinates. This point is Dunhuang city itself (Wikipedia infobox, rank 12: 40°08′28″N 94°39′50″E = 40.14111, 94.66389), used only as the nearest real, named reference point; the 65-antenna array (GP300_s65, about 30 km² per the JINST paper) lies somewhere in the Gobi Desert north of the city, not at this exact point. kind is campus with confidence uncertain, per A23, because this is a city-level regional pointer, not a surveyed array position.

### data/atlas/sites/juno-jiangmen-underground-lab.json

- `/depth_mwe/note` (provenance note)
  - old: Added 2026-09-18, closing a previously missing field. Consistent with the 700 m granite-rock depth already on file (granite density ~2.6 g/cm^3 implies ~1800 m.w.e.).
  - new: Added 2026-09-18, closing a previously missing field. Consistent with the 700 m granite-rock depth already on file (granite density ~2.6 g/cm³ implies ~1800 m.w.e.).
- `/notes/0` (notes[])
  - old: The underground experimental hall itself is reported as 'spanning more than 50 meters' (CDR) with a total civil-construction volume around 300,000 m^3 and a main hall of about 120,000 m^3 (per a secondary IHEP-related search summary, not independently verified against a fetched primary source in this session).
  - new: The underground experimental hall itself is reported as 'spanning more than 50 meters' (CDR) with a total civil-construction volume around 300,000 m³ and a main hall of about 120,000 m³ (per a secondary IHEP-related search summary, not independently verified against a fetched primary source in this session).

### data/atlas/sites/lngs-hall-a.json

- `/summary/technical` (summary.technical)
  - old: Underground experimental hall of LNGS, about 100 x 20 x 18 m under ~1400 m of rock, one of the laboratory's three main halls (A, B, C).
  - new: Underground experimental hall of LNGS, about 100 × 20 × 18 m under ~1400 m of rock, one of the laboratory's three main halls (A, B, C).

### data/atlas/sites/lngs-hall-b.json

- `/summary/technical` (summary.technical)
  - old: Underground experimental hall of LNGS, about 100 x 20 x 18 m under ~1400 m of rock; the ICARUS T600 plant occupied a 15 x 42.5 m area at the northern end from 2010 to 2013.
  - new: Underground experimental hall of LNGS, about 100 × 20 × 18 m under ~1400 m of rock; the ICARUS T600 plant occupied a 15 × 42.5 m area at the northern end from 2010 to 2013.

### data/atlas/sites/lngs-hall-c.json

- `/summary/technical` (summary.technical)
  - old: Underground experimental hall of LNGS, about 100 x 20 x 18 m under ~1400 m of rock, one of the laboratory's three main halls (A, B, C).
  - new: Underground experimental hall of LNGS, about 100 × 20 × 18 m under ~1400 m of rock, one of the laboratory's three main halls (A, B, C).

### data/atlas/sites/malargue-auger.json

- `/coordinates/note` (provenance note)
  - old: Coordinates are a geocode of the Observatory's own stated headquarters address (Av. San Martin Norte 304, Malargue), not a survey point for the 3000 km^2 surface-detector array itself, which is centred roughly 30 km away and extends around this campus/administrative point. No fetched official or technical source gives decimal coordinates for the array's own geometric centre.
  - new: Coordinates are a geocode of the Observatory's own stated headquarters address (Av. San Martin Norte 304, Malargue), not a survey point for the 3000 km² surface-detector array itself, which is centred roughly 30 km away and extends around this campus/administrative point. No fetched official or technical source gives decimal coordinates for the array's own geometric centre.
- `/notes/1` (notes[])
  - old: The array is 'extended': individual surface-detector stations and fluorescence buildings are spread across ~3000 km^2 around this point; no attempt was made in this wave to record every station's own coordinates.
  - new: The array is 'extended': individual surface-detector stations and fluorescence buildings are spread across ~3000 km² around this point; no attempt was made in this wave to record every station's own coordinates.
- `/summary/technical` (summary.technical)
  - old: Headquarters/campus site of the Pierre Auger Observatory in Malargue, Mendoza Province, Argentina; the 3000 km^2 surface-detector array and fluorescence buildings extend around this administrative point at an average altitude reported elsewhere as roughly 1400 m (not sourced in this session).
  - new: Headquarters/campus site of the Pierre Auger Observatory in Malargue, Mendoza Province, Argentina; the 3000 km² surface-detector array and fluorescence buildings extend around this administrative point at an average altitude reported elsewhere as roughly 1400 m (not sourced in this session).

### data/atlas/sites/surf-davis-campus-lz.json

- `/summary/technical` (summary.technical)
  - old: Davis Campus on the 4850 Level of SURF (former Homestake mine), ~1480 m of rock, ~4300 m.w.e. overburden. The enlarged Davis Cavern hosted LUX and now hosts LZ inside the 8 m x 6 m water shield; opened to science 30 May 2012.
  - new: Davis Campus on the 4850 Level of SURF (former Homestake mine), ~1480 m of rock, ~4300 m.w.e. overburden. The enlarged Davis Cavern hosted LUX and now hosts LZ inside the 8 m × 6 m water shield; opened to science 30 May 2012.

### data/atlas/sites/telescope-array-utah-central-site.json

- `/summary/technical` (summary.technical)
  - old: Approximate central/campus point (Delta, Utah, Millard County) for the Telescope Array observatory, at about 1400 m altitude; the actual detector footprint (507 scintillation counters over ~700 km^2, extended to ~3000 km^2 by TAx4, plus fluorescence stations at Middle Drum, Long Ridge and Black Rock Mesa) is spread around this point.
  - new: Approximate central/campus point (Delta, Utah, Millard County) for the Telescope Array observatory, at about 1400 m altitude; the actual detector footprint (507 scintillation counters over ~700 km², extended to ~3000 km² by TAx4, plus fluorescence stations at Middle Drum, Long Ridge and Black Rock Mesa) is spread around this point.

### data/atlas/sites/wipp-surface-campus.json

- `/depth_mwe/note` (provenance note)
  - old: Verification fix (2026-09-17): this agent directly fetched the EXO-200 detector design paper, which gives this figure; a later EXO-200 paper (Searches for Double Beta Decay of 134Xe with EXO-200) instead reports ~1624 (+22/-21) m.w.e. for the underground clean room, a later re-estimate not independently re-verified against a directly fetched primary source in this session. The construction paper's 1585 m.w.e. figure is recorded here as the directly sourced value; the discrepancy with the later 1624 m.w.e. figure is noted for a future pass.
  - new: Verification fix (2026-09-17): this agent directly fetched the EXO-200 detector design paper, which gives this figure; a later EXO-200 paper (Searches for Double Beta Decay of 134Xe with EXO-200) instead reports ~1624 (+22/−21) m.w.e. for the underground clean room, a later re-estimate not independently re-verified against a directly fetched primary source in this session. The construction paper's 1585 m.w.e. figure is recorded here as the directly sourced value; the discrepancy with the later 1624 m.w.e. figure is noted for a future pass.
- `/notes/1` (notes[])
  - old: Verification fix (2026-09-17, src:0vbb-verify-*): `depth_mwe` was previously left null because this agent had not directly fetched an EXO-200 paper stating the m.w.e. figure. Independent verification directly fetched the EXO-200 detector design paper (arXiv:1202.2192), which states 1585 m water equivalent; that value is now recorded. A later EXO-200 paper reports ~1624 (+22/-21) m.w.e. instead (a subsequent re-estimate), which was not independently re-verified against a directly fetched primary source in this pass; see `depth_mwe.note`.
  - new: Verification fix (2026-09-17, src:0vbb-verify-*): `depth_mwe` was previously left null because this agent had not directly fetched an EXO-200 paper stating the m.w.e. figure. Independent verification directly fetched the EXO-200 detector design paper (arXiv:1202.2192), which states 1585 m water equivalent; that value is now recorded. A later EXO-200 paper reports ~1624 (+22/−21) m.w.e. instead (a subsequent re-estimate), which was not independently re-verified against a directly fetched primary source in this pass; see `depth_mwe.note`.

### data/atlas/topics/topics.json

- `/4/overview` (topic text)
  - old: This area covers searches for extremely rare processes and for tiny deviations from the Standard Model, studied with intense sources and high-precision detectors. Quantum corrections from hypothetical heavy or feebly interacting states shift observables such as the muon anomalous magnetic moment, electric dipole moments and rare-decay rates, so measurements at the part-per-billion or 10^-13 branching-fraction level probe mass scales far above collider energies. The same facilities search directly for light, long-lived or feebly coupled states - heavy neutral leptons, dark photons and other long-lived particles - at beam dumps, fixed-target experiments and the forward regions of colliders.
  - new: This area covers searches for extremely rare processes and for tiny deviations from the Standard Model, studied with intense sources and high-precision detectors. Quantum corrections from hypothetical heavy or feebly interacting states shift observables such as the muon anomalous magnetic moment, electric dipole moments and rare-decay rates, so measurements at the part-per-billion or 10⁻¹³ branching-fraction level probe mass scales far above collider energies. The same facilities search directly for light, long-lived or feebly coupled states - heavy neutral leptons, dark photons and other long-lived particles - at beam dumps, fixed-target experiments and the forward regions of colliders.
- `/10/overview` (topic text)
  - old: The top quark is the weak-isospin partner of the bottom quark, with a mass of about 172.5 GeV and therefore a Yukawa coupling of order unity. Being heavier than the W boson it is the only quark that decays weakly into a real W and a b quark, and its lifetime is shorter than the timescale of non-perturbative strong interactions, so it does not hadronize and its spin information survives into its decay products. Abundant LHC production enables precise measurements of the mass, couplings, production cross sections and branching ratios; the Particle Data Group notes a 1.7-sigma tension between the top-quark mass inferred indirectly from the electroweak fit and the value combined directly from LHC measurements.
  - new: The top quark is the weak-isospin partner of the bottom quark, with a mass of about 172.5 GeV and therefore a Yukawa coupling of order unity. Being heavier than the W boson it is the only quark that decays weakly into a real W and a b quark, and its lifetime is shorter than the timescale of non-perturbative strong interactions, so it does not hadronize and its spin information survives into its decay products. Abundant LHC production enables precise measurements of the mass, couplings, production cross sections and branching ratios; the Particle Data Group notes a 1.7σ tension between the top-quark mass inferred indirectly from the electroweak fit and the value combined directly from LHC measurements.
- `/13/observables/1` (topic text)
  - old: unitarity-triangle angles alpha, beta and gamma
  - new: unitarity-triangle angles α, β and γ
- `/13/observables/2` (topic text)
  - old: time-dependent CP asymmetries such as sin 2beta from B to J/psi K_S
  - new: time-dependent CP asymmetries such as sin 2β from B to J/ψ K_S
- `/14/observables/1` (topic text)
  - old: B0 and Bs mixing frequencies
  - new: B⁰ and Bs mixing frequencies
- `/14/observables/7` (topic text)
  - old: Bs and B0 dimuon branching fractions
  - new: Bs and B⁰ dimuon branching fractions
- `/15/observables/0` (topic text)
  - old: branching fraction of K+ to pi+ neutrino antineutrino
  - new: branching fraction of K⁺ to π⁺ neutrino antineutrino
- `/15/observables/1` (topic text)
  - old: branching fraction or limit for K_L to pi0 neutrino antineutrino
  - new: branching fraction or limit for K_L to π⁰ neutrino antineutrino
- `/15/observables/2` (topic text)
  - old: K_L to pi0 charged-lepton-pair and K_S to dimuon branching fractions
  - new: K_L to π⁰ charged-lepton-pair and K_S to dimuon branching fractions
- `/15/observables/4` (topic text)
  - old: direct CP violation parameter in K to pi pi
  - new: direct CP violation parameter in K to ππ
- `/15/observables/7` (topic text)
  - old: searches for K to pi plus an invisible particle
  - new: searches for K to π plus an invisible particle
- `/15/overview` (topic text)
  - old: Rare kaon decays divide into searches for explicit Standard Model violations, the golden modes, other constraints on Standard Model parameters, and studies of low-energy strong interactions. The golden modes K+ to pi+ neutrino antineutrino and K_L to pi0 neutrino antineutrino are dominated by short-distance physics and calculable with negligible theoretical uncertainty. NA62 at the CERN SPS reported in 2026, using data through 2024, a branching fraction of 9.6 (+1.9/-1.8) x 10^-11 against a Standard Model estimate of (8.2 +/- 0.6) x 10^-11; KOTO at J-PARC pursues the neutral mode. Lepton-flavor and lepton-number violating kaon decays are also searched for.
  - new: Rare kaon decays divide into searches for explicit Standard Model violations, the golden modes, other constraints on Standard Model parameters, and studies of low-energy strong interactions. The golden modes K⁺ to π⁺ neutrino antineutrino and K_L to π⁰ neutrino antineutrino are dominated by short-distance physics and calculable with negligible theoretical uncertainty. NA62 at the CERN SPS reported in 2026, using data through 2024, a branching fraction of 9.6 (+1.9/−1.8) × 10⁻¹¹ against a Standard Model estimate of (8.2 ± 0.6) × 10⁻¹¹; KOTO at J-PARC pursues the neutral mode. Lepton-flavor and lepton-number violating kaon decays are also searched for.
- `/16/observables/2` (topic text)
  - old: difference of CP asymmetries in D0 to K+K- and D0 to pi+pi-
  - new: difference of CP asymmetries in D⁰ to K⁺K⁻ and D⁰ to π⁺π⁻
- `/16/overview` (topic text)
  - old: Charm hadrons provide the only accessible up-type-quark system in which meson mixing and CP violation can be studied. A meson created as a D0 time-evolves into a D0-bar, and the mixing parameters are measured to be small and positive. CP violation in decay has been established in the difference of asymmetries for D0 to K+K- and D0 to pi+pi-, with the Particle Data Group quoting (-0.159 +/- 0.029) per cent. Interpretation is limited because long-distance contributions are not calculable from first principles. Charm decays also provide decay constants, form factors and precise Vcs and Vcd.
  - new: Charm hadrons provide the only accessible up-type-quark system in which meson mixing and CP violation can be studied. A meson created as a D⁰ time-evolves into a D̄⁰, and the mixing parameters are measured to be small and positive. CP violation in decay has been established in the difference of asymmetries for D⁰ to K⁺K⁻ and D⁰ to π⁺π⁻, with the Particle Data Group quoting (-0.159 ± 0.029) per cent. Interpretation is limited because long-distance contributions are not calculable from first principles. Charm decays also provide decay constants, form factors and precise Vcs and Vcd.
- `/17/observables/2` (topic text)
  - old: the three mixing angles and the octant of theta_23
  - new: the three mixing angles and the octant of θ₂₃
- `/20/observables/5` (topic text)
  - old: solar values of the mixing angle theta_12 and the solar mass-squared difference
  - new: solar values of the mixing angle θ₁₂ and the solar mass-squared difference
- `/22/observables/1` (topic text)
  - old: the reactor mixing angle theta_13
  - new: the reactor mixing angle θ₁₃
- `/26/overview` (topic text)
  - old: Neutrinoless double beta decay is a hypothetical ultra-rare nuclear decay that would violate total lepton number by two units and require neutrinos to be Majorana particles. Under the assumption that Majorana neutrino mass is the only low-energy source of lepton-number violation, the half-life relates to an effective Majorana mass through phase space and nuclear matrix elements, whose uncertainty spreads the inferred mass by a factor of two to three; other new-physics mechanisms could dominate instead. No decay has been seen. The strongest limits come from xenon-136 and germanium-76, exceeding 10^26 years.
  - new: Neutrinoless double beta decay is a hypothetical ultra-rare nuclear decay that would violate total lepton number by two units and require neutrinos to be Majorana particles. Under the assumption that Majorana neutrino mass is the only low-energy source of lepton-number violation, the half-life relates to an effective Majorana mass through phase space and nuclear matrix elements, whose uncertainty spreads the inferred mass by a factor of two to three; other new-physics mechanisms could dominate instead. No decay has been seen. The strongest limits come from xenon-136 and germanium-76, exceeding 10²⁶ years.
- `/27/overview` (topic text)
  - old: In coherent elastic neutrino-nucleus scattering a low-energy neutrino scatters from a nucleus acting as a single particle. The total cross section is large by neutrino standards, but the process eluded detection for four decades because the nuclear recoil deposits only about a keV. COHERENT observed it at 6.7 sigma in 2017 using a 14.6 kg caesium-iodide scintillator at the Oak Ridge Spallation Neutron Source, and derived improved constraints on non-standard neutrino interactions with quarks. The process bears on nuclear structure and astrophysics as well as particle physics, and sets an irreducible neutrino background for dark-matter detectors.
  - new: In coherent elastic neutrino-nucleus scattering a low-energy neutrino scatters from a nucleus acting as a single particle. The total cross section is large by neutrino standards, but the process eluded detection for four decades because the nuclear recoil deposits only about a keV. COHERENT observed it at 6.7σ in 2017 using a 14.6 kg caesium-iodide scintillator at the Oak Ridge Spallation Neutron Source, and derived improved constraints on non-standard neutrino interactions with quarks. The process bears on nuclear structure and astrophysics as well as particle physics, and sets an irreducible neutrino background for dark-matter detectors.
- `/28/overview` (topic text)
  - old: Direct detection looks for nuclear or electron recoils left when Galactic dark matter passes through a low-background detector operated deep underground. Interpretation needs the local dark-matter density and velocity distribution, which are themselves uncertain at the level of a factor of a few. Dual-phase liquid-xenon time projection chambers currently lead for masses around tens of GeV: the Particle Data Group tabulates a spin-independent cross-section limit of 2.2 x 10^-48 cm^2 near 40 GeV from LUX-ZEPLIN, with XENONnT and PandaX-4T close behind. Sensitivity is approaching the irreducible background from coherent neutrino scattering, which those detectors have now begun to observe.
  - new: Direct detection looks for nuclear or electron recoils left when Galactic dark matter passes through a low-background detector operated deep underground. Interpretation needs the local dark-matter density and velocity distribution, which are themselves uncertain at the level of a factor of a few. Dual-phase liquid-xenon time projection chambers currently lead for masses around tens of GeV: the Particle Data Group tabulates a spin-independent cross-section limit of 2.2 × 10⁻⁴⁸ cm² near 40 GeV from LUX-ZEPLIN, with XENONnT and PandaX-4T close behind. Sensitivity is approaching the irreducible background from coherent neutrino scattering, which those detectors have now begun to observe.
- `/36/overview` (topic text)
  - old: Quantum loop effects make the muon magnetic moment deviate slightly from the Dirac value, and the anomaly can be both measured in storage rings and predicted precisely, testing the Standard Model at loop level. After the final Fermilab E989 result the experimental world average is 116 592 071.5(14.5) x 10^-11, against a Standard Model prediction of 116 592 033(62) x 10^-11 compiled by the Muon g-2 Theory Initiative; the difference, 38(63) x 10^-11, is compatible with zero and now dominated by theory uncertainty. A permanent electric dipole moment would directly signal time-reversal and, assuming CPT, CP violation; only upper limits exist.
  - new: Quantum loop effects make the muon magnetic moment deviate slightly from the Dirac value, and the anomaly can be both measured in storage rings and predicted precisely, testing the Standard Model at loop level. After the final Fermilab E989 result the experimental world average is 116 592 071.5(14.5) × 10⁻¹¹, against a Standard Model prediction of 116 592 033(62) × 10⁻¹¹ compiled by the Muon g-2 Theory Initiative; the difference, 38(63) × 10⁻¹¹, is compatible with zero and now dominated by theory uncertainty. A permanent electric dipole moment would directly signal time-reversal and, assuming CPT, CP violation; only upper limits exist.
- `/37/overview` (topic text)
  - old: Cosmic rays are a non-thermal population of particles pervading the universe, characterised by their spectrum, composition and arrival directions. Charged cosmic rays extend from tens of MeV to close to 1 ZeV, with an intensity of about 10^4 per square metre per second per steradian above 1 GeV and a steeply falling power-law spectrum. The striking spectral features are the knee at a few PeV, where the index changes from about 2.7 to about 3, a second knee near 100 PeV, and the ankle at a few EeV; the flux is largely suppressed above a few tens of EeV. Arrival directions are mostly isotropic.
  - new: Cosmic rays are a non-thermal population of particles pervading the universe, characterised by their spectrum, composition and arrival directions. Charged cosmic rays extend from tens of MeV to close to 1 ZeV, with an intensity of about 10⁴ per square metre per second per steradian above 1 GeV and a steeply falling power-law spectrum. The striking spectral features are the knee at a few PeV, where the index changes from about 2.7 to about 3, a second knee near 100 PeV, and the ankle at a few EeV; the flux is largely suppressed above a few tens of EeV. Arrival directions are mostly isotropic.

## Appendix: the rules

### Field allow-list (`common.py`)

```python
import json, os, re
ROOT='data/atlas'
SKIP_DIRS={'sources','geometry','maps','coverage','memberships'}
# Allow-list of display-string pointers (JSON-pointer with numeric indexes).
ALLOW=[
 r'^/name$', r'^/\d+/name$',
 r'^/summary/(plain|technical)$',
 r'^/why_it_matters$',
 r'^/significance(/value|/display)?$',
 r'^/key_value/display$', r'^/key_value_text/value$',
 r'^/key_specs/\d+/label$', r'^/key_specs/\d+/quantity/display$',
 r'^/(specs|intervals/\d+/specs)/[^/]+/display$',
 r'^/baselines/\d+/distance/display$',
 r'^/(depth|depth_mwe|overburden|altitude)/display$',
 r'^/(physics_goals|unique_capabilities)/(\d+/value|value(/\d+)?)$',
 r'^/energy_regime/value$', r'^/technology/value$',
 r'^/subsystems/\d+/(name|value|description/value|description/\d+/value)$',
 r'^/(specs|intervals/\d+/specs)/[^/]+/value$',
 r'^/(primary_beam|secondary_beam|target|direction)/value$',
 r'^/\d+/(overview|question)$', r'^/\d+/observables/\d+$',
 r'^/notes/\d+$',
 r'^/intervals/\d+/label$',
 r'^.*/note$',
]
ALLOW_RE=[re.compile(p) for p in ALLOW]
def allowed(ptr): return any(r.match(ptr) for r in ALLOW_RE)
```

### Rule list (`rules.py`)

```python
"""Notation rules for HEP Atlas display strings (ASCII physics notation -> Unicode).

Reviewable on purpose: an explicit ordered rule list, an explicit allow-list of
display fields (in common.py), protected spans that are never touched, and a
phrase table for the ambiguous cases (D0 meson vs the D0 experiment, "tau" the
particle vs "tau neutrino" the prose, ...).
"""
import re

SUPMAP = {**{str(i): c for i, c in enumerate('⁰¹²³⁴⁵⁶⁷⁸⁹')}, '-': '⁻', '+': '⁺'}
SUBMAP = {str(i): c for i, c in enumerate('₀₁₂₃₄₅₆₇₈₉')}
SUPCH = '⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺'
BAR = '̄'  # combining macron


def sup(s: str) -> str:
    return ''.join(SUPMAP[c] for c in s)


def subs(s: str) -> str:
    return ''.join(SUBMAP[c] for c in s)


# ---------------------------------------------------------------------------
# Protected spans: never rewritten.
# ---------------------------------------------------------------------------
PROTECT = re.compile('|'.join([
    r'\b(?:src|result|experiment|detector|site|facility|collaboration|accelerator|beamline|document|institution|person|map|geometry|topic):[\w.:/-]+',
    r'`[^`\n]*`',
    r'https?://\S+',
    r'(?<![\w])\'[^\'\n]{8,}?\'(?![\w])',          # 'quoted text' (source titles, field names)
    r'(?<![\w])"[^"\n]{8,}?"(?![\w])',             # "quoted text"
    r'“[^”\n]+”',
    r'(?<![\w])‘[^’\n]+’(?![\w])',
]))


def segments(text):
    """Yield (is_protected, chunk)."""
    pos = 0
    for m in PROTECT.finditer(text):
        if m.start() > pos:
            yield False, text[pos:m.start()]
        yield True, m.group(0)
        pos = m.end()
    if pos < len(text):
        yield False, text[pos:]


# ---------------------------------------------------------------------------
# Rules.  Each is (name, compiled pattern, replacement-callable-or-string, scope)
# scope: 'all' = every allowed field; 'display' = not in notes / note fields.
# ---------------------------------------------------------------------------
RULES = []


def rule(name, pattern, repl, scope='all', flags=0):
    RULES.append((name, re.compile(pattern, flags), repl, scope))


# --- plus/minus and asymmetric uncertainties ------------------------------
rule('pm-charge-sign', r'(?<![A-Za-z])(W|e|l|H)\(\+/-\)', r'\1±')
rule('asym-err-slash', r'\+(\d[\d.,]*)(\s?)/(\s?)-(\d)', r'+\1\2/\3−\4')
rule('asym-err-compact', r'(?<=[\d)])(\s?)\+(\d+\.\d+)-(\d+\.\d+)', r'\1+\2−\3')
rule('plus-minus-slash', r'\+/-', '±')
rule('plus-minus-dash', r'(?<=[\s\d)])\+-(?=[\s\d(])', '±')

# --- sin^2 forms (ASCII caret only; already-Unicode sin²(2θ) is left alone) ----------------
rule('sin2-2theta', r'sin\^2\(2theta_(\d+)\)', lambda m: 'sin²2θ' + subs(m.group(1)))
rule('sin2-2theta-bare', r'sin\^2\(2θ(̄?)\)', lambda m: 'sin²2θ' + m.group(1))
rule('sin2-theta-W', r'sin\^2\((?:theta_W|θ_W)\)', 'sin²θW')

# --- exponents -------------------------------------------------------------
rule('exp-braces', r'\^\{([-+]?\d+)\}', lambda m: sup(m.group(1)))
rule('exp', r'\^([-+]?\d+)', lambda m: sup(m.group(1)))

# --- e-notation (1e34 -> 10^34, 2.336e6 -> 2.336 x 10^6) -----------------------
def _enot(m):
    mant, exp = m.group(1), m.group(2)
    exp = exp.lstrip('+')
    if mant in ('1', '1.0'):
        return '10' + sup(exp)
    return f'{mant} × 10' + sup(exp)


rule('e-notation', r'(?<![\w.])(\d+(?:\.\d+)?)e([-+]?\d+)(?![\w.])', _enot)
rule('e-notation-paren', r'(?<=\))e([-+]?\d+)(?![\w.])', lambda m: ' × 10' + sup(m.group(1).lstrip('+')))

# --- multiplication ---------------------------------------------------------
rule('asym-after-power', r'(?<=[⁰¹²³⁴⁵⁶⁷⁸⁹])/-(?=\d)', '/−')
rule('times-power-of-ten', r'(?<=[\d)\]])(\s?)[x*](\s?)(?=10[' + SUPCH + r'])', r'\1×\2')
rule('times-dimensions', r'(?<=\d)( )x( )(?=\d)', r'\1×\2')
rule('times-dimensions-unit', r'(?<=\d cm) x (?=\d)|(?<=\d mm) x (?=\d)|(?<=\d km) x (?=\d)|(?<=\d m) x (?=\d)', ' × ')

# --- square root --------------------------------------------------------------
def _sqrt(m):
    inner = m.group(1).strip()
    inner = re.sub(r'^s_\{?([A-Za-z]+)\}?$', r's\1', inner)
    if re.fullmatch(r'[A-Za-z0-9]+', inner):
        return '√' + inner
    return '√(' + inner + ')'


rule('sqrt', r'sqrt\(([^()]*)\)', _sqrt)

# --- neutrinos ----------------------------------------------------------------
GREEK_FLAV = {'mu': 'μ', 'e': 'e', 'tau': 'τ', 'l': 'l'}
rule('nubar-flavour', r'\bnu_(mu|e|tau|l)[-_]bar\b', lambda m: 'ν' + BAR + GREEK_FLAV[m.group(1)])
rule('nu-flavour', r'\bnu_(mu|e|tau|l)\b', lambda m: 'ν' + GREEK_FLAV[m.group(1)])
rule('nubar', r'(?<![A-Za-z])nubar\b', 'ν' + BAR)

# --- mixing angles and mass splittings ---------------------------------------
rule('theta-subscript-digits', r'(?<![A-Za-z])theta_?(\d+)\b', lambda m: 'θ' + subs(m.group(1)))
rule('theta-W', r'(?<![A-Za-z])theta_W\b', 'θW')
rule('delta-m2', r'\bDelta m²(?:_(\d+))?', lambda m: 'Δm²' + (subs(m.group(1)) if m.group(1) else ''))

# --- significance in sigma ------------------------------------------------------
rule('sigma-after-number', r'(?<=\d)[ -]sigma(?![A-Za-z])', 'σ')

# --- pairs and charges -----------------------------------------------------------
rule('eee-charges', r'(?<![A-Za-z0-9])e\+e\+e-(?![A-Za-z0-9])', 'e⁺e⁺e⁻')
rule('ee-charges', r'(?<![A-Za-z0-9])e\+(\s?)e-(?![A-Za-z0-9])', r'e⁺\1e⁻')


# --- arrows -----------------------------------------------------------------------
rule('arrow-between-numbers', r'(?<=\d) -> (?=\d)', ' → ')
rule('arrow-double-ended', r'<->', '↔', scope='display')
rule('arrow-long', r'(?<=\s)-->(?=\s)', '→', scope='display')
rule('arrow', r'->', '→', scope='display')

# --- particle charges ---------------------------------------------------------------
GREEK_P = {'pi': 'π', 'mu': 'μ'}


def _tok(name, sign):
    return GREEK_P.get(name, name) + ('⁺' if sign == '+' else '⁻')


CHARGED = r'(?:pi|mu|K|e)'
rule('charge-sequence',
     r'(?<![A-Za-z0-9])(?:' + CHARGED + r'[+-]){2,}(?![A-Za-z0-9])',
     lambda m: re.sub(r'(pi|mu|K|e)([+-])', lambda q: _tok(q.group(1), q.group(2)), m.group(0)))
rule('charge-plus', r'(?<![A-Za-z0-9])(pi|mu|K|B|D|l|e|W)\+(?![A-Za-z0-9+])', lambda m: _tok(m.group(1), '+'))
rule('pi0', r'(?<![A-Za-z0-9])pi0(?![A-Za-z0-9])', 'π⁰')
rule('Z0', r'(?<![A-Za-z0-9])Z0(?![A-Za-z0-9])', 'Z⁰')


# --- Greek letters with subscripts that are already half-Unicode ------------------------
rule('nu-greek-underscore', r'(ν̄?)_([μeτl])(?![A-Za-z])', r'\1\2')
rule('theta-greek-digits', r'θ_(\d+)\b', lambda m: 'θ' + subs(m.group(1)))
rule('theta-greek-W', r'θ_W\b', 'θW')
rule('delta-CP', r'(?:δ_CP|delta_CP)\b', 'δCP')

# --- minus signs typed as U+2212 where an exponent was meant --------------------------------
rule('unit-minus-exponent',
     r'\b(fb|pb|nb|ab|mb|cm|mm|km|sr|GeV|MeV|TeV|eV|s)−(\d)(?!\d)',
     lambda m: m.group(1) + '⁻' + sup(m.group(2)))
rule('ten-minus-exponent', r'(?<![\w.])10−(\d+)(?![\w.])', lambda m: '10⁻' + sup(m.group(1)))
rule('ten-minus-exponent-times', r'(?<=×)10−(\d+)(?![\w.])', lambda m: '10⁻' + sup(m.group(1)))

# --- charge signs on Unicode-lepton pairs ------------------------------------------------------
rule('ee-charges-unicode-minus', r'(?<![A-Za-z0-9])e\+e−(?![A-Za-z0-9])', 'e⁺e⁻')
rule('tautau-charges', r'(?<![A-Za-z0-9])([τμ])\+\1−(?![A-Za-z0-9])', lambda m: m.group(1) + '⁺' + m.group(1) + '⁻')

# --- spelled-out Greek / symbols in clear physics contexts (display fields only) -----------------------
rule('upsilon-4S', r'\bUpsilon\((\d)S\)', r'Υ(\1S)')
rule('jpsi', r'\bJ/psi\b', 'J/ψ')
rule('abs-eta', r'\|eta\|', '|η|')
rule('eta-range', r'(?<=< )eta(?= <)', 'η', scope='display')
rule('delta-eta-phi', r'\bDelta\((eta|phi)\)', lambda m: 'Δ' + {'eta': 'η', 'phi': 'φ'}[m.group(1)], scope='display')
rule('epsilon-prime', r"\bRe\(epsilon'/epsilon\)", 'Re(ε′/ε)', scope='display')
rule('epsilon-power', r'\bepsilon([²⁴])', r'ε\1', scope='display')
rule('four-pi', r'\b4-pi\b', '4π', scope='display')
rule('degrees-display', r'(?<=\d) deg\b', '°', scope='display')


# --- unit exponents typed without a caret ----------------------------------------------------
rule('c2-units', r'\b(eV|keV|MeV|GeV|TeV)/c2\b', lambda m: m.group(1) + '/c²')
rule('cm2-after-number', r'(?<=[\d⁰¹²³⁴⁵⁶⁷⁸⁹]) cm2\b', ' cm²')
rule('km2-after-number', r'(?<=[\d⁰¹²³⁴⁵⁶⁷⁸⁹]) km2\b', ' km²')
rule('m3-after-number', r'(?<=\d) m3\b', ' m³')
rule('per-m3', r'(?<=/)m3\b', 'm³')
rule('per-cm3', r'(?<=/)cm3\b', 'cm³')
rule('phi-subscript-digit', r'(?<![A-Za-z])phi_(\d)\b', lambda m: 'φ' + subs(m.group(1)))
rule('a-mu', r'\ba_(?:mu|μ)(?![A-Za-z0-9])', 'aμ')

RULE_NAMES = [r[0] for r in RULES]


def apply_rules(text, scope_is_note, extra_rules=()):
    """Return (new_text, counts) applying RULES to unprotected segments."""
    counts = {}
    out = []
    for protected, chunk in segments(text):
        if protected:
            out.append(chunk)
            continue
        for name, pat, repl, scope in list(RULES) + list(extra_rules):
            if scope == 'display' and scope_is_note:
                continue
            chunk, n = pat.subn(repl, chunk)
            if n:
                counts[name] = counts.get(name, 0) + n
        out.append(chunk)
    return ''.join(out), counts
```

### Phrase table (`phrases.py`)

```python
"""Phrase rules for ambiguous tokens: exact context only (see rules.rule)."""
import re
BAR = '̄'
PHRASE_RULES = []

def phrase(name, pattern, repl, scope='display', literal=True):
    if literal:
        head = r'(?<![A-Za-z0-9])' if re.match(r'[A-Za-z0-9]', pattern[0]) else ''
        tail = r'(?![A-Za-z0-9])' if re.match(r'[A-Za-z0-9]', pattern[-1]) else ''
        pat = re.compile(head + re.escape(pattern) + tail)
    else:
        pat = re.compile(pattern)
    PHRASE_RULES.append((name, pat, repl, scope))

# ---- decays / processes ----------------------------------------------------------------
phrase('nu-nubar', r'\bnu(?= ν̄)', 'ν', literal=False, scope='all')
phrase('e+gamma', 'e+gamma', 'e⁺γ')
phrase('e+ gamma', 'e⁺ gamma', 'e⁺ γ')
phrase('gamma gamma', 'gamma gamma', 'γγ')
phrase('gamma-gamma', 'gamma-gamma', 'γγ')
phrase('tau tau (final states)', 'tau tau and bb final states', 'ττ and bb final states')
phrase('W -> e nu (pm)', 'e± + nu', 'e± + ν')
phrase('W -> e nu', '→ e + nu', '→ e + ν')
phrase('W -> lepton nu', 'lepton nu', 'lepton ν')
phrase('W -> mu nu', 'W → mu nu', 'W → μ ν')
phrase('mu- N -> e- N', 'mu- N → e- N', 'μ⁻ N → e⁻ N')
phrase('l+ l-', 'l⁺ l-', 'l⁺ l⁻')
phrase('B- -> tau- nu_tau-bar', 'B- → tau- ν̄τ', 'B⁻ → τ⁻ ν̄τ')
phrase('B0->D-', 'B0→D-', 'B⁰→D⁻')
phrase('D- (->K', 'D-(→', 'D⁻(→')
phrase('B(B0->D-', 'B(B0→D- ', 'B(B⁰→D⁻ ')
phrase('D0bar', 'D0bar', 'D' + BAR + '⁰')
phrase('D mu nu_mu', 'D mu νμ', 'D μ νμ')
phrase('p-pbar', 'p-pbar', 'p-p' + BAR)
phrase('ppbar', 'ppbar', 'pp' + BAR)
phrase('ttbar', 'ttbar', 'tt' + BAR)
phrase('dbar/ubar', 'dbar/ubar', 'd' + BAR + '/u' + BAR)
phrase('B-Bbar', 'B-Bbar', 'B-B' + BAR)
phrase('B-Bbar (en dash)', 'B–Bbar', 'B–B' + BAR)
phrase('B0-B0bar', 'B0-B0bar', 'B⁰-B' + BAR + '⁰')
phrase('B0 system', 'B0 system', 'B⁰ system')
phrase('K0-K0bar', 'K0-K0bar', 'K⁰-K' + BAR + '⁰')
phrase('B0 and Bs', 'B0 and Bs', 'B⁰ and Bs')
phrase('Bs and B0', 'Bs and B0', 'Bs and B⁰')
phrase('D0 to K', 'D0 to ', 'D⁰ to ')
phrase('D0 -> D0-bar', 'a D0 time-evolves into a D0-bar', 'a D⁰ time-evolves into a D' + BAR + '⁰')
phrase('K to pi pi', 'K to pi pi', 'K to ππ')
phrase('K to pi plus', 'K to pi plus', 'K to π plus')
phrase('alpha beta gamma', 'angles alpha, beta and gamma', 'angles α, β and γ')
phrase('sin 2beta', 'sin 2beta', 'sin 2β')
phrase('Xi_cc++ (name)', 'Xi_cc++', 'Ξcc⁺⁺', scope='all')
phrase('Xi_cc++ unicode', 'Ξcc++', 'Ξcc⁺⁺', scope='all')
phrase('Lambda_c+ K- pi+ pi+', 'Λc+K-π+π+', 'Λc⁺K⁻π⁺π⁺')
phrase('Lambda_b0 -> J/psi K- p', 'Λb0→J/ψK−p', 'Λb⁰→J/ψK⁻p')
phrase('D0->K-K+', 'D0→K−K⁺', 'D⁰→K⁻K⁺')
phrase('D0->pi-pi+', 'D0→π−π+', 'D⁰→π⁻π⁺')
phrase('e-/e+ (hera note)', 'e-/e⁺', 'e⁻/e⁺', scope='all')
phrase('e- x e+ (pep-ii)', '9 GeV e- x 3.1 GeV e⁺', '9 GeV e⁻ × 3.1 GeV e⁺')
phrase('e-p / e+p (zeus)', 'e-p and e+p collisions', 'e⁻p and e⁺p collisions')
phrase('Ga(nu_e,e-)Ge', 'νe,e-)', 'νe,e⁻)')
phrase('nu_e + Cl -> Ar + e- (homestake note)', 'νe + 37Cl -> 37Ar + e-', 'νe + 37Cl → 37Ar + e⁻', scope='all')
phrase('phi0', 'phi0 =', 'φ₀ =')
phrase('spectral index gamma', 'spectral index gamma', 'spectral index γ')
phrase('gamma = 3.00', ', gamma = 3.00', ', γ = 3.00')
phrase('delta_CP near pi/2', 'near pi/2', 'near π/2', scope='all')
phrase('um x um', '15 um x 15 um', '15 μm × 15 μm', scope='all')
phrase('long x 10 m', 'long x 10 m', 'long × 10 m')
phrase('Bs0->mu+mu- (note)', 'Bs0->μ⁺μ⁻', 'Bs⁰→μ⁺μ⁻', scope='all')
phrase('arrays x antennas (note)', 'arrays x 10 000 antennas', 'arrays × 10 000 antennas', scope='all')
phrase('Lambda_c+', 'Λc+', 'Λc⁺')
```

