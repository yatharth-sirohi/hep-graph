// tex.js — a readable rendering of the TeX that survives in verbatim quotes.
//
// A claim's `quote` is stored exactly as the paper printed it, and an abstract
// taken from arXiv is TeX: "$638.0 \pm 132.8$ ... ($4.8 \sigma$)". The stored
// text is never altered; this module only builds what a panel *shows* —
// "638.0 ± 132.8 ... (4.8 σ)" — and the panel keeps the verbatim string one
// click away. Handled: $…$ delimiters, Greek letters, the operators and
// relations that appear in physics abstracts, ^{…} / _{…} (as Unicode
// super/subscripts when every character has one, otherwise real <sup>/<sub>),
// \mathrm/\rm/\text groups, \bar / \overline, \sqrt, \left / \right and the
// spacing commands. Anything it does not know is shown as its bare name, never
// dropped silently and never as a backslash sequence.

const SYMBOLS = {
  // Greek
  alpha: 'α', beta: 'β', gamma: 'γ', delta: 'δ', epsilon: 'ε', varepsilon: 'ε', zeta: 'ζ', eta: 'η',
  theta: 'θ', vartheta: 'ϑ', iota: 'ι', kappa: 'κ', lambda: 'λ', mu: 'μ', nu: 'ν', xi: 'ξ', pi: 'π',
  rho: 'ρ', varrho: 'ϱ', sigma: 'σ', tau: 'τ', upsilon: 'υ', phi: 'φ', varphi: 'φ', chi: 'χ', psi: 'ψ',
  omega: 'ω', Gamma: 'Γ', Delta: 'Δ', Theta: 'Θ', Lambda: 'Λ', Xi: 'Ξ', Pi: 'Π', Sigma: 'Σ',
  Upsilon: 'Υ', Phi: 'Φ', Psi: 'Ψ', Omega: 'Ω',
  // operators, relations, arrows
  pm: '±', mp: '∓', times: '×', cdot: '·', div: '÷', ast: '∗', circ: '°', degree: '°',
  to: '→', rightarrow: '→', longrightarrow: '→', leftarrow: '←', leftrightarrow: '↔', Rightarrow: '⇒',
  le: '≤', leq: '≤', ge: '≥', geq: '≥', ll: '≪', gg: '≫', lesssim: '≲', gtrsim: '≳', sim: '∼',
  approx: '≈', simeq: '≃', neq: '≠', ne: '≠', equiv: '≡', propto: '∝',
  cup: '∪', cap: '∩', in: '∈', infty: '∞', partial: '∂', nabla: '∇', hbar: 'ℏ', ell: 'ℓ',
  ldots: '…', dots: '…', cdots: '…', prime: '′', dagger: '†', star: '⋆',
  // functions that TeX sets upright
  sin: 'sin', cos: 'cos', tan: 'tan', log: 'log', ln: 'ln', exp: 'exp', min: 'min', max: 'max',
  // escaped characters and spacing
  '%': '%', '&': '&', '#': '#', '_': '_', '$': '$', '{': '{', '}': '}',
  ',': ' ', ';': ' ', ':': ' ', ' ': ' ', '!': '', '\\': ' ', '|': '‖',
};
// Relations and binary operators, set with a space either side in a formula.
const SPACED = new Set(['to', 'rightarrow', 'longrightarrow', 'leftarrow', 'leftrightarrow', 'Rightarrow',
  'le', 'leq', 'ge', 'geq', 'll', 'gg', 'lesssim', 'gtrsim', 'sim', 'approx', 'simeq', 'neq', 'ne', 'equiv',
  'propto', 'in', 'cup', 'cap', 'pm', 'mp', 'times', 'div', 'cdot']);
// Commands that only change the typeface, or size a bracket, and add nothing.
const SWITCHES = new Set(['rm', 'it', 'bf', 'sf', 'tt', 'em', 'displaystyle', 'textstyle', 'left', 'right',
  'big', 'Big', 'bigg', 'Bigg', 'bigl', 'bigr', 'limits', 'nolimits', 'quad', 'qquad']);
