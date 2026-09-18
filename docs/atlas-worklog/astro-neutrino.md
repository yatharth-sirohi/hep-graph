# astro-neutrino — research log

Agent: `astro-neutrino` (Wave 3 domain lead, astrophysical-neutrino programme).
Verified 2026-09-17. Repository `/Users/yatharthsirohi/Desktop/HEP-Graph-atlas-v1`.

## Scope

All 9 experiments listed in `data/atlas/coverage/astro-neutrino.json`: KM3NeT
(flagship, full depth: ARCA + ORCA sites/detectors, collaboration, LoI + TDR
documents, 3 results), ANTARES, Baikal-GVD, ANITA, RNO-G, ARA, ARIANNA, P-ONE
and GRAND at the mandatory bar. Delegation followed the brief's four groups
(KM3NeT; ANTARES+Baikal-GVD; ANITA/RNO-G/ARA/ARIANNA; P-ONE+GRAND), with two
adjustments forced by a session-wide concurrency cap (20 subagents shared
across 16 leads) and, later, a session-wide usage-limit reset that killed a
running child before it could write files:

- Wave 1 (parallel): the KM3NeT child launched successfully; the other three
  groups hit "Concurrent subagent limit reached" and had to be retried after a
  short wait.
- Wave 2 (parallel, 2 of the remaining 3 groups launched): ANTARES+Baikal-GVD
  and the ANITA/RNO-G/ARA/ARIANNA radio group both launched; P-ONE+GRAND hit
  the cap again.
- Per the coordinator's explicit instruction not to keep retrying against a
  saturated cap, the lead researched P-ONE and GRAND itself, directly, via
  WebFetch/WebSearch (no further children spawned for that group).
- Mid-session, the session usage limit reset and killed the running radio
  child (ANITA/RNO-G/ARA/ARIANNA) before it wrote any entity files, though it
  had already fetched and left behind 32 well-formed `src:astro-neutrino-*`
  source records with quotes. The coordinator flagged this; the lead salvaged
  that research (verifying and reusing the quotes/URLs already captured) and
  wrote all ANITA/RNO-G/ARA/ARIANNA entity files itself, since re-spawning was
  against instructions at that point.
- The KM3NeT child completed and handed back a full report before also being
  hit by the same usage-limit reset; its files were confirmed on disk and its
  critical coordinate claims (ARCA/ORCA lat/lon and depth) were personally
  re-fetched and re-verified by the lead against the KM3NeT Letter of Intent
  (arXiv:1601.07459) directly, per the brief's re-verification requirement.

## Entities written

**Facilities**
- `facility:km3net` (KM3NeT child)
- `facility:baikal-deep-underwater-neutrino-telescope` (lead)
- `facility:mcmurdo-ldb` (lead; ANITA balloon-launch facility)
- `facility:summit-station-greenland` (lead)

**Sites**
- `site:km3net-arca-capo-passero`, `site:km3net-orca-toulon` (KM3NeT child)
- `site:antares-toulon` (lead)
- `site:baikal-gvd-lake-baikal` (lead)
- `site:mcmurdo-ldb-launch-site` (lead)
- `site:summit-station-rno-g` (lead)
- `site:south-pole-ara` (lead; new site under the existing, icecube-owned
  `facility:amundsen-scott-south-pole-station`)
- `site:moores-bay-arianna` (lead)
- `site:cascadia-basin-p-one` (lead)
- `site:grandproto300-dunhuang` (lead)

**Experiments** — `experiment:km3net` (child), `experiment:antares`,
`experiment:baikal-gvd`, `experiment:anita`, `experiment:rno-g`,
`experiment:ara`, `experiment:arianna`, `experiment:p-one`,
`experiment:grand` (all lead).

**Detectors** — `detector:km3net-arca`, `detector:km3net-orca` (child);
`detector:antares`, `detector:baikal-gvd`, `detector:anita`, `detector:rno-g`,
`detector:ara`, `detector:arianna`, `detector:p-one`, `detector:grand` (lead).

**Collaborations** — `collaboration:km3net` (child); `collaboration:antares`,
`collaboration:baikal-gvd`, `collaboration:anita`, `collaboration:rno-g`,
`collaboration:ara`, `collaboration:arianna`, `collaboration:p-one`,
`collaboration:grand` (lead).

**Documents (KM3NeT flagship)** — `document:km3net-loi` (Letter of Intent,
arXiv:1601.07459), `document:km3net-tdr-2010` (child).

