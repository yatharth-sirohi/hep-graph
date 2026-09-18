# UX review — HEP Atlas (`/atlas`)

Reviewer role: the person who did not build this. Drove the real app
(`static/atlas/generated/` data, no `?data=fixtures`) with a headless Chromium
via Playwright, scripted as four personas plus an adversarial pass, and read
`docs/HEP_ATLAS_ONTOLOGY.md` §5 and amendment A19 first because the exact
membership wording is called out as a correctness requirement.

**Method note on timing.** The underlying data bundle (`static/atlas/generated/atlas.json`)
was regenerated at least once *during* this review (`facility:fermilab`'s own
`status` flipped from `construction` to the correct `active` between my first
pass and my final verification pass — this matches a fix for the exact issue
`docs/atlas-worklog/REVIEW_scientific.md` already reported). Every finding
below was **re-verified against the live server in a final pass** immediately
before writing this report, so it reflects current behaviour, not a stale
screenshot. Where a data-level issue I originally caught turned out to have
already been fixed mid-session, I say so and point at the surviving bug
instead of double-reporting it.

All work was done with scratch Playwright scripts under
`/private/tmp/claude-501/.../scratchpad/` (not committed). App served at
`http://127.0.0.1:8820/atlas`, real data throughout.

---

## Persona 1 — Newcomer (doesn't know NuMI/LBNF/SBN)

**Task:** find DUNE; work out where its neutrinos start/end; is it running
today; what is it trying to discover; then find what experiments exist at
Fermilab; judge the plain-language text and acronym handling.

What I did: typed "DUNE" into the top search box (1 click + typing).

