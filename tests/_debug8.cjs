const { chromium } = require("playwright");
(async () => {
  const exe = "/Users/yatharthsirohi/Library/Caches/ms-playwright/chromium-1217/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing";
  const browser = await chromium.launch({ headless: true, executablePath: exe });
  const context = await browser.newContext({ viewport: {width:1440,height:960}, reducedMotion: "reduce" });
  const page = await context.newPage();
  page.on("pageerror", e => console.log("PAGEERROR", e.stack || e.message));
  await page.goto("http://127.0.0.1:8790/atlas?data=fixtures");
  await page.locator('.atlas-marker[data-id="facility:cern"]').waitFor();
  await page.locator('.atlas-marker[data-id="facility:cern"]').click({force:true});
  await page.waitForTimeout(1000);
  console.log("hash", await page.evaluate(() => location.hash));
  console.log("detail class", await page.locator("#detail-panel").getAttribute("class"));
  console.log("detail html", (await page.locator("#detail-panel").innerHTML()).slice(0,300));
  await browser.close();
})();
