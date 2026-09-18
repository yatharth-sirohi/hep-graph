# HEP Graph

HEP Graph traces documented coauthorship connections between INSPIRE researchers. Route calculations use one pinned, compact graph in Neon. The graph stores identities, authorship membership, author counts, and years; names, titles, links, and other display details are fetched only for the people and works shown in a result.

The live site is [hep-graph.vercel.app](https://hep-graph.vercel.app). There is no bundled saved-demo dataset or alternate search mode.

## Local development

Python 3.11 or newer and the dependencies in `requirements.txt` are required. Configure `HEPGRAPH_GRAPH_DATABASE_URL` and `HEPGRAPH_GRAPH_IMPORT_ID` for an existing pinned graph version, then run:

```sh
python3 -m pip install -r requirements.txt
python3 -m hepgraph.server --port 8765
```

Open [localhost:8765](http://127.0.0.1:8765/). Without database configuration, the service reports that routes are unavailable; it does not silently use a local or live graph. See [database-first search](docs/DATABASE_FIRST_SEARCH.md) for the graph configuration and validation model.

## How a connection is determined

Each hop joins two people who share enough eligible works under the selected author-count, year, and minimum-shared-work filters. Shortest-route search runs against the pinned graph; source details are hydrated after a route is found and cannot change its topology. Search results distinguish a verified route from a proven shortest route and never present an incomplete search as proof of no connection.

Researcher name, ORCID, and ID lookup makes a bounded INSPIRE identity request because the compact graph intentionally stores no names. Full person and paper details are fetched for displayed results. The current deployed graph has no certified doctoral overlay, so the PhD filter is disabled and routes are coauthorship-only. Global centrality is not available on this graph version.

## Tests

```sh
python3 -m pip install -r requirements-dev.txt
python3 -m pytest -q
```

The server and algorithm tests can run without contacting INSPIRE. Database integration tests require an isolated database set as `HEPGRAPH_TEST_DATABASE_URL`; they are skipped otherwise. Production database credentials should never be used for destructive tests.

## Scope and attribution

The graph is a dated version of INSPIRE metadata, not a continuous mirror. Source records can be corrected or added after its cutoff, and incomplete source metadata can affect results. Every path should be interpreted within the selected graph version and filters. HEP Graph is independent of INSPIRE and does not claim affiliation with it. The software license has not yet been selected; linked third-party sources retain their own terms.
