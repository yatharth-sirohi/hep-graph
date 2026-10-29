# Follow-ups 3: three data defects (CMD, HERA, Mu2e)

Branch `atlas-next`, worktree `~/Desktop/HEP-Graph-atlas-next`, 2026-10-29. Nothing is committed. `hepgraph.atlas.build` was not run (another session owns `static/atlas/generated`). `data/atlas/results/` was not touched.

Every quote below was machine-checked as a verbatim substring of the page text fetched today (HTML stripped; PDFs through `pdftotext`; whitespace collapsed). No request went to inspirehep.net, and no Wikipedia page was read or cited. `mu2e.fnal.gov` returned HTTP 403 to `WebFetch` on its status and proposals pages; it was not tried again and nothing was done to get around it. A web-search snippet that claims to describe those pages was not used as a source.

Validator: `python -m hepgraph.atlas.validate` ends `0 errors, 1892 warnings, 4 informational`. (The first run after the edit gave 2 errors, `quote-too-long` on two quotes over 300 characters; both were shortened.) No warning names a record I changed.

## Files changed

| File | Change |
| --- | --- |
| `data/atlas/collaborations/cmd.json` | status, intervals, summary, sources |
| `data/atlas/accelerators/hera.json` | `summary.plain`, `summary.technical`, one stale note |
| `data/atlas/collaborations/mu2e.json` | counts, `as_of`, `roster_source_ids`, summary |
| `data/atlas/experiments/mu2e.json` | intervals 0, 2, 3; key spec; host role; physics goal; unique capability; summary; notes; sources |
| `data/atlas/detectors/mu2e.json` | interval, placement, technology, summary, notes, sources |
| `data/atlas/coverage/muons.json` | the Mu2e row's `notes` (25 m and 2.5x10^-17 text) |
| `data/atlas/sources/` | 4 new `src:fu3-*` records; 2 INSPIRE literature records deleted; `accessed` bumped on 5 records I re-read (Fermilab news, Solodov talk, CMD history page, IPAC-2017 abstract; also `muons-inspire-experiment-mu2e`, whose note named a deleted id) |

## 1. `collaboration:cmd`: status "completed" was wrong

**Before.** `status: "completed"`. The last interval was `completed`, start 1984, `end: null`, labelled "CMD-1 experiments ended" (copied from the CMD-1 record), so the collaboration was dated as over from 1984. The summary said CMD-3 had run since 2000.

