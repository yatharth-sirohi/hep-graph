# Accessibility audit — HEP Atlas (`/atlas`) — addendum §23

Reviewer scope: keyboard navigation, focus management, ARIA, colour contrast,
non-colour-only encoding, timeline accessibility, screen-reader labels,
fallback-list navigation, and `prefers-reduced-motion` — the specific list in
§23, plus the spec's own framing that "a 3D globe cannot be the only way to
access information." Frontend fixes were made where a real gap was found;
everything else is measured and reported.

**Environment.** Local server (`.venv/bin/python -m hepgraph.server --port
8794`) on loopback. axe-core 4.11.1, injected at runtime via a route
interception to a same-origin URL (the app's own CSP is `script-src 'self'`,
correctly so — this audit works with that policy rather than weakening it;
see `findAxePath()`/`ensureAxeRoute()` in `tests/browser_atlas_a11y.cjs`) from
a local copy of the MIT-licensed npm package. Automated checks run in
headless Chromium via Playwright; the manual/keyboard checks are exercised
the same way keyboard-only and screen-reader users actually navigate (Tab
order, native `<details>`/`<input type=range>` semantics, ARIA attributes),
not by inspecting markup alone.

## What was checked

axe-core (WCAG 2.1 A + AA, plus axe's own best-practice rules) against eight
page/mode states, on both data trees (`?data=fixtures` and the generated
tree): the default globe view, an experiment panel, collaboration mode, the
filters panel (with an active filter), the timeline (moved to a past year),
results mode, the document library, and the no-WebGL fallback list (forced
via a canvas `getContext` patch, not a real GPU difference). 16 scans total.

Manual/keyboard checks, on both trees: search → keyboard-selected result →
panel (heading auto-focused) → Sources disclosure (native `<details>`,
opened with Enter) → Escape → focus returns to the search input; the
timeline slider operated with arrow keys, with its `aria-live="polite"`
readout announcing the new year; a filter checkbox toggled with Space,
announced via the `aria-live="polite"` chip row, without losing keyboard
focus across the re-render; Escape closing the mode panel (Topics/Results/
Documents) and returning focus to the button that opened it;
`prefers-reduced-motion: reduce` producing zero measured idle marker drift
over 2 seconds; and a runtime (not just source-level) contrast check against
the actual computed styles of representative elements.

## Results

**axe-core: 0 WCAG violations, 0 best-practice violations, across all 16
scans** (8 states × 2 trees), after the fixes below. **Manual checks: 30/30
pass** (both trees; one — the "uncertain marker" check on the fixtures tree —
correctly reports SKIP rather than a false pass, since the fixtures bundle
carries no `certainty: "possible"` data to exercise). All of this is
reproducible with `node tests/browser_atlas_a11y.cjs` (`HEP_URL` and
`NODE_PATH` as in the brief); it writes
`test-results/atlas/a11y-report.json` (pass/fail per check) and
`test-results/atlas/a11y-axe-report.json` (per-state violation detail) —
both gitignored, so the counts here and the log below are the durable
record.

Evidence log: `test-results/atlas/logs/a11y.log`.

## Findings and fixes

### P1 — WCAG AA contrast failures across most secondary text

`--muted` (`#5c6d78`), used for panel subtitles, key-spec labels, source
metadata, empty-state notes, the timeline legend, the footer data-version
label and more, measured **2.2–3.4:1** against the four backgrounds it
appears on (`--paper`, `--panel`, `--panel-2`, `--navy-2`) — all below the
4.5:1 WCAG AA minimum for normal text, and none of these are large text.
Separately, `.error-note` (`Could not load sources: …`, `Could not load this
entity: …`) referenced an undefined `--danger` custom property, falling back
to a hardcoded `#c0392b` that measured **2.9:1** on `--panel` — the color
naming exactly the class of error CLAUDE.md's "a database or upstream
failure is an error" rule cares about was itself close to illegible.

**Fix** (`static/atlas/atlas.css`): `--muted` changed to `#98a3a9`
(4.59–7.09:1 across all four backgrounds); `--danger` defined as `#d4786e`
(5.05:1 on `--panel`, 5.84:1 on `--paper`). Both computed with a WCAG
relative-luminance script and locked in at runtime by the "contrast:
representative text/background pairs meet WCAG AA" check (measures actual
`getComputedStyle` colors on `#detail-panel .panel-subtitle`, `.kv-list dt`,
`#data-version-label`, `#atlas-search`, compositing through any transparent
backgrounds, not just the CSS source).

