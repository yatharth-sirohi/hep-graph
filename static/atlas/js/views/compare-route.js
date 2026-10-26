// compare-route.js — the route of "Compare experiments" and its search entry: the few
// lines registry.js, the compare tray and the unit check need without loading the view.
// Pure data over atlas.json (no DOM, no fetch). The table itself is compare-rows.js and
// compare.js, which load only when the route is opened.
//
//   #/view/compare/dune,hyper-kamiokande,juno      two to four experiment slugs

export const VIEW_NAME = 'compare';
// The owner names features; this is the working title, the only place it is written.
export const WORKING_TITLE = 'Compare experiments';
export const MAX_EXPERIMENTS = 4;
export const MIN_EXPERIMENTS = 2;

/** Two comparisons the empty page offers, as slugs of experiments the Atlas holds. */
export const EXAMPLES = [
  { label: 'Three neutrino detectors', slugs: ['dune', 'hyper-kamiokande', 'juno'] },
  { label: 'Three liquid-xenon dark-matter detectors', slugs: ['lz', 'xenonnt', 'pandax-4t'] },
];

const SLUG = /^[a-z0-9][a-z0-9-]*$/;

/** `{ slugs, invalid }` from a route argument: the comma-separated slugs, once each, in order. */
export function parseArg(arg) {
  const slugs = [];
  const invalid = [];
  for (const part of String(arg || '').split(',').map((p) => p.trim()).filter(Boolean)) {
    if (!SLUG.test(part)) {
      if (!invalid.includes(part)) invalid.push(part);
    } else if (!slugs.includes(part)) {
      slugs.push(part);
    }
  }
  return { slugs, invalid };
}

/**
 * The experiments a route argument names: `experiments` (at most four, in the order
 * given), `unknown` (named, but not in the Atlas) and `extra` (a fifth and later).
 * Nothing is dropped without being reported.
 */
export function resolveArg(atlas, arg) {
  const { slugs, invalid } = parseArg(arg);
  const known = [];
  const unknown = [...invalid];
  for (const slug of slugs) {
    const record = (atlas.experiments || {})[`experiment:${slug}`];
    if (record) known.push(record); else unknown.push(slug);
  }
  return { experiments: known.slice(0, MAX_EXPERIMENTS), unknown, extra: known.slice(MAX_EXPERIMENTS) };
}

export function compareHash(slugs) {
  return `#/view/${VIEW_NAME}/${slugs.join(',')}`;
}

/** The route of a comparison, as navigate() takes it. */
export function compareRoute(slugs) {
  return { type: 'view', slug: `${VIEW_NAME}/${slugs.join(',')}` };
}

/** Search rows: the page itself, reachable by "compare", "side by side", "versus". */
export function compareSearchEntries() {
  return [{
    type: 'view',
    id: `view:${VIEW_NAME}/`,
    name: WORKING_TITLE,
    aliases: ['compare', 'comparison', 'compare experiments', 'side by side', 'versus', 'vs', 'experiment comparison'],
    subtitle: 'Two to four experiments side by side · CSV with citations',
  }];
}
