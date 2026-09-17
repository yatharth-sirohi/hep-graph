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
