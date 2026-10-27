"""The atlas stylesheet must parse as balanced CSS.

A merge once truncated the tail of one block (an open `@media` and a rule
inside it); every later rule — the whole local-map layout — was swallowed
into the unclosed block and silently stopped applying, while every other
gate stayed green until a browser test waited for a map that had no height.
Braces are cheap to count and this failure is silent, so count them.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STYLESHEETS = [
    ROOT / "static" / "atlas" / "atlas.css",
    ROOT / "static" / "atlas" / "globe.css",
    ROOT / "static" / "atlas" / "views.css",
    ROOT / "static" / "atlas" / "research.css",
    ROOT / "static" / "atlas" / "tours.css",
    ROOT / "static" / "atlas" / "phone.css",
    ROOT / "static" / "atlas" / "export.css",
    ROOT / "static" / "atlas" / "classroom.css",
]


def _strip_comments(text: str) -> str:
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def test_atlas_stylesheets_have_balanced_braces() -> None:
    for path in STYLESHEETS:
        text = _strip_comments(path.read_text(encoding="utf-8"))
        depth = 0
        for index, char in enumerate(text):
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                assert depth >= 0, f"{path.name}: stray closing brace at offset {index}"
        assert depth == 0, f"{path.name}: {depth} unclosed block(s) — every later rule is swallowed"


def test_local_map_layout_rules_are_top_level() -> None:
    """The map-route grid rules must be top-level selectors, not nested."""
    text = _strip_comments(STYLESHEETS[0].read_text(encoding="utf-8"))
    marker = "#atlas-main.is-map-route {"
    assert marker in text
    depth = text[: text.index(marker)].count("{") - text[: text.index(marker)].count("}")
    assert depth == 0, "the local-map block sits inside an unclosed earlier block"


# ---------------------------------------------------------------------------
# Design tokens: the palette's contrast and colour-vision claims are checked
# from the declarations themselves, so a casual edit to a hex value cannot
# quietly break the projector / colour-blind guarantees the stylesheet states.
# ---------------------------------------------------------------------------
MODEL_JS = ROOT / "static" / "atlas" / "js" / "model.js"
STAGE = ("#0f2231", "#060d14")  # the globe stage gradient (atlas.css .globe-stage)


def _tokens() -> dict[str, str]:
    text = STYLESHEETS[0].read_text(encoding="utf-8")
    root = text[text.index(":root {"):]
    root = _strip_comments(root[: root.index("\n}") + 2])
    return dict(re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", root))


def _rgb(hex_: str) -> tuple[float, ...]:
    h = hex_.strip().lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _luminance(rgb) -> float:
    r, g, b = (_lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast(a, b) -> float:
    la, lb = _luminance(a), _luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def _over(fg, alpha: float, bg):
    return tuple(f * alpha + b * (1 - alpha) for f, b in zip(fg, bg))


# Machado, Oliveira & Fernandes 2009, severity 1.0, applied in linear RGB.
_CVD = {
    "protan": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
    "deutan": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
    "tritan": ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900)),
}


def _unlin(c: float) -> float:
    c = max(0.0, min(1.0, c))
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def _simulate(rgb, kind: str):
    lin = [_lin(c) for c in rgb]
    return tuple(_unlin(sum(m * v for m, v in zip(row, lin))) for row in _CVD[kind])


def _lab(rgb):
    r, g, b = (_lin(c) for c in rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t: float) -> float:
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


def _distance(a, b) -> float:
    return sum((p - q) ** 2 for p, q in zip(_lab(a), _lab(b))) ** 0.5


STATUS_TOKENS = {
    "active": "--status-active",
    "upgrade": "--status-upgrade",
    "construction": "--status-construction",
    "planned": "--status-planned",
    "completed": "--status-completed",
    "retired": "--status-retired",
    "unrecorded": "--status-unrecorded",
}
GREYS = {"completed", "retired", "unrecorded"}


def test_text_tokens_meet_wcag_aa_on_every_atlas_surface() -> None:
    tokens = _tokens()
    surfaces = {name: _rgb(tokens[name]) for name in ("--paper", "--panel", "--panel-2")}
    for name in ("--white", "--muted", "--teal", "--amber", "--danger"):
        for surface, rgb in surfaces.items():
            ratio = _contrast(_rgb(tokens[name]), rgb)
            assert ratio >= 4.5, f"{name} is {ratio:.2f}:1 on {surface}; text needs 4.5:1"
    # The timeline bar is --navy-2: only the body and muted text colours sit on it.
    for name in ("--white", "--muted"):
        ratio = _contrast(_rgb(tokens[name]), _rgb(tokens["--navy-2"]))
        assert ratio >= 4.5, f"{name} is {ratio:.2f}:1 on --navy-2"


def test_control_boundary_meets_non_text_contrast() -> None:
    tokens = _tokens()
    boundary = _rgb(tokens["--line-strong"])
    for surface in ("--paper", "--panel", "--panel-2"):
        ratio = _contrast(boundary, _rgb(tokens[surface]))
        assert ratio >= 3.0, f"--line-strong is {ratio:.2f}:1 on {surface}; a control's edge needs 3:1"


def test_status_palette_contrast() -> None:
    tokens = _tokens()
    surfaces = [_rgb(tokens[n]) for n in ("--paper", "--panel", "--panel-2")] + [_rgb(h) for h in STAGE]
    for status, token in STATUS_TOKENS.items():
        colour = _rgb(tokens[token])
        for surface in surfaces:
            ratio = _contrast(colour, surface)
            assert ratio >= 3.0, f"{token} is {ratio:.2f}:1 on a surface; a status mark needs 3:1"
        if status != "unrecorded":
            ratio = _contrast(colour, _rgb(tokens["--panel-2"]))
            assert ratio >= 4.5, f"{token} is {ratio:.2f}:1 on --panel-2; only --status-unrecorded may be graphics-only"
    # A planned facility is drawn faded; the faded mark must still read on the stage.
    fade = float(tokens["--planned-fade"])
    planned = _rgb(tokens["--status-planned"])
    for stage in STAGE:
        ratio = _contrast(_over(planned, fade, _rgb(stage)), _rgb(stage))
        assert ratio >= 3.0, f"a planned facility at {fade} opacity is {ratio:.2f}:1 on the stage"


def test_status_palette_is_distinguishable_for_colour_blind_readers() -> None:
    tokens = _tokens()
    backdrop = _rgb(tokens["--panel-2"])
    colours = {s: _rgb(tokens[t]) for s, t in STATUS_TOKENS.items()}
    names = sorted(colours)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            floor = 10.0 if (a in GREYS and b in GREYS) else 15.0
            for kind in ("protan", "deutan", "tritan"):
                d = _distance(_simulate(colours[a], kind), _simulate(colours[b], kind))
                assert d >= floor, f"{a} vs {b} under {kind}: distance {d:.1f} < {floor}"
            assert _distance(colours[a], colours[b]) >= floor, f"{a} vs {b} are too close for anyone"
    assert backdrop  # the backdrop is only here to make the intent obvious to a reader


def test_model_js_status_colours_match_the_css_tokens() -> None:
    """model.js feeds the canvas/SVG code; the CSS tokens feed everything else."""
    tokens = _tokens()
    block = MODEL_JS.read_text(encoding="utf-8")
    block = block[block.index("export const STATUS_COLOR"):]
    block = block[: block.index("};")]
    js = dict(re.findall(r"(\w+):\s*'(#[0-9a-fA-F]{6})'", block))
    expect = {
        "active": "active", "upgrade": "upgrade", "commissioning": "construction",
        "construction": "construction", "approved": "planned", "proposed": "planned",
        "planned": "planned", "completed": "completed", "decommissioned": "retired",
        "shutdown": "retired", "unrecorded": "unrecorded",
    }
    assert set(js) == set(expect), "model.js STATUS_COLOR gained or lost a status"
    for status, family in expect.items():
        assert js[status].lower() == tokens[STATUS_TOKENS[family]].lower(), (
            f"model.js STATUS_COLOR.{status} drifted from {STATUS_TOKENS[family]}")


def test_institution_colour_is_not_a_status_colour() -> None:
    """Amber was both an institution dot and the "construction" status; the dot has its
    own colour now, far from every status colour, the accent amber and the facility-kind
    colours, and still readable on the globe's ocean."""
    tokens = _tokens()
    institution = _rgb(tokens["--institution"])
    others = {name: _rgb(tokens[token]) for name, token in STATUS_TOKENS.items()}
    others["--amber"] = _rgb(tokens["--amber"])
    others["--teal"] = _rgb(tokens["--teal"])
    kinds = MODEL_JS.read_text(encoding="utf-8")
    kinds = kinds[kinds.index("export const FACILITY_KIND_SHAPE"):]
    kinds = kinds[: kinds.index("};")]
    for kind, colour in re.findall(r"(\w+):\s*\{[^}]*color:\s*'(#[0-9a-fA-F]{6})'", kinds):
        others[kind] = _rgb(colour)
    assert len(others) > 15, "the facility-kind colours were not found in model.js"
    for name, colour in others.items():
        assert _distance(institution, colour) >= 15.0, f"--institution is too close to {name}"
        for kind in ("protan", "deutan", "tritan"):
            assert _distance(_simulate(institution, kind), _simulate(colour, kind)) >= 10.0, (
                f"--institution vs {name} under {kind}")
    for stage in STAGE:
        assert _contrast(institution, _rgb(stage)) >= 3.0


