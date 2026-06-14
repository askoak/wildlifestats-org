#!/usr/bin/env python3
"""Bucket 02 — firm-profile website harvester.

HTML fetches route through `_common.fetch`, readability-style extraction runs
locally, the structured dossier is emitted to local JSON, and the Supabase
write is a SECOND, non-fatal leg. That keeps the fixture/test path offline and
the credentialed path out of the repo.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

from wildlifestats._pipeline._common import claude_client, fetch, supabase_client
from wildlifestats._pipeline.firm_profile import readability


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
DEFAULT_ROSTER_PATH = REPO_ROOT / "wildlifestats/_pipeline/sources/rehab-centers/centers.yaml"
DEFAULT_BUILD_ROOT = REPO_ROOT / "wildlifestats/_build/centers"

TARGET_PAGE_FIELDS = (
    ("primary_url", "primary_url"),
    ("about_url", "about_url"),
    ("contact_url", "contact_url"),
    ("wildlife_help_url", "wildlife_help_url"),
    ("news_or_blog_url", "news_or_blog_url"),
    ("annual_reports_url", "annual_reports_url"),
)

SKIP_URL_VALUES = {"", "unknown", "none", "null", "n/a"}

PHONE_RE = re.compile(
    r"(?:\+?1[-.\s]*)?(?:\(?\d{3}\)?[-.\s]*)\d{3}[-.\s]*\d{4}(?:\s*(?:ext\.?|x)\s*\d+)?"
)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
MISSION_RE = re.compile(
    r"(?i)(?:mission(?: statement)?|our mission)\s*[:\-]\s*(?P<body>.+)$"
)
LEADERSHIP_PATTERNS = (
    re.compile(
        r"(?P<title>Executive Director|Chief Executive Officer|CEO|Medical Director|Hospital Director|Founder|President|Director of Rehabilitation)\s*[:\-]\s*(?P<name>[A-Z][A-Za-z .'\-]{2,})"
    ),
    re.compile(
        r"(?P<name>[A-Z][A-Za-z .'\-]{2,}),\s*(?P<title>Executive Director|Chief Executive Officer|CEO|Medical Director|Hospital Director|Founder|President|Director of Rehabilitation)"
    ),
)
SERVICE_KEYWORDS = (
    "rehabilitation",
    "rescue",
    "education",
    "outreach",
    "hotline",
    "transport",
    "field response",
    "wildlife help",
    "intake",
)
ACCREDITATION_KEYWORDS = (
    "aza",
    "iwrc",
    "nwra",
    "licensed",
    "license",
    "permit",
    "accredited",
    "501(c)(3)",
    "federally permitted",
)
PARTNERSHIP_KEYWORDS = ("partner", "partnership", "working with", "in collaboration with")

SYSTEM_PROMPT = """
You extract structured public-website dossiers for wildlife rehabilitation organizations.