**After.** `status: "active"` (the schema's vocabulary is `STATUSES` in `hepgraph/atlas/schema.py`; other open-ended collaborations such as `collaboration:snd` use `active` with a final `active` interval and `end: null`). The five intervals now follow the collaboration history page and agree with `experiment:cmd-1/2/3`:

| Interval | Status | Start | End |
| --- | --- | --- | --- |
| VEPP-2M data taking (CMD-1), unchanged | active | 1979 | 1984 |
| CMD-2 commissioning at VEPP-2M | construction | 1984 | 1992 |
| VEPP-2M data taking (CMD-2) | active | 1992 | 2000 |
| CMD-3 design, prototyping and commissioning at VEPP-2000 | construction | 2000 | 2010 |
| CMD-3 data taking at VEPP-2000 | active | 2010 | open |

The three intermediate statuses copy the experiment records (`cmd-2` uses `construction` for 1984-1992). `summary.technical` now says CMD-3 has taken data since 2010 and was still taking data in 2025-2026. Record-level `sources` gained the two sources below. `experiments/cmd-3.json` and the `cmd-1`, `cmd-2` and detector records were not changed; they already agree.

**Source for "taking data now".** E. Solodov on behalf of the CMD-3 Collaboration, "Update - News from CMD-3", 14th International Workshop on e+e- collisions from Phi to Psi, Pisa, 8 June 2026. Existing record `src:colliders2-solodov-cmd3-phipsi2026` (reused; `accessed` set to 2026-10-29).

* URL: https://indico.sns.it/event/140/contributions/1428/attachments/392/1169/Solodov_CMD_PhiPsi2026.pdf
* Quote (slide 8): "2025 data were collected with the reverse direction of the beams"
* Quote (slide 8, same slide): "More data (x3) to be collected (2024-2026(7?))"
* Quote (slide 38): "We plan to finish low-energy scan and take some dedicated high energy data over next two years"
* Quote (slide 38, in the note): "Then we plan to have 1-2 year break for detectors upgrades"; the timeline on that slide reads "Continue data taking".
* The interval's `quote` joins the first and third with " ... ". The start year 2010 is carried by `src:colliders2-vepp2000-high-luminosity-ipac17` (https://vepp2k.inp.nsk.su/en/node/85): "VEPP-2000 e+e− collider at BINP was commissioned and started data taking with two detectors in 2010 with old injection chain." That abstract does not name the detectors; the note says so.

**Interval dates.** Quotes from https://cmd.inp.nsk.su/?cmdc_history (Collaboration History; `src:colliders2-cmd-collaboration-history`, `accessed` set to 2026-10-29):

* "1984 - 1992 Commissioning of the CMD-2 detector at VEPP-2M collider"
* "1992 - 2000 Experiments with the CMD-2 detector at VEPP-2M collider"
* "2000 - present Commissioning of the CMD-3 detector at VEPP-2000 collider"

**Also read, not cited.** The 2026 CMD-3 papers arXiv:2608.03417 (Aug 2026), arXiv:2607.11556 and arXiv:2606.16779 show the collaboration still publishing, but none says in words that data taking continues, so none is used for the status. The CMD site's own pages (`?cmd3_history`, `?cmdc_news_db`) are stale (the news database's latest entry is from 2005), and the VEPP-2000 news page stops in 2020.

## 2. `accelerator:hera`: empty summaries

**Before.** `summary.plain` and `summary.technical` were `""`.

**After.**

* plain (47 words): "HERA was DESY's electron-proton collider in Hamburg, Germany, the only collider in the world that brought electrons or positrons into collision with protons. It ran in a 6.3-kilometre tunnel from 1992 to 2007, and its experiments used the collisions to study the inner structure of the proton."
* technical: "Electron/positron-proton storage-ring collider at DESY, 6336 m long (DESY figure): 27.5 GeV electrons or positrons on 820 GeV protons (cms 300 GeV) from 1992, then on 920 GeV protons (cms about 320 GeV) from 1998. The collider detectors H1 and ZEUS ran from 1992; HERMES (lepton beam) and HERA-B (proton beam) were fixed-target experiments. Research operation ended on 30 June 2007."

Every statement is in a source already cited by the record, re-read today:

| Statement | Quote | URL and locator |
| --- | --- | --- |
| only electron-proton collider; Hamburg; 6.3 km; 1992-2007; HERMES and HERA-B use one beam each | "The HERA storage ring facility at DESY was the only one in the world in which two different types of particles were accelerated separately and then brought to collision." "In a 6.3-kilometer-long tunnel located deep below Hamburg" "Research operation: 1992-2007" | https://www.desy.de/e141261/e158573/e158772/index_eng.html, body and "Facts and figures" (`src:geo-desy-hera-facts-page`). The same page: "Length: 6336 metres"; "The H1 and ZEUS experiments went into operation in 1992"; HERMES "used the HERA electron beam", HERA-B "used the HERA proton beam" |
| first and, so far, only | "HERA, the “Hoch Energie Ring Anlage” at DESY, Hamburg, was the first, and so-far the only, accelerator complex in which electrons and protons were collided." | https://arxiv.org/abs/0805.3334, section 2.1 (`src:hera-collider-physics-klein-yoshida-2008`) |
| 27.5 GeV; 820 then 920 GeV | "The energy of the proton beam was initially set to 820 GeV until it was increased to 920 GeV, in 1998, and kept at that value." (introduction); "The energy of the electron (positron) beam was about 27.5 GeV." | same paper; the record's own spec quotes |
| cms 300 GeV; about 320 GeV | the record's own spec quotes: `src:fu2-arxiv-hep-ex-9705001` (300 GeV) and the abstract of 0805.3334 ("cms energies of about 320 GeV") | those records |
| ended 30 June 2007 | "The electron-proton collider HERA ended its data taking on June 30, 2007." | https://arxiv.org/abs/0812.4662 (PDF), introduction (`src:dw-hera-ew-bsm-zhang-arxiv-0812-4662`); the DESY brochure agrees on "the end of June 2007" |

