# Accelerator chains and stage energies (stream M5, owner `accelerator-chains`)

2026-10-26, branch `atlas-m5-energy`. Feeds the "Follow the proton" view (teaching
plan, workstreams 2 and 5): for each laboratory, the real injector chain with
sourced intervals, and a sourced energy at every stage.

## Scope

Laboratories with an injector chain in the Atlas: CERN, Fermilab, J-PARC, BNL, KEK,
SLAC, DESY. For each: the `feeds_accelerator_ids` links (with dates where the
relationship changed), the beamline source field (`beamline.accelerator_id`, a plain
id: it already pointed at the right machine for NuMI, LBNF, BNB, CNGS, J-PARC
neutrino and KEK neutrino), stage energies, and a geometry audit for CERN, Fermilab
and J-PARC. Not touched: SPEAR, PEP, PETRA, DORIS, TRISTAN (colliders stream), the
EIC (hadron stream), experiments.

## Data contract (proposed amendment A27; nothing in `docs/HEP_ATLAS_ONTOLOGY.md` was edited)

* `accelerator.feeds_accelerator_ids[]` entry: an id string, or (A9) an object
  `{id, start?, end?, sources, verified_at, confidence, quote, locator, note}`.
  `start`/`end` are A4 Dates (objects with `approx`, `planned`, `earliest`, `latest`,
  `display` allowed). **No `start`/`end` means "from the later of the two machines'
  first state to the earlier of their last", the A9 default (hull A ∩ hull B).**
  Every link written in this stream carries `sources` and a verbatim `quote`. In
  `atlas.json` an entry with provenance only becomes `{"id": …}`, so the list mixes
  strings and objects; a consumer must accept both. The derived inverse
  `fed_by_accelerator_ids` is a plain id list without intervals.
* `specs.beam_energy`: the highest energy the machine delivers (extraction or design
  energy; per beam for a collider), as before.
* `specs.injection_energy` (**new spec key**, dimension `energy`; one added line in
  `hepgraph/atlas/schema.py`, `SPEC_KEY_DIMENSIONS`): the energy at which the machine
  receives beam from its injector **in its current configuration**. Without the
  whitelist line the validator warns `unknown-spec-key`.
* `intervals[].specs` (A3), with `kind: "phase"`, carry **earlier eras only** (Linac2
  era, 200 MeV Fermilab linac, 181 MeV J-PARC linac, 1.4 GeV Booster, LEP-injector
  SPS, RHIC-injector AGS). Current values stay at the top level. LHC per-run energies
  (`kind: "run"`) were already there. Suggested rule for a view at year Y: take
  `specs` of the covering interval with the latest start that has the key, else the
  top-level value.
* Momenta are stored in GeV with the display written in GeV/c and a note
  (CNGS, North Area, ISR). Range quantities (`min`/`max`) are shown at their midpoint
  in `display` because the validator compares the first number in `display` with the
  midpoint (a range written "0.8 to 1 GeV" warns).

## The chains (for a glance; every number and date has a URL and quote in the table below)

Energies are kinetic unless GeV/c is written. "since" and "until" are link dates.

**CERN** (protons; the lead-ion chain Linac3 → LEIR → PS has no records)

* Linac2 (50 MeV, 1978 to 2018-11-12) → PSB
* Linac4 (160 MeV H⁻, since 2020) → PSB
* PSB: in 160 MeV (50 MeV 1972 to 2018); out 2 GeV (1.4 GeV 1999 to 2018; 0.8 to 1 GeV 1972 to 1999) → PS (since 1972-05-26)
* PS: in 2 GeV (1.4 GeV 1999 to 2018; 0.8 to 1 GeV 1972 to 1999; 50 MeV straight from Linac1 before 1972); out 26 GeV (CERN also writes 25 GeV)
  → SPS (since 1976-06-17); → ISR (1971-01-27 to 1984)
* SPS: in 26 GeV; out up to 450 GeV
  → LHC (since 2008-09-10); → HL-LHC (planned, mid-2030, derived);
  → LEP as e⁺/e⁻ injector, 3.5 → 20 GeV (1989-07-14 to 2000-11-02);
  → CNGS beamline, 400 GeV/c protons (2006-07 to 2012-12);
  → North Area beamline (new), 400 GeV/c protons (from late 1976)
* LHC: in 450 GeV; 3.5 TeV per beam (Run 1, as before), 6.5 (Run 2), **6.8 TeV per beam, 13.6 TeV (Run 3)**, design 7 TeV / 14 TeV; HL-LHC 7 TeV nominal / 14 TeV (new)
* ISR: in 26 GeV/c; up to 31.4 GeV/c per ring (replaces a derived 31 GeV)

**Fermilab**

* Linac (400 MeV H⁻; 200 MeV until 1993) → Booster
* Booster: in 400 MeV (200 MeV before 1993; 800 MeV planned); out 8 GeV
  → Main Injector (since 1999-06-01); → Recycler (proton stacking, by late 2014); → BNB beamline (8 GeV kinetic)
* Recycler (8 GeV) → Main Injector (antiprotons from late 2005 to Sept 2011; protons from 2014)
* Main Injector: in 8 GeV; out 120 GeV (150 GeV as Tevatron injector 1999 to 2011; design 150 GeV)
  → NuMI beamline (120 GeV); → LBNF beamline (60 to 120 GeV);
  → Tevatron (spring 1999 to 2011-09-30)
* Tevatron: in 150 GeV; out 980 GeV per beam, 1.96 TeV
* PIP-II (800 MeV, planned) → Booster (planned, about 2030, DUNE beam 2031)

**J-PARC**

* Linac (400 MeV H⁻ since January 2014; **181 MeV 2007-01 to 2014-01**) → RCS
* RCS: in 400 MeV (181 MeV until 2014); out 3 GeV → MR (from 2008-12)
* MR: in 3 GeV; out 30 GeV (design 50 GeV) → neutrino beamline (30 GeV)

**BNL** (two new records)

* Linac (200 MeV H⁻, 1971; **new**) → Booster (1991); also → AGS directly 1971 to about 1991
* Booster (**new**): in 200 MeV; out 1.5 GeV (protons) → AGS (1991)
* AGS: in 1.5 GeV; out 24 GeV protons, 8.86 GeV per nucleon gold (design 33 GeV) → RHIC (2000-04-02 to 2026-02-06)
* RHIC: in 24 GeV (protons); 250 GeV protons / 100 GeV per nucleon gold

**KEK** (one new record)

* KEK injector linac (**new**, 600 m): 8 GeV e⁻ / 3.5 GeV e⁺ → KEKB (1998 to 2010-06-30);
  7 GeV e⁻ / 4 GeV e⁺ → SuperKEKB (from 2016-02)

**SLAC**

* SLAC linac (up to 50 GeV) → PEP-II, 9.0 GeV e⁻ / 3.1 GeV e⁺ (1999 to 2008). **The record had it reversed** (`pep-ii` feeding `slac-linac`); fixed.
  The SLC did not take beam from the linac, it *was* the linac in collider mode, so no link.

**DESY**

