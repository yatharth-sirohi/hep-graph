const { chromium } = require("playwright");
(async () => {
  const exe = "/Users/yatharthsirohi/Library/Caches/ms-playwright/chromium-1217/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing";
  const browser = await chromium.launch({ headless: true, executablePath: exe });
  const context = await browser.newContext({ viewport: {width:1440,height:960}, reducedMotion: "reduce" });
  const page = await context.newPage();
  page.on("pageerror", e => console.log("PAGEERROR", e.stack || e.message));
  await page.goto("http://127.0.0.1:8790/atlas?data=fixtures");
  await page.locator('.atlas-marker[data-id="facility:cern"]').waitFor();
  // native .click() method (dispatches a real trusted-ish click via DOM API, still runs listeners)
  const r1 = await page.locator('.atlas-marker[data-id="facility:cern"]').evaluate(el => { el.click(); return 'called'; });
  console.log('native click result', r1);
  await page.waitForTimeout(500);
  console.log("hash after native click()", await page.evaluate(() => location.hash));

  // Playwright mouse click at element center
  const box = await page.locator('.atlas-marker[data-id="facility:cern"]').boundingBox();
  console.log('box', box);
  await page.mouse.click(box.x + box.width/2, box.y + box.height/2);
  await page.waitForTimeout(500);
  console.log("hash after mouse click", await page.evaluate(() => location.hash));
  console.log("elementFromPoint", await page.evaluate(([x,y]) => { const el = document.elementFromPoint(x,y); return el ? el.outerHTML.slice(0,200) : null; }, [box.x+box.width/2, box.y+box.height/2]));
  await browser.close();
})();
