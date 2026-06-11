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


print("\n[fetch] implementation — robots, cache, dating (offline, monkeypatched)")


def _with_fetch_sandbox(fake_get):
    """Context helper: isolate CACHE_ROOT to a temp dir + stub _http_get +
    clear the rate-limit clock. Returns a restore() callable."""
    import tempfile
    from pathlib import Path
    saved = (fetch.CACHE_ROOT, fetch._http_get, dict(fetch._LAST_HIT))
    fetch.CACHE_ROOT = Path(tempfile.mkdtemp())
    fetch._http_get = fake_get
    fetch._LAST_HIT.clear()

    def restore():
        fetch.CACHE_ROOT, fetch._http_get, hits = saved
        fetch._LAST_HIT.clear()
        fetch._LAST_HIT.update(hits)
    return restore


@case("fetch returns a dated envelope, then serves the second call from cache")
def _():
    import hashlib
    calls = {"page": 0}

    def fake_get(u, timeout=30):
        if u.endswith("/robots.txt"):
            return 200, "User-agent: *\nAllow: /", None
        calls["page"] += 1
        return 200, "<html>hi</html>", '"etag-1"'

    restore = _with_fetch_sandbox(fake_get)
    try:
        e1 = fetch.fetch("https://example.org/page", rate_limit_seconds=0)
        assert e1.from_cache is False and e1.http_status == 200
        assert e1.fetched_at.endswith("Z"), "dating envelope must be ISO-Z"
        assert e1.content_hash == hashlib.sha256(b"<html>hi</html>").hexdigest()
        assert e1.source_etag == '"etag-1"'
        e2 = fetch.fetch("https://example.org/page", rate_limit_seconds=0)
        assert e2.from_cache is True, "second call must be served from cache"
        assert calls["page"] == 1, "page must be fetched over the network only once"
    finally:
        restore()


@case("fetch honors a robots Disallow with DisallowedByRobots (no network GET)")
def _():
    def fake_get(u, timeout=30):
        if u.endswith("/robots.txt"):
            return 200, "User-agent: *\nDisallow: /", None
        assert False, "page must NOT be fetched when robots disallows"

    restore = _with_fetch_sandbox(fake_get)
    try:
        fetch.fetch("https://example.org/private", rate_limit_seconds=0)
        assert False, "expected DisallowedByRobots"
    except fetch.DisallowedByRobots:
        pass
    finally:
        restore()


@case("fetch refuses to proceed when robots.txt cannot be verified")
def _():
    import urllib.error

    def fake_get(u, timeout=30):
        if u.endswith("/robots.txt"):
            raise urllib.error.URLError("network down")
        assert False, "page must NOT be fetched when robots is unverifiable"

    restore = _with_fetch_sandbox(fake_get)
    try:
        fetch.fetch("https://example.org/page", rate_limit_seconds=0)
        assert False, "expected FetchError (robots unverifiable)"
    except fetch.DisallowedByRobots:
        assert False, "should be a generic FetchError, not a robots-disallow"
    except fetch.FetchError:
        pass
    finally:
        restore()


@case("assert_robots_cached raises for a host with no cached robots")
def _():
    import tempfile
    from pathlib import Path
    saved = fetch.CACHE_ROOT
    fetch.CACHE_ROOT = Path(tempfile.mkdtemp())
    try:
        fetch.assert_robots_cached("https://never-fetched.example/x")
        assert False, "expected FetchError for uncached host"
    except fetch.FetchError:
        pass
    finally:
        fetch.CACHE_ROOT = saved


