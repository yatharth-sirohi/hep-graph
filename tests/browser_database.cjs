/* Database-only browser smoke check. Start the local server, then run with
   HEP_URL and an installed Playwright/Chrome. All API replies are mocked so
   this test cannot write to a database or depend on INSPIRE availability. */
const { chromium } = require("playwright");
const assert = require("node:assert/strict");

const base = process.env.HEP_URL || "http://127.0.0.1:8765";
const executablePath = process.env.HEP_BROWSER_EXECUTABLE;
const jobId = "a".repeat(32);

async function main() {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  const page = await browser.newPage();
  const errors = [];
  const seen = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (request) => {
    if (request.url().includes("/api/")) seen.push(new URL(request.url()));
  });
  try {
    await page.route("**/api/dataset*", (route) => route.fulfill({ json: {
      version: "graph-db:test", source_mode: "database", created_at: "2026-09-16T22:00:00Z",
      coverage: { label: "Pinned graph version", complete: true, description: "Test graph." },
      capabilities: { genealogy: false, deep_search: true, global_centrality: false },
    } }));
    await page.route("**/api/search?*", (route) => {
      const q = new URL(route.request().url()).searchParams.get("q");
      return route.fulfill({ json: { status: "ok", results: [{ id: q === "alice" ? "1" : "2", name: q, indexed: true, queryable: true }] } });
    });
    await page.route("**/api/path?*", (route) => route.fulfill({ json: {
      job_id: jobId, mode: "database", status: "searching", route_status: "searching_no_path",
      can_continue: true, sequence_number: 1, progress: { expansions: 1, stage: "continue_search" }, paths: [],
    } }));
    await page.route(`**/api/search-jobs/${jobId}*`, (route) => route.fulfill({ json: {
      job_id: jobId, mode: "database", version: "graph-db:test", status: "settled",
      route_status: "exact_route_proven", global_shortest_proven: true,
      best_route: { hops: 1 },
      can_continue: false, sequence_number: 2, progress: { expansions: 2, stage: "finished" },
      coverage: { label: "Pinned graph version", complete: true },
      paths: [{ hops: 1, people: [{ id: "1", name: "alice" }, { id: "2", name: "bob" }],
        edges: [{ source: "1", target: "2", types: ["coauthor"], shared_works: 1,
          works: [{ id: "9", title: "Test work", year: 2024, author_count: 2, source_url: "https://inspirehep.net/literature/9" }] }] }],
    } }));
    await page.goto(base, { waitUntil: "domcontentloaded" });
    await page.locator("#snapshot-label").getByText("v0.3", { exact: true }).waitFor();
    await page.locator("#last-updated").getByText("Last updated 09/16/2026", { exact: true }).waitFor();
    assert.equal(await page.locator("#data-mode").count(), 0);
    assert.equal(await page.locator("#example-select").count(), 0);
    assert.equal(await page.locator("#coverage-banner").count(), 0);
    assert.equal(await page.locator("#genealogy").isDisabled(), true);
    assert.equal(await page.locator("#genealogy").isChecked(), false);
    await page.locator("#source-query").fill("alice");
    await page.locator("#source-results .search-result[role=option]").first().click();
    await page.locator("#target-query").fill("bob");
    await page.locator("#target-results .search-result[role=option]").first().click();
    await page.locator("#find-connection").click();
    await page.locator(".path-card").first().waitFor({ timeout: 15000 });
    assert.match(await page.locator("#path-title").innerText(), /Exact shortest path/);
    assert.equal(await page.getByText("Test work").count(), 1);
    assert.doesNotMatch(await page.locator("body").innerText(), /Neon graph|graph database|graph-db:/i);
    assert.ok(seen.filter((url) => url.pathname.startsWith("/api/")).every((url) => url.searchParams.get("mode") !== "snapshot"));
    assert.ok(seen.some((url) => url.pathname === "/api/path" && url.searchParams.get("mode") === "database" && url.searchParams.get("genealogy") === "false"));
    // The person panel links to the HEP Atlas page for that INSPIRE author id (HEP Graph x Atlas).
    await page.route("**/api/person/1*", (route) => route.fulfill({ json: {
      status: "ok", mode: "database", indexed: true, queryable: true, coauthor_count: 1, combined_degree: 1,
      person: { id: "1", name: "alice", aliases: [], affiliations: [], orcid: null, profile_status: "profile",
        source_url: "https://inspirehep.net/authors/1" },
      collaborators: [], advisers: [], students: [], filters: {}, version: "graph-db:test",
      coverage: { label: "Pinned graph version", complete: true },
    } }));
    await page.locator(".path-card .person-link", { hasText: "alice" }).first().click();
    const onAtlas = page.locator("#person-content a", { hasText: "See on the HEP Atlas" });
    await onAtlas.waitFor();
    assert.equal(await onAtlas.getAttribute("href"), "/atlas/#/view/person/1");
    assert.deepEqual(errors, []);
    console.log("PASS v0.3 browser path, update date, and search-job polling");
  } finally {
    await browser.close();
  }
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
