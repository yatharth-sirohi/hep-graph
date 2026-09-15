/* Browser regressions for retaining and recovering bounded Live INSPIRE jobs.
 * Every /api request is intercepted below; this test never contacts INSPIRE. */
const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const base = process.env.HEP_URL || "http://127.0.0.1:8766";
const output = process.env.HEP_RESILIENCE_OUTPUT || path.resolve(
  __dirname,
  "../../../work/general-search/browser-resilience",
);
const storageKey = "hep-graph-active-search";
const retainedId = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
const freshId = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";
const version = "live-resilience-v1";
const coverage = {
  label: "Temporary Live INSPIRE data",
  partial: true,
  retrieved: { people: 2, works: 1 },
};
const defaultFilters = {
  min_authors: "1",
  max_authors: "10",
  min_shared: "1",
  year_start: "",
  year_end: "",
  genealogy: "true",
};

const person = (id, name) => ({
  id,
  name,
  indexed: false,
  queryable: true,
  mode: "live",
  affiliations: [],
});
const routeData = (jobId) => ({
  status: "ok",
  job_id: jobId,
  mode: "live",
  version,
  exact: false,
  exact_for_retrieved_graph: true,
  global_shortest_proven: false,
  filters: defaultFilters,
  coverage,
  paths: [{
    hops: 1,
    people: [person("9001", "Deep Source"), person("9002", "Deep Target")],
    edges: [{
      source: "9001",
      target: "9002",
      types: ["coauthor"],
      shared_works: 1,
      works: [{
        id: "resilience-work",
        title: "Mocked retrieved work",
        year: 2024,
        date_source: "preprint",
        author_count: 2,
        authors: ["9001", "9002"],
        source_url: "https://inspirehep.net/literature/resilience-work",
      }],
    }],
  }],
});
const searching = (jobId) => ({
  status: "searching",
  job_id: jobId,
  mode: "live",
  version,
  filters: defaultFilters,
  coverage,
  progress: {
    people_explored: 2,
    works_retrieved: 1,
    elapsed_seconds: 1,
    stage: "retrieve_people",
  },
  paths: [],
  can_continue: false,
});

