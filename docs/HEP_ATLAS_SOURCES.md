# HEP Atlas source catalogue (v0.2, 2026-09-17)

Companion to `docs/HEP_ATLAS_ONTOLOGY.md` (the data contract, §3.14 "Source"
and amendments A7/A18/A20/A22) and `docs/HEP_ATLAS_RESEARCH_METHOD.md` (§1
"Source hierarchy", which states the ordering principle this document only
tabulates). Where this document and the ontology disagree, the ontology's
v0.2 amendments win.

This document exists so that a research agent, given a URL, can decide in one
lookup: which `source_type` it is, what `rank` that implies, what the record
should look like, what it may and may not be cited for, and how the link
checker will treat it later.

---

## 1. What `source_type` and `rank` mean

Every `data/atlas/sources/<slug>.json` file declares a `source_type`. `rank`
is **derived** from `source_type` by the build (A7) and must never be
hand-authored; a source file that includes a `rank` key triggers the
"derived fields present in data files" warning (A12). Rank is a
**distance-to-the-fact** score, not a quality score (research method §1.1):
it says how close the publishing party stands to the fact being cited, so
that when two sources disagree the atlas has a mechanical tie-break. A PDG
review (rank 7) can still be the *right* source for a claim a rank-1 page
does not make (a world-average number), because rank decides ties between
sources of comparable topic fit, not which source is "better" in general.

## 2. The full type-to-rank table

| rank | `source_type` | what it is |
| --- | --- | --- |
| 1 | `official_experiment_site` | the collaboration's own web pages |
| 2 | `official_facility_site` | the host laboratory's or observatory's own web pages |
| 3 | `experiment_registry` | the CERN Greybook |
| 3 | `inspire_experiment_record` | an INSPIRE `/experiments/<recid>` record |
| 4 | `design_report` | a CDR, TDR, technical proposal or letter of intent |
| 5 | `detector_paper` | the instrument paper describing a detector |
| 6 | `hepdata` | the numbers behind a published figure or table |
| 7 | `pdg` | a Review of Particle Physics review chapter |
| 8 | `institution_page` | a member institution's own group or department page |
| 8 | `geocoder` | ROR, GeoNames, OpenStreetMap/Nominatim |
| 9 | `result_page` | a collaboration's own public result page |
| 9 | `press_release` | a laboratory or collaboration press office |
| 9 | `project_document` | a funding-agency or community strategy document (P5, ESPP, a roadmap) |
| 10 | `journal_article` | a refereed publication |
| 10 | `arxiv` | a preprint |
| 10 | `inspire_literature_record` | an INSPIRE `/literature/<recid>` record |
| 12 | `wikipedia` | Wikipedia |
| 12 | `wikidata` | Wikidata |
| 12 | `secondary` | anything else: news articles, blog posts, conference talks, theses used only as pointers |

`inspire_record` (the undifferentiated v0.1 type) is retired; every INSPIRE
citation must say whether it is an `/experiments/` or a `/literature/` record
(A18). Two `source_type`s can share a rank (`experiment_registry` and
`inspire_experiment_record` both rank 3; `institution_page` and `geocoder`
both rank 8; `result_page`, `press_release` and `project_document` all rank
9) because they sit at the same distance from the fact even though they are
different kinds of document — the rank does not need to be a strict order,
only a tie-break.

## 3. Each type in detail

### `official_experiment_site` (rank 1)

**What it is.** The collaboration's own website: home page, physics-goals
page, detector-overview page, institutions/members list, news page.
**URL pattern.** No fixed pattern; typically the collaboration's own domain
(`t2k-experiment.org`, `icecube.wisc.edu`, `dunescience.org`). A page hosted
on a laboratory's domain but written and maintained by the collaboration
(e.g. a CERN-hosted experiment microsite) still counts as
`official_experiment_site`, not `official_facility_site` — the test is who
wrote it, not who hosts it.
**Cite it for.** Identity, aliases, current physics goals, current member
institution lists (`official_institution_list` evidence class), current
status in the collaboration's own words, `links.website`.
**Reliability caveats.** A collaboration site can lag its own detector
(construction pages that were never updated after commissioning); check the
page's own "last updated" wording before trusting a status. It is not
neutral about significance wording — still use the collaboration's own
`result_type` vocabulary (research method §6.2), but do not let a homepage's
enthusiasm override the paper's actual claim.
**Link checker.** Collaboration sites are the most likely to reorganise
after a major milestone (post-discovery redesign, decommissioning). A 404
here is common enough that it does not by itself imply the underlying fact
is wrong — but if this was the *sole* source of a `verified` value, the
value is listed "review required" (A22), never silently kept or dropped.

