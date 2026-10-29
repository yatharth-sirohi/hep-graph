# M5 and the coverage wave: all of ground-based HEP

Integration branch `atlas-next`, 2026-10-26 to 2026-10-28.

The owner asked for every direct-detection experiment ("LZ and LUX are all
present") and for "all of HEP covered". Amendment A26 set the scope: ground-based,
underground, underwater and in-ice experimental HEP across the energy, neutrino,
rare-process and cosmic frontiers, plus high-energy nuclear physics where it
shares facilities and methods. Space missions and gravitational-wave
observatories stay out.

## What changed

| | Release (main 6182106) | Now |
| --- | ---: | ---: |
| Experiments | 131 | 388 |
| Facilities | 48 | 100 |
| Results | 109 | 499 |
| Sources | 1,927 | 3,181 |
| Accelerators | 31 | 62 |

The wave ran as seven research streams plus follow-ups. Each stream owned its
facilities, topics and registry rows. Every value carries a verbatim quote from a
source fetched during the wave.

- **Direct dark matter** (85 experiments in all).
  - Xenon: XENON10/100, ZEPLIN-I/II/III, PandaX-I/II, XMASS.
  - Germanium: CDEX, CoGeNT.
  - Cryogenic: CDMS I.
  - NaI: DAMA/NaI and DAMA/LIBRA with their tests (ANAIS-112, COSINE-100), SABRE,
    KIMS, DM-Ice.
  - Bubble chambers: PICO, COUPP, PICASSO, SIMPLE.
  - Directional detectors.
  - Newer low-mass searches.
  - Ten new laboratories, including Y2L, Yemilab and SUPL.

  The DAMA story is told as its papers tell it. DAMA/LIBRA's modulation is
  "evidence"; CoGeNT's excess is an "anomaly"; ANAIS-112 is "incompatible with
  DAMA/LIBRA at 3.3σ". XLZD/DARWIN is left out until a design report names its
  host laboratory.
- **Colliders** (31): BES/BESIII, CLEO, KLOE, CMD/SND/KEDR, SPEAR (Mark I: the
  J/ψ and the τ), PEP, PETRA (TASSO, JADE, MARK-J, PLUTO, CELLO), DORIS (ARGUS),
  TRISTAN and UA4/UA5. Proposed FCC-ee, CEPC, ILC and CLIC appear as
  accelerators, worded exactly as their sources state their status.
- **Historic discoveries** (10): Cowan–Reines, the antiproton, the two-neutrino
  experiment, CP violation, the Ω⁻, the J particle, SLAC–MIT scaling, the Υ, IMB,
  and parity violation at Nevis. Each DOI was checked against the original paper.
- **Neutrinos** (41):
  - Reactor short-baseline and sterile searches.
  - CHOOZ.
  - CERN's beam experiments: CHORUS, NOMAD, CDHS, CHARM.
  - CCFR/NuTeV, JSNS², CCM.
  - Nucleon decay: Fréjus, NUSEX, Soudan 2, MACRO, KGF.
  - Double-beta decay: Heidelberg–Moscow, NEMO-3, SuperNEMO, CANDLES.
  - Direct mass: Mainz, Troitsk, ECHo, HOLMES.
- **Precision and antimatter** (31): the CERN Antiproton Decelerator experiments,
  E821, MuLan, PIONEER, the neutron EDM and lifetime experiments, TRIUMF and the
  NIST NCNR.
- **Cosmic frontier** (36):
  - CMB: SPT, BICEP/Keck, ACT, Simons Observatory.
  - Dark-energy surveys: DESI, DES, Rubin.
  - Cosmic rays: HiRes, AGASA, Tibet ASγ and others.
  - CMB-S4, recorded with DOE/NSF's own words: "can no longer support". DESI's
    result is recorded as a preference at 2.6–4.2σ, not a discovery.
- **Hadron and nuclear** (35): JLab (GlueX, CLAS12, Qweak, PREX/CREX, MOLLER),
  EIC/ePIC, COMPASS/AMBER, NA61, NA49/50/60, HERMES, FAIR, NICA and Mainz.
- **M5 data for the views:**
  - cosmic-ray muon flux (A27) for 15 underground sites;
  - accelerator chains and per-era energies (A30);
  - detector dimensions for the line-up (A31).

Errors corrected in existing data along the way:
- CJPL's depth (2400 m.w.e. → 6720);
- J-PARC's linac energy;
- the direction of the PEP-II feed;
- CNGS's primary beam;
- Homestake's dates, which had rested on Wikipedia and now rest on Davis's Nobel
  lecture and the 1998 paper;
- K2K's origin, which had been placed at the Belle II hall.

## How the experience improved, and why it is better

A student searching for LUX, DAMA, BESIII, the antiproton's discovery or DESI now
finds them, each with its dates, its site on the globe and its headline result
quoted from the abstract. The Atlas has gone from a showcase of 131 experiments to
roughly three times that, across the whole field, without giving up the rule that
every number traces to a source.

## Verified, and how

- The integrator re-read headline results against published values for each area.
  Examples:
  - Mainz m(νe) ≤ 2.3 eV;
  - NEMO-3 > 1.1×10²⁴ yr;
  - PSI nEDM (0.0 ± 1.1 ± 0.2)×10⁻²⁶ e·cm;
  - MuLan 2196980.3(2.2) ps;
  - DOIs for every historic discovery;
  - the LZ and CJPL muon fluxes.
- At merge the validator caught ID collisions and duplicate sources, all resolved:
  - JLab's SoLID and the BR2 reactor's SoLid were distinct records sharing one id.
  - The Aidala review and the ANAIS-112 paper had each been added twice.
- A machine check of every quote in the Atlas against its fetched source:
  - 6,518 verbatim, plus 278 matched in segments;
  - 60 missing, 19 near, 55 number flags.

  An independent verifier re-read the source for every one of those 134 items
  (`VERIFY_COVERAGE_WAVE.md`).
  - **Re-check:** missing fell from 60 to 11 and near from 19 to 9. Those 20 were
    verified by hand; publisher bot checks block a machine re-fetch.
  - **Checker misses:** most items were the checker's own misses (table cells,
    PDFs, landing pages), now repointed to the exact location.
  - **Substantive errors** (34 items):
    - PandaX-4T's limit minimum sat at 30 GeV/c². The arXiv listing says 30, but
      the paper's abstract, results and conclusion all say 40, and the
      integrator re-read the paper and confirmed it.
    - Homestake's end had been read as 1994, which is only the end of one paper's
      data set; it is now "late 1990s", bounded 1997–2001, per Davis.
    - ESSnuSB's technology and physics goal were not in their quotes.
    - ProtoDUNE's tagger description went beyond its quote.
    - Notes and dates for JADE, MARK J, TASSO and VEPP-2000 were wrong.
    - Country counts for Daya Bay and GALLEX/GNO came from Wikipedia; one of the
      Daya Bay countries had no author affiliation at all.
  - **Left for a later pass:** 48 Wikipedia source records from earlier phases
    are still cited by 107 records, and Mu2e's member counts rest on INSPIRE's
    description.

## Known limits

- **Coordinates:** new sites are campus-grade approximate points unless a paper
  publishes a coordinate. No hall-level positions were invented.
- **INSPIRE ids:** none were set, because INSPIRE belongs to the supervised importer.
- **Bundle size:** `atlas.json` is 2.4 MB raw and 435 KB gzipped, inside the
  build's limits (2.5 MB / 500 KB). Measured time to first markers:
  - about 0.65 s locally;
  - about 2.4 s on a simulated fast-4G link.

  The next saving would be to load plain summaries lazily, as technical summaries
  already are.
