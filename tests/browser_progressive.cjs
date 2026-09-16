/* Progressive route delivery in the browser: mocked, versioned job states.
   No request contacts INSPIRE. Run against a server that only serves the UI. */
const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const base = process.env.HEP_URL || "http://127.0.0.1:8766";
const output = process.env.HEP_PROGRESSIVE_OUTPUT || path.resolve(__dirname, "../../../work/audit/progressive/browser");
const version = "live-deep-v1";
const coverage = { label: "Temporary Live INSPIRE data", partial: true, retrieved: { people: 12, works: 40 } };
const filters = { min_authors: 1, max_authors: 10, min_shared: 1, genealogy: true };
const person = (id, name) => ({ id, name, indexed: false, queryable: true, mode: "live", affiliations: [] });
const names = { 9001: "Deep Source", 9002: "Deep Target", 9101: "Xavier Mid", 9102: "Yara Mid", 9103: "Zed Mid", 9201: "Pia Mid", 9202: "Quinn Mid" };
const route = (routeId, ...ids) => ({
  route_id: routeId, hops: ids.length - 1, people: ids.map((id) => person(id, names[id])),
  edges: ids.slice(1).map((id, i) => ({ source: ids[i], target: id, types: ["coauthor"], shared_works: 1,
    works: [{ id: `w-${ids[i]}-${id}`, title: `Work ${ids[i]}–${id}`, year: 2024, date_source: "preprint", author_count: 2, authors: [ids[i], id], source_url: `https://inspirehep.net/literature/w-${ids[i]}-${id}` }] })),
});
const LONG = route("r-long", "9001", "9101", "9102", "9103", "9002");   // 4 hops
const SHORT = route("r-short", "9001", "9201", "9202", "9002");         // 3 hops
const progress = (n) => ({ people_explored: 10 * n, works_retrieved: 30 * n, elapsed_seconds: 3 * n, stage: "prove_shortest", requests: n });
const metrics = (extra = {}) => ({ elapsed_seconds: 12, time_to_first_verified_path: 6.2, time_to_best_route: 6.2, time_to_exact_proof: null, improvements: 0, first_hops: 4, best_hops: 4, ...extra });
const best = (r, exact = false) => ({ route_id: r.route_id, hops: r.hops, alternatives: 0, exact, found_at_seconds: 6.2, version });
const state = (sequence, status, routeStatus, paths, extra = {}) => ({
  status, job_id: "0123456789abcdef0123456789abcdef", mode: "live", version, filters, coverage, exact: false, can_continue: false,
  paths, best_route: paths.length ? best(paths[0], routeStatus === "exact_route_proven") : null,
  route_status: routeStatus, sequence_number: sequence, progress: progress(sequence), metrics: metrics(),
  events: [{ sequence_number: 0, type: "search_started", at_seconds: 0 }], ...extra,
});
const NO_ROUTE = state(1, "searching", "searching_no_path", []);
const FOUND_LONG = state(2, "searching", "verified_route_found", [LONG]);
const FOUND_LONG_AGAIN = state(3, "searching", "verified_route_found", [LONG]);
const FOUND_SHORT = state(4, "searching", "verified_route_found", [SHORT], { metrics: metrics({ improvements: 1, best_hops: 3, time_to_best_route: 12 }) });
const PROVEN_SHORT = state(5, "ok", "exact_route_proven", [SHORT], { global_shortest_proven: true, bounds: { lower: 3, upper: 3, proven: true },
  metrics: metrics({ improvements: 1, best_hops: 3, time_to_best_route: 12, time_to_exact_proof: 31.4 }) });

const scenarios = {
  "first verified route appears at once and the exact search continues": [FOUND_LONG, FOUND_LONG_AGAIN],
  "a shorter route is announced and never swapped in by itself": [FOUND_LONG, FOUND_LONG_AGAIN, FOUND_SHORT],
  "a stale version is ignored and the proof is offered, not forced": [FOUND_LONG, FOUND_SHORT, FOUND_LONG, PROVEN_SHORT],
  "stop keeps the verified route on screen": [FOUND_LONG, FOUND_LONG_AGAIN],
  "a refresh restores the server's best route": [FOUND_LONG, PROVEN_SHORT],
  "the export names the displayed route and the delivery state": [FOUND_LONG, FOUND_SHORT],
  "an equal-length route is not announced": [FOUND_LONG, state(3, "searching", "verified_route_found", [route("r-twin", "9001", "9101", "9202", "9103", "9002"), LONG], { metrics: metrics() })],
  // A job restarted on another server proves a longer route than the one on screen.
  "a proof about a longer route does not label the shown route exact": [FOUND_SHORT, state(5, "ok", "exact_route_proven", [LONG], { global_shortest_proven: true })],
  "withdrawing a route that is not on screen leaves the screen alone": [FOUND_LONG, FOUND_SHORT,
    state(5, "searching", "searching_no_path", [], { events: [{ sequence_number: 0, type: "search_started", at_seconds: 0 }, { sequence_number: 5, type: "route_withdrawn", at_seconds: 14, previous_hops: 3, previous_route_id: "r-short" }] })],
  "withdrawing the shown route replaces it and says why": [FOUND_LONG,
    state(3, "searching", "verified_route_found", [SHORT], { events: [{ sequence_number: 0, type: "search_started", at_seconds: 0 }, { sequence_number: 3, type: "route_withdrawn", at_seconds: 14, hops: 3, route_id: "r-short", previous_hops: 4, previous_route_id: "r-long" }] }),
    state(4, "searching", "verified_route_found", [SHORT])],
};

