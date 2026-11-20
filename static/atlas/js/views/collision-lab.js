// A derived comparison beside the historical energy chart; no machine point is converted.
import { h } from './chart.js';
import { patchQuietly } from '../state.js';
import { COLLISION_ENERGY as RANGE, COLLISION_MODEL as MODEL, collisionEnergies, normaliseCollisionEnergy, quadrupleExperiment } from './collision-model.js';
const fmt=value=>Number(value.toPrecision(4)).toLocaleString('en-US',{maximumSignificantDigits:4});
const inputText=value=>value.toLocaleString('en-US',{maximumFractionDigits:1});
const svgNode=(tag,attrs={},value='')=>{const n=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,v);if(value)n.textContent=value;return n};
const source=(url,text)=>h('a',{href:url,target:'_blank',rel:'noopener'},text);

export function createCollisionLab(ctx) {
  let energy=normaliseCollisionEnergy(ctx.collisionEnergyGeV),destroyed=false;
  const root=h('section',{class:'ch-block collision-lab','aria-labelledby':'collision-title'});
  const input=h('input',{id:'collision-energy',type:'number',min:RANGE.min,max:RANGE.max,step:RANGE.step,inputmode:'decimal','aria-describedby':'collision-control-help collision-input-error collision-readout'});
  const reset=h('button',{type:'button',id:'collision-reset',class:'text-btn'},'Reset to 450 GeV');
  const error=h('p',{id:'collision-input-error',role:'alert',hidden:''});
  const fixed=h('strong',{id:'collision-fixed'}),headOn=h('strong',{id:'collision-head-on'});
  const readout=h('output',{id:'collision-readout',for:'collision-energy','aria-live':'polite','aria-atomic':'true'});
  const plot=h('div',{class:'collision-plot'});
  const test=h('button',{type:'button',id:'collision-test',class:'text-btn','aria-controls':'collision-answer','aria-expanded':'false'},'Test ×4 on the comparison');
  const limit=h('p',{id:'collision-test-limit',class:'ch-note'});
  const answer=h('p',{id:'collision-answer',role:'status','aria-live':'polite',hidden:''});
  const prediction=h('details',{class:'collision-prediction'},[
    h('summary',{},'Predict: what if each beam energy quadruples?'),
    h('p',{},'At your current E, predict how the two centre-of-mass energies will change. Does each quadruple, double, or do something else? Then test the exact formulas.'),test,limit,answer,
  ]);
  const method=h('details',{id:'collision-method'},[
    h('summary',{},'Formula, assumptions and primary sources'),
    h('p',{class:'collision-formula'},'μ = mₚc² = 0.938272 GeV (rounded). E includes rest energy; it is not kinetic energy.'),
    h('p',{class:'collision-formula'},'Fixed proton target: √s = √(2μ² + 2μE). Equal head-on proton beams: √s = 2E.'),
    h('p',{},'These follow from the total energy–momentum invariant in PDG §49.2, Eqs. 49.2–49.3. Opposite equal momenta cancel in the head-on case. A fixed-target system keeps net momentum, so its centre of mass moves in the laboratory (Eqs. 49.4–49.5). Energy is not lost.'),
    h('p',{},'At E much greater than μ, fixed-target √s ≈ √(2μE), so quadrupling E gives approximately twice √s. The exact rest term is retained here, including near the lower end of the control.'),
    h('p',{},'This is the total initial proton-system centre-of-mass energy. It does not calculate a quark/gluon hard-scattering energy, a cross section or a discovery reach. No uncertainty band is calculated; values are rounded to four significant figures.'),
    h('p',{class:'collision-sources'},[source(MODEL.kinematicsURL,'PDG 2024 Kinematics · §49.2, Eqs. 49.2–49.5, PDF p.1'),' · ',source(MODEL.restEnergyURL,'PDG 2024 Physical Constants · Table 1.1, proton mass, PDF p.1')]),
  ]);
  root.append(h('h3',{id:'collision-title'},'Compare collision energies'),
    h('p',{},'Explore ideal proton–proton kinematics. Compare the same total energy per moving proton: one proton strikes a stationary proton, or two equal proton beams meet exactly head-on.'),
    h('p',{class:'ch-note'},'The head-on case uses two accelerated beams. This is not an equal total beam-energy budget. The illustrative input does not convert or change any machine point above.'),
    h('label',{for:'collision-energy'},'Total beam energy E (GeV)'),input,
    h('p',{id:'collision-control-help',class:'ch-note'},'Per moving proton, including rest energy. Range 1–10,000 GeV in 0.1 GeV steps. Use the number box or its arrow keys.'),
    error,readout,plot,
    h('p',{class:'ch-caption'},'Derived √s on one linear scale, from zero to 2E. Outline: fixed proton target; filled bar: equal head-on beams.'),
    reset,prediction,method);

  function figure(width,fontSize=14,prefix='collision-plot') {
    const values=collisionEnergies(energy),scale=fontSize/14,height=190*scale,left=16*scale,right=width-16*scale;
    const x=value=>left+(right-left)*value/values.headOnGeV;
    const svg=svgNode('svg',{width,height,viewBox:`0 0 ${width} ${height}`,role:'img','aria-labelledby':`${prefix}-title ${prefix}-desc`});
    svg.append(svgNode('title',{id:`${prefix}-title`},'Derived proton collision energies'),svgNode('desc',{id:`${prefix}-desc`},`Total energy ${energy} GeV per moving proton. Fixed target: ${fmt(values.fixedTargetGeV)} GeV, outlined. Equal head-on beams: ${fmt(values.headOnGeV)} GeV, filled. The common linear scale ends at ${fmt(values.headOnGeV)} GeV.`));
    const text=(px,y,value,anchor='start')=>svgNode('text',{x:px,y:y*scale,'text-anchor':anchor,style:`font-size:${fontSize}px`},value);
    svg.append(text(left,20,`Fixed target · ${fmt(values.fixedTargetGeV)} GeV`),
      svgNode('rect',{x:left,y:32*scale,width:x(values.fixedTargetGeV)-left,height:14*scale,class:'collision-fixed-bar'}),
      text(left,78,`Head-on beams · ${fmt(values.headOnGeV)} GeV`),
      svgNode('rect',{x:left,y:90*scale,width:right-left,height:14*scale,class:'collision-headon-bar'}),
      svgNode('line',{x1:left,x2:right,y1:130*scale,y2:130*scale,class:'collision-axis'}));
    for(const [value,anchor]of [[0,'start'],[energy,'middle'],[2*energy,'end']]){
      svg.append(svgNode('line',{x1:x(value),x2:x(value),y1:130*scale,y2:136*scale,class:'collision-axis'}),text(x(value),153,fmt(value),anchor));
    }
    svg.append(text((left+right)/2,178,'Derived √s (GeV)','middle'));return svg;
  }
  function draw(){if(!destroyed)plot.replaceChildren(figure(Math.max(260,Math.round(plot.getBoundingClientRect().width||800))))}
  function clearAnswer(){answer.hidden=true;answer.textContent='';test.setAttribute('aria-expanded','false')}
  function clearError(){error.hidden=true;error.textContent='';input.removeAttribute('aria-invalid')}
  function render(){
    input.value=String(energy);const values=collisionEnergies(energy);
    fixed.textContent=`${fmt(values.fixedTargetGeV)} GeV`;headOn.textContent=`${fmt(values.headOnGeV)} GeV`;
    readout.replaceChildren(`Accepted E = ${energy} GeV per moving proton. Fixed target: `,fixed,'; equal head-on beams: ',headOn,'.');
    const supported=energy<=RANGE.max/4;test.disabled=!supported;
    limit.textContent=supported?`Test E = ${energy} → ${4*energy} GeV.`:`For ×4, choose E at or below 2,500 GeV. Your current E would need ${inputText(4*energy)} GeV, outside this lab’s range.`;
    draw();
  }
  function accept(value,{write=true,keepAnswer=false}={}){
    energy=normaliseCollisionEnergy(value);clearError();if(!keepAnswer)clearAnswer();render();
    if(write)patchQuietly({collisionEnergy:energy});ctx.host.exportChanged?.();
  }
  input.addEventListener('change',()=>{
    if(input.value.trim()===''||!input.checkValidity()){
      input.setAttribute('aria-invalid','true');error.textContent='Enter a total energy from 1 to 10,000 GeV in 0.1 GeV steps. The comparison and link still use the last accepted energy shown below.';error.hidden=false;return;
    }
    accept(Number(input.value));
  });
  reset.addEventListener('click',()=>accept(RANGE.default));
  test.addEventListener('click',()=>{
    const run=quadrupleExperiment(energy);if(!run)return;
    accept(run.end.beamEnergyGeV,{keepAnswer:true});
    answer.textContent=`E = ${run.start.beamEnergyGeV} → ${run.end.beamEnergyGeV} GeV. Fixed-target √s: ${fmt(run.start.fixedTargetGeV)} → ${fmt(run.end.fixedTargetGeV)} GeV (×${run.fixedFactor.toFixed(2)}). Head-on √s: ${fmt(run.start.headOnGeV)} → ${fmt(run.end.headOnGeV)} GeV (×${run.headOnFactor.toFixed(2)}). The square-root approximation applies at high E; these results use the exact rest term.`;
    answer.hidden=false;test.setAttribute('aria-expanded','true');
  });
  root.addEventListener('keydown',event=>{const blank=document.getElementById('tour-blank');if(event.key!=='Escape'&&event.target.closest('input,button,summary,a')&&(!blank||blank.hidden))event.stopPropagation()});
  const observer=new ResizeObserver(draw);observer.observe(plot);render();requestAnimationFrame(draw);

  function exportFigure(){
    if(destroyed)return null;
    const values=collisionEnergies(energy),holder=h('div',{class:'collision-lab collision-export-stage','aria-hidden':'true'});
    Object.assign(holder.style,{position:'fixed',left:'-10000px',top:'0',width:'800px',pointerEvents:'none'});
    const image=svgNode('svg',{width:800,height:340,viewBox:'0 0 800 340'});
    const text=(y,value,size=18)=>svgNode('text',{x:16,y,style:`font-size:${size}px`},value);
    image.append(text(24,'Ideal proton–proton collision energies',22),text(49,`E = ${energy} GeV per moving proton; head-on uses two accelerated beams.`),text(72,'Total initial-system √s; no parton energy, cross section or discovery reach calculated.',14));
    const bars=figure(800,18,'collision-export');bars.setAttribute('y','84');image.append(bars);holder.append(image);document.body.append(holder);
    const url=new URL(location.href);url.searchParams.set('ce',String(energy));
    return {figures:[image],layout:'column',notes:[
      'Ideal proton–proton kinematics. Same total energy per moving proton; head-on uses two accelerated beams, not equal total beam-energy cost.',
      `E = ${energy} GeV (including rest energy). Fixed-target √s = ${fmt(values.fixedTargetGeV)} GeV; equal head-on √s = ${fmt(values.headOnGeV)} GeV.`,
      'μ = mₚc² = 0.938272 GeV (rounded). Fixed target: √s = √(2μ² + 2μE); equal head-on beams: √s = 2E. Outputs rounded to four significant figures.',
      'No quark/gluon hard-scattering energy, cross section, discovery reach or uncertainty band calculated. Historical machine points are not converted.',
      `PDG 2024 §49.2, Eqs. 49.2–49.5, PDF p.1: ${MODEL.kinematicsURL}`,
      `PDG 2024 Table 1.1 proton mass, PDF p.1: ${MODEL.restEnergyURL}`,
      `Reopen this comparison: ${url.href}`,
    ],release:()=>holder.remove()};
  }
  return {element:root,exportFigure,update(next){const value=normaliseCollisionEnergy(next.collisionEnergyGeV);if(value!==energy)accept(value,{write:false})},destroy(){destroyed=true;observer.disconnect()}};
}
