const { chromium } = require("playwright");
(async () => {
  const exe = "/Users/yatharthsirohi/Library/Caches/ms-playwright/chromium-1217/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing";
  const browser = await chromium.launch({ headless: true, executablePath: exe });
  const page = await browser.newPage();
  page.on("console", msg => console.log("CONSOLE", msg.type(), msg.text()));
  page.on("pageerror", err => console.log("PAGEERROR", err.message));
  page.on("requestfailed", req => console.log("REQFAIL", req.url(), req.failure() && req.failure().errorText));
  await page.goto("http://127.0.0.1:8790/atlas?data=fixtures");
  await page.waitForTimeout(4000);
  console.log("canvas count", await page.locator("canvas").count());
  console.log("markers count", await page.locator(".atlas-marker").count());
  const html = await page.content();
  require("fs").writeFileSync("/tmp/atlas_dump.html", html);
  await browser.close();
})();
