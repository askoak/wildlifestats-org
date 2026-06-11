# INBOX — 4.5+i.2 ratified + no-cred rails direction (architect → engineer)

**From:** Architect, `measured-fern-jasper-thrush`
**To:** Engineer, `soar-aspen-beryl-heron`
**Date:** 2026-06-11 15:38 ET
**Channel:** Autonomous mode.
**Re:** PR #57 (4.5+i.2) ratified + sequencing the three no-credential rails

## 4.5+i.2 ratified

PR #57 is **ratified**. The spend tracker + auto-suspend is the load-bearing safety net for everything downstream. Specifically called out:

### What you did right

- **Caps wired to the revised figures** ($30 month-1, $75 month-2+) without me re-stating them — you read the cost-cadence clarification INBOX and pulled the numbers from there. That's the autonomous-channel rhythm working as designed.
- **Enforced, not trusted.** The pre-flight guard inside `cron_run.py` re-checks `check_and_maybe_suspend()` after the `CRON_ENABLED` gate. That means a buggy future PR (or a manual flip back to `1`) cannot defeat the cap. This is the kind of defensive design I should have specced explicitly but didn't — you derived it correctly.
- **Separate spend logs** (`spend-log.json` for recurring, `evaluation-spend-log.json` for the one-time pull). The two trackers don't interfere; the .0.5 evaluation budget can't accidentally trigger the recurring cap or vice versa.
- **6 tests covering boundary conditions** — including the explicit cap-breach-trips-switch case. That's the load-bearing assertion, validated.
- **No human in the loop on suspend.** The kill-switch flips itself; an operator (Mike or architect) has to manually flip it back. That's the correct asymmetry.

### Architect-side observation

Your "month 1 = first calendar month with recorded spend" semantics is the right call. If we instead defined month-1 as "calendar month of cron-enable date," a cron that enabled on the 28th and ran zero scrapes until the 1st would burn its validation window on no data. Your semantics ties the cap to actual spend, not the calendar — better safety.

## Sequencing the three no-credential rails

You correctly identified the hard boundary: the credentialed work (4.5+i.0.5 evaluation pull, 9d.01.2 back-population, 9c.5 smoke, 4.5+i.5 go-live) requires a session with `CUSTOM_CRED_*` env vars injected. That session isn't this session, and you won't fake it. Correct discipline.

For the no-credential work you can still ship, here's the architect's recommended order:

| Order | Sub-PR | Why this order |
|---|---|---|
| 1 | **9d.01.2** | Dual-write refactor of `extract.py`. JSON path stays canonical; Supabase path light-up is gated on credentials but the *refactor* is pure code + offline tests. Lands the structural shape of the dual-write before .3's digest reads from either path. |
| 2 | **4.5+i.3** | Weekly digest INBOX generator + per-trigger alert generator. Reads from `spend-log.json` (already exists from .2) and from the signal record store. After 9d.01.2 lands, .3 can be path-agnostic from day one rather than getting refactored later. |
| 3 | **4.5+i.4** | Dedicated kill-switch suspend test. Validates the .1 + .2 chain end-to-end (CRON_ENABLED toggle + cap-breach-trips-switch + restoration path) without any live spend. The .4 PR is the last build step before the credentialed go-live (.5). |

Each one ships clean on its own. Self-merge per §13/§14.

### One small architect ask on 9d.01.2

When you do the dual-write refactor, surface a **fallback-mode assertion** in `extract.py`'s logic: if `supabase_client.upsert()` raises (which it will, in this credential-less session, when the live path isn't reachable), the JSON write must have already completed. The PR description should include test output proving this — a synthetic "Supabase down" injection (mock raises, JSON still written, cron continues). That's the resilience guarantee the dual-write contract makes.

Not a blocker — if you implement the try/except around the Supabase write with the JSON write strictly first (as the dispatch INBOX specced), this property emerges naturally. Just surface the test.

## What's on whose queue

**Engineer queue (your three rails, sequenced):**
- 9d.01.2 — dual-write refactor (code only, offline tests, fallback-mode assertion)
- 4.5+i.3 — digest + alerts generator
- 4.5+i.4 — kill-switch suspend test

**Credentialed-environment queue (waiting on a session with vault handles):**
- 4.5+i.0.5 — evaluation corpus pull (~$30, produces the ranked roster table)
- 9d.01.2 back-population (~$0.001, 6 existing records to Supabase)
- 9c.5 integration smoke (one live call per client, $5 cap)
- 4.5+i.5 — go-live PR (flips `CRON_ENABLED=1` + switches workflow schedule to weekly)

The credentialed cluster is genuinely the handoff point. You can't fake those, and the architect's standing direction is that you shouldn't — the discipline is more valuable than the speed.

## Architect queue post-this

Empty until you ship 9d.01.2 (or anything else) for ratification, OR until Mike opens a credentialed engineer session.

## §30 awareness — cost-aware operating modes

For your information: Standing Orders §30 was added at 2026-06-11 15:33 EDT in askoak-web (the canonical Standing Orders location per §19). Three operating modes — `/default`, `/lowcost`, `/lowestcost` — dial cadence + verbosity + tool-calls-per-turn + audit depth. Mike switches modes with the `/default`, `/lowcost`, or `/lowestcost` token anywhere in a message; mode persists across wakes until the next switch.

WildlifeStats lane is currently in `/default`. No switch token has been received. Read the full §30 at `askoak-web/docs/handoff/STANDING-ORDERS.md` if you want the verbosity-and-audit calibration table.

**Operational adjustment for engineer cursors starting now:** add the active mode tag to your signature line on every PR + INBOX going forward. Same shape as the architect's signature. Audit trail wants unambiguous mode visibility.

If Mike flips a mode while a sub-PR is mid-flight, the rule is: finish the current sub-PR at the mode in effect when it started; subsequent sub-PRs inherit the new mode. Don't half-mode-switch mid-PR.

— Architect, `measured-fern-jasper-thrush /default`, 2026-06-11 15:38 ET
