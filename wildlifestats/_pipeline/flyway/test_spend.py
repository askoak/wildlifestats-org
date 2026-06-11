"""Tests for the Flyway 4.5+i.2 spend tracker + auto-suspend.

Deterministic, no network, no spend. Proves the month-to-date math, the
$30/$75 cap boundary, and that hitting the cap trips the CRON_ENABLED
kill-switch.

Run from repo root:
    python wildlifestats/_pipeline/flyway/test_spend.py
"""
from __future__ import annotations

import os
import sys
import tempfile
import traceback

from wildlifestats._pipeline.flyway import spend_tracker as st

PASSED = 0
FAILED = 0


def case(name):
    def deco(fn):
        global PASSED, FAILED
        try:
            fn()
            PASSED += 1
            print(f"  PASS  {name}")
        except AssertionError as e:
            FAILED += 1
            print(f"  FAIL  {name}: {e}")
        except Exception as e:  # noqa: BLE001
            FAILED += 1
            print(f"  ERROR {name}: {type(e).__name__}: {e}")
            traceback.print_exc()
        return fn
    return deco


def _tmp(name):
    return os.path.join(tempfile.mkdtemp(), name)


def _run(ts, apify=0.0, llm=0.0):
    return {"timestamp": ts, "tier": 1, "actor_runs": 1,
            "apify_cost_usd": apify, "llm_cost_usd": llm}


print("=" * 60)
print("Flyway 4.5+i.2 spend tracker")
print("=" * 60)


@case("record_run derives total_usd and round-trips")
def _():
    p = _tmp("spend-log.json")
    st.record_run(_run("2026-06-15T04:00:00Z", apify=1.5, llm=0.5), path=p)
    runs = st.load_log(p)
    assert len(runs) == 1 and abs(runs[0]["total_usd"] - 2.0) < 1e-9


@case("month_to_date sums only the target calendar month")
def _():
    runs = [_run("2026-06-10T00:00:00Z", apify=10), _run("2026-06-20T00:00:00Z", apify=5),
            _run("2026-07-01T00:00:00Z", apify=99)]
    for r in runs:
        r["total_usd"] = r["apify_cost_usd"]
    assert st.month_to_date(runs, "2026-06") == 15
    assert st.month_to_date(runs, "2026-07") == 99


@case("cap is $30 in the first active month, $75 thereafter")
def _():
    runs = [dict(_run("2026-06-15T00:00:00Z"), total_usd=1.0)]
    assert st.cap_for(runs, "2026-06") == st.MONTH1_CAP_USD == 30.0
    assert st.cap_for(runs, "2026-07") == st.STEADY_CAP_USD == 75.0


@case("under cap -> not suspended, CRON_ENABLED untouched")
def _():
    log = _tmp("spend-log.json")
    cron = _tmp("CRON_ENABLED")
    with open(cron, "w") as f:
        f.write("1\n")
    st.record_run(_run("2026-06-15T04:00:00Z", apify=12.0), path=log)
    status = st.check_and_maybe_suspend(log_path=log, cron_enabled_path=cron, month="2026-06")
    assert status["suspended"] is False and status["cap_usd"] == 30.0
    assert open(cron).read().strip() == "1", "must not touch the switch when under cap"


@case("hitting the $30 month-1 cap trips the kill-switch")
def _():
    log = _tmp("spend-log.json")
    cron = _tmp("CRON_ENABLED")
    with open(cron, "w") as f:
        f.write("1\n")
    st.record_run(_run("2026-06-15T04:00:00Z", apify=20.0), path=log)
    st.record_run(_run("2026-06-16T04:00:00Z", apify=11.0), path=log)  # cum $31 >= $30
    status = st.check_and_maybe_suspend(log_path=log, cron_enabled_path=cron, month="2026-06")
    assert status["suspended"] is True and status["mtd_usd"] == 31.0
    assert open(cron).read().strip() == "0", "kill-switch must be set to 0 on cap breach"


@case("month-2 stays live at $40 (under the $75 steady cap)")
def _():
    log = _tmp("spend-log.json")
    cron = _tmp("CRON_ENABLED")
    with open(cron, "w") as f:
        f.write("1\n")
    st.record_run(_run("2026-06-15T04:00:00Z", apify=5.0), path=log)   # first active month
    st.record_run(_run("2026-07-10T04:00:00Z", apify=40.0), path=log)  # month 2
    status = st.check_and_maybe_suspend(log_path=log, cron_enabled_path=cron, month="2026-07")
    assert status["suspended"] is False and status["cap_usd"] == 75.0
    assert open(cron).read().strip() == "1"


print()
print("=" * 60)
print(f"Result: {PASSED} passed, {FAILED} failed")
print("=" * 60)
sys.exit(0 if FAILED == 0 else 1)
