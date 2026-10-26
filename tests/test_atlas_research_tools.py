"""Unit checks for the researchers' tools: Compare, Cite and the list exports.

What is checked here needs no browser:

  * CSV quoting (RFC 4180, the formula guard, the BOM and the "#" metadata lines);
  * BibTeX escaping (TeX math kept, the characters TeX reads as commands escaped, the
    symbols a physicist's title uses written as TeX) and the rule that an entry holds
    only fields the record carries;
  * the unit conversion Compare uses to read across a row, and its refusal to convert a
    value whose wording has more than one figure;
  * the comparison itself, built from the real records: DUNE, Hyper-K and JUNO.

The browser modules run under Node (skipped when Node is not installed). Nothing is
fetched and nothing is written.
"""
from __future__ import annotations

import csv
import io
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static" / "atlas"
JS = STATIC / "js"
DATA = ROOT / "data" / "atlas"
NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(NODE is None, reason="node is not installed")

NODE_SCRIPT = r"""
import fs from 'node:fs';
const js = process.argv[1];
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const files = await import(`${js}/research/files.js`);
const bib = await import(`${js}/research/bibtex.js`);
const units = await import(`${js}/views/compare-units.js`);
const route = await import(`${js}/views/compare-route.js`);
const rows = await import(`${js}/views/compare-rows.js`);
const lists = await import(`${js}/research/list-export.js`);

const out = {};

// ---- CSV
out.csv = {
  fields: ['plain', 'a,b', 'say "hi"', 'two\nlines', ' edge', 'edge ', '', null, 5, '=SUM(A1)', '+1', '-3', '-0.5', '@x', '1e5', '-', 'ν ± µ'].map(files.csvField),
  line: files.csvLine(['a', 'b,c', 'd"e']),
  comment: files.csvComment('Filter: Year: 2018; sorted\nby date'),
  file: files.buildCsv({ preamble: ['Data version: 1, 2'], header: ['id', 'name'], rows: [['x', 'A, "B"']] }),
  access: files.accessDate(new Date(2026, 9, 26, 23, 59)),
  name: files.fileName(['HEP Atlas', 'results', '2026-10-26'], 'csv'),
};

// ---- BibTeX
const esc = bib.bibtexEscape;
out.escape = {
  plain: esc('Observation of a new particle'),
  specials: esc('50% of A&B_c #1 {x} ~ ^ \\ <y>'),
  math: esc('Observation of the rare $B^0_s\\to\\mu^+\\mu^-$ decay'),
  lonelyDollar: esc('costs $5'),
  escapedDollar: esc('costs \\$5 or $x$'),
  emptyMath: esc('a $$ b'),
  unbalancedMath: esc('a $x{$ b'),
  unicode: esc('B⁻ → τ⁻ ν̅_τ at √s = 13 TeV, 5.02 TeV Pb–Pb'),
  superscripts: esc('3 K⁺ and D⁰ at 10⁻³'),
  whitespace: esc('  two   spaces\n and a line  '),
  braces: ['a}{b', '{{', '$x}$'].map(esc).map((t) => {
    let depth = 0; let ok = true;
    for (let i = 0; i < t.length; i += 1) { if (t[i] === '\\') { i += 1; continue; } if (t[i] === '{') depth += 1; if (t[i] === '}') { depth -= 1; if (depth < 0) ok = false; } }
    return ok && depth === 0;
  }),
  verbatim: bib.bibtexVerbatim('10.1002/(SICI)1097-0258(19980815/30)17:15/16<1661::AID-SIM968>3.0.CO;2-2 {x}'),
  key: bib.bibtexKey('result:atlas-higgs-observation-2012'),
};

const collaborations = { 'collaboration:atlas': { name: 'ATLAS Collaboration' }, 'collaboration:cms': { name: 'CMS Collaboration' } };
const base = {
  type: 'result', id: 'result:x-2012', title: 'A title', name: 'A name', date: '2012-07-04', date_kind: 'announcement',
  collaboration_ids: ['collaboration:atlas'], publication: { doi: '10.1/abc_1', arxiv: '1207.7214', url: 'https://arxiv.org/abs/1207.7214' },
};
const cite = (patch, ctx = { collaborations }) => bib.citationFor({ ...base, ...patch }, ctx);
out.cite = {
  full: cite({ published: '2013' }),
  announcement: cite({}),
  noDoiNoArxiv: cite({ publication: { url: 'https://example.org' } }),
  nullPublication: cite({ publication: null }),
  doiOnly: cite({ publication: { doi: '10.1/only' } }),
  arxivOnly: cite({ publication: { arxiv: 'arXiv:hep-ex/0001001' } }),
  noCollaboration: cite({ collaboration_ids: [] }),
  twoCollaborations: cite({ collaboration_ids: ['collaboration:atlas', 'collaboration:cms'] }),
  journal: cite({ publication: { doi: '10.1/j', journal: 'Phys. Lett. B' }, published: '2012' }),
  authors: cite({ authors: ['Doe, J.', 'Roe, R.'], collaboration_ids: [] }),
  report: cite({ publication: { arxiv: '1', report_number: 'CERN-EP-2012-1' } }),
  doc: bib.citationFor({
    type: 'document', id: 'document:d-1', name: 'A report', date: '1990-02', owner_ids: ['collaboration:atlas'],
    reference: { doi: '10.1/d', url: 'https://doi.org/10.1/d' },
  }, { collaborations }),
  docNone: bib.citationFor({ type: 'document', id: 'document:d-2', name: 'No ids', date: '1990', reference: { url: 'https://x' } }),
};

// ---- units
out.units = {
  convert: [units.convert(17.5, 'mass', 'kt', 't'), units.convert(7, 'mass', 't', 'kt'), units.convert(1285, 'length', 'km', 'm'), units.convert(13.6, 'energy', 'TeV', 'GeV'), units.convert(1, 'mass', 'kg', 'furlong'), units.convert(1, 'depth_mwe', 'm.w.e.', 'm')],
  choose: [
    units.chooseUnit('length', [{ value: 1285, unit: 'km' }, { value: 295, unit: 'km' }, { value: 52.5, unit: 'km' }]),
    units.chooseUnit('length', [{ value: 650, unit: 'm' }, { value: 1.5, unit: 'km' }]),
    units.chooseUnit('mass', [{ value: 3.7, unit: 't' }, { value: 300, unit: 'g' }]),
    units.chooseUnit('mass', [{ value: 10, unit: 'kt' }, { value: 188, unit: 'kt' }]),
    units.chooseUnit('depth_mwe', [{ value: 1750, unit: 'm.w.e.' }]),
    units.chooseUnit('length', [{ value: 1480, unit: 'm' }, { value: 2400, unit: 'm' }], 'm'),
  ],
  simple: [
    { display: '17.5 kt', value: 17.5, unit: 'kt' }, { display: 'at least 10 kt', value: 10, unit: 'kt' }, { display: '~295 km', value: 295, unit: 'km' },
    { display: '260 kt total, 188 kt fiducial', value: 260, unit: 'kt' }, { display: '700 m granite overburden', value: 700, unit: 'm' },
    { display: '1285 km', value: 1000, unit: 'km' }, { display: '400 GeV/c', value: 400, unit: 'GeV' }, { display: '1,285 km', value: 1285, unit: 'km' },
  ].map((q) => units.parseSimpleDisplay(q)),
  text: [units.composeText('at least', 10000, 't'), units.composeText('~', 0.295, 'km'), units.composeText('', 17500, 't')],
  number: [units.formatNumber(17500), units.formatNumber(0.1 + 0.2), units.formatNumber(1285.0000001)],
};

// ---- the route
out.route = {
  parse: [route.parseArg('dune,juno'), route.parseArg(' dune , dune,,JUNO,juno '), route.parseArg(''), route.parseArg('a,b,c,d,e')],
  resolve: (() => {
    const r = route.resolveArg(input.atlas, 'dune,nope,hyper-kamiokande,juno,lz,xenonnt');
    return { shown: r.experiments.map((e) => e.id), unknown: r.unknown, extra: r.extra.map((e) => e.id) };
  })(),
  hash: route.compareHash(['dune', 'juno']),
  entry: route.compareSearchEntries(),
};

// ---- the comparison of the real records
const results = new Map(Object.entries(input.results).filter(([k]) => k.startsWith('result:')));
const compare = (arg, year = 2026) => {
  const { experiments } = route.resolveArg(input.atlas, arg);
  const model = rows.buildComparison({ atlas: input.atlas, results, timelineState: { year } }, experiments);
  rows.attachSources(model, input.provenance, input.sources);
  return model;
};
const cells = (model, key) => model.rows.find((r) => r.key === key).cells.map((c) => c.lines.map(rows.lineText));
const three = compare('dune,hyper-kamiokande,juno');
const xenon = compare('lz,xenonnt,pandax-4t');
const mixed = compare('atlas,juno,nova');
out.compare = {
  rowKeys: three.rows.map((r) => r.key),
  rowLabels: three.rows.map((r) => r.label),
  heads: three.experiments.map((e) => e.short),
  status: cells(three, 'status'),
  baseline: cells(three, 'baseline'),
  mass: cells(three, 'mass'),
  energy: cells(three, 'energy'),
  depth: cells(three, 'depth'),
  tech: cells(three, 'technology'),
  results: cells(three, 'results'),
  collab: cells(three, 'collaboration'),
  xenonMass: cells(xenon, 'mass'),
  xenonDepth: cells(xenon, 'depth'),
  mixedMass: cells(mixed, 'mass'),
  mixedEnergy: cells(mixed, 'energy'),
  sourceCount: three.sourceList.length,
  // every line that is a statement of the record has at least one source here
  unsourced: three.rows.flatMap((r) => r.cells.flatMap((c) => c.lines.filter((l) => !l.derived && !l.markers.length).map(lineLabel))),
  year2010: cells(compare('dune,hyper-kamiokande,juno', 2010), 'status'),
  rangeLabel: rows.buildComparison({ atlas: input.atlas, results, timelineState: { range: [2015, 2020] } }, route.resolveArg(input.atlas, 'dune,juno').experiments).rows[0].label,
};
function lineLabel(l) { return `${l.label || ''}${l.text}`; }
const csvText = rows.comparisonCsv(three, { dataVersion: 'abc123', accessed: '2026-10-26', link: 'http://x/atlas/#/view/compare/dune' });
out.compareCsv = csvText;
let threw = false;
try {
  const bare = rows.buildComparison({ atlas: input.atlas, results, timelineState: { year: 2026 } }, route.resolveArg(input.atlas, 'dune,juno').experiments);
  rows.comparisonCsv(bare, { dataVersion: 'v', accessed: 'd' });
} catch (error) { threw = /sources/.test(error.message); }
out.csvNeedsSources = threw;

// ---- the list exports
const sourcesById = input.sources;
const resultSample = ['result:atlas-higgs-observation-2012', 'result:juno-oscillation-parameters-2026'].map((id) => results.get(id));
const rowsR = lists.resultRows(resultSample, { atlas: input.atlas, provenance: input.provenance, sourcesById, base: 'http://h/atlas/' });
const files2 = lists.listFiles('results', rowsR, { dataVersion: 'v1', accessed: '2026-10-26', filter: 'Year: 2012; sorted by date', shown: 2, total: 109, link: 'http://h/atlas/?m=results' });
out.lists = { rows: rowsR, csv: files2.csv, json: JSON.parse(files2.json), header: files2.header };

console.log(JSON.stringify(out));
"""


