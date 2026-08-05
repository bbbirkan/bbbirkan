#!/usr/bin/env python3
"""Open the terminal SVG in a real browser and look at it.

Two passes, because each proves something different:

* sandbox pass - loads the SVG through an <img> data URI, which is the same
  sandbox GitHub's camo proxy imposes (SMIL and inline CSS run, scripts and
  external references do not). Catches decode failures and blocked resources.
* frame pass - inlines the same SVG and drives its clock with setCurrentTime,
  so frames land on exact animation times instead of drifting by however long
  the previous screenshot took.

Usage:
    python3 scripts/visual_check.py [--svg assets/terminal-dark.svg] [--out /tmp/shots]
"""

from __future__ import annotations

import argparse
import base64
import sys
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

FRAME_TIMES = (0.5, 2.5, 6.0, 9.5, 13.0, 15.5)
VIEWPORT = {"width": 960, "height": 720}
SETTLE_MS = 260


def main() -> int:
    args = _parse_args()
    svg_path = Path(args.svg).resolve()
    if not svg_path.exists():
        print(f"error: {svg_path} not found", file=sys.stderr)
        return 1

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    markup = svg_path.read_text(encoding="utf-8")
    problems: list[str] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport=VIEWPORT)
        _watch(page, problems)

        _sandbox_pass(page, svg_path, problems)
        cycle = _frame_pass(page, markup, out_dir, svg_path.stem)
        browser.close()

    print(f"animation cycle: {cycle}s")
    if problems:
        print("\nPROBLEMS:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1
    print("no console/page/network errors")
    return 0


def _sandbox_pass(page: Page, svg_path: Path, problems: list[str]) -> None:
    encoded = base64.b64encode(svg_path.read_bytes()).decode("ascii")
    page.set_content(
        "<style>html,body{margin:0}</style>"
        f'<img src="data:image/svg+xml;base64,{encoded}" width="900">'
    )
    page.wait_for_selector("img")
    width, height = page.evaluate(
        "() => { const i = document.querySelector('img');"
        " return [i.naturalWidth, i.naturalHeight]; }"
    )
    if width == 0:
        problems.append("svg failed to decode in an <img> (naturalWidth == 0)")
    print(f"intrinsic size: {width}x{height}")


def _frame_pass(page: Page, markup: str, out_dir: Path, stem: str) -> float:
    page.set_content(
        "<style>html,body{margin:0;background:#22272e;display:flex;"
        "align-items:center;justify-content:center;height:100vh}"
        "svg{display:block}</style>" + markup
    )
    page.wait_for_selector("svg")
    cycle = page.evaluate(
        "() => parseFloat(document.querySelector('animate').getAttribute('dur'))"
    )

    for at in FRAME_TIMES:
        page.evaluate(
            "(t) => { const s = document.querySelector('svg');"
            " s.pauseAnimations(); s.setCurrentTime(t); }",
            at,
        )
        page.wait_for_timeout(SETTLE_MS)
        shot = out_dir / f"{stem}-t{at:05.1f}s.png"
        page.locator("svg").screenshot(path=str(shot))
        print(f"captured {shot.name}")

    # One frame just past the loop point: proves the cycle resets to empty.
    page.evaluate(
        "(t) => { const s = document.querySelector('svg'); s.setCurrentTime(t); }",
        cycle + 0.5,
    )
    page.wait_for_timeout(SETTLE_MS)
    loop_shot = out_dir / f"{stem}-loop.png"
    page.locator("svg").screenshot(path=str(loop_shot))
    print(f"captured {loop_shot.name}")
    return cycle


def _watch(page: Page, problems: list[str]) -> None:
    page.on("pageerror", lambda err: problems.append(f"pageerror: {err}"))
    page.on(
        "console",
        lambda msg: problems.append(f"console.error: {msg.text}")
        if msg.type == "error"
        else None,
    )
    page.on("requestfailed", lambda req: problems.append(f"requestfailed: {req.url}"))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--svg", default="assets/terminal-dark.svg")
    parser.add_argument("--out", default="/tmp/terminal-shots")
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
