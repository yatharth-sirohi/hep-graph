# HEP Atlas architecture

HEP Atlas is a source-backed geographic and historical knowledge graph of
experimental high-energy physics. Its primary visualisation is a globe, but the
globe is a view over the graph, not the product. HEP Graph — the existing
researcher-to-researcher network over live INSPIRE data — is unchanged by it and
remains the people layer; the two connect through INSPIRE author identifiers.

```text
HEP Atlas
├── People        → HEP Graph (live INSPIRE, existing app)
├── Globe         → facilities, sites, experiments, collaborations, institutions
├── Research      → hierarchical topics
├── Major Results → curated, sourced result registry
└── History       → intervals on every entity and relationship
```

## 1. Layers

| Layer | Where | Nature |
| --- | --- | --- |
| Canonical data | `data/atlas/**/*.json` | Human-reviewed, one file per entity, diffable, provenance-carrying |
| Schema and rules | `hepgraph/atlas/schema.py` | Enums, units, date/interval semantics, derived-state rules |
| Loader | `hepgraph/atlas/load.py` | Reads the canonical tree into a typed in-memory model |
| Validator | `hepgraph/atlas/validate.py` | Structural, referential, temporal, provenance, geometric and unit checks |
| Build | `hepgraph/atlas/build.py` | Generates the browser bundles under `static/atlas/generated/` |
| Link checker | `hepgraph/atlas/linkcheck.py` | Manual, polite; records link status back into source records |
| Scaffold | `hepgraph/atlas/scaffold.py` | Creates skeleton files so adding an experiment is one command |
| Server | `hepgraph/server.py` | Additive routes `/atlas` and `/atlas/<file>`; no change to HEP Graph routes |
| Browser app | `static/atlas/` | Vanilla HTML/CSS/JS, vendored WebGL library, no build step |

The canonical data is never read by the browser. The browser reads only
generated bundles, so runtime browsing makes no external requests at all — in
deliberate contrast to HEP Graph, whose pathfinding is live against INSPIRE.

## 2. Ontology

The full contract is `docs/HEP_ATLAS_ONTOLOGY.md`; the v0.2 amendment block at
its top is normative where it differs from the body. In summary:

- **Entities**: facility, site, accelerator, beamline, experiment, detector,
  collaboration, institution, person, result, document, topic, source.
- **Facility ≠ institution ≠ collaboration.** CERN is a facility, an
  institution and a collaboration member, with three ids and three roles.
- **Geography lives on sites.** An experiment has `facility_roles` (host, beam
  source, detector host, prototype host); a detector has `placements` with role
  and dates, so ICARUS can sit at Gran Sasso, then CERN, then Fermilab.
- **Relations have one canonical direction**; inverses are derived at build
  time, so two agents editing different partitions cannot desynchronise them.
- **Specs are typed quantities** with dimension and unit, not free text, so a
  1300 m versus 1300 km error is mechanically detectable.
- **Provenance is a value type.** Critical facts carry `sources`,
  `verified_at`, `confidence` and a claim-level `quote` or `locator`.
- **Membership carries an evidence class** — official roster, official
  institution list, INSPIRE author profile, current or historical publication
  affiliation, institutional page, self-reported, derived — and the interface
  says which one it is in words.

## 3. Temporal model

Every entity carries intervals with status, start, end, precision and sources.
Dates are strings whose precision is their length, optionally with `earliest`,
`latest`, `display` and a `planned` flag meaning "this comes from a schedule".

At build time each entity is reduced to `state_segments`: run-length-encoded
`[m0, m1, status, certainty]` in months since 1950-01. The slider, range mode,
playback and the historical tests all read that one structure.

- **Presence** is the existence hull from the earliest start to the earliest
  terminal event (or the build date).
- **State** at a time is chosen among covering intervals: operational statuses
  beat proposed/planned, then the latest start wins, then a fixed rank.
- **Certainty** is `certain` when the whole selection lies inside the interval
  at its stated precision, otherwise `possible`, which the globe hatches.
- Open intervals extend to the build date, not to the date someone verified
  them, so two records verified months apart behave identically.

This is what makes "show me 1995" defensible: nothing is displayed as operating
unless a sourced interval says it was.

## 4. Provenance and the source hierarchy

Sources are records with a type whose rank is derived, an access date, and a
retrieval mode (full text, partial, summary, failed). A value may not cite a
source that failed to retrieve, and a verbatim quote may not come from a
summarised retrieval. Rank ordering runs from the official experiment site
through laboratory sites, experiment registries, design reports, detector
papers, HEPData and the Particle Data Group, to journals and, last, secondary
sources. A `verified` value must cite something better than a secondary source.

The build splits provenance out of the main bundle into `provenance.json`,
keyed by entity and JSON pointer, so the globe stays small while every claim in
a panel can still be expanded to "why is this here".

## 5. Ingestion pipeline

```text
research agent (writes JSON + sources)
      ↓  validator (structure, references, time, units, geometry, provenance)
domain review  →  independent verifier (different agent, re-opens the sources)
      ↓  build (bundles, derived inverses, state segments, coverage outputs)
functional / UX / performance testing
      ↓  release
```

Adding an experiment is: `python -m hepgraph.atlas.scaffold experiment <slug>`,
fill the skeleton, add sources, validate, build. The coverage registry records
what is covered and what is only identified; `data/atlas/coverage/backlog.json`
holds every experiment named in the coverage scope that has not been researched
yet, so incompleteness is visible rather than implied.

## 6. Frontend rendering

The library choice and its justification are in
`docs/HEP_ATLAS_GLOBE_LIBRARY.md`. The application is plain modules loaded by
`static/atlas/index.html`: data loader, hash router and URL state, globe
renderer, timeline, detail panels, collaboration mode, topic mode, results
mode, search, and a non-WebGL fallback that renders the same data as lists and
tables. Bundles load lazily: the globe needs the manifest and `atlas.json`;
text, provenance, results, documents, institutions, memberships and people
arrive only when something asks for them. A collaboration's people are fetched
per institution, so ATLAS-scale rosters never load at once.

## 7. HEP Graph integration

People reuse INSPIRE author identifiers. Where a person is resolved, the build
derives a link into HEP Graph's existing researcher view; no pathfinding,
identity or evidence logic is duplicated. Unresolved people are kept, labelled,
and never linked. The atlas adds no write paths and no new upstream requests to
the existing application.

## 8. Deployment

The atlas is served by the same Python handler as HEP Graph, from static files
with a content-hashed data version. Generated bundles are cacheable for five
minutes; the application shell is not cached. Nothing in the atlas holds server
state, so it is unaffected by the per-process job and cache behaviour that
governs HEP Graph's live searches.
