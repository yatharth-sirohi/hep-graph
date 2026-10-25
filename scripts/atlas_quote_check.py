#!/usr/bin/env python3
"""Check that every HEP Atlas `quote` really appears in the source it cites.

For each object under data/atlas (excluding sources/) that carries a non-empty
`quote` the script fetches the cited source once, normalises both sides and
classifies the quote:

  verbatim     normalised substring of the source text
  segments     split on "..." / "…", every segment >= 12 chars is present
  near         best sliding-window token overlap >= 0.85 (not verbatim)
  missing      fetched, not found
  unfetchable  HTTP error, blocked or empty text (cannot decide)
  skipped      geocoder sources and inspirehep.net URLs (never fetched here)

Independently, a quote sitting next to a numeric `value`/`min`/`max` is flagged
`number-not-in-quote` when that number cannot be found in the quote text
(thousands separators, scientific notation, number words and SI-prefix/percent
rescalings are tolerated).

Raw bytes of every fetched URL are cached by URL hash, failures included, so
reruns cost nothing and no URL is requested twice (use --retry-failed to retry).

    python scripts/atlas_quote_check.py --cache DIR --json OUT.json
"""
from __future__ import annotations

import argparse
import collections
import concurrent.futures as cf
import gzip
import hashlib
import html
import html.parser
import http.cookiejar
import json
import math
import re
import subprocess
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ATLAS = ROOT / "data" / "atlas"
REPORT = ROOT / "docs" / "atlas-worklog" / "RELEASE_QUOTE_CHECK.md"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
PDFTOTEXT = "/opt/homebrew/bin/pdftotext"
TIMEOUT, WORKERS, MAX_BYTES = 30, 4, 200 * 1024 * 1024
HOST_GAP = {"arxiv.org": 1.5, "web.archive.org": 3.0}  # seconds between requests to one host (default 1)
HOST_UA = {"web.archive.org": "HEP-Atlas-quote-check/1.0 (research script)"}  # archive.org rate-limits browser UAs
NEAR_THRESHOLD, SEGMENT_MIN = 0.85, 12
CLASS_ORDER = ["verbatim", "segments", "near", "missing", "unfetchable", "skipped"]


# ---------------------------------------------------------------- collection

def collect_quotes(atlas: Path = ATLAS) -> list[dict]:
    """Every dict with a non-empty `quote`: file, pointer, sources, numbers."""
    items = []

    def walk(obj, ptr, f, inherited):
        if isinstance(obj, dict):
            own = obj.get("sources") if isinstance(obj.get("sources"), list) else None
            quote = obj.get("quote")
            if isinstance(quote, str) and quote.strip():
                nums = {k: obj[k] for k in ("value", "min", "max")
                        if isinstance(obj.get(k), (int, float)) and not isinstance(obj.get(k), bool)}
                items.append({"file": str(f.relative_to(ROOT)), "pointer": ptr or "/",
                              "type": f.relative_to(atlas).parts[0], "quote": quote,
                              "sources": own if own is not None else inherited,
                              "sources_inherited": own is None, "numbers": nums})
            for k, v in obj.items():
                walk(v, f"{ptr}/{k}", f, own if own is not None else inherited)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk(v, f"{ptr}/{i}", f, inherited)

    for f in sorted(atlas.rglob("*.json")):
        if f.relative_to(atlas).parts[0] == "sources":
            continue
        walk(json.loads(f.read_text()), "", f, [])
    return items


def load_sources(atlas: Path = ATLAS) -> dict[str, dict]:
    return {d["id"]: d for d in (json.loads(f.read_text()) for f in (atlas / "sources").glob("*.json"))}


ARXIV_RE = re.compile(r"arxiv\.org/(?:abs|pdf)/([^?#\s]+?)(?:\.pdf)?(?:v\d+)?/?(?:[?#].*)?$", re.I)


