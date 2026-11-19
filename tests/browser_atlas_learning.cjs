/* Connected learning regression against real generated Atlas data.
   HEP_URL=http://127.0.0.1:8876 HEP_BROWSER=chromium|webkit node tests/browser_atlas_learning.cjs
   Output includes 360px screenshots; no network or data mocks. */
const { chromium, webkit } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const base = process.env.HEP_URL || 'http://127.0.0.1:8876';
const engineName = process.env.HEP_BROWSER || 'chromium';
const out = process.env.HEP_ATLAS_OUTPUT || path.join(__dirname,'../test-results/learning');
fs.mkdirSync(out,{recursive:true});
const questions = [
  ['Why do neutrino beams go through the Earth?', 'beam-section', 'neutrino-beams-through-the-earth', 5],
  ['Why are some detectors underground?', 'underground', 'going-underground-dark-matter', 6],
  ['How did ATLAS and CMS establish the Higgs discovery?', 'results-story', 'higgs-hunt', 6],
];
(async()=>{
 const browser=await ({chromium,webkit}[engineName]).launch({headless:true});
 const failures=[];
 try {
  for(const mobile of (process.env.HEP_MOBILE_ONLY ? [true] : [false,true])) {
   const context=await browser.newContext({viewport:mobile?{width:360,height:780}:{width:1440,height:1000},
     ...(mobile?{isMobile:true,hasTouch:true}:{}),reducedMotion:'reduce'});
   const page=await context.newPage();
   page.on('pageerror',e=>failures.push(e.message));
   page.setDefaultTimeout(45000);
   const checkpoint=async()=>{
    const q=page.locator('.tour-question');
    await q.waitFor({state:'visible'});
    assert.match(await q.innerText(),/predict/i);
    await q.getByRole('button',{name:'Show answer',exact:true}).click();
    await page.waitForFunction(()=>!document.querySelector('.tour-answer').hidden);
    assert((await page.locator('.tour-answer').innerText()).length>50);
   };
   const noOverflow=async()=>{
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1),'document overflows');
    const stage=page.locator('#view-host');
    assert(await stage.evaluate(n=>n.scrollWidth<=n.clientWidth+1),'view overflows');
   };
   for(const [question,view,tour,step] of questions){
    await page.goto(`${base}/atlas`);
    await page.waitForFunction(()=>document.getElementById('tours-mode-btn')?.hidden===false);
    if(!await page.locator('#start-card').isVisible()) await page.locator('#start-here-link').click();
    await page.getByRole('link',{name:question,exact:false}).click();
    await page.waitForURL(u=>u.hash===`#/tour/${tour}`&&u.searchParams.get('step')===String(step));
    await page.locator('#view-title').waitFor({state:'visible'});
    await page.waitForFunction(v=>document.querySelector('#view-body')?.querySelector(v),view==='beam-section'?'.bs-svg':'svg');
    if(mobile) {
     const visual=page.locator(view==='beam-section'?'.bs-figure':view==='underground'?'.ug-figure':'.rs-stage');
     assert((await visual.boundingBox()).y < (await page.locator('#tour-card').boundingBox()).y, 'question must expose its visual above the phone sheet');
    }
    await checkpoint();
    await noOverflow();
    if(view==='results-story') {
     if(mobile) await page.getByRole('button',{name:'Hide text',exact:true}).click();
     await page.locator('.rs-mark[data-id="result:atlas-higgs-observation-2012"]').first().click();
     await page.locator('.rs-card').getByRole('link',{name:'Open the result',exact:true}).click();
     await page.locator('.result-evidence').waitFor();
     assert.match(page.url(), /#\/result\/atlas-higgs-observation-2012$/);
    }
   }
   // Open the beam question again, then operate the actual control with a keyboard.
   await page.goto(`${base}/atlas?step=5&e=2.5#/tour/neutrino-beams-through-the-earth`);
   await page.locator('#osc-energy').waitFor();
   if(mobile) {
    const positions=await page.evaluate(()=>({figure:document.querySelector('.bs-figure').getBoundingClientRect().top,lede:document.querySelector('.bs-lede').getBoundingClientRect().top}));
    assert(positions.figure < positions.lede, 'the question must land on the beam visual on a phone');
   }
   await checkpoint();
   const range=page.locator('#osc-energy');
   await range.scrollIntoViewIfNeeded(); await range.focus();
   await range.press('ArrowRight');
   assert.equal(await range.inputValue(),'2.51');
   assert.equal(await range.evaluate(n=>n===document.activeElement),true,'energy change loses keyboard focus');
   assert.match(await page.locator('#osc-readout').innerText(),/2.51 GeV/);
   await page.locator('.osc-method summary').click();
   assert.match(await page.locator('.osc-method').innerText(),/1.267/);
   assert.match(await page.locator('.osc-method').innerText(),/eV²/);
   await page.locator('#osc-baseline').selectOption('lbnf');
   await page.waitForURL(/#\/view\/beam-section\/lbnf$/);
   await page.waitForFunction(()=>document.querySelector('#osc-baseline')?.value==='lbnf');
   await page.locator('#osc-energy-number').fill('2.5');
   await page.locator('#osc-energy-number').press('Tab');
   assert.match(await page.locator('#osc-readout').innerText(),/2.5 GeV.*99.67%/);
   assert.match(await page.locator('.osc-maximum').innerText(),/2.591 GeV/);
   assert.equal(await page.locator('.osc-selected-point').count(),1);
   assert.equal(await page.locator('.osc-max-point').count(),1);
   await page.getByRole('button',{name:'Try the first maximum'}).click();
   assert.match(await page.locator('#osc-readout').innerText(),/2.59 GeV.*100.00%/);
   const shared=page.url();
   assert.equal(new URL(shared).searchParams.get('e'),'2.59');
   await page.reload();
   await page.waitForFunction(()=>document.querySelector('#osc-energy')?.value==='2.59');
   await noOverflow();
   await page.locator('#osc-energy').scrollIntoViewIfNeeded();
   await page.screenshot({path:path.join(out,`${engineName}-${mobile?'360':'desktop'}-lab.png`)});
   // Keyboard source disclosure, then Results and Back must restore the changed lab.
   await page.locator('.osc-method summary').focus(); await page.keyboard.press('Enter');
   assert.equal(await page.locator('.osc-method').evaluate(n=>n.open),true);
   await page.goto(`${base}/atlas?m=results&rt=higgs-physics`);
   await page.locator('#mode-panel a[href="#/result/atlas-higgs-observation-2012"]').first().click();
   await page.locator('.result-evidence').waitFor();
   await page.waitForURL(/#\/result\/atlas-higgs-observation-2012$/);
   if(!mobile) assert((await page.locator('.result-where').boundingBox()).y < 880, 'evidence must preserve the first-screen place and companion context');
   assert.match(await page.locator('.evidence-significance').innerText(),/Observed.*5.9σ.*Expected.*4.9σ/s);
   const primary=page.locator('.evidence-items .evidence-source').first();
   assert.match(await primary.getAttribute('href'),/1207\.7214v1#page=11$/);
   const primaryURL=await primary.getAttribute('href');
   // Real click: the popup requests the versioned primary PDF (download on WebKit).
   const requested=context.waitForEvent('request',{predicate:r=>r.url().startsWith(primaryURL.split('#')[0]),timeout:30000});
   await primary.click(); await requested;
   const response=await context.request.get(primaryURL.split('#')[0]);
   assert.equal(response.status(),200,'primary paper unavailable');
   assert.match(response.headers()['content-type'],/pdf/);
   const body=await response.body(); assert.equal(body.subarray(0,4).toString(),'%PDF');
   await page.getByRole('link',{name:'Read CMS’s evidence trail'}).click();
   await page.waitForURL(/#\/result\/cms-higgs-boson-observation-2012$/);
   await page.waitForFunction(()=>document.querySelector('.evidence-significance')?.textContent.includes('5.8σ'));
   assert.match(await page.locator('.evidence-significance').innerText(),/Observed.*5.0σ.*Expected.*5.8σ/s);
   const cmsURL=await page.locator('.evidence-items .evidence-source').first().getAttribute('href');
   assert.match(cmsURL,/1207\.7235v1#page=13$/);
   const cmsRequested=context.waitForEvent('request',{predicate:r=>r.url().startsWith(cmsURL.split('#')[0]),timeout:45000});
   await page.locator('.evidence-items .evidence-source').first().click(); await cmsRequested;
   const cmsResponse=await context.request.get(cmsURL.split('#')[0]);
   assert.equal(cmsResponse.status(),200); assert.match(cmsResponse.headers()['content-type'],/pdf/);
   await page.locator('.result-evidence').scrollIntoViewIfNeeded();
   await page.screenshot({path:path.join(out,`${engineName}-${mobile?'360':'desktop'}-evidence.png`)});
   await page.goBack();
   await page.waitForURL(/#\/result\/atlas-higgs-observation-2012$/);
   await page.goBack();
   await page.waitForURL(/m=results/);
   // Copy/paste and actual in-app navigation/Back preserve the lab state.
   await page.goto(shared);
   await page.waitForFunction(()=>document.querySelector('#osc-energy')?.value==='2.59');
   await page.locator('#start-here-link').click();
   await page.locator('[data-start-action=results]').click();
   await page.goBack();
   await page.waitForFunction(()=>document.querySelector('#osc-energy')?.value==='2.59');
   await noOverflow();
   await page.goto(`${base}/atlas?e=NaN#/view/beam-section/lbnf`);
   await page.waitForFunction(()=>document.querySelector('#osc-energy')?.value==='0.6');
   assert.equal(await page.locator('#osc-readout').innerText().then(t=>t.includes('NaN')),false);
   await page.goto(`${base}/atlas#/result/atlas-nature-higgs-2022`);
   await page.locator('#detail-panel h2').waitFor();
   assert.equal(await page.locator('.result-evidence').count(),0,'uncurated results must not acquire invented evidence');
   console.log(`PASS ${engineName} ${mobile?'360px mobile':'desktop'}: three questions, reveals, energy, explanation, baselines, shared/deep links, Back, primary paper`);
   await context.close();
  }
  assert.deepEqual(failures,[],'browser errors');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
