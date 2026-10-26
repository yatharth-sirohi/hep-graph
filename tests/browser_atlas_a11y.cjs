/* HEP Atlas accessibility audit (addendum §23).
   npm install --no-save playwright (or export NODE_PATH at an install that
   already has it), then: node tests/browser_atlas_a11y.cjs

   Runs axe-core (if a local copy can be found — see findAxePath()) against
   eight page/mode states on both data trees, plus manual checks this repo's
   axe-core copy can't express on its own: keyboard-only traversal (search ->
   result -> panel -> sources disclosure -> Escape -> back), timeline slider
   keyboard operation + live year announcement, filter-checkbox keyboard
   operation + live chip announcement, Escape closing a panel and returning
   focus to its trigger, prefers-reduced-motion (no idle rotation), and a
   runtime contrast check (actual computed styles, not just the CSS source)
   for representative text/background pairs. */
const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const base = process.env.HEP_URL || "http://127.0.0.1:8790";
const output = process.env.HEP_ATLAS_OUTPUT || path.join(__dirname, "../test-results/atlas");
fs.mkdirSync(output, { recursive: true });

const DATA_TREES = [
  { label: "generated", query: "" },
  { label: "fixtures", query: "?data=fixtures" },
];

// Workstream A1: a real site id per tree, so the new site panel (previously
// "Unknown entity type" — state.js's TYPE_PREFIX and panels.js's RENDERERS
// lacked site/detector/accelerator/beamline) gets its own axe scan alongside
// the other panel states below.
const SITE_SLUG = { generated: "fermilab-main-campus", fixtures: "fermilab-sbnd-hall" };

function findAxePath() {
  const candidates = [];
  if (process.env.NODE_PATH) {
    for (const dir of process.env.NODE_PATH.split(path.delimiter)) {
      candidates.push(path.join(dir, "axe-core", "axe.min.js"));
    }
  }
  // Fallback: a known local copy of the same MIT-licensed npm package, used
  // only to inject into the page at test time — never shipped or committed.
  candidates.push("/Users/yatharthsirohi/Desktop/ourIowaCityWebsite/our-iowa-city/node_modules/axe-core/axe.min.js");
  try {
    candidates.push(require.resolve("axe-core/axe.min.js"));
  } catch (error) {
    // not installed on the module path; the loop below just skips it
  }
  for (const candidate of candidates) {
    if (candidate && fs.existsSync(candidate)) return candidate;
  }
  return null;
}

const AXE_PATH = findAxePath();
if (!AXE_PATH) {
  console.warn("WARNING: no axe-core bundle found (checked NODE_PATH and a known local copy) — "
    + "axe scans will be skipped; manual checks still run.");
} else {
  console.log("Using axe-core from", AXE_PATH);
}

const results = [];
const axeReport = []; // { tree, state, violations: [...], skipped }
let failed = false;

const record = async (name, fn) => {
  const start = Date.now();
  try {
    await fn();
    results.push({ name, status: "passed", milliseconds: Date.now() - start });
    console.log("PASS", name);
  } catch (error) {
    failed = true;
    results.push({ name, status: "failed", milliseconds: Date.now() - start, error: String(error && error.stack || error) });
    console.error("FAIL", name);
    console.error(error);
  }
};

async function setRangeValue(locator, value) {
  await locator.evaluate((el, v) => {
    const proto = window.HTMLInputElement.prototype;
    const setter = Object.getOwnPropertyDescriptor(proto, "value").set;
    setter.call(el, String(v));
    el.dispatchEvent(new Event("input", { bubbles: true }));
  }, value);
}

const AXE_SOURCE = AXE_PATH ? fs.readFileSync(AXE_PATH, "utf8") : null;
// The app is served with a strict CSP (`script-src 'self'`, correctly so —
// not something this audit should weaken). `addScriptTag({ path })` injects
// an inline <script>, which that policy blocks outright. Route-intercept a
// same-origin URL instead and fulfill it locally with the axe-core source —
// the browser sees a normal same-origin script request, which the existing
// CSP already allows, and the real server never even sees this path.
async function ensureAxeRoute(page) {
  if (page.__axeRouted) return;
  await page.route("**/__axe-core-test-only__.js", (route) => route.fulfill({
    status: 200,
    contentType: "application/javascript",
    body: AXE_SOURCE,
  }));
  page.__axeRouted = true;
}

async function runAxe(page, tree, stateLabel) {
  if (!AXE_PATH) {
    axeReport.push({ tree, state: stateLabel, skipped: true, reason: "axe-core not found" });
    return { violations: [] };
  }
  await ensureAxeRoute(page);
  await page.addScriptTag({ url: "/__axe-core-test-only__.js" });
  const axeResult = await page.evaluate(async () => window.axe.run(document, {
    // Best-practice rules (e.g. "region", "landmark-one-main") are useful but
    // noisier and less settled than WCAG A/AA rules; scope the pass/fail gate
    // to WCAG 2.1 A/AA, which is what §23 actually requires, and still record
    // best-practice findings for the write-up.
    runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "best-practice"] },
  }));
  const wcagViolations = axeResult.violations.filter((v) => (v.tags || []).some((t) => t.startsWith("wcag2")));
  const bestPracticeOnly = axeResult.violations.filter((v) => !(v.tags || []).some((t) => t.startsWith("wcag2")));
  axeReport.push({
    tree,
    state: stateLabel,
    wcagViolationCount: wcagViolations.length,
    bestPracticeViolationCount: bestPracticeOnly.length,
    wcagViolations: wcagViolations.map((v) => ({
      id: v.id, impact: v.impact, help: v.help, nodes: v.nodes.length,
      targets: v.nodes.slice(0, 5).map((n) => n.target.join(" ")),
    })),
    bestPracticeViolations: bestPracticeOnly.map((v) => ({ id: v.id, impact: v.impact, help: v.help, nodes: v.nodes.length })),
  });
  return { violations: wcagViolations, all: axeResult.violations };
}

