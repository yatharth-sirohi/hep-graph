/* Mocked Live INSPIRE browser checks.
 * Run against a local static service with Playwright installed:
 *   node tests/browser_live.cjs
 * No request in this file contacts INSPIRE; every /api response is intercepted.
 */
const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const base = process.env.HEP_URL || "http://127.0.0.1:8765";
const output =
  process.env.HEP_BROWSER_OUTPUT ||
  path.resolve(__dirname, "../docs/browser-live");
const checks = [];
const errors = [];
const version = "live-inspire-v1";
const coverage = {
  label: "Temporary Live INSPIRE data",
  description: "Bounded author and retrieved-work data held in RAM for this query only.",
  complete: false,
  queries: ["mocked live author query"],
  failures: [],
};

const person = (id, name) => ({
  id,
  name,
  aliases: [],
  affiliations: ["Mock Institute"],
  orcid: null,
  profile_status: "profile",
  source_url: `https://inspirehep.net/authors/${id}`,
  indexed: false,
  queryable: true,
  mode: "live",
});

const profile = (id, name, summary = false) => ({
  status: "ok",
  mode: "live",
  version,
  person: person(id, name),
  indexed: false,
  queryable: true,
  indexed_publications: null,
  eligible_publications: null,
  coauthor_count: null,
  combined_degree: null,
  advisers: [],
  students: [],
  collaborators: [],
  reachability: null,
  coverage,
  ...(summary ? { summary: true } : {}),
});

const dataset = (mode) => mode === "snapshot"
  ? {
      source_mode: "snapshot",
      mode: "snapshot",
      version: "snapshot-test-v1",
      created_at: "2026-09-14T00:00:00Z",
      coverage: { label: "Saved demo", description: "A deterministic local snapshot.", complete: false, queries: [], failures: [] },
      examples: [{ label: "Saved example", source: "1", target: "2" }],
    }
  : { source_mode: "live", mode: "live", version, created_at: null, coverage, examples: [], counts: null, capabilities: { live_graph: true, global_centrality: false } };

const livePath = (source, target, direct = false) => ({
  status: "ok",
  mode: "live",
  version,
  exact: false,
  exact_for_retrieved_graph: true,
  global_shortest_proven: direct,
  retrieval: { people: 2, works: 1, truncated: false },
  filters: { min_authors: 1, max_authors: 10, min_shared: 1, year_start: null, year_end: null, genealogy: true },
  coverage,
  paths: [{
    hops: 1,
    people: [person(source, "Live Source"), person(target, "Live Target")],
    edges: [{ source, target, types: ["coauthor"], shared_works: 1, works: [{ id: "live-work-1", title: "Retrieved work", year: 2024, date: "2024-01-01", date_source: "preprint", author_count: 2, authors: [source, target], source_url: "https://inspirehep.net/literature/live-work-1", doi: [], arxiv: [] }] }],
  }],
});

