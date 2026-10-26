"""HEP Atlas guided tours (A28): format, validation and the `tours.json` bundle.

A tour is an authored walk through the Atlas: a sequence of steps, each with a
camera, a timeline year, a selection, optionally a local map or a computed
view, one or two plain sentences and an optional question with a worked
answer.  The rule that makes it part of the Atlas and not a slide deck is that
**every factual claim in a sentence is traceable**:

* an *own* claim carries a verbatim ``quote``, a ``locator``, ``sources``,
  ``confidence`` and ``verified_at`` (the same shape as any sourced value);
* a *reference* claim, ``{"ref": "experiment:t2k", "field": "key_specs.Baseline"}``,
  points at a field of an Atlas record that is already sourced, so the tour
  can never say something the record does not.

``covers`` names the phrase of the text a claim supports.  The validator checks
that it is a verbatim substring, that every sentence contains at least one
covered phrase, that every number in the text sits inside a covered phrase, and
that each covered number agrees with the number the reference resolves to (or
the number in the quote): the sentence cannot drift away from its evidence
without the validator noticing.  Nothing here decides whether a quote supports
a sentence; that is a reviewer's job, and the tour's log says who did it.

This module reads the loaded :class:`hepgraph.atlas.load.Atlas` and nothing
else.  ``validate.py`` and ``build.py`` call :func:`validate_tour` and
:func:`build_bundle`.  Run ``python -m hepgraph.atlas.tours show <id> <field>``
to see what a reference resolves to.
"""
from __future__ import annotations

import ast
import datetime as _dt
import json
import math
import operator
import re
from urllib.parse import quote as _urlquote
from dataclasses import dataclass, field
from typing import Any, Iterable

from . import schema

__all__ = [
    'VIEW_NAMES', 'ROUTABLE_TYPES', 'Issue', 'Resolved', 'RefError', 'resolve',
    'validate_tour', 'build_bundle', 'step_href',
]

ERROR = 'error'
WARNING = 'warning'

#: A28: the computed views a step may open.  `beam-section` is the cross-section
#: of the Earth along one beamline (M2); its `arg` is the beamline slug.
VIEW_NAMES: tuple[str, ...] = ('beam-section',)

#: The entity types the app can route to (`TYPE_PREFIX` in static/atlas/js/state.js;
#: `tests/test_atlas_tours.py` keeps the two in step).  A step may `select` only these.
ROUTABLE_TYPES: tuple[str, ...] = (
    'facility', 'experiment', 'collaboration', 'institution', 'topic', 'result',
    'document', 'site', 'detector', 'accelerator', 'beamline', 'map',
)

STEP_MIN, STEP_MAX = 5, 9
QUESTION_MIN, QUESTION_MAX = 2, 3
MINUTES_MAX = 60
SENTENCES_MAX = 2
THIN_COVERAGE = 0.5               # a sentence whose claims cover less than this warns
ALTITUDE_RANGE = (0.05, 4.0)     # what `showView` in globe.js accepts
YEAR_MIN = 1900

_SLUG_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
_SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+')
#: A number as a reader sees one: thousands commas allowed, never glued to a
#: preceding letter ("T2K", "ND280", "D2O" contain no number) and not the digits
#: of a hyphenated name ("DEAP-3600", "PandaX-4T") or of "Run 3" / "Long Shutdown 3".
_NUMBER_RE = re.compile(r'(?<![\w.])(?<![A-Za-z]-)(?<!Run )(?<!Shutdown )(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?')

#: Row keys a path segment may use to pick one item of a list.
_ROW_KEYS = ('label', 'id', 'name', 'to_site_id', 'site_id', 'facility_id', 'experiment_id',
             'entity_id')


@dataclass(frozen=True)
class Issue:
    """One tour finding; `pointer` is an RFC 6901 pointer into the tour record."""

    level: str
    rule: str
    pointer: str
    message: str


class RefError(ValueError):
    """A reference claim that cannot be resolved; the message says why."""

    def __init__(self, rule: str, message: str) -> None:
        super().__init__(message)
        self.rule = rule
        self.message = message


@dataclass
class Resolved:
    """What a reference claim points at."""

    entity_id: str
    field: str
    node: Any                   # the value the path ends on
    carrier: dict               # nearest sourced node on the path (never the record root)
    text: str                   # how the value reads, for the player and for number checks
    candidates: list[float] = field(default_factory=list)

    @property
    def sources(self) -> list[str]:
        return [s for s in self.carrier.get('sources') or [] if isinstance(s, str)]


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _pointer(*tokens: Any) -> str:
    return '/' + '/'.join(str(t).replace('~', '~0').replace('/', '~1') for t in tokens) if tokens else ''


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ''


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def sentences(text: str) -> list[str]:
    return [part for part in _SENTENCE_SPLIT_RE.split(text.strip()) if part]


def number_tokens(text: str) -> list[tuple[str, int, int]]:
    """`(token, start, end)` of every number in `text`."""
    return [(m.group(0), m.start(), m.end()) for m in _NUMBER_RE.finditer(text)]


def _token_value(token: str) -> float:
    return float(token.replace(',', ''))


def number_matches(token: str, candidates: Iterable[float]) -> bool:
    """Does the number written as `token` agree with one of `candidates`?

    A decimal token (``1.5``, ``0.98``) agrees with any candidate that rounds to
    it at the written precision, so "about 1.5 km" matches a record's 1478 m.
    An integer token must match exactly, except that one with two or more
    trailing zeros (``1500``) is read as rounded at its last non-zero digit.
    """
    clean = token.replace(',', '')
    wanted = float(clean)
    for candidate in candidates:
        if not _is_number(candidate) or not math.isfinite(candidate):
            continue
        if math.isclose(candidate, wanted, rel_tol=1e-9, abs_tol=1e-12):
            return True
        if '.' in clean:
            places = len(clean.split('.')[1])
            if math.isclose(round(candidate, places), wanted, rel_tol=1e-9, abs_tol=1e-12):
                return True
        else:
            trailing = len(clean) - len(clean.rstrip('0'))
            if trailing >= 2 and wanted != 0:
                digits = len(clean) - trailing
                if candidate != 0:
                    scale = 10 ** (math.floor(math.log10(abs(candidate))) - digits + 1)
                    if math.isclose(round(candidate / scale) * scale, wanted, rel_tol=1e-9):
                        return True
    return False


