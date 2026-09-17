const { chromium } = require("playwright");
(async () => {
  const exe = "/Users/yatharthsirohi/Library/Caches/ms-playwright/chromium-1217/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing";
  const browser = await chromium.launch({ headless: true, executablePath: exe });
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", e => errors.push(e.message));
  await page.goto("http://127.0.0.1:8790/atlas");
  await page.waitForTimeout(2000);
  console.log("notice text:", await page.locator("#data-notice").innerText().catch(()=>"(none)"));
  console.log("notice hidden class:", await page.locator("#data-notice").getAttribute("class"));
  console.log("errors", errors);
  console.log("markers", await page.locator(".atlas-marker").count());
  await browser.close();
})();