@pytest.fixture(scope="module")
def built():
    """The bundles as the browser receives them, built in memory from data/atlas (nothing is written)."""
    from hepgraph.atlas.build import build

    return build(DATA, STATIC / "generated", check=True)


@pytest.fixture(scope="module")
def out(built) -> dict:
    payload = {
        "atlas": json.loads(built.files["atlas.json"]),
        "results": json.loads(built.files["results.json"]),
        "provenance": json.loads(built.files["provenance.json"]),
        "sources": json.loads(built.files["sources.json"]),
    }
    result = subprocess.run(
        [NODE, "--input-type=module", "-e", NODE_SCRIPT, str(JS)],
        input=json.dumps(payload), capture_output=True, text=True, check=True, timeout=120,
    )
    return json.loads(result.stdout)


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------
def test_csv_fields_are_quoted_as_rfc_4180_asks(out: dict) -> None:
    f = out["csv"]["fields"]
    assert f[0] == "plain"
    assert f[1] == '"a,b"'
    assert f[2] == '"say ""hi"""'
    assert f[3] == '"two\nlines"'
    assert f[4] == '" edge"' and f[5] == '"edge "'  # edge spaces are data
    assert f[6] == "" and f[7] == ""  # empty and null are empty, never "null"
    assert f[8] == "5"
    assert f[16] == "ν ± µ"  # no escaping of non-ASCII text


