# Stream log: discoveries (coverage wave, stream c3)

Owner tag `discoveries`. Branch `atlas-c3-discoveries`. Registry rows: `data/atlas/coverage/discoveries.json`. Every date and coordinate below was read on 2026-10-26; each quote is copied verbatim from the cited page or PDF text (a script checked every quote in every record against the fetched text before the records were written).

## Scope

Historic discovery experiments at a fixed facility that were missing from the Atlas: the nine in the brief plus two optional additions.

* Cowan-Reines neutrino detection (Savannah River, 1955-56).
* Antiproton (Bevatron, 1955).
* Two-neutrino experiment (AGS, 1962).
* CP violation in K0 decay (AGS, 1963-64).
* Omega-minus (AGS 80-inch bubble chamber, 1963-64).
* E598, the Brookhaven side of the J-particle discovery (AGS, 1974).
* SLAC-MIT deep inelastic scattering (End Station A, 1967-73).
* E288, the upsilon (Fermilab, 1977).
* IMB (Ohio salt mine, 1982-91): the SN 1987A burst and the proton-decay limits.
* Optional, added: the Garwin-Lederman-Weinrich parity experiment (Nevis, 1957) and the Cosmotron accelerator (BNL, 1952-66).

Result typing follows the paper's own title (A16): eight results are typed `observation` (titles say "Observation", "Observations" or "Observed"), one `evidence` (CP violation, title "Evidence"), one `first_detection` (Cowan-Reines, title "Detection") and one `limit` (IMB-3); the Nobel discovery citation is carried in `why_it_matters` and notes. This matches the existing UA1 W/Z records. If the owner wants `discovery` typing for tours, each record needs a claim quote from a source that says "discover" (the Nobel page), which A16 does not accept as a claim source; this is a decision for the owner, not an oversight.

## Entities written

### Facilities (4)

| id | status | start | end | site / facility |
| --- | --- | --- | --- | --- |
| `facility:imb-fairport-mine` | decommissioned | 1982 | 1991 | site:imb-fairport-mine |
| `facility:lawrence-berkeley-national-laboratory` | active | 1931 | ongoing | site:lbnl-berkeley-campus |
| `facility:nevis-laboratories` | active | 1950 | ongoing | site:nevis-laboratories |
| `facility:savannah-river-site` | active | 1951 | ongoing | site:savannah-river-site |

### Sites (4)

| id | facility | lat, lon | precision | kind / confidence |
| --- | --- | --- | --- | --- |
| `site:imb-fairport-mine` | facility:imb-fairport-mine | 41.7519155, -81.2723464 | 5000 m | campus / approximate |
| `site:lbnl-berkeley-campus` | facility:lawrence-berkeley-national-laboratory | 37.8769588, -122.2456303 | 1000 m | campus / approximate |
| `site:nevis-laboratories` | facility:nevis-laboratories | 41.0317408, -73.866269 | 500 m | campus / approximate |
| `site:savannah-river-site` | facility:savannah-river-site | 33.2122041, -81.6223727 | 20000 m | campus / approximate |

### Accelerators (2)

| id | status | start | end | site / facility |
| --- | --- | --- | --- | --- |
| `accelerator:bevatron` | decommissioned | 1954-01 | 1993 | site:lbnl-berkeley-campus |
| `accelerator:cosmotron` | decommissioned | 1952 | 1966 | site:bnl-upton-campus |

### Collaborations (see integrator note) (3)

| id | status | start | end | site / facility |
| --- | --- | --- | --- | --- |
| `collaboration:e288` | completed | 1975 | 1977-09 (approx) | site:fermilab-main-campus |
| `collaboration:imb` | completed | 1982 | 1991 | site:imb-fairport-mine |
| `collaboration:slac-mit` | completed | 1967 | 1973 | site:slac-menlo-park-campus |

### Experiments (10)

| id | status | start | end | site / facility |
| --- | --- | --- | --- | --- |
| `experiment:ags-e598-j-particle` | completed | 1972-04 (earliest 1972-03; latest 1972-05; "spring of 1972"; approx) | 1974-11-07 | facility:brookhaven-national-laboratory |
| `experiment:ags-k2-cp-violation` | completed | 1963 | 1964-07-10 | facility:brookhaven-national-laboratory |
| `experiment:ags-omega-minus` | completed | 1963-06 | 1964-02-11 | facility:brookhaven-national-laboratory |
| `experiment:ags-two-neutrino` | completed | 1960-07 (latest 1962-06; approx) | 1962-07-01 | facility:brookhaven-national-laboratory |
| `experiment:bevatron-antiproton` | completed | 1955-08 | 1955-11-01 | facility:lawrence-berkeley-national-laboratory |
| `experiment:cowan-reines-neutrino` | completed | 1955-10 (earliest 1955-09; latest 1955-11; "Fall of 1955"; approx) | 1956-06 (latest 1956-06; approx) | facility:savannah-river-site |
| `experiment:fermilab-e288` | completed | 1974-02 | 1977-09 (latest 1977-09; approx) | facility:fermilab |
| `experiment:imb` | completed | 1982 | 1991 | facility:imb-fairport-mine |
| `experiment:nevis-parity-muon-decay` | completed | 1957-01 | 1957-02-15 | facility:nevis-laboratories |
| `experiment:slac-mit-deep-inelastic-scattering` | completed | 1967-08 | 1973 | facility:slac |

### Results (11)

