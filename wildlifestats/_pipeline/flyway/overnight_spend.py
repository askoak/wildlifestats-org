#!/usr/bin/env python3
"""Overnight autonomous-window spend envelope (2026-06-11, Mike $100 pre-auth).

Separate from the recurring-cron spend_tracker.py: this bounds the ONE-TIME
overnight authorization (4.5+i.0.5 eval pull, 9c.5 smoke, 9d.01.2 back-pop,
Agent F) at a $100 hard ceiling. Every billable call appends here and runs a
pre-flight check; at $100 cumulative, callers must abort.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OVERNIGHT_LOG = os.path.join(REPO, "secure", "cube", "flyway", "overnight-spend-2026-06-11.json")
CEILING_USD = 100.0


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load(path: str = OVERNIGHT_LOG) -> list[dict]:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("calls", []) if isinstance(data, dict) else data
    except (OSError, ValueError):
        return []


def cumulative(path: str = OVERNIGHT_LOG) -> float:
    return round(sum(float(c.get("total_usd", 0.0)) for c in load(path)), 6)


def preflight(est_usd: float, path: str = OVERNIGHT_LOG) -> dict:
    """Call BEFORE issuing a billable call. ok=False means abort."""
    cum = cumulative(path)
    ok = (cum + est_usd) <= CEILING_USD
    return {"ok": ok, "cumulative_usd": cum, "est_usd": est_usd, "ceiling_usd": CEILING_USD,
            "reason": "" if ok else f"would exceed ${CEILING_USD} (${cum}+${est_usd})"}


def record(*, rail: str, apify_cost_usd: float = 0.0, llm_cost_usd: float = 0.0,
           actor_runs: int = 0, path: str = OVERNIGHT_LOG) -> dict:
    total = round(float(apify_cost_usd) + float(llm_cost_usd), 6)
    calls = load(path)
    cum = round(sum(float(c.get("total_usd", 0.0)) for c in calls) + total, 6)
    entry = {"timestamp": _now(), "rail": rail, "actor_runs": actor_runs,
             "apify_cost_usd": round(float(apify_cost_usd), 6),
             "llm_cost_usd": round(float(llm_cost_usd), 6),
             "total_usd": total, "cumulative_usd": cum}
    calls.append(entry)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"ceiling_usd": CEILING_USD, "calls": calls}, f, ensure_ascii=False, indent=2)
    return entry


if __name__ == "__main__":
    print(json.dumps({"cumulative_usd": cumulative(), "ceiling_usd": CEILING_USD}))
