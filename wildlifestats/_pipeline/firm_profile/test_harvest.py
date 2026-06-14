"""Offline tests for Bucket 02 firm-profile harvesting.

Run:
    PYTHONPATH=. python wildlifestats/_pipeline/firm_profile/test_harvest.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import traceback
from pathlib import Path

from wildlifestats._pipeline._common import fetch, supabase_client
from wildlifestats._pipeline.firm_profile import harvest, readability


PASSED = 0
FAILED = 0
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def case(name: str):
    def wrap(fn):
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
    return wrap


print("=" * 64)
print("Bucket 02 firm-profile harvester")
print("=" * 64)


def _fixture_html(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def _fake_fetch(url: str, **kwargs) -> fetch.FetchEnvelope:  # noqa: ARG001
    mapping = {
        "https://example.org/about": _fixture_html("about.html"),
        "https://example.org/contact": _fixture_html("contact.html"),
        "https://example.org/help": _fixture_html("help.html"),
    }
    body = mapping[url]
    key = Path(url).name or "index"
    return fetch.FetchEnvelope(
        source_url=url,
        fetched_at="2026-06-14T20:00:00Z",
        http_status=200,
        content_hash=f"hash-{key}",
        body=body,
        source_etag=f'"etag-{key}"',
    )


CENTER = {
    "slug": "example-wildlife-center",
    "legal_name": "Example Wildlife Center, Inc.",
    "common_name": "Example Wildlife Center",
    "primary_url": "https://example.org/about",
    "about_url": "https://example.org/about",
    "contact_url": "https://example.org/contact",
    "wildlife_help_url": "https://example.org/help",
    "news_or_blog_url": "",
    "annual_reports_url": "",
    "province": "BC",
}


@case("readability keeps main content and strips site chrome")
def _():
    out = readability.extract_main_content(_fixture_html("about.html"))
    assert "Donate now" not in out.text, "nav/footer noise should be stripped"
    assert "We rescue, rehabilitate, and release native wildlife" in out.text
    assert out.paragraph_count >= 3


@case("harvest_center offline extracts mission, leadership, services, and contact")
def _():
    dossier = harvest.harvest_center(
        CENTER,
        extractor="offline",
        region_field="province",
        default_country_code="CA",
        fetch_fn=_fake_fetch,
    )
    structured = dossier["structured"]
    assert dossier["country_code"] == "CA", dossier["country_code"]
    assert dossier["region_code"] == "BC", dossier["region_code"]
    assert structured["mission_statement"] == (
        "We rescue, rehabilitate, and release native wildlife while educating the public."
    )
    assert structured["mission_statement_source_url"] == "https://example.org/about"
    assert any(item["name"] == "Jane Doe" and item["title"] == "Executive Director"
               for item in structured["leadership"])
    assert any("24/7 wildlife hotline" in item["label"] for item in structured["services_offered"])
    assert structured["contact_info"]["email"] == "help@example.org"
    assert structured["contact_info"]["phone"] == "(555) 123-4567"
    assert structured["contact_info"]["source_url"] == "https://example.org/contact"


@case("write_dossier_json parameterizes path by country and region")
def _():
    dossier = harvest.harvest_center(
        CENTER,
        extractor="offline",
        region_field="province",
        default_country_code="CA",
        fetch_fn=_fake_fetch,
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        out = harvest.write_dossier_json(dossier, build_root=Path(tmpdir))
        assert out.name == "example-wildlife-center.json"
        assert out.parent.name == "bc"
        assert out.parent.parent.name == "CA"
        payload = json.loads(out.read_text(encoding="utf-8"))
        assert payload["slug"] == "example-wildlife-center"


@case("run_batch writes local JSON before a Supabase failure")
def _():
    saved = supabase_client.upsert

    def boom(req):  # noqa: ARG001
        raise RuntimeError("supabase down")

    supabase_client.upsert = boom
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = harvest.run_batch(
                roster=[CENTER],
                extractor="offline",
                build_root=Path(tmpdir),
                no_supabase=False,
                region_field="province",
                country_field=None,
                default_country_code="CA",
                fetch_fn=_fake_fetch,
            )
            out = Path(tmpdir) / "CA" / "bc" / "example-wildlife-center.json"
            assert out.exists(), "JSON canonical write must happen before the Supabase leg"
            assert summary.dossiers_written == 1
            assert summary.supabase_ok == 0 and summary.supabase_failed == 1
    finally:
        supabase_client.upsert = saved


@case("to_supabase_row carries the provenance envelope and nested dossier content")
def _():
    dossier = harvest.harvest_center(
        CENTER,
        extractor="offline",
        region_field="province",
        default_country_code="CA",
        fetch_fn=_fake_fetch,
    )
    row = harvest.to_supabase_row(dossier)
    assert row["slug"] == "example-wildlife-center"
    assert row["fetched_at"] == "2026-06-14T20:00:00Z"
    assert row["source_url"] == "https://example.org/about"
    assert row["content_hash"], "content hash required by supabase_client gate"
    assert row["leadership"], "nested dossier content should survive row mapping"


print()
print("=" * 64)
print(f"Result: {PASSED} passed, {FAILED} failed")
print("=" * 64)
sys.exit(0 if FAILED == 0 else 1)

