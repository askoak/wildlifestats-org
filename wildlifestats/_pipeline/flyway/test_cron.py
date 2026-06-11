"""Tests for the Flyway 4.5+i.1 cron skeleton + tier rosters.

Deterministic, no network, no spend. Proves the kill-switch gates, the daily
plan is built from the real roster, and — critically — that there is NO live
spend path in this sub-PR (the executor refuses until 4.5+i.2).

Run from repo root:
    python wildlifestats/_pipeline/flyway/test_cron.py
"""
from __future__ import annotations

import sys
import traceback

from wildlifestats._pipeline.flyway import build_tier_rosters, cron_run

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


print("=" * 60)
print("Flyway 4.5+i.1 cron skeleton + tier rosters")
print("=" * 60)


@case("select_tiers splits the social roster into 50 + the rest")
def _():
    tier1, tier2 = build_tier_rosters.select_tiers()
    assert len(tier1) == 50, f"expected 50 Tier-1, got {len(tier1)}"
    assert len(tier2) >= 1, "expected a non-empty Tier-2"
    assert tier1[0]["rank"] == "1", f"Tier-1 should lead with rank 1, got {tier1[0]['rank']}"
    assert all(c["platforms"] for c in tier1), "every Tier-1 center needs >=1 scrapeable URL"


@case("CRON_ENABLED ships disabled — cron is suspended")
def _():
    assert cron_run.is_enabled() is False, "CRON_ENABLED must ship as '0' (suspended)"


@case("plan_today builds FB/IG requests for both tiers with a positive cost ceiling")
def _():
    plan = cron_run.plan_today()
    assert plan, "plan should be non-empty"
    assert all(r.platform in ("facebook", "instagram") for r in plan)
    assert {r.tier for r in plan} == {1, 2}, "plan should cover both tiers"
    assert all(r.since_date == cron_run.DAILY_WINDOW for r in plan)
    est = __import__("wildlifestats._pipeline._common.apify_client",
                     fromlist=["estimate_cost"]).estimate_cost(plan)
    assert est > 0


@case("run(dry_run) prints the plan without scraping when enabled")
def _():
    saved = cron_run.is_enabled
    cron_run.is_enabled = lambda: True
    try:
        rc = cron_run.run(dry_run=True)
        assert rc == 0
    finally:
        cron_run.is_enabled = saved


@case("run(live) REFUSES to spend — no live executor until 4.5+i.2")
def _():
    saved = cron_run.is_enabled
    cron_run.is_enabled = lambda: True
    try:
        cron_run.run(dry_run=False)
        assert False, "expected NotImplementedError — there must be no live-spend path yet"
    except NotImplementedError as e:
        assert "4.5+i.2" in str(e)
    finally:
        cron_run.is_enabled = saved


print()
print("=" * 60)
print(f"Result: {PASSED} passed, {FAILED} failed")
print("=" * 60)
sys.exit(0 if FAILED == 0 else 1)
