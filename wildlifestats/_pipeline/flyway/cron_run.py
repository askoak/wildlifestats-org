#!/usr/bin/env python3
"""Flyway 4.5+i.1 — recurring cron orchestrator (skeleton + gate + plan).

Daily entry point for the recurring early-warning pipeline. The scheduled
GitHub Actions workflow (`.github/workflows/flyway-cron.yml`) invokes this once
per day at 04:00 UTC. It is SAFE BY CONSTRUCTION at this sub-PR:

  1. KILL-SWITCH: it no-ops unless `CRON_ENABLED` (a sibling file) contains "1".
     The file ships as "0" — the cron exists and is scheduled but does nothing
     until 4.5+i.5 (go-live) flips it. Set it to "0"/delete to suspend in 30s.

  2. NO LIVE-SPEND PATH YET: the live executor deliberately raises
     NotImplementedError pointing at 4.5+i.2. The actual scrape can only run once
     .2 lands the cumulative-spend tracker + the $30/$100 auto-suspend guard. You
     cannot spend money from this PR even if CRON_ENABLED were "1".

What .1 ships: the gate, the two-tier daily PLAN (which centers, which window,
estimated cost), and a --dry-run that prints the plan without touching the
network. .2 adds the guarded executor; .3 the alerts/digest; .4 the suspend
test; .5 flips the switch.

Run:
    python -m wildlifestats._pipeline.flyway.cron_run --dry-run
"""
from __future__ import annotations

import argparse
import os

from wildlifestats._pipeline._common import apify_client
from wildlifestats._pipeline.flyway import build_tier_rosters

HERE = os.path.dirname(os.path.abspath(__file__))
CRON_ENABLED_FILE = os.path.join(HERE, "CRON_ENABLED")

# Daily cron handles Tier 1 + the trailing-7d delta on Tier 2 (architect
# Decision A). Platforms proven on the POC come first.
# Trailing-7d delta per architect Decision A; modest per-run cap because a daily
# delta rarely yields more than a handful of new posts per center. Downstream
# content_hash dedup absorbs the window overlap. The estimate ceiling below is a
# loose worst-case (every center maxing out, which never happens daily); the
# $30/$100 auto-suspend in 4.5+i.2 is the hard backstop, and .2 calibrates this
# window/cap against the first live week's ACTUAL spend.
DAILY_WINDOW = "7 days"
DAILY_MAX_POSTS = 10
PLATFORMS = ("facebook", "instagram")


def is_enabled() -> bool:
    """True only if CRON_ENABLED contains exactly '1'. Missing/empty/'0' = off."""
    try:
        with open(CRON_ENABLED_FILE, encoding="utf-8") as f:
            return f.read().strip() == "1"
    except OSError:
        return False


def _requests_for(center: dict, tier: int) -> list[apify_client.ActorRunRequest]:
    out = []
    for plat in PLATFORMS:
        url = center["platforms"].get(plat)
        if not url:
            continue
        out.append(apify_client.ActorRunRequest(
            platform=plat, target_url=url,
            org_slug=center["name"], org_ein=None, tier=tier,
            since_date=DAILY_WINDOW, max_posts=DAILY_MAX_POSTS))
    return out


def plan_today() -> list[apify_client.ActorRunRequest]:
    """The daily scrape plan: every Tier-1 center + the trailing-7d Tier-2 delta,
    one request per (center, platform-with-a-url)."""
    tier1, tier2 = build_tier_rosters.select_tiers()
    plan: list[apify_client.ActorRunRequest] = []
    for c in tier1:
        plan += _requests_for(c, tier=1)
    for c in tier2:
        plan += _requests_for(c, tier=2)
    return plan


def run(*, dry_run: bool) -> int:
    if not is_enabled():
        print("CRON_ENABLED != '1' — cron is suspended, nothing to do. "
              "(Flip to '1' at 4.5+i.5 go-live.)")
        return 0

    plan = plan_today()
    est = apify_client.estimate_cost(plan)
    print(f"Flyway daily plan: {len(plan)} actor-runs across "
          f"{len({r.org_slug for r in plan})} centers; est. ceiling ${est}")

    if dry_run:
        return 0

    # SAFETY: no live executor until 4.5+i.2 lands the cumulative-spend tracker
    # and the $30 (month-1) / $100 (month-2+) auto-suspend guard. Refuse to spend.
    raise NotImplementedError(
        "Live cron execution is deferred to Phase 4.5+i.2, which adds the "
        "cumulative-spend tracker + auto-suspend guard. This skeleton will not "
        "issue billable calls. Run with --dry-run to see the plan."
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Flyway recurring cron orchestrator")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the daily plan + cost estimate without scraping")
    args = ap.parse_args()
    return run(dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