def source_urls(src: dict) -> tuple[list[str], list[str]]:
    """(primary candidates, fallbacks tried only if the primary is unfetchable: the
    record's `archive_url`, then the arXiv copy of the same paper).

    arXiv: the PDF (it contains the abstract) is tried first; the abstract page only
    if some quote is still unresolved, which saves a request per paper."""
    ref = src.get("reference") or {}
    url = src.get("url") or ref.get("url")
    if not url and ref.get("doi"):
        url = f"https://doi.org/{ref['doi']}"
    if not url and ref.get("arxiv"):
        url = f"https://arxiv.org/abs/{ref['arxiv']}"
    if not url:
        return [], []
    m = ARXIV_RE.search(url)
    if m:
        aid = m.group(1)
        return [f"https://arxiv.org/pdf/{aid}", f"https://arxiv.org/abs/{aid}"], []
    fallback = [src["archive_url"]] if src.get("archive_url") else []
    if ref.get("arxiv"):
        aid = str(ref["arxiv"]).replace("arXiv:", "")
        fallback += [f"https://arxiv.org/pdf/{aid}", f"https://arxiv.org/abs/{aid}"]
    return [url], fallback


def skip_reason(src: dict) -> str | None:
    if src.get("source_type") == "geocoder":
        return "geocoder source"
    ref = src.get("reference") or {}
    if "inspirehep.net" in (src.get("url") or "") + (ref.get("url") or ""):
        return "inspirehep.net URL"
    return None


# ------------------------------------------------------------------- fetching

class Fetcher:
    """Cached, throttled fetcher: one request per URL ever, <=1 in flight per host."""

    def __init__(self, cache: Path, retry_failed=False, offline=False, retry_429=False):
        self.cache, self.retry_failed, self.offline, self.retry_429 = cache, retry_failed, offline, retry_429
        cache.mkdir(parents=True, exist_ok=True)
        self.guard = threading.Lock()
        self.host_lock: dict[str, threading.Lock] = collections.defaultdict(threading.Lock)
        self.host_last: dict[str, float] = {}
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def _paths(self, url):
        h = hashlib.sha1(url.encode()).hexdigest()
        return self.cache / f"{h}.raw", self.cache / f"{h}.meta.json", self.cache / f"{h}.txt"

    def get_text(self, url: str) -> tuple[str | None, dict]:
        """Extracted text (None if unfetchable) and the fetch metadata."""
        raw_p, meta_p, txt_p = self._paths(url)
        if meta_p.exists():
            meta = json.loads(meta_p.read_text())
            err = str(meta.get("error"))  # rate limits and the old size cap are not verdicts on the URL
            retry = self.retry_failed or err.startswith("response too large") or (self.retry_429 and err == "HTTP 429")
            if meta.get("error") and retry and not self.offline:
                meta_p.unlink()
            else:
                return (txt_p.read_text() if txt_p.exists() else None), meta
        if self.offline:
            return None, {"url": url, "error": "not cached (offline)"}
        meta = self._download(url, raw_p)
        text = None
        if not meta.get("error"):
            text = extract_text(raw_p.read_bytes(), meta.get("content_type", ""), raw_p)
            if len(text.strip()) < 200:
                meta["error"] = f"empty or near-empty text ({len(text.strip())} chars)"
                text = None
            else:
                txt_p.write_text(text)
        meta_p.write_text(json.dumps(meta, indent=1))
        return text, meta

    def _download(self, url, raw_p):
        host = urllib.parse.urlsplit(url).netloc.lower()
        gap = HOST_GAP.get(host, 1.0)
        with self.guard:
            lock = self.host_lock[host]
        with lock:
            wait = self.host_last.get(host, 0) + gap - time.time()
            if wait > 0:
                time.sleep(wait)
            meta = {"url": url, "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": HOST_UA.get(host, UA), "Accept-Language": "en-US,en;q=0.9",
                    "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate"})
                with self.opener.open(req, timeout=TIMEOUT) as r:
                    body = r.read(MAX_BYTES + 1)
                    enc = (r.headers.get("Content-Encoding") or "").lower()
                    if enc == "gzip":
                        body = gzip.decompress(body)
                    elif enc == "deflate":
                        body = zlib.decompress(body)
                    meta.update(status=r.status, final_url=r.geturl(),
                                content_type=r.headers.get("Content-Type", ""), bytes=len(body))
                    if len(body) > MAX_BYTES:
                        meta["error"] = "response too large"
                    else:
                        raw_p.write_bytes(body)
            except urllib.error.HTTPError as e:
                meta.update(status=e.code, error=f"HTTP {e.code}")
            except Exception as e:  # timeouts, DNS, TLS, resets
                meta["error"] = f"{type(e).__name__}: {e}"[:200]
            self.host_last[host] = time.time()
        return meta


