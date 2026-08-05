<!-- Both graphics below are generated: `python3 scripts/build.py`, rebuilt daily
     by .github/workflows/terminal.yml. Edit scripts/script_lines.py, not the SVG. -->
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/terminal-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/terminal-light.svg">
    <img alt="birkan@anvilon: ~/profile" src="assets/terminal-dark.svg" width="900">
  </picture>
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/credentials-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/credentials-light.svg">
    <img alt="DoD cleared · CDL-A · TWIC · iOS on the App Store · Anvilon LLC, Salem NJ" src="assets/credentials-dark.svg" width="900">
  </picture>
</p>

<p align="center">
  <a href="https://anvilon.net"><b>anvilon.net</b></a> ·
  <a href="https://birkan.us">birkan.us</a> ·
  <a href="mailto:info@birkan.us">info@birkan.us</a> ·
  <a href="https://linkedin.com/in/birkan-kalyon">LinkedIn</a>
</p>

---

## Shipped

**[Voltara Signal](https://voltara.anvilon.net)** — financial intelligence API, live on RapidAPI
21 finance channels watched around the clock, 3,200+ transcripts indexed, AI-extracted
sentiment per ticker — and every directional call scored against the actual market-adjusted
return, not just logged. Query a stock, get the signal in milliseconds.
`FastAPI` `NLP pipeline` `PostgreSQL` · *informational sentiment data, not investment advice*

**Covenant Fuel** — enterprise iOS + dashboard for a Nasdaq-listed carrier
A fuel logic engine for Covenant Logistics (CVLG): 2,500+ trucks, refueling decisions
optimized against net margin. Native iOS app plus a PWA dashboard.
`Swift` `TypeScript` `PWA` — [covenantfuel.com](https://covenantfuel.com)

**[Waymind](https://waymind.net)** — iOS · [live on the App Store](https://apps.apple.com/us/app/waymind/id6757075542)
Zero-latency spatial distance analysis in a 2.4 MB binary. 100% on-device — no cloud, no leaks.
`Swift` `SwiftUI` `MapKit` `StoreKit` — designed, built, submitted and shipped solo.

**Digital Fleet Core** — the whole digital backbone for CanAuto Group and CanAuto Care,
unifying showrooms and service centers. Client since 2018, still shipping.

---

## [Anvilon Data Division](https://anvilon.net/data) — research, published either way

**Dead Load** — *why 4 in 5 trucking owner-operators don't survive five years*
Monte Carlo survival analysis, n=10,000, with a simulator you can run yourself. I've spent
three years inside America's most independent industry; this is the model of what actually
kills the businesses in it.

**The Red Line's Whisper** — *are falling fertility rates a crisis or a correction?*
A demographic engine simulating population shift out to 2100, testing the "rational pause"
theory rather than assuming the panic.

**[President Politics](https://president-politics.anvilon.net)** — 27,564 presidential posts scored against Mag7 price reactions since
2022. Magnitude turned out predictable; direction never did. The negative result is the
finding, and it's published — SSRN paper filed.

`Python` `Monte Carlo` `React` `Recharts` · [read the research →](https://anvilon.net/data)

---

## What I'm building now

**Indexes, sold by the query.** This is the direction the studio is heading. Voltara Signal is
the template: take a public stream nobody has structured — thousands of hours of finance video —
index it, extract entities and sentiment with an NLP pipeline, score every call against what the
market actually did, then sell API access to the index instead of a PDF report. The corpus is
the asset; the endpoint is the product. More indexes are being built the same way.

**Validation that actually validates.** The backtesting work taught me the expensive lesson —
a gate that always passes isn't a gate. So the harnesses now get fed deliberately cheating
inputs and have to catch them, and look-ahead detection runs before any result is believed.

**Turning operational exhaust into decisions.** Field-service businesses already generate the
data that answers their expensive questions; it's just scattered across spreadsheets, dispatch
calls and someone's memory. Extraction, modelling, then a dashboard nobody needs training for.

Most of this lives in private repos. Ask and I'll walk you through any of it.

---

## The unusual part

Most engineers learn logistics from a dataset. I learned it at 3 a.m. in a 53-foot dry van,
watching a dispatcher solve with a phone call what should have been a database query.

That's the whole thesis. Three years of interstate driving — 2,000–2,500 miles a week, zero
accidents, zero violations — showed me exactly where the paper and the guesswork still live.
A DoD clearance showed me what it costs when a process genuinely isn't allowed to fail.
I build for constraints I've stood inside, not ones I imagined.

> "You can't automate what you don't understand."

---

## Stack

```
Data        PostgreSQL · DuckDB · SQLite · pandas · backtesting harnesses
Automation  Python · n8n · Claude/OpenAI/Gemini APIs · Whisper
iOS         Swift · SwiftUI · UIKit · Core Data · MapKit · StoreKit
Web         Next.js · React · TypeScript · Vite · Tailwind · PocketBase
Infra       Docker · Coolify · Cloudflare · Contabo · GitHub Actions
Markets     Alpaca API · Coinbase API · Pine Script / TradingView
```

---

## Work with me

### [Anvilon LLC](https://anvilon.net) — *"Your data hides money. We find it."*

A small New Jersey systems studio for field-service operations. The engagement ladder is
deliberately short:

| | |
|---|---|
| **1 · Forensic systems audit** | 30–40 hours of analysis, one-time fee, zero ongoing commitment. Find where the money is leaking. |
| **2 · Automation dashboards** | Findings become live dashboards and workflows. Build once, run forever. |
| **3 · Custom applications** | Native iOS and the data pipelines behind it. |

**→ [anvilon.net](https://anvilon.net)** · [info@birkan.us](mailto:info@birkan.us)

<p align="center">
  <sub>Salem, New Jersey · building from the cab</sub>
</p>
