/* Model → measured reactions → existing SNO question → primary evidence. */
const {chromium,webkit}=require('playwright');const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');const {openPrimary}=require('./browser_support/primary.cjs');
const engine=process.env.HEP_BROWSER||'chromium',base=process.env.HEP_URL||'http://127.0.0.1:8876';
const out=process.env.HEP_ATLAS_OUTPUT||path.join(__dirname,'../test-results/atlas-iterations');fs.mkdirSync(out,{recursive:true});
(async()=>{const browser=await ({chromium,webkit}[engine]).launch({headless:true});const errors=[];let active=null,size='desktop';
 try{for(const mobile of (process.env.HEP_MOBILE_ONLY?[true]:[false,true])){
  const context=await browser.newContext({viewport:mobile?{width:360,height:780}:{width:1440,height:1000},...(mobile?{isMobile:true,hasTouch:true}:{}),reducedMotion:'reduce',acceptDownloads:true});
  const page=await context.newPage();active=page;size=mobile?'360':'desktop';page.setDefaultTimeout(30000);page.on('pageerror',e=>errors.push(e.message));
  const visit=u=>page.goto(u,{waitUntil:'networkidle'});
  async function expandRecord(){
   if(!mobile)return;
   const toggle=page.locator('#detail-panel > .sheet-bar .sheet-expand');await toggle.waitFor();
   if(await toggle.getAttribute('aria-expanded')==='false')await toggle.click();
   assert.equal(await toggle.getAttribute('aria-expanded'),'true');
  }
  async function visibleInRecord(selector){
   await page.waitForFunction(selector=>{const node=document.querySelector(selector),panel=document.querySelector('#detail-panel');if(!node||!panel)return false;
    const bounds=panel.getBoundingClientRect(),bar=panel.querySelector(':scope > .sheet-bar')?.getBoundingClientRect(),box=node.getBoundingClientRect();
    return box.top>=Math.max(bounds.top,bar?.bottom||bounds.top)&&box.bottom<=bounds.bottom;
   },selector,{timeout:5000});
  }
  async function readableFlavorNames(){
   assert(await reader.locator('.evidence-flavor strong').first().evaluate(label=>{
    const text=label.firstChild,word=text.textContent.split(/\s/)[0],range=document.createRange();range.setStart(text,0);range.setEnd(text,word.length);
    return range.getClientRects().length===1;
   }),'the Electron flavor name stays on one line');
  }
  await visit(`${base}/atlas?data=generated&theme=projector&e=1.2&th=15&le=1#/view/beam-section/j-parc-neutrino`);await page.locator('#osc-angle').waitFor();
  await page.locator('.osc-flavors > summary').focus();await page.keyboard.press('Enter');
  const measured=page.locator('.osc-flavors a[data-result-evidence-link]');await measured.waitFor();
  const destination=new URL(await measured.getAttribute('href'),page.url());assert.equal(destination.hash,'#/result/sno-nc-evidence-2002');
  for(const key of ['e','th','le','step','present'])assert(!destination.searchParams.has(key),`${key} does not leak into a result link`);
  assert.equal(destination.searchParams.get('data'),'generated');assert.equal(destination.searchParams.get('theme'),'projector');
  await measured.focus();await page.keyboard.press('Enter');
  const card=page.locator('.result-evidence'),reader=card.locator('.evidence-channel-reader');await reader.waitFor();await expandRecord();
  assert.match(await card.innerText(),/standard.*⁸B|⁸B.*standard/s);assert.match(await card.innerText(),/5.3σ above zero/);
  assert.equal(await card.locator('.evidence-significance > div').count(),1,'SNO has no invented expected significance');
  const radios=reader.locator('input[type=radio]');assert.equal(await radios.count(),2);assert.equal(await reader.locator('input[value=cc]').isChecked(),true);
  const probed=()=>reader.locator('.evidence-flavor[data-probed=true]').allTextContents();assert.equal((await probed()).length,1);assert.match((await probed())[0],/Electron/);
  await radios.first().focus();await page.keyboard.press('ArrowRight');assert.equal(await reader.locator('input[value=nc]').isChecked(),true);
  assert.equal((await probed()).length,3);assert.equal(await reader.locator('input[value=nc]').evaluate(n=>n===document.activeElement),true);
  assert.match(await reader.locator('.evidence-channel-reaction').innerText(),/νx.*d.*p.*n.*νx/);
  assert.match(await reader.locator('.evidence-channel-signal').innerText(),/neutron.*capture|capture.*neutron/i);
  const fluxes=reader.locator('.evidence-channel-fluxes');assert.match(await fluxes.innerText(),/1.76.*0.06.*0.05.*0.09.*5.09.*0.44.*0.43.*0.46/s);
  assert.match(await reader.locator('tr[data-channel=nc]').innerText(),/Selected/);assert.match(await fluxes.locator('caption').innerText(),/10⁶ cm⁻² s⁻¹/);
  assert.match(await card.locator('.evidence-significance-note').innerText(),/ratio/);
  assert(await reader.evaluate(n=>n.scrollWidth<=n.clientWidth+1),'reader fits the record width');await reader.locator('.evidence-flavors').scrollIntoViewIfNeeded();await visibleInRecord('.evidence-flavors');await readableFlavorNames();
  await page.screenshot({path:path.join(out,`${engine}-${size}-sno-evidence.png`)});
  await fluxes.locator('tbody').scrollIntoViewIfNeeded();await visibleInRecord('.evidence-channel-fluxes tbody');await page.screenshot({path:path.join(out,`${engine}-${size}-sno-fluxes.png`)});
  const paper='https://arxiv.org/pdf/nucl-ex/0204008v2';
  for(const [number,label]of [[2,'reactions'],[4,'fluxes'],[5,'fit']]){
   const url=`${paper}#page=${number}`,source=card.locator(`a[href="${url}"]`).first();await source.waitFor();
   if(mobile)assert((await source.boundingBox()).height>=44,'primary-source links have phone touch targets');
   if((engine==='chromium'&&!mobile)||(engine==='webkit'&&mobile))await openPrimary(context,page,{click:async()=>{await source.focus();await page.keyboard.press('Enter')}},{url,engine,viewport:size,output:out,artifactName:`sno-${label}`,requirePDF:true});
  }
  await page.bringToFront();
  const lesson=card.locator('.evidence-next-question a[data-tour-step-link]');const lessonURL=new URL(await lesson.getAttribute('href'),page.url());
  assert.equal(lessonURL.hash,'#/tour/neutrino-oscillation-story');assert.equal(lessonURL.searchParams.get('step'),'3');await lesson.click();
  await page.waitForURL(u=>u.hash==='#/tour/neutrino-oscillation-story'&&u.searchParams.get('step')==='3');await page.locator('.tour-question').waitFor();
  await page.locator('.tour-choices input[value=equal-inferred-flux]').check();await page.getByRole('button',{name:'Show answer',exact:true}).click();assert.match(await page.locator('.tour-q-answer').innerText(),/35%.*not this division/s);
  await page.goBack();await reader.waitFor();assert.equal(await reader.locator('input[value=cc]').isChecked(),true,'fresh record visits start at the first explanatory channel');
  await page.goBack();await page.waitForFunction(()=>document.querySelector('#osc-angle')?.value==='15');assert.equal(await page.locator('#osc-energy').inputValue(),'1.2');assert.equal(await page.locator('#osc-keep-ratio').isChecked(),true);
  await visit(destination.href);await reader.waitFor();assert.match(await fluxes.innerText(),/1.76.*5.09/s);
  const generic=await page.evaluate(async()=>{const {renderEvidence}=await import('/atlas/js/result-evidence.js');return renderEvidence({experiment:'Example',measurement:'A reviewed measurement',evidence:[]}).textContent});assert.doesNotMatch(generic,/SNO|Higgs|5.3|1.76/);
  const independent=await page.evaluate(async()=>{const {renderEvidence}=await import('/atlas/js/result-evidence.js'),{evidenceFor}=await import('/atlas/js/result-evidence-data.js');const a=renderEvidence(evidenceFor('result:sno-nc-evidence-2002')),b=renderEvidence(evidenceFor('result:sno-nc-evidence-2002'));const holder=document.createElement('div');holder.hidden=true;holder.append(a,b);document.body.append(holder);a.querySelector('input[value=nc]').click();b.querySelector('input[value=cc]').click();const ok=a.querySelector('input[value=nc]').checked&&b.querySelector('input[value=cc]').checked;holder.remove();return ok});assert(independent,'reusable readers have independent native radio groups');
  const standard=new URL(destination.href);standard.searchParams.set('theme','standard');await visit(standard.href);await reader.waitFor();await expandRecord();assert(await reader.evaluate(n=>n.scrollWidth<=n.clientWidth+1));
  await reader.locator('input[value=nc]').check();await reader.locator('.evidence-flavors').scrollIntoViewIfNeeded();await visibleInRecord('.evidence-flavors');await readableFlavorNames();await page.screenshot({path:path.join(out,`${engine}-${size}-sno-evidence-standard.png`)});
  // Shared evidence source/disclosure controls also keep their native keys in an existing presenter tour.
  await visit(`${base}/atlas?data=generated&step=7&present=1#/tour/higgs-hunt`);await page.locator('#tour-card').waitFor();const openRecord=page.locator('#tour-card .tour-record-btn');if(await openRecord.isVisible())await openRecord.click();await card.waitFor();
  const definition=card.locator('details').first();await definition.locator('summary').focus();await page.keyboard.press('Enter');assert.equal(await definition.evaluate(n=>n.open),true);
  assert.equal(await page.locator('.tour-answer').evaluate(n=>n.hidden),true);assert.equal(new URL(page.url()).searchParams.get('step'),'7');
  await page.keyboard.press('b');assert.equal(await page.locator('#tour-blank').evaluate(n=>n.hidden),false);await page.keyboard.press('Enter');assert.equal(await definition.evaluate(n=>n.open),true,'first key only unblanks');
  await page.keyboard.press('Enter');assert.equal(await definition.evaluate(n=>n.open),false);assert.equal(new URL(page.url()).searchParams.get('step'),'7');
  await visit(`${base}/atlas?data=generated&embed=1&theme=projector&e=1.2&th=15#/view/beam-section/j-parc-neutrino`);await page.locator('.osc-flavors>summary').click();
  const embedded=page.locator('.osc-flavors a[data-result-evidence-link]');const embedURL=new URL(await embedded.getAttribute('href'),page.url());assert.equal(embedURL.searchParams.get('embed'),'1');assert.equal(embedURL.searchParams.get('theme'),'projector');
  await visit(`${base}/atlas?data=generated&theme=standard&e=1.2&th=15#/view/beam-section/j-parc-neutrino`);await page.locator('.osc-flavors>summary').click();
  assert.equal(new URL(await embedded.getAttribute('href'),page.url()).searchParams.get('theme'),'standard');
  await visit(embedURL.href);await reader.waitFor();assert.equal(new URL(page.url()).searchParams.get('embed'),'1');
  await context.close();console.log(`PASS ${engine} ${size}: measured reactions/fluxes, native radio/source keys, existing question, history/deep links, independent readers, themes/embed and presenter blank`);
 }assert.deepEqual(errors,[])}catch(error){if(active&&!active.isClosed()){console.error('BROWSER ERRORS',JSON.stringify(errors));console.error('FAILURE STATE',await active.evaluate(()=>({url:location.href,title:document.title,busy:document.querySelector('#detail-panel')?.getAttribute('aria-busy'),panel:document.querySelector('#detail-panel')?.innerText?.slice(0,1000),text:document.querySelector('.result-evidence')?.textContent?.slice(0,1000)})));await active.screenshot({path:path.join(out,`${engine}-${size}-sno-evidence-failure.png`)})}throw error}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
