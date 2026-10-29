// tested-by.js — "Tested by": the results of other experiments that bear on a result's claim.
//
// A result panel that reports a positive claim (an observation, evidence, an anomaly, or any result
// that states a significance) must not stand alone when other experiments have looked for the same
// thing: DAMA/LIBRA's modulation at 11.8 and 13.7 sigma reads as settled on its own, and ANAIS-112,
// COSINE-100, COSINUS and others have tested it. This lists, from the records only:
//
//   * the results of the experiments that carry a `complementary` lineage row to the result's own
//     experiment (a curated relation in the experiment records; the build writes it both ways), and
//   * the results, by any other experiment, whose own text (name, title, plain summary, the claim
//     quoted from the paper) names the result's experiment by its name or an alias.
//
// Nothing here says whether a listed result confirms or contradicts the claim: that is for the
// reader of the result. A result of the same experiment or of the same collaboration is never
// listed (DAMA/NaI is DAMA's own), nor is a technology milestone (a design report, a plan for a first
// run: it tests nothing yet). Pure: no DOM, no fetch.

/** Whether the result states a claim that others can test. */
export function statesClaim(result) {
  return Boolean(result && (result.significance || ['observation', 'evidence', 'anomaly'].includes(result.result_type)));
}

const escapeRegExp = (text) => text.replace(/[.*+?^${}()|[\]\\/]/g, '\\$&');

/** The names under which other records cite an experiment: its name, its aliases, and the words of its
 * name that are acronyms (DAMA/LIBRA -> DAMA, LIBRA). Case-sensitive on purpose: "libra" in
 * "calibration" is not the experiment. */
export function citationNames(experiment) {
  const names = new Set();
  for (const name of [experiment.name, ...(experiment.aliases || [])]) {
    if (!name) continue;
    names.add(name);
    for (const part of String(name).split(/[/\s]+/)) if (part.length >= 4 && /^[A-Z0-9][A-Za-z0-9-]*$/.test(part) && part === part.toUpperCase()) names.add(part);
  }
  return [...names].filter((name) => name.length >= 4);
}

function citesAny(blob, names) {
  return names.some((name) => new RegExp(`(?<![A-Za-z0-9])${escapeRegExp(name)}(?![A-Za-z0-9])`).test(blob));
}

const textOf = (result, text) => [
  result.name, result.title, result.summary && result.summary.plain,
  text && text[result.id] && text[result.id].claim && text[result.id].claim.quote,
].filter(Boolean).join(' \n ');

/**
 * `{ items, experiments }` or null. `items` are `{ result, experimentIds, cites }` (cites: the result's own
 * text names the experiment), the ones that cite first, then by date, newest first; `experiments` are the
 * other experiments whose results are listed, in the order they first appear.
 */
export function testedBy(result, { atlas, resultList, text }) {
  if (!statesClaim(result)) return null;
  const own = (result.experiment_ids || []).filter((id) => typeof id === 'string');
  const experiments = own.map((id) => (atlas.experiments || {})[id]).filter(Boolean);
  const complementary = new Set(experiments.flatMap((e) => (e.lineage || [])
    .filter((row) => row.relation === 'complementary').map((row) => row.experiment_id)));
  if (!complementary.size) return null;
  const names = experiments.flatMap(citationNames);
  const collaborations = new Set(result.collaboration_ids || []);
  const items = [];
  for (const other of resultList) {
    if (other.id === result.id) continue;
    // A design report, a facility's completion or a plan is not a test of anything.
    if (other.result_type === 'technology_milestone') continue;
    const otherExperiments = (other.experiment_ids || []).filter((id) => typeof id === 'string');
    if (otherExperiments.some((id) => own.includes(id))) continue;
    if ((other.collaboration_ids || []).some((id) => collaborations.has(id))) continue;
    const complements = otherExperiments.some((id) => complementary.has(id));
    const cites = citesAny(textOf(other, text), names);
    if (complements || cites) items.push({ result: other, experimentIds: otherExperiments, cites });
  }
  if (!items.length) return null;
  const when = (item) => String(item.result.date || '');
  items.sort((a, b) => (Number(b.cites) - Number(a.cites)) || (when(b) < when(a) ? -1 : when(b) > when(a) ? 1 : 0)
    || (a.result.id < b.result.id ? -1 : 1));
  const seen = [];
  for (const item of items) for (const id of item.experimentIds) if (!seen.includes(id)) seen.push(id);
  return { items, experiments: seen };
}
