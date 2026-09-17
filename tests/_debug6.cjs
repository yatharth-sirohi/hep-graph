const { chromium } = require("playwright");
(async () => {
  const exe = "/Users/yatharthsirohi/Library/Caches/ms-playwright/chromium-1217/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing";
  const browser = await chromium.launch({ headless: true, executablePath: exe });
  const context = await browser.newContext({ viewport: {width:1440,height:960}, reducedMotion: "reduce" });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:8790/atlas?data=fixtures");
  await page.waitForTimeout(2000);
  const el = page.locator('.atlas-marker[data-id="facility:cern"]');
  console.log("count", await el.count());
  console.log("visible?", await el.isVisible());
  const style = await el.evaluate(n => ({opacity:getComputedStyle(n).opacity, visibility:getComputedStyle(n).visibility, display:getComputedStyle(n).display, inlineStyle:n.getAttribute('style'), rect: (()=>{const r=n.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height};})()}));
  console.log(style);
  await browser.close();
})();
