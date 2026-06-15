#!/usr/bin/env python3
"""Federal-first `law_watch` normalization path for Federal Register data.

This module intentionally follows the repo's existing pattern:

- public-safe local JSON is the first-class output
- live source fetches happen against the official API
- tests stay deterministic and offline through injectable HTTP helpers

The current docs bundle has a mild schema mismatch between the first
`law_watch` normalized-schema note and the later page-contract note. To avoid
stalling implementation on another planning round, the normalized record below
keeps the primary schema fields and also emits a small compatibility alias set
used by the page contract (`source_id`, `jurisdiction_level`, `status_stage`,
and `relevance_*`).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Iterable, Optional

from wildlifestats._pipeline._common.fetch import USER_AGENT


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
DEFAULT_BUILD_ROOT = REPO_ROOT / "wildlifestats/_pipeline/_work/law_watch/federal_register"

SEARCH_ENDPOINT = "https://www.federalregister.gov/api/v1/documents.json"
DETAIL_ENDPOINT = "https://www.federalregister.gov/api/v1/documents/{document_number}.json"

DEFAULT_AGENCY_SLUGS = ("fish-and-wildlife-service",)
DEFAULT_TYPE_CODES = ("PRORULE", "RULE", "NOTICE")
DEFAULT_DAYS_BACK = 90
DEFAULT_PER_PAGE = 20
DEFAULT_MAX_PAGES = 5

TOPIC_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("endangered_species", ("endangered", "threatened species", "esa", "section 4(d)")),
    ("migratory_birds", ("migratory bird", "migratory birds", "bird treaty")),
    ("habitat", ("habitat", "critical habitat", "habitat conservation")),
    ("wildlife_rehabilitation", ("wildlife rehabilitation", "rehabilitation", "rehabber")),
    ("disease_surveillance", ("avian influenza", "hpai", "disease surveillance", "wildlife disease")),
    ("marine_mammals", ("marine mammal", "marine mammals", "sea lion", "whale", "dolphin")),
)

TAXA_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("birds", ("bird", "birds", "waterfowl", "raptor", "eagle", "owl")),
    ("snakes", ("snake", "snakes", "hognose")),
    ("bats", ("bat", "bats")),
    ("wolves", ("wolf", "wolves")),
    ("marine_mammals", ("marine mammal", "whale", "dolphin", "porpoise", "sea lion", "seal")),
    ("sea_turtles", ("sea turtle", "sea turtles", "turtle", "turtles")),
)


class FederalRegisterError(RuntimeError):
    """Raised for Federal Register fetch or payload problems."""


JsonGetter = Callable[[str], dict]


@dataclass
class PullSummary:
    search_hits: int
    detail_records: int
    snapshot_path: Path
    latest_path: Path


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today_utc() -> date:
    return datetime.now(timezone.utc).date()


def _parse_iso_date(raw: Optional[str]) -> Optional[date]:
    if not raw:
        return None
    try:
        return date.fromisoformat(str(raw)[:10])
    except ValueError:
        return None


def _json_get(url: str, timeout: int = 30) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            payload = resp.read().decode(charset, errors="replace")
    except Exception as exc:  # noqa: BLE001
        raise FederalRegisterError(f"fetch failed for {url}: {type(exc).__name__}: {exc}") from None
    try:
        return json.loads(payload)
    except ValueError as exc:
        raise FederalRegisterError(f"invalid JSON from {url}: {exc}") from None


def build_search_url(
    *,
    agency_slugs: Iterable[str],
    type_codes: Iterable[str] = DEFAULT_TYPE_CODES,
    published_on_or_after: str,
    published_on_or_before: Optional[str] = None,
    page: int = 1,
    per_page: int = DEFAULT_PER_PAGE,
) -> str:
    query: list[tuple[str, str]] = [
        ("per_page", str(per_page)),
        ("page", str(page)),
        ("order", "newest"),
        ("conditions[publication_date][gte]", published_on_or_after),
    ]
    if published_on_or_before:
        query.append(("conditions[publication_date][lte]", published_on_or_before))
    for slug in agency_slugs:
        query.append(("conditions[agencies][]", slug))
    for code in type_codes:
        query.append(("conditions[type][]", code))
    return f"{SEARCH_ENDPOINT}?{urllib.parse.urlencode(query, doseq=True)}"


def search_documents(
    *,
    agency_slugs: Iterable[str] = DEFAULT_AGENCY_SLUGS,
    type_codes: Iterable[str] = DEFAULT_TYPE_CODES,
    published_on_or_after: str,
    published_on_or_before: Optional[str] = None,
    page: int = 1,
    per_page: int = DEFAULT_PER_PAGE,
    json_get: JsonGetter = _json_get,
) -> dict:
    url = build_search_url(
        agency_slugs=agency_slugs,
        type_codes=type_codes,
        published_on_or_after=published_on_or_after,
        published_on_or_before=published_on_or_before,
        page=page,
        per_page=per_page,
    )
    return json_get(url)


def fetch_document_detail(
    document_number: str,
    *,
    json_get: JsonGetter = _json_get,
) -> dict:
    return json_get(DETAIL_ENDPOINT.format(document_number=document_number))


def infer_topic_tags(title: str, abstract: Optional[str], action: Optional[str]) -> list[str]:
    text = " ".join(x for x in (title, abstract or "", action or "") if x).lower()
    tags: list[str] = []
    for tag, needles in TOPIC_RULES:
        if any(needle in text for needle in needles):
            tags.append(tag)
    return tags


def infer_taxa_tags(title: str, abstract: Optional[str]) -> list[str]:
    text = " ".join(x for x in (title, abstract or "") if x).lower()
    tags: list[str] = []
    for tag, needles in TAXA_RULES:
        if any(needle in text for needle in needles):
            tags.append(tag)
    return tags


def _stage_from_type(detail: dict, *, today: Optional[date] = None) -> str:
    doc_type = str(detail.get("type") or "").strip().lower()
    deadline = _parse_iso_date(detail.get("comments_close_on"))
    now = today or _today_utc()
    if doc_type == "proposed rule":
        if deadline and deadline >= now:
            return "proposal_open"
        return "proposal_closed"
    if doc_type == "rule":
        return "finalized"
    if doc_type == "notice":
        return "notice_only"
    return "under_review"


def _status_label(detail: dict, *, today: Optional[date] = None) -> str:
    now = today or _today_utc()
    stage = _stage_from_type(detail, today=now)
    deadline = _parse_iso_date(detail.get("comments_close_on"))
    pub = _parse_iso_date(detail.get("publication_date"))
    effective = _parse_iso_date(detail.get("effective_on"))
    if deadline and deadline >= now:
        return "active_comment_period"
    if effective and effective <= now:
        return "effective_now"
    if pub and (now - pub).days <= 30:
        return "newly_posted"
    if stage == "proposal_closed":
        return "comment_closed"
    return "historical_reference"


def _action_type(detail: dict) -> str:
    doc_type = str(detail.get("type") or "").strip().lower()
    if doc_type == "proposed rule":
        return "proposed_rule"
    if doc_type == "rule":
        return "final_rule"
    if doc_type == "notice":
        return "notice"
    return "policy_update"


def _status_stage_alias(policy_stage: str) -> str:
    return {
        "proposal_open": "open_for_comment",
        "proposal_closed": "comment_closed",
        "finalized": "final",
        "notice_only": "notice",
        "under_review": "unknown",
    }.get(policy_stage, "unknown")


def _agency_names(detail: dict) -> list[str]:
    names: list[str] = []
    for agency in detail.get("agencies") or []:
        name = str(agency.get("name") or agency.get("raw_name") or "").strip()
        if name and name not in names:
            names.append(name)
    return names


def _agency_slugs(detail: dict) -> list[str]:
    slugs: list[str] = []
    for agency in detail.get("agencies") or []:
        slug = str(agency.get("slug") or "").strip()
        if slug and slug not in slugs:
            slugs.append(slug)
    return slugs


def _thread_key(detail: dict) -> Optional[str]:
    for key in detail.get("regulation_id_numbers") or []:
        if key:
            return str(key)
    regs_info = detail.get("regulations_dot_gov_info") or {}
    if regs_info.get("docket_id"):
        return str(regs_info["docket_id"])
    for key in detail.get("docket_ids") or []:
        if key:
            return str(key)
    return None


def _docket_id(detail: dict) -> Optional[str]:
    regs_info = detail.get("regulations_dot_gov_info") or {}
    if regs_info.get("docket_id"):
        return str(regs_info["docket_id"])
    dockets = detail.get("dockets") or []
    if dockets and dockets[0].get("id"):
        return str(dockets[0]["id"])
    docket_ids = detail.get("docket_ids") or []
    return str(docket_ids[0]) if docket_ids else None


def _comment_url(detail: dict) -> Optional[str]:
    if detail.get("comment_url"):
        return str(detail["comment_url"])
    for docket in detail.get("dockets") or []:
        for doc in docket.get("documents") or []:
            if doc.get("comment_url"):
                return str(doc["comment_url"])
    return None


def _related_ids(detail: dict) -> list[str]:
    values: list[str] = []
    for key in detail.get("regulation_id_numbers") or []:
        if key and key not in values:
            values.append(str(key))
    for key in detail.get("docket_ids") or []:
        if key and key not in values:
            values.append(str(key))
    regs_info = detail.get("regulations_dot_gov_info") or {}
    if regs_info.get("document_id"):
        doc_id = str(regs_info["document_id"])
        if doc_id not in values:
            values.append(doc_id)
    return values


def _relevance_reason(detail: dict) -> str:
    slugs = _agency_slugs(detail)
    if slugs:
        return f"agency allowlist: {', '.join(slugs)}"
    return "agency allowlist"


def _notes(detail: dict) -> Optional[str]:
    notes: list[str] = []
    if detail.get("correction_of"):
        notes.append("correction_of another Federal Register document")
    if "reopening" in str(detail.get("action") or "").lower():
        notes.append("reopens comment period")
    if not _comment_url(detail):
        notes.append("no direct comment URL in Federal Register payload")
    return "; ".join(notes) if notes else None


def normalize_record(
    detail: dict,
    *,
    fetched_at: Optional[str] = None,
    today: Optional[date] = None,
) -> dict:
    now_iso = fetched_at or _now_iso()
    title = str(detail.get("title") or "").strip()
    abstract = detail.get("abstract")
    policy_stage = _stage_from_type(detail, today=today)
    comment_deadline = detail.get("comments_close_on")
    comment_open = bool(comment_deadline and (_parse_iso_date(comment_deadline) or date.min) >= (today or _today_utc()))
    record = {
        "law_watch_id": f"lawwatch.federal_register_api.{detail.get('document_number')}",
        "source_system": "federal_register_api",
        "source_id": "federal_register_api",
        "source_native_id": detail.get("document_number"),
        "source_record_id": detail.get("document_number"),
        "thread_key": _thread_key(detail),
        "source_url": detail.get("html_url"),
        "canonical_url": detail.get("html_url"),
        "source_document_url": detail.get("pdf_url"),
        "retrieved_at": now_iso,
        "last_seen_at": now_iso,
        "fetched_at": now_iso,
        "title": title,
        "short_summary": abstract,
        "summary": abstract,
        "action_type": _action_type(detail),
        "policy_stage": policy_stage,
        "status_stage": _status_stage_alias(policy_stage),
        "source_authority": "Federal Register",
        "agency_names": _agency_names(detail),
        "agency_slugs": _agency_slugs(detail),
        "government_level": "federal",
        "jurisdiction_level": "federal",
        "jurisdiction_scope": "national_us",
        "topic_tags": infer_topic_tags(title, abstract, detail.get("action")),
        "taxa_tags": infer_taxa_tags(title, abstract),
        "publication_date": detail.get("publication_date"),
        "published_at": detail.get("publication_date"),
        "effective_date": detail.get("effective_on"),
        "comment_deadline": comment_deadline,
        "comment_open": comment_open,
        "status_label": _status_label(detail, today=today),
        "docket_id": _docket_id(detail),
        "document_number": detail.get("document_number"),
        "citation": detail.get("citation"),
        "related_ids": _related_ids(detail),
        "comment_url": _comment_url(detail),
        "public_safe_for_display": True,
        "attribution_badge": "Data via the Federal Register",
        "attribution_required": True,
        "license_type": "public_domain",
        "relevance_status": "in_scope",
        "relevance_reason": _relevance_reason(detail),
        "notes": _notes(detail),
    }
    record["content_hash"] = hashlib.sha256(
        json.dumps(detail, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return record


def build_snapshot(
    *,
    records: list[dict],
    agency_slugs: Iterable[str],
    published_on_or_after: str,
    published_on_or_before: str,
    generated_at: Optional[str] = None,
) -> dict:
    ordered = sorted(
        records,
        key=lambda rec: (
            rec.get("comment_open") is not True,
            rec.get("comment_deadline") or "9999-12-31",
            -((_parse_iso_date(rec.get("publication_date")) or date.min).toordinal()),
        ),
    )
    return {
        "source_system": "federal_register_api",
        "generated_at": generated_at or _now_iso(),
        "query": {
            "agency_slugs": list(agency_slugs),
            "published_on_or_after": published_on_or_after,
            "published_on_or_before": published_on_or_before,
            "type_codes": list(DEFAULT_TYPE_CODES),
        },
        "record_count": len(records),
        "records": ordered,
    }


def write_snapshot(snapshot: dict, *, build_root: Path = DEFAULT_BUILD_ROOT) -> tuple[Path, Path]:
    build_root.mkdir(parents=True, exist_ok=True)
    q = snapshot.get("query") or {}
    start = q.get("published_on_or_after", "unknown")
    end = q.get("published_on_or_before", "unknown")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snapshot_path = build_root / f"federal-register-{start}-to-{end}-{stamp}.json"
    latest_path = build_root / "latest.json"
    payload = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
    snapshot_path.write_text(payload, encoding="utf-8")
    latest_path.write_text(payload, encoding="utf-8")
    return snapshot_path, latest_path


def pull_federal_register(
    *,
    days_back: int = DEFAULT_DAYS_BACK,
    agency_slugs: Iterable[str] = DEFAULT_AGENCY_SLUGS,
    per_page: int = DEFAULT_PER_PAGE,
    max_pages: int = DEFAULT_MAX_PAGES,
    build_root: Path = DEFAULT_BUILD_ROOT,
    json_get: JsonGetter = _json_get,
    today: Optional[date] = None,
) -> PullSummary:
    now = today or _today_utc()
    start = (now - timedelta(days=days_back)).isoformat()
    end = now.isoformat()

    results: list[dict] = []
    seen: set[str] = set()
    search_hits = 0
    fetched_at = _now_iso()
    for page in range(1, max_pages + 1):
        payload = search_documents(
            agency_slugs=agency_slugs,
            published_on_or_after=start,
            published_on_or_before=end,
            page=page,
            per_page=per_page,
            json_get=json_get,
        )
        page_results = payload.get("results") or []
        if not page_results:
            break
        search_hits += len(page_results)
        for row in page_results:
            docnum = str(row.get("document_number") or "").strip()
            if not docnum or docnum in seen:
                continue
            seen.add(docnum)
            detail = fetch_document_detail(docnum, json_get=json_get)
            results.append(normalize_record(detail, fetched_at=fetched_at, today=now))
        if len(page_results) < per_page:
            break

    snapshot = build_snapshot(
        records=results,
        agency_slugs=agency_slugs,
        published_on_or_after=start,
        published_on_or_before=end,
        generated_at=fetched_at,
    )
    snapshot_path, latest_path = write_snapshot(snapshot, build_root=build_root)
    return PullSummary(
        search_hits=search_hits,
        detail_records=len(results),
        snapshot_path=snapshot_path,
        latest_path=latest_path,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days-back", type=int, default=DEFAULT_DAYS_BACK)
    ap.add_argument("--agency-slug", action="append", default=list(DEFAULT_AGENCY_SLUGS))
    ap.add_argument("--per-page", type=int, default=DEFAULT_PER_PAGE)
    ap.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES)
    ap.add_argument("--build-root", default=str(DEFAULT_BUILD_ROOT))
    args = ap.parse_args()

    summary = pull_federal_register(
        days_back=args.days_back,
        agency_slugs=args.agency_slug,
        per_page=args.per_page,
        max_pages=args.max_pages,
        build_root=Path(args.build_root),
    )
    print(
        f"search hits: {summary.search_hits} | "
        f"records: {summary.detail_records} | "
        f"snapshot: {summary.snapshot_path}"
    )


if __name__ == "__main__":
    main()
