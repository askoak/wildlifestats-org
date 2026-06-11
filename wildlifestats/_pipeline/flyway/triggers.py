#!/usr/bin/env python3
"""Flyway Phase 4.5+h — baseline + trigger engine.

Analytical only. Consumes extracted §4 signal records (the extract.py output)
and the committed signal definitions, computes per-signal baselines, and emits a
triggers.json audit artifact listing which triggers fired and — just as
importantly — which did NOT and why. NO social spend: this reuses the existing
corpus. The daily cron (4.5+i) stays disabled.

THRESHOLDS (architect prior, 2026-06-11 INBOX 4.5+h-dispatched; surfaced here so
the choice is auditable):

  volume_spike   current-week count > rolling baseline mean + VOLUME_SIGMA·stddev,
                 baseline = the up-to-8 prior weeks. Requires >= MIN_BASELINE_WEEKS
                 of prior history; below that, "insufficient_baseline_history".
  presence       >= PRESENCE_MIN_CENTERS distinct centers reporting the same
                 signal within a PRESENCE_WINDOW_DAYS rolling window.
  early / late   phenology first_of_season: first-observation week vs a multi-year
                 baseline (signal def baseline_period_years). The smoke corpus has
                 no multi-year history, so these report insufficient_baseline_history
                 rather than firing on noise.

Every fired trigger carries provenance: the record_ids, centers, week(s), the
baseline it beat, and the threshold — the audit trail that would justify a
recurring-collection spend (4.5+i).

Run:
    python -m wildlifestats._pipeline.flyway.triggers \
        --signals secure/cube/flyway/signals/smoke-2026-W24-llm.json \
        --out secure/cube/flyway/triggers/triggers-2026-W24.json \
        --run-id smoke-2026-W24
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import statistics
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from typing import Optional

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SIGNALS_DIR = os.path.join(REPO, "wildlifestats", "_pipeline", "sources", "flyway", "signals")

# --- thresholds (auditable; see module docstring) ---
VOLUME_SIGMA = 2.0
VOLUME_BASELINE_WEEKS = 8
MIN_BASELINE_WEEKS = 4
PRESENCE_MIN_CENTERS = 3
PRESENCE_WINDOW_DAYS = 7


@dataclass
class TriggerResult:
    signal_id: str
    trigger_type: str          # volume_spike | presence | early | late
    scope: str                 # e.g. "state=NY" or "national"
    fired: bool
    observed: Optional[float] = None
    baseline_mean: Optional[float] = None
    baseline_stddev: Optional[float] = None
    threshold: Optional[float] = None
    window: Optional[str] = None
    reason: str = ""
    provenance: dict = field(default_factory=dict)


def load_signal_defs() -> dict:
    defs = {}
    for fp in sorted(glob.glob(os.path.join(SIGNALS_DIR, "*.json"))):
        with open(fp, encoding="utf-8") as f:
            d = json.load(f)
        defs[d["signal_id"]] = d
    return defs


def load_records(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["records"] if isinstance(data, dict) and "records" in data else data


def _iso_week_key(date_str: str) -> Optional[str]:
    try:
        y, m, d = (int(x) for x in date_str[:10].split("-"))
        iso = date(y, m, d).isocalendar()
        return f"{iso[0]:04d}-W{iso[1]:02d}"
    except (ValueError, AttributeError):
        return None


def _center(record: dict) -> str:
    """Stable per-center key — the source Page URL (no raw text)."""
    return record.get("source_url") or record.get("source_org_id") or "unknown"


def _event_date(record: dict) -> Optional[str]:
    return (record.get("extracted_fields") or {}).get("event_date")


def _state(record: dict) -> str:
    return (record.get("extracted_fields") or {}).get("geo_state") or "??"


def evaluate(records: list[dict], signal_defs: dict) -> list[TriggerResult]:
    """Evaluate every applicable trigger across all signals present in the
    records. Returns both fired and not-fired results for a full audit."""
    results: list[TriggerResult] = []
    by_signal: dict[str, list[dict]] = {}
    for r in records:
        by_signal.setdefault(r.get("signal_id", "unknown"), []).append(r)

    for signal_id, recs in sorted(by_signal.items()):
        sdef = signal_defs.get(signal_id, {})
        stype = sdef.get("signal_type", signal_id)
        # Volume/spike per state.
        results.extend(_eval_volume(signal_id, recs))
        # Presence per signal (national scope).
        results.append(_eval_presence(signal_id, recs))
        # Phenology arrival timing needs multi-year history we don't have.
        if stype.startswith("phenology.first_of_season"):
            results.append(TriggerResult(
                signal_id, "early_late", "national", False,
                reason="insufficient_baseline_history: arrival-timing needs "
                       f"{sdef.get('baseline_period_years', 5)}yr baseline; smoke corpus is single-season",
            ))
    return results


def _eval_volume(signal_id: str, recs: list[dict]) -> list[TriggerResult]:
    out: list[TriggerResult] = []
    by_state: dict[str, dict[str, list[dict]]] = {}
    for r in recs:
        wk = _iso_week_key(_event_date(r) or "")
        if not wk:
            continue
        by_state.setdefault(_state(r), {}).setdefault(wk, []).append(r)

    for state, weeks in sorted(by_state.items()):
        ordered = sorted(weeks)
        latest = ordered[-1]
        prior = ordered[:-1]
        observed = len(weeks[latest])
        if len(prior) < MIN_BASELINE_WEEKS:
            out.append(TriggerResult(
                signal_id, "volume_spike", f"state={state}", False,
                observed=observed, window=latest,
                reason=f"insufficient_baseline_history: {len(prior)} prior week(s), "
                       f"need >= {MIN_BASELINE_WEEKS}",
                provenance={"weeks_present": ordered,
                            "record_ids": [r.get("record_id") for r in weeks[latest]]},
            ))
            continue
        baseline_weeks = prior[-VOLUME_BASELINE_WEEKS:]
        counts = [len(weeks[w]) for w in baseline_weeks]
        mean = statistics.fmean(counts)
        std = statistics.pstdev(counts) if len(counts) > 1 else 0.0
        threshold = mean + VOLUME_SIGMA * std
        fired = observed > threshold and observed > 0
        out.append(TriggerResult(
            signal_id, "volume_spike", f"state={state}", fired,
            observed=observed, baseline_mean=round(mean, 3),
            baseline_stddev=round(std, 3), threshold=round(threshold, 3), window=latest,
            reason="" if fired else "below_threshold",
            provenance={"baseline_weeks": baseline_weeks,
                        "record_ids": [r.get("record_id") for r in weeks[latest]],
                        "centers": sorted({_center(r) for r in weeks[latest]})},
        ))
    return out


def _eval_presence(signal_id: str, recs: list[dict]) -> TriggerResult:
    dated = sorted(
        ((_event_date(r), r) for r in recs if _event_date(r)),
        key=lambda t: t[0],
    )
    best_window, best_centers, best_recs = None, set(), []
    for i, (d0, _) in enumerate(dated):
        try:
            start = date.fromisoformat(d0[:10])
        except ValueError:
            continue
        end = start + timedelta(days=PRESENCE_WINDOW_DAYS - 1)
        window_recs = [r for dd, r in dated
                       if start <= date.fromisoformat(dd[:10]) <= end]
        centers = {_center(r) for r in window_recs}
        if len(centers) > len(best_centers):
            best_centers, best_recs = centers, window_recs
            best_window = f"{start.isoformat()}..{end.isoformat()}"
    fired = len(best_centers) >= PRESENCE_MIN_CENTERS
    return TriggerResult(
        signal_id, "presence", "national", fired,
        observed=len(best_centers), threshold=PRESENCE_MIN_CENTERS, window=best_window,
        reason="" if fired else f"below_threshold: max {len(best_centers)} distinct "
                                f"center(s) in any {PRESENCE_WINDOW_DAYS}d window, "
                                f"need >= {PRESENCE_MIN_CENTERS}",
        provenance={"centers": sorted(best_centers),
                    "record_ids": [r.get("record_id") for r in best_recs]},
    )


def write_triggers(results: list[TriggerResult], out_path: str, run_id: str) -> dict:
    fired = [r for r in results if r.fired]
    payload = {
        "run_id": run_id,
        "thresholds": {
            "volume_sigma": VOLUME_SIGMA, "volume_baseline_weeks": VOLUME_BASELINE_WEEKS,
            "min_baseline_weeks": MIN_BASELINE_WEEKS,
            "presence_min_centers": PRESENCE_MIN_CENTERS,
            "presence_window_days": PRESENCE_WINDOW_DAYS,
        },
        "n_evaluated": len(results),
        "n_fired": len(fired),
        "fired": [asdict(r) for r in fired],
        "evaluated": [asdict(r) for r in results],
    }
    d = os.path.dirname(out_path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return payload


def main() -> int:
    ap = argparse.ArgumentParser(description="Flyway 4.5+h baseline + trigger engine")
    ap.add_argument("--signals", required=True, help="extracted §4 signal records JSON")
    ap.add_argument("--out", required=True, help="triggers.json output path")
    ap.add_argument("--run-id", default="adhoc")
    args = ap.parse_args()

    records = load_records(args.signals)
    results = evaluate(records, load_signal_defs())
    payload = write_triggers(results, args.out, args.run_id)
    print(f"evaluated {payload['n_evaluated']} triggers -> {payload['n_fired']} fired")
    for r in payload["fired"]:
        print(f"  FIRED  {r['signal_id']} [{r['trigger_type']}] {r['scope']} "
              f"observed={r['observed']} threshold={r['threshold']}")
    print(f"triggers: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