* HERA only (no pre-accelerator records): protons LINAC III (50 MeV) → DESY III (8 GeV) → PETRA (40 GeV) → HERA 920 GeV;
  electrons LINAC II (450 MeV) → DESY II (7 GeV) → PETRA (12 GeV) → HERA 27.5 GeV. Recorded as `injection_energy` and in notes.

## Entities written

Counts: 3 new accelerator records (`bnl-linac`, `bnl-booster`, `kek-linac`), 1 new beamline
(`cern-north-area`), 26 accelerator and 1 beamline records edited, 15 source records
added, 3 geometry records and 2 map records edited, 1 schema line.

Each row shows the dates, URL and verbatim quote behind them (quotes were machine-checked
against the fetched pages with `scripts/atlas_quote_check.py` machinery on 2026-10-26).
Coordinates: none written (no new sites). `site` is the Atlas site of the machine.

#### `accelerator:ags` (edited) — status active, site site:bnl-upton-campus

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| feeds | accelerator:ags → accelerator:rhic | 2000-04-02 … 2026-02-06 | <https://www.bnl.gov/rhic/ags.php>, <https://www.bnl.gov/rhic/complex.php> | the AGS receives protons and other ions from the AGS Booster and delivers them to the Relativistic Heavy Ion Collider after acceleration. | approximate |
| spec injection_energy | 1.5 GeV (protons) |  | <https://arxiv.org/abs/1209.2803> | which accelerates the protons to 1.5 GeV. The bunch of polarized protons is then transferred to the Alternating Gradient Synchrotron (AGS) and accelerated to 24 GeV before injection into RHIC. | verified |
| interval | RHIC injector (24 GeV protons) (active) [beam_energy=24 GeV (protons); injection_energy=1.5 GeV (protons)] | 2000-04-02 … 2026-02-06 | <https://arxiv.org/abs/1209.2803>, <https://jacow.org/p01/papers/RPPH045.pdf> | The bunch of polarized protons is then transferred to the Alternating Gradient Synchrotron (AGS) and accelerated to 24 GeV before injection into RHIC. | approximate |

#### `accelerator:bnl-booster` (NEW) — status active, site site:bnl-upton-campus

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| feeds | accelerator:bnl-booster → accelerator:ags | 1991 … open | <https://www.bnl.gov/rhic/complex.php>, <https://www.bnl.gov/rhic/booster.php> | The Booster then feeds the beam into the Alternating Gradient Synchrotron. | verified |
| spec beam_energy | 1.5 GeV (protons) |  | <https://arxiv.org/abs/1209.2803> | In the case of polarized-proton running at RHIC, a pulse of polarized H− ions from the source is accelerated to 200 MeV in the linac, then stripped of its electrons as it is injected and captured as a single bunch of polarized protons in the Booster, which accelerates the protons to 1.5 GeV. | verified |
| spec injection_energy | 200 MeV (protons) |  | <https://www.bnl.gov/rhic/booster.php> | accepting heavy ions from EBIS or protons from the 200-million electron volt (MeV) Linac. | verified |
| interval | construction (construction) | 1986 … 1991 | <https://www.bnl.gov/rhic/booster.php> | Construction of the Alternating Gradient Synchrotron (AGS) Booster was begun in 1986 and completed in 1991. | verified |
| interval | operating (active) | 1991 … open | <https://www.bnl.gov/rhic/booster.php>, <https://www.bnl.gov/rhic/complex.php> | Construction of the Alternating Gradient Synchrotron (AGS) Booster was begun in 1986 and completed in 1991. | verified |

#### `accelerator:bnl-linac` (NEW) — status active, site site:bnl-upton-campus

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| feeds | accelerator:bnl-linac → accelerator:bnl-booster | 1991 … open | <https://www.bnl.gov/rhic/booster.php>, <https://www.bnl.gov/rhic/linac.php> | accepting heavy ions from EBIS or protons from the 200-million electron volt (MeV) Linac. It then feeds them to the AGS for further acceleration and delivery to RHIC. | verified |
| feeds | accelerator:bnl-linac → accelerator:ags | 1971 … until the Booster entered service (completed 1991) | <https://www.bnl.gov/rhic/linac.php>, <https://www.bnl.gov/rhic/booster.php> | The Brookhaven Linear Accelerator (Linac) operation started in 1971 as a major upgrade to the Alternating Gradient Synchroton (AGS) complex. | approximate |
| spec beam_energy | 200 MeV |  | <https://www.bnl.gov/rhic/linac.php>, <https://www.bnl.gov/rhic/complex.php> | The Linac is capable of producing a negatively charged hydrogen beam of up to 200 million electron-volts (MeV) energy and 135 microampere average current. | verified |
| spec length | 140 m (459 ft) |  | <https://www.bnl.gov/rhic/linac.php> | a radiofrequency quadropole, and nine accelerator radiofrequency cavities spanning the length of a 459 foot tunnel | derived |
| interval | operating (active) | 1971 … open | <https://www.bnl.gov/rhic/linac.php> | The Brookhaven Linear Accelerator (Linac) operation started in 1971 as a major upgrade to the Alternating Gradient Synchroton (AGS) complex. | verified |

#### `accelerator:fermilab-booster` (edited) — status active, site site:fermilab-main-campus

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| feeds | accelerator:fermilab-booster → accelerator:fermilab-main-injector | 1999-06-01 … open | <https://doi.org/10.1016/j.nima.2015.08.063>, <https://arxiv.org/abs/1408.0759> | This accelerator would use the Fermilab 8 GeV Booster as an injector and have the ability to accelerate protons up to 150 GeV | verified |
| feeds | accelerator:fermilab-booster → accelerator:fermilab-recycler | by late 2014 (first documented step: 6 batches stacked); not before the Tevatron stopped in 2011 … open | <https://arxiv.org/abs/1705.03075> | the Recycler is now used to stack high intensity protons for loading into the 120 GeV Main Injector synchrotron which is located in the same tunnel. Circumference of the Recycler is sufficient to accommodate six batches of 84 Booster bunches each; | approximate |
| spec injection_energy | 400 MeV |  | <https://doi.org/10.1016/j.nima.2015.08.063>, <https://indico.jacow.org/event/95/contributions/11894/attachments/1579/7589/TUI4M02_talk_edited_version.pdf> | Protons originate as H− ions in the Linac which accelerates them to 400 MeV. The ions are converted into protons in the Booster where they are accelerated to 8 GeV as 1.6 µs long batches with a 53 MHz bunch spacing. | verified |
| interval | 200 MeV injection (before the 1993 Linac upgrade) (active) [injection_energy=200 MeV] | 1971-05-21 … between Run Ia (ended May 1993) and Run Ib (began December 1993) | <https://arxiv.org/abs/1109.1864> | The 400 MeV linac upgrade (from the initial 200 MeV) was implemented between Run Ia and Run Ib | approximate |
| interval | Injection from the PIP-II linac (planned) (planned) [injection_energy=800 MeV] | after the 2028-2029 long shutdown; LBNF beam to DUNE planned for 2031 (planned) … open | <https://indico.jacow.org/event/95/contributions/11894/attachments/1579/7589/TUI4M02_talk_edited_version.pdf> | Booster commissioning with beam from the PIP-II linac uses the Booster Neutrino Beam facility which allows an experimental program if approved | approximate |

