# Lane handoff — WildlifeStats Architect

**Date:** 2026-06-10 ~14:00 ET
**For:** the new WildlifeStats Architect session spawning now
**From:** the prior architect of the joint sessions (`coastal-thistle-bronze-cairn` in BRWC lane)

## Scope

Architect for the **WildlifeStats.org** platform — a new, national wildlife rehabilitation research framework. Public-facing brand: WildlifeStats. Single primary repo: **askoak/wildlifestats-org**.

You partner with the WildlifeStats Engineer session. You do NOT coordinate with BRWC sessions — see Standing Orders §19 and §20 in the askoak/askoak-web repo for boundary rules.

## What WildlifeStats IS

- A national wildlife rehabilitation research framework
- Public-facing tools (national admissions dashboard, One Health hub, species encyclopedia, national-parks lens, searchable national database)
- Will host **synthetic data scaled to n=100,000** — proportional scale-up of a real wildlife center's distribution PLUS a generated multi-state county overlay so the map covers all 50 states + DC, NOT just one region
- Targets researchers, policy stakeholders, educators, journalists, conservation orgs, and citizen scientists
- Branded NEUTRALLY for national audience — no specific real wildlife center named on the public tier

## What WildlifeStats IS NOT

- NOT a clone of any specific wildlife center's site
- NOT real-time live data (it's a methodology demonstration)
- NOT a fundraising platform for any specific center
- NOT a triage-replacement (the Wildlife911 routing pattern from BRWC carries over conceptually but in WildlifeStats it's an educational encyclopedia)
- NOT something that mentions BRWC, Blue Ridge Wildlife Center, Dr. Jen Riley, Boyce VA, or any other identifying detail of the real source organization

A future authenticated tier at `wildlifestats.org/secure/` (engineer order pending) will mirror a real wildlife center's staff tools for Mike's private testing. That is the ONLY place real center data appears under the WildlifeStats brand, and it is auth-gated.

## First moves on session start

1. **Generate your seat signature.** Suggested format: `<adjective>-<plant>-<gem>-<bird>` to visually distinguish from the BRWC lane's `<weather>-<plant>-<metal>-<artifact>` pattern. Example: `vivid-aster-amber-warbler`. Lock it.
2. **Clone the repo:** `git clone https://github.com/askoak/wildlifestats-org.git /tmp/wildlifestats-org` (or pull if already cloned).
3. **Read the askoak-web Standing Orders** at `https://raw.githubusercontent.com/askoak/askoak-web/main/docs/handoff/STANDING-ORDERS.md`. Twenty rules; §19–20 govern lane discipline. You inherit ALL of them. They are canonical from the BRWC repo; you do not re-author them.
4. **Read the master plan:** `https://raw.githubusercontent.com/askoak/askoak-web/main/docs/handoff/wildlifestats-master-plan-2026-06-10.md` — the source of truth for what WildlifeStats will become across ~3 weeks of phased work.
5. **Verify GitHub auth in your session:** `gh repo view askoak/wildlifestats-org`.
6. **Greet Mike** with your seat signature and confirm WildlifeStats lane.

## Current state of WildlifeStats

### What exists right now

- **Repo:** askoak/wildlifestats-org (private) — created today 2026-06-10 ~13:48 ET
- **Live site:** wildlifestats.netlify.app serves a single-file placeholder index.html
- **Custom domain:** wildlifestats.org (Mike owns, DNS may or may not be pointed at Netlify yet — check)
- **Defensive redirect:** wildlifestats.com → wildlifestats.org (also Mike-owned; same DNS pending)
- **Netlify site name:** `wildlifestatsorg` (linked to this repo, base/build/publish all blank — pure-HTML deployment)

### What lives in the repo today

```
/                          (repo root)
  index.html               placeholder ("In development" page)
  README.md                short framework intro
  docs/
    handoff/
      LANE-HANDOFF-wildlifestats-architect-2026-06-10.md   (this file)
      LANE-HANDOFF-wildlifestats-engineer-2026-06-10.md
```

That is the entire repo. Bring it from there.

### What does NOT exist yet

- Logo (in flight — Mike is running v2.0 prompts in Gemini; embroidery-first oak-leaf-as-histogram + chipmunk mascot)
- Brand color tokens (proposed: deeper slate `#2A3F52` + warm clay `#B96F4D` + muted sage `#6B8264` on cream — subject to Mike's call)
- Synthetic n=100,000 cube — needs generation
- Any actual content beyond the placeholder
- The `/secure/` authenticated tier
- All Phase 2–6 work from the master plan

## Master plan summary (read the full doc; this is the elevator)

- **Phase 0** (today, ~done): defensive Netlify config, repo created, placeholder live
- **Phase 1:** structural fork from BRWC's public site layout (clone the IA, drop the BRWC content)
- **Phase 2:** rebrand sweep — replace every BRWC reference with WildlifeStats / national framing; new color palette and logo when Mike's logos land
- **Phase 3:** synthetic n=100,000 cube — proportional scale-up + multi-state county overlay. Architect generates; engineer wires into the site
- **Phase 4:** national-features layer — One Health hub, National Parks lens, Wildlife encyclopedia, searchable national database, multi-format ingestion sandbox
- **Phase 5:** authenticated tier `/secure/` mirroring BRWC staff site for Mike's testing
- **Phase 6:** SEO + governance polish — sitemap, schema.org Dataset markup, governance page

## Open questions Mike has deferred (don't ask again unless they actually block)

- Color palette finalization (waiting on logo)
- Whether the `/secure/` tier uses the BRWC staff passcode or its own credential (BRWC passcode is the architect default)
- Whether WildlifeStats should ever brand-acknowledge the underlying data source (default: stay silent)

## Logos: in-flight (NOT a blocker)

Mike will run three v2.0 prompts in Gemini at his own pace:
- A-v2: embroidery-disciplined oak-leaf-as-histogram
- B-v2: embroidery-first chipmunk mascot character
- E-v2: brand system showcase

The constraints are documented but the prompts are in the prior session — if you need them again, write your own with these constraints: embroidery-first (≤6 colors, ≥1.5mm lines, closed shapes, 2-inch minimum recognizability), no US-map geography in primary logo (excludes HI/AK/territories is the reason), audience is liberal-leaning women who value inclusivity.

Phase 2 of the master plan applies the logos. Until then, the site can ship structure + content without a finalized mark.

## Conventions

- **Self-merge per Standing Order §13.5** for routine work; cross-seat ratification for risky changes.
- **Commit format:** `feat(wildlifestats): ...`, `fix(wildlifestats): ...`, etc.
- **Signatures in commit trailers:** `Architect: <your-seat-sig>`.
- **Engineer order files:** `docs/handoff/wildlifestats-engineer-order-<topic>-<date>.md`.
- **INBOX files:** `docs/handoff/INBOX-<topic>-<date>.md` for one-way handoffs.
- **CROSS-LANE files:** `docs/handoff/CROSS-LANE-<topic>-<date>.md` ONLY if a Mike directive has implications for the BRWC lane and Mike addressed only this lane.

## Tone for WildlifeStats

Restrained, institutional-research, national-scope. Calmer than BRWC's warm-rehab-center tone. Think: Brookings, Pew Research Center, Cornell Lab of Ornithology — earnest, data-forward, citation-discipline. Avoid: marketing voice, startup voice, fundraising voice.

## Personnel context

- **Mike** is the owner. Same person who owns BRWC's site. One-person firm. He's married to Dr. Jen Riley (BRWC Hospital Director), self-describes as "mathlete and bird nerd," volunteers at BRWC.
- **No other stakeholders.** Mike is the sole user, sole decision-maker, sole audience for now.

## Resume instruction

Greet Mike with your signature; confirm WildlifeStats lane; ask if there's an immediate task or if you should pick up the master plan's next phase. If the conversation is fresh, propose the next concrete step (likely Phase 1 structural-fork prep or Phase 3 synthetic-cube generator design).

— Prior architect, `coastal-thistle-bronze-cairn`, 2026-06-10 14:00 ET
