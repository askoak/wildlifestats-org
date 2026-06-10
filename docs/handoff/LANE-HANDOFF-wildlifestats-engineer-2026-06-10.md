# Lane handoff — WildlifeStats Engineer

**Date:** 2026-06-10 ~14:00 ET
**For:** the new WildlifeStats Engineer session spawning now

## Scope

Engineer for **WildlifeStats.org**. Single primary repo: **askoak/wildlifestats-org**.

You partner with the WildlifeStats Architect session. You do NOT touch BRWC's askoak/askoak-web repo's `brwc/` or `brwc-public` URL path. See Standing Orders §19–20 (in askoak-web) for lane boundaries.

## First moves on session start

1. **Generate your seat signature.** Suggested format: `<verb>-<plant>-<gem>-<bird>` to distinguish from BRWC engineer's `<adjective>-<plant>-<metal>-<artifact>`. Example: `glide-fern-quartz-finch`. Lock it.
2. **Clone the repo:** `git clone https://github.com/askoak/wildlifestats-org.git /tmp/wildlifestats-org`.
3. **Read the Standing Orders** at `https://raw.githubusercontent.com/askoak/askoak-web/main/docs/handoff/STANDING-ORDERS.md`. You inherit all twenty rules. §13.5 self-merge authority and §17 "light the ceremony" govern how you work day to day.
4. **Read the master plan:** `https://raw.githubusercontent.com/askoak/askoak-web/main/docs/handoff/wildlifestats-master-plan-2026-06-10.md`.
5. **Verify GitHub auth:** `gh repo view askoak/wildlifestats-org` should return the repo info.
6. **Greet Mike** with your signature; confirm WildlifeStats engineer lane.

## What exists in the repo

Tiny. Just the placeholder and the handoff docs. Phase 1 of the master plan is the first real engineering work — wait for the WildlifeStats Architect to dispatch the Phase 1 engineer order.

## What WildlifeStats will need from you

In rough order of work effort (each is its own engineer order from the architect):

1. **Phase 1 — Structural framework.** Build the directory structure, the placeholder pages for each major section (landing, dashboard, One Health, parks lens, encyclopedia, search, governance, methodology, secure tier). Pure HTML/CSS scaffold. Architect ships the IA spec; you implement.

2. **Phase 2 — Apply branding** once logos land. Color palette tokens, logo SVG integration, typography. ~1 day.

3. **Phase 3 — Wire the synthetic n=100,000 cube** into the dashboard + map. Architect generates the cube JSON; you build the studio interface (filtering, charts, downloads with k-suppression).

4. **Phase 4 — National features.** Each as a separate engineer order:
   - One Health hub
   - National Parks lens
   - Wildlife encyclopedia
   - Searchable national database
   - Multi-format ingestion sandbox (methodology demo with sample Excel files)

5. **Phase 5 — Authenticated tier `/secure/`.** Netlify basic-auth on the `/secure/*` path. Content is an INTERNAL REWRITE/REDIRECT to BRWC's staff site (architect will spec exact mechanism).

6. **Phase 6 — SEO + governance polish.** robots.txt / sitemap.xml / Open Graph / schema.org Dataset markup / governance page.

## Conventions

- **Self-merge per Standing Order §13.5** for routine work.
- **Commit format:** `feat(wildlifestats): ...`, `fix(wildlifestats): ...`, `data(wildlifestats): ...`, etc.
- **Signatures in commit trailers:** `Engineer: <your-seat-sig>`.
- **No build pipeline** for the WildlifeStats site initially — it's pure HTML/CSS/JS deployed straight from the repo by Netlify. Keep it static; resist over-engineering until the architect specs a build step.
- **Credentials** — read from Mike's OneDrive Credentials folder by absolute path. Never paste secrets in chat. See §18 + the askoak-web `CREDENTIALS-POINTER.md`.

## What is NOT yours

- **BRWC at all.** Real BRWC site, real BRWC content, real BRWC data, real BRWC organization name. ZERO appearance on WildlifeStats public tier.
- **askoak.michaeloak.com or any path under it.** Different repo, different lane.
- **The AskOak compensation product.** Unrelated.
- **The clinical interpretation of any data.** WildlifeStats is methodology + display; clinical questions defer to subject-matter experts who'll never be in the loop here.

## Tone for WildlifeStats

National-research institutional voice. Earnest, data-forward, citation-discipline. Calmer and more neutral than BRWC's warm-rehab-center tone.

## Personnel context

- **Mike** is the owner. Same Mike as BRWC. Single user.
- Self-describes as mathlete + bird nerd. Wife is BRWC's Hospital Director. He volunteers at BRWC.
- WildlifeStats is HIS new project, separate from his consulting firm (MOA) and separate from BRWC.

## Resume instruction

Greet Mike with your signature; confirm WildlifeStats engineer lane; tell him your queue (likely empty at session start) and that you're standing by for the WildlifeStats Architect's first engineer order.

If there's an open Mike directive in the active conversation, respond to it. Don't preempt the architect by self-assigning work.

— Prior architect's brief, on behalf of the WildlifeStats engineer about to spawn, 2026-06-10 14:00 ET
