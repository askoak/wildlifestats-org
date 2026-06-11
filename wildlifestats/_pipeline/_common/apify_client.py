"""Apify API client for Bucket 01 (Social).

Phase 9 standardization of the Flyway POC's `wildlifestats/_pipeline/flyway/
apify_client.py`. Engineer is invited to refactor the POC client into
this module and delete the original once Bucket 01 lands.

CONTRACT:

  1. Token via creds.get_apify_token() — never module-level. The 2026-06-11
     Flyway POC proved this pattern; codify it.

  2. Two-tier orchestration (per Mike's Decision A 2026-06-11):
     - Tier 1: ~50 priority centers (largest by intake/revenue). Full
       backfill on first run; monthly refresh thereafter.
     - Tier 2: ~131 long-tail centers. Trailing 90-day window only;
       quarterly refresh.

  3. Per-platform actor mapping:
       Facebook  -> apify/facebook-pages-scraper
       Instagram -> apify/instagram-scraper
       X         -> apify/twitter-scraper
       TikTok    -> apify/tiktok-scraper
       YouTube   -> apify/youtube-scraper
     The Flyway POC validated FB + IG cost discipline; the others inherit
     the same rate-limit and cache pattern.

  4. NO RAW POST TEXT WRITTEN TO DISK. The Flyway POC audit log confirmed
     post_text_NOT_STORED: true on every record. This is non-negotiable
     and architect-ratified per §19 + the 2026-06-11 09:30 INBOX. Records
     carry extracted *signals* (phenology, baby-season-start, intake-volume
     deltas, etc.) — never the source post.

  5. Cost ceiling: $5-10/run for ad-hoc, $50-100/month for steady-state
     two-tier. Caller MUST surface est_cost_usd before issuing the call
     and actual_cost_usd in the run summary. Mike pre-authorized the
     steady-state spend conditional on Phase 4.5+h trigger validation
     (currently dispatched, not yet shipped).

  6. The deterministic offline matcher (Flyway's extract.py vocabulary
     lists) stays as the CI/test backend. Production recall path is the
     Claude extractor — the 2026-06-11 POC documented the zero-recall
     finding and the rationale.

THIS MODULE IS A SCAFFOLD. Engineer's Phase 9 implementation either:
  (a) refactors flyway/apify_client.py into this module verbatim, plus
      the multi-platform support added below; OR
  (b) wraps the existing flyway/apify_client.py and adds the orchestration
      layer on top.

Engineer's call. The POC client is the proven artifact; preserve it.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from . import creds

APIFY_API = "https://api.apify.com/v2"

# FB + IG use the POST-scraper actors the 2026-06-11 Flyway POC validated for
# cost discipline (posts, not page metadata) — preserving the proven artifact
# over the scaffold's page-scraper placeholders. X/TikTok/YouTube inherit the
# same rate-limit + cache + no-raw-text pattern; their input shapes are
# calibrated per-actor when Bucket 01 (9d.01) goes live.
PLATFORM_ACTORS = {
    "facebook": "apify/facebook-posts-scraper",   # POC-validated
    "instagram": "apify/instagram-post-scraper",  # POC-validated
    "x": "apify/twitter-scraper",
    "twitter": "apify/twitter-scraper",  # alias
    "tiktok": "apify/tiktok-scraper",
    "youtube": "apify/youtube-scraper",
}

# Rough per-post Apify cost by platform; FB/IG anchored on the POC (47 posts ≈
# $0.30 ≈ $0.0064/post). Used to surface a spend CEILING before a run.
PER_POST_USD = {
    "facebook": 0.007, "instagram": 0.007, "x": 0.005,
    "twitter": 0.005, "tiktok": 0.006, "youtube": 0.005,
}
PER_RUN_BASE_USD = 0.01  # actor start overhead

# Where per-run audit logs land (one line per post, NEVER any post text).
AUDIT_ROOT = Path("data/_apify_audit")

TIER_1_BACKFILL_DAYS = 365 * 2  # 2 years of history for priority centers
TIER_2_WINDOW_DAYS = 90  # trailing 90 days for long-tail centers


@dataclass
class ActorRunRequest:
    """One actor-run intent. Caller submits a list of these per refresh
    pass; orchestrator batches and rate-limits."""

    platform: str
    target_url: str  # e.g., the FB page URL for a specific center
    org_slug: str  # for record attribution
    org_ein: Optional[str]
    tier: int  # 1 (priority) or 2 (long-tail)
    since_date: Optional[str] = None  # ISO 8601; None = full backfill
    max_posts: int = 200  # safety cap per actor run
    notes: list[str] = field(default_factory=list)


@dataclass
class ActorRunResult:
    """One actor-run outcome. Records flow to extract_signals(); raw posts
    are discarded before the function returns."""

    request: ActorRunRequest
    posts_scraped: int
    apify_cost_usd: float
    apify_run_id: str
    apify_dataset_id: str
    audit_log_path: str  # path to per-run audit log (no raw text)
    succeeded: bool
    error: Optional[str] = None


def run_actor(request: ActorRunRequest) -> ActorRunResult:
    """Issue one Apify actor run and return summary.

    TODO[engineer]: implement against api.apify.com /v2/acts. Use
    creds.get_apify_token() for auth. Recommended decomposition:

    1. Resolve platform → actor via PLATFORM_ACTORS.
    2. Build the actor input dict per the actor's schema (already
       documented in flyway/apify_client.py for FB/IG; replicate the
       pattern for X/TikTok/YouTube).
    3. POST /v2/acts/{actor}/runs with the input. Apify charges per
       actor-run; capture run_id from the response.
    4. Poll /v2/actor-runs/{run_id} until status == 'SUCCEEDED' or
       'FAILED'. Backoff with retry only on transient failures.
    5. On SUCCEEDED, fetch /v2/datasets/{dataset_id}/items to get the
       scraped posts.
    6. Hand posts to the extractor; immediately discard raw text from
       memory after extraction.
    7. Write the audit log per the Flyway POC's contract — one line
       per post with post_text_NOT_STORED: true.
    8. Return ActorRunResult.

    Per the contract: NO raw post text ever lands on disk outside the
    Apify dataset (which lives in Apify's cloud, not our infrastructure).
    """
    if request.platform not in PLATFORM_ACTORS:
        raise ValueError(
            f"Unknown platform: {request.platform!r}. "
            f"Must be one of: {list(PLATFORM_ACTORS)}"
        )
    token = creds.get_apify_token()
    actor = PLATFORM_ACTORS[request.platform]
    run_input = _build_actor_input(request)

    try:
        run = _start_run(actor, run_input, token)
        run_id = run["id"]
        run = _poll_run(run_id, token)
        if run.get("status") != "SUCCEEDED":
            return ActorRunResult(
                request=request, posts_scraped=0, apify_cost_usd=_run_cost(run),
                apify_run_id=run_id, apify_dataset_id=run.get("defaultDatasetId", ""),
                audit_log_path="", succeeded=False,
                error=f"actor run status={run.get('status')}",
            )
        dataset_id = run["defaultDatasetId"]
        posts = _fetch_items(dataset_id, token, request.max_posts)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        return ActorRunResult(request, 0, 0.0, "", "", "", False,
                              error=f"Apify API error (HTTP {exc.code}): {detail}")
    except urllib.error.URLError as exc:
        return ActorRunResult(request, 0, 0.0, "", "", "", False,
                              error=f"Apify network error: {exc.reason}")

    # Audit (URLs + flags only) then DROP the raw posts. No post text ever
    # touches our disk — the bodies live only in Apify's cloud dataset.
    audit_path = _write_audit(run_id, posts, request)
    count = len(posts)
    posts = None  # explicit drop

    return ActorRunResult(
        request=request,
        posts_scraped=count,
        apify_cost_usd=_run_cost(run),
        apify_run_id=run_id,
        apify_dataset_id=dataset_id,
        audit_log_path=str(audit_path),
        succeeded=True,
    )


def estimate_cost(requests: list[ActorRunRequest]) -> float:
    """Upper-bound Apify cost for a batch (per-post ceiling × max_posts cap +
    per-run base). Surfaced in PR descriptions BEFORE a batch issues, so Mike's
    authorization is informed. Real spend is typically lower (few pages hit the
    cap). Calibrated from the POC's 47-post / ~$0.30 run."""
    total = 0.0
    for req in requests:
        per_post = PER_POST_USD.get(req.platform, 0.007)
        total += PER_RUN_BASE_USD + req.max_posts * per_post
    return round(total, 4)


# ---- HTTP + input + audit helpers (Phase 9c.4) ----
def _build_actor_input(request: ActorRunRequest) -> dict:
    """Per-platform actor input. FB/IG shapes are POC-proven; the others are
    sensible defaults pending per-actor calibration at 9d.01."""
    p, url, limit = request.platform, request.target_url, request.max_posts
    if p == "facebook":
        run_input = {"startUrls": [{"url": url}], "resultsLimit": limit,
                     "captionText": False}
        if request.since_date:
            run_input["onlyPostsNewerThan"] = request.since_date
        return run_input
    if p == "instagram":
        return {"directUrls": [url], "resultsLimit": limit}
    if p in ("x", "twitter"):
        return {"startUrls": [{"url": url}], "maxItems": limit}
    if p == "tiktok":
        return {"profiles": [url], "resultsPerPage": limit}
    if p == "youtube":
        return {"startUrls": [{"url": url}], "maxResults": limit}
    raise ValueError(f"No input builder for platform {p!r}")  # unreachable past gate


def _start_run(actor: str, run_input: dict, token: str) -> dict:
    slug = actor.replace("/", "~")
    url = f"{APIFY_API}/acts/{slug}/runs?token={token}"
    req = urllib.request.Request(
        url, data=json.dumps(run_input).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8")).get("data", {})


def _poll_run(run_id: str, token: str, *, max_wait_s: int = 600, interval_s: float = 5.0) -> dict:
    url = f"{APIFY_API}/actor-runs/{run_id}?token={token}"
    waited = 0.0
    terminal = {"SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"}
    while True:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8")).get("data", {})
        if data.get("status") in terminal or waited >= max_wait_s:
            return data
        time.sleep(interval_s)
        waited += interval_s


def _fetch_items(dataset_id: str, token: str, limit: int) -> list:
    url = f"{APIFY_API}/datasets/{dataset_id}/items?token={token}&clean=true&limit={limit}"
    with urllib.request.urlopen(url, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _run_cost(run: dict) -> float:
    """Actual run cost from Apify's run stats, where reported."""
    for key in ("usageTotalUsd", "costUsd"):
        if isinstance(run.get(key), (int, float)):
            return round(float(run[key]), 6)
    stats = run.get("stats") or {}
    if isinstance(stats.get("computeUnits"), (int, float)):
        return round(float(stats["computeUnits"]) * 0.25, 6)  # ~ $0.25/CU rough
    return 0.0


def _post_url(post: dict) -> str:
    for k in ("url", "postUrl", "facebookUrl", "permalink", "topLevelUrl", "link", "webVideoUrl"):
        if post.get(k):
            return str(post[k])
    return ""


def _write_audit(run_id: str, posts: list, request: ActorRunRequest) -> Path:
    """One JSONL line per post: source URL + attribution + flags. NEVER the
    post text, caption, image URL, or author PII (§19 + the no-raw-text rule)."""
    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    path = AUDIT_ROOT / f"{run_id}.jsonl"
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for post in posts:
            f.write(json.dumps({
                "source_url": _post_url(post),
                "platform": request.platform,
                "org_slug": request.org_slug,
                "tier": request.tier,
                "post_text_NOT_STORED": True,
            }, ensure_ascii=False) + "\n")
    return path
