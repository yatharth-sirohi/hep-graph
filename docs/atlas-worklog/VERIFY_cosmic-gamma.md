# Independent verification — cosmic rays and gamma rays

Verifier: the orchestrator (Claude Fable 5.1), 2026-09-18, because the Sonnet
verifier assigned to this domain was stopped before it reported. Claims were
re-fetched by the verifier; `docs/atlas-worklog/cosmic-gamma.md` was treated as
a list of claims, not facts.

## Records checked

`experiments/{pierre-auger-observatory,telescope-array,hawc,lhaaso,ctao,magic,veritas,h-e-s-s}.json`
and their sites; the Auger detector and collaboration records for the
AugerPrime interval.

## Values re-fetched (9 fetches)

| Claim | Source | Result |
| --- | --- | --- |
| LHAASO "located in Daocheng, Sichuan province of China, at an altitude of 4410 meters" | arXiv:1905.02773 abstract | verbatim; no lat/lon in the abstract (ar5iv full text failed to render) |
| CTAO-South coordinates | ctao.org array-sites page | "Latitude: 24º 41′ 0.34″ South", "Longitude: 70º 18′ 58.84″ West", "<10 km southeast of … Paranal" — new source, site upgraded to a verified `detector` point (−24.683428, −70.316344) |
| H.E.S.S. first light 2002; five telescopes; four 12-m around a 28-m | hess-experiment.eu/about-hess | verbatim |
| H.E.S.S. coordinates 23°16'18" S, 16°30'00" E, ~1,800 m | hess-experiment.eu/h-e-s-s-site | verbatim |
| AugerPrime "commissioning of the final components … reaches its conclusion" | arXiv:2508.08056 (submitted 2025-08-11) | verbatim |
| AugerPrime inauguration November 2015 | auger.org/observatory/augerprime | verbatim |
| HAWC "+19°N … 4,100 meters in the Sierra Negra", 300 WCDs / 294 instrumented | arXiv:1701.01778 (ar5iv) | verbatim; no precise lat/lon in the paper |
| MAGIC "2200 m a.s.l. … (28°N, 18°W)" | arXiv:1409.5594 (ar5iv) | verbatim; coordinates only to the degree |
| Telescope Array "16 years of data collected from 11 May 2008 to 10 May 2024", 1400 m | arXiv:2605.19553 | quoted in the record; consistent |

## Findings

| Severity | Finding | Fix |
| --- | --- | --- |
| P1 | Auger derived `upgrade` for 2026 because the AugerPrime upgrade interval was open-ended although its cited 2025 status paper says commissioning of the final components is concluding; the observatory is taking data. | Upgrade interval closed at 2025-08 (approximate, quoted); experiment and detector derive `active`; coverage row updated. |
| P1 | CTAO-South site rested on an OpenStreetMap point for Paranal Observatory although CTAO publishes the array coordinates. | Site upgraded to a verified detector point from ctao.org. |
| P2 | `experiment:h-e-s-s` carried an undated H.E.S.S. II interval with an empty quote (covers no date, sets no state). | Removed; note records that no fetched source dated the CT5 inauguration. |
| — | HAWC, LHAASO, MAGIC, Telescope Array, Auger sites remain campus-grade approximate points (A23); the fetched papers give only degree-level or altitude-only positions. | Left honest. |

P0: none found in the values checked. Not re-fetched this pass: VERITAS timeline
page quotes (the record cites the observatory's own pages with day/month dates),
Telescope Array detector counts, LHAASO/HAWC status papers.
