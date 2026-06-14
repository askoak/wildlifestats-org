# INBOX — Flyway 4.5+i.3 notifications → cron_run.py wiring (architect → engineer)

**From:** Architect, perplexity-architect (Perplexity Computer)
**To:** Engineer (next session — Codex or Claude Code)
**Date:** 2026-06-14 19:30 UTC
**Channel:** Autonomous mode (Mike's standing overnight authorization).
**Re:** Wire the 4.5+i.3 notifications module (PR #64, merged today) into cron_run.py

## Where to find the WO

The full engineer-ready work order is at:

**`work-orders/WO-2026-06-14-wls-flyway-notifications-cron-wiring.yml`**

The WO is predicate-context-inlined — it includes the full background on
PR #64 + the engineer's note that wiring was intentionally deferred + the
kill-switch interaction requirements. You do NOT need to read any other repo.

## Quick orientation

- PR #64 shipped the notifications module standalone (read local artifacts,
  emit weekly digest INBOX + per-trigger alert INBOXes).
- The engineer who shipped #64 explicitly held the cron_run.py wiring as a
  separate step: "Mike asked for pure code, no credentials, and no API
  calls; live cron execution remains separately gated."
- This WO does that wiring **without** flipping CRON_ENABLED.
- Tier 2, $0 budget, ~4h scope, PR for architect audit.

## Critical guardrails

- CRON_ENABLED must remain `"0"` on main after this PR merges.
- No live API calls, no credentials needed.
- notifications.py is read-only for this WO (don't edit it; only call it).
- _eval_live.py is architect-only (do not touch).
- Halt+surface on any guardrail breach.

— perplexity-architect (Perplexity Computer)
