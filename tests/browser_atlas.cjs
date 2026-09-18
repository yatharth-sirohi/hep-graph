/* HEP Atlas browser acceptance: npm install --no-save playwright, then
   node tests/browser_atlas.cjs. Set HEP_BROWSER_EXECUTABLE to use an
   installed Chromium-family browser. Exercises the globe, timeline,
   collaboration mode, search, and the no-WebGL fallback view. */
const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const base = process.env.HEP_URL || "http://127.0.0.1:8790";
// Which data tree to exercise. The fixtures are convenient but they are not
// the product: three separate features were dead against the generated
// bundles while this suite was green, because it only ever loaded fixtures.
// HEP_ATLAS_DATA=generated runs the same checks against the real build.
const dataTree = process.env.HEP_ATLAS_DATA === "generated" ? "" : "?data=fixtures";
// The fixture names DUNE by its acronym; the real data uses its full name with
// "DUNE" as an alias. Both must be searchable, so the label differs per tree.
const duneLabel = process.env.HEP_ATLAS_DATA === "generated"
  ? "Deep Underground Neutrino Experiment" : "DUNE — Experiment";
const duneHeading = process.env.HEP_ATLAS_DATA === "generated"
  ? "Deep Underground Neutrino Experiment" : "DUNE";
// The ATLAS cavern, whose marker must vanish in 1990.
const atlasCavernId = process.env.HEP_ATLAS_DATA === "generated"
  ? "site:cern-point-1-atlas" : "site:cern-lhc-point-1";
