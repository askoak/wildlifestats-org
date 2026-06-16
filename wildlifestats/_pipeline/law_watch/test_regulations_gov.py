"""Offline tests for the Regulations.gov law_watch enrichment path.

Run:
  PYTHONPATH=. python wildlifestats/_pipeline/law_watch/test_regulations_gov.py
"""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import traceback
from datetime import date
from pathlib import Path

from wildlifestats._pipeline.law_watch import cross_source_bridge as bridge
from wildlifestats._pipeline.law_watch import federal_register as fr
from wildlifestats._pipeline.law_watch import regulations_gov as rg

PASSED = 0
FAILED = 0

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_ROOT = REPO_ROOT / "tests/fixtures"


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


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))


SEARCH_FIXTURE = load_fixture("regulations_gov_documents_search.json")
PRIMARY_DOC = load_fixture("regulations_gov_document_detail_primary.json")
PRIMARY_DOCKET = load_fixture("regulations_gov_docket_detail_primary.json")
OPEN_DOC = load_fixture("regulations_gov_document_detail_open.json")
OPEN_DOCKET = load_fixture("regulations_gov_docket_detail_open.json")

FR_PROPOSED_RULE = {
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


def primary_bundle() -> dict:
    return {"document": copy.deepcopy(PRIMARY_DOC), "docket": copy.deepcopy(PRIMARY_DOCKET)}


def open_bundle() -> dict:
    return {"document": copy.deepcopy(OPEN_DOC), "docket": copy.deepcopy(OPEN_DOCKET)}


def fake_get(url: str) -> dict:
    if "/documents?" in url:
        return copy.deepcopy(SEARCH_FIXTURE)
    if "/documents/FWS-R4-ES-2025-0210-0225?" in url:
        return copy.deepcopy(PRIMARY_DOC)
    if "/documents/NOAA-NMFS-2026-0007-0003?" in url:
        return copy.deepcopy(OPEN_DOC)
    if url.endswith("/dockets/FWS-R4-ES-2025-0210"):
        return copy.deepcopy(PRIMARY_DOCKET)
    if url.endswith("/dockets/NOAA-NMFS-2026-0007"):
        return copy.deepcopy(OPEN_DOCKET)
    raise AssertionError(f"unexpected URL: {url}")


print("=" * 60)
print("law_watch regulations_gov")
print("=" * 60)


@case("build_documents_search_url includes date, agency, and type filters")
def _():
    url = rg.build_documents_search_url(
        query="snake",
        since="2026-06-01",
        page=2,
        page_size=125,
        agency_ids=("FWS", "NOAA-NMFS"),
        document_types=("Proposed Rule", "Supporting & Related"),
    )
    assert "filter%5BsearchTerm%5D=snake" in url
    assert "filter%5BpostedDate%5D%5Bge%5D=2026-06-01" in url
    assert "filter%5BagencyId%5D=FWS%2CNOAA-NMFS" in url
    assert "filter%5BdocumentType%5D=Proposed+Rule%2CSupporting+%26+Related" in url
    assert "page%5Bnumber%5D=2" in url and "page%5Bsize%5D=125" in url


@case("fetch_regulations_gov caches payloads and dedupes duplicate document ids")
def _():
    with tempfile.TemporaryDirectory() as tmp:
        bundles = rg.fetch_regulations_gov(
            query="wildlife",
            since="2026-06-01",
            cache_root=Path(tmp),
            json_get=fake_get,
            today=date(2026, 6, 15),
        )
        assert len(bundles) == 2
        cache_dir = Path(tmp) / "2026-06-15"
        assert (cache_dir / "documents-page-001.json").exists()
        assert (cache_dir / "documents-detail-FWS-R4-ES-2025-0210-0225.json").exists()
        assert (cache_dir / "dockets-detail-FWS-R4-ES-2025-0210.json").exists()

        def no_network(_: str) -> dict:
            raise AssertionError("expected cache hit, not network call")

        cached = rg.fetch_regulations_gov(
            query="wildlife",
            since="2026-06-01",
            cache_root=Path(tmp),
            json_get=no_network,
            today=date(2026, 6, 15),
        )
        assert len(cached) == 2


@case("normalize_regulations_gov maps the primary fixture per the field contract")
def _():
    record = rg.normalize_regulations_gov(
        primary_bundle(),
        fetched_at="2026-06-15T23:30:00Z",
        today=date(2026, 6, 15),
    )
    assert record["law_watch_id"] == "lawwatch.regulations_gov_api.FWS-R4-ES-2025-0210-0225"
    assert record["source_system"] == "regulations_gov_api"
    assert record["thread_key"] == "FWS-R4-ES-2025-0210"
    assert record["source_url"] == "https://www.regulations.gov/document/FWS-R4-ES-2025-0210-0225"
    assert record["source_document_url"] == "https://downloads.regulations.gov/FWS-R4-ES-2025-0210-0225/content.pdf"
    assert record["short_summary"] == PRIMARY_DOCKET["data"]["attributes"]["dkAbstract"]
    assert record["action_type"] == "proposed_rule"
    assert record["policy_stage"] == "proposal_closed"
    assert record["comment_open"] is False
    assert record["comment_window_open"] is False
    assert record["status_label"] == "comment_closed"
    assert record["docket_id"] == "FWS-R4-ES-2025-0210"
    assert record["document_number"] == "2026-11634"
    assert record["citation"] == "91 FR 35173"
    assert record["related_ids"] == ["FWS_FRDOC_0001-2460", "1018-BI23"]
    assert record["comment_url"] is None
    assert "comment URL is not explicit" in (record["notes"] or "")
    assert record["field_gaps"] == []


@case("comment_window_open flips correctly for future and past deadlines")
def _():
    future_record = rg.normalize_regulations_gov(
        open_bundle(),
        fetched_at="2026-06-15T23:30:00Z",
        today=date(2026, 6, 15),
    )
    assert future_record["comment_window_open"] is True
    assert future_record["comment_window_end_utc"] == "2099-07-20T23:59:59Z"
    assert future_record["policy_stage"] == "docket_open"
    assert future_record["action_type"] == "supporting_document"
    assert future_record["status_label"] == "active_comment_period"

    past = open_bundle()
    attrs = past["document"]["data"]["attributes"]
    attrs["commentEndDate"] = "2020-01-01T00:00:00Z"
    attrs["openForComment"] = False
    attrs["postedDate"] = "2020-01-01T00:00:00Z"
    attrs["withinCommentPeriod"] = False
    past_record = rg.normalize_regulations_gov(
        past,
        fetched_at="2026-06-15T23:30:00Z",
        today=date(2026, 6, 15),
    )
    assert past_record["comment_window_open"] is False
    assert past_record["status_label"] == "historical_reference"


@case("emit_regulations_gov_records writes jsonl and summary from offline bundles")
def _():
    with tempfile.TemporaryDirectory() as tmp:
        count = rg.emit_regulations_gov_records(
            raw_records=[primary_bundle(), open_bundle()],
            output_root=Path(tmp),
            fetched_at="2026-06-15T23:30:00Z",
            today=date(2026, 6, 15),
        )
        assert count == 2
        output_path = Path(tmp) / "regulations_gov.jsonl"
        summary_path = Path(tmp) / "regulations_gov-summary.json"
        assert output_path.exists()
        assert summary_path.exists()
        rows = bridge.load_records(output_path)
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        assert len(rows) == 2
        assert summary["record_count"] == 2
        assert summary["open_comment_windows"] == 1
        assert summary["field_gaps"] == []


@case("cross_source_bridge matches FR and RG records by document number and docket id")
def _():
    fr_record = fr.normalize_record(
        FR_PROPOSED_RULE,
        fetched_at="2026-06-15T23:30:00Z",
        today=date(2026, 6, 15),
    )
    rg_record = rg.normalize_regulations_gov(
        primary_bundle(),
        fetched_at="2026-06-15T23:30:00Z",
        today=date(2026, 6, 15),
    )
    enriched = bridge.cross_source_bridge([fr_record], [rg_record, copy.deepcopy(rg_record)])
    assert len(enriched) == 1
    row = enriched[0]
    assert row["regulations_gov_source_native_id"] == "FWS-R4-ES-2025-0210-0225"
    assert row["regulations_gov_comment_url"] == fr_record["comment_url"]
    assert row["bridge_provenance"]["matched"] is True
    assert sorted(row["bridge_provenance"]["match_keys"]) == ["docket_id", "document_number"]
    assert row["bridge_provenance"]["comment_url_source"] == "federal_register_api"


@case("emit_enriched_records writes a separate artifact without mutating inputs")
def _():
    fr_record = fr.normalize_record(
        FR_PROPOSED_RULE,
        fetched_at="2026-06-15T23:30:00Z",
        today=date(2026, 6, 15),
    )
    rg_record = rg.normalize_regulations_gov(
        primary_bundle(),
        fetched_at="2026-06-15T23:30:00Z",
        today=date(2026, 6, 15),
    )
    original_fr = copy.deepcopy(fr_record)
    original_rg = copy.deepcopy(rg_record)
    with tempfile.TemporaryDirectory() as tmp:
        output_path = Path(tmp) / "law_watch_enriched.jsonl"
        summary_path = Path(tmp) / "law_watch_enriched-summary.json"
        count = bridge.emit_enriched_records(
            fr_records=[fr_record],
            rg_records=[rg_record],
            output_path=output_path,
            summary_path=summary_path,
        )
        assert count == 1
        assert output_path.exists()
        assert summary_path.exists()
        rows = bridge.load_records(output_path)
        assert rows[0]["bridge_provenance"]["matched"] is True
        assert fr_record == original_fr
        assert rg_record == original_rg


print()
print("=" * 60)
print(f"Result: {PASSED} passed, {FAILED} failed")
print("=" * 60)
sys.exit(0 if FAILED == 0 else 1)