class _TextExtractor(html.parser.HTMLParser):
    BLOCK = {"p", "div", "br", "li", "ul", "ol", "tr", "td", "th", "table", "section", "article",
             "header", "footer", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "pre", "dd", "dt"}
    SKIP = {"script", "style", "noscript", "template", "svg"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag == "meta":
            a = dict(attrs)
            if (a.get("name") or a.get("property") or "").lower() in (
                    "description", "og:description", "citation_abstract", "dc.description") and a.get("content"):
                self.parts.append("\n" + a["content"] + "\n")
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def extract_text(body: bytes, content_type: str, raw_path: Path) -> str:
    if body[:5] == b"%PDF-" or "pdf" in content_type.lower():
        try:
            out = subprocess.run([PDFTOTEXT, "-enc", "UTF-8", str(raw_path), "-"],
                                 capture_output=True, timeout=300)
            return out.stdout.decode("utf-8", "replace")
        except Exception:
            return ""
    charset = re.search(r"charset=([\w-]+)", content_type, re.I) or re.search(rb"charset=[\"']?([\w-]+)", body[:4096], re.I)
    enc = (charset.group(1).decode() if isinstance(charset.group(1), bytes) else charset.group(1)) if charset else "utf-8"
    try:
        s = body.decode(enc, "replace")
    except LookupError:
        s = body.decode("utf-8", "replace")
    parser = _TextExtractor()
    parser.feed(s)
    return html.unescape("".join(parser.parts))


# ------------------------------------------------------------- normalisation

_MAP = str.maketrans({"‘": "'", "’": "'", "‚": "'", "‛": "'", "′": "'", "ʼ": "'", "“": '"', "”": '"',
                      "„": '"', "‟": '"', "″": '"', "–": "-", "—": "-", "―": "-", "‐": "-", "‑": "-",
                      "‒": "-", "−": "-", "⁃": "-", "﹣": "-", "－": "-", "\u00ad": None, "\u200b": None,
                      "\u200c": None, "\u200d": None, "\ufeff": None, "\u2060": None})


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).translate(_MAP).casefold()
    s = re.sub(r"\s*-\s*", "-", s)
    return re.sub(r"\s+", " ", s).strip()


def source_forms(text: str) -> list[str]:
    """Normalised source text with line-break hyphens joined, and with them kept."""
    t = unicodedata.normalize("NFKC", text).translate(_MAP)
    joined = re.sub(r"(?<=\w)-[ \t]*\n\s*(?=\w)", "", t)
    kept = re.sub(r"(?<=\w)-[ \t]*\n\s*(?=\w)", "-", t)
    return [norm(joined), norm(kept)]


GREEK = str.maketrans({"α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta", "ε": "epsilon", "ϵ": "epsilon",
                       "ζ": "zeta", "η": "eta", "θ": "theta", "κ": "kappa", "λ": "lambda", "μ": "mu", "ν": "nu",
                       "ξ": "xi", "π": "pi", "ρ": "rho", "σ": "sigma", "τ": "tau", "φ": "phi", "ϕ": "phi",
                       "χ": "chi", "ψ": "psi", "ω": "omega", "×": "x", "·": None, "⋅": None})
TEX_DROP = r"text|textrm|textit|mathrm|mathit|mathbf|rm|it|bf|left|right|rangle|langle"


