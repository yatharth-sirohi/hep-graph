# HEP Atlas iterative learning improvements — 19–20 November 2026

The user asked for an active inspect→choose→implement→verify loop. Work continues on the existing `atlas-learning-questions` branch, starting this loop at `b2add215`. No automation, production deployment, merge, tracking, account or paid service was added. The original [connected learning report](LEARNING_2026-11-19.md) retains the baseline/source audit and existing data and comprehensive-suite limits.

## Cycle 1: predict and test energy doubling

Committed as `00dca966`. The beam lab now offers an in-place prediction experiment near its first maximum. A keyboard-accessible button moves the actual curve marker to doubled energy and reveals why the phase halves. It reports the actual supported control values: T2K 0.60→1.20 GeV gives 49.42%; DUNE 2.59→5.18 GeV gives 50.04%. It distinguishes those rounded results from the ideal 100%→50% calculation. Manual edits or restored energy clear stale feedback.

Verification: tests failed before implementation; 10 learning unit tests passed afterward. Chromium and WebKit passed desktop and 360px predict/reveal, marker movement, energy URLs, keyboard focus and feedback reset checks. Full repository suite: 803 passed, 139 skipped.

## Cycle 2: compare at the same L/E

Committed as `dfcdc8dc`.

The existing baseline selector gains an optional “Keep L/E” checkbox. It scales energy with distance before rounding to the lab’s 0.01 GeV increment, making a controlled T2K/DUNE comparison possible. Default behavior still holds energy fixed. A match outside 0.2–8 GeV is refused with an accessible explanation, and the original setup stays selected. The checkbox is restored by `le=1` in beam-view and beam-tour URLs; it is cleared when leaving that scope.

The calculation follows the lab’s existing cited two-flavor vacuum formula with fixed teaching parameters. Equal L/E gives equal phase and conversion probability in that model; rounding is explicit. It remains an illustrative teaching model, not a DUNE prediction, event-rate calculation or substitute for three-flavor matter effects.

The final review found and resolved alias-state loss, obsolete hidden text in the computed accessible description, and a misleading rounded boundary refusal. Both engines pass four focused review regressions; 23 calculation/navigation/tour-player tests pass. Both engines also pass the desktop/360px comparison tests and the complete phone question→lab→result→primary-paper journey. Final post-review repository verification: **807 passed, 139 skipped**. The independent review confirmed all findings resolved.

## Cycle 3: continue from evidence to a worked question

Committed as `761edc71`.

Both curated Higgs evidence trails now offer “Compare the Higgs masses.” It opens the existing Higgs hunt step 7, where learners predict whether the mass fits agree and reveal the sourced calculation under an explicit independent-error approximation. This reuses the same tour player and existing scientific content. The evidence display accepts optional next-question metadata, so other reviewed entries can supply a future exercise without adding assumptions to the renderer.

Results and Topics share one tour-step link helper. Native/copied links retain data, embed and projector settings, supply their own step, and stay synchronized if Projector mode changes while the panel remains open. The source mass fits and separate discovery significances were not changed; this exercise does not combine the discovery significances.

Final verification: **808 passed, 139 skipped** in the full repository suite; **24 passed** in the focused evidence/learning/tour-player checks. Chromium and WebKit passed desktop and 360px journeys from both evidence trails to the question, keyboard reveal, worked answer, Back, copied links, theme changes, embed/data context and optional/missing evidence data. The separate HEP Graph browser regression passed at its mocked API boundary. Atlas validation at the preserved `2026-10-29` data date gives **0 errors, 1892 existing warnings, 4 informational**; all **84 generated files match**. Independent review found no remaining code blockers after the native-link fixes.

A rapid-navigation stress probe exposed an existing WebKit lifecycle issue: deferred globe asset requests can start while a cold document is being unloaded. The exact probe reproduces six errors on unchanged main and six on this branch, with matching call stacks in unchanged globe code. This was queued for cycle 4 and is resolved below. The copied-link learner test waits for page startup requests to settle and still asserts zero browser errors; no errors are filtered. Its final run passes both engines. Physical-device and screen-reader walkthroughs remain unperformed.

## Cycle 4: reliable cold-page exits

Committed as `eceeb178`.

The rapid-navigation failure is fixed. The trace showed the optional Earth texture and country-border requests starting after WebKit had begun leaving a document. Their creation is now part of globe initialization; loading, decoding and application remain asynchronous. Existing fallback behavior and once-only guards remain. The change adds no unload listeners.

The new regression failed before the fix and now passes in Chromium and WebKit at 360px: four rapid cold-page exit cycles, normal loading of both assets, keyboard energy input and real Back/forward restoration of energy and fixed-L/E state. A separate slow-assets case holds both optional requests while the base canvas is visible, opens the beam question and operates the lab before releasing either request. This verifies usability while loading, not a first-frame timing budget or a persisted history-cache hit.

