/* Historical energy frontier → ideal proton collision energies → primary/export. */
const {chromium,webkit}=require('playwright');const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');const {openPrimary}=require('./browser_support/primary.cjs');
const engine=process.env.HEP_BROWSER||'chromium',base=process.env.HEP_URL||'http://127.0.0.1:8876';
const out=process.env.HEP_ATLAS_OUTPUT||path.join(__dirname,'../test-results/atlas-iterations/cycle16');fs.mkdirSync(out,{recursive:true});
(async()=>{const browser=await ({chromium,webkit}[engine]).launch({headless:true});const errors=[];let active,size;
 try{for(const mobile of(process.env.HEP_MOBILE_ONLY?[true]:[false,true])){
  const context=await browser.newContext({viewport:mobile?{width:360,height:780}:{width:1440,height:1000},...(mobile?{isMobile:true,hasTouch:true}:{}),reducedMotion:'reduce',acceptDownloads:true});
  const page=await context.newPage();active=page;size=mobile?'360':'desktop';page.setDefaultTimeout(30000);page.on('pageerror',e=>errors.push(e.message));
  const visit=u=>page.goto(u,{waitUntil:'networkidle'});
  await visit(`${base}/atlas?data=generated&theme=projector&y=2012&ce=450#/view/energy-frontier`);await page.locator('#ef-chart svg.ch-svg').waitFor();
  const lab=page.locator('.collision-lab');assert.equal(await lab.count(),1,'the energy frontier needs the interactive collision comparison');
  const input=page.locator('#collision-energy'),plot=lab.locator('.collision-plot'),answer=page.locator('#collision-answer'),test=page.locator('#collision-test');
  const machineIds=()=>page.locator('#ef-chart .ch-point').evaluateAll(nodes=>nodes.map(n=>n.dataset.id));const original=await machineIds();assert(original.length>20);
  const value=async id=>Number((await page.locator(id).innerText()).replaceAll(',','').replace('GeV','').trim());
  async function check(energy){assert.equal(await input.inputValue(),String(energy));assert.equal(new URL(page.url()).searchParams.get('ce'),String(energy));assert(Math.abs(await value('#collision-fixed')-Math.sqrt(2*.938272*(.938272+energy)))<.1);assert.equal(await value('#collision-head-on'),Number((2*energy).toPrecision(4)))}
  async function set(energy){await input.fill(String(energy));await input.press('Tab');await check(energy)}
  await check(450);assert.match(await lab.innerText(),/total.*energy|energy.*total/i);assert.match(await lab.innerText(),/two accelerated beams/);
  await lab.locator('.collision-prediction>summary').focus();await page.keyboard.press('Enter');await test.focus();await page.keyboard.press('Space');await answer.waitFor();await check(1800);assert.match(await answer.innerText(),/450.*1800.*4.00/s);
  await set(1);assert.equal(await answer.isVisible(),false,'input changes clear stale feedback');await test.click();await check(4);assert.match(await answer.innerText(),/1.60/);
  await set(2500.1);assert.equal(await test.isDisabled(),true);assert.match(await page.locator('#collision-test-limit').innerText(),/2,500|2500/);assert.match(await page.locator('#collision-test-limit').innerText(),/10,000\.4/,'the refused ×4 input must retain the control precision');
  const accepted=page.url();await input.fill('0');await input.press('Tab');await page.locator('#collision-input-error').waitFor();assert.equal(page.url(),accepted,'invalid live input cannot silently clip/change accepted state');
  assert.equal(await input.getAttribute('aria-invalid'),'true');await page.locator('#collision-reset').click();await check(450);assert.equal(await page.locator('#collision-input-error').isVisible(),false);
  await input.focus();await page.keyboard.press('ArrowUp');await input.press('Tab');await check(450.1);await set(450);
  assert.deepEqual(await machineIds(),original,'model inputs do not change the recorded machine points');
  await plot.scrollIntoViewIfNeeded();assert(await lab.evaluate(n=>n.scrollWidth<=n.clientWidth+1));
  assert(await plot.locator('svg text').evaluateAll(nodes=>nodes.every(n=>parseFloat(getComputedStyle(n).fontSize)>=14)),'phone plot type stays readable');
  await page.screenshot({path:path.join(out,`${engine}-${size}-collision-model.png`)});
  await page.locator('#collision-method>summary').focus();await page.keyboard.press('Enter');const method=page.locator('#collision-method');
  for(const phrase of ['49.2','49.3','0.938272','kinetic','quark','cross section'])assert((await method.innerText()).includes(phrase),phrase);
  for(const [slug,label]of [['kinematics','kinematics'],['phys-constants','constants']]){const url=`https://pdg.lbl.gov/2024/reviews/rpp2024-rev-${slug}.pdf#page=1`;const source=method.locator(`a[href="${url}"]`);await source.waitFor();
   if((engine==='chromium'&&!mobile)||(engine==='webkit'&&mobile))await openPrimary(context,page,{click:async()=>{await source.focus();await page.keyboard.press('Enter')}},{url,engine,viewport:size,output:out,artifactName:`collision-${label}`,requirePDF:true});
  }
  await page.bringToFront();await input.focus();await input.evaluate(n=>window.__collisionInput=n);await page.evaluate(async()=>{const s=await import('/atlas/js/state.js');s.navigate({collisionEnergy:100})});await check(100);
  await page.goBack();await check(450);assert.equal(await input.evaluate(n=>n===window.__collisionInput),true,'same-view history retains the native control');assert.equal(await input.evaluate(n=>n===document.activeElement),true);
  const destination=page.url();await visit(destination);await input.waitFor();await check(450);assert.equal(await answer.isVisible(),false);
  const point=page.locator('#ef-chart .ch-point').first();await point.focus();await page.keyboard.press('Enter');await page.waitForURL(u=>u.hash.startsWith('#/accelerator/'));assert(!new URL(page.url()).searchParams.has('ce'));
  await page.goBack();await input.waitFor();await check(450);
  const trigger=page.locator(mobile?'#phone-export-btn':'#export-btn');await trigger.focus();await page.keyboard.press('Enter');await page.locator('#export-popover').waitFor();
  assert.equal(await page.locator('#export-figure').inputValue(),'history');await page.locator('#export-figure').selectOption('collision');
  await page.waitForFunction(()=>!document.querySelector('.export-download')?.disabled&&window.__hepAtlasExport?.last?.title==='Proton collision-energy model');
  const meta=await page.evaluate(()=>window.__hepAtlasExport.last);const notes=meta.footerLines.join('\n');for(const text of ['E = 450 GeV','0.938272','49.2','two accelerated beams','ce=450'])assert(notes.includes(text),text);
  if((engine==='chromium'&&!mobile)||(engine==='webkit'&&mobile)){const pending=page.waitForEvent('download');await page.locator('.export-download').focus();await page.keyboard.press('Enter');const d=await pending;const file=path.join(out,`${engine}-${size}-collision-export.png`);await d.saveAs(file);const bytes=fs.readFileSync(file);assert.equal(bytes.subarray(1,4).toString(),'PNG');assert(bytes.length>15000);assert.equal(bytes.readUInt32BE(16),meta.width);assert.equal(bytes.readUInt32BE(20),meta.height)}
  assert.equal(await page.locator('.collision-export-stage').count(),0,'temporary model SVGs are released');
  await page.locator('#export-figure').selectOption('history');await page.waitForFunction(()=>!document.querySelector('.export-download')?.disabled&&window.__hepAtlasExport?.last?.title!=='Proton collision-energy model');
  await page.getByRole('button',{name:'Close export',exact:true}).click();
  if(mobile){await visit(destination.replace('theme=projector','theme=standard'));await input.waitFor();await plot.scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,`${engine}-360-collision-standard.png`)});assert(await lab.evaluate(n=>n.scrollWidth<=n.clientWidth+1))}
  await visit(`${base}/atlas?data=generated&embed=1&theme=projector&ce=1000#/view/energy-frontier`);await input.waitFor();await check(1000);assert.equal(new URL(page.url()).searchParams.get('embed'),'1');
  await visit(`${base}/atlas?data=generated&ce=1200#/view/energy-frontier/`);await input.waitFor();await check(1200);
  await set(800);assert.equal(new URL(page.url()).hash,'#/view/energy-frontier');const canonical=page.url();await visit(canonical);await input.waitFor();await check(800);
  await context.close();console.log(`PASS ${engine} ${size}: exact collision comparison, native inputs, low/high-energy prediction, domain errors, stable chart, scoped history/deep links, sources and existing export choices`);
 }assert.deepEqual(errors,[])}catch(error){if(active&&!active.isClosed()){console.error('BROWSER ERRORS',JSON.stringify(errors));console.error(await active.evaluate(()=>({url:location.href,input:document.querySelector('#collision-energy')?.value,answer:document.querySelector('#collision-answer')?.textContent,error:document.querySelector('#collision-input-error')?.textContent})));await active.screenshot({path:path.join(out,`${engine}-${size}-collision-failure.png`)})}throw error}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
