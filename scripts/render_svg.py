"""Renders the animated terminal SVG.

Two things make this different from the usual profile terminal SVG:

1. Real typing. The reveal clip steps one character width at a time
   (calcMode="discrete") instead of sliding smoothly, and a block cursor rides
   the reveal edge, so it reads as someone typing rather than a wipe.
2. It loops. Every animation runs one shared cycle with repeatCount="indefinite",
   so a visitor who lands mid-cycle still sees the whole session instead of a
   frozen final frame.

No scripts, no external fonts, no external images - GitHub's camo proxy strips
all three, and SMIL plus inline CSS is what survives it.
"""

from __future__ import annotations

from script_lines import CMD, GAP, PROMPT_HOST, PROMPT_PATH

FONT_SIZE = 15
CHAR_W = 9.0            # 0.6 em advance, the ratio every common mono font shares
ROW_H = 26
GAP_H = 14

CANVAS_W = 900
MARGIN = 16
BAR_H = 42
CONTENT_X = 44
CONTENT_TOP = 96
BOTTOM_PAD = 34

CMD_CPS = 21.0          # a human at the keyboard
OUT_CPS = 95.0          # a program flushing stdout
START_DELAY = 0.7
PROMPT_PAUSE = 0.28     # prompt lands, then the first keystroke
AFTER_CMD_PAUSE = 0.32
AFTER_BLOCK_PAUSE = 0.62
END_HOLD = 4.5

CURSOR_W = 9
CURSOR_H = 18
CURSOR_SAMPLE_OUT = 3   # cursor keyframe every N chars on fast output lines
OFFSCREEN = -40         # cursor parking spot before the session starts

FONT_STACK = ('ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, '
              '"Liberation Mono", "DejaVu Sans Mono", monospace')


def render(lines: tuple, palette: dict, title: str) -> str:
    """Return the complete SVG document for one palette."""
    laid_out = _lay_out(lines)
    timeline = _schedule(laid_out)
    height = _canvas_height(laid_out)
    cycle = timeline["cycle"]

    body = [
        _defs(laid_out, timeline, palette, height),
        _window(palette, height),
        _title_bar(palette, title),
        _body_text(laid_out, palette),
        _cursor(timeline, palette, cycle),
    ]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" '
        f'height="{height}" viewBox="0 0 {CANVAS_W} {height}" '
        f'role="img" aria-label="{_esc(title)}">\n'
        + _styles(palette)
        + "".join(body)
        + "</svg>\n"
    )


# ---------------------------------------------------------------- layout


def _lay_out(lines: tuple) -> list[dict]:
    """Attach a y position and a character count to every rendered line."""
    prefix = _prompt_segments()
    prefix_chars = sum(len(text) for _, text in prefix)
    prefix_px = prefix_chars * CHAR_W

    placed = []
    y = CONTENT_TOP
    for line in lines:
        if line["kind"] == GAP:
            y += GAP_H
            continue
        if line["kind"] == CMD:
            segments = prefix + (("cmd", line["text"]),)
            typed = len(line["text"])
            base_px = prefix_px
        else:
            segments = line["segments"]
            typed = sum(len(text) for _, text in segments)
            base_px = 0.0
        placed.append({
            "kind": line["kind"],
            "segments": segments,
            "typed": typed,
            "base_px": base_px,
            "y": y,
        })
        y += ROW_H
    return placed


def _prompt_segments() -> tuple[tuple[str, str], ...]:
    return (
        ("user", PROMPT_HOST),
        ("dim", ":"),
        ("value", PROMPT_PATH),
        ("prompt", "$ "),
    )


def _canvas_height(laid_out: list[dict]) -> int:
    return int(laid_out[-1]["y"] + BOTTOM_PAD + MARGIN)


# ---------------------------------------------------------------- timing


