# INSPIRE data decisions

Checked 2026-09-15 UTC. This is an independent project, not an official INSPIRE service.

## Official sources and decisions

- [REST API documentation](https://github.com/inspirehep/rest-api-doc): use read-only literature and author searches with explicit field selection; numeric control numbers identify records. Up to 1,000 records per page and 10,000 results per query are documented. The per-IP quota is 15 requests per five seconds; after HTTP 429 wait at least five seconds. The optional bounded importer runs sequentially at one request per second with bounded retries. Fields are selected on search endpoints, including one-record ID searches, because individual-record responses do not support field filtering. No current supported bulk-export feed was established from the current official documentation consulted. Use bounded, recorded searches for this pilot; arrange supported bulk acquisition with INSPIRE before full-scale collection. Date/identifier partitions and offline JSONL import permit expansion without record-by-record crawling. The API documents earliest_date for search results and created/updated source timestamps.
- [Authors schema](https://inspire-schemas.readthedocs.io/en/latest/schemas/authors.html) and [degree types](https://inspire-schemas.readthedocs.io/en/latest/schemas/elements/degree_type.html): advisors contain degree_type, record, hidden and curated_relation. Accept only explicit phd entries linked to stable author records; exclude hidden relationships. Unknown/other, bachelor, master, and other supervision are excluded. Preserve curation uncertainty. Several advisers are permitted. Academic degree metadata is evidence of doctoral context, whereas adviser names alone are insufficient.
- [Literature schema](https://inspire-schemas.readthedocs.io/en/latest/schemas/hep.html): authors includes other contributors. Use inspire_roles (default author); exclude supervisor/editor occurrences from coauthorship. A thesis supervisor only becomes a doctoral edge when thesis_info explicitly identifies a PhD and the student is identified. Articles include preprints; individual conference papers qualify. Theses, books, book chapters and proceedings volumes do not. deleted, new_record and deleted_records describe tombstones and replacements. Keep these identifiers for reconciliation rather than guessing from titles or names.
- [Search guidance](https://help.inspirehep.net/knowledge-base/inspire-paper-search/): publication-date searches may mix first appearance and publication dates. Inspected responses demonstrated that date 2020-01 and preprint_date:2020-01 do not give the same population. Use the verified January arXiv identifier partition (2001.*) in the pilot, and explicit preprint_date:start->end for expansion. Literal Elasticsearch square-bracket range syntax returned no hits in the literature parser and is not used. User year filters are applied locally to normalized scholarly dates, never ingestion timestamps.
- [Terms of use](https://help.inspirehep.net/knowledge-base/terms-of-use/): HEP metadata reuse is governed by CC0 with field-specific restrictions. Email downloading is prohibited; abstracts and keywords have source-dependent restrictions. This app requests neither emails nor abstracts, keywords, private notes, or full text. It retains public names, scholarly identifiers, affiliations, roles, dates and work provenance. Linked full texts and all other third-party content retain their own terms. Source attribution remains visible for every hop. The software-license decision remains with the project owner.

## Representative responses inspected

Hostert (1621061) explicitly lists Silvia Pascoli (1019647) as a PhD adviser, with curated_relation false; label that uncertainty. Feynman (1010044) explicitly lists Wheeler (983692) with phd context. Edward Witten (983328) explicitly lists Gross (1007454) with phd context. Paul Dirac (1011729) lists Fowler with degree_type other; Steven Weinberg (983868) lists Treiman with other. Those ambiguous native records alone create no doctoral edges. The fixed saved pilot includes no historical supplement. The September 15 deep live-search release adds three separately sourced institutional PhD relationships and narrowly reviewed source corrections; see [Historical sources](HISTORICAL_SOURCES.md). Both exact public profiles must be fetched before a supplemental relationship can appear in a live result.

The Hostert thesis record 1760672 identifies a PhD and the student; the selected response did not supply a linked supervisor, so the thesis alone does not establish a pair. The ATLAS discovery record 1124337 supplies a long author list and is retained as a large-team stress case. No author list is truncated on download. Profile links provide stable identity; upstream author disambiguation can still contain errors and is not treated as personal acquaintance.


## Coverage and normalization policy

Canonical storage is SQLite with selected raw source records, author occurrences, checkpoints and provenance. Snapshot publication is atomic. A completed bounded harvest remains a partial network. Profile discovery, local person indexing, and full-neighborhood coverage are distinct; this release claims no complete person neighborhood. Paths prove an evidenced route and shortestness only within the displayed snapshot and filters. Unresolved signatures remain per-work occurrences; matching names never join them.

Repeated downloads replace stable records. Explicit replacement links, identical DOI and version-normalized arXiv identifiers deduplicate scholarly works. Conflicting authorship signatures are retained for audit and not blindly unioned into artificial collaborations. Full total authorship controls both lower and upper paper-count bounds; a partially resolved author list never becomes a small-team work. A standalone correction notice is excluded from eligible coauthor incidence only when its title starts with `Erratum`, `Errata`, or `Corrigendum`, followed by whitespace, punctuation, or the end of the title. Its raw source record and provenance remain retained. This narrow rule does not exclude addenda or research titles that mention an erratum elsewhere. Earliest documented preprint/publication date is the date convention. Unknown dates survive all-years queries only. Filter eligible distinct works first, count eligible shared works second, apply threshold third, then add doctoral edges independently.

Within the earliest documented year, preserve INSPIRE's valid `earliest_date` and its reported precision. A bare publication year cannot erase its month/day, and a later journal imprint cannot replace an earlier preprint month merely because the imprint is more precise. If `earliest_date` is absent, choose the earliest valid dated preprint, imprint, or thesis entry before falling back to a bare publication year. The professor-readiness audit corrected 778 date/date-source fields without changing any work's year or graph eligibility. The independent frozen source-table fixture pins these saved dates in the regression suite.

Updates require refresh/reconciliation and a new immutable snapshot. A bounded search refresh cannot prove that all upstream deletions were observed; before a public global service, establish a complete update/deletion feed, add regular integrity audits, and reconcile upstream merges across all affected records.


## On-demand date safeguard

Live and future saved builds use only scholarly dates. INSPIRE's computed
`earliest_date` falls back to a database creation date when no literature date
exists. It is accepted only when real scholarly fields on the same source
record corroborate its stated year/month/day precision. Otherwise the
normalizer uses a supported preprint/imprint/publication/thesis date or leaves
it unknown. A bare publication year cannot establish an added month or day.
The offline rebuild audit found no date changes in the supplied 1,180 works.
See [the official implementation](https://github.com/inspirehep/inspirehep/blob/master/backend/inspirehep/records/api/literature.py)
and [the live mode guide](ON_DEMAND.md).


## Current live-search refinements

Author lookup searches canonical names, preferred names and explicit name variants, joining literal name tokens with uppercase `AND`. It still returns separate numeric author records for user selection. The familiar spelling “Gerard ’t Hooft” resolves through the documented alias of canonical “Gerardus ’t Hooft”; aliases never join different IDs.

The official literature facets endpoint returns a compact top-100 author summary. Counts guide discovery only; every returned route requires real paper evidence. Open-ended large-team queries use `author_count:11+` and apply the full count again locally. The selected filter definitions are ≤10 authors, >10 authors, or all papers; one qualifying pair is one unweighted hop.

Current live graphs apply additional conservative identity checks, including explicit given-name conflicts, suspicious late initials-only bylines against a documented death year, and native adviser names that contradict their referenced current profiles. Source occurrences remain unchanged; the derived edge is withheld with an audit reason. No replacement identity or doctorate is inferred. See [identity collisions](IDENTITY_COLLISIONS.md).
