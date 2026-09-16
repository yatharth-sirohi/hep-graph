/* Mocked long-running live-search checks. No request contacts INSPIRE. */
const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const base = process.env.HEP_URL || "http://127.0.0.1:8766";
const output = process.env.HEP_DEEP_OUTPUT || path.resolve(__dirname, "../../../work/audit/deep-search/browser");
const version = "live-deep-v1";
const coverage = { label: "Temporary Live INSPIRE data", partial: true, retrieved: { people: 2, works: 1 } };
const person = (id, name) => ({ id, name, indexed: false, queryable: true, mode: "live", affiliations: [] });
const routeData = {
  status: "ok", mode: "live", version, exact: false, exact_for_retrieved_graph: true,
  global_shortest_proven: false, filters: { min_authors: 1, max_authors: 10, min_shared: 1, genealogy: true }, coverage,
  paths: [{ hops: 1, people: [person("9001", "Deep Source"), person("9002", "Deep Target")], edges: [{ source: "9001", target: "9002", types: ["coauthor"], shared_works: 1, works: [{ id: "deep-work", title: "Retrieved work", year: 2024, date_source: "preprint", author_count: 2, authors: ["9001", "9002"], source_url: "https://inspirehep.net/literature/deep-work" }] }] }],
};
const progress = (people = 24, works = 76, stage = "retrieving neighboring authors") => ({ people_explored: people, works_retrieved: works, elapsed_seconds: 7, stage });

async function main() {
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({ headless: true, ...(process.env.HEP_BROWSER_EXECUTABLE ? { executablePath: process.env.HEP_BROWSER_EXECUTABLE } : {}) });
  const checks = [];
  const errors = [];
  const check = async (name, fn) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, acceptDownloads: true });
    const page = await context.newPage();
    page.on("pageerror", (error) => errors.push(error.message));
    try {
      const harness = await install(page, name);
      await prepare(page);
      await fn(page, harness);
      checks.push({ name, status: "passed" });
      console.log("PASS", name);
    } finally {
      await context.close();
    }
  };

  await check("progress reports explored people works elapsed time and stage", async (page) => {
    await choosePair(page);
    await start(page);
    await page.locator("#deep-progress").waitFor({ state: "visible" });
    assert.equal(await page.locator("#deep-progress").isVisible(), true);
    assert.match(await page.locator("#deep-summary").innerText(), /24 people explored.*76 works retrieved.*7s elapsed.*retrieving neighboring authors/i);
    await page.screenshot({ path: path.join(output, "deep-progress.png"), fullPage: true });
  });

  await check("an early verified route appears while live search continues", async (page) => {
    await choosePair(page);
    await start(page);
    await page.locator("#deep-progress").waitFor({ state: "visible" });
    await page.locator("#path-cards .path-card").waitFor();
    assert.equal(await page.locator("#deep-progress").isVisible(), true);
    assert.match(await page.locator("#path-meta").innerText(), /exact for retrieved graph|Live INSPIRE/i);
  });

  await check("completed live job renders its terminal route", async (page) => {
    await choosePair(page);
    await start(page);
    await page.locator("#path-cards .path-card").waitFor();
    assert.equal(await page.locator("#find-connection").isDisabled(), false);
    assert.equal(await page.locator("#deep-progress").isVisible(), false);
  });

  await check("resource limit preserves evidence and offers continuation", async (page, h) => {
    await choosePair(page);
    await start(page);
    await page.locator("#deep-continue").waitFor({ state: "visible" });
    assert.equal(await page.locator("#path-cards .path-card").count(), 1);
    await page.locator("#deep-continue").click();
    await page.locator("#deep-continue").waitFor({ state: "hidden" });
    assert.equal(await page.locator("#path-cards .path-card").count(), 1);
    assert.ok(h.calls.some((x) => x.pathname.endsWith("/continue") && x.method === "POST"));
  });

  await check("stop immediately preserves an incomplete result and cancels once", async (page, h) => {
    await choosePair(page);
    await start(page);
    await page.locator("#deep-stop").click();
    assert.equal(await page.locator("#deep-progress").isVisible(), false);
    assert.match(await page.locator("#path-message").innerText(), /stopped|incomplete/i);
    await page.waitForTimeout(1700);
    assert.equal(h.calls.filter((x) => x.pathname.endsWith("/cancel")).length, 1);
    assert.equal(h.polls, 0);
  });

  await check("bounded no-route completion never claims exhaustive no path", async (page) => {
    await choosePair(page);
    await start(page);
    await page.locator("#path-message").waitFor({ state: "visible" });
    assert.match(await page.locator("#path-message").innerText(), /incomplete|bounded|retrieved graph/i);
    assert.doesNotMatch(await page.locator("#path-message").innerText(), /no documented connection was found/i);
  }, "incomplete");

  await check("upstream failure is stated as a live-source failure", async (page) => {
    await choosePair(page);
    await start(page);
    await page.locator("#path-message").waitFor({ state: "visible" });
    assert.match(await page.locator("#path-message").innerText(), /temporarily unavailable|live INSPIRE/i);
  }, "upstream");

  await check("not-found terminal status remains explicit", async (page) => {
    await choosePair(page);
    await start(page);
    await page.locator("#path-message").waitFor({ state: "visible" });
    assert.match(await page.locator("#path-message").innerText(), /not found|selected researcher/i);
  }, "not-found");

  await check("delayed poll cannot restore a result after mode changes", async (page, h) => {
    await choosePair(page);
    await start(page);
    await h.pollSeen;
    await page.locator("#data-mode").selectOption("snapshot");
    await page.waitForFunction(() => document.querySelector("#data-mode")?.value === "snapshot");
    h.releasePoll();
    await page.waitForTimeout(100);
    assert.equal(await page.locator("#connection-results").isVisible(), false);
    assert.equal(await page.locator("#deep-progress").isVisible(), false);
    assert.equal(h.polls, 1);
  });

  await check("delayed initial response is cancelled after mode changes", async (page, h) => {
    await choosePair(page);
    const pathSeen = h.pathSeen;
    await page.locator("#find-connection").click();
    await pathSeen;
    await page.locator("#data-mode").selectOption("snapshot");
    await page.waitForFunction(() => document.querySelector("#data-mode")?.value === "snapshot");
    h.releaseInitial();
    await h.cancelSeen;
    assert.equal(await page.locator("#connection-results").isVisible(), false);
  }, "initial-delay");

  await check("filter changes cancel an active job and stop polling", async (page, h) => {
    await choosePair(page);
    await start(page);
    await page.locator("#paper-team-size").selectOption("large");
    assert.equal(await page.locator("#deep-progress").isVisible(), false);
    await page.waitForTimeout(1700);
    assert.equal(h.calls.filter((x) => x.pathname.endsWith("/cancel")).length, 1);
    assert.equal(h.polls, 0);
  });

  await check("selection changes cancel an active job without stale evidence", async (page, h) => {
    await choosePair(page);
    await start(page);
    await page.locator('.clear-picker[data-clear="source"]').click();
    assert.equal(await page.locator("#deep-progress").isVisible(), false);
    assert.equal(await page.locator("#connection-results").isVisible(), false);
    await page.waitForTimeout(1700);
    assert.equal(h.calls.filter((x) => x.pathname.endsWith("/cancel")).length, 1);
    assert.equal(h.polls, 0);
  });

  await browser.close();
  const report = { checked_at: new Date().toISOString(), browser: browser.version(), playwright: require("playwright/package.json").version, base, status: errors.length ? "failed" : "passed", checks, uncaught_errors: errors, artifacts: ["deep-progress.png", "report.json"] };
  fs.writeFileSync(path.join(output, "report.json"), JSON.stringify(report, null, 2) + "\n");
  process.exitCode = report.status === "passed" ? 0 : 1;
}