def _schedule(laid_out: list[dict]) -> dict:
    """Walk the script once, recording when each character appears."""
    t = START_DELAY
    steps = []          # per line: list of (time, revealed_width)
    cursor = []         # (time, x, y)

    for index, line in enumerate(laid_out):
        is_cmd = line["kind"] == CMD
        cps = CMD_CPS if is_cmd else OUT_CPS
        per_char = 1.0 / cps
        line_steps = []

        if is_cmd:
            line_steps.append((t, line["base_px"]))
            cursor.append((t, line["base_px"], line["y"]))
            t += PROMPT_PAUSE

        sample = 1 if is_cmd else CURSOR_SAMPLE_OUT
        for i in range(1, line["typed"] + 1):
            at = t + (i - 1) * per_char
            width = line["base_px"] + i * CHAR_W
            line_steps.append((at, width))
            if i % sample == 0 or i == line["typed"]:
                cursor.append((at, width, line["y"]))

        t += line["typed"] * per_char
        t += AFTER_CMD_PAUSE if is_cmd else 0.0
        if not is_cmd and _block_ends(laid_out, index):
            t += AFTER_BLOCK_PAUSE
        steps.append(line_steps)

    return {"steps": steps, "cursor": cursor, "cycle": round(t + END_HOLD, 2)}


def _block_ends(laid_out: list[dict], index: int) -> bool:
    return index + 1 >= len(laid_out) or laid_out[index + 1]["kind"] == CMD


# ---------------------------------------------------------------- svg parts


def _styles(palette: dict) -> str:
    classes = ("title", "prompt", "user", "cmd", "muted", "value", "accent", "ok", "dim")
    rules = [f".{name} {{ fill: {palette[name]}; }}" for name in classes]
    return (
        "<style>\n"
        f"text {{ font: {FONT_SIZE}px {FONT_STACK}; white-space: pre; }}\n"
        f".title {{ font-size: 13px; }}\n"
        ".cmd { font-weight: 500; }\n"
        ".prompt { font-weight: 700; }\n"
        + "\n".join(rules) + "\n"
        + ".caret { animation: blink 1.06s steps(1, end) infinite; }\n"
        "@keyframes blink { 0%, 55% { opacity: 1; } 56%, 100% { opacity: 0; } }\n"
        "</style>\n"
    )


def _defs(laid_out: list[dict], timeline: dict, palette: dict, height: int) -> str:
    cycle = timeline["cycle"]
    clips = []
    for index, (line, steps) in enumerate(zip(laid_out, timeline["steps"])):
        values, key_times = _discrete_track(steps, cycle, lambda width: width, 0)
        clips.append(
            f'<clipPath id="r{index}">'
            f'<rect x="{CONTENT_X}" y="{line["y"] - ROW_H + 6}" height="{ROW_H}" width="0">'
            f'<animate attributeName="width" dur="{cycle}s" repeatCount="indefinite" '
            f'calcMode="discrete" values="{values}" keyTimes="{key_times}"/>'
            f"</rect></clipPath>"
        )
    return (
        "<defs>\n"
        + "\n".join(clips)
        + f'\n<filter id="cast" x="-20%" y="-20%" width="140%" height="140%">'
        f'<feDropShadow dx="0" dy="10" stdDeviation="14" flood-color="{palette["shadow"]}" '
        f'flood-opacity="{palette["shadow_opacity"]}"/></filter>'
        f'\n<linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="#ffffff" stop-opacity="0.06"/>'
        f'<stop offset="100%" stop-color="#ffffff" stop-opacity="0"/></linearGradient>'
        f'\n<radialGradient id="halo" cx="0.5" cy="0" r="0.9">'
        f'<stop offset="0%" stop-color="{palette["glow"]}" '
        f'stop-opacity="{palette["glow_opacity"]}"/>'
        f'<stop offset="100%" stop-color="{palette["glow"]}" stop-opacity="0"/>'
        f"</radialGradient>"
        f'\n<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
        f'<rect width="4" height="1" fill="#ffffff" fill-opacity="0.02"/></pattern>\n'
        "</defs>\n"
    )


def _window(palette: dict, height: int) -> str:
    inner_w = CANVAS_W - 2 * MARGIN
    inner_h = height - 2 * MARGIN
    return (
        f'<rect x="{MARGIN}" y="{MARGIN}" width="{inner_w}" height="{inner_h}" rx="14" '
        f'fill="{palette["window"]}" stroke="{palette["border"]}" stroke-width="1.2" '
        f'filter="url(#cast)"/>\n'
        f'<rect x="{MARGIN}" y="{MARGIN}" width="{inner_w}" height="{inner_h}" rx="14" '
        f'fill="url(#halo)"/>\n'
        f'<rect x="{MARGIN}" y="{MARGIN + BAR_H}" width="{inner_w}" '
        f'height="{inner_h - BAR_H}" fill="url(#scan)"/>\n'
    )


