"""Tests for the Flyway 4.5+h baseline + trigger engine.

Deterministic, no network, no spend. Synthetic multi-week histories prove each
trigger fires when the data warrants it; the real smoke corpus is then run to
document the honest single-season outcome.

Run from repo root:
    python wildlifestats/_pipeline/flyway/test_triggers.py
"""
from __future__ import annotations

import os
import sys
import traceback

from wildlifestats._pipeline.flyway import triggers

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


SIG = "phenology.baby_season_start.songbird"


def rec(rid, state, date_str, center):
    return {
        "record_id": rid, "signal_id": SIG, "source_url": center,
        "extracted_fields": {"geo_state": state, "event_date": date_str},
    }


def fired_of(results, ttype):
    return [r for r in results if r.trigger_type == ttype and r.fired]


print("=" * 60)
print("Flyway 4.5+h trigger engine")
print("=" * 60)


@case("volume_spike fires when latest week exceeds mean + 2sigma")
def _():
    # 6 prior weeks of 1 record each (mean 1, std 0), then a latest week of 5.
    weekly_dates = ["2026-01-05", "2026-01-12", "2026-01-19", "2026-01-26",
                    "2026-02-02", "2026-02-09"]
    records = [rec(f"p{i}", "XX", d, "https://c/a") for i, d in enumerate(weekly_dates)]
    records += [rec(f"l{i}", "XX", "2026-02-16", "https://c/a") for i in range(5)]
    res = triggers.evaluate(records, {})
    vol = fired_of(res, "volume_spike")
    assert vol, "expected a volume_spike to fire"
    assert vol[0].observed == 5 and vol[0].scope == "state=XX"
    assert vol[0].threshold == 1.0, f"threshold should be mean1+2*0=1, got {vol[0].threshold}"


@case("volume_spike does NOT fire with insufficient baseline history")
def _():
    records = [rec("a", "XX", "2026-01-05", "https://c/a"),
               rec("b", "XX", "2026-01-12", "https://c/a"),
               rec("c", "XX", "2026-01-19", "https://c/a")]  # 2 prior weeks only
    res = triggers.evaluate(records, {})
    vol = [r for r in res if r.trigger_type == "volume_spike"]
    assert vol and not vol[0].fired
    assert "insufficient_baseline_history" in vol[0].reason


@case("presence fires with >= 3 distinct centers in a 7-day window")
def _():
    records = [rec("a", "NY", "2026-03-01", "https://c/a"),
               rec("b", "NY", "2026-03-02", "https://c/b"),
               rec("c", "TN", "2026-03-03", "https://c/c")]
    res = triggers.evaluate(records, {})
    pres = fired_of(res, "presence")
    assert pres, "expected presence to fire on 3 distinct centers"
    assert pres[0].observed == 3


@case("presence does NOT fire with only 2 distinct centers")
def _():
    records = [rec("a", "NY", "2026-03-01", "https://c/a"),
               rec("b", "NY", "2026-03-02", "https://c/b"),
               rec("c", "NY", "2026-03-03", "https://c/a")]  # a repeats
    res = triggers.evaluate(records, {})
    pres = [r for r in res if r.trigger_type == "presence"]
    assert pres and not pres[0].fired
    assert "below_threshold" in pres[0].reason


@case("presence window is bounded — centers 8 days apart do not co-occur")
def _():
    records = [rec("a", "NY", "2026-03-01", "https://c/a"),
               rec("b", "NY", "2026-03-05", "https://c/b"),
               rec("c", "NY", "2026-03-20", "https://c/c")]  # c far outside window
    res = triggers.evaluate(records, {})
    pres = [r for r in res if r.trigger_type == "presence"][0]
    assert not pres.fired and pres.observed == 2, f"only 2 centers should co-occur, got {pres.observed}"


@case("real smoke corpus runs and reports an honest single-season outcome")
def _():
    path = os.path.join(triggers.REPO, "secure", "cube", "flyway", "signals",
                        "smoke-2026-W24-llm.json")
    if not os.path.exists(path):
        print("    (skipped — smoke corpus not present)")
        return
    records = triggers.load_records(path)
    res = triggers.evaluate(records, triggers.load_signal_defs())
    assert res, "evaluation should produce results"
    # Single-season corpus: no volume_spike can fire (no 4-week baseline), and
    # only 2 distinct centers exist, so presence cannot fire either. This is the
    # honest finding that motivates recurring collection (4.5+i).
    assert not [r for r in res if r.fired], \
        "single-season smoke corpus must not fire any trigger under honest thresholds"
    vol = [r for r in res if r.trigger_type == "volume_spike"]
    assert all("insufficient_baseline_history" in r.reason for r in vol)


print()
print("=" * 60)
print(f"Result: {PASSED} passed, {FAILED} failed")
print("=" * 60)
sys.exit(0 if FAILED == 0 else 1)