| id | type | date (kind) | experiment |
| --- | --- | --- | --- |
| `result:ags-two-neutrinos-observation-1962` | observation | 1962-07-01 (publication) | experiment:ags-two-neutrino |
| `result:aubert-ting-j-particle-observation-1974` | observation | 1974-12-02 (publication) | experiment:ags-e598-j-particle |
| `result:barnes-omega-minus-observation-1964` | observation | 1964-02-24 (publication) | experiment:ags-omega-minus |
| `result:chamberlain-segre-antiproton-observation-1955` | observation | 1955-11-01 (publication) | experiment:bevatron-antiproton |
| `result:christenson-cronin-fitch-turlay-k2-2pi-evidence-1964` | evidence | 1964-07-27 (publication) | experiment:ags-k2-cp-violation |
| `result:cowan-reines-neutrino-detection-1956` | first_detection | 1956-06 (announcement) | experiment:cowan-reines-neutrino |
| `result:garwin-lederman-weinrich-parity-observation-1957` | observation | 1957-02-15 (publication) | experiment:nevis-parity-muon-decay |
| `result:herb-e288-upsilon-observation-1977` | observation | 1977-06-30 (announcement) | experiment:fermilab-e288 |
| `result:imb-3-nucleon-decay-limits-1999` | limit | 1999-02-10 (publication) | experiment:imb |
| `result:imb-sn1987a-neutrino-burst-observation-1987` | observation | 1987-04-06 (publication) | experiment:imb |
| `result:slac-mit-bjorken-scaling-observation-1969` | observation | 1968-08 (announcement) | experiment:slac-mit-deep-inelastic-scattering |

## The URL and quote behind every date and coordinate

#### `facility:imb-fairport-mine`

* IMB detector operating: active, 1982 to 1991 (verified) - https://www.aps.org/about/news/2024/08/morton-salt-mine-historic-site ; https://www.aps.org/apsnews/2024/10/underground-discovery-particle-physics - "IMB was an 8,000 ton Cherenkov detector — a device able to spot a form of electromagnetic radiation that is used for particle identification — that operated between 1982 and 1991."
* IMB run ended: decommissioned, 1991 to n/a (verified) - https://www.aps.org/apsnews/2024/10/underground-discovery-particle-physics - "IMB’s run ended in 1991, but its impact continues today."

#### `facility:lawrence-berkeley-national-laboratory`

* founded (Radiation Laboratory): active, 1931 to n/a (approximate) - https://history.lbl.gov/1930s/ - "On August 26, 1931, he committed to Lawrence the Civil Engineering Testing Laboratory, an empty building adjacent to Le Conte Hall which featured substantial concrete flooring, strong enough to support an 80-ton magnet."

#### `facility:nevis-laboratories`

* cyclotron in use: active, 1950 to n/a (approximate) - https://www.nobelprize.org/uploads/2018/06/lederman-lecture.pdf - "In 1950, John Tinlot and I had been pondering how to get pions into the cloud chamber."

#### `facility:savannah-river-site`

* site construction: construction, 1951 to 1954 (verified) - https://public.srs.gov/about/ - "Site construction begins."
* production reactors in operation: active, 1954 to n/a (approximate) - https://public.srs.gov/about/ - "P, L, K Reactors and F Canyon startup."

#### `site:imb-fairport-mine`

* coordinates 41.7519155, -81.2723464 (campus, approximate, 5000 m) - https://nominatim.openstreetmap.org/search?format=jsonv2&q=Fairport+Harbor+Ohio ; https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.58.1494 - ""osm_id":181991,"lat":"41.7519155","lon":"-81.2723464""
* depth_mwe 1570 m water equivalent - https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.58.1494 - "at a depth of 1570 m water equivalent"
* depth_rock about 610 m (nearly 2,000 feet) - https://www.aps.org/about/news/2024/08/morton-salt-mine-historic-site - "Located nearly 2,000 feet underground in the Fairport Harbor Morton Salt Mine"

#### `site:lbnl-berkeley-campus`

* coordinates 37.8769588, -122.2456303 (campus, approximate, 1000 m) - https://nominatim.openstreetmap.org/search?format=jsonv2&q=Lawrence+Berkeley+National+Laboratory - ""osm_id":502495343,"lat":"37.8769588","lon":"-122.2456303""

#### `site:nevis-laboratories`

* coordinates 41.0317408, -73.866269 (campus, approximate, 500 m) - https://nominatim.openstreetmap.org/search?format=jsonv2&q=136+South+Broadway%2C+Irvington%2C+NY+10533 - ""osm_id":1387951801,"lat":"41.0317408","lon":"-73.8662690""

#### `site:savannah-river-site`

* coordinates 33.2122041, -81.6223727 (campus, approximate, 20000 m) - https://nominatim.openstreetmap.org/search?format=jsonv2&q=Savannah+River+Site - ""osm_id":20818263,"lat":"33.2122041","lon":"-81.6223727""

#### `accelerator:bevatron`

* operation: active, 1954-01 to 1993 (approximate) - https://history.lbl.gov/1950s/ ; https://elementsarchive.lbl.gov/2019/06/13/the-bevatron-40-years-of-science/ - "Construction was completed in January 1954 and the new machine, a synchrotron designed to accelerate protons up to energies of 6.5 billion electron volts, then designated BeV (now universally known as GeV), was christened the “Bevatron.”"
* decommissioned: decommissioned, 1993 to n/a (approximate) - https://elementsarchive.lbl.gov/2019/06/13/the-bevatron-40-years-of-science/ - "a particle accelerator that operated from 1954 to 1993"