def test_csv_cells_that_a_spreadsheet_would_read_as_formulas_are_defused(out: dict) -> None:
    f = out["csv"]["fields"]
    assert f[9] == "'=SUM(A1)" and f[10:12] == ["+1", "-3"] and f[12] == "-0.5"  # numbers stay numbers
    assert f[13] == "'@x"
    assert f[14] == "1e5"
    assert f[15] == "'-"  # a lone hyphen is text, not a number


def test_a_csv_file_has_a_bom_crlf_lines_and_unquoted_metadata(out: dict) -> None:
    assert out["csv"]["line"] == 'a,"b,c","d""e"'
    assert out["csv"]["comment"] == "# Filter: Year: 2018; sorted by date"
    text = out["csv"]["file"]
    assert text.startswith("﻿# Data version: 1, 2\r\n")  # a comma in metadata is not quoted
    assert text.endswith('id,name\r\nx,"A, ""B"""\r\n')
    body = [row for row in csv.reader(io.StringIO(text.lstrip("﻿"))) if row and not row[0].startswith("#")]
    assert body == [["id", "name"], ["x", 'A, "B"']]
    assert out["csv"]["access"] == "2026-10-26"
    assert out["csv"]["name"] == "hep-atlas-results-2026-10-26.csv"


# ---------------------------------------------------------------------------
# BibTeX
# ---------------------------------------------------------------------------
def test_bibtex_escaping(out: dict) -> None:
    e = out["escape"]
    assert e["plain"] == "Observation of a new particle"
    assert e["specials"] == (
        r"50\% of A\&B\_c \#1 \{x\} \textasciitilde{} \textasciicircum{} \textbackslash{} \textless{}y\textgreater{}"
    )
    # TeX math is kept exactly; the dollar signs of a text that is not math are escaped.
    assert e["math"] == r"Observation of the rare $B^0_s\to\mu^+\mu^-$ decay"
    assert e["lonelyDollar"] == r"costs \$5"
    assert e["escapedDollar"] == r"costs \$5 or $x$"
    assert e["emptyMath"] == "a b"  # "$$" would open display math in TeX
    assert "{x\\{$ b" not in e["unbalancedMath"] and e["unbalancedMath"].count("\\$") == 2
    assert e["whitespace"] == "two spaces and a line"
    assert all(e["braces"]), "every escaped value has balanced braces"