_GROUPED_RE = re.compile(r'(?<![\w.])\d{1,3}(?:[ \u00a0\u202f]\d{3})+(?:\.\d+)?')


def _numbers_in(text: str) -> list[float]:
    """Every number a source states, including ``299 792 458`` (SI digit grouping)."""
    out = [_token_value(token) for token, _s, _e in number_tokens(text)]
    out.extend(float(re.sub(r'[ \u00a0\u202f]', '', m.group(0))) for m in _GROUPED_RE.finditer(text))
    if re.search(r'\d\s*[x×]\s*10\^?[-−+]?\d', text):      # "1.7x10^-9": the 10 is a number too
        out.append(10.0)
    return out


def _date_text(value: Any) -> str:
    if isinstance(value, dict):
        return _text(value.get('display')) or str(value.get('date') or '')
    return '' if value is None else str(value)


def _quantity_candidates(quantity: dict) -> list[float]:
    """The quantity's number in its own unit and in every other unit of its dimension."""
    out: list[float] = []
    dimension, unit = quantity.get('dimension'), quantity.get('unit')
    magnitude = schema.quantity_magnitude(quantity)
    for key in ('value', 'min', 'max'):
        if _is_number(quantity.get(key)):
            out.append(float(quantity[key]))
    if magnitude is not None:
        for other in schema.UNITS.get(dimension, ()):
            scale = schema.unit_scale(dimension, other)
            if scale:
                out.append(magnitude / scale)
    return out


def _value_text(node: Any) -> str:
    if isinstance(node, dict):
        if schema.is_interval(node):
            end = _date_text(node.get('end')) or 'now'
            return f"{node.get('label')}: {node.get('status')}, {_date_text(node.get('start'))} to {end}"
        if _text(node.get('display')):
            return str(node['display'])
        if schema.is_quantity(node):
            if _is_number(node.get('value')):
                return f"{node['value']} {node.get('unit') or ''}".strip()
            return f"{node.get('min')} to {node.get('max')} {node.get('unit') or ''}".strip()
        if 'value' in node:
            return _value_text(node['value'])
        if 'date' in node:
            return _date_text(node)
        if schema.is_coordinates(node):
            return f"{node.get('lat')}, {node.get('lon')}"
        if _text(node.get('quote')):
            return node['quote']
        return json.dumps({k: v for k, v in node.items() if k not in schema.PROVENANCE_KEYS},
                          ensure_ascii=False, sort_keys=True)
    if isinstance(node, list):
        return '; '.join(_value_text(item) for item in node)
    return '' if node is None else str(node)


def _node_candidates(node: Any) -> list[float]:
    out: list[float] = []
    if isinstance(node, dict):
        if schema.is_quantity(node):
            out.extend(_quantity_candidates(node))
        elif _is_number(node.get('value')):
            out.append(float(node['value']))
    elif _is_number(node):
        out.append(float(node))
    return out


# ---------------------------------------------------------------------------
# Resolving a reference claim
# ---------------------------------------------------------------------------

_MISSING = object()


def _pick_row(rows: list, name: str) -> Any:
    if name.isdigit():
        index = int(name)
        return rows[index] if index < len(rows) else _MISSING
    for row in rows:
        if isinstance(row, dict):
            if any(row.get(key) == name for key in _ROW_KEYS):
                return row
        elif row == name:
            return row
    return _MISSING


def resolve(atlas: Any, entity_id: Any, field_path: Any) -> Resolved:
    """Follow `field_path` into the record `entity_id`; raise :class:`RefError`.

    A path is dotted.  A segment into a list picks the row whose ``label``,
    ``id``, ``name`` or ``to_site_id`` equals it, or the row at that index, and a
    label may itself contain dots (the longest match wins).  The value reached
    must lie under a sourced node (one with a non-empty ``sources``), which is
    the node whose provenance the claim inherits; a ``key_specs`` row resolves to
    its ``quantity``.
    """
    if not isinstance(entity_id, str) or not entity_id:
        raise RefError('tour-ref-unknown-entity', f'`ref` must be an entity id, got {entity_id!r}')
    if not isinstance(field_path, str) or not field_path.strip():
        raise RefError('tour-ref-unknown-field', f'`field` must be a non-empty path, got {field_path!r}')
    record = atlas.get(entity_id)
    if record is None:
        raise RefError('tour-ref-unknown-entity', f'{entity_id!r} does not exist in the Atlas')
    if schema.id_type(entity_id) in {'tour', 'source'}:
        raise RefError('tour-ref-unknown-entity', f'a claim may not reference a {schema.id_type(entity_id)}')

    parts = field_path.strip().split('.')
    node: Any = record
    carrier: dict | None = None
    i = 0
    while i < len(parts):
        if isinstance(node, dict):
            key = parts[i]
            if key not in node:
                raise RefError('tour-ref-unknown-field',
                               f'{entity_id} has no field {".".join(parts[:i + 1])!r}')
            node = node[key]
            i += 1
        elif isinstance(node, list):
            for stop in range(len(parts), i, -1):
                row = _pick_row(node, '.'.join(parts[i:stop]))
                if row is not _MISSING:
                    node, i = row, stop
                    break
            else:
                raise RefError('tour-ref-unknown-field',
                               f'{entity_id}: no item {".".join(parts[i:])!r} in the list at '
                               f'{".".join(parts[:i]) or "(top)"!r}')
        else:
            raise RefError('tour-ref-unknown-field',
                           f'{entity_id}: {".".join(parts[:i])!r} is a plain value, it has no '
                           f'{parts[i]!r}')
        if isinstance(node, dict) and node.get('sources'):
            carrier = node
    if isinstance(node, dict) and 'quantity' in node and not node.get('sources'):
        node = node['quantity']
        if isinstance(node, dict) and node.get('sources'):
            carrier = node
    if node is None:
        raise RefError('tour-ref-unknown-field', f'{entity_id} {field_path!r} is null')
    if isinstance(node, list):
        raise RefError('tour-ref-unknown-field',
                       f'{entity_id} {field_path!r} is a list; name one item of it')
    if carrier is None:
        raise RefError('tour-ref-unsourced',
                       f'{entity_id} {field_path!r} does not sit under a sourced value')
    text = _value_text(node)
    # The carrier's quote is the evidence the sentence rests on, so a number it
    # states counts as agreeing too ("since 1970" under a field whose value is a goal).
    candidates = _node_candidates(node) + _numbers_in(text) + _numbers_in(_text(carrier.get('quote')))
    return Resolved(entity_id, field_path, node, carrier, text, candidates)


