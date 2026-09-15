/* Mocked browser checks for team-size filters, selected-author preparation,
 * exactness wording, and coauthor/genealogy edge semantics. No request in
 * this file contacts INSPIRE. */
const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const base = process.env.HEP_URL || "http://127.0.0.1:8766";
const output = process.env.HEP_FILTERS_OUTPUT || path.resolve(__dirname, "../docs/browser-filters-prepare");
const version = "live-filter-ui-v1";
const coverage = {
  label: "Temporary Live INSPIRE data",
  description: "Bounded mocked records held in RAM.",
  complete: false,
  partial: true,
  queries: [],
  failures: [],
};
const person = (id, name, mode = "live") => ({
  id,
  name,
  mode,
  indexed: mode === "snapshot",
  queryable: true,
  affiliations: [],
  source_url: `https://inspirehep.net/authors/${id}`,
});
const work = {
  id: "work-1",
  title: "Shared detector paper",
  date: "2024-03-01",
  date_source: "preprint",
  author_count: 18,
  source_url: "https://inspirehep.net/literature/work-1",
  doi: [],
  arxiv: [],
};
const phd = {
  adviser: "9002",
  student: "9001",
  degree: "PhD",
  year: 2020,
  source_record: "institutional:mock-doctoral-record",
  source_kind: "institutional_historical_supplement",
  source_url: "https://inspirehep.net/literature/mock-doctoral-record",
};