#### `accelerator:fermilab-linac` (edited) — status active, site site:fermilab-main-campus

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| feeds | accelerator:fermilab-linac → accelerator:fermilab-booster | open … open | <https://doi.org/10.1016/j.nima.2015.08.063>, <https://arxiv.org/abs/1705.03075> | Protons originate as H− ions in the Linac which accelerates them to 400 MeV. The ions are converted into protons in the Booster where they are accelerated to 8 GeV as 1.6 µs long batches with a 53 MHz bunch spacing. | verified |
| interval | Original 200 MeV linac (active) [beam_energy=200 MeV] | 1970-12-01 … between Run Ia (ended May 1993) and Run Ib (began December 1993) | <https://arxiv.org/abs/1109.1864> | The 400 MeV linac upgrade (from the initial 200 MeV) was implemented between Run Ia and Run Ib | approximate |

#### `accelerator:fermilab-main-injector` (edited) — status shutdown, site site:fermilab-main-campus

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| feeds | accelerator:fermilab-main-injector → accelerator:fermilab-tevatron | spring 1999 … 2011-09-30 | <https://arxiv.org/abs/1408.0759>, <https://arxiv.org/abs/1109.1864>, <https://doi.org/10.1016/j.nima.2015.08.063> | Protons from the Booster and antiprotons from the Recycler were accelerated to 150 GeV in the Main Injector | approximate |
| spec injection_energy | 8 GeV |  | <https://doi.org/10.1016/j.nima.2015.08.063> | This accelerator would use the Fermilab 8 GeV Booster as an injector and have the ability to accelerate protons up to 150 GeV | verified |
| interval | Tevatron injector (150 GeV) (active) [beam_energy=150 GeV] | spring 1999 … 2011-09-30 | <https://arxiv.org/abs/1408.0759> | Protons from the Booster and antiprotons from the Recycler were accelerated to 150 GeV in the Main Injector | approximate |

#### `accelerator:fermilab-pip-ii` (edited) — status construction, site site:fermilab-main-campus

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| feeds | accelerator:fermilab-pip-ii → accelerator:fermilab-booster | after the 2028-2029 long shutdown; LBNF beam to DUNE planned for 2031 (planned) … open | <https://indico.jacow.org/event/95/contributions/11894/attachments/1579/7589/TUI4M02_talk_edited_version.pdf> | Booster commissioning with beam from the PIP-II linac uses the Booster Neutrino Beam facility which allows an experimental program if approved | approximate |

#### `accelerator:fermilab-recycler` (edited) — status active, site site:fermilab-main-campus

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| feeds | accelerator:fermilab-recycler → accelerator:fermilab-main-injector | late 2005 … 2011-09 | <https://arxiv.org/abs/1408.0759>, <https://arxiv.org/abs/1109.1864> | Since late 2005, all Tevatron antiprotons were extracted from the Recycler only. | approximate |
| feeds | accelerator:fermilab-recycler → accelerator:fermilab-main-injector | by late 2014 (first documented step: 6 batches stacked); not before the Tevatron stopped in 2011 … open | <https://arxiv.org/abs/1705.03075> | the Recycler is now used to stack high intensity protons for loading into the 120 GeV Main Injector synchrotron which is located in the same tunnel. Circumference of the Recycler is sufficient to accommodate six batches of 84 Booster bunches each; | approximate |

#### `accelerator:fermilab-tevatron` (edited) — status decommissioned, site site:fermilab-main-campus

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| spec injection_energy | 150 GeV |  | <https://arxiv.org/abs/1408.0759> | Protons from the Booster and antiprotons from the Recycler were accelerated to 150 GeV in the Main Injector | verified |

#### `accelerator:hera` (edited) — status completed, site site:desy-hamburg-campus

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| spec beam_energy | 27.5 GeV (electrons/positrons) |  | <https://arxiv.org/abs/0805.3334> | The energy of the electron (positron) beam was about 27.5 GeV. | verified |
| spec circumference | 6336 m |  | <https://www.desy.de/e141261/e158573/e158772/index_eng.html> | Length: 6336 metres | verified |
| spec cms_energy | 320 GeV |  | <https://arxiv.org/abs/0805.3334> | From 1992 to 2007, HERA, the first electron-proton collider, operated at cms energies of about 320 GeV | verified |
| spec injection_energy | 40 GeV (protons from PETRA); 12 GeV (electrons from PETRA) |  | <https://arxiv.org/abs/0805.3334> | Protons Source RFQ LINAC III DESY III PETRA HERA Ep 20 keV 750 keV 50 MeV 8 GeV 40 GeV 920 GeV Electrons Ee Source 150 keV LINAC II 450 MeV PIA 450 MeV DESY II 7 GeV PETRA 12 GeV HERA 27.5 GeV | verified |
| spec proton_energy | 920 GeV (protons) |  | <https://arxiv.org/abs/0805.3334> | The energy of the proton beam was initially set to 820 GeV until it was increased to 920 GeV, in 1998, and kept at that value. | verified |

#### `accelerator:hl-lhc` (edited) — status construction, site site:cern-meyrin

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| spec beam_energy | 7 TeV per beam (nominal baseline) |  | <https://accelconf.web.cern.ch/ipac2018/papers/mopml009.pdf> | The current HL-LHC baseline, with the nominal beam energy of 7.0 TeV, features the parameters shown in Table 1 [4,12]. | verified |
| spec cms_energy | 14 TeV (twice the nominal beam energy) |  | <https://accelconf.web.cern.ch/ipac2018/papers/mopml009.pdf> | The current HL-LHC baseline, with the nominal beam energy of 7.0 TeV, features the parameters shown in Table 1 [4,12]. | derived |

#### `accelerator:isr` (edited) — status decommissioned, site site:cern-meyrin

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| spec beam_energy | up to 31.4 GeV/c per ring |  | <https://arxiv.org/abs/1206.3950> | The CERN PS injected 26 GeV/c proton beams into the two rings that could accelerate up to 31.4 GeV/c. | verified |
| spec injection_energy | 26 GeV/c from the PS |  | <https://arxiv.org/abs/1206.3950> | The CERN PS injected 26 GeV/c proton beams into the two rings that could accelerate up to 31.4 GeV/c. | verified |

#### `accelerator:j-parc-linac` (edited) — status active, site site:j-parc-main-ring

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| feeds | accelerator:j-parc-linac → accelerator:j-parc-rcs | open … open | <https://arxiv.org/pdf/1106.1238>, <https://j-parc.jp/c/en/facilities/index.html> | An H− beam is accelerated up to 400 MeV5 (181 MeV at present) by the LINAC, and is converted to an H+ beam by charge-stripping foils at the RCS injection. | verified |
| spec beam_energy | 400 MeV |  | <https://j-parc.jp/c/en/facilities/accelerators/linac.html>, <https://j-parc.jp/c/en/facilities/index.html> | A 400 MeV linear accelerator | verified |
| interval | 181 MeV operation (initial energy) (active) [beam_energy=181 MeV] | 2007-01 … 2014-01 | <https://www.kek.jp/en/about/history/>, <https://j-parc.jp/c/en/about/history.html>, <https://arxiv.org/pdf/1106.1238> | 2007 Jan：181MeV proton beam at J-PARC Linac | verified |
| interval | 400 MeV operation (after the energy upgrade) (active) [beam_energy=400 MeV] | 2014-01 … open | <https://j-parc.jp/c/en/about/history.html>, <https://j-parc.jp/c/en/facilities/accelerators/linac.html> | 2014 January Energy upgrade was achieved at Linac. | verified |