def squash(s: str) -> str:
    """Letters and digits only, TeX markup and Greek letters flattened: equal squashes mean the
    two texts differ only in spacing, punctuation, math typesetting or symbol rendering."""
    s = re.sub(r"\\(?:times|cdot)(?![a-z])", "x", unicodedata.normalize("NFKC", s))
    s = re.sub(rf"\\(?:{TEX_DROP})(?![a-z])", "", s)
    s = norm(s.replace("\\", " ")).translate(GREEK)
    return re.sub(r"[^a-z0-9]", "", s)


TOKEN = re.compile(r"\d+(?:[.,]\d+)*|[^\W\d_]+")


def tokens(s: str) -> list[str]:
    return TOKEN.findall(re.sub(r"(?<=\d),(?=\d{3}\b)", "", s))


def best_window(qtoks: list[str], stoks: list[str]) -> tuple[float, str]:
    """Best multiset overlap of qtoks with any len(qtoks)-token window of stoks."""
    n, cq = len(qtoks), collections.Counter(qtoks)
    hits = [(i, t) for i, t in enumerate(stoks) if t in cq]
    cw, matched, best, best_end, j = collections.Counter(), 0, 0, 0, 0
    for i, t in hits:
        if cw[t] < cq[t]:
            matched += 1
        cw[t] += 1
        while hits[j][0] <= i - n:
            t0 = hits[j][1]
            cw[t0] -= 1
            if cw[t0] < cq[t0]:
                matched -= 1
            j += 1
        if matched > best:
            best, best_end = matched, i
    return best / n, " ".join(stoks[max(0, best_end - n + 1): best_end + 1])


class SourceText:
    def __init__(self, text: str):
        self.forms = source_forms(text)
        self.tokens = tokens(self.forms[1])
        self.squashed = squash(text)

    def classify(self, quote: str) -> dict:
        nq = norm(quote)
        if any(nq in f for f in self.forms):
            return {"class": "verbatim"}
        segs = [norm(x) for x in re.split(r"\[\s*(?:\.\.\.|…)\s*\]|\.\.\.|…", unicodedata.normalize("NFKC", quote))]
        segs = [x for x in segs if x]
        long_ = [x for x in segs if len(x) >= SEGMENT_MIN]
        if len(segs) > 1 and long_ and all(any(x in f for f in self.forms) or squash(x) in self.squashed for x in long_):
            return {"class": "segments"}
        sq = squash(quote)
        if len(sq) >= 20 and sq in self.squashed:
            return {"class": "verbatim", "match": "alnum"}
        qt = tokens(nq)
        if len(qt) >= 4:
            score, window = best_window(qt, self.tokens)
            if score >= NEAR_THRESHOLD:
                return {"class": "near", "score": round(score, 3), "window": window}
            return {"class": "missing", "score": round(score, 3), "window": window}
        return {"class": "missing", "score": 0.0}


# ------------------------------------------------------------- number check

WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
    "sixteen seventeen eighteen nineteen twenty".split())}
WORDS.update({"thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80,
              "ninety": 90, "hundred": 100, "dozen": 12, "single": 1, "twin": 2, "pair": 2, "double": 2,
              "half": 0.5, "quarter": 0.25})
SCALES = {"thousand": 1e3, "million": 1e6, "billion": 1e9, "trillion": 1e12}
NUM = r"\d+(?:\.\d+)?"


