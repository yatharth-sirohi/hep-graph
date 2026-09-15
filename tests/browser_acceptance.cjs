/* Optional browser acceptance: npm install --no-save playwright, then node tests/browser_acceptance.cjs.
   Set HEP_BROWSER_EXECUTABLE to use an installed Chromium-family browser. */
const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const base = process.env.HEP_URL || "http://127.0.0.1:8765";
const output =
  process.env.HEP_BROWSER_OUTPUT || path.join(__dirname, "../docs/browser");
fs.mkdirSync(output, { recursive: true });
const results = [],
  errors = [];
let browser, page;
const record = async (name, fn) => {
  const start = Date.now();
  await fn();
  results.push({ name, status: "passed", milliseconds: Date.now() - start });
  console.log("PASS", name);
};
const pathResponse = (p) =>
  p.waitForResponse((r) => new URL(r.url()).pathname === "/api/path");
async function find(p = page) {
  const response = pathResponse(p);
  await p.locator("#find-connection").click();
  const data = await (await response).json();
  await p.waitForFunction(
    () => !document.querySelector("#find-connection").disabled,
  );
  return data;
}
async function example(index = 0, p = page) {
  await p.locator("#example-select").selectOption(String(index));
  const response = pathResponse(p);
  await p.locator("#load-example").click();
  const data = await (await response).json();
  await p.waitForFunction(
    () => !document.querySelector("#find-connection").disabled,
  );
  return data;
}
async function loaded(p = page) {
  await p.waitForFunction(
    () => document.querySelector("#example-select option")?.value === "0",
  );
}
async function choose(which, query, name) {
  await page.locator(`#${which}-query`).fill(query);
  const option = page
    .locator(`#${which}-results button`)
    .filter({ hasText: name });
  await option.first().click();
}

