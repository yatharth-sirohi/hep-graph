# HEP Graph

**HEP Graph never guesses your path.** Select two INSPIRE researchers, choose which papers count, and inspect the documented connection between them.

HEP Graph uses the **live INSPIRE HEP API with bounded caching and temporary search state**. It retrieves the metadata needed for a search. It does not download the full INSPIRE database, run a background catalogue harvest, or require a local literature mirror.

The existing application has been refined, preserving researcher profiles, evidence inspection, shareable URLs, exports, the small offline saved snapshot, and its scoped centrality views.

## Start

Python **3.11 or newer** is required. The application has no third-party runtime dependency.

```sh
python3 launch_demo.py
```

On macOS, you can also double-click **Start HEP Graph.command**. The launcher verifies the service version before reusing a running instance. Keep its terminal open while using the app.

For a clean command-line start without opening a browser:

```sh
python3 -m hepgraph.server --port 8765 --default-mode live
```

Open [HEP Graph locally](http://127.0.0.1:8765/). To check an existing service without starting one:

```sh
python3 launch_demo.py --check
```

## What counts as a connection?

| Paper mode | Qualifying paper's full author count |
| --- | --- |
| **Small-team** — default | 10 or fewer |
| **Large-team** | More than 10 |
| **All papers** | Any author count |

One qualifying researcher pair is **one degree**, regardless of how many papers they share. There are no weighted paths, fractional collaboration strengths, or approximate-path options. Minimum shared-work and year filters operate on eligible, deduplicated works. A 2,932-author paper remains a large-team paper even if few authors resolve to profiles.

Coauthorship is the primary relationship. An explicitly documented PhD adviser relationship is additional metadata on an already connected coauthor pair. When the historical genealogy supplement is enabled, a sourced PhD relationship may also establish a clearly marked genealogy-only hop. Undergraduate mentoring, postdoctoral supervision, shared institutions, acknowledgements and inferred relationships do not create edges.

## Results you can assess

- **Exact shortest path:** the available search proof rules out a shorter qualifying route. Live zero- and one-hop results are immediate proofs; a live two-hop result is proven only after the direct-pair check is exhaustively complete.
- **Verified path:** every displayed hop has retrieved evidence and current identity checks. A deeper live result does not claim global shortestness. **Continue exact search** retains the current route and search state while looking for a shorter route or a stronger proof.
- **Search incomplete:** an upstream failure, unresolved data, time or memory limit prevented completion. It never means that no connection exists.

The algorithms compute exact unweighted shortest paths on the retrieved graph. That local fact is separate from a proof covering all qualifying INSPIRE records. INSPIRE itself can contain missing or incorrect metadata; the app reports evidence and identity exclusions rather than inventing a link.

Each hop exposes titles, dates, INSPIRE literature links, DOI/arXiv identifiers where available, total author counts and qualifying shared works. Doctoral evidence preserves its actual adviser-to-student direction and source.

## How live searches improve latency

Selecting a resolved researcher starts bounded preparation immediately, while you select the other endpoint. Typing alone does not launch graph expansion.

The search checks the direct pair first, examines both endpoint coauthor summaries, verifies candidate two-hop bridges, then expands from both ends. The official coauthor summary and historical hints guide retrieval; neither can supply a final edge without evidence. Publication pages, validated records and search frontiers are reused.

Identical concurrent upstream requests share one request. Recent identical searches reconnect to the same job or retained result. Browser refresh retains a small job handle, so a running search can reconnect. Cancellation stops further search work while safely completed shared cache entries remain reusable.

Storage is bounded:

- Shared public-metadata cache: **8 MiB serialized data**, 256 entries, 15-minute expiry.
- Retained result data: a separate **8 MiB serialized budget**, up to 32 results, 20-minute expiry.
- At most **two active deep searches** and **four retained search sessions**; their temporary SQLite databases stay in memory.
- Endpoint preparation: two workers and a bounded queue; it warms only identity, coauthor summary and one publication page.
- No growing disk cache. Stopping the server clears temporary live state. Python objects, search graphs and in-flight responses consume additional bounded memory; the cache budgets are not a total-process RAM claim.

See [search design](docs/DEEP_SEARCH.md), [storage/API behavior](docs/ON_DEMAND.md), and [measured validation](docs/VALIDATION.md).

## Saved demo and centrality

**Live INSPIRE is the default and canonical product.** The secondary **Saved demo** remains for offline demonstration, reproducible calculations and testing. Its fixed snapshot contains 5,249 indexed people, 1,180 distinct works and 43 explicit PhD records; it is a deliberately partial sample.

Centrality is available only for that saved snapshot. Its degree, harmonic, betweenness and graph-center views state their population, filters and exact or sampled method. They are **not rankings of all HEP researchers**. Global centrality is not estimated from a live path search.

The saved snapshot is supplied as a small JSON file. Local SQLite databases, downloaded caches, credentials and generated test outputs are excluded from the repository. A 622 KB frozen public-source fixture keeps independent provenance tests reproducible without a local database.

## Tests

Install development dependencies in an isolated environment:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The Python suite includes independent NetworkX comparisons, filters, large author lists, identity collisions, API failures, caching, concurrency, continuation and server protections. It makes no live INSPIRE calls.

Browser harnesses use Playwright with Chromium. After installing Playwright in your chosen development environment, start the server, then run the relevant scripts under `tests/browser_*.cjs`. `HEP_URL` selects the server; `HEP_BROWSER_EXECUTABLE` optionally selects an installed Chromium-family browser; report output is configurable. Saved acceptance checks require a server started with `--default-mode snapshot`.

Real INSPIRE regression checks require explicit invocation:

```sh
python tests/live_regression.py --group demo --repeat
python tests/live_regression.py --group known --repeat
python tests/live_regression.py --group historical --seconds 180
```

The permanent matrix contains direct, known two-hop, historical, cross-field, large-team, restrictive, identity and sparse-profile cases. Each run writes its own measured results under ignored `test-results/`. An incomplete optional case is reported separately from a successful route.

## Documentation

- [Professor demo guide](docs/PROFESSOR_DEMO.md)
- [Validation and performance](docs/VALIDATION.md)
- [Identity collision report](docs/IDENTITY_COLLISIONS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Exactness, discovery and continuation](docs/DEEP_SEARCH.md)
- [Live API and storage policy](docs/ON_DEMAND.md)
- [Data decisions and official sources](docs/DATA_DECISIONS.md)
- [Historical doctoral sources](docs/HISTORICAL_SOURCES.md)
- [Optional bounded data pipeline](docs/PIPELINE.md)
- [Security review](docs/SECURITY_REVIEW.md)

## Publication and licensing

This repository is source code for a locally runnable application. A GitHub repository is not a hosted public app. The included Dockerfile is an optional deployment starting point; its image build is not part of the verified release checks.

**Software licensing is pending.** No MIT, GPL, Apache or other software license has been selected or granted. INSPIRE metadata and linked third-party sources retain their applicable terms. See [licensing and attribution](docs/LICENSE_STRATEGY.md). HEP Graph is independent of INSPIRE and makes no affiliation claim.
