// exportpaint.js — the canvas painters behind export.js ("Take it to a slide").
//
// The globe's markers, captions and beam labels, and a local map's labels and
// symbols, are HTML. A picture of them is made here the way the page draws them
// and not from a second description of it: each element is read where it is on
// screen (its rectangle, its computed background, border, shadow, font and
// colour) and drawn onto a 2D canvas at that place; an SVG glyph or an SVG layer
// is serialized and drawn as the image it is. Nothing is looked up by name, so a
// change to a stylesheet or to globeicons.js shows up in the export with no
// change here.
//
// Everything works in a transform `xf` = { left, top, s, dx, dy }: a point at
// client (x, y) is drawn at canvas (dx + (x - left) * s, dy + (y - top) * s).

const SVG_NS = 'http://www.w3.org/2000/svg';

// ------------------------------------------------------------------ geometry

export function makeTransform(rect, scale, dx = 0, dy = 0) {
  return { left: rect.left, top: rect.top, s: scale, dx, dy };
}

export function canvasX(xf, clientX) {
  return xf.dx + (clientX - xf.left) * xf.s;
}

export function canvasY(xf, clientY) {
  return xf.dy + (clientY - xf.top) * xf.s;
}

export function canvasBox(xf, rect) {
  return {
    x: canvasX(xf, rect.left), y: canvasY(xf, rect.top), w: rect.width * xf.s, h: rect.height * xf.s,
  };
}

/** The rectangle `a` and `b` share, or null. Both are DOMRect-like (left/top/width/height). */
export function intersects(a, b) {
  return a.left < b.left + b.width && a.left + a.width > b.left
    && a.top < b.top + b.height && a.top + a.height > b.top;
}

// ------------------------------------------------------------------- style

/** Whether `el` takes part in the picture: laid out, and not hidden. (The declutter
 * passes hide a caption with `visibility`, a timeline-absent marker with `display`.) */
export function isShown(el) {
  if (!el || el.getClientRects().length === 0) return false;
  return window.getComputedStyle(el).visibility !== 'hidden';
}

/** The product of the `opacity` of `el` and its ancestors, up to (not including) `stop`. */
export function effectiveOpacity(el, stop) {
  let alpha = 1;
  for (let node = el; node && node !== stop && node.nodeType === 1; node = node.parentElement) {
    const opacity = parseFloat(window.getComputedStyle(node).opacity);
    if (!Number.isNaN(opacity)) alpha *= opacity;
  }
  return alpha;
}

function isTransparent(value) {
  if (!value || value === 'transparent') return true;
  if (/^rgba\(.*,\s*0(\.0+)?\)$/.test(value)) return true;
  return /\/\s*0(\.0+)?\)$/.test(value);
}

/** `value` if the canvas accepts it as a colour, else `fallback`. */
function usableColor(ctx, value, fallback) {
  const sentinel = '#ff00fe';
  ctx.fillStyle = sentinel;
  ctx.fillStyle = value;
  return ctx.fillStyle === sentinel && value !== sentinel ? fallback : value;
}

function splitTop(value, separator) {
  const out = [];
  let depth = 0;
  let current = '';
  for (const char of value) {
    if (char === '(') depth += 1;
    if (char === ')') depth -= 1;
    if (char === separator && depth === 0) {
      out.push(current);
      current = '';
    } else {
      current += char;
    }
  }
  if (current.trim()) out.push(current);
  return out;
}