Rules:
- Quote identity statements verbatim. Do not paraphrase mission language.
- Cite the exact supporting source URL on every extracted claim.
- Leave a field null or an array empty when the website text does not say it.
- Prefer public-facing center pages over boilerplate navigation.
- Return only the schema requested by the tool.
""".strip()

OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "mission_statement",
        "mission_statement_source_url",
        "leadership",
        "services_offered",
        "accreditations",
        "partnerships",
        "contact_info",
        "sources",
    ],
    "properties": {
        "mission_statement": {"type": ["string", "null"]},
        "mission_statement_source_url": {"type": ["string", "null"]},
        "leadership": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["name", "title", "source_url"],
                "properties": {
                    "name": {"type": "string"},
                    "title": {"type": "string"},
                    "source_url": {"type": "string"},
                },
            },
        },
        "services_offered": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["label", "source_url"],
                "properties": {
                    "label": {"type": "string"},
                    "source_url": {"type": "string"},
                },
            },
        },
        "accreditations": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["label", "source_url"],
                "properties": {
                    "label": {"type": "string"},
                    "source_url": {"type": "string"},
                },
            },
        },
        "partnerships": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["name", "source_url"],
                "properties": {
                    "name": {"type": "string"},
                    "source_url": {"type": "string"},
                },
            },
        },
        "contact_info": {
            "type": "object",
            "additionalProperties": False,
            "required": ["phone", "email", "intake_hours", "intake_address", "source_url"],
            "properties": {
                "phone": {"type": ["string", "null"]},
                "email": {"type": ["string", "null"]},
                "intake_hours": {"type": ["string", "null"]},
                "intake_address": {"type": ["string", "null"]},
                "source_url": {"type": ["string", "null"]},
            },
        },
        "sources": {"type": "array", "items": {"type": "string"}},
    },
}


@dataclass
class HarvestSummary:
    dossiers_written: int
    supabase_ok: int
    supabase_failed: int


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_roster(path: Path = DEFAULT_ROSTER_PATH) -> list[dict]:
    import yaml

    rows = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    return [row for row in rows if isinstance(row, dict)]


def collect_target_pages(center: dict) -> list[dict]:
    seen: set[str] = set()
    pages: list[dict] = []
    for field, kind in TARGET_PAGE_FIELDS:
        url = _normalize_url(center.get(field))
        if not url or url in seen:
            continue
        seen.add(url)
        pages.append({"field": field, "kind": kind, "url": url})
    return pages


def _normalize_url(raw: Any) -> str:
    if raw is None:
        return ""
    value = str(raw).strip()
    if not value or value.lower() in SKIP_URL_VALUES:
        return ""
    if value.startswith("http://") or value.startswith("https://"):
        return value
    return ""


def normalize_geo(
    center: dict,
    *,
    region_field: str = "state",
    country_field: Optional[str] = None,
    default_country_code: str = "US",
) -> tuple[str, str]:
    country = ""
    if country_field:
        country = str(center.get(country_field) or "").strip()
    country = (country or default_country_code or "US").upper()
    region = str(center.get(region_field) or "").strip()
    return country, region


def harvest_center(
    center: dict,
    *,
    extractor: str = "offline",
    region_field: str = "state",
    country_field: Optional[str] = None,
    default_country_code: str = "US",
    fetch_fn: Callable[..., fetch.FetchEnvelope] = fetch.fetch,
    force_refresh: bool = False,
    llm_extract_fn: Callable[..., claude_client.ExtractionResult] = claude_client.extract_structured,
) -> dict:
    country_code, region_code = normalize_geo(
        center,
        region_field=region_field,
        country_field=country_field,
        default_country_code=default_country_code,
    )
    page_targets = collect_target_pages(center)
    pages = [
        harvest_page(target, fetch_fn=fetch_fn, force_refresh=force_refresh)
        for target in page_targets
    ]

    if extractor == "llm":
        structured, llm_usage = extract_with_llm(center, pages, llm_extract_fn=llm_extract_fn)
    else:
        structured, llm_usage = extract_offline(center, pages), None

    source_url = (
        next((page["url"] for page in pages if not page.get("error")), "")
        or _normalize_url(center.get("primary_url"))
    )
    fetched_at = _top_level_fetched_at(pages)
    dossier = {
        "slug": center.get("slug"),
        "country_code": country_code,
        "region_code": region_code,
        "legal_name": center.get("legal_name"),
        "common_name": center.get("common_name"),
        "primary_url": _normalize_url(center.get("primary_url")),
        "extractor": "claude-structured-v1" if extractor == "llm" else "offline-heuristic-v1",
        "harvest_status": classify_harvest_status(page_targets, pages),
        "fetched_at": fetched_at,
        "source_url": source_url or "https://wildlifestats.org/centers/",
        "page_extracts": pages,
        "structured": structured,
        "llm_usage": llm_usage,
    }
    dossier["source_urls"] = sorted(
        {
            url
            for url in (
                structured.get("sources") or []
            ) + [page.get("url") for page in pages if page.get("url")]
            if url
        }
    )
    dossier["content_hash"] = _hash_payload(
        {
            "slug": dossier["slug"],
            "page_extracts": dossier["page_extracts"],
            "structured": dossier["structured"],
            "country_code": dossier["country_code"],
            "region_code": dossier["region_code"],
        }
    )
    return dossier


def harvest_page(
    target: dict,
    *,
    fetch_fn: Callable[..., fetch.FetchEnvelope] = fetch.fetch,
    force_refresh: bool = False,
) -> dict:
    try:
        env = fetch_fn(target["url"], force_refresh=force_refresh)
    except Exception as exc:  # noqa: BLE001
        return {
            "kind": target["kind"],
            "field": target["field"],
            "url": target["url"],
            "error": f"{type(exc).__name__}: {exc}",
        }

    readable = readability.extract_main_content(env.body, fallback_title=target["kind"])
    return {
        "kind": target["kind"],
        "field": target["field"],
        "url": target["url"],
        "source_url": env.source_url,
        "fetched_at": env.fetched_at,
        "source_etag": env.source_etag,
        "http_status": env.http_status,
        "content_hash": env.content_hash,
        "title": readable.title,
        "readability_score": readable.score,
        "paragraph_count": readable.paragraph_count,
        "readable_text": readable.text,
    }


def extract_with_llm(
    center: dict,
    pages: list[dict],
    *,
    llm_extract_fn: Callable[..., claude_client.ExtractionResult] = claude_client.extract_structured,
) -> tuple[dict, dict]:
    usable_pages = [page for page in pages if page.get("readable_text")]
    if not usable_pages:
        return empty_structured_record(), {}

    source_urls = [page["url"] for page in usable_pages]
    user_blocks = [
        f"[{page['kind']}] {page['url']}\nTITLE: {page.get('title', '')}\n\n{page['readable_text']}"
        for page in usable_pages
    ]
    user_content = (
        f"ORGANIZATION: {center.get('common_name') or center.get('legal_name') or center.get('slug')}\n"
        f"SLUG: {center.get('slug')}\n\n"
        + "\n\n====\n\n".join(user_blocks)
    )
    result = llm_extract_fn(
        system_prompt=SYSTEM_PROMPT,
        user_content=user_content,
        output_schema=OUTPUT_SCHEMA,
        source_urls=source_urls,
        model=claude_client.DEFAULT_MODEL,
    )
    record = empty_structured_record()
    record.update(result.record or {})
    if not record.get("sources"):
        record["sources"] = list(result.sources or source_urls)
    usage = {
        "model": result.model,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "estimated_usd": result.estimated_usd,
        "notes": list(result.notes or []),
    }
    return record, usage


def extract_offline(center: dict, pages: list[dict]) -> dict:
    record = empty_structured_record()
    record["mission_statement"], record["mission_statement_source_url"] = _find_mission(pages)
    record["leadership"] = _find_leadership(pages)
    record["services_offered"] = _find_services(pages)
    record["accreditations"] = _find_accreditations(pages)
    record["partnerships"] = _find_partnerships(pages)
    record["contact_info"] = _find_contact_info(pages)
    record["sources"] = sorted(
        {
            item["source_url"]
            for key in ("leadership", "services_offered", "accreditations", "partnerships")
            for item in record[key]
            if item.get("source_url")
        }
        | (
            {record["mission_statement_source_url"]}
            if record.get("mission_statement_source_url")
            else set()
        )
        | (
            {record["contact_info"]["source_url"]}
            if record.get("contact_info", {}).get("source_url")
            else set()
        )
    )
    return record


def empty_structured_record() -> dict:
    return {
        "mission_statement": None,
        "mission_statement_source_url": None,
        "leadership": [],
        "services_offered": [],
        "accreditations": [],
        "partnerships": [],
        "contact_info": {
            "phone": None,
            "email": None,
            "intake_hours": None,
            "intake_address": None,
            "source_url": None,
        },
        "sources": [],
    }


def _find_mission(pages: list[dict]) -> tuple[Optional[str], Optional[str]]:
    for page in _preferred_pages(pages, ("about_url", "primary_url")):
        for line in _page_lines(page):
            match = MISSION_RE.search(line)
            if not match:
                continue
            body = match.group("body").strip()
            quoted = re.search(r"[\"“](.+?)[\"”]", body)
            mission = quoted.group(1).strip() if quoted else body.strip(" \"“”")
            if mission:
                return mission, page["url"]
    return None, None


def _find_leadership(pages: list[dict]) -> list[dict]:
    results: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for page in _preferred_pages(pages, ("about_url", "contact_url", "primary_url")):
        for line in _page_lines(page):
            for pattern in LEADERSHIP_PATTERNS:
                match = pattern.search(line)
                if not match:
                    continue
                title = match.group("title").strip()
                name = match.group("name").strip(" -")
                key = (name.lower(), title.lower())
                if key in seen:
                    continue
                seen.add(key)
                results.append({"name": name, "title": title, "source_url": page["url"]})
    return results


def _find_services(pages: list[dict]) -> list[dict]:
    return _collect_keyword_bullets(pages, SERVICE_KEYWORDS, label_key="label", max_items=8)


def _find_accreditations(pages: list[dict]) -> list[dict]:
    return _collect_keyword_bullets(
        pages,
        ACCREDITATION_KEYWORDS,
        label_key="label",
        max_items=8,
        preferred=("about_url", "primary_url", "annual_reports_url"),
    )


def _find_partnerships(pages: list[dict]) -> list[dict]:
    results: list[dict] = []
    seen: set[str] = set()
    for page in _preferred_pages(pages, ("about_url", "primary_url", "news_or_blog_url")):
        for line in _page_lines(page):
            low = line.lower()
            if not any(keyword in low for keyword in PARTNERSHIP_KEYWORDS):
                continue
            payload = line.split(":", 1)[-1] if ":" in line else line
            for chunk in re.split(r";|, and | and ", payload):
                name = chunk.strip(" -")
                if len(name) < 6:
                    continue
                key = name.lower()
                if key in seen:
                    continue
                seen.add(key)
                results.append({"name": name, "source_url": page["url"]})
    return results


def _find_contact_info(pages: list[dict]) -> dict:
    contact = {
        "phone": None,
        "email": None,
        "intake_hours": None,
        "intake_address": None,
        "source_url": None,
    }
    for page in _preferred_pages(pages, ("contact_url", "wildlife_help_url", "primary_url", "about_url")):
        text = page.get("readable_text") or ""
        if not text:
            continue
        if not contact["email"]:
            email_match = EMAIL_RE.search(text)
            if email_match:
                contact["email"] = email_match.group(0)
                contact["source_url"] = page["url"]
        if not contact["phone"]:
            phone_match = PHONE_RE.search(text)
            if phone_match:
                contact["phone"] = phone_match.group(0).strip()
                contact["source_url"] = page["url"]
        for line in _page_lines(page):
            low = line.lower()
            if not contact["intake_hours"] and ("hours" in low or "open" in low or "intake" in low):
                contact["intake_hours"] = line.strip(" -")
                contact["source_url"] = page["url"]
            if not contact["intake_address"] and re.search(r"\d{2,} .+?, .+?, [A-Z]{2}\b", line):
                contact["intake_address"] = line.strip(" -")
                contact["source_url"] = page["url"]
    return contact


def _collect_keyword_bullets(
    pages: list[dict],
    keywords: tuple[str, ...],
    *,
    label_key: str,
    max_items: int,
    preferred: tuple[str, ...] = ("wildlife_help_url", "about_url", "primary_url"),
) -> list[dict]:
    results: list[dict] = []
    seen: set[str] = set()
    for page in _preferred_pages(pages, preferred):
        for line in _page_lines(page):
            low = line.lower()
            if not any(keyword in low for keyword in keywords):
                continue
            label = line.strip(" -")
            if len(label) < 6:
                continue
            key = label.lower()
            if key in seen:
                continue
            seen.add(key)
            results.append({label_key: label, "source_url": page["url"]})
            if len(results) >= max_items:
                return results
    return results


def _preferred_pages(pages: list[dict], preferred: tuple[str, ...]) -> list[dict]:
    order = {kind: idx for idx, kind in enumerate(preferred)}
    usable = [page for page in pages if page.get("readable_text")]
    return sorted(usable, key=lambda page: order.get(page["kind"], len(order)))


def _page_lines(page: dict) -> list[str]:
    text = page.get("readable_text") or ""
    return [line.strip() for line in text.splitlines() if line.strip()]


def _top_level_fetched_at(pages: list[dict]) -> str:
    stamps = [page.get("fetched_at") for page in pages if page.get("fetched_at")]
    return max(stamps) if stamps else _now_iso()


def classify_harvest_status(targets: list[dict], pages: list[dict]) -> str:
    if not targets:
        return "no_pages"
    successes = sum(1 for page in pages if not page.get("error"))
    if successes == 0:
        return "all_failed"
    if successes < len(targets):
        return "partial"
    return "ok"


def dossier_output_path(dossier: dict, *, build_root: Path = DEFAULT_BUILD_ROOT) -> Path:
    country = (dossier.get("country_code") or "XX").upper()
    region = str(dossier.get("region_code") or "_regionless").lower()
    slug = str(dossier.get("slug") or "unknown")
    return build_root / country / region / f"{slug}.json"


def write_dossier_json(dossier: dict, *, build_root: Path = DEFAULT_BUILD_ROOT) -> Path:
    out = dossier_output_path(dossier, build_root=build_root)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dossier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


def to_supabase_row(dossier: dict) -> dict:
    structured = dossier.get("structured") or {}
    return {
        "slug": dossier.get("slug"),
        "country_code": dossier.get("country_code"),
        "region_code": dossier.get("region_code"),
        "legal_name": dossier.get("legal_name"),
        "common_name": dossier.get("common_name"),
        "primary_url": dossier.get("primary_url"),
        "harvest_status": dossier.get("harvest_status"),
        "extractor": dossier.get("extractor"),
        "mission_statement": structured.get("mission_statement"),
        "mission_statement_source_url": structured.get("mission_statement_source_url"),
        "leadership": structured.get("leadership") or [],
        "services_offered": structured.get("services_offered") or [],
        "accreditations": structured.get("accreditations") or [],
        "partnerships": structured.get("partnerships") or [],
        "contact_info": structured.get("contact_info") or {},
        "source_urls": dossier.get("source_urls") or [],
        "page_extracts": dossier.get("page_extracts") or [],
        "fetched_at": dossier.get("fetched_at"),
        "source_url": dossier.get("source_url"),
        "content_hash": dossier.get("content_hash"),
    }


def dual_write_supabase(dossiers: list[dict]) -> tuple[int, int]:
    ok = failed = 0
    for dossier in dossiers:
        try:
            supabase_client.upsert(
                supabase_client.WriteRequest(
                    target_schema="wildlifestats_bucket_02_firm_profile",
                    target_table="orgs",
                    on_conflict="slug,fetched_at",
                    record=to_supabase_row(dossier),
                )
            )
            ok += 1
        except Exception as exc:  # noqa: BLE001
            failed += 1
            slug = dossier.get("slug") or "unknown"
            print(f"  supabase upsert failed ({slug}): {type(exc).__name__}")
    print(f"  supabase dual-write: {ok} ok, {failed} failed (JSON already canonical)")
    return ok, failed


def run_batch(
    *,
    roster: list[dict],
    extractor: str,
    build_root: Path,
    no_supabase: bool,
    region_field: str,
    country_field: Optional[str],
    default_country_code: str,
    limit: Optional[int] = None,
    slugs: Optional[set[str]] = None,
    fetch_fn: Callable[..., fetch.FetchEnvelope] = fetch.fetch,
    llm_extract_fn: Callable[..., claude_client.ExtractionResult] = claude_client.extract_structured,
    force_refresh: bool = False,
) -> HarvestSummary:
    dossiers_written = supabase_ok = supabase_failed = 0
    selected = roster
    if slugs:
        selected = [center for center in selected if center.get("slug") in slugs]
    if limit is not None:
        selected = selected[:limit]
    for center in selected:
        dossier = harvest_center(
            center,
            extractor=extractor,
            region_field=region_field,
            country_field=country_field,
            default_country_code=default_country_code,
            fetch_fn=fetch_fn,
            force_refresh=force_refresh,
            llm_extract_fn=llm_extract_fn,
        )
        write_dossier_json(dossier, build_root=build_root)
        dossiers_written += 1
        if not no_supabase:
            ok, failed = dual_write_supabase([dossier])
            supabase_ok += ok
            supabase_failed += failed
    return HarvestSummary(
        dossiers_written=dossiers_written,
        supabase_ok=supabase_ok,
        supabase_failed=supabase_failed,
    )


def _hash_payload(payload: dict) -> str:
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--roster", default=str(DEFAULT_ROSTER_PATH))
    ap.add_argument("--build-root", default=str(DEFAULT_BUILD_ROOT))
    ap.add_argument("--extractor", choices=["offline", "llm"], default="offline")
    ap.add_argument("--region-field", default="state")
    ap.add_argument("--country-field", default=None)
    ap.add_argument("--default-country-code", default="US")
    ap.add_argument("--slug", action="append", default=[])
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--no-supabase", action="store_true")
    ap.add_argument("--force-refresh", action="store_true")
    args = ap.parse_args()

    roster = load_roster(Path(args.roster))
    summary = run_batch(
        roster=roster,
        extractor=args.extractor,
        build_root=Path(args.build_root),
        no_supabase=args.no_supabase,
        region_field=args.region_field,
        country_field=args.country_field,
        default_country_code=args.default_country_code,
        limit=args.limit,
        slugs=set(args.slug or []),
        force_refresh=args.force_refresh,
    )
    print(
        f"dossiers: {summary.dossiers_written} | "
        f"supabase ok: {summary.supabase_ok} | "
        f"supabase failed: {summary.supabase_failed}"
    )


if __name__ == "__main__":
    main()