# ---------------------------------------------------------------------------
# Safe arithmetic for a question's worked answer
# ---------------------------------------------------------------------------

_BINARY = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
           ast.Div: operator.truediv, ast.Pow: operator.pow}
_FUNCTIONS = {'sqrt': math.sqrt, 'log10': math.log10, 'ln': math.log, 'asin': math.asin}


def evaluate(expression: str, names: dict[str, float]) -> float:
    """Evaluate `+ - * / **`, parentheses, names, `pi` and sqrt/asin/log10/ln; nothing else."""
    def walk(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant) and _is_number(node.value):
            return float(node.value)
        if isinstance(node, ast.Name):
            if node.id in names:
                return names[node.id]
            if node.id == 'pi':
                return math.pi
            raise ValueError(f'unknown name {node.id!r}')
        if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
            return _BINARY[type(node.op)](walk(node.left), walk(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            value = walk(node.operand)
            return -value if isinstance(node.op, ast.USub) else value
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in _FUNCTIONS and len(node.args) == 1 and not node.keywords):
            return _FUNCTIONS[node.func.id](walk(node.args[0]))
        raise ValueError(f'unsupported syntax: {ast.dump(node)[:60]}')

    return walk(ast.parse(expression, mode='eval'))


def round_sig(value: float, digits: int) -> float:
    if value == 0:
        return 0.0
    return float(f'{value:.{digits - 1}e}')


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class _Checker:
    def __init__(self, atlas: Any, tour: dict, build_date: _dt.date) -> None:
        self.atlas = atlas
        self.tour = tour
        self.build_date = build_date
        self.issues: list[Issue] = []
        self.own_sources: set[str] = set()

    def add(self, level: str, rule: str, pointer: str, message: str) -> None:
        self.issues.append(Issue(level, rule, pointer, message))

    def error(self, rule: str, pointer: str, message: str) -> None:
        self.add(ERROR, rule, pointer, message)

    def warn(self, rule: str, pointer: str, message: str) -> None:
        self.add(WARNING, rule, pointer, message)

    # -- sources -----------------------------------------------------------
    def source(self, source_id: Any) -> dict | None:
        record = self.atlas.get(source_id) if isinstance(source_id, str) else None
        return record if record is not None and schema.id_type(source_id) == 'source' else None

    def best_rank(self, source_ids: Iterable[str]) -> int | None:
        ranks = [schema.source_rank(s.get('source_type')) for s in map(self.source, source_ids) if s]
        ranks = [r for r in ranks if r is not None]
        return min(ranks) if ranks else None

    # -- claims ------------------------------------------------------------
    def check_claims(self, claims: Any, base: tuple, host_texts: dict[str, str],
                     *, what: str) -> list[tuple[str, str, dict]]:
        """Check a `claims` list; return `(host, covers, claim)` of the valid ones.

        `host_texts` maps the text a claim may cover (``"text"``, ``"prompt"``,
        ``"answer"``) to its string; a claim names the host with `in` (default:
        the only host there is, or ``text``).
        """
        out: list[tuple[str, str, dict]] = []
        if not isinstance(claims, list) or not claims:
            self.error('tour-claims-missing', _pointer(*base),
                       f'{what} needs at least one claim: every statement of fact is a sourced '
                       f'value or a reference to a sourced field')
            return out
        for index, claim in enumerate(claims):
            pointer = base + (index,)
            if not isinstance(claim, dict):
                self.error('tour-claim-shape', _pointer(*pointer), 'a claim is an object')
                continue
            covers = _text(claim.get('covers'))
            host = claim.get('in') or ('text' if 'text' in host_texts else next(iter(host_texts)))
            if not covers:
                self.error('tour-claim-covers', _pointer(*pointer, 'covers'),
                           '`covers` must name the phrase of the text this claim supports')
                continue
            if host not in host_texts:
                self.error('tour-claim-covers', _pointer(*pointer, 'in'),
                           f'`in` must be one of {sorted(host_texts)}, got {host!r}')
                continue
            if covers not in host_texts[host]:
                self.error('tour-claim-covers', _pointer(*pointer, 'covers'),
                           f'`covers` {covers!r} is not a verbatim phrase of the {host}')
                continue
            if 'ref' in claim:
                candidates = self.check_ref_claim(claim, pointer)
            else:
                candidates = self.check_own_claim(claim, pointer)
            if candidates is None:
                continue
            bad = [tok for tok, _s, _e in number_tokens(covers) if not number_matches(tok, candidates)]
            if bad:
                self.error('tour-claim-number-mismatch', _pointer(*pointer, 'covers'),
                           f'{covers!r}: the number(s) {", ".join(bad)} do not agree with '
                           f'{"the referenced value" if "ref" in claim else "the quote"}')
            out.append((host, covers, claim))
        return out

    def check_ref_claim(self, claim: dict, pointer: tuple) -> list[float] | None:
        extra = sorted(set(claim) - {'covers', 'in', 'ref', 'field', 'note'})
        if extra:
            self.error('tour-claim-shape', _pointer(*pointer),
                       f'a reference claim takes `covers`, `ref`, `field` (and `in`, `note`); got {extra}')
        try:
            resolved = resolve(self.atlas, claim.get('ref'), claim.get('field'))
        except RefError as exc:
            self.error(exc.rule, _pointer(*pointer), exc.message)
            return None
        rank = self.best_rank(resolved.sources)
        if rank is not None and rank > schema.VERIFIED_MAX_RANK:
            self.error('tour-ref-weak-source', _pointer(*pointer),
                       f'{resolved.entity_id} {resolved.field!r} rests only on sources of rank '
                       f'{rank} (encyclopaedias and the like); a tour may not lean on it. Cite the '
                       f'primary source as an own claim')
        elif resolved.carrier.get('confidence') not in (None, 'verified'):
            self.warn('tour-ref-not-verified', _pointer(*pointer),
                      f'{resolved.entity_id} {resolved.field!r} is `{resolved.carrier.get("confidence")}`, '
                      f'not verified; say so in the sentence or choose another field')
        return resolved.candidates

    def check_own_claim(self, claim: dict, pointer: tuple) -> list[float] | None:
        allowed = {'covers', 'in', 'quote', 'locator', 'sources', 'confidence', 'verified_at', 'note'}
        extra = sorted(set(claim) - allowed)
        if extra:
            self.error('tour-claim-shape', _pointer(*pointer), f'unknown claim key(s) {extra}')
        quote = _text(claim.get('quote'))
        if not quote:
            self.error('tour-quote-empty', _pointer(*pointer, 'quote'),
                       'an own claim needs a verbatim, non-empty `quote`')
        if not _text(claim.get('locator')):
            self.error('tour-locator-empty', _pointer(*pointer, 'locator'),
                       'an own claim needs a `locator` (section, page, table)')
        sources = claim.get('sources')
        if not isinstance(sources, list) or not sources:
            self.error('tour-claim-sources', _pointer(*pointer, 'sources'),
                       'an own claim must cite at least one source')
            sources = []
        for index, source_id in enumerate(sources):
            if self.source(source_id) is None:
                self.error('tour-claim-sources', _pointer(*pointer, 'sources', index),
                           f'{source_id!r} is not a source in the Atlas')
        self.own_sources.update(s for s in sources if isinstance(s, str))
        if claim.get('confidence') not in schema.CONFIDENCES:
            self.error('tour-claim-confidence', _pointer(*pointer, 'confidence'),
                       f'`confidence` must be one of {list(schema.CONFIDENCES)}')
        verified_at = claim.get('verified_at')
        try:
            parsed = schema.parse_date(verified_at)
        except schema.DateError:
            parsed = None
        if parsed is None or parsed.precision != 'day':
            self.error('tour-claim-verified-at', _pointer(*pointer, 'verified_at'),
                       '`verified_at` must be the day (YYYY-MM-DD) the source was read')
        if not quote:
            return None
        return _numbers_in(quote)

    # -- one text ----------------------------------------------------------
    def check_coverage(self, text: str, covered: list[tuple[str, str]], base: tuple, host: str,
                       *, extra_numbers: Iterable[float] = ()) -> None:
        """Every sentence has a covered phrase; every number sits inside one."""
        extra_numbers = list(extra_numbers)
        spans: list[tuple[int, int]] = []
        for phrase in {phrase for h, phrase in covered if h == host}:
            start = text.find(phrase)
            while start != -1:
                spans.append((start, start + len(phrase)))
                start = text.find(phrase, start + 1)
        offset = 0
        for sentence in sentences(text):
            first = text.find(sentence, offset)
            offset = first + len(sentence)
            inside = sorted((s, e) for s, e in spans if first <= s and e <= first + len(sentence))
            if not inside:
                # A line of arithmetic is its own evidence: every number in it is one of
                # the calculation's inputs, intermediate values or results.
                tokens = [t for t, _s, _e in number_tokens(sentence)]
                if tokens and all(number_matches(t, extra_numbers) for t in tokens):
                    continue
                self.error('tour-sentence-uncovered', _pointer(*base),
                           f'no claim covers any phrase of the sentence {sentence!r}')
                continue
            covered_chars, reach = 0, first
            for s, e in inside:
                covered_chars += max(0, e - max(s, reach))
                reach = max(reach, e)
            if host == 'text' and covered_chars < THIN_COVERAGE * len(sentence):
                self.warn('tour-sentence-thin', _pointer(*base),
                          f'claims cover {covered_chars} of the {len(sentence)} characters of '
                          f'{sentence!r}; widen a `covers` phrase or add a claim for the rest')
        extra = list(extra_numbers)
        for token, start, end in number_tokens(text):
            if any(s <= start and end <= e for s, e in spans):
                continue
            if extra and number_matches(token, extra):
                continue
            self.error('tour-number-uncovered', _pointer(*base),
                       f'the number {token!r} in the {host} is not inside any claim\'s `covers` phrase')

    # -- steps -------------------------------------------------------------
    def check_step(self, index: int, step: Any, seen_ids: set[str]) -> None:
        base = ('steps', index)
        if not isinstance(step, dict):
            self.error('tour-step-shape', _pointer(*base), 'a step is an object')
            return
        step_id = step.get('id')
        if not isinstance(step_id, str) or not _SLUG_RE.match(step_id):
            self.error('tour-step-id', _pointer(*base, 'id'), 'a step id is a lower-case `-` slug')
        elif step_id in seen_ids:
            self.error('tour-step-id', _pointer(*base, 'id'), f'duplicate step id {step_id!r}')
        else:
            seen_ids.add(step_id)
        title = _text(step.get('title'))
        if not title:
            self.error('tour-step-title', _pointer(*base, 'title'), 'every step needs a `title`')
        text = _text(step.get('text'))
        if not text:
            self.error('tour-step-text', _pointer(*base, 'text'), 'every step needs `text`')
        else:
            count = len(sentences(text))
            if count > SENTENCES_MAX:
                self.error('tour-text-length', _pointer(*base, 'text'),
                           f'a step has one or two sentences; this one has {count}')
            if len(text) > 420:
                self.warn('tour-text-length', _pointer(*base, 'text'),
                          f'{len(text)} characters is long for a step on a phone')
        for token, _s, _e in number_tokens(title):
            if token not in text:
                self.error('tour-number-uncovered', _pointer(*base, 'title'),
                           f'the number {token!r} in the title does not appear in the text')

        claims = self.check_claims(step.get('claims'), base + ('claims',), {'text': text} if text else {'text': ''},
                                   what=f'step {step_id or index}')
        if text:
            self.check_coverage(text, [(h, c) for h, c, _ in claims], base + ('text',), 'text')

        self.check_placement(base, step)
        if 'question' in step and step['question'] is not None:
            self.check_question(base + ('question',), step['question'])

    def check_placement(self, base: tuple, step: dict) -> None:
        camera = step.get('camera')
        if camera is not None:
            ok = isinstance(camera, dict) and set(camera) == {'lat', 'lng', 'altitude'} \
                and all(_is_number(camera[k]) for k in camera)
            if not ok:
                self.error('tour-camera', _pointer(*base, 'camera'),
                           '`camera` is {"lat", "lng", "altitude"}, all numbers')
            else:
                if not -90 <= camera['lat'] <= 90 or not -180 <= camera['lng'] <= 180:
                    self.error('tour-camera', _pointer(*base, 'camera'),
                               'camera lat/lng out of range')
                if not ALTITUDE_RANGE[0] <= camera['altitude'] <= ALTITUDE_RANGE[1]:
                    self.error('tour-camera', _pointer(*base, 'camera', 'altitude'),
                               f'altitude must be within {ALTITUDE_RANGE} globe radii')
        year = step.get('year')
        if year is not None:
            if not isinstance(year, int) or isinstance(year, bool) \
                    or not YEAR_MIN <= year <= self.build_date.year:
                self.error('tour-year', _pointer(*base, 'year'),
                           f'`year` is an integer in {YEAR_MIN}..{self.build_date.year}')
                year = None
        select = step.get('select')
        if select is not None:
            record = self.atlas.get(select) if isinstance(select, str) else None
            if record is None:
                self.error('tour-select', _pointer(*base, 'select'),
                           f'{select!r} does not exist in the Atlas')
            elif schema.id_type(select) not in ROUTABLE_TYPES:
                self.error('tour-select', _pointer(*base, 'select'),
                           f'{select!r} is a {schema.id_type(select)}; the app routes only '
                           f'{list(ROUTABLE_TYPES)}')
            elif year is not None:
                self.check_present(base, select, record, year)
        local_map = step.get('map')
        if local_map is not None:
            if not isinstance(local_map, str) or not self.atlas.has(f'map:{local_map}'):
                self.error('tour-map', _pointer(*base, 'map'),
                           f'`map` is the slug of a local map; there is no map:{local_map}')
        view = step.get('view')
        if view is not None:
            if not isinstance(view, dict) or set(view) != {'name', 'arg'}:
                self.error('tour-view', _pointer(*base, 'view'), '`view` is {"name", "arg"}')
            elif view['name'] not in VIEW_NAMES:
                self.error('tour-view', _pointer(*base, 'view', 'name'),
                           f'view name {view["name"]!r} is not one of {list(VIEW_NAMES)}')
            elif view['name'] == 'beam-section' and not self.atlas.has(f'beamline:{view["arg"]}'):
                self.warn('tour-view-arg', _pointer(*base, 'view', 'arg'),
                          f'beam-section takes a beamline slug; there is no beamline:{view["arg"]}')

    def check_present(self, base: tuple, entity_id: str, record: dict, year: int) -> None:
        """A selection the timeline hides at `year` would open a blank view."""
        kind = schema.id_type(entity_id)
        if record.get('intervals'):
            if schema.state_at(record, str(year), build_date=self.build_date) is None:
                self.error('tour-select-absent-at-year', _pointer(*base, 'select'),
                           f'{entity_id} does not exist in {year}, so the timeline would hide it')
        elif kind == 'result':
            date = record.get('date')
            date = date.get('value') if isinstance(date, dict) else date
            low = schema.lo(date)
            if low is not None and low.year > year:
                self.error('tour-select-absent-at-year', _pointer(*base, 'select'),
                           f'{entity_id} is dated {date}, after {year}')

    # -- questions ---------------------------------------------------------
    def check_question(self, base: tuple, question: Any) -> None:
        if not isinstance(question, dict):
            self.error('tour-question-shape', _pointer(*base), 'a question is an object')
            return
        prompt, answer = _text(question.get('prompt')), _text(question.get('answer'))
        if not prompt:
            self.error('tour-question-shape', _pointer(*base, 'prompt'), 'a question needs a `prompt`')
        if not answer:
            self.error('tour-question-shape', _pointer(*base, 'answer'), 'a question needs a worked `answer`')
        extra = sorted(set(question) - {'prompt', 'answer', 'claims', 'calculation'})
        if extra:
            self.error('tour-question-shape', _pointer(*base), f'unknown question key(s) {extra}')
        hosts = {'prompt': prompt, 'answer': answer}
        claims = self.check_claims(question.get('claims'), base + ('claims',), hosts, what='a question')
        covered = [(h, c) for h, c, _ in claims]
        numbers, lines = self.check_calculation(base + ('calculation',), question.get('calculation'),
                                                answer)
        if prompt:
            self.check_coverage_prompt(prompt, covered, base + ('prompt',), numbers)
        if answer:
            self.check_coverage(answer, covered, base + ('answer',), 'answer', extra_numbers=numbers)
            if lines:
                final = lines[-1]
                shown = [t for t, _s, _e in number_tokens(answer) if number_matches(t, [final])]
                if not shown:
                    self.error('tour-answer-result', _pointer(*base, 'answer'),
                               f'the answer never states the calculated result {final:g}')

    def check_coverage_prompt(self, prompt: str, covered: list[tuple[str, str]], base: tuple,
                              numbers: list[float]) -> None:
        spans: list[tuple[int, int]] = []
        for host, phrase in covered:
            if host == 'prompt':
                start = prompt.find(phrase)
                while start != -1:
                    spans.append((start, start + len(phrase)))
                    start = prompt.find(phrase, start + 1)
        for token, start, end in number_tokens(prompt):
            if not any(s <= start and end <= e for s, e in spans) and not number_matches(token, numbers):
                self.error('tour-number-uncovered', _pointer(*base),
                           f'the number {token!r} in the prompt is not inside any claim\'s `covers` phrase')

    def check_calculation(self, base: tuple, calc: Any, answer: str) -> tuple[list[float], list[float]]:
        """Verify a worked calculation; return its numbers and its line values."""
        if calc is None:
            return [], []
        if not isinstance(calc, list) or not calc:
            self.error('tour-calc', _pointer(*base), '`calculation` is a non-empty list of lines')
            return [], []
        names: dict[str, float] = {}
        numbers: list[float] = []
        values: list[float] = []
        for index, line in enumerate(calc):
            pointer = base + (index,)
            if not isinstance(line, dict) or not isinstance(line.get('name'), str) \
                    or not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', line['name']):
                self.error('tour-calc', _pointer(*pointer), 'a calculation line has an identifier `name`')
                continue
            name = line['name']
            if name in names:
                self.error('tour-calc', _pointer(*pointer, 'name'), f'{name!r} is defined twice')
                continue
            unit = line.get('unit')
            if 'expression' in line:
                digits = line.get('digits')
                if not isinstance(digits, int) or not 1 <= digits <= 6 or not _is_number(line.get('value')):
                    self.error('tour-calc', _pointer(*pointer),
                               'a computed line needs `value` and `digits` (significant digits, 1-6)')
                    continue
                try:
                    result = evaluate(str(line['expression']), names)
                except (ValueError, ZeroDivisionError, SyntaxError, OverflowError) as exc:
                    self.error('tour-calc', _pointer(*pointer, 'expression'), f'cannot evaluate: {exc}')
                    continue
                if not math.isclose(round_sig(result, digits), float(line['value']), rel_tol=1e-9):
                    self.error('tour-calc-result', _pointer(*pointer, 'value'),
                               f'{line["expression"]} = {result:.6g}, which is {round_sig(result, digits):g} '
                               f'to {digits} significant digit(s), not {line["value"]}')
                names[name] = result
                numbers.extend(_numbers_in(str(line['expression'])))
                numbers.append(float(line['value']))
                values.append(float(line['value']))
            elif 'ref' in line:
                try:
                    resolved = resolve(self.atlas, line.get('ref'), line.get('field'))
                except RefError as exc:
                    self.error(exc.rule, _pointer(*pointer), exc.message)
                    continue
                node = resolved.node
                if 'number' in line:
                    # A number the record states in words or in its quote ("sqrt(s)=540 GeV"):
                    # the literal token must be there, the unit is the author's label.
                    token = str(line['number'])
                    stated = _numbers_in(resolved.text) + _numbers_in(_text(resolved.carrier.get('quote')))
                    if not _NUMBER_RE.fullmatch(token) or not number_matches(token, stated):
                        self.error('tour-calc', _pointer(*pointer, 'number'),
                                   f'{token!r} is not a number the referenced value or its quote states')
                        continue
                    if not isinstance(line.get('unit'), str):
                        self.error('tour-calc', _pointer(*pointer, 'unit'),
                                   'name the unit of the number ("" for a pure number)')
                        continue
                    rank = self.best_rank(resolved.sources)
                    if rank is not None and rank > schema.VERIFIED_MAX_RANK:
                        self.error('tour-ref-weak-source', _pointer(*pointer),
                                   f'{resolved.entity_id} {resolved.field!r} rests only on rank {rank} sources')
                    names[name] = _token_value(token)
                    numbers.append(_token_value(token))
                    numbers.extend(resolved.candidates)
                    values.append(_token_value(token))
                    continue
                if not (isinstance(node, dict) and schema.is_quantity(node)):
                    self.error('tour-calc', _pointer(*pointer),
                               'an input taken from the Atlas must be a quantity (a number with a unit) '
                               'or name a stated number with `number`')
                    continue
                if line.get('unit'):
                    scale = schema.unit_scale(node.get('dimension'), line['unit'])
                    magnitude = schema.quantity_magnitude(node)
                    if scale is None or magnitude is None:
                        self.error('tour-calc', _pointer(*pointer, 'unit'),
                                   f'{line["unit"]!r} is not a {node.get("dimension")} unit')
                        continue
                    value = magnitude / scale
                elif _is_number(node.get('value')):
                    value = float(node['value'])
                else:
                    self.error('tour-calc', _pointer(*pointer), 'a range cannot be an input; name the value')
                    continue
                rank = self.best_rank(resolved.sources)
                if rank is not None and rank > schema.VERIFIED_MAX_RANK:
                    self.error('tour-ref-weak-source', _pointer(*pointer),
                               f'{resolved.entity_id} {resolved.field!r} rests only on rank {rank} sources')
                names[name] = value
                numbers.extend(resolved.candidates)
                values.append(value)
            elif 'value' in line:
                allowed = {'name', 'value', 'unit', 'quote', 'locator', 'sources', 'confidence',
                           'verified_at', 'note'}
                if sorted(set(line) - allowed):
                    self.error('tour-calc', _pointer(*pointer), f'unknown key(s) {sorted(set(line) - allowed)}')
                if not _is_number(line['value']):
                    self.error('tour-calc', _pointer(*pointer, 'value'), '`value` must be a number')
                    continue
                candidates = self.check_own_claim(
                    {k: v for k, v in line.items() if k not in ('name', 'value', 'unit')}, pointer)
                if candidates is not None and not number_matches(f'{line["value"]:g}', candidates) \
                        and not number_matches(str(line['value']), candidates):
                    self.error('tour-claim-number-mismatch', _pointer(*pointer, 'value'),
                               f'the constant {line["value"]} is not a number in its quote')
                names[name] = float(line['value'])
                numbers.append(float(line['value']))
                values.append(float(line['value']))
            else:
                self.error('tour-calc', _pointer(*pointer),
                           'a line is an Atlas input (`ref`/`field`), a sourced constant (`value` with '
                           'a quote) or a computed line (`expression`)')
        return numbers, values

    # -- the tour ----------------------------------------------------------
    def run(self) -> list[Issue]:
        tour = self.tour
        if tour.get('type') != 'tour':
            self.error('tour-shape', _pointer('type'), '`type` must be "tour"')
        for key in ('name', 'summary', 'audience'):
            if not _text(tour.get(key)):
                self.error('tour-shape', _pointer(key), f'`{key}` must be a non-empty string')
        minutes = tour.get('estimated_minutes')
        if not isinstance(minutes, int) or isinstance(minutes, bool) or not 1 <= minutes <= MINUTES_MAX:
            self.error('tour-shape', _pointer('estimated_minutes'),
                       f'`estimated_minutes` is an integer 1..{MINUTES_MAX}')
        steps = tour.get('steps')
        if not isinstance(steps, list):
            self.error('tour-shape', _pointer('steps'), '`steps` must be a list')
            return self.issues
        if not STEP_MIN <= len(steps) <= STEP_MAX:
            self.error('tour-step-count', _pointer('steps'),
                       f'a tour has {STEP_MIN}-{STEP_MAX} steps; this one has {len(steps)}')
        seen: set[str] = set()
        questions = 0
        for index, step in enumerate(steps):
            self.check_step(index, step, seen)
            if isinstance(step, dict) and step.get('question') is not None:
                questions += 1
        if not QUESTION_MIN <= questions <= QUESTION_MAX:
            self.error('tour-question-count', _pointer('steps'),
                       f'a tour has {QUESTION_MIN}-{QUESTION_MAX} questions; this one has {questions}')
        listed = {s for s in tour.get('sources') or [] if isinstance(s, str)}
        for missing in sorted(self.own_sources - listed):
            self.error('tour-sources-incomplete', _pointer('sources'),
                       f'a claim cites {missing}, which the tour\'s `sources` does not list')
        for unused in sorted(listed - self.own_sources):
            self.warn('tour-source-unused', _pointer('sources'),
                      f'{unused} is listed in `sources` but no claim of this tour cites it')
        return self.issues


def validate_tour(atlas: Any, tour: dict, build_date: Any = None) -> list[Issue]:
    """Every A28 finding for one tour record (generic checks run elsewhere)."""
    day = schema.as_date(build_date) or _dt.date.today()
    return _Checker(atlas, tour, day).run()


# ---------------------------------------------------------------------------
# The `tours.json` bundle
# ---------------------------------------------------------------------------

def step_href(step: dict) -> str:
    """The Atlas URL (relative to the app's own path) that shows this step's view.

    A view beats a map beats a selection, because the app has one route at a
    time; the year rides along as ``?y=`` and, on a map, the selection as ``sel=``.  `state.js` is the grammar:
    ``#/<type>/<slug>``, ``#/map/<slug>``, and the future ``#/view/<name>/<arg>``.
    """
    year = step.get('year')
    query = f'?y={year}' if isinstance(year, int) else ''
    view, local_map, select = step.get('view'), step.get('map'), step.get('select')
    if isinstance(view, dict):
        return f"{query}#/view/{view['name']}/{view['arg']}"
    if local_map:
        # On a map route the selection is the `sel` parameter (an entity id), as in localmap.js.
        if select:
            query += ('&' if query else '?') + 'sel=' + _urlquote(str(select), safe='')
        return f'{query}#/map/{local_map}'
    if select:
        kind, slug = str(select).split(':', 1)
        return f'{query}#/{kind}/{slug}'
    return query


def _resolved_claim(atlas: Any, claim: dict) -> dict:
    if 'ref' not in claim:
        return {key: claim[key] for key in ('covers', 'in', 'quote', 'locator', 'sources', 'confidence',
                                            'verified_at', 'note') if claim.get(key) not in (None, '')}
    resolved = resolve(atlas, claim['ref'], claim['field'])
    out = {'covers': claim['covers'], 'ref': claim['ref'], 'field': claim['field'],
           'value': resolved.text, 'sources': resolved.sources}
    if claim.get('in'):
        out['in'] = claim['in']
    for key in ('quote', 'locator', 'confidence'):
        if resolved.carrier.get(key):
            out[key] = resolved.carrier[key]
    return out


def _resolved_question(atlas: Any, question: dict) -> dict:
    out = {'prompt': question['prompt'], 'answer': question['answer'],
           'claims': [_resolved_claim(atlas, c) for c in question.get('claims') or []]}
    calc = []
    for line in question.get('calculation') or []:
        row = {key: line[key] for key in ('name', 'expression', 'value', 'unit', 'digits') if key in line}
        if 'ref' in line:
            resolved = resolve(atlas, line['ref'], line['field'])
            row.update({'ref': line['ref'], 'field': line['field'], 'sources': resolved.sources})
            node = resolved.node
            if 'number' in line:
                row['value'] = _token_value(str(line['number']))
            else:
                scale = schema.unit_scale(node.get('dimension'), line.get('unit')) if line.get('unit') else None
                magnitude = schema.quantity_magnitude(node)
                row['value'] = (magnitude / scale) if scale and magnitude is not None else node.get('value')
            row['display'] = resolved.text
        elif 'value' in line:
            row.update({key: line[key] for key in ('quote', 'locator', 'sources', 'confidence',
                                                   'verified_at', 'note') if line.get(key) not in (None, '')})
        calc.append(row)
    if calc:
        out['calculation'] = calc
    return out


def build_bundle(atlas: Any, build_date: str) -> tuple[dict, list[str]]:
    """`tours.json`: every tour, its references resolved, plus any build errors.

    The bundle is self-contained: a player needs no other file to show a step
    and its evidence (it loads `sources.json` only to turn a source id into a
    title).  A reference that no longer resolves is a build error, not a hole.
    """
    errors: list[str] = []
    tours: dict[str, dict] = {}
    for tour_id in sorted(atlas.by_type('tour')):
        tour = atlas.by_type('tour')[tour_id]
        steps = []
        used = set(tour.get('sources') or [])
        for index, step in enumerate(tour.get('steps') or []):
            try:
                out = {key: step[key] for key in ('id', 'title', 'text') if key in step}
                out['claims'] = [_resolved_claim(atlas, c) for c in step.get('claims') or []]
                for key in ('camera', 'year', 'select', 'map', 'view'):
                    if step.get(key) is not None:
                        out[key] = step[key]
                href = step_href(step)
                if href:
                    out['href'] = href
                if step.get('question'):
                    out['question'] = _resolved_question(atlas, step['question'])
            except (RefError, KeyError, TypeError) as exc:
                errors.append(f'{tour_id} steps[{index}]: {getattr(exc, "message", exc)}')
                continue
            for claim in out['claims'] + out.get('question', {}).get('claims', []):
                used.update(claim.get('sources') or [])
            steps.append(out)
        tours[tour_id] = {
            'id': tour_id, 'name': tour.get('name'), 'summary': tour.get('summary'),
            'audience': tour.get('audience'), 'estimated_minutes': tour.get('estimated_minutes'),
            'sources': sorted(used), 'steps': steps,
        }
    order = sorted(tours, key=lambda tid: (atlas.by_type('tour')[tid].get('order') or 1 << 30, tid))
    return {'schema': schema.SCHEMA_TAG, 'build_date': build_date, 'order': order, 'tours': tours}, errors


# ---------------------------------------------------------------------------
# Authoring aid
# ---------------------------------------------------------------------------

def referenceable(record: dict) -> Iterable[tuple[str, dict]]:
    """`(field path, sourced node)` for every field of a record a claim may reference."""
    def walk(node: Any, path: list[str]) -> Iterable[tuple[str, dict]]:
        if isinstance(node, dict):
            if path and node.get('sources') and not (len(path) == 1 and path[0] == 'sources'):
                yield '.'.join(path), node
            for key, value in node.items():
                if key in schema.PROVENANCE_KEYS or key in ('summary', 'external', 'coverage'):
                    continue
                yield from walk(value, path + [key])
        elif isinstance(node, list):
            for index, row in enumerate(node):
                label = None
                if isinstance(row, dict):
                    label = next((row[k] for k in _ROW_KEYS if isinstance(row.get(k), str)), None)
                yield from walk(row, path + [label if label and '.' not in label else str(index)])
    yield from walk(record, [])


def review_text(atlas: Any, tour: dict) -> str:
    """The tour as a reviewer reads it: each sentence, then the evidence under it."""
    lines = [f'{tour.get("id")}  {tour.get("name")}  ({tour.get("estimated_minutes")} min)',
             f'  {tour.get("summary")}']

    def evidence(claims: Iterable[dict]) -> None:
        for claim in claims:
            if 'ref' in claim:
                try:
                    resolved = resolve(atlas, claim['ref'], claim['field'])
                    node = resolved.carrier
                    lines.append(f'      [{claim["covers"]}]  = {claim["ref"]} {claim["field"]}: {resolved.text}')
                    lines.append(f'          quote: {node.get("quote") or node.get("locator")}  '
                                 f'({", ".join(resolved.sources)}; {node.get("confidence")})')
                except RefError as exc:
                    lines.append(f'      [{claim["covers"]}]  UNRESOLVED {exc.message}')
            else:
                lines.append(f'      [{claim.get("covers")}]  OWN  {claim.get("quote")}')
                lines.append(f'          {claim.get("locator")}  ({", ".join(claim.get("sources") or [])}; '
                             f'{claim.get("confidence")}, read {claim.get("verified_at")})')

    for index, step in enumerate(tour.get('steps') or [], 1):
        place = ' '.join(f'{k}={step[k]}' for k in ('year', 'select', 'map', 'view') if step.get(k))
        lines.append(f'{index}. {step.get("title")}  [{place}]')
        lines.append(f'   {step.get("text")}')
        evidence(step.get('claims') or [])
        question = step.get('question')
        if question:
            lines.append(f'   Q: {question.get("prompt")}')
            lines.append(f'   A: {question.get("answer")}')
            evidence(question.get('claims') or [])
            for row in question.get('calculation') or []:
                lines.append(f'      calc {row}')
    return '\n'.join(lines)


def main(argv: list[str] | None = None) -> int:
    """`python -m hepgraph.atlas.tours show <entity-id> <field>`: what a reference reads."""
    import argparse
    from . import load
    parser = argparse.ArgumentParser(prog='python -m hepgraph.atlas.tours')
    sub = parser.add_subparsers(dest='command', required=True)
    show = sub.add_parser('show', help='resolve one reference and print the value and its provenance')
    show.add_argument('entity_id')
    show.add_argument('field')
    listing = sub.add_parser('fields', help='list every field of a record a claim may reference')
    listing.add_argument('entity_id')
    review = sub.add_parser('review', help='print a tour beside the evidence under each sentence')
    review.add_argument('tour_id', help='tour id or slug')
    args = parser.parse_args(argv)
    atlas = load.load_atlas()
    if args.command == 'review':
        tour_id = args.tour_id if args.tour_id.startswith('tour:') else f'tour:{args.tour_id}'
        tour = atlas.get(tour_id)
        if tour is None:
            print(f'{tour_id}: not in the Atlas')
            return 1
        print(review_text(atlas, tour))
        return 0
    if args.command == 'fields':
        record = atlas.get(args.entity_id)
        if record is None:
            print(f'{args.entity_id}: not in the Atlas')
            return 1
        for path, node in referenceable(record):
            body = _value_text(node)
            quote = _text(node.get('quote'))
            rank = min([r for r in (schema.source_rank((atlas.get(s) or {}).get('source_type'))
                                    for s in node.get('sources') or []) if r is not None], default='?')
            print(f'{path} | {body[:110]} | {node.get("confidence")} r{rank}')
            if quote:
                print(f'      quote: {quote[:200]}')
        return 0
    try:
        resolved = resolve(atlas, args.entity_id, args.field)
    except RefError as exc:
        print(f'{exc.rule}: {exc.message}')
        return 1
    carrier = resolved.carrier
    print(f'value      : {resolved.text}')
    print(f'sources    : {", ".join(resolved.sources)}')
    print(f'confidence : {carrier.get("confidence")}')
    print(f'locator    : {carrier.get("locator")}')
    print(f'quote      : {carrier.get("quote")}')
    return 0


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
