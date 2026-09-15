# Professor demo guide

This sequence was exercised against the final local service on 15 September
2026. Live timings depend on INSPIRE and the network, so keep the Saved demo
open in a second tab as the deterministic fallback.

## Start

On macOS, double-click **Start HEP Graph.command** in the project folder and
keep its Terminal window open. The app opens at
[http://127.0.0.1:8765/](http://127.0.0.1:8765/) with **Live INSPIRE** selected.

From a terminal, the equivalent command is:

```sh
python3 launch_demo.py
```

The application stores live records only in bounded memory. Stopping the
server clears live search state; it does not leave a local INSPIRE mirror.

## Reliable five-minute sequence

### 1. A fast exact historical result

Select these exact author profiles:

- **Richard P. Feynman** — INSPIRE `1010044`
- **John Archibald Wheeler** — INSPIRE `983692`

Leave **Small-team (≤10 authors)** selected and click **Find connection**.
The expected result is one coauthorship hop. A one-hop path is globally
shortest by definition, so the app labels this **Exact shortest path**. Open
the evidence row and point out the paper title, date, full author count, INSPIRE
link, DOI/arXiv identifiers when supplied, and the doctoral context.

Measured after endpoint preparation: 1.008 seconds; identical repeat: 0.0013
seconds. These numbers are observations, not guarantees.

### 2. Coauthorship plus PhD context is still one degree

Select:

- **Matheus Hostert** — INSPIRE `1621061`
- **Silvia Pascoli** — INSPIRE `1019647`

The expected result is one ordinary coauthorship hop. The explicit profile
record also identifies Pascoli as Hostert's PhD adviser, so the evidence panel
shows that as additional context on the same pair. It does not draw a second
edge or count a second degree.

Suggested explanation: “The route counts people-to-people collaboration. A
paper proves a hop; it is not an extra node. Doctoral evidence annotates the
same pair when they also coauthored.”

### 3. A mixed historical path

Keep Hostert as the source and choose **Paul Adrien Maurice Dirac** — INSPIRE
`1011729`. Enable the historical genealogy supplement.

The checked result is a four-hop verified route:

```text
Hostert — Pascoli — Petcov — Sciama ← Dirac
```

The first three hops have current coauthorship evidence. The final directed
genealogy-only hop uses an explicit AIP source for Dirac's supervision of
Sciama. The app labels the route **Verified path** because a four-hop live
route has not been proven globally shortest across all qualifying INSPIRE
records. Final measured run: 3.040 seconds; repeat: 0.0038 seconds.

If time permits, try **Hostert → Albert Einstein** (`1010907`). The checked
eight-hop coauthorship route took 12.131 seconds in the final run and also
correctly remains a verified, non-global claim.

### 4. Show the paper modes

Choose:

- **Georges Aad** — INSPIRE `1066085`
- **Braden Keim Abbott** — INSPIRE `1019091`

Select **Large-team (>10 authors)**. The expected result is one exact hop on a
paper whose full INSPIRE author count is greater than 10. Open its evidence to
show that the filter uses the paper's total author count, even though the app
does not need to display or resolve every collaboration member. Final measured
run: 6.118 seconds; repeat: 0.0047 seconds.

Switching to **Small-team** changes the graph definition and therefore starts
a distinct search. **All papers** accepts both team sizes. There is no weighted
or approximate route mode; every qualifying researcher pair counts once.

### 5. Cross-field retrieval, share, refresh and export

For a short cross-field example, use **Hostert → John Richard Ellis**
(`1010819`). The checked three-hop route took 6.052 seconds. Copy the current
URL, reload it, and show that the exact identities and filters return and the
browser reconnects to retained search state when available.

Open an evidence row, then use **Export JSON** and **Export SVG**. The exports
record the source mode, stable IDs, graph filters, result status and evidence.

### 6. Saved demo and scoped centrality

Switch to **Saved demo**. Use its Hostert → Cheung example (`1621061` →
`1013775`). The fixed snapshot gives a deterministic five-hop demonstration
without internet access.

Open **Centrality** and calculate a metric. Explain that the ranking covers
only this named saved snapshot of 5,249 indexed people and 1,180 works. It is
not a ranking of all researchers in HEP, and the live mode deliberately does
not estimate global centrality from a bounded path search.

## Optional longer example

**Edward Witten** (`983328`) → **Erin Visser** (`2955074`) returned a verified
seven-hop cross-field route in 50.520 seconds in the final run. Use it when you
want to show progress stages and deeper evidence validation. Do not use it as
the first demonstration.

## What to say about accuracy

Use this concise description:

> HEP Graph searches live INSPIRE data for documented coauthorship and sourced
> genealogy paths. Every displayed hop has evidence. It calls a route globally
> shortest only when its search has actually ruled out a shorter route; an
> interrupted or bounded search is labeled incomplete instead of “no path.”

The application checks exact INSPIRE author IDs, aliases, current profiles,
paper bylines, full author counts and known identity hazards. INSPIRE can still
contain missing or incorrect metadata, so users can inspect every supporting
record.

## If live INSPIRE is slow or unavailable

Switch to **Saved demo** and continue the talk. An upstream failure is shown as
**Search incomplete** or **INSPIRE unavailable**. It is never converted into a
claim that no connection exists. The Saved demo, profiles, exports and scoped
centrality remain available offline.

## Before walking into the room

1. Start the app and confirm the home page says **Live INSPIRE**.
2. Open the Feynman–Wheeler link once so endpoint data is warm.
3. Keep a second tab on the Saved demo Hostert–Cheung result.
4. Confirm the internet connection can open one paper evidence link.
5. Keep this guide and [the validation report](VALIDATION.md) available.
