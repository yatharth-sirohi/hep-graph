// A worked reading of two points on the existing plot, with their own definitions.
import {h} from './chart.js';
import {claimItem} from './chart-inputs.js';
import {fluxText,sciText} from './underground-rows.js';
import {compareFluxes,defaultFluxPair,normaliseFluxPair} from './underground-compare.js';

export function createFluxComparison({entries,prov,loader,link,navigate,onHighlights,initialPair}) {
  const rows=entries.map(entry=>entry.row);
  const root=h('section',{class:'ch-block ug-compare',id:'ug-compare','aria-labelledby':'ug-compare-heading'});
  const fallback=defaultFluxPair(rows);
  if(!fallback){
    root.append(h('h3',{id:'ug-compare-heading'},'Compare two plotted fluxes'),h('p',{},'This build needs two plotted sites for a comparison.'));
    return {element:root,update(){},exportNotes(){return []},destroy(){}};
  }
  let destroyed=false,ticket=0,comparison=null,stateKey;
  const error=h('p',{class:'ug-compare-error',id:'ug-compare-error',role:'alert',hidden:''});
  const result=h('p',{class:'ug-compare-result',id:'ug-compare-result',role:'status','aria-live':'polite'});
  const math=h('p',{id:'ug-compare-math'});
  const values=h('div',{class:'ug-compare-values',id:'ug-compare-values'});
  const sourceBody=h('div',{id:'ug-compare-source-body','data-state':'idle'});
  const sourceSummary=h('summary',{},'Definitions and primary sources for A and B');
  const sources=h('details',{id:'ug-compare-sources'},[sourceSummary,sourceBody]);
  const selects=['A','B'].map(letter=>h('select',{id:`ug-flux-${letter.toLowerCase()}`,'aria-describedby':'ug-compare-instructions'},[
    h('option',{value:'',disabled:''},'Choose a plotted site'),
    ...entries.map(entry=>h('option',{value:entry.row.slug},`${entry.row.label}${entry.hollow?' (approximate or simulated)':''}`)),
  ]));
  const controls=h('div',{class:'ug-compare-controls'},selects.map((select,i)=>h('label',{},[`${['A','B'][i]} — site`,select])));
  root.append(h('h3',{id:'ug-compare-heading'},'Compare two plotted fluxes'),
    h('p',{id:'ug-compare-instructions'},'Choose A and B, then find their labelled outlines on the chart. Compare both fluxes in the same unit before reading their separation on the logarithmic axis.'),
    controls,error,result,math,values,
    h('p',{id:'ug-compare-limit',class:'ch-note'},'This compares reported central values; displayed results are rounded. It does not isolate the effect of depth: reference surfaces, angular cuts, thresholds and halls differ. Recorded uncertainties stay with their values; no uncertainty on this ratio is calculated.'),sources);

  async function fillSources() {
    const snapshot=comparison,run=++ticket;
    if(!snapshot)return;
    sourceBody.dataset.state='loading';sourceBody.replaceChildren(h('p',{role:'status'},'Loading the selected definitions and sources…'));
    try{
      const loaded=await loader.getSources();
      if(destroyed||run!==ticket||!root.isConnected)return;
      sourceBody.replaceChildren(...[snapshot.a,snapshot.b].map((row,i)=>{
        const claim=claimItem(prov,loaded,row.site,'/muon_flux');
        return h('article',{},[h('h4',{},`${['A','B'][i]} · ${row.label}`),claim?h('ul',{class:'source-list'},claim):h('p',{},'No source is recorded for this flux.')]);
      }));
      sourceBody.dataset.state='ready';
    }catch(problem){
      if(destroyed||run!==ticket||!root.isConnected)return;
      const retry=h('button',{type:'button',class:'text-btn'},'Retry selected sources');
      retry.addEventListener('click',()=>{sourceSummary.focus();fillSources()});
      sourceBody.dataset.state='error';sourceBody.replaceChildren(h('p',{class:'error-note',role:'alert'},`Could not load the selected sources: ${problem.message}.`),retry);
    }
  }
  sources.addEventListener('toggle',()=>{if(sources.open&&sourceBody.dataset.state==='idle')fillSources()});

  function render(pair) {
    ++ticket;
    selects.forEach((select,i)=>{select.value=rows.some(row=>row.slug===pair[i])?pair[i]:''});
    comparison=compareFluxes(rows,pair);
    error.hidden=!!comparison;result.hidden=math.hidden=values.hidden=sources.hidden=!comparison;
    sourceBody.dataset.state='idle';sourceBody.replaceChildren(h('p',{},'Open this section to load the two selected flux definitions and their sources.'));
    if(!comparison){
      const missing=pair.some(slug=>!rows.some(row=>row.slug===slug));
      error.textContent=missing?'A saved or selected site is not plotted in this Atlas build. Choose two plotted sites.':'Choose two different plotted sites to compare their fluxes.';
      result.textContent='';math.textContent='';values.replaceChildren();onHighlights([]);return;
    }
    error.textContent='';
    const {a,b,ratio,logRatio,decades}=comparison;
    const factor=Number(Math.max(ratio,1/ratio).toPrecision(3)).toLocaleString('en-US',{maximumSignificantDigits:3});
    const higher=ratio>=1?a:b,lower=ratio>=1?b:a;
    result.textContent=ratio===1?`${a.label} and ${b.label} have the same recorded central flux.`
      :`${higher.label} has about ${factor} times the recorded central muon flux of ${lower.label}.`;
    math.textContent=`A ÷ B = (${fluxText(a.flux)}) ÷ (${fluxText(b.flux)}) = ${sciText(ratio)} (dimensionless). log₁₀(A ÷ B) = ${logRatio>0?'+':''}${logRatio.toFixed(2)}. Their vertical separation is ${decades.toFixed(2)} decades; one decade is a factor of 10.`;
    values.replaceChildren(...[a,b].map((row,i)=>{
      const entry=entries.find(item=>item.row.id===row.id);
      const conversion=row.fluxQuantity.unit==='m^-2 s^-1'?' ÷ 10,000':row.fluxQuantity.unit==='m^-2 d^-1'?' ÷ 10,000 ÷ 86,400':null;
      return h('article',{},[h('h4',{},`${['A','B'][i]} · ${row.label}`),h('p',{},`Recorded: ${row.fluxQuantity.display}`),
        conversion?h('p',{class:'ug-unit-conversion'},`Unit conversion: ${sciText(row.fluxQuantity.value,6)}${conversion} = ${fluxText(row.flux)}. 1 m² = 10,000 cm²; 1 day = 86,400 s.`):null,
        h('p',{},`Plotted: ${fluxText(row.flux)}. ${entry.hollow?'Approximate or simulated (hollow marker).':'Measured (filled marker).'}`),
        link({type:'site',slug:row.slug},`Open ${row.label}`)]);
    }));
    onHighlights([{id:a.id,label:'A'},{id:b.id,label:'B'}]);
    if(sources.open)fillSources();
  }
  function update(pair) {
    const key=JSON.stringify(pair||null);
    if(key===stateKey)return;
    stateKey=key;render(normaliseFluxPair(pair)||fallback);
  }
  selects.forEach(select=>select.addEventListener('change',()=>{
    const pair=selects.map(item=>item.value);
    if(normaliseFluxPair(pair))navigate({undergroundPair:pair});else render(pair);
  }));
  // Native controls get their own keys; the presenter may first dismiss its blank screen.
  root.addEventListener('keydown',event=>{
    const blank=document.getElementById('tour-blank');
    if(event.key!=='Escape'&&event.target.closest('select,summary,button,a')&&(!blank||blank.hidden))event.stopPropagation();
  });
  function exportNotes() {
    if(destroyed||!comparison)return [];
    const {a,b,ratio,logRatio,decades}=comparison;
    const address=new URL(window.location.href);address.searchParams.set('uf',[a.slug,b.slug].join(','));
    return [
      ...[a,b].map((row,i)=>`${['A','B'][i]}: ${row.label}; recorded ${row.fluxQuantity.display}; plotted ${fluxText(row.flux)}.`),
      `Central-value comparison: A/B = ${sciText(ratio)}; log10(A/B) = ${logRatio.toFixed(2)}; vertical separation ${decades.toFixed(2)} decades.`,
      root.querySelector('#ug-compare-limit').textContent,
      `Reopen this comparison and its measurement definitions/sources: ${address.href}`,
    ];
  }
  update(initialPair);
  return {element:root,update,exportNotes,destroy(){destroyed=true;++ticket}};
}