#### `accelerator:j-parc-main-ring` (edited) — status active, site site:j-parc-main-ring

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| spec injection_energy | 3 GeV |  | <https://arxiv.org/pdf/1106.1238> | beam is accelerated up to 3 GeV by the RCS with a 25 Hz cycle. The harmonic number of the RCS is two, and there are two bunches in a cycle. About 5% of these bunches are supplied to the MR. | verified |

#### `accelerator:j-parc-rcs` (edited) — status active, site site:j-parc-main-ring

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| feeds | accelerator:j-parc-rcs → accelerator:j-parc-main-ring | 2008-12 … open | <https://arxiv.org/pdf/1106.1238>, <https://j-parc.jp/c/en/facilities/index.html> | beam is accelerated up to 3 GeV by the RCS with a 25 Hz cycle. The harmonic number of the RCS is two, and there are two bunches in a cycle. About 5% of these bunches are supplied to the MR. | approximate |
| spec injection_energy | 400 MeV |  | <https://arxiv.org/pdf/1106.1238>, <https://j-parc.jp/c/en/facilities/accelerators/linac.html> | An H− beam is accelerated up to 400 MeV5 (181 MeV at present) by the LINAC, and is converted to an H+ beam by charge-stripping foils at the RCS injection. | verified |
| interval | 181 MeV injection (before the Linac energy upgrade) (active) [injection_energy=181 MeV] | 2007-10 … 2014-01 | <https://arxiv.org/pdf/1106.1238>, <https://www.kek.jp/en/about/history/> | An H− beam is accelerated up to 400 MeV5 (181 MeV at present) by the LINAC, and is converted to an H+ beam by charge-stripping foils at the RCS injection. | verified |

#### `accelerator:kek-linac` (NEW) — status active, site none

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| feeds | accelerator:kek-linac → accelerator:kekb | 1998 … 2010-06-30 | <https://www2.kek.jp/accl/eng/fa_accl-en/kekb-ring/>, <https://arxiv.org/abs/1809.01958> | maintained nearly constant by a top-up injection from the Linac during the collision experiment. | approximate |
| feeds | accelerator:kek-linac → accelerator:superkekb | 2016-02 … open | <https://arxiv.org/abs/1809.01958> | The SuperKEKB collider complex consists of a 7-GeV electron ring (the high-energy ring, HER), a 4-GeV positron ring (the low-energy ring, LER), and an injector linear accelerator (linac) with a 1.1-GeV positron damping ring (DR) | approximate |
| spec beam_energy | 7 GeV e⁻ and 4 GeV e⁺ (SuperKEKB) |  | <https://arxiv.org/abs/1809.01958> | The SuperKEKB collider complex consists of a 7-GeV electron ring (the high-energy ring, HER), a 4-GeV positron ring (the low-energy ring, LER), and an injector linear accelerator (linac) with a 1.1-GeV positron damping ring (DR) | verified |
| spec length | 600 m |  | <https://arxiv.org/abs/1809.01958> | The 600-m injector linac is composed of 60 high-power accelerating units followed by a beam switch yard. | verified |
| interval | construction (construction) | 1978 … 1982 | <https://arxiv.org/abs/1809.01958> | It was originally constructed for Photon Factory as a 2.5-GeV electron linac beginning in 1978 and was commissioned in 1982. | verified |
| interval | operating (active) | 1982 … open | <https://arxiv.org/abs/1809.01958> | The electron–positron injector linac at KEK has delivered electrons and positrons for particle physics and photon science experiments since 1982. | verified |
| interval | KEKB injector (up to 8 GeV) (active) [beam_energy=up to 8 GeV (electrons)] | 1998 … 2010-06-30 | <https://arxiv.org/abs/1809.01958>, <https://www2.kek.jp/accl/eng/fa_accl-en/kekb-ring/> | Then, the linac was upgraded for the KEKB asymmetric-energy collider project with energy enforcement up to 8 GeV | approximate |

#### `accelerator:kekb` (edited) — status decommissioned, site site:kek-tsukuba-belle-ii

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|

#### `accelerator:lep` (edited) — status decommissioned, site site:cern-meyrin

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| spec injection_energy | 20 GeV (from the SPS) |  | <https://accelconf.web.cern.ch/l88/papers/mo1-04.pdf> | Similarly the SPS operates as an e+/e- synchrotron between 3.5 GeV and 20 GeV, the nominal LEP injection energy. | verified |

#### `accelerator:lhc` (edited) — status shutdown, site site:cern-meyrin

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| spec injection_energy | 450 GeV |  | <https://proceedings.jacow.org/ipac2024/pdf/THPR31.pdf> | SPS beams at 450 GeV are injected into the LHC via 2 transfer lines, TI2 and TI8 [6]. | verified |

#### `accelerator:linac2` (edited) — status decommissioned, site site:cern-meyrin

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| feeds | accelerator:linac2 → accelerator:psb | 1978 … 2018-11-12 | <https://home.cern/science/accelerators/proton-synchrotron-booster>, <https://home.cern/science/accelerators/linear-accelerator-2> | From 1978 until 2018, the Booster received protons from Linac2 at 50 MeV and accelerated them to 1.4 GeV for injection into the PS. | verified |

#### `accelerator:linac4` (edited) — status shutdown, site site:cern-meyrin

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| feeds | accelerator:linac4 → accelerator:psb | 2020 … open | <https://home.cern/science/accelerators/linear-accelerator-2>, <https://home.cern/science/accelerators/linear-accelerator-4> | It was replaced by Linac4, which was inaugurated in 2017 and connected to the PS Booster in 2020 during CERN’s Long Shutdown 2. | verified |

#### `accelerator:pep-ii` (edited) — status completed, site site:slac-pep-ii-ir2-babar

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| spec beam_energy | 9.0 GeV e⁻ and 3.1 GeV e⁺ |  | <https://epaper.kek.jp/p95/ARTICLES/WAQ/WAQ15.PDF> | Utilization of the existing high power, low emittance beams available at SLAC required that a great portion of the systems for pulsed extraction and transport of 9.0 GeV electrons and 3.1 GeV positrons for injection into the PEP-II rings will reside in the existing linac housing. | verified |
| spec injection_energy | 9.0 GeV e⁻ and 3.1 GeV e⁺ (full-energy injection from the linac) |  | <https://epaper.kek.jp/p95/ARTICLES/WAQ/WAQ15.PDF> | Utilization of the existing high power, low emittance beams available at SLAC required that a great portion of the systems for pulsed extraction and transport of 9.0 GeV electrons and 3.1 GeV positrons for injection into the PEP-II rings will reside in the existing linac housing. | verified |