async function main() {
  const browser = await chromium.launch({
    headless: true,
    ...(process.env.HEP_BROWSER_EXECUTABLE ? { executablePath: process.env.HEP_BROWSER_EXECUTABLE } : {}),
  });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, acceptDownloads: true });
  const page = await context.newPage();
  page.on("pageerror", (error) => errors.push(error.message));
  const apiRequests = [];
  const personRequests = [];
  let delayedPathRelease = null;
  let delayedProfileRelease = null;
  await page.route("**/api/**", async (route) => {
    const requestUrl = new URL(route.request().url());
    apiRequests.push(requestUrl);
    const mode = requestUrl.searchParams.get("mode");
    assert.ok(mode === "live" || mode === "snapshot", `missing mode on ${requestUrl.pathname}`);
    let body;
    if (requestUrl.pathname === "/api/dataset") {
      body = dataset(mode);
    } else if (requestUrl.pathname === "/api/search") {
      const q = requestUrl.searchParams.get("q") || "";
      if (mode === "snapshot") body = { status: "not_found", source: "snapshot", results: [], version: "snapshot-test-v1" };
      else if (q.toLowerCase().includes("partial")) {
        body = { status: "search_incomplete", source: "live", mode, version, message: "Live INSPIRE returned a bounded partial result.", results: [{ ...person("9001", "Partial Live Researcher"), indexed: false, queryable: true }] };
      } else {
        const resultPerson = q.toLowerCase().includes("target")
          ? person("9002", "Live Target")
          : person("9001", "Live Source");
        body = { status: "ok", source: "live", mode, version, results: [resultPerson], message: "Live result is queryable for this session only." };
      }
    } else if (requestUrl.pathname.startsWith("/api/person/")) {
      const id = requestUrl.pathname.split("/").pop();
      personRequests.push({ id, mode });
      if (delayedProfileRelease) await new Promise((resolve) => { delayedProfileRelease = resolve; });
      body = profile(id, id === "9002" ? "Live Target" : "Live Source", requestUrl.searchParams.get("summary") === "1");
    } else if (requestUrl.pathname === "/api/path") {
      if (delayedPathRelease) await new Promise((resolve) => { delayedPathRelease = resolve; });
      const source = requestUrl.searchParams.get("source") || "9001";
      const target = requestUrl.searchParams.get("target") || "9002";
      body = livePath(source, target, source === target);
    } else if (requestUrl.pathname === "/api/centrality") {
      body = { status: "unavailable", mode: "live", version, message: "Global centrality requires a complete retrieved graph. Switch to Saved demo for centrality.", coverage, filters: {} };
    } else if (requestUrl.pathname.startsWith("/api/neighborhood/")) {
      body = { status: "ok", mode: "live", version, people: [], edges: [], truncated: false, coverage, filters: {} };
    } else {
      body = { status: "not_found", mode, version };
    }
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) });
  });

  const check = async (name, fn) => {
    await fn();
    checks.push(name);
    console.log("PASS", name);
  };

  await page.goto(`${base}/?mode=live`);
  await page.locator("#mode-description").waitFor();
  await page.waitForFunction(() => document.querySelector("#data-mode")?.value === "live");

  await check("live mode source and ephemeral coverage are visible", async () => {
    assert.equal(await page.locator("#data-mode").inputValue(), "live");
    assert.match(await page.locator("#coverage-text").innerText(), /temporary|RAM|partial/i);
    assert.match(await page.locator("#snapshot-label").innerText(), /Live INSPIRE/i);
    assert.equal(await page.locator(".example-picker").isHidden(), true);
  });

  await check("live search returns a queryable Live INSPIRE identity", async () => {
    await page.locator("#source-query").fill("Live Source");
    const option = page.locator("#source-results button").filter({ hasText: "Live Source" });
    await option.first().waitFor();
    assert.match(await option.first().innerText(), /Live INSPIRE/i);
    await option.first().click();
    assert.match(await page.locator("#source-selected").innerText(), /Live INSPIRE/i);
    assert.equal(await page.locator("#source-selected").locator(".status.live").count(), 1);
  });

  await check("queryable live identities can produce a live path", async () => {
    await page.locator("#target-query").fill("Live Target");
    await page.locator("#target-results button").filter({ hasText: "Live Target" }).first().click();
    const pathResponse = page.waitForResponse((response) => {
      const u = new URL(response.url());
      return u.pathname === "/api/path" && u.searchParams.get("mode") === "live";
    });
    await page.locator("#find-connection").click();
    const response = await pathResponse;
    const data = await response.json();
    assert.equal(data.mode, "live");
    assert.equal(data.global_shortest_proven, false);
    assert.equal(data.exact_for_retrieved_graph, true);
    assert.match(await page.locator("#path-meta").innerText(), /Live INSPIRE|verified path/i);
    const downloadWait = page.waitForEvent("download");
    await page.locator("#export-json").click();
    const download = await downloadWait;
    const stream = await download.createReadStream();
    const chunks = [];
    for await (const chunk of stream) chunks.push(chunk);
    const exported = JSON.parse(Buffer.concat(chunks).toString("utf8"));
    assert.equal(exported.mode, "live");
    assert.match(exported.path_result.coverage.label, /Live INSPIRE/i);
  });

  await check("direct live identity path reports its bounded proof", async () => {
    await page.locator("#target-query").fill("Live Source");
    await page.locator("#target-results button").filter({ hasText: "Live Source" }).first().click();
    const pathResponse = page.waitForResponse((response) => {
      const u = new URL(response.url());
      return u.pathname === "/api/path" && u.searchParams.get("mode") === "live";
    });
    await page.locator("#find-connection").click();
    const data = await (await pathResponse).json();
    assert.equal(data.global_shortest_proven, true);
    assert.match(await page.locator("#path-meta").innerText(), /exact shortest path/i);
  });

  await check("mode change invalidates a delayed live path", async () => {
    const request = page.waitForRequest((r) => {
      const u = new URL(r.url());
      return u.pathname === "/api/path" && u.searchParams.get("mode") === "live";
    });
    // The current live selections remain after the preceding path result.
    const response = page.waitForResponse((r) => new URL(r.url()).pathname === "/api/dataset" && new URL(r.url()).searchParams.get("mode") === "snapshot");
    delayedPathRelease = () => {};
    await page.locator("#find-connection").click();
    await request;
    await page.locator("#data-mode").selectOption("snapshot");
    await response;
    assert.equal(await page.locator("#connection-results").isVisible(), false);
    delayedPathRelease();
    delayedPathRelease = null;
    await page.waitForTimeout(100);
    assert.equal(await page.locator("#connection-results").isVisible(), false);
  });

  await check("incomplete live search stays explicit and selectable", async () => {
    await page.locator("#data-mode").selectOption("live");
    await page.waitForFunction(() => document.querySelector("#data-mode")?.value === "live");
    await page.locator("#source-query").fill("partial");
    await page.locator("#source-results .search-result").filter({ hasText: "bounded partial" }).waitFor();
    assert.match(await page.locator("#source-results").innerText(), /bounded partial/i);
    assert.equal(await page.locator("#source-results button").count(), 1);
  });

  await check("live centrality remains unavailable with a saved-demo explanation", async () => {
    await page.locator('[data-tab="centrality"]').click();
    await page.locator("#load-centrality").click();
    await page.locator("#centrality-status").waitFor({ state: "visible" });
    assert.match(await page.locator("#centrality-status").innerText(), /global centrality|Saved demo/i);
    assert.equal(await page.locator("#centrality-results").isVisible(), false);
  });

  await check("a delayed live profile cannot repopulate state after a mode switch", async () => {
    await page.locator('[data-tab="connections"]').click();
    await page.locator("#source-query").fill("Live Source");
    await page.locator("#source-results button").filter({ hasText: "Live Source" }).first().click();
    await page.locator("#target-query").fill("Live Target");
    await page.locator("#target-results button").filter({ hasText: "Live Target" }).first().click();
    const pathResponse = page.waitForResponse((response) => {
      const u = new URL(response.url());
      return u.pathname === "/api/path" && u.searchParams.get("mode") === "live";
    });
    await page.locator("#find-connection").click();
    await pathResponse;
    await page.waitForFunction(() => !document.querySelector("#find-connection").disabled);
    const before = personRequests.length;
    delayedProfileRelease = () => {};
    const profileRequest = page.waitForRequest((request) => {
      const u = new URL(request.url());
      return u.pathname === "/api/person/9001" && u.searchParams.get("mode") === "live";
    });
    await page.locator("#path-cards .person-link").first().click();
    await profileRequest;
    const datasetResponse = page.waitForResponse((response) => {
      const u = new URL(response.url());
      return u.pathname === "/api/dataset" && u.searchParams.get("mode") === "snapshot";
    });
    await page.locator("#data-mode").selectOption("snapshot");
    await datasetResponse;
    assert.equal(await page.locator("#person-panel").isVisible(), false);
    delayedProfileRelease();
    delayedProfileRelease = null;
    await page.waitForTimeout(100);
    assert.equal(await page.locator("#person-panel").isVisible(), false);
    assert.equal(personRequests.length, before + 1, "stale profile response must not trigger a new-mode profile fetch");
    const liveDataset = page.waitForResponse((response) => {
      const u = new URL(response.url());
      return u.pathname === "/api/dataset" && u.searchParams.get("mode") === "live";
    });
    await page.locator("#data-mode").selectOption("live");
    await liveDataset;
  });

  await check("mode change invalidates live selections and results", async () => {
    await page.locator('[data-tab="connections"]').click();
    await page.locator("#data-mode").selectOption("snapshot");
    await page.waitForFunction(() => document.querySelector("#data-mode")?.value === "snapshot");
    assert.equal(await page.locator("#source-selected").isVisible(), false);
    assert.equal(await page.locator("#target-selected").isVisible(), false);
    assert.equal(await page.locator("#connection-results").isVisible(), false);
    assert.match(new URL(page.url()).searchParams.get("mode"), /snapshot/);
    assert.equal(new URL(page.url()).searchParams.has("version"), true);
  });

  await check("version-only legacy links restore Saved demo mode", async () => {
    const datasetResponse = page.waitForResponse((response) => {
      const u = new URL(response.url());
      return u.pathname === "/api/dataset" && u.searchParams.get("mode") === "snapshot";
    });
    await page.goto(`${base}/?version=legacy-snapshot-v0`);
    await datasetResponse;
    await page.waitForFunction(() => document.querySelector("#data-mode")?.value === "snapshot");
    assert.match(await page.locator("#version-warning").innerText(), /legacy-snapshot-v0|currently has/i);
    assert.equal(new URL(page.url()).searchParams.get("mode"), "snapshot");
  });

  for (const u of apiRequests) assert.ok(u.searchParams.has("mode"), `mode missing on ${u}`);
  assert.deepEqual(errors, []);
  fs.mkdirSync(output, { recursive: true });
  await page.screenshot({
    path: path.join(output, "browser-live.png"),
    fullPage: true,
  });
  fs.writeFileSync(
    path.join(output, "browser-live-report.json"),
    JSON.stringify({
      checked_at: new Date().toISOString(),
      browser: browser.version(),
      playwright: require("playwright/package.json").version,
      base,
      status: "passed",
      checks,
      api_requests: apiRequests.map((u) => u.toString()),
      person_requests: personRequests,
      uncaught_errors: errors,
      artifacts: ["browser-live.png", "browser-live-report.json"],
    }, null, 2) + "\n",
  );
  await context.close();
  await browser.close();
  console.log(JSON.stringify({ status: "passed", checks: checks.length, checks, api_requests: apiRequests.length }));
}

main().catch((error) => {
  console.error(error.stack || error);
  process.exitCode = 1;
});