#### `accelerator:cosmotron`

* commissioning: commissioning, 1952 to 1953 (approximate) - https://www.bnl.gov/about/history/accelerators.php - "Cosmotron (1952-1966)"
* operation: active, 1953 to 1966 (verified) - https://www.bnl.gov/about/history/accelerators.php ; https://www.bnl.gov/75/timeline.php - "The machine reached its full design energy of 3.3 GeV in 1953."
* decommissioned: decommissioned, 1966 to n/a (verified) - https://www.bnl.gov/about/history/accelerators.php - "After 14 years of service to the physics community, the Cosmotron ceased operation in 1966 and was dismantled in 1969."

#### `collaboration:e288`

* collaboration: active, 1975 to 1977-09 (approx) (approximate) - https://www.nobelprize.org/uploads/2018/06/lederman-lecture.pdf - "the originally proposed pair experiment got underway in 1975"
* completed: completed, 1977-09 (approx) to n/a (approximate) - https://www.nobelprize.org/uploads/2018/06/lederman-lecture.pdf - "By September, with 30,000 events, the enhancement was resolved into three clearly separated peaks"

#### `collaboration:imb`

* collaboration: active, 1982 to 1991 (approximate) - https://www.aps.org/about/news/2024/08/morton-salt-mine-historic-site - "IMB was an 8,000 ton Cherenkov detector — a device able to spot a form of electromagnetic radiation that is used for particle identification — that operated between 1982 and 1991."
* completed: completed, 1991 to n/a (approximate) - https://www.aps.org/apsnews/2024/10/underground-discovery-particle-physics - "IMB’s run ended in 1991, but its impact continues today."

#### `collaboration:slac-mit`

* collaboration: active, 1967 to 1973 (approximate) - https://www.nobelprize.org/prizes/physics/1990/press-release/ ; https://www.slac.stanford.edu/pubs/slacpubs/5500/slac-pub-5724.pdf - "Collaboration between SLAC and MIT started at the beginning of 1967"
* completed: completed, 1973 to n/a (approximate) - https://www.slac.stanford.edu/pubs/slacpubs/5500/slac-pub-5724.pdf - "inelastic electron-nucleon scattering experiments conducted between 1967 and 1973 at the Stanford"
* formation 1967 - https://www.nobelprize.org/prizes/physics/1990/press-release/ - "Collaboration between SLAC and MIT started at the beginning of 1967"

#### `experiment:ags-e598-j-particle`

* proposal: proposed, 1972-04 (earliest 1972-03; latest 1972-05; "spring of 1972"; approx) to 1974-04 (approximate) - https://www.nobelprize.org/uploads/2018/06/ting-lecture.pdf - "it gives some of the reasons I presented, in the spring of 1972, for performing an e + e experiment in a proton beam rather than in a photon beam"
* discovery run: active, 1974-04 to 1974-11-07 (verified) - https://www.nobelprize.org/uploads/2018/06/ting-lecture.pdf - "In April 1974, we finished the set-up of the experiment and started bringing an intense-proton beam into the area."
* completed: completed, 1974-11-07 to n/a (approximate) - https://www.nobelprize.org/uploads/2018/06/ting-lecture.pdf - "On Thursday, 7 November, we made a major change in the spectrometer (see Fig. 13) to start the new experiment to search for more particles."
* role host at facility:brookhaven-national-laboratory - https://www.nobelprize.org/uploads/2018/06/ting-lecture.pdf - "Figure 4 shows the layout of the slow-extracted intense proton beam from the Alternating Gradient Synchrotron (AGS) at Brookhaven, during the period 1973-1974. Our experiment (No. 598) was located in a specially designed beam line (the A-line)."

#### `experiment:ags-k2-cp-violation`

* discovery run: active, 1963 to 1964-07-10 (approximate) - https://www.bnl.gov/bnlweb/history/nobel/1980.php ; https://www.nobelprize.org/uploads/2018/06/fitch-lecture.pdf - "the opposite of what they had expected to find when they began their experiment in 1963"
* completed: completed, 1964-07-10 to n/a (approximate) - https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.13.138 - "(Received 10 July 1964)"
* role host at facility:brookhaven-national-laboratory - https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.13.138 - "were produced at the Brookhaven AGS in an internal Be target bombarded by 30-BeV protons"

#### `experiment:ags-omega-minus`

* 80-inch chamber initial run: active, 1963-06 to 1964-02-11 (approximate) - https://www.bnl.gov/about/history/accelerators.php - "When its first photograph of particle interactions was taken in June 1963, the 80-inch bubble chamber was the largest such detector in the world."
* completed: completed, 1964-02-11 to n/a (approximate) - https://cerncourier.com/nineteen-sixty-four/ - "11 February A Brookhaven National Laboratory team submits “Observation of a hyperon with strangeness minus three” to Physical Review Letters"
* role host at facility:brookhaven-national-laboratory - https://www.bnl.gov/about/history/accelerators.php - "a team of researchers led by future Laboratory director Nicholas Samios used the 80-inch to discover the omega-minus particle."

#### `experiment:ags-two-neutrino`

