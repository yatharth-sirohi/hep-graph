# Audited historical overlay

`hepgraph.historical` is a deliberately tiny, pure overlay. It does not fetch
records, create people from display names, write a database, or change INSPIRE
source metadata. It can add an edge only after both exact INSPIRE author IDs are
already resolved in the supplied snapshot **with `profile_status: "profile"`**.
Literature-only placeholders and unresolved adviser references are raw evidence,
not sufficient identity verification for an external historical relation.

## Institutional doctoral-supervision supplement

| Adviser → student | Exact INSPIRE IDs | Degree year | Institutional evidence | Overlay source record |
| --- | --- | ---: | --- | --- |
| Ralph Howard Fowler → Paul A. M. Dirac | `1035527` → `1011729` | 1926 | [Cambridge DAMTP](https://www.damtp.cam.ac.uk/events/dirac/dirac/highlights.html) says Dirac became a research student under Fowler's supervision and received his PhD in 1926. | `supplemental:cambridge-damtp-fowler-dirac` |
| Alfred Kleiner → Albert Einstein | `1049952` → `1010907` | 1905 | [ETH Library](https://library.ethz.ch/en/collections-and-archives/platforms/einstein-online/ausserordentlicher-professor-an-der-universitaet-zuerich-profes.html) says Einstein obtained the Zurich doctorate with the work under Professor Kleiner. The [ETH Research Collection thesis record](https://www.research-collection.ethz.ch/handle/20.500.11850/139872) independently identifies the doctoral thesis and Kleiner as examiner. | `supplemental:eth-library-kleiner-einstein` |
| Paul A. M. Dirac → Dennis Sciama | `1011729` → `989544` | Unspecified | The [AIP Niels Bohr Library oral-history catalogue](https://history.aip.org/history/catalog/icos/33994.html) explicitly identifies Dirac as thesis adviser and Sciama's Cambridge PhD. The [firsthand obituary by George Ellis](https://www.nature.com/articles/35001716) corroborates the Dirac/Mach-principle thesis context. Sources differ on 1952/1953, so the supplement leaves the year empty. | `supplemental:aip-oral-history-dirac-sciama` |

Every supplement relation has `degree: "PhD"`, its exact source URL,
`source_kind: "institutional_historical_supplement"`, access date `2026-09-15`,
and `uncertainty: "external_institutional_historical_source"`. That uncertainty
is deliberate: the fact is explicit, but the evidence is external to the
selected INSPIRE profile data and must stay identifiable as such.

The overlay does **not** add Hostert → Bohr or Landau. The bounded review found
Hostert → Pascoli only as an uncurated INSPIRE PhD profile assertion; Pascoli →
Petcov is `degree_type: other`, and the proposed continuation to Bohr or Landau
has no explicit institutional doctoral source and/or lacks a resolved person
record. See [the research report](HISTORICAL_RESEARCH.md).

## Exact coauthorship exclusions

The overlay removes only these exact source IDs from its derived `works` view
and records each exclusion in `coverage.historical_coauthorship_exclusions`.
It uses no title, date, name, or document-type heuristic. Normalization can
group exact DOI/arXiv versions under one work; if an excluded source ID is mixed
with any unreviewed `source_ids`, the overlay retains the work and records the
blocker in `coverage.historical_coauthorship_exclusion_conflicts`. It therefore
does not erase a potentially independent true work merely because one merged
source is historical attribution.

| Work | Reason for exclusion from research-coauthor calculations |
| --- | --- |
| [`187326`](https://inspirehep.net/literature/187326) | Special-session participant list, not a research collaboration. |
| [`361713`](https://inspirehep.net/literature/361713) | Posthumous Dirac–Tamm correspondence publication, not a 1993 Dirac collaboration. |
| [`4676`](https://inspirehep.net/literature/4676) | Translation collection, not a research collaboration among the listed historical authors. |
| [`48254`](https://inspirehep.net/literature/48254) | Retrospective/editorial attribution on an unpublished Einstein lecture, not a research collaboration. |

These exclusions are narrowly scoped to the reviewed records. They do not make
a general claim about all historical INSPIRE authorship records and do not alter
stored INSPIRE data.

## Exact contradictory native adviser relation excluded

The INSPIRE profile for John C. Polkinghorne (`1019944`) has crossed adviser
names and stable references: the row pointing to Dirac (`1011729`) displays
Salam, while a different row pointing to Salam (`990582`) displays Dirac. His
own account identifies Kemmer and Salam as his successive PhD supervisors and
describes Dirac's role as lecturing, rather than direct research supervision:
[“Gell-Mann Opened My Eyes”](https://www.the-scientist.com/gell-mann-opened-my-eyes-64150).

The broader Royal Society archive summary says that Polkinghorne studied under
Salam and Dirac, but it does not distinguish PhD supervision from teaching. The
firsthand account is more specific for this exact conflict. The old Trinity Hall
PDF citation returned HTTP 404 and is not used.

Accordingly, the overlay excludes only native
`adviser=1011729`, `student=1019944`, `source_record=1019944`, under
`coverage.historical_profile_relation_exclusions` with reason
`native_adviser_reference_conflicts_with_firsthand_phd_supervisor_account`.
It does not manufacture a Salam → Polkinghorne edge, replace a person ID from a
name, or remove a separately sourced doctoral relation.

The same audit key records the following exact native-profile correction:
`adviser=1011729`, `student=1005469`, `source_record=1005469` is excluded as
`research_supervisor_without_doctorate_in_native_profile`. Fred Hoyle's
biographical account says that Dirac became his final **research supervisor**
but that Hoyle “never applied for a PHD”:
[Years of Joy](https://www.hoyle.org.uk/A-Singular-Life/Years-of-Joy/). A
research-supervision label is therefore not admitted as doctoral genealogy.
This correction applies only to that exact native relation and preserves any
independently sourced future doctoral evidence.

## Exact authorship occurrence correction

INSPIRE literature record [`44740`](https://inspirehep.net/literature/44740),
the 1955 Einstein paper *A New Form of the General Relativistic Field
Equations*, lists “Kaufman, B.” with stable profile `2203900`. That profile is
named **S.B. Kaufman**, while the published Annals article is by Albert Einstein
and **Bruria Kaufman**, as shown by the publication's
[DOI record](https://doi.org/10.2307/2007103). The record is a valid research
publication; only its exact occurrence `(source_record=44740, person=2203900)`
is suppressed.

The overlay keeps the work and its upstream `author_count: 2`, removes only the
wrong resolved person occurrence, and raises `unresolved_count` to reflect the
now-unresolved author slot. It records the correction under
`coverage.historical_authorship_exclusions`. It does **not** add Bruria
Kaufman, search for a substitute profile, or perform a name merge. If this
source is combined with an unreviewed source ID through DOI/arXiv
normalization, it leaves the entire authorship list unmodified and writes
`coverage.historical_authorship_occurrence_conflicts` instead.

### Additional exact Einstein coauthor-profile corrections

The same occurrence-only treatment applies to three additional, independently
checked Einstein records. Each paper remains in the graph with its upstream
author count and source IDs; only the erroneous resolved profile occurrence is
made unresolved. No correct profile is inferred from a name.

| Work and erroneous profile occurrence | Evidence for the paper's author | Why only that occurrence is excluded |
| --- | --- | --- |
| [`41231`](https://inspirehep.net/literature/41231), `1005792` | The [published DOI record](https://doi.org/10.2307/1968714) is the Einstein–Infeld–Banesh Hoffmann 1938 paper; the [IAS archive](https://albert.ias.edu/server/api/core/bitstreams/30f212b7-f48a-413d-8abb-38110acc225b/content) identifies Banesh Hoffmann in the contemporary Einstein/Infeld context. | The linked INSPIRE profile is **Bernd Hoffmann**. |
| [`42599`](https://inspirehep.net/literature/42599), `987542` | Wiley's [publisher page](https://doi.org/10.1002/andp.2005517S148) credits Einstein and **O. Stern**. | The linked INSPIRE profile is **Mark A. Stern**. |
| [`44738`](https://inspirehep.net/literature/44738), `1024083` | The [JSTOR issue record](https://www.jstor.org/stable/i307229) credits Einstein and **E. G. Straus** for DOI `10.2307/1969231`. | The linked INSPIRE profile is **Emanuel Alexandre Strauss**; other Einstein records separately link Ernst G. Straus. |

These three rows are recorded under `coverage.historical_authorship_exclusions`
with their exact source record, profile ID, reason, and publication URL.

The same exact-occurrence policy applies to [`74757`](https://inspirehep.net/literature/74757), a 1971 eight-author Chicago experiment paper. Its historical
initial-only “Schulz, H.” occurrence is linked to modern Holger Schulz
(`1069266`). The available profile and historical initial-only paper attribution
do not resolve that identity safely. The overlay treats it as a disputed
historical-initials link pending disambiguation and suppresses only
`(source_record=74757, person=1069266)` with reason
`historical_initial_only_author_conflicts_with_modern_stable_profile`; it does
not identify the 1971 H. Schulz, remove the valid multi-author paper, or use a
name-derived substitute.
