/* Results → existing Higgs mass question: real data, native links and tour player. */
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
   page.on('pageerror',error=>errors.push(error.message));
   // Test copied/native destinations after their startup requests settle.
   // Rapid cold exits are separately covered by browser_atlas_navigation_lifecycle;
   // this journey retains a strict assertion against all browser errors.
   const visit=url=>page.goto(url,{waitUntil:'networkidle'});
   for(const result of ['atlas-higgs-observation-2012','cms-higgs-boson-observation-2012']) {
    await visit(`${base}/atlas?data=generated&embed=1&theme=projector&m=results#/result/${result}`);
    const exercise=page.getByRole('link',{name:'Compare the Higgs masses',exact:true});
    await exercise.waitFor();
    const href=await exercise.getAttribute('href');
    const linked=new URL(href,page.url());
    assert.equal(linked.searchParams.get('step'),'7');
    assert.equal(linked.hash,'#/tour/higgs-hunt');
    assert.equal(linked.searchParams.get('data'),'generated');
    assert.equal(linked.searchParams.get('embed'),'1');
    assert.equal(linked.searchParams.get('theme'),'projector');
    assert.equal(await page.locator('.result-evidence').evaluate(node=>node.scrollWidth<=node.clientWidth+1),true);
    await exercise.focus();await page.keyboard.press('Enter');
    await page.waitForURL(url=>url.hash==='#/tour/higgs-hunt'&&url.searchParams.get('step')==='7');
    await page.locator('.tour-question').waitFor();
    assert.match(await page.locator('.tour-q-prompt').innerText(),/126.0.*125.3/s);
    assert.equal(await page.locator('.tour-answer').isVisible(),false);
    await page.getByRole('button',{name:'Show answer',exact:true}).focus();await page.keyboard.press('Enter');
    assert.equal(await page.locator('.tour-answer').isVisible(),true);
    assert.match(await page.locator('.tour-q-answer').innerText(),/independent.*0.82/s);
    assert.equal(await page.locator('.tour-question').evaluate(node=>node.scrollWidth<=node.clientWidth+1),true);
    const deep=linked.href; // The copied href, independently of callback navigation.
    await page.screenshot({path:path.join(out,`${engine}-${mobile?'360':'desktop'}-${result}-mass-question.png`)});
    await page.goBack();await page.waitForURL(url=>url.hash===`#/result/${result}`);
    await exercise.waitFor();
    await visit(deep);
    await page.locator('.tour-question').waitFor();
    assert.match(await page.locator('.tour-q-prompt').innerText(),/two measurements agree/);
    assert.equal(await page.locator('.tour-answer').isVisible(),false,'deep link starts a fresh prediction');
    assert.equal(new URL(page.url()).searchParams.get('embed'),'1');
    assert.equal(new URL(page.url()).searchParams.get('theme'),'projector');
   }
   if(!mobile) {
    // Existing topic links use the same helper and must name their own step,
    // even when the page being left has an unrelated step in its query.
    await visit(`${base}/atlas?data=generated&embed=1&theme=projector&step=99#/topic/higgs-physics`);
    const topicTour=page.locator('.tour-links a').first();await topicTour.waitFor();
    const target=new URL(await topicTour.getAttribute('href'),page.url());
    assert(Number(target.searchParams.get('step'))>=1);
    assert.notEqual(target.searchParams.get('step'),'99');
    assert.equal(target.searchParams.get('data'),'generated');
    assert.equal(target.searchParams.get('embed'),'1');
    assert.equal(target.searchParams.get('theme'),'projector');
    await visit(target.href);
    await page.locator('#tour-card').waitFor();
    assert.equal(new URL(page.url()).searchParams.get('step'),target.searchParams.get('step'));
    for(const [route,selector] of [['result/atlas-higgs-observation-2012','.evidence-next-question a'],['topic/higgs-physics','.tour-links a']]) {
     await visit(`${base}/atlas?data=generated&theme=projector#/${route}`);
     const lesson=page.locator(selector).first();await lesson.waitFor();
     await page.locator('#theme-btn').click();
     await page.waitForURL(url=>url.searchParams.get('theme')==='standard');
     const changed=new URL(await lesson.getAttribute('href'),page.url());
     assert.equal(changed.searchParams.get('theme'),'standard','rendered links follow a later theme change');
     assert.equal(changed.searchParams.get('data'),'generated');
     await visit(changed.href);await page.locator('#tour-card').waitFor();
     assert.notEqual(await page.locator('html').getAttribute('data-theme'),'projector');
    }
   }
   const generic=await page.evaluate(async()=>{
    const {renderEvidence}=await import('/atlas/js/result-evidence.js');
    return renderEvidence({experiment:'Example',measurement:'Measured a flux',evidence:[]}).textContent;
   });
   assert.doesNotMatch(generic,/Higgs|Compare the|mass measurements/);
   await page.waitForLoadState('networkidle');
   await context.close();
   console.log(`PASS ${engine} ${mobile?'360px mobile':'desktop'}: both evidence trails, existing question, keyboard reveal, working, Back, deep links, optional data`);
  }
  assert.deepEqual(errors,[]);
 } finally {await browser.close()}
})().catch(error=>{console.error(error);process.exitCode=1});
