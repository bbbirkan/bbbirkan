"""Renders the credentials bar that sits under the terminal.

A slim row of chips a visitor reads in about a second: the credential, the
shipped app, the company. Same palette and font metrics as the terminal so the
two graphics read as one design rather than a badge service bolted on.

Deliberately local rather than shields.io - no external host to go down, no
camo cache of someone else's SVG, and the colors stay in sync with the palette.
"""

from __future__ import annotations

CHAR_W = 7.2            # 0.6 em advance at the 12px chip font size
FONT_SIZE = 12
CHIP_H = 30
CHIP_GAP = 10
CHIP_PAD_X = 14
DOT_R = 4
DOT_GAP = 9
BAR_H = 52
CANVAS_W = 900

FONT_STACK = ('ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, '
              '"Liberation Mono", "DejaVu Sans Mono", monospace')

CHIPS = (
    ("ok", "DoD CLEARED"),
    ("value", "CDL-A · TWIC"),
    ("accent", "iOS · LIVE ON THE APP STORE"),
    ("user", "ANVILON LLC · SALEM, NJ"),
)


def render(palette: dict) -> str:
    """Return the credentials bar SVG for one palette."""
    chips = [(tone, label, _chip_width(label)) for tone, label in CHIPS]
    total = sum(width for _, _, width in chips) + CHIP_GAP * (len(chips) - 1)
    x = (CANVAS_W - total) / 2
    y = (BAR_H - CHIP_H) / 2

    parts = []
    for tone, label, width in chips:
        parts.append(_chip(x, y, width, tone, label, palette))
        x += width + CHIP_GAP

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{BAR_H}" '
        f'viewBox="0 0 {CANVAS_W} {BAR_H}" role="img" '
        f'aria-label="{", ".join(label for _, label in CHIPS)}">\n'
        f"<style>text {{ font: 600 {FONT_SIZE}px {FONT_STACK}; letter-spacing: 0.4px; }}</style>\n"
        + "".join(parts)
        + "</svg>\n"
    )


def _chip(x: float, y: float, width: float, tone: str, label: str, palette: dict) -> str:
    color = palette[tone]
    text_x = x + CHIP_PAD_X + DOT_R * 2 + DOT_GAP
    return (
        f'<g><rect x="{x:.1f}" y="{y}" width="{width:.1f}" height="{CHIP_H}" rx="{CHIP_H / 2}" '
        f'fill="{palette["bar"]}" stroke="{palette["border"]}" stroke-width="1"/>'
        f'<circle cx="{x + CHIP_PAD_X + DOT_R:.1f}" cy="{y + CHIP_H / 2}" r="{DOT_R}" '
        f'fill="{color}"/>'
        f'<text x="{text_x:.1f}" y="{y + CHIP_H / 2 + 4.2}" fill="{color}">'
        f"{_esc(label)}</text></g>\n"
    )


def _chip_width(label: str) -> float:
    return CHIP_PAD_X * 2 + DOT_R * 2 + DOT_GAP + len(label) * CHAR_W


def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