/** The shadows of a computed `box-shadow` (outer only; an inset shadow is not drawn). */
export function parseShadows(value) {
  if (!value || value === 'none') return [];
  const shadows = [];
  for (const part of splitTop(value, ',')) {
    if (/\binset\b/.test(part)) continue;
    const color = (part.match(/(rgba?\([^)]*\)|color\([^)]*\)|#[0-9a-f]{3,8})/i) || [])[0];
    if (!color) continue;
    const numbers = part.replace(color, '').trim().split(/\s+/)
      .filter((token) => /^-?[\d.]+(px)?$/.test(token)).map(parseFloat);
    shadows.push({
      color, x: numbers[0] || 0, y: numbers[1] || 0, blur: numbers[2] || 0, spread: numbers[3] || 0,
    });
  }
  return shadows;
}

function radiusOf(value, w, h) {
  const first = String(value || '0').split(' ')[0];
  const number = parseFloat(first) || 0;
  const px = first.endsWith('%') ? (Math.min(w, h) * number) / 100 : number;
  return Math.max(0, Math.min(px, Math.min(w, h) / 2));
}

export function roundedPath(ctx, x, y, w, h, radii) {
  const [tl, tr, br, bl] = radii;
  ctx.beginPath();
  ctx.moveTo(x + tl, y);
  ctx.lineTo(x + w - tr, y);
  if (tr) ctx.arcTo(x + w, y, x + w, y + tr, tr);
  ctx.lineTo(x + w, y + h - br);
  if (br) ctx.arcTo(x + w, y + h, x + w - br, y + h, br);
  ctx.lineTo(x + bl, y + h);
  if (bl) ctx.arcTo(x, y + h, x, y + h - bl, bl);
  ctx.lineTo(x, y + tl);
  if (tl) ctx.arcTo(x, y, x + tl, y, tl);
  ctx.closePath();
}

function fontShorthand(cs, scale) {
  const size = (parseFloat(cs.fontSize) || 12) * scale;
  return `${cs.fontStyle} ${cs.fontWeight} ${size}px ${cs.fontFamily}`;
}

// ---------------------------------------------------------------------- box

/** Where `el` is on the canvas, and how it is turned: an element's own rotation or
 * scale (the diamond symbol on a map) is drawn from its layout size around the
 * centre of what the browser reports; anything else is its rectangle as reported. */
function geometryOf(el, cs, xf) {
  const rect = el.getBoundingClientRect();
  if (!rect.width && !rect.height) return null;
  let matrix = null;
  if (cs.transform && cs.transform !== 'none') {
    const m = new window.DOMMatrixReadOnly(cs.transform);
    const plain = Math.abs(m.b) < 1e-6 && Math.abs(m.c) < 1e-6 && Math.abs(m.a - 1) < 1e-3 && Math.abs(m.d - 1) < 1e-3;
    if (!plain) matrix = m;
  }
  if (!matrix) return { ...canvasBox(xf, rect), matrix: null };
  const w = el.offsetWidth * xf.s;
  const h = el.offsetHeight * xf.s;
  const centreX = canvasX(xf, rect.left + rect.width / 2);
  const centreY = canvasY(xf, rect.top + rect.height / 2);
  return {
    x: -w / 2, y: -h / 2, w, h, matrix, centreX, centreY,
  };
}

/** The shadows of a box: an outer shadow is clipped to the outside of the border box
 * (as CSS does), so a spread-only shadow becomes the ring it is. */
function paintBoxShadows(ctx, box, radii, shadows, scale, alpha) {
  for (const shadow of shadows) {
    ctx.save();
    ctx.beginPath();
    ctx.rect(-1e5, -1e5, 2e5, 2e5);
    roundedPath(ctx, box.x, box.y, box.w, box.h, radii);
    ctx.clip('evenodd');
    ctx.globalAlpha = alpha;
    ctx.shadowColor = shadow.color;
    ctx.shadowBlur = shadow.blur * scale;
    ctx.shadowOffsetX = shadow.x * scale;
    ctx.shadowOffsetY = shadow.y * scale;
    ctx.fillStyle = '#000';
    const spread = shadow.spread * scale;
    roundedPath(ctx, box.x - spread, box.y - spread, box.w + 2 * spread, box.h + 2 * spread,
      radii.map((r) => (r ? r + spread : 0)));
    ctx.fill();
    ctx.restore();
  }
}

function paintBorders(ctx, cs, box, radii, scale, alpha) {
  const sides = ['Top', 'Right', 'Bottom', 'Left'].map((name) => ({
    w: (parseFloat(cs[`border${name}Width`]) || 0) * scale,
    style: cs[`border${name}Style`],
    color: cs[`border${name}Color`],
  })).map((side) => (side.style === 'none' || side.style === 'hidden' ? { ...side, w: 0 } : side));
  if (sides.every((side) => side.w === 0)) return;
  ctx.save();
  ctx.globalAlpha = alpha;
  const uniform = sides.every((side) => side.w === sides[0].w && side.style === sides[0].style
    && side.color === sides[0].color);
  if (uniform) {
    const half = sides[0].w / 2;
    ctx.lineWidth = sides[0].w;
    ctx.strokeStyle = usableColor(ctx, sides[0].color, '#888');
    if (sides[0].style === 'dashed') ctx.setLineDash([sides[0].w * 3, sides[0].w * 2]);
    else if (sides[0].style === 'dotted') ctx.setLineDash([sides[0].w, sides[0].w]);
    roundedPath(ctx, box.x + half, box.y + half, box.w - 2 * half, box.h - 2 * half,
      radii.map((r) => Math.max(0, r - half)));
    ctx.stroke();
  } else {
    const [top, right, bottom, left] = sides;
    // One strip per side. A side's join with its neighbour is square, which at the
    // 3 px radius of a label is not visible.
    const strips = [
      [top, box.x, box.y, box.w, top.w, 'h'],
      [bottom, box.x, box.y + box.h - bottom.w, box.w, bottom.w, 'h'],
      [left, box.x, box.y + top.w, left.w, box.h - top.w - bottom.w, 'v'],
      [right, box.x + box.w - right.w, box.y + top.w, right.w, box.h - top.w - bottom.w, 'v'],
    ];
    for (const [side, x, y, w, h, dir] of strips) {
      if (side.w === 0 || w <= 0 || h <= 0) continue;
      const color = usableColor(ctx, side.color, '#888');
      if (side.style === 'dashed' || side.style === 'dotted') {
        ctx.save();
        ctx.beginPath();
        ctx.rect(x, y, w, h);
        ctx.clip();
        ctx.strokeStyle = color;
        ctx.lineWidth = side.w;
        ctx.setLineDash(side.style === 'dashed' ? [side.w * 3, side.w * 2] : [side.w, side.w]);
        ctx.beginPath();
        if (dir === 'h') {
          ctx.moveTo(x, y + h / 2);
          ctx.lineTo(x + w, y + h / 2);
        } else {
          ctx.moveTo(x + w / 2, y);
          ctx.lineTo(x + w / 2, y + h);
        }
        ctx.stroke();
        ctx.restore();
      } else {
        ctx.fillStyle = color;
        ctx.fillRect(x, y, w, h);
      }
    }
  }
  ctx.restore();
}

/** Draws a box of the given canvas rectangle in the style `cs` (a computed style, or a
 * pseudo-element's): shadows, background, borders. The caller has set up any rotation. */
export function paintStyledBox(ctx, cs, box, scale, { alpha = 1 } = {}) {
  const radii = ['TopLeft', 'TopRight', 'BottomRight', 'BottomLeft']
    .map((corner) => radiusOf(cs[`border${corner}Radius`], box.w / scale, box.h / scale) * scale);
  paintBoxShadows(ctx, box, radii, parseShadows(cs.boxShadow), scale, alpha);
  const background = cs.backgroundColor;
  if (!isTransparent(background)) {
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.fillStyle = usableColor(ctx, background, '#0b1620');
    roundedPath(ctx, box.x, box.y, box.w, box.h, radii);
    ctx.fill();
    ctx.restore();
  }
  paintBorders(ctx, cs, box, radii, scale, alpha);
}

/** Draws the box of `el` (shadows, background, borders). Returns its canvas rectangle,
 * or null when it is not drawn. `alpha` multiplies the element's own opacity. */
export function paintBox(ctx, el, xf, { alpha = 1 } = {}) {
  if (!isShown(el)) return null;
  const cs = window.getComputedStyle(el);
  const geometry = geometryOf(el, cs, xf);
  if (!geometry || geometry.w <= 0 || geometry.h <= 0) return null;
  const box = {
    x: geometry.x, y: geometry.y, w: geometry.w, h: geometry.h,
  };
  ctx.save();
  if (geometry.matrix) {
    const m = geometry.matrix;
    ctx.translate(geometry.centreX, geometry.centreY);
    ctx.transform(m.a, m.b, m.c, m.d, 0, 0);
  }
  paintStyledBox(ctx, cs, box, xf.s, { alpha });
  ctx.restore();
  return box;
}

/** The blur-only `drop-shadow()` halos in a computed `filter` — `{ color, sigma }` each,
 * `sigma` being the blur in CSS px — so a glyph is haloed by whatever the stylesheet says. */
export function dropShadowHalos(filter) {
  if (!filter || filter === 'none') return [];
  const halos = [];
  for (const match of filter.matchAll(/drop-shadow\(((?:[^()]|\([^()]*\))*)\)/g)) {
    const shadow = parseShadows(match[1])[0];
    if (shadow) halos.push({ color: shadow.color, sigma: shadow.blur });
  }
  return halos;
}

// --------------------------------------------------------------------- text

/** The lines a text node is set in, as index ranges with their position. */
function textLines(node) {
  const text = node.nodeValue;
  const range = document.createRange();
  range.selectNodeContents(node);
  const whole = range.getClientRects();
  if (whole.length === 1) {
    const rect = whole[0];
    return [{
      start: 0, end: text.length, left: rect.left, top: rect.top, height: rect.height,
    }];
  }
  const lines = [];
  let current = null;
  for (let i = 0; i < text.length; i += 1) {
    range.setStart(node, i);
    range.setEnd(node, i + 1);
    const rect = range.getClientRects()[0];
    if (!rect) continue;
    const blank = /\s/.test(text[i]);
    if (current && Math.abs(rect.top - current.top) < Math.max(2, rect.height * 0.4)) {
      current.end = i + 1;
    } else if (!blank) {
      current = {
        start: i, end: i + 1, left: rect.left, top: rect.top, height: rect.height,
      };
      lines.push(current);
    }
  }
  return lines;
}

function fitEllipsis(ctx, text, maxWidth) {
  if (ctx.measureText(text).width <= maxWidth) return text;
  let lo = 0;
  let hi = text.length;
  while (lo < hi) {
    const mid = Math.ceil((lo + hi) / 2);
    if (ctx.measureText(`${text.slice(0, mid)}…`).width <= maxWidth) lo = mid;
    else hi = mid - 1;
  }
  return `${text.slice(0, lo).trimEnd()}…`;
}

/** Draws every text node under `root` with the font, colour and line breaks the browser
 * gave it. A caption that overflows its box with `text-overflow: ellipsis` is cut the
 * same way. `alpha` multiplies the element's opacity (already folded in by the caller). */
export function paintText(ctx, root, xf, { alpha = 1 } = {}) {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const nodes = [];
  for (let node = walker.nextNode(); node; node = walker.nextNode()) nodes.push(node);
  for (const node of nodes) {
    const text = node.nodeValue;
    if (!text || !text.trim()) continue;
    const parent = node.parentElement;
    if (!parent || !isShown(parent)) continue;
    const lines = textLines(node);
    if (!lines.length) continue;
    const cs = window.getComputedStyle(parent);
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.font = fontShorthand(cs, xf.s);
    ctx.fillStyle = usableColor(ctx, cs.color, '#f4f7f8');
    ctx.textAlign = 'left';
    ctx.textBaseline = 'alphabetic';
    if ('letterSpacing' in ctx) ctx.letterSpacing = `${(parseFloat(cs.letterSpacing) || 0) * xf.s}px`;
    if (cs.overflow !== 'visible' || cs.overflowX !== 'visible') {
      const box = canvasBox(xf, parent.getBoundingClientRect());
      ctx.beginPath();
      ctx.rect(box.x, box.y, box.w, box.h);
      ctx.clip();
    }
    for (const line of lines) {
      let value = text.slice(line.start, line.end).replace(/\s+/g, ' ').trim();
      if (!value) continue;
      if (cs.textOverflow === 'ellipsis' && parent.scrollWidth > parent.clientWidth + 1) {
        const rect = parent.getBoundingClientRect();
        const room = rect.right - (parseFloat(cs.paddingRight) || 0) - line.left;
        value = fitEllipsis(ctx, value, room * xf.s);
      }
      const metrics = ctx.measureText(value);
      const middle = canvasY(xf, line.top + line.height / 2);
      const baseline = typeof metrics.fontBoundingBoxAscent === 'number'
        ? middle + (metrics.fontBoundingBoxAscent - metrics.fontBoundingBoxDescent) / 2
        : middle + (parseFloat(cs.fontSize) || 12) * xf.s * 0.35;
      ctx.fillText(value, canvasX(xf, line.left), baseline);
    }
    ctx.restore();
  }
}

// ------------------------------------------------------------------- images

/** An <img> loaded from SVG markup (through a blob URL, which the page's img-src allows). */
export function loadSvgImage(markup) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(new Blob([markup], { type: 'image/svg+xml;charset=utf-8' }));
    const image = new Image();
    image.onload = () => { URL.revokeObjectURL(url); resolve(image); };
    image.onerror = () => { URL.revokeObjectURL(url); reject(new Error('An SVG layer could not be drawn into the image.')); };
    image.src = url;
  });
}

