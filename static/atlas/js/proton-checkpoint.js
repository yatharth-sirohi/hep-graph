// One prediction inside Follow the proton; the existing player owns every map step.
function h(tag, attrs={}, children=[]) {
  const node=document.createElement(tag);
  for(const [key,value] of Object.entries(attrs))if(value!=null)node.setAttribute(key,value);
  for(const child of [].concat(children))if(child!=null)node.append(child instanceof Node?child:document.createTextNode(String(child)));
  return node;
}

export function createDependencyCheckpoint({exercise,trace,pause,initialOpen=false}) {
  const root=h('details',{class:'pr-checkpoint',id:'pr-beam-question'});
  root.open=initialOpen;
  const feedback=h('p',{class:'pr-beam-feedback',id:'pr-beam-feedback',role:'status','aria-live':'polite'});
  const answer=h('div',{id:'pr-beam-answer',hidden:''});
  const test=h('button',{type:'button',class:'pr-btn pr-predict-test','aria-controls':'pr-beam-answer','aria-expanded':'false',disabled:''},'Test prediction on the map');
  let guess=null;
  const options=[...exercise.branches.map(b=>({id:b.id,label:b.label})),{id:'both',label:'Both beams'}];
  const choices=h('fieldset',{class:'pr-beam-choices','aria-describedby':'pr-beam-prompt'},[
    h('legend',{},'Which beam loses its listed proton source?'),
    ...options.map(option=>{
      const input=h('input',{type:'radio',name:'pr-beam-prediction',value:option.id});
      input.addEventListener('change',()=>{
        pause();guess=option.id;test.disabled=false;answer.hidden=true;feedback.textContent='';test.setAttribute('aria-expanded','false');
      });
      return h('label',{},[input,h('span',{},option.label)]);
    }),
  ]);
  const traces=h('div',{class:'pr-beam-traces'},exercise.branches.map(branch=>{
    const button=h('button',{type:'button',class:'pr-btn','data-trace-beam':branch.id},`Trace ${branch.label}`);
    button.addEventListener('click',()=>{pause();trace(branch.traceStep)});
    return button;
  }));
  answer.append(
    h('p',{},'NuMI receives its protons from Main Injector. The Booster Neutrino Beam receives its protons directly from Booster. Sharing upstream machines does not put Main Injector in the BNB proton path.'),
    h('p',{class:'pr-beam-limit'},'This tests a necessary connection. It does not establish beam delivery, rates, or current operation; other components are assumed available.'),
    traces,
    h('ul',{class:'pr-beam-citations'},exercise.branches.map(branch=>h('li',{},
      h('a',{href:branch.evidence.url,target:'_blank',rel:'noopener','data-branch-source':branch.id},branch.evidence.locator)))),
  );
  test.addEventListener('click',()=>{
    if(!guess)return;
    pause();answer.hidden=false;test.setAttribute('aria-expanded','true');
    feedback.textContent=guess===exercise.answerId?'Your prediction matches these connections: NuMI needs Main Injector.'
      :'NuMI is the affected branch. Compare its proton source with the Booster beam’s source below.';
    trace(exercise.branches.find(branch=>branch.id===exercise.answerId).traceStep);
    feedback.scrollIntoView({block:'nearest',behavior:'auto'});
  });
  const summary=h('summary',{},'Predict which beam needs Main Injector');
  summary.addEventListener('click',pause);
  root.append(summary,
    h('p',{class:'pr-beam-prompt',id:'pr-beam-prompt'},`Use the ${exercise.year} connections. Suppose Main Injector cannot deliver protons while other components are available. Compare NuMI with the Booster Neutrino Beam (BNB).`),
    choices,test,feedback,answer);
  // Native radio keys and activation belong to the checkpoint, not map/tour shortcuts.
  root.addEventListener('keydown',event=>{
    if(event.key!=='Escape' && event.target.closest('input,button,summary,a'))event.stopPropagation();
  });
  return root;
}