async function main() {
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({ headless: true, ...(process.env.HEP_BROWSER_EXECUTABLE ? { executablePath: process.env.HEP_BROWSER_EXECUTABLE } : {}) });
  const checks = [];
  const errors = [];
  const check = async (name, fn) => {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, acceptDownloads: true });
    const page = await context.newPage();
    page.on("pageerror", (error) => errors.push(`${name}: ${error.message}`));
    try {
      const harness = await install(page, scenarios[name]);
      await prepare(page);
      await fn(page, harness);
      checks.push({ name, status: "passed" });
      console.log("PASS", name);
    } catch (error) {
      checks.push({ name, status: "failed", error: error.message });
      console.log("FAIL", name, "\n ", error.message);
      errors.push(`${name}: ${error.message}`);
    } finally {
      await context.close();
    }
  };
  const cardHops = (page) => page.locator("#path-cards .path-card .edge-summary").first().innerText();
  const routeState = (page) => page.locator("#connection-results").getAttribute("data-route-state");

  await check("first verified route appears at once and the exact search continues", async (page, h) => {
    await choosePair(page);
    await start(page);
    await page.locator("#path-cards .path-card").waitFor();
    assert.match(await cardHops(page), /4 person-to-person hops/);
    assert.equal(await routeState(page), "VERIFIED_ROUTE_FOUND");
    assert.match(await page.locator("#path-title").innerText(), /Verified route shown · 4 hops · looking for a shorter one/);
    assert.match(await page.locator("#path-meta").innerText(), /first route after 6\.2s/);
    assert.match(await page.locator("#deep-title").innerText(), /Looking for a shorter route/);
    assert.equal(await page.locator("#deep-stop").isVisible(), true);
    assert.equal(await page.locator("#route-update").isVisible(), false);
    // An opened evidence panel survives the next poll: the cards are not rebuilt.
    await page.locator("#path-cards details.evidence summary").first().click();
    await h.pollCount(2);
    assert.equal(await page.locator("#path-cards details.evidence[open]").count(), 1);
    await page.screenshot({ path: path.join(output, "verified-route-searching.png"), fullPage: true });
  });

  await check("a shorter route is announced and never swapped in by itself", async (page) => {
    await choosePair(page);
    await start(page);
    await page.locator("#route-update").waitFor({ state: "visible" });
    assert.match(await page.locator("#route-update-text").innerText(), /Shorter route found: 4 hops → 3 hops/);
    assert.equal(await page.locator("#route-update").getAttribute("role"), "status");
    assert.equal(await page.locator("#route-update").getAttribute("aria-live"), "polite");
    assert.match(await cardHops(page), /4 person-to-person hops/);
    assert.equal(await routeState(page), "BETTER_ROUTE_AVAILABLE");
    assert.match(await page.locator("#path-title").innerText(), /shorter route available/);
    await page.screenshot({ path: path.join(output, "shorter-route-offered.png"), fullPage: true });
    await page.locator("#route-update-show").click();
    assert.match(await cardHops(page), /3 person-to-person hops/);
    assert.equal(await page.locator("#route-update").isVisible(), false);
    assert.equal(await routeState(page), "VERIFIED_ROUTE_FOUND");
  });

  await check("a stale version is ignored and the proof is offered, not forced", async (page, h) => {
    await choosePair(page);
    await start(page);
    await page.locator("#route-update").waitFor({ state: "visible" });
    await h.pollCount(3); // The third poll replays sequence 2 (the 4-hop state).
    assert.equal(await page.locator("#route-update").isVisible(), true);
    assert.match(await cardHops(page), /4 person-to-person hops/);
    await page.locator("#route-update-text").filter({ hasText: "Exact shortest path found: 3 hops" }).waitFor();
    assert.equal(await page.locator("#route-update-show").innerText(), "Show exact route");
    assert.match(await cardHops(page), /4 person-to-person hops/);
    assert.equal(await routeState(page), "BETTER_ROUTE_AVAILABLE");
    assert.equal(await page.locator("#deep-progress").isVisible(), false);
    assert.equal(await page.locator("#find-connection").isDisabled(), false);
    await page.locator("#route-update-show").click();
    assert.match(await cardHops(page), /3 person-to-person hops/);
    assert.match(await page.locator("#path-title").innerText(), /Exact shortest path · 3 hops/);
    assert.match(await page.locator("#path-meta").innerText(), /exact shortest path.*proven shortest after 31s/);
    assert.equal(await routeState(page), "EXACT_ROUTE_PROVEN");
    await page.screenshot({ path: path.join(output, "exact-route-shown.png"), fullPage: true });
  });

  await check("stop keeps the verified route on screen", async (page, h) => {
    await choosePair(page);
    await start(page);
    await page.locator("#path-cards .path-card").waitFor();
    await page.locator("#deep-stop").click();
    assert.equal(await page.locator("#deep-progress").isVisible(), false);
    assert.match(await cardHops(page), /4 person-to-person hops/);
    assert.equal(await routeState(page), "VERIFIED_SEARCH_STOPPED");
    assert.match(await page.locator("#path-title").innerText(), /Verified route · 4 hops · search stopped/);
    assert.match(await page.locator("#path-message").innerText(), /stopped.*verified.*not established/i);
    await page.waitForTimeout(1700);
    assert.equal(h.calls.filter((x) => x.pathname.endsWith("/cancel")).length, 1);
    const pollsAtStop = h.polls;
    await page.waitForTimeout(1700);
    assert.equal(h.polls, pollsAtStop);
  });

  await check("a refresh restores the server's best route", async (page, h) => {
    await choosePair(page);
    await start(page);
    await page.locator("#path-cards .path-card").waitFor();
    const pathsBefore = h.calls.filter((x) => x.pathname === "/api/path").length;
    const pollsBefore = h.polls;
    // The shared URL restores the pair and re-runs the query; the tab's
    // retained job handle makes that a poll of the running job, not a new job.
    await page.reload();
    await page.waitForFunction(() => document.querySelector("#data-mode")?.value === "live");
    await page.locator("#path-cards .path-card").waitFor();
    assert.equal(h.calls.filter((x) => x.pathname === "/api/path").length, pathsBefore);
    assert.ok(h.polls > pollsBefore);
    assert.match(await cardHops(page), /3 person-to-person hops/);
    assert.equal(await routeState(page), "EXACT_ROUTE_PROVEN");
    assert.equal(await page.locator("#route-update").isVisible(), false);
  });

  await check("the export names the displayed route and the delivery state", async (page) => {
    await choosePair(page);
    await start(page);
    await page.locator("#route-update").waitFor({ state: "visible" });
    const download = page.waitForEvent("download");
    await page.locator("#export-json").click();
    const file = await (await download).path();
    const payload = JSON.parse(fs.readFileSync(file, "utf8"));
    assert.equal(payload.path_result.paths[0].hops, 4);
    assert.equal(payload.route_delivery.route_state, "BETTER_ROUTE_AVAILABLE");
    assert.equal(payload.route_delivery.route_status, "verified_route_found");
    assert.equal(payload.route_delivery.displayed_route_id, "r-long");
    assert.equal(payload.route_delivery.displayed_is_best, false);
    assert.equal(payload.route_delivery.best_route.route_id, "r-short");
    assert.equal(payload.route_delivery.best_route.hops, 3);
    assert.equal(payload.route_delivery.sequence_number, 4);
  });

  await check("an equal-length route is not announced", async (page, h) => {
    await choosePair(page);
    await start(page);
    await page.locator("#path-cards .path-card").waitFor();
    await h.pollCount(2);
    await page.waitForTimeout(300);
    assert.equal(await page.locator("#route-update").isVisible(), false);
    assert.match(await cardHops(page), /4 person-to-person hops/);
    assert.equal(await routeState(page), "VERIFIED_ROUTE_FOUND");
  });

  await check("a proof about a longer route does not label the shown route exact", async (page, h) => {
    await choosePair(page);
    await start(page);
    await page.locator("#path-cards .path-card").waitFor();
    assert.match(await cardHops(page), /3 person-to-person hops/);
    await h.pollCount(2);
    await page.locator("#deep-progress").waitFor({ state: "hidden" });
    assert.match(await cardHops(page), /3 person-to-person hops/);
    assert.equal(await routeState(page), "SEARCH_INCOMPLETE");
    assert.doesNotMatch(await page.locator("#path-title").innerText(), /Exact/);
    assert.doesNotMatch(await page.locator("#path-meta").innerText(), /exact shortest path/);
    assert.equal(await page.locator("#route-update").isVisible(), false);
  });

  await check("withdrawing a route that is not on screen leaves the screen alone", async (page, h) => {
    await choosePair(page);
    await start(page);
    await page.locator("#route-update").waitFor({ state: "visible" });
    await h.pollCount(3);
    await page.locator("#route-update").waitFor({ state: "hidden" });
    assert.match(await cardHops(page), /4 person-to-person hops/);
    assert.equal(await routeState(page), "VERIFIED_ROUTE_FOUND");
    assert.doesNotMatch(await page.locator("#path-message").innerText(), /withdrawn/);
  });

  await check("withdrawing the shown route replaces it and says why", async (page, h) => {
    await choosePair(page);
    await start(page);
    await page.locator("#path-cards .path-card").waitFor();
    assert.match(await cardHops(page), /4 person-to-person hops/);
    await page.locator("#path-message").filter({ hasText: "withdrawn after identity checks" }).waitFor();
    assert.match(await cardHops(page), /3 person-to-person hops/);
    // The explanation stays up on the next poll rather than flashing once.
    await h.pollCount(3);
    await page.waitForTimeout(200);
    assert.match(await page.locator("#path-message").innerText(), /withdrawn after identity checks.*3 hops/);
  });

  await browser.close();
  const report = { checked_at: new Date().toISOString(), browser: browser.version(), playwright: require("playwright/package.json").version, base,
    status: errors.length ? "failed" : "passed", checks, uncaught_errors: errors,
    artifacts: ["verified-route-searching.png", "shorter-route-offered.png", "exact-route-shown.png", "report.json"] };
  fs.writeFileSync(path.join(output, "report.json"), JSON.stringify(report, null, 2) + "\n");
  process.exitCode = report.status === "passed" ? 0 : 1;
}

