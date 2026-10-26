// registry.js — the table of Atlas "views": full-stage pages that draw a physics
// figure from Atlas records (a cross-section of the Earth along a neutrino beam
// today; the energy-frontier chart, the underground chart, scale comparisons and
// "follow the proton" next). A view is ONE module plus ONE line in VIEWS below.
//
// ROUTE      #/view/<name>/<arg>       (state.js: TYPE_PREFIX.view)
//            It is an ordinary route: Back/Forward, a pasted link, the `?y=` year and
//            the search box all reach it through the code every other route uses. The
//            `<arg>` is the view's own business (the beam section: `lbnf` or `numi~1`).
//
// THE ENTRY  VIEWS[name] = {
//              title,                    working title (the owner names features), shown
//                                        in the heading while the module loads
//              load,                     () => import('./<name>.js') — nothing loads
//                                        until the route is opened
//              parent(arg, atlas),       optional: { route, label } where "Back" goes
//                                        when the reader did not arrive from inside the
//                                        Atlas (a pasted link); `route` is { type, slug }
//              searchEntries(atlas),     optional: search rows { type: 'view',
//                                        id: 'view:<name>/<arg>', name, aliases,
//                                        subtitle } so the search box reaches the view.
//                                        Imported statically, so keep it small and pure.
//            }
//
// THE MODULE exports  mount(ctx)  and may return { update(ctx), destroy() }, directly
//            or as a promise. `update` runs when only the year/range changed; `destroy`
//            when the route leaves or another view takes over (stop observers, timers).
//
//   ctx = {
//     arg,            the part of the route after `<name>/`
//     atlas, index,   atlas.json (site coordinates already lifted to lat/lon) and the id -> record map
//     loader,         lazy bundles: getProvenance(), getSources(), getText(), …
//     navigate,       state.navigate — open a record (`navigate({ entity: { type, slug } })`)
//     timelineState,  { year } or { range: [lo, hi] }, the selected timeline position
//     host,           the framework's frame (below)
//   }
//   host = {
//     body,                      element for the figure and its numbers (the module owns it)
//     method,                    element inside the "Inputs and method" disclosure
//     setTitle(text), setSubtitle(textOrNode),
//     setBack({ label, route }), where "Back" goes without history (default: the globe)
//     announce(text),            polite live-region message
//     fail(message, { retry }),  show an error instead of a figure: a view that cannot
//                                draw says so; it never draws an empty chart
//   }
//
// RULES  (docs/HEP_ATLAS_TEACHING_PLAN.md, principle 1)
//   * Every mark is traceable: a computed number states its formula and inputs in
//     `host.method`, with its uncertainty; a plotted record names its source.
//   * A failure is an error message, never an empty or default figure.
//   * Use only the tokens in atlas.css; the view's own rules live in views.css.
//   * Respect prefers-reduced-motion (no animation) and give the SVG a <title>/<desc>
//     and its numbers in a table.

import { VIEW_NAME, WORKING_TITLE, beamSearchEntries, parseArg } from './beam-rows.js';
import {
  VIEW_NAME as COMPARE_NAME, WORKING_TITLE as COMPARE_TITLE, compareSearchEntries,
} from './compare-route.js';

export const VIEWS = {
  [VIEW_NAME]: {
    title: WORKING_TITLE,
    load: () => import('./beam-section.js'),
    parent(arg, atlas) {
      const parsed = parseArg(arg);
      const beamline = parsed && (atlas.beamlines || {})[`beamline:${parsed.slug}`];
      return beamline ? { route: { type: 'beamline', slug: parsed.slug }, label: `Back to ${beamline.name}` } : null;
    },
    searchEntries: beamSearchEntries,
  },
  // Two to four experiments side by side: #/view/compare/dune,juno (compare-route.js).
  [COMPARE_NAME]: {
    title: COMPARE_TITLE,
    load: () => import('./compare.js'),
    searchEntries: compareSearchEntries,
  },
};

/** `{ name, arg }` from the route's slug (`beam-section/lbnf~1`). */
export function parseViewSlug(slug) {
  const at = String(slug || '').indexOf('/');
  if (at < 0) return { name: String(slug || ''), arg: '' };
  return { name: slug.slice(0, at), arg: slug.slice(at + 1) };
}

export function getView(name) {
  return Object.prototype.hasOwnProperty.call(VIEWS, name) ? VIEWS[name] : null;
}

/** Search rows of every registered view, for the search box. */
export function viewSearchEntries(atlas) {
  return Object.values(VIEWS).flatMap((view) => (view.searchEntries ? view.searchEntries(atlas) : []));
}