The connected phone journey through all three questions, the lab and both primary papers passed again in both engines. Full repository suite: **808 passed, 139 skipped**. Independent review found no correctness, fallback or history blockers. Data/source values and the separate HEP Graph app were unchanged; the most recent dedicated Graph browser regression remains the cycle 3 pass.

This led to the two-flavor learning interaction in cycle 5 below.

## Cycle 5: track both flavors

Committed as `e1d1f929`.

“Track both flavors” expands beneath the existing oscillation curve. The same energy control updates a solid/striped probability balance, text percentages and a selected-energy/sourced-baseline caption. It distinguishes retaining the starting flavor from absorption and detector response; the two generic flavors belong to the closed two-flavor vacuum teaching model. The existing DUNE/three-flavor limitations remain visible. No experimental values, fitted parameters, URL controls or second tour were added.

The pure model exposes conversion and its survival complement. The range’s accessible value announces both outcomes, while the new definition list adds no separate live region. Paired percentage rounding preserves a displayed total of 100%; the bar follows the unrounded model. Source: the existing [T2K atmospheric-deficit and two-flavor explanation](https://t2k-experiment.org/neutrinos/beyond-the-standard-model/), rechecked for this cycle. Survival = 1 − conversion is derived from that closed model, not an observed event fraction.

Final verification: **809 passed, 139 skipped** in the repository suite; **15 focused learning tests passed**, including no mixing, first maximum, half-phase and independent Python reference values. Chromium and WebKit passed desktop/360px values, keyboard controls, first-maximum/doubling actions, fixed-L/E baseline changes, captions, reload/Back and phone tour-step preservation. Both engines passed the connected phone question→lab→primary-paper journey again. Scoped axe checks on the expanded lab found **zero WCAG A/AA violations** in standard and Projector themes at 360px. Actual screen-reader speech and timing remain unverified. Independent review found no actionable findings and checked the source and all 1,562 T2K/DUNE energy pairs for probability bounds, complement and displayed rounding.

Try either lab route below and expand “Track both flavors.” The existing default curve and phone control/plot layout are preserved. Screenshots include the dark and Projector versions in the ignored verification-artifact directory.

This led to the sourced lab export in cycle 6 below.

## Cycle 6: save the selected lab as a teaching figure

Committed as `3723f08c`.

Save image now offers the selected oscillation lab alongside the existing default beam/Earth geometry figure. It captures the curve, selected point, first maximum and solid/striped flavor balance, with the actual energy and sourced baseline. The image includes the formula, units, fixed teaching parameters, source URLs and explicit two-flavor vacuum limitations. These values come from the current controls; changing energy refreshes an open preview and disables the previous download until its replacement is ready.

The existing dialog is also available on phones in chart views. Its new “Notes included in the image” disclosure provides readable text and clickable sources before saving. Single-figure exports retain their existing behavior. Both standard slide and double-size outputs are supported. The independent review found and resolved a presenter-mode Enter/Space conflict; native export controls now work while retaining the tour step, presenter mode and Escape focus restoration. Follow-up review found no actionable issues.

Final fresh verification: **809 passed, 139 skipped** in the full repository suite. Chromium and WebKit each passed desktop and 360px figure selection, real PNG downloads, live energy changes, T2K/DUNE changes, sourced captions/notes, temporary-node cleanup and keyboard/presenter actions. Both engines also passed the mobile question→lab→Higgs-paper journey. The classroom suite passed **8 tests with 0 skips/errors**; the separate HEP Graph mocked-API browser regression passed. Scoped axe A/AA checks of the dialog and phone opener found **0 violations** in standard and Projector themes. JavaScript syntax and diff checks passed. Downloaded PNGs were visually inspected at 1920×1080, including the WebKit mobile DUNE export. Physical iOS save UI and actual screen-reader speech remain unverified.

Try either lab route below, open Save image, then choose “Oscillation lab.” The saved figure includes the current URL for reopening the selected state. Artifacts and fresh logs are retained under the ignored `test-results/atlas-iterations/` directory (`cycle6-reverified-*`, `*-oscillation-export.png`). No physics source values were changed.

This led to the SNO evidence question in cycle 7 below.

## Cycle 7: connect flavor change to SNO's measurements

Committed as `6261ba5b`.

“Track both flavors” now links to a predict/reveal question in the existing neutrino-oscillation story, SNO step 3 (2002). It opens the existing globe at SNO and asks what CC and NC inferred fluxes would imply if every arriving active neutrino were electron flavor. The worked answer compares the paper's standard-spectrum central values, **CC = 1.76** and **NC = 5.09 million cm⁻² s⁻¹**: **CC/NC ≈ 0.35, about 35%**. It distinguishes inferred fluxes from raw event counts, includes no propagated uncertainty or single-energy survival interpretation for that ratio, and attributes **5.3σ** to the collaboration's non-electron-flavor fit rather than the division. The lab link explicitly says its atmospheric-scale teaching model is not a fit to these solar data.

The existing SNO source record now opens the versioned primary PDF at the flux equations. Exact locators: **PDF page 2** for CC/NC flavor sensitivities; **page 4**, below Table II, for the shape-constrained fluxes and units; **page 5** for the non-electron fit and significance. The earlier paper/result values were preserved. No new tour player or additional result records were introduced.

Question links in panels and the lab now share the same native-link helper, retaining data/embed/theme context and a destination-specific step. Enter works during presenter mode, while B/W blank screens retain the player's normal “dismiss first” behavior. Review reproduced and verified that edge case. Expanded source quotes now wrap long uncertainty expressions inside the tour card; both engines reproduced the overflow before the scoped fix. Final independent review found no actionable code/source findings.

Final repository checks: **812 passed, 139 skipped**. The focused learning/tour suite has **43 passing tests**, including independent division, primary-source/units checks, invalid calculated-result detection and scoped link state. Chromium and WebKit each pass desktop/360px lab→SNO question→worked answer→actual primary PDF, native/copied links, embed/theme context, Back, keyboard activation and B/W presenter dismissal. Both engines also pass the existing flavor-balance regressions. Scoped axe A/AA checks report **0 violations** for the expanded SNO question and the lab disclosure in standard and Projector themes at 360px. The separate HEP Graph browser regression passes at its mocked API boundary.

The source was actually rechecked on **2026-11-19**; its access dates and the new claim verification dates were not backdated. Generated data is therefore built at **2026-11-19**. All **84 generated files match**. Moving that cutoff updates derived timeline endpoints, some derived statuses/coverage and bundle metadata; it does not verify unrelated schedules. Validation at this date gives **5 existing status errors, 1892 warnings and 4 informational**, identical to unchanged main. The 5 authored status mismatches are Main Injector, NuMI, NOvA and its two detectors. No new validation error remains. This currency gap is the next inspection, before treating current schedules as newly verified.

Initial parallel runs of the existing Higgs evidence-link regression timed out; full isolated reruns pass in both engines. Both original connected phone question→lab→Higgs-paper journeys pass in their final sequential runs. Actual screen-reader speech, physical phones and live isolated database integration remain unverified. Durable cycle-7 logs/screenshots are in the ignored `test-results/atlas-iterations/` directory.

## Cycle 8: distinguish a scheduled restart from a reported beam state

Committed as `074240ce`.

The five dated status mismatches are corrected. Their shutdown rows had used the **planned October 2026 restart as an end**, so after October the compiler showed Main Injector/NuMI/NOvA as planned and the two NOvA detectors as unrecorded, while NOvA lost its validated/globe-ready coverage flag. The last reported shutdown condition now has an open end with an explicit assumption note. The proposed NuMI run remains a separate planned annotation; the detector annotations describe a derived beam-data schedule, not detector power state. No restart or continuing shutdown was claimed as a new observation, and A3 timeline semantics were preserved.

The affected panels qualify the badge as **“Shutdown · last reported”** and visibly state that restart is unconfirmed in Atlas sources. A native disclosure loads only the reported-condition/run evidence through the existing source renderer. It handles failure/Retry and preserves keyboard focus. A pure helper respects the full precision/bounds of a planned start, historical selections and a later observed lifecycle state. It matches exactly these five records. Historical active states and the search entry remain; NOvA’s validated and globe-ready coverage flags are restored.

Primary-source audit: the [April 2026 PAC report](https://pac.fnal.gov/wp-content/uploads/2026/06/Public_PAC_Report_April_2026.pdf) records MI not operating since July 2024 (PDF page 2) and the stretch run schedule (page 3). The [Fall 2026 PAC report](https://pac.fnal.gov/wp-content/uploads/2026/10/Final_Public_PAC_Report_Sept2026.pdf#page=4) still describes stable beam on 1 October as planned and a 12-week FY27 run with a 20-week stretch goal (page 4); page 5 calls the restart upcoming. Narrow official-source searches did not find a later confirmation; this does not establish that none exists. Access/check dates reflect the actual November 19 audit. The existing broader July NOvA news statement remains acknowledged; it does not identify which data were being taken.

The three new unit regressions failed before implementation. The corrected data/helper and existing schema checks pass **74 tests**. Current-date validation gives **0 errors, 1892 existing warnings and 4 informational**; all **84 generated files match**. Review found and independently reproduced a Retry focus issue; the fix keeps focus on the disclosure summary, and follow-up review found no remaining code blocker. The repository run passed **815 tests, 139 skipped**, and both original connected phone physics-learning journeys passed again, including the live arXiv primary papers. The separate HEP Graph mocked-API browser regression passed. The final panel-order/beam-scope refinements pass their post-run Chromium/WebKit desktop and 360px checks: all five records, default beam-condition wording, reading order, lazy evidence, historical views, beam-view/Back, failure recovery and Retry focus. Scoped axe A/AA checks report **0 violations** in standard and Projector themes. Final phone rendering was visually inspected; syntax and whitespace checks pass. The status qualification stays beside its badge, before the introduction.

**External access limit:** the PAC origin sometimes serves a Cloudflare challenge to automated browsers/API requests (403). The public PDF downloaded successfully via curl and was read/visually checked. Final WebKit desktop and 360px runs each downloaded the real 199,806-byte PDF (HTTP 200), both matching it byte for byte. Final Chromium desktop and 360px runs reached the exact URL but received HTTP 403 challenge pages, correctly recorded as unverified PDF responses. The browser regression records the actual external page/download outcome at the exact primary URL, and never counts a challenge page as a verified PDF. Reliable access across browser sessions remains outside the app’s control, and no challenge bypass was attempted. The original arXiv learning-paper journeys are checked separately. Durable cycle-8 logs, source-page rendering and screenshots are under ignored `test-results/atlas-iterations/`. The downloaded Fall report's SHA-256 is `3b0f9ced6d3677f68eb84f33f7931932c79ba598e5a7770c285cece18fe53d75`.

## Cycle 9: predict and trace an accelerator dependency

Committed as `4b60b91c`.

A campus can have several proton paths with different dependencies. The existing Fermilab **Follow the proton** map player already contains the recorded Main Injector → NuMI and Booster → BNB transfers, so this cycle adds one prediction to that player. The five restart-context panels offer **Predict which beam needs Main Injector**. It opens the real historical 2016 map at Main Injector, with the question expanded. Learners choose NuMI, the Booster Neutrino Beam, or both; Test reveals the answer and traces the existing NuMI transfer. Two buttons let them compare the existing branches without introducing geometry or another player.

The answer and trace indices come from the compiled chain. A guard hides the pilot if the feeder data or required drawn stages no longer match the reviewed citations. The prompt explicitly assumes other components are available. The explanation identifies a necessary proton connection; it does not establish delivered beam, rates or current operation. Historical 2016 is stated, rather than presenting an outage simulation of the current site.

The [NuMI beam paper, §2 opening paragraph, PDF page 6](https://arxiv.org/pdf/1507.06690v2#page=6) identifies Main Injector as NuMI's proton source. The [MiniBooNE flux paper, abstract, PDF page 2](https://arxiv.org/pdf/0806.1449v2#page=2) identifies Booster as the source for BNB. Both pinned primary passages were downloaded, extracted and visually checked on 19 November 2026. Their source IDs already belong to the respective authored beamline records. No science values, authored data or generated bundles change in this cycle.

Prediction state survives tracing but resets on a different chain/year or player closure. Native radios retain keyboard behavior; prediction interactions pause playback. The phone feedback is scrolled into the player while button focus is retained. Entry links preserve data, embed and theme settings, clear a prior range/map selection and use the existing `proton` URL field. Copied links start a fresh prediction; Back returns to the source record.

Verification: the three topology/source/navigation regressions and missing-link browser check failed before implementation. Focused learning/navigation checks passed **24 tests**. The final repository suite passed **818 tests, 139 skipped**. Chromium and WebKit passed desktop and 360px entry, keyboard radios, playback pause, wrong/correct predictions, existing map highlights/trace steps, persistent feedback across traces, year reset, Escape closure, copied native links, embed/theme context and Back. The exact two primary papers returned real PDF downloads with HTTP 200 from desktop Chromium and mobile WebKit. Scoped axe A/AA checks report **0 violations** for the new checkpoint before/after reveal in standard and Projector themes.

Phone inspection reproduced feedback partly outside the card; a failing visibility assertion now passes after scrolling the feedback into view without moving button focus. Independent review reproduced a second issue: opening the question during playback did not pause. That regression failed first and passes after pausing on native summary activation. Follow-up review found no remaining issue. Existing Higgs evidence → mass-question journeys pass in both engines at desktop/360px, as do the original connected phone questions → lab → Higgs primary-paper journeys. The extracted primary-link helper also passes the five restart panels, lazy evidence, keyboard Retry and native PAC PDF download in mobile WebKit. HEP Graph's mocked-API browser check passes. Live database integrations, physical phones and actual screen-reader speech remain unverified.

Current-date validation is **0 errors, 1892 existing warnings, 4 informational**; all **84 generated files match** at `2026-11-19`. Syntax and diff checks pass. Durable logs and visually checked phone screenshots are in `test-results/atlas-iterations/cycle9-*` and `*beam-dependency*`. No merge or deployment was performed.

## Cycle 10: compare recorded underground fluxes

Committed as `84583995`.

The existing chart, data table, qualitative newcomer checkpoint and sourced m.w.e./metre exercise remain in place. A comparison block now lets the learner select any two plotted sites as A/B. The same chart labels those points and adds solid/dashed square outlines while retaining its measured/hollow markers and separate keyboard focus ring. The block shows each recorded value and uncertainty, the conversion to cm⁻² s⁻¹, the dimensionless central-value ratio, signed log₁₀(A/B) and vertical separation in decades. No extra plot or tour system was added.

The default pair exposes a real unit trap: LNGS Hall C's 3.432×10⁻⁴ m⁻² s⁻¹ is 3.432×10⁻⁸ cm⁻² s⁻¹. Dividing by SNOLAB's 3.31×10⁻¹⁰ cm⁻² s⁻¹ gives about **104**, or **2.02 decades**. The [Borexino primary abstract](https://arxiv.org/abs/1808.04207) (v3) and [SNO primary abstract](https://arxiv.org/abs/0902.2776) (v1) were rechecked on 19 November 2026. The selected-source disclosure reuses each flux's existing quote, locator, reference-surface/angular-cut definitions and primary references. These conventions differ; the displayed ratio compares reported central values and does not isolate the effect of depth. Recorded uncertainties are retained, without calculating an interval or significance for the ratio. Approximate/simulated values retain their label and hollow mark.

The new `uf=<siteA>,<siteB>` query follows the current short-query pattern and is scoped to this view and its existing tour. It restores copied links, reloads and Back/Forward; leaving for a record clears it. Missing/repeated saved choices show a recovery instruction and no false result. Controls retain their nodes/focus during updates. Selected-source requests remain lazy, reject stale responses and offer a focused Retry. The original tour's predict/reveal and worked calculation are unchanged.

The image check found A/B outlines survived export but the general figure URL omitted the pair. The existing export notes now carry the two recorded/normalized values, ratio/log separation, limitations and an exact reopen link with the selected pair. The plot and original legend continue to use the same exporter.

Final verification: the repository suite passed **821 tests, 139 skipped**. The initial three pure regressions and missing-block browser check failed before implementation. **35 focused tests** pass. The repository's lazy comparison-view guard initially matched any filename ending in “compare.js”; it was corrected to protect the exact `compare.js` / `compare-rows.js` basenames, without prohibiting this small pure arithmetic helper. All **20 research-tool tests** pass, and review verified positive and negative guard cases. The outdated failing full run was deliberately interrupted after its identified failure; the corrected full run passed and is retained as `cycle10-pytest.log`.

Chromium and WebKit pass desktop and 360px comparison journeys: common-unit math, A/B labels/outlines, missing/repeated pair recovery, simulated labels, reload, native source links, actual destination record headings, Back/Forward and chart-point focus. Mobile cases force a source failure, exercise keyboard Retry focus and change selection while the retry loads. Both primary abstracts opened with HTTP 200 from desktop Chromium/mobile WebKit and contained the published measurements. Native type-ahead changes the choice without blanking the presenter or moving the tour step. The existing energy-frontier chart still fades future points, shows the chosen-year marker and retains keyboard focus through a real resize redraw in both desktop engines.

The actual Chromium PNG was downloaded and visually checked with A/B marks, both values, the ratio, limitations and the exact pair reopening link. Its export notes and link are asserted by the browser test. Scoped axe A/AA checks report **0 violations** for chart/comparison in default, selected-sources and invalid-pair states in standard and Projector themes. Final 360px renderings were inspected. Both original connected phone question → oscillation lab → Higgs primary-paper journeys pass again, along with the separate HEP Graph mocked-API browser check. Independent follow-up reviews found no remaining blocker.

Current-date validation remains **0 errors, 1892 existing warnings, 4 informational** and all **84 generated files match** at `2026-11-19`. Syntax/diff checks pass. No authored/generated data, Graph application code, dependencies, accounts, tracking or paid services changed; no merge/deployment occurred.

Independent review reproduced loss of chart-point focus when Back changed the pair. That browser assertion failed first; the shared focus-preserving redraw now handles resize and highlight changes. Native type-ahead changes the selection while preserving presenter state. In this macOS headless environment, popup-menu arrow/Home/End selection is not synthesized even for a bare native HTML select with no handlers; those native popup interactions remain unverified. No custom keyboard handler was added to emulate them. Physical phones, actual screen-reader speech and live database integrations remain unverified. Durable cycle-10 logs, the native-select isolation probe, screenshots and actual PNG export are under ignored `test-results/atlas-iterations/`.

## Cycle 11 (20 November): choose the meaning of the local p-value

Audit found the evidence trail already distinguishes observed/expected significance and local/global results. The missing learning action was committing an interpretation before revealing the existing reciprocal calculation. Optional `choices` and `correct_choice` now extend the existing A28 question/player; they do not add another tour, route, score or quiz service. The validator enforces two to five distinct choices, supported fields, a matching answer ID and primary-question-only placement. The bundle retains the new metadata; questions without choices retain their reveal, and worked examples remain sourced readings/calculations.

Only the Higgs step-6 question pilots the feature. The learner chooses between a background-only tail at the tested mass, a model probability and a full-scan probability. Reveal retains the actual selection, labels the supported alternative in text and shows the existing 1/p ≈ 590 million calculation. The explanation says at least as signal-like, under the background-only model, at a fixed tested mass and on average. The denial of a model posterior is explicitly noted as interpretation of the conditional definition. No new significance or combination is calculated; published observed/expected values and all result records are unchanged.

The [ATLAS v1 paper, §7, printed p.16 / PDF page 17](https://arxiv.org/pdf/1207.7214v1#page=17) supports the local/global interpretation; the definition was extracted and visually checked against the actual page. The [CMS v1 §4 definition, printed p.6 / PDF page 8](https://arxiv.org/pdf/1207.7235v1#page=8) independently agrees. The existing ATLAS full-text source is pinned to the verified v1 PDF, avoiding a duplicate source. It was read on November 19 local time; the build uses November 20 after the day changed. Step text also distinguishes the later paper's 5.9σ result from the preliminary July-4 presentation. Source quotes remain short and the numerical working is preserved.

An unanswered reveal stays closed, explains the requirement and focuses the radios. Native radio keys, Tab/Option-Tab, Enter/Space, presenter blank dismissal and Escape coexist. Wrong guesses are not silently replaced. Changing a choice hides stale feedback; new steps, copied links and closed/reopened tours start fresh. Responsive changes retain the current prediction. Focused question buttons/source disclosures now use native Enter/Space instead of triggering presenter navigation. Reveal keeps its focused control visible with the feedback on a phone sheet. The sheet expands for reading only after revealing a choice answer; Hide answer or Hide text restores visual space. A focused reveal is repositioned after crossing the phone breakpoint; someone reading a source is not pulled away. Selections stay in player memory and never enter the address or persistent storage.

The 13 new backend cases and missing-radio browser check failed first. The full repository suite passes **834 tests, 139 skipped**. After the final phone/reflow changes, **56 focused tour/learning tests** pass again; the broader Python/data run preceded those JS/CSS refinements. The new Chromium and WebKit desktop/360px journeys pass, including wrong/correct feedback, reset, presenter keyboard behavior, actual primary-PDF access, legacy mass-question reveal and deep links. Both browser PDF downloads are the same 650,541-byte document as the independently downloaded/visually checked source: SHA-256 `7721161751476f028d2f221631b902cc96059144a3382bf90eb1cfb30b9042d3`. Scoped A/AA checks report **0 violations** across unanswered, required, incorrect, correct and source states in both themes. Both original phone question → lab → Higgs primary-paper journeys also pass.

WebKit's default Tab preference skips native buttons, including a bare control with no application handlers; Option-Tab was verified to include the actual answer button in both viewport contexts. The regression uses that native gesture without changing browser settings or adding a custom Tab handler. One extra legacy WebKit evidence-follow-up run timed out waiting for a record link; an isolated replay with failure-state capture passed. A second isolated diagnostic replay also passed desktop and 360px, and the separate mocked-API Graph check passed. The original failure log is retained rather than erased; its cause is not established. The legacy regression now captures its route, panel state, browser errors and a screenshot on failure. A final original-journey WebKit run separately timed out waiting for the invalid-energy deep link (`e=NaN`) to render the default, after its Back and both primary-source checks had completed. Its isolated replay passed the complete phone journey. The original log is retained and that cause is also unestablished; failure capture was added to this regression, without changing the product based on a guess.

Manual visual review caught a real gap in the first browser assertions: they verified the reveal button but not the feedback. In 360px Projector mode the original 60% sheet left an 81px body and clipped the entire feedback message. A stronger visibility regression failed before the phone expansion/spacing fix. WebKit then exposed persistent offscreen feedback after desktop-to-phone reflow; measurements confirmed it stayed offscreen after settling, and the focused-reveal resize hook fixes that case. Final acceptance requires both the control and full feedback within the body, correct/incorrect predictions, folding/reopening, responsive changes and standard/Projector themes. The initial failed runs and before/after screenshots are retained. Final Chromium/WebKit desktop and 360px prediction journeys pass all of those visibility cases; both themes were visually inspected. The ten scoped accessibility states still report zero violations after the fix. Both original connected phone journeys pass again, with the WebKit qualification below. Independent final review found no blocker in the class lifecycle or guarded resize hook.

Actual-date validation is **0 errors, 1892 existing warnings, 4 informational**, and all **84 generated files match** at `2026-11-20`. A structural audit of the 55 changed generated files found geometry changes only in build date/version across 50 maps, plus expected manifest/version, one source URL/access date and one tour-step changes. No coordinates, physical geometry, result measurements or other authored records were backfilled. Logs, diagnostic probes and screenshots are retained under ignored `test-results/atlas-iterations/cycle11-*`. Physical phones, actual screen-reader speech, native select-popup arrows and live database integrations remain unverified. No merge/deployment occurred.

## Local routes and sources

Use the current local server at `http://127.0.0.1:8876` while the loop is running. From the feature checkout, restart it with the repository environment’s `python -m hepgraph.server --port 8876` when needed.

- T2K experiment and prediction: <http://127.0.0.1:8876/atlas?e=0.6#/view/beam-section/j-parc-neutrino>
- T2K ready to compare at fixed L/E: <http://127.0.0.1:8876/atlas?e=0.6&le=1#/view/beam-section/j-parc-neutrino>
- Corresponding DUNE setup at supported energy: <http://127.0.0.1:8876/atlas?e=2.61&le=1#/view/beam-section/lbnf>
- Beam question with comparison enabled: <http://127.0.0.1:8876/atlas?step=5&e=2.5&le=1#/tour/neutrino-beams-through-the-earth>
- ATLAS evidence: <http://127.0.0.1:8876/atlas#/result/atlas-higgs-observation-2012>
- CMS evidence: <http://127.0.0.1:8876/atlas#/result/cms-higgs-boson-observation-2012>
- Higgs interpretation prediction: <http://127.0.0.1:8876/atlas?data=generated&step=6#/tour/higgs-hunt>
- Same prediction in presenter mode: <http://127.0.0.1:8876/atlas?data=generated&step=6&present=1&theme=projector#/tour/higgs-hunt>
- Existing sourced mass-compatibility question: <http://127.0.0.1:8876/atlas?step=7#/tour/higgs-hunt>
- SNO prediction and sourced flux comparison: <http://127.0.0.1:8876/atlas?step=3#/tour/neutrino-oscillation-story>
- NOvA last-reported state and restart evidence: <http://127.0.0.1:8876/atlas?y=2026#/experiment/nova>
- Main Injector last-reported state: <http://127.0.0.1:8876/atlas?y=2026#/accelerator/fermilab-main-injector>
- Underground comparison, LNGS Hall C / SNOLAB: <http://127.0.0.1:8876/atlas?data=generated&uf=lngs-hall-c,snolab-underground-lab#/view/underground>
- Same comparison inside the original question: <http://127.0.0.1:8876/atlas?data=generated&step=6&uf=lngs-hall-c,snolab-underground-lab#/tour/going-underground-dark-matter>
- Fermilab dependency question (2016, Main Injector): <http://127.0.0.1:8876/atlas?data=generated&y=2016&proton=7#/map/fermilab>
- Existing NuMI transfer used by Test: <http://127.0.0.1:8876/atlas?data=generated&y=2016&proton=8#/map/fermilab>
- Existing Booster → BNB comparison: <http://127.0.0.1:8876/atlas?data=generated&y=2016&proton=10#/map/fermilab>
- Separate HEP Graph coauthorship search: <http://127.0.0.1:8876/>

Published measurement values were preserved; cycle 7 adds a worked comparison of rechecked SNO fluxes. Sources include the [SNO primary paper, CC/NC fluxes below Table II on PDF page 4](https://arxiv.org/pdf/nucl-ex/0204008v2#page=4), the [T2K experiment paper, §3.6.1](https://arxiv.org/pdf/1106.1238v2#page=10), [DUNE baseline passage, §1](https://arxiv.org/pdf/2007.06722v4#page=12), [T2K two-flavor formula and units](https://t2k-experiment.org/neutrinos/beyond-the-standard-model/), [PDG mixing review](https://pdg.lbl.gov/2024/reviews/rpp2024-rev-neutrino-mixing.pdf), and the versioned [ATLAS](https://arxiv.org/pdf/1207.7214v1) and [CMS](https://arxiv.org/pdf/1207.7235v1) papers. The previous report records exact figures and passages. Claims about phase changes and matching L/E are derived from the displayed formula.

Logs and screenshots for this loop are retained in the ignored `test-results/atlas-iterations/` directory. Earlier temporary `/tmp/` artifacts may expire; use the durable cycle-6 through cycle-11 logs for the latest iterations. Screen-reader hardware and physical phones have not been tested. Existing database-environment skips, aging-data validation findings and legacy monolithic-browser timing limits remain as documented in the original report.


## Reproduce the current loop checks

Use the repository Python environment and the existing Playwright installation, with the feature server on port 8876. In this workspace, use `/Users/yatharthsirohi/Desktop/HEP-Graph/.venv/bin/python` in place of `python`, and prefix the browser commands with `NODE_PATH=/Users/yatharthsirohi/Desktop/HEP-Graph/node_modules`:

```sh
python -m pytest -q -p no:cacheprovider
python -m pytest -q -p no:cacheprovider tests/test_atlas_restart_context.py tests/test_atlas_schema.py
python -m pytest -q -p no:cacheprovider tests/test_atlas_beam_dependency.py tests/test_atlas_proton_chain.py tests/test_atlas_learning.py
python -m pytest -q -p no:cacheprovider tests/test_atlas_predictions.py tests/test_atlas_tours.py tests/test_atlas_tour_player.py tests/test_atlas_learning.py
python -m pytest -q -p no:cacheprovider tests/test_atlas_underground_comparison.py tests/test_atlas_charts.py tests/test_atlas_learning.py tests/test_atlas_tour_player.py
python -m hepgraph.atlas.validate --build-date 2026-11-20
python -m hepgraph.atlas.build --build-date 2026-11-20 --check
HEP_URL=http://127.0.0.1:8876 node tests/browser_atlas_predictions.cjs
HEP_URL=http://127.0.0.1:8876 HEP_BROWSER=webkit node tests/browser_atlas_predictions.cjs
HEP_URL=http://127.0.0.1:8876 node tests/browser_atlas_underground_comparison.cjs
HEP_URL=http://127.0.0.1:8876 HEP_BROWSER=webkit node tests/browser_atlas_underground_comparison.cjs
HEP_URL=http://127.0.0.1:8876 node tests/browser_atlas_beam_dependency.cjs
HEP_URL=http://127.0.0.1:8876 HEP_BROWSER=webkit node tests/browser_atlas_beam_dependency.cjs
HEP_URL=http://127.0.0.1:8876 node tests/browser_atlas_experiments.cjs
HEP_URL=http://127.0.0.1:8876 HEP_BROWSER=webkit node tests/browser_atlas_experiments.cjs
HEP_URL=http://127.0.0.1:8876 node tests/browser_atlas_comparison_edges.cjs
HEP_URL=http://127.0.0.1:8876 HEP_BROWSER=webkit node tests/browser_atlas_comparison_edges.cjs
HEP_URL=http://127.0.0.1:8876 node tests/browser_atlas_evidence_followup.cjs
HEP_URL=http://127.0.0.1:8876 HEP_BROWSER=webkit node tests/browser_atlas_evidence_followup.cjs
HEP_URL=http://127.0.0.1:8876 node tests/browser_atlas_flavors.cjs
HEP_URL=http://127.0.0.1:8876 HEP_BROWSER=webkit node tests/browser_atlas_flavors.cjs
HEP_URL=http://127.0.0.1:8876 node tests/browser_atlas_navigation_lifecycle.cjs
HEP_URL=http://127.0.0.1:8876 HEP_BROWSER=chromium node tests/browser_atlas_navigation_lifecycle.cjs
HEP_URL=http://127.0.0.1:8876 node tests/browser_atlas_restart_context.cjs
HEP_URL=http://127.0.0.1:8876 HEP_BROWSER=webkit node tests/browser_atlas_restart_context.cjs
HEP_URL=http://127.0.0.1:8876 node tests/browser_atlas_sno_question.cjs
HEP_URL=http://127.0.0.1:8876 HEP_BROWSER=webkit node tests/browser_atlas_sno_question.cjs
HEP_URL=http://127.0.0.1:8876 node tests/browser_atlas_lab_export.cjs
HEP_URL=http://127.0.0.1:8876 HEP_BROWSER=webkit node tests/browser_atlas_lab_export.cjs
HEP_URL=http://127.0.0.1:8876 node tests/browser_database.cjs
```

The validator now reports zero errors at the November 20 cutoff; cycle 8 resolves the five inherited status mismatches found in cycle 7. The build check verifies all generated files at the new cutoff. The connected phone question→lab→result→primary-paper journey uses `node tests/browser_atlas_learning.cjs` (set `HEP_BROWSER=webkit` for WebKit).
