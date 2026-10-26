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
    ROOT / "static" / "atlas" / "phone.css",
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
