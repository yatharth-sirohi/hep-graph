"""Unit checks for the guided-tour player (static/atlas/js/tour-data.js, state.js, tours.js).

The player itself needs a browser (tests/browser_atlas.cjs plays all six tours). What does
not is checked here, under Node on the real tours the build writes:

  * every step's `href` reads back as the year, selection, map or view its own fields name,
    with a view beating a map and a map beating a selection (A28);
  * a step's sentence, a question's prompt and its answer are cut at the phrases their
    claims cover and join back to the text exactly;
  * `?step=` clamps; `#/tour/<slug>?step=N`, `?step=N#/tour/<slug>` and `#/view/tour/<slug>`
    all read as the same route, and the address is written back as `?step=N#/tour/<slug>`;
  * a topic lists the tours with a step about it, a referenced field has a reader's name, a
    worked answer shows its own value (never the carrying field's text);
  * the wiring: one stylesheet in the right place, the card and the Tours button in the page,
    a search row per tour, and tours.json fetched only from the lazy callers.

Skipped when Node is not installed.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
JS = ROOT / "static" / "atlas" / "js"
DATA = ROOT / "data" / "atlas"
NODE = shutil.which("node")


@pytest.fixture(scope="module")
def built() -> dict:
    """The bundles the browser receives, built in memory (nothing is written)."""
    from hepgraph.atlas.build import build

    result = build(DATA, ROOT / "static" / "atlas" / "generated", check=True)
    return {name: json.loads(result.files[name]) for name in ("tours.json", "atlas.json", "search.json", "results.json")}


NODE_SCRIPT = r"""
import fs from 'node:fs';
const dir = process.argv[1];
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const data = await import(`${dir}/tour-data.js`);
const out = { steps: [], covered: [], topic: null, field: null, calc: null, clamp: null, meta: null, url: [] };

const tours = input.tours.order.map((id) => input.tours.tours[id]);
for (const tour of tours) {
  for (const step of tour.steps) {
    const t = data.stepTarget(step);
    out.steps.push({
      tour: tour.id, step: step.id, year: t.year, stage: t.stage, entity: t.entity, sel: t.sel,
      fields: { year: step.year ?? null, select: step.select ?? null, map: step.map ?? null, view: step.view ?? null },
    });
    const texts = [['text', step.text, step.claims]];
    if (step.question) {
      texts.push(['prompt', step.question.prompt, step.question.claims.filter((c) => c.in === 'prompt')]);
      texts.push(['answer', step.question.answer, step.question.claims.filter((c) => c.in !== 'prompt')]);
    }
    for (const [kind, text, claims] of texts) {
      const segments = data.coveredSegments(text, claims);
      out.covered.push({
        tour: tour.id, step: step.id, kind,
        joined: segments.map((s) => s.text).join('') === text,
        marked: claims.map((c, i) => segments.some((s) => s.claims.includes(i)) || !text.includes(c.covers)),
      });
    }
  }
}

const atlas = input.atlas;
const resultTopics = new Map(Object.values(input.results.results || input.results).filter((r) => r && r.id).map((r) => [r.id, r.topic_ids || []]));
const flat = { ...atlas.facilities, ...atlas.accelerators, ...atlas.experiments, ...atlas.topics, ...atlas.beamlines, ...atlas.sites, ...atlas.detectors };
const topicsOf = (id) => resultTopics.get(id) || (flat[id] && flat[id].topic_ids) || [];
out.topic = {
  higgs: data.toursCoveringTopic('topic:higgs-physics', tours, atlas.topics, topicsOf).map((r) => [r.tour.id, r.steps]),
  none: data.toursCoveringTopic('topic:no-such-topic', tours, atlas.topics, topicsOf).length,
};
const nameOf = (id) => (flat[id] && flat[id].name) || null;
out.field = {
  baseline: data.fieldLabel('key_specs.Baseline', nameOf),
  deep: data.fieldLabel('baselines.site:ash-river-nova-far-detector.distance', nameOf),
  energy: data.fieldLabel('primary_beam.value.energy', nameOf),
};
const deap = input.tours.tours['tour:going-underground-dark-matter'].steps.find((s) => s.id === 'snolab').question.calculation;
out.calc = deap.map(data.calculationLine).map((l) => [l.kind, l.name, l.valueText]);
out.clamp = [data.clampStep(undefined, 6), data.clampStep(0, 6), data.clampStep(-3, 6), data.clampStep(4, 6), data.clampStep(99, 6), data.clampStep('3', 6), data.clampStep('x', 6)];
out.meta = [data.tourMeta(tours[0]), data.tourMeta({ steps: [1], estimated_minutes: 1 }), data.tourMeta({ steps: [] })];
out.slug = [data.tourSlug('tour:higgs-hunt'), data.tourIdOf('higgs-hunt')];

