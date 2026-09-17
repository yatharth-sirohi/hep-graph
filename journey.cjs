const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: process.env.HEP_BROWSER_EXECUTABLE });
  const p = await b.newPage({ viewport: { width: 1440, height: 960 } });
  const errs = []; p.on('console', m => m.type()==='error' && errs.push(m.text().slice(0,90)));
  await p.goto(process.env.HEP_URL + '/atlas#/collaboration/dune', { waitUntil: 'networkidle' });
  await p.waitForTimeout(2200);
  await p.locator('#view-on-globe').click();
  await p.waitForTimeout(3500);
  const dots = await p.locator('.atlas-marker.tier-institution').count();
  await p.goto(process.env.HEP_URL + '/atlas?m=collab#/institution/university-of-iowa', { waitUntil: 'networkidle' });
  await p.waitForTimeout(3000);
  const panel = await p.locator('#detail-panel').innerText().catch(()=> '');
  const links = await p.locator('#detail-panel a[href*="source="]').count();
  const hrefs = await p.locator('#detail-panel a[href*="source="]').evaluateAll(a => a.map(x => x.getAttribute('href')));
  await p.screenshot({ path: 'test-results/atlas/journey-iowa.png' });
  console.log(JSON.stringify({ dots, panel: panel.replace(/\n+/g,' | ').slice(0,420), hepGraphLinks: links, hrefs, errors: errs.slice(0,3) }, null, 1));
  await b.close();
})();