def test_key_beam_colours_match_the_globe_arcs() -> None:
    """The Key draws beam arcs from copies of the globe's own colours; they must not drift."""
    globe = (ROOT / "static" / "atlas" / "js" / "globe.js").read_text(encoding="utf-8")
    icons = (ROOT / "static" / "atlas" / "js" / "globeicons.js").read_text(encoding="utf-8")

    def pair(source: str, name: str) -> list[str]:
        match = re.search(rf"{name}\s*=\s*\[('rgba\([^']+\)'),\s*('rgba\([^']+\)')\]", source)
        assert match, f"{name} not found"
        return [m.strip("'") for m in match.groups()]

    assert pair(globe, "const BEAM_COLOR") == pair(icons.replace("running:", "const BEAM_COLOR ="), "const BEAM_COLOR")
    assert pair(globe, "const BEAM_GLOW_COLOR") == pair(icons.replace("glow:", "const BEAM_GLOW_COLOR ="), "const BEAM_GLOW_COLOR")
    assert pair(globe, "const BEAM_COLOR_QUIET") == pair(icons.replace("quiet:", "const BEAM_COLOR_QUIET ="), "const BEAM_COLOR_QUIET")


def test_type_scale_is_the_documented_one() -> None:
    tokens = _tokens()
    sizes = [int(tokens[f"--text-{n}"].removesuffix("px")) for n in ("xs", "sm", "md", "lg", "xl", "2xl", "3xl")]
    assert sizes == [12, 13, 15, 17, 20, 24, 32]


