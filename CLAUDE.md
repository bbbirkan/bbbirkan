# Working on this repo

This is the profile README for `github.com/bbbirkan` (Birkan Kalyon). The two
graphics at the top are **generated**. Everything below is what you need to change
something safely without rediscovering it.

## Change X → edit Y

| To change | Edit | Then |
|---|---|---|
| Terminal text (commands, output, the story) | `scripts/script_lines.py` | rebuild + verify |
| Chip bar (DoD CLEARED, CDL-A, App Store…) | `scripts/render_badges.py` → `CHIPS` | rebuild + verify |
| Colors, either theme | `scripts/palette.py` | rebuild + verify |
| Typing speed, timing, layout, window size | `scripts/render_svg.py` (constants at top) | rebuild + verify |
| Window title | `scripts/build.py` → `WINDOW_TITLE` | rebuild |
| Prose, project list, links | `README.md` directly | check links |

**Never hand-edit `assets/*.svg`.** They are ~25 KB of generated markup and the daily
GitHub Action will silently overwrite your edit on its next run.

## The loop, every time

```bash
python3 scripts/build.py                                   # writes 4 SVGs + stats.json
pytest tests/                                              # 14 guards, must stay green
python3 scripts/visual_check.py --svg assets/terminal-dark.svg   # opens it and looks
```

`visual_check.py` is not optional for anything visual. It loads the SVG through an
`<img>` data URI — the same sandbox GitHub's camo proxy imposes — drives the animation
clock with `setCurrentTime` so frames are deterministic, screenshots six moments plus the
loop-reset frame, and exits non-zero on any console/page/network error. **Look at the
PNGs.** "The code looks right" and "curl returned 200" have both been wrong here before.

Tests catch the invisible failures: text overflowing the window, invalid SMIL `keyTimes`,
an external reference camo would strip, the two palettes drifting apart geometrically.

## Constraints that are not negotiable

- **No scripts, no remote fonts, no remote images.** GitHub's camo proxy strips all three.
  Animation is SMIL + inline CSS only. A test enforces this.
- **Everything loops.** One shared cycle, `repeatCount="indefinite"`, so a visitor landing
  mid-cycle sees the whole session instead of a frozen final frame.
- **Chips are local, not shields.io.** No external host to go down, no camo cache of
  someone else's image, colors stay in sync with `palette.py`.
- Camo caches aggressively. After a push the old graphic can persist for a while — that is
  a cache, not a failed deploy. Check `raw.githubusercontent.com` to see the truth.

## Verified facts — do not re-guess these

| Fact | Value |
|---|---|
| Live company domain | **anvilon.net** — `anvilon.us` is DEAD (HTTP 000), never link it |
| Name | Birkan **Kalyon** (the repo description said "Yıldız" once — wrong) |
| Title | Founder & Systems Engineer (not "Engineering Lead") |
| The YouTube pipeline | Belongs to **Voltara Signal**, nothing else |
| platonservis.com | A repair shop built for family. **Keep it off the profile.** |
| Voltara Signal | Financial intelligence API, **live on RapidAPI**, 21 channels, 3,200+ transcripts |
| Covenant Fuel | Enterprise work for Covenant Logistics (Nasdaq: CVLG), 2,500+ trucks |
| President Politics | 27,564 posts. Magnitude predictable, direction never. Historical analysis, **not prediction** — keep that framing |
| Anvilon service ladder | Forensic audit → automation dashboards → custom applications |
| Positioning | *"Your data hides money. We find it."* Data/API first, then iOS/web |

## Editorial rules learned the hard way

- **Few and strong beats many.** A list of small brochure sites next to a RapidAPI product
  and a Nasdaq-carrier engagement averages the portfolio *down*. It was cut for that reason.
- **Never invent metrics.** Proficiency bars implying made-up percentages were removed.
  If a number isn't on anvilon.net, the CV, or the API, it doesn't go in.
- **anvilon.net is the source of truth** for what each product is. Read it before writing
  product copy — the old README was stale and caused several wrong attributions.
- Verify every outbound link (`curl -o /dev/null -w '%{http_code}'`) before pushing.

## Live data

`build.py` pulls the repo count from the GitHub API and caches it in `assets/stats.json`,
so a tokenless run refreshes the date without reverting the count. The daily Action
(`.github/workflows/terminal.yml`, 06:17 UTC) runs `--no-live` unless a `PROFILE_TOKEN`
secret exists. That secret is **not** set today — this is expected, not a bug.
