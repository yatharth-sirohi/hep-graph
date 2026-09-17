/* HEP Atlas browser acceptance: npm install --no-save playwright, then
   node tests/browser_atlas.cjs. Set HEP_BROWSER_EXECUTABLE to use an
   installed Chromium-family browser. Exercises the globe, timeline,
   collaboration mode, search, and the no-WebGL fallback view. */
const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const base = process.env.HEP_URL || "http://127.0.0.1:8790";
const output = process.env.HEP_ATLAS_OUTPUT || path.join(__dirname, "../test-results/atlas");
fs.mkdirSync(output, { recursive: true });

const results = [];
const errors = [];
let browser;

const record = async (name, fn) => {
  const start = Date.now();
  await fn();
  results.push({ name, status: "passed", milliseconds: Date.now() - start });
  console.log("PASS", name);
};

async function setRangeValue(locator, value) {
  await locator.evaluate((el, v) => {
    const proto = window.HTMLInputElement.prototype;
    const setter = Object.getOwnPropertyDescriptor(proto, "value").set;
    setter.call(el, String(v));
    el.dispatchEvent(new Event("input", { bubbles: true }));
  }, value);
}

(async () => {
  browser = await chromium.launch({
    headless: true,
    ...(process.env.HEP_BROWSER_EXECUTABLE ? { executablePath: process.env.HEP_BROWSER_EXECUTABLE } : {}),
  });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 960 },
    reducedMotion: "reduce",
  });
  context.on("page", (p) => p.on("pageerror", (e) => errors.push(e.message)));
  context.on("page", (p) => p.on("console", (msg) => {
    if (msg.type() === "error") errors.push(`console.error: ${msg.text()}`);
  }));
  const page = await context.newPage();

  await record("Atlas loads with a WebGL canvas and no console errors", async () => {
    await page.goto(`${base}/atlas?data=fixtures`);
    await page.locator("canvas").first().waitFor({ timeout: 15000 });
    await page.waitForFunction(() => document.querySelectorAll(".atlas-marker").length > 0, { timeout: 15000 });
    assert.ok(await page.locator("canvas").count() > 0, "expected a <canvas> element");
    assert.equal(await page.locator("#data-version-label").innerText().then((t) => t.length > 0), true);
  });

  await record("Clicking a facility marker opens its detail panel", async () => {
    const marker = page.locator('.atlas-marker[data-id="facility:cern"]');
    await marker.waitFor();
    await marker.click({ force: true });
    await page.locator("#detail-panel h2").waitFor();
    assert.match(await page.locator("#detail-panel h2").innerText(), /CERN/);
    assert.equal(await page.locator("#detail-panel").isHidden(), false);
  });

  await record("Search finds DUNE and its panel shows a baseline", async () => {
    await page.locator("#atlas-search").fill("DUNE");
    await page.locator(".search-result", { hasText: "DUNE" }).first().waitFor();
    await page.locator(".search-result", { hasText: "DUNE — Experiment" }).first().click();
    await page.locator("#detail-panel h2", { hasText: "DUNE" }).waitFor();
    const panelText = await page.locator("#detail-panel").innerText();
    assert.match(panelText, /Baseline/);
    assert.match(panelText, /1285 ?km|1,285 ?km/);
  });

  await record("Collaboration mode shows institution dots on the globe", async () => {
    await page.locator(".collab-line .collab-link").first().click();
    await page.locator("#detail-panel h2", { hasText: "DUNE Collaboration" }).waitFor();
    assert.match(await page.locator("#detail-panel").innerText(), /confirmed members/);
    await page.locator("#view-on-globe").click();
    await page.waitForFunction(() => document.querySelectorAll(".atlas-marker.tier-institution").length > 0, { timeout: 10000 });
    assert.ok(await page.locator(".atlas-marker.tier-institution").count() > 0);
  });

  await record("Setting the year to 1990 hides the not-yet-built ATLAS cavern site", async () => {
    await setRangeValue(page.locator("#timeline-year"), 1990);
    await page.waitForFunction(() => {
      const el = document.querySelector('.atlas-marker[data-id="site:cern-lhc-point-1"]');
      return !!el && (el.classList.contains("is-absent") || el.classList.contains("is-dimmed"));
    }, { timeout: 5000 });
    const state = await page.locator('.atlas-marker[data-id="site:cern-lhc-point-1"]').evaluate((el) => ({
      absent: el.classList.contains("is-absent"),
      dimmed: el.classList.contains("is-dimmed"),
      display: getComputedStyle(el).display,
    }));
    assert.ok(state.absent || state.dimmed, "ATLAS site marker should be absent or dimmed at 1990");
    if (state.absent) assert.equal(state.display, "none");
    await setRangeValue(page.locator("#timeline-year"), 2026);
  });

  await record("Desktop screenshot", async () => {
    await page.screenshot({ path: path.join(output, "desktop.png"), fullPage: true });
  });

  await record("390x844 mobile viewport avoids overflow and stays usable", async () => {
    const mobile = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
    mobile.on("page", (p) => p.on("pageerror", (e) => errors.push(e.message)));
    const p = await mobile.newPage();
    await p.goto(`${base}/atlas?data=fixtures`);
    await p.locator("canvas").first().waitFor({ timeout: 15000 });
    assert.ok(await p.evaluate(() => document.documentElement.scrollWidth <= 392));
    await p.screenshot({ path: path.join(output, "mobile.png"), fullPage: true });
    await mobile.close();
  });

  await record("Without WebGL2 the accessible fallback list renders", async () => {
    const noGlBrowser = await chromium.launch({
      headless: true,
      args: ["--disable-webgl", "--disable-webgl2", "--use-gl=disabled"],
      ...(process.env.HEP_BROWSER_EXECUTABLE ? { executablePath: process.env.HEP_BROWSER_EXECUTABLE } : {}),
    });
    const noGlContext = await noGlBrowser.newContext({ viewport: { width: 1280, height: 900 } });
    const noGlErrors = [];
    noGlContext.on("page", (p) => p.on("pageerror", (e) => noGlErrors.push(e.message)));
    const noGlPage = await noGlContext.newPage();
    await noGlPage.goto(`${base}/atlas?data=fixtures`);
    await noGlPage.locator(".fallback-notice").waitFor({ timeout: 15000 });
    assert.match(await noGlPage.locator(".fallback-notice").innerText(), /not shown/i);
    assert.ok(await noGlPage.locator(".fallback-table").count() >= 3);
    assert.equal(await noGlPage.locator("canvas").count(), 0);
    await noGlPage.locator(".fallback-table a", { hasText: "Fermilab" }).first().click();
    await noGlPage.locator("#detail-panel h2", { hasText: "Fermilab" }).waitFor();
    await noGlPage.screenshot({ path: path.join(output, "fallback.png"), fullPage: true });
    assert.deepEqual(noGlErrors, [], "No uncaught errors in the fallback view");
    await noGlBrowser.close();
  });

  assert.deepEqual(errors, [], "No uncaught browser errors in the main scenario");

  fs.writeFileSync(
    path.join(output, "report.json"),
    JSON.stringify({
      browser: await browser.version(),
      engine: "Chromium via Playwright",
      base,
      checked_at: new Date().toISOString(),
      checks: results,
      uncaught_errors: errors,
      status: "passed",
    }, null, 2),
  );
  console.log(JSON.stringify({ passed: results.length, errors, browser: await browser.version() }));
  await browser.close();
})().catch(async (error) => {
  console.error(error);
  fs.writeFileSync(
    path.join(output, "report.json"),
    JSON.stringify({ status: "failed", checks: results, error: String(error), uncaught_errors: errors }, null, 2),
  );
  if (browser) await browser.close();
  process.exit(1);
});
