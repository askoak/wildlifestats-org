"""Offline tests for the aggregate-only eBird denominator stratifier.

Run:
  PYTHONPATH=. python wildlifestats/_pipeline/ebird_sampling/test_stratify.py
"""

from __future__ import annotations

import csv
import sys
import tempfile
import traceback
from pathlib import Path

from wildlifestats._pipeline.ebird_sampling import stratify

PASSED = 0
FAILED = 0

FIELDNAMES = [
    "state_name",
    "state_code",
    "county_name",
    "county_code",
    "iso_year",
    "iso_week",
    "week_start_date",
    "week_end_date",
    "observation_type",
    "protocol_name",
    "protocol_code",
    "complete_checklist_count",
    "sampling_event_count",
    "number_observers_total",
    "duration_minutes_count",
    "duration_minutes_total",
    "effort_distance_km_count",
    "effort_distance_km_total",
    "effort_area_ha_count",
    "effort_area_ha_total",
    "first_observation_date",
    "last_observation_date",
]


def case(name):
    def deco(fn):
        global PASSED, FAILED
        try:
            fn()
            PASSED += 1
            print(f"  PASS  {name}")
        except AssertionError as exc:
            FAILED += 1
            print(f"  FAIL  {name}: {exc}")
        except Exception as exc:  # noqa: BLE001
            FAILED += 1
            print(f"  ERROR {name}: {type(exc).__name__}: {exc}")
            traceback.print_exc()
        return fn

    return deco


def _write_input_csv(path: Path) -> None:
    rows = [
        {
            "state_name": "Virginia",
            "state_code": "US-VA",
            "county_name": "Fairfax",
            "county_code": "US-VA-059",
            "iso_year": "2026",
            "iso_week": "1",
            "week_start_date": "2025-12-29",
            "week_end_date": "2026-01-04",
            "observation_type": "Traveling",
            "protocol_name": "Traveling",
            "protocol_code": "P22",
            "complete_checklist_count": "4",
            "sampling_event_count": "4",
            "number_observers_total": "4",
            "duration_minutes_count": "4",
            "duration_minutes_total": "120.0",
            "effort_distance_km_count": "4",
            "effort_distance_km_total": "8.0",
            "effort_area_ha_count": "0",
            "effort_area_ha_total": "0.0",
            "first_observation_date": "2026-01-01",
            "last_observation_date": "2026-01-02",
        },
        {
            "state_name": "Virginia",
            "state_code": "US-VA",
            "county_name": "Fairfax",
            "county_code": "US-VA-059",
            "iso_year": "2026",
            "iso_week": "1",
            "week_start_date": "2025-12-29",
            "week_end_date": "2026-01-04",
            "observation_type": "Incidental",
            "protocol_name": "Incidental",
            "protocol_code": "P20",
            "complete_checklist_count": "7",
            "sampling_event_count": "7",
            "number_observers_total": "7",
            "duration_minutes_count": "0",
            "duration_minutes_total": "0.0",
            "effort_distance_km_count": "0",
            "effort_distance_km_total": "0.0",
            "effort_area_ha_count": "0",
            "effort_area_ha_total": "0.0",
            "first_observation_date": "2026-01-03",
            "last_observation_date": "2026-01-03",
        },
        {
            "state_name": "Virginia",
            "state_code": "US-VA",
            "county_name": "Richmond City",
            "county_code": "US-VA-760",
            "iso_year": "2026",
            "iso_week": "2",
            "week_start_date": "2026-01-05",
            "week_end_date": "2026-01-11",
            "observation_type": "Historical",
            "protocol_name": "Historical",
            "protocol_code": "P62",
            "complete_checklist_count": "2",
            "sampling_event_count": "2",
            "number_observers_total": "1",
            "duration_minutes_count": "1",
            "duration_minutes_total": "90.0",
            "effort_distance_km_count": "0",
            "effort_distance_km_total": "0.0",
            "effort_area_ha_count": "0",
            "effort_area_ha_total": "0.0",
            "first_observation_date": "2026-01-09",
            "last_observation_date": "2026-01-09",
        },
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


print("=" * 60)
print("ebird_sampling stratifier")
print("=" * 60)


@case("stratify_effort_csv adds effort_metadata_class and summarizes counts")
def _():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        input_path = tmp_path / "input.csv"
        output_path = tmp_path / "output.csv"
        summary_path = tmp_path / "summary.yml"
        _write_input_csv(input_path)

        run = stratify.stratify_effort_csv(
            input_path,
            output_csv_path=output_path,
            summary_path=summary_path,
            expected_source_sha256=None,
        )

        assert run.total_rows == 3, run.total_rows
        assert run.total_complete_checklists == 13, run.total_complete_checklists
        assert run.effort_present_rows == 2, run.effort_present_rows
        assert run.zero_effort_rows == 1, run.zero_effort_rows
        assert run.effort_present_checklists == 6, run.effort_present_checklists
        assert run.zero_effort_checklists == 7, run.zero_effort_checklists
        assert run.zero_effort_by_protocol["Incidental"] == 7

        output_text = output_path.read_text(encoding="utf-8")
        assert "effort_metadata_class" in output_text
        assert "zero_effort" in output_text
        assert "effort_present" in output_text

        summary_text = summary_path.read_text(encoding="utf-8")
        assert "zero_effort_complete_checklists: 7" in summary_text
        assert "effort_present_complete_checklists: 6" in summary_text
        assert "Incidental: 7" in summary_text


@case("stratify_effort_csv enforces the expected source sha when provided")
def _():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        input_path = tmp_path / "input.csv"
        _write_input_csv(input_path)
        try:
            stratify.stratify_effort_csv(input_path, expected_source_sha256="bad-hash")
            assert False, "expected sha mismatch"
        except ValueError as exc:
            assert "sha256 mismatch" in str(exc)


print()
print("=" * 60)
print(f"Result: {PASSED} passed, {FAILED} failed")
print("=" * 60)
sys.exit(0 if FAILED == 0 else 1)