async function main() {
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    ...(process.env.HEP_BROWSER_EXECUTABLE
      ? { executablePath: process.env.HEP_BROWSER_EXECUTABLE }
      : {}),
  });
  const checks = [];
  const errors = [];
  const check = async (name, fn) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    const page = await context.newPage();
    const pageErrors = [];
    page.on("pageerror", (error) => pageErrors.push(error.message));
    try {
      const harness = await install(page, name);
      await fn({ context, page, harness, pageErrors });
      assert.deepEqual(pageErrors, [], `unexpected page errors: ${pageErrors.join("; ")}`);
      checks.push({ name, status: "passed" });
      console.log("PASS", name);
    } catch (error) {
      checks.push({ name, status: "failed", error: error.message });
      errors.push(`${name}: ${error.stack || error}`);
      throw error;
    } finally {
      await context.close();
    }
  };

  try {
    await check("reload keeps the matching retained job without a second path start", async ({ page, harness }) => {
      await prepare(page);
      await choosePair(page);
      await start(page);
      assert.equal(harness.pathStarts, 1);
      await page.reload();
      await page.locator("#path-cards .path-card").waitFor();
      assert.equal(harness.pathStarts, 1, "reload must resume the server job, not create another one");
      assert.ok(harness.jobGets(retainedId) >= 1, "reload should poll the retained 32-hex handle");
    });

    await check("a changed filter never reuses a retained job from another configuration", async ({ page, harness }) => {
      await retainOnNextNavigation(page, retainedId, defaultFilters);
      await prepare(page);
      await choosePair(page);
      await page.locator("#paper-team-size").selectOption("large");
      await start(page);
      assert.equal(harness.jobGets(retainedId), 0);
      assert.equal(harness.pathStarts, 1);
    });

    await check("a legacy retained job without minimum-author scope is never reused", async ({ page, harness }) => {
      const { min_authors, ...legacyFilters } = defaultFilters;
      await retainOnNextNavigation(page, retainedId, legacyFilters);
      await prepare(page);
      await choosePair(page);
      await start(page);
      assert.equal(harness.jobGets(retainedId), 0);
      assert.equal(harness.pathStarts, 1);
    });

    await check("a temporary polling 500 retries automatically and renders the final route", async ({ page, harness }) => {
      await prepare(page);
      await choosePair(page);
      await start(page);
      await page.locator("#path-cards .path-card").waitFor({ timeout: 8000 });
      assert.equal(harness.jobGets(retainedId), 2, "one failed poll should be followed by one retry");
      assert.match(await page.locator("#path-title").innerText(), /documented route/i);
      assert.equal(await page.locator("#deep-progress").isVisible(), false);
    });

    await check("Stop cancels a job while its failed poll is waiting to retry", async ({ page, harness }) => {
      await prepare(page);
      await choosePair(page);
      await start(page);
      await page.waitForFunction(() => /Reconnecting to the running search/i.test(document.querySelector("#deep-summary")?.textContent || ""), null, { timeout: 5000 });
      await page.locator("#deep-stop").click();
      await page.waitForTimeout(2300);
      assert.equal(harness.jobGets(retainedId), 1, "Stop must clear the scheduled retry");
      assert.equal(harness.cancels, 1, "Stop sends exactly one cancellation");
      assert.equal(await page.evaluate((key) => sessionStorage.getItem(key), storageKey), null);
    });

    await check("a retained job that has expired server-side falls back to one fresh start", async ({ page, harness }) => {
      await retainOnNextNavigation(page, retainedId, defaultFilters);
      await prepare(page);
      await choosePair(page);
      await start(page);
      assert.equal(harness.jobGets(retainedId), 1);
      assert.equal(harness.pathStarts, 1);
      await page.waitForFunction(() => document.querySelector("#deep-progress")?.classList.contains("hidden") === false);
      const stored = await page.evaluate((key) => JSON.parse(sessionStorage.getItem(key)), storageKey);
      assert.equal(stored.jobId, freshId);
    });

    await check("malformed retained storage is ignored without a browser error", async ({ page, harness }) => {
      await page.addInitScript((key) => sessionStorage.setItem(key, "{invalid json"), storageKey);
      await prepare(page);
      await choosePair(page);
      await start(page);
      assert.equal(harness.pathStarts, 1);
      assert.equal(harness.jobGets(retainedId), 0);
    });

    await check("retained storage contains only a small handle and query configuration", async ({ page }) => {
      await prepare(page);
      await choosePair(page);
      await start(page);
      const saved = await page.evaluate((key) => {
        const raw = sessionStorage.getItem(key);
        return { raw, value: raw && JSON.parse(raw) };
      }, storageKey);
      assert.ok(saved.raw.length <= 2000);
      assert.deepEqual(Object.keys(saved.value).sort(), ["filters", "jobId", "savedAt", "source", "target"]);
      assert.deepEqual(saved.value.filters, defaultFilters);
      assert.equal("authors" in saved.value, false);
      assert.equal("papers" in saved.value, false);
      assert.equal("authors" in saved.value.filters, false);
      assert.equal("papers" in saved.value.filters, false);
    });
  } finally {
    await browser.close();
    const report = {
      checked_at: new Date().toISOString(),
      browser: browser.version(),
      playwright: require("playwright/package.json").version,
      base,
      status: errors.length ? "failed" : "passed",
      checks,
      uncaught_errors: errors,
    };
    fs.writeFileSync(path.join(output, "report.json"), JSON.stringify(report, null, 2) + "\n");
  }
}