def test_bibtex_turns_physics_symbols_into_tex(out: dict) -> None:
    e = out["escape"]
    assert e["unicode"] == (
        r"B$^{-}$ $\to$ $\tau^{-}$ $\bar{\nu}$\_$\tau$ at $\surd$s = 13 TeV, 5.02 TeV Pb--Pb"
    )
    assert e["superscripts"] == r"3 K$^{+}$ and D$^{0}$ at 10$^{-3}$"  # one superscript, not two


def test_bibtex_identifiers_are_not_escaped_but_never_unbalance_the_braces(out: dict) -> None:
    assert out["escape"]["verbatim"] == "10.1002/(SICI)1097-0258(19980815/30)17:15/16<1661::AID-SIM968>3.0.CO;2-2%7Bx%7D"
    assert out["escape"]["key"] == "atlas-higgs-observation-2012"


def test_an_entry_has_only_the_fields_the_record_carries(out: dict) -> None:
    c = out["cite"]
    full = c["full"]
    assert full["ok"] and full["type"] == "misc" and full["key"] == "x-2012"
    assert full["text"] == (
        "@misc{x-2012,\n"
        "  title = {{A title}},\n"
        "  author = {{ATLAS Collaboration}},\n"
        "  year = {2013},\n"
        "  doi = {10.1/abc_1},\n"
        "  eprint = {1207.7214},\n"
        "  archivePrefix = {arXiv},\n"
        "  url = {https://arxiv.org/abs/1207.7214}\n"
        "}"
    )
    assert full["missing"] == ["journal"]
    # The year of the publication when the record has one; else the year of its own date, with the announcement said.
    assert "year = {2012}" in c["announcement"]["text"] and "note = {Announced 2012-07-04}" in c["announcement"]["text"]
    assert "note" not in full["text"]
    # No DOI and no arXiv identifier: no entry, and the reason says so.
    for key in ("noDoiNoArxiv", "nullPublication", "docNone"):
        assert c[key]["ok"] is False and "neither a DOI nor an arXiv" in c[key]["reason"] and "text" not in c[key]
    assert "eprint" not in c["doiOnly"]["text"] and "doi = {10.1/only}" in c["doiOnly"]["text"]
    assert "eprint = {hep-ex/0001001}" in c["arxivOnly"]["text"] and "doi" not in c["arxivOnly"]["text"]
    # Nothing is guessed: no collaboration, no author line; a journal only if the record names one.
    assert "author" not in c["noCollaboration"]["text"] and "author" in c["noCollaboration"]["missing"]
    assert "author = {{ATLAS Collaboration} and {CMS Collaboration}}" in c["twoCollaborations"]["text"]
    assert c["journal"]["type"] == "article" and "journal = {Phys. Lett. B}" in c["journal"]["text"]
    assert "journal" not in c["journal"]["missing"]
    assert "author = {Doe, J. and Roe, R.}" in c["authors"]["text"]
    assert "note = {Announced 2012-07-04; Report number CERN-EP-2012-1}" in c["report"]["text"]
    # A document: its owner is not its author.
    assert c["doc"]["ok"] and "author" not in c["doc"]["text"] and "year = {1990}" in c["doc"]["text"]
    assert "author" in c["doc"]["missing"]


