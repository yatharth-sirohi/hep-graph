# M2 — Beams through the Earth, and Follow the proton

Integration branch `atlas-next`, 2026-10-26. Two implementation streams, one data
stream (accelerator chains), integrator checks.

## What changed

### Beam through the Earth (`#/view/beam-section/<beamline>[~row]`)

This is the first view on the new view framework. Each view is one module plus one
registry line, loaded only when its route opens.

For every sourced neutrino baseline, the view draws:

- a cross-section of the Earth along the great circle between the two recorded
  site coordinates;
- the straight chord the neutrinos travel;
- both sites, named;
- each far detector's recorded depth;
- a true-scale Earth inset;
- the dip at true size;
- a zoomed section with its vertical stretch stated (×20, or ×50 for the 250–295 km
  beams).

A method table gives every number's formula and inputs, with a worst-case
uncertainty split into Earth-radius and coordinate parts. Each beamline and
experiment panel links to the view, and search reaches it.

The integrator computed these independently from the site coordinates. They match
the view exactly:

| Beam | Dip below horizontal | Deepest point | Chord | Light time |
| --- | ---: | ---: | ---: | ---: |
| DUNE / LBNF | 5.79° | 32.5 km | 1285.4 km | 4.29 ms |
| NuMI → Soudan (MINOS) | 3.31° | 10.6 km | 735.0 km | 2.45 ms |
| NuMI → Ash River (NOvA) | 3.65° | 12.9 km | 811.1 km | 2.71 ms |
| CNGS | 3.29° | 10.5 km | 730.9 km | 2.44 ms |
| T2K / T2HK | 1.32° | 1.70 km | 294.2 km | 0.98 ms |
| K2K | 1.12° | 1.22 km | 249.5 km | 0.83 ms |

As a cross-check, the computed NuMI dip (57.7 mrad) agrees with the beamline's
published 58 mrad.

### Accelerator chains and stage energies (data, amendment A30)

- Dated feed links and per-era energies for the injector chains at CERN, Fermilab,
  J-PARC, BNL, KEK, SLAC and DESY. Examples:
  - Linac2 handed over to Linac4 in 2020.
  - The PS Booster's 1.4 GeV era ran 1999–2018.
  - LHC Runs 1, 2 and 3 at 7, 13 and 13.6 TeV.
- Three errors fixed in existing records:
  - J-PARC's linac was listed at the wrong energy. It has run at 400 MeV since
    2014, and at 181 MeV before.
  - The PEP-II link pointed the wrong way.
  - The CNGS primary beam read "muon neutrino" instead of 400 GeV/c protons.
- A new `injection_energy` spec key.

### Follow the proton (local maps of CERN, Fermilab, J-PARC, BNL, KEK, SLAC)

- **What it plays:** the injector chain of the timeline year, read from the dated
  feed links (never hard-coded).
- **Each step:** lights the stage's drawn ring or line, runs a dot once round it,
  and shows the energy in and out, the particle species (H⁻ in the linacs), and a
  source link per number.
- **Undrawn stages:** a stage the map does not draw (Linac2, the ISR, transfer
  lines) is named as "not drawn", with the map's own reason; no path is guessed.
- **Controls and sharing:** `?proton=N` shares a step. An energy ladder lists
  every stage on a log scale. Keyboard and reduced motion are supported.
- **Checked:** the integrator hand-checked the PSB in 2015 (50 MeV in, 1.4 GeV
  out), the LHC in 2015 (6.5 TeV per beam, marked as derived from 13 TeV) and the
  J-PARC RCS in 2010 (181 MeV in, 3 GeV out).

## How the experience improved, and why it is better

The plan called Beams through the Earth "the single most 'damn' visual the data
already supports". A student can now see that DUNE's beam leaves Illinois pointing
5.8° into the ground and passes 32 km under Iowa and Minnesota, with every number
derived from two coordinates on the page. Follow the proton turns CERN's map, a
picture of rings, into the machine it is: the beam handed from ring to ring,
gaining energy at each step, with the year deciding which linac starts it.

## Verified, and how

- The integrator independently computed all seven baselines (table above).
- Browser walk of the DUNE and NuMI views, with 0 console errors.
- The stream's checks:
  - view tests on three engines;
  - a CERN chain test (Linac2 in 2015, Linac4 in 2021);
  - accessibility with 0 violations.
- One merge bug was found and fixed. The proton player's no-redraw shortcut ignored
  overlay and selection changes, so Back after selecting a feature kept the drawer
  open on maps with a chain. A full render now clears the shortcut's key first.
