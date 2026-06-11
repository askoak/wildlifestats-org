# INBOX — Overnight autonomous authorization (architect → engineer)

**From:** `measured-fern-jasper-thrush /lowcost`
**To:** `soar-aspen-beryl-heron`
**Date:** 2026-06-11 15:50 ET
**Mode:** WildlifeStats lane switched `/default → /lowcost` at 15:47 ET (Mike token in message). Persists 12 hours. Self-ratify routine sub-PRs; surface only blockers + finished-rail summaries.

## Mike pre-authorizations (12-hour window, until ~03:50 ET 2026-06-12)

Mike's verbatim: *"approve up to $100"*, *"yes you are pre-authorized keep everything moving"*, *"use as many agents for that task as will get the corpus infrastructure built by morning"*, *"move it all forward your recommendation = Mike said yes unless you're absolutely blocked"*.

Translation into operational authority:

1. **Live spend ceiling: $100 total** across all rails for the 12-hour window. Includes 4.5+i.0.5 evaluation pull ($50), 9c.5 smoke ($5), 9d.01.2 back-pop (~$0.001), Agent F if dispatched (~$15-30 research, see below). Track cumulative in a `secure/cube/flyway/overnight-spend-2026-06-11.json` artifact. **Auto-halt at $100.** The 4.5+i.2 spend tracker is for the recurring cron only; this is a separate overnight envelope.

2. **Pre-authorized to ship the full credentialed cluster:** 4.5+i.0.5 evaluation pull, 9c.5 smoke, 9d.01.2 back-population, **and 4.5+i.5 go-live** if .0.5 evidence supports it (see Mike pre-auth on cadence below).

3. **Credentials live in OneDrive + Perplexity vault.** Vault handles per the 2026-06-11 09:30 INBOX (`custom-cred:api.apify.com`, `custom-cred:api.anthropic.com`, `custom-cred:oamqicylpytbldrnybcc.supabase.co`). Use vault, not OneDrive direct. Token-by-reference discipline holds.

4. **Cadence/roster decision pre-delegated to architect.** Mike's stated preference: majors weekly + non-majors quarterly. Architect draws cutoff from .0.5 evidence per the framing:
   - **Pattern 1 (long-tail concentrated in top ~30):** weekly cutoff at top 30, drop bottom 69. Trigger Agent F dispatch (see #5).
   - **Pattern 2 (broad distribution ~80 active):** weekly cutoff at ~80, demote 10-20 marginal. No Agent F.
   - **Pattern 3 (heavy skew + meaningful long-tail uniqueness):** ~30 weekly + 60-80 quarterly. Conditional Agent F.

5. **Agent F (social-handle discovery for the 80 centers in centers.yaml without handles) PRE-AUTHORIZED to dispatch automatically if .0.5 distribution is Pattern 1 or Pattern 3.** Architect dispatches up to 5 parallel research agents to find verified social handles for the long-tail 80 centers. Output: augmented social-seed CSV. Budget: $15-30 research credits. Stays within the $100 overnight ceiling.

6. **Cross-lane Apify spend visibility: ignored per Mike directive.** No cross-lane handshake on shared billing.

## Sequencing (architect direction, engineer's call on order within)

### Rail A — credential cluster (live spend, $100 ceiling)

1. **4.5+i.0.5 — evaluation corpus pull** ($50 cap, ~$25-30 expected). Ship the ranked-table report at `secure/cube/flyway/evaluation/corpus-evaluation-2026-W24.md`.
2. **9c.5 — integration smoke** ($5 cap). One live call per `_common` client (fetch, exa, claude, apify). Skip the Supabase live in this batch — 9d.01.2 back-pop covers that.
3. **9d.01.2 back-population** (~$0.001). 6 existing records → bucket_01 via dual-write. Include the §19 fallback-mode assertion test (mock-Supabase-raises proves JSON write completed).

### Rail B — no-credential code (self-ratify per `/lowcost`)

1. **9d.01.2 dual-write refactor** (code + offline tests; back-pop is Rail A.3)
2. **4.5+i.3 — weekly digest + per-trigger alerts**
3. **4.5+i.4 — dedicated kill-switch suspend test**

### Rail C — conditional on .0.5 evidence

- **Architect decision: cutoff line.** Drawn from the ranked table. Pattern-matched per the framing above. Documented in a CHECKIN-RESULTS note.
- **Agent F dispatch** (architect-side, parallel research agents) — if Pattern 1 or Pattern 3.
- **4.5+i.5 go-live** — flips `CRON_ENABLED=1` AND switches workflow schedule to weekly. Architect ratifies; engineer ships.

## Self-ratification under `/lowcost`

For routine sub-PRs (9d.01.2, 4.5+i.3, 4.5+i.4, 9c.5, .0.5):
- Engineer self-ratifies per §13/§14
- Architect spot-checks the next morning, not per-PR
- Sign-off block compressed (Mike-line + seat + mode tag)

Architect retains per-PR audit for:
- **4.5+i.5 go-live** (CRON_ENABLED flip — load-bearing, not routine)
- **Any §19 evidence** (CHECK constraint live verification)
- **Cadence-cutoff decision** (architect draws, then surfaces to Mike on his return)

## Spend tracking discipline

Append to `secure/cube/flyway/overnight-spend-2026-06-11.json` after every billable call. Schema:

```json
{
  "timestamp": "ISO 8601 UTC",
  "rail": "0.5 | 9c.5 | 9d.01.2 | agent_f | other",
  "actor_runs": int,
  "apify_cost_usd": float,
  "llm_cost_usd": float,
  "total_usd": float,
  "cumulative_usd": float
}
```

**Pre-flight check before every billable call:** read the cumulative_usd. If >= $100, abort.

## Morning handoff format

When Mike returns (~03:50 ET earliest, more likely ~08:00+), the first artifact he should see in his queue:

`docs/handoff/MORNING-CHECKIN-2026-06-12.md` — written by the last engineer or architect cursor of the overnight window. Should contain:

1. **What shipped** (list of merged PRs with one-line each)
2. **Total overnight spend** (against the $100 ceiling)
3. **.0.5 ranked-table summary** (the distribution shape verdict)
4. **Architect cadence/roster decision** (which cutoff was drawn and why)
5. **Agent F outcome** (if dispatched: count of handles found, augmented CSV path)
6. **4.5+i.5 go-live status** (shipped + cron enabled, or blocked)
7. **Anything genuinely blocked** that needs Mike on his return

Format: tight, scannable, decision-relevant. No filler.

## What to escalate to Mike via session-end §16 popup

**ONLY** if you hit one of these:

- A credential refuses to inject (vault problem, not engineer problem)
- A live API errors in a way that suggests data integrity risk
- A §19 server-side gate appears to NOT fire on a test (catastrophic)
- The $100 ceiling hits before .0.5 completes (likely a roster size miscalibration)
- A cross-lane signal that materially affects WildlifeStats

Everything else: ship, self-ratify, write the morning checkin, stand by.

## Architect (me) overnight behavior

Per `/lowcost`: I won't wake on every engineer PR. I'll surface only when:
- The `/lowestcost`-style ratification check is needed (4.5+i.5 go-live)
- The cadence-cutoff decision needs architect attention (after .0.5)
- Agent F dispatch (architect-driven)
- Engineer escalates per the criteria above

Engineer carries the autonomy weight per `/lowcost`'s "engineers absorb more autonomy."

— Architect, `measured-fern-jasper-thrush /lowcost`, 2026-06-11 15:50 ET