def test_no_literal_status_hex_survives_in_the_stylesheets() -> None:
    """The retired palette must not linger as a copy-paste in a rule."""
    retired = ("#4fd1a5", "#e6a25c", "#e6c25c", "#8a8fd6", "#7fd1e6", "#7d8b96", "#3d444a")
    for path in STYLESHEETS:
        text = path.read_text(encoding="utf-8").lower()
        for hex_ in retired:
            if path.name == "atlas.css" and hex_ in ("#7fd1e6", "#7d8b96"):
                continue  # local-map feature-type colours (beamline, road), not statuses
            assert hex_ not in text, f"{path.name} still carries the retired status colour {hex_}"


# ---------------------------------------------------------------------------
# Projector mode (classroom.css): the light theme is the same tokens redefined, so its
# contrast is measured from those declarations exactly as the standard theme's is. Body
# text is held to WCAG AAA (7:1), as a lecture hall's washed-out projector needs.
# ---------------------------------------------------------------------------
CLASSROOM_CSS = ROOT / "static" / "atlas" / "classroom.css"
SURFACES = ("--paper", "--panel", "--panel-2", "--navy", "--navy-2")


def _projector() -> dict[str, str]:
    text = _strip_comments(CLASSROOM_CSS.read_text(encoding="utf-8"))
    start = text.index(":root[data-theme='projector'] {")
    block = text[start: text.index("\n}", start) + 2]
    return dict(re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", block))


def test_projector_theme_redefines_the_surfaces_and_the_text() -> None:
    projector = _projector()
    for name in (*SURFACES, "--white", "--muted", "--teal", "--amber", "--danger", "--line", "--line-strong",
                 "--on-accent", "--on-amber"):
        assert name in projector, f"projector mode does not redefine {name}"
    # Light: every surface is lighter than every text colour.
    for surface in SURFACES:
        assert _luminance(_rgb(projector[surface])) > 0.6, f"{surface} is not a light surface"
    assert _luminance(_rgb(projector["--white"])) < 0.05, "body text is near-black on the projector theme"


def test_projector_body_text_is_at_least_7_to_1_on_every_surface() -> None:
    projector = _projector()
    for name in ("--white", "--muted"):
        for surface in SURFACES:
            ratio = _contrast(_rgb(projector[name]), _rgb(projector[surface]))
            assert ratio >= 7.0, f"{name} is {ratio:.2f}:1 on {surface}; projector body text needs 7:1"


def test_projector_accent_text_and_buttons_are_at_least_7_to_1() -> None:
    projector = _projector()
    for name in ("--teal", "--amber", "--danger"):
        for surface in SURFACES:
            ratio = _contrast(_rgb(projector[name]), _rgb(projector[surface]))
            assert ratio >= 7.0, f"{name} is {ratio:.2f}:1 on {surface}; accent text needs 7:1 here"
    for fill, ink in (("--teal", "--on-accent"), ("--amber", "--on-amber")):
        ratio = _contrast(_rgb(projector[ink]), _rgb(projector[fill]))
        assert ratio >= 7.0, f"{ink} on {fill} is {ratio:.2f}:1; a filled button's label needs 7:1"
    for surface in SURFACES:
        ratio = _contrast(_rgb(projector["--line-strong"]), _rgb(projector[surface]))
        assert ratio >= 3.0, f"--line-strong is {ratio:.2f}:1 on {surface}; a control's edge needs 3:1"


def test_projector_status_palette_keeps_the_standard_palette_guarantees() -> None:
    projector = _projector()
    surfaces = [_rgb(projector[n]) for n in ("--paper", "--panel", "--panel-2")]
    for status, token in STATUS_TOKENS.items():
        colour = _rgb(projector[token])
        for surface in surfaces:
            assert _contrast(colour, surface) >= 3.0, f"{token} is under 3:1 on a projector surface"
        if status != "unrecorded":
            ratio = _contrast(colour, _rgb(projector["--panel-2"]))
            assert ratio >= 4.5, f"{token} is {ratio:.2f}:1 on --panel-2"
    fade = float(projector["--planned-fade"])
    for surface in surfaces:
        faded = _over(_rgb(projector["--status-planned"]), fade, surface)
        assert _contrast(faded, surface) >= 3.0, "a planned facility, faded, must still read on the light surface"
    colours = {s: _rgb(projector[t]) for s, t in STATUS_TOKENS.items()}
    names = sorted(colours)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            floor = 10.0 if (a in GREYS and b in GREYS) else 15.0
            for kind in ("protan", "deutan", "tritan"):
                d = _distance(_simulate(colours[a], kind), _simulate(colours[b], kind))
                assert d >= floor, f"projector {a} vs {b} under {kind}: distance {d:.1f} < {floor}"
            assert _distance(colours[a], colours[b]) >= floor, f"projector {a} vs {b} are too close"


def test_projector_type_is_a_quarter_larger_and_strokes_are_thicker() -> None:
    standard, projector = _tokens(), _projector()
    for name in ("xs", "sm", "md", "lg", "xl", "2xl", "3xl"):
        was = int(standard[f"--text-{name}"].removesuffix("px"))
        now = int(projector[f"--text-{name}"].removesuffix("px"))
        assert 1.2 <= now / was <= 1.3, f"--text-{name}: {was}px -> {now}px is not the ~1.25x scale"
    assert int(projector["--marker-label-size"].removesuffix("px")) >= 15, "captions on the globe: 15px at least"
    assert float(projector["--beam-stroke-scale"]) > float(standard["--beam-stroke-scale"])
    css = _strip_comments(CLASSROOM_CSS.read_text(encoding="utf-8"))
    assert re.search(r"g\[pointer-events='none'\] > \* \{\s*stroke-width: (\d+(?:\.\d+)?)", css), "marker keylines"


def test_the_globe_stage_constants_are_not_redefined_by_the_projector_theme() -> None:
    """What is drawn on the dark Earth takes constants, so the globe reads the same in
    both themes: the glyph ink and the selection amber are never redefined."""
    projector, standard = _projector(), _tokens()
    for name in ("--globe-ink", "--globe-amber"):
        assert name in standard and name not in projector, name
    for stage in STAGE:
        assert _contrast(_rgb(standard["--globe-amber"]), _rgb(stage)) >= 4.5
    assert _contrast(_rgb("#1c1204"), _rgb(standard["--globe-amber"])) >= 7.0, "the selected caption's ink on amber"


def test_embed_mode_hides_the_chrome_and_keeps_the_open_link() -> None:
    css = _strip_comments(CLASSROOM_CSS.read_text(encoding="utf-8"))
    hidden = css[css.index("html.is-embed .atlas-header .brand"):]
    hidden = hidden[: hidden.index("}")]
    for selector in (".search-wrap", "#mode-buttons", ".atlas-footer", "#start-card", "#filters-btn"):
        assert selector in hidden, f"embed mode must hide {selector}"
    assert "html.is-embed:not(.embed-timeline) .timeline-bar" in css
    assert ".embed-open" in css and "html.is-embed .embed-open" in css