async function main() {
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    ...(process.env.HEP_BROWSER_EXECUTABLE
      ? { executablePath: process.env.HEP_BROWSER_EXECUTABLE }
      : {}),
  });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    acceptDownloads: true,
  });
  const page = await context.newPage();
  const pageErrors = [];
  const prepareCalls = [];
  let failOneWarmup = true;
  page.on("pageerror", (error) => pageErrors.push(error.message));

  await page.route("**/api/**", async (route) => {
    const request = route.request();
    const u = new URL(request.url());
    const mode = u.searchParams.get("mode");
    assert.ok(mode === "live" || mode === "snapshot", `missing mode on ${u.pathname}`);
    let status = 200;
    let body;
    if (u.pathname === "/api/dataset") {
      body = {
        source_mode: mode,
        mode,
        version: mode === "live" ? version : "snapshot-filter-ui-v1",
        coverage,
        examples: [],
        capabilities: { live_graph: mode === "live", global_centrality: false },
      };
    } else if (u.pathname === "/api/search") {
      const q = (u.searchParams.get("q") || "").toLowerCase();
      const id = q.includes("third") ? "9003" : q.includes("target") ? "9002" : "9001";
      const name = id === "9003" ? "Genealogy Target" : id === "9002" ? "Prepared Target" : "Prepared Source";
      body = { status: "ok", source: mode, mode, version, results: [person(id, name, mode)] };
    } else if (u.pathname.startsWith("/api/person/")) {
      const id = u.pathname.split("/").pop();
      const name = id === "9003" ? "Genealogy Target" : id === "9002" ? "Prepared Target" : "Prepared Source";
      body = { status: "ok", mode, version, person: person(id, name, mode), collaborators: [], advisers: [], students: [], coverage, filters: requestFilters(u) };
    } else if (u.pathname === "/api/prepare") {
      prepareCalls.push({ method: request.method(), url: u });
      assert.equal(request.method(), "POST");
      for (const key of ["person", "min_authors", "max_authors", "min_shared", "year_start", "year_end", "genealogy"])
        assert.equal(u.searchParams.has(key), true, `prepare omitted ${key}`);
      if (u.searchParams.get("person") === "9002" && failOneWarmup) {
        failOneWarmup = false;
        status = 503;
        body = { status: "upstream_unavailable", message: "Mock warm-up failure" };
      } else body = { status: "prepared", mode, person: u.searchParams.get("person"), filters: requestFilters(u) };
    } else if (u.pathname === "/api/path") {
      const source = u.searchParams.get("source");
      const target = u.searchParams.get("target");
      const genealogyOnly = target === "9003";
      const edge = genealogyOnly
        ? { source, target, types: ["phd"], shared_works: 0, works: [], phd: [{ ...phd, adviser: source, student: target }] }
        : { source, target, types: ["coauthor"], shared_works: 1, works: [work], phd: [phd] };
      body = {
        status: "ok",
        job_id: "cccccccccccccccccccccccccccccccc",
        can_continue: true,
        mode,
        version,
        exact: false,
        exact_for_retrieved_graph: true,
        global_shortest_proven: false,
        filters: requestFilters(u),
        coverage,
        paths: [{
          hops: 1,
          people: [person(source, "Prepared Source"), person(target, genealogyOnly ? "Genealogy Target" : "Prepared Target")],
          edges: [edge],
        }],
      };
    } else if (u.pathname.endsWith("/cancel")) {
      body = { status: "cancelled", mode, version, can_continue: false };
    } else {
      body = { status: "ok", mode, version, paths: [], people: [], edges: [] };
    }
    await route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
  });

  await page.goto(`${base}/?mode=live`);
  await page.waitForFunction(() => document.querySelector("#data-mode")?.value === "live");

  assert.equal(await page.locator("#paper-team-size").inputValue(), "small");
  assert.equal(await page.locator("#min-authors").inputValue(), "1");
  assert.equal(await page.locator("#max-authors").inputValue(), "10");
  assert.equal(new URL(page.url()).searchParams.get("min_authors"), "1");

  await page.locator("#source-query").fill("Prepared Source");
  await page.locator("#source-results button").first().waitFor();
  await page.waitForTimeout(300);
  assert.equal(prepareCalls.length, 0, "typing must not start preparation");
  await page.locator("#source-results button").first().click();
  await waitFor(() => prepareCalls.length === 1);

  await page.locator("#target-query").fill("Prepared Target");
  await page.locator("#target-results button").first().click();
  await waitFor(() => prepareCalls.length === 2);
  for (const call of prepareCalls) {
    assert.equal(call.method, "POST");
    assert.equal(call.url.searchParams.get("min_authors"), "1");
    assert.equal(call.url.searchParams.get("max_authors"), "10");
  }

  await page.locator("#paper-team-size").selectOption("large");
  assert.equal(await page.locator("#min-authors").inputValue(), "11");
  assert.equal(await page.locator("#max-authors").inputValue(), "all");
  assert.match(await page.locator("#filter-summary").innerText(), /large-team papers/i);
  await page.waitForTimeout(200);
  assert.equal(prepareCalls.length, 2, "filter preparation must be debounced");
  await waitFor(() => prepareCalls.length === 4);
  assert.deepEqual(prepareCalls.slice(2).map((x) => x.url.searchParams.get("person")).sort(), ["9001", "9002"]);
  assert.ok(prepareCalls.slice(2).every((x) => x.url.searchParams.get("min_authors") === "11" && x.url.searchParams.get("max_authors") === "all"));

  await page.locator("#paper-team-size").selectOption("all");
  assert.equal(await page.locator("#min-authors").inputValue(), "1");
  assert.equal(await page.locator("#max-authors").inputValue(), "all");
  assert.match(await page.locator("#filter-summary").innerText(), /all paper team sizes/i);
  await waitFor(() => prepareCalls.length === 6);
  assert.ok(prepareCalls.slice(4, 6).every((x) => x.url.searchParams.get("min_authors") === "1" && x.url.searchParams.get("max_authors") === "all"));

  await page.locator("#paper-team-size").dispatchEvent("change");
  await page.waitForTimeout(500);
  assert.equal(prepareCalls.length, 6, "an unchanged filter must not prepare again");

  const pathResponse = page.waitForResponse((response) => new URL(response.url()).pathname === "/api/path");
  await page.locator("#find-connection").click();
  await pathResponse;
  assert.match(await page.locator("#path-meta").innerText(), /verified path.*shortestness not established/i);
  assert.equal(await page.locator("#deep-continue").innerText(), "Continue exact search");
  assert.equal(await page.locator("line.edge.coauthor").count(), 1);
  assert.equal(await page.locator("line.edge.phd").count(), 0);
  assert.equal(await page.locator(".path-route .route-arrow").innerText(), "—");
  await page.locator("line.edge.coauthor").focus();
  await page.locator("line.edge.coauthor").press("Enter");
  const combinedEvidence = await page.locator("#edge-inspector").innerText();
  assert.match(combinedEvidence, /supplemental doctoral record/i);
  assert.match(combinedEvidence, /PHD CONTEXT/);
  assert.equal(await page.locator("#edge-inspector a[href*='mock-doctoral-record']").count(), 1);
  await page.screenshot({ path: path.join(output, "filters-prepare.png"), fullPage: true });

  const downloadWait = page.waitForEvent("download");
  await page.locator("#export-json").click();
  const download = await downloadWait;
  const chunks = [];
  for await (const chunk of await download.createReadStream()) chunks.push(chunk);
  const exported = JSON.parse(Buffer.concat(chunks).toString("utf8"));
  assert.equal(String(exported.filters.min_authors), "1");
  assert.equal(String(exported.path_result.filters.min_authors), "1");
  assert.equal(new URL(page.url()).searchParams.get("min_authors"), "1");

  await page.locator("#target-query").fill("Third target");
  await page.locator("#target-results button").first().click();
  const genealogyResponse = page.waitForResponse((response) => new URL(response.url()).pathname === "/api/path");
  await page.locator("#find-connection").click();
  await genealogyResponse;
  assert.equal(await page.locator("line.edge.coauthor").count(), 0);
  assert.equal(await page.locator("line.edge.phd").count(), 1);
  assert.equal(await page.locator("line.edge.phd").getAttribute("marker-end"), "url(#arrowhead)");
  assert.equal(await page.locator(".path-route .route-arrow").innerText(), "→");
  await page.locator("line.edge.phd").focus();
  await page.locator("line.edge.phd").press("Enter");
  assert.equal(await page.locator("#edge-inspector a[href*='mock-doctoral-record']").count(), 1);

  await page.setViewportSize({ width: 390, height: 844 });
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);

  const beforeSnapshot = prepareCalls.length;
  await page.locator("#data-mode").selectOption("snapshot");
  await page.waitForFunction(() => document.querySelector("#data-mode")?.value === "snapshot");
  await page.locator("#source-query").fill("Prepared Source");
  await page.locator("#source-results button").first().click();
  await page.waitForTimeout(100);
  assert.equal(prepareCalls.length, beforeSnapshot, "Saved demo selection must not call live preparation");

  assert.deepEqual(pageErrors, []);
  fs.writeFileSync(path.join(output, "report.json"), JSON.stringify({
    checked_at: new Date().toISOString(),
    browser: browser.version(),
    base,
    status: "passed",
    prepare_requests: prepareCalls.map(({ method, url }) => ({ method, url: url.toString() })),
    checks: [
      "small large and all paper-team modes map to exact min/max bounds",
      "identity selection prepares both endpoints without keystroke requests",
      "actual filter changes prepare selected endpoints after a debounce",
      "warm-up failure does not block path search or raise a page error",
      "verified continuable path offers Continue exact search",
      "coauthor edge keeps doctoral metadata as supplemental inspector context",
      "genealogy-only edge is dashed directed and explicitly sourced",
      "share URL and JSON export include min_authors",
      "mobile layout has no document overflow",
      "Saved demo selection does not call live preparation"
    ],
    uncaught_errors: pageErrors,
  }, null, 2) + "\n");
  await context.close();
  await browser.close();
  console.log(JSON.stringify({ status: "passed", prepares: prepareCalls.length }));
}

function requestFilters(u) {
  return {
    min_authors: u.searchParams.get("min_authors") || "1",
    max_authors: u.searchParams.get("max_authors") || "10",
    min_shared: u.searchParams.get("min_shared") || "1",
    year_start: u.searchParams.get("year_start") || "",
    year_end: u.searchParams.get("year_end") || "",
    genealogy: u.searchParams.get("genealogy") || "true",
  };
}

async function waitFor(predicate, timeout = 3000) {
  const started = Date.now();
  while (!predicate()) {
    if (Date.now() - started > timeout) throw new Error("Timed out waiting for mocked browser event");
    await new Promise((resolve) => setTimeout(resolve, 20));
  }
}

main().catch((error) => {
  console.error(error.stack || error);
  process.exitCode = 1;
});
