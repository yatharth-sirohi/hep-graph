const { chromium } = require("playwright");
(async () => {
  const exe = "/Users/yatharthsirohi/Library/Caches/ms-playwright/chromium-1217/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing";
  const browser = await chromium.launch({ headless: true, executablePath: exe });
  const context = await browser.newContext({ viewport: {width:1440,height:960} });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:8790/atlas?data=fixtures");
  await page.waitForTimeout(2000);
  const info = await page.evaluate(() => {
    const els = [...document.querySelectorAll('.atlas-marker')];
    return els.map(el => ({id: el.dataset.id, rect: el.getBoundingClientRect().toJSON ? el.getBoundingClientRect() : null, style: getComputedStyle(el).opacity, transform: el.style.transform, parentTransform: el.parentElement && el.parentElement.style.transform}));
  });
  console.log(JSON.stringify(info.slice(0,5), null, 2));
  await browser.close();
})();