### `official_facility_site` (rank 2)

**What it is.** The host laboratory's or observatory's own pages: history,
accelerator complex pages, "about us" pages.
**URL pattern.** The laboratory's own domain (`fnal.gov`, `home.cern`,
`j-parc.jp`, `lngs.infn.it`). CERN's own experiment-agnostic pages (the
accelerator complex, the North Area) are `official_facility_site`; a page
about one experiment hosted at CERN is `official_experiment_site` if the
collaboration wrote it.
**Cite it for.** Facility identity, founding and closure dates, accelerator
and beamline specs the lab itself publishes, `facility.operator_text` when
the lab states who operates it.
**Reliability caveats.** Laboratory history pages compress decades into a
paragraph; treat a bare year as `approx: true` unless the page gives a
month or day. Do not use a facility's overview page as the source for a
specific experiment's own physics claims — the facility is not the
experiment's authority.
**Link checker.** Laboratory sites are the most stable rank ≤ 2 sources
(institutional domains rarely disappear), but URL structure changes across
site redesigns are common; the link checker's `archive_url` field is
particularly worth filling for these.

### `experiment_registry` (rank 3)

**What it is.** The CERN Greybook, the closest thing to an official registry
of approved CERN experiments (codes, approval dates, spokesperson lists).
**URL pattern.** `https://greybook.cern.ch/experiment/detail?id=<code>`.
**Cite it for.** Approval status and dates, experiment codes, spokesperson
history, for CERN-based experiments only.
**Reliability caveats.** Covers CERN only; do not use it as a stand-in for
laboratories that keep no equivalent public registry (most non-CERN labs).
Greybook entries are administrative, not physics: never cite it for a result
or a technical spec.
**Link checker.** Stable URL scheme; a broken Greybook link on an old
experiment is itself informative (the record may have been merged or
retired) and worth a `notes` entry rather than silent removal.

### `inspire_experiment_record` (rank 3)