### P1 — Non-text (UI-component) contrast below 3:1 on interactive borders

`--line` (`#26404f`), used as the border for the search input, mode-toggle
buttons, ghost/text buttons, role-filter chips and select dropdowns,
measured **~1.5:1** against `--paper`/`--panel` — well under the 3:1 WCAG
1.4.11 minimum for a UI component's boundary, on exactly the controls whose
border is the only cue they're clickable (no filled background).

**Fix**: added `--line-strong` (`#5c6f7b`, 3.02–3.49:1) and applied it to
`#atlas-search`, `.mode-toggle`, `.results-filters select`,
`.text-btn`/`.jump-year-btn`, `.role-btn`, and `.filter-chip.filter-clear-all`
— the interactive controls, not the purely decorative section dividers
(`.panel-section`, `.filters-panel details`, table row borders), which are
exempt under the same WCAG note and were left as `--line` to avoid an
unnecessary visual overhaul.

### P1 — "Uncertain" globe markers had no visual encoding at all (not even color)

`docs/HEP_ATLAS_ARCHITECTURE.md` describes certainty `"possible"` segments as
something "the globe hatches." In `static/atlas/js/globe.js`,
`applyTimelineClasses()` did correctly toggle an `is-possible` class onto the
marker element — but `atlas.css` had **no rule for `.is-possible` at all**,
and the marker's own SVG glyph was built with `hatched: false` hardcoded in
`makeInteractiveElement()`, regardless of the entity's actual certainty. The
result: an uncertain-status marker was pixel-identical to a certain one, on
every visual channel — not a color-only violation, but the more basic gap
underneath it. Verified against the generated bundle's 435 `"possible"`
segments (e.g. `facility:baikal-deep-underwater-neutrino-telescope`
construction, 2015).

**Fix**: `hatched` is now computed per-marker from the timeline-resolved
certainty *before* the glyph is built (`segmentsPresence()` in `globe.js`,
threaded through `makeMarkerElement`/`makeInteractiveElement` into
`buildGlyph()`), so an uncertain marker renders an actual diagonal-hatch
fill — a real shape/pattern difference, not a class with no effect. The
accessible name also gains an `"(uncertain)"` suffix (combined with the
existing `"(approximate location)"` A23 suffix into one parenthetical when
both apply), so the distinction reaches a screen reader too, matching how
the location-approximation suffix already worked. Locked in by the
"non-colour-only encoding" check, which scrubs the generated tree to 2015
(a year with real `"possible"` facility segments — the default/current year
has none) and asserts both the hatch pattern and the label suffix; it
correctly SKIPs on the fixtures tree, which has zero `"possible"` segments.

**P2, not fixed**: the timeline legend (bottom bar) represents "Uncertain
(possible)" with a small dashed-outline dot, a different glyph family from
the hatch-fill pattern the marker itself now uses. Both correctly avoid
relying on color alone, but a sighted user comparing the legend swatch to an
actual marker won't see the same shape. Left as-is rather than redesigning
the legend within this pass; worth reconciling in a follow-up.

### P1 — Escape did not close panels, and closing them did not restore focus

Neither the detail panel nor the mode panel (Topics/Results/Documents) had
any Escape handling, and the close button
(`#close-detail`/`state.navigate({entity: null})`) did not return focus
anywhere — a keyboard user closing a panel landed on `<body>`, losing their
place entirely. The brief's own "search → result → panel → sources
disclosure → back" sequence had no working "back" by keyboard other than Tab
away or a mouse click on the (small) close button.