const atlasCavernSelector = `.atlas-marker[data-id="${atlasCavernId}"]`;
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
  context.setDefaultTimeout(45000);
  context.on("page", (p) => p.on("pageerror", (e) => errors.push(e.message)));
  context.on("page", (p) => p.on("console", (msg) => {
    if (msg.type() === "error") errors.push(`console.error: ${msg.text()}`);
  }));
  const page = await context.newPage();

  await record("Atlas loads with a WebGL canvas and no console errors", async () => {
    await page.goto(`${base}/atlas${dataTree}`);
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
    await page.locator(".search-result", { hasText: duneLabel }).first().click();
    await page.locator("#detail-panel h2", { hasText: duneHeading }).waitFor();
    const panelText = await page.locator("#detail-panel").innerText();
    assert.match(panelText, /Baseline/);
    assert.match(panelText, /1285 ?km|1,285 ?km/);
  });

  await record("Collaboration mode shows institution dots on the globe", async () => {
    await page.locator(".collab-line .collab-link").first().click();
    await page.locator("#detail-panel h2", { hasText: "DUNE Collaboration" }).waitFor();
    const panelText = await page.locator("#detail-panel").innerText();
    // Ontology amendment A19/A5 wording, sourced from the membership bundle's
    // own `counts.confirmed`/`counts.undated` — not the literal "0 confirmed
    // members" the panel used to show for every collaboration (it read a
    // `confirmed_count` field the collaboration record never carried).
    assert.match(panelText, /\d+ confirmed members \(\+\d+ undated\)/);
    assert.doesNotMatch(panelText, /\b0 confirmed members\b(?!\s*\()/, "DUNE has a real, nonzero confirmed-member count");
    await page.locator("#view-on-globe").click();
    await page.waitForFunction(() => document.querySelectorAll(".atlas-marker.tier-institution").length > 0, { timeout: 10000 });
    assert.ok(await page.locator(".atlas-marker.tier-institution").count() > 0);
  });

  await record("Experiment status badge follows the selected timeline year, not just build-time status", async () => {
    await page.goto(`${base}/atlas${dataTree}#/experiment/dune`);
    await page.locator("#detail-panel h2").waitFor();
    await setRangeValue(page.locator("#timeline-year"), 1995);
    await page.waitForFunction(() => {
      const el = document.querySelector("#detail-panel .status-badge");
      return !!el && el.textContent.trim().length > 0;
    });
    // DUNE was not proposed until the 2010s in either data tree — at 1995
    // the panel must say so plainly instead of showing a frozen status like
    // "Construction" or "Active" that didn't apply for another two decades.
    const badge1995 = await page.locator("#detail-panel .status-badge").first().innerText();
    assert.match(badge1995, /not yet/i, `expected DUNE's 1995 badge to say it did not exist yet, got "${badge1995}"`);
    assert.ok(await page.locator("#detail-panel .status-badge.is-outside-timeline").count() > 0);

    await setRangeValue(page.locator("#timeline-year"), 2026);
    await page.waitForFunction((prev) => {
      const el = document.querySelector("#detail-panel .status-badge");
      return !!el && el.textContent.trim() !== prev;
    }, badge1995);
    const badge2026 = await page.locator("#detail-panel .status-badge").first().innerText();
    assert.notEqual(badge2026, badge1995, "the badge must change when the timeline year changes");
    assert.doesNotMatch(badge2026, /not yet/i, "DUNE has a real status by 2026");
    await setRangeValue(page.locator("#timeline-year"), 2026);
  });

  await record("Experiment panel shows its plain-language summary, not the placeholder", async () => {
    await page.goto(`${base}/atlas${dataTree}#/experiment/dune`);
    await page.locator("#detail-panel h2").waitFor();
    const panelText = await page.locator("#detail-panel").innerText();
    // The real bundle puts summary.plain on the atlas.json record itself;
    // the fixtures instead put it in text.json. Whichever tree is live, one
    // of those exists for DUNE, so the placeholder must never show.
    assert.doesNotMatch(panelText, /No plain-language summary yet/);
    assert.match(panelText, /1285/, "expected DUNE's own baseline figure to appear in its plain summary");
  });

  await record("Document panel shows a real title and date, not a blank heading", async () => {
    await page.locator("#atlas-search").fill("");
    await page.locator("#atlas-search").fill("Technical Design Report");
    await page.locator(".search-result").first().waitFor();
    await page.locator(".search-result").first().click();
    await page.locator("#detail-panel h2").waitFor();
    const heading = (await page.locator("#detail-panel h2").innerText()).trim();
    const subtitle = (await page.locator("#detail-panel .panel-subtitle").innerText()).trim();
    // The bundle's document records carry `name`/`date`, not `title`/`year`;
    // reading the wrong pair left every one of the ~56 documents with a
    // blank <h2> and a subtitle ending in a dangling "· " separator.
    assert.ok(heading.length > 0, "document heading must not be blank");
    assert.doesNotMatch(subtitle, /·\s*$/, "document subtitle must not end in a dangling separator");
    assert.match(subtitle, /\d{4}/, "document subtitle should carry a real year");
  });

  await record("Fermilab facility panel lists under-construction DUNE as current, not historical", async () => {
    await page.goto(`${base}/atlas${dataTree}#/facility/fermilab`);
    await page.locator("#detail-panel h2", { hasText: /Fermi/ }).waitFor();
    const sections = await page.locator("#detail-panel .panel-section").evaluateAll(
      (nodes) => nodes.map((n) => ({ heading: n.querySelector("summary")?.textContent || "", text: n.textContent || "" })),
    );
    const current = sections.find((s) => s.heading.includes("Current experiments"));
    const historical = sections.find((s) => s.heading.includes("Historical experiments"));
    const future = sections.find((s) => s.heading.includes("Future"));
    assert.ok(current && current.text.includes(duneHeading), "DUNE should be listed under Current experiments at Fermilab");
    assert.ok(historical && !historical.text.includes(duneHeading), "DUNE must not also be listed under Historical experiments");
    assert.ok(future, "a Future / planned experiments section should exist alongside current and historical");
  });

  await record("Setting the year to 1990 hides the not-yet-built ATLAS cavern site", async () => {
    await setRangeValue(page.locator("#timeline-year"), 1990);
    await page.waitForFunction((selector) => {
      const el = document.querySelector(selector);
      return !!el && (el.classList.contains("is-absent") || el.classList.contains("is-dimmed"));
    }, atlasCavernSelector, { timeout: 5000 });
    const state = await page.locator(atlasCavernSelector).evaluate((el) => ({
      absent: el.classList.contains("is-absent"),
      dimmed: el.classList.contains("is-dimmed"),
      display: getComputedStyle(el).display,
    }));
    assert.ok(state.absent || state.dimmed, "ATLAS site marker should be absent or dimmed at 1990");
    if (state.absent) assert.equal(state.display, "none");
    await setRangeValue(page.locator("#timeline-year"), 2026);
  });

  await record("Key-specification values wrap inside the panel instead of spilling past its edge", async () => {
    await page.goto(`${base}/atlas${dataTree}#/experiment/dune`);
    await page.locator("#detail-panel h2").waitFor();
    await page.waitForFunction(() => document.querySelectorAll("#detail-panel .kv-list dd").length > 0);
    const overflowing = await page.evaluate(() => {
      const panelRight = document.getElementById("detail-panel").getBoundingClientRect().right;
      return [...document.querySelectorAll("#detail-panel .kv-list dd")]
        .filter((dd) => dd.getBoundingClientRect().right > panelRight + 1)
        .map((dd) => dd.textContent);
    });
    assert.deepEqual(overflowing, [], "no key-spec value should render past the detail panel's own right edge");
  });

  await record("Site-tier globe markers have an enlarged tap target", async () => {
    await page.goto(`${base}/atlas${dataTree}`);
    await page.waitForFunction(() => document.querySelectorAll(".atlas-marker").length > 0, { timeout: 15000 });
    const afterInset = await page.evaluate(() => {
      const el = document.querySelector(".atlas-marker.is-site-tier");
      if (!el) return null;
      return getComputedStyle(el, "::after").inset;
    });
    assert.ok(afterInset, "expected at least one site-tier marker in the DOM");
    // A negative inset grows the ::after hit box symmetrically outward from
    // the (still 12x12px) drawn glyph, without moving it off its geographic
    // anchor the way padding+margin on the marker itself would.
    assert.match(afterInset, /^-\d/, `expected a negative inset to enlarge the tap target, got "${afterInset}"`);
  });

  await record("Opening a panel does not fetch provenance/sources; opening the Sources disclosure does (P1-2)", async () => {
    // A fresh context so loader.js's in-memory bundle cache starts empty —
    // every earlier check in this file may already have opened a Sources
    // disclosure, which would otherwise mask a regression to eager fetching.
    const freshContext = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const freshErrors = [];
    freshContext.on("page", (p) => p.on("pageerror", (e) => freshErrors.push(e.message)));
    const freshPage = await freshContext.newPage();
    const requested = [];
    await freshPage.route("**/*", (route) => {
      const url = route.request().url();
      if (url.includes("provenance.json") || url.includes("sources.json")) requested.push(url);
      route.continue();
    });
    await freshPage.goto(`${base}/atlas${dataTree}#/facility/cern`);
    await freshPage.locator("#detail-panel h2").waitFor();
    assert.deepEqual(requested, [], `opening a panel must not eagerly fetch provenance/sources, got ${JSON.stringify(requested)}`);

    const sourcesSummary = freshPage.locator("#detail-panel details.panel-section summary", { hasText: "Sources" });
    await sourcesSummary.waitFor();
    await sourcesSummary.click();
    await freshPage.waitForFunction(() => {
      const summaries = [...document.querySelectorAll("#detail-panel details.panel-section summary")];
      const details = summaries.find((s) => s.textContent.trim() === "Sources")?.closest("details");
      return !!details && details.open && !details.querySelector(".loading-note");
    }, { timeout: 10000 });
    assert.ok(requested.some((u) => u.includes("provenance.json")), "opening the Sources disclosure must fetch provenance.json");
    assert.ok(requested.some((u) => u.includes("sources.json")), "opening the Sources disclosure must fetch sources.json");
    assert.deepEqual(freshErrors, [], "no console errors while loading sources lazily");
    await freshContext.close();
  });

  await record("Blocking atlas.json shows an accessible error state with a retry control (P1-4)", async () => {
    const freshContext = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const freshPage = await freshContext.newPage();
    await freshPage.route("**/atlas.json", (route) => route.abort());
    await freshPage.goto(`${base}/atlas${dataTree}`);
    await freshPage.locator("#atlas-error:not(.hidden)").waitFor({ timeout: 15000 });
    assert.equal(await freshPage.locator("#atlas-error").getAttribute("role"), "alert");
    const errorText = await freshPage.locator("#atlas-error-message").innerText();
    assert.match(errorText, /could not load|offline/i, `expected a real explanation, got "${errorText}"`);
    await freshPage.locator("#atlas-retry").waitFor();
    await freshContext.close();
  });

  await record("A throttled connection shows a visible, accessible loading state before data arrives (P1-4)", async () => {
    const freshContext = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const freshPage = await freshContext.newPage();
    const client = await freshContext.newCDPSession(freshPage);
    await client.send("Network.enable");
    await client.send("Network.emulateNetworkConditions", {
      offline: false, latency: 400, downloadThroughput: (400 * 1024) / 8, uploadThroughput: (400 * 1024) / 8,
    });
    const navigation = freshPage.goto(`${base}/atlas${dataTree}`);
    await freshPage.locator("#data-notice:not(.hidden)").waitFor({ timeout: 10000 });
    assert.equal(await freshPage.locator("#data-notice").getAttribute("role"), "status");
    const loadingText = await freshPage.locator("#data-notice").innerText();
    assert.match(loadingText, /loading/i, `expected visible loading text, got "${loadingText}"`);
    await client.send("Network.emulateNetworkConditions", {
      offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1,
    });
    await navigation;
    await freshContext.close();
  });

  await record("Desktop screenshot", async () => {
    await page.screenshot({ path: path.join(output, "desktop.png"), fullPage: true });
  });

  await record("390x844 mobile viewport avoids overflow and stays usable", async () => {
    const mobile = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
    mobile.on("page", (p) => p.on("pageerror", (e) => errors.push(e.message)));
    const p = await mobile.newPage();
    await p.goto(`${base}/atlas${dataTree}`);
    await p.locator("canvas").first().waitFor({ timeout: 15000 });
    assert.ok(await p.evaluate(() => document.documentElement.scrollWidth <= 392));
    await p.screenshot({ path: path.join(output, "mobile.png"), fullPage: true });
    await mobile.close();
  });

  // Close the main (WebGL, continuously rendering) context before launching
  // a second Chromium process for the no-WebGL check, so the two renderers
  // do not compete for CPU on the same machine.
  await context.close();

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
    await noGlPage.goto(`${base}/atlas${dataTree}`);
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
