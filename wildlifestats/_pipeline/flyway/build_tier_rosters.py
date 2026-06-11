#!/usr/bin/env python3
"""Flyway 4.5+i.1 — two-tier roster builder.

Splits the social-seed roster into the cron's two orchestration tiers
(architect Decision A): Tier 1 = ~50 priority centers (daily refresh), Tier 2 =
the rest (quarterly + trailing-7d delta). Single source of truth for which
centers the recurring cron scrapes; `cron_run.py` imports `select_tiers()` so
the audit artifacts and the live selection can never drift.

DATA RECONCILIATION (flagged to architect): the order specced Tier 1 as the top
50 of `centers.yaml` ranked by `typical_annual_intake`. But `centers.yaml` has
NO per-platform social URLs — the only registry with Facebook/Instagram/TikTok/
YouTube handles is `flyway-social-seed-top100.csv` (99 scrapeable centers). You
cannot scrape a center you have no social URL for, so the tiers are built from
the social registry, ranked by its existing Priority Tier (A/B/C) then Candidate
Rank. That registry holds 99 centers, not the ~181 the order assumed — so Tier 2
is ~49, not ~131. Intake-based re-ranking can refine Tier 1 membership later by
joining centers.yaml on name/EIN; it does not change the scrape-target set.

Run:
    python -m wildlifestats._pipeline.flyway.build_tier_rosters
"""
from __future__ import annotations

import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ROSTER_CSV = os.path.join(REPO, "wildlifestats", "_pipeline", "sources",
                          "flyway-social-seed-top100.csv")

TIER1_SIZE = 50
TIER_ORDER = {"A": 0, "B": 1, "C": 2}
PLATFORM_COLS = {
    "facebook": "Facebook URL", "instagram": "Instagram URL",
    "tiktok": "TikTok URL", "youtube": "YouTube URL", "x": "X / Other URL",
}


def _rank_key(row: dict) -> tuple:
    tier = TIER_ORDER.get((row.get("Priority Tier") or "").strip(), 9)
    try:
        rank = int((row.get("Candidate Rank") or "999").strip())
    except ValueError:
        rank = 999
    return (tier, rank)


def _center(row: dict) -> dict:
    platforms = {k: (row.get(col) or "").strip()
                 for k, col in PLATFORM_COLS.items() if (row.get(col) or "").strip()}
    return {
        "rank": (row.get("Candidate Rank") or "").strip(),
        "tier": (row.get("Priority Tier") or "").strip(),
        "name": (row.get("Center Name") or "").strip(),
        "state": (row.get("State/Country") or "").strip(),
        "platforms": platforms,
    }


def select_tiers(csv_path: str = ROSTER_CSV) -> tuple[list[dict], list[dict]]:
    """Return (tier1, tier2). Tier 1 = top TIER1_SIZE by (Priority Tier, Rank)
    among centers that have at least one scrapeable social URL."""
    with open(csv_path, encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f)]
    scrapeable = [_center(r) for r in sorted(rows, key=_rank_key)
                  if any((r.get(col) or "").strip() for col in PLATFORM_COLS.values())]
    return scrapeable[:TIER1_SIZE], scrapeable[TIER1_SIZE:]


def _write_roster(path: str, centers: list[dict], title: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# {title} — {len(centers)} centers\n")
        f.write("# rank\ttier\tname\tstate\tplatforms\n")
        for c in centers:
            plats = ",".join(sorted(c["platforms"].keys()))
            f.write(f"{c['rank']}\t{c['tier']}\t{c['name']}\t{c['state']}\t{plats}\n")


def main() -> int:
    tier1, tier2 = select_tiers()
    _write_roster(os.path.join(HERE, "tier1-roster.txt"), tier1,
                  "Flyway Tier 1 (daily refresh)")
    _write_roster(os.path.join(HERE, "tier2-roster.txt"), tier2,
                  "Flyway Tier 2 (quarterly + trailing-7d delta)")
    print(f"tier1: {len(tier1)} centers -> tier1-roster.txt")
    print(f"tier2: {len(tier2)} centers -> tier2-roster.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
