/* Manual production smoke check: run only against a URL you control.
   It performs one name lookup and one documented example route search. */
const { chromium } = require("playwright");
const assert = require("node:assert/strict");

const base = process.env.HEP_URL || "https://hep-graph.vercel.app";
const executablePath = process.env.HEP_BROWSER_EXECUTABLE;

async function main() {
  const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
  const page = await browser.newPage();
  const errors = [];
  const failedApi = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("response", (response) => {
    if (new URL(response.url()).pathname.startsWith("/api/") && response.status() >= 400)
      failedApi.push(`${response.status()} ${new URL(response.url()).pathname}`);
  });
  try {
    await page.goto(base, { waitUntil: "domcontentloaded", timeout: 30000 });
    await page.locator("#snapshot-label").getByText("Neon graph", { exact: false }).waitFor({ timeout: 30000 });
    assert.equal(await page.locator("#data-mode").count(), 0);
    assert.equal(await page.getByText("Saved demo").count(), 0);
    assert.equal(await page.locator("#genealogy").isDisabled(), true);
    await page.locator("#source-query").fill("da");
    await page.locator("#source-results .search-result[role=option]").first().waitFor({ timeout: 30000 });
    await page.locator("#source-query").fill("");
    await page.locator("#load-example").click();
    await page.locator(".path-card").first().waitFor({ timeout: 90000 });
    assert.match(await page.locator("#path-title").innerText(), /Exact shortest path/);
    assert.ok((await page.locator(".path-card .evidence").count()) >= 1);
    assert.deepEqual(failedApi, []);
    assert.deepEqual(errors, []);
    console.log("PASS production Neon graph: name lookup, example route, evidence, no demo mode");
  } finally {
    await browser.close();
  }
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
