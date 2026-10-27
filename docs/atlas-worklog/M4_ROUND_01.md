# M4 — Charts: going underground, the energy frontier, scale, results

Integration branch `atlas-next`, 2026-10-26. Three implementation streams and one
data stream (cosmic-ray muon flux, A27), plus integrator checks.

## What changed

- **Going underground** (`#/view/underground`). Fifteen underground-laboratory
  sites are plotted as depth in m.w.e. against cosmic-ray muon flux, on a log
  axis. Units are converted to cm⁻² s⁻¹ with the A27 factors, which the method
  states.
  - The integrator checked every point against its record. The range runs from
    WIPP (4.77×10⁻⁷ at 1585 m.w.e.) and Canfranc (5.26×10⁻⁷ at 2450) to SNOLAB
    (3.31×10⁻¹⁰ at 6000) and CJPL (3.0–3.5×10⁻¹⁰ at 6720).
  - The flux data corrected an old error: CJPL's depth had been recorded as
    2400 m.w.e. That figure is its rock cover, which is about 6720 m.w.e.
- **The energy frontier** (`#/view/energy-frontier`). Each machine is drawn as a
  track: one point per dated era, joined by a line.
  - The first version plotted each machine's latest energy at its first year, for
    example the LHC at 13.6 TeV in 2010. That was sent back and fixed. The LHC now
    reads 7 → 13 → 13.6 TeV across 2010, 2015 and 2022.
  - A machine whose starting energy the Atlas lacks gets a dashed ring and says so.
- **Scale comparisons.**
  - **"Compare with…" on any local map** lays another facility's footprint over the
    map at true scale. Each vertex is moved by its distance and bearing on the
    sphere, not by a shift in latitude and longitude. The overlay can also go over
    the reader's own location: that is asked only on a click, is never stored or
    put in the address, and turns the basemap off while in use.
  - **Measured:** the LHC laid over Fermilab's map is 26.59 km around against the
    scale bar.
  - **Detector line-up** (`#/view/detector-scale`): 14 detectors at one linear
    scale beside a 1.8 m person, with IceCube in its own panel. Every dimension is
    a quoted spec.
- **Results as a story** (`#/view/results-story`). Every result is placed in
  question lanes. A mark's form comes from the record's result type; its
  significance is printed verbatim, never inferred.
- **WIMP exclusion plot** (`#/view/limits/wimp-si`).
  - LZ's 2022 and 2024 limit curves come from HEPData, with 40 and 26 points, not
    thinned. Their minima match the abstracts: 9.2×10⁻⁴⁸ cm² at 36 GeV and
    2.2×10⁻⁴⁸ cm² at 40 GeV.
  - XENONnT and PandaX-4T publish no curve on HEPData, so each appears as one
    hollow diamond at the minimum its abstract states, labelled as such.

## How the experience improved, and why it is better

These are the figures every particle-physics student meets in their first course,
now drawn only from the Atlas's own sourced records. Every point opens its record,
and every chart states its inputs. A student can see that SNOLAB's rock cuts the
muon rate about a thousand-fold compared with Canfranc's. A researcher can lay
the LHC over Iowa City. An instructor can show twenty years of WIMP searches on
one plot.

## Verified, and how

- The integrator checked every underground point, the LHC, LEP, Tevatron and RHIC
  frontier tracks, the overlay's length, and the limit plot's diamonds (read back
  through the log axes).
- One data simplification is being fixed. LEP2's era carries only its top energy,
  so LEP is drawn at 209 GeV in 1995; in fact LEP2's energy rose year by year from
  about 130 GeV and reached 209 GeV only in 2000. The follow-up stream is adding
  the per-year energies.
- One merge bug was found and fixed: picking a comparison did not redraw a map
  whose proton player was loaded.
