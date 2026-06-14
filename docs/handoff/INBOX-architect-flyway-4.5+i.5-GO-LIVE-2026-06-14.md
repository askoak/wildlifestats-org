# INBOX — Flyway 4.5+i.5 GO-LIVE (architect → engineer)

**From:** Architect, perplexity-architect (Perplexity Computer)
**To:** Engineer (next session)
**Date:** 2026-06-14 19:55 UTC
**Channel:** Mike-authorized go-live (15:51 EDT: "CRON_ENABLED=1")
**Re:** First-ever production scrape of the Flyway pipeline

## Authorization

Mike authorized the cron flip at 2026-06-14 15:51 EDT. Two sequencing
confirmations from Mike at 15:52 EDT:

- **"Flip now; notifications catch up later"** — proceed without waiting
  for WO-6 (notifications wiring) to land. First ticks run silent; spend
  tracker + kill switch are still active.
- **"Weekly (existing spec)"** — the cadence locked in 2026-06-11's
  cost/cadence INBOX: Sundays 04:00 UTC, Tier 1 every week, Tier 2 only on
  the first Sunday of each month, $30/$75 caps.

## The WO

Full engineer-ready order:

**`work-orders/WO-2026-06-14-wls-flyway-4-5-i-5-go-live.yml`**

Predicate-context-inlined. You do NOT need to clone AIStandingOrders.

## Five gated deliverables (~1h scope)

1. Flip `wildlifestats/_pipeline/flyway/CRON_ENABLED` from `0` to `1`
2. Swap workflow cron from `'0 4 * * *'` to `'0 4 * * 0'`
3. Verify or add Tier 2 first-of-month gate inside cron_run.py
4. Manual smoke-test dispatch immediately after merge
5. Results YAML with smoke-test outcome

## Critical safety rails

- If CRON_ENABLED is already `'1'` on main: HALT+SURFACE
- If spend-log.json has any prior runs: HALT+SURFACE
- If caps in spend_tracker.py are NOT `$30/$75`: HALT+SURFACE
- If smoke-test fails: ROLL BACK CRON_ENABLED to `'0'`, halt, surface
- Kill switch (already tested by test_killswitch_e2e.py) auto-suspends on
  cap breach — you don't add anything new for this; the safety net is
  load-bearing and already validated

— perplexity-architect (Perplexity Computer)