What happened: a 17-item type-ahead dropdown appears instantly. The actual
**Experiment** entry ("Deep Underground Neutrino Experiment — Experiment") is
the **last** item, after the LBNF beamline, the DUNE Collaboration, 4
detectors, 2 ProtoDUNEs, and **8 technical-design-report/CDR documents**, all
of which repeat the same long name. A newcomer typing the acronym they
actually know would have to scroll past a wall of documents to reach the
thing itself. (P2, finding #10 below.)

Clicking through to the Experiment panel: status badge reads **"Construction"**
— that directly and correctly answers "is it running today" (no). Good.

"What it studies" section: **"No plain-language summary yet."** This is
false — the atlas *does* have a plain-language summary for DUNE, written and
sitting in the data (`experiment:dune.summary.plain`):

> "A very large experiment that will send neutrinos 1285 kilometres through
> the Earth from Illinois to South Dakota, where detectors filled with liquid
> argon a mile underground will record them. It aims to find out whether
> neutrinos and antineutrinos behave differently, to catch neutrinos from an
> exploding star, and to look for protons decaying."

That sentence would have answered *every part* of this persona's task in one
read (start/end, discovery goal, plain language, no unexplained jargon). It
never reaches the screen. See **Finding P0-1**.

Falling back to the jargon: expanding "Full technical section" gives a
technically dense paragraph ("wide-band on-axis beam", "LArTPC", "4850
Level of SURF") — "SURF" is never expanded anywhere on this panel (it's
expanded only if you separately navigate to the SURF facility page). A
newcomer who opens the one available fallback text hits an unexplained
acronym on the first read. (P2, finding #13.)

"Beam and sites" correctly lists Fermilab (surface, beam origin) and SURF
4850 Level (underground, far detector) — that does answer "where do the
neutrinos start and end," but it also lists "CERN Neutrino Platform, EHN1"
in the same undifferentiated list, which is only where the *prototype*
(ProtoDUNE) was tested, not part of the real 1285 km baseline. Nothing marks
that distinction; a newcomer could easily conclude DUNE's beam involves CERN.
(P2, finding #11.)

**Fermilab / "what experiments exist here":** clicked the Fermilab pin on the
globe (1 click, needed `force: true` in automation because the globe never
stops rotating — see mobile/motion notes below). Panel shows:

- Current experiments: ICARUS, NOvA, SBND
- Historical experiments: **Deep Underground Neutrino Experiment**, MicroBooNE, MINERvA, MiniBooNE, MINOS, MINOS+

DUNE — the lab's flagship, under-construction, decade-away-from-completion
project — is listed as **"Historical,"** the same bucket as MINOS (ended
2016) and MiniBooNE (ended long ago). A newcomer asking "what's at Fermilab"
would reasonably conclude DUNE already happened. See **Finding P1-1**.

**Verdict for this persona:** the raw facts needed (status, baseline,
destination) are technically retrievable, but the tool's *own* plain-language
layer — its whole reason to exist for this persona — never renders, and the
one place a newcomer would look to confirm "is DUNE still coming" gives the
wrong answer. Time: ~10 clicks, ~4 minutes to complete the nominal task, but
I would not trust what I read without cross-checking, because two things I
read turned out to be contradicted by the underlying data itself.

---

## Persona 2 — Graduate student

**Task:** DUNE far-detector mass + baseline (are these citable numbers); open
the TDR; find DUNE member institutions, then Iowa researchers, follow one
into HEP Graph; find major oscillation results; check sources are
inspectable.

Baseline: **"1285 k"** — visually cut off. Far detector fiducial mass: **"at
leas / t / kt"** — broken mid-word across three lines. This is not a narrow-
window artifact: reproduced identically at 1400px and 1920px browser width.
The full, correct text (**"1285 km"**, **"at least 10 kt"**) *is* present in
the DOM (confirmed via `innerText`), so copy-paste recovers it, but nothing
on screen tells a student that. A student skimming visually would cite
"1285 k" or misread "at leas[t]" as truncated data. See **Finding P1-2**.

Opened the TDR via "Open document (new tab)" — the link itself
(`arxiv.org/abs/2002.02967`) is correct and works. But the **document panel
itself** shows a blank heading and the subtitle **"Technical Design Report ·
"** with nothing after the separator — no title, no year, anywhere on the
panel. This is not specific to this one document: the code reads
`document.title`/`document.year`, but every document record's real fields are
`name`/`date`, so this happens for all ~56 documents in the atlas identically.
See **Finding P0-2**.

Institutions: opened DUNE Collaboration → "View collaboration on globe" (2
clicks) → 217 confirmed institution dots render correctly, University of
Iowa found and clicked (1 click on a 12px dot, had to zoom mentally to find
it — small target, see mobile section). Institution panel shows the correct
A19-format evidence wording verbatim: *"On the official institution list (as
of 2026-09)"*. **People (2): Jane M. Nachtman, Yasar Onel**, each labelled
*"INSPIRE author profile lists this collaboration"* — again matching A19's
required wording exactly. Clicked "Open in HEP Graph" on Nachtman (1 click,
opens new tab) — lands on HEP Graph's connection explorer with **"Jane M.
Nachtman · 996327 LIVE INSPIRE"** already pre-filled as the "From researcher."
This whole chain works cleanly, no console errors. **Positive finding.**

But: the collaboration panel's own **"Membership"** stat block, one section
above where I found those 217 correct institutions, says **"0 confirmed
members"** — directly above "Institutions: 228" and "Countries: 38" on the
same panel. This isn't specific to DUNE: ATLAS (170 institutions), CMS (286),
and IceCube (58) all show the identical "0 confirmed members." The code reads
a `confirmed_count` field that doesn't exist in the data; the real per-
institution roster (which the panel two clicks away gets right) says DUNE has
217 confirmed institutional members, not 0. This is the single most direct
violation of the ontology's "exact membership wording" requirement I found.
See **Finding P0-3**.

(Secondary, lower-severity: the "228" shown for DUNE institutions doesn't
match the "217" actual rows in `memberships/dune.json` either — an 11-record
mismatch between the collaboration-level summary stat and the roster file
it's supposedly summarizing.)

Results and sources: opened a handful of results (Higgs observation 2012,
Super-K atmospheric-oscillation evidence 1998, T2K electron-neutrino
appearance). Every field I checked carries a "Sources" disclosure with the
actual quoted text, a locator, and an accessed date — e.g. DUNE's baseline
traces to *"1285 km from the neutrino production target"* from the ProtoDUNE
beam-test paper, and its far-detector mass traces to the TDR's own wording.
**Sources are genuinely inspectable everywhere I checked — a strong,
consistent positive.**

**Verdict for this persona:** the "can I trust this number" answer is mixed —
sourcing itself is excellent and exactly what a grad student needs, but two
independent rendering bugs (truncated key-spec values, blank document titles)
mean the numbers and documents look unreliable or unlabeled even when the
underlying data is right. ~15 clicks, ~8 minutes.

---

## Persona 3 — HEP expert hunting for mistakes

**Task:** timeline at 1995/2005/2012 — historically plausible? Result wording
— anything called discovery that was only evidence? Planned vs. operating
visually distinguishable? Wrong units/energies/misplaced detectors?

**Timeline scrub (the headline finding).** Set `y=1995`, opened ATLAS: status
badge **"Upgrade."** Set `y=2026` (today): status badge **"Upgrade."**
Identical. Checked SBND (status "Active" at both 1995 and 2026 — SBND did not
exist until 2024), NOvA (status "Active" at 1995 — NOvA started 2014), DUNE
(status "Construction" at 1995 — DUNE was conceived in 2015). **The detail
panel's status badge never reacts to the selected year at all** — it always
shows the entity's static, build-time `status` field. This is a real,
reproducible falsehood: scrub the timeline to 1995 and open ATLAS, and the
tool tells an expert ATLAS is "in upgrade" a decade before it ever collided a
single proton. See **Finding P0-4** — this is the most serious bug in the
review, both because it's a directly false claim and because it defeats the
entire premise of having a timeline at all once a user drills into any
entity. (Contrast: the globe's own marker dimming *does* correctly use
per-year `state_segments` — I confirmed CERN/Fermilab/SURF/J-PARC/Kamioka
Observatory markers correctly go dim/absent/possible at 1995 vs. 2026. Only
the panel ignores the year.)

**Anachronistic site markers.** Zoomed into the CERN/Fermilab region at
`y=1995`: individual site-tier pins for "LHC Point 1 (ATLAS cavern)," "LHC
Point 5 — CMS cavern," "SURF 4850 Level — LBNF/DUNE far detector caverns,"
"Ash River NOvA far detector laboratory," and "Tochibora mine — Hyper-K
cavern" are all rendered, full opacity, identical to 2026 — none of these
physically existed in 1995 (LHC excavation ~1998+, SURF as a physics lab
2007+, NOvA far detector 2013+, Hyper-K cavern still under construction
today). Root cause: `site.state_segments` is `null` for every site record —
sites carry no status/interval data in this model, so the per-year dimming
logic (which *does* work at the coarser facility tier, as above) has nothing
to filter on. See **Finding P1-3**.

**Result wording.** Pulled every entry from `results.json` (58 results) and
checked `result_type` against title/significance. Genuinely well calibrated:
both 2012 Higgs papers are typed `observation` (not `discovery`), matching
their actual titles ("Observation of a new particle…"); the 1989 LEP
three-neutrino-species result is `measurement`; MiniBooNE's contested
low-energy excess is typed `anomaly` rather than any stronger claim; the 2021
IceCube Glashow-resonance single event is `first_detection`, not
`observation`/`discovery`. **No result anywhere is over-claimed as a
"discovery" that was only evidence — this is a genuine strength, worth
calling out as a positive.** I did not exhaustively re-verify every
`claim.quote` against its cited source text (58 results), so this is a
spot-check, not a full audit.

**Planned vs. operating.** The bottom legend (Active/Construction-commissioning
/Proposed-approved-planned/Uncertain) does correspond to real CSS distinctions
at the facility tier (`is-dimmed` at 40% opacity for proposed/approved/planned,
`is-possible` hatched for uncertain, `is-absent` hidden entirely) — confirmed
these classes toggle correctly across years for facility-level markers. This
mechanism is sound; it's undermined by findings P0-4 and P1-3 above, which
mean the *detail panel* and *site-level* markers don't participate in it.

**Units/energies spot-check.** DUNE: 60–120 GeV Main Injector protons, 1.0–1.2
MW beam power (upgradable to 2.4 MW), 17.5 kt LAr/cryostat, 1285 km baseline —
all checked against the cited TDR/beam-test sources and are correct, standard
values. No unit or energy errors found in this spot-check; I did not audit
the full 30-experiment set for units.

**Verdict for this persona:** an expert who only reads panels without
scrubbing the timeline would find the physics content (results wording,
key specs where legible, sourcing) trustworthy. An expert who does the one
thing the tool advertises — move the timeline — will catch a false claim
within the first panel they open, and that would end their trust in
everything else on the page.

---

## Persona 4 — Casual visitor on a phone (390×844)

Rotated/zoomed the globe: works, gestures respond, no errors.

Opened a panel (deep link to DUNE, simulating a search tap): panel takes full
width and about 70% of the viewport height, globe remains partially visible
above it — reasonable, does not fully black out the map. **Positive
side-effect discovered here:** at 390px the "Key specifications" values are
**not** truncated (full-width panel gives the value column room), which
confirms the desktop truncation bug (P1-2) is specific to the narrow
fixed-width right-hand column, not a universal layout bug.

Ran a hit-target audit across all interactive elements at this viewport:
- Facility-tier globe pins: 36×45px — borderline but usable.
- **Site-tier globe pins (individual caverns/halls): 12×12px** — far under
  any reasonable touch-target guideline (Apple HIG ~44pt, Material ~48dp).
  On a real phone these would be very difficult to tap accurately, and this
  is exactly the tier a user needs to distinguish e.g. "ATLAS cavern" from
  "CMS cavern" at the same facility. See **Finding P1-4**.
- Timeline mode buttons (Single date/Range/Play): 28px tall — under the
  guideline, though full-width-adjacent buttons make it tolerable.

Timeline: dragging/tapping the slider works and updates the "Status in
<year>" label correctly on mobile too.

Search: typed into the search box, same dropdown as desktop, box is
comfortably large (366×41px) and tap-friendly.

**Exiting collaboration mode:** entered collaboration mode via a full deep
link (`?y=2026&m=collab&c=dune#/collaboration/dune`, the only form that
actually works — see adversarial section), then tapped "Globe" in the left
nav. This did switch the view back to the plain globe, but the URL retained
`&c=dune` afterward (`?y=2026&c=dune`) with no visible indication anything
was left over — harmless in what I could observe, but a bit of stale state
that a careful QA pass should account for.

**Verdict for this persona:** mostly usable on a phone, with one concrete,
fixable accessibility problem (12px cavern-level touch targets) and one
pleasant surprise (the desktop truncation bug disappears at this width).

---

## Adversarial pass

| Test | Result |
| --- | --- |
| Back/forward after several selections (DUNE → ATLAS → Fermilab) | **Works correctly** — each back/forward step restored the exact prior panel and URL. |
| Reload while a panel is open | **Works correctly** — reloading `#/experiment/dune` restores the DUNE panel after reload. |
| Deep link straight to an experiment/facility/topic/result | **Works correctly** for all four (`#/experiment/dune`, `#/facility/fermilab`, `#/topic/neutrino-oscillations`, `#/result/sk-atmospheric-oscillation-evidence-1998`). |
| Deep link straight to a **collaboration** (institution/arcs mode) | **Fails silently** if only the query params are given: `?m=collab&c=dune` with no matching `#/collaboration/dune` hash renders 0 institution markers (verified: 182 markers with the hash present, 0 without, same query params otherwise). Normal "Copy share link" is unaffected, since it copies `window.location.href` (hash included) — but any hand-typed, hash-stripped, or edited URL breaks with zero error message. See **Finding P1-5**. |
| Copy share link → open in a fresh tab | Works when copied from a state that already has a hash (the normal case). |
| Timeline while in collaboration mode | Slider updates the year label correctly in collaboration mode too; no errors. |
| Institution arcs on a large collaboration (CMS, 286 institutions) | **Works well** — renders promptly (~2s), legible fan pattern to CERN, no console errors, no dropped-looking rendering. |
| WebGL fallback (`--disable-webgl --use-gl=disabled`) | **Excellent** — a clear banner ("The interactive 3D globe is not shown. Your browser does not report WebGL2 support...") followed by full, accessible, sortable-looking HTML tables (Facilities, Experiments, ...) with the exact same working detail-panel links. No console errors. **Strong positive.** |
| Keyboard-only navigation, visible focus | Tab order reaches every left-nav control and, after enough presses, individual globe markers; each shows a clear 2px amber `outline`. Pressing Enter on a focused globe marker (CERN) correctly opens its panel. **Positive.** |
| `prefers-reduced-motion` honoured | **Yes, cleanly.** Measured marker drift over 2s: 15px with no preference (continuous ambient auto-rotation) vs. **0px** with `reduced-motion: reduce` — the globe's idle auto-rotation is fully suppressed. Matches an explicit comment in `globe.js` about skipping the fly-in intro for this reason. **Positive.** |

One incidental finding from automation: the globe **never stops auto-
rotating** even with no user interaction (confirmed marker position drifts
continuously at idle), which is why a plain Playwright click on a facility
label needed `force: true` — the element is technically "not stable" between
frames. Not a defect on its own (reduced-motion correctly turns it off), but
worth knowing it's there by design.

---

## Findings (by severity)

### P0 — false statements shown to the user

**P0-1. Every entity's plain-language summary is authored but never
displayed.** `experiment:dune.summary.plain`, `facility:fermilab.summary.plain`,
etc. exist and are well-written in `atlas.json`, but `static/atlas/js/panels.js`
(lines 129, 194, 277, 290–291) reads `t.summary_plain` from the separately-
loaded `text.json` bundle instead — a field that bundle never contains (it
only has `summary_technical`/`notes`/`physics_goals`). Every facility,
experiment, and collaboration panel therefore shows "No plain-language
summary yet." regardless of whether one was written. Verified on DUNE,
Fermilab, ATLAS, CMS, IceCube. **This is the highest-value single fix in the
whole review** — it silently disables the tool's primary value proposition
for the newcomer persona.

**P0-2. Document panel titles are blank; dates are missing.**
`static/atlas/js/panels.js:465-466` (`renderDocument`) reads
`document_.title` / `document_.year`; every document record's actual fields
are `name` / `date`. Reproduced on all documents checked (DUNE FD TDR Vol. I
shows an empty `<h2>` and subtitle "Technical Design Report · " with a
trailing, dangling separator). The "Open document" link itself still works
because it reads `document_.reference.url` (a field that does exist), so the
content is reachable — but the panel identifying *what document you're
looking at* is broken for the entire document library (~56 records).

**P0-3. Every collaboration shows "0 confirmed members," contradicting the
adjacent institution count on the same panel.**
`static/atlas/js/panels.js:289-290` reads `collab.membership.confirmed_count`,
a field that does not exist in the data (the real field is
`institution_count`, plus a separate correct per-institution roster file).
Verified on DUNE ("0 confirmed members" next to "Institutions: 228"), ATLAS
(170), CMS (286), IceCube (58) — universal across every collaboration
checked. This is a direct violation of the ontology's A19/A5 membership-
count wording rule ("N confirmed members (+M undated)"), and it sits right
next to the correct number, so it reads as an internal contradiction, not
just a missing value. (Secondary: the "228" institution-count itself doesn't
match DUNE's 217-row roster file — worth a data-sync pass separately.)

**P0-4. Detail-panel status badges never react to the selected timeline
year.** `experimentBadge()` (`static/atlas/js/panels.js:101-104`)
unconditionally renders `exp.status`, the entity's static build-time status,
regardless of the year the user has scrubbed to. Verified live: ATLAS shows
"Upgrade" identically at `y=1995` and `y=2026`; SBND shows "Active" at 1995
(it didn't exist until 2024); DUNE shows "Construction" at 1995 (conceived
2015). This directly contradicts the globe's own markers, which *do*
correctly consume `state_segments` per year (`static/atlas/js/globe.js:187-286`),
so the bug is isolated to the panel-rendering path, not the underlying data
model — a real, comparatively contained fix. Given this is the entire
premise of an interactive timeline, I'd call this the second-most valuable
fix after P0-1.

### P1 — broken interactions / major failures

**P1-1. Facility panels mislabel active, under-construction flagship
experiments as "Historical."** `current = experiments.filter(e => e.status
=== 'active' || e.status === 'commissioning')` (`panels.js:114`, repeated at
`:405`) excludes `construction`/`proposed`/`approved`/`planned`, so DUNE
appears under "Historical experiments" at Fermilab, in the same list as
MINOS and MiniBooNE (both genuinely finished). A newcomer using exactly the
task's prescribed path ("find what experiments exist at Fermilab") is misled
about DUNE's status by the very panel meant to answer that question.

**P1-2. Key-specification values are cut off at the panel's right edge,
independent of window size.** Reproduced identically at 1400px and 1920px
browser width: DUNE's baseline renders as "1285 k" (not "1285 km"), far
detector fiducial mass wraps mid-word ("at leas" / "t"). Root cause: the
`<dd>` value cell in `.kv-list` (a CSS grid, `static/atlas/atlas.css`) has
`overflow: visible` and no `width`/wrap constraint tied to its grid track,
so long values spill past the panel's own right boundary rather than
wrapping inside it. The full text is present in the DOM (recoverable via
copy-paste) but not visible to a user reading the panel normally. Confirmed
**not** present at 390px mobile width (full-width panel gives the column
room), so this is specific to the narrow fixed desktop side panel.

**P1-3. Site-tier globe markers never reflect the timeline year.**
`site.state_segments` is `null` for every site record in the data (sites
carry no status/intervals in this model), so cavern/hall-level pins — "LHC
Point 1 (ATLAS cavern)," "SURF 4850 Level — LBNF/DUNE far detector caverns,"
"Ash River NOvA far detector laboratory," "Tochibora mine — Hyper-K cavern" —
render identically at full opacity whether the year is 1995 or 2026, even
though none of these physically existed in 1995. The coarser facility-tier
markers (CERN, Fermilab, SURF, J-PARC, Kamioka Observatory) *do* correctly
dim/hide per year, so the mechanism works — it's just missing the data it
needs at the site tier.

**P1-4. Site-tier globe markers are 12×12px — well under any usable
touch-target size.** Measured directly on the 390×844 mobile viewport. These
are exactly the markers a user needs to distinguish between e.g. ATLAS and
CMS caverns at the same facility, so this isn't a decorative element.

**P1-5. A collaboration deep link that omits the hash silently fails.**
`?m=collab&c=dune` alone (no `#/collaboration/dune`) renders 0 institution
markers; the identical query params with the hash render 182. No error is
shown either way — the globe just looks like plain Globe mode. The normal
"Copy share link" flow is unaffected (it copies the full URL including
hash), but any hand-edited, pasted-and-reformatted, or hash-stripped URL
would silently drop the collaboration view with nothing to explain why.

### P2 — annoyances / polish

10. Searching "DUNE" ranks the Experiment entity itself dead last (17th) in
    the type-ahead, behind the beamline, the collaboration, 5 detectors, and
    8 documents that all share the same long expanded name.
11. DUNE's "Beam and sites" list puts "CERN Neutrino Platform, EHN1" (the
    ProtoDUNE prototype test-beam site) in the same undifferentiated list as
    Fermilab and SURF (the actual production/detection endpoints), with
    nothing marking it as a prototype-only site.
12. While viewing a collaboration on the globe, none of the left-nav mode
    buttons (Globe/Topics/Results/Documents) shows as "active" — a small
    "where am I" gap.
13. The "Full technical section" fallback text (the only description shown
    once P0-1 is fixed for entities that genuinely lack a plain summary, and
    currently shown as if it *were* the fallback for everyone) uses
    unexplained jargon and acronyms not expanded on that panel (e.g. "SURF,"
    "LArTPC," "wide-band on-axis beam") — wrong register for a newcomer who
    opens it looking for more explanation.
14. Timeline mode buttons (Single date/Range/Play) are 28px tall on mobile,
    under the usual touch-target guideline, though adjacency makes them
    tolerable in practice.

---

## What worked (fair picture)

- **Sources are genuinely, consistently inspectable** — every sourced field
  I checked (baselines, masses, beam power, formation dates, results) shows
  a quote, a locator, and an accessed date on request. This is the strongest
  part of the tool.
- **Evidence-class wording matches the ontology's A19 spec verbatim** —
  "On the official institution list (as of 2026-09)," "INSPIRE author
  profile lists this collaboration" — exact phrasing, correctly applied.
- **Institution → people → "Open in HEP Graph" handoff works end-to-end**,
  correctly pre-filling the researcher in HEP Graph's connection explorer.
- **Result-type wording is well-calibrated against real physics history** —
  no result anywhere over-claims "discovery" when the source only supports
  "evidence" or "observation"; the 2012 Higgs results are correctly typed
  `observation`, matching their actual paper titles.
- **Back/forward and reload-with-panel-open both work correctly.**
- **Deep links to experiments/facilities/topics/results all work.**
- **The WebGL-disabled fallback is excellent** — clear explanation banner,
  full accessible data tables, same working detail panels, zero errors.
- **Keyboard navigation reaches globe markers with a clearly visible focus
  ring, and Enter activates them correctly.**
- **`prefers-reduced-motion` is honoured cleanly** — idle auto-rotation
  drops from 15px/2s drift to 0px/2s.
- **Large-collaboration institution arcs (CMS, 286 institutions) render
  without performance problems or errors.**
- **Facility-tier globe markers (the coarser layer) do correctly reflect the
  timeline year**, dimming/hiding per `state_segments` — the underlying
  mechanism is sound; it's the detail panel and the finer site tier that
  don't participate in it.

---

## Bottom line

**Would a newcomer understand what they're looking at?** Not really, and not
because the content is missing — a good, plain sentence exists for DUNE and
simply never reaches the screen (P0-1), and the one place they're told
whether DUNE exists at Fermilab tells them it's history (P1-1). The raw
material for a genuinely good newcomer experience is already written; it's
disconnected from the UI by field-name mismatches.

**Would an expert trust it?** Not after the first timeline scrub. Result
wording, unit values, and sourcing are careful and correct everywhere I
checked — the kind of rigor that should earn trust — but the moment an
expert does the one thing this tool is built around (move the year slider)
and opens any panel, it states something false (P0-4). That single bug would
end an expert's trust in the rest of the page, even though most of the rest
holds up.

## Counts and top fixes

**Severity counts:** P0: 4 · P1: 5 · P2: 5

**Five findings I'd fix first:**
1. **P0-4** — panel status badges ignore the timeline year (falsifies the
   core feature for every entity, every year).
2. **P0-1** — plain-language summaries exist in the data but never render
   (single field-name fix restores the tool's main value for newcomers).
3. **P0-3** — "0 confirmed members" on every collaboration, contradicting
   the institution count one line below it.
4. **P0-2** — blank document titles/dates across the entire document
   library.
5. **P1-1** — DUNE (and any under-construction experiment) mislabeled
   "Historical" on its own host facility's panel.

**Would a newcomer understand what they're looking at, and would an expert
trust it?** No to both, for the same underlying reason: the data and sourcing
underneath this tool are careful and mostly correct, but four field-name/
wiring bugs between that data and the screen mean the UI itself states
things (no summary exists; 0 members; wrong historical era; frozen status
badge) that the atlas's own data directly contradicts. Fix the four P0s and
this would be a genuinely trustworthy, newcomer-friendly tool — the
underlying content already supports that; the rendering layer currently
doesn't.
