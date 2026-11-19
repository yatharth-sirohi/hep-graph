/* Focused review regressions: accepted route alias, accessible error recovery,
   and a real sourced-baseline match just outside the supported energy range. */
const {chromium,webkit}=require('playwright');
const assert=require('node:assert/strict');
const engine=process.env.HEP_BROWSER||'chromium';
const base=process.env.HEP_URL||'http://127.0.0.1:8876';
(async()=>{
 const browser=await ({chromium,webkit}[engine]).launch({headless:true});
 const context=await browser.newContext({viewport:{width:360,height:780},isMobile:true,hasTouch:true,reducedMotion:'reduce'});
 const page=await context.newPage();page.setDefaultTimeout(30000);
 const failures=[];
 page.on('pageerror',error=>failures.push(error.message));
 async function check(name,run) {
  try {await run();console.log(`PASS ${engine}: ${name}`)} catch(error) {failures.push(`${name}: ${error.message}`)}
 }
 async function description() {
  if(engine!=='chromium') return page.locator('#osc-baseline-error').textContent();
  const client=await context.newCDPSession(page);
  try {
   const {root}=await client.send('DOM.getDocument');
   const {nodeId}=await client.send('DOM.querySelector',{nodeId:root.nodeId,selector:'#osc-baseline'});
   const {nodes}=await client.send('Accessibility.getPartialAXTree',{nodeId,fetchRelatives:false});
   return nodes.find(node=>node.role?.value==='combobox')?.description?.value||'';
  } finally {await client.detach()}
 }
 async function refuse() {
  await page.goto(`${base}/atlas?e=2&le=1#/view/beam-section/j-parc-neutrino`);
  await page.locator('#osc-energy').waitFor();
  await page.locator('#osc-baseline').selectOption('lbnf');
  assert.match(await description(),/outside/);
 }
 try {
  await check('accepted tour alias preserves energy and L/E preference',async()=>{
   await page.goto(`${base}/atlas?step=5&e=2.5&le=1#/view/tour/neutrino-beams-through-the-earth`);
   await page.locator('#osc-energy').waitFor();
   assert.match(page.url(),/#\/tour\/neutrino-beams-through-the-earth$/);
   assert.equal(await page.locator('#osc-energy').inputValue(),'2.5');
   assert.equal(await page.locator('#osc-keep-ratio').isChecked(),true);
  });
  await check('checkbox recovery clears the computed error description',async()=>{
   await refuse();
   await page.locator('#osc-keep-ratio').focus();await page.keyboard.press('Space');
   assert.equal(await page.locator('#osc-baseline-error').isVisible(),false);
   assert.doesNotMatch(await description(),/outside/);
  });
  await check('energy recovery clears the computed error description',async()=>{
   await refuse();
   await page.locator('#osc-energy').focus();await page.keyboard.press('ArrowLeft');
   assert.equal(await page.locator('#osc-baseline-error').isVisible(),false);
   assert.doesNotMatch(await description(),/outside/);
  });
  await check('near-boundary refusal explains why rounded 0.2 is unsupported',async()=>{
   await page.goto(`${base}/atlas?e=.2&le=1#/view/beam-section/j-parc-neutrino`);
   await page.locator('#osc-energy').waitFor();
   await page.locator('#osc-baseline').selectOption('j-parc-neutrino~1');
   assert.equal(await page.locator('#osc-baseline').inputValue(),'j-parc-neutrino');
   assert.equal(await page.locator('#osc-energy').inputValue(),'0.2');
   assert.match(await page.locator('#osc-baseline-error').innerText(),/0\.199|below 0\.2/);
  });
  assert.deepEqual(failures,[]);
 } finally {await context.close();await browser.close()}
})().catch(error=>{console.error(error);process.exitCode=1});