@case("fetch live round-trip [skipped unless WILDLIFESTATS_LIVE_FETCH=1]")
def _():
    import os
    if os.environ.get("WILDLIFESTATS_LIVE_FETCH") != "1":
        print("    (skipped — set WILDLIFESTATS_LIVE_FETCH=1 to run live)")
        return
    env = fetch.fetch("https://example.com/", rate_limit_seconds=0, force_refresh=True)
    assert env.http_status == 200 and env.body, "expected a live 200 with a body"
    assert env.content_hash and env.fetched_at.endswith("Z")
    fetch.assert_robots_cached("https://example.com/")  # must not raise post-fetch


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
    # Validation passes on a legitimate record, so upsert() proceeds to read
    # the Supabase credential. With no token in the CI environment that read
    # raises MissingCredentialError — which proves the §19 client gates did
    # NOT fire on a legitimate record and the postgrest path is wired to
    # creds (not a hardcoded module-level secret). The live HTTP call itself
    # is covered by the flag-gated live test below.
    import os
    saved_url = os.environ.pop("CUSTOM_CRED_OAMQICYLPYTBLDRNYBCC_SUPABASE_CO_URL", None)
    saved_tok = os.environ.pop("CUSTOM_CRED_OAMQICYLPYTBLDRNYBCC_SUPABASE_CO_TOKEN", None)
    req = supabase_client.WriteRequest(
        target_schema="wildlifestats_secure_bucket_05_raw_records",
        target_table="raw_records",
        record={
            "fetched_at": "2026-06-11T15:00:00Z",
            "source_url": "https://example.org/x",
            "content_hash": "abc",
            "rehab_org_ein": "94-2759874",  # Sonoma County Wildlife Rescue
        },
    )
    try:
        supabase_client.upsert(req)
        assert False, "expected MissingCredentialError (no token in CI env)"
    except supabase_client.CrossLaneViolation as e:
        assert False, f"unexpected lane violation on legitimate record: {e}"
    except supabase_client.MissingProvenance as e:
        assert False, f"unexpected provenance error: {e}"
    except creds.MissingCredentialError:
        pass  # expected — gates passed; credential read is where it stops in CI
    finally:
        if saved_url is not None:
            os.environ["CUSTOM_CRED_OAMQICYLPYTBLDRNYBCC_SUPABASE_CO_URL"] = saved_url
        if saved_tok is not None:
            os.environ["CUSTOM_CRED_OAMQICYLPYTBLDRNYBCC_SUPABASE_CO_TOKEN"] = saved_tok


@case("upsert live round-trip [skipped unless WILDLIFESTATS_LIVE_SUPABASE=1]")
def _():
    # Live, money/quota-touching round-trip against the real project. Skipped
    # by default so CI exercises only the offline gates. Enable explicitly with
    #   WILDLIFESTATS_LIVE_SUPABASE=1  (plus the Supabase creds in env)
    # to validate the actual postgrest write + the server-side §19 CHECK gate.
    import os
    if os.environ.get("WILDLIFESTATS_LIVE_SUPABASE") != "1":
        print("    (skipped — set WILDLIFESTATS_LIVE_SUPABASE=1 to run live)")
        return
    import time
    stamp = str(int(time.time()))
    # 1) A legitimate org record must write and round-trip.
    ok = supabase_client.WriteRequest(
        target_schema="wildlifestats_secure_bucket_05_raw_records",
        target_table="raw_records",
        on_conflict="rehab_org_ein,content_hash",
        record={
            "fetched_at": "2026-06-11T15:00:00Z",
            "source_url": "https://example.org/live-test",
            "content_hash": f"livetest-{stamp}",
            "rehab_org_ein": "94-2759874",
            "record": {"_test": True},
        },
    )
    returned = supabase_client.upsert(ok)
    assert returned.get("rehab_org_ein") == "94-2759874", f"round-trip mismatch: {returned}"
    # 2) A BRWC EIN must be rejected server-side (CHECK constraint), surfacing
    #    as a RuntimeError from the postgrest 4xx — never a silent success.
    brwc = supabase_client.WriteRequest(
        target_schema="wildlifestats_secure_bucket_05_raw_records",
        target_table="raw_records",
        record={
            "fetched_at": "2026-06-11T15:00:00Z",
            "source_url": "https://example.org/live-test-brwc",
            "content_hash": f"livetest-brwc-{stamp}",
            "rehab_org_ein": supabase_client.BRWC_EIN,
            "record": {"_test": True},
        },
    )
    try:
        supabase_client.upsert(brwc)
        assert False, "BRWC EIN was NOT rejected server-side — §19 breach"
    except supabase_client.CrossLaneViolation:
        pass  # client gate caught it first — also acceptable
    except RuntimeError as e:
        assert "23514" in str(e) or "raw_records_no_brwc_ein" in str(e) or "violates check" in str(e).lower(), \
            f"expected a CHECK-constraint rejection, got: {e}"


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
