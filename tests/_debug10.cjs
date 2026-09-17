const { chromium } = require("playwright");
(async () => {
  const exe = "/Users/yatharthsirohi/Library/Caches/ms-playwright/chromium-1217/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing";
  const browser = await chromium.launch({ headless: true, executablePath: exe });
  const context = await browser.newContext({ viewport: {width:1440,height:960}, reducedMotion: "reduce" });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:8790/atlas?data=fixtures");
  await page.locator('.atlas-marker[data-id="facility:cern"]').waitFor();
  const info = await page.evaluate(() => {
    const gc = document.getElementById('globe-container');
    function describe(el, depth) {
      if (!el || depth > 4) return null;
      const cs = getComputedStyle(el);
      return {
        tag: el.tagName, cls: el.className, id: el.id,
        position: cs.position, zIndex: cs.zIndex, pointerEvents: cs.pointerEvents,
        children: [...el.children].map(c => describe(c, depth+1)),
      };
    }
    return describe(gc, 0);
  });
  console.log(JSON.stringify(info, null, 1));
  await browser.close();
})();
