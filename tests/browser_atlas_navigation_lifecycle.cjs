/* Do not wait for startup readiness in the stress section: a learner may leave
   a cold page immediately. Then check a normal load and real history recovery. */
const {chromium,webkit}=require('playwright');
const assert=require('node:assert/strict');
const engine=process.env.HEP_BROWSER||'webkit';
const base=process.env.HEP_URL||'http://127.0.0.1:8876';
(async()=>{
 const browser=await ({chromium,webkit}[engine]).launch({headless:true});
 const errors=[];
 const options={viewport:{width:360,height:780},isMobile:true,hasTouch:true,reducedMotion:'reduce'};
 try {
  const stress=await browser.newContext(options);
  const page=await stress.newPage();page.setDefaultTimeout(30000);
  page.on('pageerror',error=>errors.push(error.message));
  for(let i=0;i<4;i++) {
   await page.goto(`${base}/atlas?data=generated&theme=projector&embed=1&step=1#/tour/higgs-hunt`);
   await page.locator('#tour-card').waitFor();
   await page.goto(`${base}/atlas?data=generated&theme=projector#/result/atlas-higgs-observation-2012`);
   await page.locator('#detail-panel h2').waitFor();
  }
  await stress.close();
  const context=await browser.newContext(options);
  const restored=await context.newPage();restored.setDefaultTimeout(30000);
  restored.on('pageerror',error=>errors.push(error.message));
  const assets=new Set();
  restored.on('response',response=>{
   if(response.ok()&&/earth-dark-4096.webp|countries-borders-110m.json/.test(response.url())) assets.add(new URL(response.url()).pathname);
  });
  await restored.goto(`${base}/atlas?e=2.61&le=1#/view/beam-section/lbnf`,{waitUntil:'networkidle'});
  await restored.locator('#osc-energy').waitFor();
  assert.equal(assets.size,2,'normal cold loads must still load both scenery assets');
  await restored.locator('#osc-energy').focus();await restored.keyboard.press('ArrowRight');
  assert.equal(await restored.locator('#osc-energy').inputValue(),'2.62');
  // Startup must not register two history listeners. Observe the actual route module
  // while navigating inside this document; one browser gesture means one update.
  await restored.evaluate(async()=>{
    const state=await import('/atlas/js/state.js');
    window.__historyProbe={pop:0,updates:[]};
    window.addEventListener('popstate',()=>window.__historyProbe.pop++);
    state.subscribe(s=>window.__historyProbe.updates.push({energy:s.energy,mode:s.mode,entity:s.entity,keepRatio:s.keepRatio}));
  });
  await restored.locator('#start-here-link').click();
  await restored.locator('[data-start-action=results]').click();
  await restored.waitForURL(/m=results/);await restored.locator('#mode-panel').waitFor();
  for(const direction of ['back','forward','back']) {
    await restored.evaluate(()=>window.__historyProbe={pop:0,updates:[]});
    if(direction==='back') {
      await restored.goBack();
      await restored.waitForFunction(()=>document.querySelector('#osc-energy')?.value==='2.62');
      assert.equal(await restored.locator('#osc-keep-ratio').isChecked(),true);
    } else {
      await restored.goForward();await restored.waitForURL(/m=results/);
      await restored.locator('#mode-panel').waitFor();
    }
    const history=await restored.evaluate(()=>window.__historyProbe);
    assert.equal(history.pop,1,`one native ${direction} event`);
    assert.equal(history.updates.length,1,`one route update per ${direction} gesture`);
    if(direction==='back') {
      assert.equal(history.updates[0].energy,2.62);assert.equal(history.updates[0].keepRatio,true);
      assert.equal(await restored.locator('#osc-energy').count(),1);
    } else assert.equal(history.updates[0].mode,'results');
  }
  await restored.goto(`${base}/atlas?e=.6#/view/beam-section/j-parc-neutrino`,{waitUntil:'networkidle'});
  await restored.locator('#osc-energy').waitFor();
  await restored.goBack({waitUntil:'networkidle'});
  await restored.waitForFunction(()=>document.querySelector('#osc-energy')?.value==='2.62');
  assert.equal(await restored.locator('#osc-keep-ratio').isChecked(),true);
  await restored.goForward({waitUntil:'networkidle'});
  await restored.waitForFunction(()=>document.querySelector('#osc-energy')?.value==='0.6');
  assert.equal(await restored.locator('#osc-keep-ratio').isChecked(),false);
  await context.close();
  // Starting requests earlier must not make scenery a prerequisite for learning.
  const slow=await browser.newContext(options);
  const delayed=await slow.newPage();delayed.setDefaultTimeout(30000);
  delayed.on('pageerror',error=>errors.push(error.message));
  let release;const gate=new Promise(resolve=>{release=resolve});let waiting=0;
  await slow.route(/earth-dark-4096\.webp|countries-borders-110m\.json/,async route=>{
   waiting++;await gate;await route.continue();
  });
  try {
   await delayed.goto(`${base}/atlas`,{waitUntil:'domcontentloaded'});
   await delayed.locator('#globe-container canvas').waitFor();
   await delayed.waitForFunction(()=>document.getElementById('tours-mode-btn')?.hidden===false);
   if(!await delayed.locator('#start-card').isVisible()) await delayed.locator('#start-here-link').click();
   await delayed.getByRole('link',{name:'Why do neutrino beams go through the Earth?',exact:false}).click();
   await delayed.locator('#osc-energy').waitFor();
   assert.equal(waiting,2,'optional scenery requests start without blocking the question or lab');
   assert.equal(await delayed.locator('#osc-energy').inputValue(),'2.5');
   await delayed.locator('#osc-energy').focus();await delayed.keyboard.press('ArrowRight');
   assert.equal(await delayed.locator('#osc-energy').inputValue(),'2.51');
   release();await delayed.waitForLoadState('networkidle');
  } finally {release();await slow.close()}
  assert.deepEqual(errors,[],'cold exits must not start work on a departing document');
  console.log(`PASS ${engine} 360px: rapid cold exits, normal/slow assets, keyboard energy, single Back/forward updates, state restoration, no browser errors`);
 } finally {await browser.close()}
})().catch(error=>{console.error(error);process.exitCode=1});
