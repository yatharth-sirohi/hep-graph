/* A selected teaching angle belongs to the existing lab, curve, URL and export. */
const {chromium,webkit}=require('playwright');const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');const {openPrimary}=require('./browser_support/primary.cjs');
const engine=process.env.HEP_BROWSER||'chromium',base=process.env.HEP_URL||'http://127.0.0.1:8876';
const out=process.env.HEP_ATLAS_OUTPUT||path.join(__dirname,'../test-results/atlas-iterations');fs.mkdirSync(out,{recursive:true});
(async()=>{const browser=await ({chromium,webkit}[engine]).launch({headless:true});const errors=[];let active=null,size='desktop';
 try{for(const mobile of [false,true]){
  const context=await browser.newContext({viewport:mobile?{width:360,height:780}:{width:1440,height:1000},...(mobile?{isMobile:true,hasTouch:true}:{}),reducedMotion:'reduce',acceptDownloads:true});
  const page=await context.newPage();active=page;size=mobile?'360':'desktop';page.setDefaultTimeout(30000);page.on('pageerror',e=>errors.push(e.message));
  const visit=u=>page.goto(u,{waitUntil:'networkidle'}),angle=page.locator('#osc-angle'),readout=page.locator('#osc-readout');
  const percent=async()=>Number((await readout.innerText()).match(/P = ([\d.]+)%/)[1]);
  const address=`${base}/atlas?data=generated&e=.6&th=45&theme=${mobile?'projector':'standard'}#/view/beam-section/j-parc-neutrino`;
  await visit(address);await angle.waitFor();assert.equal(await angle.inputValue(),'45');
  const peakPosition=()=>page.locator('.osc-max-point').evaluate(n=>{const [x,y]=n.getAttribute('d').slice(1).split('l')[0].split(',').map(Number);return{x:(x-48)/(n.ownerSVGElement.viewBox.baseVal.width-66),y}});
  const reference=await percent(),peak45=await peakPosition();
  assert.match(await page.locator('#osc-angle-help').innerText(),/neutrino.*parameter|model.*parameter/i);
  await page.locator('.osc-angle-experiment > summary').click();await page.locator('#osc-angle-test').click();
  assert.equal(await angle.inputValue(),'15');assert.equal(new URL(page.url()).searchParams.get('th'),'15');
  assert(Math.abs(await percent()-.25*reference)<.02,'the selected probability follows the mixing amplitude');
  assert.match(await page.locator('#osc-angle-answer').innerText(),/25%/);assert.match(await page.locator('#osc-angle-answer').innerText(),/same|unchanged/);
  const peak15=await peakPosition();
  assert(Math.abs(peak15.x-peak45.x)<1e-12,'mixing preserves the peak energy even if layout changes the SVG width');assert(peak15.y>peak45.y,'weaker mixing lowers the peak');
  await angle.focus();await page.keyboard.press('ArrowLeft');assert.equal(await angle.inputValue(),'14');
  assert.equal(await page.locator('#osc-angle-answer').isVisible(),false,'a changed input clears stale prediction feedback');assert.equal(await angle.evaluate(n=>n===document.activeElement),true);
  await page.keyboard.press('Home');assert.equal(await angle.inputValue(),'0');assert.equal(await percent(),0);
  assert.equal(await page.locator('.osc-max-point').count(),0,'a flat curve has no distinct first maximum');
  assert.equal(await page.getByRole('button',{name:'Try the first maximum',exact:true}).isDisabled(),true);
  assert.match(await page.locator('.osc-maximum').innerText(),/no distinct|no oscillations/i);
  await page.locator('.osc-flavors > summary').click();assert.equal(await page.locator('.osc-survival-value').innerText(),'100.00%');
  assert.equal(await page.locator('.osc-conversion-value').innerText(),'0.00%');
  await page.locator('.osc-experiment > summary').click();assert.equal(await page.getByRole('button',{name:'Test doubling on the curve',exact:true}).isDisabled(),true);
  await page.locator('#osc-angle-test').click();await page.getByRole('button',{name:'Test doubling on the curve',exact:true}).click();
  assert.equal(await page.locator('#osc-energy').inputValue(),'1.2');assert(Math.abs(await percent()-12.3543544)<.01);
  assert.match(await page.locator('#osc-prediction-answer').innerText(),/25%.*12.5%/s);
  await page.locator('#osc-keep-ratio').check();await page.locator('#osc-baseline').selectOption('lbnf');
  await page.waitForFunction(()=>document.querySelector('#osc-baseline')?.value==='lbnf');assert.equal(await angle.inputValue(),'15');
  assert.equal(new URL(page.url()).searchParams.get('th'),'15');assert.equal(await page.locator('#osc-energy').inputValue(),'5.22');
  await page.goBack();await page.waitForFunction(()=>document.querySelector('#osc-baseline')?.value==='j-parc-neutrino');assert.equal(await angle.inputValue(),'15');
  const saved=page.url();await page.reload({waitUntil:'networkidle'});await angle.waitFor();assert.equal(await angle.inputValue(),'15');
  await page.locator('#start-here-link').click();await page.locator('[data-start-action=results]').click();await page.waitForURL(/m=results/);assert.equal(new URL(page.url()).searchParams.has('th'),false);
  await page.goBack();await angle.waitFor();assert.equal(await angle.inputValue(),'15');
  if(mobile){
   // macOS WebKit includes native sliders with Option-Tab, as verified on the actual control.
   const nextControl=engine==='webkit'?'Alt+Tab':'Tab';
   await page.locator('#osc-energy-number').fill('1.23456');await page.locator('#osc-energy-number').press(nextControl);assert.equal(await page.locator('#osc-energy').inputValue(),'1.23');
   await page.locator('#osc-energy-number').fill('1.2');await page.locator('#osc-energy-number').press(nextControl);
   if(engine==='webkit')assert.equal(await page.evaluate(()=>document.activeElement?.id),'osc-angle');
  }else await angle.focus();
  if(mobile)await page.waitForFunction(()=>{const frame=document.querySelector('#view-host').getBoundingClientRect(),a=document.querySelector('#osc-angle').getBoundingClientRect(),p=document.querySelector('.osc-plot').getBoundingClientRect(),e=document.querySelector('#osc-energy').getBoundingClientRect();return e.top>=frame.top&&e.bottom<=frame.bottom&&a.top>=frame.top&&a.bottom<=frame.bottom&&p.top>=frame.top&&p.bottom<=frame.bottom},null,{timeout:5000});
  assert(await page.locator('.osc-lab').evaluate(n=>n.scrollWidth<=n.clientWidth+1));await page.screenshot({path:path.join(out,`${engine}-${size}-mixing.png`)});
  await page.locator(mobile?'#phone-export-btn':'#export-btn').click();await page.locator('#export-figure').selectOption('oscillation');
  const exportReady=theta=>page.waitForFunction(t=>!document.querySelector('.export-download')?.disabled&&window.__hepAtlasExport?.last?.title==='Oscillation lab'&&window.__hepAtlasExport.last.footerLines.some(s=>s.includes(`θ = ${t}°`)),theta);
  await exportReady(15);let meta=await page.evaluate(()=>window.__hepAtlasExport.last);assert.match(meta.footerLines.join('\n'),/th=15/);assert.match(meta.footerLines.join('\n'),/PDG|pdg.lbl.gov/);
  const pending=page.waitForEvent('download');await page.locator('.export-download').click();await (await pending).saveAs(path.join(out,`${engine}-${size}-mixing15-export.png`));
  await angle.focus();await page.keyboard.press('Home');await exportReady(0);meta=await page.evaluate(()=>window.__hepAtlasExport.last);assert.match(meta.footerLines.join('\n'),/no distinct|no oscillations/i);
  if(engine==='chromium'&&!mobile){const zero=page.waitForEvent('download');await page.locator('.export-download').click();await (await zero).saveAs(path.join(out,'chromium-desktop-mixing0-export.png'))}
  await page.getByRole('button',{name:'Close export',exact:true}).click();
  await visit(saved);await angle.waitFor();await page.locator('.osc-method > summary').click();
  const primary='https://pdg.lbl.gov/2024/reviews/rpp2024-rev-neutrino-mixing.pdf#page=10',source=page.locator(`.osc-method a[href="${primary}"]`);await source.waitFor();
  if((engine==='chromium'&&!mobile)||(engine==='webkit'&&mobile))await openPrimary(context,page,source,{url:primary,engine,viewport:size,output:out,artifactName:'mixing-equation',requirePDF:true});
  await page.bringToFront();assert.match(await page.locator('#osc-parameters').innerText(),/15°/);
  for(const [raw,expected]of [['NaN','45'],['-2','0'],['90','45']]){await visit(`${base}/atlas?th=${raw}#/view/beam-section/j-parc-neutrino`);await angle.waitFor();assert.equal(await angle.inputValue(),expected);assert(!await readout.innerText().then(s=>s.includes('NaN')))}
  await visit(`${base}/atlas?data=generated&step=5&e=2.5&th=15&present=1#/tour/neutrino-beams-through-the-earth`);await angle.waitFor();assert.equal(await angle.inputValue(),'15');
  await angle.focus();await page.keyboard.press('ArrowLeft');assert.equal(await angle.inputValue(),'14');assert.equal(new URL(page.url()).searchParams.get('step'),'5');assert.equal(await page.locator('#tour-blank').evaluate(n=>n.hidden),true);
  const mixing=page.locator('.osc-angle-experiment');await mixing.locator('summary').focus();await page.keyboard.press('Enter');assert.equal(await mixing.evaluate(n=>n.open),true,'native disclosure key survives presenter mode');
  await page.locator('#osc-angle-start').focus();await page.keyboard.press('Space');assert.equal(await angle.inputValue(),'45');
  await page.locator('#osc-angle-test').focus();await page.keyboard.press('Enter');assert.equal(await angle.inputValue(),'15');assert.equal(await page.locator('#osc-angle-answer').isVisible(),true);
  assert.equal(await page.locator('.tour-answer').evaluate(n=>n.hidden),true,'lab activation must not reveal the tour answer');assert.equal(new URL(page.url()).searchParams.get('step'),'5');
  await page.locator('#osc-angle-start').focus();await page.keyboard.press('Enter');await page.locator('#osc-angle-test').focus();await page.keyboard.press('b');assert.equal(await page.locator('#tour-blank').evaluate(n=>n.hidden),false);
  await page.keyboard.press('Enter');assert.equal(await page.locator('#tour-blank').evaluate(n=>n.hidden),true);assert.equal(await angle.inputValue(),'45','unblanking consumes native activation');
  await page.keyboard.press('Enter');assert.equal(await angle.inputValue(),'15');
  await page.locator('.osc-experiment > summary').focus();await page.keyboard.press('Enter');assert.equal(await page.locator('.osc-experiment').evaluate(n=>n.open),true);
  await page.getByRole('button',{name:'Test doubling on the curve',exact:true}).focus();await page.keyboard.press('Enter');assert.equal(await page.locator('#osc-energy').inputValue(),'5.18');assert.equal(new URL(page.url()).searchParams.get('step'),'5');

  if(mobile){await visit(saved.replace('projector','standard'));await angle.waitFor();await angle.focus();await page.waitForFunction(()=>{const frame=document.querySelector('#view-host').getBoundingClientRect();return['#osc-energy','.osc-plot','#osc-angle'].every(selector=>{const box=document.querySelector(selector).getBoundingClientRect();return box.top>=frame.top&&box.bottom<=frame.bottom})});assert(await page.locator('.osc-lab').evaluate(n=>n.scrollWidth<=n.clientWidth+1))}
  await context.close();console.log(`PASS ${engine} ${size}: mixing amplitude/zero, phase, prediction/doubling, native keys, baseline/history/deep links, source and actual PNG`);
 }assert.deepEqual(errors,[])}catch(error){if(active&&!active.isClosed()){console.error('FAILURE STATE',await active.evaluate(()=>({url:location.href,active:document.activeElement?.id,angle:document.querySelector('#osc-angle')?.value,energy:document.querySelector('#osc-energy')?.value,readout:document.querySelector('#osc-readout')?.textContent})));await active.screenshot({path:path.join(out,`${engine}-${size}-mixing-failure.png`)})}throw error}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