const glyphCache = new Map();

// A marker glyph's strokes run a little outside its 24 x 24 box (globeicons.js sets
// overflow: visible on it), so it is drawn from a viewBox with 2 units of margin.
const GLYPH_MARGIN = 2;
const GLYPH_BOX = 24;

/** Draws a marker's <svg> glyph — the element globeicons.js built — at its screen
 * position, with the dark halos the stylesheet puts round it (a `drop-shadow` per
 * halo: σ in CSS px, so `shadowBlur` is twice that) and an amber glow when asked. */
export async function paintGlyph(ctx, svg, xf, { alpha = 1, halos = [], glow = null } = {}) {
  const rect = svg.getBoundingClientRect();
  if (!rect.width || !rect.height) return;
  const unit = (rect.width * xf.s) / GLYPH_BOX;
  const out = Math.max(1, Math.ceil(unit * (GLYPH_BOX + 2 * GLYPH_MARGIN)));
  const clone = svg.cloneNode(true);
  clone.setAttribute('viewBox', `${-GLYPH_MARGIN} ${-GLYPH_MARGIN} ${GLYPH_BOX + 2 * GLYPH_MARGIN} ${GLYPH_BOX + 2 * GLYPH_MARGIN}`);
  clone.setAttribute('width', String(out));
  clone.setAttribute('height', String(out));
  const markup = new XMLSerializer().serializeToString(clone);
  const key = `${out}|${markup}`;
  if (!glyphCache.has(key)) glyphCache.set(key, loadSvgImage(markup));
  const image = await glyphCache.get(key);
  const x = canvasX(xf, rect.left) - GLYPH_MARGIN * unit;
  const y = canvasY(xf, rect.top) - GLYPH_MARGIN * unit;
  const size = (GLYPH_BOX + 2 * GLYPH_MARGIN) * unit;
  const draw = (shadow) => {
    ctx.save();
    ctx.globalAlpha = alpha;
    if (shadow) {
      ctx.shadowColor = shadow.color;
      ctx.shadowBlur = 2 * shadow.sigma * xf.s;
    }
    ctx.drawImage(image, x, y, size, size);
    ctx.restore();
  };
  if (glow) draw(glow);
  for (const halo of halos) draw(halo);
  draw(null);
}

