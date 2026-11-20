// A passed schedule is not evidence that a last-reported shutdown ended.
const observed = new Set(['construction','commissioning','active','shutdown','upgrade','completed','decommissioned','cancelled']);
function bound(value, upper) {
  const raw = typeof value === 'object' && value ? value[upper ? 'latest' : 'earliest'] || value.date : value;
  if (typeof raw !== 'string') return null;
  const match = /^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?$/.exec(raw);
  if (!match) return null;
  if (match[3]) return raw;
  if (!match[2]) return `${raw}-${upper ? '12-31' : '01-01'}`;
  if (!upper) return `${raw}-01`;
  const last = new Date(Date.UTC(Number(match[1]), Number(match[2]), 0)).getUTCDate();
  return `${raw}-${String(last).padStart(2,'0')}`;
}

export function unconfirmedRestart(record, buildDate, timeline = {}) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(buildDate || '')) return null;
  const rows = record?.intervals || [];
  const states = rows.map((row,index)=>({row,index,first:bound(row.start,false)})).filter(({row,first})=>
    (row.kind || 'lifecycle') === 'lifecycle' && observed.has(row.status) && !row.start?.planned && first && first <= buildDate);
  states.sort((a,b)=>b.first.localeCompare(a.first) || b.index-a.index);
  const state = states[0];
  if (!state || state.row.status !== 'shutdown' || state.row.end != null) return null;
  const plans = rows.map((row,index)=>({row,index,first:bound(row.start,false),last:bound(row.start,true)})).filter(({row,first,last})=>
    row.kind === 'run' && row.status === 'planned' && row.start?.planned && first && last && first > state.first && last < buildDate);
  plans.sort((a,b)=>b.first.localeCompare(a.first));
  const plan = plans[0];
  if (!plan) return null;
  const selectedEnd = timeline.range?.[1] ?? timeline.year ?? Number(buildDate.slice(0,4));
  if (Number(selectedEnd) < Number(plan.first.slice(0,4))) return null;
  return {stateIndex:state.index,planIndex:plan.index,start:plan.row.start};
}
