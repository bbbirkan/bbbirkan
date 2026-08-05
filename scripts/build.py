#!/usr/bin/env python3
"""Build the animated terminal SVGs for the GitHub profile README.

Usage:
    python3 scripts/build.py [--out assets] [--no-live]

Live numbers come from the GitHub API so the footer line never goes stale.
When the API is unreachable the build still succeeds using the last committed
numbers, but it says so on stderr rather than pretending the data is fresh.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import render_badges
from palette import PALETTES
from render_svg import render
from script_lines import build_lines

GITHUB_USER = "bbbirkan"
API_URL = f"https://api.github.com/users/{GITHUB_USER}"
WINDOW_TITLE = "birkan@anvilon: ~/profile"
STATS_FILE = "stats.json"
SEED_REPOS = 64          # only used the very first time, before stats.json exists
HTTP_TIMEOUT = 15


def main() -> int:
    args = _parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    stats_path = out_dir / STATS_FILE

    stats = fetch_stats(stats_path, live=not args.no_live)
    lines = build_lines(stats)

    written: list[tuple[Path, int]] = []
    for palette in PALETTES:
        target = out_dir / f"terminal-{palette['name']}.svg"
        target.write_text(render(lines, palette, WINDOW_TITLE), encoding="utf-8")
        written.append((target, target.stat().st_size))

        chips = out_dir / f"credentials-{palette['name']}.svg"
        chips.write_text(render_badges.render(palette), encoding="utf-8")
        written.append((chips, chips.stat().st_size))

    for target, size in written:
        print(f"wrote {target}  ({size / 1024:.1f} KB)")
    return 0


def fetch_stats(stats_path: Path, live: bool = True) -> dict[str, str]:
    """Live repo count when a token is around, last known count otherwise.

    The last successful count is committed to stats.json so a tokenless run
    (a scheduled Action, say) refreshes the date without silently reverting
    the repo count to whatever was hard-coded months ago.
    """
    built_at = datetime.now(timezone.utc).date().isoformat()
    last_known = _load_last_known(stats_path)

    if not live:
        return {"repos": last_known, "built_at": built_at}

    try:
        repos = str(_repo_count())
    except (urllib.error.URLError, OSError, ValueError, KeyError) as exc:
        print(f"warning: live stats unavailable ({exc}); reusing repos={last_known}",
              file=sys.stderr)
        return {"repos": last_known, "built_at": built_at}

    stats_path.write_text(json.dumps({"repos": repos}) + "\n", encoding="utf-8")
    return {"repos": repos, "built_at": built_at}


def _load_last_known(stats_path: Path) -> str:
    try:
        return str(json.loads(stats_path.read_text(encoding="utf-8"))["repos"])
    except (OSError, ValueError, KeyError):
        return str(SEED_REPOS)


def _repo_count() -> int:
    """Total repos including private ones when a token is available."""
    token = os.environ.get("GITHUB_TOKEN") or _gh_cli_token()
    if token:
        request = urllib.request.Request(
            "https://api.github.com/user/repos?per_page=1&affiliation=owner",
            headers={"Authorization": f"Bearer {token}",
                     "Accept": "application/vnd.github+json",
                     "User-Agent": "bbbirkan-profile-build"},
        )
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
            link = response.headers.get("Link", "")
        count = _last_page(link)
        if count:
            return count

    request = urllib.request.Request(
        API_URL, headers={"User-Agent": "bbbirkan-profile-build"}
    )
    with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
        payload = json.load(response)
    return payload["public_repos"]


def _last_page(link_header: str) -> int | None:
    """With per_page=1 the last page number equals the total repo count."""
    for part in link_header.split(","):
        if 'rel="last"' not in part:
            continue
        url = part.split(";")[0].strip().strip("<>")
        for chunk in url.split("?")[-1].split("&"):
            key, _, value = chunk.partition("=")
            if key == "page" and value.isdigit():
                return int(value)
    return None


def _gh_cli_token() -> str | None:
    try:
        result = subprocess.run(["gh", "auth", "token"], capture_output=True, check=False,
                                text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="assets", help="output directory")
    parser.add_argument("--no-live", action="store_true",
                        help="skip the GitHub API call and use committed numbers")
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
