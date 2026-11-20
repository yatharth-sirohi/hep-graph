/* Save the selected teaching model through the existing export dialog. */
const {chromium,webkit}=require('playwright');
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const engine=process.env.HEP_BROWSER||'chromium';const base=process.env.HEP_URL||'http://127.0.0.1:8876';
const out=process.env.HEP_ATLAS_OUTPUT||path.join(__dirname,'../test-results/atlas-iterations');fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await ({chromium,webkit}[engine]).launch({headless:true});const errors=[];
 try {
  for(const mobile of (process.env.HEP_MOBILE_ONLY?[true]:[false,true])) {
   const context=await browser.newContext({viewport:mobile?{width:360,height:780}:{width:1440,height:1000},
    ...(mobile?{isMobile:true,hasTouch:true}:{}),reducedMotion:'reduce',acceptDownloads:true});
   const page=await context.newPage();page.setDefaultTimeout(40000);page.on('pageerror',e=>errors.push(e.message));
   async function open() {
    const trigger=page.locator(mobile?'#phone-export-btn':'#export-btn');
    await trigger.waitFor();await trigger.focus();await page.keyboard.press('Enter');
    await page.locator('#export-popover').waitFor();
    await page.waitForFunction(()=>!document.querySelector('.export-download')?.disabled);
   }
   async function ready(energy) {
    await page.waitForFunction(e=>{
     const x=window.__hepAtlasExport?.last;
     return !document.querySelector('.export-download')?.disabled&&x?.title==='Oscillation lab'
      &&x.footerLines.some(line=>line.includes(`E = ${e} GeV`));
    },energy);
    const meta=await page.evaluate(()=>window.__hepAtlasExport.last);
    assert.equal(await page.locator('.export-image-notes').count(),1,'captured notes are available as text, not only canvas pixels');
    assert((await page.locator('.export-image-notes').textContent()).includes(`E = ${energy} GeV`));
    assert.match(meta.footerLines.join('\n'),/two-flavor vacuum teaching model/i);
    assert.match(meta.footerLines.join('\n'),/not a DUNE prediction.*event rate/i);
    assert.match(meta.footerLines.join('\n'),/1.267.*km.*GeV.*eV/);
    assert.match(meta.footerLines.join('\n'),/45.*2.5/);
    assert.match(meta.footerLines.join('\n'),/https:\/\/t2k-experiment.org/);
    return meta;
   }
   async function save(label) {
    const promised=page.waitForEvent('download');
    await page.locator('.export-download').focus();await page.keyboard.press('Enter');
    const download=await promised;const file=path.join(out,`${engine}-${mobile?'360':'desktop'}-${label}.png`);
    await download.saveAs(file);const png=fs.readFileSync(file);
    assert.equal(png.subarray(1,4).toString(),'PNG');assert(png.length>15000,'saved figure is not an empty canvas');
    const meta=await page.evaluate(()=>window.__hepAtlasExport.last);
    assert.equal(png.readUInt32BE(16),meta.width);assert.equal(png.readUInt32BE(20),meta.height);
    return meta;
   }
   await page.goto(mobile?`${base}/atlas?e=2.5&step=5&present=1#/tour/neutrino-beams-through-the-earth`:`${base}/atlas?e=2.5#/view/beam-section/lbnf`);await page.locator('#osc-energy').waitFor();
   await open();await page.locator('#export-figure').waitFor();
   assert.equal(await page.locator('#export-figure').inputValue(),'geometry');
   let meta=await page.evaluate(()=>window.__hepAtlasExport.last);
   assert.equal(meta.title,'Beam through the Earth');assert.match(meta.filename,/beam-section-lbnf/);
   assert.deepEqual([meta.width,meta.height],[1920,1080],'existing geometry slide stays unchanged');
   await page.locator('#export-figure').selectOption('oscillation');meta=await ready(2.5);
   assert.match(meta.filename,/oscillation-lab-lbnf/);
   assert.match(meta.footerLines.join('\n'),/#\/view\/beam-section\/lbnf/);
   assert.match(meta.footerLines.join('\n'),/1285 km/);
   assert.match(meta.footerLines.join('\n'),/2007.06722v4#page=12/);
   await page.locator('.export-image-notes > summary').focus();await page.keyboard.press('Enter');
   assert.notEqual(await page.locator('.export-image-notes').getAttribute('open'),null);
   assert.equal(await page.locator('.export-image-notes a[href="https://arxiv.org/pdf/2007.06722v4#page=12"]').count(),1);
   await page.keyboard.press('Enter');
   await save('dune-oscillation-export');
   if(mobile){assert.equal(new URL(page.url()).searchParams.get('step'),'5');assert.equal(new URL(page.url()).searchParams.get('present'),'1');}
   // Quiet energy updates must invalidate an open preview without remounting the lab.
   await page.locator('#osc-energy').focus();await page.keyboard.press('ArrowRight');await ready(2.51);
   assert.equal(await page.locator('#export-popover').isVisible(),true);
   await page.keyboard.press('Escape');await page.locator('#export-popover').waitFor({state:'hidden'});
   assert.equal(await page.evaluate(()=>document.activeElement?.id),mobile?'phone-export-btn':'export-btn');
   if(mobile)assert.equal(new URL(page.url()).searchParams.get('present'),'1','Escape closes the dialog before presenter mode');
   await page.locator('#osc-baseline').selectOption('j-parc-neutrino');
   await page.waitForFunction(()=>document.querySelector('#osc-baseline')?.value==='j-parc-neutrino');
   await page.locator('#osc-energy-number').fill('1.2');await page.locator('#osc-energy-number').press('Tab');
   await open();await page.locator('#export-figure').selectOption('oscillation');meta=await ready(1.2);
   assert.match(meta.filename,/oscillation-lab-j-parc-neutrino/);
   assert.match(meta.footerLines.join('\n'),/295.3352 km/);
   assert.match(meta.footerLines.join('\n'),/1106.1238v2#page=10/);
   assert.match(meta.footerLines.join('\n'),/49.42%.*50.58%/);
   if(!mobile){await page.locator('input[name=export-size][value=double]').check();await ready(1.2);}
   await save('t2k-oscillation-export');
   assert(await page.locator('#export-popover').evaluate(n=>n.scrollWidth<=n.clientWidth+1),'dialog fits its viewport');
   assert.equal(await page.locator('.osc-export-stage').count(),0,'temporary export figures are released');
   await page.locator('#export-figure').selectOption('geometry');
   await page.waitForFunction(()=>!document.querySelector('.export-download')?.disabled&&window.__hepAtlasExport?.last?.title==='Beam through the Earth');
   await page.getByRole('button',{name:'Close export',exact:true}).click();
   if(!mobile) {
    await page.goto(`${base}/atlas?step=4&e=1.2&present=1#/tour/neutrino-beams-through-the-earth`);
    await page.locator('#osc-energy').waitFor();await open();await page.locator('#export-figure').selectOption('oscillation');
    meta=await ready(1.2);assert.equal(meta.timeline,'2012','the export follows the selected tour step year');
    await page.getByRole('button',{name:'Close export',exact:true}).click();
    await page.goto(`${base}/atlas#/view/underground`);await page.locator('#ug-chart svg.ch-svg').waitFor();await open();
    assert.equal(await page.locator('#export-figure-field').isVisible(),false,'single-figure views keep their existing dialog');
    assert.equal(await page.evaluate(()=>window.__hepAtlasExport.last.title),'Going underground');
   }
   await context.close();console.log(`PASS ${engine} ${mobile?'360px mobile':'desktop'}: geometry default, lab PNGs, state/parameters/sources, live energy, baseline changes, keyboard, cleanup`);
  }
  assert.deepEqual(errors,[]);
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
