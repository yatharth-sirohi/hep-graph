const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: process.env.HEP_BROWSER_EXECUTABLE });
  const out = [];
  for (const route of ['#/facility/fermilab','#/experiment/dune','#/collaboration/dune','#/topic/neutrino-oscillations','#/result/atlas-higgs-observation-2012','#/institution/university-of-iowa']) {
    const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
    await p.goto(process.env.HEP_URL + '/atlas' + route, { waitUntil: 'networkidle' });
    await p.waitForTimeout(2200);
    const h2 = await p.locator('#detail-panel h2').first().textContent().catch(()=>null);
    out.push({ route, panel: h2 });
    await p.close();
  }
  console.log(JSON.stringify(out));
  await b.close();
})();
