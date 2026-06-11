# INBOX — Flyway POC post-mortem (engineer → Mike + architect)

**From:** Engineer, `soar-aspen-beryl-heron`
**Date:** 2026-06-11
**Re:** Input for the Phase 4.5+i recurring-spend decision (per the smoke-test authorization).

## (a) Actual cost
~**$0.30** Apify (31 FB + 16 IG posts via official actors; FB ~$0.22, IG ~$0.05, one wasted sync-timeout start). LLM $0 actual (session model stood in for Haiku; production est. < $0.01 for 47 posts). Well under the $5-10 authorization.

## (b) Extraction quality
- **Offline vocabulary matcher: 0/47.** Real wildlife-rehab posts do not use the narrow seed phrases. The vocabulary lists are a *prior*, not a matcher — real recall needs the LLM. (Keep offline as the deterministic CI backend only.)
- **LLM extraction: 6 solid records,** all `phenology.baby_season_start.songbird`, geographically attributed (NY: Wild Bird Fund — incl. a quantitative "patient #5,000, +12% YoY" volume signal, a kestrel nestling in Brooklyn, a fledgling in Prospect Park; TN: Walden's Puddle). **Correct negatives** on advice posts and single-injury cases — the extractor discriminates events from content.
- **0 hummingbird-arrival** — correct: June is past the Feb-May arrival window. Catching arrival requires scraping the spring window.

## (c) Methodological surprises
1. **Season drives which signal fires.** A June scrape surfaces baby-season, not arrival. The cron must run year-round; signal value rotates with the calendar.
2. **The quantitative volume signals are the sleeper value** — "+12% YoY at patient #5,000" is genuine early intelligence a baseline can trigger on, beyond presence/absence.
3. **Production LLM extractor** should pull `ANTHROPIC_API_KEY` via `custom-cred:api.anthropic.com` injection (env-shadowed in the Claude Code shell). Same pattern as Apify. To codify in `wildlifestats/_pipeline/_common/creds.py` at Phase 9.

## Recommendation
The chain works end to end. Recommend proceeding to **4.5+h (baseline + triggers)** and **4.5+i (cron, shipped DISABLED)**. The **recurring ~$50-100/mo daily spend remains Mike's call** — the POC suggests the value is real (geo-attributed, season-correct, quantitative volume signals), but the recurring authorization should come after 4.5+h proves a trigger fires on real data.

— Engineer `soar-aspen-beryl-heron`, 2026-06-11
