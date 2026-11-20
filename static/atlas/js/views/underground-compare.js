// Common-unit central-value comparisons for the existing underground chart.
export function normaliseFluxPair(value) {
  const pair=typeof value==='string'?value.split(','):value;
  return Array.isArray(pair)&&pair.length===2&&pair.every(slug=>typeof slug==='string'&&/^[a-z0-9][a-z0-9-]{0,100}$/.test(slug))?[...pair]:null;
}

const usable=row=>row&&typeof row.slug==='string'&&Number.isFinite(row.flux)&&row.flux>0;

export function defaultFluxPair(rows) {
  const valid=rows.filter(usable);
  const preferred=['lngs-hall-c','snolab-underground-lab'];
  if(preferred.every(slug=>valid.some(row=>row.slug===slug)))return preferred;
  return valid.length>=2?[valid[0].slug,valid[valid.length-1].slug]:null;
}

export function compareFluxes(rows,value) {
  const pair=normaliseFluxPair(value);
  if(!pair||pair[0]===pair[1])return null;
  const [a,b]=pair.map(slug=>rows.find(row=>row.slug===slug));
  if(!usable(a)||!usable(b))return null;
  const ratio=a.flux/b.flux;
  if(!Number.isFinite(ratio)||ratio<=0)return null;
  const logRatio=Math.log10(ratio);
  return {a,b,ratio,logRatio,decades:Math.abs(logRatio)};
}