// Commands that take one argument and show it unchanged.
const WRAPPERS = new Set(['mathrm', 'mathit', 'mathbf', 'mathsf', 'mathtt', 'mathcal', 'mathbb', 'text',
  'textrm', 'textit', 'textbf', 'textsf', 'boldsymbol', 'bm', 'operatorname', 'rm', 'it', 'bf']);
const ACCENTS = { bar: '̄', overline: '̄', hat: '̂', widehat: '̂', tilde: '̃',
  widetilde: '̃', dot: '̇', ddot: '̈', vec: '⃗', underline: '̲' };

const SUPERSCRIPTS = {
  0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹', '+': '⁺', '−': '⁻', '-': '⁻',
  '=': '⁼', '(': '⁽', ')': '⁾', n: 'ⁿ', i: 'ⁱ', '*': '*', '′': '′', '°': '°',
};
const SUBSCRIPTS = {
  0: '₀', 1: '₁', 2: '₂', 3: '₃', 4: '₄', 5: '₅', 6: '₆', 7: '₇', 8: '₈', 9: '₉', '+': '₊', '−': '₋', '-': '₋',
  '=': '₌', '(': '₍', ')': '₎', a: 'ₐ', e: 'ₑ', o: 'ₒ', x: 'ₓ', h: 'ₕ', k: 'ₖ', l: 'ₗ', m: 'ₘ', n: 'ₙ',
  p: 'ₚ', s: 'ₛ', t: 'ₜ', i: 'ᵢ', j: 'ⱼ', r: 'ᵣ', u: 'ᵤ', v: 'ᵥ',
};

