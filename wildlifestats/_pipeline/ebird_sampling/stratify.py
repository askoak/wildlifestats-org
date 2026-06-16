"""Stratify the aggregate-only eBird denominator pilot by effort metadata.

Run from repo root:
    python wildlifestats/_pipeline/ebird_sampling/stratify.py
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
DEFAULT_SOURCE_ROOT = REPO_ROOT / "wildlifestats/_pipeline/sources/ebird-sampling"
DEFAULT_INPUT_CSV = (
    DEFAULT_SOURCE_ROOT
    / "results/virginia_complete_checklist_effort_by_county_week_protocol.csv"
)
DEFAULT_OUTPUT_CSV = (
    DEFAULT_SOURCE_ROOT
    / "results/virginia_complete_checklist_effort_by_county_week_protocol_stratified.csv"
)
DEFAULT_SUMMARY_PATH = (
    DEFAULT_SOURCE_ROOT
    / "results/virginia_complete_checklist_effort_by_county_week_protocol_stratified.summary.yml"
)
CANONICAL_SOURCE_SHA256 = "553f847986b3a39145b7308987fe02eb4bcee15fbf68b28a536a36c0525847f2"

EFFORT_COUNT_COLUMNS = (
    "duration_minutes_count",
    "effort_distance_km_count",
    "effort_area_ha_count",
)
CLASSIFICATION_COLUMN = "effort_metadata_class"
EFFORT_PRESENT = "effort_present"
ZERO_EFFORT = "zero_effort"


@dataclass
class StratifyRun:
    source_csv_path: Path
    source_csv_sha256: str
    output_csv_path: Path
    output_csv_sha256: str
    summary_path: Path
    total_rows: int
    effort_present_rows: int
    zero_effort_rows: int
    total_complete_checklists: int
    effort_present_checklists: int
    zero_effort_checklists: int
    zero_effort_by_protocol: Counter[str] = field(default_factory=Counter)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _yaml_scalar(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value))


def _yaml_lines(value: object, indent: int = 0) -> list[str]:
    prefix = "  " * indent
    if isinstance(value, dict):
        if not value:
            return [f"{prefix}{{}}"]
        lines: list[str] = []
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                if not item:
                    empty = "{}" if isinstance(item, dict) else "[]"
                    lines.append(f"{prefix}{key}: {empty}")
                    continue
                lines.append(f"{prefix}{key}:")
                lines.extend(_yaml_lines(item, indent + 1))
            else:
                lines.append(f"{prefix}{key}: {_yaml_scalar(item)}")
        return lines
    if isinstance(value, list):
        if not value:
            return [f"{prefix}[]"]
        lines: list[str] = []
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}-")
                lines.extend(_yaml_lines(item, indent + 1))
            else:
                lines.append(f"{prefix}- {_yaml_scalar(item)}")
        return lines
    return [f"{prefix}{_yaml_scalar(value)}"]


def _dump_yaml(payload: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(_yaml_lines(payload)) + "\n", encoding="utf-8")


def _classify_row(row: dict[str, str]) -> str:
    any_effort = any(int(row[column]) > 0 for column in EFFORT_COUNT_COLUMNS)
    return EFFORT_PRESENT if any_effort else ZERO_EFFORT


def _output_fieldnames(fieldnames: list[str]) -> list[str]:
    if CLASSIFICATION_COLUMN in fieldnames:
        return fieldnames
    if "effort_area_ha_total" in fieldnames:
        insert_at = fieldnames.index("effort_area_ha_total") + 1
        return fieldnames[:insert_at] + [CLASSIFICATION_COLUMN] + fieldnames[insert_at:]
    return fieldnames + [CLASSIFICATION_COLUMN]


def _build_summary_payload(run: StratifyRun) -> dict[str, object]:
    zero_effort_protocols = {
        name: count
        for name, count in run.zero_effort_by_protocol.most_common()
        if count > 0
    }
    return {
        "source_csv_path": str(run.source_csv_path).replace("\\", "/"),
        "source_csv_sha256": run.source_csv_sha256,
        "output_csv_path": str(run.output_csv_path).replace("\\", "/"),
        "output_csv_sha256": run.output_csv_sha256,
        "generated_at_utc": _utc_now(),
        "classification_rule": {
            "effort_present_when_any_count_gt_zero": list(EFFORT_COUNT_COLUMNS),
            "zero_effort_when_all_counts_equal_zero": list(EFFORT_COUNT_COLUMNS),
        },
        "totals": {
            "aggregate_rows": run.total_rows,
            "total_complete_checklists": run.total_complete_checklists,
            "effort_present_rows": run.effort_present_rows,
            "effort_present_complete_checklists": run.effort_present_checklists,
            "zero_effort_rows": run.zero_effort_rows,
            "zero_effort_complete_checklists": run.zero_effort_checklists,
        },
        "zero_effort_complete_checklists_by_protocol": zero_effort_protocols,
    }


def stratify_effort_csv(
    input_csv_path: Path,
    *,
    output_csv_path: Path = DEFAULT_OUTPUT_CSV,
    summary_path: Path = DEFAULT_SUMMARY_PATH,
    expected_source_sha256: str | None = CANONICAL_SOURCE_SHA256,
) -> StratifyRun:
    if not input_csv_path.exists():
        raise FileNotFoundError(f"input csv not found: {input_csv_path}")

    source_csv_sha256 = _sha256_of_file(input_csv_path)
    if expected_source_sha256 and source_csv_sha256 != expected_source_sha256:
        raise ValueError(
            f"source csv sha256 mismatch: expected {expected_source_sha256}, got {source_csv_sha256}"
        )

    output_csv_path.parent.mkdir(parents=True, exist_ok=True)

    total_rows = 0
    effort_present_rows = 0
    zero_effort_rows = 0
    total_complete_checklists = 0
    effort_present_checklists = 0
    zero_effort_checklists = 0
    zero_effort_by_protocol: Counter[str] = Counter()

    with input_csv_path.open("r", encoding="utf-8", newline="") as source_handle:
        reader = csv.DictReader(source_handle)
        if reader.fieldnames is None:
            raise ValueError("input csv is missing a header row")
        output_fieldnames = _output_fieldnames(list(reader.fieldnames))

        with output_csv_path.open("w", encoding="utf-8", newline="") as output_handle:
            writer = csv.DictWriter(output_handle, fieldnames=output_fieldnames)
            writer.writeheader()

            for row in reader:
                total_rows += 1
                checklist_count = int(row["complete_checklist_count"])
                classification = _classify_row(row)
                row[CLASSIFICATION_COLUMN] = classification
                writer.writerow(row)

                total_complete_checklists += checklist_count
                if classification == EFFORT_PRESENT:
                    effort_present_rows += 1
                    effort_present_checklists += checklist_count
                else:
                    zero_effort_rows += 1
                    zero_effort_checklists += checklist_count
                    zero_effort_by_protocol[row["protocol_name"]] += checklist_count

    output_csv_sha256 = _sha256_of_file(output_csv_path)
    run = StratifyRun(
        source_csv_path=input_csv_path,
        source_csv_sha256=source_csv_sha256,
        output_csv_path=output_csv_path,
        output_csv_sha256=output_csv_sha256,
        summary_path=summary_path,
        total_rows=total_rows,
        effort_present_rows=effort_present_rows,
        zero_effort_rows=zero_effort_rows,
        total_complete_checklists=total_complete_checklists,
        effort_present_checklists=effort_present_checklists,
        zero_effort_checklists=zero_effort_checklists,
        zero_effort_by_protocol=zero_effort_by_protocol,
    )
    _dump_yaml(_build_summary_payload(run), summary_path)
    return run


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-csv", default=str(DEFAULT_INPUT_CSV))
    parser.add_argument("--output-csv", default=str(DEFAULT_OUTPUT_CSV))
    parser.add_argument("--summary", default=str(DEFAULT_SUMMARY_PATH))
    parser.add_argument("--expected-source-sha256", default=CANONICAL_SOURCE_SHA256)
    args = parser.parse_args()

    run = stratify_effort_csv(
        Path(args.input_csv),
        output_csv_path=Path(args.output_csv),
        summary_path=Path(args.summary),
        expected_source_sha256=args.expected_source_sha256 or None,
    )
    print(f"Source CSV verified: sha256={run.source_csv_sha256}")
    print(f"Aggregate rows stratified: {run.total_rows}")
    print(f"Total complete checklists: {run.total_complete_checklists}")
    print(f"Primary denominator (effort_present): {run.effort_present_checklists}")
    print(f"Low-trust zero-effort checklists: {run.zero_effort_checklists}")
    print(f"Wrote stratified CSV: {run.output_csv_path}")
    print(f"Wrote summary YAML: {run.summary_path}")


if __name__ == "__main__":
    main()
