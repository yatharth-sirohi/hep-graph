/* Independent accuracy checks for result scope, races, profiles and exports.
   Run with the same Playwright/Chrome configuration as browser_acceptance.cjs. */
const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const base = process.env.HEP_URL || "http://127.0.0.1:8765";
const out =
  process.env.HEP_ACCURACY_OUTPUT ||
  path.join(__dirname, "../docs/browser-accuracy");
const checks = [],
  errors = [];
let browser;
const frames = (p) =>
  p.evaluate(
    () =>
      new Promise((resolve) =>
        requestAnimationFrame(() => requestAnimationFrame(resolve)),
      ),
  );
async function open(p, query = "source=1621061&target=1019647") {
  await p.goto(base + "/?" + query);
  await p.locator(".path-card").first().waitFor();
  await p.waitForFunction(
    () => !document.querySelector("#find-connection").disabled,
  );
  await frames(p);
  await p.locator(".advanced-filters").evaluate((details) => { details.open = true; });
}
async function hold(p, pattern) {
  let release, seen;
  const gate = new Promise((r) => (release = r)),
    intercepted = new Promise((r) => (seen = r));
  await p.route(pattern, async (route) => {
    seen();
    await gate;
    await route.continue().catch(() => {});
  });
  return { intercepted, release };
}
async function downloadJSON(p, name) {
  const waiting = p.waitForEvent("download");
  await p.locator("#export-json").click();
  const d = await waiting;
  const filename = path.join(out, name);
  await d.saveAs(filename);
  return JSON.parse(fs.readFileSync(filename, "utf8"));
}
async function check(name, fn) {
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    acceptDownloads: true,
  });
  const p = await context.newPage();
  p.on("pageerror", (e) => errors.push(e.message));
  const begin = Date.now();
  try {
    await fn(p);
    checks.push({ name, status: "passed", milliseconds: Date.now() - begin });
    console.log("PASS", name);
  } catch (e) {
    checks.push({ name, status: "failed", error: e.message });
    console.log("FAIL", name, e.message);
    await p
      .screenshot({
        path: path.join(out, "failure-" + checks.length + ".png"),
        fullPage: true,
      })
      .catch(() => {});
  } finally {
    await context.close();
  }
}
(async () => {
  fs.mkdirSync(out, { recursive: true });
  browser = await chromium.launch({
    headless: true,
    ...(process.env.HEP_BROWSER_EXECUTABLE
      ? { executablePath: process.env.HEP_BROWSER_EXECUTABLE }
      : {}),
  });
  await check(
    "All-author label and exported filters match the calculated graph",
    async (p) => {
      await open(p, "source=1066085&target=1071895&max_authors=all");
      assert.match(
        await p.locator("#path-meta").innerText(),
        /all paper team sizes/i,
      );
      const data = await downloadJSON(p, "all-authors.json");
      assert.deepEqual(data.filters, data.path_result.filters);
      assert.equal(
        data.path_result.paths[0].edges[0].works[0].author_count,
        2932,
      );
    },
  );
  await check(
    "Alternative routes export one combined evidence edge per person pair",
    async (p) => {
      await open(p, "source=1621061&target=1013775");
      const data = await downloadJSON(p, "alternatives.json");
      const edges = data.displayed_graph.edges;
      const keys = edges.map((e) => [e.source, e.target].sort().join(":"));
      assert.equal(
        new Set(keys).size,
        keys.length,
        "Repeated common path segments must not duplicate displayed graph edges",
      );
      assert.equal(data.path_result.paths.length, 2);
    },
  );
  await check(
    "A delayed path cannot restore obsolete filters or evidence",
    async (p) => {
      await open(p);
      await p.locator("line.edge.coauthor").first().focus();
      await p.locator("line.edge.coauthor").first().press("Enter");
      const h = await hold(p, "**/api/path?**");
      await p.locator("#find-connection").click();
      await h.intercepted;
      await p.locator("#max-authors").selectOption("5");
      h.release();
      await p.waitForFunction(
        () => !document.querySelector("#find-connection").disabled,
      );
      await frames(p);
      assert.equal(
        await p.locator(".path-card").count(),
        0,
        "Old path must stay cleared until a new calculation",
      );
      assert.equal(
        await p.locator("#edge-inspector").isHidden(),
        true,
        "Old edge evidence must be cleared",
      );
    },
  );
  await check(
    "A delayed centrality result cannot appear under another selected metric",
    async (p) => {
      await open(p);
      await p.locator('[data-tab="centrality"]').click();
      const h = await hold(p, "**/api/centrality?**");
      await p.locator("#load-centrality").click();
      await h.intercepted;
      await p.locator("#centrality-metric").selectOption("harmonic");
      h.release();
      await p.waitForFunction(
        () => !document.querySelector("#load-centrality").disabled,
      );
      await frames(p);
      if (await p.locator("#centrality-results").isVisible())
        assert.match(
          await p.locator("#centrality-explainer strong").innerText(),
          /harmonic/i,
        );
    },
  );
  await check(
    "Profile publication and collaborator counts match the API and disclose scope",
    async (p) => {
      await open(p);
      const response = p.waitForResponse(
        (r) => new URL(r.url()).pathname === "/api/person/1621061",
      );
      await p.locator(".path-route .person-link").first().click();
      const d = await (await response).json();
      await p
        .getByRole("button", { name: "Add local neighborhood", exact: true })
        .waitFor();
      for (const field of [
        "indexed_publications",
        "eligible_publications",
        "coauthor_count",
        "combined_degree",
      ]) {
        const stat = p.locator(`[data-stat="${field}"]`);
        assert.equal(await stat.count(), 1, "Profile missing " + field);
        assert.equal(Number(await stat.innerText()), d[field]);
      }
      assert.match(
        await p.locator("#person-content").innerText(),
        /snapshot|filters/i,
      );
      await p.locator("#max-authors").selectOption("5");
      assert.equal(
        await p.locator("#person-panel").isHidden(),
        true,
        "Profile from previous filters must close",
      );
    },
  );
  await check(
    "Delayed neighborhood cannot repopulate a changed query graph",
    async (p) => {
      await open(p);
      await p.locator(".path-route .person-link").first().click();
      await p
        .getByRole("button", { name: "Add local neighborhood", exact: true })
        .waitFor();
      const h = await hold(p, "**/api/neighborhood/**");
      await p
        .getByRole("button", { name: "Add local neighborhood", exact: true })
        .click();
      await h.intercepted;
      await p.locator("#max-authors").selectOption("5");
      const response = p.waitForResponse((r) =>
        new URL(r.url()).pathname.startsWith("/api/neighborhood/"),
      );
      h.release();
      await response;
      await frames(p);
      assert.equal(await p.locator(".node").count(), 0);
    },
  );
  await check(
    "Live INSPIRE mode returns a queryable identity for a path",
    async (p) => {
      await p.goto(base + "?mode=snapshot");
      await p
        .locator('#example-select option[value="0"]')
        .waitFor({ state: "attached" });
      await p.locator("#data-mode").selectOption("live");
      await p.waitForFunction(
        () => document.querySelector("#data-mode")?.value === "live",
      );
      await p.route("**/api/search?**", (route) => {
        const live =
          new URL(route.request().url()).searchParams.get("mode") === "live";
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify(
            live
              ? {
                  status: "ok",
                  source: "live",
                  results: [
                    {
                      id: "2955074",
                      name: "Erin Visser",
                      indexed: false,
                      queryable: true,
                      mode: "live",
                      affiliations: [],
                    },
                  ],
                }
              : {
                  status: "not_found",
                  results: [],
                  message: "No matching live researcher.",
                },
          ),
        });
      });
      await p.locator("#source-query").fill("Erin Visser");
      await p
        .locator("#source-results")
        .getByText("Erin Visser")
        .waitFor();
      await p
        .locator("#source-results button")
        .filter({ hasText: "Erin Visser" })
        .waitFor({ timeout: 3000 });
      await p.locator("#source-results button").filter({ hasText: "Erin Visser" }).click();
      assert.match(await p.locator("#source-selected").innerText(), /Live INSPIRE/i);
      assert.equal(await p.locator("#source-selected .status.live").count(), 1);
    },
  );
  await check(
    "SVG export preserves the evidence definition and snapshot",
    async (p) => {
      await open(p);
      const waiting = p.waitForEvent("download");
      await p.locator("#export-svg").click();
      const d = await waiting,
        filename = path.join(out, "scoped-graph.svg");
      await d.saveAs(filename);
      const svg = fs.readFileSync(filename, "utf8");
      assert.match(svg, /sha256:/);
      assert.match(svg, /max_authors/);
      assert.match(svg, /adviser/);
      assert.match(svg, /partial|bounded/i);
    },
  );
  await check(
    "A coauthor tie stays one ordinary hop when doctoral context is also present",
    async (p) => {
      await open(p);
      const co = p.locator("line.edge.coauthor").first();
      assert.equal(await p.locator("line.edge.phd").count(), 0);
      assert.equal(await p.locator(".path-route .route-arrow").first().innerText(), "—");
      await p
        .locator("#graph-stage")
        .evaluate((el) =>
          el.scrollIntoView({ block: "center", behavior: "instant" }),
        );
      await frames(p);
      // A horizontal SVG line has a zero-height layout box. Click its actual
      // painted stroke after applying the SVG transform, away from the label.
      const point = await co.evaluate((el) => {
        const x =
          el.x1.baseVal.value +
          (el.x2.baseVal.value - el.x1.baseVal.value) * 0.3;
        const y =
          el.y1.baseVal.value +
          (el.y2.baseVal.value - el.y1.baseVal.value) * 0.3;
        const p = new DOMPoint(x, y).matrixTransform(el.getScreenCTM());
        return {
          x: p.x,
          y: p.y,
          hit: document.elementFromPoint(p.x, p.y) === el,
        };
      });
      assert.equal(
        point.hit,
        true,
        "The visible coauthor stroke must be the pointer hit target",
      );
      await p.mouse.click(point.x, point.y);
      assert.equal(await p.locator("#edge-inspector").isVisible(), true);
      assert.match(
        await p.locator("#edge-inspector").innerText(),
        /supplemental doctoral record.*Pascoli.*adviser.*Hostert.*student/s,
      );
      await p.screenshot({
        path: path.join(out, "doctoral-evidence.png"),
        fullPage: true,
      });
    },
  );
  await check(
    "Centrality profiles open a visible independently scoped neighborhood",
    async (p) => {
      await p.goto(base);
      await p
        .locator('#example-select option[value="0"]')
        .waitFor({ state: "attached" });
      await p.locator('[data-tab="centrality"]').click();
      await p.locator("#load-centrality").click();
      await p.locator("#centrality-rows .person-link").first().waitFor();
      await p.locator("#centrality-rows .person-link").first().click();
      await p
        .getByRole("button", { name: "Add local neighborhood", exact: true })
        .click();
      await p.waitForFunction(
        () => document.querySelectorAll(".node").length > 1,
      );
      assert.equal(await p.locator("#connection-results").isVisible(), true);
      assert.match(await p.locator("#path-title").innerText(), /neighborhood/i);
      assert.equal(await p.locator(".path-card").count(), 0);
      assert.equal(
        await p.locator("#copy-share").isHidden(),
        true,
        "A path share link must not pretend to restore a standalone neighborhood",
      );
      const fullyFramed = await p
        .locator("#connection-graph")
        .evaluate((svg) => {
          const bounds = svg.getBoundingClientRect();
          return [...svg.querySelectorAll(".node circle")].every((circle) => {
            const b = circle.getBoundingClientRect();
            return (
              b.left >= bounds.left &&
              b.right <= bounds.right &&
              b.top >= bounds.top &&
              b.bottom <= bounds.bottom
            );
          });
        });
      assert.equal(
        fullyFramed,
        true,
        "A newly opened standalone neighborhood must fit all node circles into the visible graph",
      );
      const d = await downloadJSON(p, "standalone-neighborhood.json");
      assert.equal(d.path_result, null);
      assert.equal(d.display_scope.type, "bounded_neighborhood");
      assert.deepEqual(d.filters, d.display_scope.filters);
      assert.ok(d.displayed_graph.nodes.length <= 100);
      await p.screenshot({
        path: path.join(out, "standalone-neighborhood.png"),
        fullPage: true,
      });
    },
  );
  await check(
    "Rapidly opening another profile cannot restore the older profile",
    async (p) => {
      await open(p);
      const h = await hold(p, "**/api/person/1621061?**");
      await p.locator(".path-route .person-link").first().click();
      await h.intercepted;
      await p.locator(".path-route .person-link").nth(1).click();
      await p
        .locator("#person-content h2")
        .getByText("Silvia Pascoli")
        .waitFor();
      const response = p.waitForResponse(
        (r) => new URL(r.url()).pathname === "/api/person/1621061",
      );
      h.release();
      await response;
      await frames(p);
      assert.equal(
        await p.locator("#person-content h2").innerText(),
        "Silvia Pascoli",
      );
    },
  );
  const report = {
    checked_at: new Date().toISOString(),
    browser: browser.version(),
    playwright: require("playwright/package.json").version,
    checks,
    uncaught_errors: errors,
    status:
      checks.every((c) => c.status === "passed") && !errors.length
        ? "passed"
        : "failed",
  };
  fs.writeFileSync(
    path.join(out, "report.json"),
    JSON.stringify(report, null, 2) + "\n",
  );
  await browser.close();
  process.exitCode = report.status === "passed" ? 0 : 1;
})().catch(async (e) => {
  console.error(e);
  if (browser) await browser.close();
  process.exitCode = 1;
});
