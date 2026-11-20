// Reviewed connection pilot for the existing map player. Answer/steps use its data.
export const DEPENDENCY_ENTRY = Object.freeze({map:'fermilab',year:2016,proton:7});
const FACILITY = 'facility:fermilab';
const BLOCKED = 'accelerator:fermilab-main-injector';
const BEAMS = [
  {id:'beamline:numi',source:BLOCKED,label:'NuMI',evidence:{
    sourceId:'src:fermilab-numi-beam-paper-2016',url:'https://arxiv.org/pdf/1507.06690v2#page=6',
    locator:'NuMI beam paper, §2 opening paragraph, PDF page 6: protons extracted from Main Injector'}},
  {id:'beamline:bnb',source:'accelerator:fermilab-booster',label:'Booster Neutrino Beam',evidence:{
    sourceId:'src:fermilab-miniboone-flux-paper-2009',url:'https://arxiv.org/pdf/0806.1449v2#page=2',
    locator:'MiniBooNE flux paper, abstract, PDF page 2: Booster delivers the protons'}},
];

export function beamDependencyAvailable(atlas) {
  return atlas?.maps?.['map:fermilab']?.facility_id === FACILITY
    && BEAMS.every(b=>atlas.beamlines?.[b.id]?.accelerator_id === b.source && atlas.accelerators?.[b.source]);
}

export function beamDependencyExercise(chain) {
  if (chain?.facilityId !== FACILITY || chain.species !== 'proton') return null;
  const stages = new Map((chain.stages || []).map(stage=>[stage.id,stage]));
  const blocked = stages.get(BLOCKED);
  if (!blocked?.drawn) return null;
  const branches = [];
  for (const reviewed of BEAMS) {
    const beam = stages.get(reviewed.id);
    const source = stages.get(beam?.record.accelerator_id);
    // A changed feeder must be reviewed against the cited passage before reuse.
    if (!beam?.drawn || !source?.drawn || source.id !== reviewed.source || beam.feederId !== source.id) return null;
    const traceStep = (chain.steps || []).findIndex(s=>s.kind==='transfer' && s.from.id===source.id && s.to.id===beam.id)+1;
    if (!traceStep) return null;
    branches.push({id:beam.id,label:reviewed.label,sourceId:source.id,sourceName:source.record.name,traceStep,evidence:reviewed.evidence});
  }
  const affected = branches.filter(branch=>branch.sourceId===blocked.id);
  if (affected.length !== 1) return null;
  return {key:[chain.year,...branches.map(b=>`${b.id}:${b.sourceId}:${b.traceStep}`)].join('|'),year:chain.year,
    blocked:{id:blocked.id,name:blocked.record.name},branches,answerId:affected[0].id};
}
