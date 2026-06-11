"""Smoke tests for the _common discipline gates.

These tests do NOT exercise live API calls. They verify the validation
gates inside the scaffold modules fire correctly — the gates are the
load-bearing part of the §19 contract, even when the implementation
behind them is still TODO[engineer].

Run from repo root:
    python wildlifestats/_pipeline/_common/test_gates.py
"""

from __future__ import annotations

import sys
import traceback

from wildlifestats._pipeline._common import (
    creds,
    fetch,
    supabase_client,
    exa_client,
    claude_client,
    apify_client,
)


PASSED = 0
FAILED = 0


def case(name: str):
    """Decorator: register a test case and run it with pass/fail counting."""
    def wrap(fn):
        global PASSED, FAILED
        try:
            fn()
            print(f"  PASS  {name}")
            PASSED += 1
        except AssertionError as e:
            print(f"  FAIL  {name}: {e}")
            FAILED += 1
        except Exception as e:
            print(f"  ERROR {name}: {type(e).__name__}: {e}")
            traceback.print_exc()
            FAILED += 1
        return fn
    return wrap


print("=" * 64)
print("WildlifeStats _common discipline gates")
print("=" * 64)

print("\n[creds] missing-credential errors carry remediation hints")


@case("get_apify_token raises clear MissingCredentialError when env empty")
def _():
    import os
    saved = os.environ.pop("CUSTOM_CRED_API_APIFY_COM_TOKEN", None)
    try:
        try:
            creds.get_apify_token()
            assert False, "expected MissingCredentialError"
        except creds.MissingCredentialError as e:
            msg = str(e)
            assert "custom-cred:api.apify.com" in msg, f"missing handle in: {msg}"
            assert "approve_credential" in msg, f"missing hint in: {msg}"
    finally:
        if saved is not None:
            os.environ["CUSTOM_CRED_API_APIFY_COM_TOKEN"] = saved


@case("is_present returns False for empty env without raising")
def _():
    import os
    saved = os.environ.pop("WILDLIFESTATS_TEST_NOT_SET", None)
    try:
        assert creds.is_present("WILDLIFESTATS_TEST_NOT_SET") is False
    finally:
        if saved is not None:
            os.environ["WILDLIFESTATS_TEST_NOT_SET"] = saved


print("\n[fetch] forbidden paths refuse before any network activity")


@case("fetch refuses /admin paths with ForbiddenPath")
def _():
    try:
        fetch.fetch("https://example.org/admin/console")
        assert False, "expected ForbiddenPath"
    except fetch.ForbiddenPath:
        pass


@case("fetch refuses /wp-admin paths with ForbiddenPath")
def _():
    try:
        fetch.fetch("https://example.org/wp-admin/")
        assert False, "expected ForbiddenPath"
    except fetch.ForbiddenPath:
        pass


print("\n[supabase] §19 RLS gates fire client-side")


@case("upsert rejects brwc_* target schema with CrossLaneViolation")
def _():
    req = supabase_client.WriteRequest(
        target_schema="brwc_patient_records",
        target_table="intake",
        record={
            "fetched_at": "2026-06-11T15:00:00Z",
            "source_url": "https://example.org/x",
            "content_hash": "abc",
        },
    )
    try:
        supabase_client.upsert(req)
        assert False, "expected CrossLaneViolation"
    except supabase_client.CrossLaneViolation as e:
        assert "brwc_" in str(e)


@case("upsert rejects unregistered WildlifeStats schema")
def _():
    req = supabase_client.WriteRequest(
        target_schema="wildlifestats_not_a_real_schema",
        target_table="t",
        record={
            "fetched_at": "2026-06-11T15:00:00Z",
            "source_url": "https://example.org/x",
            "content_hash": "abc",
        },
    )
    try:
        supabase_client.upsert(req)
        assert False, "expected CrossLaneViolation"
    except supabase_client.CrossLaneViolation as e:
        assert "registered" in str(e).lower()


@case("upsert rejects record missing provenance with MissingProvenance")
def _():
    req = supabase_client.WriteRequest(
        target_schema="wildlifestats_bucket_02_firm_profile",
        target_table="orgs",
        record={"rehab_org_id": "blue-ridge-wildlife-center"},
    )
    try:
        supabase_client.upsert(req)
        assert False, "expected MissingProvenance"
    except supabase_client.MissingProvenance as e:
        assert "fetched_at" in str(e)


@case("upsert rejects BRWC EIN in raw-records bucket with CrossLaneViolation")
def _():
    req = supabase_client.WriteRequest(
        target_schema="wildlifestats_secure_bucket_05_raw_records",
        target_table="intakes",
        record={
            "fetched_at": "2026-06-11T15:00:00Z",
            "source_url": "https://example.org/x",
            "content_hash": "abc",
            "rehab_org_ein": supabase_client.BRWC_EIN,
        },
    )
    try:
        supabase_client.upsert(req)
        assert False, "expected CrossLaneViolation"
    except supabase_client.CrossLaneViolation as e:
        assert "BRWC raw records" in str(e) and "BRWC lane" in str(e)


@case("upsert allows non-BRWC EIN in raw-records bucket past validation gates")
def _():
    # Validation passes; the actual postgrest call is still TODO[engineer],
    # which raises NotImplementedError. That's the expected outcome — it
    # means the validation gates did NOT fire on a legitimate record.
    req = supabase_client.WriteRequest(
        target_schema="wildlifestats_secure_bucket_05_raw_records",
        target_table="intakes",
        record={
            "fetched_at": "2026-06-11T15:00:00Z",
            "source_url": "https://example.org/x",
            "content_hash": "abc",
            "rehab_org_ein": "94-2759874",  # Sonoma County Wildlife Rescue
        },
    )
    try:
        supabase_client.upsert(req)
        assert False, "expected NotImplementedError (scaffold passthrough)"
    except supabase_client.CrossLaneViolation as e:
        assert False, f"unexpected lane violation on legitimate record: {e}"
    except supabase_client.MissingProvenance as e:
        assert False, f"unexpected provenance error: {e}"
    except NotImplementedError:
        pass  # expected — gates passed, scaffold raised


print("\n[exa] artifact-type validation gates")


@case("find_canonical_url rejects unknown artifact_type")
def _():
    try:
        exa_client.find_canonical_url("Some Org", "not_a_real_artifact_type")
        assert False, "expected ValueError"
    except ValueError as e:
        assert "Unknown artifact_type" in str(e)


print("\n[claude] source-URL discipline gate")


@case("extract_structured rejects calls without source_urls")
def _():
    try:
        claude_client.extract_structured(
            system_prompt="x",
            user_content="x",
            output_schema={"type": "object"},
            source_urls=[],
        )
        assert False, "expected ValueError"
    except ValueError as e:
        assert "source_url" in str(e)


print("\n[apify] platform validation gate")


@case("run_actor rejects unknown platform")
def _():
    req = apify_client.ActorRunRequest(
        platform="myspace",
        target_url="https://myspace.com/x",
        org_slug="x",
        org_ein=None,
        tier=1,
    )
    try:
        apify_client.run_actor(req)
        assert False, "expected ValueError"
    except ValueError as e:
        assert "Unknown platform" in str(e)


print()
print("=" * 64)
print(f"Result: {PASSED} passed, {FAILED} failed")
print("=" * 64)

sys.exit(0 if FAILED == 0 else 1)
