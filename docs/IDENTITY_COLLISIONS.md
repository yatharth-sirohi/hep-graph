# Identity collision review

Reviewed 15 September 2026. A real paper and a real author profile can still be joined incorrectly by upstream metadata. HEP Graph validates the binding before accepting a path edge. It withholds disputed derived links, retains source provenance, and continues searching. It never edits INSPIRE or guesses a replacement profile.

## Peter Gabriel Bergmann versus Philip Bergmann

A candidate Erin Visser–Einstein route used the 2022 paper **A large area efficient trigger scintillator with SiPM read out**, [INSPIRE 2150122](https://inspirehep.net/literature/2150122). Its “P. Bergmann” occurrence points to [Peter Gabriel Bergmann, 1016635](https://inspirehep.net/authors/1016635), whose public profile records death in October 2002.

The contemporary identity is supported by [Jülich's JuSER record 911347](https://juser.fz-juelich.de/record/911347) and its local author authority. A [primary HADES conference paper](https://inspirehep.net/files/15077742956d44ce6ab5147debdf04ca), associated with [INSPIRE 2606257](https://inspirehep.net/literature/2606257), prints **Philip Bergmann**. This full given name contradicts Peter Gabriel Bergmann. Chronology is a warning requiring review; death alone does not make posthumous publication impossible.

Five exact misattributed occurrences are permanent regression cases:

| Work ID | Earliest year | Recorded byline | Full author count |
| --- | ---: | --- | ---: |
| 2150122 | 2022 | Bergmann, P. | 8 |
| 2627214 | 2023 | Bergmann, P. | 91 |
| 2623742 | 2023 | Bergmann, P. | 88 |
| 2606257 | 2022 | Bergmann, Philip | 115 |
| 1665003 | 2017 | Bergmann, Philip | 10 |

The initial four-hop Visser–Einstein candidate was rejected. The repaired search returned a ten-hop evidenced route through Gardiner, Isaacson, Schulz, Petcov, Sciama, Hawking, Penrose, Newman and the historical Bergmann. It retains the valid historical Bergmann–Einstein edge. This is a verified route, not a claim of global shortestness.

The earlier part of the rejected candidate was genuine: [work 2960880](https://inspirehep.net/literature/2960880) has **Erin Visser and Corrado Gatto** as coauthors. It is not a Matt Visser paper. The failure was the later authorship-to-person assignment at 2150122.

### General safeguard

A matching initials-only byline more than two years after a profile's documented death year is withheld pending review. Current public death dates are retained only when supplied; unknown/invalid dates do not trigger this rule. Fully stated matching names and the publication-delay window remain eligible unless another conflict exists. Full given-name contradictions are checked independently. Original full author counts remain unchanged.

Coverage records `identity_lifetime_review` or `identity_full_name_conflicts`, including exact work/person IDs and the reason. No publication is reassigned to a guessed modern author.

## Chen-Ning Yang: adviser names point to the opposite records

[INSPIRE author 982820](https://inspirehep.net/authors/982820) contained two PhD adviser entries in the inspected response:

| Stated adviser name | Referenced ID | Current referenced person |
| --- | --- | --- |
| Teller, Edward | 1020970 | Enrico Fermi |
| Fermi, Enrico | 1019685 | Edward Teller |

The internal contradiction is sufficient to withhold both native relation assertions pending review. HEP Graph does not reverse these IDs or assume that doing so establishes the correct doctoral relationships. It records `identity_phd_conflicts` and permits separately evidenced coauthorship or institutional sources to stand independently.

Tests reproduce the exact mismatch, confirm that no guessed edge is created, preserve the original payload, and retain matching or uncertain adviser-name forms.

## Previously found collisions

The historical source review also records Bruria/S.B. Kaufman, Banesh/Bernd Hoffmann, Charles/Christie Chiu, mixed K.K. Lee identities, Micheal/Max Born, and specific editorial or session-participant attributions. [Historical sources](HISTORICAL_SOURCES.md) describes the narrowly reviewed exclusions; general name/initial regressions remain in the suite.

## Legitimate names must remain usable

Known aliases and Unicode variations are preserved. A real lookup regression verified “Gerard ’t Hooft” against canonical “Gerardus ’t Hooft” ([1019113](https://inspirehep.net/authors/1019113)); the app now searches documented canonical, preferred and variant fields. Composed and decomposed accents share a lookup key. These changes improve selection without merging distinct numeric identities.

## Limits

The guard is deliberately conservative. A plausible abbreviated name can remain uncertain, and a catalogue can contain errors these checks cannot detect. An accepted route always retains inspectable source evidence; the app does not claim universal identity resolution. Suspicious data should be reviewed against original papers or authoritative institutional records.