#### `accelerator:ps` (edited) — status shutdown, site site:cern-meyrin

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| feeds | accelerator:ps → accelerator:isr | 1971-01-27 … 1984 | <https://home.cern/science/accelerators/intersecting-storage-rings>, <https://arxiv.org/abs/1206.3950> | The Proton Synchrotron, which is still in operation, fed proton beams into the ISR. | verified |
| feeds | accelerator:ps → accelerator:sps | 1976-06-17 … open | <https://home.cern/science/accelerators/super-proton-synchrotron>, <https://be-dep-op-sps.web.cern.ch/history> | Measuring nearly 7 kilometres in circumference, it takes particles from the Proton Synchrotron and accelerates them to provide beams for the Large Hadron Collider, the NA61/SHINE and NA62 experiments, the COMPASS experiment. | verified |
| spec beam_energy | up to 26 GeV |  | <https://home.cern/science/accelerators/proton-synchrotron>, <https://home.cern/science/accelerators/accelerator-complex> | The accelerator operates at up to 26 GeV. | verified |
| spec injection_energy | 2 GeV |  | <https://home.cern/science/accelerators/proton-synchrotron-booster>, <https://home.cern/press/media-kits/accelerator-upgrades-during-ls2/> | The ions are stripped of their two electrons during injection from Linac4 into the Proton Synchrotron Booster to leave only protons, which are accelerated to 2 GeV for injection into the Proton Synchrotron (PS). | verified |
| interval | Direct Linac1 injection (50 MeV) (active) [injection_energy=50 MeV] | 1959-11-24 … 1972-05-26 | <https://home.cern/science/accelerators/proton-synchrotron-booster> | Before the Booster received its first beams on 26 May 1972, protons were injected directly from Linac1 into the PS, where they were accelerated to 26 GeV. | approximate |
| interval | Booster injection at 0.8 to 1 GeV (active) [injection_energy=about 0.9 GeV (0.8 to 1 GeV)] | 1972-05-26 … 1999 | <https://cerncourier.com/a/the-ps-booster-hits-40/> | On 26 May 1972, the PS Booster (PSB) accelerated its first protons to the design energy of 800 MeV. | approximate |
| interval | Booster injection at 1.4 GeV (active) [injection_energy=1.4 GeV] | 1999 … 2018 | <https://home.cern/press/media-kits/accelerator-upgrades-during-ls2/>, <https://cerncourier.com/a/40-years-of-cerns-proton-synchrotron/> | To cope with the almost 50% increase in injection energy from 1.4 to 2 GeV, the 20-metre-long injection line into the PS was replaced | verified |

#### `accelerator:psb` (edited) — status shutdown, site site:cern-meyrin

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| feeds | accelerator:psb → accelerator:ps | 1972-05-26 … open | <https://home.cern/science/accelerators/proton-synchrotron-booster>, <https://home.cern/science/accelerators/proton-synchrotron> | Before the Booster received its first beams on 26 May 1972, protons were injected directly from Linac1 into the PS, where they were accelerated to 26 GeV. | verified |
| spec injection_energy | 160 MeV |  | <https://home.cern/science/accelerators/proton-synchrotron-booster>, <https://home.cern/science/accelerators/accelerator-complex> | receive beams of negative hydrogen ions (H-, consisting of a hydrogen atom with an additional electron) from the linear accelerator Linac4 at 160 MeV. | verified |
| interval | Linac2 era (50 MeV injection) (active) [injection_energy=50 MeV] | 1978 … 2018 | <https://home.cern/science/accelerators/proton-synchrotron-booster> | From 1978 until 2018, the Booster received protons from Linac2 at 50 MeV and accelerated them to 1.4 GeV for injection into the PS. | verified |
| interval | Linac1 era (50 MeV injection) (active) [injection_energy=50 MeV] | 1972-05-26 … 1978 | <https://cerncourier.com/a/the-ps-booster-hits-40/>, <https://home.cern/science/accelerators/linear-accelerator-2> | The 50 MeV beam from Linac1 is distributed vertically and multiturn-injected into each ring. | verified |
| interval | 800 MeV to 1 GeV extraction era (active) [beam_energy=about 0.9 GeV (0.8 to 1 GeV)] | 1972-05-26 … 1999 | <https://cerncourier.com/a/the-ps-booster-hits-40/> | On 26 May 1972, the PS Booster (PSB) accelerated its first protons to the design energy of 800 MeV. | approximate |
| interval | 1.4 GeV extraction era (active) [beam_energy=1.4 GeV] | 1999 … 2018 | <https://cerncourier.com/a/40-years-of-cerns-proton-synchrotron/>, <https://home.cern/science/accelerators/proton-synchrotron-booster> | In 1999 the harmful effects of space charge in the PS were reduced by raising the Booster energy to 1.4 GeV. | verified |

#### `accelerator:rhic` (edited) — status completed, site site:bnl-upton-campus

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| spec beam_energy | up to 250 GeV (protons); 100 GeV per nucleon (gold) |  | <https://science.osti.gov/np/Facilities/User-Facilities/RHIC> | RHIC collides all ion beam species from protons to Uranium at energies up to 100 GeV (Giga Electron Volts) per nucleon (250 GeV for protons). | verified |
| spec injection_energy | about 24 GeV (protons); 8.86 GeV per nucleon (gold) |  | <https://arxiv.org/abs/1209.2803>, <https://jacow.org/p01/papers/RPPH045.pdf> | The bunch of polarized protons is then transferred to the Alternating Gradient Synchrotron (AGS) and accelerated to 24 GeV before injection into RHIC. | verified |

#### `accelerator:slac-linac` (edited) — status active, site site:slac-menlo-park-campus

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| feeds | accelerator:slac-linac → accelerator:pep-ii | open … open | <https://epaper.kek.jp/p95/ARTICLES/WAQ/WAQ15.PDF>, <https://www.slac.stanford.edu/gen/grad/GradHandbook/slac.html>, <https://www6.slac.stanford.edu/news/2016-05-04-slacs-historic-linac-turns-50-and-gets-makeover> | Utilization of the existing high power, low emittance beams available at SLAC required that a great portion of the systems for pulsed extraction and transport of 9.0 GeV electrons and 3.1 GeV positrons for injection into the PEP-II rings will reside in the existing linac housing. | verified |
| spec beam_energy | up to 50 GeV (electrons) |  | <https://www.slac.stanford.edu/gen/grad/GradHandbook/slac.html> | In the 1980s, new, improved klystrons manufactured at the laboratory reached peak powers of 64 MW which, in combination with SLED, boosted the linac energy to 50 GeV. | verified |
| spec length | 3.2 km (two miles) |  | <https://www.slac.stanford.edu/gen/grad/GradHandbook/slac.html>, <https://www6.slac.stanford.edu/news/2016-05-04-slacs-historic-linac-turns-50-and-gets-makeover> | The first major accelerator facility at SLAC was the two-mile-long linear accelerator, completed in 1966. | derived |
| interval | operating (active) | 1966-05-21 … open | <https://www6.slac.stanford.edu/news/2016-05-04-slacs-historic-linac-turns-50-and-gets-makeover>, <https://www.slac.stanford.edu/gen/grad/GradHandbook/slac.html> | When the linac produced its first particle beam in the early morning hours of May 21, 1966, it was the single largest civilian science project ever undertaken by the U.S. government. | verified |

#### `accelerator:slc` (edited) — status completed, site site:slac-slc-collider-hall-sld

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|

