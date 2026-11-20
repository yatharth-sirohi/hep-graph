/* Last reported beam state, unconfirmed restart, and lazy primary evidence. */
const {chromium,webkit}=require('playwright');
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const engine=process.env.HEP_BROWSER||'chromium';const base=process.env.HEP_URL||'http://127.0.0.1:8876';
const output=process.env.HEP_ATLAS_OUTPUT||path.join(__dirname,'../test-results/atlas-iterations');
const report='https://pac.fnal.gov/wp-content/uploads/2026/10/Final_Public_PAC_Report_Sept2026.pdf';
const routes=['experiment/nova','accelerator/fermilab-main-injector','beamline/numi','detector/nova-near-detector','detector/nova-far-detector'];
fs.mkdirSync(output,{recursive:true});
// A primary link can open HTML (including an origin challenge), a PDF viewer,
// or a native download. Wait for that outcome before navigating the Atlas again.
async function openPrimary(context, page, link, mobile) {
 const opened = new Set(); let response; let settle, fail; let timer;
 const outcome = new Promise((resolve,reject)=>{settle=resolve;fail=reject;timer=setTimeout(()=>reject(Error('Primary navigation did not settle')),45000)});
 const download = async item => {
  if (!item.url().startsWith(report)) return;
  try {
   const file = await item.path();assert(fs.readFileSync(file).subarray(0,5).equals(Buffer.from('%PDF-')));
   await item.saveAs(path.join(output,`${engine}-${mobile?'360':'desktop'}-pac-report.pdf`));
   settle({kind:'download',verified:true});
  } catch(error) { fail(error); }
 };
 const onPage = external => {
  opened.add(external);external.on('download',download);
  external.waitForURL(url=>url.href.startsWith(report),{waitUntil:'domcontentloaded',timeout:45000})
   .then(()=>settle({kind:'page',page:external})).catch(()=>{}); // A PDF download may close its popup.
 };
 const onResponse = value => {if(value.url().startsWith(report))response=value};
 page.on('download',download);context.on('page',onPage);context.on('response',onResponse);
 try {
  await link.click();const result=await outcome;
  // Download.path()/DOMContentLoaded are the terminal events here. WebKit's
  // ordinary Response.finished() can stay pending after a native PDF download.
  const status=response?.status() ?? null;
  const type=response?.headers()['content-type'] ?? '';
  console.log(JSON.stringify({primary:report,engine,viewport:mobile?'360':'desktop',outcome:result.kind,status,
   verifiedPDF:result.verified || (status===200&&/application\/pdf/i.test(type)) || false}));
 } finally {
  clearTimeout(timer);page.off('download',download);context.off('page',onPage);context.off('response',onResponse);
  for(const external of opened){external.off('download',download);if(!external.isClosed())await external.close()}
 }
}
(async()=>{const browser=await ({chromium,webkit}[engine]).launch({headless:true});const errors=[];
 try{for(const mobile of [false,true]){
  const context=await browser.newContext({viewport:mobile?{width:360,height:780}:{width:1440,height:1000},
   ...(mobile?{isMobile:true,hasTouch:true}:{}),reducedMotion:'reduce'});
  const page=await context.newPage();page.setDefaultTimeout(30000);page.on('pageerror',e=>errors.push(e.message));
  const visit=route=>page.goto(`${base}/atlas?y=2026&data=generated&theme=${mobile?'projector':'standard'}#/${route}`,{waitUntil:'networkidle'});
  for(const route of routes){
   const requests=[];const watch=r=>{if(r.url().includes('/provenance.json'))requests.push(r.url())};page.on('request',watch);
   await visit(route);const notice=page.locator('.status-follow-up');await notice.waitFor();
   assert.match(await page.locator('.status-badge').innerText(),/Shutdown.*last reported/is);
   assert.match(await notice.innerText(),/restart.*(?:not confirmed|unconfirmed)/is);
   assert.match(await notice.locator(':scope > p').innerText(),route.startsWith('accelerator/')?/no Main Injector beam/i:/no NuMI beam/i);
   const details=notice.locator('details');assert.equal(await details.getAttribute('data-state'),'idle');
   assert.equal(requests.length,0,'evidence stays lazy until opened');
   await notice.locator('summary').focus();await page.keyboard.press('Enter');
   await page.waitForFunction(()=>document.querySelector('.status-follow-up details')?.dataset.state==='loaded');
   assert(requests.length>0);assert.match(await details.innerText(),/PDF page 4/);
   const primary=notice.locator(`a[href^='${report}']`).first();await primary.waitFor();
   assert(await notice.evaluate(n=>n.scrollWidth<=n.clientWidth+1));
   if(route==='experiment/nova'){
    assert(await notice.evaluate(n=>!!(n.compareDocumentPosition(n.parentElement.querySelector(':scope > [data-summary]'))&Node.DOCUMENT_POSITION_FOLLOWING)),
     'restart qualification stays beside the badge, before the introduction');
    await openPrimary(context,page,primary,mobile);
    await page.bringToFront();await notice.locator('summary').focus();await page.keyboard.press('Enter');
    await page.screenshot({path:path.join(output,`${engine}-${mobile?'360':'desktop'}-restart-context.png`)});
    const beam=page.locator('.beam-section-links a').first();await beam.click();await page.locator('#osc-energy').waitFor();
    await page.goBack();await notice.waitFor();assert.equal(new URL(page.url()).hash,'#/experiment/nova');
   }
   page.off('request',watch);console.log(`CHECK ${engine} ${mobile?'360':'desktop'} ${route}: status, lazy evidence and layout`);
  }
  await page.goto(`${base}/atlas?y=2014&data=generated#/experiment/nova`,{waitUntil:'networkidle'});
  await page.locator('.status-badge').waitFor();assert.match(await page.locator('.status-badge').innerText(),/Active/);
  assert.equal(await page.locator('.status-follow-up').count(),0,'current follow-up is absent in the historical view');
  await page.goto(`${base}/atlas?y=2026&data=generated#/experiment/t2k`,{waitUntil:'networkidle'});
  await page.locator('.status-badge').waitFor();assert.equal(await page.locator('.status-follow-up').count(),0);
  {
   let fail=true;await context.route('**/generated/provenance.json',r=>fail?r.fulfill({status:503,body:'Source unavailable'}):r.continue());
   await visit('experiment/nova');await page.locator('.status-follow-up summary').click();
   await page.waitForFunction(()=>document.querySelector('.status-follow-up details')?.dataset.state==='error');
   assert.match(await page.locator('.status-follow-up [role=alert]').innerText(),/Could not load/);fail=false;
   await page.locator('.status-follow-up').getByRole('button',{name:'Retry',exact:true}).focus();await page.keyboard.press('Enter');
   await page.waitForFunction(()=>document.querySelector('.status-follow-up details')?.dataset.state==='loaded');
   assert(await page.locator('.status-follow-up summary').evaluate(n=>n===document.activeElement),'Retry retains keyboard focus at the disclosure');
  }
  await context.close();console.log(`PASS ${engine} ${mobile?'360px mobile':'desktop'}: five last-reported states, lazy evidence and primary-link request, keyboard, history, beam/Back and Retry focus`);
 }assert.deepEqual(errors,[])}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