// state.js: the address a tour link names, under a stand-in for the page.
function pageAt(path, search, hash) {
  const written = [];
  globalThis.window = {
    location: { pathname: path, search, hash, href: `http://x${path}${search}${hash}` },
    history: { pushState: (s, t, url) => written.push(['push', url]), replaceState: (s, t, url) => written.push(['replace', url]) },
    addEventListener() {},
  };
  return written;
}
const state = await import(`${dir}/state.js?${Math.random()}`);
for (const [search, hash] of [['?step=3&present=1', '#/tour/higgs-hunt'], ['', '#/tour/higgs-hunt?step=3'], ['', '#/view/tour/higgs-hunt'], ['?step=zero', '#/tour/higgs-hunt'], ['?step=0', '#/tour/higgs-hunt'], ['', '#/tour/higgs-hunt?step=2&present=1']]) {
  const written = pageAt('/atlas/', search, hash);
  const s = state.init();
  out.url.push({ search, hash, entity: s.entity, step: s.step, present: s.present });
}
{
  const written = pageAt('/atlas/', '?step=2', '#/tour/higgs-hunt');
  state.init();
  state.navigate({ step: 3 });
  state.navigate({ present: true }, { replace: true });
  state.navigate({ entity: { type: 'experiment', slug: 'lz' } });          // leaving: step and present are not written
  state.navigate({ entity: { type: 'tour', slug: 'w-and-z-at-cern' } });   // another tour: starts at the first step
  out.written = written;
  out.stepAfterLeaving = state.get().step;
}
{
  // The timeline rewrites the address (?y=) as it starts; the view-style route must keep its step.
  const written = pageAt('/atlas/', '?step=2', '#/view/tour/higgs-hunt');
  state.init();
  state.navigate({ year: 2026 }, { replace: true });
  out.aliasKept = written[0][1];
}
console.log(JSON.stringify(out));
"""


@pytest.fixture(scope="module")
def result(built: dict) -> dict:
    payload = {
        "tours": built["tours.json"], "atlas": built["atlas.json"], "results": built["results.json"],
    }
    run = subprocess.run(
        [NODE, "--input-type=module", "-e", NODE_SCRIPT, str(JS)],
        input=json.dumps(payload), capture_output=True, text=True, timeout=90,
    )
    assert run.returncode == 0, run.stderr
    return json.loads(run.stdout)


pytestmark = pytest.mark.skipif(NODE is None, reason="node is not installed")


def test_every_step_href_reads_back_as_its_own_fields(result: dict) -> None:
    assert len(result["steps"]) >= 36
    for row in result["steps"]:
        fields = row["fields"]
        where = f'{row["tour"]} {row["step"]}'
        assert row["year"] == fields["year"], where
        if fields["view"]:
            # A view beats a map beats a selection.
            assert row["stage"] == "view", where
            assert row["entity"] == {"type": "view", "slug": f'{fields["view"]["name"]}/{fields["view"]["arg"]}'}, where
        elif fields["map"]:
            assert row["stage"] == "map", where
            assert row["entity"] == {"type": "map", "slug": fields["map"]}, where
            assert row["sel"] == fields["select"], where
        elif fields["select"]:
            kind, slug = fields["select"].split(":", 1)
            assert row["stage"] == "globe", where
            assert row["entity"] == {"type": kind, "slug": slug}, where
    stages = {row["stage"] for row in result["steps"]}
    assert stages == {"globe", "map", "view"}


def test_sentences_are_cut_at_the_phrases_claims_cover_and_join_back(result: dict) -> None:
    assert result["covered"]
    for row in result["covered"]:
        assert row["joined"], row
        assert all(row["marked"]), row


def test_the_step_parameter_clamps_and_the_tour_route_reads_every_way_it_is_written(result: dict) -> None:
    assert result["clamp"] == [1, 1, 1, 4, 6, 3, 1]
    by = {(row["search"], row["hash"]): row for row in result["url"]}
    tour = {"type": "tour", "slug": "higgs-hunt"}
    assert by[("?step=3&present=1", "#/tour/higgs-hunt")]["entity"] == tour
    assert by[("?step=3&present=1", "#/tour/higgs-hunt")]["step"] == 3
    assert by[("?step=3&present=1", "#/tour/higgs-hunt")]["present"] is True
    # The query typed inside the hash is read as the query.
    inside = by[("", "#/tour/higgs-hunt?step=3")]
    assert (inside["entity"], inside["step"], inside["present"]) == (tour, 3, False)
    both = by[("", "#/tour/higgs-hunt?step=2&present=1")]
    assert (both["entity"], both["step"], both["present"]) == (tour, 2, True)
    # `#/view/tour/<slug>` stays a view route here; app.js rewrites it to the tour route.
    assert by[("", "#/view/tour/higgs-hunt")]["entity"] == {"type": "view", "slug": "tour/higgs-hunt"}
    # A step that is not a positive number is no step at all.
    assert by[("?step=zero", "#/tour/higgs-hunt")]["step"] is None
    assert by[("?step=0", "#/tour/higgs-hunt")]["step"] is None


def test_the_address_is_written_as_step_then_tour_and_forgets_both_on_leaving(result: dict) -> None:
    urls = [url for _, url in result["written"]]
    assert urls[0] == "/atlas/?step=3#/tour/higgs-hunt"
    assert urls[1] == "/atlas/?step=3&present=1#/tour/higgs-hunt"
    assert urls[2] == "/atlas/#/experiment/lz"          # neither is stranded in another route's address
    assert urls[3] == "/atlas/#/tour/w-and-z-at-cern"   # another tour starts again (the player writes step 1)
    assert result["stepAfterLeaving"] is None


def test_the_view_style_route_keeps_its_step_when_the_timeline_rewrites_the_address(result: dict) -> None:
    assert result["aliasKept"] == "/atlas/?y=2026&step=2#/view/tour/higgs-hunt"


def test_a_topic_lists_the_tours_with_a_step_about_it(result: dict) -> None:
    higgs = dict(result["topic"]["higgs"])
    assert "tour:higgs-hunt" in higgs
    assert 1 in higgs["tour:higgs-hunt"] and len(higgs["tour:higgs-hunt"]) >= 3
    assert result["topic"]["higgs"][0][0] == "tour:higgs-hunt"  # the most steps first
    assert result["topic"]["none"] == 0


def test_a_referenced_field_has_a_readers_name_and_a_worked_line_shows_its_own_value(result: dict) -> None:
    assert result["field"]["baseline"] == "Baseline"
    assert result["field"]["energy"] == "Primary beam › Energy"
    assert result["field"]["deep"].startswith("Baselines › ")
    assert result["field"]["deep"].endswith("› Distance")
    by_name = {name: [kind, value] for kind, name, value in result["calc"]}
    assert by_name["r_cm"] == ["atlas", "85 cm"]  # not the carrying field's "3600 kg"
    assert by_name["M"] == ["atlas", "3600 kg"]
    assert by_name["V"][0] == "computed"
    assert result["meta"] == ["7 steps · about 12 minutes", "1 step · about 1 minute", "0 steps"]
    assert result["slug"] == ["higgs-hunt", "tour:higgs-hunt"]


# ---------------------------------------------------------------------------
# Wiring (no Node needed beyond the module-level skip)
# ---------------------------------------------------------------------------
def test_the_page_carries_the_card_the_button_and_one_stylesheet_in_order() -> None:
    html = (ROOT / "static/atlas/index.html").read_text(encoding="utf-8")
    assert html.count('href="/atlas/tours.css"') == 1
    assert html.index("/atlas/views.css") < html.index("/atlas/tours.css") < html.index("/atlas/phone.css")
    assert 'id="tour-card"' in html
    assert re.search(r'data-mode="tours"[^>]*hidden', html), "the Tours button is hidden until the build has tours"
    assert 'id="start-tours"' in html


def test_search_finds_every_tour_and_tours_json_is_only_fetched_lazily(built: dict) -> None:
    rows = [e for e in built["search.json"]["entries"] if e[0] == "tour"]
    assert sorted(e[1] for e in rows) == sorted(built["tours.json"]["tours"])
    assert all(e[2] and "Guided tour" in e[4] for e in rows)
    # Nothing at first paint asks for the tours: app.js never fetches them itself.
    app = (JS / "app.js").read_text(encoding="utf-8")
    assert "getTours" not in app
    callers = {p.name for p in JS.rglob("*.js") if "getTours" in p.read_text(encoding="utf-8")}
    assert callers == {"loader.js", "modes.js", "panels.js", "tours.js"}