#### `accelerator:sps` (edited) — status shutdown, site site:cern-meyrin

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| feeds | accelerator:sps → accelerator:lep | 1989-07-14 … 2000-11-02 | <https://be-dep-op-sps.web.cern.ch/history>, <https://home.cern/science/accelerators/large-electron-positron-collider> | With the commissioning of the Large Electron-Positron Collider in July 1989, the SPS got a new role as an injector, sending electrons and positrons to LEP at an energy of 20 GeV. | verified |
| feeds | accelerator:sps → accelerator:lhc | 2008-09-10 … open | <https://be-dep-op-sps.web.cern.ch/history>, <https://home.cern/science/accelerators/accelerator-complex> | On 10 September 2008, the first beam from the SPS made a successful loop of the LHC. | verified |
| feeds | accelerator:sps → accelerator:hl-lhc | mid-2030 (planned) … open | <https://be-dep-op-sps.web.cern.ch/history>, <https://home.cern/science/accelerators/hilumi-lhc> | On 10 September 2008, the first beam from the SPS made a successful loop of the LHC. | derived |
| spec injection_energy | 26 GeV |  | <https://home.cern/science/accelerators/accelerator-complex> | These are accelerated to 2 GeV for injection into the Proton Synchrotron (PS), which pushes the beam up to 26 GeV. Protons are then sent to the Super Proton Synchrotron (SPS), where they are accelerated up to 450 GeV. | verified |
| interval | LEP injector (e+/e-) (active) [beam_energy=20 GeV (e+/e-); injection_energy=3.5 GeV (e+/e-)] | 1989-07-14 … 2000-11-02 | <https://accelconf.web.cern.ch/l88/papers/mo1-04.pdf>, <https://be-dep-op-sps.web.cern.ch/history>, <https://home.cern/science/accelerators/large-electron-positron-collider> | Similarly the SPS operates as an e+/e- synchrotron between 3.5 GeV and 20 GeV, the nominal LEP injection energy. | verified |

#### `accelerator:superkekb` (edited) — status active, site site:kek-tsukuba-belle-ii

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|

#### `beamline:cern-north-area` (NEW) — status shutdown, site none

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| spec proton_energy | 400 GeV/c |  | <https://be-dep-ea.web.cern.ch/northarea> | The beams are produced after the 400 GeV/c SPS proton beam on each of the three primary targets T2, T4, and T6. | verified |
| primary_beam | proton, 400 GeV/c |  | <https://be-dep-ea.web.cern.ch/northarea> | The beams are produced after the 400 GeV/c SPS proton beam on each of the three primary targets T2, T4, and T6. | verified |
| interval | beam operation (active) | late 1976 … 2026-08-31 | <https://be-dep-op-sps.web.cern.ch/history>, <https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/>, <https://home.cern/science/accelerators/accelerator-complex> | From late 1976 the SPS started delivering proton beams to fixed-target experiments in the North and West Areas. | approximate |
| interval | Long Shutdown 3 (injector complex) (shutdown) | 2026-08-31 … staged restart from 2028 onwards (planned) | <https://home.cern/all-cern-accelerators-now-on-the-road-to-hilumi/>, <https://home.cern/accelerator-report-final-countdown-cerns-injector-complex-enters-its-last-stretch-before-ls3/> | CERN’s injector complex and Antimatter Factory took their final steps towards Long Shutdown 3 (LS3) this morning, as the last particle beams were extracted and the machines fell silent. | approximate |

#### `beamline:cngs` (edited) — status completed, site none

| kind | what | dates | URL | verbatim quote | conf |
|---|---|---|---|---|---|
| spec proton_energy | 400 GeV/c |  | <https://accelconf.web.cern.ch/IPAC2013/papers/mopea058.pdf> | A 400 GeV/c proton beam is fast-extracted from the CERN SPS accelerator. | verified |
| primary_beam | proton, 400 GeV/c |  | <https://accelconf.web.cern.ch/IPAC2013/papers/mopea058.pdf> | A 400 GeV/c proton beam is fast-extracted from the CERN SPS accelerator. | verified |


#### Sources added (15)

| id | type | title | URL |
|---|---|---|---|
| `src:aidala-spin-structure-rmp-2013` | arxiv | The Spin Structure of the Nucleon | <https://arxiv.org/abs/1209.2803> |
| `src:bnl-rhic-booster-page` | official_facility_site | Booster Synchrotron (RHIC accelerator complex) | <https://www.bnl.gov/rhic/booster.php> |
| `src:bnl-rhic-linac-page` | official_facility_site | 200 MeV Linear Accelerator (RHIC accelerator complex) | <https://www.bnl.gov/rhic/linac.php> |
| `src:cern-accelerator-upgrades-ls2-media-kit` | press_release | Accelerator upgrades during LS2 | <https://home.cern/press/media-kits/accelerator-upgrades-during-ls2/> |
| `src:cern-courier-40-years-ps-1999` | press_release | 40 years of CERN's Proton Synchrotron | <https://cerncourier.com/a/40-years-of-cerns-proton-synchrotron/> |
| `src:cngs-ipac2013-gschwendtner` | journal_article | CNGS, CERN Neutrinos to Gran Sasso, Five Years of Running a 500 Kilowatt Neutrino Beam Facility at CERN (IPAC2013, MOPEA058) | <https://accelconf.web.cern.ch/IPAC2013/papers/mopea058.pdf> |
| `src:hera-collider-physics-klein-yoshida-2008` | arxiv | Collider Physics at HERA | <https://arxiv.org/abs/0805.3334> |
| `src:hl-lhc-ipac2018-mopml009` | journal_article | New High Luminosity LHC Baseline and Performance at Ultimate Energy (IPAC2018, MOPML009) | <https://accelconf.web.cern.ch/ipac2018/papers/mopml009.pdf> |
| `src:isr-bryant-arxiv-1206-3950` | arxiv | The impact of the ISR on accelerator physics and technology | <https://arxiv.org/abs/1206.3950> |
| `src:lep-injector-linac1988-warner` | journal_article | New and Proposed Linacs at CERN: the LEP (e+/e-) Injector and the SPS Heavy Ion (Pb) Injector (LINAC 1988, MO1-04) | <https://accelconf.web.cern.ch/l88/papers/mo1-04.pdf> |
| `src:lhc-ipac2024-injection-losses` | journal_article | Study of the Performance and Beam Loss Limitations during Injection of High-Intensity LHC Proton Beams (IPAC2024, THPR31) | <https://proceedings.jacow.org/ipac2024/pdf/THPR31.pdf> |
| `src:pep-ii-injection-pac1995-fieguth` | journal_article | PEP-II Injection Transport Construction Status and Commissioning Plans (PAC 1995, WAQ15) | <https://epaper.kek.jp/p95/ARTICLES/WAQ/WAQ15.PDF> |
| `src:rhic-gold-injector-pac2001-ahrens` | journal_article | Status and Recent Performance of the Accelerators that Serve as Gold Injector for RHIC (PAC 2001, RPPH045) | <https://jacow.org/p01/papers/RPPH045.pdf> |
| `src:slac-grad-handbook` | official_facility_site | The Stanford Linear Accelerator Center (SLAC graduate handbook page) | <https://www.slac.stanford.edu/gen/grad/GradHandbook/slac.html> |
| `src:slac-linac-turns-50-2016` | press_release | SLAC’s Historic Linac Turns 50 and Gets a Makeover | <https://www6.slac.stanford.edu/news/2016-05-04-slacs-historic-linac-turns-50-and-gets-makeover> |

