/* HEP Atlas classroom modes, in a real browser: projector theme, embed mode, the glossary
   popover and the plain/technical summary toggle. Same environment as
   tests/browser_atlas.cjs:

     NODE_PATH=<dir with playwright> HEP_URL=http://localhost:8863 HEP_ATLAS_DATA=generated \
       HEP_BROWSER=chromium|firefox|webkit node tests/browser_atlas_classroom.cjs

   The glossary only exists in the generated bundles, so run it with HEP_ATLAS_DATA=generated
   (the glossary checks are skipped, and say so, against the fixtures). */
const playwright = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const BROWSER_NAME = (process.env.HEP_BROWSER || "chromium").toLowerCase();
const ENGINES = { chromium: playwright.chromium, firefox: playwright.firefox, webkit: playwright.webkit };
if (!ENGINES[BROWSER_NAME]) throw new Error(`Unknown HEP_BROWSER "${BROWSER_NAME}"`);
const engine = ENGINES[BROWSER_NAME];
const MOBILE = BROWSER_NAME === "firefox" ? { hasTouch: true } : { isMobile: true, hasTouch: true };
const GENERATED = process.env.HEP_ATLAS_DATA === "generated";
const base = process.env.HEP_URL || "http://127.0.0.1:8790";
const dataTree = GENERATED ? "" : "?data=fixtures";
const output = process.env.HEP_ATLAS_OUTPUT || path.join(__dirname, "../test-results/atlas");
fs.mkdirSync(output, { recursive: true });

const results = [];
const errors = [];
let browser;

let currentTest = "";
const record = async (name, fn) => {
  const start = Date.now();
  currentTest = name;
  await fn();
  results.push({ name, status: "passed", milliseconds: Date.now() - start });
  console.log("PASS", name);
};
const skip = (name, why) => {
  results.push({ name, status: "skipped", reason: why });
  console.log("SKIP", name, "-", why);
};

function launchOptions() {
  const opts = { headless: true };
  if (BROWSER_NAME === "chromium" && process.env.HEP_BROWSER_EXECUTABLE) opts.executablePath = process.env.HEP_BROWSER_EXECUTABLE;
  return opts;
}

// Every context starts as a returning visitor (no Start-here card) with clean storage.
async function newContext(options = {}) {
  const context = await browser.newContext({ reducedMotion: "reduce", ...options });
  context.setDefaultTimeout(45000);
  await context.addInitScript(() => {
    try {
      if (!window.sessionStorage.getItem("classroom-test-initialised")) {
        window.sessionStorage.setItem("classroom-test-initialised", "1");
        window.localStorage.setItem("hep-atlas.start-here", "dismissed");
      }
    } catch (error) { /* no storage */ }
  });
  context.on("page", (p) => p.on("pageerror", (e) => errors.push(`${currentTest}: ${e.message}`)));
  context.on("page", (p) => p.on("console", (msg) => {
    if (msg.type() !== "error") return;
    // The browser's own report of the frames the iframe test asks to be refused: that is the
    // result being asserted there (the HEP Graph app and the API send frame-ancestors 'none').
    if (/Framing '.*' violates .*frame-ancestors 'none'/.test(msg.text())) return;
    errors.push(`${currentTest}: console.error: ${msg.text()}`);
  }));
  return context;
}

// `spec` is the part after /atlas: "?embed=1#/experiment/t2k", "#/map/fermilab" or "".
// The data-tree query (fixtures, when asked) is merged in front of the spec's own.
const url = (spec = "") => {
  const at = spec.indexOf("#");
  const hash = at >= 0 ? spec.slice(at) : "";
  const query = (at >= 0 ? spec.slice(0, at) : spec).replace(/^\?/, "");
  const params = [dataTree.replace(/^\?/, ""), query].filter(Boolean).join("&");
  return `${base}/atlas${params ? `?${params}` : ""}${hash}`;
};