async function install(page, name) {
  const scenario = name === "bounded no-route completion never claims exhaustive no path" ? "incomplete" :
    name === "upstream failure is stated as a live-source failure" ? "upstream" :
      name === "not-found terminal status remains explicit" ? "not-found" :
        name === "delayed initial response is cancelled after mode changes" ? "initial-delay" : name;
  const calls = [];
  let polls = 0;
  let releasePoll;
  let releaseInitial;
  let seePoll;
  let seePath;
  let seeCancel;
  const pollSeen = new Promise((resolve) => { seePoll = resolve; });
  const pathSeen = new Promise((resolve) => { seePath = resolve; });
  const cancelSeen = new Promise((resolve) => { seeCancel = resolve; });
  await page.route("**/api/**", async (route) => {
    const u = new URL(route.request().url());
    const mode = u.searchParams.get("mode");
    assert.ok(mode === "live" || mode === "snapshot", `missing mode on ${u.pathname}`);
    calls.push({ pathname: u.pathname, method: route.request().method(), mode });
    let body = {};
    if (u.pathname === "/api/dataset") {
      body = { source_mode: mode, mode, version: mode === "live" ? version : "snapshot-test-v1", coverage, counts: null, capabilities: { live_graph: true, global_centrality: false }, examples: [] };
    } else if (u.pathname === "/api/search") {
      body = { status: "ok", source: "live", mode, version, results: [person(u.searchParams.get("q")?.toLowerCase().includes("target") ? "9002" : "9001", u.searchParams.get("q")?.toLowerCase().includes("target") ? "Deep Target" : "Deep Source")] };
    } else if (u.pathname === "/api/path") {
      seePath();
      if (scenario === "initial-delay") {
        await new Promise((resolve) => { releaseInitial = resolve; });
      }
      body = { status: "searching", job_id: "deep-job-1", mode: "live", version, filters: routeFilters(), coverage, progress: progress(), can_continue: false, paths: [] };
      // The server publishes an early route as paths + best_route on a versioned state.
      if (scenario === "an early verified route appears while live search continues") body = { ...body, paths: routeData.paths, best_route: { route_id: "r-deep", hops: 1, alternatives: 0, exact: false, found_at_seconds: 2.5, version }, route_status: "verified_route_found", sequence_number: 2 };
      if (scenario === "completed live job renders its terminal route") body = { ...routeData, job_id: "deep-job-1" };
      if (scenario === "incomplete") body = { status: "search_incomplete", job_id: "deep-job-1", mode: "live", version, filters: routeFilters(), coverage, progress: progress(), paths: [], can_continue: false };
      if (scenario === "upstream") body = { status: "upstream_unavailable", job_id: "deep-job-1", mode: "live", version, message: "Live INSPIRE is temporarily unavailable.", paths: [], can_continue: false };
      if (scenario === "not-found") body = { status: "not_found", job_id: "deep-job-1", mode: "live", version, message: "The selected researcher was not found by the active source.", paths: [], can_continue: false };
    } else if (u.pathname === "/api/search-jobs/deep-job-1") {
      polls++;
      seePoll();
      if (scenario === "delayed poll cannot restore a result after mode changes") await new Promise((resolve) => { releasePoll = resolve; });
      body = { status: "ok", ...routeData, job_id: "deep-job-1" };
      if (scenario === "progress reports explored people works elapsed time and stage") body = { status: "searching", job_id: "deep-job-1", mode: "live", version, progress: progress(31, 92, "checking documented ties"), coverage, paths: [], can_continue: false };
      if (scenario === "an early verified route appears while live search continues") body = { status: "searching", job_id: "deep-job-1", mode: "live", version, progress: progress(31, 92, "checking documented ties"), coverage, paths: routeData.paths, best_route: { route_id: "r-deep", hops: 1, alternatives: 0, exact: false, found_at_seconds: 2.5, version }, route_status: "verified_route_found", sequence_number: 3, can_continue: false };
      if (scenario === "resource limit preserves evidence and offers continuation") body = { status: "resource_limit", job_id: "deep-job-1", mode: "live", version, progress: progress(83, 210, "resource limit reached"), coverage, paths: routeData.paths, can_continue: true };
    } else if (u.pathname === "/api/search-jobs/deep-job-1/continue") {
      body = { status: "searching", job_id: "deep-job-1", mode: "live", version, progress: progress(88, 224, "continuing bounded exploration"), coverage, paths: [], can_continue: false };
    } else if (u.pathname === "/api/search-jobs/deep-job-1/cancel") {
      seeCancel();
      body = { status: "cancelled", job_id: "deep-job-1", mode: "live", version, message: "The live search was cancelled.", paths: [], can_continue: false };
    } else if (u.pathname.startsWith("/api/person/")) {
      const id = u.pathname.split("/").pop();
      body = { status: "ok", mode, version, person: person(id, id === "9002" ? "Deep Target" : "Deep Source"), queryable: mode === "live", indexed: mode === "snapshot" };
    } else {
      body = { status: "ok", mode, version, paths: [], people: [], edges: [] };
    }
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) });
  });
  return { calls, get polls() { return polls; }, pollSeen, pathSeen, cancelSeen, releasePoll: () => releasePoll?.(), releaseInitial: () => releaseInitial?.() };
}

function routeFilters() { return { min_authors: 1, max_authors: 10, min_shared: 1, genealogy: true }; }
async function prepare(page) { await page.goto(`${base}/?mode=live`); await page.waitForFunction(() => document.querySelector("#data-mode")?.value === "live"); }
async function choosePair(page) {
  await page.locator("#source-query").fill("Deep Source");
  await page.locator("#source-results button").filter({ hasText: "Deep Source" }).first().click();
  await page.locator("#target-query").fill("Deep Target");
  await page.locator("#target-results button").filter({ hasText: "Deep Target" }).first().click();
}
async function start(page) { const response = page.waitForResponse((r) => new URL(r.url()).pathname === "/api/path"); await page.locator("#find-connection").click(); await response; }

main().catch((error) => { console.error(error.stack || error); process.exitCode = 1; });
