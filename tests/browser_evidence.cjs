/* Focused mocked browser checks for coverage evidence rendering.
 * The fixture contains hostile-looking source text and never contacts INSPIRE. */
const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const base = process.env.HEP_URL || "http://127.0.0.1:8765";
const output = process.env.HEP_EVIDENCE_OUTPUT || path.resolve(__dirname, "../../../work/audit/evidence-check");
const hostile = "<img src=x onerror=alert('source')> & <script>bad()</script>";
const coverage = {
  label: "Temporary Live INSPIRE data",
  description: hostile,
  complete: false,
  queries: [{ q: "<script>query</script>" }],
  failures: [{ message: "<img src=x onerror=alert('failure')>" }],
  identity_ambiguous_profiles: [
    { input: "<img src=x onerror=alert('one')>", candidates: ["A", "B"] },
    { input: "<script>profile</script>", candidates: ["C", "D"] },
  ],
  identity_phd_conflicts: [
    { author: "Chen-Ning Yang", reason: "contradictory adviser name and record ID" },
  ],
};
const version = "live-inspire-v1";
const person = (id, name) => ({ id, name, indexed: false, queryable: true, mode: "live", affiliations: [] });

async function main() {
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    ...(process.env.HEP_BROWSER_EXECUTABLE ? { executablePath: process.env.HEP_BROWSER_EXECUTABLE } : {}),
  });
  const checks = [];
  const errors = [];

  {
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const page = await context.newPage();
    page.on("pageerror", (error) => errors.push(error.message));
    await installRoutes(page);
    await page.goto(`${base}/?mode=live`);
    await page.waitForFunction(() => document.querySelector("#data-mode")?.value === "live");
    await page.locator("#coverage-details").click();
    await page.locator("#about-coverage h3").waitFor();
    const details = await page.locator("#about-coverage").textContent();
    assert.match(details, /Evidence checks for this search/);
    assert.match(details, /Ambiguous author profiles withheld: 2/);
    assert.match(details, /Doctoral references withheld for identity conflicts: 1/);
    assert.match(details, /<img src=x onerror=alert\('source'\)>/);
    assert.match(details, /<script>bad\(\)<\/script>/);
    assert.equal(await page.locator("#about-coverage img, #about-coverage script").count(), 0);
    assert.equal(await page.locator("#about-coverage [onerror], #about-coverage [onclick]").count(), 0);
    await page.screenshot({ path: path.join(output, "evidence-details.png"), fullPage: true });
    checks.push({ name: "coverage evidence counts and hostile source text are rendered as text", status: "passed" });
    await context.close();
  }

  {
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const page = await context.newPage();
    page.on("pageerror", (error) => errors.push(error.message));
    await installRoutes(page);
    await page.goto(`${base}/?mode=live`);
    await page.waitForFunction(() => document.querySelector("#data-mode")?.value === "live");
    await page.locator("#source-query").fill("Evidence Source");
    await page.locator("#source-results button").filter({ hasText: "Evidence Source" }).first().click();
    await page.locator("#target-query").fill("Evidence Target");
    await page.locator("#target-results button").filter({ hasText: "Evidence Target" }).first().click();
    const pathResponse = page.waitForResponse((response) => new URL(response.url()).pathname === "/api/path");
    await page.locator("#find-connection").click();
    await pathResponse;
    await page.locator("#deep-progress").waitFor({ state: "visible" });
    assert.match(await page.locator("#deep-summary").innerText(), /profile and paper author names/i);
    checks.push({ name: "identity validation progress uses researcher-facing wording", status: "passed" });
    await context.close();
  }

  await browser.close();
  const report = {
    checked_at: new Date().toISOString(),
    browser: browser.version(),
    playwright: require("playwright/package.json").version,
    base,
    status: errors.length ? "failed" : "passed",
    checks,
    uncaught_errors: errors,
    artifacts: ["evidence-details.png", "report.json"],
    fixture: "mocked coverage with literal hostile text; no live network",
  };
  fs.writeFileSync(path.join(output, "report.json"), JSON.stringify(report, null, 2) + "\n");
  assert.equal(report.status, "passed");
}

async function installRoutes(page) {
  await page.route("**/api/**", async (route) => {
    const u = new URL(route.request().url());
    const mode = u.searchParams.get("mode");
    assert.equal(mode, "live", `expected live mode on ${u.pathname}`);
    let body = { status: "ok", mode, version, paths: [], people: [], edges: [] };
    if (u.pathname === "/api/dataset") {
      body = { source_mode: "live", mode, version, coverage, counts: null, capabilities: { live_graph: true, global_centrality: false }, examples: [] };
    } else if (u.pathname === "/api/search") {
      const target = (u.searchParams.get("q") || "").toLowerCase().includes("target");
      body = { status: "ok", source: "live", mode, version, results: [person(target ? "9002" : "9001", target ? "Evidence Target" : "Evidence Source")] };
    } else if (u.pathname === "/api/path") {
      body = {
        status: "searching", job_id: "evidence-job", mode, version,
        filters: { min_authors: 1, max_authors: 10, min_shared: 1, genealogy: true }, coverage,
        progress: { people_explored: 3, works_retrieved: 5, elapsed_seconds: 1, stage: "validate_identity" },
        can_continue: false, paths: [],
      };
    } else if (u.pathname.startsWith("/api/search-jobs/")) {
      body = { status: "searching", job_id: "evidence-job", mode, version, coverage, progress: { people_explored: 3, works_retrieved: 5, elapsed_seconds: 1, stage: "validate_identity" }, paths: [], can_continue: false };
    }
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) });
  });
}

main().catch((error) => { console.error(error.stack || error); process.exitCode = 1; });
