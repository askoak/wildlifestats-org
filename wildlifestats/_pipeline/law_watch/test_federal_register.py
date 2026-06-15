"""Offline tests for the federal-only law_watch Federal Register path.

Run:
  PYTHONPATH=. python wildlifestats/_pipeline/law_watch/test_federal_register.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import traceback
from datetime import date
from pathlib import Path

from wildlifestats._pipeline.law_watch import federal_register as fr

PASSED = 0
FAILED = 0


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


SEARCH_PAGE = {
    "count": 2,
    "results": [
        {"document_number": "2026-11634"},
        {"document_number": "2026-11970"},
    ],
}

PROPOSED_RULE = {
    "document_number": "2026-11634",
    "title": "Endangered and Threatened Wildlife and Plants; Threatened Species Status With Section 4(d) Rule for Southern Hognose Snake",
    "abstract": "Correction and reopening of comment period for southern hognose snake proposal.",
    "type": "Proposed Rule",
    "action": "Proposed rule; reopening of comment period and announcement of public hearing; correction.",
    "publication_date": "2026-06-10",
    "effective_on": None,
    "comments_close_on": "2026-07-08",
    "html_url": "https://www.federalregister.gov/documents/2026/06/10/2026-11634/example",
    "pdf_url": "https://www.govinfo.gov/content/pkg/FR-2026-06-10/pdf/2026-11634.pdf",
    "citation": "91 FR 35173",
    "agencies": [
        {"name": "Interior Department", "slug": "interior-department"},
        {"name": "Fish and Wildlife Service", "slug": "fish-and-wildlife-service"},
    ],
    "docket_ids": ["Docket No. FWS-R4-ES-2025-0210"],
    "dockets": [{"id": "FWS-R4-ES-2025-0210", "documents": [{"comment_url": "https://www.regulations.gov/commenton/FWS-R4-ES-2025-0210-0225"}]}],
    "regulation_id_numbers": ["1018-BI23"],
    "regulations_dot_gov_info": {"docket_id": "FWS-R4-ES-2025-0210", "document_id": "FWS-R4-ES-2025-0210-0225"},
    "correction_of": "https://www.federalregister.gov/api/v1/documents/2025-00001",
}

NOTICE = {
    "document_number": "2026-11970",
    "title": "Wilderness Administration and Resource Stewardship; Managing Climbing Activities in Wilderness",
    "abstract": "The U.S. Fish and Wildlife Service announces the availability of draft guidance for wilderness climbing activities in the National Wildlife Refuge System.",
    "type": "Notice",
    "action": None,
    "publication_date": "2026-06-15",
    "effective_on": None,
    "comments_close_on": None,
    "html_url": "https://www.federalregister.gov/documents/2026/06/15/2026-11970/example",
    "pdf_url": "https://www.govinfo.gov/content/pkg/FR-2026-06-15/pdf/2026-11970.pdf",
    "citation": "91 FR 35900",
    "agencies": [
        {"name": "Interior Department", "slug": "interior-department"},
        {"name": "Fish and Wildlife Service", "slug": "fish-and-wildlife-service"},
    ],
    "docket_ids": [],
    "dockets": [],
    "regulation_id_numbers": [],
    "regulations_dot_gov_info": {},
    "correction_of": None,
}


def fake_get(url: str) -> dict:
    if "documents.json" in url:
        return SEARCH_PAGE
    if url.endswith("/2026-11634.json"):
        return PROPOSED_RULE
    if url.endswith("/2026-11970.json"):
        return NOTICE
    raise AssertionError(f"unexpected URL: {url}")


print("=" * 60)
print("law_watch federal_register")
print("=" * 60)


@case("build_search_url includes agency, type, page, and date filters")
def _():
    url = fr.build_search_url(
        agency_slugs=("fish-and-wildlife-service",),
        type_codes=("PRORULE", "NOTICE"),
        published_on_or_after="2026-03-01",
        published_on_or_before="2026-06-15",
        page=2,
        per_page=25,
    )
    assert "conditions%5Bagencies%5D%5B%5D=fish-and-wildlife-service" in url
    assert "conditions%5Btype%5D%5B%5D=PRORULE" in url
    assert "conditions%5Btype%5D%5B%5D=NOTICE" in url
    assert "page=2" in url and "per_page=25" in url
    assert "conditions%5Bpublication_date%5D%5Bgte%5D=2026-03-01" in url


@case("normalize_record maps a proposed rule into the law_watch shape")
def _():
    rec = fr.normalize_record(PROPOSED_RULE, fetched_at="2026-06-15T23:00:00Z", today=date(2026, 6, 15))
    assert rec["law_watch_id"] == "lawwatch.federal_register_api.2026-11634"
    assert rec["source_system"] == "federal_register_api"
    assert rec["source_id"] == "federal_register_api"
    assert rec["policy_stage"] == "proposal_open"
    assert rec["status_stage"] == "open_for_comment"
    assert rec["status_label"] == "active_comment_period"
    assert rec["comment_open"] is True
    assert rec["docket_id"] == "FWS-R4-ES-2025-0210"
    assert rec["comment_url"] == "https://www.regulations.gov/commenton/FWS-R4-ES-2025-0210-0225"
    assert "endangered_species" in rec["topic_tags"], rec["topic_tags"]
    assert "snakes" in rec["taxa_tags"], rec["taxa_tags"]
    assert rec["relevance_status"] == "in_scope"
    assert rec["content_hash"], "expected content_hash"


@case("normalize_record maps a notice without comment deadline cleanly")
def _():
    rec = fr.normalize_record(NOTICE, fetched_at="2026-06-15T23:00:00Z", today=date(2026, 6, 15))
    assert rec["action_type"] == "notice"
    assert rec["policy_stage"] == "notice_only"
    assert rec["status_stage"] == "notice"
    assert rec["comment_open"] is False
    assert rec["comment_deadline"] is None
    assert rec["status_label"] == "newly_posted"


@case("pull_federal_register writes a latest snapshot and counts records")
def _():
    with tempfile.TemporaryDirectory() as tmp:
        summary = fr.pull_federal_register(
            days_back=30,
            agency_slugs=("fish-and-wildlife-service",),
            per_page=10,
            max_pages=1,
            build_root=Path(tmp),
            json_get=fake_get,
            today=date(2026, 6, 15),
        )
        assert summary.search_hits == 2
        assert summary.detail_records == 2
        assert summary.snapshot_path.exists()
        assert summary.latest_path.exists()
        payload = json.loads(summary.latest_path.read_text(encoding="utf-8"))
        assert payload["record_count"] == 2
        assert payload["records"][0]["source_id"] == "federal_register_api"


print()
print("=" * 60)
print(f"Result: {PASSED} passed, {FAILED} failed")
print("=" * 60)
sys.exit(0 if FAILED == 0 else 1)