/** Draws a leader line (the span a caption is tied back to its marker or beam with):
 * from `origin` (client px) along the leader's own transform, for its own width. */
export function paintLeader(ctx, leader, origin, xf, { alpha = 1 } = {}) {
  if (!isShown(leader)) return;
  const cs = window.getComputedStyle(leader);
  if (cs.display === 'none') return;
  const m = new window.DOMMatrixReadOnly(cs.transform === 'none' ? undefined : cs.transform);
  const length = leader.offsetWidth;
  if (!length) return;
  const angle = Math.atan2(m.b, m.a);
  const x0 = origin.x + m.e;
  const y0 = origin.y + m.f;
  ctx.save();
  ctx.globalAlpha = alpha * (parseFloat(cs.opacity) || 1);
  ctx.strokeStyle = usableColor(ctx, cs.borderTopColor, '#f2b441');
  ctx.lineWidth = (parseFloat(cs.borderTopWidth) || 1.5) * xf.s;
  ctx.lineCap = 'butt';
  ctx.beginPath();
  ctx.moveTo(canvasX(xf, x0), canvasY(xf, y0));
  ctx.lineTo(canvasX(xf, x0 + Math.cos(angle) * length), canvasY(xf, y0 + Math.sin(angle) * length));
  ctx.stroke();
  ctx.restore();
}

