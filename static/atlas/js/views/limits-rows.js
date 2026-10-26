// limits-rows.js — the exclusion-plot view: which plots exist, which records link to
// them, and how a link, a search entry or a panel names the view. Pure (no DOM, no
// fetch), so panels.js and the search can use it without loading the view itself, and
// the unit check can read it under Node.
//
//   #/view/limits/<plot-slug>        e.g. #/view/limits/wimp-si
//
// The curves themselves are data (data/atlas/limits/*.json, A29), served lazily as
// limits/<plot>.json. This file only knows which records have something to show on
// which plot; tests/test_atlas_limits.py checks the table below against the data.

export const VIEW_NAME = 'limits';
// The owner names features; this is the working title, and the only place it is written
// (the heading, the panel links and the search entry all read it here).
export const WORKING_TITLE = 'WIMP exclusion plot';

export const PLOTS = {
  'wimp-si': {
    slug: 'wimp-si',
    // The plot's own heading (the bundle repeats it); the short name is the link text.
    name: 'Spin-independent WIMP–nucleon limits',
    topics: ['topic:dark-matter', 'topic:direct-dark-matter-detection'],
    experiments: ['experiment:lz', 'experiment:xenonnt', 'experiment:pandax-4t'],
    results: [
      'result:lz-first-wimp-search-2022',
      'result:lz-ws2024-wimp-search-2024',
      'result:xenonnt-first-nr-search-2023',
    ],
    hint: 'Published 90% CL limits of LZ, and the minimum of XENONnT and PandaX-4T · log–log, each curve cited',
    aliases: [
      'WIMP exclusion plot', 'WIMP-nucleon cross section limits', 'spin-independent WIMP limits',
      'dark matter limits', 'dark matter exclusion plot', 'direct detection limits',
      'direct detection exclusion plot', 'LZ limit', 'LZ WIMP limit', 'XENONnT limit',
      'PandaX-4T limit', 'cross section against WIMP mass',
    ],
  },
};

export function viewHash(arg) {
  return `#/view/${VIEW_NAME}/${arg}`;
}

/** The plot a route argument names, or null. */
export function plotFor(arg) {
  const slug = String(arg || '');
  return Object.prototype.hasOwnProperty.call(PLOTS, slug) ? PLOTS[slug] : null;
}

/** The link a record's panel offers (a topic, an experiment, a result): `{ slug, title, hint }`,
 * or null when no plot carries something of that record. */
export function limitsLinkForRecord(atlas, record) { // eslint-disable-line no-unused-vars
  if (!record || !record.id) return null;
  for (const plot of Object.values(PLOTS)) {
    if (plot.topics.includes(record.id) || plot.experiments.includes(record.id) || plot.results.includes(record.id)) {
      return { slug: `${VIEW_NAME}/${plot.slug}`, title: WORKING_TITLE, hint: plot.hint };
    }
  }
  return null;
}

/** Search rows of the view, the shape search.json rows take. */
export function limitsSearchEntries(atlas) { // eslint-disable-line no-unused-vars
  return Object.values(PLOTS).map((plot) => ({
    type: 'view',
    id: `view:${VIEW_NAME}/${plot.slug}`,
    name: `${WORKING_TITLE}: ${plot.name}`,
    aliases: plot.aliases,
    subtitle: 'Exclusion plot · published limits',
  }));
}

/** Where "Back" goes from a pasted link: the dark-matter topic. */
export function limitsParent(arg, atlas) {
  const topic = (atlas.topics || {})['topic:dark-matter'];
  return topic ? { route: { type: 'topic', slug: 'dark-matter' }, label: `Back to ${topic.name}` } : null;
}
