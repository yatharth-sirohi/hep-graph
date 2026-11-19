import { evidenceFor } from './result-evidence-data.js';
function h(tag, attrs={}, children=[]) {
  const node=document.createElement(tag);
  for(const [key,value] of Object.entries(attrs)) node.setAttribute(key,value);
  for(const child of [].concat(children)) if(child!=null) node.append(child instanceof Node?child:document.createTextNode(child));
  return node;
}
/** Optional display: curated measurement → interpretation → exact primary location.
 * Shared across Results; records without a reviewed trail keep their existing panel. */
export function renderEvidenceTrail(resultId, linkTo) {
  const e=evidenceFor(resultId);
  if(!e) return null;
  return h('section',{class:'result-evidence','aria-label':`${e.experiment} evidence trail`},[
    h('h3',{},'Read the evidence'),
    h('p',{class:'source-meta'},`Primary paper: ${e.paper}. These are the paper’s findings, following the 4 July announcement.`),
    h('h4',{},'What was measured'),h('p',{},e.measurement),h('p',{},e.mass),
    h('h4',{},e.significance.scope),
    h('dl',{class:'evidence-significance'},[
      h('div',{},[h('dt',{},'Observed in the data'),h('dd',{},e.significance.observed)]),
      h('div',{},[h('dt',{},'Expected with a Standard Model Higgs signal'),h('dd',{},e.significance.expected)]),
    ]),
    h('p',{},e.significance.at),
    h('p',{},'Observed significance measures how incompatible the data are with a background-only model at one tested mass, expressed as an equivalent one-sided Gaussian tail. Expected significance is the median sensitivity assuming a Standard Model Higgs signal; it is not another observation.'),
    h('p',{},'Neither is the probability that the Higgs exists. A global significance also accounts for searching over many masses; it depends on the search window.'),
    h('details',{},[h('summary',{},'Read the statistical definition in the paper'),
      h('a',{class:'evidence-source',href:'https://arxiv.org/pdf/1207.7235v1#page=8',target:'_blank',rel:'noopener'},'CMS §4, printed p. 6 (PDF page 8): local and global p-values')]),
    h('p',{class:'evidence-caveat'},e.significance.note),
    h('h4',{},'Follow the claim to the paper'),
    h('ol',{class:'evidence-items'},e.evidence.map(item=>h('li',{},[
      h('a',{class:'evidence-source',href:item.url,target:'_blank',rel:'noopener'},item.label),
      h('p',{class:'source-meta'},item.locator),h('p',{},item.supports),
    ]))),
    h('p',{class:'evidence-caveat'},'ATLAS and CMS are separate analyses. No joint significance is calculated here. The papers established a new boson compatible with the Higgs; further property measurements followed.'),
    linkTo({type:'result',slug:e.companion.slug},e.companion.label),
  ]);
}
