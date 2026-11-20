/* Two-flavor learning: selected energy drives both outcomes, with no color dependency. */
const {chromium,webkit}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const engine=process.env.HEP_BROWSER||'chromium';
const base=process.env.HEP_URL||'http://127.0.0.1:8876';
const out=process.env.HEP_ATLAS_OUTPUT||path.join(__dirname,'../test-results/atlas-iterations');
fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await ({chromium,webkit}[engine]).launch({headless:true});const errors=[];
 try {
  for(const mobile of [false,true]) {
   const context=await browser.newContext({viewport:mobile?{width:360,height:780}:{width:1440,height:1000},
    ...(mobile?{isMobile:true,hasTouch:true}:{}),reducedMotion:'reduce'});
   const page=await context.newPage();page.setDefaultTimeout(30000);page.on('pageerror',error=>errors.push(error.message));
   const summary=page.locator('.osc-flavors > summary');
   async function open() {await summary.focus();await page.keyboard.press('Enter')}
   async function values(l,e) {
    const raw=Math.sin(1.267*.0025*l/e)**2;
    const converted=Math.round(raw*10000)/100;
    const survival=100-converted;
    assert.equal(await page.locator('#osc-flavor-context').innerText(),`Selected energy: ${e} GeV · Baseline: ${l} km · θ = 45°`);
    assert.equal(await page.locator('.osc-conversion-value').innerText(),`${converted.toFixed(2)}%`);
    assert.equal(await page.locator('.osc-survival-value').innerText(),`${survival.toFixed(2)}%`);
    assert.match(await page.locator('#osc-energy').getAttribute('aria-valuetext'),/original-flavor survival/);
    const widths=await page.locator('.osc-flavor-bar rect[data-probability]').evaluateAll(nodes=>nodes.map(n=>Number(n.getAttribute('width'))));
    assert.equal(widths.length,2);assert(Math.abs(widths[0]+widths[1]-1000)<.001);
   }
   await page.goto(`${base}/atlas?e=.6#/view/beam-section/j-parc-neutrino`);
   await summary.waitFor();assert.equal(await page.locator('.osc-flavors').getAttribute('open'),null);
   await open();await values(295.3352,.6);
   assert.match(await page.locator('.osc-flavors').innerText(),/absorption/);
   assert.match(await page.locator('.osc-flavors').innerText(),/generic flavors|generic flavour/);
   assert.equal(await page.locator('.osc-flavor-bar pattern').count(),1,'striping provides a non-color cue');
   const initial=await page.locator('.osc-survival-part').getAttribute('width');
   await page.locator('#osc-energy-number').fill('1.2');await page.locator('#osc-energy-number').press('Tab');
   await values(295.3352,1.2);
   assert.notEqual(await page.locator('.osc-survival-part').getAttribute('width'),initial);
   await page.locator('#osc-energy').focus();await page.keyboard.press('ArrowRight');await values(295.3352,1.21);
   assert.equal(await page.locator('#osc-energy').evaluate(n=>n===document.activeElement),true);
   await page.getByRole('button',{name:'Try the first maximum',exact:true}).click();await values(295.3352,.6);
   await page.locator('.osc-experiment > summary').click();
   await page.getByRole('button',{name:'Test doubling on the curve',exact:true}).click();await values(295.3352,1.2);
   await page.locator('#osc-keep-ratio').check();await page.locator('#osc-baseline').selectOption('lbnf');
   await page.waitForFunction(()=>document.querySelector('#osc-energy')?.value==='5.22');
   await open();await values(1285,5.22);
   const shared=page.url();
   assert.equal(new URL(shared).searchParams.get('le'),'1');
   await page.locator('.osc-flavors').scrollIntoViewIfNeeded();
   assert(await page.locator('.osc-flavors').evaluate(n=>n.scrollWidth<=n.clientWidth+1));
   assert(await page.locator('#view-host').evaluate(n=>n.scrollWidth<=n.clientWidth+1));
   await page.screenshot({path:path.join(out,`${engine}-${mobile?'360':'desktop'}-flavors.png`)});
   const source=page.locator('.osc-flavors a[href^="https://t2k-experiment.org/"]');
   assert.equal(await source.getAttribute('href'),'https://t2k-experiment.org/neutrinos/beyond-the-standard-model/');
   await page.reload();await summary.waitFor();await open();await values(1285,5.22);
   await page.locator('#start-here-link').click();await page.locator('[data-start-action=results]').click();
   await page.goBack();await page.waitForFunction(()=>document.querySelector('#osc-energy')?.value==='5.22');
   await open();await values(1285,5.22);
   if(mobile) {
    await page.goto(`${base}/atlas?step=5&e=2.5#/tour/neutrino-beams-through-the-earth`);
    await summary.waitFor();await open();await values(1285,2.5);
    await page.locator('#osc-energy').focus();await page.keyboard.press('ArrowRight');await values(1285,2.51);
    assert.equal(new URL(page.url()).searchParams.get('step'),'5','energy control must not advance the tour');
   }
   await context.close();console.log(`PASS ${engine} ${mobile?'360px mobile':'desktop'}: both outcomes, keyboard, peak/doubling, fixed L/E, non-color cues, reload and Back`);
  }
  assert.deepEqual(errors,[]);
 }finally{await browser.close()}
})().catch(error=>{console.error(error);process.exitCode=1});