def _title_bar(palette: dict, title: str) -> str:
    inner_w = CANVAS_W - 2 * MARGIN
    bar_bottom = MARGIN + BAR_H
    dots = "".join(
        f'<circle cx="{cx}" cy="{MARGIN + 21}" r="6" fill="{color}"/>'
        for cx, color in ((42, "#ff5f57"), (62, "#febc2e"), (82, "#28c840"))
    )
    return (
        f'<path d="M{MARGIN} {MARGIN + 14}a14 14 0 0 1 14-14h{inner_w - 28}'
        f'a14 14 0 0 1 14 14v{BAR_H - 14}H{MARGIN}z" fill="{palette["bar"]}"/>\n'
        f'<rect x="{MARGIN}" y="{MARGIN}" width="{inner_w}" height="{BAR_H}" rx="14" '
        f'fill="url(#sheen)"/>\n'
        f'<line x1="{MARGIN}" y1="{bar_bottom}" x2="{CANVAS_W - MARGIN}" y2="{bar_bottom}" '
        f'stroke="{palette["border"]}" stroke-width="1"/>\n'
        f"{dots}\n"
        f'<text x="{CANVAS_W / 2}" y="{MARGIN + 26}" text-anchor="middle" class="title">'
        f"{_esc(title)}</text>\n"
    )


def _body_text(laid_out: list[dict], palette: dict) -> str:
    rows = []
    for index, line in enumerate(laid_out):
        spans = "".join(
            f'<tspan class="{cls}">{_esc(text)}</tspan>' for cls, text in line["segments"]
        )
        rows.append(
            f'<text x="{CONTENT_X}" y="{line["y"]}" xml:space="preserve" '
            f'clip-path="url(#r{index})">{spans}</text>'
        )
    return "<g>\n" + "\n".join(rows) + "\n</g>\n"


def _cursor(timeline: dict, palette: dict, cycle: float) -> str:
    events = timeline["cursor"]
    x_values, key_times = _discrete_track(
        [(t, x) for t, x, _ in events], cycle, lambda x: CONTENT_X + x, OFFSCREEN
    )
    y_values, _ = _discrete_track(
        [(t, y) for t, _, y in events], cycle, lambda y: y - CURSOR_H + 4, OFFSCREEN
    )
    return (
        f'<rect class="caret" width="{CURSOR_W}" height="{CURSOR_H}" rx="1.5" '
        f'fill="{palette["cursor"]}" x="-20" y="-20">\n'
        f'<animate attributeName="x" dur="{cycle}s" repeatCount="indefinite" '
        f'calcMode="discrete" values="{x_values}" keyTimes="{key_times}"/>\n'
        f'<animate attributeName="y" dur="{cycle}s" repeatCount="indefinite" '
        f'calcMode="discrete" values="{y_values}" keyTimes="{key_times}"/>\n'
        "</rect>\n"
    )


def _discrete_track(events: list, cycle: float, transform, initial: float) -> tuple[str, str]:
    """Build values/keyTimes for one looping discrete animation.

    The track holds `initial` from t=0 until its first event, so a line stays
    hidden until its turn, and holds its last value to the end of the cycle
    before the loop snaps everything back to the start.
    """
    values = [initial]
    key_times = [0.0]
    for at, raw in events:
        stamp = round(at / cycle, 5)
        if stamp <= key_times[-1]:
            stamp = key_times[-1] + 1e-5
        values.append(transform(raw))
        key_times.append(stamp)
    values.append(values[-1])
    key_times.append(1.0)
    return (
        ";".join(_num(v) for v in values),
        ";".join(_num(k) for k in key_times),
    )


def _num(value: float) -> str:
    text = f"{value:.5f}".rstrip("0").rstrip(".")
    return text or "0"


def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
