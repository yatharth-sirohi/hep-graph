/* Focused learner experiments. Uses real generated data and native controls.
   HEP_BROWSER=chromium|webkit HEP_URL=http://127.0.0.1:8876 node tests/browser_atlas_experiments.cjs */
const {chromium,webkit}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const engine=process.env.HEP_BROWSER||'chromium';
const base=process.env.HEP_URL||'http://127.0.0.1:8876';
const out=process.env.HEP_ATLAS_OUTPUT||path.join(__dirname,'../test-results/atlas-iterations');
fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await ({chromium,webkit}[engine]).launch({headless:true});
 const errors=[];
 try {
  for(const mobile of [false,true]) {
   const context=await browser.newContext({viewport:mobile?{width:360,height:780}:{width:1440,height:1000},
    ...(mobile?{isMobile:true,hasTouch:true}:{}),reducedMotion:'reduce'});
   const page=await context.newPage();page.setDefaultTimeout(30000);
   page.on('pageerror',e=>errors.push(e.message));
   for(const [beam,energy,percent] of [['j-parc-neutrino','1.2','49.42'],['lbnf','5.18','50.04']]) {
    await page.goto(`${base}/atlas?e=0.8#/view/beam-section/${beam}`);
    await page.locator('#osc-energy').waitFor();
    await page.locator('.osc-experiment > summary').focus();await page.keyboard.press('Enter');
    assert.equal(await page.locator('#osc-prediction-answer').isVisible(),false,'answer must wait for a prediction');
    await page.getByRole('button',{name:'Test doubling on the curve',exact:true}).focus();
    await page.keyboard.press('Enter');
    assert.equal(await page.locator('#osc-energy').inputValue(),energy);
    assert.match(await page.locator('#osc-readout').innerText(),new RegExp(`${percent.replace('.','\\.')}%`));
    const answer=page.locator('#osc-prediction-answer');
    assert.equal(await answer.isVisible(),true);
    assert.match(await answer.innerText(),/phase.*halv|halv.*phase/i);
    assert.match(await answer.innerText(),/round|0.01/);
    assert.equal(new URL(page.url()).searchParams.get('e'),energy);
    const point=await page.locator('.osc-selected-point').getAttribute('cy');
    await page.screenshot({path:path.join(out,`${engine}-${mobile?'360':'desktop'}-${beam}-prediction.png`)});
    await page.locator('#osc-energy').focus();await page.keyboard.press('ArrowRight');
    assert.equal(await answer.isVisible(),false,'manual exploration must not leave stale feedback');
    assert.notEqual(await page.locator('.osc-selected-point').getAttribute('cy'),point);
    assert.equal(await page.locator('#osc-energy').evaluate(n=>n===document.activeElement),true);
    await page.reload();await page.locator('#osc-energy').waitFor();
    assert.equal(await answer.isVisible(),false,'pasted physical state does not invent a previous prediction');
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'no horizontal overflow');
   }
   await context.close();
   console.log(`PASS ${engine} ${mobile?'360px mobile':'desktop'} predict-and-test, actual values, keyboard, URL, reset`);
  }
  assert.deepEqual(errors,[]);
 } finally {await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
