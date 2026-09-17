/* Manual production smoke check: run only against a URL you control.
   It performs name lookup and one documented route search. */
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
    await page.locator("#snapshot-label").getByText("v0.3", { exact: true }).waitFor({ timeout: 30000 });
    await page.locator("#last-updated").getByText("Last updated 09/16/2026", { exact: true }).waitFor({ timeout: 30000 });
    assert.equal(await page.locator("#data-mode").count(), 0);
    assert.equal(await page.locator("#example-select").count(), 0);
    assert.equal(await page.locator("#coverage-banner").count(), 0);
    assert.equal(await page.getByText("Saved demo").count(), 0);
    assert.equal(await page.locator("#genealogy").isDisabled(), true);
    await page.locator("#source-query").fill("da");
    await page.locator("#source-results .search-result[role=option]").first().waitFor({ timeout: 30000 });
    await page.locator("#source-query").fill("1621061");
    await page.locator("#source-results .search-result[role=option]").filter({ hasText: "1621061" }).first().click({ timeout: 30000 });
    await page.locator("#target-query").fill("1019647");
    await page.locator("#target-results .search-result[role=option]").filter({ hasText: "1019647" }).first().click({ timeout: 30000 });
    await page.locator("#find-connection").click();
    await page.locator(".path-card").first().waitFor({ timeout: 90000 });
    assert.match(await page.locator("#path-title").innerText(), /Exact shortest path/);
    assert.ok((await page.locator(".path-card .evidence").count()) >= 1);
    assert.deepEqual(failedApi, []);
    assert.deepEqual(errors, []);
    const noticeAfterWorkspace = await page.evaluate(() =>
      document.querySelector("#project-disclaimer").compareDocumentPosition(document.querySelector("#connections")) & Node.DOCUMENT_POSITION_PRECEDING);
    assert.ok(noticeAfterWorkspace);
    console.log("PASS production UI: version, update date, name lookup, route, evidence, bottom notice");
  } finally {
    await browser.close();
  }
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