async function install(page, script) {
  const calls = [];
  let polls = 0;
  const waiters = [];
  await page.route("**/api/**", async (route) => {
    const u = new URL(route.request().url());
    const mode = u.searchParams.get("mode");
    calls.push({ pathname: u.pathname, method: route.request().method(), mode });
    let body = {};
    if (u.pathname === "/api/dataset") {
      body = { source_mode: mode, mode, version: mode === "live" ? version : "snapshot-test-v1", coverage, counts: null, capabilities: { live_graph: true, global_centrality: false }, examples: [] };
    } else if (u.pathname === "/api/search") {
      const target = u.searchParams.get("q")?.toLowerCase().includes("target");
      body = { status: "ok", source: "live", mode, version, results: [person(target ? "9002" : "9001", target ? "Deep Target" : "Deep Source")] };
    } else if (u.pathname === "/api/path") {
      body = NO_ROUTE;
    } else if (u.pathname === "/api/search-jobs/0123456789abcdef0123456789abcdef") {
      body = script[Math.min(polls, script.length - 1)];
      polls++;
      waiters.splice(0).forEach((w) => w());
    } else if (u.pathname === "/api/search-jobs/0123456789abcdef0123456789abcdef/cancel") {
      body = { ...FOUND_LONG, status: "cancelled", route_status: "verified_search_stopped", sequence_number: 99, message: "Search stopped." };
    } else if (u.pathname.startsWith("/api/person/")) {
      const id = u.pathname.split("/").pop();
      body = { status: "ok", mode, version, person: person(id, names[id] || id), queryable: true, indexed: false };
    } else {
      body = { status: "ok", mode, version, paths: [], people: [], edges: [] };
    }
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) });
  });
  return {
    calls, get polls() { return polls; },
    pollCount: (n) => new Promise((resolve) => {
      const check = () => { if (polls >= n) resolve(); else waiters.push(check); };
      check();
    }),
  };
}

async function prepare(page) { await page.goto(`${base}/?mode=live`); await page.waitForFunction(() => document.querySelector("#data-mode")?.value === "live"); }
async function choosePair(page) {
  await page.locator("#source-query").fill("Deep Source");
  await page.locator("#source-results button").filter({ hasText: "Deep Source" }).first().click();
  await page.locator("#target-query").fill("Deep Target");
  await page.locator("#target-results button").filter({ hasText: "Deep Target" }).first().click();
}
async function start(page) { const response = page.waitForResponse((r) => new URL(r.url()).pathname === "/api/path"); await page.locator("#find-connection").click(); await response; }

main().catch((error) => { console.error(error.stack || error); process.exitCode = 1; });
