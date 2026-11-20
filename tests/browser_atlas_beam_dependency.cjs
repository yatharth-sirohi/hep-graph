/* Source-context panel -> existing Fermilab player -> predict/trace -> primary papers. */
const {chromium,webkit}=require('playwright');const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');const {openPrimary}=require('./browser_support/primary.cjs');
const engine=process.env.HEP_BROWSER||'chromium';const base=process.env.HEP_URL||'http://127.0.0.1:8876';
const output=process.env.HEP_ATLAS_OUTPUT||path.join(__dirname,'../test-results/atlas-iterations');fs.mkdirSync(output,{recursive:true});
(async()=>{const browser=await ({chromium,webkit}[engine]).launch({headless:true});const errors=[];
 try{for(const mobile of [false,true]){
  const context=await browser.newContext({viewport:mobile?{width:360,height:780}:{width:1440,height:1000},
   ...(mobile?{isMobile:true,hasTouch:true}:{}),reducedMotion:'reduce'});
  const page=await context.newPage();page.setDefaultTimeout(30000);page.on('pageerror',e=>errors.push(e.message));
  await page.goto(`${base}/atlas?data=generated&y=2026&r=2025-2026&lv=old-map-level&sel=old-map-feature&theme=projector#/experiment/nova`,{waitUntil:'networkidle'});
  const lesson=page.locator('.status-follow-up a[data-map-step-link]');await lesson.waitFor();
  if(!mobile){await page.locator('#theme-btn').click();await page.waitForURL(u=>u.searchParams.get('theme')==='standard')}
  const href=await lesson.getAttribute('href');const native=new URL(href,page.url());
  assert.equal(native.hash,'#/map/fermilab');assert.equal(native.searchParams.get('y'),'2016');assert.equal(native.searchParams.get('proton'),'7');
  assert.equal(native.searchParams.get('data'),'generated');assert.equal(native.searchParams.get('theme'),mobile?'projector':'standard');
  await lesson.focus();await page.keyboard.press('Enter');await page.locator('#pr-card:not(.hidden)').waitFor();
  await page.locator('#pr-beam-question[open]').waitFor();assert.match(await page.locator('#pr-stage-name').innerText(),/Main Injector/);
  assert.deepEqual(await page.evaluate(async()=>{const s=(await import('/atlas/js/state.js')).get();return [s.range,s.levels,s.sel]}),[null,null,null]);
  const test=page.locator('.pr-predict-test');assert.equal(await test.isDisabled(),true);
  const summary=page.locator('#pr-beam-question > summary');await summary.click();
  await page.locator('#pr-card .pr-play').click();await summary.focus();await page.keyboard.press('Enter');
  assert.equal(await page.locator('#pr-beam-question').evaluate(n=>n.open),true);
  assert.equal((await page.locator('#pr-card .pr-play').innerText()).trim(),'Play','opening the prediction pauses autoplay before an answer is selected');
  await page.locator('#pr-card .pr-play').click();
  const numi=page.locator('input[name="pr-beam-prediction"][value="beamline:numi"]');await numi.focus();await page.keyboard.press('ArrowRight');
  assert.equal(await page.locator('input[name="pr-beam-prediction"][value="beamline:bnb"]').isChecked(),true);
  assert.equal(new URL(page.url()).searchParams.get('proton'),'7','native radio arrows must not step the map player');
  assert.equal((await page.locator('#pr-card .pr-play').innerText()).trim(),'Play','prediction interaction pauses autoplay');
  await test.focus();await page.keyboard.press('Enter');
  await page.waitForURL(u=>u.searchParams.get('proton')==='8');await page.locator('#pr-beam-answer').waitFor();
  assert.match(await page.locator('#pr-beam-feedback').innerText(),/NuMI/);
  const feedbackBox=await page.locator('#pr-beam-feedback').boundingBox();const cardBox=await page.locator('#pr-card').boundingBox();
  assert(feedbackBox.y>=cardBox.y&&feedbackBox.y+feedbackBox.height<=cardBox.y+cardBox.height,'prediction feedback is readable within the player scroll area');
  assert.match(await page.locator('#pr-beam-answer').innerText(),/necessary connection/);
  assert.match(await page.locator('#pr-beam-answer').innerText(),/not.*(?:delivery|operation)/s);
  assert.equal(await test.evaluate(n=>n===document.activeElement),true,'map tracing keeps the checkpoint button focused');
  const bnb=page.locator('[data-trace-beam="beamline:bnb"]');await bnb.focus();await page.keyboard.press('Space');
  await page.waitForURL(u=>u.searchParams.get('proton')==='10');assert.match(await page.locator('#pr-stage-name').innerText(),/Booster.*BNB/s);
  assert.equal(await page.locator('#pr-beam-answer').isVisible(),true,'answer survives native trace steps');
  assert(await page.locator('.leaflet-proton-pane .pr-current.pr-from').count()>0);
  assert(await page.locator('.leaflet-proton-pane .pr-current.pr-to').count()>0);
  await page.locator('[data-trace-beam="beamline:numi"]').click();await page.waitForURL(u=>u.searchParams.get('proton')==='8');
  assert.match(await page.locator('#pr-stage-name').innerText(),/Main Injector|MI/);
  assert(await page.locator('#pr-beam-question').evaluate(n=>n.scrollWidth<=n.clientWidth+1));
  const sources=page.locator('#pr-beam-answer a[data-branch-source]');assert.equal(await sources.count(),2);
  const urls=['https://arxiv.org/pdf/1507.06690v2#page=6','https://arxiv.org/pdf/0806.1449v2#page=2'];
  for(let i=0;i<2;i++){
   assert.equal(await sources.nth(i).getAttribute('href'),urls[i]);
   if((engine==='chromium'&&!mobile)||(engine==='webkit'&&mobile))await openPrimary(context,page,sources.nth(i),
    {url:urls[i],engine,viewport:mobile?'360':'desktop',output,artifactName:`dependency-paper-${i+1}`,requirePDF:true});
  }
  await page.bringToFront();await page.locator('#pr-beam-feedback').scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(output,`${engine}-${mobile?'360':'desktop'}-beam-dependency.png`)});
  await numi.check();assert.equal(await page.locator('#pr-beam-answer').isVisible(),false,'a changed prediction clears stale feedback');
  await test.click();assert.match(await page.locator('#pr-beam-feedback').innerText(),/matches/);
  // A different historical year must reset the exercise, not retain a prior guess.
  await page.locator('#timeline-year').focus();await page.locator('#timeline-year').press('ArrowRight');
  await page.waitForURL(u=>u.searchParams.get('y')==='2017');
  await page.locator('#pr-beam-question > summary').click();assert.equal(await page.locator('#pr-beam-answer').isVisible(),false);
  assert.equal(await page.locator('input[name="pr-beam-prediction"]:checked').count(),0);
  assert.equal(await page.locator('.pr-predict-test').isDisabled(),true);
  await page.locator('#pr-beam-question > summary').focus();await page.keyboard.press('Escape');
  await page.locator('#pr-card.hidden').waitFor({state:'attached'});
  assert.equal(await page.locator('#pr-beam-question').count(),0,'closing the player clears the checkpoint');
  // Back from the original map entry restores the source record and its 2026 context.
  await page.goto(native.href,{waitUntil:'networkidle'});await page.locator('#pr-beam-question[open]').waitFor();
  assert.equal(await page.locator('#pr-beam-answer').isVisible(),false,'copied deep link starts a fresh prediction');
  await page.goto(`${base}/atlas?data=generated&y=2026&embed=1&theme=projector#/experiment/nova`,{waitUntil:'networkidle'});
  const embedded=new URL(await page.locator('.status-follow-up a[data-map-step-link]').getAttribute('href'),page.url());
  assert.equal(embedded.searchParams.get('embed'),'1');assert.equal(embedded.searchParams.get('theme'),'projector');
  await page.locator('.status-follow-up a[data-map-step-link]').click();await page.locator('#pr-beam-question[open]').waitFor();
  await page.goBack();await page.locator('.status-follow-up').waitFor();assert.equal(new URL(page.url()).searchParams.get('y'),'2026');
  await page.goto(`${base}/atlas?data=generated&y=1960&proton=1#/map/fermilab`,{waitUntil:'networkidle'});
  await page.locator('#pr-card:not(.hidden)').waitFor();assert.equal(await page.locator('#pr-beam-question').count(),0);
  await context.close();console.log(`PASS ${engine} ${mobile?'360px mobile':'desktop'}: native lesson link, radio keys, prediction/trace, source paths, reset, native link and Back`);
 }assert.deepEqual(errors,[])}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