async function install(page, name) {
  const calls = [];
  let pathStarts = 0;
  let cancels = 0;
  const gets = new Map();
  const scenario = name.startsWith("reload") ? "reload"
    : name.startsWith("a changed filter") ? "filter-change"
      : name.startsWith("a temporary polling") ? "retry"
        : name.startsWith("Stop cancels") ? "stop-retry"
          : name.startsWith("a retained job") ? "retained-404"
            : "fresh";
  await page.route("**/api/**", async (route) => {
    const request = route.request();
    const u = new URL(request.url());
    const mode = u.searchParams.get("mode");
    assert.equal(mode, "live", `expected explicit live mode on ${u.pathname}`);
    calls.push({ pathname: u.pathname, method: request.method() });
    let status = 200;
    let body;
    if (u.pathname === "/api/dataset") {
      body = {
        source_mode: "live", mode: "live", version, coverage, counts: null,
        capabilities: { live_graph: true, global_centrality: false }, examples: [],
      };
    } else if (u.pathname === "/api/search") {
      const target = /target/i.test(u.searchParams.get("q") || "");
      body = { status: "ok", source: "live", mode: "live", version, results: [person(target ? "9002" : "9001", target ? "Deep Target" : "Deep Source")] };
    } else if (u.pathname.startsWith("/api/person/")) {
      const id = u.pathname.split("/").pop();
      body = { status: "ok", mode: "live", version, person: person(id, id === "9002" ? "Deep Target" : "Deep Source") };
    } else if (u.pathname === "/api/path") {
      pathStarts++;
      body = searching(scenario === "retained-404" ? freshId : retainedId);
    } else if (/^\/api\/search-jobs\/[a-f0-9]{32}$/.test(u.pathname)) {
      const jobId = u.pathname.split("/").pop();
      gets.set(jobId, (gets.get(jobId) || 0) + 1);
      const count = gets.get(jobId);
      if (scenario === "retained-404" && jobId === retainedId) {
        status = 404;
        body = { message: "That retained job has expired." };
      } else if ((scenario === "retry" || scenario === "stop-retry") && count === 1) {
        status = 500;
        body = { message: "Temporary mock failure." };
      } else {
        body = routeData(jobId);
      }
    } else if (/^\/api\/search-jobs\/[a-f0-9]{32}\/cancel$/.test(u.pathname)) {
      cancels++;
      body = { status: "cancelled", mode: "live", version };
    } else {
      body = { status: "ok", mode: "live", version, paths: [], people: [], edges: [] };
    }
    await route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
  });
  return {
    calls,
    get pathStarts() { return pathStarts; },
    get cancels() { return cancels; },
    jobGets: (id) => gets.get(id) || 0,
  };
}

async function retainOnNextNavigation(page, jobId, filters) {
  await page.addInitScript(({ key, saved }) => sessionStorage.setItem(key, JSON.stringify(saved)), {
    key: storageKey,
    saved: { jobId, source: "9001", target: "9002", filters, savedAt: Date.now() },
  });
}

async function prepare(page) {
  await page.goto(`${base}/?mode=live`);
  await page.waitForFunction(() => document.querySelector("#data-mode")?.value === "live");
}

async function choosePair(page) {
  let response = page.waitForResponse((r) => new URL(r.url()).pathname === "/api/search");
  await page.locator("#source-query").fill("Deep Source");
  await response;
  await page.locator("#source-results button").filter({ hasText: "Deep Source" }).first().click();
  response = page.waitForResponse((r) => new URL(r.url()).pathname === "/api/search");
  await page.locator("#target-query").fill("Deep Target");
  await response;
  await page.locator("#target-results button").filter({ hasText: "Deep Target" }).first().click();
}

async function start(page) {
  const response = page.waitForResponse((r) => new URL(r.url()).pathname === "/api/path");
  await page.locator("#find-connection").click();
  await response;
}

main().catch((error) => {
  console.error(error.stack || error);
  process.exitCode = 1;
});