**Results (KM3NeT flagship)** — `result:km3net-uhe-neutrino-observation-2025`
(mandatory: the 2025 Nature KM3-230213A observation), plus two optional extras
`result:km3net-orca6-oscillation-parameters-2024` and
`result:km3net-arca-diffuse-flux-limit-2026` (child).

**Coverage** — `data/atlas/coverage/astro-neutrino.json` (9 rows, all updated
from `researched: "none"` to `"partial"`, with honest `missing_fields`; none
claimed `"complete"`).

No `people/`, `memberships/` or roster files were created anywhere in this
workstream, per the brief.

## Sources added (72 total, all `src:astro-neutrino-*`)

KM3NeT (21, by the child): official KM3NeT site pages (ARCA/ORCA detector
page, IT-site page, FR-site page, design-study page, technical-publications
page, collaboration + organization pages — all `official_experiment_site`,
rank 1), the 2016 Letter of Intent (`design_report`, rank 4, arXiv:1601.07459
— independently re-fetched and re-verified by the lead), the INSPIRE
experiment record (rank 3, recid 1108236), three press releases on
construction/deployment milestones (rank 9), two result pages (rank 9), the
2025 Nature observation's INSPIRE literature record (rank 10), and two
arXiv results papers (ORCA6 oscillations, ARCA diffuse-flux limit).

ANTARES (4, by the lead): the official site's detection-principle and
collaboration pages (rank 1), the collaboration's own 2025 "two decades"
detector paper (arXiv:2504.09473, reclassified `detector_paper` rank 4 since
it is the collaboration's comprehensive description of its own instrument),
and Wikipedia (rank 12, pointer only for the widely-cited precise coordinate).

Baikal-GVD (3, by the lead): the INR RAS official facility page (rank 2),
the collaboration's own 2023 status paper (arXiv:2309.16310, `detector_paper`
rank 5), and a CERN Courier article (rank 9, historical/press context only).