def numbers_in(text: str) -> list[float]:
    t = unicodedata.normalize("NFKC", text).translate(_MAP).casefold()
    t = re.sub(r"\\times|\\cdot", "×", t).replace("$", "").replace("{", "").replace("}", "")  # LaTeX
    t = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", t)  # 1,585 -> 1585
    # 1 585 -> 1585, but not the gap between two table entries "667.9 451.8" (a decimal before the gap, or after the three digits)
    t = re.sub(r"(?<!\.\d)(?<=\d)[\u2009 ](?=\d{3}(?!\d|\.\d))", "", t)
    out = []
    for m in re.finditer(rf"({NUM})\s*(?:x|\*|×|·|⋅)\s*10\s*\^?\s*\(?\s*([+-]?\d+)\s*\)?", t):
        out.append(float(m.group(1)) * 10 ** int(m.group(2)))
    for m in re.finditer(rf"(?<![\d.])10\s*\^\s*\(?\s*([+-]?\d+)\s*\)?", t):
        out.append(10.0 ** int(m.group(1)))
    for m in re.finditer(rf"({NUM})\s*e\s*([+-]?\d+)\b", t):
        out.append(float(m.group(1)) * 10 ** int(m.group(2)))
    for m in re.finditer(rf"({NUM})(?:\s*(thousand|million|billion|trillion))?", t):
        v = float(m.group(1))
        out.append(v * SCALES[m.group(2)] if m.group(2) else v)
    # "(2.2 +/- 0.7) x 10^-39": a plain number and a power of ten that share a parenthesis or error bar
    exps = [int(m.group(1)) for m in re.finditer(r"(?<![\d.])10\s*\^\s*\(?\s*([+-]?\d+)", t)]
    out += [q * 10.0 ** e for e in exps for q in [float(x) for x in re.findall(NUM, t)] if abs(q) > 0]
    for m in re.finditer(r"\b([a-z]+)(?:[ -]+(thousand|million|billion|trillion))?\b", t):
        if m.group(1) in WORDS:
            out.append(WORDS[m.group(1)] * (SCALES[m.group(2)] if m.group(2) else 1))
    return out


RESCALES = [1.0] + [10.0 ** e for e in (-12, -9, -6, -3, 3, 6, 9, 12, -2, -1, 1, 2)]


IMPERIAL_TO_METRE = (0.3048, 0.0254, 0.9144, 1609.344, 1852.0)  # ft, in, yd, mile, nautical mile


def number_in_quote(value: float, quote: str) -> bool:
    if value == 0:
        return True  # "none"/"zero" phrasing is too varied to police
    for q in numbers_in(quote):
        if q == 0:
            continue
        for r in RESCALES:
            if math.isclose(abs(value), q * r, rel_tol=2e-3) or math.isclose(abs(value), q / r, rel_tol=2e-3):
                return True
        # a value stored in metres whose quote gives feet / miles ("2,150 feet" -> 655 m); figures in feet are
        # rounded, so a 1 % tolerance
        for k in IMPERIAL_TO_METRE:
            if math.isclose(abs(value), q * k, rel_tol=1e-2):
                return True
    return False


def number_flags(item: dict) -> list[str]:
    return [f"{k}={v}" for k, v in item["numbers"].items() if not number_in_quote(v, item["quote"])]


# ------------------------------------------------------------------ pipeline

def check_source(sid: str, src: dict, quotes: list[dict], fetcher: Fetcher) -> dict[int, dict]:
    """Classify each quote (by index) against one source; fetch lazily."""
    reason = skip_reason(src)
    if reason:
        return {i: {"class": "skipped", "note": reason} for i in range(len(quotes))}
    primary, fallback = source_urls(src)
    if not primary:
        return {i: {"class": "unfetchable", "note": "source has no resolvable URL"} for i in range(len(quotes))}
    results: dict[int, dict] = {}
    errors: list[str] = []
    best: dict[int, dict] = {}

    def attempt(urls):
        for url in urls:
            if len(results) == len(quotes):
                return
            text, meta = fetcher.get_text(url)
            if text is None:
                errors.append(f"{url}: {meta.get('error')}")
                continue
            st = SourceText(text)
            for i, q in enumerate(quotes):
                if i in results:
                    continue
                r = dict(st.classify(q), url=url)
                if r["class"] in ("verbatim", "segments"):
                    results[i] = r
                elif i not in best or CLASS_ORDER.index(r["class"]) < CLASS_ORDER.index(best[i]["class"]):
                    best[i] = r

    attempt(primary)
    if fallback and len(errors) == len(primary):  # primary entirely unfetchable
        attempt(fallback)
    for i in range(len(quotes)):
        if i not in results:
            results[i] = best.get(i) or {"class": "unfetchable", "note": "; ".join(errors)}
    return results