I left out the injector chain, luminosity and the Klein and Yoshida 6223 m circumference (the record's circumference note already carries that conflict). `notes[1]` still said the day was "from Wikipedia", which is untrue since the de-Wikipedia stream and breaks the no-Wikipedia rule; it now cites the Zhang quote. No other change to the record.

## 3. `collaboration:mu2e` and the Mu2e records: INSPIRE-derived values

### 3a. Collaboration counts

Source: Fermilab Newsroom, "Stefano Miscetti elected as Mu2e co-spokesperson", 19 May 2023, https://news.fnal.gov/2023/05/stefano-miscetti-elected-as-mu2e-co-spokesperson/ (`src:vf-fnal-mu2e-miscetti-2023`, re-fetched, HTTP 200). Locator: first paragraph under the photograph.

* Quote: "The Mu2e collaboration brings together more than 200 people from 38 institutions across six countries"

| Field | Before | After |
| --- | --- | --- |
| `membership.institution_count` | 37, approximate, `src:muons-inspire-experiment-mu2e` ("about 37 research institutions") | 38, verified, `src:vf-fnal-mu2e-miscetti-2023`, `verified_at` 2026-10-29 |
| `membership.member_count` | 200, approximate, `src:muons-inspire-experiment-mu2e` ("more than 200 physicists") | 200, `confidence: "approximate"`, `display: "more than 200"`, note "Lower bound ... more than 200 people", same Fermilab source, `verified_at` 2026-10-29 |
| `membership.as_of` | "2025" | "2023-05" (every count now rests on the 19 May 2023 item) |
| `membership.roster_source_ids` | the INSPIRE experiment record | `[]` (a news item is not a roster; `collaboration:des` does the same) |
| `summary.plain` / `summary.technical` | more than 200 physicists, about 37 institutions, six countries named from INSPIRE | more than 200 people, 38 institutions, six countries (not named), as of May 2023 |

How "more than N" is encoded in this schema: the stated bound goes in `value`, with `confidence: "approximate"` and a note saying "lower bound" (ATLAS, BaBar, Belle II, CMS, COMET, DES, DESI all do this); `display` is allowed on a sourced value and ATLAS's `institution_count` uses it. The compare view reads only the number.

### 3b. `experiments/mu2e.json` and `detectors/mu2e.json`

Every INSPIRE-only count, date and number, with what became of it:

| Record / field | Before | After | Source and quote |
| --- | --- | --- | --- |
| experiment, interval 0 (proposed) start | 2008-10-18, INSPIRE experiment record | **2008-10** (month) | M. J. Syphers, arXiv:0910.3657 (DPF-2009), reference [3]: "Proposal P-973 submitted to Fermilab, 10 Oct. 2008; available as, MU2E-doc-388 (2008)". New `src:fu3-arxiv-0910-3657-syphers-muon-accelerator`. The day conflicts (10 Oct here, 18 Oct in INSPIRE), so only the month, on which both agree, is kept; the note says so |
| experiment, interval 1 (approved) start | 2010-08, INSPIRE | **unchanged, not re-sourced** | No source I could read states 2010-08. Syphers (October 2009) already says Mu2e "has been given relatively high priority by HEPAP and Stage-I Approval from the Fermilab PAC", so 2010-08 cannot be the first approval; recorded in the experiment's `notes` |
| experiment, interval 2 (construction) start | 2016-06, INSPIRE experiment record plus two INSPIRE literature records | **2016-07-14** (changed) | DOE Office of Science HEP "Projects, Missions, and Status", https://science.osti.gov/hep/Facilities/Projects-Missions-and-Status, Intensity Frontier Projects table, Mu2e row: "Mu2e CD-3 July 14, 2016". The page's legend defines "Critical Decision (CD) 3: Approve Start of Construction". New `src:fu3-doe-hep-projects-status` (undated page). "Ongoing" rests on PoS(WIFAI2025)020: "is currently being assembled at the Fermilab Muon Campus" |
| experiment, interval 3 (Run 1) start | 2027 planned, INSPIRE literature record of the 2026 status paper | 2027 planned, same paper's non-INSPIRE page | https://pos.sissa.it/525/020/ (A. Driutti for Mu2e, PoS WIFAI2025 020, published 20 July 2026, DOI 10.22323/1.525.0020), abstract: "initial data collection scheduled to begin in 2027". New `src:fu3-pos-wifai2025-mu2e-status`. The note also quotes "Run 1, expected to begin in 2027" and "A physics run is planned to begin at the end of 2027 to study the detector systems and collect initial physics data, preceding the scheduled long shutdown at Fermilab in 2028." |
| experiment, `key_specs[0]` single-event sensitivity | 2.5e-17, INSPIRE experiment record ("about 2.5 x 10^-17") | **2.87e-17** (changed) | Mu2e Technical Design Report, arXiv:1501.05241 (`src:muons-arxiv-1501-05241`), Chapter 1, section 1.1, p. 1-1 (PDF p. 18): "measuring Rµe with a single event sensitivity of 2.87 × 10–17". Nothing I could read states 2.5e-17 outside INSPIRE; the TDR, the collaboration's design report, gives 2.87e-17. The 3x10^-17 of the 2022 paper (`src:fu3-pos-eps-hep2021-mu2e-status`, https://pos.sissa.it/398/557/: "an unprecedented single event sensitivity of 3x10^{-17}") stays in the note, as does the INSPIRE figure; `coverage/muons.json` notes follow |
| experiment, `unique_capabilities[0]` | "A 25-metre chain of three superconducting solenoids ...", quote not found in the cited paper | **82-foot** system (changed text) | Fermilab news item above, section "A big journey for tiny particles": "An “S”-shaped, 82-foot-long system of superconducting solenoids ... will sort negatively charged muons from positive ones. This system will also transport and focus the muons toward an aluminum target." 82 ft = 25.0 m is a unit conversion, stated in the note |
| detector, interval 0 start | 2016-06, INSPIRE | **2016-07-14** | same DOE row; "installed" from PoS(WIFAI2025)020 section 2.2.3: "the tracker and the calorimeter detectors have already been installed in the Mu2e hall" |
| detector, `technology` | "A 25-metre chain ... fast CsI crystal calorimeter ...", quote not in the cited paper | three superconducting solenoids, straw tracker, crystal calorimeter, cosmic ray veto system | PoS(WIFAI2025)020 abstract: "superconducting solenoids and high-precision detectors. The solenoid system comprises production, transport, and detector solenoids. ... a straw tracker and a crystal calorimeter, ... a cosmic ray veto system surrounds the last section of the transport solenoid and the entire detector solenoid". "Fast" and "25-metre" are dropped from this field (not in the quote) |
| both summaries | "25 m", "June 2016", "fast CsI" | "82-foot (about 25 m)", "July 2016", "pure-CsI" (from the paper's "The Calorimeter System" paragraph) | as above |

Smaller re-sourcings (no number, but they cited the INSPIRE records being retired): the experiment's host-facility role now cites the Fermilab item ("which will be situated at the U.S. Department of Energy’s Fermi National Accelerator Laboratory"); its physics goal and the detector placement now cite the PoS(WIFAI2025)020 text ("The Mu2e experiment at Fermilab is designed to search for charged lepton flavor violation (CLFV) by looking for the rare, neutrinoless conversion of a muon into an electron in the Coulomb field of a nucleus."; "a process strictly forbidden in the Standard Model"; "in the field of an aluminum nucleus").

### Source records

* **Deleted** (cited by nothing in `data/atlas` after the edits; the only remaining mentions are in older worklogs and the stale generated bundles): `src:muons-inspire-lit-mu2e-status-2022`, `src:muons-inspire-lit-mu2e-status-2026`.
* **Kept**: `src:muons-inspire-experiment-mu2e`. It is still cited for the approved interval (2010-08), the collaboration's "collaboration active" interval (start 2010-08, derived from that approval) and `formation: null`, plus the two identifier-type uses the brief allows (the website link note and the INSPIRE experiment id) and the record-level `sources` of `site:fermilab-mu2e-hall`. Its note was updated to point at the new PoS source.
* **New**: `src:fu3-pos-wifai2025-mu2e-status`, `src:fu3-pos-eps-hep2021-mu2e-status`, `src:fu3-doe-hep-projects-status`, `src:fu3-arxiv-0910-3657-syphers-muon-accelerator`.

## Unresolved

1. `experiment:mu2e` "experiment approved" start 2010-08: INSPIRE only. Suspect, per the Syphers quote above. A readable source for the Stage-I approval and CD-0 dates is needed (the Mu2e status page is behind a 403).
2. `collaboration:mu2e` interval "collaboration active" start 2010-08: INSPIRE only (derived from the approval date above); `formation` stays `null`.
3. The proposal day (10 or 18 October 2008) is unresolved; the month is recorded.
4. `site:fermilab-mu2e-hall` lists `src:muons-inspire-experiment-mu2e` in its record-level `sources` (outside the files I was asked to check; nothing in it rests on that source's value).

## For the integrator

* The generated bundles (`static/atlas/generated/sources.json`, `provenance.json`) still name the two deleted source ids; a rebuild clears them.
* `collaboration:mu2e` keeps `evidence_class: "official_institution_list"`, but its counts now rest on a lab news item, not a list. `collaboration:des` uses `derived` in the same situation; I did not change the class.
* `experiment:mu2e` keeps `status: construction`. The July 2026 status paper says "The Mu2e experiment is currently transitioning from installation to active commissioning", which may deserve a `commissioning` interval; not decided here.
* `accelerator:hera` lists `src:geo-desy-hera-facts-page` twice in its record-level `sources`; harmless, not touched.

## Integrator checks and changes (2026-10-29)

* Every quote added here was re-fetched and found in its source: segment by segment where a quote joins two
  passages with "...", in the PDF where the source record points at a landing page (PoS 525/020 and the Mu2e TDR,
  arXiv:1501.05241, whose p. 1-1 gives "2.87 × 10–17"). The HERA summaries' statements are on the DESY HERA page
  ("the only one in the world", "6.3-kilometer-long tunnel", "Research operation: 1992-2007", "the proton’s inner
  structure") and in the papers quoted above.
* `collaboration:mu2e` `membership.evidence_class`: `official_institution_list` → `derived`. The counts now rest
  on a news item, not an institution list, and the UI words `official_institution_list` as "On the official
  institution list"; `collaboration:des` uses `derived` for the same situation.
* `accelerator:hera` listed `src:geo-desy-hera-facts-page` twice in its record-level `sources` (before this
  stream); the duplicate is removed.
* Left as found: `experiment:mu2e` stays `construction`. The July 2026 PoS paper says it "is currently
  transitioning from installation to active commissioning", which is not yet a commissioning date. The
  INSPIRE-only "approved 2010-08" interval and the collaboration's start that derives from it remain, with the
  conflict noted in the experiment's notes.