* discovery run: active, 1960-07 (latest 1962-06; approx) to 1962-07-01 (approximate) - https://www.bnl.gov/about/history/accelerators.php - "The AGS became the world's premiere accelerator when it reached its design energy of 33 billion electron volts (GeV) in July of 1960."
* completed: completed, 1962-07-01 to n/a (approximate) - https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.9.36 - "Phys. Rev. Lett. 9, 36 – Published 1 July, 1962"
* role host at facility:brookhaven-national-laboratory - https://www.bnl.gov/bnlweb/history/nobel/1988.php - "made their discovery at the brand-new Alternating Gradient Synchrotron (AGS)"

#### `experiment:bevatron-antiproton`

* discovery run: active, 1955-08 to 1955-11-01 (verified) - https://history.lbl.gov/1950s/ - "The antiproton experiments of the Segrè and Chamberlain team began the first week of August 1955."
* completed: completed, 1955-11-01 to n/a (approximate) - https://journals.aps.org/pr/abstract/10.1103/PhysRev.100.947 - "Phys. Rev. 100, 947 – Published 1 November, 1955"
* role host at facility:lawrence-berkeley-national-laboratory - https://www.nobelprize.org/uploads/2018/06/chamberlain-lecture.pdf - "the Bevatron, the large accelerator in Berkeley, California"

#### `experiment:cowan-reines-neutrino`

* Savannah River run: active, 1955-10 (earliest 1955-09; latest 1955-11; "Fall of 1955"; approx) to 1956-06 (latest 1956-06; approx) (approximate) - https://www.nobelprize.org/uploads/2018/06/reines-lecture.pdf - "Then, in the Fall of 1955 at the suggestion and with the moral support of John A. Wheeler, the detector was taken to a new, powerful (700 MW at that time), compact heavy water moderated reactor at the Savannah River Plant in Aiken, South Carolina."
* completed: completed, 1956-06 (latest 1956-06; approx) to n/a (approximate) - https://www.nobelprize.org/uploads/2018/06/reines-lecture.pdf - "The tests were completed and we were convinced[7]. It was a glorious feeling to have participated so intimately in learning a new thing, and in June of 1956 we thought it was time to tell the man who had started it all"
* role host at facility:savannah-river-site - https://www.nssp.uni-saarland.de/lehre/Vorlesung/Kernphysik_SS19/History/Papers/Cowan_Reines.pdf - "the equipment was taken to the Savannah River Plant of the U.S. Atomic Energy Commission"
* role beam_source at facility:savannah-river-site - https://aps.org/funding-recognition/historic-sites/savannah - "used the flux from P Reactor at the Savannah River site"

#### `experiment:fermilab-e288`

* proposal: proposed, 1974-02 to 1975 (verified) - https://history.fnal.gov/historical/experiments/e288_internal_notes.html - "February, 1974 -- Proposal E288 (formerly E70 phase 3) -- updated proposal for Di-electrons and Di-muons"
* data taking: active, 1975 to 1977-09 (latest 1977-09; approx) (approximate) - https://www.nobelprize.org/uploads/2018/06/lederman-lecture.pdf - "the originally proposed pair experiment got underway in 1975"
* MuMu2 discovery run [run]: active, 1977-05-15 to 1977-06-04 (approximate) - https://history.fnal.gov/this_day_1977_07_01.html ; https://history.fnal.gov/historical/experiments/e288_internal_notes.html - "The experimenters began taking data for E288 on May 15, 1977."
* completed: completed, 1977-09 (latest 1977-09; approx) to n/a (approximate) - https://www.nobelprize.org/uploads/2018/06/lederman-lecture.pdf - "By September, with 30,000 events, the enhancement was resolved into three clearly separated peaks"
* role host at facility:fermilab - https://history.fnal.gov/this_day_1977_07_01.html - "an experiment in the proton fixed target area led by Leon M. Lederman"

#### `experiment:imb`

* IMB detector operating: active, 1982 to 1991 (verified) - https://www.aps.org/about/news/2024/08/morton-salt-mine-historic-site ; https://www.aps.org/apsnews/2024/10/underground-discovery-particle-physics - "IMB was an 8,000 ton Cherenkov detector — a device able to spot a form of electromagnetic radiation that is used for particle identification — that operated between 1982 and 1991."
* completed: completed, 1991 to n/a (verified) - https://www.aps.org/apsnews/2024/10/underground-discovery-particle-physics - "IMB’s run ended in 1991, but its impact continues today."
* role host at facility:imb-fairport-mine - https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.58.1494 - "The IMB detector, designed to search for proton decay, is located in the Morton-Thiokol salt mine near Fairport, Ohio"

#### `experiment:nevis-parity-muon-decay`

* discovery run: active, 1957-01 to 1957-02-15 (approximate) - https://www.nobelprize.org/uploads/2018/06/lederman-lecture.pdf - "convert a Friday Chinese-lunch discussion, just after New Year, 1957, into a Tuesday morning major experimental observation."
* completed: completed, 1957-02-15 to n/a (approximate) - https://journals.aps.org/pr/abstract/10.1103/PhysRev.105.1415 - "Phys. Rev. 105, 1415 – Published 15 February, 1957"
* role host at facility:nevis-laboratories - https://journals.aps.org/pr/abstract/10.1103/PhysRev.105.1415 - "Physics Department, Nevis Cyclotron Laboratories, Columbia University, Irvington-on-Hudson, New York, New York"

#### `experiment:slac-mit-deep-inelastic-scattering`

