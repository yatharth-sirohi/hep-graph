# HEP Graph implementation contract

## Project and ownership
Local Python 3.11+ service using the standard library, SQLite persistent provenance, immutable JSON graph snapshots, plain accessible HTML/CSS/JS SVG interface. No paid service, public repository, software license grant, or deployment is authorized/required for this local delivery. User explicitly asks for delegated implementation. Work only in assigned files. Do not initialize Sites or deploy. No secrets or private contact data.

## Graph snapshot v1
`data/current.json` is an atomic published snapshot with:
```
{version: string, created_at: ISO_UTC, coverage: {label, description, complete: false, queries: [], failures: []},
 people: [{id: string INSPIRE recid, name: string, aliases: [str], affiliations: [str], orcid: str|null, profile_status: 'profile'|'literature_only', source_url: str}],
 works: [{id: str INSPIRE recid, title, year: int|null, date: str|null, date_source: str, author_count: int, authors: [resolved person ids], unresolved_count: int, document_types: [str], doi: [str], arxiv: [str], source_url, source_ids: [str], retrieved_at: ISO_UTC}],
 phd: [{adviser: person id, student: person id, degree: 'PhD', year: int|null, source_url, source_record: str, uncertainty: str|null, retrieved_at: ISO_UTC}],
 examples: [{label, source: person id, target: person id}]
}
```
Canonical SQLite stores works + per-work authorship occurrences (unresolved occurrence identity never shared), people by stable profile ID, source metadata (only allowlisted fields), queries/checkpoints, identifier aliases, doctoral evidence. JSON is a query snapshot export, not canonical storage. Profile links from literature establish IDs but do not claim full upstream profile/neighborhood coverage.

## Filters and graph
`Filters(max_authors: int|null=10, min_shared: int=1, year_start: int|null=null, year_end: int|null=null, genealogy: bool=true)`. Positive caps <=100000, min_shared <=1000; year 1000..2100 and ordered. Papers: document_types contains `article` or `conference paper`, excludes `thesis`, `book`, `book chapter`, `proceedings`; document count policy displayed. Earliest documented preprint/publication date; unknown dates included only when no date bound. Work author_count is full original list or larger explicit total; never resolved author count. Eligible distinct works first, pair thresholds second, doctoral edges independently. Directed genealogy for ancestry only; ordinary path traverses either way and shows actual direction. One person-to-person hop = one degree, papers are not people. Duplicate works merged only via stable record ID, explicit redirect/merge, exact DOI or version-normalized arXiv. Never merge authors by name.

## Python graph interface (graph agent owns hepgraph/graph.py + tests/test_graph.py)
`GraphError(code, message)` including `resource_limit`.
`Filters` dataclass with `from_dict(dict)` and `to_dict()`.
`Graph(snapshot: dict, filters: Filters)` provides:
- `.people` dict by ID; `.version`; `.filters`; `.snapshot`
- `find_paths(source, target, alternatives=3) -> {status:'ok'|'not_indexed'|'no_path'|'resource_limit', paths:[{people:[person objects], hops:int, edges:[edge objects]}], exact:bool, message?, version, filters, coverage}`
- `profile(id) -> {person, indexed_publications:int, collaborators:[{person, shared_works:int}], coauthor_count:int, combined_degree:int, advisers:[phd], students:[phd], reachability:{...}, version, filters, coverage}`
- `neighborhood(id, limit=40) -> {people:[person], edges:[edge], truncated:bool, version, filters, coverage}`
- `centrality(metric='degree', limit=25) -> {status, metric, definition, population, scope, exact, method, computed_at, rows:[{person, value, rank}], version, filters, coverage, ...radius/center details}`. degree means unique coauthors. combined_degree separate. harmonic normalized by N-1 over all indexed people. betweenness simple undirected person graph normalized. eccentricity only largest component (exclude isolates if all isolated, explain). Method may declare unavailable for bounded resource.
- `ancestry(id, direction='ancestors', limit=100)` directed doctoral records.
Edge: `{source:id,target:id,types:['coauthor'|'phd'],shared_works:int,works:[full work objects],phd:[full phd objects]}`. All evidence returned for path; neighborhood bounded nodes does not change calculation graph. Incidence representation should avoid prebuilding giant paper cliques. Hard work/node limits yield explicit resource_limit. Cache keyed on snapshot+full filters in server. Production code implements graph algorithms; NetworkX is test reference only.

## HTTP interface (integration owner implements server)
All GET JSON `/api/health`, `/api/dataset`, `/api/search?q=...&live=0|1` returns `{status:'ok'|'not_found'|'ambiguous'|'upstream_unavailable',results:[{...person,indexed:bool,indexed_publications:int,representative_work?:work}], source:'local'|'live',message?}`, `/api/path?source=&target=&max_authors=10|min_shared...`, `/api/person/{id}` profile, `/api/neighborhood/{id}?limit=40`, `/api/centrality?metric=degree`, `/api/ancestry/{id}`. All graph endpoints parse same filter keys. `max_authors=all`; genealogy true/false. Malformed input HTTP400. Limits503/422 with explicit code, never no_path. Fixed upstream host only, bounded live queries; no write endpoints or auto ingestion from browser.

## UI (frontend agent owns static/ only)
Professional research workspace: dark navy header, white/slate working surface, teal coauthorship and amber directed PhD lines, readable 16px text. Core search two identity pickers + swap + find and compact filter panel visible initially. Header tabs Connections, Centrality, About & coverage. Search lists context, indexed states, optional explicit live INSPIRE search. Show coverage banner always and exact scoped claims. Query configuration in URL incl dataset version; mismatch clearly warned. Examples read from /api/dataset. Path cards/person click, expandable evidence; graph with zoom/pan/fit/reset/labels, drag pinned nodes, bounded progressive profile-neighborhood expansion, JSON/SVG export, legend. Person panel/page and selected-metric centrality with definitions/population/timestamp. Every control must work. Use DOM textContent or escaped strings; sanitize external links to allowed HTTPS hosts. No external fonts/scripts required. Loading/error/empty states, keyboard labels, responsive mobile.