**What it is.** An INSPIRE `/experiments/<recid>` record: canonical name,
institution list, dates, linked literature.
**URL pattern.** `https://inspirehep.net/experiments/<recid>` (the human
page) or `https://inspirehep.net/api/experiments/<recid>` (the JSON API,
also acceptable and already used in several existing source records in this
atlas — either URL form is valid as long as `<recid>` is present and the
record-level `sources` check in A20 can find the id in the URL).
**Cite it for.** `external.inspire_experiment`, canonical/alias names,
approval and running dates when the facility or collaboration site does not
give them, a first-pass institution list (evidence class
`inspire_author_profile` is for *people*; for the experiment's own
institution list this is `official_institution_list`-adjacent only when
INSPIRE is explicitly reproducing the collaboration's own list — check the
record's own sourcing before treating it as authoritative).
**Reliability caveats.** INSPIRE experiment records are maintained by
librarians from collaboration input and can lag; a discrepancy between
INSPIRE and the collaboration's own site is resolved in the collaboration's
favour (research method §1, "primary over reporting").
**Link checker.** Stable; recids do not change. Rate-limited per
`RESEARCH_AGENT_RULES.md` (one request per 10 s per agent) — do not batch
INSPIRE lookups.

### `design_report` (rank 4)

**What it is.** A conceptual design report (CDR), technical design report
(TDR), technical proposal or letter of intent.
**URL pattern.** Usually an arXiv id (`arxiv.org/abs/...`) or a DOI; multi-
volume reports are one `document:` record with `volumes[]` (research method
§7), but each volume that is separately cited as a *source* for different
claims may still need its own `src:` record if it has its own arXiv id/DOI.
**Cite it for.** Design-stage physics goals, planned key specs (mark
`planned: true` per A4/A21 if the number is a design target, not an
as-built measurement), planned schedule dates.
**Reliability caveats.** A design report describes what was *planned*;
never use it as the source for what was actually built or achieved without
also checking a detector paper or a status report. `Interval.start.planned:
true` intervals sourced only from a design report may not carry status
`active`/`commissioning`/`completed`/`decommissioned` (A21).
**Link checker.** arXiv/DOI links are stable; treat a 404 as a strong signal
to re-resolve via DOI rather than drop the citation.

### `detector_paper` (rank 5)

**What it is.** The instrument paper: "The XYZ Detector", published in
NIM/JINST/similar, describing the as-built apparatus.
**URL pattern.** arXiv id or DOI (journal, typically NIM A or JINST).
**Cite it for.** As-built key specs (mass, channel count, resolution),
`technology_class`, `subsystems[]`, and — per A17 — coordinates of `kind:
detector`/`underground_lab` may rely on a detector paper (rank 5, well under
the rank-8 floor).
**Reliability caveats.** A detector paper is a snapshot at publication; an
upgraded detector needs its own paper or a status update, and the older
paper's specs should not silently stand in for the current configuration —
give the detector a fresh interval instead of overwriting the number.
**Link checker.** Same as `design_report`.

### `hepdata` (rank 6)

**What it is.** The numeric tables and machine-readable data behind a
published figure or table (hepdata.net records).
**URL pattern.** `https://www.hepdata.net/record/ins<recid>` or
`https://www.hepdata.net/record/<hepdata-id>`.
**Cite it for.** Exact numeric values in `result.key_value`, where the
published paper gives a plot but HEPData gives the underlying number;
`document.hepdata`/`result.hepdata` cross-links.
**Reliability caveats.** HEPData reproduces what the collaboration
submitted; if HEPData and the paper's text disagree, treat it as a
`purpose fit` case (research method §10.2.3) and prefer HEPData for a number
that is "the numbers behind a figure," but the paper's text for the
narrative claim (discovery/observation/evidence wording).
**Link checker.** Stable INSPIRE-linked ids.

### `pdg` (rank 7)

**What it is.** A Review of Particle Physics chapter (the Particle Data
Group's biennial review).
**URL pattern.** `https://pdg.lbl.gov/<year>/reviews/<slug>.pdf` for the
current edition's PDF chapters; the review's own author list and revision
date appear on the chapter's first page and should be recorded in the source
record's `publisher` field (e.g. "F. Takahashi et al. (Particle Data Group),
Int. J. Mod. Phys. A 41, 2630011 (2026)").
**Cite it for.** World-average numbers, status summaries that synthesise
many experiments, standard definitions and observables vocabulary — this is
what PDG is *for* (research method §1.1), so it outranks a rank-1
collaboration page for a world average even though its rank number is
higher.
**Reliability caveats.** A PDG review reflects its own revision date, not
"now" — always record the chapter's stated revision month, since a newer
experimental result can post-date the review PDG cites. Do not treat PDG as
a source for a specific collaboration's own wording of a result
(`result.claim.quote` must come from the publication or the collaboration's
own page, never PDG — A16).
**Link checker.** PDG reissues a full edition periodically and retires old
URLs; `archive_url` is worth setting proactively rather than after a 404.

### `institution_page` (rank 8)

**What it is.** A member institution's own group or department page stating
its participation in a collaboration.
**URL pattern.** The institution's own domain, no fixed structure
(university physics department group pages, national-lab division pages).
**Cite it for.** Evidence class `institutional_page` in membership rows
only (research method §4.1); campus/headquarters coordinates when no better
source exists.
**Reliability caveats.** These pages go stale (a group's page can survive
years after its members leave a collaboration) and are frequently
unmaintained after a faculty member departs. Never the sole source for a
coordinate of `kind: detector`/`underground_lab` (A17 floor is rank 8 and
these are excluded specifically). Rank 8 sources may support a `verified`
value only in combination with the rank ≤ 10 ceiling rule; they are commonly
paired with a rank ≤ 5 source for anything beyond membership.
**Link checker.** High turnover; expect more 404s here than any other rank.

### `geocoder` (rank 8)

**What it is.** ROR, GeoNames, OpenStreetMap/Nominatim — services that
return a coordinate for an organisation or place.
**URL pattern.** `https://ror.org/<ror-id>` / `https://api.ror.org/v2/organizations/<ror-id>`
for institutions; GeoNames/Nominatim URLs for places without a ROR entry.
**Cite it for.** `kind: campus` or `kind: headquarters` coordinates only
(A17, ontology §2.5). Also a source of `external.ror` for an institution.
**Reliability caveats.** A geocoder gives you the organisation's registered
address, which is very often not where a specific detector or underground
lab actually sits (SURF is nowhere near a Sanford-branded campus centroid).
This is exactly why geocoder coordinates are barred from `kind:
detector`/`underground_lab` — the validator enforces this and it is not a
formality.
**Link checker.** ROR ids are stable and versioned; GeoNames/Nominatim
results can shift if the underlying gazetteer record is edited.

### `result_page` (rank 9)

**What it is.** A collaboration's own public page presenting one result
(distinct from the general `official_experiment_site`, which is about the
experiment as a whole).
**URL pattern.** Same domain as the collaboration's official site, usually
under a `/results/` or `/physics/` path, or a public-note PDF.
**Cite it for.** `result.claim.quote` is explicitly allowed to come from a
collaboration's own result page (A16) — this is one of only two allowed
sources for that field, the other being the publication itself.
**Reliability caveats.** A result page can pre-date the refereed
publication (a conference announcement) or post-date it (a plain-language
summary written after publication); always set `result.date_kind`
correctly and do not let the page's casual wording inflate the
`result_type` beyond what the underlying paper says.
**Link checker.** Same volatility as `official_experiment_site`.

### `press_release` (rank 9)

**What it is.** A laboratory's or collaboration's press office announcement.
**URL pattern.** A laboratory news domain (`news.fnal.gov`, a CERN press
page) or the collaboration's own news section.
**Cite it for.** *That* an announcement happened and *when* — the
`announced` date and `date_kind: "announcement"` — never the scientific
wording of the claim itself (research method §1.2, §6.2; A16 explicitly
forbids `result.claim.quote` from a press release).
**Reliability caveats.** Press releases routinely round significance up
("major discovery" for what the paper calls "evidence") and simplify away
caveats. Use only for the announcement date and, cautiously, for
non-technical context.
**Link checker.** Laboratory press archives are usually stable but can be
reorganised on a CMS migration; treat archival press releases as good
`archive_url` candidates.

### `project_document` (rank 9)

**What it is.** A funding-agency or community strategy document: the 2023
P5 report, a European Strategy for Particle Physics (ESPP) document, a
national roadmap.
**URL pattern.** The publishing body's own site (e.g.
`usparticlephysics.org` for P5); often a large PDF.
**Cite it for.** Programme framing, prioritisation language, "why this
matters" context, and — per research method §3.1 — the scope test itself
("does this serve a P5 science driver?").
**Reliability caveats.** A strategy document is a snapshot of community
priorities at a point in time and is not an experimental result; never cite
it for a physics claim that should instead trace to a paper or a PDG
chapter. Good for `topic.overview` programme-level sentences, not for
numeric claims.
**Link checker.** Large PDFs on agency sites; URLs can move when a report
is superseded by its successor (P5 2014 → P5 2023) — keep both as distinct
`src:` records rather than updating one in place, since both remain
citable for their own period.

### `journal_article` (rank 10)

**What it is.** A refereed publication (the version of record).
**URL pattern.** A publisher DOI (`doi.org/10.1088/...`) or the journal's
own page.
**Cite it for.** `result.claim.quote`, `result.significance`,
`result.publication`, exact numeric values not better sourced via HEPData.
**Reliability caveats.** Paywalled journal pages sometimes show only the
abstract to an automated fetch; when only the abstract is reachable, record
`retrieval: "partial"` or `"summary"` honestly (A18) rather than claiming
`full_text`.
**Link checker.** DOIs are the most durable link type in the catalogue;
always prefer a DOI URL over a publisher's article-page URL when both
exist.

### `arxiv` (rank 10)

**What it is.** A preprint on arXiv — the same paper as the eventual
`journal_article` in most cases, but reachable and open.
**URL pattern.** `https://arxiv.org/abs/<id>`.
**Cite it for.** The same things as `journal_article` when the refereed
version is not readily fetchable; `result.claim.quote` may come from an
arXiv abstract, since that is still the collaboration's own wording of the
result, not third-party reporting.
**Reliability caveats.** A preprint can be revised after submission
(v1 → v2 …); record the version implicitly reachable at the cited URL
(arXiv resolves `/abs/<id>` to the latest version) and treat a
numerical claim that later changed between versions as a possible source
conflict (research method §10) rather than silently taking the newest.
**Link checker.** Very stable; arXiv ids do not change.

### `inspire_literature_record` (rank 10)

**What it is.** An INSPIRE `/literature/<recid>` record for a paper (as
opposed to the paper itself).
**URL pattern.** `https://inspirehep.net/literature/<recid>` or the
`/api/literature?q=...` search form.
**Cite it for.** The same role as `arxiv`/`journal_article` when INSPIRE's
own metadata (author list, affiliations, citation count) is what is being
cited, e.g. for `identity_evidence.method:
"inspire_profile_affiliation_match"`.
**Reliability caveats.** Same rate-limit note as `inspire_experiment_record`.
**Link checker.** Stable recids.

### `wikipedia` (rank 12)

**What it is.** Wikipedia articles.
**URL pattern.** `https://en.wikipedia.org/wiki/<Article_title>`.
**Cite it for.** A pointer only: to find the real source, to disambiguate a
name or spelling, or as a second corroborating citation sitting alongside a
better one. Never the sole source of a critical value (research method
§1.2). May be cited for a `kind: campus` coordinate only as a last resort
alongside a `note` explaining why nothing better was reachable, and never
for `kind: detector`/`underground_lab`.
**Reliability caveats.** Unversioned by default; if a `quote` is ever
recorded against a Wikipedia source (discouraged), pin the specific revision
URL (`.../w/index.php?title=...&oldid=...`) so the quote stays checkable.
**Link checker.** Content changes silently and often; a Wikipedia source is
the least trustworthy against future re-verification of all rank 12 types.

### `wikidata` (rank 12)

**What it is.** Wikidata items.
**URL pattern.** `https://www.wikidata.org/wiki/Q<id>`.
**Cite it for.** The same pointer role as Wikipedia; occasionally useful
for a structured cross-reference (`external` ids) to disambiguate between
similarly named entities.
**Reliability caveats.** Same as Wikipedia; crowd-edited, no version pinning
by default.
**Link checker.** Same as Wikipedia.

### `secondary` (rank 12)

**What it is.** Anything else used only as a pointer: news articles not
from a lab press office, blog posts, conference talks without a public
note, theses.
**URL pattern.** Unconstrained.
**Cite it for.** Never a critical value alone. Useful to locate a better
source, or as one of several corroborating citations.
**Reliability caveats.** Widest quality variance of any type in the table;
treat every claim from a `secondary` source as needing a better source
before it can support anything beyond `confidence: "uncertain"`.
**Link checker.** Least durable category; expect the highest 404 rate.

---

## 4. Rules that apply across every type

**A `verified` value may not rest only on a secondary source.** More
precisely (A17, research method §1.2): `confidence: "verified"` requires at
least one cited source of rank ≤ 10. Ranks 11 and up — which in this table
means `wikipedia`, `wikidata` and `secondary` (rank 12; there is no rank 11
in current use) — can never be the sole support for a verified value. They
may sit alongside a rank ≤ 10 source as a second, corroborating citation, or
stand alone only behind `confidence: "uncertain"` with a `note` explaining
that the source is weak.

**Coordinates of `kind: detector` or `underground_lab` have a stricter
floor.** They may not rest solely on `geocoder` or on any source of rank ≥ 8
— which excludes `institution_page` and `geocoder` themselves, not just
ranks 9 and up. A detector coordinate needs a source of rank ≤ 5 in
practice (a detector paper, a TDR, an official site or facility page, or an
INSPIRE/Greybook record with an explicit coordinate) — `pdg` (rank 7) alone
does not clear this floor either, since PDG chapters rarely give
coordinates in the first place.

**`retrieval` gates what a source can carry.** A source whose `retrieval`
is `"failed"` may not be cited by anything (A18) — if you could not read it,
remove the citation and fall back to `null` + `note` on the value, per the
"unknown is a value" rule (ontology §0.3). A `quote` (source-level `excerpt`
or claim-level `quote`) may not come from a source whose `retrieval` is
`"summary"` — if you only read an abstract or a search snippet, you have not
verified the exact wording deep in the document, and the value should carry
`retrieval: "summary"` honestly with no verbatim quote resting on it, or the
quote must come from a portion of the document you actually reached (title,
abstract) that the summary retrieval did in fact cover.

**Reuse before creation.** grep `data/atlas/sources/` for the same
normalised URL or DOI before writing a new `src:` record; two source records
sharing one is a build failure (A20). Update `accessed` on the existing
record instead of duplicating it.

**A source cited by nothing is a warning, not a silent no-op.** A22: an
uncited `src:` record is flagged so a reviewer can decide whether to attach
it somewhere or delete it — do not leave dead source records behind after
editing a value's citations.

**A 404 does not retroactively downgrade a value.** If the sole source of a
`verified` value later returns a broken link, the link checker marks it
"review required" (A22) rather than silently changing `confidence`; a human
reviewer decides whether the fact still stands (e.g. via the Wayback
Machine, `archive_url`, or a re-fetch of the underlying document elsewhere).

**Every `external.*` id needs a source whose URL contains that id** (A20):
an `external.inspire_institution` needs a source URL containing
`inspirehep.net/institutions/<recid>`; `external.ror` needs
`ror.org/<id>`; `external.inspire_experiment` needs
`inspirehep.net/experiments/<recid>`. A citation that merely mentions the id
in prose, without it appearing in the URL, does not satisfy this rule.

**Programme slugs.** Every `src:` id carries the programme slug of the
agent that created it (`src:topic-...` for the research-topics workstream,
`src:dune-...` for a DUNE-focused workstream, and so on), so that a
duplicate-URL warning can be traced back to the workstream that owns each
copy.
