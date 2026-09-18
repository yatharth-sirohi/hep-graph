# VERIFY colliders-historical — Wave 3 independent verification

Verifier: independent review, no subagents. Did not trust
`docs/atlas-worklog/colliders-historical.md` (the researcher's own worklog); every factual
claim below was re-checked against a freshly fetched source in this session (WebFetch +
Bash `curl` for fnal.gov/desy.de/slac domains, which 403 WebFetch). Repo:
`/Users/yatharthsirohi/Desktop/HEP-Graph-atlas-v1` (branch `hep-atlas-v1`, no git used).
`verified_at` on all fixes: 2026-09-17.

## Records checked

- Experiments (6): `experiment:cdf`, `experiment:d0`, `experiment:sld`, `experiment:babar`,
  `experiment:h1`, `experiment:zeus`.
- Detectors (6) and collaborations (6): matching `detector:*` / `collaboration:*` for the
  same six.
- Sites owned by this partition (2): `site:fermilab-cdf-collision-hall-b0`,
  `site:fermilab-d0-collision-hall`. Sites referenced but owned by the facilities lead
  (4, read-only): `site:slac-slc-collider-hall-sld`, `site:slac-pep-ii-ir2-babar`,
  `site:desy-hera-north-hall-h1`, `site:desy-hera-south-hall-zeus` — all now exist (were
  dangling at the time the researcher wrote them), resolve correctly, and carry honest
  `kind: campus` / `confidence: approximate` points per A23.
- Results (2, both owned by this partition): `result:cdf-top-quark-observation-1995`,
  `result:d0-top-quark-observation-1995`.
- All 25 `src:colliders-historical-*` source records.
- Cross-checked for consistency (read-only, not edited): `accelerators/fermilab-tevatron.json`,
  `accelerators/hera.json`, `accelerators/slc.json`, `accelerators/pep-ii.json`,
  `facilities/{fermilab,slac,desy}.json`.

## Values re-fetched

- All six INSPIRE experiment records fetched live (`https://inspirehep.net/api/experiments/<recid>`,
  ≥10 s apart): CDF (1109361), D0 (1109214), SLD (1109249), BaBar (1108553), H1 (1109080),
  ZEUS (1109012). Every `date_proposed`/`date_approved`/`date_started`/`date_completed` and every
  `description` free-text sentence quoted in the data files matches the live record **exactly**,
  including two verbatim-preserved source typos (CDF's "ans data taking has resumed" and D0's
  "silicon detectors nestled scintillating fiber detectors") — strong evidence of genuine
  copy-from-source rather than paraphrase.
- Both 1995 top-quark PRL papers fetched from `journals.aps.org` (via the DOI redirect) and from
  arXiv (hep-ex/9503002, hep-ex/9503003): titles, PRL 74:2626/2632, journal-received date
  (both **1995-02-24**, matching the "submission dates" this brief asked me to check), and
  abstract significances (CDF 4.8σ, D0 4.6σ) all confirmed.
- fnal.gov Tevatron Experiments CDF/D0 pages, cdf.fnal.gov, d0.fnal.gov, the Fermilab 2011
  shutdown press release, and the Fermilab Shutdown Process page all fetched via `curl` (403 on
  WebFetch) and every quoted sentence checked character-for-character.
- SLD's official intro page, the BaBar detector NIM abstract (hep-ex/0105044), the D0 upgraded-
  detector NIM abstract (physics/0507191), the D0 1984 Design Report (OSTI 1879497, via its
  `doi.org` redirect), CERN Courier's BaBar 25th-anniversary piece, Symmetry Magazine's PEP-II/
  BaBar shutdown piece, and www-h1.desy.de / www-zeus.desy.de all fetched and checked.
- Cross-checked the shared HERA/Tevatron/SLC/PEP-II accelerator records (owned by the facilities
  lead, not edited) for consistency with this partition's interval end dates.

## Findings by severity

### P1 (3, all fixed)

**1. A splice quote in `experiments/cdf.json` and `detectors/cdf.json` was not verbatim —
it paraphrased the source.** The "Tevatron shutdown; CDF data-taking ends" / "shut down"
interval's `quote` read: *"...CDF will have its fluids and gases removed within a month and
be completely shut down."* The actual sentence on the cited Fermilab Shutdown Process page
(`fnal.gov/pub/tevatron/shutdown-process.html`, re-fetched) is: *"It took about a month to
fully shut down the CDF detector, including time to remove its cooling fluids and gases."*
This is the exact defect class the brief warned about (sibling verifiers finding paraphrased/
spliced quotes). The D0 half of the equivalent spliced quote ("The DZero detector was
completely shut down after about three months.") **is** verbatim and was left alone. Fixed:
replaced the CDF half with the true verbatim sentence in both files.

**2. BaBar's day-precision last-data date (`2008-04-08`) overstated its confidence.** The
sole source is Symmetry Magazine's "End of PEP-II and BaBar runs at SLAC," dated 2008-04-08,
whose text says the beams were dumped and BaBar took its last data **"last night"** — i.e.
the event it describes may have happened on 2008-04-07, one day before the article's own
dateline (which is what this brief's own fact list flagged, "...to 2008-04-07 last data").
INSPIRE's `date_completed` for BaBar is month-precision only (`2008-04`) and does not
resolve the day. I could not independently confirm which calendar day is correct (SLAC's own
news archive no longer serves the original announcement; I did not fabricate a "corrected"
day from memory per A17). Fixed: downgraded `confidence` from `verified` to `approximate` and
added a note explaining the ambiguity, in all four places this date is used
(`experiments/babar.json` ×2 intervals, `detectors/babar.json` ×2 intervals,
`collaborations/babar.json` ×2 intervals) plus a `missing_fields` entry in
`coverage/colliders-historical.json`. Did **not** guess a replacement day.

**3. Both top-quark result titles/names diverged from the papers' actual published titles.**
CDF's record read *"Observation of top quark production in ppbar collisions"* — lower-cased
and missing the published title's closing clause. The real title (confirmed verbatim via
`journals.aps.org/prl/abstract/10.1103/PhysRevLett.74.2626`) is *"Observation of Top Quark
Production in p̄p Collisions with the Collider Detector at Fermilab."* D0's record read
*"Observation of the top quark"* (lower case); the real title (PRL 74, 2632) is *"Observation
of the Top Quark."* Fixed both `title` and `name` fields in `results/cdf-top-quark-
observation-1995.json` and `results/d0-top-quark-observation-1995.json` (CDF rendered with
the repo's existing ASCII "ppbar" convention rather than introducing new Unicode), with a
note recording the correction and its source.

### P2 (2, both fixed/logged)

**4. D0's collaboration size is sourced from only one of two published figures, undisclosed.**
D0's own INSPIRE experiment description states *"At its peak, the DZero Collaboration
included 650 physicists from over 80 national and international research institutions from
21 countries"* — a different, larger figure than the 540 members / 90 institutions / 18
countries used in `collaborations/d0.json` (sourced to fnal.gov, 2014, `as_of` correctly set).
Both figures are genuine and simply describe different moments; CDF's analogous total-mass
conflict is explicitly documented in-file but this one was not. Fixed: added a note to
`collaborations/d0.json` recording the INSPIRE figure as an alternate and explaining why the
dated fnal.gov figure was kept as the primary `membership` value.

**5. Cross-team interval-precision mismatch (not fixed — out of this partition's files).**
The facilities-lead-owned `accelerators/fermilab-tevatron.json`, `slc.json` and `pep-ii.json`
records end their "operation" intervals at year precision (`2011`, `1998`, `2008`) while this
partition's SLD/BaBar/CDF/D0 records correctly use day/month precision sourced to specific
quotes. Not a contradiction (the year contains the day), and not a file this partition owns,
but noted here for the facilities lead.

### P0

None found. No fabricated dates, no invented coordinates, no misclassified `result_type`
(both papers say "Observation," matching `result_type: observation`; neither claims
"discovery"), no empty-result-as-proof-of-absence, no uncited `verified` critical value.

## Checked and confirmed correct (no fix needed)

- All INSPIRE `date_proposed`/`date_approved`/`date_started`/`date_completed` fields for all
  six experiments, exactly as recorded (including D0's date_completed=2001 vs. the record's
  own description text "ran from 2001 to 2011" conflict, which the researcher correctly
  resolved in favor of 2011 and documented — I independently re-derived the same conclusion
  from the same re-fetched record).
- CDF's total-mass conflict (4,500 t fnal.gov vs. 5,000 t 1988 NIM paper) and solenoid-field
  conflict (1.4 T INSPIRE vs. 1.5 T 1988 NIM paper): both genuinely present in the cited
  sources, correctly left unreconciled with an honest note per the source hierarchy — this
  is correct handling, not an error.
- Tevatron shutdown 2011-09-30, confirmed verbatim against `news.fnal.gov` and
  `fnal.gov/pub/tevatron/shutdown-process.html`.
- SLD interval history (1983 proposed → 1984-05-04 approved → Nov 1990 checkout → 1992 first
  data (22% polarization) → Feb 1993 second run (>60%) → 1998-06 completed), every quote
  verbatim-confirmed against the live SLD intro page.
- H1/ZEUS HERA shutdown: H1's own site text "H1 Operation (ended June 2007)" confirmed
  verbatim (month precision, honestly not upgraded to ZEUS's day-precision 2007-06-30, which
  is correctly labelled as corroboration only, not H1's own sourced day).
- BaBar's asymmetric-collider physics description, CP-violation goals, and organizing-meeting/
  name-adoption history, all confirmed verbatim against CERN Courier and the INSPIRE record.
- `result:cdf-top-quark-observation-1995` / `result:d0-top-quark-observation-1995`: `claim.quote`
  for both is genuinely verbatim from the abstract (D0's "We conclude that we have observed the
  top quark and measure its mass" is the abstract's closing sentence, confirmed against the raw
  arXiv abstract page — not a fabricated splice as I initially suspected); `significance` values
  (4.8σ / 4.6σ) and `date_kind: announcement` (1995-03-02, the Fermilab public-seminar date, is
  correctly distinguished from the papers' journal-received date of 1995-02-24 and arXiv-posted
  dates of 1995-03-02/03) are all accurate.
- No duplicate `src:` URLs/DOIs anywhere in `data/atlas/sources/` (checked all ~590 source
  files, not just this partition's 25); no duplicate INSPIRE recids across `experiments/*.json`;
  no name/alias collisions between CDF/D0/SLD/BaBar/H1/ZEUS and any other entity.
- `missing_fields` in `coverage/colliders-historical.json` is honest: D0/SLD/BaBar/H1/ZEUS
  genuinely lack numeric `key_specs` (solenoid field, calorimeter type) because no detector
  paper/TDR giving those numbers was fetched — confirmed by checking each cited abstract, which
  gives qualitative descriptions only (e.g. BaBar's NIM abstract mentions the CsI calorimeter
  and solenoid but never states 1.5 T). This is not fabrication-by-omission; it is correctly
  flagged as missing rather than filled from memory.
- `retrieval` field honesty: no `summary`-retrieval source carries a `quote`; every
  `journal_article`/`detector_paper` source is marked `partial` (abstract-only), consistent
  with what was actually fetched.
- Every `src:colliders-historical-*inspire-experiment-record` URL contains its own recid
  (A20 compliance).

## Unverifiable values

- BaBar's exact last-data calendar day (2008-04-07 vs. 2008-04-08) — see P1 finding #2.
  Left as an honestly-flagged ambiguity rather than a guess.
- D0/SLD/H1/ZEUS/BaBar numeric detector specs (solenoid fields, calorimeter details) — no
  full-text detector paper or TDR was fetched by the researcher or by me within this session's
  scope; correctly left absent rather than filled from general knowledge.

## Verdict

**Substantially sound, with one real fabricated-quote defect (fixed) and two precision/
completeness gaps (fixed/logged).** This partition's INSPIRE-derived facts (dates, status
history, descriptions) are unusually well verified — every one I independently re-fetched
matched exactly, down to preserved source typos. The one clear error (a paraphrased quote
presented as verbatim in two files) has been corrected. The BaBar day-precision and D0
collaboration-size items are not errors of fact so much as honesty gaps that are now closed.
`python -m hepgraph.atlas.validate` shows **0 errors** attributable to any file this partition
owns (checked across three separate runs while a concurrent session's edits to unrelated
`experiment:sage`/`facility:baksan-neutrino-observatory` records made the total error count
fluctuate between runs — none of those errors reference cdf/d0/sld/babar/h1/zeus or any
`src:colliders-historical-*` id).