// In-page WCAG relative-luminance contrast, computed from the actual
// rendered `getComputedStyle` colors — a regression lock on the real DOM,
// not just the CSS source (catches e.g. an unrelated override or a browser
// default winning over the intended color).
async function contrastOf(page, selector) {
  return page.evaluate((sel) => {
    function parse(c) {
      const m = /rgba?\(([^)]+)\)/.exec(c);
      if (!m) return null;
      const parts = m[1].split(",").map((s) => parseFloat(s.trim()));
      return { r: parts[0], g: parts[1], b: parts[2], a: parts.length > 3 ? parts[3] : 1 };
    }
    function lin(v) {
      const c = v / 255;
      return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
    }
    function lum({ r, g, b }) {
      return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
    }
    // Walk up from the element to find an opaque background, compositing any
    // translucent backgrounds encountered (mirrors what a browser actually
    // paints), so a `background: transparent` element is measured against
    // what's really behind it, not treated as pure black.
    function effectiveBackground(el) {
      let node = el;
      let acc = { r: 255, g: 255, b: 255 }; // page default if nothing is opaque
      const layers = [];
      while (node) {
        const bg = parse(getComputedStyle(node).backgroundColor);
        if (bg && bg.a > 0) layers.unshift(bg);
        if (bg && bg.a >= 0.999) break;
        node = node.parentElement;
      }
      for (const layer of layers) {
        acc = {
          r: layer.r * layer.a + acc.r * (1 - layer.a),
          g: layer.g * layer.a + acc.g * (1 - layer.a),
          b: layer.b * layer.a + acc.b * (1 - layer.a),
        };
      }
      return acc;
    }
    const el = document.querySelector(sel);
    if (!el) return null;
    const fg = parse(getComputedStyle(el).color);
    const bg = effectiveBackground(el);
    if (!fg || !bg) return null;
    const l1 = lum(fg);
    const l2 = lum(bg);
    const [hi, lo] = l1 > l2 ? [l1, l2] : [l2, l1];
    return { ratio: (hi + 0.05) / (lo + 0.05), fg, bg, fontSize: getComputedStyle(el).fontSize };
  }, selector);
}

// The "Start here" card (static/atlas/js/start.js) appears on a first visit to a bare
// /atlas, and every context below is a first visit. The suite is about the Atlas,
// not the card, so contexts start with it dismissed (the card's own tests pass
// `{ welcome: true }` to see it). This is the same state a returning visitor has.
function dismissWelcomeByDefault(browserInstance) {
  const original = browserInstance.newContext.bind(browserInstance);
  browserInstance.newContext = async (options = {}) => {
    const { welcome, ...rest } = options;
    const context = await original(rest);
    if (!welcome) {
      await context.addInitScript(() => {
        try { window.localStorage.setItem("hep-atlas.start-here", "dismissed"); } catch (error) { /* no storage */ }
      });
    }
    return context;
  };
}

// The filter groups live in the Filters drawer, which is shut until the header's
// Filters button opens it (a calm first view). Phone-width pages use a sheet instead.
async function openFilters(page) {
  const button = page.locator("#filters-btn");
  if ((await button.getAttribute("aria-expanded")) !== "true") await button.click();
  await page.locator("#filters-panel.is-open").waitFor();
  // It slides in: wait until it has stopped, so a click does not land on a moving drawer.
  await page.waitForFunction(() => getComputedStyle(document.getElementById("filters-panel")).transform === "none");
}