**Fix**: `panels.js` now tracks `openerElement` — captured (from
`document.activeElement`) only when a genuinely new entity opens, not on a
timeline-driven re-render of the same one — and restores it via
`.focus()` when the panel closes. `modes.js` mirrors the same contract for
the mode panel. `app.js` adds one document-level `keydown` listener: Escape
closes the detail panel if one is open (checked first, since it renders on
top), else the mode panel if one is open. Locked in by two browser checks:
closing the detail panel via Escape returns focus to `#atlas-search`;
closing the mode panel via Escape returns focus to the `[data-mode="topic"]`
button.

### P2 — two axe best-practice findings, both fixed

- `heading-order`: the mode-panel's own headings ("Research topics",
  "Results", "Document library") were `<h3>`, skipping the page's `<h2>`
  level entirely (the only `<h1>` is the page title in the header). Changed
  to `<h2>` in `modes.js` — a sibling landmark's own top-level heading, same
  level as the detail panel's entity `<h2>`, not a sub-heading of anything.
- `region`: two live-region notices (`#data-notice`, `#atlas-error`) sat
  directly between `<header>` and `<main>`, outside any landmark —
  `role="status"`/`role="alert"` are live-region roles, not landmark roles.
  Wrapped both in a `<div role="region" aria-label="Site notifications">` in
  `index.html`. Separately, `#timeline-bar` was `role="group"` — a grouping
  role, not a landmark — despite being its own top-level section between
  `<main>` and `<footer>`; changed to `role="region"` in `timeline.js`
  (its existing `aria-label="Timeline"` now names a real landmark, letting a
  screen-reader user jump to it directly the same way they already can for
  the filters aside).

### Already correct (re-verified, not re-fixed)

- Skip link, `role="combobox"` search with `aria-expanded`/
  `aria-autocomplete`/`aria-controls`/`aria-activedescendant`, and the
  search results listbox's keyboard handling (arrows, Enter, Escape) were
  already correct.
- Cluster markers are real, focusable, Enter/Space-activatable controls with
  a descriptive `aria-label` ("N facilities near here — …. Press Enter to
  zoom in and expand.") — already correct, and covered independently by
  `browser_atlas.cjs`'s clustering check.
- The Sources disclosure's loading/error/retry states already used
  `role="status"`/`role="alert"` appropriately.
- The no-WebGL fallback (`fallback.js`) already renders fully accessible
  `<table>`s with `<caption>` and `scope="col"` headers, reusing the same
  detail panels — confirmed by both the axe scan (0 violations) and the
  existing `browser_atlas.cjs` fallback checks.
- `prefers-reduced-motion` was already honoured for the globe's idle
  auto-rotation and its initial-load fly-in (no camera animation at all
  under `reduced-motion: reduce`); the automated check in
  `browser_atlas_a11y.cjs` now measures 0px marker drift over 2 seconds to
  lock this in, rather than relying on a code comment.
- The role-filter buttons (institution panel), filter checkboxes and
  timeline mode buttons were already native, labelled, keyboard-operable
  controls with visible `:focus-visible` outlines.

## Severity tally

P0: 0. P1: 3 found, 3 fixed (contrast — text and UI-component; uncertain-
marker encoding; Escape/focus). P2: 3 found, 2 fixed (heading order; landmark
containment ×2 — notices and timeline bar), 1 documented (legend/marker
glyph-family mismatch for "uncertain").

## What remains

- The legend/marker glyph mismatch for "uncertain" certainty (P2 above).
- This pass audited the specific eight states the brief named; it did not
  exhaustively axe-scan every entity-panel variant (e.g. the topic panel,
  the institution panel, every document/result panel) — those share the same
  rendering code paths as the experiment/facility panels that were scanned,
  but were not scanned individually.
- No manual screen-reader (VoiceOver/NVDA) session was run; this audit is
  axe-core plus ARIA/keyboard/focus/contrast verification against the DOM
  and accessibility-relevant attributes, which is what was available in this
  headless environment.