def combine(per_source: dict[str, dict]) -> dict:
    """Overall class of one quote over its cited sources."""
    if not per_source:
        return {"class": "unfetchable", "note": "quote cites no source"}
    for cls in ("verbatim", "segments", "near"):
        hit = [(s, r) for s, r in per_source.items() if r["class"] == cls]
        if hit:
            return {"class": cls, "source": hit[0][0], **{k: v for k, v in hit[0][1].items() if k != "class"}}
    classes = {r["class"] for r in per_source.values()}
    if "missing" in classes and not classes & {"unfetchable", "skipped"}:
        sid, r = next((s, r) for s, r in per_source.items() if r["class"] == "missing")
        return {"class": "missing", "source": sid, **{k: v for k, v in r.items() if k != "class"}}
    if "unfetchable" in classes:
        sid, r = next((s, r) for s, r in per_source.items() if r["class"] == "unfetchable")
        return {"class": "unfetchable", "source": sid, "note": r.get("note", "")}
    sid, r = next((s, r) for s, r in per_source.items() if r["class"] == "skipped")
    return {"class": "skipped", "source": sid, "note": r.get("note", "")}


def run(args) -> list[dict]:
    items = collect_quotes()
    if args.only:
        items = [x for x in items if args.only in x["file"]]
    sources = load_sources()
    by_source: dict[str, list[int]] = collections.defaultdict(list)
    for n, it in enumerate(items):
        it["per_source"] = {}
        if not it["sources"]:
            it["note"] = "no sources on the quote's object or any ancestor"
        for sid in dict.fromkeys(it["sources"]):
            by_source[sid].append(n)
    fetcher = Fetcher(Path(args.cache), retry_failed=args.retry_failed, offline=args.offline,
                      retry_429=args.retry_429)

    # interleave hosts so the 4 workers are not all queued behind one throttled host
    def host(sid):
        return urllib.parse.urlsplit((sources.get(sid) or {}).get("url") or "").netloc
    queues: dict[str, list[str]] = collections.defaultdict(list)
    for sid in sorted(by_source):
        queues[host(sid)].append(sid)
    order = []
    while any(queues.values()):
        for h in sorted(queues, key=lambda k: -len(queues[k])):
            if queues[h]:
                order.append(queues[h].pop())

    def work(sid):
        src = sources.get(sid)
        idx = by_source[sid]
        if src is None:
            return sid, {k: {"class": "unfetchable", "note": "unknown source id"} for k in range(len(idx))}
        return sid, check_source(sid, src, [items[n]["quote"] for n in idx], fetcher)

    done = 0
    with cf.ThreadPoolExecutor(WORKERS) as pool:
        for sid, res in pool.map(work, order):
            for k, n in enumerate(by_source[sid]):
                items[n]["per_source"][sid] = res[k]
            done += 1
            if done % 25 == 0:
                print(f"  {done}/{len(order)} sources", flush=True)
    for it in items:
        it.update(combine(it["per_source"]))
        it["flags"] = ["number-not-in-quote: " + x for x in number_flags(it)]
    return items


# -------------------------------------------------------------------- report