/** True when `text` contains TeX markup (a `$` delimiter or a backslash command). */
export function hasTex(text) {
  // Also a bare script group outside math: some abstracts print "10^{20} eV" without $.
  return typeof text === 'string' && /\$|\\[A-Za-z%&#_{}\\,;:! |]|[\^_]\{/.test(text);
}

// The parser below walks the string once and produces runs: {text, pos} where
// pos is 'sup', 'sub' or '' (inline).
function parse(source, startInMath = false) {
  const runs = [];
  let i = 0;
  let inMath = startInMath;

  function push(text, pos) {
    if (!text) return;
    const last = runs[runs.length - 1];
    if (last && last.pos === pos) last.text += text;
    else runs.push({ text, pos });
  }

  // A unit set upright straight after a number ("10^{-3}\mathrm{eV}") would
  // read as one word; TeX leaves the gap to the author, a reader needs it.
  function unitGap(upright, pos) {
    const last = runs[runs.length - 1];
    if (pos || !last || !/^[A-Za-z]/.test(upright)) return;
    if (/[0-9⁰¹²³⁴⁵⁶⁷⁸⁹₀-₉]$/u.test(last.text) || (last.pos && /[0-9]$/.test(last.text))) push(' ', pos);
  }

  // One TeX "argument": a {group}, a \command, or a single character.
  function readArgument() {
    while (source[i] === ' ') i += 1;
    if (source[i] === '{') {
      i += 1;
      return readUntilClose();
    }
    const start = i;
    if (source[i] === '\\') {
      i += 1;
      if (/[A-Za-z]/.test(source[i] || '')) while (/[A-Za-z]/.test(source[i] || '')) i += 1;
      else i += 1;
    } else if (i < source.length) {
      i += 1;
    }
    return source.slice(start, i);
  }

  function readUntilClose() {
    const start = i;
    let depth = 1;
    while (i < source.length && depth > 0) {
      if (source[i] === '\\') i += 2;
      else {
        if (source[i] === '{') depth += 1;
        else if (source[i] === '}') depth -= 1;
        i += 1;
      }
    }
    return source.slice(start, depth === 0 ? i - 1 : i);
  }

  // Renders a fragment with a fresh parser (so its runs can be post-processed,
  // e.g. to put an accent on each letter) and returns its flat text.
  function flat(fragment) {
    return parse(fragment, inMath).map((run) => (run.pos ? flatten(run, run.pos) : run.text)).join('');
  }

  function walk(pos) {
    while (i < source.length) {
      const ch = source[i];
      if (ch === '$') {
        inMath = !inMath;
        i += 1;
      } else if (ch === '\\') {
        i += 1;
        let name = '';
        if (/[A-Za-z]/.test(source[i] || '')) {
          while (/[A-Za-z]/.test(source[i] || '')) { name += source[i]; i += 1; }
          // TeX swallows the blanks after a command name ("\Delta m").
          while (source[i] === ' ' || source[i] === '\n') i += 1;
        } else if (i < source.length) {
          name = source[i];
          i += 1;
        }
        if (name in ACCENTS) {
          push(flat(readArgument()).replace(/(\P{M})(?!\p{M})/gu, `$1${ACCENTS[name]}`), pos);
        } else if (name === 'sqrt') {
          const arg = flat(readArgument());
          push(`√${arg.length > 1 && /[+\-−\s]/.test(arg) ? `(${arg})` : arg}`, pos);
        } else if (name === 'frac') {
          const a = flat(readArgument());
          const b = flat(readArgument());
          push(`${a}/${b}`, pos);
        } else if (WRAPPERS.has(name)) {
          // \rm and \bf are switches in old TeX ({\rm e^{+}}); the others take
          // a group. A switch with no group in front of it just carries on.
          if (name === 'rm' || name === 'it' || name === 'bf') continue;
          const upright = flat(readArgument());
          if (name !== 'mathcal' && name !== 'mathbb') unitGap(upright, pos);
          push(upright, pos);
        } else if (SWITCHES.has(name)) {
          if (name === 'quad' || name === 'qquad') push(' ', pos);
          // \left. and \right. are invisible brackets
          if ((name === 'left' || name === 'right') && source[i] === '.') i += 1;
        } else if (name in SYMBOLS) {
          push(inMath && SPACED.has(name) ? ` ${SYMBOLS[name]} ` : SYMBOLS[name], pos);
        } else {
          push(name, pos);
        }
      } else if (ch === '^' || ch === '_') {
        i += 1;
        const arg = readArgument();
        const target = ch === '^' ? 'sup' : 'sub';
        for (const run of parse(arg, true)) push(run.text, target);
      } else if (ch === '{') {
        i += 1;
        const group = readUntilClose();
        const inner = parse(group, inMath);
        if (inner.length && !inner[0].pos && /^\s*\\(?:rm|mathrm|text|textrm)\b/.test(group)) unitGap(inner[0].text, pos);
        for (const run of inner) push(run.text, run.pos || pos);
      } else if (ch === '}') {
        i += 1;
      } else if (ch === '~') {
        push(' ', pos);
        i += 1;
      } else if (ch === '-' && inMath) {
        // Inside a formula TeX sets a hyphen as a minus sign.
        push('−', pos);
        i += 1;
      } else if (ch === '\'' && inMath) {
        push('′', pos);
        i += 1;
      } else {
        push(ch, pos);
        i += 1;
      }
    }
  }

  walk('');
  return runs;
}

// Unicode super/subscripts when every character has one; null otherwise.
function toUnicodeScript(text, table) {
  let out = '';
  for (const ch of text.replace(/\s+/g, '')) {
    if (!(ch in table)) return null;
    out += table[ch];
  }
  return out;
}

function flatten(run, pos) {
  const table = pos === 'sup' ? SUPERSCRIPTS : SUBSCRIPTS;
  return toUnicodeScript(run.text, table) || run.text;
}

function tidy(runs) {
  return runs
    .map((run) => ({ ...run, text: run.text.replace(/[ \t\r\n]+/g, ' ') }))
    .filter((run) => run.text !== '');
}

/**
 * The readable form of `text` as runs: [{text, pos}] with pos '', 'sup' or
 * 'sub'. A super/subscript whose characters all exist as Unicode is folded
 * into the surrounding text ("D⁰", "ν̄", "10⁻⁵"); only the others stay runs
 * (rendered as <sup>/<sub> by `readableNodes`).
 */
export function readableRuns(text) {
  const raw = tidy(parse(String(text == null ? '' : text)));
  const folded = [];
  for (const run of raw) {
    const text_ = run.pos ? toUnicodeScript(run.text, run.pos === 'sup' ? SUPERSCRIPTS : SUBSCRIPTS) : null;
    const piece = text_ != null ? { text: text_, pos: '' } : run;
    const last = folded[folded.length - 1];
    if (last && last.pos === piece.pos) last.text += piece.text;
    else folded.push({ ...piece });
  }
  const first = folded[0];
  if (first && !first.pos) first.text = first.text.replace(/^\s+/, '');
  const last = folded[folded.length - 1];
  if (last && !last.pos) last.text = last.text.replace(/\s+$/, '');
  return folded.filter((run) => run.text !== '');
}

/** The readable form of `text` as one plain string ("^"/"_" mark any script that has no Unicode form). */
export function readableText(text) {
  return readableRuns(text).map((run) => (run.pos === 'sup' ? `^(${run.text})` : run.pos === 'sub' ? `_(${run.text})` : run.text)).join('');
}

/** The readable form of `text` as DOM nodes (text, with <sup> / <sub> where Unicode has no form). */
export function readableNodes(text) {
  return readableRuns(text).map((run) => {
    if (!run.pos) return document.createTextNode(run.text);
    const el = document.createElement(run.pos);
    el.textContent = run.text;
    return el;
  });
}

/**
 * A verbatim quote as it should be shown to a reader: in quotation marks, and
 * when it carries TeX, as its readable form with a button that swaps to the
 * stored text exactly as published (and back). A quote with no TeX is shown as
 * is, with no button. The stored string is never altered; `data-verbatim`
 * carries it for anything that wants the original.
 */
export function quoteView(quote) {
  const wrap = document.createElement('span');
  wrap.className = 'quote-view';
  const text = document.createElement('span');
  text.className = 'quote-text';
  wrap.appendChild(text);
  if (!hasTex(quote)) {
    text.textContent = `“${quote}”`;
    return wrap;
  }
  wrap.dataset.verbatim = quote;
  const readable = readableNodes(quote);
  const show = (verbatim) => {
    text.replaceChildren(document.createTextNode('“'),
      ...(verbatim ? [document.createTextNode(quote)] : readable.map((node) => node.cloneNode(true))),
      document.createTextNode('”'));
    text.classList.toggle('is-verbatim', verbatim);
  };
  show(false);
  const toggle = document.createElement('button');
  toggle.type = 'button';
  toggle.className = 'text-btn quote-toggle';
  toggle.textContent = 'Show verbatim';
  toggle.addEventListener('click', () => {
    const verbatim = !text.classList.contains('is-verbatim');
    show(verbatim);
    toggle.textContent = verbatim ? 'Show readable' : 'Show verbatim';
  });
  wrap.append(' ', toggle);
  return wrap;
}

/**
 * Text that may carry TeX (a paper's own title), as a span showing its readable
 * form. The text exactly as published stays in `data-verbatim` and as the
 * hover title; text with no TeX is shown as is.
 */
export function readableView(text) {
  const span = document.createElement('span');
  if (!hasTex(text)) {
    span.textContent = text;
    return span;
  }
  span.className = 'readable-tex';
  span.dataset.verbatim = text;
  span.title = `As published: ${text}`;
  span.append(...readableNodes(text));
  return span;
}
