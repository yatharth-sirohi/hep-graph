// underground-rows.js — which laboratories the "Going underground" chart can draw, and how a
// panel, the search box or the chart itself names them. Pure data and arithmetic over
// atlas.json (no DOM, no fetch), so panels.js and the search can use it without loading the
// view, and a unit check can run it under Node.
//
//   #/view/underground           depth in m.w.e. (x) against cosmic-ray muon flux (y, log)
//
// A *row* is one site that records both `depth_mwe` and `muon_flux`. The chart reads those two
// fields and nothing else (A27, docs/HEP_ATLAS_ONTOLOGY.md).

export const VIEW_NAME = 'underground';
// The owner names features; this is the working title, and the only place it is written (the
// heading, the panel links and the search entry all read it here).
export const WORKING_TITLE = 'Going underground';

/**
 * Conversion of a recorded muon flux to cm⁻² s⁻¹, the unit the chart is drawn in.
 *
 * COPIED from hepgraph/atlas/schema.py UNIT_SCALE['muon_flux'] (amendment A27): the bundle keeps
 * each source's own unit, so the conversion is done here, with the same factors. 1 m⁻² = 10⁻⁴
 * cm⁻²; 1 d = 86 400 s. tests/test_atlas_charts.py fails if this table and the schema drift.
 */
export const MUON_FLUX_SCALE = Object.freeze({
  'cm^-2 s^-1': 1,
  'm^-2 s^-1': 1e-4,
  'm^-2 d^-1': 1e-4 / 86400,
});

/** A recorded muon flux in cm⁻² s⁻¹, or null when it has no usable number or a unit the A27 table does not list. */
export function muonFluxCm2s(quantity) {
  if (!quantity || typeof quantity.value !== 'number' || !Number.isFinite(quantity.value) || !(quantity.value > 0)) return null;
  const scale = MUON_FLUX_SCALE[quantity.unit];
  return scale === undefined ? null : quantity.value * scale;
}

/** A recorded depth in m.w.e., or null. */
export function depthMwe(quantity) {
  if (!quantity || typeof quantity.value !== 'number' || !Number.isFinite(quantity.value) || !(quantity.value > 0)) return null;
  return String(quantity.unit || 'm.w.e.') === 'm.w.e.' ? quantity.value : null;
}

/** [lo, hi] in cm⁻² s⁻¹ when the record carries a numeric range (`min` and `max`) around its value, else null.
 * Today no record does: an uncertainty written in `display` is prose, and the chart does not parse prose. */
export function fluxRange(quantity) {
  const scale = quantity ? MUON_FLUX_SCALE[quantity.unit] : undefined;
  if (scale === undefined) return null;
  const { min, max, value } = quantity;
  if (![min, max, value].every((n) => typeof n === 'number' && Number.isFinite(n)) || !(min > 0) || min > value || value > max) return null;
  return [min * scale, max * scale];
}

/** A number as a physicist writes it, to three significant figures: 3.43 × 10⁻⁸ (a plain number between 0.01 and 1000). */
export function sciText(value, digits = 3) {
  const exponent = Math.floor(Math.log10(value));
  let mantissa = Number((value / 10 ** exponent).toPrecision(digits));
  let power = exponent;
  if (mantissa >= 10) { mantissa /= 10; power += 1; }
  const sup = (n) => String(n).replace(/[0-9-]/g, (c) => '\u2070\u00b9\u00b2\u00b3\u2074\u2075\u2076\u2077\u2078\u2079\u207b'['0123456789-'.indexOf(c)]);
  return `${mantissa} \u00d7 10${sup(power)}`;
}

/** A flux as the chart's own tables write it: "3.43 × 10⁻⁸ cm⁻² s⁻¹". */
export function fluxText(value) {
  return `${sciText(value)} cm\u207b\u00b2 s\u207b\u00b9`;
}

// ---- names ------------------------------------------------------------------------
function stripParen(text) {
  return String(text || '').replace(/\s*\([^)]*\)/g, '').trim();
}

/** The shortest of a record's name and aliases that is at least `min` characters, or its name. */
function shortestName(record, min = 3) {
  if (!record) return '';
  const all = [record.name, ...(record.aliases || [])].map(stripParen).filter((t) => t.length >= min);
  all.sort((a, b) => a.length - b.length);
  return all[0] || stripParen(record.name);
}

// Display names for the sites whose own name and aliases give no good short label ("KamLAND cavity,
// Kamioka mine", "Soudan MINOS far detector cavern"). They are text on a chart, not facts: a site
// that is not listed falls back to the rule in siteLabel().
const CHART_LABELS = {
  'site:baksan-sage-underground-lab': 'Baksan',
  'site:boulby-mine': 'Boulby',
  'site:juno-jiangmen-underground-lab': 'JUNO',
  'site:kamioka-kamland': 'Kamioka',
  'site:lsc-canfranc': 'LSC',
  'site:soudan-minos-far-detector': 'Soudan',
  'site:surf-davis-campus-lz': 'SURF',
  'site:wipp-surface-campus': 'WIPP',
};

