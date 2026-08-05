"""The terminal session content: what gets typed and what it prints back.

A line is either a command (typed slowly, character by character) or program
output (dumped fast). Segments carry a color class so a single line can mix
accent, value and muted text.

Only verifiable facts belong here - the footer numbers are injected at build
time from the live GitHub API, never hand-written.
"""

from __future__ import annotations

CMD = "cmd"
OUT = "out"
GAP = "gap"

PROMPT_HOST = "birkan@anvilon"
PROMPT_PATH = "~"


def build_lines(stats: dict[str, str]) -> tuple[dict, ...]:
    """Return the ordered session script, with live stats woven into the footer."""
    return (
        command("whoami"),
        output([("value", "Birkan Kalyon"), ("muted", " · Founder & Systems Engineer @ "),
                ("accent", "Anvilon LLC")]),
        gap(),

        command("cat motd.txt"),
        output([("muted", "DoD-cleared CDL-A driver by day, systems engineer by night.")]),
        output([("muted", "I haul sensitive freight across the US and build the data")]),
        output([("muted", "systems that field operations still run on paper.")]),
        output([("accent", "Your data hides money. "), ("muted", "The job is finding it.")]),
        gap(),

        command("ls -1 ~/shipped"),
        output([("accent", "voltara-signal    "), ("muted", "sentiment API · RapidAPI      "),
                ("ok", "live")]),
        output([("accent", "covenant-fuel     "), ("muted", "iOS + dashboard · 2,500 rigs  "),
                ("ok", "enterprise")]),
        output([("accent", "waymind.net       "), ("muted", "Swift · MapKit · on-device    "),
                ("ok", "App Store")]),
        gap(),

        command("cat stack.txt"),
        output([("value", "data     "), ("muted", "postgres · duckdb · pandas · backtesting")]),
        output([("value", "api      "), ("muted", "fastapi · python · nlp pipelines")]),
        output([("value", "ios      "), ("muted", "swift · swiftui · core data · mapkit")]),
        output([("value", "web      "), ("muted", "next.js · typescript · cloudflare")]),
        gap(),

        command("tail -f now.log"),
        output([("prompt", "[live] "), ("muted", "forensic data audits · "),
                ("value", f"{stats['repos']} repos"), ("muted", " · built "),
                ("value", stats["built_at"])]),
    )


def command(text: str) -> dict:
    return {"kind": CMD, "text": text}


def output(segments: list) -> dict:
    return {"kind": OUT, "segments": tuple(segments)}


def gap() -> dict:
    return {"kind": GAP}
