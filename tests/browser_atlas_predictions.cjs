/* Optional predictions belong to the existing tour question and presenter. */
const {chromium,webkit}=require('playwright');const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');const {openPrimary}=require('./browser_support/primary.cjs');
const engine=process.env.HEP_BROWSER||'chromium';const base=process.env.HEP_URL||'http://127.0.0.1:8876';
const output=process.env.HEP_ATLAS_OUTPUT||path.join(__dirname,'../test-results/atlas-iterations');fs.mkdirSync(output,{recursive:true});
async function assertFeedbackVisible(page){
 await page.waitForFunction(()=>{
  const body=document.querySelector('#tour-body').getBoundingClientRect();
  return ['.tour-answer-btn','.tour-prediction-feedback'].every(selector=>{const box=document.querySelector(selector).getBoundingClientRect();return box.height>0&&box.top>=body.top&&box.bottom<=body.bottom});
 },null,{timeout:5000});
 const body=await page.locator('#tour-body').boundingBox();
 for(const selector of ['.tour-answer-btn','.tour-prediction-feedback']){
  const box=await page.locator(selector).boundingBox();
  assert(box&&box.height>0&&box.y>=body.y&&box.y+box.height<=body.y+body.height,`phone ${selector} remains fully visible in the tour body`);
 }
}
(async()=>{const browser=await ({chromium,webkit}[engine]).launch({headless:true});const errors=[];
 try{for(const mobile of [false,true]){
  const context=await browser.newContext({viewport:mobile?{width:360,height:780}:{width:1440,height:1000},
   ...(mobile?{isMobile:true,hasTouch:true}:{}),reducedMotion:'reduce'});
  const page=await context.newPage();page.setDefaultTimeout(30000);page.on('pageerror',e=>errors.push(e.message));
  const address=`${base}/atlas?data=generated&step=6&present=1&theme=projector#/tour/higgs-hunt`;
  await page.goto(address,{waitUntil:'networkidle'});
  const radios=page.locator('.tour-choices input[type=radio]');await radios.first().waitFor();assert.equal(await radios.count(),3);
  const reveal=page.locator('.tour-answer-btn');
  assert.equal(await page.locator('.tour-choices input:checked').count(),0);assert.equal(await reveal.getAttribute('aria-disabled'),'true');
  await reveal.focus();await page.keyboard.press('Enter');
  assert.equal(await page.locator('.tour-answer').isVisible(),false,'an unanswered prediction must not reveal the explanation');
  assert.match(await page.locator('.tour-choice-instruction').innerText(),/Choose/);
  assert.equal(await radios.first().evaluate(n=>n===document.activeElement),true,'an unanswered reveal focuses the choices');
  await page.keyboard.press('ArrowRight');assert.equal(await page.locator('input[value="model-probability"]').isChecked(),true);
  assert.equal(new URL(page.url()).searchParams.get('step'),'6','native radio arrows must not advance the presenter');
  // The installed macOS WebKit uses Option-Tab to include native buttons; bare-control probes verify the same preference.
  await page.keyboard.press(engine==='webkit'?'Alt+Tab':'Tab');assert.equal(await reveal.evaluate(n=>n===document.activeElement),true,'native Tab/Option-Tab reaches the reveal from the radio group');
  await page.keyboard.press('Enter');await page.locator('.tour-answer').waitFor();
  assert.match(await page.locator('.tour-prediction-feedback').innerText(),/does not match|Revisit/);
  assert.equal(await page.locator('input[value="model-probability"]').isChecked(),true,'feedback retains the learner’s prediction');
  assert.match(await page.locator('.tour-q-answer').innerText(),/at least.*background-only|background-only.*at least/s);
  assert.match(await page.locator('.tour-q-answer').innerText(),/on average/);
  assert.match(await page.locator('.tour-q-answer').innerText(),/590 million/);
  assert.match(await page.locator('input[value="local-background"]').locator('..').innerText(),/Supported/);
  assert.equal(await reveal.evaluate(n=>n===document.activeElement),true);
  if(mobile){
   await assertFeedbackVisible(page);
   await page.screenshot({path:path.join(output,`${engine}-360-higgs-prediction-incorrect.png`)});
   const expanded=await page.locator('#tour-card').boundingBox();
   await page.locator('.tour-collapse').click();assert.equal(await page.locator('#tour-body').isVisible(),false);
   assert((await page.locator('#tour-card').boundingBox()).height<expanded.height,'Hide text restores space for the visual');
   await page.locator('.tour-collapse').click();await assertFeedbackVisible(page);
  }
  await page.locator('input[value="local-background"]').check();assert.equal(await page.locator('.tour-answer').isVisible(),false,'changing prediction clears stale feedback');
  await reveal.focus();await page.keyboard.press('Space');assert.equal(await page.locator('.tour-answer').isVisible(),true);
  assert.match(await page.locator('.tour-prediction-feedback').innerText(),/matches/);
  if(mobile)await assertFeedbackVisible(page);
  await page.setViewportSize(mobile?{width:1024,height:900}:{width:360,height:780});
  assert.equal(await page.locator('input[value="local-background"]').isChecked(),true,'responsive changes retain the selected prediction');
  assert.equal(await page.locator('.tour-answer').isVisible(),true);assert.match(await page.locator('.tour-prediction-feedback').innerText(),/matches/);
  if(!mobile)await assertFeedbackVisible(page);
  await page.setViewportSize(mobile?{width:360,height:780}:{width:1440,height:1000});
  if(mobile)await assertFeedbackVisible(page);
  await reveal.focus();await page.keyboard.press('Enter');assert.equal(await page.locator('.tour-answer').isVisible(),false,'native Enter hides an open answer in presenter mode');
  assert.equal(new URL(page.url()).searchParams.get('step'),'6');
  await page.keyboard.press('Space');assert.equal(await page.locator('.tour-answer').isVisible(),true,'native Space reveals without advancing');
  const evidence=page.locator('.tour-answer details').filter({has:page.locator('summary',{hasText:'Sources for the question and answer'})}).first();
  await evidence.locator('summary').focus();await page.keyboard.press('Enter');
  assert.equal(await evidence.evaluate(n=>n.open),true,'source disclosure keeps its native presenter key');
  const url='https://arxiv.org/pdf/1207.7214v1';const source=evidence.locator(`a[href="${url}"]`).first();await source.waitFor();
  if((engine==='chromium'&&!mobile)||(engine==='webkit'&&mobile))await openPrimary(context,page,
   {click:async()=>{await source.focus();await page.keyboard.press('Enter')}},
   {url,engine,viewport:mobile?'360':'desktop',output,artifactName:'prediction-definition',requirePDF:true});
  await page.bringToFront();
  assert.match(await evidence.innerText(),/PDF page 17/);
  await page.locator('#tour-card').focus();await page.keyboard.press('b');assert.equal(await page.locator('#tour-blank').evaluate(n=>n.hidden),false);
  const chosen=await page.locator('.tour-choices input:checked').inputValue();await radios.last().focus();await page.keyboard.press('Space');
  assert.equal(await page.locator('#tour-blank').evaluate(n=>n.hidden),true);
  assert.equal(await page.locator('.tour-choices input:checked').inputValue(),chosen,'unblanking consumes the key before changing a prediction');
  await page.locator('.tour-next').click();await page.waitForURL(u=>u.searchParams.get('step')==='7');
  assert.equal(await page.locator('.tour-choices').count(),0,'the existing mass question keeps its original reveal');
  await reveal.focus();await page.keyboard.press('Space');assert.equal(await page.locator('.tour-answer').isVisible(),true);
  assert.match(await page.locator('.tour-q-answer').innerText(),/0\.82/);
  await page.locator('.tour-back').click();await page.waitForURL(u=>u.searchParams.get('step')==='6');
  assert.equal(await page.locator('.tour-choices input:checked').count(),0,'returning to a step starts a new prediction');
  assert.equal(await page.locator('.tour-answer').isVisible(),false);
  await page.goto(address,{waitUntil:'networkidle'});await radios.first().waitFor();
  assert.equal(await page.locator('.tour-choices input:checked').count(),0,'copied links do not publish a learner’s answer');
  assert(!page.url().includes('model-probability'));assert(!page.url().includes('local-background'));
  await page.locator('#tour-card').focus();await page.keyboard.press('a');
  assert.equal(await page.locator('.tour-answer').isVisible(),false,'presenter reveal also requires a prediction');
  assert.equal(await radios.first().evaluate(n=>n===document.activeElement),true);
  const beforePrediction=page.url();await radios.first().check();await reveal.click();
  assert.equal(page.url(),beforePrediction,'a prediction and its feedback do not enter the address');
  assert(await page.locator('.tour-question').evaluate(n=>n.scrollWidth<=n.clientWidth+1));
  await page.screenshot({path:path.join(output,`${engine}-${mobile?'360':'desktop'}-higgs-prediction.png`)});
  await page.keyboard.press('Escape');await page.waitForURL(u=>!u.searchParams.has('present'));
  await page.keyboard.press('Escape');await page.waitForURL(u=>u.hash!=='#/tour/higgs-hunt');
  await page.goto(address,{waitUntil:'networkidle'});await radios.first().waitFor();
  assert.equal(await page.locator('.tour-choices input:checked').count(),0,'closing and reopening starts a fresh prediction');
  if(mobile){
   await page.goto(address.replace('&theme=projector',''),{waitUntil:'networkidle'});await radios.first().waitFor();
   await page.locator('input[value="model-probability"]').check();await reveal.click();await assertFeedbackVisible(page);
   await page.screenshot({path:path.join(output,`${engine}-360-higgs-prediction-standard.png`)});
  }
  await context.close();console.log(`PASS ${engine} ${mobile?'360px mobile':'desktop'}: unselected guard, native radios, feedback/reset, presenter keys, source, legacy reveal and deep link`);
 }assert.deepEqual(errors,[])}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
