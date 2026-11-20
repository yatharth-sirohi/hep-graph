/* Question-first entry reuses the collision lab, predictor, sources and exporter. */
const {chromium,webkit}=require('playwright');const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');const {openPrimary}=require('./browser_support/primary.cjs');
const engine=process.env.HEP_BROWSER||'chromium',base=process.env.HEP_URL||'http://127.0.0.1:8876';
const out=process.env.HEP_ATLAS_OUTPUT||path.join(__dirname,'../test-results/atlas-iterations/cycle17');fs.mkdirSync(out,{recursive:true});
const question='Why do colliders reach higher collision energies?';
(async()=>{const browser=await ({chromium,webkit}[engine]).launch({headless:true});const errors=[];let active,size;
 try{for(const mobile of(process.env.HEP_MOBILE_ONLY?[true]:[false,true])){
  const context=await browser.newContext({viewport:mobile?{width:360,height:780}:{width:1440,height:1000},...(mobile?{isMobile:true,hasTouch:true}:{}),reducedMotion:'reduce',acceptDownloads:true});
  const page=await context.newPage();active=page;size=mobile?'360':'desktop';page.setDefaultTimeout(30000);page.on('pageerror',e=>errors.push(e.message));
  const visit=u=>page.goto(u,{waitUntil:'networkidle'});
  async function openStart(){if(!await page.locator('#start-card').isVisible())await page.locator('#start-here-link').click()}
  async function nativePresenterQuestion(title,hash,blank=false){
   await visit(`${base}/atlas?data=generated&theme=projector&step=5&present=1&e=1.2&th=15&le=1#/tour/neutrino-beams-through-the-earth`);await page.locator('.tour-question').waitFor();await openStart();
   await page.keyboard.press('Escape');assert.equal(await page.locator('#start-card').isVisible(),false);assert.equal(new URL(page.url()).searchParams.get('present'),'1','Escape closes Start before the presenter');await openStart();
   const link=page.getByRole('link',{name:title,exact:false});await link.focus();
   if(blank){await page.keyboard.press('b');await page.locator('#tour-blank').waitFor();await page.keyboard.press('Escape');await page.locator('#tour-blank').waitFor({state:'hidden',timeout:5000});assert.equal(await page.locator('#start-card').isVisible(),true,'first Escape only dismisses the blank');await page.keyboard.press('Escape');assert.equal(await page.locator('#start-card').isVisible(),false);assert.equal(new URL(page.url()).searchParams.get('present'),'1');await openStart();await link.focus();}
   if(blank){await page.keyboard.press('b');await page.locator('#tour-blank').waitFor();await page.keyboard.press('Enter');await page.locator('#tour-blank').waitFor({state:'hidden'});assert.equal(new URL(page.url()).hash,'#/tour/neutrino-beams-through-the-earth','first Enter only dismisses the presenter blank')}
   await page.keyboard.press('Enter');await page.waitForURL(u=>u.hash===hash,{timeout:5000});assert.equal(await page.locator('#start-card').isVisible(),false);assert.equal(new URL(page.url()).searchParams.has('present'),false,'Start questions use their authored default presentation');
  }
  if(process.env.HEP_START_KEYS_ONLY||process.env.HEP_START_BLANK_ONLY){await nativePresenterQuestion('How did ATLAS and CMS establish the Higgs discovery?','#/tour/higgs-hunt',!!process.env.HEP_START_BLANK_ONLY);await context.close();console.log(`PASS ${engine} ${size}: native Start question from presenter`);continue}
  await visit(`${base}/atlas?data=generated&theme=projector&m=results&rt=higgs-physics&ry=2012&r=1990-1995`);await page.locator('#mode-panel').waitFor();await openStart();
  const link=page.getByRole('link',{name:question,exact:false});assert.equal(await link.count(),1,'Start here needs the collision-energy question');
  const href=new URL(await link.getAttribute('href'),page.url());assert.equal(href.hash,'#/view/energy-frontier/collision');assert.equal(href.searchParams.get('ce'),'450');assert.equal(href.searchParams.get('data'),'generated');assert.equal(href.searchParams.get('theme'),'projector');
  for(const key of ['e','th','le','step','present','m'])assert(!href.searchParams.has(key),`${key} cannot leak into a copied question`);
  await link.focus();await page.keyboard.press('Enter');await page.waitForURL(u=>u.hash==='#/view/energy-frontier/collision');
  const lab=page.locator('.collision-lab'),plot=lab.locator('.collision-plot'),input=page.locator('#collision-energy');await input.waitFor();
  for(const key of ['m','rt','ry','r','present','th','le'])assert(!new URL(page.url()).searchParams.has(key),`${key} cannot survive a fresh Start destination`);
  assert.equal(await input.inputValue(),'450');assert.equal(await page.locator('#mode-panel').isVisible(),false);assert.equal(await page.locator('#tour-card').isVisible(),false);
  assert.equal(await page.locator('.collision-lab').count(),1);assert.equal(await page.locator('.collision-prediction').count(),1);
  async function visible(nodes){await page.waitForFunction(selectors=>{const frame=document.querySelector('#view-host').getBoundingClientRect(),head=document.querySelector('#view-host .view-head').getBoundingClientRect();return selectors.every(selector=>{const r=document.querySelector(selector).getBoundingClientRect();return r.top>=Math.max(frame.top,head.bottom)&&r.bottom<=frame.bottom&&r.left>=frame.left&&r.right<=frame.right})},nodes,{timeout:5000})}
  // Check the useful visual before scrolling or focusing a control.
  await visible(['.collision-lab .collision-plot']);assert.match(await page.locator('.collision-entry-context').innerText(),/450.*two accelerated beams/s);
  assert(await lab.evaluate(n=>!!(n.compareDocumentPosition(document.querySelector('.ef-figure'))&Node.DOCUMENT_POSITION_FOLLOWING)));
  await page.screenshot({path:path.join(out,`${engine}-${size}-collision-question-entry.png`)});
  const timeSnapshot=()=>page.evaluate(()=>({year:new URL(location.href).searchParams.get('y'),range:new URL(location.href).searchParams.get('r'),readout:document.querySelector('#timeline-readout')?.textContent,single:document.querySelector('#timeline-mode-year')?.classList.contains('is-active'),rangeMode:document.querySelector('#timeline-mode-range')?.classList.contains('is-active'),noteHidden:document.querySelector('#ef-year-note')?.hidden,note:document.querySelector('#ef-year-note')?.textContent}));
  const clickedTime=await timeSnapshot();assert.equal(clickedTime.single,true,'Start resets an old range to the dataset startup year');assert.equal(clickedTime.noteHidden,false);await page.waitForLoadState('networkidle');await page.goto('about:blank');await visit(href.href);await input.waitFor();await visible(['.collision-lab .collision-plot']);
  assert.deepEqual(await timeSnapshot(),clickedTime,'normal Start activation and its copied link must use the same startup year and chart note');

  await input.focus();if(mobile)await visible(['.collision-lab .collision-plot','#collision-energy']);
  await page.keyboard.press('ArrowUp');await input.press('Tab');assert.equal(await input.inputValue(),'450.1');assert.equal(new URL(page.url()).searchParams.get('ce'),'450.1');
  await input.fill('450');await input.press('Tab');await lab.locator('.collision-prediction>summary').focus();await page.keyboard.press('Enter');await page.locator('#collision-test').focus();await page.keyboard.press('Space');await page.locator('#collision-answer').waitFor();
  assert.match(await page.locator('#collision-answer').innerText(),/450.*1800.*4.00/s);assert.equal(new URL(page.url()).searchParams.get('ce'),'1800');assert.equal(new URL(page.url()).hash,'#/view/energy-frontier/collision');
  await page.locator('#collision-method>summary').focus();await page.keyboard.press('Enter');assert.match(await page.locator('#collision-method').innerText(),/rest energy.*kinetic/s);
  const url='https://pdg.lbl.gov/2024/reviews/rpp2024-rev-kinematics.pdf#page=1',source=page.locator(`#collision-method a[href="${url}"]`);
  if((engine==='chromium'&&!mobile)||(engine==='webkit'&&mobile))await openPrimary(context,page,{click:async()=>{await source.focus();await page.keyboard.press('Enter')}},{url,engine,viewport:size,output:out,artifactName:'collision-question-kinematics',requirePDF:true});
  await page.bringToFront();await openStart();await page.getByRole('link',{name:question,exact:false}).focus();await page.keyboard.press('Enter');assert.equal(await input.inputValue(),'450');
  await visible(['.collision-lab .collision-plot']);assert.equal(await page.locator('.collision-lab').count(),1,'reopening a question reuses one lab');assert.equal(await page.locator('#view-title').evaluate(n=>n===document.activeElement),true,'same-view question entry focuses its heading');
  await input.fill('1800');await input.press('Tab');const saved=page.url();
  // Same-URL goto with a hash can be same-document navigation. Open a copied link into a fresh document.
  await page.waitForLoadState('networkidle');await page.goto('about:blank');await visit(saved);await input.waitFor();assert.equal(await input.inputValue(),'1800');await visible(['.collision-lab .collision-plot']);assert.equal(await page.locator('#collision-answer').isVisible(),false);
  const trigger=page.locator(mobile?'#phone-export-btn':'#export-btn');await trigger.focus();await page.keyboard.press('Enter');await page.locator('#export-popover').waitFor();assert.equal(await page.locator('#export-figure').inputValue(),'collision');
  await page.waitForFunction(()=>!document.querySelector('.export-download')?.disabled&&window.__hepAtlasExport?.last?.title==='Proton collision-energy model');
  const notes=(await page.evaluate(()=>window.__hepAtlasExport.last.footerLines)).join('\n');assert(notes.includes('E = 1800 GeV'));assert(notes.includes('/energy-frontier/collision'));
  if((engine==='chromium'&&!mobile)||(engine==='webkit'&&mobile)){const pending=page.waitForEvent('download');await page.locator('.export-download').focus();await page.keyboard.press('Enter');const download=await pending;const file=path.join(out,`${engine}-${size}-collision-question-export.png`);await download.saveAs(file);assert(fs.readFileSync(file).length>15000)}
  await page.locator('#export-figure').selectOption('history');await page.waitForFunction(()=>!document.querySelector('.export-download')?.disabled&&window.__hepAtlasExport?.last?.title==='The energy frontier');
  await page.getByRole('button',{name:'Close export',exact:true}).click();
  await page.evaluate(async()=>{const s=await import('/atlas/js/state.js');s.navigate({entity:{type:'view',slug:'energy-frontier'}})});await input.waitFor();assert.equal(await input.inputValue(),'1800');
  assert(await lab.evaluate(n=>!!(n.compareDocumentPosition(document.querySelector('.ef-figure'))&Node.DOCUMENT_POSITION_PRECEDING)));
  await page.goBack();await input.waitFor();await visible(['.collision-lab .collision-plot']);assert.equal(await input.inputValue(),'1800');
  await visit(saved+'/');await input.waitFor();assert.equal(await input.inputValue(),'1800');assert.equal(new URL(page.url()).hash,'#/view/energy-frontier/collision');
  if(mobile){await visit(saved.replace('theme=projector','theme=standard'));await input.waitFor();await visible(['.collision-lab .collision-plot']);await page.screenshot({path:path.join(out,`${engine}-360-collision-question-standard.png`)})}
  await openStart();await page.getByRole('link',{name:'Follow a guided tour',exact:false}).click();await page.locator('#mode-panel .tour-start').first().waitFor();
  assert.equal(await page.locator('#mode-panel').isVisible(),true);assert.equal(new URL(page.url()).hash,'');assert.equal(new URL(page.url()).searchParams.get('m'),'tours');assert.equal(new URL(page.url()).searchParams.has('ce'),false);
  await visit(saved.replace('data=generated','data=generated&embed=1'));await input.waitFor();assert.equal(await input.inputValue(),'1800');assert.equal(new URL(page.url()).searchParams.get('embed'),'1');
  await nativePresenterQuestion('How did ATLAS and CMS establish the Higgs discovery?','#/tour/higgs-hunt');
  await nativePresenterQuestion('Why do neutrino beams go through the Earth?','#/tour/neutrino-beams-through-the-earth');
  assert.equal(new URL(page.url()).searchParams.get('e'),'2.5');for(const key of ['th','le','present'])assert(!new URL(page.url()).searchParams.has(key),'restarting a beam question drops the prior model/presenter setup');
  await nativePresenterQuestion(question,'#/view/energy-frontier/collision',true);await input.waitFor();assert.equal(new URL(page.url()).searchParams.has('present'),false);assert.equal(new URL(page.url()).searchParams.has('e'),false);
  await page.waitForLoadState('networkidle');await context.close();console.log(`PASS ${engine} ${size}: native question entry, first visual/input bounds, shared predictor, scoped/copy/Back/aliases, primary/model export, normal chart and presenter blank priority`);
 }assert.deepEqual(errors,[])}catch(error){if(active&&!active.isClosed()){console.error('BROWSER ERRORS',JSON.stringify(errors));console.error(await active.evaluate(()=>({url:location.href,title:document.querySelector('#view-title')?.textContent,startOpen:!document.querySelector('#start-card')?.hidden,input:document.querySelector('#collision-energy')?.value,scroll:document.querySelector('#view-host')?.scrollTop,plot:document.querySelector('.collision-plot')?.getBoundingClientRect().toJSON(),frame:document.querySelector('#view-host')?.getBoundingClientRect().toJSON(),head:document.querySelector('.view-head')?.getBoundingClientRect().toJSON()})));await active.screenshot({path:path.join(out,`${engine}-${size}-collision-question-failure.png`)})}throw error}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
