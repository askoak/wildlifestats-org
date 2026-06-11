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

from dataclasses import dataclass, field
from typing import Optional


PLATFORM_ACTORS = {
    "facebook": "apify/facebook-pages-scraper",
    "instagram": "apify/instagram-scraper",
    "x": "apify/twitter-scraper",
    "twitter": "apify/twitter-scraper",  # alias
    "tiktok": "apify/tiktok-scraper",
    "youtube": "apify/youtube-scraper",
}

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
    raise NotImplementedError(
        "wildlifestats._pipeline._common.apify_client.run_actor() is a "
        "Phase 9 scaffold. See flyway/apify_client.py for the validated "
        "FB/IG implementation to refactor from."
    )


def estimate_cost(requests: list[ActorRunRequest]) -> float:
    """Estimate total Apify cost for a batch of actor runs.

    Per the Flyway POC: ~$0.007/post for FB with date filter on the free
    tier; similar order of magnitude for IG. Caller surfaces this in PR
    descriptions BEFORE issuing the batch so Mike's authorization is
    informed.

    TODO[engineer]: implement per-platform per-tier cost model. The Flyway
    POC's 47-post run came in at ~$0.30 actual; calibrate from that.
    """
    raise NotImplementedError(
        "wildlifestats._pipeline._common.apify_client.estimate_cost() is a "
        "Phase 9 scaffold."
    )
