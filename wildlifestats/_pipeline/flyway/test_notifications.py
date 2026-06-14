"""Tests for the Flyway 4.5+i.3 weekly digest + trigger alert emitter.

Deterministic, no network, no credentials. Uses temporary JSON artifacts to
prove quiet-week digest math, zero-trigger streak accounting, and one-file-per-
trigger alert emission.

Run from repo root:
    python wildlifestats/_pipeline/flyway/test_notifications.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import traceback

from wildlifestats._pipeline.flyway import notifications as note

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


def _tmpdir() -> str:
    return tempfile.mkdtemp()


def _write_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def _record(record_id: str, event_date: str, source_url: str, source_type: str = "facebook") -> dict:
    return {
        "record_id": record_id,
        "signal_id": "phenology.baby_season_start.songbird",
        "source_type": source_type,
        "source_url": source_url,
        "extracted_fields": {"event_date": event_date},
    }


def _trigger_payload(*, fired: list[dict], n_evaluated: int = 3) -> dict:
    return {
        "run_id": "weekly-2026-W24",
        "n_evaluated": n_evaluated,
        "n_fired": len(fired),
        "fired": fired,
        "evaluated": fired,
    }


print("=" * 60)
print("Flyway 4.5+i.3 notifications")
print("=" * 60)


@case("weekly digest surfaces quiet-week spend and zero-trigger streak")
def _():
    tmp = _tmpdir()
    triggers_dir = os.path.join(tmp, "triggers")
    _write_json(os.path.join(triggers_dir, "triggers-2026-W22.json"), {"n_fired": 0, "fired": []})
    _write_json(os.path.join(triggers_dir, "triggers-2026-W23.json"), {"n_fired": 0, "fired": []})
    current_payload = _trigger_payload(fired=[])

    records = [
        _record("a", "2026-06-08", "https://c/a", "facebook"),
        _record("b", "2026-06-09", "https://c/b", "instagram"),
        _record("c", "2026-06-10", "https://c/a", "facebook"),
    ]
    spend_runs = [
        {"timestamp": "2026-06-02T04:00:00Z", "actor_runs": 4, "total_usd": 3.10},
        {"timestamp": "2026-06-09T04:00:00Z", "actor_runs": 8, "posts_scanned": 47, "total_usd": 4.20},
    ]
    draft = note.build_weekly_digest_draft(
        week_id="2026-W24",
        trigger_payload=current_payload,
        signal_records=records,
        spend_runs=spend_runs,
        trigger_history=note.discover_trigger_history(triggers_dir),
        generated_at="2026-06-14T12:00:00Z",
        trigger_artifact="secure/cube/flyway/triggers/triggers-2026-W24.json",
    )
    body = draft.body
    assert draft.filename == "INBOX-flyway-weekly-digest-2026-W24.md"
    assert "Scrape: 47 posts across 2 centers, 2 platforms (8 actor-runs)" in body
    assert "Signals extracted: 3 records" in body
    assert "Triggers fired: 0" in body
    assert "Spend this week: $4.20" in body
    assert "Spend month-to-date: $7.30 / $30.00" in body
    assert "Rolling 7-day spend: $4.20" in body
    assert "Zero-trigger weeks observed: 3 total (quiet streak: 3)" in body
    assert "Quiet week: no triggers this week, $4.20 spent" in body


@case("weekly digest falls back to actor-runs when post counts are absent")
def _():
    current_payload = _trigger_payload(fired=[])
    draft = note.build_weekly_digest_draft(
        week_id="2026-W24",
        trigger_payload=current_payload,
        signal_records=[],
        spend_runs=[{"timestamp": "2026-06-09T04:00:00Z", "actor_runs": 5, "total_usd": 1.25}],
        trigger_history=[],
        generated_at="2026-06-14T12:00:00Z",
    )
    assert "Scrape: 5 actor-runs" in draft.body


@case("trigger alert draft includes the fired trigger provenance")
def _():
    fired = [{
        "signal_id": "hazard.window_strike_spike",
        "trigger_type": "volume_spike",
        "scope": "state=NY",
        "window": "2026-W24",
        "observed": 5,
        "baseline_mean": 1.0,
        "baseline_stddev": 0.0,
        "threshold": 1.0,
        "reason": "",
        "provenance": {
            "centers": ["https://c/a", "https://c/b"],
            "record_ids": ["r1", "r2"],
        },
    }]
    drafts = note.build_trigger_alert_drafts(
        week_id="2026-W24",
        trigger_payload=_trigger_payload(fired=fired),
        generated_at="2026-06-14T12:00:00Z",
        trigger_artifact="secure/cube/flyway/triggers/triggers-2026-W24.json",
    )
    assert len(drafts) == 1
    assert drafts[0].filename == "INBOX-flyway-trigger-2026-W24-hazard-window-strike-spike-volume-spike-state-ny.md"
    body = drafts[0].body
    assert "hazard.window_strike_spike [volume_spike] fired for state=NY" in body
    assert "Observed: 5" in body
    assert "Threshold: 1.0" in body
    assert "Centers: `https://c/a`, `https://c/b`" in body
    assert "Record IDs: `r1`, `r2`" in body


@case("emit_notifications writes one digest plus one file per fired trigger")
def _():
    tmp = _tmpdir()
    out_dir = os.path.join(tmp, "handoff")
    triggers_dir = os.path.join(tmp, "triggers")
    payload = _trigger_payload(fired=[{
        "signal_id": "phenology.first_of_season.monarch_spring",
        "trigger_type": "presence",
        "scope": "national",
        "window": "2026-06-09..2026-06-15",
        "observed": 3,
        "threshold": 3,
        "provenance": {"centers": ["https://c/a"], "record_ids": ["ra"]},
    }], n_evaluated=1)
    _write_json(os.path.join(triggers_dir, "triggers-2026-W24.json"), payload)
    written = note.emit_notifications(
        week_id="2026-W24",
        trigger_payload=payload,
        signal_records=[_record("ra", "2026-06-10", "https://c/a")],
        spend_runs=[{"timestamp": "2026-06-09T04:00:00Z", "actor_runs": 1, "total_usd": 0.75}],
        out_dir=out_dir,
        triggers_dir=triggers_dir,
        generated_at="2026-06-14T12:00:00Z",
        trigger_artifact="secure/cube/flyway/triggers/triggers-2026-W24.json",
    )
    basenames = sorted(os.path.basename(path) for path in written)
    assert basenames == [
        "INBOX-flyway-trigger-2026-W24-phenology-first-of-season-monarch-spring-presence-national.md",
        "INBOX-flyway-weekly-digest-2026-W24.md",
    ]
    assert all(os.path.exists(path) for path in written)


print()
print("=" * 60)
print(f"Result: {PASSED} passed, {FAILED} failed")
print("=" * 60)
sys.exit(0 if FAILED == 0 else 1)
