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
