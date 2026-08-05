"""Guards for the generated terminal SVG.

These are the failure modes that are invisible in a diff: text that quietly
overflows the window, an animation that stops looping, or an external reference
that GitHub's camo proxy will strip so the badge renders blank for everyone but
the author.
"""

from __future__ import annotations

import itertools
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import render_svg
from palette import PALETTES
from render_svg import CANVAS_W, CHAR_W, CONTENT_X, MARGIN, render
from script_lines import build_lines

SVG_NS = "{http://www.w3.org/2000/svg}"
STATS = {"repos": "64", "built_at": "2026-08-05"}


@pytest.fixture(params=[p["name"] for p in PALETTES])
def document(request) -> str:
    palette = next(p for p in PALETTES if p["name"] == request.param)
    return render(build_lines(STATS), palette, "birkan@anvilon: ~/profile")


def test_renders_well_formed_xml(document: str) -> None:
    root = ET.fromstring(document)
    assert root.tag == f"{SVG_NS}svg"
    assert root.get("viewBox").startswith(f"0 0 {CANVAS_W} ")


def test_has_no_external_or_scripted_content(document: str) -> None:
    """camo strips scripts, remote fonts and remote images - none may be needed."""
    assert "<script" not in document
    assert "@import" not in document
    assert not re.search(r'(href|src)\s*=\s*"https?:', document)
    assert not re.search(r"url\(\s*['\"]?https?:", document)


def test_every_animation_loops_on_one_shared_cycle(document: str) -> None:
    root = ET.fromstring(document)
    durations = {a.get("dur") for a in root.iter(f"{SVG_NS}animate")}
    repeats = {a.get("repeatCount") for a in root.iter(f"{SVG_NS}animate")}
    assert len(durations) == 1, f"animations disagree on cycle length: {durations}"
    assert repeats == {"indefinite"}


def test_key_times_are_valid_smil(document: str) -> None:
    root = ET.fromstring(document)
    for animation in root.iter(f"{SVG_NS}animate"):
        values = animation.get("values").split(";")
        key_times = [float(k) for k in animation.get("keyTimes").split(";")]
        assert len(values) == len(key_times)
        assert key_times[0] == 0.0
        assert key_times[-1] == 1.0
        assert all(a < b for a, b in itertools.pairwise(key_times)), "keyTimes must rise"


def test_no_line_overflows_the_window(document: str) -> None:
    root = ET.fromstring(document)
    right_edge = CANVAS_W - MARGIN
    for text in root.iter(f"{SVG_NS}text"):
        if text.get("clip-path") is None:
            continue  # the centred title bar caption, not a terminal row
        chars = sum(len(span.text or "") for span in text)
        end = CONTENT_X + chars * CHAR_W
        assert end <= right_edge, f"line overflows by {end - right_edge:.0f}px: {chars} chars"


def test_reveal_ends_wide_enough_to_show_the_whole_line(document: str) -> None:
    """A clip that stops short would silently truncate the last characters."""
    root = ET.fromstring(document)
    texts = [t for t in root.iter(f"{SVG_NS}text") if t.get("clip-path")]
    clips = {c.get("id"): c for c in root.iter(f"{SVG_NS}clipPath")}

    for text in texts:
        clip_id = text.get("clip-path")[len("url(#"):-1]
        animation = clips[clip_id].find(f"{SVG_NS}rect/{SVG_NS}animate")
        final_width = float(animation.get("values").split(";")[-1])
        chars = sum(len(span.text or "") for span in text)
        assert final_width >= chars * CHAR_W - 0.01


def test_palettes_differ_but_geometry_does_not() -> None:
    lines = build_lines(STATS)
    dark, light = (render(lines, p, "t") for p in PALETTES)
    assert dark != light
    colors_only = re.compile(r'#[0-9a-fA-F]{3,8}|(?:flood|stop)-opacity="[\d.]+"')
    assert colors_only.sub("", dark) == colors_only.sub("", light)


def test_output_dumps_faster_than_a_human_types() -> None:
    assert render_svg.OUT_CPS > render_svg.CMD_CPS * 2
