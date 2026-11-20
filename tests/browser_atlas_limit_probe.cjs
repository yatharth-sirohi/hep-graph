/* Published LZ limit → hypothetical point → interpretation → exact primary. */
const {chromium,webkit}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');
const {openPrimary}=require('./browser_support/primary.cjs');
const engine=process.env.HEP_BROWSER||'chromium',base=process.env.HEP_URL||'http://127.0.0.1:8876';
const out=process.env.HEP_ATLAS_OUTPUT||path.join(__dirname,'../test-results/atlas-iterations/cycle18');fs.mkdirSync(out,{recursive:true});
(async()=>{const options={headless:true};if(engine==='chromium'&&process.env.HEP_BROWSER_EXECUTABLE)options.executablePath=process.env.HEP_BROWSER_EXECUTABLE;const browser=await({chromium,webkit}[engine]).launch(options);console.log('BROWSER',engine,browser.version());let active,size;const errors=[];
 try{for(const mobile of(process.env.HEP_MOBILE_ONLY?[true]:[false,true])){
  const context=await browser.newContext({viewport:mobile?{width:360,height:780}:{width:1440,height:1000},...(mobile?{isMobile:true,hasTouch:true}:{}),reducedMotion:'reduce',acceptDownloads:true});
  const page=await context.newPage();active=page;size=mobile?'360':'desktop';page.setDefaultTimeout(20000);page.on('pageerror',e=>errors.push(e.message));
  await page.goto(`${base}/atlas?data=generated&theme=projector#/view/limits/wimp-si`,{waitUntil:'networkidle'});await page.locator('.lm-svg').waitFor();
  const lab=page.locator('.limit-probe');assert.equal(await lab.count(),1,'the published limit chart needs an interpretation exercise');
  const disclosure=lab.locator(':scope>summary'),mass=page.locator('#limit-probe-mass'),factor=page.locator('#limit-probe-factor');
  const factorValue=async()=>factor.locator('input:checked').inputValue();
  async function setFactor(value){
   await factor.locator(`input[value="${value}"]`).focus();await page.keyboard.press('Space');
   await page.waitForFunction(value=>{
    const selected=document.querySelector('#limit-probe-factor input:checked');
    const mass=document.querySelector('#limit-probe-mass')?.value;
    return Number(selected?.value)===Number(value)&&new URL(location.href).searchParams.get('wp')===`${mass},${Number(value)}`;
   },value);
  }
  const check=page.locator('#limit-probe-check'),feedback=lab.locator('.limit-probe-feedback');
  const plot=page.locator('.lm-plot'),overlay=plot.locator('.lm-probe-overlay');
  const points=()=>page.locator('.lm-series [aria-label]').evaluateAll(ns=>ns.map(n=>n.getAttribute('aria-label')));
  const publishedPoints=await points();assert(publishedPoints.length>=68);
  assert.equal(await lab.getAttribute('open'),null);assert.equal(await overlay.count(),0);
  await disclosure.focus();await page.keyboard.press('Enter');await overlay.waitFor();
  assert.equal(new URL(page.url()).searchParams.get('wp'),'40,10');assert.equal(await mass.inputValue(),'40');
  assert.equal(await lab.locator('.limit-probe-choices input:checked').count(),0);assert.equal(await check.isDisabled(),true);
  assert.match(await page.locator('#limit-probe-published').innerText(),/2\.182.*10\^-48.*cm².*40/s);
  assert.match(await page.locator('#limit-probe-model').innerText(),/2\.182.*10\^-47.*10 ×/s);
  async function choice(value){const radio=lab.locator(`input[value="${value}"]`);await radio.focus();await page.keyboard.press('Space');await check.focus();await page.keyboard.press('Enter');await feedback.waitFor()}
  await choice('below');assert.equal(await feedback.getAttribute('data-outcome'),'revise');assert.match(await feedback.innerText(),/Excluded at 90% CL/);
  await setFactor('.1');assert.equal(await feedback.isVisible(),false);assert.equal(await check.isDisabled(),true);assert.equal(await lab.locator('.limit-probe-choices input:checked').count(),0);
  await choice('above');assert.equal(await feedback.getAttribute('data-outcome'),'revise');assert.match(await feedback.innerText(),/Not excluded.*not a detection/s);
  const above=lab.locator('input[value="above"]');await above.focus();await page.keyboard.press('ArrowDown');assert.equal(await lab.locator('input[value="below"]').isChecked(),true);assert.equal(await feedback.isVisible(),false);
  await check.focus();await page.keyboard.press('Space');assert.equal(await feedback.getAttribute('data-outcome'),'supported');
  await factor.locator('input[value=".1"]').focus();await page.keyboard.press('ArrowRight');assert.equal(await factorValue(),'1');assert.equal(await feedback.isVisible(),false);
  await choice('boundary');assert.equal(await feedback.getAttribute('data-outcome'),'supported');assert.match(await feedback.innerText(),/boundary.*not.*detection/s);
  async function markerBounds(){const ok=await plot.evaluate(el=>{const svg=el.querySelector('svg'),frame=svg.querySelector('.lm-frame').getBBox();return [...svg.querySelectorAll('.lm-probe-overlay circle,.lm-probe-overlay path')].every(n=>{const b=n.getBBox();return b.x>=frame.x&&b.x+b.width<=frame.x+frame.width&&b.y>=frame.y&&b.y+b.height<=frame.y+frame.height})});assert(ok,'both symbols stay inside the plotted range')}
  await markerBounds();
  const masses=await mass.locator('option').evaluateAll(ns=>ns.map(n=>n.value));assert.equal(masses.length,26);
  const massIndex=masses.indexOf('40');await lab.getByRole('button',{name:'Next published mass',exact:true}).focus();await page.keyboard.press('Enter');assert.equal(await mass.inputValue(),masses[massIndex+1]);await lab.getByRole('button',{name:'Previous published mass',exact:true}).focus();await page.keyboard.press('Space');assert.equal(await mass.inputValue(),'40');
  for(const m of masses)for(const f of ['.1','10']){await mass.selectOption(m);await setFactor(f);await markerBounds();await page.waitForTimeout(300)}
  assert.deepEqual(await points(),publishedPoints,'the exercise must preserve every published mark and value');
  await mass.selectOption('40');await setFactor('.1');await choice('below');
  await page.locator('.limit-probe-locate').focus();await page.keyboard.press('Enter');
  assert.match(await page.locator(':focus').getAttribute('aria-label'),/LZ.*40 GeV\/c²/s);await page.keyboard.press('ArrowRight');
  assert.match(await page.locator('.lm-readout').innerText(),/90% CL upper limit/);
  await page.screenshot({path:path.join(out,`${engine}-${size}-limit-probe-chart.png`)});
  await lab.locator('.limit-probe-controls').scrollIntoViewIfNeeded();assert(await lab.evaluate(n=>n.scrollWidth<=n.clientWidth+1));
  assert(await lab.locator('select,button').evaluateAll(ns=>ns.every(n=>n.getBoundingClientRect().height>=44)));
  await page.screenshot({path:path.join(out,`${engine}-${size}-limit-probe-controls.png`)});
  await setFactor('10');await choice('above');await page.evaluate(async()=>{const s=await import('/atlas/js/state.js');s.navigate({wimpProbe:'39,10'})});await page.locator('.limit-probe-notice').waitFor();assert.equal(await feedback.isVisible(),false,'a refused mass starts unanswered even when its fallback matches the old setup');assert.equal(await lab.locator('.limit-probe-choices input:checked').count(),0);await setFactor('.1');
  const saved=page.url();assert.equal(new URL(saved).searchParams.get('wp'),'40,0.1','copy the accepted URL after the native radio change has committed');await mass.focus();await mass.evaluate(n=>window.__limitMass=n);
  await page.evaluate(async()=>{const s=await import('/atlas/js/state.js');s.navigate({wimpProbe:'40,10'})});assert.equal(await factorValue(),'10');assert.equal(await feedback.isVisible(),false);
  await page.goBack();assert.equal(await factorValue(),'.1');assert.equal(await mass.evaluate(n=>n===window.__limitMass),true);assert.equal(await mass.evaluate(n=>n===document.activeElement),true);
  // A copied link opens an independent document, as it does in a new browser tab.
  const copied=await context.newPage();copied.on('pageerror',e=>errors.push(e.message));
  await copied.goto(saved,{waitUntil:'networkidle'});await copied.locator('.lm-probe-overlay').waitFor();
  assert.equal(await copied.locator('#limit-probe-mass').inputValue(),'40');assert.equal(await copied.locator('#limit-probe-factor input:checked').inputValue(),'.1');
  assert.equal(await copied.locator('.limit-probe-choices input:checked').count(),0);assert.equal(await copied.locator('.limit-probe-feedback').isVisible(),false);
  await copied.close();await page.bringToFront();assert.equal(await overlay.count(),1);
  await lab.locator('.limit-probe-method>summary').focus();await page.keyboard.press('Enter');
  const method=lab.locator('.limit-probe-method');for(const phrase of ['not a 90% probability','no interpolation','power-constrained','limit_unconstr'])assert((await method.innerText()).includes(phrase),phrase);
  const primary=method.locator('a[href="https://arxiv.org/pdf/2410.17036v3#page=8"]');
  if((engine==='chromium'&&!mobile)||(engine==='webkit'&&mobile))await openPrimary(context,page,{click:async()=>{await primary.focus();await page.keyboard.press('Enter')}},{url:'https://arxiv.org/pdf/2410.17036v3#page=8',engine,viewport:size,output:out,artifactName:'lz-2024-limit',requirePDF:true});
  await page.bringToFront();const trigger=page.locator(mobile?'#phone-export-btn':'#export-btn');await trigger.focus();await page.keyboard.press('Enter');await page.locator('#export-popover').waitFor();
  await page.waitForFunction(()=>!document.querySelector('.export-download')?.disabled&&window.__hepAtlasExport?.last?.footerLines.some(n=>n.includes('Hypothetical:')));
  const meta=await page.evaluate(()=>window.__hepAtlasExport.last);const notes=meta.footerLines.join('\n');for(const phrase of ['0.1 × limit','2.1816833824484827e-48','not a measurement','not a detection','2410.17036v3#page=8','155182.v2/t1','wp=40%2C0.1'])assert(notes.includes(phrase),phrase);
  if((engine==='chromium'&&!mobile)||(engine==='webkit'&&mobile)){const pending=page.waitForEvent('download');await page.locator('.export-download').focus();await page.keyboard.press('Enter');const download=await pending;const file=path.join(out,`${engine}-${size}-limit-probe-export.png`);await download.saveAs(file);const bytes=fs.readFileSync(file);assert.equal(bytes.subarray(1,4).toString(),'PNG');assert(bytes.length>15000);assert.equal(bytes.readUInt32BE(16),meta.width);assert.equal(bytes.readUInt32BE(20),meta.height)}
  await page.getByRole('button',{name:'Close export',exact:true}).click();
  await page.evaluate(async()=>{const s=await import('/atlas/js/state.js');s.navigate({entity:{type:'result',slug:'lz-ws2024-wimp-search-2024'}})});await page.waitForURL(u=>u.hash==='#/result/lz-ws2024-wimp-search-2024');assert(!new URL(page.url()).searchParams.has('wp'));
  await page.goBack();await overlay.waitFor();assert.equal(await factorValue(),'.1');
  await choice('below');await page.evaluate(async()=>{const s=await import('/atlas/js/state.js');s.navigate({theme:'standard',year:2012})});assert.equal(await feedback.getAttribute('data-outcome'),'supported');assert.equal(await factorValue(),'.1');
  if(mobile){await lab.locator('.limit-probe-controls').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,`${engine}-360-limit-probe-standard.png`)});assert(await lab.evaluate(n=>n.scrollWidth<=n.clientWidth+1))}
  await page.goto('about:blank');await page.goto(`${base}/atlas?data=generated&wp=39,10#/view/limits/wimp-si`,{waitUntil:'networkidle'});await overlay.waitFor();assert.equal(await mass.inputValue(),'40');assert.equal(await factorValue(),'10');assert.equal(new URL(page.url()).searchParams.get('wp'),'40,10');assert.match(await lab.locator('.limit-probe-notice').innerText(),/not a stored.*40 GeV/s);
  await disclosure.focus();await page.keyboard.press('Enter');await page.waitForFunction(()=>!new URL(location.href).searchParams.has('wp'));assert.equal(await overlay.count(),0);
  await trigger.focus();await page.keyboard.press('Enter');await page.waitForFunction(()=>!document.querySelector('.export-download')?.disabled);assert(!(await page.evaluate(()=>window.__hepAtlasExport.last.footerLines.join('\n'))).includes('Hypothetical:'));await page.getByRole('button',{name:'Close export',exact:true}).click();
  await context.close();console.log(`PASS ${engine} ${size}: exact LZ mass/factor interpretation, wrong/right/boundary predictions, native controls, scoped history/copied links, overlay bounds, source and PNG, ordinary export`);
 }assert.deepEqual(errors,[])}catch(e){console.error('BROWSER FAILURE',engine,size,e);console.error('BROWSER ERRORS',errors);if(active&&!active.isClosed()){try{await active.screenshot({path:path.join(out,`${engine}-${size}-limit-probe-failure.png`),timeout:5000})}catch(capture){console.error('FAILURE SCREENSHOT',capture.message)}}throw e}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