#### Map rows added

| map | entity | reason (short) | sources |
|---|---|---|---|
| `map:cern` | `beamline:cern-north-area` | underground line and caverns, no coordinates found | `src:geo-cern-north-area-infrastructure`, `src:na62-cern-north-area-page` |
| `map:brookhaven-national-laboratory` | `accelerator:bnl-booster` | only an OSM `place=locality` label of Building 942; no ring trace | `src:geo-bnl-osm-context-buildings`, `src:bnl-rhic-booster-page` |

## Conflicts (claim / source A / source B / chosen / why)

| claim | A | B | chosen | why |
|---|---|---|---|---|
| PSB extraction energy 1978 to 2018 | CERN PSB page: "From 1978 until 2018, the Booster received protons from Linac2 at 50 MeV and accelerated them to 1.4 GeV" | CERN Courier (1999, 2012): 800 MeV at first beam (1972), 1 GeV later (ISOLDE used the 1 GeV beam by 1992), "In 1999 … raising the Booster energy to 1.4 GeV" | Courier for the energy eras; PSB page kept for the 50 MeV Linac2 injection | the page compresses 40 years into one figure |
| PS top energy | accelerator-complex page: 26 GeV | LS2 media kit: "pushes the beam up to 25 GeV" | 26 GeV kept, both noted | consistent with 26 GeV/c momentum = about 25 GeV kinetic (our inference, stated as such) |
| LHC Run 3 energy | accelerator-complex page: "6.8 TeV per beam" and 13.6 TeV | same page later: "maximum energy of 6.5 TeV" | 6.8 TeV | the 6.5 TeV sentence is the Run 2 text left on the page; the LHC page and the Run 3 media kit say 6.8 |
| North Area primary energy | BE-EA page, PBC report: 400 GeV/c | SPS history: "400 and later 450 GeV" | 400 GeV/c, both noted | current page; the SPS can deliver up to 450 GeV |
| J-PARC linac energy in 2007 | old Atlas record: "design energy reached", 400 MeV | KEK history "2007 Jan: 181 MeV proton beam at J-PARC Linac"; T2K paper "400 MeV (181 MeV at present)"; J-PARC history "2014 January Energy upgrade was achieved at Linac" | 181 MeV until 2014-01, 400 MeV after | the earlier record mislabelled a 181 MeV milestone |
| PEP-II ring energies | PAC 1995 and the BaBar paper: 9.0 and 3.1 GeV | SLAC handbook page: 9.1 and 3 GeV | 9.0 and 3.1 GeV | design values in the machine's own injection paper |
| RHIC booster and AGS proton energies | Aidala et al., Rev. Mod. Phys.: 1.5 GeV, 24 GeV (kinetic) | RHIC Cold QCD Program (arXiv:2302.00605): 2.3 GeV, 23 GeV | the RMP figures | 2.3 GeV is a total energy; the quantity is kinetic |
| HERA circumference | Klein & Yoshida: 6223 m | DESY HERA page: "Length: 6336 metres" | 6336 m | DESY's own figure; matches the tunnel geometry check |
| CNGS primary beam | old record: "muon neutrino", energy empty | IPAC 2013: "A 400 GeV/c proton beam is fast-extracted from the CERN SPS" | proton, 400 GeV/c | the old value was the secondary beam |
| SLAC linac / PEP-II direction | old record: `pep-ii` feeds `slac-linac` | PAC 1995: 9.0 GeV e⁻ and 3.1 GeV e⁺ "for injection into the PEP-II rings" from the linac | linac feeds PEP-II | the link was reversed |

## Unresolved (left empty, not guessed)