ANITA (18, salvaged + verified by the lead from a child killed by a
session-limit reset before it could write entity files): the official site's
home/about/instrument/collaboration pages and four per-flight campaign pages
(all rank 1), the NASA CSBF Antarctica LDB payload page (rank 2), the INSPIRE
experiment record (rank 3, recid 1108484 — URL corrected from `/api/...` to
the canonical `/experiments/...` form so it satisfies A20's substring check),
four arXiv/journal flight-result papers (rank 10), two institution pages
(Kavli/UChicago, WashU — rank 8), and two Wikipedia pointers (rank 12).

RNO-G (7, salvaged + verified): the official site (rank 1), two Summit
Station / geo-summit.org pages (`official_facility_site`, rank 2), the JINST
design paper (arXiv:2010.12279, `design_report`, rank 4 — gives the array's
exact coordinates), a 2024 detector paper on the first seven stations (rank 5),
the INSPIRE experiment record (rank 3, recid 1826393, URL corrected the same
way as ANITA's), and a WIPAC project page (rank 8).

ARA (4, salvaged + verified): a WIPAC project page (rank 8), the 2024
collaboration overview paper (arXiv:2411.01761, rank 10), the INSPIRE
experiment record (rank 3, recid 1911572, URL corrected), and Wikipedia
(rank 12, pointer only).

ARIANNA (8, salvaged + verified): official home and research pages (rank 1),
three arXiv papers (2010 prototype, 2019 testbed, 2023 results — rank 10),
the INSPIRE experiment record (rank 3, recid 1108245, URL corrected), and two
Wikipedia pages (rank 12, one a pointer for the array in general, one a
coarse regional pointer for Moore's Bay/Minna Bluff).

P-ONE (4, by the lead): the official site (pacific-neutrino.org, rank 1),
the 2020 Nature Astronomy design paper (arXiv:2005.09493, rank 10), the 2021
EPJC site-characterization paper (arXiv:2108.04961, reclassified
`detector_paper` rank 5), and a Wikipedia pointer for the nearest named
coastal feature (Barkley Sound).

GRAND (5, by the lead): the 2018 white paper (arXiv:1810.09994, reclassified
`design_report` rank 4), a 2026 JINST prototypes paper (arXiv:2509.21306,
`detector_paper` rank 5), a 2025 ICRC progress paper on GRANDProto300
(arXiv:2507.05915, `detector_paper` rank 5 — the source of the 65-antenna
figure and the Gobi-Desert/Dunhuang location), and a Wikipedia pointer for the
nearest named city (Dunhuang).

`grep -rl` was run for every URL/DOI against `data/atlas/sources/` before any
new source was created; the lead independently re-confirmed this for its own
sources and spot-checked the salvaged/child sources for duplicates against
sibling wave-3 workstreams (`km3net-loi-2016` was in fact reused directly by
the lead's ANTARES coordinate cross-check, see Conflicts below, rather than
creating a duplicate). INSPIRE etiquette (<=1 request/10 s) was respected: the
lead made isolated Wikipedia/arXiv/official-page fetches, well spaced, and did
not crawl any institution site en masse.

## Conflicts

| claim | source A | source B | chosen | why |
| --- | --- | --- | --- | --- |
| ANTARES precise coordinates | Official site: "a latitude of 43° North" only (no longitude) | KM3NeT LoI (independently re-verified by the lead): ORCA at 42°48'N 06°02'E, "approximately 10 kilometers west of the existing ANTARES telescope site" | 42.8°N, 6.17°E, `confidence: approximate` | No single fetched source states ANTARES's own precise degrees. The LoI's relative-position statement about ORCA (a sibling KM3NeT child's independently-verified source) corroborates the widely-cited 42°48'N/6°10'E value to within ~1 km (10 km west of 6°02'E ≈ 6°10'E), upgrading the value from "uncertain" (Wikipedia-only) to "approximate" (corroborated by a rank-4 design_report's relative statement). Recorded transparently in the coordinate's own `note`. |
| ANITA-III launch date | Official ANITA-III campaign page (undated): "set to launch in December 2013" | Companion journal article (arXiv:1803.02719): actual launch December 2014 | December 2014 (actual) | The campaign page recorded a pre-launch schedule; the paper reports what actually happened — a one-year slip. Both sources are kept, with the schedule statement noted as historical context. |
| ARIANNA current status | Official home page: "the now decommissioned ARIANNA pilot experiment" | Official research page (same domain, undated): "Currently, eight ARIANNA stations are taking data" | decommissioned | Two official-tier statements cannot both be current; the home page's explicit terminal wording is treated as more authoritative/current than an inner content page's stale "currently". The 8-station claim is kept as a separate, dated interval rather than discarded. |
| Baikal-GVD site depth | INR RAS official facility page: "depth of 1100-1300 m" (historical Baikal neutrino experiment description) | 2023 collaboration status paper: "nearly constant depth of 1366 m" (current GVD lakebed) | 1366 m | The more recent, more specific figure from the collaboration's own current status paper is used; the facility page's range likely describes the older NT-200 predecessor era. |
| ORCA/ARCA depth rounding | KM3NeT general overview page: "about 2500 m" for ORCA | KM3NeT-Fr site page + LoI: "2450 m" | 2450 m | (Re-verified by the lead, originally flagged by the KM3NeT child.) The site-specific page and the primary design document agree exactly; the general overview page is a coarser rounding. |
| KM3NeT TDR publication year | Technical-publications listing page: "Year: 2009" | Design-study page: "The Technical Design Report was published in March 2010" | 2010-03 | (KM3NeT child's finding, spot-checked by the lead as plausible: 2009 likely reflects internal preliminary approval, 2010 the actual publication.) |

## Unresolved fields

- **Collaboration formation dates**: not sourced for any of the 8
  non-flagship experiments' collaborations (ANTARES has a formation *year*,
  1996, but no day/month; the rest are entirely unsourced and left `null`
  with a `locator` explaining the gap, per A15).
- **Collaboration membership counts** (institutions/countries/scientists):
  found only for ANTARES ("around 150" engineers/technicians/physicists, no
  institution/country total) and KM3NeT (qualitative "hundreds of scientists"
  only, per the brief's requirement to use the collaboration's *own* page,
  not INSPIRE/Wikipedia). All others left entirely `null`.
- **Precise seafloor/array coordinates** could not be sourced to a rank<=7
  source with actual numbers for: ANTARES (see Conflicts above — resolved via
  a cross-workstream corroboration, not a direct statement), P-ONE (Cascadia
  Basin — recorded at the nearest named coastal feature, Barkley Sound, as a
  `kind: campus` coarse regional pointer), GRAND (GRANDProto300 — recorded at
  the nearest named city, Dunhuang, same treatment), and ARIANNA (Moore's Bay
  — recorded at the nearest named headland, Minna Bluff, same treatment).
  None of these were invented; all are flagged `confidence: uncertain` with
  an explicit note, per A17.
- **ARA and ARIANNA per-station coordinates**: not published anywhere found;
  ARA reuses the icecube workstream's existing approximate South Pole anchor
  (cross-cited, not re-created) with a note about the ~2 km IceCube offset.
- **P-ONE's 2026 deployment status**: the official site's "In 2026, the first
  detection line of P-ONE will be deployed" could not be resolved to
  already-happened vs. still-upcoming from the fetched text; recorded
  descriptively in notes rather than guessed.
- **GRAND@Nançay and GRAND@Auger** prototypes are named (operating since 2023
  alongside GRANDProto300) but not modelled as separate detector/site records;
  only GRANDProto300 (the best-sourced of the three) got full treatment.
- **KM3NeT-Gr (Pylos)**: the LoI names a third candidate site near Pylos,
  Greece, but no official page describes it as built; not modelled (child's
  deliberate scope decision, confirmed reasonable by the lead).
- **Baikal-GVD's own collaboration site** (baikalgvd.jinr.ru) returned a
  persistent TLS certificate error every time it was fetched (both by the
  lead directly); INR RAS's page was used as the official-facility fallback.
  A retry from a different network/tool might recover membership and more
  current status figures.
- Several **detector-level spec totals** were deliberately left unset rather
  than computed from per-unit figures (e.g. ANTARES/ARCA/ORCA per-string PMT
  counts were sourced but array-wide totals were not multiplied out, since
  that would be an unsourced derived computation on a critical field, which
  A17 forbids the agent from doing itself).

## Children spawned and what was re-checked

1. **KM3NeT** (`general-purpose`, model `sonnet`) — completed and handed back
   a full report before being killed by a session usage-limit reset (the
   report is genuine; files were confirmed on disk). The lead personally
   re-fetched arXiv:1601.07459 (the KM3NeT Letter of Intent) via WebFetch and
   independently confirmed, word for word, both the ARCA coordinates/depth
   ("36° 16' N 16° 06' E at a depth of 3500 m ... about 100 kilometers
   offshore from Porto Palo di Capo Passero") and the ORCA coordinates/depth
   ("42° 48' N 06° 02' E at a depth of 2450 m ... roughly 40 kilometers
   offshore from Toulon ... approximately 10 kilometers west of the existing
   ANTARES telescope site") exactly as the child had recorded them. This
   incidentally let the lead upgrade its own ANTARES coordinate confidence
   (see Conflicts). The lead also fixed a schema-shape issue the child had
   NOT introduced but that a sibling site shared (`site.coordinates` flat
   shape) was already correct in the child's KM3NeT files.
2. **ANTARES + Baikal-GVD** (`general-purpose`, model `sonnet`) — launched but
   its outcome was superseded: by the time this log was written the lead had
   independently researched and written both experiments directly (the child
   agent's task/output was not consulted further once the lead's own
   from-scratch files were validated clean; no duplicate files were created
   because the lead checked `data/atlas/` before writing and found nothing
   from this child yet on disk).
3. **ANITA/RNO-G/ARA/ARIANNA (radio group)** (`general-purpose`, model
   `sonnet`) — killed by a session usage-limit reset before writing any
   entity files, but left 32 well-formed, well-quoted `src:astro-neutrino-*`
   source records on disk. The lead read every one of those source files in
   full, treated their `excerpt`/`quote` fields as claims to be reused (not
   as ground truth to copy blindly), and wrote every experiment/detector/
   site/facility/collaboration file itself from that material — including
   independently deciding the ANATRES-style balloon-placement treatment for
   ANITA, the campus-kind coordinate fallback for the coordinate-less sites,
   and fixing the two INSPIRE source URLs the child had recorded as
   `/api/experiments/<recid>` (which failed A20's substring check) to the
   canonical `/experiments/<recid>` form.
4. **P-ONE + GRAND** — not delegated a second time after hitting the
   concurrency cap twice; researched directly by the lead per the
   coordinator's explicit instruction not to keep retrying against a
   saturated cap.

## Dangling references to ids another lead owns

- `facility:amundsen-scott-south-pole-station` — owned and already landed by
  the `icecube` workstream. Referenced (not created) by `site:south-pole-ara`,
  `experiment:ara.facility_roles`, and `collaboration:ara.host_facility_id`.
  Not a validator error (the id exists on disk), but listed here per the
  brief's requirement to report every cross-workstream reference regardless.
- `src:icecube-official-detector-page` — an icecube-workstream source, cited
  (not created) by `site:south-pole-ara.coordinates.sources` to justify
  reusing the same South Pole anchor point IceCube's own site record uses.
- `src:astro-neutrino-km3net-loi-2016` — created by the KM3NeT child (same
  owner slug, `astro-neutrino`, so not a cross-workstream reference in the
  ID-registry sense) but cited by `site:antares-toulon`, written by the lead
  independently; flagged here only because the file boundary between "child
  work" and "lead work" is otherwise easy to miss.

## Confidence summary

- **verified**: KM3NeT ARCA/ORCA coordinates and depths (re-verified
  personally against the LoI), KM3NeT construction/operation intervals and
  the mandatory 2025 UHE-neutrino observation result; ANTARES depth
  (2475 m), line count (12), OM count (885), full construction/operation/
  completion dates (2006-02-14 / 2008-05-29 / 2022-02-12); Baikal-GVD
  coordinates and depth (51°46'N 104°24'E, 1366 m) and OM/string counts;
  RNO-G array coordinates (72°35'46"N 38°25'19"W) and station counts; ARA
  station count and deployment depth range; ANITA flight dates and
  float-altitude/area/volume specs; ARIANNA station counts and ice-shelf
  thickness at the 2009 prototype site; GRANDProto300 antenna counts and
  stage dates.
- **approximate**: ANTARES precise coordinates (see Conflicts); Baikal-GVD
  and GRAND collaboration "formation" lower bounds; ANITA-III/IV end dates
  (derived from stated flight durations, not independently confirmed
  calendar dates); ARIANNA's decommissioning start (set to the last
  confirmed data-collection month as a lower bound, not a sourced
  decommissioning date).
- **uncertain**: every coordinate recorded at a coarse regional pointer
  (P-ONE/Cascadia Basin at Barkley Sound, GRAND/GRANDProto300 at Dunhuang,
  ARIANNA/Moore's Bay at Minna Bluff, ARA at the reused South Pole anchor);
  all collaboration `formation` fields left `null`.
- **derived**: none of this workstream's fields were authored as derived
  values; `document_ids`/`result_ids`/`site_ids`/etc. were deliberately
  omitted per A1 (the validator's "is derived at build time" warnings on
  these files are the expected, corpus-wide consequence of every entity
  simply not declaring keys it isn't supposed to author — confirmed by
  spot-checking that the same warning fires on dozens of pre-existing
  exemplar files from other workstreams).

## Validation and build

`python -m hepgraph.atlas.validate`: 0 errors attributable to any file this
workstream owns (confirmed by grepping the full validator output for every
astro-neutrino file pattern after two fix passes). Fixes applied across a
full sweep of every one of this workstream's files, not just the first
example found, per the brief's "fix classes, not examples" rule: missing
`sources` on `experiment:antares` (a single file where the top-level array had
been omitted); missing `quote`/`locator` on 7 collaborations' `formation`
fields; missing `note` on 4 `confidence: approximate` interval rows; an
invalid site `coordinates.kind` (`approximate_region` used where a detector
placement requires `detector`/`underground_lab` or the `campus` exception);
display-string/value mismatches on 3 ANITA quantities (the validator's
"million"-word parser limitation); a plausibility-range violation from
reusing the reserved `altitude` spec key for a balloon's *float* altitude
(renamed to `float_altitude`); two `status`-vs-derived-state mismatches
(ARIANNA's terminal interval needed a real `start` to cover any time; GRAND's
prototype-stage intervals were moved off the experiment record onto the
detector record so the experiment's own status keeps matching the
collaboration's "proposed" self-description); two `experiment-without-
facility-or-site` errors (P-ONE and GRAND each needed a site, resolved via
the coarse-regional-pointer approach rather than a fabricated precise
coordinate); and four INSPIRE source URLs that used the `/api/...` path
instead of the canonical form A20's substring check requires.

`python -m hepgraph.atlas.build`: succeeds; only the pre-existing, corpus-wide
`atlas.json` bundle-size warning (over the original three-experiment pilot
budget, expected at 30+ experiments) appears, unrelated to this workstream.

No git commands were run at any point. Only files under `data/atlas/` and
this worklog were touched.
