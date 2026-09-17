const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: process.env.HEP_BROWSER_EXECUTABLE });
  const p = await b.newPage({ viewport: { width: 1440, height: 960 } });
  const errs = []; p.on('console', m => m.type()==='error' && errs.push(m.text().slice(0,100)));
  await p.goto(process.env.HEP_URL + '/atlas', { waitUntil: 'networkidle' });
  await p.waitForTimeout(2500);
  const out = {};
  for (const [label, name] of [['results','Results'],['documents','Documents'],['topics','Topics']]) {
    await p.getByRole('button', { name }).first().click().catch(()=>{});
    await p.waitForTimeout(1500);
    out[label] = await p.locator('#mode-panel li, #mode-panel tr, #mode-panel .result-card, #mode-panel a').count();
  }
  await p.goto(process.env.HEP_URL + '/atlas#/result/atlas-higgs-observation-2012', { waitUntil: 'networkidle' });
  await p.waitForTimeout(2200);
  out.resultDeepLink = await p.locator('#detail-panel h2').first().textContent().catch(()=>null);
  console.log(JSON.stringify({ out, errors: errs.slice(0,3) }));
  await b.close();
})();
