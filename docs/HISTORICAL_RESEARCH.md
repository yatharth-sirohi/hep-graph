# Historical connection evidence review

Reviewed 15 September 2026. This report describes a bounded review of records
needed for historical connection searches. It is not a catalogue-wide audit.
The application retrieves metadata on demand and retains it temporarily in RAM.

## Why deeper retrieval alone was insufficient

Two separate problems affected historical searches:

1. The earlier quick search examined too few researchers and publication pages.
2. Some source records have incomplete adviser classifications, incorrect author
   links, or editorial contributors represented as authors.

Following every upstream record reference without inspecting its meaning can
produce an incorrect shortcut. Conversely, treating every unclassified adviser
as a doctoral supervisor can manufacture genealogy. The implementation now
combines deeper retrieval, current-profile checks, and a small explicit source
correction list. The corrections never merge people by name or guess a
replacement identity.

## A documented Hostert–Dirac route

The final live search established this four-hop route:

| Connection | Evidence type | Representative source |
| --- | --- | --- |
| Matheus Hostert — Silvia Pascoli | Coauthorship; the native profile also records an uncurated PhD relation | [Light Sterile Neutrinos at νSTORM](https://inspirehep.net/literature/1601310), 2017, three authors |
| Silvia Pascoli — Serguey T. Petcov | Coauthorship | [Leptogenesis in the Neutrino Option](https://inspirehep.net/literature/1737512), 2019, five authors |
| Serguey T. Petcov — Dennis W. Sciama | Coauthorship | [Resonant neutrino spin flavor precession and supernova shock revival](https://inspirehep.net/literature/417257), 1996, four authors |
| Dennis W. Sciama ← Paul A. M. Dirac | Doctoral supervision; arrow shows adviser to student | [American Institute of Physics oral-history catalogue](https://history.aip.org/history/catalog/icos/33994.html) |

The AIP catalogue explicitly identifies Dirac as Sciama's thesis adviser and
Sciama's Cambridge PhD. George Ellis's [firsthand obituary](https://www.nature.com/articles/35001716)
corroborates the Dirac/Mach-principle doctoral context. Sources differ on whether
to give 1952 or 1953, so the overlay leaves the degree year unspecified.

The initial bounded review had found only generic descriptions of Sciama as
Dirac's research student. The archival thesis-adviser record provides the
additional evidence needed for this exact doctoral edge. It applies only to
the already resolved profiles `1011729` and `989544`.

This is a mixed coauthor/doctoral connection. It does not establish that
Hostert's doctoral ancestry runs through Petcov, Sciama, Bohr, or Landau.
The route's first hop has independent coauthorship evidence, so its validity
does not depend on upgrading the uncurated Hostert profile assertion.

## Doctoral-source policy

The native pipeline accepts an adviser edge only when the same adviser entry
contains a resolved record reference and explicitly states a PhD relationship.
It preserves whether the relation was curated. An `other` adviser type is not
automatically doctoral supervision.

Three narrowly sourced external relationships supplement incomplete native
classifications:

- Fowler → Dirac, from [Cambridge DAMTP](https://www.damtp.cam.ac.uk/events/dirac/dirac/highlights.html).
- Kleiner → Einstein, from [ETH Library](https://library.ethz.ch/en/collections-and-archives/platforms/einstein-online/ausserordentlicher-professor-an-der-universitaet-zuerich-profes.html).
- Dirac → Sciama, from the [AIP oral-history catalogue](https://history.aip.org/history/catalog/icos/33994.html).

Each keeps its institutional source URL, access date, source kind, and uncertainty
label. Both exact current INSPIRE profiles must be present. The original native
record is retained separately.

The reviewed Hostert profile lists Pascoli with a PhD classification but an
uncurated relation. Pascoli's Petcov entry is classified `other`; the reviewed
Petcov data did not establish a further adviser chain. The reviewed evidence
therefore does not justify inserting a doctoral connection to Bohr or Landau.
Shared papers, influence, friendship, and institutional overlap remain distinct
from doctoral supervision.

## Rejected shortcuts and identity hazards

The exact correction list and supporting sources are maintained in
[HISTORICAL_SOURCES.md](HISTORICAL_SOURCES.md). Examples found during the live
tests include:

- An Einstein paper linked Bruria Kaufman's author slot to an S. B. Kaufman profile.
- The 1938 Einstein–Infeld–Hoffmann paper linked Banesh Hoffmann's author slot
  to the Bernd Hoffmann profile.
- Other Einstein records linked Otto Stern to Mark Stern and E. G. Straus to
  Emanuel Strauss.
- Papers credited to C. S. Chiu or Christie Chiu appeared under Charles B. Chiu's
  stable profile. Short `C. Chiu` occurrences become ambiguous when the same
  retrieved corpus contains that conflict; full matching names remain usable.
- An initials-only `Lee, K.K.` profile linked publications credited to many
  incompatible full names, including Kuen Lee and Kyeongwon Lee. The guard
  withholds that profile's author links when the retrieved corpus demonstrates
  this unresolved identity collision.
- A 2025 laser-metrology paper credited **Micheal Born** but linked his name to
  **Max Born**. The [publisher's byline](https://doi.org/10.1117/12.3075174)
  confirms the conflict. Comparing only the initial M would miss it; fully
  stated given names are now checked against all available public name forms.
- An initial-only H. Schulz attribution in a 1971 paper could not safely be
  resolved to the modern Holger Schulz profile. That exact disputed occurrence
  is withheld pending disambiguation.
- Fred Hoyle's record classified a Dirac relationship as PhD supervision, but
  [Hoyle's biographical account](https://www.hoyle.org.uk/A-Singular-Life/Years-of-Joy/)
  states that he never applied for the doctorate.
- John Polkinghorne's adviser array crosses names and stable references. His
  [firsthand account](https://www.the-scientist.com/gell-mann-opened-my-eyes-64150)
  identifies Kemmer and Salam as his successive PhD supervisors.

Exact erroneous author occurrences become unresolved while their publications,
source IDs, and full author counts remain. The guard does not insert a guessed
person. Four individually reviewed sessions, correspondence/translation
collections, and retrospective editorial records are excluded from the
research-coauthor view.

## A posthumous date does not by itself disprove coauthorship

An earlier broad Hostert–Feynman test found a route through James M. Cline's
*Feynman Lectures on the Strong Interactions*. The [author-supplied arXiv record](https://arxiv.org/abs/2006.08594)
states that parts were finalized in collaboration with Feynman during the
1987–88 course. The displayed 2020 date is the release date, not the year of
the collaboration. The arXiv version was withdrawn over submission licensing;
that status is material context when using this particular evidence.

This differs from attributing a new collaboration to a deceased person without
evidence of joint work. The app's paper policy follows eligible INSPIRE article
and conference-paper classifications, which may include lecture preprints.
Users should inspect the linked work before interpreting any edge as an
ordinary journal research collaboration. The stricter repeated-work filter
provides a separate adversarial test of routes beyond this one-work connection.
In the final release run that optional `min_shared=2` stress case did not
finish within its 180-second allowance and was cancelled with an explicit
incomplete state. The professor sequence uses the direct Feynman–Wheeler
result instead.

## Limits of this review

Current-profile and initial checks detect clear conflicts; they cannot establish
the identity of every historical initial-only author. A source correction list
is necessarily incomplete. Every returned route exposes its actual supporting
records and source uncertainty so a researcher can inspect it.

An unsuccessful live search means that the retrieved evidence did not establish
a path within the selected filters and allowance. It does not prove that no
path exists in all of INSPIRE. A multi-hop route is shortest in its retrieved
graph; global shortestness remains unproven.

The parser's own adversarial tests also cover legitimate initials and accents:
`V.F. Weisskopf` must match Victor Frederick Weisskopf, and accented given names
must not split into extra initials. A correction that silently removes valid
edges can be as harmful to a connection search as accepting an incorrect link.
