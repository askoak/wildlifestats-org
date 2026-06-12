"""Tests for the 9d.01.2 dual-write leg in extract.py.

Deterministic, no network. Proves the §4 → signals-row mapping and the
resilience guarantee: if supabase_client.upsert() raises, the failure is
counted, never propagated — the JSON write (which happens first) stays canonical.

Run: python wildlifestats/_pipeline/flyway/test_dualwrite.py
"""
from __future__ import annotations

import sys
import traceback

from wildlifestats._pipeline._common import supabase_client
from wildlifestats._pipeline.flyway import extract as fx

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


REC = {
    "record_id": "abc123sha", "signal_id": "phenology.baby_season_start.songbird",
    "source_type": "facebook", "source_url": "https://fb.com/x",
    "extracted_at": "2026-06-11T00:00:00Z", "source_org_id": None,
    "extraction_method": "claude-haiku-flyway-extractor-v1",
    "extracted_fields": {"event_type": "songbird", "geo_state": "NY",
                         "event_date": "2026-06-10", "confidence": 0.85},
}

print("=" * 60)
print("9d.01.2 dual-write")
print("=" * 60)


@case("to_signal_row maps provenance envelope + derives iso_week")
def _():
    row = fx.to_signal_row(REC)
    assert row["record_id"] == "abc123sha"
    assert row["content_hash"] == "abc123sha", "record_id (a sha) doubles as content_hash"
    assert row["fetched_at"] == "2026-06-11T00:00:00Z" and row["source_url"] == "https://fb.com/x"
    assert row["platform"] == "facebook" and row["geo_state"] == "NY"
    assert row["iso_week"] == "2026-W24", f"got {row['iso_week']}"


@case("dual_write_supabase counts a Supabase failure, never propagates it")
def _():
    saved = supabase_client.upsert

    def boom(req):
        raise RuntimeError("supabase down")

    supabase_client.upsert = boom
    try:
        ok, failed = fx.dual_write_supabase([REC])
        assert ok == 0 and failed == 1, f"expected (0,1), got ({ok},{failed})"
    finally:
        supabase_client.upsert = saved


@case("dual_write_supabase counts a clean upsert as ok")
def _():
    saved = supabase_client.upsert
    supabase_client.upsert = lambda req: dict(req.record)
    try:
        ok, failed = fx.dual_write_supabase([REC])
        assert ok == 1 and failed == 0
    finally:
        supabase_client.upsert = saved


print()
print("=" * 60)
print(f"Result: {PASSED} passed, {FAILED} failed")
print("=" * 60)
sys.exit(0 if FAILED == 0 else 1)
