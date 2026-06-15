#!/usr/bin/env python3
"""Regulations.gov law_watch enrichment path.

This module mirrors the adjacent Federal Register helper shape while keeping
the live Regulations.gov dependency behind an env var:

  REGULATIONS_GOV_API_KEY

Tests stay fully offline by injecting canned JSON fetchers instead of using the
network path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable, Iterable, Optional

from wildlifestats._pipeline._common.fetch import USER_AGENT
from wildlifestats._pipeline.law_watch import federal_register as fr


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
DEFAULT_CACHE_ROOT = REPO_ROOT / "wildlifestats/_pipeline/law_watch/_cache/regulations_gov"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "wildlifestats/_pipeline/law_watch/_output"

API_BASE = "https://api.regulations.gov/v4"
DOCUMENTS_ENDPOINT = f"{API_BASE}/documents"
DOCKETS_ENDPOINT = f"{API_BASE}/dockets"

DEFAULT_AGENCY_IDS = ("FWS",)
DEFAULT_DOCUMENT_TYPES = ("Proposed Rule", "Rule", "Supporting & Related", "Other")
DEFAULT_PAGE_SIZE = 250
DEFAULT_MAX_PAGES = 5

REQUIRED_SCHEMA_FIELDS = (
    "law_watch_id",
    "source_system",
    "source_native_id",
    "source_url",
    "title",
    "action_type",
    "policy_stage",
    "source_authority",
    "agency_names",
    "government_level",
    "publication_date",
    "comment_open",
    "public_safe_for_display",
    "attribution_badge",
    "attribution_required",
    "license_type",
    "retrieved_at",
)


class RegulationsGovError(RuntimeError):
    """Raised for Regulations.gov fetch or payload problems."""


JsonGetter = Callable[[str], dict]


@dataclass
class EmitSummary:
    record_count: int
    output_path: Path
    summary_path: Path


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    return _now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")


def _today_utc() -> date:
    return _now_utc().date()


def _coerce_date(raw: date | str | None) -> date:
    if isinstance(raw, date):
        return raw
    if not raw:
        return _today_utc()
    return date.fromisoformat(str(raw)[:10])


def _date_only(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    try:
        return date.fromisoformat(str(raw)[:10]).isoformat()
    except ValueError:
        return None


def _parse_datetime_utc(raw: Optional[str]) -> Optional[datetime]:
    if not raw:
        return None
    text = str(raw).strip()
    if not text:
        return None
    try:
        if len(text) == 10:
            return datetime.fromisoformat(f"{text}T00:00:00+00:00")
        if text.endswith("Z"):
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _utc_iso(raw: Optional[str]) -> Optional[str]:
    parsed = _parse_datetime_utc(raw)
    if not parsed:
        return None
    return parsed.strftime("%Y-%m-%dT%H:%M:%SZ")


def _sanitize_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value)


def _json_load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _json_write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _cache_dir(cache_root: Path = DEFAULT_CACHE_ROOT, *, today: Optional[date] = None) -> Path:
    return cache_root / (today or _today_utc()).isoformat()


def _require_api_key() -> str:
    value = os.getenv("REGULATIONS_GOV_API_KEY")
    if not value:
        raise RegulationsGovError(
            "REGULATIONS_GOV_API_KEY is not set. Live Regulations.gov pulls require this env var."
        )
    return value


def _json_get(url: str, timeout: int = 30) -> dict:
    api_key = _require_api_key()
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "X-Api-Key": api_key,
        "Api-Key": api_key,
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            payload = resp.read().decode(charset, errors="replace")
    except Exception as exc:  # noqa: BLE001
        raise RegulationsGovError(f"fetch failed for {url}: {type(exc).__name__}: {exc}") from None
    try:
        return json.loads(payload)
    except ValueError as exc:
        raise RegulationsGovError(f"invalid JSON from {url}: {exc}") from None


def build_documents_search_url(
    *,
    query: str = "",
    since: date | str,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    agency_ids: Iterable[str] = DEFAULT_AGENCY_IDS,
    document_types: Iterable[str] = DEFAULT_DOCUMENT_TYPES,
) -> str:
    since_date = _coerce_date(since).isoformat()
    params: list[tuple[str, str]] = [
        ("page[number]", str(page)),
        ("page[size]", str(page_size)),
        ("sort", "-postedDate"),
        ("filter[postedDate][ge]", since_date),
    ]
    if query:
        params.append(("filter[searchTerm]", query))
    joined_agencies = ",".join(x for x in agency_ids if x)
    if joined_agencies:
        params.append(("filter[agencyId]", joined_agencies))
    joined_types = ",".join(x for x in document_types if x)
    if joined_types:
        params.append(("filter[documentType]", joined_types))
    return f"{DOCUMENTS_ENDPOINT}?{urllib.parse.urlencode(params, doseq=True)}"


def build_document_detail_url(document_id: str) -> str:
    query = urllib.parse.urlencode({"include": "attachments"})
    return f"{DOCUMENTS_ENDPOINT}/{document_id}?{query}"


def build_docket_detail_url(docket_id: str) -> str:
    return f"{DOCKETS_ENDPOINT}/{docket_id}"


def _cached_or_fetch(path: Path, url: str, *, json_get: JsonGetter = _json_get) -> dict:
    if path.exists():
        return _json_load(path)
    payload = json_get(url)
    _json_write(path, payload)
    return payload


def _unwrap_data(payload: Optional[dict]) -> dict:
    if not payload:
        return {}
    if isinstance(payload.get("data"), dict):
        return payload["data"]
    return payload


def fetch_regulations_gov(
    query: str,
    since: date | str,
    *,
    agency_ids: Iterable[str] = DEFAULT_AGENCY_IDS,
    document_types: Iterable[str] = DEFAULT_DOCUMENT_TYPES,
    page_size: int = DEFAULT_PAGE_SIZE,
    max_pages: int = DEFAULT_MAX_PAGES,
    cache_root: Path = DEFAULT_CACHE_ROOT,
    json_get: JsonGetter = _json_get,
    today: Optional[date] = None,
) -> list[dict]:
    """Fetch document + docket bundles from Regulations.gov.

    Re-runs are idempotent on cache hit. The search pages and detail payloads
    are stored separately so emit can rehydrate without another network pass.
    """

    run_day = today or _today_utc()
    cache_dir = _cache_dir(cache_root, today=run_day)
    cache_dir.mkdir(parents=True, exist_ok=True)

    seen_doc_ids: set[str] = set()
    ordered_doc_ids: list[str] = []

    for page in range(1, max_pages + 1):
        search_url = build_documents_search_url(
            query=query,
            since=since,
            page=page,
            page_size=page_size,
            agency_ids=agency_ids,
            document_types=document_types,
        )
        search_path = cache_dir / f"documents-page-{page:03d}.json"
        payload = _cached_or_fetch(search_path, search_url, json_get=json_get)
        rows = payload.get("data") or []
        if not rows:
            break
        for row in rows:
            doc_id = str(row.get("id") or "").strip()
            if not doc_id or doc_id in seen_doc_ids:
                continue
            seen_doc_ids.add(doc_id)
            ordered_doc_ids.append(doc_id)
        if len(rows) < page_size:
            break

    document_details: dict[str, dict] = {}
    docket_ids: list[str] = []
    seen_docket_ids: set[str] = set()
    for doc_id in ordered_doc_ids:
        detail_path = cache_dir / f"documents-detail-{_sanitize_id(doc_id)}.json"
        payload = _cached_or_fetch(detail_path, build_document_detail_url(doc_id), json_get=json_get)
        document = _unwrap_data(payload)
        document_details[doc_id] = document
        docket_id = str((document.get("attributes") or {}).get("docketId") or "").strip()
        if docket_id and docket_id not in seen_docket_ids:
            seen_docket_ids.add(docket_id)
            docket_ids.append(docket_id)

    docket_details: dict[str, dict] = {}
    for docket_id in docket_ids:
        detail_path = cache_dir / f"dockets-detail-{_sanitize_id(docket_id)}.json"
        payload = _cached_or_fetch(detail_path, build_docket_detail_url(docket_id), json_get=json_get)
        docket_details[docket_id] = _unwrap_data(payload)

    bundles: list[dict] = []
    for doc_id in ordered_doc_ids:
        document = document_details[doc_id]
        docket_id = str((document.get("attributes") or {}).get("docketId") or "").strip()
        bundles.append(
            {
                "document": document,
                "docket": docket_details.get(docket_id),
            }
        )
    return bundles


def load_cached_regulations_gov(
    *,
    cache_root: Path = DEFAULT_CACHE_ROOT,
    cache_date: Optional[str] = None,
) -> list[dict]:
    if cache_date:
        cache_dir = cache_root / cache_date
    else:
        dated_dirs = sorted((path for path in cache_root.glob("*") if path.is_dir()), reverse=True)
        if not dated_dirs:
            raise RegulationsGovError(f"no Regulations.gov cache found under {cache_root}")
        cache_dir = dated_dirs[0]

    document_paths = sorted(cache_dir.glob("documents-detail-*.json"))
    if not document_paths:
        raise RegulationsGovError(f"no cached document detail files found under {cache_dir}")

    docket_details: dict[str, dict] = {}
    for path in sorted(cache_dir.glob("dockets-detail-*.json")):
        docket = _unwrap_data(_json_load(path))
        docket_id = str(docket.get("id") or "").strip()
        if docket_id:
            docket_details[docket_id] = docket

    bundles: list[dict] = []
    for path in document_paths:
        document = _unwrap_data(_json_load(path))
        docket_id = str((document.get("attributes") or {}).get("docketId") or "").strip()
        bundles.append({"document": document, "docket": docket_details.get(docket_id)})
    return bundles


def _preferred_file_url(file_formats: list[dict]) -> Optional[str]:
    for fmt in file_formats:
        if str(fmt.get("format") or "").lower() == "pdf" and fmt.get("fileUrl"):
            return str(fmt["fileUrl"])
    for fmt in file_formats:
        if fmt.get("fileUrl"):
            return str(fmt["fileUrl"])
    return None


def _action_type(document_type: Optional[str]) -> str:
    doc_type = str(document_type or "").strip().lower()
    if doc_type == "proposed rule":
        return "proposed_rule"
    if doc_type == "rule":
        return "final_rule"
    if doc_type == "supporting & related":
        return "supporting_document"
    return "policy_update"


def _comment_open(attributes: dict) -> bool:
    return bool(attributes.get("openForComment") or attributes.get("withinCommentPeriod"))


def _comment_window_open(comment_end_date: Optional[str], *, now: Optional[datetime] = None) -> bool:
    if not comment_end_date:
        return False
    text = str(comment_end_date).strip()
    current = now or _now_utc()
    if len(text) == 10:
        try:
            return date.fromisoformat(text) >= current.date()
        except ValueError:
            return False
    parsed = _parse_datetime_utc(text)
    return bool(parsed and parsed >= current)


def _policy_stage(attributes: dict) -> str:
    if attributes.get("withdrawn"):
        return "historical_reference"
    doc_type = str(attributes.get("documentType") or "").strip().lower()
    comment_open = _comment_open(attributes)
    if doc_type == "proposed rule":
        return "proposal_open" if comment_open else "proposal_closed"
    if doc_type == "rule":
        return "finalized"
    if doc_type == "supporting & related" and comment_open:
        return "docket_open"
    return "under_review"


def _status_label(attributes: dict, *, today: Optional[date] = None) -> str:
    if attributes.get("withdrawn"):
        return "historical_reference"
    if _comment_open(attributes):
        return "active_comment_period"
    if _policy_stage(attributes) == "proposal_closed":
        return "comment_closed"
    pub_date = _date_only(attributes.get("postedDate"))
    if pub_date:
        days_old = (today or _today_utc()) - date.fromisoformat(pub_date)
        if days_old.days <= 30:
            return "newly_posted"
    return "historical_reference"


def _status_stage_alias(policy_stage: str) -> str:
    return {
        "proposal_open": "open_for_comment",
        "proposal_closed": "comment_closed",
        "finalized": "final",
        "docket_open": "open_for_comment",
        "historical_reference": "historical_reference",
        "under_review": "unknown",
    }.get(policy_stage, "unknown")


def _related_ids(attributes: dict, docket_attributes: dict) -> list[str]:
    values: list[str] = []
    for raw in (attributes.get("originalDocumentId"), docket_attributes.get("rin")):
        if raw and raw not in values:
            values.append(str(raw))
    return values


def _notes(attributes: dict, *, agency_id: str, comment_url: Optional[str]) -> Optional[str]:
    notes = [f"agency label remains agencyId value: {agency_id}"] if agency_id else []
    if attributes.get("withdrawn"):
        notes.append("document is withdrawn in Regulations.gov")
    if not comment_url:
        notes.append("comment URL is not explicit in Regulations.gov payload")
    return "; ".join(notes) if notes else None


def _required_field_gaps(record: dict) -> list[str]:
    gaps: list[str] = []
    for field in REQUIRED_SCHEMA_FIELDS:
        value = record.get(field)
        if value is None:
            gaps.append(field)
        elif isinstance(value, str) and not value.strip():
            gaps.append(field)
        elif isinstance(value, list) and not value:
            gaps.append(field)
    return gaps


def normalize_regulations_gov(
    raw: dict,
    *,
    fetched_at: Optional[str] = None,
    today: Optional[date] = None,
) -> dict:
    document = _unwrap_data(raw.get("document") or raw)
    docket = _unwrap_data(raw.get("docket"))
    attributes = document.get("attributes") or {}
    docket_attributes = docket.get("attributes") or {}

    now_iso = fetched_at or _now_iso()
    doc_id = str(document.get("id") or "").strip()
    docket_id = str(attributes.get("docketId") or "").strip() or None
    agency_id = str(attributes.get("agencyId") or "").strip()
    publication_date = _date_only(attributes.get("postedDate"))
    comment_deadline = attributes.get("commentEndDate")
    policy_stage = _policy_stage(attributes)
    comment_url = None

    record = {
        "law_watch_id": f"lawwatch.regulations_gov_api.{doc_id}",
        "source_system": "regulations_gov_api",
        "source_id": "regulations_gov_api",
        "source_native_id": doc_id,
        "source_record_id": doc_id,
        "thread_key": docket_id,
        "source_url": f"https://www.regulations.gov/document/{doc_id}",
        "canonical_url": f"https://www.regulations.gov/document/{doc_id}",
        "source_document_url": _preferred_file_url(attributes.get("fileFormats") or []),
        "retrieved_at": now_iso,
        "last_seen_at": now_iso,
        "fetched_at": now_iso,
        "title": attributes.get("title"),
        "short_summary": attributes.get("docAbstract") or docket_attributes.get("dkAbstract"),
        "summary": attributes.get("docAbstract") or docket_attributes.get("dkAbstract"),
        "action_type": _action_type(attributes.get("documentType")),
        "policy_stage": policy_stage,
        "status_stage": _status_stage_alias(policy_stage),
        "source_authority": "Regulations.gov",
        "agency_names": [agency_id] if agency_id else [],
        "government_level": "federal",
        "jurisdiction_level": "federal",
        "jurisdiction_scope": "national_us",
        "topic_tags": fr.infer_topic_tags(
            str(attributes.get("title") or ""),
            attributes.get("docAbstract") or docket_attributes.get("dkAbstract"),
            attributes.get("documentType"),
        ),
        "taxa_tags": fr.infer_taxa_tags(
            str(attributes.get("title") or ""),
            attributes.get("docAbstract") or docket_attributes.get("dkAbstract"),
        ),
        "publication_date": publication_date,
        "published_at": attributes.get("postedDate"),
        "effective_date": attributes.get("effectiveDate"),
        "comment_deadline": comment_deadline,
        "comment_open": _comment_open(attributes),
        "comment_window_open": _comment_window_open(comment_deadline),
        "comment_window_end_utc": _utc_iso(comment_deadline),
        "status_label": _status_label(attributes, today=today),
        "docket_id": docket_id,
        "document_number": attributes.get("frDocNum"),
        "citation": attributes.get("frVolNum") or attributes.get("sourceCitation"),
        "related_ids": _related_ids(attributes, docket_attributes),
        "comment_url": comment_url,
        "public_safe_for_display": True,
        "attribution_badge": "Data via Regulations.gov",
        "attribution_required": True,
        "license_type": "public_domain",
        "relevance_status": "in_scope",
        "relevance_reason": f"agency allowlist: {agency_id}" if agency_id else "agency allowlist",
        "notes": _notes(attributes, agency_id=agency_id, comment_url=comment_url),
    }
    record["field_gaps"] = _required_field_gaps(record)
    record["content_hash"] = hashlib.sha256(
        json.dumps({"document": document, "docket": docket}, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return record


def _sorted_records(records: list[dict]) -> list[dict]:
    return sorted(
        records,
        key=lambda rec: (
            rec.get("comment_window_open") is not True,
            rec.get("comment_deadline") or "9999-12-31T23:59:59Z",
            rec.get("publication_date") or "0000-00-00",
            rec.get("source_native_id") or "",
        ),
    )


def emit_regulations_gov_records(
    *,
    raw_records: Optional[list[dict]] = None,
    cache_root: Path = DEFAULT_CACHE_ROOT,
    cache_date: Optional[str] = None,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    fetched_at: Optional[str] = None,
    today: Optional[date] = None,
) -> int:
    bundles = raw_records if raw_records is not None else load_cached_regulations_gov(
        cache_root=cache_root,
        cache_date=cache_date,
    )
    seen: set[str] = set()
    records: list[dict] = []
    for bundle in bundles:
        record = normalize_regulations_gov(bundle, fetched_at=fetched_at, today=today)
        if record["law_watch_id"] in seen:
            continue
        seen.add(record["law_watch_id"])
        records.append(record)

    records = _sorted_records(records)
    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "regulations_gov.jsonl"
    summary_path = output_root / "regulations_gov-summary.json"

    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "source_system": "regulations_gov_api",
        "generated_at": fetched_at or _now_iso(),
        "record_count": len(records),
        "open_comment_windows": sum(1 for rec in records if rec.get("comment_window_open")),
        "unique_dockets": len({rec.get("docket_id") for rec in records if rec.get("docket_id")}),
        "field_gaps": [
            {"law_watch_id": rec["law_watch_id"], "fields": rec["field_gaps"]}
            for rec in records
            if rec.get("field_gaps")
        ],
    }
    _json_write(summary_path, summary)
    return len(records)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", default="")
    ap.add_argument("--since", default=_today_utc().replace(day=1).isoformat())
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args()

    bundles = fetch_regulations_gov(args.query, args.since)
    print(f"cached {len(bundles)} Regulations.gov document bundles")
    if args.emit:
        count = emit_regulations_gov_records(raw_records=bundles)
        print(f"wrote {count} normalized records")


if __name__ == "__main__":
    main()