* PSB date of the 800 MeV to 1 GeV step (a range 0.8 to 1 GeV is recorded for 1972 to 1999; one non-CERN record says 1988, not used).
* LEP2 injection energy (the SPS paper gives the nominal 20 GeV of the LEP1 design); LHC Run 1 energy in 2012 (4 TeV): no CERN page consulted states it (CERN's own pages were not re-searched).
* HL-LHC Run 4 energy: only the 2018 baseline (7.0 TeV nominal, 7.5 TeV "ultimate" studied) is sourced.
* Start of North Area physics beams (late 1976 is the date the SPS "started delivering proton beams"; CERN Courier dates the first muon beams in the halls to 1978, not fetched).
* First beam from the AGS into RHIC (the page dates April 2000 for the first documented gold injection; RHIC was dedicated in October 1999 after commissioning).
* End of direct Linac injection into the AGS (year precision "about 1991", approximate).
* Fermilab: first Booster beam into the Recycler for stacking (late 2014, approximate); PIP-II connection date (a May 2026 draft schedule, bounds only: after the 2028-2029 shutdown, before DUNE beam in 2031).
* The Fermilab history pages (`history.fnal.gov`, `news.fnal.gov`) returned 403 or timed out when fetched on 2026-10-26, so quotes were taken from the Shiltsev, Nagaitsev and NuMI-paper PDFs on arXiv instead.
* A CERN CDS record (HL-LHC TDR) was not read: `cds.cern.ch` shows a bot challenge, which was not bypassed; `e-publishing.cern.ch` returned HTTP 500.

## Candidates considered and excluded

* CERN: Linac1, Linac3, LEIR, LIL, EPA, AD, ELENA, ISOLDE/HIE-ISOLDE, n_TOF, East Area. Not part of the chains in the brief; LIL and EPA are the e⁺/e⁻ stages before the PS for LEP (SPS → LEP is recorded). Each would also need an `unlocated` row.
* Fermilab Main Ring (injector of Tevatron Run I, 150 GeV; retired 1999), Antiproton Source (Debuncher, Accumulator), Delivery Ring, Muon Campus beamlines.
* J-PARC: Materials and Life Science facility (takes over 90 % of the RCS beam), Hadron Experimental Facility beamlines; no records.
* BNL: EBIS and the Tandem Van de Graaffs (heavy-ion pre-injectors), NSRL, BLIP. Not on the proton path.
* KEK: damping ring (1.1 GeV), PF and PF-AR, the KEK-PS injector chain (40 MeV linac, 500 MeV booster).
* SLAC: LCLS (no record), SPEAR/PEP (colliders stream), SLC as a feed target (see above).
* DESY: LINAC II/III, PIA, DESY II/III (chain stages, listed in HERA's note with energies; no pre-accelerator records were added because the colliders stream owns PETRA, the stage that joins them to HERA).

## Geometry audit: CERN, Fermilab, J-PARC

"Drawn" = a feature in `data/atlas/geometry/` with that `entity_id`. Nothing was added to
`geometry/`: no fetched source supports a path for any missing stage, and no ring was
guessed. Three existing records were re-linked or reworded (below).

### CERN (`map:cern`)

| stage | geometry | state |
|---|---|---|
| Linac2 | none | listed in `unlocated[]` (no OSM building trace, no building number) |
| Linac4 | `linac4-building` (building footprint, approximate) | the 86 m beam line is not drawn; the footprint (107 m span) is the surface building |
| PSB | `psb-tunnel-ring` (ring, approximate, 15 m) | drawn |
| PS | `ps-tunnel-ring` (ring, verified) | drawn |
| SPS | `sps-tunnel-ring` (ring, approximate, 30 m) | drawn |
| LHC | `lhc-tunnel-ring` (ring, verified) | drawn |
| HL-LHC | surface buildings at Points 1 and 5 | new shafts and galleries not drawn |
| LEP | `lep-tunnel-ring` (ring, verified) | drawn |
| ISR | none | listed in `unlocated[]` |
| CNGS | `cngs-direction-line` (inferred direction only) | the 840 m proton line is not drawn; no coordinates found |
| North Area (new) | EHN1 and ECN3 buildings as context | **new `unlocated[]` row** (TT20, TDC2, TCC2, TT81 to TT85 are underground; no coordinates found) |

Transfer lines with no geometry (none has a fetched source with coordinates or a
scale bar): Linac2/Linac4 to PSB; PSB to PS; PS to SPS; **SPS to LHC (TI2 and TI8, named in the
IPAC 2024 paper)**; **SPS to North Area (TT20, named on the NA-CONS page; TDC2, TCC2 caverns)**;
SPS to CNGS (840 m proton line, IPAC 2013); PS to ISR; SPS to LEP. The PS to SPS lines are
known as TT2 and TT10 in CERN documents we did not fetch, so those names are not asserted.

### Fermilab (`map:fermilab`)

| stage | geometry | state |
|---|---|---|
| Linac | `fermilab-linac` (linac, approximate, 25 m) | drawn |
| Booster | `fermilab-booster-ring` (derived), extraction point (surveyed) | drawn |
| Recycler | `fermilab-recycler-ring` (derived, 8 m) | drawn |
| Main Injector | `fermilab-main-injector-ring` (derived, 8 m) | drawn |
| Tevatron | `fermilab-tevatron-ring` (derived), A0 reference point | drawn |
| PIP-II | none | `unlocated[]` (site plan not georeferenced) |
| BNB | `fermilab-bnb-beamline`, target (derived) | drawn |
| NuMI | beamline, primary beamline, target, decay pipe, absorber (surveyed) | drawn |
| LBNF | direction line only | `unlocated[]` (no coordinates for target or hall) |

Transfer lines not drawn: Linac to Booster (400 MeV line), Booster to Main Injector and
Recycler (the 8 GeV line), the retired P1 and A1 lines from the Main Injector to the Tevatron
(named in the NuMI paper's Fig. 1), the Main Injector to LBNF primary line, PIP-II to Booster
(under construction).

### J-PARC (`map:j-parc`)

| stage | geometry | state |
|---|---|---|
| Linac | `j-parc-linac-building` (building, approximate, about 333 m span) | the beam line is not drawn; the footprint is the building |
| RCS | `j-parc-rcs-tunnel` (ring, verified) | drawn |
| MR | `j-parc-main-ring-tunnel` (ring, verified) | drawn |
| neutrino beamline | beamline tunnel (verified), target station, near-detector hall, direction line | drawn |

Transfer lines not drawn: Linac to RCS, RCS to MR, RCS to the Materials and Life Science
facility, MR to the Hadron Experimental Facility (slow extraction). No source in the Atlas
gives coordinates or a scale-bar plan for any of them.

### Geometry records edited

* `geometry:bnl-linac-930-building`: now linked to `accelerator:bnl-linac` (was a context building with no entity).
* `geometry:kek-linac-building`: now linked to `accelerator:kek-linac` (same reason; the earlier note said the linac had no record).
* `geometry:bnl-ags-booster-area`: method reworded; stays a context feature. The Booster is a new `unlocated[]` row on `map:brookhaven-national-laboratory`, because that OSM `place=locality` boundary is not a trace of the ring.

## For the integrator

* **SLAC**: when the colliders stream's records merge, add `{"id": "accelerator:spear"}` and `{"id": "accelerator:pep"}` entries to `accelerator:slac-linac` `feeds_accelerator_ids`, with sources already in the Atlas or the two new ones: `src:slac-grad-handbook` ("With the advent of colliding beam storage rings (SPEAR in 1972) and PEP (in 1980) … the SLAC linac also served as source and injector for electrons and positrons.") and `src:slac-linac-turns-50-2016` ("In 1972, the linac beams were for the first time injected into the SPEAR storage ring"; "From 1980 to 2008, SLAC's collider program continued with a series of three linac-driven particle smashers"). PEP ran 1980 to 1990 (SLAC history page, not cited here).
* **DESY**: PETRA is the stage between DESY II/III and HERA (40 GeV protons, 12 GeV electrons injected into HERA). When `accelerator:petra` lands, link it to `accelerator:hera` with `src:hera-collider-physics-klein-yoshida-2008` (Table 1: "Protons Source RFQ LINAC III DESY III PETRA HERA Ep 20 keV 750 keV 50 MeV 8 GeV 40 GeV 920 GeV Electrons Ee Source 150 keV LINAC II 450 MeV PIA 450 MeV DESY II 7 GeV PETRA 12 GeV HERA 27.5 GeV"); HERA's `injection_energy` is already recorded.
* **EIC** (hadron stream): the AGS and its injectors are reused ("the other RHIC ring, refurbished for its new mission, will receive ions accelerated by C-AD’s existing injector complex", BNL newsroom, `src:heavy-ions-rhic-final-collisions-2026`); `accelerator:ags` → EIC link to be added with that source. The `ags` → `rhic` link ends on 2026-02-06 (final run).
* **schema**: one line in `hepgraph/atlas/schema.py` (`injection_energy`); decide whether to add the A27 text above to the ontology.
* **Experiments** that could cite `beamline:cern-north-area` (not edited, other streams own them): `experiment:na62`, `experiment:na64`, `experiment:na48` (completed) and the proposed `experiment:ship`; COMPASS/AMBER and NA61/SHINE have no record on this branch.
* **M2 consumers**: `feeds_accelerator_ids` mixes strings and `{id, start, end}` objects in `atlas.json`; links with `end` in the past (ISR, LEP, Linac2) or a planned `start` (PIP-II, HL-LHC) must be filtered by the view's year.
* Generated bundles were rebuilt for checking and reverted (`git checkout -- static/atlas/generated`); `atlas.json` grows by about 15 kB (1 013 726 to 1 029 250 bytes; the 400 kB pilot-budget warning already existed).
* Pre-existing and left alone: `display-value-drift` on `beamline:lbnf` (60-120 GeV and the power range); Wikipedia sourcing on the SPEAR-era SLAC records outside this stream's files.

## Checks

* `python -m hepgraph.atlas.validate`: 0 errors, 1596 warnings, 4 informational, identical to the baseline (no new warnings; the diff of the sorted output is empty).
* `python -m hepgraph.atlas.build`: succeeds (generated bundles reverted).
* `.venv/bin/python -m pytest -q`: 689 passed, 139 skipped (database-backed tests).
* Every quote added was verified verbatim against the fetched page or PDF at the time of writing (`SourceText.classify` from `scripts/atlas_quote_check.py`); a final run of the checker on the changed files is recorded in the commit message of the log commit.
