# Full-day work plan — 2026-06-10

**Author:** Architect, `measured-fern-jasper-thrush`
**Issued:** 2026-06-10 14:40 ET
**Scope:** WildlifeStats lane (askoak/wildlifestats-org).
**Mike directive 14:38 ET:** "agree with all your plan do not hesitate - get the website updated to the best it can be all elements - NO MIKE GATES"
**Mike directive 14:36 ET:** "you can check in every 30 minutes on automode standing order until 6am eastern tomorrow. use as few credits as possible. Engineer was given full autonomous permission"

## Engineer queue (autonomous, no Mike gates)

| # | Order file | Effort | Gate |
|---|---|---|---|
| 1 | `wildlifestats-engineer-order-phase1-structural-framework-2026-06-10.md` | ~half day | On main (commit 0ac19af). Pick up first. |
| 2 | `wildlifestats-engineer-order-phase1.5-ci-guardrails-2026-06-10.md` | ~1 hour | After #1. |
| 3 | `wildlifestats-engineer-order-phase2-rebrand-apply-2026-06-10.md` | ~half day | After #2. Consumes the rename ledger. |
| 4 | `wildlifestats-engineer-order-phase3-cube-2026-06-10.md` | ~half to full day | After #3. Consumes the cube spec. |
| 5 | `wildlifestats-engineer-order-phase4-features-2026-06-10.md` | multi-day, five sub-PRs | After #4. |
| 6 | `wildlifestats-engineer-order-phase6-seo-governance-2026-06-10.md` | ~half day | After #5. |

Phase 5 (secure tier) holds — see `wildlifestats-secure-tier-mechanism-note-phase5-2026-06-10.md`. Dispatches after Phase 4 completes.

## Architect deliverables (already landing today)

| File | Status |
|---|---|
| `wildlifestats-rename-ledger-phase2-2026-06-10.md` | Lands this batch. |
| `wildlifestats-synthetic-cube-spec-phase3-2026-06-10.md` | Lands this batch. |
| `wildlifestats-secure-tier-mechanism-note-phase5-2026-06-10.md` | Lands this batch. |
| `ARCHITECT-POLL-AUTHORIZATION-2026-06-10.md` | Lands this batch. |

## Architect operating mode for the rest of the window

Per the poll authorization:

- 30-minute cadence, until 2026-06-11 06:00 ET.
- On each wake: `git fetch && git log` against last checkpoint. If no engineer commits since last wake → no-op exit, cheapest possible turn. If new merges → read the diff, ratify with one-line PR comment if the work is exemplary or needs a flag.
- No new orders unless engineer raises an INBOX file requesting one.
- No status reports to Mike. Mike checks in when Mike checks in.
- Exit early if engineer reports Phase 6 complete (full pipeline done).

## Definition of "the website updated to the best it can be"

For tonight's purposes, Mike's directive resolves to: ship the full master plan, Phases 1 → 4 → 6, end-to-end, with Phase 5 as a follow-on. After Phase 6 the public site has:

- Restrained national-research IA with all section pages live.
- Final palette, typography, logo slot (real logo drops in when Mike's prompts land).
- Synthetic n=100,000 cube live at /data/ with filter UI, choropleth, CSV downloads.
- One Health, Parks, Wildlife, Ingest sections built out.
- SEO live — robots, sitemap, OG tags, schema.org Dataset.
- Methodology and Governance pages in long form.

That is the "best it can be" within today's authorization. Anything beyond — partner pilot integrations, real-time data, multi-language, etc. — is a future phase that requires a fresh authorization.

— Architect, `measured-fern-jasper-thrush`, 2026-06-10 14:40 ET
