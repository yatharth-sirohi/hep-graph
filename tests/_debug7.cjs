const { chromium } = require("playwright");
(async () => {
  const exe = "/Users/yatharthsirohi/Library/Caches/ms-playwright/chromium-1217/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing";
  const browser = await chromium.launch({ headless: true, executablePath: exe });
  const context = await browser.newContext({ viewport: {width:1440,height:960}, reducedMotion: "reduce" });
  const page = await context.newPage();
  page.on("pageerror", e => console.log("PAGEERROR", e.stack || e.message));
  page.on("console", m => console.log("CONSOLE", m.type(), m.text()));
  await page.goto("http://127.0.0.1:8790/atlas?data=fixtures");
  await page.waitForTimeout(3000);
  console.log("markers", await page.locator('.atlas-marker').count());
  console.log("canvas", await page.locator('canvas').count());
  await browser.close();
})();