* inelastic scattering programme: active, 1967-08 to 1973 (verified) - https://www.nobelprize.org/uploads/2018/06/taylor-lecture.pdf ; https://www.slac.stanford.edu/pubs/slacpubs/5500/slac-pub-5724.pdf - "They began in August 1967, using the 20 GeV spectrometer."
* completed: completed, 1973 to n/a (approximate) - https://www.slac.stanford.edu/pubs/slacpubs/5500/slac-pub-5724.pdf - "inelastic electron-nucleon scattering experiments conducted between 1967 and 1973 at the Stanford"
* role host at facility:slac - https://www.nobelprize.org/uploads/2018/06/kendall-lecture-1.pdf - "In late 1967 the first of a long series of experiments on highly inelastic electron scattering was started at the two mile accelerator at the Stanford Linear Accelerator Center (SLAC)"

#### `result:ags-two-neutrinos-observation-1962`

* date 1962-07-01 - https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.9.36 - "Phys. Rev. Lett. 9, 36 – Published 1 July, 1962"
* claim (observation) - https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.9.36 - "Observation of High-Energy Neutrino Reactions and the Existence of Two Kinds of Neutrinos"

#### `result:aubert-ting-j-particle-observation-1974`

* date 1974-12-02 - https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.33.1404 - "Phys. Rev. Lett. 33, 1404 – Published 2 December, 1974"
* claim (observation) - https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.33.1404 - "Experimental Observation of a Heavy Particle J"

#### `result:barnes-omega-minus-observation-1964`

* date 1964-02-24 - https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.12.204 - "Phys. Rev. Lett. 12, 204 – Published 24 February, 1964"
* claim (observation) - https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.12.204 - "Observation of a Hyperon with Strangeness Minus Three"

#### `result:chamberlain-segre-antiproton-observation-1955`

* date 1955-11-01 - https://journals.aps.org/pr/abstract/10.1103/PhysRev.100.947 - "Phys. Rev. 100, 947 – Published 1 November, 1955"
* claim (observation) - https://journals.aps.org/pr/abstract/10.1103/PhysRev.100.947 - "Observation of Antiprotons"

#### `result:christenson-cronin-fitch-turlay-k2-2pi-evidence-1964`

* date 1964-07-27 - https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.13.138 - "Phys. Rev. Lett. 13, 138 – Published 27 July, 1964"
* claim (evidence) - https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.13.138 - "Evidence for the 2π Decay of the K20 Meson"

#### `result:cowan-reines-neutrino-detection-1956`

* date 1956-06 - https://www.nssp.uni-saarland.de/lehre/Vorlesung/Kernphysik_SS19/History/Papers/Cowan_Reines.pdf - "The results of the present work were presented in a Post deadline paper, American Physical Society, New Haven Meeting, June, 1956."
* published 1956-07-20 - https://www.nssp.uni-saarland.de/lehre/Vorlesung/Kernphysik_SS19/History/Papers/Cowan_Reines.pdf - "20 July 1956, Volume 124, Number 3212"
* claim (first_detection) - https://api.crossref.org/works/10.1126/science.124.3212.103 - "Detection of the Free Neutrino: a Confirmation"

#### `result:garwin-lederman-weinrich-parity-observation-1957`

* date 1957-02-15 - https://journals.aps.org/pr/abstract/10.1103/PhysRev.105.1415 - "Phys. Rev. 105, 1415 – Published 15 February, 1957"
* claim (observation) - https://journals.aps.org/pr/abstract/10.1103/PhysRev.105.1415 - "Observations of the Failure of Conservation of Parity and Charge Conjugation in Meson Decays: the Magnetic Moment of the Free Muon"

#### `result:herb-e288-upsilon-observation-1977`

* date 1977-06-30 - https://history.fnal.gov/historical/experiments/e288_internal_notes.html - "6/30/77 Steve Herb announced the Upsilon (9.5) discovery in a seminar at Fermilab"
* announced 1977-06-30 - https://history.fnal.gov/this_day_1977_07_01.html - "By June 15, the experimenters were confident in their results, and Steve Herb announced the discovery at a June 30 seminar in the Fermilab Auditorium."
* published 1977-08-01 - https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.39.252 - "Phys. Rev. Lett. 39, 252 – Published 1 August, 1977"
* claim (observation) - https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.39.252 - "Observation of a Dimuon Resonance at 9.5 GeV in 400-GeV Proton-Nucleus Collisions"

#### `result:imb-3-nucleon-decay-limits-1999`

* date 1999-02-10 - https://journals.aps.org/prd/abstract/10.1103/PhysRevD.59.052004 - "Phys. Rev. D 59, 052004 – Published 10 February, 1999"
* claim (limit) - https://journals.aps.org/prd/abstract/10.1103/PhysRevD.59.052004 - "Lower limits on the nucleon lifetime are set for a wide variety of proposed decay modes."

#### `result:imb-sn1987a-neutrino-burst-observation-1987`

* date 1987-04-06 - https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.58.1494 - "Phys. Rev. Lett. 58, 1494 – Published 6 April, 1987"
* claim (observation) - https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.58.1494 - "Observation of a neutrino burst in coincidence with supernova 1987A in the Large Magellanic Cloud"

#### `result:slac-mit-bjorken-scaling-observation-1969`

