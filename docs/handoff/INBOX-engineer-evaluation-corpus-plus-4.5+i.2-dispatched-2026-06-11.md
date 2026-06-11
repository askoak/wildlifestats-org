# INBOX — Evaluation corpus pull + 4.5+i.2 dispatched (architect → engineer)

**From:** Architect, `measured-fern-jasper-thrush`
**To:** Engineer, `soar-aspen-beryl-heron`
**Date:** 2026-06-11 15:20 ET
**Channel:** Autonomous mode.
**Re:** Mike-authorized evidence-driven roster sizing + concurrent 4.5+i.2 spend tracker work

## What Mike asked

Two related questions surfaced this turn:

1. "Should we expand beyond 100 [centers] or reduce down to 50? 50 centers would have at most 50 posts per day per channel or find as many as possible and do quarterly runs for non-major centers and major-centers followed weekly is probably fine."
2. Should we evaluate what we actually pulled into the corpus from the master run and decide which centers provide valuable content?

The right answer is **yes evaluate, before locking in any cadence**. Roster size and tier-split should be evidence-driven, not roster-of-convenience-driven. Mike authorized a one-time evaluation corpus pull and dispatched both that and 4.5+i.2 in parallel (they don't conflict).

## NEW SUB-PR — 4.5+i.0.5 — Evaluation corpus pull

### Scope

One-time corpus pull to characterize every center in the 99-row social-seed roster, so the actual cadence + roster decision is evidence-driven.

**Pull parameters:**
- **Targets:** all 99 centers in the social-seed CSV, all platforms each has verified handles for
- **Window:** trailing 90 days from run time
- **Extraction:** full LLM extraction on every post (no dedup yet — we want to characterize raw content, not steady-state)
- **Storage:** signals committed to `secure/cube/flyway/signals/evaluation-2026-W24-*.json` (one file per center for traceability)
- **Raw post text:** discarded as always per §19 audit-log contract

**Spend cap:** **$50 hard cap.** Estimated actual ~$25-30 (per the math walked through with Mike). Auto-abort the pull before issuing the next call if cumulative spend would exceed $50.

This is a **one-time spend**, distinct from the recurring 4.5+i cron. Surface in the PR description that this is a one-shot evaluation expense, not a steady-state authorization.

### Output artifact (the actual deliverable)

A ranked-table report at `secure/cube/flyway/evaluation/corpus-evaluation-2026-W24.md` with one row per center, columns:

| Column | What it measures |
|---|---|
| `slug` | center slug from the social-seed CSV |
| `state` | center state |
| `tier` | current Priority Tier (A/B/C from social-seed) |
| `posts_per_week` | mean across last 90 days, all platforms summed |
| `signals_extracted_per_week` | mean LLM-extracted signal records per week |
| `unique_signal_types` | distinct phenology / baby-season / volume / etc. signals fired |
| `geographic_uniqueness_rank` | "Xth of N in state" |
| `species_coverage_breadth` | count of distinct species mentioned in extracted signals |
| `est_value_score` | composite ranking (your choice of formula; document it in the PR) |

Plus three summary statistics:
- Distribution shape: long-tail vs broad-distribution vs bimodal
- Top-30 vs bottom-69 signal density ratio
- Geographic coverage if we cut to top-30/50/70

### What Mike will do with the output

Mike (and architect) will draw cutoff lines based on the ranked table. The decision space is:

| Pattern observed | Likely cadence outcome |
|---|---|
| Long tail concentrated in top ~30 | Reduce to 30-50 high-value weekly; drop the rest |
| Broad distribution, ~80 active producers | Keep ~100 weekly with marginal-case demotions |
| Heavy skew + meaningful long-tail uniqueness | Two-tier: 30 majors weekly + 60-80 minors quarterly (Mike's preferred shape) |

The evaluation pull doesn't pre-commit to any of these — it surfaces the evidence to make the call.

### Discipline reminders

- **Re-grounded cost ceiling** for this one-time pull: 99 centers × ~4 platforms avg × 1 actor-run per center-platform × $0.05/run + ~1500 posts × $0.007 LLM = ~$30. The $50 cap is comfortable margin.
- **Use the existing `_common/apify_client.py` + `_common/claude_client.py`** paths. Don't fork a new code path for this; if 4.5+i.0.5 uses different clients than 4.5+i.x will, we lose the discipline calibration.
- **Audit log per the §19 contract:** `post_text_NOT_STORED: true` on every record. Same as the smoke and the cron.
- **No Supabase writes from this PR** — the signals go to JSON files only. Once 9d.01.2 dual-write lands, future runs (including 4.5+i.5 go-live) will dual-write, but this evaluation pull predates that and stays JSON-only.

## CONCURRENT SUB-PR — 4.5+i.2 — Spend tracker + auto-suspend

Per the cost-cadence clarification INBOX (just merged at `e6c6011`), the revised caps are:

- **Month 1: $30 hard cap** (validation window)
- **Month 2+: $75/month steady-state cap** (down from $100; ~25% headroom over Scenario D)

### 4.5+i.2 scope

A spend tracker that:

1. **Reads from `spend-log.json`** — a committed artifact at `wildlifestats/_pipeline/flyway/spend-log.json` updated by the cron itself after each run. Schema: one entry per run with `{timestamp, tier, actor_runs, apify_cost_usd, llm_cost_usd, total_usd}`.

2. **Auto-suspend on cap hit:**
   - If current-calendar-month cumulative spend ≥ $30 AND it's still month 1: suspend.
   - If current-calendar-month cumulative spend ≥ $75 AND it's month 2+: suspend.
   - Suspend = write `CRON_ENABLED=0` (the kill switch from 4.5+i.1). Next scheduled tick no-ops.

3. **Calibration loop:** at the end of every run, append the spend record and recompute the rolling 7-day spend rate. Surface in the weekly digest (4.5+i.3).

4. **Independence from the evaluation pull:** the $50 evaluation budget is one-time and goes against a separate `evaluation-spend-log.json` artifact. The recurring cron's tracker reads only `spend-log.json`. They don't interfere.

### 4.5+i.2 unblocks on .0.5

Engineer's call on sequencing. If you want to land .0.5 first to validate the cost calibration against real numbers, that's the architect's preference. If you prefer .2 first to have the kill-switch tracker in place before any live spend at all (even the .0.5 evaluation pull), that's also defensible — the .0.5 pull would then be the first run against which .2's tracker calibrates.

Architect's actual recommendation: **.2 first, then .0.5.** The .2 tracker is the safety net; firing the .0.5 pull through that tracker means we get both the evidence AND a real-world calibration of the auto-suspend math in one shot.

## Architectural note (do not action; just visible)

Mike also flagged a fourth direction worth surfacing for later: **expand the registry to find more rural/single-source centers** rather than scaling the existing 99 evenly. The 181-org `centers.yaml` includes ~80 orgs *without* social handles in the social-seed CSV — many of which may be the only rehab center in their county or species. Those orgs may have higher *per-post value* even if they post less often.

This is a **future hygiene pass**, not Phase 9 work. Out of scope for this dispatch. Architect logs it for the Phase 10 backlog: "Agent F — social handle discovery for the 80 centers in centers.yaml currently outside the social-seed CSV."

## Architect queue post-this

Empty until you ship .0.5, .2, or 9d.01.2 for ratification.

— Architect, `measured-fern-jasper-thrush`, 2026-06-11 15:20 ET
