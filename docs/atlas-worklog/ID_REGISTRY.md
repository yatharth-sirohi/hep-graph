# HEP Atlas id registry and ownership (pilot wave, 2026-09-16)

Rule: the owner creates the file; everyone else only references the id.
If you need an id that is not listed, create it in your own partition using
the slug conventions in docs/HEP_ATLAS_ONTOLOGY.md §1 and append it here.
Source ids (`src:`) are always prefixed with your program slug
(`src:dune-…`, `src:cern-…`, `src:t2k-…`) so they never collide.

| id | owner |
| --- | --- |
| facility:fermilab, site:fermilab-main-campus, site:fermilab-dune-near-detector-hall, accelerator:fermilab-linac, accelerator:fermilab-booster, accelerator:fermilab-main-injector, accelerator:fermilab-recycler, accelerator:fermilab-pip-ii, accelerator:fermilab-tevatron, beamline:lbnf, beamline:numi, beamline:bnb | fermilab-dune |
| facility:surf, site:surf-4850-level-dune-far-detector, site:surf-surface-campus | fermilab-dune |
| experiment:dune, detector:dune-far-detector-1, detector:dune-far-detector-2, detector:dune-near-detector, detector:protodune-*, collaboration:dune | fermilab-dune |
| experiment:nova, experiment:minos, experiment:minos-plus, experiment:minerva, experiment:microboone, experiment:sbnd, experiment:icarus, experiment:miniboone, facility:soudan-underground-laboratory, site:soudan-*, site:ash-river-nova-far-detector, detector:nova-*, detector:minos-*, detector:microboone, detector:sbnd, detector:icarus-t600, detector:miniboone, collaboration:nova, collaboration:minos, collaboration:minerva, collaboration:microboone, collaboration:sbnd, collaboration:icarus, collaboration:sbn, collaboration:miniboone | fermilab-neutrino-other |
| facility:cern, site:cern-meyrin, site:cern-point-1-atlas, accelerator:lhc, accelerator:sps, accelerator:ps, accelerator:psb, accelerator:linac4, accelerator:lep, accelerator:isr, accelerator:hl-lhc (as upgrade of lhc, optional) | cern-atlas |
| experiment:atlas, detector:atlas, collaboration:atlas | cern-atlas |
| experiment:cms, detector:cms, collaboration:cms, site:cern-point-5-cms | cern-cms |
| experiment:ua1, experiment:ua2, detector:ua1, detector:ua2, collaboration:ua1, collaboration:ua2, site:cern-sps-lss5 (UA1), site:cern-sps-lss4 (UA2), results of UA1/UA2 | historic-cern |
| facility:j-parc, site:j-parc-*, accelerator:j-parc-linac, accelerator:j-parc-rcs, accelerator:j-parc-main-ring, beamline:j-parc-neutrino, experiment:t2k, detector:nd280, detector:ingrid, collaboration:t2k, experiment:k2k, collaboration:k2k, facility:kek (as the K2K source), beamline:kek-neutrino | japan-neutrino |
| facility:kamioka-observatory, site:kamioka-mozumi-mine-super-kamiokande, site:kamioka-hyper-kamiokande-tochibora, experiment:super-kamiokande, detector:super-kamiokande, collaboration:super-kamiokande, experiment:hyper-kamiokande, detector:hyper-kamiokande, collaboration:hyper-kamiokande, experiment:kamiokande, experiment:kamland (optional) | japan-neutrino |
| facility:amundsen-scott-south-pole-station, site:south-pole-icecube, experiment:icecube, detector:icecube, detector:icecube-deepcore, detector:icetop, collaboration:icecube, experiment:icecube-gen2, experiment:icecube-upgrade, experiment:amanda | icecube |
| experiment:lz, detector:lz, collaboration:lz, site:surf-davis-campus-lz, experiment:lux (lineage), experiment:zeplin-iii (lineage) | dark-matter |
| facility:kek (shared: japan-neutrino creates facility:kek; flavor creates the rest), site:kek-tsukuba-belle-ii, accelerator:superkekb, accelerator:kekb, experiment:belle-ii, detector:belle-ii, collaboration:belle-ii, experiment:belle, detector:belle, collaboration:belle | flavor  (facility:kek → japan-neutrino) |
| data/atlas/institutions/*, data/atlas/memberships/*, data/atlas/people/* | membership-lead |
| data/atlas/topics/topics.json | topics-method |
| data/atlas/coverage/registry.json | orchestrator (seeded), leads append |

## Wave 3 — v1.0 coverage expansion (2026-09-17)

Same rule: the owner creates the file, everyone else references the id. Owner
names are the `owner` values in `data/atlas/coverage/<owner>.json`; each lead
edits only its own coverage file, its own worklog, and the entities below.
Source ids are prefixed with the owner slug (`src:cevns-…`, `src:axions-…`).
Shared laboratories are created by `facilities`; an experiment lead that needs
one of them references the id and reports the dangling reference until the
facilities lead lands (expected during integration, not an error to fix by
creating your own copy).

| id | owner |
| --- | --- |
| facility:brookhaven-national-laboratory, site:bnl-upton-campus, site:bnl-rhic-ip6-star, site:bnl-rhic-ip8-phenix-sphenix, accelerator:rhic, accelerator:ags, accelerator:bnl-linac (optional), accelerator:bnl-booster (optional) | facilities |
| facility:slac, site:slac-menlo-park-campus, site:slac-pep-ii-ir2-babar, site:slac-slc-collider-hall-sld, accelerator:slac-linac, accelerator:pep-ii, accelerator:slc, accelerator:pep (optional) | facilities |
| facility:desy, site:desy-hamburg-campus, site:desy-hera-north-hall-h1, site:desy-hera-south-hall-zeus, accelerator:hera, accelerator:petra (optional) | facilities |
| facility:jefferson-lab, site:jlab-newport-news, accelerator:cebaf | facilities |
| facility:oak-ridge-national-laboratory, site:ornl-sns-neutrino-alley, accelerator:sns | facilities |
| facility:los-alamos-national-laboratory, site:lanl-lansce, accelerator:lansce (LAMPF) | facilities |
| facility:argonne-national-laboratory, site:argonne-campus, accelerator:zgs (optional, historical) | facilities |
| facility:psi, site:psi-villigen, accelerator:psi-hipa | facilities |
| facility:snolab, site:snolab-underground-lab (2 km level), site:snolab-sno-cavern (optional if a distinct point is sourced) | facilities |
| facility:modane-underground-laboratory (LSM), site:lsm-frejus | facilities |
| facility:canfranc-underground-laboratory (LSC), site:lsc-canfranc | facilities |
| facility:cjpl, site:cjpl-i, site:cjpl-ii | facilities |
| facility:boulby-underground-laboratory, site:boulby-mine | facilities |
| facility:lngs exists (dark-matter); new sites site:lngs-hall-a, site:lngs-hall-c | facilities |
| facility:cern exists; new sites site:cern-point-2-alice, site:cern-point-8-lhcb, site:cern-ti12-faser, site:cern-ti18-snd-lhc (LHCf places at site:cern-point-1-atlas, TOTEM at site:cern-point-5-cms, MoEDAL at site:cern-point-8-lhcb); experiment/detector/collaboration alice, lhcb, faser, snd-lhc, lhcf, moedal, totem | colliders-lhc |
| site:fermilab-cdf-collision-hall-b0, site:fermilab-d0-collision-hall; experiment/detector/collaboration cdf, d0, sld, babar, h1, zeus | colliders-historical |
| experiment/detector/collaboration karmen (site under facility:isis? create facility:isis-neutron-source + site:isis-rutherford-appleton), lsnd (site:lanl-lansce via facilities), opera (site:lngs-hall-c via facilities; beamline:cngs), donut (site:fermilab-donut-hall or facility:fermilab campus) | accelerator-neutrino-historical |
| kamland (site:kamioka-kamland under facility:kamioka-observatory; detector:kamland shared with kamland-zen), daya-bay (facility:daya-bay-reactor-neutrino-lab + sites), reno (facility:yonggwang-hanbit-reactor-site + sites), double-chooz (facility:chooz + sites), juno (facility:juno-jiangmen + site), borexino (site:lngs-hall-c via facilities), sno and sno-plus (site:snolab-sno-cavern or snolab-underground-lab via facilities), gallex-gno (site:lngs-hall-a via facilities), sage (facility:baksan-neutrino-observatory + site), homestake (site:surf-homestake-davis-cavern-1960s or facility:surf) | reactor-solar-neutrino |
| katrin (facility:kit-karlsruhe + site), project-8, legend (LNGS via facilities; site:snolab for LEGEND-1000 if sourced), gerda, majorana-demonstrator (site:surf-davis-campus-* — reuse existing site:surf-davis-campus-lz only if the source says the same hall; else create site:surf-4850-davis-campus-majorana), exo-200 (facility:wipp + site), nexo, kamland-zen (references detector:kamland from reactor-solar-neutrino), cuore, cupid, next (LSC via facilities) | neutrino-mass-0vbb |
| km3net (facility:km3net-arca-capo-passero, facility:km3net-orca-toulon or one facility with two sites), antares (site:antares-toulon), baikal-gvd (facility:baikal-deep-underwater-neutrino-telescope + site), anita (facility:mcmurdo-ldb or note-only), rno-g (facility:summit-station-greenland + site), p-one (site:cascadia-basin-p-one), ara (site under facility:amundsen-scott-south-pole-station), arianna (site:moores-bay-arianna), grand | astro-neutrino |
| xenon1t, xenonnt (LNGS hall B exists), pandax-4t (CJPL via facilities), darkside-50, darkside-20k (LNGS hall C via facilities), deap-3600 (SNOLAB via facilities) | dm-noble-liquid |
| supercdms (SNOLAB via facilities), cdms-ii (site:soudan-cdms under facility:soudan-underground-laboratory), sensei (site under facility:fermilab MINOS hall: site:fermilab-minos-near-detector-hall — check if fermilab-neutrino-other already created one), damic (SNOLAB), damic-m (LSM via facilities), news-g (SNOLAB), cresst (LNGS hall A), edelweiss (LSM) | dm-cryogenic-low-threshold |
| admx (facility:university-of-washington-cenpa + site), haystac (facility:yale-wright-lab + site), cast (site:cern-cast-sr8 under facility:cern), iaxo (DESY via facilities; planned), alps-ii (site:desy-hera-hall-north — coordinate with facilities: reference site:desy-hera-north-hall-h1), abracadabra (facility:mit + site), dmradio (facility:slac via facilities) | axions |
| muon-g-2 (site:fermilab-mc-1-muon-campus under facility:fermilab), mu2e (site:fermilab-mu2e-hall), meg, meg-ii, mu3e (site:psi-villigen via facilities; accelerator:psi-hipa), comet (site:j-parc-hadron-hall under facility:j-parc) | muons |
| na62, na48 (site:cern-ecn3-north-area under facility:cern; accelerator:sps exists), na64 (site:cern-ehn1-h4 — note site:cern-neutrino-platform-ehn1 exists), ktev (site:fermilab-ktev-hall), e949 (site:bnl-ags via facilities: site:bnl-upton-campus), seaquest and darkquest (site:fermilab-nm4-hall), ship (site:cern-ecn3-north-area, planned), mathusla (planned; site:cern-point-5-cms surface, no new site unless sourced), koto (site:j-parc-hadron-hall — coordinate: muons creates it; reference) | fixed-target |
| coherent (site:ornl-sns-neutrino-alley via facilities), conus (facility:brokdorf-nuclear-power-plant / Leibstadt for CONUS+ — one experiment record, alias CONUS+), nucleus (facility:chooz — reference reactor-solar-neutrino's facility:chooz, or note), ricochet (facility:ill-grenoble + site) | cevns |
| pierre-auger-observatory (facility:pierre-auger-observatory + site:malargue), telescope-array (facility:telescope-array-utah + site), hawc (facility:sierra-negra + site), lhaaso (facility:lhaaso-daocheng + site), ctao (facility:roque-de-los-muchachos-observatory + facility:ctao-south-paranal + sites), veritas (facility:fred-lawrence-whipple-observatory + site), magic (site under roque-de-los-muchachos), h-e-s-s (facility:hess-khomas-highland + site) | cosmic-gamma |
| star, phenix, sphenix (sites and RHIC via facilities); experiment/detector/collaboration records | heavy-ions |
