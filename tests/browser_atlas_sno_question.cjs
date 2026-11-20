/* Existing lab -> existing SNO tour question -> versioned primary flux passage. */
const {chromium,webkit}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {openPrimary}=require('./browser_support/primary.cjs');
const engine=process.env.HEP_BROWSER||'chromium';
const base=process.env.HEP_URL||'http://127.0.0.1:8876';
const output=process.env.HEP_ATLAS_OUTPUT||path.join(__dirname,'../test-results/atlas-iterations');
const paper='https://arxiv.org/pdf/nucl-ex/0204008v2#page=4';
fs.mkdirSync(output,{recursive:true});
(async()=>{
 const browser=await ({chromium,webkit}[engine]).launch({headless:true});const errors=[];
 try{for(const mobile of (process.env.HEP_MOBILE_ONLY?[true]:[false,true])){
  const context=await browser.newContext({viewport:mobile?{width:360,height:780}:{width:1440,height:1000},
   ...(mobile?{isMobile:true,hasTouch:true}:{}),reducedMotion:'reduce'});
  const page=await context.newPage();page.setDefaultTimeout(30000);page.on('pageerror',e=>errors.push(e.message));
  await page.goto(`${base}/atlas?data=generated&theme=projector&e=1.2&le=1#/view/beam-section/j-parc-neutrino`,{waitUntil:'networkidle'});
  async function feedbackVisible(){
   await page.waitForFunction(()=>{const frame=document.querySelector('#tour-body').getBoundingClientRect();return ['.tour-answer-btn','.tour-prediction-feedback'].every(selector=>{const r=document.querySelector(selector).getBoundingClientRect();return r.height>0&&r.top>=frame.top&&r.bottom<=frame.bottom})},null,{timeout:5000});
  }
  const summary=page.locator('.osc-flavors > summary');await summary.focus();await page.keyboard.press('Enter');
  const next=page.locator('.osc-flavors a[data-tour-step-link]');await next.waitFor();
  assert.match(await page.locator('.osc-flavor-evidence').innerText(),/solar.*not a fit|not.*solar/s);
  const href=await next.getAttribute('href');const target=new URL(href,page.url());
  assert.equal(target.hash,'#/tour/neutrino-oscillation-story');assert.equal(target.searchParams.get('step'),'3');
  assert.equal(target.searchParams.get('theme'),'projector');assert.equal(target.searchParams.get('data'),'generated');
  assert.equal(target.searchParams.has('e'),false);assert.equal(target.searchParams.has('le'),false);
  await next.focus();await page.keyboard.press('Enter');
  await page.waitForURL(url=>url.hash==='#/tour/neutrino-oscillation-story'&&url.searchParams.get('step')==='3');
  await page.locator('.tour-question').waitFor();assert.equal(await page.locator('.tour-answer').isVisible(),false);
  assert.match(await page.locator('.tour-q-prompt').innerText(),/CC = 1.76.*NC = 5.09/s);
  const radios=page.locator('.tour-choices input[type=radio]');assert.equal(await radios.count(),3,'the SNO checkpoint needs three predictions');
  const reveal=page.locator('.tour-answer-btn');assert.equal(await page.locator('.tour-choices input:checked').count(),0);
  const beforePrediction=page.url();await reveal.focus();await page.keyboard.press('Enter');
  assert.equal(await page.locator('.tour-answer').isVisible(),false,'an unanswered reveal must withhold the working');
  assert.match(await page.locator('.tour-choice-instruction').innerText(),/Choose/);assert.equal(await radios.first().evaluate(n=>n===document.activeElement),true);
  await page.keyboard.press('ArrowRight');assert.equal(await page.locator('input[value=nc-must-be-larger]').isChecked(),true);
  await page.keyboard.press(engine==='webkit'?'Alt+Tab':'Tab');assert.equal(await reveal.evaluate(n=>n===document.activeElement),true);
  await page.keyboard.press('Enter');await page.locator('.tour-answer').waitFor();
  assert.match(await page.locator('.tour-prediction-feedback').innerText(),/does not match|Revisit/);
  assert.equal(await page.locator('input[value=nc-must-be-larger]').isChecked(),true,'feedback retains the learner’s prediction');
  assert.match(await page.locator('input[value=equal-inferred-flux]').locator('..').innerText(),/Supported/);
  await page.screenshot({path:path.join(output,`${engine}-${mobile?'360':'desktop'}-sno-prediction-incorrect.png`)});
  if(mobile)await feedbackVisible();
  await page.locator('input[value=equal-inferred-flux]').check();assert.equal(await page.locator('.tour-answer').isVisible(),false,'a new prediction clears stale feedback');
  assert.equal(await page.locator('.tour-prediction-feedback').textContent(),'');
  await reveal.focus();await page.keyboard.press('Space');await page.locator('.tour-answer').waitFor();
  assert.match(await page.locator('.tour-prediction-feedback').innerText(),/matches/);if(mobile)await feedbackVisible();
  assert.equal(page.url(),beforePrediction,'predictions and feedback do not enter the URL');
  const answer=await page.locator('.tour-q-answer').innerText();
  for(const text of ['35%','raw event counts','no propagated uncertainty','single-energy','5.3σ','not this division'])assert(answer.includes(text),text);
  const working=page.getByText('How it was worked out',{exact:true});await working.focus();await page.keyboard.press('Enter');
  assert.match(await page.locator('.tour-working').innerText(),/CC.*1.76.*NC.*5.09.*ratio.*0.35.*percent.*35/s);
  const sources=page.locator('.tour-answer .tour-sources > summary');await sources.focus();await page.keyboard.press('Enter');
  await page.waitForFunction(()=>document.querySelector('.tour-answer .tour-sources')?.dataset.state==='loaded');
  const primary=page.locator(`.tour-answer a[href='${paper}']`).first();await primary.waitFor();
  assert.match(await page.locator('.tour-answer .tour-sources').innerText(),/PDF page 4/);
  await openPrimary(context,page,primary,{url:paper,engine,viewport:mobile?'360':'desktop',output,artifactName:'sno-question-flux',requirePDF:true});
  await page.bringToFront();
  assert(await page.locator('.tour-question').evaluate(n=>n.scrollWidth<=n.clientWidth+1));
  await page.screenshot({path:path.join(output,`${engine}-${mobile?'360':'desktop'}-sno-question.png`)});
  await page.goBack();await page.waitForFunction(()=>document.querySelector('#osc-energy')?.value==='1.2');
  assert.equal(new URL(page.url()).searchParams.get('le'),'1','Back restores the lab comparison preference');
  // A copied/native destination must open the same question, without an in-page click handler.
  await page.goto(target.href,{waitUntil:'networkidle'});await page.locator('.tour-question').waitFor();
  assert.match(await page.locator('.tour-q-prompt').innerText(),/CC = 1.76.*NC = 5.09/s);
  assert.equal(await page.locator('.tour-answer').isVisible(),false);assert.equal(await page.locator('.tour-choices input:checked').count(),0,'copied question links start fresh');
  // Embed and theme context are carried by the same real link.
  await page.goto(`${base}/atlas?data=generated&embed=1&theme=projector&e=1.2#/view/beam-section/j-parc-neutrino`,{waitUntil:'networkidle'});
  await page.locator('.osc-flavors > summary').click();
  const embedded=new URL(await page.locator('.osc-flavors a[data-tour-step-link]').getAttribute('href'),page.url());
  assert.equal(embedded.searchParams.get('embed'),'1');assert.equal(embedded.searchParams.get('theme'),'projector');
  await page.goto(embedded.href,{waitUntil:'networkidle'});await page.locator('.tour-question').waitFor();
  assert.equal(new URL(page.url()).searchParams.get('embed'),'1');
  assert.equal(await page.locator('.tour-answer').isVisible(),false);
  // Presenter Enter used to reveal the old beam answer instead of following the link.
  await page.goto(`${base}/atlas?step=5&e=1.2&present=1#/tour/neutrino-beams-through-the-earth`,{waitUntil:'networkidle'});
  await page.locator('.osc-flavors > summary').click();
  const presenterLink=page.locator('.osc-flavors a[data-tour-step-link]');
  for(const key of ['b','w']) {
   await presenterLink.focus();await page.keyboard.press(key);await page.locator('#tour-blank').waitFor();
   await page.keyboard.press('Enter');await page.locator('#tour-blank').waitFor({state:'hidden',timeout:5000});
   assert.equal(new URL(page.url()).hash,'#/tour/neutrino-beams-through-the-earth','Enter first dismisses blanking');
  }
  await presenterLink.focus();await page.keyboard.press('Enter');
  await page.waitForURL(url=>url.hash==='#/tour/neutrino-oscillation-story'&&url.searchParams.get('step')==='3');
  await page.locator('.tour-question').waitFor();assert.equal(new URL(page.url()).searchParams.get('present'),'1');
  assert.equal(await page.locator('.tour-answer').isVisible(),false);
  await page.locator('#tour-card').focus();await page.keyboard.press('a');assert.equal(await page.locator('.tour-answer').isVisible(),false,'presenter reveal also requires a prediction');
  await page.locator('input[value=equal-raw-counts]').focus();await page.keyboard.press('Space');
  await page.locator('#tour-card').focus();await page.keyboard.press('b');await page.locator('#tour-blank').waitFor();
  await radios.first().focus();await page.keyboard.press('Space');await page.locator('#tour-blank').waitFor({state:'hidden'});
  assert.equal(await page.locator('input[value=equal-raw-counts]').isChecked(),true,'the first blank-dismissal key must not change a prediction');
  await page.locator('input[value=equal-inferred-flux]').check();await reveal.focus();await page.keyboard.press('Space');
  assert.match(await page.locator('.tour-prediction-feedback').innerText(),/matches/);assert.equal(new URL(page.url()).searchParams.get('step'),'3');
  await page.keyboard.press('Enter');assert.equal(await page.locator('.tour-answer').isVisible(),false,'native Enter hides the open answer');
  await page.locator('.tour-next').click();await page.waitForURL(u=>u.searchParams.get('step')==='4');await page.locator('.tour-back').click();await page.waitForURL(u=>u.searchParams.get('step')==='3');
  assert.equal(await page.locator('.tour-choices input:checked').count(),0,'returning to the step starts a fresh prediction');
  if(mobile){
   const standard=new URL(target.href);standard.searchParams.set('theme','standard');await page.goto(standard.href,{waitUntil:'networkidle'});await radios.first().waitFor();
   await page.locator('input[value=equal-raw-counts]').check();await reveal.click();await feedbackVisible();
   await page.screenshot({path:path.join(output,`${engine}-360-sno-prediction-standard.png`)});
  }
  // This is a completed reading journey; rapid unfinished exits have a separate lifecycle regression.
  await page.waitForLoadState('networkidle');
  await context.close();console.log(`PASS ${engine} ${mobile?'360px mobile':'desktop'}: lab -> committed SNO prediction/feedback/working -> primary PDF, keyboard/presenter, fresh links and Back`);
 }assert.deepEqual(errors,[])}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
