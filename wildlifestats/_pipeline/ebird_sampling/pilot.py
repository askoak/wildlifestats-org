"""Stream the eBird sampling archive into county-week effort denominators.

Local-only pilot for Virginia complete-checklist effort summaries.

Run from repo root:
    python wildlifestats/_pipeline/ebird_sampling/pilot.py \
      --archive C:/Users/Hello/Downloads/ebd_sampling_relMay-2026.tar
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import tarfile
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
DEFAULT_SOURCE_ROOT = REPO_ROOT / "wildlifestats/_pipeline/sources/ebird-sampling"
DEFAULT_RESULTS_DIR = DEFAULT_SOURCE_ROOT / "results"
DEFAULT_OUTPUT_CSV = DEFAULT_RESULTS_DIR / "virginia_complete_checklist_effort_by_county_week_protocol.csv"
DEFAULT_PROVENANCE_PATH = DEFAULT_SOURCE_ROOT / "provenance.yml"

DATA_MEMBER = "ebd_sampling_relMay-2026.txt.gz"
CITATION_MEMBER = "recommended_citation.txt"
TERMS_MEMBER = "terms_of_use.txt"
PROTOCOLS_MEMBER = "Protocols.txt"

REQUIRED_COLUMNS = (
    "STATE",
    "STATE CODE",
    "COUNTY",
    "COUNTY CODE",
    "OBSERVATION DATE",
    "SAMPLING EVENT IDENTIFIER",
    "OBSERVATION TYPE",
    "PROTOCOL NAME",
    "PROTOCOL CODE",
    "DURATION MINUTES",
    "EFFORT DISTANCE KM",
    "EFFORT AREA HA",
    "NUMBER OBSERVERS",
    "ALL SPECIES REPORTED",
)

OUTPUT_COLUMNS = (
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
)


@dataclass(frozen=True)
class SummaryKey:
    state_name: str
    state_code: str
    county_name: str
    county_code: str
    iso_year: int
    iso_week: int
    observation_type: str
    protocol_name: str
    protocol_code: str


@dataclass
class AggregateMetrics:
    complete_checklist_count: int = 0
    sampling_event_count: int = 0
    number_observers_total: int = 0
    duration_minutes_count: int = 0
    duration_minutes_total: float = 0.0
    effort_distance_km_count: int = 0
    effort_distance_km_total: float = 0.0
    effort_area_ha_count: int = 0
    effort_area_ha_total: float = 0.0
    first_observation_date: str | None = None
    last_observation_date: str | None = None

    def update_date_bounds(self, observed_on: str) -> None:
        if self.first_observation_date is None or observed_on < self.first_observation_date:
            self.first_observation_date = observed_on
        if self.last_observation_date is None or observed_on > self.last_observation_date:
            self.last_observation_date = observed_on


@dataclass
class PilotRun:
    archive_path: Path
    archive_size_bytes: int
    archive_sha256: str
    archive_members: list[str]
    citation: str
    rows_scanned: int
    retained_rows: int
    output_rows: int
    output_csv_path: Path
    output_csv_sha256: str
    min_observation_date: str | None
    max_observation_date: str | None
    protocol_totals: Counter[str] = field(default_factory=Counter)
    county_totals: Counter[str] = field(default_factory=Counter)


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


def _require_archive_members(archive_path: Path) -> list[str]:
    with tarfile.open(archive_path, "r") as tf:
        members = [member.name for member in tf.getmembers()]
    for required in (DATA_MEMBER, CITATION_MEMBER, TERMS_MEMBER, PROTOCOLS_MEMBER):
        if required not in members:
            raise ValueError(f"archive missing required member: {required}")
    return members


def _read_small_member_text(archive_path: Path, member_name: str) -> str:
    with tarfile.open(archive_path, "r") as tf:
        extracted = tf.extractfile(member_name)
        if extracted is None:
            raise ValueError(f"archive member not readable: {member_name}")
        return extracted.read().decode("utf-8", errors="replace").strip()


def _field_indices(header_line: str) -> dict[str, int]:
    header = header_line.rstrip("\n").split("\t")
    indices = {name: idx for idx, name in enumerate(header)}
    missing = [name for name in REQUIRED_COLUMNS if name not in indices]
    if missing:
        raise ValueError(f"sampling header missing required columns: {missing}")
    return indices


def _parse_optional_float(raw: str) -> float | None:
    raw = raw.strip()
    if not raw:
        return None
    return float(raw)


def _parse_optional_int(raw: str) -> int | None:
    raw = raw.strip()
    if not raw:
        return None
    return int(raw)


def _week_window(observed_on: date) -> tuple[str, str]:
    week_start = observed_on - timedelta(days=observed_on.isoweekday() - 1)
    week_end = week_start + timedelta(days=6)
    return week_start.isoformat(), week_end.isoformat()


def _iter_rows_from_archive(archive_path: Path):
    with tarfile.open(archive_path, "r") as tf:
        extracted = tf.extractfile(DATA_MEMBER)
        if extracted is None:
            raise ValueError(f"archive member not readable: {DATA_MEMBER}")
        with gzip.GzipFile(fileobj=extracted) as gz:
            wrapper = io.TextIOWrapper(gz, encoding="utf-8", newline="")
            indices = _field_indices(next(wrapper))
            for line in wrapper:
                yield line.rstrip("\n").split("\t"), indices


def _csv_rows_for_summary(summary: dict[SummaryKey, AggregateMetrics]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for key in sorted(
        summary,
        key=lambda item: (
            item.state_code,
            item.county_code,
            item.iso_year,
            item.iso_week,
            item.protocol_code,
        ),
    ):
        metrics = summary[key]
        week_start, week_end = _week_window(date.fromisoformat(metrics.first_observation_date))
        rows.append(
            {
                "state_name": key.state_name,
                "state_code": key.state_code,
                "county_name": key.county_name,
                "county_code": key.county_code,
                "iso_year": key.iso_year,
                "iso_week": key.iso_week,
                "week_start_date": week_start,
                "week_end_date": week_end,
                "observation_type": key.observation_type,
                "protocol_name": key.protocol_name,
                "protocol_code": key.protocol_code,
                "complete_checklist_count": metrics.complete_checklist_count,
                "sampling_event_count": metrics.sampling_event_count,
                "number_observers_total": metrics.number_observers_total,
                "duration_minutes_count": metrics.duration_minutes_count,
                "duration_minutes_total": round(metrics.duration_minutes_total, 3),
                "effort_distance_km_count": metrics.effort_distance_km_count,
                "effort_distance_km_total": round(metrics.effort_distance_km_total, 3),
                "effort_area_ha_count": metrics.effort_area_ha_count,
                "effort_area_ha_total": round(metrics.effort_area_ha_total, 3),
                "first_observation_date": metrics.first_observation_date,
                "last_observation_date": metrics.last_observation_date,
            }
        )
    return rows


def _write_csv(rows: list[dict[str, object]], output_csv_path: Path) -> None:
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    with output_csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(OUTPUT_COLUMNS))
        writer.writeheader()
        writer.writerows(rows)


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
        lines = []
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


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def _build_provenance_payload(run: PilotRun, state_code: str) -> dict[str, object]:
    top_protocols = [
        {"protocol_name": name, "complete_checklist_count": count}
        for name, count in run.protocol_totals.most_common(10)
    ]
    top_counties = [
        {"county_code": code, "complete_checklist_count": count}
        for code, count in run.county_totals.most_common(10)
    ]
    return {
        "source_system": "ebird_sampling",
        "verified_at_utc": _utc_now(),
        "local_only": True,
        "archive": {
            "path": str(run.archive_path),
            "size_bytes": run.archive_size_bytes,
            "sha256": run.archive_sha256,
            "members": run.archive_members,
            "data_member": DATA_MEMBER,
            "citation": run.citation,
        },
        "terms": {
            "data_terms_path": "wildlifestats/_pipeline/sources/ebird-sampling/DATA_TERMS.md",
            "non_commercial_only": True,
            "raw_row_redistribution_prohibited": True,
            "derived_outputs_must_carry_same_terms": True,
        },
        "pilot": {
            "target_state_code": state_code,
            "row_filter": {
                "all_species_reported": True,
                "aggregation_grain": "county_iso_week_protocol",
                "raw_row_commit_policy": "aggregate_only",
            },
            "rows_scanned": run.rows_scanned,
            "retained_complete_checklists": run.retained_rows,
            "output_rows": run.output_rows,
            "observation_date_min": run.min_observation_date,
            "observation_date_max": run.max_observation_date,
            "output_csv_path": _display_path(run.output_csv_path),
            "output_csv_sha256": run.output_csv_sha256,
            "top_protocols": top_protocols,
            "top_counties": top_counties,
        },
    }


def run_pilot(
    archive_path: Path,
    *,
    state_code: str = "US-VA",
    output_csv_path: Path = DEFAULT_OUTPUT_CSV,
    provenance_path: Path = DEFAULT_PROVENANCE_PATH,
) -> PilotRun:
    if not archive_path.exists():
        raise FileNotFoundError(f"archive not found: {archive_path}")

    archive_members = _require_archive_members(archive_path)
    archive_size_bytes = archive_path.stat().st_size
    archive_sha256 = _sha256_of_file(archive_path)
    citation = _read_small_member_text(archive_path, CITATION_MEMBER)

    summary: dict[SummaryKey, AggregateMetrics] = {}
    protocol_totals: Counter[str] = Counter()
    county_totals: Counter[str] = Counter()
    rows_scanned = 0
    retained_rows = 0
    min_observation_date: str | None = None
    max_observation_date: str | None = None

    for parts, indices in _iter_rows_from_archive(archive_path):
        rows_scanned += 1
        if parts[indices["STATE CODE"]] != state_code:
            continue
        if parts[indices["ALL SPECIES REPORTED"]] != "1":
            continue

        retained_rows += 1
        observed_on = parts[indices["OBSERVATION DATE"]]
        iso_year, iso_week, _ = date.fromisoformat(observed_on).isocalendar()
        key = SummaryKey(
            state_name=parts[indices["STATE"]],
            state_code=parts[indices["STATE CODE"]],
            county_name=parts[indices["COUNTY"]],
            county_code=parts[indices["COUNTY CODE"]],
            iso_year=iso_year,
            iso_week=iso_week,
            observation_type=parts[indices["OBSERVATION TYPE"]],
            protocol_name=parts[indices["PROTOCOL NAME"]],
            protocol_code=parts[indices["PROTOCOL CODE"]],
        )
        metrics = summary.setdefault(key, AggregateMetrics())
        metrics.complete_checklist_count += 1
        metrics.sampling_event_count += 1
        metrics.update_date_bounds(observed_on)

        observers = _parse_optional_int(parts[indices["NUMBER OBSERVERS"]])
        if observers is not None:
            metrics.number_observers_total += observers

        duration = _parse_optional_float(parts[indices["DURATION MINUTES"]])
        if duration is not None:
            metrics.duration_minutes_count += 1
            metrics.duration_minutes_total += duration

        distance = _parse_optional_float(parts[indices["EFFORT DISTANCE KM"]])
        if distance is not None:
            metrics.effort_distance_km_count += 1
            metrics.effort_distance_km_total += distance

        area = _parse_optional_float(parts[indices["EFFORT AREA HA"]])
        if area is not None:
            metrics.effort_area_ha_count += 1
            metrics.effort_area_ha_total += area

        protocol_totals[key.protocol_name or key.protocol_code] += 1
        county_totals[key.county_code] += 1

        if min_observation_date is None or observed_on < min_observation_date:
            min_observation_date = observed_on
        if max_observation_date is None or observed_on > max_observation_date:
            max_observation_date = observed_on

    rows = _csv_rows_for_summary(summary)
    _write_csv(rows, output_csv_path)
    output_csv_sha256 = _sha256_of_file(output_csv_path)

    run = PilotRun(
        archive_path=archive_path,
        archive_size_bytes=archive_size_bytes,
        archive_sha256=archive_sha256,
        archive_members=archive_members,
        citation=citation,
        rows_scanned=rows_scanned,
        retained_rows=retained_rows,
        output_rows=len(rows),
        output_csv_path=output_csv_path,
        output_csv_sha256=output_csv_sha256,
        min_observation_date=min_observation_date,
        max_observation_date=max_observation_date,
        protocol_totals=protocol_totals,
        county_totals=county_totals,
    )
    _dump_yaml(_build_provenance_payload(run, state_code), provenance_path)
    return run


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, help="Path to ebd_sampling_relMay-2026.tar")
    parser.add_argument("--state-code", default="US-VA")
    parser.add_argument("--output-csv", default=str(DEFAULT_OUTPUT_CSV))
    parser.add_argument("--provenance", default=str(DEFAULT_PROVENANCE_PATH))
    args = parser.parse_args()

    run = run_pilot(
        Path(args.archive),
        state_code=args.state_code,
        output_csv_path=Path(args.output_csv),
        provenance_path=Path(args.provenance),
    )
    print(f"Archive verified: {run.archive_path.name} sha256={run.archive_sha256}")
    print(f"Rows scanned: {run.rows_scanned}")
    print(f"Retained {run.retained_rows} complete checklists for {args.state_code}")
    print(f"Wrote {run.output_rows} aggregate rows to {run.output_csv_path}")


if __name__ == "__main__":
    main()
