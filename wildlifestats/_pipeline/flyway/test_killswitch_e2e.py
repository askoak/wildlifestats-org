"""End-to-end test for the Flyway 4.5+i kill-switch chain.

Deterministic, no network, no live spend. Validates the intended operator
flow end-to-end against temp files only:
  1. CRON_ENABLED="0" keeps the cron suspended.
  2. Manual enable to "1" allows an under-cap dry-run to proceed.
  3. A cap breach trips the kill-switch back to "0" on the next tick.
  4. Manual same-month re-enable is rejected by the spend guard.
  5. Manual restoration works again in the next calendar month.

Run from repo root:
    python wildlifestats/_pipeline/flyway/test_killswitch_e2e.py
"""
from __future__ import annotations

import os
import sys
import tempfile
import traceback

from wildlifestats._pipeline.flyway import cron_run
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


def _write(path: str, value: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(value)


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def _run(ts, apify=0.0, llm=0.0):
    return {
        "timestamp": ts,
        "tier": 1,
        "actor_runs": 1,
        "apify_cost_usd": apify,
        "llm_cost_usd": llm,
    }


print("=" * 60)
print("Flyway 4.5+i.4 kill-switch end-to-end")
print("=" * 60)


@case("toggle -> cap breach -> same-month block -> next-month restore")
def _():
    log = _tmp("spend-log.json")
    cron = _tmp("CRON_ENABLED")

    saved_cron_path = cron_run.CRON_ENABLED_FILE
    saved_guard = cron_run.spend_tracker.check_and_maybe_suspend
    saved_now_month = st._now_month

    try:
        cron_run.CRON_ENABLED_FILE = cron

        # Route the cron's pre-flight guard at temp-only files so the test never
        # touches the committed kill-switch or spend log.
        cron_run.spend_tracker.check_and_maybe_suspend = lambda: saved_guard(
            log_path=log, cron_enabled_path=cron, month=st._now_month())

        st._now_month = lambda: "2026-06"

        _write(cron, "0\n")
        rc = cron_run.run(dry_run=True)
        assert rc == 0
        assert _read(cron) == "0", "disabled cron must stay suspended"

        _write(cron, "1\n")
        rc = cron_run.run(dry_run=True)
        assert rc == 0
        assert _read(cron) == "1", "manual enable should hold when under cap"

        st.record_run(_run("2026-06-15T04:00:00Z", apify=20.0), path=log)
        st.record_run(_run("2026-06-16T04:00:00Z", apify=11.0), path=log)
        rc = cron_run.run(dry_run=True)
        assert rc == 0
        assert _read(cron) == "0", "cap breach must trip the kill-switch"

        _write(cron, "1\n")
        rc = cron_run.run(dry_run=True)
        assert rc == 0
        assert _read(cron) == "0", (
            "same-month manual re-enable must be rejected by the spend guard")

        st._now_month = lambda: "2026-07"
        _write(cron, "1\n")
        rc = cron_run.run(dry_run=True)
        assert rc == 0
        assert _read(cron) == "1", "next-month manual restore should stay live"
    finally:
        cron_run.CRON_ENABLED_FILE = saved_cron_path
        cron_run.spend_tracker.check_and_maybe_suspend = saved_guard
        st._now_month = saved_now_month


print()
print("=" * 60)
print(f"Result: {PASSED} passed, {FAILED} failed")
print("=" * 60)
sys.exit(0 if FAILED == 0 else 1)
