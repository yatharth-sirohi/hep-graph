// globeicons.js — the inline-SVG glyphs the globe draws for facilities, sites,
// institutions and cluster badges. Pure DOM, no WebGL: the legend and the
// no-WebGL fallback can draw the very same icon with `facilityGlyph`.
//
// One icon per facility kind, drawn on a 24 x 24 grid:
//   accelerator_laboratory     a storage ring around its interaction point
//   underground_laboratory     a cavern below the surface line
//   neutrino_observatory       a detector module with its photosensor
//   astroparticle_observatory  a dish and its feed
//   polar_station              a snowflake
//   reactor_site               a cooling tower
//   research_laboratory        a flask
//   spallation_source          a shattering target (starburst)
// Kind decides shape and hue; status only ever dims (globe.js / atlas.css).
//
// Every glyph is built from the same few primitives so the meanings that the
// markers carry survive the redraw:
//   * `hatched`     — certainty "possible": a diagonal hatch instead of a fill
//   * `approximate` — a campus-grade coordinate: a dashed outline, no fill
//   * `hollow`      — an institution that is uncounted / historical
// A pale keyline is drawn under the coloured shape so even the dimmest status
// colour (a closed site is #3d444a) keeps >= 3:1 against the dark Earth.

const SVG_NS = 'http://www.w3.org/2000/svg';
const INK = '#06141c';

let patternCounter = 0;

function svgEl(name, attrs) {
  const el = document.createElementNS(SVG_NS, name);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  return el;
}

function starPoints(spikes, outer, inner) {
  const points = [];
  for (let i = 0; i < spikes * 2; i += 1) {
    const radius = i % 2 === 0 ? outer : inner;
    const angle = (Math.PI * i) / spikes - Math.PI / 2;
    points.push(`${(12 + radius * Math.cos(angle)).toFixed(2)},${(12 + radius * Math.sin(angle)).toFixed(2)}`);
  }
  return points.join(' ');
}

function snowflake() {
  const out = [];
  for (const angle of [0, 60, 120]) {
    const transform = `rotate(${angle} 12 12)`;
    out.push({ t: 'line', a: { x1: 12, y1: 2.6, x2: 12, y2: 21.4, transform }, r: 'line', w: 2.2 });
    for (const sign of [1, -1]) {
      const y = sign > 0 ? 2.6 : 21.4;
      const tick = sign > 0 ? 3.8 : -3.8;
      for (const dx of [-2.6, 2.6]) {
        out.push({ t: 'line', a: { x1: 12, y1: y + tick, x2: 12 + dx, y2: y + tick / 2 - (sign > 0 ? 0.2 : -0.2), transform }, r: 'line', w: 1.7 });
      }
    }
  }
  return out;
}

// role: body = the filled shape (takes fill / hatch / dash); line = stroke only;
// ink = a detail drawn dark on a solid body, in the colour on an empty one;
// tint = a faint fill inside a stroke-only shape.
const ICONS = {
  ring: [ // accelerator laboratory: a storage ring around its interaction point
    { t: 'circle', a: { cx: 12, cy: 12, r: 8.2 }, r: 'tint' },
    { t: 'circle', a: { cx: 12, cy: 12, r: 8.2 }, r: 'line', w: 2.5 },
    { t: 'circle', a: { cx: 12, cy: 12, r: 2.3 }, r: 'dot' },
  ],
  'triangle-down': [ // underground laboratory: a surface line and a cavern below it
    { t: 'line', a: { x1: 4.2, y1: 4.2, x2: 19.8, y2: 4.2 }, r: 'line', w: 3.2 },
    { t: 'polygon', a: { points: '4.6,9 19.4,9 12,21.4' }, r: 'body' },
  ],
  hexagon: [ // neutrino observatory: a detector module and its photosensor
    { t: 'polygon', a: { points: '12,2.2 20.6,7.1 20.6,16.9 12,21.8 3.4,16.9 3.4,7.1' }, r: 'body' },
    { t: 'circle', a: { cx: 12, cy: 12, r: 3.6 }, r: 'ink' },
  ],
  diamond: [ // astroparticle observatory: a dish and its feed
    { t: 'path', a: { d: 'M21.4 3.6 L3.6 21.4 A14.2 14.2 0 0 0 21.4 3.6 Z' }, r: 'body' },
    { t: 'line', a: { x1: 12.5, y1: 12.5, x2: 6.4, y2: 6.4 }, r: 'line', w: 1.7, solid: true },
    { t: 'circle', a: { cx: 5.4, cy: 5.4, r: 2 }, r: 'dot' },
  ],
  snowflake: snowflake(),
  square: [ // reactor site: a cooling tower
    { t: 'path', a: { d: 'M4.8 21.4 C8.4 17 8.8 11 7.8 3.6 H16.2 C15.2 11 15.6 17 19.2 21.4 Z' }, r: 'body' },
    { t: 'line', a: { x1: 8.4, y1: 9.4, x2: 15.6, y2: 9.4 }, r: 'inkline', w: 1.3 },
    { t: 'line', a: { x1: 8.7, y1: 13.2, x2: 15.3, y2: 13.2 }, r: 'inkline', w: 1.3 },
  ],
  flask: [ // research laboratory
    { t: 'path', a: { d: 'M9 2.6 H15 V8.2 L19.9 17.4 C20.8 19.2 19.7 21.4 17.6 21.4 H6.4 C4.3 21.4 3.2 19.2 4.1 17.4 L9 8.2 Z' }, r: 'body' },
    { t: 'line', a: { x1: 7.4, y1: 15.2, x2: 16.6, y2: 15.2 }, r: 'inkline', w: 1.4 },
  ],
  starburst: [ // spallation source
    { t: 'polygon', a: { points: starPoints(8, 10.4, 4.6) }, r: 'body' },
    { t: 'circle', a: { cx: 12, cy: 12, r: 2 }, r: 'ink' },
  ],
  circle: [
    { t: 'circle', a: { cx: 12, cy: 12, r: 8.6 }, r: 'body' },
  ],
};

