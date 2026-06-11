#!/usr/bin/env python3
"""Phase 9c.5 — integration smoke: one live call per _common client.

SAFE BY DEFAULT. Importing this module does nothing. It only issues live,
billable calls when run as a script with --run, and only for clients whose
credential is actually present in the environment (vault CUSTOM_CRED_* handles
per creds.py). A hard cost ceiling aborts the run before it can exceed the cap.

This is the reproducible form of the architect's 9c.5 order ("each client makes
one live call against a single test target; cost + correctness validated; gated
so CI doesn't spend"). The per-client WILDLIFESTATS_LIVE_* gates in test_gates.py
are the unit-level equivalent; this runner is the single orchestrated entry point
with cost aggregation + a $5 ceiling.

Run (in a credentialed environment only):
    python -m wildlifestats._pipeline._common.smoke_9c5 --run

Per-client (single test target each):
  fetch    GET https://example.com/                 no spend
  exa      1 canonical-URL query                     ~$0.005-0.01   CUSTOM_CRED_API_EXA_AI_TOKEN
  claude   1 Haiku structured extraction             ~$0.001-0.01   CUSTOM_CRED_API_ANTHROPIC_COM_TOKEN
  apify    1 small FB posts run (limit 5)            ~$0.30         CUSTOM_CRED_API_APIFY_COM_TOKEN
  supabase skipped — DB contract already verified via the Supabase MCP; live
           REST upsert stays gated on the PostgREST Exposed-Schemas cross-lane.

A client whose credential is absent is reported SKIP (missing-credential), never
failed — the smoke validates what it can reach.
"""
from __future__ import annotations

import argparse

from . import apify_client, claude_client, creds, exa_client, fetch

COST_CEILING_USD = 5.0


def _line(client: str, status: str, detail: str = "", cost: float = 0.0) -> dict:
    return {"client": client, "status": status, "detail": detail, "cost_usd": round(cost, 4)}


def smoke_fetch() -> dict:
    try:
        env = fetch.fetch("https://example.com/", rate_limit_seconds=0, force_refresh=True)
        ok = env.http_status == 200 and bool(env.body)
        return _line("fetch", "PASS" if ok else "FAIL", f"http={env.http_status} from_cache={env.from_cache}")
    except Exception as exc:  # noqa: BLE001 — smoke reports, never crashes the batch
        return _line("fetch", "FAIL", f"{type(exc).__name__}: {exc}")


def smoke_exa() -> dict:
    if not creds.is_present("CUSTOM_CRED_API_EXA_AI_TOKEN"):
        return _line("exa", "SKIP", "no CUSTOM_CRED_API_EXA_AI_TOKEN in env")
    try:
        cands = exa_client.find_canonical_url(
            "National Audubon Society", "annual_report_landing",
            domain_hint="audubon.org", max_candidates=3)
        return _line("exa", "PASS", f"{len(cands)} candidates", cost=0.01)
    except Exception as exc:  # noqa: BLE001
        return _line("exa", "FAIL", f"{type(exc).__name__}: {exc}")


def smoke_claude() -> dict:
    if not creds.is_present("CUSTOM_CRED_API_ANTHROPIC_COM_TOKEN"):
        return _line("claude", "SKIP", "no CUSTOM_CRED_API_ANTHROPIC_COM_TOKEN in env")
    try:
        schema = {"type": "object", "required": ["topic"],
                  "properties": {"topic": {"type": "string"},
                                 "sources": {"type": "array", "items": {"type": "string"}}}}
        res = claude_client.extract_structured(
            system_prompt="Extract the main topic as a short string. Cite the source URL.",
            user_content="This page is about red-tailed hawk rehabilitation and intake.",
            output_schema=schema, source_urls=["https://example.org/hawks"])
        ok = "topic" in res.record
        return _line("claude", "PASS" if ok else "FAIL", f"topic={res.record.get('topic')!r}",
                     cost=res.estimated_usd)
    except Exception as exc:  # noqa: BLE001
        return _line("claude", "FAIL", f"{type(exc).__name__}: {exc}")


def smoke_apify() -> dict:
    if not creds.is_present("CUSTOM_CRED_API_APIFY_COM_TOKEN"):
        return _line("apify", "SKIP", "no CUSTOM_CRED_API_APIFY_COM_TOKEN in env")
    req = apify_client.ActorRunRequest(
        platform="facebook", target_url="https://www.facebook.com/lindsaywildlife",
        org_slug="lindsay-wildlife", org_ein=None, tier=1, since_date="120 days", max_posts=5)
    est = apify_client.estimate_cost([req])
    if est > COST_CEILING_USD:
        return _line("apify", "SKIP", f"estimate ${est} exceeds ${COST_CEILING_USD} ceiling")
    try:
        res = apify_client.run_actor(req)
        status = "PASS" if res.succeeded else "FAIL"
        return _line("apify", status, f"posts={res.posts_scraped} run={res.apify_run_id}",
                     cost=res.apify_cost_usd or est)
    except Exception as exc:  # noqa: BLE001
        return _line("apify", "FAIL", f"{type(exc).__name__}: {exc}")


def run_smoke() -> list[dict]:
    """Run each client's single live call, enforcing the cost ceiling as we go."""
    results: list[dict] = []
    spent = 0.0
    for fn in (smoke_fetch, smoke_exa, smoke_claude, smoke_apify):
        row = fn()
        spent += row["cost_usd"]
        if spent > COST_CEILING_USD:
            row["detail"] += f" [ABORT: cumulative ${spent:.2f} > ${COST_CEILING_USD} ceiling]"
            results.append(row)
            break
        results.append(row)
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase 9c.5 integration smoke")
    ap.add_argument("--run", action="store_true",
                    help="actually issue the live, billable calls (else dry-run plan only)")
    args = ap.parse_args()

    if not args.run:
        print("DRY RUN — pass --run to issue live calls. Plan:")
        print("  fetch=GET example.com | exa=1 query | claude=1 Haiku extract | "
              "apify=1 FB run(5) | supabase=SKIP(MCP-verified)")
        print(f"  cost ceiling: ${COST_CEILING_USD:.2f}")
        return 0

    rows = run_smoke()
    total = round(sum(r["cost_usd"] for r in rows), 4)
    print("Phase 9c.5 integration smoke")
    print("-" * 60)
    for r in rows:
        print(f"  {r['status']:5}  {r['client']:9}  ${r['cost_usd']:<7}  {r['detail']}")
    print("-" * 60)
    print(f"  total est. spend: ${total}  (ceiling ${COST_CEILING_USD})")
    failed = [r for r in rows if r["status"] == "FAIL"]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
