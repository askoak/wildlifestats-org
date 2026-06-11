#!/usr/bin/env python3
"""Flyway 4.5+i.2 — recurring-cron spend tracker + auto-suspend.

The safety net that must exist before any recurring spend. After each cron run
the orchestrator appends a spend record here; this module recomputes month-to-
date spend and, if it has hit the authorized cap, trips the kill-switch
(`CRON_ENABLED` -> "0") so the next scheduled tick no-ops. No human in the loop.

CAPS (architect cost-cadence revision 2026-06-11, after the engineer cost flag):
  - Month 1 (validation window):      $30 hard cap
  - Month 2+ (steady-state):          $75/month   (down from the naive $100)
Auto-suspend on hitting either. "Month 1" = the first calendar month in which
the cron records any spend; subsequent calendar months use the steady cap.

The recurring cron reads ONLY `spend-log.json`. The one-time evaluation pull
(4.5+i.0.5) tracks against a separate `evaluation-spend-log.json` so the two
budgets never interfere.

Run (typically by the cron after a run, or standalone to check state):
    python -m wildlifestats._pipeline.flyway.spend_tracker --check
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
SPEND_LOG = os.path.join(HERE, "spend-log.json")
CRON_ENABLED_FILE = os.path.join(HERE, "CRON_ENABLED")

MONTH1_CAP_USD = 30.0
STEADY_CAP_USD = 75.0


def _now_month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def load_log(path: str = SPEND_LOG) -> list[dict]:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("runs", []) if isinstance(data, dict) else data
    except (OSError, ValueError):
        return []


def record_run(entry: dict, path: str = SPEND_LOG) -> dict:
    """Append one run's spend. Fills total_usd from apify+llm if absent."""
    entry = dict(entry)
    if "total_usd" not in entry:
        entry["total_usd"] = round(
            float(entry.get("apify_cost_usd", 0.0)) + float(entry.get("llm_cost_usd", 0.0)), 6)
    runs = load_log(path)
    runs.append(entry)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"runs": runs}, f, ensure_ascii=False, indent=2)
    return entry


def _ym(entry: dict) -> str:
    return str(entry.get("timestamp", ""))[:7]


def first_active_month(runs: list[dict]) -> str | None:
    months = sorted({_ym(e) for e in runs if _ym(e)})
    return months[0] if months else None


def month_to_date(runs: list[dict], month: str) -> float:
    return round(sum(float(e.get("total_usd", 0.0)) for e in runs if _ym(e) == month), 6)


def cap_for(runs: list[dict], month: str) -> float:
    """$30 for the first active calendar month (validation window), $75 after."""
    first = first_active_month(runs)
    return MONTH1_CAP_USD if (first is None or month == first) else STEADY_CAP_USD


def _suspend(cron_enabled_path: str) -> None:
    with open(cron_enabled_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("0\n")


def check_and_maybe_suspend(
    *, log_path: str = SPEND_LOG, cron_enabled_path: str = CRON_ENABLED_FILE,
    month: str | None = None,
) -> dict:
    """Compute month-to-date spend; trip the kill-switch if it has hit the cap.
    Returns a status dict (suspended, mtd, cap, month, reason)."""
    month = month or _now_month()
    runs = load_log(log_path)
    mtd = month_to_date(runs, month)
    cap = cap_for(runs, month)
    if mtd >= cap:
        _suspend(cron_enabled_path)
        return {"suspended": True, "mtd_usd": mtd, "cap_usd": cap, "month": month,
                "reason": f"month-to-date ${mtd} >= ${cap} cap — CRON_ENABLED set to 0"}
    return {"suspended": False, "mtd_usd": mtd, "cap_usd": cap, "month": month,
            "reason": f"${mtd} / ${cap} this month — within cap"}


def main() -> int:
    ap = argparse.ArgumentParser(description="Flyway spend tracker + auto-suspend")
    ap.add_argument("--check", action="store_true",
                    help="recompute month-to-date spend and suspend if over cap")
    ap.add_argument("--month", default=None, help="override the YYYY-MM month (testing)")
    args = ap.parse_args()
    status = check_and_maybe_suspend(month=args.month)
    print(json.dumps(status))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