/**
 * The label drawn on the chart. A site whose own name is short enough carries it ("LNGS Hall C",
 * "CJPL-II"), so the halls of one laboratory stay told apart; otherwise the facility's short name
 * ("SNOLAB", "SURF"), else the site's own.
 */
export function siteLabel(site, facility) {
  if (CHART_LABELS[site.id]) return CHART_LABELS[site.id];
  const own = stripParen(site.name);
  if (own.length <= 14) return own;
  const fromFacility = shortestName(facility, 3);
  if (fromFacility && fromFacility.length <= 14) return fromFacility;
  const fromSite = shortestName(site, 3);
  if (fromSite.length <= 18) return fromSite;
  return `${own.slice(0, 13).trimEnd()}…`;
}

// ---- rows ---------------------------------------------------------------------------
export function viewHash() {
  return `#/view/${VIEW_NAME}`;
}

function facilityOf(atlas, site) {
  return (site.facility_id && atlas.facilities && atlas.facilities[site.facility_id]) || null;
}

/**
 * Every site with both a depth in m.w.e. and a muon flux, in order of depth (then flux, then id):
 * `{ id, slug, site, facility, label, depthMwe, flux (cm^-2 s^-1), fluxQuantity, depthQuantity }`.
 * `skipped` lists a site that carries a muon flux the chart cannot place (an unlisted unit, no
 * number, no depth), with the reason: a record is never dropped without saying so.
 */
export function undergroundData(atlas) {
  const rows = [];
  const skipped = [];
  for (const site of Object.values(atlas.sites || {})) {
    if (!site.muon_flux) continue;
    const flux = muonFluxCm2s(site.muon_flux);
    const depth = depthMwe(site.depth_mwe);
    if (flux == null || depth == null) {
      skipped.push({
        id: site.id,
        site,
        reason: flux == null
          ? `its muon flux is in a unit the chart cannot convert (${site.muon_flux.unit || 'none'}) or has no number`
          : 'it records no depth in m.w.e.',
      });
      continue;
    }
    const facility = facilityOf(atlas, site);
    rows.push({
      id: site.id,
      slug: site.id.split(':')[1],
      site,
      facility,
      label: siteLabel(site, facility),
      depthMwe: depth,
      flux,
      depthQuantity: site.depth_mwe,
      fluxQuantity: site.muon_flux,
    });
  }
  rows.sort((a, b) => (a.depthMwe - b.depthMwe) || (a.flux - b.flux) || (a.id < b.id ? -1 : 1));
  return { rows, skipped };
}

export function undergroundRows(atlas) {
  return undergroundData(atlas).rows;
}

/**
 * Sites that record a depth in m.w.e. but no muon flux: "depth known, flux not recorded". A site
 * with a rock depth in metres only (the CERN caverns, the J-PARC near hall) is not listed: its depth
 * is not on this chart's axis.
 */
export function depthOnlyRows(atlas) {
  const out = [];
  for (const site of Object.values(atlas.sites || {})) {
    if (site.muon_flux) continue;
    const depth = depthMwe(site.depth_mwe);
    if (depth == null) continue;
    out.push({ id: site.id, slug: site.id.split(':')[1], site, facility: facilityOf(atlas, site), depthMwe: depth, depthQuantity: site.depth_mwe });
  }
  out.sort((a, b) => (b.depthMwe - a.depthMwe) || (a.id < b.id ? -1 : 1));
  return out;
}

/** Rows of one facility (the underground-laboratory panel's link). */
export function rowsForFacility(atlas, facilityId) {
  return undergroundRows(atlas).filter((row) => row.site.facility_id === facilityId);
}

/** True when a record's flux or confidence marks it as less than a plain measurement: the chart draws it hollow. */
export function isApproximate(fluxQuantity, claim) {
  if (fluxQuantity && fluxQuantity.approx === true) return true;
  return !!claim && (claim.confidence === 'approximate' || claim.confidence === 'uncertain');
}

// ---- search -------------------------------------------------------------------------
/** Search entries for the Atlas search box. Nothing when the data records no muon flux at all: the
 * search never offers a chart that cannot be drawn. */
export function undergroundSearchEntries(atlas) {
  const rows = undergroundRows(atlas);
  if (!rows.length) return [];
  return [{
    type: 'view',
    id: `view:${VIEW_NAME}`,
    name: WORKING_TITLE,
    aliases: [
      'depth against muon flux',
      'cosmic-ray muon flux',
      'muon flux underground',
      'meters water equivalent',
      'm.w.e.',
      'how deep are the underground labs',
      'underground laboratories chart',
      'cosmic ray shielding',
    ],
    subtitle: `Chart · depth against muon flux, ${rows.length} laboratory sites`,
  }];
}