* date 1968-08 - https://www.nobelprize.org/uploads/2018/06/kendall-lecture-1.pdf - "14th Int. Conf. High Energy Phys., Vienna, Aug., 1968. E. D. Bloom et al., Phys. Rev. Lett. 23, 930 (1969); M. Breidenbach et al., ibid 23, 935 (1969)."
* published 1969-10-20 - https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.23.935 - "Phys. Rev. Lett. 23, 935 – Published 20 October, 1969"
* claim (observation) - https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.23.935 - "Observed Behavior of Highly Inelastic Electron-Proton Scattering"

## Sources added

| id | type | URL |
| --- | --- | --- |
| `src:disc-aps-aubert-j-particle-1974` | journal_article | https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.33.1404 |
| `src:disc-aps-barnes-omega-minus-1964` | journal_article | https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.12.204 |
| `src:disc-aps-bionta-imb-sn1987a-1987` | journal_article | https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.58.1494 |
| `src:disc-aps-breidenbach-scaling-1969` | journal_article | https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.23.935 |
| `src:disc-aps-chamberlain-antiprotons-1955` | journal_article | https://journals.aps.org/pr/abstract/10.1103/PhysRev.100.947 |
| `src:disc-aps-christenson-k2-2pi-1964` | journal_article | https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.13.138 |
| `src:disc-aps-danby-two-neutrinos-1962` | journal_article | https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.9.36 |
| `src:disc-aps-garwin-parity-1957` | journal_article | https://journals.aps.org/pr/abstract/10.1103/PhysRev.105.1415 |
| `src:disc-aps-herb-upsilon-1977` | journal_article | https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.39.252 |
| `src:disc-aps-historic-site-savannah-river` | institution_page | https://aps.org/funding-recognition/historic-sites/savannah |
| `src:disc-aps-mcgrew-imb3-nucleon-decay-1999` | journal_article | https://journals.aps.org/prd/abstract/10.1103/PhysRevD.59.052004 |
| `src:disc-aps-morton-salt-mine-historic-site` | institution_page | https://www.aps.org/about/news/2024/08/morton-salt-mine-historic-site |
| `src:disc-apsnews-imb-underground-discovery-2024` | institution_page | https://www.aps.org/apsnews/2024/10/underground-discovery-particle-physics |
| `src:disc-bnl-75-timeline` | official_facility_site | https://www.bnl.gov/75/timeline.php |
| `src:disc-bnl-nobel-1976` | official_facility_site | https://www.bnl.gov/bnlweb/history/nobel/1976.php |
| `src:disc-bnl-nobel-1980` | official_facility_site | https://www.bnl.gov/bnlweb/history/nobel/1980.php |
| `src:disc-bnl-nobel-1988` | official_facility_site | https://www.bnl.gov/bnlweb/history/nobel/1988.php |
| `src:disc-bnl-nobel-index` | official_facility_site | https://www.bnl.gov/bnlweb/history/nobel/ |
| `src:disc-bnl-omega-group` | official_facility_site | https://www.bnl.gov/omega/ |
| `src:disc-cern-courier-nineteen-sixty-four` | press_release | https://cerncourier.com/nineteen-sixty-four/ |
| `src:disc-crossref-cowan-reines-1956` | secondary | https://api.crossref.org/works/10.1126/science.124.3212.103 |
| `src:disc-doe-em-savannah-river-site` | official_facility_site | https://www.energy.gov/em/savannah-river-site |
| `src:disc-fnal-history-bottom-quark-1977-07-01` | official_facility_site | https://history.fnal.gov/this_day_1977_07_01.html |
| `src:disc-fnal-history-e288-internal-notes` | official_facility_site | https://history.fnal.gov/historical/experiments/e288_internal_notes.html |
| `src:disc-fnal-history-village-crier-upsilon-1977` | official_facility_site | https://history.fnal.gov/historical/experiments/extra_upsilon.html |
| `src:disc-lbl-elements-bevatron-40-years` | press_release | https://elementsarchive.lbl.gov/2019/06/13/the-bevatron-40-years-of-science/ |
| `src:disc-lbl-history-1930s` | official_facility_site | https://history.lbl.gov/1930s/ |
| `src:disc-lbl-history-1950s` | official_facility_site | https://history.lbl.gov/1950s/ |
| `src:disc-lbl-history-home` | official_facility_site | https://history.lbl.gov/ |
| `src:disc-nevis-directions` | official_facility_site | https://www.nevis.columbia.edu/directions.html |
| `src:disc-nevis-what-we-do` | official_facility_site | https://www.nevis.columbia.edu/what-we-do.html |
| `src:disc-nobel-1959-summary` | project_document | https://www.nobelprize.org/prizes/physics/1959/summary/ |
| `src:disc-nobel-1976-summary` | project_document | https://www.nobelprize.org/prizes/physics/1976/summary/ |
| `src:disc-nobel-1980-summary` | project_document | https://www.nobelprize.org/prizes/physics/1980/summary/ |
| `src:disc-nobel-1988-summary` | project_document | https://www.nobelprize.org/prizes/physics/1988/summary/ |
| `src:disc-nobel-1990-press-release` | press_release | https://www.nobelprize.org/prizes/physics/1990/press-release/ |
| `src:disc-nobel-1990-summary` | project_document | https://www.nobelprize.org/prizes/physics/1990/summary/ |
| `src:disc-nobel-1995-summary` | project_document | https://www.nobelprize.org/prizes/physics/1995/summary/ |
| `src:disc-nobel-lecture-chamberlain-1959` | project_document | https://www.nobelprize.org/uploads/2018/06/chamberlain-lecture.pdf |
| `src:disc-nobel-lecture-fitch-1980` | project_document | https://www.nobelprize.org/uploads/2018/06/fitch-lecture.pdf |
| `src:disc-nobel-lecture-kendall-1990` | project_document | https://www.nobelprize.org/uploads/2018/06/kendall-lecture-1.pdf |
| `src:disc-nobel-lecture-lederman-1988` | project_document | https://www.nobelprize.org/uploads/2018/06/lederman-lecture.pdf |
| `src:disc-nobel-lecture-reines-1995` | project_document | https://www.nobelprize.org/uploads/2018/06/reines-lecture.pdf |
| `src:disc-nobel-lecture-schwartz-1988` | project_document | https://www.nobelprize.org/uploads/2018/06/schwartz-lecture.pdf |
| `src:disc-nobel-lecture-segre-1959` | project_document | https://www.nobelprize.org/uploads/2018/06/segre-lecture.pdf |
| `src:disc-nobel-lecture-taylor-1990` | project_document | https://www.nobelprize.org/uploads/2018/06/taylor-lecture.pdf |
| `src:disc-nobel-lecture-ting-1976` | project_document | https://www.nobelprize.org/uploads/2018/06/ting-lecture.pdf |
| `src:disc-nominatim-fairport-harbor` | geocoder | https://nominatim.openstreetmap.org/search?format=jsonv2&q=Fairport+Harbor+Ohio |
| `src:disc-nominatim-lbnl` | geocoder | https://nominatim.openstreetmap.org/search?format=jsonv2&q=Lawrence+Berkeley+National+Laboratory |
| `src:disc-nominatim-nevis` | geocoder | https://nominatim.openstreetmap.org/search?format=jsonv2&q=136+South+Broadway%2C+Irvington%2C+NY+10533 |
| `src:disc-nominatim-srs` | geocoder | https://nominatim.openstreetmap.org/search?format=jsonv2&q=Savannah+River+Site |
| `src:disc-science-cowan-reines-1956` | journal_article | https://www.nssp.uni-saarland.de/lehre/Vorlesung/Kernphysik_SS19/History/Papers/Cowan_Reines.pdf |
| `src:disc-slac-pub-5724-riordan` | project_document | https://www.slac.stanford.edu/pubs/slacpubs/5500/slac-pub-5724.pdf |
| `src:disc-srs-about` | official_facility_site | https://public.srs.gov/about/ |