def write_report(items: list[dict], path: Path, header: str = "", baseline: list[dict] | None = None) -> None:
    by_class = collections.Counter(x["class"] for x in items)
    before = collections.Counter(x["class"] for x in baseline) if baseline else None
    by_type: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for x in items:
        by_type[x["type"]][x["class"]] += 1
    num = [x for x in items if x["flags"]]
    alnum = sum(1 for x in items if x["class"] == "verbatim" and x.get("match") == "alnum")
    L = ["# Release quote check", "", header, "",
         f"Generated by `scripts/atlas_quote_check.py` on {time.strftime('%Y-%m-%d')}. "
         f"{len(items)} quotes, {len({s for x in items for s in x['sources']})} cited sources.", ""]
    if before:
        L += ["## Summary by class (before triage -> after)", "", "| class | before | after |", "|---|---|---|"]
        L += [f"| {c} | {before[c]} | {by_class[c]} |" for c in CLASS_ORDER]
        L += [f"| number-not-in-quote (flag) | {sum(1 for x in baseline if x['flags'])} | {len(num)} |"]
    else:
        L += ["## Summary by class", "", "| class | count |", "|---|---|"]
        L += [f"| {c} | {by_class[c]} |" for c in CLASS_ORDER]
        L += [f"| number-not-in-quote (flag) | {len(num)} |"]
    L += ["", f"`verbatim` includes {alnum} quotes that match only after dropping spacing, punctuation, TeX markup "
          "and Greek-letter spelling (alphanumerics identical in order).", "",
          "## By entity type", "",
          "| type | " + " | ".join(CLASS_ORDER) + " | number flag |", "|---|" + "---|" * (len(CLASS_ORDER) + 1)]
    for t in sorted(by_type):
        nf = sum(1 for x in num if x["type"] == t)
        L.append(f"| {t} | " + " | ".join(str(by_type[t][c]) for c in CLASS_ORDER) + f" | {nf} |")

    def row(x):
        q = x["quote"].replace("|", "\\|").replace("\n", " ")[:80]
        return f"| `{x['file'].removeprefix('data/atlas/')}` | `{x['pointer']}` | {x.get('source', '')} | {x['class']} | {q} |"

    head = "| file | pointer | source | class | quote (first 80 chars) |\n|---|---|---|---|---|"
    rest = [x for x in items if x["class"] in ("near", "missing")]
    L += ["", f"## Non-verbatim, non-skipped quotes: near and missing ({len(rest)})", "", head]
    L += [row(x) for x in sorted(rest, key=lambda x: (CLASS_ORDER.index(x["class"]), x["file"], x["pointer"]))]
    unf = [x for x in items if x["class"] == "unfetchable"]
    L += ["", f"## Unfetchable ({len(unf)}), listed separately", "", head]
    L += [row(x) for x in sorted(unf, key=lambda x: (x["file"], x["pointer"]))]
    reasons = collections.Counter(x.get("note") or "quote's cited sources skipped" for x in items if x["class"] == "skipped")
    L += ["", "## Skipped (never fetched by this script)", "", "| reason | quotes |", "|---|---|"]
    L += [f"| {r} | {n} |" for r, n in reasons.most_common()]
    L += ["", f"## number-not-in-quote ({len(num)})", "", head.replace("class", "flags")]
    for x in num:
        L.append(row(x).replace(f"| {x['class']} |", f"| {'; '.join(x['flags'])} |", 1))
    path.write_text("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    default_cache = Path(__import__("tempfile").gettempdir()) / "atlas_quote_check" / "cache"
    ap.add_argument("--cache", default=str(default_cache), help="directory for cached source bytes")
    ap.add_argument("--json", help="full JSON output (default: next to the cache)")
    ap.add_argument("--report", default=str(REPORT))
    ap.add_argument("--baseline", help="earlier --json output; the report then shows before and after counts")
    ap.add_argument("--only", help="only quotes whose file path contains this text")
    ap.add_argument("--retry-failed", action="store_true", help="refetch URLs whose cached fetch failed")
    ap.add_argument("--retry-429", action="store_true", help="refetch URLs whose cached fetch was rate-limited (HTTP 429)")
    ap.add_argument("--offline", action="store_true", help="classify from the cache only")
    args = ap.parse_args()
    items = run(args)
    out = Path(args.json) if args.json else Path(args.cache).parent / "quote_check.json"
    out.write_text(json.dumps(items, indent=1, ensure_ascii=False))
    if not args.only:
        baseline = json.loads(Path(args.baseline).read_text()) if args.baseline else None
        write_report(items, Path(args.report), baseline=baseline)
    print(collections.Counter(x["class"] for x in items), "number flags:", sum(1 for x in items if x["flags"]))


if __name__ == "__main__":
    main()
