#!/usr/bin/env python3
"""Flyway 4.5+i.0.5 — one-time evaluation corpus pull + ranked roster report.

Characterizes every center in the 99-row social roster so the cadence/roster
cutoff is evidence-driven (architect dispatch 2026-06-11). Pulls a trailing
90-day window per center-platform, runs full LLM extraction, and emits a ranked
table. ONE-TIME spend, $50 eval cap nested under the $100 overnight ceiling.

Discipline: reuses _common/apify_client + _common/claude_client (no forked code
path); NO raw post text on disk (posts extracted in memory, then dropped; audit
log carries URLs + post_text_NOT_STORED:true); signals → JSON only (no Supabase).

Run:
    python -m wildlifestats._pipeline.flyway.eval_corpus --dry-run      # plan, no spend
    python -m wildlifestats._pipeline.flyway.eval_corpus --run          # live ($ ~30)
"""
from __future__ import annotations

import argparse
import json
import os

from wildlifestats._pipeline._common import apify_client
from wildlifestats._pipeline.flyway import build_tier_rosters, overnight_spend

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT_DIR = os.path.join(REPO, "secure", "cube", "flyway", "evaluation")
REPORT = os.path.join(OUT_DIR, "corpus-evaluation-2026-W24.md")

EVAL_WINDOW = "90 days"
EVAL_MAX_POSTS = 50
EVAL_CAP_USD = 50.0
PLATFORMS = ("facebook", "instagram")  # the POC-validated, cost-known pair


def all_centers() -> list[dict]:
    t1, t2 = build_tier_rosters.select_tiers()
    return t1 + t2


def plan(centers: list[dict]) -> list[apify_client.ActorRunRequest]:
    reqs = []
    for c in centers:
        for plat in PLATFORMS:
            url = c["platforms"].get(plat)
            if url:
                reqs.append(apify_client.ActorRunRequest(
                    platform=plat, target_url=url, org_slug=c["name"],
                    org_ein=None, tier=int(c.get("tier") == "A") or 2,
                    since_date=EVAL_WINDOW, max_posts=EVAL_MAX_POSTS))
    return reqs


def est_cost(reqs: list[apify_client.ActorRunRequest]) -> float:
    # apify ceiling + a rough LLM allowance (~50 posts/req * $0.0002/post Haiku)
    apify = apify_client.estimate_cost(reqs)
    llm = round(len(reqs) * EVAL_MAX_POSTS * 0.0002, 2)
    return round(apify + llm, 2)


def score(m: dict) -> float:
    """Composite value score (documented in the report). Rewards signal density
    and breadth; lightly rewards raw volume. Tunable; surfaced for audit."""
    return round(
        3.0 * m.get("signals_per_week", 0.0)
        + 1.0 * m.get("unique_signal_types", 0)
        + 0.5 * m.get("species_coverage", 0)
        + 0.2 * m.get("posts_per_week", 0.0), 4)


def main() -> int:
    ap = argparse.ArgumentParser(description="Flyway 4.5+i.0.5 evaluation corpus pull")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()

    centers = all_centers()
    reqs = plan(centers)
    estimate = est_cost(reqs)
    print(f"eval plan: {len(centers)} centers, {len(reqs)} actor-runs, "
          f"~${estimate} (cap ${EVAL_CAP_USD})")

    if not args.run:
        print("DRY RUN — pass --run to issue live calls.")
        return 0

    # ${estimate} is a loose worst-case CEILING (every run maxing posts); the
    # $50 eval cap and $100 overnight ceiling are enforced on ACTUAL spend per
    # call inside the live runner, which halts before any call that would breach.
    print(f"note: ${estimate} ceiling; expected actual ~$25-30. Live runner "
          f"halts on the ${EVAL_CAP_USD} eval cap / ${overnight_spend.CEILING_USD} overnight.")

    # Live execution is delegated to the credentialed runner path so the spend
    # logic stays in one place; see _run_live(). Imported lazily so the module
    # (and its dry-run) need no credentials to load.
    from wildlifestats._pipeline.flyway._eval_live import run_live  # noqa
    return run_live(centers, reqs, report_path=REPORT)


if __name__ == "__main__":
    raise SystemExit(main())
