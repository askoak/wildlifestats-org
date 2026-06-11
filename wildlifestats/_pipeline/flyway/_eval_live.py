#!/usr/bin/env python3
"""Live runner for 4.5+i.0.5 (separated so eval_corpus + its dry-run need no creds).

Scrapes each center-platform (apify), extracts signals in memory (claude),
aggregates per-center metrics, ranks, and writes the report. Records every
billable call to the overnight envelope and halts on the $100 ceiling / $50 eval
cap. NO raw post text on disk.
"""
from __future__ import annotations

import json
import os
import statistics
from collections import defaultdict

from wildlifestats._pipeline._common import apify_client, claude_client
from wildlifestats._pipeline.flyway import extract as fx
from wildlifestats._pipeline.flyway import eval_corpus, overnight_spend

WEEKS_IN_WINDOW = 90 / 7.0

SIGNAL_SCHEMA = {
    "type": "object",
    "required": ["matched"],
    "properties": {
        "matched": {"type": "boolean"},
        "signal_id": {"type": ["string", "null"]},
        "species_verbatim": {"type": ["string", "null"]},
        "geo_state": {"type": ["string", "null"]},
        "confidence": {"type": ["number", "null"]},
        "sources": {"type": "array", "items": {"type": "string"}},
    },
}


def _extract_one(text: str, url: str, system: str, catalog: list[dict]) -> dict | None:
    """One LLM extraction via the _common claude_client (no forked path)."""
    if not text:
        return None
    res = claude_client.extract_structured(
        system_prompt=system,
        user_content="CATALOG:\n" + json.dumps(catalog) + "\n\nPOST:\n" + text,
        output_schema=SIGNAL_SCHEMA, source_urls=[url],
        reject_on_quote_mismatch=False)
    rec = res.record
    return rec if rec.get("matched") else None, res.estimated_usd


def _scrape_posts(req, token) -> tuple[list, float]:
    """Low-level scrape returning in-memory posts + run cost. Posts are never
    written to disk by the caller — extracted then dropped."""
    actor = apify_client.PLATFORM_ACTORS[req.platform]
    run = apify_client._start_run(actor, apify_client._build_actor_input(req), token)
    run = apify_client._poll_run(run["id"], token)
    if run.get("status") != "SUCCEEDED":
        return [], apify_client._run_cost(run)
    posts = apify_client._fetch_items(run["defaultDatasetId"], token, req.max_posts)
    return posts, apify_client._run_cost(run)


def run_live(centers: list[dict], reqs, *, report_path: str) -> int:
    from wildlifestats._pipeline._common import creds
    apify_token = creds.get_apify_token()
    system = open(fx.PROMPT_PATH, encoding="utf-8").read()
    signals = fx.load_signals()
    catalog = [{"signal_id": s["signal_id"], "vocabulary": s["vocabulary"],
                "subject": s["subject_canonical"]} for s in signals]

    by_center: dict[str, dict] = defaultdict(lambda: {"posts": 0, "signals": 0,
                                                       "signal_types": set(), "species": set(),
                                                       "state": "", "tier": ""})
    halted = False
    for c in centers:
        slug = c["name"]
        by_center[slug]["state"] = c["state"]
        by_center[slug]["tier"] = c["tier"]
        for plat in eval_corpus.PLATFORMS:
            url = c["platforms"].get(plat)
            if not url:
                continue
            eval_spent = sum(float(x["total_usd"]) for x in overnight_spend.load()
                             if x.get("rail") == "0.5")
            pf = overnight_spend.preflight(0.5)
            if not pf["ok"] or eval_spent + 0.5 > eval_corpus.EVAL_CAP_USD:
                halted = True
                break
            req = apify_client.ActorRunRequest(
                platform=plat, target_url=url, org_slug=slug, org_ein=None,
                tier=1, since_date=eval_corpus.EVAL_WINDOW, max_posts=eval_corpus.EVAL_MAX_POSTS)
            try:
                posts, apify_cost = _scrape_posts(req, apify_token)
            except Exception as e:  # noqa: BLE001 — one center failing must not abort the pull
                print(f"  scrape failed {slug}/{plat}: {e}")
                continue
            llm_cost = 0.0
            for p in posts:
                by_center[slug]["posts"] += 1
                out = _extract_one(fx.post_text(p), fx.post_url(p), system, catalog)
                if isinstance(out, tuple):
                    rec, cost = out
                    llm_cost += cost or 0.0
                    if rec:
                        by_center[slug]["signals"] += 1
                        if rec.get("signal_id"):
                            by_center[slug]["signal_types"].add(rec["signal_id"])
                        if rec.get("species_verbatim"):
                            by_center[slug]["species"].add(rec["species_verbatim"])
            overnight_spend.record(rail="0.5", apify_cost_usd=apify_cost,
                                   llm_cost_usd=round(llm_cost, 6), actor_runs=1)
            posts = None  # drop raw posts
        if halted:
            break

    _write_report(by_center, report_path, halted)
    print(f"eval report: {report_path}  (halted={halted}, "
          f"cumulative ${overnight_spend.cumulative()})")
    return 0


def _metrics(slug: str, d: dict, state_counts: dict) -> dict:
    return {
        "slug": slug, "state": d["state"], "tier": d["tier"],
        "posts_per_week": round(d["posts"] / WEEKS_IN_WINDOW, 2),
        "signals_per_week": round(d["signals"] / WEEKS_IN_WINDOW, 3),
        "unique_signal_types": len(d["signal_types"]),
        "species_coverage": len(d["species"]),
    }


def _write_report(by_center: dict, path: str, halted: bool) -> None:
    rows = []
    for slug, d in by_center.items():
        m = _metrics(slug, d, by_center)
        m["est_value_score"] = eval_corpus.score(m)
        rows.append(m)
    rows.sort(key=lambda r: r["est_value_score"], reverse=True)
    scores = [r["est_value_score"] for r in rows] or [0.0]
    top30 = sum(scores[:30])
    rest = sum(scores[30:]) or 1e-9
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Flyway corpus evaluation — 2026-W24\n\n")
        if halted:
            f.write("> PARTIAL: halted on the overnight ceiling before all centers ran.\n\n")
        f.write(f"- centers evaluated: {len(rows)}\n")
        f.write(f"- top-30 vs rest signal-score ratio: {round(top30 / rest, 2)}\n")
        med = statistics.median(scores)
        f.write(f"- median value score: {round(med, 3)}; "
                f"distribution: {'long-tail' if top30 / (sum(scores) or 1e-9) > 0.6 else 'broad'}\n\n")
        f.write("| rank | slug | state | tier | posts/wk | signals/wk | sig_types | species | score |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        for i, r in enumerate(rows, 1):
            f.write(f"| {i} | {r['slug']} | {r['state']} | {r['tier']} | {r['posts_per_week']} "
                    f"| {r['signals_per_week']} | {r['unique_signal_types']} "
                    f"| {r['species_coverage']} | {r['est_value_score']} |\n")
