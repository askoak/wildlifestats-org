"""Cross-source bridge helpers for Federal Register and Regulations.gov."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Iterable, Optional


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "wildlifestats/_pipeline/law_watch/_output"
DEFAULT_ENRICHED_PATH = DEFAULT_OUTPUT_ROOT / "law_watch_enriched.jsonl"
DEFAULT_ENRICHED_SUMMARY_PATH = DEFAULT_OUTPUT_ROOT / "law_watch_enriched-summary.json"

REGULATIONS_ENRICHMENT_FIELDS = (
    "regulations_gov_law_watch_id",
    "regulations_gov_source_system",
    "regulations_gov_source_native_id",
    "regulations_gov_source_url",
    "regulations_gov_source_document_url",
    "regulations_gov_title",
    "regulations_gov_short_summary",
    "regulations_gov_policy_stage",
    "regulations_gov_status_label",
    "regulations_gov_publication_date",
    "regulations_gov_comment_deadline",
    "regulations_gov_comment_open",
    "regulations_gov_comment_window_open",
    "regulations_gov_comment_window_end_utc",
    "regulations_gov_docket_id",
    "regulations_gov_document_number",
    "regulations_gov_related_ids",
    "regulations_gov_comment_url",
)


def _date_key(raw: Optional[str]) -> tuple[int, str]:
    if not raw:
        return (0, "")
    return (1, str(raw)[:10])


def load_records(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix == ".jsonl":
        rows: list[dict] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("records"), list):
        return list(payload["records"])
    if isinstance(payload, list):
        return list(payload)
    raise ValueError(f"unsupported record payload at {path}")


def write_jsonl(records: Iterable[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def dedupe_regulations_records(records: Iterable[dict]) -> list[dict]:
    seen: set[str] = set()
    deduped: list[dict] = []
    for record in records:
        key = str(record.get("law_watch_id") or record.get("source_native_id") or "")
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(record)
    return deduped


def _match_reasons(fr_record: dict, rg_record: dict) -> list[str]:
    reasons: list[str] = []
    fr_doc = str(fr_record.get("document_number") or "").strip()
    rg_doc = str(rg_record.get("document_number") or "").strip()
    if fr_doc and rg_doc and fr_doc == rg_doc:
        reasons.append("document_number")
    fr_docket = str(fr_record.get("docket_id") or "").strip()
    rg_docket = str(rg_record.get("docket_id") or "").strip()
    if fr_docket and rg_docket and fr_docket == rg_docket:
        reasons.append("docket_id")
    return reasons


def _candidate_rank(rg_record: dict, reasons: list[str]) -> tuple[int, int, int, tuple[int, str], str]:
    return (
        0 if "document_number" in reasons else 1,
        0 if "docket_id" in reasons else 1,
        0 if rg_record.get("comment_window_open") or rg_record.get("comment_open") else 1,
        _date_key(rg_record.get("publication_date")),
        str(rg_record.get("source_native_id") or ""),
    )


def _empty_enrichment() -> dict:
    return {field: None for field in REGULATIONS_ENRICHMENT_FIELDS}


def _enrichment_payload(fr_record: dict, rg_record: Optional[dict], reasons: list[str]) -> tuple[dict, dict]:
    enrichment = _empty_enrichment()
    bridge_provenance = {
        "matched": bool(rg_record),
        "match_keys": list(reasons),
        "federal_register_law_watch_id": fr_record.get("law_watch_id"),
        "federal_register_source_native_id": fr_record.get("source_native_id"),
        "regulations_gov_law_watch_id": None,
        "regulations_gov_source_native_id": None,
        "comment_url_source": None,
    }
    if not rg_record:
        return enrichment, bridge_provenance

    comment_url = rg_record.get("comment_url") or fr_record.get("comment_url")
    comment_url_source = (
        "regulations_gov_api" if rg_record.get("comment_url") else "federal_register_api" if fr_record.get("comment_url") else None
    )
    enrichment.update(
        {
            "regulations_gov_law_watch_id": rg_record.get("law_watch_id"),
            "regulations_gov_source_system": rg_record.get("source_system"),
            "regulations_gov_source_native_id": rg_record.get("source_native_id"),
            "regulations_gov_source_url": rg_record.get("source_url"),
            "regulations_gov_source_document_url": rg_record.get("source_document_url"),
            "regulations_gov_title": rg_record.get("title"),
            "regulations_gov_short_summary": rg_record.get("short_summary"),
            "regulations_gov_policy_stage": rg_record.get("policy_stage"),
            "regulations_gov_status_label": rg_record.get("status_label"),
            "regulations_gov_publication_date": rg_record.get("publication_date"),
            "regulations_gov_comment_deadline": rg_record.get("comment_deadline"),
            "regulations_gov_comment_open": rg_record.get("comment_open"),
            "regulations_gov_comment_window_open": rg_record.get("comment_window_open"),
            "regulations_gov_comment_window_end_utc": rg_record.get("comment_window_end_utc"),
            "regulations_gov_docket_id": rg_record.get("docket_id"),
            "regulations_gov_document_number": rg_record.get("document_number"),
            "regulations_gov_related_ids": rg_record.get("related_ids"),
            "regulations_gov_comment_url": comment_url,
        }
    )
    bridge_provenance.update(
        {
            "regulations_gov_law_watch_id": rg_record.get("law_watch_id"),
            "regulations_gov_source_native_id": rg_record.get("source_native_id"),
            "comment_url_source": comment_url_source,
        }
    )
    return enrichment, bridge_provenance


def cross_source_bridge(fr_records: Iterable[dict], rg_records: Iterable[dict]) -> list[dict]:
    fr_rows = list(fr_records)
    rg_rows = dedupe_regulations_records(rg_records)
    enriched: list[dict] = []

    for fr_record in fr_rows:
        candidates: list[tuple[dict, list[str]]] = []
        for rg_record in rg_rows:
            reasons = _match_reasons(fr_record, rg_record)
            if reasons:
                candidates.append((rg_record, reasons))

        best_rg: Optional[dict] = None
        reasons: list[str] = []
        if candidates:
            best_rg, reasons = min(
                candidates,
                key=lambda item: _candidate_rank(item[0], item[1]),
            )

        merged = dict(fr_record)
        enrichment, provenance = _enrichment_payload(fr_record, best_rg, reasons)
        merged.update(enrichment)
        merged["bridge_provenance"] = provenance
        enriched.append(merged)
    return enriched


def emit_enriched_records(
    *,
    fr_records: Optional[list[dict]] = None,
    rg_records: Optional[list[dict]] = None,
    fr_path: Optional[Path] = None,
    rg_path: Optional[Path] = None,
    output_path: Path = DEFAULT_ENRICHED_PATH,
    summary_path: Path = DEFAULT_ENRICHED_SUMMARY_PATH,
) -> int:
    fr_rows = fr_records if fr_records is not None else load_records(fr_path or DEFAULT_OUTPUT_ROOT / "federal_register.jsonl")
    rg_rows = rg_records if rg_records is not None else load_records(rg_path or DEFAULT_OUTPUT_ROOT / "regulations_gov.jsonl")
    enriched = cross_source_bridge(fr_rows, rg_rows)
    write_jsonl(enriched, output_path)

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    matched = sum(1 for record in enriched if record.get("bridge_provenance", {}).get("matched"))
    summary = {
        "generated_at": date.today().isoformat(),
        "federal_register_records": len(fr_rows),
        "regulations_gov_records": len(dedupe_regulations_records(rg_rows)),
        "enriched_records": len(enriched),
        "matched_records": matched,
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(enriched)
