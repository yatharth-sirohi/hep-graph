const fs=require('node:fs');const path=require('node:path');const assert=require('node:assert/strict');
// A primary link can open HTML (including an origin challenge), a PDF viewer,
// or a native download. Wait for that outcome before navigating the Atlas again.
async function openPrimary(context, page, link, {url,engine,viewport,output,artifactName='source',requirePDF=false}) {
 const parsed=new URL(url);parsed.hash='';const report=parsed.href;const mobile=viewport==='360';
 const opened = new Set(); let response; let settle, fail; let timer;
 const outcome = new Promise((resolve,reject)=>{settle=resolve;fail=reject;timer=setTimeout(()=>reject(Error('Primary navigation did not settle')),45000)});
 const download = async item => {
  if (!item.url().startsWith(report)) return;
  try {
   const file = await item.path();assert(fs.readFileSync(file).subarray(0,5).equals(Buffer.from('%PDF-')));
   await item.saveAs(path.join(output,`${engine}-${viewport}-${artifactName}.pdf`));
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
  const verifiedPDF=result.verified || (status===200&&/application\/pdf/i.test(type)) || false;
  console.log(JSON.stringify({primary:report,engine,viewport,outcome:result.kind,status,verifiedPDF}));
  if(requirePDF)assert(verifiedPDF,'Primary origin did not return a PDF');
 } finally {
  clearTimeout(timer);page.off('download',download);context.off('page',onPage);context.off('response',onResponse);
  for(const external of opened){external.off('download',download);if(!external.isClosed())await external.close()}
 }
}
module.exports={openPrimary};
