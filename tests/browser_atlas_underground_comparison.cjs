/* The existing underground chart gains a comparison, not another tour/player. */
const {chromium,webkit}=require('playwright');const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');const {openPrimary}=require('./browser_support/primary.cjs');
const engine=process.env.HEP_BROWSER||'chromium';const base=process.env.HEP_URL||'http://127.0.0.1:8876';
const output=process.env.HEP_ATLAS_OUTPUT||path.join(__dirname,'../test-results/atlas-iterations');fs.mkdirSync(output,{recursive:true});
(async()=>{const browser=await ({chromium,webkit}[engine]).launch({headless:true});const errors=[];
 try{for(const mobile of [false,true]){
  const context=await browser.newContext({viewport:mobile?{width:360,height:780}:{width:1440,height:1000},
   ...(mobile?{isMobile:true,hasTouch:true}:{}),reducedMotion:'reduce'});
  const page=await context.newPage();page.setDefaultTimeout(30000);page.on('pageerror',e=>errors.push(e.message));
  let sourceRound=0;
  if(mobile)await page.route('**/generated/sources.json*',async route=>{
   sourceRound++;
   if(sourceRound===1)return route.fulfill({status:503,body:'Source retry regression'});
   if(sourceRound===2)await new Promise(resolve=>setTimeout(resolve,700));
   return route.continue();
  });
  const sources=[];page.on('request',r=>{if(/\/sources\.json(?:\?|$)/.test(r.url()))sources.push(r.url())});
  const pair='lngs-hall-c,snolab-underground-lab';
  await page.goto(`${base}/atlas?data=generated&theme=projector&uf=${pair}#/view/underground`,{waitUntil:'networkidle'});
  await page.locator('#ug-compare').waitFor();
  const a=page.locator('#ug-flux-a'),b=page.locator('#ug-flux-b');
  assert.equal(await a.inputValue(),'lngs-hall-c');assert.equal(await b.inputValue(),'snolab-underground-lab');
  assert.match(await page.locator('#ug-compare-result').innerText(),/104/);
  assert.match(await page.locator('#ug-compare-math').innerText(),/2\.02/);
  assert.match(await page.locator('#ug-compare-math').innerText(),/dimensionless/);
  assert.match(await page.locator('#ug-compare-values').innerText(),/3\.43.*10⁻⁸/s);
  assert.match(await page.locator('.ug-unit-conversion').innerText(),/10,000/);
  assert.match(await page.locator('#ug-compare-limit').innerText(),/reference surfaces|angular cuts/);
  assert.match(await page.locator('#ug-compare-limit').innerText(),/central values/);
  assert.equal(sources.length,0,'selected sources stay lazy');
  const highlights=()=>page.locator('#ug-chart .ch-point[data-highlight]');
  assert.equal(await highlights().count(),2);assert.equal(await page.locator('#ug-chart .ch-highlight').count(),2);
  assert.match(await page.locator('.ch-label[data-for="site:lngs-hall-c"]').textContent(),/^A ·/);
  assert.match(await page.locator('.ch-point[data-id="site:snolab-underground-lab"]').getAttribute('aria-label'),/Comparison B/);
  await b.selectOption('lngs-hall-c');await page.locator('#ug-compare-error:not([hidden])').waitFor();
  assert.equal(await page.locator('#ug-compare-result').isVisible(),false);assert.equal(await highlights().count(),0);
  await b.selectOption('snolab-underground-lab');await a.selectOption('lsm-frejus');
  assert.match(await page.locator('#ug-compare-result').innerText(),/18\.9/);
  assert.match(await page.locator('#ug-compare-values').innerText(),/6\.25.*10⁻⁹/s);
  assert.match(await page.locator('.ug-unit-conversion').innerText(),/86,400/);
  const chartPoint=page.locator('#ug-chart .ch-point[data-id="site:snolab-underground-lab"]');await chartPoint.focus();
  await page.goBack();await page.waitForFunction(()=>document.querySelector('#ug-flux-a')?.value==='lngs-hall-c');
  assert.equal(await chartPoint.evaluate(n=>n===document.activeElement),true,'same-view Back keeps chart-point focus');
  await page.goForward();await page.waitForFunction(()=>document.querySelector('#ug-flux-a')?.value==='lsm-frejus');
  assert.equal(await chartPoint.evaluate(n=>n===document.activeElement),true,'same-view Forward keeps chart-point focus');
  await a.selectOption('juno-jiangmen-underground-lab');
  assert.match(await page.locator('#ug-compare-values').innerText(),/simulated/i);
  assert.equal(await page.locator('.ch-point[data-id="site:juno-jiangmen-underground-lab"] .ch-mark.is-hollow').count(),1);
  await a.selectOption('lngs-hall-c');
  const saved=page.url();await page.reload({waitUntil:'networkidle'});await page.locator('#ug-compare').waitFor();
  assert.equal(await a.inputValue(),'lngs-hall-c');assert.equal(await b.inputValue(),'snolab-underground-lab');
  await page.locator('#ug-compare-sources > summary').focus();await page.keyboard.press('Enter');
  if(mobile){
   await page.waitForFunction(()=>document.querySelector('#ug-compare-source-body')?.dataset.state==='error');
   await page.getByRole('button',{name:'Retry selected sources',exact:true}).focus();await page.keyboard.press('Enter');
   assert.equal(await page.locator('#ug-compare-sources > summary').evaluate(n=>n===document.activeElement),true,'Retry retains focus before removing its button');
   // Change the selection while the retry is still loading: stale A must never win.
   await a.selectOption('lsm-frejus');
   await page.waitForFunction(()=>/^A · LSM/.test(document.querySelector('#ug-compare-source-body article h4')?.textContent||''));
   await a.selectOption('lngs-hall-c');
   await page.waitForFunction(()=>document.querySelector('#ug-compare-source-body article h4')?.textContent==='A · LNGS Hall C');
  }
  await page.waitForFunction(()=>document.querySelector('#ug-compare-source-body')?.dataset.state==='ready');
  const evidence=page.locator('#ug-compare-source-body');
  assert.match(await evidence.innerText(),/cos.*0\.4/s);assert.match(await evidence.innerText(),/spherical|sphere/);
  const papers=['https://arxiv.org/abs/1808.04207','https://arxiv.org/abs/0902.2776'];
  for(let i=0;i<2;i++){
   const source=evidence.locator(`a[href="${papers[i]}"]`).first();await source.waitFor();
   if((engine==='chromium'&&!mobile)||(engine==='webkit'&&mobile)){
    await openPrimary(context,page,source,{url:papers[i],engine,viewport:mobile?'360':'desktop',output,artifactName:`flux-paper-${i+1}`});
    const response=await context.request.get(papers[i]);assert.equal(response.status(),200);
    assert((await response.text()).includes(i===0?'3.432':'3.31'),'primary abstract contains the recorded measurement');
   }
  }
  // Assert the actual destination UI; an external HTML popup can leave a browser navigation barrier pending.
  await page.getByRole('link',{name:'Open LNGS Hall C',exact:true}).click({noWaitAfter:true});
  await page.locator('#detail-panel h2').waitFor();assert.equal(await page.locator('#detail-panel h2').innerText(),'LNGS Hall C');
  assert.equal(new URL(page.url()).searchParams.has('uf'),false);await page.goBack();await page.locator('#ug-compare').waitFor();
  assert.equal(await a.inputValue(),'lngs-hall-c');assert.equal(await b.inputValue(),'snolab-underground-lab');
  assert.equal(new URL(page.url()).searchParams.get('uf'),pair);
  await page.setViewportSize(mobile?{width:400,height:780}:{width:1280,height:900});
  await page.waitForFunction(()=>document.querySelectorAll('#ug-chart .ch-highlight').length===2);
  assert.match(await page.locator('.ch-label[data-for="site:lngs-hall-c"]').textContent(),/^A ·/);
  await page.setViewportSize(mobile?{width:360,height:780}:{width:1440,height:1000});
  await page.locator('#ug-compare').scrollIntoViewIfNeeded();
  assert(await page.locator('#ug-compare').evaluate(n=>n.scrollWidth<=n.clientWidth+1));
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  await page.screenshot({path:path.join(output,`${engine}-${mobile?'360':'desktop'}-underground-compare.png`)});
  if(!mobile&&engine==='chromium'){
   await page.locator('#export-btn').click();const download=page.getByRole('button',{name:'Download PNG',exact:true});
   await page.waitForFunction(()=>!document.querySelector('.export-download')?.disabled);
   await page.locator('.export-image-notes > summary').click();
   assert.match(await page.locator('.export-image-notes').innerText(),/Central-value comparison.*2\.02/s);
   const reopen=new URL(await page.locator('.export-image-notes a[href*="uf="]').getAttribute('href'));
   assert.equal(reopen.searchParams.get('uf'),pair);assert.equal(reopen.hash,'#/view/underground');
   const savedImage=page.waitForEvent('download');await download.click();
   const file=path.join(output,'cycle10-underground-comparison.png');await (await savedImage).saveAs(file);
   const bytes=fs.readFileSync(file);assert.equal(bytes.subarray(1,4).toString(),'PNG');assert(bytes.readUInt32BE(16)>500);
   await page.getByRole('button',{name:'Close export',exact:true}).click();
  }
  await page.goto(`${base}/atlas?data=generated&uf=missing,snolab-underground-lab#/view/underground`,{waitUntil:'networkidle'});
  await page.locator('#ug-compare-error:not([hidden])').waitFor();assert.equal(await page.locator('#ug-compare-result').isVisible(),false);
  await a.selectOption('lngs-hall-c');assert.match(await page.locator('#ug-compare-result').innerText(),/104/);
  await page.goto(`${base}/atlas?data=generated&step=6&present=1&uf=${pair}#/tour/going-underground-dark-matter`,{waitUntil:'networkidle'});
  await page.locator('#ug-compare').waitFor();await page.locator('.tour-question').waitFor();
  if(mobile)await page.getByRole('button',{name:'Hide text',exact:true}).click();
  // macOS headless Chromium does not synthesize native popup arrow selection, even on a bare select.
  // Native type-ahead does select an option and also exercises the presenter's B/blank shortcut boundary.
  const before=await a.inputValue();await a.focus();await page.keyboard.press('b');
  assert.notEqual(await a.inputValue(),before,'native select keys change the comparison');
  assert.equal(new URL(page.url()).searchParams.get('step'),'6','select keys must not change the tour step');
  assert.equal(await page.locator('#tour-blank').evaluate(n=>n.hidden),true,'native B selection must not blank the presenter');
  assert.equal(await a.evaluate(n=>n===document.activeElement),true,'URL update retains selector focus');
  assert.equal(new URL(page.url()).searchParams.get('uf').split(',')[0],await a.inputValue());
  assert.equal(await page.locator('#ug-chart .ch-point').count(),15);
  assert.equal(new URL(saved).searchParams.get('theme'),'projector');
  if(!mobile){
   await page.goto(`${base}/atlas?data=generated&y=1990#/view/energy-frontier`,{waitUntil:'networkidle'});
   await page.locator('#ef-chart .ch-point').first().waitFor();
   assert.equal(await page.locator('#ef-chart .ch-highlight').count(),0,'other charts keep their existing marks');
   assert(await page.locator('#ef-chart .ch-point.is-faded').count()>0);
   assert.match(await page.locator('#ef-chart .ch-xmarker-label').textContent(),/1990/);
   const other=page.locator('#ef-chart .ch-point').first();const id=await other.getAttribute('data-id');await other.focus();
   const oldSvg=await page.locator('#ef-chart .ch-svg').elementHandle();await page.setViewportSize({width:1024,height:900});
   await page.waitForFunction(node=>!node.isConnected,oldSvg);await oldSvg.dispose();
   assert.equal(await page.locator(`#ef-chart .ch-point[data-id="${id}"]`).evaluate(n=>n===document.activeElement),true,'the existing chart resize still retains focus');
  }
  await context.close();console.log(`PASS ${engine} ${mobile?'360px mobile':'desktop'}: flux ratios, A/B chart, units, types, sources, keyboard, invalid recovery, reload and Back`);
 }assert.deepEqual(errors,[])}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