// Facility kind -> icon id. model.js's FACILITY_KIND_SHAPE names the shape ids
// of the first six kinds; the last two are drawn here.
const KIND_ICON = {
  research_laboratory: 'flask',
  spallation_source: 'starburst',
};

export function iconIdForShape(shape, kind) {
  if (kind && KIND_ICON[kind]) return KIND_ICON[kind];
  return ICONS[shape] ? shape : 'circle';
}

/** `#rrggbb` mixed toward white by `amount` (0..1). */
export function lighten(hex, amount) {
  const m = /^#?([0-9a-f]{6})$/i.exec(hex || '');
  if (!m) return '#dfeeee';
  const n = parseInt(m[1], 16);
  const channel = (shift) => {
    const c = (n >> shift) & 255;
    return Math.round(c + (255 - c) * amount).toString(16).padStart(2, '0');
  };
  return `#${channel(16)}${channel(8)}${channel(0)}`;
}

/** WCAG relative luminance of `#rrggbb`. */
export function luminance(hex) {
  const m = /^#?([0-9a-f]{6})$/i.exec(hex || '');
  if (!m) return 0.5;
  const n = parseInt(m[1], 16);
  const lin = (shift) => {
    const c = ((n >> shift) & 255) / 255;
    return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * lin(16) + 0.7152 * lin(8) + 0.0722 * lin(0);
}

/** `hex`, or the nearest lighter mix of it that reaches `min` relative luminance:
 * an outline with nothing inside it has only its own colour to be seen by, and the
 * dimmest status colours (#3d444a) cannot be seen on a dark Earth. */
export function liftToLuminance(hex, min) {
  let out = hex;
  for (let step = 1; step <= 10 && luminance(out) < min; step += 1) out = lighten(hex, step * 0.1);
  return out;
}

function drawPrimitive(p, attrs) {
  return svgEl(p.t, { ...p.a, ...attrs });
}

/**
 * A marker glyph. `shape` is a model.js shape id (or 'cluster'), `kind` the
 * facility kind when it has no shape id of its own.
 */
export function buildGlyph({
  shape, kind, color, size, hollow, hatched, approximate, keyline = true,
}) {
  const svg = svgEl('svg', {
    viewBox: '0 0 24 24', width: size, height: size, 'aria-hidden': 'true', focusable: 'false',
  });
  if (shape === 'cluster') {
    svg.appendChild(svgEl('circle', {
      cx: 12, cy: 12, r: 10.2, fill: 'rgba(8,22,32,0.94)', stroke: color, 'stroke-width': 1.8,
    }));
    svg.appendChild(svgEl('circle', {
      cx: 12, cy: 12, r: 8.2, fill: 'none', stroke: color, 'stroke-width': 0.6, 'stroke-opacity': 0.45,
    }));
    return svg;
  }
  const primitives = ICONS[iconIdForShape(shape, kind)];
  // `empty`: no solid fill. An approximate marker keeps a faint tint inside its
  // dashed outline, so a major laboratory on a campus-grade point still reads as
  // a shape of its size, not as a hole.
  const empty = hollow || approximate;
  let fill = hollow ? 'none' : color;
  if (hatched && !hollow) {
    patternCounter += 1;
    const patternId = `atlas-hatch-${patternCounter}`;
    const defs = svgEl('defs', {});
    const pattern = svgEl('pattern', {
      id: patternId, width: '4', height: '4', patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(45)',
    });
    pattern.appendChild(svgEl('rect', { width: '4', height: '4', fill: 'rgba(0,0,0,0.35)' }));
    pattern.appendChild(svgEl('line', {
      x1: '0', y1: '0', x2: '0', y2: '4', stroke: color, 'stroke-width': '2',
    }));
    defs.appendChild(pattern);
    svg.appendChild(defs);
    fill = `url(#${patternId})`;
  }
  const bodyWidth = empty ? 2.4 : hatched ? 1.5 : 1;
  const dash = approximate ? '2,2' : (hatched && hollow ? '3,2' : null);
  const edge = lighten(color, 0.58);
  // An outline with nothing inside is seen by its own colour alone.
  const ink = empty ? liftToLuminance(color, 0.36) : color;

  // Keyline first, under everything: the same outline, wider. Pale under a solid
  // shape; dark under a dashed one, where a pale underlay would fill the gaps that
  // make it dashed.
  if (keyline) {
    const under = svgEl('g', {
      'stroke-linejoin': 'round', 'stroke-linecap': dash ? 'butt' : 'round', fill: 'none', 'pointer-events': 'none',
    });
    for (const p of primitives) {
      if (p.r === 'ink' || p.r === 'inkline' || p.r === 'tint') continue;
      const solidFill = p.r === 'body' || p.r === 'dot';
      const width = (p.r === 'body' || p.r === 'dot' ? bodyWidth : p.w || 2) + (dash ? 1.6 : 1.7);
      const attrs = dash
        ? { stroke: 'rgba(3,12,19,0.62)', 'stroke-width': width, fill: 'none' }
        : {
          stroke: edge, 'stroke-width': width, fill: solidFill && !empty ? edge : 'none', 'stroke-opacity': 0.92,
        };
      under.appendChild(drawPrimitive(p, attrs));
    }
    svg.appendChild(under);
  }

  const group = svgEl('g', { 'stroke-linejoin': 'round', 'stroke-linecap': dash ? 'butt' : 'round' });
  for (const p of primitives) {
    switch (p.r) {
      case 'body': {
        const attrs = { fill, stroke: ink, 'stroke-width': bodyWidth };
        if (approximate && !hollow) attrs['fill-opacity'] = hatched ? 0.6 : 0.3;
        if (dash) attrs['stroke-dasharray'] = dash;
        group.appendChild(drawPrimitive(p, attrs));
        break;
      }
      case 'tint':
        if (!hollow) group.appendChild(drawPrimitive(p, { fill: hatched ? fill : color, 'fill-opacity': hatched ? 0.6 : 0.22, stroke: 'none' }));
        break;
      case 'line': {
        const attrs = { fill: 'none', stroke: ink, 'stroke-width': p.w || 2 };
        if (dash && !p.solid) attrs['stroke-dasharray'] = dash;
        group.appendChild(drawPrimitive(p, attrs));
        break;
      }
      case 'dot':
        group.appendChild(drawPrimitive(p, { fill: ink, stroke: 'none' }));
        break;
      case 'ink':
        group.appendChild(drawPrimitive(p, { fill: empty ? ink : INK, stroke: 'none' }));
        break;
      case 'inkline':
        group.appendChild(drawPrimitive(p, {
          fill: 'none', stroke: empty ? ink : INK, 'stroke-width': p.w || 1.4, 'stroke-linecap': 'round',
        }));
        break;
      default:
        break;
    }
  }
  svg.appendChild(group);
  return svg;
}

/** The glyph for a facility kind as a ready SVG element (legend, key, fallback). */
export function facilityGlyph(kind, { shape, color, size = 18 } = {}) {
  return buildGlyph({
    shape, kind, color: color || '#9aa7b0', size, hollow: false, hatched: false, approximate: false,
  });
}