(async () => {
  const browser = await chromium.launch({
    headless: true,
    ...(process.env.HEP_BROWSER_EXECUTABLE ? { executablePath: process.env.HEP_BROWSER_EXECUTABLE } : {}),
  });
  dismissWelcomeByDefault(browser);

  for (const tree of DATA_TREES) {
    const dataTree = tree.query;

    // ---------------------------------------------------------- axe scans
    const context = await browser.newContext({ viewport: { width: 1440, height: 960 } });
    const page = await context.newPage();

    await record(`[${tree.label}] axe: default globe view`, async () => {
      await page.goto(`${base}/atlas${dataTree}`);
      await page.waitForFunction(() => document.querySelectorAll(".atlas-marker").length > 0, { timeout: 15000 });
      await runAxe(page, tree.label, "default globe view");
    });

    await record(`[${tree.label}] axe: experiment panel`, async () => {
      await page.goto(`${base}/atlas${dataTree}#/experiment/dune`);
      await page.locator("#detail-panel h2").waitFor();
      await runAxe(page, tree.label, "experiment panel");
    });

    await record(`[${tree.label}] axe: site panel`, async () => {
      await page.goto(`${base}/atlas${dataTree}#/site/${SITE_SLUG[tree.label]}`);
      await page.locator("#detail-panel h2").waitFor();
      const { violations } = await runAxe(page, tree.label, "site panel");
      assert.deepEqual(violations, [], `expected 0 WCAG axe violations on the site panel, got ${JSON.stringify(violations)}`);
    });

    await record(`[${tree.label}] axe: collaboration mode`, async () => {
      const sep = dataTree ? `${dataTree}&m=collab` : "?m=collab";
      await page.goto(`${base}/atlas${sep}#/collaboration/dune`);
      await page.waitForFunction(() => document.querySelectorAll(".atlas-marker.tier-institution").length > 0, { timeout: 15000 });
      await runAxe(page, tree.label, "collaboration mode");
    });

    await record(`[${tree.label}] axe: filters panel (with an active filter)`, async () => {
      await page.goto(`${base}/atlas${dataTree}`);
      await page.waitForFunction(() => document.querySelectorAll(".atlas-marker").length > 0, { timeout: 15000 });
      await openFilters(page);
      const region = page.locator("#filter-region-Europe");
      await region.waitFor();
      await region.check({ force: true });
      await page.locator(".filter-chip", { hasText: "Europe" }).first().waitFor();
      await runAxe(page, tree.label, "filters drawer (open, with an active filter)");
      await page.locator("#filter-clear-all").click();
    });

    await record(`[${tree.label}] axe: Key popover (open), and Escape closes it and returns focus to its button`, async () => {
      await page.goto(`${base}/atlas${dataTree}`);
      await page.waitForFunction(() => document.querySelectorAll(".atlas-marker").length > 0, { timeout: 15000 });
      await page.locator("#key-btn").click();
      await page.locator("#key-popover").waitFor();
      assert.equal(await page.locator("#key-btn").getAttribute("aria-expanded"), "true");
      // The Key carries the status colours the timeline used to: words next to every dot.
      const keyText = await page.locator("#key-popover").innerText();
      for (const term of ["Facility shape", "Accelerator laboratory", "Active", "Upgrade", "Construction / commissioning",
        "Proposed / approved / planned", "Completed", "Uncertain (possible)", "Institution dot", "Location precision"]) {
        assert.ok(keyText.toLowerCase().includes(term.toLowerCase()), `the Key must say "${term}" in words`);
      }
      await runAxe(page, tree.label, "Key popover (open)");
      await page.keyboard.press("Escape");
      await page.locator("#key-popover").waitFor({ state: "hidden" });
      assert.equal(await page.evaluate(() => document.activeElement && document.activeElement.id), "key-btn",
        "Escape closes the Key and puts focus back on the button that opened it");
    });

    await record(`[${tree.label}] axe: timeline moved to a past year`, async () => {
      await page.goto(`${base}/atlas${dataTree}`);
      await page.waitForFunction(() => document.querySelectorAll(".atlas-marker").length > 0, { timeout: 15000 });
      await setRangeValue(page.locator("#timeline-year"), 1995);
      await page.waitForFunction(() => document.querySelector("#timeline-readout").textContent.trim() === "1995");
      await runAxe(page, tree.label, "timeline moved");
    });

    await record(`[${tree.label}] axe: results mode`, async () => {
      const sep = dataTree ? `${dataTree}&m=results` : "?m=results";
      await page.goto(`${base}/atlas${sep}`);
      await page.locator("#results-mode-list").waitFor();
      await runAxe(page, tree.label, "results mode");
    });

    await record(`[${tree.label}] axe: document library`, async () => {
      const sep = dataTree ? `${dataTree}&m=docs` : "?m=docs";
      await page.goto(`${base}/atlas${sep}`);
      await page.locator(".document-library").waitFor();
      await runAxe(page, tree.label, "document library");
    });

    // ---- views: "Beam through the Earth" (static/atlas/js/views/) ----------------
    // The figure, the table, the citations and the open "Inputs and method" must all
    // be clean: an SVG that names itself, text on the tokens' contrast, a table with
    // headers, and a disclosure that is a real <details>.
    await record(`[${tree.label}] axe: beam through the Earth view, and with Inputs and method open`, async () => {
      const viewContext = await browser.newContext({ viewport: { width: 1440, height: 960 }, reducedMotion: "reduce" });
      const viewPage = await viewContext.newPage();
      viewPage.setDefaultTimeout(30000);
      await viewPage.goto(`${base}/atlas${dataTree}#/view/beam-section/lbnf`);
      await viewPage.locator(".bs-fig-a svg.bs-svg").waitFor();
      // The citations arrive after the first paint; scan once they have.
      await viewPage.waitForFunction(() => !document.querySelector("#view-host .bs-cite .loading-note"));
      const closed = await runAxe(viewPage, tree.label, "beam section view");
      assert.deepEqual(closed.violations, [], `expected 0 WCAG axe violations on the beam section, got ${JSON.stringify(closed.violations)}`);
      await viewPage.locator("#view-method > summary").click();
      await viewPage.waitForFunction(() => !document.querySelector("#view-host .bs-sources .loading-note"));
      const open = await runAxe(viewPage, tree.label, "beam section view, inputs and method open");
      assert.deepEqual(open.violations, [], `expected 0 WCAG axe violations with the method open, got ${JSON.stringify(open.violations)}`);
      await viewContext.close();
    });

    // ---- researchers' tools (static/atlas/js/views/compare*.js, js/research/) ----------
    // The comparison table with its markers, its sources and the open method; the tray; the
    // panel's "Add to compare" and "Cite"; the export bar of the lists. All must be clean.
    await record(`[${tree.label}] axe: compare view (table, markers, sources, method open), its empty state, and the tray`, async () => {
      const compareContext = await browser.newContext({ viewport: { width: 1440, height: 960 }, reducedMotion: "reduce" });
      const comparePage = await compareContext.newPage();
      comparePage.setDefaultTimeout(30000);
      await comparePage.goto(`${base}/atlas${dataTree}#/view/compare/dune,lz,nova`);
      await comparePage.locator("table.cmp-table").waitFor();
      await comparePage.locator(".cmp-source-list li").first().waitFor();
      const closed = await runAxe(comparePage, tree.label, "compare view");
      assert.deepEqual(closed.violations, [], `expected 0 WCAG axe violations on the compare view, got ${JSON.stringify(closed.violations)}`);
      await comparePage.locator("#view-method > summary").click();
      const open = await runAxe(comparePage, tree.label, "compare view, inputs and method open");
      assert.deepEqual(open.violations, [], `expected 0 WCAG axe violations with the method open, got ${JSON.stringify(open.violations)}`);
      // The empty state, with its examples (nothing in the tray).
      await comparePage.evaluate(() => { window.sessionStorage.clear(); });
      await comparePage.goto(`${base}/atlas${dataTree}#/view/compare/x`);
      await comparePage.reload();
      await comparePage.locator(".cmp-examples").waitFor();
      const empty = await runAxe(comparePage, tree.label, "compare view, nothing chosen");
      assert.deepEqual(empty.violations, [], `expected 0 WCAG axe violations on the empty compare view, got ${JSON.stringify(empty.violations)}`);
      // The tray over the globe, and the control on the experiment panel.
      await comparePage.goto(`${base}/atlas${dataTree}#/experiment/dune`);
      await comparePage.locator("#detail-panel .compare-add").click();
      await comparePage.goto(`${base}/atlas${dataTree}#/experiment/lz`);
      await comparePage.locator("#detail-panel .compare-add").click();
      await comparePage.locator("#compare-tray .compare-chip").nth(1).waitFor();
      const tray = await runAxe(comparePage, tree.label, "experiment panel with the compare tray");
      assert.deepEqual(tray.violations, [], `expected 0 WCAG axe violations with the tray, got ${JSON.stringify(tray.violations)}`);
      await compareContext.close();
    });

    await record(`[${tree.label}] axe: result panel with Cite open, and the Results list with its export bar`, async () => {
      const citeContext = await browser.newContext({ viewport: { width: 1440, height: 960 }, reducedMotion: "reduce" });
      const citePage = await citeContext.newPage();
      citePage.setDefaultTimeout(30000);
      const slug = tree.label === "generated" ? "atlas-higgs-observation-2012" : "higgs-boson-observation-2012";
      await citePage.goto(`${base}/atlas${dataTree}#/result/${slug}`);
      await citePage.locator("#detail-panel details.panel-section > summary", { hasText: /^Cite$/ }).click();
      await citePage.locator("#detail-panel .cite-entry").waitFor();
      const cite = await runAxe(citePage, tree.label, "result panel, Cite open");
      assert.deepEqual(cite.violations, [], `expected 0 WCAG axe violations with Cite open, got ${JSON.stringify(cite.violations)}`);
      await citePage.goto(`${base}/atlas${dataTree ? `${dataTree}&m=results` : "?m=results"}`);
      await citePage.locator("#mode-panel .export-bar").waitFor();
      const lists = await runAxe(citePage, tree.label, "results list with the export bar");
      assert.deepEqual(lists.violations, [], `expected 0 WCAG axe violations on the Results list, got ${JSON.stringify(lists.violations)}`);
      await citeContext.close();
    });
    // ---- views: "Results as a story" and the WIMP exclusion plot (M4) -----------------
    // Real data only (the fixture tree has no limits bundle). The timeline with a card open and its
    // table open, and the plot with its numbers and its method open, must be clean.
    if (tree.label === "generated") {
      await record(`[${tree.label}] axe: results as a story (a card open, the table open), and the WIMP exclusion plot (numbers and method open)`, async () => {
        const viewContext = await browser.newContext({ viewport: { width: 1440, height: 960 }, reducedMotion: "reduce" });
        const viewPage = await viewContext.newPage();
        viewPage.setDefaultTimeout(30000);
        await viewPage.goto(`${base}/atlas${dataTree}#/view/results-story`);
        await viewPage.locator(".rs-mark").first().waitFor();
        await viewPage.locator('.rs-mark[data-id="result:atlas-higgs-observation-2012"]').first().click();
        await viewPage.locator(".rs-card:not([hidden])").waitFor();
        await viewPage.locator(".rs-table-details > summary").click();
        const story = await runAxe(viewPage, tree.label, "results as a story");
        assert.deepEqual(story.violations, [], `expected 0 WCAG axe violations on results as a story, got ${JSON.stringify(story.violations)}`);
        await viewPage.goto(`${base}/atlas${dataTree}#/view/limits/wimp-si`);
        await viewPage.locator(".lm-svg").waitFor();
        await viewPage.locator(".lm-data > summary").first().click();
        await viewPage.locator("#view-method > summary").click();
        const limits = await runAxe(viewPage, tree.label, "WIMP exclusion plot");
        assert.deepEqual(limits.violations, [], `expected 0 WCAG axe violations on the WIMP exclusion plot, got ${JSON.stringify(limits.violations)}`);
        await viewContext.close();
      });
    }

    // ---- views: scale comparisons ------------------------------------------------
    // The detector line-up (shapes that are links, a table, a method with quotes) and a
    // local map with a comparison overlay laid on and its section open. The generated
    // tree only: the fixtures carry neither the dimensions nor the maps.
    if (tree.label === "generated") {
      await record(`[${tree.label}] axe: detector line-up view, and with Inputs and method open`, async () => {
        const viewContext = await browser.newContext({ viewport: { width: 1440, height: 960 }, reducedMotion: "reduce" });
        const viewPage = await viewContext.newPage();
        viewPage.setDefaultTimeout(30000);
        await viewPage.goto(`${base}/atlas${dataTree}#/view/detector-scale`);
        await viewPage.locator(".ds-link").first().waitFor();
        await viewPage.locator(".ds-ice-block").waitFor();
        const closed = await runAxe(viewPage, tree.label, "detector line-up view");
        assert.deepEqual(closed.violations, [], `expected 0 WCAG axe violations on the line-up, got ${JSON.stringify(closed.violations)}`);
        await viewPage.locator("#view-method > summary").click();
        await viewPage.locator('[data-quote="detector:katrin|main_spectrometer_length"] q').waitFor();
        const open = await runAxe(viewPage, tree.label, "detector line-up view, inputs and method open");
        assert.deepEqual(open.violations, [], `expected 0 WCAG axe violations with the method open, got ${JSON.stringify(open.violations)}`);
        await viewContext.close();
      });
      await record(`[${tree.label}] axe: local map with a comparison overlay and the Compare with… section open`, async () => {
        const mapContext = await browser.newContext({ viewport: { width: 1440, height: 960 }, reducedMotion: "reduce" });
        const mapPage = await mapContext.newPage();
        mapPage.setDefaultTimeout(30000);
        await mapPage.goto(`${base}/atlas${dataTree}#/map/fermilab`);
        await mapPage.locator(".map-compare-section > summary").click();
        await mapPage.selectOption("#map-compare-select", "cern");
        await mapPage.locator(".map-cmp-line").first().waitFor();
        await mapPage.locator(".map-cmp-active").waitFor();
        const result = await runAxe(mapPage, tree.label, "local map with a comparison overlay");
        assert.deepEqual(result.violations, [], `expected 0 WCAG axe violations with an overlay, got ${JSON.stringify(result.violations)}`);
        await mapContext.close();
      });
    }
    // ---- local map view (docs/HEP_ATLAS_GEOMETRY.md §4) -- begin --------
    // Two states, both of which have to be clean: the map with nothing
    // selected, and the map with the drawer open (which is where panels.js's
    // detail panel, the shape facts, the checks and the sources all land).
    // The generated tree has no `maps` yet, so this skips explicitly rather
    // than reporting a scan it never ran.
    await record(`[${tree.label}] axe: local map view`, async () => {
      const mapTreeBase = `${base}/atlas/${dataTree ? "fixtures" : "generated"}/`;
      let maps = {};
      try {
        const response = await fetch(`${mapTreeBase}atlas.json`);
        if (response.ok) maps = (await response.json()).maps || {};
      } catch (error) {
        maps = {};
      }
      // The richest map, not the alphabetically first (which on the real
      // tree is the South Pole, with a single feature).
      const mapId = Object.keys(maps)
        .filter((id) => maps[id].feature_count > 0)
        .sort((a, b) => maps[b].feature_count - maps[a].feature_count)[0];
      if (!mapId) {
        axeReport.push({
          tree: tree.label, state: "local map view", skipped: true,
          reason: "no maps in this tree",
        });
        console.log(`SKIP [${tree.label}]: local map view — this data tree publishes no \`maps\``);
        return;
      }
      const slug = mapId.split(":")[1];
      const geometry = await (await fetch(`${mapTreeBase}${maps[mapId].bundle}`)).json();
      const mapContext = await browser.newContext({ viewport: { width: 1440, height: 960 } });
      const mapPage = await mapContext.newPage();
      mapPage.setDefaultTimeout(30000);
      await mapPage.goto(`${base}/atlas${dataTree}#/map/${slug}`, { waitUntil: "domcontentloaded" });
      await mapPage.locator(".leaflet-container").waitFor({ timeout: 20000 });
      await mapPage.locator("[data-feature-row]").first().waitFor({ timeout: 20000 });
      await runAxe(mapPage, tree.label, "local map view");

      await mapPage.locator("[data-feature-row]").first().click();
      await mapPage.locator("#map-drawer-title").waitFor({ timeout: 15000 });
      await mapPage.locator("#map-depth-toggle").click();
      await mapPage.locator(".map-depth-svg").waitFor({ timeout: 15000 });
      // Open every disclosure in the left column *after* the clicks: axe
      // cannot see into a closed <details>, and each click re-renders the
      // list (so opening them first would not survive to the scan).
      await mapPage.evaluate(() => document.querySelectorAll("#map-layers details")
        .forEach((d) => { d.open = true; }));
      await runAxe(mapPage, tree.label, "local map view, drawer and depth diagram open");

      // The four §4 encodings must each be readable as text, not colour
      // alone: the legend names them, every list row states its accuracy and
      // representation, and the map surface says how to use it without one.
      const legendText = await mapPage.locator("#map-layers").innerText();
      for (const term of ["Feature type", "Status in the selected year", "Level", "Representation"]) {
        assert.ok(legendText.includes(term), `the legend must explain "${term}" in words`);
      }
      const application = mapPage.locator("#map-canvas[role='application']");
      assert.equal(await application.count(), 1, "the map surface declares role=application");
      const label = await application.getAttribute("aria-label");
      assert.match(label, /arrow keys/i, "role=application must describe its keyboard alternative");
      assert.match(label, /listed|list/i, "…and point at the accessible list that mirrors it");
      const live = mapPage.locator("#map-selection-live");
      assert.equal(await live.getAttribute("aria-live"), "polite", "selection is announced in a live region");
      assert.match(await live.innerText(), /Selected /, "…and the live region names what was selected");

      // Contrast of the map view's own text, measured on the rendered DOM.
      for (const check of [
        { selector: ".map-feature-row .map-feature-meta", min: 4.5, label: "feature row metadata" },
        { selector: ".map-subtitle", min: 4.5, label: "map subtitle" },
        // Only maps whose record carries `notes` render this one, which on
        // the real tree is none of them — measured when present.
        { selector: ".map-data-note", min: 4.5, label: "data note", optional: true },
        { selector: ".map-drawer-title", min: 4.5, label: "drawer title" },
        { selector: ".leaflet-control-scale-line", min: 4.5, label: "scale bar label" },
      ]) {
        const measured = await contrastOf(mapPage, check.selector);
        if (!measured && check.optional) continue;
        assert.ok(measured, `could not measure contrast for ${check.label} (${check.selector})`);
        assert.ok(measured.ratio >= check.min,
          `${check.label} contrast ${measured.ratio.toFixed(2)}:1 is below ${check.min}:1`);
      }

      // Toggles are buttons with aria-pressed, not colour-only chips.
      const levelIds = (maps[mapId].levels || []).map((level) => level.id);
      for (const levelId of levelIds) {
        const pressed = await mapPage.locator(`[data-level-id="${levelId}"]`).getAttribute("aria-pressed");
        assert.ok(pressed === "true" || pressed === "false", `level toggle ${levelId} exposes aria-pressed`);
      }
      assert.ok(geometry.features.length > 0, "the bundle this scan exercised actually has features");
      console.log(`[${tree.label}] axe scanned local map ${mapId} (${geometry.features.length} features)`);
      await mapContext.close();

      // A polar map is a different projection, a different north label and a
      // disabled control, so it is its own accessible state.
      const polarId = Object.keys(maps).find((id) => Math.abs(maps[id].center.lat) > 85);
      if (!polarId) return;
      const polarContext = await browser.newContext({ viewport: { width: 1440, height: 960 } });
      const polarPage = await polarContext.newPage();
      polarPage.setDefaultTimeout(30000);
      await polarPage.goto(`${base}/atlas${dataTree}#/map/${polarId.split(":")[1]}`,
        { waitUntil: "domcontentloaded" });
      await polarPage.locator(".leaflet-container").waitFor({ timeout: 20000 });
      await polarPage.waitForTimeout(1200);
      await polarPage.evaluate(() => document.querySelectorAll("#map-layers details")
        .forEach((d) => { d.open = true; }));
      await runAxe(polarPage, tree.label, "local map view, polar projection");
      // A disabled control must still explain itself, and the grid-north
      // note must be readable text rather than an unexplained arrow.
      const disabled = polarPage.locator("#map-basemap-toggle");
      assert.equal(await disabled.getAttribute("aria-disabled"), "true");
      assert.equal(await disabled.getAttribute("aria-describedby"), "map-basemap-unavailable");
      assert.match(await polarPage.locator("#map-basemap-unavailable").innerText(), /No basemap at the pole/i);
      assert.match(await polarPage.locator(".map-north").getAttribute("aria-label"),
        /grid north/i, "the north indicator explains in words that up is grid north");
      for (const check of [
        { selector: ".map-north-label", min: 4.5, label: "grid-north label" },
        { selector: "#map-basemap-unavailable", min: 4.5, label: "no-basemap note" },
        { selector: ".map-tile-notice", min: 4.5, label: "tile notice" },
      ]) {
        const measured = await contrastOf(polarPage, check.selector);
        assert.ok(measured, `could not measure contrast for ${check.label}`);
        assert.ok(measured.ratio >= check.min,
          `${check.label} contrast ${measured.ratio.toFixed(2)}:1 is below ${check.min}:1`);
      }
      console.log(`[${tree.label}] axe scanned polar local map ${polarId}`);
      await polarContext.close();
    });
    // ---- local map view -- end -------------------------------------------

    await context.close();

    // ------------------------------------------------- no-WebGL fallback
    await record(`[${tree.label}] axe: no-WebGL fallback list`, async () => {
      const noGlContext = await browser.newContext({ viewport: { width: 1280, height: 900 } });
      const noGlPage = await noGlContext.newPage();
      await noGlPage.goto(`${base}/atlas${dataTree}`);
      // WebGL2 is not force-disabled here via launch args (that requires a
      // separate browser process, done in browser_atlas.cjs); instead this
      // reuses the same technique the app itself uses to decide: stub out
      // getContext before any script runs, so supportsWebGL2() in globe.js
      // returns false and the app renders the real fallback path.
      await noGlPage.addInitScript(() => {
        const orig = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function patched(type, ...rest) {
          if (type === "webgl2") return null;
          return orig.call(this, type, ...rest);
        };
      });
      await noGlPage.goto(`${base}/atlas${dataTree}`);
      await noGlPage.locator(".fallback-notice").waitFor({ timeout: 15000 });
      await runAxe(noGlPage, tree.label, "no-WebGL fallback list");
      await noGlContext.close();
    });

    // ----------------------------------------------- keyboard traversal
    await record(`[${tree.label}] keyboard: search -> result -> panel -> sources -> Escape -> focus returns to search`, async () => {
      const kbContext = await browser.newContext({ viewport: { width: 1440, height: 960 } });
      const kbPage = await kbContext.newPage();
      await kbPage.goto(`${base}/atlas${dataTree}`);
      await kbPage.waitForFunction(() => document.querySelectorAll(".atlas-marker").length > 0, { timeout: 15000 });

      await kbPage.locator("#atlas-search").focus();
      await kbPage.keyboard.type("DUNE");
      await kbPage.locator(".search-result").first().waitFor();
      // The first option is already active (aria-activedescendant), so Enter
      // opens the best match without an arrow key first.
      await kbPage.keyboard.press("Enter");
      await kbPage.locator("#detail-panel h2").waitFor();

      // The panel's own heading takes focus on open (existing behaviour) —
      // confirm that, then reach the Sources disclosure purely by keyboard
      // and open it with Enter (native <details> semantics).
      const focusedIsHeading = await kbPage.evaluate(() => document.activeElement
        && document.activeElement.tagName === "H2" && document.activeElement.closest("#detail-panel") != null);
      assert.equal(focusedIsHeading, true, "opening a panel from a keyboard-selected search result must focus its heading");

      const sourcesSummary = kbPage.locator("#detail-panel details.panel-section summary", { hasText: "Sources" });
      await sourcesSummary.waitFor();
      await sourcesSummary.focus();
      await kbPage.keyboard.press("Enter");
      await kbPage.waitForFunction(() => {
        const summaries = [...document.querySelectorAll("#detail-panel details.panel-section summary")];
        const details = summaries.find((s) => s.textContent.trim() === "Sources")?.closest("details");
        return !!details && details.open && ["loaded", "error"].includes(details.dataset.state);
      }, { timeout: 10000 });

      // Escape closes the panel and returns focus to the search input — the
      // element that was focused when this entity was opened (§23 "focus
      // returning to the trigger").
      await kbPage.keyboard.press("Escape");
      await kbPage.waitForFunction(() => document.getElementById("detail-panel").classList.contains("hidden"));
      const focusedId = await kbPage.evaluate(() => document.activeElement && document.activeElement.id);
      assert.equal(focusedId, "atlas-search", `expected focus back on #atlas-search after Escape, got "${focusedId}"`);
      await kbContext.close();
    });

    await record(`[${tree.label}] keyboard: timeline slider announces the year via a live region`, async () => {
      const kbContext = await browser.newContext({ viewport: { width: 1440, height: 960 } });
      const kbPage = await kbContext.newPage();
      await kbPage.goto(`${base}/atlas${dataTree}`);
      await kbPage.waitForFunction(() => document.querySelectorAll(".atlas-marker").length > 0, { timeout: 15000 });

      const readoutRole = await kbPage.locator("#timeline-readout").getAttribute("aria-live");
      assert.equal(readoutRole, "polite", "the timeline readout must be a polite live region");

      const before = await kbPage.locator("#timeline-readout").innerText();
      await kbPage.locator("#timeline-year").focus();
      // Native <input type=range> keyboard operation, no custom key handling
      // needed — ArrowLeft decrements.
      for (let i = 0; i < 5; i += 1) await kbPage.keyboard.press("ArrowLeft");
      await kbPage.waitForFunction(
        (prev) => document.getElementById("timeline-readout").innerText !== prev,
        before,
      );
      const after = await kbPage.locator("#timeline-readout").innerText();
      assert.notEqual(after, before, "moving the timeline slider by keyboard must update the live-region readout");
      await kbContext.close();
    });

    await record(`[${tree.label}] keyboard: a filter checkbox is operable by keyboard and announces a chip`, async () => {
      const kbContext = await browser.newContext({ viewport: { width: 1440, height: 960 } });
      const kbPage = await kbContext.newPage();
      await kbPage.goto(`${base}/atlas${dataTree}`);
      await kbPage.waitForFunction(() => document.querySelectorAll(".atlas-marker").length > 0, { timeout: 15000 });

      const chipsLive = await kbPage.locator(".filter-chips").getAttribute("aria-live");
      assert.equal(chipsLive, "polite", "the active-filters chip row must be a polite live region");

      // Keyboard route to the drawer: the header's Filters button, Enter, and focus
      // lands in the drawer.
      await kbPage.locator("#filters-btn").focus();
      await kbPage.keyboard.press("Enter");
      await kbPage.locator("#filters-panel.is-open").waitFor();
      const drawerHasFocus = await kbPage.evaluate(() => document.getElementById("filters-panel").contains(document.activeElement));
      assert.equal(drawerHasFocus, true, "opening the Filters drawer from the keyboard must move focus into it");
      await kbPage.locator("#filter-region-Europe").focus();
      await kbPage.keyboard.press("Space");
      await kbPage.locator(".filter-chip", { hasText: "Europe" }).first().waitFor();
      assert.equal(await kbPage.locator("#filter-region-Europe").isChecked(), true, "Space must toggle a focused filter checkbox");
      // The re-render that follows a toggle must not steal keyboard focus —
      // filters.js explicitly re-finds and refocuses the same control id.
      const stillFocused = await kbPage.evaluate(() => document.activeElement && document.activeElement.id);
      assert.equal(stillFocused, "filter-region-Europe", "toggling a filter must not drop keyboard focus off the checkbox");
      await kbContext.close();
    });

    await record(`[${tree.label}] keyboard: Escape closes the mode panel and returns focus to its trigger button`, async () => {
      const kbContext = await browser.newContext({ viewport: { width: 1440, height: 960 } });
      const kbPage = await kbContext.newPage();
      await kbPage.goto(`${base}/atlas${dataTree}`);
      await kbPage.waitForFunction(() => document.querySelectorAll(".atlas-marker").length > 0, { timeout: 15000 });

      const topicsBtn = kbPage.locator('.mode-toggle[data-mode="topic"]');
      await topicsBtn.focus();
      await kbPage.keyboard.press("Enter");
      await kbPage.locator("#mode-panel .topic-tree").waitFor();
      await kbPage.keyboard.press("Escape");
      await kbPage.waitForFunction(() => document.getElementById("mode-panel").classList.contains("hidden"));
      const focusedId = await kbPage.evaluate(() => {
        const el = document.activeElement;
        return el && (el.dataset ? el.dataset.mode : null);
      });
      assert.equal(focusedId, "topic", "Escape must return focus to the mode button that opened the panel");
      await kbContext.close();
    });

    // ------------------------------------------------------ reduced motion
    await record(`[${tree.label}] prefers-reduced-motion: no idle globe rotation`, async () => {
      const rmContext = await browser.newContext({ viewport: { width: 1280, height: 900 }, reducedMotion: "reduce" });
      const rmPage = await rmContext.newPage();
      await rmPage.goto(`${base}/atlas${dataTree}`);
      await rmPage.waitForFunction(() => document.querySelectorAll(".atlas-marker").length > 0, { timeout: 15000 });
      const firstMarker = rmPage.locator(".atlas-marker").first();
      const before = await firstMarker.boundingBox();
      await rmPage.waitForTimeout(2000);
      const after = await firstMarker.boundingBox();
      const drift = before && after ? Math.hypot(after.x - before.x, after.y - before.y) : null;
      assert.ok(drift != null && drift < 1, `expected no idle marker drift under prefers-reduced-motion, measured ${drift}px`);
      await rmContext.close();
    });

    // -------------------------------------------------------- contrast lock-in
    await record(`[${tree.label}] contrast: representative text/background pairs meet WCAG AA`, async () => {
      const cContext = await browser.newContext({ viewport: { width: 1440, height: 960 } });
      const cPage = await cContext.newPage();
      await cPage.goto(`${base}/atlas${dataTree}#/experiment/dune`);
      await cPage.locator("#detail-panel h2").waitFor();
      const checks = [
        { selector: "#detail-panel .panel-subtitle", min: 4.5, label: "panel subtitle (muted text)" },
        { selector: "#detail-panel .kv-list dt", min: 4.5, label: "key-spec label (muted text)" },
        { selector: "#data-version-label", min: 4.5, label: "footer data-version label (muted text)" },
        { selector: "#atlas-search", min: 4.5, label: "search input text" },
      ];
      for (const check of checks) {
        const measured = await contrastOf(cPage, check.selector);
        assert.ok(measured, `could not measure contrast for ${check.label} (${check.selector})`);
        assert.ok(
          measured.ratio >= check.min,
          `${check.label} contrast ${measured.ratio.toFixed(2)}:1 is below ${check.min}:1 (fg ${JSON.stringify(measured.fg)}, bg ${JSON.stringify(measured.bg)})`,
        );
      }
      await cContext.close();
    });

    await record(`[${tree.label}] non-colour-only encoding: an "uncertain" marker hatches and names it in the accessible label`, async () => {
      const ncContext = await browser.newContext({ viewport: { width: 1440, height: 960 } });
      const ncPage = await ncContext.newPage();
      await ncPage.goto(`${base}/atlas${dataTree}`);
      await ncPage.waitForFunction(() => document.querySelectorAll(".atlas-marker").length > 0, { timeout: 15000 });
      // The default (current-year) view has no "possible"-certainty facility
      // segments in either bundle — 2015 does in the generated tree (checked
      // directly against static/atlas/generated/atlas.json), so move the
      // timeline there to actually exercise this path instead of trivially
      // skipping every run.
      await setRangeValue(ncPage.locator("#timeline-year"), 2015);
      await ncPage.waitForFunction(() => document.getElementById("timeline-readout").textContent.trim() === "2015");
      const hasUncertainMarker = await ncPage.evaluate(() => {
        const marker = document.querySelector(".atlas-marker.is-possible");
        if (!marker) return null;
        const label = marker.getAttribute("aria-label") || "";
        const hasPattern = !!marker.querySelector("svg pattern");
        return { label, hasPattern };
      });
      if (hasUncertainMarker == null) {
        console.log(`SKIP [${tree.label}]: no marker with is-possible (uncertain) certainty at the default view/year in this bundle`);
        return;
      }
      assert.match(hasUncertainMarker.label, /uncertain/i, "an uncertain-certainty marker must say so in its accessible name, not rely on the hatch pattern alone");
      assert.equal(hasUncertainMarker.hasPattern, true, "an uncertain-certainty marker must render a hatch pattern (not just a class with no visual effect)");
      await ncContext.close();
    });
  }

  // ---- the Start-here card (first visit to a bare /atlas): scanned open, once. It
  // only opens on the generated bundle's address, so it is not part of the tree loop.
  {
    const startContext = await browser.newContext({ viewport: { width: 1440, height: 960 }, welcome: true });
    const startPage = await startContext.newPage();
    await record("axe: Start here card (first visit), keyboard order, and dismissal", async () => {
      await startPage.goto(`${base}/atlas`);
      await startPage.locator("#start-card").waitFor({ timeout: 30000 });
      await runAxe(startPage, "generated", "Start here card");
      // Tab order inside the card: close, four questions, then the three entries.
      const order = await startPage.evaluate(() => {
        const card = document.getElementById("start-card");
        return [...card.querySelectorAll("button, a[href]")].map((el) => el.textContent.trim() || el.getAttribute("aria-label"));
      });
      assert.equal(order[0], "\u00d7", "the close button is the first control in the card");
      assert.equal(order.length, 8, `one close, four questions, three entries: ${JSON.stringify(order)}`);
      await startPage.keyboard.press("Tab");
      const inside = await startPage.evaluate(() => document.getElementById("start-card").contains(document.activeElement));
      assert.equal(inside, true, "Tab from the card's own focus stop goes to its first control");
      await startPage.keyboard.press("Escape");
      await startPage.waitForFunction(() => document.getElementById("start-card").hidden);
      // Contrast of the card's own text, measured on the rendered page.
      await startPage.locator("#start-here-link").click();
      for (const selector of [".start-lede", ".start-question-text", ".start-question-hint", ".start-kicker", ".start-heading"]) {
        const measured = await contrastOf(startPage, `#start-card ${selector}`);
        assert.ok(measured && measured.ratio >= 4.5, `${selector} contrast ${measured && measured.ratio.toFixed(2)}:1 is below 4.5:1`);
      }
    });
    await startContext.close();
  }

  // ---- about.html: one axe scan, after its live coverage numbers render
  // (not just the "Loading…" status), so the scan covers the real rendered
  // tables the same way the globe-view scans above wait for markers first.
  // One state is enough here: unlike the globe, about.html's structure does
  // not vary by data tree or route — only the numbers inside the tables do.
  {
    const aboutContext = await browser.newContext({ viewport: { width: 1280, height: 960 } });
    const aboutPage = await aboutContext.newPage();
    await record("axe: about.html (methodology/coverage page)", async () => {
      await aboutPage.goto(`${base}/atlas/about.html`);
      await aboutPage.locator("#coverage-entities table").waitFor({ timeout: 15000 });
      await runAxe(aboutPage, "about", "about.html");
    });
    await aboutContext.close();
  }

  await browser.close();

  // Wrapped in an object, not a bare array: scripts/atlas_validation_counts.py's
  // load_browser_results() globs every *.json under test-results/atlas/ and
  // calls `.get('checks')` on each parsed payload — a bare top-level array
  // has no `.get` and crashes it. `checks` is intentionally absent here (this
  // file isn't a pass/fail check report, a11y-report.json already is one) so
  // that loader's `payload.get('checks') or []` degrades to an empty list.
  fs.writeFileSync(path.join(output, "a11y-axe-report.json"), JSON.stringify({ axe_states: axeReport }, null, 2));
  fs.writeFileSync(path.join(output, "a11y-report.json"), JSON.stringify({
    checked_at: new Date().toISOString(),
    axe_source: AXE_PATH,
    checks: results,
    status: failed ? "failed" : "passed",
  }, null, 2));

  const totalWcagViolations = axeReport.reduce((sum, r) => sum + (r.wcagViolationCount || 0), 0);
  console.log(JSON.stringify({
    passed: results.filter((r) => r.status === "passed").length,
    failed: results.filter((r) => r.status === "failed").length,
    totalWcagAxeViolations: totalWcagViolations,
    axeStatesScanned: axeReport.filter((r) => !r.skipped).length,
  }));

  if (failed) process.exit(1);
})().catch((error) => {
  console.error(error);
  fs.writeFileSync(path.join(output, "a11y-report.json"), JSON.stringify({
    status: "failed", checks: results, error: String(error),
  }, null, 2));
  process.exit(1);
});