def test_every_bibtex_entry_the_atlas_would_offer_is_well_formed(built) -> None:
    """The real records, through the real module: balanced braces, no raw special character in a title."""
    results = {k: v for k, v in json.loads(built.files["results.json"]).items() if k.startswith("result:")}
    script = r"""
import fs from 'node:fs';
const js = process.argv[1];
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const bib = await import(`${js}/research/bibtex.js`);
const out = Object.values(input.results).map((r) => bib.citationFor(r, { collaborations: input.collaborations }));
console.log(JSON.stringify(out.map((c) => (c.ok ? { ok: true, text: c.text, title: c.fields.find((f) => f[0] === 'title')[1] } : { ok: false }))));
"""
    payload = {"results": results, "collaborations": json.loads(built.files["atlas.json"])["collaborations"]}
    done = subprocess.run([NODE, "--input-type=module", "-e", script, str(JS)], input=json.dumps(payload),
                          capture_output=True, text=True, check=True, timeout=60)
    entries = json.loads(done.stdout)
    offered = [e for e in entries if e["ok"]]
    assert len(entries) == 109 and len(offered) == 107  # two results carry neither a DOI nor an arXiv id
    for entry in offered:
        text = entry["text"]
        depth = 0
        for i, ch in enumerate(text):
            if text[i - 1:i] == "\\":
                continue
            depth += ch == "{"
            depth -= ch == "}"
            assert depth >= 0, text
        assert depth == 0, text
        title = re.sub(r"\$[^$]*\$", "", entry["title"])  # outside math
        assert not re.search(r"(?<!\\)[&%#_^~<>]", title), entry["title"]


# ---------------------------------------------------------------------------
# Units
# ---------------------------------------------------------------------------
def test_units_convert_by_powers_of_ten_and_only_within_a_dimension(out: dict) -> None:
    u = out["units"]
    assert u["convert"] == [17500, 0.007, 1285000, 13600, None, None]
    assert u["choose"] == ["km", "m", "g", "kt", None, "m"]
    assert u["number"] == ["17,500", "0.3", "1,285"]


def test_only_a_one_figure_one_unit_wording_is_converted(out: dict) -> None:
    simple = out["units"]["simple"]
    assert simple[0] == {"prefix": "", "number": 17.5, "unit": "kt"}
    assert simple[1]["prefix"] == "at least" and simple[2]["prefix"] == "~"
    assert simple[3:7] == [None, None, None, None]  # more than one figure; trailing words; wrong value; unit GeV/c
    assert simple[7]["number"] == 1285
    assert out["units"]["text"] == ["at least 10,000 t", "~0.295 km", "17,500 t"]


