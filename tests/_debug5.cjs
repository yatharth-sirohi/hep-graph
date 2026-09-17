const { chromium } = require("playwright");
(async () => {
  const exe = "/Users/yatharthsirohi/Library/Caches/ms-playwright/chromium-1217/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing";
  const browser = await chromium.launch({ headless: true, executablePath: exe });
  const context = await browser.newContext({ viewport: {width:1440,height:960} });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:8790/atlas?data=fixtures");
  await page.waitForTimeout(2000);
  const info = await page.evaluate(() => {
    const el = document.querySelector('.atlas-marker[data-id="facility:cern"]');
    if (!el) return {found:false};
    let chain = [];
    let n = el;
    while (n && n !== document.body) {
      const cs = getComputedStyle(n);
      chain.push({tag:n.tagName, cls:n.className, display:cs.display, position:cs.position, w:cs.width, h:cs.height, overflow:cs.overflow, transform:cs.transform});
      n = n.parentElement;
    }
    return {found:true, isConnected: el.isConnected, offsetParent: !!el.offsetParent, chain};
  });
  console.log(JSON.stringify(info, null, 2));
  console.log("globe-container rect", await page.evaluate(() => document.getElementById('globe-container').getBoundingClientRect()));
  console.log("globe-stage rect", await page.evaluate(() => document.getElementById('globe-stage').getBoundingClientRect()));
  console.log("atlas-main rect", await page.evaluate(() => document.getElementById('atlas-main').getBoundingClientRect()));
  await browser.close();
})();