Reused existing source: `src:bnl-about-history-accelerators-page` (re-fetched today; the Cosmotron, AGS and 80-inch bubble chamber passages were read again).

Access notes: the Science page (science.org) and Fermilab History pages (fnal.gov) returned HTTP 403/Cloudflare to automated fetches. The 1956 Science paper was read from a University of Saarland course-page copy of the journal PDF (page images with OCR; only clean phrases are quoted) and its title and date were cross-checked against the Crossref and PubMed (NLM esummary) records, which agree on 20 July 1956. The three Fermilab History pages were read through Wayback Machine snapshots, recorded in `archive_url`. Berkeley Lab's 2021 Bevatron news page (403) was not used. PRL/PR PDFs behind the APS paywall were not available, so those sources carry only title, date and, where APS shows one, the abstract (`retrieval: partial`).

## Conflicts

| claim | source A | source B | chosen | why |
| --- | --- | --- | --- | --- |
| Year of the muon-neutrino discovery | PRL 9, 36 dated 1 July 1962; BNL Nobel page: "their 1962 discovery" | BNL 1999 Bulletin timeline: "in 1963" | 1962 | The paper was published in July 1962; the later BNL page agrees. |
| Start of the SLAC-MIT inelastic experiments | Taylor Nobel lecture: "They began in August 1967" | Kendall Nobel lecture: "In late 1967 the first of a long series ... was started" | August 1967 | The more specific statement; Nobel press release gives early 1967 for the elastic phase (collaboration start). |
| End of the SLAC-MIT programme | Riordan SLAC-PUB-5724: experiments "conducted between 1967 and 1973" | Kendall: continued "well into the 1970s"; Nobel PR: "end of the 1960s and the beginning of the 1970s" | 1973, approximate | Only source with a year; marked approximate with both alternatives in the note. |
| Start of E288 MuMu2 data taking | Fermilab History July 1 page and Village Crier: 15 May 1977 | Village Crier (other line): run "began last May 17"; Yoh notes: "May 14-5" | 15 May 1977 | Two sources agree; the others are one-day offsets or ambiguous. |
| Date the upsilon paper was sent | Fermilab: submitted to PRL 1 July 1977; APS: published 1 August 1977 | Lederman Nobel lecture: "a paper was sent off in August of 1977" | published 1 August 1977; announced 30 June 1977 | Journal page and Fermilab history agree; the lecture is a recollection. |
| Year of the Cronin-Fitch experiment | BNL: experiment began in 1963 (Fitch lecture agrees) | Paper: received 10 July 1964, published 27 July 1964 | both recorded | Start 1963; the paper date is the result date; they are different events. |
| When the neutrino was confirmed | SRS timeline: 1956; APS plaque page: run "in early 1956" | Reines: detector reached Savannah River in fall 1955 | run from fall 1955; result June/July 1956 | The statements are compatible: installation in fall 1955, results in 1956. |
| Location of the IMB mine | 1987 PRL: "near Fairport, Ohio"; coordinates 41.7 N, 81.3 W | APS 2024 pages: "Morton Salt Mine in Painesville, Ohio" and "Fairport Harbor Morton Salt Mine" | Fairport Harbor village point | Paper wording and the village centroid agree to the paper's rounding; recorded in notes. |
| Type of the CP-violation result | PRL title: "Evidence for the 2pi decay of the K2 meson" | Nobel 1980 and BNL: "discovery" | evidence | A16: the result type follows the paper title. |