# ---------------------------------------------------------------------------
# The route and the comparison
# ---------------------------------------------------------------------------
def test_the_route_names_two_to_four_experiments_and_reports_what_it_drops(out: dict) -> None:
    parse = out["route"]["parse"]
    assert parse[0] == {"slugs": ["dune", "juno"], "invalid": []}
    assert parse[1] == {"slugs": ["dune", "juno"], "invalid": ["JUNO"]}
    assert parse[2] == {"slugs": [], "invalid": []}
    assert out["route"]["resolve"] == {
        "shown": ["experiment:dune", "experiment:hyper-kamiokande", "experiment:juno", "experiment:lz"],
        "unknown": ["nope"],
        "extra": ["experiment:xenonnt"],
    }
    assert out["route"]["hash"] == "#/view/compare/dune,juno"
    assert out["route"]["entry"][0]["id"] == "view:compare/" and "compare" in out["route"]["entry"][0]["aliases"]


def test_dune_hyper_k_and_juno_side_by_side(out: dict) -> None:
    c = out["compare"]
    assert c["heads"] == ["DUNE", "Hyper-Kamiokande", "JUNO"]
    assert c["rowKeys"] == ["status", "dates", "host", "depth", "baseline", "mass", "energy", "technology", "results", "collaboration"]
    assert c["rowLabels"][0] == "Status in 2026" and c["rowLabels"][-1] == "Collaboration size"
    assert c["status"] == [["Construction"], ["Construction"], ["Active"]]
    assert c["year2010"] == [["Not yet proposed in 2010"]] * 3  # the absence is worded, with no marker
    assert c["rangeLabel"] == "Status in 2015–2020"
    # The baselines, in one unit, each with its own label.
    assert c["baseline"] == [["Baseline: 1285 km"], ["Baseline (J-PARC to Hyper-Kamiokande): ~295 km"], ["Baseline to reactor cores: ~52.5 km"]]
    # Masses: the label stays, "260 kt total, 188 kt fiducial" is shown as recorded.
    assert c["mass"][0] == ["Far detector fiducial mass (per module): at least 10 kt", "Liquid argon per cryostat: 17.5 kt"]
    assert c["mass"][1] == ["Total / fiducial mass: 260 kt total, 188 kt fiducial"]
    assert c["mass"][2] == ["Target (liquid-scintillator) mass: 20 kt"]
    # An experiment with nothing for a row has an empty cell, which the view words "not recorded".
    assert c["energy"][1] == [] and c["energy"][2] == []
    assert c["energy"][0][0].startswith("Energy regime: GeV-scale accelerator neutrinos")
    assert c["depth"][1] == ["Depth: 650 m of rock at the detector centre", "Water-equivalent depth: 1750 m.w.e."]
    assert c["tech"] == [["Liquid-Argon TPC"], ["Water Cherenkov"], ["Liquid Scintillator"]]
    assert c["results"][1] == []
    assert c["results"][2][0].startswith("2025-11-18 · ")
    assert c["collab"][0] == ["1,500 members (as of 2026-09)", "228 institutions in 38 countries"]
    assert c["sourceCount"] > 10
    assert c["unsourced"] == [], "every value of the record has a source marker here"


def test_values_are_read_across_in_one_unit_without_changing_what_a_source_said(out: dict) -> None:
    c = out["compare"]
    assert c["xenonMass"] == [
        ["Active liquid xenon: 7 t", "Fiducial mass (SR1): 5.5 t", "Total xenon inventory: 10 t"],
        ["Total liquid xenon mass: 8.5 t", "Active liquid xenon mass: 5.9 t"],
        ["Total xenon inventory (design): 6 t", "Sensitive target mass (design): 4 t", "TPC target mass (commissioning-run analysis): 3.7 t"],
    ]
    # A converted value says what the record wrote; the unconvertible ones fix the unit of the row.
    assert c["xenonDepth"][0][0] == "Depth: ~1480 m"
    assert c["mixedMass"][0] == ["Detector weight: 7 kt (recorded: 7000 t)"]
    assert c["mixedMass"][2][0] == "Far detector mass: 14 kt"
    assert any("13,600 GeV (recorded: 13.6 TeV)" in line for line in c["mixedEnergy"][0])


