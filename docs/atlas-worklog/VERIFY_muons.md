# Independent verification — muons (Muon g-2, Mu2e, MEG, MEG II, Mu3e, COMET)

Verifier: the orchestrator (Claude Fable 5.1), 2026-09-18, because the Sonnet
verifier assigned to this domain was stopped before it reported. Every claim
below was re-fetched by the verifier, not taken from `docs/atlas-worklog/muons.md`.

## Records checked

`experiments/{muon-g-2,mu2e,meg,meg-ii,mu3e,comet}.json`, `detectors/{muon-g-2,mu2e}.json`,
`results/{muon-g-2-measurement-2021,muon-g-2-measurement-2023,muon-g-2-measurement-2025,meg-mu-to-e-gamma-limit-2016,meg-ii-mu-to-e-gamma-limit-2024}.json`,
`sites/{fermilab-mc-1-muon-campus,fermilab-mu2e-hall,j-parc-hadron-hall}.json`.

## Values re-fetched (11 sources)

| Claim | Source | Result |
| --- | --- | --- |
| g-2 2021 title "…to 0.46 ppm", "3.3 standard deviations greater than the standard model prediction" | arXiv:2104.03281 abstract | verbatim |
| g-2 2023 title "…to 0.20 ppm" | arXiv:2308.06230 abstract | verbatim |
| g-2 2025 title "…to 127 ppb", "(127 ppb) when combined with our previous results" | arXiv:2506.03069 abstract | verbatim |
| g-2 ring: "central orbit radius of 7.112 m", "chosen to be 1.45 T" | arXiv:1411.2555 full text (ar5iv) | verbatim (full text, not abstract) |
| g-2 start-up 2017-05-31; runs "from April 2018 to May 2023"; ring moved 2013; final measurement | news.fnal.gov 2025-06 | verbatim; article confirms data taking finished |
| MEG 2016: BR < 4.2 × 10⁻¹³ (90 % CL), "most stringent limit" | arXiv:1605.05081 abstract | verbatim |
| MEG II: < 7.5 × 10⁻¹³, combined < 3.1 × 10⁻¹³ (90 % C.L.) | arXiv:2310.12614 abstract | verbatim |
| Mu2e proposed 2008-10-18, approved 2010-08, "CD-3 approval for construction in June 2016", SES "about 2.5 × 10⁻¹⁷" | INSPIRE experiments/1108209 | verbatim |
| Mu2e "initial data collection scheduled to begin in 2027" | INSPIRE literature/3189846 abstract | verbatim after a capitalisation fix (P2) |
| Mu2e "25 m long superconducting solenoidal system" | INSPIRE literature/3189846 abstract and the PoS WIFAI2025 020 PDF | **not present** — P1, removed |
| Mu2e TDR title | arXiv:1501.05241 | verbatim; no solenoid length in the abstract |

## Findings

| Severity | Finding | Fix |
| --- | --- | --- |
| P1 | `experiment:mu2e` key spec and `detector:mu2e.specs.length` cited a 25 m solenoid-system quote that does not appear in the cited source's abstract or PDF text; no fetched source states the length. | Spec removed; detector length set to null with a note. |
| P2 | The 2027 quote capitalised "Initial" where the source has "initial". | Made verbatim. |
| P2 | Mu3e's construction interval is a one-month anchor (third pixel layer installed 2026-09) with approximate confidence; it drives the derived `construction` state honestly but understates the construction span. | Left; noted. |
| — | Sites MC-1, Mu2e hall, J-PARC Hadron Hall are geocoder campus points, `kind: campus`, `confidence: approximate`, with notes (A23). | Correct as recorded. |

P0: none. Result wording is conservative throughout (measurements and upper
limits; no discovery language). Flagship verdict: Muon g-2 — zero unresolved
factual contradictions; Mu2e — zero after the P1 removal.

## Not verified

MEG/MEG II/Mu3e/COMET INSPIRE experiment dates (INSPIRE records 1108527,
1679100, 1114537, 1108246) were not re-fetched in this pass; the MEG run
period 2009–2013 and MEG II 2021/2022 quotes were checked against the two arXiv
abstracts above.