/** Leaflet's vector layer, as an image the size it is on screen times `scale`: the
 * live <svg> with the computed paint of every shape written onto it (a stylesheet
 * rule such as the ghosted outline's lower opacity does not travel with a
 * serialized SVG), so the picture is the layer the reader sees. */
export async function rasterizeSvgLayer(svg, scale) {
  const rect = svg.getBoundingClientRect();
  const clone = svg.cloneNode(true);
  const paint = ['fill', 'fill-opacity', 'fill-rule', 'stroke', 'stroke-opacity', 'stroke-width',
    'stroke-dasharray', 'stroke-dashoffset', 'stroke-linecap', 'stroke-linejoin', 'opacity',
    'display', 'visibility'];
  const live = svg.querySelectorAll('*');
  const copy = clone.querySelectorAll('*');
  live.forEach((element, index) => {
    const cs = window.getComputedStyle(element);
    let style = '';
    for (const property of paint) {
      const value = cs.getPropertyValue(property);
      if (value) style += `${property}:${value};`;
    }
    copy[index].setAttribute('style', style);
  });
  clone.removeAttribute('style');
  clone.removeAttribute('class');
  clone.setAttribute('width', String(Math.max(1, Math.round(rect.width * scale))));
  clone.setAttribute('height', String(Math.max(1, Math.round(rect.height * scale))));
  const markup = new XMLSerializer().serializeToString(clone);
  const image = await loadSvgImage(markup);
  return { image, rect };
}

export { SVG_NS };