def test_the_compare_csv_is_exactly_the_table_with_a_citations_column(out: dict) -> None:
    text = out["compareCsv"]
    assert text.startswith("﻿# HEP Atlas: comparison of experiments\r\n# Atlas data version: abc123\r\n# Accessed: 2026-10-26\r\n")
    lines = [line for line in csv.reader(io.StringIO(text.lstrip("﻿"))) if not (line and line[0].startswith("#"))]
    assert lines[0] == ["Quantity", "DUNE", "Hyper-Kamiokande", "JUNO", "Citations"]
    assert [row[0] for row in lines[1:]] == out["compare"]["rowLabels"]
    assert all(len(row) == 5 for row in lines)
    by_label = {row[0]: row for row in lines[1:]}
    assert by_label["Baseline"][1:4] == ["Baseline: 1285 km", "Baseline (J-PARC to Hyper-Kamiokande): ~295 km", "Baseline to reactor cores: ~52.5 km"]
    assert by_label["Energy"][2] == "not recorded" and by_label["Key results, with dates"][2] == "not recorded"
    assert by_label["Baseline"][4].startswith("DUNE: https://") and "Hyper-Kamiokande: https://" in by_label["Baseline"][4]
    # The citations are URLs, each attributed to its experiment.
    for row in lines[1:]:
        for part in row[4].split(" | "):
            assert part == "not recorded" or re.fullmatch(r"[^:]+: https?://\S+( https?://\S+)*", part), part
    assert out["csvNeedsSources"] is True  # an export without its citations is refused, not written


# ---------------------------------------------------------------------------
# The list exports
# ---------------------------------------------------------------------------
def test_the_list_exports_carry_ids_names_dates_identifiers_and_source_urls(out: dict) -> None:
    lists = out["lists"]
    first = lists["rows"][0]
    assert first["id"] == "result:atlas-higgs-observation-2012"
    assert first["doi"] == "10.1016/j.physletb.2012.08.020" and first["arxiv"] == "1207.7214"
    assert first["experiments"] == ["ATLAS"] and first["experiment_ids"] == ["experiment:atlas"]
    assert first["atlas_url"] == "http://h/atlas/#/result/atlas-higgs-observation-2012"
    assert first["source_urls"] and all(u.startswith("http") for u in first["source_urls"])
    assert len(first["source_urls"]) == len(set(first["source_urls"]))
    text = lists["csv"]
    assert text.startswith("﻿# HEP Atlas: results list\r\n# Atlas data version: v1\r\n# Filter: Year: 2012; sorted by date\r\n# Rows: 2 of 109 results\r\n# Accessed: 2026-10-26\r\n")
    table = [row for row in csv.reader(io.StringIO(text.lstrip("﻿"))) if not (row and row[0].startswith("#"))]
    assert table[0] == lists["header"] and len(table) == 3
    assert table[1][lists["header"].index("source_urls")].count(" | ") == len(first["source_urls"]) - 1
    meta = lists["json"]["meta"]
    assert meta["data_version"] == "v1" and meta["filter"] == "Year: 2012; sorted by date" and meta["accessed"] == "2026-10-26"
    assert meta["rows_shown"] == 2 and meta["rows_in_list"] == 109
    assert lists["json"]["rows"][0]["source_urls"] == first["source_urls"]


# ---------------------------------------------------------------------------
# Wiring
# ---------------------------------------------------------------------------
def test_the_compare_view_is_registered_once_and_loads_only_when_asked() -> None:
    registry = (JS / "views" / "registry.js").read_text(encoding="utf-8")
    assert "load: () => import('./compare.js')" in registry
    for path in JS.rglob("*.js"):
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"^import .* from '[^']*compare(-rows)?\.js'", text, re.M), path.name
    # The route's few lines are all that the globe's own start-up pulls in.
    assert "compare-rows" not in registry


def test_research_css_is_linked_once_between_the_view_and_the_phone_styles() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    assert html.count('href="/atlas/research.css"') == 1
    assert html.index("/atlas/views.css") < html.index("/atlas/research.css") < html.index("/atlas/phone.css")


def test_no_research_module_writes_a_literal_colour_or_reaches_for_the_network() -> None:
    css = (STATIC / "research.css").read_text(encoding="utf-8")
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", re.sub(r"/\*.*?\*/", "", css, flags=re.S))
    for path in [*(JS / "research").glob("*.js"), JS / "views" / "compare.js", JS / "views" / "compare-rows.js"]:
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"\bfetch\(|XMLHttpRequest|sendBeacon|https?://[^\s'\"`]*\.(?:com|org)/[^\s'\"`]*\.js", text), path.name