// axe-core, when a copy can be found (the a11y suite's lookup), injected through a
// same-origin route because the page's CSP forbids inline scripts.
function findAxe() {
  const candidates = (process.env.NODE_PATH || "").split(path.delimiter).map((dir) => path.join(dir, "axe-core", "axe.min.js"));
  candidates.push("/Users/yatharthsirohi/Desktop/ourIowaCityWebsite/our-iowa-city/node_modules/axe-core/axe.min.js");
  try { candidates.push(require.resolve("axe-core/axe.min.js")); } catch (error) { /* not on the module path */ }
  return candidates.find((candidate) => candidate && fs.existsSync(candidate)) || null;
}
const AXE_PATH = findAxe();
async function axeViolations(page, ruleSet) {
  if (!page.__axeRouted) {
    await page.route("**/__axe-core-test-only__.js", (route) => route.fulfill({
      status: 200, contentType: "application/javascript", body: fs.readFileSync(AXE_PATH, "utf8"),
    }));
    page.__axeRouted = true;
  }
  if (!(await page.evaluate(() => !!window.axe))) await page.addScriptTag({ url: "/__axe-core-test-only__.js" });
  const result = await page.evaluate((runOnly) => window.axe.run(document, { runOnly }), ruleSet);
  return result.violations.map((v) => `${v.id} (${v.impact}): ${v.nodes.slice(0, 4).map((n) => n.target.join(" ")).join(" | ")}`);
}
const WCAG_AA = { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"] };
const WCAG_AAA_CONTRAST = { type: "rule", values: ["color-contrast-enhanced"] };

// WCAG contrast from computed colours, found the way a person sees them: the first
// ancestor with an opaque background is what the text sits on.
async function contrastOf(page, selector) {
  return page.locator(selector).first().evaluate((el) => {
    const parse = (value) => {
      const m = /rgba?\(([^)]+)\)/.exec(value);
      if (!m) return null;
      const [r, g, b, a = 1] = m[1].split(/[ ,/]+/).filter(Boolean).map(Number);
      return { r, g, b, a };
    };
    const lin = (c) => { const v = c / 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
    const lum = ({ r, g, b }) => 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
    let background = null;
    for (let node = el; node && !background; node = node.parentElement) {
      const bg = parse(getComputedStyle(node).backgroundColor);
      if (bg && bg.a > 0.95) background = bg;
    }
    background = background || { r: 255, g: 255, b: 255 };
    const fg = parse(getComputedStyle(el).color);
    const [hi, lo] = [lum(fg), lum(background)].sort((a, b) => b - a);
    return (hi + 0.05) / (lo + 0.05);
  });
}

const rootTheme = (page) => page.evaluate(() => document.documentElement.getAttribute("data-theme"));
const stored = (page, key) => page.evaluate((k) => { try { return window.localStorage.getItem(k); } catch (e) { return "no-storage"; } }, key);

async function waitForPanel(page, heading) {
  await page.locator("#detail-panel h2").waitFor();
  if (heading) await page.waitForFunction((h) => (document.querySelector("#detail-panel h2") || {}).textContent.includes(h), heading);
}

(async () => {
  browser = await engine.launch(launchOptions());

  // ------------------------------------------------------------ projector mode
  await record("Projector theme: ?theme=projector applies it, the header toggle is labelled and keyboard-operable, and the choice is remembered", async () => {
    const context = await newContext({ viewport: { width: 1440, height: 900 } });
    const page = await context.newPage();
    await page.goto(url("?theme=projector"));
    await page.locator("#theme-btn").waitFor();
    assert.equal(await rootTheme(page), "projector", "?theme=projector sets the theme before anything else runs");
    const button = page.locator("#theme-btn");
    assert.equal(await button.getAttribute("aria-pressed"), "true");
    assert.equal(await button.getAttribute("aria-label"), "Projector mode");
    assert.match(await button.innerText(), /Projector/);
    assert.equal(await stored(page, "hep-atlas.theme"), null, "a link's theme is not written to storage");

    // Light, large, thick: computed from the page itself.
    const look = await page.evaluate(() => {
      const css = getComputedStyle(document.documentElement);
      return {
        paper: getComputedStyle(document.body).backgroundColor,
        text: getComputedStyle(document.body).color,
        small: parseFloat(getComputedStyle(document.querySelector(".tool-btn")).fontSize),
        beam: css.getPropertyValue("--beam-stroke-scale").trim(),
        caption: css.getPropertyValue("--marker-label-size").trim(),
        borders: getComputedStyle(document.getElementById("atlas-search")).borderTopWidth,
      };
    });
    assert.equal(look.paper, "rgb(255, 255, 255)");
    assert.equal(look.text, "rgb(10, 20, 28)");
    assert.ok(look.small >= 15.5, `header controls are ~16px in projector mode (got ${look.small})`);
    assert.equal(look.beam, "1.5");
    assert.equal(look.caption, "16px");
    assert.equal(look.borders, "2px");
    for (const selector of [".atlas-title", ".tool-btn", "#data-version-label", ".footer-link"]) {
      const ratio = await contrastOf(page, selector);
      assert.ok(ratio >= 7, `${selector} is ${ratio.toFixed(2)}:1 in projector mode; body text needs 7:1`);
    }
    await page.waitForFunction(() => document.querySelectorAll(".atlas-marker").length > 0);
    // The globe's Earth image stays dark: its stage background is not the light page colour.
    const stage = await page.locator("#globe-stage").evaluate((el) => getComputedStyle(el).backgroundImage);
    assert.match(stage, /gradient/, "the stage keeps its dark gradient");

    // Keyboard: focus it, press Space, and the standard theme returns; Enter brings it back.
    await button.focus();
    await page.keyboard.press("Space");
    assert.equal(await rootTheme(page), null);
    assert.equal(await button.getAttribute("aria-pressed"), "false");
    assert.equal(await stored(page, "hep-atlas.theme"), "standard");
    assert.match(page.url(), /theme=standard/, "the address carries the choice so a shared link does too");
    await page.keyboard.press("Enter");
    assert.equal(await rootTheme(page), "projector");
    assert.equal(await stored(page, "hep-atlas.theme"), "projector");

    // Remembered: a bare address opens in projector mode; a link's own ?theme= wins over it.
    await page.goto(url());
    await page.locator("#theme-btn").waitFor();
    assert.equal(await rootTheme(page), "projector", "the remembered choice applies on a later visit");
    // Let the app finish loading before leaving the page: an aborted fetch is a console error.
    await page.waitForFunction(() => document.querySelectorAll(".atlas-marker").length > 0);
    await page.goto(url("?theme=standard"));
    await page.locator("#theme-btn").waitFor();
    assert.equal(await rootTheme(page), null, "?theme=standard beats the remembered projector choice");
    assert.equal(await stored(page, "hep-atlas.theme"), "projector", "and does not overwrite it");
    await context.close();
  });

  await record("Projector theme on a phone: the toggle is in the Views & filters sheet, and a record stays readable", async () => {
    const context = await newContext({ viewport: { width: 390, height: 844 }, ...MOBILE });
    const page = await context.newPage();
    await page.goto(url());
    await page.locator("#phone-filters-btn").waitFor();
    assert.equal(await page.locator(".header-tools").isVisible(), false, "the laptop header tools are not shown on a phone");
    await page.locator("#phone-filters-btn").click();
    await page.locator("#filters-panel.is-open").waitFor();
    const inSheet = page.locator("#phone-display-section #theme-btn");
    await inSheet.scrollIntoViewIfNeeded();
    assert.equal(await inSheet.count(), 1, "the projector toggle moves into the sheet's Display section");
    await inSheet.click();
    assert.equal(await rootTheme(page), "projector");
    assert.equal(await inSheet.getAttribute("aria-pressed"), "true");
    await page.goto(url("?theme=projector#/experiment/k2k"));
    await waitForPanel(page, "K2K");
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    assert.ok(overflow <= 1, `no horizontal page scroll in projector mode on a phone (${overflow}px over)`);
    assert.ok(await contrastOf(page, "#detail-panel .plain-summary") >= 7);
    await context.close();
  });

  if (!AXE_PATH) {
    skip("Projector mode: axe finds no WCAG A/AA violation and no failing 7:1 text contrast", "axe-core was not found on NODE_PATH");
  } else {
    await record("Projector mode: axe finds no WCAG A/AA violation and no failing 7:1 text contrast (globe, record with an open definition, embed)", async () => {
      const context = await newContext({ viewport: { width: 1440, height: 900 } });
      const page = await context.newPage();
      const scan = async (label) => {
        const aa = await axeViolations(page, WCAG_AA);
        assert.deepEqual(aa, [], `${label}: WCAG 2.x A/AA violations`);
        const enhanced = await axeViolations(page, WCAG_AAA_CONTRAST);
        assert.deepEqual(enhanced, [], `${label}: text under 7:1`);
      };
      await page.goto(url("?theme=projector"));
      await page.waitForFunction(() => document.querySelectorAll(".atlas-marker").length > 0);
      await scan("globe");
      await page.locator("#key-btn").click();
      await page.locator("#key-popover:not([hidden])").waitFor();
      await scan("Key popover");
      await page.keyboard.press("Escape");
      await page.goto(url("?theme=projector#/experiment/k2k"));
      await waitForPanel(page, "K2K");
      if (GENERATED) {
        await page.locator("#detail-panel .gloss-term").first().click();
        await page.locator("#gloss-pop").waitFor({ state: "visible" });
      }
      await scan("record with a definition open");
      await page.goto(url("?embed=1&theme=projector#/experiment/t2k"));
      await waitForPanel(page, "T2K");
      await scan("embed");
      await context.close();
    });
  }

  // ---------------------------------------------------------------- embed mode
  await record("Embed mode: ?embed=1 hides the search, view switcher, filters, footer links and timeline, keeps a one-line partial-coverage note, and offers Open in HEP Atlas", async () => {
    const context = await newContext({ viewport: { width: 1280, height: 800 } });
    const page = await context.newPage();
    await page.goto(url("?embed=1#/experiment/t2k"));
    await waitForPanel(page, "T2K");
    assert.equal(await page.evaluate(() => document.documentElement.classList.contains("is-embed")), true);
    for (const selector of [".search-wrap", "#mode-buttons", "#filters-btn", "#theme-btn", ".timeline-bar", "#start-card",
      "#start-here-link", "#share-link", ".atlas-footer .data-version-label", '.atlas-footer a[href$="about.html"]']) {
      assert.equal(await page.locator(selector).isVisible(), false, `${selector} is hidden in embed mode`);
    }
    // The footer goes, but not its honesty: coverage is partial, in one line, linking out of the frame.
    const coverage = page.locator(".atlas-footer .footer-coverage");
    assert.equal(await coverage.isVisible(), true, "the partial-coverage note stays in embed mode");
    assert.match(await coverage.innerText(), /coverage: partial/i);
    assert.equal(await coverage.getAttribute("target"), "_blank", "the coverage report opens beside the frame, not inside it");
    const footerHeight = await page.locator(".atlas-footer").evaluate((el) => el.getBoundingClientRect().height);
    assert.ok(footerHeight > 0 && footerHeight < 40, `one line, not a footer: ${footerHeight}px`);
    for (const selector of ["#embed-open", ".atlas-title", "#key-btn", "#globe-stage", "#detail-panel"]) {
      assert.equal(await page.locator(selector).isVisible(), true, `${selector} stays in embed mode`);
    }
    const href = await page.locator("#embed-open").getAttribute("href");
    const target = new URL(href, base);
    assert.equal(target.pathname.replace(/\/$/, ""), "/atlas");
    assert.equal(target.searchParams.has("embed"), false, "the full-size link drops embed");
    assert.equal(target.hash, "#/experiment/t2k", "and keeps the view");
    assert.equal(await page.locator("#embed-open").getAttribute("target"), "_blank");
    assert.match(page.url(), /embed=1/, "the address keeps embed=1 through navigation");
    // Navigating inside the embed keeps it, and the link follows the view.
    await page.evaluate(() => { window.location.hash = "#/experiment/dune"; });
    await page.waitForFunction(() => (document.querySelector("#embed-open") || {}).href.includes("experiment/dune"));
    assert.match(page.url(), /embed=1/);
    await context.close();

    // The timeline stays only for a route that needs it: a year in the address, or a map.
    const timeline = await newContext({ viewport: { width: 1280, height: 800 } });
    const tpage = await timeline.newPage();
    await tpage.goto(url("?embed=1&y=2005"));
    await tpage.locator("#timeline-bar").waitFor({ state: "attached" });
    await tpage.waitForFunction(() => document.querySelectorAll(".atlas-marker").length > 0);
    assert.equal(await tpage.locator(".timeline-bar").isVisible(), true, "a link that names a year keeps the timeline");
    await tpage.goto(url("?embed=1#/map/fermilab"));
    await tpage.waitForSelector("body.is-map-route");
    assert.equal(await tpage.locator(".timeline-bar").isVisible(), true, "a local map keeps the timeline");
    await tpage.goto(url("?embed=1"));
    await tpage.waitForFunction(() => document.querySelectorAll(".atlas-marker").length > 0);
    assert.equal(await tpage.locator(".timeline-bar").isVisible(), false, "the bare globe does not");
    await timeline.close();
  });

  await record("Embed mode in an iframe: the Atlas may be framed, the HEP Graph app and the API may not", async () => {
    const context = await newContext({ viewport: { width: 1000, height: 700 } });
    const page = await context.newPage();
    // A page on another origin that frames the atlas: a throwaway server on a free
    // loopback port (a different origin from the atlas, and both are local, so Chromium's
    // public-page-to-local-network rule, which has nothing to do with the atlas's own
    // headers, does not apply).
    const http = require("node:http");
    const course = http.createServer((req, res) => {
      res.setHeader("content-type", "text/html");
      res.end(`<!doctype html><title>Course page</title><h1>Week 7</h1>
        <iframe id="atlas" title="Atlas" src="${base}/atlas?embed=1" width="900" height="560"></iframe>
        <iframe id="app" title="App" src="${base}/" width="400" height="200"></iframe>
        <iframe id="api" title="API" src="${base}/api/health" width="400" height="100"></iframe>`);
    });
    await new Promise((resolve) => course.listen(0, "127.0.0.1", resolve));
    try {
      await page.goto(`http://127.0.0.1:${course.address().port}/week7.html`);
      const atlas = page.frameLocator("#atlas");
      await atlas.locator("#embed-open").waitFor({ timeout: 30000 });
      await atlas.locator(".atlas-marker").first().waitFor({ timeout: 30000 });
      assert.equal(await atlas.locator(".search-wrap").isVisible(), false);
      // The HEP Graph app and the API refuse to be framed: nothing of them shows.
      await page.waitForTimeout(1500);
      for (const id of ["app", "api"]) {
        const handle = await page.locator(`#${id}`).elementHandle();
        const inner = await handle.contentFrame();
        const text = inner ? await inner.evaluate(() => (document.body ? document.body.innerText : "")).catch(() => "") : "";
        assert.ok(!/service_version|HEP Graph|Find a route/i.test(text), `#${id} must not render inside a frame (got ${JSON.stringify(text.slice(0, 80))})`);
      }
    } finally {
      course.close();
    }
    await context.close();
  });

  // ------------------------------------------------------------------ glossary
  if (!GENERATED) {
    skip("Glossary popover opens and closes with the keyboard", "the fixtures have no glossary; run with HEP_ATLAS_DATA=generated");
  } else {
    await record("Glossary popover: a term opens with the keyboard, shifts nothing, shows its source, and Escape closes it", async () => {
      const context = await newContext({ viewport: { width: 1440, height: 900 } });
      const page = await context.newPage();
      await page.goto(url("#/experiment/k2k"));
      await waitForPanel(page, "K2K");
      const term = page.locator('#detail-panel .gloss-term[data-gloss="baseline"]');
      await term.waitFor({ timeout: 15000 });
      assert.equal(await page.locator('#detail-panel .gloss-term[data-gloss="baseline"]').count(), 1, "only the first use of a term is marked");
      assert.equal(await term.evaluate((el) => el.tagName), "BUTTON", "a real button");
      assert.equal(await term.getAttribute("aria-haspopup"), "dialog");
      assert.equal(await term.getAttribute("aria-expanded"), "false");
      assert.match(await term.getAttribute("aria-label"), /^baseline, definition$/);
      const decoration = await term.evaluate((el) => getComputedStyle(el).textDecorationLine + " " + getComputedStyle(el).textDecorationStyle);
      assert.match(decoration, /underline dotted/);

      const paragraph = page.locator("#detail-panel .plain-summary");
      const before = await paragraph.boundingBox();
      const panelBefore = await page.locator("#detail-panel").evaluate((el) => el.scrollHeight);
      await term.focus();
      await page.keyboard.press("Enter");
      const popover = page.locator("#gloss-pop");
      await popover.waitFor({ state: "visible" });
      assert.equal(await term.getAttribute("aria-expanded"), "true");
      assert.equal(await popover.getAttribute("role"), "dialog");
      assert.equal(await page.evaluate(() => document.activeElement && document.activeElement.id), "gloss-pop", "focus moves into the popover");
      assert.match(await popover.locator(".gloss-pop-title").innerText(), /Baseline/);
      assert.match(await popover.locator(".gloss-pop-def").innerText(), /distance a neutrino beam travels/);
      const link = popover.locator(".gloss-pop-source a");
      assert.match(await link.getAttribute("href"), /^https:\/\/pdg\.lbl\.gov\//);
      assert.equal(await link.getAttribute("rel"), "noopener");
      assert.match(await popover.locator("blockquote").evaluate((el) => el.textContent), /K2K was the first long-baseline experiment/);
      // No layout shift: the text and the panel are exactly where they were.
      const after = await paragraph.boundingBox();
      assert.deepEqual(after, before, "opening the popover moves no text");
      assert.equal(await page.locator("#detail-panel").evaluate((el) => el.scrollHeight), panelBefore);
      const box = await popover.boundingBox();
      const viewport = page.viewportSize();
      assert.ok(box.x >= 0 && box.y >= 0 && box.x + box.width <= viewport.width && box.y + box.height <= viewport.height, "the popover is inside the viewport");

      // Escape closes the popover (not the record behind it) and returns focus to the term.
      await page.keyboard.press("Escape");
      await popover.waitFor({ state: "hidden" });
      assert.equal(await term.getAttribute("aria-expanded"), "false");
      assert.equal(await page.evaluate(() => document.activeElement && document.activeElement.dataset.gloss), "baseline", "focus is back on the term");
      assert.match(page.url(), /#\/experiment\/k2k/, "the record is still open");
      assert.equal(await page.locator("#detail-panel h2").isVisible(), true);

      // Space opens it again; Tab walks its controls and leaves it, back on the term's reading order.
      await page.keyboard.press("Space");
      await popover.waitFor({ state: "visible" });
      await page.keyboard.press("Tab");
      assert.equal(await page.evaluate(() => document.activeElement.tagName), "A", "Tab reaches the source link");
      await page.keyboard.press("Tab");
      assert.equal(await page.evaluate(() => document.activeElement.tagName), "SUMMARY");
      await page.keyboard.press("Tab");
      assert.equal(await page.evaluate(() => document.activeElement.className), "gloss-pop-close");
      await page.keyboard.press("Tab");
      await popover.waitFor({ state: "hidden" });
      // A click elsewhere closes it too, and the close button.
      await term.click();
      await popover.waitFor({ state: "visible" });
      await page.locator("#globe-stage").click({ position: { x: 40, y: 400 }, force: true });
      await popover.waitFor({ state: "hidden" });
      await term.click();
      await popover.locator(".gloss-pop-close").click();
      await popover.waitFor({ state: "hidden" });
      await context.close();
    });

    await record("Glossary popover on a phone: opens by tap inside the screen with no horizontal scroll", async () => {
      const context = await newContext({ viewport: { width: 390, height: 844 }, ...MOBILE });
      const page = await context.newPage();
      await page.goto(url("#/experiment/k2k"));
      await waitForPanel(page, "K2K");
      const term = page.locator('#detail-panel .gloss-term[data-gloss="baseline"]');
      await term.waitFor({ timeout: 15000 });
      await term.tap();
      const popover = page.locator("#gloss-pop");
      await popover.waitFor({ state: "visible" });
      const box = await popover.boundingBox();
      assert.ok(box.x >= 0 && box.x + box.width <= 390 && box.y >= 0 && box.y + box.height <= 844, `the popover fits the phone screen (${JSON.stringify(box)})`);
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth) <= 1);
      await popover.locator(".gloss-pop-close").tap();
      await popover.waitFor({ state: "hidden" });
      await context.close();
    });
  }

  // ------------------------------------------------- plain / technical summary
  await record("Plain / technical toggle: plain by default, swaps in place, is remembered, and has terms in the technical text", async () => {
    const context = await newContext({ viewport: { width: 1440, height: 900 } });
    const page = await context.newPage();
    await page.goto(url("#/experiment/t2k"));
    await waitForPanel(page, "T2K");
    const toggle = page.locator("#detail-panel .summary-toggle");
    await toggle.waitFor();
    assert.equal(await toggle.locator('[role="group"]').count(), 1);
    const plainButton = toggle.locator('button[data-mode="plain"]');
    const technicalButton = toggle.locator('button[data-mode="technical"]');
    assert.equal(await plainButton.getAttribute("aria-pressed"), "true", "plain is the default");
    assert.equal(await technicalButton.getAttribute("aria-pressed"), "false");
    const summary = page.locator("#detail-panel [data-summary]").first();
    assert.match(await summary.innerText(), /A beam of neutrinos made at the J-PARC accelerator/);
    assert.equal(await stored(page, "hep-atlas.summary"), null, "nothing is stored until the reader chooses");

    // Mark the panel's own elements: an in-place swap leaves them (and open sections) alone.
    await page.evaluate(() => { window.__heading = document.querySelector("#detail-panel h2"); });
    await technicalButton.click();
    await page.waitForFunction(() => /Long-baseline accelerator neutrino/.test(document.querySelector("#detail-panel [data-summary]").textContent));
    assert.equal(await technicalButton.getAttribute("aria-pressed"), "true");
    assert.equal(await plainButton.getAttribute("aria-pressed"), "false");
    assert.equal(await stored(page, "hep-atlas.summary"), "technical");
    assert.equal(await page.evaluate(() => window.__heading === document.querySelector("#detail-panel h2")), true, "the record was not re-rendered");
    assert.equal(await page.locator("#detail-panel [data-hide-when]").first().isHidden(), true, "the technical section's duplicate is not shown twice");
    if (GENERATED) {
      await page.locator("#detail-panel [data-summary] .gloss-term").first().waitFor({ timeout: 15000 });
      const ids = await page.locator("#detail-panel .gloss-term").evaluateAll((els) => els.map((el) => el.dataset.gloss));
      assert.equal(new Set(ids).size, ids.length, "each term is marked once per record");
      assert.ok(ids.includes("baseline") && ids.includes("neutrino-oscillation"), `technical text marks its terms (${ids.join(", ")})`);
    }
    // Keyboard: the toggle is two real buttons.
    await plainButton.focus();
    await page.keyboard.press("Enter");
    await page.waitForFunction(() => /A beam of neutrinos made at/.test(document.querySelector("#detail-panel [data-summary]").textContent));
    assert.equal(await stored(page, "hep-atlas.summary"), "plain");

    // Remembered across a reload and a different record.
    await technicalButton.click();
    await page.reload();
    await waitForPanel(page, "T2K");
    assert.equal(await page.locator('#detail-panel .summary-toggle button[data-mode="technical"]').getAttribute("aria-pressed"), "true");
    await page.waitForFunction(() => /Long-baseline accelerator neutrino/.test(document.querySelector("#detail-panel [data-summary]").textContent));
    await context.close();
  });

  assert.deepEqual(errors, [], "No uncaught browser errors");

  fs.writeFileSync(
    path.join(output, `classroom-report-${BROWSER_NAME}.json`),
    JSON.stringify({
      browser: await browser.version(),
      engine: BROWSER_NAME,
      dataTree: GENERATED ? "generated" : "fixtures",
      base,
      checked_at: new Date().toISOString(),
      checks: results,
      uncaught_errors: errors,
      status: "passed",
    }, null, 2),
  );
  console.log(JSON.stringify({ passed: results.filter((r) => r.status === "passed").length, skipped: results.filter((r) => r.status === "skipped").length, errors, engine: BROWSER_NAME }));
  await browser.close();
})().catch(async (error) => {
  console.error(error);
  fs.writeFileSync(
    path.join(output, `classroom-report-${BROWSER_NAME}.json`),
    JSON.stringify({ status: "failed", checks: results, error: String(error), uncaught_errors: errors }, null, 2),
  );
  if (browser) await browser.close();
  process.exit(1);
});