## Unresolved fields (left empty or approximate, not invented)

* P Reactor coordinates (the Savannah River point is the whole-site OSM centroid, 20 km precision).
* Day-precision dates of the Savannah River run: only "Fall of 1955" and June 1956 are published; the Hanford 1953 attempt is sourced but only in notes.
* Bevatron first-beam date and building coordinates; the Bevalac era (Berkeley Lab page returned 403).
* Cosmotron first-beam date (BNL gives the 1952-1966 heading and 1953 for design energy).
* Run dates of the two-neutrino experiment (start bounded between July 1960 and July 1962).
* End of data taking for every experiment: the completed interval is a "no later than" bound (paper date, received date, or last documented activity) and is marked approximate with a note saying so. Exceptions with a sourced end: E598 (7 November 1974) and SLAC-MIT (1973 per Riordan).
* Beam and exposure details of the omega-minus run.
* E598 history after the 7 November 1974 spectrometer change.
* End Station A and IMB shaft/hall coordinates; the current owner of the Fairport mine; IMB-1/-2/-3 phase dates; the individual IMB lifetime-limit tables (not fetched).
* Nevis Laboratories founding date; follow-up measurement dates of the parity experiment.
* INSPIRE experiment ids and Greybook codes (the importer owns the INSPIRE rate budget; none contacted).
* Collaboration membership and leadership; person records; detector records for all ten experiments.

## Considered and excluded

* **Wu experiment (parity violation, National Bureau of Standards, 1956-57):** sources exist (APS "December 27, 1956: Fall of Parity Conservation", NIST blog "A Forever Stamp and a Discovery That Changed Physics Forever", Lederman Nobel lecture) but the experiment ran in the Bureau's Washington cryogenics laboratory, which would need a new historic facility and site that this stream was not assigned and for which no source for the 1956 campus coordinates was found. A good follow-up row.
* **Garwin-Lederman-Weinrich (Nevis, 1957):** included, sourced by the Physical Review page and Lederman's Nobel lecture.
* **Cosmic-ray discoveries (positron, muon, pion):** excluded as the brief says: they had no fixed facility.
* **Hanford 1953 attempt:** sourced (Science paper, Reines lecture) but a different facility with no assigned record; recorded in notes only, see integrator list.
* **Bevalac:** not needed; no sourced interval was reachable.
* **Gargamelle, Mark I at SPEAR:** other streams, not created.
* **Lederman's 1968 BNL dimuon experiment and the 1974 BNL charmed baryon:** not requested.

## For the integrator

* `institution:lawrence-berkeley-national-laboratory` has `facility_id: null`; set it to `facility:lawrence-berkeley-national-laboratory`. `institution:columbia-university` could point to `facility:nevis-laboratories` (not done: another stream's records).
* `map:brookhaven-national-laboratory` now warns that `accelerator:cosmotron` is neither drawn nor listed in `unlocated[]`; add an `unlocated` entry (the Cosmotron was dismantled in 1969) or drop the accelerator.
* Hanford 1953: add `facility:hanford-site` (reactor_site) and a predecessor experiment, then a `predecessor` lineage row on `experiment:cowan-reines-neutrino`.
* Fermilab: `experiment:fermilab-e288` has no accelerator (the 400 GeV Main Ring is not an Atlas record) and its predecessor E70 (proposal 17 June 1970) is not an Atlas record.
* No antimatter topic exists; `experiment:bevatron-antiproton` uses `topic:precision-and-rare-processes` plus the `antimatter` experiment kind.
* Collaboration records `collaboration:imb`, `collaboration:e288`, `collaboration:slac-mit` were created because the experiment bar asks for one where a collaboration exists; the brief did not list them, so drop them if unwanted (the experiments then need `collaboration_ids: []` plus a note).
* Lineage: `experiment:imb` carries `complementary` to `experiment:kamiokande` (APS News: both saw the SN 1987A neutrinos). No source states a successor row for any other experiment here; APS says IMB and Kamioka "influence[d] the design of later detectors like Super-Kamiokande", which is not a successor relation.
* If other streams cite the same DOIs or Nobel pages (for example the Aubert J-particle paper, PRL 33, 1404, in the colliders stream), the A20 duplicate-source check will fail at merge; keep one source id and repoint.
* The new sources and results are named `src:disc-*`; result ids are listed above for the tours stream.

## Checks

Run in the worktree on the final commit (see the report for the exact lines):

* `python -m hepgraph.atlas.validate`: 0 errors. Warnings rose from 1596 to 1601: four `experiment-without-active-beam` (Cowan-Reines, E288, IMB, Nevis; 74 existing records have the same warning) and one `map-entity-unaccounted` (Cosmotron).
* `python -m hepgraph.atlas.build`: succeeds; `static/atlas/generated` was reverted, not committed. All ten experiments appear with their facility and with state segments (possible/certain) derived from the dated intervals.
* `python -m pytest -q`: 689 passed, 139 skipped.
* Each of the three data commits was validated in a clean export of that commit: 0 errors.

