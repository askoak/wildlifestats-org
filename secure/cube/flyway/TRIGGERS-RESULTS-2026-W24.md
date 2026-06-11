# Flyway 4.5+h — baseline + trigger results (2026-W24)

Analytical pass over the existing 6-record smoke corpus
(`signals/smoke-2026-W24-llm.json`). **No new social spend.** The daily cron
(4.5+i) stays disabled.

## Thresholds (architect prior, surfaced for audit)

| Trigger | Rule |
|---|---|
| `volume_spike` | current-week count > rolling baseline mean + **2σ**, baseline = up to 8 prior weeks; requires ≥ **4** prior weeks of history |
| `presence` | ≥ **3** distinct centers reporting the same signal within a **7-day** window |
| `early` / `late` | phenology arrival vs a multi-year baseline (signal def `baseline_period_years`) |

## Outcome — 0 of 3 triggers fired (honest single-season result)

| Signal | Trigger | Scope | Fired | Why not |
|---|---|---|---|---|
| `baby_season_start.songbird` | volume_spike | state=NY | no | insufficient_baseline_history (1 prior week, need ≥4) |
| `baby_season_start.songbird` | volume_spike | state=TN | no | insufficient_baseline_history (0 prior weeks) |
| `baby_season_start.songbird` | presence | national | no | below_threshold (max 1 distinct center in any 7-day window, need ≥3) |

Artifact: [`triggers/triggers-2026-W24.json`](triggers/triggers-2026-W24.json) — every evaluation carries provenance (record_ids, centers, weeks, baseline, threshold).

## Reading the result

**The engine works** — unit tests (`flyway/test_triggers.py`, 6/6) prove `volume_spike` fires on a synthetic ≥4-week history exceeding mean+2σ, and `presence` fires on ≥3 distinct centers within 7 days, with the bounded-window and insufficient-history negatives also covered.

**Nothing fires on the real corpus because the corpus is a single one-week snapshot from 2 centers.** You cannot compute a rolling baseline from one week, and 2 centers can't clear a ≥3-center presence bar. This is the honest, decision-relevant finding:

> Triggering requires a baseline; a baseline requires recurring collection over multiple weeks across the roster. The single smoke run cannot fire a trigger no matter how the signal looks.

That is precisely the input the **4.5+i recurring-spend decision** (≈$50–100/mo, on Mike's queue) needs: the analytical layer is built and proven, and the only thing standing between it and live early-warning triggers is multi-week collection. The Wild Bird Fund "patient #5,000, +12% YoY" record is exactly the kind of volume observation that *would* fire once a baseline exists.

## Next

- 4.5+i (recurring cron) — Mike's call; this result is the input.
- When recurring collection lands, re-run `python -m wildlifestats._pipeline.flyway.triggers --signals <weekly> --out triggers/triggers-<week>.json` per cube run.