(async () => {
  browser = await chromium.launch({
    headless: true,
    ...(process.env.HEP_BROWSER_EXECUTABLE
      ? { executablePath: process.env.HEP_BROWSER_EXECUTABLE }
      : {}),
  });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    acceptDownloads: true,
  });
  context.on("page", p => p.on("pageerror", e => errors.push(e.message)));
  page = await context.newPage();
  let baseline, share;
  await record("Real snapshot loads with explicit coverage", async () => {
    await page.goto(base);
    await loaded();
    assert.match(
      await page.locator("#coverage-text").innerText(),
      /partial|bounded/i,
    );
    assert.equal(
      (await page.locator("#example-select option").count()) >= 3,
      true,
    );
  });
  await record(
    "Search disambiguates Witten identities using context",
    async () => {
      await page.locator("#source-query").fill("Witten");
      await page.locator("#source-results button").first().waitFor();
      assert.ok((await page.locator("#source-results button").count()) > 1);
      assert.match(await page.locator("#source-results").innerText(), /983328/);
      await page
        .locator("#source-results button")
        .filter({ hasText: "Edward Witten" })
        .first()
        .click();
      await choose("target", "Gross", "David Jonathan Gross");
      const d = await find();
      assert.equal(d.status, "ok");
      assert.equal(d.paths[0].hops, 1);
    },
  );
  await record(
    "A coauthor hop keeps doctoral evidence as supplemental context",
    async () => {
      baseline = await example(0);
      assert.equal(baseline.status, "ok");
      assert.equal(baseline.paths[0].hops, 1);
      assert.ok(baseline.paths[0].edges[0].types.includes("phd"));
      assert.ok(baseline.paths[0].edges[0].types.includes("coauthor"));
      assert.equal(
        await page.locator(".path-route .route-arrow").first().innerText(),
        "—",
      );
      assert.equal(await page.locator("line.edge.phd").count(), 0);
      assert.ok((await page.locator("line.edge.coauthor").count()) >= 1);
    },
  );
  await record(
    "Work evidence expands with identifiers and doctoral source",
    async () => {
      await page.locator(".evidence summary").first().click();
      assert.ok(
        (await page.locator('.evidence a[href^="https://doi.org/"]').count()) >
          0,
      );
      assert.ok(
        (await page
          .locator('.evidence a[href^="https://arxiv.org/"]')
          .count()) > 0,
      );
      assert.match(
        await page.locator(".evidence").first().innerText(),
        /adviser|student/i,
      );
    },
  );
  await record(
    "Share link reload restores selected people, filters, and route",
    async () => {
      await page.locator("#copy-share").click();
      share = page.url();
      const u = new URL(share);
      assert.equal(u.searchParams.get("source"), "1621061");
      assert.equal(u.searchParams.get("target"), "1019647");
      assert.equal(u.searchParams.get("min_authors"), "1");
      assert.ok(u.searchParams.get("version"));
      const second = await context.newPage();
      const response = pathResponse(second);
      await second.goto(share);
      const d = await (await response).json();
      assert.equal(d.paths[0].hops, 1);
      await second.close();
    },
  );
  await record("Genealogy remains independent of paper filters", async () => {
    await page.locator(".advanced-filters > summary").click();
    await page.locator("#max-authors").selectOption("custom");
    await page.locator("#max-authors-custom").fill("1");
    await page.locator("#max-authors-custom").blur();
    let d = await find();
    assert.equal(d.status, "ok");
    assert.deepEqual(d.paths[0].edges[0].types, ["phd"]);
    await page.locator("#genealogy").uncheck();
    d = await find();
    assert.equal(d.status, "no_path");
    assert.match(
      await page.locator("#path-message").innerText(),
      /indexed|snapshot|filters/i,
    );
  });
  await record(
    "Custom caps, repeated-work threshold and date range affect calculations",
    async () => {
      await page.locator("#max-authors-custom").fill("7");
      await page.locator("#min-shared").selectOption("2");
      await page.locator("#year-start").fill("2018");
      await page.locator("#year-end").fill("2021");
      await page.locator("#year-end").blur();
      const d = await find();
      assert.equal(d.filters.max_authors, 7);
      assert.equal(d.filters.min_shared, 2);
      assert.equal(d.filters.year_start, 2018);
      assert.equal(d.filters.year_end, 2021);
      for (const p of d.paths)
        for (const e of p.edges) {
          assert.ok(e.shared_works >= 2);
          for (const w of e.works) {
            assert.ok(w.author_count <= 7 && w.year >= 2018 && w.year <= 2021);
          }
        }
      const second = await context.newPage();
      const response = pathResponse(second);
      await second.goto(page.url());
      await response;
      assert.equal(await second.locator("#max-authors").inputValue(), "custom");
      assert.equal(
        await second.locator("#max-authors-custom").inputValue(),
        "7",
      );
      await second.close();
    },
  );
  await record("Invalid custom input reports a validation error", async () => {
    await page.locator("#max-authors-custom").fill("0");
    await page.locator("#max-authors-custom").blur();
    await page.locator("#find-connection").click();
    assert.match(
      await page.locator("#global-status").innerText(),
      /integer|whole number|between|positive|invalid/i,
    );
  });
  await record(
    "Profiles show scholarly context, counts, genealogy and reachability",
    async () => {
      const r = pathResponse(page);
      await page.goto(share);
      await r;
      await page.locator(".path-route .person-link").first().click();
      await page.locator("#person-content h2").waitFor();
      await page
        .getByRole("button", { name: "Add local neighborhood", exact: true })
        .waitFor();
      const t = await page.locator("#person-content").innerText();
      assert.match(t, /ORCID/);
      assert.match(t, /Affiliation/i);
      assert.match(t, /reachable|reachability|component/i);
      assert.match(t, /Silvia Pascoli/);
    },
  );
  await record(
    "Bounded progressive neighborhood and edge evidence inspector work",
    async () => {
      await page
        .getByRole("button", { name: "Add local neighborhood", exact: true })
        .click();
      await page.waitForFunction(
        () => document.querySelectorAll(".node").length > 2,
      );
      assert.ok((await page.locator(".node").count()) <= 100);
      await page.locator("#close-profile").click();
      // In a dense neighborhood an edge's bounding-box center can lie under
      // another node. Exercise the edge's supported keyboard action directly.
      await page.locator("line.edge").first().focus();
      await page.locator("line.edge").first().press("Enter");
      await page.locator("#edge-inspector:not(.hidden)").waitFor();
      assert.match(
        await page.locator("#edge-inspector").innerText(),
        /work|doctoral/i,
      );
    },
  );
  await record(
    "Pan, zoom, fit, reset, labels and dragging change the displayed view",
    async () => {
      const viewport = page.locator("g.viewport");
      let before = await viewport.getAttribute("transform");
      await page.locator('[data-graph="zoom-in"]').click();
      assert.notEqual(await viewport.getAttribute("transform"), before);
      await page.locator("#show-labels").uncheck();
      assert.equal(await page.locator(".node text").count(), 0);
      await page.locator("#show-labels").check();
      await page.locator('[data-graph="fit"]').click();
      const node = page.locator(".node").first();
      await node.evaluate(el => el.scrollIntoView({behavior: "instant", block: "center"}));
      await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
      const b = await node.locator("circle").boundingBox();
      before = await node.getAttribute("transform");
      await page.mouse.move(b.x + b.width / 2, b.y + b.height / 2);
      await page.mouse.down();
      await page.mouse.move(b.x + b.width / 2 + 50, b.y + b.height / 2 + 45, {
        steps: 5,
      });
      await page.mouse.up();
      assert.notEqual(
        await page.locator(".node").first().getAttribute("transform"),
        before,
      );
      if (await page.locator("#close-profile").isVisible())
        await page.locator("#close-profile").click();
      await page.locator("#graph-stage").evaluate(el => el.scrollIntoView({behavior: "instant", block: "center"}));
      const stage = await page.locator("#graph-stage").boundingBox();
      before = await viewport.getAttribute("transform");
      await page.mouse.move(stage.x + 10, stage.y + 10);
      await page.mouse.down();
      await page.mouse.move(stage.x + 45, stage.y + 35, { steps: 4 });
      await page.mouse.up();
      assert.notEqual(await viewport.getAttribute("transform"), before);
      await page.locator('[data-graph="reset"]').click();
    },
  );
  await record(
    "Displayed graph exports as JSON and standalone styled SVG",
    async () => {
      let waiting = page.waitForEvent("download");
      await page.locator("#export-json").click();
      let dl = await waiting;
      await dl.saveAs(path.join(output, "displayed-graph.json"));
      const exported = JSON.parse(
        fs.readFileSync(path.join(output, "displayed-graph.json"), "utf8"),
      );
      assert.match(JSON.stringify(exported), /1621061/);
      assert.match(
        JSON.stringify(exported),
        /positions|pinned|displayed_graph|nodes/,
      );
      waiting = page.waitForEvent("download");
      await page.locator("#export-svg").click();
      dl = await waiting;
      await dl.saveAs(path.join(output, "displayed-graph.svg"));
      assert.match(
        fs.readFileSync(path.join(output, "displayed-graph.svg"), "utf8"),
        /<style/,
      );
    },
  );
  await record(
    "All five centrality metrics render scoped method metadata",
    async () => {
      await page.locator('[data-tab="centrality"]').click();
      for (const metric of [
        "degree",
        "combined_degree",
        "harmonic",
        "betweenness",
        "eccentricity",
      ]) {
        const needsClick = await page.locator("#centrality-results").isHidden();
        const response = page.waitForResponse(
          (r) =>
            new URL(r.url()).pathname === "/api/centrality" &&
            new URL(r.url()).searchParams.get("metric") === metric,
        );
        await page.locator("#centrality-metric").selectOption(metric);
        if (needsClick)
          await page.locator("#load-centrality").click();
        const d = await (await response).json();
        assert.equal(d.status, "ok");
        await page.waitForFunction(
          () => !document.querySelector("#load-centrality").disabled,
        );
        assert.ok((await page.locator("#centrality-rows tr").count()) > 0);
        assert.match(
          await page.locator("#centrality-explainer").innerText(),
          /snapshot|population|method/i,
        );
        if (metric === "betweenness") {
          assert.equal(d.exact, false);
          assert.match(
            await page.locator("#centrality-explainer").innerText(),
            /sample|estimate|uncertainty/i,
          );
        }
      }
    },
  );
  await record(
    "Coverage tab, stale-snapshot and failed-request states are visible",
    async () => {
      await page.locator('[data-tab="about"]').click();
      assert.doesNotMatch(
        await page.locator("#about-coverage").innerText(),
        /Loading/,
      );
      const second = await context.newPage();
      await second.goto(
        base + "/?source=1621061&target=1019647&version=missing-snapshot",
      );
      await second.locator("#version-warning:not(.hidden)").waitFor();
      await second.close();
      const failure = await context.newPage();
      await failure.route("**/api/dataset*", (route) =>
        route.fulfill({
          status: 503,
          contentType: "application/json",
          body: JSON.stringify({ message: "Simulated service unavailable" }),
        }),
      );
      await failure.goto(base);
      await failure.locator("#global-status.error").waitFor();
      assert.match(
        await failure.locator("#global-status").innerText(),
        /unavailable/i,
      );
      await failure.close();
    },
  );
  await record(
    "Mobile and desktop viewports avoid document overflow",
    async () => {
      const mobile = await browser.newContext({
        viewport: { width: 390, height: 844 },
        isMobile: true,
        hasTouch: true,
      });
      mobile.on("page", p => p.on("pageerror", e => errors.push(e.message)));
      const p = await mobile.newPage();
      const r = pathResponse(p);
      await p.goto(share);
      await r;
      await p.waitForFunction(
        () => !document.querySelector("#find-connection").disabled,
      );
      assert.ok(
        await p.evaluate(() => document.documentElement.scrollWidth <= 392),
      );
      await p.waitForFunction(() => {
        const stage = document.querySelector("#graph-stage");
        const node = stage?.querySelector(".node");
        if (!stage || !node) return false;
        const s = stage.getBoundingClientRect();
        const n = node.getBoundingClientRect();
        return n.width > 0 && n.height > 0 && n.left >= s.left - 2 &&
          n.right <= s.right + 2 && n.top >= s.top - 2 && n.bottom <= s.bottom + 2;
      });
      await p.screenshot({
        path: path.join(output, "mobile.png"),
        fullPage: true,
      });
      await mobile.close();
      await page.goto(share);
      await page.locator(".path-card").first().waitFor();
      assert.ok(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= window.innerWidth + 2,
        ),
      );
      await page.screenshot({
        path: path.join(output, "desktop.png"),
        fullPage: true,
      });
    },
  );
  await record(
    "Real five-hop alternatives render and swapping reverses endpoints",
    async () => {
      let response = pathResponse(page);
      await page.goto(base + "/?source=1621061&target=1013775");
      let data = await (await response).json();
      await page.waitForFunction(
        () => !document.querySelector("#find-connection").disabled,
      );
      assert.equal(data.paths[0].hops, 5);
      assert.ok(data.paths.length >= 2);
      assert.equal(await page.locator(".path-card").count(), data.paths.length);
      await page.screenshot({
        path: path.join(output, "five-hop.png"),
        fullPage: true,
      });
      await page.locator("#swap-people").click();
      data = await find();
      assert.equal(data.paths[0].people[0].id, "1013775");
      assert.equal(data.paths[0].people.at(-1).id, "1621061");
      assert.equal(data.paths[0].hops, 5);
    },
  );
  await record(
    "Pending requests show loading and discovered unindexed people cannot create paths",
    async () => {
      let release;
      const gate = new Promise((resolve) => {
        release = resolve;
      });
      await page.route("**/api/path?**", async (route) => {
        await gate;
        await route.continue();
      });
      const response = pathResponse(page);
      await page.locator("#find-connection").click();
      try {
        assert.equal(await page.locator("#find-connection").isDisabled(), true);
        assert.match(
          await page.locator("#find-connection").innerText(),
          /Finding/,
        );
      } finally {
        release();
      }
      await response;
      await page.waitForFunction(
        () => !document.querySelector("#find-connection").disabled,
      );
      await page.unroute("**/api/path?**");
      // Replay the identity/status independently observed by http_acceptance.py.
      // This UI case is deterministic and does not make a fresh upstream request.
      await page.route("**/api/search?**", (route) =>
        route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            status: "ok",
            source: "live",
            results: [
              {
                id: "2955074",
                name: "Erin Visser",
                indexed: false,
                affiliations: [],
                orcid: null,
              },
            ],
          }),
        }),
      );
      await page.locator("#source-query").fill("Erin Visser");
      await page
        .locator("#source-results button")
        .filter({ hasText: "Erin Visser" })
        .click();
      assert.match(
        await page.locator("#source-selected").innerText(),
        /not indexed/i,
      );
      await page.locator("#find-connection").click();
      assert.match(
        await page.locator("#global-status").innerText(),
        /not indexed.*snapshot/i,
      );
      await page.unroute("**/api/search?**");
    },
  );
  assert.deepEqual(errors, [], "No uncaught browser errors");
  fs.writeFileSync(
    path.join(output, "report.json"),
    JSON.stringify(
      {
        browser: await browser.version(),
        engine: "Chromium via Playwright",
        base,
        checked_at: new Date().toISOString(),
        checks: results,
        uncaught_errors: errors,
        status: "passed",
      },
      null,
      2,
    ),
  );
  console.log(
    JSON.stringify({
      passed: results.length,
      errors,
      browser: await browser.version(),
    }),
  );
  await browser.close();
})().catch(async (error) => {
  console.error(error);
  if (page)
    await page
      .screenshot({ path: path.join(output, "failure.png"), fullPage: true })
      .catch(() => {});
  fs.writeFileSync(
    path.join(output, "report.json"),
    JSON.stringify(
      {
        status: "failed",
        checks: results,
        error: String(error),
        uncaught_errors: errors,
      },
      null,
      2,
    ),
  );
  if (browser) await browser.close();
  process.exit(1);
});
